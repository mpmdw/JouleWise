"""Code-only slots (S-9, S-11, S-15, S-16), the analysis lane and the command line."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.b6.analysis import slots
from joulewise.b6.analysis_lane import AnalysisLane, HarvestLane
from joulewise.flags.catalog import load_catalog
from joulewise.b6.analysis import session_index
from tests.b6.analysis.fakes import WITH_NONCOUNTING, attempt_line, write_loop_root

ROOT = Path(__file__).resolve().parents[3]


class SlotCode(unittest.TestCase):
    def test_s11_takes_the_longest_non_claim_smoke_phase(self):
        rows = [{"pack": "alpha", "phase": "decode", "duration_s": 1.9, "claim": False},
                {"pack": "alpha", "phase": "decode", "duration_s": 2.1, "claim": False},
                {"pack": "alpha", "phase": "prefill-p2048", "duration_s": 0.5, "claim": False}]
        self.assertEqual(slots.s11_phase_lengths(rows), {"alpha": {"decode": 2.1, "prefill-p2048": 0.5}})

    def test_s11_refuses_claim_rows_and_non_target_phases(self):
        for row in ({"pack": "alpha", "phase": "decode", "duration_s": 1.0, "claim": True},
                    {"pack": "alpha", "phase": "decode", "duration_s": 1.0},
                    {"pack": "alpha", "phase": "prefill-p42", "duration_s": 1.0, "claim": False},
                    {"pack": "alpha", "phase": "decode", "duration_s": 0.0, "claim": False},
                    {"pack": "alpha", "phase": "decode", "duration_s": 1, "claim": False}):
            with self.subTest(row=row), self.assertRaises(slots.SlotRefusal):
                slots.s11_phase_lengths([row])

    def test_s9_is_f_min_over_four_t_phase(self):
        """Registration S-11 comparison values: 1.9935 s gives 0.238 W, 6.6009 s gives 0.0720 W."""
        lines = slots.s9_power_lines({"alpha": {"decode": 1.9935}, "beta": {"decode": 6.6009}})
        self.assertEqual(round(lines["alpha"]["decode"], 3), 0.238)
        self.assertEqual(round(lines["beta"]["decode"], 4), 0.0720)
        self.assertEqual(slots.F_MIN_J, 1.9)

    def test_s15_carries_values_and_refuses_them_for_gamma(self):
        values = slots.s15_quantities("alpha", {"whole_machine/qwen3-1p7b/decode/mean_j": 1.0, "reported/x": 2.0})
        self.assertEqual(values["values"], {"whole_machine/qwen3-1p7b/decode/mean_j": 1.0})
        self.assertIn("AC-to-DC loss is not included", values["boundary"])
        with self.assertRaises(slots.SlotRefusal):
            slots.s15_quantities("gamma", {"whole_machine/qwen3-8b/decode/mean_j": 1.0})
        self.assertEqual(slots.s15_quantities("gamma", {})["values"], {})

    def test_s16_counts_removals_under_each_catalog(self):
        b5 = load_catalog(ROOT / "configs/campaigns/v5_claim_25g83/flag_catalog.json")
        b6 = load_catalog(ROOT / "configs/b6/flag_catalog_b6.json")
        changed_to_flag = next(c for c in sorted(b5.codes) if c in b6.codes
                               and b5.effect(c) == "EXCLUDE_WINDOW" and b6.effect(c) == "DISCLOSE")
        unchanged = next(c for c in sorted(b5.codes) if c in b6.codes and b5.effect(c) == b6.effect(c))
        new_member = next(c for c in sorted(b6.codes) if c not in b5.codes and b6.effect(c) == "EXCLUDE_MEMBER")
        sessions = {"w-alpha": [{"code": changed_to_flag, "run_id": None}, {"code": unchanged, "run_id": "r1"},
                                {"code": new_member, "run_id": "r2"}, {"code": new_member, "run_id": "r3"}],
                    "w-beta": [{"code": new_member, "run_id": "r1"}]}
        counts = slots.s16_replay_counts(sessions, b5, b6)
        self.assertEqual(set(counts), {changed_to_flag, new_member})
        self.assertEqual(counts[changed_to_flag]["block5"], {"runs_removed": 0, "sessions_removed": 1})
        self.assertEqual(counts[changed_to_flag]["block6"], {"runs_removed": 0, "sessions_removed": 0})
        self.assertEqual(counts[new_member]["block6"], {"runs_removed": 3, "sessions_removed": 0})
        self.assertIsNone(counts[new_member]["block5_effect"])
        with self.assertRaises(slots.SlotRefusal):
            slots.s16_replay_counts({"w": [{"code": 3}]}, b5, b6)


class Lane(unittest.TestCase):
    def test_loop_seam_unchanged(self):
        self.assertIsNone(AnalysisLane().precision_reached("alpha", object(), ["s"]))
        self.assertFalse(HarvestLane().capabilities().pack_scoped_flags)

    def test_lane_file_is_the_base_bytes(self):
        # It is a block-6 harvest program file; the driver lives in new files only.
        result = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "991358f73f6d509c8a1ace3e812ff4e81a3983b2",
                                 "--", "joulewise/b6/analysis_lane.py"], capture_output=True)
        if result.returncode not in (0, 1):
            self.skipTest("base commit unavailable in this clone")
        self.assertEqual(result.returncode, 0)


class SessionIndex(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name).resolve()
        self.loop = write_loop_root(self.tmp / "night-b6/loop", WITH_NONCOUNTING)
        self.measurement = self.tmp / "measurement"
        self.measurement.mkdir()
        for session_id, *_ in WITH_NONCOUNTING:
            archive = self.tmp / "night-b6/sessions" / session_id / "archive"
            archive.mkdir(parents=True)
            (archive / "harvest.json").write_text(json.dumps({"synthetic": session_id}))

    def tearDown(self):
        self._tmp.cleanup()

    def test_index_lists_every_session_with_its_locations_and_digests(self):
        index = session_index.build_session_index(self.loop, measurement=self.measurement)
        self.assertEqual(index["schema_version"], "joulewise.b6_session_index.v1")
        rows = {row["session_id"]: row for row in index["sessions"]}
        self.assertEqual(len(rows), 10)
        row = rows["r2-gamma"]
        self.assertTrue(row["counting"])
        self.assertEqual(Path(row["archive_root"]), self.tmp / "night-b6/sessions/r2-gamma/archive")
        self.assertEqual(Path(row["claim_runs_root"]), self.tmp / "night-b6/sessions/r2-gamma/archive/sources/claim-runs")
        self.assertEqual(len(row["harvest_record_sha256"]), 64)
        self.assertFalse(rows["r5-alpha"]["counting"])
        path = self.tmp / "index.json"
        path.write_text(json.dumps(index))
        self.assertEqual(session_index.load_session_index(path, loop_root=self.loop), index)

    def test_a_changed_harvest_record_or_loop_record_is_refused(self):
        path = self.tmp / "index.json"
        path.write_text(json.dumps(session_index.build_session_index(self.loop, measurement=self.measurement)))
        (self.tmp / "night-b6/sessions/r1-alpha/archive/harvest.json").write_text("{}")
        with self.assertRaises(session_index.IndexRefusal) as caught:
            session_index.load_session_index(path)
        self.assertEqual(caught.exception.code, "session_index_digest_mismatch")
        path.write_text(json.dumps(session_index.build_session_index(self.loop, measurement=self.measurement)))
        with (self.loop / "attempts.jsonl").open("a") as stream:
            stream.write(json.dumps(attempt_line("r6-alpha", "alpha", 6, "pending_harvest")) + "\n")
        with self.assertRaises(session_index.IndexRefusal) as caught:
            session_index.load_session_index(path, loop_root=self.loop)
        self.assertEqual(caught.exception.code, "session_index_stale")

    def test_an_undecided_session_has_no_digest_and_a_decided_one_needs_its_record(self):
        with (self.loop / "attempts.jsonl").open("a") as stream:
            stream.write(json.dumps(attempt_line("r6-alpha", "alpha", 6, "pending_harvest")) + "\n")
        rows = {r["session_id"]: r for r in session_index.build_session_index(self.loop, measurement=self.measurement)["sessions"]}
        self.assertIsNone(rows["r6-alpha"]["harvest_record_sha256"])
        (self.tmp / "night-b6/sessions/r1-beta/archive/harvest.json").unlink()
        with self.assertRaises(session_index.IndexRefusal) as caught:
            session_index.build_session_index(self.loop, measurement=self.measurement)
        self.assertEqual(caught.exception.code, "harvest_record_absent")

    def test_malformed_index_is_refused(self):
        path = self.tmp / "index.json"
        path.write_text(json.dumps({"schema_version": "other", "sessions": []}))
        with self.assertRaises(session_index.IndexRefusal):
            session_index.load_session_index(path)


class CommandLine(unittest.TestCase):
    def run_cli(self, *argv):
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([sys.executable, "-B", str(ROOT / "scripts/b6_analyze.py"), *argv],
                              capture_output=True, env=env, cwd=ROOT)

    def test_slots_command_prints_only_path_and_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp).resolve()
            rows = tmp / "rows.json"
            rows.write_text(json.dumps([{"pack": "alpha", "phase": "decode", "duration_s": 2.0, "claim": False}]))
            result = self.run_cli("slots", "--smoke-rows", str(rows), "--out", str(tmp / "slots.json"))
            self.assertEqual(result.returncode, 0, result.stderr)
            path, digest = result.stdout.decode().split()
            self.assertEqual(Path(path), tmp / "slots.json")
            self.assertEqual(len(digest), 64)
            values = json.loads((tmp / "slots.json").read_text())
            self.assertEqual(values["S-9"]["alpha"]["decode"], 1.9 / 8.0)
            self.assertEqual(self.run_cli("slots", "--smoke-rows", str(rows), "--out", str(tmp / "slots.json")).returncode, 2)

    def test_index_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp).resolve()
            loop = write_loop_root(tmp / "b6/loop", WITH_NONCOUNTING)
            for session_id, *_ in WITH_NONCOUNTING:
                (tmp / "b6/sessions" / session_id / "archive").mkdir(parents=True)
                (tmp / "b6/sessions" / session_id / "archive/harvest.json").write_text("{}")
            (tmp / "m").mkdir()
            result = self.run_cli("index", "--loop-root", str(loop), "--measurement", str(tmp / "m"), "--out", str(tmp / "i.json"))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(Path(result.stdout.decode().split()[0]), tmp / "i.json")
            self.assertEqual(len(json.loads((tmp / "i.json").read_text())["sessions"]), 10)

    def test_analyse_command_with_the_production_adapter_refuses_until_l9_lands(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp).resolve()
            loop = write_loop_root(tmp / "loop")
            result = self.run_cli("analyse", "--mode", "blind-dry-run", "--loop-root", str(loop), "--custody", str(tmp / "c"))
            # A dirty or unavailable checkout refuses first; either way exit 2 with structure only.
            self.assertEqual(result.returncode, 2)
            text = result.stderr.decode()
            self.assertTrue(text.startswith(("analysis - tooling_refusal", "node ")), text)


if __name__ == "__main__":
    unittest.main()
