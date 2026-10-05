# Policy audit smoke evidence — 2026-10-05

Scope: ARE-rLOGIC offline lab only. Echoes of Aurion was not modified.

Runtime: Hugging Face Sandbox, Python 3.12 slim, Linux x86_64.

Regression result: 14/14 tests passed.

Offline policy artifact:
`SHA-256 17bd88eac019e2674e1b1a90410397480b179bd962871708708c2f0941608561`

Policy audit artifact:
`SHA-256 5805360a5fe3b2fae10dfc38112062df76ae6e95f9d3a4b5790e9d5aff6bc231`

Two independent audit runs were byte-identical.

Held-out fixture audit:

- validation rows: 3
- unique validation states: 3
- known states: 2
- unknown states: 1
- supported recommendations: 1
- unsupported recommendations: 1

The audit deliberately does not report expected reward, causal policy value, regret, or production fitness. It only records held-out evidence support for advisory recommendations.

A direct CLI execution bug was found during runtime validation (`ModuleNotFoundError` when invoking `python aurion_lab/policy_audit.py`). The CLI bootstrap was corrected and the exact resulting commit was revalidated successfully.

BoxLite remained unavailable in the validation sandbox because the Python package and `/dev/kvm` were absent; the fallback path stayed green.
