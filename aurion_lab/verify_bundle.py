#!/usr/bin/env python3
"""Verify a deterministic ARE-rLOGIC evidence ZIP without extracting it."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aurion_lab.offline_value import ContractError
from aurion_lab.pack_bundle import BUNDLE_FILES
from aurion_lab.run_pipeline import MANIFEST_SCHEMA

VERIFY_BUNDLE_SCHEMA = "aurion.rl.bundle_verify.v1"


def bytes_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_bundle(path: Path) -> dict[str, Any]:
    bundle_sha = file_sha256(path)

    with zipfile.ZipFile(path, "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise ContractError("bundle contains duplicate entry names")
        if tuple(sorted(names)) != tuple(sorted(BUNDLE_FILES)):
            raise ContractError(f"unexpected bundle entries: {names}")
        for name in names:
            p = Path(name)
            if p.is_absolute() or ".." in p.parts or len(p.parts) != 1:
                raise ContractError(f"unsafe bundle entry: {name}")

        manifest_bytes = archive.read("manifest.json")
        try:
            manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ContractError("invalid manifest.json in bundle") from exc

        if not isinstance(manifest, dict) or manifest.get("schema") != MANIFEST_SCHEMA:
            raise ContractError("unsupported or missing manifest schema")

        checks = []
        for artifact in ("split", "policy", "audit"):
            entry = manifest.get("artifacts", {}).get(artifact)
            if not isinstance(entry, dict):
                raise ContractError(f"missing artifact manifest entry: {artifact}")
            name = entry.get("path")
            expected = entry.get("sha256")
            if name not in BUNDLE_FILES or name == "manifest.json":
                raise ContractError(f"invalid bundled artifact path: {name!r}")
            if not isinstance(expected, str) or len(expected) != 64:
                raise ContractError(f"invalid artifact hash: {artifact}")
            actual = bytes_sha256(archive.read(name))
            checks.append({
                "artifact": artifact,
                "path": name,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "match": actual == expected,
            })

    ok = all(check["match"] for check in checks)
    return {
        "schema": VERIFY_BUNDLE_SCHEMA,
        "status": "pass" if ok else "fail",
        "bundle_sha256": bundle_sha,
        "manifest_sha256": bytes_sha256(manifest_bytes),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    report = verify_bundle(args.bundle)
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
