# Manifest verification contract

A run manifest is useful only if its referenced artifacts still match the hashes it
records.

`aurion.rl.manifest_verify.v1` verifies the local `split.json`, `policy.json`,
and `audit.json` files against the SHA-256 values recorded in
`aurion.rl.run_manifest.v1`.

The verifier fails closed when an artifact is missing, modified, or referenced by an
unsafe absolute/parent-traversal path.

This verifies integrity of the evidence bundle. It does not certify policy quality,
authorize Aurion execution, or prove the source data were semantically correct.
