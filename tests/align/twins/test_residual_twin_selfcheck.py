"""Self-checks of the lane A7 twin (tests/align/twins/residual_twin.py).

Closed forms and hand-computable cases first, then production-shaped synthetic worlds
run end to end through the twin's own functions. The twin is checked against exact
rational arithmetic (``fractions``) where float error is the only thing in question.

Bar policy (PIPELINE.md "Rules every lane follows", and the brief's rule 3): an agreement
bar between two computations sits between 1e6 times the float noise and 1% of the
smallest printed uncertainty. Every float-agreement bar below is set at that floor,
1e6 * (float noise of the computation), with the float noise named beside it: machine
epsilon for correctly rounded sums and a few operations, epsilon times the condition
number of the scaled normal matrix for a linear solve (Higham 2002, Thm 7.2 and 10.4:
a backward-stable solve's forward error scales with the condition number). Where a
printed standard error exists, the test also checks the bar is below 1% of it, so the
band is not empty. Statistical bars are stated in standard errors with the tail
probability they correspond to. Exact equality is used only where bit identity is the
property (integers, or identical code on identical inputs).
"""

from __future__ import annotations

import math
import random
import sys
import unittest
from dataclasses import replace
from fractions import Fraction
from statistics import NormalDist

from tests.align.twins import residual_twin as T
from tests.align.twins.residual_twin import (
    EnergyModel, TurnRow, design_row, fit_energy_model, grouped_benign_threshold,
    min_detectable_hidden_decode_tokens, predict_episode, residual_score,
)

EPS = sys.float_info.epsilon
BAND_FLOOR = 1e6  # the rule's lower end: bar = 1e6 x the computation's float noise

# Production-shaped turn-energy model for an 8B model on an M3 Max-class machine.
# Chosen as dyadic rationals near the physical values so that a noise-free world's energies
# are exact in float64 (every product x_j * beta_j has <= 47 significant bits):
#   intercept 2 J per model call (fixed per-call cost),
#   prefill 5/64 = 0.078 J/token (about 40 W at about 500 tokens/s),
#   decode 7/8 = 0.875 J/token (about 30 W at about 34 tokens/s),
#   context x decode 2^-15 = 3.05e-5 J per decode token per context token (+0.6 J/token at 20k),
#   context x prefill 2^-18 = 3.8e-6 J per prefill token per context token.
BETA = (2.0, 5 / 64, 7 / 8, 2.0 ** -15, 2.0 ** -18)


def make_episode_rows(rng: random.Random, episode_id: str, group: str, *, turns: int, sigma_j: float,
                      half_width_range_j: tuple[float, float], noise_free: bool = False):
    """One multi-turn agent episode: context grows by each turn's prefill (tool results, user
    text) and decode. Returns (rows, true total J without measurement error)."""
    context = rng.randint(1_500, 3_000)  # system prompt + task statement
    rows, true_total = [], 0.0
    for _ in range(turns):
        prefill = rng.randint(100, 1_500)   # tool result or user message
        decode = rng.randint(30, 800)       # reasoning + tool call
        half_width = rng.uniform(*half_width_range_j)
        x = (1, prefill, decode, context * decode, context * prefill)
        mean = math.fsum(b * v for b, v in zip(BETA, x))
        true = mean if noise_free else mean + rng.gauss(0.0, sigma_j)
        measured = true if noise_free else true + rng.gauss(0.0, half_width)
        rows.append(TurnRow(episode_id, group, context, prefill, decode, 8.0, measured, half_width))
        true_total += true
        context += prefill + decode
    return rows, true_total


