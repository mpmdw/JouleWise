"""Correctness invariants for unit-atomic (per-test) shard splitting.

tests/test_shard_tests.py pins the module-atomic contract; this module covers
the opt-in split path added beside it.  The load-bearing property is the
coverage one: resolving every unit of every shard back to test ids must
reconstruct exactly the set of tests a whole-module run would have executed,
because anything missing from that set is a test no shard runs and no gate
reports.  It matters more here than it would with a hand-written unit list,
since the remainder unit is COMPUTED -- nothing in the timing map spells out
which tests it covers.
"""

from contextlib import contextmanager, redirect_stdout
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.fspath(ROOT / "scripts"))

import shard_tests  # noqa: E402


ALPHA = "tests.shard_split_fixture_alpha"
BETA = "tests.shard_split_fixture_beta"
ALPHA_METHODS = ("test_one", "test_three", "test_two")
ALPHA_HEAVY = ("test_one",)
BETA_METHODS = ("test_only",)


def _import_name(canonical: str) -> str:
    """Mirror discover's tests/-relative import name without importing."""

    prefix = "tests."
    return canonical[len(prefix) :] if canonical.startswith(prefix) else canonical


def _make_fixture_module(canonical, method_names, *, recorder=None, alias=None):
    """Build a TestCase-bearing module object; nothing is written to disk."""

    import_name = _import_name(canonical)
    module = types.ModuleType(import_name)

    def _make_test(method_name):
        def test(self):
            if recorder is not None:
                recorder.append(f"{canonical}.{method_name}")

        return test

    namespace = {"__module__": import_name}
    for method_name in method_names:
        namespace[method_name] = _make_test(method_name)
    case = type("FixtureTests", (unittest.TestCase,), namespace)
    setattr(module, alias or "FixtureTests", case)
    return module


def _ids(canonical, method_names, class_name="FixtureTests"):
    return tuple(f"{canonical}.{class_name}.{name}" for name in sorted(method_names))


def _declared(canonical, method_names, *, seconds=100.0):
    return {
        unit_id: seconds + index
        for index, unit_id in enumerate(_ids(canonical, method_names))
    }


def _declaration(canonical, method_names, *, seconds=100.0, remainder=5.0):
    """Declare `method_names` explicitly; every other test rides the remainder."""

    declaration = {
        "granularity": "test",
        "reason": "fixture",
        "declared": _declared(canonical, method_names, seconds=seconds),
    }
    if remainder is not None:
        declaration["remainder_weight_seconds"] = remainder
    return {canonical: declaration}


def _remainder(canonical):
    return f"{canonical}{shard_tests.REMAINDER_SUFFIX}"


@contextmanager
def _installed(*modules):
    """Make fixture modules importable under their tests/-relative names."""

    installed = {module.__name__: module for module in modules}
    with mock.patch.dict(sys.modules, installed):
        yield


@contextmanager
def _discovered(*canonical_names):
    with mock.patch.object(
        shard_tests, "discover_test_modules", return_value=tuple(canonical_names)
    ):
        yield


@contextmanager
def _split_map(splits):
    with mock.patch.object(
        shard_tests, "load_split_declarations", return_value=splits
    ):
        yield


def _write_timings(directory, **extra):
    payload = {"seconds_by_module": {"tests.test_a": 1.0, "tests.test_b": 3.0}}
    payload.update(extra)
    path = Path(directory) / "timings.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _resolved_test_ids(units, splits):
    """Resolve scheduled units back to the test ids a shard would run."""

    resolved = []
    for module, declaration in splits.items():
        owned = [
            unit
            for unit in units
            if unit == _remainder(module) or unit.startswith(f"{module}.")
        ]
        if owned:
            resolved.extend(
                shard_tests.resolve_units_to_test_ids(
                    module,
                    owned,
                    shard_tests.discover_test_ids(module),
                    declaration["declared"],
                )
            )
    return resolved


