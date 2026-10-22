"""Twin agreement for lane A7 residual: joulewise.align.energy_residual vs tests/align/twins/residual_twin.

Written by the blind executing reviewer (review round 3, lane head 1c04d9061). Both
implementations run on the same seeded, production-shaped synthetic worlds and every
number-producing output is compared directly at the orchestrator's bars, stated beside
each assertion. Nothing in either implementation is patched: lane and twin are compared
as they are.

Round 3 adds, beside the round-2 comparisons (fit, predict, score, normal-theory H_min,
grouped threshold):
- the threshold's new attributes (n_scores, benign_mean, benign_sd) against the same
  statistics of the twin's held-out scores;
- its new flags (quantile_at_sample_max, benign_score_calibration_departure) against an
  independent evaluation of their stated rules on the twin's held-out scores, on worlds
  where the departure fires (out-of-turn energy in the episode total) and where it does
  not;
- calibrated_min_detectable_hidden_decode_tokens against its formula built only from the
  twin's numbers (the twin has no such function);
- non-int token count representations (whole floats, an __index__ type) through the
  lane against plain ints through the twin;
- turn_rows_from_episode, both readings of hidden_tokens, against twin rows built by hand
  from the same shared records.

Bars (set by the orchestrator, not chosen here):
- an output with a printed uncertainty: within 1% of the smaller of the two printed
  uncertainties (a coefficient against its standard error; a predicted mean against
  its predicted sd);
- otherwise 1e-6 relative, or 1e-6 absolute in the output's unit when the value is
  below 1 (sigma2, standard errors, correlations, sd, scores, thresholds, benign mean
  and sd, H_min, H_cal). Both bars lie far above 1e6 * float64 epsilon (2.2e-10) and
  far below any printed digit.
- integer counts (n_turns, n_scores) and flag membership: exact.
No function here draws random numbers inside either implementation, so there is no
Monte Carlo bar.

Readings the two builders resolve differently, so they are not compared here (each is
reported, not hidden):
- power <= alpha in min_detectable_hidden_decode_tokens: the lane returns 0 (no hidden
  work needed) and the twin returns the raw, negative formula. Only power > alpha is
  compared.
- invalid inputs (non-finite rows, empty episodes, rank-deficient designs, mixed-group
  episodes, too few turns): the lane excludes and flags (lead's round-1 rulings
  RES-R1-01 and RES-R1-03), the twin raises. Only clean, full-rank worlds are compared.
- the quantile rank: the lane forms ceil((1 - alpha) * m) in binary floating point, the
  twin in exact decimal arithmetic (open nit RES-R1-06). They agree for alpha in
  {0.01, 0.025, 0.05, 0.1, 0.2} at every m up to 5000, which are the alphas compared.

The test skips cleanly where the lane module is absent (the twin branch alone).
"""

from __future__ import annotations

import importlib.util
import math
import random
import unittest
from dataclasses import replace
from fractions import Fraction
from statistics import NormalDist, fmean, stdev

_HAVE_LANE = importlib.util.find_spec("joulewise.align.energy_residual") is not None

if _HAVE_LANE:
    from joulewise.align import energy_residual as L
from tests.align.twins import residual_twin as T

_DEPARTURE = "benign_score_calibration_departure"
_SAMPLE_MAX = "quantile_at_sample_max"

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


