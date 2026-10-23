"""Read window supports without turning interval means into point samples."""

from __future__ import annotations

import json

from joulewise.align.records import PowerTrace


def window_supports(trace: PowerTrace) -> tuple[tuple[int, int] | None, ...] | None:
    """Return supports in the trace clock, or None for instantaneous power.

    Apple records retain each native support in sample_support_ns, including
    variable widths. Explicit unknown entries remain unknown. Malformed or
    non-end-stamped supports must never silently select point interpolation.
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
        return tuple(supports)
    width = trace.averaging_window_ns
    if width is not None and width > 0:
        return tuple((t - width, t) for t in trace.t_ns)
    return None
