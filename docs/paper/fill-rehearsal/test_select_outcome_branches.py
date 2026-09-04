from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("select_outcome_branches.py")
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

    def test_reader_facing_counts_exclude_html_comments(self) -> None:
        markers = " ".join(
            (
                SELECTOR.TRANSFER_MARKER,
                SELECTOR.FAILED_COMPONENTS_MARKER,
                SELECTOR.DECODE_VERDICT_MARKER,
                SELECTOR.PREFILL_VERDICT_MARKER,
                SELECTOR.REFUSAL_REASON_MARKER,
            )
        )
        draft = self._draft(3, f"<!-- {markers} -->")
        visible = SELECTOR._reader_facing_text(draft)
        for marker in (
            SELECTOR.TRANSFER_MARKER,
            SELECTOR.FAILED_COMPONENTS_MARKER,
            SELECTOR.DECODE_VERDICT_MARKER,
            SELECTOR.PREFILL_VERDICT_MARKER,
            SELECTOR.REFUSAL_REASON_MARKER,
        ):
            self.assertNotIn(marker, visible)
        self.assertEqual(SELECTOR._abstract_word_count(draft), 3)

        skeleton = SCRIPT.parents[1] / "draft-v2-skeleton.md"
        source_text = skeleton.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.md"
            output = root / "selected.md"
            source.write_text(f"<!-- {markers} -->\n{source_text}", encoding="utf-8")
            result = subprocess.run(
                (
                    sys.executable,
                    str(SCRIPT),
                    "--source",
                    str(source),
                    "--output",
                    str(output),
                    "--outcome",
                    "A",
                ),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("selected A:", result.stdout)


if __name__ == "__main__":
    unittest.main()
