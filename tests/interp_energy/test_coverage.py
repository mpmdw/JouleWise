"""Seeded Monte Carlo checks; tolerances include binomial/MC sampling error.

These check specified synthetic populations, not arbitrary drift or hardware.
Each replicate randomizes ABBA/BAAB independently of the generated noise.
"""

import math
import unittest

try:
    import numpy as np
except ImportError:
    np = None

from joulewise.interp_energy.lockin import (
    NoiseModel, demodulate, estimate_abba, make_schedule, simulate_trace,
)


@unittest.skipIf(np is None, "optional NumPy extra unavailable")
class CoverageTests(unittest.TestCase):
    def _check_population(self, noise, *, n_trials=180, bootstrap=False):
        methods = [("demod_hac", demodulate, {"hac_lags": 3}),
                   ("abba_hac", estimate_abba, {"hac_lags": 3})]
        if bootstrap:
            methods += [("demod_bootstrap", demodulate, {"ci_method": "block_bootstrap",
                                                        "bootstrap_block_length": 4,
                                                        "bootstrap_replicates": 399}),
                        ("abba_bootstrap", estimate_abba, {"ci_method": "block_bootstrap",
                                                          "bootstrap_block_length": 4,
                                                          "bootstrap_replicates": 399})]
        samples = {name: [] for name, _, _ in methods}
        coverage = {name: 0 for name in samples}
        for trial in range(n_trials):
            trace = simulate_trace(make_schedule(128, seed=1000 + trial), noise=noise,
                                   baseline_w=27, effect_fraction=1e-4, seed=5000 + trial)
            for name, estimator, kwargs in methods:
                result = estimator(trace, seed=9000 + trial, **kwargs)
                samples[name].append(result.contrast_w)
                coverage[name] += result.ci_low_w <= trace.contrast_w <= result.ci_high_w
        for name, values in samples.items():
            with self.subTest(method=name, noise=noise):
                mc_se = np.std(values, ddof=1) / math.sqrt(n_trials)
                self.assertLess(abs(np.mean(values) - trace.contrast_w), 4 * mc_se)
                # Four binomial SEs about nominal .95 (not a promise of .95).
                tolerance = 4 * math.sqrt(.95 * .05 / n_trials)
                self.assertLessEqual(abs(coverage[name] / n_trials - .95), tolerance)

    def test_white_noise_unbiasedness_and_hac_bootstrap_coverage(self):
        self._check_population(NoiseModel(white_sd_w=.03), bootstrap=True)

    def test_red_noise_drift_steps_and_bursts_hac_bootstrap_coverage(self):
        self._check_population(NoiseModel(white_sd_w=.03, pink_sd_w=.08,
                                          thermal_amplitude_w=.1, thermal_tau_seconds=300,
                                          steps=((211, .05), (707, -.03)),
                                          burst_rate_hz=.03, burst_mean_seconds=1,
                                          burst_amplitude_w=.1), bootstrap=True)

    def test_fundamental_white_noise_coverage(self):
        values, covered, n = [], 0, 180
        for trial in range(n):
            trace = simulate_trace(make_schedule(128, kind="square"), seed=2000 + trial,
                                   noise=NoiseModel(white_sd_w=.03), effect_fraction=-1e-4)
            result = demodulate(trace, fundamental=True, hac_lags=3)
            values.append(result.contrast_w)
            covered += result.ci_low_w <= trace.contrast_w <= result.ci_high_w
        self.assertLess(abs(np.mean(values) - trace.contrast_w), 4 * np.std(values, ddof=1) / math.sqrt(n))
        self.assertLessEqual(abs(covered / n - .95), 4 * math.sqrt(.95 * .05 / n))


if __name__ == "__main__":
    unittest.main()
