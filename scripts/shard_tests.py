#!/usr/bin/env python3
"""Run the stdlib unittest suite in deterministic shards.

The checked-in timing map is a scheduling hint only.  Discovery is always
performed from the current ``tests/`` tree, so an unmeasured new module is
still included and receives the median measured weight.

Sharding is UNIT-atomic, where a unit is either a whole module (the default)
or a single test id belonging to a module the timing map explicitly declares
splittable.  Whole-module packing cannot produce a shard shorter than the
suite's longest single module, so a module that dominates the suite is a hard
floor on wall-clock until its tests are dealt to shards individually.  The
per-test route is opt-in behind ``--split`` and is driven entirely by the
``split_modules`` block of the timing map, which declares only the individually
heavy tests and lets everything else in the module ride along in one remainder
unit.  With that block absent (and always without ``--split``) behaviour is
exactly module-atomic.

Examples:
  python3 scripts/shard_tests.py --shards 4 --index 1
  python3 scripts/shard_tests.py --workers 4
  python3 scripts/shard_tests.py --shards 8 --index 1 --split
"""

from __future__ import annotations

import argparse
import fnmatch
import importlib
import json
import math
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TESTS_DIR = ROOT / "tests"
DEFAULT_TIMINGS_PATH = ROOT / "scripts" / "test_timings.json"
TEST_FILE_RE = re.compile(r"^[_a-z]\w*\.py$", re.IGNORECASE)
DISCOVERY_PATTERN = "test*.py"
TIMINGS_RELATIVE_PATH = "scripts/test_timings.json"
UNKNOWN_WEIGHT_KEY = "unknown_module_weight_seconds"
SPLIT_MODULES_KEY = "split_modules"
SPLIT_DECLARATION_KEYS = frozenset(
    {"granularity", "reason", "declared", "remainder_weight_seconds"}
)
REMAINDER_SUFFIX = "::remainder"
SHARD_SUMMARY_RE = re.compile(
    r"^SHARD SUMMARY index=(?P<index>\d+)/(?P<shards>\d+) "
    r"modules=(?P<modules>\d+) tests=(?P<tests>\d+) "
    r"failures=(?P<failures>\d+) errors=(?P<errors>\d+) "
    r"skipped=(?P<skipped>\d+) result=(?P<result>PASS|FAIL)$",
    re.MULTILINE,
)


def _discover_files(directory: Path, pattern: str):
    """Yield files using unittest discovery's ordering/package recursion rules."""

    for entry in sorted(directory.iterdir(), key=lambda path: path.name):
        if entry.is_file():
            if TEST_FILE_RE.match(entry.name) and fnmatch.fnmatch(entry.name, pattern):
                yield entry
            continue
        if not entry.is_dir() or not entry.name.isidentifier():
            continue
        # unittest accepts a non-package start directory, but only descends
        # through importable packages below it.
        if (entry / "__init__.py").is_file():
            yield from _discover_files(entry, pattern)


def discover_test_modules(
    tests_dir: Path | str = DEFAULT_TESTS_DIR,
    *,
    root: Path | str = ROOT,
    pattern: str = DISCOVERY_PATTERN,
) -> tuple[str, ...]:
    """Return the import names selected by ``unittest discover -s tests``."""

    tests_path = Path(tests_dir).resolve()
    root_path = Path(root).resolve()
    if not tests_path.is_dir():
        raise ValueError(f"test start directory does not exist: {tests_path}")
    try:
        tests_path.relative_to(root_path)
    except ValueError as exc:
        raise ValueError(f"test start directory must be under root: {tests_path}") from exc

    modules = []
    for path in _discover_files(tests_path, pattern):
        relative = path.relative_to(root_path).with_suffix("")
        modules.append(".".join(relative.parts))
    return tuple(modules)


def load_timing_map(path: Path | str = DEFAULT_TIMINGS_PATH) -> dict[str, float]:
    """Load and validate the checked-in module-to-seconds scheduling map."""

    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    values = payload.get("seconds_by_module")
    if not isinstance(values, dict) or not values:
        raise ValueError("timing map must contain a nonempty seconds_by_module object")

    timings = {}
    for module, seconds in values.items():
        if not isinstance(module, str) or not module:
            raise ValueError("timing map module names must be nonempty strings")
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
            raise ValueError(f"timing for {module!r} must be numeric")
        weight = float(seconds)
        if not math.isfinite(weight) or weight <= 0:
            raise ValueError(f"timing for {module!r} must be finite and positive")
        timings[module] = weight
    return timings