class ConservativeUnknownWeightTests(unittest.TestCase):
    def test_checked_in_map_declares_a_weight_above_the_median(self):
        payload = json.loads(
            (ROOT / "scripts" / "test_timings.json").read_text(encoding="utf-8")
        )
        declared = float(payload["unknown_module_weight_seconds"])
        self.assertEqual(shard_tests.conservative_unknown_weight(), declared)
        # The whole point of the separate accessor: the pinned median fallback
        # would price an unmeasured module far below an average one.
        self.assertGreater(
            declared, shard_tests.default_module_weight(shard_tests.load_timing_map())
        )

    def test_absent_key_falls_back_to_the_median(self):
        with tempfile.TemporaryDirectory() as directory:
            path = _write_timings(directory)
            self.assertEqual(
                shard_tests.conservative_unknown_weight(path),
                shard_tests.default_module_weight(shard_tests.load_timing_map(path)),
            )

    def test_present_but_invalid_key_is_refused(self):
        for value in (0, -1.0, "fast", True):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                path = _write_timings(directory, unknown_module_weight_seconds=value)
                with self.assertRaisesRegex(
                    ValueError, "unknown_module_weight_seconds"
                ):
                    shard_tests.conservative_unknown_weight(path)


class SplitDeclarationLoadingTests(unittest.TestCase):
    def test_checked_in_declarations_load_and_still_match_their_modules(self):
        """Guard the real timing map, not just synthetic fixtures.

        Without this, a declared id that gets renamed only bites whoever next
        runs with --split.  Here it fails the suite the moment the rename
        lands, which is the point of the guard.  An empty split_modules block
        passes trivially, so this holds before anything is declared too.
        """

        splits = shard_tests.load_split_declarations()
        discovered_modules = set(shard_tests.discover_test_modules())
        for module, declaration in splits.items():
            with self.subTest(module=module):
                self.assertIn(module, discovered_modules)
                self.assertEqual(declaration["granularity"], "test")
                self.assertIsNone(
                    shard_tests.verify_split_declaration(
                        module, declaration["declared"]
                    )
                )

    def test_checked_in_declarations_schedule_every_test_exactly_once(self):
        splits = shard_tests.load_split_declarations()
        if not splits:
            self.skipTest("no split_modules declared in the checked-in timing map")
        modules = shard_tests.discover_test_modules()
        units, weights = shard_tests.expand_units(
            modules,
            shard_tests.load_timing_map(),
            splits,
            unknown_weight=shard_tests.conservative_unknown_weight(),
        )
        for module, declaration in splits.items():
            with self.subTest(module=module):
                owned = [
                    unit
                    for unit in units
                    if unit == _remainder(module) or unit.startswith(f"{module}.")
                ]
                executed = shard_tests.resolve_units_to_test_ids(
                    module,
                    owned,
                    shard_tests.discover_test_ids(module),
                    declaration["declared"],
                )
                self.assertEqual(
                    sorted(executed), sorted(shard_tests.discover_test_ids(module))
                )
                self.assertNotIn(
                    module, weights, "a split module must not also pack whole"
                )

    def test_valid_declaration_round_trips_with_float_weights(self):
        with tempfile.TemporaryDirectory() as directory:
            path = _write_timings(
                directory, split_modules=_declaration(ALPHA, ALPHA_HEAVY)
            )
            loaded = shard_tests.load_split_declarations(path)
        self.assertEqual(set(loaded), {ALPHA})
        self.assertEqual(loaded[ALPHA]["granularity"], "test")
        self.assertEqual(loaded[ALPHA]["reason"], "fixture")
        self.assertEqual(loaded[ALPHA]["declared"], _declared(ALPHA, ALPHA_HEAVY))
        self.assertEqual(loaded[ALPHA]["remainder_weight_seconds"], 5.0)
        for weight in loaded[ALPHA]["declared"].values():
            self.assertIsInstance(weight, float)

    def test_remainder_weight_is_optional(self):
        with tempfile.TemporaryDirectory() as directory:
            path = _write_timings(
                directory,
                split_modules=_declaration(ALPHA, ALPHA_HEAVY, remainder=None),
            )
            loaded = shard_tests.load_split_declarations(path)
        self.assertIsNone(loaded[ALPHA]["remainder_weight_seconds"])

    def test_documentation_keys_are_ignored(self):
        block = _declaration(ALPHA, ALPHA_HEAVY)
        block["_note"] = "why these modules are split"
        block[ALPHA]["_measured"] = "2026-08-23 hosted CI"
        with tempfile.TemporaryDirectory() as directory:
            path = _write_timings(directory, split_modules=block)
            loaded = shard_tests.load_split_declarations(path)
        self.assertEqual(set(loaded), {ALPHA})

    def test_malformed_declarations_fail_closed(self):
        declared = _declared(ALPHA, ALPHA_HEAVY)
        cases = (
            ("not an object", [], "must be a JSON object"),
            ("declaration not an object", {ALPHA: []}, "must be a JSON object"),
            (
                "wrong granularity",
                {ALPHA: {"granularity": "class", "reason": "r", "declared": declared}},
                "granularity",
            ),
            (
                "missing granularity",
                {ALPHA: {"reason": "r", "declared": declared}},
                "granularity",
            ),
            (
                "blank reason",
                {ALPHA: {"granularity": "test", "reason": "  ", "declared": declared}},
                "'reason'",
            ),
            (
                "missing declared",
                {ALPHA: {"granularity": "test", "reason": "r"}},
                "'declared'",
            ),
            (
                "empty declared",
                {ALPHA: {"granularity": "test", "reason": "r", "declared": {}}},
                "'declared'",
            ),
            (
                "superseded units key",
                {ALPHA: {"granularity": "test", "reason": "r", "units": declared}},
                "unrecognized keys",
            ),
            (
                "foreign unit id",
                {
                    ALPHA: {
                        "granularity": "test",
                        "reason": "r",
                        "declared": {f"{BETA}.FixtureTests.test_only": 1.0},
                    }
                },
                "must begin with",
            ),
            (
                "module id as unit id",
                {
                    ALPHA: {
                        "granularity": "test",
                        "reason": "r",
                        "declared": {f"{ALPHA}.": 1.0},
                    }
                },
                "names no test",
            ),
            (
                "nonpositive weight",
                {
                    ALPHA: {
                        "granularity": "test",
                        "reason": "r",
                        "declared": {f"{ALPHA}.FixtureTests.test_one": 0},
                    }
                },
                "finite and positive",
            ),
            (
                "non-numeric weight",
                {
                    ALPHA: {
                        "granularity": "test",
                        "reason": "r",
                        "declared": {f"{ALPHA}.FixtureTests.test_one": "slow"},
                    }
                },
                "must be numeric",
            ),
            (
                "nonpositive remainder weight",
                {
                    ALPHA: {
                        "granularity": "test",
                        "reason": "r",
                        "declared": declared,
                        "remainder_weight_seconds": 0,
                    }
                },
                "remainder_weight_seconds",
            ),
            (
                "non-numeric remainder weight",
                {
                    ALPHA: {
                        "granularity": "test",
                        "reason": "r",
                        "declared": declared,
                        "remainder_weight_seconds": "rest",
                    }
                },
                "remainder_weight_seconds",
            ),
            (
                "unrecognized key",
                {
                    ALPHA: {
                        "granularity": "test",
                        "reason": "r",
                        "declared": declared,
                        "remaindr_weight_seconds": 5.0,
                    }
                },
                "unrecognized keys",
            ),
        )
        for case, block, pattern in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                path = _write_timings(directory, split_modules=block)
                with self.assertRaisesRegex(ValueError, pattern):
                    shard_tests.load_split_declarations(path)


