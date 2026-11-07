"""Round-6 executing review (2026-11-07): adversarial tests of lead ruling R6-7.

R6-7: no exit path may leave the host at AC powermode 2 unrestored, and no
restore may run while a measuring night holds the host night lock.

* The run_night ``dead-man`` mode is the night's last exit when the night job
  never launched (or when ``run_night`` died without its close). It restores
  the High Power marker its own plan's session owns, after it has proved the
  chain is gone, and never under a measuring night or for another plan.
* The night lock is a real cross-process flock: an R1 driver parked in its
  High Power leg defers every session-start restore, and a SIGKILL of that
  driver releases the lock so the next session start restores.

Fake sudo/pmset only; nothing real runs.
"""
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
from tests import test_run_night as rn

ROOT = Path(__file__).resolve().parents[2]


def load_tests(loader, tests, pattern):
    """Only this module's own tests (DeadManHighPowerTests inherits the
    NightDriverTests fixture, not its tests)."""
    suite = unittest.TestSuite()
    for case in (DeadManHighPowerTests, NightLockAcrossProcessesTests, PhaseOrderTests):
        names = sorted(name for name in vars(case) if name.startswith("test_"))
        suite.addTests(case(name) for name in names)
    return suite


class DeadManHighPowerTests(rn.NightDriverTests):
    """The dead-man exit (never launched, or run_night killed without its close)."""

    def _armed_w1_session(self, *, owner_custody=None):
        mapping = json.loads(self.plan_path.read_text())
        mapping["ac_powermode"] = 2
        self.plan_path.write_text(json.dumps(mapping))
        host = self._power_host(2)
        marker = Path(powermode.host_marker_path())
        powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG,
                                    owner={"custody_root": owner_custody or self.custody,
                                           "plan_path": None if owner_custody else self.plan_path})
        night = self.custody / "night"
        night.mkdir(exist_ok=True)
        return host, marker

    def _dead_man_at_completion(self):
        plan = self.driver._load_plan(self.plan_path)
        with mock.patch.object(self.driver.time, "time",
                               return_value=plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S):
            return self.driver.dead_man(self.plan_path)

    def test_a_never_launched_w1_night_is_restored_by_its_dead_man(self):
        # The J4 release is the first restore; if the watchdog never ran (or
        # its restore failed), the dead-man is the night's last exit.
        host, marker = self._armed_w1_session()
        self.assertEqual(self._dead_man_at_completion(), self.driver.EXIT_GO)
        self.assertEqual(host.mode, 0)
        self.assertFalse(marker.exists())
        self.assertIn("ac powermode exit restore (dead_man)", (self.custody / "night.log").read_text())
        self.driver.run_courier.assert_called_once()

    def test_the_dead_man_after_a_killed_run_night_restores_once_the_chain_is_gone(self):
        # run_night has no SIGTERM handler: a TERM (or KILL) skips its close.
        host, marker = self._armed_w1_session()
        (self.custody / "night/chain.started").write_text(json.dumps({"pid": 999999, "pgid": 999999,
                                                                       "epoch_s": time.time()}))
        with mock.patch.object(self.driver.os, "killpg", side_effect=ProcessLookupError):
            self.assertEqual(self._dead_man_at_completion(), self.driver.EXIT_GO)
        self.assertEqual(host.mode, 0)
        self.assertFalse(marker.exists())

    def test_the_dead_man_never_restores_while_the_chain_is_alive(self):
        host, marker = self._armed_w1_session()
        (self.custody / "night/chain.started").write_text(json.dumps({"pid": os.getpid(), "pgid": os.getpgid(0),
                                                                       "epoch_s": time.time()}))
        self.assertEqual(self._dead_man_at_completion(), self.driver.EXIT_REFUSED)
        self.assertNotIn("restore", host.calls)
        self.assertEqual(host.mode, 2)
        self.assertTrue(marker.exists())

    def test_the_dead_man_never_restores_under_a_measuring_night(self):
        host, marker = self._armed_w1_session()
        other = powermode.HostLock(role="a measuring night")
        self.assertTrue(other.acquire())
        self.addCleanup(other.release)
        self.assertEqual(self._dead_man_at_completion(), self.driver.EXIT_GO)
        self.assertNotIn("restore", host.calls)
        self.assertEqual(host.mode, 2)
        self.assertTrue(marker.exists())

    def test_the_dead_man_leaves_another_sessions_marker_alone(self):
        host, marker = self._armed_w1_session(owner_custody=self.root / "a-retried-session" / "custody")
        self.assertEqual(self._dead_man_at_completion(), self.driver.EXIT_GO)
        self.assertNotIn("restore", host.calls)
        self.assertEqual(host.mode, 2)
        self.assertTrue(marker.exists())


