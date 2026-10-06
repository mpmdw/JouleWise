"""Battery hazard: the Mac is on battery, charging, or its battery current is not ~0.

Measured directly from ``/usr/sbin/ioreg -r -c AppleSmartBattery``; the exact
stdout bytes are kept.  The frozen BFG grammar (``battery_float.parse``)
reads ExternalConnected, IsCharging, InstantAmperage (signed), Amperage
(gauge-averaged), UpdateTime and Voltage; it is reused, not edited.  The
``PowerTelemetryData`` accumulators and the adapter wattage are read by a
separate line reader in this module.

Arm (plan §2.3): ExternalConnected Yes; IsCharging No; |InstantAmperage| <=
200 mA; the reading no older than 180 s.  A probe or parse failure is
UNMEASURED and refuses.

In the window the monitor polls every 5 s and keeps the raw bytes whenever
UpdateTime changes (a new gauge publication; the gauge publishes every 60 s).
The 5 s poll reads the grammar's six fields in process
(:class:`RegistryReader`, about 0.03 ms of CPU against 13 ms for an ``ioreg``
child); ``ioreg`` itself runs only when one of them changes, so each
publication is read once, by the grammar, within 5 s of appearing.  The
member rule of plan §3.4 is :func:`span_findings`.

Accumulator units (lane L1 check, 2026-10-05, on recorded and live bytes)
-------------------------------------------------------------------------
Data: 66 distinct archived publications with ``PowerTelemetryData`` (UpdateTime
1790373525 to 1791193581: the 09-25 float captures, every c1 and c2
calibration capture of 10-01, block 3's 10-03 and 10-04 captures and the
premortem desk reads of 10-05) plus a live desk read at UpdateTime 1791249441.

1. ``SystemPowerIn`` is the adapter input power in mW: it equals
   ``SystemVoltageIn`` (mV) x ``SystemCurrentIn`` (mA) / 1000 to within 1.7 %
   on all 66 publications (e.g. 27139 mV x 2047 mA = 55.55 W against 54919;
   27408 x 496 = 13.59 W against 13619).
2. ``SystemLoad`` = ``SystemPowerIn`` - ``BatteryPower`` (mW).  The one
   publication with a nonzero instant BatteryPower (c2 d06 post, UpdateTime
   1790899521) reads SystemPowerIn 91581, SystemLoad 91715, BatteryPower -134:
   91581 - (-134) = 91715 exactly.  BatteryPower > 0 is charging, < 0 is
   discharging.  The gauge's InstantAmperage read 0 at that same publication.
3. Each ``Accumulated*`` field adds its instantaneous mW value once per tick;
   each ``*AccumulatorCount`` counts ticks.  Ticks run at 0.980 to 0.991 per
   UpdateTime second over all 65 intervals (594 per 600 s; 178 per 180 s;
   51795 per 52320 s), so one tick is about 1.01 s and accumulated/count is
   the mean power in mW over the counted ticks.  Between consecutive publications
   dAccumulatedSystemPowerIn / dSystemPowerInAccumulatorCount gives a mean
   input power (32.6 W during a calibration capture, 3.2 W idle) consistent
   with the instantaneous readings.
4. BatteryPower is split by sign into two accumulators:
   ``AccumulatedBatteryPower`` / ``BatteryPowerAccumulatorCount`` sum the
   charging ticks (positive), ``AccumulatedBatteryDischarge`` /
   ``BatteryDischargeAccumulatorCount`` sum the discharging ticks (negative;
   ioreg prints them as unsigned 64-bit two's complement).  Proven by an exact
   identity on every one of the 65 consecutive-publication intervals:
   d(AccumulatedSystemLoad) - d(AccumulatedSystemPowerIn)
       = -(d(AccumulatedBatteryDischarge) + d(AccumulatedBatteryPower)),
   with zero residual on all 65 (e.g. 81318250 = 81460902 - 142652 across
   09-25 20:47 to 10-01 06:17).
5. Positive control on a real event: between the 09-25 20:47 publication
   (discharge count 7627) and the 10-01 06:17 t0 publication (22670), the
   discharge accumulator gained 15043 ticks at a mean of -5415 mW.  The
   archived 10-01 04:24:54Z gauge reading inside that interval (the 0555Z
   attempt) was -447 mA at 12180 mV = -5444 mW.  They agree within 0.6 %.
6. The battery assists briefly even on a 140 W adapter: each of the 28
   archived calibration captures (180 or 240 s between its pre and post
   publications) shows 7-32 discharge ticks at a mean of -122 to -151 mW
   (about -11 mA at 12.2 V) while InstantAmperage read 0 at both bounding
   publications.  That is far below the 2.4 W rule; it is disclosed as
   ``battery.accumulator_activity``.
   ``BatteryPowerAccumulatorCount`` stayed at 4727 (no charging tick) from
   10-01 to the live read of 10-05.

So the unit of ``AccumulatedBatteryPower`` (and of the discharge
accumulator) per count is mW, i.e. about mJ per tick, and the accumulator
rule of §3.4 is applied: an interval between two publications that overlaps
a member's span is flagged when |d(accumulated)/d(count)| exceeds
200 mA x the publication's Voltage (2.436 W at 12180 mV) for either sign.
"""

