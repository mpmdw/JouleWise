from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import validate_align_v4_w1_plan as validator

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "configs/campaigns/align_v4/night_plan.template.json"


def filled_template():
    value = json.loads(TEMPLATE.read_text())
    align = value["align_v4"]
    value["plan_id"] = "align-v4-w1-synthetic"
    value["window_max_s"] = 44_640
    align.update(status="SYNTHETIC_TEST_ONLY", B_D=8192, I_D=300,
                 T_dead=(1750 - 300) / 1.13544, effort="xhigh")
    align["thermal_policy"] = {
        "sensors": {"s_fast": "TC0P", "s_slow": "TG0P", "fan_keys": [],
                    "r0_sha256": "a" * 64},
        "delta_fast_c": 8.0, "delta_slow_c": 5.0,
        "turn_cap_s": 120, "chunk_tokens": 512,
    }
    costs = {"anchor": 3131.27 / 4, "D": 1800, "X-G": 1150, "Y-G": 1150,
             "X-S": 850, "Y-S": 850}
    for row in align["members"]:
        row["member_s"] = costs[row["role"]]
    align["arithmetic"].update(align_s=21931.27, programmed_span_s=26927)
    return value


def matching_inputs(value):
    align = value["align_v4"]
    return {"R0": {"reasoning_effort": align["effort"]},
            "R1": {key: copy.deepcopy(align[key]) for key in ("B_D", "I_D", "T_dead", "thermal_policy")}}


class W1PlanTests(unittest.TestCase):
    def test_amendment_table_arithmetic_and_synthetic_plan_validate(self):
        good = filled_template()
        result = validator.validate(good, matching_inputs(good))
        self.assertEqual(result, {"members": 18, "align_s": 21931.27,
                                  "programmed_span_s": 26927, "window_max_s": 44640})

    def test_committed_template_and_each_remaining_placeholder_are_refused(self):
        template = json.loads(TEMPLATE.read_text())
        with self.assertRaisesRegex(ValueError, "PENDING_R1"):
            validator.validate(template)
        good = filled_template()
        for path in (("align_v4", "B_D"), ("align_v4", "I_D"),
                     ("align_v4", "T_dead"), ("align_v4", "effort"),
                     ("align_v4", "thermal_policy", "sensors", "s_fast")):
            candidate = copy.deepcopy(good)
            target = candidate
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = "PENDING_R1"
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "PENDING_R1"):
                validator.validate(candidate, matching_inputs(good))
        for index in range(18):
            candidate = copy.deepcopy(good)
            candidate["align_v4"]["members"][index]["member_s"] = "PENDING_R1"
            with self.subTest(member=index + 1), self.assertRaisesRegex(ValueError, "PENDING_R1"):
                validator.validate(candidate, matching_inputs(good))

    def test_cli_refuses_template_and_accepts_filled_copy(self):
        refused = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/validate_align_v4_w1_plan.py")],
                                 cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(refused.returncode, 2)
        self.assertIn("REFUSED", refused.stderr)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "night_plan.json"
            path.write_text(json.dumps(filled_template()))
            inputs = Path(temporary) / "inputs.json"
            inputs.write_text(json.dumps(matching_inputs(filled_template())))
            accepted = subprocess.run(
                [sys.executable, "-B", str(ROOT / "scripts/validate_align_v4_w1_plan.py"), str(path),
                 "--inputs", str(inputs)],
                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertIn('"window_max_s": 44640', accepted.stdout)

    def test_arithmetic_or_cap_mismatch_is_refused(self):
        for field, value in (("align_s", 21931.26), ("programmed_span_s", 26926)):
            candidate = filled_template()
            candidate["align_v4"]["arithmetic"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validator.validate(candidate, matching_inputs(candidate))
        candidate = filled_template()
        candidate["align_v4"]["members"][4]["member_s"] = 1801
        with self.assertRaisesRegex(ValueError, "1,800"):
            validator.validate(candidate, matching_inputs(candidate))

    def test_template_is_not_mistakable_for_a_run_night_plan(self):
        from joulewise import night_gate
        good = filled_template()
        with self.assertRaises(night_gate.PlanError):
            night_gate.NightPlan.from_mapping(good)
        self.assertNotEqual(good.get("schema"), night_gate.HAZARD_PLAN_SCHEMA)
        disguised = copy.deepcopy(good)
        disguised["schema"] = night_gate.HAZARD_PLAN_SCHEMA
        with self.assertRaisesRegex(ValueError, "not a run_night plan"):
            validator.validate(disguised, matching_inputs(good))

    def test_values_must_equal_the_inputs_the_kit_installs(self):
        good = filled_template()
        inputs = matching_inputs(good)
        inputs["R1"]["B_D"] = 7168
        with self.assertRaisesRegex(ValueError, "disagrees with registration/inputs.json on: B_D"):
            validator.validate(good, inputs)
        pending = matching_inputs(good)
        pending["R1"]["thermal_policy"] = None
        with self.assertRaisesRegex(ValueError, "still pending for: thermal_policy"):
            validator.validate(good, pending)
        with self.assertRaisesRegex(ValueError, "still pending"):
            validator.validate(good)  # committed inputs.json is pending

    def test_thermal_policy_uses_the_canonical_gate_validator(self):
        candidate = filled_template()
        candidate["align_v4"]["thermal_policy"]["turn_cap_s"] = 400
        with self.assertRaisesRegex(ValueError, "turn_cap_s exceeds 300"):
            validator.validate(candidate, matching_inputs(candidate))


if __name__ == "__main__":
    unittest.main()
