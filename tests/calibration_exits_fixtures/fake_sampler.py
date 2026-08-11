#!/usr/bin/env python3
"""Event-driven, O(protocol-event-count) powermetrics process fixture."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import time
from xml.sax.saxutils import escape


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-o", required=True)
args, _unknown = parser.parse_known_args()

mode = os.environ.get("JW_FAKE_SAMPLER_MODE", "normal")
stubborn = mode.endswith("-stubborn")
if stubborn:
    mode = mode.removesuffix("-stubborn")

running = True


def stop(_signum, _frame):
    global running
    running = False


signal.signal(signal.SIGTERM, signal.SIG_IGN if stubborn else stop)
output = Path(args.o)
if mode == "never":
    while running:
        time.sleep(0.01)
    raise SystemExit(0)

origin = float(os.environ.get("JW_FAKE_TIME_ORIGIN", "1700000000"))
time_scale = float(os.environ.get("JW_FAKE_TIME_SCALE", "1"))
hw_model = os.environ["JW_FAKE_HW_MODEL"]
os_build = os.environ["JW_FAKE_OS_BUILD"]
events_path = output.parent.parent / "events.jsonl"
last_endpoint: float | None = None
record_count = 0


def document(endpoint: float, elapsed_s: float, gpu_power: int) -> bytes:
    timestamp = datetime.fromtimestamp(endpoint, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    elapsed_ns = max(1, round(elapsed_s * 1_000_000_000))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>is_delta</key><true/>
<key>kern_bootargs</key><string></string>
<key>kern_boottime</key><integer>1</integer>
<key>thermal_pressure</key><string>Nominal</string>
<key>hw_model</key><string>{escape(hw_model)}</string>
<key>kern_osversion</key><string>{escape(os_build)}</string>
<key>timestamp</key><date>{timestamp}</date>
<key>elapsed_ns</key><integer>{elapsed_ns}</integer>
<key>processor</key><dict>
<key>cpu_power</key><integer>10000</integer>
<key>gpu_power</key><integer>{gpu_power}</integer>
<key>ane_power</key><integer>0</integer>
<key>cpu_energy</key><real>{10000 * elapsed_s:.12g}</real>
<key>gpu_energy</key><real>{gpu_power * elapsed_s:.12g}</real>
<key>ane_energy</key><real>0.0</real>
</dict></dict></plist>'''.encode()


def append_record(handle, endpoint: float, gpu_power: int) -> None:
    global last_endpoint, record_count
    if last_endpoint is not None and endpoint <= last_endpoint + 1e-9:
        return
    elapsed_s = 0.1 if last_endpoint is None else endpoint - last_endpoint
    if record_count:
        handle.write(b"\0")
    handle.write(document(endpoint, elapsed_s, gpu_power))
    last_endpoint = endpoint
    record_count += 1


def emit_fixed_span(handle, start: float, end: float, count: int, power: int) -> None:
    if end <= start:
        return
    for index in range(1, count + 1):
        append_record(handle, start + (end - start) * index / count, power)


def emit_idle_to(handle, endpoint: float) -> None:
    start = last_endpoint if last_endpoint is not None else endpoint - 0.5
    emit_fixed_span(handle, start, endpoint, 32, 10000)


events_handle = None
active_on: float | None = None


def drain_events(handle) -> int:
    global events_handle, active_on
    if events_handle is None:
        try:
            events_handle = events_path.open(encoding="utf-8")
        except OSError:
            return 0
    consumed = 0
    while True:
        line = events_handle.readline()
        if not line:
            break
        try:
            row = json.loads(line)
            timestamp_s = float(row["timestamp_s"])
            event_type = str(row["event_type"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
        consumed += 1
        if event_type in {"sampling_started", "sampling_stopped"}:
            emit_idle_to(handle, timestamp_s)
        elif event_type in {"pulse_command_on", "warmup_command_on"}:
            emit_idle_to(handle, timestamp_s)
            active_on = timestamp_s
        elif event_type in {"pulse_command_off", "warmup_command_off"}:
            if active_on is not None:
                emit_fixed_span(handle, active_on, timestamp_s, 64, 30000)
            active_on = None
    return consumed


with output.open("wb", buffering=0) as capture:
    # Anchor placement may observe the clock once; record *quantity* never
    # does.  This mirrors the accelerated writer clock closely enough for the
    # real clock-intersection gate while keeping all subsequent work event-led.
    first_endpoint = float(
        os.environ.get(
            "JW_FAKE_INITIAL_ENDPOINT",
            str(origin + ((time.time() - origin) / time_scale)),
        )
    )
    append_record(capture, first_endpoint, 10000)
    if mode != "one":
        append_record(capture, first_endpoint + 1.0, 10000)
    while running:
        if mode != "one":
            drain_events(capture)
        time.sleep(0.001)
    if mode != "one":
        # Consume the final sampling_stopped line once.  There is no capture
        # rewrite: every protocol event contributes records at most once.
        drain_events(capture)

if events_handle is not None:
    events_handle.close()
result_path = os.environ.get("JW_FAKE_SAMPLER_RESULT_PATH")
if result_path:
    raw = output.read_bytes()
    Path(result_path).write_text(
        json.dumps(
            {
                "record_count": record_count,
                "capture_sha256": hashlib.sha256(raw).hexdigest(),
                "capture_bytes": len(raw),
                "result": "complete",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
