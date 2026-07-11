"""Pinned stdlib fixtures for P2-037 distributions and multiplicity."""

from __future__ import annotations

import math
import unittest

from joulewise.analysis_engine.distributions import (
    exact_sign_flip_p_value,
    student_t_cdf,
    student_t_quantile,
    two_sided_student_t_p_value,
)
from joulewise.analysis_engine.multiplicity import (
    adjust_p_values,
    benjamini_hochberg_adjust,
    holm_adjust,
)


class StudentTDistributionTests(unittest.TestCase):
    def test_cdf_matches_hand_computable_low_df_probabilities(self) -> None:
        # df=1 is Cauchy: F(1) = 1/2 + atan(1)/pi = 3/4.
        self.assertAlmostEqual(student_t_cdf(1.0, 1), 0.75, places=14)
        # For df=2 and t=2: F(t) = 1/2 + t/(2*sqrt(t^2+2)).
        expected_df2 = 0.5 + 2.0 / (2.0 * math.sqrt(6.0))
        self.assertAlmostEqual(student_t_cdf(2.0, 2), expected_df2, places=14)
        self.assertEqual(student_t_cdf(0.0, 4), 0.5)
        self.assertAlmostEqual(
            student_t_cdf(-2.0, 2),
            1.0 - expected_df2,
            places=14,
        )

    def test_quantile_pins_planned_small_sample_critical_values(self) -> None:
        # Planned n=5..10 means df=4..9 exactly (B4).
        critical_values = {
            4: 2.7764451051977944,
            5: 2.5705818356363155,
            6: 2.4469118511449700,
            7: 2.3646242515927853,
            8: 2.3060041352041667,
            9: 2.2621571627982055,
        }
        for df, expected in critical_values.items():
            with self.subTest(df=df):
                actual = student_t_quantile(0.975, df)
                self.assertAlmostEqual(actual, expected, places=9)
                self.assertAlmostEqual(student_t_cdf(actual, df), 0.975, places=12)

    def test_quantile_is_symmetric_and_round_trips(self) -> None:
        for df in (1, 4, 9, 30):
            with self.subTest(df=df):
                upper = student_t_quantile(0.9, df)
                lower = student_t_quantile(0.1, df)
                self.assertAlmostEqual(lower, -upper, places=12)
                self.assertAlmostEqual(student_t_cdf(lower, df), 0.1, places=12)
                self.assertAlmostEqual(student_t_cdf(upper, df), 0.9, places=12)

    def test_two_sided_p_value_pins_center_critical_and_zero_tail(self) -> None:
        self.assertEqual(two_sided_student_t_p_value(0.0, 4), 1.0)
        self.assertAlmostEqual(
            two_sided_student_t_p_value(2.7764451051977987, 4),
            0.05,
            places=12,
        )
        self.assertEqual(two_sided_student_t_p_value(1.0e308, 4), 0.0)
        self.assertEqual(student_t_cdf(-1.0e308, 4), 0.0)
        self.assertEqual(student_t_cdf(1.0e308, 4), 1.0)

    def test_invalid_distribution_inputs_fail_closed(self) -> None:
        for invalid in (float("nan"), float("inf"), -float("inf"), True):
            with self.subTest(value=invalid):
                with self.assertRaisesRegex(ValueError, "finite"):
                    student_t_cdf(invalid, 4)
        for invalid_df in (0, -1, 4.0, True):
            with self.subTest(df=invalid_df):
                with self.assertRaisesRegex(ValueError, "df"):
                    student_t_cdf(0.0, invalid_df)  # type: ignore[arg-type]
        for invalid_probability in (0.0, 1.0, -0.1, 1.1):
            with self.subTest(probability=invalid_probability):
                with self.assertRaisesRegex(ValueError, "probability"):
                    student_t_quantile(invalid_probability, 4)


class ExactSignFlipTests(unittest.TestCase):
    def test_six_equal_paired_deltas_have_exact_two_of_sixty_four_tail(self) -> None:
        # Only all-positive and all-negative signs attain |mean| >= 1.
        self.assertEqual(exact_sign_flip_p_value([1.0] * 6), 2 / 64)

    def test_pairing_happens_before_sign_flips(self) -> None:
        condition_a = [100.0, 200.0, 300.0, 400.0, 500.0, 600.0]
        condition_b = [101.0, 201.0, 301.0, 401.0, 501.0, 601.0]
        paired_deltas = [
            value_b - value_a
            for value_a, value_b in zip(condition_a, condition_b, strict=True)
        ]
        self.assertEqual(paired_deltas, [1.0] * 6)
        self.assertEqual(exact_sign_flip_p_value(paired_deltas), 0.03125)

    def test_zero_observed_mean_includes_every_sign_assignment(self) -> None:
        self.assertEqual(exact_sign_flip_p_value([1.0, -1.0] * 3), 1.0)

    def test_applicability_status_remains_a_caller_decision(self) -> None:
        # The primitive can enumerate n=5; B7 requires the caller to report
        # not_run rather than use this p-value below six exchangeable blocks.
        self.assertEqual(exact_sign_flip_p_value([1.0] * 5), 2 / 32)

    def test_sign_flip_limits_and_nonfinite_inputs_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "at most 20"):
            exact_sign_flip_p_value([1.0] * 21)
        with self.assertRaisesRegex(ValueError, "at least one"):
            exact_sign_flip_p_value([])
        with self.assertRaisesRegex(ValueError, r"deltas\[1\]"):
            exact_sign_flip_p_value([1.0, float("nan")])
        with self.assertRaisesRegex(ValueError, "tolerance"):
            exact_sign_flip_p_value([1.0], tolerance=-1.0)


