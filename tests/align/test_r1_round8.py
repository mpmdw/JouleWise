"""Lead rulings R8-1, R8-3, R8-4, R8-5 and R8-6 (round 8, 2026-11-07).

* R8-1: an interrupt (INT/TERM/HUP) after the chain launched terminates the
  chain's process group and proves it gone, then the normal close retakes the
  lock and restores; the R1 driver does the same for its runtime and the
  runtime's descendants. Real signals while a real chain or runtime runs.
* R8-3: the runtime's teardown watchdog arms when the first signal is held.
* R8-4: a heavy redo's release bound carries the 65 s pre-roll.
* R8-5: an interrupt during ``--dry-arm`` restores nothing.
* R8-6: aliased picks fail R1's thermometry bar.

Fake sudo/pmset only; nothing real changes the power mode.
"""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

from joulewise.align.apple import powermode
from joulewise.align.apple import r1_runtime as rt
from scripts import align_r1_rehearsal as r1
from tests import test_run_night as rn
from tests.align import test_r1_rehearsal as rehearsal_tests

ROOT = Path(__file__).resolve().parents[2]


def load_tests(loader, tests, pattern):
    """Only this module's own tests (the night cases inherit the
    NightDriverTests fixture, not its tests)."""
    suite = unittest.TestSuite()
    for case in (NightInterruptTests, NightUnprovenCloseTests, SignalLatchTests, R1InterruptTests, TerminateTreeTests, WatchdogArmTests, RedoReleaseBoundTests,
                 DryArmInterruptTests, AliasedPicksBarTests, DocTests):
        names = sorted(name for name in vars(case) if name.startswith("test_"))
        suite.addTests(case(name) for name in names)
    return suite


