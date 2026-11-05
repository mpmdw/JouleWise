#!/usr/bin/env python3
"""Bounded, synthetic-only before/after profile for the post-release speed plan.

Uses the repository's committed S0 window builder and S2 timing-only adapter.
No study index, real-data path or analysis CLI is accepted. The default run
does not create or open a restricted/ directory. Run from the repository with
an explicit TMPDIR outside /Users/edr and keep the JSON/profile files there.
"""
from __future__ import annotations

import argparse
import ast
import atexit
from bisect import bisect_left
import cProfile
from contextlib import nullcontext
import hashlib
import json
import os
from pathlib import Path
import pstats
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def canonical(value):
    from joulewise.b5_analysis.dry_run import _plain
    return json.dumps(_plain(value), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def baseline_function(reference, module, name, class_name=None):
    relative = Path(module.__file__).relative_to(ROOT).as_posix()
    source = subprocess.run(["git", "-C", str(ROOT), "show", reference + ":" + relative],
                            check=True, capture_output=True, text=True).stdout
    nodes = ast.parse(source).body
    if class_name:
        nodes = next(node.body for node in nodes if isinstance(node, ast.ClassDef) and node.name == class_name)
    node = next(node for node in nodes if isinstance(node, ast.FunctionDef) and node.name == name)
    namespace = dict(vars(module))
    exec(compile(ast.Module(body=[node], type_ignores=[]), "baseline/" + relative, "exec"), namespace)
    return namespace[name]


def _bundle_files(inventory, relative):
    """Experimental prefix index, retained in the benchmark only."""
    prefix = relative + "/"
    position = bisect_left(inventory, prefix)
    while position < len(inventory) and inventory[position].startswith(prefix):
        yield inventory[position]
        position += 1


def indexed_candidate(function):
    """Apply the measured, deferred indexing experiment to the reference AST.

    Keep the full copy/selection function identical except the inventory scan.
    Refuse source drift instead of silently benchmarking another operation.
    """
    import inspect
    node = ast.parse(inspect.getsource(function)).body[0]
    loops = [part for part in ast.walk(node) if isinstance(part, ast.For)
             and ast.unparse(part.target) == "name" and ast.unparse(part.iter) == "sorted(inventory)"]
    if len(loops) != 1 or ast.unparse(loops[0].body[0]) != "if not name.startswith(relative + '/'):\n    continue":
        raise ValueError("bracket inventory loop changed; re-review benchmark")
    loop = loops[0]
    loop.iter = ast.parse("_bundle_files(_ordered_inventory, relative)", mode="eval").body
    loop.body = loop.body[1:]
    inserts = 0
    for part in ast.walk(node):
        for field, statements in ast.iter_fields(part):
            if field != "body" or not isinstance(statements, list):
                continue
            for position, statement in enumerate(statements):
                if isinstance(statement, ast.Assign) and ast.unparse(statement) == "copies, failed = ([], None)":
                    statements.insert(position, ast.parse("_ordered_inventory = sorted(inventory)").body[0])
                    inserts += 1
                    break
    if inserts != 1:
        raise ValueError("bracket copy setup changed; re-review benchmark")
    namespace = dict(function.__globals__, _bundle_files=_bundle_files)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 "candidate/bracket.py", "exec"), namespace)
    return namespace[function.__name__]


def census_profile(built, bulk):
    from tests.b5_analysis import fixtures_s2 as fx
    handle = fx.handle(built)
    names = handle.source_names()
    started, cpu = time.perf_counter(), time.process_time()
    if bulk:
        handle.census_sources(names)
    else:
        for name in names:
            handle.source_bytes("sources/" + name)
    return {"wall_s": time.perf_counter() - started, "cpu_s": time.process_time() - cpu,
            "source_files": len(names),
            "census_sha256": digest([vars(row) for row in handle.census()])}


