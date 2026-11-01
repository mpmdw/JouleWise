"""Closed-form and hand-computed checks of the frontier twin (tests/align/twins/frontier_twin.py).

These check the twin on its own. Comparing it with joulewise/align/frontier.py
is a separate step.

Tolerance rule used below (every bar carries its derivation where it is used):
- float noise: EPS = 2**-52, the spacing of doubles at 1.0. A chain of k
  correctly rounded operations moves a result by at most about k * EPS
  relative, and a recursive sum over n terms by at most about n * EPS
  relative. Bars built this way are named noise bars.
- Monte Carlo: a probability p estimated from B replicates has standard error
  sqrt(p (1 - p) / B). Bars are 4 standard errors. A two-sided normal tail
  beyond 4 sigma is about 6e-5, so a correct twin fails such a check with
  negligible probability. The seeds are fixed, so every run is deterministic.
"""

from __future__ import annotations

import math
import random
import unittest
from fractions import Fraction

from tests.align.twins.frontier_twin import (
    ConfigRow, average_ranks, catch_rate, cheapest_reaching, default_n_boot, frontier_agreement,
    joule_token_divergence, kendall_tau, ols_fit, pareto_frontier, percentile, spearman_rho,
)

EPS = 2.0 ** -52


def row(config_id, trials, caught, joules, tokens, *, half_width=0.0, model="m", params_b=4.0):
    return ConfigRow(config_id=config_id, model=model, params_b=params_b, trials=trials, caught=caught,
                     joules_mean=joules, joules_half_width=half_width, tokens_mean=tokens)


# A four-config world worked by hand (catch rate, joules, tokens):
#   A 5/10 = 0.5  J 10  T 100
#   B 6/10 = 0.6  J 12  T  90
#   C 5/10 = 0.5  J 11  T  80
#   D 4/10 = 0.4  J 12  T  70
# Joules: C is dominated by A (same catch, 10 < 11); D by A (0.5 > 0.4, 10 < 12);
#   A and B are not dominated -> frontier [A, B].
# Tokens: A is dominated by B (0.6 > 0.5, 90 < 100); B, C, D are not dominated
#   (no config with catch >= 0.6 costs <= 90; none with catch >= 0.5 costs <= 80;
#   none costs <= 70) -> frontier [D, C, B], cheapest first.
HAND_WORLD = [
    row("A", 10, 5, 10.0, 100.0),
    row("B", 10, 6, 12.0, 90.0),
    row("C", 10, 5, 11.0, 80.0),
    row("D", 10, 4, 12.0, 70.0),
]