def default_module_weight(timings: dict[str, float]) -> float:
    """Return the deterministic fallback used for unmeasured modules."""

    if not timings:
        raise ValueError("cannot calculate a default weight from an empty timing map")
    return float(statistics.median(timings.values()))


def _load_timings_payload(path: Path | str) -> dict:
    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"timing map {path} must contain a JSON object")
    return payload


def conservative_unknown_weight(path: Path | str = DEFAULT_TIMINGS_PATH) -> float:
    """Return the fail-safe scheduling weight for an unmeasured module.

    A module that discovery finds but the timing map does not measure still has
    to be packed into some shard, and the packer needs a number for it.
    ``default_module_weight()`` supplies the MEDIAN of the measured weights and
    keeps doing so (tests/test_shard_tests.py pins that), but the median is the
    wrong estimator here.  The measured suite is heavy-tailed: most modules
    finish in well under a second while a handful run for many minutes, so the
    median asserts that an unmeasured module is effectively free.  Add a heavy
    module, and the packer drops it into an already-full shard and the CI job
    overruns with nothing reporting a mistake.

    The timing map therefore carries an explicit ``unknown_module_weight_seconds``
    (currently the arithmetic MEAN of the measured weights, which reserves the
    cost of an average module rather than of a trivial one), and this function
    reads it.  When the key is absent -- an older map -- it falls back to
    ``default_module_weight(load_timing_map(path))`` so nothing breaks.  A key
    that is present but not a finite positive number is a defect in the map and
    raises rather than being silently replaced by a guess.
    """

    payload = _load_timings_payload(path)
    if UNKNOWN_WEIGHT_KEY not in payload:
        return default_module_weight(load_timing_map(path))
    seconds = payload[UNKNOWN_WEIGHT_KEY]
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
        raise ValueError(f"{UNKNOWN_WEIGHT_KEY} must be numeric")
    weight = float(seconds)
    if not math.isfinite(weight) or weight <= 0:
        raise ValueError(f"{UNKNOWN_WEIGHT_KEY} must be finite and positive")
    return weight