def make_world(seed: int, *, n_episodes: int, n_groups: int, turns: int = 20, sigma_j: float = 3.0,
               half_width_range_j: tuple[float, float] = (0.5, 2.0), episode_half_width_j: float = 1.0,
               hidden_tokens=None):
    """benign-style mapping {episode_id: (rows, measured total J, half-width J)}.

    ``hidden_tokens(rows) -> H`` adds H hidden decode tokens per episode, spread evenly over
    its turns, at the true per-token cost (beta_decode + beta_cxd * context of that turn);
    the logged rows are unchanged. Turn half-widths 0.5-2 J bracket the about 1 J attribution
    limit; the episode total carries a 1 J standard uncertainty.
    """
    rng = random.Random(seed)
    world = {}
    for e in range(n_episodes):
        eid = f"ep{e:04d}"
        rows, true_total = make_episode_rows(rng, eid, f"pair{e % n_groups}", turns=turns,
                                             sigma_j=sigma_j, half_width_range_j=half_width_range_j)
        if hidden_tokens is not None:
            h = hidden_tokens(rows)
            true_total += math.fsum((h / len(rows)) * (BETA[2] + BETA[3] * r.context_tokens) for r in rows)
        measured = true_total + rng.gauss(0.0, episode_half_width_j)
        world[eid] = (rows, measured, episode_half_width_j)
    return world


def all_rows(world):
    return [r for eid in sorted(world) for r in world[eid][0]]


def exact_wls(X, y, a):
    """Exact rational WLS solution of the float inputs: (coef, (X'AX)^-1, RSS_weighted)."""
    p = len(X[0])
    Xf = [[Fraction(v) for v in row] for row in X]
    yf = [Fraction(v) for v in y]
    af = [Fraction(v) for v in a]
    M = [[sum(af[i] * Xf[i][j] * Xf[i][k] for i in range(len(X))) for k in range(p)] for j in range(p)]
    v = [sum(af[i] * Xf[i][j] * yf[i] for i in range(len(X))) for j in range(p)]
    # Gauss-Jordan on [M | v | I]
    aug = [M[j][:] + [v[j]] + [Fraction(int(j == k)) for k in range(p)] for j in range(p)]
    for c in range(p):
        pivot = next(r for r in range(c, p) if aug[r][c] != 0)
        aug[c], aug[pivot] = aug[pivot], aug[c]
        inv = 1 / aug[c][c]
        aug[c] = [x * inv for x in aug[c]]
        for r in range(p):
            if r != c and aug[r][c] != 0:
                f = aug[r][c]
                aug[r] = [x - f * y_ for x, y_ in zip(aug[r], aug[c])]
    coef = [aug[j][p] for j in range(p)]
    M_inv = [[aug[j][p + 1 + k] for k in range(p)] for j in range(p)]
    resid = [yf[i] - sum(Xf[i][j] * coef[j] for j in range(p)) for i in range(len(X))]
    rss = sum(af[i] * resid[i] ** 2 for i in range(len(X)))
    return coef, M_inv, rss


def cond1(M):
    """1-norm condition number of a small symmetric positive definite matrix (via the twin's Cholesky)."""
    p = len(M)
    L = T._cholesky(M)
    M_inv = [T._cholesky_solve(L, [1.0 if i == j else 0.0 for i in range(p)]) for j in range(p)]
    norm1 = lambda A: max(math.fsum(abs(A[i][j]) for i in range(p)) for j in range(p))
    return norm1(M) * norm1(M_inv)


# ---------------------------------------------------------------- design_row

class DesignRowTest(unittest.TestCase):
    def test_hand_row(self):
        r = TurnRow("e", "g", context_tokens=2_000, prefill_tokens=300, decode_tokens=120,
                    duration_s=4.5, energy_j=0.0, energy_half_width_j=1.0)
        # Exact: integer products below 2**53 convert to float exactly.
        self.assertEqual(design_row(r), [1.0, 300.0, 120.0, 240_000.0, 600_000.0])

    def test_duration_is_not_a_regressor(self):
        r = TurnRow("e", "g", 9_000, 700, 400, 3.0, 0.0, 1.0)
        # Exact: identical code on inputs that differ only in a field the row must not read.
        self.assertEqual(design_row(r), design_row(replace(r, duration_s=300.0)))

    def test_large_products_exact(self):
        r = TurnRow("e", "g", 120_000, 4_000, 3_000, 1.0, 0.0, 1.0)
        # Exact: 3.6e8 and 4.8e8 are integers below 2**53.
        self.assertEqual(design_row(r)[3:], [360_000_000.0, 480_000_000.0])


