"""Hand-computed estimator fixtures for P2-037 (C-027 B4-B6/B8)."""

from __future__ import annotations

import math
import unittest

from joulewise.analysis_engine.estimators import (
    DeterministicBoundTerm,
    PairedObservation,
    RatioObservation,
    StochasticVarianceTerm,
    estimate_mean_of_request_ratios,
    estimate_paired_blocks,
    estimate_ratio_of_totals,
    tost_p_value,
)


def ratio_observation(
    block_id: str,
    *,
    energy_a: float,
    energy_b: float,
    tokens_a: int,
    tokens_b: int,
    source_a: str = "runtime_observed",
    source_b: str = "runtime_observed",
    tokenizer_a: str = "tokenizer-sha256:test",
    tokenizer_b: str = "tokenizer-sha256:test",
    policy_a: str = "greedy/max_new_tokens=200",
    policy_b: str = "greedy/max_new_tokens=200",
    stop_a: str = "max_tokens",
    stop_b: str = "max_tokens",
    stochastic_terms: tuple[StochasticVarianceTerm, ...] = (),
) -> RatioObservation:
    return RatioObservation(
        block_id=block_id,
        energy_a_j=energy_a,
        energy_b_j=energy_b,
        output_tokens_a=tokens_a,
        output_tokens_b=tokens_b,
        token_count_source_a=source_a,
        token_count_source_b=source_b,
        stop_reason_a=stop_a,
        stop_reason_b=stop_b,
        output_policy_a=policy_a,
        output_policy_b=policy_b,
        tokenizer_identity_a=tokenizer_a,
        tokenizer_identity_b=tokenizer_b,
        energy_stochastic_terms=stochastic_terms,
    )


