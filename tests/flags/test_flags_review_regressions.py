"""Regressions for the 2026-10-05 independent review of the flag package.

Each test fails on the reviewed head (78914f74) and passes after the fix.
Collector findings (1, 2, 4 and the collector mutation survivors) are in
``test_flags_collect.py``; this file holds the exclusion, schema, sink and
catalog findings (5 to 9) and the exclusion mutation survivors (10).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from joulewise.flags.catalog import (
    NEVER_CLASSIFIED_CODES,
    CatalogError,
    catalog_from_bytes,
    draft_catalog,
    draft_catalog_document,
)
from joulewise.flags.exclusions import compute, contention_span_flags, first_claim_usable
from joulewise.flags.schema import make_flag, make_interval, make_scope, make_source, validate_flag
from joulewise.flags.sink import FlagSink, read_flags

CATALOG = draft_catalog()
EMITTED = {"wall_s": 1.0, "monotonic_ns": 1, "boot_session_uuid": None}
S = 1_000_000_000


def roster() -> dict[str, Any]:
    """The reviewer's probe roster: 10 repeats (stage s_rep), 10 quads (s_quad)."""

    members = []
    for i in range(10):
        members.append({"run_id": f"r{i}", "stage_id": "s_rep",
                        "units": [{"cell_id": "c", "stratum": "repeat", "unit_id": f"u{i}"}]})
    for q in range(10):
        for k in range(4):
            members.append({"run_id": f"q{q}_{k}", "stage_id": "s_quad",
                            "units": [{"cell_id": "c", "stratum": "quad", "unit_id": f"q{q}"}]})
    return {"plan_id": "P", "attempt": 1, "chain_started_monotonic_ns": None, "members": members,
            "cells": [{"cell_id": "c"}]}


SPANS = {m["run_id"]: {"monotonic_ns": [i * 100, i * 100 + 50]} for i, m in enumerate(roster()["members"])}


def flag(code: str, level: str, *, interval=None, observed=None, **scope) -> dict[str, Any]:
    return make_flag(
        code=code, family=CATALOG.entry(code)["family"] or "DIAGNOSTIC", klass="PHYSICS",
        scope=make_scope(level, plan_id="P", attempt=1, **scope), source=make_source("window", "probe"),
        observed=observed, interval=make_interval(monotonic_ns=interval) if interval else None, emitted=EMITTED,
    )


def excluded(result) -> list[str]:
    return [m["run_id"] for m in result["members_excluded"]]


class StageScopeTests(unittest.TestCase):
    """Finding 5: a stage flag naming no roster stage excluded nobody, silently."""

    def test_unknown_stage_is_unmatched_and_applied_conservatively(self) -> None:
        result = compute([flag("contention.request_overlap", "stage", stage_id="S_REP")], roster(), SPANS, CATALOG)
        self.assertEqual(result["flag_counts"]["unmatched_member"], 1)
        self.assertEqual(len(result["members_excluded"]), 50)
        self.assertFalse(result["claim_usable"])

    def test_unknown_stage_with_an_interval_excludes_only_overlapping_members(self) -> None:
        result = compute([flag("contention.request_overlap", "stage", stage_id="S_REP", interval=[0, 60])],
                         roster(), SPANS, CATALOG)
        self.assertEqual(excluded(result), ["r0"])
        self.assertEqual(result["flag_counts"]["unmatched_member"], 1)

    def test_quad_flag_without_run_id_is_unmatched_and_applied(self) -> None:
        result = compute([flag("battery.member_span", "quad", interval=[1000, 1010])], roster(), SPANS, CATALOG)
        self.assertEqual(excluded(result), ["q0_0"])
        self.assertEqual(result["flag_counts"]["unmatched_member"], 1)

    def test_known_stage_is_unchanged(self) -> None:
        result = compute([flag("contention.request_overlap", "stage", stage_id="s_rep")], roster(), SPANS, CATALOG)
        self.assertEqual(len(result["members_excluded"]), 10)
        self.assertEqual(result["flag_counts"]["unmatched_member"], 0)


