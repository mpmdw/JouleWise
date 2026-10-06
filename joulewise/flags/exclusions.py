"""Blind exclusions: which members and windows the sealed catalog removes.

Three parts, all pure functions of their arguments (no I/O, no clock reads
except the ``emitted`` stamp of a new flag, which callers may pin):

1. :func:`compute` -- the exclusion function of plan section 3.3. It applies
   the catalog's effect to every flag, joins interval flags to member spans,
   applies the roster rule and the cell unit minimum of section 3.5, and
   returns a deterministic document. It reads only ``code``, ``scope``,
   ``interval.monotonic_ns`` and ``flag_id`` of a flag, and only the named
   structural keys of the roster and spans. It never reads ``observed``,
   ``expected``, ``evidence`` or ``detail``, and never any energy, power or
   duration. ``tests/flags/test_flags_exclusions.py`` proves this by passing
   inputs whose other fields raise when read.

2. The physics-in-span joins of section 3.4 (:func:`battery_span_flags`,
   :func:`thermal_span_flags`, :func:`contention_span_flags`,
   :func:`clock_span_flags`, :func:`clock_systematic_flags`). They turn the
   monitor's journals, normalized as documented on each function, into
   member-level flags. The harvest (lane L5) normalizes the journals and calls
   them; the flags they return go into ``compute`` like any other flag.

3. :func:`first_claim_usable` -- a pack's analysed window is its first
   claim-usable attempt, so attempts are never mixed.

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
controller's ``time.monotonic_ns()`` domain. Optional
``"request_monotonic_ns": [start, end]`` is used by the contention join.
"""

from __future__ import annotations

import bisect
from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence

from joulewise.flags.catalog import (
    DISCLOSE,
    EXCLUDE_MEMBER,
    EXCLUDE_WINDOW,
    UNCLASSIFIED,
    Catalog,
)
from joulewise.flags.schema import (
    canonical_json_bytes,
    make_flag,
    make_interval,
    make_scope,
    make_source,
)

EXCLUSIONS_SCHEMA = "joulewise.exclusions.v1"
BATTERY_LIMIT_MA = 200
BATTERY_MAX_GAP_S = 120.0
THERMAL_MAX_GAP_S = 15.0
CONTENTION_LIMIT_CPU_S_PER_S = 0.05
CONTENTION_EXCLUDED_IN_WINDOW = ("kernel_task",)
CLOCK_SYSTEMATIC_MINIMUM_N = 5
# Every target cell has a quad stratum (floors: repeats and quads; GAMMA
# contrasts: quads only). A roster cell may declare its full set in "strata".
REQUIRED_STRATA = ("quad",)
_NS = 1_000_000_000


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
            elif chain_started is not None and (created is None or created < chain_started):
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


# --------------------------------------------------------------------------
# Physics in span (plan section 3.4)
# --------------------------------------------------------------------------


def _member_flag(
    code: str,
    family: str,
    run_id: str,
    span: tuple[int, int],
    observed: Any,
    expected: Any,
    detail: str,
    collector: str,
    context: Mapping[str, Any] | None,
    span_entry: Mapping[str, Any],
    emitted: Mapping[str, Any] | None,
    level: str = "member",
) -> dict[str, Any]:
    context = context or {}
    return make_flag(
        code=code,
        family=family,
        klass="PHYSICS",
        scope=make_scope(
            level,
            plan_id=context.get("plan_id"),
            attempt=context.get("attempt"),
            stage_id=span_entry.get("stage_id"),
            run_id=run_id if level == "member" else None,
            bundle_id=span_entry.get("bundle_id"),
        ),
        source=make_source("harvest", f"joulewise.flags.exclusions.{collector}"),
        observed=observed,
        expected=expected,
        detail=detail,
        interval=make_interval(monotonic_ns=span),
        catalog_sha256=context.get("catalog_sha256"),
        emitted=emitted,
    )


