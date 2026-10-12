"""S1 synthetic variants, layered over S0 without rebuilding per test.

The pin2 named windows are S0's exported real-writer/real-harvest fixtures.
Variants copy only authenticated structural outputs, never a bundle summary.
"""
from dataclasses import dataclass, replace
import atexit
import copy
import json
from pathlib import Path
import tempfile

from joulewise.b5_analysis.archive import open_archive, open_attempt_record
from joulewise.b5_analysis.windows import AnalysedWindow, SealPins
from joulewise.flags.catalog import load_catalog
from joulewise.flags.exclusions import compute, GAMMA_PACK_ID
from tests.b5_analysis import fixtures as s0

_CACHE = {}
PINS = SealPins.load()
CATALOG = load_catalog(s0.ROOT / "configs/campaigns/v5_claim_25g83/flag_catalog.json")


@dataclass(frozen=True)
class Snapshot:
    entry: object
    harvest: dict
    exclusions: dict
    roster: dict
    planned: dict


def s0_planned():
    # Independently from the known S0 builder's science plan, not the outputs
    # being verified. Quad membership is A1, B1, B2, A2 in roster order.
    return {"df-b5t-family": {
        "repeat": {f"s0-mock-r{i:02d}": (f"s0-mock-r{i:02d}",) for i in range(1, 11)},
        "quad": {f"s0-mock-b{i:02d}": tuple(f"s0-mock-b{i:02d}-{p}" for p in ("a1", "b1", "b2", "a2"))
                 for i in range(1, 11)}}}


def cached(name="STD", *, pack="alpha"):
    key = (name, pack)
    if key not in _CACHE:
        if pack == "alpha":
            entry = s0.archived_entry("pin2", name)
        else:
            built = s0.build_window(pack, variants=() if name == "STD" else (name,))
            atexit.register(built.close)
            entry = built.entry
        root = entry.archive_root
        _CACHE[key] = Snapshot(entry, json.loads((root / "harvest.json").read_bytes()),
            json.loads((root / "derived/exclusions.json").read_bytes()),
            json.loads((root / "derived/roster.json").read_bytes()), s0_planned())
    return copy.deepcopy(_CACHE[key])


def recompute(snapshot, roster, removed=(), *, code="thermal.os_level_nonzero"):
    flags = [{"flag_id": f"s1-{i}", "code": code,
              "scope": {"level": "member", "plan_id": roster["plan_id"], "attempt": roster["attempt"],
                        "run_id": run, "bundle_id": None, "stage_id": None},
              "interval": {"monotonic_ns": None}}
             for i, run in enumerate(removed)]
    document = compute(flags, roster, {}, CATALOG)
    document["harvest_checkout"] = snapshot.harvest["harvest_checkout"]
    return document


def p42_snapshot():
    snapshot = cached("SIX_QUADS_REMOVED")
    cid = "df-ph-prefill-p42-mock"
    for cell in snapshot.roster["cells"]:
        cell.update(cell_id=cid, target=False)
    for member in snapshot.roster["members"]:
        for unit in member["units"]:
            unit["cell_id"] = cid
    snapshot.exclusions.clear()
    snapshot.exclusions.update(recompute(snapshot, snapshot.roster,
        [f"s0-mock-b{i:02d}-a1" for i in range(1, 7)]))
    snapshot.planned[cid] = snapshot.planned.pop("df-b5t-family")
    return snapshot


def gamma_snapshot(*, midpoint_lost=False, attempt=1):
    # Structural GAMMA variant: S0's pinned writer outputs plus the real pure
    # exclusions function on a quad-only contrast roster. No energy is read.
    snapshot = cached()
    cid = "ctr-d117-decode-mock"
    snapshot.roster.update(pack_id=GAMMA_PACK_ID, attempt=attempt)
    snapshot.roster["cells"] = [{"cell_id": cid, "strata": ["quad"], "target": True}]
    for member in snapshot.roster["members"]:
        member["units"] = [{**u, "cell_id": cid} for u in member["units"] if u["stratum"] == "quad"]
    doc = recompute(snapshot, snapshot.roster)
    if midpoint_lost:
        flag = {"flag_id": "s1-midpoint", "code": "neg8.midpoint_lost",
                "scope": {"level": "window", "plan_id": snapshot.roster["plan_id"], "attempt": attempt,
                          "run_id": None, "bundle_id": None, "stage_id": None},
                "interval": {"monotonic_ns": None}}
        doc = compute([flag], snapshot.roster, {}, CATALOG)
        doc["harvest_checkout"] = snapshot.harvest["harvest_checkout"]
    return replace(snapshot, entry=replace(snapshot.entry, pack="gamma", pack_id=GAMMA_PACK_ID, attempt=attempt),
                   exclusions=doc, planned={cid: {"quad": snapshot.planned["df-b5t-family"]["quad"]}})


