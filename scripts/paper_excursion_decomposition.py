#!/usr/bin/env python3
"""Per-pulse edge-excursion decomposition for the worked calibration capture.

WHAT THIS PRODUCES.  The paper reports one number for the worked capture
``20260722T145535-e941c821``: the calibration bound ``B_fiducial`` = 0.030067931757111657 s.
That bound is a *maximum* over 118 edge quantities (59 commanded pulses, each
with a switch-on edge and a switch-off edge).  A single maximum hides whether
the instrument is off by a repeatable, same-direction amount on every pulse, or
whether it scatters around zero and one unlucky pulse set the maximum.  This
script prints the whole distribution so the two can be told apart.

TWO DIFFERENT PER-EDGE QUANTITIES ARE EMITTED, and they must not be confused:

  1. The **best-fit lag** (``delta_on_s``, ``delta_off_s``): the single on/off
     time shift pair whose predicted power trace matches the observed trace most
     closely.  Signed, in the sense *detected minus commanded* -- a positive
     onset lag means the instrument shows the pulse starting later than it was
     commanded.  This is the quantity that answers "which way, and by how much,
     is the instrument off?"

  2. The **allowed interval** (``onset_residual_lower_s`` .. ``onset_residual_upper_s``
     and the offset pair): the full range of edge shifts the trace cannot rule
     out.  It is wider than the best-fit lag because each power record averages
     roughly a tenth of a second and so cannot pin an edge to a point.  Its
     ``worst excursion`` -- ``max(|lower|, |upper|)`` -- is what actually feeds
     the bound: ``B_fiducial = max over the 118 worst excursions + B_anchor``.

Both are emitted per pulse.  Statements about the *bound* must use quantity 2;
statements about the instrument's *direction of error* use quantity 1.

HOW THE VALUES ARE RE-DERIVED.  The read path mirrors
``scripts/check_paper_replay_fence.py``: the retained ``instrument_evidence.json``
supplies the recorded clock-stamp block and the artifact fingerprints;
``raw/powermetrics.plist`` and ``events.jsonl`` are hash-verified against that
block and handed to ``rederive_detection_from_artifacts`` under the v3 anchor
method.  The pulse rows stored inside the 2026-07-22 evidence file are from the
earlier (v2) anchor estimator and are NEVER read as values here -- only the
primary bytes are.

CALIBRATION GATE.  Before any per-pulse number is written, the re-derivation
must reproduce the two values the draft prints for this capture:
``b_fiducial_s`` = 0.030067931757111657 and ``projection_evaluated_cell_count``
= 122859, as exactly equal 64-bit floats / integers.  Any difference is a hard
stop (exit 2) and no output file is written.

USAGE
    python3 scripts/paper_excursion_decomposition.py \
        --corpus-root /path/to/corpus \
        --out docs/paper/round7/excursion-decomposition.json

``--corpus-root`` is the directory CONTAINING ``runs_window_a_20260722/``, not
the capture directory itself.  The capture is read but never written.

EXIT CODES
    0  the calibration gate held and the data file was written
    2  the calibration gate failed, detection did not converge, or present
       primary artifact bytes disagreed with their retained digest
    3  a required primary artifact could not be located
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

MEMBER_ID = "20260722T145535-e941c821"
SOURCE_DIRECTORY = Path("runs_window_a_20260722") / "instrument_validation" / MEMBER_ID

# The two values the frozen draft prints for this capture (draft-v1.md, the
# evidence comment above Section 2's worked example, and Appendix A.3.6).
DRAFT_B_FIDUCIAL_S = 0.030067931757111657
DRAFT_CELL_COUNT = 122859
EXPECTED_PULSE_COUNT = 59

# Additional roots searched for the raw plist (it is ~88 MB and not in git),
# mirroring scripts/check_paper_replay_fence.py.
BACKUP_ROOTS = (
    Path("/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup"),
)

# Fixed float formatting: milliseconds are reported to this many decimal places
# so the file is byte-reproducible across runs and platforms.  Second-valued
# quantities that the draft prints (the bound, the anchor term) are kept at full
# binary64 repr so they can be compared digit-for-digit with the draft.
MS_DECIMALS = 6


class ArtifactsUnavailable(RuntimeError):
    """The primary custody artifacts are not present on this machine."""


class ArtifactIntegrityMismatch(RuntimeError):
    """Present primary bytes disagree with their retained identity."""


class CalibrationGateFailed(RuntimeError):
    """The re-derivation did not reproduce the draft's printed values."""


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _ms(seconds: float) -> float:
    """Seconds to milliseconds at fixed precision (deterministic output)."""

    return round(seconds * 1000.0, MS_DECIMALS)


