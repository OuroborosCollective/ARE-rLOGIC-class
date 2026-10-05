#!/usr/bin/env python3
"""Run the complete offline evidence pipeline and emit a deterministic manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aurion_lab.code_provenance import collect as collect_code_provenance
from aurion_lab.offline_value import decimal_from_json, read_jsonl, train, write_model
from aurion_lab.policy_audit import audit, write_report
from aurion_lab.split_guard import guard, write_report as write_split_report

MANIFEST_SCHEMA = "aurion.rl.run_manifest.v1"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run(train_path: Path, validation_path: Path, output_dir: Path, gamma_text: str) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    gamma = decimal_from_json(gamma_text, "gamma")

    split_path = output_dir / "split.json"
    policy_path = output_dir / "policy.json"
    audit_path = output_dir / "audit.json"
    manifest_path = output_dir / "manifest.json"

    split = guard(train_path, validation_path)
    write_split_report(split, split_path)
    if split["status"] != "pass":
        raise SystemExit("split guard failed")

    policy = train(read_jsonl(train_path), gamma)
    write_model(policy, policy_path)

    audit_report = audit(policy, read_jsonl(validation_path))
    write_report(audit_report, audit_path)

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "gamma": str(gamma),
        "inputs": {
            "train": {"path": train_path.as_posix(), "sha256": sha256(train_path)},
            "validation": {"path": validation_path.as_posix(), "sha256": sha256(validation_path)},
        },
        "implementation": collect_code_provenance(),
        "artifacts": {
            "split": {"path": "split.json", "sha256": sha256(split_path)},
            "policy": {"path": "policy.json", "sha256": sha256(policy_path)},
            "audit": {"path": "audit.json", "sha256": sha256(audit_path)},
        },
        "summary": {
            "split_status": split["status"],
            "known_states": audit_report["known_states"],
            "unknown_states": audit_report["unknown_states"],
            "supported_recommendation_states": audit_report["supported_recommendation_states"],
            "unsupported_recommendation_states": audit_report["unsupported_recommendation_states"],
        },
    }
    manifest_path.write_text(canonical(manifest) + "\n", encoding="utf-8", newline="\n")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("train", type=Path)
    parser.add_argument("validation", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--gamma", default="0.9")
    args = parser.parse_args()
    manifest = run(args.train, args.validation, args.output_dir, args.gamma)
    print(canonical(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
