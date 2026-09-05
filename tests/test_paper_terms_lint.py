from __future__ import annotations

import hashlib
import json
import os
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
PROTOCOL = REPO / "docs/paper/protocol/prospective-comparison-protocol.md"
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
    appendix = next((s for s in sections if s.startswith("A.6 Synthetic partial-record enclosure\n")), "")
    if body.count("[FILL:PE-01]") != 1 or appendix.count("[FILL:PE-01]") != 1:
        errors.append("PE-01 must occur once, in Appendix A.6")
    image = "(figures/figA_partial_record_enclosure.svg)"
    if appendix.count(image) != 1 or "Figure A1. Synthetic; no hardware observation." not in appendix:
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
            (draft.replace("Figure A1. Synthetic; no hardware observation.", "Figure A1."), registry),
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
        combined = draft + "\n" + PROTOCOL.read_text(encoding="utf-8")
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
                self.assertIn(required, combined)

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
        for headline in (SELECTOR.ABSTRACT_HEADLINE, SELECTOR.CONCLUSION_HEADLINE):
            self.assertEqual(" ".join(draft.split()).count(headline), 1)
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

    def test_both_record_support_arms_and_new_registry_rows_match_primary(self) -> None:
        from collections import Counter

        locator = "docs/process_traces/2026-08-09-prefill-phase-proof/results.json"
        primary = Path(os.environ.get("R7F_CORPUS_ROOT", REPO)) / locator
        raw = primary.read_bytes()
        self.assertEqual(raw, (REPO / locator).read_bytes())
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(digest, "e93c1d9c9ccff764cb6c64379cc3551c710e63b38b5314569d89662d2b88d8b1")
        payload = json.loads(raw)
        expected = {
            "1.5B": ({"2": 37, "3": 13},
                     {"not_resolvable_sample_count": 37, "identifiable": 13},
                     {"runs_window_a10_20260725": 10, "runs_window_c_20260726": 40}),
            "7B": ({"3": 33, "4": 17}, {"identifiable": 50},
                   {"runs_window_7bfloor_20260729": 50}),
        }
        self.assertEqual({s["stack"] for s in payload["stack_summaries"]}, set(expected))
        for stack, (overlaps, outcomes, roots) in expected.items():
            with self.subTest(stack=stack):
                rows = [r for r in payload["bundles"] if r["stack"] == stack]
                summary = next(s for s in payload["stack_summaries"] if s["stack"] == stack)
                self.assertEqual(len(rows), 50)
                self.assertEqual(len({(r["corpus_root"], r["bundle"]) for r in rows}), 50)
                self.assertEqual(summary["bundle_count"], len(rows))
                self.assertEqual(Counter(str(r["power"]["prefill_overlap_sample_count"]) for r in rows), overlaps)
                self.assertEqual(summary["prefill_overlap_sample_count"], overlaps)
                self.assertEqual(Counter(r["resolvability"]["rederived"] for r in rows), outcomes)
                self.assertEqual(summary["resolvability"], outcomes)
                self.assertEqual(Counter(Path(r["corpus_root"]).name for r in rows), roots)
                self.assertEqual(Counter(r["model"]["name"] for r in rows),
                                 {f"Qwen2.5-{stack}-Instruct-4bit": 50})
        registry = FILL_REGISTRY.read_text()
        for number, value in ((135, "50"), (136, "50"), (137, "33"), (138, "17"),
                              (139, "Qwen2.5-7B-Instruct-4bit")):
            rows = [r for r in registry.splitlines() if r.startswith(f"| DG-{number} —")]
            self.assertEqual(len(rows), 1)
            cells = [c.strip() for c in rows[0].split("|")]
            self.assertEqual(cells[2], f"`{value}`")
            self.assertIn(locator, cells[3])
            self.assertIn(digest, cells[3])
            self.assertEqual(cells[5], "EXTRACT")
            self.assertIn("NON_CLAIM_BEARING", cells[6])
        draft = " ".join(SUCCESSOR_DRAFT.read_text().split())
        for phrase in ("all 50 prompt-processing phases were identifiable",
                       "33 overlapped three records and 17 overlapped four",
                       "does not isolate a causal effect of model size"):
            self.assertIn(phrase, draft)

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

    def test_round_one_derivations_and_suppliers_are_complete(self) -> None:
        import importlib.util
        import math
        import statistics
        from joulewise.analysis_engine.distributions import two_sided_student_t_p_value
        path = REPO / "docs/paper/figures/reproduce_worked_examples.py"
        spec = importlib.util.spec_from_file_location("paper_worked_examples", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sidecar = REPO / "docs/paper/figures/worked-examples.json"
        payload = json.loads(sidecar.read_text())
        self.assertEqual(json.loads(json.dumps(module.synthetic())), payload["synthetic"])
        registry = FILL_REGISTRY.read_text()
        self.assertIn(hashlib.sha256(sidecar.read_bytes()).hexdigest(), registry)
        self.assertIn(hashlib.sha256(path.read_bytes()).hexdigest(), registry)
        for key in [f"SYN-{i:02d}" for i in range(2, 9)] + [f"DG-{i}" for i in range(129, 135)]:
            rows = [r for r in registry.splitlines() if r.startswith("| " + key + " —")]
            self.assertEqual(len(rows), 1, key)
            self.assertEqual(rows[0].split("|")[5].strip(), "DERIVE", key)
        sy = payload["synthetic"]
        self.assertEqual(sy["composition_absolute"]["corner_widened_unguarded_floor_j"], 1.6656)
        self.assertEqual(sy["composition_comparative"]["corner_widened_unguarded_floor_j"], 1.7656)
        self.assertAlmostEqual(max(sy[k]["corner_widened_guarded_floor_j"] + .4 for k in
                                  ("composition_absolute", "composition_comparative")), 3.0484)
        self.assertEqual(max(sy["cases"], key=lambda r: r["bound"])["signs"], [1, -1, 1])
        for block in sy["blocks"]:
            self.assertEqual(math.fsum(.5*v for v in block["member_integrals"]),
                             block["envelope_integral_sum"])
        deltas = [5.0,7.6,5.5,4.2,4.7,6.8,5.5,3.6,3.9,3.2]
        t = statistics.mean(deltas)/(statistics.stdev(deltas)/math.sqrt(10))
        self.assertAlmostEqual(two_sided_student_t_p_value(t, 9), 1.28854294284577e-6, places=18)
        c = 1.5/2.262
        geometry = [10-c]*5 + [10+c]*5
        se = statistics.stdev(geometry)/math.sqrt(10)
        self.assertAlmostEqual(2.262*se, .5)
        self.assertAlmostEqual(10/se, 45.24)
        self.assertLess(two_sided_student_t_p_value(10/se, 9), .025)
        h = payload["historical"]
        self.assertEqual(len(h["native_constraints"]), 1665)
        self.assertTrue(all(r["native_end_label_s"].is_integer() for r in h["native_constraints"]))
        self.assertEqual(h["native_constraints"][0]["q_ns"], 0)
        self.assertEqual(h["native_constraints"][1]["q_ns"], 118530666)
        for geom, count in zip(h["geometry"], (2, 3)):
            from decimal import Decimal
            phase = Decimal(geom["start"]), Decimal(geom["end"])
            overlaps = [max(Decimal(0), min(phase[1], Decimal(r["end"])) -
                            max(phase[0], Decimal(r["start"]))) for r in geom["records"]]
            self.assertEqual(overlaps, [Decimal(r["overlap"]) for r in geom["records"]])
            self.assertEqual(sum(v > 0 for v in overlaps), count)
            self.assertEqual(overlaps[0], 0)
            self.assertEqual(overlaps[-1], 0)
        draft = SUCCESSOR_DRAFT.read_text()
        for row in h["local_records"]:
            printed = (f"| {row['index']} | {row['native_end_label']:.0f} | "
                       f"{row['start_s']-1784757381:.9f} | {row['end_s']-1784757381:.9f} | "
                       f"{row['gpu_w']:.8f} | {row['predicted_w']:.8f} | {row['loss']:.6f} |")
            self.assertIn(printed, draft)

    def test_prospective_sections_and_editorial_ledger_are_outside_article(self) -> None:
        draft, protocol = SUCCESSOR_DRAFT.read_text(), PROTOCOL.read_text()
        self.assertIn("Status: PROSPECTIVE / UNPERFORMED.", protocol)
        self.assertEqual(draft.count("(protocol/prospective-comparison-protocol.md)"), 1)
        self.assertNotIn("## First-use audit ledger", draft)
        for moved in ("Two directional comparisons—", "### Measured admission rules",
                      "Under D-173,", "The registered minimum basis is forty",
                      "revision\n`3b1b1768", "The prospective design"):
            self.assertIn(moved, protocol)
            self.assertNotIn(moved, draft)
        for cure in ("constant clock rate between stamps remains an unverified assumption",
                     "without assuming independence", "Linear growth reduces a large discrepancy",
                     "three is a chosen cutoff, not proof of adequate", "unrounded standard deviation"):
            self.assertIn(cure, draft)
        self.assertNotIn("the adjusted test passes, so the example supports", protocol)
        self.assertIn("pass the sign check; Holm must pass", protocol)
        self.assertIn("five block differences equal 10−c and five equal 10+c", protocol)
        figure = (REPO / "docs/paper/figures/fig1_boundary_attribution.svg").read_text()
        self.assertIn("0.010 s × 30 W", figure)
        self.assertNotIn("wrong phase", figure)
        gate = (REPO / "docs/paper/figures/fig3_decision_gates.svg").read_text()
        self.assertIn("Holm pass?", gate)
        self.assertIn("no authorized comparison result", gate)

    def test_references_close_existing_citations_and_availability_is_restricted(self) -> None:
        draft = SUCCESSOR_DRAFT.read_text()
        related = draft.split("## 6. Related work\n")[1].split("## 7.")[0]
        refs = draft.split("## 9. References\n")[1].split("## Appendix A.")[0]
        numbers = [int(n) for n in re.findall(r"^(\d+)\. ", refs, re.MULTILINE)]
        self.assertEqual(numbers, list(range(1, 22)))
        self.assertEqual(set(map(int, re.findall(r"\[(\d+)\]", related))), set(numbers))
        self.assertIn("https://hotcarbon.org/assets/2026/paper-17.pdf", refs)
        self.assertIn("https://hotcarbon.org/assets/2026/paper-46.pdf", refs)
        self.assertNotIn("[REF NEEDED]", refs)
        availability = draft.split("## 7. Evidence and code availability\n")[1].split("## 8.")[0]
        for phrase in ("No public submission", "not been released as a complete public reproduction",
                       "cannot\nreplace unavailable primary bytes"):
            self.assertIn(phrase, availability)
        protocol = PROTOCOL.read_text()
        for phrase in ("open_paper_input(ref)",
                       "Correct points with coherently wrong widths cannot count as"):
            self.assertIn(phrase, protocol)
            self.assertNotIn(phrase, availability)
        self.assertIn("ten named members", availability)
        self.assertIn("forty of `runs_window_c_20260726/`", availability)

    def test_post_cut_structure_figures_and_protocol_subjects(self) -> None:
        draft, protocol = SUCCESSOR_DRAFT.read_text(), PROTOCOL.read_text()
        self.assertEqual(re.findall(r"^## (\d+)\.", draft, re.MULTILINE),
                         [str(n) for n in range(1, 10)])
        self.assertEqual(re.findall(r"^### A\.(\d+) ", draft, re.MULTILINE),
                         [str(n) for n in range(1, 8)])
        first_figures = list(dict.fromkeys(re.findall(r"Figure (A?\d+)\b", draft)))
        self.assertEqual([n for n in first_figures if n.isdigit()], ["1", "2", "3"])
        self.assertEqual([n for n in first_figures if n.startswith("A")],
                         [f"A{n}" for n in range(1, 7)])
        for label, locator in re.findall(r"!\[Figure (A?\d+)[^\]]*\]\(([^)]+)\)", draft):
            self.assertRegex(draft, rf"(?m)^\*?Figure {label}\. ")
            svg = (SUCCESSOR_DRAFT.parent / locator).read_text()
            # The two separately issued figures have unnumbered artwork;
            # whenever a number is embedded, it must match the caption.
            embedded = re.findall(r"Figure (A?\d+)\.", svg)
            if label not in ("2", "A1"):
                self.assertTrue(embedded, locator)
            self.assertTrue(all(number == label for number in embedded), locator)
        self.assertIn("Figure P1.", protocol)
        self.assertNotRegex(protocol, r"Figure [1-9]|^### A\.")
        for phrase in ("P.6 describes the separate", "gap described in P.5 above",
                       "measured admission predicates in P.4", "permits no interpretation of the effect"):
            self.assertIn(phrase, protocol)
        self.assertNotIn("the effect may be absent", protocol)
        self.assertNotIn("**close-out artifact**", draft)
        self.assertNotIn("### Adding publication safeguards", draft)
        self.assertIn("### Adding publication safeguards", protocol)
        self.assertNotIn("synthetic P1", draft)
        self.assertNotIn("SYNTHETIC P1", draft)
        self.assertNotIn("**Gross energy**", draft)
        self.assertNotIn("**Idle-subtracted energy**", draft)
        self.assertNotIn("**same-cell floor**", draft)

    def test_replay_pin_supplies_repository_only_synthetic_producer(self) -> None:
        draft = SUCCESSOR_DRAFT.read_text()
        pin = "2d96783857741f03ad9d634328efaf8bc6d676bc"
        self.assertIn(f"`{pin}`", draft)
        self.assertIn("Any later explicitly issued replay pin supersedes it", draft)
        for path in ("docs/paper/figures/reproduce_worked_examples.py",
                     "docs/paper/figures/build_mechanism_figures.py",
                     "docs/paper/figures/worked-examples.json"):
            result = subprocess.run(["git", "cat-file", "-e", f"{pin}:{path}"],
                                    cwd=REPO, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        command = re.search(r"(?m)^python3 -B -c '(import json, runpy; .+)'$", draft)
        self.assertIsNotNone(command)
        result = subprocess.run([sys.executable, "-B", "-c", command.group(1)],
                                cwd=REPO, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        parent = json.loads((REPO / "docs/paper/figures/worked-examples.json").read_text())
        self.assertEqual(json.loads(result.stdout), parent["synthetic"])

    def test_pulse_rectangle_display_encloses_unrounded_limits(self) -> None:
        from decimal import Decimal
        data = json.loads((REPO / "docs/paper/figures/worked-examples.json").read_text())
        svg = (REPO / "docs/paper/figures/figA6_pulse_fit.svg").read_text()
        for edge, label in (("onset", "on"), ("offset", "off")):
            match = re.search(label + r" ∈ \[([−\d.]+), ([−\d.]+)\] ms", svg)
            self.assertIsNotNone(match)
            lower, upper = (Decimal(s.replace("−", "-")) for s in match.groups())
            fit = data["historical"]["fit"]
            self.assertLessEqual(lower, Decimal(str(fit[f"{edge}_residual_lower_s"])) * 1000)
            self.assertGreaterEqual(upper, Decimal(str(fit[f"{edge}_residual_upper_s"])) * 1000)


if __name__ == "__main__":
    unittest.main()
