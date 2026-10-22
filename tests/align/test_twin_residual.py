"""Twin agreement for lane A7 residual: joulewise.align.energy_residual vs tests/align/twins/residual_twin.

Written by the blind executing reviewer (review round 2, lane head 971b2f31c). Both
implementations run on the same seeded, production-shaped synthetic worlds and every
number-producing output is compared directly at the orchestrator's bars, stated beside
each assertion. Round 1 reconciled one reading (R6, predict_episode's variance); the lead
ruled the twin's reading (var = s' cov s + n * sigma2) and the lane now implements it, so
nothing is patched here: lane and twin are compared as they are.

Bars (set by the orchestrator, not chosen here):
- an output with a printed uncertainty: within 1% of the smaller of the two printed
  uncertainties (a coefficient against its standard error; a predicted mean against
  its predicted sd);
- otherwise 1e-6 relative, or 1e-6 absolute in the output's unit when the value is
  below 1 (sigma2, standard errors, correlations, sd, scores, thresholds, H_min). Both
  bars lie far above 1e6 * float64 epsilon (2.2e-10) and far below any printed digit.
No function here draws random numbers, so there is no Monte Carlo bar.

Readings the two builders resolve differently, so they are not compared here (each is
reported, not hidden):
- power <= alpha in min_detectable_hidden_decode_tokens: the lane returns 0 (no hidden
  work needed) and the twin returns the raw, negative formula. Only power > alpha is
  compared.
- invalid inputs (non-finite rows, empty episodes, rank-deficient designs, mixed-group
  episodes, too few turns): the lane excludes and flags (lead's round-1 rulings
  RES-R1-01 and RES-R1-03), the twin raises. Only clean, full-rank worlds are compared.
- the quantile rank: the lane forms ceil((1 - alpha) * m) in binary floating point, the
  twin in exact decimal arithmetic. They agree for alpha in {0.01, 0.025, 0.05, 0.1, 0.2}
  at every m up to 5000 (checked), which are the alphas compared here.

The test skips cleanly where the lane module is absent (the twin branch alone).
"""

from __future__ import annotations

import importlib.util
import math
import random
import unittest

_HAVE_LANE = importlib.util.find_spec("joulewise.align.energy_residual") is not None

if _HAVE_LANE:
    from joulewise.align import energy_residual as L
from tests.align.twins import residual_twin as T

# Regimes: (coefficients: J, J/token, J/token, J/(ctx*token), J/(ctx*token)),
# extra per-turn sd J, turn half-width range J, episode half-width J, turn-count range,
# starting-context range in tokens.
# nvml8b: an 8B model on a whole GPU; m3max: the M3 Max instrument regime (about 1 J
# per-run attribution limit); boundary: no extra variance, so the moment estimate sits
# on or near the sigma2 = 0 truncation; longctx: a long-context agent (contexts start at
# 20k-60k tokens and reach about 200k) with few turns and wide turn half-widths.
_REGIMES = {
    "nvml8b": ((3.0, 0.0012, 0.22, 3.0e-6, 2.0e-7), 2.5, (0.2, 2.5), 1.5, (8, 40), (1500, 3000)),
    "m3max": ((1.0, 0.0004, 0.35, 0.15 / 4096, 5.0e-8), 0.5, (0.3, 1.2), 1.0, (8, 40), (1500, 3000)),
    "boundary": ((5.0, 0.005, 0.12, 1.0e-5, 4.0e-6), 0.0, (0.5, 2.0), 1.0, (8, 40), (1500, 3000)),
    "longctx": ((4.0, 0.0009, 0.30, 2.0e-6, 6.0e-8), 6.0, (1.0, 8.0), 3.0, (4, 15), (20_000, 60_000)),
}


