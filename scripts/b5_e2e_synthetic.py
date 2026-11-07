#!/usr/bin/env python3
"""Full joined block-5 driver on the committed S10 SYNTHETIC windows: timing and digests.

Never accepts a data index and never touches real measurements. It restores the
committed S10 production-dispatch fixtures (tests/fixtures/b5_analysis/s10) and
runs the real ``dry_run.run`` through ``JoinedHarness.execute`` (Python-only test
seams, so the run is synthetic), with the D-188 phase timers' restricted tier.

Every locator is deterministic: the restored chain, the scratch Git repository
and the custody root live at fixed paths under ``--scratch`` and the scratch
repository's commit dates are fixed. Two runs of different analysis code at the
same ``--scratch`` path therefore produce byte-comparable custody trees, so the
manifest written here can be compared across runs (and across machines with the
same scratch path) file by file. The D-188 comparator
(tools/b5_equivalence/compare_b5_results.py) can then adjudicate any difference.

    TMPDIR=/tmp/jwb5e2e/tmp python3.13 -B scripts/b5_e2e_synthetic.py \\
        --scratch /tmp/jwb5e2e/run --out /tmp/jwb5e2e/out/head --workers 7

Writes OUT/summary.json (exit code, wall, per-step wall/cpu from the restricted
timer, record digest, full custody manifest), OUT/runtime-phases.jsonl and
OUT/detail.txt (scripts/b5_phase_report.py --detail). ``--keep-custody`` moves
the custody tree to OUT/custody for the comparator. ``--cprofile DIR`` writes
per-step cProfile stats of the driver and of every spawned pool task (slower;
attribution only); ``--cprofile-report DIR OUT.txt`` renders them per step.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ''):
    sys.path.insert(0, str(ROOT))

FIXED_DATE = '2026-11-06T00:00:00+00:00'


def _forbid(path):
    path = Path(path).absolute()
    if 'restricted' in path.parts and not path.is_relative_to(Path(os.environ.get('JW_B5_E2E_SCRATCH', '/nonexistent'))):
        raise SystemExit('refusing a restricted/ path outside the synthetic scratch root: ' + str(path))
    if path.is_relative_to('/Users/edr') or path.is_relative_to(ROOT):
        raise SystemExit('scratch/out must be outside the checkout and outside /Users/edr: ' + str(path))


def _environment(workers, sample_ms, scratch):
    os.environ.update(
        GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1', GIT_NO_LAZY_FETCH='1', GIT_ATTR_NOSYSTEM='1',
        GIT_AUTHOR_DATE=FIXED_DATE, GIT_COMMITTER_DATE=FIXED_DATE,
        JW_B5_S10_REAL_PROGRAMS='1', JOULEWISE_B5_ANALYSIS_WORKERS=str(workers),
        JOULEWISE_B5_PHASE_SAMPLE_MS=str(sample_ms), JW_B5_E2E_SCRATCH=str(scratch))
    os.environ.pop('JW_B5_S10_CHAIN_CACHE', None)
    settings = {'core.excludesFile': '/dev/null', 'core.attributesFile': '/dev/null',
                'core.fsmonitor': 'false', 'core.hooksPath': '/dev/null', 'commit.gpgSign': 'false'}
    os.environ['GIT_CONFIG_COUNT'] = str(len(settings))
    for i, (key, value) in enumerate(settings.items()):
        os.environ['GIT_CONFIG_KEY_' + str(i)] = key
        os.environ['GIT_CONFIG_VALUE_' + str(i)] = value


class _FixedTemporaryDirectory:
    """TemporaryDirectory at a fixed path (harness root), recreated empty."""

    def __init__(self, path):
        self.name = str(path)
        shutil.rmtree(self.name, ignore_errors=True)
        os.makedirs(self.name)

    def cleanup(self):
        shutil.rmtree(self.name, ignore_errors=True)

    def __enter__(self):
        return self.name

    def __exit__(self, *exc):
        self.cleanup()


def _fixed_tempfile(scratch):
    """A tempfile stand-in for the two synthetic test-harness modules only."""
    shim = types.ModuleType('tempfile_fixed')
    shim.__dict__.update({k: getattr(tempfile, k) for k in dir(tempfile) if not k.startswith('__')})

    def mkdtemp(suffix=None, prefix=None, dir=None):
        if prefix == 's10-chain-':
            path = scratch / 'chain'
            shutil.rmtree(path, ignore_errors=True)
            path.mkdir(parents=True)
            return str(path)
        return tempfile.mkdtemp(suffix, prefix, dir)

    def TemporaryDirectory(suffix=None, prefix=None, dir=None, **kwargs):
        if prefix == 's10-joined-':
            return _FixedTemporaryDirectory(scratch / 'joined')
        return tempfile.TemporaryDirectory(suffix, prefix, dir, **kwargs)

    shim.mkdtemp, shim.TemporaryDirectory = mkdtemp, TemporaryDirectory
    return shim


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def manifest(root):
    rows = {}
    for path in sorted(Path(root).rglob('*')):
        if path.is_symlink():
            rows[str(path.relative_to(root))] = 'symlink:' + os.readlink(path)
        elif path.is_file():
            rows[str(path.relative_to(root))] = _sha256(path)
    return rows


def code_digest():
    """sha256 over the working-tree bytes of the analysis code (detects the checked-out version)."""
    digest = hashlib.sha256()
    for top in ('joulewise', 'scripts', 'configs', 'tools'):
        for path in sorted((ROOT / top).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.name != 'b5_e2e_synthetic.py':
                digest.update(str(path.relative_to(ROOT)).encode() + b'\0' + path.read_bytes() + b'\0')
    return digest.hexdigest()


def _git(*args):
    try:
        return subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True).stdout.strip()
    except OSError:
        return None


def step_table(phases_path):
    steps = {}
    for line in phases_path.read_text().splitlines():
        row = json.loads(line)
        if row.get('event') == 'step_end':
            steps[row['step']] = dict(wall_s=row['wall_ms'] / 1000, driver_cpu_s=row['cpu_ms'] / 1000,
                                      serial_s=row['serial_ms'] / 1000)
    return steps


def report_profiles(directory, out, top=40):
    """Per step and process group (driver / pool workers): top functions by self and cumulative time."""
    import io
    import pstats
    groups = {}
    for path in sorted(Path(directory).glob('*.prof')):
        group, _pid, step = path.stem.split('-', 2)
        groups.setdefault((step.removeprefix('step'), group), []).append(str(path))
    order = {s: i for i, s in enumerate(('0', '1', '2', '3', '3b', '4', '5', '8', '6', '9', '9b', '10', '11'))}
    with open(out, 'w') as handle:
        for (step, group), files in sorted(groups.items(), key=lambda kv: (order.get(kv[0][0], 99), kv[0][1])):
            stats = pstats.Stats(files[0])
            for extra in files[1:]:
                stats.add(extra)
            for key in ('tottime', 'cumulative'):
                buffer = io.StringIO()
                stats.stream = buffer
                stats.sort_stats(key).print_stats(top)
                handle.write(f'\n===== step {step} {group} ({len(files)} processes) by {key} =====\n')
                handle.write(buffer.getvalue())


def main(argv=None):
    if argv is None and sys.argv[1:2] == ['--pack-checkpoint']:
        pack_checkpoint(Path(sys.argv[2]), Path(sys.argv[3]))
        return 0
    if argv is None and sys.argv[1:2] == ['--cprofile-report']:
        report_profiles(Path(sys.argv[2]), Path(sys.argv[3]))
        return 0
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--scratch', type=Path, required=True,
                        help='fixed synthetic root (same path for runs that are compared)')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, required=True)
    parser.add_argument('--label', default='run')
    parser.add_argument('--sample-ms', type=int, default=200)
    parser.add_argument('--keep-custody', action='store_true')
    parser.add_argument('--cprofile-steps', metavar='STEPS',
                        help='with --cprofile: profile only these comma-separated steps (others run unprofiled)')
    parser.add_argument('--sample-stacks', metavar='STEPS',
                        help='comma-separated step ids: sample the driver main thread\'s Python stack every '
                             '20 ms during those steps and write OUT/stacks-step<ID>.json (low overhead)')
    parser.add_argument('--checkpoint-at', metavar='STEP',
                        help='at the start of STEP (after every earlier step committed), save the run state and '
                             'restricted custody to --checkpoint-dir, then stop the run (synthetic refusal)')
    parser.add_argument('--checkpoint-dir', type=Path)
    parser.add_argument('--resume', type=Path, metavar='DIR',
                        help='a checkpoint directory (state.pkl + restricted.tar) or a directory of *.b64 parts '
                             'from --pack-checkpoint: restore it as step 0 and run the remaining steps')
    parser.add_argument('--resume-drop-leaves', default='',
                        help='comma-separated VDL leaf ids whose checkpoint entries are not restored '
                             '(an r2 resume drops L4_calibration_bracket, which r2 never stores)')
    parser.add_argument('--stop-after', help='synthetic partial run: every later step refuses with '
                        "'synthetic_stop_after' (so the record still closes); for time-boxed hosts")
    parser.add_argument('--interrupt-after-step', metavar='STEP',
                        help='production resume (lane b5-robust): kill the run (KeyboardInterrupt) right after '
                             "STEP's checkpoint, then continue it with dry_run.run(..., resume=True)")
    parser.add_argument('--interrupt-in-step', metavar='STEP',
                        help='production resume: kill the run after the first serial runner invocation of STEP '
                             'returns (its partial outputs stay on disk), then continue it with resume=True')
    parser.add_argument('--vdl-mode', default='on',
                        help="JOULEWISE_B5_VDL for the run: 'on' (default; serves verified hits as a real blind "
                             "run's BLIND_ON does, so timings are comparable), 'off', or 'shadow:<permille>' "
                             "(the synthetic default, recomputes sampled hits: stricter, slower)")
    parser.add_argument('--cprofile', type=Path,
                        help='write per-step cProfile stats of the driver and of every pool task to DIR '
                             '(slows the run; use for attribution, not for timing)')
    args = parser.parse_args(argv)
    scratch, out = args.scratch.absolute(), args.out.absolute()
    for path in (scratch, out, Path(os.environ.get('TMPDIR', tempfile.gettempdir()))):
        _forbid(path)
    if out.exists() and any(out.iterdir()):
        parser.error('--out must be empty')
    out.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(scratch, ignore_errors=True)
    scratch.mkdir(parents=True)
    _environment(args.workers, args.sample_ms, scratch)
    os.environ['JOULEWISE_B5_VDL'] = args.vdl_mode
    if args.cprofile is not None:
        _forbid(args.cprofile.absolute())
        args.cprofile.mkdir(parents=True, exist_ok=True)
        os.environ[PROFILE_ENV] = str(args.cprofile.absolute())
        if args.cprofile_steps:
            os.environ[PROFILE_STEPS_ENV] = args.cprofile_steps
        _profile_driver_steps(args.cprofile.absolute())

    from tests.b5_analysis import fixtures_s10, joined_s10
    shim = _fixed_tempfile(scratch)
    fixtures_s10.tempfile = shim
    joined_s10.tempfile = shim
    from joulewise.b5_analysis import dry_run as d
    if args.stop_after is not None:
        ids = [step for step, _ in d.STEPS]
        if args.stop_after not in ids:
            parser.error('--stop-after must be a registered step id')
        cut = ids.index(args.stop_after)

        def stopped(s, r):
            raise d.AnalysisRefusal('synthetic_stop_after')
        d.STEPS = tuple(item if i <= cut else (item[0], stopped) for i, item in enumerate(d.STEPS))
    if args.checkpoint_at is not None:
        if args.checkpoint_dir is None:
            parser.error('--checkpoint-at needs --checkpoint-dir')
        _forbid(args.checkpoint_dir.absolute())
        _install_checkpoint(d, args.checkpoint_at, args.checkpoint_dir.absolute())
    if args.resume is not None:
        _install_resume(d, args.resume.absolute(), {x for x in args.resume_drop_leaves.split(',') if x})

    if args.sample_stacks:
        _sample_driver_stacks(out, set(args.sample_stacks.split(',')))

    started = time.monotonic()
    print('restoring committed synthetic S10 windows', flush=True)
    fixture = fixtures_s10.chain_fixture()
    harness = joined_s10.JoinedHarness(fixture.index)
    restore_s = time.monotonic() - started
    os.environ['JW_B5_E2E_REPO'], os.environ['JW_B5_E2E_HEAD'] = str(harness.repo), harness.head
    custody = scratch / 'custody'
    print('running joined driver: workers', args.workers, 'custody', custody, flush=True)
    if args.interrupt_after_step or args.interrupt_in_step:
        interrupted = _production_interrupt(d, args.interrupt_after_step, args.interrupt_in_step)
        try:
            harness.execute(args.label, custody=custody)
        except KeyboardInterrupt:
            print('interrupted; resuming', flush=True)
        else:
            raise SystemExit('the run finished before the requested interrupt')
        finally:
            interrupted()
        import functools
        run, d.run = d.run, functools.partial(d.run, resume=True)
        try:
            result = harness.execute(args.label, custody=custody)
        finally:
            d.run = run
    else:
        result = harness.execute(args.label, custody=custody)
    run_dir = custody / 'dry-run'
    phases = run_dir / 'restricted/logs/runtime-phases.jsonl'
    summary = dict(
        synthetic_only=True, label=args.label, workers=args.workers, sample_ms=args.sample_ms,
        vdl_mode=args.vdl_mode,
        exit_code=result.code, wall_s=result.wall_s, restore_s=restore_s,
        machine=dict(cpu_count=os.cpu_count(), platform=platform.platform(), python=sys.version),
        git_head=_git('rev-parse', 'HEAD'), git_status=_git('status', '--porcelain', '--', 'joulewise', 'scripts',
                                                            'configs', 'tools'),
        code_sha256=code_digest(), scratch=str(scratch),
        record_sha256=_sha256(result.path) if result.path.exists() else None,
        statuses=[(r['step'], r['window'], r['status']) for r in (result.record or {}).get('steps', [])],
        steps=step_table(phases) if phases.exists() else None)
    files = manifest(custody)
    summary['manifest_sha256'] = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    summary['manifest'] = files
    (out / 'summary.json').write_text(json.dumps(summary, indent=1, sort_keys=True) + '\n')
    if phases.exists():
        shutil.copyfile(phases, out / 'runtime-phases.jsonl')
        with open(out / 'detail.txt', 'w') as handle:
            subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/b5_phase_report.py'), '--detail', str(phases)],
                           stdout=handle, stderr=subprocess.STDOUT)
    (out / 'stderr.txt').write_text(result.stderr)
    codes = run_dir / 'restricted/decisions/step-codes.jsonl'
    if codes.exists():  # synthetic custody: raw refusal codes per step
        shutil.copyfile(codes, out / 'step-codes.jsonl')
    logs = run_dir / 'restricted/logs'
    if result.code != 0 and logs.is_dir():
        # Synthetic custody only: keep the child logs that carry a traceback or refusal.
        kept = out / 'failure-logs'
        kept.mkdir()
        for path in sorted(logs.iterdir()):
            if path.is_file() and path.stat().st_size < 2_000_000:
                text = path.read_text(errors='replace')
                if 'Traceback' in text or 'refus' in text.lower() or 'error' in text.lower():
                    shutil.copyfile(path, kept / path.name)
    if args.keep_custody:
        shutil.move(str(custody), str(out / 'custody'))
    harness.close()
    print(json.dumps({k: summary[k] for k in ('label', 'exit_code', 'wall_s', 'record_sha256', 'manifest_sha256',
                                              'code_sha256')}), flush=True)
    for step, row in (summary['steps'] or {}).items():
        print(f'step {step:>3}: {row["wall_s"]:9.1f} s', flush=True)
    return 0 if result.code == 0 else 1


def _production_interrupt(d, after_step, in_step):
    """Install one synthetic kill for --interrupt-after-step / --interrupt-in-step; return the uninstaller."""
    from joulewise.b5_analysis import resume
    ids = [step for step, _ in d.STEPS]
    if after_step is not None:
        if after_step not in ids:
            raise SystemExit('--interrupt-after-step must be a registered step id')
        position, write = ids.index(after_step) + 1, resume.Checkpoints.write

        def killing_write(self, s, runner, *, position=None, stopped, ran, _at=position):
            write(self, s, runner, position=position, stopped=stopped, ran=ran)
            if position == _at:
                raise KeyboardInterrupt('synthetic kill after step ' + after_step)
        resume.Checkpoints.write = killing_write
        return lambda: setattr(resume.Checkpoints, 'write', write)
    if in_step not in ids:
        raise SystemExit('--interrupt-in-step must be a registered step id')
    run = d.StepRunner.run

    def killing_run(self, main, argv, *, step, window=None, stdout_path=None):
        result = run(self, main, argv, step=step, window=window, stdout_path=stdout_path)
        if step == in_step:
            raise KeyboardInterrupt('synthetic kill inside step ' + in_step)
        return result
    killing_run.__wrapped__ = run
    d.StepRunner.run = killing_run
    return lambda: setattr(d.StepRunner, 'run', run)


# ------------------------------------------------------------ checkpoint / resume
# A one-hour host cannot run the whole synthetic chain. The state at the start of
# a step (every earlier step committed) is saved by one run and restored as
# "step 0" of another at the SAME fixed locators, so the remaining steps, the
# final record and every custody byte are those of an uninterrupted run (the
# member pools start cold; that changes timing only).

_LIVE_LOGS = ('logs/runtime-phases.jsonl', 'logs/runtime-vdl-counters.json')


def _transport_dumps(value):
    """pack_parallel's private transport, self-contained so an r2 checkout can use it."""
    import io
    import pickle
    from types import MappingProxyType
    from joulewise.b5_analysis.windows import _SELECTION_TOKEN

    buffer = io.BytesIO()

    class TransportPickler(pickle.Pickler):
        def persistent_id(self, item):
            return 'selected-window' if item is _SELECTION_TOKEN else None

    pickler = TransportPickler(buffer, protocol=pickle.HIGHEST_PROTOCOL)
    pickler.dispatch_table = {MappingProxyType: lambda value: (_mapping_proxy, (dict(value),))}
    pickler.dump(value)
    return buffer.getvalue()


