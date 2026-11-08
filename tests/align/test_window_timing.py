import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.align.window_timing_synthetic import EPOCH, NS, campaign, fixture, options
from tests.align.benchmark_window_timing import scan_partition
from joulewise.align import window_timing
from joulewise.align.window_timing import GitRecords, Interval, partition, read_window, worksheet


class WindowTimingTest(unittest.TestCase):
    def read(self, docs=None, **overrides):
        docs = fixture() if docs is None else docs
        opts = options()
        opts.update(overrides)
        return read_window(docs.__getitem__, **opts)

    def test_native_records_have_exact_disjoint_wall_and_member_totals(self):
        report = self.read()
        self.assertEqual(report["wall_ns"], 100*NS)
        self.assertEqual(sum(report["phase_ns"].values()), 100*NS)
        # 15..20, 57..58, 60..70, 85..90 are the four recorded gaps.
        self.assertEqual(report["phase_ns"]["unattributed"], 21*NS)
        self.assertEqual(report["phase_ns"]["references"], 10*NS)
        member = report["members"]["m1"]
        self.assertEqual(member["wall_ns"], 40*NS)
        self.assertEqual(member["phase_ns"]["decode"], 13*NS)
        self.assertEqual(member["phase_ns"]["gates"], 5*NS)
        self.assertEqual(member["phase_ns"]["holds"], 4*NS)
        self.assertEqual(member["activity_ns"]["prefill"], 3*NS)
        self.assertEqual(member["activity_ns"]["tool"], 2*NS)
        self.assertEqual(member["unavailable"], ["eligibility"])
        self.assertEqual(sum(member["phase_ns"].values()), member["wall_ns"])
        self.assertEqual(report["ceiling"]["terminal_minus_origin_ns"], 85*NS)
        self.assertEqual(report["ceiling"]["status"], "closed_before_ceiling")
        self.assertIn("G1", worksheet(report))

    def test_reference_rollup_keeps_member_activity(self):
        report = self.read(stage_phases={"refs": "references", "science": "references"})
        self.assertEqual(report["members"]["m1"]["phase_ns"]["references"], 40*NS)
        self.assertEqual(report["members"]["m1"]["activity_ns"]["decode"], 13*NS)

    def test_aggregate_only_r1_wait_is_not_backdated_across_release(self):
        docs = fixture()
        docs["r1.json"] = json.dumps(dict(phases=[dict(
            name="step-d", started_ns=(EPOCH+20)*NS, ended_ns=(EPOCH+60)*NS,
            attempt=1, os_batch_wait_s=11164, g0_release={"unplaced": True},
            superseded_attempts=[dict(name="step-d", started_ns=(EPOCH+10)*NS,
                                     ended_ns=(EPOCH+12)*NS, attempt=0, os_batch_wait_s=3)],
            result={"phases_s": {"decode": 20}})])).encode()
        report = self.read(docs, r1_result="r1.json")
        self.assertEqual(sum(a["os_batch_wait_ns"] for a in report["attempts"]), 11167*NS)
        self.assertEqual(report["attempts"][1]["wait_placement"], "unplaced")
        self.assertTrue(all(a["os_batch_wait_basis"] == "requested, unmeasured" for a in report["attempts"]))
        self.assertNotIn("os_batch_wait", report["activity_ns"])
        self.assertEqual(report["wall_ns"], 100*NS)

    def test_missing_episode_clock_mapping_cannot_be_guessed(self):
        docs = fixture()
        path = "runs/m1/outputs/align_episode.json"
        episode = json.loads(docs[path])
        episode["clock_mappings"] = []
        docs[path] = json.dumps(episode).encode()
        report = self.read(docs)
        self.assertEqual(report["members"]["m1"]["phase_ns"]["decode"], 0)
        self.assertTrue(any("clock_mapping_unavailable" in s for s in report["warnings"]))

    def test_missing_first_token_does_not_become_prefill_or_decode(self):
        docs = fixture()
        path = "runs/m1/outputs/align_episode.json"
        episode = json.loads(docs[path])
        episode["turns"][0]["first_token_ns"] = None
        docs[path] = json.dumps(episode).encode()
        report = self.read(docs)
        self.assertEqual(report["members"]["m1"]["phase_ns"]["decode"], NS)
        self.assertTrue(any("first_token_unavailable" in s for s in report["warnings"]))

    def test_episode_with_wrong_clock_mapping_cannot_expand_window(self):
        docs = fixture()
        p = "runs/m1/outputs/align_episode.json"
        ep = json.loads(docs[p])
        ep["clock_mappings"][0]["offset_ns"] -= 1000*NS
        docs[p] = json.dumps(ep).encode()
        report = self.read(docs)
        self.assertEqual(report["wall_ns"], 100*NS)
        self.assertEqual(report["members"]["m1"]["phase_ns"]["decode"], 0)
        self.assertIn("episode_placement", report["members"]["m1"]["unavailable"])

    def test_torn_journal_and_unclosed_stage_are_visible(self):
        docs = fixture()
        docs["night/chain-stages.jsonl"] += b'{"torn":\n'
        path = "runs/m1/events.jsonl"
        rows = [r for r in map(json.loads, docs[path].splitlines())
                if not (r["phase"] == "idle_baseline" and r["event_type"] == "stage_completed")]
        docs[path] = b"\n".join(json.dumps(r).encode() for r in rows)
        report = self.read(docs)
        self.assertTrue(any("malformed_json_line" in s for s in report["warnings"]))
        self.assertTrue(any("unclosed_event" in s for s in report["warnings"]))
        self.assertEqual(report["members"]["m1"]["phase_ns"]["idle"], 0)

    def test_ceiling_tail_is_unknown_without_explicit_wait_evidence(self):
        docs = fixture()
        docs["night/chain.exited"] = json.dumps(dict(epoch_s=EPOCH+59520, monotonic_ns=59520*NS)).encode()
        docs["night/result.json"] = json.dumps(dict(started_epoch_s=EPOCH, ended_epoch_s=EPOCH+59520)).encode()
        report = self.read(docs)
        self.assertEqual(report["ceiling"]["status"], "at_or_after_ceiling_cause_unproven")
        self.assertEqual(report["ceiling"]["post_last_stage_ns"], (59520-85)*NS)
        self.assertGreater(report["phase_ns"]["unattributed"], 59000*NS)

    def test_deadline_tail_is_an_overlay_never_added_to_wall(self):
        docs = fixture()
        p = "runs/m1/outputs/align_episode.json"
        ep = json.loads(docs[p])
        ep["hardware"]["token_budget"] = {"deadline_ns": 150*NS}
        docs[p] = json.dumps(ep).encode()
        report = self.read(docs)
        self.assertEqual(report["members"]["m1"]["deadline_tail_ns"], 8*NS)
        self.assertEqual(sum(report["phase_ns"].values()), 100*NS)

    def test_clock_step_is_flagged(self):
        docs = fixture()
        docs["night/result.json"] = json.dumps(dict(started_epoch_s=EPOCH, ended_epoch_s=EPOCH+87,
                                                   started_monotonic_ns=0, ended_monotonic_ns=80*NS)).encode()
        self.assertTrue(any("clock_elapsed_disagreement" in s for s in self.read(docs)["warnings"]))

    def test_native_paired_clock_fallback_and_gate_missingness(self):
        docs = fixture()
        p = "runs/m1/outputs/align_episode.json"
        ep = json.loads(docs[p])
        ep["clock_mappings"] = []
        ep["hardware"].pop("thermal")
        ep["hardware"]["paired_clock_stamps_ns"] = [dict(
            epoch_ns=(EPOCH+30)*NS, monotonic_before_ns=130*NS,
            monotonic_after_ns=130*NS, wall_resolution_ns=1, monotonic_resolution_ns=1)]
        docs[p] = json.dumps(ep).encode()
        report = self.read(docs)
        self.assertEqual(report["members"]["m1"]["phase_ns"]["decode"], 17*NS)
        self.assertIn("gate_intervals", report["members"]["m1"]["unavailable"])
        self.assertIn("clock_mapping_uncertainty_ns", report["members"]["m1"])

    def test_run_night_log_admission_aggregate_can_be_refined_by_dwell(self):
        docs = fixture()
        docs["night/log.txt"] = ("2027-01-15T08:00:00+00:00 night driver started\n"
                                  "2027-01-15T08:00:05+00:00 night gate verdict=GO\n").encode()
        docs["dwell.json"] = json.dumps(dict(started_epoch_s=EPOCH+2, ended_epoch_s=EPOCH+4)).encode()
        report = self.read(docs, night_log="night/log.txt")
        self.assertEqual(report["activity_ns"]["admission_aggregate"], NS)

    def test_overlapping_members_have_unknown_ownership_at_window_level(self):
        docs = fixture()
        for path, raw in list(docs.items()):
            if path.startswith("runs/m1/"):
                obj = raw.replace(b'"m1"', b'"m2"')
                docs[path.replace("runs/m1/", "runs/m2/")] = obj
        report = self.read(docs, bundles=["runs/m1", "runs/m2"])
        self.assertTrue(any("overlapping_member_envelopes" in w for w in report["warnings"]))
        self.assertEqual(report["members"]["m1"]["wall_ns"], 40*NS)
        self.assertTrue(all(r["member"] is None for r in report["ledger"] if r["ambiguous"]))

    def test_window_ownership_conflict_survives_different_activity_priorities(self):
        docs, opts = campaign(2)
        path = "runs/m002/events.jsonl"
        rows = [json.loads(r) for r in docs[path].splitlines()]
        for row in rows:
            row["timestamp_s"] -= 20
        docs[path] = "".join(json.dumps(r)+"\n" for r in rows).encode()
        # Deliberately omit m2's episode: its lifecycle still overlaps m1.
        del docs["runs/m002/outputs/align_episode.json"]
        report = read_window(docs.__getitem__, **opts)
        overlap = [r for r in report["ledger"] if EPOCH*NS+40*NS <= r["start_ns"] < EPOCH*NS+60*NS]
        self.assertTrue(overlap)
        self.assertTrue(all(r["ambiguous"] and r["phase"] == "unattributed" for r in overlap))
        self.assertEqual(report["members"]["m001"]["phase_ns"]["decode"], 13*NS)

    def test_no_chain_exit_does_not_substitute_last_stage_as_terminal(self):
        report = self.read(chain_exited=None)
        self.assertEqual(report["ceiling"]["status"], "unavailable")
        self.assertIsNone(report["ceiling"]["terminal_ns"])

    def test_malformed_or_reversed_native_rows_flagged_without_accounting(self):
        docs = fixture()
        docs["night/chain-stages.jsonl"] += (b'null\n'+json.dumps(dict(
            started_epoch_s=EPOCH+30, ended_epoch_s=EPOCH+10, kind="backup", stage_id="bad")).encode()+b'\n')
        report = self.read(docs)
        self.assertEqual(report["wall_ns"], 100*NS)
        self.assertTrue(any("reversed_epoch_interval" in w for w in report["warnings"]))

    def test_repeatability_and_input_bytes_unchanged(self):
        docs = fixture()
        before = dict(docs)
        one, two = self.read(docs), self.read(docs)
        self.assertEqual(json.dumps(one, sort_keys=True), json.dumps(two, sort_keys=True))
        self.assertEqual(docs, before)

    def test_log_rows_from_other_windows_do_not_expand_envelope(self):
        docs = fixture()
        docs["night/log.txt"] = ("2027-01-14T08:00:00+00:00 night driver started\n"
                                  "2027-01-14T08:00:05+00:00 night gate verdict=GO\n").encode()
        report = self.read(docs, night_log="night/log.txt")
        self.assertEqual(report["wall_ns"], 100*NS)
        self.assertTrue(any("log_event_outside_driver_bounds" in w for w in report["warnings"]))

    def test_paired_stamps_exposing_clock_step_invalidate_episode_placement(self):
        docs = fixture()
        p = "runs/m1/outputs/align_episode.json"
        ep = json.loads(docs[p])
        # A valid explicit mapping is retained with added uncertainty. This
        # exercises the paired-stamp-only fallback's refusal of a clock step.
        ep["clock_mappings"] = []
        ep["hardware"]["paired_clock_stamps_ns"] = [
            dict(epoch_ns=(EPOCH+30)*NS, monotonic_before_ns=130*NS, monotonic_after_ns=130*NS),
            dict(epoch_ns=(EPOCH+60)*NS, monotonic_before_ns=158*NS, monotonic_after_ns=158*NS)]
        docs[p] = json.dumps(ep).encode()
        report = self.read(docs)
        self.assertEqual(report["members"]["m1"]["phase_ns"]["decode"], 0)
        self.assertTrue(any("episode_clock_elapsed_disagreement" in w for w in report["warnings"]))

    def test_native_r1_brackets_are_scaffold_without_bundles(self):
        docs = {"r1.json": json.dumps(dict(phases=[dict(
            name="pre_calibration_bracket", started_ns=10*NS, ended_ns=15*NS,
            os_batch_wait_s=0, result={})])).encode()}
        report = read_window(docs.__getitem__, r1_result="r1.json")
        self.assertEqual(report["phase_ns"]["scaffold"], 5*NS)


