# Aurion companion ingest smoke evidence — 2026-10-05

Scope: sanitized Aurion companion demonstrations only. Echoes of Aurion was not modified by this work.

Runtime: Hugging Face Sandbox, Python 3.12 slim, Linux x86_64.

Focused regression result: 6/6 tests passed.

Two independent ingest runs were byte-identical.

Normalized demonstration dataset:
`SHA-256 13c201d9cf396f84f0efe50a028ec771752f314c6b89df20c337908130674bec`

Ingest report:
`SHA-256 d0136269df5cbce456ec6acbbabe8eb8fb2870215c69b9958a5541f57b859f83`

The ingest accepts only pseudonymous SHA-256 sample/episode identifiers plus bounded numeric feature/state/action vectors. Extra account identity, free-text note fields, timestamps, captured frames, duplicate samples, duplicate episode/sequence positions, and wrong vector dimensions fail closed.

Reward semantics are explicitly absent. These demonstrations are not treated as discounted-return training records and do not gain production authority.
