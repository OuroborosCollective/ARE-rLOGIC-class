import tempfile
import unittest
from pathlib import Path

from aurion_lab.run_pipeline import run, sha256


class RunPipelineTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def test_end_to_end_manifest_is_reproducible(self):
        train = self.root() / "fixtures" / "sample_transitions.jsonl"
        validation = self.root() / "fixtures" / "sample_validation_transitions.jsonl"
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a"
            b = Path(tmp) / "b"
            ma = run(train, validation, a, "0.9")
            mb = run(train, validation, b, "0.9")
            self.assertEqual(ma["summary"], mb["summary"])
            self.assertEqual(ma["inputs"], mb["inputs"])
            self.assertEqual(ma["artifacts"]["policy"]["sha256"], mb["artifacts"]["policy"]["sha256"])
            self.assertEqual(ma["artifacts"]["audit"]["sha256"], mb["artifacts"]["audit"]["sha256"])
            self.assertEqual(ma["artifacts"]["split"]["sha256"], mb["artifacts"]["split"]["sha256"])

    def test_manifest_links_real_artifacts(self):
        train = self.root() / "fixtures" / "sample_transitions.jsonl"
        validation = self.root() / "fixtures" / "sample_validation_transitions.jsonl"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            manifest = run(train, validation, out, "0.9")
            for name in ("split", "policy", "audit"):
                artifact = out / f"{name}.json"
                self.assertEqual(manifest["artifacts"][name]["sha256"], sha256(artifact))

    def test_expected_summary(self):
        train = self.root() / "fixtures" / "sample_transitions.jsonl"
        validation = self.root() / "fixtures" / "sample_validation_transitions.jsonl"
        with tempfile.TemporaryDirectory() as tmp:
            manifest = run(train, validation, Path(tmp) / "run", "0.9")
            self.assertEqual(manifest["summary"]["split_status"], "pass")
            self.assertEqual(manifest["summary"]["known_states"], 2)
            self.assertEqual(manifest["summary"]["unknown_states"], 1)
            self.assertEqual(manifest["summary"]["supported_recommendation_states"], 1)
            self.assertEqual(manifest["summary"]["unsupported_recommendation_states"], 1)


if __name__ == "__main__":
    unittest.main()
