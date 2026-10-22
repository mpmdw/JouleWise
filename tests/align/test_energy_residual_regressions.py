"""Record-path calibration, representation and separate-integral regressions."""

from __future__ import annotations

import importlib.util
import math
import random
import unittest
from dataclasses import asdict, replace
from statistics import NormalDist, fmean, stdev

from joulewise.align.energy_residual import (
    TurnRow, calibrated_min_detectable_hidden_decode_tokens,
    design_row, fit_energy_model, grouped_benign_threshold,
    min_detectable_hidden_decode_tokens, predict_episode, residual_score,
    turn_rows_from_episode,
)
from joulewise.align.records import Episode, ToolCall, Turn

_GPU_COEF = (3.0, .0012, .22, 3e-6, 2e-7)
_M3_COEF = (1.0, .0004, .35, .15/4096, 5e-8)


def _sensor_world(seed, groups, per_group, *, coef=_GPU_COEF,
                  sigma=2.5, turn_h=(.2, 2.5), episode_h=1.5):
    """Production-shaped 8B agent; planning parameters in J, s and token units.

    12-40 turns, growing cached contexts, tool-result prefills 40-6000,
    decodes 20-2500; true extra turn noise and separate sensor measurements.
    The default world reproduces the reviewer's 7910-row calibration.
    """
    rng, out = random.Random(seed), {}
    for group in range(groups):
        for index in range(per_group):
            eid = f"ep-{seed}-{group}-{index}"
            n, context = rng.randint(12, 40), rng.randint(1500, 3000)
            rows, true_total = [], 0.0
            for k in range(n):
                pf = min(6000, max(40, int(rng.lognormvariate(math.log(600), 1.0))))
                if k == 0:
                    pf = rng.randint(200, 1200)
                dc = min(2500, max(20, int(rng.lognormvariate(math.log(300), .8))))
                h = rng.uniform(*turn_h)
                x = (1, pf, dc, context*dc, context*pf)
                true = math.fsum(a*b for a, b in zip(x, coef)) + rng.gauss(0, sigma)
                measured = true + rng.gauss(0, h)
                rows.append(TurnRow(eid, f"shade/pair-{group}", context, pf, dc,
                                    pf/3000 + dc/60, measured, h))
                true_total += true
                context += pf + dc
            out[eid] = (rows, true_total + rng.gauss(0, episode_h), episode_h)
    return out


def _leave_pair_scores(bench):
    """Independent explicit leave-pair-out calibration, including bad totals."""
    scores = []
    groups = sorted({r.group for rows, _, _ in bench.values() for r in rows})
    for group in groups:
        training = [r for rows, _, _ in bench.values()
                    if rows and rows[0].group != group for r in rows]
        model = fit_energy_model(training)
        for rows, total, h in bench.values():
            if rows and rows[0].group == group:
                score = residual_score(model, rows, total, h)
                if math.isfinite(score):
                    scores.append(score)
    return scores


def _ols_three(rows):
    """Independent stdlib 3-column OLS via pivoted normal-equation elimination."""
    x = [[1.0, r.prefill_tokens, r.decode_tokens] for r in rows]
    a = [[math.fsum(r[i]*r[j] for r in x) for j in range(3)]
         + [math.fsum(r[i]*t.energy_j for r, t in zip(x, rows))]
         for i in range(3)]
    for j in range(3):
        pivot = max(range(j, 3), key=lambda k: abs(a[k][j]))
        a[j], a[pivot] = a[pivot], a[j]
        for i in range(j+1, 3):
            ratio = a[i][j]/a[j][j]
            a[i] = [v-ratio*u for v, u in zip(a[i], a[j])]
    coef = [0.0]*3
    for j in reversed(range(3)):
        coef[j] = (a[j][3]-math.fsum(a[j][k]*coef[k]
                                    for k in range(j+1, 3)))/a[j][j]
    rss = math.fsum((r.energy_j-math.fsum(c*v for c, v in zip(coef, xx)))**2
                    for r, xx in zip(rows, x))
    return coef, rss/(len(rows)-3)


