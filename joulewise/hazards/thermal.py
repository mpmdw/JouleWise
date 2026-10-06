"""Thermal hazard: the OS reports thermal pressure.

Measured directly as the OS thermal-pressure level published on the notify
bus: ``/usr/bin/notifyutil -g com.apple.system.thermalpressurelevel`` prints
``com.apple.system.thermalpressurelevel <n>``; unprivileged and instant;
0 is nominal (read live on 10-05: 0).

Arm: level = 0, else REFUSE.  A failed, timed-out or unparsable read is
UNMEASURED and refuses.

``pmset -g therm`` is recorded as a diagnostic only.  On this Mac it prints
only "No thermal warning level has been recorded" notes (read live on 10-05),
so a check built on it tests nothing (plan §1, graft 1).

In the window the monitor reads the level every 5 s; :func:`span_findings`
gives ``thermal.os_level_nonzero`` for any sample in a member's stream that is
not 0.  The existing per-member powermetrics check
``thermal_pressure_elevated_in_window`` (``environment_admission.py``,
reached through strict validation in ``reduce.py``) is unchanged.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from joulewise.hazards.base import (
    PASS, REFUSE, UNMEASURED, Context, Measurement, Verdict, coverage_gap, finding,
    require_thresholds, row,
)

MODULE = "thermal"
NOTIFY_KEY = "com.apple.system.thermalpressurelevel"
NOTIFYUTIL_ARGV = ("/usr/bin/notifyutil", "-g", NOTIFY_KEY)
PMSET_THERM_ARGV = ("/usr/bin/pmset", "-g", "therm")  # diagnostic only, never judged
PROBE_TIMEOUT_S = 5.0

DEFAULT_THRESHOLDS: dict[str, Any] = {"max_level": 0, "max_gap_s": 15}
ARM_THRESHOLD_KEYS = ("max_level",)

_LINE = re.compile(r"\A" + re.escape(NOTIFY_KEY) + r" (-?[0-9]{1,20})\n?\Z")


class NotifyReader:
    """The same notify-bus state read in process (``notify_register_check`` then
    ``notify_get_state``), as ``notifyutil -g`` does, without a child process.

    The monitor reads it every 5 s; a child per read cost more CPU than every
    other in-window probe but ps.  Registration only observes the key.
    tests/hazards/test_thermal.py checks it equals ``notifyutil -g`` live.
    """

    def __init__(self) -> None:
        import ctypes
        import sys

        if sys.platform != "darwin":
            raise OSError("the notify bus requires macOS")
        self._ctypes = ctypes
        self._libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
        self._libc.notify_register_check.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
        self._libc.notify_get_state.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint64)]
        self._libc.notify_cancel.argtypes = [ctypes.c_int]
        token = ctypes.c_int()
        status = self._libc.notify_register_check(NOTIFY_KEY.encode(), ctypes.byref(token))
        if status != 0:
            raise OSError(f"notify_register_check status {status}")
        self._token = token.value

    def read(self) -> int:
        state = self._ctypes.c_uint64()
        status = self._libc.notify_get_state(self._token, self._ctypes.byref(state))
        if status != 0:
            raise OSError(f"notify_get_state status {status}")
        return int(state.value)

    def close(self) -> None:
        if self._token is not None:
            self._libc.notify_cancel(self._token)
            self._token = None


def parse_level(stdout: bytes) -> int:
    """The level from notifyutil's exact output; anything else raises ValueError."""

    try:
        text = stdout.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("notifyutil output is not ASCII") from exc
    match = _LINE.match(text)
    if match is None:
        raise ValueError(f"unrecognised notifyutil output {text[:80]!r}")
    return int(match.group(1))


def measure(ctx: Context, *, diagnostics: bool = False) -> Measurement:
    """Read the level; with ``diagnostics`` also keep ``pmset -g therm`` bytes (never judged)."""

    started = ctx.stamp()
    completed = ctx.run(NOTIFYUTIL_ARGV, PROBE_TIMEOUT_S)
    raw = [ctx.keep_raw("thermal.notifyutil.txt", completed.stdout)]
    values: dict[str, Any] = {"argv": list(NOTIFYUTIL_ARGV), "returncode": completed.returncode,
                              "stdout": completed.stdout.decode("utf-8", errors="replace"),
                              "level": None}
    error = None
    if completed.error:
        error = f"notifyutil could not run: {completed.error}"
    elif completed.timed_out:
        error = f"notifyutil timed out after {PROBE_TIMEOUT_S} s"
    elif completed.returncode != 0:
        error = f"notifyutil exit code {completed.returncode}"
    else:
        try:
            values["level"] = parse_level(completed.stdout)
        except ValueError as exc:
            error = str(exc)
    if diagnostics:
        therm = ctx.run(PMSET_THERM_ARGV, PROBE_TIMEOUT_S)
        raw.append(ctx.keep_raw("thermal.pmset-therm.txt", therm.stdout))
        values["pmset_therm_diagnostic"] = {
            "argv": list(PMSET_THERM_ARGV), "returncode": therm.returncode,
            "timed_out": therm.timed_out, "error": therm.error,
            "stdout": therm.stdout.decode("utf-8", errors="replace")}
    finished = ctx.stamp()
    return Measurement(MODULE, "instant", values, tuple(raw), started, finished, error)


