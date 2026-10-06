#!/usr/bin/env python3
"""Stream the POWER-Z KM003C wall-side meter plus the SMC power keys to JSON lines.

A recorded, disclosed diagnostic of whole-machine DC input: never a refusal,
never a claim number.  Standard library only (``joulewise.external.km003c_usb``
reaches libusb and CommonCrypto through ctypes).  Runs at plain QoS: the
2026-10-06 probe found 200 ms polls at plain QoS clean, and the reader costs
well under 1 % of one core.

    km003c_monitor.py --out STREAM.jsonl [--duration S] [--stop-file PATH]
                      [--rate 2] [--poll-ms 200] [--reset] [--init-attempts 4]

Lines (``k`` is the kind):

``h``  header, first line: schema, status ("streaming" or "absent" with the
       reason), model, USB ids and descriptor strings, hardware and firmware
       versions read from the meter, the HardwareID used for StreamingAuth
       (hex) and its form, the auth level, rate index, samples per second,
       poll period, QoS, init attempts and their errors, the process id
       (``process_id``; ``vid``/``pid`` are the USB ids), start times on
       CLOCK_MONOTONIC_RAW, ``time.monotonic_ns`` (the driver's span clock)
       and CLOCK_REALTIME, SMC keys and units.  The RAW/monotonic pairs at
       start and end let a harvest move member spans onto RAW without the
       hazard monitor's journal.
``b``  one per poll, including polls that found the meter's queue empty
       (n = 0, p = ""), so poll timing and the SMC series stay continuous:
       ``tx`` CLOCK_MONOTONIC_RAW ns just before the GetData request is
       written, ``rx`` CLOCK_MONOTONIC_RAW ns when the answer's read returned,
       ``rt`` CLOCK_REALTIME ns at receipt, ``n`` samples, ``p`` the raw
       n x 20 sample bytes in hex, ``smc`` the SMC keys read right after the
       USB answer, and ``smc_err`` only when a key failed.
``e``  a protocol error: an answer that is not an AdcQueue PutData (raw hex,
       first 100 bytes) or a USB error on a poll.
``t``  trailer, last line: poll, empty, bad and USB-error counts, elapsed
       seconds, end times (RAW and monotonic), the process's own rusage and
       the stop reason.

Stops on SIGTERM, SIGINT or SIGHUP (the current poll finishes, then
StopGraph, Disconnect, release), on ``--duration`` or when ``--stop-file``
appears.  Initialisation is retried with a USB reset between attempts.  A
meter that is absent (no libusb, no device, every init attempt failed) gives
a header with status "absent", a trailer and exit 0: an absent meter is a
recorded fact, not a failure.  Exit 2 only for usage errors or an unwritable
``--out``.
"""

from __future__ import annotations

import argparse
import json
import os
import resource
import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.external import km003c_usb as usb  # noqa: E402
from joulewise.hazards import smc  # noqa: E402

SCHEMA = "joulewise.km003c_stream.v1"
RAW = time.CLOCK_MONOTONIC_RAW


def raw_ns() -> int:
    return time.clock_gettime_ns(RAW)


def rusage() -> dict:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    return {"utime_s": ru.ru_utime, "stime_s": ru.ru_stime, "maxrss": ru.ru_maxrss,
            "nvcsw": ru.ru_nvcsw, "nivcsw": ru.ru_nivcsw}


