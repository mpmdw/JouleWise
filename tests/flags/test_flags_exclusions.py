"""The blind exclusion function, the physics-in-span joins and the cell minimum."""

from __future__ import annotations

import random
import unittest
from collections.abc import Mapping
from typing import Any, Iterator

from joulewise.flags.catalog import DISCLOSE, EXCLUDE_MEMBER, draft_catalog, draft_catalog_document, catalog_from_bytes
from joulewise.flags.exclusions import (
    battery_span_flags,
    clock_span_flags,
    clock_systematic_flags,
    compute,
    contention_span_flags,
    first_claim_usable,
    render,
    thermal_span_flags,
)
from joulewise.flags.schema import make_flag, make_interval, make_scope, make_source, validate_flag

S = 1_000_000_000
EMITTED = {"wall_s": 1.0, "monotonic_ns": 1, "boot_session_uuid": None}
PLAN = "plan-alpha"
CATALOG = draft_catalog()


# ------------------------------------------------------------------ fixtures


def floor_roster(prefix: str = "a", attempt: Any = 1, cell: str = "cell-decode") -> dict[str, Any]:
    """One floor cell: 10 absolute repeats, then 10 A,B,B,A null quads (50 members)."""

    members = []
    for index in range(1, 11):
        members.append({"run_id": f"{prefix}-r{index:02d}", "stage_id": "s01-abs",
                        "units": [{"cell_id": cell, "stratum": "repeat", "unit_id": f"r{index:02d}"}]})
    for quad in range(1, 11):
        for position in ("A1", "B1", "B2", "A2"):
            members.append({"run_id": f"{prefix}-q{quad:02d}-{position}", "stage_id": "s02-abba",
                            "units": [{"cell_id": cell, "stratum": "quad", "unit_id": f"q{quad:02d}"}]})
    members.append({"run_id": f"{prefix}-aux-neg8-01", "stage_id": "s00-neg8", "units": []})
    return {"plan_id": PLAN, "attempt": attempt, "chain_started_monotonic_ns": 100 * S,
            "members": members, "cells": [{"cell_id": cell, "target": True}]}


def spans_for(roster: Mapping[str, Any], start_s: int = 1000, length_s: int = 60) -> dict[str, Any]:
    spans = {}
    for index, member in enumerate(roster["members"]):
        a = (start_s + index * (length_s + 10)) * S
        spans[member["run_id"]] = {"monotonic_ns": [a, a + length_s * S],
                                   "request_monotonic_ns": [a + 5 * S, a + (length_s - 5) * S],
                                   "stage_id": member.get("stage_id")}
    return spans


def member_flag(code: str, run_id: str, *, family: str = "MEMBER_VALIDITY", klass: str = "NUMBER",
                level: str = "member", attempt: Any = 1, interval=None, observed=None) -> dict[str, Any]:
    return make_flag(
        code=code, family=family, klass=klass,
        scope=make_scope(level, plan_id=PLAN, attempt=attempt, run_id=run_id if level in ("member", "quad") else None,
                         stage_id="s02-abba" if level == "stage" else None),
        source=make_source("harvest", "test"),
        observed=observed if observed is not None else {"run": run_id},
        interval=make_interval(monotonic_ns=interval) if interval else None,
        emitted=EMITTED,
    )


def window_flag(code: str, *, family: str = "PACK_IDENTITY", klass: str = "NUMBER", interval=None,
                attempt: Any = 1) -> dict[str, Any]:
    return make_flag(
        code=code, family=family, klass=klass,
        scope=make_scope("window", plan_id=PLAN, attempt=attempt),
        source=make_source("harvest", "test"), observed={"code": code},
        interval=make_interval(monotonic_ns=interval) if interval else None, emitted=EMITTED,
    )


def cell(result: Mapping[str, Any], cell_id: str = "cell-decode") -> Mapping[str, Any]:
    return next(item for item in result["cells"] if item["cell_id"] == cell_id)


