"""Public manifest-policy and artifact round trips for P2-037 B8."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from joulewise.analysis_engine import (
    estimate_manifest_observations,
    ratio_collection_evidence_reasons,
    ratio_observation_from_evidence,
)
from joulewise.analysis_engine.artifact import (
    calculate_claim_verdicts_id,
    finalize_claim_verdicts,
    render_claim_verdicts,
    validate_claim_verdicts,
)
from joulewise.analysis_engine.estimators import Interval, PairedEstimate
from joulewise.analysis_engine.inputs import BundleEvidence, token_provenance
from joulewise.analysis_engine.claims import evaluate_claim
from joulewise.analysis_engine.ratio import convert_floor_to_ratio_units
from tests.test_analysis_claims import minimal_artifact


def ratio_metric(form: str) -> dict[str, object]:
    return {
        "name": "energy_output_token_j",
        "metric_tag": "energy_output_token",
        "window_class": "idle_subtracted_request",
        "unit": "J/token",
        "ratio_estimand": {
            "form": form,
            "numerator_metric": "energy_request_j",
            "denominator": "runtime_observed_output_tokens",
            "denominator_unit": "token",
            "tokenizer_scope": "same_identity_required",
            "output_policy_scope": "same_policy_required",
        },
    }


def provenance(
    tokens: int = 100,
    *,
    source: str = "runtime_observed",
    tokenizer: str = "tok-a",
    policy: str = "fixed-100",
    stop_reason: str = "requested_tokens_emitted",
) -> dict[str, object]:
    return {
        "output_tokens": tokens,
        "token_count_source": source,
        "stop_reason": stop_reason,
        "output_policy": {
            "name": policy,
            "requested_tokens": 100,
            "emitted_tokens": tokens,
            "sampler": {"kind": "greedy", "temperature": 0.0},
        },
        "tokenizer_identity": {"name": tokenizer, "revision": "sha256:test"},
    }


def observation(
    block_id: str,
    energy_b: float,
    tokens: int,
):
    value, reasons = ratio_observation_from_evidence(
        block_id=block_id,
        energy_a_j=0.0,
        energy_b_j=energy_b,
        provenance_a=provenance(tokens),
        provenance_b=provenance(tokens),
    )
    if value is None:  # pragma: no cover - fixture construction assertion
        raise AssertionError(reasons)
    return value


def interval(value: Interval) -> dict[str, float]:
    return {"lower": value.lower, "upper": value.upper}


def estimator_row(value: PairedEstimate) -> dict[str, object]:
    return {
        "name": value.estimator,
        "n": value.n,
        "df": value.df,
        "estimate": value.estimate,
        "s_d": value.sample_stddev,
        "SE_repeat": value.se_repeat,
        "SE_metrology": value.se_metrology,
        "SE_total": value.se_total,
        "t_critical_95": value.t_critical_95,
        "repeat_point_CI95": interval(value.repeat_point_ci95),
        "metrology_aware_CI95": interval(value.metrology_aware_ci95),
        "variance_contributions": [asdict(term) for term in value.variance_contributions],
        "excluded_stochastic_terms": list(value.excluded_stochastic_terms),
        "raw_p": value.raw_p,
    }


class RatioManifestPolicyTests(unittest.TestCase):
    def test_ratio_floor_is_converted_from_joules_before_claim_comparison(self) -> None:
        values = (
            observation("block-1", energy_b=0.15, tokens=1),
            observation("block-2", energy_b=0.15, tokens=1),
        )
        floor = {
            "status": "resolved",
            "floor_row_ids": ["floor-a", "floor-b"],
            "floor_abs_j": 0.1,
            "floor_cmp_j": 0.1,
            "active_floor_j": 0.1,
            "transport_verdict": "exact",
            "resolutions": [
                {
                    "status": "exact",
                    "source_cell_ids": [floor_id],
                    "transport_group_id": None,
                    "transport_rule_id": "direct",
                    "floor_abs_j": 0.1,
                    "floor_cmp_j": 0.1,
                    "floor_gate_j": 0.1,
                    "reason_codes": [],
                }
                for floor_id in ("floor-a", "floor-b")
            ],
        }

        # The pre-fix mixed-unit comparison admitted 0.15 J/token above a
        # numeric 0.1 J floor.  With one token on each side the two numerator
        # floor contributions sum to 0.2 J/token, so the claim is unresolved.
        converted, reasons = convert_floor_to_ratio_units(
            ratio_metric("mean_of_request_ratios"), values, floor
        )
        result = evaluate_claim(
            estimate=0.15,
            metrology_aware_ci95={"lower": 0.14, "upper": 0.16},
            decision_interval={"lower": 0.14, "upper": 0.16},
            floor_gate_j=converted["active_floor_j"],
            adjusted_rejected=True,
            base_reason_codes=reasons,
        )

        self.assertEqual(converted["active_floor_j"], 0.2)
        self.assertEqual(result["outcome"], "not_resolvable")
        self.assertIn("effect_not_above_floor", result["reason_codes"])

    def test_public_dispatch_uses_each_predeclared_form(self) -> None:
        values = (
            observation("block-1", energy_b=10.0, tokens=100),
            observation("block-2", energy_b=40.0, tokens=200),
        )
        mean_ratios = estimate_manifest_observations(
            ratio_metric("mean_of_request_ratios"), values
        )
        ratio_totals = estimate_manifest_observations(
            ratio_metric("ratio_of_totals"), values
        )

        self.assertAlmostEqual(mean_ratios.estimate, (0.1 + 0.2) / 2.0)
        self.assertAlmostEqual(ratio_totals.estimate, 50.0 / 300.0)
        self.assertEqual(mean_ratios.ratio_estimand, "mean_of_request_ratios")
        self.assertEqual(ratio_totals.ratio_estimand, "ratio_of_totals")
        self.assertNotEqual(mean_ratios.estimate, ratio_totals.estimate)

    def test_form_must_be_frozen_before_observations_are_dispatched(self) -> None:
        metric = ratio_metric("mean_of_request_ratios")
        metric["ratio_estimand"] = dict(metric["ratio_estimand"])  # type: ignore[arg-type]
        metric["ratio_estimand"].pop("form")  # type: ignore[union-attr]
        values = (
            observation("block-1", energy_b=10.0, tokens=100),
            observation("block-2", energy_b=10.0, tokens=100),
        )
        with self.assertRaisesRegex(ValueError, "exact adjudicated B8 object"):
            estimate_manifest_observations(metric, values)

    def test_missing_or_configured_denominator_and_tokenizer_mismatch_fail_closed(self) -> None:
        cases = {
            "missing token count": (
                {**provenance(), "output_tokens": None},
                provenance(),
                "runtime_token_denominator_required",
            ),
            "configured token source": (
                provenance(source="config_fallback"),
                provenance(),
                "runtime_token_denominator_required",
            ),
            "tokenizer mismatch": (
                provenance(tokenizer="tok-a"),
                provenance(tokenizer="tok-b"),
                "tokenizer_identity_mismatch",
            ),
            "output policy mismatch": (
                provenance(policy="fixed-100"),
                provenance(policy="fixed-200"),
                "output_policy_required",
            ),
        }
        for label, (left, right, reason) in cases.items():
            with self.subTest(label=label):
                value, reasons = ratio_observation_from_evidence(
                    block_id="block-1",
                    energy_a_j=1.0,
                    energy_b_j=2.0,
                    provenance_a=left,
                    provenance_b=right,
                )
                self.assertIsNone(value)
                self.assertIn(reason, reasons)

    def test_server_usage_is_runtime_evidence_but_mixed_sources_fail_closed(self) -> None:
        server, reasons = ratio_observation_from_evidence(
            block_id="block-1",
            energy_a_j=1.0,
            energy_b_j=2.0,
            provenance_a=provenance(source="server_usage"),
            provenance_b=provenance(source="server_usage"),
        )
        self.assertIsNotNone(server)
        self.assertEqual(reasons, ())
        collection_reasons = ratio_collection_evidence_reasons(
            (
                (provenance(source="runtime_observed"), provenance(source="runtime_observed")),
                (provenance(source="server_usage"), provenance(source="server_usage")),
            )
        )
        self.assertIn("runtime_token_denominator_required", collection_reasons)

    def test_realized_stop_reason_is_validated_but_not_part_of_policy_equality(self) -> None:
        value, reasons = ratio_observation_from_evidence(
            block_id="block-1",
            energy_a_j=1.0,
            energy_b_j=2.0,
            provenance_a=provenance(stop_reason="requested_tokens_emitted"),
            provenance_b=provenance(stop_reason="backend_stop"),
        )
        self.assertIsNotNone(value)
        self.assertEqual(reasons, ())

        missing_stop = provenance()
        missing_stop["stop_reason"] = None
        value, reasons = ratio_observation_from_evidence(
            block_id="block-1",
            energy_a_j=1.0,
            energy_b_j=2.0,
            provenance_a=missing_stop,
            provenance_b=provenance(),
        )
        self.assertIsNone(value)
        self.assertIn("stop_reason_required", reasons)

    def test_bundle_policy_identity_excludes_realized_emitted_count_and_stop(self) -> None:
        def bundle(emitted: int, stop: str) -> BundleEvidence:
            return BundleEvidence(
                entry={},
                bundle_id=f"bundle-{emitted}",
                relative_path=f"bundle-{emitted}",
                path=Path(f"bundle-{emitted}"),
                summary={"measurement_quality": {"token_counts_source": "runtime_observed"}},
                metadata={
                    "workload_observed": {"output_token_count": emitted},
                    "workload_provenance": {
                        "output_policy": {
                            "name": "fixed_budget_exact",
                            "requested_tokens": 100,
                            "emitted_tokens": emitted,
                            "stop_condition": stop,
                        },
                        "sampler": {"kind": "greedy", "temperature": 0.0},
                        "tokenizer": {"name": "tok-a", "revision": "sha256:test"},
                    },
                },
                raw_config={},
                strict_problems=(),
                base_reason_codes=(),
                config_sha256=None,
                summary_sha256=None,
                replacement_classification="registered",
                inclusion_status="included",
            )

        first = token_provenance(bundle(100, "requested_tokens_emitted"))
        second = token_provenance(bundle(80, "backend_stop"))
        self.assertEqual(
            {
                key: first["output_policy"][key]
                for key in ("name", "requested_tokens", "sampler")
            },
            {
                key: second["output_policy"][key]
                for key in ("name", "requested_tokens", "sampler")
            },
        )
        self.assertNotEqual(
            first["output_policy"]["emitted_tokens"],
            second["output_policy"]["emitted_tokens"],
        )
        self.assertNotEqual(first["stop_reason"], second["stop_reason"])

    def test_truncated_or_unsubstantiated_fixed_budget_output_is_ratio_ineligible(self) -> None:
        cases = {
            "truncated": provenance(tokens=80),
            "empty": provenance(tokens=0),
            "missing emitted evidence": {
                **provenance(),
            },
            "count disagreement": {
                **provenance(),
            },
        }
        for label, bad in cases.items():
            with self.subTest(label=label):
                bad["output_policy"] = dict(bad["output_policy"])
                bad["output_policy"]["name"] = "fixed_budget_exact"
                bad["output_policy"]["requested_tokens"] = 100
                if label == "missing emitted evidence":
                    bad["output_policy"].pop("emitted_tokens")
                elif label == "count disagreement":
                    bad["output_policy"]["emitted_tokens"] = 99
                value, reasons = ratio_observation_from_evidence(
                    block_id="block-1",
                    energy_a_j=1.0,
                    energy_b_j=2.0,
                    provenance_a=bad,
                    provenance_b=provenance(),
                )
                self.assertIsNone(value)
                self.assertTrue(
                    {"runtime_token_denominator_required", "output_policy_required"}
                    & set(reasons)
                )

    def test_sealed_suite_uses_per_item_realized_outcomes_for_ratio_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sealed-suite"
            (path / "outputs").mkdir(parents=True)
            events = []
            records = []
            for item_index, stop_reason in enumerate(
                ("requested_tokens_emitted", "requested_tokens_emitted")
            ):
                events.extend(
                    [
                        {
                            "timestamp_s": float(item_index * 10),
                            "event_type": "item_start",
                            "phase": "suite",
                            "message": "start",
                            "metadata": {
                                "item_id": f"item-{item_index}",
                                "item_index": item_index,
                                "output_policy": "fixed_budget_exact",
                                "planned_output_tokens": 2,
                            },
                        },
                        {
                            "timestamp_s": float(item_index * 10 + 1),
                            "event_type": "item_end",
                            "phase": "suite",
                            "message": "end",
                            "metadata": {
                                "item_id": f"item-{item_index}",
                                "item_index": item_index,
                                "status": "succeeded",
                                "emitted_tokens": 2,
                                "stop_reason": stop_reason,
                            },
                        },
                    ]
                )
                records.append(
                    {
                        "item_id": f"item-{item_index}",
                        "item_index": item_index,
                        "status": "succeeded",
                        "emitted_tokens": 2,
                        "stop_reason": stop_reason,
                        "tokens": [{"index": 0}, {"index": 1}],
                        "emitted_token_ids": [10, 11],
                    }
                )
            (path / "events.jsonl").write_text(
                "".join(json.dumps(event) + "\n" for event in events)
            )
            (path / "outputs" / "suite_items.jsonl").write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
            evidence = BundleEvidence(
                entry={},
                bundle_id="sealed-suite",
                relative_path="sealed-suite",
                path=path,
                summary={"measurement_quality": {"token_counts_source": "runtime_observed"}},
                metadata={
                    "suite": {"suite_id": "sealed"},
                    "workload_observed": {"output_token_count": 4},
                    "workload_provenance": {
                        "output_policy": {
                            "name": "fixed_budget_exact",
                            "requested_tokens": 4,
                            "emitted_tokens": 4,
                            "stop_condition": "suite_completed",
                        },
                        "sampler": {"kind": "greedy"},
                        "tokenizer": {"name": "tok-a"},
                    },
                },
                raw_config={},
                strict_problems=(),
                base_reason_codes=(),
                config_sha256=None,
                summary_sha256=None,
                replacement_classification="registered",
                inclusion_status="included",
            )
            realized = token_provenance(evidence)
            self.assertNotEqual(realized["stop_reason"], "suite_completed")
            self.assertEqual(len(realized["output_policy"]["realized_items"]), 2)
            value, reasons = ratio_observation_from_evidence(
                block_id="block-1",
                energy_a_j=1.0,
                energy_b_j=2.0,
                provenance_a=realized,
                provenance_b=realized,
            )
            self.assertIsNotNone(value)
            self.assertEqual(reasons, ())

            # Adversarial checker shape: the durable item record says the
            # generation failed/truncated while the marker lane looks clean.
            # Marker precedence would incorrectly leave this ratio-eligible.
            records[1]["status"] = "failed"
            records[1]["stop_reason"] = "truncated"
            (path / "outputs" / "suite_items.jsonl").write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
            conflicting = token_provenance(evidence)
            self.assertFalse(
                conflicting["output_policy"]["realized_items"][1][
                    "record_marker_agreement"
                ]
            )
            value, reasons = ratio_observation_from_evidence(
                block_id="block-conflicting-record",
                energy_a_j=1.0,
                energy_b_j=2.0,
                provenance_a=conflicting,
                provenance_b=realized,
            )
            self.assertIsNone(value)
            self.assertIn("output_policy_required", reasons)

            records[1]["status"] = "succeeded"
            records[1]["stop_reason"] = "requested_tokens_emitted"
            records[1]["tokens"] = []
            (path / "outputs" / "suite_items.jsonl").write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
            inconsistent = token_provenance(evidence)
            value, reasons = ratio_observation_from_evidence(
                block_id="block-2",
                energy_a_j=1.0,
                energy_b_j=2.0,
                provenance_a=inconsistent,
                provenance_b=realized,
            )
            self.assertIsNone(value)
            self.assertIn("runtime_token_denominator_required", reasons)

    def test_both_forms_round_trip_through_claim_artifact(self) -> None:
        values = (
            observation("block-1", energy_b=10.0, tokens=100),
            observation("block-2", energy_b=10.0, tokens=100),
        )
        for form in ("mean_of_request_ratios", "ratio_of_totals"):
            with self.subTest(form=form):
                estimate = estimate_manifest_observations(ratio_metric(form), values)
                artifact = copy.deepcopy(minimal_artifact())
                artifact["claim_verdicts_id"] = ""
                contrast = artifact["contrasts"][0]
                contrast["metric"] = ratio_metric(form)
                contrast["estimator"] = estimator_row(estimate)
                contrast["deterministic_bounds"] = {
                    "terms": [asdict(term) for term in estimate.deterministic_bounds],
                    "total": estimate.deterministic_bound_total,
                    "decision_interval": interval(estimate.decision_interval),
                }
                contrast["floor"].update(
                    floor_abs_j=0.025,
                    floor_cmp_j=0.05,
                    active_floor_j=0.05,
                )
                contrast["floor"]["resolutions"][0].update(
                    floor_abs_j=0.025,
                    floor_cmp_j=0.05,
                    floor_gate_j=0.05,
                )
                contrast["multiplicity"].update(
                    raw_p=estimate.raw_p,
                    adjusted_p=estimate.raw_p,
                    rejected=True,
                )
                artifact["families"][0]["adjusted_p_values"]["ctr-test"] = estimate.raw_p
                finalized = finalize_claim_verdicts(artifact)
                reread = json.loads(render_claim_verdicts(finalized))
                self.assertEqual(validate_claim_verdicts(reread), [])
                self.assertEqual(
                    reread["claim_verdicts_id"], calculate_claim_verdicts_id(reread)
                )

    def test_ratio_of_totals_null_sd_rule_is_exactly_named(self) -> None:
        artifact = copy.deepcopy(minimal_artifact())
        artifact["contrasts"][0]["estimator"]["s_d"] = None
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
        self.assertTrue(
            any("estimator.s_d" in error for error in validate_claim_verdicts(artifact))
        )


if __name__ == "__main__":
    unittest.main()
