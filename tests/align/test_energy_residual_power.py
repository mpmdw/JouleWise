"""Monte Carlo coverage, calibration and sabotage power through the real API."""

from __future__ import annotations

import math
import unittest
from dataclasses import replace
from statistics import NormalDist

from joulewise.align.energy_residual import (
    design_row, fit_energy_model, grouped_benign_threshold,
    min_detectable_hidden_decode_tokens, predict_episode, residual_score,
    turn_rows_from_episode,
)
from tests.align.test_energy_residual import (
    _COEF, _EPISODE_H, _SIGMA, _adapt, _dot, _hidden, _world,
)

_NORMAL = NormalDist()
_ALPHA, _POWER = .05, .8  # Conventional false-positive/power choices in the brief.


def _true_total(rows):
    return math.fsum(_dot(design_row(row), _COEF) for row in rows)


def _noise_variance(rows, measurement_h):
    return math.fsum(_SIGMA**2+row.energy_half_width_j**2 for row in rows) + measurement_h**2


class TestEnergyResidualCoverage(unittest.TestCase):
    def test_coefficient_standard_error_coverage_across_seeds(self):
        # 128 independent worlds make binomial SE about 0.041 at 68% coverage;
        # the five-coefficient 95% simultaneous bar is approximately 0.106.
        # A factor-two covariance error changes coverage much more than this.
        seeds = 128
        target = _NORMAL.cdf(1)-_NORMAL.cdf(-1)
        counts, errors, ses = [0]*5, [[] for _ in range(5)], [[] for _ in range(5)]
        for seed in range(seeds):
            data = _world(1_000_000+seed*1000, 24)
            rows = [row for datum in data for row in _adapt(datum)[0]]
            model = fit_energy_model(rows)
            self.assertEqual(model.flags, ())
            for j in range(5):
                se = math.sqrt(model.cov[j][j])
                error = model.coef[j]-_COEF[j]
                counts[j] += abs(error) <= se
                errors[j].append(error)
                ses[j].append(se)
        # Bonferroni controls a 5-coefficient, two-sided 95% family.
        z = _NORMAL.inv_cdf(1-.05/(2*5))
        bar = z*math.sqrt(target*(1-target)/seeds)
        table = "\ncoefficient true mean_se coverage expected\n" + "\n".join(
            f"{j} {_COEF[j]:.6g} {sum(ses[j])/seeds:.6g} "
            f"{counts[j]/seeds:.4f} {target:.4f}" for j in range(5))
        for j in range(5):
            self.assertLessEqual(abs(counts[j]/seeds-target), bar, table)
            # Mean bias SE combines independent fit uncertainties across seeds.
            mean_se = math.sqrt(math.fsum(se*se for se in ses[j]))/seeds
            self.assertLessEqual(abs(sum(errors[j])/seeds), z*mean_se, table)
        print(table)


