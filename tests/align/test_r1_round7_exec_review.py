"""Round-7 executing review of the R1 round-7 changes (2026-11-07).

Adversarial tests written by the reviewer:

* R1 driver: a deferred guard restore (here: a W1 session's marker found
  after the retake) must not be undone by the driver's second, idempotent
  restore attempt in its ``finally`` (that attempt bypassed both checks).
* R7-7: ``admit_ac_powermode`` under a plan of 2 must refuse, with the
  markers kept, when the owed Automatic restore of an R1 marker does not read
  back 0 (it admitted, because the mode then equalled the plan's 2).
* run_night's close frees the retaken host night lock on its ``not_owner``
  return as on every other.
* R7-2/R7-12: the driver's G0_cap_W1 and the kit's re-derivation agree on
  random inputs (censored waits, X-G fallback, rounding boundaries).

Fake sudo/pmset only; nothing real changes the power mode.
"""
import json
import math
import os
from pathlib import Path
import random
import subprocess
import tempfile
import unittest
from unittest import mock

from joulewise.align.apple import powermode
from scripts import align_r1_rehearsal as r1
from scripts import align_v4_kit as kit
from tests import test_run_night as rn
from tests.align import test_r1_rehearsal as rehearsal_tests

BANK, SPAM_A, SPAM_B, XG = ("D_bank_benign_s1_gated_held", "D_spam_benign_s1_gated_held_a",
                            "D_spam_benign_s1_gated_held_b", "X_G_contrast")


def load_tests(loader, tests, pattern):
    """Only this module's own tests (the night case inherits the
    NightDriverTests fixture, not its tests)."""
    suite = unittest.TestSuite()
    for case in (R1FinalRestoreTests, AdmissionReadBackTests, NightCloseLockTests, G0CapAgreementTests):
        suite.addTests(case(name) for name in sorted(vars(case)) if name.startswith("test_"))
    return suite


class _HostState(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.tmp = Path(temporary.name)
        env = mock.patch.dict(os.environ, {powermode.HOST_STATE_ENV: str(self.tmp / "host-power")})
        env.start()
        self.addCleanup(env.stop)
        self.marker = Path(powermode.host_marker_path())


class R1FinalRestoreTests(_HostState):
    def test_the_finally_never_undoes_a_deferred_w1_span(self):
        world = rehearsal_tests.FakeWorld()
        other = str(self.tmp / "w1-session" / "custody")
        installed = {}

        def runner(argv):
            argv = tuple(str(v) for v in argv)
            if "--r1-kind" in argv and argv[argv.index("--r1-kind") + 1] == "harvest" and not installed:
                # A W1 session's own High Power span lands before the close
                # (the case the guard's W1-marker check exists for).
                powermode.write_host_marker(self.marker, tag=powermode.W1_MARKER_TAG,
                                            owner={"custody_root": other})
                world.mode = 2
                installed["calls"] = len(world.calls)
            return world(argv)

        args = rehearsal_tests.R1Tests.args(self, self.tmp)
        with mock.patch.object(r1, "_run", runner), \
                mock.patch.object(r1, "_now_local", lambda: rehearsal_tests.NOON_SAFE):
            r1.run(args)
        self.assertTrue(installed)
        self.assertNotIn(r1.PowerModeGuard.AUTO, world.calls[installed["calls"]:])
        self.assertEqual(world.mode, 2)
        self.assertTrue(powermode.owned_by(self.marker, custody_root=other))
        result = json.loads((args.output / "r1_result.json").read_text())
        self.assertIn("W1 session", result["restore_deferred"])
        free = powermode.HostLock(role="probe")
        self.assertTrue(free.acquire())   # the driver still frees its retaken lock
        free.release()


class AdmissionReadBackTests(_HostState):
    def test_a_plan_two_admission_refuses_when_the_r1_restore_reads_back_two(self):
        powermode.write_host_marker(self.marker, tag=powermode.R1_MARKER_TEXT, owner={"writer": "R1 driver"})
        calls = []

        def stuck(argv):
            # sudo exits 0, but the host still reads AC powermode 2.
            calls.append(tuple(argv))
            return subprocess.CompletedProcess(argv, 0, "AC Power:\n lowpowermode 0\n powermode 2\n", "")

        record = powermode.admit_ac_powermode(2, markers=[self.marker], runner=stuck)
        self.assertIn(tuple(powermode.RESTORE_AUTOMATIC), calls)
        self.assertFalse(record["admitted"])
        self.assertIn("R7-7", record["reason"])
        self.assertEqual(record["observed"], 2)
        self.assertTrue(self.marker.exists())

    def test_a_plan_two_admission_after_a_working_r1_restore_still_refuses_on_the_mode(self):
        powermode.write_host_marker(self.marker, tag=powermode.R1_MARKER_TEXT, owner={"writer": "R1 driver"})
        state = {"mode": 2}

        def host(argv):
            if tuple(argv) == tuple(powermode.RESTORE_AUTOMATIC):
                state["mode"] = 0
            return subprocess.CompletedProcess(argv, 0, f"AC Power:\n powermode {state['mode']}\n", "")

        record = powermode.admit_ac_powermode(2, markers=[self.marker], runner=host)
        self.assertFalse(record["admitted"])
        self.assertEqual(record["reason"], "AC powermode 0 != expected 2")
        self.assertFalse(self.marker.exists())


class NightCloseLockTests(rn.NightDriverTests):
    def test_the_not_owner_close_frees_the_retaken_lock(self):
        mapping = json.loads(self.plan_path.read_text())
        mapping["ac_powermode"] = 2
        self.plan_path.write_text(json.dumps(mapping))
        host = self._power_host(2)
        marker = Path(powermode.host_marker_path())
        powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG,
                                    owner={"custody_root": self.custody, "plan_path": self.plan_path})
        other = self.root / "retry" / "custody"
        real_spawn = self._popen_recorder()[1]

        def spawn(argv, *args, **kwargs):
            powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG, owner={"custody_root": other})
            return real_spawn(argv, *args, **kwargs)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            self.assertEqual(self.driver.run_night(self.plan_path), 0)
        self.assertNotIn("restore", host.calls)
        self.assertEqual(host.mode, 2)
        free = powermode.HostLock(role="probe")
        self.assertTrue(free.acquire(), "run_night kept the retaken host night lock after its not_owner close")
        free.release()