# ---------------------------------------------------------------- the weighted solve

class WeightedSolveTest(unittest.TestCase):
    def test_solve_matches_exact_rational(self):
        world = make_world(11, n_episodes=3, n_groups=1, half_width_range_j=(0.5, 6.0))
        rows = all_rows(world)
        X = [design_row(r) for r in rows]
        y = [r.energy_j for r in rows]
        a = [1.0 / (4.0 + r.energy_half_width_j ** 2) for r in rows]  # weights at s = 4 J^2
        fit = T.weighted_fit(X, y, a)
        coef_x, M_inv_x, _ = exact_wls(X, y, a)
        d = fit["scale"]
        kappa = cond1(fit["scaled_normal"])
        # Compare in scaled coordinates b_j = c_j * d_j, where the solve happens.
        b_x = [coef_x[j] * Fraction(d[j]) for j in range(T.P)]
        b_f = [Fraction(v) for v in fit["scaled_coef"]]
        norm_b = max(abs(v) for v in b_x)
        err = max(abs(b_f[j] - b_x[j]) for j in range(T.P)) / norm_b
        # Float noise of a backward-stable solve: kappa * eps (Higham Thm 7.2); bar at the band floor.
        bar = BAND_FLOOR * kappa * EPS
        self.assertLessEqual(float(err), bar, f"kappa={kappa:.3g} err={float(err):.3g} bar={bar:.3g}")
        # Band not empty: absolute bar in scaled coordinates below 1% of the smallest standard
        # error there (sqrt of the scaled inverse's diagonal).
        se_scaled = [math.sqrt(T._cholesky_solve(T._cholesky(fit["scaled_normal"]),
                                                 [1.0 if i == j else 0.0 for i in range(T.P)])[j])
                     for j in range(T.P)]
        self.assertLessEqual(bar * float(norm_b), 0.01 * min(se_scaled))
        # Covariance, scaled the same way: (M_z^-1)_jk = cov_jk d_j d_k.
        cov_err = max(abs(Fraction(fit["cov"][j][k]) * Fraction(d[j]) * Fraction(d[k])
                          - M_inv_x[j][k] * Fraction(d[j]) * Fraction(d[k]))
                      for j in range(T.P) for k in range(T.P))
        cov_norm = max(abs(M_inv_x[j][k] * Fraction(d[j]) * Fraction(d[k]))
                       for j in range(T.P) for k in range(T.P))
        # The inverse is p solves of the same system: same float noise kappa * eps per column.
        self.assertLessEqual(float(cov_err / cov_norm), bar)

    def test_scaled_normal_has_unit_diagonal(self):
        world = make_world(12, n_episodes=4, n_groups=1)
        rows = all_rows(world)
        fit = T.weighted_fit([design_row(r) for r in rows], [r.energy_j for r in rows], [1.0] * len(rows))
        for j in range(T.P):
            # Each diagonal entry is sum a_i x_ij^2 / d_j^2 with d_j^2 that same sum rounded and
            # square-rooted: a few roundings, float noise a few eps; bar at the band floor.
            self.assertAlmostEqual(fit["scaled_normal"][j][j], 1.0, delta=BAND_FLOOR * EPS)


# ---------------------------------------------------------------- fit_energy_model

