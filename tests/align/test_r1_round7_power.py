"""Lead rulings R7-4, R7-5, R7-7, R7-10 and R7-11 (round 7, 2026-11-07).

* R7-4: run_night and the v4 install end on SIGTERM/SIGHUP through their
  normal close (High Power restore included); real signals.
* R7-5: the host night lock lives as long as the night's process tree (the
  chain and the R1 runtime children inherit it), and a close restores only
  after it has retaken the lock itself; otherwise the marker stays.
* R7-7: the R1 guard reads ``pmset -g custom`` back before it clears a
  marker, and keeps them unless the read-back is AC powermode 0.
* R7-10: the host state directory is fixed in production; the environment
  override is a test seam that production entry points refuse; the night,
  arm and R1 records carry the path.
* R7-11: a host-lock failure other than another holder has its own refusal
  code and runs the restore path; an exception before admission runs it
  too; a failed marker write after a plan-2 admission refuses the night.

Fake sudo/pmset only; nothing real changes the power mode.
"""
import errno
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from joulewise.align.apple import powermode
from scripts import align_r1_rehearsal as r1
from tests import test_run_night as rn
from tests.align import test_r1_rehearsal as rehearsal_tests

ROOT = Path(__file__).resolve().parents[2]
_REAL_POPEN = subprocess.Popen   # the night tests patch subprocess.Popen itself
HOLD_FD = ("import os, sys, time\n"
           "fd = int(sys.argv[1]); os.fstat(fd)\n"
           "print('holding', flush=True)\n"
           "time.sleep(60)\n")


def load_tests(loader, tests, pattern):
    """Only this module's own tests (the night cases inherit the
    NightDriverTests fixture, not its tests)."""
    suite = unittest.TestSuite()
    for case in (LockInheritanceTests, NightLockTreeTests, R1GuardTests, HostStateDirTests,
                 NightSignalTests, HostLockErrorTests):
        names = sorted(name for name in vars(case) if name.startswith("test_"))
        suite.addTests(case(name) for name in names)
    return suite


def spawn_holder(case, fd):
    """A real child that inherited ``fd`` (as the chain or the runtime does)
    and keeps it open until killed."""
    process = _REAL_POPEN([sys.executable, "-B", "-c", HOLD_FD, str(fd)], pass_fds=(fd,),
                          stdout=subprocess.PIPE, text=True)
    case.addCleanup(lambda: (process.poll() is None and process.kill(), process.wait(), process.stdout.close()))
    case.assertEqual(process.stdout.readline().strip(), "holding")
    return process


class HostStateCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.tmp = Path(temporary.name)
        env = mock.patch.dict(os.environ, {powermode.HOST_STATE_ENV: str(self.tmp / "host-power")})
        env.start()
        self.addCleanup(env.stop)
        self.marker = Path(powermode.host_marker_path())

    def holder(self, fd):
        return spawn_holder(self, fd)


class LockInheritanceTests(HostStateCase):
    """R7-5 primitives: release never unlocks an inherited description;
    retake proves no descendant holds it."""

    def test_a_child_that_inherited_the_lock_keeps_it_after_the_parent_releases(self):
        lock = powermode.HostLock(role="night")
        self.assertTrue(lock.acquire())
        child = self.holder(lock.fd)
        lock.release()
        # With LOCK_UN in release the inherited description would be unlocked.
        self.assertFalse(powermode.HostLock(role="session start").acquire())
        child.kill()
        child.wait(timeout=10)
        probe = powermode.HostLock(role="session start")
        self.assertTrue(probe.acquire(wait_s=5, poll_s=0.05))
        probe.release()

    def test_retake_fails_while_a_descendant_holds_the_lock_and_succeeds_after(self):
        lock = powermode.HostLock(role="night")
        self.assertTrue(lock.acquire())
        child = self.holder(lock.fd)
        self.assertFalse(lock.retake())
        self.assertFalse(lock.held)
        child.kill()
        child.wait(timeout=10)
        self.assertTrue(lock.retake())
        self.assertTrue(lock.held)
        lock.release()


