"""2026-10-09 desk erratum: synthetic 18-member windows, first 12 clean members."""

import json
import os
import unittest
from unittest import mock

from joulewise import whole_window as ww
from tests import test_harvest_b5_window as hb
from tests import test_neg8_survivors as survivors


IDS = [f"neg8-refcorpus-r{index:02d}" for index in range(1, 19)]


class CleanCorpusCapTests(hb.WindowTestCase):
    ISOLATE = hb.Neg8ScreenTests.ISOLATE

    def window_with_corpus(self, name, *, size=18, failed=(), reverse=False):
        window = hb.Window(self.tmp / name, catalog_overrides=self.ISOLATE,
                           corpus_size=size, reverse_corpus=reverse)
        self.assertIsNone(hb.neg8_corpus(window, failed))
        return window

    def finish(self, window, *, physics=(), drift=0.0, stored_conditions=()):
        bound = json.loads((window.bound / "neg8-drift-bound.json").read_bytes())
        points = hb.neg8_trajectory(drift)
        survivors.HarvestSurvivorTests.write_verdict(window, points, bound)
        if stored_conditions:
            path = window.claim / "whole-window-verdict.json"
            row = json.loads(path.read_bytes())
            core = row["idle_admission_core"]
            core["conditions"] = sorted({*core["conditions"], *stored_conditions})
            core["neg8_bracket"]["conditions"] = core["conditions"]
            core["neg8_bracket"].update({"decision": "failed", "passed": False})
            hb.put(path, row)

        def meter(run):
            for bundle_id, code in physics:
                run.emit(code, level="member", run_id=bundle_id, collector="monitor", observed={"synthetic": True})

        # The in-window mint has already read all collected points.  During
        # the desk pass the clean builder needs only recorded kept points.
        reads = []
        with hb.neg8_reference_gates(points), mock.patch.object(hb.h._Harvest, "meter_joins", meter):
            real = ww._reference_energy_evidence

            def energy(path, *args, **kwargs):
                reads.append(path.name)
                return real(path, *args, **kwargs)

            with mock.patch.object(ww, "_reference_energy_evidence", energy):
                window.harvest()
        self.assertFalse(set(reads) & set(IDS), reads)
        return self.record(window, "derived/neg8-corpus-physics.json")

    @staticmethod
    def record(window, path):
        return json.loads((window.archive / path).read_bytes())

    def assert_clean(self, window, expected, capped=(), dropped=()):
        physics = self.record(window, "derived/neg8-corpus-physics.json")
        self.assertEqual((physics["members_kept"], physics["beyond_cap"],
                          physics["clean_bound_validated"], physics["problems"]),
                         (len(expected), list(capped), True, []))
        clean = self.record(window, "withheld/neg8-clean-bound.json")["bound"]
        raw = (window.archive / "derived/neg8-clean-corpus.json").read_bytes()
        self.assertEqual(clean["reference_corpus"]["member_ids"], expected)
        self.assertEqual([row["bundle_id"] for row in json.loads(raw)["members"]], expected)
        self.assertTrue(ww.validate_neg8_drift_bound_artifact(
            clean, reference_corpus_bytes=raw, require_corpus_identity=True))
        emitted = [flag["scope"]["run_id"] for flag in window.flags()
                   if flag["code"] == "neg8.corpus_member_dropped"]
        self.assertEqual(set(emitted), set(dropped))
        self.assertFalse(set(emitted) & set(capped))
        return clean

    def test_collected_manifest_accepts_18_10_and_13_with_a_gap_and_uses_route_2(self):
        for name, failed in (("18", []), ("10", IDS[:8]), ("13-gap", [IDS[i] for i in (0, 3, 5, 10, 16)])):
            with self.subTest(name=name):
                window = self.window_with_corpus(name, failed=failed)
                self.assertIsNone(ww.load_neg8_drift_bound_artifact(window.bound / "neg8-drift-bound.json"))
                self.finish(window)
                check = self.record(window, "derived/neg8-bound.json")
                self.assertEqual((check["derived_from"], check["members_committed"], check["members_collected"],
                                  check["dropped_bundle_ids"], check["problems"]),
                                 ("collected_subset", 18, 18 - len(failed), failed, []))
                self.assertNotIn("neg8.bound_not_derived", window.codes())

    def test_collected_manifest_refuses_9_and_a_succeeded_member_left_out(self):
        window = self.window_with_corpus("stale-9")
        self.assertIsNone(hb.neg8_corpus(window, IDS[:9], derive=False))
        window.harvest()
        check = self.record(window, "derived/neg8-bound.json")
        self.assertIsNone(check["derived_from"])
        self.assertIn("collected_members_below_minimum", check["problems"])
        self.assertIn("neg8.bound_not_derived", window.codes())

        window = self.window_with_corpus("selected")
        committed = json.loads((window.measurement / hb.CORPUS_RELATIVE).read_bytes())
        self.assertIsNone(hb.neg8_corpus(window, manifest_members=committed["members"][1:]))
        window.harvest()
        check = self.record(window, "derived/neg8-bound.json")
        self.assertIsNone(check["derived_from"])
        self.assertIn("dropped_member_succeeded:" + IDS[0], check["problems"])
        self.assertIn("neg8.bound_not_derived", window.codes())

    def test_18_clean_members_use_12_and_disclose_six_beyond_cap(self):
        window = self.window_with_corpus("cap18")
        self.finish(window)
        self.assert_clean(window, IDS[:12], IDS[12:])
        self.assertNotIn("neg8.screen_failed", window.codes())
        allowance = self.record(window, "derived/neg8-allowance.json")
        self.assertEqual((allowance["source"], allowance["bound_used"]),
                         ("survivor_rescreen", "corpus_physics_clean"))

    def test_14_bound_members_with_two_physics_drops_use_12(self):
        window = self.window_with_corpus("14-drop2", failed=IDS[14:])
        physics = [(IDS[0], "contention.request_overlap"), (IDS[13], "thermal.os_level_nonzero")]
        self.finish(window, physics=physics)
        self.assert_clean(window, IDS[1:13], dropped=[IDS[0], IDS[13]])

    def test_the_worked_example_caps_after_status_and_physics_losses(self):
        failed = [IDS[i - 1] for i in (2, 3, 5)]
        window = self.window_with_corpus("worked-example", failed=failed)
        self.finish(window, physics=[(IDS[8], "contention.request_overlap")])
        kept = [bundle_id for bundle_id in IDS if bundle_id not in {*failed, IDS[8]}]
        clean = self.assert_clean(window, kept[:12], kept[12:], dropped=[IDS[8]])
        self.assertEqual(clean["estimator"]["student_t_critical_95"], 2.201)

    def test_11_clean_members_use_all_11(self):
        window = self.window_with_corpus("11", failed=IDS[11:])
        self.finish(window)
        self.assert_clean(window, IDS[:11])

    def test_9_clean_members_are_underived_from_corpus_physics(self):
        window = self.window_with_corpus("9-clean", failed=IDS[11:])
        physics = [(bundle_id, "battery.accumulator_excursion") for bundle_id in IDS[:2]]
        record = self.finish(window, physics=physics)
        self.assertEqual((record["members_collected"], record["members_kept"], record["beyond_cap"],
                          record["clean_bound_validated"]), (11, 9, [], False))
        flag, = [flag for flag in window.flags() if flag["code"] == "neg8.bound_not_derived"]
        self.assertEqual(flag["observed"]["source"], "corpus_physics")
        self.assertEqual((flag["observed"]["members_collected"], flag["observed"]["members_kept"]), (11, 9))
        self.assertIn("clean_members_below_minimum", flag["observed"]["problems"])
        self.assertFalse((window.archive / "withheld/neg8-clean-bound.json").exists())

    def test_committed_order_decides_the_cap_when_artifact_order_differs(self):
        window = self.window_with_corpus("reverse", reverse=True)
        original = json.loads((window.bound / "neg8-drift-bound.json").read_bytes())
        self.assertEqual(original["reference_corpus"]["member_ids"], list(reversed(IDS)))
        self.finish(window)
        self.assert_clean(window, IDS[:12], IDS[12:])

    def test_a_changed_committed_order_cannot_decide_the_clean_bound(self):
        window = self.window_with_corpus("changed-order")
        path = window.measurement / hb.CORPUS_ORDER_RELATIVE
        order = json.loads(path.read_bytes())
        order["executed_order"].reverse()
        hb.put(path, order)  # the plan tree still pins the original order bytes
        physics = self.finish(window)
        self.assertFalse(physics["clean_bound_validated"])
        self.assertEqual(physics["problems"], ["corpus_order_manifest_differs_from_pin"])
        self.assertEqual((physics["members_collected"], physics["members_kept"]), (18, 0))
        flag, = [flag for flag in window.flags() if flag["code"] == "neg8.bound_not_derived"]
        self.assertEqual(flag["observed"]["source"], "corpus_physics")
        self.assertEqual(flag["observed"]["problems"], physics["problems"])
        self.assertEqual((flag["observed"]["members_collected"], flag["observed"]["members_kept"]), (18, 0))

    def test_an_unreadable_order_reports_collected_members_and_only_the_order_failure(self):
        window = self.window_with_corpus("missing-order", failed=IDS[13:])
        (window.measurement / hb.CORPUS_ORDER_RELATIVE).unlink()
        physics = self.finish(window)
        self.assertEqual((physics["members_collected"], physics["members_kept"], physics["problems"]),
                         (13, 0, ["corpus_order_manifest_unreadable"]))
        self.assertFalse(physics["clean_bound_validated"])
        flag, = [flag for flag in window.flags() if flag["code"] == "neg8.bound_not_derived"]
        self.assertEqual((flag["observed"]["source"], flag["observed"]["members_collected"],
                          flag["observed"]["members_kept"], flag["observed"]["problems"]),
                         ("corpus_physics", 13, 0, ["corpus_order_manifest_unreadable"]))
        self.assertIn("neg8.screen_failed", window.codes())
        self.assertEqual(self.record(window, "derived/neg8-allowance.json")["source"], "none")
        self.assertFalse((window.archive / "withheld/neg8-clean-bound.json").exists())

    def test_the_clean_bound_keeps_stored_nonunderived_conditions_without_physics_losses(self):
        for size, failed in ((12, ()), (18, ()), (18, IDS[10:])):
            with self.subTest(size=size, failed=failed):
                window = self.window_with_corpus(f"guard-{size}-{len(failed)}", size=size, failed=failed)
                physics = self.finish(window, stored_conditions=["neg8_bracket_reference_invalid"])
                self.assertEqual((physics["dropped"], physics["clean_bound_validated"]), ([], True))
                screen = self.record(window, "derived/neg8-screen.json")
                self.assertIn("neg8_bracket_reference_invalid", screen["stored"]["conditions_beyond_bound_underived"])
                self.assertEqual((screen["harvest_reference_losses"], screen["rescreen"]["evaluated"],
                                  screen["rescreen"]["problems"]),
                                 ({}, False, ["conditions_beyond_bound_underived"]))
                self.assertIn("neg8.screen_failed", window.codes())
                self.assertEqual(self.record(window, "derived/neg8-allowance.json")["source"], "none")

    def test_physics_losses_still_rederive_stored_nonunderived_conditions(self):
        for loss in (IDS[0], "b5t-neg8-end-3"):
            for drift, decision in ((0.0, "passed"), (2.0, "failed")):
                with self.subTest(loss=loss, drift=drift):
                    window = self.window_with_corpus(f"loss-{loss}-{drift}")
                    self.finish(window, physics=[(loss, "contention.request_overlap")], drift=drift,
                                stored_conditions=["neg8_bracket_reference_invalid"])
                    screen = self.record(window, "derived/neg8-screen.json")
                    self.assertIn("neg8_bracket_reference_invalid",
                                  screen["stored"]["conditions_beyond_bound_underived"])
                    self.assertEqual((screen["rescreen"]["evaluated"], screen["rescreen"]["decision"],
                                      screen["rescreen"]["problems"]), (True, decision, []))
                    self.assertEqual("neg8.screen_failed" in window.codes(), decision == "failed")

    def test_an_unavailable_clean_bound_cannot_use_the_uncapped_collected_bound(self):
        for stored_underived in (False, True):
            with self.subTest(stored_underived=stored_underived):
                window = self.window_with_corpus(f"no-clean-bound-{stored_underived}")
                path = window.measurement / hb.CORPUS_ORDER_RELATIVE
                order = json.loads(path.read_bytes())
                order["executed_order"].reverse()
                hb.put(path, order)  # the pinned order bytes remain unchanged
                conditions = [ww.CONDITION_NEG8_DRIFT_BOUND_UNDERIVED,
                              ww.CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED] if stored_underived else []
                physics = self.finish(window, stored_conditions=conditions)
                self.assertFalse(physics["clean_bound_validated"])
                self.assertIn("corpus_order_manifest_differs_from_pin", physics["problems"])
                screen = self.record(window, "derived/neg8-screen.json")
                self.assertEqual((screen["rescreen"]["evaluated"], screen["rescreen"]["decision"],
                                  screen["rescreen"]["problems"]), (False, None, ["clean_bound_unavailable"]))
                self.assertIsNone(screen["bound_used"])
                self.assertIn("neg8.screen_failed", window.codes())
                self.assertFalse((window.archive / "withheld/neg8-rescreen-bracket.json").exists())
                self.assertEqual(self.record(window, "derived/neg8-allowance.json")["source"], "none")
                row = json.loads((window.claim / "whole-window-verdict.json").read_bytes())
                self.assertEqual(ww.harvest_neg8_allowance_bracket(window.archive, row),
                                 (None, "screen_not_passed"))

    def test_a_reversed_12_member_manifest_is_rewritten_in_committed_order(self):
        window = self.window_with_corpus("reverse12", size=12, reverse=True)
        original_raw = (window.measurement / hb.CORPUS_RELATIVE).read_bytes()
        self.finish(window)
        self.assert_clean(window, IDS[:12])
        self.assertNotEqual((window.archive / "derived/neg8-clean-corpus.json").read_bytes(), original_raw)

    def test_allowance_authenticates_the_capped_bound_and_refuses_a_tampered_clean_manifest(self):
        window = self.window_with_corpus("allowance")
        self.finish(window)
        row = json.loads((window.claim / "whole-window-verdict.json").read_bytes())
        bracket, problem = ww.harvest_neg8_allowance_bracket(window.archive, row)
        self.assertIsNone(problem)
        clean = self.assert_clean(window, IDS[:12], IDS[12:])
        self.assertEqual(bracket["drift_bound_artifact"], clean)
        path = window.archive / "derived/neg8-clean-corpus.json"
        os.chmod(path, 0o600)
        path.write_bytes(path.read_bytes() + b" ")
        self.assertEqual(ww.harvest_neg8_allowance_bracket(window.archive, row),
                         (None, "clean_bound_unauthenticated"))

    def test_12_members_without_losses_preserve_bound_screen_and_allowance(self):
        for drift in (0.2, 2.0):
            with self.subTest(drift=drift):
                window = self.window_with_corpus(f"unchanged12-{drift}", size=12)
                original = json.loads((window.bound / "neg8-drift-bound.json").read_bytes())
                manifest_raw = (window.measurement / hb.CORPUS_RELATIVE).read_bytes()
                self.finish(window, drift=drift)
                clean = self.assert_clean(window, IDS[:12])
                self.assertEqual((window.archive / "derived/neg8-clean-corpus.json").read_bytes(), manifest_raw)
                self.assertEqual(hb.h.canonical_json_bytes(clean), hb.h.canonical_json_bytes(original))
                row = json.loads((window.claim / "whole-window-verdict.json").read_bytes())
                stored = row["idle_admission_core"]["neg8_bracket"]
                self.assertEqual("neg8.screen_failed" in window.codes(), stored["decision"] == "failed")
                allowance, problem = ww.harvest_neg8_allowance_bracket(window.archive, row)
                if stored["decision"] == "passed":
                    rescreen = self.record(window, "withheld/neg8-rescreen-bracket.json")["bracket"]
                    self.assertEqual(rescreen, stored)
                    self.assertEqual(rescreen["drift_allowances"], stored["drift_allowances"])
                    self.assertEqual((allowance, problem), (stored, None))
                else:
                    rescreen = self.record(window, "derived/neg8-screen.json")["rescreen"]
                    self.assertEqual((rescreen["evaluated"], rescreen["problems"]),
                                     (False, ["conditions_beyond_bound_underived"]))
                    self.assertFalse((window.archive / "withheld/neg8-rescreen-bracket.json").exists())
                    self.assertEqual((allowance, problem), (None, "screen_not_passed"))


class CleanBoundMultiplierTests(unittest.TestCase):
    def test_the_core_builder_uses_the_registered_t_at_12_and_10(self):
        for n, expected in ((12, 2.201), (10, 2.262)):
            with self.subTest(n=n):
                bound = survivors.bound_artifact(survivors.RULING_CORPUS[:n])
                for family in bound["claim_family_bounds"].values():
                    self.assertEqual(family["estimator"]["student_t_critical_95"], expected)
