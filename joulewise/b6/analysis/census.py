"""Which block-6 sessions exist and which count, from the loop's acceptance.

Registration §4 decides counting; the session loop applies it and appends one
line per attempt to ``<loop root>/attempts.jsonl`` (``joulewise.b6.loop``).
Re-harvest corrections live in ``state.json`` under ``reharvested``.  This
module reads only those two files.  It never opens a harvest's
``exclusions.json``: block 5's ``claim_usable`` there can disagree with
block 6's §8.2 (RUN_STATE item 53: r2-gamma carries ``claim_usable: false``
from ``neg8.midpoint_lost_primary``, a rule §8.2 drops, and counts).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from joulewise.b6 import queue

CENSUS_SCHEMA = "joulewise.b6_session_census.v1"
REPLICATION_PACKS = ("alpha", "beta", "gamma")
# Statuses written by joulewise.b6.queue.outcome for an attempt whose harvest
# has not decided it; such a session has no harvested bytes to analyse.
UNDECIDED = frozenset(("pending_harvest", "pending_registration"))


class CensusRefusal(ValueError):
    """A malformed loop record; ``code`` is a structure token."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class SessionEntry:
    session_id: str
    pack: str
    round: int
    status: str
    cause: str | None
    counting: bool
    structure_ok: bool
    physics_stop: str | None
    codes: tuple[str, ...]
    t0: int = 0                # integer epoch seconds (structure); orders ties in pairing

    @property
    def decided(self) -> bool:
        return self.status not in UNDECIDED


@dataclass(frozen=True)
class Census:
    entries: tuple[SessionEntry, ...]
    closed: bool

    def pack(self, pack: str) -> tuple[SessionEntry, ...]:
        return tuple(e for e in self.entries if e.pack == pack)

    def counting(self, pack: str) -> tuple[SessionEntry, ...]:
        return tuple(e for e in self.pack(pack) if e.counting)

    def get(self, session_id: str, pack: str | None = None) -> SessionEntry:
        found = [e for e in self.entries if e.session_id == session_id and (pack is None or e.pack == pack)]
        if len(found) != 1:
            raise CensusRefusal("session_not_in_census")
        return found[0]


def order_key(entry: SessionEntry) -> tuple:
    """Registered order: pack order of the registration, then round, then t0."""
    return (REPLICATION_PACKS.index(entry.pack), entry.round, entry.t0, entry.session_id)


def _strings(value) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)) or not all(isinstance(v, str) for v in value):
        raise CensusRefusal("attempt_line_malformed")
    return tuple(value)


def census_from_state(state: dict, *, packs=REPLICATION_PACKS) -> Census:
    """Build the census from a loop state that carries its ``attempts``."""
    attempts = state.get("attempts")
    if not isinstance(attempts, list):
        raise CensusRefusal("attempts_absent")
    corrections = state.get("reharvested", {})
    if not isinstance(corrections, dict):
        raise CensusRefusal("reharvested_malformed")
    seen = set()
    entries = []
    for attempt in attempts:
        try:
            t0 = attempt.get("t0", 0)
            session_id, round_number = attempt["session_id"], attempt["round"]
            attempt_packs, outcomes, line = attempt["packs"], attempt["outcomes"], attempt["line"]
            structure_ok = attempt["structure_ok"]
        except (TypeError, KeyError):
            raise CensusRefusal("attempt_line_malformed") from None
        if (not isinstance(session_id, str) or not session_id or type(round_number) is not int
                or type(t0) not in (int, float) or isinstance(t0, bool)
                or round_number < 1 or type(structure_ok) is not bool or not isinstance(line, dict)
                or not isinstance(outcomes, dict)):
            raise CensusRefusal("attempt_line_malformed")
        if session_id in seen:
            raise CensusRefusal("attempt_session_duplicated")
        seen.add(session_id)
        current = corrections.get(session_id, outcomes)
        for pack in _strings(attempt_packs):
            if pack not in packs:
                continue
            outcome = current.get(pack) if isinstance(current, dict) else None
            if not isinstance(outcome, dict) or not isinstance(outcome.get("status"), str):
                raise CensusRefusal("attempt_outcome_malformed")
            pack_flags = line.get("pack_flags", {})
            if not isinstance(pack_flags, dict):
                raise CensusRefusal("attempt_line_malformed")
            codes = set(_strings(line.get("excluding_reasons"))) | set(_strings(line.get("window_flags")))
            codes |= set(_strings(pack_flags.get(pack)))
            physics_stop = line.get("physics_stop")
            if physics_stop is not None and not isinstance(physics_stop, str):
                raise CensusRefusal("attempt_line_malformed")
            entries.append(SessionEntry(
                session_id=session_id, pack=pack, round=round_number, status=outcome["status"],
                cause=outcome.get("cause"),
                # The loop's own reading of its acceptance decides counting.
                counting=session_id in queue.counting_ids(state, pack),
                structure_ok=structure_ok, physics_stop=physics_stop, codes=tuple(sorted(codes)), t0=int(t0)))
    return Census(tuple(sorted(entries, key=order_key)), closed=state.get("state") == "DONE")


def load_census(loop_root: Path, *, packs=REPLICATION_PACKS) -> Census:
    """Read ``attempts.jsonl`` and ``state.json`` of a loop root, nothing else."""
    root = Path(loop_root)
    try:
        lines = (root / "attempts.jsonl").read_text(encoding="utf-8").splitlines()
        attempts = [json.loads(line) for line in lines if line.strip()]
        state_path = root / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    except (OSError, UnicodeError, ValueError):
        raise CensusRefusal("loop_record_unreadable") from None
    if not isinstance(state, dict):
        raise CensusRefusal("loop_record_unreadable")
    return census_from_state({**state, "attempts": attempts}, packs=packs)


def structure_record(census: Census) -> dict:
    """The census as structure: identities, rounds, status words, counting."""
    return {"schema_version": CENSUS_SCHEMA, "closed": census.closed,
            "sessions": [{"session_id": e.session_id, "pack": e.pack, "round": e.round, "t0": e.t0,
                          "status": e.status, "counting": e.counting, "structure_ok": e.structure_ok}
                         for e in census.entries]}