class NightLockAcrossProcessesTests(unittest.TestCase):
    """A real second process holds the lock and its High Power marker, as an
    R1 driver in a High Power leg does; real signals end it."""

    HOLDER = (
        "import sys, time\n"
        "from joulewise.align.apple import powermode\n"
        "lock = powermode.HostLock(role='R1 driver')\n"
        "assert lock.acquire()\n"
        "powermode.write_host_marker(powermode.host_marker_path(), tag=powermode.R1_MARKER_TEXT,\n"
        "                            owner={'writer': 'R1 driver'})\n"
        "print('held', flush=True)\n"
        "try:\n"
        "    time.sleep(60)\n"
        "except KeyboardInterrupt:\n"
        "    import os; os.unlink(powermode.host_marker_path()); lock.release(); print('restored', flush=True)\n"
    )

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.state = Path(temporary.name) / "host-power"
        env = mock.patch.dict(os.environ, {powermode.HOST_STATE_ENV: str(self.state)})
        env.start()
        self.addCleanup(env.stop)
        self.calls, self.mode = [], 2

    def runner(self, argv):
        self.calls.append(tuple(argv))
        if tuple(argv) == powermode.RESTORE_AUTOMATIC:
            self.mode = 0
        return subprocess.CompletedProcess(argv, 0, f"AC Power:\n powermode {self.mode}\n", "")

    def holder(self):
        process = subprocess.Popen([sys.executable, "-B", "-c", self.HOLDER], cwd=ROOT, stdout=subprocess.PIPE,
                                   text=True, env=dict(os.environ, PYTHONPATH=str(ROOT)))
        self.addCleanup(lambda: (process.poll() is None and process.kill(), process.wait(), process.stdout.close()))
        self.assertEqual(process.stdout.readline().strip(), "held")
        return process

    def test_session_start_defers_under_a_live_holder_and_restores_after_its_sigkill(self):
        from scripts import align_v4_session as session
        holder = self.holder()
        measurement = Path(self.state).parent / "m"
        for _ in range(3):
            record = session.session_start_restore(measurement, runner=self.runner)
            self.assertEqual(record["action"], "deferred_measuring_night")
        self.assertEqual(self.calls, [])
        holder.send_signal(signal.SIGKILL)
        holder.wait(timeout=10)
        self.assertTrue(Path(powermode.host_marker_path()).exists())
        record = session.session_start_restore(measurement, runner=self.runner)
        self.assertEqual(record["action"], "restored")
        self.assertIn(powermode.RESTORE_AUTOMATIC, self.calls)
        self.assertFalse(Path(powermode.host_marker_path()).exists())

    def test_admission_refuses_under_a_live_holder_then_admits_after_its_own_teardown(self):
        holder = self.holder()
        marker = powermode.host_marker_path()
        refused = powermode.admit_ac_powermode(0, markers=[marker], runner=self.runner)
        self.assertFalse(refused["admitted"])
        self.assertNotIn(powermode.RESTORE_AUTOMATIC, self.calls)
        holder.send_signal(signal.SIGINT)
        self.assertEqual(holder.stdout.readline().strip(), "restored")
        holder.wait(timeout=10)
        self.calls.clear()
        # The holder's own teardown cleared the marker; nothing is owed.
        record = powermode.restore_owed([marker], runner=self.runner, reason="session_start")
        self.assertEqual((record["action"], self.calls), ("none", []))

    def test_an_exit_restore_rechecks_the_owner_under_the_lock(self):
        # Sol F9: a late exit of plan P1 passes the owner check, then a retry
        # session installs (under the lock), replaces the marker with its own
        # and leaves the host at 2 before P1's exit takes the free lock.
        marker = Path(powermode.host_marker_path())
        mine, retry = Path(self.state).parent / "p1/custody", Path(self.state).parent / "retry/custody"
        powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG, owner={"custody_root": mine})
        real_acquire = powermode.HostLock.acquire

        def install_in_between(lock, *args, **kwargs):
            powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG, owner={"custody_root": retry})
            return real_acquire(lock, *args, **kwargs)

        with mock.patch.object(powermode.HostLock, "acquire", install_in_between):
            record = powermode.restore_owed([marker], runner=self.runner, owner={"custody_root": mine},
                                            reason="launch_abandoned")
        self.assertEqual(record["action"], "not_owner")
        self.assertEqual((self.calls, self.mode), ([], 2))
        self.assertTrue(powermode.owned_by(marker, custody_root=retry))


class PhaseOrderTests(unittest.TestCase):
    """R6-1 / R6-2 on the phase table the driver runs (any cap, with or without 4-bit)."""

    def test_gated_runs_follow_a_d_turn_and_calibrations_follow_a_bounded_precool(self):
        from joulewise.align.apple import r1_runtime_contract as contract
        from scripts import align_r1_rehearsal as r1
        for include_4bit in (False, True):
            for cap in (900.0, 1500.0):
                phases = r1.phase_plan(include_4bit, precool_cap_s=cap)
                kinds = [kind for _name, kind, _duration, _class in phases]
                for index, (name, kind, _duration, _class) in enumerate(phases):
                    if name in r1.GATED_NAMES or kind == "x-g":
                        # R6-1: only W1's own idle (inside the member) after a D
                        # turn; no idle segment, no cool-to-band in between.
                        self.assertIn(kinds[index - 1], r1.D_TURN_KINDS, (name, kinds[index - 1]))
                    if kind in contract.G0_INCONCLUSIVE_KINDS:
                        # R6-2: a bounded precool to the G0 band of R right before.
                        before = phases[index - 1]
                        self.assertEqual(before[1], "idle-until-soak", name)
                        self.assertIn(before[2], (cap, r1.COOLDOWN_AFTER_D_MAX_S), name)
                self.assertNotIn("cooldown_after_30b", [name for name, *_ in phases])   # R6-6
                gated = [i for i, (n, k, *_) in enumerate(phases) if n in r1.GATED_NAMES or k == "x-g"]
                self.assertEqual(gated, list(range(gated[0], gated[0] + 4)))
                self.assertEqual(phases[gated[0] - 1][0], "planning_turn_R_plus_0C")
                # LEAD-RULINGS-2 R7-1: D_bank, D_spam a, D_spam b, X-G.
                self.assertEqual([phases[i][0] for i in gated],
                                 ["D_bank_benign_s1_gated_held", "D_spam_benign_s1_gated_held_a",
                                  "D_spam_benign_s1_gated_held_b", "X_G_contrast"])


if __name__ == "__main__":
    unittest.main()
