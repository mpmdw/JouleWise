"""Selection, dependency mapping, and isolated shard-runner regressions."""

import contextlib
from concurrent.futures import Future
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import quick_suite as quick
from scripts import shard_tests
from tests.git_fixture import init_git_fixture


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.weights = {"tests.test_fast": 0.1, "tests.test_boundary": 5.0,
                        "tests.test_heavy": 10.0, "tests.test_exclusive": 0.2,
                        "tests.test_split": 0.3, quick.DOCS_MODULE: 99.0}
        self.modules = (*self.weights, "tests.test_unknown")

    def select(self, **kwargs):
        return quick.select_modules(self.modules, self.weights,
                                    {"tests.test_exclusive"}, {"tests.test_split"},
                                    **kwargs)

    def test_threshold_is_strict_and_fence_is_mandatory(self):
        selected, excluded = self.select()
        self.assertEqual(set(selected), {"tests.test_fast", quick.DOCS_MODULE})
        self.assertIn("weight=5.000s >= 5s", excluded["tests.test_boundary"])
        selected, _ = self.select(max_seconds=6)
        self.assertIn("tests.test_boundary", selected)
        self.assertNotIn("tests.test_heavy", selected)

    def test_exclusive_and_split_excluded_even_below_threshold(self):
        selected, excluded = self.select(max_seconds=100)
        self.assertNotIn("tests.test_exclusive", selected)
        self.assertNotIn("tests.test_split", selected)
        self.assertEqual(excluded["tests.test_exclusive"], "exclusive")
        self.assertEqual(excluded["tests.test_split"], "split")

    def test_unknown_is_listed_and_always_included_in_touched(self):
        _, excluded = self.select()
        self.assertEqual(excluded["tests.test_unknown"], "unknown weight")
        selected, excluded = self.select(tier="touched")
        self.assertEqual(selected["tests.test_unknown"], "unknown weight")
        self.assertNotIn("tests.test_unknown", excluded)

    def test_touched_adds_related_heavy_exclusive_and_split(self):
        related = {"tests.test_heavy", "tests.test_split", "tests.test_exclusive"}
        selected, excluded = self.select(tier="touched", touched=related)
        self.assertTrue(related <= selected.keys())
        self.assertIn("tests.test_boundary", excluded)

    def test_every_discovered_module_has_exactly_one_disposition(self):
        for tier in ("quick", "touched"):
            selected, excluded = self.select(tier=tier)
            self.assertFalse(selected.keys() & excluded.keys())
            self.assertEqual(selected.keys() | excluded.keys(), set(self.modules))

    def test_a211_denied_even_when_cheap_touched_or_unknown(self):
        denied = {
            "tests.test_paper_round7_artifacts", "tests.test_admit_model_panel_entry",
            "tests.test_rpt001_report_slice", "tests.test_floor_extraction",
            "tests.test_run_campaign",
        }
        self.assertEqual(quick.CANONICAL_PATH_MODULES, denied)
        for tier in ("quick", "touched"):
            for weights in ({name: 0.1 for name in denied}, {}):
                with self.subTest(tier=tier, weights=weights):
                    selected, excluded = quick.select_modules(
                        denied, weights, {}, {}, tier=tier, touched=denied,
                    )
                    self.assertEqual(selected, {})
                    self.assertEqual(set(excluded), denied)
                    self.assertTrue(all("A211" in reason for reason in excluded.values()))


class TouchedTests(unittest.TestCase):
    def test_maps_names_prefixes_imports_literal_paths_and_direct_test_edits(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            root = Path(tmp)
            sources = {
                "tests.test_energy_extra": "# prefix match\n",
                "tests.test_generator_variants": "# script prefix\n",
                "tests.test_consumer": "from joulewise import energy\n",
                "tests.test_script_consumer": "# generator compatibility\n",
                "tests.test_doc": "PATH = 'docs/contract.md'\n",
                "tests.test_direct": "# changed test itself\n",
                "tests.test_unrelated": "# unrelated\n",
            }
            for module, source in sources.items():
                path = root / (module.replace(".", "/") + ".py")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source, encoding="utf-8")
            selected = quick.touched_modules(
                sources, ("joulewise/energy.py", "scripts/generator.py",
                          "docs/contract.md", "tests/test_direct.py"), root,
            )
            self.assertEqual(selected, sources.keys() - {"tests.test_unrelated"})

    def test_git_mapping_includes_worktree_index_untracked_and_deleted_paths(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            root = Path(tmp)

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root,
                                               stderr=subprocess.STDOUT)

            init_git_fixture(root, "-q")
            for name in ("deleted.py", "staged.py", "worktree.py", "committed.py"):
                (root / name).write_text("before\n")
            git("add", ".")
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "-c", "commit.gpgsign=false", "commit", "-qm", "base")
            (root / "committed.py").write_text("after\n")
            git("add", "committed.py")
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "-c", "commit.gpgsign=false", "commit", "-qm", "next")
            (root / "deleted.py").unlink()
            (root / "staged.py").write_text("after\n")
            git("add", "staged.py")
            (root / "worktree.py").write_text("after\n")
            (root / "new space.py").write_text("new\n")
            self.assertEqual(set(quick.changed_paths("HEAD~1", root)),
                             {"deleted.py", "staged.py", "worktree.py",
                              "committed.py", "new space.py"})


