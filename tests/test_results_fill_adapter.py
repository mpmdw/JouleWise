"""Synthetic verdicts produced by the real estimator, evaluator and finalizer."""
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import unittest

from joulewise.analysis_engine.artifact import (
    finalize_claim_verdicts, render_claim_verdicts, validate_claim_verdicts,
)
from joulewise.analysis_engine.claims import CLAIM_OUTCOMES, evaluate_claim
from joulewise.analysis_engine.estimators import (
    DeterministicBoundTerm, PairedObservation, estimate_paired_blocks, tost_p_value,
)
from tests.test_analysis_claims import minimal_artifact

FIXTURES = Path(__file__).parent / "fixtures" / "results_fill"


def produced_verdict(outcome="direction_supported"):
    artifact = deepcopy(minimal_artifact())
    artifact["inputs"]["limitations"] = ["SYNTHETIC fixture; no live measurement or paper issuance"]
    row = artifact["contrasts"][0]
    delta = 0.1 if outcome == "equivalent" else 2.0
    bound = 0.25
    estimate = estimate_paired_blocks(tuple(
        PairedObservation(f"block-{i}", 0.0, (0.0 if i == 1 else 4.0) if outcome == "unresolved" else delta,
                          deterministic_terms=(DeterministicBoundTerm(
                              "E_clock_anchor_shift_bound_j", 0.0, bound),))
        for i in (1, 2)
    ))
    row["estimator"] = {
        "name": estimate.estimator, "n": estimate.n, "df": estimate.df,
        "estimate": estimate.estimate, "s_d": estimate.sample_stddev,
        "SE_repeat": estimate.se_repeat, "SE_metrology": estimate.se_metrology,
        "SE_total": estimate.se_total, "t_critical_95": estimate.t_critical_95,
        "repeat_point_CI95": asdict(estimate.repeat_point_ci95),
        "metrology_aware_CI95": asdict(estimate.metrology_aware_ci95),
        "variance_contributions": [], "excluded_stochastic_terms": [],
        "raw_p": estimate.raw_p,
    }
    row["deterministic_bounds"] = {
        "terms": [asdict(term) for term in estimate.deterministic_bounds],
        "total": estimate.deterministic_bound_total,
        "decision_interval": asdict(estimate.decision_interval),
    }
    if outcome in {"not_resolvable", "equivalent"}:
        floor = 3.0 if outcome == "not_resolvable" else 0.5
        row["floor"].update(floor_abs_j=floor, floor_cmp_j=floor, active_floor_j=floor)
        row["floor"]["resolutions"][0].update(
            floor_abs_j=floor, floor_cmp_j=floor, floor_gate_j=floor)
    if outcome == "equivalent":
        row["equivalence"] = {"margin": 1.0, "method": "tost_v1"}
        row["estimator"]["raw_p"] = tost_p_value(
            estimate.estimate, estimate.se_total, estimate.df, 1.0)[2]
    if outcome == "not_estimable":
        row["estimator"].update(n=0, df=None)
        for key in ("estimate", "s_d", "SE_repeat", "SE_metrology", "SE_total",
                    "t_critical_95", "repeat_point_CI95", "metrology_aware_CI95", "raw_p"):
            row["estimator"][key] = None
        row["deterministic_bounds"] = {"terms": [], "total": None, "decision_interval": None}
        row["bundle_blocks"]["included_bundle_ids"] = []
        for block in row["bundle_blocks"]["blocks"]:
            block.update(included=False, reason_codes=["metric_missing_or_nonfinite"])
        row["sampling"]["observed_complete_n"] = 0
        row["randomization_check"]["n_blocks"] = 0
    raw_p = row["estimator"]["raw_p"]
    row["multiplicity"].update(raw_p=raw_p, adjusted_p=raw_p,
                               rejected=False if raw_p is None else raw_p <= 0.05)
    family = artifact["families"][0]
    family.update(finite_test_count=0 if raw_p is None else 1,
                  raw_ordering=[] if raw_p is None else ["ctr-test"],
                  adjusted_p_values={"ctr-test": raw_p},
                  missing_test_ids=["ctr-test"] if raw_p is None else [])
    row["claim_evaluation"] = evaluate_claim(
        estimate=row["estimator"]["estimate"],
        metrology_aware_ci95=row["estimator"]["metrology_aware_CI95"],
        decision_interval=row["deterministic_bounds"]["decision_interval"],
        floor_gate_j=row["floor"]["active_floor_j"],
        adjusted_rejected=row["multiplicity"]["rejected"],
        hypothesized_direction=row["hypothesized_direction"], equivalence=row["equivalence"],
    )
    assert row["claim_evaluation"]["outcome"] == outcome
    return finalize_claim_verdicts(artifact)


