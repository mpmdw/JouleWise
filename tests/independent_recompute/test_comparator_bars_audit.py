"""Focused, synthetic audit probes for the comparator's numeric bars."""
import importlib.util
import json
import math
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "compare_b5_recompute_bar_audit", ROOT / "scripts/compare_b5_recompute.py")
cmp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cmp)
CODED = ROOT / "configs/analysis/b5/recompute_bars.json"


class ComparatorBarAuditTests(unittest.TestCase):
    def setUp(self):
        self.bars = cmp.load_bars(CODED)

    def test_relative_bar_boundary_catches_two_ppm_and_admits_float_noise(self):
        comparison = cmp.Comparison(self.bars)
        reference = 100.0
        bar = comparison.bar("run_phase_energy_j", "synthetic/request", reference)
        self.assertAlmostEqual(bar, 0.0001)

        noise = math.nextafter(reference, math.inf)
        self.assertLess(noise - reference, bar / 1_000_000)
        self.assertEqual(
            comparison.numeric("run_phase_energy_j", "noise", reference, noise)["verdict"], "AGREE")
        self.assertEqual(
            comparison.numeric("run_phase_energy_j", "fault", reference, reference + 2 * bar)["verdict"],
            "DISAGREE")

    def test_zero_uses_absolute_floor_and_counts_remain_exact(self):
        comparison = cmp.Comparison(self.bars)
        self.assertEqual(comparison.bar("floor_j", "synthetic/zero", 0.0), 1e-6)
        self.assertEqual(comparison.bar("count", "synthetic/count", 10), 0.0)
        self.assertEqual(comparison.numeric("count", "count", 10, 10.0)["verdict"], "AGREE")
        self.assertEqual(comparison.numeric("count", "changed", 10, 10.000000000000002)["verdict"], "DISAGREE")

    def test_ordinary_agreeing_row_keeps_legacy_bytes(self):
        row = cmp.Comparison(self.bars).numeric("floor_j", "synthetic/floor", 38.0, 38.000001)
        self.assertEqual(
            json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False),
            '{"bar":3.7999999999999995e-05,"difference":9.999999974752427e-07,"family":"floor_j",'
            '"key":"synthetic/floor","l9":38.0,"recompute":38.000001,"verdict":"AGREE"}')

    def test_relative_term_overflow_refuses_instead_of_silently_agreeing(self):
        self.bars["families"]["run_phase_energy_j"]["relative"] = 2.0
        comparison = cmp.Comparison(self.bars)
        with self.assertRaisesRegex(cmp.Refusal, "^bar_nonfinite_at_runtime$"):
            comparison.numeric("run_phase_energy_j", "huge", 1.7e308, 1.6e308)

    def test_finite_opposite_extremes_disagree_and_remain_strict_json(self):
        comparison = cmp.Comparison(self.bars)
        row = comparison.numeric("run_phase_energy_j", "huge", 1.7e308, -1.7e308)
        self.assertEqual((row["verdict"], row["difference"], row["reason"]),
                         ("DISAGREE", None, "difference_nonfinite"))
        json.dumps(row, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
