"""Vendored test oracle for lane L9-ENV-3 (do not import from joulewise).

The function below is copied byte for byte from lane L9-ENV-2's patched
``joulewise/reduce.py`` (commit e1b3a0510, file sha256 ``d37f731c...``).  That
patch was never merged; it serves only as the oracle for the analysis-side
clamp in ``joulewise/whole_window.py``.  ``tests/test_whole_window_inverted_corner_clamp.py``
proves that substituting this function into origin/main's reduce.py rebuilds
exactly the e1b3a0510 bytes.
"""

from __future__ import annotations

import math

from joulewise.bundle_read import TracePoint, Window
from joulewise.reduce import (
    ANCHOR_SHIFT_METHOD,
    _anchor_shift_envelope,
    _shift_energy_j,
)

SOURCE_COMMIT = "e1b3a0510"
SOURCE_PATH = "joulewise/reduce.py"
SOURCE_FILE_SHA256 = (
    "d37f731c07116c025a7670043e13c6a0f37bee74d2217ae08d160f4ac0074f8f"
)
FUNCTION_NAME = "_corner_composed_anchor_shift_envelope"
FUNCTION_SOURCE_SHA256 = (
    "31ff400ab51881ec64c71e55d044d05f5b7a69d16d4ab351ae7883931772bf6e"
)


def _corner_composed_anchor_shift_envelope(
    contributions: list[tuple[list[TracePoint], list[Window]]],
    bundle_bound_s: float | None,
    fiducial_bound_s: float | None,
    wall_minus_monotonic_span_s: float = 0.0,
) -> dict[str, float | str] | None:
    """Current-wire envelope over common shift and two independent edges.

    With nonnegative power, integrated energy is monotonically nonincreasing
    in every window start and monotonically nondecreasing in every window
    stop.  Therefore the extrema over independent ``eps_on``/``eps_off``
    intervals occur at their four corners.  At each corner the remaining
    ``delta_common`` dimension is evaluated by the existing breakpoint-exact
    scanner above, so no continuous common-shift extremum is skipped.
    """

    if (
        bundle_bound_s is None
        or fiducial_bound_s is None
        or not math.isfinite(bundle_bound_s)
        or not math.isfinite(fiducial_bound_s)
        or bundle_bound_s < 0.0
        or fiducial_bound_s < 0.0
        or not math.isfinite(wall_minus_monotonic_span_s)
        or wall_minus_monotonic_span_s < 0.0
        or not contributions
        or any(
            not curve
            or not windows
            or any(point.power_w < 0.0 for point in curve)
            for curve, windows in contributions
        )
    ):
        return None

    # G7(c), current-wire only: evaluate interval association after removing a
    # shared epoch.  Adding a 2026-scale epoch before a ~50 us anchor delta can
    # round the delta itself by several microseconds; relative coordinates keep
    # the same physical overlaps without that avoidable float association.
    # Frozen 0.5.1/0.6.1 never call this current-wire corner evaluator.
    origin_s = contributions[0][0][0].t
    contributions = [
        (
            [
                TracePoint(
                    t=point.t - origin_s,
                    power_w=point.power_w,
                    support_start_s=(
                        point.support_start_s - origin_s
                        if point.support_start_s is not None
                        else None
                    ),
                    support_end_s=(
                        point.support_end_s - origin_s
                        if point.support_end_s is not None
                        else None
                    ),
                )
                for point in curve
            ],
            [
                Window(
                    start_s=window.start_s - origin_s,
                    end_s=window.end_s - origin_s,
                )
                for window in windows
            ],
        )
        for curve, windows in contributions
    ]

    point_j = _shift_energy_j(contributions, 0.0)
    common_only = _anchor_shift_envelope(contributions, bundle_bound_s)
    # The wall-minus-monotonic span is an independent per-edge clock error
    # just like the fiducial emission lag, so it widens the corner offsets;
    # corner evaluation stays exact under the same monotonicity argument and
    # is tighter than the frozen v2 arm's 2*span*maxP additive term.
    edge_bound_s = fiducial_bound_s + wall_minus_monotonic_span_s
    corner_envelopes: list[dict[str, float | str]] = []
    for eps_on_s in (-edge_bound_s, edge_bound_s):
        for eps_off_s in (-edge_bound_s, edge_bound_s):
            corner_contributions: list[tuple[list[TracePoint], list[Window]]] = []
            for curve, windows in contributions:
                shifted_windows = [
                    Window(
                        start_s=window.start_s + eps_on_s,
                        end_s=window.end_s + eps_off_s,
                    )
                    for window in windows
                ]
                # Ed's 2026-10-30 ruling (lane L9-ENV-2): a window shorter
                # than 2*edge_bound inverts at the (+edge, -edge) corner.
                # The admissible set then contains an empty interval, so
                # with nonnegative power the true minimum contribution is
                # 0 J: clamp to a zero-length window at the shifted midpoint
                # (inside the original window) instead of dropping the
                # envelope.  Non-inverted windows are untouched.
                shifted_windows = [
                    Window(
                        start_s=(window.start_s + window.end_s) / 2.0,
                        end_s=(window.start_s + window.end_s) / 2.0,
                    )
                    if window.end_s < window.start_s
                    else window
                    for window in shifted_windows
                ]
                corner_contributions.append((curve, shifted_windows))
            corner = _anchor_shift_envelope(corner_contributions, bundle_bound_s)
            if corner is None:
                return None
            corner_envelopes.append(corner)

    if common_only is None or not corner_envelopes:
        return None
    lower_j = min(float(envelope["lower_j"]) for envelope in corner_envelopes)
    upper_j = max(float(envelope["upper_j"]) for envelope in corner_envelopes)
    if not (
        math.isfinite(point_j)
        and math.isfinite(lower_j)
        and math.isfinite(upper_j)
        and lower_j <= point_j <= upper_j
    ):
        return None
    independent_edge_bound_j = max(
        0.0,
        float(common_only["lower_j"]) - lower_j,
        upper_j - float(common_only["upper_j"]),
    )
    return {
        "method": ANCHOR_SHIFT_METHOD,
        "anchor_bound_s": bundle_bound_s + edge_bound_s,
        "point_j": point_j,
        "lower_j": lower_j,
        "upper_j": upper_j,
        "max_abs_delta_j": max(point_j - lower_j, upper_j - point_j),
        "wall_minus_monotonic_independent_edge_span_s": (
            wall_minus_monotonic_span_s
        ),
        "independent_edge_shift_bound_j": independent_edge_bound_j,
    }
