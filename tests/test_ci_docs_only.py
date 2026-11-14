"""The CI range classifiers: docs-only (scripts/ci_docs_only.sh) suppresses tests only for
unreferenced Markdown; targeted-docs (scripts/ci_docs_targeted.sh) also admits docs/assets images and
narrows referenced docs to the test modules that name them; state-only (scripts/ci_state_only.sh) admits only the state records."""
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from tests.git_fixture import init_git_fixture

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ci_docs_only.sh"
TARGETED_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ci_docs_targeted.sh"
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


class TargetedDocsClassifierTests(unittest.TestCase):
    """scripts/ci_docs_targeted.sh: exit 1 = full suite; exit 0 prints docs-only or targeted <modules>."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        init_git_fixture(self.repo, "-q")
        self.write({
            "README.md": "x\n", "docs/notes.md": "x\n", "docs/guide.md": "x\n", "docs/two.md": "x\n",
            "docs/helped.md": "x\n", "docs/scripted.md": "x\n", "docs/assets/readme/fig.svg": "<svg/>\n",
            "docs/assets/readme/used.png": "x\n", "assets/logo.svg": "<svg/>\n", "docs/site/s.md": "x\n",
            "tests/test_guide.py": "PATH = 'docs/guide.md'\n",
            "tests/test_two_a.py": "PATH = 'docs/two.md'\n",
            "tests/sub/test_two_b.py": "PATH = 'docs/two.md'\n",
            "tests/test_img.py": "PATH = 'docs/assets/readme/used.png'\n",
            "tests/helpers.py": "PATH = 'docs/helped.md'\n",
            "scripts/tool.py": "PATH = 'docs/scripted.md'\n",
            "joulewise/core.py": "x = 1\n",
            "docs/process/BUILT.md": "x\n", "scripts/watch.py": "P = ROOT / 'docs' / 'process' / 'BUILT.md'\n",
            "docs/BASE.md": "x\n", "tests/test_base.py": "P = ROOT / 'docs' / 'BASE.md'\n",
            "docs/CODE.md": "x\n", "docs/analysis/reader.py": "P = 'CODE.md'\n",
            "docs/a*[x].md": "x\n", "scripts/glob.sh": "cat 'docs/a*[x].md'\n",
            "docs/bad.md": "x\n", "tests/test_$(id).py": "P = 'docs/bad.md'\n",
            "docs/dot.md": "x\n", "tests/x.py/test_y.py": "P = 'docs/dot.md'\n",
            "docs/pydir.md": "x\n", "tests/py/test_z.py": "P = 'docs/pydir.md'\n"})
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
        done = subprocess.run(["bash", str(TARGETED_SCRIPT), before or self.base, after], cwd=self.repo,
                              env=self.env, capture_output=True, text=True)
        return done.returncode, done.stdout.strip()

    def test_unreferenced_markdown_is_docs_only(self):
        self.assertEqual(self.classify({"docs/notes.md": "y\n"}), (0, "docs-only"))

    def test_markdown_referenced_by_one_test_module_is_targeted(self):
        self.assertEqual(self.classify({"docs/guide.md": "y\n"}), (0, "targeted tests.test_guide"))

    def test_modules_from_several_files_and_subdirectories_are_sorted_and_unique(self):
        self.assertEqual(self.classify({"docs/two.md": "y\n", "docs/guide.md": "y\n"}),
                         (0, "targeted tests.sub.test_two_b tests.test_guide tests.test_two_a"))

    def test_markdown_referenced_by_a_test_helper_is_full(self):
        self.assertEqual(self.classify({"docs/helped.md": "y\n"}), (1, ""))

    def test_markdown_referenced_from_scripts_is_full(self):
        self.assertEqual(self.classify({"docs/scripted.md": "y\n"}), (1, ""))

    def test_one_helper_reference_makes_a_targeted_range_full(self):
        self.assertEqual(self.classify({"docs/guide.md": "y\n", "docs/helped.md": "y\n"}), (1, ""))

    def test_python_file_in_the_range_is_full_even_when_it_is_the_referencing_test(self):
        # The referencing test is edited by the range itself: the diff has a .py path, so full.
        self.assertEqual(self.classify({"docs/guide.md": "y\n", "tests/test_guide.py": "x = 1\n"}), (1, ""))

    def test_unreferenced_image_under_docs_assets_is_docs_only(self):
        self.assertEqual(self.classify({"docs/assets/readme/fig.svg": "<svg>y</svg>\n"}), (0, "docs-only"))

    def test_every_image_extension_is_a_docs_path(self):
        for ext in ("svg", "png", "jpg", "jpeg", "webp", "gif"):
            with self.subTest(ext=ext):
                self.assertEqual(self.classify({f"docs/assets/new.{ext}": "y\n"}), (0, "docs-only"))

    def test_image_referenced_by_a_test_module_is_targeted(self):
        self.assertEqual(self.classify({"docs/assets/readme/used.png": "y\n"}), (0, "targeted tests.test_img"))

    def test_image_outside_docs_assets_is_full(self):
        for path in ("assets/logo.svg", "docs/logo.svg", "docs/other/logo.png"):
            with self.subTest(path=path):
                self.assertEqual(self.classify({path: "y\n"}), (1, ""))

    def test_other_extension_under_docs_assets_is_full(self):
        self.assertEqual(self.classify({"docs/assets/data.json": "{}\n"}), (1, ""))

    def test_glob_read_docs_directories_are_full(self):
        for path in ("docs/registrations/b9.md", "docs/contracts/c.md", "docs/process_traces/t/r.md",
                     "docs/null/n.md", "docs/site/s.md", "docs/site/img.svg"):
            with self.subTest(path=path):
                self.assertEqual(self.classify({path: "y\n"}), (1, ""))

    def test_mixed_range_with_python_is_full(self):
        self.assertEqual(self.classify({"docs/notes.md": "y\n", "joulewise/core.py": "x = 2\n"}), (1, ""))

    def test_markdown_outside_docs_and_root_is_full(self):
        self.assertEqual(self.classify({"configs/plan.md": "y\n"}), (1, ""))

    def test_empty_range_is_full(self):
        self.assertEqual(self.classify({}), (1, ""))

    def test_malformed_unknown_and_zero_shas_are_full(self):
        for before in ("not-a-sha", "0123456789" * 4, "0" * 40):
            with self.subTest(before=before):
                self.assertEqual(self.classify({"docs/notes.md": "y\n"}, before=before), (1, ""))

    def test_reader_that_builds_the_path_in_code_is_found_by_basename(self):
        self.assertEqual(self.classify({"docs/process/BUILT.md": "y\n"}), (1, ""))

    def test_basename_hit_in_a_test_module_joins_the_targeted_set(self):
        self.assertEqual(self.classify({"docs/BASE.md": "y\n"}), (0, "targeted tests.test_base"))

    def test_python_under_docs_that_names_the_doc_is_full(self):
        self.assertEqual(self.classify({"docs/CODE.md": "y\n"}), (1, ""))

    def test_invalid_test_module_name_is_full(self):
        self.assertEqual(self.classify({"docs/bad.md": "y\n"}), (1, ""))

    def test_dotted_directory_or_py_component_in_the_module_path_is_full(self):
        for path in ("docs/dot.md", "docs/pydir.md"):
            with self.subTest(path=path):
                self.assertEqual(self.classify({path: "y\n"}), (1, ""))

    def test_path_with_glob_characters_is_matched_as_a_fixed_string(self):
        self.assertEqual(self.classify({"docs/a*[x].md": "y\n"}), (1, ""))

    def test_symlink_named_like_a_doc_is_full(self):
        self.git("checkout", "-q", self.base)
        (self.repo / "docs" / "link.md").symlink_to("notes.md")
        after = self.commit()
        done = subprocess.run(["bash", str(TARGETED_SCRIPT), self.base, after], cwd=self.repo, env=self.env,
                              capture_output=True, text=True)
        self.assertEqual((done.returncode, done.stdout.strip()), (1, ""))

    def test_symlink_replaced_by_a_regular_doc_is_full(self):
        # The guard reads the mode on both sides: a symlink before the range is refused too.
        self.git("checkout", "-q", self.base)
        (self.repo / "docs" / "flip.md").symlink_to("notes.md")
        before = self.commit()
        (self.repo / "docs" / "flip.md").unlink()
        (self.repo / "docs" / "flip.md").write_text("now a regular file\n", encoding="utf-8")
        after = self.commit()
        done = subprocess.run(["bash", str(TARGETED_SCRIPT), before, after], cwd=self.repo, env=self.env,
                              capture_output=True, text=True)
        self.assertEqual((done.returncode, done.stdout.strip()), (1, ""))

    def test_gitlink_named_like_a_doc_is_full(self):
        self.git("checkout", "-q", self.base)
        self.git("update-index", "--add", "--cacheinfo", "160000," + self.base + ",docs/sub.md")
        self.git("commit", "-q", "-m", "gitlink")
        after = self.git("rev-parse", "HEAD")
        done = subprocess.run(["bash", str(TARGETED_SCRIPT), self.base, after], cwd=self.repo, env=self.env,
                              capture_output=True, text=True)
        self.assertEqual((done.returncode, done.stdout.strip()), (1, ""))

    def test_docs_only_script_contract_is_unchanged_for_referenced_markdown(self):
        self.git("checkout", "-q", self.base)
        self.write({"docs/guide.md": "y\n"})
        after = self.commit()
        rc = subprocess.run(["bash", str(SCRIPT), self.base, after], cwd=self.repo, env=self.env).returncode
        self.assertEqual(rc, 1)


class TargetedDocsWorkflowTests(unittest.TestCase):
    def text(self):
        return WORKFLOW.read_text(encoding="utf-8")

    def job(self, name):
        text = self.text()
        start = text.index(f"\n  {name}:\n")
        rest = text[start + 1:]
        end = rest.find("\n  # ", 1)
        nxt = [i for i in (rest.find("\n  " + m + ":\n", 1) for m in ("changes", "fences", "test", "build"))
               if i > 0]
        return rest[:min(nxt + ([end] if end > 0 else []))]

    def test_workflow_wires_the_targeted_lane(self):
        text = self.text()
        self.assertIn("elif verdict=$(classify ci_docs_targeted.sh); then", text)
        self.assertIn("targeted: ${{ steps.paths.outputs.targeted || '' }}", text)

    def test_targeted_modules_run_inside_the_required_quick_job_and_fail_it(self):
        text = self.text()
        self.assertNotIn("docs-targeted", text)
        quick = self.job("quick")
        self.assertIn("      - name: Targeted docs test modules\n        if: needs.changes.outputs.targeted != ''\n",
                      quick)
        self.assertIn("run: python -m unittest -v $TARGETED_MODULES", quick)
        self.assertNotIn("continue-on-error", quick)
        self.assertNotIn("|| true", quick)
        self.assertNotIn("TARGETED_MODULES || ", quick)

    def test_quick_job_is_not_skipped_by_the_targeted_verdict(self):
        quick = self.job("quick")
        skip = quick.split("      - uses: actions/checkout@v5", 1)[0]
        self.assertIn("&& needs.changes.outputs.targeted == ''", skip)
        for step in ("actions/checkout@v5", "actions/setup-python@v6", "Install zsh"):
            index = quick.index(step)
            self.assertIn("|| needs.changes.outputs.targeted != ''", quick[index:index + 400].split("run:")[0]
                          if "run:" in quick[index:index + 400] else quick[index:index + 400], step)
        self.assertNotIn("needs: [changes]\n    if:", quick)
        self.assertNotIn("\n    if:", quick)

    def paths_block(self):
        text = self.text()
        return text.split("      - name: Detect code changes\n", 1)[1].split("\n\n", 1)[0]

    def test_changes_job_sets_code_false_only_with_a_verdict_and_exports_targeted(self):
        block = self.paths_block()
        self.assertEqual(block.count("code=false"), 4, block)
        self.assertIn("printf 'code=%s\\nstate=%s\\ntargeted=%s\\n' \"$code\" \"$state\" \"$targeted\" >> \"$GITHUB_OUTPUT\"",
                      block)
        # The targeted verdict branch sets code=false and targeted together, behind the regex.
        self.assertIn("code=false; targeted=${verdict#targeted }", block)
        self.assertIn("docs-only) code=false ;;", block)
        self.assertIn("code=true; state=false; targeted=\n", block)

    def verdict_snippet(self):
        block = self.paths_block()
        start = block.index('            case "$verdict" in')
        end = block.index("            esac", start) + len("            esac")
        return textwrap.dedent(block[start:end])

    def simulate(self, verdict):
        script = ('verdict=$1; code=true; targeted=\n' + self.verdict_snippet()
                  + '\nprintf "%s|%s" "$code" "$targeted"\n')
        return subprocess.run(["bash", "-c", script, "sim", verdict], capture_output=True, text=True).stdout

    def test_hostile_or_malformed_verdicts_keep_the_full_suite(self):
        for verdict in ("targeted tests.test_$(id)", "targeted tests.test_a;id", "targeted tests.test_a ",
                        "targeted tests.test_a\ntargeted=evil", "targeted tests.test_a\n", "targeted tests..x",
                        "targeted tests.x.py.test_y", "targeted tests.py", "targeted tests.test_a  tests.test_b",
                        "targeted tests.", "targeted", "docs-only ", "", "targeted tests.test_a tests.py.b"):
            with self.subTest(verdict=verdict):
                self.assertEqual(self.simulate(verdict), "true|")

    def test_good_verdicts_are_accepted(self):
        self.assertEqual(self.simulate("docs-only"), "false|")
        self.assertEqual(self.simulate("targeted tests.test_a tests.sub.test_b"),
                         "false|tests.test_a tests.sub.test_b")
        self.assertEqual(self.simulate("targeted tests.test_py_x"), "false|tests.test_py_x")


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
    """The workflow runs the BASE commit's classifier; a state-only range keeps the quick tier."""

    # The modules that read the live RUN_STATE.md, TASK_QUEUE.md or CURRENT.json content.
    LIVE_STATE_READERS = ("tests.test_gen_state", "tests.test_gen_current", "tests.test_docs_freshness")

    def test_workflow_wires_the_classifier_into_the_quick_job(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('git show "$before:scripts/$1" | bash -s -- "$before" "$after"', text)
        self.assertIn("elif classify ci_state_only.sh; then", text)
        self.assertIn("state: ${{ steps.paths.outputs.state || 'false' }}", text)
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