class IntervalIdentityTests(unittest.TestCase):
    """Finding 6: flag_id left out the interval, so a second interval was dropped."""

    def test_two_intervals_are_two_flags_and_both_exclude(self) -> None:
        a = flag("contention.request_overlap", "window", interval=[0, 60], observed={"cpu": 0.2})
        b = flag("contention.request_overlap", "window", interval=[2000, 2060], observed={"cpu": 0.2})
        self.assertNotEqual(a["flag_id"], b["flag_id"])
        self.assertEqual(validate_flag(a), [])
        self.assertEqual(validate_flag(b), [])
        self.assertEqual(excluded(compute([a, b], roster(), SPANS, CATALOG)), ["r0", "q2_2"])
        with tempfile.TemporaryDirectory() as directory:
            sink = FlagSink(Path(directory) / "x.jsonl")
            self.assertEqual((sink.append(a), sink.append(b)), (True, True))

    def test_changing_the_interval_after_emission_is_detected(self) -> None:
        a = flag("contention.request_overlap", "window", interval=[0, 60])
        a["interval"]["monotonic_ns"] = [0, 70]
        self.assertIn("flag_id does not match", "; ".join(validate_flag(a)))


class MalformedRecordTests(unittest.TestCase):
    """Finding 7: read_flags dropped an exclusion-bearing record without a trace."""

    def test_malformed_physics_flag_blocks_release(self) -> None:
        good = flag("battery.member_span", "member", run_id="q0_0")
        bad = dict(good, evidence=[{"path": "/abs/raw.plist", "sha256": "0" * 64}])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "y.jsonl"
            path.write_text(json.dumps(bad) + "\n")
            flags, problems = read_flags(path)
        self.assertEqual(len(problems), 1)
        self.assertEqual([f["code"] for f in flags], ["records.malformed_flag"])
        self.assertEqual(flags[0]["observed"]["salvaged_code"], "battery.member_span")
        self.assertEqual(flags[0]["scope"]["plan_id"], "P")
        self.assertEqual(validate_flag(flags[0]), [])
        result = compute(flags, roster(), SPANS, CATALOG)
        self.assertEqual(result["unclassified"], ["records.malformed_flag"])
        self.assertTrue(result["release_blocked"])

    def test_unparseable_line_blocks_release_for_any_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "z.jsonl"
            path.write_bytes(b'{"code": "battery.member_span", "scope": ')
            flags, _ = read_flags(path)
        self.assertEqual(flags[0]["scope"]["plan_id"], None)
        self.assertTrue(compute(flags, roster(), SPANS, CATALOG)["release_blocked"])

    def test_catalog_may_not_classify_the_never_classified_codes(self) -> None:
        for code in NEVER_CLASSIFIED_CODES:
            document = draft_catalog_document()
            document["codes"][code] = {"family": "RECORDS", "klass": "REPRESENTATION", "effect": "DISCLOSE"}
            with self.subTest(code=code), self.assertRaises(CatalogError):
                catalog_from_bytes(json.dumps(document).encode())
            self.assertNotIn(code, CATALOG.codes)


class CellRuleTests(unittest.TestCase):
    """Finding 8: a roster could lower the sealed minimum or lose a stratum."""

    def test_roster_minimum_cannot_lower_the_catalog_rule(self) -> None:
        ro = roster()
        ro["cells"] = [{"cell_id": "c", "minimum": {"repeat": 1, "quad": 1}}]
        flags = [flag("battery.member_span", "member", run_id=f"r{i}") for i in range(9)]
        result = compute(flags, ro, SPANS, CATALOG)
        self.assertEqual(result["cells"][0]["n_repeats"], 1)
        self.assertEqual(result["cells"][0]["minimum"], {"quad": 8, "repeat": 8})
        self.assertFalse(result["claim_usable"])
        self.assertEqual(result["reasons"], ["cell.below_minimum"])

    def test_roster_that_lost_the_quad_stratum_is_not_resolvable(self) -> None:
        ro = roster()
        ro["members"] = [m for m in ro["members"] if m["run_id"].startswith("r")]
        result = compute([], ro, SPANS, CATALOG)
        self.assertFalse(result["cells"][0]["resolvable"])
        self.assertEqual(result["cells"][0]["planned"]["quad"], 0)
        self.assertFalse(result["claim_usable"])

    def test_declared_floor_strata_catch_a_lost_repeat_stratum(self) -> None:
        ro = roster()
        ro["members"] = [m for m in ro["members"] if not m["run_id"].startswith("r")]
        self.assertTrue(compute([], ro, SPANS, CATALOG)["claim_usable"])  # looks like a contrast cell
        ro["cells"] = [{"cell_id": "c", "strata": ["repeat", "quad"]}]
        result = compute([], ro, SPANS, CATALOG)
        self.assertFalse(result["claim_usable"])
        self.assertEqual(result["cells"][0]["n_kept"], {"quad": 10, "repeat": 0})