class PairedBlockEstimatorTests(unittest.TestCase):
    def test_normative_paired_fixture_defeats_marginal_intervals(self) -> None:
        a = [100.0, 200.0, 300.0, 400.0, 500.0]
        b = [101.0, 201.0, 301.0, 401.0, 501.0]
        result = estimate_paired_blocks(
            tuple(
                PairedObservation(f"block-{index}", value_a, value_b)
                for index, (value_a, value_b) in enumerate(zip(a, b), start=1)
            )
        )

        self.assertEqual(result.n, 5)
        self.assertEqual(result.df, 4)
        self.assertEqual(result.paired_values, (1.0, 1.0, 1.0, 1.0, 1.0))
        self.assertEqual(result.estimate, 1.0)
        self.assertEqual(result.sample_stddev, 0.0)
        self.assertEqual(result.se_repeat, 0.0)
        self.assertEqual(result.se_total, 0.0)
        self.assertEqual((result.repeat_point_ci95.lower, result.repeat_point_ci95.upper), (1.0, 1.0))
        self.assertEqual(
            (result.metrology_aware_ci95.lower, result.metrology_aware_ci95.upper),
            (1.0, 1.0),
        )
        self.assertIsNone(result.t_statistic)
        self.assertEqual(result.raw_p, 0.0)

    def test_paired_df_is_exactly_n_minus_one_for_n_five_to_ten(self) -> None:
        for n in range(5, 11):
            with self.subTest(n=n):
                result = estimate_paired_blocks(
                    tuple(
                        PairedObservation(f"b-{index}", float(index), float(index + 1))
                        for index in range(n)
                    )
                )
                self.assertEqual(result.df, n - 1)

    def test_metrology_variance_widens_ci_and_gross_repetition_is_not_double_counted(self) -> None:
        with_terms = []
        without_gross = []
        for index in range(5):
            idle = StochasticVarianceTerm(
                "E_idle_mean_j2",
                variance_a=0.25,
                variance_b=0.25,
                correlation_scope="independent_run",
            )
            gross = StochasticVarianceTerm(
                "E_gross_repetition_j2",
                variance_a=1_000_000.0,
                variance_b=1_000_000.0,
                covariance_ab=None,
            )
            base = dict(block_id=f"b-{index}", value_a=float(index), value_b=float(index + 1))
            with_terms.append(PairedObservation(**base, stochastic_terms=(idle, gross)))
            without_gross.append(PairedObservation(**base, stochastic_terms=(idle,)))

        governed = estimate_paired_blocks(tuple(with_terms))
        comparison = estimate_paired_blocks(tuple(without_gross))
        self.assertEqual(governed.excluded_stochastic_terms, ("E_gross_repetition_j2",))
        self.assertEqual(governed.se_metrology, comparison.se_metrology)
        self.assertEqual(governed.metrology_aware_ci95, comparison.metrology_aware_ci95)
        self.assertGreater(governed.se_total, governed.se_repeat)

    def test_p2044_hand_fixture_propagates_five_halves_per_run(self) -> None:
        term = StochasticVarianceTerm(
            "E_idle_mean_j2",
            variance_a=2.5,
            variance_b=2.5,
            covariance_ab=None,
            correlation_scope="independent_run",
        )
        result = estimate_paired_blocks(
            (
                PairedObservation("b-1", 100.0, 101.0, stochastic_terms=(term,)),
                PairedObservation("b-2", 200.0, 201.0, stochastic_terms=(term,)),
            )
        )
        self.assertEqual(result.se_repeat, 0.0)
        self.assertAlmostEqual(result.se_metrology**2, 2.5, places=15)
        self.assertAlmostEqual(result.se_total, math.sqrt(2.5), places=15)
        ratio = estimate_mean_of_request_ratios(
            tuple(
                ratio_observation(
                    f"ratio-{index}",
                    energy_a=100.0 * index,
                    energy_b=100.0 * index + 1.0,
                    tokens_a=10,
                    tokens_b=10,
                    stochastic_terms=(term,),
                )
                for index in (1, 2)
            )
        )
        self.assertAlmostEqual(ratio.se_metrology**2, 1 / 40, places=15)

    def test_deterministic_bounds_expand_only_decision_interval(self) -> None:
        observations = tuple(
            PairedObservation(
                f"b-{index}",
                float(index),
                float(index + 2),
                deterministic_terms=(
                    DeterministicBoundTerm("interpolation", bound_a=0.25, bound_b=0.5),
                    DeterministicBoundTerm("clock", bound_a=0.1, bound_b=0.1),
                ),
            )
            for index in range(5)
        )
        result = estimate_paired_blocks(observations)
        self.assertEqual(result.metrology_aware_ci95.lower, 2.0)
        self.assertEqual(result.metrology_aware_ci95.upper, 2.0)
        self.assertAlmostEqual(result.deterministic_bound_total, 0.95)
        self.assertAlmostEqual(result.decision_interval.lower, 1.05)
        self.assertAlmostEqual(result.decision_interval.upper, 2.95)

    def test_unknown_covariance_fails_closed(self) -> None:
        observations = tuple(
            PairedObservation(
                f"b-{index}",
                1.0,
                2.0,
                stochastic_terms=(
                    StochasticVarianceTerm(
                        "E_idle_mean_j2",
                        variance_a=1.0,
                        variance_b=1.0,
                    ),
                ),
            )
            for index in range(2)
        )
        with self.assertRaisesRegex(ValueError, "covariance_ab is required"):
            estimate_paired_blocks(observations)

    def test_tost_family_p_value_is_max_of_hand_computed_one_sided_tests(self) -> None:
        # df=1 is Cauchy.  With estimate=0, margin=1, SE=1, the two test
        # statistics are +1 and -1, whose one-sided tails are each 0.25.
        lower, upper, combined = tost_p_value(0.0, 1.0, 1, 1.0)
        self.assertAlmostEqual(lower, 0.25, places=14)
        self.assertAlmostEqual(upper, 0.25, places=14)
        self.assertEqual(combined, max(lower, upper))
        self.assertEqual(tost_p_value(0.0, 0.0, 4, 1.0), (0.0, 0.0, 0.0))


