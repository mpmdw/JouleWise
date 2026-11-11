#!/usr/bin/env python3
"""ALIGN v4 native W1 smoke (Opus build); see docs/align/v4/W1-SMOKE.md.

MBP only, by the magistrate, in a gap between windows, never during one.

  run    stage and run the labelled, non-registrable smoke (use --detach, then exit the agent)
  parse  turn a smoke directory into a PASS/FAIL table (exit 0 only on PASS)
  faults list the arm fault catalogue with expected refusals

The kit is CLI-only: ``run`` is the supported entry. ``prepare-child`` is internal (the
runner starts it, bounded by the remaining budget, with the pinned smoke directory's
descriptor); no in-process API is supported.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.align import w1_smoke as smoke  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    run = sub.add_parser('run')
    run.add_argument('--measurement-root', type=Path, required=True)
    run.add_argument('--smoke-dir', type=Path, required=True, help='new directory for this smoke')
    run.add_argument('--prequal-report', type=Path, required=True,
                     help='Air prequal-w1.json (status PASS, next w1, same commit, clean)')
    run.add_argument('--next-arm-triage', type=Path, required=True, help='the packet planned for the W1 arm')
    run.add_argument('--w1-disk-config', type=Path, required=True)
    run.add_argument('--obc-off-attested-by', required=True)
    run.add_argument('--battery-log', type=Path, required=True,
                     help='the live battery log the W1 arm will read (scripts/align_v4_battery_log.py sample)')
    run.add_argument('--python-bin', help='base interpreter for the isolated venv (default: <measurement-root>/.venv/bin/python)')
    run.add_argument('--detach', action='store_true', help='re-run detached in a new session and return')
    parse = sub.add_parser('parse')
    parse.add_argument('smoke_dir', type=Path)
    parse.add_argument('--json', type=Path, help='also write the report here')
    sub.add_parser('faults')
    child = sub.add_parser('prepare-child', help=argparse.SUPPRESS)
    child.add_argument('--measurement-root', type=Path, required=True)
    child.add_argument('--session-root', type=Path, required=True)
    child.add_argument('--smoke-dir', type=Path, required=True)
    child.add_argument('--anchor-fd', type=int, required=True)
    child.add_argument('--result', type=Path, required=True)
    child.add_argument('--keep', required=True)
    args = parser.parse_args(argv)
    if args.command == 'prepare-child':
        return prepare_child(args)
    if args.command == 'faults':
        for fault in smoke.ARM_FAULTS:
            print(f'{fault["id"]}: expect {fault["expect"]} {fault["needle"]!r} - {fault["doc"]}')
        return 0
    if args.command == 'parse':
        report = smoke.parse(args.smoke_dir)
        if args.json:
            args.json.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + '\n')
        print(smoke.render(report))
        return 0 if report['status'] == 'PASS' else 1
    if args.smoke_dir.exists():
        parser.error('--smoke-dir must be a new directory')
    # Validate the destination (and the detached log beside it) BEFORE any write, detached or not.
    config = smoke.load_config(args.measurement_root)
    roots = smoke.production_roots(args.measurement_root, config)
    log_path = args.smoke_dir.with_name(args.smoke_dir.name + '.out')
    violations = smoke.destination_violations(args.smoke_dir, roots) + [
        v for v in smoke.destination_violations(log_path, roots) if 'production' in v['why']]
    if args.detach and os.path.lexists(log_path):
        # D3-1: the detached log is always NEW; an existing (possibly hard-linked or symlinked) file
        # is never appended to.
        violations.append({'path': str(log_path), 'why': 'the detached log already exists'})
    if violations:
        print(json.dumps({'smoke': 'refused', 'reason': 'destination', 'violations': violations}, default=str),
              file=sys.stderr)
        return 2
    if args.detach:
        rest = [a for a in (argv if argv is not None else sys.argv[1:]) if a != '--detach']
        try:
            os.close(smoke._walk_dir(args.smoke_dir.parent, create=True))   # no non-system symlink followed
            pid = smoke.detach([sys.executable, '-B', str(Path(__file__).resolve()), *rest], log_path)
        except (smoke.IsolationAbort, OSError) as exc:
            print(json.dumps({'smoke': 'refused', 'reason': 'detached log', 'error': str(exc)}), file=sys.stderr)
            return 2
        print(json.dumps({'detached_pid': pid, 'smoke_dir': str(args.smoke_dir)}))
        return 0
    runner = smoke.SmokeRunner(
        args.measurement_root, args.smoke_dir, packet=json.loads(args.next_arm_triage.read_bytes()),
        battery_log=args.battery_log,
        obc_off_attested_by=args.obc_off_attested_by, w1_disk_config=args.w1_disk_config,
        prequal_report=args.prequal_report, python=args.python_bin, cli=True)
    return runner.run()


def prepare_child(args):
    """The dedicated prepare process: the production prepare with the smoke's reduced view, its
    state written exclusively beneath the inherited smoke-directory descriptor."""
    import stat
    import traceback
    info = os.fstat(args.anchor_fd)
    if not stat.S_ISDIR(info.st_mode):
        print('prepare-child: --anchor-fd is not a directory descriptor', file=sys.stderr)
        return 2
    anchor = smoke.Anchor(args.smoke_dir, args.anchor_fd)
    try:
        state = smoke.prepare_smoke(args.measurement_root, args.session_root, json.loads(args.keep),
                                    anchor=anchor, child=True)
        smoke.safe_write(anchor, args.result, json.dumps(state, indent=2, sort_keys=True, default=str) + '\n',
                         exclusive=True)
    except Exception:  # noqa: BLE001 - the parent reads rc and stderr
        traceback.print_exc()
        return 1
    return 0


if __name__ == '__main__':
    from joulewise.align.apple import powermode
    powermode.mark_production_entry('align_v4_w1_smoke')
    raise SystemExit(main())
