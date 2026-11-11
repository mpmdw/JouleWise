"""Synthetic-journal tests for scripts/align_r1_thermal_replay.py (RL-59 item 4)."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import math
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("align_r1_thermal_replay",
                                              ROOT / "scripts/align_r1_thermal_replay.py")
replay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(replay)

NS = replay.NS
T0 = 5_000 * NS
WALL_OFFSET = 1_794_000_000 * NS
FAST, SLOW = "TV0h", "Tf08"
SENSORS = {"s_fast": FAST, "s_slow": SLOW, "fan_keys": ["F0Ac"], "r0_sha256": "0" * 64}


def stamp(mono):
    return {"monotonic_ns": mono, "monotonic_raw_ns": mono, "wall_ns": mono + WALL_OFFSET}


def journal_lines(slow_at, *, n=400, fast=34.0, status_at=None, skip=(), g0=None):
    """1 Hz readings; slow_at(i) gives S_slow at second i. Every row also carries
    decoy energy/power/token fields that the replay must never keep."""
    lines = [{"schema": replay.JOURNAL_SCHEMA, "module": "temperature", "kind": "session_start",
              "seq": 0, "started": stamp(T0), "finished": stamp(T0),
              "values": {"thermal": SENSORS}, "raw": [], "error": None}]
    for i in range(n):
        if i in skip:
            continue
        t = T0 + i * NS + 1000
        status = {"os_level": 0, "pm_state": "Nominal", "pm_observed_ns": t + 2_500_000,
                  "monotonic_ns": t + 3_000_000}
        if status_at is not None:
            status.update(status_at(i))
        lines.append({"schema": replay.JOURNAL_SCHEMA, "module": "temperature", "kind": "reading",
                      "seq": i + 1, "started": stamp(t), "finished": stamp(t + 2_000_000),
                      "values": {"sensors": {FAST: fast, SLOW: slow_at(i), "F0Ac": 0.0},
                                 "errors": {}, "status": status, "source": "smc",
                                 "energy_j": 123.0, "gpu_power_w": 9.9, "tokens": 77},
                      "raw": [], "error": None})
    if g0 is not None:
        lines.append({"schema": replay.JOURNAL_SCHEMA, "module": "temperature",
                      "kind": "align_thermal_gate", "seq": n + 2, "started": stamp(T0), "finished": stamp(T0),
                      "values": {"state": "end", "gate": g0}, "raw": [], "error": None})
    return lines


def write_journal(directory, name, lines):
    path = Path(directory) / name / "outputs" / "align_thermal.jsonl"
    path.parent.mkdir(parents=True)
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in lines))
    return path


def session_from(lines):
    temps = [FAST, SLOW]
    projected = [p for p in (replay.project_line(r, temps) for r in lines) if p is not None]
    rows = replay.sample_rows([p for p in projected if p["kind"] == "reading"])
    return replay.Session(rows, FAST, SLOW)


START = T0 + 130 * NS
REF = {"fast_c": 34.0, "slow_c": 27.0}


class ReleaseLogicTests(unittest.TestCase):
    def test_flat_in_band_releases_after_ten_good_samples(self):
        s = session_from(journal_lines(lambda i: 27.0))
        out = replay.replay_g0(s, START, REF, cap_s=1200)
        self.assertEqual(out["outcome"], "released")
        self.assertTrue(7.0 < out["wait_s"] < 10.0, out["wait_s"])

    def test_above_band_times_out_at_the_cap(self):
        s = session_from(journal_lines(lambda i: 27.0 + replay.DELTA_SLOW_C + 0.01))
        out = replay.replay_g0(s, START, REF, cap_s=200)
        self.assertEqual(out["outcome"], "timeout")
        self.assertGreaterEqual(out["wait_s"], 200.0)
        self.assertAlmostEqual(out["slow_c"], 28.51, places=6)

    def test_band_edge_is_inclusive(self):
        s = session_from(journal_lines(lambda i: 27.0 + replay.DELTA_SLOW_C))
        self.assertEqual(replay.replay_g0(s, START, REF, cap_s=200)["outcome"], "released")

    def test_steep_cooling_waits_for_the_slope_bar(self):
        # In band throughout, cooling 0.5 C/min until t = 200 s, then flat.
        def slow(i):
            return 28.0 - 0.5 * min(i, 200) / 60
        s = session_from(journal_lines(slow))
        out = replay.replay_g0(s, START, {"fast_c": 34.0, "slow_c": 27.0}, cap_s=1200)
        self.assertEqual(out["outcome"], "released")
        # The 60 s slope window must be mostly flat before |slope| <= 0.2 C/min.
        self.assertGreater(out["wait_s"], 200 - 130 + 30)

    def test_status_conditions_block_release_unless_ignored(self):
        lines = journal_lines(lambda i: 27.0, status_at=lambda i: {"pm_state": "Moderate"})
        s = session_from(lines)
        self.assertEqual(replay.replay_g0(s, START, REF, cap_s=100)["outcome"], "timeout")
        self.assertEqual(replay.replay_g0(s, START, REF, cap_s=100, use_status=False)["outcome"], "released")

    def test_stale_pm_observation_blocks_release(self):
        lines = journal_lines(lambda i: 27.0, status_at=lambda i: {"pm_observed_ns": T0})
        self.assertEqual(replay.replay_g0(session_from(lines), START, REF, cap_s=100)["outcome"], "timeout")

    def test_coverage_gap_makes_the_gate_unobserved_with_a_300_s_limit(self):
        s = session_from(journal_lines(lambda i: 30.0, n=900, skip=set(range(140, 150))))
        out = replay.replay_g0(s, START, REF, cap_s=1200)
        self.assertEqual(out["outcome"], "unobserved")
        self.assertTrue(300.0 <= out["wait_s"] < 302.0, out["wait_s"])

    def test_capture_reference_is_the_median_of_the_final_60_s(self):
        s = session_from(journal_lines(lambda i: float(i)))
        anchor = T0 + 100 * NS + 500_000_000
        ref = s.capture_reference(anchor)
        self.assertTrue(ref["captured"])
        self.assertEqual(ref["samples"], 60)
        self.assertEqual(ref["slow_c"], 70.5)  # median of seconds 41..100
        self.assertEqual(s.mono_from_epoch((anchor + WALL_OFFSET) / NS), anchor)

    def test_capture_reference_refuses_low_coverage(self):
        s = session_from(journal_lines(lambda i: 27.0, skip=set(range(60, 70))))
        self.assertFalse(s.capture_reference(T0 + 100 * NS)["captured"])


class FieldRefusalTests(unittest.TestCase):
    def test_forbidden_fields_are_refused(self):
        for name in ("energy_j", "gpu_power_w", "tokens", "decode_tok_s", "joules", "watts",
                     "turn_owned_j", "perf_score", "soc_pct", "Tpower"):
            with self.subTest(name=name), self.assertRaises(replay.Refused):
                replay.require_temperature_field(name)

    def test_non_temperature_fields_are_refused(self):
        for name in ("F0Ac", "status", "pm_state", "Txx"):
            with self.subTest(name=name), self.assertRaises(replay.Refused):
                replay.require_temperature_field(name)
        self.assertEqual(replay.require_temperature_field("Tp01"), "Tp01")

    def test_projection_never_keeps_decoy_fields(self):
        with tempfile.TemporaryDirectory() as d:
            path = write_journal(d, "m", journal_lines(lambda i: 27.0, n=20))
            text = json.dumps(replay.read_journal(path))
        for name in ("energy_j", "gpu_power_w", "tokens", "123.0", "9.9", "F0Ac"):
            self.assertNotIn(name, text)

    def test_cli_refuses_a_requested_energy_field(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = replay.main(["--manifest", "/nonexistent", "--root", "/nonexistent",
                                "--field", "gpu_power"])
        self.assertEqual(code, 3)
        self.assertIn("refused field", err.getvalue())

    def test_only_thermal_journals_are_read(self):
        with tempfile.TemporaryDirectory() as d:
            other = Path(d) / "power_trace.csv"
            other.write_text("t,w\n")
            with self.assertRaises(replay.Refused):
                replay.read_journal(other)
            path = write_journal(d, "m", journal_lines(lambda i: 27.0, n=5))
            with self.assertRaises(replay.Refused):
                replay.read_journal(path, sha256="0" * 64)


class DeskTests(unittest.TestCase):
    def build(self, d, *, control_outcome="released"):
        # Control: flat at R_op, releases in about 8 s. Gated member: idle 1.2 C
        # above R_op, so it times out against R_op and releases against itself.
        g0c = {"kind": "G0", "outcome": control_outcome, "start_ns": START, "end_ns": START + 8 * NS,
               "duration_s": 8.5, "reference": {**REF, "source_member": "r1_step_30b_pre_warmup"},
               "release": {"fast_c": 34.0, "slow_c": 27.0}, "slope_c_per_min": 0.0, "exit_sample_ns": START}
        g0d = {**g0c, "outcome": "timeout", "duration_s": 200.0}
        c = write_journal(d, "c", journal_lines(lambda i: 27.0, g0=g0c))
        m = write_journal(d, "d", journal_lines(lambda i: 28.7, g0=g0d))
        anchor_epoch = (T0 + 100 * NS + 500_000_000 + WALL_OFFSET) / NS
        sha = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (c, m)}
        manifest = {"r_op": REF, "policy": {"s_fast": FAST, "s_slow": SLOW, "delta_fast_c": 1.0,
                                            "delta_slow_c": 1.5, "g0_cap_s": 1200},
                    "members": [
                        {"label": "control", "role": "control", "journal": "c/outputs/align_thermal.jsonl",
                         "sha256": sha[c], "warmup_entry_epoch_s": anchor_epoch},
                        {"label": "member", "role": "gated", "journal": "d/outputs/align_thermal.jsonl",
                         "sha256": sha[m], "warmup_entry_epoch_s": anchor_epoch}]}
        mp = Path(d) / "manifest.json"
        mp.write_text(json.dumps(manifest))
        return mp

    def test_member_releases_against_its_own_reference(self):
        with tempfile.TemporaryDirectory() as d:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = replay.main(["--manifest", str(self.build(d)), "--root", d])
        text = out.getvalue()
        self.assertEqual(code, 0, text)
        self.assertIn("SELF-CHECK PASSED", text)
        row = next(line for line in text.splitlines() if line.startswith("| member | +0.000 | +1.700"))
        self.assertIn("| released |", row)

    def test_self_check_failure_stops_before_any_verdict(self):
        with tempfile.TemporaryDirectory() as d:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = replay.main(["--manifest", str(self.build(d, control_outcome="timeout")), "--root", d])
        text = out.getvalue()
        self.assertEqual(code, 2)
        self.assertIn("SELF-CHECK FAILED", text)
        self.assertNotIn("Own pre-warmup reference", text)

    def test_manifest_policy_must_be_the_registered_one(self):
        with tempfile.TemporaryDirectory() as d:
            mp = self.build(d)
            manifest = json.loads(mp.read_text())
            manifest["policy"]["delta_slow_c"] = 2.0
            mp.write_text(json.dumps(manifest))
            with self.assertRaises(replay.Refused):
                replay.run(mp, d)


class ScenarioTests(unittest.TestCase):
    """RL-64 item 1: the consume case (step-D's capture) and delta_slow 1.0 C."""

    def build(self, d):
        # Control flat at R_op. The leg idles at 28.6 before warmup (its own
        # reference) and settles after warmup 1.2 C above it: inside a 1.5 C
        # band of its own reference, never inside a 1.0 C one. step-D's capture
        # is 29.0 C, 0.4 C above the leg's, which puts the leg inside 1.0 C of it.
        g0c = {"kind": "G0", "outcome": "released", "start_ns": START, "end_ns": START + 8 * NS,
               "duration_s": 8.5, "reference": {**REF, "source_member": "r1_step_30b_pre_warmup"},
               "release": {"fast_c": 34.0, "slow_c": 27.0}, "slope_c_per_min": 0.0, "exit_sample_ns": START}
        g0d = {**g0c, "outcome": "timeout", "duration_s": 1200.0}

        def leg(i):
            if i < 101:
                return 28.6
            return 31.8 if i < 130 else 29.8 + 2.0 * math.exp(-(i - 130) / 40)
        c = write_journal(d, "c", journal_lines(lambda i: 27.0, g0=g0c))
        sd = write_journal(d, "sd", journal_lines(lambda i: 29.0, g0=g0d))
        lg = write_journal(d, "lg", journal_lines(leg, n=600, g0=g0d))
        anchor_epoch = (T0 + 100 * NS + 500_000_000 + WALL_OFFSET) / NS
        members = [("control", "control", c, "c"), ("step_D (retry)", "gated", sd, "sd"),
                   ("leg", "gated", lg, "lg")]
        manifest = {"r_op": REF, "policy": {"s_fast": FAST, "s_slow": SLOW, "delta_fast_c": 1.0,
                                            "delta_slow_c": 1.5, "g0_cap_s": 1200},
                    "members": [{"label": label, "role": role, "journal": f"{sub}/outputs/align_thermal.jsonl",
                                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                 "warmup_entry_epoch_s": anchor_epoch}
                                for label, role, path, sub in members]}
        mp = Path(d) / "manifest.json"
        mp.write_text(json.dumps(manifest))
        return mp

    def test_scenarios_cover_own_and_consume_at_both_bands(self):
        with tempfile.TemporaryDirectory() as d:
            report = replay.run(self.build(d), d, with_scenarios=True)
        self.assertEqual(report["failures"], [])
        sc = report["scenarios"]
        self.assertAlmostEqual(sc["consume_references"]["step_D (retry)"]["slow_c"], 29.0)
        rows = {(r["label"], r["reference"], r["delta_slow_c"]): r for r in sc["rows"]}
        self.assertEqual(set(rows), {(label, ref, d) for label in ("step_D (retry)", "leg")
                                     for ref in ("own", "consume step_D (retry)") for d in (1.5, 1.0)})
        own15, own10 = rows[("leg", "own", 1.5)], rows[("leg", "own", 1.0)]
        self.assertEqual(own15["outcome"], "released")
        self.assertAlmostEqual(own15["slow_inside_c"], 0.3, delta=0.05)  # 28.6 + 1.5 - 29.8
        self.assertLessEqual(own15["band_only_s"], own15["wait_s"] + 1e-9)
        self.assertIsNotNone(own15["slope_only_s"])
        # The tighter band never admits the settled state: no release, no margin.
        self.assertNotEqual(own10["outcome"], "released")
        self.assertIsNone(own10["slow_inside_c"])
        self.assertIsNone(own10["band_only_s"])
        # Consuming step-D's warmer reference (0.4 C above the leg's own) loosens the band.
        con10 = rows[("leg", "consume step_D (retry)", 1.0)]
        self.assertAlmostEqual(con10["ref_minus_own_slow_c"], 0.4, places=6)
        self.assertEqual(con10["outcome"], "released")
        self.assertAlmostEqual(con10["slow_inside_c"], 0.2, delta=0.05)  # 29.0 + 1.0 - 29.8
        # step-D against its own capture is the consume case for itself.
        self.assertEqual(rows[("step_D (retry)", "own", 1.0)]["wait_s"],
                         rows[("step_D (retry)", "consume step_D (retry)", 1.0)]["wait_s"])

    def test_cli_prints_the_scenario_table_only_on_request(self):
        with tempfile.TemporaryDirectory() as d:
            mp = self.build(d)
            for argv, present in ((["--scenarios"], True), ([], False)):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = replay.main(["--manifest", str(mp), "--root", d, *argv])
                self.assertEqual(code, 0)
                self.assertEqual("Scenarios (RL-64 item 1)" in out.getvalue(), present)


class KeyRoleTests(unittest.TestCase):
    """RL-75/76: release, deciding condition and reference sensitivity by key pair and band."""

    def test_rows_report_decider_and_sensitivity(self):
        with tempfile.TemporaryDirectory() as d:
            report = replay.run(ScenarioTests().build(d), d, with_key_roles=True)
        self.assertEqual(report["failures"], [])
        rows = {(r["label"], r["slow"], r["delta_slow_c"]): r for r in report["key_roles"]}
        # The leg settles 1.2 C above its own Tf08 reference: never inside 1.0 C, and at
        # 1.5 C it reaches the band before its slope flattens, so the slope bar decides
        # and a 0.05 C reference shift does not move the release.
        self.assertNotEqual(rows[("leg", "Tf08", 1.0)]["outcome"], "released")
        self.assertIsNone(rows[("leg", "Tf08", 1.0)]["s_per_0p01c"])
        r15 = rows[("leg", "Tf08", 1.5)]
        self.assertEqual(r15["outcome"], "released")
        self.assertEqual(r15["decided_by"], "slope")
        self.assertLess(abs(r15["s_per_0p01c"]), 0.5)
        self.assertGreaterEqual(r15["release_s"], r15["band_only_s"])
        # The fast-family proxy pair (one key in both roles) on a flat fast key.
        proxy = rows[("leg", "TV0h", 1.0)]
        self.assertEqual(proxy["fast"], "TV0h")
        self.assertEqual(proxy["outcome"], "released")
        # Planning members are never replayed by key role (they had a heater).
        self.assertFalse(any(r["label"].startswith("planning") for r in report["key_roles"]))
        taus = {(t["label"], t["key"]): t for t in report["cooling_tau"]}
        self.assertIn(("leg", "Tf08"), taus)
        self.assertAlmostEqual(taus[("leg", "Tf08")]["peak_excess_c"], 3.2, delta=0.05)

    def test_cli_prints_key_roles_only_on_request(self):
        with tempfile.TemporaryDirectory() as d:
            mp = ScenarioTests().build(d)
            for argv, present in ((["--key-roles"], True), ([], False)):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = replay.main(["--manifest", str(mp), "--root", d, *argv])
                self.assertEqual(code, 0)
                self.assertEqual("Key roles (RL-75/76)" in out.getvalue(), present)


if __name__ == "__main__":
    unittest.main()