class NightLockTreeTests(rn.NightDriverTests):
    """R7-5 in run_night: the chain inherits the lock; the close retakes it."""

    def _plan_two_with_own_marker(self):
        mapping = json.loads(self.plan_path.read_text())
        mapping["ac_powermode"] = 2
        self.plan_path.write_text(json.dumps(mapping))
        host = self._power_host(2)
        marker = Path(powermode.host_marker_path())
        powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG, owner={"custody_root": self.custody})
        return host, marker

    def test_the_chain_inherits_the_host_night_lock_under_plan_two(self):
        host, _marker = self._plan_two_with_own_marker()
        seen = []
        real_acquire = powermode.HostLock.acquire

        def spy(lock, *args, **kwargs):
            taken = real_acquire(lock, *args, **kwargs)
            if lock.role.startswith("night:") and taken:
                seen.append(lock.fd)
            return taken
        with mock.patch.object(powermode.HostLock, "acquire", spy):
            exit_code, calls = self._run_night()
        self.assertEqual((exit_code, calls), (0, [["/bin/zsh", str(self.chain)]]))
        [chain_kwargs] = self.popen_kwargs
        self.assertIn(seen[0], chain_kwargs.get("pass_fds", ()))
        self.assertEqual(host.mode, 0)          # the close retook the lock and restored

    def test_a_plan_zero_chain_inherits_no_lock(self):
        self._power_host(0)
        exit_code, calls = self._run_night()
        self.assertEqual((exit_code, calls), (0, [["/bin/zsh", str(self.chain)]]))
        self.assertEqual(self.popen_kwargs[0].get("pass_fds", ()), ())

    def test_the_close_never_restores_while_a_process_of_the_night_holds_the_lock(self):
        host, marker = self._plan_two_with_own_marker()
        survivors = []
        real_spawn = self._popen_recorder()[1]

        def spawn(argv, *args, **kwargs):
            # A chain descendant that outlives supervision keeps the inherited lock.
            survivors.extend(spawn_holder(self, fd) for fd in kwargs.get("pass_fds", ()))
            return real_spawn(argv, *args, **kwargs)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            exit_code = self.driver.run_night(self.plan_path)
        self.assertEqual(exit_code, 0)
        self.assertEqual(len(survivors), 1)
        self.assertNotIn("restore", host.calls)
        self.assertEqual(host.mode, 2)
        self.assertTrue(marker.exists())
        self.assertIn("ac powermode close deferred", (self.custody / "night.log").read_text())
        # Once that process is gone the backstop restores (here: a session start).
        survivors[0].kill()
        survivors[0].wait(timeout=10)
        record = powermode.restore_owed([marker], runner=lambda argv: host[tuple(argv)], reason="session_start")
        self.assertEqual(record["action"], "restored")
        self.assertEqual(host.mode, 0)

    def test_the_admission_record_and_log_carry_the_host_state_dir(self):
        self._plan_two_with_own_marker()
        exit_code, _calls = self._run_night()
        self.assertEqual(exit_code, 0)
        self.assertIn(f"host state dir {powermode.host_state_dir()}", (self.custody / "night.log").read_text())


