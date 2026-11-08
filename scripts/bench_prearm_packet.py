#!/usr/bin/env python3
"""Single-process synthetic packet benchmark; no measurements or launchd calls."""

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.prearm_packet import build, canonical, run_checks, verify  # noqa: E402
from joulewise.terminal_wake import publish, read_event  # noqa: E402
from tests.test_prearm_packet import PrearmPacketTests  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=int, default=7)
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("repetitions must be positive")
    fixture = PrearmPacketTests()
    fixture.setUp()
    timings = {key: [] for key in ("original_static_s", "off_host_build_s", "host_verify_s", "marker_publish_read_s")}
    try:
        for index in range(256):
            (fixture.root / f"kit/synthetic-{index:03d}.json").write_bytes(b" " * 4096)
        expected = run_checks(fixture.root, fixture.recipe)
        for index in range(args.repetitions):
            started = time.perf_counter()
            assert run_checks(fixture.root, fixture.recipe) == expected
            timings["original_static_s"].append(time.perf_counter() - started)
            packet = fixture.base / f"packet-{index}.json"
            started = time.perf_counter()
            digest = build(fixture.root, fixture.recipe, packet, now=100)
            timings["off_host_build_s"].append(time.perf_counter() - started)
            started = time.perf_counter()
            assert verify(fixture.root, fixture.recipe, packet, digest, now=101) == expected
            timings["host_verify_s"].append(time.perf_counter() - started)
            started = time.perf_counter()
            marker = publish(fixture.base, "synthetic", "HAZARD_PACK", now=100)
            assert read_event(marker) is not None
            timings["marker_publish_read_s"].append(time.perf_counter() - started)
        print(json.dumps({"repetitions": args.repetitions, "python": sys.version.split()[0],
                          "synthetic_extra_bytes": 256 * 4096, "exact_results_equal": True,
                          "results_sha256": hashlib.sha256(canonical(expected)).hexdigest(),
                          "timings": {key: {"median_s": statistics.median(values), "min_s": min(values),
                                            "max_s": max(values)} for key, values in timings.items()},
                          "caveat": "marker timing excludes launchd scheduling and watchdog gates"}, sort_keys=True, indent=2))
    finally:
        fixture.doCleanups()


if __name__ == "__main__":
    main()