class TestEnergyResidualExclusions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Calibration/evaluation sizes reproduce the lead's review world.
        cls.bench = _sensor_world(20_000, 10, 30)
        cls.rows = [r for rows, _, _ in cls.bench.values() for r in rows]
        cls.model = fit_energy_model(cls.rows)
        cls.threshold = grouped_benign_threshold(cls.bench, alpha=.05)

    def test_unusable_episode_score_uses_exact_finite_order_statistic(self):
        bench = dict(self.bench)
        key = next(iter(bench))
        bench[key] = (bench[key][0], 0.0, math.inf)
        threshold = grouped_benign_threshold(bench, alpha=.05)
        scores = _leave_pair_scores(bench)
        self.assertEqual(len(scores), 299)  # 300 episodes minus one failed total.
        # Identical ordered training rows/refits and score inputs: bit identity.
        self.assertEqual(threshold, sorted(scores)[math.ceil(.95*299)-1])
        self.assertIn("nonfinite_measurement", threshold.flags)
        self.assertIn("excluded_heldout_scores=1", threshold.flags)
        evaluation = _sensor_world(30_000, 10, 100)
        caught = sum(residual_score(self.model, rows, total+500, h) > threshold
                     for rows, total, h in evaluation.values())
        # At most 40 turns, 2.5 J extra sd and 1.5 J episode uncertainty give
        # D about 16 J; +500 J shifts scores >30, far past this ~1.6 threshold.
        self.assertEqual(caught, 1000)

    def test_one_missing_turn_fit_is_identical_to_explicit_exclusion(self):
        bench = dict(self.bench)
        key = list(bench)[5]
        rows, total, h = bench[key]
        damaged = list(rows)
        damaged[3] = replace(damaged[3], energy_j=math.nan)
        bench[key] = (damaged, total, h)
        all_rows = [r for rr, _, _ in bench.values() for r in rr]
        model = fit_energy_model(all_rows)
        expected = fit_energy_model([r for r in all_rows if math.isfinite(r.energy_j)])
        self.assertEqual(len(all_rows), 7910)  # Fixed review-world integer count.
        self.assertEqual(model.n_turns, 7909)
        self.assertEqual(asdict(model), asdict(expected))  # Identical fit inputs.
        self.assertIn("excluded_turn_rows=1", model.flags)
        threshold = grouped_benign_threshold(bench, alpha=.05)
        self.assertTrue(math.isfinite(threshold))
        self.assertIn("excluded_turn_rows=1", threshold.flags)
        # A fit's recorded exclusion flags are provenance, not invalid scored
        # counts. Valid normalized logged work must retain usable power values.
        scored_rows = self.bench[key][0]
        normal = min_detectable_hidden_decode_tokens(
            model, scored_rows, alpha=.05, power=.8, measured_half_width_j=h)
        calibrated = calibrated_min_detectable_hidden_decode_tokens(
            model, scored_rows, threshold=threshold, power=.8, measured_half_width_j=h)
        self.assertTrue(math.isfinite(normal))
        self.assertTrue(math.isfinite(calibrated))
        self.assertIn("nonfinite_input", normal.flags)
        self.assertIn("nonfinite_input", calibrated.flags)

    def test_empty_episode_does_not_change_threshold(self):
        bench = dict(self.bench)
        bench["empty-episode"] = ((), 35.0, 1.5)
        threshold = grouped_benign_threshold(bench, alpha=.05)
        # Empty episode contributes no fit row and no score: identical arithmetic.
        self.assertEqual(threshold, self.threshold)
        self.assertIn("excluded_empty_episodes=1", threshold.flags)

    def test_every_unusable_fit_field_is_counted_and_excluded(self):
        for change in (dict(energy_j=math.inf), dict(energy_half_width_j=math.nan),
                       dict(energy_half_width_j=-1), dict(context_tokens=-1),
                       dict(prefill_tokens=1.5), dict(decode_tokens=True)):
            with self.subTest(change=change):
                rows = [replace(self.rows[0], **change)] + self.rows[1:80]
                model = fit_energy_model(rows)
                self.assertEqual(asdict(model), asdict(fit_energy_model(rows[1:])))
                self.assertEqual(model.n_turns, 79)  # 80 minus one unusable row.
                self.assertIn("excluded_turn_rows=1", model.flags)


