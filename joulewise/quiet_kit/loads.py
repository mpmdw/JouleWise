"""CPU duty loops and library MLX pulses, each reporting its exact CPU time."""
from __future__ import annotations

import argparse
import json
import resource
import time


def run(kind, duty, period_s, duration_s):
    if not 0 <= duty <= 1 or period_s <= 0 or duration_s < 0:
        raise ValueError('duty in [0,1], positive period and nonnegative duration required')
    before = resource.getrusage(resource.RUSAGE_SELF)
    start = time.monotonic()
    start_raw_ns = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    buffers = None
    if kind == 'gpu':
        from joulewise.powermetrics_fiducial import allocate_matmul_buffers, run_matmul_pulse
        buffers = allocate_matmul_buffers()
    end = start+duration_s
    cycles = 0
    while time.monotonic() < end:
        tick = start+cycles*period_s
        busy_until = min(end, tick+period_s*duty)
        if kind == 'gpu' and busy_until > time.monotonic():
            run_matmul_pulse(busy_until-time.monotonic(), buffers)
        else:
            while time.monotonic() < busy_until:
                pass
        time.sleep(max(0., min(end, tick+period_s)-time.monotonic()))
        cycles += 1
    after = resource.getrusage(resource.RUSAGE_SELF)
    elapsed = time.monotonic()-start
    cpu = after.ru_utime+after.ru_stime
    load_cpu = cpu-before.ru_utime-before.ru_stime
    return {'kind': kind, 'duty': duty, 'period_s': period_s, 'duration_s': duration_s,
            'elapsed_s': elapsed, 'cpu_seconds': cpu, 'load_cpu_seconds': load_cpu,
            'start_raw_ns': start_raw_ns, 'end_raw_ns': time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW),
            'true_cpu_s_per_s': cpu/elapsed if elapsed else None}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('kind', choices=('cpu', 'gpu'))
    parser.add_argument('--duty', type=float, required=True)
    parser.add_argument('--period-s', type=float, required=True)
    parser.add_argument('--duration-s', type=float, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(run(args.kind, args.duty, args.period_s, args.duration_s), sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
