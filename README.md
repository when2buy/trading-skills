# When2buy Trading Skills

Reusable Codex skills for trading research, deployment, execution monitoring, and operations.

## Catalog

| Skill | Purpose |
|---|---|
| [Strategy Watchdog](skills/strategy-watchdog/SKILL.md) | Attach T-5 readiness and T+2 execution checks, repair execution defects, retry through attributable canonical paths, and prevent only precise duplicate or direction conflicts. |

## Install

Clone this repository, then copy the desired skill directory into the Codex skills directory:

```bash
git clone https://github.com/when2buy/trading-skills.git
cp -R trading-skills/skills/strategy-watchdog ~/.codex/skills/
```

Invoke it with:

```text
$strategy-watchdog
```

## Repository contract

- Put each installable skill under `skills/<skill-name>/`.
- Keep credentials, raw broker responses, account identifiers, and generated runtime evidence out
  of this repository.
- Treat paper/live authorization, account selection, sizing, and risk limits as explicit external
  contracts; a skill must not infer or weaken them.
- Route trading actions through the canonical strategy execution system. Monitoring skills must not
  invent substitute trades or bypass duplicate-order, attribution, quote, max-loss, or assignment
  controls.
- Validate every skill before publishing and include deterministic scripts when repetition or
  execution safety requires them.