class G0CapAgreementTests(unittest.TestCase):
    """R7-2/R7-12: the driver's record must always equal the kit's re-derivation."""

    OUTCOMES = ("released", "released", "released", "timeout", "deadman", "unobserved")

    def slots(self, rng):
        rows = [{"run": run, "g0_outcome": rng.choice(self.OUTCOMES),
                 "phases_s": {"G0": round(rng.uniform(0.0, 1200.0), rng.choice((0, 1, 3)))}}
                for run in (BANK, SPAM_A, SPAM_B)]
        status = rng.choice(("measured", "measured", "inconclusive"))
        outcome = "released" if status == "measured" else rng.choice(self.OUTCOMES)
        x_g = {"status": status, "g0_outcome": outcome, "g0_wait_s": round(rng.uniform(0.0, 1200.0), 2)}
        return rows, x_g

    def test_driver_and_kit_agree_on_random_records(self):
        rng = random.Random(20261107)
        timeout = kit.r1_g0_timeout_s()
        self.assertEqual(timeout, 1200.0)
        for _ in range(500):
            rows, x_g = self.slots(rng)
            driver = json.loads(json.dumps(r1.w1_g0_cap(rows, x_g, timeout)))
            derived = kit.w1_g0_cap({"deadman_budget": rows, "x_g": x_g})
            for key in ("value_s", "x_g_fallback", "r1_g0_timeout_s", "waits_s", "max_g0_s", "floor_s", "factor"):
                self.assertEqual(driver[key], derived[key], (key, rows, x_g))
            self.assertEqual(sorted(driver["censored"]), sorted(derived["censored"]))
            counted = [w for w in derived["waits_s"].values()]
            expected = min(max(math.ceil(1.25 * max(counted)), 600), 1200)
            self.assertEqual(derived["value_s"], expected)
            for row in rows:
                if row["g0_outcome"] != "released":
                    self.assertEqual(derived["waits_s"][row["run"]], 1200.0)

    def test_rounding_boundaries(self):
        timeout = kit.r1_g0_timeout_s()
        for peak, value in ((480.0, 600), (480.0001, 601), (959.2, 1199), (960.0, 1200), (1199.9, 1200)):
            rows = [{"run": run, "g0_outcome": "released", "phases_s": {"G0": wait}}
                    for run, wait in ((BANK, 10.0), (SPAM_A, peak), (SPAM_B, 0.0))]
            x_g = {"status": "measured", "g0_outcome": "released", "g0_wait_s": 1.0}
            with self.subTest(peak=peak):
                self.assertEqual(r1.w1_g0_cap(rows, x_g, timeout)["value_s"], value)
                self.assertEqual(kit.w1_g0_cap({"deadman_budget": rows, "x_g": x_g})["value_s"], value)


if __name__ == "__main__":
    unittest.main()