def _in_force(times: Sequence[int], span: tuple[int, int]) -> tuple[list[int], bool]:
    """Indices of the in-force readings for ``span`` and whether both ends are covered.

    In force: the last reading at or before the start, every reading inside,
    and the first reading at or after the end.
    """

    start, stop = span
    first_after_start = bisect.bisect_right(times, start)
    last_before_stop = bisect.bisect_left(times, stop)
    chosen: list[int] = []
    if first_after_start > 0:
        chosen.append(first_after_start - 1)
    chosen.extend(range(first_after_start, last_before_stop))
    covered_after = last_before_stop < len(times)
    if covered_after:
        chosen.append(last_before_stop)
    return sorted(set(chosen)), first_after_start > 0 and covered_after


def _max_gap_exceeded(times: Sequence[int], chosen: Sequence[int], limit_ns: int) -> bool:
    return any(times[b] - times[a] > limit_ns for a, b in zip(chosen, chosen[1:]))


def _span_items(spans: Mapping[str, Mapping[str, Any]]) -> list[tuple[str, tuple[int, int], Mapping[str, Any]]]:
    items = []
    for run_id in sorted(spans):
        entry = spans[run_id]
        span = _pair(entry.get("monotonic_ns"))
        if span is not None:
            items.append((run_id, span, entry))
    return items