from __future__ import annotations

import ctypes
import json
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from joulewise import battery_float
from joulewise.hazards.base import (
    PASS, REFUSE, UNMEASURED, Context, Measurement, Verdict, coverage_gap, finding,
    require_thresholds, row,
)

MODULE = "battery"
IOREG_BATTERY_ARGV = battery_float.IOREG_BATTERY_ARGV
PROBE_TIMEOUT_S = battery_float.PROBE_TIMEOUT_S
ProbeError = battery_float.ProbeError

DEFAULT_THRESHOLDS: dict[str, Any] = {
    "limit_ma": battery_float.LIMIT_MA,                  # 200 mA, #421
    "max_update_age_s": battery_float.MAX_UPDATE_AGE_S,  # 180 s
    "max_unobserved_s": 120,  # in window: no publication for longer -> battery.unmeasured
}
ARM_THRESHOLD_KEYS = ("limit_ma", "max_update_age_s")

ACCUMULATOR_FIELDS = (
    "BatteryPower", "AccumulatedBatteryPower", "BatteryPowerAccumulatorCount",
    "AccumulatedBatteryDischarge", "BatteryDischargeAccumulatorCount",
    "SystemPowerIn", "AccumulatedSystemPowerIn", "SystemPowerInAccumulatorCount",
    "SystemLoad", "AccumulatedSystemLoad", "SystemLoadAccumulatorCount",
    "SystemVoltageIn", "SystemCurrentIn", "PowerTelemetryErrorCount",
)
_TOP_LINE = re.compile(rb'^ {6}"(PowerTelemetryData|AdapterDetails)" = \{(.*)\}$', re.M)
_INT_MEMBER = re.compile(rb'"([A-Za-z0-9_]+)"=([0-9]{1,20})(?=[,}]|$)')
_UPDATE_TIME = re.compile(rb'^ {6}"UpdateTime" = ([0-9]{1,20})$', re.M)


# --------------------------------------------------------------------------
# Reading


def _signed64(text: bytes) -> int:
    value = int(text)
    if value >= 2 ** 64:
        raise ValueError("integer exceeds 64 bits")
    return value - 2 ** 64 if value >= 2 ** 63 else value


def read_accumulators(raw: bytes) -> dict[str, Any]:
    """The separate line reader: top-level PowerTelemetryData and AdapterDetails.

    Returns ``{"power_telemetry": {field: int|None}, "adapter_watts": int|None}``.
    Absent lines give None values; a malformed member is skipped, never guessed.
    """

    telemetry: dict[str, int | None] = {name: None for name in ACCUMULATOR_FIELDS}
    watts = None
    for match in _TOP_LINE.finditer(raw):
        name, body = match.group(1), match.group(2)
        members = {key.decode(): value for key, value in _INT_MEMBER.findall(body)}
        if name == b"PowerTelemetryData":
            for field in ACCUMULATOR_FIELDS:
                if field in members:
                    telemetry[field] = _signed64(members[field])
        elif name == b"AdapterDetails" and "Watts" in members:
            watts = _signed64(members["Watts"])
    return {"power_telemetry": telemetry, "adapter_watts": watts}