def init_meter(args, errors: list[str], stopping=lambda: False):
    """(meter, header fields) on success; raises MeterAbsent after the last failed
    attempt, or as soon as ``stopping()`` is true between attempts (a SIGTERM
    during initialisation ends the retries)."""

    lib = usb.load_libusb(args.libusb)  # MeterAbsent when libusb is missing
    for attempt in range(1, args.init_attempts + 1):
        if stopping():
            raise usb.MeterAbsent(f"stopped by a signal before init attempt {attempt}")
        device = None
        try:
            device = usb.UsbDevice(lib, vid=args.vid, pid=args.pid,
                                   reset=args.reset or attempt > 1)
            meter = usb.Meter(device)
            meter.drain()
            meter.connect()
            fields = {"descriptor": device.descriptor(), **meter.device_info()}
            level, used, form = 0, None, None
            # Firmware 2.x returns the HardwareID block in plaintext; older
            # firmware encrypts it.  Try both readings.
            for candidate, name in zip(meter.hardware_ids(), ("plaintext", "decrypted")):
                if len(candidate) == 12:
                    level = meter.auth(candidate)
                    if level:
                        used, form = candidate, name
                        break
            if not level:
                raise RuntimeError("StreamingAuth refused for the plaintext and decrypted HardwareID")
            meter.start_graph(args.rate)
            fields.update(hardware_id=used.hex(), hardware_id_form=form, auth_level=level,
                          init_attempts=attempt)
            return meter, fields
        except Exception as exc:  # transient USB state: reset and retry
            errors.append(f"attempt {attempt}: {type(exc).__name__}: {exc}")
            if device is not None:
                device.close()
            if attempt < args.init_attempts and not stopping():
                time.sleep(1.0)
    raise usb.MeterAbsent(f"all {args.init_attempts} init attempts failed")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--rate", type=int, default=2, choices=sorted(usb.RATES_SPS))
    ap.add_argument("--poll-ms", type=float, default=200.0)
    ap.add_argument("--duration", type=float, default=0.0, help="seconds; 0 = until signalled")
    ap.add_argument("--stop-file", type=Path, default=None)
    ap.add_argument("--reset", action="store_true", help="reset the USB device before the first attempt")
    ap.add_argument("--init-attempts", type=int, default=4)
    ap.add_argument("--vid", type=lambda s: int(s, 0), default=usb.VID)
    ap.add_argument("--pid", type=lambda s: int(s, 0), default=usb.PID)
    ap.add_argument("--libusb", default=None, help="path to libusb-1.0.dylib (default: Homebrew)")
    args = ap.parse_args(argv)
    if args.init_attempts < 1 or args.poll_ms <= 0:
        ap.error("--init-attempts must be >= 1 and --poll-ms > 0")
    try:
        out = open(args.out, "x", buffering=1 << 16)
    except OSError as exc:
        print(f"km003c_monitor: cannot create {args.out}: {exc}", file=sys.stderr)
        return 2

    stop = {"reason": None}

    def on_signal(signum, _frame):
        stop["reason"] = f"signal {signum}"

    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, on_signal)

    poll_s = args.poll_ms / 1000.0
    reader = smc.Reader()
    header = {"k": "h", "schema": SCHEMA, "status": "streaming", "reason": None,
              "model": "POWER-Z KM003C", "vid": f"{args.vid:04x}", "pid": f"{args.pid:04x}",
              "rate_idx": args.rate, "sps": usb.RATES_SPS[args.rate], "poll_s": poll_s,
              "qos": "default", "init_errors": [], "process_id": os.getpid(),
              "smc_keys": list(smc.KEYS), "smc_units": dict(smc.UNITS)}
    meter = None
    counts = {"polls": 0, "empties": 0, "bad": 0, "usb_errors": 0}
    t_start = raw_ns()
    # Everything after the output is open sits inside the cleanup boundary: a
    # failed write (a full disk) still stops the graph and releases the meter.
    try:
        try:
            meter, fields = init_meter(args, header["init_errors"],
                                       stopping=lambda: stop["reason"] is not None)
            header.update(fields)
        except usb.MeterAbsent as exc:
            header.update(status="absent", reason=str(exc), init_attempts=len(header["init_errors"]))
        header.update(start_raw_ns=raw_ns(), start_mono_ns=time.monotonic_ns(), start_real_ns=time.time_ns())
        t_start = header["start_raw_ns"]
        out.write(json.dumps(header, sort_keys=True) + "\n")
        out.flush()
        if meter is not None:
            next_t = time.monotonic()
            deadline = next_t + args.duration if args.duration > 0 else None
            last_flush = next_t
            keys = smc.KEYS
            while stop["reason"] is None:
                packet = meter.poll_request()
                tx = raw_ns()
                try:
                    meter.usb.write(packet, 500)
                    reply = meter.usb.read(500)
                    rx = raw_ns()
                    rt = time.time_ns()
                    payload, n, ok = usb.parse_put_data(reply)
                except usb.UsbError as exc:
                    rx, rt, payload, n, ok, reply = raw_ns(), time.time_ns(), b"", 0, False, None
                    counts["usb_errors"] += 1
                    out.write(json.dumps({"k": "e", "rx": rx, "usb_error": str(exc)}) + "\n")
                counts["polls"] += 1
                read = reader.read(keys)
                values = read["values"]
                smc_text = ",".join(f'"{key}":{"null" if values[key] is None else repr(values[key])}'
                                    for key in keys)
                if ok:
                    if n == 0:
                        counts["empties"] += 1
                    line = ('{"k":"b","tx":%d,"rx":%d,"rt":%d,"n":%d,"p":"%s","smc":{%s}'
                            % (tx, rx, rt, n, payload.hex(), smc_text))
                    if read["errors"]:
                        line += ',"smc_err":' + json.dumps(read["errors"])
                    out.write(line + "}\n")
                elif reply is not None:
                    counts["bad"] += 1
                    out.write(json.dumps({"k": "e", "rx": rx, "raw": reply[:100].hex()}) + "\n")
                now = time.monotonic()
                if now - last_flush >= 1.0:
                    out.flush()
                    last_flush = now
                if deadline is not None and now >= deadline:
                    stop["reason"] = "duration"
                    break
                if args.stop_file is not None and counts["polls"] % 5 == 0 and args.stop_file.exists():
                    stop["reason"] = "stop file"
                    break
                next_t += poll_s
                pause = next_t - time.monotonic()
                if pause > 0:
                    # A signal handler that returns does not cut the sleep short
                    # (PEP 475); the loop exits after at most one poll period.
                    time.sleep(pause)
                else:
                    next_t = time.monotonic()  # late: resume the grid from now
    finally:
        if meter is not None:
            try:
                meter.stop_graph()
                meter.disconnect()
            finally:
                meter.usb.close()
        reader.close()
        end_raw = raw_ns()
        trailer = {"k": "t", **counts, "elapsed_s": (end_raw - t_start) / 1e9, "end_raw_ns": end_raw,
                   "end_mono_ns": time.monotonic_ns(), **rusage(),
                   "stop_reason": stop["reason"] or ("absent" if meter is None else "exception")}
        try:
            out.write(json.dumps(trailer, sort_keys=True) + "\n")
            out.flush()
            os.fsync(out.fileno())
        finally:
            out.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