# ------------------------------------------------------------------ poison


class Poisoned(Exception):
    pass


class PoisonMapping(Mapping):
    """A mapping whose energy-like and value fields raise when read."""

    POISON = frozenset({"observed", "expected", "evidence", "detail", "energy_j", "phase_energy_j",
                        "power_w", "duration_s", "summary_metrics", "mean_power_w"})

    def __init__(self, data: Mapping[str, Any]) -> None:
        self._data = dict(data)

    def __getitem__(self, key: str) -> Any:
        if key in self.POISON:
            raise Poisoned(f"blind function read {key!r}")
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def get(self, key, default=None):  # noqa: D401 - Mapping.get would route through __getitem__
        if key in self.POISON:
            raise Poisoned(f"blind function read {key!r}")
        return self._data.get(key, default)


def poison_flag(flag: Mapping[str, Any]) -> PoisonMapping:
    return PoisonMapping(flag)


def poison_roster(roster: Mapping[str, Any]) -> PoisonMapping:
    members = [PoisonMapping({**m, "energy_j": 1.0, "summary_metrics": {}}) for m in roster["members"]]
    bundles = [PoisonMapping({**b, "phase_energy_j": 2.0}) for b in roster.get("bundles") or []]
    data = {**roster, "members": members, "energy_j": 3.0}
    if "bundles" in roster:
        data["bundles"] = bundles
    data["cells"] = [PoisonMapping({**c, "mean_power_w": 4.0}) for c in roster["cells"]]
    return PoisonMapping(data)


def poison_spans(spans: Mapping[str, Any]) -> dict[str, Any]:
    return {run_id: PoisonMapping({**entry, "duration_s": 60.0, "energy_j": 5.0}) for run_id, entry in spans.items()}


# ------------------------------------------------------------------ compute


