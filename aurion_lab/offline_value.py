#!/usr/bin/env python3
"""Deterministic offline value baseline for Aurion research exports.

This is an auditable baseline, not a production policy. It consumes logged
transitions, computes exact discounted returns with Decimal arithmetic, and emits
an advisory policy artifact. It never imports or calls the Aurion runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

TRANSITION_SCHEMA = "aurion.rl.transition.v1"
POLICY_SCHEMA = "aurion.rl.empirical_policy.v1"


class ContractError(ValueError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def decimal_from_json(value: Any, field: str) -> Decimal:
    if isinstance(value, bool):
        raise ContractError(f"{field} must be numeric, not boolean")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ContractError(f"{field} must be numeric") from exc


def decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    normalized = value.normalize()
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def state_key(observation: Any) -> str:
    return hashlib.sha256(canonical(observation).encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ContractError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ContractError(f"{path}:{line_number}: each row must be an object")
            rows.append(row)
    return rows


def validate_transition(row: dict[str, Any]) -> None:
    if row.get("schema") != TRANSITION_SCHEMA:
        raise ContractError(f"unsupported schema: {row.get('schema')!r}")
    for field in ("episode_id", "tick", "observation", "action", "reward", "terminal"):
        if field not in row:
            raise ContractError(f"{field} is required")
    if not isinstance(row["episode_id"], str) or not row["episode_id"]:
        raise ContractError("episode_id must be a non-empty string")
    if not isinstance(row["tick"], int) or isinstance(row["tick"], bool) or row["tick"] < 0:
        raise ContractError("tick must be a non-negative integer")
    if not isinstance(row["terminal"], bool):
        raise ContractError("terminal must be boolean")
    decimal_from_json(row["reward"], "reward")


def train(rows: list[dict[str, Any]], gamma: Decimal) -> dict[str, Any]:
    if gamma < 0 or gamma > 1:
        raise ContractError("gamma must be between 0 and 1 inclusive")

    episodes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        validate_transition(row)
        episodes[row["episode_id"]].append(row)

    # state -> action canonical JSON -> aggregate
    aggregates: dict[str, dict[str, dict[str, Any]]] = {}

    for episode_id in sorted(episodes):
        episode = sorted(episodes[episode_id], key=lambda item: item["tick"])
        ticks = [row["tick"] for row in episode]
        if len(ticks) != len(set(ticks)):
            raise ContractError(f"duplicate tick in episode {episode_id!r}")

        running_return = Decimal("0")
        for row in reversed(episode):
            reward = decimal_from_json(row["reward"], "reward")
            running_return = reward + gamma * running_return

            skey = state_key(row["observation"])
            akey = canonical(row["action"])
            state_bucket = aggregates.setdefault(skey, {})
            entry = state_bucket.setdefault(
                akey,
                {
                    "observation": row["observation"],
                    "action": row["action"],
                    "sum_return": Decimal("0"),
                    "samples": 0,
                },
            )
            entry["sum_return"] += running_return
            entry["samples"] += 1

    states: list[dict[str, Any]] = []
    for skey in sorted(aggregates):
        action_values: list[dict[str, Any]] = []
        for akey in sorted(aggregates[skey]):
            entry = aggregates[skey][akey]
            mean = entry["sum_return"] / Decimal(entry["samples"])
            action_values.append(
                {
                    "action": entry["action"],
                    "mean_return": decimal_text(mean),
                    "samples": entry["samples"],
                    "_action_key": akey,
                }
            )

        best = min(
            action_values,
            key=lambda item: (-Decimal(item["mean_return"]), item["_action_key"]),
        )
        clean_values = [
            {k: v for k, v in item.items() if k != "_action_key"} for item in action_values
        ]
        states.append(
            {
                "state_key": skey,
                "observation": aggregates[skey][sorted(aggregates[skey])[0]]["observation"],
                "best_action": best["action"],
                "best_mean_return": best["mean_return"],
                "action_values": clean_values,
            }
        )

    return {
        "schema": POLICY_SCHEMA,
        "gamma": decimal_text(gamma),
        "algorithm": "empirical_discounted_return_v1",
        "states": states,
    }


def write_model(model: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(canonical(model) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--gamma", default="1")
    args = parser.parse_args()

    gamma = decimal_from_json(args.gamma, "gamma")
    model = train(read_jsonl(args.input), gamma)
    write_model(model, args.output)
    print(f"wrote deterministic policy with {len(model['states'])} states to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