def load_split_declarations(path: Path | str = DEFAULT_TIMINGS_PATH) -> dict[str, dict]:
    """Load the optional ``split_modules`` block, validating it strictly.

    Shape::

        "split_modules": {
          "tests.test_reduce": {
            "granularity": "test",
            "reason": "<why splitting this module is safe>",
            "declared": {"tests.test_reduce.SomeClass.test_heavy_a": 252.9, ...},
            "remainder_weight_seconds": 264.0
          }
        }

    ``declared`` lists only the tests heavy enough to be worth scheduling
    individually.  Everything else in the module is gathered at run time into a
    single REMAINDER unit, so a test added to a split module is picked up
    automatically and no one has to hand-edit this file to keep the suite
    covered.  Enumerating every test id here instead would mean two hand-kept
    lists of the same thing, and the second one rots.

    Absent key -> ``{}``, and every caller then behaves module-atomically.

    Validation fails closed because a malformed declaration is a request to run
    part of a module in one process and the rest in another; there is no safe
    partial reading of it.  Keys beginning with ``_`` are ignored at both
    levels, matching the ``_provenance``-style documentation keys the timing map
    already uses.
    """

    payload = _load_timings_payload(path)
    declared = payload.get(SPLIT_MODULES_KEY)
    if declared is None:
        return {}
    if not isinstance(declared, dict):
        raise ValueError(f"{SPLIT_MODULES_KEY} must be a JSON object")

    splits: dict[str, dict] = {}
    for module, declaration in declared.items():
        if module.startswith("_"):
            continue
        if not module:
            raise ValueError(f"{SPLIT_MODULES_KEY} keys must be nonempty module names")
        if not isinstance(declaration, dict):
            raise ValueError(f"split declaration for {module!r} must be a JSON object")
        unexpected = sorted(
            key
            for key in declaration
            if key not in SPLIT_DECLARATION_KEYS and not key.startswith("_")
        )
        if unexpected:
            raise ValueError(
                f"split declaration for {module!r} has unrecognized keys: "
                f"{', '.join(unexpected)}; expected "
                f"{', '.join(sorted(SPLIT_DECLARATION_KEYS))}"
            )
        granularity = declaration.get("granularity")
        if granularity != "test":
            raise ValueError(
                f"split declaration for {module!r} must set granularity to "
                f'"test"; got {granularity!r}'
            )
        reason = declaration.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(
                f"split declaration for {module!r} must carry a nonempty 'reason' "
                "string recording why the module's tests are safe to run in "
                "separate processes"
            )
        declared_units = declaration.get("declared")
        if not isinstance(declared_units, dict) or not declared_units:
            raise ValueError(
                f"split declaration for {module!r} must carry a nonempty 'declared' "
                "object mapping test id to seconds"
            )
        prefix = f"{module}."
        weights: dict[str, float] = {}
        for unit_id, seconds in declared_units.items():
            if not isinstance(unit_id, str) or not unit_id.startswith(prefix):
                raise ValueError(
                    f"split unit id {unit_id!r} declared under {module!r} must "
                    f"begin with {prefix!r}"
                )
            if not unit_id[len(prefix) :].strip("."):
                raise ValueError(
                    f"split unit id {unit_id!r} declared under {module!r} names no "
                    "test below the module"
                )
            if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
                raise ValueError(f"weight for split unit {unit_id!r} must be numeric")
            weight = float(seconds)
            if not math.isfinite(weight) or weight <= 0:
                raise ValueError(
                    f"weight for split unit {unit_id!r} must be finite and positive"
                )
            weights[unit_id] = weight

        remainder_seconds = declaration.get("remainder_weight_seconds")
        if remainder_seconds is not None:
            if isinstance(remainder_seconds, bool) or not isinstance(
                remainder_seconds, (int, float)
            ):
                raise ValueError(
                    f"remainder_weight_seconds for {module!r} must be numeric"
                )
            remainder_seconds = float(remainder_seconds)
            if not math.isfinite(remainder_seconds) or remainder_seconds <= 0:
                raise ValueError(
                    f"remainder_weight_seconds for {module!r} must be finite and "
                    "positive"
                )

        splits[module] = {
            "granularity": "test",
            "reason": reason,
            "declared": weights,
            "remainder_weight_seconds": remainder_seconds,
        }
    return splits


def _ensure_import_paths() -> None:
    """Put ROOT and tests/ on ``sys.path`` the way ``discover -s tests`` does.

    ``run_shard()`` inlines this same sequence; it is duplicated rather than
    factored out of it because that function's exact behaviour is pinned by
    tests/test_shard_tests.py.
    """

    root_path = os.fspath(ROOT)
    if root_path not in sys.path:
        sys.path.insert(0, root_path)
    tests_path = os.fspath(DEFAULT_TESTS_DIR)
    if tests_path not in sys.path:
        sys.path.insert(0, tests_path)


def _module_test_ids(module: str, imported) -> frozenset[str]:
    """Return canonical test ids for an already-imported module object."""

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(imported, pattern=DISCOVERY_PATTERN)
    ids: set[str] = set()
    stack = [suite]
    while stack:
        item = stack.pop()
        if isinstance(item, unittest.TestSuite):
            stack.extend(item)
            continue
        if not isinstance(item, unittest.TestCase):
            raise ValueError(
                f"{module} yielded a non-TestCase item {item!r}; it cannot be "
                "addressed by test id and must not be declared splittable"
            )
        case_class = type(item)
        qualname = case_class.__qualname__
        method = getattr(item, "_testMethodName", None) or item.id().rpartition(".")[2]
        _assert_addressable(module, imported, case_class, qualname, method)
        ids.add(f"{module}.{qualname}.{method}")
    return frozenset(ids)


