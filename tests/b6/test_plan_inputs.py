"""Block-six clock policy reaches the driver without changing block-five sizing."""
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.b5 import plan
from joulewise.b6 import plan_inputs, precheck
from joulewise.hazards import clock

ROOT = Path(__file__).resolve().parents[2]


class ClockThresholdTests(unittest.TestCase):
    def test_block6_policy_reaches_driver_and_precheck(self):
        reg = ROOT / "configs/b6/registration"
        thresholds = plan_inputs.thresholds(ROOT, reg)
        checked, audit = plan.audit_thresholds(
            thresholds, plan.hazard_threshold_defaults(),
            sized={("clock", "t_stream_max_s"): 335, ("disk", "planned_bytes"): 1})
        self.assertEqual(checked["clock"]["h_ms"], 0)
        self.assertEqual(precheck.thresholds_for(ROOT, "ALPHA", reg)["clock"]["h_ms"], 0)
        self.assertIn({"key": "clock.h_ms", "value": 0, "default": 3.7},
                      audit["differences_from_defaults"])
        self.assertTrue(clock.frequency_bound(4 * clock.FREQUENCY_SCALE, checked["clock"])["passes"])
        self.assertEqual(clock.DEFAULT_THRESHOLDS["h_ms"], 3.7)

    def test_block5_sizing_copy_remains_identical(self):
        self.assertEqual((ROOT / "configs/b6/registration/sizing_b5.json").read_bytes(),
                         (ROOT / plan_inputs.SIZING).read_bytes())

    def test_registered_overrides_still_reach_both_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            reg = Path(directory)
            (reg / "precheck_thresholds.json").write_text(json.dumps({"clock": {"frequency_margin_ppm": 0.5}}))
            self.assertEqual(plan_inputs.thresholds(ROOT, reg)["clock"]["frequency_margin_ppm"], 0.5)
            self.assertEqual(precheck.thresholds_for(ROOT, "ALPHA", reg)["clock"]["frequency_margin_ppm"], 0.5)