class AttemptChoiceTests(unittest.TestCase):
    """Finding 9: an attempt with an unclassified code was chosen; duplicate bytes counted."""

    def test_release_blocked_attempt_is_not_chosen(self) -> None:
        r1 = compute([flag("brand.new_code", "window")], roster(), SPANS, CATALOG)
        self.assertTrue(r1["claim_usable"])
        self.assertTrue(r1["release_blocked"])
        self.assertIsNone(first_claim_usable([{**r1, "attempt": 1}]))
        clean = compute([], roster(), SPANS, CATALOG)
        # A later clean attempt is not substituted while attempt 1 is undecided.
        self.assertIsNone(first_claim_usable([{**r1, "attempt": 1}, {**clean, "attempt": 2}]))
        # An unusable attempt stays unusable whatever its codes become.
        unusable = compute([flag("brand.new_code", "window"), flag("pack.identity_mismatch", "window")],
                           roster(), SPANS, CATALOG)
        self.assertEqual(first_claim_usable([{**unusable, "attempt": 1}, {**clean, "attempt": 2}]), 2)
        self.assertIsNone(first_claim_usable([{"attempt": 1, "claim_usable": True}]))

    def test_member_with_two_admissible_bundles_is_excluded(self) -> None:
        ro = roster()
        ro["bundles"] = [{"bundle_id": f"b{m['run_id']}", "run_id": m["run_id"], "attempt": 1,
                          "created_monotonic_ns": 5} for m in ro["members"]]
        ro["bundles"].append({"bundle_id": "dup", "run_id": "r0", "attempt": 1, "created_monotonic_ns": 9})
        result = compute([], ro, SPANS, CATALOG)
        self.assertEqual(result["duplicate_bundles"], ["r0"])
        self.assertEqual(result["members_excluded"][0]["run_id"], "r0")
        self.assertEqual(result["members_excluded"][0]["codes"], ["member.bytes_ambiguous"])
        self.assertEqual(result["cells"][0]["n_repeats"], 9)


class MutationSurvivorTests(unittest.TestCase):
    """Finding 10: the contention limit and the overlap boundary were not pinned."""

    def test_contention_limit_boundary(self) -> None:
        span = {"m1": {"monotonic_ns": [10 * S, 60 * S], "request_monotonic_ns": [15 * S, 55 * S]}}

        def run(cpu: float):
            intervals = [{"monotonic_ns": [t * S, (t + 10) * S], "processes": []} for t in range(0, 100, 10)]
            intervals[3]["processes"] = [{"pid": 99, "comm": "fseventsd", "cpu_s_per_s": cpu}]
            return [f["code"] for f in contention_span_flags(intervals, span)]

        self.assertEqual(run(0.06), ["contention.request_overlap"])
        self.assertEqual(run(0.04), [])

    def test_interval_touching_a_span_endpoint_overlaps(self) -> None:
        start, stop = SPANS["r3"]["monotonic_ns"]
        at_stop = flag("clock.step_overlap", "window", interval=[stop, stop + 5])
        self.assertEqual(excluded(compute([at_stop], roster(), SPANS, CATALOG)), ["r3"])
        at_start = flag("clock.step_overlap", "window", interval=[start - 5, start])
        self.assertEqual(excluded(compute([at_start], roster(), SPANS, CATALOG)), ["r3"])


if __name__ == "__main__":
    unittest.main()
