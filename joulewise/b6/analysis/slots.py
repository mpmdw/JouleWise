"""Code for the registration slots whose values come later (§14).

Each function computes a slot from its registered source.  The values are
filled by automation on the measurement Mac, never by a seat: every input
here is restricted (smoke phase durations, flag rows of block-5 sessions) and
every output that carries a number is restricted too.

* S-11: T_phase per pack and target phase, the longest target-phase duration
  among the pack's non-claim smoke runs (§14 S-11).
* S-9: P* = F_min / (4 × T_phase) per pack and phase, F_min = 1.9 J (S-10).
* S-15: whole-machine energy per phase.  §9.5 item 5 carries block 5's
  definition, which its S-15 commit fixes.  No such definition exists at
  ``adapter.L9_TARGET_COMMIT`` (L9 has only B5-PLAN §8.2's member-level
  cross-check), so this module defines no arithmetic for it: the values come
  from the adapter under ``whole_machine/`` keys, are summarised by §10 like
  any quantity, and are refused for GAMMA, which has no repeat stratum.
* S-16: replay counts beside each new or changed rule of §8, structure only:
  for every code whose effect differs between block 5's sealed catalog and
  block 6's, how many runs and sessions each rule removes on block 5's
  usable sessions.
"""
from __future__ import annotations

import math
from collections.abc import Iterable, Mapping

F_MIN_J = 1.9                      # S-10, registered by the cold gate of 2026-10-17
TARGET_PHASES = ("decode", "prefill-p2048")
WHOLE_MACHINE_PREFIX = "whole_machine/"
WHOLE_MACHINE_BOUNDARY = "DC input at the USB-C port; the adapter's AC-to-DC loss is not included."
EXCLUDE_WINDOW, EXCLUDE_MEMBER = "EXCLUDE_WINDOW", "EXCLUDE_MEMBER"


class SlotRefusal(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def s11_phase_lengths(rows: Iterable[Mapping]) -> dict[str, dict[str, float]]:
    """S-11 from smoke rows ``{"pack", "phase", "duration_s", "claim": False}``.

    Only non-claim smoke runs of a target phase count; the longest wins when
    they differ.  A pack with no smoke run of a target phase has no T_phase
    for it (the slot stays open), never a default.
    """
    lengths: dict[str, dict[str, float]] = {}
    for row in rows:
        if row.get("claim") is not False:
            raise SlotRefusal("smoke_row_not_marked_non_claim")
        duration = row.get("duration_s")
        if (not isinstance(row.get("pack"), str) or row.get("phase") not in TARGET_PHASES
                or not isinstance(duration, float) or not math.isfinite(duration) or duration <= 0):
            raise SlotRefusal("smoke_row_malformed")
        phases = lengths.setdefault(row["pack"], {})
        phases[row["phase"]] = max(phases.get(row["phase"], 0.0), duration)
    return {pack: dict(sorted(phases.items())) for pack, phases in sorted(lengths.items())}


def s9_power_lines(phase_lengths: Mapping[str, Mapping[str, float]], *, f_min_j: float = F_MIN_J) -> dict:
    """S-9: P* = F_min / (4 × T_phase) in watts, per pack and phase."""
    return {pack: {phase: f_min_j / (4.0 * length) for phase, length in sorted(phases.items())}
            for pack, phases in sorted(phase_lengths.items())}


def s15_quantities(pack: str, quantities: Mapping[str, float | None]) -> dict:
    """S-15's whole-machine values of one session, as the adapter supplied them."""
    machine = {k: v for k, v in quantities.items() if k.startswith(WHOLE_MACHINE_PREFIX)}
    if machine and pack == "gamma":
        raise SlotRefusal("whole_machine_not_given_for_gamma")
    return {"boundary": WHOLE_MACHINE_BOUNDARY, "values": dict(sorted(machine.items()))}


def s16_replay_counts(sessions: Mapping[str, Iterable[Mapping]], block5_catalog, block6_catalog) -> dict:
    """S-16 over block 5's usable sessions: ``sessions[id]`` lists flag rows
    ``{"code", "run_id"}`` (``run_id`` None for a session-level flag).

    For each code whose effect differs between the catalogs, or that only
    block 6 lists, count the runs and sessions it removes under each rule.
    Counts only; the replay reads codes, never a value.
    """
    def effect(catalog, code):
        return catalog.effect(code) if code in catalog.codes else None

    counts: dict[str, dict] = {}
    for session_id, rows in sorted(sessions.items()):
        for row in rows:
            code, run_id = row.get("code"), row.get("run_id")
            if not isinstance(code, str) or (run_id is not None and not isinstance(run_id, str)):
                raise SlotRefusal("replay_flag_row_malformed")
            before, after = effect(block5_catalog, code), effect(block6_catalog, code)
            if before == after:
                continue
            item = counts.setdefault(code, {"block5_effect": before, "block6_effect": after,
                                            "block5": {"runs": set(), "sessions": set()},
                                            "block6": {"runs": set(), "sessions": set()}})
            for side, rule in (("block5", before), ("block6", after)):
                if rule == EXCLUDE_WINDOW:
                    item[side]["sessions"].add(session_id)
                elif rule == EXCLUDE_MEMBER and run_id is not None:
                    item[side]["runs"].add((session_id, run_id))
    return {code: {"block5_effect": item["block5_effect"], "block6_effect": item["block6_effect"],
                   **{side: {"runs_removed": len(item[side]["runs"]), "sessions_removed": len(item[side]["sessions"])}
                      for side in ("block5", "block6")}}
            for code, item in sorted(counts.items())}
