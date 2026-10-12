"""S1 contract checks on synthetic fixtures only; module caches all windows."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import unittest
from unittest import mock

from joulewise.b5_analysis import kept_units as ku
from joulewise.b5_analysis.windows import AnalysisRefusal, WindowIndex, select_analysed_attempts
from tests.b5_analysis import fixtures_s1 as fx


class KeptUnitsTests(unittest.TestCase):
    def case(self, name="STD", **kwargs):
        case = fx.Case(fx.cached(name, **kwargs))
        self.addCleanup(case.close)
        return case

    def load(self, case, handle=None):
        return ku.load_kept_units(handle or case.handle(), sealed_catalog_sha256=fx.CATALOG.sha256,
                                  planned_units=case.planned)

    def refuses(self, case, code, handle=None):
        with self.assertRaisesRegex(AnalysisRefusal, "^" + code + "$"):
            self.load(case, handle)

    # Plan's named fixtures first.
    def test_removed_repeat_gives_n_r_9_n_b_10(self):
        units = self.load(self.case("REPEAT6_REMOVED"))
        cell = units.cell("df-b5t-family")
        self.assertEqual((cell.n_r, cell.n_b), (9, 10))
        self.assertEqual(units.removed_run_ids(), {"s0-mock-r06"})

    def test_removed_quad_member_removes_all_four_siblings(self):
        case = self.case("QUAD_MEMBER_REMOVED")
        units = self.load(case)
        self.assertEqual(len(case.exclusions["members_excluded"]), 1)
        self.assertEqual(units.cell("df-b5t-family").n_b, 9)
        self.assertEqual(units.removed_run_ids(), set(case.planned["df-b5t-family"]["quad"]["s0-mock-b01"]))
        dropped = units.cell("df-b5t-family").dropped[0]
        self.assertEqual(dropped.run_ids, case.planned["df-b5t-family"]["quad"]["s0-mock-b01"])
        self.assertEqual(dropped.positions, (10, 11, 12, 13))
        self.assertEqual(dropped.stage_ids, ("02_abba",) * 4)
        self.assertEqual(dropped.families, ("PHYSICS_IN_SPAN",))

    def test_six_removed_quads_not_claim_usable(self):
        case = self.case("SIX_QUADS_REMOVED")
        self.assertFalse(case.exclusions["claim_usable"])
        self.assertEqual(case.exclusions["reasons"], ["cell.below_minimum"])
        self.assertEqual(case.exclusions["cells"][0]["n_kept"]["quad"], 4)
        self.assertFalse(case.record().claim_usable)
        with self.assertRaisesRegex(AnalysisRefusal, "^attempt_not_claim_usable$"):
            case.handle()

    def test_five_removed_quads_load_at_minimum(self):
        units = self.load(self.case("FIVE_QUADS_REMOVED"))
        self.assertEqual(units.cell("df-b5t-family").n_b, 5)
        self.assertEqual(dict(units.cell("df-b5t-family").minimum), {"quad": 5, "repeat": 5})

    def test_beta_archive_with_alpha_sealed_spec_refuses(self):
        # S0 has a shared mock plan. A structural variant over its real pin4
        # harvest uses the sealed BETA ids, and first loads with BETA's spec.
        snapshot, _ = fx.registered_snapshot("beta", base=fx.cached(pack="beta"))
        case = fx.Case(snapshot); self.addCleanup(case.close)
        self.assertEqual(len(self.load(case).cells), 3)
        alpha, _ = fx.registered_snapshot("alpha")
        case.planned = alpha.planned
        self.refuses(case, "exclusions_plan_mismatch")

    def move_first_dropped_to_kept(self, case):
        cell = case.exclusions["cells"][0]
        dropped = cell["dropped_units"].pop(0)
        cell["kept_units"][dropped["stratum"]].append(dropped["unit_id"])
        # Leave only n_kept stale, so its guard has an independent mutation bite.
        count_key = {"repeat": "n_repeats", "quad": "n_quads"}[dropped["stratum"]]
        cell[count_key] += 1

    def test_moved_unit_with_stale_outputs_digest_refuses(self):
        case = self.case("QUAD_MEMBER_REMOVED")
        handle = case.handle()
        self.move_first_dropped_to_kept(case)
        case.write(update_digest=False)
        self.refuses(case, "exclusions_record_unauthenticated", handle)

    def test_moved_unit_with_updated_digest_stale_n_kept_refuses(self):
        case = self.case("QUAD_MEMBER_REMOVED")
        self.move_first_dropped_to_kept(case)
        case.write()
        self.refuses(case, "exclusions_cell_inconsistent")

    def test_handbuilt_usable_target_with_four_quads_refuses(self):
        case = self.case("SIX_QUADS_REMOVED")
        case.exclusions.update(claim_usable=True, reasons=[])
        case.write()
        self.refuses(case, "kept_units_below_minimum")

    def test_p42_non_target_with_four_quads_loads(self):
        case = fx.Case(fx.p42_snapshot())
        self.addCleanup(case.close)
        units = self.load(case)
        self.assertEqual(units.cell("df-ph-prefill-p42-mock").n_b, 4)
        self.assertFalse(units.cell("df-ph-prefill-p42-mock").target)

    def test_p42_precheck_is_the_only_member_gate_exception(self):
        case = fx.Case(fx.p42_snapshot())
        self.addCleanup(case.close)
        units = self.load(case)
        cid, run = "df-ph-prefill-p42-mock", "s0-mock-r01"
        units.stop_if_member_code_on_kept_unit(cid, run, "insufficient_in_window_samples", p42_precheck=True)
        with self.assertRaisesRegex(AnalysisRefusal, "^member_code_on_kept_unit$"):
            units.stop_if_member_code_on_kept_unit(cid, run, "paired_block_incomplete")
        target = self.load(self.case())
        with self.assertRaisesRegex(AnalysisRefusal, "^member_code_on_kept_unit$"):
            target.stop_if_member_code_on_kept_unit("df-b5t-family", run, "insufficient_in_window_samples", p42_precheck=True)

    def selection(self, cases):
        records = [case.record() for case in cases]
        return select_analysed_attempts(WindowIndex(tuple(r.entry for r in records)), records)

    def test_release_blocked_refuses_load_and_selection_does_not_skip(self):
        early = self.case()
        early.entry = replace(early.entry, pack="gamma")
        early.exclusions["release_blocked"] = True
        early.write()
        self.refuses(early, "attempt_release_blocked")
        later = fx.Case(fx.gamma_snapshot(attempt=2))
        self.addCleanup(later.close)
        alpha, beta = self.case(), self.case()
        beta.entry = replace(beta.entry, pack="beta")
        beta.write()
        with self.assertRaisesRegex(AnalysisRefusal, "^analysed_attempt_undecided$"):
            self.selection([alpha, beta, early, later])

    def test_draft_catalog_minimum_eight_digest_refuses(self):
        case = self.case()
        original = case.handle()
        from joulewise.flags.catalog import draft_catalog_document
        draft = draft_catalog_document()
        self.assertEqual(draft["rules"]["cell_unit_minimum"], 8)
        case.exclusions["catalog_sha256"] = hashlib.sha256(json.dumps(draft, sort_keys=True).encode()).hexdigest()
        case.write()
        with self.assertRaisesRegex(AnalysisRefusal, "^exclusions_catalog_mismatch$"):
            case.handle()
        self.refuses(case, "exclusions_catalog_mismatch", ku.ArchiveHandle(original.window, case.harvest, {}))

    def test_s1_catalog_check_independent_of_attempt_reader(self):
        case = self.case()
        handle = case.handle()
        with self.assertRaisesRegex(AnalysisRefusal, "^exclusions_catalog_mismatch$"):
            ku.load_kept_units(handle, sealed_catalog_sha256="0" * 64, planned_units=case.planned)

    def test_cell_minimum_four_refuses(self):
        case = self.case()
        case.exclusions["cells"][0]["minimum"]["quad"] = 4
        case.write()
        self.refuses(case, "exclusions_cell_inconsistent")

    def test_three_member_quad_in_roster_refuses(self):
        case = self.case()
        case.roster["members"][13]["units"] = []
        case.write()
        self.refuses(case, "exclusions_roster_mismatch")

    def test_gamma_midpoint_lost_first_attempt_selects_second(self):
        early, later = fx.Case(fx.gamma_snapshot(midpoint_lost=True)), fx.Case(fx.gamma_snapshot(attempt=2))
        self.addCleanup(early.close); self.addCleanup(later.close)
        self.assertEqual(early.exclusions["reasons"], ["neg8.midpoint_lost_primary"])
        alpha, beta = self.case(), self.case()
        beta.entry = replace(beta.entry, pack="beta"); beta.write()
        self.assertEqual(self.selection([alpha, beta, early, later])["gamma"].attempt, 2)
        self.assertEqual(self.load(later).for_contrast("ctr-d117-decode-mock").n_b, 10)

    def test_no_summaries_or_sources_or_withheld_are_opened(self):
        case = self.case("QUAD_MEMBER_REMOVED")
        handle = case.handle()
        expected = {case.root / "derived/exclusions.json", case.root / "derived/roster.json", ku.CATALOG_PATH}
        real_read = Path.read_bytes
        def read(path):
            if path not in expected:
                raise AssertionError("S1 opened a bundle or another archive input")
            return real_read(path)
        with mock.patch.object(Path, "read_bytes", read), \
                mock.patch.object(handle, "source_bytes", side_effect=AssertionError("source read")), \
                mock.patch.object(handle, "withheld_bytes", side_effect=AssertionError("withheld read")):
            units = self.load(case, handle)
            record = units.to_record()
        self.assertEqual(record["cells"]["df-b5t-family"]["n_b"], 9)
        self.assertTrue(record["cells"]["df-b5t-family"]["dropped"])

    def test_strict_json_duplicate_and_nonfinite_refuse(self):
        for raw in (b'{"claim_usable":true,"claim_usable":false}', b'{"x":NaN}', b'{"x":Infinity}',
                    b'{"x":-Infinity}', b'{"x":1e999}', b'[]', b'\xff', b'{'):
            with self.subTest(raw=raw):
                case = self.case()
                handle = case.handle()
                case.write(exclusions_raw=raw)
                refreshed = ku.ArchiveHandle(handle.window, case.harvest, {})
                self.refuses(case, "exclusions_schema_invalid", refreshed)

    def test_schema_usable_reasons_unclassified_and_release_types(self):
        for field, value, code in (("schema_version", "wrong", "exclusions_schema_invalid"),
                                   ("claim_usable", 1, "exclusions_schema_invalid"),
                                   ("reasons", ["window.null"], "exclusions_schema_invalid"),
                                   ("unclassified", ["unknown"], "exclusions_schema_invalid"),
                                   ("release_blocked", 0, "attempt_release_blocked"),
                                   ("release_blocked", None, "attempt_release_blocked")):
            with self.subTest(field=field, value=value):
                case = self.case(); handle = case.handle()
                case.exclusions[field] = value; case.write()
                self.refuses(case, code, ku.ArchiveHandle(handle.window, case.harvest, {}))

    def test_unknown_top_level_fields_are_allowed(self):
        case = self.case()
        case.exclusions["new_pin_field"] = {"restricted_number": 12.5}
        case.write()
        self.assertEqual(self.load(case).cell("df-b5t-family").n_r, 10)

    def test_attempt_or_plan_disagreement_refuses(self):
        for which, field, value in (("exclusions", "attempt", 2), ("roster", "attempt", True),
                                     ("exclusions", "plan_id", "other"), ("roster", "plan_id", "other")):
            with self.subTest(which=which, field=field):
                case = self.case(); getattr(case, which)[field] = value; case.write()
                self.refuses(case, "exclusions_attempt_mismatch")

    def test_count_disjointness_duplicates_and_strata_refuse(self):
        edits = (lambda c: c["planned"].update(quad=11), lambda c: c.update(n_quads=11),
                 lambda c: c["kept_units"]["quad"].append(c["kept_units"]["quad"][0]),
                 lambda c: c["kept_units"]["quad"].append(c["dropped_units"][0]["unit_id"]),
                 lambda c: c["dropped_units"].append(c["dropped_units"][0].copy()),
                 lambda c: c["minimum"].update(repeat=True), lambda c: c["n_kept"].update(quad=10))
        for i, edit in enumerate(edits):
            with self.subTest(i=i):
                case = self.case("QUAD_MEMBER_REMOVED"); cell = case.exclusions["cells"][0]
                edit(cell)
                case.write(); self.refuses(case, "exclusions_cell_inconsistent")

    def test_roster_digest_guard(self):
        case = self.case(); handle = case.handle()
        (case.root / "derived/roster.json").write_bytes(b'{}')
        self.refuses(case, "roster_record_unauthenticated", handle)

    def test_roster_strata_include_strata_carried_by_units(self):
        # exclusions.compute takes the union of declared and member strata.
        case = self.case()
        case.roster["cells"][0]["strata"] = ["quad"]
        case.exclusions = fx.recompute(case.snapshot, case.roster)
        case.write()
        self.assertEqual((self.load(case).cell("df-b5t-family").n_r,
                          self.load(case).cell("df-b5t-family").n_b), (10, 10))

    def test_roster_membership_position_target_and_duplicate_guard(self):
        for variant in ("drop_ids", "drop_positions", "target", "duplicate", "unit_missing", "bad_code"):
            with self.subTest(variant=variant):
                case = self.case("QUAD_MEMBER_REMOVED")
                cell = case.exclusions["cells"][0]
                if variant == "drop_ids": cell["dropped_units"][0]["run_ids"][0] = "other"
                if variant == "drop_positions": cell["dropped_units"][0]["positions"][0] = 100
                if variant == "target": case.roster["cells"][0]["target"] = False
                if variant == "duplicate": case.roster["members"].append(case.roster["members"][0])
                if variant == "unit_missing": cell["kept_units"]["quad"][0] = "absent"
                if variant == "bad_code": cell["dropped_units"][0]["codes"] = ["unknown.code"]
                case.write(); self.refuses(case, "exclusions_roster_mismatch")

    def test_planned_universe_includes_dropped_members_and_order(self):
        for variant in ("missing_cell", "missing_dropped", "wrong_member", "wrong_order", "extra_cell"):
            with self.subTest(variant=variant):
                case = self.case("QUAD_MEMBER_REMOVED"); units = case.planned["df-b5t-family"]["quad"]
                if variant == "missing_cell": case.planned.clear()
                if variant == "missing_dropped": del units["s0-mock-b01"]
                if variant == "wrong_member": units["s0-mock-b01"] = ("other",) * 4
                if variant == "wrong_order": units["s0-mock-b01"] = tuple(reversed(units["s0-mock-b01"]))
                if variant == "extra_cell": case.planned["extra"] = {}
                self.refuses(case, "exclusions_plan_mismatch")

    def test_mappings_unknown_cells_members_and_member_tripwire(self):
        units = self.load(self.case("QUAD_MEMBER_REMOVED")); cid = "df-b5t-family"
        self.assertFalse(units.is_kept(cid, "s0-mock-b01-a2"))
        self.assertTrue(units.is_kept(cid, "s0-mock-r01"))
        self.assertEqual(len(units.kept_run_ids(cid, "quad")), 36)
        with self.assertRaisesRegex(AnalysisRefusal, "^exclusions_cell_unknown$"): units.cell("missing")
        with self.assertRaisesRegex(AnalysisRefusal, "^exclusions_member_unknown$"): units.is_kept(cid, "missing")
        with self.assertRaisesRegex(AnalysisRefusal, "^member_code_on_kept_unit$"):
            units.stop_if_member_code_on_kept_unit(cid, "s0-mock-r01", "paired_block_incomplete")
        units.stop_if_member_code_on_kept_unit(cid, "s0-mock-b01-a2", "paired_block_incomplete")
        spec = {"cells": [{"kind": "absolute", "condition_family_id": cid},
                          {"kind": "comparative", "condition_family_id": cid}]}
        self.assertEqual(units.for_floor_cell(spec["cells"][1]), (units.cell(cid), "quad"))
        reported = units.for_reported_cell(spec, 0)
        self.assertEqual(reported.removed_quad_ordinals, ((11, 12, 13, 14),))
        self.assertEqual(reported.kept_repeat_ordinals, tuple(range(1, 11)))
        with self.assertRaisesRegex(AnalysisRefusal, "^exclusions_plan_mismatch$"): units.for_contrast(cid)
        spec["cells"][1]["condition_family_id"] = "missing"
        with self.assertRaises(AnalysisRefusal): units.for_reported_cell(spec, 0)

    def test_j3_missing_kept_member_names_run_and_does_not_remove_unit(self):
        units = self.load(self.case()); cid = "df-b5t-family"
        all_ids = units.kept_run_ids(cid)
        before = units.to_record()
        with self.assertRaisesRegex(AnalysisRefusal, "^kept_member_outside_verdict_membership:s0-mock-r06$"):
            ku.require_kept_members_in_verdict(units, all_ids - {"s0-mock-r06"})
        self.assertEqual(units.to_record(), before)
        units.require_verdict_membership(all_ids)

    def test_j3_dropped_members_need_not_be_in_verdict(self):
        units = self.load(self.case("QUAD_MEMBER_REMOVED"))
        ku.require_kept_members_in_verdict(units, units.kept_run_ids("df-b5t-family"))

    def test_j3_checks_every_cell_and_quad_member(self):
        snapshot, _ = fx.registered_snapshot("gamma")
        case = fx.Case(snapshot); self.addCleanup(case.close)
        units = self.load(case)
        membership = frozenset(run for cid in units.cells for run in units.kept_run_ids(cid))
        last_cell = list(units.cells.values())[-1]
        missing = last_cell.kept["quad"][-1].run_ids[-1]
        with self.assertRaisesRegex(AnalysisRefusal, "^kept_member_outside_verdict_membership:" + missing + "$"):
            ku.require_kept_members_in_verdict(units, membership - {missing})

    def test_structure_record_has_only_allowed_fields_no_ids_restricted_codes_or_floats(self):
        case = self.case("QUAD_MEMBER_REMOVED")
        restricted = next(code for code, entry in fx.CATALOG.codes.items() if entry["blinding"] == "RESTRICTED")
        structure = next(code for code, entry in fx.CATALOG.codes.items() if entry["blinding"] == "STRUCTURE")
        case.exclusions["flag_counts"]["by_code"].update({restricted: 7, structure: 3})
        case.exclusions["unknown"] = {"float": 1.25, "restricted": restricted, "run_id": "s0-mock-r01"}
        case.write()
        units = self.load(case); record = units.to_structure_record()
        rendered = json.dumps(record)
        for member in case.roster["members"]: self.assertNotIn(member["run_id"], rendered)
        for code, entry in fx.CATALOG.codes.items():
            if entry["blinding"] == "RESTRICTED": self.assertNotIn(code, rendered)
        def inspect(value):
            self.assertNotIsInstance(value, float)
            if isinstance(value, dict):
                for item in value.values(): inspect(item)
            if isinstance(value, list):
                for item in value: inspect(item)
        inspect(record)
        self.assertEqual(record["flags_by_code"][structure], 3)
        self.assertEqual(record["flags_by_family"], case.exclusions["flag_counts"]["by_family"])
        self.assertEqual(record["cells"], {"df-b5t-family": {"n_r": 10, "n_b": 9}})
        self.assertEqual(record["verdict"], "COLLECTED"); self.assertIs(record["claim_usable"], True)
        self.assertEqual(set(record), {"pack", "plan_id", "attempt", "verdict", "claim_usable", "exclusions_sha256",
            "roster_sha256", "catalog_sha256", "harvest_record_sha256", "flags_by_family", "flags_by_code", "cells"})

    def test_records_are_deterministic_digest_bound_and_immutable(self):
        case = self.case("QUAD_MEMBER_REMOVED"); units = self.load(case)
        self.assertEqual(units.to_record(), self.load(case).to_record())
        self.assertEqual(units.exclusions_sha256, case.harvest["outputs"]["derived/exclusions.json"])
        self.assertEqual(units.roster_sha256, case.harvest["outputs"]["derived/roster.json"])
        self.assertEqual(units.catalog_sha256, fx.CATALOG.sha256)
        with self.assertRaises(TypeError): units.cells["new"] = None
        with self.assertRaises(TypeError): units.cell("df-b5t-family").minimum["quad"] = 4
        record = units.to_record(); record["cells"].clear()
        self.assertTrue(units.cells)

    def test_labelled_sensitivity_views_preserve_primary(self):
        units = self.load(self.case("QUAD_MEMBER_REMOVED")); cid = "df-b5t-family"
        restored = units.with_units_restored(cid, ["s0-mock-b01"], label="load-correlated")
        self.assertEqual(restored.cell(cid).n_b, 10)
        self.assertEqual(units.cell(cid).n_b, 9)
        subset = units.without_units(cid, ["s0-mock-b02"], label="leave-one-out")
        self.assertEqual(subset.cell(cid).n_b, 8)
        self.assertEqual(subset.sensitivity_label, "leave-one-out")
        self.assertEqual(len(subset.removed_run_ids()), 8)
        with self.assertRaises(AnalysisRefusal): units.without_units(cid, ["missing"], label="leave-one-out")

    def test_all_registered_cells_and_decode_p42_alias_removal(self):
        for pack in ("alpha", "beta", "gamma"):
            with self.subTest(pack=pack):
                snapshot, spec = fx.registered_snapshot(pack, remove_first_decode_quad=True)
                case = fx.Case(snapshot); self.addCleanup(case.close)
                units = self.load(case)
                self.assertEqual(len(units.cells), 2 if pack == "gamma" else 3)
                if pack == "gamma":
                    for contrast in spec["contrasts"]:
                        cell = units.for_contrast(contrast["contrast_id"])
                        self.assertEqual(cell.n_r, 0)
                        self.assertEqual(cell.n_b, 9 if "decode" in cell.cell_id.split("-") else 10)
                else:
                    for index in range(3):
                        mapped = units.for_reported_cell(spec, index)
                        cell = mapped.cell
                        if "p2048" in cell.cell_id.split("-"):
                            self.assertEqual((cell.n_r, cell.n_b), (10, 10))
                        else:
                            self.assertEqual((cell.n_r, cell.n_b), (10, 9))
                            self.assertEqual(mapped.removed_quad_ordinals, ((11, 12, 13, 14),))
                    decode = next(c.cell_id for c in units.cells.values() if "decode" in c.cell_id.split("-"))
                    p42 = next(c.cell_id for c in units.cells.values() if "p42" in c.cell_id.split("-"))
                    self.assertEqual(units.removed_run_ids(decode), units.removed_run_ids(p42))


if __name__ == "__main__":
    unittest.main()
