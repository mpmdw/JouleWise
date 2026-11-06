"""Synthetic acceptance for the ALIGN v4 R1 rehearsal driver."""
from __future__ import annotations

import json
import os
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
                 t_decline=None, busy_once=(), sudo_listing=None, unsettled_soak_once=False,
                 release_c=None, released=True, ignore_automatic=False):
        self.mode = 0
        self.attempts = {}
        self.release_c = release_c or {}
        self.released = released
        self.ignore_automatic = ignore_automatic
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
            if not (mode == 0 and self.ignore_automatic):
                self.mode = mode
            return completed(argv)
        kind = argv[argv.index("--r1-kind") + 1]
        # Like a real runtime, write into --output so directory custody is testable.
        out = Path(argv[argv.index("--output") + 1])
        out.mkdir(parents=True, exist_ok=False)
        self.attempts[kind] = self.attempts.get(kind, 0) + 1
        (out / "attempt.txt").write_text(f"{kind} {self.attempts[kind]}\n")
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
                   "reference_c": 40.0, "g0_release_c": self.release_c.get(offset, 40.0 + offset),
                   "delta_slow_c": 0.5,
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
            payload["released"] = self.released
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

    def test_restore_command_success_without_automatic_readback_keeps_marker(self):
        with tempfile.TemporaryDirectory() as td:
            marker = Path(td) / "restore-required"
            marker.write_text("prior crash\n")
            world = FakeWorld(ignore_automatic=True)
            world.mode = 2
            guard = r1.PowerModeGuard(world, marker)
            with self.assertRaisesRegex(r1.Refusal, "cannot_restore"):
                guard.__enter__()
            self.assertTrue(marker.exists())
            self.assertEqual(world.mode, 2)

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

    def test_sudo_rule_match_is_command_exact_not_a_prefix(self):
        listing = ("(root) NOPASSWD: /usr/bin/pmset -c powermode 0\n"
                   "(root) NOPASSWD: /usr/bin/pmset -c powermode 20\n")
        guard = r1.PowerModeGuard(lambda argv: completed(argv, out=listing))
        with self.assertRaisesRegex(r1.Refusal, "powermode 2"):
            guard.__enter__()

    def test_zsh_chain_verifies_sudo_listing(self):
        chain = (Path(__file__).resolve().parents[2] / "scripts/night_chains/align_r1_rehearsal.zsh").read_text()
        self.assertIn("sudo -n -l", chain)
        self.assertIn("'/usr/bin/pmset -c powermode 2'", chain)

    def test_zsh_power_marker_survives_into_the_next_night(self):
        # NIGHT_DIR is new every night, so a marker there is never seen by the
        # next night's startup after a SIGKILL; run_night's MEASUREMENT_ROOT is
        # stable and required.
        chain = (Path(__file__).resolve().parents[2] / "scripts/night_chains/align_r1_rehearsal.zsh").read_text()
        self.assertIn(': "${MEASUREMENT_ROOT:?', chain)
        self.assertIn('POWER_MARKER="$MEASUREMENT_ROOT/.align-r1-high-power"', chain)
        self.assertNotIn('POWER_MARKER="$NIGHT_DIR', chain)

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

    def test_deadman_refuses_negative_phase_accounting(self):
        phases = {name: 1.0 for name in r1.DEADMAN_PHASES}
        phases["H"] = -1.0
        result = {"admitted_turns": 3, "x7": False,
                  "deadman": {"T_dead_s": 100.0, "phases_s": phases}}
        with self.assertRaisesRegex(r1.Refusal, "non-negative"):
            r1.deadman_summary("d", result)

    def test_atomic_json_preserves_the_previous_record_and_happy_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "record.json"
            value = {"z": [1, 2], "a": "same bytes"}
            expected = json.dumps(value, indent=2, sort_keys=True) + "\n"
            r1._atomic_json(path, value)
            self.assertEqual(path.read_text(), expected)
            previous = path.read_bytes()
            with patch.object(r1.os, "replace", side_effect=OSError("synthetic crash")):
                with self.assertRaisesRegex(OSError, "synthetic crash"):
                    r1._atomic_json(path, {"replacement": True})
            self.assertEqual(path.read_bytes(), previous)
            self.assertFalse((path.parent / ".record.json.tmp").exists())

    def test_registration_cannot_overwrite_the_measurement_record(self):
        with tempfile.TemporaryDirectory() as td:
            args = self.args(td, registration=Path(td) / "run/r1_result.json")
            with patch.object(r1, "_run", FakeWorld()):
                self.assertEqual(r1.run(args), 3)
            record = json.loads((Path(td) / "run/r1_result.json").read_text())
            self.assertEqual(record["status"], "refused")
            self.assertIn("registration inside R1 custody", record["error"])

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

    def test_marker_is_written_before_high_power_command(self):
        with tempfile.TemporaryDirectory() as td:
            marker = Path(td)/'host.marker'
            observed = []
            world = FakeWorld()
            def runner(argv):
                if tuple(argv) == r1.PowerModeGuard.HIGH:
                    observed.append(marker.exists())
                return world(argv)
            guard = r1.PowerModeGuard(runner, marker)
            with guard:
                guard.high()
            self.assertEqual(observed, [True])

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
        rows = [{"reference_c": 40, "g0_release_c": 40 + o, "delta_slow_c": 0.5, "energy_j": 10 + o}
                for o in (0, 2, 5)]
        with self.assertRaisesRegex(r1.Refusal, "designed offset"):
            r1.planning_temperature_summary(rows)

    def test_planning_release_is_checked_against_the_gate_band_not_1e9(self):
        # A measured S_slow 0.4 C off R + offset is a valid G0 release within
        # delta_slow = 0.5 C; 0.6 C off is not the designed state.
        rows = [{"reference_c": 40.0, "g0_release_c": 40.0 + o + e, "delta_slow_c": 0.5, "energy_j": 100 + 3 * o}
                for o, e in ((0, 0.0), (2, 0.4), (4, -0.3))]
        summary = r1.planning_temperature_summary(rows)
        self.assertEqual(summary["measured_release_range_c"], [40.0, 43.7])
        self.assertAlmostEqual(summary["points"][1]["release_error_c"], 0.4)
        # beta_T is fitted on the measured release temperatures.
        xs, ys = [40.0, 42.4, 43.7], [100.0, 106.0, 112.0]
        xbar, ybar = sum(xs) / 3, sum(ys) / 3
        beta = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sum((x - xbar) ** 2 for x in xs)
        self.assertAlmostEqual(summary["beta_T_j_per_c"], beta)
        rows[1]["g0_release_c"] = 42.6
        with self.assertRaisesRegex(r1.Refusal, "outside R \\+ designed offset"):
            r1.planning_temperature_summary(rows)
        rows[1]["g0_release_c"] = 42.0
        rows[2]["delta_slow_c"] = 1.0
        with self.assertRaisesRegex(r1.Refusal, "one gate band"):
            r1.planning_temperature_summary(rows)

    def test_planning_release_band_end_to_end(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(release_c={2: 42.4})
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 0)
            registration = json.loads((Path(td) / "registration/r1_slots.json").read_text())
            self.assertEqual(registration["planning_temperature"]["points"][1]["g0_release_c"], 42.4)

    def test_u5_is_declared_with_c_equal_one_and_evaluated(self):
        self.assertEqual(r1.U5_C, 1.0)
        temperature = {"delta_slow_c": 2.0, "beta_T_j_per_c": 1.0, "beta_T_ci90_j_per_c": [-0.5, 2.5],
                       "abs_beta_T_90_j_per_c": 2.5}
        gated = {r1.REPLAY_PAIR[0]: {"energy_j": 1000.0}, r1.REPLAY_PAIR[1]: {"energy_j": 1006.0}}
        u5 = r1.u5_verdict(temperature, gated)
        # sigma_pair = max(|1000 - 1006|, 2.97) = 6; bar = 1.0 x 6.
        self.assertEqual((u5["c"], u5["sigma_pair_j"], u5["bar_j"]), (1.0, 6.0, 6.0))
        self.assertEqual(u5["state_shift_bound90_j"], 5.0)
        self.assertEqual(u5["verdict"], "pass")
        gated[r1.REPLAY_PAIR[1]]["energy_j"] = 1001.0  # floor 2.97 J governs
        u5 = r1.u5_verdict(temperature, gated)
        self.assertEqual((u5["sigma_pair_j"], u5["verdict"]), (2.97, "inconclusive"))
        temperature.update(beta_T_j_per_c=2.0, abs_beta_T_90_j_per_c=3.5)
        self.assertEqual(r1.u5_verdict(temperature, gated)["verdict"], "fail")
        with tempfile.TemporaryDirectory() as td:
            with patch.object(r1, "_run", FakeWorld()):
                self.assertEqual(r1.run(self.args(td)), 0)
            registration = json.loads((Path(td) / "registration/r1_slots.json").read_text())
            self.assertEqual(registration["u5"]["c"], 1.0)
            self.assertEqual(registration["u5"]["sigma_pair_j"], 36.0)
            self.assertIn(registration["u5"]["verdict"], ("pass", "fail", "inconclusive"))

    def test_heavy_redo_waits_for_a_g0_release_against_the_soak(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(busy_once={"step-d"})
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 0)
            kinds = [c[c.index("--r1-kind") + 1] for c in world.calls if "--r1-kind" in c]
            first = kinds.index("step-d")
            # The contaminated attempt is followed by a release, never directly by the redo.
            self.assertEqual(kinds[first:first + 3], ["step-d", "g0-release-soak", "step-d"])
            release = [c for c in world.calls if "--r1-kind" in c and "g0-release-soak" in c][0]
            soak_ref = Path(td) / "run/soak_reference.json"
            self.assertEqual(release[release.index("--soak-reference") + 1], str(soak_ref.resolve()))
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            step = [p for p in result["phases"] if p["name"] == "step_D_prefill_10k_decode_4096"][0]
            self.assertTrue(step["g0_release"]["released"])
            # The soak redo (light) needs no release; the first heavy attempt neither.
            self.assertNotIn("g0_release", step["superseded_attempts"][0])

    def test_accepted_attempt_owns_the_canonical_directory(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(busy_once={"step-d"}, unsettled_soak_once=True)
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 0)
            run_dir = Path(td) / "run"
            self.assertEqual((run_dir / "step_D_prefill_10k_decode_4096/attempt.txt").read_text(), "step-d 2\n")
            self.assertEqual((run_dir / "step_D_prefill_10k_decode_4096.rejected1/attempt.txt").read_text(),
                             "step-d 1\n")
            self.assertEqual((run_dir / "idle_soak/attempt.txt").read_text(), "idle 2\n")
            self.assertTrue((run_dir / "idle_soak.rejected1").is_dir())
            self.assertFalse(list(run_dir.glob("*.redo*")))
            result = json.loads((run_dir / "r1_result.json").read_text())
            step = [p for p in result["phases"] if p["name"] == "step_D_prefill_10k_decode_4096"][0]
            self.assertEqual(step["output_dir"], str((run_dir / "step_D_prefill_10k_decode_4096").resolve()))
            self.assertEqual(step["superseded_attempts"][0]["output_dir"],
                             str((run_dir / "step_D_prefill_10k_decode_4096.rejected1").resolve()))

    def test_every_post_soak_runtime_call_gets_the_soak_reference(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 0)
            reference = json.loads((Path(td) / "run/soak_reference.json").read_text())
            self.assertEqual(reference["schema"], r1.SOAK_REFERENCE_SCHEMA)
            self.assertAlmostEqual(reference["sensors_c"]["s_slow"], 40.0, places=6)
            runtime = [c for c in world.calls if "--r1-kind" in c]
            kinds = [c[c.index("--r1-kind") + 1] for c in runtime]
            soak = kinds.index("idle")
            self.assertTrue(all("--soak-reference" not in c for c in runtime[:soak + 1]))
            self.assertTrue(all("--soak-reference" in c for c in runtime[soak + 1:]))

    def test_aba_legs_avoid_the_os_batch_window_and_are_redone_on_load(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(busy_once={"high-power-aba-b"})

            def wait(expected_s, **_):
                world.calls.append(("WAIT", expected_s))
                return 0.0
            with patch.object(r1, "_run", world), patch.object(r1, "wait_outside_os_batch", wait):
                self.assertEqual(r1.run(self.args(td)), 0)
            for leg in ("high-power-aba-a1", "high-power-aba-b", "high-power-aba-a2"):
                index = next(i for i, c in enumerate(world.calls) if "--r1-kind" in c and leg in c)
                window = world.calls[index - 2:index]
                self.assertEqual(window[0][0], "WAIT", leg)
                self.assertIn("g0-release-soak", window[1], leg)
                self.assertEqual(window[0][1], r1.QUIET_SEGMENT_BOUND_S + r1.G0_RELEASE_BOUND_S)
            b_calls = [c for c in world.calls if "--r1-kind" in c and "high-power-aba-b" in c]
            self.assertEqual(len(b_calls), 2)
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            b = [p for p in result["phases"] if p["name"] == "high_power_B"]
            self.assertEqual(len(b), 1)
            self.assertEqual(b[0]["superseded_attempts"][0]["redo_reason"], "cpu_load")
            self.assertEqual(b[0]["powermode"], 2)
            self.assertIn("os_load", b[0])

    def test_aba_leg_without_g0_release_makes_adoption_inconclusive(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(t_decline={"a1": 20.0, "b": 30.0, "a2": 21.0}, released=False)
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 0)
            registration = json.loads((Path(td) / "registration/r1_slots.json").read_text())
            self.assertEqual(registration["high_power"]["verdict"], "inconclusive")
            self.assertEqual(registration["high_power"]["rule_outcome"]["verdict"], "adopt")
            self.assertEqual(registration["ac_powermode"], 0)

    def test_runtime_contract_fields_are_enforced_at_the_seam(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()
            original = world.__call__

            def drop_recovery(argv):
                result = original(argv)
                if "idle-until-soak" in argv:
                    payload = json.loads(result.stdout)
                    del payload["recovery_curve"]
                    result = completed(argv, out=json.dumps(payload))
                return result
            with patch.object(r1, "_run", drop_recovery):
                self.assertEqual(r1.run(self.args(td)), 3)
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            self.assertIn("contract fields missing: recovery_curve", result["error"])

    def test_signal_burst_cannot_interrupt_the_automatic_restore(self):
        # Executing review 2026-11-06: a second TERM/INT during teardown (an
        # operator pressing Ctrl-C again, or a burst) interrupted every Python
        # restore attempt and left the host in High Power.
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()
            state = {"in_b": False}

            def runner(argv):
                argv = tuple(str(v) for v in argv)
                if "--r1-kind" in argv and "high-power-aba-b" in argv:
                    state["in_b"] = True
                    os.kill(os.getpid(), signal.SIGTERM)       # first signal: abort the leg
                if argv == r1.PowerModeGuard.AUTO and state["in_b"]:
                    os.kill(os.getpid(), signal.SIGINT)        # a further signal mid-restore
                return world(argv)
            previous = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
            with patch.object(r1, "_run", runner):
                rc = r1.run(self.args(td, power_marker=Path(td) / "marker"))
            self.assertEqual(rc, 4)
            self.assertEqual(world.mode, 0)
            self.assertFalse((Path(td) / "marker").exists())
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            self.assertEqual(result["status"], "aborted")
            self.assertEqual({sig: signal.getsignal(sig) for sig in previous}, previous)

    def test_gated_d_runs_must_arm_the_step_d_t_dead(self):
        # Executing review 2026-11-06: the duty bar (ruling 1(d)) is a share of
        # T_dead, and the driver took each gated run's T_dead_s on trust. A run
        # reporting 5,000 s (past the workload's own 1800/1.13544 bound) passed
        # the bar. Every gated run must arm the one T_dead R1 freezes.
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()

            def runner(argv):
                result = world(argv)
                if "--r1-kind" in argv and "d-spam-benign-s1-b" in argv:
                    payload = json.loads(result.stdout)
                    payload["deadman"]["T_dead_s"] = 5000.0
                    result = completed(argv, out=json.dumps(payload))
                return result
            with patch.object(r1, "_run", runner):
                self.assertEqual(r1.run(self.args(td)), 3)
            self.assertEqual(world.mode, 0)
            self.assertFalse((Path(td) / "registration/r1_slots.json").exists())
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            self.assertIn("D_spam_benign_s1_gated_held_b", result["error"])
            self.assertIn("T_dead", result["error"])
            kinds = [c[c.index("--r1-kind") + 1] for c in world.calls if "--r1-kind" in c]
            # Fail fast: nothing after the offending run.
            self.assertEqual(kinds[-1], "d-spam-benign-s1-b")

    def test_zsh_chain_signal_burst_still_restores_automatic(self):
        # The chain's own trap must also survive a second signal: with
        # ``trap - ... TERM`` the next TERM killed both the shell and its
        # restoring sudo, so the backstop never ran.
        repo = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
            td = Path(td)
            (td / "bin").mkdir()
            state, armed = td / "pm_state", td / "armed"
            state.write_text("0\n")
            sudo = td / "bin/sudo"
            sudo.write_text(
                "#!/bin/zsh\n"
                'if [[ "$1 $2" == "-n -l" ]]; then\n'
                '  print "(root) NOPASSWD: /usr/bin/pmset -c powermode 0, /usr/bin/pmset -c powermode 2"; exit 0\n'
                "fi\n"
                'if [[ "$1 $2 $3 $4" == "-n /usr/bin/pmset -c powermode" ]]; then\n'
                f'  if [[ -e {armed} && "$5" == 0 ]]; then kill -TERM 0; sleep 0.5; fi\n'
                f'  print -r -- "$5" > {state}; exit 0\n'
                "fi\n"
                "exit 1\n")
            shim = td / "py"
            # Stands in for the driver: High Power is on, then the group is signalled.
            shim.write_text(f"#!/bin/zsh\nprint 2 > {state}\n: > {armed}\nkill -TERM 0\nsleep 5\n")
            for path in (sudo, shim):
                path.chmod(0o755)
            (td / "mroot").mkdir()
            env = dict(os.environ, PATH=f"{td / 'bin'}:{os.environ['PATH']}", PY=str(shim),
                       NIGHT_DIR=str(td / "night"), MEASUREMENT_ROOT=str(td / "mroot"),
                       ALIGN_R1_RUNTIME="/usr/bin/true")
            proc = subprocess.run(["/bin/zsh", str(repo / "scripts/night_chains/align_r1_rehearsal.zsh")],
                                  env=env, start_new_session=True, capture_output=True, text=True,
                                  timeout=60)
            self.assertEqual(state.read_text().strip(), "0", proc.stderr)
            self.assertEqual(proc.returncode, 130)

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
