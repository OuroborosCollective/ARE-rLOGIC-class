# Replay smoke evidence — 2026-10-05

Scope: isolated ARE-rLOGIC offline lab only. No Echoes of Aurion repository or runtime was modified.

## Runtime

Execution environment: Hugging Face Sandbox, Python 3.12 slim, Linux x86_64.

Command surface:

```text
python -m unittest discover -s aurion_lab/tests -v
python aurion_lab/replay.py aurion_lab/fixtures/sample_observations.jsonl /tmp/out1.jsonl
python aurion_lab/replay.py aurion_lab/fixtures/sample_observations.jsonl /tmp/out2.jsonl
sha256sum /tmp/out1.jsonl /tmp/out2.jsonl
cmp /tmp/out1.jsonl /tmp/out2.jsonl
python aurion_lab/boxlite_preflight.py
```

## Regression

4/4 tests passed:

- action choice is invariant to available-action ordering;
- empty action sets fail closed;
- repeated file replay is byte-reproducible;
- equivalent JSON input produces stable candidate output.

## Determinism evidence

Both independent replay outputs produced the same SHA-256:

```text
c34042fd00b08a423e72a760c01cc4b77a9b1da39ae84bff51a3f9bb26b2fdc5
```

Each replay wrote exactly 3 candidate rows.

## BoxLite capability probe

The validation sandbox reported:

```text
platform=linux/x86_64
boxlite_python_installed=false
kvm_exists=false
kvm_read_write_access=false
boxlite_ready=false
fallback=run aurion_lab/replay.py directly; no production dependency is required
```

Conclusion: the baseline works without BoxLite. BoxLite remains an optional isolation layer on hosts where its runtime and hardware virtualization requirements are satisfied.

## Hugging Face dataset boundary

The existing private `Thorsu/miha-evidence` dataset was inspected read-only. It currently exposes 8 rows (7 train, 1 validation) and already carries reinforcement-learning and deterministic-evaluation metadata. No dataset files were modified, copied, transformed, or written by this work.
