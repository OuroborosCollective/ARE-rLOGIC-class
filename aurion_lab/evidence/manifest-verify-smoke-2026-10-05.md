# Manifest verification smoke evidence — 2026-10-05

Scope: ARE-rLOGIC offline lab only. Echoes of Aurion was not modified.

Runtime: Hugging Face Sandbox, Python 3.12 slim, Linux x86_64.

Regression result: 26/26 tests passed.

Valid evidence bundle verification result: pass.

Manifest SHA-256:
`991b414402d4ac48de8df9891ef817cfd11dc3de39487f863ac29eb7ab1db440`

Verified artifact hashes:

- split: `32aaba4bf49371f3a660054888b7bb6e9e7bf421b3c70ad484cbd42c321c2ce7`
- policy: `17bd88eac019e2674e1b1a90410397480b179bd962871708708c2f0941608561`
- audit: `5805360a5fe3b2fae10dfc38112062df76ae6e95f9d3a4b5790e9d5aff6bc231`

Tamper test: replacing `policy.json` with a different payload made verification fail with exit code 2 and a hash mismatch while unaffected artifacts still verified correctly.

Additional fail-closed tests cover missing artifacts and parent-traversal/absolute artifact paths.

The verifier checks evidence-bundle integrity only. It does not certify policy quality or authorize execution in Aurion.