class FrontierTests(unittest.TestCase):
    def test_equal_fractions_give_equal_catch_rates(self):
        # Correctly rounded division sends the same rational to the same float.
        self.assertEqual(catch_rate(row("x", 3, 1, 1.0, 1.0)), catch_rate(row("y", 6, 2, 1.0, 1.0)))

    def test_hand_world_joule_frontier(self):
        self.assertEqual(pareto_frontier(HAND_WORLD, cost="joules"), ["A", "B"])

    def test_hand_world_token_frontier(self):
        self.assertEqual(pareto_frontier(HAND_WORLD, cost="tokens"), ["D", "C", "B"])

    def test_exact_tie_keeps_both_ordered_by_id(self):
        # X2 (1/3) and X1 (2/6) have equal catch and equal cost: neither dominates.
        rows = [row("X2", 3, 1, 5.0, 5.0), row("X1", 6, 2, 5.0, 5.0), row("Y", 3, 2, 9.0, 9.0)]
        self.assertEqual(pareto_frontier(rows, cost="joules"), ["X1", "X2", "Y"])

    def test_equal_cost_higher_catch_dominates(self):
        rows = [row("lo", 10, 3, 5.0, 5.0), row("hi", 10, 4, 5.0, 5.0)]
        self.assertEqual(pareto_frontier(rows, cost="joules"), ["hi"])

    def test_equal_catch_lower_cost_dominates(self):
        rows = [row("cheap", 10, 3, 5.0, 5.0), row("dear", 10, 3, 6.0, 6.0)]
        self.assertEqual(pareto_frontier(rows, cost="tokens"), ["cheap"])

    def test_frontier_rises_in_cost_and_catch(self):
        rng = random.Random(11)
        rows = [row(f"c{k:02d}", 20, rng.randrange(21), rng.uniform(1, 100), rng.uniform(1, 100))
                for k in range(40)]
        by_id = {r.config_id: r for r in rows}
        for cost in ("joules", "tokens"):
            front = [by_id[i] for i in pareto_frontier(rows, cost=cost)]
            for a, b in zip(front, front[1:]):
                cost_a = a.joules_mean if cost == "joules" else a.tokens_mean
                cost_b = b.joules_mean if cost == "joules" else b.tokens_mean
                self.assertLess(cost_a, cost_b)  # no exact cost ties in uniform draws
                self.assertLess(catch_rate(a), catch_rate(b))

    def test_empty_and_single(self):
        self.assertEqual(pareto_frontier([], cost="joules"), [])
        self.assertEqual(pareto_frontier([row("only", 4, 0, 1.0, 1.0)], cost="tokens"), ["only"])

    def test_bad_inputs_raise(self):
        with self.assertRaises(ValueError):
            pareto_frontier(HAND_WORLD, cost="watts")
        with self.assertRaises(ValueError):
            pareto_frontier([row("a", 4, 1, 1.0, 1.0), row("a", 4, 2, 2.0, 2.0)], cost="joules")
        with self.assertRaises(ValueError):
            pareto_frontier([row("a", 4, 5, 1.0, 1.0)], cost="joules")
        with self.assertRaises(ValueError):
            pareto_frontier([row("a", 0, 0, 1.0, 1.0)], cost="joules")


class KendallTests(unittest.TestCase):
    def test_no_ties_hand(self):
        # [1,2,3,4] vs [1,3,2,4]: of 6 pairs only (2,3) is discordant -> (5 - 1) / 6 = 2/3.
        tau_a, tau_b = kendall_tau([1, 2, 3, 4], [1, 3, 2, 4])
        self.assertEqual(tau_a, 2 / 3)  # (C - D) / n0 = 4 / 6: one correctly rounded division
        self.assertEqual(tau_b, 2 / 3)  # 4 / sqrt(36) and sqrt(36) = 6 exactly

    def test_reversed_is_minus_one(self):
        self.assertEqual(kendall_tau([1, 2, 3], [3, 2, 1]), (-1.0, -1.0))

    def test_ties_hand(self):
        # [1,1,2] vs [1,2,3]: pair (1,2) tied in x, pairs (1,3) and (2,3) concordant.
        # n0 = 3, n1 = 1, n2 = 0: tau_b = 2 / sqrt(2 * 3) = 0.8164965809277261, tau_a = 2 / 3.
        tau_a, tau_b = kendall_tau([1, 1, 2], [1, 2, 3])
        self.assertEqual(tau_a, 2 / 3)
        # Bar: one product, one sqrt, one division, each within half an ulp: 4 EPS relative.
        self.assertAlmostEqual(tau_b, 0.8164965809277261, delta=4 * EPS)

    def test_hand_world_tau(self):
        # J = [10, 12, 11, 12], T = [100, 90, 80, 70]. Pairs: AB, AC, AD, CD discordant; BC concordant;
        # BD tied in J. C = 1, D = 4, n0 = 6, n1 = 1, n2 = 0.
        # tau_b = -3 / sqrt(5 * 6) = -0.5477225575051661; tau_a = -3 / 6 = -0.5.
        result = frontier_agreement(HAND_WORLD)
        self.assertEqual(result["kendall_tau_a"], -0.5)
        # Bar: one product, one sqrt, one division: 4 EPS relative on a value of size about 0.55.
        self.assertAlmostEqual(result["kendall_tau"], -0.5477225575051661, delta=4 * EPS)

    def test_undefined_is_nan(self):
        tau_a, tau_b = kendall_tau([1.0], [2.0])
        self.assertTrue(math.isnan(tau_a) and math.isnan(tau_b))
        tau_a, tau_b = kendall_tau([1, 1, 1], [1, 2, 3])
        self.assertEqual(tau_a, 0.0)
        self.assertTrue(math.isnan(tau_b))


