"""Gate-prune P3 lane P3-DRV: the HAZARD_PACK driver's round-3 behaviour.

Covered: the KM003C wall meter wired per ``~/night-archive/wallmeter-probe/WIRING.md``
(a named supervisor, no restart after a clean "absent" exit, a SIGTERM stop
proven gone, its stream listed in the custody record, the dead-man reaping an
orphaned meter, and DISCLOSE flags for its supervision failures); and the R3-5
hold, which stops the hazard monitor and the meter no sooner than 5 s after the
chain exits.

Each end-to-end test drives the real driver through the shared harness of
``tests/test_b5_driver.py``; the meter program is a stand-in with the real
script's stream header, trailer and signal handling.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from joulewise.b5 import driver as b5_driver
from tests.test_b5_driver import Harness, load_driver

REPO_ROOT = Path(__file__).resolve().parents[1]

# A stand-in for scripts/km003c_monitor.py: the same create-once --out, header
# status and trailer; SIGTERM/SIGINT/SIGHUP end the stream with a trailer and
# exit 0. Modes: "streaming" runs until signalled; "absent" writes an absent
# header and trailer and exits 0 at once; "crash" exits 3 after 0.3 s.
FAKE_METER = r"""
import json, pathlib, signal, sys, time
mode, out = sys.argv[1], pathlib.Path(sys.argv[sys.argv.index("--out") + 1])
stop = {"reason": None}
def on_signal(number, _frame):
    stop["reason"] = "signal %d" % number
for number in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(number, on_signal)
with open(out, "x") as handle:
    status = "absent" if mode == "absent" else "streaming"
    handle.write(json.dumps({"k": "h", "schema": "joulewise.km003c_stream.v1", "status": status}) + "\n")
    handle.flush()
    if mode == "absent":
        handle.write(json.dumps({"k": "t", "stop_reason": "absent"}) + "\n")
        raise SystemExit(0)
    if mode == "crash":
        time.sleep(0.3)
        raise SystemExit(3)
    while stop["reason"] is None:
        time.sleep(0.05)
    handle.write(json.dumps({"k": "t", "stop_reason": stop["reason"]}) + "\n")
