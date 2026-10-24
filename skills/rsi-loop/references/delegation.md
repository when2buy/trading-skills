# Delegating to agents safely

## Order of operations
1. Pick tasks that are read-only against production, use no serving capacity, put negligible load
   on anything, and write only to the repo.
2. Write the delegation document (`templates/DELEGATION.md`) **before** starting the agent.
3. Get explicit human approval of tasks + guardrails + the single write (if any).
4. Claim visibly: row in the delegation doc, comment on the tracking issue, `agent:in-progress` label.
5. Run the agent in its own workspace / repo copy.
6. Review output, then the human decides merges.

## Guardrail checklist
- Allowlist of read commands; explicit prohibitions (restart, kill, delete, privilege escalation,
  inference to live endpoints, unassigned capacity, external publishing).
- The one permitted write, with the exact command posted first and a one-line undo.
- Load caps and timeouts; no whole-disk scans (run low priority if scanning at all).
- Circuit breaker: anomaly or security finding -> stop and report; do not self-fix. Keep security
  details out of public repos and issues.
- Metadata only; no request bodies in artifacts.
- Pre-commit secret scan; > 1 MB files stay out.
- PRs only; no merging, no closing issues, no touching others' PRs.

## Reviewing agent output
- Raw data over summaries. For each batch: read the diff, scan for secrets, spot-check 2-3 key
  claims on the live system yourself.
- Feed review findings back to the agent, and turn general ones into rules (for example "the canary
  listened on a port the dashboard scans" -> bind locally and avoid scanned ranges).
- Close issues only with evidence attached; closing is itself a progress signal.

## Verify the guardrails actually worked
After an agent runs, confirm: nothing it was forbidden to touch changed; its canary is not visible
to discovery; its commits contain no secrets; its claims match raw data.
