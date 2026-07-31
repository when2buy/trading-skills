---
name: strategy-watchdog
description: Attach time-bounded Codex monitoring to scheduled paper or live strategy executions, with a pre-entry readiness check and a post-entry execution check, evidence capture, safe infrastructure recovery, duplicate-order prevention, and fail-closed handling. Use when a user asks to monitor, watchdog, babysit, check, recover, or schedule checks around a trading strategy run, especially at T-5 minutes and T+2 minutes.
---

# Strategy Watchdog

Monitor a named strategy execution without changing its economic intent. Prefer a correctly
completed canonical execution; accumulate operational evidence; stop the run when safe recovery is
not possible.

## Establish the contract

Record these fields before installing a watchdog:

- workspace and applicable `AGENTS.md`
- strategy IDs, symbols, account profile, and paper/live environment
- scheduled entry timestamp and timezone
- canonical scheduler, runner, registry, state store, and execution gateway
- approved repair scope and immutable trading parameters
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
5. Existing positions and working/recent orders for duplicate or OCC collisions.

Repair only non-economic infrastructure defects such as a missing exact cron line, a dead expected
process, a stale strategy-scoped lock whose owner is conclusively gone, or a release/config
misalignment where the already-approved canonical artifact is unambiguous. Re-run focused tests
after repair. Do not submit an early order during the pre-check.

## T+2 post-entry check

Inspect scheduler heartbeats, runner result, strategy state, attributed broker orders, fills,
positions, and rejection messages. Classify each strategy independently:

- `FILLED_OR_OPEN`: attributed package is filled or partially filled and managed.
- `WORKING`: valid attributed order is still working; keep normal management active.
- `VALID_NO_TRADE`: the algorithm intentionally rejected the opportunity through an economic or
  risk gate.
- `RECOVERED`: an infrastructure failure was safely repaired and the canonical runner retried.
- `STOPPED_SAFE`: execution cannot be recovered without violating intent or safety.
- `UNKNOWN`: evidence is incomplete; do not guess or duplicate.

Treat quote freshness, minimum credit, spread quality, max loss, buying power, collision, assignment,
and account-risk checks as algorithmic gates. Never weaken them merely to force a fill.

## Recovery ladder

Apply the first sufficient action and stop:

1. Re-read current state and distinguish broker latency from failure.
2. Repair a strategy-scoped scheduler, process, path, permission, config, or stale-lock defect.
3. Retry only through the canonical scheduler/runner and execution gateway when all are true:
   - the original entry window remains open;
   - no attributed or overlapping working order, fill, or position exists;
   - idempotency and collision checks are active;
   - geometry, direction, lots, account, release, and risk gates remain unchanged.
4. Otherwise mark `STOPPED_SAFE` for that run and preserve the reason.

Never place a direct/manual broker order, invent substitute contracts, extend the entry window,
change sizing, cross accounts, cancel unrelated orders, or bypass ownership/risk/quote gates. A
profit objective does not justify taking a different trade from the approved algorithm.

Read `references/decision-matrix.md` when diagnosing ambiguous post-entry outcomes.

## Evidence and handoff

Persist a non-sensitive JSON/Markdown incident record with timestamps, commands, hashes, scheduler
events, derived broker status, actions, and final classification. Separate observed facts from
inference. State whether an order was submitted, accepted, working, partial, filled, rejected, or
not attempted; “runner succeeded” is not proof of a fill.

The launcher removes each one-shot cron marker after it fires. Confirm cleanup, retain the manifest
and logs, and turn recurring defects into tested infrastructure fixes.
