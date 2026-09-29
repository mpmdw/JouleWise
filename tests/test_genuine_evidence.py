"""The fixture must satisfy real identity, battery and environment predicates."""
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.bundle_read import BundleReader, WindowBatteryRefusal, authenticate_window_members
from joulewise.environment_admission import current_environment_refusals
from joulewise.whole_window import _current_strict_summary, custody_telemetry_identity
from tests.bfgs_fixtures import write_charging_pair
from tests.genuine_evidence import write_genuine_evidence


class GenuineEvidenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.bundle = Path(temporary.name) / "genuine"
        self.bundle.mkdir()
        self.summary = {
            "status": "succeeded",
            "summary_provenance": {"reducer_version": "0.5.2"},
            "measurement_quality": {"telemetry_source": "mock"},
            "gross_energy_j": 40.0,
        }
        (self.bundle / "summary_metrics.json").write_text(json.dumps(self.summary))
        write_genuine_evidence(self.bundle)

    def test_current_nonmock_evidence_passes_real_gates(self):
        metadata = json.loads((self.bundle / "metadata.json").read_text())
        summary = json.loads((self.bundle / "summary_metrics.json").read_text())
        identity = custody_telemetry_identity(self.bundle, summary=summary)
        self.assertTrue(identity.triangle_agrees)
        self.assertFalse(identity.production_predicate_exempt)
        self.assertTrue(_current_strict_summary(summary, self.bundle))
        self.assertEqual(summary["gross_energy_j"], self.summary["gross_energy_j"])
        self.assertEqual(authenticate_window_members([("member", self.bundle)])["member"].status, "pass")
        window = BundleReader(self.bundle).measured_window()
        self.assertEqual(current_environment_refusals(
            metadata, bundle_path=self.bundle,
            measured_window_start_s=window.start_s, measured_window_end_s=window.end_s,
        ), ())

    def test_charging_mutation_is_refused(self):
        write_charging_pair(self.bundle)
        with self.assertRaises(WindowBatteryRefusal) as caught:
            authenticate_window_members([("member", self.bundle)])
        self.assertEqual(caught.exception.members[0]["status"], "battery_float_confounded")

    def test_config_digest_mutation_is_refused(self):
        path = self.bundle / "config.json"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaises(WindowBatteryRefusal) as caught:
            authenticate_window_members([("member", self.bundle)])
        self.assertEqual(caught.exception.members[0]["status"], "battery_float_evidence_missing")

    def test_controller_bundle_stays_strictly_valid_after_attachment(self):
        from unittest.mock import patch
        from joulewise.cli import validate_bundle
        from tests.bfgs_fixtures import produce_strict_bundle
        source = {"git_commit": "1" * 40, "tracked": "clean", "staged": "clean",
                  "untracked": "clean", "diff_sha256": "2" * 64}
        with patch("joulewise.bundle._capture_source_state", return_value=source):
            bundle = produce_strict_bundle(self.bundle.parent, "controller")
        self.assertEqual(validate_bundle(bundle, strict=True), [])
        before = json.loads((bundle / "metadata.json").read_text())["adapters"]["telemetry"]
        write_genuine_evidence(bundle)
        after = json.loads((bundle / "metadata.json").read_text())["adapters"]["telemetry"]
        self.assertEqual(after, before)
        self.assertEqual(validate_bundle(bundle, strict=True), [])


    def test_cpu_and_adapter_core_rederive_from_bundle_bytes(self):
        from joulewise.whole_window import _current_core_rederivation_reasons
        from tests.genuine_evidence import POLICY, populate_whole_window_core
        import hashlib

        root = self.bundle.parent
        bundle_ids = [self.bundle.name]
        row = {
            "bundle_ids": bundle_ids,
            "idle_admission_core": {
                "adapter_wattage_continuity": {"decision": "stable"},
                "conditions": [],
            },
        }
        populate_whole_window_core(root, row)
        core = row["idle_admission_core"]
        self.assertEqual(core["members"][0]["cpu_admission"]["decision"], "admitted")
        self.assertEqual(core["adapter_wattage_continuity"]["decision"], "stable")
        manifest = {"members": [{"execution": "invoked", "bundle_ids": bundle_ids}]}

        def rederive():
            return _current_core_rederivation_reasons(
                core=core, bundle_ids=bundle_ids, manifests=[manifest],
                runs_root=root, policy_sha256=hashlib.sha256(POLICY.read_bytes()).hexdigest(),
            )

        clean = rederive()
        self.assertNotIn("cpu_admission_core_failed", clean)
        self.assertNotIn("adapter_continuity_failed", clean)
        # Plant busy CPU telemetry without changing the stored admission ledger.
        idle = self.bundle / "rich_telemetry_idle.jsonl"
        original = idle.read_text()
        records = [json.loads(line) for line in original.splitlines() if line.strip()]
        for record in records:
            record["clusters"] = [{"cpus": [{"idle_ratio": 0.0, "down_ratio": 0.0}]}]
        idle.write_text("".join(json.dumps(record) + "\n" for record in records))
        self.assertIn("cpu_admission_core_failed", rederive())
        idle.write_text(original)
        # Plant an adapter renegotiation while retaining the stored continuity.
        path = self.bundle / "metadata.json"
        metadata = json.loads(path.read_text())
        metadata["environment"]["post_run_observation"]["power"]["adapter_watts"] = 70.0
        path.write_text(json.dumps(metadata))
        self.assertIn("adapter_continuity_failed", rederive())

    def test_nested_fixture_context_keeps_charging_control_and_restores_it(self):
        from tests.genuine_evidence import genuine_evidence_builders, _CHARGING, _BUILDERS_ACTIVE
        with genuine_evidence_builders(charging=True):
            with genuine_evidence_builders():
                self.assertTrue(_CHARGING.get())
                self.assertTrue(_BUILDERS_ACTIVE.get())
        self.assertFalse(_CHARGING.get())
        self.assertFalse(_BUILDERS_ACTIVE.get())


    def test_reference_primary_is_consistent_and_requires_real_calibration(self):
        from joulewise.whole_window import _reference_energy_evidence, _scientific_config_identity
        from tests.genuine_evidence import write_genuine_reference

        write_genuine_reference(self.bundle)
        summary = json.loads((self.bundle / "summary_metrics.json").read_text())
        self.assertEqual(summary["status"], "succeeded")
        gate = summary["window_evidence_precheck"]["gross_request"]
        self.assertEqual(gate["reasons"], ["instrument_calibration_missing"])
        self.assertGreaterEqual(gate["cadence_ratio"], gate["cadence_ratio_min"])
        self.assertTrue(_scientific_config_identity(self.bundle)[1])
        self.assertEqual(_reference_energy_evidence(self.bundle), (None, None, "provenance"))


    def test_deferred_core_waits_for_members_before_adapter_evaluation(self):
        import shutil
        from tests.genuine_evidence import genuine_evidence_builders, populate_whole_window_core
        from tests.test_floor_extraction import CpuAndWholeWindowClaimBarrierTests

        root = self.bundle.parent
        ids = [self.bundle.name, "second"]
        with genuine_evidence_builders():
            row = CpuAndWholeWindowClaimBarrierTests._whole_window_row(root, ids)
        self.assertEqual(row["idle_admission_core"]["adapter_wattage_continuity"]["decision"], "stable")
        shutil.copytree(self.bundle, root / "second")
        populate_whole_window_core(root, row)
        self.assertEqual(row["idle_admission_core"]["adapter_wattage_continuity"]["decision"], "stable")
        self.assertEqual(row["idle_admission_core"]["adapter_wattage_continuity"]["observation_count"], 8)
