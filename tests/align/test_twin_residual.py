"""Twin agreement for lane A7 residual: joulewise.align.energy_residual against
tests/align/twins/residual_twin.py, review round 3 (lane head 1c04d9061).

Written by the round-3 blind executing reviewer. Both implementations run on the same
seeded worlds built through the shared records (Episode, Turn, ToolCall): the lane reads
them through its own adapter turn_rows_from_episode, the twin through TurnRows built here
by hand from the same Turn fields. Nothing in either implementation is patched.

Worlds (every number below is an assumption for scale, not a measurement):
- h100_8b: an 8B model on a whole H100 under vLLM with prefix caching. 6-30 turns,
  first prefill 2.7k-4.3k (system prompt, tool schemas, task), later prefills the tool
  result (lognormal, median 400, 30-8000), decode lognormal median 180 (15-2000).
  Turn energy (2, 8e-4, 0.25, 2.5e-6, 1.5e-7) . x + N(0, 3^2) J; turn half-width
  sqrt(0.4^2 + (2% of the turn's energy)^2) J; whole-episode integral half-width 2 J.
- a100x4_70b: a 70B model, tensor parallel over four A100s, NVML 100 ms / 25 ms duty.
  Coefficients (20, 0.33, 33, 2e-4, 5e-6), extra sd 30 J, turn half-widths 5-20 J, episode
  half-width 52 J (the lane doc's NVML example), 4-20 turns, decode median 250.
- m3max_8b: the M3 Max instrument regime of the lane doc: (1, 4e-4, 0.35, 0.15/4096, 5e-8),
  extra sd 0.5 J, turn half-widths 0.3-1.2 J, episode half-width 1 J (attribution limit).
- jetson_3b: a 3B model on a Jetson AGX Orin, INA3221 rails: (0.5, 0.05, 0.6, 2.2e-5,
  1.8e-6), extra sd 1 J, turn half-widths 0.5-3 J, episode half-width 2 J.
- noisy_turns: the h100_8b costs with extra sd 0.3 J and turn half-widths 5-15 J: the
  extra variance is a small fraction of the measurement variance, which stresses the
  precision of sigma2 (the lane's moment bar is stated relative to n - p, the twin's
  relative to sigma2 + mean h^2).
- boundary: no extra variance at all (sigma2 = 0), so the moment estimate sits on or near
  its truncation at zero; turn half-widths 0.5-2 J, episode half-width 1 J.
- longctx: a long-context agent resuming a 20k-60k token transcript (contexts reach about
  150k), 4-15 turns, extra sd 6 J, turn half-widths 1-8 J, episode half-width 3 J.
Context grows by each turn's prefill plus visible decode; a hidden scratchpad is not
re-fed (the shared record's convention). The measured total is the sum of TRUE turn
energies plus N(0, episode half-width^2): the separate whole-episode integral of the lead's
RES-R1-02 ruling. Turn energies are the true energy plus N(0, h_i^2) (fit inputs only).

Bars (set by the orchestrator; not chosen here):
- an output with a printed uncertainty: within 1% of the smaller of the two printed
  uncertainties (a coefficient against its standard error; a predicted mean against its
  predicted sd);
- otherwise 1e-6 relative, or 1e-6 absolute in the output's unit when the value is below
  1 (sigma2 in J^2, standard errors, correlations, sd, scores, thresholds, benign mean and
  sd, H_min and H_cal in tokens). Both bars lie far above 1e6 * float64 epsilon (2.2e-10).
- integer counts (n_turns, n_scores), token fields and flag membership: exact.
No function compared here draws random numbers, so no Monte Carlo bar applies.

Readings the two builders resolve differently, so they are not compared (each reported):
- power <= alpha in min_detectable_hidden_decode_tokens: lane 0 with a flag, twin the raw
  negative formula. Only power > alpha is compared.
- invalid inputs, rank-deficient designs, mixed-group or empty episodes: the lane excludes
  and flags (lead's RES-R1-01/RES-R1-03 rulings), the twin raises. Only clean full-rank
  worlds are compared.
- the quantile rank: lane ceil((1 - alpha) * m) in binary floating point, twin in exact
  decimal arithmetic (open nit RES-R1-06). Only alphas for which they agree at every m
  up to 5000 (0.01, 0.025, 0.05, 0.1, 0.2) are compared.

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
from joulewise.align.records import Episode, ToolCall, Turn
from tests.align.twins import residual_twin as T

_NS = 1_000_000_000
_DEPARTURE = "benign_score_calibration_departure"
_SAMPLE_MAX = "quantile_at_sample_max"
_NORMAL = NormalDist()

# name: (coef, extra sd J, turn half-width rule, episode half-width J, turn range,
#        decode median tokens, prefill tok/s, decode tok/s)
_REGIMES = {
    "h100_8b": ((2.0, 8e-4, 0.25, 2.5e-6, 1.5e-7), 3.0, ("rel", 0.4, 0.02), 2.0, (6, 30), 180, 8000, 90),
    "a100x4_70b": ((20.0, 0.33, 33.0, 2e-4, 5e-6), 30.0, ("uniform", 5.0, 20.0), 52.0, (4, 20), 250, 3000, 30),
    "m3max_8b": ((1.0, 4e-4, 0.35, 0.15 / 4096, 5e-8), 0.5, ("uniform", 0.3, 1.2), 1.0, (6, 30), 180, 600, 40),
    "jetson_3b": ((0.5, 0.05, 0.6, 2.2e-5, 1.8e-6), 1.0, ("uniform", 0.5, 3.0), 2.0, (6, 24), 150, 500, 40),
    "noisy_turns": ((2.0, 8e-4, 0.25, 2.5e-6, 1.5e-7), 0.3, ("uniform", 5.0, 15.0), 2.0, (6, 30), 180, 8000, 90),
    "boundary": ((5.0, 0.005, 0.12, 1e-5, 4e-6), 0.0, ("uniform", 0.5, 2.0), 1.0, (6, 30), 180, 2000, 80),
    "longctx": ((4.0, 9e-4, 0.30, 2e-6, 6e-8), 6.0, ("uniform", 1.0, 8.0), 3.0, (4, 15), 300, 8000, 60),
}
# Starting cached context (tokens) where it is not 0: a long-context agent resumes a
# 20k-60k token transcript and reaches about 150k.
_START_CTX = {"longctx": (20_000, 60_000)}


def _true_mean(coef, ctx, pf, dc):
    return math.fsum(a * b for a, b in zip(coef, (1, pf, dc, ctx * dc, ctx * pf)))


def _episode(rng, regime, eid, pair, *, hidden=0, hidden_costs=True, unowned_j=0.0):
    """(Episode, {turn index: (energy J, half-width J)}, measured total J, episode half-width J).

    hidden: hidden decode tokens added to every turn (sabotage; counted in decode_tokens and
    hidden_tokens as the shared record defines). unowned_j: energy per tool call added to the
    total only (no turn owns it), an assumption for scale.
    """
    coef, sigma, hrule, hw_ep, (tlo, thi), dmed, pf_rate, dc_rate = _REGIMES[regime]
    n = rng.randint(tlo, thi)
    ctx = rng.randint(*_START_CTX[regime]) if regime in _START_CTX else 0
    now, turns, energy, true_sum = 0, [], {}, 0.0
    for k in range(n):
        pf = (rng.randint(2500, 3500) + rng.randint(200, 800) if k == 0
              else 20 + min(8000, max(30, int(rng.lognormvariate(math.log(400), 1.1)))))
        dc = min(2000, max(15, int(rng.lognormvariate(math.log(dmed), 0.9))))
        first = now + math.ceil(pf / pf_rate * _NS)
        end = first + math.ceil((dc + hidden) / dc_rate * _NS)
        wait = int(rng.uniform(0.2, 3.0) * _NS)
        calls = (ToolCall("tool", end, end + wait, 60, 400),) if k < n - 1 else ()
        turns.append(Turn(k, now, end, ctx, pf, dc + hidden, hidden_tokens=hidden,
                          first_token_ns=first, tool_calls=calls))
        mu = _true_mean(coef, ctx, pf, dc)
        e_true = mu + rng.gauss(0, sigma)
        if hrule[0] == "rel":
            h = math.sqrt(hrule[1] ** 2 + (hrule[2] * max(mu, 0.0)) ** 2)
        else:
            h = rng.uniform(hrule[1], hrule[2])
        hid_j = hidden * (coef[2] + coef[3] * ctx) if hidden_costs else 0.0
        energy[k] = (e_true + hid_j + rng.gauss(0, h), h)
        true_sum += e_true + hid_j
        now = end + (wait if calls else 0)
        ctx += pf + dc
    ep = Episode(eid, pair, "sabotage" if hidden else "benign", "synthetic", "mock/vllm", 0,
                 "host", 0, max(now, 1), tuple(turns))
    total = true_sum + unowned_j * (n - 1) + rng.gauss(0, hw_ep)
    return ep, energy, total, hw_ep


def _world(seed, regime, groups, per, **kwargs):
    rng = random.Random(seed)
    return {f"{regime}-{seed}-{g}-{i}": _episode(rng, regime, f"{regime}-{seed}-{g}-{i}",
                                                  f"shade/pair-{g:02d}", **kwargs)
            for g in range(groups) for i in range(per)}


def _twin_rows(ep, energy, *, counts_logged=False):
    return [T.TurnRow(ep.episode_id, ep.task_pair, t.context_tokens, t.prefill_tokens,
                      t.decode_tokens - (0 if counts_logged else t.hidden_tokens),
                      (t.end_ns - t.start_ns) / _NS, *energy[t.index])
            for t in ep.logged_turns()]


def _benches(world, **kwargs):
    lane = {eid: (L.turn_rows_from_episode(ep, en, hidden_token_counts_logged=kwargs.get("counts_logged", False)),
                  tot, hw) for eid, (ep, en, tot, hw) in world.items()}
    twin = {eid: (_twin_rows(ep, en, **kwargs), tot, hw) for eid, (ep, en, tot, hw) in world.items()}
    return lane, twin


def _all(bench):
    return [r for rows, _, _ in bench.values() for r in rows]


def _close(a, b):
    # Orchestrator bar, no printed uncertainty: 1e-6 relative, or 1e-6 absolute in the
    # output's unit below 1. Far above 1e6 * float64 epsilon (2.2e-10).
    if math.isinf(a) or math.isinf(b):
        return a == b
    scale = max(abs(a), abs(b))
    return abs(a - b) <= (1e-6 * scale if scale >= 1 else 1e-6)


def _check_fit(test, ml, mt, label, worst):
    test.assertEqual(ml.n_turns, mt.n_turns, label)  # integer count: exact
    test.assertTrue(_close(ml.sigma2_per_turn, mt.sigma2_per_turn), (label, ml.sigma2_per_turn, mt.sigma2_per_turn))
    worst["sigma2 rel"] = max(worst["sigma2 rel"], abs(ml.sigma2_per_turn - mt.sigma2_per_turn)
                              / max(mt.sigma2_per_turn, 1.0))
    for j in range(5):
        se_l, se_t = math.sqrt(ml.cov[j][j]), math.sqrt(mt.cov[j][j])
        # A coefficient's printed uncertainty is its SE: 1% of the smaller SE.
        d = abs(ml.coef[j] - mt.coef[j]) / min(se_l, se_t)
        worst["coef/SE"] = max(worst["coef/SE"], d)
        test.assertLessEqual(d, 0.01, (label, j, ml.coef[j], mt.coef[j]))
        test.assertTrue(_close(se_l, se_t), (label, j, se_l, se_t))  # an SE: 1e-6 bar
        for k in range(5):
            # Correlations are unitless and at most 1 in size: 1e-6 absolute.
            rl = ml.cov[j][k] / (se_l * math.sqrt(ml.cov[k][k]))
            rt = mt.cov[j][k] / (se_t * math.sqrt(mt.cov[k][k]))
            worst["corr abs"] = max(worst["corr abs"], abs(rl - rt))
            test.assertLessEqual(abs(rl - rt), 1e-6, (label, j, k, rl, rt))


@unittest.skipUnless(_HAVE_LANE, "lane module joulewise.align.energy_residual absent (twin branch)")
class TestTwinResidualAgreementRound3(unittest.TestCase):
    def test_fit_predict_score_and_power_agree_across_regimes(self):
        worst = {"coef/SE": 0.0, "sigma2 rel": 0.0, "corr abs": 0.0, "mean/sd": 0.0, "H rel": 0.0}
        for regime in _REGIMES:
            for seed in range(3):
                world = _world(310_000 + seed, regime, 4, 8)
                bl, bt = _benches(world)
                ml, mt = L.fit_energy_model(_all(bl)), T.fit_energy_model(_all(bt))
                label = f"{regime} seed {seed} n={ml.n_turns}"
                self.assertEqual(ml.flags, (), label)  # clean full-rank world: no flags
                _check_fit(self, ml, mt, label, worst)
                for eid in list(world)[:5]:
                    rl, total, hw = bl[eid]
                    rt = bt[eid][0]
                    mean_l, sd_l = L.predict_episode(ml, rl)
                    mean_t, sd_t = T.predict_episode(mt, rt)
                    # Predicted mean: its printed uncertainty is the predicted sd; 1% of the smaller.
                    worst["mean/sd"] = max(worst["mean/sd"], abs(mean_l - mean_t) / min(sd_l, sd_t))
                    self.assertLessEqual(abs(mean_l - mean_t), 0.01 * min(sd_l, sd_t), (label, eid))
                    self.assertTrue(_close(sd_l, sd_t), (label, eid, sd_l, sd_t))  # sd: 1e-6 bar
                    # Same (lane) model through both predictors isolates predict from fit.
                    mean_x, sd_x = T.predict_episode(ml, rt)
                    self.assertTrue(_close(mean_l, mean_x) and _close(sd_l, sd_x), (label, eid))
                    for shift in (0.0, 3.0 * sd_l, 30.0 * sd_l):  # J of unexplained energy
                        self.assertTrue(_close(L.residual_score(ml, rl, total + shift, hw),
                                               T.residual_score(mt, rt, total + shift, hw)), (label, eid, shift))
                    for alpha in (0.01, 0.05, 0.1):
                        for power in (0.5, 0.8, 0.95):
                            hl = L.min_detectable_hidden_decode_tokens(
                                ml, rl, alpha=alpha, power=power, measured_half_width_j=hw)
                            ht = T.min_detectable_hidden_decode_tokens(
                                mt, rt, alpha=alpha, power=power, measured_half_width_j=hw)
                            worst["H rel"] = max(worst["H rel"], abs(hl - ht) / ht)
                            self.assertTrue(_close(hl, ht), (label, eid, alpha, power, hl, ht))
        print("\nround-3 fit/predict/score/H_min agreement, worst:", worst)

    def test_sabotage_and_deleted_turn_scores_agree(self):
        # Hidden decode (energy-bearing and zero-energy) and deleted turns go through the
        # lane's adapter; the twin gets hand-built rows of the same logged turns.
        for regime in ("h100_8b", "a100x4_70b", "m3max_8b"):
            benign = _world(320_000, regime, 4, 8)
            bl, bt = _benches(benign)
            ml, mt = L.fit_energy_model(_all(bl)), T.fit_energy_model(_all(bt))
            rng = random.Random(320_001)
            for i in range(6):
                for hidden, costs in ((64, True), (64, False), (0, True)):
                    ep, en, tot, hw = _episode(rng, regime, f"s{i}", "shade/pair-99",
                                               hidden=hidden, hidden_costs=costs)
                    rl = L.turn_rows_from_episode(ep, en)
                    rt = _twin_rows(ep, en)
                    # Token fields copied from integer Turn fields: exact identity.
                    self.assertEqual([(r.context_tokens, r.prefill_tokens, r.decode_tokens) for r in rl],
                                     [(r.context_tokens, r.prefill_tokens, r.decode_tokens) for r in rt])
                    self.assertTrue(_close(L.residual_score(ml, rl, tot, hw),
                                           T.residual_score(mt, rt, tot, hw)), (regime, i, hidden, costs))
                    for deleted in (1, 3):
                        if deleted >= len(ep.turns):
                            continue
                        tampered = replace(ep, turns=tuple(replace(t, logged=t.index >= deleted)
                                                           for t in ep.turns))
                        dl = L.turn_rows_from_episode(tampered, en)
                        dt = _twin_rows(tampered, en)
                        self.assertEqual(len(dl), len(ep.turns) - deleted)  # integer count: exact
                        self.assertTrue(_close(L.residual_score(ml, dl, tot, hw),
                                               T.residual_score(mt, dt, tot, hw)), (regime, i, deleted))

    def test_heldout_scores_threshold_attributes_flags_and_calibrated_power_agree(self):
        # (regime, seed, groups, per pair, unowned J per tool call). m covers integer
        # (1 - alpha) * m ranks (m = 20, 60, 100, 120), the sample-maximum edge m < 1/alpha
        # for alpha 0.01 and 0.025, a SHADE-like 17 pairs, and unowned energy (assumption
        # for scale, several J per call against D of a few to tens of J), which moves the
        # held-out mean by many standard errors.
        cases = [("h100_8b", 0, 17, 6, 0.0), ("m3max_8b", 1, 5, 12, 0.0), ("jetson_3b", 2, 6, 10, 0.0),
                 ("a100x4_70b", 3, 4, 5, 0.0), ("noisy_turns", 4, 6, 20, 0.0), ("h100_8b", 5, 6, 20, 3.0),
                 ("m3max_8b", 6, 5, 12, 2.0), ("boundary", 7, 6, 10, 0.0), ("longctx", 8, 4, 10, 0.0)]
        flag_states, worst_h = {True: 0, False: 0}, 0.0
        for regime, seed, groups, per, unowned in cases:
            world = _world(330_000 + seed, regime, groups, per, unowned_j=unowned)
            bl, bt = _benches(world)
            twin_scores = T.held_out_benign_scores(bt)
            m = groups * per
            self.assertEqual(len(twin_scores), m)  # integer count: exact
            fold_models = {}
            for eid, group, st in twin_scores:
                if group not in fold_models:
                    fold_models[group] = L.fit_energy_model(
                        [r for rows, _, _ in bl.values() if rows[0].group != group for r in rows])
                rows, total, hw = bl[eid]
                # Per-episode held-out scores first: localizes any threshold disagreement.
                self.assertTrue(_close(L.residual_score(fold_models[group], rows, total, hw), st), (regime, eid))
            values = [s for _, _, s in twin_scores]
            mu_t, sd_t = fmean(values), stdev(values)
            # The lead's departure rule, evaluated on the twin's scores.
            departs = abs(mu_t) > 4 / math.sqrt(m) or abs(sd_t - 1) > 4 / math.sqrt(2 * (m - 1))
            flag_states[departs] += 1
            full_l, full_t = L.fit_energy_model(_all(bl)), T.fit_energy_model(_all(bt))
            for alpha in (0.01, 0.025, 0.05, 0.1, 0.2):
                label = (regime, m, unowned, alpha)
                tl = L.grouped_benign_threshold(bl, alpha=alpha)
                tt = T.grouped_benign_threshold(bt, alpha=alpha)
                self.assertTrue(_close(tl, tt), (label, tl, tt))  # threshold: 1e-6 bar
                self.assertEqual(tl.n_scores, m, label)  # integer count: exact
                self.assertTrue(_close(tl.benign_mean, mu_t), (label, tl.benign_mean, mu_t))  # 1e-6 bar
                self.assertTrue(_close(tl.benign_sd, sd_t), (label, tl.benign_sd, sd_t))  # 1e-6 bar
                expected = {_DEPARTURE} if departs else set()
                if math.ceil((1 - Fraction(repr(alpha))) * m) == m:
                    expected.add(_SAMPLE_MAX)
                self.assertEqual(set(tl.flags), expected, label)  # flag membership: exact
                for eid in list(world)[:3]:
                    rows_l, _, hw = bl[eid]
                    rows_t = bt[eid][0]
                    _, sd_pred = T.predict_episode(full_t, rows_t)
                    d = math.sqrt(sd_pred ** 2 + hw ** 2)
                    e = full_t.coef[2] + full_t.coef[3] * fmean(r.context_tokens for r in rows_t)
                    for power in (0.5, 0.8, 0.95):
                        # The lead's ruled formula, from twin numbers only (no twin function).
                        ht = max(0.0, (tt - mu_t + _NORMAL.inv_cdf(power) * sd_t) * d / e)
                        hl = L.calibrated_min_detectable_hidden_decode_tokens(
                            full_l, rows_l, threshold=tl, power=power, measured_half_width_j=hw)
                        hp = L.calibrated_min_detectable_hidden_decode_tokens(
                            full_l, rows_l, threshold=float(tl), power=power, measured_half_width_j=hw,
                            benign_mean=float(tl.benign_mean), benign_sd=float(tl.benign_sd))
                        self.assertEqual(hl, hp)  # identical code on identical numbers: bit identity
                        self.assertTrue(_close(hl, ht), (label, eid, power, hl, ht))  # 1e-6 bar
                        if ht >= 1:
                            worst_h = max(worst_h, abs(hl - ht) / ht)
        # Both flag states exercised (integer counts: exact).
        self.assertGreaterEqual(flag_states[True], 2, flag_states)
        self.assertGreaterEqual(flag_states[False], 3, flag_states)
        print("\nround-3 threshold/H_cal agreement: departure states", flag_states, "worst H_cal rel", worst_h)

    def test_reasoning_count_readings_agree_with_hand_built_twin_rows(self):
        # A benign reasoning model: every turn carries a stripped scratchpad (lognormal,
        # median 300 tokens) whose energy is in the turn and the total. Both readings of
        # hidden_tokens go through the lane adapter and through hand-built twin rows.
        rng = random.Random(340_000)
        world = {}
        for g in range(5):
            for i in range(8):
                eid = f"r{g}-{i}"
                world[eid] = _episode(rng, "h100_8b", eid, f"shade/pair-{g:02d}",
                                      hidden=int(rng.lognormvariate(math.log(300), 0.5)))
        for logged in (False, True):
            bl, bt = _benches(world, counts_logged=logged)
            for eid in world:
                # Integer token fields and identical copied floats: exact field identity.
                self.assertEqual([tuple(vars(r).values()) for r in bl[eid][0]],
                                 [tuple(vars(r).values()) for r in bt[eid][0]], (logged, eid))
            worst = {"coef/SE": 0.0, "sigma2 rel": 0.0, "corr abs": 0.0}
            _check_fit(self, L.fit_energy_model(_all(bl)), T.fit_energy_model(_all(bt)), logged, worst)
            self.assertTrue(_close(L.grouped_benign_threshold(bl, alpha=0.05),
                                   T.grouped_benign_threshold(bt, alpha=0.05)), logged)  # 1e-6 bar

    def test_non_int_token_representations_agree_with_plain_int_twin(self):
        class IndexCount:  # stdlib stand-in for numpy.int64: not an int, has __index__
            def __init__(self, value):
                self.value = value

            def __index__(self):
                return self.value

        converters = [float, IndexCount]
        if importlib.util.find_spec("numpy"):
            import numpy as np
            converters += [np.int64, np.uint32]
        world = _world(350_000, "h100_8b", 4, 8)
        bl, bt = _benches(world)
        mt = T.fit_energy_model(_all(bt))
        tt = T.grouped_benign_threshold(bt, alpha=0.05)
        for convert in converters:
            conv = {eid: ([replace(r, context_tokens=convert(r.context_tokens),
                                   prefill_tokens=convert(r.prefill_tokens),
                                   decode_tokens=convert(r.decode_tokens)) for r in rows], tot, hw)
                    for eid, (rows, tot, hw) in bl.items()}
            ml = L.fit_energy_model(_all(conv))
            label = getattr(convert, "__name__", str(convert))
            self.assertEqual(ml.flags, (), label)
            worst = {"coef/SE": 0.0, "sigma2 rel": 0.0, "corr abs": 0.0}
            _check_fit(self, ml, mt, label, worst)
            self.assertTrue(_close(L.grouped_benign_threshold(conv, alpha=0.05), tt), label)  # 1e-6 bar


if __name__ == "__main__":
    unittest.main()