def gone(pid, timeout_s=10.0):
    """True once ``pid`` no longer exists (an orphan is reaped by launchd)."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            return False
        time.sleep(0.05)
    return False


# A real "chain": it starts a member in its own process group, publishes both
# pids and keeps measuring. ``stubborn`` ignores TERM in both, so only the
# group KILL ends them.
CHAIN = r'''
import json, os, signal, subprocess, sys, time
ready, stubborn = sys.argv[1], sys.argv[2] == "stubborn"
code = "import signal, time\n" + ("signal.signal(signal.SIGTERM, signal.SIG_IGN)\n" if stubborn else "") + "time.sleep(300)\n"
member = subprocess.Popen([sys.executable, "-c", code])
if stubborn:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
with open(ready + ".tmp", "w") as handle:
    json.dump({"chain": os.getpid(), "member": member.pid}, handle)
os.replace(ready + ".tmp", ready)
time.sleep(300)
'''

NIGHT_CHILD = r'''
import json, os, signal, subprocess, sys, time
from pathlib import Path
from unittest import mock
signal.signal(signal.SIGINT, signal.default_int_handler)   # a background parent may have ignored it
from joulewise.align.apple import powermode
from tests import test_run_night as rn
ready, stubborn, chain_code = sys.argv[1], sys.argv[2], sys.argv[3]
case = rn.NightDriverTests("test_status_fake_only_cleans_planned_measurement_root")
case.setUp()
mapping = json.loads(case.plan_path.read_text()); mapping["ac_powermode"] = 2
case.plan_path.write_text(json.dumps(mapping))
host = case._power_host(2)
marker = Path(powermode.host_marker_path())
powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG, owner={"custody_root": case.custody})
real_popen = subprocess.Popen
seen = {}
def spawn(argv, *args, **kwargs):
    if list(argv) == ["/bin/zsh", str(case.chain)]:
        seen["pass_fds"] = list(kwargs.get("pass_fds", ()))
        return real_popen([sys.executable, "-B", "-c", chain_code, ready, stubborn], *args, **kwargs)
    return real_popen(argv, *args, **kwargs)
outcome = {}
try:
    with mock.patch.object(case.driver.subprocess, "Popen", spawn), \
            mock.patch.object(case.driver, "GROUP_WAIT_S", 2):
        outcome["exit"] = case.driver.run_night(case.plan_path)
except BaseException as error:
    outcome["raised"] = type(error).__name__ + ": " + str(error)
night = case.custody / "night"
def alive(pid):
    # Checked here, before the parent's emergency cleanup can kill anything
    # (round-8 Sol critique); an orphan is reaped by launchd within moments.
    for _ in range(100):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        time.sleep(0.05)
    return True
pids = json.loads(Path(ready).read_text()) if Path(ready).exists() else {}
outcome["alive_after"] = {role: alive(pid) for role, pid in pids.items()}
outcome.update(mode=host.mode, marker=marker.exists(), calls=host.calls, pass_fds=seen.get("pass_fds"),
               log=(case.custody / "night.log").read_text(), exited=(night / "chain.exited").exists(),
               unkilled=(night / "chain.unkilled").exists())
print(json.dumps(outcome), flush=True)
'''


class NightInterruptTests(unittest.TestCase):
    """R8-1 in run_night with real signals: a real chain that inherited the
    host night lock is measuring under a plan of 2 when the signal lands."""

    def run_and_signal(self, signum, *, stubborn=False):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            ready = Path(tmp) / "chain.ready"
            child = subprocess.Popen(
                [sys.executable, "-B", "-c", NIGHT_CHILD, str(ready), "stubborn" if stubborn else "plain", CHAIN],
                cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                env=dict(os.environ, PYTHONPATH=str(ROOT), TMPDIR=tmp))
            pids = None
            try:
                deadline = time.monotonic() + 120
                while not ready.exists() and child.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertTrue(ready.exists(), child.stderr.read() if child.poll() is not None else "no chain")
                pids = json.loads(ready.read_text())
                time.sleep(0.5)     # run_night is inside its chain wait loop
                child.send_signal(signum)
                out, err = child.communicate(timeout=180)
            finally:
                if child.poll() is None:
                    child.kill()
                    child.communicate()
                for pid in (pids or {}).values():
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except OSError:
                        pass
        self.assertEqual(child.returncode, 0, err)
        return json.loads(out.strip().splitlines()[-1]), pids

    def check(self, outcome, pids):
        self.assertIn("KeyboardInterrupt", outcome.get("raised", ""))
        self.assertTrue(outcome["pass_fds"])                      # R7-5: the chain held the lock
        self.assertIn("chain terminated on interrupt (lead ruling R8-1)", outcome["log"])
        self.assertIn('"proven": true', outcome["log"])
        self.assertTrue(outcome["exited"])
        self.assertFalse(outcome["unkilled"])
        # The close retook the lock and restored: mode 0, marker gone.
        self.assertNotIn("ac powermode close deferred", outcome["log"])
        self.assertIn("ac powermode close: restore Automatic", outcome["log"])
        self.assertEqual((outcome["mode"], outcome["marker"]), (0, False))
        # Observed by run_night's own process right after it returned, before
        # any cleanup here.
        self.assertEqual(outcome["alive_after"], {"chain": False, "member": False})

    def test_sigterm_while_the_chain_runs_stops_it_and_restores(self):
        self.check(*self.run_and_signal(signal.SIGTERM))

    def test_sighup_while_the_chain_runs_stops_it_and_restores(self):
        self.check(*self.run_and_signal(signal.SIGHUP))

    def test_sigint_on_a_chain_that_ignores_term_is_killed_and_restored(self):
        outcome, pids = self.run_and_signal(signal.SIGINT, stubborn=True)
        self.check(outcome, pids)


# A real runtime: it starts a "heater" that ignores TERM, publishes both pids,
# and on TERM exits at once, orphaning the heater (as a forced exit could).
RUNTIME = (
    "import os, signal, subprocess, sys, time\n"
    "out = sys.argv[sys.argv.index('--output') + 1]\n"
    "os.makedirs(out)\n"
    "heater = subprocess.Popen([sys.executable, '-c', 'import signal, time\\n"
    "signal.signal(signal.SIGTERM, signal.SIG_IGN)\\ntime.sleep(300)\\n'],\n"
    "                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
    "signal.signal(signal.SIGTERM, lambda *_: os._exit(143))\n"
    "open(os.path.join(out, 'pids.tmp'), 'w').write(f'{os.getpid()} {heater.pid}')\n"
    "os.replace(os.path.join(out, 'pids.tmp'), os.path.join(out, 'pids'))\n"
    "time.sleep(300)\n")


class R1InterruptTests(unittest.TestCase):
    """R8-1 in the R1 driver with a real signal while a real runtime (and a
    descendant of it) runs under the adopted High Power."""

    def setUp(self):
        clock = mock.patch.object(r1, "_now_local", lambda: rehearsal_tests.NOON_SAFE)
        clock.start()
        self.addCleanup(clock.stop)
        wait = mock.patch.object(r1, "TREE_STOP_WAIT_S", 1.0)
        wait.start()
        self.addCleanup(wait.stop)
        # The run's termination proofs are module state; never leak an
        # unproven one into a later guard in this process.
        self.addCleanup(r1._CHILD_TERMINATIONS.clear)

    def run_interrupted(self, td, *, extra_patches=()):
        td = Path(td)
        script = td / "runtime.py"
        script.write_text(RUNTIME)
        world = rehearsal_tests.FakeWorld(t_decline={"a1": 20.0, "b": 30.0, "a2": 21.0})
        real_run = r1._run
        segment = td / "run" / "X_G_contrast"
        at_restore = []

        def runner(argv):
            if "--r1-kind" in argv and "x-g" in argv:
                return real_run([sys.executable, str(script), *argv[1:]])
            if tuple(argv) == r1.PowerModeGuard.AUTO and (segment / "pids").exists():
                heater = int((segment / "pids").read_text().split()[1])
                try:
                    os.kill(heater, 0)
                    at_restore.append("heater alive")
                except ProcessLookupError:
                    at_restore.append("heater gone")
            return world(argv)

        done = threading.Event()

        def signal_when_started():
            deadline = time.monotonic() + 60
            while not (segment / "pids").exists() and time.monotonic() < deadline and not done.is_set():
                time.sleep(0.05)
            if (segment / "pids").exists() and not done.wait(0.2):
                os.kill(os.getpid(), signal.SIGTERM)    # only while the runtime is running
        args = rehearsal_tests.R1Tests.args(self, td, include_4bit=False)
        thread = threading.Thread(target=signal_when_started, daemon=True)
        try:
            with mock.patch.object(r1, "_run", runner):
                for patcher in extra_patches:
                    patcher.start()
                try:
                    thread.start()
                    rc = r1.run(args)
                finally:
                    done.set()
                    for patcher in extra_patches:
                        patcher.stop()
        finally:
            done.set()
            if thread.is_alive() or thread.ident is not None:
                thread.join()
            if (segment / "pids").exists():
                for pid in map(int, (segment / "pids").read_text().split()):
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except OSError:
                        pass
        runtime_pid, heater_pid = map(int, (segment / "pids").read_text().split())
        result = json.loads((td / "run/r1_result.json").read_text())
        return rc, world, result, runtime_pid, heater_pid, at_restore

    def test_the_runtime_and_its_descendants_are_proven_gone_before_the_restore(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
            rc, world, result, runtime_pid, heater_pid, at_restore = self.run_interrupted(td)
            self.assertEqual(rc, 4)
            # Nothing of the run lived at the restore (nor at the teardown's
            # idempotent second attempt).
            self.assertTrue(at_restore)
            self.assertEqual(set(at_restore), {"heater gone"})
            self.assertEqual(world.mode, 0)
            self.assertFalse((Path(td) / ".align-r1-high-power").exists())
            self.assertFalse(Path(powermode.host_marker_path()).exists())
            [termination] = result["child_terminations"]
            self.assertTrue(termination["proven"])
            self.assertEqual(termination["pid"], runtime_pid)
            self.assertIn(str(heater_pid), termination["descendants"])
            self.assertEqual(termination["survivors"], {})
            self.assertTrue(gone(heater_pid))
            self.assertNotIn("restore_deferred", result)

    def test_an_unproven_descendant_defers_the_restore(self):
        # A descendant this driver cannot end (as a root powermetrics would be).
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
            stuck = mock.patch.object(r1, "_tree_survivors", lambda tree: dict(tree))
            rc, world, result, _runtime, heater_pid, at_restore = self.run_interrupted(td, extra_patches=(stuck,))
            self.assertEqual(rc, 4)
            self.assertEqual(at_restore, [])                    # no restore ran
            self.assertEqual(world.mode, 2)
            self.assertTrue((Path(td) / ".align-r1-high-power").exists())
            self.assertTrue(Path(powermode.host_marker_path()).exists())
            self.assertFalse(result["child_terminations"][0]["proven"])
            self.assertIn("R8-1", result["restore_deferred"])
            # The lock is free afterwards, so the next session start restores.
            from scripts import align_v4_session as session
            record = session.session_start_restore(Path(td) / "m", runner=world)
            self.assertEqual((record["action"], world.mode), ("restored", 0))


class NightUnprovenCloseTests(rn.NightDriverTests):
    """R8-1 (round-8 Sol critique): an interrupt whose chain termination is not
    proven defers the close even when the lock could be retaken (a survivor
    that does not hold the lock, such as an unsignalable root descendant)."""

    def test_an_unproven_chain_termination_restores_nothing(self):
        mapping = json.loads(self.plan_path.read_text())
        mapping["ac_powermode"] = 2
        self.plan_path.write_text(json.dumps(mapping))
        host = self._power_host(2)
        marker = Path(powermode.host_marker_path())
        powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG, owner={"custody_root": self.custody})
        calls = {"census": 0, "terminate": 0}
        real_census = self.driver.agent_census

        def census(probes):
            calls["census"] += 1
            if calls["census"] >= 2:          # the first in-window census: the signal lands here
                raise KeyboardInterrupt("signal 15")
            return real_census(probes)

        def terminate(*_args, **_kwargs):
            calls["terminate"] += 1
            return False                      # the group could not be proven gone
        spawn = lambda argv, *a, **k: rn.UnkillableProcess(argv)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), \
                mock.patch.object(self.driver, "agent_census", census), \
                mock.patch.object(self.driver, "_terminate_process_group", terminate), \
                self.assertRaises(KeyboardInterrupt):
            self.driver.run_night(self.plan_path)
        self.assertEqual(calls["terminate"], 1)
        log = (self.custody / "night.log").read_text()
        self.assertIn("not proven gone after the interrupt (lead ruling R8-1)", log)
        self.assertNotIn("restore", host.calls)
        self.assertEqual(host.mode, 2)
        self.assertTrue(marker.exists())
        probe = powermode.HostLock(role="probe")            # the close freed the lock
        self.assertTrue(probe.acquire())
        probe.release()
        self.assertIsNone(self.driver._CHAIN_TERMINATION_UNPROVEN)   # cleared for the next night


class SignalLatchTests(unittest.TestCase):
    """R8-1 (round-8 Sol critique): the first TERM/HUP/INT latches the
    shutdown, so a second one cannot escape before the termination begins."""

    def test_a_second_signal_is_swallowed_without_closing(self):
        from scripts import run_night
        _closing, restore = run_night._install_termination_handlers()
        self.addCleanup(restore)
        with self.assertRaises(KeyboardInterrupt):
            os.kill(os.getpid(), signal.SIGTERM)
            time.sleep(1)
        os.kill(os.getpid(), signal.SIGHUP)      # would raise again without the latch
        time.sleep(0.2)
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(0.2)


class TerminateTreeTests(unittest.TestCase):
    """R8-1: ``_terminate`` ends the child, then proves its descendants gone,
    even one that ignores TERM and holds the child's output pipe."""

    def test_an_orphan_holding_the_pipe_neither_hangs_nor_survives(self):
        code = ("import os, signal, subprocess, sys, time\n"
                "g = subprocess.Popen([sys.executable, '-c', 'import signal, time\\n"
                "signal.signal(signal.SIGTERM, signal.SIG_IGN)\\ntime.sleep(300)\\n'])\n"
                "signal.signal(signal.SIGTERM, lambda *_: os._exit(143))\n"
                "print(g.pid, flush=True)\n"
                "time.sleep(300)\n")
        process = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)
        grandchild = int(process.stdout.readline())
        self.addCleanup(lambda: [os.kill(pid, signal.SIGKILL) for pid in (grandchild, process.pid)
                                 if not gone(pid, 0.01)])
        outcome = {}
        with mock.patch.object(r1, "TREE_STOP_WAIT_S", 1.0):
            worker = threading.Thread(target=lambda: outcome.update(r1._terminate(process, grace_s=1.0)),
                                      daemon=True)
            worker.start()
            worker.join(60)
        self.assertFalse(worker.is_alive(), "_terminate hung on the inherited pipe")
        self.assertTrue(outcome["proven"])
        self.assertIn(str(grandchild), outcome["descendants"])
        self.assertTrue(gone(grandchild))
        self.assertEqual(process.returncode, 143)

    def test_a_pipe_held_by_an_unrecorded_process_is_not_proven(self):
        # The child exited before any census (round-8 Sol critique): its
        # orphan was never recorded but still holds the output pipe.
        code = ("import subprocess, sys\n"
                "g = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(300)'])\n"
                "print(g.pid, flush=True)\n")
        process = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)
        orphan = int(process.stdout.readline())
        self.addCleanup(lambda: gone(orphan, 0.01) or os.kill(orphan, signal.SIGKILL))
        deadline = time.monotonic() + 30
        while process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        with mock.patch.object(r1, "TREE_STOP_WAIT_S", 0.5):
            outcome = r1._terminate(process, grace_s=0.5)
        self.assertFalse(outcome["proven"])
        self.assertTrue(outcome["pipes_held_open"])

    def test_a_child_that_is_never_reaped_is_not_proven(self):
        class Stuck:
            pid, returncode, stdout, stderr = 999999, None, None, None

            def poll(self):
                return None

            def send_signal(self, _number):
                pass

            def kill(self):
                pass

            def communicate(self, timeout=None):
                raise subprocess.TimeoutExpired("stuck", timeout)

            def wait(self, timeout=None):
                raise subprocess.TimeoutExpired("stuck", timeout)
        with mock.patch.object(r1, "_process_table", lambda: {}), \
                mock.patch.object(r1, "REAP_AFTER_KILL_S", 0.1), mock.patch.object(r1, "TREE_STOP_WAIT_S", 0.1):
            outcome = r1._terminate(Stuck(), grace_s=0.2)
        self.assertFalse(outcome["proven"])
        self.assertTrue(outcome["unreaped"])

    def test_identity_is_pid_and_start_time_not_command(self):
        started = "Sat Nov 7 06:00:00 2026"
        tree = {101: (started, "python heater"), 102: (started, "sudo powermetrics")}
        table = {101: (1, started, "/usr/bin/other-program"),        # exec'd: still the same process
                 102: (1, "Sat Nov 7 06:05:00 2026", "sudo powermetrics")}   # pid reused: not ours
        with mock.patch.object(r1, "_process_table", lambda: table):
            self.assertEqual(r1._tree_survivors(tree), {101: tree[101]})