class SplitVerificationTests(unittest.TestCase):
    def test_discovered_ids_are_canonical_and_complete(self):
        with _installed(_make_fixture_module(ALPHA, ALPHA_METHODS)):
            discovered = shard_tests.discover_test_ids(ALPHA)
        self.assertEqual(discovered, frozenset(_ids(ALPHA, ALPHA_METHODS)))

    def test_declaration_naming_a_subset_verifies(self):
        # Undeclared tests are expected: the remainder unit carries them, which
        # is what keeps a newly added test from needing a timing-map edit.
        with _installed(_make_fixture_module(ALPHA, ALPHA_METHODS)):
            self.assertIsNone(
                shard_tests.verify_split_declaration(ALPHA, _ids(ALPHA, ALPHA_HEAVY))
            )
            self.assertIsNone(
                shard_tests.verify_split_declaration(ALPHA, _ids(ALPHA, ALPHA_METHODS))
            )

    def test_vanished_declared_id_is_named_and_explained(self):
        ghost_id = f"{ALPHA}.FixtureTests.test_renamed_away"
        with _installed(_make_fixture_module(ALPHA, ALPHA_METHODS)):
            with self.assertRaises(ValueError) as raised:
                shard_tests.verify_split_declaration(
                    ALPHA, [*_ids(ALPHA, ALPHA_HEAVY), ghost_id]
                )
        message = str(raised.exception)
        self.assertIn(ALPHA, message)
        self.assertIn(ghost_id, message)
        self.assertIn("DECLARED BUT MISSING", message)
        self.assertIn("remainder", message)
        self.assertIn("scripts/test_timings.json", message)

    def test_unaddressable_test_class_is_refused(self):
        # An id unittest could not resolve back to its test is worse than no
        # split at all, so discovery refuses to mint one.
        module = _make_fixture_module(ALPHA, ALPHA_METHODS, alias="RenamedAlias")
        with _installed(module):
            with self.assertRaisesRegex(ValueError, "not splittable by test id"):
                shard_tests.discover_test_ids(ALPHA)