def _mapping_proxy(value):
    from types import MappingProxyType
    return MappingProxyType(value)


def _transport_loads(payload):
    import io
    import pickle
    from joulewise.b5_analysis.archive import ArchiveHandle
    from joulewise.b5_analysis.windows import _SELECTION_TOKEN

    class TransportUnpickler(pickle.Unpickler):
        def persistent_load(self, identity):
            if identity != 'selected-window':
                raise pickle.UnpicklingError('unknown transport identity')
            return _SELECTION_TOKEN

    reader = TransportUnpickler(io.BytesIO(payload))
    value = reader.load()
    for item in reader.memo.copy().values():
        if isinstance(item, ArchiveHandle) and '_rebuilt_roster_bindings' in item.__dict__:
            item._rebuilt_roster_bindings = {id(roster): roster for roster in item._rebuilt_roster_bindings.values()}
    return value


def _ensure_sources_replay_class():
    """An r2 checkout builds the identical replay as a closure; give it the picklable class."""
    from dataclasses import dataclass
    from joulewise.b5_analysis import context

    if hasattr(context, '_SourcesReplay'):
        return

    @dataclass(frozen=True)
    class _SourcesReplay:
        archive: object
        roster: object

        def __call__(self, candidate, runs_root):
            from joulewise.b5_analysis.sources_replay import replay_claim_sources
            return replay_claim_sources(candidate, runs_root, archive=self.archive, roster=self.roster).problem

    _SourcesReplay.__module__ = context.__name__
    _SourcesReplay.__qualname__ = '_SourcesReplay'
    context._SourcesReplay = _SourcesReplay


