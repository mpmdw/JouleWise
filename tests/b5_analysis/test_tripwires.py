"""X1/J2/J3 stop records and the shared validator counterfactual."""
from dataclasses import replace
import json
import unittest
from unittest import mock

from joulewise import whole_window as ww
from joulewise.b5 import harvest
from joulewise.b5_analysis import context as ctx
from tests.b5_analysis import fixtures_s3b as fx

_WINDOWS = {}


class TripwireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if "BETA_STD" not in _WINDOWS:
            _WINDOWS["BETA_STD"] = fx.cached()

    def case(self):
        case = fx.Case()
        self.addCleanup(case.close)
        return case

    def reference(self, case):
        return next(run for run, slot in ctx.roster_references(case.roster()).items() if slot == "start")

    def fire(self, case):
        with self.assertRaises(ctx.TripwireRefusal) as caught:
            case.build()
        self.assertEqual(caught.exception.code, "excluded_reference_in_screen")
        return caught.exception

    def test_outside_loss_codes_real_pinned_screen_still_uses_reference(self):
        for code in ("member.whole_window_member_failure", "records.malformed_flag_member_exclusion_possible",
                     "roster.before_chain_started", "member.token_count_mismatch", "member.config_not_in_inventory",
                     "member.anchor_energy_envelope_exceeded"):
            with self.subTest(code=code):
                case = self.case()
                target = self.reference(case)
                self.assertNotIn(code, harvest.NEG8_REFERENCE_LOSS_CODES)
                case.exclude(target, code)
                source, screen, bracket, aggregated = case.pinned_rescreen()
                self.assertEqual(source, "survivor_rescreen")
                self.assertIn(target, aggregated)
                case.install_rescreen(screen, bracket)
                stop = self.fire(case)
                public = stop.unrestricted
                self.assertEqual(public["intersection_count"], 1)
                self.assertEqual(public["excluded_reference_count"], 1)
                self.assertEqual(public["survivor_count"], len(aggregated))
                expected = code if fx.CATALOG.entry(code)["blinding"] == "STRUCTURE" else "restricted code"
                self.assertEqual(public["members"], ({"member_id": target, "code": expected},))
                self.assertIn(target, stop.restricted["survivor_bundle_ids"])
                self.assertEqual(set(public), {"pack", "stop", "survivor_count", "excluded_reference_count",
                    "intersection_count", "members"})
                if expected == "restricted code":
                    self.assertNotIn(code, repr(public))

    def test_same_excluded_reference_already_lost_is_silent(self):
        case = self.case()
        target = self.reference(case)
        case.exclude(target, "member.whole_window_member_failure")
        case.exclude(target, "thermal.os_level_nonzero")
        source, screen, bracket, aggregated = case.pinned_rescreen()
        self.assertEqual(source, "survivor_rescreen")
        self.assertNotIn(target, aggregated)
        case.install_rescreen(screen, bracket)
        self.assertNotIn(target, case.build().survivor_bundle_ids)

    def test_included_failed_admission_pair_names_same_reference(self):
        case = self.case()
        target = self.reference(case)
        case.admission_failure(target)
        case.exclude(target, "member.whole_window_member_failure")
        source, screen, bracket, aggregated = case.pinned_rescreen()
        self.assertEqual(source, "survivor_rescreen")
        self.assertIn(target, aggregated)
        case.install_rescreen(screen, bracket)
        stop = self.fire(case)
        self.assertEqual(stop.unrestricted["members"][0]["member_id"], target)
        with mock.patch.object(ctx, "excluded_reference_in_screen", return_value=None):
            context = case.build()
        with fx.adapter_projection(case):
            result = ww.validate_whole_window_verdict_row(case.row, case.window.claim, set(case.row["bundle_ids"]),
                consumption_session=case.session(context))
        self.assertFalse(result.admitted)
        reason = "reference_in_screen_named_by_verdict:environment_admission_failed:" + target
        self.assertIn(reason, result.reasons)

    def test_kept_member_outside_verdict_stops_before_survivor_computation(self):
        case = self.case()
        archive, units = case.inputs()
        run = next(iter(next(iter(units.cells.values())).kept["repeat"])).run_ids[0]
        case.row["bundle_ids"].remove(run)
        case.row["excluded_bundles"] = [{"bundle_id": run, "problems": ["bundle_strict_invalid"],
                                        "detail": "restricted diagnostic not copied"}]
        with mock.patch.object(ctx, "survivor_set", side_effect=AssertionError("tripwire must run first")):
            with self.assertRaises(ctx.TripwireRefusal) as caught:
                ctx.build_context(archive.window, archive, units, case.assessment, case.row)
        stop = caught.exception
        self.assertEqual(stop.code, "kept_member_outside_verdict_membership:" + run)
        self.assertEqual(stop.unrestricted["problems"], ("bundle_strict_invalid",))
        self.assertNotIn("restricted diagnostic", repr(stop.unrestricted))
        self.assertEqual(units, case.inputs()[1])

    def test_kept_tripwire_counterfactual_and_no_number_before_stop(self):
        case = self.case()
        with mock.patch.object(ww, "_derived_neg8_decision", side_effect=AssertionError("unexpected number")):
            self.assertIsNone(case.build().sources_replay)
        case.exclude(self.reference(case), "member.config_not_in_inventory")
        with mock.patch.object(ww, "_derived_neg8_decision", side_effect=AssertionError("unexpected number")):
            self.fire(case)

    def test_two_stop_records_serialize_with_public_redaction(self):
        case = self.case()
        target = self.reference(case)
        code = "member.anchor_energy_envelope_exceeded"
        case.exclude(target, code)
        stop = self.fire(case)
        public = json.loads(json.dumps(stop.to_structure_record()))
        restricted = json.loads(json.dumps(stop.to_record()))
        self.assertEqual(public["members"], [{"member_id": target, "code": "restricted code"}])
        self.assertEqual(restricted["members"], [{"member_id": target, "code": code}])
        self.assertIn(target, restricted["survivor_bundle_ids"])
        self.assertNotIn("survivor_bundle_ids", public)
        public["members"][0]["code"] = "local copy changed"
        self.assertEqual(stop.unrestricted["members"][0]["code"], "restricted code")
