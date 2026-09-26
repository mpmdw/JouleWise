"""Battery float observations and authenticated derivation-window replay.

The ioreg parser accepts only the exact whole-document grammar of cold ruling
BFG-D-PARSER-ESC-01 §4: byte framing, one line type per physical line, and a
recursive-descent value grammar that must consume each value to its last byte.
Anything outside that allow-list is a ``ProbeError``, never a pass.  All
consumers use this module for the probe and predicate (directive #421).

Grammar freeze (refuter M-2, obligation R2-9): any change to the structural
stage (``_structure`` and ``_recorded_values``) while the Revision-5 epoch is
unissued must, in the same PR, replay every committed Revision-5 verdict with
zero ``compare_verdict`` differences; otherwise it is a registration amendment
that needs an owner ruling.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import time
from typing import Any, Callable, Mapping

IOREG_BATTERY_ARGV = ("/usr/sbin/ioreg", "-r", "-c", "AppleSmartBattery")
PROBE_TIMEOUT_S = 10
SCHEMA = "joulewise.battery_float.v1"
POLICY_ID = "bfg-01"
LIMIT_MA = 200
MAX_UPDATE_AGE_S = 180
_REQUIRED = ("ExternalConnected", "IsCharging", "InstantAmperage", "UpdateTime")
_OPTIONAL = ("Amperage", "Voltage", "Temperature", "FullyCharged", "CurrentCapacity",
             "AppleRawCurrentCapacity", "AppleRawMaxCapacity")
_UINT = re.compile(r"[0-9]{1,20}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_COMMIT = re.compile(r"[0-9a-f]{40}\Z")
_SESSION_ID = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._-]*\Z")
VERDICT_SCHEMA = "joulewise.battery_float_verdict.v1"
VERDICT_DIRECTORY = "configs/calibration/battery_float_verdicts"
LEDGER_HEAD_PIN = "configs/calibration/calibration_ledger_head.json"


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


def _structure(raw: Any) -> dict[str, tuple[bytes, bytes]]:
    """Accept one whole ioreg document (ruling §4) or raise ``ProbeError``.

    Returns every top-level key with its verbatim line and VALUE bytes.  No
    state crosses a physical line except the expected line type (BODY or
    TAIL) and the set of top-level keys; nesting exists only inside one
    value, checked by recursive descent that must consume it to its last
    byte.  Frozen for the Revision-5 epoch (module docstring).
    """
    header = re.compile(
        rb"\+-o AppleSmartBattery  <class AppleSmartBattery, id 0x[0-9a-f]+, registered, "
        rb"matched, active, busy [0-9]+ \([0-9]+ ms\), retain [0-9]+>")
    opening, closing = b"    {", b"    }"
    prop = re.compile(rb' {6}"([A-Za-z0-9_][A-Za-z0-9_.-]*)" = (.+)')
    tail = re.compile(rb" *")
    key = re.compile(rb'"[A-Za-z0-9_][A-Za-z0-9_.-]*"')
    atom = re.compile(rb"Yes|No|[0-9]+")
    data = re.compile(rb"<(?:[0-9a-f]{2})*>")
    max_bytes, max_line, max_depth = 1_048_576, 262_144, 64

    def value(text: bytes, at: int, depth: int, where: str) -> int:
        """Consume one VALUE starting at ``at``; return the cursor after it."""
        head = text[at:at + 1]
        if head == b'"':
            return string(text, at, where)
        if head == b"(" or head == b"{":
            if depth >= max_depth:
                raise ProbeError(f"{where}: depth")
            return container(text, at, depth + 1, where)
        token = (data if head == b"<" else atom).match(text, at)
        if token is None:
            raise ProbeError(f"{where}: token")
        return token.end()

    def string(text: bytes, at: int, where: str) -> int:
        cursor = at + 1
        while cursor < len(text) and text[cursor:cursor + 1] != b'"':
            if text[cursor:cursor + 1] == b"\\":
                if text[cursor + 1:cursor + 2] not in (b'"', b"\\"):
                    raise ProbeError(f"{where}: escape")
                cursor += 1
            cursor += 1
        if cursor >= len(text):
            raise ProbeError(f"{where}: unclosed string")
        return cursor + 1

    def container(text: bytes, at: int, depth: int, where: str) -> int:
        is_dict = text[at:at + 1] == b"{"
        end, name = (b"}", "dict") if is_dict else (b")", "array")
        cursor = at + 1
        members: set[bytes] = set()
        if text[cursor:cursor + 1] == end:
            return cursor + 1
        while True:
            if is_dict:
                member = key.match(text, cursor)
                if member is None:
                    raise ProbeError(f"{where}: nested key")
                if member.group() in members:
                    raise ProbeError(f"{where}: duplicate nested key {member.group().decode()}")
                members.add(member.group())
                cursor = member.end()
                if text[cursor:cursor + 1] != b"=":
                    raise ProbeError(f"{where}: token")
                cursor += 1
                # "K"=, and "K"=} are ioreg's unserialisable members.
                if text[cursor:cursor + 1] not in (b",", b"}"):
                    cursor = value(text, cursor, depth, where)
            else:
                cursor = value(text, cursor, depth, where)
            follow = text[cursor:cursor + 1]
            if follow == end:
                return cursor + 1
            if follow != b",":
                if cursor >= len(text):
                    raise ProbeError(f"{where}: unclosed {name}")
                raise ProbeError(f"{where}: token")
            cursor += 1

    if not isinstance(raw, bytes) or not raw or len(raw) > max_bytes:
        raise ProbeError("framing: type/size")
    if re.search(rb"[^\n\x20-\x7e]", raw):
        raise ProbeError("framing: byte")
    if not raw.endswith(b"\n"):
        raise ProbeError("framing: final LF")
    lines = raw.split(b"\n")[:-1]
    if not header.fullmatch(lines[0]):
        raise ProbeError("header")
    if lines[1:2] != [opening]:
        raise ProbeError("open")
    properties: dict[str, tuple[bytes, bytes]] = {}
    in_body = True
    for number, line in enumerate(lines[2:], start=3):
        where = f"line {number}"
        if not in_body:
            if not tail.fullmatch(line):
                raise ProbeError(f"{where}: tail")
            continue
        if line == closing and properties:
            in_body = False
            continue
        if len(line) > max_line:
            raise ProbeError(f"{where}: length")
        match = prop.fullmatch(line)
        if match is None:
            raise ProbeError(f"{where}: property")
        name, text = match.group(1).decode("ascii"), match.group(2)
        if name in properties:
            raise ProbeError(f"{where}: duplicate key {name}")
        if value(text, 0, 0, where) != len(text):
            raise ProbeError(f"{where}: value suffix")
        properties[name] = (line, text)
    if in_body:
        raise ProbeError("close")
    return properties


def _recorded_values(properties: Mapping[str, tuple[bytes, bytes]]) -> dict[str, str]:
    """Type-check every registered property (ruling §4 and obligation R2-8).

    A required key is present exactly once; ``ExternalConnected``,
    ``IsCharging`` and ``FullyCharged`` are exactly ``Yes``/``No``; every
    registered integer fullmatches ``[0-9]{1,20}`` below 2^64.  A missing
    recorded key stays ``None``; a malformed one is not a pass.  Frozen for
    the Revision-5 epoch (module docstring).
    """
    values = {name: properties[name][1].decode("ascii")
              for name in (*_REQUIRED, *_OPTIONAL) if name in properties}
    for name in _REQUIRED:
        if name not in values:
            raise ProbeError(f"required {name}")
    for name in ("ExternalConnected", "IsCharging", "FullyCharged"):
        if name in values and values[name] not in ("Yes", "No"):
            raise ProbeError(f"boolean {name}")
    for name in ("InstantAmperage", "UpdateTime", "Amperage", "Voltage", "Temperature",
                 "CurrentCapacity", "AppleRawCurrentCapacity", "AppleRawMaxCapacity"):
        if name in values and (not _UINT.fullmatch(values[name]) or int(values[name]) >= 2**64):
            raise ProbeError(f"uint64 {name}")
    return values


def parse(raw: bytes, wall_time_s: float) -> dict[str, Any]:
    """Accept one whole ioreg document, then evaluate the float predicate.

    Structural acceptance (``_structure``) and typing (``_recorded_values``)
    run over the whole document before any predicate; any fault raises
    ``ProbeError``.
    """
    properties = _structure(raw)
    values = _recorded_values(properties)
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
        optional[field] = None if key not in values else _signed(values[key])
    optional["fully_charged"] = None if "FullyCharged" not in values else values["FullyCharged"] == "Yes"
    reasons = []
    if values["ExternalConnected"] != "Yes":
        reasons.append("ExternalConnected is not Yes")
    if values["IsCharging"] != "No":
        reasons.append("IsCharging is not No")
    if abs(current) > LIMIT_MA:
        reasons.append("InstantAmperage exceeds 200 mA")
    return {
        "object_count": 1,
        "property_lines": [properties[key][0].decode("ascii") for key in (*_REQUIRED, *_OPTIONAL)
                           if key in properties],
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
        # Obligation R2-11: only the probe's exact stdout bytes reach the
        # grammar.  Text was decoded by the runner (universal newlines turn
        # CR into LF), so it is refused, never re-encoded.
        if not isinstance(raw_value, bytes):
            raise ProbeError("probe stdout is not bytes")
        raw = raw_value
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
                           preregistration_sha256: str) -> CommittedVerdict:
    """Return the authentic committed harvest verdict, or raise ``NoRecord``.

    Obligations v1.1 §4.3. ``preregistration_sha256`` is the caller's pinned
    registration digest, always required: a record never authenticates
    against no registration.  Consumers call ``authenticate_committed_verdict``.
    """
    # Imported here, not at module scope: night_gate imports this module on
    # every arm and t0 path, and those minimal import surfaces carry no
    # authentication layer.
    from joulewise.authentication_io import ingest_git_authentication_input

    root = Path(repo_root)
    # The caller's digest is validated on its own, so a record that omits the
    # field can never match an absent digest (final delta, Astra R3).
    if not (isinstance(preregistration_sha256, str)
            and re.fullmatch(r"[0-9a-f]{64}", preregistration_sha256)):
        raise NoRecord("identity mismatch: preregistration_sha256")
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
    touching = (_git(root, "log", "--full-history", "--no-merges", "--no-renames", "--format=%H", "--", rel) or b"").decode().split()
    adding = (_git(root, "log", "--full-history", "--no-merges", "--no-renames", "--diff-filter=A", "--format=%H", "--", rel) or b"").decode().split()
    if len(touching) != 1 or adding != touching or not _COMMIT.fullmatch(touching[0]):
        raise NoRecord(f"path history is not a single adding commit "
                       f"({len(touching)} commits, {len(adding)} adding)")
    # --no-merges: an honest harvest commit reaching main through a --no-ff merge is one adding commit; a merge that rewrites the record is caught by the adding-blob check below (BFG-D row-6 M-1).
    if _git(root, "show", f"{touching[0]}:{rel}") != committed:
        raise NoRecord("path history is not a single adding commit (the adding commit's bytes differ from HEAD)")
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
    if record.get("preregistration_sha256") != preregistration_sha256:
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
    # 5. The adding commit is also the pin update that authenticates this
    # exact ledger head. A later pin update cannot retroactively license it.
    from joulewise.calibration_ledger import _head_pin
    pin_commit = _git(root, "show", f"{touching[0]}:{LEDGER_HEAD_PIN}")
    pin_change = _git(root, "diff-tree", "--root", "-r", "--name-only",
                      touching[0], "--", LEDGER_HEAD_PIN)
    try:
        pin = _head_pin(json.loads(pin_commit)) if pin_commit is not None else None
    except (ValueError, TypeError):
        pin = None
    ledger_head = record.get("ledger_head")
    if (not pin_change or not isinstance(ledger_head, dict)
            or pin != (ledger_head.get("sequence"), ledger_head.get("head_digest"))):
        raise NoRecord("verdict not committed with its ledger head pin")
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


@dataclasses.dataclass(frozen=True, slots=True)
class AuthenticatedSlot:
    slot: str
    attempt_id: str
    verdict: str                      # "pass" | "battery_float_confounded" | "battery_float_evidence_missing"
    reasons: tuple[str, ...]
    pre_raw_sha256: str | None
    post_raw_sha256: str | None
    pre_update_age_s: float | None
    post_update_age_s: float | None
    delta_q_mah: int | None
    instrument_evidence_sha256: str | None


@dataclasses.dataclass(frozen=True, slots=True)
class AuthenticatedVerdict:
    session_id: str
    preregistration_sha256: str
    status: str                       # the RECORDED status; it governs every consumer decision
    slots: tuple[AuthenticatedSlot, ...]
    file_sha256: str                  # sha256 of the committed record bytes
    commit: str                       # the single adding commit


REFUSAL_TEXT = {
    "registration_digest_required": "battery-float registration digest missing or invalid for {id}",
    "custody_failure": ("battery-float custody failure for {id}: {detail}; restore the custody bytes "
                        "byte-exact from the harvest archive"),
    "record_unauthenticated": "battery-float harvest verdict missing or uncommitted for {id}: {detail}",
    "verdict_mismatch": ("battery-float harvest verdict for {id} cannot be re-established from raw "
                         "bytes ({detail}); custody failure"),
}


class BatteryVerdictRefusal(RuntimeError):
    """Authentication of a committed harvest verdict failed. Never a verdict; every consumer refuses."""
    def __init__(self, code: str, session_id: str, detail: str) -> None:
        self.code, self.session_id, self.detail = code, session_id, detail
        super().__init__(REFUSAL_TEXT[code].format(id=session_id, detail=detail))


def authenticate_committed_verdict(
    repo_root: Path | str, *, session: Any, preregistration_sha256: str,
) -> AuthenticatedVerdict:
    """The one consumer entry to a window's battery verdict (consumer-drift final texts v1.1 §3.1).

    Replays the custody bytes (``validate_window``), loads the committed
    record (``load_committed_verdict``) and requires the two to agree
    (``compare_verdict``), in obligations v1.1 §4.4 step 3 order.  Any failure
    is a ``BatteryVerdictRefusal``, never a verdict.  The result is built from
    the RECORD, which governs; the recomputation is only its custody check.
    Eligibility (kind, terminality, membership of the epoch) is the caller's.
    """
    session_id = session.session_id
    if not _is_sha256(preregistration_sha256):
        raise BatteryVerdictRefusal("registration_digest_required", session_id, "")
    from joulewise.authentication_io import V2AuthenticationInputError

    try:
        recomputed = validate_window(session)
    except CustodyFailure as failure:
        raise BatteryVerdictRefusal("custody_failure", session_id, failure.detail) from failure
    try:
        record = load_committed_verdict(repo_root, session_id, session=session,
                                        preregistration_sha256=preregistration_sha256)
    except NoRecord as missing:
        raise BatteryVerdictRefusal("record_unauthenticated", session_id, missing.reason) from missing
    except V2AuthenticationInputError as error:
        raise BatteryVerdictRefusal("record_unauthenticated", session_id, str(error)) from error
    difference = compare_verdict(record, recomputed)
    if difference is not None:
        raise BatteryVerdictRefusal("verdict_mismatch", session_id, difference)
    return AuthenticatedVerdict(
        session_id=session_id,
        preregistration_sha256=preregistration_sha256,
        status=record["status"],
        slots=tuple(AuthenticatedSlot(
            slot=entry["slot"], attempt_id=entry.get("attempt_id"), verdict=entry.get("verdict"),
            reasons=tuple(entry.get("reasons") or ()),
            pre_raw_sha256=entry.get("pre_raw_sha256"), post_raw_sha256=entry.get("post_raw_sha256"),
            pre_update_age_s=entry.get("pre_update_age_s"),
            post_update_age_s=entry.get("post_update_age_s"),
            delta_q_mah=entry.get("delta_q_mah"),
            instrument_evidence_sha256=entry.get("instrument_evidence_sha256"),
        ) for entry in record["slots"]),
        file_sha256=record.file_sha256,
        commit=record.commit,
    )