class TestEnergyResidualIdentifiability(unittest.TestCase):
    def test_no_cache_ols_matches_independent_three_column_solve(self):
        bench = _sensor_world(41, 4, 10)
        rows = [replace(r, context_tokens=0, energy_half_width_j=0)
                for rr, _, _ in bench.values() for r in rr]
        model = fit_energy_model(rows)
        expected, sigma2 = _ols_three(rows)
        for j in range(3):
            printed_se = float(f"{math.sqrt(model.cov[j][j]):.6g}")
            # Agreement is 1% of the printed coefficient standard error.
            self.assertLess(abs(model.coef[j]-expected[j]), .01*printed_se)
        # Variance has no printed uncertainty: the required 1e-6 relative bar.
        self.assertTrue(math.isclose(model.sigma2_per_turn, sigma2, rel_tol=1e-6))
        for j in (3, 4):
            self.assertIn(f"unidentified_column:{model.names[j]}", model.flags)
            self.assertEqual(model.coef[j], 0.0)  # Exact representation convention.
            self.assertEqual(model.cov[j], (0.0,)*5)
            self.assertEqual(tuple(row[j] for row in model.cov), (0.0,)*5)
        prediction = predict_episode(model, [replace(rows[0], context_tokens=1)])
        self.assertIn("unidentified_column_used:context_decode_tokens", prediction.flags)
        # Context zero makes the unidentified context-decode term exactly zero.
        boundary = min_detectable_hidden_decode_tokens(
            model, rows[:20], alpha=.05, power=.8, measured_half_width_j=1.5)
        self.assertIn("unidentified_column:context_decode_tokens", boundary.flags)
        self.assertTrue(math.isfinite(boundary))

    def test_constant_decode_keeps_scores_but_cannot_identify_hidden_token_energy(self):
        bench = _sensor_world(42, 4, 10)
        cap = {eid: ([replace(r, decode_tokens=512) for r in rows], total, h)
               for eid, (rows, total, h) in bench.items()}
        model = fit_energy_model([r for rows, _, _ in cap.values() for r in rows])
        threshold = grouped_benign_threshold(cap, alpha=.05)
        self.assertTrue(math.isfinite(model.sigma2_per_turn))
        self.assertTrue(math.isfinite(threshold))
        self.assertIn("unidentified_column:decode_tokens", model.flags)
        rows, total, h = next(iter(cap.values()))
        self.assertTrue(math.isfinite(residual_score(model, rows, total, h)))
        boundary = min_detectable_hidden_decode_tokens(
            model, rows, alpha=.05, power=.8, measured_half_width_j=h)
        self.assertTrue(math.isnan(boundary))
        self.assertIn("hidden_decode_energy_unidentified", boundary.flags)


class TestEnergyResidualSeparateIntegral(unittest.TestCase):
    def test_m3_score_sd_resolves_the_old_double_count_above_the_bar(self):
        # Independent calibration/evaluation compute budgets: 300 / 1000 episodes.
        parameters = dict(coef=_M3_COEF, sigma=.5, turn_h=(.3, 1.2), episode_h=1.0)
        calibration = _sensor_world(1, 10, 30, **parameters)
        model = fit_energy_model([r for rows, _, _ in calibration.values() for r in rows])
        evaluation = _sensor_world(2, 10, 100, **parameters)
        scores, old_scores = [], []
        for rows, total, h in evaluation.values():
            mean, sd = predict_episode(model, rows)
            scores.append(residual_score(model, rows, total, h))
            old_sd = math.sqrt(sd**2 + sum(r.energy_half_width_j**2 for r in rows))
            old_scores.append((total-mean)/math.hypot(old_sd, h))
        n = len(scores)
        # For n unit-normal scores, sd SE=1/sqrt(2*(n-1)); four SE give about
        # 6e-5 false failure and resolve departures of 0.0895 at n=1000.
        bar = 4/math.sqrt(2*(n-1))
        current, old = stdev(scores), stdev(old_scores)
        message = f"M3 separate integral: sd={current:.6f}, pre-fix sd={old:.6f}, bar=1 +/- {bar:.6f}"
        self.assertLessEqual(abs(current-1), bar, message)
        # Mutation check: the pre-fix formula must fail the same honest bar.
        self.assertGreater(abs(old-1), bar, message)
        print(message)


