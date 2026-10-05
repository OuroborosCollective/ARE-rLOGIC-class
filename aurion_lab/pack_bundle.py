#!/usr/bin/env python3
"""Create a deterministic portable ZIP for a verified offline evidence run."""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aurion_lab.verify_manifest import verify

BUNDLE_FILES = ("audit.json", "manifest.json", "policy.json", "split.json")
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pack(run_dir: Path, output: Path) -> str:
    manifest_path = run_dir / "manifest.json"
    report = verify(manifest_path)
    if report["status"] != "pass":
        raise SystemExit("manifest verification failed; refusing to pack")

    missing = [name for name in BUNDLE_FILES if not (run_dir / name).is_file()]
    if missing:
        raise SystemExit(f"missing bundle files: {', '.join(missing)}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as archive:
        archive.comment = b""
        for name in BUNDLE_FILES:
            info = zipfile.ZipInfo(filename=name, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.extra = b""
            info.comment = b""
            archive.writestr(info, (run_dir / name).read_bytes())

    return sha256(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    digest = pack(args.run_dir, args.output)
    print(f"bundle_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
