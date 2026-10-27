"""Self-checks of the moe stats twin (tests/align/twins/moe_twin.py) against hand and closed-form values.

These tests check the twin alone, against numbers derived by hand from the
spec's definitions (the lane brief's stats API), never against the lane's own
module. Each expected value is written as the closed form it came from.

Tolerances. Every float comparison uses ``float_bar(n_ops, magnitude)``: each
floating-point operation (+, -, *, /, and libm log and sqrt, which are within
one ulp) adds at most EPS of relative error to the largest intermediate
magnitude it touches, so n_ops operations accumulate at most n_ops * EPS *
magnitude to first order. Each call states its operation count. Exact
equality is used only for integers, for p values that are ratios of integer
counts computed by one division on both sides, and for identical code on
identical inputs.
"""

from __future__ import annotations

import math
import sys
import unittest
from fractions import Fraction
from math import comb

from joulewise.align.records import RouterLog
from tests.align.twins.moe_twin import (
    default_mc_size, episode_stats, grouped_permutation_test, load_imbalance, mean_reuse_distance,
    reuse_fraction, usage_entropy,
)

EPS = sys.float_info.epsilon  # 2.2e-16: relative spacing of doubles at 1.0 (twice the unit roundoff)


def float_bar(n_ops: int, magnitude: float = 1.0) -> float:
    """First-order rounding bound for n_ops operations on values up to ``magnitude`` (module docstring)."""
    return n_ops * EPS * max(1.0, abs(magnitude))


def make_log(num_experts, top_k, phases, rows, layers=None):
    """RouterLog from rows[t][j] = expert ids at token t, layer j."""
    n_layers = len(rows[0]) if rows else (len(layers) if layers else 1)
    return RouterLog("synthetic", num_experts, top_k, tuple(layers or range(n_layers)), tuple(phases),
                     tuple(tuple(tuple(ids) for ids in row) for row in rows))


# Hand example used by several tests: 4 experts, top-2, two layers, tokens P P D D.
#   layer 0: t0 {0,1}  t1 {0,2}  t2 {0,1}  t3 {2,3}
#   layer 1: t0 {0,1}  t1 {0,1}  t2 {0,1}  t3 {0,1}
HAND = make_log(4, 2, ("prefill", "prefill", "decode", "decode"), [
    [(0, 1), (0, 1)],
    [(0, 2), (0, 1)],
    [(0, 1), (0, 1)],
    [(2, 3), (0, 1)],
])

# Entropy op count for one layer of E experts: per expert one division, one log, one multiply, one
# subtraction (4E), then one log and one division (2); the closed form on the test side costs at
# most 4 more; the mean over L layers adds L additions and one division.
def entropy_ops(num_experts: int, n_layers: int) -> int:
    return 4 * num_experts + 2 + 4 + n_layers + 1


# Load-imbalance op count for one layer: E additions and one division for the mean, E subtractions,
# E squarings, E additions and one division for the variance, one sqrt and one division (4E + 4);
# the closed form on the test side costs at most 4 more; the mean over L layers adds L + 1.
def cv_ops(num_experts: int, n_layers: int) -> int:
    return 4 * num_experts + 4 + 4 + n_layers + 1