def bracket_profile(built, function, profile_path=None):
    from joulewise.b5_analysis import bracket
    from tests.b5_analysis import fixtures_s2 as fx
    handle = fx.handle(built)
    inputs = bracket._Inputs(handle)
    profiler = cProfile.Profile() if profile_path else None
    # Time actual copy-out and selection, including authenticated reads and
    # the S2 strict-validation seam. Hash outputs AFTER stopping the timer.
    with tempfile.TemporaryDirectory(prefix="speed-benchmark-") as tmp, fx.capture_adapter():
        destination = Path(tmp)
        started, cpu = time.perf_counter(), time.process_time()
        with profiler if profiler else nullcontext():
            paths = function(handle, inputs, destination)
        measurement = {"wall_s": time.perf_counter() - started, "cpu_s": time.process_time() - cpu,
                       "selected_bundles": len(paths)}
        copied = {path.relative_to(destination).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in destination.rglob("*") if path.is_file()}
        measurement.update(copied_files=len(copied), copied_sha256=digest(copied),
                           selection_sha256=digest([path.relative_to(destination).as_posix() for path in paths]),
                           census_sha256=digest([vars(row) for row in handle.census()]))
    if profiler:
        profiler.dump_stats(profile_path)
        stats = pstats.Stats(profiler)
        top = sorted(stats.stats.items(), key=lambda pair: pair[1][3], reverse=True)[:12]
        measurement["profile_top"] = [{"function": f"{Path(key[0]).name}:{key[1]}:{key[2]}",
                                       "calls": value[1], "cumulative_s": value[3]}
                                      for key, value in top]
    return measurement


def full_size_copy_window(built, count):
    """Expand only the S2 copy/selection workload; no fake claim validation.

    S2's strict timing stubs and archived bytes are explicit fixture seams.
    Extra, distinct roster ids copy those synthetic bundles. Rebind the
    archive inventory and output digests using its existing builder helpers.
    This window is never handed to a claim consumer or the analysis driver.
    """
    from tests.b5_analysis import fixtures_s2 as fx
    root = Path(tempfile.mkdtemp(prefix="speed-full-size-"))
    atexit.register(shutil.rmtree, root, ignore_errors=True)
    expanded = fx.fork(built, root)
    sources = expanded.archive / "sources/claim-runs"
    roster_path = expanded.archive / "derived/roster.json"
    assessments_path = expanded.archive / "withheld/member-assessments.json"
    roster = json.loads(roster_path.read_bytes())
    assessments = json.loads(assessments_path.read_bytes())
    members = {row["run_id"]: row for row in roster["members"]}
    candidates = sorted(name for name, row in assessments["members"].items()
                        if name in members and row.get("strict_valid") and row.get("status") == "succeeded"
                        and row.get("anchor_recorded") == "bounded" and (sources / name).is_dir())
    if not candidates or count < len(candidates):
        raise ValueError("full-size count must cover the original selected S2 bundles")
    for number in range(count - len(candidates)):
        source_id = candidates[number % len(candidates)]
        run_id = f"speed-synthetic-extra-{number:04d}"
        shutil.copytree(sources / source_id, sources / run_id)
        roster["members"].append({**members[source_id], "run_id": run_id})
        assessments["members"][run_id] = {**assessments["members"][source_id],
                                         "bundle_path": str(expanded.claim / run_id)}
    fx.s0.put(roster_path, roster)
    fx.s0.put(assessments_path, assessments)
    fx.refresh(expanded)
    return expanded


