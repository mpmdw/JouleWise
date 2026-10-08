"""scripts/repin.py: stale Kind-P pins fail with their command; busywork does not (lane L7)."""

from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from scripts import digest_pin_census as census
from scripts import repin
from tests.test_digest_pin_census import REDUCE_SOURCE, build_tree, rows_by_path, sha

ROOT = Path(__file__).resolve().parents[1]


class MiniatureTree:
    """build_tree plus its committed registry, in a temporary directory."""

    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name)
        self.digests = build_tree(self.root)
        with redirect_stdout(io.StringIO()):
            census.main(["--write", "--root", str(self.root)])

    def path(self, relative: str) -> Path:
        return self.root / relative

    def edit(self, relative: str, old: str, new: str) -> None:
        path = self.path(relative)
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"{old!r} not in {relative}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def check(self, *names: str) -> tuple[int, str]:
        out = io.StringIO()
        code = repin.check(list(names) or ["registry"], root=self.root, runner=_never_run, out=out)
        return code, out.getvalue()

    def close(self) -> None:
        self._temporary.cleanup()


def _never_run(argv):  # the miniature tree has no generators to run
    raise AssertionError(f"unexpected subprocess {argv}")


class RegistryCheckTests(unittest.TestCase):
    def tree(self) -> MiniatureTree:
        tree = MiniatureTree()
        self.addCleanup(tree.close)
        return tree

    def test_a_current_tree_passes(self) -> None:
        tree = self.tree()
        self.assertEqual(repin.registry_stale(tree.root), ([], []))
        self.assertEqual(tree.check(), (0, "PASS 1 pin families current\n"))

    def test_tampered_pack_config_fails_with_the_pack_command(self) -> None:
        tree = self.tree()
        tree.edit("configs/campaigns/packx/run_01.json", "512", "513")
        code, out = tree.check()
        self.assertEqual(code, 1)
        self.assertIn("pin pack:packx stale: configs/campaigns/packx/plan_tree.json /members/0/config_sha256 "
                      "(pack_config_bytes) no longer carries the target's current digest", out)
        self.assertIn("run python scripts/repin.py --write pack:packx", out)
        # The fixture recorded the old digest of its era; it is never checked.
        self.assertNotIn("tests/fixtures", out)

    def test_tampered_prompt_pin_fails(self) -> None:
        tree = self.tree()
        tree.edit("configs/campaigns/packx/prompt_pin.json", "sky", "sea")
        code, out = tree.check()
        self.assertEqual(code, 1)
        self.assertIn("/prompt_pin_sha256 (pack_config_bytes)", out)
        self.assertIn("--write pack:packx", out)

    def test_tampered_acceptance_fails_and_write_refuses_to_reissue_it(self) -> None:
        tree = self.tree()
        tree.edit("configs/calibration/acceptance.json", "raw_capture_sha256", "raw_capture_sha256_x")
        code, out = tree.check()
        self.assertEqual(code, 1)
        self.assertIn("pin calibration_issued stale: configs/calibration/ledger_head.json /acceptance_sha256", out)
        self.assertIn("run python scripts/repin.py --write calibration_issued", out)
        before = tree.path("configs/calibration/ledger_head.json").read_bytes()
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(repin.write_registry_family("calibration_issued", tree.root), 1)
        self.assertIn("This pin protects a number: re-issue the artifact with its issuer", out.getvalue())
        self.assertEqual(tree.path("configs/calibration/ledger_head.json").read_bytes(), before)

    def test_core_code_edit_fails_and_is_never_auto_repinned(self) -> None:
        tree = self.tree()
        tree.edit("joulewise/reduce.py", "sum(samples)", "sum(samples) * 1.0")
        code, out = tree.check()
        self.assertEqual(code, 1)
        self.assertIn("(estimator_code) no longer carries the target's current digest [file:joulewise/reduce.py]", out)
        before = tree.path("configs/calibration/acceptance.json").read_bytes()
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(repin.write_registry_family("estimator_code", tree.root), 1)
        self.assertIn("frozen code file:joulewise/reduce.py changed", out.getvalue())
        self.assertEqual(tree.path("configs/calibration/acceptance.json").read_bytes(), before)

    def test_frozen_battery_grammar_edit_fails_and_write_refuses(self) -> None:
        tree = self.tree()
        tree.edit("joulewise/battery_float.py", "LIMIT_MA = 200", "LIMIT_MA = 250")
        code, out = tree.check()
        self.assertEqual(code, 1)
        self.assertIn("pin issued_code stale: tests/test_example.py #L2", out)
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(repin.write_registry_family("issued_code", tree.root), 1)
        self.assertIn("never from a head", out.getvalue())

    def test_test_held_copy_is_rewritten_by_one_command(self) -> None:
        tree = self.tree()
        # A legitimate plan-tree edit (its own pins stay consistent) leaves the
        # test's copy stale: one command repins it, then the check passes.
        tree.edit("configs/campaigns/packx/plan_tree.json", '"members"', '"note": "reviewed",\n  "members"')
        new_plan = sha(tree.path("configs/campaigns/packx/plan_tree.json").read_bytes())
        code, out = tree.check()
        self.assertEqual(code, 1)
        self.assertIn("pin pinned_config_copy stale: tests/test_example.py #L1", out)
        self.assertIn("run python scripts/repin.py --write pinned_config_copy", out)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(repin.write("pinned_config_copy", root=tree.root), 0)
        self.assertIn(new_plan, tree.path("tests/test_example.py").read_text())
        self.assertNotIn(tree.digests["plan"], tree.path("tests/test_example.py").read_text())
        self.assertEqual(tree.check()[0], 0)

    def test_busywork_edits_need_no_repin(self) -> None:
        tree = self.tree()
        # An unpinned validator, a synthetic literal's neighbour, a line shift.
        tree.edit("joulewise/paper_validator.py", "return value", "return value  # one-line edit")
        tree.edit("tests/test_example.py", "PLAN_TREE_SHA256", "# a new comment line\nPLAN_TREE_SHA256")
        self.assertEqual(tree.check()[0], 0)

    def test_missing_target_fails_and_missing_pinning_file_is_a_note(self) -> None:
        tree = self.tree()
        tree.path("configs/campaigns/packx/prompt_pin.json").unlink()
        tree.path("tests/test_example.py").unlink()
        code, out = tree.check()
        self.assertEqual(code, 1)
        self.assertIn("/prompt_pin_sha256 (pack_config_bytes) pinned target is missing", out)
        self.assertIn("note: pinning file tests/test_example.py is gone", out)

    def test_named_registry_family_filters_rows(self) -> None:
        tree = self.tree()
        tree.edit("configs/campaigns/packx/run_01.json", "512", "513")
        self.assertEqual(tree.check("issued_code")[0], 0)
        self.assertEqual(tree.check("pack_config_bytes")[0], 1)


