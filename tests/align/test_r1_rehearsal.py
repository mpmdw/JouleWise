"""Synthetic acceptance for the ALIGN v4 R1 rehearsal driver."""
from __future__ import annotations

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


MOUNT_INTERNAL = ("/dev/disk3s1s1 on / (apfs, sealed, local, read-only, journaled)\n"
                  "devfs on /dev (devfs, local, nobrowse)\n"
                  "/dev/disk3s5 on /System/Volumes/Data (apfs, local, journaled, nobrowse)\n")
MOUNT_SSD = MOUNT_INTERNAL + "/dev/disk6s1 on /Volumes/JW-EXT (apfs, local, nodev, nosuid, journaled)\n"


def diskutil_plist(device):
    import plistlib
    external = device.startswith("/dev/disk6")
    return plistlib.dumps({"VolumeUUID": "0" * 8 + "-0000-0000-0000-" + "0" * 12,
                           "VolumeName": "JW-EXT" if external else "Macintosh HD",
                           "FilesystemType": "apfs", "BusProtocol": "USB" if external else "Apple Fabric",
                           "WritableVolume": True, "Internal": not external}).decode()


class FakeWorld:
    def __init__(self, fail_kind=None, fail_restore=False, interrupt_kind=None,
                 t_decline=None, busy_once=(), sudo_listing=None, unsettled_soak_once=False,
                 release_c=None, released=True, mount_after=None, journal_gap_kind=None, tail=20.0,
                 precool_timeout=(), leg_g0_unreleased=(), thermometry_status="pass",
                 b_d=8192, slot_changes=None, failed_soak_reads=0, g0_timeout=(), calibration_g0_timeouts=None,
                 gated_decode_tokens=12600, g0_waits=None, step_d_rate=20.0):
        self.tail = tail
        self.step_d_rate = step_d_rate
        # R7-2: gated run / X-G (by output name) -> its released G0 wait (s).
        self.g0_waits = dict(g0_waits or {})
        self.precool_timeout = set(precool_timeout)
        # R6-1: gated runs / X-G (by output name) whose G0 times out.
        self.g0_timeout = set(g0_timeout)
        # R6-2: kind -> how many times step-d / a designed state reports INCONCLUSIVE.
        self.calibration_g0_timeouts = dict(calibration_g0_timeouts or {})
        self.gated_decode_tokens = gated_decode_tokens
        self.leg_g0_unreleased = set(leg_g0_unreleased)
        self.thermometry_status = thermometry_status
        self.invocations = []     # (kind, output name, AC powermode at the call)
        self.b_d = b_d
        self.slot_changes = slot_changes or {}
        self.failed_soak_reads = failed_soak_reads
        self.mounted = False
        self.mount_after = mount_after
        self.journal_gap_kind = journal_gap_kind
        self.mode = 0
        self.attempts = {}
        self.release_c = release_c or {}
        self.released = released
        self.calls = []
        self.fail_kind = fail_kind
        self.fail_restore = fail_restore
        self.interrupt_kind = interrupt_kind
        self.t_decline = t_decline or {"a1": 20.0, "b": 21.0, "a2": 20.0}
        self.busy_once = set(busy_once)
        self.unsettled_soak_once = unsettled_soak_once
        self.charge_resume_soc = 94
        self.sudo_listing = sudo_listing if sudo_listing is not None else (
            "(root) NOPASSWD: /usr/bin/pmset -c powermode 0\n"
            "(root) NOPASSWD: /usr/bin/pmset -c powermode 2\n")

    def __call__(self, argv):
        argv = tuple(str(v) for v in argv)
        self.calls.append(argv)
        if argv == ("/sbin/mount",):
            return completed(argv, out=MOUNT_SSD if self.mounted else MOUNT_INTERNAL)
        if argv[:3] == ("/usr/sbin/diskutil", "info", "-plist"):
            return completed(argv, out=diskutil_plist(argv[3]))
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
        if kind == self.mount_after:
            self.mounted = True  # the SSD is attached while this segment runs
        # Like a real runtime, write into --output so directory custody is testable.
        out = Path(argv[argv.index("--output") + 1])
        out.mkdir(parents=True, exist_ok=False)
        self.invocations.append((kind, out.name, self.mode))
        self.attempts[kind] = self.attempts.get(kind, 0) + 1
        (out / "attempt.txt").write_text(f"{kind} {self.attempts[kind]}\n")
        if kind == self.interrupt_kind:
            raise KeyboardInterrupt("synthetic signal path")
        if kind == self.fail_kind:
            return completed(argv, code=9, err="synthetic runtime failure")
        slots = {f"S{i}": float(i) for i in range(1, 10)}
        # S5 = S6 = delta_slow and S7 = G_turn, as the runtime derives them.
        slots.update(S5_fast=8.0, S5=1.0, S6=1.0, S7=120.0, B_D=self.b_d, I_D=101.5, T_dead=1451.018, N_chunk=256,
                     t_decline=23.0, **{"class": "heavy"})
        slots.update(self.slot_changes)
        offset = int(kind.rsplit("-", 1)[-1][:-1]) if kind.startswith("d-planning-turn") else 0
        busy = kind in self.busy_once
        self.busy_once.discard(kind)
        if self.calibration_g0_timeouts.get(kind, 0) > 0 and not busy:
            # R6-2: the runtime's INCONCLUSIVE result for a G0 timeout.
            self.calibration_g0_timeouts[kind] -= 1
            return completed(argv, out=json.dumps({
                "kind": kind, "segment_status": "inconclusive", "g0_released": False, "g0_outcome": "timeout",
                "g0_wait_s": 1200.0, "g0_timeout_s": 1200.0,
                "cpu_busy_cores": [0.1] * 61, "cpu_busy_t_s": [float(i) for i in range(61)],
                "census": [{"pid": 1, "name": "launchd"}],
                "ac_powermode": {"value": self.mode, "source": "pmset -g custom", "observed_at": "episode_start"}}))
        payload = {"kind": kind, "fake_smc_journal": True,
                   "reference_c": 40.0, "g0_release_c": self.release_c.get(offset, 40.0 + offset),
                   "delta_slow_c": 0.5,
                   "energy_j": 100.0 + 3.0 * offset,
                   "cpu_busy_cores": [0.9] * 61 if busy else [0.1] * 61,
                   "cpu_busy_t_s": ([float(i) for i in range(30)] + [float(i) + 20 for i in range(30, 61)]
                                    if kind == self.journal_gap_kind else [float(i) for i in range(61)]),
                   "census": [{"pid": 1, "name": "launchd"}],
                   "slots": slots if kind == "step-d" else {}}
        if kind == "step-d" or kind.startswith("d-planning-turn"):
            # R7-2: every G0 wait, under the R1 G0 timeout.
            payload.update(g0_outcome="released", g0_wait_s=45.0, g0_timeout_s=1200.0)
        if kind == "idle":
            payload['sensor_roles'] = {'s_slow': 's_slow'}
            slope = 0.5 / 60 if self.unsettled_soak_once else 0.0
            self.unsettled_soak_once = False
            # Valid 1 Hz reads with their times; failed reads leave gaps in the
            # times (the runtime drops them), here inside the last 20 min.
            times = [float(t) for t in range(1800) if not 1000 <= t < 1000 + self.failed_soak_reads]
            payload["sensor_series_c"] = {"s_slow": [40.0 + slope * t + (0.05 if int(t) % 2 else -0.05)
                                                     for t in times]}
            payload["sensor_series_t_s"] = {"s_slow": times}
            payload["sensor_series_end_t_s"] = 1799.0
        if kind == "step-d":
            payload["e_D_j_per_token"] = 3.6
            payload["slot_detail"] = {"r_decode_tok_per_s": self.step_d_rate}
        if kind in ("step-30b", "step-d") or kind.startswith(("d-spam", "d-bank")):
            payload["battery_drain_pct_per_h"] = {"step-30b": 4.0, "step-d": 6.0}.get(kind, 7.0)
        if kind == "harvest":
            payload["charge_resume_soc_pct"] = self.charge_resume_soc
        if kind == "idle-until-soak":
            payload["recovery_curve"] = [[0, 55.0], [600, 45.0], [900, 41.0]]
            payload["released"] = out.name not in self.precool_timeout
        if kind in ("step-30b", "step-d"):
            # Keys as the kit's ready_inputs policy names them (TC0P die, TG0P heatsink).
            payload["thermometry"] = {"status": self.thermometry_status, "s_fast": "TC0P", "s_slow": "TG0P",
                                      "r0_sensors": {"s_fast": "TC0P", "s_slow": "TG0P"},
                                      "die_candidates": ["TC0P"], "heatsink_candidates": ["TG0P"],
                                      "sensor_pick_changed": False, "flags": [], "reasons": [],
                                      "alias_groups": [["TCMb", "TVD0"]],   # R7-13
                                      "classification_sha256": "c" * 64}
        if kind == "x-g" or kind.startswith(("d-spam", "d-bank")):
            payload.update(reference_source="r1_soak_reference",
                           gate_waits_s={"G0": [120.0], "G1": [40.0, 50.0, 60.0], "H": [30.0, 30.0, 30.0]},
                           # R6-1: W1's inter-member schedule (the kit configs' idle).
                           inter_member_idle_s=300.0,
                           g0_outcome="timeout" if out.name in self.g0_timeout else "released",
                           # R7-2: the G0 wait under the R1 G0 timeout.
                           g0_wait_s=1200.0 if out.name in self.g0_timeout else self.g0_waits.get(out.name, 120.0),
                           g0_timeout_s=1200.0)
        if kind.startswith("d-") and "planning" not in kind and kind != "d-4bit":
            payload.update(energy_j={"d-spam-benign-s1-a": 30000.0, "d-spam-benign-s1-b": 30036.0,
                                     "d-bank-benign-s1": 32000.0}[kind],
                           admitted_turns=3, x7=False, turn_cap_tokens=4096,
                           # R6-3: 12,600 tokens in 700 s = 18 tok/s (step-d: 20).
                           decode_tokens=self.gated_decode_tokens,
                           deadman={"T_dead_s": 1451.018, "phases_s": {
                               "G0": self.g0_waits.get(out.name, 120.0), "G1": 150.0, "H": 90.0, "decode": 700.0,
                               "prefill": 120.0, "tool": 6.0, "tail": self.tail}})
            if out.name in self.g0_timeout:
                # R6-1: a G0 timeout admits no turn and decodes nothing (R7-2: at 1,200 s).
                payload.update(admitted_turns=0, decode_tokens=0, gate_waits_s={"G0": [1200.0], "G1": [], "H": []},
                               g0_wait_s=1200.0, deadman={"T_dead_s": 1451.018, "phases_s": {
                                   "G0": 1200.0, "G1": 0.0, "H": 0.0, "decode": 0.0,
                                   "prefill": 0.0, "tool": 0.0, "tail": 0.0}})
        if kind == "g0-release-soak":
            payload["released"] = self.released
        if kind in ("step-30b", "d-4bit", "g0-release-soak") or kind.startswith("high-power-aba-"):
            # R7-2: every G0 wait is recorded; these kinds keep the 600 s cap.
            payload.update(g0_outcome="released" if kind != "g0-release-soak" or self.released else "timeout",
                           g0_wait_s=30.0 if kind != "g0-release-soak" or self.released else 600.0,
                           g0_timeout_s=600.0)
            if kind == "g0-release-soak":
                payload["g0"] = {"outcome": payload.pop("g0_outcome")}
        if kind in ("step-30b", "step-d", "x-g", "d-4bit") or kind.startswith(("d-", "high-power-aba-")):
            # Ruling 7: the episode-start AC powermode the member observed.
            payload["ac_powermode"] = {"value": self.mode, "source": "pmset -g custom", "observed_at": "episode_start"}
        if kind.startswith("high-power-aba-"):
            leg = kind.rsplit("-", 1)[-1]
            payload["g0_released"] = leg not in self.leg_g0_unreleased
            payload["t_decline_s"] = self.t_decline[leg] if payload["g0_released"] else None
        return completed(argv, out=json.dumps(payload))