# Round-2 reviewer-world planning parameters, not hardware measurements.
_RECORD_COEF = (2.0, .0008, .25, 2.5e-6, 1.5e-7)
_RECORD_SIGMA, _RECORD_EP_H = 3.0, 2.0
_NS = 1_000_000_000
_NORMAL = NormalDist()
_DEPARTURE = "benign_score_calibration_departure"


def _record_mean(context, prefill, decode):
    x = (1, prefill, decode, context*decode, context*prefill)
    return math.fsum(a*b for a, b in zip(x, _RECORD_COEF))


def _record_episode(rng, eid, group, *, hidden=None, n_turns=None):
    """vLLM-like 8B agent with prefix cache, growing context and real ToolCalls.

    Planning assumptions: 8000 prefill / 90 decode tokens/s, 0.2-3 s tool waits,
    0.4 J turn-sensor floor plus 2% gain noise. Whole-episode noise is independent.
    Hidden reasoning content is not re-fed into subsequent context.
    """
    n = n_turns if n_turns is not None else rng.randint(6, 30)
    context, now, true_sum, added = 0, 0, 0.0, 0.0
    turns, energy, spec = [], {}, []
    for k in range(n):
        prefill = (rng.randint(2500, 3500) + rng.randint(200, 800) if k == 0 else
                   20 + min(8000, max(30, int(rng.lognormvariate(math.log(400), 1.1)))))
        decode = min(2000, max(15, int(rng.lognormvariate(math.log(180), .9))))
        hid = hidden(rng, k) if hidden else 0
        first = now + math.ceil(prefill/8000*_NS)
        end = first + math.ceil((decode+hid)/90*_NS)
        wait = int(rng.uniform(.2, 3.0)*_NS)
        calls = (ToolCall("tool", end, end+wait, 60, 400),) if k < n-1 else ()
        turns.append(Turn(k, now, end, context, prefill, decode+hid,
                          hidden_tokens=hid, first_token_ns=first, tool_calls=calls))
        mu = _record_mean(context, prefill, decode)
        true = mu + rng.gauss(0, _RECORD_SIGMA)
        h = math.sqrt(.4**2 + (.02*max(mu, 0.0))**2)
        hidden_j = hid*(_RECORD_COEF[2]+_RECORD_COEF[3]*context)
        energy[k] = (true+hidden_j+rng.gauss(0, h), h)
        true_sum += true
        added += hidden_j
        spec.append((context, prefill, decode))
        now = end + (wait if calls else 0)
        context += prefill+decode
    episode = Episode(eid, group, "benign", "synthetic-8b", "mock/vllm", 0,
                      "host", 0, max(now, 1), tuple(turns))
    return episode, energy, true_sum+added+rng.gauss(0, _RECORD_EP_H), _RECORD_EP_H, spec


def _record_world(seed, groups, per_group, **kwargs):
    rng, out = random.Random(seed), {}
    for group in range(groups):
        for index in range(per_group):
            eid = f"w{seed}-{group}-{index}"
            out[eid] = _record_episode(rng, eid, f"shade/pair-{group:02d}", **kwargs)
    return out


def _record_bench(world, **kwargs):
    return {eid: (turn_rows_from_episode(ep, en, **kwargs), total, h)
            for eid, (ep, en, total, h, _) in world.items()}


def _tool_energy(world, seed, parameters, *, owned):
    """Per-call energy A+B*wait+N(0,C**2), in total and optionally its owner."""
    a, b, c = parameters
    rng, out = random.Random(seed), {}
    for eid, (ep, en, total, h, spec) in world.items():
        new_en, extra = dict(en), 0.0
        for turn in ep.turns:
            add = math.fsum(a+b*(call.end_ns-call.start_ns)/_NS+rng.gauss(0, c)
                            for call in turn.tool_calls)
            if owned:
                e, hw = new_en[turn.index]
                new_en[turn.index] = (e+add, hw)
            extra += add
        out[eid] = (ep, new_en, total+extra, h, spec)
    return out


