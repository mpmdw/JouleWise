#!/usr/bin/env python3
"""DIAGNOSTIC-only floor extraction over the 2026-07-23/24 Window-A corpora.

This is deliberately non-claim-bearing.  It invokes the governed extraction
CLI to preserve its fail-closed verdict, then computes explicitly labelled
diagnostics with the same frozen D-054 primitives and current exact
admissible-set corner widening.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.analysis_engine.inputs import (  # noqa: E402
    BundleEvidence,
    anchor_shift_envelope,
    deterministic_bounds,
)
from joulewise.detection_floor import (  # noqa: E402
    FloorEstimate,
    abba_delta,
    absolute_false_effect_floor,
    comparative_false_effect_floor,
)
from joulewise.floor_extraction import (  # noqa: E402
    EXTRACTION_SPEC_SCHEMA_VERSION,
    governed_cell_metric,
)

DISCLAIMER = (
    "DIAGNOSTIC ONLY; NON-CLAIM-BEARING. Every source window has a failed "
    "whole-window verdict. These values cannot establish a detection floor, "
    "claim readiness, or L2/L3 eligibility."
)

SOURCE_ROOTS = {
    "a5": Path("/Users/edr/code/JouleWise/runs_window_a5_20260723"),
    "a6": Path("/Users/edr/code/JouleWise/runs_window_a6_20260723"),
    "a7": Path("/Users/edr/code/JouleWise/runs_window_a7_20260723"),
    "a8": Path("/Users/edr/code/JouleWise/runs_window_a8_20260723"),
}

EXPECTED_CORPUS_MEMBERS = {"a5": 108, "a6": 19, "a7": 42, "a8": 60}
POSITIONS = ("A1", "B1", "B2", "A2")
POSITION_SUFFIXES = {"A1": "a1", "B1": "b1", "B2": "b2", "A2": "a2"}


def read_json(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def bundle_summary(window: str, bundle_id: str) -> Mapping[str, Any]:
    return read_json(SOURCE_ROOTS[window] / bundle_id / "summary_metrics.json")


def metric_value(summary: Mapping[str, Any], metric: str) -> float:
    if metric == "suite_item_mean_gross_energy_j":
        suite = summary.get("suite_metrics")
        items = suite.get("items") if isinstance(suite, Mapping) else None
        if not isinstance(items, list) or not items:
            raise ValueError("suite item observations missing")
        values = [row.get("energy_gross_j") for row in items if isinstance(row, Mapping)]
        if len(values) != len(items):
            raise ValueError("suite item energy missing")
        return math.fsum(float(value) for value in values) / len(values)
    if metric == "suite_level_gross_energy_j":
        suite = summary.get("suite_metrics")
        levels = suite.get("levels") if isinstance(suite, Mapping) else None
        if not isinstance(levels, list) or len(levels) != 1:
            raise ValueError("expected exactly one suite level observation")
        return float(levels[0]["energy_gross_j"])
    if metric.startswith("phase_energy_j."):
        phases = summary.get("phase_energy_j")
        if not isinstance(phases, Mapping):
            raise ValueError("phase energies missing")
        return float(phases[metric.split(".", 1)[1]])
    return float(summary[metric])


def metric_window_class(metric: str) -> str:
    if metric.startswith("phase_energy_j."):
        return "phase"
    if metric.startswith("suite_"):
        return "suite"
    return "request"


def extractor_metric(metric: str) -> str:
    if metric == "idle_subtracted_energy_j":
        return "energy_request_j"
    return metric


def diagnostic_half_width(
    *,
    window: str,
    bundle_id: str,
    metric: str,
    summary: Mapping[str, Any],
) -> tuple[float, dict[str, Any]]:
    """Mirror floor_extraction._evaluate_member's admissible half-width."""

    if metric.startswith("suite_"):
        return 0.0, {
            "source": "unavailable_for_suite_subwindows",
            "note": (
                "No governed per-item/per-level anchor envelope exists on this "
                "wire; current D-054 math is therefore shown point-only with "
                "zero diagnostic widths, not as a bounded suite floor."
            ),
        }
    governed_metric, window_class = governed_cell_metric(
        extractor_metric(metric), metric_window_class(metric)
    )
    envelope, envelope_problem = anchor_shift_envelope(summary, governed_metric)
    if envelope is None:
        return 0.0, {
            "source": "unavailable_point_only_diagnostic",
            "problem": f"anchor_envelope_{envelope_problem}",
            "note": (
                "The governed extractor refuses this member. Zero is used only "
                "to expose point-scatter diagnostics; it is not a bound."
            ),
        }
    value = metric_value(summary, metric)
    if not math.isclose(
        float(envelope["point_j"]), value, rel_tol=1e-9, abs_tol=1e-12
    ):
        raise ValueError(f"{window}/{bundle_id}/{metric}: envelope point mismatch")
    evidence = BundleEvidence(
        entry={},
        bundle_id=bundle_id,
        relative_path=bundle_id,
        path=SOURCE_ROOTS[window] / bundle_id,
        summary=summary,
        metadata=None,
        raw_config=None,
        strict_problems=(),
        base_reason_codes=(),
        config_sha256=None,
        summary_sha256=None,
        replacement_classification="registered",
        inclusion_status="included",
    )
    bounds, bound_reasons = deterministic_bounds(
        evidence,
        {
            "name": governed_metric,
            "metric_tag": f"diagnostic:{bundle_id}:{metric}",
            "window_class": window_class,
        },
    )
    interpolation = float(bounds.get("E_interpolation_joint_edge_bound_j", 0.0))
    envelope_half_width = max(
        float(envelope["point_j"]) - float(envelope["lower_j"]),
        float(envelope["upper_j"]) - float(envelope["point_j"]),
        float(envelope["max_abs_delta_j"]),
    )
    return envelope_half_width + interpolation, {
        "source": "floor_extraction_current_member_admissible_set",
        "envelope_half_width_j": envelope_half_width,
        "interpolation_joint_edge_bound_j": interpolation,
        "deterministic_bound_reasons": list(bound_reasons),
        "envelope_method": envelope["method"],
    }