class HandExample(unittest.TestCase):
    """All four statistics on the 4-token hand example, each value derived in the comment."""

    def test_usage_entropy(self):
        # Both phases. Layer 0 counts (3,2,2,1)/8: H = (3/8)ln(8/3) + (1/2)ln 4 + (1/8)ln 8
        #   = (5/2)ln 2 - (3/8)ln 3, normalised by ln 4 = 2 ln 2: 5/4 - (3/16)log2(3).
        # Layer 1 counts (4,4,0,0)/8: H = ln 2, normalised 1/2.
        l0 = 5 / 4 - (3 / 16) * math.log2(3)
        bar = float_bar(entropy_ops(4, 2), math.log(4))  # intermediate entropies reach ln 4
        got = usage_entropy(HAND, per_layer=True)
        self.assertEqual(len(got), 2)
        self.assertAlmostEqual(got[0], l0, delta=bar)
        self.assertAlmostEqual(got[1], 0.5, delta=bar)
        self.assertAlmostEqual(usage_entropy(HAND), (l0 + 0.5) / 2, delta=bar)
        # Prefill (t0, t1). Layer 0 counts (2,1,1,0)/4: H = (1/2)ln 2 + (1/2)ln 4 = (3/2)ln 2 -> 3/4.
        # Layer 1 counts (2,2,0,0)/4 -> 1/2. Mean 5/8.
        self.assertAlmostEqual(usage_entropy(HAND, phase="prefill"), 5 / 8, delta=bar)
        # Decode (t2, t3). Layer 0 counts (1,1,1,1)/4 -> 1. Layer 1 (2,2,0,0)/4 -> 1/2. Mean 3/4.
        self.assertAlmostEqual(usage_entropy(HAND, phase="decode"), 3 / 4, delta=bar)

    def test_load_imbalance(self):
        bar = float_bar(cv_ops(4, 2), 1.0)  # CVs here are at most 1
        # Both. Layer 0 counts (3,2,2,1): mean 2, population variance (1+0+0+1)/4 = 1/2,
        #   CV = sqrt(1/2)/2. Layer 1 (4,4,0,0): mean 2, variance 4, CV 1.
        self.assertAlmostEqual(load_imbalance(HAND), (math.sqrt(0.5) / 2 + 1) / 2, delta=bar)
        # Prefill. Layer 0 (2,1,1,0): mean 1, variance 1/2, CV sqrt(1/2). Layer 1 (2,2,0,0): CV 1.
        self.assertAlmostEqual(load_imbalance(HAND, phase="prefill"), (math.sqrt(0.5) + 1) / 2, delta=bar)
        # Decode. Layer 0 (1,1,1,1): CV 0. Layer 1 (2,2,0,0): CV 1. Mean 1/2.
        self.assertAlmostEqual(load_imbalance(HAND, phase="decode"), 0.5, delta=bar)

    def test_reuse_fraction(self):
        bar = float_bar(8)  # at most 6 halves summed (exact) and one division per value
        # Both. Layer 0 pairs: {0,1}&{0,2} = 1/2, {0,2}&{0,1} = 1/2, {0,1}&{2,3} = 0.
        #   Layer 1 pairs: 1, 1, 1. Mean of 6 items = 4/6.
        self.assertAlmostEqual(reuse_fraction(HAND), 4 / 6, delta=bar)
        # Prefill: one pair per layer, 1/2 and 1 -> 3/4.
        self.assertAlmostEqual(reuse_fraction(HAND, phase="prefill"), 3 / 4, delta=bar)
        # Decode: layer 0 {0,1}&{2,3} = 0, layer 1 = 1 -> 1/2.
        self.assertAlmostEqual(reuse_fraction(HAND, phase="decode"), 1 / 2, delta=bar)

    def test_mean_reuse_distance(self):
        bar = float_bar(2, 2.0)  # integer sum (exact) and one division; values at most 2
        # Both. Layer 0: t1 e0 (last t0) 1; t2 e0 (last t1) 1, e1 (last t0) 2; t3 e2 (last t1) 2;
        #   first uses e0@t0, e1@t0, e2@t1, e3@t3 excluded. Layer 1: six reuses of distance 1.
        #   Pooled: (1+1+2+2 + 6)/10 = 1.2. (The mean of layer means would be (1.5+1)/2 = 1.25.)
        self.assertAlmostEqual(mean_reuse_distance(HAND), 12 / 10, delta=bar)
        # Prefill: layer 0 t1 e0 -> 1; layer 1 t1 e0, e1 -> 1, 1. Pooled 1.
        self.assertAlmostEqual(mean_reuse_distance(HAND, phase="prefill"), 1.0, delta=bar)
        # Decode: layer 0 t3 picks {2,3}, both first uses within decode (READINGS R1: the earlier
        #   prefill use of e2 does not count); layer 1 t3 e0, e1 -> 1, 1. Pooled 1.
        self.assertAlmostEqual(mean_reuse_distance(HAND, phase="decode"), 1.0, delta=bar)

    def test_episode_stats_is_the_four_by_three(self):
        stats = episode_stats(HAND)
        names = ("usage_entropy", "load_imbalance", "reuse_fraction", "mean_reuse_distance")
        funcs = (usage_entropy, load_imbalance, reuse_fraction, mean_reuse_distance)
        expected_keys = {f"{n}_{p}" for n in names for p in ("prefill", "decode", "both")}
        self.assertEqual(set(stats), expected_keys)
        for name, func in zip(names, funcs):
            for label, phase in (("prefill", "prefill"), ("decode", "decode"), ("both", None)):
                # identical code on identical input: bit identity is the property
                self.assertEqual(stats[f"{name}_{label}"], func(HAND, phase=phase))