class WatchdogArmTests(unittest.TestCase):
    """R8-3: the teardown watchdog counts from the first held signal."""

    def test_the_watchdog_fires_inside_a_blocked_close(self):
        exits = []
        term = rt.Termination(timeout_s=0.5, exit_now=exits.append, hard_s=5.0).install()
        self.addCleanup(term.restore)
        inside = []

        class Managed:
            def close(self):
                os.kill(os.getpid(), signal.SIGTERM)     # held by the close deferral
                time.sleep(2.0)                           # a close blocked past the watchdog
                inside.append(list(exits))

        with mock.patch.object(rt, "CLOSE_SIGNAL_DEFER_MAX_S", 30.0):
            with self.assertRaises(SystemExit) as stop:
                rt.close_managed_session(Managed())
        self.assertEqual(stop.exception.code, 128 + signal.SIGTERM)
        # Without R8-3 the watchdog armed only when the deferral delivered the
        # signal, after the close: nothing had fired inside it.
        self.assertEqual(inside, [[128 + signal.SIGTERM]])
        self.assertEqual(term.signum, signal.SIGTERM)
        self.assertEqual(term.armed_signum, signal.SIGTERM)

    def test_a_handler_that_is_not_the_runtimes_termination_is_left_alone(self):
        seen = []
        previous = signal.signal(signal.SIGTERM, lambda signum, _frame: seen.append(signum))
        self.addCleanup(signal.signal, signal.SIGTERM, previous)

        class Managed:
            def close(self):
                os.kill(os.getpid(), signal.SIGTERM)
                time.sleep(0.2)
        rt.close_managed_session(Managed())
        self.assertEqual(seen, [signal.SIGTERM])