def _world(seed: int, regime: str, n_groups: int, per_group: int):
    """{episode_id: (row specs, measured total J, episode half-width J)}.

    Context grows by every prefill (tool result, heavy-tailed 40-6000 tokens) and
    decode (20-2500). Each turn's measured energy is its true energy plus N(0, h_i^2);
    the measured total is the sum of TRUE turn energies plus N(0, h_episode^2), the
    pipeline's separate whole-episode integral (lead's RES-R1-02 ruling).
    """
    coef, sigma, (hlo, hhi), hw_ep, (tlo, thi), (clo, chi) = _REGIMES[regime]
    rng = random.Random(seed)
    out = {}
    for g in range(n_groups):
        for i in range(per_group):
            eid = f"{regime}-{seed}-{g}-{i}"
            ctx = rng.randint(clo, chi)
            specs, true_total = [], 0.0
            for k in range(rng.randint(tlo, thi)):
                pf = rng.randint(200, 1200) if k == 0 else min(
                    6000, max(40, int(rng.lognormvariate(math.log(600), 1.0))))
                dc = min(2500, max(20, int(rng.lognormvariate(math.log(300), 0.8))))
                h = rng.uniform(hlo, hhi)
                x = (1, pf, dc, ctx * dc, ctx * pf)
                e_true = math.fsum(a * b for a, b in zip(x, coef)) + rng.gauss(0, sigma)
                specs.append((eid, f"shade/pair-{g}", ctx, pf, dc, pf / 3000 + dc / 60,
                              e_true + rng.gauss(0, h), h))
                true_total += e_true
                ctx += pf + dc
            out[eid] = (specs, true_total + rng.gauss(0, hw_ep), hw_ep)
    return out


def _rows(module, specs):
    return [module.TurnRow(*s) for s in specs]


def _bench(module, world):
    return {eid: (_rows(module, specs), total, hw) for eid, (specs, total, hw) in world.items()}


def _close(a: float, b: float) -> bool:
    # Orchestrator bar for outputs with no printed uncertainty: 1e-6 relative, or
    # 1e-6 absolute in the output's unit when the value is below 1. Far above
    # 1e6 * float64 epsilon (2.2e-10).
    if math.isinf(a) or math.isinf(b):
        return a == b
    scale = max(abs(a), abs(b))
    return abs(a - b) <= (1e-6 * scale if scale >= 1 else 1e-6)


_FIT_CASES = [(regime, seed) for regime in _REGIMES for seed in range(8)]


