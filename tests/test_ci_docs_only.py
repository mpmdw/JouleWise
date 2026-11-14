"""The CI range classifiers: docs-only (scripts/ci_docs_only.sh) suppresses tests only for
unreferenced Markdown; class A (scripts/ci_state_only.sh, RL-144 term 1) admits the state records and
documentation no test reads, and runs the quick tier and fences instead of the shards."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.git_fixture import init_git_fixture

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ci_docs_only.sh"
STATE_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ci_state_only.sh"
WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"


class DocsOnlyClassifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t"}
        self.env = env
        init_git_fixture(self.repo, "-q")
        self.write({"README.md": "x\n", "docs/notes.md": "x\n", "docs/seal.md": "x\n",
                    "tests/test_seal.py": "PATH = 'docs/seal.md'\n", "joulewise/core.py": "x = 1\n"})
        self.base = self.commit()

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, files):
        for name, text in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", "c")
        return self.git("rev-parse", "HEAD")

    def classify(self, files, before=None):
        self.git("checkout", "-q", self.base)
        self.write(files)
        after = self.commit()
        return subprocess.run(["bash", str(SCRIPT), before or self.base, after], cwd=self.repo,
                              env=self.env).returncode

    def test_unreferenced_docs_markdown_is_docs_only(self):
        self.assertEqual(self.classify({"docs/notes.md": "y\n"}), 0)

    def test_root_markdown_is_docs_only(self):
        self.assertEqual(self.classify({"README.md": "y\n"}), 0)

    def test_python_under_docs_runs_tests(self):
        self.assertEqual(self.classify({"docs/tool.py": "x = 2\n"}), 1)

    def test_config_under_docs_runs_tests(self):
        self.assertEqual(self.classify({"docs/table.json": "{}\n"}), 1)

    def test_markdown_referenced_by_a_test_runs_tests(self):
        self.assertEqual(self.classify({"docs/seal.md": "changed\n"}), 1)

    def test_mixed_range_runs_tests(self):
        self.assertEqual(self.classify({"docs/notes.md": "y\n", "joulewise/core.py": "x = 2\n"}), 1)

    def test_markdown_outside_docs_and_root_runs_tests(self):
        self.assertEqual(self.classify({"configs/plan.md": "y\n"}), 1)

    def test_workflow_change_runs_tests(self):
        self.assertEqual(self.classify({".github/workflows/ci.yml": "on: push\n"}), 1)

    def test_glob_read_docs_directories_run_tests(self):
        for path in ("docs/paper/new.md", "docs/paper/paper1/paper1.md", "docs/registrations/b9.md", "docs/contracts/c.md", "docs/process_traces/t/r.md",
                     "docs/null/n.md", "docs/site/s.md"):
            with self.subTest(path=path):
                self.assertEqual(self.classify({path: "y\n"}), 1)

    def test_empty_range_runs_tests(self):
        self.assertEqual(self.classify({}), 1)

    def test_malformed_sha_runs_tests(self):
        self.assertEqual(self.classify({"docs/notes.md": "y\n"}, before="not-a-sha"), 1)

    def test_unknown_commit_runs_tests(self):
        self.assertEqual(self.classify({"docs/notes.md": "y\n"}, before="0123456789" * 4), 1)


class StateOnlyClassifierTests(unittest.TestCase):
    """Class A: state records, plus documentation that no test reads (full path, basename, parent dir)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        init_git_fixture(self.repo, "-q")
        self.write({"RUN_STATE.md": "x\n", "TASK_QUEUE.md": "x\n", "docs/process/CURRENT.json": "{}\n",
                    "docs/notes.md": "x\n", "joulewise/core.py": "x = 1\n",
                    "docs/run_reports/2026-11-12-pr746-review.md": "x\n",
                    "docs/analysis/b5/edge-check-reading-rule.md": "x\n",
                    "docs/registrations/block6_freeze_by_commit_addendum.md": "x\n",
                    "docs/paper/paper1/paper1.md": "x\n", "docs/paper/paper1/fill_index.md": "x\n",
                    "docs/paper/paper1/figures/f.svg": "<svg/>\n", "docs/paper/read_by_test.md": "x\n",
                    "docs/paper/round7/r.md": "x\n", "docs/read/by_path.md": "x\n",
                    "docs/read/by_name.md": "x\n", "docs/readdir/other.md": "x\n",
                    "docs/readjoin/other.md": "x\n", "docs/readbase.md": "x\n", "docs/fig.svg": "<svg/>\n",
                    "CANONICAL.md": "x\n",
                    "tests/test_reader.py": ("A = 'docs/read/by_path.md'\n"
                                             "B = ROOT / 'docs' / 'x' / 'by_name.md'\n"
                                             "C = 'docs/readdir/'\n"
                                             "D = ROOT / \"docs\" / \"readjoin\"\n"
                                             "E = ROOT / 'CANONICAL.md'\n"
                                             "F = ROOT / 'docs' / 'paper' / 'read_by_test.md'\n"
                                             "G = ROOT / 'docs' / 'paper' / 'round7'\n")})
        self.base = self.commit()

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, files):
        for name, text in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", "c")
        return self.git("rev-parse", "HEAD")

    def classify(self, files, before=None):
        return self.classify_full(files, before)[0]

    def classify_full(self, files, before=None):
        self.git("checkout", "-q", self.base)
        self.write(files)
        after = self.commit()
        result = subprocess.run(["bash", str(STATE_SCRIPT), before or self.base, after], cwd=self.repo,
                                env=self.env, capture_output=True, text=True)
        return result.returncode, result.stdout.split()

    def test_run_state_alone_is_state_only(self):
        self.assertEqual(self.classify({"RUN_STATE.md": "y\n"}), 0)

    def test_run_state_with_generated_current_pointer_is_state_only(self):
        self.assertEqual(self.classify({"RUN_STATE.md": "y\n", "docs/process/CURRENT.json": "{\"a\": 1}\n"}), 0)

    def test_task_queue_is_state_only(self):
        self.assertEqual(self.classify({"TASK_QUEUE.md": "y\n"}), 0)

    def test_state_with_unread_docs_is_class_a(self):
        self.assertEqual(self.classify({"RUN_STATE.md": "y\n", "docs/notes.md": "y\n"}), 0)

    def test_pr746_file_list_is_class_a(self):
        # Real PR #746: a b5 reading rule and its review report.
        self.assertEqual(self.classify({"docs/analysis/b5/edge-check-reading-rule.md": "y\n",
                                        "docs/run_reports/2026-11-12-pr746-review.md": "y\n"}), 0)

    def test_new_run_report_and_state_records_are_class_a(self):
        # Shape of PR #712's report files plus the state records the lead appends.
        self.assertEqual(self.classify({"docs/run_reports/2026-11-13-new.md": "y\n", "RUN_STATE.md": "y\n",
                                        "TASK_QUEUE.md": "y\n", "docs/fig.svg": "<svg>y</svg>\n"}), 0)

    def test_docs_read_by_a_test_run_everything(self):
        cases = {
            "full path named in a test": "docs/read/by_path.md",
            "basename named in a test (path parts are joined)": "docs/elsewhere/by_name.md",
            "parent directory named in a test": "docs/readdir/new.md",
            "parent directory joined from quoted parts in a test": "docs/readjoin/new.md",
            "root document named in a test": "CANONICAL.md",
        }
        for why, path in cases.items():
            with self.subTest(why=why):
                self.assertEqual(self.classify({path: "y\n"}), 1)

    CENSUS = "tests.test_d165_rationale_census"

    def test_paper_text_is_class_a_with_the_census_as_declared_extra_test(self):
        # Shape of PRs #716-#718: paper text plus fill index, figures and a run report.
        self.assertEqual(self.classify_full({"docs/paper/new.md": "y\n", "docs/paper/paper1/fill_index.md": "y\n",
                                             "docs/paper/paper1/figures/f.svg": "<svg>y</svg>\n",
                                             "docs/run_reports/new.md": "y\n"}), (0, [self.CENSUS]))

    def test_paper_text_with_state_records_names_the_census_once(self):
        self.assertEqual(self.classify_full({"docs/paper/a.md": "y\n", "docs/paper/b.md": "y\n",
                                             "RUN_STATE.md": "y\n"}), (0, [self.CENSUS]))

    def test_ranges_without_paper_text_name_no_extra_test(self):
        self.assertEqual(self.classify_full({"docs/notes.md": "y\n", "RUN_STATE.md": "y\n"}), (0, []))

    def test_paper_text_read_by_another_test_runs_everything(self):
        for path in ("docs/paper/read_by_test.md", "docs/paper/elsewhere/read_by_test.md",
                     "docs/paper/round7/new.md"):
            with self.subTest(path=path):
                self.assertEqual(self.classify_full({path: "y\n"}), (1, []))

    def test_paper_code_and_data_run_everything(self):
        for path in ("docs/paper/paper1/fill_check_b5.py", "docs/paper/table.json", "docs/paper/protocol"):
            with self.subTest(path=path):
                self.assertEqual(self.classify_full({path: "y\n"})[0], 1)
        self.assertEqual(self.classify_full({"docs/paper/new.md": "y\n", "joulewise/core.py": "x = 2\n"})[0], 1)

    def test_declared_extra_test_exists(self):
        self.assertTrue((SCRIPT.parents[1] / "tests" / "test_d165_rationale_census.py").is_file())
        self.assertIn("'docs/paper/*|" + self.CENSUS + "'", STATE_SCRIPT.read_text(encoding="utf-8"))

    def test_registration_and_other_read_directories_run_everything(self):
        for path in ("docs/registrations/block6_freeze_by_commit_addendum.md", "docs/registrations/new.md",
                     "docs/contracts/c.md",
                     "docs/process/NIGHT_HANDBACK.md", "docs/process_traces/t/r.md", "docs/unseals/u.md",
                     "docs/site/s.md", "docs/null/n.md", "docs/campaign_packs/p.md"):
            with self.subTest(path=path):
                self.assertEqual(self.classify({path: "y\n"}), 1)

    def test_code_unknown_and_machine_readable_paths_run_everything(self):
        for path in ("joulewise/core.py", "tests/test_new.py", "scripts/tool.sh", "configs/x.json",
                     ".github/workflows/ci.yml", "docs/tool.py", "docs/table.json", "docs/data.csv",
                     "docs/run_reports/derived.json", "unknown.txt", "pyproject.toml", "sub/notes.md",
                     "docs/noext", "package.json"):
            with self.subTest(path=path):
                self.assertEqual(self.classify({path: "y\n"}), 1)

    def test_one_unclassifiable_path_runs_everything(self):
        self.assertEqual(self.classify({"docs/notes.md": "y\n", "docs/unknown.bin": "y\n"}), 1)

    def test_a_reference_added_in_the_range_runs_everything(self):
        self.assertEqual(self.classify({"docs/notes.md": "y\n", "tests/test_new.py": "P = 'notes.md'\n"}), 1)

    def test_a_reference_removed_in_the_range_runs_everything(self):
        self.assertEqual(self.classify({"docs/read/by_path.md": "y\n", "tests/test_reader.py": "pass\n"}), 1)

    def test_state_with_code_runs_everything(self):
        self.assertEqual(self.classify({"RUN_STATE.md": "y\n", "joulewise/core.py": "x = 2\n"}), 1)

    def test_other_process_files_run_everything(self):
        for path in ("docs/process/OTHER.json", "docs/process_traces/t/r.md", "RUN_STATE.md.bak",
                     "sub/RUN_STATE.md"):
            with self.subTest(path=path):
                self.assertEqual(self.classify({path: "y\n"}), 1)

    def test_empty_range_runs_everything(self):
        self.assertEqual(self.classify({}), 1)

    def test_malformed_sha_runs_everything(self):
        self.assertEqual(self.classify({"RUN_STATE.md": "y\n"}, before="not-a-sha"), 1)

    def test_unknown_commit_runs_everything(self):
        self.assertEqual(self.classify({"RUN_STATE.md": "y\n"}, before="0123456789" * 4), 1)

    def test_zero_sha_runs_everything(self):
        self.assertEqual(self.classify({"RUN_STATE.md": "y\n"}, before="0" * 40), 1)


