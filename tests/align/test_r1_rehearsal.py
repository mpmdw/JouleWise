"""Synthetic acceptance for the ALIGN v4 R1 rehearsal driver."""
from __future__ import annotations

import json
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import align_r1_rehearsal as r1


def completed(argv, code=0, out="", err=""):
    return subprocess.CompletedProcess(argv, code, out, err)


class FakeWorld:
    def __init__(self, fail_kind=None, fail_restore=False, interrupt_kind=None):
        self.mode = 0
        self.calls = []
        self.fail_kind = fail_kind
        self.fail_restore = fail_restore
        self.interrupt_kind = interrupt_kind

    def __call__(self, argv):
        argv = tuple(str(v) for v in argv)
        self.calls.append(argv)
        if argv == r1.PowerModeGuard.QUERY:
            return completed(argv, out=f"AC Power: powermode {self.mode}\n")
        if argv in (r1.PowerModeGuard.AUTO, r1.PowerModeGuard.HIGH):
            mode = int(argv[-1])
            if mode == 0 and self.fail_restore:
                return completed(argv, code=1, err="restore denied")
            self.mode = mode
            return completed(argv)
        kind = argv[argv.index("--r1-kind") + 1]
        if kind == self.interrupt_kind:
            raise KeyboardInterrupt("synthetic signal path")
        if kind == self.fail_kind:
            return completed(argv, code=9, err="synthetic runtime failure")
        slots = {f"S{i}": float(i) for i in range(1, 10)}
        slots.update(B_D=8192, I_D=101.5, T_dead=1451.018, N_chunk=256,
                     t_decline=23.0, **{"class": "heavy"})
        payload = {"kind": kind, "fake_smc_journal": True,
                   "reference_c": 40.0,
                   "g0_release_c": 40.0 + (int(kind.rsplit("-", 1)[-1][:-1]) if kind.startswith("d-planning-turn") else 0),
                   "energy_j": 100.0 + 3.0 * (int(kind.rsplit("-", 1)[-1][:-1]) if kind.startswith("d-planning-turn") else 0),
                   "slots": slots if kind == "step-d" else {}}
        return completed(argv, out=json.dumps(payload))


class R1Tests(unittest.TestCase):
    def args(self, root, **changes):
        values = dict(output=Path(root) / "run", registration=Path(root) / "registration/r1_slots.json",
                      runtime=["fake-runtime"], include_4bit=True, synthetic=True)
        values.update(changes)
        return type("Args", (), values)()

    def test_synthetic_rehearsal_fills_every_slot_and_entire_plan(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 0)
            registration = json.loads((Path(td) / "registration/r1_slots.json").read_text())
            self.assertEqual(set(registration["slots"]), set(r1.SLOT_NAMES))
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            names = [phase["name"] for phase in result["phases"]]
            self.assertEqual(names[:8], [row[0] for row in r1.phase_plan(True)][:8])
            self.assertIn("D_4bit_optional", names)
            self.assertEqual(names[-4:], ["high_power_A1", "high_power_B", "high_power_A2", "harvest"])
            self.assertEqual([p["designed_g0_offset_c"] for p in result["phases"] if p["name"].startswith("planning_turn")], [0.0, 2.0, 4.0])
            self.assertEqual(registration["planning_temperature"]["absolute_band_c"], [40.0, 44.0])
            self.assertEqual(registration["ac_powermode"], 0)
            self.assertAlmostEqual(registration["planning_temperature"]["beta_T_j_per_c"], 3.0)
            self.assertEqual(registration["planning_temperature"]["beta_T_ci95_j_per_c"], [3.0, 3.0])
            self.assertEqual([p["powermode"] for p in result["phases"][-4:-1]], [0, 2, 0])
            self.assertEqual(world.mode, 0)
            self.assertGreaterEqual(world.calls.count(r1.PowerModeGuard.AUTO), 4)
            self.assertTrue(any("fake_smc_journal" in json.dumps(p) for p in result["phases"]))

    def test_restore_on_normal_error_and_signal_equivalent_paths(self):
        cases = ((FakeWorld(), 0), (FakeWorld(fail_kind="x-g"), 3),
                 (FakeWorld(interrupt_kind="x-g"), 4))
        for index, (world, expected) in enumerate(cases):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as td:
                with patch.object(r1, "_run", world):
                    self.assertEqual(r1.run(self.args(td, include_4bit=False)), expected)
                self.assertEqual(world.mode, 0)
                self.assertIn(r1.PowerModeGuard.AUTO, world.calls)

    def test_refuses_before_work_when_restore_cannot_be_proved(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(fail_restore=True)
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 3)
            runtime_calls = [call for call in world.calls if "--r1-kind" in call]
            self.assertEqual(runtime_calls, [])
            self.assertFalse((Path(td) / "registration/r1_slots.json").exists())

    def test_power_helper_uses_only_the_two_allowed_sudo_commands(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 0)
            sudo_calls = [call for call in world.calls if call and call[0] == "sudo"]
            self.assertTrue(sudo_calls)
            self.assertTrue(all(call in (r1.PowerModeGuard.AUTO, r1.PowerModeGuard.HIGH)
                                for call in sudo_calls))

    def test_persistent_marker_recovers_prior_sigkill_with_fake_pmset_and_sudo(self):
        with tempfile.TemporaryDirectory() as td:
            marker = Path(td)/'high.marker'
            marker.write_text('previous run died\n')
            world = FakeWorld()
            guard = r1.PowerModeGuard(world, marker)
            with guard:
                self.assertFalse(marker.exists())  # startup restoration
                guard.high()
                self.assertTrue(marker.exists())
            self.assertFalse(marker.exists())
            self.assertEqual(world.mode, 0)

    def test_refuses_missing_or_nonfinite_slots(self):
        values = {name: 1.0 for name in r1.SLOT_NAMES[:-1]}
        values["class"] = "heavy"
        del values["S9"]
        with self.assertRaisesRegex(r1.Refusal, "omitted slots: S9"):
            r1.derive_slots({"slots": values})
        values["S9"] = float("nan")
        with self.assertRaisesRegex(r1.Refusal, "not finite"):
            r1.derive_slots({"slots": values})

    def test_planning_temperature_refuses_wrong_g0_release(self):
        rows = [{"reference_c": 40, "g0_release_c": 40 + o, "energy_j": 10 + o} for o in (0, 2, 5)]
        with self.assertRaisesRegex(r1.Refusal, "designed offset"):
            r1.planning_temperature_summary(rows)

    def test_plan_pins_durations_and_gated_held_members(self):
        rows = r1.phase_plan(False)
        self.assertEqual(rows[0], ("pre_calibration_bracket", "calibration-pre", None, "light"))
        self.assertEqual(rows[1], ("idle_soak", "idle", 1800, "light"))
        self.assertEqual(rows[-1], ("post_calibration_bracket", "calibration-post", None, "light"))
        self.assertEqual([row[2] for row in rows if row[0].startswith("cooldown")], [600, 600])
        self.assertIn(("step_D_prefill_10k_decode_4096", "step-d", None, "heavy"), rows)
        self.assertIn(("D_spam_s1_gated_held", "d-spam-s1", None, "heavy"), rows)
        self.assertIn(("D_benign_s1_gated_held", "d-benign-s1", None, "heavy"), rows)


if __name__ == "__main__":
    unittest.main()
