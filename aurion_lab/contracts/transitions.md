# Transition contract

The offline value baseline consumes JSONL records with schema
`aurion.rl.transition.v1`.

Required fields:

```json
{
  "schema": "aurion.rl.transition.v1",
  "episode_id": "episode-a",
  "tick": 0,
  "observation": {},
  "action": {},
  "reward": 0,
  "terminal": false
}
```

Rules:

- records are research exports only; they are not production state;
- `episode_id` and `tick` identify replay order;
- duplicate ticks within an episode fail closed;
- rewards are parsed with exact decimal arithmetic;
- `gamma` is explicit and constrained to `0 <= gamma <= 1`;
- output is advisory `aurion.rl.empirical_policy.v1` data;
- ties are resolved by canonical JSON action ordering so repeated runs are deterministic;
- no output from this lab may execute inside Aurion without a separate deterministic Aurion implementation and its normal runtime/regression/evidence gates.

The baseline intentionally uses no randomness and no third-party Python dependency.
