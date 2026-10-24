---
name: rsi-loop
description: Bootstrap and run a recursive self-improvement (RSI) engineering loop for a human + agent + repository team - what to build on day 0, how to run each improvement round (define the problem, read the data, dig in parallel, freeze the yardstick, cross-check, canary, write it down as a rule), how to delegate safely to agents, and how to keep a re-verifiable research ledger. Use when taking over a new system, service, model, or strategy, when starting an optimisation, debugging, or research round, when asked to set up agent guardrails, task tracking, or an evidence ledger, or when a team wants its agents to compound each other's work instead of restarting from scratch.
---

# RSI Loop

"Recursive self-improvement" here does **not** mean a model editing its own weights. It means the
*working method* of a human + agent + repository team improves itself: every round writes its
lessons into the repo (rules, yardsticks, tests, templates), and the next agent starts from that
state instead of from zero. What gets improved includes the process itself - the yardstick, the
gates, the delegation rules.

**The loop compounds only because knowledge lives in the repo, not in any one agent's context.**

Works for anything you can measure and change: a serving stack, a data pipeline, a trading
strategy, a training recipe. Examples below are domain-neutral; see `references/evolution.md` for
the case history this was distilled from.

## Pick your entry point

| You are... | Read |
|---|---|
| Taking over a new system | "Day 0" below, then copy `templates/` |
| Starting an optimisation / investigation round | "The seven-step round" + `references/measurement.md` |
| About to hand work to an agent | `references/delegation.md`, then `templates/DELEGATION.md` |
| Running research that must be re-checkable | "Research ledger" below, `templates/ROUND-README.md`, `templates/verify.py` |
| Wondering why a rule exists | `references/evolution.md`, `references/pitfalls.md` |

## Day 0: make the repo takeover-able

Goal: **anyone (human or agent) can read four documents and take over.**

1. **Read-only survey of the live system first.** Only inspect (list, status, logs, metrics,
   config); change nothing. Write the first evidence report. Documented numbers are leads; the
   live system is the fact. A plan written before this survey tends to be overturned within the
   hour.
2. **Write `AGENTS.md`** (template: `templates/AGENTS.md`): what to read first, a table of hard
   rules where **every rule states what incident produced it**, common commands, commit rules.
   Rule #1 is always "ask a human before touching production."
3. **Define standard cases with pass conditions**: a replayable set of requests/inputs with a
   written pass criterion each. "Fixed" always means "passes this set". A success status code is
   never a pass; check the fields that matter.
4. **Define the yardstick and its noise**: pick one metric, repeat the *same* configuration >= 5
   times, and take the spread as the A/A noise. Noise sets the decision threshold. If noise is
   bigger than the effects you care about, fix the yardstick before measuring anything else.
5. **Turn on observation**: per-minute counters (volume, queueing, hit rates, errors), kept >= 30
   days. Without history, claims like "it is slower at night" cannot be checked later.
6. **One tracking system**: a single task table with stable IDs, a milestone page with checkboxes
   (date + evidence link when ticked), and one open-questions page for fact conflicts and
   decisions that need a human. New work gets an ID in the table; no parallel numbering schemes.

Suggested layout:

```
AGENTS.md  ACCESS.md
docs/{ARCHITECTURE,ROADMAP}.md  docs/sop/  docs/plans/  docs/<object>/README.md  docs/history/
tracking/{STATUS,MILESTONES,OPEN-QUESTIONS}.md
evidence/   configs/   scripts/   tests/   skills/
```

## The seven-step round

| # | Step | Done when |
|---|---|---|
| 1 | **Define the problem** | A replayable input, the pre-fix bad output or baseline number, and the pass condition are all written down. A human confirmed the *definition* of the metric (e.g. which span "latency" covers). |
| 2 | **Read the data first** | Real traffic/logs are broken down: where time goes, which class is slow, how large each share is. Fit a simple model if you can. You can say "the main cause is X, ~Y%, removing it should reach Z" - and which part is physically unfixable. |
| 3 | **Dig in parallel** | Split the question across agents, one angle each (source code, measurement, upstream, reference implementation). Each returns a conclusion plus raw data. |
| 4 | **Freeze the yardstick** | Same inputs (hash-checked), same machine, A/A noise measured, **one variable changed at a time**. Each variant's difference exceeds noise, with a correctness proof (identical outputs, or a quality gate). |
| 5 | **Cross-check** | The lead agent/human re-verifies sub-agents' key claims against raw data; any cross-machine claim is re-run on one machine. An "errata" section exists even if it says "checked, no corrections". |
| 6 | **Canary, then roll out** | Reproduce production on a spare machine first -> change -> full standard cases + a stability test -> report -> **human approves** -> staged rollout, original kept, rollback command written *before* acting. |
| 7 | **Write it down as a rule** | Pitfalls go into the SOP / `AGENTS.md` / tests; negative results go into the ledger; status docs are updated. The next agent avoids the same trap without reading your conversation. |

