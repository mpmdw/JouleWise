"""``night/window.journal.jsonl``: the window lifecycle as appended transitions (RL-108 side branch).

NOT FOR MERGE. Built under RL-108's side-branch conditions; adoption needs a research-lead ruling.

One writer function, ``append``. It is called by the night driver at five transitions:

=================  ==========================================================  =========================
to                 where                                                       facts (structure only)
=================  ==========================================================  =========================
DriverStarted      ``run_night._run_night``, after the first census line       none
ChainOpen          after ``chain.started`` is claimed and before the chain is  none
                   spawned (``run_night._run_night``; ``b5.driver``)
ChainExited        ``run_night._record_chain_exit``, after ``chain.exited``    exit_code, launch_failed,
                   (written only once the chain group is proven gone)          reaped_by
ResultWritten      ``run_night._write_result``, after ``result.json``          verdict, chain_outcome,
                                                                               chain_exit_code, chain_exit
Delivered or       ``run_night._finish_reporting``, after ``courier.json``     sent
DeadmanTail
=================  ==========================================================  =========================

RL-108 condition 4: no write inside a member. Members run only inside the chain's process group, between
``chain.started`` and ``chain.exited``. ``append`` refuses (returns False, writes nothing) whenever that span
may be open: ``chain.started`` exists with a recorded identity and ``chain.exited`` does not. The single
exception is ``ChainOpen`` itself, admitted only while ``chain.started`` is still the empty claim, i.e. before
any chain process exists. So a night whose chain termination is unproven gets no line after ``ChainOpen``.
There is no activity during members to list.

The journal is a derived trace, never an input: no gate, verdict, harvest, engine or recompute reads it, and
a failed append never changes the night (``append`` never raises). Reasons and messages are never copied in;
facts are the fixed keys above.
"""
from __future__ import annotations

import json
import os
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

SCHEMA = "joulewise.window_journal.v1"
NAME = "window.journal.jsonl"
STATES = ("DriverStarted", "ChainOpen", "ChainExited", "ResultWritten", "Delivered", "DeadmanTail")
FACT_KEYS = frozenset({"exit_code", "launch_failed", "reaped_by", "verdict", "chain_outcome",
                       "chain_exit_code", "chain_exit", "sent"})
CHAIN_EXIT_KEYS = frozenset({"contract", "word", "class", "declared"})
_SCALARS = (str, int, float, bool, type(None))


def member_span_may_be_open(night_dir: Path) -> bool:
    """True when a chain process may exist that has not been proven gone (fail closed on any error)."""
    started, exited = Path(night_dir) / "chain.started", Path(night_dir) / "chain.exited"
    try:
        if not os.path.lexists(started):
            return False
        if os.path.lexists(exited):
            return False
        return True
    except OSError:
        return True


def _claim_is_empty(night_dir: Path) -> bool:
    try:
        return os.lstat(Path(night_dir) / "chain.started").st_size == 0
    except OSError:
        return False


def _clean_facts(facts: Mapping[str, Any] | None) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, value in (facts or {}).items():
        if key not in FACT_KEYS:
            raise ValueError(f"window journal fact not allowed: {key}")
        if key == "chain_exit":
            if value is not None and not (isinstance(value, Mapping) and set(value) == CHAIN_EXIT_KEYS
                                          and all(isinstance(v, _SCALARS) for v in value.values())):
                raise ValueError("window journal chain_exit malformed")
            value = None if value is None else dict(value)
        elif not isinstance(value, _SCALARS):
            raise ValueError(f"window journal fact not a scalar: {key}")
        clean[key] = value
    return clean


def _last_transition(path: Path) -> tuple[str | None, int]:
    try:
        lines = path.read_bytes().splitlines()
    except FileNotFoundError:
        return None, 0
    last = json.loads(lines[-1]) if lines else {}
    return (last.get("to") if isinstance(last, dict) else None), len(lines)


def append(night_dir: Path, to: str, *, writer: str, facts: Mapping[str, Any] | None = None) -> bool:
    """Append one transition; False (nothing written) when refused or on any failure. Never raises."""
    try:
        night_dir = Path(night_dir)
        if to not in STATES:
            raise ValueError(f"window journal state unknown: {to}")
        if to == "ChainOpen":
            if not _claim_is_empty(night_dir) or os.path.lexists(night_dir / "chain.exited"):
                return False
        elif member_span_may_be_open(night_dir):
            return False
        path = night_dir / NAME
        previous, count = _last_transition(path)
        line = {"schema": SCHEMA, "sequence": count + 1, "from": previous, "to": to, "writer": writer,
                "epoch_s": time.time(), "monotonic_ns": time.monotonic_ns(), "facts": _clean_facts(facts)}
        payload = (json.dumps(line, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            written = os.write(descriptor, payload)
            if written != len(payload):
                return False
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return True
    except Exception:  # noqa: BLE001 - the journal is a trace; it never changes the night
        return False


def read(night_dir: Path) -> list[dict[str, Any]]:
    """Parse the journal strictly (tests and the Air-side replay; never a gate)."""
    rows = []
    for number, raw in enumerate((Path(night_dir) / NAME).read_bytes().splitlines(), 1):
        row = json.loads(raw)
        if (not isinstance(row, dict) or row.get("schema") != SCHEMA or row.get("sequence") != number
                or row.get("to") not in STATES or (rows and row.get("from") != rows[-1]["to"])
                or (not rows and row.get("from") is not None)):
            raise ValueError(f"window journal line {number} malformed")
        _clean_facts(row.get("facts"))
        rows.append(row)
    return rows
