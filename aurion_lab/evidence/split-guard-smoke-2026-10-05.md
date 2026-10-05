# Split guard smoke evidence — 2026-10-05

Scope: ARE-rLOGIC offline lab only. Echoes of Aurion was not modified.

Runtime: Hugging Face Sandbox, Python 3.12 slim, Linux x86_64.

Regression result: 19/19 tests passed.

Split guard result: pass.

- train rows: 6
- validation rows: 3
- train episodes: episode-a, episode-b, episode-c
- validation episodes: validation-a, validation-b, validation-c
- episode overlap: 0
- exact row overlap: 0
- duplicate train rows: 0
- duplicate validation rows: 0

Source file hashes:

- train SHA-256: `dab04cb6f33820883ea48a533acc38d39b479dcc40f0d96d34c49586382946b5`
- validation SHA-256: `80c1c1911666dad0ecd3871a8422052a7542a32242c65e79a4905c7d41e6654c`

Two independently emitted split reports were byte-identical:

`SHA-256 32aaba4bf49371f3a660054888b7bb6e9e7bf421b3c70ad484cbd42c321c2ce7`

The guard fails closed on duplicate rows, shared episode IDs, or exact cross-split row overlap. It is a provenance/leakage check, not a proof of statistical independence.

The offline policy and held-out policy audit also completed successfully in the same validation run. BoxLite remained optional and unavailable on the sandbox host; the fallback path stayed green.
