#!/usr/bin/env python3
"""Log battery observations and derive top-up evidence (Opus cold MED-3).

  sample  --log LOG   append one ``battery_float.observe`` record (ioreg AppleSmartBattery)
  derive  --log LOG   print the evidence the arm will derive from LOG at this moment

Run ``sample`` on a cadence (for example every 60-120 s) between windows; the arm reads
LOG with ``--battery-log``. The evidence is computed by
``joulewise.align.apple.v4_topup``; no time is typed by hand.
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


def main(argv=None, *, runner=None, now=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('sample', 'derive'):
        p = sub.add_parser(name)
        p.add_argument('--log', type=Path, required=True)
    args = parser.parse_args(argv)
    from joulewise import battery_float
    from joulewise.align.apple import v4_topup
    if args.command == 'sample':
        record, _raw = battery_float.observe(phase='topup_log', runner=runner)
        with args.log.open('a') as handle:
            handle.write(json.dumps(record, sort_keys=True, allow_nan=False) + '\n')
        print(json.dumps({k: record[k] for k in ('wall_time_s', 'is_charging', 'current_capacity_pct',
                                                 'external_connected', 'probe_error')}, sort_keys=True))
        return 0
    evidence = v4_topup.derive_from_file(args.log, (now or time.time)())
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence['admissible'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
