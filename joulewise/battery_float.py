"""Battery float observations and authenticated derivation-window replay.

The ioreg parser deliberately reads only standalone, top-level property lines.
All consumers use this module for the probe and predicate (directive #421).
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import time
from typing import Any, Callable, Mapping

from joulewise.authentication_io import ingest_git_authentication_input

IOREG_BATTERY_ARGV = ("/usr/sbin/ioreg", "-r", "-c", "AppleSmartBattery")
PROBE_TIMEOUT_S = 10
SCHEMA = "joulewise.battery_float.v1"
POLICY_ID = "bfg-01"
LIMIT_MA = 200
MAX_UPDATE_AGE_S = 180
_PROPERTY = re.compile(rb'^\s+("[A-Za-z][A-Za-z0-9]*" = .+)$')
_REQUIRED = ("ExternalConnected", "IsCharging", "InstantAmperage", "UpdateTime")
_OPTIONAL = ("Amperage", "Voltage", "Temperature", "FullyCharged", "CurrentCapacity",
             "AppleRawCurrentCapacity", "AppleRawMaxCapacity")
_UINT = re.compile(r"[0-9]+\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_COMMIT = re.compile(r"[0-9a-f]{40}\Z")
_SESSION_ID = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._-]*\Z")
VERDICT_SCHEMA = "joulewise.battery_float_verdict.v1"
VERDICT_DIRECTORY = "configs/calibration/battery_float_verdicts"


class ProbeError(ValueError):
    """A reading cannot establish the predicate."""


class CustodyFailure(RuntimeError):
    """Bytes whose digest was recorded before finalization are absent or differ.

    Deliberately not a ``ValueError``/``OSError``: no consumer may swallow it
    as ``battery_float_evidence_missing``.  It is never a verdict; every
    consumer refuses, and restoring the bytes is the only cure (A-R5b-1).
    """

    def __init__(self, failures: list[dict[str, Any]]) -> None:
        self.failures = failures
        self.detail = "; ".join(
            f"{item['slot']}/{item['artifact']} expected {item['expected_sha256']} "
            f"observed {item['observed_sha256'] or 'absent'}"
            for item in failures
        )
        super().__init__(f"custody failure: {self.detail}")


class NoRecord(ValueError):
    """No authentic committed harvest verdict exists for the session."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class CommittedVerdict(dict):
    """An authenticated harvest verdict record, plus where it was committed."""

    file_sha256: str
    commit: str


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
    """Run the bounded probe and return its record plus exact stdout bytes.

    Every failure of the probe or the parse is recorded as ``probe_error`` and
    never as a pass; the caller decides the refusal its site owes.
    """
    before = monotonic_ns()
    wall = time.time() if wall_time_s is None else wall_time_s
    raw = b""
    stderr = ""
    exit_code: int | None = None
    timed_out = False
    error: str | None = None
    update_age_s: float | None = None
    try:
        result = (subprocess.run(IOREG_BATTERY_ARGV, capture_output=True,
                                 timeout=PROBE_TIMEOUT_S, check=False)
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
    except Exception as exc:  # any runner or parse failure is a probe error
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
    else:
        record["update_age_s"] = update_age_s
    record["probe_error"] = error is not None
    return record, raw


def require_pass(record: Mapping[str, Any]) -> None:
    if record.get("probe_error"):
        raise ProbeError("; ".join(record["reasons"]))
    if not record.get("passed"):
        raise ValueError("; ".join(record["reasons"]))


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _is_wall_time(value: Any) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def validate_window(session: Any) -> dict[str, Any]:
    """Replay every finalized slot from ledger-authenticated primary bytes.

    Obligations v1.1 §4.1: bytes whose digest was recorded before
    finalization (the evidence file by the ledger row, each raw file by the
    evidence) and that are now absent or different are a custody failure,
    never a verdict; every other fault is instrument state.
    """
    slots = []
    failures: list[dict[str, Any]] = []
    for slot, observation in session.finalized_slots.items():
        reasons: list[str] = []
        records: dict[str, dict[str, Any]] = {}
        digests: dict[str, str] = {}
        ages: dict[str, float | None] = {"pre": None, "post": None}
        confounded = missing = False
        custody = Path(observation.custody_locator)
        expected_evidence = observation.artifact_sha256.get("instrument_evidence.json")

        def custody_failure(artifact: str, expected: str, observed: str | None) -> None:
            failures.append({"slot": slot, "attempt_id": observation.attempt_id,
                             "artifact": artifact, "expected_sha256": expected,
                             "observed_sha256": observed})

        if expected_evidence is None:  # E0
            missing = True
            reasons.append("instrument_evidence.json has no ledger digest")
        else:
            try:  # E1
                evidence_raw = (custody / "instrument_evidence.json").read_bytes()
            except OSError:
                evidence_raw = None
            observed = None if evidence_raw is None else hashlib.sha256(evidence_raw).hexdigest()
            if observed != expected_evidence:
                custody_failure("instrument_evidence.json", expected_evidence, observed)
            else:
                try:  # E2 (whole evidence)
                    evidence = json.loads(evidence_raw)
                except ValueError:
                    evidence = None
                battery = evidence.get("battery_float") if isinstance(evidence, dict) else None
                if not isinstance(battery, dict):
                    missing = True
                    reasons.append("evidence missing: no battery_float record")
                for phase in ("pre", "post") if isinstance(battery, dict) else ():
                    stored = battery.get(phase)
                    expected_path = f"raw/battery_float.{phase}.ioreg"
                    fault = (
                        "phase not recorded" if not isinstance(stored, dict) else
                        "raw path mismatch" if stored.get("raw_path") != expected_path else
                        "raw digest not recorded" if not _is_sha256(stored.get("raw_stdout_sha256")) else
                        "wall time not recorded" if not _is_wall_time(stored.get("wall_time_s")) else
                        None
                    )
                    if fault is not None:  # E2 (phase)
                        missing = True
                        reasons.append(f"{phase} evidence missing: {fault}")
                        continue
                    try:  # E3
                        raw = (custody / expected_path).read_bytes()
                    except OSError:
                        raw = None
                    digest = None if raw is None else hashlib.sha256(raw).hexdigest()
                    if digest != stored["raw_stdout_sha256"]:
                        custody_failure(phase, stored["raw_stdout_sha256"], digest)
                        continue
                    digests[phase] = digest
                    if stored.get("exit_code") != 0 or stored.get("timed_out"):  # E4
                        missing = True
                        reasons.append(f"{phase} evidence missing: probe failed")
                        continue
                    try:  # E5
                        records[phase] = parse(raw, float(stored["wall_time_s"]))
                    except ProbeError as exc:
                        missing = True
                        reasons.append(f"{phase} evidence missing: {exc}")
                        continue
                    ages[phase] = records[phase]["update_age_s"]
                    if not records[phase]["passed"]:  # E6
                        confounded = True
                        reasons.extend(f"{phase}: {reason}" for reason in records[phase]["reasons"])
        verdict = ("battery_float_confounded" if confounded else
                   "battery_float_evidence_missing" if missing else "pass")
        pre_q = records.get("pre", {}).get("apple_raw_current_capacity_mah")
        post_q = records.get("post", {}).get("apple_raw_current_capacity_mah")
        slots.append({"slot": slot, "attempt_id": observation.attempt_id, "verdict": verdict,
                      "reasons": reasons, "pre_raw_sha256": digests.get("pre"),
                      "post_raw_sha256": digests.get("post"),
                      "pre_update_age_s": ages["pre"], "post_update_age_s": ages["post"],
                      "delta_q_mah": post_q - pre_q if pre_q is not None and post_q is not None else None,
                      "instrument_evidence_sha256": expected_evidence})
    if failures:
        raise CustodyFailure(failures)
    statuses = {slot["verdict"] for slot in slots}
    status = ("battery_float_confounded" if "battery_float_confounded" in statuses else
              "battery_float_evidence_missing" if "battery_float_evidence_missing" in statuses else "pass")
    return {"status": status, "slots": slots}


def verdict_relative_path(session_id: str) -> str:
    """The record's path relative to the repository root (obligations §4.2)."""
    if not isinstance(session_id, str) or not _SESSION_ID.fullmatch(session_id):
        raise ValueError(f"session id {session_id!r} cannot name a verdict file")
    return f"{VERDICT_DIRECTORY}/{session_id}.json"


def render_verdict(record: Mapping[str, Any]) -> bytes:
    """The exact bytes a verdict record is written as."""
    return (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def predates_battery_float(session: Any) -> bool:
    """Whether every finalized row's authenticating evidence lacks ``battery_float``.

    Such a session was captured before A-R5b and carries no observation to
    judge.  A row whose evidence does not authenticate against it never
    counts as predating, so custody damage cannot manufacture the exemption.
    """
    rows = list(session.finalized_slots.values())
    if not rows:
        return False
    for observation in rows:
        expected = observation.artifact_sha256.get("instrument_evidence.json")
        try:
            raw = (Path(observation.custody_locator) / "instrument_evidence.json").read_bytes()
            evidence = json.loads(raw)
        except (OSError, ValueError):
            return False
        if (expected is None or hashlib.sha256(raw).hexdigest() != expected
                or not isinstance(evidence, dict) or "battery_float" in evidence):
            return False
    return True


def _session_epoch(session: Any) -> dict[str, Any]:
    epochs = [dict(row.identity_epoch) for row in session.finalized_slots.values()]
    if not epochs or any(epoch != epochs[0] for epoch in epochs):
        raise ValueError("finalized rows disagree on the identity epoch")
    return epochs[0]


def verdict_record(session: Any, *, snapshot: Any, preregistration_sha256: str,
                   tool_commit: str, module_sha256: str, wall_time_s: float) -> dict[str, Any]:
    """Compute the harvest verdict record; raises ``CustodyFailure`` unchanged."""
    window = validate_window(session)
    return {
        "schema": VERDICT_SCHEMA,
        "policy_id": POLICY_ID,
        "session_id": session.session_id,
        "session_kind": session.session_kind,
        "session_state": session.state,
        "identity_epoch": _session_epoch(session),
        "preregistration_sha256": preregistration_sha256,
        "ledger_head": {"sequence": snapshot.head_sequence, "head_digest": snapshot.head_digest},
        "computed_wall_time_s": wall_time_s,
        "tool_commit": tool_commit,
        "battery_float_module_sha256": module_sha256,
        "status": window["status"],
        "slots": [{key: slot[key] for key in (
            "slot", "attempt_id", "verdict", "reasons", "pre_raw_sha256", "post_raw_sha256",
            "pre_update_age_s", "post_update_age_s", "delta_q_mah", "instrument_evidence_sha256",
        )} for slot in window["slots"]],
    }


def _git(repo_root: Path, *argv: str) -> bytes | None:
    try:
        return subprocess.run(("git", "-C", str(repo_root), *argv), check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def load_committed_verdict(repo_root: Path | str, session_id: str, *, session: Any,
                           preregistration_sha256: str | None) -> CommittedVerdict:
    """Return the authentic committed harvest verdict, or raise ``NoRecord``.

    Obligations v1.1 §4.3.  ``preregistration_sha256`` is the caller's pinned
    registration digest; ``None`` is passed only by the count-only and
    diagnostic consumers that hold no pinned digest (report finding).
    """
    root = Path(repo_root)
    try:
        rel = verdict_relative_path(session_id)
    except ValueError:
        raise NoRecord("identity mismatch: session_id") from None
    # 1. The HEAD blob exists, and the working tree holds exactly its bytes.
    committed = _git(root, "show", f"HEAD:{rel}")
    if committed is None:
        raise NoRecord("absent or uncommitted")
    committed = ingest_git_authentication_input(
        rel, committed, grammar="json", label="Git-committed battery-float harvest verdict")
    try:
        working = (root / rel).read_bytes()
    except OSError:
        working = None
    if working != committed:
        raise NoRecord("working tree differs from HEAD")
    # 2. Exactly one commit in HEAD's history touches the path, and it added it.
    touching = (_git(root, "log", "--no-renames", "--format=%H", "--", rel) or b"").decode().split()
    adding = (_git(root, "log", "--no-renames", "--diff-filter=A", "--format=%H", "--", rel)
              or b"").decode().split()
    if len(touching) != 1 or adding != touching or not _COMMIT.fullmatch(touching[0]):
        raise NoRecord(f"path history is not a single adding commit "
                       f"({len(touching)} commits, {len(adding)} adding)")
    # 3. Identity.
    try:
        record = json.loads(committed)
    except ValueError:
        record = None
    if not isinstance(record, dict) or record.get("schema") != VERDICT_SCHEMA:
        raise NoRecord("identity mismatch: schema")
    if record.get("session_id") != session_id:
        raise NoRecord("identity mismatch: session_id")
    rows = list(session.finalized_slots.values())
    if not rows or any(record.get("identity_epoch") != dict(row.identity_epoch) for row in rows):
        raise NoRecord("identity mismatch: identity_epoch")
    if preregistration_sha256 is not None and record.get("preregistration_sha256") != preregistration_sha256:
        raise NoRecord("identity mismatch: preregistration_sha256")
    # 4. Slot binding to the ledger rows.
    slots = record.get("slots")
    recorded = {entry.get("slot"): entry for entry in slots if isinstance(entry, dict)} \
        if isinstance(slots, list) else {}
    if not isinstance(slots, list) or len(recorded) != len(slots):
        raise NoRecord("slot binding mismatch: slots")
    unbound = sorted(set(recorded) ^ set(session.finalized_slots), key=str)
    if unbound:
        raise NoRecord(f"slot binding mismatch: {unbound[0]}")
    for name, observation in session.finalized_slots.items():
        if recorded[name].get("instrument_evidence_sha256") != observation.artifact_sha256.get(
                "instrument_evidence.json"):
            raise NoRecord(f"slot binding mismatch: {name}")
    result = CommittedVerdict(record)
    result.file_sha256 = hashlib.sha256(committed).hexdigest()
    result.commit = touching[0]
    return result


def compare_verdict(record: Mapping[str, Any], recomputed: Mapping[str, Any]) -> str | None:
    """The first difference between a recorded and a recomputed verdict, or None."""
    if record.get("status") != recomputed.get("status"):
        return f"status recorded {record.get('status')} recomputed {recomputed.get('status')}"
    recorded_slots = {entry["slot"]: entry for entry in record.get("slots", [])}
    recomputed_slots = {entry["slot"]: entry for entry in recomputed.get("slots", [])}
    if set(recorded_slots) != set(recomputed_slots):
        return "slot set differs"
    for name in recomputed_slots:
        for field in ("verdict", "pre_raw_sha256", "post_raw_sha256", "instrument_evidence_sha256"):
            left = recorded_slots[name].get(field)
            right = recomputed_slots[name].get(field)
            if left != right:
                return f"{name}.{field} recorded {left} recomputed {right}"
    return None
