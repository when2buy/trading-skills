# Trading Skills Repository Guide

This repository contains reusable agent skills, not strategy secrets or runtime state.

For every new or updated skill:

1. Keep the skill self-contained under `skills/<skill-name>/`.
2. Use only `name` and `description` in `SKILL.md` frontmatter.
3. Keep the core workflow concise; put detailed decision tables in `references/`.
4. Add deterministic scripts for fragile, repeatable operations.
5. Never commit credentials, raw broker/account responses, runtime manifests, order logs, or
   strategy-specific private data.
6. Make live mutations only when an operator mandate exists and preserve canonical account,
   allocation, release lineage, attribution, collision, quote, and risk gates.
7. Validate Python scripts with `py_compile` and validate the skill folder with the Codex
   `quick_validate.py` utility before publishing.

Update the catalog in `README.md` whenever a skill is added or renamed.
