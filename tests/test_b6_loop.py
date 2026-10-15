"""All loop transitions with temporary roots, fake time, and fake lanes."""
import fcntl
import json
import os
import plistlib
import shutil
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.b6 import loop as loop_module, queue
from joulewise.b6.lanes import Done, Exclusion, HarvestCapabilities, Hazard, LaneMissing, Lanes, Prepared, PrecheckResult, Running, SessionLine, SmokeResult, Waker, resolve
from joulewise.b6.mailer import Mailer
from joulewise.flags.catalog import Catalog
from scripts import b6_loop as cli_module
from scripts.b6_loop import main
from tests.test_b6_mailer import Clock, Transport
from tests.test_b6_registration import CATALOG, ROOT, modular, registrations


class Precheck:
    def __init__(self):
        self.calls, self.remedies, self.results = [], [], []
        self.fingerprint = {"code_commit": "fixed", "os_build": "test", "model_hashes": {},
                            "boot_session": "boot", "meter_device": "meter", "powermetrics_version": "test", "packs": []}

    def run(self, layout, plan_path):
        self.calls.append(layout.packs)
        return self.results.pop(0) if self.results else PrecheckResult(fingerprint=self.fingerprint)

    def remedy(self, hazard):
        self.remedies.append(hazard)
        return True


class Driver:
    def __init__(self):
        self.prepared, self.jobs, self.launch_calls = {}, {}, []
        self.running_forever = False

    def prepare_session(self, layout, rendered, *, smoke, keep, staging_root):
        key = layout.session_id + ("-smoke" if smoke else "")
        if key not in self.prepared:
            staging_root.mkdir(parents=True, exist_ok=True)
            self.prepared[key] = Prepared(key, str(staging_root / "plan.json"), str(staging_root / "terminal.json"), 360)
        return self.prepared[key]

    def launch(self, prepared):
        if prepared.session_id not in self.jobs:
            self.jobs[prepared.session_id] = prepared
            self.launch_calls.append(prepared.session_id)
        return Running(prepared.session_id)

    def status(self, handle):
        if self.running_forever:
            return handle
        Path(self.jobs[handle.handle].terminal_path).write_text("{}")
        return Done()


class Desk:
    def __init__(self):
        self.smokes, self.lines = [], []
        self.smoke_calls, self.session_calls = [], []

    def evaluate_smoke(self, prepared, done):
        self.smoke_calls.append(prepared.session_id)
        return self.smokes.pop(0) if self.smokes else SmokeResult("pass")

    def session_desk(self, prepared, done):
        self.session_calls.append(prepared.session_id)
        if self.lines:
            return self.lines.pop(0)
        pack = prepared.session_id.split("-")[1]
        return SessionLine(prepared.session_id, (pack,), minutes={"chain": 6, "harvest": 1, "desk": 1})


class Analysis:
    def __init__(self): self.calls = []
    def precision_reached(self, pack_id, reg, counting_ids):
        self.calls.append((pack_id, counting_ids))
        return True


