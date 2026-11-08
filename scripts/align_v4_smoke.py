#!/usr/bin/env python3
"""Record and parse isolated NON-REGISTRABLE MBP smoke attempts (never analyse)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align import w1_smoke as smoke


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    for name in ('init', 'record', 'teardown', 'report'):
        s = sub.add_parser(name)
        s.add_argument('--root', type=Path, required=True)
    sub.choices['init'].add_argument('--candidate', required=True)
    for name in ('record', 'teardown'):
        s = sub.choices[name]
        s.add_argument('--case', required=True, choices=smoke.CASES)
        s.add_argument('--gap-confirmed', action='store_true', required=True,
                       help='operator confirms no measurement window or other collection is active')
        s.add_argument('argv', nargs=argparse.REMAINDER)
    sub.choices['record'].add_argument('--timeout-s', type=int, default=120)
    sub.choices['record'].add_argument('--artifact', action='append', default=[], metavar='NAME=RELATIVE_PATH')
    sub.choices['record'].add_argument('--chain-start', help='relative chain.started path (required for negative arms)')
    args = p.parse_args(argv)
    try:
        if args.command == 'init':
            smoke.init(args.root, args.candidate)
        elif args.command == 'report':
            result = smoke.report(args.root)
            print(smoke.table(result))
            smoke.write_once(args.root / 'smoke-report.json', result)
            return 0 if result['status'] == 'pass' else 1
        else:
            if sys.platform != 'darwin':
                raise ValueError('native recorder is MBP-only; use injected runners for synthetic tests')
            command = args.argv[1:] if args.argv[:1] == ['--'] else args.argv
            if not command:
                raise ValueError('an explicit command argv is required')
            if args.command == 'teardown':
                rows = smoke.teardown(args.root, args.case, [command])
                return 0 if all(r['returncode'] == 0 for r in rows) else 1
            artifacts = [item.split('=', 1) for item in args.artifact]
            if any(len(item) != 2 for item in artifacts):
                raise ValueError('--artifact must be NAME=RELATIVE_PATH')
            result = smoke.capture(args.root, args.case, command, artifacts=artifacts,
                                   chain_start=args.chain_start, timeout_s=args.timeout_s)
            print(json.dumps({'case': args.case, 'returncode': result['returncode'], 'timed_out': result['timed_out']}))
            return 1 if result['timed_out'] else 0  # expected nonzero refusal is parsed by report
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        print('align_v4_smoke: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