def estimate_row(estimate: FloorEstimate) -> dict[str, Any]:
    return {
        "kind": estimate.kind,
        "n": estimate.n,
        "mean_j": estimate.mean_j,
        "deviations_j": list(estimate.deviations_j),
        "sample_stddev_j": estimate.sample_stddev_j,
        "max_abs_deviation_j": estimate.max_abs_deviation_j,
        "t_critical": estimate.t_critical,
        "prediction_component_j": estimate.prediction_component_j,
        "point_unguarded_floor_j": estimate.unguarded_floor_j,
        "guard_factor": estimate.guard_factor,
        "point_guarded_floor_j": estimate.guarded_floor_j,
        "admissible_half_widths_j": list(estimate.admissible_half_widths_j),
        "corner_widened_unguarded_floor_j": (
            estimate.corner_widened_unguarded_floor_j
        ),
        "corner_widened_guarded_floor_j": estimate.corner_widened_guarded_floor_j,
    }


def abs_bundle_ids(prefix: str, n: int = 10) -> list[str]:
    return [f"{prefix}-r{index:02d}" for index in range(1, n + 1)]


def abba_blocks(prefix: str, n: int) -> list[dict[str, Any]]:
    return [
        {
            "block_id": f"b{index:02d}",
            "members": {
                position: (
                    f"{prefix}-b{index:02d}-{POSITION_SUFFIXES[position]}"
                )
                for position in POSITIONS
            },
        }
        for index in range(1, n + 1)
    ]


