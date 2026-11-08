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
TAIL = 20.0


def filled_template():
    value = json.loads(TEMPLATE.read_text())
    align = value["align_v4"]
    value["plan_id"] = "align-v4-w1-synthetic"
    value["window_max_s"] = 44_640
    align.update(status="SYNTHETIC_TEST_ONLY", B_D=8192, I_D=300, max_r1_tail_s=TAIL,
                 T_dead=(1750 - 300) / 1.13544, effort="xhigh")
    align["thermal_policy"] = {
        "classification_sha256": "b" * 64,
        "sensors": {"s_fast": "TC0P", "s_slow": "TG0P", "fan_keys": [],
                    "r0_sha256": "a" * 64},
        "delta_fast_c": 8.0, "delta_slow_c": 5.0,
        "turn_cap_s": 120, "g0_cap_s": 600, "chunk_tokens": 512, "heavy": True, "per_turn": True,
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


def matching_slots(value):
    return {"ac_powermode": 0, "max_r1_tail_s": value["align_v4"]["max_r1_tail_s"]}


def check(value, inputs=None, slots=None):
    return validator.validate(value, inputs if inputs is not None else matching_inputs(value),
                              slots if slots is not None else matching_slots(value))


class W1PlanTests(unittest.TestCase):
    def test_g0_cap_policy_validates_and_template_keeps_placeholder(self):
        value = filled_template()
        value['align_v4']['thermal_policy']['g0_cap_s'] = 625
        self.assertEqual(check(value)['members'], 18)
        template = validator.build_template()
        self.assertEqual(template['align_v4']['thermal_policy']['g0_cap_s'], validator.PLACEHOLDER)

    def test_classification_digest_is_preserved_and_bound_to_inputs(self):
        good = filled_template()
        self.assertEqual(check(good)["members"], 18)
        inputs = matching_inputs(good)
        good["align_v4"]["thermal_policy"]["classification_sha256"] = "c" * 64
        with self.assertRaisesRegex(ValueError, "disagrees with registration/inputs.json on: thermal_policy"):
            check(good, inputs)

    def test_amendment_table_arithmetic_and_synthetic_plan_validate(self):
        good = filled_template()
        result = check(good)
        self.assertEqual(result, {"members": 18, "align_s": 21931.27,
                                  "programmed_span_s": 26927, "window_max_s": 44640})

    def test_committed_template_and_each_remaining_placeholder_are_refused(self):
        template = json.loads(TEMPLATE.read_text())
        with self.assertRaisesRegex(ValueError, "PENDING_R1"):
            validator.validate(template)
        good = filled_template()
        for path in (("align_v4", "B_D"), ("align_v4", "I_D"),
                     ("align_v4", "T_dead"), ("align_v4", "effort"),
                     ("align_v4", "thermal_policy", "classification_sha256"),
                     ("align_v4", "thermal_policy", "g0_cap_s"),
                     ("align_v4", "thermal_policy", "sensors", "s_fast")):
            candidate = copy.deepcopy(good)
            target = candidate
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = "PENDING_R1"
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "PENDING_R1"):
                check(candidate, matching_inputs(good), matching_slots(good))
        for index in range(18):
            candidate = copy.deepcopy(good)
            candidate["align_v4"]["members"][index]["member_s"] = "PENDING_R1"
            with self.subTest(member=index + 1), self.assertRaisesRegex(ValueError, "PENDING_R1"):
                check(candidate, matching_inputs(good), matching_slots(good))

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
            slots = Path(temporary) / "r1_slots.json"
            slots.write_text(json.dumps(matching_slots(filled_template())))
            accepted = subprocess.run(
                [sys.executable, "-B", str(ROOT / "scripts/validate_align_v4_w1_plan.py"), str(path),
                 "--inputs", str(inputs), "--r1-slots", str(slots)],
                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertIn('"window_max_s": 44640', accepted.stdout)

    def test_arithmetic_or_cap_mismatch_is_refused(self):
        for field, value in (("align_s", 21931.26), ("programmed_span_s", 26926)):
            candidate = filled_template()
            candidate["align_v4"]["arithmetic"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                check(candidate)
        candidate = filled_template()
        candidate["align_v4"]["members"][4]["member_s"] = 1801
        with self.assertRaisesRegex(ValueError, "1,800"):
            check(candidate)

    def test_template_is_not_mistakable_for_a_run_night_plan(self):
        from joulewise import night_gate
        good = filled_template()
        with self.assertRaises(night_gate.PlanError):
            night_gate.NightPlan.from_mapping(good)
        self.assertNotEqual(good.get("schema"), night_gate.HAZARD_PLAN_SCHEMA)
        disguised = copy.deepcopy(good)
        disguised["schema"] = night_gate.HAZARD_PLAN_SCHEMA
        with self.assertRaisesRegex(ValueError, "not a run_night plan"):
            check(disguised, matching_inputs(good))

    def test_values_must_equal_the_inputs_the_kit_installs(self):
        good = filled_template()
        inputs = matching_inputs(good)
        inputs["R1"]["B_D"] = 7168
        with self.assertRaisesRegex(ValueError, "disagrees with registration/inputs.json on: B_D"):
            check(good, inputs)
        pending = matching_inputs(good)
        pending["R1"]["thermal_policy"] = None
        with self.assertRaisesRegex(ValueError, "still pending for: thermal_policy"):
            check(good, pending)
        with self.assertRaisesRegex(ValueError, "still pending"):
            validator.validate(good)  # committed inputs.json is pending

    def test_committed_template_is_regenerated_from_the_kit_roster(self):
        self.assertEqual(TEMPLATE.read_bytes(), validator.template_bytes())
        template = json.loads(TEMPLATE.read_text())
        plan = json.loads((ROOT / "configs/campaigns/align_v4/collection_plan.json").read_text())
        self.assertEqual([m["config_sha256"] for m in template["align_v4"]["members"]],
                         [m["config_sha256"] for m in plan["members"]])
        stale = copy.deepcopy(plan)
        stale["members"][4]["config_sha256"] = "0" * 64
        self.assertNotEqual(validator.template_bytes(stale), TEMPLATE.read_bytes())

    def test_template_thermal_policy_heavy_per_turn_are_validated_not_supplied(self):
        template = json.loads(TEMPLATE.read_text())
        self.assertIs(template["align_v4"]["thermal_policy"]["heavy"], True)
        self.assertIs(template["align_v4"]["thermal_policy"]["per_turn"], True)
        for key in ("heavy", "per_turn"):
            candidate = filled_template()
            del candidate["align_v4"]["thermal_policy"][key]
            with self.subTest(missing=key), self.assertRaisesRegex(ValueError, "missing or unknown fields"):
                check(candidate)
        candidate = filled_template()
        candidate["align_v4"]["thermal_policy"]["heavy"] = False
        candidate["align_v4"]["thermal_policy"]["per_turn"] = False
        with self.assertRaisesRegex(ValueError, "heavy with per-turn"):
            check(candidate)
        candidate = filled_template()
        candidate["align_v4"]["thermal_policy"]["per_turn"] = "yes"
        with self.assertRaisesRegex(ValueError, "per_turn must be boolean"):
            check(candidate)
        candidate = filled_template()
        candidate["align_v4"]["thermal_policy"]["window_reference"] = {"role": "capture"}
        with self.assertRaisesRegex(ValueError, "installed per member"):
            check(candidate)

    def test_t_dead_follows_lead_ruling_l1_and_binds_r1_tail(self):
        good = filled_template()
        good["align_v4"].update(max_r1_tail_s=75.0, T_dead=(1800 - 300 - 75 - 10) / 1.13544)
        self.assertEqual(check(good)["members"], 18)
        stale = copy.deepcopy(good)
        stale["align_v4"]["T_dead"] = (1750 - 300) / 1.13544
        with self.assertRaisesRegex(ValueError, "lead ruling L1"):
            check(stale)
        with self.assertRaisesRegex(ValueError, "r1_slots.json on: max_r1_tail_s"):
            check(good, slots={"max_r1_tail_s": 20.0})
        with self.assertRaisesRegex(ValueError, "r1_slots.json is still pending"):
            check(good, slots={"max_r1_tail_s": None})
        candidate = filled_template()
        candidate["align_v4"]["max_r1_tail_s"] = "PENDING_R1"
        with self.assertRaisesRegex(ValueError, "PENDING_R1"):
            check(candidate)
        # L1 can go non-positive (I_D + max_r1_tail_s + 10 >= 1800): the T_dead
        # equality alone would accept it; the kit's member-fit assertion must refuse.
        no_room = filled_template()
        no_room["align_v4"].update(I_D=1700, max_r1_tail_s=95.0,
                                   T_dead=(1800 - 1700 - 95 - 10) / 1.13544)
        with self.assertRaisesRegex(ValueError, "L1: .*member cap"):
            check(no_room)

    def test_thermal_policy_uses_the_canonical_gate_validator(self):
        candidate = filled_template()
        candidate["align_v4"]["thermal_policy"]["turn_cap_s"] = 400
        with self.assertRaisesRegex(ValueError, "turn_cap_s exceeds 300"):
            check(candidate)


if __name__ == "__main__":
    unittest.main()
