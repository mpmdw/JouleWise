"""Authenticated, immutable units of the block-5 exclusions function.

This reader opens only the exclusions and roster outputs. Full records belong
in restricted custody; ``to_structure_record`` is the pre-release projection.
It neither opens bundles nor re-applies exclusions at analysis time.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from joulewise.flags.catalog import CatalogError, catalog_from_bytes
from .archive import ArchiveHandle
from .windows import AnalysisRefusal, AnalysedWindow, freeze

SCHEMA = "joulewise.b5_kept_units.v1"
CATALOG_PATH = Path(__file__).resolve().parents[2] / "configs/campaigns/v5_claim_25g83/flag_catalog.json"


def _strict_json(raw: bytes, code: str) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError()
            result[key] = value
        return result

    def number(text):
        value = float(text)
        if not math.isfinite(value):
            raise ValueError()
        return value

    def constant(_text):
        raise ValueError()

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_float=number, parse_constant=constant)
        if not isinstance(value, dict):
            raise ValueError()
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise AnalysisRefusal(code) from None


def _strings(value: Any) -> bool:
    return isinstance(value, list) and all(type(x) is str and x for x in value) and len(set(value)) == len(value)


def _count(value: Any) -> bool:
    return type(value) is int and value >= 0


@dataclass(frozen=True)
class Unit:
    cell_id: str
    stratum: str
    unit_id: str
    run_ids: tuple[str, ...]
    positions: tuple[int, ...]
    stage_ids: tuple[str | None, ...]


@dataclass(frozen=True)
class DroppedUnit(Unit):
    codes: tuple[str, ...]
    families: tuple[str, ...]


@dataclass(frozen=True)
class CellKeptUnits:
    cell_id: str
    target: bool
    planned: Mapping[str, int]
    minimum: Mapping[str, int]
    kept: Mapping[str, tuple[Unit, ...]]
    dropped: tuple[DroppedUnit, ...]
    n_r: int
    n_b: int


@dataclass(frozen=True)
class ReportedCellKept:
    cell: CellKeptUnits
    kept_repeat_ordinals: tuple[int, ...]
    removed_repeat_ordinals: tuple[int, ...]
    kept_quad_ordinals: tuple[tuple[int, ...], ...]
    removed_quad_ordinals: tuple[tuple[int, ...], ...]


def _unit_record(unit: Unit) -> dict:
    result = {"cell_id": unit.cell_id, "stratum": unit.stratum, "unit_id": unit.unit_id,
              "run_ids": list(unit.run_ids), "positions": list(unit.positions), "stage_ids": list(unit.stage_ids)}
    if isinstance(unit, DroppedUnit):
        result.update(codes=list(unit.codes), families=list(unit.families))
    return result


@dataclass(frozen=True)
class KeptUnits:
    window: AnalysedWindow
    exclusions_sha256: str
    roster_sha256: str
    catalog_sha256: str
    cells: Mapping[str, CellKeptUnits]
    flags_by_family: Mapping[str, int]
    structure_codes: Mapping[str, int]
    sensitivity_label: str | None = None

    def cell(self, cell_id: str) -> CellKeptUnits:
        try:
            return self.cells[cell_id]
        except (KeyError, TypeError):
            raise AnalysisRefusal("exclusions_cell_unknown") from None

    def kept_run_ids(self, cell_id: str, stratum: str | None = None) -> frozenset[str]:
        cell = self.cell(cell_id)
        strata = cell.kept if stratum is None else {stratum: cell.kept.get(stratum, ())}
        return frozenset(run for units in strata.values() for unit in units for run in unit.run_ids)

    def is_kept(self, cell_id: str, run_id: str) -> bool:
        cell = self.cell(cell_id)
        if run_id in self.kept_run_ids(cell_id):
            return True
        if any(run_id in unit.run_ids for unit in cell.dropped):
            return False
        raise AnalysisRefusal("exclusions_member_unknown")

    def removed_run_ids(self, cell_id: str | None = None) -> frozenset[str]:
        cells = self.cells.values() if cell_id is None else (self.cell(cell_id),)
        return frozenset(run for cell in cells for unit in cell.dropped for run in unit.run_ids)

    def for_floor_cell(self, spec_cell: Mapping[str, Any]) -> tuple[CellKeptUnits, str]:
        try:
            stratum = {"absolute": "repeat", "comparative": "quad"}[spec_cell["kind"]]
            cell = self.cell(spec_cell["condition_family_id"])
        except (KeyError, TypeError):
            raise AnalysisRefusal("exclusions_plan_mismatch") from None
        if stratum not in cell.kept:
            raise AnalysisRefusal("exclusions_plan_mismatch")
        return cell, stratum

    def for_reported_cell(self, spec: Mapping[str, Any], index: int) -> ReportedCellKept:
        try:
            if type(index) is not int or index < 0:
                raise ValueError()
            absolute, repeat = self.for_floor_cell(spec["cells"][2 * index])
            comparative, quad = self.for_floor_cell(spec["cells"][2 * index + 1])
            if absolute.cell_id != comparative.cell_id or repeat != "repeat" or quad != "quad":
                raise ValueError()
        except (KeyError, IndexError, TypeError, ValueError):
            raise AnalysisRefusal("exclusions_plan_mismatch") from None
        cell = absolute
        all_units = [unit for units in cell.kept.values() for unit in units] + list(cell.dropped)
        repeats = sorted((u for u in all_units if u.stratum == "repeat"), key=lambda u: u.positions)
        quads = sorted((u for u in all_units if u.stratum == "quad"), key=lambda u: u.positions)
        if len(repeats) != 10 or len(quads) != 10:
            raise AnalysisRefusal("exclusions_plan_mismatch")
        dropped = {(u.stratum, u.unit_id) for u in cell.dropped}
        def ordinals(units, removed, quad=False):
            return tuple(tuple(range(11 + 4*i, 15 + 4*i)) if quad else i + 1
                         for i, u in enumerate(units) if ((u.stratum, u.unit_id) in dropped) == removed)
        return ReportedCellKept(cell, ordinals(repeats, False), ordinals(repeats, True),
                                ordinals(quads, False, True), ordinals(quads, True, True))

    def for_contrast(self, contrast_id: str) -> CellKeptUnits:
        cell = self.cell(contrast_id)
        if set(cell.kept) != {"quad"}:
            raise AnalysisRefusal("exclusions_plan_mismatch")
        return cell

    def stop_if_member_code_on_kept_unit(self, cell_id: str, run_id: str, code: str,
                                       *, p42_precheck: bool = False) -> None:
        """The caller identifies a precheck; p42 permits no other gate exception."""
        if self.is_kept(cell_id, run_id):
            if p42_precheck is True and not self.cell(cell_id).target and "p42" in cell_id.split("-"):
                return
            raise AnalysisRefusal("member_code_on_kept_unit")

    def require_verdict_membership(self, bundle_ids: Sequence[str]) -> None:
        require_kept_members_in_verdict(self, bundle_ids)

    def _changed_units(self, cell_id, unit_ids, label, restore):
        if not isinstance(label, str) or not label:
            raise AnalysisRefusal("exclusions_plan_mismatch")
        cell = self.cell(cell_id)
        wanted = frozenset(unit_ids)
        candidates = list(cell.dropped) if restore else [u for rows in cell.kept.values() for u in rows]
        if wanted - {u.unit_id for u in candidates}:
            raise AnalysisRefusal("exclusions_plan_mismatch")
        kept = {s: list(rows) for s, rows in cell.kept.items()}
        dropped = list(cell.dropped)
        for unit in candidates:
            if unit.unit_id not in wanted:
                continue
            if restore:
                dropped.remove(unit)
                kept[unit.stratum].append(Unit(unit.cell_id, unit.stratum, unit.unit_id,
                                              unit.run_ids, unit.positions, unit.stage_ids))
            else:
                kept[unit.stratum].remove(unit)
                dropped.append(DroppedUnit(unit.cell_id, unit.stratum, unit.unit_id, unit.run_ids,
                                           unit.positions, unit.stage_ids, (), ()))
        kept = freeze({s: tuple(sorted(rows, key=lambda u: u.unit_id)) for s, rows in kept.items()})
        changed = replace(cell, kept=kept, dropped=tuple(sorted(dropped, key=lambda u: (u.stratum, u.unit_id))),
                          n_r=len(kept.get("repeat", ())), n_b=len(kept.get("quad", ())))
        return replace(self, cells=freeze({**self.cells, cell_id: changed}), sensitivity_label=label)

    def without_units(self, cell_id, unit_ids, *, label) -> KeptUnits:
        """A labelled descriptive view; never mutate the primary exclusions."""
        return self._changed_units(cell_id, unit_ids, label, False)

    def with_units_restored(self, cell_id, unit_ids, *, label) -> KeptUnits:
        return self._changed_units(cell_id, unit_ids, label, True)

    def to_record(self) -> dict:
        """Restricted custody only: contains unit/member identifiers and codes."""
        return {"schema_version": SCHEMA, "pack": self.window.pack, "plan_id": self.window.plan_id,
                "attempt": self.window.attempt, "harvest_pin": self.window.harvest_pin,
                "exclusions_sha256": self.exclusions_sha256, "roster_sha256": self.roster_sha256,
                "catalog_sha256": self.catalog_sha256, "sensitivity_label": self.sensitivity_label,
                "cells": {cid: {"target": c.target, "planned": dict(c.planned), "minimum": dict(c.minimum),
                    "n_r": c.n_r, "n_b": c.n_b,
                    "kept": {s: [_unit_record(u) for u in rows] for s, rows in c.kept.items()},
                    "dropped": [_unit_record(u) for u in c.dropped]} for cid, c in self.cells.items()}}

    def to_structure_record(self) -> dict:
        """P9(b)(2) allowlist; never copy unknown fields from an input record."""
        return {"pack": self.window.pack, "plan_id": self.window.plan_id, "attempt": self.window.attempt,
                "verdict": self.window.record.verdict, "claim_usable": self.window.record.claim_usable,
                "sensitivity_label": self.sensitivity_label,
                "exclusions_sha256": self.exclusions_sha256, "roster_sha256": self.roster_sha256,
                "catalog_sha256": self.catalog_sha256, "harvest_record_sha256": self.window.harvest_record_sha256,
                "flags_by_family": dict(self.flags_by_family), "flags_by_code": dict(self.structure_codes),
                "cells": {cid: {"n_r": c.n_r, "n_b": c.n_b} for cid, c in self.cells.items()}}


def require_kept_members_in_verdict(kept_units: KeptUnits, bundle_ids: Sequence[str]) -> None:
    """J3 tripwire, pure: the writer may not omit a kept science member."""
    # A bare string would be read as a set of characters, and None or a generator has no stable membership.
    if (isinstance(bundle_ids, (str, bytes)) or not isinstance(bundle_ids, (Sequence, Mapping, set, frozenset))
            or any(not isinstance(item, str) or not item for item in bundle_ids)):
        raise AnalysisRefusal("verdict_membership_invalid")
    membership = frozenset(bundle_ids)
    for cell in kept_units.cells.values():
        for units in cell.kept.values():
            for unit in units:
                for run_id in unit.run_ids:
                    if run_id not in membership:
                        raise AnalysisRefusal(f"kept_member_outside_verdict_membership:{run_id}")


def load_kept_units(archive: ArchiveHandle, *, sealed_catalog_sha256: str,
                    planned_units: Mapping[str, Mapping[str, Mapping[str, Sequence[str]]]]) -> KeptUnits:
    # 1. Both byte strings come exclusively through the authenticated handle.
    exclusions_raw = archive.output_bytes("derived/exclusions.json")
    roster_raw = archive.output_bytes("derived/roster.json")
    # 2. Parse strictly, but allow the pins' additive top-level keys.
    document = _strict_json(exclusions_raw, "exclusions_schema_invalid")
    roster = _strict_json(roster_raw, "exclusions_roster_mismatch")
    if document.get("release_blocked") is not False:
        raise AnalysisRefusal("attempt_release_blocked")
    if (document.get("schema_version") != "joulewise.exclusions.v1"
            or document.get("claim_usable") is not True or document.get("reasons") != []
            or document.get("unclassified") != []):
        raise AnalysisRefusal("exclusions_schema_invalid")
    # 3. The local catalog is itself authenticated against the supplied seal digest.
    if document.get("catalog_sha256") != sealed_catalog_sha256:
        raise AnalysisRefusal("exclusions_catalog_mismatch")
    try:
        catalog_raw = CATALOG_PATH.read_bytes()
        if hashlib.sha256(catalog_raw).hexdigest() != sealed_catalog_sha256:
            raise AnalysisRefusal("exclusions_catalog_mismatch")
        _strict_json(catalog_raw, "exclusions_catalog_mismatch")
        catalog = catalog_from_bytes(catalog_raw)
    except (OSError, CatalogError):
        raise AnalysisRefusal("exclusions_catalog_mismatch") from None
    # 4. An attempt id is an integer, never a coercible string or bool.
    if any(type(row.get("attempt")) is not int or row.get("attempt") != archive.record["attempt"]
           or row.get("plan_id") != archive.record["plan_id"] for row in (document, roster)):
        raise AnalysisRefusal("exclusions_attempt_mismatch")
    # 5. Count/list accounting, before any roster or spec comparison.
    cells = document.get("cells")
    if not isinstance(cells, list) or not cells:
        raise AnalysisRefusal("exclusions_cell_inconsistent")
    cell_ids = set()
    for cell in cells:
        if (not isinstance(cell, dict) or type(cell.get("cell_id")) is not str or not cell["cell_id"]
                or cell["cell_id"] in cell_ids or type(cell.get("target")) is not bool):
            raise AnalysisRefusal("exclusions_cell_inconsistent")
        cell_ids.add(cell["cell_id"])
        if (any(not isinstance(cell.get(key), dict) for key in ("planned", "minimum", "n_kept", "kept_units"))
                or not isinstance(cell.get("dropped_units"), list)):
            raise AnalysisRefusal("exclusions_cell_inconsistent")
        strata = set(cell["planned"])
        if (not strata or strata - {"repeat", "quad"}
                or any(set(cell[key]) != strata for key in ("minimum", "n_kept", "kept_units"))):
            raise AnalysisRefusal("exclusions_cell_inconsistent")
        dropped = {s: [] for s in strata}
        for unit in cell["dropped_units"]:
            if (not isinstance(unit, dict) or type(unit.get("stratum")) is not str or unit["stratum"] not in strata
                    or type(unit.get("unit_id")) is not str or not unit["unit_id"]
                    or not _strings(unit.get("codes")) or not unit["codes"]):
                raise AnalysisRefusal("exclusions_cell_inconsistent")
            dropped[unit["stratum"]].append(unit["unit_id"])
        for s in strata:
            kept = cell["kept_units"][s]
            if (not _strings(kept) or len(set(dropped[s])) != len(dropped[s]) or set(kept) & set(dropped[s])
                    or not _count(cell["planned"][s]) or cell["planned"][s] != len(kept) + len(dropped[s])
                    or not _count(cell["n_kept"][s]) or cell["n_kept"][s] != len(kept)
                    or not _count(cell["minimum"][s]) or cell["minimum"][s] < catalog.cell_unit_minimum):
                raise AnalysisRefusal("exclusions_cell_inconsistent")
        if any(type(cell.get(key)) is not int or cell[key] != len(cell["kept_units"].get(s, ()))
               for key, s in (("n_repeats", "repeat"), ("n_quads", "quad"))):
            raise AnalysisRefusal("exclusions_cell_inconsistent")
    # 6. Reconstruct units in roster order, including auxiliary members' positions.
    roster_units = {}
    member_ids = set()
    roster_cells = roster.get("cells")
    if (roster.get("schema") != "joulewise.b5_harvest_roster.v1"
            or roster.get("pack_id") != archive.window.pack_id
            or not isinstance(roster_cells, list) or not isinstance(roster.get("members"), list)):
        raise AnalysisRefusal("exclusions_roster_mismatch")
    specs = {}
    for spec in roster_cells:
        if (not isinstance(spec, dict) or type(spec.get("cell_id")) is not str or spec["cell_id"] in specs
                or type(spec.get("target", True)) is not bool or not _strings(spec.get("strata", ["quad"]))):
            raise AnalysisRefusal("exclusions_roster_mismatch")
        specs[spec["cell_id"]] = spec
    if set(specs) != cell_ids:
        raise AnalysisRefusal("exclusions_roster_mismatch")
    for position, member in enumerate(roster["members"]):
        if (not isinstance(member, dict) or type(member.get("run_id")) is not str or not member["run_id"]
                or member["run_id"] in member_ids or not isinstance(member.get("units", []), list)
                or member.get("stage_id") is not None and type(member["stage_id"]) is not str):
            raise AnalysisRefusal("exclusions_roster_mismatch")
        member_ids.add(member["run_id"])
        seen = set()
        for unit in member.get("units", []):
            if (not isinstance(unit, dict) or any(type(unit.get(k)) is not str or not unit[k]
                                               for k in ("cell_id", "stratum", "unit_id"))):
                raise AnalysisRefusal("exclusions_roster_mismatch")
            key = (unit["cell_id"], unit["stratum"], unit["unit_id"])
            if key in seen or key[0] not in specs or key[1] not in ("repeat", "quad"):
                raise AnalysisRefusal("exclusions_roster_mismatch")
            seen.add(key)
            roster_units.setdefault(key, []).append((member["run_id"], position, member.get("stage_id")))
    result = {}
    universe = {}
    for cell in cells:
        cid = cell["cell_id"]
        if (cell["target"] != specs[cid].get("target", True)
                or set(cell["planned"]) != (set(specs[cid].get("strata", ["quad"]))
                                           | {key[1] for key in roster_units if key[0] == cid})):
            raise AnalysisRefusal("exclusions_roster_mismatch")
        units = {}
        for key, members in roster_units.items():
            if key[0] != cid:
                continue
            if len(members) != {"repeat": 1, "quad": 4}[key[1]]:
                raise AnalysisRefusal("exclusions_roster_mismatch")
            units[key[1:]] = Unit(cid, *key[1:], tuple(m[0] for m in members),
                                 tuple(m[1] for m in members), tuple(m[2] for m in members))
        listed = {(s, uid) for s, ids in cell["kept_units"].items() for uid in ids}
        listed.update((u["stratum"], u["unit_id"]) for u in cell["dropped_units"])
        if listed != set(units):
            raise AnalysisRefusal("exclusions_roster_mismatch")
        dropped_units = []
        for dropped in cell["dropped_units"]:
            unit = units[dropped["stratum"], dropped["unit_id"]]
            # compute() sorts dropped run_ids lexically, independently of positions.
            if (not _strings(dropped.get("run_ids")) or sorted(dropped["run_ids"]) != sorted(unit.run_ids)
                    or dropped.get("positions") != list(unit.positions)
                    or any(type(p) is not int for p in dropped["positions"])
                    or any(code not in catalog.codes for code in dropped["codes"])):
                raise AnalysisRefusal("exclusions_roster_mismatch")
            families = tuple(sorted({catalog.entry(code)["family"] for code in dropped["codes"]}))
            dropped_units.append(DroppedUnit(unit.cell_id, unit.stratum, unit.unit_id, unit.run_ids,
                                             unit.positions, unit.stage_ids, tuple(dropped["codes"]), families))
        kept = freeze({s: tuple(units[s, uid] for uid in sorted(ids)) for s, ids in cell["kept_units"].items()})
        result[cid] = CellKeptUnits(cid, cell["target"], freeze(cell["planned"]), freeze(cell["minimum"]), kept,
                                   tuple(sorted(dropped_units, key=lambda u: (u.stratum, u.unit_id))),
                                   len(kept.get("repeat", ())), len(kept.get("quad", ())))
        universe[cid] = {s: {uid: units[s, uid].run_ids for stratum, uid in units if stratum == s}
                         for s in cell["planned"]}
    # A shared member has one disposition, across strata and across cells.
    kept_members = {run for cell in result.values() for rows in cell.kept.values()
                    for unit in rows for run in unit.run_ids}
    dropped_members = {run for cell in result.values() for unit in cell.dropped for run in unit.run_ids}
    if kept_members & dropped_members:
        raise AnalysisRefusal("kept_units_member_split_across_cells")
    excluded_members = document.get("members_excluded")
    if (not isinstance(excluded_members, list)
            or any(not isinstance(member, dict) or type(member.get("run_id")) is not str
                   or not member["run_id"] for member in excluded_members)):
        raise AnalysisRefusal("exclusions_schema_invalid")
    if any(member["run_id"] in kept_members for member in excluded_members):
        raise AnalysisRefusal("excluded_member_in_kept_unit")
    # 7. Compare every member in every unit, not only the counts or unit ids.
    try:
        planned = {cid: {s: {uid: tuple(ids) for uid, ids in units.items()} for s, units in strata.items()}
                   for cid, strata in planned_units.items()}
    except (AttributeError, TypeError):
        raise AnalysisRefusal("exclusions_plan_mismatch") from None
    if universe != planned:
        raise AnalysisRefusal("exclusions_plan_mismatch")
    # 8. The p42 non-target cell has accounting and roster checks, but no gate.
    for cell in result.values():
        p42_non_target = not cell.target and "p42" in cell.cell_id.split("-")
        if not p42_non_target and any(len(cell.kept[s]) < cell.minimum[s] for s in cell.kept):
            raise AnalysisRefusal("kept_units_below_minimum")
    counts = document.get("flag_counts")
    families = {entry["family"] for entry in catalog.codes.values()}
    if (not isinstance(counts, dict) or any(not isinstance(counts.get(k), dict) for k in ("by_family", "by_code"))
            or any(type(key) is not str or not _count(n) for k in ("by_family", "by_code") for key, n in counts[k].items())
            or any(family not in families for family in counts["by_family"])
            or any(code not in catalog.codes for code in counts["by_code"])):
        raise AnalysisRefusal("exclusions_schema_invalid")
    return KeptUnits(archive.window, hashlib.sha256(exclusions_raw).hexdigest(), hashlib.sha256(roster_raw).hexdigest(),
                     sealed_catalog_sha256, freeze(result), freeze(counts["by_family"]),
                     freeze({code: n for code, n in counts["by_code"].items()
                             if catalog.entry(code)["blinding"] == "STRUCTURE"}))