class UnitExpansionTests(unittest.TestCase):
    def test_undeclared_modules_stay_module_atomic(self):
        units, weights = shard_tests.expand_units(
            (BETA, "tests.test_unmeasured"),
            {BETA: 4.0},
            {},
            unknown_weight=9.0,
        )
        self.assertEqual(units, (BETA, "tests.test_unmeasured"))
        self.assertEqual(weights, {BETA: 4.0, "tests.test_unmeasured": 9.0})

    def test_declared_module_expands_to_declared_ids_plus_one_remainder(self):
        with _installed(_make_fixture_module(ALPHA, ALPHA_METHODS)):
            units, weights = shard_tests.expand_units(
                (ALPHA,),
                {ALPHA: 1000.0},
                _declaration(ALPHA, ALPHA_HEAVY),
                unknown_weight=9.0,
            )
        self.assertEqual(units, (*_ids(ALPHA, ALPHA_HEAVY), _remainder(ALPHA)))
        self.assertEqual(weights[_remainder(ALPHA)], 5.0)
        self.assertEqual(weights[_ids(ALPHA, ALPHA_HEAVY)[0]], 100.0)
        self.assertNotIn(ALPHA, weights)

    def test_remainder_is_omitted_when_every_test_is_declared(self):
        with _installed(_make_fixture_module(ALPHA, ALPHA_METHODS)):
            units, weights = shard_tests.expand_units(
                (ALPHA,), {}, _declaration(ALPHA, ALPHA_METHODS), unknown_weight=9.0
            )
        self.assertEqual(units, _ids(ALPHA, ALPHA_METHODS))
        self.assertNotIn(_remainder(ALPHA), weights)

    def test_remainder_without_a_weight_is_priced_as_the_whole_module(self):
        # Over-reserving idles a shard; under-reserving overruns the job.
        with _installed(_make_fixture_module(ALPHA, ALPHA_METHODS)):
            _, measured = shard_tests.expand_units(
                (ALPHA,),
                {ALPHA: 1000.0},
                _declaration(ALPHA, ALPHA_HEAVY, remainder=None),
                unknown_weight=9.0,
            )
            _, unmeasured = shard_tests.expand_units(
                (ALPHA,),
                {},
                _declaration(ALPHA, ALPHA_HEAVY, remainder=None),
                unknown_weight=9.0,
            )
        self.assertEqual(measured[_remainder(ALPHA)], 1000.0)
        self.assertEqual(unmeasured[_remainder(ALPHA)], 9.0)

    def test_vanished_declared_id_stops_expansion(self):
        with _installed(_make_fixture_module(ALPHA, ALPHA_METHODS[:2])):
            with self.assertRaisesRegex(ValueError, "DECLARED BUT MISSING"):
                shard_tests.expand_units(
                    (ALPHA,),
                    {},
                    _declaration(ALPHA, ALPHA_METHODS),
                    unknown_weight=9.0,
                )

    def test_declaration_for_an_unscheduled_module_is_inert(self):
        # CI schedules a filtered subset (exclusive modules run in their own
        # jobs), so a declaration outside the passed list must not break it.
        units, weights = shard_tests.expand_units(
            (BETA,), {BETA: 4.0}, _declaration(ALPHA, ALPHA_HEAVY), unknown_weight=9.0
        )
        self.assertEqual(units, (BETA,))
        self.assertEqual(weights, {BETA: 4.0})

    def test_every_test_id_lands_in_exactly_one_shard(self):
        splits = _declaration(ALPHA, ALPHA_HEAVY)
        with _installed(
            _make_fixture_module(ALPHA, ALPHA_METHODS),
            _make_fixture_module(BETA, BETA_METHODS),
        ):
            discovered_ids = shard_tests.discover_test_ids(ALPHA)
            units, weights = shard_tests.expand_units(
                (BETA, ALPHA), {BETA: 4.0}, splits, unknown_weight=9.0
            )
            # One declared heavy test + one remainder + one whole module.
            self.assertEqual(len(units), 3)
            for shard_count in (1, 2, 3):
                with self.subTest(shards=shard_count):
                    partitions = shard_tests.partition_modules(
                        units, weights, shard_count, unknown_weight=9.0
                    )
                    scheduled = [unit for shard in partitions for unit in shard]
                    self.assertEqual(len(scheduled), len(set(scheduled)))
                    self.assertEqual(set(scheduled), set(units))

                    # Resolve every shard's units back to the tests it runs.
                    executed = [
                        test_id
                        for shard in partitions
                        for test_id in _resolved_test_ids(shard, splits)
                    ]
                    self.assertEqual(sorted(executed), sorted(discovered_ids))
                    self.assertEqual(len(executed), len(set(executed)))
                    self.assertEqual(
                        [unit for unit in scheduled if unit == BETA], [BETA]
                    )

    def test_a_new_test_joins_the_remainder_with_no_timing_map_edit(self):
        # The reason the declaration is a subset rather than an enumeration.
        splits = _declaration(ALPHA, ALPHA_HEAVY)
        grown = (*ALPHA_METHODS, "test_added_yesterday")
        with _installed(_make_fixture_module(ALPHA, grown)):
            units, weights = shard_tests.expand_units(
                (ALPHA,), {}, splits, unknown_weight=9.0
            )
            executed = _resolved_test_ids(units, splits)
        self.assertEqual(sorted(executed), sorted(_ids(ALPHA, grown)))
        self.assertIn(f"{ALPHA}.FixtureTests.test_added_yesterday", executed)
        self.assertEqual(set(units), {*_ids(ALPHA, ALPHA_HEAVY), _remainder(ALPHA)})

    def test_expansion_and_partitioning_are_order_independent(self):
        declaration = _declaration(ALPHA, ALPHA_METHODS[:2])
        reversed_declaration = {
            ALPHA: {
                **declaration[ALPHA],
                "declared": dict(reversed(declaration[ALPHA]["declared"].items())),
            }
        }
        with _installed(
            _make_fixture_module(ALPHA, ALPHA_METHODS),
            _make_fixture_module(BETA, BETA_METHODS),
        ):
            first_units, first_weights = shard_tests.expand_units(
                (ALPHA, BETA), {BETA: 4.0}, declaration, unknown_weight=9.0
            )
            second_units, second_weights = shard_tests.expand_units(
                (BETA, ALPHA), {BETA: 4.0}, reversed_declaration, unknown_weight=9.0
            )
        self.assertEqual(first_units, second_units)
        self.assertEqual(first_weights, second_weights)
        for shard_count in (1, 2, 3, 4):
            with self.subTest(shards=shard_count):
                self.assertEqual(
                    shard_tests.partition_modules(
                        first_units, first_weights, shard_count, unknown_weight=9.0
                    ),
                    shard_tests.partition_modules(
                        tuple(reversed(second_units)),
                        dict(reversed(second_weights.items())),
                        shard_count,
                        unknown_weight=9.0,
                    ),
                )

    def test_duplicate_and_invalid_inputs_are_refused(self):
        with self.assertRaisesRegex(ValueError, "duplicates"):
            shard_tests.expand_units((BETA, BETA), {}, {}, unknown_weight=9.0)
        with self.assertRaisesRegex(ValueError, "finite and positive"):
            shard_tests.expand_units((BETA,), {}, {}, unknown_weight=0.0)


