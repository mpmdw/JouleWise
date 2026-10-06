"""Blind exclusions: which members and windows the sealed catalog removes.

Two parts, both pure functions of their arguments (no I/O, no clock reads):

1. :func:`compute` -- the exclusion function of plan section 3.3. It applies
   the catalog's effect to every flag, joins interval flags to member spans,
   applies the roster rule and the cell unit minimum of section 3.5, and
   returns a deterministic document. It reads only ``code``, ``scope``,
   ``interval.monotonic_ns`` and ``flag_id`` of a flag, and only the named
   structural keys of the roster and spans. It never reads ``observed``,
   ``expected``, ``evidence`` or ``detail``, and never any energy, power or
   duration. ``tests/flags/test_flags_exclusions.py`` proves this by passing
   inputs whose other fields raise when read.

2. :func:`first_claim_usable` -- a pack's analysed window is its first
   claim-usable attempt, so attempts are never mixed.

The physics-in-span joins of plan section 3.4 (monitor journals against
member spans) have one implementation: the harvest's
(``joulewise.b5.harvest``: ``battery_member_flags``, ``thermal_member_flags``,
``contention_member_flags``, ``clock_member_flags``, ``clock_steps`` and the
``clock.systematic`` rule), which reads lane L1's journals and is held equal to
L1's own member join on L1's journal bytes. Their flags reach :func:`compute`
like any other flag. This module once carried a second copy of those joins
with a different interval shape that nothing on the block-5 path called; it
was removed (fix lane fx-flags, 2026-10-06) so that the two could not drift.

Input shapes for :func:`compute`
--------------------------------

``roster``::

    {
      "plan_id": str | None, "attempt": str | int | None,
      "chain_started_monotonic_ns": int | None,
      "members": [
        {"run_id": str, "stage_id": str | None,
         "units": [{"cell_id": str, "stratum": "repeat" | "quad" | ...,
                    "unit_id": str}, ...]},          # [] for auxiliary members
        ...                                           # in plan order
      ],
      "cells": [{"cell_id": str, "target": bool,      # default True
                 "strata": [str, ...],                # declared strata; default ["quad"]
                 "minimum": {stratum: int}}, ...],    # may only raise the catalog rule (8)
      "bundles": [{"bundle_id": str, "run_id": str,   # optional; when present,
                   "attempt": str | int | None,       # a roster member without an
                   "created_monotonic_ns": int | None}]  # admissible bundle is
    }                                                 # excluded (member.bytes_missing)

A cell's strata are the declared ``strata`` (floors ``["repeat", "quad"]``,
contrasts ``["quad"]``; ``["quad"]`` when not declared) plus any stratum its
units carry. A declared stratum with no units has zero kept units, so a roster
that lost a stratum is below the minimum, not resolvable.

A member with two admissible bundles is excluded (``member.bytes_ambiguous``).

A unit is the set of members sharing ``(cell_id, stratum, unit_id)``. A
repeat is a one-member unit; a quad is a four-member unit. Any excluded member
removes its whole unit, so a flagged quad member removes its quad and the
A, B, B, A drift cancellation is kept.

``spans``: ``{run_id: {"monotonic_ns": [start, stop]}}`` -- the member's
sampler stream, from the ``start_sampling`` stamp to the stop stamp, in the
controller's ``time.monotonic_ns()`` domain. Other keys are ignored.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence

from joulewise.flags.catalog import (
    DISCLOSE,
    EXCLUDE_MEMBER,
    EXCLUDE_WINDOW,
    UNCLASSIFIED,
    Catalog,
)
from joulewise.flags.schema import canonical_json_bytes

EXCLUSIONS_SCHEMA = "joulewise.exclusions.v1"
# Every target cell has a quad stratum (floors: repeats and quads; GAMMA
# contrasts: quads only). A roster cell may declare its full set in "strata".
REQUIRED_STRATA = ("quad",)


class ExclusionInputError(ValueError):
    """The roster or spans are structurally unusable (not a flag matter)."""


# --------------------------------------------------------------------------
# compute
# --------------------------------------------------------------------------


def _pair(value: Any) -> tuple[int, int] | None:
    if (
        isinstance(value, (list, tuple))
        and len(value) == 2
        and all(isinstance(item, int) and not isinstance(item, bool) for item in value)
        and value[0] <= value[1]
    ):
        return int(value[0]), int(value[1])
    return None


def _overlaps(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] <= b[1] and b[0] <= a[1]


def _same(expected: Any, observed: Any) -> bool:
    """A scope binding matches when either side is unknown or both agree."""

    if expected is None or observed is None:
        return True
    return str(expected) == str(observed)


def compute(
    flags: Iterable[Mapping[str, Any]],
    roster: Mapping[str, Any],
    spans: Mapping[str, Mapping[str, Any]],
    catalog: Catalog,
) -> dict[str, Any]:
    """Apply the sealed catalog to ``flags`` over ``roster``; pure and blind."""

    plan_id = roster["plan_id"] if "plan_id" in roster else None
    attempt = roster["attempt"] if "attempt" in roster else None
    chain_started = (
        roster["chain_started_monotonic_ns"] if "chain_started_monotonic_ns" in roster else None
    )

    members: list[dict[str, Any]] = []
    member_index: dict[str, int] = {}
    stage_members: dict[str, list[str]] = defaultdict(list)
    for position, member in enumerate(roster["members"]):
        run_id = member["run_id"]
        if not isinstance(run_id, str) or not run_id:
            raise ExclusionInputError("roster member run_id must be a nonempty string")
        if run_id in member_index:
            raise ExclusionInputError(f"duplicate run_id in roster: {run_id}")
        stage_id = member["stage_id"] if "stage_id" in member else None
        units = []
        for unit in member["units"] if "units" in member else ():
            units.append((unit["cell_id"], unit["stratum"], str(unit["unit_id"])))
        member_index[run_id] = position
        members.append({"run_id": run_id, "stage_id": stage_id, "units": units})
        if stage_id is not None:
            stage_members[stage_id].append(run_id)

    member_spans: dict[str, tuple[int, int] | None] = {}
    for run_id in member_index:
        entry = spans[run_id] if run_id in spans else None
        member_spans[run_id] = _pair(entry["monotonic_ns"]) if entry is not None and "monotonic_ns" in entry else None

    excluded: dict[str, set[str]] = defaultdict(set)
    window_reasons: set[str] = set()
    unclassified: set[str] = set()
    by_code: dict[str, int] = defaultdict(int)
    by_family: dict[str, int] = defaultdict(int)
    by_effect: dict[str, int] = defaultdict(int)
    foreign: set[str] = set()
    unmatched: set[str] = set()
    span_unknown: set[str] = set()
    seen_ids: set[str] = set()

    for flag in flags:
        flag_id = flag["flag_id"]
        if flag_id in seen_ids:
            continue
        seen_ids.add(flag_id)
        code = flag["code"]
        scope = flag["scope"]
        level = scope["level"]
        if not _same(plan_id, scope["plan_id"]) or not _same(attempt, scope["attempt"]):
            foreign.add(flag_id)
            continue
        entry = catalog.entry(code)
        effect = entry["effect"]
        by_code[code] += 1
        by_family[entry["family"] or UNCLASSIFIED] += 1
        by_effect[effect] += 1
        if effect == UNCLASSIFIED:
            unclassified.add(code)
            continue
        if effect == DISCLOSE:
            continue
        if effect == EXCLUDE_WINDOW:
            window_reasons.add(code)
            continue
        if effect != EXCLUDE_MEMBER:  # pragma: no cover - catalog validation forbids it
            unclassified.add(code)
            continue
        if level == "member" or (level == "quad" and scope["run_id"] is not None):
            run_id = scope["run_id"]
            if run_id in member_index:
                excluded[run_id].add(code)
            else:
                unmatched.add(flag_id)
            continue
        candidates = list(member_index)
        if level == "stage" and stage_members.get(scope["stage_id"]):
            candidates = list(stage_members[scope["stage_id"]])
        elif level in ("stage", "quad"):
            # A stage that names no roster stage, or a quad flag without a
            # run_id, cannot be placed. It is recorded as unmatched and applied
            # to every member its interval overlaps (all members when it has
            # no interval): conservative, like a span that cannot be placed.
            unmatched.add(flag_id)
        interval = _pair(flag["interval"]["monotonic_ns"])
        for run_id in candidates:
            if interval is None:
                excluded[run_id].add(code)
                continue
            span = member_spans[run_id]
            if span is None:
                # A span we cannot place is treated as overlapping: conservative.
                span_unknown.add(run_id)
                excluded[run_id].add(code)
            elif _overlaps(span, interval):
                excluded[run_id].add(code)

    # Roster rule: bundles outside the roster, attempt or chain are ignored;
    # a roster member with no admissible bundle is excluded.
    bundles_ignored: list[dict[str, Any]] = []
    duplicate_bundles: list[str] = []
    if "bundles" in roster and roster["bundles"] is not None:
        admitted: dict[str, list[str]] = defaultdict(list)
        for bundle in roster["bundles"]:
            bundle_id = str(bundle["bundle_id"])
            run_id = bundle["run_id"]
            bundle_attempt = bundle["attempt"] if "attempt" in bundle else None
            created = bundle["created_monotonic_ns"] if "created_monotonic_ns" in bundle else None
            reason = None
            if run_id not in member_index:
                reason = "roster.not_in_plan"
            elif not _same(attempt, bundle_attempt):
                reason = "roster.foreign_attempt"
            elif chain_started is not None and created is None:
                # No stamp places the bundle after the chain started, so it is
                # not used; the label says why (it was not shown to be early).
                reason = "roster.creation_unplaced"
            elif chain_started is not None and created < chain_started:
                reason = "roster.before_chain_started"
            if reason is not None:
                bundles_ignored.append({"bundle_id": bundle_id, "run_id": run_id, "code": reason})
                continue
            admitted[run_id].append(bundle_id)
        for run_id in member_index:
            if not admitted.get(run_id):
                excluded[run_id].add("member.bytes_missing")
            elif len(admitted[run_id]) > 1:
                # Two admissible bundles for one member: which bytes are the
                # member is ambiguous, so neither is used (no silent pick).
                duplicate_bundles.append(run_id)
                excluded[run_id].add("member.bytes_ambiguous")

    # Cells and the unit minimum.
    units: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for member in members:
        for cell_id, stratum, unit_id in member["units"]:
            units[(cell_id, stratum, unit_id)].append(member["run_id"])
    cell_specs: dict[str, Mapping[str, Any]] = {}
    for cell in roster["cells"] if "cells" in roster else ():
        cell_specs[cell["cell_id"]] = cell
    cell_ids = sorted(set(cell_specs) | {key[0] for key in units})
    default_minimum = catalog.cell_unit_minimum

    cells_out: list[dict[str, Any]] = []
    any_target_unresolvable = False
    for cell_id in cell_ids:
        spec = cell_specs.get(cell_id, {})
        target = bool(spec["target"]) if "target" in spec else True
        minimum_spec = spec["minimum"] if "minimum" in spec else {}
        declared = spec["strata"] if "strata" in spec else None
        required = set(declared) if declared is not None else set(REQUIRED_STRATA)
        strata = sorted({key[1] for key in units if key[0] == cell_id} | required)
        planned: dict[str, int] = {}
        kept: dict[str, list[str]] = {}
        dropped: list[dict[str, Any]] = []
        minimum: dict[str, int] = {}
        for stratum in strata:
            unit_keys = sorted(key for key in units if key[0] == cell_id and key[1] == stratum)
            planned[stratum] = len(unit_keys)
            # A roster may raise a stratum's minimum, never lower it below
            # the sealed catalog rule (review 2026-10-05).
            minimum[stratum] = (
                max(int(minimum_spec[stratum]), default_minimum)
                if stratum in minimum_spec
                else default_minimum
            )
            kept[stratum] = []
            for key in unit_keys:
                run_ids = units[key]
                codes = sorted({code for run_id in run_ids for code in excluded.get(run_id, ())})
                if codes:
                    dropped.append(
                        {
                            "stratum": stratum,
                            "unit_id": key[2],
                            "codes": codes,
                            "run_ids": sorted(run_ids),
                            "positions": sorted(member_index[run_id] for run_id in run_ids),
                        }
                    )
                else:
                    kept[stratum].append(key[2])
        resolvable = all(len(kept[s]) >= minimum[s] for s in strata) and bool(strata)
        if target and not resolvable:
            any_target_unresolvable = True
        cells_out.append(
            {
                "cell_id": cell_id,
                "target": target,
                "planned": planned,
                "minimum": minimum,
                "n_repeats": len(kept.get("repeat", [])),
                "n_quads": len(kept.get("quad", [])),
                "n_kept": {s: len(kept[s]) for s in strata},
                "kept_units": kept,
                "dropped_units": sorted(
                    dropped, key=lambda item: (item["stratum"], item["unit_id"])
                ),
                "resolvable": resolvable,
            }
        )

    if any_target_unresolvable:
        window_reasons.add("cell.below_minimum")

    members_excluded = [
        {
            "run_id": run_id,
            "position": member_index[run_id],
            "codes": sorted(codes),
            "families": sorted(
                {
                    catalog.entry(code)["family"] or UNCLASSIFIED
                    for code in codes
                }
            ),
        }
        for run_id, codes in excluded.items()
        if codes
    ]
    members_excluded.sort(key=lambda item: (item["position"], item["run_id"]))

    return {
        "schema_version": EXCLUSIONS_SCHEMA,
        "catalog_sha256": catalog.sha256,
        "plan_id": plan_id,
        "attempt": attempt,
        "members_excluded": members_excluded,
        "bundles_ignored": sorted(bundles_ignored, key=lambda item: (item["bundle_id"], item["code"])),
        "duplicate_bundles": sorted(duplicate_bundles),
        "cells": cells_out,
        "claim_usable": not window_reasons,
        "reasons": sorted(window_reasons),
        "unclassified": sorted(unclassified),
        "release_blocked": bool(unclassified),
        "flag_counts": {
            "by_code": dict(sorted(by_code.items())),
            "by_family": dict(sorted(by_family.items())),
            "by_effect": dict(sorted(by_effect.items())),
            "foreign_scope": len(foreign),
            "unmatched_member": len(unmatched),
        },
        "span_unknown": sorted(span_unknown),
    }


def render(result: Mapping[str, Any]) -> bytes:
    """Canonical bytes of a :func:`compute` result (identical inputs, identical bytes)."""

    return canonical_json_bytes(result) + b"\n"


def first_claim_usable(attempts: Sequence[Mapping[str, Any]]) -> Any:
    """The first attempt, in order, whose exclusions say ``claim_usable``; else ``None``.

    An attempt that is claim-usable but ``release_blocked`` (an unclassified
    code) is undecided: classifying the code may exclude it, and skipping to
    a later attempt would pick the analysed window before that is known. So
    the answer is ``None`` until it is classified. A missing
    ``release_blocked`` counts as blocked. An attempt that is not claim-usable
    stays so whatever the classification (classifying can only add
    exclusions), so it is passed over.
    """

    for attempt in attempts:
        if attempt["claim_usable"] is not True:
            continue
        if attempt.get("release_blocked", True) is not False:
            return None
        return attempt["attempt"]
    return None
