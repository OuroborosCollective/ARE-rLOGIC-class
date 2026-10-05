#!/usr/bin/env python3
"""Fail-safe BoxLite capability probe.

This file does not install BoxLite and does not touch Aurion. It only reports whether
the current host appears capable of running the optional isolated executor.
"""

from __future__ import annotations

import importlib.util
import os
import platform


def main() -> int:
    system = platform.system().lower()
    machine = platform.machine().lower()
    installed = importlib.util.find_spec("boxlite") is not None
    kvm_exists = os.path.exists("/dev/kvm")
    kvm_access = os.access("/dev/kvm", os.R_OK | os.W_OK) if kvm_exists else False

    print(f"platform={system}/{machine}")
    print(f"boxlite_python_installed={str(installed).lower()}")

    if system == "linux":
        print(f"kvm_exists={str(kvm_exists).lower()}")
        print(f"kvm_read_write_access={str(kvm_access).lower()}")
        ready = installed and kvm_exists and kvm_access
    elif system == "darwin":
        ready = installed and machine in {"arm64", "aarch64"}
    else:
        ready = False

    print(f"boxlite_ready={str(ready).lower()}")
    if not ready:
        print("fallback=run aurion_lab/replay.py directly; no production dependency is required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
