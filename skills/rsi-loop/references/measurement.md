# Measurement and evidence rules

## Yardstick
1. Pick one metric per question. Define it with a human (what span, what unit, what is excluded).
2. **A/A first**: repeat the *same* configuration >= 5 times. The spread is the noise. Decision
   threshold = a bit above noise (we used 2% after reducing noise from 4-9%).
3. If noise exceeds the effect size you care about, improve the yardstick before anything else
   (steady-state only, locked clocks, fixed seeds, warm caches, fresh cache prefixes for cache tests).

## Controls
- **Same machine**: same-model machines still differed ~6%; a restart alone drifted 3-4%. Use A/B/A
  or ABABA on one machine. Never compare across machines and call it an effect.
- **Same bytes**: before/after uses identical request bytes; record sha256.
- **Reproduce production first** on the canary; proceed only when key scenarios match within the
  stated tolerance.
- **One variable at a time**; record every variant including rejected ones.

## Correctness
- System-level changes: prove identical outputs (token/byte level).
- Numerics-changing changes: quality gate with a paired test (e.g. McNemar) on a benchmark set.
- Status codes prove nothing; check the fields the user depends on (billing counts, finish reason,
  tool-call arguments).

## Scope and provenance
- State where the conclusion holds. "+22% in an isolated pool" is not "+22% in production".
- Every number traces to a raw file or a command.
- Failures are evidence: keep rejected options, retractions, and errata as separate files.
- Cross-checking: the lead re-verifies 2-3 key sub-agent claims against raw data every batch.

## Targets that are physically unreachable
Before promising a target, compute the share of real traffic that cannot reach it under the
current hardware (e.g. work that must be recomputed no matter what). Re-define the target for that
share (e.g. a per-unit-of-work rate) and agree it with the human up front.