class FitClosedFormTest(unittest.TestCase):
    def test_noise_free_world_recovers_coefficients_and_zero_sigma2(self):
        rng = random.Random(21)
        rows = []
        for e in range(10):
            rows += make_episode_rows(rng, f"ep{e}", "pair0", turns=20, sigma_j=0.0,
                                      half_width_range_j=(0.5, 2.0), noise_free=True)[0]
        # The world's energies are exact: x . BETA in rationals equals the float energy.
        for r in rows[:50]:
            self.assertEqual(Fraction(r.energy_j),
                             sum(Fraction(b) * Fraction(v) for b, v in zip(BETA, design_row(r))))
        model = fit_energy_model(rows)
        # Exact zero: the residuals are float noise (~1e-12 J) against 0.5-2 J half-widths, so the
        # moment numerator is negative and the truncation at zero (reading R2) returns 0.0.
        self.assertEqual(model.sigma2_per_turn, 0.0)
        a = [1.0 / r.energy_half_width_j ** 2 for r in rows]
        fit = T.weighted_fit([design_row(r) for r in rows], [r.energy_j for r in rows], a)
        kappa = cond1(fit["scaled_normal"])
        d = fit["scale"]
        b_true = [BETA[j] * d[j] for j in range(T.P)]
        err = max(abs(model.coef[j] * d[j] - b_true[j]) for j in range(T.P)) / max(map(abs, b_true))
        # Float noise of the solve kappa * eps, plus a few eps for the unscaling; band floor.
        bar = BAND_FLOOR * (kappa + 4) * EPS
        self.assertLessEqual(err, bar, f"kappa={kappa:.3g} err={err:.3g}")
        self.assertEqual(model.n_turns, 200)
        self.assertEqual(model.names, T.NAMES)

    def test_equal_half_widths_one_step_closed_form(self):
        # With every h_i = h the weights are uniform, the fit is OLS whatever s is, and the
        # moment update is s = RSS / (n - p) - h^2 in one step (reading R2).
        rng = random.Random(31)
        rows = []
        for e in range(8):
            rows += make_episode_rows(rng, f"ep{e}", "pair0", turns=20, sigma_j=3.0,
                                      half_width_range_j=(1.0, 1.0))[0]
        n, h2 = len(rows), 1.0
        X = [design_row(r) for r in rows]
        y = [r.energy_j for r in rows]
        _, M_inv_x, rss_x = exact_wls(X, y, [1.0] * n)
        s_x = rss_x / (n - T.P) - Fraction(h2)
        self.assertGreater(s_x, 0)
        model = fit_energy_model(rows)
        # RSS is stationary in the coefficients at the least-squares minimum, so the solve's
        # error enters only at second order; the float noise is a few eps relative on s + h^2.
        bar = BAND_FLOOR * EPS
        self.assertLessEqual(abs(Fraction(model.sigma2_per_turn) - s_x) / (s_x + Fraction(h2)), bar)
        # Band not empty: 1% of the printed standard error of s, about (s + h^2) sqrt(2/(n-p)).
        self.assertLess(bar, 0.01 * math.sqrt(2 / (n - T.P)))
        # cov = (s + h^2) (X'X)^-1, compared entrywise against the largest entry's scale.
        cov_x = [[(s_x + Fraction(h2)) * M_inv_x[j][k] for k in range(T.P)] for j in range(T.P)]
        fit = T.weighted_fit(X, y, [1.0] * n)
        kappa = cond1(fit["scaled_normal"])
        d = fit["scale"]
        scaled = lambda c, j, k: c * Fraction(d[j]) * Fraction(d[k])
        worst = max(abs(scaled(Fraction(model.cov[j][k]) - cov_x[j][k], j, k)) for j in range(T.P) for k in range(T.P))
        norm = max(abs(scaled(cov_x[j][k], j, k)) for j in range(T.P) for k in range(T.P))
        # Normwise relative error of the scaled inverse: float noise kappa * eps (p solves of the
        # same system) plus the s error above; band floor.
        self.assertLessEqual(float(worst / norm), BAND_FLOOR * (kappa + 1) * EPS)

    def test_fixed_point_satisfies_paule_mandel_equation(self):
        # Heterogeneous half-widths (0.5-6 J against a 3 J extra sd) make the weighting matter.
        world = make_world(41, n_episodes=40, n_groups=1, half_width_range_j=(0.5, 6.0))
        rows = all_rows(world)
        n = len(rows)
        model = fit_energy_model(rows)
        self.assertGreater(model.sigma2_per_turn, 0.0)
        q = T.weighted_q(rows, model.sigma2_per_turn)
        # Q is a weighted least-squares minimum (stationary in the coefficients); its float noise
        # is a few eps relative, and the stopping rule leaves s within CONVERGENCE_REL of its
        # fixed point times a contraction factor measured below 1e-2 on these worlds.
        bar = BAND_FLOOR * EPS * (n - T.P)
        self.assertLessEqual(abs(q - (n - T.P)), bar, f"Q={q!r} n-p={n - T.P}")
        # The world exercises the rule: the one-step unit-weight moment estimate (no iteration)
        # misses the equation by far more than the bar.
        X = [design_row(r) for r in rows]
        hv = [r.energy_half_width_j ** 2 for r in rows]
        fit0 = T.weighted_fit(X, [r.energy_j for r in rows], [1.0] * n)
        s0 = T._moment_update([1.0] * n, fit0["resid"], fit0["leverage"], hv)
        self.assertGreater(abs(T.weighted_q(rows, s0) - (n - T.P)), 1e3 * bar)

    def test_row_order_does_not_change_a_bit(self):
        rows = all_rows(make_world(51, n_episodes=10, n_groups=1, half_width_range_j=(0.5, 6.0)))
        shuffled = rows[:]
        random.Random(0).shuffle(shuffled)
        # Exact: every sum is math.fsum (correctly rounded), so the same multiset of rows gives
        # bit-identical results whatever the order.
        self.assertEqual(fit_energy_model(rows), fit_energy_model(shuffled))

    def test_refusals(self):
        rows = all_rows(make_world(61, n_episodes=1, n_groups=1))
        with self.assertRaises(ValueError):
            fit_energy_model(rows[:T.P])          # no degrees of freedom for the moment equation
        with self.assertRaises(ValueError):
            fit_energy_model([replace(r, prefill_tokens=0) for r in rows])  # a zero design column
        # s = 0 and a zero half-width would give an infinite weight. A fit on float data never
        # reaches it (float residuals are never all exactly zero), so the guard is tested where
        # it lives.
        with self.assertRaises(ValueError):
            T._weights(0.0, [1.0, 0.0])


