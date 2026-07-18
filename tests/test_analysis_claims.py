"""Five-outcome, sensitivity, floor, and artifact fixtures for P2-037."""

from __future__ import annotations

import copy
import hashlib
import unittest
from pathlib import Path

from joulewise.analysis_engine.artifact import (
    calculate_claim_verdicts_id,
    finalize_claim_verdicts,
    render_claim_verdicts,
    validate_claim_verdicts,
)
from joulewise.analysis_engine import _combined_floor, _interpolation_reasons, _subset_floor
from joulewise.analysis_engine.estimators import (
    DeterministicBoundTerm,
    PairedObservation,
    estimate_paired_blocks,
)
from joulewise.analysis_engine.claims import REDUCER_REASON_CODES, evaluate_claim
from joulewise.analysis_engine.inputs import (
    BundleEvidence,
    FloorRequest,
    FloorResolution,
    LoadedAnalysisInputs,
    governed_stochastic_variance,
    resolve_floor,
    window_evidence_precheck,
)
from joulewise.analysis_engine.sensitivity import (
    influence_triggers,
    randomization_check,
    summarize_loo,
)
from tests.test_detection_floor import make_artifact, make_consumer


HEX = "a" * 64
MANIFEST_ID = "am-" + "b" * 64


def bundle_audit_row(bundle_id: str) -> dict:
    side, index = bundle_id.split("-")
    return {
        "bundle_id": bundle_id,
        "relative_path": f"runs/{bundle_id}",
        "entry_id": f"entry-{bundle_id}",
        "block_id": f"block-{index}",
        "cell_id": f"cell-{side}",
        "condition_id": f"cond-{side}",
        "config_sha256": HEX,
        "expected_config_sha256": HEX,
        "manifest_config_sha256": HEX,
        "summary_sha256": HEX,
        "strict_status": "valid",
        "strict_problems": [],
        "summary_status": "succeeded",
        "base_reason_codes": [],
        "window_prechecks": {},
        "cooldown_cap_hit": False,
        "campaign_cooldown": None,
        "idle_window_suspect": False,
        "token_provenance": {
            "output_tokens": None,
            "token_count_source": None,
            "stop_reason": None,
            "output_policy": None,
            "tokenizer_identity": None,
        },
        "scientific_identity": None,
        "replacement_classification": "registered",
        "inclusion_status": "included",
    }


def evaluation(**overrides):
    values = {
        "estimate": 2.0,
        "metrology_aware_ci95": {"lower": 1.5, "upper": 2.5},
        "decision_interval": {"lower": 1.25, "upper": 2.75},
        "floor_gate_j": 1.0,
        "adjusted_rejected": True,
    }
    values.update(overrides)
    return evaluate_claim(**values)


