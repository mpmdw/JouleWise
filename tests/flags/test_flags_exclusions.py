"""The blind exclusion function and the cell minimum."""

from __future__ import annotations

import random
import unittest
from collections.abc import Mapping
from typing import Any, Iterator

from joulewise.flags.catalog import DISCLOSE, draft_catalog, draft_catalog_document, catalog_from_bytes
from joulewise.flags.exclusions import compute, first_claim_usable, render
from joulewise.flags.schema import make_flag, make_interval, make_scope, make_source

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

    def test_catalog_rule_holds_and_a_roster_minimum_can_only_raise_it(self) -> None:
        document = draft_catalog_document()
        document["rules"]["cell_unit_minimum"] = 10
        import json

        strict = catalog_from_bytes(json.dumps(document).encode())
        roster = floor_roster()
        result = compute([member_flag("member.anchor_not_bounded", "a-r03")], roster, spans_for(roster), strict)
        self.assertFalse(result["claim_usable"])
        # A roster cannot lower the sealed rule (review 2026-10-05).
        roster["cells"] = [{"cell_id": "cell-decode", "minimum": {"repeat": 9, "quad": 10}}]
        result = compute([member_flag("member.anchor_not_bounded", "a-r03")], roster, spans_for(roster), strict)
        self.assertFalse(result["claim_usable"])
        self.assertEqual(cell(result)["minimum"], {"repeat": 10, "quad": 10})
        # It can raise it.
        roster["cells"] = [{"cell_id": "cell-decode", "minimum": {"repeat": 10}}]
        result = compute([member_flag("member.anchor_not_bounded", "a-r03")], roster, spans_for(roster), CATALOG)
        self.assertFalse(result["claim_usable"])
        self.assertEqual(cell(result)["minimum"], {"repeat": 10, "quad": 8})

    def test_non_target_cell_does_not_block_the_window(self) -> None:
        roster = floor_roster()
        roster["cells"] = [{"cell_id": "cell-decode", "target": False}]
        flags = [member_flag("member.admission_aborted", f"a-q0{q}-A1") for q in (1, 2, 3)]
        result = compute(flags, roster, spans_for(roster), CATALOG)
        self.assertFalse(cell(result)["resolvable"])
        self.assertTrue(result["claim_usable"])


class SealedCellMinimumTests(unittest.TestCase):
    """The cell rule under the block-5 catalog of this tree, whose minimum is 5.

    ``CellMinimumTests`` above runs the same function under the draft catalog,
    whose rule is the code's fallback ``DEFAULT_CELL_UNIT_MINIMUM`` (8); it
    proves the mechanism.  This class proves the registered value: seal gate
    ruling SG-1 (2026-10-07) set ``rules.cell_unit_minimum`` to 5 in
    ``configs/campaigns/v5_claim_25g83/flag_catalog.json``, the smallest count
    for which the registered floor estimator's guard
    (``joulewise.detection_floor.small_sample_guard_factor``) is defined.
    """

    @classmethod
    def setUpClass(cls) -> None:
        from pathlib import Path

        from joulewise.flags.catalog import SEALED_CATALOG_RELATIVE_PATH, load_catalog

        sealed = Path(__file__).resolve().parents[2] / SEALED_CATALOG_RELATIVE_PATH
        if not sealed.exists():
            raise unittest.SkipTest("the block-5 catalog is not in this tree")
        cls.catalog = load_catalog(sealed)

    def lose(self, stratum: str, count: int, roster=None) -> Mapping[str, Any]:
        """One floor cell with one member removed from each of ``count`` units of ``stratum``."""

        roster = floor_roster() if roster is None else roster
        run_ids = [f"a-q{index:02d}-B1" if stratum == "quad" else f"a-r{index:02d}" for index in range(1, count + 1)]
        flags = [member_flag("member.admission_aborted", run_id) for run_id in run_ids]
        return compute(flags, roster, spans_for(roster), self.catalog)

    def test_five_kept_units_are_usable_and_four_are_not(self) -> None:
        for stratum, counter in (("quad", "n_quads"), ("repeat", "n_repeats")):
            with self.subTest(stratum=stratum):
                five = self.lose(stratum, 5)
                self.assertEqual(cell(five)["minimum"], {"quad": 5, "repeat": 5})
                self.assertEqual((cell(five)[counter], cell(five)["resolvable"], five["claim_usable"], five["reasons"]),
                                 (5, True, True, []))
                four = self.lose(stratum, 6)
                self.assertEqual((cell(four)[counter], cell(four)["resolvable"], four["claim_usable"], four["reasons"]),
                                 (4, False, False, ["cell.below_minimum"]))

    def test_three_lost_quads_no_longer_remove_the_window(self) -> None:
        # Under the minimum of 8 this was cell.below_minimum
        # (CellMinimumTests.test_three_lost_quads_put_cell_below_minimum).
        result = self.lose("quad", 3)
        self.assertEqual((cell(result)["n_quads"], cell(result)["n_repeats"]), (7, 10))
        self.assertEqual((result["claim_usable"], result["reasons"]), (True, []))
        self.assertEqual(len(result["members_excluded"]), 3)

    def test_a_roster_can_still_raise_the_minimum_above_5_and_never_lower_it(self) -> None:
        roster = floor_roster()
        roster["cells"] = [{"cell_id": "cell-decode", "minimum": {"quad": 8, "repeat": 1}}]
        result = self.lose("quad", 3, roster)
        self.assertEqual(cell(result)["minimum"], {"quad": 8, "repeat": 5})
        self.assertEqual(result["reasons"], ["cell.below_minimum"])


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

    def test_a_bundle_no_stamp_places_is_unplaced_not_early(self) -> None:
        """Rehearsal round 1, B7: a None creation stamp is not evidence the bundle predates the chain."""
        roster = floor_roster()
        bundles = [b for b in self.bundles(roster) if b["run_id"] != "a-r02"]
        bundles.append({"bundle_id": "unplaced", "run_id": "a-r02", "attempt": 1, "created_monotonic_ns": None})
        roster["bundles"] = bundles
        result = compute([], roster, spans_for(roster), CATALOG)
        self.assertEqual(result["bundles_ignored"], [{"bundle_id": "unplaced", "run_id": "a-r02",
                                                      "code": "roster.creation_unplaced"}])
        # Still not used: the member has no admissible bundle.
        self.assertEqual(result["members_excluded"][0]["run_id"], "a-r02")
        self.assertEqual(result["members_excluded"][0]["codes"], ["member.bytes_missing"])

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
        attempts = [{"attempt": 1, "claim_usable": False, "release_blocked": False},
                    {"attempt": 2, "claim_usable": True, "release_blocked": False},
                    {"attempt": 3, "claim_usable": True, "release_blocked": False}]
        self.assertEqual(first_claim_usable(attempts), 2)
        self.assertIsNone(first_claim_usable([{"attempt": 1, "claim_usable": False}]))



