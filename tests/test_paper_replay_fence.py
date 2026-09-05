"""Tests for the Section 4 replay fence (``scripts/check_paper_replay_fence.py``).

Two layers, because the fence's two halves have different reach.

The extraction half needs no measurement artifacts, so it runs everywhere,
including in hosted CI: it proves that the draft still states each fenced value
exactly once at the anchor the fence looks for, and that the arithmetic the
draft performs on its own printed numbers is right.  An edit that moves, splits,
or renumbers one of the two worked examples fails here.

The replay half needs the capture's primary bytes -- ``raw/powermetrics.plist``
is about 88 MB and is not in the repository -- so it runs only on a machine that
holds the retained corpus and skips elsewhere.  A skip is never a pass: the
script itself exits 3 for an absent corpus, and this module asserts that
distinction rather than treating absence as agreement.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
FENCE_PATH = ROOT / "scripts" / "check_paper_replay_fence.py"
DRAFT = ROOT / "docs" / "paper" / "draft-v2-skeleton.md"

FENCE_SPEC = importlib.util.spec_from_file_location("check_paper_replay_fence", FENCE_PATH)
assert FENCE_SPEC is not None and FENCE_SPEC.loader is not None
FENCE = importlib.util.module_from_spec(FENCE_SPEC)
FENCE_SPEC.loader.exec_module(FENCE)

CORPUS_ROOT = Path(os.environ.get("R7F_CORPUS_ROOT", ROOT))
CORPUS = CORPUS_ROOT / FENCE.SOURCE_DIRECTORY
CORPUS_PRESENT = (CORPUS / "instrument_evidence.json").is_file() and (
    CORPUS / "raw" / "powermetrics.plist"
).is_file()


class DraftLiteralExtractionTests(unittest.TestCase):
    """The draft still states every fenced value where the fence looks."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = DRAFT.read_text(encoding="utf-8")
        cls.literals = FENCE.extract_draft_literals(cls.text)

    def test_every_fenced_value_is_present(self) -> None:
        expected = {
            "pulse_count",
            "cell_count",
            "anchor_bound_s",
            "b_fiducial_s",
            "subtraction_minuend",
            "subtraction_subtrahend",
            "subtraction_result",
            "pulse_ordinal_word",
            "planned_on_offset_s",
            "planned_off_offset_s",
            "command_on_epoch_s",
            "command_off_epoch_s",
            "onset_residual_lower_s",
            "onset_residual_upper_s",
            "offset_residual_lower_s",
            "offset_residual_upper_s",
            "best_fit_delta_on_s",
            "best_fit_delta_off_s",
            "retained_residual_bound_s",
            "clock_stamps",
            "wall_resolution_s",
            "monotonic_resolution_s",
        }
        self.assertEqual(set(self.literals), expected)

    def test_historical_heading_and_duplicate_fail_closed(self) -> None:
        self.assertIn("*Worked historical-capture arithmetic.*", self.text)
        legacy = self.text.replace("*Worked historical-capture arithmetic.*",
                                   "**Worked current-capture arithmetic.**")
        self.assertEqual(FENCE.extract_draft_literals(legacy), self.literals)
        for suffix in ("*Worked historical-capture arithmetic.* duplicate",
                       "**Worked current-capture arithmetic.** duplicate"):
            with self.subTest(suffix=suffix), self.assertRaises(FENCE.FenceError):
                FENCE.extract_draft_literals(self.text + "\n" + suffix)

    def test_five_stamp_rows_in_solver_order(self) -> None:
        sys.path.insert(0, str(ROOT))
        from joulewise.uncertainty_evidence import STAMP_ORDER

        printed = tuple(row["stamp"] for row in self.literals["clock_stamps"])
        self.assertEqual(printed, STAMP_ORDER)

    def test_draft_internal_identities_hold(self) -> None:
        self.assertEqual(FENCE.check_draft_internal_identities(self.literals), [])

    def test_extraction_fails_closed_when_an_anchor_is_lost(self) -> None:
        mutated = self.text.replace("a final capture bound of", "a final capture limit of", 1)
        self.assertNotEqual(mutated, self.text)
        with self.assertRaises(FENCE.FenceError):
            FENCE.extract_draft_literals(mutated)

    def test_extraction_fails_closed_when_a_stamp_row_is_dropped(self) -> None:
        row = "| `post_parse` |"
        index = self.text.find(row)
        self.assertGreater(index, 0)
        end = self.text.find("\n", index)
        mutated = self.text[:index] + self.text[end + 1 :]
        with self.assertRaises(FENCE.FenceError):
            FENCE.extract_draft_literals(mutated)

    def test_internal_check_catches_a_perturbed_difference(self) -> None:
        literals = dict(self.literals)
        literals["subtraction_result"] = "0.0289329345611147593"
        self.assertTrue(FENCE.check_draft_internal_identities(literals))


class FenceInvocationTests(unittest.TestCase):
    """The committed script's own exit contract."""

    def test_literals_only_mode_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(FENCE_PATH), "--literals-only"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("INTERNAL MISMATCHES 0", completed.stdout)

    def test_absent_corpus_exits_three_not_zero(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(FENCE_PATH),
                "--corpus-root",
                str(ROOT / "tests" / "fixtures" / "no-such-corpus"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 3, completed.stdout + completed.stderr)
        self.assertIn("PRIMARY ARTIFACTS UNAVAILABLE", completed.stdout)


@unittest.skipUnless(
    CORPUS_PRESENT,
    "retained capture 20260722T145535-e941c821 is not on this machine; "
    "run scripts/check_paper_replay_fence.py where the corpus lives",
)
class ReplayAgainstPrimaryArtifactsTests(unittest.TestCase):
    """Re-derive both Section 4 substitutions and match the draft's literals."""

    def test_every_fenced_value_replays(self) -> None:
        literals = FENCE.extract_draft_literals(DRAFT.read_text(encoding="utf-8"))
        derived = FENCE.derive_from_artifacts(ROOT, CORPUS_ROOT)
        rows = FENCE.compare(literals, derived)
        mismatches = [row for row in rows if not row["match"]]
        self.assertEqual(mismatches, [], f"{len(mismatches)} of {len(rows)} values disagree")


if __name__ == "__main__":
    unittest.main()
