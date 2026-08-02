"""Five-outcome, sensitivity, floor, and artifact fixtures for P2-037."""

from __future__ import annotations

import base64
import copy
import gzip
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.analysis_engine.artifact import (
    calculate_claim_verdicts_id,
    finalize_claim_verdicts,
    render_claim_verdicts,
    validate_claim_verdicts,
)
from joulewise.analysis_engine import (
    _combined_floor,
    _decorate_v3_floor,
    _interpolation_reasons,
    _subset_floor,
)
from joulewise.analysis_engine.estimators import (
    DeterministicBoundTerm,
    PairedObservation,
    RatioObservation,
    estimate_paired_blocks,
)
from joulewise.analysis_engine.ratio import convert_floor_to_ratio_units
from joulewise.analysis_engine.claims import (
    REASON_CODES,
    REDUCER_REASON_CODES,
    evaluate_claim,
    ordered_reason_codes,
)
from joulewise.analysis_engine.inputs import (
    ANCHOR_FALLBACK_MEMBER_REFUSAL,
    AnalysisInputError,
    BundleEvidence,
    FloorRequest,
    FloorResolution,
    GOVERNED_REDUCER_IDLE_METHOD_PAIRS,
    LoadedAnalysisInputs,
    MOCK_TELEMETRY_CLAIM_REFUSAL,
    _read_bundle,
    anchor_shift_envelope,
    bind_floor_artifact_evidence,
    deterministic_bounds,
    governed_stochastic_variance,
    metric_value,
    resolve_floor,
    window_evidence_precheck,
)
from joulewise.cli import validate_bundle
from joulewise.analysis_engine.sensitivity import (
    influence_triggers,
    randomization_check,
    summarize_loo,
)
from joulewise.detection_floor import (
    ATTRIBUTION_FLOOR_SOURCE,
    ATTRIBUTION_LIMIT_CLASS,
    STACK_IDENTITY_DOMAIN,
    attribution_single_count_discipline,
    canonical_domain_sha256,
    comparative_false_effect_floor,
)
from scripts import mint_floor_artifact as mint
from joulewise.whole_window import CustodyTelemetryIdentity
from tests.test_detection_floor import (
    make_artifact,
    make_cell,
    make_consumer,
    make_regime,
    whole_window_allowance,
)


HEX = "a" * 64
MANIFEST_ID = "am-" + "b" * 64

# Byte-exact copy of the stored 0.5.0/v2 corpus wire
# runs_recal4_20260719/p2015-df-su-sentinel-abs-r01/summary_metrics.json
# (gzip+base64; never hand-simplified).  The sha256 pin guards the fixture.
_SENTINEL_SUMMARY_SHA256 = (
    "8abd820ea4955713897c512cde703c0e05dfe9aa3a1b1daabc4c4062459f42e8"
)
_SENTINEL_SUMMARY_B64 = "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"


