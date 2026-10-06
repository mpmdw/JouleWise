"""The HAZARD_PACK branch of scripts/run_night.py, driven end to end.

The driver, the plan writer, the chain bytes and the zsh run are production
code. Fakes stand only at hardware and other-lane seams: the hazard arm (L1),
the lineage writer (L3), the monitor and collector programs (L1, L4), the G10
program (L8), the network-time setter, the free-space reading, the agent census
and the courier; the chain's tools are the fake measurement checkout's.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest
from pathlib import Path
from unittest import mock

from joulewise import night_gate
from joulewise.b5 import chain as b5_chain
from joulewise.b5 import driver as b5_driver
from joulewise.b5 import plan as b5_plan
from tests.fixtures.b5_plan import fake_window

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/run_night.py"
SIX = night_gate.HAZARD_MODULES


def load_driver():
    spec = importlib.util.spec_from_file_location("run_night_b5_test_module", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def probe(argv, *, exit_code=1, stdout=""):
    return night_gate.ProbeResult(tuple(argv), exit_code, stdout, "", time.monotonic_ns())


class Census:
    """The agent census seam: clean (exit 1, empty) unless a response is queued."""

    def __init__(self):
        self.responses: list[night_gate.ProbeResult] = []
        self.calls = 0

    def run(self, argv):
        argv = tuple(argv)
        if argv == night_gate.AGENT_CENSUS_ARGV:
            self.calls += 1
            if self.responses:
                return self.responses.pop(0)
            return probe(argv)
        raise AssertionError(f"unexpected probe {argv}")

    def probes(self):
        return night_gate.Probes(run=self.run, now_epoch_s=time.time, monotonic_ns=time.monotonic_ns,
                                 read_text=lambda path: Path(path).read_text(),
                                 checkout_head=lambda: "a" * 40, measurement_head=lambda _root: "b" * 40)


class FakeArm:
    """The hazard arm seam, in the section 2.2 order, with injectable verdicts.

    Instant reads (battery, thermal, disk, clock frequency) come before network
    time OFF; the instrument cadence probe and the contention dwell come after
    OFF and the record-only collectors.
    """

    INSTANT = ("battery", "thermal", "disk", "clock")

    def __init__(self, *, verdicts=None, raises=None, skip_hooks=False, raw=None):
        self.verdicts = dict(verdicts or {})
        self.raises = raises
        self.skip_hooks = skip_hooks
        self.raw = raw
        self.contexts = []
        self.hook_results = {}

    def __call__(self, context):
        self.contexts.append(context)
        if self.raises is not None:
            raise self.raises
        if self.raw is not None:
            return self.raw
        context.record_root.mkdir(parents=True, exist_ok=True)
        verdicts = {name: b5_driver.PASS for name in SIX}

        def refuse_if_any(modules):
            hit = {name: self.verdicts[name] for name in modules if self.verdicts.get(name, "PASS") != "PASS"}
            if not hit:
                return None
            verdicts.update(hit)
            path = context.record_root / "arm.json"
            path.write_text(json.dumps({"verdicts": verdicts}))
            return {"go": False, "verdicts": verdicts, "reasons": [f"{k} {v}" for k, v in hit.items()],
                    "record_path": str(path)}

        refused = refuse_if_any(self.INSTANT)
        if refused:
            return refused
        if not self.skip_hooks:
            self.hook_results["off"] = context.network_time_off()
            self.hook_results["collectors"] = context.record_only_collectors()
        refused = refuse_if_any(("instrument", "contention"))
        if refused:
            return refused
        path = context.record_root / "arm.json"
        path.write_text(json.dumps({"verdicts": verdicts}))
        return {"go": True, "verdicts": verdicts, "reasons": [], "record_path": str(path)}


class NetworkTime:
    """The OFF setter seam: a state file; OFF while OFF prints the 10-01 0137Z wording."""

    def __init__(self, root: Path, *, initial="off", stdout=None, returncode=0):
        self.state = root / "network-time-state"
        self.state.write_text(initial)
        self.stdout = stdout
        self.returncode = returncode
        self.calls = 0

    def run(self, argv, timeout):
        self.calls += 1
        was = self.state.read_text()
        self.state.write_text("off")
        stdout = self.stdout if self.stdout is not None else (
            "Network Time is already off.\n" if was == "off" else "setusingnetworktime: Off\n")
        now = b5_driver.stamp()
        return b5_driver.CommandResult(tuple(argv), self.returncode, stdout, "", False, None, now, now)


class Harness:
    def __init__(self, test: unittest.TestCase, pack="alpha", *, g10=True, behavior=None, arm=None):
        self.test = test
        self.temporary = tempfile.TemporaryDirectory(prefix=f"b5-driver-{pack}-")
        test.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.measurement = fake_window.build_checkout(self.root, behavior=behavior)
        t0 = (int(time.time()) // 60) * 60
        self.record = b5_plan.write_window_plan(
            fake_window.inputs(self.root, self.measurement, pack, plan_id=f"b5-{pack}-1", t0_epoch_s=t0, g10=g10),
            settle_s=0, pack_digest=lambda _root: "e" * 64, threshold_defaults=fake_window.threshold_defaults)
        self.plan_path = Path(self.record["plan"]["path"])
        self.plan = night_gate.NightPlan.from_mapping(json.loads(self.plan_path.read_text()))
        self.custody = Path(self.plan.custody_root)
        self.night = self.custody / "night"
        self.home = self.root / "home"
        (self.home / "Library/LaunchAgents").mkdir(parents=True)
        self.census = Census()
        self.network = NetworkTime(self.root)
        self.arm = arm or FakeArm()
        self.lineage_calls = []
        self.flags = []
        self.free_bytes = 10 ** 13
        self.courier = self.root / "courier"
        self.courier.write_text("#!/bin/sh\nexit 0\n")
        self.courier.chmod(0o755)
        self.collector_argv = [sys.executable, "-c", "print('collected')"]
        self.collectors_factory = lambda request: list(self.collector_argv)
        self.monitor_argv = [sys.executable, "-c", "import time; time.sleep(600)"]
        self.g10_source = ("import json, pathlib, sys; night = pathlib.Path(sys.argv[1]); "
                           "journal = (night / 'monitor_supervision.jsonl').read_text(); "
                           "(night / 'g10.json').write_text(json.dumps({'result': 'DISCHARGED', "
                           "'monitor_running': '\"start\"' in journal and '\"stop\"' not in journal}))")
        self.driver = load_driver()
        self.driver.make_probes = lambda: self.census.probes()
        self.driver._durable_record = mock.Mock(return_value=None)
        self.sent = {"attempted": 1, "sent": True, "heartbeat_seen": True, "last_error": None}
        self.driver.run_courier = mock.Mock(return_value=self.sent)
        self.driver._resolve_courier_bin = lambda _bin: (self.courier, None, None)
        self.driver._hazard_seams = lambda: self.seams()
        patcher = mock.patch.dict(os.environ, {"HOME": str(self.home)})
        patcher.start()
        test.addCleanup(patcher.stop)
        home = mock.patch.object(Path, "home", return_value=self.home)
        home.start()
        test.addCleanup(home.stop)

    def run_command(self, argv, timeout):
        if tuple(argv) == b5_driver.NETWORK_TIME_OFF_ARGV:
            return self.network.run(argv, timeout)
        return b5_driver.run_bounded(argv, timeout)

    def publish_lineage(self, request):
        self.lineage_calls.append(request)
        return {"claim": str(request.claim_runs_root), "bound": str(request.bound_runs_root)}

    def emit_flag(self, custody, fields):
        flag = b5_driver.build_flag(fields, boot_session_uuid="BOOT")
        self.flags.append(flag)
        path = Path(custody) / "flags" / b5_driver.DRIVER_FLAGS
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as handle:
            handle.write(json.dumps(flag, sort_keys=True) + "\n")

    def seams(self):
        return b5_driver.Seams(
            arm=self.arm, publish_lineage=self.publish_lineage,
            monitor_argv=lambda request: list(self.monitor_argv),
            collectors_argv=lambda request: self.collectors_factory(request),
            g10_argv=lambda night, t: [sys.executable, "-c", self.g10_source, str(night)],
            run_command=self.run_command, disk_free_bytes=lambda path: self.free_bytes,
            emit_flag=self.emit_flag, boot_session_uuid=lambda: "BOOT")

    def run(self, **keywords):
        return self.driver.run_night(self.plan_path, **keywords)

    def result(self):
        return json.loads((self.night / "result.json").read_text())

    def hazard(self):
        return json.loads((self.night / b5_driver.HAZARD_RESULT).read_text())

    def custody_digests(self):
        window = self.plan.hazard_window
        return {
            "ledger": fake_window.sha256(Path(window["bindings"]["ledger_path"])),
            "launch_agents": fake_window.tree_digest(self.home / "Library/LaunchAgents"),
            "runs_and_backups": fake_window.tree_digest(
                Path(window["runs_roots"]["claim"]), Path(window["runs_roots"]["bound"]),
                Path(window["bindings"]["claim_backup_destination"]),
                Path(window["bindings"]["bound_backup_destination"])),
            "network_time": self.network.state.read_text(),
        }

    def replace_chain(self, text):
        chain = Path(self.plan.chain_path)
        chain.write_text(text)
        Path(self.plan.chain_sha256_path).write_bytes(b5_chain.sidecar_bytes(chain.read_bytes(), chain.name))


class HazardRefusalTests(unittest.TestCase):
    """Each hazard REFUSE (or UNMEASURED) is NULL: nothing launched, nothing changed."""

    def assert_null(self, harness, *, off_expected: bool):
        before = harness.custody_digests()
        code = harness.run()
        self.assertEqual(harness.driver.EXIT_REFUSED, code)
        result = harness.result()
        self.assertEqual("REFUSED", result["verdict"])
        self.assertFalse((harness.night / "chain.started").exists())
        self.assertEqual(before, harness.custody_digests())
        self.assertEqual([], fake_window.calls(harness.measurement))   # no chain tool ever ran
        self.assertEqual([], harness.lineage_calls)
        self.assertFalse((harness.night / b5_driver.MONITOR_JOURNAL).exists())
        self.assertFalse((harness.night / b5_driver.INVENTORY_RECORD).exists())
        self.assertEqual(1 if off_expected else 0, harness.network.calls)
        refusal = json.loads((harness.night / "refusal.json").read_text())
        self.assertEqual([], harness.driver.validate_refusal(refusal))
        return result, refusal

    def test_every_hazard_refuse_and_unmeasured_is_a_null_window(self):
        for module in SIX:
            for status in (b5_driver.REFUSE, b5_driver.UNMEASURED):
                with self.subTest(module=module, status=status):
                    harness = Harness(self, arm=FakeArm(verdicts={module: status}))
                    result, refusal = self.assert_null(harness, off_expected=module not in FakeArm.INSTANT)
                    self.assertEqual(b5_driver.REFUSED_HAZARD, result["aborted_reason"])
                    self.assertEqual(status, refusal["refusal"]["evidence"]["verdicts"][module])
                    decision = json.loads((harness.night / b5_driver.ARM_DECISION).read_text())
                    self.assertFalse(decision["go"])
                    self.assertEqual([module], decision["not_pass"])
                    hazard = harness.hazard()
                    self.assertEqual(("REFUSED", "arm"), (hazard["verdict"], hazard["stage_reached"]))

    def test_an_arm_that_raises_or_answers_unreadably_is_unmeasured(self):
        cases = {"raises": FakeArm(raises=RuntimeError("probe exploded")),
                 "go without verdicts": FakeArm(raw={"go": True}),
                 "garbage": FakeArm(raw=["GO"])}
        for label, arm in cases.items():
            with self.subTest(case=label):
                harness = Harness(self, arm=arm)
                result, _ = self.assert_null(harness, off_expected=False)
                self.assertEqual(b5_driver.REFUSED_HAZARD, result["aborted_reason"])

    def test_an_arm_that_never_returns_is_null_and_nothing_launches(self):
        # Review finding (L2 guards a): an arm that does not return within
        # t0_stage_cap_s + ARM_RETURN_GRACE_S is NULL, never GO.
        release = threading.Event()
        self.addCleanup(release.set)

        class BlockingArm(FakeArm):
            def __call__(self, context):
                self.contexts.append(context)
                release.wait(60)
                return {"go": True, "verdicts": {name: "PASS" for name in SIX}}
        harness = Harness(self, g10=False, arm=BlockingArm())
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        plan = json.loads(harness.plan_path.read_text())
        plan["hazard_window"]["t0_stage_cap_s"] = 0.2
        harness.plan_path.write_text(json.dumps(plan))
        grace = mock.patch.object(b5_driver, "ARM_RETURN_GRACE_S", 0.3)
        grace.start()
        self.addCleanup(grace.stop)
        started = time.monotonic()
        result, refusal = self.assert_null(harness, off_expected=False)
        self.assertLess(time.monotonic() - started, 30)
        self.assertEqual(1, len(harness.arm.contexts))
        self.assertEqual(b5_driver.REFUSED_HAZARD, result["aborted_reason"])
        decision = json.loads((harness.night / b5_driver.ARM_DECISION).read_text())
        self.assertEqual((False, "timeout"), (decision["go"], decision["arm_error"]))
        self.assertTrue(any("did not return" in reason for reason in decision["reasons"]))
        self.assertEqual(sorted(SIX), decision["not_pass"])

    def test_agent_census_refuses_before_any_action(self):
        harness = Harness(self)
        harness.census.responses.append(probe(night_gate.AGENT_CENSUS_ARGV, exit_code=0, stdout="4242 claude\n"))
        result, _ = self.assert_null(harness, off_expected=False)
        self.assertEqual("night_refused_agent_present", result["aborted_reason"])
        self.assertEqual([], harness.arm.contexts)
        self.assertFalse((harness.night / b5_driver.ARM_DECISION).exists())
        self.assertFalse((harness.night / b5_driver.NETWORK_TIME_ACTION).exists())

    def test_final_census_before_launch_refuses_without_publishing(self):
        harness = Harness(self)
        harness.census.responses += [probe(night_gate.AGENT_CENSUS_ARGV),
                                     probe(night_gate.AGENT_CENSUS_ARGV, exit_code=0, stdout="7 codex\n")]
        result, _ = self.assert_null(harness, off_expected=True)
        self.assertEqual("night_refused_agent_present", result["aborted_reason"])
        self.assertEqual("final_census", harness.hazard()["stage_reached"])


class ArmRecordTests(unittest.TestCase):
    def test_arm_decision_is_unchanged_when_every_collector_raises_or_times_out(self):
        for label in ("raises", "times out", "exits nonzero"):
            with self.subTest(case=label):
                harness = Harness(self, g10=False)
                harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
                patches = []
                if label == "raises":
                    def boom(_request):
                        raise RuntimeError("collector package missing")
                    harness.collectors_factory = boom
                elif label == "times out":
                    harness.collector_argv = [sys.executable, "-c", "import time; time.sleep(30)"]
                    patches.append(mock.patch.object(b5_driver, "COLLECTOR_TIMEOUT_S", 0.5))
                else:
                    harness.collector_argv = [sys.executable, "-c", "raise SystemExit(7)"]
                for item in patches:
                    item.start()
                    self.addCleanup(item.stop)
                self.assertEqual(harness.driver.EXIT_GO, harness.run())
                self.assertEqual("GO", harness.result()["verdict"])
                self.assertTrue((harness.night / "chain.started").exists())
                record = json.loads((harness.night / b5_driver.COLLECTORS_RECORD).read_text())
                self.assertIn("collector_error", record)
                decision = json.loads((harness.night / b5_driver.ARM_DECISION).read_text())
                self.assertTrue(decision["go"])

    def test_the_10_01_already_off_output_arms_and_is_recorded(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        action = json.loads((harness.night / b5_driver.NETWORK_TIME_ACTION).read_text())
        self.assertEqual("Network Time is already off.\n", action["stdout"])
        self.assertEqual(list(b5_driver.NETWORK_TIME_OFF_ARGV), action["argv"])
        flag = next(item for item in harness.flags if item["code"] == "network_time.off_output")
        self.assertEqual("Network Time is already off.\n", flag["observed"]["stdout"])

    def test_off_wording_and_return_code_are_never_read(self):
        harness = Harness(self, g10=False)
        harness.network.stdout = "You need administrator access to run this tool... exiting!\n"
        harness.network.returncode = 1
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertTrue((harness.night / "chain.started").exists())

    def test_hooks_the_arm_skipped_still_run_before_launch(self):
        harness = Harness(self, g10=False, arm=FakeArm(skip_hooks=True))
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertEqual(1, harness.network.calls)
        self.assertTrue((harness.night / b5_driver.COLLECTORS_RECORD).is_file())
        diagnostics = harness.hazard()["diagnostics"]
        self.assertTrue(any("without running network time OFF" in item for item in diagnostics))


class LaunchTests(unittest.TestCase):
    def test_chain_digest_mismatch_is_a_flag_and_the_chain_runs(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        Path(harness.plan.chain_path).write_text("#!/bin/zsh -f\n# edited after sealing\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertTrue((harness.night / "chain.exited").exists())
        flag = next(item for item in harness.flags if item["code"] == "code.executed_differs_from_sealed")
        self.assertEqual("night_chain_digest_mismatch", flag["source"]["legacy_code"])
        self.assertEqual(("CODE_IDENTITY", "NUMBER"), (flag["family"], flag["klass"]))
        self.assertFalse(harness.hazard()["chain"]["matches_sidecar"])

    def test_lineage_failure_is_a_flag_and_the_chain_runs(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")

        def broken(request):
            raise RuntimeError("window_lineage unavailable")
        harness.publish_lineage = broken
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertIn("records.lineage_formality", [item["code"] for item in harness.flags])
        self.assertFalse(json.loads((harness.night / b5_driver.LINEAGE_RECORD).read_text())["published"])

    def test_lineage_is_published_into_both_runs_roots_after_go_and_before_launch(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\ntest ! -e \"$NIGHT_DIR/never\" && exit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        request = harness.lineage_calls[0]
        roots = harness.plan.hazard_window["runs_roots"]
        self.assertEqual((Path(roots["claim"]), Path(roots["bound"])), (request.claim_runs_root, request.bound_runs_root))
        self.assertEqual("BOOT", request.boot_session_uuid)
        self.assertTrue(request.arm_record_path.name == "arm.json")

    def test_disk_low_stops_the_chain_and_is_recorded(self):
        harness = Harness(self)
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 60\n")
        harness.free_bytes = 5 * 1024 ** 3
        code = harness.run()
        self.assertEqual(harness.driver.EXIT_ABORTED, code)
        result = harness.result()
        self.assertEqual(("ABORTED", b5_driver.STOPPED_DISK_LOW), (result["verdict"], result["aborted_reason"]))
        self.assertTrue((harness.night / "chain.exited").exists())
        refusal = json.loads((harness.night / "refusal.json").read_text())
        self.assertEqual([], harness.driver.validate_refusal(refusal))
        self.assertIn("disk.low", [item["code"] for item in harness.flags])
        hazard = harness.hazard()
        self.assertFalse(hazard["g10"]["ran"])
        self.assertTrue(hazard["monitor"]["stop"]["proven_stopped"])

    def test_in_window_agent_census_still_aborts_the_chain(self):
        harness = Harness(self)
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 60\n")
        harness.census.responses += [probe(night_gate.AGENT_CENSUS_ARGV), probe(night_gate.AGENT_CENSUS_ARGV),
                                     probe(night_gate.AGENT_CENSUS_ARGV, exit_code=0, stdout="99 claude\n")]
        self.assertEqual(harness.driver.EXIT_ABORTED, harness.run())
        self.assertEqual("night_aborted_agent_present", harness.result()["aborted_reason"])
        self.assertFalse(harness.hazard()["g10"]["ran"])

    def test_survivors_of_a_natural_exit_are_proven_gone_before_the_exit_is_recorded(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 120 &\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        census = json.loads((harness.night / "chain.exit-census.json").read_text())
        self.assertFalse(census["absent"])
        self.assertTrue(census["proven"])
        self.assertTrue(any("sleep" in line for line in census["survivors"]))
        self.assertTrue((harness.night / "chain.exited").exists())

    def test_monitor_keeps_journaling_while_chain_termination_is_unproven(self):
        # Review finding (L2 guards b): when the chain's process group is not
        # proven gone, the monitor is left running for the dead-man and no
        # stop is recorded.
        harness = Harness(self, g10=True)
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 120 &\nexit 0\n")
        attempts = []

        def unproven(process, *args, **kwargs):
            attempts.append(kwargs.get("pgid"))
            return False
        harness.driver._terminate_process_group = unproven

        def cleanup():
            for line in (harness.night / b5_driver.MONITOR_JOURNAL).read_text().splitlines():
                event = json.loads(line)
                if event.get("pgid"):
                    with contextlib.suppress(ProcessLookupError, PermissionError):
                        os.killpg(event["pgid"], signal.SIGKILL)
            for pgid in attempts:
                with contextlib.suppress(ProcessLookupError, PermissionError, TypeError):
                    os.killpg(pgid, signal.SIGKILL)
        self.addCleanup(cleanup)
        # Unproven termination withholds the courier (allow_courier=False).
        self.assertEqual(harness.driver.EXIT_COURIER_FAILED, harness.run())
        self.assertTrue(attempts)
        self.assertTrue((harness.night / "chain.unkilled").exists())
        hazard = harness.hazard()
        self.assertFalse(hazard["chain"]["termination_proven"])
        self.assertTrue(hazard["monitor"]["left_running"])
        self.assertIsNone(hazard["monitor"]["stop"])
        self.assertEqual((False, "chain termination not proven"), (hazard["g10"]["ran"], hazard["g10"]["reason"]))
        events = [json.loads(line) for line in (harness.night / b5_driver.MONITOR_JOURNAL).read_text().splitlines()]
        self.assertEqual("start", events[0]["event"])
        self.assertNotIn("stop", [event["event"] for event in events])
        os.killpg(events[0]["pgid"], 0)   # the monitor's group is still alive
        self.assertEqual("REFUSED", harness.result()["verdict"])

    def test_monitor_that_dies_is_restarted_and_the_gap_recorded(self):
        harness = Harness(self, g10=False)
        harness.monitor_argv = [sys.executable, "-c", "raise SystemExit(3)"]
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 4\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        monitor = harness.hazard()["monitor"]
        self.assertGreaterEqual(monitor["restarts"], 2)
        self.assertGreaterEqual(len(monitor["gaps"]), 2)
        events = [json.loads(line)["event"] for line in
                  (harness.night / b5_driver.MONITOR_JOURNAL).read_text().splitlines()]
        self.assertEqual("start", events[0])
        self.assertIn("restart", events)
        self.assertEqual("stop", events[-1])

    def test_monitor_runs_in_its_own_group_and_is_proven_stopped(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 2\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        start = json.loads((harness.night / b5_driver.MONITOR_JOURNAL).read_text().splitlines()[0])
        stop = harness.hazard()["monitor"]["stop"]
        self.assertTrue(stop["was_running"] and stop["group_absent"] and stop["proven_stopped"])
        with self.assertRaises(ProcessLookupError):
            os.killpg(start["pgid"], 0)

    def test_g10_runs_after_the_chain_with_the_monitor_still_journaling(self):
        harness = Harness(self, g10=True)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        g10 = json.loads((harness.night / b5_driver.G10_RECORD).read_text())
        self.assertTrue(g10["monitor_running"])
        driver_record = json.loads((harness.night / b5_driver.G10_DRIVER_RECORD).read_text())
        self.assertEqual(0, driver_record["returncode"])
        self.assertEqual("DISCHARGED", harness.hazard()["g10"]["result"])
        chain_exit = json.loads((harness.night / "chain.exited").read_text())
        self.assertLess(chain_exit["epoch_s"], driver_record["started"]["wall_s"])

    def test_rehearse_never_runs_a_hazard_window(self):
        harness = Harness(self)
        harness.run(rehearsal=True)
        self.assertEqual([], harness.arm.contexts)
        self.assertFalse((harness.night / "chain.started").exists())
        result = harness.result()
        self.assertEqual(("REFUSED", "night_receipt_class_invalid"), (result["verdict"], result["aborted_reason"]))

    def test_rerun_after_an_arm_is_refused_without_a_second_arm(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        calls = len(harness.arm.contexts)
        self.assertEqual(harness.driver.EXIT_REFUSED, harness.run())
        self.assertEqual(calls, len(harness.arm.contexts))


class CourierPayloadTests(unittest.TestCase):
    """For this class the courier carries structure only: no runs-root file, no chain log."""

    def test_durable_record_and_courier_prompt_carry_structure_only(self):
        harness = Harness(self, g10=True)
        driver = harness.driver
        real = load_driver()
        driver._durable_record = real._durable_record
        driver.run_courier = real.run_courier
        prompt_file = harness.root / "courier-prompt.txt"
        harness.courier.write_text("#!/bin/sh\nprintf '%s' \"$2\" > " + str(prompt_file) +
                                   "\ntouch " + str(harness.night / "courier.sent") + "\nexit 0\n")
        observed_run = driver.t0_rehearsal.observed_run

        def fake_git(argv, **kwargs):
            argv = [str(item) for item in argv]
            if argv[0] != "git":
                return observed_run(argv, **kwargs)
            if argv[:2] == ["git", "clone"]:
                Path(argv[-1]).mkdir(parents=True)
            stdout = "https://example.invalid/repo.git\n" if "get-url" in argv else ""
            return subprocess.CompletedProcess(argv, 0, stdout, "")

        patcher = mock.patch.object(driver.t0_rehearsal, "observed_run", side_effect=fake_git)
        patcher.start()
        self.addCleanup(patcher.stop)
        code = harness.run()
        self.assertEqual(driver.EXIT_GO, code, harness.result())
        published = harness.custody / "results-clone/docs/process_traces/night-results" / harness.plan.plan_id
        names = sorted(path.name for path in published.rglob("*") if path.is_file())
        self.assertIn("hazard_result.json", names)
        self.assertIn("result.json", names)
        for forbidden in ("chain.stdout.log", "chain.stderr.log", "chain-stages.jsonl", "monitor.stdout.log", "driver.jsonl"):
            self.assertNotIn(forbidden, names)
        runs = {path.name for root in harness.plan.hazard_window["runs_roots"].values()
                for path in Path(root).rglob("*")}
        self.assertFalse(set(names) & (runs - {"result.json"}))
        # No published file is a copy of anything under a runs root (bundles, logs, bounds).
        run_digests = {hashlib.sha256(path.read_bytes()).hexdigest()
                       for root in harness.plan.hazard_window["runs_roots"].values()
                       for path in Path(root).rglob("*") if path.is_file()}
        for path in published.rglob("*"):
            if path.is_file():
                self.assertNotIn(hashlib.sha256(path.read_bytes()).hexdigest(), run_digests, path.name)
        prompt = prompt_file.read_text()
        self.assertIn("HAZARD_PACK window", prompt)
        self.assertIn("Never open, quote or summarize chain or campaign logs", prompt)
        for root in harness.plan.hazard_window["runs_roots"].values():
            self.assertNotIn(root, prompt)


class DryArmTests(unittest.TestCase):
    def test_dry_arm_with_an_agent_alive_refuses_at_the_census_before_any_action(self):
        harness = Harness(self)
        harness.census.responses.append(probe(night_gate.AGENT_CENSUS_ARGV, exit_code=0, stdout="1 claude\n"))
        before = harness.custody_digests()
        code = harness.driver._main(["run", "--plan", str(harness.plan_path), "--dry-arm"])
        self.assertEqual(harness.driver.EXIT_REFUSED, code)
        self.assertEqual([], harness.arm.contexts)
        self.assertEqual(0, harness.network.calls)
        self.assertEqual(before, harness.custody_digests())
        self.assertFalse(harness.night.exists())
        record = json.loads(next((harness.custody / "dry-arm").rglob("dry-arm.json")).read_text())
        self.assertEqual(("REFUSED", "census", False), (record["verdict"], record["stage"], record["arm_ran"]))

    def test_dry_arm_without_agents_arms_but_never_launches(self):
        harness = Harness(self)
        before = harness.custody_digests()
        self.assertEqual(0, harness.run(dry_arm=True))
        self.assertEqual(1, len(harness.arm.contexts))
        self.assertTrue(harness.arm.contexts[0].dry_arm)
        self.assertNotEqual(harness.custody / "hazards", harness.arm.contexts[0].record_root)
        self.assertFalse(harness.night.exists())
        self.assertEqual([], harness.lineage_calls)
        self.assertEqual([], fake_window.calls(harness.measurement))
        self.assertEqual(before, harness.custody_digests())
        self.assertFalse((harness.custody / "flags").exists())

    def test_dry_arm_refuses_other_classes(self):
        driver = load_driver()
        with tempfile.TemporaryDirectory() as directory:
            plan = Path(directory) / "plan.json"
            plan.write_text(json.dumps({"receipt_class": "DIAGNOSTIC_NO_PACK"}))
            self.assertEqual(driver.EXIT_REFUSED, driver.run_night(plan, dry_arm=True))
            self.assertFalse((Path(directory) / "night-custody").exists())


class MockRuntimeDryRenderTests(unittest.TestCase):
    """A mock-runtime run of all three packs' rendered chains through the HAZARD_PACK driver."""

    def run_pack(self, pack, behavior=None):
        harness = Harness(self, pack, behavior=behavior)
        code = harness.run()
        result = harness.result()
        self.assertEqual(harness.driver.EXIT_GO, code, result)
        self.assertEqual(("GO", 0), (result["verdict"], result["chain_exit_code"]))
        for name, run_ids in fake_window.expected_bundles(harness.plan).items():
            root = Path(harness.plan.hazard_window["runs_roots"][name])
            present = {path.name for path in root.iterdir() if (path / "summary_metrics.json").is_file()}
            self.assertEqual(run_ids, present, name)
        hazard = harness.hazard()
        self.assertTrue(hazard["arm"]["go"])
        self.assertEqual({name: "PASS" for name in SIX}, hazard["arm"]["verdicts"])
        self.assertTrue(hazard["lineage"]["published"])
        self.assertTrue(hazard["monitor"]["stop"]["proven_stopped"])
        self.assertEqual("DISCHARGED", hazard["g10"]["result"])
        self.assertEqual(["network_time.off_output"], hazard["flags_emitted"])
        self.assertTrue(hazard["chain"]["matches_sidecar"])
        inventory = json.loads((harness.night / b5_driver.INVENTORY_RECORD).read_text())
        checkout = inventory["measurement_checkout"]
        self.assertEqual(40, len(checkout["head"]))
        self.assertIn("scripts/run_campaign.py", checkout["files"])
        self.assertEqual(fake_window.sha256(harness.measurement / "scripts/run_campaign.py"),
                         checkout["files"]["scripts/run_campaign.py"])
        self.assertEqual(fake_window.sha256(Path(harness.plan.chain_path)), inventory["chain"]["sha256"])
        return harness, hazard

    def test_alpha_beta_and_gamma_run_end_to_end(self):
        for pack in ("alpha", "beta", "gamma"):
            with self.subTest(pack=pack):
                harness, hazard = self.run_pack(pack)
                self.assertTrue(all(row["rc"] == 0 for row in hazard["chain"]["stages"]))
                corpus = hazard["neg8_corpus"]
                self.assertEqual((12, 12, False, []), (corpus["members_listed"], corpus["members_kept"],
                                                       corpus["pruned"], corpus["errors"]))
                self.assertEqual(corpus["committed_manifest"]["sha256"], corpus["collected_manifest"]["sha256"])

    def test_alpha_with_one_failed_science_member_and_eleven_corpus_members(self):
        order = json.loads((REPO_ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5/"
                                        "05_phase_prefill_p2048_abba_blocks_01_05/order_manifest.json").read_text())
        victim = order["executed_order"][3]["run_id"]
        harness = Harness(self, "alpha", behavior={"fail_run_ids": [victim, "neg8-refcorpus-r12"]})
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        stage = next(call for call in fake_window.calls(harness.measurement)
                     if call["tool"] == "collect" and call["config_dir"].endswith("05_phase_prefill_p2048_abba_blocks_01_05"))
        self.assertEqual((20, 1), (len(stage["attempted"]), stage["failures"]))
        derive = next(call for call in fake_window.calls(harness.measurement) if call["tool"] == "derive")
        self.assertEqual((11, True), (derive["members"], derive["ok"]))
        hazard = harness.hazard()
        rows = {row["stage_id"]: row["rc"] for row in hazard["chain"]["stages"]}
        self.assertEqual(0, rows["alpha-bound-derivation"])
        self.assertEqual(0, rows["alpha-post-calibration"])
        # Review finding (L2 NEG-8): the pruned manifest the derivation read is
        # located in hazard_result.json by path and SHA-256, for the harvest.
        collected = harness.night / "transcript" / b5_chain.NEG8_COLLECTED_MANIFEST
        corpus = hazard["neg8_corpus"]
        self.assertEqual({"path": str(collected), "sha256": fake_window.sha256(collected)},
                         corpus["collected_manifest"])
        self.assertEqual(fake_window.sha256(REPO_ROOT / "configs/campaigns/neg8_reference_corpus_v5/"
                                                        "derivation/settled_corpus.json"),
                         corpus["committed_manifest"]["sha256"])
        self.assertEqual((12, 11, True), (corpus["members_listed"], corpus["members_kept"], corpus["pruned"]))
        self.assertEqual(fake_window.sha256(harness.night / "transcript" / b5_chain.NEG8_COLLECTED_SUMMARY),
                         corpus["summary"]["sha256"])



