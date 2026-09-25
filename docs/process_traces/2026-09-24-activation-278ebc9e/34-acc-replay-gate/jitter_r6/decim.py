#!/usr/bin/env python3
"""Diagnostic r6 pairwise decimation and energy-preserving 25G83 jitter replay."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from joulewise import powermetrics_fiducial as detector  # noqa: E402

REGISTRY = ROOT / "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json"
NIGHTS = {
    "n1": Path("/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919"),
    "n2": Path("/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919"),
}
MISS = "no_plateau_interior_intervals"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def intervals(path: Path) -> list[detector.TraceInterval]:
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
        raise ValueError(f"bad GPU trace: {path}")
    return rows


def commands(path: Path) -> dict[str, list[detector.CommandedPulse]]:
    pairs: dict[str, list[detector.CommandedPulse]] = {"warmup": [], "pulse": []}
    pending = {}
    for line in path.read_text().splitlines():
        row = json.loads(line)
        kind = row.get("event_type", "")
        if "_command_" not in kind:
            continue
        name, edge = kind.split("_command_", 1)
        stamp = detector.stamp_from_mapping(row["metadata"]["clock_stamp"])
        if edge == "on":
            pending[name] = stamp
        elif edge == "off":
            start = pending.pop(name)
            pairs[name].append(
                detector.CommandedPulse(
                    start.epoch_s,
                    stamp.epoch_s,
                    detector.clock_stamp_half_width_s(start),
                    detector.clock_stamp_half_width_s(stamp),
                )
            )
    if pending or len(pairs["pulse"]) != 59:
        raise ValueError(f"incomplete r6 commands: {path}")
    return pairs


def pairwise(rows: list[detector.TraceInterval], phase: int) -> list[detector.TraceInterval]:
    out = []
    for i in range(phase, len(rows) - 1, 2):
        a, b = rows[i : i + 2]
        elapsed = b.end_s - a.start_s
        energy = a.power_w * a.duration_s + b.power_w * b.duration_s
        out.append(detector.TraceInterval(a.start_s, b.end_s, energy / elapsed))
    return out


def resample(
    source: list[detector.TraceInterval], template_lengths: list[float]
) -> list[detector.TraceInterval]:
    """Tile source time with template lengths; conserve integral within each tile."""
    out = []
    start = source[0].start_s
    limit = source[-1].end_s
    source_index = 0
    template_index = 0
    while start < limit - 1e-9:
        end = min(start + template_lengths[template_index % len(template_lengths)], limit)
        energy = 0.0
        cursor = start
        while cursor < end - 1e-9:
            while source_index < len(source) and source[source_index].end_s <= cursor + 1e-9:
                source_index += 1
            if source_index == len(source) or source[source_index].start_s > cursor + 1e-6:
                raise ValueError("r6 source trace has a coverage gap")
            piece_end = min(end, source[source_index].end_s)
            energy += source[source_index].power_w * (piece_end - cursor)
            cursor = piece_end
        out.append(detector.TraceInterval(start, end, energy / (end - start)))
        start = end
        template_index += 1
    return out


def geometry_misses(
    rows: list[detector.TraceInterval], pulses: list[detector.CommandedPulse]
) -> list[int]:
    # Same production interior call as the deterministic replay. The high
    # baseline exits at amplitude before projection for every nonempty interior.
    baseline = max(row.power_w for row in rows) + 100.0
    budget = detector._ProjectionWorkBudget(cell_budget=1, wall_budget_s=60.0)
    misses = [
        i
        for i, pulse in enumerate(pulses)
        if MISS in detector._fit_pulse(i, pulse, rows, baseline, 1.0, budget).reasons
    ]
    if budget.evaluated_cell_count:
        raise AssertionError("jitter diagnostic entered projection")
    return misses


def run(r6_root: Path) -> dict:
    registry = json.loads(REGISTRY.read_text())
    templates = []
    for label, archive in NIGHTS.items():
        for slot in range(1, 13):
            capture = archive / "runs" / "instrument_validation" / f"d079-epoch-25g83-derivation-{label}-20260919-d{slot:02d}"
            trace_path = capture / "power_trace.csv"
            evidence = json.loads((capture / "instrument_evidence.json").read_text())
            lengths = [row.duration_s for row in intervals(trace_path)]
            templates.append({
                "capture": f"{label}-d{slot:02d}",
                "fitted": evidence["clock_anchor_resolved"] is True and len(evidence["pulses"]) == 59,
                "lengths": lengths,
                "sha256": digest(trace_path),
            })
    members = []
    for member in registry["derivation_corpus"]["members"]:
        capture = r6_root / member["source_directory"]
        trace_path = capture / "power_trace.csv"
        events_path = capture / "events.jsonl"
        evidence_path = capture / "instrument_evidence.json"
        evidence = json.loads(evidence_path.read_text())
        if digest(evidence_path) != member["instrument_evidence_sha256"]:
            raise ValueError(f"r6 evidence digest mismatch: {member['member_id']}")
        source = intervals(trace_path)
        pairs = commands(events_path)
        anchor = float(evidence.get("clock_anchor", {}).get("effective_clock_anchor_bound_s") or 0)
        decimation = []
        for phase in (0, 1):
            rows = detector.trim_trace_after_pulses(pairwise(source, phase), pairs["warmup"])
            fit = detector.detect_pulses(rows, pairs["pulse"], trace_anchor_bound_s=anchor)
            decimation.append({"phase": phase, "detected": sum(p.detected for p in fit.fits), "b_fiducial_s": fit.b_fiducial_s})
        jitter = []
        for template in templates:
            rows = detector.trim_trace_after_pulses(resample(source, template["lengths"]), pairs["warmup"])
            misses = geometry_misses(rows, pairs["pulse"])
            jitter.append({"template": template["capture"], "misses": misses})
        members.append({
            "member_id": member["member_id"],
            "source_sha256": {name: digest(capture / name) for name in ("power_trace.csv", "events.jsonl", "instrument_evidence.json")},
            "decimation": decimation,
            "jitter": jitter,
        })
    trials = [trial for member in members for trial in member["jitter"]]
    return {
        "schema": "r6-25g83-jitter-diagnostic/v1",
        "method": "r6 frame-mean power integrated onto consecutive 25G83 recorded frame durations, repeated to cover each r6 trace; v3 production _fit_pulse interior test",
        "registry_sha256": digest(REGISTRY),
        "templates": [{k: v for k, v in row.items() if k != "lengths"} for row in templates],
        "members": members,
        "summary": {
            "r6_members": len(members),
            "templates": len(templates),
            "jitter_trials": len(trials),
            "zero_miss_trials": sum(not trial["misses"] for trial in trials),
            "missed_pulses": sum(len(trial["misses"]) for trial in trials),
            "pairwise_59_of_59": sum(row["detected"] == 59 for member in members for row in member["decimation"]),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r6-root", type=Path, required=True, help="allowed local copy containing r6 source_directory paths")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("results.json"))
    args = parser.parse_args()
    result = run(args.r6_root)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("r6 jitter diagnostic:", result["summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
