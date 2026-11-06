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

_PACK_WORKER = None


def pool_runtime(action, directory, count, payload=None):
    """One barrier-held probe per existing worker, outside the step timer."""
    from joulewise import analysis_member_pool as members
    from joulewise.b5_analysis import pack_parallel as pp
    root = Path(directory)
    (root / str(os.getpid())).touch()
    deadline = time.monotonic() + 30
    while len(list(root.iterdir())) < count:
        if time.monotonic() >= deadline:
            raise RuntimeError('synthetic worker-cache barrier timed out')
        time.sleep(.01)
    if action == 'restore':
        members._WORKER_PHYSICS, members._WORKER_MEMOS = pp.loads(payload)
        return None
    return pp.dumps((members._WORKER_PHYSICS, members._WORKER_MEMOS))


def snapshot_workers(caches):
    pool = caches.pool
    if pool is None:
        return None
    count = len(pool._processes)
    if not count:
        return None
    wait_idle(pool, count)
    with tempfile.TemporaryDirectory(prefix='speed-worker-cache-') as directory:
        futures = [pool.submit(pool_runtime, 'snapshot', directory, count) for _ in range(count)]
        states = [future.result() for future in futures]
        wait_idle(pool, count)
        return states


def wait_idle(pool, count):
    # Future completion precedes the executor manager's idle-permit release.
    # Wait for it so probing/restoring cannot accidentally start another slot.
    deadline = time.monotonic() + 5
    while pool._idle_worker_semaphore._value < count:
        if time.monotonic() >= deadline:
            raise RuntimeError('synthetic worker-cache pool did not become idle')
        time.sleep(.001)


def restore_workers(caches, states):
    if not states:
        return
    from joulewise import analysis_member_pool as members
    pool = members._pool(caches)
    with tempfile.TemporaryDirectory(prefix='speed-worker-cache-') as directory:
        futures = [pool.submit(pool_runtime, 'restore', directory, len(states), state) for state in states]
        for future in futures:
            future.result()
        wait_idle(pool, len(states))


def retain_synthetic_prefix(state, pack):
    """Retain immutable synthetic inputs after both pack computations finish."""
    if os.environ.get('JW_B5_SPEED_RETAIN_PREFIX') != '1':
        return
    root = state.repo_root.parent
    temporary = Path(os.environ['TMPDIR'])
    backup = temporary / ('stage2-retained-' + root.name)
    if (backup / 'paths.json').exists():
        return
    (root / (pack + '-done')).touch()
    if not all((root / (p + '-done')).exists() for p in ('alpha', 'beta')):
        return
    try:
        with (root / 'backup-started').open('x'):
            pass
    except FileExistsError:
        return
    inputs = state.windows['alpha'].archive_root.parent.parent
    if inputs.parent != temporary or not inputs.name.startswith('s10-chain-'):
        raise AssertionError('restart retention requires this benchmark\'s synthetic S10 root')
    ignore = lambda _path, names: [name for name in names if name == 'restricted']
    shutil.copytree(inputs, backup / 'inputs', copy_function=os.link, symlinks=True, ignore=ignore)
    shutil.copytree(state.repo_root, backup / 'harness/repository', copy_function=os.link, symlinks=True, ignore=ignore)
    prefix = root / 'prefix-10'
    shutil.copytree(prefix if prefix.exists() else root / 'prefix', backup / 'harness/prefix',
                    copy_function=os.link, symlinks=True, ignore=ignore)
    (backup / 'paths.json').write_text(json.dumps(dict(inputs=str(inputs), harness=str(root)))+'\n')