def _heterogeneous_energy(world, seed, rel_sd):
    """Replace intrinsic noise with rel_sd*mean, consistently in both integrals."""
    rng, out = random.Random(seed), {}
    for eid, (ep, en, _, h, spec) in world.items():
        new_en, true_sum = {}, 0.0
        for (context, prefill, decode), (k, (_, hw)) in zip(spec, sorted(en.items())):
            mu = _record_mean(context, prefill, decode)
            true = mu+rng.gauss(0, rel_sd*mu)
            new_en[k] = (true+rng.gauss(0, hw), hw)
            true_sum += true
        out[eid] = (ep, new_en, true_sum+rng.gauss(0, h), h, spec)
    return out


class _IndexCount:
    """Stdlib stand-in for a table scalar such as numpy.int64."""
    def __init__(self, value):
        self.value = value

    def __index__(self):
        return self.value


class TestEnergyResidualTokenRepresentations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bench = _record_bench(_record_world(800_003, 4, 5))
        cls.rows = [r for rows, _, _ in cls.bench.values() for r in rows]
        cls.model = fit_energy_model(cls.rows)
        cls.threshold = grouped_benign_threshold(cls.bench, alpha=.05)

    def _check_representation(self, convert):
        def converted(rows):
            return [replace(r, context_tokens=convert(r.context_tokens),
                            prefill_tokens=convert(r.prefill_tokens),
                            decode_tokens=convert(r.decode_tokens)) for r in rows]
        rows = converted(self.rows)
        other = fit_energy_model(rows)
        # All counts normalize to identical Python ints, so the same ordered
        # design/energy inputs must give bit-identical fit and score arithmetic.
        self.assertEqual(asdict(other), asdict(self.model))
        self.assertNotIn("invalid_token_count", other.flags)
        self.assertFalse(any(f.startswith("excluded_turn_rows=") for f in other.flags))
        for plain, adapted in zip(self.rows, rows):
            self.assertEqual(design_row(plain), design_row(adapted))
            self.assertTrue(all(type(x) is int for x in design_row(adapted)[1:]))
        bench = {eid: (converted(rr), total, h)
                 for eid, (rr, total, h) in self.bench.items()}
        threshold = grouped_benign_threshold(bench, alpha=.05)
        self.assertEqual(threshold, self.threshold)  # Identical normalized inputs.
        self.assertEqual(threshold.flags, self.threshold.flags)
        rr, total, h = next(iter(bench.values()))
        score = residual_score(self.model, rr, total+1e6, h)
        self.assertTrue(math.isfinite(score))
        # +1 MJ is orders above this world's tens-of-J score denominator.
        self.assertGreater(score, threshold)
        normal = min_detectable_hidden_decode_tokens(
            self.model, rr, alpha=.05, power=.8, measured_half_width_j=h)
        plain = min_detectable_hidden_decode_tokens(
            self.model, next(iter(self.bench.values()))[0],
            alpha=.05, power=.8, measured_half_width_j=h)
        self.assertEqual(normal, plain)  # Same normalized mean context as well.

    def test_indexable_counts_are_bit_identical_to_plain_ints(self):
        self._check_representation(_IndexCount)

    def test_whole_real_counts_are_bit_identical_to_plain_ints(self):
        self._check_representation(float)

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "optional NumPy table scalars absent")
    def test_numpy_int64_counts_are_bit_identical_to_plain_ints(self):
        import numpy as np
        self._check_representation(np.int64)

    def test_invalid_counts_remain_counted_exclusions(self):
        for value in (512.5, math.nan, -1, True, math.inf, -math.inf, "512"):
            with self.subTest(value=value):
                rows = [replace(self.rows[0], decode_tokens=value)] + self.rows[1:]
                fit = fit_energy_model(rows)
                # Excluding the one invalid row preserves identical ordered inputs.
                self.assertEqual(asdict(fit), asdict(fit_energy_model(rows[1:])))
                self.assertEqual(fit.n_turns, len(rows)-1)
                self.assertIn("invalid_token_count", fit.flags)
                self.assertIn("excluded_turn_rows=1", fit.flags)
                self.assertIn("invalid_token_count", design_row(rows[0]).flags)


