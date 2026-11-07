"""Adversarial checks from the executing review of R1 round 5 (d1639a0b3).

Each test probes a LEAD-RULINGS-2 ruling from a direction its own tests did
not: R5-1 (an INCONCLUSIVE gated run never masks a failing judged run), R5-4
(no non-evidence budget reaches a gated D run or the ruling 1(f) assertion),
and R5-5/R5-6 (a real signal while R1 holds the adopted High Power series mode
leaves the host Automatic, the marker gone and r1_result.json written).
Synthetic only: no model, sensor, sudo or host setting is touched.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime as rt
from scripts import align_r1_rehearsal as r1
from scripts import align_v4_kit as kit
from tests.align import test_r1_rehearsal as base

FakeWorld, NOON_SAFE, completed = base.FakeWorld, base.NOON_SAFE, base.completed

ROOT = Path(__file__).resolve().parents[2]
ADOPT = {"a1": 20.0, "b": 30.0, "a2": 21.0}


def _run_world(td, world, expected=0):
    args = base.R1Tests.args(None, td)
    with patch.object(r1, "_now_local", lambda: NOON_SAFE), patch.object(r1, "_run", world):
        code = r1.run(args)
    result = json.loads((Path(td) / "run/r1_result.json").read_text())
    path = Path(td) / "registration/r1_slots.json"
    return code, result, (json.loads(path.read_text()) if path.exists() else None)


class DutyBarTests(unittest.TestCase):
    def test_an_inconclusive_run_never_masks_a_failing_judged_run(self):
        # R5-1 (R6-1 since round 6): run a's G0 times out (INCONCLUSIVE, and run
        # b then follows no D turn); the bank run is cut by the deadman (X7).
        # The bar must read FAIL, not INCONCLUSIVE.
        world = FakeWorld(g0_timeout={"D_spam_benign_s1_gated_held_a"})

        def runner(argv):
            out = world(argv)
            if "--r1-kind" in argv and "d-bank-benign-s1" in argv:
                payload = json.loads(out.stdout)
                payload["x7"] = True
                out = completed(argv, out=json.dumps(payload))
            return out
        with tempfile.TemporaryDirectory() as td:
            code, result, registration = _run_world(td, runner)
            self.assertEqual(code, 0, result.get("error"))
            rows = {row["run"]: row["duty_bar"]["verdict"] for row in registration["deadman_budget"]}
            self.assertEqual(rows, {"D_spam_benign_s1_gated_held_a": "inconclusive",
                                    "D_spam_benign_s1_gated_held_b": "inconclusive",
                                    "D_bank_benign_s1_gated_held": "fail"})
            self.assertEqual(registration["duty_bar"]["verdict"], "fail")
            self.assertIs(registration["duty_bar"]["pass"], False)
            self.assertEqual(registration["duty_bar"]["inconclusive_runs"],
                             ["D_spam_benign_s1_gated_held_a", "D_spam_benign_s1_gated_held_b"])

    def test_a_bank_run_g0_timeout_leaves_u5_to_the_replay_pair(self):
        # R5-1 scope (R6-1 since round 6): only a replay-pair run makes U5
        # INCONCLUSIVE; the bank run's G0 timeout makes the duty bar
        # INCONCLUSIVE and nothing else.
        world = FakeWorld(g0_timeout={"D_bank_benign_s1_gated_held"})
        with tempfile.TemporaryDirectory() as td:
            code, result, registration = _run_world(td, world)
            self.assertEqual(code, 0, result.get("error"))
            self.assertEqual(registration["duty_bar"]["verdict"], "inconclusive")
            self.assertTrue(registration["u5"]["sigma_pair_valid"])
            self.assertNotEqual(registration["u5"]["verdict"], "inconclusive")


class BudgetTests(unittest.TestCase):
    NON_EVIDENCE_B_D = (0, 1023, 1025, 4096 + 512, 40960 + 1024, 8192.0, True, "8192", None, math.nan)

    def test_no_non_evidence_b_d_reaches_a_gated_run(self):
        # R5-4: the runtime (before model work) and the driver (right after
        # step-d) both refuse; a float equal to an admissible budget is not one.
        for b_d in self.NON_EVIDENCE_B_D:
            with self.subTest(b_d=b_d):
                with self.assertRaises(rt.Refused):
                    rt.gated_budget({"T_dead": 1200.0, "B_D": b_d})
                world = FakeWorld(b_d=b_d)
                with tempfile.TemporaryDirectory() as td:
                    code, result, registration = _run_world(td, world, expected=3)
                    self.assertEqual(code, 3)
                    self.assertIsNone(registration)
                    kinds = [kind for kind, _, _ in world.invocations]
                    self.assertFalse([k for k in kinds if k.startswith(("d-spam", "d-bank"))], kinds)
        for t_dead in (math.nan, math.inf, -1.0, 0.0, True, "1200", None):
            with self.subTest(t_dead=t_dead), self.assertRaises(rt.Refused):
                rt.gated_budget({"T_dead": t_dead, "B_D": 8192})
        self.assertEqual(rt.gated_budget({"T_dead": 1200, "B_D": 1024}), (1200.0, 1024))

    def _slots(self, rows, rate=11.0, cap=None):
        names = kit.GATED_D_RUN_NAMES
        base = {k: 0.0 for k in kit.GATED_PHASES}
        return {"deadman_budget": [{"run": n, "phases_s": {**base, **row}, "decode_tokens": 0}
                                   for n, row in zip(names, rows)],
                "budget_fit_inputs": {"r_decode_tok_per_s": rate, "r_decode_step_d_tok_per_s": rate,
                                      "turn_cap_tokens": kit.d_turn_cap_tokens() if cap is None else cap},
                "slots": {"B_D": 40960}}

    def test_ruling_1f_takes_each_term_at_its_worst_run(self):
        # The worst case combines the worst G0, the worst holds and the worst
        # prefill + tool even when no single run had all three.
        rows = ({"G0": 300.0, "prefill": 10.0}, {"G1": 200.0, "H": 100.0, "prefill": 10.0},
                {"prefill": 150.0, "tool": 20.0})
        slots = self._slots(rows)
        cap = kit.d_turn_cap_tokens()
        fit = kit.ruling_1f_fit(slots, 6144, 2000.0)
        self.assertEqual(fit["terms_s"], {"G0_s": 300.0, "holds_s": 300.0, "prefill_tool_s": 170.0,
                                          "decode_s": (6144 + cap) / 11.0})
        self.assertAlmostEqual(fit["worst_s"], 770.0 + (6144 + cap) / 11.0)
        self.assertFalse(kit.ruling_1f_fit(slots, 6144, fit["worst_s"] - 1.0)["fits"])
        self.assertTrue(kit.ruling_1f_fit(slots, 6144, fit["worst_s"])["fits"])
        # The sizing aid never names a budget that itself misses T_dead.
        best = kit.max_fitting_b_d(slots, 1600.0)
        if best is not None:
            self.assertTrue(kit.ruling_1f_fit(slots, best, 1600.0)["fits"])
            self.assertFalse(best + 1024 <= 40960 and kit.ruling_1f_fit(slots, best + 1024, 1600.0)["fits"])

    def test_ruling_1f_refuses_non_evidence(self):
        good = ({"G0": 100.0}, {"G0": 100.0}, {"G0": 100.0})
        for label, slots in (
                ("bool phase", self._slots(({"G0": True}, *good[1:]))),
                ("nan phase", self._slots(({"G1": math.nan}, *good[1:]))),
                ("negative phase", self._slots(({"H": -1.0}, *good[1:]))),
                ("zero rate", self._slots(good, rate=0.0)),
                ("bool rate", self._slots(good, rate=True)),
                ("wrong cap", self._slots(good, cap=2048)),
                ("bool cap", self._slots(good, cap=True))):
            with self.subTest(label), self.assertRaises(ValueError):
                kit.ruling_1f_fit(slots, 6144, 5000.0)
        duplicate = self._slots(good)
        duplicate["deadman_budget"][2]["run"] = duplicate["deadman_budget"][0]["run"]
        with self.assertRaisesRegex(ValueError, "exactly the three gated D runs"):
            kit.ruling_1f_fit(duplicate, 6144, 5000.0)
        missing = self._slots(good)
        del missing["deadman_budget"][1]["phases_s"]["tool"]
        with self.assertRaises(ValueError):
            kit.ruling_1f_fit(missing, 6144, 5000.0)


CHILD = r'''
import json, signal, sys, time
from pathlib import Path
# The caller's own handlers, which r1.run restores on return: a late signal of
# the burst then cannot kill the child between the restore and the print below
# (a test race, seen under taskpolicy -b; the driver's teardown is what is tested).
for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
    signal.signal(sig, signal.SIG_IGN)
sys.path.insert(0, sys.argv[3])
from unittest.mock import patch
from scripts import align_r1_rehearsal as r1
from tests.align.test_r1_rehearsal import FakeWorld, NOON_SAFE
root, park = Path(sys.argv[1]), sys.argv[2]
world = FakeWorld(t_decline={"a1": 20.0, "b": 30.0, "a2": 21.0})
def runner(argv):
    argv = tuple(str(v) for v in argv)
    if "--output" in argv and Path(argv[argv.index("--output") + 1]).name == park:
        (root / "ready").write_text(str(world.mode))
        time.sleep(60)
    return world(argv)
args = type("Args", (), dict(output=root / "run", registration=root / "registration/r1_slots.json",
                             runtime=["fake-runtime"], include_4bit=False, synthetic=True))()
with patch.object(r1, "_now_local", lambda: NOON_SAFE), patch.object(r1, "_run", runner):
    code = r1.run(args)
print(json.dumps({"code": code, "mode": world.mode}))
'''


class RealSignalSeriesHighPowerTests(unittest.TestCase):
    def test_a_real_signal_under_the_adopted_series_mode_restores_automatic(self):
        # R5-5 keeps the host at 2 from the A-B-A decision to calibration-post
        # (step-d, X-G, the gated runs, the planning turns). A real TERM, INT
        # or HUP there (a burst for TERM) must leave the host Automatic, remove
        # the marker and still write r1_result.json.
        for park, signals in (("step_D_prefill_10k_decode_4096", (signal.SIGTERM, signal.SIGTERM)),
                              ("planning_turn_R_plus_2C.precool", (signal.SIGINT,)),
                              ("planning_turn_R_plus_0C", (signal.SIGHUP, signal.SIGTERM))):
            with self.subTest(park=park), tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
                td = Path(td)
                proc = subprocess.Popen([sys.executable, "-B", "-c", CHILD, str(td), park, str(ROOT)],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                deadline = time.monotonic() + 120
                while not (td / "ready").exists() and proc.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertEqual((td / "ready").read_text(), "2")     # parked under High Power
                for sig in signals:
                    proc.send_signal(sig)
                    time.sleep(0.05)
                out, err = proc.communicate(timeout=120)
                self.assertEqual(proc.returncode, 0, err)
                row = json.loads(out.strip().splitlines()[-1])
                self.assertEqual(row, {"code": 4, "mode": 0})
                self.assertFalse((td / ".align-r1-high-power").exists())
                result = json.loads((td / "run/r1_result.json").read_text())
                self.assertEqual(result["status"], "aborted")
                self.assertEqual(result["powermode"][-1]["point"], "restore_automatic")
                self.assertFalse((td / "registration/r1_slots.json").exists())


if __name__ == "__main__":
    unittest.main()
