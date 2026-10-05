# Evidence archive smoke evidence — 2026-10-05

Scope: ARE-rLOGIC offline lab only. Echoes of Aurion was not modified.

Runtime: Hugging Face Sandbox, Python 3.12 slim, Linux x86_64.

Regression result: 30/30 tests passed.

Two independently produced evidence archives were byte-identical:

`SHA-256 486d5e59ca6a287cee3d2b0ec0b151b12cdf5c04ffe6e0b4ec99b8eeb5472a57`

Embedded manifest SHA-256:

`991b414402d4ac48de8df9891ef817cfd11dc3de39487f863ac29eb7ab1db440`

Verified embedded artifacts:

- split: `32aaba4bf49371f3a660054888b7bb6e9e7bf421b3c70ad484cbd42c321c2ce7`
- policy: `17bd88eac019e2674e1b1a90410397480b179bd962871708708c2f0941608561`
- audit: `5805360a5fe3b2fae10dfc38112062df76ae6e95f9d3a4b5790e9d5aff6bc231`

The archive uses fixed ZIP timestamps, stable file ordering, no ZIP comment, stored entries without compression, and normalized permissions. Identical evidence therefore yields identical archive bytes.

The bundle verifier rejects tampered entries, unexpected files, duplicate names, and unsafe paths. Packaging is refused unless the local manifest verifier passes first.

This is transport integrity only and does not authorize policy execution in Aurion.
