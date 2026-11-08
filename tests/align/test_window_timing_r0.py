"""Invented R0 records only; no model, host probes or measurement data."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from joulewise.align.window_timing import GitRecords, NS, read_window, worksheet


def native():
    return dict(schema="joulewise.align.r0.report.v1",
                created_utc="2026-01-02T00:00:00+00:00",
                finished_utc="2026-01-02T00:01:40+00:00", total_seconds=100,
                checks=[dict(check="smc", check_seconds=40),
                        dict(check="model-load", model="D", check_seconds=10),
                        dict(check="ladder", model="D", check_seconds=20, rungs=[
                            dict(rung="xhigh", episodes=[dict(pair="invented", turns=[
                                dict(seconds=6, raw_text="DO_NOT_EXPORT", score="DO_NOT_EXPORT"),
                                dict(seconds=4)])]),
                            dict(rung="medium", episodes=[dict(turns=[dict(seconds=5)])]),
                            dict(rung="low", status="not_run", episodes=[])]),
                        dict(check="long-decode", model="D", check_seconds=25,
                             attempts=[dict(seconds=20, memory_samples=[dict(power="DO_NOT_EXPORT")])])],
                census=[dict(monotonic_s=1000, cpu_interval=dict(
                            start_monotonic_s=1000, end_monotonic_s=1030, elapsed_s=30)),
                        dict(monotonic_s=1040, cpu_interval=dict(
                            start_monotonic_s=1020, end_monotonic_s=1080, elapsed_s=60))],
                config=dict(models=dict(D=dict(source="/Users/edr/night-do-not-open"))),
                energy="DO_NOT_EXPORT")


NOTE = """# ALIGN v4 R0 re-run 99 (2026-01-01 16:00-16:01 PST): invented

- Record: `/Users/edr/night-do-not-open` (created 00:00:00Z, finished 00:01:40Z; 100.0 s wall). Other prose.
- Agents: activation abc exited 15:55:00 PST (event 1); desk fence 15:57:00 (event 2); the run's dwell ended 16:00:00; activation def spawned 16:02:00 (event 3), after the run finished.

| Check | Status | Wall s |
|---|---|---|
| smc | DO_NOT_EXPORT | 40.0 |
| model-load (D) | DO_NOT_EXPORT | 10.0 |
| ladder (D) | DO_NOT_EXPORT | 45.0 |