def minimal_contrast(outcome="direction_supported"):
    ready = outcome in {"direction_supported", "equivalent"}
    reason_codes = []
    direction = "positive" if outcome == "direction_supported" else None
    return {
        "contrast_id": "ctr-test",
        "plan_id": "AP-2",
        "family_instance_id": "fam-test",
        "claim_role": "primary",
        "metric": {
            "name": "gross_energy_j",
            "metric_tag": "gross_request",
            "window_class": "request",
            "unit": "J",
            "ratio_estimand": None,
        },
        "conditions": {
            "condition_a_id": "cond-a",
            "condition_b_id": "cond-b",
            "cell_a_id": "cell-a",
            "cell_b_id": "cell-b",
            "difference_orientation": "condition_b_minus_condition_a",
        },
        "hypothesized_direction": "positive",
        "equivalence": None,
        "mde": None,
        "bundle_blocks": {
            "planned_block_ids": ["block-1", "block-2"],
            "included_bundle_ids": ["a-1", "a-2", "b-1", "b-2"],
            "blocks": [
                {
                    "block_id": block_id,
                    "bundle_a_id": f"a-{index}",
                    "bundle_b_id": f"b-{index}",
                    "included": True,
                    "reason_codes": [],
                }
                for index, block_id in enumerate(("block-1", "block-2"), 1)
            ],
        },
        "sampling": {
            "confirmatory_status": "confirmatory",
            "planned_n": 2,
            "observed_complete_n": 2,
        },
        "estimator": {
            "name": "paired_block_mean_difference_t_v1",
            "n": 2,
            "df": 1,
            "estimate": 2.0,
            "s_d": 0.0,
            "SE_repeat": 0.0,
            "SE_metrology": 0.0,
            "SE_total": 0.0,
            "t_critical_95": 12.706,
            "repeat_point_CI95": {"lower": 2.0, "upper": 2.0},
            "metrology_aware_CI95": {"lower": 2.0, "upper": 2.0},
            "variance_contributions": [],
            "excluded_stochastic_terms": [],
            "raw_p": 0.0,
        },
        "deterministic_bounds": {
            "terms": [{"name": "interpolation", "bound": 0.25}],
            "total": 0.25,
            "decision_interval": {"lower": 1.75, "upper": 2.25},
        },
        "floor": {
            "status": "resolved",
            "floor_row_ids": ["floor-cell"],
            "floor_abs_j": 0.5,
            "floor_cmp_j": 1.0,
            "active_floor_j": 1.0,
            "transport_verdict": "transported",
            "resolutions": [
                {
                    "status": "transported",
                    "source_cell_ids": ["floor-cell"],
                    "transport_group_id": "tg-1",
                    "transport_rule_id": "same_stack_componentwise_worst_case.v1",
                    "floor_abs_j": 0.5,
                    "floor_cmp_j": 1.0,
                    "floor_gate_j": 1.0,
                    "reason_codes": [],
                }
            ],
        },
        "multiplicity": {"raw_p": 0.0, "adjusted_p": 0.0, "rejected": True},
        "randomization_check": {
            "status": "not_required",
            "reason": None,
            "n_blocks": 2,
            "exact_two_sided_p": None,
            "rejects": None,
        },
        "loo": {"status": "not_run", "rows": []},
        "sensitivity_status": "not_run",
        "claim_evaluation": {
            "outcome": outcome,
            "direction": direction,
            "reason_codes": reason_codes,
            "claim_ready_for_l2_l3": ready,
            "claim_level_ceiling": "L2" if ready else "L1",
        },
    }


def minimal_artifact():
    contrast = minimal_contrast()
    body = {
        "schema_version": "joulewise.claim_verdicts.v1",
        "claim_verdicts_id": "",
        "engine": {
            "implementation": "joulewise.analysis_engine",
            "algorithm_version": "1",
            "difference_orientation": "condition_b_minus_condition_a",
            "policy_identity": {
                "floor_resolution": "declared_exact_bundle_config_floor_v1",
                "stochastic_variance": "p2044_reducer_0_4_1_idle_variance_v1",
                "campaign_cooldown": "campaign_provenance_v1_hash_bound_per_member_v1",
            },
        },
        "inputs": {
            "analysis_manifest": {"manifest_id": MANIFEST_ID, "file_sha256": HEX},
            "floor_artifact": {"artifact_id": "df-test", "file_sha256": HEX},
            "runs_root_label": "runs",
            "evidence_class": "current",
            "limitations": [],
        },
        "bundle_audit": [
            bundle_audit_row(bundle_id)
            for bundle_id in ("a-1", "a-2", "b-1", "b-2")
        ],
        "sampling_audit": {
            "design": "fixed_n",
            "planned_n_blocks": 2,
            "registered_blocks": ["block-1", "block-2"],
            "valid_replacements": [],
            "unregistered_matching_bundles": [],
            "top_up_detected": False,
            "demoted_contrast_ids": [],
        },
        "families": [
            {
                "family_instance_id": "fam-test",
                "plan_id": "AP-2",
                "claim_role": "primary",
                "method": "holm",
                "alpha": 0.05,
                "q": None,
                "m": 1,
                "contrast_ids": ["ctr-test"],
                "finite_test_count": 1,
                "raw_ordering": ["ctr-test"],
                "adjusted_p_values": {"ctr-test": 0.0},
                "missing_test_ids": [],
                "structural_status": "complete",
            }
        ],
        "contrasts": [contrast],
    }
    return finalize_claim_verdicts(body)


