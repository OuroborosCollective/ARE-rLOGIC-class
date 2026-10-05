import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from aurion_lab.offline_value import ContractError
from aurion_lab.pack_bundle import pack
from aurion_lab.run_pipeline import run
from aurion_lab.verify_bundle import verify_bundle


class BundleTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def make_run(self, out: Path):
        run(
            self.root() / "fixtures" / "sample_transitions.jsonl",
            self.root() / "fixtures" / "sample_validation_transitions.jsonl",
            out,
            "0.9",
        )

    def test_bundle_is_byte_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run1 = root / "run1"
            run2 = root / "run2"
            self.make_run(run1)
            self.make_run(run2)
            bundle1 = root / "a.zip"
            bundle2 = root / "b.zip"
            self.assertEqual(pack(run1, bundle1), pack(run2, bundle2))
            self.assertEqual(bundle1.read_bytes(), bundle2.read_bytes())

    def test_valid_bundle_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run"
            self.make_run(run_dir)
            bundle = root / "bundle.zip"
            pack(run_dir, bundle)
            report = verify_bundle(bundle)
            self.assertEqual(report["status"], "pass")
            self.assertTrue(all(x["match"] for x in report["checks"]))

    def test_tampered_entry_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run"
            self.make_run(run_dir)
            bundle = root / "bundle.zip"
            pack(run_dir, bundle)

            rewritten = root / "tampered.zip"
            with zipfile.ZipFile(bundle, "r") as src, zipfile.ZipFile(rewritten, "w") as dst:
                for info in src.infolist():
                    data = src.read(info.filename)
                    if info.filename == "policy.json":
                        data = b"{}\n"
                    dst.writestr(info, data)

            self.assertEqual(verify_bundle(rewritten)["status"], "fail")

    def test_unexpected_entry_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run"
            self.make_run(run_dir)
            bundle = root / "bundle.zip"
            pack(run_dir, bundle)
            bad = root / "bad.zip"
            with zipfile.ZipFile(bundle, "r") as src, zipfile.ZipFile(bad, "w") as dst:
                for info in src.infolist():
                    dst.writestr(info, src.read(info.filename))
                dst.writestr("../escape.txt", b"no")
            with self.assertRaises(ContractError):
                verify_bundle(bad)


if __name__ == "__main__":
    unittest.main()