def locate_raw_powermetrics(corpus_root: Path, expected_sha256: str) -> bytes:
    """Return the retained raw plist bytes, hash-verified against the evidence."""

    candidates: list[Path] = [
        corpus_root / SOURCE_DIRECTORY / "raw" / "powermetrics.plist"
    ]
    for root in BACKUP_ROOTS:
        if root.is_dir():
            candidates.extend(
                root.glob(f"*/instrument_validation/{MEMBER_ID}/raw/powermetrics.plist")
            )
            candidates.extend(
                root.glob(
                    f"*/*/instrument_validation/{MEMBER_ID}/raw/powermetrics.plist"
                )
            )
    seen: list[str] = []
    for candidate in candidates:
        if not candidate.is_file():
            continue
        raw = candidate.read_bytes()
        if _sha256(raw) == expected_sha256:
            return raw
        seen.append(f"{candidate} (sha256 {_sha256(raw)})")
    if seen:
        raise ArtifactIntegrityMismatch(
            "raw/powermetrics.plist does not match its retained sha256; "
            f"inspected: {seen}"
        )
    raise ArtifactsUnavailable(
        "raw/powermetrics.plist matching sha256 "
        f"{expected_sha256} not found; no candidate paths existed"
    )


def rederive(repository_root: Path, corpus_root: Path) -> dict[str, Any]:
    """Re-derive the detection under the v3 anchor from primary bytes only."""

    sys.path.insert(0, str(repository_root))
    sys.dont_write_bytecode = True

    from joulewise.adapters.powermetrics import (  # noqa: PLC0415
        anchor_records_from_powermetrics,
        parse_powermetrics_records,
    )
    from joulewise.powermetrics_fiducial import (  # noqa: PLC0415
        rederive_detection_from_artifacts,
    )
    from joulewise.uncertainty_evidence import (  # noqa: PLC0415
        CLOCK_METHOD_V3,
        derive_powermetrics_anchor_v3,
        stamp_from_mapping,
    )

    directory = corpus_root / SOURCE_DIRECTORY
    evidence_path = directory / "instrument_evidence.json"
    if not evidence_path.is_file():
        raise ArtifactsUnavailable(f"{evidence_path} is not present")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    hashes = evidence["artifact_sha256"]

    events_path = directory / "events.jsonl"
    if not events_path.is_file():
        raise ArtifactsUnavailable(f"{events_path} is not present")
    events_raw = events_path.read_bytes()
    if _sha256(events_raw) != hashes["events.jsonl"]:
        raise ArtifactIntegrityMismatch(
            "events.jsonl does not match its retained sha256"
        )
    raw = locate_raw_powermetrics(corpus_root, hashes["raw/powermetrics.plist"])

    anchor_block = evidence["clock_anchor"]
    stamps = {
        name: stamp_from_mapping(row)
        for name, row in anchor_block["clock_stamps"].items()
        if isinstance(row, dict)
    }
    derived_anchor = derive_powermetrics_anchor_v3(
        stamps=stamps,
        records=anchor_records_from_powermetrics(parse_powermetrics_records(raw)),
    )
    if derived_anchor.get("status") != "bounded":
        raise CalibrationGateFailed(
            f"re-derived clock anchor is not bounded: {derived_anchor.get('status')!r}"
        )

    detection = rederive_detection_from_artifacts(
        raw, events_raw, anchor_block, anchor_method=CLOCK_METHOD_V3
    )
    return {
        "detection": detection,
        "anchor": derived_anchor,
        "evidence": evidence,
        "events_sha256": hashes["events.jsonl"],
        "raw_sha256": hashes["raw/powermetrics.plist"],
    }


