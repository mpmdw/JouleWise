from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "paper_terms_lint.py"
REAL_DRAFT = REPO / "docs" / "paper" / "draft-v1.md"
REAL_PLAN = REPO / "docs" / "paper" / "round7" / "retensing-plan.md"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class FixtureLintTests(unittest.TestCase):
    def test_later_build_gloss_absence_and_placeholder(self) -> None:
        draft_lines = [f"ordinary line {number}" for number in range(1, 61)]
        draft_lines[49] = "The resolution bound is introduced here."
        draft = "\n".join(draft_lines) + "\n"
        plan = """\
### H01 — fixture — draft line 10 — FIXED
**A — early:** The resolution bound controls this result.

### H02 — fixture — draft line 60 — FIXED
**A — late:** The resolution bound controls this result.

### H03 — fixture — draft line 10 — FIXED
**A — glossed:** The resolution bound (plain measurement limit) controls this result.

### H04 — fixture — draft line 10 — FIXED
**A — absent:** The whole-window gate controls this result.

### H05 — fixture — draft line 10 — FIXED
**A — token:** The [whole-window gate] is filled later.

### H06 — fixture — draft line 10 — FIXED
**A — dash gloss:** The whole-window gate — plain measurement stop — controls this result.

### H07 — fixture — draft line 10 — FIXED
**A — plural:** The resolution bounds control this result.

### H08 — fixture — draft line 10 — FIXED
**A — hyphen:** The resolution-bound controls this result.
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft_path = root / "draft.md"
            plan_path = root / "plan.md"
            draft_path.write_text(draft, encoding="utf-8")
            plan_path.write_text(plan, encoding="utf-8")
            result = run_cli(
                "lint",
                "--draft",
                str(draft_path),
                "--plan",
                str(plan_path),
                "--verbose",
                "--json",
            )

        self.assertEqual(result.returncode, 1, result.stderr)
        payload = json.loads(result.stdout)
        findings = payload["findings"]
        self.assertEqual(
            {(item["block"], item["term"], item["first_line"]) for item in findings},
            {
                ("H01", "resolution bound", 50),
                ("H04", "whole-window gate", None),
                ("H07", "resolution bound", 50),
                ("H08", "resolution bound", 50),
            },
        )
        self.assertNotIn("H02", {item["block"] for item in findings})
        self.assertNotIn("H05", {item["block"] for item in findings})
        glossed = {
            (item["block"], item["term"], item["status"])
            for item in payload["glossed"]
        }
        self.assertIn(("H03", "resolution bound", "glossed"), glossed)
        self.assertIn(("H06", "whole-window gate", "glossed"), glossed)


class RealDocumentRegressionTests(unittest.TestCase):
    """Standing contract: the retensing plan stays lint-clean.

    Historically this class asserted the HELD plan's known findings; the
    2026-08-31 lexicon-constrained rewrite (magistrate ruling R-1/R-2)
    brought the plan to zero findings, so the standing regression inverts:
    any reintroduced early-insertion vocabulary must turn this red.
    """

    @classmethod
    def setUpClass(cls) -> None:
        result = run_cli(
            "lint",
            "--draft",
            str(REAL_DRAFT),
            "--plan",
            str(REAL_PLAN),
            "--json",
        )
        if result.returncode != 0:
            raise AssertionError(
                f"retensing plan must stay lint-clean: {result.stderr}\n{result.stdout}"
            )
        cls.payload = json.loads(result.stdout)

    def test_plan_is_lint_clean(self) -> None:
        self.assertEqual(self.payload["finding_count"], 0)
        self.assertGreaterEqual(self.payload["sentence_count"], 80)

    def test_reintroduced_early_vocabulary_is_caught(self) -> None:
        # The gate itself must still catch the historical failure class: a
        # variant sentence using unbuilt registry vocabulary at the Abstract
        # insertion line goes red.
        plan_text = REAL_PLAN.read_text(encoding="utf-8")
        target = "**A = B — admitted evidence:** For each group"
        self.assertIn(target, plan_text)
        poisoned = plan_text.replace(
            target,
            "**A = B — admitted evidence:** TERM A exceeds the "
            "whole-window gate; for each group",
            1,
        )
        with tempfile.TemporaryDirectory() as tmp:
            poisoned_path = Path(tmp) / "poisoned-plan.md"
            poisoned_path.write_text(poisoned, encoding="utf-8")
            result = run_cli(
                "lint",
                "--draft",
                str(REAL_DRAFT),
                "--plan",
                str(poisoned_path),
                "--json",
            )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertGreater(payload["finding_count"], 0)

if __name__ == "__main__":
    unittest.main()
