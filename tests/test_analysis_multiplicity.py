"""Pinned stdlib fixtures for P2-037 distributions and multiplicity."""

from __future__ import annotations

import itertools
import math
import random
import unittest
from fractions import Fraction

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
from joulewise.analysis_engine.sensitivity import randomization_check


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
    TIE_WORLDS = {
        "A": ("151.1", "-144.4", "-160.0", "8.9", "-38.9", "-199.3"),
        "B": ("146.0", "43.7", "-124.6", "-122.6", "152.8", "50.7"),
    }
    TIE_DECIMAL_P_VALUES = {"A": 18 / 64, "B": 42 / 64}
    GRID_WORLDS = {
        246: (
            (
                "1773.4", "1117.6", "1207.5", "1150.1", "1710.0",
                "1566.2", "1801.5", "1925.3", "1590.7", "414.2",
            ),
            (
                "1786.0", "1121.0", "1214.3", "1145.0", "1711.3",
                "1567.8", "1803.2", "1929.1", "1591.2", "419.2",
            ),
            52 / 1024,
        ),
        264: (
            (
                "501.2", "1142.5", "1990.6", "1356.9", "710.6",
                "1881.0", "1550.0", "278.4", "761.1", "272.4",
            ),
            (
                "506.4", "1151.1", "1987.0", "1360.2", "716.9",
                "1889.5", "1553.0", "274.7", "765.1", "273.0",
            ),
            54 / 1024,
        ),
    }

    @staticmethod
    def _oracle_p_values(exact_values: tuple[Fraction, ...]) -> tuple[float, float]:
        """Independently count exact and band tails using rational sums."""
        observed = abs(sum(exact_values))
        # The ruled relative width is K times binary64 unit roundoff.
        tau = Fraction(10**6, 2**53) * sum(abs(value) for value in exact_values)
        band_threshold = observed - tau
        # Reuse rational half-sums; still enumerate every assignment with
        # itertools.product, without the production integer lift or threshold.
        midpoint = len(exact_values) // 2
        partial_sums = [
            tuple(
                sum(terms, Fraction(0))
                for terms in itertools.product(*[(-value, value) for value in half])
            )
            for half in (exact_values[:midpoint], exact_values[midpoint:])
        ]
        exact_count = 0
        band_count = 0
        for left, right in itertools.product(*partial_sums):
            magnitude = abs(left + right)
            if magnitude >= observed:
                exact_count += 1
                band_count += 1
            elif magnitude >= band_threshold:
                band_count += 1
        assignments = 1 << len(exact_values)
        return exact_count / assignments, band_count / assignments

    @classmethod
    def _decimal_oracle(cls, texts: tuple[str, ...]) -> float:
        return cls._oracle_p_values(tuple(Fraction(text) for text in texts))[0]

    @classmethod
    def _fraction_oracles(cls, values: list[float]) -> tuple[float, float]:
        """Return the exact binary oracle and the band oracle in one pass."""
        return cls._oracle_p_values(tuple(Fraction(value) for value in values))

    @staticmethod
    def _grid_deltas(
        condition_a: tuple[str, ...], condition_b: tuple[str, ...]
    ) -> tuple[tuple[Fraction, ...], list[float], list[float]]:
        pairs = tuple(zip(condition_a, condition_b, strict=True))
        decimal_deltas = tuple(Fraction(b) - Fraction(a) for a, b in pairs)
        joule_deltas = [float(b) - float(a) for a, b in pairs]
        # All source values are on a 0.1 J grid.  One tenth of a joule is
        # exactly 100 mJ; integer grid conversion precedes float subtraction.
        millijoule_deltas = [
            float(int(Fraction(b) * 10) * 100)
            - float(int(Fraction(a) * 10) * 100)
            for a, b in pairs
        ]
        return decimal_deltas, joule_deltas, millijoule_deltas

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

    def test_tie_worlds_match_decimal_truth_and_band_oracle(self) -> None:
        for name, binary_expected in (("A", 16 / 64), ("B", 40 / 64)):
            texts = self.TIE_WORLDS[name]
            values = [float(text) for text in texts]
            expected = self.TIE_DECIMAL_P_VALUES[name]
            self.assertEqual(self._decimal_oracle(texts), expected)
            self.assertEqual(self._fraction_oracles(values)[0], binary_expected)
            for scale in (1, 1 / 1024, 1024, 1000, 1 / 1000, 1 / 3600):
                scaled = [value * scale for value in values]
                with self.subTest(world=name, scale=scale):
                    binary_p, band_p = self._fraction_oracles(scaled)
                    actual = exact_sign_flip_p_value(scaled)
                    self.assertEqual(actual, expected)
                    self.assertEqual(actual, band_p)
                    self.assertGreaterEqual(actual, binary_p)

    def test_grid_recorded_worlds_keep_nonrejection_in_joules_and_millijoules(self) -> None:
        design = {
            "scheme": "paired_label_swap_within_block",
            "exchangeability": "within_block",
        }
        for seed, (condition_a, condition_b, expected) in self.GRID_WORLDS.items():
            decimal_deltas, joules, millijoules = self._grid_deltas(
                condition_a, condition_b
            )
            self.assertEqual(self._oracle_p_values(decimal_deltas)[0], expected)
            for unit, values in (("J", joules), ("mJ", millijoules)):
                with self.subTest(seed=seed, unit=unit):
                    binary_p, band_p = self._fraction_oracles(values)
                    self.assertEqual(binary_p, 50 / 1024 if unit == "J" else expected)
                    actual = exact_sign_flip_p_value(values)
                    self.assertEqual(actual, expected)
                    self.assertEqual(actual, band_p)
                    self.assertGreaterEqual(actual, binary_p)
                    result = randomization_check(values, design, alpha=0.05)
                    self.assertEqual(result["exact_two_sided_p"], expected)
                    self.assertIs(result["rejects"], False)

    def test_band_boundary_includes_half_tau_and_excludes_twice_tau(self) -> None:
        relative_band = Fraction(10**6, 2**53)
        # For [4 - b, b], the observed sum and absolute total are both 4;
        # the other absolute sum is 4 - 2b.
        # Thus b = relative_band gives gap = tau/2, while b = 4*relative_band
        # gives gap = 2*tau.  Every constructed input is exactly binary.
        for multiplier, gap_ratio, expected in (
            (1, Fraction(1, 2), 1.0),
            (4, Fraction(2), 2 / 4),
        ):
            small = relative_band * multiplier
            exact_values = (Fraction(4) - small, small)
            values = [float(value) for value in exact_values]
            with self.subTest(gap_over_tau=gap_ratio):
                self.assertEqual(tuple(Fraction(value) for value in values), exact_values)
                observed = abs(sum(exact_values))
                tau = relative_band * sum(abs(value) for value in exact_values)
                alternate = abs(exact_values[0] - exact_values[1])
                self.assertEqual(observed - alternate, gap_ratio * tau)
                binary_p, band_p = self._fraction_oracles(values)
                self.assertEqual(binary_p, 2 / 4)
                self.assertEqual(band_p, expected)
                self.assertEqual(exact_sign_flip_p_value(values), expected)

    def test_power_of_two_rescaling_preserves_p_value(self) -> None:
        worlds = [
            [float(text) for text in texts] for texts in self.TIE_WORLDS.values()
        ] + [
            [3.0, -2.0, 1.0, 0.0, -4.0, 7.0],
            [0.125, -0.25, 0.5, -1.0, 2.0, 4.0],
        ]
        for values in worlds:
            for scale in (1 / 1024, 1024):
                scaled = [value * scale for value in values]
                with self.subTest(values=values, scale=scale):
                    self.assertTrue(
                        all(
                            Fraction(result) == Fraction(value) * Fraction(scale)
                            for value, result in zip(values, scaled, strict=True)
                        )
                    )
                    self.assertEqual(
                        exact_sign_flip_p_value(scaled), exact_sign_flip_p_value(values)
                    )
                    self.assertEqual(
                        exact_sign_flip_p_value(scaled), self._fraction_oracles(scaled)[1]
                    )

    def test_real_unit_conversions_match_decimal_truth(self) -> None:
        worlds = [
            (name, [float(text) for text in texts], self._decimal_oracle(texts))
            for name, texts in self.TIE_WORLDS.items()
        ]
        for seed, (condition_a, condition_b, expected) in self.GRID_WORLDS.items():
            decimal_deltas, joules, _ = self._grid_deltas(condition_a, condition_b)
            self.assertEqual(self._oracle_p_values(decimal_deltas)[0], expected)
            worlds.append((str(seed), joules, expected))
        # Convert J to mJ, kJ and Wh by multiplying the supplied floats.
        for name, values, expected in worlds:
            for scale in (1000, 1 / 1000, 1 / 3600):
                with self.subTest(world=name, scale=scale):
                    scaled = [value * scale for value in values]
                    binary_p, band_p = self._fraction_oracles(scaled)
                    actual = exact_sign_flip_p_value(scaled)
                    self.assertEqual(actual, expected)
                    self.assertEqual(actual, band_p)
                    self.assertGreaterEqual(actual, binary_p)

    def test_continuous_noise_worlds_are_unchanged(self) -> None:
        for seed in range(300):
            rng = random.Random(seed)
            values = [rng.gauss(2.0, 3.0) for _ in range(12)]
            expected = exact_sign_flip_p_value(values)
            # Thirty seeds check both independent oracles; all 300 retain
            # the production-to-production rescaling property checks.
            if seed < 30:
                binary_p, band_p = self._fraction_oracles(values)
                with self.subTest(seed=seed, scale=1):
                    self.assertEqual(expected, band_p)
                    self.assertEqual(expected, binary_p)
                    self.assertGreaterEqual(expected, binary_p)
            for scale in (1 / 1024, 1024, 1000):
                scaled = [value * scale for value in values]
                with self.subTest(seed=seed, scale=scale):
                    actual = exact_sign_flip_p_value(scaled)
                    self.assertEqual(actual, expected)

    def test_caller_reports_exact_p_value_and_rejection_for_both_designs(self) -> None:
        block_ids = [f"b{index}" for index in range(6)]
        designs = [
            {"scheme": "paired_label_swap_within_block", "exchangeability": "within_block"},
            {
                "scheme": "stratified_paired_label_swap",
                "exchangeability": "within_named_strata",
                "named_strata": [
                    {"stratum_id": "early", "block_ids": block_ids[:3]},
                    {"stratum_id": "late", "block_ids": block_ids[3:]},
                ],
            },
        ]
        for name, texts in self.TIE_WORLDS.items():
            values = [float(text) for text in texts]
            expected = self._decimal_oracle(texts)
            self.assertEqual(expected, self.TIE_DECIMAL_P_VALUES[name])
            for scale in (1, 1 / 1024, 1024, 1000):
                scaled = [value * scale for value in values]
                self.assertEqual(self._fraction_oracles(scaled)[1], expected)
                for design in designs:
                    for alpha in (0.05, expected):
                        with self.subTest(world=name, scale=scale, design=design, alpha=alpha):
                            result = randomization_check(
                                scaled, design, alpha=alpha, block_ids=block_ids
                            )
                            self.assertEqual(result["exact_two_sided_p"], expected)
                            self.assertEqual(result["rejects"], expected <= alpha)

    def test_subnormal_deltas_and_exact_zero_ties(self) -> None:
        tiny = math.ulp(0.0)
        for values, expected in (
            ([tiny] * 6, 2 / 64),
            ([tiny, -tiny] * 3, 1.0),
            ([0.0, -0.0] * 3, 1.0),
            # Here tau is about 2.2e190, far larger than the 1.0 term.
            ([1.0e300, -1.0e300, tiny, -tiny, 0.0, 1.0], 1.0),
        ):
            with self.subTest(values=values):
                self.assertEqual(self._fraction_oracles(values)[1], expected)
                self.assertEqual(exact_sign_flip_p_value(values), expected)

    def test_sign_flip_limits_and_nonfinite_inputs_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "at most 20"):
            exact_sign_flip_p_value([1.0] * 21)
        with self.assertRaisesRegex(ValueError, "at least one"):
            exact_sign_flip_p_value([])
        with self.assertRaisesRegex(ValueError, r"deltas\[1\]"):
            exact_sign_flip_p_value([1.0, float("nan")])
        with self.assertRaisesRegex(ValueError, "finite derived sums"):
            exact_sign_flip_p_value([1.0e308, 1.0e308])


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
