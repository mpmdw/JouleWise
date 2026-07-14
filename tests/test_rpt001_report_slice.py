"""Offline smoke tests for the RPT-001 report vertical slice.

These run against the committed rpt001-v2 artifacts and report source; they
do NOT reread the real bundle corpus (which is gitignored). Real-bundle
ingestion is the lead-run local gate (spec §0.4/§9.4).
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
import statistics
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "analysis" / "rpt001-v2"
SEALED_ANALYSIS = REPO / "analysis" / "rpt001-v1"
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
claims_lint = load_script("rpt001_claims_lint", "claims_lint.py")


class TestRpt001Artifacts(unittest.TestCase):
    def test_1p5b_identifier_is_pinned(self):
        expected = "LEGACY-M3MAX-QWEN25-1P5B-MLX"
        self.assertEqual(make_figures.STACK_IDS["example-mac-mlx-local"], expected)
        self.assertIn(expected, (ANALYSIS / "claims_index.jsonl").read_text())
        self.assertNotIn("LEGACY-M3MAX-QWEN25-15B-MLX", REPO.joinpath(
            "figures/rpt001-v2/F1_legacy_l1_instrument_results.svg").read_text())

    def test_v1_publication_is_byte_unchanged(self):
        expected = {
            "analysis/rpt001-v1/aggregates.json": "fe849005553f0671c1e5d8b213497e0a4139918323ae16635acd98fa278b6f6f",
            "analysis/rpt001-v1/artifact_manifest.json": "69a5344eb55796fd9e6bd5a02965f6e8e2c8ae3ba3fcca1c615968a3b1a77e8b",
            "analysis/rpt001-v1/claims_index.jsonl": "c8d8a841e6036a715e20c443b8982e0035de5e4b258675a3e86346b274da3df2",
            "analysis/rpt001-v1/dataset.csv": "0a2fdf9912b4a364ea7c87211b5c7599eebf20197a1d48b43629019644ea660f",
            "analysis/rpt001-v1/input_manifest.json": "cf016eed5434a228e50c8b95591ff10408a6d90b025bb1ea0a857f1bd01b9805",
            "analysis/rpt001-v1/tables/S1_legacy_stack_identity.csv": "975f66fe94a0017e380eccb23146838232f74aa35579aa46e4d8c67e78a6516a",
            "analysis/rpt001-v1/tables/S1_legacy_stack_identity.md": "5e8433e19817e46b145a580916b27cdf0260c400467d444c3aeb6cf730827571",
            "analysis/rpt001-v1/tables/T1_legacy_l1_results.csv": "6e0096a80a4c6f8d8ada22f9add2bf58d826359a3be3d250e34ef319304dea10",
            "analysis/rpt001-v1/tables/T1_legacy_l1_results.md": "c28a99db36e60cb6ea37560c3da140ce40be566e124e5dbc5761dafd1abd542e",
            "figures/rpt001-v1/F1_legacy_l1_instrument_results.svg": "33e5918dc74470433f1b868f2ba9e68b102c581820ea19fa83a9a02186af3b41",
        }
        for relative, digest in expected.items():
            with self.subTest(relative=relative):
                self.assertEqual(hashlib.sha256((REPO / relative).read_bytes()).hexdigest(), digest)

    def test_defaults_and_artifact_version_are_v2(self):
        self.assertEqual(make_figures.ARTIFACT_VERSION, "rpt001-v2")
        self.assertEqual(build_capstone.ANALYSIS, ANALYSIS)
        self.assertIn("figures/rpt001-v2/", build_capstone.FIGURE_REL)
        self.assertEqual(
            claims_lint.DEFAULT_CLAIMS_INDEX_PATH,
            Path("analysis/rpt001-v2/claims_index.jsonl"),
        )

    def test_realized_tokens_come_from_artifact_without_stop_inference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            member = "example-mac-mlx-local__r1"
            bundle = root / member
            (bundle / "outputs").mkdir(parents=True)
            (bundle / "config.json").write_text(json.dumps({
                "model": {}, "quantization": {}, "hardware_target": {},
                "workload_profile": {"output_tokens": 2, "prompt_text": "p"},
            }))
            (bundle / "metadata.json").write_text(json.dumps({
                "workload_observed": {"output_token_count": 2}, "device": {},
            }))
            (bundle / "summary_metrics.json").write_text(json.dumps({
                "gross_energy_j": 3, "energy_request_j": 2,
                "energy_output_token_j": 1, "ttft_s": 0.1,
                "throughput_tokens_s": 20, "measurement_quality": {},
            }))
            (bundle / "outputs" / "tokens.jsonl").write_text(
                '{"index": 0}\n{"index": 1}\n', encoding="utf-8"
            )
            (bundle / "events.jsonl").write_text(json.dumps({
                "timestamp_s": 1.0, "event_type": "phase_end", "phase": "decode",
                "message": "done", "metadata": {"emitted_tokens": 2},
            }) + "\n")
            rows = make_figures.extract_rows(
                root,
                {"example-mac-mlx-local": {"members": [member], "cooldown": []}},
                {member: "tree"},
            )
        self.assertEqual(rows[0]["runtime_output_tokens"], 2)
        self.assertEqual(rows[0]["token_count_source"], "outputs/tokens.jsonl")
        self.assertEqual(rows[0]["runtime_stop_reason"], "unknown")
        self.assertEqual(rows[0]["output_policy"], "unknown")
        self.assertEqual(rows[0]["energy_output_token_j"], "")

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
            self.assertEqual(row["runtime_output_tokens"], "512")
            self.assertEqual(row["token_count_source"], "outputs/tokens.jsonl")
            self.assertEqual(row["runtime_stop_reason"], "unknown")
            self.assertEqual(row["output_policy"], "unknown")
            self.assertEqual(row["energy_output_token_j"], "")

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
        self.assertEqual(
            (ANALYSIS / "claims_index.jsonl").read_bytes(),
            (SEALED_ANALYSIS / "claims_index.jsonl").read_bytes(),
        )

    def test_figure_labels_and_honesty(self):
        svg = (REPO / "figures" / "rpt001-v2" /
               "F1_legacy_l1_instrument_results.svg").read_text(encoding="utf-8")
        self.assertIn(LEGACY_LABEL, svg)
        self.assertIn("min–max range (not a confidence interval)", svg)
        self.assertIn("idle-subtracted energy_request_j", svg)
        self.assertIn("gross gross_energy_j", svg)
        self.assertIn("Per-output-token companion omitted", svg)
        self.assertIn("no stop reason is inferred", svg)
        self.assertNotIn("runtime-observed output token", svg)
        self.assertNotIn("Panel B", svg)
        self.assertNotIn("95%", svg)
        self.assertNotIn("CI", svg.replace("CPU", ""))

    def test_t1_and_s1_labels(self):
        t1 = (ANALYSIS / "tables" / "T1_legacy_l1_results.md").read_text(encoding="utf-8")
        s1 = (ANALYSIS / "tables" / "S1_legacy_stack_identity.md").read_text(encoding="utf-8")
        self.assertIn(LEGACY_LABEL, t1)
        self.assertIn("cooldown cap hit", t1)
        self.assertIn("per-output-token companion is omitted", t1)
        self.assertNotIn("idlesub_mj_output_token_mean", t1)
        self.assertIn("unknown (legacy bundle)", s1)
        for field in ("tokenizer_identity", "measurement_boundary", "telemetry_backend"):
            self.assertIn(field, s1)

    def test_v2_artifact_manifest_references_only_v2_outputs(self):
        manifest = json.loads((ANALYSIS / "artifact_manifest.json").read_text())
        self.assertEqual(manifest["artifact_version"], "rpt001-v2")
        self.assertTrue(manifest["outputs"])
        self.assertTrue(all("rpt001-v2" in path for path in manifest["outputs"]))

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
                       "Table S1", "Table T1", "per-output-token companion is omitted",
                       "not labeled", "as an observed stop reason", "rpt001-v2"):
            self.assertIn(needed, page)
        self.assertNotIn("Panel B", page)
        self.assertNotIn("mJ per runtime-observed output token", page)
        self.assertNotIn("values remain explicitly tokenizer-unknown", page)
        for forbidden in ("more efficient", "less efficient", "scales with model size"):
            self.assertNotIn(forbidden, page.lower())


if __name__ == "__main__":
    unittest.main()
