#!/usr/bin/env python3
"""Conservative, deterministic audit for advisory offline policy artifacts.

This tool does not estimate causal policy value. It only checks evidence support:
whether validation observations are represented in the learned artifact and whether
the recommended action is present in the held-out logged behavior for that state.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from aurion_lab.offline_value import (
    ContractError,
    POLICY_SCHEMA,
    TRANSITION_SCHEMA,
    canonical,
    read_jsonl,
    state_key,
    validate_transition,
)

AUDIT_SCHEMA = "aurion.rl.policy_audit.v1"


def read_policy(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("policy must be a JSON object")
    if value.get("schema") != POLICY_SCHEMA:
        raise ContractError(f"unsupported policy schema: {value.get('schema')!r}")
    states = value.get("states")
    if not isinstance(states, list):
        raise ContractError("policy states must be a list")
    return value


def audit(policy: dict[str, Any], validation_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if policy.get("schema") != POLICY_SCHEMA:
        raise ContractError(f"unsupported policy schema: {policy.get('schema')!r}")

    policy_by_state: dict[str, dict[str, Any]] = {}
    for state in policy.get("states", []):
        if not isinstance(state, dict):
            raise ContractError("policy states must contain objects")
        skey = state.get("state_key")
        if not isinstance(skey, str) or not skey:
            raise ContractError("policy state_key must be a non-empty string")
        if skey in policy_by_state:
            raise ContractError(f"duplicate policy state_key: {skey}")
        if "best_action" not in state:
            raise ContractError(f"policy state {skey} is missing best_action")
        policy_by_state[skey] = state

    observed_actions: dict[str, set[str]] = defaultdict(set)
    observations: dict[str, Any] = {}
    validation_count = 0

    for row in validation_rows:
        validate_transition(row)
        if row.get("schema") != TRANSITION_SCHEMA:
            raise ContractError(f"unsupported validation schema: {row.get('schema')!r}")
        skey = state_key(row["observation"])
        observations[skey] = row["observation"]
        observed_actions[skey].add(canonical(row["action"]))
        validation_count += 1

    known_states = sorted(set(observed_actions) & set(policy_by_state))
    unknown_states = sorted(set(observed_actions) - set(policy_by_state))

    supported_states = []
    unsupported_states = []

    for skey in known_states:
        best_action = policy_by_state[skey]["best_action"]
        action_key = canonical(best_action)
        entry = {
            "state_key": skey,
            "observation": observations[skey],
            "recommended_action": best_action,
            "held_out_observed_actions": [
                json.loads(action) for action in sorted(observed_actions[skey])
            ],
        }
        if action_key in observed_actions[skey]:
            supported_states.append(entry)
        else:
            unsupported_states.append(entry)

    return {
        "schema": AUDIT_SCHEMA,
        "policy_schema": POLICY_SCHEMA,
        "validation_rows": validation_count,
        "validation_unique_states": len(observed_actions),
        "known_states": len(known_states),
        "unknown_states": len(unknown_states),
        "supported_recommendation_states": len(supported_states),
        "unsupported_recommendation_states": len(unsupported_states),
        "supported": supported_states,
        "unsupported": unsupported_states,
        "unknown": [
            {
                "state_key": skey,
                "observation": observations[skey],
                "held_out_observed_actions": [
                    json.loads(action) for action in sorted(observed_actions[skey])
                ],
            }
            for skey in unknown_states
        ],
        "interpretation": (
            "Evidence-support audit only. Agreement with held-out logged actions is not "
            "a causal estimate of policy quality or reward."
        ),
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(canonical(report) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("policy", type=Path)
    parser.add_argument("validation", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    report = audit(read_policy(args.policy), read_jsonl(args.validation))
    write_report(report, args.output)
    print(
        "audit "
        f"known={report['known_states']} "
        f"unknown={report['unknown_states']} "
        f"supported={report['supported_recommendation_states']} "
        f"unsupported={report['unsupported_recommendation_states']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