class AgreementTests(unittest.TestCase):
    def test_hand_world(self):
        result = frontier_agreement(HAND_WORLD)
        self.assertEqual(result["joule_frontier"], {"A", "B"})
        self.assertEqual(result["token_frontier"], {"B", "C", "D"})
        self.assertEqual(result["symmetric_difference"], {"A", "C", "D"})
        self.assertEqual(result["joule_frontier_order"], ["A", "B"])
        self.assertEqual(result["token_frontier_order"], ["D", "C", "B"])
        self.assertFalse(result["identical"])
        self.assertFalse(result["kill_condition_met"])

    def test_proportional_costs_give_identical_frontiers(self):
        rows = [row(r.config_id, r.trials, r.caught, 0.25 * r.tokens_mean, r.tokens_mean) for r in HAND_WORLD]
        result = frontier_agreement(rows)
        self.assertTrue(result["identical"])
        self.assertTrue(result["kill_condition_met"])
        self.assertEqual(result["symmetric_difference"], frozenset())
        self.assertEqual(result["kendall_tau"], 1.0)  # C = n0, D = 0, no ties: n0 / sqrt(n0 * n0)


# Production-shaped world: Qwen3 4B, 8B, 14B and a model with a different attention
# design, five conditions each. Catch counts depend on the condition only (50
# hint-using trials). Tokens = base(condition) x verbosity(model); joules = tokens x
# joules-per-token(model). Smaller models write more tokens; the hybrid-attention
# model spends fewer joules per token.
CONDITIONS = {  # condition: (caught of 50, base decode tokens)
    "thinking_on": (40, 4000.0),
    "budget_50": (35, 2000.0),
    "budget_25": (30, 1000.0),
    "concise": (25, 600.0),
    "thinking_off": (20, 300.0),
}
MODELS = {  # model: (params_b, verbosity, joules per token)
    "qwen3-4b": (4.0, 1.5, 0.10),
    "qwen3-8b": (8.0, 1.2, 0.18),
    "qwen3-14b": (14.0, 1.0, 0.30),
    "hybrid-attn-7b": (7.0, 1.3, 0.12),
}


def production_world(*, same_joules_per_token=False):
    rows = []
    for model, (params_b, verbosity, j_per_tok) in MODELS.items():
        for condition, (caught, base_tokens) in CONDITIONS.items():
            tokens = base_tokens * verbosity
            joules = tokens * (0.2 if same_joules_per_token else j_per_tok)
            rows.append(ConfigRow(f"{model}/{condition}", model, params_b, 50, caught,
                                  joules, 0.01 * joules, tokens))
    return rows


class ProductionShapedTests(unittest.TestCase):
    def test_frontiers_differ_by_construction(self):
        # At every condition (one catch level) the fewest tokens belong to qwen3-14b
        # (verbosity 1.0), and the fewest joules to qwen3-4b (1.5 x 0.10 = 0.15 J per
        # base token, against 0.216, 0.30 and 0.156). Cost rises with catch inside each
        # model, so each frontier is that model's five configs.
        result = frontier_agreement(production_world())
        four_b = {f"qwen3-4b/{c}" for c in CONDITIONS}
        fourteen_b = {f"qwen3-14b/{c}" for c in CONDITIONS}
        self.assertEqual(result["joule_frontier"], four_b)
        self.assertEqual(result["token_frontier"], fourteen_b)
        self.assertEqual(result["symmetric_difference"], four_b | fourteen_b)
        self.assertFalse(result["kill_condition_met"])
        self.assertLess(result["kendall_tau"], 1.0)

    def test_same_joules_per_token_gives_kill(self):
        # Joules = 0.2 x tokens for every model, so the two cost orders coincide.
        result = frontier_agreement(production_world(same_joules_per_token=True))
        self.assertTrue(result["kill_condition_met"])
        self.assertEqual(result["kendall_tau"], 1.0)  # no ties among the 20 token values

    def test_cheapest_reaching_on_production_world(self):
        # Target 0.7 in joules. qwen3-4b/budget_50 (catch 0.7, 300 J) reaches whenever
        # Bin(50, 0.7) >= 35 (probability 0.569). The nearest rival at that catch level,
        # hybrid-attn-7b/budget_50, costs 312 J, four half-widths (3 J each) dearer, and
        # cheaper configs reach only by upward catch noise, so qwen3-4b/budget_50 is the
        # most probable winner.
        probs = cheapest_reaching(production_world(), 0.7, cost="joules", n_boot=4000, seed=3)
        self.assertEqual(max(probs, key=probs.get), "qwen3-4b/budget_50")
        # Bar for the sum: 20 float additions of values in [0, 1]: 20 EPS.
        self.assertLessEqual(sum(probs.values()), 1.0 + 20 * EPS)


