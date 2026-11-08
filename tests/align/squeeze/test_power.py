import math
import unittest

try:
    import numpy as np
except ImportError:
    np = None

if np is not None:
    from joulewise.align.squeeze.adversary import Attack, Noise, attack_families
    from joulewise.align.squeeze.detection import Threshold
    from joulewise.align.squeeze.power import (
        adaptive_frontier, continuous_max_cohort_any_fpr, estimate_power,
        normal_energy_max_power, wilson_interval,
    )
    from joulewise.align.squeeze.residual import ResidualModel


@unittest.skipUnless(np is not None, "optional NumPy extra unavailable")
class PowerTests(unittest.TestCase):
    def setUp(self):
        self.model = ResidualModel((2, .001, .5, 0, 0), form="turn")

    def power(self, **kwargs):
        defaults = dict(m=20, heldout_size=40, hidden_work_tokens=256,
                        attacks=(Attack("none"),), trials=512, selection_size=64, seed=33)
        defaults.update(kwargs)
        return estimate_power(self.model, **defaults)

    def test_gaussian_quadrature_null_and_limits(self):
        for m in (20, 28, 39):
            self.assertAlmostEqual(normal_energy_max_power(0, 38, m), 1/(m+1), places=7)
        self.assertGreater(normal_energy_max_power(1000, 38, 39), .9999)
        self.assertLess(normal_energy_max_power(-1000, 38, 20), .0001)

    def test_energy_power_rises_with_work_and_falls_with_noise_and_m(self):
        p = lambda h, sd, m: normal_energy_max_power(h*.5, sd, m)
        self.assertLess(p(128, 38, 20), p(256, 38, 20))
        self.assertGreater(p(256, 19, 20), p(256, 58, 20))
        self.assertGreater(p(256, 38, 20), p(256, 38, 39))

    def test_joint_null_marginal_and_cohort_references(self):
        for m in (20, 39):
            r = self.power(m=m, hidden_work_tokens=0, trials=4096)
            self.assertLess(abs(r.joint_probability-1/(m+1)), 4*r.joint_mc_se)
            self.assertLess(abs(r.cohort_any_probability-40/(m+40)), 4*r.cohort_any_mc_se)
            self.assertIn("zero_dose_control_not_hidden_work_detection", r.flags)
            # SE accounts for shared-threshold variation, unlike pooled binomial SE.
            pooled = (r.joint_probability*(1-r.joint_probability)/(4096*40))**.5
            # q=tail(max) ~ Beta(1,m); ICC=1/(m+2) for tests sharing it.
            expected_se = pooled * (1 + 39/(m+2))**.5
            self.assertAlmostEqual(r.joint_mc_se, expected_se, delta=.1*expected_se)
            self.assertGreater(r.joint_mc_se, pooled*1.2)

    def test_same_seed_bit_identical_and_high_dose_power(self):
        a = self.power(hidden_work_tokens=2048).to_dict()
        b = self.power(hidden_work_tokens=2048).to_dict()
        self.assertEqual(a, b)
        self.assertEqual(a["joint_probability"], 1)
        self.assertEqual(a["cohort_target_probability"], 1)

    def test_adversary_sees_calibration_cut_but_not_evaluation(self):
        attacks = attack_families()["padding"]
        kwargs = dict(threshold=Threshold(2, 20, 20), attacks=attacks,
                      hidden_work_tokens=256, heldout_size=1000, seed=14)
        small = adaptive_frontier(self.model, selection_size=2, **kwargs)
        large = adaptive_frontier(self.model, selection_size=500, **kwargs)
        # Test stream must be unchanged by search budget.
        for a, b in zip(small, large):
            self.assertEqual(a["joint_probability"], b["joint_probability"])
            self.assertEqual(a["monitor_probability"], b["monitor_probability"])
        for rows in (small, large):
            selected = [i for i, row in enumerate(rows) if row["selected_on_search"]]
            self.assertEqual(selected, [int(np.argmin([r["selection_probability"] for r in rows]))])

    def test_mixed_attack_escapes_single_channel_but_joint_detects_large_work(self):
        r = self.power(attacks=attack_families()["combined"], hidden_work_tokens=4096)
        self.assertEqual(r.joint_probability, 1)
        self.assertEqual(sum(r.chosen_attack_counts.values()), r.trials)

    def test_fixed_frontier_matches_independent_gaussian_or_probability(self):
        rows = adaptive_frontier(self.model, threshold=Threshold(2, 20, 20),
                                 attacks=attack_families()["smoothing"],
                                 hidden_work_tokens=128, heldout_size=20000,
                                 selection_size=64, noise=Noise(38), seed=102)
        cdf = lambda z: .5*math.erfc(-z/math.sqrt(2))
        expected = 1-cdf(2)*cdf(2-64/38)
        self.assertLess(abs(rows[0]["joint_probability"]-expected),
                        4*math.sqrt(expected*(1-expected)/20000))
        # Same evaluation draws: lowering only energy cost cannot increase alarms.
        self.assertGreaterEqual(rows[0]["joint_probability"], rows[1]["joint_probability"])
        self.assertGreaterEqual(rows[1]["joint_probability"], rows[2]["joint_probability"])

    def test_no_universal_squeeze_for_opaque_logged_computation(self):
        r = self.power(attacks=(Attack("opaque", logged_fraction=1, monitor_visibility=0),),
                       hidden_work_tokens=10000, trials=4096)
        self.assertLess(abs(r.joint_probability-1/21), 4*r.joint_mc_se)
        self.assertIn("assumed_monitor_evasion", r.flags)

    def test_exact_cohort_reference_and_wilson_limits(self):
        self.assertEqual(continuous_max_cohort_any_fpr(20, 40), 2/3)
        lo, hi = wilson_interval(0, 40)
        self.assertAlmostEqual(lo, 0)
        self.assertGreater(hi, .05)
        lo, hi = wilson_interval(40, 40)
        self.assertLess(lo, 1)
        self.assertAlmostEqual(hi, 1)

    def test_invalid_power_input(self):
        for kwargs in ({"heldout_size": 0}, {"trials": 1}, {"m": True},
                       {"attacks": []}, {"attacks": (Attack("x"), Attack("x"))},
                       {"hidden_work_tokens": -1}, {"selection_size": 0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.power(**kwargs)


if __name__ == "__main__":
    unittest.main()