class R1GuardTests(HostStateCase):
    """R7-5 and R7-7 in the R1 driver."""

    def test_runtime_children_inherit_the_drivers_lock(self):
        lock = powermode.HostLock(role="R1 driver")
        self.assertTrue(lock.acquire())
        self.addCleanup(lock.release)
        code = ("import os, sys; fd = int(sys.argv[1]); st = os.fstat(fd); "
                "print(st.st_ino == os.stat(sys.argv[2]).st_ino)")
        with mock.patch.object(r1, "_CHILD_HOST_LOCK", lock):
            result = r1._run([sys.executable, "-B", "-c", code, str(lock.fd), powermode.night_lock_path()])
        self.assertEqual((result.returncode, result.stdout.strip()), (0, "True"), result.stderr)

    def guard(self, world):
        local = self.tmp / ".align-r1-high-power"
        lock = powermode.HostLock(role="R1 driver")
        self.assertTrue(lock.acquire())
        self.addCleanup(lock.release)
        guard = r1.PowerModeGuard(world, local, self.marker, lock=lock)
        return guard, local, lock

    def test_a_restore_that_does_not_read_back_zero_keeps_both_markers(self):
        # Round-6 cold pass probe G: sudo exits 0 but the mode still reads 2.
        world = rehearsal_tests.FakeWorld()

        def stuck(argv):
            if tuple(argv) == r1.PowerModeGuard.AUTO:
                world.calls.append(tuple(argv))
                return rehearsal_tests.completed(tuple(argv))
            return world(argv)
        guard, local, _lock = self.guard(stuck)
        guard.__enter__()
        guard.high()
        self.assertEqual(world.mode, 2)
        with self.assertRaisesRegex(r1.Refusal, "restore_failed"):
            guard.__exit__(None, None, None)
        self.assertTrue(local.exists())
        self.assertTrue(self.marker.exists())
        self.assertEqual(guard.records[-1]["point"], "after_restore_automatic")
        self.assertEqual(guard.records[-1]["observed"], 2)

    def test_a_restore_that_reads_back_zero_clears_both_markers(self):
        world = rehearsal_tests.FakeWorld()
        guard, local, _lock = self.guard(world)
        with guard:
            guard.high()
        self.assertEqual(world.mode, 0)
        self.assertFalse(local.exists())
        self.assertFalse(self.marker.exists())

    def test_the_close_defers_while_a_runtime_child_still_holds_the_lock(self):
        world = rehearsal_tests.FakeWorld()
        guard, local, lock = self.guard(world)
        guard.__enter__()
        guard.high()
        child = self.holder(lock.fd)
        self.assertFalse(guard.restore())
        self.assertTrue(guard.deferred)
        self.assertEqual(world.mode, 2)
        self.assertNotIn(r1.PowerModeGuard.AUTO, world.calls[-3:])
        self.assertTrue(local.exists())
        self.assertTrue(self.marker.exists())
        child.kill()
        child.wait(timeout=10)
        # The next session start restores once the child is gone.
        from scripts import align_v4_session as session
        record = session.session_start_restore(self.tmp / "m", runner=world)
        self.assertEqual((record["action"], world.mode), ("restored", 0))

    def test_the_r1_result_records_the_host_state_dir(self):
        world = rehearsal_tests.FakeWorld()
        args = rehearsal_tests.R1Tests.args(self, self.tmp)
        with mock.patch.object(r1, "_run", world), \
                mock.patch.object(r1, "_now_local", lambda: rehearsal_tests.NOON_SAFE):
            self.assertEqual(r1.run(args), 0)
        result = json.loads((args.output / "r1_result.json").read_text())
        self.assertEqual(result["host_state_dir"], powermode.host_state_dir())
        self.assertEqual(result["host_state_dir"], str(self.tmp / "host-power"))


class HostStateDirTests(HostStateCase):
    """R7-10: fixed in production; the override is a test seam production refuses."""

    def tearDown(self):
        powermode._PRODUCTION_ENTRY = None

    def test_the_default_is_the_fixed_shared_path(self):
        with mock.patch.dict(os.environ, {powermode.HOST_STATE_ENV: ""}):
            self.assertEqual(powermode.host_state_dir(), "/Users/Shared/JouleWise/host-power")
        self.assertEqual(Path(powermode.host_state_dir()), self.tmp / "host-power")   # the test seam

    def test_a_production_entry_refuses_the_override_everywhere_it_is_used(self):
        powermode.mark_production_entry("run_night")
        for use in (powermode.host_state_dir, powermode.host_marker_path, powermode.night_lock_path,
                    lambda: powermode.HostLock()):
            with self.assertRaisesRegex(powermode.HostStateOverrideRefused, "test seam only"):
                use()
        with mock.patch.dict(os.environ, {powermode.HOST_STATE_ENV: powermode.HOST_STATE_DEFAULT}):
            self.assertEqual(powermode.host_state_dir(), powermode.HOST_STATE_DEFAULT)

    def test_every_production_entry_point_marks_itself_before_main(self):
        for script, entry in (("scripts/run_night.py", "run_night"),
                              ("scripts/align_v4_session.py", "align_v4_session"),
                              ("scripts/align_r1_rehearsal.py", "align_r1_rehearsal"),
                              ("scripts/magistrate_watchdog.py", "magistrate_watchdog")):
            block = (ROOT / script).read_text().rsplit("__main__", 1)[1]
            self.assertRegex(block, r"mark_production_entry\([\'\"]%s[\'\"]\)[^\n]*\n\s*raise SystemExit\(main\(\)\)"
                             % entry, script)

    def test_the_session_cli_refuses_an_exported_override(self):
        measurement = self.tmp / "m"
        powermode.write_host_marker(Path(powermode.host_marker_path()), tag=powermode.R1_MARKER_TEXT)
        completed = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts/align_v4_session.py"), "prepare",
             "--measurement-root", str(measurement), "--session-root", str(self.tmp / "s")],
            cwd=ROOT, capture_output=True, text=True, timeout=120,
            env=dict(os.environ, PYTHONPATH=str(ROOT)))
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("test seam only", completed.stderr)
        self.assertTrue(Path(powermode.host_marker_path()).exists())   # nothing restored in the wrong place

    def test_the_r1_driver_refuses_an_override_under_its_production_entry(self):
        powermode.mark_production_entry("align_r1_rehearsal")
        output = self.tmp / "r1-out"
        rc = r1.main(["--output", str(output), "--runtime", "fake-runtime"])
        self.assertEqual(rc, 3)
        self.assertFalse(output.exists())


