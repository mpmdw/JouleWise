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


OWNED_REGISTRY_ENV = "JOULEWISE_TEST_OWNED_DESCENDANT_REGISTRY"
OWNED_REGISTRY_SCHEMA = "joulewise.test_owned_fake_sampler.v1"
LOGICAL_ACK_PATH_ENV = "JW_FAKE_SAMPLER_ACK_PATH"
LOGICAL_CLOCK_ORIGIN_ENV = "JW_FAKE_LOGICAL_CLOCK_ORIGIN"
LOGICAL_ACK_SCHEMA = "joulewise.test_sampler_ack.v1"
LOGICAL_FIRST_RECORD_DELAY_S = 0.1
LOGICAL_READY_EPSILON_S = 0.000001


def register_owned_sampler() -> None:
    registry_value = os.environ.get(OWNED_REGISTRY_ENV)
    if not registry_value:
        return
    registry = Path(registry_value)
    pid = os.getpid()
    record = registry / f"fake-sampler-{pid}.json"
    temporary = registry / f".fake-sampler-{pid}.tmp"
    temporary.write_text(
        json.dumps(
            {
                "schema": OWNED_REGISTRY_SCHEMA,
                "pid": pid,
                "pgid": os.getpgid(0),
                "sampler_path": str(Path(__file__).resolve()),
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, record)


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-o", required=True)
args, _unknown = parser.parse_known_args()
register_owned_sampler()

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
ack_path_value = os.environ.get(LOGICAL_ACK_PATH_ENV)
logical_origin_value = os.environ.get(LOGICAL_CLOCK_ORIGIN_ENV)
ack_path = Path(ack_path_value) if ack_path_value else None
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
# Bytes read from the event file that do not yet form a whole line.  The event
# file is appended to by a *separate* process, so any read can land mid-line.
events_buffer = bytearray()
ack_handle = None
active_on: float | None = None


def acknowledge(handle, sequence: int, event_type: str, **metadata) -> None:
    global ack_handle
    if ack_path is None:
        return
    handle.flush()
    os.fsync(handle.fileno())
    if ack_handle is None:
        ack_handle = ack_path.open("x", encoding="utf-8")
    ack_handle.write(
        json.dumps(
            {
                "schema": LOGICAL_ACK_SCHEMA,
                "sequence": sequence,
                "event_type": event_type,
                **metadata,
            },
            sort_keys=True,
        )
        + "\n"
    )
    ack_handle.flush()
    os.fsync(ack_handle.fileno())


def drain_events(handle) -> int:
    """Consume only whole event lines; hold a torn tail until it completes.

    The writer appends to the event file from another process, so a read can
    land in the middle of a line.  Text-mode ``readline()`` both *returns and
    consumes* such a partial line, so the fragment fails to parse, the rest of
    the line arrives as a second unparseable fragment, and the event -- with
    its acknowledgement -- is lost permanently.  Bytes are therefore buffered
    and only newline-terminated lines are parsed; whatever follows the last
    newline stays in the buffer for the next drain.  This mirrors the
    buffered-until-newline idiom already used by the parent-side reader in
    ``tests/test_calibration_exits.py``.
    """

    global events_handle, active_on
    if events_handle is None:
        try:
            events_handle = events_path.open("rb")
        except OSError:
            return 0
    while True:
        chunk = events_handle.read(65536)
        if not chunk:
            break
        events_buffer.extend(chunk)
    consumed = 0
    while True:
        newline = events_buffer.find(b"\n")
        if newline < 0:
            break
        raw_line = bytes(events_buffer[:newline])
        del events_buffer[: newline + 1]
        if not raw_line.strip():
            continue
        try:
            row = json.loads(raw_line)
            timestamp_s = float(row["timestamp_s"])
            event_type = str(row["event_type"])
            sequence = row.get("test_protocol_sequence")
        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
            UnicodeDecodeError,
        ) as error:
            # A COMPLETE line that does not parse is a fixture/protocol defect,
            # never a transport artefact -- the torn-tail case is handled above
            # and never reaches here.  Silently dropping it is what made the
            # original event-loss wedge invisible, so fail loudly instead.
            raise RuntimeError(
                "fake sampler could not parse a complete event line: "
                f"{raw_line!r}"
            ) from error
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
        if isinstance(sequence, int) and not isinstance(sequence, bool):
            acknowledge(handle, sequence, event_type)
    return consumed


with output.open("wb", buffering=0) as capture:
    # The legacy direct-fixture path may observe the clock once for anchor
    # placement; record *quantity* never does. The logical writer instead
    # supplies a fixed origin and advances all subsequent work by events.
    if logical_origin_value is None:
        first_endpoint = float(
            os.environ.get(
                "JW_FAKE_INITIAL_ENDPOINT",
                str(origin + ((time.time() - origin) / time_scale)),
            )
        )
    else:
        first_endpoint = float(logical_origin_value) + LOGICAL_FIRST_RECORD_DELAY_S
    append_record(capture, first_endpoint, 10000)
    if mode != "one":
        append_record(capture, first_endpoint + 1.0, 10000)
    if ack_path is not None:
        acknowledge(
            capture,
            0,
            "sampler_ready",
            logical_epoch_s=first_endpoint + LOGICAL_READY_EPSILON_S,
        )
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
if ack_handle is not None:
    ack_handle.close()
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