class TestEnergyResidualCalibrationDiagnostics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Same independent budgets/seeds as the lead: m=600 calibration episodes
        # from 12 task pairs; n=2000 evaluation episodes from 20 other pairs.
        cls.calibration_world = _record_world(600_000, 12, 50)
        cls.evaluation_world = _record_world(700_000, 20, 100)

    def test_owned_tool_energy_has_no_departure_but_omitted_ownership_does(self):
        for parameters in ((.5, .5, .5), (2.0, 1.0, 1.0)):
            for owned in (True, False):
                with self.subTest(parameters=parameters, owned=owned):
                    bench = _record_bench(_tool_energy(
                        self.calibration_world, 1, parameters, owned=owned))
                    threshold = grouped_benign_threshold(bench, alpha=.05)
                    self.assertEqual(_DEPARTURE in threshold.flags, not owned)
                    self.assertEqual(threshold.n_scores, len(bench))  # No data removed.
                    print(f"tool {parameters}, owned={owned}: threshold={threshold:.4f}, "
                          f"mean={threshold.benign_mean:+.4f}, sd={threshold.benign_sd:.4f}, "
                          f"flags={threshold.flags}")

    def test_departure_matches_independent_heldout_moments_and_sd_only_case(self):
        for label, world, expected_flag in (
            ("control", self.calibration_world, False),
            ("large unowned", _tool_energy(self.calibration_world, 1, (6, 4, 2), owned=False), True),
            ("8% intrinsic noise", _heterogeneous_energy(self.calibration_world, 11, .08), True),
        ):
            with self.subTest(label=label):
                bench = _record_bench(world)
                threshold = grouped_benign_threshold(bench, alpha=.05)
                scores = _leave_pair_scores(bench)
                m, mu, sd = len(scores), fmean(scores), stdev(scores)
                self.assertEqual(threshold.n_scores, m)  # Finite integer count.
                # Identical refits and scores in the same order: bit identity.
                self.assertEqual(threshold.benign_mean, mu)
                self.assertEqual(threshold.benign_sd, sd)
                # Mean SE=1/sqrt(m); sample-sd SE=1/sqrt(2*(m-1)) for iid
                # unit normals. Four SE have ~6e-5 false flag per comparison;
                # at m=600 resolve mean 0.163 and sd 0.116. Fold dependence
                # can increase the actual false-flag rate.
                mean_departure = abs(mu) > 4/math.sqrt(m)
                sd_departure = abs(sd-1) > 4/math.sqrt(2*(m-1))
                self.assertEqual(_DEPARTURE in threshold.flags, mean_departure or sd_departure)
                self.assertEqual(_DEPARTURE in threshold.flags, expected_flag)
                if label == "8% intrinsic noise":
                    self.assertFalse(mean_departure)
                    self.assertTrue(sd_departure)
                self.assertEqual(threshold, sorted(scores)[math.ceil(.95*m)-1])
                print(f"{label}: m={m}, mean={mu:+.4f}, sd={sd:.4f}, flags={threshold.flags}")

    def test_calibrated_power_resolves_unowned_energy_loss(self):
        parameters = (2.0, 1.0, 1.0)  # J/call, W during wait, J scatter: scale assumptions.
        bench = _record_bench(_tool_energy(self.calibration_world, 1, parameters, owned=False))
        evaluation = _record_bench(_tool_energy(self.evaluation_world, 2, parameters, owned=False))
        model = fit_energy_model([r for rr, _, _ in bench.values() for r in rr])
        threshold = grouped_benign_threshold(bench, alpha=.05)
        self.assertIn(_DEPARTURE, threshold.flags)
        caught_normal, caught_calibrated, false_positives = 0, 0, 0
        normal_tokens, calibrated_tokens = [], []
        for rows, total, h in evaluation.values():
            normal = min_detectable_hidden_decode_tokens(
                model, rows, alpha=.05, power=.8, measured_half_width_j=h)
            calibrated = calibrated_min_detectable_hidden_decode_tokens(
                model, rows, threshold=threshold, power=.8, measured_half_width_j=h)
            explicit = calibrated_min_detectable_hidden_decode_tokens(
                model, rows, threshold=float(threshold)+0.0, power=.8,
                measured_half_width_j=h, benign_mean=threshold.benign_mean,
                benign_sd=threshold.benign_sd)
            # Threshold arithmetic loses metadata; explicit plain numbers must
            # reproduce identical formula inputs and therefore identical bits.
            self.assertEqual(calibrated, explicit)
            context = fmean(r.context_tokens for r in rows)
            _, sd = predict_episode(model, rows)
            expected = max(0, (float(threshold)-threshold.benign_mean
                               + _NORMAL.inv_cdf(.8)*threshold.benign_sd)
                           * math.hypot(sd, h)/(model.coef[2]+model.coef[3]*context))
            # H_cal has no printed uncertainty: 1e-6 relative agreement.
            self.assertTrue(math.isclose(calibrated, expected, rel_tol=1e-6))
            e_true = _RECORD_COEF[2]+_RECORD_COEF[3]*context
            caught_normal += residual_score(model, rows, total+normal*e_true, h) > threshold
            caught_calibrated += residual_score(model, rows, total+calibrated*e_true, h) > threshold
            false_positives += residual_score(model, rows, total, h) > threshold
            normal_tokens.append(normal)
            calibrated_tokens.append(calibrated)
        n, m, power = len(evaluation), threshold.n_scores, .8
        zp = _NORMAL.inv_cdf(power)
        # The estimated score cut mu_b-zp*s_b has SE
        # sqrt(1/m+zp**2/(2*(m-1))); converting to tail probability multiplies
        # by phi(zp). Combine with binomial SE sqrt(power*(1-power)/n).
        # Four combined SE fail a correct approximation about 6e-5 and resolve
        # 0.064 at the declared m=600,n=2000 budgets (lead's round-2 bar).
        cut_se = math.sqrt(1/m+zp*zp/(2*(m-1)))
        bar = 4*math.sqrt((cut_se*_NORMAL.pdf(zp))**2 + power*(1-power)/n)
        message = (f"unowned tool world m={m}, n={n}: "
                   f"normal-theory H median={sorted(normal_tokens)[n//2]:.1f}, "
                   f"detection={caught_normal/n:.4f}; "
                   f"calibrated H median={sorted(calibrated_tokens)[n//2]:.1f}, "
                   f"detection={caught_calibrated/n:.4f}; power={power}, bar={bar:.6f}")
        self.assertLessEqual(abs(caught_calibrated/n-power), bar, message)
        self.assertGreater(abs(caught_normal/n-power), bar, message)
        # Calibration-quantile and evaluation binomial uncertainty combine
        # as alpha*(1-alpha)*(1/m+1/n); four SE ~6e-5 false failure.
        fp_bar = 4*math.sqrt(.05*.95*(1/m+1/n))
        self.assertLessEqual(abs(false_positives/n-.05), fp_bar, message)
        print(message)

    def test_sample_max_flag_boundary_and_single_finite_score(self):
        bench = _record_bench(_record_world(800_013, 4, 5))
        for m in (19, 20):
            subset = dict(list(bench.items())[:m])
            threshold = grouped_benign_threshold(subset, alpha=.05)
            # ceil(.95*m) is m for 19 and m-1 for 20. A new iid continuous
            # score exceeds a sample maximum with probability ~1/(m+1).
            self.assertEqual("quantile_at_sample_max" in threshold.flags, m == 19)
            scores = _leave_pair_scores(subset)
            self.assertEqual(threshold, sorted(scores)[math.ceil(.95*m)-1])  # Same arithmetic.
        big = {eid: entry for eid, entry in _record_bench(self.calibration_world).items()
               if entry[0][0].group == "shade/pair-00"}
        # Three training rows cannot identify the required model: only the
        # tiny held-out episode has a finite score, exactly as in edges2.
        ep, en, total, h, _ = _record_episode(random.Random(3), "tiny", "shade/pair-99", n_turns=3)
        big["tiny"] = (turn_rows_from_episode(ep, en), total, h)
        threshold = grouped_benign_threshold(big, alpha=.05)
        self.assertEqual(threshold.n_scores, 1)
        self.assertIn("quantile_at_sample_max", threshold.flags)
        self.assertIn("insufficient_calibration_scores", threshold.flags)
        self.assertTrue(math.isnan(threshold.benign_sd))
        self.assertTrue(math.isfinite(threshold))

    def test_calibrated_power_keeps_identifiability_and_invalid_summary_flags(self):
        bench = _record_bench(_record_world(42, 4, 5))
        rows = [r for rr, _, _ in bench.values() for r in rr]
        model = fit_energy_model([replace(r, decode_tokens=512) for r in rows])
        result = calibrated_min_detectable_hidden_decode_tokens(
            model, rows[:20], threshold=2.0, benign_mean=0.0, benign_sd=1.0,
            power=.8, measured_half_width_j=_RECORD_EP_H)
        self.assertTrue(math.isnan(result))
        self.assertIn("hidden_decode_energy_unidentified", result.flags)
        model = fit_energy_model([replace(r, context_tokens=0) for r in rows])
        result = calibrated_min_detectable_hidden_decode_tokens(
            model, [replace(r, context_tokens=0) for r in rows[:20]],
            threshold=2.0, benign_mean=0.0, benign_sd=1.0,
            power=.8, measured_half_width_j=_RECORD_EP_H)
        self.assertTrue(math.isfinite(result))
        self.assertIn("unidentified_column:context_decode_tokens", result.flags)
        missing = calibrated_min_detectable_hidden_decode_tokens(
            model, rows[:20], threshold=2.0, power=.8, measured_half_width_j=_RECORD_EP_H)
        self.assertTrue(math.isnan(missing))
        self.assertIn("invalid_calibration_summary", missing.flags)


