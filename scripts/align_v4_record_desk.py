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
    from joulewise.align.apple.desk_record import describe, finalize, replay, gate_evidence, validate_gate
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=ROOT)
    parser.add_argument('--commit', help='full SHA pinning the descriptor')
    parser.add_argument('--record', help='repository-relative descriptor path at that commit')
    parser.add_argument('--describe', type=Path, metavar='LAYOUT.json',
                        help='write a descriptor; layout names relative roots and the MBP finalize manifest')
    parser.add_argument('--finalize', type=Path, metavar='LAYOUT.json',
                        help='on the MBP, seal a complete successful harvest export before transfer')
    parser.add_argument('--gate-evidence', type=Path, help='write structured triage evidence after a passing replay')
    parser.add_argument('--inputs', type=Path, required=True, help='local exported evidence tree')
    parser.add_argument('--output', type=Path, required=True,
                        help='new report directory, or descriptor JSON with --describe; outside the input tree')
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--profile', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.describe is not None or args.finalize is not None:
            if (args.describe is not None and args.finalize is not None) or args.commit or args.record or args.profile or args.gate_evidence:
                parser.error('--describe/--finalize cannot be combined with each other or replay options')
            if args.output.resolve().is_relative_to(args.inputs.resolve()):
                raise ValueError('descriptor output must be outside the immutable record')
            layout = json.loads((args.describe or args.finalize).read_bytes())
            value = (finalize(args.inputs, layout) if args.finalize else
                     describe(args.inputs, layout, repository=args.repository))
            with args.output.open('x') as handle:
                handle.write(json.dumps(value, indent=2, sort_keys=True)+'\n')
            return 0
        if not args.commit or not args.record:
            parser.error('replay requires --commit and --record')
        if args.gate_evidence:
            if args.gate_evidence.resolve().is_relative_to(args.inputs.resolve()):
                raise ValueError('gate evidence must be outside the immutable record')
            if args.gate_evidence.exists() or not args.gate_evidence.parent.is_dir():
                raise ValueError('gate evidence requires a new file in an existing directory')
        status = replay(args.repository, args.commit, args.record, args.inputs, args.output,
                        workers=args.workers, profile=args.profile)
        passed = status['pilot_status'] == 'instrument_ok' and status['harvest_status'] == 'ok'
        if passed and args.gate_evidence:
            evidence = gate_evidence(args.repository, args.commit, args.record, args.output)
            receipt = json.loads((args.output/'REPLAY.json').read_bytes())
            validate_gate(evidence, receipt['session_id'])
            with args.gate_evidence.open('x') as handle:
                handle.write(json.dumps(evidence, indent=2, sort_keys=True)+'\n')
        return 0 if passed else 2
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError, subprocess.SubprocessError) as exc:
        print('align_v4_record_desk: '+str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
