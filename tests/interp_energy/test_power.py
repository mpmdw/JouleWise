import json
from pathlib import Path
import subprocess
import sys
import unittest

from joulewise.interp_energy.power import plan_power, study_reference


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/interp_energy/power_analysis.py"


class PowerTests(unittest.TestCase):
    def test_study_95000_pair_reproduction(self):
        reference = study_reference()
        row = reference["rows"][-1]
        self.assertAlmostEqual(row["required_pairs"], 95000, delta=200)
        self.assertEqual(row["pairs_using_rounded_2_80"], 94864)
        self.assertEqual(row["required_replays"], 2 * row["required_pairs"])
        self.assertAlmostEqual(row["required_hours"], row["required_replays"] * 100 / 3600)

    def test_budget_power_and_quadratic_scaling(self):
        kwargs = dict(unit_sd_fraction=.0011, unit_seconds=200, budget_hours=1)
        small = plan_power(effect_fraction=1e-5, **kwargs)
        large = plan_power(effect_fraction=1e-4, **kwargs)
        self.assertEqual(small.budget_units, 18)
        self.assertAlmostEqual(small.required_units / large.required_units, 100, delta=.2)
        self.assertGreater(large.detection_power, small.detection_power)
        self.assertFalse(small.detectable)
        funded = plan_power(effect_fraction=1e-4, **{**kwargs, "budget_hours": large.required_hours + .001})
        self.assertGreaterEqual(funded.detection_power, .8)
        self.assertTrue(funded.detectable)

    def test_systematic_bound_does_not_average_down(self):
        plan = plan_power(effect_fraction=1e-5, unit_sd_fraction=.0011,
                          unit_seconds=200, budget_hours=1e6, systematic_bound_fraction=.0001)
        self.assertTrue(plan.statistically_detectable)
        self.assertFalse(plan.above_systematic_bound)
        self.assertFalse(plan.detectable)

    def test_empty_budget_zero_noise_and_sign(self):
        kwargs = dict(unit_sd_fraction=0, unit_seconds=200)
        empty = plan_power(effect_fraction=1e-5, budget_hours=0, **kwargs)
        self.assertEqual(empty.detection_power, 0)
        self.assertIsNone(empty.mde_fraction)
        truncated = plan_power(effect_fraction=1e-5, budget_hours=.1, **kwargs)
        self.assertEqual(truncated.budget_hours, .1)
        self.assertAlmostEqual(truncated.used_budget_hours, 200 / 3600)
        positive = plan_power(effect_fraction=1e-5, **kwargs)
        negative = plan_power(effect_fraction=-1e-5, **kwargs)
        self.assertEqual(positive.required_units, 1)
        self.assertEqual(positive.detection_power, negative.detection_power)

    def test_bad_inputs(self):
        defaults = dict(effect_fraction=1e-5, unit_sd_fraction=.0011, unit_seconds=200)
        for key, value in (("effect_fraction", 0), ("effect_fraction", float("nan")),
                           ("unit_sd_fraction", -1), ("unit_seconds", 0),
                           ("budget_hours", -1), ("alpha", 1), ("target_power", .4)):
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                plan_power(**{**defaults, key: value})

    def test_cli_paired_only_without_site_packages(self):
        proc = subprocess.run([sys.executable, "-B", "-S", str(SCRIPT), "--paired-only"],
                              cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["status"], "DESK_ONLY")
        self.assertIn("required_replays", result["paired_plan"])
        self.assertAlmostEqual(result["study_reference"]["rows"][-1]["required_pairs"], 95000, delta=200)

    def test_lockin_import_is_lazy_without_numpy_or_mlx(self):
        proc = subprocess.run([sys.executable, "-B", "-S", "-c",
                               "import sys; import joulewise.interp_energy.lockin; "
                               "assert 'numpy' not in sys.modules; assert 'mlx' not in sys.modules"],
                              cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_cli_invalid_plan_structured_error(self):
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "--effect-fraction", "0", "--paired-only"],
                              cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stderr)["status"], "invalid_plan")

    def test_cli_missing_numpy_structured_error(self):
        proc = subprocess.run([sys.executable, "-B", "-S", str(SCRIPT)],
                              cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("NumPy", json.loads(proc.stderr)["error"])


if __name__ == "__main__":
    unittest.main()
