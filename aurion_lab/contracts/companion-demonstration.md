# Aurion companion demonstration ingest

This lane accepts sanitized observation/action demonstrations exported from
Aurion's append-only companion memory.

Input schema: `aurion.rl.demonstration.v1`.

Required privacy boundary:

- no account identifier;
- no raw session identifier;
- no raw sample identifier;
- no timestamp;
- no free-text note;
- no captured frame;
- only pseudonymous SHA-256 episode/sample identifiers and bounded numeric vectors.

The lane contains no reward field. Companion demonstrations therefore must not be
fed into the empirical discounted-return policy as if a reward had been observed.

The ingest normalizes ordering, rejects duplicate sample identities or duplicate
episode/sequence positions, checks exact vector dimensions, and emits a
deterministic dataset hash plus implementation hash.

Aurion remains production authority. This lane is research evidence only.
