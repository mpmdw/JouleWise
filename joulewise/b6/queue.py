"""Pure round rotation and pack stopping over structure-only attempts."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime

from joulewise.flags.catalog import EXCLUDE_WINDOW


@dataclass(frozen=True)
class Selection:
    packs: tuple[str, ...]
    round: int


@dataclass(frozen=True)
class Close:
    counts: dict
    short: dict


@dataclass(frozen=True)
class Idle:
    reasons: dict


def rotation(base_order, regs, round_number):
    order = [p for p in base_order if p in regs]
    order += sorted(set(regs) - set(order), key=lambda p: (regs[p].commit_time, p))
    offset = (round_number - 1) % len(order) if order else 0
    return order[offset:] + order[:offset]


def counting_ids(state, pack):
    # Re-harvest corrections live in state, leaving attempts append-only.
    corrections = state.get("reharvested", {})
    return [a["session_id"] for a in state.get("attempts", [])
            if corrections.get(a["session_id"], a["outcomes"]).get(pack, {}).get("status") == "counting"]


def outcome(reg, line, catalog):
    if not line.structure_ok:
        return {"status": "not_counting", "cause": "collection.structure_failed"}
    if line.harvest_rc in (2, 3):
        return {"status": "pending_harvest", "cause": None}
    if line.physics_stop:
        return {"status": "physics_stopped", "cause": line.physics_stop}
    codes = sorted(set(line.window_flags) | set(line.pack_flags.get(reg.pack_id, ())))
    excluded = [c for c in codes if reg.flag_effects.get(c, catalog.effect(c)) == EXCLUDE_WINDOW]
    return {"status": "not_counting", "cause": excluded[0]} if excluded else {"status": "counting", "cause": None}


def pack_state(state, reg):
    return state.get("packs", {}).get(reg.pack_id, {})


def done_reason(state, reg, now):
    count = len(counting_ids(state, reg.pack_id))
    if count >= reg.target_sessions:
        return "target"
    if pack_state(state, reg).get("precision_reached") and count >= reg.minimum_sessions:
        return "precision"
    end = reg.stopping.get("end_t0_before")
    if end and now >= datetime.fromisoformat(end).timestamp():
        return f"short:{count}" if count < reg.minimum_sessions else "end_date"
    return None


def next_session(state, regs, now):
    if not regs:
        return Idle({"registrations": "no_open_packs"})
    cap = state.get("science_minutes_max", 265)
    oversized = {p for p, r in regs.items() if r.session_shape == "modular"
                 and sum(m["est_minutes"] for m in r.modules) > cap}
    eligible = [p for p, r in regs.items() if p not in oversized and not done_reason(state, r, now)
                and pack_state(state, r).get("status", "open") == "open"]
    if not eligible:
        if all(done_reason(state, r, now) for r in regs.values()):
            return Close({p: len(counting_ids(state, p)) for p in regs},
                         {p: len(counting_ids(state, p)) for p, r in regs.items() if done_reason(state, r, now).startswith("short:")})
        return Idle({p: "pack_unit_exceeds_cap" if p in oversized else pack_state(state, r).get("hold_reason")
                     for p, r in regs.items()})
    round_number = state.get("round", 1)
    used = set(state.get("slots", {}).get(str(round_number), ()))
    order = rotation(state.get("base_order", ["alpha", "beta", "gamma"]), regs, round_number)
    available = [p for p in order if p in eligible and p not in used]
    if not available:
        round_number += 1
        order = rotation(state.get("base_order", ["alpha", "beta", "gamma"]), regs, round_number)
        available = [p for p in order if p in eligible]
    lead = available[0]
    chosen = [lead]
    if regs[lead].session_shape == "modular":
        minutes = sum(m["est_minutes"] for m in regs[lead].modules)
        for p in available[1:]:
            r = regs[p]
            cost = sum(m["est_minutes"] for m in r.modules)
            if r.session_shape == "modular" and r.reference_cadence == regs[lead].reference_cadence and minutes + cost <= state.get("science_minutes_max", 265):
                chosen.append(p)
                minutes += cost
    return Selection(tuple(chosen), round_number)


def consume(state, selection):
    state = deepcopy(state)
    state["round"] = selection.round
    slots = state.setdefault("slots", {}).setdefault(str(selection.round), [])
    for p in selection.packs:
        if p not in slots:
            slots.append(p)
            s = state.setdefault("packs", {}).setdefault(p, {})
            s["attempts_since_resume"] = s.get("attempts_since_resume", 0) + 1
    return state


def rotate(state, regs):
    state = deepcopy(state)
    events = []
    for p, reg in regs.items():
        s = state.setdefault("packs", {}).setdefault(p, {})
        if s.get("status", "open") != "open" or len(counting_ids(state, p)) >= reg.target_sessions:
            continue
        history = [state.get("reharvested", {}).get(a["session_id"], a["outcomes"])[p]
                   for a in state.get("attempts", [])[s.get("resumed_at", 0):] if p in a["packs"]]
        failures = ("not_counting", "physics_stopped")
        if len(history) >= 2 and all(h["status"] in failures for h in history[-2:]) and history[-1]["cause"] == history[-2]["cause"]:
            s.update(status="held", hold_reason="same_cause_twice")
            events.append(("same_cause_twice", p))
        elif s.get("attempts_since_resume", 0) >= s.get("attempt_limit", reg.attempts_before_pause):
            s.update(status="paused", hold_reason="attempts")
            events.append(("pack_paused", p))
    return state, events


def resume(state, pack=None, attempts=5):
    if type(attempts) is not int or attempts < 1:
        raise ValueError("attempts must be a positive integer")
    state = deepcopy(state)
    for p, s in state.get("packs", {}).items():
        if pack is None or p == pack:
            s.update(status="open", hold_reason=None, attempts_since_resume=0, attempt_limit=attempts,
                     resumed_at=len(state.get("attempts", [])))
    return state