class GammaMidpointLostTests(unittest.TestCase):
    """Orchestrator ruling Q11 (2026-10-07): on GAMMA only, neg8.midpoint_lost is not claim-usable."""

    GAMMA = "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
    ALPHA = "d117_floor_qwen3-1p7b_v5"
    BETA = "d117_floor_qwen3-8b_v5"

    def attempt(self, pack_id: Any, attempt: int, *, lost: bool) -> dict[str, Any]:
        roster = dict(floor_roster(attempt=attempt), pack_id=pack_id)
        flags = [window_flag("neg8.midpoint_lost", family="NEG8", attempt=attempt)] if lost else []
        return compute(flags, roster, spans_for(roster), CATALOG)

    def test_the_rule_is_registered_for_gamma_only(self) -> None:
        from joulewise.flags.exclusions import GAMMA_PACK_ID, PACK_SCOPED_WINDOW_REASONS
        self.assertEqual(GAMMA_PACK_ID, self.GAMMA)
        self.assertEqual(dict(PACK_SCOPED_WINDOW_REASONS),
                         {self.GAMMA: {"neg8.midpoint_lost": "neg8.midpoint_lost_primary"}})
        self.assertEqual(CATALOG.entry("neg8.midpoint_lost")["effect"], DISCLOSE)

    def test_gamma_with_a_lost_midpoint_is_not_claim_usable_and_a_later_clean_attempt_is_analysed(self) -> None:
        first = self.attempt(self.GAMMA, 1, lost=True)
        self.assertFalse(first["claim_usable"])
        self.assertEqual(first["reasons"], ["neg8.midpoint_lost_primary"])
        self.assertEqual(first["members_excluded"], [])
        self.assertFalse(first["release_blocked"])
        second = self.attempt(self.GAMMA, 2, lost=False)
        self.assertTrue(second["claim_usable"])
        attempts = [{"attempt": 1, "claim_usable": first["claim_usable"],
                     "release_blocked": first["release_blocked"]},
                    {"attempt": 2, "claim_usable": second["claim_usable"],
                     "release_blocked": second["release_blocked"]}]
        self.assertEqual(first_claim_usable(attempts), 2)

    def test_the_floor_packs_keep_the_flag_disclose(self) -> None:
        for pack_id in (self.ALPHA, self.BETA, None):
            with self.subTest(pack_id=pack_id):
                result = self.attempt(pack_id, 1, lost=True)
                self.assertTrue(result["claim_usable"])
                self.assertEqual(result["reasons"], [])
                self.assertEqual(result["flag_counts"]["by_code"], {"neg8.midpoint_lost": 1})
                self.assertEqual(first_claim_usable([{"attempt": 1, "claim_usable": result["claim_usable"],
                                                      "release_blocked": result["release_blocked"]}]), 1)

    def test_a_foreign_attempts_flag_does_not_exclude_gamma(self) -> None:
        roster = dict(floor_roster(attempt=2), pack_id=self.GAMMA)
        result = compute([window_flag("neg8.midpoint_lost", family="NEG8", attempt=1)], roster,
                         spans_for(roster), CATALOG)
        self.assertTrue(result["claim_usable"])

    def test_the_rule_reads_only_the_pack_id_and_the_code(self) -> None:
        roster = dict(floor_roster(), pack_id=self.GAMMA)
        spans = spans_for(roster)
        flags = [window_flag("neg8.midpoint_lost", family="NEG8")]
        clear = compute(flags, roster, spans, CATALOG)
        blind = compute([poison_flag(f) for f in flags], poison_roster(roster), poison_spans(spans), CATALOG)
        self.assertEqual(render(blind), render(clear))
        self.assertEqual(blind["reasons"], ["neg8.midpoint_lost_primary"])

    def test_the_harvest_hands_compute_the_pack_id(self) -> None:
        from joulewise.b5 import harvest
        roster, _spans = harvest.l4_exclusion_inputs({"pack_id": self.GAMMA, "cells": [], "members": []}, {},
                                                    plan_id=PLAN, attempt=1)
        self.assertEqual(roster["pack_id"], self.GAMMA)


if __name__ == "__main__":
    unittest.main()
