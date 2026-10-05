# Offline value smoke evidence — 2026-10-05

Scope: ARE-rLOGIC offline lab only. Echoes of Aurion was not modified.

Runtime: Hugging Face Sandbox, Python 3.12 slim, Linux x86_64.

Regression result: 9/9 tests passed.

Deterministic replay output:
`SHA-256 c34042fd00b08a423e72a760c01cc4b77a9b1da39ae84bff51a3f9bb26b2fdc5`

Deterministic offline policy output:
`SHA-256 17bd88eac019e2674e1b1a90410397480b179bd962871708708c2f0941608561`

Two independent policy runs were byte-identical. The fixture produced two empirical states; for the hostile fixture state the advisory best action was `attack` with exact discounted mean return `3.4` at `gamma=0.9`.

The algorithm uses exact decimal arithmetic, explicit gamma, canonical ordering, duplicate-tick rejection, and no randomness or third-party Python dependency.

BoxLite was unavailable in the validation sandbox because the Python package and `/dev/kvm` were absent; the fallback path remained green. No MIHA/Hugging Face dataset was changed.