def _install_checkpoint(d, step, directory):
    import copy as _copy
    import tarfile
    from joulewise import analysis_run_cache as arc

    def checkpoint(s, r):
        caches = arc.current()
        saved = _copy.copy(s)
        saved._runner = saved.vdl_store = saved.deadline = saved.physics_store = None
        payload = dict(state=saved, physics=dict(s.physics_store or {}),
                       entries=None if s.vdl_store is None else s.vdl_store.export_entries(),
                       memos={k: dict(v) for k, v in (caches.memos or {}).items()},
                       counter=r._counter, last_exception_class=r.last_exception_class, step=step)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'state.pkl').write_bytes(_transport_dumps(payload))
        with tarfile.open(directory / 'restricted.tar', 'w') as tar:
            for path in sorted(s.restricted.rglob('*')):
                relative = path.relative_to(s.restricted).as_posix()
                if path.is_file() and relative not in _LIVE_LOGS and not relative.startswith('logs/runtime-stack-'):
                    tar.add(path, arcname=relative, recursive=False)
        print('checkpoint written before step', step, flush=True)
        raise d.AnalysisRefusal('synthetic_stop_after')

    d.STEPS = tuple((sid, checkpoint) if sid == step else (sid, fn) for sid, fn in d.STEPS)


def pack_checkpoint(directory, out, part_chars=3_000_000):
    """Compress a checkpoint into base64 text parts small enough for a text diff."""
    import base64
    import io
    import tarfile
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w:xz', preset=9) as tar:
        for name in ('state.pkl', 'restricted.tar'):
            tar.add(directory / name, arcname=name)
    text = base64.encodebytes(buffer.getvalue()).decode()
    out.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(buffer.getvalue()).hexdigest()
    parts = [text[i:i + part_chars] for i in range(0, len(text), part_chars)]
    for index, part in enumerate(parts):
        (out / f'ckpt.part{index:03d}.b64').write_text(part)
    (out / 'ckpt.sha256').write_text(digest + '\n')
    print(json.dumps(dict(parts=len(parts), compressed_bytes=len(buffer.getvalue()), sha256=digest)))


