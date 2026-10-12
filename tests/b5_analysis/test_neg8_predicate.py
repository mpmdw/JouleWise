"""One reference predicate: strict validation OR custody triangle, no config leg."""
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise import whole_window as ww
from joulewise.neg8_survivors import (neg8_reference_strict_invalid, neg8_reference_energy_unreadable,
    neg8_stored_conditions)


class Neg8PredicateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s3-predicate-")
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)

    def test_supplied_problems_and_validator_exception(self):
        with mock.patch.object(ww, "_custody_strict_invalid", return_value=False):
            clean = neg8_reference_strict_invalid(self.path, strict_problems=[])
            self.assertFalse(clean.invalid)
            self.assertFalse(clean.strict_ran)
            failed = neg8_reference_strict_invalid(self.path, strict_problems=["re-reduction mismatch"])
            self.assertTrue(failed.invalid)
            self.assertEqual(failed.problems, ("re-reduction mismatch",))
            validator = mock.Mock(side_effect=RuntimeError("synthetic exception"))
            raised = neg8_reference_strict_invalid(self.path, validator=validator)
            validator.assert_called_once_with(self.path, strict=True)
            self.assertTrue(raised.invalid)
            self.assertTrue(raised.strict_ran)
            self.assertEqual(raised.problems, ("strict_validation_raised:RuntimeError",))

    def test_triangle_disagreement_is_independent_of_strict_result(self):
        from tests import test_neg8_survivors as support
        from tests import test_harvest_b5_window as hb
        support.write_unreadable_reference(hb, self.path, "strict_invalid")
        verdict = neg8_reference_strict_invalid(self.path, strict_problems=[])
        self.assertTrue(verdict.triangle_disagrees)
        self.assertTrue(verdict.invalid)

    def test_no_registered_config_leg(self):
        with mock.patch.object(ww, "_custody_strict_invalid", return_value=False), \
                mock.patch.object(ww, "_scientific_config_identity", side_effect=AssertionError("config leg ran")):
            self.assertFalse(neg8_reference_strict_invalid(self.path, strict_problems=[]).invalid)

    def test_energy_matches_real_writer_for_unreadable_shapes(self):
        from tests import test_neg8_survivors as support
        support.VerdictWriterSurvivorTests.setUpClass()
        helper = support.VerdictWriterSurvivorTests()
        helper.root = self.path
        member = helper.references((8.0,), (8.1,), (8.0,))[0]
        summaries = (member.summary, None, {}, {**member.summary, "gross_energy_j": float("nan")},
            {key: value for key, value in member.summary.items() if key != "energy_anchor_shift_envelopes"},
            {**member.summary, "idle_subtracted_energy_j": "unreadable"})
        for summary in summaries:
            with self.subTest(summary=type(summary).__name__):
                candidate = replace(member, summary=summary)
                writer = (helper.run_campaign._gross_energy_for(candidate), helper.run_campaign._idle_subtracted_energy_for(candidate))
                self.assertEqual(neg8_reference_energy_unreadable(summary), None in writer)

    def test_stored_condition_selection(self):
        core = {"conditions": ["neg8_fault", "other", "calibration_acceptance_bound_stale"],
            "neg8_bracket": {"conditions": ["custom_bracket_condition", "neg8_fault"]}}
        self.assertEqual(neg8_stored_conditions(core), frozenset({"neg8_fault", "custom_bracket_condition"}))
        self.assertEqual(neg8_stored_conditions(None), frozenset())


if __name__ == "__main__":
    unittest.main()