def _assert_addressable(
    module, imported, case_class, qualname: str, method: str
) -> None:
    """Reject ids ``loadTestsFromNames`` could not resolve back to this test.

    ``loadTestsFromNames`` resolves a dotted id by importing the module and then
    walking attribute lookups, so a test class that is present in the suite but
    not reachable under its own ``__qualname__`` (an alias, an import from a
    helper module under a different name, a class synthesized by ``load_tests``)
    would produce a unit id that no shard can load.  Catch that where the
    declaration is verified instead of in the middle of a CI run.
    """

    obj = imported
    for part in qualname.split("."):
        obj = getattr(obj, part, None)
        if obj is None:
            break
    if obj is not case_class or not hasattr(case_class, method):
        raise ValueError(
            f"{module} is not splittable by test id: its test "
            f"{qualname}.{method} is not reachable as the attribute path "
            f"{module}.{qualname} of the module, so unittest could not load that "
            "id in a shard. Run this module whole (remove its "
            f"{SPLIT_MODULES_KEY} entry)."
        )


def discover_test_ids(module: str) -> frozenset[str]:
    """Return every test id in ``module`` as ``tests.<mod>.<Class>.<method>``.

    The module is imported (under discover's tests/-relative import name, the
    same translation the runner uses) and its suite is walked, so this reflects
    exactly the tests the runner would execute for the whole module.
    """

    _ensure_import_paths()
    imported = importlib.import_module(_unittest_import_name(module))
    return _module_test_ids(module, imported)


def verify_split_declaration(module: str, declared_unit_ids) -> None:
    """Fail closed when a declared test id no longer exists in the module.

    Tests the declaration does NOT name are fine -- the remainder unit sweeps
    them up automatically, which is the whole reason they are not enumerated.
    A DECLARED id that has vanished is the dangerous direction, and it is the
    one a computed remainder would otherwise hide: rename a heavy test and its
    declared id stops matching anything, the renamed test silently joins the
    remainder, and whichever shard owns the remainder inherits that test's
    minutes while the scheduler's weights still say the work is elsewhere.
    Nothing fails; the job just runs long, for a reason nobody can see. So stop
    here and say so.
    """

    discovered = discover_test_ids(module)
    missing = sorted(frozenset(declared_unit_ids) - discovered)
    if not missing:
        return

    raise ValueError(
        "\n".join(
            (
                f"split declaration for {module} names {len(missing)} test id(s) "
                f"the module no longer defines (of {len(discovered)} discovered).",
                "DECLARED BUT MISSING -- renamed or removed. Their measured "
                "weight now schedules nothing, and if they were renamed their "
                "cost has moved into the remainder unit unpriced: "
                + ", ".join(missing),
                "Fix: re-measure this module's per-test seconds and update "
                f'"{SPLIT_MODULES_KEY}" -> "{module}" -> "declared" (and '
                '"remainder_weight_seconds") in '
                f"{TIMINGS_RELATIVE_PATH} so every declared id names a test that "
                f"exists. Deleting the module's {SPLIT_MODULES_KEY} entry "
                "restores whole-module scheduling and is always safe.",
            )
        )
    )


def resolve_units_to_test_ids(module: str, unit_ids, discovered_ids, declared_ids):
    """Expand one module's assigned units into the test ids to actually run.

    A declared unit stands for itself; the remainder unit stands for every
    discovered test id no declaration claims.  A declared id that has vanished
    from the module is deliberately kept in the result rather than dropped, so
    the shard owning it errors on an unresolvable name instead of quietly
    running one test fewer.
    """

    declared = frozenset(declared_ids)
    remainder_id = f"{module}{REMAINDER_SUFFIX}"
    resolved: set[str] = set()
    for unit_id in unit_ids:
        if unit_id == remainder_id:
            resolved |= frozenset(discovered_ids) - declared
            continue
        resolved.add(unit_id)
    return tuple(sorted(resolved))