def _unpack_checkpoint(source):
    import base64
    import io
    import tarfile
    import tempfile as _tempfile
    if (source / 'state.pkl').exists():
        return source
    raw = base64.decodebytes(''.join(p.read_text() for p in sorted(source.glob('ckpt.part*.b64'))).encode())
    expected = (source / 'ckpt.sha256').read_text().strip()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise SystemExit('checkpoint parts do not match ckpt.sha256')
    target = Path(_tempfile.mkdtemp(prefix='b5-e2e-ckpt-'))
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:xz') as tar:
        tar.extractall(target, filter='data')
    return target


def _install_resume(d, source, drop_leaves):
    import tarfile
    from joulewise import analysis_run_cache as arc

    source = _unpack_checkpoint(source)
    _ensure_sources_replay_class()
    payload = _transport_loads((source / 'state.pkl').read_bytes())
    saved = payload['state']
    done = {record.step for record in saved.step_records}
    live = {'_runner', 'vdl_store', 'deadline', 'physics_store', 'workers', 'ignored_backup', 'restricted',
            'step_records'}

    def restore(s, r):
        with tarfile.open(source / 'restricted.tar') as tar:
            tar.extractall(s.restricted, filter='data')
        for name, value in vars(saved).items():
            if name not in live:
                setattr(s, name, value)
        s.physics_store.update(payload['physics'])
        caches = arc.current()
        if s.vdl_store is not None and payload['entries'] is not None:
            entries = dict(payload['entries'])
            entries['entries'] = {key: entry for key, entry in entries['entries'].items()
                                  if entry.leaf_id not in drop_leaves}
            s.vdl_store.merge_entries(entries)
        for name, table in payload['memos'].items():
            caches.memos.setdefault(name, {}).update(table)
        r._counter = payload['counter']
        r.last_exception_class = payload['last_exception_class']
        print('resumed', len(saved.step_records), 'records; next step', payload['step'], flush=True)
        return list(saved.step_records)

    def skipped(s, r):
        return []

    d.STEPS = tuple((sid, restore) if sid == '0' else (sid, skipped) if sid in done else (sid, fn)
                    for sid, fn in d.STEPS)