class CheapestReachingTests(unittest.TestCase):
    def test_default_n_boot(self):
        n = default_n_boot()
        self.assertEqual(n, 10001)
        # sqrt(1 / (4 n)) < 0.005  <=>  1 / (4 n) < 1/40000, checked in exact fractions.
        self.assertLess(Fraction(1, 4 * n), Fraction(1, 40000))
        self.assertFalse(Fraction(1, 4 * (n - 1)) < Fraction(1, 40000))

    def test_deterministic_world(self):
        # caught = trials or 0 makes the binomial draws fixed; half-width 0 makes costs fixed.
        rows = [row("never", 10, 0, 1.0, 1.0), row("cheap", 10, 10, 5.0, 50.0), row("dear", 10, 10, 9.0, 90.0)]
        self.assertEqual(cheapest_reaching(rows, 0.5, cost="joules", n_boot=50),
                         {"never": 0.0, "cheap": 1.0, "dear": 0.0})

    def test_reaching_is_at_least(self):
        rows = [row("full", 10, 10, 5.0, 5.0)]
        self.assertEqual(cheapest_reaching(rows, 1.0, cost="joules", n_boot=20), {"full": 1.0})
        rows = [row("tenth", 10, 1, 5.0, 5.0)]
        # Bin(10, 0.1) >= 1 has probability 1 - 0.9**10 = 0.6513; the float target 0.1
        # must count 1/10 as reaching (READINGS R2), so the estimate is near 0.65, not 0.
        p = cheapest_reaching(rows, 0.1, cost="joules", n_boot=4000, seed=5)["tenth"]
        expected = 1 - 0.9 ** 10
        self.assertAlmostEqual(p, expected, delta=4 * math.sqrt(expected * (1 - expected) / 4000))

    def test_clearly_cheapest(self):
        # Costs 10 +- 0.1 and 20 +- 0.1 (sd = half-width): the difference has mean 10 and
        # sd sqrt(0.02) = 0.141, so a reversal needs a 70-sigma draw. Every one of the
        # n_boot replicates goes to A; the estimate is exactly 1. Interval: with B of B
        # wins, the one-sided 95% lower bound on the true probability is 1 - 3/B
        # (rule of three), 0.9997 at the default B = 10001.
        rows = [row("A", 50, 50, 10.0, 1.0, half_width=0.1), row("B", 50, 50, 20.0, 1.0, half_width=0.1)]
        probs = cheapest_reaching(rows, 0.9, cost="joules")
        self.assertEqual(probs, {"A": 1.0, "B": 0.0})

    def test_tied_pair_near_half(self):
        rows = [row("A", 50, 50, 10.0, 1.0, half_width=1.0), row("B", 50, 50, 10.0, 1.0, half_width=1.0)]
        n_boot = default_n_boot()
        probs = cheapest_reaching(rows, 0.9, cost="joules", seed=1)
        bar = 4 * math.sqrt(0.25 / n_boot)  # 4 standard errors at p = 1/2
        self.assertAlmostEqual(probs["A"], 0.5, delta=bar)
        self.assertAlmostEqual(probs["B"], 0.5, delta=bar)
        # Every replicate has a winner, so the two credits sum to n_boot / n_boot.
        # Bar: two divisions and one addition, each within half an ulp: 2 EPS.
        self.assertAlmostEqual(probs["A"] + probs["B"], 1.0, delta=2 * EPS)

    def test_normal_difference_closed_form(self):
        # A ~ N(10, 1), B ~ N(11, 1): P(A < B) = Phi(1 / sqrt(2)) = (1 + erf(1/2)) / 2 = 0.76025.
        rows = [row("A", 50, 50, 10.0, 1.0, half_width=1.0), row("B", 50, 50, 11.0, 1.0, half_width=1.0)]
        n_boot = 20000
        p_true = 0.5 * (1 + math.erf(0.5))
        probs = cheapest_reaching(rows, 0.9, cost="joules", n_boot=n_boot, seed=2)
        self.assertAlmostEqual(probs["A"], p_true, delta=4 * math.sqrt(p_true * (1 - p_true) / n_boot))

    def test_binomial_reach_closed_form(self):
        # A is cheap but reaches target 1.0 only when Bin(2, 1/2) = 2: probability 1/4.
        # B is dear and always reaches. So P(A) = 0.25 and P(B) = 0.75.
        rows = [row("A", 2, 1, 10.0, 1.0), row("B", 2, 2, 20.0, 1.0)]
        n_boot = 20000
        probs = cheapest_reaching(rows, 1.0, cost="joules", n_boot=n_boot, seed=4)
        bar = 4 * math.sqrt(0.25 * 0.75 / n_boot)
        self.assertAlmostEqual(probs["A"], 0.25, delta=bar)
        self.assertAlmostEqual(probs["B"], 0.75, delta=bar)

    def test_probabilities_sum_to_reach_probability(self):
        # Only A exists; it reaches with probability 1/4, so the values sum to about 1/4, not 1.
        n_boot = 20000
        probs = cheapest_reaching([row("A", 2, 1, 10.0, 1.0)], 1.0, cost="joules", n_boot=n_boot, seed=6)
        self.assertAlmostEqual(probs["A"], 0.25, delta=4 * math.sqrt(0.25 * 0.75 / n_boot))

    def test_token_cost_is_fixed_and_exact_ties_split(self):
        # Token costs are not resampled (READINGS R7): equal token costs tie in every
        # replicate and split the credit exactly; a lower token cost always wins
        # however large the joule half-width.
        tied = [row("A", 10, 10, 1.0, 100.0, half_width=50.0), row("B", 10, 10, 1.0, 100.0, half_width=50.0)]
        self.assertEqual(cheapest_reaching(tied, 0.5, cost="tokens", n_boot=101), {"A": 0.5, "B": 0.5})
        ordered = [row("A", 10, 10, 99.0, 100.0, half_width=50.0), row("B", 10, 10, 1.0, 101.0, half_width=50.0)]
        self.assertEqual(cheapest_reaching(ordered, 0.5, cost="tokens", n_boot=101), {"A": 1.0, "B": 0.0})

    def test_no_reacher(self):
        self.assertEqual(cheapest_reaching(HAND_WORLD, 1.01, cost="joules", n_boot=30),
                         {"A": 0.0, "B": 0.0, "C": 0.0, "D": 0.0})

    def test_seed_reproducible(self):
        rows = [row("A", 20, 15, 10.0, 1.0, half_width=1.0), row("B", 20, 16, 10.5, 1.0, half_width=1.0)]
        # Identical code on identical inputs: bit-identity is the property.
        self.assertEqual(cheapest_reaching(rows, 0.75, cost="joules", n_boot=500, seed=9),
                         cheapest_reaching(rows, 0.75, cost="joules", n_boot=500, seed=9))