class TestEnergyResidualPower(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 400 calibration and 1000 evaluation episodes give an independent
        # binomial comparison SE of sqrt(.05*.95*(1/400+1/1000))=0.012894.
        # Even a family-corrected bar is below the 0.05 signal of a dead detector.
        cls.calibration_data = _world(2_000_000, 400)
        cls.calibration = {datum[0].episode_id:_adapt(datum)
                           for datum in cls.calibration_data}
        cls.training_rows = [row for rows, _, _ in cls.calibration.values() for row in rows]
        cls.model = fit_energy_model(cls.training_rows)
        cls.threshold = grouped_benign_threshold(cls.calibration, alpha=_ALPHA)
        cls.evaluation = _world(3_000_000, 1000)

    def test_grouped_quantile_is_real_leave_pair_out(self):
        # Real refits, not patched score fixtures, independently construct the
        # held-out scores and the specified inverse-ECDF order statistic.
        data = _world(4_000_000, 24)
        benign = {f"unrelated-key-{i}":_adapt(datum) for i, datum in enumerate(data)}
        groups = {row.group for rows, _, _ in benign.values() for row in rows}
        scores = []
        for group in sorted(groups):
            training = [r for rows, _, _ in benign.values() for r in rows if r.group != group]
            model = fit_energy_model(training)
            for rows, energy, h in benign.values():
                if rows[0].group == group:
                    scores.append(residual_score(model, rows, energy, h))
        expected = sorted(scores)[math.ceil((1-_ALPHA)*len(scores))-1]
        actual = grouped_benign_threshold(benign, alpha=_ALPHA)
        # Quantile has no printed uncertainty: 1e-6 relative agreement.
        self.assertTrue(math.isclose(actual, expected, rel_tol=1e-6), (actual, expected))
        self.assertEqual(actual.flags, ())

    def test_held_out_benign_false_positive_rate(self):
        count = sum(residual_score(self.model, *_adapt(datum)) > self.threshold
                    for datum in self.evaluation)
        n, m = len(self.evaluation), len(self.calibration)
        rate = count/n
        # Include independent calibration-quantile and evaluation binomial
        # uncertainty; neither test set is used to choose the threshold.
        se = math.sqrt(_ALPHA*(1-_ALPHA)*(1/n+1/m))
        message = f"benign threshold={self.threshold:.6f}, FP={count}/{n}={rate:.6f}, SE={se:.6f}"
        # One combined binomial SE is the brief's requested agreement bar.
        self.assertLessEqual(abs(rate-_ALPHA), se, message)
        print(message)

    def test_hidden_decode_power_curve(self):
        ratios = (0, .5, 1, 1.5, 2)
        results = []
        for ratio in ratios:
            caught, probabilities, approximate, tokens = 0, [], [], []
            for datum in self.evaluation:
                episode, energies, total, h = datum
                benign_rows = turn_rows_from_episode(episode, energies)
                boundary = min_detectable_hidden_decode_tokens(
                    self.model, benign_rows, alpha=_ALPHA, power=_POWER,
                    measured_half_width_j=h)
                # An equal integer count per turn makes hidden work's mean
                # context exactly the episode's mean, as the power API assumes.
                per_turn = math.ceil(ratio*boundary/len(benign_rows))
                hidden_episode = _hidden(episode, per_turn)
                logged = turn_rows_from_episode(hidden_episode, energies)
                added = per_turn*math.fsum(_COEF[2]+_COEF[3]*r.context_tokens
                                          for r in benign_rows)
                caught += residual_score(self.model, logged, total+added, h) > self.threshold
                mean, sd = predict_episode(self.model, logged)
                denominator = math.hypot(sd, h)
                # Exact conditional normal theory uses known generating
                # coefficients and all real noise terms. Parameter uncertainty
                # remains in the detector denominator; the fitted model is fixed.
                mu = _true_total(benign_rows)+added-mean
                noise_sd = math.sqrt(_noise_variance(benign_rows, h))
                probabilities.append(_NORMAL.cdf((mu-self.threshold*denominator)/noise_sd))
                fitted_per_token = self.model.coef[2]+self.model.coef[3]*sum(
                    r.context_tokens for r in logged)/len(logged)
                approximate.append(_NORMAL.cdf(
                    per_turn*len(logged)*fitted_per_token/denominator-self.threshold))
                tokens.append(per_turn*len(logged))
            n = len(self.evaluation)
            expected = sum(probabilities)/n
            se = math.sqrt(math.fsum(p*(1-p) for p in probabilities))/n
            results.append((ratio, sum(tokens)/n, caught/n, expected, sum(approximate)/n, se))
        table = "\nH/Hmin mean_H observed conditional_theory normal_approx binomial_SE\n" + "\n".join(
            f"{r:.1f} {h:.3f} {obs:.4f} {theory:.4f} {approx:.4f} {se:.5f}"
            for r, h, obs, theory, approx, se in results)
        # Five powers get a two-sided 95% simultaneous normal/binomial bar.
        z = _NORMAL.inv_cdf(1-.05/(2*len(results)))
        for _, _, observed, expected, _, se in results:
            # One count is the minimum discrete empirical-rate resolution.
            self.assertLessEqual(abs(observed-expected), z*se+1/len(self.evaluation), table)
        # Removing hidden energy must miss the high-H branch by much more than
        # the same Monte Carlo bar; the next test checks that negative control.
        print(table)

    def test_deleted_turn_tampering_matches_theory(self):
        results = []
        for deleted in (1, 2, 4):
            caught, probabilities = 0, []
            for episode, energies, total, h in self.evaluation:
                full = turn_rows_from_episode(episode, energies)
                tampered = replace(
                    episode, condition="sabotage",
                    turns=tuple(replace(t, logged=False) if t.index < deleted else t
                                for t in episode.turns),
                    flags=episode.flags+("simulated_deleted_turn",))
                rows = turn_rows_from_episode(tampered, energies)
                caught += residual_score(self.model, rows, total, h) > self.threshold
                mean, sd = predict_episode(self.model, rows)
                # Deleted turns retain their noise in measured energy even
                # though they disappear from the detector's predicted variance.
                denominator = math.hypot(sd, h)
                probabilities.append(_NORMAL.cdf(
                    (_true_total(full)-mean-self.threshold*denominator) /
                    math.sqrt(_noise_variance(full, h))))
            n = len(self.evaluation)
            expected = sum(probabilities)/n
            se = math.sqrt(math.fsum(p*(1-p) for p in probabilities))/n
            results.append((deleted, caught/n, expected, se))
        table = "\ndeleted_turns observed theory binomial_SE\n" + "\n".join(
            f"{d} {observed:.4f} {expected:.4f} {se:.5f}"
            for d, observed, expected, se in results)
        # Three deletion effects: two-sided 95% simultaneous binomial bar.
        z = _NORMAL.inv_cdf(1-.05/(2*len(results)))
        for _, observed, expected, se in results:
            self.assertLessEqual(abs(observed-expected), z*se+1/len(self.evaluation), table)
        print(table)

    def test_zero_energy_hidden_work_is_false_positives_only(self):
        caught, benign = 0, 0
        for episode, energies, total, h in self.evaluation:
            rows = turn_rows_from_episode(episode, energies)
            boundary = min_detectable_hidden_decode_tokens(
                self.model, rows, alpha=_ALPHA, power=_POWER,
                measured_half_width_j=h)
            # Counterfactual backend executes the hidden work with zero added
            # energy; a semantic or duration detector would spuriously catch it.
            hidden_episode = _hidden(episode, math.ceil(2*boundary/len(rows)))
            hidden_rows = turn_rows_from_episode(hidden_episode, energies)
            caught += residual_score(self.model, hidden_rows, total, h) > self.threshold
            benign += residual_score(self.model, rows, total, h) > self.threshold
        self.assertEqual(caught, benign)  # Same visible work and same energy inputs.
        n, m = len(self.evaluation), len(self.calibration)
        se = math.sqrt(_ALPHA*(1-_ALPHA)*(1/n+1/m))
        self.assertLessEqual(abs(caught/n-_ALPHA), se,
                             f"zero-energy control={caught}/{n}; alpha={_ALPHA}, SE={se:.6f}")
        print(f"zero-energy hidden control: {caught}/{n} = {caught/n:.6f}")


if __name__ == "__main__":
    unittest.main()
