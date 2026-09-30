#!/usr/bin/env python3
"""Blind CAP-RULE-25G83-2 replay of retained protocol-v3 captures (R0).

Usage: python3 -B scripts/cap_replay_harness.py SIZING CAPTURE_DIR [...]
       python3 -B scripts/cap_replay_harness.py REPORT CAPTURE_DIR [...]

SIZING changes only the detector's two work limits, temporarily and in this
foreground process. It never accesses a stored or derived bound. REPORT uses
production defaults and compares bounds only to produce an equality boolean;
neither mode serializes evidence, fits, bounds, screens, or energy statistics.
Ratio always means cells / production cap, including in SIZING. A null need
is not zero: only resolved, complete 59-pulse fits supply a sizing need.

For archive-only raw bytes, --raw-powermetrics PATH overrides the raw path for
one capture. No missing/dataless file is downloaded. This tool does not set a
cap, arm a window, or claim that a replay is live hardware validation.
"""

from __future__ import annotations

import argparse
from contextlib import nullcontext
import functools
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import time
from unittest.mock import patch

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from joulewise import powermetrics_fiducial as production
from joulewise.adapters.powermetrics import parse_powermetrics_records

SIZING_CELL_BUDGET = 5_000_000
SIZING_WALL_BUDGET_S = 3_600.0
# macOS SF_DATALESS; inspect metadata before any read that could hydrate iCloud.
SF_DATALESS = 0x40000000


class ReplayInputError(ValueError):
    """A fixed, non-outcome diagnostic safe to print."""


def retained_bytes(path: Path) -> bytes:
    try:
        info = path.stat()
        if getattr(info, "st_flags", 0) & SF_DATALESS:
            raise ReplayInputError("dataless_file_not_read")
        if not path.is_file() or info.st_size == 0:
            raise ReplayInputError("bytes_not_retained")
        return path.read_bytes()
    except OSError:
        raise ReplayInputError("bytes_not_retained") from None


def _evidence_inputs(raw: bytes, mode: str) -> dict:
    # Select top-level inputs before decoding values. In SIZING even the
    # stored bound is skipped as opaque JSON text, along with every screen,
    # pulse statistic and energy value. REPORT admits only the scalar needed
    # for the explicitly authorized equality boolean.
    text = raw.decode("utf-8")
    decoder = json.JSONDecoder()
    allowed = {"protocol_id", "clock_anchor", "artifact_sha256"}
    if mode == "REPORT":
        allowed.add("b_fiducial_s")
    result = {}
    cursor = 0

    def whitespace(index):
        while index < len(text) and text[index].isspace():
            index += 1
        return index

    cursor = whitespace(cursor)
    if text[cursor:cursor + 1] != "{":
        raise ReplayInputError("malformed_evidence")
    cursor = whitespace(cursor + 1)
    while text[cursor:cursor + 1] != "}":
        key, cursor = decoder.raw_decode(text, cursor)
        cursor = whitespace(cursor)
        if not isinstance(key, str) or text[cursor:cursor + 1] != ":":
            raise ReplayInputError("malformed_evidence")
        start = cursor = whitespace(cursor + 1)
        depth, quoted, escaped = 0, False, False
        while cursor < len(text):
            char = text[cursor]
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char in "[{":
                depth += 1
            elif char in "]}":
                if depth == 0:
                    break
                depth -= 1
            elif char == "," and depth == 0:
                break
            cursor += 1
        if cursor == start or depth or quoted:
            raise ReplayInputError("malformed_evidence")
        if key in allowed:
            if key in result:
                raise ReplayInputError("malformed_evidence")
            result[key] = json.loads(text[start:cursor])
        if text[cursor:cursor + 1] == ",":
            cursor = whitespace(cursor + 1)
            if text[cursor:cursor + 1] == "}":
                raise ReplayInputError("malformed_evidence")
        elif text[cursor:cursor + 1] != "}":
            raise ReplayInputError("malformed_evidence")
    if whitespace(cursor + 1) != len(text):
        raise ReplayInputError("malformed_evidence")
    return result


def _stored_reproduced(detection, evidence: dict) -> bool:
    stored = evidence.get("b_fiducial_s")
    return (
        not isinstance(stored, bool)
        and isinstance(stored, (int, float))
        and math.isfinite(stored)
        and detection.b_fiducial_s is not None
        and detection.b_fiducial_s == stored
    )