class RunUnitsTests(unittest.TestCase):
    def test_only_the_assigned_declared_test_id_executes(self):
        executed = []
        assigned = _ids(ALPHA, ALPHA_HEAVY)
        output = io.StringIO()
        with (
            _installed(_make_fixture_module(ALPHA, ALPHA_METHODS, recorder=executed)),
            _discovered(ALPHA, BETA),
            _split_map(_declaration(ALPHA, ALPHA_HEAVY)),
            redirect_stdout(output),
        ):
            exit_code = shard_tests.run_units(assigned, 4, 2)

        text = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertEqual(executed, [f"{ALPHA}.test_one"])
        self.assertIn(f"MODULE START {ALPHA}", text)
        self.assertIn(
            f"MODULE PASS {ALPHA} tests=1 failures=0 errors=0 skipped=0 ", text
        )
        self.assertIn(f"units=1/{len(ALPHA_METHODS)}", text)
        self.assertIn(
            "SHARD SUMMARY index=2/4 modules=1 tests=1 failures=0 errors=0 "
            "skipped=0 result=PASS",
            text,
        )
        self.assertIsNotNone(shard_tests.SHARD_SUMMARY_RE.search(text))

    def test_remainder_unit_runs_exactly_the_undeclared_tests(self):
        executed = []
        output = io.StringIO()
        with (
            _installed(_make_fixture_module(ALPHA, ALPHA_METHODS, recorder=executed)),
            _discovered(ALPHA, BETA),
            _split_map(_declaration(ALPHA, ALPHA_HEAVY)),
            redirect_stdout(output),
        ):
            exit_code = shard_tests.run_units((_remainder(ALPHA),), 4, 3)

        text = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertEqual(
            executed, [f"{ALPHA}.test_three", f"{ALPHA}.test_two"]
        )
        self.assertIn(f"MODULE PASS {ALPHA} tests=2 ", text)
        self.assertIn(f"units=2/{len(ALPHA_METHODS)}", text)
        self.assertIn("SHARD SUMMARY index=3/4 modules=1 tests=2 ", text)

    def test_whole_module_and_test_id_units_coexist_in_one_shard(self):
        executed = []
        assigned = (BETA, *_ids(ALPHA, ALPHA_HEAVY))
        output = io.StringIO()
        with (
            _installed(
                _make_fixture_module(ALPHA, ALPHA_METHODS, recorder=executed),
                _make_fixture_module(BETA, BETA_METHODS, recorder=executed),
            ),
            _discovered(ALPHA, BETA),
            _split_map(_declaration(ALPHA, ALPHA_HEAVY)),
            redirect_stdout(output),
        ):
            exit_code = shard_tests.run_units(assigned, 2, 1)

        text = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertEqual(sorted(executed), [f"{ALPHA}.test_one", f"{BETA}.test_only"])
        # Alphabetical module order, and only the split module carries units=.
        self.assertLess(
            text.index(f"MODULE START {ALPHA}"), text.index(f"MODULE START {BETA}")
        )
        self.assertRegex(
            text,
            rf"MODULE PASS {ALPHA} tests=1 failures=0 errors=0 skipped=0 "
            rf"seconds=\d+\.\d{{3}} units=1/{len(ALPHA_METHODS)}\n",
        )
        self.assertRegex(
            text,
            rf"MODULE PASS {BETA} tests=1 failures=0 errors=0 skipped=0 "
            r"seconds=\d+\.\d{3}\n",
        )
        self.assertIn("SHARD SUMMARY index=1/2 modules=2 tests=2 ", text)

    def test_zero_units_fails_closed(self):
        output = io.StringIO()
        with _discovered(ALPHA, BETA), redirect_stdout(output):
            exit_code = shard_tests.run_units((), 1, 1)

        self.assertNotEqual(exit_code, 0)
        self.assertIn("SHARD ERROR assigned zero modules", output.getvalue())
        self.assertIn("modules=0 tests=0", output.getvalue())
        self.assertIn("result=FAIL", output.getvalue())

    def test_unimportable_module_fails_closed(self):
        missing = "tests.shard_split_fixture_absent"
        output = io.StringIO()
        with _discovered(missing), redirect_stdout(output):
            exit_code = shard_tests.run_units((missing,), 1, 1)

        text = output.getvalue()
        self.assertNotEqual(exit_code, 0)
        self.assertIn(f"MODULE LOAD ERROR {missing}", text)
        self.assertIn(f"MODULE FAIL {missing} tests=0 failures=0 errors=1", text)
        self.assertIn("modules=1 tests=0", text)
        self.assertIn("result=FAIL", text)

    def test_unresolvable_declared_id_fails_closed(self):
        # A vanished id is kept rather than dropped, so the shard errors loudly
        # instead of quietly running one test fewer.
        ghost = f"{ALPHA}.FixtureTests.test_removed"
        output = io.StringIO()
        with (
            _installed(_make_fixture_module(ALPHA, ALPHA_METHODS)),
            _discovered(ALPHA),
            _split_map(_declaration(ALPHA, ALPHA_HEAVY)),
            redirect_stdout(output),
        ):
            exit_code = shard_tests.run_units((ghost,), 1, 1)

        self.assertNotEqual(exit_code, 0)
        self.assertIn("result=FAIL", output.getvalue())


