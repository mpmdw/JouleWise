"""Read Darwin's stored clock correction without changing kernel clock state.

The ABI is sys/timex.h in the macOS SDK: native unsigned int/int and long,
including native padding (not Linux's struct timex). modes is always zero.
Raw output bytes are retained as hex in the JSON probe for custody/replay.
"""
from __future__ import annotations

import ctypes
from fractions import Fraction
import math
import sys
from collections.abc import Mapping

PROBE_SCHEMA = "joulewise.kernel_frequency_probe.v1"
ANCHOR_CHECK_VERSION = "kernel-frequency-residual/v1"
GATE_SCHEMA = "joulewise.kernel_frequency_gate.v1"
FREQUENCY_SCALE = 1 << 16
ANCHOR_LIMIT_NS = 5_000_000


class Timex(ctypes.Structure):
    _fields_ = [("modes", ctypes.c_uint), ("offset", ctypes.c_long),
                ("freq", ctypes.c_long), ("maxerror", ctypes.c_long),
                ("esterror", ctypes.c_long), ("status", ctypes.c_int),
                ("constant", ctypes.c_long), ("precision", ctypes.c_long),
                ("tolerance", ctypes.c_long), ("ppsfreq", ctypes.c_long),
                ("jitter", ctypes.c_long), ("shift", ctypes.c_int),
                ("stabil", ctypes.c_long), ("jitcnt", ctypes.c_long),
                ("calcnt", ctypes.c_long), ("errcnt", ctypes.c_long),
                ("stbcnt", ctypes.c_long)]


def read_kernel_frequency(*, libc=None):
    """Return raw word, scaled ppm, syscall status and untouched output bytes.

    TIME_ERROR (5) is a successful read of an undisciplined clock, not errno.
    An injected libc supports hermetic ABI and error tests on any platform.
    """
    if libc is None:
        if sys.platform != "darwin" or ctypes.sizeof(ctypes.c_long) != 8:
            raise OSError("kernel frequency probe requires 64-bit macOS")
        libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
    call = libc.ntp_adjtime
    call.argtypes = [ctypes.POINTER(Timex)]
    call.restype = ctypes.c_int
    value = Timex()  # zero modes: read only, including on error paths
    ctypes.set_errno(0)
    status = int(call(ctypes.byref(value)))
    return {"schema_version": PROBE_SCHEMA, "modes": 0,
            "raw_word": int(value.freq), "ppm": value.freq / FREQUENCY_SCALE,
            "call_status": status, "timex_status": int(value.status),
            "errno": ctypes.get_errno() if status == -1 else 0,
            "raw_hex": bytes(value).hex()}


_PROBE_KEYS = {"schema_version", "modes", "raw_word", "ppm", "call_status",
               "timex_status", "errno", "raw_hex"}


def validate_probe(record):
    """Authenticate interpretation against the preserved struct bytes."""
    if not isinstance(record, Mapping) or set(record) != _PROBE_KEYS:
        raise ValueError("kernel frequency probe keys are invalid")
    if record["schema_version"] != PROBE_SCHEMA or any(
            type(record[key]) is not int for key in
            ("modes", "raw_word", "call_status", "timex_status", "errno")):
        raise ValueError("kernel frequency probe fields are invalid")
    if record["modes"] != 0 or not 0 <= record["call_status"] <= 5 or record["errno"] != 0:
        raise ValueError("kernel frequency read failed or was not read-only")
    if type(record["ppm"]) is not float or not math.isfinite(record["ppm"]):
        raise ValueError("kernel frequency ppm is invalid")
    try:
        raw = bytes.fromhex(record["raw_hex"])
        if len(raw) != ctypes.sizeof(Timex) or raw.hex() != record["raw_hex"]:
            raise ValueError("wrong timex byte length/encoding")
        value = Timex.from_buffer_copy(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("kernel frequency raw bytes are invalid") from exc
    if (value.modes != 0 or value.freq != record["raw_word"]
            or value.status != record["timex_status"]
            or record["ppm"] != value.freq / FREQUENCY_SCALE):
        raise ValueError("kernel frequency interpretation differs from raw bytes")
    return record


def anchor_residual_ns(delta_ns, span_ns, frequency):
    """Exact absolute residual; delta is signed wall-minus-RAW movement."""
    validate_probe(frequency)
    if type(delta_ns) is not int or type(span_ns) is not int or span_ns < 0:
        raise ValueError("anchor delta/span is invalid")
    return abs(Fraction(delta_ns) - Fraction(frequency["raw_word"] * span_ns,
                                            FREQUENCY_SCALE * 1_000_000))


def frequency_gate(frequency, t_stream_max_s):
    """Ruling 76 B.2, with exact arithmetic at the inclusive 5 ms limit."""
    validate_probe(frequency)
    if isinstance(t_stream_max_s, bool):
        raise ValueError("maximum sampler stream is invalid")
    span = Fraction(str(t_stream_max_s))
    if span <= 0:
        raise ValueError("maximum sampler stream must be positive")
    rate_ppm = Fraction(abs(frequency["raw_word"]), FREQUENCY_SCALE)
    bound_s = Fraction(37, 10_000) + (rate_ppm + Fraction(1, 4)) * span / 1_000_000
    margin_s = Fraction(5, 1000) - bound_s
    return {"schema_version": GATE_SCHEMA, "kernel_frequency": dict(frequency),
            "t_stream_max_s": float(span), "h_max_ms": 3.60,
            "placement_margin_ms": 0.10, "frequency_margin_ppm": 0.25,
            "limit_ms": 5.0, "bound_ms": float(bound_s * 1000),
            "margin_ms": float(margin_s * 1000), "passes": margin_s >= 0}


def validate_gate(gate):
    if not isinstance(gate, Mapping):
        raise ValueError("kernel frequency gate is absent")
    expected = frequency_gate(gate.get("kernel_frequency"), gate.get("t_stream_max_s"))
    if dict(gate) != expected or not expected["passes"]:
        raise ValueError("kernel frequency gate failed or differs from recomputation")
    return gate
