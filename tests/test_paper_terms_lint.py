from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "paper_terms_lint.py"
REAL_DRAFT = REPO / "docs" / "paper" / "draft-v1.md"
REAL_PLAN = REPO / "docs" / "paper" / "round7" / "retensing-plan.md"
SUCCESSOR_DRAFT = REPO / "docs" / "paper" / "draft-v2-skeleton.md"
FILL_REGISTRY = REPO / "docs" / "paper" / "results-fill-registry.md"


def enclosure_placement_errors(draft: str, registry: str) -> list[str]:
    """Bind the appendix-only row without treating it as a Results fill."""
    errors = []
    rows = [line for line in registry.splitlines() if line.startswith("| PE-01 —")]
    if len(rows) != 1:
        return ["PE-01 row must occur exactly once"]
    cells = [cell.strip() for cell in rows[0].strip("|").split("|")]
    if len(cells) != 7 or cells[1] != "`[FILL:PE-01]`" or cells[4] != "DERIVE":
        errors.append("PE-01 marker and DERIVE rule must occupy their registry columns")
    if "SYNTHETIC_FIGURE_PLACED" not in rows[0] or "TOKEN_MISSING" in rows[0]:
        errors.append("PE-01 must record the synthetic placement")
    body = draft.split("## First-use audit ledger", 1)[0]
    sections = re.split(r"(?m)^### ", body)
    appendix = next((s for s in sections if s.startswith("A.7 Synthetic partial-record enclosure\n")), "")
    if body.count("[FILL:PE-01]") != 1 or appendix.count("[FILL:PE-01]") != 1:
        errors.append("PE-01 must occur once, in Appendix A.7")
    image = "(figures/figA_partial_record_enclosure.svg)"
    if appendix.count(image) != 1 or "Figure A1. SYNTHETIC P1; no hardware observation." not in appendix:
        errors.append("PE-01 appendix figure and synthetic caption are required")
    introduction = body.split("## 1. Introduction", 1)[-1].split("## 2.", 1)[0]
    if "Appendix Figure A1 shows the records, window, and three energy results for this synthetic example." not in introduction:
        errors.append("Introduction must cite Figure A1")
    return errors


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

    def test_enclosure_registry_row_and_appendix_placement(self) -> None:
        draft = SUCCESSOR_DRAFT.read_text(encoding="utf-8")
        registry = FILL_REGISTRY.read_text(encoding="utf-8")
        self.assertEqual(enclosure_placement_errors(draft, registry), [])
        row = next(line for line in registry.splitlines() if line.startswith("| PE-01 —"))
        mutations = (
            (draft, registry.replace(row, "")),
            (draft, registry + "\n" + row),
            (draft, registry.replace(row, row.replace("| DERIVE |", "| MEASURED |"))),
            (draft.replace("[FILL:PE-01]", "[FILL:PE-02]"), registry),
            ("[FILL:PE-01]\n" + draft.replace("[FILL:PE-01]", ""), registry),
            (draft.replace("(figures/figA_partial_record_enclosure.svg)", "(missing.svg)"), registry),
            (draft.replace("Figure A1. SYNTHETIC P1; no hardware observation.", "Figure A1."), registry),
            (draft.replace("Appendix Figure A1 shows", "The appendix shows"), registry),
        )
        for index, (changed_draft, changed_registry) in enumerate(mutations):
            with self.subTest(mutation=index):
                self.assertTrue(enclosure_placement_errors(changed_draft, changed_registry))

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

    def test_fallback_preserves_ratified_paper_k_rulings(self) -> None:
        draft = SUCCESSOR_DRAFT.read_text(encoding="utf-8")
        registry = FILL_REGISTRY.read_text(encoding="utf-8")

        self.assertIn(
            "# JouleWise: Timing Sensitivity of Phase-Energy Assignments on Apple Silicon",
            draft,
        )
        self.assertGreaterEqual(draft.count("[FILL:"), 1)
        self.assertNotIn("[FILL:TR-01]", draft)
        self.assertEqual(
            draft.count(
                "Transfer of the pulse-derived timing allowance to inference was not tested."
            ),
            1,
        )
        for retired in (
            "largest false",
            "same timing error moved together",
            "uniform shared shift cancels",
            "straight line joining those samples",
            "claim-bearing **energy terms**",
            "2.776445",
            "4.808944",
            "95/95",
            "BUILD AFTER CAMPAIGN AND TRANSFER FIDUCIAL",
            "the headline remains conditional on it",
            "the floor packs set A = B",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, draft)

        for required in (
            "registered timing domain—the edge movements fixed before collection",
            "A\nshared sign is one choice applied across all blocks",
            "An A/B/B/A block is four runs in the order A, B, B, A.",
            "The measurand is energy assigned to each phase by\n"
            "**interval-overlap allocation**: each sampling record's energy is divided",
            "Its \\(\\pm10\\)-ms two-edge timing\n"
            "envelope is [8.8, 9.2] J, while allowing each record's energy to sit anywhere\n"
            "inside its own interval gives the nonnegative partial-record enclosure\n"
            "[8, 10] J: the eight records lying wholly inside contribute 8 J, and the two\n"
            "records the window only partly covers contribute between 0 and 1 J each.",
            "Both ratios\nmeasure enlargement under specified perturbation sets; they do not estimate\n"
            "how often or how strongly those errors occur.",
            "For native interval-average records, the reducer integrates constant reported power\n"
            "over the overlap duration; its interpolation-bound term is zero. Timing\n"
            "uncertainty enters through separately recomputed boundary envelopes.",
            "Using the\ncode's fixed three-decimal lookup-table convention, \\(t_{.975,4}=2.776\\)",
            "We apply Holm at nominal family-wise level 0.05 to two\n"
            "model-based tests; error control depends on their distributional and dependence\n"
            "assumptions.",
            "The comparison supports this fixed prompt and makes no prompt-population\n"
            "generality claim.",
            "\\(F+B\\) is only a non-gating planning diagnostic, neither necessary\n"
            "nor sufficient for acceptance",
        ):
            with self.subTest(required=required):
                self.assertIn(required, draft)

        self.assertNotIn("d165_shared_sign_local_corner_replay.v1", registry)
        self.assertIn(
            "The protocol-first title fixed before collection is **JouleWise: Timing\n"
            "Sensitivity of Phase-Energy Assignments on Apple Silicon**.",
            registry,
        )
        self.assertEqual(
            draft.count(
                "registered timing domain—the edge movements fixed before collection"
            ),
            2,
        )
        self.assertGreaterEqual(
            registry.count("d165_shared_sign_local_corner_replay.v2"),
            5,
        )
        self.assertIn("| LIMITATION | WITHDRAWN 2026-09-04", registry)

    def test_historical_headline_matches_registered_json_and_svg(self) -> None:
        from tests.test_select_outcome_branches import SELECTOR
        draft = SUCCESSOR_DRAFT.read_text(encoding="utf-8")
        registry = FILL_REGISTRY.read_text(encoding="utf-8")
        source = REPO / "docs/paper/round7/excursion-decomposition.json"
        figure = REPO / "docs/paper/figures/fig4_edge_excursions.svg"
        payload = json.loads(source.read_text(encoding="utf-8"))
        for path, digest in (
            (source, "21618026dfc677165b2a1acd511ff0d3130bd3837fa344c9ca9fbac95d7e058b"),
            (figure, "6ac9d5c7a84ac1bb8d3c0da036449f77e0e5d2d36564dfc33a1c2812912782cf"),
        ):
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
            self.assertIn(digest, registry)
        rows = payload["per_pulse"]
        self.assertEqual(len(rows), 59)
        self.assertEqual(sum(row["onset_best_fit_lag_ms"] > 0 for row in rows), 59)
        self.assertEqual(sum(row["offset_best_fit_lag_ms"] < 0 for row in rows), 49)
        self.assertEqual(payload["summary"]["onset_best_fit_lag"]["count_positive"], 59)
        self.assertEqual(payload["summary"]["offset_best_fit_lag"]["count_negative"], 49)
        self.assertEqual(draft.count(SELECTOR.HEADLINE), 2)
        self.assertIn("Figure 2. Historical current-method re-derivation, one GPU pulse capture.", draft)
        self.assertIn("onset (switch-on edge) — 59 of 59 are late", figure.read_text())
        self.assertIn("offset (switch-off edge) — 49 of 59 are early", figure.read_text())

    def test_record_support_matches_registered_population_and_statistics(self) -> None:
        source = REPO / "docs/process_traces/2026-08-09-prefill-phase-proof/results.json"
        payload = json.loads(source.read_text())
        summary = next(row for row in payload["stack_summaries"] if row["stack"] == "1.5B")
        self.assertEqual(summary["bundle_count"], 50)
        self.assertEqual(summary["resolvability"],
                         {"not_resolvable_sample_count": 37, "identifiable": 13})
        self.assertEqual(summary["prefill_overlap_sample_count"], {"2": 37, "3": 13})
        rows = [row for row in payload["bundles"] if "1.5B" in row["model"]["name"]]
        self.assertEqual(len(rows), 50)
        self.assertEqual(len({row["bundle"] for row in rows}), 50)
        self.assertEqual(sum(row["power"]["prefill_overlap_sample_count"] == 2 for row in rows), 37)
        stats_path = REPO / "docs/paper/round7/dg071-dg075-statistics.json"
        self.assertEqual(hashlib.sha256(stats_path.read_bytes()).hexdigest(),
                         "9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7")
        stats = json.loads(stats_path.read_text())["statistics"]
        draft = SUCCESSOR_DRAFT.read_text()
        for key, count, median, iqr in (("DG-071", 406, "120.9186", "5.9508"),
                                        ("DG-075", 405, "120.9224", "5.8949")):
            self.assertEqual(stats[key]["sample_count"], count)
            self.assertEqual(stats[key]["median_ms"], median)
            self.assertEqual(stats[key]["iqr_ms"], iqr)
            self.assertIn(median + " ms", draft)
            self.assertIn(iqr + " ms", draft)

    def test_retired_result_rows_remain_and_have_no_draft_slots(self) -> None:
        draft = SUCCESSOR_DRAFT.read_text()
        registry = FILL_REGISTRY.read_text()
        ids = [f"DS-{i:02d}" for i in range(9, 34)] + [
            f"PG-{i:02d}" for i in range(1, 9)] + ["OB-01", "OR-01"]
        for row_id in ids:
            with self.subTest(row=row_id):
                rows = [line for line in registry.splitlines()
                        if line.startswith("| " + row_id + " —")]
                self.assertEqual(len(rows), 1)
                self.assertIn("RETIRED_FALLBACK 2026-09-05", rows[0])
                self.assertNotIn("[FILL:" + row_id + "]", draft)
        self.assertNotIn("OUTCOME-BRANCH", draft)
        self.assertNotIn("A — every required ratio passes", draft)
        self.assertNotIn("outcome A / outcome B", draft)
        self.assertNotIn("| Contrast | Point estimate |", draft)

    def test_synthetic_source_maps_reproduce_printed_arithmetic(self) -> None:
        import itertools
        import math
        import statistics
        fixture = REPO / "tests/fixtures/fcm_r4_real_blocks/measured_pair.json"
        digest = hashlib.sha256(fixture.read_bytes()).hexdigest()
        self.assertEqual(digest, "ba9398bf74829d0dbf00dc19b6bb14c4119efc750e132dfef1daab0fc2808ea4")
        self.assertIn(digest, FILL_REGISTRY.read_text())
        blocks = json.loads(fixture.read_text())["blocks"]
        point, shared_allowance, local_allowance = [], [], []
        for block in blocks:
            delta, zero = block["delta_j"], block["zero_point_contrast_j"]
            onset, offset = block["onset_sweep_j"], block["offset_sweep_j"]
            point.append(delta)
            shared_allowance.append(max(abs(min(onset) + min(offset) - 2*zero),
                                        abs(max(onset) + max(offset) - 2*zero)) + abs(zero-delta))
            local_allowance.append(sum(block["bundle_residual_half_widths_j"])/2)
        def bound(values: list[float]) -> float:
            return max(max(map(abs, values)), abs(statistics.mean(values)) +
                       12.706*statistics.stdev(values)*math.sqrt(1+1/len(values)))
        maximum = max(bound([d+s*q+t*l for d,q,l,t in
                             zip(point,shared_allowance,local_allowance,signs)])
                      for s in (-1,1) for signs in itertools.product((-1,1), repeat=2))
        for actual, printed in ((bound(point), 2.4305766103), (maximum, 8.8304376431),
                                (maximum/bound(point), 3.6330628732)):
            self.assertAlmostEqual(actual, printed, places=9)
        draft = SUCCESSOR_DRAFT.read_text()
        self.assertIn("SYNTHETIC ARITHMETIC", draft)
        self.assertIn("registry\nSYN-01", draft)
        p1 = json.loads((REPO / "docs/paper/figures/figA_partial_record_enclosure.json").read_text())
        self.assertFalse(p1["claim_bearing"])
        self.assertEqual(p1["label"], "SYNTHETIC P1")
        records = p1["inputs"]["records"]
        start, end = p1["inputs"]["window_s"]
        def overlap(a: float, b: float) -> float:
            return sum(row["power_w"]*max(0,min(b,row["end_s"])-max(a,row["start_s"]))
                       for row in records)
        whole = [row for row in records if start <= row["start_s"] and row["end_s"] <= end]
        touched = [row for row in records if min(end,row["end_s"]) > max(start,row["start_s"])]
        lower = sum(row["power_w"]*(row["end_s"]-row["start_s"]) for row in whole)
        upper = sum(row["power_w"]*(row["end_s"]-row["start_s"]) for row in touched)
        for actual, expected in ((overlap(start,end),9), (lower,8), (upper,10),
                                 (overlap(start+.01,end-.01),8.8),
                                 (overlap(start-.01,end+.01),9.2)):
            self.assertAlmostEqual(actual, expected)
        svg = REPO / "docs/paper/figures/figA_partial_record_enclosure.svg"
        self.assertEqual(hashlib.sha256(svg.read_bytes()).hexdigest(), p1["figure"]["sha256"])

    def test_references_close_existing_citations_and_availability_is_restricted(self) -> None:
        draft = SUCCESSOR_DRAFT.read_text()
        related = draft.split("## 8. Related work\n")[1].split("## 9.")[0]
        refs = draft.split("## 11. References\n")[1].split("## Appendix A.")[0]
        numbers = [int(n) for n in re.findall(r"^(\d+)\. ", refs, re.MULTILINE)]
        self.assertEqual(numbers, list(range(1, 22)))
        self.assertEqual(set(map(int, re.findall(r"\[(\d+)\]", related))), set(numbers))
        self.assertIn("https://hotcarbon.org/assets/2026/paper-17.pdf", refs)
        self.assertIn("https://hotcarbon.org/assets/2026/paper-46.pdf", refs)
        self.assertNotIn("[REF NEEDED]", refs)
        availability = draft.split("## 9. Evidence and code availability\n")[1].split("## 10.")[0]
        for phrase in ("No public submission", "not been released as a complete public reproduction",
                       "cannot\nreplace unavailable primary bytes", "open_paper_input(ref)",
                       "Correct points with coherently wrong widths cannot count as"):
            self.assertIn(phrase, availability)


if __name__ == "__main__":
    unittest.main()
