"""Agent-free handoff and orchestration; host commands and data are synthetic."""
from contextlib import ExitStack
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import signal
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import types
import unittest
import unittest.mock
from unittest.mock import patch

from scripts import launch_align_r0 as launcher
from scripts import run_align_r1_smoke as smoke

REPO = Path(launcher.__file__).resolve().parents[1]


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.args = SimpleNamespace(output=self.root / "capture", soak_reference=self.root / "soak.json",
                                    deadline=time.time() + 9000, pmset_bin="fake-pmset")
        self.args.soak_reference.write_text("{}")
        self.events = []
        self.fault_step = None
        self.live = set()
        self.feeds = [self.feed(name) for name in ("meter", "agents", "volumes")]
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name in ("ac_power", "night_agents", "condition13", "read_power", "display", "dwell", "part"):
            self.stack.enter_context(patch.object(smoke, name, side_effect=self.operation(name)))
        self.stack.enter_context(patch.object(smoke.powermode, "restore_automatic",
                                             side_effect=self.operation("restore")))
        self.stack.enter_context(patch.object(smoke.powermode, "HostLock"))
        self.stack.enter_context(patch.object(smoke.powermode, "host_marker_path", return_value=str(self.root / "marker")))

    def operation(self, name):
        def call(*args, **kwargs):
            event = "part-" + args[1] if name == "part" else name
            self.events.append(event)
            if event == self.fault_step:
                raise RuntimeError("injected " + event)
            if name == "part":
                kwargs["on_start"]()
                return {"rc": 0, "argv": ["synthetic", event]}
            return {"ok": True, "rc": 0, "observed": 0}
        return call

    def feed(self, name):
        outer = self
        class Feed:
            def __init__(self):
                self.name = name
                self.path = outer.args.output / (name + ".jsonl")
            def start(self):
                outer.events.append("start-" + name)
                outer.live.add(name)  # failure AFTER resource acquisition must still clean up
                self.path.write_text(name + "\n")
                if outer.fault_step == "start-" + name:
                    raise RuntimeError("injected start " + name)
                return {"rc": 0}
            def poll(self):
                pass
            def stop(self):
                outer.events.append("stop-" + name)
                outer.live.discard(name)
                if outer.fault_step == "stop-" + name:
                    raise RuntimeError("injected stop " + name)
                return {"rc": 0, "proven_stopped": True}
            def files(self):
                return [self.path]
        return Feed()

    def run_runner(self):
        return smoke.run(self.args, feeds=self.feeds)

    def receipt(self):
        return json.loads((self.args.output / "runner_receipt.json").read_text())

    def test_order_and_receipt(self):
        self.assertEqual(self.run_runner(), 0)
        self.assertEqual(self.events, ["night_agents", "ac_power", "condition13", "start-meter",
            "start-agents", "start-volumes", "read_power", "display", "dwell", "part-A", "part-B",
            "restore", "stop-volumes", "stop-agents", "stop-meter"])
        receipt = self.receipt()
        self.assertEqual(receipt["parts"], {"A": True, "B": True})
        self.assertEqual(receipt["rc"], 0)
        self.assertEqual(receipt["soak_reference"], str(self.args.soak_reference))
        for step in receipt["steps"]:
            self.assertEqual(step["rc"], 0, step)
            self.assertLessEqual(step["started"]["epoch_s"], step["ended"]["epoch_s"])
            self.assertLessEqual(step["started"]["monotonic_ns"], step["ended"]["monotonic_ns"])
        for name in ("meter", "agents", "volumes"):
            entry = receipt["feeds"][name]
            self.assertTrue(entry["stop"]["proven_stopped"])
            self.assertEqual(entry["files"], [{"path": name + ".jsonl",
                "sha256": hashlib.sha256((name + "\n").encode()).hexdigest()}])
        self.assertFalse(self.live)

    def test_part_b_skipped_on_part_a_nonzero_without_retry(self):
        with patch.object(smoke, "part", return_value={"rc": 17}) as part:
            self.assertEqual(self.run_runner(), 17)
        self.assertEqual([c.args[1] for c in part.call_args_list], ["A"])
        self.assertEqual(self.receipt()["parts"], {"A": True, "B": False})
        self.assertFalse(self.live)

    def test_every_failure_path_stops_all_feeds_and_writes_receipt(self):
        for failed in ("ac_power", "night_agents", "condition13", "start-meter", "start-agents",
                       "start-volumes", "read_power", "display", "dwell", "part-A", "part-B",
                       "restore", "stop-volumes", "stop-agents", "stop-meter"):
            with self.subTest(step=failed):
                self.args.output = self.root / failed
                for feed in self.feeds:
                    feed.path = self.args.output / (feed.name + ".jsonl")
                self.events.clear()
                self.fault_step = failed
                self.assertNotEqual(self.run_runner(), 0)
                self.assertFalse(self.live)
                for name in ("meter", "agents", "volumes"):
                    self.assertEqual(self.events.count("stop-" + name), 1)
                self.assertNotEqual(self.receipt()["rc"], 0)
                self.assertTrue(any(row["rc"] != 0 for row in self.receipt()["steps"]))

    def test_missing_soak_refuses_before_feeds(self):
        self.args.soak_reference.unlink()
        self.assertNotEqual(self.run_runner(), 0)
        self.assertFalse(any(e.startswith("start-") for e in self.events))

    def test_foreign_w1_marker_and_loaded_night_refuse_without_any_pmset(self):
        marker = self.root / "marker"
        marker.write_text("foreign W1")
        commands = []
        def host(argv):
            commands.append(argv)
            return subprocess.CompletedProcess(argv, 0, "123\t0\tcom.joulewise.night.align-r1\n", "")
        # Use real preflight operations and restore path, with fake hosts.
        with patch.object(smoke, "night_agents", ProductionSeamTests.real_night_agents), \
             patch.object(smoke, "ac_power", ProductionSeamTests.real_ac_power), \
             patch.object(smoke, "host_run", side_effect=host), \
             patch.object(smoke.powermode, "_run", side_effect=host), \
             patch.object(smoke.powermode, "restore_automatic") as restore:
            self.assertEqual(self.run_runner(), 2)
            restore.assert_not_called()
        self.assertEqual(commands, [["/bin/launchctl", "list"]])
        self.assertEqual(marker.read_text(), "foreign W1")
        self.assertEqual(self.receipt()["steps"][-4]["result"]["action"], "no_power_read")

    def test_early_refusal_owes_no_restore(self):
        self.fault_step = "ac_power"
        self.assertEqual(self.run_runner(), 2)
        self.assertNotIn("restore", self.events)

    def test_default_feed_order_and_volume_boundaries(self):
        self.feeds[2].before_part = lambda: self.events.append("volume-boundary")
        self.feeds[2].close = lambda: self.events.append("close-volume")
        with patch.object(smoke, "AgentFeed", return_value=self.feeds[1]), \
             patch.object(smoke, "MeterFeed", return_value=self.feeds[0]), \
             patch.object(smoke, "VolumeFeed", return_value=self.feeds[2]):
            self.assertEqual(smoke.run(self.args), 0)
        self.assertLess(self.events.index("start-agents"), self.events.index("start-meter"))
        self.assertEqual(self.events[self.events.index("dwell") + 1:self.events.index("restore")],
                         ["volume-boundary", "part-A", "volume-boundary", "part-B"])
        self.assertGreater(self.events.index("close-volume"),
                           max(self.events.index("stop-" + name) for name in ("agents", "meter", "volumes")))

    def test_signal_still_cleans_and_records_termination(self):
        with patch.object(smoke, "part", side_effect=SystemExit(143)):
            self.assertEqual(self.run_runner(), 143)
        self.assertFalse(self.live)
        self.assertEqual(self.receipt()["rc"], 143)

    def test_expired_deadline_starts_nothing_and_receipt_is_create_once(self):
        self.args.deadline = time.time() - 1
        self.assertNotEqual(self.run_runner(), 0)
        self.assertFalse(any(e.startswith("start-") for e in self.events))
        original = (self.args.output / "runner_receipt.json").read_bytes()
        with self.assertRaises(FileExistsError):
            self.run_runner()
        self.assertEqual((self.args.output / "runner_receipt.json").read_bytes(), original)

    def test_display_nonzero_is_recorded_like_r0_and_not_fatal(self):
        with patch.object(smoke, "display", return_value={"rc": 1}):
            self.assertEqual(self.run_runner(), 0)
        self.assertTrue(self.receipt()["parts"]["B"])
        self.assertEqual(next(s["rc"] for s in self.receipt()["steps"] if s["name"] == "display"), 1)

    def test_failed_part_spawn_is_not_recorded_as_ran(self):
        with patch.object(smoke, "part", side_effect=OSError("cannot spawn")):
            self.assertNotEqual(self.run_runner(), 0)
        self.assertEqual(self.receipt()["parts"], {"A": False, "B": False})

    def test_signal_during_meter_acquisition_still_registers_child_for_cleanup(self):
        with patch.object(smoke.driver, "production_seams"), \
             patch.object(smoke.driver, "MonitorSupervisor") as supervisor, \
             patch.object(smoke.night, "_terminate_process_group", return_value=True) as reap:
            supervisor.return_value.process = None
            supervisor.return_value.stop.return_value = {"stop": {"proven_stopped": True}}
            child = SimpleNamespace(pid=12345)
            def start():
                signal.raise_signal(signal.SIGTERM)
                supervisor.return_value.process = child
                return True
            supervisor.return_value.start.side_effect = start
            self.assertEqual(smoke.run(self.args, feeds=[smoke.MeterFeed(self.args.output)]), 143)
            reap.assert_called_once()

    def test_signals_during_meter_readiness_or_restart_preserve_owned_handle(self):
        for point in ("readiness", "restart"):
            with self.subTest(point=point), patch.object(smoke.driver, "production_seams"), \
                 patch.object(smoke.driver, "MonitorSupervisor") as supervisor, \
                 patch.object(smoke.driver, "await_meter_ready", return_value={"ready": True}) as ready, \
                 patch.object(smoke.night, "_terminate_process_group", return_value=True) as reap:
                self.args.output = self.root / point
                old, new = SimpleNamespace(pid=12345), SimpleNamespace(pid=12346)
                supervisor.return_value.process = old
                supervisor.return_value.start.return_value = True
                supervisor.return_value.stop.return_value = {}
                feed = smoke.MeterFeed(self.args.output)
                def restart(*_args):
                    signal.raise_signal(signal.SIGTERM)
                    supervisor.return_value.process = new
                    return {"ready": True}
                if point == "readiness":
                    ready.side_effect = restart
                else:
                    supervisor.return_value.poll.side_effect = restart
                with patch.object(smoke, "dwell", side_effect=lambda *_args: feed.poll()):
                    self.assertEqual(smoke.run(self.args, feeds=[feed]), 143)
                self.assertIs(reap.call_args.args[0], new)