def check_calibration_gate(detection: Any) -> dict[str, Any]:
    """Hard stop unless the draft's two printed values are reproduced exactly."""

    problems: list[str] = []
    if not detection.all_pulses_detected:
        problems.append("re-derived detection did not detect every commanded pulse")
    if detection.reasons:
        problems.append(f"detection carries reasons {list(detection.reasons)}")
    if len(detection.fits) != EXPECTED_PULSE_COUNT:
        problems.append(
            f"pulse count is {len(detection.fits)}, expected {EXPECTED_PULSE_COUNT}"
        )
    if detection.b_fiducial_s is None:
        problems.append("b_fiducial_s is None")
    elif detection.b_fiducial_s != DRAFT_B_FIDUCIAL_S:
        problems.append(
            "b_fiducial_s mismatch: derived "
            f"{detection.b_fiducial_s!r} != draft {DRAFT_B_FIDUCIAL_S!r}"
        )
    if detection.projection_evaluated_cell_count != DRAFT_CELL_COUNT:
        problems.append(
            "projection_evaluated_cell_count mismatch: derived "
            f"{detection.projection_evaluated_cell_count!r} != draft {DRAFT_CELL_COUNT!r}"
        )
    if problems:
        raise CalibrationGateFailed("; ".join(problems))
    return {
        "b_fiducial_s_draft": DRAFT_B_FIDUCIAL_S,
        "b_fiducial_s_derived": detection.b_fiducial_s,
        "b_fiducial_s_matches_exactly": True,
        "projection_evaluated_cell_count_draft": DRAFT_CELL_COUNT,
        "projection_evaluated_cell_count_derived": (
            detection.projection_evaluated_cell_count
        ),
        "projection_evaluated_cell_count_matches_exactly": True,
        "pulse_count": len(detection.fits),
        "all_pulses_detected": True,
    }


# --------------------------------------------------------------------------
# Descriptive statistics.  Everything here is a plain summary of the numbers
# above -- no model is fitted to them, and no significance is claimed.
# --------------------------------------------------------------------------


def _quantile(ordered: list[float], fraction: float) -> float:
    """Linear-interpolated quantile of an already-sorted sample."""

    if not ordered:
        raise ValueError("empty sample")
    if len(ordered) == 1:
        return ordered[0]
    position = fraction * (len(ordered) - 1)
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return ordered[lower_index]
    weight = position - lower_index
    return ordered[lower_index] * (1.0 - weight) + ordered[upper_index] * weight


def describe(values: list[float]) -> dict[str, Any]:
    """Median, spread, extremes, and sign counts for one sample (in ms)."""

    ordered = sorted(values)
    median = statistics.median(ordered)
    q1 = _quantile(ordered, 0.25)
    q3 = _quantile(ordered, 0.75)
    absolute_deviations = sorted(abs(value - median) for value in ordered)
    return {
        "count": len(ordered),
        "min_ms": round(ordered[0], MS_DECIMALS),
        "q1_ms": round(q1, MS_DECIMALS),
        "median_ms": round(median, MS_DECIMALS),
        "q3_ms": round(q3, MS_DECIMALS),
        "max_ms": round(ordered[-1], MS_DECIMALS),
        "iqr_ms": round(q3 - q1, MS_DECIMALS),
        "mean_ms": round(statistics.fmean(ordered), MS_DECIMALS),
        "stdev_ms": round(statistics.stdev(ordered), MS_DECIMALS)
        if len(ordered) > 1
        else 0.0,
        "median_absolute_deviation_ms": round(
            statistics.median(absolute_deviations), MS_DECIMALS
        ),
        "count_positive": sum(1 for value in ordered if value > 0.0),
        "count_negative": sum(1 for value in ordered if value < 0.0),
        "count_zero": sum(1 for value in ordered if value == 0.0),
        "distinct_values_ms": sorted(
            {round(value, MS_DECIMALS) for value in ordered}
        ),
    }


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    """Pearson correlation; ``None`` when either sample has no spread."""

    if len(xs) != len(ys) or len(xs) < 2:
        return None
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    dx = [x - mean_x for x in xs]
    dy = [y - mean_y for y in ys]
    denominator = math.sqrt(sum(v * v for v in dx)) * math.sqrt(sum(v * v for v in dy))
    if denominator == 0.0:
        return None
    return sum(a * b for a, b in zip(dx, dy, strict=True)) / denominator