def battery_span_flags(
    publications: Sequence[Mapping[str, Any]],
    spans: Mapping[str, Mapping[str, Any]],
    *,
    limit_ma: int = BATTERY_LIMIT_MA,
    max_gap_s: float = BATTERY_MAX_GAP_S,
    accumulator: Mapping[str, Any] | None = None,
    context: Mapping[str, Any] | None = None,
    emitted: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """``battery.member_span``, ``battery.unmeasured`` and the accumulator rule.

    ``publications``: one entry per gauge publication (a change of the
    battery's ``UpdateTime``), each ``{"monotonic_ns": int,
    "instant_amperage_ma": int | None, "amperage_ma": int | None,
    "is_charging": bool | None, "external_connected": bool | None,
    "voltage_mv": int | None, "accumulated_battery_power": number | None,
    "battery_power_accumulator_count": int | None}``. ``monotonic_ns`` is when
    the publication took effect in the controller's clock domain.

    A member is flagged ``battery.member_span`` if any in-force publication
    has ``|InstantAmperage| > limit``, ``|Amperage| > limit``, ``IsCharging``
    true or ``ExternalConnected`` false. A missing field in an in-force
    publication, a missing publication before the start or after the end, or
    a gap of more than ``max_gap_s`` between in-force publications flags
    ``battery.unmeasured``.

    ``accumulator`` enables the accumulator rule only once lane L1 has
    confirmed the units: ``{"scale_w_per_unit": float, "voltage_v": float}``.
    For each pair of consecutive in-force publications the mean battery power
    over the nonzero seconds is ``(delta AccumulatedBatteryPower x scale) /
    delta BatteryPowerAccumulatorCount``; above ``limit_ma x V`` it flags
    ``battery.accumulator_excursion``. Without it the rule is not evaluated.
    """

    ordered = sorted(publications, key=lambda item: int(item["monotonic_ns"]))
    times = [int(item["monotonic_ns"]) for item in ordered]
    limit_ns = int(max_gap_s * _NS)
    out: list[dict[str, Any]] = []
    for run_id, span, entry in _span_items(spans):
        chosen, covered = _in_force(times, span)
        violations = []
        missing_fields = False
        for index in chosen:
            pub = ordered[index]
            inst = pub.get("instant_amperage_ma")
            avg = pub.get("amperage_ma")
            charging = pub.get("is_charging")
            external = pub.get("external_connected")
            if inst is None or avg is None or charging is None or external is None:
                missing_fields = True
            reasons = []
            if inst is not None and abs(inst) > limit_ma:
                reasons.append("instant_amperage")
            if avg is not None and abs(avg) > limit_ma:
                reasons.append("amperage")
            if charging is True:
                reasons.append("is_charging")
            if external is False:
                reasons.append("external_disconnected")
            if reasons:
                violations.append(
                    {
                        "monotonic_ns": times[index],
                        "instant_amperage_ma": inst,
                        "amperage_ma": avg,
                        "is_charging": charging,
                        "external_connected": external,
                        "reasons": reasons,
                    }
                )
        if violations:
            out.append(
                _member_flag(
                    "battery.member_span", "PHYSICS_IN_SPAN", run_id, span,
                    {"violations": violations}, {"abs_ma_max": limit_ma,
                     "is_charging": False, "external_connected": True},
                    f"{len(violations)} in-force battery publication(s) out of float",
                    "battery_span_flags", context, entry, emitted,
                )
            )
        gap = _max_gap_exceeded(times, chosen, limit_ns)
        if not covered or gap or missing_fields:
            out.append(
                _member_flag(
                    "battery.unmeasured", "PHYSICS_IN_SPAN", run_id, span,
                    {"publications_in_force": len(chosen), "ends_covered": covered,
                     "gap_exceeded": gap, "missing_fields": missing_fields},
                    {"max_gap_s": max_gap_s},
                    "battery publications do not cover the member span",
                    "battery_span_flags", context, entry, emitted,
                )
            )
        if accumulator is not None:
            scale = float(accumulator["scale_w_per_unit"])
            excursions = []
            for a, b in zip(chosen, chosen[1:]):
                first, second = ordered[a], ordered[b]
                c0 = first.get("battery_power_accumulator_count")
                c1 = second.get("battery_power_accumulator_count")
                p0 = first.get("accumulated_battery_power")
                p1 = second.get("accumulated_battery_power")
                if None in (c0, c1, p0, p1) or c1 <= c0:
                    continue
                volts = (
                    second.get("voltage_mv") / 1000.0
                    if second.get("voltage_mv") is not None
                    else float(accumulator["voltage_v"])
                )
                mean_w = abs(p1 - p0) * scale / (c1 - c0)
                threshold_w = limit_ma / 1000.0 * volts
                if mean_w > threshold_w:
                    excursions.append(
                        {"interval_monotonic_ns": [times[a], times[b]],
                         "mean_w": mean_w, "threshold_w": threshold_w,
                         "nonzero_seconds": c1 - c0}
                    )
            if excursions:
                out.append(
                    _member_flag(
                        "battery.accumulator_excursion", "PHYSICS_IN_SPAN", run_id, span,
                        {"excursions": excursions}, {"abs_ma_max": limit_ma},
                        "battery accumulator implies a mean power above the float limit",
                        "battery_span_flags", context, entry, emitted,
                    )
                )
    return out


def thermal_span_flags(
    samples: Sequence[Mapping[str, Any]],
    spans: Mapping[str, Mapping[str, Any]],
    *,
    max_gap_s: float = THERMAL_MAX_GAP_S,
    context: Mapping[str, Any] | None = None,
    emitted: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """``thermal.os_level_nonzero`` and ``thermal.unmeasured``.

    ``samples``: ``{"monotonic_ns": int, "level": int | None}`` from the
    monitor's 5 s reads of ``com.apple.system.thermalpressurelevel``; ``None``
    means the probe failed. A member is flagged when any in-force sample (the
    last at or before the start, every one inside, the first at or after the
    end) is nonzero. Failed probes in force, an uncovered end, or a gap above
    ``max_gap_s`` flag ``thermal.unmeasured``.
    """

    ordered = sorted(samples, key=lambda item: int(item["monotonic_ns"]))
    times = [int(item["monotonic_ns"]) for item in ordered]
    limit_ns = int(max_gap_s * _NS)
    out: list[dict[str, Any]] = []
    for run_id, span, entry in _span_items(spans):
        chosen, covered = _in_force(times, span)
        levels = [(times[i], ordered[i].get("level")) for i in chosen]
        nonzero = [{"monotonic_ns": t, "level": level} for t, level in levels if level not in (0, None)]
        failed = any(level is None for _, level in levels)
        if nonzero:
            out.append(
                _member_flag(
                    "thermal.os_level_nonzero", "PHYSICS_IN_SPAN", run_id, span,
                    {"samples": nonzero}, {"level": 0},
                    "OS thermal pressure level nonzero in the member span",
                    "thermal_span_flags", context, entry, emitted,
                )
            )
        gap = _max_gap_exceeded(times, chosen, limit_ns)
        if not covered or gap or failed:
            out.append(
                _member_flag(
                    "thermal.unmeasured", "DIAGNOSTIC", run_id, span,
                    {"samples_in_force": len(chosen), "ends_covered": covered,
                     "gap_exceeded": gap, "probe_failed": failed},
                    {"max_gap_s": max_gap_s},
                    "thermal samples do not cover the member span",
                    "thermal_span_flags", context, entry, emitted,
                )
            )
    return out


def contention_span_flags(
    intervals: Sequence[Mapping[str, Any]],
    spans: Mapping[str, Mapping[str, Any]],
    *,
    limit_cpu_s_per_s: float = CONTENTION_LIMIT_CPU_S_PER_S,
    excluded_comms: Iterable[str] = CONTENTION_EXCLUDED_IN_WINDOW,
    context: Mapping[str, Any] | None = None,
    emitted: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """``contention.request_overlap``, ``contention.unmeasured`` and the kernel_task share.

    ``intervals``: one per pair of ``ps`` snapshots, ``{"monotonic_ns": [a, b],
    "processes": [{"pid": int, "comm": str, "cpu_s_per_s": float,
    "outside": bool}]}``. ``cpu_s_per_s`` is the difference of cumulative CPU
    time over the interval divided by its length. ``outside`` is false for
    the measurement tree (driver, chain process group, sudo and powermetrics,
    caffeinate, the monitor); it defaults to true.

    The member's request span is ``spans[run_id]["request_monotonic_ns"]``,
    falling back to the sampler span. An outside process above the limit in
    an interval that overlaps the request flags the member. ``kernel_task``
    is excluded in window (its time during a request is the workload's own
    driver and I/O work); its largest share is disclosed. Any part of the
    request no interval covers flags ``contention.unmeasured``.
    """

    excluded = set(excluded_comms)
    ordered = []
    for item in intervals:
        pair = _pair(item.get("monotonic_ns"))
        if pair is not None:
            ordered.append((pair, item.get("processes") or []))
    ordered.sort(key=lambda entry: entry[0])
    out: list[dict[str, Any]] = []
    for run_id, span, entry in _span_items(spans):
        request = _pair(entry.get("request_monotonic_ns")) or span
        overlapping = [(pair, procs) for pair, procs in ordered if _overlaps(pair, request)]
        offenders: dict[tuple[int, str], float] = {}
        kernel_share = None
        for _pair_value, procs in overlapping:
            for proc in procs:
                comm = str(proc.get("comm"))
                cpu = float(proc.get("cpu_s_per_s") or 0.0)
                if comm in excluded:
                    kernel_share = cpu if kernel_share is None else max(kernel_share, cpu)
                    continue
                if proc.get("outside", True) is False:
                    continue
                if cpu > limit_cpu_s_per_s:
                    key = (int(proc.get("pid") or 0), comm)
                    offenders[key] = max(offenders.get(key, 0.0), cpu)
        if offenders:
            top = sorted(offenders.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
            out.append(
                _member_flag(
                    "contention.request_overlap", "PHYSICS_IN_SPAN", run_id, request,
                    {"offenders": [{"pid": pid, "comm": comm, "cpu_s_per_s": cpu}
                                   for (pid, comm), cpu in top]},
                    {"cpu_s_per_s_max": limit_cpu_s_per_s},
                    f"{len(offenders)} outside process(es) above the contention limit",
                    "contention_span_flags", context, entry, emitted,
                )
            )
        # Coverage of the request by the union of overlapping intervals.
        cursor = request[0]
        for pair, _procs in overlapping:
            if pair[0] > cursor:
                break
            cursor = max(cursor, pair[1])
        if cursor < request[1] or not overlapping:
            out.append(
                _member_flag(
                    "contention.unmeasured", "PHYSICS_IN_SPAN", run_id, request,
                    {"covered_until_monotonic_ns": cursor, "intervals": len(overlapping)},
                    {"covered_until_monotonic_ns": request[1]},
                    "ps intervals do not cover the member request",
                    "contention_span_flags", context, entry, emitted,
                )
            )
        if kernel_share is not None:
            out.append(
                _member_flag(
                    "contention.kernel_task_share", "DIAGNOSTIC", run_id, request,
                    {"kernel_task_cpu_s_per_s_max": kernel_share}, None,
                    "kernel_task CPU share during the request (disclosed)",
                    "contention_span_flags", context, entry, emitted,
                )
            )
    return out


def _step_interval(step: Mapping[str, Any]) -> tuple[int, int] | None:
    value = step.get("monotonic_ns")
    if isinstance(value, int) and not isinstance(value, bool):
        return value, value
    return _pair(value)


def clock_span_flags(
    steps: Sequence[Mapping[str, Any]],
    spans: Mapping[str, Mapping[str, Any]],
    *,
    calibration_spans: Mapping[str, Sequence[int]] | None = None,
    context: Mapping[str, Any] | None = None,
    emitted: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """``clock.step_overlap`` (member) and ``clock.step_overlap_calibration`` (window).

    ``steps``: the monitor's ``clock.step`` events, each ``{"monotonic_ns":
    [t_before, t_after]}`` (the two 1 Hz samples between which the residual
    moved more than 1 ms) or a single ``int``. ``calibration_spans`` maps a
    capture name (``pre``/``post``) to its ``[start, stop]``.
    """

    intervals = sorted(i for i in (_step_interval(step) for step in steps) if i is not None)
    out: list[dict[str, Any]] = []
    for run_id, span, entry in _span_items(spans):
        hits = [list(i) for i in intervals if _overlaps(i, span)]
        if hits:
            out.append(
                _member_flag(
                    "clock.step_overlap", "PHYSICS_IN_SPAN", run_id, span,
                    {"steps_monotonic_ns": hits}, {"steps": 0},
                    "a clock step falls inside the member span",
                    "clock_span_flags", context, entry, emitted,
                )
            )
    for name in sorted(calibration_spans or {}):
        span = _pair(list((calibration_spans or {})[name]))
        if span is None:
            continue
        hits = [list(i) for i in intervals if _overlaps(i, span)]
        if hits:
            out.append(
                _member_flag(
                    "clock.step_overlap_calibration", "CLOCK_SYSTEMATIC", name, span,
                    {"capture": name, "steps_monotonic_ns": hits}, {"steps": 0},
                    f"a clock step falls inside the {name} calibration capture",
                    "clock_span_flags", context, {"stage_id": name}, emitted,
                    level="window",
                )
            )
    return out


def clock_systematic_flags(
    anchor_statuses: Mapping[str, Any],
    *,
    minimum_n: int = CLOCK_SYSTEMATIC_MINIMUM_N,
    context: Mapping[str, Any] | None = None,
    emitted: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """``clock.systematic``: more than half of at least ``minimum_n`` recorded anchors not ``bounded``.

    ``anchor_statuses`` maps run_id to the recorded per-member anchor status
    (``None`` when not recorded). The per-member anchor bound itself stays
    authoritative and is its own member exclusion (``member.anchor_not_bounded``).
    """

    recorded = {run_id: status for run_id, status in anchor_statuses.items() if status is not None}
    not_bounded = sorted(run_id for run_id, status in recorded.items() if status != "bounded")
    n = len(recorded)
    if n < minimum_n or len(not_bounded) * 2 <= n:
        return []
    context = context or {}
    return [
        make_flag(
            code="clock.systematic",
            family="CLOCK_SYSTEMATIC",
            klass="NUMBER",
            scope=make_scope("window", plan_id=context.get("plan_id"), attempt=context.get("attempt")),
            source=make_source("harvest", "joulewise.flags.exclusions.clock_systematic_flags"),
            observed={"recorded": n, "not_bounded": len(not_bounded), "run_ids": not_bounded},
            expected={"not_bounded_at_most_half_of": n, "minimum_n": minimum_n},
            detail=f"{len(not_bounded)} of {n} recorded anchors not bounded",
            catalog_sha256=context.get("catalog_sha256"),
            emitted=emitted,
        )
    ]
