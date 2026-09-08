"""Desk-only migration checks; no suppliers, external corpus, or paper writes."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from tests import test_paper_first_use_ledger as first_use

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs/paper"
GUIDANCE = (
    PAPER / "round7/fill-checklist.md",
    PAPER / "fill-rehearsal/branch-selection.md",
)
SELECTOR = PAPER / "fill-rehearsal/select_outcome_branches.py"
spec = importlib.util.spec_from_file_location("migration_selector", SELECTOR)
selector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selector)


def guidance_failures(text: str) -> list[str]:
    """Reject known obsolete imperatives on the two active operating surfaces.

    Deliberately not a general English policy classifier. Negative controls below
    model the concrete regression shapes; parked quotations are not inputs.
    """
    normalized = " ".join(text.split())
    hazards = {
        "retired selector": r"--outcome\s+(?:A|B|REFUSAL)\b",
        "retired choices": r"accepts exactly `?A`?,? (?:`?B`?|or `?REFUSAL`?)",
        "retired selection instruction": r"(?:select|choose) (?:one of )?`?(?:A|B|REFUSAL)`?\b",
        "retired fill instruction": r"(?:fill|populate|render) (?:the )?(?:retired|RETIRED_FALLBACK) rows",
        "frozen edit instruction": r"(?:edit|overwrite) (?:the )?frozen draft in place",
        "ledger bypass": r"(?:skip|bypass|omit) (?:the )?(?:replacement |fill )?ledger",
        "observed prospective counts": r"(?:treat|report|use) prospective counts as (?:observed|collected)",
    }
    return [name for name, pattern in hazards.items()
            if re.search(pattern, normalized, re.IGNORECASE)]


def assembled_gloss_failures(article: str, protocol: str, ledger: str) -> list[str]:
    # Pass an explicit assembled body: never substitute an old paragraph or
    # concatenate parked replacements in lieu of checking the actual article.
    rows, body = first_use._parse_ledger(article + "\n" + protocol + "\n" + ledger)
    return first_use._gloss_failures(rows, body)


class PaperSuccessorMigrationTests(unittest.TestCase):
    def test_active_guidance_rejects_known_unsafe_instructions(self):
        for path in GUIDANCE:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(guidance_failures(text), [])
                for required in ("METHODS_DIAGNOSTIC", "S1/S6", "open_paper_input",
                                 "replacement ledger", "250", "read-only"):
                    self.assertIn(required, text)
        guide = GUIDANCE[1].read_text(encoding="utf-8")
        choices = re.findall(r"--outcome\s+(\w+)", guide)
        self.assertTrue(choices)
        self.assertEqual(set(choices), set(selector.BRANCHES))

    def test_unsafe_instruction_mutations_fail_with_clean_control(self):
        clean = GUIDANCE[0].read_text(encoding="utf-8")
        self.assertEqual(guidance_failures(clean), [])
        mutations = (
            "Run --outcome A", "Run --outcome B", "Run --outcome REFUSAL",
            "--outcome accepts exactly A, B, or REFUSAL.",
            "Select one of A, B, or REFUSAL today.",
            "Fill retired rows.", "Populate RETIRED_FALLBACK rows.",
            "Edit the frozen draft in place.", "Bypass the replacement ledger.",
            "Treat prospective counts as observed.",
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.assertTrue(guidance_failures(clean + "\n" + mutation))

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

    def test_assembled_first_uses_use_read_only_ledger(self):
        article = (PAPER / "draft-v2-skeleton.md").read_text(encoding="utf-8")
        protocol = (PAPER / "protocol/prospective-comparison-protocol.md").read_text(encoding="utf-8")
        ledger = (PAPER / "protocol/first-use-audit-ledger.md").read_text(encoding="utf-8")
        self.assertEqual(assembled_gloss_failures(article, protocol, ledger), [])

    def test_synthetic_relocation_fails_even_when_old_home_is_correct(self):
        term = "powermetrics"
        construction = "macOS powermetrics is the power sampler used here."
        row = first_use.LedgerRow(term, "Old home", "glossed-at-first-use", construction)

        def failures(text):
            # Other requirements are intentionally absent in this small fixture;
            # isolate the selected real construction without weakening its rule.
            return [failure for failure in first_use._gloss_failures([row], text.splitlines())
                    if failure.startswith(term + ":")]

        old_home = "## Old home\n\n" + construction
        self.assertEqual(failures(old_home), [])
        relocated = "## Abstract\n\nWe use powermetrics.\n\n" + old_home
        self.assertTrue(failures(relocated))
        # Merely checking the old home would pass and miss this defect.
        self.assertEqual(failures(relocated.split("## Old home", 1)[1]), [])
        # Even an editorial approval of a parked sheet supplies no construction.
        approved = "<!-- Parked sheet mechanically approved. -->\n" + relocated
        self.assertTrue(failures(approved))
        corrected = "## Abstract\n\n" + construction + "\n\n" + old_home
        self.assertEqual(failures(corrected), [])

    def test_inventory_covers_migration_and_first_use_gates(self):
        inventory = (PAPER / "round7/successor-migration-inventory.md").read_text(encoding="utf-8")
        for target in ("S1", "S6", "NEEDS_RULING", "TR-01", "DS-34", "OB-01/OR-01",
                       "prompt 0", "common", "Operands", "Units", "Signs", "Sampling units",
                       "Thresholds", "Figure encodings", "Synthetic labels", "input/output",
                       "replacement", "historical replay", "live fill adjudication",
                       "built-terms-lexicon.md", "first-use-audit-ledger.md"):
            with self.subTest(target=target):
                self.assertIn(target.casefold(), inventory.casefold())
        self.assertIn("does not constitute empirical fill", inventory)


if __name__ == "__main__":
    unittest.main()
