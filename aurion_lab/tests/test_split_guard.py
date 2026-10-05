import tempfile
import unittest
from pathlib import Path

from aurion_lab.split_guard import guard, write_report


class SplitGuardTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def train(self):
        return self.root() / "fixtures" / "sample_transitions.jsonl"

    def validation(self):
        return self.root() / "fixtures" / "sample_validation_transitions.jsonl"

    def test_fixture_split_passes(self):
        report = guard(self.train(), self.validation())
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["episode_overlap"], [])
        self.assertEqual(report["exact_row_overlap_hashes"], [])
        self.assertEqual(report["train"]["rows"], 6)
        self.assertEqual(report["validation"]["rows"], 3)

    def test_hashes_are_stable(self):
        a = guard(self.train(), self.validation())
        b = guard(self.train(), self.validation())
        self.assertEqual(a["train"]["sha256"], b["train"]["sha256"])
        self.assertEqual(a["validation"]["sha256"], b["validation"]["sha256"])

    def test_episode_overlap_fails(self):
        train = self.train().read_text(encoding="utf-8")
        validation = self.validation().read_text(encoding="utf-8").replace(
            '"validation-a"', '"episode-a"', 1
        )
        with tempfile.TemporaryDirectory() as tmp:
            train_path = Path(tmp) / "train.jsonl"
            validation_path = Path(tmp) / "validation.jsonl"
            train_path.write_text(train, encoding="utf-8")
            validation_path.write_text(validation, encoding="utf-8")
            report = guard(train_path, validation_path)
            self.assertEqual(report["status"], "fail")
            self.assertIn("episode-a", report["episode_overlap"])

    def test_exact_row_overlap_fails(self):
        first_train_row = self.train().read_text(encoding="utf-8").splitlines()[0]
        validation = self.validation().read_text(encoding="utf-8") + first_train_row + "\n"
        with tempfile.TemporaryDirectory() as tmp:
            validation_path = Path(tmp) / "validation.jsonl"
            validation_path.write_text(validation, encoding="utf-8")
            report = guard(self.train(), validation_path)
            self.assertEqual(report["status"], "fail")
            self.assertTrue(report["exact_row_overlap_hashes"])

    def test_report_is_byte_reproducible(self):
        report = guard(self.train(), self.validation())
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.json"
            b = Path(tmp) / "b.json"
            write_report(report, a)
            write_report(report, b)
            self.assertEqual(a.read_bytes(), b.read_bytes())


if __name__ == "__main__":
    unittest.main()