def expand_units(
    modules,
    timings: dict[str, float],
    splits: dict[str, dict],
    *,
    unknown_weight: float,
) -> tuple[tuple[str, ...], dict[str, float]]:
    """Expand discovered modules into the schedulable units and their weights.

    A module named in ``splits`` contributes one unit per DECLARED test id plus
    one ``<module>::remainder`` unit standing for every discovered test it does
    not declare, so a newly added test is scheduled without anyone editing the
    timing map.  Its declaration is verified against discovery first, so a
    declared id that has vanished stops the run instead of drifting into the
    remainder.  A module with nothing left over emits no remainder unit.  Every
    other module contributes itself as a single unit weighted by ``timings``,
    falling back to ``unknown_weight``.

    A remainder with no ``remainder_weight_seconds`` is priced at the module's
    whole-module weight.  That over-reserves -- the remainder is a strict subset
    of the module -- which is the safe direction: over-reserving idles a shard,
    under-reserving overruns the job that everything else waits on.

    The returned pair feeds ``partition_modules()`` directly: that packer is
    already generic over opaque unit names plus a weight dict -- it only ever
    does ``timings.get(name, unknown_weight)``, sorts, and greedily assigns --
    so per-test packing reuses it rather than introducing a second packer with
    its own balance and tie-breaking behaviour.  Because the returned weight map
    covers every returned unit, the ``unknown_weight`` handed to the packer is
    never actually consulted; it is still passed so the packer's validation of
    it stays meaningful.

    A declaration for a module the caller did not pass is ignored rather than
    rejected: callers legitimately schedule a filtered subset (CI packs the
    ordinary modules and runs the ``exclusive_modules`` ones in their own jobs).
    A stale declaration therefore degrades packing back to whole modules, which
    is slow but never drops a test.
    """

    if not math.isfinite(unknown_weight) or unknown_weight <= 0:
        raise ValueError("unknown-module weight must be finite and positive")
    module_list = list(modules)
    if len(module_list) != len(set(module_list)):
        raise ValueError("module list contains duplicates")

    units: list[str] = []
    weights: dict[str, float] = {}
    for module in sorted(module_list):
        declaration = splits.get(module)
        if declaration is None:
            units.append(module)
            weights[module] = float(timings.get(module, unknown_weight))
            continue
        declared = declaration["declared"]
        verify_split_declaration(module, declared.keys())
        for unit_id in sorted(declared):
            units.append(unit_id)
            weights[unit_id] = float(declared[unit_id])
        remainder_ids = discover_test_ids(module) - frozenset(declared)
        if not remainder_ids:
            continue
        remainder_weight = declaration.get("remainder_weight_seconds")
        if remainder_weight is None:
            remainder_weight = timings.get(module, unknown_weight)
        remainder_id = f"{module}{REMAINDER_SUFFIX}"
        units.append(remainder_id)
        weights[remainder_id] = float(remainder_weight)

    if len(units) != len(set(units)):
        raise ValueError("expanded unit list contains duplicates")
    return tuple(units), weights


def partition_modules(
    modules,
    timings: dict[str, float],
    shard_count: int,
    *,
    unknown_weight: float | None = None,
) -> tuple[tuple[str, ...], ...]:
    """Assign whole modules with deterministic longest-processing-time packing."""

    if shard_count < 1:
        raise ValueError("shard count must be at least 1")
    module_list = list(modules)
    if len(module_list) != len(set(module_list)):
        raise ValueError("module list contains duplicates")
    _validate_shard_capacity(len(module_list), shard_count)
    if unknown_weight is None:
        unknown_weight = default_module_weight(timings)
    if not math.isfinite(unknown_weight) or unknown_weight <= 0:
        raise ValueError("unknown-module weight must be finite and positive")

    weighted = sorted(
        ((float(timings.get(module, unknown_weight)), module) for module in module_list),
        key=lambda item: (-item[0], item[1]),
    )
    partitions: list[list[str]] = [[] for _ in range(shard_count)]
    totals = [0.0] * shard_count
    for weight, module in weighted:
        shard_index = min(range(shard_count), key=lambda index: (totals[index], index))
        partitions[shard_index].append(module)
        totals[shard_index] += weight

    # Preserve unittest's normal alphabetical module order inside each process.
    return tuple(tuple(sorted(partition)) for partition in partitions)


def partition_totals(
    partitions, timings: dict[str, float], *, unknown_weight: float | None = None
) -> tuple[float, ...]:
    """Return estimated seconds for each partition (useful for inspection)."""

    if unknown_weight is None:
        unknown_weight = default_module_weight(timings)
    return tuple(
        sum(float(timings.get(module, unknown_weight)) for module in partition)
        for partition in partitions
    )


