---
name: strategy-watchdog
description: Monitor and actively recover scheduled paper or live strategy executions, including pre-entry readiness, post-entry reconciliation, bug repair, canonical retry, operator-authorized catch-up, evidence capture, and precise duplicate/conflict prevention. Use when a user asks to monitor, watchdog, babysit, fix, recover, or drive a trading strategy run to its intended terminal outcome, especially around T-5 and T+2.
---

# Strategy Watchdog

Drive a named strategy execution to its authorized terminal outcome. Observe, diagnose, repair,
retry, and verify rather than merely reporting why execution stopped. Preserve the current operator
contract and real economic/risk constraints, but never turn broad or ambiguous safety checks into a
reason to block an otherwise valid execution.

## Operating priority

Use this order of priorities:

1. Complete the operator-authorized strategy execution through the canonical system.
2. Prevent only proven duplicate, opposite-direction netting, account, or risk-limit violations.
3. Repair bugs and infrastructure defects that prevent execution, then retry and verify.
4. Preserve evidence and report an unresolved blocker only after exhausting in-scope recovery.

Treat the operator's latest explicit instruction as an amendment to the execution contract. It may
change the catch-up deadline, price tolerance, quantity, or recovery method. Record the old and new
values and apply the amendment prospectively; do not silently infer an amendment.

## Establish the contract

Record these fields before installing a watchdog:

- workspace and applicable `AGENTS.md`
- strategy IDs, symbols, account profile, and paper/live environment
- scheduled entry timestamp and timezone
- canonical scheduler, runner, registry, state store, and execution gateway
- approved repair scope, current trading parameters, and operator-authorized amendments
- evidence/log directory

For AlphaVault-managed strategies, read the AlphaVault Ops manual and current agent updates at every
watchdog process start. Never read credentials from another repository or persist secrets/raw
account responses.

## Install the two checks

Use `scripts/install_watchdog.py`. It converts the strategy time to UTC because many hosts ignore
`CRON_TZ`, groups strategies sharing one entry timestamp, writes a manifest, and renders or installs
one-shot T-5 and T+2 cron jobs.

Preview first:

```bash
python scripts/install_watchdog.py \
  --workspace /absolute/workspace \
  --run-date 2026-07-31 \
  --entry-time 10:30 \
  --strategy-id strategy_a \
  --account-profile live_account
```

Install only when the user has authorized monitoring and the repair scope:

```bash
python scripts/install_watchdog.py ... --allow-repair --install
```

Run the same command again to update an identical watchdog idempotently. Use one manifest for
strategies sharing an entry time so concurrent agents do not race over the same account.

## T-5 pre-entry check

Remain read-only toward the broker. Verify:

1. Broker clock, market session, account status, and expected paper/live profile.
2. Exact strategy registration, enabled state, runtime config, release lineage, and package count.
3. Independent scheduler presence, executable child command, process/lock health, and writable logs.
4. Quote/contract discovery availability without treating availability as fillability.
5. Existing positions and working/recent orders, indexed by attribution, OCC, and side.

Repair in-scope defects such as a missing cron line, dead process, stale strategy-scoped lock,
release/config mismatch, overly broad collision guard, or another code bug that prevents an
approved execution. Re-run focused tests after a code repair. Do not submit before the authorized
entry window.

## T+2 post-entry check

Inspect scheduler heartbeats, runner result, strategy state, attributed broker orders, fills,
positions, and rejection messages. Classify each strategy independently:

- `FILLED_OR_OPEN`: attributed package is filled or partially filled and managed.
- `WORKING`: valid attributed order is still working; keep normal management active.
- `VALID_NO_TRADE`: the algorithm intentionally rejected the opportunity through an economic or
  risk gate.
- `RECOVERED`: an infrastructure failure was safely repaired and the canonical runner retried.
- `BLOCKED`: a specific unresolved constraint prevents execution after recovery was exhausted.
- `UNKNOWN`: evidence is incomplete; do not guess or duplicate.

Treat quote freshness, minimum credit, spread quality, max loss, buying power, assignment, and
account-risk checks as algorithmic gates under the current execution contract. An explicit operator
amendment may change an economic parameter; record it and re-run the affected checks.

Do not treat account occupancy as a global collision. Build one broker snapshot, then compare each
candidate leg by exact OCC and side:

- unrelated OCC contracts do not conflict;
- same OCC and same side may coexist when attribution and aggregate risk remain valid;
- same OCC and opposite side conflicts because a netting broker can erase strategy ownership;
- an attributed working/fill for the same strategy and idempotency key is a duplicate;
- uncertain data triggers reconciliation, not an immediate permanent stop.

For shared accounts, normalize the snapshot and run
`scripts/check_occ_conflicts.py --input snapshot.json`. Use its candidate-level result as evidence;
do not replace it with an underlying-wide or account-wide occupancy check.

## Recovery ladder

Apply the first sufficient action, then continue until execution reaches a verified terminal state:

1. Re-read current state and distinguish broker latency from failure.
2. Repair a strategy-scoped scheduler, process, path, permission, config, or stale-lock defect.
3. Fix the blocking code or configuration bug when intended behavior is established by tests,
   config, runbook, or an explicit operator instruction.
4. Retry through the canonical scheduler/runner and execution gateway when:
   - the original window or an explicitly authorized catch-up window remains open;
   - no attributed duplicate exists for this strategy/idempotency key;
   - exact OCC/side reconciliation permits the candidate;
   - the current geometry, account, quantity, price tolerance, and risk gates pass.
5. If the canonical scheduler cannot express an explicitly authorized recovery, use the canonical
   ExecutionGateway/operator-recovery entry point with attributable client-order IDs. Never call a
   raw broker SDK merely to bypass the strategy system.
6. Reconcile broker orders, fills, positions, and management registration. Continue monitoring a
   working order until its authorized deadline.
7. Mark `BLOCKED` only with a concrete failed constraint and after all authorized recovery paths are
   exhausted.

Never invent substitute contracts, cross accounts, cancel unrelated orders, or bypass attribution
and risk controls. Do not preserve a stale scheduler window, price tolerance, or collision rule
after the operator explicitly amends it.

Read `references/decision-matrix.md` when diagnosing ambiguous post-entry outcomes.

## Evidence and handoff

Persist a non-sensitive JSON/Markdown incident record with timestamps, commands, hashes, scheduler
events, derived broker status, actions, and final classification. Separate observed facts from
inference. State whether an order was submitted, accepted, working, partial, filled, rejected, or
not attempted; “runner succeeded” is not proof of a fill.

The launcher removes each one-shot cron marker after it fires. Confirm cleanup, retain the manifest
and logs, and turn recurring defects into tested infrastructure fixes.