def _average_ranks(values: list[float]) -> list[float]:
    """Ranks with ties given the average of the positions they span."""

    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    position = 0
    while position < len(order):
        end = position
        while (
            end + 1 < len(order) and values[order[end + 1]] == values[order[position]]
        ):
            end += 1
        average = (position + end) / 2.0 + 1.0
        for index in range(position, end + 1):
            ranks[order[index]] = average
        position = end + 1
    return ranks


def _spearman(xs: list[float], ys: list[float]) -> float | None:
    """Spearman rank correlation: Pearson correlation of the average ranks."""

    if len(xs) != len(ys) or len(xs) < 2:
        return None
    return _pearson(_average_ranks(xs), _average_ranks(ys))


def _ols_slope(xs: list[float], ys: list[float]) -> dict[str, float | None]:
    """Least-squares straight-line fit of ``ys`` against ``xs`` (descriptive)."""

    if len(xs) != len(ys) or len(xs) < 2:
        return {"slope": None, "intercept": None}
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    if denominator == 0.0:
        return {"slope": None, "intercept": None}
    slope = (
        sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
        / denominator
    )
    return {
        "slope": round(slope, MS_DECIMALS),
        "intercept": round(mean_y - slope * mean_x, MS_DECIMALS),
    }


def build_payload(
    derived: dict[str, Any],
    gate: dict[str, Any],
    replay_command: str,
) -> dict[str, Any]:
    """Assemble the deterministic data file from the re-derived detection."""

    detection = derived["detection"]
    anchor = derived["anchor"]

    per_pulse: list[dict[str, Any]] = []
    for fit in detection.fits:
        onset_worst_s = max(
            abs(fit.onset_residual_lower_s), abs(fit.onset_residual_upper_s)
        )
        offset_worst_s = max(
            abs(fit.offset_residual_lower_s), abs(fit.offset_residual_upper_s)
        )
        per_pulse.append(
            {
                "pulse_index": fit.pulse_index,
                "onset_best_fit_lag_ms": _ms(fit.delta_on_s),
                "offset_best_fit_lag_ms": _ms(fit.delta_off_s),
                "onset_allowed_lower_ms": _ms(fit.onset_residual_lower_s),
                "onset_allowed_upper_ms": _ms(fit.onset_residual_upper_s),
                "offset_allowed_lower_ms": _ms(fit.offset_residual_lower_s),
                "offset_allowed_upper_ms": _ms(fit.offset_residual_upper_s),
                "onset_worst_excursion_ms": _ms(onset_worst_s),
                "offset_worst_excursion_ms": _ms(offset_worst_s),
                "amplitude_w": fit.amplitude_w,
            }
        )

    indices = [float(row["pulse_index"]) for row in per_pulse]
    onset_lags = [row["onset_best_fit_lag_ms"] for row in per_pulse]
    offset_lags = [row["offset_best_fit_lag_ms"] for row in per_pulse]
    onset_worst = [row["onset_worst_excursion_ms"] for row in per_pulse]
    offset_worst = [row["offset_worst_excursion_ms"] for row in per_pulse]
    all_worst = onset_worst + offset_worst

    anchor_bound_s = float(anchor["effective_clock_anchor_bound_s"])
    max_worst_ms = max(all_worst)

    return {
        "schema": "joulewise-excursion-decomposition/v1",
        "capture_member_id": MEMBER_ID,
        "capture_relative_path": str(SOURCE_DIRECTORY),
        "replay_command": replay_command,
        "artifact_sha256": {
            "events.jsonl": derived["events_sha256"],
            "raw/powermetrics.plist": derived["raw_sha256"],
        },
        "anchor_method": detection.anchor_method,
        "calibration_gate": gate,
        "bound_terms": {
            "b_fiducial_s": detection.b_fiducial_s,
            "b_anchor_s": anchor_bound_s,
            "max_worst_edge_excursion_ms": round(max_worst_ms, MS_DECIMALS),
            "b_fiducial_ms": round(detection.b_fiducial_s * 1000.0, MS_DECIMALS),
            "b_anchor_ms": (
                round(anchor_bound_s * 1000.0, MS_DECIMALS)
                if anchor_bound_s is not None
                else None
            ),
            "projection_evaluated_cell_count": (
                detection.projection_evaluated_cell_count
            ),
        },
        "per_pulse": per_pulse,
        "summary": {
            "onset_best_fit_lag": describe(onset_lags),
            "offset_best_fit_lag": describe(offset_lags),
            "onset_worst_excursion": describe(onset_worst),
            "offset_worst_excursion": describe(offset_worst),
            "all_118_worst_excursions": describe(all_worst),
        },
        "independence_descriptors": {
            "note": (
                "Descriptive only. No significance test, model, or confidence "
                "statement is attached to any number in this block."
            ),
            "onset_lag_vs_pulse_index": {
                "spearman_rho": (
                    None
                    if (rho := _spearman(indices, onset_lags)) is None
                    else round(rho, MS_DECIMALS)
                ),
                "ols_ms_per_pulse": _ols_slope(indices, onset_lags),
            },
            "offset_lag_vs_pulse_index": {
                "spearman_rho": (
                    None
                    if (rho := _spearman(indices, offset_lags)) is None
                    else round(rho, MS_DECIMALS)
                ),
                "ols_ms_per_pulse": _ols_slope(indices, offset_lags),
            },
            "onset_worst_excursion_vs_pulse_index": {
                "spearman_rho": (
                    None
                    if (rho := _spearman(indices, onset_worst)) is None
                    else round(rho, MS_DECIMALS)
                ),
                "ols_ms_per_pulse": _ols_slope(indices, onset_worst),
            },
            "offset_worst_excursion_vs_pulse_index": {
                "spearman_rho": (
                    None
                    if (rho := _spearman(indices, offset_worst)) is None
                    else round(rho, MS_DECIMALS)
                ),
                "ols_ms_per_pulse": _ols_slope(indices, offset_worst),
            },
            "onset_vs_offset_within_pulse": {
                "best_fit_lag_pearson_r": (
                    None
                    if (r := _pearson(onset_lags, offset_lags)) is None
                    else round(r, MS_DECIMALS)
                ),
                "best_fit_lag_spearman_rho": (
                    None
                    if (rho := _spearman(onset_lags, offset_lags)) is None
                    else round(rho, MS_DECIMALS)
                ),
                "worst_excursion_pearson_r": (
                    None
                    if (r := _pearson(onset_worst, offset_worst)) is None
                    else round(r, MS_DECIMALS)
                ),
                "worst_excursion_spearman_rho": (
                    None
                    if (rho := _spearman(onset_worst, offset_worst)) is None
                    else round(rho, MS_DECIMALS)
                ),
            },
        },
    }


