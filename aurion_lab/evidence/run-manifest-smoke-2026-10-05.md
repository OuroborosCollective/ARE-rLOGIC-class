# Run manifest smoke evidence — 2026-10-05

Scope: ARE-rLOGIC offline lab only. Echoes of Aurion was not modified.

Runtime: Hugging Face Sandbox, Python 3.12 slim, Linux x86_64.

Regression result: 22/22 tests passed.

The complete offline evidence pipeline was executed twice from identical inputs and parameters. Both runs produced byte-identical manifests:

`SHA-256 991b414402d4ac48de8df9891ef817cfd11dc3de39487f863ac29eb7ab1db440`

The manifest binds these deterministic artifacts:

- split report: `32aaba4bf49371f3a660054888b7bb6e9e7bf421b3c70ad484cbd42c321c2ce7`
- policy: `17bd88eac019e2674e1b1a90410397480b179bd962871708708c2f0941608561`
- audit: `5805360a5fe3b2fae10dfc38112062df76ae6e95f9d3a4b5790e9d5aff6bc231`

Input provenance:

- train: `dab04cb6f33820883ea48a533acc38d39b479dcc40f0d96d34c49586382946b5`
- validation: `80c1c1911666dad0ecd3871a8422052a7542a32242c65e79a4905c7d41e6654c`

A first implementation accidentally encoded the output-directory path into the manifest, causing two otherwise identical runs to differ. Runtime validation caught this. The manifest was corrected to use stable relative artifact names and the exact fixed commit was revalidated successfully.

The manifest contains no timestamp, host identity, random identifier, remote URL, credential, or mutable runtime state. It is evidence linkage only and does not authorize production execution in Aurion.

BoxLite remained optional and unavailable on the validation host; the fallback path stayed green.