class DivergenceHelperTests(unittest.TestCase):
    def test_ols_hand(self):
        # x = 0..3, y = [0, 1, 1, 2]: Sxx = 5, Sxy = 3, b = 0.6, a = 1 - 0.6 * 1.5 = 0.1,
        # residuals [-0.1, 0.3, -0.3, 0.1], SSR = 0.2, sd = sqrt(0.2 / 2) = 0.31622776601683794.
        a, b, sd = ols_fit([0.0, 1.0, 2.0, 3.0], [0.0, 1.0, 1.0, 2.0])
        # Bar: sums over n = 4 terms (4 EPS each) plus about 8 further operations,
        # on quantities of size at most 2: (2 * 4 + 8) * EPS * 2.
        bar = (2 * 4 + 8) * EPS * 2
        self.assertAlmostEqual(a, 0.1, delta=bar)
        self.assertAlmostEqual(b, 0.6, delta=bar)
        self.assertAlmostEqual(sd, 0.31622776601683794, delta=bar)

    def test_spearman_hand(self):
        # No ties: d = [-1, 1, -1, 1, 0], sum d^2 = 4, rho = 1 - 6 * 4 / (5 * 24) = 0.8.
        # Bar: rank sums over 5 terms and about 6 further operations: (2 * 5 + 6) EPS.
        self.assertAlmostEqual(spearman_rho([1, 2, 3, 4, 5], [2, 1, 4, 3, 5]), 0.8, delta=16 * EPS)
        # Ties: ranks x = [1, 2.5, 2.5, 4], y = [1, 2, 3, 4]; Sxy = 4.5, Sxx = 4.5, Syy = 5;
        # rho = 4.5 / sqrt(22.5) = 0.9486832980505138. Same bar with n = 4: (2 * 4 + 6) EPS.
        self.assertAlmostEqual(spearman_rho([1, 2, 2, 3], [1, 2, 3, 4]), 0.9486832980505138, delta=14 * EPS)

    def test_average_ranks_hand(self):
        self.assertEqual(average_ranks([10, 20, 20, 30]), [1.0, 2.5, 2.5, 4.0])
        self.assertEqual(average_ranks([3, 1, 2]), [3.0, 1.0, 2.0])
        self.assertEqual(average_ranks([7, 7, 7]), [2.0, 2.0, 2.0])

    def test_percentile_hand(self):
        values = [float(k) for k in range(101)]  # position q * 100
        self.assertEqual(percentile(values, 0.0), 0.0)
        self.assertEqual(percentile(values, 1.0), 100.0)
        # q = 0.025 -> position 0.025 * 100 = 2.5 -> halfway between 2 and 3 = 2.5.
        # Bar: the product q * 100 and the interpolation step each round once, on values
        # up to 100: 2 EPS * 100.
        self.assertAlmostEqual(percentile(values, 0.025), 2.5, delta=2 * EPS * 100)
        self.assertEqual(percentile([4.0, 1.0, 3.0, 2.0], 0.5), 2.5)