# --------------------------------------------------------------------------
# Figure 4.  A static SVG for the paper: white surface, generic sans-serif,
# no external references, matching the three existing figure sources.  Two
# categorical series carried by hue AND marker shape, so identity survives
# grayscale printing and colour-vision deficiency.  Palette slots 1 and 2 of
# the validated default categorical order.
# --------------------------------------------------------------------------

SVG_WIDTH = 1240
SVG_HEIGHT = 700
PLOT_LEFT = 118.0
# A reserved right gutter carries the three reference-line labels.  Keeping
# them outside the plotting area means no label can ever land on a data mark,
# whatever the numbers turn out to be.
PLOT_RIGHT = 962.0
GUTTER_LEFT = PLOT_RIGHT + 14.0
PLOT_TOP = 150.0
PLOT_BOTTOM = 476.0
Y_MIN_MS = -20.0
Y_MAX_MS = 30.0

INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_GRID = "#ececec"
INK_AXIS = "#9a9a9a"
SERIES_ONSET = "#2a78d6"
SERIES_OFFSET = "#eb6834"


def _x_of(pulse_index: int, pulse_count: int) -> float:
    span = PLOT_RIGHT - PLOT_LEFT
    return PLOT_LEFT + span * pulse_index / (pulse_count - 1)


