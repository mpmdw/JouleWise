#!/usr/bin/env python3.13
"""Probe one detached cadence pin using its own read-only launcher plan."""

import argparse
from datetime import date, datetime, time, timedelta
from functools import lru_cache
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

LOCAL = ZoneInfo("America/Los_Angeles")


def local_stamp(epoch):
    return datetime.fromtimestamp(epoch, LOCAL).isoformat()


def sweep(day, probe):
    start = int(datetime.combine(day, time.min, LOCAL).timestamp())
    stop = int(datetime.combine(day + timedelta(days=1), time.min, LOCAL).timestamp())
    minute_epochs = list(range(start, stop, 60))
    checkpoints = minute_epochs + [stop - 1]
    boundaries = [start]
    for left, right in zip(checkpoints, checkpoints[1:]):
        left_admitted = probe(left)["admitted"]
        if left_admitted == probe(right)["admitted"]:
            continue
        while right - left > 1:
            middle = (left + right) // 2
            if probe(middle)["admitted"] == left_admitted:
                left = middle
            else:
                right = middle
        boundaries.append(right)
    bands = [
        {
            "from": local_stamp(first),
            "through": local_stamp(after - 1),
            "admitted": probe(first)["admitted"],
        }
        for first, after in zip(boundaries, boundaries[1:] + [stop])
    ]
    bisect_witnesses = [
        {
            "before": probe(epoch - 1),
            "at": probe(epoch),
            "after": probe(epoch + 1),
        }
        for epoch in boundaries[1:]
    ]
    return {
        "date": day.isoformat(),
        "bands": bands,
        "witnesses": bisect_witnesses,
        "samples": [probe(epoch) for epoch in checkpoints],
    }


def kit_windows(value):
    """Find explicit batch or blackout window fields in the unchanged kit."""
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = key.lower().replace("-", "_")
            if ("window" in normalized and "batch" in normalized) or "blackout" in normalized:
                if child:
                    yield key
            yield from kit_windows(child)
    elif isinstance(value, list):
        for child in value:
            yield from kit_windows(child)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--kit", type=Path, required=True)
    parser.add_argument("--legs", required=True, help="comma-separated kit leg IDs")
    parser.add_argument("--batch-window", help="omit to pass None")
    when = parser.add_mutually_exclusive_group(required=True)
    when.add_argument("--t0", type=int, help="epoch seconds")
    when.add_argument("--day", type=date.fromisoformat, action="append")
    args = parser.parse_args()

    kit = args.kit.resolve(strict=True)
    declared_windows = list(kit_windows(json.loads(kit.read_bytes())))
    if declared_windows:
        parser.error(f"kit names a window in {declared_windows}")
    sys.path.insert(0, str(args.checkout.resolve(strict=True)))
    from scripts.launch_cadence_span import cadence_plan

    @lru_cache(maxsize=None)
    def probe(epoch):
        result = {"epoch": epoch, "local": local_stamp(epoch)}
        try:
            plan = cadence_plan(kit, args.legs, args.batch_window, t0=epoch)
        except ValueError as error:
            return {**result, "admitted": False, "refusal": str(error)}
        return {**result, "admitted": True, "worst_case_s": plan["worst_case_s"]}

    result = probe(args.t0) if args.t0 is not None else [sweep(day, probe) for day in args.day]
    json.dump(result, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
