"""Context construction, survivor accounting and archive authentication."""
import ast
import copy
from dataclasses import FrozenInstanceError, replace
import inspect
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
from unittest import mock

from joulewise import whole_window as ww
from joulewise.b5 import harvest
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

    def test_builder_uses_archive_window_and_refuses_foreign_kept_window(self):
        case = self.case()
        archive, units = case.inputs()
        self.assertNotIn("window", inspect.signature(ctx.build_context).parameters)
        foreign = replace(units, window=replace(units.window, plan_id="counterfactual-other-window"))
        with self.assertRaisesRegex(AnalysisRefusal, "^context_window_mismatch$"):
            ctx.build_context(archive, foreign, case.assessment, case.row, test_only_allow_synthetic_binding=True)

    def test_builder_refuses_foreign_kept_record_digests(self):
        case = self.case()
        archive, units = case.inputs()
        for field in ("roster_sha256", "exclusions_sha256"):
            with self.subTest(field=field):
                foreign = replace(units, **{field: "0" * 64})
                with self.assertRaisesRegex(AnalysisRefusal, "^context_kept_units_mismatch$"):
                    ctx.build_context(archive, foreign, case.assessment, case.row, test_only_allow_synthetic_binding=True)

    def test_builder_refuses_foreign_window_bracket(self):
        from types import SimpleNamespace
        case = self.case()
        archive, units = case.inputs()
        bracket = SimpleNamespace(window=replace(archive.window, plan_id="counterfactual-other-window"),
                                  evaluation=case.assessment)
        with self.assertRaisesRegex(AnalysisRefusal, "^context_window_mismatch$"):
            ctx.build_context(archive, units, bracket, case.row, test_only_allow_synthetic_binding=True)

    def test_synthetic_context_requires_explicit_named_test_argument(self):
        case = self.case()
        archive, units = case.inputs()
        self.assertEqual(archive.plan_tree_binding_kind, "synthetic")
        for value in (False, None, 1, "true"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(AnalysisRefusal, "^context_synthetic_binding_requires_test$"):
                    ctx.build_context(archive, units, case.assessment, case.row,
                                      test_only_allow_synthetic_binding=value)
        with self.assertRaisesRegex(AnalysisRefusal, "^context_synthetic_binding_requires_test$"):
            ctx.build_context(archive, units, case.assessment, case.row)
        context = ctx.build_context(archive, units, case.assessment, case.row, test_only_allow_synthetic_binding=True)
        self.assertEqual(context.neg8_harvest_archive, archive.window.archive_root)
        binding = next(row for row in archive.census() if row.path == "binding/plan_tree")
        self.assertEqual(binding.check, "plan_tree_binding:synthetic")
        self.assertEqual(binding.sha256, case.plan_tree_digest)

    def test_survivor_record_loss_and_count_edits_cannot_hide_excluded_reference(self):
        case = self.case()
        roster = case.roster()
        target = next(run for run, slot in ctx.roster_references(roster).items() if slot == "start")
        case.exclude(target, "member.whole_window_member_failure")
        screen = case.read("derived/neg8-screen.json")
        screen["rescreen"]["survivors"].update(reference_counts={"start": 2, "midpoint": 1, "end": 3},
            reference_losses=[{"bundle_id": target, "position": "start", "reason": "strict_invalid"}])
        case.write("derived/neg8-screen.json", screen)
        archive = case.handle()
        with self.assertRaisesRegex(AnalysisRefusal, "^survivor_set_record_differs_from_bracket$"):
            ctx.survivor_set(archive, case.row, case.roster(archive))

    def test_survivor_record_loss_reason_must_equal_withheld_bracket(self):
        case = self.case()
        target = next(run for run, slot in ctx.roster_references(case.roster()).items() if slot == "end")
        screen = case.read("derived/neg8-screen.json")
        screen["rescreen"]["survivors"].update(reference_counts={"start": 3, "midpoint": 1, "end": 2},
            reference_losses=[{"bundle_id": target, "position": "end", "reason": "strict_invalid"}])
        case.write_survivors(screen)
        screen["rescreen"]["survivors"]["reference_losses"][0]["reason"] = "counterfactual-loss-reason"
        case.write("derived/neg8-screen.json", screen)
        archive = case.handle()
        with self.assertRaisesRegex(AnalysisRefusal, "^survivor_set_record_differs_from_bracket$"):
            ctx.survivor_set(archive, case.row, case.roster(archive))

    def test_survivor_withheld_bracket_must_authenticate(self):
        case = self.case()
        path = case.archive / ww.NEG8_HARVEST_SURVIVOR_BRACKET
        path.write_bytes(path.read_bytes() + b" ")
        archive = case.handle()
        with self.assertRaisesRegex(AnalysisRefusal, "^survivor_bracket_unauthenticated$"):
            ctx.survivor_set(archive, case.row, case.roster(archive))

    def test_missing_rescreen_and_malformed_survivors_are_closed_refusals(self):
        case = self.case()
        original = case.read("derived/neg8-screen.json")
        for value in (None, [], "malformed"):
            for field in ("rescreen", "survivors"):
                with self.subTest(field=field, value=value):
                    screen = copy.deepcopy(original)
                    if field == "rescreen":
                        screen[field] = value
                    else:
                        screen["rescreen"][field] = value
                    if field == "rescreen" and value is not None:
                        # S0 already refuses a non-mapping rescreen. Probe
                        # this function's independent guard as well.
                        with mock.patch.object(ctx, "read_output", return_value=screen):
                            with self.assertRaisesRegex(AnalysisRefusal, "^neg8_screen_record_invalid$"):
                                ctx.read_screen_record(case.handle())
                    else:
                        case.write("derived/neg8-screen.json", screen)
                        with self.assertRaisesRegex(AnalysisRefusal, "^neg8_screen_record_invalid$"):
                            ctx.rebuilt_roster(case.handle(), case.row)
                        with self.assertRaisesRegex(AnalysisRefusal, "^neg8_screen_record_invalid$"):
                            ctx.read_screen_record(case.handle())
        case.write("derived/neg8-screen.json", {key: value for key, value in original.items() if key != "rescreen"})
        with self.assertRaisesRegex(AnalysisRefusal, "^neg8_screen_record_invalid$"):
            ctx.rebuilt_roster(case.handle(), case.row)

    def test_authenticated_roster_rejects_identity_and_supplied_copy(self):
        case = self.case()
        archive = case.handle()
        actual = ctx.authenticated_roster(archive)
        for field in ("schema", "pack_id", "plan_id", "attempt"):
            with self.subTest(field=field):
                wrong = copy.deepcopy(actual)
                wrong[field] = "counterfactual"
                case.write("derived/roster.json", wrong)
                with self.assertRaisesRegex(AnalysisRefusal, "^context_roster_invalid$"):
                    ctx.authenticated_roster(case.handle())
        case.write("derived/roster.json", actual)
        with self.assertRaisesRegex(AnalysisRefusal, "^context_roster_differs_from_archive$"):
            ctx.authenticated_roster(case.handle(), {**actual, "members": []})

    def test_survivor_loss_record_shape_refuses_at_survivor_function(self):
        case = self.case()
        roster = case.roster()
        original = case.read("derived/neg8-screen.json")
        for field, value in (("harvest_reference_losses", {"synthetic": 1}),
                             ("reference_losses", "malformed"),
                             ("reference_losses", [{"bundle_id": "synthetic", "reason": None}])):
            with self.subTest(field=field, value=value):
                screen = copy.deepcopy(original)
                if field == "harvest_reference_losses":
                    screen[field] = value
                else:
                    screen["rescreen"]["survivors"][field] = value
                case.write("derived/neg8-screen.json", screen)
                archive = case.handle()
                # Isolate this function's guard from the roster replay's
                # earlier parser, using its real, already computed roster.
                with mock.patch.object(ctx, "checked_rebuilt_roster", return_value=roster):
                    with self.assertRaisesRegex(AnalysisRefusal, "^survivor_set_record_invalid$"):
                        ctx.survivor_set(archive, case.row, roster)

    def test_excluded_record_shape_and_member_codes_refuse_at_reader(self):
        case = self.case()
        original = case.read("derived/exclusions.json")
        for value in (None, [{"run_id": "synthetic", "codes": []}],
                      [{"run_id": "synthetic", "codes": [None]}]):
            with self.subTest(value=value):
                case.write("derived/exclusions.json", {**original, "members_excluded": value})
                with self.assertRaisesRegex(AnalysisRefusal, "^exclusions_schema_invalid$"):
                    ctx._excluded(case.handle())

    def test_tripwire_catalog_bytes_must_match_authenticated_catalog_digest(self):
        case = self.case()
        path = Path(case.tmp.name) / "counterfactual-catalog.json"
        path.write_bytes(ctx.CATALOG_PATH.read_bytes() + b" ")
        with mock.patch.object(ctx, "CATALOG_PATH", path):
            with self.assertRaisesRegex(AnalysisRefusal, "^exclusions_catalog_mismatch$"):
                ctx._catalog(case.handle())

    def test_computed_survivors_equal_real_pinned_aggregation(self):
        case = self.case()
        archive = fx.original_handle(case.window)
        row = case.window.writer_row
        original_roster = archive.output_bytes("derived/roster.json")
        self.assertEqual(ctx.roster_references(ctx.authenticated_roster(archive)), {})
        survivors = ctx.survivor_set(archive, row, ctx.rebuilt_roster(archive, row))
        source, _screen, _bracket, aggregated = case.pinned_rescreen(row=row)
        self.assertEqual(source, "survivor_rescreen")
        self.assertTrue(aggregated)
        self.assertEqual(survivors.bundle_ids, aggregated)
        self.assertEqual(sum(map(len, survivors.by_slot.values())), len(aggregated))
        self.assertEqual(fx.s0.sha(case.window.archive / "harvest.json"), case.window.entry.harvest_record_sha256)
        self.assertEqual(original_roster, archive.output_bytes("derived/roster.json"))

    def test_unmodified_producer_projection_is_preserved_and_context_builds(self):
        case = self.case()
        archive, units = case.inputs()
        raw = archive.output_bytes("derived/roster.json")
        self.assertEqual(raw, (case.window.archive / "derived/roster.json").read_bytes())
        self.assertEqual(ctx.roster_references(ctx.authenticated_roster(archive)), {})
        rebuilt = ctx.rebuilt_roster(archive, case.row)
        self.assertTrue(ctx.roster_references(rebuilt))
        context = ctx.build_context(archive, units, case.assessment, case.row, test_only_allow_synthetic_binding=True)
        self.assertEqual(dict(context.roster_references), ctx.roster_references(rebuilt))
        self.assertEqual(raw, archive.output_bytes("derived/roster.json"))

    def test_pack_not_archived_refuses_even_when_unlisted_plan_file_exists(self):
        case = self.case()
        name = case.plan_tree_path().removeprefix("sources/")
        manifest = case.archive / "sources/SHA256SUMS"
        manifest.write_text("\n".join(line for line in manifest.read_text().splitlines()
            if line.split("  ", 1)[1] != name) + "\n")
        self.assertTrue((case.archive / case.plan_tree_path()).is_file())
        with mock.patch.object(harvest, "build_roster", wraps=harvest.build_roster) as build:
            with self.assertRaisesRegex(AnalysisRefusal, "^roster_pack_not_archived$"):
                case.build()
        build.assert_not_called()

    def test_rebuild_materializes_exact_authenticated_repo_inventory(self):
        case = self.case()
        archive = case.handle()
        names = {name for name in archive.source_names() if name.startswith("repo/")}
        unlisted = case.archive / "sources/repo/unlisted-counterfactual.json"
        unlisted.parent.mkdir(parents=True, exist_ok=True)
        unlisted.write_text('{"not_archived":true}')
        real = harvest.build_roster
        def build(pack, repo):
            self.assertEqual(pack, repo / "configs/campaigns" / archive.window.pack_id)
            self.assertNotEqual(repo, case.window.measurement)
            self.assertEqual({path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file()},
                {name.removeprefix("repo/") for name in names})
            return real(pack, repo)
        with mock.patch.object(archive, "source_bytes", wraps=archive.source_bytes) as read, \
                mock.patch.object(harvest, "build_roster", side_effect=build):
            roster = ctx.rebuilt_roster(archive, case.row)
        self.assertTrue(ctx.roster_references(roster))
        self.assertEqual({call.args[0] for call in read.call_args_list}, {"sources/" + name for name in names})
        census = {row.path: row.check for row in archive.census()}
        self.assertEqual(census["sources/SHA256SUMS"], "input_census")
        self.assertTrue(all(census["sources/" + name] == "sources_sha256sums" for name in names))
        self.assertNotIn("sources/repo/unlisted-counterfactual.json", census)

    def test_archived_pack_bytes_must_match_source_manifest(self):
        case = self.case()
        path = case.archive / case.plan_tree_path()
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(AnalysisRefusal, "^archive_source_unauthenticated$"):
            case.build()

    def test_uninvoked_bundleless_spare_retained_in_rebuilt_roster_but_neither_set(self):
        case = self.case()
        archive = fx.original_handle(case.window)
        row = case.window.writer_row
        roster = ctx.rebuilt_roster(archive, row)
        tree = json.loads(archive.source_bytes(case.plan_tree_path()))
        planned = {member["run_id"] for stage in tree["stage_graph"]
            for member in (stage.get("spare_retry") or {}).get("members", [])}
        archived = ctx.authenticated_roster(archive)
        absent = planned - {member["run_id"] for member in archived["members"]}
        self.assertTrue(absent)
        self.assertTrue(absent <= set(ctx.roster_references(roster)))
        self.assertTrue(all(member.get("spare_slot") in ctx.SLOTS for member in roster["members"]
            if member["run_id"] in absent))
        self.assertTrue(absent.isdisjoint(ctx.survivor_set(archive, row, roster).bundle_ids))
        self.assertTrue(absent.isdisjoint(ctx.excluded_references(archive, roster)))

    def test_bundleless_spare_harvest_only_bundle_absent_loss_is_admitted(self):
        # Explicit loss-record counterfactual, not a rewritten reference
        # roster and not evidence that the catalog producer omits this trace.
        case = self.case()
        roster = case.roster()
        archived_ids = {member["run_id"] for member in case.read("derived/roster.json")["members"]}
        spare = next(member["run_id"] for member in roster["members"]
            if member.get("spare_slot") and member["run_id"] not in archived_ids)
        screen = case.read("derived/neg8-screen.json")
        screen["harvest_reference_losses"][spare] = "bundle_absent"
        case.write("derived/neg8-screen.json", screen)
        archive = case.handle()
        roster = case.roster(archive)
        survivors = ctx.survivor_set(archive, case.row, roster)
        self.assertEqual(survivors.harvest_reference_losses[spare], "bundle_absent")
        self.assertNotIn(spare, survivors.bundle_ids)
        self.assertNotIn(spare, ctx.excluded_references(archive, roster))
        self.assertNotIn(spare, case.build().survivor_bundle_ids)

    def test_sources_replay_hands_rebuilt_roster_to_frozen_catalog_helper(self):
        # Wire-only spy; the original catalog archive is tested separately.
        from joulewise.b5_analysis import sources_replay
        case = self.case()
        archive = case.handle()
        row = copy.deepcopy(case.row)
        row["row_provenance"]["source_campaign_manifests"] = []
        row["idle_admission_core"]["conditions"].append("whole_window_campaign_membership_unresolved")
        roster = ctx.rebuilt_roster(archive, row)
        with mock.patch.object(harvest, "claim_neg8_sources", return_value="synthetic_wire_probe") as claim:
            result = sources_replay.replay_claim_sources(row, case.window.claim, archive=archive, roster=roster)
        self.assertEqual(result.problem, "synthetic_wire_probe")
        self.assertIs(claim.call_args.kwargs["roster"], roster)
        self.assertTrue(ctx.roster_references(claim.call_args.kwargs["roster"]))
        self.assertEqual(ctx.roster_references(ctx.authenticated_roster(archive)), {})

    def test_swapped_reference_slots_keep_projection_but_fail_sealed_digest(self):
        case = self.case()
        original = case.roster()
        tree = case.read(case.plan_tree_path())
        stages = [stage for stage in tree["stage_graph"] if stage.get("spare_retry", {}).get("slot") in ("start", "end")]
        self.assertEqual(len(stages), 2)
        stages[0]["spare_retry"]["slot"], stages[1]["spare_retry"]["slot"] = (
            stages[1]["spare_retry"]["slot"], stages[0]["spare_retry"]["slot"])
        raw = json.dumps(tree).encode()
        case.write_source(case.plan_tree_path().removeprefix("sources/"), raw)
        archive = case.handle()
        # Prove equality is insufficient: grant only the counterfactual seal
        # digest, then execute the actual rebuild and projection check.
        with mock.patch.object(archive, "plan_tree_sha256", return_value=hashlib.sha256(raw).hexdigest()):
            swapped = ctx.rebuilt_roster(archive, case.row)
        original_refs, swapped_refs = ctx.roster_references(original), ctx.roster_references(swapped)
        self.assertEqual(set(original_refs), set(swapped_refs))
        self.assertTrue(any(original_refs[run] != swapped_refs[run] for run in original_refs))
        # The real fixture seal remains the original plan's digest.
        with mock.patch.object(harvest, "l4_exclusion_inputs", wraps=harvest.l4_exclusion_inputs) as project:
            with self.assertRaisesRegex(AnalysisRefusal, "^roster_plan_tree_not_sealed$"):
                case.build()
        project.assert_not_called()

    def test_rebuilt_projection_must_equal_archive_member_for_member(self):
        for mode in ("unit", "stage", "missing_reference", "extra_member", "cell", "json_type"):
            with self.subTest(mode=mode):
                case = self.case()
                archived = case.read("derived/roster.json")
                if mode == "unit":
                    member = next(member for member in archived["members"] if member["units"])
                    member["units"][0]["unit_id"] += "-counterfactual"
                elif mode == "stage":
                    archived["members"][0]["stage_id"] = "counterfactual-stage"
                elif mode == "missing_reference":
                    refs = ctx.roster_references(case.roster())
                    archived["members"] = [member for member in archived["members"]
                        if member["run_id"] != next(iter(refs))]
                elif mode == "extra_member":
                    archived["members"].append({"run_id": "counterfactual-extra", "stage_id": "extra",
                        "kind": "auxiliary", "units": []})
                elif mode == "cell":
                    archived["cells"][0]["target"] = not archived["cells"][0]["target"]
                else:
                    archived["cells"][0]["target"] = int(archived["cells"][0]["target"])
                case.write("derived/roster.json", archived)
                with self.assertRaisesRegex(AnalysisRefusal, "^roster_rebuild_differs_from_archive$"):
                    ctx.rebuilt_roster(case.handle(), case.row)

    def test_filtered_spare_may_leave_no_basis_exclusion_or_evaluator_trace(self):
        for mode in ("basis", "exclusion", "evaluator"):
            with self.subTest(mode=mode):
                case = self.case()
                roster = case.roster()
                archived = case.read("derived/roster.json")
                archived_ids = {member["run_id"] for member in archived["members"]}
                spare = next(member["run_id"] for member in roster["members"]
                    if member.get("spare_slot") and member["run_id"] not in archived_ids)
                if mode == "basis":
                    # Authentic basis shape with an occurrence of the omitted
                    # planned spare; the check concerns ids, not a runs scan.
                    basis = ww._validated_evaluation_basis(case.row, case.window.claim)
                    basis = copy.deepcopy(basis)
                    occurrence = copy.deepcopy(basis["member_occurrences"][0])
                    occurrence["bundle_id"] = spare
                    basis["member_occurrences"].append(occurrence)
                    with mock.patch.object(ww, "_validated_evaluation_basis", return_value=basis):
                        with self.assertRaisesRegex(AnalysisRefusal, "^roster_rebuild_differs_from_archive$"):
                            ctx.rebuilt_roster(case.handle(), case.row)
                elif mode == "exclusion":
                    document = case.read("derived/exclusions.json")
                    document["members_excluded"].append({"run_id": spare, "codes": ["member.timeout"]})
                    case.write("derived/exclusions.json", document)
                else:
                    screen = case.read("derived/neg8-screen.json")
                    screen["rescreen"]["survivors"].setdefault("reference_losses", []).append(
                        {"bundle_id": spare, "position": "start", "reason": "bundle_absent"})
                    case.write("derived/neg8-screen.json", screen)
                if mode != "basis":
                    with self.assertRaisesRegex(AnalysisRefusal, "^roster_rebuild_differs_from_archive$"):
                        ctx.rebuilt_roster(case.handle(), case.row)

    def catalog_spare(self):
        case = self.case(name="BETA_SOURCES_RECOVERED")
        screen = case.read("derived/neg8-screen.json")
        archived_ids = {member["run_id"] for member in case.read("derived/roster.json")["members"]}
        spare = next(run for run, reason in screen["harvest_reference_losses"].items()
            if reason == "bundle_absent" and run not in archived_ids)
        loss = next(item for item in screen["rescreen"]["survivors"]["reference_losses"]
            if item["bundle_id"] == spare)
        self.assertEqual(loss["reason"], "bundle_absent")
        self.assertIn(spare, ctx.roster_references(case.roster()))
        return case, screen, spare, loss

    def refuse_catalog_spare(self, case):
        with self.assertRaisesRegex(AnalysisRefusal, "^roster_rebuild_differs_from_archive$"):
            ctx.rebuilt_roster(case.handle(), case.row)

    def test_catalog_absent_spare_evaluator_other_reason_refuses(self):
        case, screen, _spare, loss = self.catalog_spare()
        loss["reason"] = "member.timeout"
        case.write("derived/neg8-screen.json", screen)
        self.refuse_catalog_spare(case)

    def test_catalog_absent_spare_evaluator_without_harvest_loss_refuses(self):
        case, screen, spare, _loss = self.catalog_spare()
        del screen["harvest_reference_losses"][spare]
        case.write("derived/neg8-screen.json", screen)
        self.refuse_catalog_spare(case)

    def test_catalog_absent_spare_harvest_other_reason_refuses(self):
        case, screen, spare, _loss = self.catalog_spare()
        screen["harvest_reference_losses"][spare] = "member.timeout"
        case.write("derived/neg8-screen.json", screen)
        self.refuse_catalog_spare(case)

    def test_catalog_absent_spare_basis_occurrence_refuses(self):
        case, _screen, spare, _loss = self.catalog_spare()
        basis = copy.deepcopy(ww._validated_evaluation_basis(case.row, case.window.claim))
        occurrence = {**basis["member_occurrences"][0], "bundle_id": spare}
        basis["member_occurrences"].append(occurrence)
        with mock.patch.object(ww, "_validated_evaluation_basis", return_value=basis):
            self.refuse_catalog_spare(case)

    def test_catalog_absent_spare_exclusions_entry_refuses(self):
        case, _screen, spare, _loss = self.catalog_spare()
        document = case.read("derived/exclusions.json")
        document["members_excluded"].append({"run_id": spare, "codes": ["member.timeout"]})
        case.write("derived/exclusions.json", document)
        self.refuse_catalog_spare(case)

    def test_build_roster_and_projection_helpers_are_source_equal_at_governing_pins(self):
        names = ("build_roster", "l4_exclusion_inputs", "_resolve_repo_path", "_condition_tag",
                 "_family_workload", "read_json", "sha256_file")
        working = Path(harvest.__file__).read_text()
        def functions(source):
            return {node.name: ast.get_source_segment(source, node) for node in ast.parse(source).body
                if isinstance(node, ast.FunctionDef) and node.name in names}
        actual = functions(working)
        self.assertEqual(set(actual), set(names))
        for shape in ("pin2", "pin4"):
            source = subprocess.check_output(["git", "show", fx.PINS.pins[shape]["head"] + ":joulewise/b5/harvest.py"],
                cwd=fx.ROOT).decode()
            self.assertEqual(actual, functions(source), shape)

    def test_roster_rejects_duplicate_ids_and_both_slot_fields_even_same_slot(self):
        for members in ([{"run_id": "synthetic-ref", "neg8_slot": "start", "spare_slot": "start"}],
                        [{"run_id": "synthetic-ref", "neg8_slot": "start"}] * 2):
            with self.assertRaisesRegex(AnalysisRefusal, "^context_roster_invalid$"):
                ctx.roster_references({"members": members})

    def test_loss_outside_rebuilt_reference_set_still_refuses(self):
        case = self.case()
        screen = case.read("derived/neg8-screen.json")
        screen["harvest_reference_losses"]["counterfactual-not-a-reference"] = "bundle_absent"
        case.write("derived/neg8-screen.json", screen)
        with self.assertRaisesRegex(AnalysisRefusal, "^survivor_set_loss_not_reference$"):
            case.build()

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
        case.write_survivors(screen)
        self.assertTrue(case.build().survivor_bundle_ids)
        refs = ctx.roster_references(case.roster())
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
        refs = ctx.roster_references(case.roster())
        target = next(run for run, slot in refs.items() if slot == "end")
        screen = case.read("derived/neg8-screen.json")
        screen["rescreen"]["survivors"].update(reference_counts={"start": 3, "midpoint": 1, "end": 2},
            reference_losses=[{"bundle_id": target, "position": "end", "reason": "strict_invalid"}])
        case.write_survivors(screen)
        archive, _units = case.inputs()
        result = ctx.survivor_set(archive, case.row, case.roster(archive))
        self.assertNotIn(target, result.bundle_ids)
        self.assertIn(target, result.basis_reference_ids)
        bad_row = copy.deepcopy(case.row)
        bad_row["evaluation_basis"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(AnalysisRefusal, "^evaluation_basis_invalid$"):
            ctx.survivor_set(archive, bad_row, case.roster(archive))
        # A writer-omitted reference is neither a survivor nor an invented
        # loss. Remove it from both the validated basis and row membership.
        case = self.case()
        refs = ctx.roster_references(case.roster())
        target = next(run for run, slot in refs.items() if slot == "start")
        case.row["bundle_ids"].remove(target)
        case.row["evaluation_basis"]["member_occurrences"] = [item for item in
            case.row["evaluation_basis"]["member_occurrences"] if item["bundle_id"] != target]
        case.rehash_basis()
        screen = case.read("derived/neg8-screen.json")
        screen["rescreen"]["survivors"]["reference_counts"] = {"start": 2, "midpoint": 1, "end": 3}
        case.write_survivors(screen)
        archive, _units = case.inputs()
        result = ctx.survivor_set(archive, case.row, case.roster(archive))
        self.assertNotIn(target, result.bundle_ids)
        self.assertNotIn(target, result.basis_reference_ids)

    def test_harvest_loss_list_without_evaluator_loss_row(self):
        case = self.case()
        refs = ctx.roster_references(case.roster())
        target = next(run for run, slot in refs.items() if slot == "end")
        screen = case.read("derived/neg8-screen.json")
        screen["harvest_reference_losses"] = {target: "member.timeout"}
        screen["rescreen"]["survivors"].update(reference_counts={"start": 3, "midpoint": 1, "end": 2}, reference_losses=[])
        case.write_survivors(screen)
        archive, _units = case.inputs()
        result = ctx.survivor_set(archive, case.row, case.roster(archive))
        self.assertNotIn(target, result.bundle_ids)

    def test_authenticated_roster_and_exclusions_cannot_be_substituted(self):
        case = self.case()
        archive, _units = case.inputs()
        fake = ww._archive_thaw(case.roster(archive))
        fake["members"][0]["neg8_slot"] = "start"
        with self.assertRaisesRegex(AnalysisRefusal, "^context_roster_differs_from_archive$"):
            ctx.excluded_references(archive, fake)
        path = case.archive / "derived/exclusions.json"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaisesRegex(AnalysisRefusal, "^exclusions_record_unauthenticated$"):
            ctx.excluded_references(archive, case.roster(archive))

    def test_copied_rebuilt_roster_cannot_inherit_authentication(self):
        case = self.case()
        archive = case.handle()
        roster = case.roster(archive)
        document = ww._archive_thaw(roster)
        member = next(member for member in document["members"] if member.get("spare_slot"))
        member["spare_slot"] = "start" if member["spare_slot"] == "end" else "end"
        replacement = replace(roster, _document=ctx.freeze(document))
        with self.assertRaisesRegex(AnalysisRefusal, "^context_roster_differs_from_archive$"):
            ctx.survivor_set(archive, case.row, replacement)
        with self.assertRaisesRegex(AnalysisRefusal, "^context_roster_differs_from_archive$"):
            ctx.excluded_references(archive, replacement)

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