class ClaimOutcomeTests(unittest.TestCase):
    def test_environment_barrier_reasons_are_canonical_reducer_codes(self):
        self.assertTrue(
            {"environment_admission_failed", "environment_override"}
            <= REDUCER_REASON_CODES
        )

    def test_all_five_outcomes_and_strict_floor_boundary(self):
        self.assertEqual(evaluation()["outcome"], "direction_supported")
        self.assertEqual(
            evaluation(estimate=1.0)["outcome"], "not_resolvable"
        )
        self.assertEqual(
            evaluation(
                metrology_aware_ci95={"lower": -0.5, "upper": 2.5},
                decision_interval={"lower": -0.75, "upper": 2.75},
            )["outcome"],
            "unresolved",
        )
        self.assertEqual(
            evaluation(
                estimate=None,
                metrology_aware_ci95=None,
                decision_interval=None,
            )["outcome"],
            "not_estimable",
        )
        equivalent = evaluation(
            estimate=0.1,
            metrology_aware_ci95={"lower": -0.2, "upper": 0.4},
            decision_interval={"lower": -0.4, "upper": 0.6},
            floor_gate_j=0.5,
            equivalence={"margin": 1.0, "method": "tost_v1"},
        )
        self.assertEqual(equivalent["outcome"], "equivalent")

    def test_normative_four_j_interpolation_counterexample_fails_closed(self):
        estimate = estimate_paired_blocks(
            tuple(
                PairedObservation(
                    f"block-{index}",
                    value_a=float(index),
                    value_b=float(index + 6),
                    deterministic_terms=(
                        DeterministicBoundTerm(
                            "E_interpolation_joint_edge_bound_j",
                            bound_a=2.0,
                            bound_b=2.0,
                        ),
                    ),
                )
                for index in range(1, 6)
            )
        )
        reasons = _interpolation_reasons(
            estimate,
            {"active_floor_j": 1.0},
        )
        self.assertEqual(
            reasons,
            [
                "interpolation_bound_exceeds_floor",
                "interpolation_bound_exceeds_half_effect",
            ],
        )
        result = evaluation(base_reason_codes=reasons)
        self.assertEqual(result["outcome"], "not_resolvable")
        self.assertIn("interpolation_bound_exceeds_floor", result["reason_codes"])
        self.assertIn(
            "interpolation_bound_exceeds_half_effect", result["reason_codes"]
        )

        below = estimate_paired_blocks(
            tuple(
                PairedObservation(
                    f"below-{index}",
                    value_a=float(index),
                    value_b=float(index + 6),
                    deterministic_terms=(
                        DeterministicBoundTerm(
                            "E_interpolation_joint_edge_bound_j",
                            bound_a=0.05,
                            bound_b=0.05,
                        ),
                    ),
                )
                for index in range(1, 6)
            )
        )
        self.assertEqual(_interpolation_reasons(below, {"active_floor_j": 1.0}), [])

    def test_demotions_and_verdict_sensitivity_preserve_point_outcome_but_cap_claim(self):
        demoted = evaluation(
            base_reason_codes=("outcome_dependent_top_up",),
            confirmatory_status="demoted_exploratory",
        )
        self.assertEqual(demoted["outcome"], "direction_supported")
        self.assertFalse(demoted["claim_ready_for_l2_l3"])
        self.assertEqual(demoted["claim_level_ceiling"], "L1")
        influential = evaluation(
            base_reason_codes=("loo_verdict_influential",),
            sensitivity_blocking=True,
        )
        self.assertEqual(influential["outcome"], "direction_supported")
        self.assertFalse(influential["claim_ready_for_l2_l3"])