class MultiplicityAdjustmentTests(unittest.TestCase):
    def test_holm_matches_hand_calculated_four_contrast_family(self) -> None:
        raw = {"a": 0.01, "b": 0.04, "c": 0.03, "d": 0.002}
        self.assertEqual(
            holm_adjust(raw, m=4),
            {"a": 0.03, "b": 0.06, "c": 0.06, "d": 0.008},
        )

    def test_bh_matches_hand_calculated_four_contrast_family(self) -> None:
        raw = {"a": 0.01, "b": 0.04, "c": 0.03, "d": 0.002}
        self.assertEqual(
            benjamini_hochberg_adjust(raw, m=4),
            {"a": 0.02, "b": 0.04, "c": 0.04, "d": 0.008},
        )

    def test_ties_are_id_sorted_then_monotone_for_both_methods(self) -> None:
        raw = {"z_tie": 0.01, "late": 0.04, "a_tie": 0.01, "missing": None}
        self.assertEqual(
            holm_adjust(raw, m=4),
            {"a_tie": 0.04, "late": 0.08, "missing": None, "z_tie": 0.04},
        )
        bh = benjamini_hochberg_adjust(raw, m=4)
        self.assertEqual(list(bh), ["a_tie", "late", "missing", "z_tie"])
        self.assertAlmostEqual(bh["a_tie"], 0.02, places=15)
        self.assertAlmostEqual(bh["z_tie"], 0.02, places=15)
        self.assertAlmostEqual(bh["late"], 0.16 / 3.0, places=15)
        self.assertIsNone(bh["missing"])

    def test_missing_p_values_remain_in_frozen_denominator(self) -> None:
        raw = {"a": 0.01, "b": 0.04, "c_missing": None, "d_missing": None}
        self.assertEqual(
            holm_adjust(raw, m=4),
            {"a": 0.04, "b": 0.12, "c_missing": None, "d_missing": None},
        )
        self.assertEqual(
            benjamini_hochberg_adjust(raw, m=4),
            {"a": 0.04, "b": 0.08, "c_missing": None, "d_missing": None},
        )
        with self.assertRaisesRegex(ValueError, "exactly m=4"):
            holm_adjust({"a": 0.01, "b": 0.04}, m=4)

    def test_zero_tail_ties_remain_zero_and_missing_never_rejects(self) -> None:
        raw = {"a_zero": 0.0, "z_zero": 0.0, "missing": None, "one": 1.0}
        for method in (holm_adjust, benjamini_hochberg_adjust):
            with self.subTest(method=method.__name__):
                adjusted = method(raw, m=4)
                self.assertEqual(adjusted["a_zero"], 0.0)
                self.assertEqual(adjusted["z_zero"], 0.0)
                self.assertIsNone(adjusted["missing"])
                self.assertEqual(adjusted["one"], 1.0)

        records = adjust_p_values(raw, method="holm", m=4, alpha=0.05)
        self.assertTrue(records["a_zero"]["rejected"])
        self.assertTrue(records["z_zero"]["rejected"])
        self.assertFalse(records["missing"]["rejected"])
        self.assertFalse(records["one"]["rejected"])

    def test_method_thresholds_and_exploratory_none_are_fail_closed(self) -> None:
        raw = {"a": 0.01, "b": 0.02, "c": 0.20, "missing": None}
        holm = adjust_p_values(raw, method="holm", m=4, alpha=0.05)
        self.assertEqual(holm["a"]["adjusted_p"], 0.04)
        self.assertTrue(holm["a"]["rejected"])
        self.assertFalse(holm["b"]["rejected"])

        bh = adjust_p_values(
            raw,
            method="benjamini_hochberg",
            m=4,
            q=0.05,
        )
        self.assertTrue(bh["a"]["rejected"])
        self.assertTrue(bh["b"]["rejected"])
        self.assertFalse(bh["c"]["rejected"])
        self.assertFalse(bh["missing"]["rejected"])

        exploratory = adjust_p_values(raw, method="exploratory_none", m=4)
        for record in exploratory.values():
            self.assertIsNone(record["adjusted_p"])
            self.assertFalse(record["rejected"])

    def test_invalid_family_or_method_inputs_fail_closed(self) -> None:
        invalid_probabilities = (-0.01, 1.01, float("nan"), float("inf"), True)
        for invalid in invalid_probabilities:
            with self.subTest(p=invalid):
                with self.assertRaisesRegex(ValueError, "p-value"):
                    holm_adjust({"a": invalid}, m=1)
        with self.assertRaisesRegex(ValueError, "unsupported"):
            adjust_p_values({"a": 0.1}, method="sidak", m=1, alpha=0.05)
        with self.assertRaisesRegex(ValueError, "q=None"):
            adjust_p_values({"a": 0.1}, method="holm", m=1, alpha=0.05, q=0.1)
        with self.assertRaisesRegex(ValueError, "alpha=None"):
            adjust_p_values(
                {"a": 0.1},
                method="benjamini_hochberg",
                m=1,
                alpha=0.05,
                q=0.1,
            )


if __name__ == "__main__":
    unittest.main()
