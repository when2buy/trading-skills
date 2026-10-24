# Tasks delegated to agents (since <date>)

> **What this page is**: which tasks are delegated, what the agent may and may not touch, how it delivers.
> **Approval**: <who> on <date> (tasks, guardrails, the one write operation, delivery method).
> **Execution**: <n> agent(s), each in its own repository copy; <lead agent / human> reviews PRs, then <who> decides merges. Claim label: `agent:in-progress`.

## 1. Tasks

| # | Task | Workstream / issue | Output | Planned | Status |
|---|---|---|---|---|---|
| 1 | <read-only verification / data report / draft...> | <line> / <#issue> | <PR / report / list> | <date> | pending |

> Selection criteria: read-only against production, no serving capacity used, negligible load,
> output only goes into the repo. Doing them cannot affect users.

## 2. Guardrails (the agent must follow)

- **Production is read-only.** Allowed commands: <allowlist, e.g. `cat ls du(ionice+nice+timeout) ss ps df`, status/inspect/log reads, metrics and health GETs>
- **Forbidden**: <start/stop/restart/remove/exec of workloads, `kill`, `sudo`, service-manager changes, editing config or code, deleting or moving files, sending inference requests to live endpoints, using capacity other than assigned, publishing externally...>
- **The one write operation** (delete this line if none): <what, where>. Post the exact command in <issue> before adding it. Undo: `<one line>`.
- **Load caps**: at most <n> requests per target per minute, <n> s timeout; no whole-disk scans.
- **Circuit breaker**: on any production error, latency rise, disk alert, or security finding, **stop and report immediately**; do not self-fix. Security details do not go into public repos or issues; report them directly.
- **Privacy**: collect metadata only (lengths, durations, tiers, caller network); never write request bodies into the repo or reports.
- **Before committing**: scan for secrets (key / token / secret / password / Bearer / `sk-` / private keys); files > 1 MB stay out, keep a summary.
- **Delivery**: open PRs only, tick issue boxes with evidence; do not merge, close issues, or touch others' PRs.

## 3. Not delegated

<Anything that changes production, spends money, deletes, publishes externally, or uses unapproved machines - and who owns each.>

## 4. Reporting cadence

After each item: output link, up to three key findings, anything needing a human decision.
If blocked for over an hour, stop and report instead of pushing on.