class CellMinimumTests(unittest.TestCase):
    def test_clean_window_is_claim_usable_with_full_cells(self) -> None:
        roster = floor_roster()
        result = compute([], roster, spans_for(roster), CATALOG)
        self.assertTrue(result["claim_usable"])
        self.assertEqual((cell(result)["n_repeats"], cell(result)["n_quads"]), (10, 10))
        self.assertEqual(result["members_excluded"], [])

    def test_one_excluded_repeat_keeps_cell_with_nine(self) -> None:
        roster = floor_roster()
        result = compute([member_flag("member.anchor_not_bounded", "a-r03")], roster, spans_for(roster), CATALOG)
        self.assertEqual((cell(result)["n_repeats"], cell(result)["n_quads"]), (9, 10))
        self.assertTrue(cell(result)["resolvable"])
        self.assertTrue(result["claim_usable"])
        self.assertEqual(result["members_excluded"][0]["run_id"], "a-r03")
        self.assertEqual(result["members_excluded"][0]["position"], 2)

    def test_flagged_quad_member_drops_whole_quad(self) -> None:
        roster = floor_roster()
        result = compute([member_flag("battery.member_span", "a-q04-B2", family="PHYSICS_IN_SPAN",
                                      klass="PHYSICS")], roster, spans_for(roster), CATALOG)
        self.assertEqual(cell(result)["n_quads"], 9)
        dropped = cell(result)["dropped_units"]
        self.assertEqual(len(dropped), 1)
        self.assertEqual(dropped[0]["unit_id"], "q04")
        self.assertEqual(sorted(dropped[0]["run_ids"]), sorted(f"a-q04-{p}" for p in ("A1", "B1", "B2", "A2")))
        self.assertNotIn("q04", cell(result)["kept_units"]["quad"])

    def test_three_lost_quads_put_cell_below_minimum(self) -> None:
        roster = floor_roster()
        flags = [member_flag("member.admission_aborted", f"a-q0{q}-A1") for q in (1, 5, 9)]
        result = compute(flags, roster, spans_for(roster), CATALOG)
        self.assertEqual(cell(result)["n_quads"], 7)
        self.assertFalse(cell(result)["resolvable"])
        self.assertFalse(result["claim_usable"])
        self.assertEqual(result["reasons"], ["cell.below_minimum"])

    def test_two_lost_quads_and_two_lost_repeats_still_resolve(self) -> None:
        roster = floor_roster()
        flags = [member_flag("member.admission_aborted", "a-q01-A1"), member_flag("member.admission_aborted", "a-q02-B1"),
                 member_flag("member.anchor_not_bounded", "a-r01"), member_flag("member.anchor_not_bounded", "a-r10")]
        result = compute(flags, roster, spans_for(roster), CATALOG)
        self.assertEqual((cell(result)["n_repeats"], cell(result)["n_quads"]), (8, 8))
        self.assertTrue(result["claim_usable"])

    def test_contrast_cell_needs_eight_of_ten_quads(self) -> None:
        members = []
        for quad in range(1, 11):
            for position in ("A1", "B1", "B2", "A2"):
                members.append({"run_id": f"g-b{quad:02d}-{position}", "stage_id": "gamma",
                                "units": [{"cell_id": "contrast-decode", "stratum": "quad", "unit_id": f"b{quad:02d}"}]})
        roster = {"plan_id": PLAN, "attempt": 1, "members": members, "cells": [{"cell_id": "contrast-decode"}]}
        two = compute([member_flag("contention.request_overlap", f"g-b0{q}-B1") for q in (1, 2)], roster, {}, CATALOG)
        self.assertTrue(two["claim_usable"])
        self.assertEqual(cell(two, "contrast-decode")["n_quads"], 8)
        three = compute([member_flag("contention.request_overlap", f"g-b0{q}-B1") for q in (1, 2, 3)], roster, {},
                        CATALOG)
        self.assertFalse(three["claim_usable"])

    def test_catalog_rule_and_cell_minimum_override_the_default(self) -> None:
        document = draft_catalog_document()
        document["rules"]["cell_unit_minimum"] = 10
        import json

        strict = catalog_from_bytes(json.dumps(document).encode())
        roster = floor_roster()
        result = compute([member_flag("member.anchor_not_bounded", "a-r03")], roster, spans_for(roster), strict)
        self.assertFalse(result["claim_usable"])
        roster["cells"] = [{"cell_id": "cell-decode", "minimum": {"repeat": 9, "quad": 10}}]
        result = compute([member_flag("member.anchor_not_bounded", "a-r03")], roster, spans_for(roster), strict)
        self.assertTrue(result["claim_usable"])

    def test_non_target_cell_does_not_block_the_window(self) -> None:
        roster = floor_roster()
        roster["cells"] = [{"cell_id": "cell-decode", "target": False}]
        flags = [member_flag("member.admission_aborted", f"a-q0{q}-A1") for q in (1, 2, 3)]
        result = compute(flags, roster, spans_for(roster), CATALOG)
        self.assertFalse(cell(result)["resolvable"])
        self.assertTrue(result["claim_usable"])


