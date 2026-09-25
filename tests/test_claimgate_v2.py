"""Focused CG-1/CG-2 component regressions pending full engine wiring."""

import math
import unittest

from joulewise.analysis_engine.claims import effective_equivalence_margin, evaluate_claim
from joulewise.analysis_engine import _claim_raw_p, _combined_floor, _v2_sign_flip_diagnostic
from joulewise.analysis_engine.inputs import FloorResolution
from joulewise.analysis_engine.distributions import student_t_quantile
from joulewise.analysis_engine.estimators import (
    DeterministicBoundTerm,
    EnvelopeTermScopeUnknown,
    PairedObservation,
    StochasticVarianceTerm,
    aggregate_envelope_observation,
    estimate_paired_blocks,
)
from joulewise.detection_floor import estimate_scale_floor, small_sample_guard_factor


class ClaimGateV2Tests(unittest.TestCase):
    def _equivalence(self, margin, interval, **kwargs):
        registered_shape = kwargs.pop("registered_claim_shape", "equivalence")
        evaluated_shape = kwargs.pop("evaluated_claim_shape", "equivalence")
        return evaluate_claim(
            estimate=0.0,
            metrology_aware_ci95={"lower": -interval, "upper": interval},
            decision_interval={"lower": -interval, "upper": interval},
            floor_gate_j=0.8,
            adjusted_rejected=True,
            equivalence={"method": "tost_v2", "margin": margin},
            claim_rule_version="v2",
            floor_class="estimate",
            floor_unit="J/correct",
            estimand_unit="J/correct",
            claim_side_bound=0.1,
            registered_claim_shape=registered_shape,
            evaluated_claim_shape=evaluated_shape,
            **kwargs,
        )

    def test_effective_margin_is_strict_for_containment_and_registration(self):
        self.assertAlmostEqual(effective_equivalence_margin(2.0, 0.8), 1.2)
        self.assertEqual(self._equivalence(2.0, 1.19)["outcome"], "equivalent")
        self.assertEqual(self._equivalence(2.0, 1.21)["outcome"], "unresolved")
        refused = self._equivalence(0.9, 0.01)
        self.assertEqual(refused["outcome"], "not_resolvable")
        self.assertIn("equivalence_margin_not_above_floor", refused["reason_codes"])

    def test_raw_tost_uses_effective_margin_before_holm(self):
        observations = tuple(
            PairedObservation(str(index), 0.0, value)
            for index, value in enumerate((-0.5, -0.25, 0.0, 0.25, 0.5, -0.25, 0.25, 0.0))
        )
        estimate = estimate_paired_blocks(observations, confidence=0.90)
        prepared = {
            "manifest": {"claim_rule_version": "v2", "equivalence": {"method": "tost_v2", "margin": 2.0}},
            "floor": {"floor_est": 0.8},
            "global_reason_codes": (),
        }
        from joulewise.analysis_engine.estimators import tost_p_value
        self.assertAlmostEqual(
            _claim_raw_p(prepared, estimate),
            tost_p_value(estimate.estimate, estimate.se_total, estimate.df, 1.2)[2],
        )
        self.assertNotAlmostEqual(
            _claim_raw_p(prepared, estimate),
            tost_p_value(estimate.estimate, estimate.se_total, estimate.df, 2.0)[2],
        )
        self.assertIsNone(_claim_raw_p(prepared, estimate, {"floor_est": None}))

    def test_v2_floor_resolution_and_sign_flip_remain_typed(self):
        resolution = FloorResolution(
            status="exact", artifact_id="cal", artifact_sha256="0" * 64,
            source_cell_ids=("c",), transport_group_id=None, transport_rule_id=None,
            floor_abs_j=2.0, floor_cmp_j=3.0, floor_gate_j=3.0,
            reason_codes=(), floor_est=0.8, floor_unit="J", floor_class="estimate",
        )
        combined = _combined_floor((resolution,), claim_rule_version="v2")
        self.assertEqual(combined["active_floor_j"], 0.8)
        self.assertEqual(combined["floor_class"], "estimate")
        observations = tuple(PairedObservation(str(i), 0.0, 1.0) for i in range(5))
        estimate = estimate_paired_blocks(observations)
        diagnostic = _v2_sign_flip_diagnostic(estimate, 5)
        self.assertEqual(diagnostic["minimum_attainable_p"], 2 / 2**5)
        self.assertEqual(diagnostic["exact_two_sided_p"], 2 / 2**5)

    def test_floor_mismatch_and_second_shape_fail_closed(self):
        wrong_unit = evaluate_claim(
            estimate=3.0,
            metrology_aware_ci95={"lower": 1.0, "upper": 5.0},
            decision_interval={"lower": 0.5, "upper": 5.5},
            floor_gate_j=0.8,
            adjusted_rejected=True,
            claim_rule_version="v2",
            floor_class="block",
            floor_unit="J",
            estimand_unit="J/correct",
            claim_side_bound=0.5,
            registered_claim_shape="direction",
            evaluated_claim_shape="direction",
        )
        self.assertEqual(wrong_unit["outcome"], "not_resolvable")
        self.assertIn("floor_class_mismatch", wrong_unit["reason_codes"])
        self.assertIn("floor_unit_mismatch", wrong_unit["reason_codes"])
        exploratory = self._equivalence(2.0, 0.5, registered_claim_shape="direction")
        self.assertEqual(exploratory["outcome"], "equivalent")
        self.assertFalse(exploratory["claim_ready_for_l2_l3"])

    def test_sign_flip_diagnostic_does_not_demote_v2(self):
        result = self._equivalence(2.0, 0.5, base_reason_codes=["randomization_check_insufficient_blocks"])
        self.assertEqual(result["outcome"], "equivalent")
        self.assertTrue(result["claim_ready_for_l2_l3"])

    def test_estimate_floor_uses_envelope_mean_scale_and_guard(self):
        values = [0.0, 1.0, -1.0, 2.0, -2.0]
        sd = math.sqrt(sum(value * value for value in values) / 4)
        expected = small_sample_guard_factor(5) * student_t_quantile(0.975, 4) * sd / math.sqrt(5)
        self.assertAlmostEqual(estimate_scale_floor(values), expected)
        with self.assertRaisesRegex(ValueError, "at least five"):
            estimate_scale_floor(values[:4])

    def test_equivalence_confidence_is_90_percent_and_ci95_is_retained(self):
        observations = tuple(PairedObservation(str(i), 0.0, float(i)) for i in range(5))
        ninety = estimate_paired_blocks(observations, confidence=0.90)
        default = estimate_paired_blocks(observations)
        self.assertEqual(ninety.interval_confidence, 0.90)
        self.assertEqual(ninety.metrology_aware_ci95, default.metrology_aware_ci95)
        self.assertEqual(ninety.metrology_aware_interval, ninety.metrology_aware_ci90)
        self.assertLess(
            ninety.metrology_aware_ci90.upper - ninety.estimate,
            ninety.metrology_aware_ci95.upper - ninety.estimate,
        )
        self.assertEqual(ninety.decision_interval.upper, ninety.metrology_aware_ci90.upper)
        with self.assertRaisesRegex(ValueError, "confidence"):
            estimate_paired_blocks(observations, confidence=0.91)

    def test_independent_block_variances_divide_by_n_squared(self):
        blocks = tuple(
            PairedObservation(
                f"b{i}", 10.0 + i, 12.0 + i,
                stochastic_terms=(StochasticVarianceTerm(
                    "meter", 4.0, 9.0, 2.0, "independent_run"),),
                deterministic_terms=(DeterministicBoundTerm("clock", 0.1, 0.2),),
            ) for i in range(3)
        )
        envelope = aggregate_envelope_observation("e1", blocks, n_reg=3)
        self.assertEqual((envelope.value_a, envelope.value_b), (11.0, 13.0))
        self.assertAlmostEqual(envelope.stochastic_terms[0].variance_a, 4 / 3)
        self.assertAlmostEqual(envelope.stochastic_terms[0].variance_b, 3.0)
        self.assertAlmostEqual(envelope.stochastic_terms[0].covariance_ab, 2 / 3)
        self.assertAlmostEqual(envelope.deterministic_terms[0].contrast_bound, 0.3)
        with self.assertRaisesRegex(ValueError, "n_reg"):
            aggregate_envelope_observation("e1", blocks[:2], n_reg=3)

    def test_unregistered_shared_scope_refuses_instead_of_dividing(self):
        blocks = tuple(PairedObservation(
            f"b{i}", 0.0, 1.0,
            stochastic_terms=(StochasticVarianceTerm("shared", 1.0, 9.0, 0.0, "shared_envelope"),),
        ) for i in range(2))
        with self.assertRaisesRegex(EnvelopeTermScopeUnknown, "envelope_term_scope_unknown"):
            aggregate_envelope_observation("e1", blocks, n_reg=2)


if __name__ == "__main__":
    unittest.main()
