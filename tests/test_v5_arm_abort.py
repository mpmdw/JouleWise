"""Authentic verifier expiry path on synthetic receipts; no machine probes."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, battery_float, network_time_off
from joulewise import arm_readiness_evidence_t0 as author
from joulewise.night_gate import NightPlan
from scripts import check_v5_arm_abort as checker
from scripts import write_v5_qualification_plan as writer
from tests import battery_float_corpus as corpus
from tests.test_arm_readiness_schemas import sample_arm, sample_evidence, probe_clock_value, TEST_BOOT_SESSION_ID
from tests import test_v5_qualification_plan as writer_tests


class ArmAbortTests(unittest.TestCase):
    def setUp(self):
        # Reuse the fixture constructor; its actual gate/serializer are exercised
        # in the writer tests. Only physical/frozen readiness inputs are stubbed.
        fixture = writer_tests.PlanWriterTests("test_canonical_create_once_records_and_run_command")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.root = fixture.root
        self.custody = self.root / "a1-fixture"
        self.custody.mkdir()
        self.pack = fixture.pack
        self.head = fixture.head
        self.context = copy.deepcopy(fixture.input["arm_context"])
        self.context["custody_root"] = str(self.custody)
        self.digest = fixture.input["pack"]["sha256"]
        auth = dict(fixture.input["authorization"], purpose="G2B_SHAKEDOWN",
                    authority="D-171 §3", attempt_id="a1-fixture/1")
        auth_ref = writer.create_record(self.custody / "authorization_record.json", auth)
        confirmation = writer.read_object(fixture.confirm)
        confirmation_ref = writer.create_record(self.custody / "step6_confirmation_record.json", confirmation)
        binding = {"pack_id": self.pack.name, "pack_root": str(self.pack), "pack_sha256": self.digest,
                   "attempt_ordinal": 1, "authorization_record": auth_ref, "confirmation_record": confirmation_ref}
        plan = dict(fixture.input["plan"], plan_id="a1-fixture", custody_root=str(self.custody), pack_night=binding)
        self.plan = NightPlan.from_mapping(plan)
        self.context_path = self.custody / "arm-only-context.json"
        writer.create_record(self.context_path, {"schema_version": writer.ARM_ONLY_SCHEMA,
            "occurrence": "a1", "mode": "ARM_ONLY_NO_LAUNCH", "head": self.head,
            "pack_night": binding, "arm_context": self.context, "plan_binding": plan})
        self.clock = 1_000_000_000_000
        self.epoch = 2000.
        self.valid_until = self.clock + 300_000_000_000
        self.arm = sample_arm(self.root)
        self.arm.update(arm_context=self.context, valid_until_monotonic_ns=self.valid_until)
        self.arm["reviewed_main"].update(head_commit=self.head, local_main_commit=self.head, origin_main_commit=self.head)
        self.arm["pack"].update(pack_id=self.pack.name, pack_root=str(self.pack), pack_sha256=self.digest,
                                window_id="a1-fixture", plan_id="a1-fixture")
        self.pack_custody = self.custody / self.pack.name
        self.namespace = self.pack_custody / "arm_readiness.receipts"
        self.namespace.mkdir(parents=True)
        self.arm_path = self.namespace / "arm-0001.json"
        evidence_dir = self.pack_custody / author._EVIDENCE_DIRECTORY
        evidence_dir.mkdir()
        input_dir = self.pack_custody / author._INPUT_DIRECTORY
        input_dir.mkdir()
        (self.pack_custody / author._SOURCE_DIRECTORY).mkdir()
        for index, row in enumerate(author._EXPECTED_ROWS):
            receipt = sample_evidence()
            kind = author._ROW_KIND[row]
            origin = self.clock - 10_000_000_000
            receipt.update(evidence_id=f"fixture-{index:02}", kind=kind,
                           valid_until_monotonic_ns=origin + author._validity_horizon_ns(kind),
                           head_commit=self.head, pack_sha256=self.digest)
            if kind == "CLOCK_ATTESTATION":
                value = probe_clock_value()
                value["r1_batch_finished_monotonic_ns"] = origin - 50_000_000_000
                receipt["facts"] = [{"fact_id": "clock.correct_and_prior_state.v1", "value_type": "OBJECT",
                    "value": value, "source_kind": "PROBE", "source_path": "clock-source.json", "source_sha256": "0" * 64}]
            source_path = self.pack_custody / author._source_path(row)
            source_ref = writer.create_record(source_path, {"primary_artifacts": [], "input_artifacts": [], "fixture": True})
            for fact in receipt["facts"]:
                fact.update(source_path=source_path.relative_to(self.pack_custody).as_posix(), source_sha256=source_ref["sha256"])
            path = evidence_dir / author._receipt_name(row)
            reference = writer.create_record(path, receipt)
            path.with_name(path.name + ".sha256").write_bytes(readiness.gnu_sidecar(reference["sha256"], path.name))
            self.arm["evidence"].append({"evidence_id": receipt["evidence_id"], "receipt_kind": "evidence",
                "namespace": "WINDOW_CUSTODY", "path": path.relative_to(self.pack_custody).as_posix(),
                "sha256": reference["sha256"], "schema_version": receipt["schema_version"], "status": "PASS"})
        for index, (step, name) in enumerate(author._CAPTURE_FILES.items()):
            writer.create_record(input_dir / name, {"schema_version": author._COMMAND_SCHEMA,
                "step_id": step, "argv": ["fixture-command"], "cwd": str(self.root), "exit_code": 0,
                "stdout": "fixture", "stderr": "", "boot_session_id": TEST_BOOT_SESSION_ID,
                "started_monotonic_ns": self.clock - (620 - index * 100) * 1_000_000_000,
                "finished_monotonic_ns": self.clock - (610 - index * 100) * 1_000_000_000})
        self.arm["evidence"].sort(key=lambda r: r["evidence_id"])
        self.save_arm()
        self.evidence = {"network_time_off": {}, "battery": {},
                         "expiry_check_deadline_epoch_s": 2400., "s1_t0_not_before_epoch_s": 2500.}
        off_path = self.custody / "network_time_off.json"
        off = {"schema": network_time_off.SCHEMA, "argv": list(network_time_off.OFF_ARGV),
               "exit_code": 0, "stdout": "Network Time is already off.\n", "stderr": "",
               "boot_id": TEST_BOOT_SESSION_ID, "plan_id": self.plan.plan_id, "window_id": "a1-fixture",
               "epoch_s": self.epoch - 1500, "monotonic_s": self.clock / 1e9 - 1500}
        self.evidence["network_time_off"] = writer.create_record(off_path, off)
        for phase in ("arm", "publication", "t0"):
            raw = corpus.document(corpus.required(int(self.epoch)))
            raw_path = self.custody / f"battery-{phase}.ioreg"
            raw_path.write_bytes(raw)
            record, _ = battery_float.observe(phase=phase, wall_time_s=self.epoch,
                monotonic_ns=lambda: self.clock, raw_path=str(raw_path), plan_id=self.plan.plan_id,
                runner=lambda argv, raw=raw: SimpleNamespace(args=argv, stdout=raw, stderr=b"", returncode=0))
            self.evidence["battery"][phase] = {
                "record": writer.create_record(self.custody / f"battery-{phase}.json", record),
                "raw": writer.locator(raw_path)}
        self.evidence_path = self.custody / "arm-abort-evidence.json"
        self.save_evidence()
        self.patches = [mock.patch.object(readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID),
                        mock.patch.object(readiness.time, "monotonic_ns", side_effect=lambda: self.clock),
                        mock.patch.object(readiness, "_derive_arm_semantics_for_verification", return_value=([], []))]
        for patch in self.patches:
            patch.start()
            self.addCleanup(patch.stop)

    def save_arm(self):
        self.arm_path.write_bytes(readiness.render_json(self.arm))
        self.arm_path.with_name(self.arm_path.name + ".sha256").write_bytes(
            readiness.gnu_sidecar(writer.locator(self.arm_path)["sha256"], self.arm_path.name))

    def save_evidence(self):
        self.evidence_path.write_bytes(readiness.render_json(self.evidence))

    def observe(self):
        return checker.observe(self.context_path, self.arm_path, self.evidence_path,
                               now_ns=lambda: self.clock, now_epoch=lambda: self.epoch,
                               boot=lambda: TEST_BOOT_SESSION_ID)

    def finish(self, **kwargs):
        return checker.finish(self.context_path, now_ns=lambda: self.clock,
                              now_epoch=lambda: self.epoch, boot=lambda: TEST_BOOT_SESSION_ID, **kwargs)

    def expire(self):
        self.clock = self.valid_until + 1
        self.epoch = 2300.000000001

    def test_native_battery_phases_bind_sites_and_preserve_raw_authentication(self):
        for site, phase in (("arm", "arm_check"), ("publication", "publish_install"),
                            ("publication", "validate_install"), ("t0", "t0_power_row")):
            path = Path(self.evidence["battery"][site]["record"]["path"])
            value = writer.read_object(path); value["phase"] = phase
            path.write_bytes(readiness.render_json(value))
            self.evidence["battery"][site]["record"] = writer.locator(path)
            self.assertEqual(len(checker.battery_sources(self.evidence["battery"], self.plan)), 6)
        value["phase"] = "publish_install"
        path.write_bytes(readiness.render_json(value))
        self.evidence["battery"]["t0"]["record"] = writer.locator(path)
        with self.assertRaisesRegex(ValueError, "battery_record"):
            checker.battery_sources(self.evidence["battery"], self.plan)
        value["phase"] = "t0_power_row"; value["raw_stdout_sha256"] = "0" * 64
        path.write_bytes(readiness.render_json(value))
        self.evidence["battery"]["t0"]["record"] = writer.locator(path)
        with self.assertRaisesRegex(ValueError, "battery_record"):
            checker.battery_sources(self.evidence["battery"], self.plan)

    def test_real_verifier_pass_then_canonical_expiry_and_create_once_control(self):
        observed = self.observe()
        self.assertEqual("PASS", observed["arm_verification"]["status"])
        self.assertEqual(self.valid_until + 1, observed["earliest_expired_check_monotonic_ns"])
        self.assertEqual(15, len(observed["receipt_horizons"]))
        self.assertEqual(50_000_000_000, observed["q110"]["elapsed_ns"])
        self.expire()
        record = self.finish()
        self.assertEqual("readiness_record_expired", record["refusal_reason_code"])
        self.assertTrue(all(record["absence"].values()))
        target = self.custody / "arm-abort-control.json"
        self.assertEqual(0o600, target.stat().st_mode & 0o777)
        before = target.read_bytes()
        with self.assertRaises(FileExistsError):
            self.finish()
        self.assertEqual(before, target.read_bytes())

    def test_cannot_authenticate_already_expired_arm_or_finish_without_observation(self):
        with self.assertRaises(FileNotFoundError):
            self.finish()
        self.expire()
        with self.assertRaises(readiness.ArmReadinessError) as caught:
            self.observe()
        self.assertEqual("readiness_record_expired", caught.exception.reason_code)

    def test_no_shortcut_at_exact_expiry_and_wait_uses_own_horizon(self):
        self.observe()
        self.clock = self.valid_until
        with self.assertRaisesRegex(ValueError, "not_yet_expired"):
            self.finish()
        waits = []
        def advance(seconds):
            waits.append(seconds)
            self.clock += max(1, int(seconds * 1e9))
            self.epoch += seconds
        self.finish(wait=True, sleep=advance)
        self.assertEqual([1e-9], waits)

    def test_boot_change_and_late_or_s1_order_refuse(self):
        self.observe()
        self.expire()
        with self.assertRaisesRegex(ValueError, "boot_changed"):
            checker.finish(self.context_path, boot=lambda: "other-boot")
        self.epoch = 2501
        with self.assertRaisesRegex(ValueError, "expiry_or_s1_order"):
            self.finish()

    def test_each_consumption_pending_started_bundle_and_sampler_artifact_refuses(self):
        self.observe()
        self.expire()
        for name in ("capability.consumed.json", "launch.pending", "chain.started", "metadata.json", "powermetrics.raw.txt"):
            with self.subTest(name=name):
                path = self.custody / name
                path.write_text("fixture")
                with self.assertRaisesRegex(ValueError, "launch_or_bundle_present"):
                    self.finish()
                path.unlink()
        path = Path(self.context["claim_runs_root"]) / "unknown-bundle"
        path.mkdir()
        with self.assertRaisesRegex(ValueError, "runs_not_empty"):
            self.finish()

    def test_wrong_refusal_and_expired_arm_accepted_refuse(self):
        self.observe()
        self.expire()
        for replacement in (mock.Mock(return_value={}), mock.Mock(side_effect=readiness.ArmReadinessError("readiness_record_consumed", "fixture"))):
            with mock.patch.object(readiness, "verify_arm_receipt", replacement):
                with self.assertRaises(ValueError):
                    self.finish()

    def test_arm_bytes_mutated_missing_t0_or_false_pass_refuse(self):
        self.observe()
        self.expire()
        self.arm["issued_at_utc"] = "2026-10-05T00:00:00Z"
        self.save_arm()
        with self.assertRaises(ValueError):
            self.finish()

    def test_retained_t0_source_changed_after_observation_refuses(self):
        observed = self.observe()
        source = next(ref for ref in observed["sources"] if author._SOURCE_DIRECTORY in ref["path"])
        Path(source["path"]).write_bytes(b"{}\n")
        self.expire()
        with self.assertRaises(ValueError):
            self.finish()

    def test_second_arm_after_observation_refuses(self):
        self.observe()
        other = copy.deepcopy(self.arm)
        other["receipt_id"] = "arm-0002"
        other["supersedes"] = {"receipt_id": self.arm["receipt_id"],
            "receipt_path": "arm_readiness.receipts/" + self.arm_path.name,
            "receipt_sha256": writer.locator(self.arm_path)["sha256"],
            "pack_id": self.pack.name, "pack_sha256": self.digest}
        path = self.namespace / "arm-0002.json"
        ref = writer.create_record(path, other)
        path.with_name(path.name + ".sha256").write_bytes(readiness.gnu_sidecar(ref["sha256"], path.name))
        self.expire()
        with self.assertRaisesRegex(ValueError, "a1_fresh_arm_namespace"):
            self.finish()

    def test_off_settle_is_before_author_not_after_expiry_wait(self):
        path = Path(self.evidence["network_time_off"]["path"])
        off = writer.read_object(path)
        off.update(epoch_s=self.epoch - 605, monotonic_s=self.clock / 1e9 - 605)
        path.write_bytes(readiness.render_json(off))
        self.evidence["network_time_off"] = writer.locator(path)
        self.save_evidence()
        with self.assertRaisesRegex(ValueError, "has not settled"):
            self.observe()

    def test_battery_nonpass_digest_mismatch_and_missing_site_refuse(self):
        del self.evidence["battery"]["publication"]
        self.save_evidence()
        with self.assertRaisesRegex(ValueError, "battery_sites"):
            self.observe()

    def test_battery_raw_mutation_refuses(self):
        Path(self.evidence["battery"]["arm"]["raw"]["path"]).write_bytes(b"different raw bytes")
        with self.assertRaises(ValueError):
            self.observe()

    def test_battery_authentic_nonpass_refuses(self):
        item = self.evidence["battery"]["arm"]
        raw = corpus.document(corpus.required(int(self.epoch)).replace(b'"InstantAmperage" = 0', b'"InstantAmperage" = 201'))
        raw_path = Path(item["raw"]["path"])
        raw_path.write_bytes(raw)
        record, _ = battery_float.observe(phase="arm", wall_time_s=self.epoch,
            monotonic_ns=lambda: self.clock, raw_path=str(raw_path), plan_id=self.plan.plan_id,
            runner=lambda argv: SimpleNamespace(args=argv, stdout=raw, stderr=b"", returncode=0))
        record_path = Path(item["record"]["path"])
        record_path.write_bytes(readiness.render_json(record))
        item.update(record=writer.locator(record_path), raw=writer.locator(raw_path))
        self.save_evidence()
        with self.assertRaises(ValueError):
            self.observe()

    def test_t0_membership_and_clock_probe_source_refuse(self):
        self.arm["evidence"].pop()
        self.save_arm()
        with self.assertRaisesRegex(ValueError, "t0_arm_binding"):
            self.observe()

    def test_clock_row_must_have_probe_lineage(self):
        path = self.pack_custody / author._EVIDENCE_DIRECTORY / author._receipt_name("clock.correct_and_prior_state")
        receipt = writer.read_object(path)
        receipt["facts"][0]["source_kind"] = "GIT"
        path.write_bytes(readiness.render_json(receipt))
        digest = writer.locator(path)["sha256"]
        path.with_name(path.name + ".sha256").write_bytes(readiness.gnu_sidecar(digest, path.name))
        for ref in self.arm["evidence"]:
            if ref["path"] == path.relative_to(self.pack_custody).as_posix():
                ref["sha256"] = digest
        self.save_arm()
        with self.assertRaisesRegex(ValueError, "clock_not_probe"):
            self.observe()


if __name__ == "__main__":
    unittest.main()


class A2ExpiryTests(unittest.TestCase):
    def test_a2_uses_same_authentic_expiry_recipe_with_distinct_occurrence(self):
        fixture = ArmAbortTests('test_real_verifier_pass_then_canonical_expiry_and_create_once_control')
        fixture.setUp()
        try:
            value = writer.read_object(fixture.context_path)
            value['occurrence'] = 'a2'
            fixture.context_path.write_bytes(readiness.render_json(value))
            fixture.observe()
            fixture.expire()
            result = fixture.finish()
            self.assertEqual(result['occurrence'], 'a2')
            self.assertEqual(result['refusal_reason_code'], 'readiness_record_expired')
            self.assertTrue(all(result['absence'].values()))
        finally:
            fixture.doCleanups()