class SensitivityTests(unittest.TestCase):
    def test_design_respecting_randomization_statuses(self):
        deterministic = randomization_check(
            [1.0] * 5,
            {"scheme": "deterministic_rotation", "exchangeability": "none"},
        )
        self.assertEqual(deterministic["status"], "not_required")
        too_small = randomization_check(
            [1.0] * 5,
            {"scheme": "paired_label_swap_within_block", "exchangeability": "within_block"},
        )
        self.assertEqual(too_small["status"], "not_run")
        exact = randomization_check(
            [1.0] * 6,
            {"scheme": "paired_label_swap_within_block", "exchangeability": "within_block"},
        )
        self.assertEqual(exact["exact_two_sided_p"], 2 / 64)
        with self.assertRaisesRegex(ValueError, "unsupported randomization"):
            randomization_check(
                [1.0] * 6,
                {"scheme": "global_label_shuffle", "exchangeability": "global"},
            )
        stratified = randomization_check(
            [1.0] * 6,
            {
                "scheme": "stratified_paired_label_swap",
                "exchangeability": "within_named_strata",
                "named_strata": [
                    {"stratum_id": "early", "block_ids": ["b1", "b2", "b3"]},
                    {"stratum_id": "late", "block_ids": ["b4", "b5", "b6"]},
                ],
            },
            block_ids=["b1", "b2", "b3", "b4", "b5", "b6"],
        )
        self.assertEqual(stratified["exact_two_sided_p"], 2 / 64)
        with self.assertRaisesRegex(ValueError, "cover each frozen block"):
            randomization_check(
                [1.0] * 6,
                {
                    "scheme": "stratified_paired_label_swap",
                    "exchangeability": "within_named_strata",
                    "named_strata": [
                        {"stratum_id": "incomplete", "block_ids": ["b1", "b2"]}
                    ],
                },
                block_ids=["b1", "b2", "b3", "b4", "b5", "b6"],
            )

    def test_loo_triggers_every_verdict_and_magnitude_rule(self):
        full = {
            "estimate": 2.0,
            "floor_status": "above_floor",
            "adjusted_rejection": True,
            "outcome": "direction_supported",
        }
        changed = {
            "estimate": -1.0,
            "floor_status": "not_above_floor",
            "adjusted_rejection": False,
            "outcome": "unresolved",
        }
        triggers = influence_triggers(full, changed, active_threshold=1.0)
        self.assertEqual(
            triggers,
            [
                "estimate_sign",
                "floor_status",
                "adjusted_rejection",
                "outcome",
                "estimate_magnitude",
            ],
        )
        status, verdict, magnitude_only = summarize_loo(
            [{"influence_triggers": triggers}]
        )
        self.assertEqual(status, "concern")
        self.assertTrue(verdict)
        self.assertFalse(magnitude_only)

        no_floor_threshold = influence_triggers(
            full,
            {**full, "estimate": 100.0},
            active_threshold=None,
        )
        self.assertNotIn("estimate_magnitude", no_floor_threshold)