class ProductionSeamTests(unittest.TestCase):
    real_night_agents = staticmethod(smoke.night_agents)
    real_ac_power = staticmethod(smoke.ac_power)
    def test_ac_and_loaded_wildcard_night_agent_refuse(self):
        with patch.object(smoke, "host_run", return_value=subprocess.CompletedProcess([], 0, "Battery Power", "")):
            with self.assertRaisesRegex(ValueError, "AC power"):
                smoke.ac_power()
        for label in ("com.joulewise.night", "com.joulewise.night.align-r1"):
            with patch.object(smoke, "host_run", return_value=subprocess.CompletedProcess([], 0, "123\t0\t" + label, "")):
                with self.assertRaisesRegex(ValueError, "night agent"):
                    smoke.night_agents()
        with patch.object(smoke, "host_run", return_value=subprocess.CompletedProcess([], 1, "", "unreadable")):
            with self.assertRaises(ValueError):
                smoke.night_agents()

    def test_condition13_drift_is_not_caught_or_cached(self):
        with patch.object(smoke, "host_run", return_value=subprocess.CompletedProcess([], 0, "a" * 40, "")), \
             patch.object(smoke.reg, "verify_r1_executed_sources", side_effect=ValueError("condition 13 drift")) as check:
            for _ in range(2):
                with self.assertRaisesRegex(ValueError, "condition 13 drift"):
                    smoke.condition13()
            self.assertEqual(check.call_count, 2)

    def test_census_producers_and_idempotent_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            probe = SimpleNamespace(argv=("fake-pgrep",), exit_code=1, stdout="", stderr="", monotonic_ns=1)
            with patch.object(smoke.night, "agent_census", return_value=(probe, None)) as agents, \
                 patch.object(smoke.r1.VolumeWatch, "census", return_value={"verdict": "PASS"}) as volumes, \
                 patch.object(smoke.r1.VolumeWatch, "__init__", return_value=None), \
                 patch.object(smoke.night, "_append_census", wraps=smoke.night._append_census) as append:
                feed_a, feed_v = smoke.AgentFeed(root), smoke.VolumeFeed(root)
                feed_v.watch.records = []
                volumes.side_effect = lambda *_: (feed_v.watch.records.append(
                    {"point": "sample", "verdict": "PASS"}) or {"verdict": "PASS"})
                for feed in (feed_a, feed_v):
                    feed.start(); feed.start(); feed.stop(); feed.stop(); feed.poll()
                feed_v.close(); feed_v.close()
                self.assertEqual(agents.call_count, 1)
                self.assertEqual(append.call_count, 1)
                self.assertEqual(volumes.call_count, 2)  # feed start and close
                self.assertTrue((root / "censuses.jsonl").is_file())
                self.assertTrue((root / "volume_censuses.jsonl").is_file())

    def test_stop_before_start_cannot_create_an_orphan(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(smoke.driver, "production_seams") as seams:
            for feed in (smoke.MeterFeed(Path(directory)), smoke.AgentFeed(Path(directory)), smoke.VolumeFeed(Path(directory))):
                feed.stop(); feed.start(); feed.stop()
            seams.assert_not_called()

    def test_part_proves_group_absence_even_when_leader_already_exited(self):
        with tempfile.TemporaryDirectory() as directory:
            args = SimpleNamespace(output=Path(directory), soak_reference=Path(directory) / "soak", deadline=time.time() + 7200)
            with patch.object(smoke.subprocess, "Popen") as popen, \
                 patch.object(smoke.night, "_terminate_process_group", return_value=True) as reap:
                popen.return_value.poll.return_value = popen.return_value.wait.return_value = 0
                self.assertEqual(smoke.part(args, "A", [])["rc"], 0)
                reap.assert_called_once_with(popen.return_value, evidence={})

    def test_meter_reuses_driver_and_stops_even_exited_leader(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(smoke.driver, "production_seams") as seams, \
                 patch.object(smoke.driver, "MonitorSupervisor") as supervisor, \
                 patch.object(smoke.driver, "await_meter_ready", return_value={"ready": True}), \
                 patch.object(smoke.night, "_terminate_process_group", return_value=True) as reap:
                seams.return_value.meter_argv.return_value = ["fake-meter"]
                supervisor.return_value.start.return_value = True
                supervisor.return_value.stop.return_value = {"stop": {"proven_stopped": True}}
                feed = smoke.MeterFeed(root)
                feed.start(); feed.start(); feed.stop(); feed.stop()
                self.assertEqual(supervisor.return_value.start.call_count, 1)
                self.assertEqual(supervisor.return_value.stop.call_count, 1)
                reap.assert_called_once()
                self.assertEqual(supervisor.call_args.kwargs["name"], "meter")
                self.assertIs(supervisor.call_args.kwargs["identity"], smoke.night.observe_identity)
                supervisor.call_args.args[0]()
                self.assertEqual(seams.return_value.meter_argv.call_count, 1)

    def test_restore_never_sets_mode_under_another_nights_lock(self):
        with patch.object(smoke.powermode, "HostLock") as lock, \
             patch.object(smoke.powermode, "restore_automatic") as restore:
            lock.return_value.acquire.return_value = False
            with self.assertRaisesRegex(ValueError, "host night lock"):
                smoke.restore_power(power_read=True)
            restore.assert_not_called()
            lock.return_value.release.assert_called_once()

    def test_restore_leaves_foreign_marker_under_host_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "foreign-marker"
            marker.write_text("W1 owns this")
            with patch.object(smoke.powermode, "host_marker_path", return_value=str(marker)), \
                 patch.object(smoke.powermode, "HostLock") as lock, \
                 patch.object(smoke.powermode, "restore_automatic") as restore:
                lock.return_value.acquire.return_value = True
                self.assertEqual(smoke.restore_power(power_read=True)["action"], "foreign_marker_left")
                restore.assert_not_called()
                lock.return_value.acquire.assert_called_once()
                lock.return_value.release.assert_called_once()
            self.assertEqual(marker.read_text(), "W1 owns this")

    def test_display_uses_configured_pmset(self):
        with patch.object(smoke.launcher, "sleep_display", return_value={"exit_code": 0}) as display:
            smoke.display("/synthetic/pmset")
            display.assert_called_once_with("/synthetic/pmset")

    def test_only_agent_census_polls_and_volume_census_runs_at_four_boundaries(self):
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            root = Path(directory)
            volume = smoke.VolumeFeed(root)
            agent = smoke.AgentFeed(root)
            volume_sample = stack.enter_context(patch.object(volume, "sample"))
            agent_sample = stack.enter_context(patch.object(agent, "sample"))
            clock = stack.enter_context(patch.object(smoke.time, "monotonic", return_value=0))
            volume.start(); agent.start()
            for instant in (30, 60, 300, 1900, 5000):
                clock.return_value = instant
                smoke.poll_feeds([agent, volume])
            self.assertEqual(volume_sample.call_count, 1)
            self.assertEqual(agent_sample.call_count, 6)
            volume.before_part(); volume.before_part(); volume.stop(); volume.stop(); volume.close(); volume.close()
            self.assertEqual(volume_sample.call_count, 4)
            self.assertEqual(agent.interval, 30)

    def test_part_b_may_finish_after_1800_seconds(self):
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            args = SimpleNamespace(output=Path(directory), soak_reference=Path(directory) / "soak", deadline=9000)
            clock = SimpleNamespace(now=0)
            stack.enter_context(patch.object(smoke.time, "time", side_effect=lambda: clock.now))
            stack.enter_context(patch.object(smoke.time, "monotonic", side_effect=lambda: clock.now))
            stack.enter_context(patch.object(smoke.time, "sleep", side_effect=lambda _: setattr(clock, "now", clock.now + 500)))
            popen = stack.enter_context(patch.object(smoke.subprocess, "Popen"))
            popen.return_value.poll.side_effect = lambda: None if clock.now < 2000 else 0
            popen.return_value.wait.return_value = 0
            enforcer = stack.enter_context(patch.object(smoke, "PartDeadline"))
            enforcer.return_value.expired.return_value = False
            enforcer.return_value.cancel.return_value = None
            stack.enter_context(patch.object(smoke.night, "_terminate_process_group", return_value=True))
            try:
                result = smoke.part(args, "B", [])
            except TimeoutError as exc:
                self.fail(f"legitimate Part B was truncated: {exc}")
            self.assertEqual(result["rc"], 0)
            self.assertEqual(clock.now, 2000)
            self.assertEqual(enforcer.call_args.kwargs["deadline_monotonic"], 5720)

    def test_full_part_cap_must_fit_before_spawn(self):
        for which, cap in launcher.r1_part_caps().items():
            with self.subTest(part=which), tempfile.TemporaryDirectory() as directory, \
                 patch.object(smoke.subprocess, "Popen") as spawn, \
                 patch.object(smoke.time, "time", return_value=1000):
                args = SimpleNamespace(output=Path(directory), soak_reference=Path(directory) / "soak",
                                       deadline=1000 + smoke.WORK_RESERVE_S + cap - 1)
                # A bypass mutant may proceed; make that path terminate cleanly
                # so the witness fails by assertion instead of setup errors.
                spawn.return_value.poll.return_value = spawn.return_value.wait.return_value = 0
                with patch.object(smoke, "PartDeadline") as enforcer, \
                     patch.object(smoke.night, "_terminate_process_group", return_value=True):
                    enforcer.return_value.expired.return_value = False
                    enforcer.return_value.cancel.return_value = None
                    with self.assertRaisesRegex(TimeoutError, "not started.*deadline"):
                        smoke.part(args, which, [])
                spawn.assert_not_called()

    def test_deadline_after_start_is_reported_as_deadline(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(smoke.subprocess, "Popen") as spawn, \
             patch.object(smoke, "PartDeadline"), \
             patch.object(smoke.night, "_terminate_process_group", return_value=True), \
             patch.object(smoke.time, "time", side_effect=[0, 0, 9000]):
            args = SimpleNamespace(output=Path(directory), soak_reference=Path(directory) / "soak", deadline=9000)
            spawn.return_value.poll.return_value = None
            with self.assertRaisesRegex(TimeoutError, "work deadline"):
                smoke.part(args, "A", [])

    def test_meter_missing_dc_in_batch_refuses_and_is_still_stoppable(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(smoke.driver, "production_seams"), \
             patch.object(smoke.driver, "MonitorSupervisor") as supervisor, \
             patch.object(smoke.driver, "await_meter_ready", return_value={"ready": False}), \
             patch.object(smoke.night, "_terminate_process_group", return_value=True):
            supervisor.return_value.start.return_value = True
            feed = smoke.MeterFeed(Path(directory))
            with self.assertRaisesRegex(ValueError, "DC-in"):
                feed.start()
            feed.stop()
            supervisor.return_value.stop.assert_called_once()

    def test_real_synthetic_part_is_reaped_on_success_failure_timeout_and_feed_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "fixture_smoke.py"
            script.write_text("import sys,time\nprint('synthetic',flush=True)\ntime.sleep(float(sys.argv[1]))\nraise SystemExit(int(sys.argv[2]))\n")
            args = SimpleNamespace(output=root, soak_reference=root / "soak", deadline=time.time() + 7200)
            real_popen = subprocess.Popen
            processes = []
            def spawn(argv, **kwargs):
                p = real_popen(argv, **kwargs)
                processes.append(p)
                self.addCleanup(smoke.night._terminate_process_group, p, prove_group_absent=False)
                return p
            for index, (seconds, code, timeout, failed_feed) in enumerate(((0, 0, 3, False), (0, 19, 3, False),
                                                        (10, 0, .1, False), (10, 0, 3, True))):
                args.output = root / str(index)
                args.output.mkdir()
                with self.subTest(seconds=seconds, code=code, timeout=timeout, failed_feed=failed_feed), \
                     patch.object(smoke, "part_argv", return_value=[sys.executable, "-B", str(script), str(seconds), str(code)]), \
                     patch.object(smoke.subprocess, "Popen", side_effect=spawn), \
                     patch.object(smoke.night, "_group_census", return_value=(True, [])), \
                     patch.object(smoke.launcher, "r1_part_caps", return_value={"A": timeout}), \
                     patch.object(smoke, "poll_feeds", side_effect=RuntimeError("feed failed") if failed_feed else None):
                    if seconds:
                        with self.assertRaises((RuntimeError, TimeoutError)):
                            smoke.part(args, "A", [])
                    else:
                        self.assertEqual(smoke.part(args, "A", [])["rc"], code)
                    self.assertIsNotNone(processes[-1].poll())

    def test_part_deadline_stops_capture_even_while_census_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            args = SimpleNamespace(output=Path(directory), soak_reference=Path(directory) / "soak", deadline=time.time() + 7200)
            children = []
            real_popen = subprocess.Popen
            def spawn(argv, **kwargs):
                child = real_popen(argv, **kwargs)
                children.append(child)
                self.addCleanup(smoke.night._terminate_process_group, child, prove_group_absent=False)
                return child
            def blocked_feed(_feeds):
                time.sleep(.3)
                self.assertIsNotNone(children[0].poll(), "capture extended by a blocked census")
            with patch.object(smoke, "part_argv", return_value=[sys.executable, "-B", "-c", "import time;time.sleep(10)"]), \
                 patch.object(smoke.subprocess, "Popen", side_effect=spawn), \
                 patch.object(smoke.night, "_group_census", return_value=(True, [])), \
                 patch.object(smoke, "poll_feeds", side_effect=blocked_feed), \
                 patch.object(smoke.launcher, "r1_part_caps", return_value={"A": .05}):
                with self.assertRaises(TimeoutError):
                    smoke.part(args, "A", [])


class LauncherTests(unittest.TestCase):
    def launch_files(self, module, root, *, kind="r0", checks=None, keep_going=True, seconds=11400, **extra):
        repo = root / "repo"
        (repo / "scripts").mkdir(parents=True)
        for name in ("align_r0_checks.py", "run_align_r1_smoke.py"):
            (repo / "scripts" / name).write_text("")
        config, soak = root / "config", root / "soak"
        config.write_text("{}"); soak.write_text("{}")
        args = SimpleNamespace(repo=repo, config=config, soak_reference=soak, output=root / "out",
            python_bin=Path(sys.executable), runner_kind=kind, checks=checks, keep_going=keep_going,
            magistrate_pid=1234, deadline=1000 + seconds, custody_root=root / "custody", exit_wait_seconds=180,
            start_wait_seconds=30, disk_path=root, launchctl_bin="fake-launchctl", pmset_bin="fake-pmset",
            pgrep_bin="fake-pgrep", kill_bin="fake-kill")
        for name, value in extra.items():
            setattr(args, name, value)
        with patch.object(module, "pid_alive", return_value=True), patch.object(module.time, "time", return_value=1000), \
             patch.object(module.uuid, "uuid4", return_value=SimpleNamespace(hex="fixed")), \
             patch.object(module.subprocess, "run", side_effect=[subprocess.CalledProcessError(19, []),
                 subprocess.CompletedProcess([], 0, "", "")]):
            with self.assertRaises(subprocess.CalledProcessError):
                module.launch(args)
        job = root / "custody/r0-launches/fixed"
        return (job / "runner.json").read_bytes(), (job / "com.joulewise.align-r0.fixed.plist").read_bytes()

    def test_r0_runner_json_and_plist_bytes_unchanged_and_r1_has_exit_timeout(self):
        source = subprocess.check_output(["git", "show", "2d54da7e9:scripts/launch_align_r0.py"], cwd=smoke.ROOT, text=True)
        baseline = types.ModuleType("r0_launcher_baseline")
        baseline.__file__ = launcher.__file__
        exec(compile(source, baseline.__file__, "exec"), baseline.__dict__)
        for checks, keep in ((None, True), ("smc,battery", False)):
            outputs = []
            for module in (baseline, launcher):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    outputs.append(tuple(data.replace(str(root).encode(), b"ROOT") for data in
                        self.launch_files(module, root, checks=checks, keep_going=keep)))
            self.assertEqual(*outputs)
            self.assertNotIn("ExitTimeOut", plistlib.loads(outputs[1][1]))
        with tempfile.TemporaryDirectory() as directory:
            _, plist = self.launch_files(launcher, Path(directory), kind="r1-smoke")
            self.assertGreaterEqual(plistlib.loads(plist)["ExitTimeOut"], 2 * launcher.R1_CLEANUP_GRACE_S + 10)

    def test_r1_smoke_plist_runs_interactive_like_the_night_templates(self):
        # RUN_STATE 274: under the default ProcessType the smoke's 300 s idle
        # capture ran at ~240 ms a frame and hit its 460 s timeout; the night
        # templates W1 runs under declare Interactive (~130 ms a frame).
        for name in ("com.joulewise.night.plist.template", "com.joulewise.night-probe.plist.template"):
            text = (smoke.ROOT / "configs/launchd" / name).read_text()
            self.assertIn("<key>ProcessType</key><string>Interactive</string>", text)
        with tempfile.TemporaryDirectory() as directory:
            _, plist = self.launch_files(launcher, Path(directory), kind="r1-smoke")
            self.assertEqual("Interactive", plistlib.loads(plist).get("ProcessType"))

    def test_launch_refuses_deadline_shorter_than_caps_dwell_and_grace(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "deadline cannot fit"):
                self.launch_files(launcher, Path(directory), kind="r1-smoke",
                                  seconds=launcher.r1_minimum_seconds() - 1)
            self.assertFalse((Path(directory) / "custody").exists())

    def test_r0_argv_is_byte_identical_and_r1_has_no_keep_going(self):
        args = SimpleNamespace(repo=Path("/synthetic/repo"), python_bin=Path("/synthetic/python"),
                               config=Path("/synthetic/config"), output=Path("/synthetic/new"), checks=None,
                               keep_going=True, runner_kind="r0", soak_reference=None, deadline=1234, pmset_bin="fake-pmset")
        expected = ["/synthetic/python", "/synthetic/repo/scripts/align_r0_checks.py", "--config",
                    "/synthetic/config", "--output", "/synthetic/new", "--keep-going"]
        self.assertEqual(json.dumps(launcher.runner_argv(args)), json.dumps(expected))
        args.checks = "smc,battery"; args.keep_going = False
        self.assertEqual(launcher.runner_argv(args), expected[:-1] + ["--checks", "smc,battery"])
        args.runner_kind = "r1-smoke"; args.soak_reference = Path("/synthetic/soak")
        argv = launcher.runner_argv(args)
        self.assertEqual(argv, ["/synthetic/python", "/synthetic/repo/scripts/run_align_r1_smoke.py",
            "--output", "/synthetic/new", "--soak-reference", "/synthetic/soak", "--deadline", "1234",
            "--pmset-bin", "fake-pmset"])

    def test_caps_derive_post_g0_budget_from_runtime_config(self):
        from joulewise.align.apple import r1_runtime as rt
        self.assertEqual(launcher.r1_part_caps(), {"A": 3120, "B": 5720})
        with patch.object(rt, "smoke_post_g0_budget", return_value={"total": 3333}) as budget:
            self.assertEqual(launcher.r1_part_caps(), {"A": 3120, "B": 6453})
            budget.assert_called_once_with(rt.STEP_QUIET_S, 1580)

    def test_r1_outer_run_does_not_dwell_before_feeds_and_allows_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = Path(directory) / "runner.json"
            spec.write_text(json.dumps({"kind": "r1-smoke", "argv": ["fake-python", "fake-runner"]}))
            args = SimpleNamespace(deadline=time.time() + 7200, runner_spec=spec, pmset_bin="fake-pmset")
            with patch.object(launcher, "sleep_display") as display, patch.object(launcher.time, "sleep") as sleep, \
                 patch.object(launcher.signal, "signal"), patch.object(launcher.subprocess, "Popen") as popen:
                popen.return_value.wait.return_value = 0
                popen.return_value.poll.return_value = 0
                self.assertEqual(launcher.run_until_deadline(args), 0)
                display.assert_not_called(); sleep.assert_not_called()
                self.assertEqual(popen.call_args.args[0], ["fake-python", "fake-runner"])
                self.assertLess(popen.return_value.wait.call_args.kwargs["timeout"], 7200 - 170)

    def test_real_launchagent_handoff_runs_engine_and_cleans_on_term(self):
        from tests.test_magistrate_desk_fence import LaunchAgentTests
        for terminate in (False, True):
            with self.subTest(terminate=terminate):
                h = LaunchAgentTests()
                real_temp = tempfile.TemporaryDirectory
                with patch.object(tempfile, "TemporaryDirectory", side_effect=lambda **kw: real_temp(prefix="jw-r1-smoke-fixture-", **kw)):
                    h.setUp()
                self.addCleanup(h.doCleanups)
                def cleanup_feeds(h=h):
                    h.stop_worker()
                    path = h.output / smoke.driver.METER_JOURNAL
                    if path.exists():
                        for line in path.read_text().splitlines():
                            event = json.loads(line)
                            if event["event"] == "start":
                                try:
                                    os.killpg(event["pid"], signal.SIGTERM)
                                except ProcessLookupError:
                                    pass
                self.addCleanup(cleanup_feeds)
                # Copy only the launcher/wrapper into the synthetic fixture.
                # The kit budget still comes from this checkout's config.
                from tests import test_magistrate_desk_fence as desk
                source = getattr(launcher, "_fixture_source", Path(launcher.__file__).read_text())
                source = source.replace('repo = Path(__file__).resolve().parents[1]', f'repo = Path({str(smoke.ROOT)!r})')
                source = source.replace('            handoff(args)\n',
                    '            Path(os.environ["WP10_FIXTURE_ROOT"]).joinpath("handoff-entered").touch()\n'
                    '            handoff(args)\n'
                    '            Path(os.environ["WP10_FIXTURE_ROOT"]).joinpath("handoff-returned").touch()\n')
                fixture_launcher = h.root / "launch_align_r0.py"
                fixture_launcher.write_text(source)
                (h.root / "run_align_r0_launchagent.sh").write_bytes(
                    (smoke.ROOT / "scripts/run_align_r0_launchagent.sh").read_bytes())
                (h.repo / "scripts/run_align_r1_smoke.py").write_text(
                    "import os,sys,subprocess,signal\n"
                    "from pathlib import Path\n"
                    f"sys.path.insert(0, {str(smoke.ROOT)!r})\n"
                    "from scripts import run_align_r1_smoke as s\n"
                    "from tests.test_b5_driver_p3 import fake_meter_argv\n"
                    "root=Path(os.environ['WP10_FIXTURE_ROOT'])\n"
                    "s.ROOT=root/'measurement'\n"
                    "def host(argv):\n"
                    "    code,out=0,''\n"
                    "    if '-g' in argv and 'batt' in argv: out=\"Now drawing from 'AC Power'\\n\"\n"
                    "    elif '-g' in argv and 'custom' in argv: out='AC Power:\\n powermode 0\\n'\n"
                    "    elif '-g' in argv or '-lf' in argv:\n"
                    "        code=1\n"
                    "        if '-g' in argv:\n"
                    "            try: os.killpg(int(argv[argv.index('-g')+1]),0); code=0\n"
                    "            except ProcessLookupError: pass\n"
                    "    return subprocess.CompletedProcess(argv,code,out,'')\n"
                    "s.host_run=host\n"
                    "s.powermode._run=host\n"
                    "s.night.observe_identity=lambda pid: type('Identity',(),{'state':'LIVE','start_time':'fixture-start'})()\n"
                    "s.condition13=lambda:{'rc':0,'fixture':True}\n"
                    "s.display=lambda *_:{'rc':0,'fixture':True}\n"
                    "original=s.driver.production_seams\n"
                    "def seams(repo):\n"
                    "    result=original(repo); result.meter_argv=fake_meter_argv(); return result\n"
                    "s.driver.production_seams=seams\n"
                    "s.night._group_census=lambda pgid,timeout_s=1: (host(['/fake/pgrep','-lf','-g',str(pgid),'.']).returncode==1,[])\n"
                    "os.environ[s.powermode.HOST_STATE_ENV]=str(root/'host-power')\n"
                    "raise SystemExit(s.main())\n")
                (h.repo / "scripts/align_r1_followup_kit.py").write_text(
                    "import json,os,sys,time\nfrom pathlib import Path\n"
                    "part=sys.argv[sys.argv.index('--part')+1]\n"
                    "output=Path(sys.argv[sys.argv.index('--output')+1]); output.mkdir()\n"
                    "(output/'started').write_text(str(os.getpid()))\n"
                    f"time.sleep({10 if terminate else .05})\n")
                soak = h.root / "soak.json"
                soak.write_text("{}")
                with patch.object(desk, "SCRIPT", fixture_launcher):
                    result = h.launch("--runner-kind", "r1-smoke", "--soak-reference", str(soak),
                                      "--deadline", str(time.time() + 11400))
                self.assertEqual(result.returncode, 0, result.stderr)
                h.wait_for(lambda: (h.root / "handoff-entered").exists())
                # Keep the owner alive beyond the .5 s dwell seam: a skipped
                # handoff wait must produce output while this witness watches.
                until = time.monotonic() + 1.5
                while time.monotonic() < until:
                    self.assertIsNone(h.owner.poll())
                    self.assertFalse((h.root / "handoff-returned").exists(), "handoff returned before magistrate exit")
                    self.assertFalse(h.output.exists(), "R1 output before magistrate exit")
                    self.assertFalse((h.output / smoke.driver.METER_JOURNAL).exists())
                    time.sleep(.03)
                h.owner.terminate(); h.owner.wait(timeout=5)
                if terminate:
                    h.wait_for(lambda: (h.output / "part-a/started").exists(), timeout=15)
                    os.kill(int((h.root / "worker.pid").read_text()), signal.SIGTERM)
                h.wait_for(lambda: (h.root / "worker.done").exists(), timeout=15)
                receipt = json.loads((h.output / "runner_receipt.json").read_text())
                self.assertEqual(receipt["rc"], 143 if terminate else 0, h.logs())
                self.assertEqual(receipt["parts"], {"A": True, "B": not terminate})
                self.assertTrue(receipt["feeds"]["meter"]["stop"]["proven_stopped"])
                self.assertFalse((h.custody / launcher.FENCE_NAME).exists())
                self.assertFalse((h.root / "service.loaded").exists())
                for row in (h.output / smoke.driver.METER_JOURNAL).read_text().splitlines():
                    event = json.loads(row)
                    if event["event"] == "start":
                        with self.assertRaises(ProcessLookupError):
                            os.kill(event["pid"], 0)
                for name in ("part-a", "part-b"):
                    path = h.output / name / "started"
                    if path.exists():
                        with self.assertRaises(ProcessLookupError):
                            os.kill(int(path.read_text()), 0)


# RUN_STATE 276: wall seconds observed on the MBP (timestamps only). Part A
# must fit all of them with the full G0 cap; the old 1,800 s could not.
SMOKE_276_PREDECESSOR_S = 551.3      # capture-predecessor-30b runtime span, smoke 276
SMOKE_276_STEP_D_PRE_G0_S = 521.6    # step-d runtime start to G0 entry (R1 night: 518.1, 516.0)
R1_STEP_D_AFTER_G0_CLOSE_S = 134.6   # R1 night step-d G0 end to runtime end (max of two)


class SmokeAdmissionBudgetTests(unittest.TestCase):
    """Part A = predecessor + step-D start-up + full G0 cap + close (RUN_STATE 276)."""

    def need(self):
        config = json.loads((launcher.Path(launcher.__file__).resolve().parents[1]
                             / "configs/align/v4/r1_runtime.json").read_text())
        from joulewise.align.apple import r1_runtime as rt
        return (SMOKE_276_PREDECESSOR_S + SMOKE_276_STEP_D_PRE_G0_S + rt.g0_timeout_s(config)
                + R1_STEP_D_AFTER_G0_CLOSE_S)

    def test_part_a_budget_covers_predecessor_pre_g0_full_g0_cap_and_close(self):
        from joulewise.align.apple import r1_runtime as rt
        self.assertGreaterEqual(rt.SMOKE_ADMISSION_S, self.need())
        self.assertEqual(rt.SMOKE_ADMISSION_S, 3000)
        post_g0 = rt.smoke_post_g0_budget(rt.STEP_QUIET_S, 1580)["total"]
        self.assertEqual(post_g0, 2600)   # the Part B watchdog after G0 is unchanged
        self.assertEqual(launcher.r1_part_caps(),
                         {"A": rt.SMOKE_ADMISSION_S + 120, "B": rt.SMOKE_ADMISSION_S + post_g0 + 120})
        self.assertEqual(launcher.r1_minimum_seconds(), 3120 + 5720 + 300 + 2 * 180 + 10)

    def test_runtime_pre_g0_watchdog_is_the_admission_budget(self):
        from joulewise.align.apple import r1_runtime as rt

        class Stop(Exception):
            pass

        def segment(**_):
            return SimpleNamespace(run=lambda: (_ for _ in ()).throw(Stop()), close=lambda: [])

        root = launcher.Path(launcher.__file__).resolve().parents[1]
        for part in ("A", "B"):
            with self.subTest(part=part), tempfile.TemporaryDirectory() as tmp, \
                    patch.object(rt, "read_soak_reference", return_value={}), \
                    patch.object(rt, "Segment", side_effect=segment), \
                    patch.object(rt.time, "monotonic", return_value=1.0), \
                    patch.object(rt.signal, "setitimer") as timer, \
                    patch.object(rt, "SmokeWatchdog") as watchdog:
                code = rt.main(["--config", str(root / "configs/align/v4/r1_runtime.json"),
                                "--r1-kind", "step-d", "--output", str(Path(tmp) / "out"),
                                "--smoke-part", part, "--smoke-started", "0"],
                               backend_factory=lambda _config: SimpleNamespace(close=lambda: None),
                               stdout=__import__("io").StringIO())
                self.assertNotEqual(code, 0)
                timer.assert_not_called()                 # RUN_STATE 278: ITIMER_REAL is the deadman's
                armed = watchdog.return_value.set.call_args_list[0].args
                self.assertGreaterEqual(armed[0] + 1.0, self.need())
                self.assertEqual(armed, (rt.SMOKE_ADMISSION_S - 1.0,))
                watchdog.return_value.stop.assert_called_once_with()

    def test_g0_released_after_1800_s_but_inside_budget_admits_and_stops_part_a(self):
        from joulewise.align.apple import r1_runtime as rt
        for elapsed, admits in ((2300.0, True), (rt.SMOKE_ADMISSION_S + 1.0, False)):
            with self.subTest(elapsed=elapsed), tempfile.TemporaryDirectory() as tmp:
                segment = object.__new__(rt.Segment)
                segment.kind, segment.out, segment.smoke_part, segment.smoke_started = "step-d", Path(tmp), "A", 0
                segment.smoke_watchdog = unittest.mock.Mock()
                session = SimpleNamespace(reference={"fast_c": 40., "slow_c": 40.},
                                          wait=lambda *a, **kw: {"outcome": "released"})
                with patch.object(rt.time, "monotonic", return_value=elapsed), \
                        patch.object(rt.signal, "setitimer") as timer, \
                        patch.object(rt, "rearm_deadman") as rearm:
                    segment.reference_hook({}, quiet_s=300, rearm_s=1580, capture=True)(session)
                    if admits:
                        self.assertEqual(session.wait("G0", deadman="d")["outcome"], "released")
                        timer.assert_not_called()
                        segment.smoke_watchdog.set.assert_called_once_with(0)   # Part A disarms after G0
                        rearm.assert_called_once_with("d", 0, "R1_smoke_A_stop_after_G0")
                    else:
                        with self.assertRaisesRegex(rt.RuntimeFailure, "did not release within 3000 s"):
                            session.wait("G0", deadman="d")
                self.assertEqual(json.loads((Path(tmp) / "smoke_part_a.json").read_text())["admission_s"], elapsed)

    def test_kit_part_a_checks_use_the_admission_budget(self):
        from joulewise.align.apple import thermal_gates
        from scripts import align_r1_followup_kit as kit

        def invoke(runtime, kind, out, **kwargs):
            if kind == "capture-predecessor-30b":
                return {"synthetic": True}
            out.mkdir(parents=True)
            (out / "smoke_part_a.json").write_text("{}")
            (out / kit.rt.CUSTODY_NAME).write_text(json.dumps({"files": {"runs/member/config.json": "a" * 64}}))
            return {"bundle": "runs/member"}

        runtime = ["synthetic", "--config", str(kit.ROOT / kit.r1.DEFAULT_RUNTIME_CONFIG)]
        budget = kit.rt.SMOKE_ADMISSION_S
        cases = (([0, 1900, 2500], None),                      # smoke 276's timing admits
                 ([0, budget, budget], "exhausted at predecessor"),
                 ([0, 1900, budget + 1], f"exceeded {budget} s including close"))
        for clock, refusal in cases:
            with self.subTest(clock=clock), tempfile.TemporaryDirectory() as tmp, \
                    patch.object(kit.reg, "verify_r1_executed_sources"), \
                    patch.object(thermal_gates, "load_window_reference", return_value=({}, {})), \
                    patch.object(kit, "time", SimpleNamespace(monotonic=iter(clock).__next__)):
                if refusal is None:
                    self.assertEqual(kit.smoke(Path(tmp) / "s", "A", runtime, soak_reference="x",
                                               invoke=invoke)["part"], "A")
                else:
                    with self.assertRaisesRegex(ValueError, refusal):
                        kit.smoke(Path(tmp) / "s", "A", runtime, soak_reference="x", invoke=invoke)


class SmokeTimerOwnerTests(unittest.TestCase):
    """RUN_STATE 278: ITIMER_REAL has one owner, the episode deadman.

    These run the REAL EpisodeDeadman.guard on a SystemClock, so its WP8
    refusal ("cannot replace an active timer") is live, not faked."""

    def setUp(self):
        self.previous_alarm = signal.getsignal(signal.SIGALRM)
        self.addCleanup(signal.signal, signal.SIGALRM, self.previous_alarm)
        self.addCleanup(signal.setitimer, signal.ITIMER_REAL, 0)
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL), (0.0, 0.0))

    def guarded(self, deadman):
        try:
            with deadman.guard():
                return signal.getitimer(signal.ITIMER_REAL)[0]
        except RuntimeError as error:
            self.fail(f"the smoke stole the deadman's timer: {error}")

    def test_part_b_post_g0_turn_arms_the_real_episode_deadman(self):
        from joulewise.align.apple import r1_runtime as rt
        from joulewise.align.apple.budget import EpisodeDeadman
        from joulewise.clock import SystemClock
        clock = SystemClock()
        with tempfile.TemporaryDirectory() as tmp:
            segment = object.__new__(rt.Segment)
            segment.kind, segment.out, segment.smoke_part = "step-d", Path(tmp), "B"
            segment.smoke_started, segment.quiet_spans = rt.time.monotonic(), []
            if hasattr(rt, "SmokeWatchdog"):
                segment.smoke_watchdog = rt.SmokeWatchdog(send=lambda *a: self.fail("watchdog fired"))
                self.addCleanup(segment.smoke_watchdog.stop)
            session = SimpleNamespace(reference={"fast_c": 40., "slow_c": 40.}, flags=[],
                                      wait=lambda *a, **kw: {"outcome": "released"})
            deadman = EpisodeDeadman(clock, clock.stamp(), 5)
            segment.reference_hook({}, quiet_s=0, rearm_s=1580, capture=True)(session)
            self.assertEqual(session.wait("G0", deadman=deadman)["outcome"], "released")
            # The re-armed turn: the workload's first guarded model call.
            armed = self.guarded(deadman)
            self.assertGreater(armed, 1500)            # the deadman's 1,580 s, not the smoke's 2,600 s
            self.assertLessEqual(armed, 1580)
            self.assertEqual(signal.getitimer(signal.ITIMER_REAL), (0.0, 0.0))
            total = rt.smoke_post_g0_budget(0, 1580)["total"]   # quiet 0 here: 1,580 + 600 + 120
            left = segment.smoke_watchdog.deadline - rt.time.monotonic()
            self.assertGreater(left, total - 10)        # the post-G0 watchdog is still armed, off the itimer
            self.assertLessEqual(left, total)

    def test_pre_g0_guarded_call_runs_under_the_smoke_admission_watchdog(self):
        from joulewise.align.apple import r1_runtime as rt
        from joulewise.align.apple.budget import EpisodeDeadman
        from joulewise.clock import SystemClock
        seen = {}

        def run():
            clock = SystemClock()
            seen["timer"] = self.guarded(EpisodeDeadman(clock, clock.stamp(), 5))
            seen["watchdog_left"] = fake.smoke_watchdog.deadline - rt.time.monotonic()
            return {"ok": True}

        fake = SimpleNamespace(run=run, close=lambda: [])
        for part in ("A", "B"):
            with self.subTest(part=part), tempfile.TemporaryDirectory() as tmp, \
                    patch.object(rt, "read_soak_reference", return_value={}), \
                    patch.object(rt, "Segment", return_value=fake):
                seen.clear()
                before = signal.getsignal(signal.SIGUSR1)
                code = rt.main(["--config", str(REPO / "configs/align/v4/r1_runtime.json"),
                                "--r1-kind", "step-d", "--output", str(Path(tmp) / "out"),
                                "--smoke-part", part, "--smoke-started", str(rt.time.monotonic())],
                               backend_factory=lambda _config: SimpleNamespace(close=lambda: None),
                               stdout=io.StringIO())
                self.assertEqual(code, 0, json.loads((Path(tmp) / "out" / rt.CUSTODY_NAME).read_text()))
                self.assertGreater(seen["timer"], 4)
                self.assertGreater(seen["watchdog_left"], rt.SMOKE_ADMISSION_S - 10)
                self.assertFalse(fake.smoke_watchdog.active)          # stopped by main's finally
                self.assertEqual(signal.getitimer(signal.ITIMER_REAL), (0.0, 0.0))
                self.assertEqual(signal.getsignal(signal.SIGUSR1), before)  # handler restored

    def test_runs_without_a_step_d_smoke_part_start_no_watchdog_and_touch_no_timer(self):
        from joulewise.align.apple import r1_runtime as rt

        class Stop(Exception):
            pass

        def segment(**_):
            return SimpleNamespace(run=lambda: (_ for _ in ()).throw(Stop()), close=lambda: [])

        for extra in (["--r1-kind", "step-d"], ["--r1-kind", "step-30b"],
                      ["--r1-kind", "step-30b", "--smoke-part", "A", "--smoke-started", "0"]):
            before = signal.getsignal(signal.SIGUSR1)
            with self.subTest(argv=extra), tempfile.TemporaryDirectory() as tmp, \
                    patch.object(rt, "read_soak_reference", return_value={}), \
                    patch.object(rt, "Segment", side_effect=segment), \
                    patch.object(rt.signal, "setitimer") as timer, \
                    patch.object(rt, "SmokeWatchdog") as watchdog:
                code = rt.main(["--config", str(REPO / "configs/align/v4/r1_runtime.json"),
                                "--output", str(Path(tmp) / "out"), *extra],
                               backend_factory=lambda _config: SimpleNamespace(close=lambda: None),
                               stdout=io.StringIO())
                self.assertNotEqual(code, 0)
                timer.assert_not_called()
                watchdog.assert_not_called()
                self.assertEqual(signal.getsignal(signal.SIGUSR1), before)

    def test_watchdog_fires_once_on_the_main_thread_and_disarms_and_stops(self):
        from joulewise.align.apple import r1_runtime as rt

        class Fired(Exception):
            pass

        def handler(_sig, _frame):
            raise Fired()

        previous = signal.signal(rt.SMOKE_WATCHDOG_SIGNAL, handler)
        self.addCleanup(signal.signal, rt.SMOKE_WATCHDOG_SIGNAL, previous)
        watchdog = rt.SmokeWatchdog()
        self.addCleanup(watchdog.stop)
        watchdog.set(0.05)
        with self.assertRaises(Fired):
            time.sleep(5)                               # interrupted, as the itimer interrupted a sleep
        self.assertIsNone(watchdog.deadline)            # one shot
        watchdog.set(0.05)
        watchdog.set(0)                                 # 0 disarms, like setitimer(..., 0)
        time.sleep(0.3)
        watchdog.set(0.05)
        watchdog.stop()                                 # stop: nothing is sent afterwards
        time.sleep(0.3)
        self.assertFalse(watchdog.active)
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL), (0.0, 0.0))