class UnitTests(unittest.TestCase):
    def test_flags_have_the_joulewise_flag_v1_shape(self):
        fields = {"code": "disk.low", "family": "DIAGNOSTIC", "klass": "PHYSICS",
                  "scope": {"level": "window", "plan_id": "p", "attempt": 1},
                  "source": {"stage": "window", "collector": "b5.driver"},
                  "observed": {"free_bytes": 1}, "expected": {"low_bytes": 2}, "detail": "d"}
        flag = b5_driver.build_flag(fields, boot_session_uuid="BOOT")
        self.assertEqual({"schema_version", "flag_id", "code", "family", "klass", "scope", "interval", "source",
                          "observed", "expected", "evidence", "detail", "emitted", "catalog_sha256", "blinding"},
                         set(flag))
        identity = json.dumps({"code": "disk.low", "scope": flag["scope"], "observed": {"free_bytes": 1},
                               "source": flag["source"], "interval": flag["interval"]},
                              sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(hashlib.sha256(identity.encode()).hexdigest()[:20], flag["flag_id"])
        # Two intervals are two facts: the fallback's flag_id changes with the interval
        # exactly as joulewise.flags.schema.make_flag's does.
        timed = dict(fields, interval={"monotonic_ns": [1, 2], "monotonic_raw_ns": None, "wall_s": None})
        self.assertNotEqual(flag["flag_id"], b5_driver.build_flag(timed)["flag_id"])
        self.assertEqual(["level", "plan_id", "attempt", "stage_id", "run_id", "bundle_id"], list(flag["scope"]))
        try:
            from joulewise.flags.schema import make_flag, validate_flag
        except ImportError:
            return  # lane L4's package lands at integration; then the shapes must agree exactly
        self.assertEqual([], validate_flag(flag))
        produced = make_flag(**fields)
        self.assertEqual(produced["flag_id"], flag["flag_id"])
        self.assertEqual(make_flag(**timed)["flag_id"], b5_driver.build_flag(timed)["flag_id"])
        self.assertEqual([], validate_flag(b5_driver.build_flag(timed)))

    def test_decision_reading_is_conservative(self):
        go = {name: "PASS" for name in SIX}
        self.assertTrue(b5_driver.normalize_decision({"go": True, "verdicts": go})["go"])
        self.assertTrue(b5_driver.normalize_decision({"verdict": "GO", "verdicts": {
            name: {"status": "PASS"} for name in SIX}})["go"])
        for raw in ({"go": True, "verdicts": {**go, "thermal": "UNMEASURED"}},
                    {"go": True, "verdicts": {k: v for k, v in go.items() if k != "disk"}},
                    {"go": "yes", "verdicts": go}, {"go": False, "verdicts": go}, None, "GO", 1):
            with self.subTest(raw=raw):
                self.assertFalse(b5_driver.normalize_decision(raw)["go"])

    def test_executed_inventory_hashes_tracked_files_and_records_head_and_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            measurement = fake_window.build_checkout(root)
            (measurement / "scripts/run_campaign.py").write_text("# edited after commit\n")
            chain = root / "chain.zsh"
            chain.write_text("exit 0\n")
            record = b5_driver.executed_inventory(
                measurement_root=measurement, driver_root=REPO_ROOT,
                pack_root=measurement / "configs/campaigns" / fake_window.PACKS["alpha"],
                chain_path=chain, git=b5_driver._git)
            checkout = record["measurement_checkout"]
            self.assertEqual([], checkout["errors"])
            self.assertFalse(checkout["status_clean"])
            self.assertIn("scripts/run_campaign.py", checkout["status_porcelain"])
            self.assertEqual(fake_window.sha256(measurement / "scripts/run_campaign.py"),
                             checkout["files"]["scripts/run_campaign.py"])
            self.assertEqual(fake_window.sha256(chain), record["chain"]["sha256"])
            self.assertIn("driver_checkout", record)
            broken = b5_driver.executed_inventory(
                measurement_root=root / "missing", driver_root=None, pack_root=root / "missing/pack",
                chain_path=root / "missing.zsh", git=b5_driver._git)
            self.assertEqual(3, len(broken["measurement_checkout"]["errors"]))
            self.assertIsNone(broken["chain"]["sha256"])

    def hazard_plan(self, root):
        mapping = fake_window.hazard_plan_mapping(root, plan_id="b5-alpha-1", t0_epoch_s=1_800_000_000.0,
                                                  authored_epoch_s=1_799_999_000.0)
        return night_gate.NightPlan.from_mapping(mapping)

    def test_production_seams_follow_the_other_lanes_command_lines(self):
        import types
        seams = b5_driver.production_seams(REPO_ROOT)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            plan = self.hazard_plan(root)
            g10 = seams.g10_argv(root / "night", 335)
            self.assertEqual([str(REPO_ROOT / "scripts/g10_clock_step_control.py"), "--night-dir",
                              str(root / "night"), "--t-stream-max-s", "335.0"], g10[2:])
            collectors = seams.collectors_argv(b5_driver.CollectorRequest(plan, root / "plan.json", root, "arm"))
            self.assertEqual(["--stage", "arm", "--custody", str(root)], collectors[3:7])
            self.assertIn("--h-claim", collectors)
            self.assertEqual(b5_driver.run_bounded, seams.run_command)
            # The monitor: lane L1's config, written once, and its --config command line.
            built = {}
            fake = types.SimpleNamespace(
                build_config=lambda **kw: built.update(kw) or {"schema": "fake", **{k: str(v) for k, v in kw.items()}},
                validate_config=lambda config: config,
                monitor_dir=lambda custody: Path(custody) / "hazards" / "monitor")
            with mock.patch.dict(sys.modules, {"joulewise.hazards": types.ModuleType("joulewise.hazards"),
                                               "joulewise.hazards.monitor": fake}):
                sys.modules["joulewise.hazards"].monitor = fake
                request = b5_driver.MonitorRequest(plan, root / "plan.json", root, root / "night", 42)
                monitor = seams.monitor_argv(request)
                again = seams.monitor_argv(request)
            config = root / "hazards/monitor/config.json"
            self.assertEqual(["/usr/sbin/taskpolicy", "-b", sys.executable, "-B",
                              str(REPO_ROOT / "scripts/hazard_monitor.py"), "--config", str(config)], monitor)
            self.assertEqual(monitor, again)
            self.assertTrue(config.is_file())
            self.assertEqual((42,), tuple(built["tree_roots"]))
            self.assertEqual([plan.hazard_window["runs_roots"]["claim"], plan.hazard_window["runs_roots"]["bound"]],
                             [item["requested_path"] for item in built["disk_targets"]][:2])
            self.assertEqual(10 * 1024 ** 3, built["low_bytes"])

    def test_production_arm_adapter_reads_lane_l1_results_conservatively(self):
        import types
        seen = {}

        class Result:
            def __init__(self, decision, document, refused_at=None):
                self.decision, self.document, self.refused_at = decision, document, refused_at
                self.reasons, self.path = ("r",), Path("/fixture/hazards/arm.json")

            @property
            def go(self):
                return self.decision == "GO"

        def hazard(module, *statuses):
            return {module: [{"phase": "p", "verdict": {"module": module, "status": status}} for status in statuses]}

        documents = {
            "go": Result("GO", {"hazards": {**{m: [{"verdict": {"status": "PASS"}}] for m in SIX}},
                                "network_time_off": {"returncode": 0, "stdout": "off"},
                                "record_only": [{"name": "flags.arm", "returncode": 0}]}),
            "refused clock after a pass": Result("NULL", {"hazards": {**hazard("clock", "PASS", "REFUSE"),
                                                                      **hazard("battery", "PASS")}},
                                                 refused_at="final"),
        }
        fake = types.SimpleNamespace(
            ArmConfig=lambda **kw: seen.setdefault("config", kw) or kw,
            run=lambda config: documents[seen["case"]])
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(
                sys.modules, {"joulewise.hazards": types.ModuleType("joulewise.hazards"),
                              "joulewise.hazards.arm": fake}):
            sys.modules["joulewise.hazards"].arm = fake
            root = Path(directory).resolve()
            plan = self.hazard_plan(root)
            context = b5_driver.ArmContext(
                plan=plan, plan_path=root / "plan.json", custody_root=root, night_dir=root / "night",
                record_root=root / "hazards", hazard_window=plan.hazard_window,
                thresholds={name: {} for name in SIX}, t_stream_max_s=335.0, planned_bytes=7,
                disk_volumes=(), disk_targets=({"path": str(root), "copies": 1},), measurement_tree_pids=(9,),
                census={"clean": True}, arm_deadline_epoch_s=0.0, dry_arm=False, record_only_argv=("collect",),
                network_time_off=dict, record_only_collectors=dict, agent_census=dict)
            seen["case"] = "go"
            decision = b5_driver.normalize_decision(b5_driver._production_arm(context))
            self.assertTrue(decision["go"])
            self.assertEqual("off", decision["network_time_off"]["stdout"])
            config = seen["config"]
            self.assertEqual(root, config["custody_dir"])
            self.assertEqual(7, config["thresholds"]["disk"]["planned_bytes"])
            self.assertEqual(335.0, config["thresholds"]["clock"]["t_stream_max_s"])
            self.assertEqual(["collect"], config["record_only"][0]["argv"])
            self.assertEqual((9,), config["tree_roots"])
            seen.clear()
            seen["case"] = "refused clock after a pass"
            decision = b5_driver.normalize_decision(b5_driver._production_arm(context))
            self.assertFalse(decision["go"])
            self.assertEqual("REFUSE", decision["verdicts"]["clock"])
            self.assertEqual("PASS", decision["verdicts"]["battery"])
            self.assertEqual("NOT_EVALUATED", decision["verdicts"]["instrument"])
            self.assertEqual("final", decision["refused_at"])

    def test_the_windows_own_sizing_wins_over_copied_threshold_values(self):
        # Review finding (L2 thresholds): a disk.planned_bytes or clock.t_stream_max_s
        # copied into the thresholds never overrides the window's own values.
        copied = {**{name: {} for name in SIX},
                  "disk": {"planned_bytes": 1, "headroom_bytes": 5},
                  "clock": {"t_stream_max_s": 100, "h_ms": 3.7}}
        context = types.SimpleNamespace(thresholds=copied, planned_bytes=7, t_stream_max_s=335.0)
        thresholds = b5_driver._arm_thresholds(context)
        self.assertEqual({"planned_bytes": 7, "headroom_bytes": 5}, thresholds["disk"])
        self.assertEqual({"t_stream_max_s": 335.0, "h_ms": 3.7}, thresholds["clock"])
        self.assertEqual(1, copied["disk"]["planned_bytes"])   # the plan's mapping is not mutated

    def test_production_lineage_adapter_passes_the_pack_identity(self):
        import types
        seen = {}
        fake = types.SimpleNamespace(publish_window_lineage=lambda **kw: seen.update(kw) or {"ok": True})
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(
                sys.modules, {"joulewise.window_lineage": fake}):
            root = Path(directory).resolve()
            plan = self.hazard_plan(root)
            window = plan.hazard_window
            request = b5_driver.LineageRequest(
                plan=plan, plan_path=root / "plan.json", custody_root=root, night_dir=root / "night",
                hazard_window=window, claim_runs_root=Path(window["runs_roots"]["claim"]),
                bound_runs_root=Path(window["runs_roots"]["bound"]), arm_record_path=None,
                arm_decision_path=root / "night/arm_decision.json", boot_session_uuid="BOOT")
            self.assertEqual({"ok": True}, b5_driver._production_lineage(request))
        self.assertEqual(window["pack"]["pack_plan_id"], seen["plan_id"])
        self.assertNotEqual(plan.plan_id, seen["plan_id"])
        self.assertEqual(window["pack"]["window_id"], seen["window_id"])
        self.assertEqual(window["bracket_session_id"], seen["bracket_session_id"])
        self.assertEqual((window["bindings"]["pre_attempt_id"], window["bindings"]["post_attempt_id"]),
                         (seen["pre_attempt_id"], seen["post_attempt_id"]))
        self.assertEqual("BOOT", seen["boot_session_id"])
        self.assertEqual(root / "night/arm_decision.json", seen["arm_decision_path"])

    def test_arm_run_off_and_collectors_are_recorded_once_not_rerun(self):
        harness = Harness(self, g10=False, arm=FakeArm(raw={
            "go": True, "verdicts": {name: "PASS" for name in SIX}, "record_path": None,
            "network_time_off": {"argv": list(b5_driver.NETWORK_TIME_OFF_ARGV), "returncode": 0,
                                 "stdout": "Network Time is already off.\n", "stderr": ""},
            "record_only": [{"name": "flags.arm", "returncode": 0}]}))
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertEqual(0, harness.network.calls)
        action = json.loads((harness.night / b5_driver.NETWORK_TIME_ACTION).read_text())
        self.assertEqual(("arm", "Network Time is already off.\n"), (action["ran_by"], action["stdout"]))
        collectors = json.loads((harness.night / b5_driver.COLLECTORS_RECORD).read_text())
        self.assertEqual("arm", collectors["ran_by"])
        self.assertFalse((harness.night / "network_time_off.action-01.json").exists())

    def test_a_monitor_command_that_cannot_be_built_is_retried_and_never_holds_the_chain(self):
        harness = Harness(self, g10=False)

        def unavailable(_request):
            raise ModuleNotFoundError("No module named 'joulewise.hazards'")
        original = harness.seams
        harness.driver._hazard_seams = lambda: (lambda s: (setattr(s, "monitor_argv", unavailable), s)[1])(original())
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 2\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        monitor = harness.hazard()["monitor"]
        self.assertEqual(0, monitor["starts"])
        self.assertGreaterEqual(monitor["start_failures"], 2)

    def test_the_monitor_disk_low_marker_stops_the_chain(self):
        harness = Harness(self, g10=False)
        marker = harness.custody / "hazards/monitor/disk.low"
        harness.monitor_argv = [sys.executable, "-c", (
            "import json, pathlib, time; p = pathlib.Path(%r); p.parent.mkdir(parents=True, exist_ok=True); "
            "p.write_text(json.dumps({'low': [{'path': '/runs', 'free_bytes': 5}]})); time.sleep(600)") % str(marker)]
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 60\n")
        self.assertEqual(harness.driver.EXIT_ABORTED, harness.run())
        self.assertEqual(b5_driver.STOPPED_DISK_LOW, harness.result()["aborted_reason"])
        self.assertEqual(str(marker), harness.hazard()["disk_floor"]["stops"][0]["source"])

    def test_dead_man_stops_an_orphaned_monitor_group_and_never_a_reused_pid(self):
        from joulewise.measurement_liveness import observe_identity
        with tempfile.TemporaryDirectory() as directory:
            night = Path(directory)
            process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                                       start_new_session=True)
            self.addCleanup(lambda: process.poll() is None and process.kill())
            identity = observe_identity(process.pid)
            start = {"event": "start", "pid": process.pid, "pgid": process.pid, "start_time": identity.start_time}
            (night / b5_driver.MONITOR_JOURNAL).write_text(json.dumps(start) + "\n")
            stale = dict(start, start_time="Thu Jan  1 00:00:00 1970")
            (night / "stale.jsonl").write_text(json.dumps(stale) + "\n")
            reused = b5_driver.reap_orphan_monitor(night, identity=lambda pid: type(identity)(
                "LIVE", "Thu Jan  1 00:00:00 1970"))
            self.assertFalse(reused["signalled"])
            self.assertIsNone(process.poll())
            reaped = b5_driver.reap_orphan_monitor(night, identity=observe_identity)
            self.assertTrue(reaped["signalled"])
            self.assertEqual(-signal.SIGTERM, process.wait(timeout=10))
            with (night / b5_driver.MONITOR_JOURNAL).open("a") as handle:
                handle.write(json.dumps({"event": "stop", "proven_stopped": True}) + "\n")
            self.assertIsNone(b5_driver.reap_orphan_monitor(night, identity=observe_identity))


if __name__ == "__main__":
    unittest.main()
