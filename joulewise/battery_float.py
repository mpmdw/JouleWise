"""Battery float observations and authenticated derivation-window replay.

The ioreg parser deliberately reads only standalone, top-level property lines.
All consumers use this module for the probe and predicate (directive #421).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from typing import Any, Callable, Mapping

IOREG_BATTERY_ARGV = ("/usr/sbin/ioreg", "-r", "-c", "AppleSmartBattery")
SCHEMA = "joulewise.battery_float.v1"
POLICY_ID = "bfg-01"
LIMIT_MA = 200
MAX_UPDATE_AGE_S = 180
_PROPERTY = re.compile(rb'^\s+("[A-Za-z][A-Za-z0-9]*" = .+)$')
_REQUIRED = ("ExternalConnected", "IsCharging", "InstantAmperage", "UpdateTime")
_OPTIONAL = ("Amperage", "Voltage", "Temperature", "FullyCharged", "CurrentCapacity",
             "AppleRawCurrentCapacity", "AppleRawMaxCapacity")
_UINT = re.compile(r"[0-9]+\Z")


class ProbeError(ValueError):
    """A reading cannot establish the predicate."""


def _unsigned(value: str) -> int:
    if not _UINT.fullmatch(value):
        raise ProbeError("malformed unsigned integer")
    number = int(value)
    if number >= 2**64:
        raise ProbeError("integer exceeds 64 bits")
    return number


def _signed(value: str) -> int:
    number = _unsigned(value)
    return number - 2**64 if number >= 2**63 else number


def parse(raw: bytes, wall_time_s: float) -> dict[str, Any]:
    """Parse one complete ioreg object; raise ProbeError on required-data faults."""
    if not isinstance(raw, bytes):
        raise ProbeError("stdout is not bytes")
    lines = raw.splitlines()
    count = sum(line.startswith(b"+-o") for line in lines)
    if count != 1:
        raise ProbeError(f"AppleSmartBattery object count {count}, expected 1")
    properties: dict[str, list[tuple[str, str]]] = {}
    for line in lines:
        match = _PROPERTY.fullmatch(line)
        if match is None:
            continue
        try:
            whole = match.group(1).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ProbeError("property line is not UTF-8") from exc
        key, value = whole.split('" = ', 1)
        properties.setdefault(key[1:], []).append((line.decode("utf-8"), value))
    for key in _REQUIRED:
        if len(properties.get(key, ())) != 1:
            raise ProbeError(f"{key} must occur exactly once")
    values = {key: entries[0][1] for key, entries in properties.items() if len(entries) == 1}
    if values["ExternalConnected"] not in ("Yes", "No") or values["IsCharging"] not in ("Yes", "No"):
        raise ProbeError("malformed battery boolean")
    current = _signed(values["InstantAmperage"])
    update = _unsigned(values["UpdateTime"])
    age = wall_time_s - update
    if age > MAX_UPDATE_AGE_S:
        stale = ProbeError(f"UpdateTime stale: {age:g} s")
        stale.update_age_s = age
        raise stale
    optional: dict[str, Any] = {}
    for key, field in (("Amperage", "amperage_ma"), ("Voltage", "voltage_mv"),
                       ("Temperature", "temperature_raw"), ("CurrentCapacity", "current_capacity_pct"),
                       ("AppleRawCurrentCapacity", "apple_raw_current_capacity_mah"),
                       ("AppleRawMaxCapacity", "apple_raw_max_capacity_mah")):
        try:
            optional[field] = None if key not in values else _signed(values[key])
        except ProbeError:
            optional[field] = None
    optional["fully_charged"] = None if "FullyCharged" not in values else values["FullyCharged"] == "Yes"
    if "FullyCharged" in values and values["FullyCharged"] not in ("Yes", "No"):
        optional["fully_charged"] = None
    reasons = []
    if values["ExternalConnected"] != "Yes":
        reasons.append("ExternalConnected is not Yes")
    if values["IsCharging"] != "No":
        reasons.append("IsCharging is not No")
    if abs(current) > LIMIT_MA:
        reasons.append("InstantAmperage exceeds 200 mA")
    return {
        "object_count": count,
        "property_lines": [entry[0] for key in (*_REQUIRED, *_OPTIONAL) for entry in properties.get(key, ())],
        "external_connected_raw": values["ExternalConnected"],
        "is_charging_raw": values["IsCharging"],
        "instant_amperage_raw": values["InstantAmperage"],
        "update_time_raw": values["UpdateTime"],
        "external_connected": values["ExternalConnected"] == "Yes",
        "is_charging": values["IsCharging"] == "Yes",
        "instant_amperage_ma": current,
        "update_time_s": update,
        "update_age_s": age,
        **optional,
        "passed": not reasons,
        "reasons": reasons,
    }


def observe(*, phase: str, runner: Callable | None = None, wall_time_s: float | None = None,
            monotonic_ns: Callable[[], int] = time.monotonic_ns, raw_path: str | None = None,
            **identity: Any) -> tuple[dict[str, Any], bytes]:
    """Run the bounded probe and return its record plus exact stdout bytes."""
    before = monotonic_ns()
    wall = time.time() if wall_time_s is None else wall_time_s
    raw = b""
    stderr = ""
    exit_code: int | None = None
    timed_out = False
    error: str | None = None
    try:
        result = (subprocess.run(IOREG_BATTERY_ARGV, capture_output=True, timeout=10, check=False)
                  if runner is None else runner(IOREG_BATTERY_ARGV))
        raw_value = result.stdout
        raw = raw_value.encode("utf-8") if isinstance(raw_value, str) else raw_value
        stderr_value = result.stderr
        stderr = stderr_value.decode("utf-8", errors="replace") if isinstance(stderr_value, bytes) else stderr_value
        exit_code = getattr(result, "returncode", getattr(result, "exit_code", None))
        if tuple(result.args if hasattr(result, "args") else result.argv) != IOREG_BATTERY_ARGV:
            raise ProbeError("probe argv mismatch")
        if exit_code != 0:
            raise ProbeError(f"ioreg exit code {exit_code}")
        parsed = parse(raw, wall)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        error = f"ioreg timeout: {exc}"
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        error = f"{type(exc).__name__}: {exc}"
        update_age_s = getattr(exc, "update_age_s", None)
    after = monotonic_ns()
    record: dict[str, Any] = {
        "schema": SCHEMA, "policy_id": POLICY_ID, "limit_ma": LIMIT_MA,
        "max_update_age_s": MAX_UPDATE_AGE_S, "phase": phase,
        "plan_id": identity.get("plan_id"), "session_id": identity.get("session_id"),
        "slot": identity.get("slot"), "attempt_id": identity.get("attempt_id"),
        "wall_time_s": wall, "monotonic_before_ns": before, "monotonic_after_ns": after,
        "argv": list(IOREG_BATTERY_ARGV), "exit_code": exit_code, "timed_out": timed_out,
        "stderr": stderr, "raw_stdout_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_path": raw_path, "object_count": None, "property_lines": [],
        "external_connected_raw": None, "is_charging_raw": None,
        "instant_amperage_raw": None, "update_time_raw": None,
        "external_connected": None, "is_charging": None, "instant_amperage_ma": None,
        "update_time_s": None, "update_age_s": None, "amperage_ma": None,
        "voltage_mv": None, "temperature_raw": None, "fully_charged": None,
        "current_capacity_pct": None, "apple_raw_current_capacity_mah": None,
        "apple_raw_max_capacity_mah": None, "passed": False,
        "reasons": [error] if error else [],
    }
    if error is None:
        record.update(parsed)
    elif 'update_age_s' in locals():
        record["update_age_s"] = update_age_s
    record["probe_error"] = error is not None
    return record, raw


def require_pass(record: Mapping[str, Any]) -> None:
    if record.get("probe_error"):
        raise ProbeError("; ".join(record["reasons"]))
    if not record.get("passed"):
        raise ValueError("; ".join(record["reasons"]))


def validate_window(session: Any) -> dict[str, Any]:
    """Replay every finalized slot from ledger-authenticated primary bytes."""
    slots = []
    for slot, observation in session.finalized_slots.items():
        reasons: list[str] = []
        records = {}
        digests = {}
        verdict = "pass"
        custody = Path(observation.custody_locator)
        try:
            evidence_raw = (custody / "instrument_evidence.json").read_bytes()
            if hashlib.sha256(evidence_raw).hexdigest() != observation.artifact_sha256["instrument_evidence.json"]:
                raise ProbeError("instrument_evidence.json ledger digest mismatch")
            evidence = json.loads(evidence_raw)
            battery = evidence["battery_float"]
            for phase in ("pre", "post"):
                try:
                    stored = battery[phase]
                    expected_path = f"raw/battery_float.{phase}.ioreg"
                    if stored.get("raw_path") != expected_path:
                        raise ProbeError(f"{phase} raw path mismatch")
                    raw = (custody / expected_path).read_bytes()
                    digest = hashlib.sha256(raw).hexdigest()
                    digests[phase] = digest
                    if digest != stored["raw_stdout_sha256"]:
                        raise ProbeError(f"{phase} raw digest mismatch")
                    if stored.get("exit_code") != 0 or stored.get("timed_out"):
                        raise ProbeError(f"{phase} probe failed")
                    records[phase] = parse(raw, float(stored["wall_time_s"]))
                    if not records[phase]["passed"]:
                        verdict = "battery_float_confounded"
                        reasons.extend(f"{phase}: {reason}" for reason in records[phase]["reasons"])
                except (OSError, KeyError, TypeError, ValueError) as exc:
                    if verdict != "battery_float_confounded":
                        verdict = "battery_float_evidence_missing"
                    reasons.append(f"{phase} evidence missing or unauthenticated: {type(exc).__name__}: {exc}")
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            if verdict != "battery_float_confounded":
                verdict = "battery_float_evidence_missing"
            reasons.append(f"evidence missing or unauthenticated: {type(exc).__name__}: {exc}")
        pre_q = records.get("pre", {}).get("apple_raw_current_capacity_mah")
        post_q = records.get("post", {}).get("apple_raw_current_capacity_mah")
        slots.append({"slot": slot, "attempt_id": observation.attempt_id, "verdict": verdict,
                      "reasons": reasons, "pre_raw_sha256": digests.get("pre"),
                      "post_raw_sha256": digests.get("post"),
                      "delta_q_mah": post_q - pre_q if pre_q is not None and post_q is not None else None})
    statuses = {slot["verdict"] for slot in slots}
    status = ("battery_float_confounded" if "battery_float_confounded" in statuses else
              "battery_float_evidence_missing" if "battery_float_evidence_missing" in statuses else "pass")
    return {"status": status, "slots": slots}
