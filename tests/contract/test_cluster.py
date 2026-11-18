"""Collect the shared integration contract on main."""

import importlib
from pathlib import Path
import re
import sys
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from tests.contract import cluster
from tests.contract.cluster import ClusterScenarios, MAIN_CASES, SOURCE, _offload_sources

MEMBER_FILES = sorted(Path(__file__).parent.glob("test_cluster_[0-9]*.py"))


class TestClusterMain(ClusterScenarios, unittest.TestCase):
    # A member leaf owns collection of the activated cross-PR scenarios.
    select_main = bool(MEMBER_FILES)


def _scenario_ids(suite):
    ids = set()
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            ids.update(_scenario_ids(test))
        elif isinstance(test, ClusterScenarios):
            method = test.id().rsplit(".", 1)[-1]
            ids.add(method.removeprefix("test_").replace("_", "-"))
    return ids


def _check_scenario_collection(main_suite, member_suites, contract_ids):
    main_ids = _scenario_ids(main_suite)
    expected_main = MAIN_CASES if member_suites else contract_ids
    collected = set(main_ids)
    for suite in member_suites.values():
        collected.update(_scenario_ids(suite))
    if collected != contract_ids:
        raise AssertionError(f"cluster collection differs from contract: "
                             f"missing {sorted(contract_ids - collected)}, "
                             f"unexpected {sorted(collected - contract_ids)}")
    if main_ids != expected_main:
        raise AssertionError("main collected a different scenario set from its contract assignment")
    for name, suite in member_suites.items():
        ids = _scenario_ids(suite)
        expected = contract_ids - MAIN_CASES
        if ids != expected:
            raise AssertionError(f"{name}: missing {sorted(expected - ids)}, "
                                 f"unexpected {sorted(ids - expected)}")


def load_tests(loader, standard_tests, pattern):
    contract = (SOURCE / "docs/ops/cluster_contract.md").read_text(encoding="utf-8")
    scenarios = contract.split("### 3.2 Scenarios", 1)[1].split("\n## 4.", 1)[0]
    ids = set(re.findall(r"^\| ([A-Z][0-9]*-[A-Z]?[0-9]+) \|", scenarios, re.MULTILINE))
    # Validate the real unittest collection, including a member's load_tests.
    # A user's focused -k selection can still run after the inventory check.
    inventory = unittest.TestLoader()
    members = {
        path.name: inventory.loadTestsFromModule(
            importlib.import_module(f"{__package__}.{path.stem}" if __package__ else path.stem),
            pattern=pattern)
        for path in MEMBER_FILES
    }
    if inventory.errors:
        raise AssertionError("\n".join(inventory.errors))
    main = inventory.loadTestsFromTestCase(TestClusterMain) if loader.testNamePatterns else standard_tests
    _check_scenario_collection(main, members, ids)
    return standard_tests


class TestClusterInventory(unittest.TestCase):
    def test_at_most_one_offload_source(self):
        sources = _offload_sources()
        self.assertTrue(not sources or sources == ["joulewise/span_offload.py"], sources)

    def test_partial_member_collection_fails(self):
        main = unittest.TestSuite(
            TestClusterMain(name) for name in ("test_A_09", "test_A_12"))
        ids = MAIN_CASES | {"X-17", "X-18"}

        class Member(ClusterScenarios, unittest.TestCase):
            required_ports = ("D",)

        complete = unittest.TestSuite([Member("test_X_17"), Member("test_X_18")])
        for incomplete in (unittest.TestSuite(), unittest.TestSuite([Member("test_X_17")])):
            with self.assertRaisesRegex(AssertionError, "test_cluster_799.py: missing"):
                _check_scenario_collection(main, {"good": complete, "test_cluster_799.py": incomplete}, ids)


class TestClusterBoundary(unittest.TestCase):
    def test_close_uses_fixture_roots(self):
        with ExitStack() as stack:
            world = cluster.World(self, stack, cluster.FixtureHooks(), {"C": None})
            with patch.object(world, "process", return_value=cluster.Result(0, "", "")):
                world.close(world.span())
            argv, _ = world.close_call()
            for flag, path in (("--campaign-root", world.campaign),
                               ("--work-root", world.worktrees),
                               ("--fence", world.host / cluster.fence.FENCE_NAME)):
                self.assertEqual(argv[argv.index(flag) + 1], str(path))

    def test_worker_checkpoints_and_boundary_violation(self):
        with ExitStack() as stack:
            world = cluster.World(self, stack, cluster.FixtureHooks(), {})
            script = world.root / "close_offload.py"
            script.write_text("""\
import os
import subprocess
import sys
import time
from joulewise import durable
from tests.contract.cluster import Boundary, REAL_MONOTONIC

if "--_worker" in sys.argv:
    assert isinstance(time.time.__self__, Boundary)
    assert isinstance(time.monotonic.__self__, Boundary)
    assert isinstance(os.killpg.__self__, Boundary)
    durable.checkpoint("contract.worker")
    if "--escape" in sys.argv:
        try:
            REAL_MONOTONIC()
        except AssertionError:
            pass
else:
    durable.checkpoint("contract.supervisor")
    proc = subprocess.Popen([sys.executable, "-B", __file__, *sys.argv[1:], "--_worker"],
                            start_new_session=True)
    raise SystemExit(proc.wait())
""", encoding="utf-8")
            for args in ([], ["--escape"]):
                with self.subTest(args=args):
                    work = world.root / f"invocation-{len(args)}"
                    work.mkdir()
                    argv = cluster._child_argv(script, world.controls, work, args)
                    if args:
                        with self.assertRaisesRegex(AssertionError, "monotonic"):
                            world.process(argv, work)
                    else:
                        self.assertEqual(world.process(argv, work).code, 0)
            self.assertEqual(world.checkpoints, ["contract.supervisor", "contract.worker"] * 2)

    def test_argparse_failure_is_not_duplicate_pointer_xfail(self):
        original = cluster.gen_current.main

        def bad_argv(argv):
            return original([*argv, "--invalid-contract-test-option"])

        result = unittest.TestResult()
        with patch.object(cluster.gen_current, "main", bad_argv), patch("sys.stderr"):
            TestClusterMain("test_A_12").run(result)
        self.assertFalse(result.expectedFailures)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("SystemExit: 2", result.errors[0][1])

    def test_preflight_requires_the_check_diagnostic(self):
        def invoke(world, name):
            return cluster.Result(2, "", f"[Errno 2] No such file: {world.root / field[-1]}")

        field = []
        hooks = cluster.FixtureHooks(
            prepare=lambda world, **inputs: field.append(inputs["bad_preflight"][0]), invoke=invoke)
        with ExitStack() as stack:
            test = unittest.TestCase()
            world = cluster.World(test, stack, hooks, {})
            with self.assertRaisesRegex(AssertionError, "PREFLIGHT: missing offload_config"):
                cluster._preflight(test, world)
