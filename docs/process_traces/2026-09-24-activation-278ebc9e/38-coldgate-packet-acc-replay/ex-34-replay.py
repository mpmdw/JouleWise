#!/usr/bin/env python3
"""R-ACC-1(b) desk replay of the production detector's interior test."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from joulewise import powermetrics_fiducial as detector  # noqa: E402

NIGHTS = {
    "n1": Path("/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919"),
    "n2": Path("/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919"),
}
MISS = "no_plateau_interior_intervals"
PULSES = 59


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_intervals(path: Path) -> list[detector.TraceInterval]:
    with path.open(newline="") as stream:
        rows = [
            detector.TraceInterval(
                float(row["interval_start_s"]),
                float(row["interval_end_s"]),
                float(row["power_w"]),
            )
            for row in csv.DictReader(stream)
            if row["rail"] == detector.PRIMARY_RAIL
        ]
    if not rows or any(row.end_s <= row.start_s for row in rows):
        raise ValueError(f"bad or empty GPU interval trace: {path}")
    return rows


def load_pulses(path: Path) -> list[detector.CommandedPulse]:
    stamps: dict[str, list[float]] = {"pulse_command_on": [], "pulse_command_off": []}
    for line in path.read_text().splitlines():
        event = json.loads(line)
        if event["event_type"] in stamps:
            stamps[event["event_type"]].append(
                float(event["metadata"]["clock_stamp"]["epoch_s"])
            )
    ons, offs = stamps.values()
    if len(ons) != PULSES or len(offs) != PULSES:
        raise ValueError(f"expected {PULSES} commanded pulse pairs: {path}")
    pulses = [detector.CommandedPulse(on, off) for on, off in zip(ons, offs)]
    if any(p.off_s <= p.on_s for p in pulses):
        raise ValueError(f"nonpositive commanded pulse: {path}")
    return pulses


def geometry_misses(
    intervals: list[detector.TraceInterval], pulses: list[detector.CommandedPulse]
) -> list[int]:
    # _fit_pulse executes the exact production interior filter before amplitude
    # and projection. An intentionally high baseline makes every nonempty
    # interior return at the amplitude gate, avoiding irrelevant heavy fitting.
    # Only the presence of the interior reason is used here.
    baseline = max(row.power_w for row in intervals) + 100.0
    budget = detector._ProjectionWorkBudget(cell_budget=1, wall_budget_s=60.0)
    misses = []
    for index, pulse in enumerate(pulses):
        fit = detector._fit_pulse(index, pulse, intervals, baseline, 1.0, budget)
        if MISS in fit.reasons:
            misses.append(index)
    if budget.evaluated_cell_count:
        raise AssertionError("geometry replay unexpectedly entered projection")
    return misses


def capture_record(label: str, archive: Path, slot: int) -> dict:
    capture = archive / "runs" / "instrument_validation" / f"d079-epoch-25g83-derivation-{label}-20260919-d{slot:02d}"
    trace_path = capture / "power_trace.csv"
    events_path = capture / "events.jsonl"
    evidence_path = capture / "instrument_evidence.json"
    intervals = load_intervals(trace_path)
    pulses = load_pulses(events_path)
    evidence = json.loads(evidence_path.read_text())
    if evidence["protocol_id"] != detector.PROTOCOL_ID:
        raise ValueError(f"unexpected recorded protocol: {capture}")
    recorded = [p["pulse_index"] for p in evidence["pulses"] if MISS in p["reasons"]]
    if len(evidence["pulses"]) not in (0, PULSES):
        raise ValueError(f"partial recorded fit set: {capture}")
    v3 = geometry_misses(intervals, pulses)
    # Counterfactual v4 keeps each archived command-on phase and extends its
    # observed on/off duration by exactly 1 s. The archive contains v3 frames;
    # their timing is the object of this geometry-only replay.
    v4 = geometry_misses(
        intervals,
        [detector.CommandedPulse(p.on_s, p.off_s + 1.0) for p in pulses],
    )
    return {
        "capture": f"{label}-d{slot:02d}",
        "archive": str(capture),
        "source_sha256": {
            "power_trace.csv": sha256(trace_path),
            "events.jsonl": sha256(events_path),
            "instrument_evidence.json": sha256(evidence_path),
        },
        "interval_count": len(intervals),
        "commanded_pulses": len(pulses),
        "recorded_fit_count": len(evidence["pulses"]),
        "recorded_capture_reasons": evidence["reasons"],
        "recorded_misses": recorded,
        "v3_replay_misses": v3,
        "v4_replay_misses": v4,
        "v3_exact_match": recorded == v3,
    }


def run() -> dict:
    captures = [
        capture_record(label, archive, slot)
        for label, archive in NIGHTS.items()
        for slot in range(1, 13)
    ]
    if len(captures) != 24 or sum(c["commanded_pulses"] for c in captures) != 24 * PULSES:
        raise AssertionError("archive population is not 24 x 59")
    return {
        "schema": "acceptance-25g83-r-acc-1b-replay/v1",
        "rule": "production _fit_pulse interior filter, inset 0.25 s",
        "v4_counterfactual": "recorded command-on and observed duration plus 1.0 s",
        "captures": captures,
        "summary": {
            "capture_count": 24,
            "pulse_count": 24 * PULSES,
            "recorded_miss_count": sum(len(c["recorded_misses"]) for c in captures),
            "v3_replay_miss_count": sum(len(c["v3_replay_misses"]) for c in captures),
            "v4_replay_miss_count": sum(len(c["v4_replay_misses"]) for c in captures),
            "v3_exact_capture_count": sum(c["v3_exact_match"] for c in captures),
            "verdict": "PASS" if all(c["v3_exact_match"] and not c["v4_replay_misses"] for c in captures) else "FAIL",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("results.json"))
    args = parser.parse_args()
    result = run()
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for c in result["captures"]:
        print(f"{c['capture']:7} recorded={c['recorded_misses']} v3={c['v3_replay_misses']} v4={c['v4_replay_misses']}")
    print(f"R-ACC-1(b): {result['summary']['verdict']}")
    return 0 if result["summary"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
