"""Step-3 structure checks and immutable, per-window consumption contexts.

S(W) is computed once, from the validated basis and both authenticated loss
lists. No fallback infers reference roles from names or campaign manifests.
Stop records are returned on the exception: callers custody ``restricted``
and may serialize only ``unrestricted`` before release.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any, Mapping

from joulewise import whole_window as ww
from joulewise.flags.catalog import catalog_from_bytes
from .archive import ArchiveHandle
from .kept_units import CATALOG_PATH, KeptUnits, _strict_json, require_kept_members_in_verdict
from .windows import AnalysisRefusal, AnalysedWindow, freeze

SLOTS = ("start", "midpoint", "end")


def read_output(archive: ArchiveHandle, relative: str) -> dict:
    return _strict_json(archive.output_bytes(relative), "archive_output_shape_invalid")


def authenticated_roster(archive: ArchiveHandle, roster: Mapping | None = None) -> dict:
    actual = read_output(archive, "derived/roster.json")
    if (actual.get("schema") != "joulewise.b5_harvest_roster.v1"
            or actual.get("pack_id") != archive.window.pack_id
            or actual.get("plan_id") != archive.window.plan_id or actual.get("attempt") != archive.window.attempt):
        raise AnalysisRefusal("context_roster_invalid")
    if roster is not None and ww.canonical_sha256(ww._archive_thaw(roster)) != ww.canonical_sha256(actual):
        raise AnalysisRefusal("context_roster_differs_from_archive")
    return actual


def roster_references(roster: Mapping) -> dict[str, str]:
    members = roster.get("members")
    if not isinstance(members, (list, tuple)):
        raise AnalysisRefusal("context_roster_invalid")
    result, seen = {}, set()
    for member in members:
        if not isinstance(member, Mapping) or not isinstance(member.get("run_id"), str):
            raise AnalysisRefusal("context_roster_invalid")
        run_id = member["run_id"]
        if not run_id or run_id in seen:
            raise AnalysisRefusal("context_roster_invalid")
        seen.add(run_id)
        slots = {member[key] for key in ("neg8_slot", "spare_slot") if member.get(key) in SLOTS}
        if len(slots) > 1:
            raise AnalysisRefusal("context_roster_invalid")
        if slots:
            result[run_id] = slots.pop()
    return result


@dataclass(frozen=True)
class SurvivorSet:
    bundle_ids: frozenset[str]
    by_slot: Mapping[str, frozenset[str]]
    basis_reference_ids: frozenset[str]
    harvest_reference_losses: Mapping[str, str]
    evaluator_reference_losses: tuple[Mapping[str, Any], ...]


def survivor_set(archive: ArchiveHandle, row: Mapping, roster: Mapping) -> SurvivorSet:
    """ERRATUM-RULING X1.7: basis references less both loss lists, counted."""
    references = roster_references(authenticated_roster(archive, roster))
    basis = ww._validated_evaluation_basis(row, archive.window.claim_runs_root)
    if basis is None:
        raise AnalysisRefusal("evaluation_basis_invalid")
    basis_ids = frozenset(item["bundle_id"] for item in basis["member_occurrences"] if item["bundle_id"] in references)
    screen = read_output(archive, "derived/neg8-screen.json")
    harvest_losses = screen.get("harvest_reference_losses")
    rescreen = screen.get("rescreen")
    survivors = rescreen.get("survivors") if isinstance(rescreen, Mapping) else None
    if not isinstance(harvest_losses, Mapping) or not isinstance(survivors, Mapping):
        raise AnalysisRefusal("survivor_set_record_invalid")
    losses = survivors.get("reference_losses", [])
    if (any(not isinstance(key, str) or not isinstance(reason, str) for key, reason in harvest_losses.items())
            or not isinstance(losses, list) or any(not isinstance(item, Mapping)
                or not isinstance(item.get("bundle_id"), str) or not isinstance(item.get("reason"), str) for item in losses)):
        raise AnalysisRefusal("survivor_set_record_invalid")
    lost = frozenset(harvest_losses) | frozenset(item["bundle_id"] for item in losses)
    if lost - frozenset(references):
        raise AnalysisRefusal("survivor_set_loss_not_reference")
    ids = basis_ids - lost
    by_slot = {slot: frozenset(run for run in ids if references[run] == slot) for slot in SLOTS}
    counts = survivors.get("reference_counts")
    def count_mismatch():
        excluded = frozenset(_excluded(archive)) & frozenset(references)
        public = {"pack": archive.window.pack, "stop": "survivor_set_count_mismatch",
                  "survivor_count": len(ids), "excluded_reference_count": len(excluded),
                  "intersection_count": len(ids & excluded)}
        restricted = {**public, "survivor_bundle_ids": sorted(ids), "excluded_reference_ids": sorted(excluded),
            "harvest_reference_losses": dict(harvest_losses), "evaluator_reference_losses": losses,
            "recorded_counts": counts, "computed_counts": {slot: len(by_slot[slot]) for slot in SLOTS}}
        raise TripwireRefusal("survivor_set_count_mismatch", public, restricted)
    if "reference_counts" not in survivors:
        counts = {"start": 3, "midpoint": 1, "end": 3}
        # The historical bracket preserves its bytes at the planned shape.
        # An absent spare outside the basis can still be a harvest loss.
    if (not isinstance(counts, Mapping) or set(counts) != set(SLOTS)
            or any(type(counts[slot]) is not int or counts[slot] != len(by_slot[slot]) for slot in SLOTS)):
        count_mismatch()
    return SurvivorSet(ids, freeze(by_slot), basis_ids, freeze(harvest_losses), freeze(losses))


def _excluded(archive: ArchiveHandle) -> dict[str, tuple[str, ...]]:
    document = read_output(archive, "derived/exclusions.json")
    members = document.get("members_excluded")
    if not isinstance(members, list):
        raise AnalysisRefusal("exclusions_schema_invalid")
    result = {}
    for member in members:
        if (not isinstance(member, Mapping) or not isinstance(member.get("run_id"), str)
                or not member["run_id"] or not isinstance(member.get("codes"), list) or not member["codes"]
                or any(not isinstance(code, str) for code in member["codes"])):
            raise AnalysisRefusal("exclusions_schema_invalid")
        result[member["run_id"]] = tuple(sorted(set(result.get(member["run_id"], ())) | set(member["codes"])))
    return result


def excluded_references(archive: ArchiveHandle, roster: Mapping) -> frozenset[str]:
    """X1.6: all excluded roster references/spares, regardless of loss code."""
    references = roster_references(authenticated_roster(archive, roster))
    return frozenset(_excluded(archive)) & frozenset(references)


class TripwireRefusal(AnalysisRefusal):
    def __init__(self, code: str, unrestricted: Mapping, restricted: Mapping):
        super().__init__(code)
        self.unrestricted = freeze(unrestricted)
        self.restricted = freeze(restricted)

    def to_structure_record(self) -> dict:
        """JSON-ready P9 public projection, copied from the fixed record."""
        return ww._archive_thaw(self.unrestricted)

    def to_record(self) -> dict:
        """JSON-ready full record; restricted custody only."""
        return ww._archive_thaw(self.restricted)


def _catalog(archive: ArchiveHandle):
    raw = CATALOG_PATH.read_bytes()
    document = read_output(archive, "derived/exclusions.json")
    if hashlib.sha256(raw).hexdigest() != document.get("catalog_sha256"):
        raise AnalysisRefusal("exclusions_catalog_mismatch")
    return catalog_from_bytes(raw)


def excluded_reference_in_screen(archive: ArchiveHandle, survivors: SurvivorSet,
                                 excluded: frozenset[str]) -> None:
    """X1.8–11; J2's config mismatch is folded into this same stop."""
    intersection = survivors.bundle_ids & excluded
    if not intersection:
        return
    codes = _excluded(archive)
    catalog = _catalog(archive)
    members = []
    full = []
    for run in sorted(intersection):
        for code in codes[run]:
            entry = catalog.codes.get(code)
            public_code = code if entry is not None and entry.get("blinding") == "STRUCTURE" else "restricted code"
            members.append({"member_id": run, "code": public_code})
            full.append({"member_id": run, "code": code})
    public = {"pack": archive.window.pack, "stop": "excluded_reference_in_screen",
              "survivor_count": len(survivors.bundle_ids), "excluded_reference_count": len(excluded),
              "intersection_count": len(intersection), "members": members}
    restricted = {**public, "members": full, "survivor_bundle_ids": sorted(survivors.bundle_ids),
                  "excluded_reference_ids": sorted(excluded), "intersection": sorted(intersection),
                  "harvest_reference_losses": dict(survivors.harvest_reference_losses),
                  "evaluator_reference_losses": list(survivors.evaluator_reference_losses)}
    raise TripwireRefusal("excluded_reference_in_screen", public, restricted)


