#!/usr/bin/env python3
"""Pin-free R5(n) native-frame report from raw powermetrics plist streams."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import plistlib
import statistics
from typing import Any

from joulewise import battery_float
from joulewise.calibration_ledger import load_calibration_ledger_snapshot

STOP_THRESHOLD_MS = 150.0


def native_intervals_ms(raw: bytes) -> list[float]:
    """Read NUL-separated records and drop the first, unsteady sample."""
    parts = [part for part in raw.split(b"\x00") if part.strip()]
    if len(parts) < 2:
        raise ValueError("at least two plist records are required")
    lengths: list[float] = []
    for index, part in enumerate(parts):
        record = plistlib.loads(part)
        if not isinstance(record, dict):
            raise ValueError(f"record {index} is not a plist dictionary")
        elapsed = record.get("elapsed_ns")
        if not isinstance(elapsed, int) or isinstance(elapsed, bool) or elapsed <= 0:
            raise ValueError(f"record {index} has invalid elapsed_ns")
        if index:
            lengths.append(elapsed / 1_000_000)
    return lengths


def capture_paths(window: Path) -> list[Path]:
    if window.is_file():
        return [window]
    paths = sorted(window.glob("*/raw/powermetrics.plist"))
    if not paths:
        paths = sorted(window.glob("**/raw/powermetrics.plist"))
    if not paths:
        raise ValueError(f"{window}: no raw/powermetrics.plist captures")
    return paths


def report_window(label: str, window: Path, *, ledger: Path, session_id: str,
                  head_pin: Path | None = None) -> dict[str, Any]:
    root = ledger.resolve().parent.parent
    pin = head_pin or root / "configs/calibration/calibration_ledger_head.json"
    snapshot = load_calibration_ledger_snapshot(
        ledger, pin, require_committed_pin=True, verify_custody=False,
        mode="read_replay", repo_root=root,
    )
    if snapshot.refusal_reasons:
        raise ValueError("ledger: " + ", ".join(snapshot.refusal_reasons))
    session = snapshot.bracket_session_by_id.get(session_id)
    if session is None:
        raise ValueError(f"session {session_id} is not in the ledger")
    if session.state not in {"finalized", "aborted"}:
        raise ValueError(f"session {session_id} is not terminal")
    # Obligations v1.1 §4.5: the committed harvest verdict governs; the
    # recomputation from raw bytes is only its custody check.
    try:
        recomputed = battery_float.validate_window(session)
    except battery_float.CustodyFailure as failure:
        raise ValueError(f"battery-float custody failure: {failure.detail}") from failure
    try:
        record = battery_float.load_committed_verdict(
            root, session_id, session=session, preregistration_sha256=None,
        )
    except battery_float.NoRecord as missing:
        raise ValueError(
            f"battery-float harvest verdict missing or uncommitted: {missing.reason}"
        ) from missing
    difference = battery_float.compare_verdict(record, recomputed)
    if difference is not None:
        raise ValueError(f"battery-float harvest verdict cannot be re-established: {difference}")
    battery_verdict = record["status"]
    captures = []
    all_lengths: list[float] = []
    for path in capture_paths(window):
        lengths = native_intervals_ms(path.read_bytes())
        all_lengths.extend(lengths)
        captures.append({
            "path": str(path), "interval_count": len(lengths),
            "median_native_frame_ms": statistics.median(lengths),
            "max_native_frame_ms": max(lengths),
        })
    median_of_medians = statistics.median(row["median_native_frame_ms"] for row in captures)
    result = {
        "window": label, "captures": captures,
        "median_native_frame_ms": statistics.median(all_lengths),
        "max_native_frame_ms": max(all_lengths),
        "median_of_capture_medians_ms": median_of_medians,
        "r5_n_verdict": "STOP" if median_of_medians > STOP_THRESHOLD_MS else "CONTINUE",
        "r5_n_threshold_ms": STOP_THRESHOLD_MS,
    }
    if battery_verdict != "pass":
        result["diagnostic_only"] = battery_verdict
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", action="append", required=True, metavar="LABEL=PATH")
    parser.add_argument("--calibration-ledger", type=Path, required=True)
    parser.add_argument("--head-pin", type=Path)
    parser.add_argument("--session", action="append", required=True, metavar="LABEL=SESSION_ID")
    args = parser.parse_args(argv)
    reports = []
    try:
        windows = {}
        for item in args.window:
            label, separator, path = item.partition("=")
            if not separator or not label or not path:
                raise ValueError("--window requires LABEL=PATH")
            if label in windows:
                raise ValueError(f"duplicate --window label {label}")
            windows[label] = Path(path)
        sessions = {}
        for item in args.session:
            label, separator, session_id = item.partition("=")
            if not separator or not label or not session_id:
                raise ValueError("--session requires LABEL=SESSION_ID")
            if label in sessions:
                raise ValueError(f"duplicate --session label {label}")
            sessions[label] = session_id
        if windows.keys() != sessions.keys():
            raise ValueError("--window and --session labels must match exactly")
        for label, path in windows.items():
            reports.append(report_window(
                label, path, ledger=args.calibration_ledger,
                session_id=sessions[label], head_pin=args.head_pin,
            ))
    except (OSError, ValueError, plistlib.InvalidFileException) as error:
        parser.error(str(error))
    print(json.dumps({"schema": "joulewise.calibration_cadence_report.v1", "windows": reports}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
