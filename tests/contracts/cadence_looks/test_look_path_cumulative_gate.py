"""Guard the narrow scope of the RL-202a cumulative bundle disposition."""

import copy
import unittest

from .run_look_path_ci import SUPERSEDED, V2, V2_ASSERTION, case_verdict


class CumulativeGateTests(unittest.TestCase):
    def outcome(self, case):
        return {
            "suite": V2,
            "case": case,
            "returncode": 1,
            "stdout": "",
            "stderr": f"Traceback\nValueError: {V2_ASSERTION}\n",
            "supersession": {
                "assertion": V2_ASSERTION,
                "complete_certificate_recheck": True,
                "affected": [{
                    "expected_leg_id": leg,
                    "observed_leg_id": leg,
                    "expected_dc_code": "meter_absent",
                    "observed_dc_code": "not_bracketed",
                    "certificate_sha256": "a" * 64,
                } for leg in SUPERSEDED[case]],
            },
        }

    def test_all_four_exact_proofs_are_superseded(self):
        for name in SUPERSEDED:
            with self.subTest(name=name):
                self.assertEqual(case_verdict(self.outcome(name)), "SUPERSEDED")

    def test_generic_comparator_failure_alone_blocks(self):
        result = self.outcome("meter_absent_fresh")
        result["supersession"] = None
        with self.assertRaisesRegex(ValueError, "no exact mismatch proof"):
            case_verdict(result)

    def test_every_leg_identity_and_code_must_match(self):
        original = self.outcome("dc_only_three_hidden")
        for key, replacement in (("observed_leg_id", "L001"), ("observed_dc_code", "boot_mismatch")):
            with self.subTest(key=key):
                result = copy.deepcopy(original)
                result["supersession"]["affected"][-1][key] = replacement
                with self.assertRaisesRegex(ValueError, "code-only mismatch for L008"):
                    case_verdict(result)

    def test_other_failures_and_unexpected_historical_pass_block(self):
        original = self.outcome("dc_four_hidden_two_levels")
        for changes in ({"stderr": "ValueError: another checker\n"}, {"returncode": 0},
                        {"case": "anchor_unusable_fresh"}, {"suite": "suite-v3"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                case_verdict({**original, **changes})