class ClosedForms(unittest.TestCase):
    """Uniform and collapsed routing, where each statistic has a closed form."""

    def round_robin(self, num_experts, top_k, n_tokens, n_layers):
        # token t picks the top_k consecutive experts starting at (t * top_k) mod E; E divisible by k
        rows = [[tuple((t * top_k + i) % num_experts for i in range(top_k)) for _ in range(n_layers)]
                for t in range(n_tokens)]
        return make_log(num_experts, top_k, ["decode"] * n_tokens, rows)

    def test_uniform_round_robin(self):
        # E = 8, k = 2, 40 tokens: each expert chosen 40*2/8 = 10 times per layer.
        log = self.round_robin(8, 2, 40, 3)
        self.assertAlmostEqual(usage_entropy(log), 1.0, delta=float_bar(entropy_ops(8, 3), math.log(8)))
        self.assertAlmostEqual(load_imbalance(log), 0.0, delta=float_bar(cv_ops(8, 3), 10.0))  # counts 10
        # Consecutive tokens use disjoint pairs; a pair returns every E/k = 4 tokens.
        self.assertEqual(reuse_fraction(log), 0.0)  # sum of exact zeros
        self.assertAlmostEqual(mean_reuse_distance(log), 4.0, delta=float_bar(2, 4.0))  # int sum, one division

    def test_top1_round_robin_distance_is_E(self):
        log = self.round_robin(5, 1, 23, 2)
        self.assertAlmostEqual(mean_reuse_distance(log), 5.0, delta=float_bar(2, 5.0))  # int sum, one division

    def test_collapsed_routing(self):
        # Every token picks experts {0, 1} of E = 8: entropy ln 2 / ln 8 = 1/3; counts n,n,0,...,0 give
        # population CV = sqrt((E - k) / k) = sqrt(3) (a sample std would give sqrt(8/7) times that);
        # every pair fully reused; every reuse at distance 1.
        n = 30
        log = make_log(8, 2, ["prefill"] * n, [[(0, 1), (1, 0)] for _ in range(n)])
        self.assertAlmostEqual(usage_entropy(log), 1 / 3, delta=float_bar(entropy_ops(8, 2), math.log(8)))
        self.assertAlmostEqual(load_imbalance(log), math.sqrt(3), delta=float_bar(cv_ops(8, 2), math.sqrt(3)))  # relative error on the CV
        self.assertAlmostEqual(reuse_fraction(log), 1.0, delta=float_bar(2 * (n - 1) + 1))  # sum of ones, one division
        self.assertAlmostEqual(mean_reuse_distance(log), 1.0, delta=float_bar(2))  # int sum, one division


class PhaseReading(unittest.TestCase):
    """READINGS R1: sequential statistics run on the phase's sub-sequence."""

    def test_interleaved_turns(self):
        # One layer, top-1, E = 4. Tokens: t0 P {0}, t1 D {1}, t2 P {2}, t3 D {1}.
        log = make_log(4, 1, ("prefill", "decode", "prefill", "decode"), [[(0,)], [(1,)], [(2,)], [(1,)]])
        # Decode sub-sequence (t1, t3): one pair, fully reused; distance 1 in sub-sequence positions.
        self.assertEqual(reuse_fraction(log, phase="decode"), 1.0)  # 1/1, exact
        self.assertEqual(mean_reuse_distance(log, phase="decode"), 1.0)  # 1/1, exact
        # Whole log: pairs (0,1), (1,2), (2,3) share nothing; expert 1 reused after 2 tokens.
        self.assertEqual(reuse_fraction(log), 0.0)  # sum of exact zeros
        self.assertEqual(mean_reuse_distance(log), 2.0)  # 2/1, exact

    def test_bad_phase_raises(self):
        with self.assertRaises(ValueError):
            usage_entropy(HAND, phase="both")


