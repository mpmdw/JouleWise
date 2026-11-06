"""SSD qualification tooling: plan balance, write pattern, extraction, evaluation.

Synthetic worlds only: each effect the criteria must catch is planted above
its margin, and its absence is checked to pass. Writes go to a temporary
directory in bytes, never gigabytes.
"""
from __future__ import annotations

import json
import random
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest

from joulewise.align.apple import ssd_qualification as q


def world(*, presence_w=0.0, write_idle_w=0.0, write_decode_w=0.0, idle_sd=0.002, decode_sd=0.02,
          drift_w_per_h=0.05, seed=7, schedule=None):
    """Segment rows with known effects; drift is linear in the ordinal."""

    rng = random.Random(seed)
    schedule = schedule or q.plan()
    rows = []
    for seg in schedule["segments"]:
        if not seg["analyzed"]:
            continue
        hours = seg["ordinal"] * 180 / 3600
        if seg["load"] == "idle":
            base, sd, write = 0.020, idle_sd, write_idle_w
        else:
            base, sd, write = 25.0, decode_sd, write_decode_w
        value = base + drift_w_per_h * hours + rng.gauss(0, sd)
        if seg["presence"] == "attached":
            value += presence_w if seg["load"] == "decode" else 0.0
        if seg["condition"] == "write" and seg["presence"] == "attached":
            value += write
        rows.append({**{k: seg[k] for k in ("ordinal", "block", "presence", "load", "condition", "pair")},
                     "power_w": {"gpu": value, "cpu": 1.0, "ane": 0.0}, "extract_flags": []})
    return rows


GOOD_OPS = {"arm_check_start": "PASS", "arm_check_end": "PASS", "volume_lost": 0,
            "metadata_daemon_contention_intervals": 0, "battery_float_violations": 0,
            "s_slow_presence_offset_c": 0.1}


class PlanTests(unittest.TestCase):
    def test_abba_balance_and_shape(self):
        schedule = q.plan()
        analyzed = [s for s in schedule["segments"] if s["analyzed"]]
        for block in {s["block"] for s in analyzed}:
            for load in ("idle", "decode"):
                segs = [s for s in analyzed if s["block"] == block and s["load"] == load]
                pos = {c: sum(i for i, s in enumerate(segs) if s["condition"] == c) for c in ("quiet", "write")}
                self.assertEqual(pos["quiet"], pos["write"], (block, load))
        targets = {(s["presence"], s["write_target"]) for s in analyzed if s["condition"] == "write"}
        self.assertEqual(targets, {("attached", "external"), ("detached", "internal")})
        self.assertTrue(all(s["burst_after"] == (s["condition"] == "write") for s in analyzed))

    def test_plan_refuses_one_sided_blocks(self):
        with self.assertRaises(ValueError):
            q.plan(blocks=("attached", "attached"))
        with self.assertRaises(ValueError):
            q.plan(idle_pairs=1)

    def test_default_has_independent_presence_residual_degrees_of_freedom(self):
        schedule = q.plan()
        self.assertEqual(schedule["blocks"],
                         ["attached", "detached", "attached", "detached", "attached"])