class SplitCliTests(unittest.TestCase):
    def _run_main(self, argv, *, splits, recorder_name):
        calls = []

        def record(units, shard_count, shard_index):
            calls.append((shard_index, tuple(units)))
            return 0

        other = "run_units" if recorder_name == "run_shard" else "run_shard"
        with (
            _installed(
                _make_fixture_module(ALPHA, ALPHA_METHODS),
                _make_fixture_module(BETA, BETA_METHODS),
            ),
            _discovered(ALPHA, BETA),
            mock.patch.object(
                shard_tests, "load_timing_map", return_value={ALPHA: 300.0, BETA: 4.0}
            ),
            mock.patch.object(
                shard_tests, "load_split_declarations", return_value=splits
            ) as load_splits,
            mock.patch.object(
                shard_tests, "conservative_unknown_weight", return_value=9.0
            ),
            mock.patch.object(shard_tests, recorder_name, side_effect=record),
            mock.patch.object(shard_tests, other) as forbidden,
            redirect_stdout(io.StringIO()),
        ):
            exit_code = shard_tests.main(argv)
            forbidden.assert_not_called()
            splits_loaded = load_splits.called
        return exit_code, calls, splits_loaded

    def test_default_cli_path_stays_module_atomic(self):
        exit_code, calls, splits_loaded = self._run_main(
            ["--shards", "2", "--index", "1"],
            splits=_declaration(ALPHA, ALPHA_HEAVY),
            recorder_name="run_shard",
        )
        self.assertEqual(exit_code, 0)
        self.assertFalse(
            splits_loaded, "--split is opt-in; declarations must be ignored"
        )
        self.assertEqual(calls, [(1, (ALPHA,))])

    def test_split_cli_routes_every_test_id_exactly_once(self):
        splits = _declaration(ALPHA, ALPHA_HEAVY)
        collected = []
        for index in (1, 2):
            exit_code, calls, splits_loaded = self._run_main(
                ["--shards", "2", "--index", str(index), "--split"],
                splits=splits,
                recorder_name="run_units",
            )
            self.assertEqual(exit_code, 0)
            self.assertTrue(splits_loaded)
            collected.extend(calls)

        self.assertEqual([index for index, _ in collected], [1, 2])
        scheduled = [unit for _, units in collected for unit in units]
        self.assertEqual(len(scheduled), len(set(scheduled)))
        self.assertEqual(
            set(scheduled), {BETA, _remainder(ALPHA), *_ids(ALPHA, ALPHA_HEAVY)}
        )
        with _installed(_make_fixture_module(ALPHA, ALPHA_METHODS)):
            executed = [
                test_id
                for _, units in collected
                for test_id in _resolved_test_ids(units, splits)
            ]
        self.assertEqual(sorted(executed), sorted(_ids(ALPHA, ALPHA_METHODS)))

    def test_split_flag_reaches_worker_children(self):
        # A worker run fans out to child processes; if the flag stops here the
        # parent silently reverts to whole-module scheduling.
        class _FakePopen:
            argv_log = []

            def __init__(self, argv, cwd=None, stdout=None, stderr=None, text=None):
                type(self).argv_log.append(list(argv))
                index = argv[argv.index("--index") + 1]
                shards = argv[argv.index("--shards") + 1]
                stdout.write(
                    f"SHARD SUMMARY index={index}/{shards} modules=1 tests=1 "
                    "failures=0 errors=0 skipped=0 result=PASS\n"
                )
                self.returncode = 0

            def wait(self):
                return self.returncode

        for split in (False, True):
            with self.subTest(split=split):
                _FakePopen.argv_log = []
                with (
                    mock.patch.object(shard_tests.subprocess, "Popen", _FakePopen),
                    redirect_stdout(io.StringIO()),
                ):
                    exit_code = shard_tests.run_workers(2, split=split)
                self.assertEqual(exit_code, 0)
                self.assertEqual(len(_FakePopen.argv_log), 2)
                for argv in _FakePopen.argv_log:
                    self.assertEqual("--split" in argv, split)

        with (
            _discovered(ALPHA, BETA),
            mock.patch.object(shard_tests, "run_workers", return_value=0) as workers,
            redirect_stdout(io.StringIO()),
        ):
            shard_tests.main(["--workers", "2", "--split"])
        workers.assert_called_once_with(2, split=True)

    def test_split_cli_reports_a_vanished_declared_id(self):
        stderr = io.StringIO()
        with (
            _installed(_make_fixture_module(ALPHA, ALPHA_METHODS[:2])),
            _discovered(ALPHA, BETA),
            mock.patch.object(
                shard_tests, "load_timing_map", return_value={ALPHA: 30.0, BETA: 4.0}
            ),
            _split_map(_declaration(ALPHA, ALPHA_METHODS)),
            mock.patch.object(shard_tests, "run_units") as run_units,
            mock.patch("sys.stderr", stderr),
            redirect_stdout(io.StringIO()),
        ):
            exit_code = shard_tests.main(["--shards", "2", "--index", "1", "--split"])

        self.assertEqual(exit_code, 2)
        run_units.assert_not_called()
        self.assertIn("DECLARED BUT MISSING", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
