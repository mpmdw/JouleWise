"""Command dispatch; read-only commands need only the standard library."""
from __future__ import annotations

import argparse
import json
import os
import plistlib
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

from .paths import ARCHIVE, atomic, executable, fence, mkdir, read_bytes, read_json
from .schedule import BY_ID, PLANS, TOTAL_SECONDS

MODEL_PYTHON = '/Users/edr/code/JouleWise/.venv/bin/python'
LABEL = 'com.joulewise.quiet-kit'


def complete(root: Path, test_id: str) -> bool:
    doc = read_json(fence(root / test_id / 'result.json'), {})
    return doc.get('complete') is True and fence(root / test_id / 'summary.md').is_file()


def test_status(root: Path, test_id: str) -> str:
    from .paths import children
    if complete(root, test_id):
        return 'complete'
    attempts = [p for p in children(root / test_id / 'attempts') if p.name.isdigit()]
    return f'{len(attempts)} attempts so far' if attempts else 'not started'


def plan_text(root: Path) -> str:
    lines = [f'{i}. {p.test_id}: ' + ('estimate pending' if p.ruling_required else f'{p.estimate_s/60:.2f} min') +
             f'; {test_status(root, p.test_id)}; {p.basis}'
             for i, p in enumerate(PLANS, 1)]
    lines.append(f'Total estimated wall hours: {TOTAL_SECONDS/3600:.3f}' +
                 (' + M10 pending ruling' if any(p.ruling_required for p in PLANS) else ''))
    lines.append('M3 logs alongside all tests; analysis needs at least 3 h. Estimates exclude hazard waits.')
    lines.append('Planned bytes are conservative reservations, not measured storage use.')
    return '\n'.join(lines)


def render_plist(repo: Path, root: Path, model_python: str) -> bytes:
    template = read_bytes(fence(repo / 'configs/launchd/com.joulewise.quiet-kit.plist.template')).decode()
    for key, value in {'REPO': str(fence(repo)), 'ARCHIVE': str(fence(root)),
                       'MODEL_PYTHON': executable(model_python)}.items():
        template = template.replace('{{' + key + '}}', escape(value))
    raw = template.encode()
    plistlib.loads(raw)  # reject malformed substitutions before installation
    return raw


def arm(repo: Path, root: Path, model_python: str, command=subprocess.run, emit=print) -> int:
    path = fence(root / 'launchd' / (LABEL + '.plist'))
    emit(f'mkdir -p {path.parent}')
    mkdir(path.parent)
    # launchd's TMPDIR must exist before launch; no agent name in its path.
    emit('mkdir -p /private/tmp/jw-quiet-kit')
    mkdir('/private/tmp/jw-quiet-kit')
    emit(f'write {path}')
    atomic(path, render_plist(repo, root, model_python))
    for argv in (['/usr/bin/plutil', '-lint', '--', str(path)],
                 ['/bin/launchctl', 'bootout', f'gui/{os.getuid()}/{LABEL}'],
                 ['/bin/launchctl', 'bootstrap', f'gui/{os.getuid()}', str(path)]):
        emit(' '.join(argv))
        result = command(argv, capture_output=True, text=True, timeout=30)
        emit((result.stdout or '') + (result.stderr or ''))
        if result.returncode and argv[1] != 'bootout':
            return result.returncode
        if result.returncode and argv[1] == 'bootout':
            # launchctl commonly returns 3/113 for a missing service.
            if result.returncode not in (3, 113) and not any(
                    s in (result.stderr or '').lower() for s in ('not loaded', 'could not find service', 'no such process')):
                return result.returncode
    return 0


def main(argv=None, *, seams=None, emit=print) -> int:
    parser = argparse.ArgumentParser(description='Unattended non-claim quiet-machine calibration kit')
    modes = parser.add_mutually_exclusive_group(required=True)
    for name in ('plan', 'arm', 'disarm', 'status', 'run', 'plumbing-check'):
        modes.add_argument('--' + name, action='store_true')
    modes.add_argument('--reanalyze', choices=tuple(BY_ID))
    parser.add_argument('--model-python', default=MODEL_PYTHON)
    parser.add_argument('--deadline-hours', type=float, default=2*TOTAL_SECONDS/3600 + 6)
    parser.add_argument('--test', choices=tuple(BY_ID))
    parser.add_argument('--scale', type=float)
    parser.add_argument('--archive', type=Path, default=ARCHIVE,
                        help='output root (default threshold-validation; useful for desk seams)')
    args = parser.parse_args(argv)
    root = fence(args.archive)
    repo = fence(Path(__file__).resolve().parents[2])
    fence(args.model_python)
    if args.scale is not None and args.scale <= 0:
        parser.error('--scale must be positive')
    if args.scale is not None and args.run and seams is None:
        parser.error('--scale is for plumbing checks and desk seams; real measurements use the frozen durations')
    if args.deadline_hours <= 0:
        parser.error('--deadline-hours must be positive')
    if args.plan:
        emit(plan_text(root))
        return 0
    if args.status:
        emit(json.dumps(read_json(root / 'STATUS.json', {'state': 'not started'}), indent=2))
        for p in PLANS:
            emit(f'{p.test_id}: {test_status(root, p.test_id)}')
        return 0
    if args.arm:
        return arm(repo, root, args.model_python, emit=emit)
    if args.disarm:
        command = ['/bin/launchctl', 'bootout', f'gui/{os.getuid()}/{LABEL}']
        emit(' '.join(command))
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        emit((result.stdout or '') + (result.stderr or ''))
        return 0 if result.returncode in (0, 3, 113) else result.returncode
    from .runner import Runner, production_seams
    worker = Runner(repo, root, args.model_python, seams or production_seams(repo, args.model_python),
                    deadline_hours=args.deadline_hours, scale=args.scale or 1., emit=emit)
    if args.reanalyze:
        return worker.reanalyze(args.reanalyze)
    if args.plumbing_check:
        return worker.plumbing(args.test or 'm5-gpu-rail', args.scale)
    return worker.run()
