"""The between-session summary (registration §10) and the side-by-side table (§11.1).

For each printed quantity Q and each pack: each session's value of Q,
computed by §9 within that session (block 5's analysed session first, then
the block-6 sessions in registered order); their mean; their sample standard
deviation (divisor n - 1).  Nothing else: no ratio of the deviation to any
half-width, no pooled interval, no test.

Side by side (§11.1): block 5's value, each block-6 session's value, the
difference between the blocks (mean over the block-6 sessions minus block 5's
value) and each block-6 session's own difference from block 5.

A quantity undefined in any of the sessions it would summarise gets no mean
and no deviation, and the sessions that lack it are named: a mean over fewer
sessions would print a different n than §10's without saying why.
"""
from __future__ import annotations

import math

from joulewise.b6.analysis.adapter import SessionAnalysis

LABEL = "between-session summary (n sessions): mean, standard deviation"
INCLUSIVE_LABEL = "including sessions that did not count (n = {n})"


def session_values(analysis: SessionAnalysis) -> dict[str, float | None]:
    """Every printed quantity of one session, contrasts' dbar included (§10)."""
    values = dict(analysis.quantities)
    for contrast_id, contrast in sorted(analysis.contrasts.items()):
        values[f"contrast/{contrast_id}/dbar_j"] = contrast.get("dbar")
    return values


def _finite(value) -> bool:
    return isinstance(value, float) and math.isfinite(value)


def describe(values: list[tuple[str, float | None]]) -> dict:
    """§10 for one quantity: n, mean and sample standard deviation."""
    missing = [session for session, value in values if not _finite(value)]
    record = {"n": len(values), "sessions": [session for session, _ in values]}
    if missing or not values:
        return {**record, "mean": None, "sd": None, "undefined_in": missing}
    numbers = [value for _, value in values]
    mean = math.fsum(numbers) / len(numbers)
    sd = math.sqrt(math.fsum((v - mean) ** 2 for v in numbers) / (len(numbers) - 1)) if len(numbers) > 1 else None
    return {**record, "mean": mean, "sd": sd, "undefined_in": []}


def pack_summary(block5: SessionAnalysis, sessions: list[SessionAnalysis]) -> dict:
    """§10 for every quantity of one pack: block 5 first, then ``sessions``."""
    columns = [("block5", session_values(block5))] + [(s.session_id, session_values(s)) for s in sessions]
    keys = sorted({key for _, values in columns for key in values})
    return {"label": LABEL, "quantities": {
        key: describe([(name, values.get(key)) for name, values in columns]) for key in keys}}


def side_by_side(block5: SessionAnalysis, sessions: list[SessionAnalysis]) -> dict:
    """§11.1 for every quantity of one pack."""
    reference = session_values(block5)
    columns = [(s.session_id, session_values(s)) for s in sessions]
    keys = sorted(set(reference) | {key for _, values in columns for key in values})
    table = {}
    for key in keys:
        b5 = reference.get(key)
        b6 = [(name, values.get(key)) for name, values in columns]
        own = {name: (value - b5 if _finite(value) and _finite(b5) else None) for name, value in b6}
        block6 = describe(b6)
        delta = block6["mean"] - b5 if block6["mean"] is not None and _finite(b5) else None
        table[key] = {"block5": b5 if _finite(b5) else None, "block6": dict(b6),
                      "block6_mean": block6["mean"], "delta": delta, "session_differences": own}
    return {"quantities": table}