class PartitionTest(unittest.TestCase):
    def test_full_report_and_worksheet_bytes_equal_independent_scan(self):
        docs, opts = campaign(22)
        sweep = read_window(docs.__getitem__, **opts)
        with patch.object(window_timing, "partition", scan_partition):
            scan = read_window(docs.__getitem__, **opts)
        self.assertEqual(json.dumps(sweep, sort_keys=True), json.dumps(scan, sort_keys=True))
        self.assertEqual(worksheet(sweep), worksheet(scan))

    def test_sweep_equals_independent_integer_grid_oracle(self):
        rng = random.Random(412)
        for _ in range(80):
            intervals = []
            for i in range(20):
                a, b = sorted(rng.sample(range(41), 2))
                intervals.append(Interval(a, b, "decode" if i % 2 else "idle", str(i), i % 4,
                                          member="m"+str(i % 3)))
            actual = partition(0, 40, intervals)
            self.assertEqual(sum(r["end_ns"]-r["start_ns"] for r in actual), 40)
            expanded = [(r["phase"], r["member"]) for r in actual
                        for _ in range(r["end_ns"]-r["start_ns"])]
            expected = []
            for t in range(40):
                active = [i for i in intervals if i.start_ns <= t < i.end_ns]
                top = [i for i in active if i.priority == max(a.priority for a in active)] if active else []
                labels = {(i.phase, i.member) for i in top}
                expected.append(next(iter(labels)) if len(labels) == 1 else ("unattributed", None))
            self.assertEqual(expanded, expected)

    def test_reversed_interval_refused(self):
        with self.assertRaises(ValueError):
            Interval(10, 2, "idle", "bad", 1)

    def test_conflict_and_reference_overlay_equal_scan_oracle(self):
        spans = [Interval(-5, 50, "references", "parent", 1),
                 Interval(2, 30, "decode", "member-a", 3, "a"),
                 Interval(15, 20, "idle", "member-b", 3, "b"),
                 Interval(25, 25, "holds", "zero", 9, "a")]
        self.assertEqual(partition(0, 40, spans), scan_partition(0, 40, spans))