class StateOnlyWorkflowTests(unittest.TestCase):
    """The workflow runs the BASE commit's classifier; a state-only range keeps the quick tier."""

    # The modules that read the live RUN_STATE.md, TASK_QUEUE.md or CURRENT.json content.
    LIVE_STATE_READERS = ("tests.test_gen_state", "tests.test_gen_current", "tests.test_docs_freshness")

    def test_workflow_wires_the_classifier_into_the_quick_job(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('git show "$before:scripts/$1" | bash -s -- "$before" "$after"', text)
        self.assertIn("elif extra=$(classify ci_state_only.sh); then", text)
        self.assertIn("state: ${{ steps.paths.outputs.state || 'false' }}", text)
        self.assertIn("extra: ${{ steps.paths.outputs.extra || '' }}", text)
        self.assertIn("run: python3 -m unittest $EXTRA_TESTS", text)
        self.assertIn("if: needs.changes.outputs.code == 'true' || needs.changes.outputs.state == 'true'\n"
                      "        run: python3 scripts/quick_suite.py --tier quick --workers 4", text)

    def test_live_state_readers_are_in_the_quick_tier(self):
        import json
        import sys
        sys.path.insert(0, str(SCRIPT.parent))
        import quick_suite
        import shard_tests
        modules = shard_tests.discover_test_modules()
        payload = json.loads(shard_tests.DEFAULT_TIMINGS_PATH.read_text(encoding="utf-8"))
        selected, excluded = quick_suite.select_modules(
            modules, shard_tests.load_timing_map(), payload.get("exclusive_modules", {}),
            shard_tests.load_split_declarations())
        for module in self.LIVE_STATE_READERS:
            with self.subTest(module=module):
                self.assertIn(module, selected, excluded.get(module))

if __name__ == "__main__":
    unittest.main()