def _sample_driver_stacks(out, steps, interval=0.02, depth=40):
    """Driver main-thread stack sampler for the named steps (attribution of driver-serial time)."""
    import collections
    import threading
    from joulewise.b5_analysis import phase_timing

    main = threading.main_thread().ident
    begin, end = phase_timing.step_begin, phase_timing.step_end
    state = {}

    def key(code):
        return f'{os.path.basename(code.co_filename)}:{code.co_firstlineno}:{code.co_qualname}'

    def sampler(step, stop):
        self_counts, inclusive, edges, stacks = (collections.Counter() for _ in range(4))
        samples = 0
        while not stop.wait(interval):
            frame = sys._current_frames().get(main)
            chain = []
            while frame is not None and len(chain) < depth:
                chain.append(key(frame.f_code))
                frame = frame.f_back
            if not chain:
                continue
            samples += 1
            self_counts[chain[0]] += 1
            for name in set(chain):
                inclusive[name] += 1
            for callee, caller in zip(chain, chain[1:]):
                edges[caller + ' -> ' + callee] += 1
            stacks[' <- '.join(chain[:8])] += 1
        document = dict(step=step, interval_s=interval, samples=samples,
                        self=self_counts.most_common(80), inclusive=inclusive.most_common(150),
                        edges=edges.most_common(250), stacks=stacks.most_common(60))
        (out / f'stacks-step{step}.json').write_text(json.dumps(document, indent=1) + '\n')

    def step_begin(step):
        begin(step)
        if step in steps:
            stop = threading.Event()
            thread = threading.Thread(target=sampler, args=(step, stop), daemon=True, name='e2e-stack-sampler')
            thread.start()
            state[step] = (stop, thread)

    def step_end(step):
        if step in state:
            stop, thread = state.pop(step)
            stop.set()
            thread.join()
        end(step)

    phase_timing.step_begin, phase_timing.step_end = step_begin, step_end


