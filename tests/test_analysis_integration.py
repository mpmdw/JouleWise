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
    FloorRequest,
    MOCK_TELEMETRY_CLAIM_REFUSAL,
    _campaign_cooldown_evidence,
    bind_floor_artifact_evidence,
    campaign_cooldown_evidence,
    declared_evidence_roots,
    floor_binding_reason_codes,
    floor_request_for_evidence,
    floor_stack_identity,
    load_analysis_inputs,
    realized_scientific_identity,
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
    ATTRIBUTION_FLOOR_SOURCE,
    ATTRIBUTION_LIMIT_CLASS,
    abba_delta,
    absolute_false_effect_floor,
    attribution_single_count_discipline,
    build_absolute_record,
    build_comparative_record,
    build_floor_artifact,
    build_floor_cell,
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
    make_regime,
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


def install_explicit_mock_sampler(bundle: Path) -> None:
    metadata_path = bundle / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["workload_provenance"]["sampler"] = {
        "api": "mock_runtime.generate",
        "kind": "deterministic_mock",
        "pinned": True,
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
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
                        "run_id": reference_ids[0],
                        "bundle_ids": [reference_ids[0]],
                        "role": "neg8_daily_reference_start",
                        "sentinel_position": "start",
                    },
                    {
                        "execution": "invoked",
                        "run_id": f"{source_name}-campaign-members",
                        "bundle_ids": bundle_ids,
                    },
                    {
                        "execution": "invoked",
                        "run_id": reference_ids[1],
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
                run_id = json.loads(config.read_text(encoding="utf-8"))["run_id"]
                install_explicit_mock_sampler(cls.runs_root / run_id)
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
                self.assertNotIn("floor_limit_class", contrast["floor"])
                self.assertNotIn("floor_limit", evaluation)
                self.assertTrue(
                    all(
                        "floor_limit_class" not in resolution
                        for resolution in contrast["floor"]["resolutions"]
                    )
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

    def test_attribution_limited_floor_is_claim_bearing_in_final_artifact(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = manifest["contrasts"][0]
        selector = target["floor_selector"]
        condition_ids = selector["condition_family_ids"]
        cells = [
            make_cell(
                cell_id=f"attribution-{condition_id}",
                condition=condition_id,
                energies=[0.0] * 5,
                deltas=[0.0] * 5,
                absolute_half_widths=[0.5] * 5,
                comparative_half_widths=[0.5] * 5,
            )
            for condition_id in condition_ids
        ]
        for cell in cells:
            cell["key"].update(
                backend="powermetrics",
                metric=selector["metric"],
                window_class=selector["window_class"],
            )
            cell["transport_group_id"] = "tg-analysis-attribution"
        group = build_transport_group(
            transport_group_id="tg-analysis-attribution",
            backend="powermetrics",
            metric=selector["metric"],
            window_class=selector["window_class"],
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
        floor_artifact = build_floor_artifact(
            artifact_id="analysis-attribution-floor",
            calibration_scope="window_a",
            source_class="synthetic",
            provenance=make_artifact()["provenance"],
            cells=cells,
            transport_groups=[group],
            idle_drift_guard={
                "calibration_status": "calibrated",
                "method": "p2_015_prediction_guard_v1",
                "guard_w": 0.25,
                "n_bundles": 2,
                "bundle_sha256": ["1" * 64, "2" * 64],
                "cell_id": cells[0]["cell_id"],
                "artifact_sha256": "3" * 64,
            },
        )
        self.assertEqual(validate_floor_artifact(floor_artifact), [])
        cells_by_condition = {
            cell["key"]["condition_family_id"]: cell for cell in cells
        }

        def labelled_floor_request(
            contrast, condition_id, rows, artifact
        ):
            del rows, artifact
            if contrast["contrast_id"] != target["contrast_id"]:
                return None
            cell = cells_by_condition[condition_id]
            return FloorRequest(
                backend=cell["key"]["backend"],
                metric=cell["key"]["metric"],
                window_class=cell["key"]["window_class"],
                condition_family_id=condition_id,
                condition_family_sha256=cell["key"][
                    "condition_family_sha256"
                ],
                stack_identity_sha256=cell["source_regime"][
                    "stack_identity_sha256"
                ],
                consumer_stress={},
            )

        with tempfile.TemporaryDirectory() as tmp:
            floor_path = Path(tmp) / "attribution-floor.json"
            floor_path.write_text(
                json.dumps(floor_artifact, indent=2) + "\n",
                encoding="utf-8",
            )
            artifact = analyze_claims(
                self.manifest_path,
                self.runs_root,
                floor_path,
                strict_validator=validate_bundle,
                _floor_request_factory=labelled_floor_request,
            )

        observed = next(
            contrast
            for contrast in artifact["contrasts"]
            if contrast["contrast_id"] == target["contrast_id"]
        )
        floor = observed["floor"]
        self.assertEqual(floor["status"], "resolved")
        self.assertEqual(
            floor["floor_limit_class"],
            ATTRIBUTION_LIMIT_CLASS,
        )
        self.assertEqual(floor["floor_source"], ATTRIBUTION_FLOOR_SOURCE)
        self.assertEqual(
            floor["single_count_discipline"],
            attribution_single_count_discipline(),
        )
        self.assertEqual(
            set(floor["point_floor_diagnostics"]),
            {cell["cell_id"] for cell in cells},
        )
        for resolution, cell in zip(
            floor["resolutions"], cells, strict=True
        ):
            self.assertEqual(resolution["status"], "exact")
            self.assertEqual(
                resolution["floor_gate_j"],
                cell["floor_gate_j"],
            )
            self.assertEqual(
                resolution["floor_limit_class"],
                ATTRIBUTION_LIMIT_CLASS,
            )
        expected_floor = max(cell["floor_gate_j"] for cell in cells)
        self.assertEqual(floor["active_floor_j"], expected_floor)
        evaluation = observed["claim_evaluation"]
        self.assertNotIn(
            "floor_transport_inapplicable",
            evaluation["reason_codes"],
        )
        self.assertEqual(
            evaluation["floor_limit"],
            {
                "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
                "floor_source": ATTRIBUTION_FLOOR_SOURCE,
                "published_floor_j": expected_floor,
                "point_floor_diagnostics": floor[
                    "point_floor_diagnostics"
                ],
                "single_count_discipline": (
                    attribution_single_count_discipline()
                ),
            },
        )
        self.assertEqual(validate_claim_verdicts(artifact), [])
        missing_single_count = json.loads(json.dumps(artifact))
        del missing_single_count["contrasts"][
            artifact["contrasts"].index(observed)
        ]["claim_evaluation"]["floor_limit"]["single_count_discipline"]
        missing_single_count["claim_verdicts_id"] = (
            calculate_claim_verdicts_id(missing_single_count)
        )
        self.assertTrue(
            any(
                "single_count_discipline" in error
                for error in validate_claim_verdicts(missing_single_count)
            )
        )

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
            source_class="synthetic",
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
        analysis_root = self.root / (
            f"independent-analysis-corpus{scenario_suffix}"
        )
        shutil.copytree(self.runs_root, analysis_root)
        evidence_roots = {
            "a10": self.root / f"independent-a10-evidence{scenario_suffix}",
            "window_c": (
                self.root / f"independent-window-c-evidence{scenario_suffix}"
            ),
        }
        for evidence_root in evidence_roots.values():
            evidence_root.mkdir()
        floor_dir = self.root / f"independent-floor{scenario_suffix}"
        floor_dir.mkdir(exist_ok=True)
        calibration_plan_path = floor_dir / "calibration_plan.json"
        calibration_plan_path.write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.detection_floor_calibration_plan.v1",
                    "plan_id": "floor-exact-cli-plan",
                    "calibration_scope": "window_a",
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
        order_rows = {"a10": [], "window_c": []}
        campaign_rows = {"a10": [], "window_c": []}
        calibration_roots_by_id = {}
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
                    root_id = "a10" if index < 5 else "window_c"
                    evidence_root = evidence_roots[root_id]
                    calibration_roots_by_id[run_id] = evidence_root
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
                            [
                                "run",
                                str(config_path),
                                "--runs-dir",
                                str(evidence_root),
                            ]
                        )
                    self.assertEqual(code, 0)
                    install_explicit_mock_sampler(evidence_root / run_id)
                    calibration_ids.append(run_id)
                    order_rows[root_id].append(
                        {
                            "index": len(order_rows[root_id]) + 1,
                            "config": config_path.name,
                            "run_id": run_id,
                        }
                    )
                    campaign_rows[root_id].append(
                        {
                            "run_index": len(campaign_rows[root_id]) + 1,
                            "run_id": run_id,
                        }
                    )

            def calibration_record(run_id):
                bundle = calibration_roots_by_id[run_id] / run_id
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
                    [row["metric_value_j"] for row in observations],
                    admissible_half_widths_j=[0.0] * len(observations),
                ),
                observations,
                consumption_semantics_id="d078_minted_envelopes_v1",
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
                comparative_false_effect_floor(
                    [block["delta_j"] for block in blocks],
                    admissible_half_widths_j=[0.0] * len(blocks),
                ),
                blocks,
                consumption_semantics_id="d078_minted_envelopes_v1",
                whole_window_drift_allowance=drift_allowance,
            )
            first_bundle = calibration_roots_by_id[
                calibration_ids[0]
            ] / calibration_ids[0]
            stack = floor_stack_identity(
                json.loads((first_bundle / "config.json").read_text(encoding="utf-8")),
                json.loads((first_bundle / "metadata.json").read_text(encoding="utf-8")),
            )
            self.assertIsNotNone(stack)
            component_regime = make_regime(stack_identity=stack)
            cell = build_floor_cell(
                cell_id=f"floor-{condition_id}",
                key={
                    "backend": "mock",
                    "metric": "gross_energy_j",
                    "window_class": "request",
                    **condition_family(condition_id),
                },
                eligibility={
                    "use_role": "primary_claim_gate",
                    "minimum_claim_n": 5,
                    "status": "claim_ready",
                    "claim_usable": True,
                    "reason_codes": [],
                },
                absolute=absolute,
                comparative=comparative,
                transport_group_id=f"tg-{condition_id}",
                provenance={
                    "absolute": {
                        "calibration_cell_id": f"floor-{condition_id}-abs",
                        "evidence_root_id": "a10",
                        "order_manifest": {
                            "manifest_id": "floor-exact-a10-order",
                            "sha256": "0" * 64,
                        },
                        "campaign_log": {"sha256": "0" * 64},
                        "extraction_report": {"sha256": "0" * 64},
                        "extraction_spec": {"sha256": "0" * 64},
                        "bundle_ids": [
                            observation["bundle_id"]
                            for observation in observations
                        ],
                        "bundle_sha256s": [
                            observation["bundle_sha256"]
                            for observation in observations
                        ],
                        "source_regime": component_regime,
                    },
                    "comparative": {
                        "calibration_cell_id": f"floor-{condition_id}-cmp",
                        "evidence_root_id": "window_c",
                        "order_manifest": {
                            "manifest_id": "floor-exact-window-c-order",
                            "sha256": "0" * 64,
                        },
                        "campaign_log": {"sha256": "0" * 64},
                        "extraction_report": {"sha256": "0" * 64},
                        "extraction_spec": {"sha256": "0" * 64},
                        "bundle_ids": [
                            member["bundle_id"]
                            for block in blocks
                            for member in block["members"]
                        ],
                        "bundle_sha256s": [
                            member["bundle_sha256"]
                            for block in blocks
                            for member in block["members"]
                        ],
                        "source_regime": component_regime,
                    },
                },
            )
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
        root_descriptor_hashes = {}
        for root_id, evidence_root in evidence_roots.items():
            order_path = evidence_root / "order_manifest.json"
            order_path.write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.order_manifest.v1",
                        "manifest_id": f"floor-exact-{root_id.replace('_', '-')}-order",
                        "executed_order": order_rows[root_id],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            campaign_path = evidence_root / "campaign_log.jsonl"
            campaign_path.write_text(
                "".join(
                    json.dumps(row, sort_keys=True) + "\n"
                    for row in campaign_rows[root_id]
                ),
                encoding="utf-8",
            )
            root_descriptor_hashes[root_id] = {
                "order_manifest": hashlib.sha256(
                    order_path.read_bytes()
                ).hexdigest(),
                "campaign_log": hashlib.sha256(
                    campaign_path.read_bytes()
                ).hexdigest(),
            }
        extraction_spec_path = floor_dir / "extraction_spec.json"
        extraction_spec_path.write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.floor_extraction_spec.fixture.v1",
                    "condition_family_ids": condition_ids,
                    "absolute_n": 5,
                    "comparative_n_blocks": 5,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        extraction_report_path = floor_dir / "extraction_report.json"
        extraction_report_path.write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.floor_extraction_report.fixture.v1",
                    "cell_ids": [cell["cell_id"] for cell in cells],
                    "bundle_ids": [
                        bundle_id
                        for cell in cells
                        for component in ("absolute", "comparative")
                        for bundle_id in cell["provenance"][component]["bundle_ids"]
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        common_descriptor_hashes = {
            "extraction_report": hashlib.sha256(
                extraction_report_path.read_bytes()
            ).hexdigest(),
            "extraction_spec": hashlib.sha256(
                extraction_spec_path.read_bytes()
            ).hexdigest(),
        }
        for cell in cells:
            for component in ("absolute", "comparative"):
                component_provenance = cell["provenance"][component]
                root_id = component_provenance["evidence_root_id"]
                descriptor_hashes = {
                    **root_descriptor_hashes[root_id],
                    **common_descriptor_hashes,
                }
                for descriptor_name, descriptor_sha256 in descriptor_hashes.items():
                    component_provenance[descriptor_name][
                        "sha256"
                    ] = descriptor_sha256
        provenance = make_artifact()["provenance"]
        provenance["calibration_plan"] = {
            "plan_id": "floor-exact-cli-plan",
            "declared_calibration_scope": "window_a",
            "relative_path": "calibration_plan.json",
            "sha256": calibration_plan_sha256,
        }
        exact_floor = build_floor_artifact(
            artifact_id="floor-exact-cli",
            calibration_scope="window_a",
            source_class="synthetic",
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
        bare_root_binding = bind_floor_artifact_evidence(
            exact_floor,
            floor_path,
            analysis_root,
            strict_validator=validate_bundle,
        )
        self.assertIn(
            "evidence_root_mapping_required",
            bare_root_binding.global_problems,
        )
        self.assertIn(
            "evidence_root_mapping_required",
            floor_binding_reason_codes(bare_root_binding),
        )
        self.assertFalse(bare_root_binding.bound_cell_ids)
        bare_loaded = load_analysis_inputs(
            self.manifest_path,
            analysis_root,
            floor_path,
            strict_validator=validate_bundle,
        )
        self.assertIn(
            "evidence_root_mapping_required",
            floor_binding_reason_codes(bare_loaded.floor_binding),
        )

        missing_root_binding = bind_floor_artifact_evidence(
            exact_floor,
            floor_path,
            {"a10": evidence_roots["a10"]},
            strict_validator=validate_bundle,
        )
        self.assertIn(
            "missing_evidence_root_mapping: 'window_c'",
            missing_root_binding.global_problems,
        )
        self.assertFalse(missing_root_binding.bound_cell_ids)

        surplus_root_binding = bind_floor_artifact_evidence(
            exact_floor,
            floor_path,
            {**evidence_roots, "unexpected": analysis_root},
            strict_validator=validate_bundle,
        )
        self.assertFalse(
            any(
                problem.startswith("unknown_evidence_root_mapping:")
                for problem in surplus_root_binding.global_problems
            ),
            surplus_root_binding.global_problems,
        )
        self.assertNotIn(
            "unknown_evidence_root_mapping",
            floor_binding_reason_codes(surplus_root_binding),
        )
        self.assertEqual(
            surplus_root_binding.bound_cell_ids,
            (
                frozenset(
                    cell["cell_id"] for cell in exact_floor["cells"]
                )
                if production_identity
                else frozenset()
            ),
        )

        wrong_root = floor_dir / "wrong-evidence-root"
        wrong_root.mkdir()
        wrong_root_binding = bind_floor_artifact_evidence(
            exact_floor,
            floor_path,
            {
                "a10": wrong_root,
                "window_c": evidence_roots["window_c"],
            },
            strict_validator=validate_bundle,
        )
        self.assertTrue(
            any(
                problem.startswith("component_evidence_root_disagreement:")
                for problem in wrong_root_binding.global_problems
            )
        )
        self.assertFalse(wrong_root_binding.bound_cell_ids)

        leaked_path_artifact = json.loads(json.dumps(exact_floor))
        leaked_path_artifact["provenance"]["calibration_plan"][
            "relative_path"
        ] = str(calibration_plan_path.resolve())
        leaked_path_binding = bind_floor_artifact_evidence(
            leaked_path_artifact,
            floor_path,
            evidence_roots,
            strict_validator=validate_bundle,
        )
        self.assertTrue(
            any(
                problem.startswith("artifact_absolute_path_leakage:")
                for problem in leaked_path_binding.global_problems
            )
        )
        self.assertFalse(leaked_path_binding.bound_cell_ids)

        loaded = load_analysis_inputs(
            self.manifest_path,
            analysis_root,
            floor_path,
            strict_validator=validate_bundle,
            evidence_roots=evidence_roots,
        )
        self.assertFalse(
            {
                "evidence_root_mapping_required",
                "missing_evidence_root_mapping",
                "unknown_evidence_root_mapping",
            }
            & set(floor_binding_reason_codes(loaded.floor_binding))
        )
        if production_identity:
            self.assertFalse(loaded.floor_binding.global_problems)
            self.assertEqual(
                loaded.floor_binding.bound_cell_ids,
                frozenset(cell["cell_id"] for cell in exact_floor["cells"]),
            )
        self.assertEqual(len(loaded.registered), 30)
        self.assertFalse(
            any(
                evidence.bundle_id.startswith("cal-")
                for evidence in (
                    *loaded.registered.values(),
                    *loaded.extra_audits,
                )
            )
        )
        missing_loaded = load_analysis_inputs(
            self.manifest_path,
            analysis_root,
            floor_path,
            strict_validator=validate_bundle,
            evidence_roots={"a10": evidence_roots["a10"]},
        )
        self.assertIn(
            "missing_evidence_root_mapping: 'window_c'",
            missing_loaded.floor_binding.global_problems,
        )

        output = self.root / f"exact-cli-claim-verdicts{scenario_suffix}.json"
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as stderr:
            code = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(analysis_root),
                    "--evidence-root",
                    f"a10={evidence_roots['a10']}",
                    "--evidence-root",
                    f"window_c={evidence_roots['window_c']}",
                    "--floor-artifact",
                    str(floor_path),
                    "--output",
                    str(output),
                ]
            )
        self.assertEqual(code, 0, stderr.getvalue())
        artifact = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(len(artifact["bundle_audit"]), 30)
        self.assertFalse(
            any(
                row["bundle_id"].startswith("cal-")
                for row in artifact["bundle_audit"]
            )
        )
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
                    [block["delta_j"] for block in changed_blocks],
                    admissible_half_widths_j=[0.0] * len(changed_blocks),
                ),
                changed_blocks,
                consumption_semantics_id=changed_cell["comparative"][
                    "consumption_semantics_id"
                ],
                whole_window_drift_allowance=changed_cell["comparative"][
                    "whole_window_drift_allowance"
                ],
            )
            comparative_provenance = changed_cell["provenance"]["comparative"]
            comparative_provenance["bundle_ids"] = [
                member["bundle_id"]
                for block in changed_blocks
                for member in block["members"]
            ]
            comparative_provenance["bundle_sha256s"] = [
                member["bundle_sha256"]
                for block in changed_blocks
                for member in block["members"]
            ]
            changed_cell["floor_cmp_j"] = changed_cell["comparative"][
                "drift_widened_guarded_floor_j"
            ]
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
                analysis_root,
                candidate_path,
                strict_validator=validate_bundle,
                evidence_roots=evidence_roots,
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
            analysis_root,
            floor_dir / "floor-relabeled-abba.json",
            strict_validator=validate_bundle,
            evidence_roots=evidence_roots,
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
                [observation["metric_value_j"] for observation in fake_observations],
                admissible_half_widths_j=[0.0] * len(fake_observations),
            ),
            fake_observations,
            consumption_semantics_id=fabricated_cell["absolute"][
                "consumption_semantics_id"
            ],
            whole_window_drift_allowance=fabricated_cell["absolute"][
                "whole_window_drift_allowance"
            ],
        )
        fabricated_cell["floor_abs_j"] = fabricated_cell["absolute"][
            "drift_widened_guarded_floor_j"
        ]
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
                    str(analysis_root),
                    "--evidence-root",
                    f"a10={evidence_roots['a10']}",
                    "--evidence-root",
                    f"window_c={evidence_roots['window_c']}",
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

    def test_cli_evidence_root_parser_rejects_malformed_and_duplicate_ids(self):
        base = [
            "analyze-claims",
            "--analysis-manifest",
            str(self.manifest_path),
            "--runs-root",
            str(self.runs_root),
            "--floor-artifact",
            str(self.floor_path),
            "--output",
            str(self.root / "parser-must-not-run.json"),
        ]
        cases = (
            (["--evidence-root", "a10"], "expected ID=PATH"),
            (["--evidence-root", f"={self.runs_root}"], "ID must be nonempty"),
            (["--evidence-root", "a10="], "PATH must be nonempty"),
            (
                [
                    "--evidence-root",
                    f"a10={self.runs_root}",
                    "--evidence-root",
                    f"a10={self.runs_root}",
                ],
                "duplicate evidence-root ID",
            ),
        )
        for evidence_args, expected in cases:
            with self.subTest(evidence_args=evidence_args):
                stderr = io.StringIO()
                with (
                    redirect_stderr(stderr),
                    self.assertRaises(SystemExit) as raised,
                ):
                    main([*base, *evidence_args])
                self.assertEqual(raised.exception.code, 2)
                self.assertIn(expected, stderr.getvalue())

    def test_claim_output_cannot_be_written_under_floor_evidence_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence_root = Path(tmp)
            with self.assertRaisesRegex(
                AnalysisInputError,
                "output must be outside floor evidence roots",
            ):
                analyze_claims(
                    self.manifest_path,
                    self.runs_root,
                    self.floor_path,
                    strict_validator=validate_bundle,
                    evidence_roots={"a10": evidence_root},
                    output_path=evidence_root / "claim-verdicts.json",
                )

    def test_declared_evidence_roots_filters_valid_artifacts_and_fails_closed_on_read(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            supplied = {
                "a10": root / "a10",
                "window_c": root / "window-c",
                "unexpected": root / "unexpected",
            }
            self.assertEqual(
                declared_evidence_roots(self.floor_path, supplied),
                {
                    "a10": supplied["a10"],
                    "window_c": supplied["window_c"],
                },
            )
            self.assertIsNone(declared_evidence_roots(self.floor_path, None))

            missing = root / "missing.json"
            self.assertIs(declared_evidence_roots(missing, supplied), supplied)

            with mock.patch.object(
                Path,
                "read_bytes",
                side_effect=PermissionError("fixture unreadable"),
            ):
                self.assertIs(
                    declared_evidence_roots(self.floor_path, supplied),
                    supplied,
                )

            invalid_utf8 = root / "invalid-utf8.json"
            invalid_utf8.write_bytes(b"\xff")
            self.assertIs(
                declared_evidence_roots(invalid_utf8, supplied),
                supplied,
            )

            invalid_json = root / "invalid-json.json"
            invalid_json.write_text("{\n", encoding="utf-8")
            self.assertIs(
                declared_evidence_roots(invalid_json, supplied),
                supplied,
            )

            unusable = root / "unusable.json"
            unusable.write_text("[]\n", encoding="utf-8")
            self.assertIs(
                declared_evidence_roots(unusable, supplied),
                supplied,
            )

    def test_claim_output_separation_preserves_declared_root_and_ignores_surplus_symlink(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            declared_roots = {
                "a10": root / "a10",
                "window_c": root / "window-c",
            }
            for declared_root in declared_roots.values():
                declared_root.mkdir()

            exact_output = root / "exact-claim-verdicts.json"
            analyze_claims(
                self.manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
                evidence_roots=declared_roots,
                output_path=exact_output,
            )
            self.assertTrue(exact_output.is_file())

            declared_target = root / "declared-target"
            declared_target.mkdir()
            declared_symlink = root / "declared-symlink"
            declared_symlink.symlink_to(declared_target, target_is_directory=True)
            with self.assertRaisesRegex(
                AnalysisInputError,
                "path_resolution_refused: symlink input",
            ):
                analyze_claims(
                    self.manifest_path,
                    self.runs_root,
                    self.floor_path,
                    strict_validator=validate_bundle,
                    evidence_roots={
                        **declared_roots,
                        "a10": declared_symlink,
                    },
                    output_path=root / "declared-symlink-must-not-write.json",
                )

            surplus_target = root / "surplus-target"
            surplus_target.mkdir()
            surplus_symlink = root / "surplus-symlink"
            surplus_symlink.symlink_to(surplus_target, target_is_directory=True)
            surplus_output = root / "surplus-symlink-claim-verdicts.json"
            analyze_claims(
                self.manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
                evidence_roots={
                    **declared_roots,
                    "unexpected": surplus_symlink,
                },
                output_path=surplus_output,
            )
            self.assertTrue(surplus_output.is_file())

    def test_cli_output_separation_preserves_exact_and_absent_mapping_and_ignores_surplus_containment(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            declared_roots = {
                "a10": root / "a10",
                "window_c": root / "window-c",
            }
            for declared_root in declared_roots.values():
                declared_root.mkdir()
            evidence_args = [
                "--evidence-root",
                f"a10={declared_roots['a10']}",
                "--evidence-root",
                f"window_c={declared_roots['window_c']}",
            ]
            base = [
                "analyze-claims",
                "--analysis-manifest",
                str(self.manifest_path),
                "--runs-root",
                str(self.runs_root),
                "--floor-artifact",
                str(self.floor_path),
            ]

            exact_output = root / "exact-cli-claim-verdicts.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                exact_code = main(
                    [*base, *evidence_args, "--output", str(exact_output)]
                )
            self.assertEqual(exact_code, 0)
            self.assertTrue(exact_output.is_file())

            absent_output = root / "absent-cli-claim-verdicts.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                absent_code = main([*base, "--output", str(absent_output)])
            self.assertEqual(absent_code, 0)
            self.assertTrue(absent_output.is_file())

            declared_output = declared_roots["a10"] / "must-not-write.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                declared_code = main(
                    [*base, *evidence_args, "--output", str(declared_output)]
                )
            self.assertEqual(declared_code, 2)
            self.assertFalse(declared_output.exists())

            absent_refused_output = self.runs_root / "must-not-write-without-roots.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                absent_refused_code = main(
                    [*base, "--output", str(absent_refused_output)]
                )
            self.assertEqual(absent_refused_code, 2)
            self.assertFalse(absent_refused_output.exists())

            surplus_root = root / "surplus"
            surplus_root.mkdir()
            surplus_output = surplus_root / "claim-verdicts.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                surplus_code = main(
                    [
                        *base,
                        *evidence_args,
                        "--evidence-root",
                        f"unexpected={surplus_root}",
                        "--output",
                        str(surplus_output),
                    ]
                )
            self.assertEqual(surplus_code, 0)
            self.assertTrue(surplus_output.is_file())

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

    def test_realized_identity_accepts_directory_shaped_model_artifact(self):
        fixture = Path("tests/fixtures/d078_r01")
        raw_config = json.loads(
            (fixture / "config.json").read_text(encoding="utf-8")
        )
        metadata = json.loads(
            (fixture / "metadata.json").read_text(encoding="utf-8")
        )
        artifact = metadata["workload_provenance"]["model"][
            "artifact_identity"
        ]
        self.assertEqual(artifact["kind"], "file_set")
        self.assertNotIn("sha256", artifact)

        identity = realized_scientific_identity(raw_config, metadata)

        self.assertIsNotNone(identity)
        self.assertEqual(
            identity["model_artifact"]["sha256"],
            artifact["folded_sha256"],
        )

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