class RedoReleaseBoundTests(unittest.TestCase):
    """R8-4: a heavy redo's release is its 65 s pre-roll plus the 600 s G0 cap."""

    def test_a_heavy_redo_waits_with_the_release_preroll(self):
        self.assertEqual(r1.release_segment_bound_s(), 65 + 600)
        with tempfile.TemporaryDirectory() as td:
            args = type("Args", (), dict(runtime=["fake-runtime"], volume_watch=None,
                                         segment_bounds={"step-d": 5000.0}))()
            waits, attempts = [], []

            def invoke(_runtime, kind, target, *a, **k):
                if kind == "g0-release-soak":
                    return {"released": True}
                attempts.append(kind)
                Path(target).mkdir(parents=True, exist_ok=True)
                return {}

            def verdict(_name, _result, wall_s=None):
                return {"redo": len(attempts) == 1}
            with mock.patch.object(r1, "wait_outside_os_batch", lambda bound: waits.append(bound) or 0.0), \
                    mock.patch.object(r1, "_invoke", invoke), mock.patch.object(r1, "os_load_verdict", verdict):
                r1._segment(args, Path(td), "step", "step-d", None, "heavy", {"phases": []}, quiet=True)
        self.assertEqual(waits, [5000.0, 5000.0 + 665])


