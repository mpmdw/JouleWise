"""Desk-only migration checks; no suppliers, external corpus, or paper writes."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs/paper"
SELECTOR = PAPER / "fill-rehearsal/select_outcome_branches.py"
spec = importlib.util.spec_from_file_location("migration_selector", SELECTOR)
selector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selector)


class PaperSuccessorMigrationTests(unittest.TestCase):


    def test_current_selector_rejects_legacy_outcomes(self):
        for outcome in ("A", "B", "REFUSAL"):
            with self.subTest(outcome=outcome):
                result = subprocess.run(
                    [sys.executable, str(SELECTOR), "--outcome", outcome],
                    capture_output=True, text=True, cwd=ROOT,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("invalid choice", result.stderr)

    def test_current_selector_copies_fresh_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "successor.md"
            command = [sys.executable, str(SELECTOR), "--source",
                       str(PAPER / "draft-v2-skeleton.md"), "--output", str(output),
                       "--outcome", "METHODS_DIAGNOSTIC"]
            result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), (PAPER / "draft-v2-skeleton.md").read_bytes())
            again = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(again.returncode, 2)
            self.assertIn("already exists", again.stderr)
            self.assertLessEqual(selector.validate_methods_draft(output.read_text()), 250)
            same_path = subprocess.run(
                [sys.executable, str(SELECTOR), "--source", str(output),
                 "--output", str(output), "--outcome", "METHODS_DIAGNOSTIC"],
                capture_output=True, text=True, cwd=ROOT,
            )
            self.assertEqual(same_path.returncode, 2)
            self.assertIn("must differ", same_path.stderr)
            self.assertEqual(output.read_bytes(), (PAPER / "draft-v2-skeleton.md").read_bytes())

    def test_retired_fills_and_overlong_abstract_refuse(self):
        article = (PAPER / "draft-v2-skeleton.md").read_text(encoding="utf-8")
        for marker in ("DS-32", "PG-08", "OB-01", "OR-01", "R_example", "V5-example"):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                selector.validate_methods_draft(article + f"\n<!-- [FILL:{marker}] -->")
        with self.assertRaisesRegex(ValueError, "limit is 250"):
            selector.validate_methods_draft(article.replace(
                "## Abstract\n", "## Abstract\n" + "extra " * 251 + "\n", 1))


if __name__ == "__main__":
    unittest.main()
