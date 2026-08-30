#!/usr/bin/env python3
"""Project prefill-arm resolvability at 512 / 1024 / 2048 prompt tokens.

Desk pre-registration for the D-162 G2 shakedown, answering reviewer-panel
item D1 ("the paper never states the projected overlap count ... and never
states the contingency") as re-scoped by D-166 R-2.

The script is a reader, not a re-runner.  It walks the retained bundle
corpora, pulls the prompt-processing ("prefill") phase boundaries out of each
bundle's ``events.jsonl``, pulls each *powermetrics* record's support interval
out of the same bundle's ``power_trace.csv``, and recomputes the overlap count
with the identical predicate the production reducer applies
(``joulewise/reduce.py::_in_window_sample_count``).  Nothing is simulated and
no bundle is written to.

Outputs a single JSON document carrying every input duration, every derived
rate, and every projection, so that each number printed in the companion
Markdown is traceable to a hashed retained file.

Usage:

    .venv/bin/python scripts/paper_prefill_resolvability_projection.py \
        --corpus-root /Users/edr/code/JouleWise \
        --out docs/paper/round7/prefill-resolvability-projection.json
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any, Iterable, Sequence


# --------------------------------------------------------------------------
# Constants that are ruled elsewhere.  Each is restated here with its ONE home
# so a reader can check that this script did not invent a threshold.

# joulewise/reduce.py:116 -- a phase needs at least this many overlapping
# powermetrics records before the reducer will call it resolvable.
MIN_PHASE_SAMPLES = 3

# joulewise/window_duration_margins.py:801-803 -- the repository's own named
# quantity "sample-count margin", schema-checked at :1091-1093.
#     sample_count_margin = overlapping_power_interval_count - MIN_PHASE_SAMPLES

# D-166 R-2 candidate prefill lengths, in prompt tokens.
CANDIDATE_LENGTHS = (512, 1024, 2048)

# D-166 R-2 reads "... show >= 3 overlapping records with margin (>= 5) in
# every shakedown member".  Two readings of "margin (>= 5)" survive the
# sentence; both are evaluated and neither is silently preferred.
RULE_READINGS = {
    # The repository already has a field literally named "margin" that means
    # count - MIN_PHASE_SAMPLES.  Under that convention margin >= 5 means:
    "A_repo_margin_field": {
        "gloss": (
            "'margin' is the repository's sample_count_margin field, "
            "count minus MIN_PHASE_SAMPLES; margin >= 5 therefore requires "
            "count >= 8 in every small-model member."
        ),
        "min_count": MIN_PHASE_SAMPLES + 5,
    },
    # Plain English: pass the >=3 rule with room to spare, where "with room to
    # spare" is spelled out as at least 5 records.
    "B_plain_english_floor": {
        "gloss": (
            "'>= 3 overlapping records with margin' is operationalised by the "
            "parenthetical as an absolute floor of 5 records in every "
            "small-model member."
        ),
        "min_count": 5,
    },
}

SMALL_MODEL_V4 = "Qwen2.5-1.5B-Instruct-4bit"
LARGE_MODEL_V4 = "Qwen2.5-7B-Instruct-4bit"

# D-164: the _v5 campaign pair.  Parameter counts and 4-bit weight sizes are
# the model-panel survey's table (docs/process_traces/2026-08-28-model-panel/
# 00-SURVEY.md, section 1).
V5_PAIR = {
    "small": {
        "repo": "mlx-community/Qwen3-1.7B-4bit",
        "revision_prefix": "3b1b1768",
        "params_b": 1.7,
        "weights_gb_4bit": 0.97,
        "predecessor": SMALL_MODEL_V4,
        "predecessor_params_b": 1.5,
        "predecessor_weights_gb_4bit": 0.87,
    },
    "large": {
        "repo": "mlx-community/Qwen3-8B-4bit",
        "revision_prefix": "545dc425",
        "params_b": 8.0,
        "weights_gb_4bit": 4.61,
        "predecessor": LARGE_MODEL_V4,
        "predecessor_params_b": 7.0,
        # The survey table covers the campaign models only. This one is the
        # measured on-disk size of the pinned local artifact
        # /Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit
        # (4.0 GiB = 4.30 GB), not a survey figure.
        "predecessor_weights_gb_4bit": 4.30,
        "predecessor_weights_source": "measured on-disk size of the pinned local artifact",
    },
}

# Slowdown multipliers applied to the measured Qwen2.5 prefill durations to
# stand in for the unmeasured Qwen3 durations.  1.0 is "identical rate"; the
# parameter-count ratio is the assumption the companion document argues for;
# the rest sweep the sensitivity question.
TRANSFER_MULTIPLIERS = (1.0, 1.133, 1.25, 1.5, 2.0, 3.0)


# --------------------------------------------------------------------------
# Bundle reading


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_prefill_phases(events_path: Path) -> list[tuple[int | None, float, float]]:
    """Return every (prompt_tokens, prefill_start_s, prefill_end_s) in a bundle.

    The boundary is the runtime's own paired phase_start / phase_end events for
    ``phase == "prefill"``; there is no precomputed duration field in a bundle.

    A bundle can hold MORE THAN ONE prefill phase.  Single-item cells hold one;
    a suite bundle (``jw_mixed_v1``) holds one per item.  Taking only the last
    pair silently discards the others and makes the bundle disagree with its own
    recorded label, because the reducer labels the bundle on its worst phase.
    The prompt token count is carried on each ``phase_start`` record, so each
    phase is attributed to its own prompt length.
    """
    phases: list[tuple[int | None, float, float]] = []
    open_start: float | None = None
    open_tokens: int | None = None
    with events_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if '"phase' not in line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("phase") != "prefill":
                continue
            metadata = event.get("metadata") or {}
            if event.get("event_type") == "phase_start":
                open_start = float(event["timestamp_s"])
                raw_tokens = metadata.get("prompt_tokens")
                open_tokens = int(raw_tokens) if raw_tokens is not None else None
            elif event.get("event_type") == "phase_end" and open_start is not None:
                phases.append((open_tokens, open_start, float(event["timestamp_s"])))
                open_start = None
                open_tokens = None
    return phases


def read_support_intervals(trace_path: Path) -> list[tuple[float, float]]:
    """Return one (support_start_s, support_end_s) per distinct power record.

    A *powermetrics* record is written once per rail (cpu / gpu / ane) at the
    same timestamp, so the rows are de-duplicated on ``timestamp_s`` before the
    supports are returned: the reducer counts records, not rail rows.
    """
    supports: dict[float, tuple[float, float]] = {}
    with trace_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            raw_start = row.get("interval_start_s")
            raw_end = row.get("interval_end_s")
            if not raw_start or not raw_end:
                continue
            supports[float(row["timestamp_s"])] = (float(raw_start), float(raw_end))
    return [supports[key] for key in sorted(supports)]


def overlap_count(supports: Sequence[tuple[float, float]], start: float, end: float) -> int:
    """The reducer's predicate, verbatim in meaning.

    joulewise/reduce.py:196-206 counts a record when its support and the phase
    window overlap for strictly positive time:
        min(window_end, support_end) > max(window_start, support_start)
    """
    return sum(
        1
        for support_start, support_end in supports
        if min(end, support_end) > max(start, support_start)
    )


def recorded_label(summary_path: Path) -> str | None:
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    try:
        return summary["measurement_quality"]["phase_identifiability"]["prefill"]
    except (KeyError, TypeError):
        return None


def read_model(metadata_path: Path) -> tuple[str | None, str | None]:
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, None
    model = metadata.get("model") or {}
    if not isinstance(model, dict):
        return None, None
    return model.get("name"), model.get("revision")


def scan_corpora(
    corpus_root: Path, models: Iterable[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[float]]:
    """Walk every retained ``runs*/<bundle>/`` directory once.

    Returns (phase observations, bundle summaries, every record period seen).
    """
    wanted = set(models)
    observations: list[dict[str, Any]] = []
    bundle_rows: list[dict[str, Any]] = []
    all_periods: list[float] = []
    for corpus_dir in sorted(p for p in corpus_root.iterdir() if p.is_dir() and p.name.startswith("runs")):
        for bundle_dir in sorted(p for p in corpus_dir.iterdir() if p.is_dir()):
            events_path = bundle_dir / "events.jsonl"
            trace_path = bundle_dir / "power_trace.csv"
            metadata_path = bundle_dir / "metadata.json"
            if not (events_path.is_file() and trace_path.is_file() and metadata_path.is_file()):
                continue
            model_name, model_revision = read_model(metadata_path)
            if model_name not in wanted:
                continue
            phases = read_prefill_phases(events_path)
            if not phases:
                continue
            supports = read_support_intervals(trace_path)
            if not supports:
                continue
            periods = [b - a for (a, _), (b, _) in zip(supports, supports[1:])]
            tiling_gaps = [abs(nxt_start - prev_end) for (_, prev_end), (nxt_start, _) in zip(supports, supports[1:])]
            all_periods.extend(periods)
            events_sha = sha256_of(events_path)
            trace_sha = sha256_of(trace_path)
            label = recorded_label(bundle_dir / "summary_metrics.json")
            counts: list[int] = []
            for index, (prompt_tokens, start, end) in enumerate(phases):
                if prompt_tokens is None:
                    continue
                count = overlap_count(supports, start, end)
                counts.append(count)
                observations.append(
                    {
                        "corpus": corpus_dir.name,
                        "bundle": bundle_dir.name,
                        "path": str(bundle_dir),
                        "phase_index": index,
                        "phases_in_bundle": len(phases),
                        # A bundle holding exactly one prefill phase has the shape
                        # the _v5 prefill cells will have: one prompt, one member.
                        "cell_shape": "single_item_cell" if len(phases) == 1 else "multi_item_suite",
                        "model_name": model_name,
                        "model_revision": model_revision,
                        "prompt_tokens": prompt_tokens,
                        "prefill_start_s": start,
                        "prefill_end_s": end,
                        "prefill_duration_s": end - start,
                        "overlap_record_count": count,
                        "sample_count_margin": count - MIN_PHASE_SAMPLES,
                        "events_jsonl_sha256": events_sha,
                        "power_trace_csv_sha256": trace_sha,
                    }
                )
            if not counts:
                continue
            worst = min(counts)
            bundle_rows.append(
                {
                    "corpus": corpus_dir.name,
                    "bundle": bundle_dir.name,
                    "path": str(bundle_dir),
                    "model_name": model_name,
                    "phases_in_bundle": len(phases),
                    "worst_phase_overlap_count": worst,
                    "recomputed_label": (
                        "identifiable" if worst >= MIN_PHASE_SAMPLES else "not_resolvable_sample_count"
                    ),
                    "recorded_prefill_identifiability": label,
                    "record_count_in_trace": len(supports),
                    "record_period_s_median": statistics.median(periods) if periods else None,
                    "record_period_s_max": max(periods) if periods else None,
                    "record_period_s_min": min(periods) if periods else None,
                    "max_abs_tiling_gap_s": max(tiling_gaps) if tiling_gaps else None,
                    "events_jsonl_sha256": events_sha,
                    "power_trace_csv_sha256": trace_sha,
                }
            )
    return observations, bundle_rows, all_periods


# --------------------------------------------------------------------------
# Statistics helpers


def quantile(sorted_values: Sequence[float], fraction: float) -> float:
    if not sorted_values:
        raise ValueError("empty")
    index = min(len(sorted_values) - 1, max(0, int(round(fraction * (len(sorted_values) - 1)))))
    return sorted_values[index]


def describe(values: Sequence[float]) -> dict[str, Any]:
    ordered = sorted(values)
    return {
        "n": len(ordered),
        "min": ordered[0],
        "q1": quantile(ordered, 0.25),
        "median": statistics.median(ordered),
        "q3": quantile(ordered, 0.75),
        "max": ordered[-1],
        "iqr": quantile(ordered, 0.75) - quantile(ordered, 0.25),
    }


def least_squares_affine(points: Sequence[tuple[float, float]]) -> dict[str, float]:
    """Fit duration = fixed_overhead_s + tokens / marginal_rate_tok_s."""
    n = len(points)
    mean_x = sum(x for x, _ in points) / n
    mean_y = sum(y for _, y in points) / n
    sxx = sum((x - mean_x) ** 2 for x, _ in points)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in points)
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    residuals = [y - (intercept + slope * x) for x, y in points]
    return {
        "fixed_overhead_s": intercept,
        "seconds_per_token": slope,
        "marginal_rate_tokens_per_s": 1.0 / slope,
        "max_abs_residual_s": max(abs(r) for r in residuals),
        "points": [{"prompt_tokens": x, "duration_s": y, "residual_s": r} for (x, y), r in zip(points, residuals)],
    }


def guaranteed_record_count(duration_s: float, period_s: float) -> int:
    """Lower bound on overlapping records, derived in the companion document.

    Powermetrics records tile the timeline with no gap: each record's support
    begins exactly where the previous one's ended (verified per bundle by
    ``max_abs_tiling_gap_s``).  A phase window therefore overlaps one record
    plus one more for every tile boundary that falls strictly inside it.  With
    tile period no greater than ``period_s`` there are at least
    floor(duration / period_s) such boundaries, so:

        count >= floor(duration / period_s) + 1

    Using the LARGEST observed period makes this a bound, not an estimate: a
    longer period means fewer boundaries and so fewer records.
    """
    return math.floor(duration_s / period_s) + 1


def best_case_record_count(duration_s: float, period_s: float) -> int:
    """Upper bound, using the SHORTEST observed period and lucky alignment."""
    return math.floor(duration_s / period_s) + 2


# --------------------------------------------------------------------------
# Main


def build(corpus_root: Path, repo_root: Path) -> dict[str, Any]:
    observations, bundle_rows, all_periods = scan_corpora(corpus_root, (SMALL_MODEL_V4, LARGE_MODEL_V4))
    if not observations:
        raise SystemExit(f"no retained prefill phases found under {corpus_root}")

    # ---- the instrument: how long is one powermetrics record, and do records
    #      leave gaps between them?
    ordered_periods = sorted(all_periods)
    max_gap = max(row["max_abs_tiling_gap_s"] for row in bundle_rows if row["max_abs_tiling_gap_s"] is not None)
    period_typical_s = statistics.median(ordered_periods)
    period_conservative_s = quantile(ordered_periods, 0.99)
    period_worst_observed_s = ordered_periods[-1]
    period_optimistic_s = ordered_periods[0]
    sampler = {
        "record_count_examined": len(ordered_periods),
        "bundles_examined": len(bundle_rows),
        "records_tile_without_gap": max_gap < 1e-6,
        "max_abs_tiling_gap_s_over_population": max_gap,
        "tiling_note": (
            "Each record's support begins where the previous one's support "
            "ended, to within floating-point noise. Record width and record "
            "spacing are therefore the same quantity measured per record, and "
            "no interval of the timeline is left uncovered. The reason median "
            "spacing exceeds the narrowest observed widths is that the widths "
            "themselves vary, not that the sampler pauses."
        ),
        "record_period_s": {
            "min": ordered_periods[0],
            "p01": quantile(ordered_periods, 0.01),
            "median": period_typical_s,
            "p95": quantile(ordered_periods, 0.95),
            "p99": period_conservative_s,
            "p999": quantile(ordered_periods, 0.999),
            "max": period_worst_observed_s,
        },
        "long_period_note": (
            "The maximum observed period is far above the 99th percentile "
            "because a few traces drop samples. The conservative bound uses "
            "the 99th percentile, and the maximum is reported beside it so the "
            "choice is visible rather than assumed."
        ),
    }

    # ---- measured evidence, grouped by model, prompt length and cell shape
    groups: dict[tuple[str, int, str], list[dict[str, Any]]] = defaultdict(list)
    for observation in observations:
        key = (observation["model_name"], observation["prompt_tokens"], observation["cell_shape"])
        groups[key].append(observation)

    evidence: list[dict[str, Any]] = []
    for (model_name, prompt_tokens, cell_shape), members in sorted(groups.items()):
        durations = [m["prefill_duration_s"] for m in members]
        counts = Counter(m["overlap_record_count"] for m in members)
        evidence.append(
            {
                "model_name": model_name,
                "prompt_tokens": prompt_tokens,
                "cell_shape": cell_shape,
                "corpora": sorted({m["corpus"] for m in members}),
                "bundle_count": len({(m["corpus"], m["bundle"]) for m in members}),
                "prefill_phase_count": len(members),
                "prefill_duration_s": describe(durations),
                "overlap_record_count_histogram": {str(k): v for k, v in sorted(counts.items())},
                "min_overlap_record_count": min(counts),
                "max_overlap_record_count": max(counts),
                "min_sample_count_margin": min(counts) - MIN_PHASE_SAMPLES,
                "phases_below_min_phase_samples": sum(v for k, v in counts.items() if k < MIN_PHASE_SAMPLES),
                "tokens_per_second_from_median_duration": prompt_tokens / statistics.median(durations),
            }
        )

    # ---- does the recorded per-bundle label agree with a fresh recount?
    disagreements = [
        row
        for row in bundle_rows
        if row["recorded_prefill_identifiability"] is not None
        and row["recorded_prefill_identifiability"] != row["recomputed_label"]
    ]
    label_agreement = {
        "bundles_with_recorded_label": sum(1 for r in bundle_rows if r["recorded_prefill_identifiability"]),
        "disagreement_count": len(disagreements),
        "disagreement_examples": [
            {
                "path": r["path"],
                "phases_in_bundle": r["phases_in_bundle"],
                "worst_phase_overlap_count": r["worst_phase_overlap_count"],
                "recomputed_label": r["recomputed_label"],
                "recorded_label": r["recorded_prefill_identifiability"],
            }
            for r in disagreements[:10]
        ],
    }

    # ---- validate the bound against every measured group
    bound_check = []
    for group in evidence:
        duration_min = group["prefill_duration_s"]["min"]
        duration_max = group["prefill_duration_s"]["max"]
        predicted_min = guaranteed_record_count(duration_min, period_conservative_s)
        predicted_max = best_case_record_count(duration_max, period_optimistic_s)
        bound_check.append(
            {
                "model_name": group["model_name"],
                "prompt_tokens": group["prompt_tokens"],
                "cell_shape": group["cell_shape"],
                "phases": group["prefill_phase_count"],
                "observed_min_count": group["min_overlap_record_count"],
                "observed_max_count": group["max_overlap_record_count"],
                "bound_min_count": predicted_min,
                "bound_max_count": predicted_max,
                "lower_bound_holds": predicted_min <= group["min_overlap_record_count"],
                "upper_bound_holds": predicted_max >= group["max_overlap_record_count"],
            }
        )
    bound_validation = {
        "conservative_period_used_s": period_conservative_s,
        "optimistic_period_used_s": period_optimistic_s,
        "groups_checked": len(bound_check),
        "all_lower_bounds_hold": all(r["lower_bound_holds"] for r in bound_check),
        "all_upper_bounds_hold": all(r["upper_bound_holds"] for r in bound_check),
        "rows": bound_check,
    }

    # ---- affine duration model for the small model
    def group_for(model_name: str, shape: str | None = None) -> dict[int, dict[str, Any]]:
        chosen: dict[int, dict[str, Any]] = {}
        for group in evidence:
            if group["model_name"] != model_name:
                continue
            if shape is not None and group["cell_shape"] != shape:
                continue
            length = group["prompt_tokens"]
            existing = chosen.get(length)
            # Prefer the group with more phases behind it.
            if existing is None or group["prefill_phase_count"] > existing["prefill_phase_count"]:
                chosen[length] = group
        return chosen

    small_single = group_for(SMALL_MODEL_V4, "single_item_cell")
    small_suite = group_for(SMALL_MODEL_V4, "multi_item_suite")
    large_single = group_for(LARGE_MODEL_V4, "single_item_cell")

    fit_points = [
        (float(length), small_single[length]["prefill_duration_s"]["median"])
        for length in sorted(small_single)
        if length >= 128
    ]
    small_fit = least_squares_affine(fit_points)

    large_fit = None
    if len(large_single) >= 2:
        large_fit = least_squares_affine(
            [(float(k), v["prefill_duration_s"]["median"]) for k, v in sorted(large_single.items())]
        )
    shared_lengths = sorted(set(large_single) & set(small_single))
    large_over_small_ratio = None
    if shared_lengths:
        token_count = shared_lengths[0]
        large_median = large_single[token_count]["prefill_duration_s"]["median"]
        small_median = small_single[token_count]["prefill_duration_s"]["median"]
        large_over_small_ratio = {
            "at_prompt_tokens": token_count,
            "large_median_duration_s": large_median,
            "small_median_duration_s": small_median,
            "duration_ratio": large_median / small_median,
            "note": (
                "Measured at ONE prompt length only. With a single length there "
                "is no way to split this ratio into a fixed startup term and a "
                "per-token term, so it must not be used to scale the large "
                "model to any other length."
            ),
        }

    # ---- projections
    def project(
        model_key: str,
        basis_groups: dict[int, dict[str, Any]],
        fallback_scale: float = 1.0,
        fallback_basis: str = "small_model_affine_fit_times_multiplier",
    ) -> list[dict[str, Any]]:
        """Project record counts per candidate length and assumed slowdown.

        ``fallback_scale`` is consulted only for a length with no retained
        measurement.  It must never silently borrow another model's fit, so the
        caller supplies both the scale and a name saying what was borrowed.
        """
        rows = []
        for length in CANDIDATE_LENGTHS:
            base = basis_groups.get(length)
            for multiplier in TRANSFER_MULTIPLIERS:
                if base is not None:
                    basis = "measured_qwen25_duration_times_multiplier"
                    duration_min = base["prefill_duration_s"]["min"] * multiplier
                    duration_median = base["prefill_duration_s"]["median"] * multiplier
                    duration_max = base["prefill_duration_s"]["max"] * multiplier
                    phases_behind = base["prefill_phase_count"]
                    measured_min_count = base["min_overlap_record_count"]
                else:
                    basis = fallback_basis
                    fitted = (
                        (small_fit["fixed_overhead_s"] + length * small_fit["seconds_per_token"])
                        * fallback_scale
                        * multiplier
                    )
                    duration_min = duration_median = duration_max = fitted
                    phases_behind = 0
                    measured_min_count = None
                worst_case = guaranteed_record_count(duration_min, period_conservative_s)
                typical = guaranteed_record_count(duration_median, period_typical_s)
                best_case = best_case_record_count(duration_max, period_optimistic_s)
                rows.append(
                    {
                        "model_key": model_key,
                        "prompt_tokens": length,
                        "transfer_multiplier": multiplier,
                        "basis": basis,
                        "phases_behind_basis": phases_behind,
                        "projected_duration_s_min": duration_min,
                        "projected_duration_s_median": duration_median,
                        "projected_duration_s_max": duration_max,
                        "guaranteed_record_count_worst_case": worst_case,
                        "record_count_at_typical_period": typical,
                        "record_count_best_case": best_case,
                        "sample_count_margin_worst_case": worst_case - MIN_PHASE_SAMPLES,
                        "measured_qwen25_min_record_count": measured_min_count,
                        "rule_verdicts": {
                            name: {
                                "required_min_count": reading["min_count"],
                                "passes_on_guaranteed_bound": worst_case >= reading["min_count"],
                                "passes_on_measured_qwen25_minimum": (
                                    measured_min_count >= reading["min_count"]
                                    if measured_min_count is not None and multiplier == 1.0
                                    else None
                                ),
                            }
                            for name, reading in RULE_READINGS.items()
                        },
                    }
                )
        return rows

    # The large arm has NO retained measurement at any candidate length, so its
    # rows are the small model's fit scaled by the one duration ratio that was
    # actually measured between the two models (at 128 prompt tokens).  That
    # ratio mixes a fixed startup term with a per-token term and cannot be
    # separated, so the large rows are informational only.  The D-166 rule
    # constrains the SMALL model's members, which is the arm with real evidence.
    large_scale = large_over_small_ratio["duration_ratio"] if large_over_small_ratio else 1.0
    projections = project("small_qwen3_1p7b", small_single) + project(
        "large_qwen3_8b",
        large_single,
        fallback_scale=large_scale,
        fallback_basis=(
            "small_model_affine_fit_times_measured_p128_duration_ratio_times_multiplier"
        ),
    )

    # ---- sensitivity: what slowdown does each length need to clear each reading
    sensitivity = []
    for length in CANDIDATE_LENGTHS:
        base = small_single.get(length)
        if base is None:
            continue
        measured_min_duration = base["prefill_duration_s"]["min"]
        measured_median_duration = base["prefill_duration_s"]["median"]
        for name, reading in RULE_READINGS.items():
            boundaries_needed = reading["min_count"] - 1
            required_conservative = boundaries_needed * period_conservative_s
            required_typical = boundaries_needed * period_typical_s
            sensitivity.append(
                {
                    "prompt_tokens": length,
                    "reading": name,
                    "required_min_count": reading["min_count"],
                    "required_duration_s_guaranteed": required_conservative,
                    "required_duration_s_typical_period": required_typical,
                    "measured_qwen25_min_duration_s": measured_min_duration,
                    "measured_qwen25_median_duration_s": measured_median_duration,
                    "slowdown_needed_on_shortest_member": required_conservative / measured_min_duration,
                    "slowdown_needed_on_median_member": required_typical / measured_median_duration,
                    "clears_already_at_qwen25_rate": base["min_overlap_record_count"] >= reading["min_count"],
                    "note": (
                        "required_duration_s_guaranteed is the phase duration at "
                        "which the guaranteed bound first reaches "
                        "required_min_count using the 99th-percentile record "
                        "period. A shorter typical period reaches it sooner, but "
                        "not in every member, and the rule reads 'every member'."
                    ),
                }
            )

    # ---- contingency
    surviving = {}
    for name, reading in RULE_READINGS.items():
        rows = []
        for length in CANDIDATE_LENGTHS:
            base = small_single.get(length)
            suite = small_suite.get(length)
            rows.append(
                {
                    "prompt_tokens": length,
                    "measured_min_count_single_item_cells": base["min_overlap_record_count"] if base else None,
                    "measured_min_count_suite_items": suite["min_overlap_record_count"] if suite else None,
                    "clears_on_single_item_evidence": (
                        base["min_overlap_record_count"] >= reading["min_count"] if base else None
                    ),
                }
            )
        survivors = [r["prompt_tokens"] for r in rows if r["clears_on_single_item_evidence"]]
        surviving[name] = {
            "required_min_count": reading["min_count"],
            "per_length": rows,
            "lengths_clearing_on_retained_qwen25_evidence": survivors,
            "shortest_clearing_length": survivors[0] if survivors else None,
        }

    return {
        "schema": "joulewise.prefill_resolvability_projection.v1",
        "script_version": "prefill-resolvability-projection/v1",
        "purpose": (
            "Desk pre-registration of prefill-arm resolvability expectations at "
            "512 / 1024 / 2048 prompt tokens for the D-162 G2 shakedown "
            "(D-166 R-2; reviewer-panel item D1). It states projections under a "
            "named transfer assumption, and what each G2 outcome selects. It "
            "does not predict the G2 outcome."
        ),
        "inputs": {
            "corpus_root": str(corpus_root),
            "repo_root": str(repo_root),
            "models_scanned": [SMALL_MODEL_V4, LARGE_MODEL_V4],
            "overlap_predicate_source": "joulewise/reduce.py:196-206 (_in_window_sample_count)",
            "min_phase_samples_source": "joulewise/reduce.py:116",
            "margin_field_source": "joulewise/window_duration_margins.py:801-803, schema-checked at :1091-1093",
            "rule_source": (
                "docs/process_traces/2026-08-28-workload-consult/04-MAGISTRATE-RULING.md R-2; "
                "docs/decision_log.md D-166"
            ),
            "phase_boundary_source": "events.jsonl phase_start / phase_end records with phase == 'prefill'",
        },
        "rule_readings": RULE_READINGS,
        "sampler": sampler,
        "periods_used": {
            "conservative_p99_period_s": period_conservative_s,
            "typical_median_period_s": period_typical_s,
            "optimistic_shortest_period_s": period_optimistic_s,
            "worst_observed_period_s": period_worst_observed_s,
        },
        "measured_evidence": evidence,
        "recorded_label_agreement": label_agreement,
        "bound_validation": bound_validation,
        "duration_model": {
            "small_model_affine_fit": small_fit,
            "large_model_affine_fit": large_fit,
            "large_over_small_duration_ratio": large_over_small_ratio,
        },
        "transfer_assumption": {
            "pair": V5_PAIR,
            "multipliers_swept": list(TRANSFER_MULTIPLIERS),
            "parameter_count_ratio_small": V5_PAIR["small"]["params_b"] / V5_PAIR["small"]["predecessor_params_b"],
            "weight_byte_ratio_small": (
                V5_PAIR["small"]["weights_gb_4bit"] / V5_PAIR["small"]["predecessor_weights_gb_4bit"]
            ),
            "statement": (
                "No Qwen3 prefill duration has been measured on this machine. "
                "Every Qwen3 row below is a Qwen2.5 measurement multiplied by an "
                "assumed slowdown. That is an assumption, not a measurement, and "
                "the G2 shakedown is what replaces it."
            ),
        },
        "projections": projections,
        "sensitivity": sensitivity,
        "contingency": {
            "outcome_name_when_a_phase_fails": "not_resolvable_sample_count",
            "surviving_lengths": surviving,
        },
        "phase_observations": observations,
        "bundle_rows": bundle_rows,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--corpus-root",
        type=Path,
        default=Path("/Users/edr/code/JouleWise"),
        help="directory holding the retained runs*/ corpora (read-only)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="checkout the ruled constants were read from",
    )
    parser.add_argument("--out", type=Path, required=True, help="JSON output path")
    args = parser.parse_args(argv)

    document = build(args.corpus_root.resolve(), args.repo_root.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