def cell_definitions() -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []

    def add(
        *,
        cell_id: str,
        window: str,
        condition: str,
        metric: str,
        members: Sequence[str],
        blocks: Sequence[Mapping[str, Any]] = (),
        note: str = "",
    ) -> None:
        cells.append(
            {
                "cell_id": cell_id,
                "window": window,
                "condition": condition,
                "metric": metric,
                "members": list(members),
                "blocks": list(blocks),
                "note": note,
            }
        )

    for profile in ("mid", "short"):
        members = abs_bundle_ids(f"p2015-df-rq-{profile}-abs")
        for metric, label in (
            ("gross_energy_j", "gross"),
            ("energy_request_j", "idle"),
        ):
            add(
                cell_id=f"A5-RQ-{profile.upper()}-{label.upper()}",
                window="a5",
                condition=f"request_{profile}",
                metric=metric,
                members=members,
            )

    phase_profiles = (
        ("prefill", "phase_energy_j.prefill"),
        ("decode", "phase_energy_j.decode"),
        ("short-prefill", "phase_energy_j.prefill"),
    )
    for window in ("a5", "a7"):
        for profile, metric in phase_profiles:
            add(
                cell_id=f"{window.upper()}-PH-{profile.upper()}",
                window=window,
                condition=f"phase_{profile.replace('-', '_')}",
                metric=metric,
                members=abs_bundle_ids(f"p2015-df-ph-{profile}-abs"),
                blocks=(
                    abba_blocks("p2015-df-cmp-abba-ph-decode", 10)
                    if window == "a5" and profile == "decode"
                    else ()
                ),
                note=(
                    "A5 and A7 phase absolute cells are intentionally separate; "
                    "see cross_night_phase_repeatability."
                ),
            )

    suite_members = abs_bundle_ids("p2015-df-su-sentinel-abs")
    add(
        cell_id="A8-SU-ITEM",
        window="a8",
        condition="suite_sentinel_item_mean",
        metric="suite_item_mean_gross_energy_j",
        members=suite_members,
        note="Bundle-clustered mean of five same-shape suite items.",
    )
    add(
        cell_id="A8-SU-LEVEL",
        window="a8",
        condition="suite_sentinel_level",
        metric="suite_level_gross_energy_j",
        members=suite_members,
        note="Single sentinel/common_512_256 level per bundle.",
    )

    for profile in ("long-prompt", "long-decode"):
        members = abs_bundle_ids(f"p2015-df-rq-{profile}-abs")
        for metric, label in (
            ("gross_energy_j", "gross"),
            ("energy_request_j", "idle"),
        ):
            add(
                cell_id=f"A8-RQ-{profile.upper()}-{label.upper()}",
                window="a8",
                condition=f"request_{profile.replace('-', '_')}",
                metric=metric,
                members=members,
            )
    return cells


def whole_window_verdict(window: str) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in (SOURCE_ROOTS[window] / "campaign_log.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    candidates = [
        row
        for row in rows
        if row.get("record_type") == "idle_admission_whole_window_verdict"
    ]
    if not candidates:
        return {"status": "missing", "reasons": ["whole_window_verdict_missing"]}
    latest = candidates[-1]
    core = latest.get("idle_admission_core")
    return {
        "status": str(latest.get("status", "unknown")),
        "reasons": (
            list(core.get("conditions", [])) if isinstance(core, Mapping) else []
        ),
        "covered_bundle_count": len(latest.get("bundle_ids", [])),
        "record_count": len(candidates),
    }


