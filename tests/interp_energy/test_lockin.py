from dataclasses import replace
import math
import unittest

try:
    import numpy as np
except ImportError:
    np = None

from joulewise.interp_energy.lockin import (
    NoiseModel, Schedule, abba_differences, demodulate, estimate_abba,
    make_schedule, simulate_trace,
)


@unittest.skipIf(np is None, "optional NumPy extra unavailable")
class SyntheticTraceTests(unittest.TestCase):
    def test_interval_average_and_fraction_convention(self):
        schedule = Schedule((-1, 1, 1, -1), 1.0)
        np.testing.assert_allclose(schedule.window_reference([0, .5, 1, 2.5], [1, 1.5, 3, 3.5]),
                                   [-1, 0, 1, 0])
        trace = simulate_trace(schedule, baseline_w=20, effect_fraction=.01,
                               sample_rate_hz=2, noise=NoiseModel(white_sd_w=0))
        self.assertAlmostEqual(trace.contrast_w, .2)
        self.assertAlmostEqual(np.mean(trace.power_w[trace.reference == 1]) -
                               np.mean(trace.power_w[trace.reference == -1]), .2)

    def test_square_abba_and_biphase_schedule_balance(self):
        for kind in ("square", "abba", "randomized_abba", "manchester"):
            schedule = make_schedule(32, kind=kind, seed=14)
            self.assertEqual(sum(schedule.chips), 0)
            self.assertEqual(schedule, make_schedule(32, kind=kind, seed=14))
            self.assertEqual(len(schedule.chips), 128)
        randomized = np.array(make_schedule(32, seed=14).chips).reshape(-1, 4)
        self.assertEqual(set(randomized[:, 0]), {-1, 1})
        manchester = np.array(make_schedule(32, kind="manchester").chips).reshape(-1, 2)
        np.testing.assert_equal(manchester.sum(axis=1), 0)

    def test_all_noise_components_reproducible_and_additive(self):
        schedule = make_schedule(16, chip_seconds=1)
        noise = NoiseModel(white_sd_w=.02, pink_sd_w=.1, thermal_amplitude_w=.2,
                           thermal_tau_seconds=10, steps=((10.125, .3), (30, -.1)),
                           burst_rate_hz=1, burst_mean_seconds=.5, burst_amplitude_w=.4)
        a = simulate_trace(schedule, noise=noise, seed=91)
        b = simulate_trace(schedule, noise=noise, seed=91)
        np.testing.assert_array_equal(a.power_w, b.power_w)
        np.testing.assert_allclose(a.power_w, a.baseline_w + sum(a.components_w.values()))
        for component in ("white", "pink", "thermal", "steps", "bursts"):
            self.assertGreater(np.ptp(a.components_w[component]), 0)
        self.assertAlmostEqual(np.std(a.components_w["pink"]), .1)
        self.assertGreaterEqual(np.min(a.components_w["bursts"]), 0)

    def test_pink_has_red_spectrum(self):
        trace = simulate_trace(make_schedule(512), sample_rate_hz=8,
                               noise=NoiseModel(white_sd_w=0, pink_sd_w=.1), seed=42)
        spectrum = np.abs(np.fft.rfft(trace.components_w["pink"])) ** 2
        # Equal-width octave-average power should fall approximately as 1/f.
        low, high = np.mean(spectrum[20:40]), np.mean(spectrum[320:640])
        self.assertGreater(low / high, 6)
        self.assertLess(low / high, 40)

    def test_sample_rates_and_partial_windows(self):
        for rate in (1, 8, 10, 1000):
            trace = simulate_trace(make_schedule(8, chip_seconds=1), sample_rate_hz=rate)
            self.assertEqual(len(trace.power_w), 32 * rate)
            self.assertAlmostEqual(trace.ends_seconds[-1], 32)
        trace = simulate_trace(make_schedule(8, chip_seconds=.71), sample_rate_hz=7)
        self.assertAlmostEqual(trace.ends_seconds[-1], trace.schedule.duration_seconds)
        self.assertTrue(np.all(np.abs(trace.reference) <= 1 + 1e-12))

    def test_steps_and_thermal_are_window_averaged(self):
        trace = simulate_trace(make_schedule(8, chip_seconds=1), sample_rate_hz=1,
                               noise=NoiseModel(white_sd_w=0, thermal_amplitude_w=2,
                                                thermal_tau_seconds=3, steps=((.25, 4),)))
        self.assertAlmostEqual(trace.components_w["steps"][0], 3)
        self.assertAlmostEqual(trace.components_w["thermal"][0], 2 * (1 - 3 * (1 - math.exp(-1 / 3))))


