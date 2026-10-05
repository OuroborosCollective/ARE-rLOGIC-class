import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from aurion_lab.offline_value import ContractError, read_jsonl, train, write_model
from aurion_lab.policy_audit import audit, write_report


class PolicyAuditTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def policy(self):
        rows = read_jsonl(self.root() / "fixtures" / "sample_transitions.jsonl")
        return train(rows, Decimal("0.9"))

    def validation(self):
        return read_jsonl(self.root() / "fixtures" / "sample_validation_transitions.jsonl")

    def test_expected_support_counts(self):
        report = audit(self.policy(), self.validation())
        self.assertEqual(report["validation_rows"], 3)
        self.assertEqual(report["validation_unique_states"], 3)
        self.assertEqual(report["known_states"], 2)
        self.assertEqual(report["unknown_states"], 1)
        self.assertEqual(report["supported_recommendation_states"], 1)
        self.assertEqual(report["unsupported_recommendation_states"], 1)

    def test_row_order_is_irrelevant(self):
        rows = self.validation()
        self.assertEqual(audit(self.policy(), rows), audit(self.policy(), list(reversed(rows))))

    def test_duplicate_policy_state_fails_closed(self):
        policy = self.policy()
        policy["states"].append(dict(policy["states"][0]))
        with self.assertRaises(ContractError):
            audit(policy, self.validation())

    def test_report_is_byte_reproducible(self):
        report = audit(self.policy(), self.validation())
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.json"
            b = Path(tmp) / "b.json"
            write_report(report, a)
            write_report(report, b)
            self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_report_never_claims_reward_quality(self):
        report = audit(self.policy(), self.validation())
        self.assertIn("not a causal estimate", report["interpretation"])
        serialized = json.dumps(report)
        self.assertNotIn("expected_reward", serialized)
        self.assertNotIn("policy_value", serialized)


if __name__ == "__main__":
    unittest.main()
