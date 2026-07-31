#!/usr/bin/env python3
"""Launch a bounded Codex Strategy Watchdog run from a manifest."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import subprocess
import sys


CODEX = Path("/usr/local/bin/codex")
CRON_LOCK = Path("/tmp/strategy-watchdog-crontab.lock")


def cron_marker(watchdog_id: str, phase: str) -> str:
    return f"STRATEGY-WATCHDOG-{watchdog_id}-{phase.upper()}"


def remove_own_cron(marker: str) -> None:
    CRON_LOCK.touch(exist_ok=True)
    with CRON_LOCK.open("r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        current = subprocess.run(
            ["crontab", "-l"], text=True, capture_output=True, check=False
        )
        if current.returncode not in (0, 1):
            return
        kept = [
            line for line in current.stdout.splitlines() if f"# {marker}" not in line
        ]
        subprocess.run(
            ["crontab", "-"],
            input="\n".join(kept).rstrip() + "\n",
            text=True,
            check=False,
        )


def prompt_for(manifest: dict, phase: str, manifest_path: Path) -> str:
    strategy_list = ", ".join(manifest["strategy_ids"])
    phase_task = (
        "Perform the T-5 pre-entry readiness check. Broker interaction must remain read-only; "
        "do not submit an early order."
        if phase == "pre"
        else
        "Perform the T+2 execution check. Reconcile scheduler logs, attributed broker orders, "
        "fills and positions before deciding whether any recovery is needed."
    )
    repair = (
        "The operator authorized bounded infrastructure repair."
        if manifest.get("allow_repair")
        else
        "This run is read-only; report defects but do not repair them."
    )
    return f"""Use $strategy-watchdog.

You are the {phase.upper()} watchdog for a scheduled {manifest['environment']} strategy execution.
{phase_task}

Manifest: {manifest_path}
Workspace: {manifest['workspace']}
Strategies: {strategy_list}
Account profile: {manifest['account_profile']}
Scheduled entry: {manifest['entry_at']}
Evidence directory: {manifest['evidence_dir']}
{repair}

Read the workspace AGENTS.md and all required local operational manuals before acting. Work only on
the listed strategies and account. Do not expose credentials or save raw account responses.

Preserve the approved algorithm exactly: strategy IDs, account, paper/live environment, entry
window, contracts selected by the algorithm, geometry, direction, package counts, release lineage,
and every quote/collision/max-loss/account-risk/assignment gate. Never place a direct broker order.
Any retry must use the canonical scheduler/runner and ExecutionGateway, occur inside the original
entry window, and happen only after proving there is no overlapping working order, fill, or
position. Do not cancel or modify unrelated orders.

Repair strategy-scoped infrastructure only when the intended approved artifact is unambiguous and
run focused validation afterward. A valid economic/risk-gate skip is VALID_NO_TRADE, not a bug. If
safe recovery is impossible or time has expired, classify STOPPED_SAFE and leave the strategy
without a new entry.

Write a non-sensitive timestamped incident/evidence record under the evidence directory. End with
one classification per strategy: FILLED_OR_OPEN, WORKING, VALID_NO_TRADE, RECOVERED, STOPPED_SAFE,
or UNKNOWN, and state whether any broker order action occurred.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--phase", choices=("pre", "post"), required=True)
    parser.add_argument("--print-prompt", action="store_true")
    parser.add_argument("--no-cleanup", action="store_true")
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    prompt = prompt_for(manifest, args.phase, manifest_path)
    if args.print_prompt:
        print(prompt)
        return 0

    evidence_dir = Path(manifest["evidence_dir"]).resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    final_path = evidence_dir / f"{args.phase}-{stamp}-final.md"
    transcript_path = evidence_dir / f"{args.phase}-{stamp}-codex.log"
    summary_path = evidence_dir / f"{args.phase}-{stamp}-launcher.json"
    command = [
        str(CODEX),
        "exec",
        "--ephemeral",
        "--color",
        "never",
        "-C",
        str(Path(manifest["workspace"]).resolve()),
        "-s",
        "danger-full-access",
        "-c",
        'approval_policy="never"',
        "-o",
        str(final_path),
        prompt,
    ]
    started = datetime.now(timezone.utc)
    with transcript_path.open("w", encoding="utf-8") as transcript:
        completed = subprocess.run(
            command,
            text=True,
            stdout=transcript,
            stderr=subprocess.STDOUT,
            check=False,
        )
    finished = datetime.now(timezone.utc)
    summary = {
        "watchdog_id": manifest["watchdog_id"],
        "phase": args.phase,
        "started_at_utc": started.isoformat(),
        "finished_at_utc": finished.isoformat(),
        "returncode": completed.returncode,
        "final_message": str(final_path),
        "transcript": str(transcript_path),
        "broker_action_by_launcher": False,
    }
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    if not args.no_cleanup:
        remove_own_cron(cron_marker(manifest["watchdog_id"], args.phase))
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
