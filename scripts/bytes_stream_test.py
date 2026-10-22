#!/usr/bin/env python3
"""Non-claim MLX streaming probe: evaluate a fresh reduction of B bytes N times.

The payload byte count is a logical read count, not a memory-controller counter.
Allocation/initialization are outside the recorded CLOCK_MONOTONIC_RAW span.
The caller must capture rails and KM003C concurrently and retain this receipt.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time


def stream(byte_count, repeats, *, mx=None, clock_ns=None):
    if type(byte_count) is not int or byte_count <= 0 or type(repeats) is not int or repeats <= 0:
        raise ValueError("byte count and repeats must be positive integer counts")
    if mx is None:
        import mlx.core as mx  # Lazy: schema/help/tests work on a non-Mac seat.
    if clock_ns is None:
        clock_ns = lambda: time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    data = mx.ones((byte_count,), dtype=mx.uint8)
    mx.eval(data)
    mx.synchronize()
    start = clock_ns()
    for _ in range(repeats):
        # A newly constructed, immediately evaluated reduction per iteration
        # prevents reuse of one cached lazy result. No payload-sized output.
        result = mx.sum(data)
        mx.eval(result)
    mx.synchronize()
    end = clock_ns()
    if end <= start:
        raise ValueError("stream has no positive monotonic span")
    return {"schema_version": "joulewise.bytes_stream.v1", "non_claim": True,
            "clock": "CLOCK_MONOTONIC_RAW", "start_ns": start, "end_ns": end,
            "duration_s": (end - start) / 1_000_000_000,
            "bytes_per_read": byte_count, "repeats": repeats, "bytes_read": byte_count * repeats,
            "boundary": "logical uint8 payload reads; excludes initialization and reduction workspace"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bytes", type=int, required=True, dest="byte_count")
    parser.add_argument("--repeats", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    result = stream(args.byte_count, args.repeats)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
