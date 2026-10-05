import json
import tempfile
import unittest
from pathlib import Path

from aurion_lab.offline_value import ContractError
from aurion_lab.run_pipeline import run
from aurion_lab.verify_manifest import verify


class VerifyManifestTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def make_run(self, root: Path):
        return run(
            self.root() / "fixtures" / "sample_transitions.jsonl",
            self.root() / "fixtures" / "sample_validation_transitions.jsonl",
            root,
            "0.9",
        )

    def test_valid_manifest_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            self.make_run(out)
            report = verify(out / "manifest.json")
            self.assertEqual(report["status"], "pass")
            self.assertTrue(all(x["match"] for x in report["checks"]))

    def test_tampered_policy_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            self.make_run(out)
            (out / "policy.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(verify(out / "manifest.json")["status"], "fail")

    def test_missing_artifact_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            self.make_run(out)
            (out / "audit.json").unlink()
            self.assertEqual(verify(out / "manifest.json")["status"], "fail")

    def test_path_escape_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            self.make_run(out)
            path = out / "manifest.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["artifacts"]["policy"]["path"] = "../policy.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(ContractError):
                verify(path)


if __name__ == "__main__":
    unittest.main()