class EffectTests(unittest.TestCase):
    def test_window_excluding_flag_makes_window_not_claim_usable(self) -> None:
        roster = floor_roster()
        result = compute([window_flag("pack.identity_mismatch")], roster, spans_for(roster), CATALOG)
        self.assertFalse(result["claim_usable"])
        self.assertEqual(result["reasons"], ["pack.identity_mismatch"])
        self.assertEqual(result["members_excluded"], [])

    def test_disclosed_flags_change_nothing_but_counts(self) -> None:
        roster = floor_roster()
        flags = [window_flag("network_time.off_output", family="DIAGNOSTIC", klass="REPRESENTATION"),
                 member_flag("contention.kernel_task_share", "a-r01", family="DIAGNOSTIC", klass="PHYSICS")]
        result = compute(flags, roster, spans_for(roster), CATALOG)
        self.assertTrue(result["claim_usable"])
        self.assertEqual(result["members_excluded"], [])
        self.assertEqual(result["flag_counts"]["by_effect"], {DISCLOSE: 2})

    def test_unknown_code_is_unclassified_and_blocks_release_not_collection(self) -> None:
        roster = floor_roster()
        result = compute([member_flag("brand.new_code", "a-r01")], roster, spans_for(roster), CATALOG)
        self.assertEqual(result["unclassified"], ["brand.new_code"])
        self.assertTrue(result["release_blocked"])
        self.assertTrue(result["claim_usable"])
        self.assertEqual(result["members_excluded"], [])

    def test_foreign_attempt_flags_are_ignored(self) -> None:
        roster = floor_roster()
        result = compute([window_flag("pack.identity_mismatch", attempt=2)], roster, spans_for(roster), CATALOG)
        self.assertTrue(result["claim_usable"])
        self.assertEqual(result["flag_counts"]["foreign_scope"], 1)

    def test_window_interval_flag_excludes_only_overlapping_members(self) -> None:
        roster = floor_roster()
        spans = spans_for(roster)
        target = spans["a-q03-B1"]["monotonic_ns"]
        flag = window_flag("clock.step_overlap", family="PHYSICS_IN_SPAN", klass="PHYSICS",
                           interval=(target[0] + S, target[0] + 2 * S))
        result = compute([flag], roster, spans, CATALOG)
        self.assertEqual([m["run_id"] for m in result["members_excluded"]], ["a-q03-B1"])
        self.assertEqual(cell(result)["n_quads"], 9)

    def test_member_span_unknown_is_treated_as_overlapping(self) -> None:
        roster = floor_roster()
        spans = spans_for(roster)
        del spans["a-r05"]
        flag = window_flag("clock.step_overlap", family="PHYSICS_IN_SPAN", klass="PHYSICS", interval=(1, 2))
        result = compute([flag], roster, spans, CATALOG)
        self.assertEqual([m["run_id"] for m in result["members_excluded"]], ["a-r05"])
        self.assertEqual(result["span_unknown"], ["a-r05"])

    def test_stage_level_member_effect_without_interval_excludes_the_stage(self) -> None:
        roster = floor_roster()
        result = compute([member_flag("member.status_not_succeeded", "", level="stage")], roster,
                         spans_for(roster), CATALOG)
        self.assertEqual(len(result["members_excluded"]), 40)
        self.assertFalse(result["claim_usable"])

    def test_duplicate_flag_ids_count_once(self) -> None:
        roster = floor_roster()
        flag = member_flag("member.anchor_not_bounded", "a-r01")
        result = compute([flag, dict(flag)], roster, spans_for(roster), CATALOG)
        self.assertEqual(result["flag_counts"]["by_code"], {"member.anchor_not_bounded": 1})


