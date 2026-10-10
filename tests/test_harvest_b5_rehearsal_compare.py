"""Opt-in, structure-only replay of the admitted real rehearsal's screen.

Run with B5_REHEARSAL_COMPARE=1 and TMPDIR pointing into .scratch-fix.
Copies only required rehearsal bytes, preserves recorded paths through a
read-only filesystem map, and keeps all new outputs in memory.  No claim
root is accepted.  Both screens reuse the pinned archive's recorded primary
re-reductions; the unchanged, expensive estimator is not executed again.
"""
from __future__ import annotations

import builtins
import contextlib
import copy
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import joulewise
from joulewise import whole_window as working_ww
from joulewise.b5 import harvest as working_h

REPO = Path(__file__).resolve().parents[1]
PIN = "224a264c5faaae90cdf56118df37e773a932700b"
ARCHIVE = Path("/Users/edr/night-archive/gate-prune/rehearsal-real/corpus18-20261009T1949Z/archive-pinned")


def pinned_module(relative, name):
    raw = subprocess.run(["git", "show", f"{PIN}:{relative}"], cwd=REPO,
                         check=True, capture_output=True).stdout
    module = types.ModuleType(name)
    module.__file__ = str(REPO / relative)
    sys.modules[name] = module
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


@unittest.skipUnless(os.environ.get("B5_REHEARSAL_COMPARE") == "1", "opt-in real rehearsal replay")
class RealRehearsalComparison(unittest.TestCase):
    def test_pinned_and_working_screen_bytes_and_flags(self):
        scratch = REPO / ".scratch-fix"
        self.assertTrue(scratch.is_dir(), "create the authorized scratch directory first")
        tempfile.tempdir = str(scratch)
        with tempfile.TemporaryDirectory(prefix="rehearsal-", dir=scratch) as directory:
            local = Path(directory)
            source = ARCHIVE / "sources"
            row = json.loads((source / "claim-runs/whole-window-verdict.json").read_bytes())
            plan = json.loads((source / "night-custody/night_plan.json").read_bytes())
            claim = Path(row["evaluation_scope"]["runs_root"])
            bound = Path(working_h._plan_value(plan, "bound_runs_root"))
            custody = Path(working_h._plan_value(plan, "custody_root"))
            measurement = Path(working_h._plan_value(plan, "measurement_root"))
            roots = [(claim, local / "claim"), (bound, local / "bound"),
                     (custody, local / "custody"), (measurement, local / "repo")]
            for original, _ in roots:
                self.assertTrue(ARCHIVE.parent in original.parents, "only the open rehearsal may be replayed")
            for name, target in (("repo", "repo"), ("night-custody", "custody")):
                shutil.copytree(source / name, local / target)
            (local / "claim").mkdir()
            for path in (source / "claim-runs").iterdir():
                target = local / "claim" / path.name
                if path.is_file():
                    shutil.copy2(path, target)
                elif path.name == "campaign_manifests" or path.name.startswith("neg8-window"):
                    shutil.copytree(path, target)
                else:
                    # Evaluation-basis validation needs these bytes for every
                    # included science member, but no science raw streams.
                    target.mkdir()
                    for name in ("config.json", "metadata.json", "summary_metrics.json"):
                        if (path / name).is_file():
                            shutil.copy2(path / name, target / name)
            (local / "bound").mkdir()
            for path in (source / "bound-runs").iterdir():
                if path.is_file():
                    shutil.copy2(path, local / "bound" / path.name)
            bound_value = json.loads((local / "bound/neg8-drift-bound.json").read_bytes())
            corpus_bytes = (local / "custody/night/transcript/neg8-settled-corpus.collected.json").read_bytes()
            check = json.loads((ARCHIVE / "derived/neg8-bound.json").read_bytes())
            roster = json.loads((ARCHIVE / "derived/roster.json").read_bytes())
            members = json.loads((ARCHIVE / "withheld/member-assessments.json").read_bytes())["members"]
            stage_codes = {"neg8.corpus_member_dropped", "neg8.reference_lost", "neg8.midpoint_lost",
                           "neg8.screen_failed"}
            seed = [json.loads(line) for line in (ARCHIVE / "derived/flags.jsonl").read_bytes().splitlines()
                    if line.strip()]
            seed = [flag for flag in seed if flag["code"] not in stage_codes]
            old_h = pinned_module("joulewise/b5/harvest.py", "joulewise.b5._rehearsal_pinned_h")
            old_ww = pinned_module("joulewise/whole_window.py", "joulewise._rehearsal_pinned_ww")

            def mapped(path):
                if not isinstance(path, (str, bytes, os.PathLike)):
                    return path
                candidate = Path(os.fsdecode(path))
                for original, target in roots:
                    if candidate == original or original in candidate.parents:
                        return target / candidate.relative_to(original)
                # A replay dependency must never wander into blinded roots.
                text = str(candidate)
                if text.startswith(("/Users/edr/night-b5/", "/Users/edr/night-custody/v5-b5-",
                                    "/Users/edr/night-archive/harvest-v5-b5-")):
                    raise AssertionError("blinded dependency forbidden")
                return path

            real_open, real_io_open, real_stat = builtins.open, io.open, Path.stat
            real_iterdir, real_glob = Path.iterdir, Path.glob

            def open_copy(function, path, mode="r", *args, **kwargs):
                target = mapped(path)
                if target != path and any(flag in mode for flag in ("w", "a", "x", "+")):
                    raise AssertionError("rehearsal copy is read-only during replay")
                return function(target, mode, *args, **kwargs)

            def iterator(function, path, *args, **kwargs):
                target = Path(mapped(path))
                for value in function(target, *args, **kwargs):
                    yield path / value.relative_to(target) if target != path else value

            from joulewise import reduce as reducer
            reductions = {}
            recorded = {}
            for path in (ARCHIVE / "withheld/reductions").glob("neg8-window*.summary_metrics.rereduced.json"):
                raw = path.read_bytes()
                bundle_id = path.name.removesuffix(".summary_metrics.rereduced.json")
                self.assertTrue(members[bundle_id]["rereduced"]["sha256"] == working_h.sha256_bytes(raw),
                                "recorded reduction digest must authenticate")
                recorded[bundle_id] = json.loads(raw)

            def reduce_once(path, *args, **kwargs):
                key = (str(path), repr(args), repr(sorted(kwargs.items())))
                if key not in reductions:
                    summary = recorded[path.name]
                    reductions[key] = SimpleNamespace(to_dict=lambda: copy.deepcopy(summary))
                return reductions[key]

            snapshots = []
            with contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(builtins, "open", lambda p, *a, **k:
                                                     open_copy(real_open, p, *a, **k)))
                stack.enter_context(mock.patch.object(io, "open", lambda p, *a, **k:
                                                     open_copy(real_io_open, p, *a, **k)))
                stack.enter_context(mock.patch.object(Path, "stat", lambda p, *a, **k:
                                                     real_stat(Path(mapped(p)), *a, **k)))
                stack.enter_context(mock.patch.object(Path, "iterdir", lambda p:
                                                     iterator(real_iterdir, p)))
                stack.enter_context(mock.patch.object(Path, "glob", lambda p, *a, **k:
                                                     iterator(real_glob, p, *a, **k)))
                stack.enter_context(mock.patch.object(reducer, "reduce_bundle", reduce_once))
                for module, ww in ((old_h, old_ww), (working_h, working_ww)):
                    output = {}

                    def write(path, raw):
                        relative = str(path.relative_to(ARCHIVE))
                        if relative in output:
                            raise AssertionError("output repeated")
                        output[relative] = raw
                        return module.sha256_bytes(raw)

                    def write_json(path, value):
                        return write(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode())

                    run = object.__new__(module._Harvest)
                    run.inputs = SimpleNamespace(claim_runs_root=claim, bound_runs_root=bound, plan=plan)
                    run.archive, run.derived, run.withheld = ARCHIVE, ARCHIVE / "derived", ARCHIVE / "withheld"
                    run.repo_root_copy = local / "repo"
                    run.pack_copy = run.repo_root_copy / Path(working_h._plan_value(plan, "pack_root")).relative_to(measurement)
                    run.roster, run.members, run.outputs = copy.deepcopy(roster), copy.deepcopy(members), {}
                    run.neg8, run.neg8_bound_value = copy.deepcopy(check), copy.deepcopy(bound_value)
                    run.neg8_corpus_bytes, run.neg8_collected_bound = corpus_bytes, copy.deepcopy(bound_value)
                    catalog = module.Catalog.load(source / "inputs/flag_catalog.json")
                    run.flags = module.FlagLedger(plan_id=plan["plan_id"], attempt=plan.get("attempt"),
                                                  catalog=catalog, boot_session_uuid="rehearsal-replay",
                                                  now=lambda: 0.0, monotonic_ns=lambda: 0)
                    run.flags._records = {flag["flag_id"]: copy.deepcopy(flag) for flag in seed}
                    initial_ids = set(run.flags._records)
                    with mock.patch.object(joulewise, "whole_window", ww), \
                            mock.patch.dict(sys.modules, {"joulewise.whole_window": ww}), \
                            mock.patch.object(module, "write_once", write), \
                            mock.patch.object(module, "write_json_once", write_json):
                        run.neg8_corpus_physics()
                        result = run.neg8_screen(row)
                        run.neg8_allowance(row, result)
                    emitted = [flag for flag in run.flags.records if flag["flag_id"] not in initial_ids]
                    snapshots.append((output, json.dumps(emitted, sort_keys=True).encode()))
                    screen = json.loads(output["derived/neg8-screen.json"])
                    self.assertTrue(screen["rescreen"]["evaluated"], "real rehearsal screen must execute")
                    self.assertTrue(screen["rescreen"]["decision"] == "passed", "real rehearsal must pass")
                    self.assertTrue(run.neg8_clean_bound is not None, "real clean bound must validate")
            self.assertTrue(snapshots[0][0] == snapshots[1][0], "pinned/working output bytes differ")
            self.assertTrue(snapshots[0][1] == snapshots[1][1], "pinned/working emitted flags differ")
            derived = {name: raw for name, raw in snapshots[0][0].items() if name.startswith("derived/")}
            self.assertTrue(len(derived) == 4, "all four derived screen records must be compared")
            self.assertTrue(all(raw == (ARCHIVE / name).read_bytes() for name, raw in derived.items()),
                            "replayed derived bytes differ from the archived pinned outputs")
            self.assertTrue(len(reductions) > 0, "recorded primary reference reductions must be replayed")
            print("rehearsal_derived_byte_identity PASS")
            print("rehearsal_withheld_byte_identity PASS")
            print("rehearsal_emitted_flags_equal PASS")
            print("rehearsal_archived_derived_byte_identity PASS")
            print("rehearsal_derived_records", len(derived))
            print("rehearsal_recorded_reductions", len(reductions))


if __name__ == "__main__":
    unittest.main()