class UndefinedIsNaN(unittest.TestCase):
    """READINGS R6."""

    def test_empty_phase(self):
        log = make_log(4, 2, ["prefill"] * 3, [[(0, 1)], [(1, 2)], [(2, 3)]])
        for func in (usage_entropy, load_imbalance, reuse_fraction, mean_reuse_distance):
            self.assertTrue(math.isnan(func(log, phase="decode")), func.__name__)
        self.assertTrue(all(math.isnan(x) for x in usage_entropy(log, phase="decode", per_layer=True)))

    def test_single_token_and_no_reuse(self):
        log = make_log(4, 2, ["decode"], [[(0, 1)]])
        self.assertTrue(math.isnan(reuse_fraction(log)))
        self.assertTrue(math.isnan(mean_reuse_distance(log)))
        log2 = make_log(4, 2, ["decode", "decode"], [[(0, 1)], [(2, 3)]])
        self.assertTrue(math.isnan(mean_reuse_distance(log2)))
        self.assertEqual(reuse_fraction(log2), 0.0)  # one pair, exact zero

    def test_single_expert(self):
        log = make_log(1, 1, ["decode"] * 3, [[(0,)]] * 3)
        self.assertTrue(math.isnan(usage_entropy(log)))  # normaliser ln 1 = 0
        self.assertEqual(load_imbalance(log), 0.0)  # one count, zero spread, exact


def exact_p_one_group_1_to_20(sabotage_sum: int) -> float:
    """Two-sided exact p for values 1..20, 10 sabotage, one group, by subset-sum counting.

    An independent route to the exact p: with k1 = k0 = 10, T = (2 S - 210) / 10 where S is the
    sabotage sum, so |T*| >= |T_obs| iff |2 S* - 210| >= |2 S_obs - 210|; ways[k][s] counts the
    k-subsets of {1..20} with sum s.
    """
    ways = [[0] * 211 for _ in range(11)]
    ways[0][0] = 1
    for v in range(1, 21):
        for k in range(10, 0, -1):
            for s in range(210, v - 1, -1):
                ways[k][s] += ways[k - 1][s - v]
    total = sum(ways[10])
    d = abs(2 * sabotage_sum - 210)
    count = sum(ways[10][s] for s in range(211) if abs(2 * s - 210) >= d)
    return count / total