class PatternTests(unittest.TestCase):
    def test_fixed_cadence_bytes_and_fsyncs(self):
        now = [0.0]
        clock = lambda: now[0]  # noqa: E731

        def sleep(seconds):
            now[0] += seconds

        pattern = {"fast": {"period_s": 0.1, "bytes": 10, "fsync_every_s": None},
                   "slow": {"period_s": 1.0, "bytes": 3, "fsync_every_s": 5.0}}
        with tempfile.TemporaryDirectory() as tmp:
            stats = q.PatternWriter(tmp, pattern=pattern, clock=clock, sleep=sleep).run(10.0)
            self.assertEqual(stats["streams"]["fast"]["writes"], 100)
            self.assertEqual(stats["streams"]["slow"]["writes"], 10)
            self.assertEqual(stats["streams"]["slow"]["fsyncs"], 2)
            self.assertEqual((Path(tmp) / "fast.bin").stat().st_size, 1000)
            self.assertEqual(stats["max_lateness_s"], 0.0)

    def test_window_pattern_matches_the_sizing_evidence(self):
        # 52 kB x 10 Hz = 520 kB/s against the disk law's 512.4 kB/s slope.
        rate = q.WORST_CASE_EXTRA["powermetrics_like"]["bytes"] / q.WORST_CASE_EXTRA["powermetrics_like"]["period_s"]
        self.assertAlmostEqual(rate / 512_401.34, 1.0, delta=0.03)

    def test_teardown_burst(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = q.teardown_burst(tmp, nbytes=1000, copies=2, chunk=64)
            self.assertEqual(out["bytes"], 2000)
            self.assertTrue(all(Path(p).stat().st_size == 1000 for p in out["paths"]))


def record(t, gpu_w, width=0.1):
    return SimpleNamespace(timestamp_s=t, elapsed_ns=int(width * 1e9),
                           rail_energy_mj={"gpu_energy": int(round(gpu_w * width * 1000)),
                                           "cpu_energy": 0, "ane_energy": 0})


class ExtractTests(unittest.TestCase):
    def test_overlap_weighted_core_power(self):
        records = [record(1000 + i * 0.1, 30.0 if 1010 <= 1000 + i * 0.1 < 1030 else 5.0) for i in range(400)]
        out = q.segment_power(records, 1010.0, 1030.0, guard_s=2.0)
        self.assertAlmostEqual(out["power_w"]["gpu"], 30.0, places=6)
        self.assertEqual(out["flags"], [])

    def test_extract_uses_journal_stamps_and_flags_gaps(self):
        records = [record(1000 + i * 0.1, 10.0) for i in range(200)]
        journal = [{"kind": "segment", "analyzed": True, "ordinal": 1, "block": "1-attached", "presence": "attached",
                    "load": "idle", "condition": "quiet", "pair": "p", "work_start_epoch_s": 1000.0,
                    "work_end_epoch_s": 1030.0},
                   {"kind": "segment", "analyzed": False, "work_start_epoch_s": 0, "work_end_epoch_s": 1}]
        rows = q.extract(b"", journal, guard_s=2.0, parse=lambda _b: records)
        self.assertEqual(len(rows), 1)
        self.assertIn("segment.coverage_below_95pct", rows[0]["extract_flags"])


class EvaluateTests(unittest.TestCase):
    def test_null_world_allows_a(self):
        verdict = q.evaluate(world(), ops=GOOD_OPS)
        self.assertEqual(verdict["criteria"]["Q2_write_idle"], q.PASS, verdict["estimates_w"]["write_idle"])
        self.assertEqual(verdict["criteria"]["Q3_write_decode"], q.PASS)
        self.assertEqual(verdict["criteria"]["Q1_presence_decode"], q.PASS)
        self.assertEqual(verdict["strongest_option_allowed"], "A")

    def test_margins_follow_s_r(self):
        margins = q.criteria_margins(s_r_min_j=19.0, t_episode_s=234.5)
        self.assertAlmostEqual(margins["q2_write_idle_w"], 0.05 * 19 / 234.5)
        self.assertAlmostEqual(margins["q3_write_decode_w"], 0.30 * 19 / 234.5)

    def test_planted_write_effects_are_caught(self):
        m = q.criteria_margins()
        idle = q.evaluate(world(write_idle_w=3 * m["q2_write_idle_w"]), ops=GOOD_OPS)
        self.assertEqual(idle["criteria"]["Q2_write_idle"], q.FAIL)
        self.assertEqual(idle["strongest_option_allowed"], "B")
        decode = q.evaluate(world(write_decode_w=3 * m["q3_write_decode_w"]), ops=GOOD_OPS)
        self.assertEqual(decode["criteria"]["Q3_write_decode"], q.FAIL)

    def test_planted_presence_offset_is_caught(self):
        verdict = q.evaluate(world(presence_w=0.3), ops=GOOD_OPS)  # 1.2 % of 25 W
        self.assertEqual(verdict["criteria"]["Q1_presence_decode"], q.FAIL)
        self.assertEqual(verdict["strongest_option_allowed"], "C")

    def test_three_block_presence_design_is_inconclusive_not_pseudoreplicated(self):
        schedule = q.plan(blocks=("attached", "detached", "attached"))
        verdict = q.evaluate(world(schedule=schedule), ops=GOOD_OPS)
        self.assertEqual(verdict["criteria"]["Q1_presence_decode"], q.INCONCLUSIVE)
        self.assertEqual(verdict["strongest_option_allowed"], "C")

    def test_presence_interval_uses_blocks_as_independent_units(self):
        estimate = q.presence_offset(world(), load="decode")
        self.assertEqual(estimate["df"], 2)

    def test_noisy_decode_never_passes(self):
        for seed in range(5):
            verdict = q.evaluate(world(decode_sd=0.2, seed=seed), ops=GOOD_OPS)
            self.assertIn(verdict["criteria"]["Q3_write_decode"], (q.INCONCLUSIVE, q.FAIL))
            self.assertNotEqual(verdict["strongest_option_allowed"], "A")

    def test_judge_three_outcomes(self):
        self.assertEqual(q._judge({"mean": 0.0, "lo": -1.0, "hi": 1.0}, 2.0), q.PASS)
        self.assertEqual(q._judge({"mean": 0.5, "lo": -1.0, "hi": 3.0}, 2.0), q.INCONCLUSIVE)
        self.assertEqual(q._judge({"mean": 2.5, "lo": 2.1, "hi": 3.0}, 2.0), q.FAIL)
        self.assertEqual(q._judge(None, 2.0), q.INCONCLUSIVE)

    def test_operational_failures_and_missing_evidence_give_c(self):
        for key, value in (("volume_lost", 1), ("metadata_daemon_contention_intervals", None),
                           ("arm_check_end", None), ("s_slow_presence_offset_c", 0.8)):
            with self.subTest(key=key):
                verdict = q.evaluate(world(), ops={**GOOD_OPS, key: value})
                self.assertEqual(verdict["strongest_option_allowed"], "C")


class OpsTests(unittest.TestCase):
    def test_ps_time_and_daemon_rates(self):
        self.assertEqual(q.parse_ps_time("1:02.50"), 62.5)
        self.assertEqual(q.parse_ps_time("1-01:00:00.00"), 90000.0)
        before = q.parse_ps("  10 0:01.00 mds_stores\n  11 0:00.10 python3\n")
        after = q.parse_ps("  10 0:13.00 mds_stores\n  11 0:50.00 python3\n  12 0:00.50 mdworker_shared\n")
        rates = q.daemon_cpu_rates(before, after, 120.0)
        self.assertAlmostEqual(rates["rates"]["mds_stores"], 0.1)
        self.assertTrue(rates["contended"])
        self.assertNotIn("python3", rates["rates"])

    def test_summarize_ops(self):
        seg = {"kind": "segment", "analyzed": True, "load": "idle", "condition": "quiet", "flags": [],
               "metadata_daemons": {"contended": False}}
        journal = [{"kind": "arm_check", "verdict": "PASS"},
                   {**seg, "presence": "attached", "smc_means": {"B0AC": -20.0, "TS0P": 41.0}},
                   {**seg, "presence": "detached", "smc_means": {"B0AC": 15.0, "TS0P": 40.8}},
                   {"kind": "arm_check", "verdict": "PASS"}]
        ops = q.summarize_ops(journal, s_slow_key="TS0P")
        self.assertEqual(q.operational(ops)["verdict"], q.PASS, ops)
        self.assertAlmostEqual(ops["s_slow_presence_offset_c"], 0.2)
        ops = q.summarize_ops(journal)
        self.assertIsNone(ops["s_slow_presence_offset_c"])
        self.assertEqual(q.operational(ops)["verdict"], q.FAIL)


class RunSessionTests(unittest.TestCase):
    def test_short_session_journals_every_segment_internally(self):
        schedule = q.plan(idle_pairs=2, decode_pairs=2, segment_s=0.01, gap_s=0.0, settle_s=0.0)
        presence = []
        stamps = iter(range(1000, 2000))

        def decode():
            t = float(next(stamps))
            return {"work_start_epoch_s": t, "work_end_epoch_s": t + 0.5}

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            rows = q.run_session(schedule, journal_path=tmp / "internal/journal.jsonl", external_dir=tmp / "ext",
                                 internal_dir=tmp / "int", decode=decode, wait_presence=presence.append,
                                 pattern={"s": {"period_s": 0.005, "bytes": 4, "fsync_every_s": 0.01}},
                                 burst_bytes=16, burst_copies=2,
                                 ps_text=lambda: " 10 0:00.00 mds\n", is_attached=lambda: True)
            self.assertEqual(presence, ["attached", "detached", "attached", "detached", "attached"])
            segments = [r for r in rows if r["kind"] == "segment"]
            self.assertEqual(len(segments), len(schedule["segments"]))
            on_disk = [json.loads(line) for line in (tmp / "internal/journal.jsonl").read_text().splitlines()]
            self.assertEqual(len(on_disk), len(rows))
            writes = [r for r in segments if r["condition"] == "write"]
            self.assertTrue(all(r["burst"]["bytes"] == 32 for r in writes))
            self.assertTrue(any((tmp / "ext").iterdir()) and any((tmp / "int").iterdir()))
            self.assertTrue(all(r["metadata_daemons"]["contended"] is False for r in segments if r["analyzed"]))

    def test_journal_inside_external_tree_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                q.run_session(q.plan(), journal_path=Path(tmp) / "j.jsonl", external_dir=Path(tmp) / "x",
                              internal_dir=tmp, decode=dict, wait_presence=lambda _k: None)


class FixedDecodeCliTests(unittest.TestCase):
    def test_dry_run_imports_no_mlx(self):
        import contextlib
        import io
        import sys
        from scripts import align_ssd_fixed_decode as cli
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["--model", "/models/q30", "--tokens", "8", "--dry-run"]), 0)
        self.assertEqual(json.loads(out.getvalue())["eos_stop"], False)
        self.assertNotIn("mlx_lm", sys.modules)


if __name__ == "__main__":
    unittest.main()