class _Result:
    def __init__(self, returncode: int, stdout: str) -> None:
        self.returncode = returncode
        self.stdout = stdout


class CommandFamilyTests(unittest.TestCase):
    def test_stale_generator_fails_with_its_write_command(self) -> None:
        calls = []

        def runner(argv):
            calls.append(argv)
            return _Result(1, "checking\nFAIL generated Phase D drift: runsheet\n")

        out = io.StringIO()
        self.assertEqual(repin.check(["g2_phase_d"], runner=runner, out=out), 1)
        self.assertEqual(calls, [[sys.executable, "-B", "scripts/gen_g2_phase_d.py", "--check"]])
        self.assertEqual(out.getvalue(), "pin g2_phase_d stale: FAIL generated Phase D drift: runsheet (exit 1): "
                                         "run python scripts/repin.py --write g2_phase_d\n")

    def test_write_runs_the_generator_without_check(self) -> None:
        calls = []

        def runner(argv):
            calls.append(argv)
            return _Result(0, "updated\n")

        with redirect_stdout(io.StringIO()):
            self.assertEqual(repin.write("pack:d117_floor_qwen25_7b_v2", runner=runner), 0)
        self.assertEqual(calls, [[sys.executable, "-B", "configs/campaigns/d117_floor_qwen25_7b_v2/generate_configs.py",
                                  "--preserve-current-frozen-bytes"]])

    def test_every_pack_with_a_check_generator_is_a_family(self) -> None:
        names = repin.all_names()
        self.assertEqual(names[:3], ["g2_phase_d", "state", "paper_custody_fixture"])
        self.assertEqual(names[-1], "registry")
        for pack in repin.PACK_CHECK_ARGS:
            self.assertIn(f"pack:{pack}", names)

    def test_unknown_family_is_reported(self) -> None:
        out = io.StringIO()
        self.assertEqual(repin.check(["nope"], out=out), 1)
        self.assertIn("unknown pin family 'nope'", out.getvalue())
        with redirect_stdout(io.StringIO()):
            self.assertEqual(repin.write("nope"), 2)


ERA_PATH = "configs/campaigns/packy/sizing_source.json"
ERA_SPEC = {"commit_pointer": "/head", "scope_pointer": r"^/provenance/production/[0-9]+/source/sha256$"}


def _git(root: Path, *argv: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t",
                           "-c", "commit.gpgsign=false", *argv],
                          check=True, capture_output=True, text=True).stdout.strip()


