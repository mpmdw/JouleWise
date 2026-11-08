#!/usr/bin/env python3
"""Log battery observations and derive top-up evidence (Opus cold MED-3, delta2).

  sample  --log LOG [--loop --interval-s N --pidfile P]
                      append one ``battery_float.observe`` record (ioreg AppleSmartBattery);
                      with ``--loop`` keep appending every N seconds until stopped
  stop    --pidfile P stop a running ``sample --loop`` (SIGTERM; it exits cleanly)
  derive  --log LOG [--log LOG2 ...] [--window-journal J ...]
                      print the evidence the arm will derive at this moment

Procedure (lead ruling: NO sampler during a window; an ioreg spawn on the measuring Mac is
activity the quiet guard exists to catch). The magistrate sequence is:

  1. terminal completion of the window  ->  ``sample --loop --interval-s 120 --pidfile P``
  2. finalize/hash/push the record, cool-down, triage (the sampler runs throughout)
  3. before the quiet/arm dwell           ->  ``stop --pidfile P``
  4. arm with ``--battery-log LOG`` (all between-window logs) and
     ``--window-battery-journal J`` (each window's hazard battery journal)

Across a window the evidence is that window's own 1 Hz SMC battery capture
(``joulewise.align.apple.v4_topup.window_records``), merged in time order with the logs. A gap
at a boundary above 300 s, or a missing window journal, breaks continuity (basis (b) only).
No time is typed by hand.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main(argv=None, *, runner=None, now=None, sleep=None, kill=os.kill):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('sample')
    p.add_argument('--log', type=Path, required=True)
    p.add_argument('--loop', action='store_true', help='keep sampling until stopped (between windows only)')
    p.add_argument('--interval-s', type=float, default=120.0)
    p.add_argument('--max-samples', type=int, default=None, help='stop after N samples (tests)')
    p.add_argument('--pidfile', type=Path, default=None, help='written while looping; used by ``stop``')
    p = sub.add_parser('stop')
    p.add_argument('--pidfile', type=Path, required=True)
    p = sub.add_parser('derive')
    p.add_argument('--log', type=Path, action='append', default=[])
    p.add_argument('--window-journal', type=Path, action='append', default=[])
    args = parser.parse_args(argv)
    from joulewise import battery_float
    from joulewise.align.apple import v4_topup
    if args.command == 'stop':
        try:
            pid = int(args.pidfile.read_text().strip())
            kill(pid, signal.SIGTERM)
        except (OSError, ValueError) as exc:
            print(f'no running sampler for {args.pidfile}: {exc}', file=sys.stderr)
            return 1
        print(f'stopped sampler pid {pid}')
        return 0
    if args.command == 'sample':
        taken = 0
        stopping = []
        if args.loop:
            if args.pidfile is not None:
                args.pidfile.write_text(f'{os.getpid()}\n')
            try:
                signal.signal(signal.SIGTERM, lambda *_: stopping.append(True))
            except ValueError:      # not the main thread (tests)
                pass
        try:
            while True:
                record, _raw = battery_float.observe(phase='topup_log', runner=runner)
                with args.log.open('a') as handle:
                    handle.write(json.dumps(record, sort_keys=True, allow_nan=False) + '\n')
                print(json.dumps({k: record[k] for k in ('wall_time_s', 'is_charging', 'current_capacity_pct',
                                                         'external_connected', 'probe_error')}, sort_keys=True))
                taken += 1
                if not args.loop or stopping or (args.max_samples is not None and taken >= args.max_samples):
                    return 0
                try:
                    (sleep or time.sleep)(args.interval_s)
                except KeyboardInterrupt:
                    return 0
                if stopping:
                    return 0
        finally:
            if args.loop and args.pidfile is not None and args.pidfile.exists():
                args.pidfile.unlink()
    evidence = v4_topup.derive_from_sources(args.log, args.window_journal, (now or time.time)())
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence['admissible'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