class PermutationTest(unittest.TestCase):

    def test_hand_one_group(self):
        # Values 1,2,3,4, sabotage = {3,4}: T = 3.5 - 1.5 = 2. The 6 arrangements give T in
        # {-2, -1, 0, 0, 1, 2}; two-sided |T| >= 2 for 2 of them: p = 2/6.
        stat, p, n_used = grouped_permutation_test([1.0, 2.0, 3.0, 4.0], [0, 0, 1, 1], ["g"] * 4)
        self.assertEqual(stat, 2.0)  # exact rational 2, converted
        self.assertEqual(p, 2 / 6)  # integer count over integer total, one division on each side
        self.assertEqual(n_used, 6)

    def test_groups_restrict_arrangements(self):
        # Groups a: (1 benign, 2 sabotage), b: (10 benign, 20 sabotage). T = 11 - 5.5 = 5.5.
        # Within-group arrangements: 2 x 2 = 4, with T = 5.5, 4.5, -4.5, -5.5: p = 2/4.
        # (Unrestricted, C(4,2) = 6 arrangements, |T| >= 5.5 for 4 of them: p would be 4/6.)
        stat, p, n_used = grouped_permutation_test([1.0, 2.0, 10.0, 20.0], [0, 1, 0, 1], ["a", "a", "b", "b"])
        self.assertEqual(stat, 5.5)  # exact rational 11/2, converted
        self.assertEqual(p, 2 / 4)
        self.assertEqual(n_used, 4)

    def test_exact_zero_counts_every_arrangement(self):
        # Sabotage {0.1, 0.2, 0.3}, benign {0.3, 0.2, 0.1}: the means are exactly equal, so T = 0 and
        # every one of C(6,3) = 20 arrangements is at least as extreme: p = 1. (Left-to-right float
        # addition gives (0.1+0.2)+0.3 = 0.6000000000000001 but (0.3+0.2)+0.1 = 0.6; the returned
        # statistic must still be exactly 0.)
        stat, p, n_used = grouped_permutation_test([0.1, 0.2, 0.3, 0.3, 0.2, 0.1], [1, 1, 1, 0, 0, 0], ["g"] * 6)
        self.assertEqual(stat, 0.0)
        self.assertEqual(p, 1.0)
        self.assertEqual(n_used, 20)

    def test_mirror_tie_is_counted(self):
        # Values 0.2, 0.1, 0.3, 0.2 (symmetric about 0.2), one sabotage, at 0.3: T = 0.3 - 0.5/3 = 2/15.
        # The 4 arrangements: sabotage at 0.2 -> 0.2 - 0.6/3 = 0; at 0.1 -> 0.1 - 0.7/3 = -2/15 (the
        # mirror); at 0.3 -> 2/15; at the other 0.2 -> 0. Two-sided, |T| >= 2/15 for 2 of 4: p = 2/4.
        # In float with index-order sums, T_obs = 0.13333333333333333 but the mirror's magnitude is
        # 0.1333333333333333, one ulp smaller, so a float comparison without a tie rule counts 1 of 4
        # (p = 1/4); the twin compares exact rationals (READINGS R9).
        stat, p, n_used = grouped_permutation_test([0.2, 0.1, 0.3, 0.2], [0, 0, 1, 0], ["g"] * 4)
        self.assertAlmostEqual(stat, 2 / 15, delta=float_bar(4, 1.0))  # Fraction -> float, plus 2 ops for 2/15
        self.assertEqual(p, 2 / 4)
        self.assertEqual(n_used, 4)

    def test_sign_is_sabotage_minus_benign(self):
        stat, _, _ = grouped_permutation_test([5.0, 6.0, 1.0, 2.0], [1, 1, 0, 0], ["g"] * 4)
        self.assertEqual(stat, 4.0)  # 5.5 - 1.5, exact

    def test_exact_mc_boundary(self):
        # Five groups of 5 with 2 sabotage each: C(5,2)^5 = 10^5 arrangements, the inclusive limit.
        values = [((7 * i) % 11) / 3 for i in range(25)]
        labels = [1, 1, 0, 0, 0] * 5
        groups = [g for g in "abcde" for _ in range(5)]
        stat, p, n_used = grouped_permutation_test(values, labels, groups)
        self.assertEqual(n_used, 100_000)
        count = p * n_used
        # p = count / N by one division, so p * N is within one rounding of an integer: bar = N * EPS
        self.assertAlmostEqual(count, round(count), delta=float_bar(1, n_used))
        self.assertGreaterEqual(round(count), 1)  # the observed arrangement is always counted
        # One more group of 2 with 1 sabotage: 2 * 10^5 arrangements, Monte Carlo at the default size.
        stat2, p2, n_used2 = grouped_permutation_test(values + [0.5, 0.25], labels + [1, 0], groups + ["f", "f"])
        self.assertEqual(n_used2, default_mc_size())

    def test_default_mc_size(self):
        # sqrt(p(1-p)/n) < 0.005 at p = 0.05  <=>  n > 0.0475 / 0.000025 = 1900, so 1901.
        n = default_mc_size()
        self.assertEqual(n, 1901)
        p, se = Fraction(1, 20), Fraction(1, 200)
        self.assertLess(p * (1 - p) / n, se * se)  # exact rationals
        self.assertEqual(p * (1 - p) / (n - 1), se * se)  # n - 1 = 1900 sits exactly on the bar

    def test_monte_carlo_matches_exact_p(self):
        # Values 1..20 in one group, 10 sabotage with sum 131: C(20,10) = 184,756 arrangements, so
        # Monte Carlo. Exact p by subset-sum counting = 9686 / 184756 = 0.0524.
        sabotage = {20, 19, 18, 17, 16, 15, 14, 8, 3, 1}
        self.assertEqual(sum(sabotage), 131)
        values = [float(v) for v in range(1, 21)]
        labels = [1 if v in sabotage else 0 for v in range(1, 21)]
        p_exact = exact_p_one_group_1_to_20(131)
        self.assertEqual(p_exact, 9686 / 184756)  # integer counts, one division each side
        stat, p_mc, n = grouped_permutation_test(values, labels, ["g"] * 20, seed=0)
        self.assertEqual(n, 1901)
        self.assertEqual(stat, (131 - 79) / 10)  # (2*131 - 210)/10 = 5.2; both sides one division of ints
        # (count + 1)/(n + 1) has mean (n p + 1)/(n + 1), bias (1 - p)/(n + 1), and standard deviation
        # sqrt(n p (1 - p))/(n + 1). Bar = bias + 4 standard deviations: a correct implementation
        # exceeds it for under 1e-4 of seeds (two-sided normal tail at 4 sigma is 6.3e-5).
        bias = (1 - p_exact) / (n + 1)
        sd = math.sqrt(n * p_exact * (1 - p_exact)) / (n + 1)
        self.assertLessEqual(abs(p_mc - p_exact), bias + 4 * sd)
        # The estimator's form: p (n + 1) - 1 is an integer count in [0, n]; one division, bar (n+1) EPS.
        c = p_mc * (n + 1) - 1
        self.assertAlmostEqual(c, round(c), delta=float_bar(2, n + 1))
        self.assertTrue(0 <= round(c) <= n)

    def test_monte_carlo_permutes_within_groups_only(self):
        # Group A: 16 values 0.0 with 12 sabotage; group B: 16 values 100.0 with 4 sabotage.
        # C(16,12)^2 = 1820^2 = 3,312,400 arrangements: Monte Carlo. T = (4*100)/16 - (12*100)/16 = -50.
        # Every within-group shuffle leaves T at exactly -50, so count = n and p = (n+1)/(n+1) = 1.
        # (Shuffling across groups would make T near 0 typical and p tiny.)
        values = [0.0] * 16 + [100.0] * 16
        labels = [1] * 12 + [0] * 4 + [1] * 4 + [0] * 12
        groups = ["A"] * 16 + ["B"] * 16
        stat, p, n = grouped_permutation_test(values, labels, groups)
        self.assertEqual(stat, -50.0)  # exact rational -50
        self.assertEqual(p, 1.0)
        self.assertEqual(n, 1901)

    def test_given_n_perm_and_seed(self):
        values = [float(v) for v in range(1, 21)]
        labels = [1] * 10 + [0] * 10
        a = grouped_permutation_test(values, labels, ["g"] * 20, n_perm=500, seed=3)
        b = grouped_permutation_test(values, labels, ["g"] * 20, n_perm=500, seed=3)
        self.assertEqual(a, b)  # identical code, input and seed: bit identity is the property
        self.assertEqual(a[2], 500)
        # Sabotage {1..10} has the extreme sum 55; only it and its mirror {11..20} reach |T| = 10,
        # 2 of 184,756 arrangements, so almost every draw is less extreme: p is near 1/501.
        self.assertEqual(a[0], -10.0)  # 5.5 - 15.5, exact
        # p = (count + 1)/501 with count <= 2: three or more hits in 500 draws at a per-draw rate of
        # 2/184,756 = 1.1e-5 has probability about 3e-8. Both sides are one division of integers.
        self.assertLessEqual(a[1], 3 / 501)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            grouped_permutation_test([1.0, 2.0], [0, 1], ["g"])
        with self.assertRaises(ValueError):
            grouped_permutation_test([1.0, 2.0], [0, 2], ["g", "g"])
        with self.assertRaises(ValueError):
            grouped_permutation_test([1.0, float("nan")], [0, 1], ["g", "g"])

    def test_one_class_empty_is_undefined(self):
        stat, p, n = grouped_permutation_test([1.0, 2.0], [1, 1], ["g", "g"])
        self.assertTrue(math.isnan(stat) and math.isnan(p))
        self.assertEqual(n, 0)


if __name__ == "__main__":
    unittest.main()