class RatioEstimatorTests(unittest.TestCase):
    def test_normative_100_mj_fixture_widens_by_12_41465_mj(self) -> None:
        observations = tuple(
            ratio_observation(
                f"b-{index}",
                energy_a=0.0,
                energy_b=10.0,
                tokens_a=100,
                tokens_b=100,
                stochastic_terms=(
                    StochasticVarianceTerm(
                        "E_idle_mean_j2",
                        variance_a=0.0,
                        variance_b=1.0,
                        correlation_scope="independent_run",
                    ),
                ),
            )
            for index in range(5)
        )
        result = estimate_mean_of_request_ratios(observations)

        expected_se = math.sqrt(1.0 / 5.0) / 100.0
        expected_half_width = 2.776 * expected_se
        self.assertEqual(result.ratio_estimand, "mean_of_request_ratios")
        self.assertEqual(result.estimate, 0.1)
        self.assertEqual(result.se_repeat, 0.0)
        self.assertAlmostEqual(result.se_total, expected_se, places=15)
        self.assertAlmostEqual(
            (result.metrology_aware_ci95.upper - result.estimate) * 1000.0,
            12.414649411,
            places=9,
        )
        self.assertAlmostEqual(result.metrology_aware_ci95.lower, 0.1 - expected_half_width)
        self.assertAlmostEqual(result.metrology_aware_ci95.upper, 0.1 + expected_half_width)

    def test_ratio_forms_differ_with_varying_denominators_and_match_hand_math(self) -> None:
        observations = (
            ratio_observation(
                "b-1",
                energy_a=0.0,
                energy_b=10.0,
                tokens_a=100,
                tokens_b=100,
            ),
            ratio_observation(
                "b-2",
                energy_a=0.0,
                energy_b=40.0,
                tokens_a=200,
                tokens_b=200,
            ),
        )
        mean_ratios = estimate_mean_of_request_ratios(observations)
        ratio_totals = estimate_ratio_of_totals(observations)

        self.assertAlmostEqual(mean_ratios.estimate, (0.1 + 0.2) / 2.0)
        self.assertAlmostEqual(ratio_totals.estimate, 50.0 / 300.0)
        self.assertNotEqual(mean_ratios.estimate, ratio_totals.estimate)
        self.assertEqual(ratio_totals.jackknife_estimates, (0.2, 0.1))
        self.assertAlmostEqual(ratio_totals.se_repeat, 0.05)

    def test_ratio_of_totals_adds_independent_numerator_metrology_variance(self) -> None:
        variance = (
            StochasticVarianceTerm(
                "E_idle_mean_j2",
                variance_a=0.0,
                variance_b=1.0,
                correlation_scope="independent_run",
            ),
        )
        observations = tuple(
            ratio_observation(
                f"b-{index}",
                energy_a=0.0,
                energy_b=10.0,
                tokens_a=100,
                tokens_b=100,
                stochastic_terms=variance,
            )
            for index in range(5)
        )
        mean_ratios = estimate_mean_of_request_ratios(observations)
        ratio_totals = estimate_ratio_of_totals(observations)

        expected_variance = 5.0 / (5 * 100) ** 2
        self.assertEqual(ratio_totals.estimate, 0.1)
        self.assertEqual(ratio_totals.se_repeat, 0.0)
        self.assertAlmostEqual(ratio_totals.se_metrology**2, expected_variance, places=18)
        self.assertAlmostEqual(ratio_totals.se_total, mean_ratios.se_total, places=15)

    def test_runtime_token_evidence_fails_closed(self) -> None:
        base = [
            ratio_observation(
                "b-1",
                energy_a=1.0,
                energy_b=2.0,
                tokens_a=10,
                tokens_b=10,
            ),
            ratio_observation(
                "b-2",
                energy_a=1.0,
                energy_b=2.0,
                tokens_a=10,
                tokens_b=10,
            ),
        ]

        variants = {
            "configured denominator": [replace_ratio(base[0], token_count_source_a="config_fallback"), base[1]],
            "mixed source": [replace_ratio(base[0], token_count_source_a="server_usage", token_count_source_b="server_usage"), base[1]],
            "tokenizer": [replace_ratio(base[0], tokenizer_identity_b="another"), base[1]],
            "output policy": [replace_ratio(base[0], output_policy_b="sampling/temp=1"), base[1]],
            "stop reason": [replace_ratio(base[0], stop_reason_b=""), base[1]],
            "zero tokens": [replace_ratio(base[0], output_tokens_b=0), base[1]],
        }
        for label, observations in variants.items():
            with self.subTest(label=label), self.assertRaises(ValueError):
                estimate_mean_of_request_ratios(observations)


