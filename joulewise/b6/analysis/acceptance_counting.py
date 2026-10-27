"""Counting is the loop's, checked against each session's acceptance record.

Registration §4 decides counting; the session's acceptance
(``derived/b6-acceptance.json``, schema ``joulewise.b6_acceptance.v1``,
written by ``joulewise.b6.acceptance``) judged it, and the loop recorded it
(``attempts.jsonl``, ``state.json``).  The analysis reads counting from there
and never from block 5's ``claim_usable`` (RUN_STATE item 53; design §4.6,
§12).  Pipeline audit L5: the run refuses unless the loop's counting equals
the acceptance's for every session, and later unless analysis counting (the
binding's count after the desk exclusion, design §4.6) equals it too.

Only the record's ``schema``, ``session_id`` and ``counting`` are read.
"""
from __future__ import annotations

import json
from pathlib import Path

from joulewise.b6.analysis.census import Census
from joulewise.b6.analysis.session_index import ACCEPTANCE_RECORD

SCHEMA = "joulewise.b6_acceptance.v1"


class CountingRefusal(ValueError):
    def __init__(self, code: str, sessions=()):
        super().__init__(code)
        self.code = code
        self.sessions = tuple(sessions)


def acceptance_counting(index: dict) -> dict[str, bool | None]:
    """Each indexed session's acceptance counting; None where it has none yet."""
    result = {}
    for row in index["sessions"]:
        if row.get("acceptance_record_sha256") is None:
            result[row["session_id"]] = None
            continue
        try:
            record = json.loads((Path(row["archive_root"]) / ACCEPTANCE_RECORD).read_bytes())
            counting = record["counting"]
            if record.get("schema") != SCHEMA or record.get("session_id") != row["session_id"] or type(counting) is not bool:
                raise ValueError()
        except (OSError, ValueError, KeyError, TypeError):
            raise CountingRefusal("acceptance_record_unreadable", [row["session_id"]]) from None
        result[row["session_id"]] = counting
    return result


def require_loop_equals_acceptance(census: Census, index: dict) -> dict[str, bool | None]:
    """Refuse unless the index names the census's sessions and, for each decided
    session, the loop's counting equals the acceptance record's."""
    indexed = [(row["session_id"], row["pack"]) for row in index["sessions"]]
    if sorted(indexed) != sorted((e.session_id, e.pack) for e in census.entries):
        raise CountingRefusal("session_index_differs_from_census")
    accepted = acceptance_counting(index)
    differing = [e.session_id for e in census.entries
                 if e.decided and accepted.get(e.session_id) is not e.counting]
    if differing:
        raise CountingRefusal("b6_counting_records_disagree", differing)
    return accepted


def analysis_counting_problems(census: Census, accepted: dict, analysed: dict) -> list[list[str]]:
    """``[session, code]`` for every analysed session whose analysis counting
    (the binding's count after the desk exclusion) is missing or differs from
    the acceptance counting.  ``analysed`` maps each session that a completed
    unit analysed to the analysis counting that unit reported (None if none).
    Audit L5 requires equality for every session, so a missing value is a
    refusal too, never a pass."""
    problems = []
    for entry in census.entries:
        if entry.session_id not in analysed:
            continue
        value = analysed[entry.session_id]
        if value is None:
            problems.append([entry.session_id, "analysis_counting_not_reported"])
        elif value is not accepted.get(entry.session_id):
            problems.append([entry.session_id, "analysis_counting_differs_from_acceptance"])
    return problems