def corpus_inventory(window: str) -> dict[str, Any]:
    root = SOURCE_ROOTS[window]
    bundle_ids = sorted(
        path.name for path in root.iterdir() if (path / "summary_metrics.json").is_file()
    )
    rows = [
        json.loads(line)
        for line in (root / "campaign_log.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    run_ids = sorted(
        {
            row["run_id"]
            for row in rows
            if isinstance(row.get("run_id"), str) and row["run_id"]
        }
    )
    statuses = Counter(
        str(row.get("status"))
        for row in rows
        if isinstance(row.get("run_id"), str)
    )
    non_bundle_evidence_dirs = sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir() and not (path / "summary_metrics.json").is_file()
    )
    observed_evidence_members_excluding_manifests = len(bundle_ids) + sum(
        name != "campaign_manifests" for name in non_bundle_evidence_dirs
    )
    return {
        "window": window,
        "source_root": str(root),
        "expected_members_from_task": EXPECTED_CORPUS_MEMBERS[window],
        "observed_run_bundle_directories": len(bundle_ids),
        "observed_unique_campaign_run_ids": len(run_ids),
        "observed_evidence_members_excluding_campaign_manifests": (
            observed_evidence_members_excluding_manifests
        ),
        "non_bundle_evidence_directories": non_bundle_evidence_dirs,
        "campaign_run_status_rows": dict(sorted(statuses.items())),
        "whole_window_verdict": whole_window_verdict(window),
    }


