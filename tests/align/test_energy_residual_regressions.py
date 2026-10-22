"""Round-1 regression worlds: real refits, separate integrals and partial designs."""

from __future__ import annotations

import math
import random
import unittest
from dataclasses import asdict, replace
from statistics import stdev

from joulewise.align.energy_residual import (
    TurnRow, design_row, fit_energy_model, grouped_benign_threshold,
    min_detectable_hidden_decode_tokens, predict_episode, residual_score,
)

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


if __name__ == "__main__":
    unittest.main()
