"""Regressions for fix lane fx-flags (2026-10-06).

(1) The three-pack sealed inventory is in ``test_flags_collect.py``
    (``ExecutedCodeTests.test_three_pack_sealed_inventory_*``).
(2) One physics-in-span join: ``joulewise.flags.exclusions`` no longer carries
    its own copy; the harvest's joins, run on lane L1's journal fixtures, feed
    ``exclusions.compute`` and exclude exactly the members L1's own join flags.
(3) One battery naming: the codes lane L1's monitor join emits are the ones
    L4's draft classifies, with the block-5 catalog's family, class and effect.

Each test here fails on the lane's base (cf39f313) and passes after the fix,
except the fixture agreement test, which pins the remaining join to L1.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any

from joulewise.flags import exclusions
from joulewise.flags.catalog import (
    DRAFT_CODES,
    SEALED_CATALOG_RELATIVE_PATH,
    UNCLASSIFIED,
    draft_catalog,
    load_catalog,
)
from joulewise.flags.schema import make_flag, make_interval, make_scope, make_source

REPO = Path(__file__).resolve().parents[2]
L1_JOURNALS = REPO / "tests" / "fixtures" / "b5_harvest" / "l1_monitor"
EMITTED = {"wall_s": 1.0, "monotonic_ns": 1, "boot_session_uuid": None}
PLAN = "plan-fx"


def _importable(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


L1_AVAILABLE = _importable("joulewise.hazards.battery")
L5_AVAILABLE = _importable("joulewise.b5.harvest")

# The block-5 flag catalog, revision 3 (branch design/2026-10-05-v5-claim-block-draft,
# configs/campaigns/v5_claim_25g83/flag_catalog.json at 71c91d74): its
# battery.member_span and battery.accumulator_* entries, transcribed.
CATALOG_R3_BATTERY = {
    "battery.member_span": ("PHYSICS_IN_SPAN", "PHYSICS", "EXCLUDE_MEMBER"),
    "battery.unmeasured": ("PHYSICS_IN_SPAN", "PHYSICS", "EXCLUDE_MEMBER"),
    "battery.accumulator_excursion": ("PHYSICS_IN_SPAN", "PHYSICS", "EXCLUDE_MEMBER"),
    "battery.accumulator_diagnostic": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
    "battery.accumulator_activity": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
    "battery.accumulator_unavailable": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
    # lane 2026-10-06-smc-battery-meter: the registry fallback when SMC B0AC is unread
    "battery.smc_unavailable": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
}


def _entry(codes: Any, code: str) -> tuple[str, str, str] | None:
    entry = codes.get(code)
    return None if entry is None else (entry["family"], entry["klass"], entry["effect"])


class BatteryNamingTests(unittest.TestCase):
    """(3) L1's battery codes and L4's agree, and both match the catalog."""

    def test_l4_battery_vocabulary_matches_the_catalog(self) -> None:
        l4 = {code: _entry(DRAFT_CODES, code) for code in DRAFT_CODES
              if code == "battery.member_span" or code == "battery.unmeasured"
              or code.startswith("battery.accumulator_") or code == "battery.smc_unavailable"}
        self.assertEqual(l4, CATALOG_R3_BATTERY)

    def test_sealed_catalog_battery_entries_match_l4_when_present(self) -> None:
        sealed = REPO / SEALED_CATALOG_RELATIVE_PATH
        if not sealed.exists():
            self.skipTest("the sealed catalog is not in this tree yet (lane L6)")
        catalog = load_catalog(sealed)
        for code, expected in CATALOG_R3_BATTERY.items():
            self.assertEqual(_entry(catalog.codes, code), expected, code)

    @unittest.skipUnless(L1_AVAILABLE, "lane L1's joulewise.hazards is not in this tree")
    def test_every_code_l1s_battery_join_emits_is_classified_by_l4(self) -> None:
        from joulewise.hazards import battery
        from tests.hazards.test_battery import SpanRig

        rig = SpanRig()
        rig.setUp()
        smc = rig.smc_lines(600)  # the monitor's 1 s SMC B0AC reads, 0 mA
        scenarios = {
            # the 09-30 0555Z publication: -447 mA on AC, judged on the registry (no SMC reads)
            "publication": rig.series(10, special={3: {"instant": -447}}),
            # the 10-06 probe burst: B0AC -865 mA between clean publications
            "smc_burst": rig.series(10) + rig.smc_lines(600, current={150: -865}),
            # 20 discharge ticks averaging -3 W between two 0 mA publications
            "accumulator_excursion": rig.series(10, special={3: {"ticks": 20, "energy": -60_000}}) + smc,
            # the archived calibration-capture assist, about -140 mW
            "assist": rig.series(10, special={3: {"ticks": 21, "energy": -2927}}) + smc,
            # a gauge counter reset
            "counter_reset": rig.series(10, special={3: {"ticks": -30_000, "energy": 0}}) + smc,
        }
        emitted: dict[str, set[str]] = {}
        for name, readings in scenarios.items():
            emitted[name] = {f["code"] for f in battery.span_findings(readings, rig.span(130, 170))}
        self.assertEqual(emitted["publication"], {"battery.smc_unavailable", "battery.member_span"})
        self.assertEqual(emitted["smc_burst"], {"battery.member_span"})
        self.assertEqual(emitted["assist"], {"battery.accumulator_activity"})
        self.assertEqual(emitted["counter_reset"], {"battery.accumulator_unavailable"})
        catalog = draft_catalog()
        for code in set().union(*emitted.values()):
            self.assertNotEqual(catalog.effect(code), UNCLASSIFIED, code)
            self.assertEqual(_entry(catalog.codes, code), CATALOG_R3_BATTERY[code], code)


class OneSpanJoinTests(unittest.TestCase):
    """(2) The harvest's joins are the only physics-in-span implementation."""

    def test_exclusions_carries_no_second_span_join(self) -> None:
        removed = ("battery_span_flags", "thermal_span_flags", "contention_span_flags",
                   "clock_span_flags", "clock_systematic_flags")
        self.assertEqual([name for name in removed if hasattr(exclusions, name)], [])

    def test_number_rows_name_the_harvest_joins(self) -> None:
        rows = json.loads((REPO / "configs" / "flags" / "number_rows.json").read_text(encoding="utf-8"))["rows"]
        sites = [holder.get("evaluation_site") or "" for row in rows
                 for holder in (row, row.get("equivalent") or {})]
        self.assertEqual([site for site in sites if site.startswith("joulewise/flags/exclusions.py:")
                          and site.partition(":")[2] not in ("compute", "first_claim_usable")], [])

    @unittest.skipUnless(L5_AVAILABLE, "lane L5's joulewise.b5.harvest is not in this tree")
    def test_harvest_joins_on_l1_fixtures_feed_compute_like_l1s_own_join(self) -> None:
        from joulewise.b5 import harvest as h
        # The harvest has no default thresholds: it reads registration 6.9's
        # flat block (fx-harvest).  The harvest tests keep this literal equal
        # to the design branch's registered block (RegisteredThresholdTests).
        from tests.test_harvest_b5_window import REGISTERED_HARVEST_THRESHOLDS

        expected = json.loads((L1_JOURNALS / "expected.json").read_bytes())["cases"]
        journals = {module: h.read_monitor_journal(L1_JOURNALS / f"{module}.jsonl", module)[0]
                    for module in h.MONITOR_MODULES}
        thresholds = dict(REGISTERED_HARVEST_THRESHOLDS)
        steps, _changes = h.clock_steps(journals["clock"], thresholds)
        catalog = draft_catalog()
        flags, spans, members = [], {}, []
        for name, case in sorted(expected.items()):
            span = case["span"]["monotonic_ns"]
            request = (case["request"] or case["span"])["monotonic_ns"]
            spans[name] = {"monotonic_ns": span}
            members.append({"run_id": name, "units": [{"cell_id": "c", "stratum": "repeat", "unit_id": name}]})
            found = []
            for join, module, window in ((h.battery_member_flags, "battery", span),
                                         (h.thermal_member_flags, "thermal", span),
                                         (h.contention_member_flags, "contention", request),
                                         (h.clock_member_flags, "clock", span)):
                found.extend(join(window, journals[module], thresholds))
            found.extend(("clock.step_overlap", {"step": step["interval_monotonic_ns"]},
                          {"monotonic_ns": step["interval_monotonic_ns"]})
                         for step in steps if h._overlaps(step["interval_monotonic_ns"], span))
            for code, observed, interval in found:
                entry = catalog.entry(code)
                flags.append(make_flag(
                    code=code, family=entry["family"], klass=entry["klass"],
                    scope=make_scope("member", plan_id=PLAN, attempt=1, run_id=name),
                    source=make_source("harvest", "joulewise.b5.harvest"), observed=observed,
                    interval=make_interval(monotonic_ns=interval.get("monotonic_ns")), emitted=EMITTED))
        roster = {"plan_id": PLAN, "attempt": 1, "members": members,
                  "cells": [{"cell_id": "c", "strata": ["repeat"]}]}
        result = exclusions.compute(flags, roster, spans, catalog)
        self.assertEqual(result["unclassified"], [])
        got = {item["run_id"]: item["codes"] for item in result["members_excluded"]}
        # The fixtures' only battery excursion is the -447 mA discharge (publication
        # 3), which L1's recorded join excluded; under the battery-assist ruling
        # (2026-10-06) the harvest discloses discharge (battery.assist), so it
        # excludes no member.
        want = {name: sorted(set(case["l1_codes"]) - {"battery.member_span"}) for name, case in expected.items()}
        want = {name: codes for name, codes in want.items() if codes}
        self.assertEqual(got, want)


if __name__ == "__main__":
    unittest.main()
