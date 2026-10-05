# Run manifest contract

A complete offline experiment run emits one manifest with schema
`aurion.rl.run_manifest.v1`.

The manifest binds together:

- exact train and validation input SHA-256 hashes;
- split-integrity artifact hash;
- learned advisory policy artifact hash;
- held-out policy-audit artifact hash;
- explicit gamma;
- compact audit summary counts.

The manifest is deterministic for identical inputs and parameters. It contains no
timestamp, hostname, random identifier, remote URL, credential, or mutable runtime
state.

The manifest is evidence linkage only. It does not authorize production execution
inside Aurion.