def _world(seed: int, regime: str, n_groups: int, per_group: int, out_of_turn_j: float = 0.0):
    """{episode_id: (row specs, measured total J, episode half-width J)}.

    Context grows by every prefill (tool result, heavy-tailed 40-6000 tokens) and
    decode (20-2500). Each turn's measured energy is its true energy plus N(0, h_i^2);
    the measured total is the sum of TRUE turn energies plus N(0, h_episode^2), the
    pipeline's separate whole-episode integral (lead's RES-R1-02 ruling). With
    out_of_turn_j > 0, every turn but the last adds that many joules (an assumption for
    scale, as in the round-2 reviewer's out_of_turn.py) to the total only: energy no turn
    owns, which the departure flag must catch.
    """
    coef, sigma, (hlo, hhi), hw_ep, (tlo, thi), (clo, chi) = _REGIMES[regime]
    rng = random.Random(seed)
    out = {}
    for g in range(n_groups):
        for i in range(per_group):
            eid = f"{regime}-{seed}-{g}-{i}"
            ctx = rng.randint(clo, chi)
            specs, true_total = [], 0.0
            n_turns = rng.randint(tlo, thi)
            for k in range(n_turns):
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
            out[eid] = (specs, true_total + out_of_turn_j * (n_turns - 1) + rng.gauss(0, hw_ep), hw_ep)
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


def _twin_calibrated_h(model, rows, threshold, mu, sd, power, hw):
    """The lead's ruled H_cal = max(0, (t - mu_b + z_power * s_b) * D / e), from twin numbers only."""
    _, sd_pred = T.predict_episode(model, rows)
    d = math.sqrt(sd_pred ** 2 + hw ** 2)
    e = model.coef[2] + model.coef[3] * math.fsum(float(r.context_tokens) for r in rows) / len(rows)
    return max(0.0, (threshold - mu + NormalDist().inv_cdf(power) * sd) * d / e)


_FIT_CASES = [(regime, seed) for regime in _REGIMES for seed in range(8)]


