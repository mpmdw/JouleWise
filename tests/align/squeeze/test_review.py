"""Independent synthetic review oracles; no measurement or model inputs."""

import math
import unittest
import warnings

try:
    import numpy as np
except ImportError:
    np = None

if np is not None:
    from joulewise.align.squeeze.adversary import Attack, Noise, attack_effect
    from joulewise.align.squeeze.detection import JointScore, Threshold, max_threshold
    from joulewise.align.squeeze.power import (
        adaptive_frontier, estimate_power, normal_energy_max_power,
    )
    from joulewise.align.squeeze.residual import Carrier, ResidualModel


@unittest.skipUnless(np is not None, "optional NumPy extra unavailable")
class NumericalReviewTests(unittest.TestCase):
    def test_hidden_residual_survives_large_common_padding(self):
        model = ResidualModel((0, 0, .5, 0, 0), form="turn")
        effect = attack_effect(model, Carrier(), Attack("padding", padding_tokens=2**54), 1)
        # Executed padding is common to physical and predicted work. It must
        # not round away the independently representable hidden half joule.
        self.assertEqual(effect.residual_shift_j, .5)

    def test_overflowing_joint_arithmetic_is_refused(self):
        cases = (
            (JointScore(1e-308), [[0, 1e308]]),
            (JointScore(1, energy_location_j=-1e308), [[0, 1e308]]),
            (JointScore(1, energy_weight=1e308), [[0, 1e308]]),
            (JointScore(1, mode="sum"), [[1e308, 1e308]]),
        )
        for rule, scores in cases:
            with self.subTest(rule=rule), warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                with self.assertRaises(ValueError):
                    rule(scores)

    def test_nonfinite_attack_accounting_is_refused(self):
        model = ResidualModel((0, 0, 1e308, 0, 0), form="turn")
        # Finite inputs do not imply representable output joules.
        with self.assertRaises(ValueError):
            attack_effect(model, Carrier(), Attack("overflow"), 2)

    def test_sequence_forgery_and_off_meter_tools_defeat_both_channels(self):
        model = ResidualModel((2, .001, .3, .00004, .0000002))
        # Fabricated counts cancel even the nonlinear sequence energy term.
        forged = attack_effect(model, Carrier(), Attack("forged", phantom_logged_tokens=512), 512)
        remote = attack_effect(model, Carrier(), Attack(
            "remote", tool_fraction=1, tool_meter_fraction=0, tool_monitor_visibility=0), 512)
        for effect in (forged, remote):
            self.assertEqual((effect.monitor_shift, effect.residual_shift_j), (0, 0))
            self.assertEqual(effect.total_work_tokens, 512)


@unittest.skipUnless(np is not None, "optional NumPy extra unavailable")
class StatisticalReviewTests(unittest.TestCase):
    def setUp(self):
        self.model = ResidualModel((0, 0, .5, 0, 0), form="turn")

    def test_iid_realized_tail_tolerance_coverage(self):
        rng = np.random.default_rng(7201)
        trials, m = 12000, 39
        # For Uniform(0,1), the true tail is known for every realized maximum.
        tail = 1 - rng.uniform(size=(trials, m)).max(axis=1)
        bound = max_threshold(range(m)).realized_fpr_upper(.9)
        coverage = np.mean(tail <= bound)
        self.assertLess(abs(coverage-.9), 5*math.sqrt(.9*.1/trials))

    def test_tied_joint_scores_are_conservative(self):
        rule = JointScore(1)
        points = np.array([[0, 1], [1, 0], [0, 1], [1, 0], [2, 0]])
        for future in range(len(points)):
            threshold = rule.calibrate(np.delete(points, future, axis=0))
            alarm = threshold.exceeds(rule(points[future]))
            self.assertEqual(alarm, future == 4)

    def test_gaussian_energy_reference_against_direct_random_maxima(self):
        rng = np.random.default_rng(7202)
        n, m, sd = 40000, 39, 38
        maxima = rng.normal(size=(n, m)).max(axis=1)
        future = rng.normal(size=n)
        # Preserve reused oracle arrays on NumPy 2.2.6/Python 3.14, too.
        maxima.setflags(write=False)
        future.setflags(write=False)
        for shift in (0, 38, 114):
            expected = normal_energy_max_power(shift, sd, m)
            observed = np.mean(future + shift/sd > maxima)
            self.assertLess(abs(observed-expected),
                            5*math.sqrt(expected*(1-expected)/n))

    def test_null_cohort_fraction_matches_beta_binomial_tail(self):
        m, n, trials, cut = 20, 100, 8192, 7
        # q = tail(max calibration) ~ Beta(1,m), K|q ~ Binomial(n,q).
        # P(K=0)=m/(m+n); the recurrence avoids special-function dependencies.
        mass = m/(m+n)
        masses = [mass]
        for k in range(cut-1):
            mass *= (n-k)/(m+n-k-1)
            masses.append(mass)
        expected = 1 - math.fsum(masses)
        result = estimate_power(
            self.model, m=m, heldout_size=n, hidden_work_tokens=0,
            attacks=(Attack("null"),), trials=trials, selection_size=1,
            target_fraction=.07, seed=7203)
        self.assertLess(abs(result.cohort_target_probability-expected),
                        5*math.sqrt(expected*(1-expected)/trials))

    def test_heavy_tail_dependent_channels_preserve_joint_null_rank(self):
        result = estimate_power(
            self.model, m=39, heldout_size=4, hidden_work_tokens=0,
            attacks=(Attack("null"),), noise=Noise(58, correlation=-.7, student_df=3),
            trials=8192, selection_size=1, seed=7204)
        self.assertLess(abs(result.joint_probability-.025), 5*result.joint_mc_se)

    def test_grid_selection_against_analytic_gaussian_oracle(self):
        threshold, h, sd = 2.1, 256, 38
        fractions = (0, .25, .5, .75, 1)
        attacks = tuple(Attack(str(f), logged_fraction=f) for f in fractions)
        cdf = lambda z: .5*math.erfc(-z/math.sqrt(2))
        expected = [1-cdf(threshold-h*f/128)*cdf(threshold-.5*h*(1-f)/sd)
                    for f in fractions]
        rows = adaptive_frontier(
            self.model, threshold=Threshold(threshold, 39, 39), attacks=attacks,
            hidden_work_tokens=h, heldout_size=50000, noise=Noise(sd),
            selection_size=50000, seed=7205)
        chosen = [i for i, row in enumerate(rows) if row["selected_on_search"]]
        self.assertEqual(chosen, [int(np.argmin(expected))])
        for row, probability in zip(rows, expected):
            self.assertLess(abs(row["joint_probability"]-probability),
                            5*math.sqrt(probability*(1-probability)/50000))

    def test_cohort_size_cannot_change_search_choices(self):
        args = dict(m=39, hidden_work_tokens=256,
                    attacks=tuple(Attack(str(f), logged_fraction=f) for f in (0, .5, 1)),
                    trials=64, selection_size=128, seed=7206)
        a = estimate_power(self.model, heldout_size=1, **args)
        b = estimate_power(self.model, heldout_size=100, **args)
        self.assertEqual(a.chosen_attack_counts, b.chosen_attack_counts)


if __name__ == "__main__":
    unittest.main()