class CommittedReaderTest(unittest.TestCase):
    def test_reads_commit_only_and_cli_matches_library_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
            def git(*args):
                return subprocess.run(["git", "-C", tmp, *args], check=True, capture_output=True, env=env)
            git("init", "-q")
            for path, raw in fixture().items():
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
            git("add", ".")
            git("-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid",
                "-c", "core.hooksPath=/dev/null", "commit", "-qm", "synthetic record")
            store = GitRecords(root, "HEAD")
            before = git("status", "--porcelain").stdout
            expected = read_window(store.read, **options())
            (root / "runs/m1/metadata.json").write_text("uncommitted corrupt input")
            self.assertEqual(expected, read_window(store.read, **options()))
            args = [sys.executable, "-B", "-m", "joulewise.align.window_timing", "--repo", tmp,
                    "--ref", "HEAD", "--night-result", "night/result.json", "--chain-started", "night/chain.started",
                    "--chain-exited", "night/chain.exited", "--chain-journal", "night/chain-stages.jsonl",
                    "--plan", "plan.json", "--bundle", "runs/m1", "--stage-phase", "refs=references",
                    "--span", "arm=arm.json", "--span", "dwell=dwell.json", "--span", "offload=offload.json",
                    "--format", "json"]
            output = subprocess.run(args, check=True, capture_output=True).stdout
            self.assertEqual(json.loads(output)["ledger"], expected["ledger"])
            self.assertEqual(before, b"")
            self.assertEqual(git("status", "--porcelain").stdout.count(b"\n"), 1)
            for unsafe in ("../outside", "/Users/edr/jw-b5-sealed/a", "restricted/a", "x/night-archive/a",
                           "x/night-custody/a", "x/jw-b5-secret/a", ".git/config"):
                with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                    store.read(unsafe)
            (root / "link.json").symlink_to("/nonexistent-synthetic-target")
            git("add", "link.json")
            git("-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid",
                "-c", "core.hooksPath=/dev/null", "commit", "-qm", "synthetic symlink")
            with self.assertRaises(ValueError):
                GitRecords(root, "HEAD").read("link.json")


if __name__ == "__main__":
    unittest.main()