def _kept_tripwire(archive: ArchiveHandle, kept_units: KeptUnits, row: Mapping) -> None:
    try:
        require_kept_members_in_verdict(kept_units, row.get("bundle_ids"))
    except AnalysisRefusal as exc:
        if not exc.code.startswith("kept_member_outside_verdict_membership:"):
            raise
        run = exc.code.split(":", 1)[1]
        problems = sorted({problem for item in row.get("excluded_bundles", []) if isinstance(item, Mapping)
            and item.get("bundle_id") == run for problem in item.get("problems", []) if isinstance(problem, str)})
        public = {"pack": archive.window.pack, "stop": exc.code, "member_id": run}
        # Problem strings are permitted by J3.3; do not copy arbitrary detail.
        safe = [word for word in problems if word == "bundle_strict_invalid"]
        if safe:
            public["problems"] = safe
        raise TripwireRefusal(exc.code, public, {**public, "problems": problems,
            "kept_units": kept_units.to_record(), "verdict_bundle_ids": row.get("bundle_ids")}) from None


def build_context(window: AnalysedWindow, archive: ArchiveHandle, kept_units: KeptUnits,
                  window_bracket, row: Mapping, *, roster: Mapping | None = None) -> ww.ArchiveContext:
    """One explicit call per window and bound; never mutate an earlier context."""
    if archive.window != window or kept_units.window != window:
        raise AnalysisRefusal("context_window_mismatch")
    actual = authenticated_roster(archive, roster)
    if (kept_units.roster_sha256 != hashlib.sha256(archive.output_bytes("derived/roster.json")).hexdigest()
            or kept_units.exclusions_sha256 != hashlib.sha256(archive.output_bytes("derived/exclusions.json")).hexdigest()):
        raise AnalysisRefusal("context_kept_units_mismatch")
    _kept_tripwire(archive, kept_units, row)
    survivors = survivor_set(archive, row, actual)
    excluded = excluded_references(archive, actual)
    excluded_reference_in_screen(archive, survivors, excluded)
    removed = kept_units.removed_run_ids() | frozenset(_excluded(archive))
    assessment = window_bracket
    if hasattr(window_bracket, "evaluation"):
        if window_bracket.window != window:
            raise AnalysisRefusal("context_window_mismatch")
        assessment = {**ww._archive_thaw(window_bracket.evaluation), "reasons": []}
    replay, manifests = None, ()
    screen = read_output(archive, "derived/neg8-screen.json")
    rescreen = screen.get("rescreen", {})
    source = rescreen.get("reference_source", {})
    provenance = row.get("row_provenance") or {}
    if (window.governed_e2 and provenance.get("source_campaign_manifests") in (None, [])
            and source.get("source") == "claim_campaign_manifests_authenticated"
            and rescreen.get("evaluated") is True and rescreen.get("decision") == "passed"):
        from .sources_replay import replay_claim_sources
        result = replay_claim_sources(row, window.claim_runs_root, archive=archive, roster=actual)
        if result.problem is not None:
            raise AnalysisRefusal(result.problem)
        manifests = result.catalog_manifests
        def replay(candidate, runs_root):
            return replay_claim_sources(candidate, runs_root, archive=archive, roster=actual).problem
    return ww.ArchiveContext(neg8_harvest_archive=window.archive_root, window_bracket=assessment,
        governed_e3=window.governed_e3, removed_bundle_ids=removed, roster_references=roster_references(actual),
        survivor_bundle_ids=survivors.bundle_ids, sources_replay=replay, catalog_manifests=manifests)