def _y_of(value_ms: float) -> float:
    span = PLOT_BOTTOM - PLOT_TOP
    return PLOT_BOTTOM - span * (value_ms - Y_MIN_MS) / (Y_MAX_MS - Y_MIN_MS)


def _f(value: float) -> str:
    """Coordinate formatting: two decimals, deterministic across platforms."""

    return f"{value:.2f}"


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(payload: dict[str, Any]) -> str:
    """Render Figure 4 from the same payload that is written to JSON."""

    per_pulse = payload["per_pulse"]
    pulse_count = len(per_pulse)
    onset_summary = payload["summary"]["onset_best_fit_lag"]
    offset_summary = payload["summary"]["offset_best_fit_lag"]
    bound = payload["bound_terms"]
    onset_median = onset_summary["median_ms"]
    offset_median = offset_summary["median_ms"]
    onset_late = onset_summary["count_positive"]
    offset_early = offset_summary["count_negative"]

    worst = max(per_pulse, key=lambda row: row["onset_worst_excursion_ms"])
    worst_index = worst["pulse_index"]

    parts: list[str] = []
    add = parts.append

    add('<?xml version="1.0" encoding="UTF-8"?>')
    add(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" '
        f'height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" '
        'font-family="sans-serif">'
    )
    add(f'<rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" fill="#ffffff"/>')

    # --- Title block -------------------------------------------------------
    add(
        f'<text x="60" y="52" font-size="23" font-weight="600" '
        f'fill="{INK_PRIMARY}">Edge timing excursions of all 59 calibration '
        f"pulses</text>"
    )
    add(
        f'<text x="60" y="80" font-size="14.5" fill="{INK_SECONDARY}">'
        "Measured data from capture "
        f'{_escape(payload["capture_member_id"])}. Each point is a best-fit '
        "lag: how much later (positive) or earlier (negative) the power</text>"
    )
    add(
        f'<text x="60" y="101" font-size="14.5" fill="{INK_SECONDARY}">'
        "trace shows an edge than the moment that edge was commanded. A "
        "switch-on edge is an onset; a switch-off edge is an offset. "
        f"{pulse_count} pulses give {2 * pulse_count} edges.</text>"
    )

    # --- Grid and axes -----------------------------------------------------
    add(f'<g stroke="{INK_GRID}" stroke-width="1">')
    tick_ms = -20
    while tick_ms <= 30:
        y = _y_of(float(tick_ms))
        add(
            f'<line x1="{_f(PLOT_LEFT)}" y1="{_f(y)}" x2="{_f(PLOT_RIGHT)}" '
            f'y2="{_f(y)}"/>'
        )
        tick_ms += 5
    add("</g>")

    add(f'<g stroke="{INK_AXIS}" stroke-width="1.2">')
    add(
        f'<line x1="{_f(PLOT_LEFT)}" y1="{_f(PLOT_TOP)}" x2="{_f(PLOT_LEFT)}" '
        f'y2="{_f(PLOT_BOTTOM)}"/>'
    )
    add("</g>")

    add(f'<g font-size="13" fill="{INK_SECONDARY}" text-anchor="end">')
    tick_ms = -20
    while tick_ms <= 30:
        y = _y_of(float(tick_ms))
        if tick_ms > 0:
            label = f"+{tick_ms}"
        elif tick_ms < 0:
            label = f"−{abs(tick_ms)}"
        else:
            label = "0"
        add(f'<text x="{_f(PLOT_LEFT - 12)}" y="{_f(y + 4.5)}">{label}</text>')
        tick_ms += 5
    add("</g>")

    add(
        f'<text transform="translate(46,{_f((PLOT_TOP + PLOT_BOTTOM) / 2)}) '
        f'rotate(-90)" font-size="14" fill="{INK_SECONDARY}" '
        'text-anchor="middle">excursion (milliseconds)</text>'
    )

    # X ticks: pulse index.
    add(f'<g font-size="13" fill="{INK_SECONDARY}" text-anchor="middle">')
    for tick in (0, 10, 20, 30, 40, 50, pulse_count - 1):
        x = _x_of(tick, pulse_count)
        add(f'<text x="{_f(x)}" y="{_f(PLOT_BOTTOM + 26)}">{tick}</text>')
    add("</g>")
    add(
        f'<text x="{_f((PLOT_LEFT + PLOT_RIGHT) / 2)}" y="{_f(PLOT_BOTTOM + 52)}" '
        f'font-size="14" fill="{INK_SECONDARY}" text-anchor="middle">'
        "pulse index (order of firing within the capture)</text>"
    )

    # --- Zero line: the commanded edge time --------------------------------
    zero_y = _y_of(0.0)
    add(
        f'<line x1="{_f(PLOT_LEFT)}" y1="{_f(zero_y)}" x2="{_f(PLOT_RIGHT)}" '
        f'y2="{_f(zero_y)}" stroke="{INK_PRIMARY}" stroke-width="1.8"/>'
    )
    add(
        f'<text x="{_f(GUTTER_LEFT)}" y="{_f(zero_y + 4.5)}" font-size="12.5" '
        f'fill="{INK_PRIMARY}">commanded</text>'
    )
    add(
        f'<text x="{_f(GUTTER_LEFT)}" y="{_f(zero_y + 20)}" font-size="12.5" '
        f'fill="{INK_PRIMARY}">edge time (0)</text>'
    )

    # --- Median reference lines: the repeatable part of the error ----------
    for median, colour, label in (
        (onset_median, SERIES_ONSET, "onset median"),
        (offset_median, SERIES_OFFSET, "offset median"),
    ):
        y = _y_of(median)
        add(
            f'<line x1="{_f(PLOT_LEFT)}" y1="{_f(y)}" x2="{_f(PLOT_RIGHT)}" '
            f'y2="{_f(y)}" stroke="{colour}" stroke-width="1.6" '
            'stroke-dasharray="9 5"/>'
        )
        sign = "+" if median > 0 else "−"
        add(
            f'<text x="{_f(GUTTER_LEFT)}" y="{_f(y - 4)}" font-size="12.5" '
            f'fill="{INK_SECONDARY}">{label}</text>'
        )
        add(
            f'<text x="{_f(GUTTER_LEFT)}" y="{_f(y + 12)}" font-size="12.5" '
            f'fill="{INK_SECONDARY}">{sign}{abs(median):g} ms</text>'
        )

    # --- Data marks --------------------------------------------------------
    add(f'<g fill="{SERIES_OFFSET}" stroke="#ffffff" stroke-width="1.5">')
    for row in per_pulse:
        x = _x_of(row["pulse_index"], pulse_count)
        y = _y_of(row["offset_best_fit_lag_ms"])
        add(f'<rect x="{_f(x - 4.5)}" y="{_f(y - 4.5)}" width="9" height="9"/>')
    add("</g>")

    add(f'<g fill="{SERIES_ONSET}" stroke="#ffffff" stroke-width="1.5">')
    for row in per_pulse:
        x = _x_of(row["pulse_index"], pulse_count)
        y = _y_of(row["onset_best_fit_lag_ms"])
        add(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="5"/>')
    add("</g>")

    # --- Callout on the pulse that sets the bound --------------------------
    worst_x = _x_of(worst_index, pulse_count)
    worst_y = _y_of(worst["onset_best_fit_lag_ms"])
    add(
        f'<line x1="{_f(worst_x + 14)}" y1="{_f(worst_y - 24)}" '
        f'x2="{_f(worst_x + 3)}" y2="{_f(worst_y - 8)}" '
        f'stroke="{INK_SECONDARY}" stroke-width="1.2"/>'
    )
    add(
        f'<text x="{_f(worst_x + 18)}" y="{_f(worst_y - 28)}" font-size="12.5" '
        f'fill="{INK_SECONDARY}">pulse {worst_index}, '
        f'+{worst["onset_best_fit_lag_ms"]:g} ms — the edge that sets the '
        "published bound</text>"
    )

    # --- Legend ------------------------------------------------------------
    legend_y = PLOT_BOTTOM + 92
    add(
        f'<circle cx="{_f(PLOT_LEFT + 6)}" cy="{_f(legend_y - 4)}" r="5" '
        f'fill="{SERIES_ONSET}" stroke="#ffffff" stroke-width="1.5"/>'
    )
    add(
        f'<text x="{_f(PLOT_LEFT + 20)}" y="{_f(legend_y)}" font-size="13.5" '
        f'fill="{INK_PRIMARY}">onset (switch-on edge) — {onset_late} of '
        f"{pulse_count} are late</text>"
    )
    add(
        f'<rect x="{_f(PLOT_LEFT + 396)}" y="{_f(legend_y - 8.5)}" width="9" '
        f'height="9" fill="{SERIES_OFFSET}" stroke="#ffffff" '
        'stroke-width="1.5"/>'
    )
    add(
        f'<text x="{_f(PLOT_LEFT + 414)}" y="{_f(legend_y)}" font-size="13.5" '
        f'fill="{INK_PRIMARY}">offset (switch-off edge) — {offset_early} of '
        f"{pulse_count} are early</text>"
    )

    # --- Notes -------------------------------------------------------------
    notes = [
        "The dashed lines are each series' median — the part of the error that "
        "repeats from pulse to pulse rather than varying between them.",
        "The published bound is not read off this chart. It comes from the "
        "widest end of each edge's allowed interval: the full range of shifts "
        "the trace cannot rule out, which is",
        "wider than the best fit because each power record averages about a "
        "tenth of a second. That widest end is "
        f'{bound["max_worst_edge_excursion_ms"]:.2f} ms, on pulse '
        f"{worst_index}'s onset;",
        f'adding the {bound["b_anchor_ms"]:.2f} ms clock-anchor term gives the '
        f'published B_fiducial = {bound["b_fiducial_ms"]:.2f} ms. Values here '
        "are shown to two decimals; the data file carries them in full.",
        "Best-fit lags fall on a 0.5 ms grid because the fitting search steps "
        "in 0.5 ms increments. The allowed intervals are continuous.",
    ]
    note_y = legend_y + 32
    for note in notes:
        add(
            f'<text x="{_f(PLOT_LEFT)}" y="{_f(note_y)}" font-size="12.5" '
            f'fill="{INK_SECONDARY}">{_escape(note)}</text>'
        )
        note_y += 19
    add("</svg>")
    return "\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Re-derive the worked capture under the v3 anchor and write the "
            "per-pulse edge-excursion distribution behind B_fiducial."
        )
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="checkout supplying the joulewise package (default: this checkout)",
    )
    parser.add_argument(
        "--corpus-root",
        type=Path,
        required=True,
        help="directory CONTAINING runs_window_a_20260722/ (read, never written)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="path of the JSON data file to write",
    )
    parser.add_argument(
        "--svg",
        type=Path,
        default=None,
        help="optional path for the Figure 4 SVG rendered from the same payload",
    )
    args = parser.parse_args(argv)

    repository_root = args.repository_root.resolve()
    corpus_root = args.corpus_root.resolve()
    replay_command = (
        "python3 scripts/paper_excursion_decomposition.py "
        f"--corpus-root {corpus_root} "
        "--out docs/paper/round7/excursion-decomposition.json"
    )

    try:
        derived = rederive(repository_root, corpus_root)
    except ArtifactsUnavailable as exc:
        print(f"artifacts unavailable: {exc}", file=sys.stderr)
        return 3
    except ArtifactIntegrityMismatch as exc:
        print(f"ARTIFACT INTEGRITY MISMATCH: {exc}", file=sys.stderr)
        return 2

    try:
        gate = check_calibration_gate(derived["detection"])
    except CalibrationGateFailed as exc:
        print(f"CALIBRATION GATE FAILED: {exc}", file=sys.stderr)
        print("no output written", file=sys.stderr)
        return 2

    print(
        "ok   b_fiducial_s: draft="
        f"{DRAFT_B_FIDUCIAL_S!r} derived={derived['detection'].b_fiducial_s!r}"
    )
    print(
        "ok   projection_evaluated_cell_count: draft="
        f"{DRAFT_CELL_COUNT} derived="
        f"{derived['detection'].projection_evaluated_cell_count}"
    )

    payload = build_payload(derived, gate, replay_command)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {args.out}")

    if args.svg is not None:
        args.svg.parent.mkdir(parents=True, exist_ok=True)
        args.svg.write_text(build_svg(payload), encoding="utf-8")
        print(f"wrote {args.svg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