class Harvest:
    def capabilities(self): return HarvestCapabilities(True, True, True)


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.clock = Clock()
        self.precheck, self.driver, self.desk, self.analysis = Precheck(), Driver(), Desk(), Analysis()
        self.transport = Transport()
        self.mailer = Mailer(self.root, CATALOG, clock=self.clock, transport=self.transport)
        self.run_calls, self.remote = [], ""
        self.regs = registrations()
        self.loop = loop_module.Loop(ROOT, self.root, regs=self.regs, clock=self.clock, run=self.runner,
            lanes=Lanes(self.precheck, self.driver, self.desk, Harvest(), self.analysis), mailer=self.mailer, catalog=CATALOG)
        self.addCleanup(self.assert_messages_not_withheld)

    def assert_messages_not_withheld(self):
        for path in (self.root / "outbox").glob("*.json"):
            self.assertFalse(json.loads(path.read_text())["blocked"], path.name)

    def runner(self, argv):
        self.run_calls.append(argv)
        self.assertEqual(argv[-3:], ["ls-remote", "origin", "refs/heads/ops/stop*"])
        return SimpleNamespace(returncode=0, stdout=self.remote)

    def state(self): return self.loop.read_state()

    def tick_to(self, state, limit=150):
        for _ in range(limit):
            if self.state()["state"] == state:
                return
            self.loop.tick()
            self.clock.advance(300)
        self.fail(f"did not reach {state}: {self.state()['state']}")

    def messages(self, kind):
        return [json.loads(p.read_text()) for p in (self.root / "outbox").glob("*.json") if json.loads(p.read_text())["kind"] == kind]

    def test_no_losses_nine_rotated_sessions_close_once_and_wake_once(self):
        self.tick_to("DONE", 200)
        state = self.state()
        self.assertEqual([a["packs"][0] for a in state["attempts"]],
                         ["alpha", "beta", "gamma", "beta", "gamma", "alpha", "gamma", "alpha", "beta"])
        self.assertEqual([len(queue.counting_ids(state, p)) for p in self.regs], [3, 3, 3])
        self.assertEqual(len(self.messages("close")), 1)
        self.assertEqual(len(list((self.root / "wake").glob("*.json"))), 1)
        self.assertEqual(len(self.desk.smoke_calls), 3)
        self.assertEqual(len(self.transport.closed), 9)
        self.loop.tick()
        self.assertEqual(len(self.messages("close")), 1)

    def test_transient_missing_pack_not_close_and_return_resumes(self):
        self.loop.regs_source = registrations(target=1)
        for _ in range(2):
            self.tick_to("ROTATE")
            self.loop.tick()
        regs = self.loop.regs_source
        self.loop.regs_source = {p: regs[p] for p in ("alpha", "beta")}
        for _ in range(2):
            self.assertEqual(self.loop.tick(), 0)
            self.assertEqual(self.state()["state"], "NEXT")
            self.assertEqual(self.state()["idle_reasons"]["gamma"], "pack_not_open")
        self.assertEqual(self.messages("close"), [])
        self.assertEqual(len(self.messages("loop_hold")), 1)
        self.assertEqual(json.loads(self.messages("loop_hold")[0]["body"])["cause"], "pack_not_open:gamma")
        self.assertEqual(len(list((self.root / "wake").glob("*.json"))), 1)
        self.loop.regs_source = regs
        self.loop.tick()
        self.assertEqual(self.state()["state"], "PRECHECK")
        self.assertEqual(self.state()["session"]["packs"], ["gamma"])

    def test_resume_done_returns_to_next(self):
        state = self.state()
        state["state"] = "DONE"
        loop_module.atomic_state(self.root / "state.json", state)
        self.loop.control("resume")
        self.assertEqual(self.state()["state"], "NEXT")

    def test_missing_tree_compose_exception_records_hold_and_notifies_once(self):
        reg = self.regs["alpha"]
        self.loop.regs_source = {"alpha": replace(reg, data={**reg.data, "plan_tree_ref": "configs/missing-b6-plan.json"})}
        self.assertEqual(self.loop.tick(), 0)
        state = self.state()
        self.assertEqual(state["state"], "HOLD_LOOP")
        self.assertEqual(state["hold_reason"], "exception:FileNotFoundError:NEXT")
        self.assertEqual(state["last_exception"]["type"], "FileNotFoundError")
        self.assertEqual(state["last_exception"]["state"], "NEXT")
        self.assertLessEqual(len(state["last_exception"]["message"]), 200)
        self.loop.tick()
        self.assertEqual(len(self.messages("loop_hold")), 1)
        self.assertNotIn("missing-b6-plan", self.messages("loop_hold")[0]["body"])
        self.assertEqual(len(list((self.root / "wake").glob("*.json"))), 1)

    def test_registration_exception_is_inside_tick_boundary(self):
        with patch.object(self.loop, "_registrations", side_effect=OSError("x" * 220)):
            self.assertEqual(self.loop.tick(), 0)
        self.assertEqual(self.state()["hold_reason"], "exception:OSError:NEXT")
        self.assertEqual(len(self.state()["last_exception"]["message"]), 200)

    def assert_launch_exception_rolls_back(self, state):
        self.tick_to(state)
        with patch.object(self.driver, "launch", side_effect=OSError("synthetic launch failure")):
            self.assertEqual(self.loop.tick(), 0)
        self.assertEqual(self.state()["state"], "HOLD_LOOP")
        self.assertEqual(self.state()["hold_reason"], "exception:OSError:" + state)
        self.assertFalse((self.root / "collection.active").exists())
        self.assertEqual(self.state()["packs"]["alpha"]["attempts_since_resume"], 0)
        self.assertEqual(self.state()["slots"].get("1", []), [])
        self.assertEqual(len(self.messages("loop_hold")), 1)
        self.assertEqual(len(list((self.root / "wake").glob("*.json"))), 1)

    def test_session_launch_exception_returns_slot_and_attempt(self):
        self.assert_launch_exception_rolls_back("SESSION_RUN")

    def test_smoke_launch_exception_removes_marker(self):
        self.assert_launch_exception_rolls_back("SMOKE_RUN")

    def test_status_exception_keeps_marker_and_defers_notifications(self):
        self.tick_to("SESSION_RUN")
        self.loop.tick()
        self.assertIn("handle", self.state()["session"])
        with patch.object(self.driver, "status", side_effect=OSError("synthetic status failure")):
            self.assertEqual(self.loop.tick(), 0)
        self.assertEqual(self.state()["hold_reason"], "exception:OSError:SESSION_RUN")
        self.assertTrue((self.root / "collection.active").exists())
        self.assertEqual(self.state()["packs"]["alpha"]["attempts_since_resume"], 1)
        self.assertEqual(self.messages("loop_hold"), [])
        self.assertFalse((self.root / "wake").exists())
        with self.assertRaises(ValueError):
            self.loop.control("resume")
        self.loop.tick()
        self.assertEqual(self.messages("loop_hold"), [])
        Path(self.state()["session"]["prepared"]["terminal_path"]).write_text("{}")
        # The collection has ended: the deferred hold is mailed and wakes once, then resume recovers.
        self.loop.tick()
        self.loop.tick()
        self.assertEqual(len(self.messages("loop_hold")), 1)
        self.assertTrue(self.messages("loop_hold")[0]["delivered"])
        self.assertEqual(len(list((self.root / "wake").glob("*.json"))), 1)
        self.assertNotIn("deferred_event", self.state())
        self.loop.control("resume")
        self.assertEqual(self.state()["state"], "SESSION_RUN")
        self.tick_to("ROTATE")
        self.assertEqual(len(self.state()["attempts"]), 1)

    def test_flush_errors_recorded_without_stalling_precheck(self):
        self.loop.tick()
        with patch.object(self.mailer, "flush", side_effect=OSError("synthetic io failure")):
            self.assertEqual(self.loop.tick(), 0)
        self.assertEqual(self.state()["state"], "SMOKE_RUN")
        self.assertEqual(self.state()["last_io_error"], {"operation": "mailer.flush", "type": "OSError"})

    def test_bootstrap_errors_do_not_escape_tick(self):
        with patch.object(self.loop.waker, "bootstrap_deferred", side_effect=OSError("synthetic io failure")):
            self.assertEqual(self.loop.tick(), 0)
        self.assertEqual(self.state()["state"], "PRECHECK")
        self.assertEqual(self.state()["last_io_error"], {"operation": "waker.bootstrap_deferred", "type": "OSError"})

    def test_arm_wait_remeasures_thermal_before_launch_and_slot(self):
        self.tick_to("ARM_WAIT")
        self.clock.advance(1800)
        self.precheck.results = [PrecheckResult(would_refuse=(Hazard("thermal"),))]
        self.loop.tick()
        self.assertEqual(self.state()["state"], "WAIT_PHYSICS")
        self.assertEqual(self.state()["wait"]["return_state"], "ARM_WAIT")
        self.assertEqual(self.state()["slots"], {})
        self.assertEqual(self.state()["packs"]["alpha"]["attempts_since_resume"], 0)
        self.assertFalse(any("-smoke" not in sid for sid in self.driver.launch_calls))
        self.clock.advance(299)
        self.loop.tick()
        self.assertEqual(self.state()["state"], "ARM_WAIT")
        self.transport.no = True
        self.loop.tick()
        self.assertEqual(self.state()["hold_reason"], "owner_no")
        self.assertFalse(any("-smoke" not in sid for sid in self.driver.launch_calls))

    def test_arm_wait_clear_remeasure_then_launch(self):
        self.tick_to("ARM_WAIT")
        self.clock.advance(1800)
        self.precheck.results = [PrecheckResult(would_refuse=(Hazard("thermal"),))]
        self.loop.tick()
        self.clock.advance(299)
        self.tick_to("SESSION_RUN")
        self.loop.tick()
        self.assertIn("r1-alpha", self.driver.launch_calls)
        self.assertEqual(self.state()["slots"], {"1": ["alpha"]})

    def test_arm_wait_fingerprint_change_runs_fresh_smoke(self):
        self.tick_to("ARM_WAIT")
        old = self.state()["session"]["smoke_prepared"]
        self.clock.advance(1800)
        self.precheck.fingerprint = {**self.precheck.fingerprint, "boot_session": "new-boot"}
        self.loop.tick()
        self.assertEqual(self.state()["state"], "SMOKE_RUN")
        self.assertEqual(self.state()["session"]["fingerprint"], self.precheck.fingerprint)
        self.assertNotIn("smoke_prepared", self.state()["session"])
        self.loop.tick()
        self.assertNotEqual(self.state()["session"]["smoke_prepared"]["terminal_path"], old["terminal_path"])

    def test_arm_wait_certain_exclusion_holds_pack(self):
        self.tick_to("ARM_WAIT")
        self.clock.advance(1800)
        self.precheck.results = [PrecheckResult(certain_exclusion=(Exclusion("model.identity_mismatch"),))]
        self.loop.tick()
        self.assertEqual(self.state()["state"], "NEXT")
        self.assertEqual(self.state()["packs"]["alpha"]["status"], "held")
        self.assertEqual(self.state()["slots"], {})

    def assert_session_refusals_retry(self, at_status):
        from joulewise.b6.lanes import Refused
        self.tick_to("SESSION_RUN")
        launched = []
        launch, status = self.driver.launch, self.driver.status
        def launch_retry(prepared):
            launched.append(prepared)
            return launch(prepared) if at_status or len(launched) > 2 else Refused(("battery_float",))
        def status_retry(handle):
            return Refused(("battery_float",)) if len(launched) <= 2 else status(handle)
        with patch.object(self.driver, "launch", side_effect=launch_retry), patch.object(self.driver, "status", side_effect=status_retry):
            for _ in range(2):
                self.tick_to("WAIT_PHYSICS")
                state = self.state()
                self.assertFalse((self.root / "collection.active").exists())
                self.assertEqual(state["attempts"], [])
                self.assertEqual(state["packs"]["alpha"]["attempts_since_resume"], 0)
                self.assertEqual(state["slots"]["1"], [])
                self.assertEqual(state["wait"]["hazard"], "battery_float")
                self.assertEqual(state["wait"]["return_state"], "ARM_WAIT")
                self.assertFalse(any(k in state["session"] for k in ("started", "t0", "handle", "launch_confirmed")))
                self.tick_to("SESSION_RUN")
            self.tick_to("ROTATE")
        state = self.state()
        self.assertEqual(state["packs"]["alpha"]["status"], "open")
        self.assertEqual(state["packs"]["alpha"]["attempts_since_resume"], 1)
        self.assertEqual(state["slots"], {"1": ["alpha"]})
        self.assertEqual([a["session_id"] for a in state["attempts"]], ["r1-alpha"])
        self.assertEqual(state["attempts"][0]["line"]["session_id"], "r1-alpha")
        self.assertEqual(len({Path(p.plan_path).parent for p in launched}), 3)
        self.assertEqual(len({p.terminal_path for p in launched}), 3)
        self.assertEqual([p.session_id for p in launched], ["r1-alpha", "r1-alpha-a1", "r1-alpha-a2"])

    def test_session_refused_at_status_twice_is_one_measured_attempt(self):
        self.assert_session_refusals_retry(at_status=True)

    def test_session_refused_at_launch_twice_is_one_measured_attempt(self):
        self.assert_session_refusals_retry(at_status=False)

    def test_smoke_refused_retries_under_new_staging(self):
        from joulewise.b6.lanes import Refused
        self.tick_to("SMOKE_RUN")
        with patch.object(self.driver, "launch", return_value=Refused(("thermal",))):
            self.loop.tick()
        old = next(iter(p for p in self.driver.prepared.values() if "-smoke" in p.session_id))
        self.assertEqual(self.state()["state"], "WAIT_PHYSICS")
        self.assertFalse((self.root / "collection.active").exists())
        self.assertEqual(self.state()["wait"]["return_state"], "SMOKE_RUN")
        self.tick_to("ARM_WAIT")
        self.assertNotEqual(old.terminal_path, self.state()["session"]["smoke_prepared"]["terminal_path"])
        self.assertEqual(self.state()["packs"]["alpha"]["attempts_since_resume"], 0)

    def test_reharvest_keeps_loop_owned_flags_before_outcome(self):
        codes = ("registration.after_first_session", "notice.undelivered", "notice.no_unreadable")
        catalog = Catalog({**CATALOG.codes, **{c: {"effect": "DISCLOSE", "blinding": "STRUCTURE"} for c in codes}}, None)
        self.loop.catalog = self.mailer.catalog = catalog
        reg = self.regs["alpha"]
        self.regs["alpha"] = replace(reg, data={**reg.data, "flag_effects": {c: "EXCLUDE_WINDOW" for c in codes}})
        self.desk.lines = [SessionLine("r1-alpha", ("alpha",), harvest_rc=2, window_flags=codes + ("disk.low",))]
        self.tick_to("ROTATE")
        original = (self.root / "attempts.jsonl").read_bytes()
        with patch.object(queue, "outcome", wraps=queue.outcome) as outcome:
            self.loop.control("reharvested", session_id="r1-alpha")
        self.assertEqual(set(outcome.call_args.args[1].window_flags), set(codes))
        self.assertEqual(self.state()["reharvested"]["r1-alpha"]["alpha"]["status"], "not_counting")
        self.assertEqual(queue.counting_ids(self.state(), "alpha"), [])
        self.assertEqual((self.root / "attempts.jsonl").read_bytes(), original)

    def test_no_probe_exception_flags_attempt_and_still_runs(self):
        self.tick_to("ARM_WAIT")
        self.clock.advance(1800)
        with patch.object(self.mailer, "has_no", side_effect=OSError("synthetic no failure")):
            self.tick_to("ROTATE")
        self.assertIn("notice.no_unreadable", self.state()["attempts"][0]["line"]["window_flags"])

    def test_no_probe_reported_failure_flags_attempt(self):
        with patch.object(self.transport, "has_no", side_effect=OSError("synthetic no failure")):
            self.tick_to("ROTATE")
        self.assertIn("notice.no_unreadable", self.state()["attempts"][0]["line"]["window_flags"])

    def test_confirmed_owner_no_survives_probe_record_read_error(self):
        self.tick_to("ARM_WAIT")
        self.clock.advance(1800)
        with patch.object(self.mailer, "has_no", return_value=True), patch.object(self.mailer, "entry", side_effect=OSError("synthetic record read error")):
            self.loop.tick()
        self.assertEqual(self.state()["hold_reason"], "owner_no")
        self.assertEqual(self.state()["state"], "HOLD_LOOP")

    def test_remote_stop_unavailable_flags_attempt(self):
        self.loop.run = lambda argv: SimpleNamespace(returncode=1, stdout="")
        self.tick_to("ROTATE")
        self.assertIn("notice.no_unreadable", self.state()["attempts"][0]["line"]["window_flags"])

    def test_physics_wait_299_second_ticks_measure_twelve_times(self):
        self.loop.tick()
        self.precheck.results = [PrecheckResult(would_refuse=(Hazard("thermal"),))] * 12
        for _ in range(12):
            self.loop.tick()
            self.clock.advance(299)
        self.assertEqual(len(self.precheck.calls), 12)

    def test_physics_wait_intervals_one_remedy_one_mail_at_two_hours(self):
        result = PrecheckResult(would_refuse=(Hazard("disk", "12 J restricted"),), remedies=("disk",))
        self.precheck.results = [result] * 40
        self.loop.tick()
        self.loop.tick()
        self.assertEqual(self.state()["state"], "WAIT_PHYSICS")
        self.assertEqual(self.precheck.remedies, ["disk"])
        for _ in range(24):
            calls = len(self.precheck.calls)
            self.loop.tick()
            self.assertEqual(len(self.precheck.calls), calls)
            self.clock.advance(300)
            self.loop.tick()
        self.assertEqual(len(self.messages("physics_wait_2h")), 1)
        self.assertEqual(self.precheck.remedies, ["disk"])
        self.clock.advance(300)
        self.loop.tick()
        self.assertEqual(len(self.messages("physics_wait_2h")), 1)

    def test_smoke_on_changed_fingerprint_new_pack_and_harvest_fault(self):
        self.tick_to("ROTATE")
        self.assertEqual(len(self.desk.smoke_calls), 1)
        self.precheck.fingerprint = {**self.precheck.fingerprint, "code_commit": "changed"}
        self.tick_to("SMOKE_RUN")
        self.assertEqual(self.state()["session"]["packs"], ["beta"])
        self.tick_to("ROTATE")
        self.loop.state = self.state()
        self.loop.state["harvest_fault"] = True
        loop_module.atomic_state(self.root / "state.json", self.loop.state)
        self.tick_to("SMOKE_RUN")
        self.assertTrue(self.state()["session"]["needs_smoke"])

    def test_changing_hazards_keep_continuous_wait_clock_and_mail_once(self):
        self.loop.tick()
        started = self.clock()
        for minute, hazard in ((0, "contention"), (50, "thermal"), (100, "contention"),
                               (115, "contention"), (125, "contention"), (130, "thermal")):
            self.clock.now = started + minute * 60
            self.precheck.results = [PrecheckResult(would_refuse=(Hazard(hazard),))]
            self.loop.tick()
            with self.subTest(minute=minute):
                self.assertEqual(self.state()["wait"]["since"], started)
                self.assertEqual(self.state()["wait"]["hazard"], hazard)
                self.assertEqual(len(self.messages("physics_wait_2h")), int(minute >= 120))
        self.assertEqual(len([e for e in self.transport.sent if e["kind"] == "physics_wait_2h"]), 1)
        self.clock.advance(300)
        self.loop.tick()
        self.assertEqual(self.state()["state"], "PRECHECK")
        self.assertIsNone(self.state()["wait"])
        self.precheck.results = [PrecheckResult(would_refuse=(Hazard("thermal"),))]
        self.loop.tick()
        self.assertEqual(self.state()["wait"]["since"], self.clock())
        self.assertFalse(self.state()["wait"]["mailed"])
        self.loop.control("hold")
        self.assertIsNone(self.state()["wait"])

    def test_each_offered_remedy_runs_once_per_hazard_per_wait_episode(self):
        self.loop.tick()
        for hazard in ("disk", "sampler", "disk", "sampler"):
            self.precheck.results = [PrecheckResult(would_refuse=(Hazard(hazard),), remedies=(hazard,))]
            self.loop.tick()
            self.clock.advance(300)
        self.assertEqual(self.precheck.remedies, ["disk", "sampler"])
        self.loop.tick()
        self.precheck.results = [PrecheckResult(would_refuse=(Hazard("disk"),), remedies=("disk",))]
        self.loop.tick()
        self.assertEqual(self.precheck.remedies, ["disk", "sampler", "disk"])

    def test_smoke_failure_holds_pack_next_proceeds_same_codes_hold_loop(self):
        self.desk.smokes = [SmokeResult("fail", ("disk.low",)), SmokeResult("fail", ("disk.low",))]
        self.tick_to("NEXT")
        self.loop.tick()
        self.tick_to("SMOKE_DESK")
        self.loop.tick()
        self.assertEqual(self.state()["packs"]["alpha"]["status"], "held")
        self.loop.tick()
        self.assertEqual(self.state()["session"]["packs"], ["beta"])
        self.tick_to("HOLD_LOOP")
        self.assertEqual(len(self.messages("smoke_hold")), 2)

    def test_certain_exclusion_next_pack_same_code_hold_and_thin_margin(self):
        self.precheck.results = [PrecheckResult(certain_exclusion=(Exclusion("model.identity_mismatch"),))] * 2
        self.loop.tick()
        self.loop.tick()
        self.assertEqual(self.state()["state"], "NEXT")
        self.assertEqual(self.driver.launch_calls, [])
        self.loop.tick()
        self.loop.tick()
        self.assertEqual(self.state()["state"], "HOLD_LOOP")
        self.loop.control("resume")
        self.precheck.results = [PrecheckResult(thin_margin=True, predicted_flags=("disk.low",), fingerprint={})]
        self.loop.tick()
        self.loop.tick()
        self.assertTrue(json.loads(self.messages("arm_notice")[0]["body"])["thin_margin"])

    def test_owner_no_local_and_remote_no_session_launch(self):
        self.tick_to("ARM_WAIT")
        self.transport.no = True
        self.clock.advance(1800)
        self.loop.tick()
        self.assertEqual(self.state()["state"], "HOLD_LOOP")
        self.assertFalse(any("-smoke" not in sid for sid in self.driver.launch_calls))
        self.loop.control("resume")
        self.transport.no = False
        self.remote = "hash refs/heads/ops/stop-owner\n"
        self.loop.tick()
        self.loop.tick()
        self.assertEqual(self.state()["state"], "HOLD_LOOP")
        self.loop.control("resume")
        self.remote = ""
        (self.root / "STOP").write_text("owner")
        self.loop.tick()
        self.loop.tick()
        self.assertEqual(self.state()["state"], "HOLD_LOOP")

    def test_structure_defect_holds_and_records_registration_notice_flags(self):
        self.transport.fail = True
        self.regs["alpha"] = replace(self.regs["alpha"], commit_time=self.clock() + 999999)
        self.desk.lines = [SessionLine("r1-alpha", ("alpha",), structure_ok=False, structure_defects=("missing_class",))]
        self.tick_to("HOLD_LOOP")
        attempt = self.state()["attempts"][0]
        self.assertFalse(attempt["structure_ok"])
        self.assertEqual(attempt["outcomes"]["alpha"]["status"], "not_counting")
        self.assertIn("registration.after_first_session", attempt["line"]["window_flags"])
        self.assertIn("notice.undelivered", attempt["line"]["window_flags"])

    def test_harvest_fault_pending_reharvest_counting_append_only(self):
        self.desk.lines = [SessionLine("r1-alpha", ("alpha",), harvest_rc=2, verdict="HARVEST_FAULT")]
        self.tick_to("ROTATE")
        original = (self.root / "attempts.jsonl").read_bytes()
        self.assertEqual(self.state()["attempts"][0]["outcomes"]["alpha"]["status"], "pending_harvest")
        self.loop.control("reharvested", session_id="r1-alpha")
        self.assertEqual(queue.counting_ids(self.state(), "alpha"), ["r1-alpha"])
        self.assertEqual((self.root / "attempts.jsonl").read_bytes(), original)
        self.tick_to("SMOKE_RUN")

    def test_overrun_delivers_once_while_active_defers_wake_never_kills(self):
        self.loop.waker = Waker(self.root, wake_argv=["/usr/bin/true"], run=self.runner)
        self.tick_to("SESSION_RUN")
        self.driver.running_forever = True
        self.loop.tick()
        sent = len(self.transport.sent)
        active_during_send = []
        send = self.transport.send
        def observe_send(entry):
            active_during_send.append((self.root / "collection.active").exists())
            return send(entry)
        self.transport.send = observe_send
        prior = self.mailer.enqueue("loop_hold", "prior", "queued", {"state": "HOLD_LOOP"})
        self.clock.advance(3961)
        self.loop.tick()
        self.assertEqual(self.state()["hold_reason"], "overrun")
        self.assertEqual(len(self.messages("overrun")), 1)
        self.assertEqual(len(self.transport.sent), sent + 2)
        self.assertTrue(self.mailer.entry(prior)["delivered"])
        self.assertEqual(active_during_send, [True, True])
        self.assertEqual(len([e for e in self.transport.sent if e["kind"] == "overrun"]), 1)
        self.assertEqual(len(list((self.root / "wake").glob("*.json"))), 1)
        wake = json.loads(next((self.root / "wake").glob("*.json")).read_text())
        self.assertTrue(wake["job_deferred"])
        self.assertTrue((self.root / "collection.active").exists())
        self.loop.tick()
        self.assertEqual(len(self.transport.sent), sent + 2)
        self.assertFalse(any("kill" in argv or "launchctl" in argv for argv in self.run_calls))
        Path(self.state()["session"]["prepared"]["terminal_path"]).write_text("{}")
        self.loop.control("resume")
        later = self.mailer.enqueue("loop_hold", "later", "manual", {"state": "HOLD_LOOP"})
        (self.root / "collection.active").write_text("synthetic\n100\n")
        self.loop.control("hold")
        self.loop.tick()
        self.assertFalse(self.mailer.entry(later)["delivered"])
        self.assertEqual(len(self.transport.sent), sent + 2)

    def test_crash_after_launch_next_tick_adopts_no_second_job(self):
        self.tick_to("SESSION_RUN")
        real = loop_module.atomic_state
        writes = []
        def crash(path, state):
            writes.append(state["state"])
            if len(writes) == 2:
                raise RuntimeError("synthetic crash after launch")
            return real(path, state)
        with patch.object(loop_module, "atomic_state", side_effect=crash):
            with self.assertRaises(RuntimeError):
                self.loop.tick()
        jobs = len(self.driver.launch_calls)
        self.loop.tick()
        self.assertEqual(len(self.driver.launch_calls), jobs)
        self.loop.tick()
        self.assertEqual(self.state()["state"], "SESSION_DESK")

    def test_lock_and_no_mail_wake_during_collection(self):
        self.root.mkdir(exist_ok=True)
        with (self.root / "loop.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(self.loop.tick(), 0)
            self.assertFalse((self.root / "state.json").exists())
        self.tick_to("SMOKE_RUN")
        self.driver.running_forever = True
        sent = len(self.transport.sent)
        self.loop.tick()
        self.clock.advance(300)
        self.loop.tick()
        self.assertEqual(len(self.transport.sent), sent)
        self.assertFalse((self.root / "wake").exists())

    def test_missing_lane_holds_with_exact_name(self):
        self.loop.lanes = resolve()
        self.loop.tick()
        self.assertEqual(self.state()["hold_reason"], "lane_missing:driver")
        self.assertEqual(self.driver.launch_calls, [])

    def test_missing_launch_does_not_consume_slot(self):
        self.tick_to("ARM_WAIT")
        self.clock.advance(1800)
        self.loop.tick()
        self.driver.launch = lambda prepared: LaneMissing("driver")
        self.loop.tick()
        self.assertEqual(self.state()["state"], "HOLD_LOOP")
        self.assertEqual(self.state()["packs"]["alpha"]["attempts_since_resume"], 0)
        self.assertEqual(self.state()["slots"]["1"], [])

    def test_smoke_physics_wait_and_retry_new_key(self):
        self.desk.smokes = [SmokeResult("physics", ("thermal",)), SmokeResult("pass")]
        self.tick_to("SMOKE_DESK")
        first = self.state()["session"]["smoke_prepared"]
        self.loop.tick()
        self.assertEqual(self.state()["state"], "WAIT_PHYSICS")
        previous = len(self.driver.launch_calls)
        self.loop.tick()
        self.assertEqual(len(self.driver.launch_calls), previous)
        self.clock.advance(300)
        self.loop.tick()
        self.tick_to("ARM_WAIT")
        self.assertEqual(len(self.driver.launch_calls), previous + 1)
        self.assertEqual(self.state()["packs"]["alpha"]["attempts_since_resume"], 0)
        retry = self.state()["session"]["smoke_prepared"]
        self.assertNotEqual(Path(first["plan_path"]).parent, Path(retry["plan_path"]).parent)
        self.assertNotEqual(first["terminal_path"], retry["terminal_path"])

    def test_physics_stop_faults_rotates_and_records_not_counting(self):
        self.desk.lines = [SessionLine("r1-alpha", ("alpha",), physics_stop="thermal")]
        self.tick_to("ROTATE")
        self.assertEqual(self.state()["attempts"][0]["outcomes"]["alpha"], {"status": "physics_stopped", "cause": "thermal"})
        self.assertEqual(len(self.messages("physics_ended_session")), 1)
        self.loop.tick()
        self.loop.tick()
        self.assertEqual(self.state()["session"]["packs"], ["beta"])

    def test_h3_requires_confirmation_for_registered_interleaving(self):
        class Unconfirmed:
            def capabilities(self): return HarvestCapabilities(True, True, False)
        self.loop.regs_source = {"beta": modular("beta", interleave="quad_round_robin")}
        self.loop.lanes = replace(self.loop.lanes, harvest=Unconfirmed())
        self.loop.tick()
        self.assertEqual(self.state()["state"], "NEXT")
        self.assertEqual(self.state()["packs"]["beta"]["hold_reason"], "interleave_unconfirmed:H3")
        self.assertEqual(self.state()["packs"]["beta"]["status"], "held")
        self.assertIsNone(self.state()["session"])
        self.assertEqual(self.driver.prepared, {})
        self.loop.tick()
        self.assertEqual(len(self.messages("loop_hold")), 1)
        self.assertEqual(len(list((self.root / "wake").glob("*.json"))), 1)

    def test_unconfirmed_interleave_holds_beta_and_alpha_proceeds(self):
        class Unconfirmed:
            def capabilities(self): return HarvestCapabilities(True, True, False)
        self.loop.config = {**self.loop.config, "base_order": ["beta", "alpha"]}
        self.loop.regs_source = {"beta": modular("beta", interleave="quad_round_robin"), "alpha": self.regs["alpha"]}
        self.loop.lanes = replace(self.loop.lanes, harvest=Unconfirmed())
        self.loop.tick()
        self.assertEqual(self.state()["state"], "NEXT")
        self.assertEqual(self.state()["packs"]["beta"]["status"], "held")
        self.loop.tick()
        self.assertEqual(self.state()["session"]["packs"], ["alpha"])
        self.tick_to("ROTATE")
        self.assertEqual(len(self.messages("loop_hold")), 1)

    def test_measured_done_physics_stops_still_count_attempts_and_same_cause(self):
        self.loop.regs_source = {"alpha": self.regs["alpha"]}
        self.desk.lines = [SessionLine("r1-alpha", ("alpha",), physics_stop="battery_float"),
                           SessionLine("r2-alpha", ("alpha",), physics_stop="battery_float")]
        status = self.driver.status
        with patch.object(self.driver, "status", side_effect=lambda handle: replace(status(handle), physics_stop="battery_float")):
            for _ in range(2):
                self.tick_to("ROTATE")
                self.loop.tick()
        state = self.state()
        self.assertEqual(state["packs"]["alpha"]["hold_reason"], "same_cause_twice")
        self.assertEqual(state["packs"]["alpha"]["attempts_since_resume"], 2)
        self.assertEqual(state["slots"], {"1": ["alpha"], "2": ["alpha"]})
        self.assertEqual([a["outcomes"]["alpha"]["status"] for a in state["attempts"]], ["physics_stopped"] * 2)

    def test_end_date_short_prints_count_and_empty_queue_waits(self):
        self.loop.regs_source = {}
        self.loop.tick()
        self.assertEqual(self.state()["state"], "NEXT")
        self.loop.regs_source = self.regs
        self.clock.advance(30*86400)
        self.loop.tick()
        self.assertEqual(self.state()["state"], "DONE")
        short = json.loads(self.messages("close")[0]["body"])["short"]
        self.assertEqual(short, {p: 0 for p in self.regs})

    def test_no_mail_or_wake_while_session_running(self):
        self.tick_to("SESSION_RUN")
        self.driver.running_forever = True
        sent = len(self.transport.sent)
        self.loop.tick()
        self.clock.advance(300)
        self.loop.tick()
        self.assertEqual(len(self.transport.sent), sent)
        self.assertFalse((self.root / "wake").exists())

    def test_wake_record_dedup_and_optional_job_deferred_while_active(self):
        calls = []
        waker = Waker(self.root, wake_argv=["/usr/bin/true"], run=lambda argv: calls.append(argv))
        (self.root / "collection.active").write_text("synthetic\n100\n")
        first = waker.wake("overrun", {"session_id": "s"})
        self.assertTrue(first["job_deferred"])
        self.assertEqual(calls, [])
        (self.root / "collection.active").unlink()
        second = waker.wake("overrun", {"session_id": "s"})
        self.assertEqual(first["seq"], second["seq"])
        self.assertEqual(calls[0][:2], ["launchctl", "bootstrap"])
        job = plistlib.loads(Path(calls[0][-1]).read_bytes())
        self.assertEqual(job["ProgramArguments"], ["/usr/bin/true"])
        waker.wake("overrun", {"session_id": "s"})
        self.assertEqual(len(calls), 1)

    def test_precision_counting_minimum_and_h3_unconfirmed(self):
        data = dict(self.regs["alpha"].data)
        data["stopping"] = {**data["stopping"], "precision": {"quantity": "registered", "max_half_width_J": 1, "evaluator": "test:bit"}}
        self.regs["alpha"] = replace(self.regs["alpha"], data=data)
        self.loop.regs_source = {"alpha": self.regs["alpha"]}
        self.tick_to("DONE")
        self.assertEqual(len(self.state()["attempts"]), 2)
        self.assertEqual(len(self.analysis.calls), 1)

    def test_deferred_wakes_bootstrap_once_on_first_marker_free_tick_after_flush(self):
        calls = []
        key = self.mailer.enqueue("loop_hold", "s", "wait", {"state": "HOLD_LOOP"})
        def run(argv):
            self.assertTrue(self.mailer.entry(key)["delivered"])
            calls.append(argv)
        self.loop.waker = Waker(self.root, wake_argv=["/usr/bin/true"], run=run)
        self.loop.state = self.state()
        self.loop.state["state"] = "HOLD_LOOP"
        loop_module.atomic_state(self.root / "state.json", self.loop.state)
        active = self.root / "collection.active"
        active.write_text("synthetic\n100\n")
        for reason in ("overrun", "lane_missing"):
            self.loop.waker.wake(reason, {"session_id": "s"})
        self.loop.tick()
        self.assertEqual(calls, [])
        active.unlink()
        self.loop.tick()
        self.assertEqual(len(calls), 2)
        for argv in calls:
            self.assertEqual(argv[:2], ["launchctl", "bootstrap"])
            self.assertEqual(plistlib.loads(Path(argv[-1]).read_bytes())["ProgramArguments"], ["/usr/bin/true"])
        self.loop.tick()
        self.assertEqual(len(calls), 2)
        records = [json.loads(p.read_text()) for p in (self.root / "wake").glob("*.json")]
        self.assertTrue(all(r["bootstrap_attempted"] and not r["job_deferred"] for r in records))

    def test_cli_live_runner_draft_reasons_github_delivery_and_stop_probe(self):
        repo, loop_root = self.root / "repo", self.root / "loop"
        loop_catalog = json.loads((ROOT / "configs/b6/loop.json").read_text())["flag_catalog"]
        for relative in ("configs/b6/loop.json", "configs/campaigns/v5_claim_25g83/flag_catalog.json", loop_catalog,
                         *(f"configs/b6/packs/{p}/registration.json" for p in ("alpha", "beta", "gamma"))):
            target = repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        config = json.loads((repo / "configs/b6/loop.json").read_text())
        mailer = Mailer(loop_root, CATALOG, clock=lambda: 0)
        key = mailer.enqueue("loop_hold", "prior", None, {"state": "HOLD_LOOP"})
        loops, calls = [], []
        def factory(*args, **kwargs):
            loop = loop_module.Loop(*args, **kwargs)
            loops.append(loop)
            return loop
        def run(argv, **kwargs):
            self.assertIn(argv[0], {"git", "gh"})
            self.assertFalse(any("@" in arg for arg in argv))
            self.assertEqual(kwargs, {"capture_output": True, "text": True, "timeout": 120, "check": False})
            calls.append(argv)
            output = json.dumps([{"number": 9}]) if argv[0] == "gh" and "issues?" in argv[2] else ""
            return SimpleNamespace(returncode=0, stdout=output)
        with patch.object(cli_module.subprocess, "run", side_effect=run):
            self.assertEqual(main(["--repo-root", str(repo), "--loop-root", str(loop_root), "tick"], factory=factory), 0)
            loop = loops[0]
            self.assertFalse(loop._stop())
        state = loop.read_state()
        self.assertEqual(state["packs"], {})
        self.assertIsNone(state["session"])
        self.assertEqual(state["pack_not_open"], {
            f"configs/b6/packs/{p}/registration.json": ["draft"] for p in ("alpha", "beta", "gamma")})
        self.assertTrue(mailer.entry(key)["delivered"])
        self.assertEqual(loop.mailer.transport.repo, config["github_repo"])
        self.assertIsInstance(loop.lanes.driver, type(resolve().driver))
        self.assertTrue(any(argv[0] == "gh" for argv in calls))
        self.assertTrue(any("ls-remote" in argv for argv in calls))

    def test_cli_live_runner_timeout_returns_failure(self):
        argv = ["git", "status"]
        with patch.object(cli_module.subprocess, "run", side_effect=subprocess.TimeoutExpired(argv, 120)) as run:
            result = cli_module.live_run(argv)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        run.assert_called_once_with(argv, capture_output=True, text=True, timeout=120, check=False)

    def test_guard_skip_pass_terminal_and_overrun_plist_and_cli_override(self):
        template = (ROOT / "configs/launchd/com.joulewise.b6loop.plist.template").read_text()
        plist = plistlib.loads(template.replace("__REPO_ROOT__", str(ROOT)).replace("__LOOP_ROOT__", str(self.root)).encode())
        self.assertEqual(plist["StartInterval"], 300)
        self.assertEqual(plist["ProcessType"], "Background")
        self.assertTrue(plist["RunAtLoad"])
        self.assertTrue(plist["ProgramArguments"][1].endswith("b6_loop_guard.zsh"))
        active, terminal, marker = self.root / "collection.active", self.root / "terminal", self.root / "passed"
        # Sole non-Git subprocess exception: the guard execs harmless printf.
        environment = {**os.environ, "JW_B6_LOOP_ROOT": str(self.root),
                       "JW_B6_LOOP_TICK": f"/usr/bin/touch {marker}"}
        def guard():
            result = subprocess.run(["/bin/zsh", str(ROOT / "scripts/b6_loop_guard.zsh")], env=environment,
                                    capture_output=True, text=True, timeout=0.5)
            self.assertEqual(result.returncode, 0, result.stderr)
        active.write_text(f"{terminal}\n3600\n")
        guard()
        self.assertFalse(marker.exists())
        terminal.write_text("{}")
        guard()
        self.assertTrue(marker.exists())
        marker.unlink()
        terminal.unlink()
        os.utime(active, (1, 1))
        guard()
        self.assertTrue(marker.exists())
        marker.unlink()
        active.unlink()
        guard()
        self.assertTrue(marker.exists())
        factories = []
        def factory(repo, root, **kwargs):
            factories.append(root)
            return SimpleNamespace(read_state=lambda: {})
        with patch("builtins.print"):
            self.assertEqual(main(["status", "--loop-root", str(self.root)], factory=factory), 0)
            with patch.dict(os.environ, {"JW_B6_LOOP_ROOT": str(self.root)}):
                self.assertEqual(main(["status"], factory=factory), 0)
        self.assertEqual(factories, [str(self.root)] * 2)
