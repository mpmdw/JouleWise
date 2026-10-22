"""Twin agreement for lane A7 residual: joulewise.align.energy_residual vs tests/align/twins/residual_twin.

Written by the blind executing reviewer (review round 1). Both implementations run on
the same seeded, production-shaped synthetic worlds and every number-producing output
is compared at the orchestrator's bars (stated beside each assertion).

One reading differs between the two and is reconciled explicitly, not hidden:
R6, predict_episode's variance. The lane adds sum(h_turn**2) of the scored rows
(var = s'cov s + sum(sigma2 + h_i**2)); the twin adds only n*sigma2. Test
test_predict_episode_r6_identity checks that this is the ONLY difference
(lane sd**2 == twin sd**2 + sum h_i**2). The score, threshold and power tests then
compare the lane against the twin with that one term added (a patched twin
predict_episode), so every other step of those paths is checked at the 1e-6 bar.
Unreconciled, the R6 difference moves the threshold and H_min by roughly 5-25 %
on these worlds; which reading is right is a ruling for the lead (review finding).

No Monte Carlo output exists in these functions (no random draws), so every
comparison is deterministic and uses the non-Monte-Carlo bars. The test skips
cleanly where the lane module is absent (the twin branch alone).
"""

from __future__ import annotations

import importlib.util
import math
import random
import unittest
from unittest import mock

_HAVE_LANE = importlib.util.find_spec("joulewise.align.energy_residual") is not None

if _HAVE_LANE:
    from joulewise.align import energy_residual as L
from tests.align.twins import residual_twin as T

# Regimes: (coefficients J, J/token, J/token, J/(ctx*token), J/(ctx*token)),
# extra per-turn sd J, turn half-width range J, episode half-width J.
# nvml8b: an 8B model on a whole GPU; m3max: the M3 Max instrument regime
# (about 1 J per-run attribution limit); boundary: no extra variance, so the
# moment estimate sits on or near the sigma2 = 0 truncation.
_REGIMES = {
    "nvml8b": ((3.0, 0.0012, 0.22, 3.0e-6, 2.0e-7), 2.5, (0.2, 2.5), 1.5),
    "m3max": ((1.0, 0.0004, 0.35, 0.15 / 4096, 5.0e-8), 0.5, (0.3, 1.2), 1.0),
    "boundary": ((5.0, 0.005, 0.12, 1.0e-5, 4.0e-6), 0.0, (0.5, 2.0), 1.0),
}


def _world(seed: int, regime: str, n_groups: int, per_group: int):
    """{episode_id: (rows tuple-spec, measured total J, episode half-width J)}.

    Turns 8-40 per episode; context starts at 1.5k-3k tokens and grows by every
    prefill (tool result, heavy-tailed 40-6000 tokens) and decode (20-2500).
    Measured total = sum of true turn energies + episode measurement noise.
    """
    coef, sigma, (hlo, hhi), hw_ep = _REGIMES[regime]
    rng = random.Random(seed)
    out = {}
    for g in range(n_groups):
        for i in range(per_group):
            eid = f"{regime}-{seed}-{g}-{i}"
            ctx = rng.randint(1500, 3000)
            specs, true_total = [], 0.0
            for k in range(rng.randint(8, 40)):
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
    # Orchestrator bar for outputs with no printed uncertainty: 1e-6 relative,
    # or 1e-6 absolute in the output's unit when the value is below 1.
    # Both lie far above 1e6 * float64 epsilon (2.2e-10).
    if math.isinf(a) or math.isinf(b):
        return a == b
    scale = max(abs(a), abs(b))
    return abs(a - b) <= (1e-6 * scale if scale >= 1 else 1e-6)


def _twin_predict_lane_r6(model, rows):
    """Twin predict_episode with the lane's R6 term (sum h_i**2) added; nothing else changed."""
    mean, sd = _TWIN_PREDICT(model, rows)
    return mean, math.sqrt(sd * sd + math.fsum(float(r.energy_half_width_j) ** 2 for r in rows))