def replace_ratio(value: RatioObservation, **updates: object) -> RatioObservation:
    fields = {
        "block_id": value.block_id,
        "energy_a_j": value.energy_a_j,
        "energy_b_j": value.energy_b_j,
        "output_tokens_a": value.output_tokens_a,
        "output_tokens_b": value.output_tokens_b,
        "token_count_source_a": value.token_count_source_a,
        "token_count_source_b": value.token_count_source_b,
        "stop_reason_a": value.stop_reason_a,
        "stop_reason_b": value.stop_reason_b,
        "output_policy_a": value.output_policy_a,
        "output_policy_b": value.output_policy_b,
        "tokenizer_identity_a": value.tokenizer_identity_a,
        "tokenizer_identity_b": value.tokenizer_identity_b,
        "energy_stochastic_terms": value.energy_stochastic_terms,
        "energy_deterministic_terms": value.energy_deterministic_terms,
    }
    fields.update(updates)
    return RatioObservation(**fields)  # type: ignore[arg-type]


class MixedWireAnchorTermIntersectionTests(unittest.TestCase):
    """A required anchor bound erased by term-name intersection refuses (Fix E).

    Pairing an anchor-era (0.5.1) bundle that carries
    ``E_clock_anchor_shift_bound_j`` against a pre-anchor (0.4.2) bundle that
    additively records no such term must NOT let the intersection silently drop
    the bound (under-bounding); the contrast refuses with
    ``anchor_energy_envelope_unrecorded``.
    """

    def _evidence(self, entry_id, cell_id, block_id, condition_id, summary):
        from pathlib import Path

        from joulewise.analysis_engine.inputs import BundleEvidence

        return BundleEvidence(
            entry={
                "entry_id": entry_id,
                "cell_id": cell_id,
                "block_id": block_id,
                "condition_id": condition_id,
                "role": "condition",
            },
            bundle_id=entry_id,
            relative_path=entry_id,
            path=Path(entry_id),
            summary=summary,
            metadata=None,
            raw_config=None,
            strict_problems=(),
            base_reason_codes=(),
            config_sha256=None,
            summary_sha256=None,
            replacement_classification="registered",
            inclusion_status="included",
        )

    def test_window_precheck_refuses_capture_pipeline_presentation(self) -> None:
        """The analysis precheck independently pins both barrier branches."""

        from joulewise.analysis_engine.inputs import window_evidence_precheck
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V2
        from tests.test_floor_extraction import make_summary

        for metadata, expected in (
            (
                {
                    "uncertainty_evidence": {
                        "clock_anchor": {"method": CLOCK_METHOD_V2}
                    }
                },
                "capture_pipeline_superseded",
            ),
            ({"uncertainty_evidence": {"capture_pipeline_absent": True}}, "capture_pipeline_absent"),
        ):
            with self.subTest(expected=expected):
                evidence = self._evidence(
                    "v2-member", "cell", "block", "condition", make_summary(40.0)
                )
                evidence.metadata = metadata
                result = window_evidence_precheck(
                    evidence,
                    {
                        "metric_tag": "gross_request",
                        "name": "gross_energy_j",
                        "window_class": "request",
                    },
                )
                self.assertIn(expected, result["reasons"])

    def test_superseded_anchor_wire_refuses_by_version_not_method(self) -> None:
        from unittest import mock

        import joulewise.analysis_engine as engine
        from joulewise.analysis_engine.inputs import LoadedAnalysisInputs
        from tests.test_floor_extraction import make_summary

        anchor_summary = make_summary(40.0, reducer="0.5.1")
        pre_anchor_summary = make_summary(39.0, reducer="0.4.2", anchor_bound=None)

        effective = {}
        entries = []
        block_ids = ("blk1", "blk2")
        for block_id in block_ids:
            a_id = f"{block_id}-A"
            b_id = f"{block_id}-B"
            effective[a_id] = self._evidence(
                a_id, "cell_a", block_id, "cond_a", anchor_summary
            )
            effective[b_id] = self._evidence(
                b_id, "cell_b", block_id, "cond_b", pre_anchor_summary
            )
            entries.append(effective[a_id].entry)
            entries.append(effective[b_id].entry)

        inputs = LoadedAnalysisInputs(
            manifest={
                "entries": entries,
                "design": {
                    "sampling_plan": {"planned_n_blocks": 2},
                    "randomization": {"scheme": "deterministic"},
                },
            },
            manifest_sha256="",
            floor_artifact={},
            floor_sha256="",
            registered={},
            effective=effective,
            extra_audits=(),
            valid_replacements=(),
            unregistered_matching=(),
            top_up_entry_ids=frozenset(),
        )
        contrast = {
            "contrast_id": "C1",
            "cell_a_id": "cell_a",
            "cell_b_id": "cell_b",
            "condition_a_id": "cond_a",
            "condition_b_id": "cond_b",
            "block_ids": list(block_ids),
            "metric": {"name": "gross_energy_j", "window_class": "request"},
        }

        def stochastic_factory(evidence_a, evidence_b, metric):
            return (
                (
                    StochasticVarianceTerm(
                        name="E_idle_mean_j2",
                        variance_a=1e-4,
                        variance_b=1e-4,
                        covariance_ab=0.0,
                        correlation_scope="independent_run",
                    ),
                ),
                [],
            )

        with mock.patch.object(
            engine, "_resolve_contrast_floor", return_value=[]
        ), mock.patch.object(
            engine, "randomization_check", return_value={"status": "not_applicable"}
        ), mock.patch.object(engine, "_randomization_alpha", return_value=0.05):
            prepared = engine._prepare_contrast(
                inputs,
                contrast,
                {},
                None,
                stochastic_factory,
                evidence_class="current",
            )

        self.assertNotIn(
            "anchor_energy_envelope_unrecorded", prepared["global_reason_codes"]
        )
        # Point estimation remains replay-readable, while every contributing
        # row carries the universal version barrier into claim evaluation.
        self.assertEqual(len(prepared["observations"]), 2)
        self.assertIsNotNone(prepared["estimate"])
        for row in prepared["block_rows"]:
            self.assertTrue(row["included"])
            self.assertIn("clock_anchor_unresolved", row["reason_codes"])
            self.assertNotIn(
                "anchor_energy_envelope_unrecorded", row["reason_codes"]
            )


class TransferFiducialAnalysisInputTests(unittest.TestCase):
    def test_transfer_bundle_refused_by_analysis_inputs(self) -> None:
        from joulewise.analysis_engine.inputs import (
            _transfer_classification_reason_codes,
        )
        from joulewise.transfer_fiducial import TransferFiducialClass

        class Reader:
            @staticmethod
            def transfer_fiducial_class():
                return TransferFiducialClass(True, True, False, True)

        self.assertEqual(
            _transfer_classification_reason_codes(Reader()),
            (
                "transfer_fiducial_claim_ineligible",
                "transfer_fiducial_class_inconsistent",
            ),
        )


if __name__ == "__main__":
    unittest.main()
