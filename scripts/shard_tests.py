#!/usr/bin/env python3
"""Run the stdlib unittest suite in deterministic, module-atomic shards.

The checked-in timing map is a scheduling hint only.  Discovery is always
performed from the current ``tests/`` tree, so an unmeasured new module is
still included and receives the median measured weight.

Examples:
  python3 scripts/shard_tests.py --shards 4 --index 1
  python3 scripts/shard_tests.py --workers 4
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


def run_workers(worker_count: int) -> int:
    """Run all shards concurrently in child processes and aggregate results."""

    if worker_count < 1:
        raise ValueError("worker count must be at least 1")

    command_prefix = [sys.executable, os.fspath(Path(__file__).resolve())]
    processes = []
    with tempfile.TemporaryDirectory(prefix="joulewise-shards-") as temp_dir:
        for index in range(1, worker_count + 1):
            output_path = Path(temp_dir) / f"shard-{index}.log"
            output_handle = output_path.open("w", encoding="utf-8")
            process = subprocess.Popen(
                [*command_prefix, "--shards", str(worker_count), "--index", str(index)],
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
        return run_workers(args.workers)

    timings = load_timing_map()
    partitions = partition_modules(modules, timings, args.shards)
    return run_shard(partitions[args.index - 1], args.shards, args.index)


if __name__ == "__main__":
    raise SystemExit(main())
