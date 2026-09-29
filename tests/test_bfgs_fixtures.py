"""Counterfactual checks for the S1 evidence-forward fixture helpers."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from joulewise import battery_float, whole_window
from joulewise.bundle import RunBundleWriter
from joulewise.bundle_read import BundleReader, WindowBatteryRefusal, authenticate_window_members
from joulewise.cli import validate_bundle
from joulewise.clock import FakeClock
from tests.bfgs_fixtures import (
    FIXTURES, injected_battery_runner, injected_battery_runner_at, rebind_config,
    exemption_parity, produce_strict_bundle, write_capture_evidence,
    write_charging_pair, write_passing_pair,
)
from tests.test_bundle_read import load_config


class BfgsFixtureTests(unittest.TestCase):
    def test_second_form_grants_are_exactly_the_a2_closed_list(self) -> None:
        from tests.bfgs_fixtures import PARITY_SECOND_FORM_TEST_IDS, PARITY_TEST_IDS

        # Remaining named ledger after genuine-evidence conversion; same-count
        # substitutions in either grant list must fail too.
        expected = frozenset({
            "tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity",
            "tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity",
            "tests.test_analysis_integration.AnalysisIntegrationTests.test_named_strata_manifest_preserves_terminal_mock_refusal_with_production_telemetry_identity",
            "tests.test_analysis_integration.AnalysisIntegrationTests.test_private_stochastic_seam_changes_recorded_policy_identity_with_production_telemetry_identity",
            "tests.test_analysis_integration.AnalysisIntegrationTests.test_real_controller_pinned_model_matches_canonical_bytes_and_is_included",
            "tests.test_analysis_integration.AnalysisIntegrationTests.test_real_controller_unpinned_model_is_included_by_loader",
            "tests.test_analysis_integration.AnalysisIntegrationTests.test_unregistered_matching_topup_demotes_but_preserves_fixed_n_analysis_with_production_telemetry_identity",
            "tests.test_analysis_integration.AnalysisIntegrationTests.test_valid_replacement_fills_original_slot_without_sixth_block_with_production_telemetry_identity",
            "tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_failed_adapter_continuity_refuses_but_clean_core_passes",
            "tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_later_passed_row_cannot_supersede_failed_whole_window_row",
        })
        self.assertEqual(PARITY_SECOND_FORM_TEST_IDS, expected)
        self.assertEqual(PARITY_TEST_IDS, expected)
        self.assertTrue(expected <= PARITY_TEST_IDS)

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def bundle(self, run_id: str) -> Path:
        writer = RunBundleWriter.create(self.root, load_config(run_id=run_id), FakeClock())
        writer.write_metadata({"device": {"telemetry": "mock"}})
        return writer.path

    def test_rebound_passing_pair_passes_window_gate(self) -> None:
        bundle = self.bundle("fixture-pass")
        rebind_config(bundle)
        self.assertEqual(json.loads((bundle / "metadata.json").read_text())["device"]["telemetry"],
                         "powermetrics")
        write_passing_pair(bundle)
        verdict = authenticate_window_members((("member", bundle),))["member"]
        self.assertEqual(verdict.status, "pass")
        reader = BundleReader(bundle)
        reader.metadata()
        self.assertEqual(reader.battery_float_status, "pass")

    def test_raw_byte_flip_raises_custody_failure(self) -> None:
        bundle = self.bundle("fixture-corrupt")
        rebind_config(bundle)
        write_passing_pair(bundle)
        raw = bundle / "raw/battery_float.pre.ioreg"
        body = raw.read_bytes()
        raw.write_bytes(bytes([body[0] ^ 1]) + body[1:])
        with self.assertRaises(battery_float.CustodyFailure):
            authenticate_window_members((("member", bundle),))

    def test_charging_pair_refuses_as_confounded(self) -> None:
        bundle = self.bundle("fixture-charging")
        rebind_config(bundle)
        write_charging_pair(bundle)
        with self.assertRaises(WindowBatteryRefusal) as caught:
            authenticate_window_members((("charging", bundle),))
        self.assertEqual(caught.exception.members[0]["status"], "battery_float_confounded")

    def test_config_changed_after_binding_refuses_without_writes(self) -> None:
        bundle = self.bundle("fixture-stale")
        rebind_config(bundle)
        metadata_before = (bundle / "metadata.json").read_bytes()
        (bundle / "config.json").write_bytes((bundle / "config.json").read_bytes() + b" ")
        for writer in (write_passing_pair, write_charging_pair):
            with self.subTest(writer=writer.__name__):
                with self.assertRaisesRegex(ValueError, "^config not bound$"):
                    writer(bundle)
                self.assertEqual((bundle / "metadata.json").read_bytes(), metadata_before)
                self.assertEqual(list((bundle / "raw").glob("battery_float.*")), [])

    def test_h5_mock_bound_pair_writers_refuse_without_writes(self) -> None:
        bundle = self.bundle("fixture-mock")
        metadata_before = (bundle / "metadata.json").read_bytes()
        for writer in (write_passing_pair, write_charging_pair):
            with self.subTest(writer=writer.__name__):
                with self.assertRaisesRegex(ValueError, "^battery pair on mock config$"):
                    writer(bundle)
                self.assertEqual((bundle / "metadata.json").read_bytes(), metadata_before)
                self.assertEqual(list((bundle / "raw").glob("battery_float.*")), [])

    def test_h6_rebind_then_pair_passes_and_has_new_digest(self) -> None:
        bundle = self.bundle("fixture-h6")
        (bundle / "summary_metrics.json").write_text(json.dumps({
            "idle_baseline": {"telemetry_backend": "mock"},
        }))
        old_digest = json.loads((bundle / "metadata.json").read_text())["config_sha256"]
        rebind_config(bundle)
        metadata = json.loads((bundle / "metadata.json").read_text())
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        self.assertEqual(metadata["device"]["telemetry"], "powermetrics")
        self.assertEqual(summary["idle_baseline"]["telemetry_backend"], "powermetrics")
        self.assertNotEqual(metadata["config_sha256"], old_digest)
        self.assertEqual(metadata["config_sha256"],
                         hashlib.sha256((bundle / "config.json").read_bytes()).hexdigest())
        write_passing_pair(bundle)
        self.assertEqual(authenticate_window_members((("member", bundle),))["member"].status,
                         "pass")

    def test_capture_pair_and_digest_authenticate(self) -> None:
        root = self.root / "capture"
        digest = write_capture_evidence(
            root, validation_id="validation-1", session_id="session-1", slot="slot-1",
            evidence={"protocol_id": "fixture-protocol"},
        )
        self.assertEqual(digest, hashlib.sha256((root / "instrument_evidence.json").read_bytes()).hexdigest())
        self.assertEqual(json.loads((root / "instrument_evidence.json").read_text())["protocol_id"],
                         "fixture-protocol")
        self.assertEqual(battery_float.authenticate_capture(root, expected={
            "attempt_id": "validation-1", "session_id": "session-1", "slot": "slot-1",
        }).status, "pass")

    def test_runner_is_deterministic_and_rejects_other_argv(self) -> None:
        runner = injected_battery_runner()
        self.assertEqual(runner(battery_float.IOREG_BATTERY_ARGV).stdout,
                         runner(battery_float.IOREG_BATTERY_ARGV).stdout)
        with self.assertRaises(AssertionError):
            runner(("/usr/bin/true",))

    def test_h8_produced_bundle_passes_gate_and_strict_validation(self) -> None:
        bundle = produce_strict_bundle(self.root, "strict-h8")
        self.assertEqual(authenticate_window_members((("member", bundle),))["member"].status,
                         "pass")
        self.assertEqual(validate_bundle(bundle, strict=True), [])
        metadata = json.loads((bundle / "metadata.json").read_text())
        self.assertEqual(set(metadata["battery_float"]), {"pre", "post"})

    def test_h9_produced_bundle_with_charging_reading_is_confounded(self) -> None:
        bundle = produce_strict_bundle(self.root, "strict-h9")
        rebind_config(bundle)
        write_charging_pair(bundle)
        with self.assertRaises(WindowBatteryRefusal) as caught:
            authenticate_window_members((("member", bundle),))
        self.assertEqual(caught.exception.members[0]["label"], "member")
        self.assertEqual(caught.exception.members[0]["status"],
                         "battery_float_confounded")

    def test_h10_missing_raw_powermetrics_refuses_strict_validation(self) -> None:
        bundle = produce_strict_bundle(self.root, "strict-h10")
        (bundle / "raw" / "powermetrics.plist").unlink()
        self.assertTrue(validate_bundle(bundle, strict=True))

    def test_h11_mock_mutation_refused_before_bundle_creation(self) -> None:
        def set_mock(config):
            config["hardware_target"]["telemetry_backend"] = "mock"

        with self.assertRaisesRegex(ValueError, "^strict bundle on mock backend$"):
            produce_strict_bundle(self.root, "strict-h11", mutate_config=set_mock)
        self.assertFalse((self.root / "strict-h11").exists())

    def test_h12_stale_reading_fails_the_controller_run(self) -> None:
        with self.assertRaisesRegex(AssertionError, "strict bundle run failed"):
            produce_strict_bundle(self.root, "strict-h12",
                                  clock_start=1790373526.0 + 3600)

    def test_h13_runner_at_rewrites_only_the_update_time_line(self) -> None:
        runner = injected_battery_runner_at(lambda: 1790568378.9)
        stamped = runner(battery_float.IOREG_BATTERY_ARGV).stdout
        committed = (FIXTURES / "float.ioreg").read_bytes()
        changed = [
            (old, new)
            for old, new in zip(committed.splitlines(), stamped.splitlines())
            if old != new
        ]
        self.assertEqual(len(committed.splitlines()), len(stamped.splitlines()))
        self.assertEqual(len(changed), 1)
        self.assertIn(b'"UpdateTime" = ', changed[0][0])
        self.assertTrue(changed[0][1].endswith(b'"UpdateTime" = 1790568378'))

    def test_h14_runner_at_refuses_any_other_command_line(self) -> None:
        runner = injected_battery_runner_at(lambda: 1790568378.9)
        with self.assertRaises(AssertionError):
            runner(("/usr/bin/true",))

    def _granted_parity(self, test_id: str, *, second: bool = False):
        first_ids = frozenset({test_id})
        second_ids = frozenset({test_id}) if second else frozenset()
        return patch.multiple("tests.bfgs_fixtures", PARITY_TEST_IDS=first_ids,
                              PARITY_SECOND_FORM_TEST_IDS=second_ids)

    def _floor_case(self):
        from joulewise.floor_extraction import EXTRACTION_SPEC_SCHEMA_VERSION, extract_cells
        from tests.test_floor_extraction import (
            install_synthetic_recovered_manifest, make_summary, write_bundle,
        )

        ids = [f"plan-r{index:02d}" for index in range(1, 4)]
        install_synthetic_recovered_manifest(self.root, ids)
        config_template = json.loads((Path(__file__).parent / "fixtures/d078_r01/config.json").read_text())
        for bundle_id in ids:
            summary = make_summary(40.0, anchor_bound=0.0)
            summary["measurement_quality"]["telemetry_source"] = "powermetrics"
            write_bundle(self.root, bundle_id, summary)
            bundle = self.root / bundle_id
            config = copy.deepcopy(config_template)
            config["run_id"] = bundle_id
            (bundle / "config.json").write_text(json.dumps(config) + "\n")
            metadata = json.loads((bundle / "metadata.json").read_text())
            metadata["run_id"] = bundle_id
            metadata["adapters"] = {"telemetry": {"name": "powermetrics"}}
            (bundle / "metadata.json").write_text(json.dumps(metadata) + "\n")
            rebind_config(bundle)
            write_passing_pair(bundle)
        spec = {"schema_version": EXTRACTION_SPEC_SCHEMA_VERSION, "cells": [{
            "cell_id": "DF-RQ-GROSS-MID", "kind": "absolute",
            "metric": "gross_energy_j", "window_class": "request",
            "members": [{"slot": b, "bundle_id": b} for b in ids],
        }]}
        return ids, spec, extract_cells

    def test_h15_exemption_parity_preserves_floor_members(self) -> None:
        from joulewise.whole_window import WholeWindowDriftAllowanceResult

        ids, spec, extract_cells = self._floor_case()
        # Match the original summary-only floor fixture's independent seams.
        with (self._granted_parity(self.id()), exemption_parity(self.id()),
              patch("joulewise.floor_extraction._default_strict_validator",
                    lambda path, strict: []),
              patch("joulewise.floor_extraction._whole_window_extraction_refusals",
                    lambda runs_root, referenced_bundle_ids, **kwargs: ()),
              patch("joulewise.floor_extraction.whole_window_drift_allowances",
                    lambda runs_root, referenced_bundle_ids, **kwargs:
                    WholeWindowDriftAllowanceResult("legacy", {}))):
            self.assertEqual({key: value.status for key, value in
                              authenticate_window_members((key, self.root / key) for key in ids).items()},
                             {key: "pass" for key in ids})
            report = extract_cells(self.root, spec)
        self.assertEqual(report["spec_membership_refusals"], [])
        self.assertTrue(report["all_cells_extractable"])
        self.assertEqual(report["cells"][0]["n_admitted"], 3)
        self.assertEqual([member["metric_value_j"] for member in report["cells"][0]["members"]],
                         [40.0, 40.0, 40.0])

    def test_h16_ungranted_id_rejected_before_body(self) -> None:
        ran = False
        with self.assertRaisesRegex(AssertionError, "exemption parity not granted"):
            with exemption_parity("tests.not_granted.X.test_y"):
                ran = True
        self.assertFalse(ran)

    def test_h17_charging_member_refused_under_parity(self) -> None:
        bundle = self.bundle("h17")
        rebind_config(bundle)
        write_charging_pair(bundle)
        with self._granted_parity(self.id()), exemption_parity(self.id()):
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members((("member", bundle),))
        self.assertEqual(caught.exception.members[0]["status"], "battery_float_confounded")

    def test_h18_unbound_config_refused_under_parity(self) -> None:
        bundle = self.bundle("h18")
        rebind_config(bundle)
        write_passing_pair(bundle)
        config_path = bundle / "config.json"
        config_path.write_bytes(config_path.read_bytes() + b" ")
        with self._granted_parity(self.id()), exemption_parity(self.id()):
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members((("member", bundle),))
        self.assertEqual(caught.exception.members[0]["status"],
                         "battery_float_evidence_missing")

    def _whole_window_case(self):
        from tests.test_analysis_integration import install_passing_analysis_whole_window

        member = produce_strict_bundle(self.root, "member")
        install_passing_analysis_whole_window(self.root, ["member"], source_name="h-parity")
        references = []
        template = json.loads((Path(__file__).parent / "fixtures/d078_r01/config.json").read_text())
        for position in ("start", "end"):
            bundle_id = f"h-parity-neg8-reference-{position}"
            bundle = self.root / bundle_id
            summary_path = bundle / "summary_metrics.json"
            summary = json.loads(summary_path.read_text())
            summary["measurement_quality"] = {"telemetry_source": "powermetrics"}
            summary_path.write_text(json.dumps(summary) + "\n")
            config = copy.deepcopy(template)
            config["run_id"] = bundle_id
            (bundle / "config.json").write_text(json.dumps(config) + "\n")
            (bundle / "metadata.json").write_text(json.dumps({
                "run_id": bundle_id, "adapters": {"telemetry": {"name": "powermetrics"}},
            }) + "\n")
            rebind_config(bundle)
            write_passing_pair(bundle)
            references.append(bundle)
        return (member, *references)

    def _assert_second_form_admits(self, bundles):
        from tests.test_analysis_integration import prepared_minted_consumption_session

        ids = {bundle.name for bundle in bundles}
        verdicts = authenticate_window_members((bundle.name, bundle) for bundle in bundles)
        self.assertEqual({name: verdict.status for name, verdict in verdicts.items()},
                         {name: "pass" for name in ids})
        registered = {bundles[0].name}
        session = prepared_minted_consumption_session(self.root, registered)
        self.assertTrue(session.ready)
        self.assertEqual(whole_window.whole_window_refusal_reasons(
            self.root, registered, consumption_session=session), ())

    def test_h19_second_form_admits_bound_window(self) -> None:
        from joulewise.analysis_engine.inputs import load_analysis_inputs
        from tests.test_analysis_integration import (
            AnalysisIntegrationTests, PRODUCTION_TELEMETRY_IDENTITY,
            install_passing_analysis_whole_window,
        )

        bundles = self._whole_window_case()
        with self._granted_parity(self.id(), second=True), exemption_parity(self.id()):
            self._assert_second_form_admits(bundles)

        # Z7's registered corpus: retain the original reference energies and
        # envelope, then bind and pair each reference before claim loading.
        case = AnalysisIntegrationTests(
            "test_real_controller_unpinned_model_is_included_by_loader")
        case.setUpClass()
        try:
            case.setUp()
            manifest = json.loads(case.manifest_path.read_text())
            member_ids = sorted(entry["run_id"] for entry in manifest["entries"])
            source_name = "analysis-whole-window-source"
            reference_ids = [
                f"{source_name}-neg8-reference-{position}"
                for position in ("start", "end")
            ]
            for reference_id in reference_ids:
                shutil.rmtree(case.runs_root / reference_id)
            install_passing_analysis_whole_window(
                case.runs_root, member_ids, source_name=source_name)
            template = json.loads(
                (Path(__file__).parent / "fixtures/d078_r01/config.json").read_text())
            for reference_id in reference_ids:
                reference = case.runs_root / reference_id
                summary_path = reference / "summary_metrics.json"
                summary = json.loads(summary_path.read_text())
                summary["measurement_quality"] = {"telemetry_source": "powermetrics"}
                summary_path.write_text(json.dumps(summary) + "\n")
                config = copy.deepcopy(template)
                config["run_id"] = reference_id
                (reference / "config.json").write_text(json.dumps(config) + "\n")
                (reference / "metadata.json").write_text(json.dumps({
                    "run_id": reference_id,
                    "adapters": {"telemetry": {"name": "powermetrics"}},
                }) + "\n")
                rebind_config(reference)
                write_passing_pair(reference)
            with (self._granted_parity(self.id(), second=True),
                  exemption_parity(self.id()),
                  patch("joulewise.analysis_engine.inputs.custody_telemetry_identity",
                        return_value=PRODUCTION_TELEMETRY_IDENTITY)):
                verdicts = authenticate_window_members(
                    (bundle_id, case.runs_root / bundle_id)
                    for bundle_id in [*member_ids, *reference_ids])
                self.assertEqual({verdict.status for verdict in verdicts.values()},
                                 {"pass"})
                loaded = load_analysis_inputs(
                    case.manifest_path, case.runs_root, case.floor_path,
                    strict_validator=validate_bundle)
            self.assertEqual(len(loaded.registered), len(member_ids))
            self.assertEqual({evidence.inclusion_status
                              for evidence in loaded.registered.values()},
                             {"included"})
            self.assertEqual({reason for evidence in loaded.registered.values()
                              for reason in evidence.base_reason_codes}, set())
        finally:
            case.doCleanups()
            case.tearDownClass()

    def test_h20_first_form_keeps_original_current_summary(self) -> None:
        original = whole_window._current_strict_summary
        with self._granted_parity(self.id()), exemption_parity(self.id()):
            self.assertIs(whole_window._current_strict_summary, original)

    def test_h21_charging_member_refused_under_both_forms(self) -> None:
        bundles = self._whole_window_case()
        write_charging_pair(bundles[0])
        with self._granted_parity(self.id(), second=True), exemption_parity(self.id()):
            with self.assertRaises(WindowBatteryRefusal) as caught:
                self._assert_second_form_admits(bundles)
        self.assertEqual(caught.exception.members[0]["status"], "battery_float_confounded")

    def test_h22_unbound_member_refused_under_both_forms(self) -> None:
        bundles = self._whole_window_case()
        config_path = bundles[0] / "config.json"
        config_path.write_bytes(config_path.read_bytes() + b" ")
        with self._granted_parity(self.id(), second=True), exemption_parity(self.id()):
            with self.assertRaises(WindowBatteryRefusal) as caught:
                self._assert_second_form_admits(bundles)
        self.assertEqual(caught.exception.members[0]["status"],
                         "battery_float_evidence_missing")


if __name__ == "__main__":
    unittest.main()