def _result_counts(result: unittest.TestResult) -> tuple[int, int, int, int]:
    return (
        result.testsRun,
        len(result.failures),
        len(result.errors),
        len(result.skipped),
    )


def _unittest_import_name(module: str) -> str:
    """Translate the canonical repo name to discover's top-level import name."""

    prefix = f"{DEFAULT_TESTS_DIR.name}."
    return module[len(prefix) :] if module.startswith(prefix) else module


def _validate_shard_capacity(module_count: int, shard_count: int) -> None:
    """Reject a shard layout that would necessarily assign zero modules."""

    if shard_count > module_count:
        raise ValueError(
            f"shard count {shard_count} exceeds discovered module count "
            f"{module_count}; refusing to create empty shards"
        )


def run_shard(modules, shard_count: int, shard_index: int) -> int:
    """Run one shard in this process and return a shell-style exit code."""

    root_path = os.fspath(ROOT)
    if root_path not in sys.path:
        sys.path.insert(0, root_path)
    tests_path = os.fspath(DEFAULT_TESTS_DIR)
    if tests_path not in sys.path:
        # ``unittest discover -s tests`` imports test files relative to this
        # directory.  Match that behavior even though this script lives in
        # scripts/ and therefore has a different default sys.path[0].
        sys.path.insert(0, tests_path)
    loader = unittest.TestLoader()
    total_tests = total_failures = total_errors = total_skipped = 0
    successful = bool(modules)

    if not modules:
        print("SHARD ERROR assigned zero modules; refusing to pass", flush=True)

    for module in modules:
        print(f"MODULE START {module}", flush=True)
        try:
            imported_module = importlib.import_module(_unittest_import_name(module))
            suite = loader.loadTestsFromModule(
                imported_module, pattern=DISCOVERY_PATTERN
            )
        except Exception as exc:
            total_errors += 1
            successful = False
            print(
                f"MODULE LOAD ERROR {module}: {type(exc).__name__}: {exc}",
                flush=True,
            )
            print(
                f"MODULE FAIL {module} tests=0 failures=0 errors=1 "
                "skipped=0 seconds=0.000",
                flush=True,
            )
            continue
        started = time.monotonic()
        result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
        elapsed = time.monotonic() - started
        tests_run, failures, errors, skipped = _result_counts(result)
        total_tests += tests_run
        total_failures += failures
        total_errors += errors
        total_skipped += skipped
        module_ok = result.wasSuccessful()
        successful = successful and module_ok
        print(
            f"MODULE {'PASS' if module_ok else 'FAIL'} {module} "
            f"tests={tests_run} failures={failures} errors={errors} "
            f"skipped={skipped} seconds={elapsed:.3f}",
            flush=True,
        )

    print(
        f"SHARD SUMMARY index={shard_index}/{shard_count} modules={len(modules)} "
        f"tests={total_tests} failures={total_failures} errors={total_errors} "
        f"skipped={total_skipped} result={'PASS' if successful else 'FAIL'}",
        flush=True,
    )
    return 0 if successful else 1


def _owning_module(unit: str, known_modules) -> str:
    """Return the discovered module a unit belongs to.

    A unit is a module name, a test id below one, or a module's remainder.  The
    longest dotted prefix that discovery actually found is the owner.  A name
    with no such prefix is treated as a module name, which preserves today's
    behaviour for an unimportable assignment: it reaches the import and reports
    MODULE LOAD ERROR instead of being silently dropped.
    """

    if unit in known_modules:
        return unit
    if unit.endswith(REMAINDER_SUFFIX):
        return unit[: -len(REMAINDER_SUFFIX)]
    parts = unit.split(".")
    for stop in range(len(parts) - 1, 0, -1):
        candidate = ".".join(parts[:stop])
        if candidate in known_modules:
            return candidate
    return unit