class DryArmInterruptTests(rn.NightDriverTests):
    """R8-5: an interrupt during --dry-arm only exits (round-7 cold probe D)."""

    def test_an_interrupt_in_a_dry_arm_restores_nothing(self):
        mapping = json.loads(self.plan_path.read_text())
        mapping["ac_powermode"] = 2
        self.plan_path.write_text(json.dumps(mapping))
        host = self._power_host(2)
        marker = Path(powermode.host_marker_path())
        powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG,
                                    owner={"custody_root": self.custody, "plan_path": self.plan_path})
        real_write = sys.stderr.write

        def write(text):
            if text.startswith("dry-arm refused: --dry-arm applies"):
                raise KeyboardInterrupt("operator Ctrl-C during the desk dry-arm")
            return real_write(text)
        with mock.patch.object(sys.stderr, "write", write), self.assertRaises(KeyboardInterrupt):
            self.driver.run_night(self.plan_path, dry_arm=True)
        self.assertEqual(host.mode, 2)
        self.assertTrue(marker.exists())
        self.assertNotIn("restore", host.calls)

    def test_an_interrupt_in_the_initial_census_of_a_dry_arm_restores_nothing(self):
        mapping = json.loads(self.plan_path.read_text())
        mapping["ac_powermode"] = 2
        self.plan_path.write_text(json.dumps(mapping))
        host = self._power_host(2)
        marker = Path(powermode.host_marker_path())
        powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG,
                                    owner={"custody_root": self.custody, "plan_path": self.plan_path})

        def census(_probes):
            raise KeyboardInterrupt("signal 15")
        with mock.patch.object(self.driver, "agent_census", census), self.assertRaises(KeyboardInterrupt):
            self.driver.run_night(self.plan_path, dry_arm=True)
        self.assertEqual(host.mode, 2)
        self.assertTrue(marker.exists())
        self.assertNotIn("restore", host.calls)


