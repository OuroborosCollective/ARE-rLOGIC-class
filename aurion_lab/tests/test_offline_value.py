import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from aurion_lab.offline_value import ContractError, read_jsonl, train, write_model


class OfflineValueTests(unittest.TestCase):
    def fixture_rows(self):
        root = Path(__file__).resolve().parents[1]
        return read_jsonl(root / "fixtures" / "sample_transitions.jsonl")

    def test_training_is_row_order_invariant(self):
        rows = self.fixture_rows()
        self.assertEqual(train(rows, Decimal("1")), train(list(reversed(rows)), Decimal("1")))

    def test_expected_best_action(self):
        model = train(self.fixture_rows(), Decimal("1"))
        hostile = next(state for state in model["states"] if state["observation"]["hostile"])
        self.assertEqual(hostile["best_action"]["type"], "attack")
        self.assertEqual(hostile["best_mean_return"], "3.5")

    def test_duplicate_tick_fails_closed(self):
        rows = self.fixture_rows()
        duplicate = dict(rows[0])
        rows.append(duplicate)
        with self.assertRaises(ContractError):
            train(rows, Decimal("1"))

    def test_invalid_gamma_fails_closed(self):
        with self.assertRaises(ContractError):
            train(self.fixture_rows(), Decimal("1.1"))

    def test_model_is_byte_reproducible(self):
        model = train(self.fixture_rows(), Decimal("0.9"))
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.json"
            b = Path(tmp) / "b.json"
            write_model(model, a)
            write_model(model, b)
            self.assertEqual(a.read_bytes(), b.read_bytes())


if __name__ == "__main__":
    unittest.main()