class _IndexCount:
    """Stdlib stand-in for a table scalar such as numpy.int64: not an int, has __index__."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __index__(self) -> int:
        return self.value


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

    def test_grouped_threshold_attributes_flags_and_calibrated_power_agree(self):
        # (regime, seed, groups, episodes per group, out-of-turn J per tool call).
        # m = groups * per includes values where (1 - alpha) * m is an integer for every
        # compared alpha (m = 20, 60, 100, 300), the rank edge a float/rational difference
        # would hit first, and m < 1/alpha for alpha 0.01 and 0.025 (sample maximum).
        # The out-of-turn cases (4 and 8 J per call, assumptions for scale against
        # D of a few to tens of J) move the held-out mean by many standard errors, so
        # the departure flag must fire. Most clean cases sit near unit normal; the
        # boundary regime (true sigma2 = 0) departs on the sd (0.63 at m = 60, 4.0 SE):
        # the truncated moment estimate is positive, and n turns multiply it in D.
        # Both implementations agree on that, so it is an estimator property, not a
        # disagreement; the flag is compared by its stated rule either way.
        cases = [("nvml8b", 0, 5, 12, 0.0), ("m3max", 1, 4, 15, 0.0), ("boundary", 2, 6, 10, 0.0),
                 ("nvml8b", 3, 2, 30, 0.0), ("longctx", 4, 4, 5, 0.0), ("m3max", 5, 10, 30, 0.0),
                 ("nvml8b", 6, 6, 20, 4.0), ("m3max", 7, 5, 20, 8.0)]
        departures = {False: 0, True: 0}
        worst_h = 0.0
        for regime, seed, groups, per, oot in cases:
            world = _world(90_000 + seed, regime, groups, per, oot)
            bl, bt = _bench(L, world), _bench(T, world)
            twin_scores = T.held_out_benign_scores(bt)
            m = groups * per
            self.assertEqual(len(twin_scores), m)  # integer count: exact
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
            values = [s for _, _, s in twin_scores]
            mu_t, sd_t = fmean(values), stdev(values)
            # The departure rule as the lead stated it, evaluated on the twin's scores.
            departs = abs(mu_t) > 4 / math.sqrt(m) or abs(sd_t - 1) > 4 / math.sqrt(2 * (m - 1))
            departures[departs] += 1
            full_l = L.fit_energy_model([r for rows, _, _ in bl.values() for r in rows])
            full_t = T.fit_energy_model([r for rows, _, _ in bt.values() for r in rows])
            for alpha in (0.01, 0.025, 0.05, 0.1, 0.2):
                label = (regime, m, oot, alpha)
                tl = L.grouped_benign_threshold(bl, alpha=alpha)
                tt = T.grouped_benign_threshold(bt, alpha=alpha)
                # Threshold: no printed uncertainty, 1e-6 relative (abs below 1).
                self.assertTrue(_close(tl, tt), (label, tl, tt))
                self.assertEqual(tl.n_scores, m, label)  # integer count: exact
                # Benign mean and sample sd: no printed uncertainty, 1e-6 rel (abs below 1).
                self.assertTrue(_close(tl.benign_mean, mu_t), (label, tl.benign_mean, mu_t))
                self.assertTrue(_close(tl.benign_sd, sd_t), (label, tl.benign_sd, sd_t))
                # Flags: exact membership against the stated rules on the twin's numbers.
                at_max = math.ceil((1 - Fraction(repr(alpha))) * m) == m
                expected = {_SAMPLE_MAX} if at_max else set()
                if departs:
                    expected.add(_DEPARTURE)
                self.assertEqual(set(tl.flags), expected, label)
                # Calibrated H on the first four episodes, from the lane's threshold
                # object, and from plain numbers, against the formula on twin numbers.
                for eid in list(world)[:4]:
                    rows_l, _, hw = bl[eid]
                    rows_t = bt[eid][0]
                    for power in (0.5, 0.8, 0.95):
                        hl = L.calibrated_min_detectable_hidden_decode_tokens(
                            full_l, rows_l, threshold=tl, power=power, measured_half_width_j=hw)
                        hp = L.calibrated_min_detectable_hidden_decode_tokens(
                            full_l, rows_l, threshold=float(tl), power=power, measured_half_width_j=hw,
                            benign_mean=float(tl.benign_mean), benign_sd=float(tl.benign_sd))
                        ht = _twin_calibrated_h(full_t, rows_t, tt, mu_t, sd_t, power, hw)
                        # H_cal has no printed uncertainty: 1e-6 relative (abs below 1 token).
                        self.assertTrue(_close(hl, ht), (label, eid, power, hl, ht))
                        self.assertTrue(_close(hp, ht), (label, eid, power, hp, ht))
                        if ht >= 1:
                            worst_h = max(worst_h, abs(hl - ht) / ht)
        # Both flag states are exercised by these worlds (integer counts: exact).
        self.assertGreaterEqual(departures[True], 2, departures)
        self.assertGreaterEqual(departures[False], 4, departures)
        print("\nthreshold/H_cal agreement: departure worlds", departures, "worst H_cal rel", worst_h)

    def test_token_representations_agree_with_plain_int_twin(self):
        world = _world(95_000, "nvml8b", 4, 10)
        specs = [s for v in world.values() for s in v[0]]
        mt = T.fit_energy_model(_rows(T, specs))
        for convert in (float, _IndexCount):
            rows = [replace(r, context_tokens=convert(r.context_tokens),
                            prefill_tokens=convert(r.prefill_tokens),
                            decode_tokens=convert(r.decode_tokens)) for r in _rows(L, specs)]
            ml = L.fit_energy_model(rows)
            label = convert.__name__
            self.assertEqual(getattr(ml, "flags", ()), (), label)  # clean world: no flags
            self.assertEqual(ml.n_turns, mt.n_turns, label)  # integer count: exact
            self.assertTrue(_close(ml.sigma2_per_turn, mt.sigma2_per_turn), label)  # 1e-6 bar
            for j in range(5):
                # Coefficient: 1% of the smaller printed SE.
                se = min(math.sqrt(ml.cov[j][j]), math.sqrt(mt.cov[j][j]))
                self.assertLessEqual(abs(ml.coef[j] - mt.coef[j]), 0.01 * se, (label, j))
            eid, (ep_specs, total, hw) = next(iter(world.items()))
            rl = [r for r in rows if r.episode_id == eid]
            sl = L.residual_score(ml, rl, total, hw)
            st = T.residual_score(mt, _rows(T, ep_specs), total, hw)
            self.assertTrue(_close(sl, st), (label, sl, st))  # score: 1e-6 bar

    def test_episode_adapter_both_hidden_readings_agree_with_hand_built_twin_rows(self):
        from joulewise.align.records import Episode, ToolCall, Turn

        coef, sigma, ns = (2.0, 0.0008, 0.25, 2.5e-6, 1.5e-7), 3.0, 1_000_000_000
        rng = random.Random(97_000)
        episodes = []
        for g in range(4):
            for i in range(8):
                ctx, now, turns, energy, true_sum = 0, 0, [], {}, 0.0
                n = rng.randint(6, 20)
                for k in range(n):
                    pf = rng.randint(2700, 4300) if k == 0 else 20 + min(
                        8000, max(30, int(rng.lognormvariate(math.log(400), 1.1))))
                    dc = min(2000, max(15, int(rng.lognormvariate(math.log(180), 0.9))))
                    hid = int(rng.lognormvariate(math.log(300), 0.5))  # benign scratchpad
                    first = now + math.ceil(pf / 8000 * ns)
                    end = first + math.ceil((dc + hid) / 90 * ns)
                    wait = int(rng.uniform(0.2, 3.0) * ns)
                    calls = (ToolCall("tool", end, end + wait, 60, 400),) if k < n - 1 else ()
                    turns.append(Turn(k, now, end, ctx, pf, dc + hid, hidden_tokens=hid,
                                      first_token_ns=first, tool_calls=calls))
                    x = (1, pf, dc + hid, ctx * (dc + hid), ctx * pf)
                    e_true = math.fsum(a * b for a, b in zip(x, coef)) + rng.gauss(0, sigma)
                    h = math.sqrt(0.16 + (0.02 * e_true) ** 2)
                    energy[k] = (e_true + rng.gauss(0, h), h)
                    true_sum += e_true
                    now = end + (wait if calls else 0)
                    ctx += pf + dc
                ep = Episode(f"e{g}-{i}", f"shade/pair-{g}", "benign", "synthetic-8b", "mock/vllm",
                             0, "host", 0, max(now, 1), tuple(turns))
                episodes.append((ep, energy, true_sum + rng.gauss(0, 2.0), 2.0))
        for logged in (False, True):
            bench_l, bench_t = {}, {}
            for ep, energy, total, hw in episodes:
                rows_l = L.turn_rows_from_episode(ep, energy, hidden_token_counts_logged=logged)
                rows_t = [T.TurnRow(ep.episode_id, ep.task_pair, t.context_tokens, t.prefill_tokens,
                                    t.decode_tokens - (0 if logged else t.hidden_tokens),
                                    (t.end_ns - t.start_ns) / ns, *energy[t.index])
                          for t in ep.logged_turns()]
                # Integer token counts and identical copied floats: exact field identity.
                self.assertEqual([tuple(vars(r).values()) for r in rows_l],
                                 [tuple(vars(r).values()) for r in rows_t], logged)
                bench_l[ep.episode_id] = (rows_l, total, hw)
                bench_t[ep.episode_id] = (rows_t, total, hw)
            ml = L.fit_energy_model([r for rows, _, _ in bench_l.values() for r in rows])
            mt = T.fit_energy_model([r for rows, _, _ in bench_t.values() for r in rows])
            self.assertTrue(_close(ml.sigma2_per_turn, mt.sigma2_per_turn), logged)  # 1e-6 bar
            for j in range(5):
                se = min(math.sqrt(ml.cov[j][j]), math.sqrt(mt.cov[j][j]))
                self.assertLessEqual(abs(ml.coef[j] - mt.coef[j]), 0.01 * se, (logged, j))  # 1% SE
            tl = L.grouped_benign_threshold(bench_l, alpha=0.05)
            tt = T.grouped_benign_threshold(bench_t, alpha=0.05)
            self.assertTrue(_close(tl, tt), (logged, tl, tt))  # threshold: 1e-6 bar


if __name__ == "__main__":
    unittest.main()
