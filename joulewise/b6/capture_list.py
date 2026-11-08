"""A plain append-only capture list and one-way legacy ledger adapter."""

from __future__ import annotations

import fcntl
import json
import os
import time
from pathlib import Path
from typing import Any, Mapping

from joulewise.b6.registration import decimal_s

SCHEMA = "joulewise.b6_capture_list.v1"
LOCK_TIMEOUT_S = 30.0
FIELDS = ("seq", "session_id", "slot", "attempt_id", "value_s", "disposition",
          "captured_utc", "evidence_path", "evidence_sha256")


def _row(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema", value.get("schema_version")) != SCHEMA:
        raise ValueError("capture list schema is invalid")
    if any(key not in value for key in FIELDS) or type(value["seq"]) is not int:
        raise ValueError("capture list row is incomplete")
    if value["value_s"] is not None and not isinstance(value["value_s"], str):
        raise ValueError("capture list time must be a lexeme")
    if value["value_s"] is not None:
        decimal_s(value["value_s"])
    return value


def append(path: Path | str, row: Mapping) -> str | None:
    """Write one whole line under flock; problems become caller flags."""
    lock_fd = fd = None
    try:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        value = _row({"schema": SCHEMA, **row})
        payload = (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
        lock_fd = os.open(str(target) + ".lock", os.O_CREAT | os.O_RDWR, 0o600)
        deadline = time.monotonic() + LOCK_TIMEOUT_S
        while True:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    return "calibration.capture_list_write_failed: lock_timeout"
                time.sleep(0.01)
        fd = os.open(target, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        view = memoryview(payload)
        while view:
            written = os.write(fd, view)
            if written == 0:
                return "calibration.capture_list_write_failed: short_write"
            view = view[written:]
        os.fsync(fd)
        return None
    except (OSError, ValueError, TypeError, ArithmeticError):
        return "calibration.capture_list_write_failed: write_error"
    finally:
        for opened in (fd, lock_fd):
            if opened is not None:
                try:
                    os.close(opened)
                except OSError:
                    pass


def read(path: Path | str) -> tuple[list[dict], list[str]]:
    rows, problems = [], []
    try:
        raw = Path(path).read_bytes()
    except FileNotFoundError:
        return rows, problems
    except OSError:
        return rows, ["calibration.capture_list_line_unreadable: file"]
    for number, line in enumerate(raw.splitlines(), 1):
        try:
            rows.append(_row(json.loads(line)))
        except (ValueError, TypeError, UnicodeDecodeError, ArithmeticError):
            problems.append(f"calibration.capture_list_line_unreadable: line {number}")
    return rows, problems


def import_custody_ledger(ledger_path: Path | str) -> list[dict]:
    """Project finalized receipts, without pins, chain validation or raw reads.

    Shared with the precheck adapter. Historical finalizations and finalized
    slots of aborted sessions remain observations; reservations are not.
    """
    rows = []
    try:
        raw = Path(ledger_path).read_bytes()
    except FileNotFoundError:
        return rows
    for line in raw.splitlines():
        try:
            receipt = json.loads(line)
            if not isinstance(receipt, Mapping):
                continue
            if receipt.get("event") not in (
                    "finalization", "bracket-session-slot-finalization",
                    "historical-import-v1-finalization"):
                continue
            locator = Path(receipt["custody_locator"])
            artifact = receipt.get("artifact_sha256") or {}
            rows.append({"schema": SCHEMA, "seq": receipt["sequence"],
                         "session_id": receipt.get("session_id"), "slot": receipt.get("slot"),
                         "attempt_id": receipt["attempt_id"],
                         "value_s": receipt.get("exact_bound_lexeme_s"),
                         "disposition": receipt["disposition"],
                         "captured_utc": receipt.get("capture_wall_time_s"),
                         "evidence_path": str(locator / "instrument_evidence.json"),
                         "evidence_sha256": artifact.get("instrument_evidence.json")})
        except (ValueError, TypeError, KeyError, UnicodeDecodeError):
            continue
    return sorted(rows, key=lambda row: row["seq"])
