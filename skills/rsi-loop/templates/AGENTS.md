# AGENTS.md - for agents (and humans) taking over this repository

> Agents such as Claude Code and Codex read this first (`CLAUDE.md` can be a symlink to this file).

## What this repository is

<One sentence: what system it manages and who it serves.>

## Read these four, in order

1. `docs/ARCHITECTURE.md` - how a request/job flows, where each component lives
2. `tracking/STATUS.md` - current state, who is doing what
3. `docs/sop/<main SOP>.md` - the process for changing anything
4. `docs/<object>/README.md` for the object you will touch

Direction and this week's work: `docs/ROADMAP.md` -> the single task table `docs/plans/PLAN-<...>.md`
(new work gets a T-number there; do not invent another numbering scheme).

## Hard rules

> Each rule states **what incident produced it**. A rule with no incident behind it does not belong yet.

| # | Rule | Why (what happened) |
|---|---|---|
| 1 | **Ask a human before touching production** | Affects users; the human may have chosen "observe only" |
| 2 | Before acting, check **who else is operating** on the target (process list, recent logins, terminal sessions, other agent sessions) | <date>: two parties changed the same machines at once |
| 3 | **Canary first** on spare capacity; promote only after the full standard cases pass and a human approves; keep the original; write the rollback command before acting | SOP phases 3-4 |
| 4 | **Never read, copy, or print secrets**; verify credentials by length / status code only | |
| 5 | Kill processes **by exact PID**, never `pkill -f <pattern>` | The pattern matched the agent's own command line |
| 6 | Long jobs go in `tmux` / `setsid nohup`; no foreground `sleep` | Foreground jobs die with the SSH session |
| 7 | Conclusions need evidence: before/after on the same input bytes, raw inputs and outputs | A success status code is not a pass |
| 8 | After a change, sync: machine-readable config, the object's architecture page, `tracking/STATUS.md` | Doc/deployment drift caused most misjudgements |
| 9 | Scan reports for internal addresses and credentials before publishing; verify the published copy is byte-identical | Published reports are public |
| <n> | <new rule> | <what happened> |

## Common commands

```bash
# connect to machines (see ACCESS.md)
# inspect current state
# run the standard cases
```

## Committing

- Do not push to the main branch; open a PR.
- Read tokens from the environment; never put them in command-line arguments or URLs.
- Evidence directories are append-only: add files, do not move existing ones.