def replay_capture(capture: Path, mode: str, *, raw_path: Path | None = None) -> dict:
    """Return only blind work/cadence information, plus REPORT's boolean."""
    if mode not in {"SIZING", "REPORT"}:
        raise ValueError("mode must be SIZING or REPORT")
    started = time.monotonic()
    result = {
        "capture": str(capture), "mode": mode, "cells": None,
        "need": None, "median_frame_ms": None, "ratio": None,
        "disposition": "not_replayed", "trigger": None,
        "reason": None, "replay_failed": False,
    }
    if mode == "REPORT":
        result["stored B reproduced"] = False
    try:
        evidence = _evidence_inputs(
            retained_bytes(capture / "instrument_evidence.json"), mode
        )
        if evidence.get("protocol_id") != production.PROTOCOL_ID:
            raise ReplayInputError("protocol_v3_required")
        raw = retained_bytes(raw_path or capture / "raw/powermetrics.plist")
        events = retained_bytes(capture / "events.jsonl")
        expected = evidence.get("artifact_sha256")
        if not isinstance(expected, dict):
            raise ReplayInputError("artifact_hashes_missing")
        for name, data in (("raw/powermetrics.plist", raw), ("events.jsonl", events)):
            if expected.get(name) != hashlib.sha256(data).hexdigest():
                raise ReplayInputError("artifact_hash_mismatch")
        records = parse_powermetrics_records(raw)
        if not records:
            raise ReplayInputError("native_frames_missing")
        result["median_frame_ms"] = statistics.median(
            record.elapsed_ns / 1_000_000.0 for record in records
        )
        # rederive_detection_from_artifacts has no limit arguments. Rebind its
        # detector call to the very same production function with only these
        # two explicit keywords. Never change module constants or code bytes.
        context = nullcontext()
        if mode == "SIZING":
            context = patch.object(
                production, "detect_pulses",
                functools.partial(
                    production.detect_pulses,
                    projection_cell_budget=SIZING_CELL_BUDGET,
                    projection_wall_budget_s=SIZING_WALL_BUDGET_S,
                ),
            )
        with context:
            detection = production.rederive_detection_from_artifacts(
                raw, events, evidence.get("clock_anchor"),
                protocol_id=production.PROTOCOL_ID,
            )
        cells = detection.projection_evaluated_cell_count
        trigger = detection.projection_budget_trigger
        complete = (
            len(detection.fits) == production.PULSE_COUNT
            and detection.all_pulses_detected
            and all(fit.detected for fit in detection.fits)
        )
        result.update(
            cells=cells,
            ratio=cells / production.DETECTION_PROJECTION_CELL_BUDGET,
            disposition=(detection.projection_disposition or
                         ("invalid" if detection.reasons else "valid")),
            trigger=trigger,
            reason=("pulse_detection_incomplete" if not complete and not trigger else None),
        )
        # A deadline stop is failed replay evidence, never a capture finding
        # (R8(c)). Sizing hitting either raised limit refuses the rule (R2(e)).
        result["replay_failed"] = trigger == "wall_deadline"
        if mode == "SIZING" and (
            cells >= SIZING_CELL_BUDGET or trigger is not None
            or time.monotonic() - started >= SIZING_WALL_BUDGET_S
        ):
            result["rule_refused"] = True
        if (mode == "SIZING" and complete and trigger is None
                and not result.get("rule_refused")):
            result["need"] = cells
        if mode == "REPORT":
            result["stored B reproduced"] = _stored_reproduced(detection, evidence)
    except ReplayInputError as exc:
        result.update(reason=str(exc), replay_failed=True)
    except ValueError as exc:
        # Production messages are not serialized: a future exception could
        # include an outcome. Recognize only its fixed alignment refusal.
        if str(exc) == "calibration trace anchor is unresolved":
            result.update(cells=0, ratio=0.0, disposition="clock_anchor_unresolved",
                          reason="clock_anchor_unresolved")
        else:
            result.update(reason="invalid_replay_inputs", replay_failed=True)
    except (KeyError, TypeError, OverflowError):
        result.update(reason="invalid_replay_inputs", replay_failed=True)
    result["elapsed_s"] = time.monotonic() - started
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("SIZING", "REPORT"))
    parser.add_argument("captures", nargs="+", type=Path)
    parser.add_argument("--raw-powermetrics", type=Path)
    args = parser.parse_args(argv)
    if args.raw_powermetrics is not None and len(args.captures) != 1:
        parser.error("--raw-powermetrics requires exactly one capture")
    failed = False
    for capture in args.captures:
        result = replay_capture(capture, args.mode, raw_path=args.raw_powermetrics)
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        failed |= result["replay_failed"] or result.get("rule_refused", False)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
