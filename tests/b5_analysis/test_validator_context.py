"""S3 ruling conformance over cached synthetic writer/harvest windows."""
import copy
from dataclasses import FrozenInstanceError, replace
import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from joulewise import whole_window as ww
from tests.b5_analysis import fixtures_s3 as fx


class ValidatorContextTests(unittest.TestCase):
    def case(self, name="BETA_STD"):
        case = fx.Case(name)
        self.addCleanup(case.close)
        return case

    def validate(self, case, *, context=True, session=None):
        if session is None:
            session = case.session()
        if not context:
            session._archive_context = None  # fresh no-context test double
        with fx.adapter_projection(case):
            return ww.validate_whole_window_verdict_row(case.row, case.window.claim,
                set(case.row["bundle_ids"]), consumption_session=session)

    def test_standard_underived_row_admitted(self):
        case = self.case()
        families = case.row["idle_admission_core"]["neg8_bracket"]["claim_families"]
        self.assertTrue(all(record["drift_allowance_j"] is None for record in families.values()))
        result = self.validate(case)
        self.assertEqual(result.reasons, ())
        self.assertTrue(result.admitted)
        self.assertEqual(result.allowance_source, "survivor_rescreen")

    def test_context_allowances_use_same_archive_and_no_context_is_absent(self):
        case = self.case()
        log = case.window.claim / "campaign_log.jsonl"
        original = log.read_bytes()
        self.addCleanup(log.write_bytes, original)
        rows = [json.loads(line) for line in original.splitlines() if line.strip()]
        rows = [case.row if row.get("record_type") == "idle_admission_whole_window_verdict" else row for row in rows]
        log.write_text("".join(json.dumps(row) + "\n" for row in rows))
        session = case.session()
        with fx.adapter_projection(case):
            result = ww.whole_window_drift_allowances(case.window.claim, set(case.row["bundle_ids"]),
                evaluation_basis_sha256=case.row["evaluation_basis"]["sha256"], consumption_session=session)
            self.assertEqual(result.status, "allowances")
            without = case.session()
            without._archive_context = None
            self.assertEqual(ww.whole_window_drift_allowances(case.window.claim, set(case.row["bundle_ids"]),
                evaluation_basis_sha256=case.row["evaluation_basis"]["sha256"], consumption_session=without).status, "absent")
            self.assertEqual(ww.whole_window_drift_allowances(case.window.claim, set(case.row["bundle_ids"]),
                evaluation_basis_sha256=case.row["evaluation_basis"]["sha256"], consumption_session=session,
                neg8_harvest_archive=case.archive / "another-window").status, "absent")
        self.assertIn("archive_context_changed", session.refusal_reasons)

    def test_no_context_stored_failure_refuses(self):
        result = self.validate(self.case(), context=False)
        self.assertFalse(result.admitted)
        self.assertIn("whole_window_neg8_verdict_failed", result.reasons)
        self.assertFalse(hasattr(result, "detail"))

    def test_context_nested_immutable_and_copied(self):
        source = {"nested": {"items": [1, 2]}}
        ctx = ww.ArchiveContext(Path("/private/tmp"), window_bracket=source,
            roster_references={"ref": "start"}, removed_bundle_ids={"member"},
            catalog_manifests=(({"path": "manifest"}, {"members": [{"bundle_ids": ["member"]}]}),))
        source["nested"]["items"].append(3)
        self.assertEqual(ctx.window_bracket["nested"]["items"], (1, 2))
        with self.assertRaises(TypeError):
            ctx.window_bracket["nested"]["changed"] = True
        with self.assertRaises(TypeError):
            ctx.catalog_manifests[0][1]["members"][0]["bundle_ids"][0] = "changed"
        with self.assertRaises(FrozenInstanceError):
            ctx.governed_e3 = True

    def test_session_refuses_second_context_before_cached_admit(self):
        case = self.case()
        session = case.session()
        self.assertTrue(self.validate(case, session=session).admitted)
        other = replace(case.context, removed_bundle_ids=frozenset({"different"}))
        with fx.adapter_projection(case):
            result = ww.validate_whole_window_verdict_row(case.row, case.window.claim,
                set(case.row["bundle_ids"]), consumption_session=session, archive_context=other)
        self.assertFalse(result.admitted)
        self.assertEqual(result.reasons, ("archive_context_changed",))
        self.assertFalse(session._row_validation_results)
        self.assertFalse(self.validate(case, session=session).admitted)

    def test_session_assignment_refuses_changed_context(self):
        case = self.case()
        session = case.session()
        with self.assertRaisesRegex(ValueError, "archive_context_changed"):
            session.archive_context = replace(case.context, governed_e3=False)
        self.assertIn("archive_context_changed", session.refusal_reasons)

    def test_status_words(self):
        for status in ("passed", "failed", "flagged", "invalid", "unknown", None, {"word": "failed"}):
            with self.subTest(status=status):
                case = self.case()
                case.row["status"] = status
                case.bind_row()
                result = self.validate(case)
                self.assertEqual(result.admitted, status in ("passed", "failed"), result.reasons)
                if status not in ("passed", "failed"):
                    self.assertIn("whole_window_neg8_verdict_failed", result.reasons)

    def test_removed_science_real_rederivation_and_kept_counterfactual(self):
        case = self.case()
        bundle = "s0-mock-r06"
        case.admission_failure(bundle)
        case.remove_science_member(bundle)
        result = self.validate(case)
        self.assertTrue(result.admitted, result.reasons)
        self.assertIn(f"removed_member_rederivation:environment_admission_failed:{bundle}", result.detail)
        case.context = replace(case.context, removed_bundle_ids=frozenset())
        result = self.validate(case)
        self.assertFalse(result.admitted)
        self.assertIn(f"member_code_on_kept_unit:{bundle}", result.reasons)

    def test_included_reference_fault_in_survivors_refuses_lost_answers(self):
        case = self.case()
        bundle = "b5t-neg8-start-1"
        case.admission_failure(bundle)
        result = self.validate(case)
        self.assertFalse(result.admitted)
        self.assertIn(f"reference_in_screen_named_by_verdict:environment_admission_failed:{bundle}", result.reasons)
        case.lose_reference(bundle)
        result = self.validate(case)
        self.assertTrue(result.admitted, result.reasons)
        self.assertIn(f"removed_member_rederivation:environment_admission_failed:{bundle}", result.detail)

    def test_member_condition_without_named_member(self):
        case = self.case()
        code = "thermal_pressure_elevated_in_window"
        case.row["idle_admission_core"]["conditions"].append(code)
        case.bind_row()
        result = self.validate(case)
        self.assertIn(f"member_condition_unnamed:{code}", result.reasons)

    def test_excluded_bundle_member_condition_removed_only(self):
        case = self.case()
        bundle = "omitted-science"
        case.row["excluded_bundles"].append({"bundle_id": bundle, "reason": "strict_invalid"})
        case.row["idle_admission_core"]["conditions"].append("whole_window_bundle_invalid")
        case.context = replace(case.context, removed_bundle_ids=frozenset({bundle}))
        case.bind_row()
        self.assertTrue(self.validate(case).admitted)
        case.context = replace(case.context, removed_bundle_ids=frozenset())
        self.assertIn(f"member_code_on_kept_unit:{bundle}", self.validate(case).reasons)

    def test_unknown_and_ambiguous_conditions_never_answered(self):
        for code in ("calibration_ledger_baseline_missing", "whole_window_campaign_membership_ambiguous", "campaign_occurrence_ambiguous", "other_fault"):
            with self.subTest(code=code):
                case = self.case()
                case.row["idle_admission_core"]["conditions"].append(code)
                case.bind_row()
                result = self.validate(case)
                self.assertIn("whole_window_verdict_provenance_invalid", result.reasons)
                self.assertNotIn(code, result.answered_conditions)

    def test_condition_list_and_basis_malformed_refuse(self):
        for label, value in (("conditions", None), ("conditions", {}), ("conditions", [{"unknown": "condition"}]),
                             ("basis", "0" * 64), ("basis", None)):
            with self.subTest(label=label, value=value):
                case = self.case()
                if label == "conditions":
                    case.row["idle_admission_core"]["conditions"] = value
                else:
                    case.row["evaluation_basis"]["sha256"] = value
                case.bind_row()
                result = self.validate(case)
                self.assertFalse(result.admitted)
                self.assertIn("whole_window_verdict_provenance_invalid", result.reasons)

    def test_missing_failed_and_changed_window_bracket(self):
        case = self.case()
        case.context = replace(case.context, window_bracket=None)
        self.assertIn("window_bracket_not_passed", self.validate(case).reasons)
        bracket = ww._archive_thaw(fx.context(case.window).window_bracket)
        bracket["status"] = "failed"
        case.context = replace(case.context, window_bracket=bracket)
        self.assertIn("window_bracket_not_passed", self.validate(case).reasons)
        bracket["status"] = "passed"
        bracket["b_fiducial_s"] += 0.001
        case.context = replace(case.context, window_bracket=bracket)
        self.assertIn("window_bracket_differs_from_harvest", self.validate(case).reasons)

    def test_window_bracket_exact_comparison_fields_and_digest(self):
        case = self.case()
        original = ww._archive_thaw(case.context.window_bracket)
        for field in ww._WINDOW_BRACKET_FIELDS:
            with self.subTest(field=field):
                bracket = copy.deepcopy(original)
                bracket[field] = "failed" if field == "status" else {"s3_counterfactual": "changed"}
                expected = "window_bracket_not_passed" if field == "status" else "window_bracket_differs_from_harvest"
                self.assertEqual(ww._window_bracket_problem(replace(case.context, window_bracket=bracket)), expected)
        for field in ww._WINDOW_ACCEPTANCE_FIELDS:
            with self.subTest(acceptance=field):
                bracket = copy.deepcopy(original)
                bracket["acceptance"][field] = {"s3_counterfactual": "changed"}
                self.assertEqual(ww._window_bracket_problem(replace(case.context, window_bracket=bracket)),
                    "window_bracket_differs_from_harvest")
        bracket = copy.deepcopy(original)
        bracket.update(window_start_s="different", window_end_s="different", members=["different"])
        self.assertIsNone(ww._window_bracket_problem(replace(case.context, window_bracket=bracket)))
        wrapper = case.read("withheld/bracket-evaluation.json")
        wrapper["assessment"]["b_fiducial_s"] += 0.001
        case.write("withheld/bracket-evaluation.json", wrapper, authenticate=False)
        self.assertEqual(ww._window_bracket_problem(case.context), "window_bracket_differs_from_harvest")

    def test_ungoverned_stale_condition_never_answered(self):
        case = self.case()
        case.context = replace(case.context, governed_e3=False)
        result = self.validate(case)
        self.assertFalse(result.admitted)
        self.assertNotIn("calibration_acceptance_bound_stale", result.answered_conditions)

    def test_adapter_result_disclosed_record_mismatch_and_absence(self):
        case = self.case()
        result = self.validate(case)
        decision = case.row["idle_admission_core"]["adapter_wattage_continuity"]["decision"]
        self.assertNotEqual(decision, "stable")
        self.assertTrue(result.admitted)
        self.assertIn(f"adapter_continuity_decision:{decision}", result.detail)
        self.assertIn("adapter_continuity_failed", self.validate(case, context=False).reasons)
        case.row["idle_admission_core"]["adapter_wattage_continuity"]["observation_count"] += 1
        case.bind_row()
        self.assertIn("adapter_continuity_record_mismatch", self.validate(case).reasons)
        self.assertIn("adapter_continuity_failed", self.validate(case, context=False).reasons)
        case.row["idle_admission_core"]["adapter_wattage_continuity"] = None
        case.bind_row()
        self.assertIn("adapter_continuity_evidence_missing", self.validate(case).reasons)
        self.assertIn("adapter_continuity_evidence_missing", self.validate(case, context=False).reasons)

    def test_adapter_no_context_three_cases_match_head(self):
        case = self.case()
        source = fx.SCRATCH / "base_whole_window.py"
        source.write_bytes(subprocess.check_output(["git", "show", "HEAD:joulewise/whole_window.py"], cwd=fx.ROOT))
        spec = importlib.util.spec_from_file_location("s3_adapter_base_whole_window", source)
        base = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = base
        spec.loader.exec_module(base)
        continuity = copy.deepcopy(case.row["idle_admission_core"]["adapter_wattage_continuity"])
        for label in ("reproduced_nonstable", "record_mismatch", "record_absent"):
            with self.subTest(label=label):
                value = copy.deepcopy(continuity)
                if label == "record_mismatch":
                    value["observation_count"] += 1
                elif label == "record_absent":
                    value = None
                case.row["idle_admission_core"]["adapter_wattage_continuity"] = value
                case.bind_row()
                with fx.adapter_projection(case):
                    # Adapter telemetry and memoized real environment checks
                    # are shared seams; both row/core validators run themselves.
                    with mock.patch.object(base, "_load_idle_records", ww._load_idle_records), \
                            mock.patch.object(base, "current_environment_refusals", ww.current_environment_refusals), \
                            mock.patch.object(base, "_derived_neg8_decision", ww._derived_neg8_decision):
                        def probe(module):
                            session = case.session()
                            session._archive_context = None
                            return module._validate_row_uncached(case.row, case.window.claim,
                                set(case.row["bundle_ids"]), consumption_session=session)
                        self.assertEqual(probe(ww), probe(base))

    def test_one_stored_endpoint_changed_refuses(self):
        case = self.case()
        case.row["idle_admission_core"]["neg8_bracket"]["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]["start"]["mean_j"] += 1
        case.bind_row()
        self.assertIn("whole_window_verdict_conflict", self.validate(case).reasons)

    def test_stored_shape_policy_and_artifact_still_authenticate(self):
        for change in ("schema", "policy", "shape", "artifact"):
            with self.subTest(change=change):
                case = self.case()
                bracket = case.row["idle_admission_core"]["neg8_bracket"]
                if change == "schema":
                    bracket["schema_version"] = "wrong"
                elif change == "policy":
                    bracket["policy"] = {}
                elif change == "shape":
                    del bracket["drift_bound_artifact"]
                else:
                    bracket["drift_bound_artifact"] = {"bad": "artifact"}
                case.bind_row()
                self.assertIn("whole_window_verdict_provenance_invalid", self.validate(case).reasons)

    def test_custody_triangle_not_waived_for_removed_member(self):
        case = self.case()
        bundle = "s0-mock-r06"
        case.context = replace(case.context, removed_bundle_ids=frozenset({bundle}))
        actual = ww._custody_strict_invalid
        with mock.patch.object(ww, "_custody_strict_invalid", side_effect=lambda path, *args:
                              Path(path).name == bundle or actual(path, *args)):
            self.assertIn("bundle_strict_invalid", self.validate(case).reasons)

    def test_kept_cpu_comparison_independent(self):
        case = self.case()
        case.row["idle_admission_core"]["members"][0]["cpu_admission"]["sample_count"] += 1
        case.bind_row()
        for context in (True, False):
            self.assertIn("cpu_admission_core_failed", self.validate(case, context=context).reasons)

    def test_source_manifest_bytes_and_coverage_independent(self):
        case = self.case()
        descriptor = case.row["row_provenance"]["source_campaign_manifests"][0]
        descriptor["sha256"] = "0" * 64
        case.bind_row()
        self.assertIn("whole_window_verdict_provenance_invalid", self.validate(case).reasons)
        with fx.adapter_projection(case):
            result = ww.validate_whole_window_verdict_row(case.row, case.window.claim, {"missing-member"},
                archive_context=case.context)
        self.assertIn("whole_window_verdict_coverage_incomplete", result.reasons)

    def test_allowance_authentication_refusals(self):
        for change, problem in (("row", "allowance_record_names_another_row"),
                ("wrapper", "survivor_bracket_unauthenticated"), ("arithmetic", "survivor_arithmetic_differs"),
                ("bound", "clean_bound_unauthenticated"), ("none", "screen_not_passed"),
                ("decision", "survivor_bracket_not_passed")):
            with self.subTest(change=change):
                case = self.case()
                record = case.read(ww.NEG8_HARVEST_ALLOWANCE_RECORD)
                if change == "row":
                    record["verdict"]["row_sha256"] = "0" * 64
                    case.write(ww.NEG8_HARVEST_ALLOWANCE_RECORD, record)
                elif change == "bound":
                    (case.archive / ww.NEG8_HARVEST_CLEAN_BOUND).unlink()
                elif change == "none":
                    record["source"] = "none"
                    case.write(ww.NEG8_HARVEST_ALLOWANCE_RECORD, record)
                else:
                    wrapper = case.read(ww.NEG8_HARVEST_SURVIVOR_BRACKET)
                    if change == "decision":
                        wrapper["bracket"]["decision"] = "failed"
                    else:
                        wrapper["bracket"]["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]["drift_allowance_j"] += 1
                    case.write(ww.NEG8_HARVEST_SURVIVOR_BRACKET, wrapper, authenticate=change != "wrapper")
                    if change != "wrapper":
                        record["survivor_bracket"]["sha256"] = fx.s0.sha(case.archive / ww.NEG8_HARVEST_SURVIVOR_BRACKET)
                        case.write(ww.NEG8_HARVEST_ALLOWANCE_RECORD, record)
                self.assertEqual(ww.harvest_neg8_allowance_bracket(case.archive, case.row)[1], problem)
                result = self.validate(case)
                self.assertIn("whole_window_neg8_verdict_failed", result.reasons)
                self.assertIn(problem, result.detail)

    def test_stored_source_absent_and_failed_no_fallback(self):
        for absent in (True, False):
            case = self.case()
            record = case.read(ww.NEG8_HARVEST_ALLOWANCE_RECORD)
            record["source"] = "stored_verdict"
            if absent:
                case.row["idle_admission_core"]["neg8_bracket"] = None
            case.write(ww.NEG8_HARVEST_ALLOWANCE_RECORD, record)
            case.bind_row()
            if absent:
                self.assertEqual(ww.harvest_neg8_allowance_bracket(case.archive, case.row)[1], "stored_bracket_absent")
            self.assertIn("whole_window_neg8_verdict_failed", self.validate(case).reasons)

    def test_two_end_references_lost_record_source_none_refuses(self):
        case = self.case()
        screen = case.read("derived/neg8-screen.json")
        screen["harvest_reference_losses"] = {"b5t-neg8-end-2": "member.timeout", "b5t-neg8-end-3": "member.timeout"}
        screen["rescreen"].update(decision="failed", conditions=["neg8_bracket_reference_invalid"])
        case.write("derived/neg8-screen.json", screen)
        record = case.read(ww.NEG8_HARVEST_ALLOWANCE_RECORD)
        record["source"] = "none"
        case.write(ww.NEG8_HARVEST_ALLOWANCE_RECORD, record)
        case.context = replace(case.context, survivor_bundle_ids=case.context.survivor_bundle_ids - {"b5t-neg8-end-2", "b5t-neg8-end-3"})
        result = self.validate(case)
        self.assertFalse(result.admitted)
        self.assertIn("screen_not_passed", result.detail)

    def test_screen_structure_and_bound_guards(self):
        for change in ("loss_id", "counts", "freshness"):
            case = self.case()
            if change == "loss_id":
                screen = case.read("derived/neg8-screen.json")
                screen["harvest_reference_losses"]["not-a-roster-reference"] = "strict_invalid"
                case.write("derived/neg8-screen.json", screen)
            elif change == "counts":
                case.context = replace(case.context, survivor_bundle_ids=frozenset())
            else:
                wrapper = case.read(ww.NEG8_HARVEST_SURVIVOR_BRACKET)
                wrapper["bracket"]["bound_freshness"].pop("decision")
                case.write(ww.NEG8_HARVEST_SURVIVOR_BRACKET, wrapper)
                record = case.read(ww.NEG8_HARVEST_ALLOWANCE_RECORD)
                record["survivor_bracket"]["sha256"] = fx.s0.sha(case.archive / ww.NEG8_HARVEST_SURVIVOR_BRACKET)
                case.write(ww.NEG8_HARVEST_ALLOWANCE_RECORD, record)
            self.assertIn("whole_window_neg8_verdict_failed", self.validate(case).reasons)

    def test_core_empty_sources_never_silent(self):
        case = self.case()
        reasons = ww._current_core_rederivation_reasons(core=case.row["idle_admission_core"],
            bundle_ids=case.row["bundle_ids"], manifests=[], runs_root=case.window.claim,
            policy_sha256=case.row["campaign_policy"]["sha256"], archive_context=case.context)
        self.assertEqual(reasons, {"core_rederivation_sources_empty"})

    def test_session_operative_bound_is_context_bracket(self):
        case = self.case()
        session = case.session()
        session._prepared = False
        with mock.patch.object(ww, "_current_strict_summary", return_value=False), \
                mock.patch.object(ww, "capture_pipeline_refusal", return_value=None):
            session._prepare(bundle_paths={bundle: case.window.claim / bundle for bundle in case.row["bundle_ids"]},
                policy=ww.CampaignPolicy.from_mapping(ww._registered_policy(case.row["campaign_policy"]["sha256"])))
        self.assertTrue(session.ready, session.refusal_reasons)
        self.assertEqual(session.operative_fiducial_bound_s, case.context.window_bracket["b_fiducial_s"])
        self.assertEqual(session.consumption_semantics_id, ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID)

    def test_no_context_blocks_1_to_3_byte_identical_to_head(self):
        from dataclasses import asdict
        from joulewise.calibration_ledger import CalibrationLedgerSnapshot, LEDGER_SCHEMA
        from tests import test_neg8_survivors as support
        scratch = fx.ROOT / ".scratch-s3"
        source = scratch / "base_whole_window.py"
        source.write_bytes(subprocess.check_output(["git", "show", "HEAD:joulewise/whole_window.py"], cwd=fx.ROOT))
        spec = importlib.util.spec_from_file_location("s3_base_whole_window", source)
        base = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = base
        spec.loader.exec_module(base)
        support.VerdictWriterSurvivorTests.setUpClass()
        helper = support.VerdictWriterSurvivorTests()
        comparisons = []
        with tempfile.TemporaryDirectory(prefix="s3-neutrality-") as temporary:
            for block in (1, 2, 3):
                root = Path(temporary) / "runs/v5" / f"block-{block}"
                root.mkdir(parents=True)
                helper.root = root
                members = helper.references((8.0,), (), (8.0,))
                ids = {member.bundle_id for member in members}
                # Use the same production policy the synthetic writer harness
                # registers; direct legacy summary parsing remains real.
                from tests import test_harvest_b5_window as hb
                policy_sha = hb.sha(hb.ROOT / hb.POLICY)
                manifests = [{"execution": "invoked", "run_id": member.bundle_id, "bundle_ids": [member.bundle_id],
                    "role": member.declared_role, "sentinel_position": member.sentinel_position} for member in members]
                for member in members:
                    fx.s0.put(root / member.bundle_id / "summary_metrics.json", {**member.summary, "status": "succeeded"})
                manifest_path = root / "campaign_manifests/source.json"
                fx.s0.put(manifest_path, {"schema_version": "joulewise.campaign_provenance.v1", "members": manifests,
                    "campaign_policy": {"sha256": policy_sha}})
                policy = ww._registered_bracket_policy(policy_sha)
                endpoint = {"point_j": 8.0, "lower_j": 8.0, "upper_j": 8.0}
                bracket = ww.evaluate_neg8_bracket(endpoint, endpoint, ww.Neg8BracketPolicy.from_mapping(policy))
                row = {"record_type": "idle_admission_whole_window_verdict", "schema_version": ww.WHOLE_WINDOW_SCHEMA,
                    "status": "passed", "bundle_ids": sorted(ids), "campaign_policy": {"sha256": policy_sha},
                    "idle_admission_core": {"schema_version": ww.IDLE_ADMISSION_CORE_SCHEMA, "policy_sha256": policy_sha,
                        "conditions": [], "members": [{"bundle_id": bundle, "cpu_admission": {"decision": "admitted"}} for bundle in sorted(ids)],
                        "adapter_wattage_continuity": {"schema_version": ww.ADAPTER_CONTINUITY_SCHEMA, "decision": "stable"},
                        "neg8_bracket": bracket}}
                row["row_provenance"] = ww.build_row_provenance(policy_sha256=policy_sha, bundle_ids=sorted(ids),
                    source_manifests=[{"path": "campaign_manifests/source.json", "sha256": fx.s0.sha(manifest_path)}])
                (root / "campaign_log.jsonl").write_text(json.dumps(row) + "\n")
                def probe(module):
                    session = module.AuthenticatedConsumptionSession(root, ids,
                        calibration_ledger_snapshot=CalibrationLedgerSnapshot(LEDGER_SCHEMA, root / "unused-synthetic-ledger", 0,
                            "0" * 64, (), (), ()))
                    session._prepared = True
                    reasons = module._validate_row(row, root, ids, consumption_session=session)
                    allowance = module.whole_window_drift_allowances(root, ids, consumption_session=session)
                    return json.dumps({"reasons": reasons, "allowance": asdict(allowance)}, sort_keys=True, separators=(",", ":"))
                old, current = probe(base), probe(ww)
                self.assertEqual(current, old)
                self.assertEqual(json.loads(current)["reasons"], [True, []])
                comparisons.append({"block": block, "base": old, "current": current, "equal": True})
        (scratch / "neutrality.json").write_text(json.dumps(comparisons, indent=2) + "\n")


class CatalogContextTests(unittest.TestCase):
    validate = ValidatorContextTests.validate
    def case(self, name="BETA_SOURCES_RECOVERED"):
        case = fx.Case(name)
        self.addCleanup(case.close)
        records = ww.load_authenticated_campaign_catalog(case.window.claim, case.window.claim / "campaign_log.jsonl")
        sources = tuple(({"path": "campaign_manifests/" + record.path.name,
            "sha256": hashlib.sha256(record.raw_bytes).hexdigest()}, record.value) for record in records)
        case.context = replace(case.context, sources_replay=lambda row, root: None, catalog_manifests=sources)
        return case

    def test_catalog_recovery_feeds_both_rederivations(self):
        case = self.case()
        actual = ww._derived_neg8_decision
        with mock.patch.object(ww, "_derived_neg8_decision", wraps=actual) as derive:
            result = self.validate(case)
        self.assertTrue(result.admitted, result.reasons)
        self.assertIn("whole_window_campaign_membership_unresolved", result.answered_conditions)
        call = derive.call_args
        self.assertTrue(call.args[0])
        self.assertEqual(call.kwargs["unreadable_energy"], "lost")
        self.assertTrue(call.kwargs["require_replicated_endpoints"])
        self.assertEqual(call.kwargs["required_reference_ids"], frozenset(case.context.roster_references))
        self.assertEqual(call.kwargs["exclude_bundle_ids"], case.read("derived/neg8-screen.json")["harvest_reference_losses"])
        self.assertIsNotNone(call.kwargs["surviving_reference_check"])

    def test_catalog_empty_manifest_list_refuses(self):
        case = self.case()
        case.context = replace(case.context, catalog_manifests=())
        result = self.validate(case)
        self.assertFalse(result.admitted)
        self.assertIn("core_rederivation_sources_empty", result.reasons)

    def test_catalog_replay_problem_and_preconditions(self):
        for change in ("missing_callable", "problem", "evaluated", "decision", "source", "nonempty_descriptors"):
            with self.subTest(change=change):
                case = self.case()
                spy = mock.Mock(return_value="reference_not_in_roster" if change == "problem" else None)
                case.context = replace(case.context, sources_replay=None if change == "missing_callable" else spy)
                if change in {"evaluated", "decision", "source"}:
                    screen = case.read("derived/neg8-screen.json")
                    if change == "evaluated":
                        screen["rescreen"]["evaluated"] = False
                    elif change == "decision":
                        screen["rescreen"]["decision"] = "failed"
                    else:
                        screen["rescreen"]["reference_source"]["source"] = "claim_campaign_manifests_unauthenticated"
                    case.write("derived/neg8-screen.json", screen)
                elif change == "nonempty_descriptors":
                    case.row["row_provenance"]["source_campaign_manifests"] = [ww._archive_thaw(case.context.catalog_manifests[0][0])]
                    case.bind_row()
                result = self.validate(case)
                self.assertFalse(result.admitted)
                self.assertIn("whole_window_verdict_provenance_invalid", result.reasons)
                self.assertNotIn("whole_window_campaign_membership_unresolved", result.answered_conditions)
                if change in {"evaluated", "decision", "source", "nonempty_descriptors"}:
                    spy.assert_not_called()
                elif change == "problem":
                    self.assertIn("reference_not_in_roster", result.detail)

    def test_catalog_endpoint_disagreement_refuses(self):
        case = self.case()
        actual = ww._derived_neg8_decision
        def derive(*args, **kwargs):
            bracket, problem = actual(*args, **kwargs)
            if isinstance(bracket, dict):
                bracket["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]["start"]["mean_j"] += 1
            return bracket, problem
        with mock.patch.object(ww, "_derived_neg8_decision", side_effect=derive):
            self.assertIn("whole_window_verdict_conflict", self.validate(case).reasons)


if __name__ == "__main__":
    unittest.main()