power energy residual score DO_NOT_EXPORT 123456
Launcher dwell 999 s (configured only, must not create another interval).
"""


class R0TimingTest(unittest.TestCase):
    def read(self, doc=None):
        docs = {"r0.json": json.dumps(native() if doc is None else doc).encode()}
        return read_window(docs.__getitem__, r0_result="r0.json")

    def test_native_duration_budget_is_not_fabricated_epoch_placement(self):
        report = self.read()
        r0 = report["r0"]
        self.assertEqual(r0["wall_ns"], 100*NS)
        self.assertEqual(r0["checks_ns"], 95*NS)
        self.assertEqual(r0["unattributed_ns"], 5*NS)
        self.assertEqual(report["phase_ns"]["unattributed"], 100*NS)
        self.assertEqual(sum(report["phase_ns"].values()), report["wall_ns"])
        self.assertIn("check_placement", r0["unavailable"])
        self.assertEqual(r0["checks"][1]["model"], "D")

    def test_rungs_and_attempts_are_nested_call_sums_not_extra_wall(self):
        r0 = self.read()["r0"]
        self.assertEqual([r["call_ns"] for r in r0["rungs"]], [10*NS, 5*NS, None])
        self.assertTrue(all(r["wall_ns"] is None for r in r0["rungs"]))
        self.assertEqual(r0["calls"][-1]["duration_ns"], 20*NS)
        self.assertEqual(r0["checks_ns"], 95*NS)

    def test_cpu_observation_windows_union_and_never_become_waits(self):
        r0 = self.read()["r0"]
        self.assertEqual(r0["cpu_observation_union_ns"], 80*NS)
        self.assertEqual(len(r0["cpu_observations"]), 2)
        self.assertIn("quiet_guard_wait", r0["unavailable"])
        self.assertEqual(r0["unattributed_ns"], 5*NS)

    def test_timing_projection_does_not_copy_outcomes_payloads_or_paths(self):
        report = self.read()
        text = json.dumps(report) + worksheet(report)
        self.assertNotIn("DO_NOT_EXPORT", text)
        self.assertNotIn("/Users/edr/night", text)

    def test_note_rounding_and_observed_dwell(self):
        report = read_window({"NOTE.md": NOTE.encode()}.__getitem__, r0_note="NOTE.md")
        r0 = report["r0"]
        self.assertEqual(r0["format"], "committed_note")
        self.assertEqual(r0["checks_ns"], 95*NS)
        self.assertEqual(r0["unattributed_ns"], 5*NS)
        self.assertEqual(r0["rounding_bound_ns"], 200_000_000)
        self.assertEqual(report["wall_ns"], 400*NS)
        self.assertEqual(report["phase_ns"]["dwell"], 300*NS)
        self.assertEqual(report["phase_ns"]["unattributed"], 100*NS)
        self.assertEqual(r0["post_finish_to_agent_ns"], 20*NS)
        self.assertEqual(r0["milestones"]["desk_fence_ns"]-report["start_ns"], 120*NS)
        self.assertEqual(len(report["sources"]), 1)
        self.assertNotIn("DO_NOT_EXPORT", worksheet(report))

    def test_note_midnight_crossing_uses_explicit_pst_date(self):
        note = NOTE.replace("2026-01-01 16:00-16:01 PST", "2026-01-01 23:59-00:01 PST")
        note = note.replace("00:00:00Z, finished 00:01:40Z", "07:59:00Z, finished 08:01:00Z")
        note = note.replace("100.0 s wall", "120.0 s wall")
        note = note.replace("15:55:00 PST", "23:54:00 PST").replace("15:57:00", "23:56:00")
        note = note.replace("16:00:00", "23:59:00").replace("16:02:00", "00:02:00")
        r = read_window({"N.md": note.encode()}.__getitem__, r0_note="N.md")
        self.assertEqual(r["r0"]["epoch_wall_ns"], 120*NS)
        self.assertEqual(r["phase_ns"]["dwell"], 300*NS)
        self.assertEqual(r["r0"]["post_finish_to_agent_ns"], 60*NS)

    def test_configured_dwell_alone_is_unavailable(self):
        note = "\n".join(l for l in NOTE.splitlines() if not l.startswith("- Agents:"))
        r = read_window({"N.md": note.encode()}.__getitem__, r0_note="N.md")
        self.assertEqual(r["wall_ns"], 100*NS)
        self.assertEqual(r["phase_ns"]["dwell"], 0)
        self.assertIn("dwell", r["r0"]["unavailable"])

    def test_missing_step_and_turn_times_remain_unknown(self):
        d = native()
        del d["checks"][0]["check_seconds"]
        del d["checks"][2]["rungs"][0]["episodes"][0]["turns"][0]["seconds"]
        r0 = self.read(d)["r0"]
        self.assertIsNone(r0["checks"][0]["duration_ns"])
        self.assertEqual(r0["unattributed_ns"], 45*NS)
        self.assertEqual(r0["rungs"][0]["call_ns"], 4*NS)
        self.assertEqual(r0["rungs"][0]["missing_call_times"], 1)

    def test_overbooked_or_negative_times_do_not_create_negative_unknown(self):
        d = native()
        d["checks"][0]["check_seconds"] = 200
        r = self.read(d)
        self.assertIsNone(r["r0"]["unattributed_ns"])
        self.assertTrue(any("r0_check_budget_exceeds_wall" in w for w in r["warnings"]))
        d["checks"][0]["check_seconds"] = -1
        r = self.read(d)
        self.assertIsNone(r["r0"]["checks"][0]["duration_ns"])

    def test_missing_finish_does_not_invent_epoch_end_from_monotonic_total(self):
        d = native()
        del d["finished_utc"]
        with self.assertRaisesRegex(ValueError, "no observed timing"):
            self.read(d)

    def test_schema_and_exclusive_inputs(self):
        d = native()
        d["schema"] = "wrong"
        with self.assertRaisesRegex(ValueError, "R0 report schema"):
            self.read(d)
        with self.assertRaisesRegex(ValueError, "one R0"):
            read_window({}.__getitem__, r0_result="r0.json", r0_note="NOTE.md")

    def test_malformed_nested_rows_and_absent_observations_are_visible(self):
        d = native()
        d["checks"][2]["rungs"].extend([None, {"rung": "medium", "episodes": "bad"}])
        d["checks"][3]["attempts"] = [None]
        d["census"] = [None, {"cpu_interval": "bad"}]
        r = self.read(d)
        self.assertIsNone(r["r0"]["cpu_observation_union_ns"])
        self.assertIn("cpu_observations", r["r0"]["unavailable"])
        self.assertTrue(any("expected_list" in w for w in r["warnings"]))

    def test_duplicate_checks_cannot_reconcile_a_budget(self):
        d = native()
        d["checks"].append(d["checks"][1])
        r = self.read(d)
        self.assertIsNone(r["r0"]["unattributed_ns"])
        self.assertTrue(any("duplicate_R0_check" in w for w in r["warnings"]))

    def test_git_cli_uses_committed_note_and_never_embedded_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.run(["git", "-C", directory, *args], check=True, capture_output=True)
            git("-c", "init.defaultBranch=synthetic", "init", "-q", "--template=")
            git("config", "maintenance.auto", "false")
            git("config", "gc.auto", "0")
            (root/"NOTE.md").write_text(NOTE)
            git("add", "NOTE.md")
            git("-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid",
                "-c", "core.hooksPath=/dev/null", "commit", "-qm", "synthetic note")
            (root/"NOTE.md").write_text("uncommitted ignored")
            expected = read_window(GitRecords(directory, "HEAD").read, r0_note="NOTE.md")
            output = subprocess.check_output([sys.executable, "-B", "-m", "joulewise.align.window_timing",
                "--repo", directory, "--ref", "HEAD", "--r0-note", "NOTE.md", "--format", "json"])
            self.assertEqual(json.loads(output)["r0"], expected["r0"])


if __name__ == "__main__":
    unittest.main()