class InputSeamTests(unittest.TestCase):
    def test_combined_floor_uses_every_selected_absolute_and_comparative_max(self):
        resolutions = (
            FloorResolution(
                status="transported",
                artifact_id="df",
                artifact_sha256=HEX,
                source_cell_ids=("abs-high",),
                transport_group_id="g1",
                transport_rule_id="rule",
                floor_abs_j=4.0,
                floor_cmp_j=1.0,
                floor_gate_j=4.0,
                reason_codes=(),
            ),
            FloorResolution(
                status="transported",
                artifact_id="df",
                artifact_sha256=HEX,
                source_cell_ids=("cmp-high",),
                transport_group_id="g2",
                transport_rule_id="rule",
                floor_abs_j=2.0,
                floor_cmp_j=7.0,
                floor_gate_j=7.0,
                reason_codes=(),
            ),
        )
        combined = _combined_floor(resolutions)
        self.assertEqual(combined["floor_abs_j"], 4.0)
        self.assertEqual(combined["floor_cmp_j"], 7.0)
        self.assertEqual(combined["active_floor_j"], 7.0)

    def test_loo_floor_resolution_receives_only_retained_physical_blocks(self):
        evidence = []
        for index in range(5):
            evidence.append(
                BundleEvidence(
                    entry={"entry_id": f"e-{index}"},
                    bundle_id=f"bundle-{index}",
                    relative_path=f"bundle-{index}",
                    path=Path(f"bundle-{index}"),
                    summary={},
                    metadata={},
                    raw_config={},
                    strict_problems=(),
                    base_reason_codes=(),
                    config_sha256=HEX,
                    summary_sha256=HEX,
                    replacement_classification="registered",
                    inclusion_status="included",
                )
            )
        artifact = make_artifact()
        inputs = LoadedAnalysisInputs(
            manifest={},
            manifest_sha256=HEX,
            floor_artifact=artifact,
            floor_sha256=HEX,
            registered={},
            effective={},
            extra_audits=(),
            valid_replacements=(),
            unregistered_matching=(),
            top_up_entry_ids=frozenset(),
        )
        prepared = {
            "manifest": {
                "condition_a_id": "cond-a",
                "condition_b_id": "cond-b",
                "floor_selector": {
                    "metric": "gross_energy_j",
                    "window_class": "gross_request",
                    "condition_family_ids": ["cond-a", "cond-b"],
                },
            },
            "observation_parts": [
                {
                    "block_id": f"block-{index}",
                    "evidence_a": row,
                    "evidence_b": row,
                }
                for index, row in enumerate(evidence)
            ],
        }
        observed_counts = []

        def factory(contrast, condition_id, rows, floor_artifact):
            del contrast, condition_id, floor_artifact
            observed_counts.append(len(rows))
            return None

        floor, _ = _subset_floor(
            inputs,
            prepared,
            factory,
            omit_block="block-2",
        )
        self.assertEqual(observed_counts, [4, 4])
        self.assertEqual(floor["status"], "refused")

    def test_cooldown_cap_false_without_verified_campaign_provenance_fails_closed(self):
        summary = {
            "status": "succeeded",
            "claim_eligibility": {
                "gross_request": {"eligible": True, "reasons": []}
            },
            "measurement_quality": {"cooldown_cap_hit": False},
        }
        evidence = BundleEvidence(
            entry={"entry_id": "e", "block_id": "b", "cell_id": "c", "condition_id": "d"},
            bundle_id="bundle",
            relative_path="bundle",
            path=Path("bundle"),
            summary=summary,
            metadata={},
            raw_config={},
            strict_problems=(),
            base_reason_codes=(),
            config_sha256=HEX,
            summary_sha256=HEX,
            replacement_classification="registered",
            inclusion_status="included",
        )
        result = window_evidence_precheck(
            evidence,
            {
                "name": "gross_energy_j",
                "metric_tag": "gross_request",
                "window_class": "request",
            },
        )
        self.assertFalse(result["eligible"])
        self.assertIn("window_evidence_precheck_missing", result["reasons"])
        self.assertIn("campaign_cooldown_evidence_missing", result["reasons"])
        self.assertTrue(result["legacy_precheck_not_claim_evaluator"])

    def test_p2044_governed_variance_and_distinct_failure_reasons(self):
        evidence = BundleEvidence(
            entry={},
            bundle_id="bundle",
            relative_path="bundle",
            path=Path("bundle"),
            summary={"energy_variance_terms_j2": {"E_idle_mean_j2": 1.0}},
            metadata={},
            raw_config={},
            strict_problems=(),
            base_reason_codes=(),
            config_sha256=HEX,
            summary_sha256=HEX,
            replacement_classification="registered",
            inclusion_status="included",
        )
        terms, reasons = governed_stochastic_variance(
            evidence, {"name": "energy_request_j"}
        )
        self.assertEqual(terms, ())
        self.assertEqual(reasons, ("required_error_term_unknown",))

        evidence.summary = {
            "summary_provenance": {"reducer_version": "0.4.1"},
            "idle_mean_uncertainty": {
                "status": "estimated",
                "method": "newey_west_bartlett_10s_iid_floor_v1",
                "correlation_scope": "shared_session_unknown",
            },
            "energy_variance_terms_j2": {"E_idle_mean_j2": 2.5},
        }
        terms, reasons = governed_stochastic_variance(
            evidence, {"name": "energy_request_j"}
        )
        self.assertEqual(terms, ())
        self.assertEqual(reasons, ("required_covariance_unknown",))

        evidence.summary["idle_mean_uncertainty"]["correlation_scope"] = (
            "independent_run"
        )
        terms, reasons = governed_stochastic_variance(
            evidence, {"name": "energy_request_j"}
        )
        self.assertEqual(reasons, ())
        self.assertEqual(
            terms,
            (
                {
                    "name": "E_idle_mean_j2",
                    "variance": 2.5,
                    "correlation_scope": "independent_run",
                },
            ),
        )

        evidence.summary["summary_provenance"]["reducer_version"] = "0.4.2"
        evidence.summary["idle_mean_uncertainty"]["additive_diagnostic"] = {
            "effective_lag_count": 4
        }
        terms, reasons = governed_stochastic_variance(
            evidence, {"name": "energy_request_j"}
        )
        self.assertEqual(reasons, ())
        self.assertEqual(terms[0]["variance"], 2.5)

        for rejected_version in ("0.4.0", "0.5.0"):
            with self.subTest(reducer_version=rejected_version):
                evidence.summary["summary_provenance"]["reducer_version"] = (
                    rejected_version
                )
                terms, reasons = governed_stochastic_variance(
                    evidence, {"name": "energy_request_j"}
                )
                self.assertEqual(terms, ())
                self.assertEqual(reasons, ("required_error_term_unknown",))

    def test_typed_floor_request_resolves_and_tampered_regime_refuses(self):
        artifact = make_artifact()
        artifact["calibration_scope"] = "window_a"
        consumer = make_consumer()
        request = FloorRequest(
            backend=consumer.pop("backend"),
            metric=consumer.pop("metric"),
            window_class=consumer.pop("window_class"),
            condition_family_id=consumer.pop("condition_family_id"),
            condition_family_sha256=consumer.pop("condition_family_sha256"),
            stack_identity_sha256=consumer.pop("stack_identity_sha256"),
            consumer_stress=consumer,
        )
        resolution = resolve_floor(artifact, HEX, request)
        self.assertEqual(resolution.status, "transported")
        self.assertEqual(
            resolution.floor_gate_j,
            max(resolution.floor_abs_j, resolution.floor_cmp_j),
        )
        harder = copy.deepcopy(dict(request.consumer_stress))
        harder["p95_sample_gap_s_max"] = 999.0
        refused = resolve_floor(
            artifact,
            HEX,
            FloorRequest(
                backend=request.backend,
                metric=request.metric,
                window_class=request.window_class,
                condition_family_id=request.condition_family_id,
                condition_family_sha256=request.condition_family_sha256,
                stack_identity_sha256=request.stack_identity_sha256,
                consumer_stress=harder,
            ),
        )
        self.assertEqual(refused.status, "refused")
        self.assertIn("cadence_harder_than_calibration", refused.reason_codes)

        missing = resolve_floor(
            artifact,
            HEX,
            FloorRequest(
                backend=request.backend,
                metric=request.metric,
                window_class=request.window_class,
                condition_family_id="unregistered-family",
                condition_family_sha256=request.condition_family_sha256,
                stack_identity_sha256=request.stack_identity_sha256,
                consumer_stress=request.consumer_stress,
            ),
        )
        self.assertEqual(missing.status, "refused")
        self.assertEqual(missing.reason_codes, ("cell_missing",))

        stale_artifact = copy.deepcopy(artifact)
        stale_artifact["cells"][0]["eligibility"].update(
            {"status": "stale", "claim_usable": False}
        )
        stale = resolve_floor(stale_artifact, HEX, request)
        self.assertEqual(stale.status, "refused")
        self.assertIn("cell_stale", stale.reason_codes)

        ambiguous_artifact = copy.deepcopy(artifact)
        duplicate_group = copy.deepcopy(ambiguous_artifact["transport_groups"][0])
        duplicate_group["transport_group_id"] = "tg-duplicate"
        ambiguous_artifact["transport_groups"].append(duplicate_group)
        ambiguous = resolve_floor(ambiguous_artifact, HEX, request)
        self.assertEqual(ambiguous.status, "refused")
        self.assertEqual(ambiguous.reason_codes, ("transport_group_incomplete",))

    def test_smoke_floor_and_pending_idle_guard_are_never_claim_usable(self):
        smoke = make_artifact()
        consumer = make_consumer()
        request = FloorRequest(
            backend=consumer.pop("backend"),
            metric=consumer.pop("metric"),
            window_class=consumer.pop("window_class"),
            condition_family_id=consumer.pop("condition_family_id"),
            condition_family_sha256=consumer.pop("condition_family_sha256"),
            stack_identity_sha256=consumer.pop("stack_identity_sha256"),
            consumer_stress=consumer,
        )
        resolution = resolve_floor(smoke, HEX, request)
        self.assertEqual(resolution.status, "refused")
        self.assertIn("cell_not_claim_ready", resolution.reason_codes)

        idle = copy.deepcopy(smoke)
        idle["calibration_scope"] = "window_a"
        idle["cells"][0]["key"]["metric"] = "energy_request_j"
        idle["transport_groups"][0]["metric"] = "energy_request_j"
        idle_request = FloorRequest(
            backend=request.backend,
            metric="energy_request_j",
            window_class=request.window_class,
            condition_family_id=request.condition_family_id,
            condition_family_sha256=request.condition_family_sha256,
            stack_identity_sha256=request.stack_identity_sha256,
            consumer_stress=request.consumer_stress,
        )
        idle_resolution = resolve_floor(idle, HEX, idle_request)
        self.assertEqual(idle_resolution.status, "refused")
        self.assertIn("consumer_term_unknown", idle_resolution.reason_codes)


