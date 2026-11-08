#!/usr/bin/env python3
"""Read a committed terminal-record descriptor and run the v4 desk on a laptop.

See docs/perf/2026-11-08-eng-desk.md for the explicit export layout. This
entry point has no prepare/install/harvest or measurement-host command path.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main(argv=None):
    from joulewise.align.apple.desk_record import describe, replay
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=ROOT)
    parser.add_argument('--commit', help='full SHA pinning the descriptor')
    parser.add_argument('--record', help='repository-relative descriptor path at that commit')
    parser.add_argument('--describe', type=Path, metavar='LAYOUT.json',
                        help='write a descriptor instead of replaying; layout has explicit relative roots and targets')
    parser.add_argument('--inputs', type=Path, required=True, help='local exported evidence tree')
    parser.add_argument('--output', type=Path, required=True,
                        help='new report directory, or descriptor JSON with --describe; outside the input tree')
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--profile', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.describe is not None:
            if args.commit or args.record or args.profile:
                parser.error('--describe cannot be combined with --commit, --record or --profile')
            if args.output.resolve().is_relative_to(args.inputs.resolve()):
                raise ValueError('descriptor output must be outside the immutable record')
            value = describe(args.inputs, json.loads(args.describe.read_bytes()))
            with args.output.open('x') as handle:
                handle.write(json.dumps(value, indent=2, sort_keys=True)+'\n')
            return 0
        if not args.commit or not args.record:
            parser.error('replay requires --commit and --record')
        status = replay(args.repository, args.commit, args.record, args.inputs, args.output,
                        workers=args.workers, profile=args.profile)
        return 0 if status['pilot_status'] == 'instrument_ok' else 2
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.CalledProcessError) as exc:
        print('align_v4_record_desk: '+str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
