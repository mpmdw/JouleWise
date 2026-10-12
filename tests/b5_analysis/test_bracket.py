"""L9 S2 rule probes, entirely synthetic; fixture builds are module-cached."""
import inspect
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from joulewise import calibration_bracketing as calibration
from joulewise.b5_analysis import bracket as br
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis import fixtures_s2 as fx

_WINDOWS = {}


def windows():
    for name in ("GAMMA_STD", "ALPHA_STD", "BETA_STD"):
        if name not in _WINDOWS:
            _WINDOWS[name] = fx.build_named(name)
    return _WINDOWS


class BracketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.windows = windows()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s2-test-")
        self.addCleanup(self.tmp.cleanup)
        self.adapter = fx.capture_adapter()
        self.adapter.__enter__()
        self.addCleanup(self.adapter.__exit__, None, None, None)

    def cloned(self, name="GAMMA_STD"):
        return fx.fork(self.windows[name], Path(self.tmp.name) / "clone")

    def evaluate(self, built):
        return br.evaluate_window_bracket(fx.handle(built), repo_root=fx.s0.ROOT)

    def test_gamma_equals_harvest_and_records_only_trigger(self):
        built = self.windows["GAMMA_STD"]
        handle = fx.handle(built)
        result = br.evaluate_window_bracket(handle, repo_root=fx.s0.ROOT)
        self.assertEqual((result.trigger_scope, result.compared_with_harvest), ("window_evidence", "equal"))
        self.assertEqual(result.evaluation["status"], "passed")
        prospective = result.evaluation["acceptance"]["prospective_rederivation"]
        self.assertIn("new_systematic_failure_challenges_preflight_screen", prospective["recorded_only_triggers"])
        self.assertEqual(result.sources_sha256sums_sha256, fx.s0.sha(built.archive / "sources/SHA256SUMS"))
        self.assertEqual(result.ledger_copy_sha256, fx.s0.sha(built.archive / br.LEDGER_COPY))
        census = {row.path: row for row in handle.census()}
        self.assertEqual(census["sources/SHA256SUMS"].sha256, result.sources_sha256sums_sha256)
        self.assertEqual(census["sources/SHA256SUMS"].check, "input_census")

    def test_alpha_sealed_is_fresh_without_harvest_digest(self):
        built = self.windows["ALPHA_STD"]
        self.assertNotIn("withheld/bracket-evaluation.json", fx.handle(built).record["outputs"])
        result = self.evaluate(built)
        self.assertEqual((result.trigger_scope, result.compared_with_harvest), ("sealed", "no_harvest_digest"))
        self.assertEqual(result.evaluation["acceptance"]["freshness"]["status"], "fresh")

    def test_source_inventory_read_once(self):
        built = self.windows["GAMMA_STD"]
        manifest = built.archive / "sources/SHA256SUMS"
        original = Path.read_bytes
        reads = []
        def read(path):
            if path == manifest:
                reads.append(path)
            return original(path)
        with mock.patch.object(Path, "read_bytes", read):
            self.evaluate(built)
        self.assertEqual(len(reads), 1)

    def test_each_listed_assessment_field_must_match(self):
        built = self.cloned()
        target = built.archive / "withheld/bracket-evaluation.json"
        original = json.loads(target.read_bytes())
        # Typed from Erratum 3 item 10(ii), independently of the implementation.
        for key in ("status", "pre", "post", "endpoint_max_b_fiducial_s", "drift_s",
                    "calibration_drift_allowance_s", "b_fiducial_s", "bracket_binding"):
            with self.subTest(key=key):
                row = json.loads(json.dumps(original))
                row["assessment"][key] = "counterfactual"
                fx.s0.put(target, row)
                fx.refresh(built)
                with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_differs_from_harvest$"):
                    self.evaluate(built)
        for key in ("freshness", "preflight", "drift", "allowance", "prospective_rederivation"):
            with self.subTest(key="acceptance." + key):
                row = json.loads(json.dumps(original))
                row["assessment"]["acceptance"][key] = "counterfactual"
                fx.s0.put(target, row)
                fx.refresh(built)
                with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_differs_from_harvest$"):
                    self.evaluate(built)
        row = json.loads(json.dumps(original))
        row["reasons"] = ["counterfactual"]
        fx.s0.put(target, row)
        fx.refresh(built)
        with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_differs_from_harvest$"):
            self.evaluate(built)

    def test_members_and_window_times_are_not_comparison_fields(self):
        built = self.cloned()
        target = built.archive / "withheld/bracket-evaluation.json"
        row = json.loads(target.read_bytes())
        row["members"] = 999
        row["assessment"].update(members=999, window_start_s=-999, window_end_s=999)
        fx.s0.put(target, row)
        fx.refresh(built)
        self.assertEqual(self.evaluate(built).compared_with_harvest, "equal")

    def test_edited_harvest_without_updated_output_digest_refuses(self):
        built = self.cloned()
        target = built.archive / "withheld/bracket-evaluation.json"
        with target.open("ab") as output:
            output.write(b" ")
        with self.assertRaisesRegex(AnalysisRefusal, "^archive_output_unauthenticated$"):
            self.evaluate(built)

    def test_governed_sealed_scope_is_not_passed(self):
        actual = calibration.evaluate_calibration_bracket
        def sealed(*args, **kwargs):
            kwargs["trigger_scope"] = "sealed"
            return actual(*args, **kwargs)
        with mock.patch.object(calibration, "evaluate_calibration_bracket", side_effect=sealed):
            with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_not_passed$"):
                self.evaluate(self.windows["GAMMA_STD"])

    def test_appended_three_entries_cut_at_terminal_without_changing_evaluation(self):
        built = self.cloned()
        original = self.evaluate(built)
        path = built.archive / br.LEDGER_COPY
        raw = path.read_bytes()
        last = json.loads(raw.splitlines()[-1])
        # The tail is deliberately not part of this window's decision chain.
        appended = b"".join(json.dumps({"sequence": last["sequence"] + n, "receipt_digest": "a" * 64}).encode() + b"\n"
                            for n in (1, 2, 3))
        path.write_bytes(raw + appended)
        fx.refresh(built)
        pin = json.loads((built.archive / br.TERMINAL_PIN).read_bytes())
        self.assertEqual(br.ledger_prefix(path.read_bytes(), pin), raw)
        changed = self.evaluate(built)
        self.assertEqual(changed.evaluation, original.evaluation)
        self.assertNotEqual(changed.ledger_copy_sha256, original.ledger_copy_sha256)

    def test_absent_terminal_sequence_refuses(self):
        built = self.windows["GAMMA_STD"]
        raw = (built.archive / br.LEDGER_COPY).read_bytes()
        pin = json.loads((built.archive / br.TERMINAL_PIN).read_bytes())
        pin["sequence"] += 100
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_prefix_not_at_terminal_pin$"):
            br.ledger_prefix(raw, pin)

    def test_terminal_head_mismatch_refuses(self):
        built = self.windows["GAMMA_STD"]
        raw = (built.archive / br.LEDGER_COPY).read_bytes()
        pin = json.loads((built.archive / br.TERMINAL_PIN).read_bytes())
        pin["head_digest"] = "a" * 64
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_prefix_not_at_terminal_pin$"):
            br.ledger_prefix(raw, pin)

    def test_chain_change_below_terminal_refuses(self):
        built = self.windows["GAMMA_STD"]
        raw = (built.archive / br.LEDGER_COPY).read_bytes()
        pin = json.loads((built.archive / br.TERMINAL_PIN).read_bytes())
        raw = raw.replace(b'"predecessor_digest":"', b'"predecessor_digest":"a', 1)
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_prefix_not_at_terminal_pin$"):
            br.ledger_prefix(raw, pin)

    def test_ledger_copy_digest_mismatch(self):
        built = self.cloned()
        with (built.archive / br.LEDGER_COPY).open("ab") as output:
            output.write(b" ")
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copy_digest_mismatch$"):
            self.evaluate(built)

    def test_missing_ledger_manifest_line_refuses(self):
        built = self.cloned()
        path = built.archive / "sources/SHA256SUMS"
        path.write_text("".join(line for line in path.read_text().splitlines(keepends=True)
                                if not line.endswith("  ledger/calibration_observation_ledger.jsonl\n")))
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copy_digest_mismatch$"):
            self.evaluate(built)

    def test_live_ledger_one_byte_changed_mid_file_refuses(self):
        built = self.windows["GAMMA_STD"]
        raw = (built.archive / br.LEDGER_COPY).read_bytes()
        path = Path(self.tmp.name) / "live.jsonl"
        path.write_bytes(raw + b"synthetic extension\n")
        br.require_ledger_copies_are_prefixes([fx.handle(built)], path)
        raw = bytearray(path.read_bytes())
        raw[len(raw) // 2] ^= 1
        path.write_bytes(raw)
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copy_not_prefix_of_live$"):
            br.require_ledger_copies_are_prefixes([fx.handle(built)], path)

    def test_archived_copy_changed_mid_file_with_digest_rebound_refuses(self):
        built = self.cloned()
        path = built.archive / br.LEDGER_COPY
        raw = path.read_bytes()
        live = Path(self.tmp.name) / "live.jsonl"
        live.write_bytes(raw)
        changed = bytearray(raw)
        changed[len(changed) // 2] ^= 1
        path.write_bytes(changed)
        fx.refresh(built)
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copy_not_prefix_of_live$"):
            br.require_ledger_copies_are_prefixes([fx.handle(built)], live)

    def test_release_checks_whole_archived_copy_not_only_terminal_cut(self):
        built = self.cloned()
        path = built.archive / br.LEDGER_COPY
        raw = path.read_bytes()
        path.write_bytes(raw + b"later archived bytes\n")
        fx.refresh(built)
        live = Path(self.tmp.name) / "live.jsonl"
        live.write_bytes(raw)
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copy_not_prefix_of_live$"):
            br.require_ledger_copies_are_prefixes([fx.handle(built)], live)

    def test_one_snapshot_cannot_be_supplied_for_two_windows(self):
        self.assertEqual(tuple(inspect.signature(br.evaluate_window_bracket).parameters), ("archive", "repo_root"))
        first = self.evaluate(self.windows["ALPHA_STD"])
        second = self.evaluate(self.windows["GAMMA_STD"])
        self.assertNotEqual(first.terminal_sequence, second.terminal_sequence)
        self.assertNotEqual(first.ledger_copy_sha256, second.ledger_copy_sha256)

    def test_distinct_post_capture_bounds_and_three_operative_bounds(self):
        results = [self.evaluate(self.windows[name]) for name in ("ALPHA_STD", "BETA_STD", "GAMMA_STD")]
        self.assertEqual(len({row.b_fiducial_s for row in results}), 3)
        for result in results:
            pre, post = result.evaluation["pre"], result.evaluation["post"]
            self.assertNotEqual(pre["b_fiducial_s"], post["b_fiducial_s"])
            self.assertEqual(result.evaluation["endpoint_max_b_fiducial_s"], post["b_fiducial_s"])
            self.assertEqual(result.b_fiducial_s, result.evaluation["b_fiducial_s"])

    def test_member_missing_operative_bound_refuses(self):
        window = self.evaluate(self.windows["GAMMA_STD"])
        with self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
            br.require_member_bound_is_window_bracket({}, window)

    def test_member_pre_capture_bound_substituted_refuses(self):
        window = self.evaluate(self.windows["GAMMA_STD"])
        provenance = {"operative_fiducial_bound_s": window.evaluation["pre"]["b_fiducial_s"]}
        with self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
            br.require_member_bound_is_window_bracket(provenance, window)

    def test_member_another_window_bound_substituted_refuses(self):
        gamma, beta = (self.evaluate(self.windows[name]) for name in ("GAMMA_STD", "BETA_STD"))
        with self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
            br.require_member_bound_is_window_bracket({"operative_fiducial_bound_s": beta.b_fiducial_s}, gamma)

    def test_member_bound_matches_exactly_and_rejects_nonfinite_and_bool(self):
        window = self.evaluate(self.windows["GAMMA_STD"])
        br.require_member_bound_is_window_bracket({"operative_fiducial_bound_s": window.b_fiducial_s}, window)
        with self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
            br.require_member_bound_is_window_bracket({"operative_fiducial_bound_s": window.b_fiducial_s}, window.evaluation)
        for value in (True, "0.045031", float("nan"), float("inf"), window.b_fiducial_s + 1e-15):
            with self.subTest(value=value), self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
                br.require_member_bound_is_window_bracket({"operative_fiducial_bound_s": value}, window)

    def test_missing_cutoff_plan_path_or_window_identity_refuses(self):
        built = self.cloned()
        plan_path = built.archive / "sources/repo/configs/campaigns" / built.entry_data["pack_id"] / "plan_tree.json"
        original = json.loads(plan_path.read_bytes())
        for field in ("plan.path", "window_identity"):
            with self.subTest(field=field):
                row = json.loads(json.dumps(original))
                if field == "plan.path":
                    del row["plan"]["path"]
                else:
                    del row["window_identity"]
                fx.s0.put(plan_path, row)
                fx.refresh(built)
                with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_not_passed$"):
                    self.evaluate(built)
        acceptance = dict(calibration.load_calibration_acceptance_bound())
        del acceptance["ledger_cutoff"]
        with mock.patch.object(calibration, "_acceptance_bound_from_authenticated_bytes", return_value=acceptance):
            with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_not_passed$"):
                self.evaluate(self.windows["GAMMA_STD"])

    def test_alpha_stale_assessment_refuses_even_if_status_says_passed(self):
        # Counterfactual ALPHA assessment: the independent fresh guard must
        # survive a frozen-evaluator result that reports passed but reads stale.
        real = calibration.evaluate_calibration_bracket
        def stale(*args, **kwargs):
            assessment, reasons = real(*args, **kwargs)
            assessment["acceptance"]["freshness"]["status"] = "stale"
            self.assertEqual((assessment["status"], reasons), ("passed", ()))
            return assessment, reasons
        with mock.patch.object(calibration, "evaluate_calibration_bracket", side_effect=stale):
            with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_not_passed$"):
                self.evaluate(self.windows["ALPHA_STD"])

    def test_alpha_failed_assessment_without_reasons_refuses(self):
        real = calibration.evaluate_calibration_bracket
        def failed(*args, **kwargs):
            assessment, reasons = real(*args, **kwargs)
            self.assertEqual(reasons, ())
            assessment["status"] = "failed"
            return assessment, reasons
        with mock.patch.object(calibration, "evaluate_calibration_bracket", side_effect=failed):
            with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_not_passed$"):
                self.evaluate(self.windows["ALPHA_STD"])

    def test_assessment_selection_tamper_refuses_at_both_pins(self):
        # Review PB: flag all but one originally selected member invalid, then
        # omit selected assessments outright. Neither may choose the span.
        for name in ("ALPHA_STD", "GAMMA_STD"):
            built = fx.fork(self.windows[name], Path(self.tmp.name) / name)
            target = built.archive / "withheld/member-assessments.json"
            original = json.loads(target.read_bytes())
            selected = [key for key, member in original["members"].items()
                        if member.get("strict_valid") and member.get("status") == "succeeded"
                        and member.get("anchor_recorded") == "bounded"
                        and Path(member["bundle_path"]).is_relative_to(built.claim)]
            self.assertGreater(len(selected), 1)
            for mode in ("flag_invalid", "omit"):
                with self.subTest(pin=name, mode=mode):
                    row = json.loads(json.dumps(original))
                    for key in selected[1:]:
                        if mode == "omit":
                            del row["members"][key]
                        else:
                            row["members"][key]["strict_valid"] = False
                    fx.s0.put(target, row)
                    fx.refresh(built)
                    with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_not_passed$"):
                        self.evaluate(built)

    def test_selection_recomputes_strict_validation_from_bundle_bytes(self):
        built = self.cloned("ALPHA_STD")
        assessments = json.loads((built.archive / "withheld/member-assessments.json").read_bytes())["members"]
        member = next(row for row in assessments.values() if row.get("strict_valid")
                      and row.get("status") == "succeeded" and row.get("anchor_recorded") == "bounded"
                      and Path(row["bundle_path"]).is_relative_to(built.claim))
        metadata = built.archive / "sources/claim-runs" / Path(member["bundle_path"]).relative_to(built.claim) / "metadata.json"
        row = json.loads(metadata.read_bytes())
        row["synthetic_s2_member"]["strict_valid"] = False
        fx.s0.put(metadata, row)
        fx.refresh(built)
        with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_not_passed$"):
            self.evaluate(built)

    def test_unrostered_bundle_cannot_enter_recomputed_selection(self):
        built = self.cloned("ALPHA_STD")
        assessments = json.loads((built.archive / "withheld/member-assessments.json").read_bytes())["members"]
        member = next(row for row in assessments.values() if row.get("strict_valid")
                      and row.get("status") == "succeeded" and row.get("anchor_recorded") == "bounded"
                      and Path(row["bundle_path"]).is_relative_to(built.claim))
        source = built.archive / "sources/claim-runs" / Path(member["bundle_path"]).relative_to(built.claim)
        shutil.copytree(source, built.archive / "sources/claim-runs/unrostered-synthetic-bundle")
        fx.refresh(built)
        self.assertEqual(self.evaluate(built).evaluation["status"], "passed")

    def test_registered_valid_capture_withheld_refuses_via_wrapper(self):
        built = self.windows["GAMMA_STD"]
        baseline = json.loads((built.archive / "withheld/bracket-evaluation.json").read_bytes())["assessment"]
        self.assertEqual(baseline["status"], "passed")
        real = calibration.discover_calibration_candidates
        seen = []
        def withheld(*args, **kwargs):
            candidates = real(*args, **kwargs)
            remaining = tuple(row for row in candidates if "s2-extra-valid-pre" not in row.relative_path)
            self.assertEqual(len(candidates) - len(remaining), 1)
            seen.append(len(remaining))
            return remaining
        # The evaluator also checks candidate completeness. Keep that duplicate
        # check from masking deletion of the wrapper's independent guard: its
        # result boundary returns this fixture's otherwise passing assessment.
        with mock.patch.object(calibration, "discover_calibration_candidates", side_effect=withheld), \
                mock.patch.object(calibration, "evaluate_calibration_bracket", return_value=(baseline, ())):
            with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_not_passed$"):
                self.evaluate(built)
        self.assertTrue(seen)

    def test_custody_refusals_pass_through_window_input_and_roster_reads(self):
        for relative in ("sources/repo/configs/campaigns/" + self.windows["GAMMA_STD"].entry_data["pack_id"] + "/campaign_policy.json",
                         "member_events"):
            built = fx.fork(self.windows["GAMMA_STD"], Path(self.tmp.name) / str(len(relative)))
            if relative == "member_events":
                target = next((built.archive / "sources/claim-runs").glob("*/events.jsonl"))
            else:
                roster = json.loads((built.archive / "sources/repo/configs/campaigns" / built.entry_data["pack_id"] / "plan_tree.json").read_bytes())
                target = built.archive / "sources/repo" / roster["campaign_policy"]["path"]
            with target.open("ab") as output:
                output.write(b" ")
            with self.subTest(relative=relative), self.assertRaisesRegex(AnalysisRefusal, "^archive_source_unauthenticated$"):
                self.evaluate(built)

    def test_harvest_scope_status_reasons_and_governed_word_must_match(self):
        built = self.cloned()
        target = built.archive / "harvest.json"
        original = json.loads(target.read_bytes())
        for key, value in (("trigger_scope", "sealed"), ("status", "failed"),
                           ("reasons", ["counterfactual"]), ("reasons", None),
                           ("erratum_3_governed", False), ("evaluated", False)):
            with self.subTest(key=key):
                row = json.loads(json.dumps(original))
                row["calibration_bracket"][key] = value
                fx.s0.put(target, row)
                fx.refresh(built)
                with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_differs_from_harvest$"):
                    self.evaluate(built)

    def test_mapping_stand_in_for_window_bracket_refuses(self):
        with self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
            br.require_member_bound_is_window_bracket({"operative_fiducial_bound_s": .123}, {"b_fiducial_s": .123})


class BlockBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = fx.toy_ledger()
        cls.acceptance = {"identity_epoch": calibration.load_calibration_acceptance_bound()["identity_epoch"],
                          "artifact_role": "issued",
                          "derivation_corpus": {"members": [{"b_fiducial_s": "0.036"}] * 24}}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s2-block-")
        self.addCleanup(self.tmp.cleanup)

    def test_made_up_b_max_and_b_sens(self):
        prefix = br.ledger_prefix(self.raw, fx.pin_at(self.raw, 500))
        maximum = br.block_b_max(self.acceptance, prefix)
        self.assertEqual((maximum.value_s, maximum.attained_by_sequence, maximum.T), (.040, 456, 500))
        self.assertEqual(br.b_sens(.038, maximum), .040)
        self.assertEqual(br.b_sens(.045, maximum), .045)

    def test_acceptance_maximum_can_dominate_without_a_ledger_sequence(self):
        acceptance = dict(self.acceptance, derivation_corpus={"members": [{"b_fiducial_s": ".050"}] * 24})
        maximum = br.block_b_max(acceptance, br.ledger_prefix(self.raw, fx.pin_at(self.raw, 500)))
        self.assertEqual((maximum.value_s, maximum.attained_by_sequence), (.050, None))

    def test_acceptance_member_attainer_is_identified_from_ledger_row(self):
        acceptance = dict(self.acceptance, derivation_corpus={"members": [
            {"member_id": "toy-188", "b_fiducial_s": ".900"}] * 24})
        maximum = br.block_b_max(acceptance, br.ledger_prefix(self.raw, fx.pin_at(self.raw, 500)))
        self.assertEqual((maximum.value_s, maximum.attained_by_sequence), (.900, 376))

    def test_T_window_is_second_and_its_copy_is_cut_at_500(self):
        archives = [fx.toy_archive(Path(self.tmp.name) / str(n), self.raw, n, pack=pack)
                    for n, pack in zip((480, 500, 490), ("alpha", "beta", "gamma"))]
        maximum = br.block_b_max_for_archives([fx.handle(item) for item in archives])
        self.assertEqual((maximum.value_s, maximum.attained_by_sequence, maximum.T), (.040, 456, 500))

    def test_copy_disagrees_below_T_refuses(self):
        archives = [fx.toy_archive(Path(self.tmp.name) / str(n), self.raw, n, pack=pack)
                    for n, pack in zip((480, 500, 490), ("alpha", "beta", "gamma"))]
        (archives[0].archive / br.LEDGER_COPY).write_bytes(fx.toy_ledger(changed_at=456))
        # Both chains are internally valid, independently bound, and at their
        # respective pins. Only the cross-window byte-prefix rule rejects them.
        fx.s0.put(archives[0].archive / br.TERMINAL_PIN, fx.pin_at(fx.toy_ledger(changed_at=456), 480))
        fx.refresh(archives[0])
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copies_disagree_below_T$"):
            br.block_b_max_for_archives([fx.handle(item) for item in archives])

    def test_b_max_unchanged_when_all_historical_capture_files_unreadable(self):
        prefix = br.ledger_prefix(self.raw, fx.pin_at(self.raw, 500))
        original = br.block_b_max(self.acceptance, prefix)
        self.assertEqual((original.value_s, original.attained_by_sequence, original.T), (.040, 456, 500))
        # Refuse every file read, including absent/unreachable historical
        # locators. B_max must do zero file I/O and keep every ledger row.
        with mock.patch.object(Path, "read_bytes", side_effect=PermissionError("historical file unreadable")), \
                mock.patch.object(Path, "read_text", side_effect=PermissionError("historical file unreadable")):
            self.assertEqual(br.block_b_max(self.acceptance, prefix), original)

    def test_b_max_refuses_malformed_chain(self):
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_prefix_not_at_terminal_pin$"):
            br.block_b_max(self.acceptance, self.raw + b"broken\n")

    def test_b_max_refuses_bad_numeric_bound(self):
        for value in (True, "NaN", "-0.1", "Infinity", "1e1000", "bad"):
            acceptance = dict(self.acceptance, derivation_corpus={"members": [{"b_fiducial_s": value}] * 24})
            with self.subTest(value=value), self.assertRaisesRegex(AnalysisRefusal, "^block_b_max_invalid$"):
                br.block_b_max(acceptance, self.raw)

    def archives(self):
        return [fx.toy_archive(Path(self.tmp.name) / str(n), self.raw, n, pack=pack)
                for n, pack in zip((480, 500, 490), ("alpha", "beta", "gamma"))]

    def test_largest_bound_at_row_T_is_included(self):
        raw = fx.toy_ledger(bounds={500: "0.9"})
        prefix = br.ledger_prefix(raw, fx.pin_at(raw, 500))
        maximum = br.block_b_max(self.acceptance, prefix)
        self.assertEqual((maximum.value_s, maximum.attained_by_sequence, maximum.T), (.9, 500, 500))

    def test_b_max_acceptance_rewritten_members_cut_list_or_unissued_role_refuses(self):
        archives = self.archives()
        original = json.loads((archives[0].archive / "sources/inputs/acceptance.json").read_bytes())
        for mode in ("rewritten", "cut", "unissued", "missing_cutoff"):
            with self.subTest(mode=mode):
                row = json.loads(json.dumps(original))
                if mode == "rewritten":
                    for member in row["derivation_corpus"]["members"]:
                        member["b_fiducial_s"] = "0.9"
                elif mode == "cut":
                    row["derivation_corpus"]["members"] = row["derivation_corpus"]["members"][:3]
                elif mode == "unissued":
                    row["artifact_role"] = "schema_fixture_unissued"
                else:
                    del row["ledger_cutoff"]
                for built in archives:
                    fx.s0.put(built.archive / "sources/inputs/acceptance.json", row)
                    fx.refresh(built)
                with self.assertRaisesRegex(AnalysisRefusal, "^block_b_max_invalid$"):
                    br.block_b_max_for_archives([fx.handle(built) for built in archives])

    def test_b_max_requires_issued_role_and_exactly_24_members(self):
        for role, count in (("schema_fixture_unissued", 24), ("issued", 3), ("issued", 1), ("issued", 25)):
            acceptance = dict(self.acceptance, artifact_role=role,
                              derivation_corpus={"members": [{"b_fiducial_s": ".036"}] * count})
            with self.subTest(role=role, count=count), self.assertRaisesRegex(AnalysisRefusal, "^block_b_max_invalid$"):
                br.block_b_max(acceptance, self.raw)

    def test_b_max_acceptance_bytes_must_match_across_all_archives(self):
        archives = self.archives()
        target = archives[0].archive / "sources/inputs/acceptance.json"
        target.write_bytes(target.read_bytes() + b" ")
        fx.refresh(archives[0])
        # Isolate byte equality from registry authentication: a parser returning
        # the same document does not excuse different acceptance bytes.
        with mock.patch.object(calibration, "_acceptance_bound_from_authenticated_bytes",
                               return_value=calibration.load_calibration_acceptance_bound()):
            with self.assertRaisesRegex(AnalysisRefusal, "^block_b_max_invalid$"):
                br.block_b_max_for_archives([fx.handle(built) for built in archives])

    def test_b_max_missing_cutoff_is_named_refusal(self):
        archives = self.archives()
        acceptance = dict(calibration.load_calibration_acceptance_bound())
        del acceptance["ledger_cutoff"]
        for built in archives:
            fx.s0.put(built.archive / "sources/inputs/acceptance.json", acceptance)
            fx.refresh(built)
        with mock.patch.object(calibration, "_acceptance_bound_from_authenticated_bytes", return_value=acceptance):
            with self.assertRaisesRegex(AnalysisRefusal, "^block_b_max_invalid$"):
                br.block_b_max_for_archives([fx.handle(built) for built in archives])

    def test_b_max_requires_three_distinct_packs(self):
        handles = [fx.handle(built) for built in self.archives()]
        for archives in ([], handles[:1], handles[:2], [handles[1]] * 3, handles + handles[:1]):
            with self.subTest(count=len(archives)), self.assertRaisesRegex(AnalysisRefusal, "^block_b_max_invalid$"):
                br.block_b_max_for_archives(archives)

    def test_empty_ledger_prefix_check_refuses_even_with_readable_live_ledger(self):
        live = Path(self.tmp.name) / "live.jsonl"
        live.write_bytes(self.raw)
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copy_not_prefix_of_live$"):
            br.require_ledger_copies_are_prefixes([], live)

    def test_nonempty_epoch_continuation_registry_refuses(self):
        with mock.patch.object(calibration, "EPOCH_CONTINUATION_REGISTRY", {"future": {}}):
            with self.assertRaisesRegex(AnalysisRefusal, "^block_b_max_invalid$"):
                br.block_b_max(self.acceptance, self.raw)
