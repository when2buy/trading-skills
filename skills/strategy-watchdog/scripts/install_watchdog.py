#!/usr/bin/env python3
"""Render or install one-shot Strategy Watchdog cron jobs."""

from __future__ import annotations

import argparse
from datetime import date, datetime, time, timedelta, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
from zoneinfo import ZoneInfo


SKILL_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = SKILL_ROOT / "scripts" / "launch_watchdog.py"
CRON_LOCK = Path("/tmp/strategy-watchdog-crontab.lock")
SAFE_TOKEN = re.compile(r"^[A-Za-z0-9_.:-]+$")


def safe_token(value: str, label: str) -> str:
    if not SAFE_TOKEN.fullmatch(value):
        raise ValueError(f"{label} contains unsafe characters: {value!r}")
    return value


def parse_entry(run_date: str, entry_time: str, timezone_name: str) -> datetime:
    day = date.fromisoformat(run_date)
    hour, minute = (int(part) for part in entry_time.split(":"))
    return datetime.combine(day, time(hour, minute), ZoneInfo(timezone_name))


def watchdog_id(
    workspace: Path,
    run_date: str,
    entry_time: str,
    strategy_ids: list[str],
    account_profile: str,
) -> str:
    source = "|".join(
        [str(workspace), run_date, entry_time, account_profile, *sorted(strategy_ids)]
    )
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:10]
    return f"{run_date.replace('-', '')}-{entry_time.replace(':', '')}-{digest}"


def marker(job_id: str, phase: str) -> str:
    return f"STRATEGY-WATCHDOG-{job_id}-{phase.upper()}"


def cron_line(
    when: datetime,
    manifest: Path,
    phase: str,
    job_id: str,
    log_dir: Path,
) -> str:
    utc = when.astimezone(timezone.utc)
    phase_marker = marker(job_id, phase)
    lock_path = f"/tmp/strategy-watchdog-{job_id}-{phase}.lock"
    command = [
        "/usr/bin/flock",
        "-n",
        lock_path,
        "/usr/bin/python3",
        str(LAUNCHER),
        "--manifest",
        str(manifest),
        "--phase",
        phase,
    ]
    rendered = " ".join(shlex.quote(part) for part in command)
    log_path = shlex.quote(str(log_dir / f"{phase}.cron.log"))
    return (
        f"{utc.minute} {utc.hour} {utc.day} {utc.month} * "
        f"{rendered} >> {log_path} 2>&1 # {phase_marker}"
    )


def read_crontab() -> list[str]:
    completed = subprocess.run(
        ["crontab", "-l"], text=True, capture_output=True, check=False
    )
    if completed.returncode not in (0, 1):
        raise RuntimeError(completed.stderr.strip() or "cannot read crontab")
    return completed.stdout.splitlines()


def install_cron(lines: list[str], markers: list[str]) -> None:
    CRON_LOCK.touch(exist_ok=True)
    with CRON_LOCK.open("r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        existing = read_crontab()
        filtered = [
            line for line in existing if not any(f"# {item}" in line for item in markers)
        ]
        payload = "\n".join([*filtered, *lines]).rstrip() + "\n"
        subprocess.run(["crontab", "-"], input=payload, text=True, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--run-date", required=True)
    parser.add_argument("--entry-time", required=True, help="HH:MM in --timezone")
    parser.add_argument("--timezone", default="America/New_York")
    parser.add_argument("--strategy-id", action="append", required=True)
    parser.add_argument("--account-profile", required=True)
    parser.add_argument("--environment", choices=("paper", "live"), default="live")
    parser.add_argument("--pre-minutes", type=int, default=5)
    parser.add_argument("--post-minutes", type=int, default=2)
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--allow-repair", action="store_true")
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        raise ValueError(f"workspace is not a directory: {workspace}")
    strategy_ids = sorted({safe_token(item, "strategy ID") for item in args.strategy_id})
    account_profile = safe_token(args.account_profile, "account profile")
    if args.pre_minutes < 1 or args.pre_minutes > 60:
        raise ValueError("--pre-minutes must be between 1 and 60")
    if args.post_minutes < 1 or args.post_minutes > 60:
        raise ValueError("--post-minutes must be between 1 and 60")
    entry = parse_entry(args.run_date, args.entry_time, args.timezone)
    job_id = watchdog_id(
        workspace, args.run_date, args.entry_time, strategy_ids, account_profile
    )
    evidence_dir = (
        args.evidence_dir.resolve()
        if args.evidence_dir
        else workspace / "reports" / "strategy-watchdog" / job_id
    )
    evidence_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = evidence_dir / "manifest.json"
    pre_at = entry - timedelta(minutes=args.pre_minutes)
    post_at = entry + timedelta(minutes=args.post_minutes)
    manifest = {
        "schema_version": 1,
        "watchdog_id": job_id,
        "workspace": str(workspace),
        "run_date": args.run_date,
        "entry_at": entry.isoformat(),
        "timezone": args.timezone,
        "strategy_ids": strategy_ids,
        "account_profile": account_profile,
        "environment": args.environment,
        "allow_repair": bool(args.allow_repair),
        "immutable_execution_fields": [
            "strategy_ids",
            "account_profile",
            "environment",
            "entry_at",
            "geometry",
            "direction",
            "package_count",
            "risk_gates",
            "release_lineage",
        ],
        "checks": {
            "pre": pre_at.isoformat(),
            "post": post_at.isoformat(),
        },
        "evidence_dir": str(evidence_dir),
        "installed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        cron_line(pre_at, manifest_path, "pre", job_id, evidence_dir),
        cron_line(post_at, manifest_path, "post", job_id, evidence_dir),
    ]
    markers = [marker(job_id, "pre"), marker(job_id, "post")]
    if args.install:
        if not args.allow_repair:
            raise ValueError("--install requires explicit --allow-repair")
        install_cron(lines, markers)
    result = {
        "installed": bool(args.install),
        "manifest": str(manifest_path),
        "watchdog_id": job_id,
        "cron_lines": lines,
        "scheduled_utc": {
            "pre": pre_at.astimezone(timezone.utc).isoformat(),
            "post": post_at.astimezone(timezone.utc).isoformat(),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
