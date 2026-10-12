"""Context construction, survivor accounting and archive authentication."""
import ast
import copy
from dataclasses import FrozenInstanceError
import inspect
from pathlib import Path
import unittest
from unittest import mock

from joulewise import whole_window as ww
from joulewise.b5_analysis import context as ctx
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis import fixtures_s3b as fx

_WINDOWS = {}


def windows():
    if "BETA_STD" not in _WINDOWS:
        _WINDOWS["BETA_STD"] = fx.cached()
    return _WINDOWS


class ContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        windows()

    def case(self, **kwargs):
        case = fx.Case(**kwargs)
        self.addCleanup(case.close)
        return case

    def test_computed_survivors_equal_real_pinned_aggregation(self):
        case = self.case()
        archive, _units = case.inputs()
        survivors = ctx.survivor_set(archive, case.row, case.read("derived/roster.json"))
        source, _screen, _bracket, aggregated = case.pinned_rescreen()
        self.assertEqual(source, "survivor_rescreen")
        self.assertTrue(aggregated)
        self.assertEqual(survivors.bundle_ids, aggregated)
        self.assertEqual(sum(map(len, survivors.by_slot.values())), len(aggregated))

    def test_real_producer_missing_slot_fields_is_explicit_gap(self):
        case = self.case(contract_roster=False)
        archive, units = case.inputs()
        roster = ctx.authenticated_roster(archive)
        self.assertEqual(ctx.roster_references(roster), {})
        with self.assertRaisesRegex(AnalysisRefusal, "^survivor_set_count_mismatch$"):
            ctx.build_context(archive.window, archive, units, case.assessment, case.row)

    def test_recorded_counts_changed_with_rebound_digests_refuses(self):
        case = self.case()
        screen = case.read("derived/neg8-screen.json")
        screen["rescreen"]["survivors"]["reference_counts"] = {"start": 2, "midpoint": 1, "end": 3}
        case.write("derived/neg8-screen.json", screen)
        with self.assertRaisesRegex(AnalysisRefusal, "^survivor_set_count_mismatch$"):
            case.build()
        screen["rescreen"]["survivors"]["reference_counts"] = None
        case.write("derived/neg8-screen.json", screen)
        with self.assertRaisesRegex(AnalysisRefusal, "^survivor_set_count_mismatch$"):
            case.build()

    def test_historical_counts_absent_requires_full_plan_without_losses(self):
        case = self.case()
        screen = case.read("derived/neg8-screen.json")
        screen["rescreen"]["survivors"].pop("reference_counts", None)
        case.write("derived/neg8-screen.json", screen)
        self.assertTrue(case.build().survivor_bundle_ids)
        refs = ctx.roster_references(case.read("derived/roster.json"))
        screen["harvest_reference_losses"] = {next(iter(refs)): "member.timeout"}
        case.write("derived/neg8-screen.json", screen)
        with self.assertRaisesRegex(AnalysisRefusal, "^survivor_set_count_mismatch$"):
            case.build()

    def test_second_bound_returns_new_immutable_context_and_same_set(self):
        case = self.case()
        first = case.build()
        assessment = copy.deepcopy(case.assessment)
        assessment["b_fiducial_s"] += 0.001
        second = case.build(bracket=assessment)
        self.assertIsNot(first, second)
        self.assertNotEqual(first.window_bracket["b_fiducial_s"], second.window_bracket["b_fiducial_s"])
        self.assertEqual(first.survivor_bundle_ids, second.survivor_bundle_ids)
        with self.assertRaises(FrozenInstanceError):
            first.survivor_bundle_ids = frozenset()

    def test_standard_context_admitted_with_survivor_allowance(self):
        case = self.case()
        context = case.build()
        with fx.adapter_projection(case):
            result = ww.validate_whole_window_verdict_row(case.row, case.window.claim, set(case.row["bundle_ids"]),
                consumption_session=case.session(context))
        self.assertTrue(result.admitted, result.reasons)
        self.assertEqual(result.reasons, ())
        self.assertEqual(result.allowance_source, "survivor_rescreen")

    def test_removed_ids_include_every_member_of_a_dropped_unit(self):
        case = self.case()
        _archive, units = case.inputs()
        quad = next(iter(next(iter(units.cells.values())).kept["quad"]))
        case.exclude(quad.run_ids[0], "thermal.os_level_nonzero")
        context = case.build()
        self.assertTrue(set(quad.run_ids) <= context.removed_bundle_ids)
        self.assertEqual(context.removed_bundle_ids, frozenset(quad.run_ids))

    def test_survivor_object_computed_once_and_shared_by_tripwire_and_context(self):
        case = self.case()
        actual = ctx.survivor_set
        seen = []
        def tripwire(archive, survivor, excluded):
            seen.append(survivor)
        with mock.patch.object(ctx, "survivor_set", wraps=actual) as compute, \
                mock.patch.object(ctx, "excluded_reference_in_screen", side_effect=tripwire):
            context = case.build()
        self.assertEqual(compute.call_count, 1)
        self.assertIs(context.survivor_bundle_ids, seen[0].bundle_ids)

    def test_both_loss_lists_and_basis_are_used(self):
        case = self.case()
        archive, _units = case.inputs()
        refs = ctx.roster_references(case.read("derived/roster.json"))
        target = next(run for run, slot in refs.items() if slot == "end")
        screen = case.read("derived/neg8-screen.json")
        screen["rescreen"]["survivors"].update(reference_counts={"start": 3, "midpoint": 1, "end": 2},
            reference_losses=[{"bundle_id": target, "position": "end", "reason": "strict_invalid"}])
        case.write("derived/neg8-screen.json", screen)
        archive, _units = case.inputs()
        result = ctx.survivor_set(archive, case.row, case.read("derived/roster.json"))
        self.assertNotIn(target, result.bundle_ids)
        self.assertIn(target, result.basis_reference_ids)
        bad_row = copy.deepcopy(case.row)
        bad_row["evaluation_basis"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(AnalysisRefusal, "^evaluation_basis_invalid$"):
            ctx.survivor_set(archive, bad_row, case.read("derived/roster.json"))
        # A writer-omitted reference is neither a survivor nor an invented
        # loss. Remove it from both the validated basis and row membership.
        case = self.case()
        refs = ctx.roster_references(case.read("derived/roster.json"))
        target = next(run for run, slot in refs.items() if slot == "start")
        case.row["bundle_ids"].remove(target)
        case.row["evaluation_basis"]["member_occurrences"] = [item for item in
            case.row["evaluation_basis"]["member_occurrences"] if item["bundle_id"] != target]
        case.rehash_basis()
        screen = case.read("derived/neg8-screen.json")
        screen["rescreen"]["survivors"]["reference_counts"] = {"start": 2, "midpoint": 1, "end": 3}
        case.write("derived/neg8-screen.json", screen)
        archive, _units = case.inputs()
        result = ctx.survivor_set(archive, case.row, case.read("derived/roster.json"))
        self.assertNotIn(target, result.bundle_ids)
        self.assertNotIn(target, result.basis_reference_ids)

    def test_harvest_loss_list_without_evaluator_loss_row(self):
        case = self.case()
        refs = ctx.roster_references(case.read("derived/roster.json"))
        target = next(run for run, slot in refs.items() if slot == "end")
        screen = case.read("derived/neg8-screen.json")
        screen["harvest_reference_losses"] = {target: "member.timeout"}
        screen["rescreen"]["survivors"].update(reference_counts={"start": 3, "midpoint": 1, "end": 2}, reference_losses=[])
        case.write("derived/neg8-screen.json", screen)
        archive, _units = case.inputs()
        result = ctx.survivor_set(archive, case.row, case.read("derived/roster.json"))
        self.assertNotIn(target, result.bundle_ids)

    def test_authenticated_roster_and_exclusions_cannot_be_substituted(self):
        case = self.case()
        archive, _units = case.inputs()
        fake = case.read("derived/roster.json")
        fake["members"][0]["neg8_slot"] = "start"
        with self.assertRaisesRegex(AnalysisRefusal, "^context_roster_differs_from_archive$"):
            ctx.excluded_references(archive, fake)
        path = case.archive / "derived/exclusions.json"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaisesRegex(AnalysisRefusal, "^exclusions_record_unauthenticated$"):
            ctx.excluded_references(archive, case.read("derived/roster.json"))

    def test_no_typed_survivor_list_in_stage_tests_or_fixture(self):
        # A list of energy mock-adapter inputs is not a survivor expectation.
        # Any expected survivor set must originate in the computed function
        # or in the actual pinned evaluator's observed aggregation.
        for relative in ("test_context.py", "test_tripwires.py", "test_sources_replay.py", "fixtures_s3b.py"):
            tree = ast.parse((Path(__file__).parent / relative).read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.keyword) and node.arg == "survivor_bundle_ids":
                    self.assertFalse(isinstance(node.value, (ast.List, ast.Set, ast.Tuple)), relative)
                    if isinstance(node.value, ast.Call):
                        self.assertFalse(any(isinstance(arg, (ast.List, ast.Set, ast.Tuple)) for arg in node.value.args), relative)
        source = inspect.getsource(fx.Case.__init__)
        self.assertNotIn("s3.context(", source)