_TWIN_PREDICT = T.predict_episode

_FIT_CASES = [(regime, seed) for regime in _REGIMES for seed in range(8)]


@unittest.skipUnless(_HAVE_LANE, "lane module joulewise.align.energy_residual absent (twin branch)")
class TestTwinResidualAgreement(unittest.TestCase):
    def test_fit_agrees(self):
        worst = {"coef/SE": 0.0, "SE rel": 0.0, "corr abs": 0.0, "sigma2": 0.0}
        for regime, seed in _FIT_CASES:
            world = _world(50_000 + seed, regime, 4, 12)
            specs = [s for v in world.values() for s in v[0]]
            ml = L.fit_energy_model(_rows(L, specs))
            mt = T.fit_energy_model(_rows(T, specs))
            label = f"{regime} seed {seed} n={len(specs)}"
            self.assertEqual(ml.n_turns, mt.n_turns, label)  # integer count: exact
            self.assertTrue(_close(ml.sigma2_per_turn, mt.sigma2_per_turn),
                            (label, ml.sigma2_per_turn, mt.sigma2_per_turn))
            worst["sigma2"] = max(worst["sigma2"], abs(ml.sigma2_per_turn - mt.sigma2_per_turn))
            for j in range(5):
                se_l, se_t = math.sqrt(ml.cov[j][j]), math.sqrt(mt.cov[j][j])
                # Coefficient j has a printed uncertainty, its SE: bar is 1% of the
                # smaller of the two printed SEs (orchestrator's half-width rule).
                d = abs(ml.coef[j] - mt.coef[j]) / min(se_l, se_t)
                worst["coef/SE"] = max(worst["coef/SE"], d)
                self.assertLessEqual(d, 0.01, (label, j, ml.coef[j], mt.coef[j]))
                # An SE carries no printed uncertainty of its own: 1e-6 relative.
                self.assertTrue(_close(se_l, se_t), (label, j, se_l, se_t))
                worst["SE rel"] = max(worst["SE rel"], abs(se_l - se_t) / se_t)
                for k in range(5):
                    # Correlations are unitless and below 1: 1e-6 absolute.
                    rl = ml.cov[j][k] / math.sqrt(ml.cov[j][j] * ml.cov[k][k])
                    rt = mt.cov[j][k] / math.sqrt(mt.cov[j][j] * mt.cov[k][k])
                    worst["corr abs"] = max(worst["corr abs"], abs(rl - rt))
                    self.assertLessEqual(abs(rl - rt), 1e-6, (label, j, k, rl, rt))
        print("\nfit agreement, worst over", len(_FIT_CASES), "worlds:", worst)

    def test_predict_episode_r6_identity(self):
        for regime, seed in _FIT_CASES[::2]:
            world = _world(60_000 + seed, regime, 3, 10)
            specs = [s for v in world.values() for s in v[0]]
            ml = L.fit_energy_model(_rows(L, specs))
            mt = T.fit_energy_model(_rows(T, specs))
            for eid, (ep_specs, _, _) in list(world.items())[:6]:
                rl, rt = _rows(L, ep_specs), _rows(T, ep_specs)
                mean_l, sd_l = L.predict_episode(ml, rl)
                mean_t, sd_t = T.predict_episode(mt, rt)
                # The mean has a printed uncertainty (the sd): 1% of the smaller sd.
                self.assertLessEqual(abs(mean_l - mean_t), 0.01 * min(sd_l, sd_t), (eid, mean_l, mean_t))
                # R6: the lane's variance exceeds the twin's by exactly sum(h_i**2)
                # of the scored rows. No printed uncertainty on a variance: 1e-6 relative.
                h2 = math.fsum(s[7] ** 2 for s in ep_specs)
                self.assertTrue(_close(sd_l ** 2, sd_t ** 2 + h2), (eid, sd_l ** 2, sd_t ** 2, h2))
                # Same model into both (duck-typed): isolates predict from fit.
                mean_x, sd_x = T.predict_episode(ml, rt)
                self.assertTrue(_close(mean_l, mean_x), (eid, mean_l, mean_x))
                self.assertTrue(_close(sd_l ** 2, sd_x ** 2 + h2), (eid, sd_l, sd_x))

    def test_score_and_power_agree_under_reconciled_r6(self):
        with mock.patch.object(T, "predict_episode", _twin_predict_lane_r6):
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
                        for power in (0.5, 0.8, 0.9):
                            hl = L.min_detectable_hidden_decode_tokens(
                                ml, rl, alpha=alpha, power=power, measured_half_width_j=hw)
                            ht = T.min_detectable_hidden_decode_tokens(
                                mt, rt, alpha=alpha, power=power, measured_half_width_j=hw)
                            # H_min has no printed uncertainty: 1e-6 relative.
                            self.assertTrue(_close(hl, ht), (eid, alpha, power, hl, ht))

    def test_score_agrees_with_unpatched_twin_when_scored_rows_carry_no_turn_h(self):
        # With the scored rows' h set to 0 the R6 term vanishes, so the lane and the
        # UNPATCHED twin must agree (fit still uses the real h).
        for regime, seed in _FIT_CASES[1::3]:
            world = _world(80_000 + seed, regime, 3, 10)
            specs = [s for v in world.values() for s in v[0]]
            ml = L.fit_energy_model(_rows(L, specs))
            mt = T.fit_energy_model(_rows(T, specs))
            for eid, (ep_specs, total, hw) in list(world.items())[:5]:
                zero = [s[:7] + (0.0,) for s in ep_specs]
                sl = L.residual_score(ml, _rows(L, zero), total, hw)
                st = T.residual_score(mt, _rows(T, zero), total, hw)
                self.assertTrue(_close(sl, st), (eid, sl, st))  # 1e-6 bar as above
                hl = L.min_detectable_hidden_decode_tokens(
                    ml, _rows(L, zero), alpha=0.05, power=0.8, measured_half_width_j=hw)
                ht = T.min_detectable_hidden_decode_tokens(
                    mt, _rows(T, zero), alpha=0.05, power=0.8, measured_half_width_j=hw)
                self.assertTrue(_close(hl, ht), (eid, hl, ht))

    def test_grouped_threshold_agrees_under_reconciled_r6(self):
        cases = [("nvml8b", 0, 5, 12), ("m3max", 1, 4, 15), ("boundary", 2, 6, 7), ("nvml8b", 3, 2, 30)]
        with mock.patch.object(T, "predict_episode", _twin_predict_lane_r6):
            for regime, seed, groups, per in cases:
                world = _world(90_000 + seed, regime, groups, per)
                bl, bt = _bench(L, world), _bench(T, world)
                twin_scores = T.held_out_benign_scores(bt)
                # Per-episode held-out scores first (localizes any disagreement).
                for eid, group, st in twin_scores:
                    others = [r for k, (rows, _, _) in bl.items() if rows[0].group != group for r in rows]
                    model = L.fit_energy_model(others)
                    rows, total, hw = bl[eid]
                    sl = L.residual_score(model, rows, total, hw)
                    self.assertTrue(_close(sl, st), (regime, eid, sl, st))  # 1e-6 bar
                for alpha in (0.01, 0.05, 0.1, 0.2):
                    tl = L.grouped_benign_threshold(bl, alpha=alpha)
                    tt = T.grouped_benign_threshold(bt, alpha=alpha)
                    # Threshold: no printed uncertainty, 1e-6 relative (abs below 1).
                    self.assertTrue(_close(tl, tt), (regime, groups * per, alpha, tl, tt))
                    self.assertEqual(getattr(tl, "flags", ()), ())


if __name__ == "__main__":
    unittest.main()
