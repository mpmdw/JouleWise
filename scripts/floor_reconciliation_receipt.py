#!/usr/bin/env python3
"""Reconcile the two retained-corpus WO-005 powermetrics reconstructions.

The retained corpus is read only. The sole write is the requested receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.adapters.powermetrics import parse_powermetrics_records
from joulewise.bundle_read import BundleReader, Window

COUNTER_TOLERANCE_J = 1e-5
QWEN_R1 = "example-mac-mlx-qwen35-122b-512t__r1"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _anchored_records(bundle: Path, metadata: dict[str, Any]) -> list[Any]:
    raw = (bundle / "raw" / "powermetrics.plist").read_bytes()
    device = metadata.get("device")
    if isinstance(device, dict) and isinstance(
        device.get("plist_anchor_offset_s"), int | float
    ):
        native = parse_powermetrics_records(raw)
        first_plist_s = native[0].metadata["plist_first_timestamp_s"]
        anchor_s = first_plist_s - float(device["plist_anchor_offset_s"])
        return parse_powermetrics_records(raw, timestamp_anchor_s=anchor_s)
    evidence = metadata.get("uncertainty_evidence")
    anchor = evidence.get("clock_anchor") if isinstance(evidence, dict) else None
    if isinstance(anchor, dict) and isinstance(
        anchor.get("first_sample_end_point_epoch_s"), int | float
    ):
        return parse_powermetrics_records(
            raw,
            first_record_endpoint_s=float(anchor["first_sample_end_point_epoch_s"]),
        )
    raise ValueError(f"{bundle.name}: no recognized powermetrics anchor evidence")


def _stage_window(reader: BundleReader) -> Window:
    starts = [
        float(event["timestamp_s"])
        for event in reader.events()
        if event.get("event_type") == "stage_started"
        and event.get("phase") == "measured_run"
    ]
    ends = [
        float(event["timestamp_s"])
        for event in reader.events()
        if event.get("event_type") == "stage_completed"
        and event.get("phase") == "measured_run"
    ]
    if len(starts) != 1 or len(ends) != 1:
        raise ValueError(f"{reader.path.name}: measured_run stage envelope is ambiguous")
    return Window(starts[0], ends[0])


def _overlap_totals(records: list[Any], window: Window) -> tuple[float, float]:
    power_terms: list[float] = []
    counter_terms: list[float] = []
    for record in records:
        duration_s = record.elapsed_ns / 1_000_000_000.0
        start_s = record.timestamp_s - duration_s
        overlap_s = max(
            0.0,
            min(window.end_s, record.timestamp_s) - max(window.start_s, start_s),
        )
        if overlap_s == 0.0:
            continue
        power_terms.append(record.combined_power_w * overlap_s)
        counter_j = sum(record.rail_energy_mj.values()) / 1000.0
        counter_terms.append(counter_j * overlap_s / duration_s)
    return math.fsum(power_terms), math.fsum(counter_terms)


def _pct(legacy_j: float, reference_j: float) -> float:
    return (legacy_j - reference_j) / reference_j * 100.0


def _bundle_row(bundle: Path) -> dict[str, Any]:
    reader = BundleReader(bundle)
    metadata = reader.metadata()
    summary = _json(bundle / "summary_metrics.json")
    records = _anchored_records(bundle, metadata)
    measured = reader.measured_window()
    if measured is None:
        raise ValueError(f"{bundle.name}: no canonical sampling window")
    stage = _stage_window(reader)
    canonical_power_j, canonical_counter_j = _overlap_totals(records, measured)
    stage_power_j, stage_counter_j = _overlap_totals(records, stage)
    legacy_gross_j = float(summary["gross_energy_j"])

    per_record_deltas_j = [
        abs(
            record.combined_power_w * record.elapsed_ns / 1_000_000_000.0
            - sum(record.rail_energy_mj.values()) / 1000.0
        )
        for record in records
    ]
    raw_idle = (bundle / "raw" / "powermetrics_idle.plist").read_bytes()
    idle_records = parse_powermetrics_records(raw_idle)
    idle_powers = [record.combined_power_w for record in idle_records]
    idle_durations = [record.elapsed_ns / 1_000_000_000.0 for record in idle_records]
    idle_duration_s = math.fsum(idle_durations)
    idle_arithmetic_w = math.fsum(idle_powers) / len(idle_powers)
    idle_weighted_w = math.fsum(
        power_w * duration_s
        for power_w, duration_s in zip(idle_powers, idle_durations, strict=True)
    ) / idle_duration_s
    legacy_idle_subtracted_j = summary.get("idle_subtracted_energy_j")
    corrected_idle_subtracted_j = (
        canonical_power_j - idle_weighted_w * measured.duration_s
    )
    raw_workload = (bundle / "raw" / "powermetrics.plist").read_bytes()
    return {
        "bundle": bundle.name,
        "raw_sha256": {
            "powermetrics.plist": _sha256(raw_workload),
            "powermetrics_idle.plist": _sha256(raw_idle),
        },
        "record_count": len(records),
        "canonical_sampling_window": {
            "start_s": measured.start_s,
            "end_s": measured.end_s,
            "duration_s": measured.duration_s,
        },
        "noncanonical_stage_envelope": {
            "start_s": stage.start_s,
            "end_s": stage.end_s,
            "duration_s": stage.duration_s,
        },
        "legacy_trapezoid_gross_j": legacy_gross_j,
        "authoritative_support_overlap_power_j": canonical_power_j,
        "canonical_support_overlap_counter_j": canonical_counter_j,
        "legacy_minus_authoritative_j": legacy_gross_j - canonical_power_j,
        "legacy_minus_authoritative_pct": _pct(legacy_gross_j, canonical_power_j),
        "stage_envelope_support_overlap_power_j": stage_power_j,
        "stage_envelope_support_overlap_counter_j": stage_counter_j,
        "legacy_minus_stage_envelope_pct": _pct(legacy_gross_j, stage_power_j),
        "counter_consistency": {
            "tolerance_j": COUNTER_TOLERANCE_J,
            "max_per_record_abs_delta_j": max(per_record_deltas_j),
            "all_records_within_tolerance": max(per_record_deltas_j)
            <= COUNTER_TOLERANCE_J,
        },
        "idle": {
            "record_count": len(idle_records),
            "arithmetic_mean_w": idle_arithmetic_w,
            "duration_weighted_mean_w": idle_weighted_w,
            "arithmetic_minus_weighted_w": idle_arithmetic_w - idle_weighted_w,
            "legacy_idle_subtracted_j": legacy_idle_subtracted_j,
            "corrected_idle_subtracted_j": corrected_idle_subtracted_j,
            "legacy_minus_corrected_idle_subtracted_j": (
                float(legacy_idle_subtracted_j) - corrected_idle_subtracted_j
                if isinstance(legacy_idle_subtracted_j, int | float)
                else None
            ),
        },
    }


def build_receipt(runs_root: Path) -> dict[str, Any]:
    bundles = sorted(
        path
        for path in runs_root.iterdir()
        if path.is_dir() and (path / "raw" / "powermetrics.plist").is_file()
    )
    rows = [_bundle_row(bundle) for bundle in bundles]
    qwen = next((row for row in rows if row["bundle"] == QWEN_R1), None)
    if qwen is None:
        raise ValueError(f"retained corpus is missing {QWEN_R1}")
    return {
        "schema": "joulewise.wo005_reconciliation.v1",
        "work_order": "WO-005",
        "corpus": {"logical_root": "runs", "bundle_count": len(rows)},
        "frozen_semantics": {
            "window": "sampling_started_to_sampling_stopped",
            "record_support": "[endpoint-elapsed_ns/1e9, endpoint)",
            "partial_edges": "power_w_times_positive_overlap_duration",
            "whole_interval_assignment": False,
            "endpoint_interpolation": False,
            "counter_tolerance_j_per_record": COUNTER_TOLERANCE_J,
        },
        "authoritative_reference": {
            "name": "support_overlap_power_times_duration_over_sampling_boundaries",
            "reason": (
                "It is the frozen reducer estimand, uses the canonical D-026 sampling "
                "boundaries, and is independently counter-consistent."
            ),
        },
        "t07_reconciliation": {
            "scanner_reconstruction_pct": qwen["legacy_minus_authoritative_pct"],
            "verifier_reconstruction_pct": qwen[
                "legacy_minus_stage_envelope_pct"
            ],
            "resolution": (
                "The scanner used the canonical sampling_started/sampling_stopped "
                "window (-0.498%). The approximately -0.93% verifier result used the "
                "wider stage_started/stage_completed measured_run envelope, which "
                "includes telemetry startup and shutdown outside the energy estimand."
            ),
            "authoritative_bundle": QWEN_R1,
        },
        "bundles": rows,
    }


def verify_receipt(receipt: dict[str, Any]) -> None:
    if receipt["corpus"]["bundle_count"] != 6:
        raise ValueError("expected exactly six retained powermetrics bundles")
    if not all(
        row["counter_consistency"]["all_records_within_tolerance"]
        for row in receipt["bundles"]
    ):
        raise ValueError("a retained record exceeds the counter-consistency tolerance")
    reconciliation = receipt["t07_reconciliation"]
    if not math.isclose(
        reconciliation["scanner_reconstruction_pct"],
        -0.4980639151088995,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise ValueError("canonical scanner reconstruction no longer reproduces")
    if not (-0.95 < reconciliation["verifier_reconstruction_pct"] < -0.90):
        raise ValueError("stage-envelope verifier reconstruction no longer matches -0.93%")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    receipt = build_receipt(args.runs_root)
    if args.verify:
        verify_receipt(receipt)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
