"""Strict-bundle and CLI integration fixtures for P2-037."""

from __future__ import annotations

import io
import hashlib
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from joulewise.analysis_engine import AnalysisInputError, analyze_claims
from joulewise.analysis_engine.artifact import render_claim_verdicts
from joulewise.analysis_engine.artifact import (
    calculate_claim_verdicts_id,
    validate_claim_verdicts,
)
from joulewise.analysis_manifest import calculate_manifest_id
from joulewise.analysis_engine.multiplicity import holm_adjust
from joulewise.analysis_engine.estimators import StochasticVarianceTerm
from joulewise.cli import main, validate_bundle
from joulewise.detection_floor import (
    build_floor_artifact,
    build_transport_group,
)
from scripts.generate_matrix import main as generate_matrix
from tests.test_detection_floor import make_artifact, make_cell


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"
SIDECARS = {"order_manifest.json", "analysis_manifest.json"}


class AnalysisIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls._temporary.name)
        cls.config_dir = cls.root / "configs"
        cls.runs_root = cls.root / "runs"
        cls.floor_path = cls.root / "floor.json"
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = generate_matrix(
                [
                    "--base",
                    str(BASE_CONFIG),
                    "--model-tag",
                    "mock-model",
                    "--out-dir",
                    str(cls.config_dir),
                ]
            )
        if code != 0:
            raise AssertionError(f"matrix generation failed: {code}")
        for config in sorted(cls.config_dir.glob("*.json")):
            if config.name in SIDECARS:
                continue
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = main(["run", str(config), "--runs-dir", str(cls.runs_root)])
            if code != 0:
                raise AssertionError(f"mock run failed for {config.name}: {code}")
        cls.floor_path.write_text(
            json.dumps(make_artifact(), indent=2) + "\n", encoding="utf-8"
        )
        cls.manifest_path = cls.config_dir / "analysis_manifest.json"

    @classmethod
    def tearDownClass(cls):
        cls._temporary.cleanup()

    def test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact(self):
        first = analyze_claims(
            self.manifest_path,
            self.runs_root,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        second = analyze_claims(
            self.manifest_path,
            self.runs_root,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertEqual(first, second)
        self.assertEqual(render_claim_verdicts(first), render_claim_verdicts(second))
        self.assertEqual(len(first["bundle_audit"]), 30)
        self.assertTrue(all(row["strict_status"] == "valid" for row in first["bundle_audit"]))
        self.assertEqual(len(first["families"]), 4)
        self.assertEqual(len(first["contrasts"]), 24)
        for contrast in first["contrasts"]:
            with self.subTest(contrast=contrast["contrast_id"]):
                evaluation = contrast["claim_evaluation"]
                self.assertEqual(evaluation["outcome"], "not_resolvable")
                self.assertFalse(evaluation["claim_ready_for_l2_l3"])
                # Reducer 0.4.2 supplies the governed precheck, so its
                # absence reason must NOT appear; the remaining fail-closed
                # reasons keep the outcome not_resolvable.
                self.assertNotIn(
                    "window_evidence_precheck_missing", evaluation["reason_codes"]
                )
                self.assertIn(
                    "campaign_cooldown_evidence_missing", evaluation["reason_codes"]
                )
                self.assertIn("floor_transport_inapplicable", evaluation["reason_codes"])
                self.assertNotIn("loo_magnitude_influential", evaluation["reason_codes"])
                self.assertEqual(contrast["estimator"]["n"], 5)
                self.assertEqual(contrast["estimator"]["df"], 4)
                self.assertEqual(len(contrast["loo"]["rows"]), 5)
                self.assertTrue(
                    all(
                        "estimate_magnitude" not in row["influence_triggers"]
                        for row in contrast["loo"]["rows"]
                    )
                )
        by_id = {contrast["contrast_id"]: contrast for contrast in first["contrasts"]}
        for family in first["families"]:
            for omission_index in range(5):
                raw = {
                    contrast_id: by_id[contrast_id]["loo"]["rows"][omission_index]["raw_p"]
                    for contrast_id in family["contrast_ids"]
                }
                adjusted = holm_adjust(raw, m=family["m"])
                for contrast_id in family["contrast_ids"]:
                    self.assertEqual(
                        by_id[contrast_id]["loo"]["rows"][omission_index]["adjusted_p"],
                        adjusted[contrast_id],
                    )
        omitted_loo = json.loads(json.dumps(first))
        omitted_loo["contrasts"][0]["loo"] = {"status": "not_run", "rows": []}
        omitted_loo["claim_verdicts_id"] = calculate_claim_verdicts_id(omitted_loo)
        self.assertTrue(validate_claim_verdicts(omitted_loo))

    def test_named_strata_manifest_completes_leave_one_block_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / "configs"
            shutil.copytree(self.config_dir, config_dir)
            manifest_path = config_dir / "analysis_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            block_ids = manifest["contrasts"][0]["block_ids"]
            manifest["design"]["randomization"] = {
                "scheme": "stratified_paired_label_swap",
                "exchangeability": "within_named_strata",
                "named_strata": [
                    {"stratum_id": "early", "block_ids": block_ids[:3]},
                    {"stratum_id": "late", "block_ids": block_ids[3:]},
                ],
            }
            manifest["manifest_id"] = calculate_manifest_id(manifest)
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            artifact = analyze_claims(
                manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
            )

        self.assertTrue(
            all(
                contrast["loo"]["status"] == "complete"
                for contrast in artifact["contrasts"]
            )
        )
        self.assertTrue(
            all(
                len(contrast["loo"]["rows"]) == 5
                for contrast in artifact["contrasts"]
            )
        )

    def test_hash_bound_campaign_cooldown_is_rechecked_per_member(self):
        runs = self.root / "cooldown-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        bundle_ids = [entry["run_id"] for entry in manifest["entries"]]
        campaign_dir = runs / "campaign_manifests"
        raw_dir = campaign_dir / "raw"
        raw_dir.mkdir(parents=True)
        trace = b'{"idle_power_w":5.0,"timestamp_s":1.0}\n'
        trace_path = raw_dir / "cooldown.jsonl"
        trace_path.write_bytes(trace)
        descriptor = {
            "path": "raw/cooldown.jsonl",
            "sha256": hashlib.sha256(trace).hexdigest(),
            "records": 1,
        }
        session_id = "campaign-fixture"
        members = []
        for index, bundle_id in enumerate(bundle_ids):
            cooldown = (
                {
                    "result": "first_run_exempt",
                    "session_id": session_id,
                    "following_run_id": bundle_id,
                }
                if index == 0
                else {
                    "result": "recovered",
                    "session_id": session_id,
                    "following_run_id": bundle_id,
                    "raw_artifact": descriptor,
                }
            )
            members.append(
                {
                    "run_id": bundle_id,
                    "bundle_ids": [bundle_id],
                    "execution": "invoked",
                    "preceding_campaign_cooldown": cooldown,
                }
            )
        (campaign_dir / "campaign-fixture.json").write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.campaign_provenance.v1",
                    "session_id": session_id,
                    "analysis_manifest_id": manifest["manifest_id"],
                    "first_physical_run_id": bundle_ids[0],
                    "members": members,
                    "cooldown_gates": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertTrue(
            all(row["campaign_cooldown"]["verified"] for row in artifact["bundle_audit"])
        )
        self.assertTrue(
            all(
                "campaign_cooldown_evidence_missing"
                not in contrast["claim_evaluation"]["reason_codes"]
                for contrast in artifact["contrasts"]
            )
        )

        trace_path.write_bytes(trace + b'{"tampered":true}\n')
        refuted = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertTrue(
            any(
                "campaign_cooldown_evidence_missing"
                in contrast["claim_evaluation"]["reason_codes"]
                for contrast in refuted["contrasts"]
            )
        )

    def test_artifact_is_path_relocation_deterministic(self):
        expected = analyze_claims(
            self.manifest_path,
            self.runs_root,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        relocated = self.root / "relocated"
        relocated_configs = relocated / "configs"
        relocated_runs = relocated / "runs"
        relocated_floor = relocated / "floor.json"
        shutil.copytree(self.config_dir, relocated_configs)
        shutil.copytree(self.runs_root, relocated_runs)
        shutil.copy2(self.floor_path, relocated_floor)
        observed = analyze_claims(
            relocated_configs / "analysis_manifest.json",
            relocated_runs,
            relocated_floor,
            strict_validator=validate_bundle,
        )
        self.assertEqual(observed, expected)
        self.assertEqual(render_claim_verdicts(observed), render_claim_verdicts(expected))

    def test_unrelated_invalid_utf8_config_is_ignored_by_closed_set_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / "runs"
            shutil.copytree(self.runs_root, runs)
            before = analyze_claims(
                self.manifest_path,
                runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )
            unrelated = runs / "unrelated-invalid-utf8"
            unrelated.mkdir()
            (unrelated / "config.json").write_bytes(b"\xff\xfe")
            after = analyze_claims(
                self.manifest_path,
                runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )
            self.assertEqual(after, before)
            self.assertEqual(render_claim_verdicts(after), render_claim_verdicts(before))
            self.assertEqual(len(after["bundle_audit"]), 30)

    def test_private_stochastic_seam_changes_recorded_policy_identity(self):
        def unavailable_floor(contrast, condition_id, rows, floor_artifact):
            del contrast, condition_id, rows, floor_artifact
            return None

        def governed_pair_terms(evidence_a, evidence_b, metric):
            del evidence_a, evidence_b, metric
            return (
                (
                    StochasticVarianceTerm(
                        "fixture_governed_j2",
                        variance_a=0.25,
                        variance_b=0.25,
                        correlation_scope="independent_run",
                    ),
                ),
                (),
            )

        artifact = analyze_claims(
            self.manifest_path,
            self.runs_root,
            self.floor_path,
            strict_validator=validate_bundle,
            _floor_request_factory=unavailable_floor,
            _pair_stochastic_factory=governed_pair_terms,
        )
        self.assertIn(
            "private_test_seam:",
            artifact["engine"]["policy_identity"]["floor_resolution"],
        )
        self.assertIn(
            "private_test_seam:",
            artifact["engine"]["policy_identity"]["stochastic_variance"],
        )
        estimator = artifact["contrasts"][0]["estimator"]
        self.assertGreater(estimator["SE_metrology"], 0.0)
        self.assertGreater(estimator["SE_total"], estimator["SE_repeat"])
        repeat_width = (
            estimator["repeat_point_CI95"]["upper"]
            - estimator["repeat_point_CI95"]["lower"]
        )
        metrology_width = (
            estimator["metrology_aware_CI95"]["upper"]
            - estimator["metrology_aware_CI95"]["lower"]
        )
        self.assertGreater(metrology_width, repeat_width)

    def test_cli_default_resolves_exact_floor_from_declared_bundle_inputs(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        condition_ids = sorted(
            {
                entry["condition_id"]
                for entry in manifest["entries"]
                if entry["role"] == "condition"
            }
        )
        cells = []
        for condition_id in condition_ids:
            entries = sorted(
                (
                    entry
                    for entry in manifest["entries"]
                    if entry["condition_id"] == condition_id
                ),
                key=lambda entry: entry["planned_rep_index"],
            )
            cell = make_cell(cell_id=f"floor-{condition_id}", condition=condition_id)
            cell["key"].update(backend="mock", metric="gross_energy_j")
            observations = cell["absolute"]["bundle_observations"]
            for observation, entry in zip(observations, entries, strict=True):
                observation["bundle_id"] = entry["run_id"]
                observation["config_sha256"] = hashlib.sha256(
                    (self.runs_root / entry["run_id"] / "config.json").read_bytes()
                ).hexdigest()
            cell["provenance"]["bundle_ids"] = [
                observation["bundle_id"] for observation in observations
            ]
            cells.append(cell)
        group = build_transport_group(
            transport_group_id="tg-exact-cli",
            backend="mock",
            metric="gross_energy_j",
            window_class="request",
            stack_identity=cells[0]["source_regime"]["stack_identity"],
            source_cells=cells,
            allowed_consumer_condition_families=[
                {
                    key: cell["key"][key]
                    for key in (
                        "condition_family_id",
                        "condition_family_definition",
                        "condition_family_sha256",
                    )
                }
                for cell in cells
            ],
        )
        for cell in cells:
            cell["transport_group_id"] = "tg-exact-cli"
        exact_floor = build_floor_artifact(
            artifact_id="floor-exact-cli",
            calibration_scope="window_a",
            provenance=make_artifact()["provenance"],
            cells=cells,
            transport_groups=[group],
        )
        floor_path = self.root / "floor-exact-cli.json"
        floor_path.write_text(json.dumps(exact_floor, indent=2) + "\n", encoding="utf-8")
        output = self.root / "exact-cli-claim-verdicts.json"
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as stderr:
            code = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(self.runs_root),
                    "--floor-artifact",
                    str(floor_path),
                    "--output",
                    str(output),
                ]
            )
        self.assertEqual(code, 0, stderr.getvalue())
        artifact = json.loads(output.read_text(encoding="utf-8"))
        gross = [
            contrast
            for contrast in artifact["contrasts"]
            if contrast["metric"]["name"] == "gross_energy_j"
        ]
        self.assertTrue(gross)
        self.assertTrue(all(contrast["floor"]["status"] == "resolved" for contrast in gross))
        self.assertTrue(
            all(
                resolution["status"] == "exact"
                for contrast in gross
                for resolution in contrast["floor"]["resolutions"]
            )
        )

    def test_cli_writes_artifact_and_invalid_input_writes_nothing(self):
        output = self.root / "cli-claim-verdicts.json"
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(self.runs_root),
                    "--floor-artifact",
                    str(self.floor_path),
                    "--output",
                    str(output),
                ]
            )
        self.assertEqual(code, 0, stderr.getvalue())
        self.assertTrue(output.is_file())
        self.assertIn("claim-verdicts:", stdout.getvalue())
        invalid_floor = self.root / "invalid-floor.json"
        invalid_floor.write_text("{}\n", encoding="utf-8")
        refused_output = self.root / "must-not-exist.json"
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            refused = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(self.runs_root),
                    "--floor-artifact",
                    str(invalid_floor),
                    "--output",
                    str(refused_output),
                ]
            )
        self.assertEqual(refused, 2)
        self.assertFalse(refused_output.exists())

    def test_cli_refuses_output_aliases_and_paths_inside_immutable_inputs(self):
        floor_before = self.floor_path.read_bytes()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            aliases_floor = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(self.runs_root),
                    "--floor-artifact",
                    str(self.floor_path),
                    "--output",
                    str(self.floor_path),
                ]
            )
        self.assertEqual(aliases_floor, 2)
        self.assertEqual(self.floor_path.read_bytes(), floor_before)

        inside_runs = self.runs_root / "must-not-write-claim-verdicts.json"
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            inside = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(self.runs_root),
                    "--floor-artifact",
                    str(self.floor_path),
                    "--output",
                    str(inside_runs),
                ]
            )
        self.assertEqual(inside, 2)
        self.assertFalse(inside_runs.exists())

    def test_legacy_flag_refuses_any_nonexact_six_bundle_manifest_set(self):
        with self.assertRaisesRegex(
            AnalysisInputError,
            "exactly the frozen six-bundle allowlist",
        ):
            analyze_claims(
                self.manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
                legacy_l1_mechanics=True,
                legacy_allowlist=frozenset(),
            )

    def test_valid_replacement_fills_original_slot_without_sixth_block(self):
        runs = self.root / "replacement-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        shutil.rmtree(runs / target["run_id"])
        replacement = json.loads(
            (self.config_dir / target["config"]).read_text(encoding="utf-8")
        )
        replacement["run_id"] = target["run_id"] + "-replacement"
        replacement["run_metadata"]["tags"].extend(
            [
                f"analysis-replacement-of={target['entry_id']}",
                "analysis-replacement-reason=bundle_incomplete",
            ]
        )
        config_path = self.root / "replacement-config.json"
        config_path.write_text(json.dumps(replacement, indent=2) + "\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["run", str(config_path), "--runs-dir", str(runs)]), 0)
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertEqual(len(artifact["sampling_audit"]["valid_replacements"]), 1)
        self.assertFalse(artifact["sampling_audit"]["top_up_detected"])
        self.assertEqual(artifact["sampling_audit"]["demoted_contrast_ids"], [])
        affected = [
            contrast
            for contrast in artifact["contrasts"]
            if target["cell_id"]
            in {
                contrast["conditions"]["cell_a_id"],
                contrast["conditions"]["cell_b_id"],
            }
        ]
        self.assertTrue(affected)
        self.assertTrue(all(contrast["estimator"]["n"] == 5 for contrast in affected))

    def test_replacement_with_changed_rep_tag_is_topup_not_slot_fill(self):
        runs = self.root / "wrong-rep-replacement-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        shutil.rmtree(runs / target["run_id"])
        replacement = json.loads(
            (self.config_dir / target["config"]).read_text(encoding="utf-8")
        )
        replacement["run_id"] = target["run_id"] + "-wrong-rep-replacement"
        replacement["run_metadata"]["tags"] = [
            "rep6" if tag == "rep1" else tag
            for tag in replacement["run_metadata"]["tags"]
        ]
        replacement["run_metadata"]["tags"].extend(
            [
                f"analysis-replacement-of={target['entry_id']}",
                "analysis-replacement-reason=bundle_incomplete",
            ]
        )
        config_path = self.root / "wrong-rep-replacement-config.json"
        config_path.write_text(
            json.dumps(replacement, indent=2) + "\n", encoding="utf-8"
        )
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["run", str(config_path), "--runs-dir", str(runs)]), 0)

        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertEqual(artifact["sampling_audit"]["valid_replacements"], [])
        self.assertTrue(artifact["sampling_audit"]["top_up_detected"])
        extra = next(
            row
            for row in artifact["bundle_audit"]
            if row["bundle_id"] == replacement["run_id"]
        )
        self.assertIn("config_hash_mismatch", extra["base_reason_codes"])

    def test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples(self):
        runs = self.root / "incomplete-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        shutil.rmtree(runs / target["run_id"])
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        affected = [
            contrast
            for contrast in artifact["contrasts"]
            if target["cell_id"]
            in {
                contrast["conditions"]["cell_a_id"],
                contrast["conditions"]["cell_b_id"],
            }
        ]
        self.assertEqual(len(affected), 12)
        for contrast in affected:
            with self.subTest(contrast=contrast["contrast_id"]):
                self.assertEqual(contrast["estimator"]["n"], 4)
                self.assertEqual(contrast["estimator"]["df"], 3)
                missing = next(
                    row
                    for row in contrast["bundle_blocks"]["blocks"]
                    if row["block_id"] == target["block_id"]
                )
                self.assertFalse(missing["included"])
                self.assertIn("bundle_missing", missing["reason_codes"])
                self.assertIn(
                    "fixed_n_plan_incomplete",
                    contrast["claim_evaluation"]["reason_codes"],
                )
                self.assertEqual(
                    contrast["claim_evaluation"]["outcome"],
                    "not_resolvable",
                )

    def test_bundle_config_byte_mutation_is_excluded_even_when_identity_and_metadata_hash_match(self):
        runs = self.root / "config-byte-mutation-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        bundle = runs / target["run_id"]
        config_path = bundle / "config.json"
        config_path.write_bytes(config_path.read_bytes() + b" ")
        config_hash = hashlib.sha256(config_path.read_bytes()).hexdigest()
        metadata_path = bundle / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["config_sha256"] = config_hash
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        audit = next(
            row
            for row in artifact["bundle_audit"]
            if row["entry_id"] == target["entry_id"]
        )
        self.assertEqual(audit["inclusion_status"], "excluded")
        self.assertIn("config_hash_mismatch", audit["base_reason_codes"])
        self.assertNotEqual(
            audit["config_sha256"], audit["expected_config_sha256"]
        )

    def test_registered_bundle_symlink_escape_is_rejected(self):
        runs = self.root / "symlink-escape-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(entry for entry in manifest["entries"] if entry["role"] == "condition")
        outside = self.root / "outside-registered-bundle"
        shutil.copytree(runs / target["run_id"], outside)
        shutil.rmtree(runs / target["run_id"])
        (runs / target["run_id"]).symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(AnalysisInputError, "must not be a symlink"):
            analyze_claims(
                self.manifest_path,
                runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )

    def test_public_engine_rejects_false_precheck_without_governed_reason(self):
        runs = self.root / "false-precheck-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition" and entry["planned_rep_index"] == 1
        )
        summary_path = runs / target["run_id"] / "summary_metrics.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["window_evidence_precheck"] = {
            "gross_request": {"eligible": False, "reasons": []}
        }
        summary_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        audit = next(
            row
            for row in artifact["bundle_audit"]
            if row["entry_id"] == target["entry_id"]
        )
        gross = audit["window_prechecks"]["gross_request"]
        self.assertFalse(gross["eligible"])
        self.assertIn("window_evidence_precheck_missing", gross["reasons"])

    def test_realized_model_artifact_identity_disagreement_fails_cohort_closed(self):
        runs = self.root / "identity-mismatch-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition" and entry["planned_rep_index"] == 1
        )
        metadata_path = runs / target["run_id"] / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["workload_provenance"]["model"]["artifact_identity"]["sha256"] = (
            "0" * 64
        )
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        audit = next(
            row
            for row in artifact["bundle_audit"]
            if row["entry_id"] == target["entry_id"]
        )
        self.assertEqual(audit["strict_status"], "valid")
        self.assertEqual(audit["inclusion_status"], "excluded")
        self.assertIn("config_hash_mismatch", audit["base_reason_codes"])

    def test_unregistered_matching_topup_demotes_but_preserves_fixed_n_analysis(self):
        runs = self.root / "topup-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        topup = json.loads((self.config_dir / target["config"]).read_text(encoding="utf-8"))
        topup["run_id"] = target["run_id"] + "-topup"
        topup["run_metadata"]["tags"] = [
            "rep6" if tag == "rep1" else tag
            for tag in topup["run_metadata"]["tags"]
        ]
        config_path = self.root / "topup-config.json"
        config_path.write_text(json.dumps(topup, indent=2) + "\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["run", str(config_path), "--runs-dir", str(runs)]), 0)
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertTrue(artifact["sampling_audit"]["top_up_detected"])
        self.assertEqual(len(artifact["sampling_audit"]["demoted_contrast_ids"]), 12)
        demoted = [
            contrast
            for contrast in artifact["contrasts"]
            if contrast["sampling"]["confirmatory_status"] == "demoted_exploratory"
        ]
        self.assertEqual(len(demoted), 12)
        for contrast in demoted:
            self.assertEqual(contrast["estimator"]["n"], 5)
            self.assertIn(
                "outcome_dependent_top_up",
                contrast["claim_evaluation"]["reason_codes"],
            )
            self.assertFalse(contrast["claim_evaluation"]["claim_ready_for_l2_l3"])

        laundered = json.loads(json.dumps(artifact))
        laundered["sampling_audit"].update(
            unregistered_matching_bundles=[],
            top_up_detected=False,
            demoted_contrast_ids=[],
        )
        for contrast in laundered["contrasts"]:
            contrast["sampling"]["confirmatory_status"] = "confirmatory"
            evaluation = contrast["claim_evaluation"]
            evaluation["reason_codes"] = [
                reason
                for reason in evaluation["reason_codes"]
                if reason != "outcome_dependent_top_up"
            ]
        laundered["claim_verdicts_id"] = calculate_claim_verdicts_id(laundered)
        errors = validate_claim_verdicts(laundered)
        self.assertTrue(
            any("must exactly enumerate top-up audits" in error for error in errors),
            errors,
        )

    def test_unregistered_matching_sentinel_topup_demotes_linked_contrasts(self):
        runs = self.root / "sentinel-topup-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "drift_sentinel_start"
            and entry["planned_rep_index"] == 1
        )
        topup = json.loads((self.config_dir / target["config"]).read_text(encoding="utf-8"))
        topup["run_id"] = target["run_id"] + "-topup"
        topup["run_metadata"]["tags"] = [
            "rep6" if tag == "rep1" else tag
            for tag in topup["run_metadata"]["tags"]
        ]
        config_path = self.root / "sentinel-topup-config.json"
        config_path.write_text(json.dumps(topup, indent=2) + "\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["run", str(config_path), "--runs-dir", str(runs)]), 0)
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertTrue(artifact["sampling_audit"]["top_up_detected"])
        self.assertEqual(len(artifact["sampling_audit"]["demoted_contrast_ids"]), 24)
        self.assertTrue(
            all(
                contrast["sampling"]["confirmatory_status"]
                == "demoted_exploratory"
                for contrast in artifact["contrasts"]
            )
        )


if __name__ == "__main__":
    unittest.main()