def update_time(raw: bytes) -> int | None:
    """The top-level UpdateTime without the full grammar (the monitor's cheap check)."""

    match = _UPDATE_TIME.search(raw)
    return int(match.group(1)) if match else None


# --------------------------------------------------------------------------
# The in-process poll


REGISTRY_CLASS = b"AppleSmartBattery"
# The six top-level properties the frozen grammar judges (ExternalConnected,
# IsCharging, InstantAmperage, Amperage, UpdateTime, Voltage).
REGISTRY_KEYS = ("UpdateTime", "ExternalConnected", "IsCharging", "InstantAmperage", "Amperage",
                 "Voltage")
_CF_STRING_ENCODING_UTF8 = 0x08000100
_CF_NUMBER_SINT64 = 4


class RegistryReader:
    """The grammar's six fields read in process from the AppleSmartBattery entry
    of the IO registry: the same properties ``ioreg -r -c AppleSmartBattery``
    prints, without a child process.

    ``read()`` returns ``{key: int | bool | None}`` (None: the property is
    absent); InstantAmperage and Amperage come back signed.  Each read matches
    the service afresh (``IOServiceGetMatchingService``) and copies one
    property at a time (``IORegistryEntryCreateCFProperty``): read-only, and a
    driver that re-registers is never read through a stale entry.  Raises
    OSError off macOS, when the service is absent, or on an unexpected value
    type.  tests/hazards/test_battery.py checks it against ``ioreg`` live.

    It is a trigger, never a measurement: the monitor runs ``ioreg``, whose
    bytes the frozen grammar judges and the custody keeps, whenever a value
    read here changes.
    """

    def __init__(self) -> None:
        if sys.platform != "darwin":
            raise OSError("the IO registry requires macOS")
        iokit = ctypes.CDLL("/System/Library/Frameworks/IOKit.framework/IOKit")
        cf = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
        iokit.IOServiceMatching.restype = ctypes.c_void_p
        iokit.IOServiceMatching.argtypes = [ctypes.c_char_p]
        iokit.IOServiceGetMatchingService.restype = ctypes.c_uint
        iokit.IOServiceGetMatchingService.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        iokit.IORegistryEntryCreateCFProperty.restype = ctypes.c_void_p
        iokit.IORegistryEntryCreateCFProperty.argtypes = [ctypes.c_uint, ctypes.c_void_p,
                                                          ctypes.c_void_p, ctypes.c_uint]
        iokit.IOObjectRelease.restype = ctypes.c_int
        iokit.IOObjectRelease.argtypes = [ctypes.c_uint]
        cf.CFStringCreateWithCString.restype = ctypes.c_void_p
        cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
        cf.CFGetTypeID.restype = ctypes.c_ulong
        cf.CFGetTypeID.argtypes = [ctypes.c_void_p]
        cf.CFNumberGetTypeID.restype = ctypes.c_ulong
        cf.CFBooleanGetTypeID.restype = ctypes.c_ulong
        cf.CFNumberGetValue.restype = ctypes.c_bool
        cf.CFNumberGetValue.argtypes = [ctypes.c_void_p, ctypes.c_long, ctypes.c_void_p]
        cf.CFBooleanGetValue.restype = ctypes.c_bool
        cf.CFBooleanGetValue.argtypes = [ctypes.c_void_p]
        cf.CFRelease.argtypes = [ctypes.c_void_p]
        self._iokit, self._cf = iokit, cf
        self._number, self._boolean = cf.CFNumberGetTypeID(), cf.CFBooleanGetTypeID()
        self._keys: dict[str, int] = {}
        for name in REGISTRY_KEYS:
            ref = cf.CFStringCreateWithCString(None, name.encode("ascii"), _CF_STRING_ENCODING_UTF8)
            if not ref:
                self.close()
                raise OSError(f"CFStringCreateWithCString({name}) failed")
            self._keys[name] = ref

    def read(self) -> dict[str, int | bool | None]:
        matching = self._iokit.IOServiceMatching(REGISTRY_CLASS)
        if not matching:
            raise OSError("IOServiceMatching(AppleSmartBattery) failed")
        service = self._iokit.IOServiceGetMatchingService(0, matching)  # consumes ``matching``
        if not service:
            raise OSError("no AppleSmartBattery service in the IO registry")
        try:
            return {name: self._value(service, name, key) for name, key in self._keys.items()}
        finally:
            self._iokit.IOObjectRelease(service)

    def _value(self, service: int, name: str, key: int) -> int | bool | None:
        ref = self._iokit.IORegistryEntryCreateCFProperty(service, key, None, 0)
        if not ref:
            return None
        try:
            kind = self._cf.CFGetTypeID(ref)
            if kind == self._boolean:
                return bool(self._cf.CFBooleanGetValue(ref))
            if kind == self._number:
                value = ctypes.c_int64()
                if not self._cf.CFNumberGetValue(ref, _CF_NUMBER_SINT64, ctypes.byref(value)):
                    raise OSError(f"{name} is not an exact 64-bit integer")
                return value.value
            raise OSError(f"{name} has CF type id {kind}, not a number or boolean")
        finally:
            self._cf.CFRelease(ref)

    def close(self) -> None:
        for ref in self._keys.values():
            self._cf.CFRelease(ref)
        self._keys = {}