def linear_pairs(seed, *, n, half_width, second_source_sd=0.0):
    """joules = 3 + 0.3 tokens + N(0, half_width) [+ N(0, second_source_sd) independent of tokens]."""
    rng = random.Random(seed)
    pairs = []
    for k in range(n):
        tokens = 200.0 + 60.0 * k
        joules = 3.0 + 0.3 * tokens + rng.gauss(0.0, half_width)
        if second_source_sd:
            joules += rng.gauss(0.0, second_source_sd)
        pairs.append((tokens, joules, half_width))
    return pairs


class DivergenceTests(unittest.TestCase):
    def test_exact_linear_world(self):
        pairs = [(t, 2.0 + 3.0 * t, 0.5) for t in (100.0, 200.0, 300.0, 450.0, 700.0, 1000.0)]
        result = joule_token_divergence(pairs, n_boot=300)
        # Bar: residuals of an exact fit are float noise; n = 6 sums plus about 8 more
        # operations on joules up to 3002: (2 * 6 + 8) * EPS * 3002.
        noise = (2 * 6 + 8) * EPS * 3002
        self.assertLessEqual(result["residual_sd"], noise)
        self.assertLessEqual(result["residual_sd_interval"][1], noise)
        self.assertAlmostEqual(result["slope"], 3.0, delta=noise)
        # Ranks of x and y coincide, so Sxy, Sxx and Syy are the same float: rho = 1 exactly.
        self.assertEqual(result["spearman_rho"], 1.0)
        self.assertEqual(result["spearman_interval"], (1.0, 1.0))
        self.assertEqual(result["median_half_width"], 0.5)
        self.assertFalse(result["diverges"])

    def test_noise_at_half_width_does_not_diverge_beyond_nominal_rate(self):
        # Joules are linear in tokens plus noise with sd equal to the half-width, so the
        # residual sd equals the median half-width. The gate's nominal false-alarm rate
        # is the one-sided tail (1 - level) / 2 = 0.025. Over S = 100 seeds the alarm
        # count has mean 2.5 and sd sqrt(100 * 0.025 * 0.975) = 1.56; the bar is the
        # mean plus 3 sd, 7.2, so at most 7 alarms.
        alarms = 0
        for seed in range(100):
            result = joule_token_divergence(linear_pairs(1000 + seed, n=30, half_width=5.0),
                                            n_boot=1000, seed=seed)
            alarms += bool(result["diverges"])
        self.assertLessEqual(alarms, 7)

    def test_second_energy_source_diverges(self):
        # A second source with sd 5 x half-width, independent of tokens: the residual sd
        # is about sqrt(1 + 25) = 5.1 half-widths. With n = 40 its relative standard
        # error is about 1 / sqrt(2 (n - 2)) = 0.115, so the 95% lower end sits near
        # 5.1 (1 - 2 x 0.115) = 3.9 half-widths, far above 1 half-width.
        for seed in range(5):
            result = joule_token_divergence(linear_pairs(500 + seed, n=40, half_width=5.0, second_source_sd=25.0),
                                            n_boot=2000, seed=seed)
            self.assertTrue(result["diverges"], msg=f"seed {seed}: {result['residual_sd_interval']}")
            self.assertGreater(result["spearman_rho"], 0.9)

    def test_median_half_width_even_and_odd(self):
        base = [(100.0, 30.0), (200.0, 61.0), (300.0, 89.0), (400.0, 121.0)]
        even = joule_token_divergence([(t, j, h) for (t, j), h in zip(base, (1.0, 2.0, 3.0, 4.0))], n_boot=50)
        self.assertEqual(even["median_half_width"], 2.5)
        odd = joule_token_divergence([(t, j, h) for (t, j), h in zip(base[:3], (1.0, 3.0, 2.0))], n_boot=50)
        self.assertEqual(odd["median_half_width"], 2.0)

    def test_interval_brackets_and_seed_reproducible(self):
        pairs = linear_pairs(7, n=25, half_width=4.0, second_source_sd=6.0)
        first = joule_token_divergence(pairs, n_boot=800, seed=3)
        # Identical code on identical inputs: bit-identity is the property.
        self.assertEqual(first, joule_token_divergence(pairs, n_boot=800, seed=3))
        low, high = first["residual_sd_interval"]
        self.assertLessEqual(low, high)
        low, high = first["spearman_interval"]
        self.assertLessEqual(low, high)

    def test_bad_inputs_raise(self):
        with self.assertRaises(ValueError):
            joule_token_divergence([(1.0, 1.0, 1.0), (2.0, 2.0, 1.0)])
        with self.assertRaises(ValueError):
            joule_token_divergence([(1.0, 1.0, 1.0), (1.0, 2.0, 1.0), (1.0, 3.0, 1.0)])
        with self.assertRaises(ValueError):
            joule_token_divergence([(1.0, 1.0, 1.0), (2.0, 1.0, 1.0), (3.0, 1.0, 1.0)])
        with self.assertRaises(ValueError):
            joule_token_divergence(linear_pairs(1, n=5, half_width=1.0), level=1.0)


if __name__ == "__main__":
    unittest.main()
