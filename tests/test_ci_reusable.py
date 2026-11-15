"""The reusable CI definition (RL-144 step 1c): job names stay the ones branch protection requires
(under the caller's `ci /` prefix), every shard reads ONE merged timing map, a PR's own CI edit has
a self-test path, and the timing-map merge keeps the branch split block verbatim while main supplies weights."""
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REUSABLE = (ROOT / ".github" / "workflows" / "ci-reusable.yml").read_text(encoding="utf-8")
SELFTEST = (ROOT / ".github" / "workflows" / "ci-selftest.yml").read_text(encoding="utf-8")

# Job ids the required contexts are built from (matrix expansion adds the "(3.13, N)" part).
JOB_IDS = ("quick", "fences", "changes", "test", "calibration-exits-exclusive",
           "calibration-writer-crash-matrix-exclusive", "build", "installed-wheel")


def job_text(job: str) -> str:
    start = REUSABLE.index(f"\n  {job}:\n")
    following = [REUSABLE.index(f"\n  {other}:\n") for other in JOB_IDS
                 if other != job and REUSABLE.index(f"\n  {other}:\n") > start]
    return REUSABLE[start:min(following) if following else len(REUSABLE)]


class ReusableWorkflowShapeTests(unittest.TestCase):
    def test_is_a_workflow_call_without_its_own_concurrency(self):
        self.assertRegex(REUSABLE, r"(?m)^on:\n  workflow_call:\n")
        # A concurrency group here would collide with the caller's and deadlock the run.
        self.assertNotRegex(REUSABLE, r"(?m)^concurrency:")

    def test_every_job_the_required_contexts_name_exists(self):
        for job in JOB_IDS:
            self.assertIn(f"\n  {job}:\n", REUSABLE, job)
        self.assertIn("shard: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]", job_text("test"))
        self.assertIn("shard: [1, 2]", job_text("calibration-writer-crash-matrix-exclusive"))
        for job in JOB_IDS:  # no job renamed: the check name is the job id
            self.assertNotRegex(job_text(job).split("\n    runs-on")[0], r"\n    name:")

    def test_every_shard_reads_the_one_merged_map(self):
        self.assertIn("main_sha: ${{ steps.main.outputs.main_sha }}", job_text("changes"))
        for job in ("test", "calibration-writer-crash-matrix-exclusive"):
            text = job_text(job)
            self.assertIn("MAIN_SHA: ${{ needs.changes.outputs.main_sha }}", text, job)
            self.assertIn('timings_file = os.environ["JW_TIMINGS_FILE"]', text, job)
            self.assertNotIn("load_timing_map()", text, job)
            self.assertNotIn("load_split_declarations()", text, job)
            self.assertNotIn("conservative_unknown_weight()", text, job)
            self.assertNotIn('Path("scripts/test_timings.json").read_text', text, job)

    def test_lane_missing_pieces_are_named_not_crashed_on(self):
        for job in ("quick", "fences", "test", "calibration-writer-crash-matrix-exclusive"):
            self.assertIn("Merge origin/main into this branch", job_text(job), job)
        for job, module in (("calibration-exits-exclusive", "test_calibration_exits"),
                            ("calibration-writer-crash-matrix-exclusive", "test_calibration_writer_crash_matrix")):
            self.assertIn(f"[ -f tests/{module}.py ]", job_text(job))

    def test_the_selftest_calls_the_prs_own_copy(self):
        self.assertIn("uses: ./.github/workflows/ci-reusable.yml", SELFTEST)
        self.assertNotIn("@main", SELFTEST)
        for path in ("ci-reusable.yml", "ci-selftest.yml", "ci.yml"):
            self.assertIn(f'".github/workflows/{path}"', SELFTEST)


class TimingMergeTests(unittest.TestCase):
    def run_merge(self, lane, main):
        step = job_text("test")
        body = step.split("Fetch main's timing map", 1)[1].split("python3 - <<'PY'\n", 1)[1].split("\n          PY\n")[0]
        script = textwrap.dedent(body)
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "scripts").mkdir()
            if lane is not None:
                (tmp / "scripts" / "test_timings.json").write_text(json.dumps(lane))
            (tmp / "main_test_timings.json").write_text(json.dumps(main))
            env_file = tmp / "env"
            env = {**os.environ, "RUNNER_TEMP": str(tmp), "GITHUB_ENV": str(env_file)}
            done = subprocess.run([sys.executable, "-c", script], cwd=tmp, env=env,
                                  capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr)
            return json.loads((tmp / "merged_test_timings.json").read_text()), env_file.read_text()

    def test_main_wins_lane_only_modules_survive_exclusive_is_mains(self):
        lane = {"seconds_by_module": {"a": 1.0, "lane_only": 9.0}, "exclusive_modules": ["lane_excl"],
                "split_modules": {"lane_only": {"declared": {}}, "a": {"declared": {"x": 1}}},
                "unknown_module_weight_seconds": 5.0, "_note": "lane"}
        main = {"seconds_by_module": {"a": 2.0, "b": 3.0}, "exclusive_modules": ["main_excl"],
                "split_modules": {"a": {"declared": {"y": 2}}}, "unknown_module_weight_seconds": 26.98}
        merged, env = self.run_merge(lane, main)
        self.assertEqual(merged["seconds_by_module"], {"a": 2.0, "lane_only": 9.0, "b": 3.0})
        self.assertEqual(merged["exclusive_modules"], ["main_excl"])
        # The runner resolves remainders from the branch's own block, so it survives verbatim.
        self.assertEqual(merged["split_modules"], lane["split_modules"])
        self.assertEqual(merged["unknown_module_weight_seconds"], 26.98)
        self.assertIn("JW_TIMINGS_FILE=", env)

    def test_the_two_merge_heredocs_are_identical(self):
        def body(job):
            return job_text(job).split("Fetch main's timing map", 1)[1].split("python3 - <<'PY'\n", 1)[1].split("\n          PY\n")[0]
        self.assertEqual(body("test"), body("calibration-writer-crash-matrix-exclusive"))

    def test_lane_without_a_map_uses_main_alone(self):
        main = {"seconds_by_module": {"a": 2.0}, "exclusive_modules": [], "split_modules": {}}
        merged, _ = self.run_merge(None, main)
        self.assertEqual(merged["seconds_by_module"], {"a": 2.0})


if __name__ == "__main__":
    unittest.main()