# ---------------------------------------------------------------- predict_episode, residual_score

def hand_model(coef, cov, sigma2):
    return EnergyModel(T.NAMES, tuple(coef), tuple(tuple(r) for r in cov), sigma2, 100)


class PredictAndScoreTest(unittest.TestCase):
    def test_predict_hand_case(self):
        rows = [TurnRow("e", "g", 10, 4, 2, 1.0, 0.0, 1.0),    # x = [1, 4, 2, 20, 40]
                TurnRow("e", "g", 16, 6, 3, 1.0, 0.0, 1.0)]    # x = [1, 6, 3, 48, 96]
        # S = [2, 10, 5, 68, 136]; mean = 2*1 + 10*0.5 + 5*2 + 68*0.25 + 136*0.125 = 51
        cov = [[0.0] * 5 for _ in range(5)]
        cov[0][0], cov[1][1], cov[0][1], cov[1][0] = 1.0, 0.25, 0.5, 0.5
        # quad = 2^2*1 + 10^2*0.25 + 2*(2*10*0.5) = 49; per-turn part 2 * 6 = 12; var = 61
        model = hand_model((1.0, 0.5, 2.0, 0.25, 0.125), cov, 6.0)
        mean, sd = predict_episode(model, rows)
        # Exact: every intermediate is a small dyadic rational and sqrt is correctly rounded.
        self.assertEqual(mean, 51.0)
        self.assertEqual(sd, math.sqrt(61.0))

    def test_predict_no_rows(self):
        model = hand_model((1.0,) * 5, [[1.0] * 5] * 5, 4.0)
        self.assertEqual(predict_episode(model, []), (0.0, 0.0))  # exact: empty sums are 0

    def test_score_three_four_five(self):
        rows = [TurnRow("e", "g", 10, 4, 2, 1.0, 0.0, 1.0)]    # x = [1, 4, 2, 20, 40]
        model = hand_model((1.0, 0.5, 2.0, 0.25, 0.125), [[0.0] * 5] * 5, 9.0)
        # predicted = 1 + 2 + 4 + 5 + 5 = 17; sd_pred = sqrt(9) = 3; half-width 4 -> denominator 5
        self.assertEqual(residual_score(model, rows, 27.0, 4.0), 2.0)    # exact: (27-17)/5
        self.assertEqual(residual_score(model, rows, 7.0, 4.0), -2.0)    # exact: (7-17)/5


