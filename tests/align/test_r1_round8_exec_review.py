"""Executing review of the R1 round-8 changes (2026-11-07), adversarial tests.

Written by the reviewer, not the builder, against `a13d6fc99`. Real signals,
real chains and real runtimes; fake sudo/pmset only (nothing real changes the
power mode). See docs/align/reviews/2026-11-07-r1-round8-executing-review.md.

* A second (and third) signal while run_night is terminating the chain does
  not cut the termination or the close short.
* A process of the night that escaped the chain's group but holds the host
  night lock never sees a restore (the group proof passes, the retake fails).
* A second and third signal while the R1 driver is ending a runtime that
  ignores TERM does not cut the KILL, the tree proof or the restore short.
* Two findings were pinned as expected failures and are fixed by the round-8
  dispositions (LEAD-RULINGS-2): MEDIUM-1 (a signal swallowed by
  ``_qualification_observe`` latched the shutdown, so later signals were lost
  too; D8-1) and MEDIUM-2 (a non-interrupt chain termination that was not
  proven still restored when the lock could be retaken; D8-2).
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
from scripts import align_r1_rehearsal as r1
from tests import test_run_night as rn
from tests.align import test_r1_rehearsal as rehearsal_tests
from tests.align.test_r1_round8 import CHAIN, NIGHT_CHILD, gone

ROOT = Path(__file__).resolve().parents[2]


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for case in (NightRepeatedSignalTests, NightLockHoldingEscapeeTests, R1RepeatedSignalTests,
                 SwallowedSignalLatchTests, NightUnprovenNonInterruptCloseTests):
        names = sorted(name for name in vars(case) if name.startswith("test_"))
        suite.addTests(case(name) for name in names)
    return suite


# A chain whose member leaves the chain's process group (its own session) and
# keeps every inheritable descriptor, the host night lock included.
ESCAPEE_CHAIN = r'''
import json, os, subprocess, sys, time
ready = sys.argv[1]
member = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"],
                          start_new_session=True, close_fds=False)
with open(ready + ".tmp", "w") as handle:
    json.dump({"chain": os.getpid(), "member": member.pid}, handle)
os.replace(ready + ".tmp", ready)
time.sleep(300)
'''


def night_with_signals(chain_code, stubborn, signals):
    """Run NIGHT_CHILD with ``chain_code``; once the chain is up, send each
    ``(delay_s, signum)`` in turn. Returns (outcome, pids, returncode, stderr)."""
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
        ready = Path(tmp) / "chain.ready"
        child = subprocess.Popen(
            [sys.executable, "-B", "-c", NIGHT_CHILD, str(ready), "stubborn" if stubborn else "plain", chain_code],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            env=dict(os.environ, PYTHONPATH=str(ROOT), TMPDIR=tmp))
        pids = None
        try:
            deadline = time.monotonic() + 120
            while not ready.exists() and child.poll() is None and time.monotonic() < deadline:
                time.sleep(0.05)
            if not ready.exists():
                raise AssertionError(child.stderr.read() if child.poll() is not None else "no chain")
            pids = json.loads(ready.read_text())
            time.sleep(0.5)
            for delay_s, signum in signals:
                time.sleep(delay_s)
                if child.poll() is None:
                    child.send_signal(signum)
            out, err = child.communicate(timeout=240)
        finally:
            if child.poll() is None:
                child.kill()
                child.communicate()
            for pid in (pids or {}).values():
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
    return json.loads(out.strip().splitlines()[-1]), pids, child.returncode, err


class NightRepeatedSignalTests(unittest.TestCase):
    """R8-1: once the first signal has landed, no later TERM/HUP/INT can cut
    the chain termination or the close short."""

    def test_signals_during_the_termination_do_not_cut_it_short(self):
        # A chain that ignores TERM keeps run_night in the termination (TERM,
        # wait, re-signalled census, KILL) for several seconds; every further
        # signal lands inside it.
        signals = [(0.0, signal.SIGTERM)] + [(0.4, s) for s in
                                             (signal.SIGHUP, signal.SIGINT, signal.SIGTERM) * 3]
        outcome, pids, returncode, err = night_with_signals(CHAIN, True, signals)
        self.assertEqual(returncode, 0, err)
        self.assertEqual(outcome.get("raised"), "KeyboardInterrupt: signal 15")   # the first one only
        log = outcome["log"]
        self.assertEqual(log.count("chain terminated on interrupt (lead ruling R8-1)"), 1)
        self.assertIn('"proven": true', log)
        self.assertTrue(outcome["exited"])
        self.assertFalse(outcome["unkilled"])
        self.assertNotIn("ac powermode close deferred", log)
        self.assertIn("ac powermode close: restore Automatic", log)
        self.assertEqual((outcome["mode"], outcome["marker"]), (0, False))
        self.assertEqual(outcome["alive_after"], {"chain": False, "member": False})


class NightLockHoldingEscapeeTests(unittest.TestCase):
    """R7-5 + R8-1: the group proof covers only the chain's group; a process
    of the night that left the group but holds the lock is still protected,
    because the close must retake the lock before it restores."""

    def test_an_escapee_that_holds_the_lock_sees_no_restore(self):
        outcome, pids, returncode, err = night_with_signals(ESCAPEE_CHAIN, False, [(0.0, signal.SIGTERM)])
        self.assertEqual(returncode, 0, err)
        log = outcome["log"]
        self.assertIn("KeyboardInterrupt", outcome.get("raised", ""))
        self.assertIn("chain terminated on interrupt (lead ruling R8-1)", log)
        self.assertEqual(outcome["alive_after"], {"chain": False, "member": True})
        # The escapee lived on with the lock: nothing was restored under it.
        self.assertIn("ac powermode close deferred", log)
        self.assertIn("could not be retaken", log)
        self.assertNotIn("restore", outcome["calls"])        # neither at admission nor at the close
        self.assertEqual((outcome["mode"], outcome["marker"]), (2, True))


# A runtime that ignores TERM (so the driver must KILL it after its grace)
# and whose heater ignores TERM and inherits the runtime's output pipes.
STUBBORN_RUNTIME = (
    "import os, signal, subprocess, sys, time\n"
    "out = sys.argv[sys.argv.index('--output') + 1]\n"
    "os.makedirs(out)\n"
    "heater = subprocess.Popen([sys.executable, '-c', 'import signal, time\\n"
    "signal.signal(signal.SIGTERM, signal.SIG_IGN)\\ntime.sleep(300)\\n'])\n"
    "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
    "open(os.path.join(out, 'pids.tmp'), 'w').write(f'{os.getpid()} {heater.pid}')\n"
    "os.replace(os.path.join(out, 'pids.tmp'), os.path.join(out, 'pids'))\n"
    "time.sleep(300)\n")


class R1RepeatedSignalTests(unittest.TestCase):
    """R8-1 in the R1 driver: further INT/HUP/TERM during the grace, the KILL
    and the tree proof are ignored; the restore runs once nothing is left."""

    def setUp(self):
        for name, value in (("_now_local", lambda: rehearsal_tests.NOON_SAFE), ("TREE_STOP_WAIT_S", 1.0),
                            ("RUNTIME_TERM_GRACE_S", 2.0)):
            patcher = mock.patch.object(r1, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(r1._CHILD_TERMINATIONS.clear)

    def test_signals_during_the_runtime_kill_do_not_cut_the_close_short(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
            td = Path(td)
            script = td / "runtime.py"
            script.write_text(STUBBORN_RUNTIME)
            world = rehearsal_tests.FakeWorld(t_decline={"a1": 20.0, "b": 30.0, "a2": 21.0})
            real_run = r1._run
            segment = td / "run" / "X_G_contrast"
            at_restore = []

            def runner(argv):
                if "--r1-kind" in argv and "x-g" in argv:
                    return real_run([sys.executable, str(script), *argv[1:]])
                if tuple(argv) == r1.PowerModeGuard.AUTO and (segment / "pids").exists():
                    pids = list(map(int, (segment / "pids").read_text().split()))
                    at_restore.append(tuple("alive" if not gone(pid, 0.01) else "gone" for pid in pids))
                return world(argv)

            done = threading.Event()

            def signal_storm():
                deadline = time.monotonic() + 60
                while not (segment / "pids").exists() and time.monotonic() < deadline and not done.is_set():
                    time.sleep(0.05)
                if not (segment / "pids").exists() or done.wait(0.2):
                    return
                os.kill(os.getpid(), signal.SIGTERM)
                for signum in (signal.SIGINT, signal.SIGHUP, signal.SIGTERM) * 3:
                    if done.wait(0.4):
                        return
                    os.kill(os.getpid(), signum)

            args = rehearsal_tests.R1Tests.args(self, td, include_4bit=False)
            thread = threading.Thread(target=signal_storm, daemon=True)
            try:
                with mock.patch.object(r1, "_run", runner):
                    thread.start()
                    rc = r1.run(args)
            finally:
                done.set()
                thread.join()
                if (segment / "pids").exists():
                    for pid in map(int, (segment / "pids").read_text().split()):
                        try:
                            os.kill(pid, signal.SIGKILL)
                        except OSError:
                            pass
            runtime_pid, heater_pid = map(int, (segment / "pids").read_text().split())
            result = json.loads((td / "run/r1_result.json").read_text())
        self.assertEqual(rc, 4)
        [termination] = result["child_terminations"]
        self.assertTrue(termination["proven"], termination)
        self.assertEqual(termination["pid"], runtime_pid)
        self.assertEqual(termination["returncode"], -signal.SIGKILL)     # the grace ran out: KILLed
        self.assertIn(str(heater_pid), termination["descendants"])
        self.assertEqual(termination["survivors"], {})
        self.assertNotIn("pipes_held_open", termination)
        self.assertTrue(at_restore)
        self.assertEqual(set(at_restore), {("gone", "gone")})              # nothing of the run at the restore
        self.assertEqual(world.mode, 0)
        self.assertNotIn("restore_deferred", result)
        self.assertFalse(Path(powermode.host_marker_path()).exists())


class SwallowedSignalLatchTests(unittest.TestCase):
    """MEDIUM-1 (fixed by round-8 disposition D8-1): the round-8 latch sets
    ``closing`` before the KeyboardInterrupt is raised. ``_qualification_observe``
    (the s1 HID observation inside the chain loop) caught BaseException, so a
    first signal landing there was swallowed and every later TERM/HUP/INT was
    then swallowed by the latch: the night could no longer be interrupted.
    D8-1: the observation records its fault and re-raises KeyboardInterrupt
    and SystemExit, so the first signal reaches run_night's R8-1 handling.
    (The original body called the observation outside ``assertRaises``,
    expecting the swallow; with the fix the first signal itself escapes, and
    the latch rightly swallows any later one.)"""

    def test_a_signal_after_a_swallowed_one_still_interrupts(self):
        from scripts import run_night
        _closing, restore = run_night._install_termination_handlers()
        self.addCleanup(restore)
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            def observation():
                os.kill(os.getpid(), signal.SIGTERM)
                time.sleep(1)
            with self.assertRaises(KeyboardInterrupt):
                run_night._qualification_observe(Path(tmp), "hid", observation)    # no longer swallowed
            faults = [json.loads(line) for line in (Path(tmp) / "producer-faults.jsonl").read_text().splitlines()]
            self.assertEqual([(f["producer"], f["status"]) for f in faults], [("hid", "REFUSED")])  # still recorded

    def test_system_exit_is_not_an_observation_failure(self):
        from scripts import run_night
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            def observation():
                raise SystemExit(3)
            with self.assertRaises(SystemExit):
                run_night._qualification_observe(Path(tmp), "hid", observation)
            self.assertIsNone(run_night._qualification_observe(Path(tmp), "hid", lambda: 1 / 0))


class NightUnprovenNonInterruptCloseTests(rn.NightDriverTests):
    """MEDIUM-2 (fixed by round-8 disposition D8-2): the round-8 Sol fix
    deferred the close only when an interrupt's chain termination was
    unproven; a census-abort (or window deadline, or supervision stop)
    termination that was unproven still restored whenever the lock could be
    retaken, i.e. under exactly the survivor the fix names (one that does not
    hold the lock). D8-2: _run_night sets _CHAIN_TERMINATION_UNPROVEN on every
    unproven path and the close defers."""

    def test_an_unproven_census_abort_restores_nothing(self):
        mapping = json.loads(self.plan_path.read_text())
        mapping["ac_powermode"] = 2
        self.plan_path.write_text(json.dumps(mapping))
        host = self._power_host(2)
        marker = Path(powermode.host_marker_path())
        powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG, owner={"custody_root": self.custody})
        self.source.census_responses = [
            rn._probe(rn.night_gate.AGENT_CENSUS_ARGV, exit_code=1),
            rn._probe(rn.night_gate.AGENT_CENSUS_ARGV, exit_code=1),
            rn._probe(rn.night_gate.AGENT_CENSUS_ARGV, stdout="agent\n"),
        ]
        spawn = lambda argv, *a, **k: rn.UnkillableProcess(argv)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), \
                mock.patch.object(self.driver.time, "sleep"), \
                mock.patch.object(self.driver, "_terminate_process_group", return_value=False):
            self.driver.run_night(self.plan_path)
        self.assertTrue((self.custody / "night/chain.unkilled").exists())
        self.assertNotIn("restore", host.calls)
        self.assertEqual(host.mode, 2)
        self.assertTrue(marker.exists())                    # left for the dead-man / next session start
        log = (self.custody / "night.log").read_text()
        self.assertIn("not proven gone after the chain stop", log)
        probe = powermode.HostLock(role="probe")            # the close freed the lock
        self.assertTrue(probe.acquire())
        probe.release()
        self.assertIsNone(self.driver._CHAIN_TERMINATION_UNPROVEN)

    def test_an_exception_escaping_the_chain_wait_restores_nothing(self):
        # D8-2, "any path": a non-interrupt exception out of the chain wait
        # never terminated the chain, so its termination is unproven.
        mapping = json.loads(self.plan_path.read_text())
        mapping["ac_powermode"] = 2
        self.plan_path.write_text(json.dumps(mapping))
        host = self._power_host(2)
        marker = Path(powermode.host_marker_path())
        powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG, owner={"custody_root": self.custody})
        with mock.patch.object(self.driver, "_run_chain_once", side_effect=RuntimeError("chain wait broke")), \
                self.assertRaises(RuntimeError):
            self.driver.run_night(self.plan_path)
        self.assertNotIn("restore", host.calls)
        self.assertEqual(host.mode, 2)
        self.assertTrue(marker.exists())
        log = (self.custody / "night.log").read_text()
        self.assertIn("exception escaping the chain wait (RuntimeError: chain wait broke)", log)
        self.assertIsNone(self.driver._CHAIN_TERMINATION_UNPROVEN)


if __name__ == "__main__":
    unittest.main()