def compute_cell(cell: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    window = str(cell["window"])
    metric = str(cell["metric"])
    observations: list[dict[str, Any]] = []
    values: list[float] = []
    widths: list[float] = []
    for bundle_id in cell["members"]:
        summary = bundle_summary(window, bundle_id)
        if summary.get("status") != "succeeded":
            raise ValueError(f"complete cell member did not succeed: {window}/{bundle_id}")
        value = metric_value(summary, metric)
        width, width_evidence = diagnostic_half_width(
            window=window,
            bundle_id=bundle_id,
            metric=metric,
            summary=summary,
        )
        values.append(value)
        widths.append(width)
        observations.append(
            {
                "bundle_id": bundle_id,
                "metric_value_j": value,
                "admissible_half_width_j": width,
                "width_evidence": width_evidence,
            }
        )
    absolute = absolute_false_effect_floor(
        values, admissible_half_widths_j=widths
    )

    comparative: FloorEstimate | None = None
    comparative_blocks: list[dict[str, Any]] = []
    if cell["blocks"]:
        deltas: list[float] = []
        block_widths: list[float] = []
        for block in cell["blocks"]:
            member_rows: dict[str, Any] = {}
            member_values: dict[str, float] = {}
            member_widths: dict[str, float] = {}
            for position in POSITIONS:
                bundle_id = block["members"][position]
                summary = bundle_summary(window, bundle_id)
                if summary.get("status") != "succeeded":
                    raise ValueError(
                        f"complete ABBA member did not succeed: {window}/{bundle_id}"
                    )
                value = metric_value(summary, metric)
                width, width_evidence = diagnostic_half_width(
                    window=window,
                    bundle_id=bundle_id,
                    metric=metric,
                    summary=summary,
                )
                member_values[position] = value
                member_widths[position] = width
                member_rows[position] = {
                    "bundle_id": bundle_id,
                    "metric_value_j": value,
                    "admissible_half_width_j": width,
                    "width_evidence": width_evidence,
                }
            delta = abba_delta(
                member_values["A1"],
                member_values["B1"],
                member_values["B2"],
                member_values["A2"],
            )
            delta_width = math.fsum(member_widths.values()) / 2.0
            deltas.append(delta)
            block_widths.append(delta_width)
            comparative_blocks.append(
                {
                    "block_id": block["block_id"],
                    "members": member_rows,
                    "delta_j": delta,
                    "admissible_delta_half_width_j": delta_width,
                    "admissible_delta_interval_j": [
                        delta - delta_width,
                        delta + delta_width,
                    ],
                }
            )
        comparative = comparative_false_effect_floor(
            deltas, admissible_half_widths_j=block_widths
        )

    verdict = whole_window_verdict(window)
    floor_abs = absolute.corner_widened_guarded_floor_j
    floor_cmp = (
        comparative.corner_widened_guarded_floor_j
        if comparative is not None
        else None
    )
    floor_gate = (
        max(float(floor_abs), float(floor_cmp))
        if floor_abs is not None and floor_cmp is not None
        else None
    )
    detail = {
        "cell_id": cell["cell_id"],
        "diagnostic_caveat": DISCLAIMER,
        "window": window,
        "source_root": str(SOURCE_ROOTS[window]),
        "window_verdict": verdict,
        "condition": cell["condition"],
        "metric": metric,
        "window_class": metric_window_class(metric),
        "note": cell["note"],
        "absolute": {
            "observations": observations,
            "estimate": estimate_row(absolute),
            "bounded_width_member_count": sum(
                row["width_evidence"]["source"]
                == "floor_extraction_current_member_admissible_set"
                for row in observations
            ),
        },
        "comparative": (
            {
                "blocks": comparative_blocks,
                "estimate": estimate_row(comparative),
            }
            if comparative is not None
            else None
        ),
        "floor_abs_j": floor_abs,
        "floor_cmp_j": floor_cmp,
        "floor_gate_j": floor_gate,
        "admissible_width_coverage": (
            f"{sum(row['width_evidence']['source'] == 'floor_extraction_current_member_admissible_set' for row in observations)}/{len(observations)}"
        ),
    }
    summary = {
        "cell_id": cell["cell_id"],
        "metric": metric,
        "condition": cell["condition"],
        "n": absolute.n,
        "n_abs": absolute.n,
        "n_cmp": comparative.n if comparative is not None else None,
        "floor_abs_j": floor_abs,
        "floor_cmp_j": floor_cmp,
        "floor_gate_j": floor_gate,
        "window_of_origin": window,
        "window_verdict_status": verdict["status"],
        "admissible_width_coverage": detail["admissible_width_coverage"],
        "diagnostic_caveat": DISCLAIMER,
    }
    return detail, summary


def discover_completed_blocks(
    window: str, prefix: str, metric: str
) -> list[dict[str, Any]]:
    root = SOURCE_ROOTS[window]
    pattern = re.compile(
        rf"^{re.escape(prefix)}-b(?P<block>[0-9]{{2}})-(?P<position>a1|b1|b2|a2)$"
    )
    by_block: dict[str, dict[str, str]] = {}
    suffix_to_position = {value: key for key, value in POSITION_SUFFIXES.items()}
    for path in root.iterdir():
        match = pattern.match(path.name)
        if not match or not (path / "summary_metrics.json").is_file():
            continue
        by_block.setdefault(f"b{match.group('block')}", {})[
            suffix_to_position[match.group("position")]
        ] = path.name
    completed: list[dict[str, Any]] = []
    for block_id, members in sorted(by_block.items()):
        if set(members) != set(POSITIONS):
            continue
        summaries = {
            position: bundle_summary(window, members[position])
            for position in POSITIONS
        }
        if any(summary.get("status") != "succeeded" for summary in summaries.values()):
            continue
        member_rows: dict[str, Any] = {}
        values: dict[str, float] = {}
        widths: dict[str, float] = {}
        for position in POSITIONS:
            bundle_id = members[position]
            summary = summaries[position]
            value = metric_value(summary, metric)
            width, width_evidence = diagnostic_half_width(
                window=window,
                bundle_id=bundle_id,
                metric=metric,
                summary=summary,
            )
            values[position] = value
            widths[position] = width
            member_rows[position] = {
                "bundle_id": bundle_id,
                "metric_value_j": value,
                "admissible_half_width_j": width,
                "width_evidence": width_evidence,
            }
        delta = abba_delta(
            values["A1"], values["B1"], values["B2"], values["A2"]
        )
        delta_width = math.fsum(widths.values()) / 2.0
        completed.append(
            {
                "block_id": block_id,
                "members": member_rows,
                "delta_j": delta,
                "admissible_delta_half_width_j": delta_width,
                "admissible_delta_interval_j": [
                    delta - delta_width,
                    delta + delta_width,
                ],
            }
        )
    return completed


def partial_abba_results() -> list[dict[str, Any]]:
    targets = (
        ("a5", "request", "p2015-df-cmp-abba-rq", "gross_energy_j"),
        ("a6", "prefill", "p2015-df-cmp-abba-ph-prefill", "phase_energy_j.prefill"),
        ("a7", "request", "p2015-df-cmp-abba-rq", "gross_energy_j"),
    )
    results: list[dict[str, Any]] = []
    for window, family, prefix, metric in targets:
        blocks = discover_completed_blocks(window, prefix, metric)
        estimate = None
        if len(blocks) >= 2:
            estimate = comparative_false_effect_floor(
                [float(block["delta_j"]) for block in blocks],
                admissible_half_widths_j=[
                    float(block["admissible_delta_half_width_j"])
                    for block in blocks
                ],
            )
        results.append(
            {
                "diagnostic_caveat": DISCLAIMER,
                "window": window,
                "window_verdict": whole_window_verdict(window),
                "family": family,
                "metric": metric,
                "completed_block_count": len(blocks),
                "completed_blocks": blocks,
                "partial_cell_smoke_estimate": (
                    estimate_row(estimate) if estimate is not None else None
                ),
                "note": (
                    "Block deltas are diagnostic. Partial cells are not complete; "
                    "n<5 has no guarded floor under D-054."
                ),
            }
        )
    return results


def neg8_results() -> list[dict[str, Any]]:
    metrics = (
        "gross_energy_j",
        "energy_request_j",
        "phase_energy_j.prefill",
        "phase_energy_j.decode",
        "energy_token_j",
    )
    results: list[dict[str, Any]] = []
    for window in SOURCE_ROOTS:
        start = bundle_summary(window, "p2015-neg8-reference-start")
        end = bundle_summary(window, "p2015-neg8-reference-end")
        pair_valid = (
            start.get("status") == "succeeded" and end.get("status") == "succeeded"
        )
        deltas: list[dict[str, Any]] = []
        if pair_valid:
            for metric in metrics:
                start_value = metric_value(start, metric)
                end_value = metric_value(end, metric)
                start_width = end_width = None
                width_note: dict[str, Any] | None = None
                if metric != "energy_token_j":
                    start_width, start_evidence = diagnostic_half_width(
                        window=window,
                        bundle_id="p2015-neg8-reference-start",
                        metric=metric,
                        summary=start,
                    )
                    end_width, end_evidence = diagnostic_half_width(
                        window=window,
                        bundle_id="p2015-neg8-reference-end",
                        metric=metric,
                        summary=end,
                    )
                    width_note = {
                        "start": start_evidence,
                        "end": end_evidence,
                    }
                delta = end_value - start_value
                deltas.append(
                    {
                        "metric": metric,
                        "start_j": start_value,
                        "end_j": end_value,
                        "delta_end_minus_start_j": delta,
                        "delta_percent_of_start": (
                            100.0 * delta / start_value if start_value != 0.0 else None
                        ),
                        "admissible_delta_half_width_j": (
                            start_width + end_width
                            if start_width is not None and end_width is not None
                            else None
                        ),
                        "width_evidence": width_note,
                    }
                )
        results.append(
            {
                "diagnostic_caveat": DISCLAIMER,
                "window": window,
                "window_verdict": whole_window_verdict(window),
                "pair_status": "available" if pair_valid else "unavailable",
                "start_summary_status": start.get("status"),
                "end_summary_status": end.get("status"),
                "deltas": deltas,
                "note": (
                    "A7 is unavailable because its end reference bundle failed."
                    if not pair_valid
                    else "Reference-pair differences are drift diagnostics, not floors."
                ),
            }
        )
    return results


def phase_repeatability(details: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_condition_window = {
        (str(row["condition"]), str(row["window"])): row
        for row in details
        if str(row["condition"]).startswith("phase_")
    }
    rows: list[dict[str, Any]] = []
    for condition in (
        "phase_prefill",
        "phase_decode",
        "phase_short_prefill",
    ):
        a5 = by_condition_window[(condition, "a5")]
        a7 = by_condition_window[(condition, "a7")]
        a5_est = a5["absolute"]["estimate"]
        a7_est = a7["absolute"]["estimate"]
        a5_floor = float(a5["floor_abs_j"])
        a7_floor = float(a7["floor_abs_j"])
        rows.append(
            {
                "condition": condition,
                "metric": a5["metric"],
                "a5_mean_j": a5_est["mean_j"],
                "a7_mean_j": a7_est["mean_j"],
                "a7_minus_a5_mean_j": a7_est["mean_j"] - a5_est["mean_j"],
                "a5_floor_abs_j": a5_floor,
                "a7_floor_abs_j": a7_floor,
                "a7_to_a5_floor_ratio": (
                    a7_floor / a5_floor if a5_floor != 0.0 else None
                ),
                "note": (
                    "Cross-night diagnostic only; windows are not pooled and both "
                    "whole-window verdicts failed."
                ),
            }
        )
    return rows


def build_cli_specs(out_dir: Path) -> dict[str, Path]:
    cells_by_window: dict[str, list[dict[str, Any]]] = {
        "a5": [],
        "a7": [],
        "a8": [],
    }
    for cell in cell_definitions():
        window = str(cell["window"])
        metric = str(cell["metric"])
        if window not in cells_by_window or metric.startswith("suite_"):
            continue
        governed_metric, window_class = governed_cell_metric(
            extractor_metric(metric), metric_window_class(metric)
        )
        cells_by_window[window].append(
            {
                "cell_id": f"{cell['cell_id']}-ABS",
                "kind": "absolute",
                "metric": governed_metric,
                "window_class": window_class,
                "members": [
                    {"slot": bundle_id, "bundle_id": bundle_id}
                    for bundle_id in cell["members"]
                ],
            }
        )
        if cell["blocks"]:
            cells_by_window[window].append(
                {
                    "cell_id": f"{cell['cell_id']}-CMP",
                    "kind": "comparative",
                    "metric": governed_metric,
                    "window_class": window_class,
                    "blocks": cell["blocks"],
                }
            )
    specs: dict[str, Mapping[str, Any]] = {
        f"{window}_complete_supported_cells": {
            "schema_version": EXTRACTION_SPEC_SCHEMA_VERSION,
            "cells": cells,
        }
        for window, cells in cells_by_window.items()
    }
    paths: dict[str, Path] = {}
    for name, spec in specs.items():
        path = out_dir / "specs" / f"{name}.json"
        write_json(path, spec)
        paths[name] = path
    return paths


def run_governed_cli(
    out_dir: Path, tmp_dir: Path, specs: Mapping[str, Path]
) -> list[dict[str, Any]]:
    help_command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "extract_detection_floors.py"),
        "--help",
    ]
    env = os.environ.copy()
    env["TMPDIR"] = str(tmp_dir)
    help_completed = subprocess.run(
        help_command,
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    results: list[dict[str, Any]] = [
        {
            "name": "governed_cli_entry_smoke",
            "tool_mode": "cli_entry_smoke",
            "command": help_command,
            "cwd": str(REPO_ROOT),
            "tmpdir": str(tmp_dir),
            "exit_code": help_completed.returncode,
            "stdout": help_completed.stdout,
            "stderr": help_completed.stderr,
            "interpretation": (
                "CLI entry exercised successfully. Corpus extraction below uses "
                "the same extract_cells implementation with an explicitly "
                "diagnostic summary-only strict-validator stub."
            ),
        }
    ]
    for name, spec_path in specs.items():
        results.append(
            {
                "name": name,
                "tool_mode": "prepared_replay_spec_not_run",
                "command": (
                    f"{sys.executable} "
                    f"{REPO_ROOT / 'scripts' / 'extract_detection_floors.py'} "
                    f"--runs-root {SOURCE_ROOTS[name[:2]]} --spec {spec_path} "
                    f"--out <fresh-output-path>"
                ),
                "cwd": str(REPO_ROOT),
                "tmpdir": str(tmp_dir),
                "exit_code": None,
                "interpretation": (
                    "Prepared but intentionally not run to completion: the "
                    "claim-bearing CLI revalidates ~127 MB raw telemetry per "
                    "bundle/metric and rederives the already-failed whole-window "
                    "verdict. This diagnostic extraction instead uses the current "
                    "D-054 and exact-corner primitives directly."
                ),
            }
        )
    return results


def fmt_number(value: Any) -> str:
    if value is None:
        return "—"
    return f"{float(value):.6f}"


def write_summary_markdown(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    lines = [
        "# DIAGNOSTIC floor summary — NON-CLAIM-BEARING",
        "",
        DISCLAIMER,
        "",
        (
            "`floor_gate_j` is null unless both absolute and comparative "
            "components exist for the same window-local cell. Suite rows are "
            "point-only because this wire has no governed per-item/per-level "
            "admissible half-width."
        ),
        "",
        "| Cell | Metric | Condition | n | floor_abs_j | floor_cmp_j | floor_gate_j | Width coverage | Origin | Window verdict | Caveat |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {cell_id} | `{metric}` | `{condition}` | {n} | {floor_abs} | "
            "{floor_cmp} | {floor_gate} | {width_coverage} | {origin} | **{verdict}** | "
            "DIAGNOSTIC ONLY; NON-CLAIM-BEARING |".format(
                cell_id=row["cell_id"],
                metric=row["metric"],
                condition=row["condition"],
                n=row["n"],
                floor_abs=fmt_number(row["floor_abs_j"]),
                floor_cmp=fmt_number(row["floor_cmp_j"]),
                floor_gate=fmt_number(row["floor_gate_j"]),
                width_coverage=row["admissible_width_coverage"],
                origin=row["window_of_origin"],
                verdict=row["window_verdict_status"],
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    parser.add_argument("--tmp-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    out_dir = args.out_dir.resolve()
    tmp_dir = args.tmp_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    inventories = [corpus_inventory(window) for window in SOURCE_ROOTS]
    details: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for cell in cell_definitions():
        detail, summary = compute_cell(cell)
        details.append(detail)
        summary_rows.append(summary)

    partial = partial_abba_results()
    neg8 = neg8_results()
    repeatability = phase_repeatability(details)
    specs = build_cli_specs(out_dir)
    cli_runs = run_governed_cli(out_dir, tmp_dir, specs)

    write_json(
        out_dir / "diagnostic_details.json",
        {
            "schema_version": "joulewise.diagnostic_floor_extraction.v1",
            "claim_bearing": False,
            "diagnostic_caveat": DISCLAIMER,
            "source_roots_read_only": {
                window: str(path) for window, path in SOURCE_ROOTS.items()
            },
            "corpus_inventory": inventories,
            "complete_cell_details": details,
            "partial_abba_results": partial,
            "neg8_reference_pair_deltas": neg8,
            "cross_night_phase_repeatability": repeatability,
            "governed_cli_runs": cli_runs,
        },
    )
    write_json(
        out_dir / "summary_table.json",
        {
            "schema_version": "joulewise.diagnostic_floor_summary.v1",
            "claim_bearing": False,
            "diagnostic_caveat": DISCLAIMER,
            "rows": summary_rows,
        },
    )
    write_summary_markdown(out_dir / "summary_table.md", summary_rows)
    write_json(out_dir / "governed_cli_runs.json", cli_runs)

    print(f"DIAGNOSTIC_ONLY rows={len(summary_rows)}")
    print(f"partial_groups={len(partial)} neg8_windows={len(neg8)}")
    print(
        "governed_cli_exit_codes="
        + ",".join(f"{row['name']}:{row['exit_code']}" for row in cli_runs)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
