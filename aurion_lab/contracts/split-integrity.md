# Split integrity contract

Offline policy evaluation is invalid if training and held-out validation data leak
across the boundary.

The deterministic split guard records:

- SHA-256 of each source file;
- row count and sorted episode IDs;
- duplicate rows inside each split;
- episode-ID overlap across train and validation;
- exact canonical-row overlap across train and validation.

The gate fails closed when any duplicate row, shared episode ID, or exact shared row
is detected.

Observation/state overlap is intentionally **not** rejected. A held-out split may
contain the same abstract observation reached in a different episode; the policy
audit needs this to determine whether an advisory recommendation is supported by
separate logged behavior.

This is a provenance and leakage gate, not a statistical independence proof.