def _group_units_by_module(units) -> tuple[tuple[str, bool, tuple[str, ...]], ...]:
    """Group units into ``(module, whole_module, unit_ids)`` triples.

    Modules come back in alphabetical order and test ids are alphabetical within
    a module, so a shard's output ordering does not depend on packing order.
    """

    known_modules = frozenset(discover_test_modules())
    grouped: dict[str, dict] = {}
    for unit in units:
        module = _owning_module(unit, known_modules)
        whole_module = module == unit
        entry = grouped.setdefault(module, {"whole_module": whole_module, "ids": []})
        if entry["whole_module"] != whole_module:
            raise ValueError(
                f"{module} is assigned both as a whole module and by test id; a "
                "module is scheduled one way or the other"
            )
        if whole_module and entry["ids"]:
            raise ValueError(f"module {module} is assigned more than once")
        entry["ids"].append(unit)

    return tuple(
        (module, grouped[module]["whole_module"], tuple(sorted(grouped[module]["ids"])))
        for module in sorted(grouped)
    )


def run_units(units, shard_count: int, shard_index: int) -> int:
    """Run one shard of mixed whole-module and per-test units in this process.

    Output grammar is the same as ``run_shard()`` -- CI log harvesting and
    ``SHARD_SUMMARY_RE`` both parse it -- with one addition: a module assigned
    by test id gets a trailing ``units=<ran>/<total>`` field on its MODULE line
    counting the tests this shard ran out of the tests the module defines, so a
    reader can tell the line covers part of a module rather than all of it.
    ``modules=`` in the summary counts DISTINCT modules this shard touched, so
    for a module split across shards each shard reports it once.

    The declarations are re-read here because a remainder unit names its tests
    by exclusion: it stands for the module's discovered tests minus the declared
    ones, and both halves are resolved against the live module at run time.
    """

    _ensure_import_paths()
    loader = unittest.TestLoader()
    total_tests = total_failures = total_errors = total_skipped = 0
    unit_list = list(units)
    successful = bool(unit_list)

    if not unit_list:
        print("SHARD ERROR assigned zero modules; refusing to pass", flush=True)

    groups = _group_units_by_module(unit_list)
    # Only a module assigned by test id needs the declarations; a shard of whole
    # modules must not depend on the timing map to run.
    splits = (
        load_split_declarations()
        if any(not whole_module for _, whole_module, _ in groups)
        else {}
    )
    for module, whole_module, unit_ids in groups:
        print(f"MODULE START {module}", flush=True)
        try:
            imported_module = importlib.import_module(_unittest_import_name(module))
            if whole_module:
                module_total = ran_total = None
                suite = loader.loadTestsFromModule(
                    imported_module, pattern=DISCOVERY_PATTERN
                )
            else:
                # Both counts come from the live module, so a partial line
                # reports the module's real size rather than the declaration's
                # claim about it.
                discovered_ids = _module_test_ids(module, imported_module)
                test_ids = resolve_units_to_test_ids(
                    module,
                    unit_ids,
                    discovered_ids,
                    splits.get(module, {}).get("declared", ()),
                )
                module_total = len(discovered_ids)
                ran_total = len(test_ids)
                suite = loader.loadTestsFromNames(
                    [_unittest_import_name(test_id) for test_id in test_ids]
                )
        except Exception as exc:
            total_errors += 1
            successful = False
            print(
                f"MODULE LOAD ERROR {module}: {type(exc).__name__}: {exc}",
                flush=True,
            )
            print(
                f"MODULE FAIL {module} tests=0 failures=0 errors=1 "
                "skipped=0 seconds=0.000",
                flush=True,
            )
            continue
        started = time.monotonic()
        result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
        elapsed = time.monotonic() - started
        tests_run, failures, errors, skipped = _result_counts(result)
        total_tests += tests_run
        total_failures += failures
        total_errors += errors
        total_skipped += skipped
        module_ok = result.wasSuccessful()
        successful = successful and module_ok
        units_field = "" if whole_module else f" units={ran_total}/{module_total}"
        print(
            f"MODULE {'PASS' if module_ok else 'FAIL'} {module} "
            f"tests={tests_run} failures={failures} errors={errors} "
            f"skipped={skipped} seconds={elapsed:.3f}{units_field}",
            flush=True,
        )

    print(
        f"SHARD SUMMARY index={shard_index}/{shard_count} modules={len(groups)} "
        f"tests={total_tests} failures={total_failures} errors={total_errors} "
        f"skipped={total_skipped} result={'PASS' if successful else 'FAIL'}",
        flush=True,
    )
    return 0 if successful else 1


