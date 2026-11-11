"""Synthetic-journal tests for scripts/align_r1_thermal_replay.py (RL-59 item 4)."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
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


class FollowupTests(unittest.TestCase):
    def cases(self, *, role="gated", offset=0, slow=28.2, end_s=200):
        lines = journal_lines(lambda i: slow)
        rows = session_from(lines).rows
        journal = {"rows": rows, "s_fast": FAST, "s_slow": SLOW,
                   "g0": [{"start_ns": START, "end_ns": START + end_s * NS, "reference": REF}]}
        own = {"captured": True, "fast_c": 34.0, "slow_c": 28.0}
        return replay.followup_cases({"role": role, "planning_offset_c": offset}, journal, own,
                                     {"capture": {"fast_c": 34.0, "slow_c": 28.5}})

    def test_consume_uses_fixed_capture_and_prints_both_margins(self):
        cases = self.cases()
        for c in cases:
            if c["reference_label"] == "capture":
                self.assertEqual(c["outcome"], "released")
                self.assertEqual(c["reference"]["slow_c"], 28.5)
                self.assertAlmostEqual(c["slow_margin_c"], 28.5 + c["delta_slow_c"] - 28.2)
                self.assertEqual(c["fast_margin_c"], 1.0)
        self.assertEqual({c["delta_slow_c"] for c in cases}, {1.0, 1.5})

    def test_tighter_band_is_censored_before_future_workload_rows(self):
        cases = self.cases(slow=28.2, end_s=5)
        for c in cases:
            self.assertEqual(c["outcome"], "right_censored")
            self.assertIsNone(c["slow_margin_c"])
            self.assertEqual(c["wait_s"], 5)
        # With a full observed cap the same non-releasing recorded-reference
        # case is a timeout, rather than exhaustion masquerading as a timeout.
        s = session_from(journal_lines(lambda i: 30.0, n=500))
        c = replay.replay_g0(s, START, REF, cap_s=100, observed_until_ns=START + 100 * NS)
        self.assertEqual(c["outcome"], "timeout")

    def test_planning_offsets_consume_slow_only_and_are_labelled_trace_only(self):
        c = next(c for c in self.cases(role="planning", offset=4)
                 if c["reference_label"] == "capture")
        self.assertEqual(c["reference"], {"fast_c": 150.0, "slow_c": 32.5})
        self.assertTrue(c["trace_only"])

    def test_release_margin_does_not_use_the_later_colder_timeout_sample(self):
        lines = journal_lines(lambda i: 28.2 if i < 250 else 27.0)
        journal = {"rows": session_from(lines).rows, "s_fast": FAST, "s_slow": SLOW,
                   "g0": [{"start_ns": START, "end_ns": START + 200 * NS, "reference": REF}]}
        cases = replay.followup_cases({"role": "gated"}, journal,
                                     {"captured": True, **REF}, {})
        c = next(c for c in cases if c["reference_label"] == "own" and c["delta_slow_c"] == 1.5)
        self.assertEqual(c["outcome"], "released")
        self.assertAlmostEqual(c["slow_margin_c"], 0.3)
        self.assertLess(c["wait_s"], 20)


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

    def test_consume_source_must_be_an_observed_d_member(self):
        with tempfile.TemporaryDirectory() as d:
            mp = self.build(d)
            with self.assertRaises(replay.Refused):
                replay.run(mp, d, consume_labels=("control",))
            report = replay.run(mp, d, consume_labels=("member",))
            self.assertEqual(report["consume_references"]["member"]["slow_c"], 28.7)
            self.assertTrue(all(o["followup"] for o in report["results"]))

    def test_failed_self_check_never_computes_followup_verdicts(self):
        with tempfile.TemporaryDirectory() as d:
            report = replay.run(self.build(d, control_outcome="timeout"), d, consume_labels=("member",))
            self.assertTrue(report["failures"])
            self.assertFalse(report["consume_references"])
            self.assertTrue(all("followup" not in o for o in report["results"]))


if __name__ == "__main__":
    unittest.main()