class RosterRuleTests(unittest.TestCase):
    def bundles(self, roster):
        return [{"bundle_id": f"b-{m['run_id']}", "run_id": m["run_id"], "attempt": 1,
                 "created_monotonic_ns": 200 * S} for m in roster["members"]]

    def test_foreign_attempt_and_pre_chain_bundles_are_ignored(self) -> None:
        roster = floor_roster()
        bundles = self.bundles(roster)
        bundles.append({"bundle_id": "old", "run_id": "a-r01", "attempt": 0, "created_monotonic_ns": 200 * S})
        bundles.append({"bundle_id": "early", "run_id": "a-r02", "attempt": 1, "created_monotonic_ns": 50 * S})
        roster["bundles"] = bundles
        result = compute([], roster, spans_for(roster), CATALOG)
        ignored = {(item["bundle_id"], item["code"]) for item in result["bundles_ignored"]}
        self.assertEqual(ignored, {("old", "roster.foreign_attempt"), ("early", "roster.before_chain_started")})
        self.assertTrue(result["claim_usable"])
        self.assertEqual(result["members_excluded"], [])

    def test_bundle_from_before_chain_start_cannot_stand_in_for_a_member(self) -> None:
        roster = floor_roster()
        bundles = [b for b in self.bundles(roster) if b["run_id"] != "a-r02"]
        bundles.append({"bundle_id": "early", "run_id": "a-r02", "attempt": 1, "created_monotonic_ns": 50 * S})
        roster["bundles"] = bundles
        result = compute([], roster, spans_for(roster), CATALOG)
        self.assertEqual(result["members_excluded"][0]["run_id"], "a-r02")
        self.assertEqual(result["members_excluded"][0]["codes"], ["member.bytes_missing"])

    def test_missing_bundle_excludes_member_and_its_quad(self) -> None:
        roster = floor_roster()
        roster["bundles"] = [b for b in self.bundles(roster) if b["run_id"] != "a-q07-A2"]
        result = compute([], roster, spans_for(roster), CATALOG)
        self.assertEqual(cell(result)["n_quads"], 9)
        self.assertEqual(cell(result)["dropped_units"][0]["codes"], ["member.bytes_missing"])

    def test_bundle_not_in_plan_is_ignored(self) -> None:
        roster = floor_roster()
        roster["bundles"] = self.bundles(roster) + [{"bundle_id": "stray", "run_id": "zz", "attempt": 1,
                                                     "created_monotonic_ns": 200 * S}]
        result = compute([], roster, spans_for(roster), CATALOG)
        self.assertEqual(result["bundles_ignored"], [{"bundle_id": "stray", "run_id": "zz",
                                                      "code": "roster.not_in_plan"}])


class BlindnessTests(unittest.TestCase):
    def test_poison_mapping_does_raise_when_read(self) -> None:
        with self.assertRaises(Poisoned):
            dict(poison_flag(member_flag("member.anchor_not_bounded", "a-r01")))

    def test_compute_never_reads_energy_or_observed(self) -> None:
        roster = floor_roster()
        roster["bundles"] = [{"bundle_id": f"b-{m['run_id']}", "run_id": m["run_id"], "attempt": 1,
                              "created_monotonic_ns": 200 * S} for m in roster["members"]]
        spans = spans_for(roster)
        flags = [
            member_flag("member.anchor_energy_envelope_exceeded", "a-r02", observed={"energy_j": 12.5}),
            member_flag("battery.member_span", "a-q02-A1", family="PHYSICS_IN_SPAN", klass="PHYSICS"),
            window_flag("clock.step_overlap", family="PHYSICS_IN_SPAN", klass="PHYSICS",
                        interval=tuple(spans["a-r09"]["monotonic_ns"])),
            window_flag("network_time.off_output", family="DIAGNOSTIC", klass="REPRESENTATION"),
            member_flag("brand.new_code", "a-r04"),
        ]
        clear = compute(flags, roster, spans, CATALOG)
        blind = compute([poison_flag(f) for f in flags], poison_roster(roster), poison_spans(spans), CATALOG)
        self.assertEqual(render(blind), render(clear))
        self.assertEqual({m["run_id"] for m in blind["members_excluded"]}, {"a-r02", "a-q02-A1", "a-r09"})


