import copy
import tempfile
import unittest
from pathlib import Path

from aurion_lab.companion_ingest import ContractError, normalize, read_jsonl, write_jsonl


class CompanionIngestTests(unittest.TestCase):
    def rows(self):
        root = Path(__file__).resolve().parents[1]
        return read_jsonl(root / "fixtures" / "sample_companion_demonstrations.jsonl")

    def test_fixture_normalizes(self):
        rows, report = normalize(self.rows())
        self.assertEqual(len(rows), 2)
        self.assertEqual(report["rows"], 2)
        self.assertEqual(report["episodes"], 1)
        self.assertEqual(report["reward_semantics"], "absent")
        self.assertFalse(report["production_authority"])

    def test_order_is_irrelevant(self):
        rows = self.rows()
        a, ar = normalize(rows)
        b, br = normalize(list(reversed(rows)))
        self.assertEqual(a, b)
        self.assertEqual(ar, br)

    def test_duplicate_sample_fails_closed(self):
        rows = self.rows()
        rows.append(copy.deepcopy(rows[0]))
        with self.assertRaises(ContractError):
            normalize(rows)

    def test_extra_identity_or_note_field_is_rejected(self):
        row = copy.deepcopy(self.rows()[0])
        row["account_id"] = 7
        with self.assertRaises(ContractError):
            normalize([row])
        row = copy.deepcopy(self.rows()[0])
        row["note"] = "free text"
        with self.assertRaises(ContractError):
            normalize([row])

    def test_invalid_vector_dimension_fails_closed(self):
        row = copy.deepcopy(self.rows()[0])
        row["observation"]["feature_vector"] = row["observation"]["feature_vector"][:-1]
        with self.assertRaises(ContractError):
            normalize([row])

    def test_normalized_jsonl_is_byte_reproducible(self):
        rows, _ = normalize(self.rows())
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.jsonl"
            b = Path(tmp) / "b.jsonl"
            write_jsonl(rows, a)
            write_jsonl(rows, b)
            self.assertEqual(a.read_bytes(), b.read_bytes())


if __name__ == "__main__":
    unittest.main()