PACIFIC = r1.ZoneInfo("America/Los_Angeles")
NOON_SAFE = r1.datetime(2026, 11, 7, 2, 0, tzinfo=PACIFIC)


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
            self.assertEqual(names, [row[0] for row in r1.phase_plan(True)] + ["harvest"])
            self.assertIn("D_4bit_optional", names)
            # R6-6: no cooldown_after_30b; the A-B-A legs follow the 30B step.
            self.assertEqual(names[2:6], ["step_30b", "high_power_A1", "high_power_B", "high_power_A2"])
            self.assertEqual([p["name"] for p in result["phases"]
                              if p["name"].startswith("planning_turn") and "." not in p["name"]],
                             ["planning_turn_R_plus_4C", "planning_turn_R_plus_2C", "planning_turn_R_plus_0C"])
            self.assertLess(names.index("planning_turn_R_plus_0C"), names.index("post_calibration_bracket"))
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
            self.assertEqual([p["powermode"] for p in result["phases"][3:6]], [0, 2, 0])
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
        # Round-4 LOWs: ruling 16 reads "A legs infinite, B finite" as not
        # adopted, and a JSON true is not 1 s of t_decline.
        self.assertEqual(adopt(None, 30, None),
                         {"verdict": "not_adopted", "reason": "A legs infinite, B finite"})
        for bad in ((True, 25, 20), (20, True, 20), (20, 25, False), (20, "25", 20)):
            with self.subTest(bad=bad), self.assertRaisesRegex(r1.Refusal, "positive or null"):
                adopt(*bad)

    def test_gated_d_runs_are_replay_pair_plus_bank_benign(self):
        kinds = [row[1] for row in r1.phase_plan(False) if row[0].endswith("_gated_held")
                 or row[0].endswith(("_held_a", "_held_b"))]
        # R7-1: the bank run first, then the replay pair.
        self.assertEqual(kinds, ["d-bank-benign-s1", "d-spam-benign-s1-a", "d-spam-benign-s1-b"])

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
        moments = [r1.datetime(2026, 11, 7, 11, 30, tzinfo=PACIFIC)]
        def now():
            return moments[-1]
        def sleep(seconds):
            sleeps.append(seconds)
            moments.append(moments[-1] + r1.timedelta(seconds=seconds))
        waited = r1.wait_outside_os_batch(1800, now=now, sleep=sleep)
        self.assertEqual(moments[-1].strftime("%H:%M"), "13:15")
        self.assertEqual(waited, sum(sleeps))
        self.assertEqual(r1.wait_outside_os_batch(600, now=lambda: r1.datetime(2026, 11, 7, 11, 30, tzinfo=PACIFIC),
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
        # Round-4 executing review HIGH-2: a replay run with an unreleased G0
        # has no turn and energy_j 0; |E_a - E_b| is then a whole episode, which
        # would make sigma_pair huge and U5 a false PASS.
        temperature.update(beta_T_j_per_c=1.0, abs_beta_T_90_j_per_c=2.5)
        empty = {r1.REPLAY_PAIR[0]: {"energy_j": 0, "admitted_turns": 0},
                 r1.REPLAY_PAIR[1]: {"energy_j": 9000.0, "admitted_turns": 12}}
        u5 = r1.u5_verdict(temperature, empty)
        self.assertEqual(u5["verdict"], "inconclusive")
        self.assertFalse(u5["sigma_pair_valid"])
        self.assertIn(r1.REPLAY_PAIR[0], u5["sigma_pair_invalid_reason"])
        both = {name: {"energy_j": 1000.0, "admitted_turns": 3} for name in r1.REPLAY_PAIR}
        self.assertTrue(r1.u5_verdict(temperature, both)["sigma_pair_valid"])
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
            # The ruling 20 volume census runs before every invocation; skip it here.
            calls = [c for c in world.calls if c[0] not in ("/sbin/mount", "/usr/sbin/diskutil")]
            for leg in ("high-power-aba-a1", "high-power-aba-b", "high-power-aba-a2"):
                index = next(i for i, c in enumerate(calls) if "--r1-kind" in c and leg in c)
                window = calls[index - 2:index]
                self.assertEqual(window[0][0], "WAIT", leg)
                self.assertIn("g0-release-soak", window[1], leg)
                # Round-3 LOW-1: the bound comes from the configured values (the
                # committed runtime config's step deadman, 1,580 s), not an
                # assumed 1,800 + 600 s. R5-5 runs the legs before step-d, so the
                # member intercept is the runtime's admissible maximum I_D (1,750 s).
                self.assertAlmostEqual(window[0][1], 65 + 600 + 1750 + 1.13544 * 1580 + 120)
            kinds = [c[c.index("--r1-kind") + 1] for c in world.calls if "--r1-kind" in c]
            self.assertLess(kinds.index("high-power-aba-a2"), kinds.index("step-d"))
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

    def test_step_d_without_an_admissible_budget_refuses_before_any_gated_run(self):
        # Lead ruling R5-4: a gated D run is never unbudgeted. step-d floors a
        # small budget to 0; the driver refuses right after step-d (Mac time),
        # before the cooldown, X-G and the gated runs.
        for b_d in (0, 512, 41984):
            with self.subTest(b_d=b_d), tempfile.TemporaryDirectory() as td:
                world = FakeWorld(b_d=b_d)
                with patch.object(r1, "_run", world):
                    self.assertEqual(r1.run(self.args(td)), 3)
                result = json.loads((Path(td) / "run/r1_result.json").read_text())
                self.assertIn("step-d.B_D", result["error"])
                kinds = [c[c.index("--r1-kind") + 1] for c in world.calls if "--r1-kind" in c]
                self.assertEqual(kinds[-1], "step-d")
                self.assertEqual(world.mode, 0)

    def test_step_d_with_a_null_slot_refuses_right_after_step_d(self):
        # Executing review round 4 LOW-9: a no-rise t63 (S2) is null; that
        # fails R1's thermometry bar at step-d, not after the night.
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(slot_changes={"S2": None})
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 3)
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            self.assertIn("slot S2 is not finite numeric evidence", result["error"])
            kinds = [c[c.index("--r1-kind") + 1] for c in world.calls if "--r1-kind" in c]
            self.assertEqual(kinds[-1], "step-d")

    def test_soak_sd_uses_the_last_1200_seconds_not_samples(self):
        # Fable cold pass round 4 LOW-2: dropped reads must not stretch the window.
        times = [float(t) for t in range(1800) if not 700 <= t < 800]
        values = [50.0 if t < 600 else 40.0 for t in times]
        out = r1.soak_detrended({"k": values}, {"k": times}, 1799.0)["k"]
        self.assertEqual(out["mean_c"], 40.0)          # the last 1,200 samples would reach t = 500 (50 C)
        self.assertEqual(out["window_reads"], 1100)
        sparse = [t for t in times if not 1000 <= t < 1300]
        with self.assertRaisesRegex(r1.Refusal, "valid reads in the last 1200 s"):
            r1.soak_detrended({"k": [40.0] * len(sparse)}, {"k": sparse}, 1799.0)
        with self.assertRaisesRegex(r1.Refusal, "sensor_series_t_s"):
            r1.soak_detrended({"k": values}, None, 1799.0)
        # Sol critique: reads that stop 600 s before the soak ends cannot pass
        # as the last 20 min (the window ends at the soak's end, not the last read).
        early = [float(t) for t in range(1200)]
        with self.assertRaisesRegex(r1.Refusal, "valid reads in the last 1200 s"):
            r1.soak_detrended({"k": [40.0] * 1200}, {"k": early}, 1799.0)
        with self.assertRaisesRegex(r1.Refusal, "sensor_series_end_t_s"):
            r1.soak_detrended({"k": values}, {"k": times}, None)
        with self.assertRaisesRegex(r1.Refusal, "spans"):
            r1.soak_detrended({"k": [40.0] * 1300}, {"k": [t / 2 for t in range(1300)]}, 649.5)

    def test_soak_with_failed_reads_end_to_end(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(r1, "_run", FakeWorld(failed_soak_reads=50)):
                self.assertEqual(r1.run(self.args(td)), 0)
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            soak = next(p for p in result["phases"] if p["name"] == "idle_soak")
            self.assertEqual(soak["soak_detrended"]["s_slow"]["window_reads"], 1150)

    def test_a_first_signal_during_teardown_still_writes_r1_result(self):
        # Fable cold pass round 4 LOW-4: after a normal completion, a first
        # signal inside the driver's finally (here during the last Automatic
        # restore) must not skip the restore record or r1_result.json.
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td / Path("a") if False else Path(td) / "a")), 0)
            restores = world.calls.count(r1.PowerModeGuard.AUTO)
            world = FakeWorld()
            seen = {"auto": 0}

            def runner(argv):
                argv = tuple(str(v) for v in argv)
                if argv == r1.PowerModeGuard.AUTO:
                    seen["auto"] += 1
                    if seen["auto"] == restores:          # the restore in ``finally``
                        os.kill(os.getpid(), signal.SIGTERM)
                return world(argv)
            previous = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
            with patch.object(r1, "_run", runner):
                rc = r1.run(self.args(Path(td) / "b"))
            self.assertEqual(rc, 0)
            self.assertEqual(world.mode, 0)
            result = json.loads((Path(td) / "b/run/r1_result.json").read_text())
            self.assertEqual(result["status"], "complete")
            # The signal neither interrupted the last restore nor became a teardown error.
            self.assertNotIn("teardown_errors", result)
            # Restore records: proof at entry, the context exit, and the one in ``finally``.
            self.assertEqual([r["point"] for r in result["powermode"]].count("restore_automatic"), 3)
            self.assertEqual({sig: signal.getsignal(sig) for sig in previous}, previous)

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

    def test_battery_drain_and_charge_resume_are_contract_fields_and_registered(self):
        # Council ruling 4(b) (executing review M-4): R1 reports the drain rate
        # under D and under the 30B and the SoC at which charging resumes.
        with tempfile.TemporaryDirectory() as td:
            with patch.object(r1, "_run", FakeWorld()):
                self.assertEqual(r1.run(self.args(td)), 0)
            battery = json.loads((Path(td) / "registration/r1_slots.json").read_text())["battery"]
            self.assertEqual(battery["drain_pct_per_h"]["30B"], 4.0)
            self.assertAlmostEqual(battery["drain_pct_per_h"]["D"], (6.0 + 7.0 * 3) / 4)
            self.assertEqual(battery["charge_resume_soc_pct"], 94)
        for kind, field in (("step-30b", "battery_drain_pct_per_h"), ("step-d", "battery_drain_pct_per_h"),
                            ("d-bank-benign-s1", "battery_drain_pct_per_h"), ("harvest", "charge_resume_soc_pct")):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as td:
                world = FakeWorld()

                def runner(argv, kind=kind, field=field):
                    result = world(argv)
                    if "--r1-kind" in argv and argv[argv.index("--r1-kind") + 1] == kind:
                        payload = json.loads(result.stdout)
                        del payload[field]
                        result = completed(argv, out=json.dumps(payload))
                    return result
                with patch.object(r1, "_run", runner):
                    self.assertEqual(r1.run(self.args(td)), 3)
                result = json.loads((Path(td) / "run/r1_result.json").read_text())
                self.assertIn(f"contract fields missing: {field}", result["error"])

    def test_first_signal_gives_the_runtime_a_term_grace_before_kill(self):
        # Fable cold pass MEDIUM-1: subprocess.run SIGKILLed the runtime the
        # instant the driver's handler raised, so a runtime that needs time on
        # TERM (close the SMC journal, stop powermetrics, write its terminal
        # custody record) never finished it.
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
            td = Path(td)
            script = td / "slow_runtime.py"
            script.write_text(
                "import os, signal, sys, time\n"
                "out = sys.argv[sys.argv.index('--output') + 1]\n"
                "os.makedirs(out)\n"
                "def term(signum, frame):\n"
                "    time.sleep(1.0)\n"
                "    open(os.path.join(out, 'terminal.json'), 'w').write('{\"status\": \"aborted\"}')\n"
                "    sys.exit(143)\n"
                "signal.signal(signal.SIGTERM, term)\n"
                "open(os.path.join(out, 'pid'), 'w').write(str(os.getpid()))\n"
                "time.sleep(60)\n")
            world, real_run = FakeWorld(), r1._run
            segment = td / "run" / "X_G_contrast"

            def runner(argv):
                if "--r1-kind" in argv and "x-g" in argv:
                    return real_run([sys.executable, str(script), *argv[1:]])
                return world(argv)

            def signal_when_started():
                deadline = time.monotonic() + 30
                while not (segment / "pid").exists() and time.monotonic() < deadline:
                    time.sleep(0.05)
                time.sleep(0.2)
                os.kill(os.getpid(), signal.SIGTERM)
            thread = threading.Thread(target=signal_when_started, daemon=True)
            thread.start()
            with patch.object(r1, "_run", runner):
                rc = r1.run(self.args(td, include_4bit=False))
            thread.join()
            self.assertEqual(rc, 4)
            self.assertEqual(world.mode, 0)
            self.assertTrue((segment / "terminal.json").exists(), "runtime was killed before its TERM teardown")
            pid = int((segment / "pid").read_text())
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)

    def test_runtime_that_ignores_term_is_killed_after_the_grace(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
            stubborn = subprocess.Popen([sys.executable, "-c",
                                         "import signal, time\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
                                         "print('ready', flush=True)\ntime.sleep(60)\n"],
                                        stdout=subprocess.PIPE, text=True)
            self.assertEqual(stubborn.stdout.readline().strip(), "ready")
            started = time.monotonic()
            r1._terminate(stubborn, grace_s=1.0)
            self.assertLess(time.monotonic() - started, 15)
            self.assertEqual(stubborn.returncode, -signal.SIGKILL)
        self.assertEqual(r1.RUNTIME_TERM_GRACE_S, 20.0)

    def test_runtime_argv_comes_from_the_inputs_list(self):
        repo = Path(__file__).resolve().parents[2]
        inputs = json.loads((repo / "configs/campaigns/align_v4/registration/inputs.json").read_text())
        entry = inputs["WP15"]["runtime_entrypoint"]
        self.assertIsInstance(entry, list)
        argv = r1.runtime_argv_from_inputs(repo / "configs/campaigns/align_v4/registration/inputs.json")
        self.assertEqual(argv[:3], [sys.executable, "-B", str(repo / entry[0])])
        self.assertEqual(argv[3:], entry[1:])
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "inputs.json"
            for bad in ("scripts/align_r1_runtime.py --config x", [], ["/bin/sh", "-c", "x"],
                        ["../outside.py"], ["scripts/missing_runtime.py"]):
                path.write_text(json.dumps({"WP15": {"runtime_entrypoint": bad}}))
                with self.subTest(bad=bad), self.assertRaises(r1.Refusal):
                    r1.runtime_argv_from_inputs(path)

    def test_zsh_chain_passes_the_inputs_entrypoint_unless_overridden(self):
        repo = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
            td = Path(td)
            (td / "bin").mkdir()
            sudo = td / "bin/sudo"
            sudo.write_text("#!/bin/zsh\n"
                            'if [[ "$1 $2" == "-n -l" ]]; then\n'
                            '  print "(root) NOPASSWD: /usr/bin/pmset -c powermode 0, /usr/bin/pmset -c powermode 2"\n'
                            "fi\nexit 0\n")
            shim = td / "py"
            shim.write_text(f'#!/bin/zsh\nprint -r -l -- "$@" > {td / "argv"}\n')
            for path in (sudo, shim):
                path.chmod(0o755)
            (td / "mroot").mkdir()
            env = dict(os.environ, PATH=f"{td / 'bin'}:{os.environ['PATH']}", PY=str(shim),
                       NIGHT_DIR=str(td / "night"), MEASUREMENT_ROOT=str(td / "mroot"))
            env.pop("ALIGN_R1_RUNTIME", None)
            chain = ["/bin/zsh", str(repo / "scripts/night_chains/align_r1_rehearsal.zsh")]
            proc = subprocess.run(chain, env=env, capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            argv = (td / "argv").read_text().splitlines()
            self.assertEqual(argv[argv.index("--runtime-entrypoint") + 1],
                             str(repo / "configs/campaigns/align_v4/registration/inputs.json"))
            self.assertNotIn("--runtime", argv)
            proc = subprocess.run(chain, env=dict(env, ALIGN_R1_RUNTIME="/opt/runtime"), capture_output=True,
                                  text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            argv = (td / "argv").read_text().splitlines()
            self.assertEqual(argv[argv.index("--runtime") + 1], "/opt/runtime")

    # --- Round-4 fixes ----------------------------------------------------

    def test_load_journal_must_cover_the_segment_wall_time(self):
        # Executing review MEDIUM-1: one sample over an 1,800 s soak was accepted.
        one = {"cpu_busy_cores": [3.9], "cpu_busy_t_s": [0.0], "census": [{"pid": 1}]}
        with self.assertRaisesRegex(r1.Refusal, "1 samples over 1800.0 s"):
            r1.os_load_verdict("idle_soak", one, wall_s=1800.0)
        full = {"cpu_busy_cores": [0.1] * 1616, "cpu_busy_t_s": [float(i) for i in range(1616)],
                "census": [{"pid": 1}]}
        self.assertFalse(r1.os_load_verdict("idle_soak", full, wall_s=1800.0)["redo"])  # 0.9*1800-5 = 1615
        with self.assertRaisesRegex(r1.Refusal, "one sample time per"):
            r1.os_load_verdict("idle_soak", {**full, "cpu_busy_t_s": [0.0]}, wall_s=10.0)
        with self.assertRaisesRegex(r1.Refusal, "nondecreasing"):
            r1.os_load_verdict("x", {"cpu_busy_cores": [0.1, 0.1], "cpu_busy_t_s": [1.0, 0.0],
                                     "census": [1]}, wall_s=1.0)

    def test_a_gap_in_the_load_journal_refuses_r1_and_restores_automatic(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(journal_gap_kind="step-30b")
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 3)
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            self.assertIn("21.0 s gap", result["error"])
            self.assertEqual(world.mode, 0)

    def test_l1_is_evaluated_on_the_r1_record_and_bounds_the_duty_share(self):
        # Executing review MEDIUM-2 probe P3: a 700 s tail; W1 would arm
        # L1 = (1800 - 101.5 - 700 - 10)/1.13544 = 870.6 s, not 1,451 s.
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(tail=700.0)
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 0)
            registration = json.loads((Path(td) / "registration/r1_slots.json").read_text())
            l1 = registration["l1"]
            self.assertAlmostEqual(l1["l1_T_dead_s"], (1800 - 101.5 - 700 - 10) / 1.13544)
            self.assertEqual(l1["effective_T_dead_s"], l1["l1_T_dead_s"])
            self.assertFalse(l1["armed_fits"])
            self.assertTrue(l1["member_fit_ok"])
            self.assertAlmostEqual(l1["member_fit_worst_armed_s"], 101.5 + 1.13544 * 1451.018 + 700 + 10)
            # G0 + G1 + H = 360 s: within 40 % of the armed 1,451 s, not of L1's 870.6 s.
            self.assertFalse(registration["duty_bar"]["pass"])
            self.assertAlmostEqual(registration["duty_bar"]["duty_T_dead_s"], l1["l1_T_dead_s"])
        with tempfile.TemporaryDirectory() as td:
            with patch.object(r1, "_run", FakeWorld()):
                self.assertEqual(r1.run(self.args(td)), 0)
            registration = json.loads((Path(td) / "registration/r1_slots.json").read_text())
            self.assertEqual(registration["l1"]["effective_T_dead_s"], 1451.018)
            self.assertTrue(registration["duty_bar"]["pass"])

    def test_external_volume_at_t0_refuses_before_any_powermode_or_runtime_work(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()
            world.mounted = True
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 3)
            self.assertFalse([c for c in world.calls if "--r1-kind" in c])
            self.assertNotIn(r1.PowerModeGuard.HIGH, world.calls)
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            self.assertIn("external_volume.t0", result["error"])
            self.assertIn("/Volumes/JW-EXT", result["error"])
            points = [row["point"] for row in result["external_volumes"]]
            self.assertEqual(points, ["t0", "terminal"])
            self.assertEqual(result["external_volumes"][0]["external"][0]["mount_point"], "/Volumes/JW-EXT")

    def test_external_volume_attached_mid_r1_refuses_at_the_next_segment(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(mount_after="step-30b")
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 3)
            kinds = [c[c.index("--r1-kind") + 1] for c in world.calls if "--r1-kind" in c]
            self.assertEqual(kinds[-1], "step-30b")
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            self.assertEqual(result["status"], "refused")
            # R6-6: the next segment is A1's release (no cooldown_after_30b).
            self.assertIn("external_volume.before:g0-release-soak:high_power_A1.g0_release0", result["error"])
            self.assertEqual(world.mode, 0)
            self.assertFalse((Path(td) / "registration/r1_slots.json").exists())

    def test_clean_r1_records_every_volume_census(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(r1, "_run", FakeWorld()):
                self.assertEqual(r1.run(self.args(td)), 0)
            registration = json.loads((Path(td) / "registration/r1_slots.json").read_text())
            points = [row["point"] for row in registration["external_volumes"]]
            self.assertEqual(points[0], "t0")
            self.assertEqual(points[-1], "before_registration")
            self.assertTrue(all(row["verdict"] == "PASS" for row in registration["external_volumes"]))
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            self.assertEqual(result["external_volumes"][-1]["point"], "terminal")

    def test_rerun_into_an_existing_output_is_a_refusal_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "run"
            out.mkdir()
            (out / "r1_result.json").write_text('{"status": "complete"}\n')
            world = FakeWorld()
            with patch.object(r1, "_run", world):
                self.assertEqual(r1.run(self.args(td)), 3)
            self.assertEqual(json.loads((out / "r1_result.json").read_text()), {"status": "complete"})
            self.assertFalse([c for c in world.calls if "--r1-kind" in c])
            self.assertEqual(world.mode, 0)
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "run").mkdir()  # a SIGKILLed run left no terminal record
            with patch.object(r1, "_run", FakeWorld()):
                self.assertEqual(r1.run(self.args(td)), 3)
            result = json.loads((Path(td) / "run/r1_result.json").read_text())
            self.assertIn("output directory already exists", result["error"])

    def test_batch_window_is_pacific_wall_time_across_a_dst_change(self):
        # Cold pass LOW 8. From 23:00 PST on 2027-03-13 (a fixed -08:00 offset,
        # as datetime.now().astimezone() gave), a 12 h segment ends at 12:00
        # PDT on 2027-03-14, inside that day's 11:45-13:15 window. The fixed
        # offset put the window at 12:45-14:15 PDT, so the segment started at
        # once and ran into the batch window.
        from datetime import timezone
        utc = timezone.utc
        moments = [r1.datetime(2027, 3, 13, 23, 0, tzinfo=timezone(r1.timedelta(hours=-8)))]

        def sleep(seconds):
            moments.append((moments[-1].astimezone(utc) + r1.timedelta(seconds=seconds)).astimezone(PACIFIC))
        waited = r1.wait_outside_os_batch(12 * 3600, now=lambda: moments[-1], sleep=sleep)
        self.assertGreater(waited, 0)
        self.assertEqual(moments[-1].astimezone(PACIFIC).strftime("%Y-%m-%d %H:%M %Z"), "2027-03-14 13:15 PDT")
        self.assertEqual(r1._now_local().tzinfo, PACIFIC)

    def test_driver_record_satisfies_the_kit_evidence_binding(self):
        # MEDIUM-3 end to end: the kit binds exactly what the driver writes.
        from scripts import align_v4_kit as kit
        from tests.align.test_v4_kit import ready_inputs
        for synthetic in (False, True):
            with self.subTest(synthetic=synthetic), tempfile.TemporaryDirectory() as td:
                # R7-2: 1(f) now carries G0_cap_W1 (>= 600 s), so the fake
                # decodes at 40 tok/s for the frozen B_D to fit T_dead.
                with patch.object(r1, "_run", FakeWorld(step_d_rate=40.0, gated_decode_tokens=28000)):
                    self.assertEqual(r1.run(self.args(td, synthetic=synthetic)), 0)
                slots = json.loads((Path(td) / "registration/r1_slots.json").read_text())
                inputs, _ = ready_inputs(101.5, slots["max_r1_tail_s"])
                # R5-4: the thermal policy is the one R1 measured; R7-2: W1's G0 cap is R1's slot.
                inputs["R1"]["thermal_policy"].update(chunk_tokens=slots["slots"]["N_chunk"],
                                                      delta_slow_c=slots["slots"]["S6"],
                                                      turn_cap_s=slots["slots"]["S7"],
                                                      g0_cap_s=slots["g0_cap_w1"]["value_s"])
                self.assertEqual(slots["g0_cap_w1"]["value_s"], 600)
                self.assertEqual(slots["budget_fit_inputs"]["turn_cap_tokens"], 4096)
                # R6-3: min(step-d 40 tok/s, the gated runs' 40 tok/s).
                self.assertEqual(slots["budget_fit_inputs"]["r_decode_tok_per_s"], 40.0)
                self.assertEqual(slots["budget_fit_inputs"]["r_decode_step_d_tok_per_s"], 40.0)
                # R6-5: the policy carries R1's classification digest.
                inputs["R1"]["thermal_policy"]["classification_sha256"] = \
                    slots["thermometry"]["D"]["classification_sha256"]
                if synthetic:
                    with self.assertRaisesRegex(ValueError, "source must be"):
                        kit.require_ready(inputs, slots)
                    kit.require_ready(inputs, slots, synthetic=True)
                else:
                    kit.require_ready(inputs, slots)

    def test_plan_pins_durations_and_gated_held_members(self):
        rows = r1.phase_plan(False)
        self.assertEqual(rows[0], ("pre_calibration_bracket", "calibration-pre", None, "light"))
        self.assertEqual(rows[1], ("idle_soak", "idle", 1800, "light"))
        self.assertEqual(rows[-1], ("post_calibration_bracket", "calibration-post", None, "light"))
        # R6-6: cooldown_after_30b is gone; ruling 1(c)'s post-D cooldown stays.
        self.assertEqual([row[2] for row in rows if row[0].startswith("cooldown")], [1500])
        self.assertNotIn("cooldown_after_30b", [row[0] for row in rows])
        self.assertIn(("step_D_prefill_10k_decode_4096", "step-d", None, "heavy"), rows)
        self.assertIn(("D_spam_benign_s1_gated_held_a", "d-spam-benign-s1-a", None, "heavy"), rows)
        self.assertIn(("D_spam_benign_s1_gated_held_b", "d-spam-benign-s1-b", None, "heavy"), rows)
        self.assertIn(("D_bank_benign_s1_gated_held", "d-bank-benign-s1", None, "heavy"), rows)


class Round5RulingTests(unittest.TestCase):
    """LEAD-RULINGS-2 R5-1, R5-2, R5-3, R5-5 and R5-7 in the driver."""

    def setUp(self):
        clock = patch.object(r1, "_now_local", lambda: NOON_SAFE)
        clock.start()
        self.addCleanup(clock.stop)

    def run_world(self, td, world, expected=0, **changes):
        args = R1Tests.args(self, td, **changes)
        with patch.object(r1, "_run", world):
            self.assertEqual(r1.run(args), expected)
        result = json.loads((Path(td) / "run/r1_result.json").read_text())
        path = Path(td) / "registration/r1_slots.json"
        return result, (json.loads(path.read_text()) if path.exists() else None)

    def test_step_d_and_later_d_measurements_run_under_the_adopted_series_mode(self):
        # R5-5 (protocol v4 :243-251): the slots come from the D step run under
        # the ADOPTED mode, so the A-B-A decision precedes step-d.
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(t_decline={"a1": 20.0, "b": 30.0, "a2": 21.0})
            result, registration = self.run_world(td, world)
            self.assertEqual(registration["high_power"]["verdict"], "adopt")
            modes = {name: mode for _, name, mode in world.invocations}
            kinds = [kind for kind, _, _ in world.invocations]
            self.assertLess(kinds.index("high-power-aba-a2"), kinds.index("step-d"))
            for name in ("step_D_prefill_10k_decode_4096", "X_G_contrast", "D_bank_benign_s1_gated_held",
                         "planning_turn_R_plus_0C", "D_4bit_optional"):
                self.assertEqual(modes[name], 2, name)
            self.assertEqual(modes["step_30b"], 0)
            self.assertEqual(modes["post_calibration_bracket"], 0)
            self.assertEqual(registration["slots_ac_powermode"], 2)
            step = [p for p in result["phases"] if p["name"] == "step_D_prefill_10k_decode_4096"][0]
            self.assertEqual(step["powermode"], 2)
            self.assertEqual(world.mode, 0)
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()
            _, registration = self.run_world(td, world)
            self.assertEqual(registration["high_power"]["verdict"], "not_adopted")
            self.assertEqual({mode for kind, _, mode in world.invocations if kind == "step-d"}, {0})

    def test_a_member_that_ran_outside_the_series_mode_refuses(self):
        # An unobserved mode (both episode-start pmset reads failed) is not
        # evidence either (Sol critique of round 5).
        for kind, value, expected in (("step-d", 0, "series mode is 2"), ("step-d", None, "series mode is 2"),
                                      ("d-planning-turn-r-plus-0c", None, "series mode is 2"),
                                      ("high-power-aba-b", None, "series mode is 2")):
            with self.subTest(kind=kind, value=value), tempfile.TemporaryDirectory() as td:
                world = FakeWorld(t_decline={"a1": 20.0, "b": 30.0, "a2": 21.0})

                def runner(argv):
                    result = world(argv)
                    if "--r1-kind" in argv and argv[argv.index("--r1-kind") + 1] == kind:
                        payload = json.loads(result.stdout)
                        payload["ac_powermode"] = {"value": value, "source": "pmset", "observed_at": "episode_start"}
                        result = completed(argv, out=json.dumps(payload))
                    return result
                result, registration = self.run_world(td, runner, expected=3)
                self.assertIsNone(registration)
                self.assertIn(expected, result["error"])
                self.assertEqual(world.mode, 0)

    def test_batch_window_admission_uses_each_segment_s_full_bound(self):
        # Sol critique of round 5: the steps now run 600 s past the member and
        # the designed states have a 900 s preheat outside the deadman.
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()
            waits = []

            def wait(expected_s, **_):
                waits.append((world.invocations[-1][0] if world.invocations else None, expected_s))
                return 0.0
            with patch.object(r1, "wait_outside_os_batch", wait):
                self.run_world(td, world)
            bounds = [w for _, w in waits]
            # Round-5 executing review: R5-2 put the G0 and the steps' 300 s
            # quiet outside the deadman, so they join the bound. R7-2: step-d
            # and the designed states arm the 1,200 s R1 G0 timeout.
            self.assertEqual(bounds.count(3300), 1)   # 30B step: 1,800 + 600 G0 + 300 quiet + 600 recovery
            # R8-4: the re-armed member 1,750 + 1.13544 x 1,580 + 120, then D
            # step + 1,200 + 300 + 600; states + 900 + 1,200.
            self.assertEqual(sum(1 for b in bounds if abs(b - 5763.9952) < 1e-6), 1 + 3)
        table = r1.segment_bounds(r1.runtime_g0_timeout_s(None), r1.runtime_step_deadman_s(None))
        self.assertEqual(table["step-30b"], 3300)
        self.assertAlmostEqual(table["step-d"], 5763.9952)
        self.assertAlmostEqual(table["d-planning-turn-r-plus-4c"], 5763.9952)
        # Each bound covers the runtime's own caps around the re-armed deadman.
        from joulewise.align.apple import r1_runtime as rt
        from joulewise.align.apple import thermal_gates
        deadman = rt.DEADMAN_FACTOR * r1.runtime_step_deadman_s(None)
        g0_cap = rt.g0_timeout_s(json.loads(r1.runtime_config_path(None).read_text()))
        self.assertGreaterEqual(table["step-d"], g0_cap + rt.STEP_QUIET_S + deadman + rt.RECOVERY_CAP_S)
        self.assertGreaterEqual(table["d-planning-turn-r-plus-0c"], rt.PREHEAT_CAP_S + g0_cap + deadman)
        self.assertGreaterEqual(table["step-30b"], thermal_gates.G0_CAP_DEFAULT_S + rt.STEP_QUIET_S + deadman
                                + rt.RECOVERY_CAP_S)

    def test_full_inventory_thermometry_is_registered_and_a_null_pick_fails_the_bar(self):
        with tempfile.TemporaryDirectory() as td:
            _, registration = self.run_world(td, FakeWorld())
            self.assertEqual(registration["thermometry"]["bar"], "pass")
            self.assertEqual(registration["thermometry"]["D"]["classification_sha256"], "c" * 64)
            self.assertIn("30B_record_only", registration["thermometry"])
        with tempfile.TemporaryDirectory() as td:
            _, registration = self.run_world(td, FakeWorld(thermometry_status="fail"))
            self.assertEqual(registration["thermometry"]["bar"], "fail")
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()

            def runner(argv):
                result = world(argv)
                if "--r1-kind" in argv and "step-d" in argv:
                    payload = json.loads(result.stdout)
                    del payload["thermometry"]
                    result = completed(argv, out=json.dumps(payload))
                return result
            result, registration = self.run_world(td, runner, expected=3)
            self.assertIn("thermometry", result["error"])

    def test_designed_start_states_run_warmest_first(self):
        # R5-2: R + 4 C runs first, then R + 2 C, then R + 0 C. R6-2: each
        # starts from the G0 band of R (the post-D cooldown, then precools).
        names = [row[0] for row in r1.phase_plan(False)]
        planning = [n for n in names if n.startswith("planning_turn") and "." not in n]
        self.assertEqual(planning, ["planning_turn_R_plus_4C", "planning_turn_R_plus_2C", "planning_turn_R_plus_0C"])
        self.assertEqual(names.index(planning[0]), names.index("cooldown_after_D") + 1)
        with tempfile.TemporaryDirectory() as td:
            _, registration = self.run_world(td, FakeWorld())
            # beta_T still fits on the offsets, whatever the run order.
            self.assertAlmostEqual(registration["planning_temperature"]["beta_T_j_per_c"], 3.0)
            self.assertEqual(registration["planning_temperature"]["run_order_offsets_c"], [4.0, 2.0, 0.0])

    def test_each_gated_d_run_follows_a_d_turn_with_w1_s_schedule_and_consumes_the_soak(self):
        # R6-1 (supersedes R5-1's cool-to-band): nothing but the member's own
        # W1 idle stands between the preceding D turn and each gated run or X-G.
        rows = r1.phase_plan(False)
        names = [row[0] for row in rows]
        d_turns = ("step-d", "d-spam-benign-s1-a", "d-spam-benign-s1-b", "d-bank-benign-s1",
                   *(f"d-planning-turn-r-plus-{o}c" for o in (0, 2, 4)))
        for name in [n for n, _ in r1.GATED_D_RUNS] + ["X_G_contrast"]:
            before = rows[names.index(name) - 1]
            self.assertIn(before[1], d_turns, name)
            self.assertNotIn(name + ".precool", names)
        self.assertEqual(names[names.index("X_G_contrast") - 1], "D_spam_benign_s1_gated_held_b")   # W1's D -> X
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()
            result, registration = self.run_world(td, world)
            soak = str((Path(td) / "run/soak_reference.json").resolve())
            for call in world.calls:
                if "--r1-kind" in call and call[call.index("--r1-kind") + 1].startswith(("d-spam", "d-bank", "x-g")):
                    self.assertEqual(call[call.index("--soak-reference") + 1], soak)
            # Run order on the host: no segment between a D turn and the next gated member.
            ran = [name for _, name, _ in world.invocations]
            for name in [n for n, _ in r1.GATED_D_RUNS] + ["X_G_contrast"]:
                self.assertNotIn(ran[ran.index(name) - 1].rsplit(".", 1)[-1], ("precool", "precool_retry"))
            self.assertEqual(registration["duty_bar"]["verdict"], "pass")
            self.assertEqual(registration["duty_bar"]["inconclusive_runs"], [])
            schedule = registration["duty_bar"]["schedule"]
            self.assertEqual(schedule["inter_member_idle_s"], {"D": 300.0, "X-G": 300.0})
            self.assertEqual(schedule["authority"], "LEAD-RULINGS-2 R6-1")
            self.assertEqual(registration["x_g"]["status"], "measured")
            self.assertEqual(registration["x_g"]["follows_d_turn"], "D_spam_benign_s1_gated_held_b")

    def test_a_gated_g0_timeout_makes_that_run_inconclusive_not_a_refusal(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(g0_timeout={"D_spam_benign_s1_gated_held_a"})
            result, registration = self.run_world(td, world)
            self.assertEqual(result["status"], "complete")
            rows = {row["run"]: row for row in registration["deadman_budget"]}
            # Without R6-1 this row read FAIL (no admitted turn).
            self.assertEqual(rows["D_spam_benign_s1_gated_held_a"]["duty_bar"]["verdict"], "inconclusive")
            self.assertIn("G0 did not release", rows["D_spam_benign_s1_gated_held_a"]["inconclusive_reason"])
            # Run b (R7-1: after a) then followed a member that dispatched no
            # D turn: it did not test W1's D-after-D G0 either.
            self.assertIsNone(rows["D_spam_benign_s1_gated_held_b"]["follows_d_turn"])
            self.assertEqual(rows["D_spam_benign_s1_gated_held_b"]["duty_bar"]["verdict"], "inconclusive")
            self.assertEqual(rows["D_bank_benign_s1_gated_held"]["follows_d_turn"], "planning_turn_R_plus_0C")
            self.assertEqual(rows["D_bank_benign_s1_gated_held"]["duty_bar"]["verdict"], "pass")
            self.assertEqual(registration["duty_bar"]["verdict"], "inconclusive")
            self.assertFalse(registration["duty_bar"]["pass"])
            self.assertEqual(registration["duty_bar"]["inconclusive_runs"],
                             ["D_spam_benign_s1_gated_held_a", "D_spam_benign_s1_gated_held_b"])
            # The replay pair cannot decide U5 either.
            self.assertEqual(registration["u5"]["verdict"], "inconclusive")
            self.assertFalse(registration["u5"]["sigma_pair_valid"])
            # The kit stays conservative (R7-2): the timed-out run's G0 counts
            # at the full 1,200 s R1 timeout in G0_cap_W1, ruling 1(f)'s G0
            # term, so W1 is refused.
            self.assertEqual(registration["g0_cap_w1"]["value_s"], 1200)
            self.assertEqual(registration["g0_cap_w1"]["censored"], ["D_spam_benign_s1_gated_held_a"])
            from scripts import align_v4_kit as kit
            from tests.align.test_v4_kit import ready_inputs
            inputs, _ = ready_inputs(101.5, registration["max_r1_tail_s"])
            inputs["R1"]["thermal_policy"].update(chunk_tokens=registration["slots"]["N_chunk"],
                                                  delta_slow_c=registration["slots"]["S6"],
                                                  turn_cap_s=registration["slots"]["S7"],
                                                  classification_sha256="c" * 64, g0_cap_s=1200)
            with self.assertRaisesRegex(ValueError, r"ruling 1\(f\).*G0_s 1200\.0"):
                kit.check_r1_evidence(inputs, registration, synthetic=True)
        with tempfile.TemporaryDirectory() as td:
            _, registration = self.run_world(td, FakeWorld(g0_timeout={"X_G_contrast"}))
            self.assertEqual(registration["x_g"]["status"], "inconclusive")
            self.assertEqual(registration["x_g"]["g0_outcome"], "timeout")

    def test_a_gated_run_without_the_soak_reference_refuses(self):
        for field, value in (("reference_source", "self_capture"), ("reference_c", 47.5)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as td:
                world = FakeWorld()

                def runner(argv):
                    result = world(argv)
                    if "--r1-kind" in argv and "d-spam-benign-s1-a" in argv:
                        payload = json.loads(result.stdout)
                        payload[field] = value
                        result = completed(argv, out=json.dumps(payload))
                    return result
                result, registration = self.run_world(td, runner, expected=3)
                self.assertIsNone(registration)
                self.assertIn("D_spam_benign_s1_gated_held_a", result["error"])

    def test_an_aba_leg_whose_own_g0_does_not_release_is_inconclusive_and_r1_continues(self):
        # R5-3 (exec MEDIUM-1): ruling 16's INCONCLUSIVE path, not a night refusal.
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(t_decline={"a1": 20.0, "b": 30.0, "a2": 21.0}, leg_g0_unreleased={"b"})
            result, registration = self.run_world(td, world)
            self.assertEqual(result["status"], "complete")
            high = registration["high_power"]
            self.assertEqual(high["verdict"], "inconclusive")
            self.assertEqual(high["leg_g0_released"], {"A1": True, "B": False, "A2": True})
            self.assertIsNone(high["t_decline_s"]["B"])     # not read as "no decline"
            self.assertEqual(high["rule_outcome"]["verdict"], "not_evaluated")
            self.assertEqual(registration["ac_powermode"], 0)
            self.assertIn("planning_turn_R_plus_0C", [p["name"] for p in result["phases"]])

    def test_aba_leg_must_report_its_own_g0_outcome(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()

            def runner(argv):
                result = world(argv)
                if "--r1-kind" in argv and "high-power-aba-a1" in argv:
                    payload = json.loads(result.stdout)
                    del payload["g0_released"]
                    result = completed(argv, out=json.dumps(payload))
                return result
            result, _ = self.run_world(td, runner, expected=3)
            self.assertIn("g0_released", result["error"])

    def test_s6_stays_delta_slow_with_a_todo_tied_to_the_gated_g1_median(self):
        # R5-7: S6 = delta_slow until the FD 2.6 tuning.
        with tempfile.TemporaryDirectory() as td:
            _, registration = self.run_world(td, FakeWorld())
            s6 = registration["s6_tuning"]
            self.assertEqual(s6["status"], "TODO")
            self.assertEqual(s6["S6_c"], registration["slots"]["S6"])
            self.assertEqual(s6["G1_median_s"], 50.0)    # three runs x [40, 50, 60]
            self.assertEqual(s6["H_median_s"], 30.0)
            self.assertEqual(s6["G1_waits"], 9)



class Round6RulingTests(unittest.TestCase):
    """LEAD-RULINGS-2 R6-1, R6-2, R6-3 and R6-6 in the driver."""

    setUp = Round5RulingTests.setUp
    run_world = Round5RulingTests.run_world

    def test_w1_schedule_comes_from_the_w1_plan_and_is_checked_before_any_work(self):
        # R6-1: the value is W1's (night_plan.template.json member configs), not hard-coded.
        self.assertEqual(r1.w1_inter_member_idle_s(), {"D": 300.0, "X-G": 300.0})
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()
            with patch.object(r1, "w1_inter_member_idle_s", lambda root=r1.ROOT: {"D": 450.0, "X-G": 300.0}):
                result, registration = self.run_world(td, world, expected=3)
            self.assertIsNone(registration)
            self.assertIn("R6-1", result["error"])
            self.assertFalse([c for c in world.calls if "--r1-kind" in c])
            self.assertNotIn(r1.PowerModeGuard.HIGH, world.calls)

    def test_a_gated_member_that_idled_another_schedule_refuses(self):
        for kind in ("d-bank-benign-s1", "x-g"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as td:
                world = FakeWorld()

                def runner(argv):
                    result = world(argv)
                    if "--r1-kind" in argv and argv[argv.index("--r1-kind") + 1] == kind:
                        payload = json.loads(result.stdout)
                        payload["inter_member_idle_s"] = 0.0
                        result = completed(argv, out=json.dumps(payload))
                    return result
                result, registration = self.run_world(td, runner, expected=3)
                self.assertIsNone(registration)
                self.assertIn("W1's", result["error"])
                self.assertEqual(world.mode, 0)

    def test_step_d_and_each_later_designed_state_get_a_bounded_precool_from_config(self):
        rows = r1.phase_plan(False, precool_cap_s=777.0)
        names = [row[0] for row in rows]
        for name in (r1.STEP_D_NAME, "planning_turn_R_plus_2C", "planning_turn_R_plus_0C"):
            self.assertEqual(rows[names.index(name) - 1], (name + ".precool", "idle-until-soak", 777.0, "light"))
        # The first designed state follows ruling 1(c)'s post-D cooldown (same band, recorded curve).
        self.assertEqual(names[names.index("planning_turn_R_plus_4C") - 1], "cooldown_after_D")
        self.assertEqual(r1.runtime_precool_cap_s(None), 1500)
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(precool_timeout={"planning_turn_R_plus_2C.precool"})
            with patch.object(r1, "runtime_precool_cap_s", lambda argv: 777.0):
                result, registration = self.run_world(td, world)
            durations = {c[c.index("--output") + 1].rsplit("/", 1)[-1]: c[c.index("--duration-s") + 1]
                         for c in world.calls if "--duration-s" in c}
            self.assertEqual(durations[r1.STEP_D_NAME + ".precool"], "777.0")
            self.assertEqual(durations["planning_turn_R_plus_0C.precool"], "777.0")
            # A precool that did not reach the band is recorded, never a refusal.
            self.assertIs(registration["calibration_precools"]["planning_turn_R_plus_2C.precool"], False)
            self.assertEqual(result["status"], "complete")

    def test_a_step_d_g0_timeout_is_retried_once_after_another_precool(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(calibration_g0_timeouts={"step-d": 1})
            result, registration = self.run_world(td, world)
            self.assertEqual(result["status"], "complete")
            ran = [name for _, name, _ in world.invocations]
            i = ran.index(r1.STEP_D_NAME)
            self.assertEqual(ran[i - 1:i + 3], [r1.STEP_D_NAME + ".precool", r1.STEP_D_NAME,
                                                 r1.STEP_D_NAME + ".precool_retry", r1.STEP_D_NAME])
            run = Path(td) / "run"
            self.assertTrue((run / (r1.STEP_D_NAME + ".g0_timeout1") / "attempt.txt").exists())
            self.assertEqual((run / r1.STEP_D_NAME / "attempt.txt").read_text(), "step-d 2\n")
            self.assertEqual(registration["inconclusive_segments"], {})
            self.assertEqual(set(registration["slots"]), set(r1.SLOT_NAMES))
            step = [p for p in result["phases"] if p["name"] == r1.STEP_D_NAME]
            self.assertEqual([p.get("segment_status") for p in step], ["inconclusive", None])

    def test_a_twice_timed_out_step_d_is_inconclusive_and_the_kit_refuses_w1(self):
        from scripts import align_v4_kit as kit
        from tests.align.test_v4_kit import ready_inputs
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(calibration_g0_timeouts={"step-d": 2})
            result, registration = self.run_world(td, world)
            # Not a night refusal: the rest of R1 ran and r1_slots is written.
            self.assertEqual(result["status"], "complete")
            self.assertIn(r1.STEP_D_NAME, registration["inconclusive_segments"])
            ran = [name for _, name, _ in world.invocations]
            for name in [n for n, _ in r1.GATED_D_RUNS] + ["X_G_contrast"]:
                self.assertNotIn(name, ran)        # unbudgeted without step-d (R5-4)
                self.assertIn(name, registration["skipped_segments"])
            self.assertIn("planning_turn_R_plus_0C", ran)
            self.assertIsNone(registration["slots"])
            self.assertEqual(registration["thermometry"]["bar"], "inconclusive")
            self.assertEqual(registration["u5"]["verdict"], "inconclusive")
            self.assertEqual(registration["x_g"]["status"], "not_run")
            self.assertEqual(world.mode, 0)
            inputs, _ = ready_inputs()
            with self.assertRaises(ValueError):
                kit.check_r1_evidence(inputs, registration, synthetic=True)

    def test_a_twice_timed_out_designed_state_is_inconclusive_and_u5_too(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(calibration_g0_timeouts={"d-planning-turn-r-plus-0c": 2})
            result, registration = self.run_world(td, world)
            self.assertEqual(result["status"], "complete")
            self.assertEqual(list(registration["inconclusive_segments"]), ["planning_turn_R_plus_0C"])
            self.assertEqual(registration["planning_temperature"]["status"], "inconclusive")
            self.assertEqual(registration["u5"]["verdict"], "inconclusive")
            # Fail closed at the kit (Sol critique of round 6).
            from scripts import align_v4_kit as kit
            from tests.align.test_v4_kit import ready_inputs
            inputs, _ = ready_inputs(101.5, registration["max_r1_tail_s"])
            with self.assertRaisesRegex(ValueError, r"INCONCLUSIVE \(R6-2\): planning_turn_R_plus_0C"):
                kit.check_r1_evidence(inputs, registration, synthetic=True)
            # R6-1: the first gated run (R7-1: D_bank) then followed no D turn
            # (R + 0 C dispatched none), so it is INCONCLUSIVE; the later ones follow it.
            rows = {row["run"]: row for row in registration["deadman_budget"]}
            self.assertIsNone(rows["D_bank_benign_s1_gated_held"]["follows_d_turn"])
            self.assertEqual(rows["D_bank_benign_s1_gated_held"]["duty_bar"]["verdict"], "inconclusive")
            self.assertEqual(rows["D_spam_benign_s1_gated_held_a"]["duty_bar"]["verdict"], "pass")
            self.assertEqual(rows["D_spam_benign_s1_gated_held_b"]["duty_bar"]["verdict"], "pass")
            self.assertEqual(registration["duty_bar"]["verdict"], "inconclusive")
        with tempfile.TemporaryDirectory() as td:
            # Once only: the retry measures it and beta_T is fitted as usual.
            _, registration = self.run_world(td, FakeWorld(calibration_g0_timeouts={"d-planning-turn-r-plus-2c": 1}))
            self.assertAlmostEqual(registration["planning_temperature"]["beta_T_j_per_c"], 3.0)

    def test_an_inconclusive_result_must_say_its_g0_did_not_release(self):
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld(calibration_g0_timeouts={"step-d": 1})

            def runner(argv):
                result = world(argv)
                payload = json.loads(result.stdout) if result.stdout.startswith("{") else None
                if payload and payload.get("segment_status") == "inconclusive":
                    payload["g0_released"] = True
                    result = completed(argv, out=json.dumps(payload))
                return result
            result, _ = self.run_world(td, runner, expected=3)
            self.assertIn("g0_released false", result["error"])

    def test_ruling_1f_decode_rate_is_the_minimum_over_step_d_and_the_gated_runs(self):
        with tempfile.TemporaryDirectory() as td:
            _, registration = self.run_world(td, FakeWorld(gated_decode_tokens=7000))   # 10 tok/s
            fit = registration["budget_fit_inputs"]
            self.assertEqual(fit["r_decode_step_d_tok_per_s"], 20.0)
            self.assertEqual(fit["r_decode_gated_tok_per_s"],
                             {name: 10.0 for name, _ in r1.GATED_D_RUNS})
            self.assertEqual(fit["r_decode_tok_per_s"], 10.0)
            rows = {row["run"]: row for row in registration["deadman_budget"]}
            self.assertEqual(rows["D_bank_benign_s1_gated_held"]["decode_tokens"], 7000)
        with tempfile.TemporaryDirectory() as td:
            # A run that decoded nothing (G0 timeout) has no rate; step-d's is kept.
            _, registration = self.run_world(td, FakeWorld(gated_decode_tokens=28000,
                                                           g0_timeout={"D_bank_benign_s1_gated_held"}))
            fit = registration["budget_fit_inputs"]
            self.assertIsNone(fit["r_decode_gated_tok_per_s"]["D_bank_benign_s1_gated_held"])
            self.assertEqual(fit["r_decode_tok_per_s"], 20.0)
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()

            def runner(argv):
                result = world(argv)
                if "--r1-kind" in argv and "d-spam-benign-s1-a" in argv:
                    payload = json.loads(result.stdout)
                    payload["deadman"]["phases_s"]["decode"] = 0.0
                    result = completed(argv, out=json.dumps(payload))
                return result
            result, _ = self.run_world(td, runner, expected=3)
            self.assertIn("decode tokens in 0.0 s", result["error"])

    def test_changed_pick_s7_records_the_accepted_quiet_window_reference(self):
        # R6-4: the lead ACCEPTED the quiet-window median as R for the R1 picks.
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()

            def runner(argv):
                result = world(argv)
                if "--r1-kind" in argv and argv[argv.index("--r1-kind") + 1] == "step-d":
                    payload = json.loads(result.stdout)
                    payload["thermometry"].update(sensor_pick_changed=True, s7_for_r1_picks={
                        "keys": {"s_fast": "TC1P", "s_slow": "TG1P"}, "S7": 60.0,
                        "band_c": {"s_fast": 1.0, "s_slow": 1.25}})
                    result = completed(argv, out=json.dumps(payload))
                return result
            _, registration = self.run_world(td, runner)
            picks = registration["thermometry"]["D"]["s7_for_r1_picks"]
            self.assertEqual(picks["S7"], 60.0)
            self.assertEqual(picks["reference_rule_status"], "ACCEPTED")
            self.assertIn("quiet window", picks["reference_rule"])

    def test_a_released_g0_that_decoded_nothing_is_not_a_d_turn_predecessor(self):
        # Sol critique of round 6: G0 released, then no D work (zero decode tokens).
        with tempfile.TemporaryDirectory() as td:
            world = FakeWorld()

            def runner(argv):
                result = world(argv)
                # R7-1: D_spam b is the D member before X-G.
                if "--r1-kind" in argv and argv[argv.index("--r1-kind") + 1] == "d-spam-benign-s1-b":
                    payload = json.loads(result.stdout)
                    payload.update(admitted_turns=0, decode_tokens=0)
                    payload["deadman"]["phases_s"].update(decode=0.0, prefill=0.0, tool=0.0)
                    result = completed(argv, out=json.dumps(payload))
                return result
            _, registration = self.run_world(td, runner)
            self.assertIsNone(registration["x_g"]["follows_d_turn"])
            self.assertEqual(registration["x_g"]["status"], "inconclusive")

    def test_cooldown_after_30b_is_dropped_and_nothing_reads_it(self):
        # R6-6: step-30b's own 600 s recovery observation is the idle.
        names = [row[0] for row in r1.phase_plan(True)]
        self.assertNotIn("cooldown_after_30b", names)
        self.assertEqual(names[names.index("step_30b") + 1], "high_power_A1")
        self.assertEqual(r1.ABA_LEG_I_D_BOUND_S, 1750)    # the accepted A-B-A batch-window bound


if __name__ == "__main__":
    unittest.main()
