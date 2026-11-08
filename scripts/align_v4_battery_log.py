#!/usr/bin/env python3
"""Log battery observations and derive top-up evidence (Opus cold MED-3).

  sample  --log LOG [--loop --interval-s N]
                      append one ``battery_float.observe`` record (ioreg AppleSmartBattery);
                      with ``--loop`` keep appending every N seconds until stopped
  derive  --log LOG   print the evidence the arm will derive from LOG at this moment

Procedure (delta2): run ``sample --loop --interval-s 120`` continuously as a cheap logger from
the series' initial charge acquisition through every window and turnaround, so a charge
completed long ago stays provable by continuous float. The arm reads LOG with
``--battery-log``. A sampler pause longer than the 300 s gap rule only costs basis (b) until the
next completed charge. The evidence is computed by ``joulewise.align.apple.v4_topup``; no time is
typed by hand.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main(argv=None, *, runner=None, now=None, sleep=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('sample', 'derive'):
        p = sub.add_parser(name)
        p.add_argument('--log', type=Path, required=True)
        if name == 'sample':
            p.add_argument('--loop', action='store_true', help='keep sampling until interrupted')
            p.add_argument('--interval-s', type=float, default=120.0)
            p.add_argument('--max-samples', type=int, default=None, help='stop after N samples (tests)')
    args = parser.parse_args(argv)
    from joulewise import battery_float
    from joulewise.align.apple import v4_topup
    if args.command == 'sample':
        taken = 0
        while True:
            record, _raw = battery_float.observe(phase='topup_log', runner=runner)
            with args.log.open('a') as handle:
                handle.write(json.dumps(record, sort_keys=True, allow_nan=False) + '\n')
            print(json.dumps({k: record[k] for k in ('wall_time_s', 'is_charging', 'current_capacity_pct',
                                                     'external_connected', 'probe_error')}, sort_keys=True))
            taken += 1
            if not args.loop or (args.max_samples is not None and taken >= args.max_samples):
                return 0
            try:
                (sleep or time.sleep)(args.interval_s)
            except KeyboardInterrupt:
                return 0
    evidence = v4_topup.derive_from_file(args.log, (now or time.time)())
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence['admissible'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
