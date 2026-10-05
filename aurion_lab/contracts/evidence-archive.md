# Evidence archive contract

A verified offline run can be packaged as a portable deterministic ZIP containing
exactly four files:

- `manifest.json`
- `split.json`
- `policy.json`
- `audit.json`

The archive uses fixed metadata, fixed ordering, no ZIP comment, and stored entries
without compression so identical evidence yields identical archive bytes across
repeated runs.

Packaging is refused unless the local manifest verifier passes first.

The bundle verifier reads the ZIP in place, rejects duplicate/unexpected/unsafe
entry names, and rechecks the split/policy/audit hashes against the embedded
manifest.

This is transport integrity only. It does not authorize production use in Aurion or
claim that an advisory policy is safe.
