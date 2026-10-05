#!/usr/bin/env python3
"""Deterministic source-code provenance for the offline evidence pipeline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

CORE_FILES = (
    "offline_value.py",
    "policy_audit.py",
    "split_guard.py",
    "run_pipeline.py",
    "verify_manifest.py",
    "pack_bundle.py",
    "verify_bundle.py",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect(root: Path | None = None) -> dict:
    base = root or Path(__file__).resolve().parent
    files = [{"path": name, "sha256": sha256(base / name)} for name in CORE_FILES]
    aggregate = hashlib.sha256(
        json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {"algorithm":"sha256-file-list-v1","files":files,"aggregate_sha256":aggregate}
