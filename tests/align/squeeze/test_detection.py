import math
import unittest

from joulewise.align.squeeze.detection import (
    JointScore, Threshold, conformal_pvalue, conformal_threshold,
    detection_surface, max_threshold, order_threshold, pareto_frontier,
    separate_channel_fpr_bounds,
)

try:
    import numpy as np
except ImportError:
    np = None


class ThresholdTests(unittest.TestCase):
    def test_strict_max_and_ties(self):
        t = max_threshold([1, 3, 3])
        self.assertEqual(t.value, 3)
        self.assertFalse(t.exceeds(3))
        self.assertTrue(t.exceeds(math.nextafter(3, math.inf)))
        self.assertEqual(conformal_pvalue([1, 3, 3], 3), 0.75)
        self.assertEqual(conformal_pvalue([1, 3, 3], 4), 0.25)

    def test_exact_max_rules_at_requested_sizes(self):
        for m in (20, 28, 39):
            with self.subTest(m=m):
                t = max_threshold(range(m))
                self.assertEqual((t.rank, t.value), (m, m-1))
                self.assertEqual(t.marginal_fpr_bound, 1/(m+1))

    def test_conformal_plus_one_not_empirical_quantile(self):
        self.assertEqual(conformal_threshold(range(20)).rank, 20)
        self.assertEqual(conformal_threshold(range(39)).rank, 38)
        self.assertEqual(conformal_threshold(range(39)).marginal_fpr_bound, 0.05)
        # An m=18 sample cannot support a finite .05 split-conformal cut.
        self.assertEqual(conformal_threshold(range(18)).value, math.inf)
        self.assertEqual(conformal_threshold([1, 2], alpha=0).value, math.inf)

    def test_rank_symmetry_enumeration(self):
        # Exhaustive identity of the future rank among m+1 distinct values.
        for m in (3, 20, 39):
            for k in (1, m-1, m, m+1):
                alarms = 0
                for future in range(m+1):
                    cal = [v for v in range(m+1) if v != future]
                    t = order_threshold(cal, k)
                    alarms += t.exceeds(future)
                self.assertEqual(alarms/(m+1), t.marginal_fpr_bound)

    def test_pvalue_and_threshold_equivalence(self):
        for cal in ([0]*20, list(range(20)), list(range(39))):
            t = conformal_threshold(cal, .05)
            for x in (0, 3, 18, 19, 20, 37, 38, 40):
                self.assertEqual(t.exceeds(x), conformal_pvalue(cal, x) <= .05)

    def test_realized_tail_is_not_marginal_tail(self):
        t = max_threshold(range(20))
        self.assertAlmostEqual(t.realized_fpr_upper(), 1-0.1**(1/20))
        self.assertGreater(t.realized_fpr_upper(), .10)
        self.assertGreater(t.realized_fpr_upper(), t.marginal_fpr_bound)
        self.assertEqual(t.cohort_any_fpr_bound(100), 1)
        with self.assertRaises(ValueError):
            order_threshold(range(20), 19).realized_fpr_upper()

    def test_or_of_separate_maxima_needs_union_bound(self):
        t = max_threshold(range(39))
        self.assertEqual(separate_channel_fpr_bounds(t, t), {"or": .05, "and": .025})
        # With anticorrelated channels, two distinct future ranks alarm.
        alarms = 0
        for future in range(21):
            benign = [v for v in range(21) if v != future]
            monitor = max_threshold(benign)
            energy = max_threshold([-v for v in benign])
            alarms += monitor.exceeds(future) or energy.exceeds(-future)
        self.assertEqual(alarms/21, 2/21)

    def test_invalid_scores_and_parameters_fail_closed(self):
        for values in ([], [math.nan], [math.inf], [-math.inf], [True], ["1"]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                max_threshold(values)
        for m in (0, -1, 3.5, True):
            with self.assertRaises(ValueError):
                Threshold(0, m, 1)
        for alpha in (-1, 1, math.nan, 2):
            with self.assertRaises(ValueError):
                conformal_threshold([1, 2], alpha)
        with self.assertRaises(ValueError):
            max_threshold([0]).exceeds(math.nan)


@unittest.skipUnless(np is not None, "optional NumPy extra unavailable")
class JointTests(unittest.TestCase):
    def test_joint_calibration_exact_rank_symmetry_with_dependence(self):
        scores = np.column_stack((np.arange(21), -np.arange(21)))
        rule = JointScore(2, monitor_location=10, mode="max")
        # Deliberately dependent channels; joint score remains one frozen map.
        joint = rule(scores)
        count = 0
        for i in range(21):
            t = rule.calibrate(np.delete(scores, i, axis=0))
            count += t.exceeds(joint[i])
        self.assertLessEqual(count, 1)

    def test_frozen_score_shapes_and_weights(self):
        scores = np.array([[2, 6], [-1, 3]])
        np.testing.assert_array_equal(JointScore(3)(scores), [2, 1])
        np.testing.assert_array_equal(JointScore(3, mode="min")(scores), [2, -1])
        np.testing.assert_array_equal(JointScore(3, mode="sum")(scores), [4, 0])
        np.testing.assert_array_equal(JointScore(3, energy_weight=2)(scores), [4, 2])
        self.assertEqual(JointScore(3)(np.ones((2, 4, 2))).shape, (2, 4))

    def test_grid_or_and_and_units(self):
        scores = [[0, 0], [1, 3], [2, 1], [2, 4]]
        actual = detection_surface(scores, [1, 2], [1, 3])
        np.testing.assert_array_equal(actual, [[.75, .5], [.5, .25]])
        actual = detection_surface(scores, [1, 2], [1, 3], mode="and")
        np.testing.assert_array_equal(actual, [[.25, .25], [0, 0]])

    def test_pareto_tradeoff_and_duplicates(self):
        points = [[.1, .8], [.5, .5], [.8, .1], [.9, .9], [.5, .5]]
        np.testing.assert_array_equal(pareto_frontier(points), [True, True, True, False, True])

    def test_missing_and_invalid_joint_inputs(self):
        for value in (0, -1, math.inf):
            with self.assertRaises(ValueError):
                JointScore(value)
        for a in ([1], [[0, math.nan]], np.zeros((2, 3))):
            with self.assertRaises(ValueError):
                JointScore(1)(a)
        with self.assertRaises(ValueError):
            detection_surface([], [1], [1])
        with self.assertRaises(ValueError):
            detection_surface([[0, 0]], [], [1])


if __name__ == "__main__":
    unittest.main()
