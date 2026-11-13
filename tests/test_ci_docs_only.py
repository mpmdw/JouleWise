"""The CI range classifiers: docs-only (scripts/ci_docs_only.sh) suppresses tests only for
unreferenced Markdown; state-only (scripts/ci_state_only.sh) admits only the state records."""
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
        for path in ("docs/registrations/b9.md", "docs/contracts/c.md", "docs/process_traces/t/r.md",
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
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        init_git_fixture(self.repo, "-q")
        self.write({"RUN_STATE.md": "x\n", "TASK_QUEUE.md": "x\n", "docs/process/CURRENT.json": "{}\n",
                    "docs/notes.md": "x\n", "joulewise/core.py": "x = 1\n"})
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
        return subprocess.run(["bash", str(STATE_SCRIPT), before or self.base, after], cwd=self.repo,
                              env=self.env).returncode

    def test_run_state_alone_is_state_only(self):
        self.assertEqual(self.classify({"RUN_STATE.md": "y\n"}), 0)

    def test_run_state_with_generated_current_pointer_is_state_only(self):
        self.assertEqual(self.classify({"RUN_STATE.md": "y\n", "docs/process/CURRENT.json": "{\"a\": 1}\n"}), 0)

    def test_task_queue_is_state_only(self):
        self.assertEqual(self.classify({"TASK_QUEUE.md": "y\n"}), 0)

    def test_state_with_docs_runs_everything(self):
        self.assertEqual(self.classify({"RUN_STATE.md": "y\n", "docs/notes.md": "y\n"}), 1)

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
    """The workflow runs the BASE commit's classifier and gives state-only ranges the touched tier."""

    def test_workflow_wires_the_classifier_and_the_touched_tier(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('git show "$before:scripts/$1" | bash -s -- "$before" "$after"', text)
        self.assertIn("elif classify ci_state_only.sh; then", text)
        self.assertIn('quick_suite.py --tier touched --since "$BASE_SHA"', text)
        self.assertIn("state: ${{ steps.paths.outputs.state || 'false' }}", text)


if __name__ == "__main__":
    unittest.main()
