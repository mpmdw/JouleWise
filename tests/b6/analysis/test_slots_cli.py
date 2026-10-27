"""Slots this driver owns (S-15, S-16), the session index, the lane file and the command line."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.b6.analysis import session_index, slots
from joulewise.b6.analysis.acceptance_counting import CountingRefusal, acceptance_counting
from joulewise.b6.analysis_lane import AnalysisLane, HarvestLane
from joulewise.flags.catalog import load_catalog
from tests.b6.analysis.fakes import WITH_NONCOUNTING, attempt_line, build_block6

ROOT = Path(__file__).resolve().parents[3]


class SlotCode(unittest.TestCase):
    def test_s9_and_s11_are_not_this_driver_s(self):
        """B6-2 filled them in the registration; the driver neither recomputes nor copies them."""
        self.assertFalse(hasattr(slots, "s11_phase_lengths"))
        self.assertFalse(hasattr(slots, "s9_power_lines"))

    def test_s15_carries_values_and_refuses_them_for_gamma(self):
        values = slots.s15_quantities("alpha", {"whole_machine/qwen3-1p7b/decode/mean_j": 1.0, "reported/x": 2.0})
        self.assertEqual(values["values"], {"whole_machine/qwen3-1p7b/decode/mean_j": 1.0})
        self.assertIn("AC-to-DC loss is not included", values["boundary"])
        with self.assertRaises(slots.SlotRefusal):
            slots.s15_quantities("gamma", {"whole_machine/qwen3-8b/decode/mean_j": 1.0})
        self.assertEqual(slots.s15_quantities("gamma", {})["values"], {})

    def catalogs(self):
        return (load_catalog(ROOT / "configs/campaigns/v5_claim_25g83/flag_catalog.json"),
                load_catalog(ROOT / "configs/b6/flag_catalog_b6.json"))

    def test_s16_counts_removals_under_each_catalog(self):
        b5, b6 = self.catalogs()
        changed_to_flag = next(c for c in sorted(b5.codes) if c in b6.codes
                               and b5.effect(c) == "EXCLUDE_WINDOW" and b6.effect(c) == "DISCLOSE")
        unchanged = next(c for c in sorted(b5.codes) if c in b6.codes and b5.effect(c) == b6.effect(c))
        new_member = next(c for c in sorted(b6.codes) if c not in b5.codes and b6.effect(c) == "EXCLUDE_MEMBER")
        sessions = {"w-alpha": [{"code": changed_to_flag, "run_id": None}, {"code": unchanged, "run_id": "r1"},
                                {"code": new_member, "run_id": "r2"}, {"code": new_member, "run_id": "r3"}],
                    "w-beta": [{"code": new_member, "run_id": "r1"}]}
        counts = slots.s16_replay_counts(sessions, b5, b6)
        self.assertNotIn(unchanged, counts)
        self.assertEqual(counts[changed_to_flag]["block5"], {"runs_removed": 0, "sessions_removed": 1})
        self.assertEqual(counts[changed_to_flag]["block6"], {"runs_removed": 0, "sessions_removed": 0})
        self.assertEqual(counts[new_member]["block6"], {"runs_removed": 3, "sessions_removed": 0})
        self.assertIsNone(counts[new_member]["block5_effect"])
        with self.assertRaises(slots.SlotRefusal):
            slots.s16_replay_counts({"w": [{"code": 3}]}, b5, b6)

    def test_s16_says_not_evaluated_instead_of_zero(self):
        """Audit B6-5: a rule the replay host cannot evaluate never prints a silent zero."""
        b5, b6 = self.catalogs()
        counts = slots.s16_replay_counts({}, b5, b6, evaluated=())
        self.assertTrue(counts)
        self.assertTrue(all(row["block5"] == row["block6"] == "not evaluated" for row in counts.values()))
        some = next(iter(counts))
        evaluated = slots.s16_replay_counts({}, b5, b6, evaluated=[some])
        self.assertEqual(evaluated[some]["block6"], {"runs_removed": 0, "sessions_removed": 0})


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
        self.block = build_block6(self.tmp, WITH_NONCOUNTING, compressed=False)

    def tearDown(self):
        self._tmp.cleanup()

    def index(self):
        return session_index.build_session_index(self.block.loop, measurement=self.block.measurement)

    def test_index_lists_every_session_with_its_locations_and_digests(self):
        index = self.index()
        self.assertEqual(index["schema_version"], "joulewise.b6_session_index.v1")
        rows = {row["session_id"]: row for row in index["sessions"]}
        self.assertEqual(len(rows), 10)
        row = rows["r2-gamma"]
        self.assertTrue(row["counting"])
        base = self.tmp / "b6/sessions/r2-gamma"
        self.assertEqual(Path(row["archive_root"]), base / "archive")
        self.assertEqual(Path(row["claim_runs_root"]), base / "archive/sources/claim-runs")
        self.assertEqual(row["runs_roots"], [str(base / "runs-parent/claim-runs")])
        self.assertEqual(row["compression_record"], str(base / "archive") + ".desk/compression.jsonl")
        for key in ("harvest_record_sha256", "acceptance_record_sha256", "session_record_sha256"):
            self.assertEqual(len(row[key]), 64)
        self.assertFalse(rows["r5-alpha"]["counting"])
        path = self.tmp / "index.json"
        path.write_text(json.dumps(index))
        self.assertEqual(session_index.load_session_index(path, loop_root=self.block.loop), index)

    def test_a_reharvested_session_is_located_by_its_session_record(self):
        record_path = self.tmp / "b6/sessions/r1-alpha/session.json"
        record = json.loads(record_path.read_text())
        old = Path(record["paths"]["archive"])
        new = old.with_name("archive.reharvest-1")
        old.rename(new)
        record["paths"]["archive"] = str(new)
        record_path.write_text(json.dumps(record))
        row = next(r for r in self.index()["sessions"] if r["session_id"] == "r1-alpha")
        self.assertEqual(Path(row["archive_root"]), new)

    def test_changed_records_are_refused(self):
        for changed in ("archive/harvest.json", "archive/derived/b6-acceptance.json", "session.json"):
            with self.subTest(changed=changed):
                path = self.tmp / "index.json"
                path.write_text(json.dumps(self.index()))
                target = self.tmp / "b6/sessions/r1-beta" / changed
                original = target.read_text()
                target.write_text(original.rstrip("}") + ', "changed": true}')
                with self.assertRaises(session_index.IndexRefusal) as caught:
                    session_index.load_session_index(path)
                self.assertEqual(caught.exception.code, "session_index_digest_mismatch")
                target.write_text(original)
        path = self.tmp / "index.json"
        path.write_text(json.dumps(self.index()))
        with (self.block.loop / "attempts.jsonl").open("a") as stream:
            stream.write(json.dumps(attempt_line("r6-alpha", "alpha", 6, "pending_harvest")) + "\n")
        with self.assertRaises(session_index.IndexRefusal) as caught:
            session_index.load_session_index(path, loop_root=self.block.loop)
        self.assertEqual(caught.exception.code, "session_index_stale")

    def test_an_undecided_session_has_no_digest_and_a_decided_one_needs_its_records(self):
        with (self.block.loop / "attempts.jsonl").open("a") as stream:
            stream.write(json.dumps(attempt_line("r6-alpha", "alpha", 6, "pending_harvest")) + "\n")
        rows = {r["session_id"]: r for r in self.index()["sessions"]}
        self.assertIsNone(rows["r6-alpha"]["harvest_record_sha256"])
        self.assertIsNone(rows["r6-alpha"]["acceptance_record_sha256"])
        (self.tmp / "b6/sessions/r1-beta/archive/derived/b6-acceptance.json").unlink()
        with self.assertRaises(session_index.IndexRefusal) as caught:
            self.index()
        self.assertEqual(caught.exception.code, "acceptance_record_absent")

    def test_acceptance_counting_reads_only_the_acceptance_record(self):
        counting = acceptance_counting(self.index())
        self.assertEqual(counting["r5-alpha"], False)
        self.assertEqual(counting["r2-gamma"], True)
        path = self.tmp / "b6/sessions/r2-gamma/archive/derived/b6-acceptance.json"
        path.write_text(json.dumps({**json.loads(path.read_text()), "session_id": "r3-gamma"}))
        with self.assertRaises(CountingRefusal) as caught:
            acceptance_counting(self.index())
        self.assertEqual((caught.exception.code, caught.exception.sessions),
                         ("acceptance_record_unreadable", ("r2-gamma",)))

    def test_malformed_index_is_refused(self):
        path = self.tmp / "index.json"
        path.write_text(json.dumps({"schema_version": "other", "sessions": []}))
        with self.assertRaises(session_index.IndexRefusal):
            session_index.load_session_index(path)


class CommandLine(unittest.TestCase):
    def run_cli(self, *argv):
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "JW_B5_SYNTHETIC_ONLY": "1",
               "TMPDIR": tempfile.gettempdir()}
        return subprocess.run([sys.executable, "-B", str(ROOT / "scripts/b6_analyze.py"), *argv],
                              capture_output=True, env=env, cwd=ROOT)

    def test_index_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp).resolve()
            block = build_block6(tmp / "t", WITH_NONCOUNTING, compressed=False)
            result = self.run_cli("index", "--loop-root", str(block.loop), "--measurement", str(block.measurement),
                                  "--out", str(tmp / "i.json"))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(Path(result.stdout.decode().split()[0]), tmp / "i.json")
            self.assertEqual(len(json.loads((tmp / "i.json").read_text())["sessions"]), 10)
            self.assertEqual(self.run_cli("index", "--loop-root", str(block.loop), "--measurement",
                                          str(block.measurement), "--out", str(tmp / "i.json")).returncode, 2)

    def test_analyse_command_with_the_production_adapter_refuses_until_l9_lands(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp).resolve()
            block = build_block6(tmp / "t", compressed=False)
            result = self.run_cli("analyse", "--mode", "per-session", "--loop-root", str(block.loop),
                                  "--index", str(block.index), "--custody", str(tmp / "c"))
            # A dirty or unavailable checkout refuses first; either way exit 2 with structure only.
            self.assertEqual(result.returncode, 2)
            text = result.stderr.decode()
            self.assertTrue(text.startswith(("analysis - tooling_refusal", "node ")), text)

    def test_synthetic_mode_refuses_a_root_outside_tmpdir(self):
        result = self.run_cli("analyse", "--mode", "per-session", "--loop-root", "/var/not-tmp/loop",
                              "--index", "/var/not-tmp/index.json", "--custody", "/var/not-tmp/c")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr.decode().strip(), "analysis - tooling_refusal synthetic_root_outside_tmpdir")


if __name__ == "__main__":
    unittest.main()
