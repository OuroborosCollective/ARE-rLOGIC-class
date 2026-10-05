# Policy audit contract

The policy audit is deliberately conservative. It answers only:

1. Was a held-out validation observation represented in the learned policy artifact?
2. If represented, was the policy's recommended action actually observed for that
   same state in held-out logged behavior?

It does **not** estimate policy reward, causal uplift, regret, counterfactual value,
or production fitness.

Output schema: `aurion.rl.policy_audit.v1`.

The report separates states into:

- `supported`: known state, recommended action observed in held-out logs;
- `unsupported`: known state, recommended action not observed in held-out logs;
- `unknown`: held-out state absent from the policy artifact.

This gate exists to prevent a tiny offline fixture from being misrepresented as
proof that an RL policy is safe or better than Aurion's deterministic runtime.
Aurion remains authoritative.