def registered_snapshot(pack, *, remove_first_decode_quad=False, base=None):
    """Synthetic roster over the sealed planned ids; still no member bundles.

    This exercises all real cell-id spaces, including decode's p42 aliases.
    The structural records are recomputed by the real exclusion function, not
    presented as full writer/harvest integration evidence.
    """
    snapshot = base or cached()
    pack_id = {"alpha": "d117_floor_qwen3-1p7b_v5", "beta": "d117_floor_qwen3-8b_v5",
               "gamma": GAMMA_PACK_ID}[pack]
    root = s0.ROOT / "configs/campaigns" / pack_id
    members, cells, planned = {}, {}, {}
    def add(cid, stratum, uid, runs):
        planned.setdefault(cid, {}).setdefault(stratum, {})[uid] = tuple(runs)
        cells.setdefault(cid, {"cell_id": cid, "target": "p42" not in cid.split("-"), "strata": []})
        if stratum not in cells[cid]["strata"]:
            cells[cid]["strata"].append(stratum)
        for run in runs:
            member = members.setdefault(run, {"run_id": run, "stage_id": "synthetic-registered", "units": []})
            member["units"].append({"cell_id": cid, "stratum": stratum, "unit_id": uid})
    if pack != "gamma":
        spec = json.loads((root / "extraction_spec.json").read_bytes())
        for cell in spec["cells"]:
            cid = cell["condition_family_id"]
            if cell["kind"] == "absolute":
                for member in cell["members"]:
                    add(cid, "repeat", member["bundle_id"], [member["bundle_id"]])
            else:
                for block in cell["blocks"]:
                    add(cid, "quad", block["block_id"], [block["members"][p] for p in ("A1", "B1", "B2", "A2")])
    else:
        spec = json.loads((root / "analysis_manifest_v3.json").read_bytes())
        for contrast in spec["contrasts"]:
            for block in contrast["block_ids"]:
                rows = sorted((m for m in contrast["members"] if m["block_id"] == block), key=lambda m: m["order_index"])
                add(contrast["contrast_id"], "quad", block, [m["run_id"] for m in rows])
    roster = {**snapshot.roster, "pack_id": pack_id, "cells": list(cells.values()), "members": list(members.values())}
    removed = ()
    if remove_first_decode_quad:
        cid = next(cid for cid in planned if "decode" in cid.split("-"))
        removed = (next(iter(planned[cid]["quad"].values()))[0],)
    doc = recompute(snapshot, roster, removed)
    return replace(snapshot, entry=replace(snapshot.entry, pack=pack, pack_id=pack_id),
                   roster=roster, exclusions=doc, planned=planned), spec


class Case:
    """A disposable structural copy with independent digest-update controls."""
    def __init__(self, snapshot=None):
        self.snapshot = snapshot or cached()
        self.tmp = tempfile.TemporaryDirectory(prefix="b5-s1-case-")
        self.root = Path(self.tmp.name)
        self.exclusions = copy.deepcopy(self.snapshot.exclusions)
        self.roster = copy.deepcopy(self.snapshot.roster)
        self.harvest = copy.deepcopy(self.snapshot.harvest)
        self.entry = replace(self.snapshot.entry, archive_root=self.root)
        self.planned = copy.deepcopy(self.snapshot.planned)
        self.write()

    def write(self, *, update_digest=True, exclusions_raw=None, roster_raw=None):
        self.harvest.update(attempt=self.entry.attempt, plan_id=self.entry.plan_id, pack_id=self.entry.pack_id,
                            claim_usable=self.exclusions.get("claim_usable", False),
                            exclude_window_reasons=self.exclusions.get("reasons", []))
        self.exclusions["harvest_checkout"] = self.harvest["harvest_checkout"]
        for relative, value, raw in (("derived/exclusions.json", self.exclusions, exclusions_raw),
                                     ("derived/roster.json", self.roster, roster_raw),
                                     ("derived/window_flags.json", {
                                         "schema": "joulewise.window_flags.v1",
                                         "exclusions": {"claim_usable": self.harvest["claim_usable"]},
                                         "flags": {"total": 0, "by_family": {}, "by_code": {}}}, None)):
            path = self.root / relative
            s0.put(path, value)
            if raw is not None:
                path.write_bytes(raw)
            if update_digest:
                self.harvest["outputs"][relative] = s0.sha(path)
        # An S1 copy does not claim to have copied or authenticated the screen.
        self.harvest["outputs"].pop("derived/neg8-screen.json", None)
        s0.put(self.root / "harvest.json", self.harvest)
        self.entry = replace(self.entry, harvest_record_sha256=s0.sha(self.root / "harvest.json"),
                             claim_usable=self.harvest["claim_usable"])

    def record(self):
        return open_attempt_record(self.entry, seal_pins=PINS)

    def handle(self):
        return open_archive(AnalysedWindow.from_record(self.record()), seal_pins=PINS)

    def close(self):
        self.tmp.cleanup()