def _grammar(raw: bytes, wall_time_s: float) -> dict[str, Any]:
    """The frozen BFG grammar on one captured ioreg document.

    The only place this package calls the grammar.  It replays one observation
    at a given wall time and never consumes or produces a window verdict, the
    raw-boundary use that ``tests/test_battery_float_consumers.py`` registers
    by its exact call text.
    """

    return battery_float.parse(raw, wall_time_s)


def parse_reading(raw: bytes, wall_time_s: float) -> dict[str, Any]:
    """The frozen grammar's fields plus the accumulators.  Raises ProbeError on a
    reading the grammar refuses; a stale reading is returned with its age (the
    judge refuses it)."""

    try:
        parsed = _grammar(raw, wall_time_s)
    except ProbeError as exc:
        age = getattr(exc, "update_age_s", None)
        if age is None:
            raise
        # Stale is a judged property, not a probe failure: re-read the same
        # bytes at the gauge's own UpdateTime to obtain the fields.
        parsed = _grammar(raw, wall_time_s - age)
        parsed["update_age_s"] = age
    values = {
        "external_connected": parsed["external_connected"],
        "is_charging": parsed["is_charging"],
        "instant_amperage_ma": parsed["instant_amperage_ma"],
        "amperage_ma": parsed["amperage_ma"],
        "voltage_mv": parsed["voltage_mv"],
        "update_time_s": parsed["update_time_s"],
        "update_age_s": parsed["update_age_s"],
        "fully_charged": parsed["fully_charged"],
        "current_capacity_pct": parsed["current_capacity_pct"],
    }
    values.update(read_accumulators(raw))
    return values


