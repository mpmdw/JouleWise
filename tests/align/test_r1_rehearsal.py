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


PMSET_TEMPLATE = (
    "System-wide power settings:\n"
    "Currently in use:\n"
    " lowpowermode         0\n"
    "Battery Power:\n"
    " lowpowermode         0\n"
    " powermode            0\n"
    "AC Power:\n"
    " lowpowermode         0\n"
    " powermode            {mode}\n"
    " sleep                0\n"
)


class FakeWorld:
    def __init__(self, fail_kind=None, fail_restore=False, interrupt_kind=None,
                 t_decline=None, busy_once=(), sudo_listing=None, unsettled_soak_once=False):
        self.mode = 0
        self.calls = []
        self.fail_kind = fail_kind
        self.fail_restore = fail_restore
        self.interrupt_kind = interrupt_kind
        self.t_decline = t_decline or {"a1": 20.0, "b": 21.0, "a2": 20.0}
        self.busy_once = set(busy_once)
        self.unsettled_soak_once = unsettled_soak_once
        self.sudo_listing = sudo_listing if sudo_listing is not None else (
            "(root) NOPASSWD: /usr/bin/pmset -c powermode 0\n"
            "(root) NOPASSWD: /usr/bin/pmset -c powermode 2\n")

    def __call__(self, argv):
        argv = tuple(str(v) for v in argv)
        self.calls.append(argv)
        if argv == r1.PowerModeGuard.LIST:
            return completed(argv, out=self.sudo_listing)
        if argv == r1.PowerModeGuard.QUERY:
            return completed(argv, out=PMSET_TEMPLATE.format(mode=self.mode))
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
        offset = int(kind.rsplit("-", 1)[-1][:-1]) if kind.startswith("d-planning-turn") else 0
        busy = kind in self.busy_once
        self.busy_once.discard(kind)
        payload = {"kind": kind, "fake_smc_journal": True,
                   "reference_c": 40.0, "g0_release_c": 40.0 + offset,
                   "energy_j": 100.0 + 3.0 * offset,
                   "cpu_busy_cores": [0.9] * 61 if busy else [0.1] * 61,
                   "census": [{"pid": 1, "name": "launchd"}],
                   "slots": slots if kind == "step-d" else {}}
        if kind == "idle":
            slope = 0.5 / 60 if self.unsettled_soak_once else 0.0
            self.unsettled_soak_once = False
            payload["sensor_series_c"] = {"s_slow": [40.0 + slope * i + (0.05 if i % 2 else -0.05)
                                                     for i in range(1800)]}
        if kind == "step-d":
            payload["e_D_j_per_token"] = 3.6
        if kind == "idle-until-soak":
            payload["recovery_curve"] = [[0, 55.0], [600, 45.0], [900, 41.0]]
        if kind.startswith("d-") and "planning" not in kind and kind != "d-4bit":
            payload.update(energy_j={"d-spam-benign-s1-a": 30000.0, "d-spam-benign-s1-b": 30036.0,
                                     "d-bank-benign-s1": 32000.0}[kind],
                           admitted_turns=3, x7=False,
                           deadman={"T_dead_s": 1451.018, "phases_s": {
                               "G0": 120.0, "G1": 150.0, "H": 90.0, "decode": 700.0,
                               "prefill": 120.0, "tool": 6.0, "tail": 20.0}})
        if kind == "g0-release-soak":
            payload["released"] = True
        if kind.startswith("high-power-aba-"):
            payload["t_decline_s"] = self.t_decline[kind.rsplit("-", 1)[-1]]
        return completed(argv, out=json.dumps(payload))


NOON_SAFE = r1.datetime(2026, 11, 7, 2, 0).astimezone()