class ClaimArtifactTests(unittest.TestCase):
    def test_artifact_identity_and_bytes_are_deterministic(self):
        first = minimal_artifact()
        second = minimal_artifact()
        self.assertEqual(first, second)
        self.assertEqual(render_claim_verdicts(first), render_claim_verdicts(second))
        self.assertEqual(first["claim_verdicts_id"], calculate_claim_verdicts_id(first))
        self.assertEqual(
            hashlib.sha256(render_claim_verdicts(first)).hexdigest(),
            hashlib.sha256(render_claim_verdicts(second)).hexdigest(),
        )
        self.assertEqual(validate_claim_verdicts(first), [])

    def test_artifact_mutations_fail_schema_math_and_reason_order(self):
        artifact = minimal_artifact()
        mutants = []
        wrong_df = copy.deepcopy(artifact)
        wrong_df["contrasts"][0]["estimator"]["df"] = 2
        mutants.append(wrong_df)
        floor_min = copy.deepcopy(artifact)
        floor_min["contrasts"][0]["floor"]["active_floor_j"] = 0.5
        mutants.append(floor_min)
        absolute_path = copy.deepcopy(artifact)
        absolute_path["inputs"]["runs_root_label"] = "/tmp/runs"
        mutants.append(absolute_path)
        bad_reason = copy.deepcopy(artifact)
        bad_reason["contrasts"][0]["claim_evaluation"]["reason_codes"] = [
            "not_a_reason"
        ]
        mutants.append(bad_reason)
        for mutant in mutants:
            mutant["claim_verdicts_id"] = calculate_claim_verdicts_id(mutant)
            with self.subTest(mutant=mutants.index(mutant)):
                self.assertTrue(validate_claim_verdicts(mutant))

    def test_rehashed_audit_floor_ratio_and_sampling_mutants_are_rejected(self):
        cases = []

        audit_escape = copy.deepcopy(minimal_artifact())
        audit_escape["bundle_audit"][0]["host_root"] = "/tmp/escape"
        cases.append((audit_escape, "unrecognized key(s): host_root"))

        ghost_block = copy.deepcopy(minimal_artifact())
        ghost_block["sampling_audit"]["registered_blocks"].append("ghost-block")
        cases.append((ghost_block, "must exactly match contrast planned blocks"))

        ghost_replacement = copy.deepcopy(minimal_artifact())
        ghost_replacement["sampling_audit"]["valid_replacements"].append(
            {
                "entry_id": "ghost-entry",
                "original_bundle_id": "a-1",
                "replacement_bundle_id": "ghost-bundle",
                "relative_path": "runs/ghost-bundle",
            }
        )
        cases.append((ghost_replacement, "replacement_bundle_id: missing bundle audit"))

        invalid_ratio = copy.deepcopy(minimal_artifact())
        invalid_ratio["contrasts"][0]["metric"]["ratio_estimand"] = {
            "form": "analyst_selected_after_observation"
        }
        cases.append((invalid_ratio, "ratio_estimand must be an exact adjudicated B8 object"))

        missing_comparative_floor = copy.deepcopy(minimal_artifact())
        missing_comparative_floor["contrasts"][0]["floor"]["resolutions"][0][
            "floor_cmp_j"
        ] = None
        cases.append(
            (missing_comparative_floor, "floor_cmp_j: usable resolution must be numeric")
        )

        refused_inside_resolved = copy.deepcopy(minimal_artifact())
        resolution = refused_inside_resolved["contrasts"][0]["floor"][
            "resolutions"
        ][0]
        resolution.update(
            status="refused",
            floor_abs_j=None,
            floor_cmp_j=None,
            floor_gate_j=None,
            reason_codes=["cell_missing"],
        )
        cases.append(
            (
                refused_inside_resolved,
                "resolved floor requires only usable resolutions",
            )
        )

        inner_outer_mismatch = copy.deepcopy(minimal_artifact())
        inner_outer_mismatch["contrasts"][0]["floor"]["resolutions"][0].update(
            floor_abs_j=0.75,
            floor_cmp_j=1.25,
            floor_gate_j=1.25,
        )
        cases.append((inner_outer_mismatch, "must equal resolution maximum"))

        for mutant, fragment in cases:
            mutant["claim_verdicts_id"] = calculate_claim_verdicts_id(mutant)
            with self.subTest(fragment=fragment):
                errors = validate_claim_verdicts(mutant)
                self.assertTrue(
                    any(fragment in error for error in errors),
                    errors,
                )

    def test_json_valid_wrong_types_return_errors_instead_of_crashing(self):
        mutations = (
            lambda artifact: artifact["bundle_audit"][0].__setitem__(
                "entry_id", []
            ),
            lambda artifact: artifact["bundle_audit"][0].__setitem__(
                "replacement_classification", {}
            ),
            lambda artifact: artifact["families"][0]["contrast_ids"].__setitem__(
                0, []
            ),
            lambda artifact: artifact["contrasts"][0].__setitem__(
                "family_instance_id", {}
            ),
            lambda artifact: artifact["contrasts"][0]["estimator"].__setitem__(
                "SE_repeat", None
            ),
            lambda artifact: artifact["contrasts"][0]["estimator"].__setitem__(
                "t_critical_95", []
            ),
            lambda artifact: artifact["contrasts"][0]["floor"][
                "resolutions"
            ][0].__setitem__("status", {}),
            lambda artifact: artifact["contrasts"][0][
                "randomization_check"
            ].__setitem__("status", []),
        )
        for index, mutate in enumerate(mutations):
            mutant = copy.deepcopy(minimal_artifact())
            mutate(mutant)
            mutant["claim_verdicts_id"] = calculate_claim_verdicts_id(mutant)
            with self.subTest(index=index):
                self.assertTrue(validate_claim_verdicts(mutant))

    def test_rehashed_semantic_claim_mutants_are_rejected(self):
        cases = []

        below_floor = copy.deepcopy(minimal_artifact())
        below_floor["contrasts"][0]["floor"].update(
            floor_cmp_j=3.0,
            active_floor_j=3.0,
        )
        cases.append((below_floor, "claim_evaluation.outcome: disagrees"))

        not_rejected = copy.deepcopy(minimal_artifact())
        not_rejected["contrasts"][0]["multiplicity"]["rejected"] = False
        cases.append((not_rejected, "multiplicity.rejected"))

        zero_crossing = copy.deepcopy(minimal_artifact())
        zero_crossing["contrasts"][0]["estimator"]["metrology_aware_CI95"] = {
            "lower": -1.0,
            "upper": 5.0,
        }
        zero_crossing["contrasts"][0]["deterministic_bounds"]["decision_interval"] = {
            "lower": -1.25,
            "upper": 5.25,
        }
        cases.append((zero_crossing, "claim_evaluation.outcome: disagrees"))

        missing_audit = copy.deepcopy(minimal_artifact())
        missing_audit["bundle_audit"] = []
        cases.append((missing_audit, "missing bundle audit row"))

        bad_scatter = copy.deepcopy(minimal_artifact())
        bad_scatter["contrasts"][0]["estimator"]["s_d"] = 999.0
        cases.append((bad_scatter, "SE_repeat: must equal s_d/sqrt(n)"))

        bad_critical = copy.deepcopy(minimal_artifact())
        bad_critical["contrasts"][0]["estimator"]["t_critical_95"] = 1.96
        cases.append((bad_critical, "t_critical_95: disagrees with df"))

        forged_p = copy.deepcopy(minimal_artifact())
        forged_contrast = forged_p["contrasts"][0]
        forged_contrast["estimator"]["raw_p"] = 0.5
        forged_contrast["multiplicity"].update(
            raw_p=0.5,
            adjusted_p=0.5,
            rejected=False,
        )
        forged_contrast["claim_evaluation"].update(
            outcome="unresolved",
            direction=None,
            reason_codes=["multiplicity_not_rejected"],
            claim_ready_for_l2_l3=False,
            claim_level_ceiling="L1",
        )
        forged_p["families"][0].update(
            adjusted_p_values={"ctr-test": 0.5},
            raw_ordering=["ctr-test"],
        )
        cases.append((forged_p, "estimator.raw_p: disagrees"))

        for mutant, fragment in cases:
            mutant["claim_verdicts_id"] = calculate_claim_verdicts_id(mutant)
            with self.subTest(fragment=fragment):
                errors = validate_claim_verdicts(mutant)
                self.assertTrue(
                    any(fragment in error for error in errors),
                    errors,
                )


if __name__ == "__main__":
    unittest.main()
