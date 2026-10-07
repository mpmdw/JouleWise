"""The flag catalog loader and the draft code table."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from joulewise.flags.catalog import (
    DERIVED_CODES,
    DISCLOSE,
    DRAFT_CODES,
    EXCLUDE_MEMBER,
    EXCLUDE_WINDOW,
    NEVER_CLASSIFIED_CODES,
    SEALED_CATALOG_RELATIVE_PATH,
    UNCLASSIFIED,
    CatalogError,
    draft_catalog,
    draft_catalog_document,
    load_catalog,
    missing_codes,
    validate_catalog,
)

REPO = Path(__file__).resolve().parents[2]


class CatalogTests(unittest.TestCase):
    def test_draft_table_matches_plan_section_3_5(self) -> None:
        window = {code for code, entry in DRAFT_CODES.items() if entry["effect"] == EXCLUDE_WINDOW}
        self.assertTrue({
            "pack.identity_mismatch", "code.executed_differs_from_sealed", "model.identity_mismatch",
            "neg8.bound_not_derived", "neg8.screen_failed", "instrument.precal_screen_failed",
            "clock.systematic", "cell.below_minimum",
        } <= window)
        member = {code for code, entry in DRAFT_CODES.items() if entry["effect"] == EXCLUDE_MEMBER}
        self.assertTrue({
            "battery.member_span", "battery.unmeasured", "thermal.os_level_nonzero",
            "contention.request_overlap", "contention.unmeasured", "clock.step_overlap",
            "member.admission_aborted", "member.anchor_not_bounded", "member.bytes_missing",
        } <= member)
        self.assertEqual(DRAFT_CODES["member.anchor_energy_envelope_exceeded"]["blinding"], "RESTRICTED")
        self.assertEqual(DRAFT_CODES["network_time.off_output"]["effect"], DISCLOSE)
        self.assertEqual(missing_codes(draft_catalog(), DERIVED_CODES), [])

    def test_loaded_catalog_sha_is_over_exact_file_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "flag_catalog.json"
            raw = json.dumps(draft_catalog_document(), indent=2).encode() + b"\n"
            path.write_bytes(raw)
            catalog = load_catalog(path)
        self.assertEqual(catalog.sha256, hashlib.sha256(raw).hexdigest())
        self.assertEqual(catalog.effect("battery.member_span"), EXCLUDE_MEMBER)
        self.assertEqual(catalog.cell_unit_minimum, 8)

    def test_unknown_code_is_unclassified(self) -> None:
        catalog = draft_catalog()
        self.assertEqual(catalog.effect("brand.new_code"), UNCLASSIFIED)
        self.assertIsNone(catalog.entry("brand.new_code")["family"])

    def test_malformed_catalogs_are_refused(self) -> None:
        good = draft_catalog_document()
        cases = []
        bad = json.loads(json.dumps(good))
        bad["codes"]["battery.member_span"]["effect"] = "STOP_COLLECTION"
        cases.append(bad)
        bad = json.loads(json.dumps(good))
        bad["schema_version"] = "v0"
        cases.append(bad)
        bad = json.loads(json.dumps(good))
        bad["codes"]["Bad Code"] = {"family": "RECORDS", "klass": "REPRESENTATION", "effect": DISCLOSE}
        cases.append(bad)
        bad = json.loads(json.dumps(good))
        bad["rules"]["cell_unit_minimum"] = 0
        cases.append(bad)
        for case in cases:
            with self.subTest(case=case.get("schema_version")):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "catalog.json"
                    path.write_text(json.dumps(case))
                    with self.assertRaises(CatalogError):
                        load_catalog(path)
        self.assertTrue(validate_catalog([]))
        with self.assertRaises(CatalogError):
            load_catalog(Path("/nonexistent/catalog.json"))

    def test_sealed_catalog_classifies_every_code_this_lane_emits(self) -> None:
        sealed = REPO / SEALED_CATALOG_RELATIVE_PATH
        if not sealed.exists():
            self.skipTest("sealed catalog not in this tree yet (lane L6)")
        catalog = load_catalog(sealed)
        self.assertEqual(missing_codes(catalog, EMITTED_BY_THIS_LANE), [])
        self.assertEqual(missing_codes(catalog, EMITTED_BY_THE_SPAN_JOINS), [])
        self.assertEqual(catalog.effect("cell.below_minimum"), EXCLUDE_WINDOW)

    def test_draft_classifies_every_code_this_lane_emits(self) -> None:
        self.assertEqual(missing_codes(draft_catalog(), EMITTED_BY_THIS_LANE), [])
        self.assertEqual(missing_codes(draft_catalog(), EMITTED_BY_THE_SPAN_JOINS), [])
        # These two stay unclassified on purpose: they always block release.
        self.assertEqual(missing_codes(draft_catalog(), NEVER_CLASSIFIED_CODES), sorted(NEVER_CLASSIFIED_CODES))


# Codes that joulewise.flags.collect and joulewise.flags.exclusions.compute can emit.
EMITTED_BY_THIS_LANE = (
    "pack.identity_mismatch", "code.executed_differs_from_sealed", "model.identity_mismatch",
    "model.identity_unpinned", "calibration.ledger_not_ready", "pack.identity_unmeasured",
    "code.identity_unmeasured", "model.identity_unmeasured", "calibration.ledger_readiness_unmeasured",
    "records.checkout_untracked", *DERIVED_CODES,
)

# Physics-in-span codes the harvest's joins (joulewise.b5.harvest) and lane
# L1's monitor join emit; their flags reach exclusions.compute, so the draft
# must classify every one. (L4's own copy of these joins was removed by fix
# lane fx-flags, 2026-10-06; the harvest's are the only implementation.)
EMITTED_BY_THE_SPAN_JOINS = (
    "battery.member_span", "battery.unmeasured", "battery.accumulator_excursion",
    "battery.accumulator_diagnostic", "battery.accumulator_activity", "battery.accumulator_unavailable",
    "battery.smc_unavailable", "battery.assist", "thermal.os_level_nonzero", "thermal.unmeasured", "contention.request_overlap", "contention.unmeasured",
    "contention.kernel_task_share", "clock.step_overlap", "clock.step_overlap_calibration", "clock.unmeasured",
    "clock.systematic",
)


if __name__ == "__main__":
    unittest.main()
