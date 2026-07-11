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


RUNNING = True


def _stop(_signum: int, _frame: object) -> None:
    global RUNNING
    RUNNING = False


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
    previous_endpoint_s = time.monotonic() - interval_s
    with output.open("wb", buffering=0) as handle:
        while RUNNING and (args.n is None or index < args.n):
            if index == 0 and args.n is None and mode == "wide":
                time.sleep(1.2)
            if index:
                time.sleep(interval_s)
                # On SIGTERM, finish one complete interval after the controller's
                # stop marker so strict reduction has a real right-edge bracket.
                if not RUNNING:
                    time.sleep(interval_s)
            document = dict(documents[index % len(documents)])
            endpoint_s = time.monotonic()
            document["elapsed_ns"] = max(
                1, int((endpoint_s - previous_endpoint_s) * 1_000_000_000)
            )
            previous_endpoint_s = endpoint_s
            native_timestamp = datetime.now(UTC)
            if mode == "inconsistent":
                native_timestamp += timedelta(seconds=60)
            document["timestamp"] = native_timestamp
            if mode == "contaminated_post" and invocation >= 4:
                gpu = dict(document.get("gpu", {}))
                gpu["idle_ratio"] = 0.0
                gpu["freq_hz"] = 1200.0
                document["gpu"] = gpu
            if index:
                handle.write(b"\0")
            handle.write(plistlib.dumps(document))
            index += 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