raise SystemExit(0)
"""


def fake_meter_argv(mode: str = "streaming"):
    def argv(request):
        out_dir = Path(request.custody_root).joinpath(*b5_driver.METER_STREAM_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        return [sys.executable, "-c", FAKE_METER, mode, "--out", str(b5_driver.next_meter_stream(out_dir))]
    return argv


def patch(test: unittest.TestCase, target, name: str, value) -> None:
    patcher = mock.patch.object(target, name, value)
    patcher.start()
    test.addCleanup(patcher.stop)


def flags(harness: Harness, code: str) -> list[dict]:
    return [item for item in harness.flags if item["code"] == code]


def journal(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def group_gone(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


# --------------------------------------------------------------------------
# The supervisor: a name, and the meter's restart policy


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="b5-p3-supervisor-")
        self.addCleanup(directory.cleanup)
        self.night = Path(directory.name)
        patch(self, b5_driver, "MONITOR_RESTART_INTERVAL_S", 0.0)

    def supervisor(self, argv, **keywords):
        supervisor = b5_driver.MonitorSupervisor(argv, night_dir=self.night, popen=subprocess.Popen,
                                                 group_census=load_driver()._group_census, **keywords)
        self.addCleanup(lambda: supervisor.stopped or supervisor.stop())
        return supervisor

    def wait_exit(self, supervisor, timeout=10.0):
        deadline = time.monotonic() + timeout
        while supervisor.process is not None and supervisor.process.poll() is None:
            self.assertLess(time.monotonic(), deadline)
            time.sleep(0.05)

    def test_named_supervisors_write_their_own_journal_and_logs(self):
        monitor = self.supervisor([sys.executable, "-c", "print('monitor')"])
        meter = self.supervisor([sys.executable, "-c", "print('meter')"], name="meter")
        self.assertTrue(monitor.start() and meter.start())
        self.wait_exit(monitor)
        self.wait_exit(meter)
        monitor.stop()
        meter.stop()
        self.assertEqual("monitor\n", (self.night / "monitor.stdout.log").read_text())
        self.assertEqual("meter\n", (self.night / "meter.stdout.log").read_text())
        self.assertEqual(b5_driver.MONITOR_JOURNAL, monitor.summary()["journal"])
        self.assertEqual(b5_driver.METER_JOURNAL, meter.summary()["journal"])
        for name, supervisor in ((b5_driver.MONITOR_JOURNAL, monitor), (b5_driver.METER_JOURNAL, meter)):
            events = [line["event"] for line in journal(self.night / name)]
            self.assertEqual(["start", "exit", "stop"], events, name)
        # The hazard monitor's summary keeps its shape.
        self.assertNotIn("final_exit", monitor.summary())

    def test_a_clean_exit_is_final_and_never_restarted(self):
        meter = self.supervisor([sys.executable, "-c", "raise SystemExit(0)"], name="meter",
                                restart_on_clean_exit=False)
        self.assertTrue(meter.start())
        self.wait_exit(meter)
        for _ in range(5):
            meter.poll()
        self.assertEqual(1, meter.starts)
        summary = meter.stop()
        self.assertEqual(0, summary["final_exit"]["returncode"])
        self.assertTrue(summary["final_exit"]["final"])
        self.assertTrue(summary["stop"]["proven_stopped"])
        events = journal(self.night / b5_driver.METER_JOURNAL)
        self.assertEqual(["start", "exit", "stop"], [line["event"] for line in events])
        self.assertTrue(events[1]["final"])

    def test_a_nonzero_exit_or_a_signal_death_is_restarted(self):
        for code in ("raise SystemExit(3)", "import os, signal; os.kill(os.getpid(), signal.SIGKILL)"):
            with self.subTest(code):
                (self.night / b5_driver.METER_JOURNAL).unlink(missing_ok=True)
                meter = self.supervisor([sys.executable, "-c", code], name="meter", restart_on_clean_exit=False)
                self.assertTrue(meter.start())
                self.wait_exit(meter)
                meter.poll()
                self.assertEqual(2, meter.starts)
                self.assertIsNone(meter.summary()["final_exit"])
                meter.stop()

    def test_the_hazard_monitor_still_restarts_after_a_clean_exit(self):
        monitor = self.supervisor([sys.executable, "-c", "raise SystemExit(0)"])
        self.assertTrue(monitor.start())
        self.wait_exit(monitor)
        monitor.poll()
        self.assertEqual(2, monitor.starts)

    def test_stop_sends_sigterm_and_proves_the_group_gone(self):
        out = self.night / "stream-001.jsonl"
        meter = self.supervisor([sys.executable, "-c", FAKE_METER, "streaming", "--out", str(out)],
                                name="meter", restart_on_clean_exit=False)
        self.assertTrue(meter.start())
        deadline = time.monotonic() + 10
        while not out.exists() or not out.read_text():
            self.assertLess(time.monotonic(), deadline)
            time.sleep(0.05)
        pgid = meter.process.pid
        summary = meter.stop()
        stop = summary["stop"]
        self.assertEqual((True, 0, True, True),
                         (stop["was_running"], stop["returncode"], stop["group_absent"], stop["proven_stopped"]))
        self.assertNotIn("escalated_to_kill", stop)
        # The meter saw SIGTERM and closed its stream with a trailer.
        self.assertEqual({"k": "t", "stop_reason": f"signal {int(signal.SIGTERM)}"},
                         json.loads(out.read_text().splitlines()[-1]))
        self.assertTrue(group_gone(pgid))


# --------------------------------------------------------------------------
# The production seam


class ProductionSeamTests(unittest.TestCase):
    def test_the_meter_runs_at_plain_qos_into_a_new_create_once_stream(self):
        with tempfile.TemporaryDirectory(prefix="b5-p3-seam-") as directory:
            custody = Path(directory)
            seams = b5_driver.production_seams(REPO_ROOT)
            request = b5_driver.MonitorRequest(None, custody / "plan.json", custody, custody / "night", 1)
            first = seams.meter_argv(request)
            self.assertEqual([sys.executable, "-B", str(REPO_ROOT / "scripts/km003c_monitor.py"), "--out",
                              str(custody / "hazards/meter/stream-001.jsonl")], first)
            self.assertNotIn(b5_driver.TASKPOLICY_ARGV[0], first)
            (custody / "hazards/meter/stream-001.jsonl").write_text("")
            self.assertEqual(str(custody / "hazards/meter/stream-002.jsonl"), seams.meter_argv(request)[-1])

    def test_the_absent_meter_script_exits_zero_once(self):
        # The real script with no libusb: an absent header, a trailer, exit 0
        # (the supervisor's "final" exit).
        with tempfile.TemporaryDirectory(prefix="b5-p3-absent-") as directory:
            out = Path(directory) / "stream-001.jsonl"
            result = subprocess.run([sys.executable, "-B", str(REPO_ROOT / "scripts/km003c_monitor.py"),
                                     "--out", str(out), "--libusb", str(Path(directory) / "no-libusb.dylib")],
                                    capture_output=True, timeout=60)
            self.assertEqual(0, result.returncode, result.stderr)
            lines = [json.loads(line) for line in out.read_text().splitlines()]
            self.assertEqual(("h", "absent"), (lines[0]["k"], lines[0]["status"]))
            self.assertEqual(("t", "absent"), (lines[-1]["k"], lines[-1]["stop_reason"]))


# --------------------------------------------------------------------------
# The meter in a window, end to end


class MeterWindowTests(unittest.TestCase):
    def harness(self, mode="streaming", chain="/bin/sleep 2\nexit 0\n"):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\n" + chain)
        harness.meter_argv = fake_meter_argv(mode)
        return harness

    def test_the_meter_streams_through_the_window_and_is_stopped_by_sigterm(self):
        harness = self.harness()
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertEqual("GO", harness.result()["verdict"])
        meter = harness.hazard()["meter"]
        self.assertEqual((1, 0, b5_driver.METER_JOURNAL), (meter["starts"], meter["restarts"], meter["journal"]))
        self.assertEqual((True, True, 0), (meter["stop"]["was_running"], meter["stop"]["proven_stopped"],
                                           meter["stop"]["returncode"]))
        stream = harness.custody / "hazards/meter/stream-001.jsonl"
        self.assertEqual([{"path": "hazards/meter/stream-001.jsonl", "status": "streaming",
                           "sha256": b5_driver._sha256_file(stream)}], meter["streams"])
        self.assertEqual(f"signal {int(signal.SIGTERM)}", json.loads(stream.read_text().splitlines()[-1])["stop_reason"])
        events = journal(harness.night / b5_driver.METER_JOURNAL)
        self.assertEqual(["start", "stop"], [line["event"] for line in events])
        self.assertTrue(group_gone(events[0]["pgid"]))
        self.assertEqual([], flags(harness, "meter.supervision_fault"))
        # The hazard monitor kept its own journal and logs.
        self.assertEqual(b5_driver.MONITOR_JOURNAL, harness.hazard()["monitor"]["journal"])
        self.assertNotIn("meter", "".join(line.get("argv", [""])[-1] for line in
                                          journal(harness.night / b5_driver.MONITOR_JOURNAL)
                                          if line["event"] == "start"))

    def test_an_absent_meter_is_started_once_and_never_restarted(self):
        harness = self.harness("absent", "/bin/sleep 3\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        meter = harness.hazard()["meter"]
        self.assertEqual((1, 0), (meter["starts"], meter["restarts"]))
        self.assertEqual((0, True), (meter["final_exit"]["returncode"], meter["final_exit"]["final"]))
        self.assertEqual(["absent"], [row["status"] for row in meter["streams"]])
        self.assertEqual(["hazards/meter/stream-001.jsonl"], [row["path"] for row in meter["streams"]])
        self.assertEqual([], flags(harness, "meter.supervision_fault"))

    def test_a_crashed_meter_is_restarted_into_a_new_stream(self):
        harness = self.harness("crash", "/bin/sleep 3\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        meter = harness.hazard()["meter"]
        self.assertGreaterEqual(meter["starts"], 2)
        self.assertEqual([f"hazards/meter/stream-{index:03d}.jsonl" for index in range(1, meter["starts"] + 1)],
                         [row["path"] for row in meter["streams"]])
        self.assertTrue(all(item["returncode"] == 3 for item in meter["exits"]))

    def test_a_meter_that_cannot_start_is_a_disclose_flag_and_the_window_runs(self):
        harness = self.harness()
        harness.meter_argv = lambda request: [str(harness.root / "no-such-meter")]
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertEqual("GO", harness.result()["verdict"])
        found = flags(harness, "meter.supervision_fault")
        self.assertEqual("start_failed", found[0]["observed"]["event"])
        self.assertEqual(("DIAGNOSTIC", "PHYSICS"), (found[0]["family"], found[0]["klass"]))
        self.assertEqual(1, len([item for item in found if item["observed"]["event"] == "start_failed"]))
        report = harness.driver.run_courier.call_args.kwargs["report"]["facts"]
        self.assertFalse(report["fault"])
        self.assertIn("meter.supervision_fault", harness.hazard()["flags_emitted"])

    def test_a_crash_looping_meter_is_flagged_once_not_a_fault(self):
        patch(self, b5_driver, "MONITOR_RESTART_INTERVAL_S", 0.0)
        harness = self.harness("crash", "/bin/sleep 6\nexit 0\n")
        patch(self, b5_driver, "MONITOR_BACKOFF_AFTER", 2)
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        found = [item for item in flags(harness, "meter.supervision_fault")
                 if item["observed"]["event"] == "crash_loop"]
        self.assertEqual(1, len(found))
        report = harness.driver.run_courier.call_args.kwargs["report"]["facts"]
        self.assertNotIn("monitor_crash_loop", report["fault_reasons"])
        self.assertFalse(report["fault"])

    def test_the_meter_is_stopped_on_the_chain_already_started_refusal(self):
        harness = self.harness()
        harness.night.mkdir(parents=True, exist_ok=True)
        real = harness.driver._claim_chain_start
        harness.driver._claim_chain_start = lambda night: None
        self.addCleanup(setattr, harness.driver, "_claim_chain_start", real)
        self.assertEqual(harness.driver.EXIT_REFUSED, harness.run())
        meter = harness.hazard()["meter"]
        self.assertTrue(meter["stop"]["proven_stopped"])
        self.assertEqual("streaming", meter["streams"][0]["status"])

    def test_the_meter_supervision_journal_is_published_and_the_stream_is_not(self):
        driver = load_driver()
        self.assertIn(b5_driver.METER_JOURNAL, driver.HAZARD_ARTIFACTS)
        self.assertFalse(any("stream" in name for name in driver.HAZARD_ARTIFACTS))
        harness = self.harness()
        harness.run()
        artifacts = [row["path"] for row in harness.driver._artifact_list(harness.custody, harness.night)]
        self.assertIn(f"night/{b5_driver.METER_JOURNAL}", artifacts)
        self.assertFalse(any(path.startswith("hazards/") for path in artifacts))


# --------------------------------------------------------------------------
# R3-5: the monitor and the meter outlive the chain by at least 5 s


class PostChainHoldTests(unittest.TestCase):
    def test_the_monitor_stops_no_sooner_than_five_seconds_after_the_chain_exits(self):
        # Behavioural on any driver: the monitor journal's stop request against chain.exited.
        harness = Harness(self, g10=False)
        patcher = mock.patch.object(b5_driver, "MONITOR_POST_CHAIN_HOLD_S", 5.0, create=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        exited = json.loads((harness.night / "chain.exited").read_text())["monotonic_ns"]
        (stop,) = [line for line in journal(harness.night / b5_driver.MONITOR_JOURNAL) if line["event"] == "stop"]
        self.assertGreaterEqual(stop["requested"]["monotonic_ns"] - exited, 5_000_000_000)

    def test_monitor_and_meter_stop_no_sooner_than_five_seconds_after_the_chain_exits(self):
        harness = Harness(self, g10=False)
        patch(self, b5_driver, "MONITOR_POST_CHAIN_HOLD_S", 5.0)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        harness.meter_argv = fake_meter_argv()
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        exited = json.loads((harness.night / "chain.exited").read_text())["monotonic_ns"]
        stops = {}
        for name in (b5_driver.MONITOR_JOURNAL, b5_driver.METER_JOURNAL):
            (stop,) = [line for line in journal(harness.night / name) if line["event"] == "stop"]
            stops[name] = stop["requested"]["monotonic_ns"]
            self.assertGreaterEqual(stop["requested"]["monotonic_ns"] - exited, 5_000_000_000, name)
        hold = harness.hazard()["monitor_stop"]
        self.assertEqual(5.0, hold["hold_s"])
        self.assertGreaterEqual(hold["chain_returned"]["monotonic_ns"], exited)
        self.assertGreaterEqual(hold["released_after_chain_s"], 5.0)
        self.assertEqual(stops[b5_driver.MONITOR_JOURNAL], hold["monitor_stop_requested"]["monotonic_ns"])

    def test_the_hold_counts_from_the_chain_and_does_not_add_to_g10(self):
        stamp = b5_driver.stamp()
        stamp["monotonic_ns"] -= 10_000_000_000  # the chain returned 10 s ago (G10 ran meanwhile)
        polls = []
        started = time.monotonic()
        record = b5_driver.hold_monitors_after_chain(stamp, lambda: polls.append(1), hold_s=5.0)
        self.assertLess(time.monotonic() - started, 0.5)
        self.assertEqual([], polls)
        self.assertGreaterEqual(record["released_after_chain_s"], 10.0)

    def test_the_supervisors_keep_polling_during_the_hold(self):
        polls = []
        record = b5_driver.hold_monitors_after_chain(b5_driver.stamp(), lambda: polls.append(1), hold_s=2.0)
        self.assertGreaterEqual(len(polls), 2)
        self.assertGreaterEqual(record["released_after_chain_s"], 2.0)


# --------------------------------------------------------------------------
# The dead-man and an orphaned meter


class DeadManMeterTests(unittest.TestCase):
    def test_the_dead_man_stops_an_orphaned_meter_group(self):
        from joulewise.measurement_liveness import observe_identity
        harness = Harness(self, g10=False)
        harness.night.mkdir(parents=True, exist_ok=True)
        process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], start_new_session=True)
        self.addCleanup(lambda: process.poll() is None and process.kill())
        identity = observe_identity(process.pid)
        start = {"event": "start", "pid": process.pid, "pgid": process.pid, "start_time": identity.start_time}
        (harness.night / b5_driver.METER_JOURNAL).write_text(json.dumps(start) + "\n")
        harness.driver._completion_epoch_s = lambda plan: 0.0
        harness.driver.dead_man(harness.plan_path)
        self.assertEqual(-signal.SIGTERM, process.wait(timeout=10))
        self.assertIn("dead-man wall meter cleanup", (harness.custody / "night.log").read_text())

    def test_the_reaper_reads_the_named_journal(self):
        with tempfile.TemporaryDirectory(prefix="b5-p3-reap-") as directory:
            night = Path(directory)
            process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                                       start_new_session=True)
            self.addCleanup(lambda: process.poll() is None and process.kill())
            (night / b5_driver.METER_JOURNAL).write_text(
                json.dumps({"event": "start", "pid": process.pid, "pgid": process.pid}) + "\n")
            self.assertIsNone(b5_driver.reap_orphan_monitor(night))
            self.assertIsNone(process.poll())
            self.assertTrue(b5_driver.reap_orphan_monitor(night, journal=b5_driver.METER_JOURNAL)["signalled"])
            self.assertEqual(-signal.SIGTERM, process.wait(timeout=10))


if __name__ == "__main__":
    unittest.main()
