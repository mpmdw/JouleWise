"""Text-only worked examples; no import of harvest or its existing fixtures."""

import math
import unittest

from joulewise.twins.harvest_twin import (
    PowerInterval, ReferenceEnergy, anchor_envelope, calibration_bracket,
    endpoint_bound, member_arithmetic, overlap_energy, session_drift,
)


class RegisteredExamples(unittest.TestCase):
    def near(self, observed, expected):
        # 1e-7 J: below 1% of the finest printed half-unit (0.00005 J)
        # in these examples, and above 1e6 × float noise at their scale.
        self.assertAlmostEqual(observed, expected, delta=1e-7)

    def test_overlap_example_reg_0_4(self):
        rows = [PowerInterval(9.90, 10.03, 20), PowerInterval(10.03, 10.16, 30),
                PowerInterval(10.16, 10.29, 30)]
        self.near(overlap_energy(rows, 10, 10.25), 7.20)

    def test_bracket_examples_b6_1_7(self):
        self.near(calibration_bracket(.040, .030, .014531).operative_fiducial_s, .054531)
        self.near(calibration_bracket(.028, .048, .014531).operative_fiducial_s, .068)

    def test_exact_timing_examples_reg_0_10(self):
        rows = [PowerInterval(9.95, 10.08, 2), PowerInterval(10.08, 10.99, 30),
                PowerInterval(10.99, 11.12, 20), PowerInterval(11.12, 11.25, 4)]
        first = anchor_envelope(rows, 10.015, 11.055, .0457, .0003, .002)
        self.near(first.point_j, 28.730)
        self.near(first.max_abs_delta_j, 1.048)
        # The local edge-power approximation incorrectly gives 1.048 here.
        second = anchor_envelope(rows, 10.015, 11.000, .0457, .0003, .002)
        self.near(second.max_abs_delta_j, 1.428)

    def test_internal_common_shift_breakpoint(self):
        rows = [PowerInterval(0, 1, 0), PowerInterval(1, 2, 10), PowerInterval(2, 3, 0)]
        env = anchor_envelope(rows, 1, 2, 0, 0, .5)
        self.near(env.maximum_j, 10)
        self.near(env.minimum_j, 5)
        # Both endpoints of the common-shift range give 5, not the max 10.

    def test_epoch_coordinates_keep_small_shifts_and_rounded_supports(self):
        epoch = 1790000000
        rows = [PowerInterval(epoch + a, epoch + b, p) for a, b, p in
                [(0, 1, 2), (1, 2, 40), (2, 3, 10), (3, 4, 2)]]
        env = anchor_envelope(rows, epoch + 1.5, epoch + 2.5, .0457, .0003, .002)
        self.near(env.max_abs_delta_j, 2.36)
        rounded = [PowerInterval(epoch, epoch + 1, 2),
                   PowerInterval(math.nextafter(epoch + 1, -math.inf), epoch + 2, 3)]
        self.near(overlap_energy(rounded, epoch, epoch + .5), 1)

    def test_member_bounds_and_idle_subtraction(self):
        rows = [PowerInterval(0, 10, 8)]
        member = member_arithmetic(rows, (2, 8), {"prefill": (2, 3), "decode": (3, 8)},
                                   idle_power_w=2, operative_fiducial_s=.1,
                                   wall_minus_monotonic_span_s=0,
                                   effective_clock_bound_s=.01,
                                   whole_window_drift_allowance_j=.8)
        self.near(member.gross_energy_j, 48)
        self.near(member.idle_subtracted_energy_j, 36)
        self.near(member.phase_energy_j["prefill"], 8)
        self.near(member.phase_energy_j["decode"], 40)
        for terms in member.phase_bounds_j.values():
            self.near(terms["E_clock_anchor_shift_bound_j"], 1.6)
            self.assertEqual(terms["E_interpolation_joint_edge_bound_j"], 0)
            self.near(terms["E_whole_window_drift_allowance_j"], .4)

    def test_reference_example_b6_1_8(self):
        corpus = [36.42, 36.95, 36.61, 37.18, 36.80, 36.55,
                  37.02, 36.71, 36.88, 36.39, 37.10, 36.67]
        refs = lambda xs: [ReferenceEnergy(x, x - 5) for x in xs]
        start, end = refs([36.70, 36.92, 36.58]), refs([37.01, 36.84, 37.12])
        result = session_drift(refs(corpus), start, end, ReferenceEnergy(37.05, 32.05))
        self.assertTrue(result.passed)
        self.near(result.gross.bound_j, .64666666666667)
        self.near(result.gross.difference_j, .25666666666667)
        end[-1] = None
        lost = session_drift(refs(corpus), start, end, None)
        self.near(lost.gross.bound_j, .695)
        self.near(lost.gross.difference_j, .19166666666667)
        self.near(lost.gross.spread_j, lost.gross.difference_j)
        self.near(lost.member_drift_allowance_j, .3475)

    def test_both_families_decide_and_block_minima_differ(self):
        corpus = [ReferenceEnergy(10 + i / 100, 5 + i / 100) for i in range(6)]
        start = [ReferenceEnergy(10, 5)] * 3
        end = [ReferenceEnergy(10, 6)] * 3
        result = session_drift(corpus, start, end, None, block=6)
        self.assertTrue(result.gross.passed)
        self.assertFalse(result.idle_subtracted.passed)
        self.assertFalse(result.passed)
        with self.assertRaises(ValueError):
            session_drift(corpus, start, end, None, block=5)

    def test_count_adjustment_symmetric_and_equality_passes(self):
        corpus = list(range(12))
        self.assertEqual(endpoint_bound(corpus, 2, 3), endpoint_bound(corpus, 3, 2))
        flat = [ReferenceEnergy(10, 5)] * 12
        self.assertTrue(session_drift(flat, flat[:2], flat[:3], None).passed)

    def test_first_twelve_clean_in_committed_order(self):
        flat = [ReferenceEnergy(10, 5)] * 12
        result = session_drift([None, *flat, ReferenceEnergy(1e9, 1e9)], flat[:3], flat[:3], None)
        self.assertEqual(result.gross.corpus_n, 12)
        self.assertEqual(result.gross.bound_j, 0)

    def test_invalid_evidence(self):
        for power in (-1, math.inf, math.nan, True):
            with self.assertRaises(ValueError):
                PowerInterval(0, 1, power)
        with self.assertRaises(ValueError):
            overlap_energy([PowerInterval(0, 2, 1), PowerInterval(1, 3, 1)], 0, 1)
        with self.assertRaises(ValueError):
            calibration_bracket(.01, .02, -1)
        with self.assertRaises(ValueError):
            endpoint_bound([1] * 12, True, 3)
        flat = [ReferenceEnergy(1, -1)] * 12
        with self.assertRaises(ValueError):
            session_drift(flat, flat[:1], flat[:3], None)


if __name__ == "__main__":
    unittest.main()
