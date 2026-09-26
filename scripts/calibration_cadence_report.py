#!/usr/bin/env python3
"""Pin-free R5(n) native-frame report from raw powermetrics plist streams."""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
from pathlib import Path
import plistlib
import statistics
import sys
from typing import Any

sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import battery_float
from joulewise.calibration_ledger import SESSION_KIND_DERIVATION, load_calibration_ledger_snapshot

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
    if any(character in str(window) for character in "*?["):
        roots = [Path(path) for path in glob.glob(str(window))]
        paths = sorted({capture for root in roots for capture in capture_paths(root)})
        if not paths:
            raise ValueError(f"{window}: no raw/powermetrics.plist captures")
        return paths
    if window.is_file():
        return [window.resolve()]
    paths = sorted(path.resolve() for path in window.rglob("powermetrics.plist")
                   if path.parent.name == "raw")
    if not paths:
        raise ValueError(f"{window}: no raw/powermetrics.plist captures")
    return paths


def report_window(label: str, window: Path, *, ledger: Path, session_id: str,
                  head_pin: Path | None = None,
                  preregistration_sha256: str | None = None) -> dict[str, Any]:
    if preregistration_sha256 is None:
        raise ValueError("--preregistration-sha256 is required")
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
    if session.session_kind != SESSION_KIND_DERIVATION:
        raise ValueError(f"session {session_id} is kind {session.session_kind}, not derivation")
    # Obligations v1.1 §4.5: the committed harvest verdict governs; the
    # recomputation from raw bytes is only its custody check.
    try:
        verdict = battery_float.authenticate_committed_verdict(
            root, session=session, preregistration_sha256=preregistration_sha256)
    except battery_float.BatteryVerdictRefusal as refusal:
        raise ValueError(str(refusal)) from refusal
    battery_verdict = verdict.status
    derived: dict[Path, str] = {}
    for observation in session.finalized_slots.values():
        path = (Path(observation.custody_locator) / "raw/powermetrics.plist").resolve()
        digest = observation.artifact_sha256.get("raw/powermetrics.plist")
        if not isinstance(digest, str) or len(digest) != 64 or path in derived:
            raise ValueError(f"session {session_id}: capture inventory is incomplete or duplicated")
        derived[path] = digest
    supplied = set(capture_paths(window))
    if supplied != set(derived):
        raise ValueError(f"session {session_id}: --window capture paths disagree with ledger inventory")
    captures = []
    all_lengths: list[float] = []
    for path, digest in sorted(derived.items()):
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError(f"session {session_id}: capture digest disagrees with ledger for {path}")
        lengths = native_intervals_ms(raw)
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
    parser.add_argument("--preregistration-sha256", required=True)
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
                preregistration_sha256=args.preregistration_sha256,
            ))
    except (OSError, ValueError, plistlib.InvalidFileException) as error:
        parser.error(str(error))
    print(json.dumps({"schema": "joulewise.calibration_cadence_report.v1", "windows": reports}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
