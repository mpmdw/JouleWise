from argparse import Namespace
import unittest

try:
    import numpy as np
except ImportError:
    np = None

from scripts.interp_energy.power_analysis import compare_synthetic


@unittest.skipIf(np is None, "optional NumPy extra unavailable")
class DesignComparisonTests(unittest.TestCase):
    def _args(self, **overrides):
        values = dict(trials=128, baseline_w=27, white_sd_w=.03, pink_sd_w=0,
                      thermal_amplitude_w=0, thermal_tau_seconds=300, step=[],
                      burst_rate_hz=0, burst_mean_seconds=1, burst_amplitude_w=0,
                      slow_chip_seconds=8, chip_seconds=1, simulation_seconds=1024,
                      schedule="randomized_abba", seed=12345, sample_rate_hz=4,
                      effect_fraction=1e-5, budget_hours=1, alpha=.05, target_power=.8,
                      systematic_bound_fraction=0)
        return Namespace(**(values | overrides))

    def test_white_noise_has_no_assumed_lockin_gain(self):
        report = compare_synthetic(self._args())
        ratio = report["variance_ratio_slow_over_lockin"]
        self.assertGreater(ratio, .6)
        self.assertLess(ratio, 1.6)

    def test_red_noise_can_reduce_required_independent_session_hours(self):
        report = compare_synthetic(self._args(pink_sd_w=.2))
        ratio = report["variance_ratio_slow_over_lockin"]
        self.assertGreater(ratio, 2)
        plans = [report["designs"][name]["plan_independent_sessions"] for name in ("slow_abba", "lockin")]
        self.assertAlmostEqual(plans[0]["required_hours"] / plans[1]["required_hours"], ratio, delta=.05)
        self.assertEqual(report["status"], "SYNTHETIC_UNCALIBRATED")

    def test_bad_geometry_is_refused(self):
        for args in (self._args(simulation_seconds=1), self._args(chip_seconds=.73), self._args(trials=2)):
            with self.assertRaises(ValueError):
                compare_synthetic(args)


if __name__ == "__main__":
    unittest.main()
