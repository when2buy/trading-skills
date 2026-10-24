# Change-the-live-system checklist (copy into the tracking row or the PR and tick off)

> Six phases: register -> baseline -> localise -> canary -> roll out -> accept & observe.
> If an item cannot be done, write why. Do not silently skip it.

## Phase 0: register
- [ ] Problem has three things: a **replayable input**, the **pre-fix bad output / baseline number**, a **pass condition**
- [ ] Task table has a T-number and a lead; STATUS has a row
- [ ] A human confirmed the metric's definition (e.g. which span "latency" covers)

## Phase 1: baseline (read-only)
- [ ] Standard cases run against current production; results archived
- [ ] Real traffic/logs broken down: where time goes, what share, what is fixable vs physically fixed
- [ ] A/A noise known (same configuration >= 5 runs); decision threshold: ____ %

## Phase 2: localise
- [ ] Per-stage timing identifies the main cause (not a guess)
- [ ] Relevant source / upstream / reference implementation read; parallel threads each have raw data
- [ ] Sub-agents' key claims re-verified on raw data; cross-machine claims re-run on one machine

## Phase 3: canary
- [ ] Spare machine; recent use checked; owner notified in the tracking issue
- [ ] Artifact / data / launch parameters match production (checksums)
- [ ] **Reproduces production first**: key scenarios within the agreed tolerance (we used +/-15%)
- [ ] Canary binds locally / outside discovery and dashboard scan ranges
- [ ] One variable at a time; every variant, including rejected ones, has a recorded result
- [ ] Correctness: identical output (token/byte level) or a quality gate with a paired test
- [ ] Stability: replay realistic concurrency, before/after with the same seed
- [ ] Risk list: under what conditions could this change go bad? Each checked

## Phase 4: roll out (precondition: a human read the benchmark report and approved)
- [ ] Rollback command written before acting; original kept (renamed); config backed up
- [ ] Drain traffic first; change the lowest-traffic unit first; observe, then proceed one by one
- [ ] Units someone else is iterating on are skipped and noted

## Phase 5: accept & report
- [ ] Full standard cases through the real user path
- [ ] Report: conclusion first; what changed in production and how to undo it; what failed / was not done; scope
- [ ] Scanned for internal addresses, credentials, customer content; published copy byte-identical
- [ ] Synced config, architecture page, STATUS, stable-version record; drift check clean

## Phase 6: observe & write it down
- [ ] No regression in the observation window
- [ ] Pitfalls added to the SOP / AGENTS.md / tests (with the incident)
- [ ] Negative results, retractions, errata are in the ledger
- [ ] Issue closed with evidence; milestone ticked with date and evidence
