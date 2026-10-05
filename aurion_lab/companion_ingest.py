#!/usr/bin/env python3
"""Validate and normalize sanitized Aurion companion demonstrations."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

DEMONSTRATION_SCHEMA = "aurion.rl.demonstration.v1"
SOURCE_SCHEMA = "aurion-companion-memory.v1"
REPORT_SCHEMA = "aurion.rl.companion_ingest_report.v1"
EXPECTED_KEYS = {
    "schema", "source_schema", "sample_id", "episode_id",
    "sequence_index", "observation", "action",
}

class ContractError(ValueError):
    pass

def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def is_hex_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)

def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value == value and abs(value) != float("inf")

def validate_vector(value: Any, length: int, field: str, unit_interval: bool = False) -> None:
    if not isinstance(value, list) or len(value) != length:
        raise ContractError(f"{field} must be a list of length {length}")
    if not all(finite_number(item) for item in value):
        raise ContractError(f"{field} must contain finite numbers")
    if unit_interval and not all(0 <= item <= 1 for item in value):
        raise ContractError(f"{field} values must be within [0, 1]")

def validate_row(row: dict[str, Any]) -> None:
    keys = set(row)
    if keys != EXPECTED_KEYS:
        raise ContractError(f"unexpected row shape; extra={sorted(keys-EXPECTED_KEYS)} missing={sorted(EXPECTED_KEYS-keys)}")
    if row["schema"] != DEMONSTRATION_SCHEMA:
        raise ContractError("unsupported demonstration schema")
    if row["source_schema"] != SOURCE_SCHEMA:
        raise ContractError("unsupported source schema")
    if not is_hex_sha256(row["sample_id"]) or not is_hex_sha256(row["episode_id"]):
        raise ContractError("sample_id and episode_id must be lowercase SHA-256 hex")
    if not isinstance(row["sequence_index"], int) or isinstance(row["sequence_index"], bool) or row["sequence_index"] < 0:
        raise ContractError("sequence_index must be a non-negative integer")

    observation = row["observation"]
    if not isinstance(observation, dict) or set(observation) != {"feature_vector", "state_vector", "state_mask"}:
        raise ContractError("invalid observation shape")
    validate_vector(observation["feature_vector"], 16, "feature_vector")
    validate_vector(observation["state_vector"], 6, "state_vector")
    state_mask = observation["state_mask"]
    if not isinstance(state_mask, list) or len(state_mask) != 6 or not all(item in (0, 1) and not isinstance(item, bool) for item in state_mask):
        raise ContractError("state_mask must contain six 0/1 integers")

    action = row["action"]
    if not isinstance(action, dict) or set(action) != {"vector"}:
        raise ContractError("invalid action shape")
    validate_vector(action["vector"], 4, "action.vector", True)

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ContractError(f"{path}:{line_number}: invalid JSON") from exc
            if not isinstance(value, dict):
                raise ContractError(f"{path}:{line_number}: row must be an object")
            validate_row(value)
            rows.append(value)
    if not rows:
        raise ContractError("dataset must contain at least one row")
    return rows

def normalize(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    seen_samples = set()
    seen_positions = set()
    for row in rows:
        validate_row(row)
        sample_id = row["sample_id"]
        position = (row["episode_id"], row["sequence_index"])
        if sample_id in seen_samples:
            raise ContractError("duplicate sample_id")
        if position in seen_positions:
            raise ContractError("duplicate episode/sequence position")
        seen_samples.add(sample_id)
        seen_positions.add(position)
    normalized = sorted(rows, key=lambda row: (row["episode_id"], row["sequence_index"], row["sample_id"]))
    canonical_bytes = ("\n".join(canonical(row) for row in normalized) + "\n").encode("utf-8")
    report = {
        "schema": REPORT_SCHEMA,
        "source_schema": SOURCE_SCHEMA,
        "demonstration_schema": DEMONSTRATION_SCHEMA,
        "rows": len(normalized),
        "episodes": len({row["episode_id"] for row in normalized}),
        "dataset_sha256": sha256_bytes(canonical_bytes),
        "feature_vector_length": 16,
        "state_vector_length": 6,
        "action_vector_length": 4,
        "semantics": "human-demonstration-observation-action-only",
        "reward_semantics": "absent",
        "production_authority": False,
    }
    return normalized, report

def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(canonical(row) for row in rows) + "\n", encoding="utf-8", newline="\n")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("normalized_output", type=Path)
    parser.add_argument("report_output", type=Path)
    args = parser.parse_args()
    rows = read_jsonl(args.input)
    normalized, report = normalize(rows)
    write_jsonl(normalized, args.normalized_output)
    payload = {**report, "source_file_sha256": sha256_file(args.input), "implementation_sha256": sha256_file(Path(__file__).resolve())}
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.write_text(canonical(payload) + "\n", encoding="utf-8", newline="\n")
    print(f"companion_ingest rows={report['rows']} episodes={report['episodes']} dataset_sha256={report['dataset_sha256']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