class EraRecordTests(unittest.TestCase):
    """A document that declares its era commit is verified at that commit, not today's tree."""

    def setUp(self) -> None:
        patcher = patch.dict(census.ERA_RECORDS, {ERA_PATH: ERA_SPEC})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.tree = MiniatureTree()
        self.addCleanup(self.tree.close)
        root = self.tree.root
        _git(root, "commit", "-qm", "era")
        self.era = _git(root, "rev-parse", "HEAD")
        record = {"head": self.era, "provenance": {"production": [
            {"source": {"path": "joulewise/reduce.py", "sha256": sha(REDUCE_SOURCE)}}]}}
        self.tree.path(ERA_PATH).parent.mkdir(parents=True)
        self.tree.path(ERA_PATH).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        # The recorded core file changes after the era, as the core-prune lanes did.
        self.tree.edit("joulewise/reduce.py", "sum(samples)", "sum(samples) * 1.0")
        _git(root, "add", ".")
        _git(root, "commit", "-qm", "after the era")
        with redirect_stdout(io.StringIO()):
            census.main(["--write", "--root", str(root)])

    def rows(self) -> list:
        registry = census.load_registry(self.tree.root)
        return rows_by_path(registry)[ERA_PATH]

    def test_era_row_resolves_at_its_declared_commit_and_passes(self) -> None:
        self.assertEqual(self.rows(), [("/provenance/production/0/source/sha256", "estimator_code",
                                        f"file@{self.era}:joulewise/reduce.py")])
        self.assertEqual(self.tree.check(), (0, "PASS 1 pin families current\n"))

    def test_tampered_era_literal_fails_and_write_refuses(self) -> None:
        self.tree.edit(ERA_PATH, sha(REDUCE_SOURCE), sha(REDUCE_SOURCE + "#"))
        code, out = self.tree.check()
        self.assertEqual(code, 1)
        self.assertIn("no longer carries the target's digest at its recorded commit "
                      f"[file@{self.era}:joulewise/reduce.py]: {repin.ERA_REMEDY}", out)
        before = self.tree.path(ERA_PATH).read_bytes()
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(repin.write_registry_family("estimator_code", self.tree.root), 1)
        self.assertIn("era record of", out.getvalue())
        self.assertEqual(self.tree.path(ERA_PATH).read_bytes(), before)

    def test_moving_the_declared_commit_fails(self) -> None:
        later = _git(self.tree.root, "rev-parse", "HEAD")
        self.tree.edit(ERA_PATH, self.era, later)
        code, out = self.tree.check()
        self.assertEqual(code, 1)
        self.assertIn(f"declares era commit {later}, not the recorded one", out)
        # A regenerated registry shows the move in its diff: at the later commit
        # the recorded digest names no bytes, so the row becomes unresolved.
        with redirect_stdout(io.StringIO()):
            census.main(["--write", "--root", str(self.tree.root)])
        self.assertEqual(self.rows(), [("/provenance/production/0/source/sha256", "pack_config_bytes", None)])

    def test_declared_commit_outside_history_fails_check_and_refuses_the_census(self) -> None:
        self.tree.edit(ERA_PATH, self.era, "0" * 40)
        code, out = self.tree.check()
        self.assertEqual(code, 1)
        self.assertIn("declares era commit unreadable", out)
        with self.assertRaises(census.EraRecordError):
            census.census(self.tree.root)


class RealTreeTests(unittest.TestCase):
    def test_committed_registry_kind_p_rows_are_current(self) -> None:
        stale, warnings = repin.registry_stale(ROOT)
        self.assertEqual([(row.path, row.pointer, row.reason) for row in stale], [])
        self.assertEqual(warnings, [])

    def test_real_generator_families_pass(self) -> None:
        out = io.StringIO()
        self.assertEqual(repin.check(["paper_custody_fixture", "g2_phase_d", "pack:d117_floor_qwen3-8b_v5"],
                                     out=out), 0, out.getvalue())

    def test_cli_subcommand_aliases(self) -> None:
        result = subprocess.run([sys.executable, "-B", "scripts/repin.py", "check", "paper_custody_fixture"],
                                cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "PASS 1 pin families current\n")
        listing = subprocess.run([sys.executable, "-B", "scripts/repin.py", "--list"], cwd=ROOT,
                                 capture_output=True, text=True, check=True).stdout
        self.assertIn("registry: Kind-P rows of configs/pins/registry.json", listing)

    def test_ci_runs_the_repin_check(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("run: python scripts/repin.py --check", workflow)


if __name__ == "__main__":
    unittest.main()
