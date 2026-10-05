# Evidence surface

Keep experiment evidence separate from production truth.

Each experiment should record:

- source dataset or fixture identity;
- code or notebook revision;
- seed and environment parameters;
- training/evaluation command;
- metrics and failures;
- produced model or policy reference;
- deterministic replay/evaluation result where available.

A green training run is not evidence that Aurion behavior changed. Production evidence belongs to the Aurion runtime and regression surfaces after a deterministic implementation is integrated there.
