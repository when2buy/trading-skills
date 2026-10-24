# <Object> round <N>: <one-line topic> (<date>)

> Task: T<id>. Previous round: <link>. Re-check: `python3 verify.py` (read-only, no network, no GPU).

## Conclusions (read this first)

| Question | Result | Verdict | Scope |
|---|---|---|---|
| <question this round answers> | <number, with noise / repeat count> | adopted / rejected / retracted / inconclusive | <configuration and scale where it holds; where it is NOT extrapolated> |

## How it was measured

- Yardstick: <metric>, A/A noise <x>%, decision threshold <y>%
- Control: <same-machine A/B/A or ABABA; same input bytes, sha256>
- Correctness: <identical outputs / quality-gate result>

## Corrections and retractions

<What this round overturned from earlier claims, and which of its own conclusions it retracted.
If none, write "checked, no corrections". Details go in `errata/`.>

## What the next round should ask

<The previous conclusion determines the next question. E.g. "isolated-pool gain holds; going to
production first needs the routing problem solved" -> round N+1.>

## Record boundary

This directory keeps curated metadata, source excerpts, and small result files (listed in
`ARTIFACTS.json`); no weights, raw traces, full responses, token IDs, or credentials.