# ---------------------------------------------------------------- min_detectable_hidden_decode_tokens

class MinDetectableTest(unittest.TestCase):
    def setUp(self):
        self.rows = [TurnRow("e", "g", 1_000, 4, 2, 1.0, 0.0, 1.0),
                     TurnRow("e", "g", 3_000, 6, 3, 1.0, 0.0, 1.0)]   # mean context 2000
        # cov zero, sigma2 4.5 per turn, 2 turns -> sd_pred 3; half-width 4 -> denominator 5
        self.model = hand_model((1.0, 0.5, 0.25, 1e-5, 0.0), [[0.0] * 5] * 5, 4.5)
        self.e = 0.25 + 1e-5 * 2_000   # 0.27 J per hidden token

    def test_standard_normal_quantiles(self):
        # Printed table values: z_0.95 = 1.645 (3 decimals -> half a unit 0.0005),
        # z_0.80 = 0.8416 (4 decimals -> 0.00005).
        self.assertAlmostEqual(NormalDist().inv_cdf(0.95), 1.645, delta=0.0005)
        self.assertAlmostEqual(NormalDist().inv_cdf(0.80), 0.8416, delta=0.00005)

    def test_closed_form(self):
        h = min_detectable_hidden_decode_tokens(self.model, self.rows, alpha=0.05, power=0.8,
                                                measured_half_width_j=4.0)
        expected = (NormalDist().inv_cdf(0.95) + NormalDist().inv_cdf(0.8)) * 5.0 / self.e
        # A handful of operations: float noise a few eps relative; band floor.
        self.assertAlmostEqual(h, expected, delta=BAND_FLOOR * EPS * expected)
        # Hand value: 2.4865 * 5 / 0.27 = 46.05 tokens (2 decimals printed -> 0.005).
        self.assertAlmostEqual(h, 46.05, delta=0.005)

    def test_defining_property_power_at_threshold(self):
        h = min_detectable_hidden_decode_tokens(self.model, self.rows, alpha=0.05, power=0.8,
                                                measured_half_width_j=4.0)
        shift = h * self.e / 5.0
        p = 1.0 - NormalDist().cdf(NormalDist().inv_cdf(0.95) - shift)
        # cdf(inv_cdf(.)) round trip: float noise a few eps; band floor.
        self.assertAlmostEqual(p, 0.8, delta=BAND_FLOOR * EPS)

    def test_power_equal_alpha_needs_no_tokens(self):
        h = min_detectable_hidden_decode_tokens(self.model, self.rows, alpha=0.2, power=0.2,
                                                measured_half_width_j=4.0)
        # z_0.8 + z_0.2 = 0 by symmetry; float noise of inv_cdf a few eps times z ~ 1, scaled by
        # D / e = 18.5 tokens per unit z; band floor.
        self.assertAlmostEqual(h, 0.0, delta=BAND_FLOOR * EPS * 5.0 / self.e)

    def test_nonpositive_per_token_energy_is_infinite(self):
        model = hand_model((1.0, 0.5, -0.02, 1e-5, 0.0), [[0.0] * 5] * 5, 4.5)   # e = 0.0 J
        self.assertEqual(min_detectable_hidden_decode_tokens(model, self.rows, alpha=0.05, power=0.8,
                                                             measured_half_width_j=4.0), math.inf)

    def test_refusals(self):
        for kw in ({"alpha": 0.0, "power": 0.8}, {"alpha": 0.05, "power": 1.0}):
            with self.assertRaises(ValueError):
                min_detectable_hidden_decode_tokens(self.model, self.rows, measured_half_width_j=4.0, **kw)
        with self.assertRaises(ValueError):
            min_detectable_hidden_decode_tokens(self.model, [], alpha=0.05, power=0.8,
                                                measured_half_width_j=4.0)


# ---------------------------------------------------------------- grouped_benign_threshold