class SupersessionAwareCooldownJoinTests(unittest.TestCase):
    """Declaration-first cooldown-join and supersession regressions."""

    @staticmethod
    def _manifest(
        tmp: Path,
        name: str,
        session: str,
        bundle_id: str,
        *,
        analysis_manifest_id: str | None = None,
        cooldown: object | None = None,
        execution: str = "invoked",
        outcome: str | None = None,
        schema_version: str = "joulewise.campaign_provenance.v1",
    ) -> Path:
        campaign_dir = tmp / "campaign_manifests"
        campaign_dir.mkdir(parents=True, exist_ok=True)
        if cooldown is None:
            cooldown = {
                "result": "first_run_exempt",
                "session_id": session,
                "following_run_id": bundle_id,
            }
        manifest = {
            "schema_version": schema_version,
            "analysis_manifest_id": analysis_manifest_id,
            "session_id": session,
            "first_physical_run_id": bundle_id,
            "members": [
                {
                    "config": f"{bundle_id}.json",
                    "execution": execution,
                    "run_id": bundle_id,
                    "bundle_ids": [bundle_id],
                    "preceding_campaign_cooldown": (
                        cooldown if execution == "invoked" else None
                    ),
                }
            ],
        }
        if outcome is not None:
            manifest["members"][0]["outcome"] = outcome
        path = campaign_dir / name
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def _install_legacy_existing_binding(
        self,
        root: Path,
        manifest_name: str,
        *,
        outcome: str = "usable",
    ) -> dict:
        manifest_path = root / "campaign_manifests" / manifest_name
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        member = manifest["members"][0]
        status = {
            "usable": "skipped",
            "failed": "failed",
            "incomplete": "incomplete_existing",
            "waived": "waived",
        }[outcome]
        classification = (
            outcome if outcome in {"usable", "failed", "waived"} else "usable"
        )
        member_rows = []
        for bundle_id in member["bundle_ids"]:
            row = {
                "bundle_id": bundle_id,
                "status": "succeeded" if classification == "usable" else "failed",
                "strict_valid": classification == "usable",
                "collection_integrity_flags": (
                    [] if classification == "usable" else ["fixture_failure"]
                ),
                "collection_classification": classification,
            }
            if classification == "waived":
                row["waiver"] = {"scope": "fixture_failure"}
            member_rows.append(row)
        log_row = {
            "status": status,
            "run_id": member["run_id"],
            "config": str(root / "configs" / member["config"]),
            "campaign_provenance_manifest": str(manifest_path.resolve()),
            "members": member_rows,
        }
        log_path = root / "campaign_log.jsonl"
        prior = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        log_path.write_text(
            prior + json.dumps(log_row, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return log_row

    def _install_real_supersession(
        self,
        root: Path,
        bundle_id: str,
        *,
        selected_manifest: str | tuple[str, int],
        superseded_manifests: list[str | tuple[str, int]],
    ) -> dict:
        from joulewise.whole_window import (
            OCCURRENCE_SUPERSESSION_SCHEMA,
            supersession_entry_sha256,
        )

        canonical = root / bundle_id
        canonical.mkdir()
        quarantine = Path(tempfile.mkdtemp(prefix="d5j-quarantine-"))
        self.addCleanup(shutil.rmtree, quarantine, ignore_errors=True)
        custody_hashes = {}
        for name, payload in (
            ("config.json", {"run_id": bundle_id}),
            ("metadata.json", {"status": "failed"}),
            ("summary_metrics.json", {"status": "failed"}),
        ):
            raw = (json.dumps(payload, sort_keys=True) + "\n").encode()
            (canonical / name).write_bytes(raw)
            (quarantine / name).write_bytes(raw)
            custody_hashes[name] = hashlib.sha256(raw).hexdigest()

        def occurrence(manifest_ref: str | tuple[str, int]) -> dict:
            manifest_name, bundle_index = (
                (manifest_ref, 0)
                if isinstance(manifest_ref, str)
                else manifest_ref
            )
            path = root / "campaign_manifests" / manifest_name
            return {
                "bundle_id": bundle_id,
                "source_manifest": {
                    "path": f"campaign_manifests/{manifest_name}",
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                },
                "member_index": 0,
                "bundle_index": bundle_index,
            }

        entry = {
            "schema_version": OCCURRENCE_SUPERSESSION_SCHEMA,
            "record_type": "campaign_occurrence_supersession",
            "runs_root": str(root.resolve()),
            "bundle_id": bundle_id,
            "reason": "failed occurrence quarantined before retry",
            "selected_occurrence": occurrence(selected_manifest),
            "superseded_occurrences": [
                occurrence(name) for name in superseded_manifests
            ],
            "quarantine": {
                "path": str(quarantine.resolve()),
                "config_sha256": custody_hashes["config.json"],
                "metadata_sha256": custody_hashes["metadata.json"],
                "summary_sha256": custody_hashes["summary_metrics.json"],
            },
        }
        entry["entry_sha256"] = supersession_entry_sha256(entry)
        log_path = root / "campaign_log.jsonl"
        prior = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        log_path.write_text(
            prior + json.dumps(entry, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return entry

    def _duplicated_root(self) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="fix9-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self._manifest(tmp, "campaign-a.json", "session-a", "dup-bundle")
        self._manifest(tmp, "campaign-b.json", "session-b", "dup-bundle")
        return tmp

    def _physical_manifest_root(self, members: list[dict]) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="fix10-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        campaign_dir = tmp / "campaign_manifests"
        campaign_dir.mkdir(parents=True)
        manifest = {
            "schema_version": "joulewise.campaign_provenance.v1",
            "analysis_manifest_id": None,
            "session_id": "physical-session",
            "first_physical_run_id": "dup-bundle",
            "members": members,
        }
        (campaign_dir / "physical.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        return tmp

    @staticmethod
    def _physical_member(
        bundle_ids: list[str], physical_members: list[dict]
    ) -> dict:
        return {
            "execution": "invoked",
            "run_id": "dup-bundle",
            "bundle_ids": bundle_ids,
            "physical_members": physical_members,
        }

    @staticmethod
    def _first_exempt_cooldown() -> dict:
        return {
            "result": "first_run_exempt",
            "session_id": "physical-session",
            "following_run_id": "dup-bundle",
        }

    def test_duplicate_without_supersession_still_refuses(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        resolved = _campaign_cooldown_evidence(self._duplicated_root(), None)
        row = resolved["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])
        self.assertIsNone(row["manifest"])

    def test_d097_v2_invoked_then_existing_refuses_for_every_outcome(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        for outcome in ("usable", "failed", "incomplete", "waived"):
            with self.subTest(outcome=outcome):
                root = Path(tempfile.mkdtemp(prefix=f"gauntlet-v2-i-e-{outcome}-"))
                self.addCleanup(shutil.rmtree, root, ignore_errors=True)
                self._manifest(
                    root,
                    "00-invoked.json",
                    "invoked-session",
                    "bundle",
                    schema_version="joulewise.campaign_provenance.v2",
                )
                self._manifest(
                    root,
                    "01-existing.json",
                    "existing-session",
                    "bundle",
                    execution="existing",
                    outcome=outcome,
                    schema_version="joulewise.campaign_provenance.v2",
                )

                # D-097: v2 is deferred until writer-minted discrimination exists.
                self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_v1_existing_outcome_cannot_bypass_missing_log_binding(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-b1-v1-outcome-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(root, "00-invoked.json", "invoked-session", "bundle")
        self._manifest(
            root,
            "01-existing.json",
            "existing-session",
            "bundle",
            execution="existing",
            outcome="usable",
        )

        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_d097_relabelled_v1_outcome_manifest_refuses_at_catalog_gate(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-b1-relabel-probe-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(root, "00-invoked.json", "invoked-session", "bundle")
        existing_path = self._manifest(
            root,
            "01-existing.json",
            "existing-session",
            "bundle",
            execution="existing",
        )
        self._install_legacy_existing_binding(root, "01-existing.json")

        relabelled = json.loads(existing_path.read_text(encoding="utf-8"))
        relabelled["schema_version"] = "joulewise.campaign_provenance.v2"
        relabelled["members"][0]["outcome"] = "usable"
        existing_path.write_text(json.dumps(relabelled), encoding="utf-8")
        (root / "campaign_log.jsonl").unlink()

        # D-097 release condition 2: a label-only v2 must fail at catalog intake.
        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_d097_bare_v2_existing_refuses_at_catalog_gate(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-v2-e-only-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(
            root,
            "00-existing.json",
            "existing-session",
            "bundle",
            execution="existing",
            outcome="usable",
            schema_version="joulewise.campaign_provenance.v2",
        )

        # D-097: v2 is uniformly malformed before commit 3's writer exists.
        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_d097_v2_failed_existing_then_retry_refuses_at_catalog_gate(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-v2-e-i-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(
            root,
            "00-existing.json",
            "existing-session",
            "bundle",
            execution="existing",
            outcome="failed",
            schema_version="joulewise.campaign_provenance.v2",
        )
        self._manifest(
            root,
            "01-existing.json",
            "second-existing-session",
            "bundle",
            execution="existing",
            outcome="failed",
            schema_version="joulewise.campaign_provenance.v2",
        )
        self._manifest(
            root,
            "02-invoked.json",
            "invoked-session",
            "bundle",
            schema_version="joulewise.campaign_provenance.v2",
        )

        # D-097: no v2 truth-table shape is consumable in the interim state.
        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_d097_v2_superseded_retry_still_refuses_at_catalog_gate(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import (
            validate_occurrence_supersession_entry,
            validated_supersession_entries,
        )

        root = Path(tempfile.mkdtemp(prefix="gauntlet-v2-e-i-repair-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(
            root,
            "00-existing.json",
            "existing-session",
            "bundle",
            execution="existing",
            outcome="failed",
            schema_version="joulewise.campaign_provenance.v2",
        )
        self._manifest(
            root,
            "01-existing.json",
            "second-existing-session",
            "bundle",
            execution="existing",
            outcome="failed",
            schema_version="joulewise.campaign_provenance.v2",
        )
        self._manifest(
            root,
            "02-invoked.json",
            "invoked-session",
            "bundle",
            schema_version="joulewise.campaign_provenance.v2",
        )
        entry = self._install_real_supersession(
            root,
            "bundle",
            selected_manifest="02-invoked.json",
            superseded_manifests=["00-existing.json"],
        )

        self.assertTrue(validate_occurrence_supersession_entry(entry, root))
        self.assertEqual(validated_supersession_entries(root), [entry])
        # D-097: a valid supersession cannot license a deferred v2 manifest.
        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_legacy_existing_aliases_bind_every_closed_log_outcome(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        for outcome in ("usable", "failed", "incomplete", "waived"):
            with self.subTest(outcome=outcome):
                root = Path(tempfile.mkdtemp(prefix=f"gauntlet-v1-{outcome}-"))
                self.addCleanup(shutil.rmtree, root, ignore_errors=True)
                self._manifest(
                    root, "00-invoked.json", "invoked-session", "bundle"
                )
                self._manifest(
                    root,
                    "01-existing.json",
                    "existing-session",
                    "bundle",
                    execution="existing",
                )
                self._install_legacy_existing_binding(
                    root, "01-existing.json", outcome=outcome
                )

                row = _campaign_cooldown_evidence(root, None)["bundle"]

                self.assertEqual(row["result"], "first_run_exempt")
                self.assertTrue(row["verified"])
                self.assertEqual(
                    row["manifest"], "campaign_manifests/00-invoked.json"
                )

    def test_one_legacy_log_row_cannot_authenticate_two_existing_members(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-b2-log-reuse-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        manifest_path = self._manifest(
            root, "physical.json", "physical-session", "bundle"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        existing = {
            **manifest["members"][0],
            "execution": "existing",
            "preceding_campaign_cooldown": None,
        }
        manifest["members"].extend([existing, dict(existing)])
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self._install_legacy_existing_binding(root, "physical.json")

        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_legacy_existing_binding_failures_refuse_join_globally(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        for case in (
            "missing",
            "inconsistent",
            "conflicting",
            "ambiguous",
            "unparseable",
        ):
            with self.subTest(case=case):
                root = Path(tempfile.mkdtemp(prefix=f"gauntlet-v1-{case}-"))
                self.addCleanup(shutil.rmtree, root, ignore_errors=True)
                self._manifest(
                    root,
                    "00-existing.json",
                    "existing-session",
                    "bundle",
                    execution="existing",
                )
                self._manifest(root, "01-invoked.json", "invoked-session", "bundle")
                if case != "missing":
                    row = self._install_legacy_existing_binding(
                        root, "00-existing.json"
                    )
                    log_path = root / "campaign_log.jsonl"
                    if case in {"inconsistent", "conflicting"}:
                        original = json.loads(json.dumps(row))
                        row["members"][0]["bundle_id"] = "other-bundle"
                        log_path.write_text(
                            (
                                json.dumps(original, sort_keys=True) + "\n"
                                if case == "conflicting"
                                else ""
                            )
                            + json.dumps(row, sort_keys=True)
                            + "\n",
                            encoding="utf-8",
                        )
                    elif case == "ambiguous":
                        log_path.write_text(
                            log_path.read_text(encoding="utf-8")
                            + json.dumps(row, sort_keys=True)
                            + "\n",
                            encoding="utf-8",
                        )
                    elif case == "unparseable":
                        log_path.write_text(
                            log_path.read_text(encoding="utf-8") + "{not-json\n",
                            encoding="utf-8",
                        )

                self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_unknown_prospective_existing_outcome_refuses_join_globally(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-v2-unknown-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(
            root,
            "00-existing.json",
            "existing-session",
            "bundle",
            execution="existing",
            outcome="surprising",
            schema_version="joulewise.campaign_provenance.v2",
        )
        self._manifest(
            root,
            "01-invoked.json",
            "invoked-session",
            "bundle",
            schema_version="joulewise.campaign_provenance.v2",
        )

        # D-097: all v2 outcomes refuse, including values outside the old enum.
        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_result_map_keyset_unions_candidates_and_declared_ids(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        declared_only = "declared-with-zero-emissions"
        root = self._physical_manifest_root(
            [
                self._physical_member(
                    ["dup-bundle", declared_only],
                    [
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": (
                                self._first_exempt_cooldown()
                            ),
                        }
                    ],
                )
            ]
        )

        joined = _campaign_cooldown_evidence(root, None)

        candidate_ids = {"dup-bundle"}
        declared_ids = {"dup-bundle", declared_only}
        self.assertEqual(set(joined), candidate_ids | declared_ids)

    def test_unresolved_declared_id_has_exact_refusal_payload(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = self._physical_manifest_root(
            [self._physical_member(["dup-bundle"], [])]
        )

        self.assertEqual(
            _campaign_cooldown_evidence(root, None),
            {
                "dup-bundle": {
                    "result": "unknown",
                    "verified": False,
                    "session_id": None,
                    "manifest": None,
                    "raw_artifact": None,
                }
            },
        )

    def test_repeated_declared_bundle_with_malformed_physical_row_refuses(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = self._physical_manifest_root(
            [
                self._physical_member(
                    ["dup-bundle", "dup-bundle"],
                    [
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": (
                                self._first_exempt_cooldown()
                            ),
                        },
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": "malformed",
                        },
                    ],
                )
            ]
        )

        row = _campaign_cooldown_evidence(root, None)["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])
        self.assertIsNone(row["manifest"])

    def test_b1_partial_supersession_cannot_launder_malformed_declaration(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import (
            validate_occurrence_supersession_entry,
            validated_supersession_entries,
        )

        root = Path(tempfile.mkdtemp(prefix="d5j-b1-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(root, "campaign-a.json", "session-a", "dup-bundle")
        self._manifest(root, "campaign-b.json", "session-b", "dup-bundle")
        self._manifest(
            root,
            "campaign-c.json",
            "session-c",
            "dup-bundle",
            cooldown="malformed",
        )
        entry = self._install_real_supersession(
            root,
            "dup-bundle",
            selected_manifest="campaign-b.json",
            superseded_manifests=["campaign-a.json"],
        )

        self.assertTrue(validate_occurrence_supersession_entry(entry, root))
        self.assertEqual(validated_supersession_entries(root), [entry])
        row = _campaign_cooldown_evidence(root, None)["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])
        self.assertIsNone(row["manifest"])

    def test_other_catalog_declaration_does_not_create_duplicate(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="d5j-b2-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(
            root,
            "selected.json",
            "selected-session",
            "dup-bundle",
            analysis_manifest_id="selected",
        )
        self._manifest(
            root,
            "filtered-sibling.json",
            "filtered-session",
            "dup-bundle",
            analysis_manifest_id="other",
        )

        row = _campaign_cooldown_evidence(root, "selected")["dup-bundle"]
        self.assertEqual(row["result"], "first_run_exempt")
        self.assertTrue(row["verified"])
        self.assertEqual(row["manifest"], "campaign_manifests/selected.json")

    def test_b2_wrong_schema_duplicate_or_unreadable_catalog_refuses_join(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        for label, sibling in (
            ("unreadable", b"{ this is not json"),
            (
                "wrong-schema",
                json.dumps(
                    {
                        "schema_version": "joulewise.campaign_provenance.v999",
                        "analysis_manifest_id": "selected",
                        "members": [
                            {
                                "execution": "invoked",
                                "run_id": "solo-bundle",
                                "bundle_ids": ["solo-bundle"],
                                "preceding_campaign_cooldown": "malformed",
                            }
                        ],
                    }
                ).encode(),
            ),
        ):
            with self.subTest(label=label):
                root = Path(tempfile.mkdtemp(prefix=f"d5j-catalog-{label}-"))
                self.addCleanup(shutil.rmtree, root, ignore_errors=True)
                self._manifest(
                    root,
                    "selected.json",
                    "selected-session",
                    "solo-bundle",
                    analysis_manifest_id="selected",
                )
                (root / "campaign_manifests" / "sibling.json").write_bytes(sibling)
                self.assertEqual(
                    _campaign_cooldown_evidence(root, "selected"),
                    {},
                )

    def test_nonselected_manifest_with_nonobject_member_refuses_catalog(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-b3-catalog-member-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(
            root,
            "selected.json",
            "selected-session",
            "bundle",
            analysis_manifest_id="selected",
        )
        sibling = {
            "schema_version": "joulewise.campaign_provenance.v1",
            "analysis_manifest_id": "other",
            "members": [None],
        }
        (root / "campaign_manifests" / "sibling.json").write_text(
            json.dumps(sibling), encoding="utf-8"
        )

        self.assertEqual(_campaign_cooldown_evidence(root, "selected"), {})

    def test_cross_member_duplicate_with_malformed_physical_row_refuses(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = self._physical_manifest_root(
            [
                self._physical_member(
                    ["dup-bundle"],
                    [
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": (
                                self._first_exempt_cooldown()
                            ),
                        }
                    ],
                ),
                self._physical_member(
                    ["dup-bundle"],
                    [
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": "malformed",
                        }
                    ],
                ),
            ]
        )

        row = _campaign_cooldown_evidence(root, None)["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])
        self.assertIsNone(row["manifest"])

    def test_repeated_declarations_use_true_positions_for_supersession(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import validated_supersession_entries

        root = self._physical_manifest_root(
            [
                self._physical_member(
                    ["dup-bundle", "dup-bundle"],
                    [
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": (
                                self._first_exempt_cooldown()
                            ),
                        },
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": (
                                self._first_exempt_cooldown()
                            ),
                        },
                    ],
                )
            ]
        )
        entry = self._install_real_supersession(
            root,
            "dup-bundle",
            selected_manifest=("physical.json", 0),
            superseded_manifests=[("physical.json", 1)],
        )

        self.assertEqual(validated_supersession_entries(root), [entry])
        row = _campaign_cooldown_evidence(root, None)["dup-bundle"]
        self.assertEqual(row["result"], "first_run_exempt")
        self.assertTrue(row["verified"])
        self.assertEqual(row["manifest"], "campaign_manifests/physical.json")

    def test_single_declared_occurrence_keeps_physical_and_legacy_resolution(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        physical_root = self._physical_manifest_root(
            [
                self._physical_member(
                    ["dup-bundle"],
                    [
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": (
                                self._first_exempt_cooldown()
                            ),
                        }
                    ],
                )
            ]
        )
        physical = _campaign_cooldown_evidence(physical_root, None)["dup-bundle"]
        self.assertEqual(physical["result"], "first_run_exempt")
        self.assertTrue(physical["verified"])
        self.assertEqual(physical["manifest"], "campaign_manifests/physical.json")

        legacy_root = Path(tempfile.mkdtemp(prefix="fix10-legacy-"))
        self.addCleanup(shutil.rmtree, legacy_root, ignore_errors=True)
        self._manifest(
            legacy_root, "legacy.json", "legacy-session", "single-bundle"
        )
        legacy = _campaign_cooldown_evidence(legacy_root, None)["single-bundle"]
        self.assertEqual(legacy["result"], "first_run_exempt")
        self.assertTrue(legacy["verified"])
        self.assertEqual(legacy["manifest"], "campaign_manifests/legacy.json")

    def test_valid_supersession_resolves_selected_occurrence(self):
        from joulewise.analysis_engine import inputs as inputs_module

        entry = {
            "bundle_id": "dup-bundle",
            "selected_occurrence": {
                "source_manifest": {"path": "campaign_manifests/campaign-b.json"},
                "member_index": 0,
                "bundle_index": 0,
            },
            "superseded_occurrences": [
                {
                    "source_manifest": {
                        "path": "campaign_manifests/campaign-a.json"
                    },
                    "member_index": 0,
                    "bundle_index": 0,
                }
            ],
        }
        with unittest.mock.patch.object(
            inputs_module,
            "supersession_entry_validation_results",
            return_value=([entry], [True]),
        ):
            resolved = inputs_module._campaign_cooldown_evidence(
                self._duplicated_root(), None
            )
        row = resolved["dup-bundle"]
        self.assertEqual(row["manifest"], "campaign_manifests/campaign-b.json")
        self.assertEqual(row["session_id"], "session-b")

    def test_validated_log_supersession_selects_governing_cooldown_row(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import (
            validate_occurrence_supersession_entry,
            validated_supersession_entries,
        )

        root = self._duplicated_root()
        bundle_id = "dup-bundle"
        entry = self._install_real_supersession(
            root,
            bundle_id,
            selected_manifest="campaign-b.json",
            superseded_manifests=["campaign-a.json"],
        )
        self.assertTrue(validate_occurrence_supersession_entry(entry, root))
        self.assertEqual(validated_supersession_entries(root), [entry])

        row = _campaign_cooldown_evidence(root, None)[bundle_id]
        self.assertEqual(row["manifest"], "campaign_manifests/campaign-b.json")
        self.assertEqual(row["session_id"], "session-b")
        self.assertTrue(row["verified"])

    def test_v4_valid_exact_plus_corrupted_same_bundle_clone_refuses(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import (
            supersession_entry_validation_results,
            validated_supersession_entries,
        )

        root = self._duplicated_root()
        entry = self._install_real_supersession(
            root,
            "dup-bundle",
            selected_manifest="campaign-b.json",
            superseded_manifests=["campaign-a.json"],
        )
        corrupted_clone = dict(entry)
        corrupted_clone["entry_sha256"] = "0" * 64
        with (root / "campaign_log.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(corrupted_clone, sort_keys=True) + "\n")

        raw = supersession_entry_validation_results(root)
        self.assertIsNotNone(raw)
        assert raw is not None
        self.assertEqual(raw[0], [entry, corrupted_clone])
        self.assertEqual(raw[1], [True, False])
        self.assertEqual(validated_supersession_entries(root), [entry])
        row = _campaign_cooldown_evidence(root, None)["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])
        self.assertIsNone(row["manifest"])

    def test_invalid_json_supersession_reader_input_refuses_join_globally(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-sup-json-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(root, "campaign.json", "session", "bundle")
        (root / "campaign_log.jsonl").write_text(
            "{unidentifiable-json\n", encoding="utf-8"
        )

        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_unidentifiable_supersession_record_refuses_join_globally(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import OCCURRENCE_SUPERSESSION_SCHEMA

        root = Path(tempfile.mkdtemp(prefix="gauntlet-sup-unidentifiable-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(root, "campaign.json", "session", "bundle")
        (root / "campaign_log.jsonl").write_text(
            json.dumps(
                {
                    "schema_version": OCCURRENCE_SUPERSESSION_SCHEMA,
                    "record_type": "campaign_occurrence_supersession",
                    "reason": "bundle identity was lost",
                }
            )
            + "\n",
            encoding="utf-8",
        )

        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_exact_supersession_cannot_license_emission_subset(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import validated_supersession_entries

        root = Path(tempfile.mkdtemp(prefix="d5j-struck-cell-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(
            root,
            "selected.json",
            "selected-session",
            "dup-bundle",
            analysis_manifest_id="selected",
        )
        self._manifest(
            root,
            "filtered.json",
            "filtered-session",
            "dup-bundle",
            analysis_manifest_id="selected",
            cooldown="malformed",
        )
        entry = self._install_real_supersession(
            root,
            "dup-bundle",
            selected_manifest="selected.json",
            superseded_manifests=["filtered.json"],
        )

        self.assertEqual(validated_supersession_entries(root), [entry])
        row = _campaign_cooldown_evidence(root, "selected")["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])
        self.assertIsNone(row["manifest"])

    def _assert_7b_corpus_shape_resolves(self) -> None:
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import validated_supersession_entries

        root = Path(tempfile.mkdtemp(prefix="d5j-real-shape-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        bundle_ids = [f"member-{index:02d}" for index in range(57)]
        genuine_indices = (44, 45)
        original_names: dict[str, str] = {}
        for index, bundle_id in enumerate(bundle_ids):
            name = f"campaign-{index:02d}-0-invoked.json"
            original_names[bundle_id] = name
            self._manifest(
                root,
                name,
                f"session-{index:02d}",
                bundle_id,
            )
            aliases = 1 if index < 24 else 2 if index < 44 else 0
            for alias_index in range(aliases):
                alias_name = (
                    f"campaign-{index:02d}-{alias_index + 1}-existing.json"
                )
                self._manifest(
                    root,
                    alias_name,
                    f"existing-{index:02d}-{alias_index}",
                    bundle_id,
                    execution="existing",
                )
                self._install_legacy_existing_binding(root, alias_name)

        duplicate_ids = tuple(bundle_ids[index] for index in genuine_indices)
        for retry_index, (member_index, bundle_id) in enumerate(
            zip(genuine_indices, duplicate_ids, strict=True)
        ):
            retry_name = f"campaign-{member_index:02d}-1-invoked.json"
            self._manifest(
                root,
                retry_name,
                f"retry-session-{retry_index}",
                bundle_id,
            )
            if retry_index == 1:
                alias_name = f"campaign-{member_index:02d}-2-existing.json"
                self._manifest(
                    root,
                    alias_name,
                    "retry-existing-session",
                    bundle_id,
                    execution="existing",
                )
                self._install_legacy_existing_binding(root, alias_name)
            self._install_real_supersession(
                root,
                bundle_id,
                selected_manifest=retry_name,
                superseded_manifests=[original_names[bundle_id]],
            )

        self.assertEqual(len(validated_supersession_entries(root)), 2)
        joined = _campaign_cooldown_evidence(root, None)
        self.assertEqual(len(joined), 57)
        self.assertTrue(all(row["verified"] for row in joined.values()))
        for index, bundle_id in enumerate(duplicate_ids):
            self.assertEqual(
                joined[bundle_id]["session_id"], f"retry-session-{index}"
            )

    def _assert_contrast_corpus_shape_resolves(self) -> None:
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import validated_supersession_entries

        root = Path(tempfile.mkdtemp(prefix="d5j-contrast-shape-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        bundle_ids = [f"member-{index:02d}" for index in range(47)]
        target = bundle_ids[23]
        for index, bundle_id in enumerate(bundle_ids):
            self._manifest(
                root,
                f"campaign-{index:02d}-0-invoked.json",
                f"session-{index:02d}",
                bundle_id,
            )
        retries = []
        for retry_index in (1, 2):
            name = f"campaign-23-{retry_index}-invoked.json"
            retries.append(name)
            self._manifest(
                root,
                name,
                f"retry-session-{retry_index}",
                target,
            )
        self._install_real_supersession(
            root,
            target,
            selected_manifest=retries[-1],
            superseded_manifests=["campaign-23-0-invoked.json", retries[0]],
        )

        self.assertEqual(len(validated_supersession_entries(root)), 1)
        joined = _campaign_cooldown_evidence(root, None)
        self.assertEqual(len(joined), 47)
        self.assertTrue(all(row["verified"] for row in joined.values()))
        self.assertEqual(joined[target]["session_id"], "retry-session-2")

    def test_57_member_fixture_preserves_44_aliases_and_two_supersessions(self):
        self._assert_7b_corpus_shape_resolves()

    def test_47_member_fixture_preserves_one_consumed_supersession(self):
        self._assert_contrast_corpus_shape_resolves()

    def test_supersession_naming_mismatched_occurrences_refuses(self):
        from joulewise.analysis_engine import inputs as inputs_module

        entry = {
            "bundle_id": "dup-bundle",
            "selected_occurrence": {
                "source_manifest": {"path": "campaign_manifests/campaign-b.json"},
                "member_index": 0,
                "bundle_index": 0,
            },
            "superseded_occurrences": [
                {
                    "source_manifest": {
                        "path": "campaign_manifests/campaign-OTHER.json"
                    },
                    "member_index": 3,
                    "bundle_index": 0,
                }
            ],
        }
        with unittest.mock.patch.object(
            inputs_module,
            "supersession_entry_validation_results",
            return_value=([entry], [True]),
        ):
            resolved = inputs_module._campaign_cooldown_evidence(
                self._duplicated_root(), None
            )
        row = resolved["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])

    def test_matcher_partial_extra_and_repeated_identities_refuse(self):
        from joulewise.whole_window import (
            supersession_selected_occurrence_identity as match,
        )

        a = ("campaign_manifests/a.json", 0, 0)
        b = ("campaign_manifests/b.json", 0, 0)
        c = ("campaign_manifests/c.json", 0, 0)
        entry = {
            "bundle_id": "x",
            "selected_occurrence": {
                "source_manifest": {"path": b[0]},
                "member_index": 0,
                "bundle_index": 0,
            },
            "superseded_occurrences": [
                {
                    "source_manifest": {"path": a[0]},
                    "member_index": 0,
                    "bundle_index": 0,
                }
            ],
        }
        self.assertEqual(match([entry], "x", [a, b]), b)
        self.assertIsNone(match([entry], "x", [a, b, c]))
        self.assertIsNone(match([entry], "x", [a]))
        self.assertIsNone(match([entry], "x", [a, a]))
        self.assertIsNone(match([entry], "wrong-id", [a, b]))
        self.assertIsNone(match([entry, dict(entry)], "x", [a, b]))

class CooldownResultKeysetUnitTests(unittest.TestCase):
    """Direct structural lock for the C1 keyset union (audit finding F1).

    The public join cannot currently produce an emission-only id (emissions
    are sourced from declared invoked positions), so this exercises the
    helper directly: the defensive leg must surface an undeclared emission
    id rather than dropping it.
    """

    def test_emission_only_id_is_included_after_declared_ids(self):
        from joulewise.analysis_engine.inputs import _cooldown_result_bundle_ids

        declared = {"decl-a": [("m", 0, 0)], "decl-b": [("m", 1, 0)]}
        emissions = {"decl-b": [(("m", 1, 0), {})], "emit-only": [(("m", 2, 0), {})]}
        self.assertEqual(
            _cooldown_result_bundle_ids(declared, emissions),
            ["decl-a", "decl-b", "emit-only"],
        )

    def test_no_emission_only_ids_yields_declared_order(self):
        from joulewise.analysis_engine.inputs import _cooldown_result_bundle_ids

        declared = {"decl-a": [("m", 0, 0)]}
        self.assertEqual(
            _cooldown_result_bundle_ids(declared, {"decl-a": [(("m", 0, 0), {})]}),
            ["decl-a"],
        )