def judge(measurement: Measurement, thresholds: Mapping[str, Any]) -> Verdict:
    limits = require_thresholds(MODULE, thresholds, ARM_THRESHOLD_KEYS)
    if measurement.module != MODULE:
        raise ValueError("thermal.judge received another module's measurement")
    if measurement.error:
        return Verdict(MODULE, UNMEASURED, (measurement.error,), limits)
    level = measurement.values["level"]
    if type(level) is not int:
        return Verdict(MODULE, UNMEASURED, ("thermal pressure level absent",), limits)
    observed = {"level": level}
    if level > limits["max_level"] or level < 0:
        return Verdict(MODULE, REFUSE, (f"OS thermal pressure level {level} is not nominal "
                                        f"(limit {limits['max_level']})",), limits, observed)
    return Verdict(MODULE, PASS, (), limits, observed)


def span_findings(samples: Sequence[Mapping[str, Any]], span: Mapping[str, Any],
                  thresholds: Mapping[str, Any] = DEFAULT_THRESHOLDS) -> list[dict[str, Any]]:
    """``thermal.os_level_nonzero`` and ``thermal.unmeasured`` for one member's stream."""

    start, stop = span["monotonic_ns"]
    found = []
    for item in samples:
        stamp = item["finished"]["monotonic_ns"]
        level = (item.get("values") or {}).get("level")
        if item.get("error") or level is None or not start <= stamp <= stop:
            continue
        if level != 0:
            found.append(finding("thermal.os_level_nonzero", span=span, observed=level,
                                 expected=0, interval={"monotonic_ns": [stamp, stamp]},
                                 detail=f"OS thermal pressure level {level} inside the stream",
                                 evidence=item.get("raw") or ()))
    good = [item["finished"]["monotonic_ns"] for item in samples
            if not item.get("error") and (item.get("values") or {}).get("level") is not None]
    gap = coverage_gap(good, start, stop, int(thresholds["max_gap_s"] * 1_000_000_000))
    if gap is not None:
        found.append(finding("thermal.unmeasured", span=span, observed=gap,
                             expected=thresholds["max_gap_s"],
                             detail="no thermal reading for longer than "
                                    f"{thresholds['max_gap_s']} s overlapping the span"))
    return found


# Inventory rows (configs/gates/physics_rows.json) whose physical check this
# module performs.  tests/hazards/test_physics_coverage.py keeps the two in step.
PROTECTS: tuple[tuple[str, str, str, int], ...] = (
    # base line 1482: `pmset -g therm` exited nonzero.
    row("joulewise/arm_readiness_evidence_t0.py", "_thermal_probe",
        "evidence_author_t0_machine_preflight_underivable", 1),
    # base line 1493: Thermal pressure: pmset therm lacks the 'No thermal/performance warning level has...
    row("joulewise/arm_readiness_evidence_t0.py", "_thermal_probe",
        "evidence_author_t0_machine_preflight_underivable", 2),
)

# Proxy rows on paths block 5 no longer runs that this module's direct
# measurement replaces (configs/gates/physics_rows.json, "retired_proxy").
SUPERSEDES: tuple[tuple[str, str, str, int], ...] = (
    # base line 1094: Display, idle, screensaver and thermal predicates are true, and the quiet_mac_pre...
    row("joulewise/arm_readiness.py", "<module>",
        "predicate t0.display_thermal_idle.v1", 1),
    # base line 7168: The MACHINE_PREFLIGHT receipt has display, screensaver, idle and thermal predicat...
    row("joulewise/arm_readiness.py", "_evaluate_rows",
        "readiness_dependency_refused (row t0.display_thermal_idle)", 1),
    # base line 1756: pmset -g therm parse and exit code
    row("joulewise/night_gate.py", "_check_machine",
        "night_probe_error (thermal output malformed; also 1763 thermal probe nonzero exit)", 1),
    # base line 1766: pmset -g therm: every CPU_Speed_Limit line must read 100
    row("joulewise/night_gate.py", "_check_machine",
        "night_refused_not_quiet (thermal predicate failed)", 1),
)
