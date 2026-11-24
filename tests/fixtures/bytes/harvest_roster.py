"""The one writer of synthetic BYTES harvest rosters (``derived/roster.json``).

The harvest writes a session roster through ``l4_exclusion_inputs`` and
``Harvest.finish`` (``joulewise/b5/harvest.py``). Each member carries
``run_id``, ``stage_id``, ``kind`` and ``units`` and nothing else, so a real
roster names no role. Roles come from the plan walk and reach the export
table (``joulewise/b6/acceptance.py`` ``_stage_roles``).

Every BYTES fixture writes its roster here, through those same harvest
functions. A synthetic roster therefore has the real shape, and
``tests/test_bytes_roster_shape.py`` fails if one carries a key the harvest
does not write (RL-201 §4.2(1) cold review, 2026-11-24).
"""
from __future__ import annotations

from pathlib import Path

from joulewise.b5 import harvest

# Harvest.finish writes the projection without these keys: they are stream
# timing and stay in withheld/.
WITHHELD_KEYS = ("bundles", "chain_started_monotonic_ns")
# l4_exclusion_inputs takes a unit's stratum from its extraction cell's kind:
# a floor family has an absolute cell of repeats and a comparative cell of quads.
CELL_KIND = {"repeat": "absolute", "quad": "comparative"}


def member(run_id, stage_id, units=()):
    """One planned member: units are ``{cell_id, stratum, unit_id}``; a member with units is science."""
    return {"run_id": run_id, "stage_id": stage_id, "units": [dict(unit) for unit in units]}


def document(pack_id, members, *, attempt=1, plan_id=None):
    """The roster document the harvest writes for these planned members, in their order."""
    cells, internal = {}, []
    for planned in members:
        extraction = []
        for unit in planned.get("units") or ():
            kind = CELL_KIND[unit["stratum"]]
            cell_id = f"{unit['cell_id']}/{kind}"
            cells.setdefault(cell_id, {"cell_id": cell_id, "kind": kind, "condition_family_id": unit["cell_id"]})
            extraction.append({"cell_id": cell_id, "unit_kind": unit["stratum"], "unit_id": unit["unit_id"]})
        internal.append({"run_id": planned["run_id"], "stage_id": planned["stage_id"],
                         "kind": "science" if extraction else "auxiliary", "cells": extraction})
    projected, _spans = harvest.l4_exclusion_inputs(
        {"pack_id": pack_id, "cells": list(cells.values()), "members": internal}, {},
        plan_id=pack_id if plan_id is None else plan_id, attempt=attempt)
    return {key: value for key, value in projected.items() if key not in WITHHELD_KEYS}


def write(path, pack_id, members, **kwargs):
    """Write with the harvest's own writer; return the SHA-256 its receipt records."""
    return harvest.write_json_once(Path(path), document(pack_id, members, **kwargs))
