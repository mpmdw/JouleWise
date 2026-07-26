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
from unittest import mock

from joulewise.analysis_engine import AnalysisInputError, analyze_claims
from joulewise.analysis_engine.artifact import render_claim_verdicts
from joulewise.analysis_engine.artifact import (
    calculate_claim_verdicts_id,
    validate_claim_verdicts,
)
from joulewise.analysis_manifest import calculate_manifest_id
from joulewise.analysis_engine.estimators import StochasticVarianceTerm
from joulewise.analysis_engine.multiplicity import holm_adjust
from joulewise.analysis_engine.inputs import (
    BundleEvidence,
    CONSUMPTION_PROVENANCE_PRECHECK_KEY,
    FloorEvidenceBinding,
    MOCK_TELEMETRY_CLAIM_REFUSAL,
    _campaign_cooldown_evidence,
    campaign_cooldown_evidence,
    floor_binding_reason_codes,
    floor_request_for_evidence,
    floor_stack_identity,
    load_analysis_inputs,
    window_evidence_precheck,
)
from joulewise.idle_admission import ADAPTER_CONTINUITY_SCHEMA, NEG8_BRACKET_SCHEMA
from joulewise.whole_window import (
    CustodyTelemetryIdentity,
    IDLE_ADMISSION_CORE_SCHEMA,
    WHOLE_WINDOW_SCHEMA,
    build_row_provenance,
    source_manifest_descriptors,
)
from joulewise.cli import main, validate_bundle
from joulewise.detection_floor import (
    abba_delta,
    absolute_false_effect_floor,
    build_absolute_record,
    build_comparative_record,
    build_floor_artifact,
    build_transport_group,
    canonical_domain_sha256,
    comparative_false_effect_floor,
    complete_bundle_sha256,
    STACK_IDENTITY_DOMAIN,
    validate_floor_artifact,
)
from scripts.generate_matrix import main as generate_matrix
from tests.test_detection_floor import (
    condition_family,
    make_artifact,
    make_cell,
    whole_window_allowance,
)


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"
SIDECARS = {"order_manifest.json", "analysis_manifest.json"}
CLEAN_SOURCE_STATE = {
    "git_commit": "1" * 40,
    "tracked": "clean",
    "staged": "clean",
    "untracked": "clean",
    "diff_sha256": "2" * 64,
}
# No strict-valid powermetrics fixture exists in-repo. The positive companions
# therefore stipulate production telemetry identity while exercising the real
# strict-valid mock bundles and the real analyze_claims wiring.
PRODUCTION_TELEMETRY_IDENTITY = CustodyTelemetryIdentity(
    custody_bound_config=True,
    config_backend_class="powermetrics",
    metadata_backend_class="powermetrics",
    summary_backend_class="powermetrics",
    triangle_agrees=True,
)


