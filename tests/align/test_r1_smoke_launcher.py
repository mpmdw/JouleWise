"""Agent-free handoff and orchestration; host commands and data are synthetic."""
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import types
import unittest
from unittest.mock import patch

from scripts import launch_align_r0 as launcher
from scripts import run_align_r1_smoke as smoke


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.args = SimpleNamespace(output=self.root / "capture", soak_reference=self.root / "soak.json",
                                    deadline=time.time() + 7200)
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
        self.assertEqual(self.events, ["ac_power", "night_agents", "condition13", "start-meter",
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
                feed_v.watch.records = [{"point": "sample", "verdict": "PASS"}]
                for feed in (feed_a, feed_v):
                    feed.start(); feed.start(); feed.stop(); feed.stop(); feed.poll()
                self.assertEqual(agents.call_count, 1)
                self.assertEqual(append.call_count, 1)
                self.assertEqual(volumes.call_count, 1)
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
                supervisor.call_args.args[0]()
                self.assertEqual(seams.return_value.meter_argv.call_count, 1)

    def test_restore_never_sets_mode_under_another_nights_lock(self):
        with patch.object(smoke.powermode, "HostLock") as lock, \
             patch.object(smoke.powermode, "restore_automatic") as restore:
            lock.return_value.acquire.return_value = False
            with self.assertRaisesRegex(ValueError, "host night lock"):
                smoke.restore_power()
            restore.assert_not_called()
            lock.return_value.release.assert_called_once()

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
                     patch.object(smoke, "PART_LIMIT_S", timeout), \
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
                 patch.object(smoke, "poll_feeds", side_effect=blocked_feed), patch.object(smoke, "PART_LIMIT_S", .05):
                with self.assertRaises(TimeoutError):
                    smoke.part(args, "A", [])


class LauncherTests(unittest.TestCase):
    def test_r0_argv_is_byte_identical_and_r1_has_no_keep_going(self):
        args = SimpleNamespace(repo=Path("/synthetic/repo"), python_bin=Path("/synthetic/python"),
                               config=Path("/synthetic/config"), output=Path("/synthetic/new"), checks=None,
                               keep_going=True, runner_kind="r0", soak_reference=None, deadline=1234)
        expected = ["/synthetic/python", "/synthetic/repo/scripts/align_r0_checks.py", "--config",
                    "/synthetic/config", "--output", "/synthetic/new", "--keep-going"]
        self.assertEqual(json.dumps(launcher.runner_argv(args)), json.dumps(expected))
        args.checks = "smc,battery"; args.keep_going = False
        self.assertEqual(launcher.runner_argv(args), expected[:-1] + ["--checks", "smc,battery"])
        args.runner_kind = "r1-smoke"; args.soak_reference = Path("/synthetic/soak")
        argv = launcher.runner_argv(args)
        self.assertEqual(argv, ["/synthetic/python", "/synthetic/repo/scripts/run_align_r1_smoke.py",
            "--output", "/synthetic/new", "--soak-reference", "/synthetic/soak", "--deadline", "1234"])

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
                    "s.condition13=lambda:{'rc':0,'fixture':True}\n"
                    "s.display=lambda:{'rc':0,'fixture':True}\n"
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
                result = h.launch("--runner-kind", "r1-smoke", "--soak-reference", str(soak),
                                  "--deadline", str(time.time() + 7200))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse(h.output.exists())  # magistrate still alive
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


class MutantTests(unittest.TestCase):
    def test_required_regressions_are_killed_by_the_witnesses(self):
        # Compile one changed source in isolation; never edit a condition-13
        # file or execute a live command. The witnesses must fail, not error.
        mutations = [
            ("launcher", '*(["--keep-going"] if args.keep_going else [])', '*[]',
             LauncherTests, "test_r0_argv_is_byte_identical_and_r1_has_no_keep_going"),
            ("smoke", 'step("read_power", read_power)', 'step("read_power", lambda: {})',
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
        ]
        for target, before, after, case, name in mutations:
            with self.subTest(witness=name, mutation=after):
                original = globals()[target]
                source = Path(original.__file__).read_text()
                self.assertEqual(source.count(before), 1)
                candidate = types.ModuleType("r1_smoke_mutant")
                candidate.__file__ = original.__file__
                exec(compile(source.replace(before, after), original.__file__, "exec"), candidate.__dict__)
                result = unittest.TestResult()
                with patch.dict(globals(), {target: candidate}):
                    case(name).run(result)
                self.assertTrue(result.failures, (name, result.errors))
                self.assertFalse(result.errors, result.errors)


if __name__ == "__main__":
    unittest.main()
