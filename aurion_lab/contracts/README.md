# Offline contracts

The first integration contract is intentionally file-based and read-only from the point of view of Aurion.

## Observation input

Recommended JSONL envelope:

```json
{"schema":"aurion.rl.observation.v1","episode_id":"...","tick":0,"observation":{},"available_actions":[]}
```

Rules:

- every row must be replayable from captured evidence;
- timestamps are metadata, not simulation truth;
- no live Aurion endpoint is required;
- no credentials or secrets belong in datasets.

## Candidate output

Recommended JSONL envelope:

```json
{"schema":"aurion.rl.candidate.v1","episode_id":"...","tick":0,"action":{},"score":0.0,"model_ref":"..."}
```

Candidate output is advisory only. It cannot be executed by Aurion without an explicit deterministic adapter implemented and tested in the Aurion repository.