def sentinel_stored_wire() -> dict:
    raw = gzip.decompress(base64.b64decode(_SENTINEL_SUMMARY_B64))
    if hashlib.sha256(raw).hexdigest() != _SENTINEL_SUMMARY_SHA256:
        raise AssertionError("embedded sentinel wire fixture drifted")
    return json.loads(raw)


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
            "floor_artifact": {
                "artifact_id": "df-test",
                "file_sha256": HEX,
                "evidence_root_ids": ["floor-root"],
            },
            "runs_root_label": "runs",
            "evidence_class": "current",
            "limitations": [],
        },
        "supersession_audit": [
            {
                "scope": "analysis_corpus",
                "evidence_root_id": None,
                "authenticated_basis": {
                    "kind": "analysis_manifest_file_sha256",
                    "sha256": HEX,
                },
                "raw_count": 0,
                "validated_count": 0,
                "status": "clean",
            },
            {
                "scope": "floor_evidence",
                "evidence_root_id": "floor-root",
                "authenticated_basis": {
                    "kind": "floor_component_campaign_log_sha256",
                    "sha256s": [HEX],
                },
                "raw_count": 0,
                "validated_count": 0,
                "status": "clean",
            },
        ],
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
            {
                "environment_admission_failed",
                "environment_override",
                MOCK_TELEMETRY_CLAIM_REFUSAL,
            }
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

    def test_significant_negative_does_not_satisfy_positive_registration(self):
        result = evaluation(
            estimate=-2.0,
            metrology_aware_ci95={"lower": -2.5, "upper": -1.5},
            decision_interval={"lower": -2.75, "upper": -1.25},
            hypothesized_direction="positive",
        )
        self.assertEqual(result["outcome"], "direction_supported")
        self.assertEqual(result["direction"], "negative")
        self.assertFalse(result["claim_ready_for_l2_l3"])
        self.assertEqual(result["claim_level_ceiling"], "L1")

    def test_abba_arm_means_use_paired_t_and_never_cancel_bounds(self):
        observations = (
            PairedObservation(
                block_id="b01",
                value_a=(10.0 + 14.0) / 2.0,
                value_b=(20.0 + 22.0) / 2.0,
                stochastic_terms=(),
                deterministic_terms=(
                    DeterministicBoundTerm(
                        name="anchor",
                        bound_a=(0.2 + 0.4) / 2.0,
                        bound_b=(0.5 + 0.7) / 2.0,
                    ),
                ),
            ),
            PairedObservation(
                block_id="b02",
                value_a=(11.0 + 15.0) / 2.0,
                value_b=(21.0 + 23.0) / 2.0,
                stochastic_terms=(),
                deterministic_terms=(
                    DeterministicBoundTerm(
                        name="anchor",
                        bound_a=(0.2 + 0.4) / 2.0,
                        bound_b=(0.5 + 0.7) / 2.0,
                    ),
                ),
            ),
        )
        estimate = estimate_paired_blocks(
            observations,
            estimator="abba_block_arm_mean_difference_t_v1",
        )
        self.assertEqual(estimate.paired_values, (9.0, 9.0))
        self.assertEqual(estimate.estimate, 9.0)
        self.assertAlmostEqual(estimate.deterministic_bound_total, 0.9)

    def test_cross_stack_armwise_floor_is_max_never_sum_and_clause11_survives(self):
        discipline = attribution_single_count_discipline()
        diagnostic_a = {
            "label": "repeatability_diagnostic",
            "published_claim_floor": False,
            "unguarded_floor_j": 0.3,
            "guard_factor": 1.5,
            "guarded_floor_j": 0.45,
        }
        diagnostic_b = {
            "label": "repeatability_diagnostic",
            "published_claim_floor": False,
            "unguarded_floor_j": 0.5,
            "guard_factor": 1.5,
            "guarded_floor_j": 0.75,
        }
        resolutions = (
            FloorResolution(
                status="exact",
                artifact_id="df",
                artifact_sha256=HEX,
                source_cell_ids=("floor-a",),
                transport_group_id=None,
                transport_rule_id=None,
                floor_abs_j=0.5,
                floor_cmp_j=1.0,
                floor_gate_j=1.0,
                reason_codes=(),
                floor_source=ATTRIBUTION_FLOOR_SOURCE,
                floor_limit_class=ATTRIBUTION_LIMIT_CLASS,
                point_floor_diagnostics=diagnostic_a,
                single_count_discipline=discipline,
            ),
            FloorResolution(
                status="exact",
                artifact_id="df",
                artifact_sha256=HEX,
                source_cell_ids=("floor-b",),
                transport_group_id=None,
                transport_rule_id=None,
                floor_abs_j=0.7,
                floor_cmp_j=1.2,
                floor_gate_j=1.2,
                reason_codes=(),
                floor_source=ATTRIBUTION_FLOOR_SOURCE,
                floor_limit_class=ATTRIBUTION_LIMIT_CLASS,
                point_floor_diagnostics=diagnostic_b,
                single_count_discipline=discipline,
            ),
        )
        manifest = {
            "schema_version": "joulewise.analysis_manifest.v3",
            "arms": [
                {"arm_id": "A", "condition_family_id": "cond-a"},
                {"arm_id": "B", "condition_family_id": "cond-b"},
            ],
        }
        contrast_registration = {
            "floor_selector": {"condition_family_ids": ["cond-a", "cond-b"]}
        }
        floor = _decorate_v3_floor(
            manifest,
            contrast_registration,
            _combined_floor(resolutions),
            resolutions,
        )
        self.assertEqual(floor["active_floor_j"], 1.2)
        self.assertNotEqual(floor["active_floor_j"], 2.2)
        self.assertEqual(floor["aggregation"], "max_never_sum")

        artifact = minimal_artifact()
        contrast = artifact["contrasts"][0]
        physical_bundle_ids = []
        physical_audits = []
        for block_index in (1, 2):
            position_ids = {
                "A1": f"a1-{block_index}",
                "B1": f"b1-{block_index}",
                "B2": f"b2-{block_index}",
                "A2": f"a2-{block_index}",
            }
            physical_bundle_ids.extend(position_ids.values())
            contrast["bundle_blocks"]["blocks"][block_index - 1].update(
                {
                    "bundle_a_id": None,
                    "bundle_b_id": None,
                    "position_bundle_ids": position_ids,
                }
            )
            for position, bundle_id in position_ids.items():
                audit = bundle_audit_row(bundle_id)
                is_a = position.startswith("A")
                audit.update(
                    {
                        "entry_id": f"entry-{bundle_id}",
                        "cell_id": "cell-a" if is_a else "cell-b",
                        "condition_id": "cond-a" if is_a else "cond-b",
                    }
                )
                physical_audits.append(audit)
        contrast["bundle_blocks"]["included_bundle_ids"] = sorted(
            physical_bundle_ids
        )
        artifact["bundle_audit"] = physical_audits
        contrast["floor"] = floor
        contrast["estimator"]["name"] = "abba_block_arm_mean_difference_t_v1"
        contrast["claim_evaluation"] = evaluate_claim(
            estimate=contrast["estimator"]["estimate"],
            metrology_aware_ci95=contrast["estimator"]["metrology_aware_CI95"],
            decision_interval=contrast["deterministic_bounds"]["decision_interval"],
            floor_gate_j=floor["active_floor_j"],
            adjusted_rejected=True,
            hypothesized_direction="positive",
            floor_metadata={
                key: floor[key]
                for key in (
                    "floor_source",
                    "floor_limit_class",
                    "point_floor_diagnostics",
                    "single_count_discipline",
                )
            },
        )
        artifact["supersession_audit"] = [
            {
                "scope": "analysis_corpus",
                "evidence_root_id": None,
                "authenticated_basis": {
                    "kind": "whole_window_evaluation_basis_sha256",
                    "sha256": HEX,
                },
                "raw_count": 1,
                "validated_count": 1,
                "status": "clean",
            },
            {
                "scope": "floor_evidence",
                "evidence_root_id": "floor-root",
                "authenticated_basis": {
                    "kind": "floor_component_campaign_log_sha256",
                    "sha256s": [HEX],
                },
                "raw_count": 0,
                "validated_count": 0,
                "status": "clean",
            },
        ]
        published = finalize_claim_verdicts(artifact)
        self.assertEqual(validate_claim_verdicts(published), [])
        published_contrast = published["contrasts"][0]
        self.assertEqual(
            published_contrast["claim_evaluation"]["floor_limit"][
                "single_count_discipline"
            ],
            discipline,
        )
        self.assertEqual(
            discipline["effective_clearable_effect_formula"],
            "floor_j + claim_side_bound_j",
        )
        self.assertEqual(published_contrast["deterministic_bounds"]["total"], 0.25)

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
    def _bind_mlx_file_set_floor(
        self,
        observed_metadata: dict,
    ):
        fixture = Path("tests/fixtures/d078_r01")
        raw_config = json.loads(
            (fixture / "config.json").read_text(encoding="utf-8")
        )
        mint_metadata = json.loads(
            (fixture / "metadata.json").read_text(encoding="utf-8")
        )
        stack = mint._derive_stack_identity(raw_config, mint_metadata)
        artifact = make_artifact(
            [make_cell(regime=make_regime(stack_identity=stack))]
        )
        records: dict[str, tuple[dict, dict]] = {}
        cell = artifact["cells"][0]
        for record in cell["absolute"]["bundle_observations"]:
            records[record["bundle_id"]] = (
                record,
                {
                    "plan_sha256": HEX,
                    "block_id": None,
                    "label": None,
                    "sequence_index": None,
                },
            )
        for block in cell["comparative"]["blocks"]:
            for record in block["members"]:
                records[record["bundle_id"]] = (
                    record,
                    {
                        "plan_sha256": HEX,
                        "block_id": block["block_id"],
                        "label": record["plan_label"],
                        "sequence_index": record["plan_sequence_index"],
                    },
                )

        class FakeReader:
            def __init__(self, path):
                self.path = Path(path)

            def raw_summary(self):
                record, _ = records[self.path.name]
                return {
                    "status": "succeeded",
                    "measurement_quality": {
                        "telemetry_source": "powermetrics"
                    },
                    "energy_uncertainty_status": "bounded",
                    "gross_energy_j": record["metric_value_j"],
                }

            def raw_metadata(self):
                return observed_metadata

            def raw_config(self):
                _, order_tags = records[self.path.name]
                return {**raw_config, "_order_tags": order_tags}

        with (
            tempfile.TemporaryDirectory() as tmp,
            patch(
                "joulewise.analysis_engine.inputs._campaign_order_binding_problems",
                return_value=(),
            ),
            patch(
                "joulewise.analysis_engine.inputs._source_provenance_admission_problems",
                return_value=(),
            ),
            patch(
                "joulewise.analysis_engine.inputs.BundleReader",
                FakeReader,
            ),
            patch(
                "joulewise.analysis_engine.inputs.complete_bundle_sha256",
                return_value="a" * 64,
            ),
            patch(
                "joulewise.analysis_engine.inputs._sha256_file",
                return_value="b" * 64,
            ),
            patch(
                "joulewise.analysis_engine.inputs.scientific_config_identity",
                return_value={"identity": "test"},
            ),
            patch(
                "joulewise.analysis_engine.inputs._calibration_order_tags",
                side_effect=lambda config: config["_order_tags"],
            ),
            patch(
                "joulewise.analysis_engine.inputs.anchor_fallback_member_unusable",
                return_value=False,
            ),
            patch(
                "joulewise.analysis_engine.inputs.custody_telemetry_identity",
                return_value=CustodyTelemetryIdentity(
                    custody_bound_config=True,
                    config_backend_class="powermetrics",
                    metadata_backend_class="powermetrics",
                    summary_backend_class="powermetrics",
                    triangle_agrees=True,
                ),
            ),
        ):
            binding = bind_floor_artifact_evidence(
                artifact,
                Path(tmp) / "floor.json",
                {
                    "a10": Path(tmp) / "a10",
                    "window_c": Path(tmp) / "window_c",
                },
                strict_validator=lambda path, strict: [],
            )
        return binding

    def test_mint_derived_folded_artifact_stack_binds_end_to_end(self):
        fixture = Path("tests/fixtures/d078_r01")
        metadata = json.loads(
            (fixture / "metadata.json").read_text(encoding="utf-8")
        )
        expected_stack = mint._derive_stack_identity(
            json.loads(
                (fixture / "config.json").read_text(encoding="utf-8")
            ),
            metadata,
        )
        expected_hash = canonical_domain_sha256(
            STACK_IDENTITY_DOMAIN,
            expected_stack,
        )

        binding = self._bind_mlx_file_set_floor(metadata)

        self.assertIn("cell-1", binding.bound_cell_ids)
        self.assertEqual(
            binding.cell_stack_identity_sha256["cell-1"],
            expected_hash,
        )
        self.assertFalse(
            any(
                "stack identity is unavailable" in problem
                for problem in binding.problems_by_cell["cell-1"]
            )
        )

    def test_folded_artifact_binding_keeps_missing_and_malformed_fail_closed(
        self,
    ):
        fixture = Path("tests/fixtures/d078_r01")
        valid = json.loads(
            (fixture / "metadata.json").read_text(encoding="utf-8")
        )
        missing = copy.deepcopy(valid)
        missing_artifact = missing["workload_provenance"]["model"][
            "artifact_identity"
        ]
        missing_artifact.pop("sha256", None)
        missing_artifact.pop("folded_sha256", None)
        malformed = copy.deepcopy(valid)
        malformed_artifact = malformed["workload_provenance"]["model"][
            "artifact_identity"
        ]
        malformed_artifact.pop("sha256", None)
        malformed_artifact["folded_sha256"] = "not-a-sha256"

        for label, metadata, should_bind in (
            ("valid", valid, True),
            ("missing", missing, False),
            ("malformed", malformed, False),
        ):
            with self.subTest(label=label):
                binding = self._bind_mlx_file_set_floor(metadata)
                if should_bind:
                    self.assertIn("cell-1", binding.bound_cell_ids)
                    self.assertFalse(
                        any(
                            "stack identity is unavailable" in problem
                            for problem in binding.problems_by_cell["cell-1"]
                        )
                    )
                else:
                    self.assertNotIn("cell-1", binding.bound_cell_ids)
                    self.assertTrue(
                        any(
                            "stack identity is unavailable" in problem
                            for problem in binding.problems_by_cell["cell-1"]
                        )
                    )

    def test_label_disagreement_is_strict_invalid_at_claim_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            bundle = runs_root / "member"
            shutil.copytree(Path("tests/fixtures/d078_r01"), bundle)
            summary_path = bundle / "summary_metrics.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["measurement_quality"]["telemetry_source"] = "mock"
            summary_path.write_text(
                json.dumps(summary, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            source_config = json.loads(
                (bundle / "config.json").read_text(encoding="utf-8")
            )
            with (
                patch(
                    "joulewise.analysis_engine.inputs._source_provenance_admission_problems",
                    return_value=(),
                ),
                patch(
                    "joulewise.analysis_engine.inputs._realized_identity_matches_config",
                    return_value=True,
                ),
            ):
                evidence = _read_bundle(
                    {},
                    bundle,
                    runs_root,
                    source_config,
                    strict_validator=lambda path, strict: (),
                )
        self.assertIn("bundle_strict_invalid", evidence.base_reason_codes)
        self.assertNotIn(
            MOCK_TELEMETRY_CLAIM_REFUSAL,
            evidence.base_reason_codes,
        )

    def test_honest_strict_mock_member_is_refused_at_claim_boundary(self):
        fixture = Path("tests/fixtures/axi_valid_burst")
        source_config = json.loads(
            (fixture / "config.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_bundle(fixture, strict=True), [])
        with (
            patch(
                "joulewise.analysis_engine.inputs._source_provenance_admission_problems",
                return_value=(),
            ),
            patch(
                "joulewise.analysis_engine.inputs._realized_identity_matches_config",
                return_value=True,
            ),
        ):
            evidence = _read_bundle(
                {},
                fixture,
                fixture.parent,
                source_config,
                strict_validator=lambda path, strict: validate_bundle(
                    path, strict=strict
                ),
            )
        self.assertEqual(
            evidence.base_reason_codes,
            (MOCK_TELEMETRY_CLAIM_REFUSAL,),
        )
        self.assertEqual(evidence.strict_problems, ())
        self.assertEqual(evidence.inclusion_status, "excluded")

    def test_floor_binding_rejects_comparative_abba_fallback_member(self):
        artifact = make_artifact()
        fallback_bundle_id = "cell-1-b0-A1"
        stack_identity = artifact["cells"][0]["source_regime"][
            "stack_identity"
        ]

        class FakeReader:
            def __init__(self, path):
                self.path = Path(path)

            def raw_summary(self):
                return {
                    "status": "succeeded",
                    "measurement_quality": {
                        "telemetry_source": "powermetrics"
                    },
                    "energy_uncertainty_status": "bounded",
                    "gross_energy_j": 100.0,
                }

            def raw_metadata(self):
                anchor = {"status": "bounded"}
                if self.path.name == fallback_bundle_id:
                    anchor["trace_fallback_method"] = (
                        "legacy_spawn_bracket_midpoint_v1"
                    )
                return {
                    "uncertainty_evidence": {"clock_anchor": anchor}
                }

            def raw_config(self):
                return {}

        with (
            tempfile.TemporaryDirectory() as tmp,
            patch(
                "joulewise.analysis_engine.inputs._campaign_order_binding_problems",
                return_value=(),
            ),
            patch(
                "joulewise.analysis_engine.inputs._source_provenance_admission_problems",
                return_value=(),
            ),
            patch(
                "joulewise.analysis_engine.inputs.BundleReader",
                FakeReader,
            ),
            patch(
                "joulewise.analysis_engine.inputs.complete_bundle_sha256",
                return_value="a" * 64,
            ),
            patch(
                "joulewise.analysis_engine.inputs._sha256_file",
                return_value="b" * 64,
            ),
            patch(
                "joulewise.analysis_engine.inputs.scientific_config_identity",
                return_value={"identity": "test"},
            ),
            patch(
                "joulewise.analysis_engine.inputs.floor_stack_identity",
                return_value=stack_identity,
            ),
            patch(
                "joulewise.analysis_engine.inputs.custody_telemetry_identity",
                return_value=CustodyTelemetryIdentity(
                    custody_bound_config=True,
                    config_backend_class="powermetrics",
                    metadata_backend_class="powermetrics",
                    summary_backend_class="powermetrics",
                    triangle_agrees=True,
                ),
            ),
        ):
            binding = bind_floor_artifact_evidence(
                artifact,
                Path(tmp) / "floor.json",
                Path(tmp) / "runs",
                strict_validator=lambda path, strict: [],
            )
        self.assertNotIn("cell-1", binding.bound_cell_ids)
        self.assertIn(
            ANCHOR_FALLBACK_MEMBER_REFUSAL,
            binding.problems_by_cell["cell-1"],
        )

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

    def test_partially_limited_transport_preserves_only_labelled_source(self):
        diagnostic = {
            "absolute": {
                "label": "repeatability_diagnostic",
                "published_claim_floor": False,
                "unguarded_floor_j": 0.4,
                "guard_factor": 1.5,
                "guarded_floor_j": 0.6,
            }
        }
        combined = _combined_floor(
            (
                FloorResolution(
                    status="transported",
                    artifact_id="df",
                    artifact_sha256=HEX,
                    source_cell_ids=("C1", "C2"),
                    transport_group_id="tg1",
                    transport_rule_id="rule",
                    floor_abs_j=0.5,
                    floor_cmp_j=1.0,
                    floor_gate_j=1.0,
                    reason_codes=(),
                    floor_source=ATTRIBUTION_FLOOR_SOURCE,
                    floor_limit_class=ATTRIBUTION_LIMIT_CLASS,
                    point_floor_diagnostics={"C1": diagnostic},
                    single_count_discipline=attribution_single_count_discipline(),
                ),
            )
        )
        self.assertEqual(
            combined["point_floor_diagnostics"],
            {"C1": diagnostic},
        )

        artifact = minimal_artifact()
        contrast = artifact["contrasts"][0]
        contrast["floor"] = combined
        contrast["claim_evaluation"]["floor_limit"] = {
            "floor_source": ATTRIBUTION_FLOOR_SOURCE,
            "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
            "published_floor_j": combined["active_floor_j"],
            "point_floor_diagnostics": combined["point_floor_diagnostics"],
            "single_count_discipline": attribution_single_count_discipline(),
        }
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
        self.assertEqual(validate_claim_verdicts(artifact), [])

    def test_multi_source_exact_resolution_is_rejected_at_both_boundaries(self):
        diagnostic_c1 = {
            "label": "repeatability_diagnostic",
            "published_claim_floor": False,
            "unguarded_floor_j": 0.4,
            "guard_factor": 1.5,
            "guarded_floor_j": 0.6,
        }
        diagnostic_c2 = {
            **diagnostic_c1,
            "unguarded_floor_j": 0.5,
            "guarded_floor_j": 0.75,
        }
        source_diagnostics = {
            "C1": diagnostic_c1,
            "C2": diagnostic_c2,
        }
        resolution = FloorResolution(
            status="exact",
            artifact_id="df",
            artifact_sha256=HEX,
            source_cell_ids=("C1", "C2"),
            transport_group_id=None,
            transport_rule_id="direct",
            floor_abs_j=0.5,
            floor_cmp_j=1.0,
            floor_gate_j=1.0,
            reason_codes=(),
            floor_source=ATTRIBUTION_FLOOR_SOURCE,
            floor_limit_class=ATTRIBUTION_LIMIT_CLASS,
            point_floor_diagnostics=source_diagnostics,
            single_count_discipline=attribution_single_count_discipline(),
        )

        with self.assertRaisesRegex(
            AnalysisInputError,
            "exact floor resolution must name exactly one source cell",
        ):
            _combined_floor((resolution,))

        artifact = minimal_artifact()
        contrast = artifact["contrasts"][0]
        wrongly_nested = {
            source_id: copy.deepcopy(source_diagnostics)
            for source_id in ("C1", "C2")
        }
        contrast["floor"] = {
            "status": "resolved",
            "floor_row_ids": ["C1", "C2"],
            "floor_abs_j": 0.5,
            "floor_cmp_j": 1.0,
            "active_floor_j": 1.0,
            "transport_verdict": "exact",
            "resolutions": [
                {
                    "status": "exact",
                    "source_cell_ids": ["C1", "C2"],
                    "transport_group_id": None,
                    "transport_rule_id": "direct",
                    "floor_abs_j": 0.5,
                    "floor_cmp_j": 1.0,
                    "floor_gate_j": 1.0,
                    "reason_codes": [],
                    "floor_source": ATTRIBUTION_FLOOR_SOURCE,
                    "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
                    "point_floor_diagnostics": source_diagnostics,
                    "single_count_discipline": (
                        attribution_single_count_discipline()
                    ),
                }
            ],
            "floor_source": ATTRIBUTION_FLOOR_SOURCE,
            "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
            "point_floor_diagnostics": wrongly_nested,
            "single_count_discipline": attribution_single_count_discipline(),
        }
        contrast["claim_evaluation"]["floor_limit"] = {
            "floor_source": ATTRIBUTION_FLOOR_SOURCE,
            "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
            "published_floor_j": 1.0,
            "point_floor_diagnostics": wrongly_nested,
            "single_count_discipline": attribution_single_count_discipline(),
        }
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)

        errors = validate_claim_verdicts(artifact)
        self.assertTrue(
            any(
                "exact resolution must name exactly one source cell" in error
                for error in errors
            ),
            errors,
        )

    def test_ratio_conversion_scales_labelled_point_floor_diagnostics(self):
        metric = {
            "ratio_estimand": {
                "form": "mean_of_request_ratios",
                "numerator_metric": "energy_request_j",
                "denominator": "runtime_observed_output_tokens",
                "denominator_unit": "token",
                "tokenizer_scope": "same_identity_required",
                "output_policy_scope": "same_policy_required",
            }
        }
        observations = tuple(
            RatioObservation(
                block_id=f"block-{index}",
                energy_a_j=1.0,
                energy_b_j=1.0,
                output_tokens_a=100,
                output_tokens_b=200,
                token_count_source_a="runtime_observed",
                token_count_source_b="runtime_observed",
                stop_reason_a="length",
                stop_reason_b="length",
                output_policy_a="fixed",
                output_policy_b="fixed",
                tokenizer_identity_a="tokenizer",
                tokenizer_identity_b="tokenizer",
            )
            for index in (1, 2)
        )
        leaf = {
            "label": "repeatability_diagnostic",
            "published_claim_floor": False,
            "unguarded_floor_j": 0.4,
            "guard_factor": 1.5,
            "guarded_floor_j": 0.6,
        }
        floor = {
            "status": "resolved",
            "floor_abs_j": 0.8,
            "floor_cmp_j": 0.8,
            "active_floor_j": 0.8,
            "point_floor_diagnostics": {
                source_id: {"absolute": copy.deepcopy(leaf)}
                for source_id in ("C1", "C2")
            },
            "resolutions": [
                {
                    "status": "exact",
                    "source_cell_ids": [source_id],
                    "floor_abs_j": 0.4,
                    "floor_cmp_j": 0.4,
                    "floor_gate_j": 0.4,
                    "point_floor_diagnostics": {"absolute": copy.deepcopy(leaf)},
                }
                for source_id in ("C1", "C2")
            ],
        }

        converted, reasons = convert_floor_to_ratio_units(
            metric,
            observations,
            floor,
        )

        self.assertEqual(reasons, ())
        self.assertAlmostEqual(
            converted["resolutions"][0]["point_floor_diagnostics"]["absolute"][
                "guarded_floor_j"
            ],
            0.006,
        )
        self.assertAlmostEqual(
            converted["resolutions"][1]["point_floor_diagnostics"]["absolute"][
                "guarded_floor_j"
            ],
            0.003,
        )
        self.assertAlmostEqual(
            converted["point_floor_diagnostics"]["C1"]["absolute"][
                "guarded_floor_j"
            ],
            0.006,
        )
        self.assertAlmostEqual(
            converted["point_floor_diagnostics"]["C1"]["absolute"][
                "unguarded_floor_j"
            ],
            0.004,
        )
        self.assertAlmostEqual(
            converted["point_floor_diagnostics"]["C2"]["absolute"][
                "guarded_floor_j"
            ],
            0.003,
        )
        self.assertEqual(
            floor["point_floor_diagnostics"]["C1"]["absolute"][
                "guarded_floor_j"
            ],
            0.6,
        )

    def test_ratio_conversion_refuses_conflicting_transport_diagnostic_scales(self):
        metric = {
            "ratio_estimand": {
                "form": "mean_of_request_ratios",
                "numerator_metric": "energy_request_j",
                "denominator": "runtime_observed_output_tokens",
                "denominator_unit": "token",
                "tokenizer_scope": "same_identity_required",
                "output_policy_scope": "same_policy_required",
            }
        }
        observations = (
            RatioObservation(
                block_id="block-1",
                energy_a_j=1.0,
                energy_b_j=1.0,
                output_tokens_a=100,
                output_tokens_b=200,
                token_count_source_a="runtime_observed",
                token_count_source_b="runtime_observed",
                stop_reason_a="length",
                stop_reason_b="length",
                output_policy_a="fixed",
                output_policy_b="fixed",
                tokenizer_identity_a="tokenizer",
                tokenizer_identity_b="tokenizer",
            ),
        )
        leaf = {
            "label": "repeatability_diagnostic",
            "published_claim_floor": False,
            "unguarded_floor_j": 0.4,
            "guard_factor": 1.5,
            "guarded_floor_j": 0.6,
        }
        source_diagnostics = {
            "C1": {"absolute": copy.deepcopy(leaf)}
        }
        floor = _combined_floor(
            tuple(
                FloorResolution(
                    status="transported",
                    artifact_id="df",
                    artifact_sha256=HEX,
                    source_cell_ids=("C1",),
                    transport_group_id="tg-1",
                    transport_rule_id=(
                        "same_stack_componentwise_worst_case.v1"
                    ),
                    floor_abs_j=0.4,
                    floor_cmp_j=0.4,
                    floor_gate_j=0.4,
                    reason_codes=(),
                    floor_source=ATTRIBUTION_FLOOR_SOURCE,
                    floor_limit_class=ATTRIBUTION_LIMIT_CLASS,
                    point_floor_diagnostics=copy.deepcopy(
                        source_diagnostics
                    ),
                    single_count_discipline=(
                        attribution_single_count_discipline()
                    ),
                )
                for _ in range(2)
            )
        )
        self.assertEqual(floor["active_floor_j"], 0.4)

        converted, reasons = convert_floor_to_ratio_units(
            metric,
            observations,
            floor,
        )

        self.assertEqual(reasons, ("ratio_floor_conversion_undefined",))
        self.assertEqual(converted["floor_abs_j"], 0.006)
        self.assertEqual(converted["floor_cmp_j"], 0.006)
        self.assertEqual(converted["active_floor_j"], 0.006)
        self.assertEqual(
            [
                resolution["floor_gate_j"]
                for resolution in converted["resolutions"]
            ],
            [0.004, 0.002],
        )
        self.assertEqual(
            converted["point_floor_diagnostics"],
            {
                "C1": {
                    "condition_a": {
                        "absolute": {
                            **leaf,
                            "unguarded_floor_j": 0.004,
                            "guarded_floor_j": 0.006,
                        }
                    },
                    "condition_b": {
                        "absolute": {
                            **leaf,
                            "unguarded_floor_j": 0.002,
                            "guarded_floor_j": 0.003,
                        }
                    },
                }
            },
        )
        self.assertEqual(floor["active_floor_j"], 0.4)

        zero_diagnostic_floor = copy.deepcopy(floor)
        for resolution in zero_diagnostic_floor["resolutions"]:
            diagnostic = resolution["point_floor_diagnostics"]["C1"][
                "absolute"
            ]
            diagnostic["unguarded_floor_j"] = 0.0
            diagnostic["guarded_floor_j"] = 0.0
        zero_published = zero_diagnostic_floor["point_floor_diagnostics"][
            "C1"
        ]["absolute"]
        zero_published["unguarded_floor_j"] = 0.0
        zero_published["guarded_floor_j"] = 0.0

        zero_converted, zero_reasons = convert_floor_to_ratio_units(
            metric,
            observations,
            zero_diagnostic_floor,
        )

        self.assertEqual(
            zero_reasons,
            ("ratio_floor_conversion_undefined",),
        )
        self.assertEqual(
            set(zero_converted["point_floor_diagnostics"]["C1"]),
            {"condition_a", "condition_b"},
        )

        artifact = minimal_artifact()
        contrast = artifact["contrasts"][0]
        contrast["metric"]["unit"] = "J/token"
        contrast["metric"]["ratio_estimand"] = metric["ratio_estimand"]
        contrast["floor"] = converted
        contrast["claim_evaluation"] = evaluate_claim(
            estimate=contrast["estimator"]["estimate"],
            metrology_aware_ci95=contrast["estimator"][
                "metrology_aware_CI95"
            ],
            decision_interval=contrast["deterministic_bounds"][
                "decision_interval"
            ],
            floor_gate_j=converted["active_floor_j"],
            adjusted_rejected=contrast["multiplicity"]["rejected"],
            base_reason_codes=reasons,
            floor_metadata={
                "floor_source": converted["floor_source"],
                "floor_limit_class": converted["floor_limit_class"],
                "point_floor_diagnostics": converted[
                    "point_floor_diagnostics"
                ],
                "single_count_discipline": converted[
                    "single_count_discipline"
                ],
            },
        )
        self.assertEqual(
            contrast["claim_evaluation"]["outcome"],
            "not_resolvable",
        )
        self.assertFalse(
            contrast["claim_evaluation"]["claim_ready_for_l2_l3"]
        )

        published = finalize_claim_verdicts(artifact)

        self.assertEqual(validate_claim_verdicts(published), [])
        self.assertEqual(
            published["contrasts"][0]["floor"]["active_floor_j"],
            0.006,
        )
        self.assertEqual(
            published["contrasts"][0]["claim_evaluation"]["reason_codes"],
            ["ratio_floor_conversion_undefined"],
        )

        omitted_reason = copy.deepcopy(published)
        omitted_contrast = omitted_reason["contrasts"][0]
        omitted_floor = omitted_contrast["floor"]
        omitted_contrast["claim_evaluation"] = evaluate_claim(
            estimate=omitted_contrast["estimator"]["estimate"],
            metrology_aware_ci95=omitted_contrast["estimator"][
                "metrology_aware_CI95"
            ],
            decision_interval=omitted_contrast["deterministic_bounds"][
                "decision_interval"
            ],
            floor_gate_j=omitted_floor["active_floor_j"],
            adjusted_rejected=omitted_contrast["multiplicity"]["rejected"],
            base_reason_codes=(),
            floor_metadata={
                "floor_source": omitted_floor["floor_source"],
                "floor_limit_class": omitted_floor["floor_limit_class"],
                "point_floor_diagnostics": omitted_floor[
                    "point_floor_diagnostics"
                ],
                "single_count_discipline": omitted_floor[
                    "single_count_discipline"
                ],
            },
        )
        omitted_reason["claim_verdicts_id"] = calculate_claim_verdicts_id(
            omitted_reason
        )

        omitted_errors = validate_claim_verdicts(omitted_reason)

        self.assertTrue(
            any(
                "ratio diagnostic collision requires "
                "ratio_floor_conversion_undefined"
                in error
                for error in omitted_errors
            ),
            omitted_errors,
        )

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

        # 0.4.0 is an unknown wire; 0.5.0 with the v1 method is a CROSSED
        # pair under the T0.3 exact matrix — both fail closed.
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

    def test_t03_exact_reducer_idle_method_pair_matrix(self):
        """Every allowed pair passes; every crossed or unknown pair fails."""

        v1 = "newey_west_bartlett_10s_iid_floor_v1"
        v2 = "duration_weighted_newey_west_bartlett_10s_iid_floor_v2"
        self.assertEqual(
            dict(GOVERNED_REDUCER_IDLE_METHOD_PAIRS),
            {
                "0.4.1": v1,
                "0.4.2": v1,
                "0.5.0": v2,
                "0.5.2": v2,
                "0.6.0": v2,
                "0.6.2": v2,
            },
        )

        def variance_for(reducer_version, method):
            evidence = BundleEvidence(
                entry={},
                bundle_id="bundle",
                relative_path="bundle",
                path=Path("bundle"),
                summary={
                    "summary_provenance": {"reducer_version": reducer_version},
                    "idle_mean_uncertainty": {
                        "status": "estimated",
                        "method": method,
                        "correlation_scope": "independent_run",
                    },
                    "energy_variance_terms_j2": {"E_idle_mean_j2": 2.5},
                },
                metadata={},
                raw_config={},
                strict_problems=(),
                base_reason_codes=(),
                config_sha256=HEX,
                summary_sha256=HEX,
                replacement_classification="registered",
                inclusion_status="included",
            )
            return governed_stochastic_variance(
                evidence, {"name": "energy_request_j"}
            )

        for reducer_version, method in GOVERNED_REDUCER_IDLE_METHOD_PAIRS.items():
            with self.subTest(pair=(reducer_version, method)):
                terms, reasons = variance_for(reducer_version, method)
                self.assertEqual(reasons, ())
                self.assertEqual(terms[0]["variance"], 2.5)

        crossed = [
            ("0.4.1", v2),
            ("0.4.2", v2),
            ("0.5.0", v1),
            ("0.5.1", v1),
            ("0.6.0", v1),
            ("0.6.1", v1),
            ("0.4.3", v1),
            ("0.7.0", v2),
            ("0.5.1", "some_future_method_v3"),
        ]
        for reducer_version, method in crossed:
            with self.subTest(pair=(reducer_version, method)):
                terms, reasons = variance_for(reducer_version, method)
                self.assertEqual(terms, ())
                self.assertEqual(reasons, ("required_error_term_unknown",))

    def test_cooldown_disposition_matches_controller_over_boolean_grid(self):
        from joulewise.analysis_engine.inputs import _cooldown_result_from_raw
        from joulewise.cooldown import cooldown_disposition_from_raw

        expected = {
            (False, False): "cap_hit",
            (False, True): "cap_hit",
            (True, False): "recovered",
            (True, True): None,
        }
        for terminal_state, disposition in expected.items():
            with self.subTest(terminal_state=terminal_state):
                terminal = {
                    "release": terminal_state[0],
                    "release_criteria_met_late": terminal_state[1],
                }
                self.assertEqual(
                    cooldown_disposition_from_raw([terminal]), disposition
                )
                self.assertEqual(_cooldown_result_from_raw([terminal]), disposition)

    def test_t03_exact_stored_recal4_sentinel_wire_is_consumable(self):
        """The byte-exact stored 0.5.0 corpus wire yields the governed term."""

        summary = sentinel_stored_wire()
        provenance = summary["summary_provenance"]
        self.assertEqual(provenance["reducer_version"], "0.5.0")
        self.assertEqual(
            summary["idle_mean_uncertainty"]["method"],
            "duration_weighted_newey_west_bartlett_10s_iid_floor_v2",
        )
        evidence = BundleEvidence(
            entry={},
            bundle_id="p2015-df-su-sentinel-abs-r01",
            relative_path="p2015-df-su-sentinel-abs-r01",
            path=Path("p2015-df-su-sentinel-abs-r01"),
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
        terms, reasons = governed_stochastic_variance(
            evidence, {"name": "energy_request_j"}
        )
        self.assertEqual(reasons, ())
        self.assertEqual(
            terms,
            (
                {
                    "name": "E_idle_mean_j2",
                    "variance": summary["energy_variance_terms_j2"]["E_idle_mean_j2"],
                    "correlation_scope": "independent_run",
                },
            ),
        )
        # The stored wire predates the anchor fix: deterministic bounds must
        # NOT invent an anchor term, and must not refuse for lacking one.
        bounds, bound_reasons = deterministic_bounds(
            evidence,
            {"name": "gross_energy_j", "metric_tag": "gross_request", "window_class": "request"},
        )
        self.assertNotIn("E_clock_anchor_shift_bound_j", bounds)
        self.assertNotIn("anchor_energy_envelope_unrecorded", bound_reasons)

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

    def test_engine_consumes_corner_widened_guarded_floor(self):
        cell = make_cell(
            energies=[0.0, 1.0, -1.0, 0.0, 0.0],
            deltas=[0.0] * 5,
            absolute_half_widths=[0.01] * 5,
        )
        artifact = make_artifact([cell])
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
        self.assertEqual(resolution.floor_gate_j, 3.2578982723565812)

    def test_engine_consumes_whole_window_drift_widened_floor(self):
        allowance = whole_window_allowance()
        cell = make_cell(
            energies=[0.0, 1.0, -1.0, 0.0, 0.0],
            deltas=[0.0] * 5,
            absolute_half_widths=[0.01] * 5,
            whole_window_drift_allowance=allowance,
        )
        artifact = make_artifact([cell])
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
        expected = max(
            cell["absolute"]["drift_widened_guarded_floor_j"],
            cell["comparative"]["drift_widened_guarded_floor_j"],
        )
        self.assertEqual(resolution.floor_gate_j, expected)
        self.assertEqual(
            expected,
            max(
                cell["absolute"]["corner_widened_guarded_floor_j"],
                cell["comparative"]["corner_widened_guarded_floor_j"],
            )
            + allowance["allowance_j"],
        )

    def test_engine_consumes_comparative_widened_floor_as_operative_gate(self):
        deltas = [1.0, -1.0, 0.0, 0.0, 0.0]
        cell = make_cell(
            energies=[0.0] * 5,
            deltas=deltas,
            comparative_half_widths=[0.5] * 5,
        )
        artifact = make_artifact([cell])
        artifact["calibration_scope"] = "window_a"
        widened = cell["comparative"]["corner_widened_guarded_floor_j"]
        point = comparative_false_effect_floor(
            deltas, admissible_half_widths_j=[0.0] * len(deltas)
        ).guarded_floor_j
        self.assertGreater(widened, point)

        # The nested widened record is authoritative at the consumption seam;
        # a stale denormalized scalar must not shrink the operative gate.
        artifact["cells"][0]["floor_cmp_j"] = point
        consumer = make_consumer(
            condition_family_id=cell["key"]["condition_family_id"],
            condition_family_sha256=cell["key"]["condition_family_sha256"],
        )
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
        self.assertEqual(resolution.status, "exact")
        self.assertEqual(resolution.floor_cmp_j, widened)
        self.assertEqual(resolution.floor_gate_j, widened)

    def test_labelled_floor_resolves_and_remains_claim_bearing(self):
        cell = make_cell(
            energies=[0.0] * 5,
            deltas=[0.0] * 5,
            absolute_half_widths=[0.5] * 5,
            comparative_half_widths=[0.5] * 5,
        )
        artifact = make_artifact([cell])
        artifact["calibration_scope"] = "window_a"
        consumer = make_consumer(
            condition_family_id=cell["key"]["condition_family_id"],
            condition_family_sha256=cell["key"]["condition_family_sha256"],
        )
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
        self.assertEqual(resolution.status, "exact")
        self.assertEqual(
            resolution.floor_limit_class,
            ATTRIBUTION_LIMIT_CLASS,
        )
        self.assertEqual(resolution.floor_source, ATTRIBUTION_FLOOR_SOURCE)
        self.assertEqual(
            resolution.single_count_discipline,
            attribution_single_count_discipline(),
        )
        self.assertIsNotNone(resolution.point_floor_diagnostics)
        result = evaluate_claim(
            estimate=10.0,
            metrology_aware_ci95={"lower": 9.5, "upper": 10.5},
            decision_interval={"lower": 9.25, "upper": 10.75},
            floor_gate_j=resolution.floor_gate_j,
            adjusted_rejected=True,
            floor_metadata={
                "floor_limit_class": resolution.floor_limit_class,
                "floor_source": resolution.floor_source,
                "point_floor_diagnostics": resolution.point_floor_diagnostics,
                "single_count_discipline": (
                    resolution.single_count_discipline
                ),
            },
        )
        self.assertEqual(result["outcome"], "direction_supported")
        self.assertTrue(result["claim_ready_for_l2_l3"])
        self.assertEqual(
            result["floor_limit"]["single_count_discipline"],
            attribution_single_count_discipline(),
        )
        self.assertEqual(
            result["floor_limit"]["published_floor_j"],
            resolution.floor_gate_j,
        )

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


def _bounds_evidence(summary: dict) -> BundleEvidence:
    return BundleEvidence(
        entry={},
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


class AnchorBoundPropagationTests(unittest.TestCase):
    """T0.6: current anchor-envelope fields become deterministic bounds."""

    GROSS_METRIC = {
        "name": "gross_energy_j",
        "metric_tag": "gross_request",
        "window_class": "request",
    }

    def _summary(self, reducer_version: str = "0.5.2", **overrides) -> dict:
        summary = {
            "summary_provenance": {"reducer_version": reducer_version},
            "gross_energy_j": 40.0,
            "energy_bound_terms_j": {
                "E_interpolation_joint_edge_bound_j": 0.02,
                "E_drift_bound_j": 0.0,
                "E_clock_anchor_shift_bound_j": 0.05,
            },
            "energy_anchor_shift_envelopes": {
                "/gross_energy_j": {
                    "method": "common_trace_shift_plus_independent_edge_corners_v3",
                    "anchor_bound_s": 0.05,
                    "point_j": 40.0,
                    "lower_j": 39.96,
                    "upper_j": 40.03,
                    "max_abs_delta_j": 0.04,
                }
            },
        }
        summary.update(overrides)
        return summary

    def test_current_v3_anchor_wire_propagates_larger_envelope_or_scalar(self):
        bounds, reasons = deterministic_bounds(
            _bounds_evidence(self._summary()), self.GROSS_METRIC
        )
        self.assertEqual(reasons, ())
        self.assertEqual(bounds["E_clock_anchor_shift_bound_j"], 0.05)
        # Interpolation stays a SEPARATE term; never folded into the anchor.
        self.assertEqual(bounds["E_interpolation_joint_edge_bound_j"], 0.02)

    def test_current_mint_refuses_replay_only_v1_and_v2_envelope_methods(self):
        for reducer_version in ("0.5.2", "0.6.2"):
            for method in (
                "common_trace_shift_interval_overlap_v1",
                "common_trace_shift_plus_independent_edge_span_v2",
            ):
                with self.subTest(
                    reducer_version=reducer_version, method=method
                ):
                    summary = self._summary(reducer_version=reducer_version)
                    summary["energy_anchor_shift_envelopes"][
                        "/gross_energy_j"
                    ]["method"] = method
                    envelope, problem = anchor_shift_envelope(
                        summary, "gross_energy_j"
                    )
                    self.assertIsNone(problem)
                    self.assertEqual(envelope["method"], method)
                    bounds, reasons = deterministic_bounds(
                        _bounds_evidence(summary), self.GROSS_METRIC
                    )
                    self.assertNotIn("E_clock_anchor_shift_bound_j", bounds)
                    self.assertIn("clock_anchor_unresolved", reasons)
                    self.assertNotIn(
                        "anchor_energy_envelope_unrecorded", reasons
                    )

    def test_reducer_v2_golden_envelope_propagates_end_to_end(self):
        # F3 defect shape: reducer 0.5.2 emits v2, but the consumer formerly
        # accepted only v1 and silently turned this committed golden malformed.
        summary = json.loads(
            Path("tests/goldens/d078_r01_reducer_052.json").read_text(
                encoding="utf-8"
            )
        )
        envelope, problem = anchor_shift_envelope(summary, "gross_energy_j")
        self.assertIsNone(problem)
        self.assertEqual(
            envelope["method"],
            "common_trace_shift_plus_independent_edge_corners_v3",
        )
        bounds, reasons = deterministic_bounds(
            _bounds_evidence(summary), self.GROSS_METRIC
        )
        self.assertEqual(reasons, ())
        self.assertEqual(
            bounds["E_clock_anchor_shift_bound_j"],
            max(
                envelope["max_abs_delta_j"],
                summary["energy_bound_terms_j"]["E_clock_anchor_shift_bound_j"],
            ),
        )

    def test_reducer_mint_method_is_registered_by_every_consumer(self):
        from joulewise.reduce import ANCHOR_SHIFT_METHOD
        from joulewise.analysis_engine.inputs import ANCHOR_SHIFT_ENVELOPE_METHODS

        self.assertIn(ANCHOR_SHIFT_METHOD, ANCHOR_SHIFT_ENVELOPE_METHODS)

    def test_v1_remains_registered_and_unknown_method_is_malformed(self):
        summary = self._summary()
        summary["energy_anchor_shift_envelopes"]["/gross_energy_j"][
            "method"
        ] = "common_trace_shift_interval_overlap_v1"
        envelope, problem = anchor_shift_envelope(summary, "gross_energy_j")
        self.assertIsNone(problem)
        self.assertEqual(
            envelope["method"], "common_trace_shift_interval_overlap_v1"
        )
        summary["energy_anchor_shift_envelopes"]["/gross_energy_j"][
            "method"
        ] = "common_trace_shift_typo_v99"
        envelope, problem = anchor_shift_envelope(summary, "gross_energy_j")
        self.assertIsNone(envelope)
        self.assertEqual(problem, "malformed")

    def test_anchor_wire_without_envelope_fails_closed(self):
        summary = self._summary()
        del summary["energy_anchor_shift_envelopes"]
        bounds, reasons = deterministic_bounds(
            _bounds_evidence(summary), self.GROSS_METRIC
        )
        self.assertNotIn("E_clock_anchor_shift_bound_j", bounds)
        self.assertIn("anchor_energy_envelope_unrecorded", reasons)

    def test_anchor_wire_without_request_scalar_fails_closed(self):
        summary = self._summary()
        del summary["energy_bound_terms_j"]["E_clock_anchor_shift_bound_j"]
        bounds, reasons = deterministic_bounds(
            _bounds_evidence(summary), self.GROSS_METRIC
        )
        self.assertNotIn("E_clock_anchor_shift_bound_j", bounds)
        self.assertIn("anchor_energy_envelope_unrecorded", reasons)

    def test_malformed_envelope_fails_closed_even_on_pre_anchor_wires(self):
        summary = self._summary(reducer_version="0.4.2")
        envelope = summary["energy_anchor_shift_envelopes"]["/gross_energy_j"]
        envelope["max_abs_delta_j"] = 0.001  # understates its own reach
        bounds, reasons = deterministic_bounds(
            _bounds_evidence(summary), self.GROSS_METRIC
        )
        self.assertNotIn("E_clock_anchor_shift_bound_j", bounds)
        self.assertIn("anchor_energy_envelope_unrecorded", reasons)

    def test_pre_anchor_04x_wires_carry_the_universal_claim_barrier(self):
        # Confirmation-round-4 P0 inversion: 0.4.x anchors are exactly as
        # defective as 0.5.0's, so the universal D-078 barrier must fire —
        # the former empty-reasons assertion asserted the escape hatch.
        for reducer_version in ("0.4.1", "0.4.2"):
            with self.subTest(reducer_version=reducer_version):
                summary = self._summary(reducer_version=reducer_version)
                del summary["energy_anchor_shift_envelopes"]
                del summary["energy_bound_terms_j"][
                    "E_clock_anchor_shift_bound_j"
                ]
                bounds, reasons = deterministic_bounds(
                    _bounds_evidence(summary), self.GROSS_METRIC
                )
                self.assertNotIn("E_clock_anchor_shift_bound_j", bounds)
                self.assertIn("clock_anchor_unresolved", reasons)

    def test_point_anchor_wires_always_refuse_even_when_all_observations_are_old(self):
        # W3 defect shape: the mixed-wire guard only noticed an anchor term on
        # one side, so an all-0.5.0/all-0.6.0 analysis silently dropped D-078.
        for reducer_version in ("0.5.0", "0.6.0"):
            with self.subTest(reducer_version=reducer_version):
                summary = self._summary(reducer_version=reducer_version)
                del summary["energy_anchor_shift_envelopes"]
                del summary["energy_bound_terms_j"]["E_clock_anchor_shift_bound_j"]
                _bounds, reasons = deterministic_bounds(
                    _bounds_evidence(summary), self.GROSS_METRIC
                )
                self.assertIn("clock_anchor_unresolved", reasons)

    def test_superseded_anchor_composition_wire_refuses_by_version(self):
        # T3 defect shape: 0.5.1 formerly consumed its stored max-composed
        # envelope exactly like 0.5.2.  It remains parseable, but claim use is
        # barred by version and is not mislabeled as malformed envelope data.
        summary = self._summary(reducer_version="0.5.1")
        summary["energy_anchor_shift_envelopes"]["/gross_energy_j"][
            "method"
        ] = "common_trace_shift_plus_independent_edge_span_v2"
        envelope, problem = anchor_shift_envelope(summary, "gross_energy_j")
        self.assertIsNone(problem)
        self.assertEqual(
            envelope["method"],
            "common_trace_shift_plus_independent_edge_span_v2",
        )
        bounds, reasons = deterministic_bounds(
            _bounds_evidence(summary), self.GROSS_METRIC
        )
        self.assertNotIn("E_clock_anchor_shift_bound_j", bounds)
        self.assertIn("clock_anchor_unresolved", reasons)
        self.assertNotIn("anchor_energy_envelope_unrecorded", reasons)

        current_bounds, current_reasons = deterministic_bounds(
            _bounds_evidence(self._summary(reducer_version="0.5.2")),
            self.GROSS_METRIC,
        )
        self.assertNotIn("clock_anchor_unresolved", current_reasons)
        self.assertEqual(current_bounds["E_clock_anchor_shift_bound_j"], 0.05)

    def test_phase_envelope_propagates_through_the_phase_pointer(self):
        summary = {
            "summary_provenance": {"reducer_version": "0.5.2"},
            "phase_energy_j": {"prefill": 5.0},
            "window_evidence_precheck": {
                "phase": {
                    "prefill": {
                        "eligible": True,
                        "reasons": [],
                        "windows": [{"interpolation_joint_edge_bound_j": 0.01}],
                    }
                }
            },
            "energy_anchor_shift_envelopes": {
                "/phase_energy_j/prefill": {
                    "method": "common_trace_shift_plus_independent_edge_corners_v3",
                    "anchor_bound_s": 0.05,
                    "point_j": 5.0,
                    "lower_j": 4.9,
                    "upper_j": 5.05,
                    "max_abs_delta_j": 0.1,
                }
            },
        }
        bounds, reasons = deterministic_bounds(
            _bounds_evidence(summary),
            {
                "name": "phase_energy_j.prefill",
                "metric_tag": "gross_prefill",
                "window_class": "phase",
            },
        )
        self.assertEqual(reasons, ())
        self.assertEqual(bounds["E_clock_anchor_shift_bound_j"], 0.1)

    def test_envelope_pass_never_makes_a_contrast_identifiable_by_itself(self):
        """The contrast consumes the anchor bound explicitly (T0.6)."""

        term = DeterministicBoundTerm(
            "E_clock_anchor_shift_bound_j", bound_a=0.6, bound_b=0.6
        )
        observations = tuple(
            PairedObservation(
                f"b-{index}", 100.0, 101.0, deterministic_terms=(term,)
            )
            for index in range(5)
        )
        estimate = estimate_paired_blocks(observations)
        # Effect 1.0 J with a 1.2 J anchor bound: the decision interval
        # crosses zero even though every member passed its envelope gate.
        self.assertLess(estimate.decision_interval.lower, 0.0)
        self.assertGreater(estimate.metrology_aware_ci95.lower, 0.0)

    def test_whole_window_allowance_is_one_named_contrast_term(self):
        allowance = whole_window_allowance(value=0.6, observed=0.5, derived=0.6)
        evidence = _bounds_evidence(self._summary())
        evidence.whole_window_drift_allowances = {
            "gross_energy": allowance
        }
        bounds, reasons = deterministic_bounds(evidence, self.GROSS_METRIC)
        self.assertEqual(reasons, ())
        self.assertEqual(bounds["E_whole_window_drift_allowance_j"], 0.3)

        term = DeterministicBoundTerm(
            "E_whole_window_drift_allowance_j",
            bound_a=bounds["E_whole_window_drift_allowance_j"],
            bound_b=bounds["E_whole_window_drift_allowance_j"],
        )
        estimate = estimate_paired_blocks(
            tuple(
                PairedObservation(
                    f"b-{index}",
                    100.0,
                    101.0,
                    deterministic_terms=(term,),
                )
                for index in range(5)
            )
        )
        self.assertEqual(
            {
                row.name: row.bound
                for row in estimate.deterministic_bounds
            }["E_whole_window_drift_allowance_j"],
            0.6,
        )

    def test_required_whole_window_allowance_missing_refuses_metric(self):
        evidence = _bounds_evidence(self._summary())
        evidence.whole_window_drift_allowance_required = True
        bounds, reasons = deterministic_bounds(evidence, self.GROSS_METRIC)
        self.assertNotIn("E_whole_window_drift_allowance_j", bounds)
        self.assertIn(
            "whole_window_drift_allowance_unrecorded",
            reasons,
        )
        self.assertIn(
            "whole_window_drift_allowance_unrecorded",
            REDUCER_REASON_CODES,
        )
        result = evaluation(base_reason_codes=reasons)
        self.assertEqual(result["outcome"], "not_resolvable")
        self.assertFalse(result["claim_ready_for_l2_l3"])

    def test_new_anchor_reason_codes_are_registered_and_not_resolvable(self):
        added = {
            "clock_anchor_unresolved",
            "anchor_energy_envelope_unrecorded",
            "anchor_energy_envelope_exceeds_quarter_metric",
            "calibration_bracket_exceeds_minted_bound",
        }
        self.assertLessEqual(added, REASON_CODES)
        self.assertEqual(sorted(added), ordered_reason_codes(added))
        for reason in sorted(added):
            with self.subTest(reason=reason):
                result = evaluation(base_reason_codes=[reason])
                self.assertEqual(result["outcome"], "not_resolvable")
                self.assertFalse(result["claim_ready_for_l2_l3"])

    def test_stored_precheck_carrying_anchor_reasons_stays_readable(self):
        """A 0.5.1 precheck with the new barrier reasons must not collapse
        into ``window_evidence_precheck_missing`` — and no amount of clean
        source provenance may override the metric-level failure."""

        evidence = _bounds_evidence(
            {
                "status": "succeeded",
                "window_evidence_precheck": {
                    "gross_request": {
                        "eligible": False,
                        "reasons": ["clock_anchor_unresolved"],
                    }
                },
                "measurement_quality": {"cooldown_cap_hit": False},
            }
        )
        result = window_evidence_precheck(evidence, dict(self.GROSS_METRIC))
        self.assertFalse(result["eligible"])
        self.assertIn("clock_anchor_unresolved", result["reasons"])
        self.assertNotIn("window_evidence_precheck_missing", result["reasons"])


class MetricWindowHygieneTests(unittest.TestCase):
    """T0.6 (audit P1.4): metric/window crossings fail loudly."""

    def test_phase_window_with_gross_metric_fails_loudly(self):
        with self.assertRaisesRegex(AnalysisInputError, "phase_energy_j"):
            metric_value(
                {"gross_energy_j": 40.0},
                {"name": "gross_energy_j", "window_class": "phase"},
            )

    def test_phase_path_with_request_window_fails_loudly(self):
        with self.assertRaisesRegex(AnalysisInputError, "phase path"):
            metric_value(
                {"phase_energy_j": {"prefill": 5.0}},
                {"name": "phase_energy_j.prefill", "window_class": "request"},
            )

    def test_legacy_throughput_field_is_never_extracted(self):
        with self.assertRaisesRegex(
            AnalysisInputError, "inter_token_throughput_tokens_s"
        ):
            metric_value(
                {"throughput_tokens_s": 225.0},
                {"name": "throughput_tokens_s", "window_class": "request"},
            )

    def test_consistent_pairs_still_extract(self):
        self.assertEqual(
            metric_value(
                {"phase_energy_j": {"decode": 7.5}},
                {"name": "phase_energy_j.decode", "window_class": "phase"},
            ),
            7.5,
        )
        self.assertEqual(
            metric_value(
                {"gross_energy_j": 40.0},
                {"name": "gross_energy_j", "window_class": "request"},
            ),
            40.0,
        )


class ClaimArtifactTests(unittest.TestCase):
    def test_d093_divergence_cannot_be_rehashed_around_estimation_precedence(self):
        artifact = minimal_artifact()
        artifact["supersession_audit"] = [
            {
                "scope": "analysis_corpus",
                "evidence_root_id": None,
                "authenticated_basis": {
                    "kind": "whole_window_evaluation_basis_sha256",
                    "sha256": HEX,
                },
                "raw_count": 2,
                "validated_count": 1,
                "status": "refused",
            },
            {
                "scope": "floor_evidence",
                "evidence_root_id": "floor-root",
                "authenticated_basis": {
                    "kind": "floor_component_campaign_log_sha256",
                    "sha256s": [HEX],
                },
                "raw_count": 0,
                "validated_count": 0,
                "status": "clean",
            },
        ]
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
        errors = validate_claim_verdicts(artifact)
        self.assertTrue(
            any("supersession refusal forbids estimation" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("supersession refusal must take precedence" in error for error in errors),
            errors,
        )

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