def measure(ctx: Context) -> Measurement:
    started = ctx.stamp()
    completed = ctx.run(IOREG_BATTERY_ARGV, PROBE_TIMEOUT_S)
    raw_refs = (ctx.keep_raw("battery.ioreg", completed.stdout),)
    values: dict[str, Any] = {"argv": list(IOREG_BATTERY_ARGV), "returncode": completed.returncode,
                              "stderr": completed.stderr.decode("utf-8", errors="replace")}
    error = None
    if completed.error:
        error = f"ioreg could not run: {completed.error}"
    elif completed.timed_out:
        error = f"ioreg timed out after {PROBE_TIMEOUT_S} s"
    elif completed.returncode != 0:
        error = f"ioreg exit code {completed.returncode}"
    else:
        try:
            values.update(parse_reading(completed.stdout, started.wall_ns / 1e9))
        except ValueError as exc:  # ProbeError is a ValueError
            error = f"ioreg bytes refused by the BFG grammar: {exc}"
    finished = ctx.stamp()
    return Measurement(MODULE, "instant", values, raw_refs, started, finished, error)


# --------------------------------------------------------------------------
# Judge


def judge(measurement: Measurement, thresholds: Mapping[str, Any]) -> Verdict:
    limits = require_thresholds(MODULE, thresholds, ARM_THRESHOLD_KEYS)
    if measurement.module != MODULE:
        raise ValueError("battery.judge received another module's measurement")
    if measurement.error:
        return Verdict(MODULE, UNMEASURED, (measurement.error,), limits)
    values = measurement.values
    reasons = list(reading_reasons(values, limits, include_amperage=False))
    if values["update_age_s"] > limits["max_update_age_s"]:
        reasons.append(f"UpdateTime stale: {values['update_age_s']:g} s > "
                       f"{limits['max_update_age_s']} s")
    observed = {key: values[key] for key in ("external_connected", "is_charging",
                                             "instant_amperage_ma", "amperage_ma",
                                             "update_age_s", "voltage_mv")}
    observed["adapter_watts"] = values.get("adapter_watts")
    return Verdict(MODULE, REFUSE if reasons else PASS, tuple(reasons), limits, observed)


def reading_reasons(values: Mapping[str, Any], limits: Mapping[str, Any], *,
                    include_amperage: bool) -> list[str]:
    reasons = []
    if values["external_connected"] is not True:
        reasons.append("ExternalConnected is not Yes (on battery)")
    if values["is_charging"] is not False:
        reasons.append("IsCharging is not No (charging)")
    if abs(values["instant_amperage_ma"]) > limits["limit_ma"]:
        reasons.append(f"|InstantAmperage| {abs(values['instant_amperage_ma'])} mA > "
                       f"{limits['limit_ma']} mA")
    amperage = values.get("amperage_ma")
    if include_amperage and amperage is not None and abs(amperage) > limits["limit_ma"]:
        reasons.append(f"|Amperage| {abs(amperage)} mA > {limits['limit_ma']} mA")
    return reasons


# --------------------------------------------------------------------------
# Accumulators and the member rule (plan §3.4)


ACCUMULATOR_SIGNS = (("charge", "AccumulatedBatteryPower", "BatteryPowerAccumulatorCount"),
                     ("discharge", "AccumulatedBatteryDischarge",
                      "BatteryDischargeAccumulatorCount"))


def accumulator_interval(earlier: Mapping[str, Any], later: Mapping[str, Any]) -> dict[str, Any]:
    """Mean battery power between two publications, split by sign, in mW.

    ``charge_mean_mw`` = d(AccumulatedBatteryPower) / d(BatteryPowerAccumulatorCount)
    and ``discharge_mean_mw`` = d(AccumulatedBatteryDischarge) /
    d(BatteryDischargeAccumulatorCount), each over its own nonzero ticks
    (None when no tick of that sign occurred).

    Each sign is read on its own.  ``<sign>_unavailable`` is None when that
    sign's rule can be evaluated, otherwise the reason it cannot: a field not
    read at both publications, a counter that went backward (a reboot or gauge
    reset), or energy that moved with no tick.  ``available`` is True only
    when both signs can be evaluated.
    """

    a = earlier.get("power_telemetry") or {}
    b = later.get("power_telemetry") or {}
    result: dict[str, Any] = {}
    for label, total, count in ACCUMULATOR_SIGNS:
        result[f"{label}_ticks"] = None
        result[f"{label}_mean_mw"] = None
        result[f"{label}_unavailable"] = None
        if any(item.get(name) is None for item in (a, b) for name in (total, count)):
            result[f"{label}_unavailable"] = f"{total} or {count} not read at both publications"
            continue
        ticks = b[count] - a[count]
        energy = b[total] - a[total]
        result[f"{label}_ticks"] = ticks
        result[f"{label}_energy_mw_ticks"] = energy
        if ticks < 0:
            result[f"{label}_unavailable"] = f"{count} went backward by {-ticks}: a counter reset"
        elif ticks == 0 and energy != 0:
            result[f"{label}_unavailable"] = f"{total} moved by {energy} with no {count} tick"
        elif ticks:
            result[f"{label}_mean_mw"] = energy / ticks
    result["available"] = all(result[f"{label}_unavailable"] is None
                              for label, _total, _count in ACCUMULATOR_SIGNS)
    return result


