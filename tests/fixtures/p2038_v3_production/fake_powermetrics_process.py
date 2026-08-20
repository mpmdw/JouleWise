#!/usr/bin/env python3
"""Fast process fixture carrying the independent p2-038.3 native timeline."""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import signal
import time
from datetime import UTC, datetime
from pathlib import Path


STOP_REQUESTED = False


def _stop(_signum: int, _frame: object) -> None:
    global STOP_REQUESTED
    STOP_REQUESTED = True


def _profile() -> dict:
    return json.loads(
        Path(__file__).with_name("paired_clock_native_records.json").read_text(
            encoding="utf-8"
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-n", type=int)
    parser.add_argument("-i", type=int, default=1000)
    parser.add_argument("-o", required=True)
    args, _unknown = parser.parse_known_args()
    mode = os.environ.get("P2038_FAKE_POWERMETRICS_MODE", "normal")
    state_path_text = os.environ.get("P2038_FAKE_POWERMETRICS_STATE")
    invocation = 0
    if state_path_text:
        state_path = Path(state_path_text)
        try:
            invocation = int(state_path.read_text(encoding="utf-8")) + 1
        except (FileNotFoundError, ValueError):
            invocation = 1
        state_path.write_text(str(invocation), encoding="utf-8")
    # Direct adversarial arms use SystemClock rather than the deterministic
    # positive-path replay clock.  Give those arms a contemporaneous stream;
    # they are expected to exercise their own refusal semantics.
    base_s = float(os.environ.get("P2038_V3_FIXTURE_EPOCH_S", time.time()))
    template_raw = (
        Path(__file__).parents[1] / "powermetrics_sample.plist"
    ).read_bytes()
    template = plistlib.loads(next(frame for frame in template_raw.split(b"\0") if frame.strip()))
    rows = _profile()["native_records"]
    if args.n is not None:
        rows = rows[: args.n]
    signal.signal(signal.SIGTERM, _stop)
    with Path(args.o).open("wb", buffering=0) as handle:
        for index, row in enumerate(rows):
            document = dict(template)
            # The independent production profile is pinned to the D-079
            # acceptance epoch; do not inherit the capture date's old OS
            # identity from the parser template.
            document["hw_model"] = "Mac15,9"
            document["kern_osversion"] = "25F84"
            document["timestamp"] = datetime.fromtimestamp(
                base_s + float(row["endpoint_offset_s"]), UTC
            )
            document["elapsed_ns"] = int(row["elapsed_ns"])
            document["is_delta"] = True
            processor = dict(document["processor"])
            elapsed_s = document["elapsed_ns"] / 1_000_000_000.0
            for rail, counter in (
                ("cpu_power", "cpu_energy"),
                ("gpu_power", "gpu_energy"),
                ("ane_power", "ane_energy"),
            ):
                processor[counter] = round(float(processor[rail]) * elapsed_s)
            document["processor"] = processor
            if mode == "inconsistent":
                document["timestamp"] = datetime.fromtimestamp(
                    base_s + float(row["endpoint_offset_s"]) + 60.0, UTC
                )
            if mode == "contaminated_post" and args.n is not None:
                gpu = dict(document.get("gpu", {}))
                gpu["idle_ratio"] = 0.0
                gpu["freq_hz"] = 1200.0
                document["gpu"] = gpu
            if mode == "rail_only" and args.n is not None:
                document.pop("gpu", None)
            if mode == "extreme_post" and args.n is not None:
                for rail in ("cpu_power", "gpu_power", "ane_power"):
                    processor[rail] = 1_000_000_000_000.0
                    processor[rail.replace("_power", "_energy")] = (
                        1_000_000_000_000_000
                    )
                document["processor"] = processor
            if index:
                handle.write(b"\0")
            handle.write(plistlib.dumps(document))
            # Keep this a stream, rather than completing every future frame
            # before controller-side admission can form its causal slice.
            # The cap keeps the fixture fast while preserving ordered arrival.
            if index + 1 < len(rows):
                time.sleep(min(args.i / 1_000.0, 0.01))
    while args.n is None and not STOP_REQUESTED:
        time.sleep(0.01)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
