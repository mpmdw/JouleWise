#!/usr/bin/env python3
"""Pin-free R5(n) native-frame report from raw powermetrics plist streams."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import plistlib
import statistics
from typing import Any

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


def report_window(label: str, window: Path) -> dict[str, Any]:
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
    return {
        "window": label, "captures": captures,
        "median_native_frame_ms": statistics.median(all_lengths),
        "max_native_frame_ms": max(all_lengths),
        "median_of_capture_medians_ms": median_of_medians,
        "r5_n_verdict": "STOP" if median_of_medians > STOP_THRESHOLD_MS else "CONTINUE",
        "r5_n_threshold_ms": STOP_THRESHOLD_MS,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", action="append", required=True, metavar="LABEL=PATH")
    args = parser.parse_args(argv)
    reports = []
    try:
        for item in args.window:
            label, separator, path = item.partition("=")
            if not separator or not label or not path:
                raise ValueError("--window requires LABEL=PATH")
            reports.append(report_window(label, Path(path)))
    except (OSError, ValueError, plistlib.InvalidFileException) as error:
        parser.error(str(error))
    print(json.dumps({"schema": "joulewise.calibration_cadence_report.v1", "windows": reports}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
