"""Erratum-2 recovery and X3 catalog provenance, entirely synthetic."""
import copy
from dataclasses import replace
import hashlib
from pathlib import Path
import unittest
from unittest import mock

from joulewise import whole_window as ww
from joulewise.b5 import harvest
from joulewise.b5_analysis import sources_replay as replay
from joulewise.b5_analysis.context import roster_references
from joulewise.campaign_provenance import load_authenticated_campaign_catalog
from tests.b5_analysis import fixtures_s3b as fx

_WINDOWS = {}


class SourcesReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if "BETA_SOURCES_RECOVERED" not in _WINDOWS:
            _WINDOWS["BETA_SOURCES_RECOVERED"] = fx.cached("BETA_SOURCES_RECOVERED")

    def case(self):
        case = fx.Case("BETA_SOURCES_RECOVERED")
        self.addCleanup(case.close)
        return case

    def run_replay(self, case, row=None, roster=None):
        archive = case.handle()
        with fx.adapter_projection(case):
            return replay.replay_claim_sources(row or case.row, case.window.claim, archive=archive,
                roster=roster if roster is not None else case.roster(archive))

    def test_recovered_catalog_feeds_core_and_reference_rederivation(self):
        case = self.case()
        real_derive = ww._derived_neg8_decision
        real_core = ww._current_core_rederivation_reasons
        with fx.adapter_projection(case), mock.patch.object(ww, "_derived_neg8_decision", wraps=real_derive) as derive, \
                mock.patch.object(ww, "_current_core_rederivation_reasons", wraps=real_core) as core:
            context = case.build()
            result = ww.validate_whole_window_verdict_row(case.row, case.window.claim, set(case.row["bundle_ids"]),
                consumption_session=case.session(context))
        self.assertTrue(result.admitted, result.reasons)
        self.assertIn("whole_window_campaign_membership_unresolved", result.answered_conditions)
        self.assertTrue(context.catalog_manifests)
        core_call = core.call_args
        paths = ww._manifest_bundle_paths(core_call.kwargs["manifests"], case.window.claim)
        self.assertEqual(set(paths), set(case.row["bundle_ids"]))
        # The final validator call also replays the catalog survivor bracket.
        self.assertTrue(derive.call_args.kwargs["require_replicated_endpoints"])
        self.assertEqual(derive.call_args.kwargs["unreadable_energy"], "lost")

    def test_item6_arguments_and_projected_manifests(self):
        case = self.case()
        real = ww._derived_neg8_decision
        with mock.patch.object(ww, "_derived_neg8_decision", wraps=real) as derive:
            result = self.run_replay(case)
        self.assertIsNone(result.problem)
        call = derive.call_args
        for key in ("point_drift", "current", "require_replicated_endpoints", "return_bracket"):
            self.assertIs(call.kwargs[key], True)
        self.assertEqual(call.kwargs["unreadable_energy"], "lost")
        self.assertEqual(call.kwargs["exclude_bundle_ids"], dict(result.reference_losses))
        self.assertEqual(call.kwargs["required_reference_ids"], frozenset(roster_references(case.roster())))
        self.assertEqual(call.kwargs["drift_bound_artifact"], case.read(ww.NEG8_HARVEST_CLEAN_BOUND)["bound"])
        self.assertIsNotNone(call.kwargs["surviving_reference_check"])
        paths = ww._manifest_bundle_paths(ww._archive_thaw(result.projected_manifests), case.window.claim)
        self.assertEqual(set(paths), set(case.row["bundle_ids"]))
        for descriptor, _manifest in result.catalog_manifests:
            raw = (case.window.claim / descriptor["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), descriptor["sha256"])

    def test_replay_required_no_callable_or_empty_catalog_refuses(self):
        case = self.case()
        with fx.adapter_projection(case):
            context = case.build()
            for changed in (replace(context, sources_replay=None), replace(context, catalog_manifests=())):
                with self.subTest(empty_catalog=not changed.catalog_manifests):
                    result = ww.validate_whole_window_verdict_row(case.row, case.window.claim, set(case.row["bundle_ids"]),
                        consumption_session=case.session(changed))
                    self.assertFalse(result.admitted)
                    if not changed.catalog_manifests:
                        self.assertIn("core_rederivation_sources_empty", result.reasons)

    def test_recorded_recovery_preconditions_are_required(self):
        for field in ("source", "evaluated", "decision"):
            with self.subTest(field=field):
                case = self.case()
                screen = case.read("derived/neg8-screen.json")
                if field == "source":
                    screen["rescreen"]["reference_source"]["source"] = "verdict_sources"
                elif field == "evaluated":
                    screen["rescreen"][field] = False
                else:
                    screen["rescreen"][field] = "failed"
                case.write("derived/neg8-screen.json", screen)
                with mock.patch.object(replay, "replay_claim_sources") as called:
                    context = case.build()
                called.assert_not_called()
                self.assertIsNone(context.sources_replay)
                with fx.adapter_projection(case):
                    result = ww.validate_whole_window_verdict_row(case.row, case.window.claim, set(case.row["bundle_ids"]),
                        consumption_session=case.session(context))
                self.assertFalse(result.admitted)
                self.assertIn("whole_window_verdict_provenance_invalid", result.reasons)

    def test_bundleless_spare_is_rebuilt_neither_survivor_nor_excluded_and_loss_admitted(self):
        case = self.case()
        archive = fx.original_handle(case.window)
        from joulewise.b5_analysis import context as ctx
        row = case.window.writer_row
        roster = ctx.rebuilt_roster(archive, row)
        archived = case.read("derived/roster.json")
        self.assertEqual(archive.output_bytes("derived/roster.json"),
            (case.window.archive / "derived/roster.json").read_bytes())
        roster_ids = {member["run_id"] for member in archived["members"]}
        losses = case.read("derived/neg8-screen.json")["harvest_reference_losses"]
        absent = {run for run, reason in losses.items() if reason == "bundle_absent"}
        self.assertTrue(absent)
        self.assertTrue(absent.isdisjoint(roster_ids))
        refs = roster_references(roster)
        survivors = ctx.survivor_set(archive, row, roster)
        excluded = ctx.excluded_references(archive, roster)
        self.assertTrue(absent <= set(refs))
        self.assertTrue(all(member.get("spare_slot") in ctx.SLOTS for member in roster["members"]
            if member["run_id"] in absent))
        self.assertTrue(absent.isdisjoint(survivors.bundle_ids))
        self.assertTrue(absent.isdisjoint(excluded))
        self.assertTrue(absent <= set(survivors.harvest_reference_losses))
        real = harvest.claim_neg8_sources
        with fx.adapter_projection(case), mock.patch.object(harvest, "claim_neg8_sources", wraps=real) as claim:
            result = replay.replay_claim_sources(row, case.window.claim, archive=archive, roster=roster)
        self.assertIsNone(result.problem)
        self.assertTrue(absent <= set(roster_references(claim.call_args.kwargs["roster"])))
        units = fx.load_kept_units(archive, sealed_catalog_sha256=fx.PINS.sealed["catalog_sha256"],
            planned_units=fx.s0_planned())
        with fx.adapter_projection(case):
            context = ctx.build_context(archive.window, archive, units, case.assessment, row)
        self.assertTrue(context.catalog_manifests)
        self.assertEqual(context.neg8_harvest_archive, case.window.archive)
        self.assertTrue(absent.isdisjoint(context.survivor_bundle_ids))

    def test_original_catalog_matching_absence_losses_accept_rebuild(self):
        # Original indexed archive and writer row, with no output rebind.
        case = self.case()
        archive = fx.original_handle(case.window)
        from joulewise.b5_analysis import context as ctx
        screen = ctx.read_output(archive, "derived/neg8-screen.json")
        archived = ctx.authenticated_roster(archive)
        absent = {run for run, reason in screen["harvest_reference_losses"].items() if reason == "bundle_absent"}
        self.assertTrue(absent)
        self.assertTrue(absent.isdisjoint({member["run_id"] for member in archived["members"]}))
        evaluator = {item["bundle_id"]: item["reason"]
            for item in screen["rescreen"]["survivors"]["reference_losses"]}
        self.assertTrue(absent <= set(evaluator))
        self.assertTrue(all(evaluator[run] == "bundle_absent" for run in absent))
        roster = ctx.rebuilt_roster(archive, case.window.writer_row)
        survivors = ctx.survivor_set(archive, case.window.writer_row, roster)
        self.assertTrue(absent <= set(roster_references(roster)))
        self.assertTrue(absent.isdisjoint(survivors.bundle_ids))
        self.assertTrue(absent.isdisjoint(ctx.excluded_references(archive, roster)))
        self.assertEqual(fx.s0.sha(case.window.archive / "harvest.json"), case.window.entry.harvest_record_sha256)

    def test_replay_problem_stops_builder_and_validator(self):
        case = self.case()
        from joulewise.b5_analysis.windows import AnalysisRefusal
        with mock.patch.object(replay, "replay_claim_sources", return_value=replay.SourcesReplay("reference_not_in_roster")):
            with self.assertRaisesRegex(AnalysisRefusal, "^reference_not_in_roster$"):
                case.build()
        with fx.adapter_projection(case):
            context = replace(case.build(), sources_replay=lambda _row, _root: "reference_not_in_roster")
            result = ww.validate_whole_window_verdict_row(case.row, case.window.claim, set(case.row["bundle_ids"]),
                consumption_session=case.session(context))
        self.assertFalse(result.admitted)
        self.assertIn("whole_window_verdict_provenance_invalid", result.reasons)
        self.assertIn("reference_not_in_roster", result.detail)

    def test_trigger_a_clock_b_c_are_exact(self):
        case = self.case()
        row = copy.deepcopy(case.row)
        row["row_provenance"]["source_campaign_manifests"] = [{"path": "recorded"}]
        self.assertEqual(self.run_replay(case, row).problem, "sources_replay_not_applicable")
        archive = case.handle()
        archive.window = replace(archive.window, governed_e2=False)
        self.assertEqual(replay.replay_claim_sources(case.row, case.window.claim, archive=archive,
            roster=case.roster()).problem, "recovery_predates_erratum")
        with fx.adapter_projection(case), mock.patch("joulewise.window_lineage.is_hazard_runs_root", return_value=False):
            result = replay.replay_claim_sources(case.row, case.window.claim, archive=case.handle(), roster=case.roster())
        self.assertEqual(result.problem, "runs_root_not_hazard")
        for word in ("missing", "whole_window_campaign_membership_ambiguous", "campaign_occurrence_unresolved"):
            row = copy.deepcopy(case.row)
            if word == "missing":
                row["idle_admission_core"]["conditions"].remove("whole_window_campaign_membership_unresolved")
            else:
                row["idle_admission_core"]["conditions"].append(word)
            self.assertEqual(self.run_replay(case, row).problem, "membership_condition_not_unresolved")

    def test_catalog_authentication_schema_and_trigger_d_e_f(self):
        case = self.case()
        catalog = load_authenticated_campaign_catalog(case.window.claim, case.window.claim / "campaign_log.jsonl")
        for supplied, word in ((None, "source_manifest_unauthenticated"), ([], "source_manifests_unrecorded"),
                ([replace(catalog[0], value={**catalog[0].value, "schema_version": "joulewise.campaign_provenance.v1"})],
                 "source_manifest_schema_v1")):
            with mock.patch("joulewise.campaign_provenance.load_authenticated_campaign_catalog", return_value=supplied):
                self.assertEqual(self.run_replay(case).problem, word)
        original = ww.ordinary_present_bundle_paths
        with mock.patch.object(ww, "ordinary_present_bundle_paths", side_effect=lambda root, run: [root / run]):
            self.assertEqual(self.run_replay(case).problem, "no_absent_invoked_member")
        def ambiguous(root, run):
            paths = original(root, run)
            return paths * 2 if paths else paths
        with mock.patch.object(ww, "ordinary_present_bundle_paths", side_effect=ambiguous):
            self.assertEqual(self.run_replay(case).problem, "invoked_member_ambiguous")
        with mock.patch.object(ww, "_is_recognizable_occurrence_supersession", return_value=True):
            self.assertEqual(self.run_replay(case).problem, "occurrence_supersession_present")

    def test_policy_member_path_and_roster_checks(self):
        case = self.case()
        row = copy.deepcopy(case.row)
        row["campaign_policy"]["sha256"] = "0" * 64
        # Keep the basis valid so this counterfactual reaches the policy
        # registration check after the authenticated roster rebuild.
        basis = row["evaluation_basis"]
        basis["policy_sha256"] = row["campaign_policy"]["sha256"]
        basis["sha256"] = ww.canonical_sha256({key: value for key, value in basis.items() if key != "sha256"})
        self.assertEqual(self.run_replay(case, row).problem, "policy_unregistered")
        catalog = load_authenticated_campaign_catalog(case.window.claim, case.window.claim / "campaign_log.jsonl")
        for mode, word in (("policy", "source_manifest_policy_differs"), ("duplicate", "source_manifest_members_invalid"),
                           ("path", "source_manifest_path_invalid")):
            values = list(catalog)
            value = copy.deepcopy(values[0].value)
            path = values[0].path
            if mode == "policy":
                value["campaign_policy"]["sha256"] = "0" * 64
            elif mode == "duplicate":
                value["members"].append(value["members"][0])
            else:
                path = Path("..")
            values[0] = replace(values[0], value=value, path=path)
            with mock.patch("joulewise.campaign_provenance.load_authenticated_campaign_catalog", return_value=values):
                self.assertEqual(self.run_replay(case).problem, word)
        roster = ww._archive_thaw(case.roster())
        target = next(iter(roster_references(roster)))
        for member in roster["members"]:
            if member["run_id"] == target:
                member.pop("neg8_slot", None)
                member.pop("spare_slot", None)
        self.assertEqual(self.run_replay(case, roster=roster).problem, "context_roster_differs_from_archive")

    def test_reference_role_position_disagreement_is_not_a_passing_screen(self):
        case = self.case()
        catalog = load_authenticated_campaign_catalog(case.window.claim, case.window.claim / "campaign_log.jsonl")
        changed = []
        altered = False
        for record in catalog:
            value = copy.deepcopy(record.value)
            for member in value["members"]:
                if not altered and member.get("sentinel_position") == "start":
                    # A malformed role/position pair from the authenticated
                    # catalog provider; all other source inputs stay real.
                    member["role"] = "neg8_daily_reference_start"
                    member["sentinel_position"] = "end"
                    altered = True
            changed.append(replace(record, value=value))
        self.assertTrue(altered)
        with mock.patch("joulewise.campaign_provenance.load_authenticated_campaign_catalog", return_value=changed):
            self.assertEqual(self.run_replay(case).problem, "sources_replay_screen_not_passed")

    def test_recomputed_losses_not_copied_from_screen(self):
        case = self.case()
        target = next(iter(roster_references(case.roster())))
        case.exclude(target, "member.timeout")
        result = self.run_replay(case)
        self.assertEqual(result.problem, "sources_replay_losses_differ")

    def test_loss_recompute_equals_frozen_harvest_evaluation(self):
        case = self.case()
        source, screen, _bracket, aggregated = case.pinned_rescreen()
        self.assertEqual(source, "survivor_rescreen")
        result = self.run_replay(case)
        self.assertIsNone(result.problem)
        self.assertEqual(dict(result.reference_losses), screen["harvest_reference_losses"])
        self.assertTrue(aggregated)
        self.assertTrue(all(run not in aggregated for run in result.reference_losses))

    def test_harvest_loss_outside_invoked_catalog_is_compared_without_counting_it(self):
        case = self.case()
        roster = case.roster()
        catalog = load_authenticated_campaign_catalog(case.window.claim, case.window.claim / "campaign_log.jsonl")
        invoked = {run for record in catalog for member in record.value["members"]
            if member.get("execution") == "invoked" for run in member["bundle_ids"]}
        unused = next(member["run_id"] for member in roster["members"]
            if member.get("spare_slot") and member["run_id"] not in invoked)
        # An absent, uninvoked spare can have a harvest-only loss flag, but
        # the exclusion function never received it; X(W) must stay empty.
        flags = case.flags() + [{"code": "member.timeout", "scope": {"level": "member", "run_id": unused}}]
        case.write("derived/flags.jsonl", flags)
        source, screen, bracket, aggregated = case.pinned_rescreen()
        self.assertEqual(source, "survivor_rescreen")
        self.assertIn(unused, screen["harvest_reference_losses"])
        self.assertNotIn(unused, aggregated)
        case.install_rescreen(screen, bracket)
        result = self.run_replay(case)
        self.assertIsNone(result.problem)
        self.assertEqual(result.reference_losses[unused], "member.timeout")

    def test_config_flag_does_not_change_replay_loss_predicate(self):
        case = self.case()
        target = next(iter(roster_references(case.roster())))
        case.exclude(target, "member.config_not_in_inventory")
        result = self.run_replay(case)
        self.assertIsNone(result.problem)
        self.assertNotIn(target, result.reference_losses)

    def test_loss_precedence_and_lost_reference_energy_is_not_read(self):
        case = self.case()
        target = next(run for run, slot in roster_references(case.roster()).items() if slot == "end")
        case.exclude(target, "member.timeout")
        case.exclude(target, "thermal.os_level_nonzero")
        source, screen, bracket, aggregated = case.pinned_rescreen()
        self.assertEqual(source, "survivor_rescreen")
        self.assertNotIn(target, aggregated)
        case.install_rescreen(screen, bracket)
        # Install the observer inside the mock telemetry boundary so it sees
        # the real evaluator's selected energy calls, including exclusions.
        with fx.adapter_projection(case):
            projected_energy = ww._reference_energy_evidence
            def evidence(path, **kwargs):
                self.assertNotEqual(Path(path).name, target)
                return projected_energy(path, **kwargs)
            with mock.patch.object(ww, "_reference_energy_evidence", side_effect=evidence):
                result = replay.replay_claim_sources(case.row, case.window.claim, archive=case.handle(),
                    roster=case.roster())
        self.assertIsNone(result.problem)
        self.assertEqual(result.reference_losses[target], "thermal.os_level_nonzero")

    def test_recompute_summary_status_strict_and_energy_losses(self):
        case = self.case()
        roster = case.roster()
        with fx.adapter_projection(case):
            sources = harvest.claim_neg8_sources(case.row, case.window.claim, roster=roster)
        self.assertNotIsInstance(sources, str)
        manifests = sources[0]
        target = next(run for run, slot in roster_references(roster).items() if slot == "start" and
                      (case.window.claim / run).is_dir())
        path = case.window.claim / target / "summary_metrics.json"
        raw = path.read_bytes()
        self.addCleanup(path.write_bytes, raw)
        original = fx.s0.sha(path)
        for mode, word in (("absent", "summary_unreadable"), ("failed", "status_not_succeeded"),
                           ("energy", "energy_unreadable"), ("strict", "strict_invalid")):
            with self.subTest(mode=mode):
                if mode == "absent":
                    path.unlink()
                elif mode == "failed":
                    summary = ww._read_json_object(path)
                    summary["status"] = "failed"
                    fx.s0.put(path, summary)
                elif mode == "energy":
                    # The writer's reader is exercised against a malformed
                    # stored summary on this actual synthetic bundle.
                    path.write_text('{"status":"succeeded"}')
                else:
                    path.write_bytes(raw)
                with fx.adapter_projection(case):
                    if mode == "strict":
                        actual = replay.neg8_reference_strict_invalid
                        def predicate(bundle, **kwargs):
                            if Path(bundle).name == target:
                                from joulewise.neg8_survivors import ReferenceStrictVerdict
                                return ReferenceStrictVerdict(True, ("synthetic strict problem",), False, True)
                            return actual(bundle, **kwargs)
                        with mock.patch.object(replay, "neg8_reference_strict_invalid", side_effect=predicate):
                            harvested, complete = replay.recompute_reference_losses(manifests, case.window.claim, roster, case.flags())
                    else:
                        harvested, complete = replay.recompute_reference_losses(manifests, case.window.claim, roster, case.flags())
                self.assertEqual(complete[target], word)
                if mode == "energy":
                    self.assertEqual(harvested[target], word)
                else:
                    self.assertNotIn(target, harvested)
                path.write_bytes(raw)
        self.assertEqual(fx.s0.sha(path), original)

    def test_loss_list_edit_rebound_and_flags_authentication(self):
        case = self.case()
        screen = case.read("derived/neg8-screen.json")
        # Preserve the absent spare's required matching absence records;
        # change a present reference to exercise the downstream comparison.
        target = next(run for run in roster_references(case.roster()) if run in case.row["bundle_ids"])
        screen["harvest_reference_losses"][target] = "member.timeout"
        case.write("derived/neg8-screen.json", screen)
        self.assertEqual(self.run_replay(case).problem, "sources_replay_losses_differ")
        case = self.case()
        path = case.archive / "derived/flags.jsonl"
        path.write_bytes(path.read_bytes() + b" \n")
        self.assertEqual(self.run_replay(case).problem, "archive_output_unauthenticated")

    def test_clean_bound_absent_and_endpoint_disagreement_refuse(self):
        case = self.case()
        allowance = case.read(ww.NEG8_HARVEST_ALLOWANCE_RECORD)
        allowance["clean_bound"] = None
        case.write(ww.NEG8_HARVEST_ALLOWANCE_RECORD, allowance)
        self.assertEqual(self.run_replay(case).problem, "clean_bound_unavailable")
        case = self.case()
        wrapper = case.read(ww.NEG8_HARVEST_SURVIVOR_BRACKET)
        first = next(iter(wrapper["bracket"]["claim_families"].values()))
        first["start_mean_j"] = "endpoint counterfactual"
        case.write(ww.NEG8_HARVEST_SURVIVOR_BRACKET, wrapper)
        allowance = case.read(ww.NEG8_HARVEST_ALLOWANCE_RECORD)
        allowance["survivor_bracket"]["sha256"] = fx.s0.sha(case.archive / ww.NEG8_HARVEST_SURVIVOR_BRACKET)
        case.write(ww.NEG8_HARVEST_ALLOWANCE_RECORD, allowance)
        self.assertEqual(self.run_replay(case).problem, "whole_window_verdict_conflict")

    def test_basis_fresh_hash_check_and_failed_evaluator(self):
        case = self.case()
        row = copy.deepcopy(case.row)
        row["evaluation_basis"]["sha256"] = "0" * 64
        self.assertEqual(self.run_replay(case, row).problem, "evaluation_basis_invalid")
        result = self.run_replay(case)
        self.assertIsNone(result.problem)
        basis = ww._validated_evaluation_basis(case.row, case.window.claim)
        target = next(iter(roster_references(case.roster())))
        check = replay._basis_reference_check(basis)
        self.assertIsNone(check(target, case.window.claim / target))
        self.assertEqual(check("not-in-basis", case.window.claim / target), "reference_not_in_verdict_basis")
        path = case.window.claim / target / "metadata.json"
        raw = path.read_bytes()
        self.addCleanup(path.write_bytes, raw)
        path.write_bytes(raw + b" ")
        self.assertEqual(check(target, case.window.claim / target), "reference_not_in_verdict_basis")
        path.write_bytes(raw)
        with mock.patch.object(ww, "_derived_neg8_decision", return_value=({"decision": "failed", "conditions": []}, None)):
            self.assertEqual(self.run_replay(case).problem, "sources_replay_screen_not_passed")

    def test_original_catalog_bytes_bound_to_archive_census(self):
        case = self.case()
        result = self.run_replay(case)
        self.assertIsNone(result.problem)
        archive = case.handle()
        with fx.adapter_projection(case):
            replay.replay_claim_sources(case.row, case.window.claim, archive=archive, roster=case.roster())
        census = {item.path for item in archive.census()}
        self.assertIn("derived/flags.jsonl", census)
        self.assertIn("sources/SHA256SUMS", census)
        self.assertTrue(any(path.endswith("campaign_log.jsonl") for path in census))
        self.assertTrue(any("campaign_manifests/" in path for path in census))