class AliasedPicksBarTests(unittest.TestCase):
    """R8-6: s_fast and s_slow in one alias group fail R1's thermometry bar."""

    def setUp(self):
        clock = mock.patch.object(r1, "_now_local", lambda: rehearsal_tests.NOON_SAFE)
        clock.start()
        self.addCleanup(clock.stop)

    def run_with_aliases(self, groups):
        with tempfile.TemporaryDirectory() as td:
            world = rehearsal_tests.FakeWorld()

            def runner(argv):
                result = world(argv)
                if "--r1-kind" in argv and argv[argv.index("--r1-kind") + 1] == "step-d":
                    payload = json.loads(result.stdout)
                    payload["thermometry"]["alias_groups"] = groups
                    result = rehearsal_tests.completed(argv, out=json.dumps(payload))
                return result
            args = rehearsal_tests.R1Tests.args(self, td)
            with mock.patch.object(r1, "_run", runner):
                self.assertEqual(r1.run(args), 0)
            return json.loads((Path(td) / "registration/r1_slots.json").read_text())["thermometry"]

    def test_aliased_picks_fail_the_bar_at_r1(self):
        thermometry = self.run_with_aliases([["TC0P", "TG0P", "TZ9Z"]])    # the FakeWorld picks
        self.assertEqual(thermometry["bar"], "fail")
        self.assertIn("r1.picks_aliased", thermometry["flags"])
        self.assertIn("R8-6", thermometry["bar_reason"])

    def test_aliases_elsewhere_keep_the_bar(self):
        thermometry = self.run_with_aliases([["TCMb", "TVD0"], ["TC0P", "TZ9Z"]])
        self.assertEqual(thermometry["bar"], "pass")
        self.assertNotIn("r1.picks_aliased", thermometry["flags"])

    def test_the_rule(self):
        self.assertTrue(r1.picks_aliased({"s_fast": "A", "s_slow": "A", "alias_groups": []}))
        self.assertTrue(r1.picks_aliased({"s_fast": "A", "s_slow": "B", "alias_groups": [["A", "B"]]}))
        self.assertFalse(r1.picks_aliased({"s_fast": "A", "s_slow": "B", "alias_groups": [["A", "C"]]}))
        self.assertFalse(r1.picks_aliased({"s_fast": None, "s_slow": None, "alias_groups": []}))


class DocTests(unittest.TestCase):
    """R8-7: protocol v4 states R7-1, R7-2 and R7-3; R8-1/R8-2 in the contract."""

    def test_protocol_v4_records_round7_rulings(self):
        text = " ".join((ROOT / "docs/align/pilot_protocol_v4.md").read_text().split())
        for needle in ("Gated-block order (LEAD-RULINGS-2 R7-1)", "D_bank, D_spam a, D_spam b, X-G",
                       "R1's G0 timeout (LEAD-RULINGS-2 R7-2)", "G0 timeout of 1,200 s",
                       "`r1_slots.g0_cap_w1.value_s`", "(LEAD-RULINGS-2 R7-3)", "magistrate's call"):
            self.assertIn(needle, text)

    def test_contract_records_r8_1_and_r8_2(self):
        text = " ".join((ROOT / "docs/align/r1_runtime_contract.md").read_text().split())
        for needle in ("lead ruling R8-1", "lead ruling R8-2", "R8-3", "R8-4", "R8-5", "R8-6", "5,763.9952 s",
                       "54,342.97 s", "5,163.9952 s", "56,206.96 s", "D8-1", "D8-2", "D8-3", "D8-4", "D8-5"):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