@unittest.skipUnless(_HAVE_LANE, "lane module joulewise.align.energy_residual absent (twin branch)")
class TestTwinResidualAgreement(unittest.TestCase):
    def test_fit_agrees(self):
        worst = {"coef/SE": 0.0, "SE rel": 0.0, "corr abs": 0.0, "sigma2 abs": 0.0}
        for regime, seed in _FIT_CASES:
            world = _world(50_000 + seed, regime, 4, 12)
            specs = [s for v in world.values() for s in v[0]]
            ml = L.fit_energy_model(_rows(L, specs))
            mt = T.fit_energy_model(_rows(T, specs))
            label = f"{regime} seed {seed} n={len(specs)}"
            self.assertEqual(getattr(ml, "flags", ()), (), label)  # clean world: no flags
            self.assertEqual(ml.n_turns, mt.n_turns, label)  # integer count: exact
            self.assertTrue(_close(ml.sigma2_per_turn, mt.sigma2_per_turn),
                            (label, ml.sigma2_per_turn, mt.sigma2_per_turn))
            worst["sigma2 abs"] = max(worst["sigma2 abs"], abs(ml.sigma2_per_turn - mt.sigma2_per_turn))
            for j in range(5):
                se_l, se_t = math.sqrt(ml.cov[j][j]), math.sqrt(mt.cov[j][j])
                # A coefficient's printed uncertainty is its SE: 1% of the smaller SE.
                d = abs(ml.coef[j] - mt.coef[j]) / min(se_l, se_t)
                worst["coef/SE"] = max(worst["coef/SE"], d)
                self.assertLessEqual(d, 0.01, (label, j, ml.coef[j], mt.coef[j]))
                # An SE has no printed uncertainty of its own: 1e-6 relative.
                self.assertTrue(_close(se_l, se_t), (label, j, se_l, se_t))
                worst["SE rel"] = max(worst["SE rel"], abs(se_l - se_t) / se_t)
                for k in range(5):
                    # Correlations are unitless and at most 1 in size: 1e-6 absolute.
                    rl = ml.cov[j][k] / math.sqrt(ml.cov[j][j] * ml.cov[k][k])
                    rt = mt.cov[j][k] / math.sqrt(mt.cov[j][j] * mt.cov[k][k])
                    worst["corr abs"] = max(worst["corr abs"], abs(rl - rt))
                    self.assertLessEqual(abs(rl - rt), 1e-6, (label, j, k, rl, rt))
        print("\nfit agreement, worst over", len(_FIT_CASES), "worlds:", worst)

    def test_predict_episode_agrees(self):
        for regime, seed in _FIT_CASES[::2]:
            world = _world(60_000 + seed, regime, 3, 10)
            specs = [s for v in world.values() for s in v[0]]
            ml = L.fit_energy_model(_rows(L, specs))
            mt = T.fit_energy_model(_rows(T, specs))
            for eid, (ep_specs, _, _) in list(world.items())[:6]:
                rl, rt = _rows(L, ep_specs), _rows(T, ep_specs)
                mean_l, sd_l = L.predict_episode(ml, rl)
                mean_t, sd_t = T.predict_episode(mt, rt)
                # The mean's printed uncertainty is the predicted sd: 1% of the smaller.
                self.assertLessEqual(abs(mean_l - mean_t), 0.01 * min(sd_l, sd_t), (eid, mean_l, mean_t))
                # The sd has no printed uncertainty: 1e-6 relative.
                self.assertTrue(_close(sd_l, sd_t), (eid, sd_l, sd_t))
                # Same model into both (duck-typed) isolates predict from fit: 1e-6 bar.
                mean_x, sd_x = T.predict_episode(ml, rt)
                self.assertTrue(_close(mean_l, mean_x), (eid, mean_l, mean_x))
                self.assertTrue(_close(sd_l, sd_x), (eid, sd_l, sd_x))

    def test_score_and_power_agree(self):
        for regime, seed in _FIT_CASES[::2]:
            world = _world(70_000 + seed, regime, 3, 10)
            specs = [s for v in world.values() for s in v[0]]
            ml = L.fit_energy_model(_rows(L, specs))
            mt = T.fit_energy_model(_rows(T, specs))
            for eid, (ep_specs, total, hw) in list(world.items())[:6]:
                rl, rt = _rows(L, ep_specs), _rows(T, ep_specs)
                for shift in (0.0, 25.0, 250.0):  # J of unexplained energy
                    sl = L.residual_score(ml, rl, total + shift, hw)
                    st = T.residual_score(mt, rt, total + shift, hw)
                    # A score has no printed uncertainty: 1e-6 rel (abs below 1).
                    self.assertTrue(_close(sl, st), (eid, shift, sl, st))
                for alpha in (0.01, 0.05, 0.1):
                    for power in (0.5, 0.8, 0.9, 0.99):
                        hl = L.min_detectable_hidden_decode_tokens(
                            ml, rl, alpha=alpha, power=power, measured_half_width_j=hw)
                        ht = T.min_detectable_hidden_decode_tokens(
                            mt, rt, alpha=alpha, power=power, measured_half_width_j=hw)
                        # H_min has no printed uncertainty: 1e-6 relative.
                        self.assertTrue(_close(hl, ht), (eid, alpha, power, hl, ht))

    def test_grouped_threshold_agrees(self):
        # (regime, seed, groups, episodes per group); m = groups * per includes values
        # where (1 - alpha) * m is an integer for every compared alpha (m = 20, 60, 100,
        # 300), the rank edge a float/rational difference would hit first.
        cases = [("nvml8b", 0, 5, 12), ("m3max", 1, 4, 15), ("boundary", 2, 6, 10),
                 ("nvml8b", 3, 2, 30), ("longctx", 4, 4, 5), ("m3max", 5, 10, 30)]
        for regime, seed, groups, per in cases:
            world = _world(90_000 + seed, regime, groups, per)
            bl, bt = _bench(L, world), _bench(T, world)
            twin_scores = T.held_out_benign_scores(bt)
            self.assertEqual(len(twin_scores), groups * per)  # integer count: exact
            # Per-episode held-out scores first (localizes any disagreement): the lane's
            # public functions, fit on the other task pairs, against the twin's scores.
            models = {}
            for eid, group, st in twin_scores:
                if group not in models:
                    models[group] = L.fit_energy_model(
                        [r for rows, _, _ in bl.values() if rows[0].group != group for r in rows])
                rows, total, hw = bl[eid]
                sl = L.residual_score(models[group], rows, total, hw)
                self.assertTrue(_close(sl, st), (regime, eid, sl, st))  # 1e-6 bar
            for alpha in (0.01, 0.025, 0.05, 0.1, 0.2):
                tl = L.grouped_benign_threshold(bl, alpha=alpha)
                tt = T.grouped_benign_threshold(bt, alpha=alpha)
                # Threshold: no printed uncertainty, 1e-6 relative (abs below 1).
                self.assertTrue(_close(tl, tt), (regime, groups * per, alpha, tl, tt))
                self.assertEqual(getattr(tl, "flags", ()), ())


if __name__ == "__main__":
    unittest.main()