@unittest.skipIf(np is None, "optional NumPy extra unavailable")
class EstimatorTests(unittest.TestCase):
    def test_signed_tiny_effect_and_null_at_both_cadences(self):
        for rate in (1, 8, 1000):
            for effect in (-1e-5, 0, 1e-5):
                trace = simulate_trace(make_schedule(32), baseline_w=27, effect_fraction=effect,
                                       sample_rate_hz=rate, noise=NoiseModel(white_sd_w=0))
                for result in (demodulate(trace), estimate_abba(trace)):
                    self.assertAlmostEqual(result.contrast_w, effect * 27, places=10)
                    self.assertLess(result.standard_error_w, 1e-11)

    def test_demodulation_and_abba_cancel_linear_drift(self):
        for kind in ("abba", "randomized_abba", "square", "manchester"):
            trace = simulate_trace(make_schedule(32, kind=kind), noise=NoiseModel(white_sd_w=0))
            time = (trace.starts_seconds + trace.ends_seconds) / 2
            trace = replace(trace, power_w=trace.power_w + .001 * time)
            self.assertAlmostEqual(demodulate(trace).contrast_w, trace.contrast_w, places=10)
            if kind in ("abba", "randomized_abba"):
                np.testing.assert_allclose(abba_differences(trace), trace.contrast_w, atol=1e-12)
            if kind == "square":
                self.assertAlmostEqual(demodulate(trace, fundamental=True).contrast_w,
                                       trace.contrast_w, places=10)

    def test_fundamental_handles_edge_averages_and_harmonics(self):
        trace = simulate_trace(make_schedule(32, chip_seconds=.73, kind="square"),
                               sample_rate_hz=7, effect_fraction=.001,
                               noise=NoiseModel(white_sd_w=0))
        self.assertTrue(np.any(np.abs(trace.reference) < .99))
        for fundamental in (False, True):
            self.assertAlmostEqual(demodulate(trace, fundamental=fundamental).contrast_w,
                                   trace.contrast_w, places=10)
        reverse = Schedule(tuple(-c for c in trace.schedule.chips), .73, "square")
        reversed_trace = simulate_trace(reverse, sample_rate_hz=7, noise=NoiseModel(white_sd_w=0))
        self.assertAlmostEqual(demodulate(reversed_trace, fundamental=True).contrast_w,
                               reversed_trace.contrast_w, places=10)

    def test_estimators_preserve_input_at_khz_cadence(self):
        trace = simulate_trace(make_schedule(32), sample_rate_hz=1000)
        original = [x.copy() for x in (trace.starts_seconds, trace.ends_seconds, trace.reference, trace.power_w)]
        demodulate(trace, edge_guard_seconds=.1)
        estimate_abba(trace)
        for before, after in zip(original, (trace.starts_seconds, trace.ends_seconds, trace.reference, trace.power_w)):
            np.testing.assert_array_equal(before, after)

    def test_edge_guard_and_equal_chip_coverage(self):
        trace = simulate_trace(make_schedule(32, kind="square"), noise=NoiseModel(white_sd_w=0))
        result = demodulate(trace, edge_guard_seconds=.125)
        self.assertAlmostEqual(result.retained_fraction, .875)
        self.assertAlmostEqual(result.contrast_w, trace.contrast_w)
        # Removing one window is an unequal ABBA arm, not a smaller iid sample.
        trace = simulate_trace(make_schedule(32), noise=NoiseModel(white_sd_w=0))
        broken = replace(trace, starts_seconds=trace.starts_seconds[1:],
                         ends_seconds=trace.ends_seconds[1:], reference=trace.reference[1:],
                         power_w=trace.power_w[1:])
        with self.assertRaisesRegex(ValueError, "equal nonempty chip coverage"):
            estimate_abba(broken)

    def test_invalid_and_unidentifiable_inputs(self):
        with self.assertRaises(ValueError):
            NoiseModel(pink_sd_w=-1)
        with self.assertRaises(ValueError):
            Schedule((-1, 1), 2)
        with self.assertRaises(ValueError):
            make_schedule(8.5)
        trace = simulate_trace(make_schedule(32), noise=NoiseModel(white_sd_w=0))
        for kwargs in ({"hac_lags": 32}, {"confidence": 1}, {"edge_guard_seconds": 1},
                       {"ci_method": "iid"}, {"ci_method": "block_bootstrap", "bootstrap_block_length": 32}):
            with self.assertRaises(ValueError):
                demodulate(trace, **kwargs)
        with self.assertRaisesRegex(ValueError, "at least eight"):
            demodulate(simulate_trace(make_schedule(4)))
        with self.assertRaisesRegex(ValueError, "unidentifiable"):
            demodulate(simulate_trace(make_schedule(8, kind="square", chip_seconds=.5), sample_rate_hz=1))
        with self.assertRaisesRegex(ValueError, "ABBA or BAAB"):
            estimate_abba(simulate_trace(make_schedule(8, kind="square")))
        with self.assertRaises(ValueError):
            demodulate(replace(trace, power_w=np.full(len(trace.power_w), np.nan)))


if __name__ == "__main__":
    unittest.main()