def publications(readings: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Distinct gauge publications from monitor journal readings, in time order.

    A publication is the first good reading carrying a new UpdateTime.  Its
    time is UpdateTime mapped into the controller's monotonic domain through
    that reading's own (wall, monotonic) stamp pair.
    """

    seen: dict[int, dict[str, Any]] = {}
    for item in readings:
        values = item.get("values") or {}
        if item.get("error") or values.get("update_time_s") is None:
            continue
        key = values["update_time_s"]
        if key in seen:
            continue
        stamp = item["started"]
        offset_ns = stamp["wall_ns"] - stamp["monotonic_ns"]
        seen[key] = {"update_time_s": key, "monotonic_ns": key * 1_000_000_000 - offset_ns,
                     "values": values, "reading": item}
    return [seen[key] for key in sorted(seen)]


def span_findings(readings: Sequence[Mapping[str, Any]], span: Mapping[str, Any],
                  thresholds: Mapping[str, Any] = DEFAULT_THRESHOLDS) -> list[dict[str, Any]]:
    """``battery.member_span``, ``battery.accumulator_activity``,
    ``battery.accumulator_unavailable`` and ``battery.unmeasured``.

    ``span`` is ``{"monotonic_ns": [start, stop], ...}`` (the member's
    sampler stream, controller ``time.monotonic_ns``).  The publications in
    force are the last one at or before the start, every one inside the span
    and the first one at or after the end.  Conservative by design: it can
    also flag a neighbouring member.
    """

    limits = dict(thresholds)
    start, stop = span["monotonic_ns"]
    pubs = publications(readings)
    before = [p for p in pubs if p["monotonic_ns"] <= start]
    inside = [p for p in pubs if start < p["monotonic_ns"] < stop]
    after = [p for p in pubs if p["monotonic_ns"] >= stop]
    in_force = ([before[-1]] if before else []) + inside + ([after[0]] if after else [])
    found: list[dict[str, Any]] = []
    for pub in in_force:
        reasons = reading_reasons(pub["values"], limits, include_amperage=True)
        if reasons:
            found.append(finding(
                "battery.member_span", span=span, observed=_observed(pub), expected=limits,
                detail="; ".join(reasons), evidence=pub["reading"].get("raw") or (),
                interval={"monotonic_ns": [pub["monotonic_ns"], pub["monotonic_ns"]]}))
    for earlier, later in zip(in_force, in_force[1:]):
        delta = accumulator_interval(earlier["values"], later["values"])
        voltage = later["values"].get("voltage_mv") or earlier["values"].get("voltage_mv")
        interval = {"monotonic_ns": [earlier["monotonic_ns"], later["monotonic_ns"]]}
        unavailable = {label: delta[f"{label}_unavailable"]
                       for label, _total, _count in ACCUMULATOR_SIGNS
                       if delta[f"{label}_unavailable"]}
        if not voltage:
            unavailable = {label: "Voltage not read at either publication"
                           for label, _total, _count in ACCUMULATOR_SIGNS}
        if unavailable:
            # The rule did not run for this sign on this interval: disclosed,
            # never silently passed.
            found.append(finding(
                "battery.accumulator_unavailable", span=span,
                observed={**delta, "voltage_mv": voltage, "unavailable": unavailable},
                expected=None, interval=interval,
                detail=(f"accumulator rule not evaluated between publications "
                        f"{earlier['update_time_s']} and {later['update_time_s']}: "
                        + "; ".join(f"{label}: {reason}"
                                    for label, reason in sorted(unavailable.items())))))
        if not voltage:
            continue
        limit_mw = limits["limit_ma"] * voltage / 1000
        for label, _total, _count in ACCUMULATOR_SIGNS:
            mean = delta[f"{label}_mean_mw"]
            if label in unavailable or mean is None:
                continue
            code = ("battery.member_span" if abs(mean) > limit_mw
                    else "battery.accumulator_activity")
            found.append(finding(
                code, span=span, observed={**delta, "voltage_mv": voltage}, expected=limit_mw,
                interval=interval,
                detail=(f"{label} accumulator mean {mean:+.1f} mW over "
                        f"{delta[f'{label}_ticks']} ticks between publications "
                        f"{earlier['update_time_s']} and {later['update_time_s']}; "
                        f"limit {limit_mw:.1f} mW")))
    gap = coverage_gap([p["monotonic_ns"] for p in pubs], start, stop,
                       int(limits["max_unobserved_s"] * 1_000_000_000))
    if gap is not None:
        found.append(finding("battery.unmeasured", span=span, observed=gap,
                             expected=limits["max_unobserved_s"],
                             detail="no gauge publication observed for more than "
                                    f"{limits['max_unobserved_s']} s overlapping the span"))
    return found


def _observed(pub: Mapping[str, Any]) -> dict[str, Any]:
    values = pub["values"]
    return {key: values.get(key) for key in ("update_time_s", "external_connected",
                                             "is_charging", "instant_amperage_ma",
                                             "amperage_ma", "voltage_mv")}


# Inventory rows (configs/gates/physics_rows.json) whose physical check this
# module performs.  tests/hazards/test_physics_coverage.py keeps the two in step.
#
# PROTECTS is _PROTECTS_WRITTEN plus the rows of the frozen BFG module
# (joulewise/battery_float.py) that this module now evaluates through it.  Those
# rows are read from the coverage map on first use, not written here: the
# consumer guard (tests/test_battery_float_consumers.py) reserves the names of
# the grammar's primitives as strings in any production file that names its
# module, and two of those keys name one.  tests/hazards/test_battery.py pins
# the loaded rows literally, so the coverage check stays two-sided.
COVERAGE_MAP = Path(__file__).resolve().parents[2] / "configs" / "gates" / "physics_rows.json"
FROZEN_GRAMMAR_FILE = "joulewise/battery_float.py"
_PROTECTS_WRITTEN: tuple[tuple[str, str, str, int], ...] = (
    # base line 1136: AC state, supply, negotiation and power policy match the frozen policy. The produ...
    row("joulewise/arm_readiness.py", "<module>",
        "predicate t0.power_path.v1", 1),
    # base line 1970: On battery: live `pmset -g batt` does not report 'AC Power'.
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_power",
        "evidence_author_t0_power_preflight_underivable", 1),
    # base line 1999: The ioreg battery-float probe errored (grammar, staleness, read failure).
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_power",
        "evidence_author_t0_power_preflight_underivable", 5),
    # base line 2002: Battery not at float: charging, or nonzero current (IsCharging, InstantAmperage).
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_power",
        "evidence_author_t0_power_preflight_underivable", 6),
    # base line 1254: ioreg battery probe could not be run/parsed, or UpdateTime older than MAX_UPDATE_...
    row("joulewise/night_agent_install.py", "validate_install",
        "battery_float.observe ProbeError (uncaught here; Transaction catch-all exit 1)", 1),
    # base line 1272: Live ioreg reading: AC connected, not charging, |InstantAmperage| <= 200 mA, righ...
    row("joulewise/night_agent_install.py", "validate_install",
        "battery not at float (Refused 3)", 1),
    # base line 1664: live pmset -g batt output contains 'AC Power'
    row("joulewise/night_gate.py", "_check_machine",
        "night_refused_not_quiet (ac_power)", 1),
    # base line 1693: ioreg probe ran and its bytes parsed under the frozen BFG grammar
    row("joulewise/night_gate.py", "_check_machine",
        "night_probe_error (battery_float probe_error)", 1),
    # base line 1695: ioreg AppleSmartBattery: ExternalConnected Yes, IsCharging No, |InstantAmperage|...
    row("joulewise/night_gate.py", "_check_machine",
        "night_refused_battery_float", 1),
    # base line 954: re-parses raw ioreg battery output at the arm, publication and t0 boundaries: on...
    row("joulewise/v5_qualification.py", "battery_boundaries",
        "battery passed=False (probe error, timeout, rc!=0, wrong argv, parse failure, or parsed not passed)", 1),
    # base line 148: raw ioreg shows AC attached, not charging, at float
    row("scripts/check_v5_arm_abort.py", "battery_sources",
        "battery_float.require_pass", 1),
    # base line 694: Boundary (arm/publication/T-0) and per-bundle raw ioreg readings show AC power an...
    row("scripts/harvest_v5_g2b_window.py", "harvest",
        "battery_observation_not_passed (RECOVER; also lines 642, 645)", 1),
    # base line 88: raw ioreg battery records at arm/publication/t0 show on-battery or charging
    row("scripts/harvest_v5_qualification.py", "harvest",
        "battery_boundary_not_passed (admission-abort branch)", 1),
    # base line 110: raw ioreg battery records show on battery or charging at a boundary
    row("scripts/harvest_v5_qualification.py", "harvest",
        "battery_boundary_not_passed", 1),
)

# Proxy rows on paths block 5 no longer runs that this module's direct
# measurement replaces (configs/gates/physics_rows.json, "retired_proxy").
SUPERSEDES: tuple[tuple[str, str, str, int], ...] = (
    # base line 7168: The POWER_PREFLIGHT receipt says AC state, negotiation, supply and power policy m...
    row("joulewise/arm_readiness.py", "_evaluate_rows",
        "readiness_dependency_refused (row t0.power_path)", 1),
    # base line 1976: The system_profiler SPPowerDataType output is not JSON.
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_power",
        "evidence_author_t0_power_preflight_underivable", 3),
    # base line 1984: No connected adapter with a known positive wattage is found.
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_power",
        "evidence_author_t0_power_preflight_underivable", 4),
    # base line 74: First line of pmset -g batt contains 'AC Power'.
    row("joulewise/prewindow.py", "t0_check",
        "BLOCK not on AC power", 1),
    # base line 78: pmset ran.
    row("joulewise/prewindow.py", "t0_check",
        "BLOCK power probe failed", 1),
    # base line 111: First line of pmset -g batt contains 'AC Power'.
    row("scripts/prewindow_check.sh", "check_once",
        "BLOCK not on AC power", 1),
)


def frozen_grammar_rows(path: Path = COVERAGE_MAP) -> tuple[tuple[str, str, str, int], ...]:
    """The coverage map's ``protects`` rows of the frozen BFG module assigned to battery."""

    document = json.loads(Path(path).read_text())
    return tuple(row(entry["key"]["file"], entry["key"]["function"], entry["key"]["code"],
                     entry["key"]["occurrence"])
                 for entry in document["rows"]
                 if entry["key"]["file"] == FROZEN_GRAMMAR_FILE
                 and entry.get("disposition") == "protects" and entry.get("module") == MODULE)


def __getattr__(name: str) -> Any:
    # PEP 562: PROTECTS is built on first use, so importing this module (the arm,
    # the monitor) never depends on reading the coverage map.
    if name == "PROTECTS":
        value = _PROTECTS_WRITTEN + frozen_grammar_rows()
        globals()["PROTECTS"] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