class TestEnergyResidualLoggedReasoningCounts(unittest.TestCase):
    def test_adapter_opt_in_matches_manually_logged_scratchpad_counts(self):
        world = _record_world(800_010, 12, 25,
                              hidden=lambda rng, k: int(rng.lognormvariate(math.log(300), .5)))
        subtracted, counted, manual = _record_bench(world), {}, {}
        for eid, (ep, en, total, h, _) in world.items():
            rows = turn_rows_from_episode(ep, en, hidden_token_counts_logged=True)
            expected = [replace(r, decode_tokens=t.decode_tokens)
                        for r, t in zip(subtracted[eid][0], ep.logged_turns())]
            # Integer count identity: the adapter keeps exactly the reported
            # decode count; every other field and flag is unchanged.
            self.assertEqual(rows, tuple(expected))
            self.assertEqual(rows.flags, subtracted[eid][0].flags)
            counted[eid] = (rows, total, h)
            manual[eid] = (expected, total, h)
        fit_counted = fit_energy_model([r for rr, _, _ in counted.values() for r in rr])
        fit_manual = fit_energy_model([r for rr, _, _ in manual.values() for r in rr])
        fit_subtracted = fit_energy_model([r for rr, _, _ in subtracted.values() for r in rr])
        # Identical Python integer designs, ordered rows and energies: bit identity.
        self.assertEqual(asdict(fit_counted), asdict(fit_manual))
        threshold = grouped_benign_threshold(counted, alpha=.05)
        self.assertEqual(threshold, grouped_benign_threshold(manual, alpha=.05))
        # Four coefficient SE fail a correct normal fit about 6e-5 of the time.
        self.assertLessEqual(abs(fit_counted.coef[2]-_RECORD_COEF[2]),
                             4*math.sqrt(fit_counted.cov[2][2]))
        sub_threshold = grouped_benign_threshold(subtracted, alpha=.05)
        print(f"scratchpad subtracted: sigma2={fit_subtracted.sigma2_per_turn:.3f}, "
              f"decode={fit_subtracted.coef[2]:.5f}, threshold={sub_threshold:.4f}; "
              f"counted: sigma2={fit_counted.sigma2_per_turn:.3f}, "
              f"decode={fit_counted.coef[2]:.5f}, threshold={threshold:.4f}")


if __name__ == "__main__":
    unittest.main()
