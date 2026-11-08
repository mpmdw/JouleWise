#!/usr/bin/env python3
"""ALIGN v4 pre-arm PREQUAL extension (W1 and the next measurement); see docs/align/v4/W1-SMOKE-opus.md.

Runs on the Air (never the measurement Mac) before any MBP launch. One command,
a PASS/FAIL table, exit 0 only when every check passes (PENDING allowed only
for checks that gate a later measurement than --next).

  python3.13 -B scripts/align_v4_w1_prequal.py --output DIR --next w1

Exit codes: 0 pass, 1 fail, 3 incomplete (--only), 2 usage.
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

from joulewise.align import w1_prequal as wp  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', type=Path, help='new report directory (prequal-w1.json, prequal-w1.md)')
    parser.add_argument('--next', dest='next_window', choices=wp.NEXT, default='w1',
                        help='the next measurement to be armed')
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--commit', help='candidate commit (default: repo HEAD)')
    parser.add_argument('--python-bin', default=sys.executable)
    parser.add_argument('--only', help='comma-separated subset (report is then INCOMPLETE at best)')
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--waive', action='append', default=[], metavar='CHECK=RULING',
                        help='record a lead waiver for one FAILing check (ruling reference required)')
    parser.add_argument('--work', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--probe', choices=sorted(wp.CHECKS), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.probe:
        os.environ.setdefault('JOULEWISE_HOST_STATE_DIR', str(Path(args.work) / 'host-state'))
        ctx = wp.Context(args.repo, args.work, args.next_window, args.commit, args.python_bin)
        ctx.work.mkdir(parents=True, exist_ok=True)
        print(json.dumps(wp.probe(args.probe, ctx), sort_keys=True, default=str), flush=True)
        return 0
    if args.output is None:
        parser.error('--output is required')
    if args.output.exists():
        parser.error('--output must be a new directory')
    only = set(args.only.split(',')) if args.only else None
    if only and not only <= set(wp.CHECKS):
        parser.error(f'unknown checks: {sorted(only - set(wp.CHECKS))}')
    waivers = {}
    for item in args.waive:
        name, _, ruling = item.partition('=')
        if name not in wp.CHECKS or not ruling.strip():
            parser.error(f'--waive needs CHECK=RULING with a known check: {item!r}')
        waivers[name] = ruling.strip()
    work = args.work or args.output.with_name(args.output.name + '.work')
    work.mkdir(parents=True, exist_ok=True)
    ctx = wp.Context(args.repo, work, args.next_window, args.commit, args.python_bin)
    report = wp.run_all(ctx, only=only, jobs=args.jobs, waivers=waivers, script=Path(__file__).resolve())
    args.output.mkdir(parents=True)
    (args.output / 'prequal-w1.json').write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + '\n')
    text = wp.table(report)
    (args.output / 'prequal-w1.md').write_text(text)
    print(text)
    return wp.EXIT[report['status']]


if __name__ == '__main__':
    raise SystemExit(main())
