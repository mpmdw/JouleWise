"""Joint measured-curve envelope for an adjacent prefill/decode boundary.

The ordinary reducer emits a marginal energy envelope for each phase.  Those
two envelopes are useful for statements about either phase alone, but they do
not retain the geometry of their shared interior boundary.  This module keeps
that geometry explicit for desk analysis: one displacement moves the nominal
prefill stop and decode start together, so energy transferred out of one phase
is transferred into the other (apart from any measured gap between the two
markers).

Only interval-support traces are admitted.  On such a trace each phase energy
is piecewise linear in the boundary displacement.  Evaluating the displacement
limits and every point where a shifted boundary crosses a measured support
edge therefore gives the exact curve without assuming an unmeasured waveform.
The helper is diagnostic only; it does not change reducer summary bytes or
license a claim estimator.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from joulewise.bundle_read import TracePoint, Window
from joulewise.reduce import _integrate


PHASE_BOUNDARY_METHOD = "shared_prefill_decode_boundary_sweep_v1"


class PhaseBoundaryError(ValueError):
    """The supplied measured curve cannot support the joint sweep."""


@dataclass(frozen=True)
class Interval:
    """Closed numeric interval."""

    lower: float
    upper: float


@dataclass(frozen=True)
class PhaseBoundaryPoint:
    """One point on the one-parameter phase-allocation curve."""

    boundary_shift_s: float
    prefill_energy_j: float
    decode_energy_j: float
    total_phase_energy_j: float
    prefill_share: float
    normalized_decode_minus_prefill: float


@dataclass(frozen=True)
class PhaseBoundaryEnvelope:
    """Joint curve and its scalar projections.

    ``normalized_decode_minus_prefill`` is the signed phase asymmetry
    ``(decode - prefill) / (decode + prefill)``.  It is ``1 - 2 *
    prefill_share`` and therefore has no unit.
    """

    method: str
    boundary_bound_s: float
    point: PhaseBoundaryPoint
    prefill_energy_j: Interval
    decode_energy_j: Interval
    joint_total_phase_energy_j: Interval
    independent_box_total_phase_energy_j: Interval
    joint_prefill_share: Interval
    independent_box_prefill_share: Interval
    joint_normalized_decode_minus_prefill: Interval
    independent_box_normalized_decode_minus_prefill: Interval
    curve: tuple[PhaseBoundaryPoint, ...]


def _finite(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


def _interval(values: list[float]) -> Interval:
    return Interval(lower=min(values), upper=max(values))


def phase_boundary_envelope(
    curve: list[TracePoint],
    prefill_window: Window,
    decode_window: Window,
    boundary_bound_s: float,
    independent_prefill_energy_j: Interval,
    independent_decode_energy_j: Interval,
) -> PhaseBoundaryEnvelope:
    """Re-integrate two adjacent phases over one shared boundary displacement.

    The nominal marker gap, if any, is preserved: a displacement ``d`` uses
    ``prefill.end + d`` and ``decode.start + d``.  The outer phase edges do not
    move.  ``boundary_bound_s`` is a caller-selected sensitivity range; this
    helper does not assert that it isolates one physical error component.

    The two ``independent_*`` intervals must be the reducer's independently
    emitted phase envelopes.  They are intentionally not inferred from the
    shared-boundary sweep: the mission comparison is between the new joint
    projection and the reducer's existing marginal box.
    """

    if not _finite(boundary_bound_s) or float(boundary_bound_s) < 0.0:
        raise PhaseBoundaryError("boundary_bound_s must be finite and nonnegative")
    bound = float(boundary_bound_s)
    for name, interval in (
        ("prefill", independent_prefill_energy_j),
        ("decode", independent_decode_energy_j),
    ):
        if (
            not isinstance(interval, Interval)
            or not _finite(interval.lower)
            or not _finite(interval.upper)
            or interval.lower < 0.0
            or interval.lower > interval.upper
        ):
            raise PhaseBoundaryError(
                f"independent {name} energy interval must be finite, "
                "nonnegative, and ordered"
            )
    window_values = (
        prefill_window.start_s,
        prefill_window.end_s,
        decode_window.start_s,
        decode_window.end_s,
    )
    if not all(_finite(value) for value in window_values):
        raise PhaseBoundaryError("phase window edges must be finite")
    if not (
        prefill_window.start_s < prefill_window.end_s
        <= decode_window.start_s
        < decode_window.end_s
    ):
        raise PhaseBoundaryError(
            "one ordered, nonoverlapping prefill/decode window pair is required"
        )
    if (
        prefill_window.end_s - bound <= prefill_window.start_s
        or decode_window.start_s + bound >= decode_window.end_s
    ):
        raise PhaseBoundaryError("the boundary sweep would collapse a phase window")
    if not curve:
        raise PhaseBoundaryError("a nonempty interval-support curve is required")

    support_edges: set[float] = set()
    for point in curve:
        if (
            not _finite(point.t)
            or not _finite(point.power_w)
            or point.power_w < 0.0
            or not _finite(point.support_start_s)
            or not _finite(point.support_end_s)
            or float(point.support_end_s) <= float(point.support_start_s)
        ):
            raise PhaseBoundaryError(
                "every trace point must have nonnegative power and finite positive interval support"
            )

    # Match the current reducer's association rule: subtract one shared epoch
    # before adding millisecond-scale boundary displacements.  This preserves
    # overlap geometry while avoiding avoidable rounding at 2026-scale epoch
    # timestamps.
    origin_s = curve[0].t
    curve = [
        TracePoint(
            t=point.t - origin_s,
            power_w=point.power_w,
            support_start_s=float(point.support_start_s) - origin_s,
            support_end_s=float(point.support_end_s) - origin_s,
        )
        for point in curve
    ]
    prefill_window = Window(
        start_s=prefill_window.start_s - origin_s,
        end_s=prefill_window.end_s - origin_s,
    )
    decode_window = Window(
        start_s=decode_window.start_s - origin_s,
        end_s=decode_window.end_s - origin_s,
    )
    for point in curve:
        support_edges.add(float(point.support_start_s))
        support_edges.add(float(point.support_end_s))

    if (
        min(support_edges) > prefill_window.start_s
        or max(support_edges) < decode_window.end_s
    ):
        raise PhaseBoundaryError("the measured curve does not cover both outer edges")

    shifts = {-bound, 0.0, bound}
    for edge in support_edges:
        for nominal_boundary in (
            prefill_window.end_s,
            decode_window.start_s,
        ):
            shift = edge - nominal_boundary
            if -bound <= shift <= bound:
                shifts.add(shift)

    points: list[PhaseBoundaryPoint] = []
    for shift in sorted(shifts):
        prefill_j = _integrate(
            curve,
            prefill_window.start_s,
            prefill_window.end_s + shift,
        )
        decode_j = _integrate(
            curve,
            decode_window.start_s + shift,
            decode_window.end_s,
        )
        total_j = math.fsum((prefill_j, decode_j))
        if not all(math.isfinite(value) for value in (prefill_j, decode_j, total_j)):
            raise PhaseBoundaryError("the measured-curve integral is nonfinite")
        if total_j <= 0.0:
            raise PhaseBoundaryError("phase share is undefined for nonpositive total energy")
        share = prefill_j / total_j
        points.append(
            PhaseBoundaryPoint(
                boundary_shift_s=shift,
                prefill_energy_j=prefill_j,
                decode_energy_j=decode_j,
                total_phase_energy_j=total_j,
                prefill_share=share,
                normalized_decode_minus_prefill=1.0 - 2.0 * share,
            )
        )

    point = next(candidate for candidate in points if candidate.boundary_shift_s == 0.0)
    prefill = _interval([candidate.prefill_energy_j for candidate in points])
    decode = _interval([candidate.decode_energy_j for candidate in points])
    joint_total = _interval([candidate.total_phase_energy_j for candidate in points])
    joint_share = _interval([candidate.prefill_share for candidate in points])
    joint_asymmetry = _interval(
        [candidate.normalized_decode_minus_prefill for candidate in points]
    )

    box_total = Interval(
        lower=math.fsum(
            (
                independent_prefill_energy_j.lower,
                independent_decode_energy_j.lower,
            )
        ),
        upper=math.fsum(
            (
                independent_prefill_energy_j.upper,
                independent_decode_energy_j.upper,
            )
        ),
    )
    box_lower_denominator = math.fsum(
        (
            independent_prefill_energy_j.lower,
            independent_decode_energy_j.upper,
        )
    )
    box_upper_denominator = math.fsum(
        (
            independent_prefill_energy_j.upper,
            independent_decode_energy_j.lower,
        )
    )
    if box_lower_denominator <= 0.0 or box_upper_denominator <= 0.0:
        raise PhaseBoundaryError(
            "independent marginal box has undefined phase-share corners"
        )
    box_share = Interval(
        lower=independent_prefill_energy_j.lower / box_lower_denominator,
        upper=independent_prefill_energy_j.upper / box_upper_denominator,
    )
    return PhaseBoundaryEnvelope(
        method=PHASE_BOUNDARY_METHOD,
        boundary_bound_s=bound,
        point=point,
        prefill_energy_j=prefill,
        decode_energy_j=decode,
        joint_total_phase_energy_j=joint_total,
        independent_box_total_phase_energy_j=box_total,
        joint_prefill_share=joint_share,
        independent_box_prefill_share=box_share,
        joint_normalized_decode_minus_prefill=joint_asymmetry,
        independent_box_normalized_decode_minus_prefill=Interval(
            lower=1.0 - 2.0 * box_share.upper,
            upper=1.0 - 2.0 * box_share.lower,
        ),
        curve=tuple(points),
    )
