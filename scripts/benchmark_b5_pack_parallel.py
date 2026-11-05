#!/usr/bin/env python3
"""Synthetic S10 joined-window pack timing/equality; never accepts a data index.

Dispatch through RunState/StepRunner with artifacts/ custody. The public driver
entry point creates restricted/, so it is deliberately not called here.
"""
from __future__ import annotations

import argparse
from copy import copy
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
from unittest.mock import patch

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from joulewise.b5_analysis import dry_run as d
from scripts.benchmark_b5_speed_plan import baseline_function, digest


def safe_paths():
    """Reject blinded paths even if an input accidentally retains an old locator."""
    root = Path(__file__).absolute().parents[1]

    realpath = os.path.realpath

    def contained_realpath(path, *, strict=False):
        absolute = Path(os.path.abspath(path))
        check(absolute)
        if not absolute.is_relative_to(root):
            return realpath(path, strict=strict)
        # Resolve only beneath the already-known checkout root. Ordinary
        # realpath also lstats every ancestor outside this clone.
        cursor = root
        for part in absolute.relative_to(root).parts:
            cursor = cursor / part
            try:
                if os.path.islink(cursor):
                    target = Path(os.readlink(cursor))
                    cursor = Path(contained_realpath(target if target.is_absolute() else cursor.parent / target,
                                                     strict=strict))
            except OSError:
                if strict:
                    raise
        return str(cursor)

    def check(path):
        if isinstance(path, (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(path)).absolute()
            if 'restricted' in path.parts or (path.is_relative_to('/Users/edr') and not path.is_relative_to(root)):
                raise RuntimeError('benchmark attempted a forbidden path')

    def audit(event, args):
        if event in ('open', 'os.listdir', 'os.scandir', 'os.chdir'):
            check(args[0])
    sys.addaudithook(audit)
    os.path.realpath = contained_realpath
    for name in ('stat', 'lstat'):
        original = getattr(os, name)

        def guarded(path, *args, _original=original, **kwargs):
            check(path)
            return _original(path, *args, **kwargs)
        setattr(os, name, guarded)


def snapshot(state, records):
    outputs = dict(state.outputs)
    for item in outputs.values():
        if hashlib.sha256((state.restricted / item['name']).read_bytes()).hexdigest() != item['sha256']:
            raise AssertionError('registered output bytes changed')
    census = {p: [vars(row) for row in a.census()] for p, a in state.archives.items()}
    rows = [r.as_dict() for r in records]
    return dict(outputs=outputs, records=rows, census=census,
                outputs_sha256=digest(outputs), records_sha256=digest(rows), census_sha256=digest(census))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--step', choices=('3b', '10', '11', '5'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    temporary = Path(os.environ['TMPDIR']).absolute()
    if temporary.is_relative_to('/Users/edr') or 'restricted' in temporary.parts:
        parser.error('TMPDIR must be outside /Users/edr and restricted/')
    if not args.output.absolute().is_relative_to(temporary):
        parser.error('output must be under TMPDIR')
    os.environ.update(GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1', GIT_NO_LAZY_FETCH='1',
                      JW_B5_S10_REAL_PROGRAMS='1', JOULEWISE_B5_ANALYSIS_WORKERS='3')
    safe_paths()
    from tests.b5_analysis.fixtures_s10 import chain_fixture
    from tests.b5_analysis.joined_s10 import JoinedHarness
    from joulewise.analysis_run_cache import analysis_run_caches
    from joulewise.analysis_verified_store import resolve_mode
    from joulewise.b5_analysis.deadline_observer import observe_wall_deadline
    from joulewise.whole_window import shared_instrument_calibration_physics_cache

    print('Restoring committed synthetic S10 windows', flush=True)
    fixture = chain_fixture()
    harness = JoinedHarness(fixture.index)
    result = dict(synthetic_only=True, baseline=args.baseline, step=args.step, workers=3,
                  fixture='committed S10 full-size production-dispatch joined window', runs={})
    if args.step == '3b':
        owner, name, cls = d.RunState, 'prepare_brackets', 'RunState'
        old = baseline_function(args.baseline, d, name, cls)
    elif args.step == '10':
        owner, name = d, 'step_10'
        old = baseline_function(args.baseline, d, name)
    elif args.step == '11':
        from joulewise.b5_analysis import sensitivity
        owner, name = sensitivity, 'sensitivity_pass'
        old = baseline_function(args.baseline, sensitivity, name)
    else:
        from scripts import emit_floor_mint_pinset as emit
        owner, name = emit, 'emit_indexed_pinset'
        old = baseline_function(args.baseline, emit, name)
    current = getattr(owner, name)
    checkpoint = None
    try:
        # Identical input and output locators on both runs, with a fresh run
        # store. All registered bytes, rows and archive censuses are compared.
        for label, implementation in (('before', old), ('after', current)):
            artifacts = harness.root / 'artifacts'
            if artifacts.exists():
                shutil.rmtree(artifacts)
            from joulewise.b5_analysis import pack_parallel as pp
            if checkpoint is None:
                artifacts.mkdir()
                state = d.RunState('blind-dry-run', harness.index, artifacts, harness.head,
                                   seal_pins=harness.pins, repo_root=harness.repo)
                physics, entries, memos, counter = {}, None, None, 0
            else:
                shutil.copytree(harness.root / 'prefix', artifacts)
                state, physics, entries, memos, counter = pp.loads(checkpoint)
            runner = d.StepRunner(artifacts)
            runner._counter = counter
            times = {}
            with ExitStack() as stack:
                stack.enter_context(harness.git_seams())
                stack.enter_context(patch.object(owner, name, implementation))
                stack.enter_context(shared_instrument_calibration_physics_cache(physics))
                caches = stack.enter_context(analysis_run_caches(physics, workers=3,
                    memos=memos, vdl_entries=entries,
                    vdl_mode=resolve_mode('on', synthetic=True), vdl_commit=harness.head))
                deadline = stack.enter_context(observe_wall_deadline())
                caches.deadline = deadline
                state.workers, state.deadline, state.physics_store = 3, deadline, physics
                state.vdl_store, state._runner = caches.vdl, runner
                for step, function in d.STEPS:
                    if label == 'after' and step != args.step:
                        continue
                    if owner is d and name == 'step_10' and step == '10':
                        function = implementation
                    if label == 'before' and step == args.step:
                        saved = copy(state)
                        saved._runner, saved.vdl_store, saved.deadline = None, None, None
                        checkpoint = pp.dumps((saved, physics, caches.vdl.export_entries(),
                                               caches.memos, runner._counter))
                        shutil.copytree(artifacts, harness.root / 'prefix')
                    started = time.perf_counter()
                    rows = function(state, runner)
                    times[step] = time.perf_counter() - started
                    state.step_records.extend(rows)
                    print(label, step, [r.status for r in rows], f'{times[step]:.3f}s', flush=True)
                    if any(r.status != 'ok' and not d.is_nonstopping_outcome(r) for r in rows):
                        args.output.write_text(json.dumps(dict(result, failure=snapshot(state, rows)), indent=2)+'\n')
                        raise AssertionError('synthetic joined run refused at step ' + step)
                    if step == args.step:
                        break
            result['runs'][label] = dict(wall_s=times, **snapshot(state, state.step_records))
        for field in ('outputs', 'records', 'census'):
            if result['runs']['before'][field] != result['runs']['after'][field]:
                raise AssertionError('synthetic joined mismatch: ' + field)
        result['digests_equal'] = True
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        print(json.dumps(dict(digests_equal=True, step=args.step,
            before_s=result['runs']['before']['wall_s'][args.step],
            after_s=result['runs']['after']['wall_s'][args.step])), flush=True)
    finally:
        harness.close()


if __name__ == '__main__':
    main()
elif __name__ == '__mp_main__':
    safe_paths()
