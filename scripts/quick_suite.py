#!/usr/bin/env python3
"""Fast, isolated unittest modules; touched adds related heavy and unmeasured modules.

Run from any directory. Each selection/exclusion is printed, followed by module
results and one QUICK SUMMARY line. --module replays one failure with the same
loader and temporary-directory isolation, without running the tier again.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import json
import math
import multiprocessing
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time

if __package__:
    from . import shard_tests
else:
    import shard_tests

ROOT = shard_tests.ROOT
DOCS_MODULE = "tests.test_docs_freshness"


def changed_paths(since: str, root: Path = ROOT) -> tuple[str, ...]:
    """Include committed, staged, unstaged, deleted, and new untracked paths.

    Disabling rename detection includes both names, so tests of the old import
    remain relevant when a production module is renamed.
    """
    revision = subprocess.check_output(
        ["git", "rev-parse", "--verify", "--end-of-options", f"{since}^{{commit}}"],
        cwd=root, text=True,
    ).strip()
    paths = subprocess.check_output(
        ["git", "diff", "--name-only", "--no-renames", "-z", revision, "--"],
        cwd=root,
    )
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=root,
    )
    return tuple(sorted({os.fsdecode(p) for p in (paths + untracked).split(b"\0") if p}))


def touched_modules(modules, paths, root: Path = ROOT) -> frozenset[str]:
    """Conservative textual dependency matching, including direct test edits."""
    paths = tuple(Path(path).as_posix() for path in paths)
    stems = {
        Path(path).stem for path in paths
        if path.startswith(("joulewise/", "scripts/")) and path.endswith(".py")
    }
    selected = set()
    for module in modules:
        relative = module.replace(".", "/") + ".py"
        source = (root / relative).read_text(encoding="utf-8")
        if (relative in paths
                or any(Path(relative).stem.startswith(f"test_{stem}") for stem in stems)
                or any(stem in source for stem in stems)
                or any(path in source for path in paths)):
            selected.add(module)
    return frozenset(selected)


def select_modules(modules, timings, exclusive, splits, *, max_seconds=5.0,
                   tier="quick", touched=frozenset()):
    """Return selected/excluded reason maps; unknown weights never mean cheap.

    Unknown modules are ALL included in touched, even without a textual match.
    The docs fence is mandatory regardless of its measured weight.
    """
    selected, excluded = {}, {}
    for module in sorted(modules):
        reasons = []
        if module not in timings:
            reasons.append("unknown weight")
        elif timings[module] >= max_seconds:
            reasons.append(f"weight={timings[module]:.3f}s >= {max_seconds:g}s")
        if module in exclusive:
            reasons.append("exclusive")
        if module in splits:
            reasons.append("split")
        if module == DOCS_MODULE:
            selected[module] = "docs fence"
        elif tier == "touched" and (module in touched or module not in timings):
            selected[module] = "; ".join(
                (["touched path"] if module in touched else []) + reasons
            )
        elif not reasons:
            selected[module] = f"weight={timings[module]:.3f}s < {max_seconds:g}s"
        else:
            excluded[module] = "; ".join(reasons)
    return selected, excluded


@dataclass
class Result:
    name: str
    returncode: int
    seconds: float
    output: str
    rerun: str


def run_command(name: str, command: list[str], rerun: str) -> Result:
    """Pool workers launch pristine interpreters, one per module.

    /tmp is explicit: an inherited TMPDIR may point inside the checkout.
    Child TMPDIR/TEMP/TMP all point at a separate directory outside the repo.
    Campaign-registry fixtures also stay there, away from operator custody.
    """
    started = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix="joulewise-quick-", dir="/tmp") as tmp:
            tmp = str(Path(tmp).resolve())
            if Path(tmp).is_relative_to(ROOT.resolve()):
                raise ValueError("test temporary directory must be outside the repository")
            env = dict(os.environ, TMPDIR=tmp, TEMP=tmp, TMP=tmp,
                       PYTHONDONTWRITEBYTECODE="1",
                       JOULEWISE_CUSTODY_PARENT=str(Path(tmp) / "custody"),
                       JOULEWISE_ADDITIONAL_CUSTODY_PARENTS="[]",
                       R7F_CORPUS_ROOT=str(ROOT))
            process = subprocess.run(command, cwd=ROOT, env=env, text=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return Result(name, process.returncode, time.monotonic() - started,
                      process.stdout, rerun)
    except Exception as exc:
        return Result(name, 1, time.monotonic() - started,
                      f"{type(exc).__name__}: {exc}\n", rerun)


def module_job(module: str):
    # Only shard_tests owns test importing, load_tests hooks, and result policy.
    code = ("from scripts import shard_tests; import sys; "
            "sys.exit(shard_tests.run_shard((sys.argv[1],), 1, 1))")
    command = [sys.executable, "-c", code, module]
    rerun = shlex.join([sys.executable, str(Path(__file__).resolve()), "--module", module])
    return module, command, rerun


def report(result: Result) -> None:
    print(f"{'PASS' if result.returncode == 0 else 'FAIL'} {result.name} "
          f"seconds={result.seconds:.3f}", flush=True)
    if result.returncode:
        print(result.output, end="" if result.output.endswith("\n") else "\n")
        print(f"RERUN {result.rerun}", flush=True)


def positive_seconds(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be finite and positive")
    return number


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier", choices=("quick", "touched"), default="quick")
    parser.add_argument("--since", help="Git base (required for touched)")
    parser.add_argument("--max-seconds", type=positive_seconds, default=5.0)
    parser.add_argument("--workers", type=positive_int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--module", help="replay a single discovered module")
    args = parser.parse_args(argv)
    if args.tier == "touched" and not args.since and not args.module:
        parser.error("--tier touched requires --since")
    started = time.monotonic()
    try:
        modules = shard_tests.discover_test_modules()
        if args.module:
            if args.module not in modules:
                parser.error(f"module not discovered: {args.module}")
            result = run_command(*module_job(args.module))
            print(result.output, end="" if result.output.endswith("\n") else "\n")
            report(result)
            return int(result.returncode != 0)
        timings = shard_tests.load_timing_map()
        splits = shard_tests.load_split_declarations()
        payload = json.loads(shard_tests.DEFAULT_TIMINGS_PATH.read_text(encoding="utf-8"))
        exclusive = payload.get("exclusive_modules", {})
        if not isinstance(exclusive, dict):
            raise ValueError("exclusive_modules must be an object")
        paths = changed_paths(args.since) if args.tier == "touched" else ()
        touched = touched_modules(modules, paths) if paths else frozenset()
        selected, excluded = select_modules(
            modules, timings, exclusive, splits, max_seconds=args.max_seconds,
            tier=args.tier, touched=touched,
        )
        if DOCS_MODULE not in selected:
            raise ValueError(f"required fence module not discovered: {DOCS_MODULE}")
        for path in paths:
            print(f"CHANGED {path}")
        for module in modules:
            if module in selected:
                print(f"SELECT {module}: {selected[module]}")
            else:
                print(f"EXCLUDE {module}: {excluded[module]}")
        print(f"START tier={args.tier} modules={len(selected)} "
              f"excluded={len(excluded)} workers={args.workers}", flush=True)
        command = [sys.executable, str(ROOT / "scripts/gen_state.py"), "--check"]
        results = [run_command("gen_state", command, shlex.join(command))]
        report(results[0])
        # Keep the mandatory fence first; touched exclusive modules run alone
        # after the ordinary pool, preserving their scheduling declaration.
        docs = run_command(*module_job(DOCS_MODULE))
        results.append(docs)
        report(docs)
        pooled = set(selected) - {DOCS_MODULE} - set(exclusive)
        with ProcessPoolExecutor(max_workers=args.workers,
                                 mp_context=multiprocessing.get_context("spawn")) as pool:
            futures = {
                pool.submit(run_command, *module_job(module)): module
                for module in sorted(pooled, key=lambda m: (-timings.get(m, math.inf), m))
            }
            for future in as_completed(futures):
                module = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    result = Result(module, 1, 0.0, f"Worker failed: {exc}\n",
                                    module_job(module)[2])
                results.append(result)
                report(result)
        for module in sorted(set(selected) & set(exclusive) - {DOCS_MODULE}):
            result = run_command(*module_job(module))
            results.append(result)
            report(result)
        failures = sum(result.returncode != 0 for result in results)
        print(f"QUICK SUMMARY tier={args.tier} modules={len(selected)} "
              f"excluded={len(excluded)} failures={failures} "
              f"seconds={time.monotonic() - started:.3f} "
              f"result={'FAIL' if failures else 'PASS'}", flush=True)
        return int(bool(failures))
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"QUICK ERROR {exc}", file=sys.stderr)
        print(f"QUICK SUMMARY tier={args.tier} result=FAIL", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