class MutantTests(unittest.TestCase):
    def test_required_regressions_are_killed_by_the_witnesses(self):
        # Compile one changed source in isolation; never edit a condition-13
        # file or execute a live command. The witnesses must fail, not error.
        mutations = [
            ("launcher", '*(["--keep-going"] if args.keep_going else [])', '*[]',
             LauncherTests, "test_r0_argv_is_byte_identical_and_r1_has_no_keep_going"),
            ("smoke", 'step("read_power", read_owned_power)', 'step("read_power", lambda: {})',
             RunnerTests, "test_order_and_receipt"),
            ("smoke", 'if fatal and row["rc"]:', 'if fatal and row["rc"] and name != "part-A":',
             RunnerTests, "test_part_b_skipped_on_part_a_nonzero_without_retry"),
            ("smoke", 'for f in reversed(feeds)', 'for f in reversed(feeds) if f.name != "meter"',
             RunnerTests, "test_every_failure_path_stops_all_feeds_and_writes_receipt"),
            ("smoke", 'for f in reversed(feeds)', 'for f in reversed(feeds) if f.name != "agents"',
             RunnerTests, "test_every_failure_path_stops_all_feeds_and_writes_receipt"),
            ("smoke", 'for f in reversed(feeds)', 'for f in reversed(feeds) if f.name != "volumes"',
             RunnerTests, "test_every_failure_path_stops_all_feeds_and_writes_receipt"),
            ("smoke", 'proven = night._terminate_process_group(child, evidence=proof)', 'proven = True',
             ProductionSeamTests, "test_part_proves_group_absence_even_when_leader_already_exited"),
            ("smoke", '"sha256": digest', '"sha256": "0" * 64', RunnerTests, "test_order_and_receipt"),
            ("smoke", 'or re.search(r"(?:^|\\s)com\\.joulewise\\.night\\S*", result.stdout)', '',
             ProductionSeamTests, "test_ac_and_loaded_wildcard_night_agent_refuse"),
            ("smoke", 'reg.verify_r1_executed_sources(ROOT, {"executed_commit": result.stdout.strip()})',
             'result.stdout.strip()', ProductionSeamTests, "test_condition13_drift_is_not_caught_or_cached"),
            ("smoke", 'if not readiness["ready"]:', 'if False:', ProductionSeamTests,
             "test_meter_missing_dc_in_batch_refuses_and_is_still_stoppable"),
            ("smoke", 'cap = launcher.r1_part_caps()[which]', 'cap = 1800', ProductionSeamTests,
             "test_part_b_may_finish_after_1800_seconds"),
            ("smoke", 'if remaining < cap:', 'if False:', ProductionSeamTests,
             "test_full_part_cap_must_fit_before_spawn"),
            ("launcher", 'while pid_alive(args.magistrate_pid):', 'while False:', LauncherTests,
             "test_real_launchagent_handoff_runs_engine_and_cleans_on_term"),
        ]
        for target, before, after, case, name in mutations:
            with self.subTest(witness=name, mutation=after):
                original = globals()[target]
                source = Path(original.__file__).read_text()
                self.assertEqual(source.count(before), 1)
                candidate = types.ModuleType("r1_smoke_mutant")
                candidate.__file__ = original.__file__
                exec(compile(source.replace(before, after), original.__file__, "exec"), candidate.__dict__)
                candidate._fixture_source = source.replace(before, after)
                result = unittest.TestResult()
                with patch.dict(globals(), {target: candidate}):
                    case(name).run(result)
                self.assertTrue(result.failures, (name, result.errors))
                self.assertFalse(result.errors, result.errors)


