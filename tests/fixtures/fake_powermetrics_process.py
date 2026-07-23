#!/usr/bin/env python3
"""Small process-level powermetrics CLI fixture for P2-038 tests.

It reuses the committed captured plist documents and changes only the native
whole-second date plus requested interval. The production parser, NUL framing,
rail extraction, launch/readiness bracket, and termination path remain real.
"""

from __future__ import annotations

import argparse
import os
import plistlib
import signal
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path


STOP_REQUESTED_AT_S: float | None = None


def _stop(_signum: int, _frame: object) -> None:
    global STOP_REQUESTED_AT_S
    if STOP_REQUESTED_AT_S is None:
        STOP_REQUESTED_AT_S = time.monotonic()


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-n", type=int)
    parser.add_argument("-i", type=int, default=1000)
    parser.add_argument("-o", required=True)
    args, _unknown = parser.parse_known_args()
    mode = os.environ.get("P2038_FAKE_POWERMETRICS_MODE", "normal")
    invocation = 0
    state_path_text = os.environ.get("P2038_FAKE_POWERMETRICS_STATE")
    if state_path_text:
        state_path = Path(state_path_text)
        try:
            invocation = int(state_path.read_text()) + 1
        except (FileNotFoundError, ValueError):
            invocation = 1
        state_path.write_text(str(invocation))

    fixture = Path(__file__).with_name("powermetrics_sample.plist")
    documents = [
        plistlib.loads(frame)
        for frame in fixture.read_bytes().split(b"\0")
        if frame.strip()
    ]
    signal.signal(signal.SIGTERM, _stop)
    output = Path(args.o)
    interval_s = args.i / 1000.0
    index = 0
    # Record 0's averaging window opens at process start: real powermetrics
    # never reports support from before its own spawn, and the D-078 causal
    # constraint rejects such data.
    previous_endpoint_s = time.monotonic()
    with output.open("wb", buffering=0) as handle:
        while args.n is None or index < args.n:
            if index == 0 and args.n is None and mode == "wide":
                time.sleep(1.2)
            if index == 0:
                # Real powermetrics emits its first record only after one full
                # averaging interval; record 0's window END must causally
                # follow the spawn by at least elapsed_ns (D-078).
                time.sleep(interval_s)
            if index:
                time.sleep(interval_s)
            document = dict(documents[index % len(documents)])
            endpoint_s = time.monotonic()
            document["elapsed_ns"] = max(
                1, int((endpoint_s - previous_endpoint_s) * 1_000_000_000)
            )
            previous_endpoint_s = endpoint_s
            # Keep the delta-aggregate invariant power * elapsed == energy;
            # the D-078 estimator fails closed on inconsistent records.
            processor = dict(document["processor"])
            elapsed_s = document["elapsed_ns"] / 1_000_000_000.0
            for rail, counter in (
                ("cpu_power", "cpu_energy"),
                ("gpu_power", "gpu_energy"),
                ("ane_power", "ane_energy"),
            ):
                processor[counter] = round(float(processor[rail]) * elapsed_s)
            document["processor"] = processor
            native_timestamp = datetime.now(UTC)
            if mode == "inconsistent":
                native_timestamp += timedelta(seconds=60)
            document["timestamp"] = native_timestamp
            if mode == "contaminated_post" and invocation >= 3:
                gpu = dict(document.get("gpu", {}))
                gpu["idle_ratio"] = 0.0
                gpu["freq_hz"] = 1200.0
                document["gpu"] = gpu
            # Keep the pre-run admission capture complete so this mode proves
            # CPU/GPU idle on merit.  Only the post-run sentinel is rail-only,
            # which withholds the drift term without laundering admission.
            if mode == "rail_only" and invocation >= 3:
                document.pop("gpu", None)
            if mode == "extreme_post" and invocation >= 4:
                processor = dict(document["processor"])
                for rail in ("cpu_power", "gpu_power", "ane_power"):
                    processor[rail] = 1_000_000_000_000.0
                    counter = rail.replace("_power", "_energy")
                    processor[counter] = round(
                        1_000_000_000_000.0
                        * document["elapsed_ns"]
                        / 1_000_000_000.0
                    )
                document["processor"] = processor
            if index:
                handle.write(b"\0")
            handle.write(plistlib.dumps(document))
            index += 1
            # SIGTERM can arrive after a sample write but before the next loop
            # condition.  Pin the fixture contract to an endpoint at least one
            # requested interval after the signal so the controller's stop
            # marker always has a real right-edge sample bracket.
            if (
                STOP_REQUESTED_AT_S is not None
                and endpoint_s >= STOP_REQUESTED_AT_S + interval_s
            ):
                break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
