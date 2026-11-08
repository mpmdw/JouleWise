"""Tiny synthetic populations only. No native runtime, files or measurements."""

from dataclasses import replace
from pathlib import Path
import subprocess
import sys
import unittest

try:
    import numpy as np
except ImportError:
    np = None

from joulewise.interp_energy.tamper_detection import (
    Edit, StressNoise, calibrate, edit_catalogue, expected_signal, reference_model,
    simulate_detector, synthetic_noise,
)

ROOT = Path(__file__).resolve().parents[2]
EDITS = {edit.name: edit for edit in edit_catalogue()}


class SignalTests(unittest.TestCase):
    def signal(self, name):
        return expected_signal(EDITS[name])

    def test_behaviour_is_large_in_gross_energy_and_accounted_in_residual(self):
        value = self.signal("behaviour_shortening")
        self.assertLess(value["gpu_gross_delta_j"], -1000)
        self.assertEqual(value["gpu_j"], 0)
        self.assertEqual(value["dc_j"], 0)
        self.assertEqual(value["time_s"], 0)

    def test_timing_idle_padding_and_adaptive_observational_equivalence(self):
        plain = self.signal("precision_swap")
        padded = self.signal("precision_idle_mask")
        adaptive = self.signal("precision_adaptive")
        self.assertLess(plain["time_s"], -30)
        self.assertEqual(padded["time_s"], 0)
        self.assertGreater(padded["gpu_j"], plain["gpu_j"])
        self.assertLess(padded["gpu_j"], -800)
        self.assertLess(padded["dc_j"], -1000)
        self.assertTrue(all(adaptive[c] == self.signal("sham")[c]
                            for c in ("gpu_j", "dc_j", "time_s")))

    def test_unlogged_and_logged_equal_dose_and_cpu_boundary_gap(self):
        hidden = self.signal("hidden_gpu_edit")
        logged = self.signal("logged_gpu_edit")
        self.assertEqual(hidden["gpu_gross_delta_j"], logged["gpu_gross_delta_j"])
        self.assertEqual(hidden["dc_gross_delta_j"], logged["dc_gross_delta_j"])
        self.assertEqual(hidden["gpu_j"], 200)
        self.assertEqual(logged["gpu_j"], 0)
        self.assertEqual(logged["time_s"], 0)
        cpu = self.signal("hidden_cpu_edit")
        self.assertEqual(cpu["gpu_j"], 0)
        self.assertEqual(cpu["dc_j"], 40)
        self.assertEqual(self.signal("hidden_gpu_tool_wait")["time_s"], 0)

    def test_surgical_predictions_are_sub_joule_and_doses_are_linear(self):
        self.assertLess(self.signal("surgical_astra")["gpu_j"], .1)
        self.assertEqual(self.signal("fixed_k_expert_identity")["gpu_j"], 0)
        for dose in (0, 25, 50, 100, 200, 400):
            self.assertEqual(expected_signal(Edit("dose", gpu_dose_j=dose))["gpu_j"], dose)
        # Same dense layout: zeroing is a switching hypothesis, not bytes saved.
        for fraction in (-.01, 0, .01):
            edit = replace(EDITS["dense_zero_hypothesis"], rate_fraction=fraction)
            self.assertAlmostEqual(expected_signal(edit)["gpu_j"],
                                   fraction * self.signal("sham")["baseline_gpu_j"])

    def test_invalid_inputs(self):
        for kwargs in ({"gpu_dose_j": -1}, {"decode_ratio": 0}, {"rate_fraction": float("nan")},
                       {"padding": "idle"}, {"accounted_gpu_j": 10}, {"accounted_seconds": 1},
                       {"adversary": "unknown"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Edit("bad", **kwargs)
        with self.assertRaises(ValueError):
            expected_signal(Edit("x"), model=replace(reference_model(), coefficient_basis="above_idle"))
        with self.assertRaises(ValueError):
            StressNoise(gpu_sd_j=-1)

    def test_import_and_design_cli_without_optional_packages(self):
        code = """
import sys
from joulewise.interp_energy import tamper_detection, tamper_challenge
assert tamper_detection.expected_signal(tamper_detection.Edit('test'))['gpu_j'] == 0
assert not any(n.split('.')[0] in {'numpy', 'mlx', 'mlx_lm', 'torch'} for n in sys.modules)
"""
        run = subprocess.run([sys.executable, "-B", "-S", "-c", code], cwd=ROOT,
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        run = subprocess.run([sys.executable, "-B", "-S", "scripts/interp_energy/tamper_detection.py",
                              "--design-only"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('SYNTHETIC_DESIGN_NOT_REGISTERED', run.stdout)


@unittest.skipIf(np is None, "optional NumPy unavailable; no native runtime required")
class DetectorTests(unittest.TestCase):
    def test_both_signs_trigger_and_joint_null_error_is_controlled_for_iid_population(self):
        rng = np.random.default_rng(1234)
        detector = calibrate(rng.normal(size=(10000, 3)))
        null = detector.flags(rng.normal(size=(20000, 3))).any(axis=1).mean()
        self.assertGreater(null, .025)
        self.assertLess(null, .07)
        self.assertTrue(detector.flags([[100, 0, 0], [-100, 0, 0]])[:, 0].all())
        self.assertFalse(detector.flags([detector.thresholds]).any())

    def test_cpu_only_and_padding_channels(self):
        rng = np.random.default_rng(321)
        detector = calibrate(rng.normal(size=(2000, 3)))
        def flags(name):
            signal = expected_signal(EDITS[name])
            return detector.flags([[signal[c] for c in ("gpu_j", "dc_j", "time_s")]])[0]
        self.assertEqual(list(flags("hidden_cpu_edit")), [False, True, False])
        self.assertEqual(list(flags("precision_idle_mask")), [True, True, False])
        self.assertFalse(flags("precision_adaptive").any())

    def test_bad_calibration_and_observations(self):
        for values in ([[1, 2]], [[1, 2, float("nan")]], [[0, 0, 0]] * 100,
                       [[1, 2, 3]] * 10):
            with self.subTest(values=values[:1]), self.assertRaises(ValueError):
                calibrate(values)
        detector = calibrate(np.random.default_rng(0).normal(size=(100, 3)))
        with self.assertRaises(ValueError):
            detector.scores([[0, float("inf"), 1]])

    def test_stress_noise_reproducibility_absolute_scale_and_common_session_floor(self):
        noise = StressNoise(session_sd_j=0, pink_fraction=0, burst_rate_hz=0)
        values = synthetic_noise(2048, seed=45, noise=noise)
        np.testing.assert_array_equal(values, synthetic_noise(2048, seed=45, noise=noise))
        self.assertAlmostEqual(values[:, 0].std(), 2.97, delta=.2)
        self.assertGreater(np.corrcoef(values.T)[0, 1], .5)
        shifted = synthetic_noise(2048, seed=45, noise=replace(noise, session_sd_j=20))
        self.assertGreater(abs(shifted[:, 0].mean() - values[:, 0].mean()), 1)
        self.assertAlmostEqual(shifted[:, 0].std(), values[:, 0].std())

    def test_end_to_end_nulls_positive_controls_and_signed_dose_ladder(self):
        edits = tuple(EDITS[n] for n in ("sham", "surgical_astra", "precision_swap",
                      "precision_idle_mask", "precision_adaptive", "behaviour_shortening"))
        noise = StressNoise(session_sd_j=0)
        report = simulate_detector(copies_per_class=128, seed=43, noise=noise, edits=edits)
        self.assertEqual(report, simulate_detector(copies_per_class=128, seed=43, noise=noise, edits=edits))
        rows = {row["edit"]["name"]: row for row in report["classes"]}
        self.assertGreater(rows["precision_swap"]["channel_flag_rates"]["time_s"], .99)
        self.assertEqual(rows["precision_idle_mask"]["forced_choice_rate"], 1)
        self.assertLess(rows["precision_idle_mask"]["channel_flag_rates"]["time_s"], .1)
        for name in ("sham", "surgical_astra", "precision_adaptive", "behaviour_shortening"):
            self.assertLess(rows[name]["any_flag_rate"], .12)
            self.assertGreater(rows[name]["forced_choice_rate"], .3)
            self.assertLess(rows[name]["forced_choice_rate"], .7)
        self.assertIn("NOT_HARDWARE_EVIDENCE", report["status"])
        # A dose ladder is a power curve, not a semantic edit classifier.
        ladder = tuple(Edit(str(j), gpu_dose_j=j) for j in (0, 5, 10, 20, 40, 80))
        curve = simulate_detector(copies_per_class=256, seed=12, noise=noise, edits=ladder)
        rates = [r["any_flag_rate"] for r in curve["classes"]]
        self.assertLess(rates[0], rates[-1])
        self.assertGreater(rates[-1], .99)


if __name__ == "__main__":
    unittest.main()
