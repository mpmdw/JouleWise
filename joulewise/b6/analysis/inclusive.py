"""The flagged-inclusive index (registration §11.4).

Every collected session is indexed, counting or not.  A non-counting session
is added back to the labelled line when it (i) ran the registered experiment
(no W1, W2, W3 or S1 condition) and (ii) can be computed (at least the
registered minimum of kept units in every stratum, a defined b_op and a
defined drift screen).  Session-level excluding flags P1 to P4 and D1 are
ignored for it; run exclusions still apply (they are inside the per-session
analysis).  Admission reads structure only: codes, counts and verdict words.

Two passes (lead ruling of 2026-10-27 on §12.3 item 3): :func:`pre_admission`
applies (i) from the loop's record, and every session that meets (i), counting
or not, is analysed, because (ii) needs its computed kept units, b_op and drift
screen; :func:`admission` then applies (ii) to those results.  A session
failing (i) is recorded with its structural reason and not analysed.
"""
from __future__ import annotations

from joulewise.b6.analysis.adapter import COMPLETED, SessionAnalysis
from joulewise.b6.analysis.census import SessionEntry

COUNTING, ADDED = "counting", "added"
NOT_HARVESTED, NOT_REGISTERED, NOT_COMPUTABLE, CANDIDATE = (
    "not_harvested", "not_registered_experiment", "not_computable", "candidate")


def _groups(codes, table: dict) -> list[str]:
    present = set(codes)
    return sorted(group for group, members in table.items() if present & set(members))


def pre_admission(entry: SessionEntry, rules: dict) -> tuple[str, list[str]]:
    if entry.counting:
        return COUNTING, []
    if not entry.decided:
        return NOT_HARVESTED, []
    wrong = _groups(entry.codes, rules["not_registered_experiment"])
    if not entry.structure_ok and "S1" not in wrong:
        wrong = sorted(wrong + ["S1"])
    if wrong:
        return NOT_REGISTERED, wrong
    return CANDIDATE, []


def admission(entry: SessionEntry, analysis: SessionAnalysis | None, rules: dict) -> tuple[str, list[str]]:
    decision, reasons = pre_admission(entry, rules)
    if decision != CANDIDATE:
        return decision, reasons
    if analysis is None or analysis.status not in COMPLETED:
        return NOT_COMPUTABLE, ["analysis_not_completed"]
    reasons = []
    if not analysis.b_op_defined:
        reasons.append("b_op_undefined")
    if analysis.drift_screen == "undefined":
        reasons.append("drift_screen_undefined")
    minimum = rules["minimum_kept_units_per_stratum"]
    counts = [n for strata in analysis.kept_units.values() for n in strata.values()]
    if not counts or any(type(n) is not int or n < minimum for n in counts):
        reasons.append("N3")
    return (NOT_COMPUTABLE, reasons) if reasons else (ADDED, [])
