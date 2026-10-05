import unittest
from pathlib import Path
from aurion_lab.code_provenance import CORE_FILES, collect

class CodeProvenanceTests(unittest.TestCase):
    def test_provenance_is_stable_and_complete(self):
        a = collect()
        b = collect()
        self.assertEqual(a, b)
        self.assertEqual([x["path"] for x in a["files"]], list(CORE_FILES))
        self.assertEqual(len(a["aggregate_sha256"]), 64)

    def test_all_referenced_files_exist(self):
        root = Path(__file__).resolve().parents[1]
        for name in CORE_FILES:
            self.assertTrue((root / name).is_file(), name)

if __name__ == "__main__":
    unittest.main()