def produced_token_verdict():
    from joulewise.analysis_engine import estimate_manifest_observations
    from tests.test_analysis_ratio_integration import ratio_metric, observation, estimator_row
    artifact = produced_verdict()
    row = artifact["contrasts"][0]
    metric = ratio_metric("ratio_of_totals")
    estimate = estimate_manifest_observations(metric, tuple(
        observation(f"block-{i}", energy_b=10.0, tokens=100) for i in (1, 2)))
    row["metric"] = metric
    row["estimator"] = estimator_row(estimate)
    row["deterministic_bounds"] = {"terms": [asdict(term) for term in estimate.deterministic_bounds],
                                   "total": estimate.deterministic_bound_total,
                                   "decision_interval": asdict(estimate.decision_interval)}
    row["floor"].update(floor_abs_j=0.025, floor_cmp_j=0.05, active_floor_j=0.05)
    row["floor"]["resolutions"][0].update(floor_abs_j=0.025, floor_cmp_j=0.05, floor_gate_j=0.05)
    row["multiplicity"].update(raw_p=estimate.raw_p, adjusted_p=estimate.raw_p, rejected=True)
    artifact["families"][0]["adjusted_p_values"]["ctr-test"] = estimate.raw_p
    row["claim_evaluation"] = evaluate_claim(
        estimate=estimate.estimate, metrology_aware_ci95=asdict(estimate.metrology_aware_ci95),
        decision_interval=asdict(estimate.decision_interval), floor_gate_j=0.05,
        adjusted_rejected=True, hypothesized_direction="positive")
    return finalize_claim_verdicts(artifact)


def campaigns():
    return {role: {"verdict": f"{role}-verdict.json", "floor_artifact": f"{role}-floor.json",
                   "extraction": f"{role}-extraction.json", "cells": {}}
            for role in ("alpha", "beta")}


class ResultsFillAdapterTests(unittest.TestCase):
    def test_real_ratio_producer_supplies_token_quantity_without_conversion(self):
        artifact = produced_token_verdict()
        from joulewise.results_fill_adapter import adapt_claim_verdicts
        output = adapt_claim_verdicts(render_claim_verdicts(artifact), campaigns=campaigns())
        self.assertEqual(output["gamma"]["contrasts"][0]["j_per_token"], 0.1)
        self.assertEqual(output["gamma"]["contrasts"][0]["metric"]["unit"], "J/token")

    def test_real_producer_fixtures_cover_every_outcome_and_copy_fields(self):
        for outcome in sorted(CLAIM_OUTCOMES):
            with self.subTest(outcome=outcome):
                produced = produced_verdict(outcome)
                raw = (FIXTURES / f"{outcome}.json").read_bytes()
                self.assertEqual(json.loads(raw), produced)
                self.assertEqual(validate_claim_verdicts(produced), [])
                from joulewise.results_fill_adapter import adapt_claim_verdicts
                output = adapt_claim_verdicts(raw, campaigns=campaigns())
                self.assertEqual(output["schema_version"], "joulewise.results_fill_input.v1")
                self.assertEqual(output["campaigns"], campaigns())
                self.assertEqual(output["gamma"]["claim_verdicts_id"], produced["claim_verdicts_id"])
                row = output["gamma"]["contrasts"][0]
                source = produced["contrasts"][0]
                self.assertEqual(row["claim_evaluation"], source["claim_evaluation"])
                self.assertEqual(row["estimate"], source["estimator"]["estimate"])
                self.assertEqual(row["interval"], source["estimator"]["metrology_aware_CI95"])
                self.assertEqual(row["decision_interval"], source["deterministic_bounds"]["decision_interval"])
                self.assertEqual(row["n"], source["estimator"]["n"])
                self.assertIsNone(row["j_per_token"])
                self.assertNotIn("STOP_FILL", json.dumps(output))

    def test_invalid_verdicts_refuse_before_emitting_manifest(self):
        raw = render_claim_verdicts(produced_verdict())
        from joulewise.results_fill_adapter import ResultsFillAdapterError, adapt_claim_verdicts
        for mutant in (raw.replace(b'"direction_supported"', b'"equivalent"'),
                       raw.replace(b'"schema_version":', b'"schema_version": null, "schema_version":', 1),
                       raw.replace(b'"estimate": 2.0', b'"estimate": NaN'), b'{}'):
            with self.subTest(mutant=mutant[:30]), self.assertRaises(ResultsFillAdapterError):
                adapt_claim_verdicts(mutant, campaigns=campaigns())

    def test_adapter_keeps_callers_objects_independent_and_requires_campaign_roles(self):
        from joulewise.results_fill_adapter import ResultsFillAdapterError, adapt_claim_verdicts
        source = campaigns()
        output = adapt_claim_verdicts(render_claim_verdicts(produced_verdict()), campaigns=source)
        output["campaigns"]["alpha"]["cells"]["decode"] = {}
        self.assertEqual(source["alpha"]["cells"], {})
        with self.assertRaises(ResultsFillAdapterError):
            adapt_claim_verdicts(render_claim_verdicts(produced_verdict()), campaigns={})