def joined_step0(reference, pairs):
    """Use JoinedHarness's real inputs/Git seams, with a literal-ban-safe path.

    Run only step 0 through its real StepRunner, using artifacts/ as the
    RunState custody directory. Do not invoke run(), whose fixed directory
    name is restricted/. No later step is represented as having run.
    """
    from joulewise.b5_analysis import dry_run as d
    from tests.b5_analysis import fixtures as fx, fixtures_s3 as s3, fixtures_s3b as sb
    from tests.b5_analysis.joined_s10 import JoinedHarness
    built = {pack: sb.cached("BETA_STD") if pack == "beta" else s3.cached(pack.upper() + "_STD")
             for pack in d.PACKS}
    rows = [window.entry_data for window in built.values()]
    beta = built["beta"].entry_data
    rows = [{**beta, "attempt": n, "entry_kind": "no_archive", "archive_root": None,
             "harvest_record_sha256": None, "verdict": "NO_COLLECTION", "claim_usable": False,
             "record_citation": "synthetic-history.md:1"} for n in range(1, beta["attempt"])] + rows
    old = baseline_function(reference, d, "prepare_initial", "RunState")
    current = d.RunState.prepare_initial
    measured = []
    with tempfile.TemporaryDirectory(prefix="speed-joined-inputs-") as tmp:
        index = Path(tmp) / "index.json"
        index.write_bytes(d._canonical({"schema": "joulewise.b5_window_index.v1", "attempts": rows}))
        harness = JoinedHarness(index, windows=built.values(), pack_table=fx.PACK_TABLE)
        try:
            for pair in range(pairs):
                result = {}
                for name in (("before", "after") if pair % 2 == 0 else ("after", "before")):
                    artifacts = harness.root / f"{pair}-{name}" / "artifacts"
                    artifacts.mkdir(parents=True)
                    state = d.RunState("blind-dry-run", harness.index, artifacts, harness.head,
                                       pack_table=fx.PACK_TABLE, seal_pins=harness.pins, repo_root=harness.repo)
                    runner = d.StepRunner(artifacts)
                    started, cpu = time.perf_counter(), time.process_time()
                    with patch.object(d.RunState, "prepare_initial", old if name == "before" else current):
                        records = d.step_0(state, runner)
                    result[name] = {"wall_s": time.perf_counter() - started,
                                    "cpu_s": time.process_time() - cpu,
                                    "outputs_sha256": digest(state.outputs),
                                    "records_sha256": digest([r.as_dict() for r in records]),
                                    "source_files": sum(len(a.source_names()) for a in state.archives.values())}
                    if [r.status for r in records] != ["ok"]:
                        raise AssertionError("synthetic joined step 0 refused")
                for field in ("outputs_sha256", "records_sha256"):
                    if result["before"][field] != result["after"][field]:
                        raise AssertionError("synthetic joined step 0 mismatch: " + field)
                measured.append(result)
        finally:
            harness.close()
    return measured


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, help="Git code reference; never a data root")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pairs", type=int, default=3, choices=range(1, 6))
    parser.add_argument("--joined-step0", action="store_true", help="also time joined synthetic step 0")
    parser.add_argument("--bundle-count", type=int, default=125, choices=range(57, 251),
                        help="S2 copy workload size, not a claim-bearing analysis window")
    args = parser.parse_args(argv)
    temporary = Path(os.environ["TMPDIR"]).absolute()
    if str(temporary).startswith("/Users/edr/") or "restricted" in temporary.parts:
        parser.error("TMPDIR must be outside /Users/edr and restricted/")
    temporary = temporary.resolve(strict=True)
    output = args.output.absolute()
    if not output.is_relative_to(temporary) or "restricted" in output.parts:
        parser.error("output must be under TMPDIR, outside restricted/")
    os.environ["GIT_CONFIG_GLOBAL"] = "/dev/null"
    os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
    from joulewise.b5_analysis import bracket
    from tests.b5_analysis import fixtures_s2 as fx
    before = baseline_function(args.baseline, bracket, "_window_inputs")
    candidate = indexed_candidate(bracket._window_inputs)
    built = full_size_copy_window(fx.build_named("ALPHA_STD"), args.bundle_count)
    result = {"synthetic_only": True, "fixture": "S2 ALPHA_STD expanded for copy/selection only",
              "target_bundles": args.bundle_count,
              "bracket_candidate": "prefix indexing; deferred from production (no reliable wall gain)",
              "implemented": "step-0 ordered bulk census only",
              "baseline": args.baseline, "python": sys.version.split()[0], "worker_processes": 0,
              "concurrent_load": "User reports an ongoing seven-worker study analysis; not inspected",
              "pairs": {"bracket": [], "census": []}}
    for pair in range(args.pairs):
        # Alternate order to reduce systematic cache-warming bias.
        order = ("before", "after") if pair % 2 == 0 else ("after", "before")
        bracket_rows, census_rows = {}, {}
        for name in order:
            bracket_rows[name] = bracket_profile(built, before if name == "before" else candidate)
            census_rows[name] = census_profile(built, name == "after")
        for field in ("copied_sha256", "selection_sha256", "census_sha256"):
            if bracket_rows["before"][field] != bracket_rows["after"][field]:
                raise AssertionError("synthetic bracket mismatch: " + field)
        if census_rows["before"]["census_sha256"] != census_rows["after"]["census_sha256"]:
            raise AssertionError("synthetic census mismatch")
        result["pairs"]["bracket"].append(bracket_rows)
        result["pairs"]["census"].append(census_rows)
    result["profiles"] = {name: bracket_profile(built, fn, output.with_suffix("." + name + ".prof"))
                          for name, fn in (("before", before), ("after", candidate))}
    if args.joined_step0:
        result["pairs"]["joined_step0"] = joined_step0(args.baseline, args.pairs)
    result["median_wall_s"] = {kind: {name: statistics.median(row[name]["wall_s"] for row in rows)
                                     for name in ("before", "after")}
                               for kind, rows in result["pairs"].items()}
    result["digests_equal"] = True
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "median_wall_s": result["median_wall_s"], "digests_equal": True}))


if __name__ == "__main__":
    main()