class NightSignalTests(unittest.TestCase):
    """R7-4 with real signals: run_night under a plan of 2 is parked inside
    the chain spawn while it holds the host night lock; TERM or HUP must run
    its close (Automatic restored, marker removed)."""

    CHILD = r'''
import json, os, sys, time, unittest
from pathlib import Path
from unittest import mock
from joulewise.align.apple import powermode
from tests import test_run_night as rn
case = rn.NightDriverTests("test_status_fake_only_cleans_planned_measurement_root")
case.setUp()
mapping = json.loads(case.plan_path.read_text()); mapping["ac_powermode"] = 2
case.plan_path.write_text(json.dumps(mapping))
host = case._power_host(2)
marker = Path(powermode.host_marker_path())
powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG, owner={"custody_root": case.custody})
def parked(argv, *args, **kwargs):
    print(json.dumps({"parked": powermode.host_state_dir()}), flush=True)
    time.sleep(60)
    raise AssertionError("not signalled")
outcome = {}
try:
    with mock.patch.object(case.driver.subprocess, "Popen", parked):
        outcome["exit"] = case.driver.run_night(case.plan_path)
except BaseException as error:
    outcome["raised"] = type(error).__name__ + ": " + str(error)
outcome.update(mode=host.mode, marker=marker.exists(), calls=host.calls,
               log=(case.custody / "night.log").read_text())
print(json.dumps(outcome), flush=True)
'''

    def run_and_signal(self, signum):
        with tempfile.TemporaryDirectory() as tmp:
            child = subprocess.Popen([sys.executable, "-B", "-c", self.CHILD], cwd=ROOT, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True,
                                     env=dict(os.environ, PYTHONPATH=str(ROOT), TMPDIR=tmp))
            try:
                parked = json.loads(child.stdout.readline())
                with mock.patch.dict(os.environ, {powermode.HOST_STATE_ENV: parked["parked"]}):
                    self.assertFalse(powermode.HostLock(role="probe").acquire())   # the night holds it
                child.send_signal(signum)
                out, err = child.communicate(timeout=60)
            finally:
                if child.poll() is None:
                    child.kill()
                    child.communicate()
        self.assertEqual(child.returncode, 0, err)
        return json.loads(out.strip().splitlines()[-1])

    def test_sigterm_runs_the_close(self):
        outcome = self.run_and_signal(signal.SIGTERM)
        self.assertIn("KeyboardInterrupt", outcome.get("raised", ""))
        self.assertEqual((outcome["mode"], outcome["marker"]), (0, False))
        self.assertIn("ac powermode close", outcome["log"])

    def test_sighup_runs_the_close(self):
        outcome = self.run_and_signal(signal.SIGHUP)
        self.assertIn("KeyboardInterrupt", outcome.get("raised", ""))
        self.assertEqual((outcome["mode"], outcome["marker"]), (0, False))