def run_workers(worker_count: int, *, split: bool = False) -> int:
    """Run all shards concurrently in child processes and aggregate results."""

    if worker_count < 1:
        raise ValueError("worker count must be at least 1")

    command_prefix = [sys.executable, os.fspath(Path(__file__).resolve())]
    processes = []
    with tempfile.TemporaryDirectory(prefix="joulewise-shards-") as temp_dir:
        for index in range(1, worker_count + 1):
            output_path = Path(temp_dir) / f"shard-{index}.log"
            output_handle = output_path.open("w", encoding="utf-8")
            child_argv = [
                *command_prefix,
                "--shards",
                str(worker_count),
                "--index",
                str(index),
            ]
            if split:
                child_argv.append("--split")
            process = subprocess.Popen(
                child_argv,
                cwd=ROOT,
                stdout=output_handle,
                stderr=subprocess.STDOUT,
                text=True,
            )
            processes.append((index, process, output_handle, output_path))

        for _, process, _, _ in processes:
            process.wait()

        total_modules = total_tests = total_failures = total_errors = total_skipped = 0
        failed_shards = []
        for index, process, output_handle, output_path in processes:
            output_handle.close()
            output = output_path.read_text(encoding="utf-8")
            print(f"===== SHARD {index}/{worker_count} OUTPUT =====")
            print(output, end="" if output.endswith("\n") else "\n")
            match = SHARD_SUMMARY_RE.search(output)
            if (
                match is None
                or match.group("result") != "PASS"
                or process.returncode != 0
            ):
                failed_shards.append(index)
            if match is not None:
                total_modules += int(match.group("modules"))
                total_tests += int(match.group("tests"))
                total_failures += int(match.group("failures"))
                total_errors += int(match.group("errors"))
                total_skipped += int(match.group("skipped"))

    successful = not failed_shards
    failed_text = ",".join(map(str, failed_shards)) if failed_shards else "none"
    print(
        f"WORKERS SUMMARY shards={worker_count} modules={total_modules} "
        f"tests={total_tests} failures={total_failures} errors={total_errors} "
        f"skipped={total_skipped} failed_shards={failed_text} "
        f"result={'PASS' if successful else 'FAIL'}"
    )
    return 0 if successful else 1


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--shards", type=_positive_int, help="total shard count")
    mode.add_argument("--workers", type=_positive_int, help="run N shards concurrently")
    parser.add_argument("--index", type=_positive_int, help="1-based shard index")
    parser.add_argument(
        "--split",
        action="store_true",
        help=(
            "schedule the modules declared under split_modules in "
            f"{TIMINGS_RELATIVE_PATH} one test at a time instead of whole "
            "(default off: whole-module scheduling)"
        ),
    )
    args = parser.parse_args(argv)
    if args.shards is not None:
        if args.index is None:
            parser.error("--index is required with --shards")
        if args.index > args.shards:
            parser.error("--index cannot exceed --shards")
    elif args.index is not None:
        parser.error("--index is only valid with --shards")
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    modules = discover_test_modules()
    shard_count = args.workers if args.workers is not None else args.shards
    try:
        _validate_shard_capacity(len(modules), shard_count)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.workers is not None:
        return run_workers(args.workers, split=args.split)

    timings = load_timing_map()
    if not args.split:
        partitions = partition_modules(modules, timings, args.shards)
        return run_shard(partitions[args.index - 1], args.shards, args.index)

    # Opt-in per-test path.  It uses the conservative unmeasured-module weight
    # because nothing pins this path's fallback, and an unmeasured module is
    # likelier to be new than to be free.
    try:
        unknown_weight = conservative_unknown_weight()
        splits = load_split_declarations()
        units, weights = expand_units(
            modules, timings, splits, unknown_weight=unknown_weight
        )
        partitions = partition_modules(
            units, weights, args.shards, unknown_weight=unknown_weight
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return run_units(partitions[args.index - 1], args.shards, args.index)


if __name__ == "__main__":
    raise SystemExit(main())
