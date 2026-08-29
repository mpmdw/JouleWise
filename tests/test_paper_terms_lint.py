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
        if result.returncode != 1:
            raise AssertionError(f"expected real-plan findings: {result.stderr}\n{result.stdout}")
        cls.payload = json.loads(result.stdout)

    def test_audit_terms_are_reported_at_early_insertion_lines(self) -> None:
        findings = self.payload["findings"]
        pairs = {(item["line"], item["term"]) for item in findings}

        # Round 1's whole-window wording was replaced by floor-window wording;
        # at least the wording actually present must remain mechanically caught.
        self.assertTrue(
            any(
                line in {11, 31} and term in {"whole-window gate", "floor window"}
                for line, term in pairs
            )
        )
        self.assertTrue(any(line in {11, 31} and term == "claim gate" for line, term in pairs))
        self.assertIn((11, "claim-anchored limit"), pairs)

        for line in (11, 31, 243):
            self.assertIn((line, "1.5B"), pairs)
            self.assertIn((line, "7B"), pairs)

    def test_term_a_and_b_are_findings_if_a_variant_uses_them(self) -> None:
        plan_text = REAL_PLAN.read_text(encoding="utf-8")
        variant_lines = [
            line
            for line in plan_text.splitlines()
            if line.startswith(("**A —", "**B —", "**C —", "**D —", "**A = B —"))
        ]
        finding_terms = {item["term"] for item in self.payload["findings"]}
        for term in ("TERM A", "TERM B"):
            if any(term in line for line in variant_lines):
                self.assertIn(term, finding_terms)

    def test_real_lexicon_pins_first_build_lines(self) -> None:
        result = run_cli("lexicon", "--draft", str(REAL_DRAFT), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        terms = {item["term"]: item["first_line"] for item in json.loads(result.stdout)["terms"]}

        # Pinned with:
        # rg -n -i -m 1 'resolution bound|detection floor' docs/paper/draft-v1.md
        self.assertEqual(terms["resolution bound"], 11)
        self.assertEqual(terms["detection floor"], 11)


if __name__ == "__main__":
    unittest.main()
