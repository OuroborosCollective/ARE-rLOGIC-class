# Code provenance smoke evidence — 2026-10-05

Scope: ARE-rLOGIC offline lab only. Echoes of Aurion was not modified.

Runtime: Hugging Face Sandbox, Python 3.12 slim, Linux x86_64.

Regression result: 32/32 tests passed.

Two complete offline runs produced byte-identical manifests:

`SHA-256 8622b3f27d549ce464a0ae75b44cc9c69fc717ebcfad8135b6ac529998b3f98c`

The manifest now binds the exact source hashes of eight core offline-evidence modules.

Implementation aggregate:

`SHA-256 0ddfc92369d6a56458f4bbdb8a4e885bf262f0cfd15b0f180d29a83efab00916`

The provenance fingerprint is deterministic and includes the provenance logic itself. No timestamp, hostname, git remote, credential, or mutable runtime metadata is part of the fingerprint.

This binds evidence to the code that produced it; it still does not authorize production execution in Aurion.
