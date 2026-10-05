#!/usr/bin/env python3
"""Verify an offline run manifest and all referenced local artifacts fail-closed."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aurion_lab.offline_value import ContractError
from aurion_lab.run_pipeline import MANIFEST_SCHEMA, sha256

VERIFY_SCHEMA = "aurion.rl.manifest_verify.v1"


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("manifest must be a JSON object")
    if value.get("schema") != MANIFEST_SCHEMA:
        raise ContractError(f"unsupported manifest schema: {value.get('schema')!r}")
    return value


def verify(manifest_path: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    root = manifest_path.parent
    checks: list[dict[str, Any]] = []

    for name in ("split", "policy", "audit"):
        entry = manifest.get("artifacts", {}).get(name)
        if not isinstance(entry, dict):
            raise ContractError(f"artifact entry missing: {name}")
        rel = entry.get("path")
        expected = entry.get("sha256")
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise ContractError(f"unsafe artifact path for {name}")
        if not isinstance(expected, str) or len(expected) != 64:
            raise ContractError(f"invalid artifact hash for {name}")
        target = root / rel
        exists = target.is_file()
        actual = sha256(target) if exists else None
        checks.append({
            "artifact": name,
            "path": rel,
            "exists": exists,
            "expected_sha256": expected,
            "actual_sha256": actual,
            "match": exists and actual == expected,
        })

    ok = all(item["match"] for item in checks)
    return {
        "schema": VERIFY_SCHEMA,
        "manifest_sha256": sha256(manifest_path),
        "status": "pass" if ok else "fail",
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    report = verify(args.manifest)
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