PROFILE_ENV = 'JW_B5_E2E_CPROFILE'
PROFILE_STEPS_ENV = 'JW_B5_E2E_CPROFILE_STEPS'


def _profiled_step(step):
    wanted = os.environ.get(PROFILE_STEPS_ENV)
    return not wanted or step in wanted.split(',')
_PROFILES = {}
_ACTIVE = []


def _current_step(directory):
    try:
        return (Path(directory) / 'current-step').read_text().strip() or 'none'
    except OSError:
        return 'none'


def _dump_profiles(directory, prefix):
    for step, profile in _PROFILES.items():
        try:
            profile.dump_stats(str(Path(directory) / f'{prefix}-{os.getpid()}-step{step}.prof'))
        except Exception:  # noqa: BLE001 - attribution only
            pass


def _profile_driver_steps(directory):
    """Parent: one profile per registered step, switched by the driver's own step hooks."""
    import atexit
    import cProfile
    from joulewise.b5_analysis import phase_timing

    begin, end = phase_timing.step_begin, phase_timing.step_end

    def step_begin(step):
        tmp = directory / 'current-step.tmp'
        tmp.write_text(step)
        os.replace(tmp, directory / 'current-step')
        begin(step)
        if not _profiled_step(step):
            return
        profile = _PROFILES.setdefault(step, cProfile.Profile())
        try:
            profile.enable()
            _ACTIVE.append(profile)
        except ValueError:
            pass

    def step_end(step):
        while _ACTIVE:
            _ACTIVE.pop().disable()
        end(step)
        (directory / 'current-step').write_text('none')

    phase_timing.step_begin, phase_timing.step_end = step_begin, step_end
    atexit.register(_dump_profiles, directory, 'driver')


