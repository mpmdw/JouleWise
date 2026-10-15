"""Job-wide low-load clock logger, run as a stdlib child."""
from __future__ import annotations

import argparse
import os
import signal
import time

from .paths import append, fence


def main(argv=None):
    from joulewise.hazards import clock
    from joulewise.hazards.base import Context
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--kind', default='measurement')
    parser.add_argument('--parent-pid', type=int)
    args = parser.parse_args(argv)
    path = fence(args.out)
    stopped = False
    def stop(*_):
        nonlocal stopped
        stopped = True
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    ctx = Context()
    while not stopped and (args.parent_pid is None or os.getppid() == args.parent_pid):
        row = clock.sample(ctx)
        try:
            boot = clock.read_boot_session_inprocess()
        except Exception as e:
            boot = None
            row['error'] = str(e)
        frequency = row.get('frequency')
        if frequency:
            frequency['frequency_ppm'] = frequency.get('ppm')
        append(path, {'kind': args.kind, 'boot_session_uuid': boot, **row})
        until = time.monotonic()+10.
        while not stopped and time.monotonic() < until:
            if args.parent_pid is not None and os.getppid() != args.parent_pid:
                stopped = True
                break
            time.sleep(min(.25, max(0., until-time.monotonic())))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
