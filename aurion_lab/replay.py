#!/usr/bin/env python3
"""Deterministic contract smoke-test for Aurion offline RL exports.

This is deliberately not an RL policy. It proves that exported observations can be
validated and transformed into advisory candidate actions without importing or
calling the Aurion runtime.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

OBSERVATION_SCHEMA = "aurion.rl.observation.v1"
CANDIDATE_SCHEMA = "aurion.rl.candidate.v1"
MODEL_REF = "deterministic-baseline-v1"


class ContractError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def choose_action(available_actions: list[Any]) -> Any:
    if not available_actions:
        raise ContractError("available_actions must contain at least one action")
    return min(available_actions, key=_canonical)


def transform(record: dict[str, Any]) -> dict[str, Any]:
    if record.get("schema") != OBSERVATION_SCHEMA:
        raise ContractError(f"unsupported schema: {record.get('schema')!r}")
    if "episode_id" not in record or "tick" not in record:
        raise ContractError("episode_id and tick are required")
    actions = record.get("available_actions")
    if not isinstance(actions, list):
        raise ContractError("available_actions must be a list")

    return {
        "schema": CANDIDATE_SCHEMA,
        "episode_id": record["episode_id"],
        "tick": record["tick"],
        "action": choose_action(actions),
        "score": 0.0,
        "model_ref": MODEL_REF,
    }


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ContractError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ContractError(f"{path}:{line_number}: each row must be an object")
            yield value


def run(input_path: Path, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in read_jsonl(input_path):
            candidate = transform(record)
            handle.write(_canonical(candidate) + "\n")
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    count = run(args.input, args.output)
    print(f"wrote {count} deterministic candidate rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