class FreshSoakPartATests(unittest.TestCase):
    """RL-89/RL-94: --fresh-soak runs the night's idle soak first; --parts A stops after A."""
    operation, feed, run_runner, receipt = (RunnerTests.operation, RunnerTests.feed,
                                            RunnerTests.run_runner, RunnerTests.receipt)

    def setUp(self):
        RunnerTests.setUp(self)
        self.args.soak_reference = None
        self.args.fresh_soak, self.args.parts = True, "A"
        original = self.operation("part")

        def part(*args, **kwargs):
            if args[1] == "soak":
                self.events.append("part-soak")
                path = self.args.output / "soak" / "soak_reference.json"
                path.parent.mkdir(parents=True)
                path.write_text("{}")
                return {"rc": 0}
            self.assertEqual(self.args.soak_reference, self.args.output / "soak" / "soak_reference.json")
            return original(*args, **kwargs)
        self.stack.enter_context(patch.object(smoke, "part", side_effect=part))

    def test_order_and_receipt(self):
        self.assertEqual(self.run_runner(), 0)
        self.assertEqual(self.events, ["night_agents", "ac_power", "condition13", "start-meter",
            "start-agents", "start-volumes", "read_power", "display", "dwell", "part-soak", "part-A",
            "restore", "stop-volumes", "stop-agents", "stop-meter"])
        receipt = self.receipt()
        self.assertEqual(receipt["parts"], {"A": True, "B": False})
        self.assertEqual((receipt["fresh_soak"], receipt["parts_requested"]), (True, "A"))
        self.assertEqual(receipt["soak_reference"], str(self.args.output / "soak" / "soak_reference.json"))
        soak = next(s for s in receipt["steps"] if s["name"] == "soak")
        self.assertEqual(soak["result"]["soak_reference_sha256"], hashlib.sha256(b"{}").hexdigest())

    def test_soak_failure_runs_no_part(self):
        self.fault_step = None
        with patch.object(smoke, "part", side_effect=lambda *a, **k: {"rc": 3}):
            self.assertEqual(self.run_runner(), 3)
        self.assertEqual(self.receipt()["parts"], {"A": False, "B": False})
        self.assertIsNone(self.receipt()["soak_reference"])
        self.assertFalse(self.live)

    def test_part_a_failure_after_soak_stops_and_cleans(self):
        self.fault_step = "part-A"
        self.assertEqual(self.run_runner(), 2)
        self.assertEqual(self.events[-5:], ["part-A", "restore", "stop-volumes", "stop-agents", "stop-meter"])
        self.assertFalse(self.live)


