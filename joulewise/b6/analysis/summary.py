"""The between-session summary (registration §10) and the side-by-side table (§11.1).

For each printed quantity Q and each pack: each session's value of Q,
computed by §9 within that session (block 5's analysed session first, then
the block-6 sessions in registered order); their mean; their sample standard
deviation (divisor n - 1).  Nothing else: no ratio of the deviation to any
half-width, no pooled interval, no test.

Side by side (§11.1): block 5's value, each block-6 session's value, the
difference between the blocks (mean over the block-6 sessions minus block 5's
value) and each block-6 session's own difference from block 5.

A session without a value of Q (for example a contrast that is not estimable)
is left out of Q's summary and listed with its reason; n counts the sessions
that have a value.  With fewer than two values the summary prints "not
computable (n < 2)".  The registration is silent on a missing value; this is
the lead's ruling of 2026-10-27 (report B6-AN-1, author decision AD-1): §10 is
descriptive and no claim rests on it, so withholding it would hide information.
"""
from __future__ import annotations

import math

from joulewise.b6.analysis.adapter import SessionAnalysis

LABEL = "between-session summary (n sessions): mean, standard deviation"
INCLUSIVE_LABEL = "including sessions that did not count (n = {n})"
INCLUSIVE_NONE = "including sessions that did not count: none"
NOT_COMPUTABLE = "not computable (n < 2)"


def session_values(analysis: SessionAnalysis) -> dict[str, float | None]:
    """Every printed quantity of one session, contrasts' dbar included (§10)."""
    values = dict(analysis.quantities)
    for contrast_id, contrast in sorted(analysis.contrasts.items()):
        values[f"contrast/{contrast_id}/dbar_j"] = contrast.get("dbar")
    return values


def missing_reason(analysis: SessionAnalysis, key: str) -> str:
    """Why a session has no value of ``key``.  Restricted (it may be an outcome word)."""
    if key in analysis.reasons:
        return analysis.reasons[key]
    if key.startswith("contrast/") and key.endswith("/dbar_j"):
        outcome = analysis.contrasts.get(key.split("/")[1], {}).get("outcome")
        if outcome is not None:
            return outcome
    if key not in session_values(analysis):
        return "quantity_absent"
    return "value_undefined"


def _finite(value) -> bool:
    return isinstance(value, float) and math.isfinite(value)


def _split(rows):
    present = [(name, value) for name, value, _ in rows if _finite(value)]
    missing = [{"session": name, "reason": reason} for name, value, reason in rows if not _finite(value)]
    return present, missing


def describe(rows: list[tuple[str, float | None, str | None]]) -> dict:
    """§10 for one quantity over ``(session, value, reason if missing)`` rows."""
    present, missing = _split(rows)
    record = {"n": len(present), "sessions": [name for name, _ in present], "missing": missing}
    if len(present) < 2:
        return {**record, "mean": None, "sd": None, "note": NOT_COMPUTABLE}
    numbers = [value for _, value in present]
    mean = math.fsum(numbers) / len(numbers)
    sd = math.sqrt(math.fsum((v - mean) ** 2 for v in numbers) / (len(numbers) - 1))
    return {**record, "mean": mean, "sd": sd, "note": None}


def _rows(key, sessions: list[SessionAnalysis], names=None):
    names = names or [s.session_id for s in sessions]
    return [(name, session_values(s).get(key), missing_reason(s, key)) for name, s in zip(names, sessions)]


def _keys(sessions: list[SessionAnalysis]) -> list[str]:
    return sorted({key for s in sessions for key in session_values(s)})


def pack_summary(block5: SessionAnalysis, sessions: list[SessionAnalysis], keys=None) -> dict:
    """§10 for each quantity of one pack (``keys``, else every quantity the
    sessions carry): block 5 first, then ``sessions``."""
    columns = [block5] + list(sessions)
    names = ["block5"] + [s.session_id for s in sessions]
    keys = _keys(columns) if keys is None else sorted(keys)
    return {"label": LABEL, "quantities": {key: describe(_rows(key, columns, names)) for key in keys}}


def side_by_side(block5: SessionAnalysis, sessions: list[SessionAnalysis], keys=None) -> dict:
    """§11.1 for each quantity of one pack.  The block-6 mean is over the
    block-6 sessions with a value; the sessions without one are listed."""
    table = {}
    for key in (_keys([block5] + list(sessions)) if keys is None else sorted(keys)):
        b5 = session_values(block5).get(key)
        b5 = b5 if _finite(b5) else None
        present, missing = _split(_rows(key, sessions))
        mean = math.fsum(v for _, v in present) / len(present) if present else None
        table[key] = {"block5": b5, "block5_missing": None if b5 is not None else missing_reason(block5, key),
                      "block6": dict(present), "block6_missing": missing, "block6_n": len(present),
                      "block6_mean": mean, "delta": mean - b5 if mean is not None and b5 is not None else None,
                      "session_differences": {name: (v - b5 if b5 is not None else None) for name, v in present}}
    return {"quantities": table}