def synthetic_pack_worker(task):
    """Apply JoinedHarness's existing Git observations inside spawned openers."""
    from joulewise.b5_analysis import pack_parallel as pp
    if task.function != 'joulewise.b5_analysis.reported_parallel:reported_pack':
        return _PACK_WORKER(task)
    from tests.b5_analysis.joined_s10 import JoinedHarness
    (state, _pack, _counter), _kwargs = pp.loads(task.payload)
    harness = object.__new__(JoinedHarness)
    harness.repo, harness.head = state.repo_root, state.commit
    if _pack == 'alpha' and os.environ.get('JW_B5_SPEED_RETAIN_PREFIX') == '1':
        # A synthetic-only restart point avoids repeating a long joined prefix
        # for the next slice. Input bytes must be retained at these same paths.
        saved = copy(state)
        saved.restricted = harness.repo.parent / 'artifacts'
        checkpoint = Path(os.environ['TMPDIR']) / ('stage2-before10-' + harness.repo.parent.name + '.pkl')
        checkpoint.write_bytes(pp.dumps((saved, task.physics, task.vdl.get('entries'),
                                         task.vdl.get('memos'), _counter)))
    started = time.perf_counter()
    with harness.git_seams():
        outcome = _PACK_WORKER(task)
    wall = time.perf_counter() - started
    retain_synthetic_prefix(state, _pack)
    event = dict(function=task.function, pack=_pack, workers=task.workers, ok=outcome.ok,
                 pid=os.getpid(), wall_s=wall,
                 status=pp.loads(outcome.value)[0][0].status if outcome.ok else None)
    path = Path(os.environ['TMPDIR']) / 'stage2-worker-events.jsonl'
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(descriptor, (json.dumps(event, sort_keys=True)+'\n').encode())
    finally:
        os.close(descriptor)
    return outcome


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
            path = Path(os.path.abspath(os.fsdecode(path)))
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
    parser.add_argument('--resume-prefix', type=Path,
                        help='this benchmark\'s synthetic before-10 pickle, with inputs retained at identical paths')
    parser.add_argument('--fresh-prefix', action='store_true',
                        help='replay the real joined prefix for both timings, preserving naturally warm workers')
    parser.add_argument('--retain-prefix', action='store_true',
                        help='retain synthetic inputs for restart; includes backup overhead, so use a clean timing rerun')
    args = parser.parse_args(argv)
    temporary = Path(os.environ['TMPDIR']).absolute()
    if temporary.is_relative_to('/Users/edr') or 'restricted' in temporary.parts:
        parser.error('TMPDIR must be outside /Users/edr and restricted/')
    if not args.output.absolute().is_relative_to(temporary):
        parser.error('output must be under TMPDIR')
    if args.resume_prefix is not None and not args.resume_prefix.absolute().is_relative_to(temporary):
        parser.error('synthetic restart must be under TMPDIR')
    os.environ.update(GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1', GIT_NO_LAZY_FETCH='1',
                      JW_B5_S10_REAL_PROGRAMS='1', JOULEWISE_B5_ANALYSIS_WORKERS='3')
    if args.retain_prefix:
        os.environ['JW_B5_SPEED_RETAIN_PREFIX'] = '1'
    safe_paths()
    from tests.b5_analysis.fixtures_s10 import chain_fixture
    from tests.b5_analysis.joined_s10 import JoinedHarness
    from joulewise.analysis_run_cache import analysis_run_caches
    from joulewise.analysis_verified_store import resolve_mode
    from joulewise.b5_analysis.deadline_observer import observe_wall_deadline
    from joulewise.whole_window import shared_instrument_calibration_physics_cache

    from joulewise.b5_analysis import pack_parallel as pp
    initial = None
    if args.resume_prefix is None:
        print('Restoring committed synthetic S10 windows', flush=True)
        fixture = chain_fixture()
        harness = JoinedHarness(fixture.index)
    else:
        initial = args.resume_prefix.read_bytes()
        seed, *_ = pp.loads(initial)
        harness = object.__new__(JoinedHarness)
        harness.repo, harness.head, harness.index = seed.repo_root, seed.commit, seed.index_path
        harness.root, harness.pins, harness.pack_table = seed.repo_root.parent, seed.pins, seed.pack_table
        harness.close = lambda: None
        if args.step not in ('10', '11') or args.fresh_prefix:
            initial = None  # Reuse only the immutable synthetic inputs for an earlier slice.
        print('Reusing this benchmark\'s retained synthetic inputs', flush=True)
    result = dict(synthetic_only=True, baseline=args.baseline, step=args.step, workers=3,
                  fixture='committed S10 full-size production-dispatch joined window',
                  resumed_synthetic_prefix=args.resume_prefix is not None, runs={})
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
            seed = checkpoint if label == 'after' and not args.fresh_prefix else initial
            prefix = harness.root / ('prefix-' + args.step if label == 'after' else 'prefix')
            if seed is None:
                artifacts.mkdir()
                state = d.RunState('blind-dry-run', harness.index, artifacts, harness.head,
                                   seal_pins=harness.pins, repo_root=harness.repo)
                physics, entries, memos, counter, worker_states = {}, None, None, 0, None
            else:
                shutil.copytree(prefix, artifacts)
                saved = pp.loads(seed)
                state, physics, entries, memos, counter = saved[:5]
                worker_states = saved[5] if len(saved) > 5 else None
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
                restore_workers(caches, worker_states)
                reached = initial is None or label == 'after'
                for step, function in d.STEPS:
                    if not reached:
                        if step != '10':
                            continue
                        reached = True
                    if label == 'after' and not args.fresh_prefix and step != args.step:
                        continue
                    if owner is d and name == 'step_10' and step == '10':
                        function = implementation
                    if label == 'before' and step == args.step:
                        saved = copy(state)
                        saved._runner, saved.vdl_store, saved.deadline = None, None, None
                        checkpoint = pp.dumps((saved, physics, caches.vdl.export_entries(),
                                               caches.memos, runner._counter, snapshot_workers(caches)))
                        prefix = harness.root / ('prefix-' + args.step)
                        if prefix.exists():
                            shutil.rmtree(prefix)
                        shutil.copytree(artifacts, prefix)
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
    from joulewise.b5_analysis import pack_parallel as pp
    _PACK_WORKER = pp.run_pack
    pp.run_pack = synthetic_pack_worker
