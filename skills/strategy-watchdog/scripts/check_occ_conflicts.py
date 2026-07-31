#!/usr/bin/env python3
"""Classify exact-OCC conflicts from a normalized candidate/account snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SIDES = {
    "buy": "buy",
    "long": "buy",
    "sell": "sell",
    "short": "sell",
}


def normalized_side(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return SIDES.get(value.strip().lower())


def classify(payload: dict) -> dict:
    strategy_id = payload.get("strategy_id")
    idempotency_key = payload.get("idempotency_key")
    candidates = payload.get("candidate", [])
    existing = payload.get("existing", [])
    if not isinstance(candidates, list) or not isinstance(existing, list):
        raise ValueError("candidate and existing must be lists")

    by_occ: dict[str, list[dict]] = {}
    for item in existing:
        if not isinstance(item, dict):
            raise ValueError("each existing item must be an object")
        occ = item.get("occ")
        if isinstance(occ, str) and occ:
            by_occ.setdefault(occ, []).append(item)

    result = {
        "unrelated": [],
        "same_direction": [],
        "opposite_conflicts": [],
        "duplicates": [],
        "unknown": [],
    }
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("each candidate item must be an object")
        occ = candidate.get("occ")
        side = normalized_side(candidate.get("side"))
        if not isinstance(occ, str) or not occ or side is None:
            result["unknown"].append({"candidate": candidate, "reason": "invalid_candidate"})
            continue
        matches = by_occ.get(occ, [])
        if not matches:
            result["unrelated"].append({"occ": occ, "side": side})
            continue
        for item in matches:
            existing_side = normalized_side(item.get("side"))
            record = {
                "occ": occ,
                "candidate_side": side,
                "existing_side": existing_side,
                "existing_strategy_id": item.get("strategy_id"),
                "existing_idempotency_key": item.get("idempotency_key"),
            }
            if (
                strategy_id
                and idempotency_key
                and item.get("strategy_id") == strategy_id
                and item.get("idempotency_key") == idempotency_key
            ):
                result["duplicates"].append(record)
            elif existing_side is None:
                result["unknown"].append({**record, "reason": "unknown_existing_side"})
            elif existing_side == side:
                result["same_direction"].append(record)
            else:
                result["opposite_conflicts"].append(record)

    result["allowed"] = not any(
        result[key] for key in ("opposite_conflicts", "duplicates", "unknown")
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(classify(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