def _profiled_task(original, directory):
    """Worker: profile each pool task under the step the driver is in."""
    import cProfile
    import functools

    @functools.wraps(original)
    def run(*args, **kwargs):
        step = _current_step(directory)
        if _ACTIVE or not _profiled_step(step):
            return original(*args, **kwargs)
        profile = _PROFILES.setdefault(step, cProfile.Profile())
        try:
            profile.enable()
        except ValueError:
            return original(*args, **kwargs)
        _ACTIVE.append(profile)
        try:
            return original(*args, **kwargs)
        finally:
            _ACTIVE.pop()
            profile.disable()
    return run


def _seamed_pack_worker(original):
    """Spawned pack workers see the same synthetic Git observations as the parent."""
    import functools

    @functools.wraps(original)
    def run(task):
        from tests.b5_analysis.joined_s10 import JoinedHarness
        harness = object.__new__(JoinedHarness)
        harness.repo, harness.head = Path(os.environ['JW_B5_E2E_REPO']), os.environ['JW_B5_E2E_HEAD']
        with harness.git_seams():
            return original(task)
    return run


def _install_worker_hooks():
    import importlib
    try:
        from joulewise.b5_analysis import pack_parallel as pp
    except ImportError:  # r2 has no pack scheduling
        pp = None
    if pp is not None:
        pp.run_pack = _seamed_pack_worker(pp.run_pack)
    directory = os.environ.get(PROFILE_ENV)
    if not directory:
        return
    import atexit
    for module, name in (('joulewise.analysis_member_pool', 'run_member'),
                         ('joulewise.b5_analysis.parallel', 'run_child'),
                         ('joulewise.b5_analysis.pack_parallel', 'run_pack'),
                         ('joulewise.whole_window', '_strict_validation_worker')):
        try:
            owner = importlib.import_module(module)
        except ImportError:
            continue
        if hasattr(owner, name):
            setattr(owner, name, _profiled_task(getattr(owner, name), directory))
    atexit.register(_dump_profiles, directory, 'worker')


if __name__ == '__main__':
    sys.exit(main())
elif __name__ == '__mp_main__' and os.environ.get('JW_B5_E2E_REPO'):
    _install_worker_hooks()
