"""Read window supports without turning interval means into point samples."""

from __future__ import annotations

import json
import math

from joulewise.align.records import PowerTrace


def _support_edge_quantum_ns(end_ns: int) -> float:
    # The adapter forms start_s = end_s - elapsed_ns/1e9. Subtraction and
    # representation of the shared edge cost <= ulp(end_s) seconds; converting
    # the two versions to ns costs <= two half-ulps of the ns product. Thus
    # their disagreement is bounded by ulp(end_s*1e9) + ulp(end_s)*1e9.
    # At epoch 1.79e9 s this is 256 + 238.42 = 494.42 ns, already priced by
    # the sampler's clock representation/arithmetic and _conversion_error_ns.
    # A snap moves at most quantum*P/1e9 J (1.98e-5 J at 40 W), not a new
    # sensor uncertainty. Derive this in the trace clock, before mapping it.
    end_s = end_ns / 1_000_000_000
    return math.ulp(end_s * 1_000_000_000) + math.ulp(end_s) * 1_000_000_000


def window_supports(
    trace: PowerTrace, *, flags: list[str] | None = None,
) -> tuple[tuple[int, int] | None, ...] | None:
    """Return supports in the trace clock, or None for instantaneous power.

    Apple records retain each native support in sample_support_ns, including
    variable widths. Explicit unknown entries remain unknown. Malformed or
    non-end-stamped supports must never silently select point interpolation.
    Powermetrics edges within their float conversion quantum share one edge;
    flags receives support_edge_snapped:<channel> and its integer snap count.
    The recorded trace and its evidence are never rewritten.
    """
    if trace.unit != "W":
        return None
    try:
        notes = json.loads(trace.notes)
    except (TypeError, ValueError):
        notes = {}
    raw = notes.get("sample_support_ns") if isinstance(notes, dict) else None
    if isinstance(notes, dict) and "sample_support_ns" in notes:
        if not isinstance(raw, list) or len(raw) != len(trace.t_ns):
            raise ValueError("invalid sample_support_ns")
        if trace.source != "powermetrics" and all(support is None for support in raw):
            width = trace.averaging_window_ns
            return (tuple((t-width, t) for t in trace.t_ns)
                    if width is not None and width > 0 else None)
        supports = []
        for end, support in zip(trace.t_ns, raw):
            if support is None:
                supports.append(None)
            elif (isinstance(support, list) and len(support) == 2
                  and all(isinstance(t, int) and not isinstance(t, bool) for t in support)
                  and support[0] < support[1] == end):
                supports.append(tuple(support))
            else:
                raise ValueError("invalid sample_support_ns")
        if trace.source == "powermetrics":
            snapped = 0
            for i in range(1, len(supports)):
                previous, current = supports[i-1], supports[i]
                if previous is None or current is None:
                    continue
                start, end = current
                edge = previous[1]
                if (start != edge and edge < end
                        and abs(start-edge) <= _support_edge_quantum_ns(edge)):
                    supports[i] = (edge, end)
                    snapped += 1
            if snapped and flags is not None:
                flags.extend((f"support_edge_snapped:{trace.channel}",
                              f"support_edge_snap_count:{trace.channel}:{snapped}"))
        return tuple(supports)
    width = trace.averaging_window_ns
    if width is not None and width > 0:
        return tuple((t - width, t) for t in trace.t_ns)
    return None