class SoakChildTests(unittest.TestCase):
    def soak_result(self, slope=0.0):
        times = [float(t) for t in range(1801)]
        series = {key: [30.0 + slope * t / 60.0 + (0.01 if t % 2 else 0.0) for t in times] for key in ("TV0h", "Th0C")}
        return {"sensor_series_c": series, "sensor_series_t_s": {k: times for k in series},
                "sensor_series_end_t_s": 1800.0, "sensor_roles": {"s_fast": "TV0h", "s_slow": "Th0C"},
                "cpu_busy_cores": [0.1] * 1801, "cpu_busy_t_s": times, "census": [{"ok": True}]}

    def run_child(self, result, *, batch=False):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "soak"
            calls = []
            def invoke(runtime, kind, output, duration=None, **kwargs):
                calls.append((kind, Path(output).name, duration, kwargs))
                return result
            def wait(seconds, *, sleep):
                if batch:
                    sleep(60.0)
                return 0.0
            with patch.object(smoke.reg, "verify_r1_executed_sources"), \
                 patch.object(smoke.r1, "executed_commit", return_value="0" * 40), \
                 patch.object(smoke.r1, "runtime_argv_from_inputs", return_value=["runtime"]), \
                 patch.object(smoke.r1, "wait_outside_os_batch", side_effect=wait), \
                 patch.object(smoke.r1, "_invoke", side_effect=invoke):
                path = smoke.soak_child(out, Path(directory) / "inputs.json")
                return calls, json.loads(path.read_text())

    def test_night_idle_soak_path_and_reference(self):
        calls, reference = self.run_child(self.soak_result())
        self.assertEqual(calls, [("idle", "idle_soak", smoke.soak_seconds(),
                                  {"quiet": True, "contract_key": "idle_soak"})])
        self.assertEqual(smoke.soak_seconds(), 1800.0)
        self.assertEqual(reference["schema"], smoke.r1.SOAK_REFERENCE_SCHEMA)
        self.assertEqual(set(reference["sensors_c"]), {"TV0h", "Th0C"})
        self.assertEqual(reference["sensor_roles"], {"s_fast": "TV0h", "s_slow": "Th0C"})
        self.assertTrue(all(v["settled"] for v in reference["detrended"].values()))

    def test_unsettled_soak_and_os_batch_overlap_refuse(self):
        with self.assertRaisesRegex(ValueError, "unresolved slope"):
            self.run_child(self.soak_result(slope=0.5))
        with self.assertRaisesRegex(ValueError, "OS batch"):
            self.run_child(self.soak_result(), batch=True)

    def test_launcher_argv_minimum_and_cap(self):
        args = SimpleNamespace(repo=Path("/synthetic/repo"), python_bin=Path("/synthetic/python"),
                               output=Path("/synthetic/new"), runner_kind="r1-smoke", soak_reference=None,
                               fresh_soak=True, parts="A", deadline=1234, pmset_bin="fake-pmset")
        self.assertEqual(launcher.runner_argv(args), ["/synthetic/python",
            "/synthetic/repo/scripts/run_align_r1_smoke.py", "--output", "/synthetic/new", "--fresh-soak",
            "--parts", "A", "--deadline", "1234", "--pmset-bin", "fake-pmset"])
        self.assertEqual(launcher.r1_soak_cap_s(), 1800 + 30 + 120)
        self.assertEqual(launcher.r1_minimum_seconds("A", True), 3120 + 1950 + 300 + 2 * 180 + 10)
        self.assertEqual(launcher.r1_minimum_seconds(), 3120 + 5720 + 300 + 2 * 180 + 10)

    def test_launch_fresh_soak_part_a_spec_and_deadline(self):
        helper = LauncherTests()
        with tempfile.TemporaryDirectory() as directory:
            spec, _ = helper.launch_files(launcher, Path(directory), kind="r1-smoke", soak_reference=None,
                                          fresh_soak=True, parts="A",
                                          seconds=launcher.r1_minimum_seconds("A", True))
            argv = json.loads(spec)["argv"]
            self.assertIn("--fresh-soak", argv)
            self.assertNotIn("--soak-reference", argv)
            self.assertEqual(argv[argv.index("--parts") + 1], "A")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "deadline cannot fit"):
                helper.launch_files(launcher, Path(directory), kind="r1-smoke", soak_reference=None,
                                    fresh_soak=True, parts="A",
                                    seconds=launcher.r1_minimum_seconds("A", True) - 1)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "not both"):
                helper.launch_files(launcher, Path(directory), kind="r1-smoke", fresh_soak=True)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "r1-smoke only"):
                helper.launch_files(launcher, Path(directory), parts="A")

    def test_runner_cli_takes_exactly_one_soak_source(self):
        for argv in (["--output", "/x", "--deadline", "1"],
                     ["--output", "/x", "--deadline", "1", "--fresh-soak", "--soak-reference", "/s"]):
            with self.assertRaises(SystemExit), patch("sys.stderr", io.StringIO()):
                smoke.main(argv)


if __name__ == "__main__":
    unittest.main()
