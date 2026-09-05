from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "docs/paper/fill-rehearsal/select_outcome_branches.py"
SKELETON = REPO / "docs/paper/draft-v2-skeleton.md"
SPEC = importlib.util.spec_from_file_location("select_outcome_branches", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
SELECTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SELECTOR)


class SelectorGuardTests(unittest.TestCase):
    @staticmethod
    def _draft(words: int, comment: str = "") -> str:
        body = " ".join("word" for _ in range(words))
        return f"## Abstract\n\n{body}\n{comment}\n## 1. Introduction\n"

    def test_rendered_abstract_word_budget_accepts_250_and_rejects_251(self) -> None:
        self.assertEqual(SELECTOR._check_abstract_word_budget(self._draft(250)), 250)
        with self.assertRaisesRegex(ValueError, "rendered Abstract has 251 words"):
            SELECTOR._check_abstract_word_budget(self._draft(251))

    def test_single_outcome_copies_exact_bytes_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "selected.md"
            command = [sys.executable, str(SCRIPT), "--source", str(SKELETON),
                       "--output", str(output), "--outcome", "METHODS_DIAGNOSTIC"]
            result = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), SKELETON.read_bytes())
            result = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("already exists", result.stderr)
            self.assertEqual(output.read_bytes(), SKELETON.read_bytes())

    def test_retired_outcomes_are_rejected_without_output(self) -> None:
        for outcome in ("A", "B", "REFUSAL"):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "forbidden.md"
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), "--source", str(SKELETON),
                     "--output", str(output), "--outcome", outcome],
                    cwd=REPO, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())

    def test_guard_rejects_branch_fill_headline_and_limitation_regressions(self) -> None:
        source = SKELETON.read_text(encoding="utf-8")
        self.assertLessEqual(SELECTOR.validate_methods_draft(source), 250)
        mutations = (
            source + "\n<!-- OUTCOME-BRANCH:A:START -->",
            source + "\n## First-use audit ledger\n",
            source.replace("(protocol/prospective-comparison-protocol.md)", "(missing.md)"),
            source + "\n[protocol](protocol/prospective-comparison-protocol.md)",
            source + "\n### Measured admission rules\n",
            source.replace("## 4. Historical", "[FILL:PG-08]\n## 4. Historical"),
            source + "\n<!-- [FILL:DS-32] -->",
            source.replace("49 of 59 fitted offsets", "50 of 59 fitted offsets", 1),
            source.replace(SELECTOR.TRANSFER_LIMITATION_SENTENCE, "", 1),
            source.replace("(figures/fig4_edge_excursions.svg)", "(other.svg)"),
        )
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=index), self.assertRaises(ValueError):
                SELECTOR.validate_methods_draft(mutation)

    def test_reader_facing_counts_exclude_comments(self) -> None:
        draft = self._draft(3, f"<!-- {SELECTOR.TRANSFER_LIMITATION_SENTENCE} -->")
        self.assertNotIn(SELECTOR.TRANSFER_LIMITATION_SENTENCE,
                         SELECTOR._reader_facing_text(draft))
        self.assertEqual(SELECTOR._abstract_word_count(draft), 3)


if __name__ == "__main__":
    unittest.main()
