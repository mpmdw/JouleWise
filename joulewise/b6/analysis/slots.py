"""Code for the registration slots this driver owns (§14).

S-9 and S-11 are filled in the registration by B6-2
(``lane/2026-10-22-b6-s9-s11`` c37614f71); the driver neither recomputes
nor copies them.  Their consumer, the desk exclusion of §8.3 item 3 (design
§4.6), belongs to the binding, which reports its result as each session's
``analysis_counting``.

* S-15: whole-machine energy per phase.  The definition is design §8 (audit
  B6-7), filled by the lead; this module defines no arithmetic for it.  The
  values come from the adapter under ``whole_machine/`` keys, are summarised
  by §10 like any quantity, carry the registered boundary sentence, and are
  refused for GAMMA, which has no repeat stratum (§9.5 item 5).
* S-16: replay counts beside each new or changed rule of §8, structure only:
  for every code whose effect differs between block 5's sealed catalog and
  block 6's, how many runs and sessions each rule removes on block 5's usable
  sessions.  A rule the replay host cannot evaluate (its inputs are absent
  there) prints "not evaluated", never zero (audit B6-5).
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping

WHOLE_MACHINE_PREFIX = "whole_machine/"
WHOLE_MACHINE_BOUNDARY = "DC input at the USB-C port; the adapter's AC-to-DC loss is not included."
EXCLUDE_WINDOW, EXCLUDE_MEMBER = "EXCLUDE_WINDOW", "EXCLUDE_MEMBER"
NOT_EVALUATED = "not evaluated"


class SlotRefusal(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def s15_quantities(pack: str, quantities: Mapping[str, float | None]) -> dict:
    """S-15's whole-machine values of one session, as the adapter supplied them."""
    machine = {k: v for k, v in quantities.items() if k.startswith(WHOLE_MACHINE_PREFIX)}
    if machine and pack == "gamma":
        raise SlotRefusal("whole_machine_not_given_for_gamma")
    return {"boundary": WHOLE_MACHINE_BOUNDARY, "values": dict(sorted(machine.items()))}


def s16_replay_counts(sessions: Mapping[str, Iterable[Mapping]], block5_catalog, block6_catalog, *,
                      evaluated: Iterable[str] | None = None) -> dict:
    """S-16 over block 5's usable sessions: ``sessions[id]`` lists flag rows
    ``{"code", "run_id"}`` (``run_id`` None for a session-level flag).

    Every code whose effect differs between the catalogs, or that only block 6
    lists, gets the runs and sessions it removes under each rule.  ``evaluated``
    names the codes whose inputs the replay host had; any other changed code
    prints "not evaluated" instead of a count.  Counts only.
    """
    def effect(catalog, code):
        return catalog.effect(code) if code in catalog.codes else None

    changed = sorted(code for code in set(block5_catalog.codes) | set(block6_catalog.codes)
                     if effect(block5_catalog, code) != effect(block6_catalog, code))
    can = set(changed) if evaluated is None else set(evaluated)
    counts = {code: {"block5_effect": effect(block5_catalog, code), "block6_effect": effect(block6_catalog, code),
                     "block5": {"runs": set(), "sessions": set()}, "block6": {"runs": set(), "sessions": set()}}
              for code in changed}
    for session_id, rows in sorted(sessions.items()):
        for row in rows:
            code, run_id = row.get("code"), row.get("run_id")
            if not isinstance(code, str) or (run_id is not None and not isinstance(run_id, str)):
                raise SlotRefusal("replay_flag_row_malformed")
            if code not in counts:
                continue
            item = counts[code]
            for side, rule in (("block5", item["block5_effect"]), ("block6", item["block6_effect"])):
                if rule == EXCLUDE_WINDOW:
                    item[side]["sessions"].add(session_id)
                elif rule == EXCLUDE_MEMBER and run_id is not None:
                    item[side]["runs"].add((session_id, run_id))
    return {code: {"block5_effect": item["block5_effect"], "block6_effect": item["block6_effect"],
                   **{side: ({"runs_removed": len(item[side]["runs"]), "sessions_removed": len(item[side]["sessions"])}
                             if code in can else NOT_EVALUATED) for side in ("block5", "block6")}}
            for code, item in counts.items()}
