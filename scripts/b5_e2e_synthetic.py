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
the custody tree to OUT/custody for the comparator.
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--scratch', type=Path, required=True,
                        help='fixed synthetic root (same path for runs that are compared)')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, required=True)
    parser.add_argument('--label', default='run')
    parser.add_argument('--sample-ms', type=int, default=200)
    parser.add_argument('--keep-custody', action='store_true')
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

    from tests.b5_analysis import fixtures_s10, joined_s10
    shim = _fixed_tempfile(scratch)
    fixtures_s10.tempfile = shim
    joined_s10.tempfile = shim
    from joulewise.b5_analysis import dry_run as d

    started = time.monotonic()
    print('restoring committed synthetic S10 windows', flush=True)
    fixture = fixtures_s10.chain_fixture()
    harness = joined_s10.JoinedHarness(fixture.index)
    restore_s = time.monotonic() - started
    os.environ['JW_B5_E2E_REPO'], os.environ['JW_B5_E2E_HEAD'] = str(harness.repo), harness.head
    custody = scratch / 'custody'
    print('running joined driver: workers', args.workers, 'custody', custody, flush=True)
    result = harness.execute(args.label, custody=custody)
    run_dir = custody / 'dry-run'
    phases = run_dir / 'restricted/logs/runtime-phases.jsonl'
    summary = dict(
        synthetic_only=True, label=args.label, workers=args.workers, sample_ms=args.sample_ms,
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
    if args.keep_custody:
        shutil.move(str(custody), str(out / 'custody'))
    harness.close()
    print(json.dumps({k: summary[k] for k in ('label', 'exit_code', 'wall_s', 'record_sha256', 'manifest_sha256',
                                              'code_sha256')}), flush=True)
    for step, row in (summary['steps'] or {}).items():
        print(f'step {step:>3}: {row["wall_s"]:9.1f} s', flush=True)
    return 0 if result.code == 0 else 1


def _seamed_pack_worker(original):
    """Spawned pack workers see the same synthetic Git observations as the parent."""
    def run(task):
        from tests.b5_analysis.joined_s10 import JoinedHarness
        harness = object.__new__(JoinedHarness)
        harness.repo, harness.head = Path(os.environ['JW_B5_E2E_REPO']), os.environ['JW_B5_E2E_HEAD']
        with harness.git_seams():
            return original(task)
    return run


if __name__ == '__main__':
    sys.exit(main())
elif __name__ == '__mp_main__' and os.environ.get('JW_B5_E2E_REPO'):
    try:
        from joulewise.b5_analysis import pack_parallel as _pp
    except ImportError:  # r2 has no pack scheduling
        _pp = None
    if _pp is not None:
        _pp.run_pack = _seamed_pack_worker(_pp.run_pack)