class GroupedThresholdTest(unittest.TestCase):
    def test_quantile_definition_by_hand(self):
        xs = [5.0, 1.0, 4.0, 2.0, 3.0]
        self.assertEqual(T.empirical_quantile(xs, Fraction(3, 5)), 3.0)    # k = ceil(3.0) = 3
        self.assertEqual(T.empirical_quantile(xs, Fraction(61, 100)), 4.0) # k = ceil(3.05) = 4
        self.assertEqual(T.empirical_quantile(xs, 1), 5.0)                 # k = n
        # alpha read as its printed decimal: (1 - 0.05) * 20 = 19 exactly, (1 - 0.3) * 10 = 7.
        twenty = [float(i) for i in range(1, 21)]
        self.assertEqual(T.empirical_quantile(twenty, 1 - T._decimal(0.05)), 19.0)
        self.assertEqual(T.empirical_quantile(twenty[:10], 1 - T._decimal(0.3)), 7.0)

    def test_threshold_is_order_statistic_of_held_out_scores(self):
        world = make_world(71, n_episodes=40, n_groups=4)
        scores = sorted(s for _, _, s in T.held_out_benign_scores(world))
        self.assertEqual(len(scores), 40)
        # k = ceil(0.95 * 40) = 38 by hand. Exact: identical code on identical inputs.
        self.assertEqual(grouped_benign_threshold(world, alpha=0.05), scores[37])

    def test_each_fold_is_fit_on_the_other_groups_only(self):
        world = make_world(72, n_episodes=40, n_groups=4)
        held = {eid: (g, s) for eid, g, s in T.held_out_benign_scores(world)}
        # Manual fold for pair1. Exact: identical code on identical inputs.
        train = [r for eid in sorted(world) if held[eid][0] != "pair1" for r in world[eid][0]]
        model = fit_energy_model(train)
        for eid, (g, s) in held.items():
            if g == "pair1":
                rows, total, hw = world[eid]
                self.assertEqual(s, residual_score(model, rows, total, hw))
        # Leakage check: changing one pair1 episode's turn energies cannot move any other pair1
        # score (its fold never sees pair1) and must move every other pair's scores.
        target = next(eid for eid in sorted(world) if held[eid][0] == "pair1")
        rows, total, hw = world[target]
        changed = dict(world)
        changed[target] = ([replace(r, energy_j=r.energy_j + 50.0) for r in rows], total, hw)
        held2 = {eid: (g, s) for eid, g, s in T.held_out_benign_scores(changed)}
        for eid, (g, s) in held.items():
            if eid == target:
                continue
            if g == "pair1":
                self.assertEqual(held2[eid][1], s)
            else:
                self.assertNotEqual(held2[eid][1], s)

    def test_refusals(self):
        world = make_world(73, n_episodes=6, n_groups=1)
        with self.assertRaises(ValueError):
            grouped_benign_threshold(world, alpha=0.05)        # one task pair: no other pairs to fit on
        world = make_world(74, n_episodes=8, n_groups=2)
        rows, total, hw = world["ep0000"]
        mixed = dict(world)
        mixed["ep0000"] = (rows[:10] + [replace(r, group="pair1") for r in rows[10:]], total, hw)
        with self.assertRaises(ValueError):
            grouped_benign_threshold(mixed, alpha=0.05)
        for alpha in (0.0, 1.0):
            with self.assertRaises(ValueError):
                grouped_benign_threshold(world, alpha=alpha)


# ---------------------------------------------------------------- production-shaped worlds, end to end

