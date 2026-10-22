"""Independent arithmetic and seeded sampling checks for alignment statistics."""
from __future__ import annotations

import math
import random
import unittest
from statistics import NormalDist
from unittest.mock import patch

from joulewise.align import stats

from joulewise.align.stats import (
    auc, cluster_bootstrap_auc_ci, delong_ci, fit_logistic, paired_auc_difference,
)


class StatisticsTests(unittest.TestCase):
    def close(self, actual, expected):
        # No uncertainty is printed: use the brief\'s 1e-6 relative bar.
        # At zero, relative error is undefined; 1e6 binary64 ulps at unit
        # scale resolves only arithmetic noise, well below 1e-6.
        bar = 1e-6 * abs(expected) if expected else 1e6 * math.ulp(1.0)
        self.assertLessEqual(abs(actual - expected), bar)

    def test_auc_ties_and_orientation(self):
        cases = [
            ([1, 2, 3, 4], [0, 0, 1, 1], 1),
            ([4, 3, 2, 1], [0, 0, 1, 1], 0),
            ([2, 2, 2, 2], [0, 0, 1, 1], 0.5),
            ([0, 1, 1, 2], [0, 0, 1, 1], 0.875),
        ]
        for scores, labels, expected in cases:
            with self.subTest(scores=scores):
                self.close(auc(scores, labels), expected)

    def test_auc_independent_pair_enumeration(self):
        rng = random.Random(29)
        # Integer scores force ties; 150 episodes resembles the 30-seed pilot.
        scores = [rng.randrange(20) for _ in range(150)]
        labels = [i % 2 for i in range(150)]
        comparisons = [float(a > b) + 0.5 * (a == b)
                       for a, ya in zip(scores, labels) if ya
                       for b, yb in zip(scores, labels) if not yb]
        self.close(auc(scores, labels), sum(comparisons) / len(comparisons))

    def test_delong_closed_form_logit(self):
        # Positives 1,3,5 versus negatives 0,2,4: placements are 1/3,2/3,1
        # in each class, sample variance 1/9, AUC variance 2/27.
        scores, labels = list(range(6)), [0, 1, 0, 1, 0, 1]
        estimate = 2 / 3
        z = NormalDist().inv_cdf(0.975)
        delta = z * math.sqrt(2 / 27) / (estimate * (1 - estimate))
        center = math.log(2)
        expected = tuple(1 / (1 + math.exp(-v)) for v in (center - delta, center + delta))
        for actual, target in zip(delong_ci(scores, labels), expected):
            self.close(actual, target)

    def test_paired_delong_closed_form(self):
        scores, labels = list(range(6)), [0, 1, 0, 1, 0, 1]
        result = paired_auc_difference(scores, [-s for s in scores], labels)
        # Reversing scores doubles each placement deviation: variance 8/27.
        se = math.sqrt(8 / 27)
        expected = (1 / 3, se, math.erfc((1 / 3) / (se * math.sqrt(2))))
        for actual, target in zip(result, expected):
            self.close(actual, target)
        same = paired_auc_difference(scores, scores, labels)
        self.close(same[0], 0)
        self.close(same[1], 0)
        self.close(same[2], 1)
        self.assertIn("zero_variance", same.flags)

    def test_paired_order_and_tie_covariance(self):
        a = [1, 2, 2, 4, 5, 5, 7, 8]
        b = [2, 1, 4, 3, 5, 7, 6, 6]
        labels = [0, 1, 0, 1, 0, 1, 0, 1]
        def placements(values):
            positive = [s for s, y in zip(values, labels) if y]
            negative = [s for s, y in zip(values, labels) if not y]
            return ([sum((p > n) + (p == n) / 2 for n in negative) / len(negative) for p in positive],
                    [sum((p > n) + (p == n) / 2 for p in positive) / len(positive) for n in negative])
        ap, an = placements(a)
        bp, bn = placements(b)
        def var(values):
            mean = sum(values) / len(values)
            return sum((v - mean) ** 2 for v in values) / (len(values) - 1)
        expected_se = math.sqrt(var([x - y for x, y in zip(ap, bp)]) / 4
                                + var([x - y for x, y in zip(an, bn)]) / 4)
        difference, se, _ = paired_auc_difference(a, b, labels)
        self.close(difference, auc(a, labels) - auc(b, labels))
        self.close(se, expected_se)

    def test_logistic_penalised_separable_known_optimum(self):
        # Standardised x is ±1, six examples per side. Symmetry makes intercept
        # zero. For b=log(3), sigmoid(b)=3/4; derivative -12/(1+exp(b))+l2*b=0
        # when l2=3/log(3). Strict positive curvature proves a unique optimum.
        target = math.log(3)
        penalty = 3 / target
        X = [[100 + 20 * sign, 5] for sign in [-1] * 6 + [1] * 6]
        beta = fit_logistic(X, [0] * 6 + [1] * 6, l2=penalty)
        self.assertFalse(beta.flags)
        self.close(beta[0], -5 * target)
        self.close(beta[1], target / 20)
        self.close(beta[2], 0)
        # Independently solve the scalar score equation by bracketed bisection.
        lo, hi = 0.0, 12 / penalty
        for _ in range(60):  # 60 halvings exceed the 53-bit float mantissa.
            mid = (lo + hi) / 2
            if penalty * mid - 12 / (1 + math.exp(mid)) < 0:
                lo = mid
            else:
                hi = mid
        self.close(beta[1] * 20, (lo + hi) / 2)

    def test_logistic_intercept_unpenalised_and_scale(self):
        labels = [0] * 3 + [1] * 9
        beta = fit_logistic([[] for _ in labels], labels, l2=100)
        self.close(beta[0], math.log(3))
        X = [[x] for x in (-3, -2, -1, 0, 1, 2, 3, 4)]
        y = [0, 1, 0, 0, 1, 0, 1, 1]
        a = fit_logistic(X, y, l2=2)
        b = fit_logistic([[7 + 1000 * row[0]] for row in X], y, l2=2)
        for row in X:
            self.close(a[0] + a[1] * row[0], b[0] + b[1] * (7 + 1000 * row[0]))

    def test_undefined_analyses_are_flagged(self):
        bad = auc([1, math.nan], [0, 1])
        self.assertTrue(math.isnan(bad))
        self.assertIn("nonfinite_score", bad.flags)
        for result in (delong_ci([1], [1]), paired_auc_difference([1], [1], [1]),
                       cluster_bootstrap_auc_ci([1], [1], ["a"]),
                       fit_logistic([[1], [2]], [0, 0], l2=1)):
            self.assertTrue(result.flags)
        self.assertIn("insufficient_class_size", delong_ci([0, 1], [0, 1]).flags)
        self.assertIn("boundary_degenerate", delong_ci([0, 0, 1, 1], [0, 0, 1, 1]).flags)
        self.assertIn("invalid_level", delong_ci([0, 1], [0, 1], level=1).flags)
        self.assertIn("invalid_shape", fit_logistic([[1], [1, 2]], [0, 1], l2=1).flags)
        self.assertIn("invalid_l2", fit_logistic([[1], [2]], [0, 1], l2=-1).flags)
        result = cluster_bootstrap_auc_ci([0, 1], [0, 1], ["a"], n_boot=10)
        self.assertIn("length_mismatch", result.flags)

    def test_cluster_bootstrap_matches_literal_resampling(self):
        scores = [0, 2, 1, 3, 2, 5, 1, 4, 4]
        labels = [0, 1, 0, 1, 0, 1, 0, 1, 1]
        groups = ["a", "a", "b", "b", "b", "c", "c", "c", "c"]
        seed, count = 41, 2000  # Fixed computational budget, explicit API parameter.
        rng = random.Random(seed)
        values = []
        for _ in range(count):
            indices = [i for _ in range(3) for name in [("a", "b", "c")[rng.randrange(3)]]
                       for i, group in enumerate(groups) if group == name]
            # Independent U enumeration after literally duplicating whole groups.
            pos = [scores[i] for i in indices if labels[i]]
            neg = [scores[i] for i in indices if not labels[i]]
            values.append(sum((p > n) + (p == n) / 2 for p in pos for n in neg) / (len(pos) * len(neg)))
        values.sort()
        def percentile(probability):
            rank = (count - 1) * probability
            lower = math.floor(rank)
            return values[lower] + (rank - lower) * (values[math.ceil(rank)] - values[lower])
        actual = cluster_bootstrap_auc_ci(scores, labels, groups, n_boot=count, seed=seed)
        self.close(actual[0], percentile(0.025))
        self.close(actual[1], percentile(0.975))
        self.assertEqual(actual[2], count)
        # Identical inputs and RNG path require bit-identical reproducibility.
        self.assertEqual(actual, cluster_bootstrap_auc_ci(scores, labels, groups, n_boot=count, seed=seed))

    def test_bootstrap_single_class_draws_and_atoms(self):
        result = cluster_bootstrap_auc_ci([0, 1], [0, 1], ["neg", "pos"], n_boot=100, seed=2)
        self.assertTrue(any(f.startswith("single_class_resamples:") for f in result.flags))
        constant = cluster_bootstrap_auc_ci([1, 1, 1, 1], [0, 1, 0, 1], ["a", "a", "b", "b"])
        self.close(constant[0], 0.5)
        self.close(constant[1], 0.5)
        self.assertIn("degenerate_bootstrap", constant.flags)

    def test_automatic_budget_exhaustion_is_flagged(self):
        # Four draws deliberately exhaust the configurable compute budget;
        # this fixture tests the flag, not inferential precision.
        with patch.object(stats, "AUTO_BOOTSTRAP_MAX_REPLICATES", 4):
            result = cluster_bootstrap_auc_ci(
                [0, 1, 0, 3, 2, 1, 0, 4, 3, 2], [0, 1] * 5,
                [str(i // 2) for i in range(10)], seed=9)
        self.assertEqual(result[2], 4)
        self.assertIn("bootstrap_precision_target_not_met", result.flags)

    def test_automatic_bootstrap_precision(self):
        # Five mixed-class groups produce a discrete, production-shaped cluster
        # distribution. Verify endpoint SE using a literal independent replay.
        scores = [0, 1, 0, 3, 2, 1, 0, 4, 3, 2]
        labels = [0, 1] * 5
        groups = [str(i // 2) for i in range(10)]
        result = cluster_bootstrap_auc_ci(scores, labels, groups, seed=9)
        B = result[2]
        rng = random.Random(9)
        values = []
        for _ in range(B):
            indices = [j for _ in range(5) for k in [rng.randrange(5)] for j in (2 * k, 2 * k + 1)]
            pos = [scores[i] for i in indices if labels[i]]
            neg = [scores[i] for i in indices if not labels[i]]
            values.append(sum((a > b) + (a == b) / 2 for a in pos for b in neg) / 25)
        values.sort()
        def q(p):
            index = (B - 1) * p
            lower = int(index)
            return values[lower] + (index - lower) * (values[min(lower + 1, B - 1)] - values[lower])
        half = (result[1] - result[0]) / 2
        bandwidth = min(0.025, B ** (-1 / 5))
        rank_se = math.sqrt(0.025 * 0.975 / B)
        for p in (0.025, 0.975):
            span = q(p + bandwidth) - q(p - bandwidth)
            error = rank_se * span / (2 * bandwidth)
            if span == 0:
                error = (q(p + rank_se) - q(p - rank_se)) / 2
            # Required MC endpoint bar: 1% of returned interval half-width.
            self.assertLess(error, 0.01 * half)


def coverage_counts(worlds=200, n_boot=799):
    """Normal(0,1) benign vs Normal(0.7,1) sabotage: true AUC Φ(0.7/√2).

    One hundred independent task pairs hold three examples of each class. Scores
    within a group are independent here, so DeLong and cluster intervals both
    estimate the stated marginal AUC. n_boot is an explicit compute budget.
    """
    truth = NormalDist().cdf(0.7 / math.sqrt(2))
    hits = [0, 0]
    for seed in range(worlds):
        rng = random.Random(seed)
        labels = [j % 2 for _ in range(100) for j in range(6)]
        scores = [rng.gauss(0.7 * label, 1) for label in labels]
        groups = [str(i // 6) for i in range(len(labels))]
        intervals = (delong_ci(scores, labels),
                     cluster_bootstrap_auc_ci(scores, labels, groups, n_boot=n_boot, seed=seed))
        for i, interval in enumerate(intervals):
            hits[i] += interval[0] <= truth <= interval[1]
    return truth, hits


class CoverageTests(unittest.TestCase):
    def test_seeded_interval_coverage(self):
        worlds = 200
        truth, counts = coverage_counts(worlds)
        print(f"INTERVAL COVERAGE truth={truth:.9f} worlds={worlds} "
              f"delong_hits={counts[0]} bootstrap_hits={counts[1]}")
        # One binomial SE around nominal 95% coverage, as requested in brief.
        tolerance = math.sqrt(0.95 * 0.05 / worlds)
        for name, count in zip(("DeLong", "cluster bootstrap"), counts):
            with self.subTest(method=name, count=count):
                self.assertLessEqual(abs(count / worlds - 0.95), tolerance)


if __name__ == "__main__":
    unittest.main()
