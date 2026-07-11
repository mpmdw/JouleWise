"""Offline smoke tests for the RPT-001 report vertical slice.

These run against the committed rpt001-v1 artifacts and report source; they
do NOT reread the real bundle corpus (which is gitignored). Real-bundle
ingestion is the lead-run local gate (spec §0.4/§9.4).
"""

from __future__ import annotations

import csv
import importlib.util
import json
import shutil
import statistics
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "analysis" / "rpt001-v1"
LEGACY_LABEL = "legacy L1 (manual review; pre-2M)"
RUNS = Path("/Users/edr/code/JouleWise/runs")


def load_script(name: str, filename: str):
    path = REPO / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


make_figures = load_script("rpt001_make_figures", "make_figures.py")
build_capstone = load_script("rpt001_build_capstone", "build_capstone.py")


class TestRpt001Artifacts(unittest.TestCase):
    def test_1p5b_identifier_is_pinned(self):
        expected = "LEGACY-M3MAX-QWEN25-1P5B-MLX"
        self.assertEqual(make_figures.STACK_IDS["example-mac-mlx-local"], expected)
        self.assertIn(expected, (ANALYSIS / "claims_index.jsonl").read_text())
        self.assertNotIn("LEGACY-M3MAX-QWEN25-15B-MLX", REPO.joinpath(
            "figures/rpt001-v1/F1_legacy_l1_instrument_results.svg").read_text())

    def test_fixture_scale_double_generation_is_byte_identical(self):
        with open(ANALYSIS / "dataset.csv", newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        stacks_a = make_figures.per_stack_metrics(rows)
        stacks_b = make_figures.per_stack_metrics([dict(row) for row in rows])
        outputs_a = (
            make_figures.render_figure(stacks_a),
            make_figures.csv_table(make_figures.T1_COLUMNS,
                make_figures.t1_rows(stacks_a, {})),
            json.dumps(make_figures.claims_row(stacks_a, {
                sid: value["metrics"]["energy_request_j"]["mean"]
                for sid, value in stacks_a.items()}), sort_keys=True) + "\n",
        )
        outputs_b = (
            make_figures.render_figure(stacks_b),
            make_figures.csv_table(make_figures.T1_COLUMNS,
                make_figures.t1_rows(stacks_b, {})),
            json.dumps(make_figures.claims_row(stacks_b, {
                sid: value["metrics"]["energy_request_j"]["mean"]
                for sid, value in stacks_b.items()}), sort_keys=True) + "\n",
        )
        self.assertEqual([v.encode() for v in outputs_a], [v.encode() for v in outputs_b])

    def test_forbidden_gate_bypass_families(self):
        examples = [
            "The small stack uses less energy.",
            "The small stack has lower energy consumption.",
            "This is a 6.7× energy saving.",
            "The small stack outperforms the large stack.",
            "Energy consumption increases with parameter count.",
        ]
        for text in examples:
            self.assertTrue(any(pattern.search(text) for pattern in build_capstone.FORBIDDEN_PHRASES), text)

    @unittest.skipUnless(RUNS.is_dir(), "real runs corpus unavailable")
    def test_gate_inputs_rejects_tampered_bundle_tree(self):
        manifest = json.loads((ANALYSIS / "input_manifest.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "experiments").mkdir()
            tampered = manifest["experiments"][0]["members"][0]
            for exp in manifest["experiments"]:
                shutil.copy2(RUNS / "experiments" / f"{exp['experiment_id']}.json",
                             root / "experiments")
                for member in exp["members"]:
                    if member == tampered:
                        shutil.copytree(RUNS / member, root / member)
                    else:
                        (root / member).symlink_to(RUNS / member, target_is_directory=True)
            with (root / tampered / "summary_metrics.json").open("a", encoding="utf-8") as fh:
                fh.write(" ")
            with self.assertRaises(SystemExit):
                make_figures.gate_inputs(root, manifest)

    @unittest.skipUnless(RUNS.is_dir(), "real runs corpus unavailable")
    def test_exact_means_are_derived_from_source_summaries(self):
        manifest = json.loads((ANALYSIS / "input_manifest.json").read_text())
        expected = {}
        for exp in manifest["experiments"]:
            values = [json.loads((RUNS / member / "summary_metrics.json").read_text())[
                "energy_request_j"] for member in exp["members"]]
            expected[make_figures.STACK_IDS[exp["experiment_id"]]] = statistics.mean(values)
        claim = json.loads((ANALYSIS / "claims_index.jsonl").read_text())
        for stack_id, mean in expected.items():
            self.assertIn(f"{mean!r} J for stack {stack_id}", claim["claim_text"])

    def test_dataset_six_rows_pinned_order(self):
        with open(ANALYSIS / "dataset.csv", newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), 6)
        self.assertEqual(
            [r["run_id"] for r in rows],
            [f"example-mac-mlx-local__r{i}" for i in (1, 2, 3)]
            + [f"example-mac-mlx-qwen35-122b-512t__r{i}" for i in (1, 2, 3)],
        )
        for row in rows:
            self.assertEqual(row["evidence_class"], "legacy_l1_manual_review_pre_2m")
            self.assertFalse(row["bundle_path"].startswith("/"))

    def test_claims_row_shape(self):
        lines = (ANALYSIS / "claims_index.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        row = json.loads(lines[0])
        self.assertEqual(row["schema"], "joulewise.claims_index.v1")
        self.assertEqual(row["claim_id"], "CLM-RPT001-LEGACY-L1-001")
        self.assertEqual(row["claim_level"], "L1")
        self.assertEqual(row["legacy_label"], LEGACY_LABEL)
        self.assertIsNone(row["analysis_manifest_ref"])
        self.assertEqual(row["verdict_ref"]["status"], "not_applicable_l1")
        self.assertIn("44.42591347410544", row["claim_text"])
        self.assertIn("298.68731644234157", row["claim_text"])

    def test_figure_labels_and_honesty(self):
        svg = (REPO / "figures" / "rpt001-v1" /
               "F1_legacy_l1_instrument_results.svg").read_text(encoding="utf-8")
        self.assertIn(LEGACY_LABEL, svg)
        self.assertIn("min–max range (not a confidence interval)", svg)
        self.assertIn("idle-subtracted energy_request_j", svg)
        self.assertIn("gross gross_energy_j", svg)
        self.assertIn("runtime-observed output token", svg)
        self.assertNotIn("95%", svg)
        self.assertNotIn("CI", svg.replace("CPU", ""))

    def test_t1_and_s1_labels(self):
        t1 = (ANALYSIS / "tables" / "T1_legacy_l1_results.md").read_text(encoding="utf-8")
        s1 = (ANALYSIS / "tables" / "S1_legacy_stack_identity.md").read_text(encoding="utf-8")
        self.assertIn(LEGACY_LABEL, t1)
        self.assertIn("cooldown cap hit", t1)
        self.assertIn("unknown (legacy bundle)", s1)
        for field in ("tokenizer_identity", "measurement_boundary", "telemetry_backend"):
            self.assertIn(field, s1)

    def test_report_profile_and_chapters(self):
        src = REPO / "docs" / "report_src"
        profile = json.loads((src / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(profile["schema"], "joulewise.report_profile.v1")
        self.assertEqual(len(profile["chapters"]), 13)
        self.assertEqual(profile["bibliography"], "references.csl.json")
        self.assertEqual(profile["source_map"], "source_map.json")
        self.assertTrue((src / profile["bibliography"]).is_file())
        self.assertTrue((src / profile["source_map"]).is_file())
        for chapter in profile["chapters"]:
            self.assertTrue((src / chapter).is_file(), chapter)
        self.assertIsNone(profile["format_adapter"]["renderer"])

    def test_generated_page_contents(self):
        page = (REPO / "docs" / "report_src" / "generated" /
                "rpt001_vertical_slice.md").read_text(encoding="utf-8")
        self.assertTrue(page.startswith("<!-- GENERATED by scripts/build_capstone.py"))
        for needed in (LEGACY_LABEL, "CLM-RPT001-LEGACY-L1-001",
                       "scripts/build_capstone.py", "--full", "artifact_manifest.json",
                       "Table S1", "Table T1"):
            self.assertIn(needed, page)
        for forbidden in ("more efficient", "less efficient", "scales with model size"):
            self.assertNotIn(forbidden, page.lower())


if __name__ == "__main__":
    unittest.main()