class EndToEndTest(unittest.TestCase):
    def test_fit_recovers_coefficients_and_sigma2(self):
        sigma_j = 3.0
        rows = all_rows(make_world(81, n_episodes=200, n_groups=8, sigma_j=sigma_j))
        model = fit_energy_model(rows)
        lines = []
        for j, name in enumerate(T.NAMES):
            se = math.sqrt(model.cov[j][j])
            z = (model.coef[j] - BETA[j]) / se
            lines.append(f"{name}: fit {model.coef[j]:.6g} true {BETA[j]:.6g} se {se:.3g} z {z:+.2f}")
        # 4 standard errors: two-sided normal tail 6.3e-5 per coefficient for a correct fit.
        for j in range(T.P):
            self.assertLessEqual(abs(model.coef[j] - BETA[j]), 4 * math.sqrt(model.cov[j][j]), "\n".join(lines))
        # SE of the moment estimate: Var Q = 2(n-p) and dQ/ds = -sum a_i (1 - lev_i) ~ -sum a_i,
        # so se(s) ~ sqrt(2(n-p)) / sum_i 1/(s + h_i^2); 4 standard errors as above.
        n = len(rows)
        se_s = math.sqrt(2 * (n - T.P)) / math.fsum(1 / (sigma_j ** 2 + r.energy_half_width_j ** 2) for r in rows)
        self.assertLessEqual(abs(model.sigma2_per_turn - sigma_j ** 2), 4 * se_s,
                             f"sigma2 {model.sigma2_per_turn:.4g} true {sigma_j ** 2} se {se_s:.3g}")

    def test_benign_scores_are_standard_normal_and_threshold_near_z(self):
        world = make_world(82, n_episodes=400, n_groups=8)
        scores = [s for _, _, s in T.held_out_benign_scores(world)]
        n = len(scores)
        mean = math.fsum(scores) / n
        sd = math.sqrt(math.fsum((s - mean) ** 2 for s in scores) / (n - 1))
        # Under the correct model a held-out score is N(0, 1): se(mean) = 1/sqrt(n),
        # se(sd) ~ 1/sqrt(2n); 4 standard errors (two-sided tail 6.3e-5).
        self.assertLessEqual(abs(mean), 4 / math.sqrt(n), f"mean {mean:.4f}")
        self.assertLessEqual(abs(sd - 1.0), 4 / math.sqrt(2 * n), f"sd {sd:.4f}")
        threshold = grouped_benign_threshold(world, alpha=0.05)
        z = NormalDist().inv_cdf(0.95)
        # se of the sample 0.95 quantile = sqrt(a(1-a)/n) / phi(z); 4 standard errors.
        se_q = math.sqrt(0.05 * 0.95 / n) / NormalDist().pdf(z)
        self.assertLessEqual(abs(threshold - z), 4 * se_q, f"threshold {threshold:.4f} z {z:.4f} se {se_q:.3f}")
        # Inverse-ECDF definition: at most alpha of the held-out scores lie strictly above it.
        self.assertLessEqual(sum(s > threshold for s in scores), math.floor(0.05 * n))

    def test_detection_at_min_detectable_matches_power(self):
        alpha, power = 0.05, 0.8
        train = make_world(83, n_episodes=200, n_groups=8)
        model = fit_energy_model(all_rows(train))
        z_alpha = NormalDist().inv_cdf(1 - alpha)

        def h_min(rows):
            return min_detectable_hidden_decode_tokens(model, rows, alpha=alpha, power=power,
                                                       measured_half_width_j=1.0)

        n_test = 800
        table = []
        # Hidden work that costs zero energy leaves the measured total equal to a benign one's;
        # it gets its own seed so it is an independent draw from the H=0 world.
        for label, seed, hidden, expected in (("H=0", 84, None, alpha), ("H=H_min", 84, h_min, power),
                                              ("H=H_min at zero energy", 85, None, alpha)):
            world = make_world(seed, n_episodes=n_test, n_groups=8, hidden_tokens=hidden)
            flagged = sum(residual_score(model, rows, total, hw) > z_alpha for rows, total, hw in world.values())
            rate = flagged / n_test
            se = math.sqrt(expected * (1 - expected) / n_test)
            table.append((label, rate, expected, se))
        msg = "\n".join(f"{lab}: detected {r:.3f} expected {e:.3f} binomial se {s:.3f}" for lab, r, e, s in table)
        for _, rate, expected, se in table:
            # 4 binomial standard errors (two-sided normal tail 6.3e-5).
            self.assertLessEqual(abs(rate - expected), 4 * se, msg)


if __name__ == "__main__":
    unittest.main()