class DeterminismTests(unittest.TestCase):
    def test_identical_inputs_give_identical_bytes_in_any_order(self) -> None:
        roster = floor_roster()
        roster["bundles"] = [{"bundle_id": f"b-{m['run_id']}", "run_id": m["run_id"], "attempt": 1,
                              "created_monotonic_ns": 200 * S} for m in roster["members"]]
        spans = spans_for(roster)
        flags = [member_flag("member.anchor_not_bounded", f"a-r0{i}") for i in range(1, 4)]
        flags += [member_flag("battery.member_span", "a-q05-A1", family="PHYSICS_IN_SPAN", klass="PHYSICS"),
                  window_flag("calibration.no_bracket", family="CALIBRATION")]
        expected = render(compute(flags, roster, spans, CATALOG))
        generator = random.Random(7)
        for _ in range(5):
            shuffled_flags = list(flags)
            generator.shuffle(shuffled_flags)
            shuffled_roster = dict(roster, bundles=generator.sample(roster["bundles"], len(roster["bundles"])))
            shuffled_spans = dict(generator.sample(list(spans.items()), len(spans)))
            self.assertEqual(render(compute(shuffled_flags, shuffled_roster, shuffled_spans, CATALOG)), expected)


class FirstClaimUsableTests(unittest.TestCase):
    def test_first_claim_usable_attempt_is_analysed(self) -> None:
        attempts = [{"attempt": 1, "claim_usable": False}, {"attempt": 2, "claim_usable": True},
                    {"attempt": 3, "claim_usable": True}]
        self.assertEqual(first_claim_usable(attempts), 2)
        self.assertIsNone(first_claim_usable([{"attempt": 1, "claim_usable": False}]))


# ------------------------------------------------------------------ physics in span


def one_span(start_s: float, stop_s: float, request=None) -> dict[str, Any]:
    entry = {"monotonic_ns": [int(start_s * S), int(stop_s * S)], "stage_id": "s02"}
    if request:
        entry["request_monotonic_ns"] = [int(request[0] * S), int(request[1] * S)]
    return {"m1": entry}


def publication(t_s: float, inst: int = 0, avg: int = 0, charging: bool = False, external: bool = True, **extra):
    return {"monotonic_ns": int(t_s * S), "instant_amperage_ma": inst, "amperage_ma": avg,
            "is_charging": charging, "external_connected": external, **extra}


def codes(flags) -> list[str]:
    for flag in flags:
        assert validate_flag(flag) == [], validate_flag(flag)
    return sorted(flag["code"] for flag in flags)


class BatterySpanTests(unittest.TestCase):
    def test_float_publications_pass(self) -> None:
        pubs = [publication(t) for t in (0, 60, 120, 180)]
        self.assertEqual(battery_span_flags(pubs, one_span(70, 130)), [])

    def test_in_force_publication_out_of_float_flags_member(self) -> None:
        # The 09-30 0555Z reading: AC attached, -447 mA. It publishes before
        # the span starts and is still in force at the start.
        pubs = [publication(0), publication(60, inst=-447, avg=-120), publication(120), publication(180)]
        flags = battery_span_flags(pubs, one_span(70, 130))
        self.assertEqual(codes(flags), ["battery.member_span"])
        self.assertEqual(flags[0]["scope"]["run_id"], "m1")
        self.assertEqual(flags[0]["interval"]["monotonic_ns"], [70 * S, 130 * S])
        self.assertEqual(flags[0]["observed"]["violations"][0]["reasons"], ["instant_amperage"])

    def test_publication_after_the_end_is_in_force_too(self) -> None:
        pubs = [publication(0), publication(60), publication(131, avg=250)]
        self.assertEqual(codes(battery_span_flags(pubs, one_span(70, 130))), ["battery.member_span"])

    def test_charging_or_disconnected_flags_member(self) -> None:
        for kwargs in ({"charging": True}, {"external": False}):
            pubs = [publication(0), publication(60, **kwargs), publication(120)]
            with self.subTest(**kwargs):
                self.assertEqual(codes(battery_span_flags(pubs, one_span(70, 110))), ["battery.member_span"])

    def test_publication_gap_over_120_s_flags_unmeasured(self) -> None:
        pubs = [publication(0), publication(130), publication(190)]
        self.assertEqual(codes(battery_span_flags(pubs, one_span(70, 140))), ["battery.unmeasured"])
        self.assertEqual(codes(battery_span_flags([publication(0)], one_span(10, 20))), ["battery.unmeasured"])
        missing = [publication(0), dict(publication(60), instant_amperage_ma=None), publication(120)]
        self.assertEqual(codes(battery_span_flags(missing, one_span(70, 110))), ["battery.unmeasured"])

    def test_accumulator_rule_only_when_units_confirmed(self) -> None:
        pubs = [publication(0, accumulated_battery_power=0, battery_power_accumulator_count=100, voltage_mv=12180),
                publication(60, accumulated_battery_power=300, battery_power_accumulator_count=110, voltage_mv=12180),
                publication(120, accumulated_battery_power=300, battery_power_accumulator_count=110, voltage_mv=12180)]
        self.assertEqual(battery_span_flags(pubs, one_span(10, 50)), [])
        flags = battery_span_flags(pubs, one_span(10, 50), accumulator={"scale_w_per_unit": 1.0, "voltage_v": 12.18})
        self.assertEqual(codes(flags), ["battery.accumulator_excursion"])
        self.assertAlmostEqual(flags[0]["observed"]["excursions"][0]["mean_w"], 30.0)
        low = battery_span_flags(pubs, one_span(10, 50), accumulator={"scale_w_per_unit": 0.01, "voltage_v": 12.18})
        self.assertEqual(low, [])