class HostLockErrorTests(rn.NightDriverTests):
    """R7-11: lock errors, exceptions before admission, failed marker writes."""

    def _declare_two(self):
        mapping = json.loads(self.plan_path.read_text())
        mapping["ac_powermode"] = 2
        self.plan_path.write_text(json.dumps(mapping))

    def _own_marker(self):
        marker = Path(powermode.host_marker_path())
        powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG,
                                    owner={"custody_root": self.custody, "plan_path": self.plan_path})
        return marker

    def test_a_lock_file_error_has_its_own_code_and_runs_the_restore_path(self):
        self._declare_two()
        host = self._power_host(2)
        marker = self._own_marker()
        real_acquire = powermode.HostLock.acquire

        def broken_for_the_night(lock, *args, **kwargs):
            if lock.role.startswith("night:"):
                raise OSError(errno.EIO, "Input/output error", powermode.night_lock_path())
            return real_acquire(lock, *args, **kwargs)
        with mock.patch.object(powermode.HostLock, "acquire", broken_for_the_night):
            exit_code, calls = self._run_night()
        self.assertEqual((exit_code, calls), (3, []))
        refusal = json.loads((self.custody / "night/refusal.json").read_text())["refusal"]
        self.assertEqual(refusal["reason"], "night_refused_host_lock_error")
        self.assertIn("Input/output error", refusal["detail"])
        self.assertEqual(refusal["evidence"]["exit_restore"]["action"], "restored")
        self.assertEqual(host.mode, 0)
        self.assertFalse(marker.exists())

    def test_another_holder_is_still_the_powermode_refusal(self):
        self._declare_two()
        self._power_host(2)
        self._own_marker()
        other = powermode.HostLock(role="another measuring night")
        self.assertTrue(other.acquire())
        self.addCleanup(other.release)
        with mock.patch.object(powermode, "NIGHT_LOCK_WAIT_S", 0.0):
            exit_code, _calls = self._run_night()
        self.assertEqual(exit_code, 3)
        refusal = json.loads((self.custody / "night/refusal.json").read_text())["refusal"]
        self.assertEqual(refusal["reason"], "night_refused_ac_powermode")
        self.assertIn("another night holds the host night lock", refusal["detail"])

    def test_an_exception_before_admission_runs_the_restore_path(self):
        self._declare_two()
        host = self._power_host(2)
        marker = self._own_marker()
        with mock.patch.object(self.driver, "_append_census", side_effect=OSError(errno.ENOSPC, "No space")):
            with self.assertRaises(OSError):
                self._run_night()
        self.assertEqual(host.mode, 0)
        self.assertFalse(marker.exists())
        self.assertIn("ac powermode exit restore (exception_before_admission)",
                      (self.custody / "night.log").read_text())

    def test_an_exception_after_the_lock_is_taken_restores_under_it_and_frees_it(self):
        self._declare_two()
        host = self._power_host(2)
        marker = self._own_marker()
        with mock.patch.object(self.driver, "_admit_ac_powermode", side_effect=KeyboardInterrupt("signal 15")):
            with self.assertRaises(KeyboardInterrupt):
                self._run_night()
        self.assertEqual(host.mode, 0)
        self.assertFalse(marker.exists())
        free = powermode.HostLock(role="probe")
        self.assertTrue(free.acquire())
        free.release()

    def test_a_failed_marker_write_after_a_plan_two_admission_refuses_before_measuring(self):
        self._declare_two()
        host = self._power_host(2)
        with mock.patch.object(powermode, "write_host_marker", side_effect=OSError(errno.EROFS, "Read-only")):
            exit_code, calls = self._run_night()
        self.assertEqual((exit_code, calls), (3, []))
        refusal = json.loads((self.custody / "night/refusal.json").read_text())["refusal"]
        self.assertEqual(refusal["reason"], "night_refused_ac_powermode")
        self.assertIn("could not be written", refusal["detail"])
        self.assertEqual(host.mode, 0)          # the close restored Automatic


if __name__ == "__main__":
    unittest.main()