Step 7 is what makes the loop recursive and is the one most often skipped.

### Change-the-live-system SOP (steps 4-6 in detail)

Register -> baseline (read-only) -> localise -> canary -> roll out -> accept & observe. Full
checklist: `templates/SOP-checklist.md`. Key points:

- **A canary must first reproduce production**: same artifact, data, and parameters (checksum
  them), and key scenarios matching production numbers within a stated tolerance (we used +/-15%).
  A canary that cannot reproduce production produces untrustworthy gains.
- **A canary must not look like production** to discovery/monitoring: bind locally and stay out of
  the port ranges your dashboards scan.
- **A human approves from the benchmark report, not from an agent's summary.**
- **Roll out one unit at a time**, lowest-traffic first; keep the original.

## Measurement rules (summary; details in `references/measurement.md`)

- Measure the noise first; never claim a gain smaller than it.
- Compare on the same machine (A/B/A or ABABA); cross-machine differences masquerade as effects.
- Before/after on byte-identical inputs, checked by hash.
- Report correctness and speed together.
- State the scope of every conclusion ("holds in the isolated 1+1 setup; not extrapolated to prod").
- Every number traces to a raw file or command.
- Negative results are first-class: keep rejected options, retracted claims, errata.

## Delegating to agents (details in `references/delegation.md`)

Write the guardrails **before** the work: read-only command allowlist, explicit prohibitions, the
single permitted write (if any) with its one-line undo, load caps, a circuit breaker ("on any
production anomaly or security finding: stop and report, do not self-fix"), privacy rules
(metadata only), and delivery = PR only (no merge, no closing issues). Claim tasks visibly (task
table + issue comment + label). Review by raw data, not by the agent's summary.

| Humans | Agents |
|---|---|
| Set goals, thresholds, and metric definitions | Decompose, dig in parallel, build measurement tools, run A/B, compute noise |
| Approve every production change | Run experiments and canaries on spare capacity |
| Decide adopt / reject | Write records, reports, handoffs, PRs |
| Decide which lines to open or stop | Propose "what the next round should ask" |

## Research ledger (re-checkable rounds)

One directory per round: `README.md` (question, conclusion, scope, next question), `PLAN.md`,
`ARTIFACTS.json` (path, bytes, sha256 per evidence file), `verify.py` (one command, read-only, no
network, no GPU), `errata/` (retractions and corrections as their own files). Keep only curated
metadata and small files; never weights, raw traces, full responses, or credentials; files > 1 MB
keep a summary only. Merge a research branch to mainline only when its conclusion is adopted.

## Docs and tracking discipline

- Direction (roadmap) -> orthogonal workstreams, one lead each -> one task table -> milestones.
- All fact conflicts and human decisions live on one open-questions page: who to ask, what it blocks.
- Separate *current state* (architecture / status / machine-readable config) from *history*
  (one report per round, linked not moved).
- Every report leads with the conclusion, states what changed in production and how to undo it,
  lists corrections to earlier claims, and lists decisions needed.
- After any change, sync the three places that drift: machine-readable config, the object's
  architecture page, the status page.
- Scan before publishing anything public (internal addresses, credentials, customer content);
  verify the published copy is byte-identical to the local one.
- Define a term in one sentence on first use; give the conclusion before the details.

## Honest limits

The loop is still pushed by people (which lines to open/stop is human judgment); cross-team change
announcements are manual; non-determinism is rarely fully removed; research branches pile up unless
the merge cadence is set explicitly. The natural next step is to make yardstick + gates +
rollback run automatically on every commit.
