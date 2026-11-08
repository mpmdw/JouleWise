"""Correctness invariants for the module-atomic unittest shard runner."""

from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = ROOT / "tests"
sys.path.insert(0, os.fspath(ROOT / "scripts"))

import shard_tests  # noqa: E402


def _suite_modules(suite) -> set[str]:
    modules = set()
    stack = [suite]
    while stack:
        item = stack.pop()
        if isinstance(item, unittest.TestSuite):
            stack.extend(item)
            continue
        module = item.__class__.__module__
        if module.startswith(("test_", "align.")):
            module = f"tests.{module}"
        modules.add(module)
    return modules


def _unittest_discover_module_set() -> set[str]:
    """Inspect unittest's discovered suite without executing any test."""

    old_path = list(sys.path)
    try:
        loader = unittest.TestLoader()
        suite = loader.discover(os.fspath(TESTS_DIR))
    finally:
        sys.path[:] = old_path
    if loader.errors:
        raise AssertionError(f"unittest discovery errors: {loader.errors}")
    return _qualified(_suite_modules(suite))


def _qualified(modules) -> set[str]:
    """``discover -s tests`` names modules relative to tests/, including any
    nested package; the shard manifest names all of them relative to ROOT."""
    return {m if m.startswith("tests.") else f"tests.{m}" for m in modules}


UNTIMED_ALLOWANCE_KEY = "untimed_module_allowance"


def _untimed_allowance_rules(payload) -> dict[str, dict]:
    """Validate and return the timing map's ``untimed_module_allowance`` rules.

    Each non-``_`` key is a module-name prefix (``tests.align.`` covers that
    package; ``tests.test_qwen4`` covers top-level modules with that stem).
    A rule carries ``max_source_bytes`` and a nonempty ``reason``.
    """

    block = payload.get(UNTIMED_ALLOWANCE_KEY, {})
    if not isinstance(block, dict):
        raise AssertionError(f"{UNTIMED_ALLOWANCE_KEY} must be a JSON object")
    rules = {}
    for prefix, rule in block.items():
        if prefix.startswith("_"):
            continue
        if not prefix.startswith("tests.") or len(prefix) <= len("tests."):
            raise AssertionError(f"allowance prefix {prefix!r} must name tests.<something>")
        if not isinstance(rule, dict):
            raise AssertionError(f"allowance for {prefix!r} must be a JSON object")
        limit = rule.get("max_source_bytes")
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise AssertionError(f"allowance for {prefix!r} needs a positive max_source_bytes")
        reason = rule.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise AssertionError(f"allowance for {prefix!r} needs a nonempty reason")
        rules[prefix] = rule
    return rules


def _untimed_allowance_violations(modules, timings, exemptions, rules, root: Path):
    """Return discovered modules with no weight that no allowance covers.

    A module without a weight is packed at ``unknown_module_weight_seconds``.
    That is acceptable only for a module under an allowed prefix whose source
    file is no larger than the rule's ``max_source_bytes``; everything else
    needs a measured weight or a documented exemption.
    """

    violations = set()
    for module in set(modules) - set(timings) - set(exemptions):
        source = root.joinpath(*module.split(".")).with_suffix(".py")
        if not any(
            module.startswith(prefix)
            and source.stat().st_size <= rule["max_source_bytes"]
            for prefix, rule in rules.items()
        ):
            violations.add(module)
    return violations


class ShardPartitionInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = shard_tests.discover_test_modules()
        cls.timings = shard_tests.load_timing_map()
        cls.discover_set = _unittest_discover_module_set()

    def test_union_is_full_discover_set_and_partitions_are_disjoint(self):
        self.assertEqual(set(self.modules), self.discover_set)
        for shard_count in (1, 2, 4, 8):
            with self.subTest(shards=shard_count):
                partitions = shard_tests.partition_modules(
                    self.modules, self.timings, shard_count
                )
                flattened = [module for partition in partitions for module in partition]
                self.assertEqual(set(flattened), self.discover_set)
                self.assertEqual(len(flattened), len(self.discover_set))
                self.assertEqual(len(flattened), len(set(flattened)))

    def test_every_discovered_module_has_timing_or_documented_exemption(self):
        """Every module is weighed, exempted, or inside a documented allowance.

        Modules land on many lanes at once, so the allowance lets a small new
        module under a declared prefix (today tests.align. and tests.test_qwen4)
        merge before a CI harvest weighs it, packed at the documented
        unknown_module_weight_seconds.  A module above the size bound, or
        outside every prefix, still fails here until it carries a weight.
        """

        payload = shard_tests._load_timings_payload(shard_tests.DEFAULT_TIMINGS_PATH)
        exemptions = payload.get("timing_exemptions", {})
        self.assertIsInstance(exemptions, dict)
        for module, reason in exemptions.items():
            with self.subTest(module=module):
                self.assertIsInstance(reason, str)
                self.assertTrue(reason.strip())
                self.assertNotIn(module, self.timings)
                # An exemption expires with its module: deleting the test
                # module must also delete the exemption entry.
                self.assertIn(
                    module,
                    self.discover_set,
                    "timing_exemptions names a module that no longer exists",
                )
        rules = _untimed_allowance_rules(payload)
        self.assertEqual(
            _untimed_allowance_violations(
                self.modules, self.timings, exemptions, rules, ROOT
            ),
            set(),
        )

    def test_untimed_allowance_admits_only_small_modules_under_a_prefix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tests/align").mkdir(parents=True)
            (root / "tests/align/test_small.py").write_bytes(b"#" * 100)
            (root / "tests/align/test_large.py").write_bytes(b"#" * 101)
            (root / "tests/test_other.py").write_bytes(b"#" * 10)
            (root / "tests/test_timed.py").write_bytes(b"#" * 10_000)
            modules = (
                "tests.align.test_small",
                "tests.align.test_large",
                "tests.test_other",
                "tests.test_timed",
            )
            rules = _untimed_allowance_rules(
                {
                    UNTIMED_ALLOWANCE_KEY: {
                        "_doc": "ignored",
                        "tests.align.": {"max_source_bytes": 100, "reason": "r"},
                    }
                }
            )
            violations = _untimed_allowance_violations(
                modules, {"tests.test_timed": 1.0}, {}, rules, root
            )
        self.assertEqual(violations, {"tests.align.test_large", "tests.test_other"})
        for bad in (
            {"tests.align.": {"max_source_bytes": 0, "reason": "r"}},
            {"tests.align.": {"max_source_bytes": True, "reason": "r"}},
            {"tests.align.": {"max_source_bytes": 100, "reason": " "}},
            {"align.": {"max_source_bytes": 100, "reason": "r"}},
            [],
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(AssertionError):
                    _untimed_allowance_rules({UNTIMED_ALLOWANCE_KEY: bad})

    def test_partition_is_deterministic(self):
        for shard_count in (1, 2, 4, 8):
            with self.subTest(shards=shard_count):
                first = shard_tests.partition_modules(
                    self.modules, self.timings, shard_count
                )
                second = shard_tests.partition_modules(
                    tuple(reversed(self.modules)),
                    dict(reversed(self.timings.items())),
                    shard_count,
                )
                self.assertEqual(first, second)

    def test_unknown_modules_use_median_weight_deterministically(self):
        timings = {"tests.test_heavy": 9.0, "tests.test_light": 1.0}
        modules = (
            "tests.test_new_b",
            "tests.test_light",
            "tests.test_new_a",
            "tests.test_heavy",
        )
        self.assertEqual(shard_tests.default_module_weight(timings), 5.0)
        expected = (
            ("tests.test_heavy", "tests.test_light"),
            ("tests.test_new_a", "tests.test_new_b"),
        )
        self.assertEqual(shard_tests.partition_modules(modules, timings, 2), expected)
        self.assertEqual(
            shard_tests.partition_modules(tuple(reversed(modules)), timings, 2), expected
        )

        with self.subTest(case="more shards than modules"):
            with self.assertRaisesRegex(ValueError, "refusing to create empty shards"):
                shard_tests.partition_modules(("tests.test_only",), {}, 2)


class NestedPackageDiscoveryTests(unittest.TestCase):
    def test_nested_modules_match_discovery_and_execute_once_in_shards(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tests_dir = root / "tests"
            nested = tests_dir / "shard_nested_fixture"
            deeper = nested / "deeper"
            deeper.mkdir(parents=True)
            for package in (nested, deeper):
                (package / "__init__.py").touch()
            execution_log = root / "executed.txt"
            relative_files = (
                "test_shard_top_fixture.py",
                "shard_nested_fixture/test_child.py",
                "shard_nested_fixture/deeper/test_grandchild.py",
            )
            for relative in relative_files:
                (tests_dir / relative).write_text(
                    "from pathlib import Path\n"
                    "import unittest\n"
                    "class FixtureTests(unittest.TestCase):\n"
                    "    def test_once(self):\n"
                    f"        with Path({str(execution_log)!r}).open('a') as log:\n"
                    "            log.write(__name__ + '\\n')\n",
                    encoding="utf-8",
                )
            expected_imports = {
                "test_shard_top_fixture",
                "shard_nested_fixture.test_child",
                "shard_nested_fixture.deeper.test_grandchild",
            }
            expected_modules = {f"tests.{name}" for name in expected_imports}
            with (
                mock.patch.dict(sys.modules),
                mock.patch.object(sys, "path", list(sys.path)),
                mock.patch.object(shard_tests, "ROOT", root),
                mock.patch.object(shard_tests, "DEFAULT_TESTS_DIR", tests_dir),
            ):
                loader = unittest.TestLoader()
                suite = loader.discover(os.fspath(tests_dir))
                self.assertEqual(loader.errors, [])
                self.assertEqual(suite.countTestCases(), len(expected_modules))
                self.assertEqual(_qualified(_suite_modules(suite)), expected_modules)
                modules = shard_tests.discover_test_modules(tests_dir, root=root)
                self.assertEqual(set(modules), expected_modules)
                self.assertEqual(len(modules), len(expected_modules))
                timings = dict.fromkeys(modules, 1.0)
                for shard_count in (1, 2, 3):
                    with self.subTest(shards=shard_count):
                        execution_log.write_text("", encoding="utf-8")
                        partitions = shard_tests.partition_modules(
                            modules, timings, shard_count
                        )
                        for index, partition in enumerate(partitions, 1):
                            with redirect_stdout(io.StringIO()):
                                exit_code = shard_tests.run_shard(
                                    partition, shard_count, index
                                )
                            self.assertEqual(exit_code, 0)
                        executed = execution_log.read_text(
                            encoding="utf-8"
                        ).splitlines()
                        self.assertEqual(set(executed), expected_imports)
                        self.assertEqual(len(executed), len(expected_imports))

    def test_already_qualified_module_names_are_preserved(self):
        case = type(
            "FixtureTests", (unittest.TestCase,),
            {"__module__": "tests.align.test_fixture"},
        )
        self.assertEqual(
            _suite_modules(unittest.TestSuite([case()])), {"tests.align.test_fixture"}
        )


class ShardExitStatusTests(unittest.TestCase):
    def _assert_pattern_sensitive_load_tests_matches_discover_count(self):
        module_name = "shard_fixture_pattern_sensitive"
        fixture_module = types.ModuleType(module_name)

        def passing_test(self):
            pass

        fixture_case = type(
            "PatternSensitiveTests",
            (unittest.TestCase,),
            {
                "__module__": module_name,
                "test_first": passing_test,
                "test_second": passing_test,
            },
        )
        fixture_module.PatternSensitiveTests = fixture_case
        observed_patterns = []

        def load_tests(loader, standard_tests, pattern):
            observed_patterns.append(pattern)
            if pattern == "test*.py":
                return standard_tests
            return loader.suiteClass()

        fixture_module.load_tests = load_tests
        discover_loader = unittest.TestLoader()
        discover_count = discover_loader.loadTestsFromModule(
            fixture_module, pattern="test*.py"
        ).countTestCases()

        output = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {module_name: fixture_module}),
            mock.patch.object(
                shard_tests, "discover_test_modules", return_value=(module_name,)
            ),
            mock.patch.object(
                shard_tests, "load_timing_map", return_value={module_name: 1.0}
            ),
            redirect_stdout(output),
        ):
            exit_code = shard_tests.main(["--shards", "1", "--index", "1"])

        self.assertEqual(discover_count, 2)
        self.assertEqual(
            observed_patterns,
            ["test*.py", "test*.py"],
        )
        self.assertEqual(exit_code, 0)
        self.assertIn(f"MODULE PASS {module_name} tests={discover_count}", output.getvalue())

    def test_failing_module_makes_shard_exit_nonzero(self):
        module_name = "shard_fixture_failing_module"
        fixture_module = types.ModuleType(module_name)

        def fail_test(self):
            self.fail("intentional shard-runner fixture failure")

        fixture_case = type(
            "IntentionalFailure",
            (unittest.TestCase,),
            {"__module__": module_name, "test_failure": fail_test},
        )
        fixture_module.IntentionalFailure = fixture_case

        output = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {module_name: fixture_module}),
            mock.patch.object(
                shard_tests, "discover_test_modules", return_value=(module_name,)
            ),
            mock.patch.object(
                shard_tests, "load_timing_map", return_value={module_name: 1.0}
            ),
            redirect_stdout(output),
        ):
            exit_code = shard_tests.main(["--shards", "1", "--index", "1"])

        self.assertNotEqual(exit_code, 0)
        self.assertIn(f"MODULE FAIL {module_name}", output.getvalue())
        self.assertIn("result=FAIL", output.getvalue())

        checks = (
            (
                "pattern-sensitive load_tests",
                self._assert_pattern_sensitive_load_tests_matches_discover_count,
            ),
            ("zero-module shard", self._assert_zero_module_shard_fails_closed),
            (
                "excess shard count",
                self._assert_cli_rejects_more_shards_than_discovered_modules,
            ),
            ("out-of-range index", self._assert_cli_rejects_index_outside_shard_range),
            (
                "unimportable module",
                self._assert_unimportable_assigned_module_fails_closed,
            ),
            ("four-shard union", self._assert_four_shard_cli_routes_full_disjoint_union),
        )
        for case, check in checks:
            with self.subTest(case=case):
                check()

    def _assert_zero_module_shard_fails_closed(self):
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = shard_tests.run_shard((), 1, 1)

        self.assertNotEqual(exit_code, 0)
        self.assertIn("SHARD ERROR assigned zero modules", output.getvalue())
        self.assertIn("modules=0 tests=0", output.getvalue())
        self.assertIn("result=FAIL", output.getvalue())

    def _assert_cli_rejects_more_shards_than_discovered_modules(self):
        modules = ("shard_fixture_one", "shard_fixture_two")
        stderr = io.StringIO()
        with (
            mock.patch.object(
                shard_tests, "discover_test_modules", return_value=modules
            ),
            mock.patch.object(
                shard_tests,
                "load_timing_map",
                return_value={module: 1.0 for module in modules},
            ) as load_timings,
            redirect_stdout(io.StringIO()),
            mock.patch("sys.stderr", stderr),
        ):
            exit_code = shard_tests.main(["--shards", "3", "--index", "3"])

        self.assertNotEqual(exit_code, 0)
        self.assertIn("shard count 3 exceeds discovered module count 2", stderr.getvalue())
        load_timings.assert_not_called()

    def _assert_cli_rejects_index_outside_shard_range(self):
        for argv in (
            ["--shards", "4", "--index", "5"],
            ["--shards", "4", "--index", "0"],
        ):
            with self.subTest(argv=argv):
                with (
                    self.assertRaises(SystemExit) as raised,
                    mock.patch("sys.stderr", io.StringIO()),
                ):
                    shard_tests.main(argv)
                self.assertNotEqual(raised.exception.code, 0)

    def _assert_unimportable_assigned_module_fails_closed(self):
        module_name = "shard_fixture_module_that_does_not_exist"
        output = io.StringIO()
        with (
            mock.patch.object(
                shard_tests, "discover_test_modules", return_value=(module_name,)
            ),
            mock.patch.object(
                shard_tests, "load_timing_map", return_value={module_name: 1.0}
            ),
            redirect_stdout(output),
        ):
            exit_code = shard_tests.main(["--shards", "1", "--index", "1"])

        self.assertNotEqual(exit_code, 0)
        self.assertIn(f"MODULE LOAD ERROR {module_name}", output.getvalue())
        self.assertIn("modules=1 tests=0", output.getvalue())
        self.assertIn("errors=1", output.getvalue())
        self.assertIn("result=FAIL", output.getvalue())

    def _assert_four_shard_cli_routes_full_disjoint_union(self):
        modules = tuple(f"shard_fixture_{index}" for index in range(8))
        timings = {module: float(index + 1) for index, module in enumerate(modules)}
        assigned = []

        def record_shard(shard_modules, shard_count, shard_index):
            assigned.append((shard_index, tuple(shard_modules)))
            return 0

        for index in range(1, 5):
            with (
                mock.patch.object(
                    shard_tests, "discover_test_modules", return_value=modules
                ),
                mock.patch.object(
                    shard_tests, "load_timing_map", return_value=timings
                ),
                mock.patch.object(shard_tests, "run_shard", side_effect=record_shard),
            ):
                exit_code = shard_tests.main(
                    ["--shards", "4", "--index", str(index)]
                )
            self.assertEqual(exit_code, 0)

        self.assertEqual([index for index, _ in assigned], [1, 2, 3, 4])
        flattened = [module for _, shard in assigned for module in shard]
        self.assertEqual(set(flattened), set(modules))
        self.assertEqual(len(flattened), len(set(flattened)))


if __name__ == "__main__":
    unittest.main()
