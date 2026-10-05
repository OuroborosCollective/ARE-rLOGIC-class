#!/usr/bin/env python3
"""Deterministic split-integrity and provenance guard for offline RL fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aurion_lab.offline_value import ContractError, canonical, read_jsonl, validate_transition

REPORT_SCHEMA = "aurion.rl.split_guard.v1"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def row_hash(row: dict[str, Any]) -> str:
    return hashlib.sha256(canonical(row).encode("utf-8")).hexdigest()


def inspect_split(path: Path) -> dict[str, Any]:
    rows = read_jsonl(path)
    episodes: set[str] = set()
    hashes: set[str] = set()
    duplicate_rows: set[str] = set()

    for row in rows:
        validate_transition(row)
        episode_id = row["episode_id"]
        episodes.add(episode_id)
        digest = row_hash(row)
        if digest in hashes:
            duplicate_rows.add(digest)
        hashes.add(digest)

    return {
        "path": path.as_posix(),
        "sha256": file_sha256(path),
        "rows": len(rows),
        "episodes": sorted(episodes),
        "unique_row_hashes": len(hashes),
        "duplicate_row_hashes": sorted(duplicate_rows),
        "_row_hashes": hashes,
    }


def guard(train_path: Path, validation_path: Path) -> dict[str, Any]:
    train = inspect_split(train_path)
    validation = inspect_split(validation_path)

    train_hashes = train.pop("_row_hashes")
    validation_hashes = validation.pop("_row_hashes")

    episode_overlap = sorted(set(train["episodes"]) & set(validation["episodes"]))
    row_overlap = sorted(train_hashes & validation_hashes)

    violations: list[str] = []
    if train["duplicate_row_hashes"]:
        violations.append("duplicate rows inside train split")
    if validation["duplicate_row_hashes"]:
        violations.append("duplicate rows inside validation split")
    if episode_overlap:
        violations.append("episode_id overlap between train and validation")
    if row_overlap:
        violations.append("exact row overlap between train and validation")

    return {
        "schema": REPORT_SCHEMA,
        "train": train,
        "validation": validation,
        "episode_overlap": episode_overlap,
        "exact_row_overlap_hashes": row_overlap,
        "status": "fail" if violations else "pass",
        "violations": violations,
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(canonical(report) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("train", type=Path)
    parser.add_argument("validation", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    report = guard(args.train, args.validation)
    write_report(report, args.output)
    print(
        f"split_guard status={report['status']} "
        f"train_rows={report['train']['rows']} "
        f"validation_rows={report['validation']['rows']} "
        f"episode_overlap={len(report['episode_overlap'])} "
        f"row_overlap={len(report['exact_row_overlap_hashes'])}"
    )
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
