from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "docs" / "paper" / "fill-rehearsal" / "select_outcome_branches.py"
SKELETON = REPO / "docs" / "paper" / "draft-v2-skeleton.md"
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

    def test_every_selected_outcome_retains_three_fixed_limitations(self) -> None:
        limitation = SELECTOR.TRANSFER_LIMITATION_SENTENCE
        source_text = SKELETON.read_text(encoding="utf-8")
        self.assertEqual(source_text.count(limitation), 9)
        self.assertNotIn("[FILL:TR-01]", source_text)

        for outcome in SELECTOR.BRANCHES:
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "selected.md"
                result = subprocess.run(
                    (
                        sys.executable,
                        str(SCRIPT),
                        "--source",
                        str(SKELETON),
                        "--output",
                        str(output),
                        "--outcome",
                        outcome,
                    ),
                    cwd=REPO,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                rendered = output.read_text(encoding="utf-8")
                self.assertEqual(rendered.count(limitation), len(SELECTOR.GROUPS))
                self.assertIn("transfer_limitations=3", result.stdout)

    def test_selected_branches_construct_allocation_and_preserve_verdicts(self) -> None:
        source = SKELETON.read_text(encoding="utf-8")
        for outcome in SELECTOR.BRANCHES:
            with self.subTest(outcome=outcome):
                selected = source
                for group in SELECTOR.GROUPS:
                    selected = SELECTOR._select_group(selected, group, outcome)
                abstract = selected.split("## Abstract\n", 1)[1].split(
                    "\n## 1. Introduction", 1
                )[0]
                sentences = abstract.split(". ")
                allocation = next(s for s in sentences if "assigns energy" in s)
                self.assertIn("average power times overlap duration", allocation)
                calculation = next(s for s in sentences if "Using a timing allowance" in s)
                self.assertIn("work with time-stamped start and stop commands", calculation)
                self.assertIn("bounds on repeat scatter or same-condition differences", calculation)
                self.assertIn("each largest bound by its recorded-time value", calculation)
                self.assertIn("holds each record at its reported average" if outcome == "REFUSAL"
                              else "holding each record at its reported average", abstract)
                conclusion = selected.split("## 10. Conclusion\n", 1)[1].split(
                    "## 11. References", 1
                )[0]
                first_sentence = conclusion.strip().split(". ", 1)[0]
                self.assertIn("phase energy—average power times overlap duration", first_sentence)
                self.assertIn("held-average reconstruction, which holds each record", first_sentence)
                if outcome == "REFUSAL":
                    self.assertIn("would recalculate", calculation)
                    self.assertIn("and divide each", calculation)
                    for section in (abstract, conclusion, selected.split(
                        "## 7.", 1
                    )[-1].split("### Further limitations", 1)[0]):
                        self.assertIn("verified failed production-window record", section)
                        self.assertIn("methods/diagnostics fallback", section)
                        self.assertIn("unaffected model-comparison verdicts remain reportable", section)
                        self.assertIn("zero denominator", section)
                else:
                    self.assertIn("JouleWise recalculated", calculation)
                    self.assertIn("and divided each", calculation)

    def test_reader_facing_counts_exclude_fixed_limitation_in_comments(self) -> None:
        draft = self._draft(
            3,
            f"<!-- {SELECTOR.TRANSFER_LIMITATION_SENTENCE} -->",
        )
        visible = SELECTOR._reader_facing_text(draft)
        self.assertNotIn(SELECTOR.TRANSFER_LIMITATION_SENTENCE, visible)
        self.assertEqual(SELECTOR._abstract_word_count(draft), 3)


if __name__ == "__main__":
    unittest.main()