def install_passing_analysis_whole_window(
    runs_root: Path, bundle_ids: list[str], *, source_name: str
) -> None:
    """Install one provenance-bound passing verdict for a synthetic corpus."""

    bundle_ids = sorted(bundle_ids)
    reference_ids = [
        f"{source_name}-neg8-reference-start",
        f"{source_name}-neg8-reference-end",
    ]
    for bundle_id in reference_ids:
        bundle = runs_root / bundle_id
        bundle.mkdir(parents=True, exist_ok=True)
        summary = {
            "gross_energy_j": 1.0,
            "energy_anchor_shift_envelopes": {
                "/gross_energy_j": {
                    "point_j": 1.0,
                    "lower_j": 0.99,
                    "upper_j": 1.01,
                }
            },
        }
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
    covered_ids = sorted([*bundle_ids, *reference_ids])
    # Anchor to the repo-registered production policy: re-derivation resolves
    # tolerances from tracked policy files only (fail-closed on unknown shas).
    registered_policy_path = (
        ROOT / "configs" / "campaign_policies" / "quiet_mac_p2_production.json"
    )
    policy_sha = hashlib.sha256(registered_policy_path.read_bytes()).hexdigest()
    registered_bracket = json.loads(registered_policy_path.read_text())[
        "idle_admission_extension"
    ]["neg8_bracket"]
    campaign_dir = runs_root / "campaign_manifests"
    campaign_dir.mkdir(parents=True, exist_ok=True)
    source_path = campaign_dir / f"{source_name}.json"
    source_path.write_text(
        json.dumps(
            {
                "schema_version": "joulewise.campaign_provenance.v1",
                "session_id": source_name,
                "analysis_manifest_id": None,
                "campaign_policy": {"sha256": policy_sha},
                "members": [
                    {
                        "execution": "invoked",
                        "bundle_ids": [reference_ids[0]],
                        "role": "neg8_daily_reference_start",
                        "sentinel_position": "start",
                    },
                    {
                        "execution": "invoked",
                        "bundle_ids": bundle_ids,
                    },
                    {
                        "execution": "invoked",
                        "bundle_ids": [reference_ids[1]],
                        "role": "neg8_daily_reference_end",
                        "sentinel_position": "end",
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    descriptors = source_manifest_descriptors(runs_root, [source_path])
    row = {
        "schema_version": WHOLE_WINDOW_SCHEMA,
        "record_type": "idle_admission_whole_window_verdict",
        "status": "passed",
        "campaign_policy": {"sha256": policy_sha},
        "bundle_ids": covered_ids,
        "idle_admission_core": {
            "schema_version": IDLE_ADMISSION_CORE_SCHEMA,
            "policy_sha256": policy_sha,
            "members": [
                {
                    "bundle_id": bundle_id,
                    "cpu_admission": {"decision": "admitted"},
                }
                for bundle_id in covered_ids
            ],
            "adapter_wattage_continuity": {
                "schema_version": ADAPTER_CONTINUITY_SCHEMA,
                "decision": "stable",
            },
            "neg8_bracket": {
                "schema_version": NEG8_BRACKET_SCHEMA,
                "decision": "passed",
                "policy": dict(registered_bracket),
            },
            "conditions": [],
        },
    }
    row["row_provenance"] = build_row_provenance(
        policy_sha256=policy_sha,
        bundle_ids=covered_ids,
        source_manifests=descriptors,
    )
    (runs_root / "campaign_log.jsonl").write_text(json.dumps(row) + "\n")


class AnalysisIntegrationTests(unittest.TestCase):
    def setUp(self):
        source_patch = mock.patch(
            "joulewise.bundle._capture_source_state",
            return_value=dict(CLEAN_SOURCE_STATE),
        )
        source_patch.start()
        self.addCleanup(source_patch.stop)

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
        with mock.patch(
            "joulewise.bundle._capture_source_state",
            return_value=dict(CLEAN_SOURCE_STATE),
        ):
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
        manifest = json.loads(cls.manifest_path.read_text())
        bundle_ids = sorted(entry["run_id"] for entry in manifest["entries"])
        install_passing_analysis_whole_window(
            cls.runs_root,
            bundle_ids,
            source_name="analysis-whole-window-source",
        )

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
        self.assertTrue(
            all(
                row["inclusion_status"] == "excluded"
                and MOCK_TELEMETRY_CLAIM_REFUSAL in row["base_reason_codes"]
                for row in first["bundle_audit"]
            )
        )
        self.assertEqual(len(first["families"]), 4)
        self.assertEqual(len(first["contrasts"]), 24)
        for contrast in first["contrasts"]:
            with self.subTest(contrast=contrast["contrast_id"]):
                evaluation = contrast["claim_evaluation"]
                self.assertEqual(evaluation["outcome"], "not_estimable")
                self.assertFalse(evaluation["claim_ready_for_l2_l3"])
                self.assertIn(
                    MOCK_TELEMETRY_CLAIM_REFUSAL,
                    evaluation["reason_codes"],
                )
                # Reducer 0.4.2 supplies the governed precheck, so its
                # absence reason must NOT appear; the remaining fail-closed
                # reasons keep the mock campaign terminally ineligible.
                self.assertNotIn(
                    "window_evidence_precheck_missing", evaluation["reason_codes"]
                )

                self.assertIn(
                    "campaign_cooldown_evidence_missing", evaluation["reason_codes"]
                )
                self.assertIn("floor_transport_inapplicable", evaluation["reason_codes"])
                self.assertNotIn("loo_magnitude_influential", evaluation["reason_codes"])
                self.assertEqual(contrast["estimator"]["n"], 0)
                self.assertIsNone(contrast["estimator"]["df"])
                self.assertEqual(
                    contrast["loo"],
                    {"status": "not_run", "rows": []},
                )
        self.assertEqual(validate_claim_verdicts(first), [])

    def test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity(
        self,
    ):
        with mock.patch(
            "joulewise.analysis_engine.inputs.custody_telemetry_identity",
            return_value=PRODUCTION_TELEMETRY_IDENTITY,
        ):
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
        self.assertTrue(
            all(row["strict_status"] == "valid" for row in first["bundle_audit"])
        )
        self.assertEqual(len(first["families"]), 4)
        self.assertEqual(len(first["contrasts"]), 24)
        for contrast in first["contrasts"]:
            with self.subTest(contrast=contrast["contrast_id"]):
                evaluation = contrast["claim_evaluation"]
                self.assertEqual(evaluation["outcome"], "not_resolvable")
                self.assertFalse(evaluation["claim_ready_for_l2_l3"])
                self.assertNotIn(
                    "window_evidence_precheck_missing", evaluation["reason_codes"]
                )
                self.assertIn(
                    "campaign_cooldown_evidence_missing", evaluation["reason_codes"]
                )
                self.assertIn(
                    "floor_transport_inapplicable", evaluation["reason_codes"]
                )
                self.assertNotIn(
                    "loo_magnitude_influential", evaluation["reason_codes"]
                )
                self.assertEqual(contrast["estimator"]["n"], 5)
                self.assertEqual(contrast["estimator"]["df"], 4)
                self.assertEqual(len(contrast["loo"]["rows"]), 5)
                self.assertTrue(
                    all(
                        "estimate_magnitude" not in row["influence_triggers"]
                        for row in contrast["loo"]["rows"]
                    )
                )
        by_id = {
            contrast["contrast_id"]: contrast for contrast in first["contrasts"]
        }
        for family in first["families"]:
            for omission_index in range(5):
                raw = {
                    contrast_id: by_id[contrast_id]["loo"]["rows"][
                        omission_index
                    ]["raw_p"]
                    for contrast_id in family["contrast_ids"]
                }
                adjusted = holm_adjust(raw, m=family["m"])
                for contrast_id in family["contrast_ids"]:
                    self.assertEqual(
                        by_id[contrast_id]["loo"]["rows"][omission_index][
                            "adjusted_p"
                        ],
                        adjusted[contrast_id],
                    )
        omitted_loo = json.loads(json.dumps(first))
        omitted_loo["contrasts"][0]["loo"] = {"status": "not_run", "rows": []}
        omitted_loo["claim_verdicts_id"] = calculate_claim_verdicts_id(
            omitted_loo
        )
        self.assertTrue(validate_claim_verdicts(omitted_loo))

    def test_analysis_loader_refuses_when_whole_window_verdict_is_missing(self):
        # F5 defect shape: P2-037 formerly loaded cleanup/cooldown/bundles/floor
        # while routing entirely around the campaign-wide causal verdict.
        with tempfile.TemporaryDirectory() as tmp:
            copied_runs = Path(tmp) / "runs-without-whole-window"
            shutil.copytree(self.runs_root, copied_runs)
            (copied_runs / "campaign_log.jsonl").unlink()
            loaded = load_analysis_inputs(
                self.manifest_path,
                copied_runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )
            self.assertTrue(loaded.registered)
            for evidence in loaded.registered.values():
                self.assertFalse(evidence.included)
                self.assertIn(
                    "whole_window_neg8_verdict_missing", evidence.base_reason_codes
                )

    def test_analysis_loader_consumes_session_operated_envelopes(self):
        """Claim inputs use the authenticated widened view, not stored bounds."""

        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target_id = manifest["entries"][0]["run_id"]
        summary_path = self.runs_root / target_id / "summary_metrics.json"
        stored_bytes = summary_path.read_bytes()
        widened_by_bundle: dict[str, Mapping[str, object]] = {}

        class FakeConsumptionSession:
            def __init__(self, runs_root, bundle_ids):
                self.runs_root = Path(runs_root)
                self.bundle_ids = frozenset(bundle_ids)
                self.ready = True
                self.refusal_reasons = ()

            def summary_for(self, bundle_id):
                summary = json.loads(
                    (self.runs_root / bundle_id / "summary_metrics.json").read_text(
                        encoding="utf-8"
                    )
                )
                point = float(summary["gross_energy_j"])
                summary["energy_anchor_shift_envelopes"] = {
                    "/gross_energy_j": {
                        "method": "authenticated_anchor_shift_extrema_v1",
                        "anchor_bound_s": 0.03,
                        "point_j": point,
                        "lower_j": point - 0.25,
                        "upper_j": point + 0.25,
                        "max_abs_delta_j": 0.25,
                    }
                }
                widened_by_bundle[bundle_id] = summary
                return summary

            def provenance_for(self, bundle_id):
                envelope = widened_by_bundle[bundle_id][
                    "energy_anchor_shift_envelopes"
                ]["/gross_energy_j"]
                return {
                    "consumption_semantics_id": (
                        "d078_authenticated_max_bracket_rederivation_v1"
                    ),
                    "minted_bound_dominated": True,
                    "minted_fiducial_bound_s": 0.01,
                    "operative_fiducial_bound_s": 0.03,
                    "calibration_bracket": {
                        "pre": {
                            "bundle_id": "pre",
                            "manifest_sha256": "1" * 64,
                            "calibration_evidence_sha256": "2" * 64,
                        },
                        "post": {
                            "bundle_id": "post",
                            "manifest_sha256": "3" * 64,
                            "calibration_evidence_sha256": "4" * 64,
                        },
                    },
                    "operative_envelopes": {
                        "/gross_energy_j": {
                            **envelope,
                            "half_width_j": 0.25,
                        }
                    },
                }

        with (
            mock.patch(
                "joulewise.analysis_engine.inputs.AuthenticatedConsumptionSession",
                FakeConsumptionSession,
            ),
            mock.patch(
                "joulewise.analysis_engine.inputs.whole_window_refusal_reasons",
                return_value=(),
            ),
            mock.patch(
                "joulewise.analysis_engine.inputs.whole_window_drift_allowances",
                return_value=mock.Mock(status="legacy", allowances={}),
            ),
        ):
            loaded = load_analysis_inputs(
                self.manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
            )

        target = next(
            evidence
            for evidence in loaded.effective.values()
            if evidence.bundle_id == target_id
        )
        self.assertIs(target.summary, widened_by_bundle[target_id])
        self.assertEqual(
            target.summary["energy_anchor_shift_envelopes"][
                "/gross_energy_j"
            ]["anchor_bound_s"],
            0.03,
        )
        self.assertIn(
            CONSUMPTION_PROVENANCE_PRECHECK_KEY,
            target.audit_row()["window_prechecks"],
        )
        self.assertEqual(summary_path.read_bytes(), stored_bytes)

    def test_production_request_factory_reaches_predeclared_transport(self):
        loaded = load_analysis_inputs(
            self.manifest_path,
            self.runs_root,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        contrast = loaded.manifest["contrasts"][0]
        condition_id = contrast["condition_a_id"]
        evidence = [
            row
            for row in loaded.effective.values()
            if row.entry.get("condition_id") == condition_id
        ]
        self.assertTrue(evidence)
        stack = floor_stack_identity(evidence[0].raw_config, evidence[0].metadata)
        self.assertIsNotNone(stack)
        source = make_cell(cell_id="transport-source", condition="calibration-only")
        source["key"].update(
            backend="mock",
            metric=contrast["floor_selector"]["metric"],
            window_class=contrast["floor_selector"]["window_class"],
        )
        source["source_regime"]["stack_identity"] = stack
        source["source_regime"]["stack_identity_sha256"] = canonical_domain_sha256(
            STACK_IDENTITY_DOMAIN, stack
        )
        source["transport_group_id"] = "tg-production-transport"
        group = build_transport_group(
            transport_group_id="tg-production-transport",
            backend="mock",
            metric=contrast["floor_selector"]["metric"],
            window_class=contrast["floor_selector"]["window_class"],
            stack_identity=stack,
            source_cells=[source],
            allowed_consumer_condition_families=[condition_family(condition_id)],
        )
        artifact = build_floor_artifact(
            artifact_id="production-transport",
            calibration_scope="window_a",
            provenance=make_artifact()["provenance"],
            cells=[source],
            transport_groups=[group],
        )
        binding = FloorEvidenceBinding(
            bound_cell_ids=frozenset({source["cell_id"]}),
            cell_scientific_identity_sha256={},
            cell_stack_identity_sha256={
                source["cell_id"]: source["source_regime"]["stack_identity_sha256"]
            },
            bound_bundle_sha256s=frozenset(),
            problems_by_cell={source["cell_id"]: ()},
            global_problems=(),
        )
        request = floor_request_for_evidence(
            artifact,
            binding,
            contrast,
            condition_id,
            evidence,
        )
        self.assertIsNotNone(request)
        self.assertEqual(request.condition_family_id, condition_id)
        self.assertEqual(request.stack_identity_sha256, group["stack_identity_sha256"])

    def test_named_strata_manifest_preserves_terminal_mock_refusal(self):
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
            loaded = load_analysis_inputs(
                manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
            )

        self.assertEqual(
            loaded.manifest["design"]["randomization"]["scheme"],
            "stratified_paired_label_swap",
        )
        self.assertTrue(loaded.registered)
        self.assertTrue(
            all(
                not evidence.included
                and MOCK_TELEMETRY_CLAIM_REFUSAL
                in evidence.base_reason_codes
                for evidence in loaded.registered.values()
            )
        )

    def test_named_strata_manifest_preserves_terminal_mock_refusal_with_production_telemetry_identity(
        self,
    ):
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
            with mock.patch(
                "joulewise.analysis_engine.inputs.custody_telemetry_identity",
                return_value=PRODUCTION_TELEMETRY_IDENTITY,
            ):
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
        trace = (
            b'{"idle_power_w":5.0,"release":true,'
            b'"release_criteria_met_late":false,"timestamp_s":1.0}\n'
        )
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

    def test_physical_repetition_rows_supply_each_canonical_cooldown(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / "runs"
            campaign_dir = runs / "campaign_manifests"
            raw_dir = campaign_dir / "raw"
            raw_dir.mkdir(parents=True)
            trace = (
                b'{"release":true,"release_criteria_met_late":false,'
                b'"rolling_mean_power_w":5.0,"timestamp_s":10.0}\n'
            )
            trace_path = raw_dir / "config-r2.jsonl"
            trace_path.write_bytes(trace)
            descriptor = {
                "path": "raw/config-r2.jsonl",
                "sha256": hashlib.sha256(trace).hexdigest(),
                "records": 1,
            }
            session_id = "physical-repetition-campaign"
            first_run_id = "config__r1"
            second_run_id = "config__r2"
            first_cooldown = {
                "result": "first_run_exempt",
                "session_id": session_id,
                "following_run_id": first_run_id,
            }
            second_cooldown = {
                "result": "recovered",
                "session_id": session_id,
                "following_run_id": second_run_id,
                "raw_artifact": descriptor,
            }
            (campaign_dir / "physical.json").write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.campaign_provenance.v1",
                        "session_id": session_id,
                        "analysis_manifest_id": "physical-manifest",
                        "first_physical_run_id": first_run_id,
                        "members": [
                            {
                                "run_id": "config",
                                "bundle_ids": [first_run_id, second_run_id],
                                "execution": "invoked",
                                # Compatibility summary must not fan out over
                                # the physical rows below.
                                "preceding_campaign_cooldown": first_cooldown,
                                "physical_members": [
                                    {
                                        "bundle_id": first_run_id,
                                        "preceding_campaign_cooldown": first_cooldown,
                                    },
                                    {
                                        "bundle_id": second_run_id,
                                        "preceding_campaign_cooldown": second_cooldown,
                                    },
                                ],
                            }
                        ],
                        "cooldown_gates": [second_cooldown],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            cooldowns = _campaign_cooldown_evidence(
                runs, "physical-manifest"
            )

            self.assertEqual(cooldowns[first_run_id]["result"], "first_run_exempt")
            self.assertTrue(cooldowns[first_run_id]["verified"])
            self.assertEqual(cooldowns[second_run_id]["result"], "recovered")
            self.assertTrue(cooldowns[second_run_id]["verified"])
            self.assertEqual(cooldowns[second_run_id]["raw_artifact"], descriptor)
            for bundle_id in (first_run_id, second_run_id):
                evidence = BundleEvidence(
                    entry={},
                    bundle_id=bundle_id,
                    relative_path=bundle_id,
                    path=runs / bundle_id,
                    summary={
                        "window_evidence_precheck": {
                            "gross_request": {"eligible": True, "reasons": []}
                        },
                        "measurement_quality": {"cooldown_cap_hit": False},
                    },
                    metadata={},
                    raw_config={},
                    strict_problems=(),
                    base_reason_codes=(),
                    config_sha256=None,
                    summary_sha256=None,
                    replacement_classification="registered",
                    inclusion_status="included",
                    campaign_cooldown=cooldowns[bundle_id],
                )
                precheck = window_evidence_precheck(
                    evidence,
                    {"name": "gross_energy_j", "metric_tag": "gross_request"},
                )
                self.assertNotIn(
                    "campaign_cooldown_evidence_missing", precheck["reasons"]
                )

    def test_real_cap_hit_campaign_records_defeat_summary_only_reading(self):
        """Audit P0.4: the four real cap-hit members carry
        ``measurement_quality.cooldown_cap_hit=null`` in their summaries, so
        summary-only extraction would treat them as clean n.  The verified
        campaign-log join must mark each one ``cooldown_cap_hit``."""

        from tests.test_floor_extraction import (
            AUDIT_CAP_HIT_TABLE,
            install_real_cap_hit_manifest,
        )

        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp)
            for bundle_id in AUDIT_CAP_HIT_TABLE:
                install_real_cap_hit_manifest(runs, bundle_id)
            cooldowns = campaign_cooldown_evidence(runs)
            for bundle_id in AUDIT_CAP_HIT_TABLE:
                evidence = BundleEvidence(
                    entry={},
                    bundle_id=bundle_id,
                    relative_path=bundle_id,
                    path=runs / bundle_id,
                    summary={
                        "window_evidence_precheck": {
                            "gross_request": {"eligible": True, "reasons": []}
                        },
                        # The stored summary fact for all four members.
                        "measurement_quality": {"cooldown_cap_hit": None},
                    },
                    metadata={},
                    raw_config={},
                    strict_problems=(),
                    base_reason_codes=(),
                    config_sha256=None,
                    summary_sha256=None,
                    replacement_classification="registered",
                    inclusion_status="included",
                    campaign_cooldown=cooldowns[bundle_id],
                )
                precheck = window_evidence_precheck(
                    evidence,
                    {"name": "gross_energy_j", "metric_tag": "gross_request"},
                )
                self.assertFalse(precheck["eligible"])
                self.assertIn("cooldown_cap_hit", precheck["reasons"])
                self.assertNotIn(
                    "campaign_cooldown_evidence_missing", precheck["reasons"]
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
        contrast = artifact["contrasts"][0]
        self.assertEqual(contrast["estimator"]["n"], 0)
        self.assertIsNone(contrast["estimator"]["SE_metrology"])
        self.assertEqual(
            contrast["claim_evaluation"]["outcome"],
            "not_estimable",
        )
        self.assertIn(
            MOCK_TELEMETRY_CLAIM_REFUSAL,
            contrast["claim_evaluation"]["reason_codes"],
        )

    def test_private_stochastic_seam_changes_recorded_policy_identity_with_production_telemetry_identity(
        self,
    ):
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

        with mock.patch(
            "joulewise.analysis_engine.inputs.custody_telemetry_identity",
            return_value=PRODUCTION_TELEMETRY_IDENTITY,
        ):
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

    def _exercise_cli_distinct_calibration_binding(
        self,
        *,
        production_identity: bool,
    ):
        scenario_suffix = "-production" if production_identity else ""
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        condition_ids = sorted(
            {
                entry["condition_id"]
                for entry in manifest["entries"]
                if entry["role"] == "condition"
            }
        )
        # Calibration and consumer bundles share only the immutable runs root;
        # every calibration run ID below is distinct from every manifest
        # consumer run ID.
        calibration_root = self.root / (
            f"independent-consumer-and-calibration-runs{scenario_suffix}"
        )
        shutil.copytree(self.runs_root, calibration_root)
        floor_dir = self.root / f"independent-floor{scenario_suffix}"
        floor_dir.mkdir(exist_ok=True)
        calibration_plan_path = floor_dir / "calibration_plan.json"
        calibration_plan_path.write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.detection_floor_calibration_plan.v1",
                    "plan_id": "floor-exact-cli-plan",
                    "condition_family_ids": condition_ids,
                    "comparative_member_labels": ["A", "B", "B", "A"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        calibration_plan_sha256 = hashlib.sha256(
            calibration_plan_path.read_bytes()
        ).hexdigest()
        cells = []
        groups = []
        order_rows = []
        campaign_rows = []
        all_bound_hashes = []
        for condition_id in condition_ids:
            entries = sorted(
                (
                    entry
                    for entry in manifest["entries"]
                    if entry["condition_id"] == condition_id
                ),
                key=lambda entry: entry["planned_rep_index"],
            )
            source_config = json.loads(
                (self.config_dir / entries[0]["config"]).read_text(encoding="utf-8")
            )
            calibration_ids = []
            with mock.patch(
                "joulewise.bundle._capture_source_state",
                return_value=dict(CLEAN_SOURCE_STATE),
            ):
                for index in range(25):
                    run_id = f"cal-{condition_id}-{index:02d}"
                    calibration_config = json.loads(json.dumps(source_config))
                    calibration_config["run_id"] = run_id
                    tags = calibration_config["run_metadata"]["tags"]
                    tags.append(
                        f"calibration-plan-sha256={calibration_plan_sha256}"
                    )
                    if index >= 5:
                        block_index = (index - 5) // 4
                        sequence_index = (index - 5) % 4
                        labels = ("A", "B", "B", "A")
                        tags.extend(
                            (
                                f"calibration-abba-block-id=floor-{condition_id}-b{block_index}",
                                f"calibration-abba-label={labels[sequence_index]}",
                                f"calibration-abba-sequence-index={sequence_index + 1}",
                            )
                        )
                    config_path = floor_dir / f"{run_id}.json"
                    config_path.write_text(
                        json.dumps(calibration_config, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        code = main(
                            ["run", str(config_path), "--runs-dir", str(calibration_root)]
                        )
                    self.assertEqual(code, 0)
                    calibration_ids.append(run_id)
                    order_rows.append(
                        {"index": len(order_rows) + 1, "config": config_path.name, "run_id": run_id}
                    )
                    campaign_rows.append(
                        {"run_index": len(campaign_rows) + 1, "run_id": run_id}
                    )

            def calibration_record(run_id):
                bundle = calibration_root / run_id
                summary = json.loads((bundle / "summary_metrics.json").read_text(encoding="utf-8"))
                bundle_hash = complete_bundle_sha256(bundle)
                all_bound_hashes.append(bundle_hash)
                return {
                    "bundle_id": run_id,
                    "bundle_sha256": bundle_hash,
                    "config_sha256": hashlib.sha256((bundle / "config.json").read_bytes()).hexdigest(),
                    "metric_value_j": summary["gross_energy_j"],
                }

            observations = [calibration_record(run_id) for run_id in calibration_ids[:5]]
            drift_allowance = whole_window_allowance(
                value=5e-324,
                observed=0.0,
                derived=5e-324,
            )
            absolute = build_absolute_record(
                absolute_false_effect_floor(
                    [row["metric_value_j"] for row in observations]
                ),
                observations,
                whole_window_drift_allowance=drift_allowance,
            )
            blocks = []
            for block_index in range(5):
                ids = calibration_ids[5 + block_index * 4 : 9 + block_index * 4]
                member_records = [calibration_record(run_id) for run_id in ids]
                positioned = [
                    {"position": position, **record}
                    for position, record in zip(
                        ("A1", "B1", "B2", "A2"), member_records, strict=True
                    )
                ]
                delta = abba_delta(
                    positioned[0]["metric_value_j"],
                    positioned[1]["metric_value_j"],
                    positioned[2]["metric_value_j"],
                    positioned[3]["metric_value_j"],
                )
                blocks.append(
                    {
                        "block_id": f"floor-{condition_id}-b{block_index}",
                        "executed_labels": ["A", "B", "B", "A"],
                        "members": positioned,
                        "delta_j": delta,
                    }
                )
            comparative = build_comparative_record(
                comparative_false_effect_floor([block["delta_j"] for block in blocks]),
                blocks,
                whole_window_drift_allowance=drift_allowance,
            )
            cell = make_cell(cell_id=f"floor-{condition_id}", condition=condition_id)
            first_bundle = calibration_root / calibration_ids[0]
            stack = floor_stack_identity(
                json.loads((first_bundle / "config.json").read_text(encoding="utf-8")),
                json.loads((first_bundle / "metadata.json").read_text(encoding="utf-8")),
            )
            self.assertIsNotNone(stack)
            cell["key"].update(backend="mock", metric="gross_energy_j", window_class="request")
            cell["absolute"] = absolute
            cell["comparative"] = comparative
            cell["floor_abs_j"] = absolute["guarded_floor_j"]
            cell["floor_cmp_j"] = comparative["guarded_floor_j"]
            cell["floor_gate_j"] = max(cell["floor_abs_j"], cell["floor_cmp_j"])
            cell["source_regime"]["stack_identity"] = stack
            cell["source_regime"]["stack_identity_sha256"] = canonical_domain_sha256(
                STACK_IDENTITY_DOMAIN, stack
            )
            cell["transport_group_id"] = f"tg-{condition_id}"
            cell["provenance"]["bundle_ids"] = [row["bundle_id"] for row in observations]
            cell["provenance"]["bundle_sha256s"] = [row["bundle_sha256"] for row in observations]
            cells.append(cell)
            groups.append(
                build_transport_group(
                    transport_group_id=f"tg-{condition_id}",
                    backend="mock",
                    metric="gross_energy_j",
                    window_class="request",
                    stack_identity=stack,
                    source_cells=[cell],
                    allowed_consumer_condition_families=[
                        {
                            key: cell["key"][key]
                            for key in (
                                "condition_family_id",
                                "condition_family_definition",
                                "condition_family_sha256",
                            )
                        }
                    ],
                )
            )
        order_path = floor_dir / "order_manifest.json"
        order_path.write_text(
            json.dumps(
                {"schema_version": "joulewise.order_manifest.v1", "executed_order": order_rows},
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        campaign_path = calibration_root / "campaign_log.jsonl"
        whole_window_lines = [
            line
            for line in campaign_path.read_text(encoding="utf-8").splitlines()
            if json.loads(line).get("record_type")
            == "idle_admission_whole_window_verdict"
        ]
        campaign_path.write_text(
            "".join(line + "\n" for line in whole_window_lines)
            + "".join(
                json.dumps(row, sort_keys=True) + "\n" for row in campaign_rows
            ),
            encoding="utf-8",
        )
        provenance = make_artifact()["provenance"]
        provenance["calibration_plan"] = {
            "plan_id": "floor-exact-cli-plan",
            "sha256": calibration_plan_sha256,
        }
        provenance["order_manifest"]["sha256"] = hashlib.sha256(order_path.read_bytes()).hexdigest()
        provenance["campaign_log"]["sha256"] = hashlib.sha256(campaign_path.read_bytes()).hexdigest()
        exact_floor = build_floor_artifact(
            artifact_id="floor-exact-cli",
            calibration_scope="window_a",
            provenance=provenance,
            cells=cells,
            transport_groups=groups,
            idle_drift_guard={
                "calibration_status": "calibrated",
                "method": "p2_015_prediction_guard_v1",
                "guard_w": 0.25,
                "n_bundles": 2,
                "bundle_sha256": all_bound_hashes[:2],
                "cell_id": cells[0]["cell_id"],
                "artifact_sha256": "3" * 64,
            },
        )
        self.assertEqual(validate_floor_artifact(exact_floor), [])
        floor_path = floor_dir / "floor-exact-cli.json"
        floor_path.write_text(json.dumps(exact_floor, indent=2) + "\n", encoding="utf-8")
        output = self.root / f"exact-cli-claim-verdicts{scenario_suffix}.json"
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as stderr:
            code = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(calibration_root),
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
        if production_identity:
            self.assertTrue(
                all(
                    contrast["floor"]["status"] == "resolved"
                    for contrast in gross
                ),
            )
            self.assertTrue(
                all(
                    resolution["status"] == "exact"
                    for contrast in gross
                    for resolution in contrast["floor"]["resolutions"]
                )
            )
            self.assertTrue(
                all(
                    contrast["loo"]["status"] == "complete"
                    for contrast in gross
                )
            )
            self.assertTrue(
                all(len(contrast["loo"]["rows"]) == 5 for contrast in gross)
            )
        else:
            self.assertTrue(
                all(
                    contrast["floor"]["status"] == "refused"
                    and all(
                        "artifact_schema_invalid" in resolution["reason_codes"]
                        for resolution in contrast["floor"]["resolutions"]
                    )
                    for contrast in gross
                )
            )
            self.assertTrue(
                all(
                    contrast["loo"] == {"status": "not_run", "rows": []}
                    and MOCK_TELEMETRY_CLAIM_REFUSAL
                    in contrast["claim_evaluation"]["reason_codes"]
                    for contrast in gross
                )
            )

        def refresh_first_cell(candidate):
            changed_cell = candidate["cells"][0]
            changed_blocks = changed_cell["comparative"]["blocks"]
            for changed_block in changed_blocks:
                members = changed_block["members"]
                changed_block["delta_j"] = abba_delta(
                    members[0]["metric_value_j"],
                    members[1]["metric_value_j"],
                    members[2]["metric_value_j"],
                    members[3]["metric_value_j"],
                )
            changed_cell["comparative"] = build_comparative_record(
                comparative_false_effect_floor(
                    [block["delta_j"] for block in changed_blocks]
                ),
                changed_blocks,
                whole_window_drift_allowance=changed_cell["comparative"][
                    "whole_window_drift_allowance"
                ],
            )
            changed_cell["floor_cmp_j"] = changed_cell["comparative"]["guarded_floor_j"]
            changed_cell["floor_gate_j"] = max(
                changed_cell["floor_abs_j"], changed_cell["floor_cmp_j"]
            )
            candidate["transport_groups"][0] = build_transport_group(
                transport_group_id=changed_cell["transport_group_id"],
                backend="mock",
                metric="gross_energy_j",
                window_class="request",
                stack_identity=changed_cell["source_regime"]["stack_identity"],
                source_cells=[changed_cell],
                allowed_consumer_condition_families=[
                    {
                        key: changed_cell["key"][key]
                        for key in (
                            "condition_family_id",
                            "condition_family_definition",
                            "condition_family_sha256",
                        )
                    }
                ],
            )

        def binding_for(candidate, name):
            candidate_path = floor_dir / name
            candidate_path.write_text(
                json.dumps(candidate, indent=2) + "\n", encoding="utf-8"
            )
            return load_analysis_inputs(
                self.manifest_path,
                calibration_root,
                candidate_path,
                strict_validator=validate_bundle,
            ).floor_binding

        relabeled = json.loads(json.dumps(exact_floor))
        relabeled_members = relabeled["cells"][0]["comparative"]["blocks"][0]["members"]
        payload_keys = (
            "bundle_id",
            "bundle_sha256",
            "config_sha256",
            "metric_value_j",
        )
        for key in payload_keys:
            relabeled_members[0][key], relabeled_members[1][key] = (
                relabeled_members[1][key],
                relabeled_members[0][key],
            )
        refresh_first_cell(relabeled)
        relabeled_binding = binding_for(relabeled, "floor-relabeled-abba.json")
        self.assertTrue(
            any(
                "calibration_abba_label_mismatch" in problem
                for problem in relabeled_binding.problems_by_cell[relabeled["cells"][0]["cell_id"]]
            )
        )
        self.assertNotIn(
            relabeled["cells"][0]["cell_id"], relabeled_binding.bound_cell_ids
        )
        self.assertIn(
            "calibration_abba_label_mismatch",
            floor_binding_reason_codes(relabeled_binding),
        )
        relabeled_result = analyze_claims(
            self.manifest_path,
            calibration_root,
            floor_dir / "floor-relabeled-abba.json",
            strict_validator=validate_bundle,
        )
        self.assertTrue(
            any(
                "calibration_abba_label_mismatch" in resolution["reason_codes"]
                for contrast in relabeled_result["contrasts"]
                for resolution in contrast["floor"]["resolutions"]
            )
        )

        reordered = json.loads(json.dumps(exact_floor))
        reordered_members = reordered["cells"][0]["comparative"]["blocks"][0]["members"]
        for key in payload_keys:
            reordered_members[1][key], reordered_members[2][key] = (
                reordered_members[2][key],
                reordered_members[1][key],
            )
        refresh_first_cell(reordered)
        reordered_binding = binding_for(reordered, "floor-reordered-members.json")
        self.assertTrue(
            any(
                "calibration_abba_member_order_mismatch" in problem
                for problem in reordered_binding.problems_by_cell[reordered["cells"][0]["cell_id"]]
            )
        )
        self.assertNotIn(
            reordered["cells"][0]["cell_id"], reordered_binding.bound_cell_ids
        )
        self.assertIn(
            "calibration_abba_member_order_mismatch",
            floor_binding_reason_codes(reordered_binding),
        )

        plan_bytes = calibration_plan_path.read_bytes()
        try:
            calibration_plan_path.write_bytes(plan_bytes + b" ")
            plan_binding = binding_for(exact_floor, "floor-tampered-plan.json")
        finally:
            calibration_plan_path.write_bytes(plan_bytes)
        self.assertIn(
            "calibration_plan_bytes_hash_mismatch", plan_binding.global_problems
        )
        self.assertFalse(plan_binding.bound_cell_ids)
        self.assertIn(
            "calibration_plan_bytes_hash_mismatch",
            floor_binding_reason_codes(plan_binding),
        )

        guard_tampered = json.loads(json.dumps(exact_floor))
        guard_tampered["idle_drift_guard"]["bundle_sha256"] = all_bound_hashes[25:27]
        guard_binding = binding_for(guard_tampered, "floor-tampered-guard.json")
        self.assertIn(
            "idle_drift_guard_provenance_mismatch", guard_binding.global_problems
        )
        self.assertFalse(guard_binding.bound_cell_ids)
        self.assertIn(
            "idle_drift_guard_provenance_mismatch",
            floor_binding_reason_codes(guard_binding),
        )

        fabricated = json.loads(json.dumps(exact_floor))
        fabricated_cell = fabricated["cells"][0]
        fake_observations = fabricated_cell["absolute"]["bundle_observations"]
        for observation in fake_observations:
            observation["metric_value_j"] += 1.0
        fabricated_cell["absolute"] = build_absolute_record(
            absolute_false_effect_floor(
                [observation["metric_value_j"] for observation in fake_observations]
            ),
            fake_observations,
            whole_window_drift_allowance=fabricated_cell["absolute"][
                "whole_window_drift_allowance"
            ],
        )
        fabricated_cell["floor_abs_j"] = fabricated_cell["absolute"]["guarded_floor_j"]
        fabricated_cell["floor_gate_j"] = max(
            fabricated_cell["floor_abs_j"], fabricated_cell["floor_cmp_j"]
        )
        fabricated["transport_groups"][0] = build_transport_group(
            transport_group_id=fabricated_cell["transport_group_id"],
            backend="mock",
            metric="gross_energy_j",
            window_class="request",
            stack_identity=fabricated_cell["source_regime"]["stack_identity"],
            source_cells=[fabricated_cell],
            allowed_consumer_condition_families=[
                {
                    key: fabricated_cell["key"][key]
                    for key in (
                        "condition_family_id",
                        "condition_family_definition",
                        "condition_family_sha256",
                    )
                }
            ],
        )
        fabricated_path = floor_dir / "floor-fabricated-metrics.json"
        fabricated_path.write_text(
            json.dumps(fabricated, indent=2) + "\n", encoding="utf-8"
        )
        fabricated_output = self.root / (
            f"fabricated-floor-claim-verdicts{scenario_suffix}.json"
        )
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as stderr:
            code = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(calibration_root),
                    "--floor-artifact",
                    str(fabricated_path),
                    "--output",
                    str(fabricated_output),
                ]
            )
        self.assertEqual(code, 0, stderr.getvalue())
        refused = json.loads(fabricated_output.read_text(encoding="utf-8"))
        affected_condition = fabricated_cell["key"]["condition_family_id"]
        affected = [
            resolution
            for contrast in refused["contrasts"]
            for resolution in contrast["floor"]["resolutions"]
            if resolution["source_cell_ids"] == []
            or affected_condition
            in {
                contrast["conditions"]["condition_a_id"],
                contrast["conditions"]["condition_b_id"],
            }
        ]
        self.assertTrue(affected)
        self.assertTrue(
            any(
                row["status"] == "refused"
                and "artifact_schema_invalid" in row["reason_codes"]
                for row in affected
            )
        )

    def test_cli_binds_distinct_calibration_bundles_and_preserves_mock_refusal(self):
        self._exercise_cli_distinct_calibration_binding(
            production_identity=False,
        )

    def test_cli_binds_distinct_calibration_bundles_and_preserves_mock_refusal_with_production_telemetry_identity(
        self,
    ):
        with (
            mock.patch(
                "joulewise.analysis_engine.inputs.custody_telemetry_identity",
                return_value=PRODUCTION_TELEMETRY_IDENTITY,
            ),
            mock.patch(
                "joulewise.analysis_engine.inputs.anchor_fallback_member_unusable",
                return_value=False,
            ),
        ):
            self._exercise_cli_distinct_calibration_binding(
                production_identity=True,
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
        install_passing_analysis_whole_window(
            runs,
            [
                replacement["run_id"]
                if entry["entry_id"] == target["entry_id"]
                else entry["run_id"]
                for entry in manifest["entries"]
            ],
            source_name="replacement-whole-window-source",
        )
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertEqual(artifact["sampling_audit"]["valid_replacements"], [])
        self.assertTrue(artifact["sampling_audit"]["top_up_detected"])
        self.assertEqual(
            len(artifact["sampling_audit"]["demoted_contrast_ids"]),
            12,
        )
        replacement_audit = next(
            row
            for row in artifact["bundle_audit"]
            if row["bundle_id"] == replacement["run_id"]
        )
        self.assertEqual(
            replacement_audit["replacement_classification"],
            "replacement_candidate",
        )
        self.assertEqual(replacement_audit["inclusion_status"], "excluded")
        self.assertIn(
            MOCK_TELEMETRY_CLAIM_REFUSAL,
            replacement_audit["base_reason_codes"],
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
        self.assertTrue(affected)
        self.assertTrue(all(contrast["estimator"]["n"] == 0 for contrast in affected))
        self.assertTrue(
            all(
                MOCK_TELEMETRY_CLAIM_REFUSAL
                in contrast["claim_evaluation"]["reason_codes"]
                for contrast in affected
            )
        )

    def test_valid_replacement_fills_original_slot_without_sixth_block_with_production_telemetry_identity(
        self,
    ):
        runs = self.root / "replacement-production-runs"
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
        replacement["run_id"] = target["run_id"] + "-production-replacement"
        replacement["run_metadata"]["tags"].extend(
            [
                f"analysis-replacement-of={target['entry_id']}",
                "analysis-replacement-reason=bundle_incomplete",
            ]
        )
        config_path = self.root / "replacement-production-config.json"
        config_path.write_text(
            json.dumps(replacement, indent=2) + "\n", encoding="utf-8"
        )
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(
                main(["run", str(config_path), "--runs-dir", str(runs)]),
                0,
            )
        install_passing_analysis_whole_window(
            runs,
            [
                replacement["run_id"]
                if entry["entry_id"] == target["entry_id"]
                else entry["run_id"]
                for entry in manifest["entries"]
            ],
            source_name="replacement-production-whole-window-source",
        )
        with mock.patch(
            "joulewise.analysis_engine.inputs.custody_telemetry_identity",
            return_value=PRODUCTION_TELEMETRY_IDENTITY,
        ):
            artifact = analyze_claims(
                self.manifest_path,
                runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )
        self.assertEqual(
            len(artifact["sampling_audit"]["valid_replacements"]),
            1,
        )
        self.assertFalse(artifact["sampling_audit"]["top_up_detected"])
        self.assertEqual(
            artifact["sampling_audit"]["demoted_contrast_ids"],
            [],
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
        self.assertTrue(affected)
        self.assertTrue(
            all(contrast["estimator"]["n"] == 5 for contrast in affected)
        )

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
                self.assertEqual(contrast["estimator"]["n"], 0)
                self.assertIsNone(contrast["estimator"]["df"])
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
                self.assertIn(
                    MOCK_TELEMETRY_CLAIM_REFUSAL,
                    contrast["claim_evaluation"]["reason_codes"],
                )
                self.assertEqual(
                    contrast["claim_evaluation"]["outcome"],
                    "not_estimable",
                )

    def test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity(
        self,
    ):
        runs = self.root / "incomplete-production-runs"
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
        with mock.patch(
            "joulewise.analysis_engine.inputs.custody_telemetry_identity",
            return_value=PRODUCTION_TELEMETRY_IDENTITY,
        ):
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

    def test_cleanup_suspect_is_excluded_even_with_stale_broad_runner_waiver(self):
        from joulewise import reduce as reduce_module

        runs = self.root / "cleanup-suspect-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition" and entry["planned_rep_index"] == 1
        )
        bundle = runs / target["run_id"]
        events_path = bundle / "events.jsonl"
        events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
        cleanup = next(
            event
            for event in events
            if event["event_type"] == "stage_completed" and event["phase"] == "cleanup"
        )
        cleanup["metadata"]["cleanup_ok"] = False
        events_path.write_text(
            "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
            encoding="utf-8",
        )
        metadata_path = bundle / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata.setdefault("extra", {})["node_cleanup"] = [
            {"path": "/remote/tmp/joulewise-task", "removed": False}
        ]
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        summary = reduce_module.reduce_bundle(bundle)
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.assertEqual(validate_bundle(bundle, strict=True), [])

        unwaived = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        unwaived_audit = next(
            row for row in unwaived["bundle_audit"] if row["entry_id"] == target["entry_id"]
        )
        unwaived_inputs = load_analysis_inputs(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        unwaived_evidence = unwaived_inputs.registered[target["entry_id"]]
        self.assertEqual(
            unwaived_evidence.claim_evidence_flags,
            ("runtime_cleanup_ok", "remote_cleanup_failed"),
        )
        self.assertIsNone(unwaived_evidence.waiver)
        self.assertEqual(unwaived_audit["inclusion_status"], "excluded")
        self.assertIn("required_error_term_unknown", unwaived_audit["base_reason_codes"])
        affected = [
            contrast
            for contrast in unwaived["contrasts"]
            if target["cell_id"]
            in {
                contrast["conditions"]["cell_a_id"],
                contrast["conditions"]["cell_b_id"],
            }
        ]
        self.assertTrue(affected)
        self.assertTrue(
            all(
                "required_error_term_unknown"
                in contrast["claim_evaluation"]["reason_codes"]
                for contrast in affected
            )
        )

        campaign_dir = runs / "campaign_manifests"
        campaign_dir.mkdir(parents=True, exist_ok=True)
        waiver = {
            "target_kind": "bundle_id",
            "target": target["run_id"],
            "reason": "cleanup residue reviewed and bounded",
            "approver": "campaign-owner",
            "timestamp": "2026-07-11T00:00:00Z",
            "scope": "any",
        }
        (campaign_dir / "cleanup-waiver.json").write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.campaign_provenance.v1",
                    "session_id": "cleanup-waiver-fixture",
                    "created_at": "2026-07-11T00:00:00Z",
                    "config_dir": str(self.config_dir),
                    "analysis_manifest_id": manifest["manifest_id"],
                    "first_physical_run_id": None,
                    "members": [
                        {
                            "config": target["config"],
                            "run_id": target["run_id"],
                            "bundle_ids": [target["run_id"]],
                            "execution": "existing",
                            "preceding_campaign_cooldown": None,
                            "claim_evidence": [
                                {
                                    "bundle_id": target["run_id"],
                                    "claim_evidence_flags": [
                                        "runtime_cleanup_ok",
                                    ],
                                    "waiver": waiver,
                                }
                            ],
                        }
                    ],
                    "cooldown_gates": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        waived = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        waived_audit = next(
            row for row in waived["bundle_audit"] if row["entry_id"] == target["entry_id"]
        )
        waived_inputs = load_analysis_inputs(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        waived_evidence = waived_inputs.registered[target["entry_id"]]
        self.assertEqual(waived_audit["inclusion_status"], "excluded")
        self.assertIn("required_error_term_unknown", waived_audit["base_reason_codes"])
        self.assertIsNone(waived_evidence.waiver)

    def test_malformed_campaign_claim_evidence_refuses_with_analysis_input_error(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = manifest["entries"][0]
        malformed_values = (
            ("claim_evidence_flags", [["runtime_cleanup_ok"]]),
            ("bundle_id", [target["run_id"]]),
        )
        for field, value in malformed_values:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                runs = Path(tmp) / "runs"
                shutil.copytree(self.runs_root, runs)
                campaign_dir = runs / "campaign_manifests"
                campaign_dir.mkdir(parents=True, exist_ok=True)
                evidence = {
                    "bundle_id": target["run_id"],
                    "claim_evidence_flags": ["runtime_cleanup_ok"],
                    "waiver": None,
                }
                evidence[field] = value
                (campaign_dir / "malformed.json").write_text(
                    json.dumps(
                        {
                            "schema_version": "joulewise.campaign_provenance.v1",
                            "analysis_manifest_id": manifest["manifest_id"],
                            "members": [
                                {
                                    "config": target["config"],
                                    "run_id": target["run_id"],
                                    "bundle_ids": [target["run_id"]],
                                    "claim_evidence": [evidence],
                                }
                            ],
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )

                with self.assertRaisesRegex(
                    AnalysisInputError, "malformed campaign claim evidence"
                ):
                    load_analysis_inputs(
                        self.manifest_path,
                        runs,
                        self.floor_path,
                        strict_validator=validate_bundle,
                    )

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
            self.assertEqual(contrast["estimator"]["n"], 0)
            self.assertIn(
                "outcome_dependent_top_up",
                contrast["claim_evaluation"]["reason_codes"],
            )
            self.assertIn(
                MOCK_TELEMETRY_CLAIM_REFUSAL,
                contrast["claim_evaluation"]["reason_codes"],
            )
            self.assertEqual(
                contrast["claim_evaluation"]["outcome"],
                "not_estimable",
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

    def test_unregistered_matching_topup_demotes_but_preserves_fixed_n_analysis_with_production_telemetry_identity(
        self,
    ):
        runs = self.root / "topup-production-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        topup = json.loads(
            (self.config_dir / target["config"]).read_text(encoding="utf-8")
        )
        topup["run_id"] = target["run_id"] + "-production-topup"
        topup["run_metadata"]["tags"] = [
            "rep6" if tag == "rep1" else tag
            for tag in topup["run_metadata"]["tags"]
        ]
        config_path = self.root / "topup-production-config.json"
        config_path.write_text(
            json.dumps(topup, indent=2) + "\n", encoding="utf-8"
        )
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(
                main(["run", str(config_path), "--runs-dir", str(runs)]),
                0,
            )
        with mock.patch(
            "joulewise.analysis_engine.inputs.custody_telemetry_identity",
            return_value=PRODUCTION_TELEMETRY_IDENTITY,
        ):
            artifact = analyze_claims(
                self.manifest_path,
                runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )
        self.assertTrue(artifact["sampling_audit"]["top_up_detected"])
        self.assertEqual(
            len(artifact["sampling_audit"]["demoted_contrast_ids"]),
            12,
        )
        demoted = [
            contrast
            for contrast in artifact["contrasts"]
            if contrast["sampling"]["confirmatory_status"]
            == "demoted_exploratory"
        ]
        self.assertEqual(len(demoted), 12)
        for contrast in demoted:
            self.assertEqual(contrast["estimator"]["n"], 5)
            self.assertIn(
                "outcome_dependent_top_up",
                contrast["claim_evaluation"]["reason_codes"],
            )
            self.assertFalse(
                contrast["claim_evaluation"]["claim_ready_for_l2_l3"]
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