class R1Tests(unittest.TestCase):
    def setUp(self):
        clock = patch.object(r1, "_now_local", lambda: NOON_SAFE)
        clock.start()
        self.addCleanup(clock.stop)

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
            self.assertEqual([p["name"] for p in result["phases"] if p["name"].startswith("planning_turn")],
                             ["planning_turn_R_plus_0C", "planning_turn_R_plus_2C", "planning_turn_R_plus_4C"])
            self.assertLess(names.index("planning_turn_R_plus_4C"), names.index("post_calibration_bracket"))
            self.assertEqual(registration["planning_temperature"]["designed_release_range_c"], [40.0, 44.0])
            self.assertEqual(registration["ac_powermode"], 0)
            self.assertEqual(registration["high_power"]["verdict"], "not_adopted")
            self.assertAlmostEqual(registration["planning_temperature"]["beta_T_j_per_c"], 3.0)
            self.assertAlmostEqual(registration["planning_temperature"]["abs_beta_T_90_j_per_c"], 3.0)
            self.assertEqual(len(registration["deadman_budget"]), 3)
            self.assertTrue(registration["duty_bar"]["pass"])
            self.assertEqual(registration["max_r1_tail_s"], 20.0)
            self.assertAlmostEqual(registration["projected_mde"]["replay_pair_abs_diff_j"], 36.0)
            self.assertAlmostEqual(registration["projected_mde"]["replay_pair_floor_tokens"], 10.0)
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
            self.assertTrue(all(call in (r1.PowerModeGuard.AUTO, r1.PowerModeGuard.HIGH,
                                             r1.PowerModeGuard.LIST)
                                for call in sudo_calls))

    def test_refuses_incomplete_sudo_rule_before_any_runtime_work(self):
        guard = r1.PowerModeGuard(lambda argv: completed(argv, out="/usr/bin/pmset -c powermode 0\n"))
        with self.assertRaisesRegex(r1.Refusal, "sudo_rule_missing"):
            guard.__enter__()
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(sudo_listing="(root) NOPASSWD: /usr/bin/pmset -c powermode 0\n")
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 3)
            self.assertFalse([call for call in world.calls if "--r1-kind" in call])

    def test_zsh_chain_verifies_sudo_listing(self):
        chain = (Path(__file__).resolve().parents[2] / "scripts/night_chains/align_r1_rehearsal.zsh").read_text()
        self.assertIn("sudo -n -l", chain)
        self.assertIn("'/usr/bin/pmset -c powermode 2'", chain)

    def test_ac_powermode_reads_only_the_ac_powermode_key(self):
        self.assertEqual(r1.parse_ac_powermode(PMSET_TEMPLATE.format(mode=2)), 2)
        # lowpowermode precedes powermode in the AC block and must not match.
        self.assertEqual(r1.parse_ac_powermode(PMSET_TEMPLATE.format(mode=0)), 0)
        self.assertIsNone(r1.parse_ac_powermode("AC Power:\n lowpowermode 0\n"))
        self.assertIsNone(r1.parse_ac_powermode("Battery Power:\n powermode 2\n"))

    def test_series_powermode_is_the_aba_adoption_outcome(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(t_decline={"a1": 20.0, "b": 30.0, "a2": 21.0})
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 0)
            registration = json.loads((Path(td) / "registration/r1_slots.json").read_text())
            self.assertEqual(registration["high_power"]["verdict"], "adopt")
            self.assertEqual(registration["ac_powermode"], 2)
            self.assertEqual(world.mode, 0)  # the host itself is still restored
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            aba = [p for p in result["phases"] if p["name"].startswith("high_power_")]
            self.assertTrue(all(p["g0_release"]["released"] for p in aba))

    def test_high_power_adoption_rule(self):
        adopt = r1.high_power_adoption
        self.assertEqual(adopt(20, 25, 20)["verdict"], "adopt")
        self.assertEqual(adopt(20, 24.9, 20)["verdict"], "not_adopted")
        self.assertEqual(adopt(20, None, 22)["verdict"], "adopt")
        self.assertEqual(adopt(None, None, None)["verdict"], "not_adopted")
        self.assertEqual(adopt(20, 40, 27)["verdict"], "inconclusive")
        self.assertEqual(adopt(20, 40, None)["verdict"], "inconclusive")

    def test_gated_d_runs_are_replay_pair_plus_bank_benign(self):
        kinds = [row[1] for row in r1.phase_plan(False) if row[0].endswith("_gated_held")
                 or row[0].endswith(("_held_a", "_held_b"))]
        self.assertEqual(kinds, ["d-spam-benign-s1-a", "d-spam-benign-s1-b", "d-bank-benign-s1"])

    def test_duty_bar_fails_on_gate_hold_share_and_names_fallbacks(self):
        result = {"admitted_turns": 3, "x7": False, "deadman": {"T_dead_s": 1000.0, "phases_s": {
            "G0": 300.0, "G1": 60.0, "H": 50.0, "decode": 400.0, "prefill": 50.0, "tool": 5.0, "tail": 10.0}}}
        row = r1.deadman_summary("d", result)
        self.assertFalse(row["duty_bar"]["checks"]["gate_hold_le_40pct_T_dead"])
        self.assertAlmostEqual(row["predicted_turns_per_episode"], (1000 - 300 - 10) / (565 / 3))
        del result["deadman"]["phases_s"]["tail"]
        with self.assertRaisesRegex(r1.Refusal, "tail"):
            r1.deadman_summary("d", result)

    def test_cooldown_after_d_waits_for_soak_up_to_1500_s_and_records_curve(self):
        rows = {row[0]: row for row in r1.phase_plan(False)}
        self.assertEqual(rows["cooldown_after_D"][1:3], ("idle-until-soak", 1500))

    def test_quiet_segment_redone_on_sustained_cpu_load(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(busy_once={"step-d"}, unsettled_soak_once=True)
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 0)
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            step = [p for p in result["phases"] if p["name"] == "step_D_prefill_10k_decode_4096"]
            self.assertEqual(len(step), 1)
            self.assertEqual(step[0]["attempt"], 1)
            self.assertEqual(step[0]["superseded_attempts"][0]["redo_reason"], "cpu_load")
            soak = [p for p in result["phases"] if p["name"] == "idle_soak"][0]
            self.assertEqual(soak["superseded_attempts"][0]["redo_reason"], "soak_slope")
            self.assertTrue(soak["soak_detrended"]["s_slow"]["settled"])
            self.assertAlmostEqual(soak["soak_detrended"]["s_slow"]["detrended_sd_c"], 0.05, places=3)

    def test_quiet_segments_avoid_the_os_batch_window(self):
        sleeps = []
        moments = [r1.datetime(2026, 11, 7, 11, 30).astimezone()]
        def now():
            return moments[-1]
        def sleep(seconds):
            sleeps.append(seconds)
            moments.append(moments[-1] + r1.timedelta(seconds=seconds))
        waited = r1.wait_outside_os_batch(1800, now=now, sleep=sleep)
        self.assertEqual(moments[-1].strftime("%H:%M"), "13:15")
        self.assertEqual(waited, sum(sleeps))
        self.assertEqual(r1.wait_outside_os_batch(600, now=lambda: r1.datetime(2026, 11, 7, 11, 30).astimezone(),
                                                  sleep=sleep), 0.0)

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
        self.assertEqual([row[2] for row in rows if row[0].startswith("cooldown")], [600, 1500])
        self.assertIn(("step_D_prefill_10k_decode_4096", "step-d", None, "heavy"), rows)
        self.assertIn(("D_spam_benign_s1_gated_held_a", "d-spam-benign-s1-a", None, "heavy"), rows)
        self.assertIn(("D_spam_benign_s1_gated_held_b", "d-spam-benign-s1-b", None, "heavy"), rows)
        self.assertIn(("D_bank_benign_s1_gated_held", "d-bank-benign-s1", None, "heavy"), rows)


if __name__ == "__main__":
    unittest.main()