class ThermalSpanTests(unittest.TestCase):
    def samples(self, levels):
        return [{"monotonic_ns": int(i * 5 * S), "level": level} for i, level in enumerate(levels)]

    def test_nominal_level_passes(self) -> None:
        self.assertEqual(thermal_span_flags(self.samples([0] * 20), one_span(12, 60)), [])

    def test_nonzero_level_in_span_flags_member(self) -> None:
        levels = [0] * 20
        levels[5] = 1
        flags = thermal_span_flags(self.samples(levels), one_span(12, 60))
        self.assertEqual(codes(flags), ["thermal.os_level_nonzero"])
        self.assertEqual(thermal_span_flags(self.samples(levels), one_span(40, 60)), [])

    def test_failed_probe_or_gap_flags_unmeasured(self) -> None:
        levels = [0] * 20
        levels[4] = None
        self.assertEqual(codes(thermal_span_flags(self.samples(levels), one_span(12, 60))), ["thermal.unmeasured"])
        sparse = [{"monotonic_ns": 0, "level": 0}, {"monotonic_ns": 40 * S, "level": 0}]
        self.assertEqual(codes(thermal_span_flags(sparse, one_span(10, 30))), ["thermal.unmeasured"])


class ContentionSpanTests(unittest.TestCase):
    def interval(self, a, b, *processes):
        return {"monotonic_ns": [int(a * S), int(b * S)], "processes": list(processes)}

    def test_quiet_intervals_pass(self) -> None:
        intervals = [self.interval(t, t + 10, {"pid": 1, "comm": "launchd", "cpu_s_per_s": 0.001})
                     for t in range(0, 100, 10)]
        self.assertEqual(contention_span_flags(intervals, one_span(10, 60, request=(15, 55))), [])

    def test_outside_process_over_limit_flags_member(self) -> None:
        intervals = [self.interval(t, t + 10) for t in range(0, 100, 10)]
        intervals[3] = self.interval(30, 40, {"pid": 99, "comm": "fseventsd", "cpu_s_per_s": 1.84})
        flags = contention_span_flags(intervals, one_span(10, 60, request=(15, 55)))
        self.assertEqual(codes(flags), ["contention.request_overlap"])
        self.assertEqual(flags[0]["observed"]["offenders"][0]["comm"], "fseventsd")
        self.assertEqual(flags[0]["interval"]["monotonic_ns"], [15 * S, 55 * S])

    def test_interval_outside_the_request_does_not_flag(self) -> None:
        intervals = [self.interval(t, t + 10) for t in range(0, 100, 10)]
        intervals[0] = self.interval(0, 10, {"pid": 99, "comm": "mediaanalysisd", "cpu_s_per_s": 1.14})
        self.assertEqual(contention_span_flags(intervals, one_span(10, 60, request=(15, 55))), [])

    def test_kernel_task_and_measurement_tree_are_not_contention(self) -> None:
        intervals = [self.interval(t, t + 10, {"pid": 0, "comm": "kernel_task", "cpu_s_per_s": 0.4},
                                   {"pid": 7, "comm": "powermetrics", "cpu_s_per_s": 0.3, "outside": False})
                     for t in range(0, 100, 10)]
        flags = contention_span_flags(intervals, one_span(10, 60, request=(15, 55)))
        self.assertEqual(codes(flags), ["contention.kernel_task_share"])
        self.assertEqual(CATALOG.effect("contention.kernel_task_share"), DISCLOSE)

    def test_uncovered_request_flags_unmeasured(self) -> None:
        intervals = [self.interval(0, 10), self.interval(10, 20), self.interval(40, 60)]
        self.assertEqual(codes(contention_span_flags(intervals, one_span(10, 60, request=(15, 55)))),
                         ["contention.unmeasured"])
        self.assertEqual(CATALOG.effect("contention.unmeasured"), EXCLUDE_MEMBER)