class RunnerTests(unittest.TestCase):
    def test_a211_single_module_replay_cannot_bypass_guard(self):
        for module in quick.CANONICAL_PATH_MODULES:
            with (self.subTest(module=module),
                  mock.patch.object(quick, "run_command") as run,
                  contextlib.redirect_stderr(io.StringIO()) as output):
                with self.assertRaises(SystemExit) as raised:
                    quick.main(["--module", module])
                self.assertEqual(raised.exception.code, 2)
                self.assertIn("A211", output.getvalue())
                run.assert_not_called()

    def test_stale_weight_reports_strict_threefold_boundary_for_pass_and_fail(self):
        for code in (0, 1):
            for seconds, weight, stale in ((3.0, 1.0, False), (3.001, 1.0, True),
                                           (30.0, None, False)):
                with self.subTest(code=code, seconds=seconds, weight=weight):
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        quick.report(quick.Result("tests.test_sample", code, seconds,
                                                  "detail\n", "replay"), weight)
                    self.assertEqual("STALE WEIGHT" in output.getvalue(), stale)

    def test_tier_aggregates_failure_and_runs_each_selected_module_once(self):
        calls = []

        def run(name, command, rerun):
            calls.append(name)
            return quick.Result(name, int(name == "tests.test_broken"), 0.1,
                                "failure detail\n", rerun)

        def submit(fn, *args):
            future = Future()
            future.set_result(fn(*args))
            return future

        weights = {quick.DOCS_MODULE: 0.1, "tests.test_broken": 0.2,
                   "tests.test_heavy": 20.0}
        output = io.StringIO()
        with (mock.patch.object(shard_tests, "discover_test_modules", return_value=tuple(weights)),
              mock.patch.object(shard_tests, "load_timing_map", return_value=weights),
              mock.patch.object(shard_tests, "load_split_declarations", return_value={}),
              mock.patch.object(quick, "run_command", side_effect=run),
              mock.patch.object(quick, "ProcessPoolExecutor") as pool,
              contextlib.redirect_stdout(output)):
            pool.return_value.__enter__.return_value.submit.side_effect = submit
            self.assertEqual(quick.main([]), 1)
        self.assertEqual(calls, ["gen_state", quick.DOCS_MODULE, "tests.test_broken"])
        self.assertIn("EXCLUDE tests.test_heavy:", output.getvalue())
        self.assertIn("RERUN ", output.getvalue())
        self.assertRegex(output.getvalue().splitlines()[-1],
                         r"^QUICK SUMMARY tier=quick modules=2 excluded=1 failures=1 .* result=FAIL$")

    def test_module_command_calls_shard_runner_without_reimplementing_loader(self):
        module, command, rerun = quick.module_job("tests.test_example")
        self.assertEqual(command[:2], [sys.executable, "-c"])
        with mock.patch.object(shard_tests, "run_shard", return_value=7) as runner:
            with mock.patch.object(sys, "argv", ["-c", module]):
                with self.assertRaises(SystemExit) as raised:
                    exec(command[2], {})
        runner.assert_called_once_with((module,), 1, 1)
        self.assertEqual(raised.exception.code, 7)
        self.assertIn("--module tests.test_example", rerun)

    def test_child_tmpdir_outside_repo_despite_inherited_tmpdir(self):
        code = ("import os, pathlib, tempfile; "
                "p=pathlib.Path(tempfile.gettempdir()).resolve(); "
                "assert not p.is_relative_to(pathlib.Path.cwd()); "
                "assert all(os.environ[k] == str(p) for k in ('TMPDIR','TEMP','TMP')); "
                "assert pathlib.Path(os.environ['JOULEWISE_CUSTODY_PARENT']).is_relative_to(p); "
                "assert os.environ['JOULEWISE_ADDITIONAL_CUSTODY_PARENTS'] == '[]'; "
                "assert pathlib.Path(os.environ['R7F_CORPUS_ROOT']) == pathlib.Path.cwd(); "
                "print('isolated')")
        with mock.patch.dict(os.environ, {"TMPDIR": str(quick.ROOT)}):
            result = quick.run_command("probe", [sys.executable, "-c", code], "replay")
        self.assertEqual(result.returncode, 0, result.output)
        self.assertEqual(result.output, "isolated\n")

    def test_failure_keeps_diagnostics_seconds_and_replay_command(self):
        result = quick.run_command("broken", [sys.executable, "-c",
                                              "print('diagnostic'); exit(3)"], "replay")
        self.assertEqual(result.returncode, 3)
        self.assertGreater(result.seconds, 0)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            quick.report(result)
        self.assertIn("FAIL broken seconds=", output.getvalue())
        self.assertIn("diagnostic", output.getvalue())
        self.assertIn("RERUN replay", output.getvalue())

    def test_missing_touched_base_and_invalid_limits_are_rejected(self):
        for args in (["--tier", "touched"], ["--workers", "0"],
                     ["--max-seconds", "nan"], ["--max-seconds", "0"]):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    quick.main(args)
                self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