class ClockSpanTests(unittest.TestCase):
    def test_step_inside_span_flags_member(self) -> None:
        flags = clock_span_flags([{"monotonic_ns": [30 * S, 31 * S]}], one_span(10, 60))
        self.assertEqual(codes(flags), ["clock.step_overlap"])
        self.assertEqual(clock_span_flags([{"monotonic_ns": [70 * S, 71 * S]}], one_span(10, 60)), [])

    def test_step_in_calibration_capture_flags_window(self) -> None:
        flags = clock_span_flags([{"monotonic_ns": 5 * S}], {}, calibration_spans={"pre": [0, 10 * S]})
        self.assertEqual(codes(flags), ["clock.step_overlap_calibration"])
        self.assertEqual(flags[0]["scope"]["level"], "window")

    def test_clock_systematic_needs_majority_of_five(self) -> None:
        self.assertEqual(clock_systematic_flags({"a": "bounded", "b": "unknown", "c": "unknown", "d": "unknown"}), [])
        statuses = {"a": "bounded", "b": "bounded", "c": "unknown", "d": "unknown", "e": "exceeded"}
        self.assertEqual(codes(clock_systematic_flags(statuses)), ["clock.systematic"])
        statuses["f"] = "bounded"
        self.assertEqual(clock_systematic_flags(statuses), [])


class EndToEndTests(unittest.TestCase):
    def test_physics_flags_feed_compute_and_drop_the_quad(self) -> None:
        roster = floor_roster()
        spans = spans_for(roster)
        a, b = spans["a-q06-B2"]["monotonic_ns"]
        last = max(entry["monotonic_ns"][1] for entry in spans.values())
        pubs = [publication(t / S) for t in range(0, last + 120 * S, 60 * S)]
        for pub in pubs:
            if a <= pub["monotonic_ns"] <= b:
                pub["instant_amperage_ma"] = -447
        flags = battery_span_flags(pubs, spans, context={"plan_id": PLAN, "attempt": 1})
        excluded = {f["scope"]["run_id"] for f in flags if f["code"] == "battery.member_span"}
        self.assertIn("a-q06-B2", excluded)
        self.assertTrue(excluded <= {f"a-q06-{p}" for p in ("A1", "B1", "B2", "A2")} | {"a-q05-A2", "a-q07-A1"})
        self.assertEqual([f for f in flags if f["code"] == "battery.unmeasured"], [])
        result = compute(flags, roster, spans, CATALOG)
        self.assertNotIn("q06", cell(result)["kept_units"]["quad"])
        self.assertTrue(result["claim_usable"])


if __name__ == "__main__":
    unittest.main()
