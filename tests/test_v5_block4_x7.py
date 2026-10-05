"""Attempt-history and native NULL recovery fixtures; never live qualification."""
import copy
from dataclasses import replace
from pathlib import Path
import subprocess
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, calibration_ledger as ledger
from joulewise import night_gate, v5_qualification as q
from scripts import restore_v5_null_reservation as restore


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(readiness.render_json(value))
    return q.reference(path)


def attempt(name, previous, *, occurrence="s1", verdict="NULL", **extra):
    return {"schema": q.ATTEMPT_HARVEST_SCHEMA, "plan_id": name,
            "occurrence": occurrence, "previous_attempt": previous, "verdict": verdict,
            "cause_codes": ["chain_never_started"] if verdict == "NULL" else [],
            "cause_classes": [], **extra}


def bind_history_fixture(path, plan, archive_root, *, occurrence="s1", previous=None):
    """Canonical static authority for component fixtures that mock runtime launch."""
    archive_root.mkdir(parents=True, exist_ok=True)
    custody = Path(plan.custody_root)
    custody.mkdir(parents=True, exist_ok=True)
    chain = Path(plan.chain_path)
    if "V5_QUALIFICATION_OCCURRENCE" not in chain.read_text():
        chain.write_text(f"export V5_QUALIFICATION_OCCURRENCE={occurrence}\n" + chain.read_text())
    Path(plan.chain_sha256_path).write_bytes(readiness.gnu_sidecar(q.sha(chain), chain.name))
    binding = getattr(plan, "pack_night", None) or {}
    pack_id = binding.get("pack_id", "fixture-pack")
    pack_root = Path(binding.get("pack_root", str(custody.parent / pack_id)))
    if pack_root.name != pack_id:
        canonical = pack_root.parent / pack_id
        if not canonical.exists():
            shutil.copytree(pack_root, canonical)
        pack_root = canonical
    pack_root.mkdir(parents=True, exist_ok=True)
    pointer = {"none": True} if previous is None else previous
    auth = {"purpose": "G2B_SHAKEDOWN", "attempt_id": plan.plan_id + "/1", "claim_eligible": False,
            "permitted_blocks": 1, "pack_sha256": "a" * 64, "permitted_chain_sha256": q.sha(chain),
            "authority": "D-171 fixture", "previous_attempt": pointer, "block_archive_root": str(archive_root)}
    auth_ref = put(custody / "history-fixture-authorization.json", auth)
    confirm_ref = put(custody / "history-fixture-confirmation.json", {})
    value = {"schema": night_gate.PACK_PLAN_SCHEMA, "schema_version": 3,
             "plan_id": plan.plan_id, "receipt_class": "TRANSACTION_PACK", "t0_epoch_s": 0.,
             "window_max_s": 3600, "authored_epoch_s": 0., "repo_head": "a" * 40,
             "measurement_root": str(getattr(plan, "measurement_root", custody.parent)), "measurement_head": "a" * 40,
             "chain_path": str(chain), "chain_sha256_path": plan.chain_sha256_path,
             "custody_root": str(custody), "registration_path": None, "previous_attempt": pointer,
             "block_archive_root": str(archive_root),
             "pack_night": {"pack_id": pack_id, "pack_root": str(pack_root), "pack_sha256": "a" * 64,
                            "attempt_ordinal": 1, "authorization_record": auth_ref, "confirmation_record": confirm_ref}}
    put(path, value)
    return night_gate.NightPlan.from_mapping(value)


class AttemptHistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.archive = self.root / "block-harvests"
        self.archive.mkdir()

    def save(self, record):
        return put(self.archive / "attempts" / record["plan_id"] / "harvest.json", record)

    def history(self, record, **kwargs):
        return q.attempt_history(record, self.archive, **kwargs)

    def admission(self, name, previous):
        bundle = self.root / name
        reason = "display became or remained awake during idle admission"
        metadata = put(bundle / "metadata.json", {
            "run_id": name, "campaign_policy": {"sha256": q.sha(Path(__file__).resolve().parents[1] / "configs/campaign_policies/quiet_mac_p2_production.json")}, "environment_admission": {
                "policy_version": "environment-guard-cooldown-v2", "on_fail": "abort",
                "schema_version": "joulewise.environment_admission.v1", "decision": "abort", "failure": reason,
                "guard_observations": [{"phase": "before_attempt_1", "capture_skipped": False,
                    "errors": {}, "display_power_state": "any_awake", "screensaver_engaged": False}]}})
        summary = put(bundle / "summary_metrics.json", {"status": "failed", "failure_message": reason})
        events_path = bundle / "events.jsonl"
        events_path.write_bytes(readiness.render_json({"event_type": "failure", "phase": "idle_baseline", "message": reason}).replace(b"\n", b" ") + b"\n")
        events = q.reference(events_path)
        return attempt(name, previous, verdict="RECOVER", cause_codes=[q.ADMISSION_ABORT_CODE],
            cause_classes=["instrument_physics"], recovery_classification="admission_abort",
            admission_abort={"metadata": metadata, "summary": summary, "events": events})

    def test_first_attempt_and_completed_harvest_replay(self):
        current = attempt("first", {"none": True})
        self.assertEqual(self.history(current)["harvests"], [])
        saved = self.save(current)
        self.assertEqual(self.history(current, current_harvest=Path(saved["path"]))["harvests"], [saved])

    def test_missing_pointer_and_wrong_sha256_refuse(self):
        current = attempt("first", {"none": True})
        del current["previous_attempt"]
        with self.assertRaisesRegex(q.HarvestRefusal, "record_invalid"):
            self.history(current)
        prior = self.save(attempt("prior", {"none": True}))
        prior["sha256"] = "0" * 64
        with self.assertRaisesRegex(q.HarvestRefusal, "digest_mismatch"):
            self.history(attempt("fresh", prior))
        for value in (None, {}, {"none": False}, {"none": 1}, {"none": True, "path": "/extra"}):
            with self.subTest(value=value), self.assertRaises(q.HarvestRefusal):
                q.previous_attempt(value)

    def test_null_to_fresh_s1_spends_neither_allowance(self):
        prior = self.save(attempt("prior", {"none": True}))
        proof = self.history(attempt("fresh", prior))
        self.assertEqual((proof["s2_count"], proof["admission_abort_count"]), (0, 0))
        self.assertEqual(proof["harvests"], [prior])

    def test_fork_refuses(self):
        prior = self.save(attempt("first", {"none": True}))
        self.save(attempt("fork", prior))
        with self.assertRaisesRegex(q.HarvestRefusal, "fork"):
            self.history(attempt("current", prior))

    def test_orphan_and_second_none_refuse(self):
        prior = self.save(attempt("first", {"none": True}))
        second = self.save(attempt("second", prior))
        # The unreferenced record follows an existing ancestor but is not on
        # the current chain; census catches it even though its own hash passes.
        outside = put(self.root / "outside/harvest.json", attempt("outside", {"none": True}))
        orphan = self.save(attempt("orphan", outside))
        with self.assertRaisesRegex(q.HarvestRefusal, "orphan"):
            self.history(attempt("current", second))
        Path(orphan["path"]).unlink()
        self.save(attempt("second-root", {"none": True}))
        with self.assertRaisesRegex(q.HarvestRefusal, "second_none"):
            self.history(attempt("current", second))

    def test_symlink_or_external_predecessor_refuses(self):
        outside = put(self.root / "external/harvest.json", attempt("outside", {"none": True}))
        with self.assertRaisesRegex(q.HarvestRefusal, "outside_block"):
            self.history(attempt("current", outside))
        (self.archive / "hidden").symlink_to(self.root / "external", target_is_directory=True)
        with self.assertRaisesRegex(q.HarvestRefusal, "symlink"):
            self.history(attempt("current", {"none": True}))

    def test_one_admission_abort_rearms_without_end_state_or_s2(self):
        abort = self.admission("abort", {"none": True})
        proof = self.history(abort)
        disposition = q.admission_abort_disposition(abort, proof)
        self.assertFalse(disposition["end_state"])
        self.assertFalse(disposition["consumes_s2"])
        self.assertIn("fresh_s1", disposition["next_step"])
        self.assertEqual(self.history(attempt("fresh", self.save(abort)))["admission_abort_count"], 1)

    def test_second_admission_abort_requires_consult_and_third_attempt_refuses(self):
        first = self.admission("first", {"none": True})
        second = self.admission("second", self.save(first))
        proof = self.history(second)
        self.assertTrue(proof["same_refusal_twice"])
        self.assertEqual(q.admission_abort_disposition(second, proof)["next_step"], "same_refusal_twice_consult_required")
        with self.assertRaisesRegex(q.HarvestRefusal, "same_refusal_twice"):
            self.history(attempt("third", self.save(second)))

    def test_admission_with_other_recover_cause_and_mutated_guard_refuse(self):
        abort = self.admission("first", {"none": True})
        mixed = copy.deepcopy(abort)
        mixed["cause_codes"].append("battery_observation_not_passed")
        with self.assertRaisesRegex(q.HarvestRefusal, "other_recover_cause"):
            self.history(mixed)
        ref = abort["admission_abort"]["metadata"]
        path = Path(ref["path"])
        document = q.read(path)
        document["environment_admission"]["guard_observations"][0]["capture_skipped"] = True
        abort["admission_abort"]["metadata"] = put(path, document)
        with self.assertRaisesRegex(q.HarvestRefusal, "not_guard_attested"):
            self.history(abort)

    def test_tooling_recover_to_s2_and_physics_recover_refusal(self):
        recover = attempt("s1", {"none": True}, verdict="RECOVER",
                          cause_codes=["named_launch_defect"], cause_classes=["tooling"])
        prior = self.save(recover)
        self.assertEqual(self.history(attempt("s2", prior, occurrence="s2", verdict="PASS"))["s2_count"], 1)
        recover["cause_classes"] = ["instrument_physics"]
        prior = self.save(recover)
        with self.assertRaisesRegex(q.HarvestRefusal, "named_tooling_recover"):
            self.history(attempt("s2", prior, occurrence="s2"))

    def test_second_s2_refuses_and_s1_cannot_bypass_tooling_s2_rule(self):
        recover = attempt("first", {"none": True}, verdict="RECOVER",
                          cause_codes=["named_launch_defect"], cause_classes=["tooling"])
        first_s2 = self.save(attempt("s2-first", self.save(recover), occurrence="s2", verdict="PASS"))
        with self.assertRaisesRegex(q.HarvestRefusal, "second_s2"):
            self.history(attempt("s2-second", first_s2, occurrence="s2", verdict="PASS"))
        # An ordinary tooling RECOVER must use the governed s2 path.
        Path(first_s2["path"]).unlink()
        with self.assertRaisesRegex(q.HarvestRefusal, "not_rearmable"):
            self.history(attempt("fresh-s1", q.reference(self.archive / "attempts/first/harvest.json")))

    def test_qualification_and_r3_harvests_are_not_attempts(self):
        first = self.save(attempt("first", {"none": True}))
        put(Path(first["path"]).parent / "qualification/harvest.json", {"schema": "qualification"})
        put(Path(first["path"]).parent / "reharvest-1/harvest.json", {"schema": "derived"})
        self.assertEqual(self.history(attempt("fresh", first))["harvests"], [first])

    def test_all_native_display_and_screensaver_guard_reasons_replay(self):
        from joulewise.environment_admission import environment_observation_failure
        for index, observation in enumerate((
                {"display_power_state": "any_awake", "screensaver_engaged": False},
                {"display_power_state": "all_asleep", "screensaver_engaged": True},
                {"display_power_state": "unknown", "screensaver_engaged": False},
                {"display_power_state": "all_asleep", "screensaver_engaged": None})):
            record = self.admission(f"guard-{index}", {"none": True})
            evidence = record["admission_abort"]
            metadata = q.read(Path(evidence["metadata"]["path"]))
            metadata["environment_admission"]["guard_observations"][0].update(observation)
            reason = environment_observation_failure(observation)
            metadata["environment_admission"]["failure"] = reason
            evidence["metadata"] = put(Path(evidence["metadata"]["path"]), metadata)
            evidence["summary"] = put(Path(evidence["summary"]["path"]), {"status": "failed", "failure_message": reason})
            evidence["events"] = put(Path(evidence["events"]["path"]), {"event_type": "failure", "phase": "idle_baseline", "message": reason})
            # Events are native one-object-per-line, not pretty printed JSON.
            path = Path(evidence["events"]["path"])
            path.write_bytes(readiness.render_json(q.read(path)).replace(b"\n", b" ") + b"\n")
            evidence["events"] = q.reference(path)
            self.assertTrue(q.is_admission_abort(record))

    def test_cpu_gpu_and_combined_power_retry_failures_replay_native_rows(self):
        from joulewise.schemas import CampaignPolicy
        from joulewise.idle_admission import evaluate_cpu_idle_admission
        from joulewise.adapters.powermetrics import idle_window_gpu_quality
        policy = CampaignPolicy.from_mapping(q.read(Path(__file__).resolve().parents[1] / "configs/campaign_policies/quiet_mac_p2_production.json"))
        for kind in ("cpu", "gpu", "combined-power"):
            record = self.admission(kind, {"none": True})
            evidence = record["admission_abort"]
            metadata = q.read(Path(evidence["metadata"]["path"]))
            admission = metadata["environment_admission"]
            reason = "idle environment admission failed after one retry"
            admission.update(failure=reason, attempts=[], idle_admission_extension={"sha256": policy.idle_admission_extension.sha256()},
                guard_observations=[{"phase": phase, "capture_skipped": False, "errors": {},
                                     "display_power_state": "all_asleep", "screensaver_engaged": False}
                                    for phase in ("before_attempt_1", "after_attempt_1", "before_attempt_2", "after_attempt_2")])
            rows = [{"clusters": [{"cpus": [{"idle_ratio": 0.1 if kind == "cpu" else 0.9, "down_ratio": 0.0}]}],
                     "gpu": {"idle_ratio": 0.1 if kind == "gpu" else 1.0, "freq_hz": 100.0},
                     "processor_combined_power_w": 2.0 if kind == "combined-power" else 0.1}] * 30
            evidence["telemetry"] = []
            for ordinal in (1, 2):
                gpu = idle_window_gpu_quality(rows)
                cpu = evaluate_cpu_idle_admission(rows, policy.idle_admission_extension.cpu_criteria,
                                                 gpu_admitted=gpu["idle_window_suspect"] is False)
                admission["attempts"].append({"attempt": ordinal, "baseline": gpu, "admitted": False,
                    "gpu_admitted": gpu["idle_window_suspect"] is False, "cpu_admission": cpu, "cpu_admission_enforced": True})
                path = Path(evidence["metadata"]["path"]).parent / ("rich_telemetry_idle.jsonl" if ordinal == 1 else "rich_telemetry_idle_attempt_2.jsonl")
                path.write_bytes(b"".join(readiness.render_json(row).replace(b"\n", b" ") + b"\n" for row in rows))
                evidence["telemetry"].append(q.reference(path))
            evidence["metadata"] = put(Path(evidence["metadata"]["path"]), metadata)
            evidence["summary"] = put(Path(evidence["summary"]["path"]), {"status": "failed", "failure_message": reason})
            path = Path(evidence["events"]["path"])
            path.write_bytes(readiness.render_json({"event_type": "failure", "phase": "idle_baseline", "message": reason}).replace(b"\n", b" ") + b"\n")
            evidence["events"] = q.reference(path)
            self.assertTrue(q.is_admission_abort(record))
            admission["attempts"][1]["cpu_admission"]["admitted"] = True
            evidence["metadata"] = put(Path(evidence["metadata"]["path"]), metadata)
            with self.assertRaisesRegex(q.HarvestRefusal, "cpu_replay_mismatch"):
                q.is_admission_abort(record)

    def test_every_per_run_environment_policy_guard_replays(self):
        from joulewise.schemas import CampaignPolicy
        from joulewise.environment import evaluate_environment_policy
        policy = CampaignPolicy.from_mapping(q.read(Path(__file__).resolve().parents[1] / "configs/campaign_policies/quiet_mac_p2_production.json"))
        clean = {"power_source": "AC Power", "power": {"external_connected": True}, "low_power_mode": False,
                 "display_power_state": "all_asleep", "screensaver_engaged": False, "thermal_pressure": "nominal"}
        for key in clean:
            record = self.admission("environment-" + key, {"none": True})
            evidence = record["admission_abort"]
            metadata = q.read(Path(evidence["metadata"]["path"]))
            snapshot = copy.deepcopy(clean)
            snapshot[key] = {"external_connected": False} if key == "power" else None
            evaluation = evaluate_environment_policy(snapshot, policy.environment_guard)
            self.assertFalse(evaluation["eligible"])
            evaluation["snapshot"] = snapshot
            reason = "critical per-run environment policy did not pass"
            metadata["environment_admission"].update(failure=reason, per_run_environment_evaluation=evaluation)
            metadata["environment_admission"]["guard_observations"][0].update(display_power_state="all_asleep", screensaver_engaged=False)
            evidence["metadata"] = put(Path(evidence["metadata"]["path"]), metadata)
            evidence["summary"] = put(Path(evidence["summary"]["path"]), {"status": "failed", "failure_message": reason})
            path = Path(evidence["events"]["path"])
            path.write_bytes(readiness.render_json({"event_type": "failure", "phase": "idle_baseline", "message": reason}).replace(b"\n", b" ") + b"\n")
            evidence["events"] = q.reference(path)
            self.assertTrue(q.is_admission_abort(record))
            evaluation["eligible"] = True
            evidence["metadata"] = put(Path(evidence["metadata"]["path"]), metadata)
            with self.assertRaisesRegex(q.HarvestRefusal, "environment_replay_mismatch"):
                q.is_admission_abort(record)


class WriterHistoryTests(unittest.TestCase):
    def setUp(self):
        from tests.test_v5_qualification_plan import PlanWriterTests
        self.fixture = PlanWriterTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root

    def prior(self, verdict="NULL", *, admission=False, physics=False):
        f = self.fixture
        chain = f.root / "prior-chain.zsh"; chain.write_text("export V5_QUALIFICATION_OCCURRENCE=s1\nexit 0\n")
        sidecar = f.root / "prior-chain.sha256"
        plan_path = f.root / "prior/night_plan.json"
        plan = bind_history_fixture(plan_path, SimpleNamespace(plan_id="prior", custody_root=str(plan_path.parent),
            chain_path=str(chain), chain_sha256_path=str(sidecar), pack_night={"pack_id": f.pack.name, "pack_root": str(f.pack)}),
            Path(f.input["block_archive_root"]))
        record = q.attempt_record(plan, plan_path, "s1", verdict=verdict, cause_codes=["named_launch_defect"] if verdict == "RECOVER" else ["chain_never_started"],
                                  cause_classes=["instrument_physics" if physics else "tooling"] if verdict == "RECOVER" else [])
        if admission:
            record.update(AttemptHistoryTests.admission(self, "prior", {"none": True}))
        ref = put(Path(plan.block_archive_root) / "attempts/prior/harvest.json", record)
        f.input["previous_attempt"] = ref
        return ref

    def test_writer_omission_and_wrong_sha_refuse_before_authorization(self):
        f = self.fixture
        del f.input["previous_attempt"]
        with self.assertRaisesRegex(ValueError, "inputs.keys"):
            f.write()
        self.assertFalse((f.custody / "authorization_record.json").exists())
        prior = self.prior()
        f.input["previous_attempt"] = dict(prior, sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "digest_mismatch"):
            f.write()
        self.assertFalse((f.custody / "authorization_record.json").exists())

    def test_null_to_fresh_s1_writer_binds_create_once_history(self):
        ref = self.prior()
        self.fixture.write()
        plan = q.read(self.fixture.output)
        auth = q.read(Path(plan["pack_night"]["authorization_record"]["path"]))
        self.assertEqual(auth["previous_attempt"], ref)
        self.assertEqual(plan["previous_attempt"], ref)
        self.assertEqual(plan["block_archive_root"], auth["block_archive_root"])
        self.assertFalse("end_state" in plan)

    def test_admission_abort_to_fresh_s1_writer_spends_no_s2(self):
        self.prior("RECOVER", admission=True)
        self.fixture.write()
        record = q.read(self.fixture.custody / "qualification-plan-record.json")
        self.assertEqual(record["occurrence"], "s1")
        self.assertNotIn("end_state", record)
        self.assertNotIn("s2_authority", record)

    def s2(self, *, physics=False):
        from scripts import write_v5_qualification_plan as writer
        f = self.fixture
        prior = self.prior("RECOVER", physics=physics)
        f.chain.write_text(f.chain.read_text().replace("V5_QUALIFICATION_OCCURRENCE=s1", "V5_QUALIFICATION_OCCURRENCE=s2"))
        f.bind_clock_sizing()
        cure = put(f.root / "cure.json", {"fixture": "R3 cure"})
        coverage = put(f.root / "coverage.json", {"fixture": "head coverage"})
        f.input["s2_authority"] = put(f.root / "s2-authority.json", {"schema": "joulewise.v5_qualification_s2_authority.v1",
            "new_plan_id": f.input["plan"]["plan_id"], "lead_approved": True, "s1_harvest": prior,
            "tooling_cause": "named_launch_defect", "r3_cure": cure, "head_coverage": coverage})
        return writer.write_qualification("s2", f.input, f.output)

    def test_tooling_recover_to_s2_writer_and_authenticated_plan_replay(self):
        self.s2()
        f = self.fixture
        plan = night_gate.NightPlan.from_mapping(q.read(f.output))
        record = q.attempt_record(plan, f.output, "s2", verdict="PASS", cause_codes=[], cause_classes=[])
        self.assertEqual(q.checked_history(record, plan)["s2_count"], 1)
        self.assertEqual(q.read(f.custody / "qualification-plan-record.json")["occurrence"], "s2")

    def test_s2_writer_after_physics_recover_refuses(self):
        with self.assertRaisesRegex(q.HarvestRefusal, "named_tooling_recover"):
            self.s2(physics=True)
        self.assertFalse(self.fixture.output.exists())

    def test_second_s2_writer_refuses_before_authorization(self):
        from scripts import write_v5_qualification_plan as writer
        f = self.fixture
        root = Path(f.input["block_archive_root"])
        first = put(root / "attempts/tooling/harvest.json", attempt("tooling", {"none": True},
            verdict="RECOVER", cause_codes=["named_launch_defect"], cause_classes=["tooling"]))
        aborted = AttemptHistoryTests.admission(self, "aborted-s2", first)
        aborted["occurrence"] = "s2"
        second = put(root / "attempts/aborted-s2/harvest.json", aborted)
        prior = put(root / "attempts/fresh-tooling/harvest.json", attempt("fresh-tooling", second,
            verdict="RECOVER", cause_codes=["named_launch_defect"], cause_classes=["tooling"]))
        f.input["previous_attempt"] = prior
        f.input["s2_authority"] = put(f.root / "unused-authority.json", {})
        f.chain.write_text(f.chain.read_text().replace("V5_QUALIFICATION_OCCURRENCE=s1", "V5_QUALIFICATION_OCCURRENCE=s2"))
        f.bind_clock_sizing()
        with self.assertRaisesRegex(q.HarvestRefusal, "attempt_history_second_s2"):
            writer.write_qualification("s2", f.input, f.output)
        self.assertFalse((f.custody / "authorization_record.json").exists())

    def test_s2_runtime_observation_and_control_order_bind_the_written_chain(self):
        from scripts import run_night as driver, check_v5_arm_abort as checker
        self.s2()
        f = self.fixture
        plan = night_gate.NightPlan.from_mapping(q.read(f.output))
        self.assertTrue(driver._s1_observation_enabled(plan))
        boot = "12345678-1234-5678-9234-567812345678"
        inputs = f.custody / plan.pack_night["pack_id"] / "arm_readiness.t0.inputs"
        for filename in driver.t0_author._CAPTURE_FILES.values():
            put(inputs / filename, {"boot_session_id": boot, "started_monotonic_ns": 1000})
        controls = {}
        for label in ("a1", "a2"):
            controls[label + "_control"] = put(f.root / (label + "-expired.json"), {
                "schema_version": checker.CONTROL_SCHEMA, "occurrence": label, "verdict": "PASS",
                "refusal_reason_code": "readiness_record_expired", "boot_session_id": boot,
                "checked_monotonic_ns": 999, "absence": {key: True for key in checker.ABSENCE_KEYS}})
        record = q.read(f.custody / "qualification-plan-record.json")
        record["prerequisites"].update(controls)
        with mock.patch.object(readiness, "_current_boot_session_id", return_value=boot):
            driver._admit_qualification_control_order(plan, record)
            for occurrence in ("a1", "a2", "s1"):
                with self.subTest(occurrence=occurrence), self.assertRaisesRegex(night_gate.PackNightRefusal, "occurrence binding"):
                    driver._admit_qualification_control_order(plan, dict(record, occurrence=occurrence))
            path = Path(controls["a2_control"]["path"])
            control = q.read(path)
            control["checked_monotonic_ns"] = 1000
            record["prerequisites"]["a2_control"] = put(path, control)
            with self.assertRaisesRegex(night_gate.PackNightRefusal, "prior expiry"):
                driver._admit_qualification_control_order(plan, record)

    def test_fresh_attempt_go_uses_frozen_calibration_identity(self):
        from scripts import run_night as driver
        from tests.test_run_night import ProbeSource, BOOT_UUID
        self.s2()
        f = self.fixture
        plan = night_gate.NightPlan.from_mapping(q.read(f.output))
        prepared = driver._prepare_pack_night(plan, f.output, f.output.read_bytes())
        arm = {"status": "PASS", "arm_disposition": "GO", "receipt_id": "arm-0001",
               "boot_session_id": BOOT_UUID, "valid_until_monotonic_ns": 10**18,
               "pack": {"pack_root": str(f.pack), "pack_id": f.pack.name,
                        "pack_sha256": plan.pack_night["pack_sha256"], "plan_id": "frozen-calibration"},
               "reviewed_main": {"head_commit": f.head}, "arm_context": f.input["arm_context"]}
        arm_ref = put(f.custody / "native-arm.json", arm)
        state = {"path": Path(arm_ref["path"]), "arm": arm, "sha256": arm_ref["sha256"]}
        refs = {"window_chain": q.reference(f.chain), "window_environment": put(f.root / "window.env", {}),
                "launch_manifest": put(f.root / "launch-manifest.json", {})}
        probes = replace(ProbeSource(1001).probes(), checkout_head=lambda: f.head)
        receipt = night_gate.Receipt(night_gate.SCHEMA, "TRANSACTION_PACK", plan.plan_id, "GO",
            tuple(night_gate.ConditionRow(f"C{i}", "PASS", None, (),
                {"boot_session_uuid": BOOT_UUID} if i == 4 else {}) for i in range(1, 6)), None, 1)
        (f.custody / "night").mkdir(exist_ok=True)
        # Native plan, authority, chain and context authentication remain real.
        # ARM/T0 machine replay and launch inventory are explicit fixture seams.
        with mock.patch.object(readiness, "_pack_record", return_value={"plan_id": "frozen-calibration"}), \
             mock.patch.object(readiness, "_verify_arm_receipt"), \
             mock.patch.object(readiness, "_current_boot_session_id", return_value=BOOT_UUID), \
             mock.patch.object(driver, "_pack_rehearsal_roots"), \
             mock.patch.object(driver, "_pack_launch_references", return_value=refs), \
             mock.patch.object(driver, "_pack_evidence", return_value=[]):
            driver._produce_pack_go(plan, f.output, f.output.read_bytes(), prepared, state, receipt, probes)
            go_path = f.custody / "night/go_receipt.json"
            go = q.read(go_path)
            self.assertEqual(go["plan_id"], plan.plan_id)
            self.assertEqual(go["authorization"]["attempt_id"], plan.plan_id + "/2")
            go_path.unlink()
            (f.custody / "night/go-census.json").unlink()
            arm["pack"]["plan_id"] = plan.plan_id
            state["sha256"] = put(state["path"], arm)["sha256"]
            with self.assertRaisesRegex(night_gate.PackNightRefusal, "arm_receipt.pack.plan_id"):
                driver._produce_pack_go(plan, f.output, f.output.read_bytes(), prepared, state, receipt, probes)
            self.assertFalse(go_path.exists())

    def test_s2_assembly_and_desk_consume_authenticated_occurrence(self):
        from joulewise import t0_rehearsal as t0
        from scripts import produce_t0_rehearsal_bundle as producer, v5_s1_desk_closeout as desk
        from tests.test_t0_rehearsal import FixtureBuilder
        f = self.fixture
        f.input["prerequisites"]["g10_control"] = put(f.root / "positive.json", {"schema_version": t0.POSITIVE_CONTROL_SCHEMA})
        self.s2()
        plan = night_gate.NightPlan.from_mapping(q.read(f.output))
        record_path = f.custody / "qualification-plan-record.json"
        record = q.read(record_path)
        native = FixtureBuilder(f.root / "native-go-fixture").build()
        go = producer.read(native / "night/go_receipt.json")
        go.update(purpose="G2B_SHAKEDOWN", plan_id=plan.plan_id, plan_sha256=q.sha(f.output),
                  repo_head=f.head, window_chain_sha256=q.sha(f.chain))
        go["authorization"].update(purpose="G2B_SHAKEDOWN", claim_eligible=False)
        put(f.custody / "night/go_receipt.json", go)
        put(f.custody / "night/observation-origin.json", {
            "schema_version": "joulewise.t0_rehearsal_observation_origin.v1",
            "proof_scope": producer.QUALIFICATION_OBSERVED, "boot_session_id": go["boot_session_id"],
            "plan": q.reference(f.output), "standdown": q.reference(f.confirm),
            "producer": record["prerequisites"]["observation_producers"]["driver"]})
        inputs = dict(positive_control=record["prerequisites"]["g10_control"]["path"],
                      positive_sha256=record["prerequisites"]["g10_control"]["sha256"],
                      positive_artifacts=[ref["path"] for ref in record["prerequisites"]["g10_artifacts"]])
        # Stop at the next real admission surface; this isolates the occurrence
        # adapter without claiming a complete physical G10/STOP lifecycle.
        with mock.patch.object(q, "g10_sources", side_effect=ValueError("next G10 admission")) as replay:
            with self.assertRaisesRegex(ValueError, "next G10 admission"):
                producer.assemble(f.custody, **inputs)
            self.assertEqual(replay.call_count, 1)
            put(record_path, dict(record, occurrence="s1"))
            with self.assertRaisesRegex(ValueError, "occurrence differs"):
                producer.assemble(f.custody, **inputs)
            self.assertEqual(replay.call_count, 1)
        put(record_path, record)
        put(f.custody / go["pack_id"] / "arm_readiness.receipts" / (go["arm_receipt"]["receipt_id"] + ".json"),
            {"fixture": "wrong native ARM digest"})
        with mock.patch.object(q, "load_plan", return_value=plan), mock.patch.dict(desk.os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "desk ARM digest mismatch"):
                desk.closeout(f.output)
            put(record_path, dict(record, occurrence="s1"))
            with self.assertRaisesRegex(ValueError, "occurrence binding mismatch"):
                desk.closeout(f.output)


class NullReservationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.pin = {"ledger_schema": ledger.LEDGER_SCHEMA, "sequence": 0, "head_digest": ledger.GENESIS_DIGEST}
        self.identity = {"session_id": "session", "window_id": "window", "plan_id": "plan",
                         "plan_sha256": "a" * 64, "evidence_root_id": "evidence", "runs_root": str(self.root / "runs")}
        self.slots = {role: {"attempt_id": "attempt-" + role, "custody_locator": str(self.root / "runs/instrument_validation" / ("attempt-" + role)),
                    "identity_epoch": {key: "fixture" for key in ledger.IDENTITY_EPOCH_FIELDS},
                    "t1_bindings": {key: "fixture" for key in ledger.T1_FIELDS},
                    "expected_time_role": role} for role in ("pre", "post")}
        self.row = ledger._new_bracket_session_record(sequence=1, predecessor_digest=ledger.GENESIS_DIGEST,
            event=ledger.BRACKET_SESSION_OPEN_EVENT, session_identity=self.identity, fields={"slots": self.slots})
        self.live = self.root / "ledger.jsonl"; self.live.write_bytes(b"")
        pin = self.root / "pin.json"; put(pin, self.pin)
        kwargs = dict(self.identity); kwargs["runs_root"] = Path(kwargs["runs_root"])
        self.row = ledger._jsonable(ledger.append_bracket_session_receipt(self.live, **kwargs, slots=self.slots,
            head_pin_path=pin, require_committed_pin=False, repo_root=self.root))
        self.raw = self.live.read_bytes()

    def test_native_reservation_unit_validates(self):
        self.assertEqual(restore.validate_tail(b"", self.raw, self.pin, self.row), self.row)

    def test_two_row_tail_and_wrong_seed_or_reservation_refuse(self):
        with self.assertRaisesRegex(q.HarvestRefusal, "not_one_reservation_unit"):
            restore.validate_tail(b"", self.raw + self.raw, self.pin, self.row)
        bad = copy.deepcopy(self.row); bad["session_id"] = "different"
        with self.assertRaisesRegex(q.HarvestRefusal, "not_attempt_reservation"):
            restore.validate_tail(b"", self.raw, self.pin, bad)
        pin = dict(self.pin, sequence=1)
        with self.assertRaisesRegex(q.HarvestRefusal, "seed_not_pinned"):
            restore.validate_tail(b"", self.raw, pin, self.row)

    def test_two_open_rows_are_not_the_native_reservation_unit(self):
        row = ledger.canonical_json_bytes(self.row) + b"\n"
        with self.assertRaisesRegex(q.HarvestRefusal, "not_attempt_reservation"):
            restore.validate_tail(b"", row + row, self.pin, self.row)

    def test_native_reservation_has_two_rows_and_replays(self):
        live = self.root / "ledger.jsonl"; live.write_bytes(b"")
        pin_path = self.root / "pin.json"; put(pin_path, self.pin)
        kwargs = dict(self.identity); kwargs["runs_root"] = Path(kwargs["runs_root"])
        row = ledger.append_bracket_session_receipt(live, **kwargs, slots=self.slots,
            head_pin_path=pin_path, require_committed_pin=False, repo_root=self.root)
        raw = live.read_bytes()
        rows = [readiness.parse_json_bytes(line) for line in raw.splitlines()]
        self.assertEqual([record["event"] for record in rows], [ledger.APPEND_INTENT_EVENT, ledger.BRACKET_SESSION_OPEN_EVENT])
        self.assertEqual(restore.validate_tail(b"", raw, self.pin, dict(row)), dict(row))

    def test_null_restore_after_chain_started_refuses_even_for_symlink(self):
        plan = SimpleNamespace(plan_id="plan", custody_root=str(self.root))
        harvest = {"schema": q.ATTEMPT_HARVEST_SCHEMA, "verdict": "NULL", "plan_id": "plan", "plan_sha256": "a" * 64}
        restore.require_null(harvest, plan, "a" * 64)
        started = self.root / "night/chain.started"
        started.parent.mkdir()
        started.write_bytes(b"{}\n")
        with self.assertRaisesRegex(q.HarvestRefusal, "chain_started"):
            restore.require_null(harvest, plan, "a" * 64)
        started.unlink(); started.symlink_to(self.root / "missing")
        with self.assertRaisesRegex(q.HarvestRefusal, "chain_started"):
            restore.require_null(harvest, plan, "a" * 64)

    def test_recover_or_wrong_plan_never_qualifies_as_null(self):
        plan = SimpleNamespace(plan_id="plan", custody_root=str(self.root))
        harvest = {"schema": q.ATTEMPT_HARVEST_SCHEMA, "verdict": "RECOVER", "plan_id": "plan", "plan_sha256": "a" * 64}
        with self.assertRaisesRegex(q.HarvestRefusal, "requires_attempt_null"):
            restore.require_null(harvest, plan, "a" * 64)

    def restore_fixture(self):
        from tests.test_v5_qualification_plan import PlanWriterTests
        fixture = PlanWriterTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        frozen = put(fixture.pack / "calibration_plan.json", {"plan_id": fixture.custody.name})
        subprocess.run(["git", "-C", str(fixture.repo), "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(fixture.repo), "-c", "user.name=Fixture", "-c",
                        "user.email=fixture@example.invalid", "commit", "-qm", "NULL restore fixture"],
                       check=True, capture_output=True)
        head = subprocess.check_output(["git", "-C", str(fixture.repo), "rev-parse", "HEAD"], text=True).strip()
        fixture.input["head"] = head
        fixture.input["plan"].update(repo_head=head, measurement_head=head)
        digest = readiness.committed_pack_tree_sha256(fixture.pack)
        fixture.input["pack"]["sha256"] = fixture.input["authorization"]["pack_sha256"] = digest
        fixture.write()
        plan = night_gate.NightPlan.from_mapping(q.read(fixture.output))
        context = fixture.input["arm_context"]
        identity = {**self.identity, "plan_id": plan.plan_id, "plan_sha256": frozen["sha256"],
                    "session_id": context["bracket_session_id"], "runs_root": context["claim_runs_root"]}
        slots = copy.deepcopy(self.slots)
        for role in ("pre", "post"):
            slots[role]["attempt_id"] = context[role + "_attempt_id"]
            slots[role]["custody_locator"] = str(Path(identity["runs_root"]) / "instrument_validation" / slots[role]["attempt_id"])
        row = ledger._new_bracket_session_record(sequence=1, predecessor_digest=ledger.GENESIS_DIGEST,
            event=ledger.BRACKET_SESSION_OPEN_EVENT, session_identity=identity, fields={"slots": slots})
        live = fixture.root / "attempt-ledger.jsonl"; live.write_bytes(b"")
        pin_path = fixture.root / "native-pin.json"; put(pin_path, self.pin)
        kwargs = dict(identity); kwargs["runs_root"] = Path(kwargs["runs_root"])
        row = ledger._jsonable(ledger.append_bracket_session_receipt(live, **kwargs, slots=slots,
            head_pin_path=pin_path, require_committed_pin=False, repo_root=fixture.repo))
        raw = live.read_bytes()
        seed = fixture.root / "seed-ledger.jsonl"; seed.write_bytes(b"")
        pin = fixture.root / "head-pin.json"; put(pin, self.pin)
        argv = ["/fixture/python", str(fixture.repo / "scripts/reserve_calibration_window_bracket.py"),
                "--execute", "--ledger", str(live), "--head-pin", str(pin)]
        for key, value in identity.items():
            argv.extend(["--" + key.replace("_", "-"), value])
        for role in ("pre", "post"):
            argv.extend(["--" + role + "-attempt-id", context[role + "_attempt_id"]])
        capture = plan.pack_night["pack_id"] + "/arm_readiness.t0.inputs/ledger-reservation.json"
        put(fixture.custody / capture, {"schema_version": restore.COMMAND_CAPTURE_SCHEMA,
            "step_id": "ledger-reservation", "exit_code": 0, "argv": argv,
            "stdout": readiness.render_json({"status": "reserved", "receipt": row}).decode()})
        courier = fixture.custody / "night/courier.sent"; courier.parent.mkdir()
        courier.write_bytes(b"fixture-only courier closure\n")
        harvest = put(Path(plan.block_archive_root) / "attempts" / plan.plan_id / "harvest.json",
                      q.attempt_record(plan, fixture.output, "s1", verdict="NULL", cause_codes=["chain_never_started"], cause_classes=[]))
        return fixture, live, seed, pin, harvest, raw

    def test_native_restore_copies_create_once_leaves_pin_and_replays_record(self):
        fixture, live, seed, pin, harvest, raw = self.restore_fixture()
        pin_before = pin.read_bytes()
        output = fixture.custody / "null-reservation-restore.json"
        reference = restore.restore(q.reference(fixture.output), harvest, q.reference(seed), output=output)
        self.assertEqual(live.read_bytes(), b"")
        self.assertEqual(pin.read_bytes(), pin_before)
        self.assertEqual((fixture.custody / "null-reservation-ledger.jsonl").read_bytes(), raw)
        self.assertEqual(restore.verify_restore(reference, harvest, restored_ledger=q.reference(live))["head_pin"], q.reference(pin))
        live.write_bytes(raw)
        with self.assertRaisesRegex(q.HarvestRefusal, "custody_exists"):
            restore.restore(q.reference(fixture.output), harvest, q.reference(seed), output=output)
        self.assertEqual(live.read_bytes(), raw)

    def test_two_row_restore_preserves_live_ledger_pin_and_absence_of_output(self):
        fixture, live, seed, pin, harvest, raw = self.restore_fixture()
        live.write_bytes(raw + raw)
        pin_before = pin.read_bytes()
        output = fixture.custody / "null-reservation-restore.json"
        with self.assertRaisesRegex(q.HarvestRefusal, "not_one_reservation_unit"):
            restore.restore(q.reference(fixture.output), harvest, q.reference(seed), output=output)
        self.assertEqual(live.read_bytes(), raw + raw)
        self.assertEqual(pin.read_bytes(), pin_before)
        self.assertFalse(output.exists())
        self.assertFalse((fixture.custody / "null-reservation-ledger.jsonl").exists())

    def test_next_attempt_requires_and_authenticates_restore_without_pooling_ledger_bytes(self):
        fixture, live, seed, pin, harvest, raw = self.restore_fixture()
        restored = restore.restore(q.reference(fixture.output), harvest, q.reference(seed),
                                   output=fixture.custody / "null-reservation-restore.json")
        old_plan = night_gate.NightPlan.from_mapping(q.read(fixture.output))
        chain = fixture.root / "fresh-chain.zsh"
        chain.write_text(f"export CALIBRATION_LEDGER={live}\nexport LEDGER_HEAD_PIN={pin}\nexit 0\n")
        path = fixture.root / "fresh/night_plan.json"
        plan = bind_history_fixture(path, SimpleNamespace(plan_id="fresh", custody_root=str(path.parent),
            chain_path=str(chain), chain_sha256_path=str(fixture.root / "fresh-chain.sha256"),
            pack_night={"pack_id": fixture.pack.name, "pack_root": str(fixture.pack)}),
            Path(old_plan.block_archive_root), previous=harvest)
        with self.assertRaisesRegex(q.HarvestRefusal, "restore_required"):
            q.verify_attempt_restore(plan, writer=True)
        value = q.read(path)
        value["null_reservation_restore"] = restored
        auth_path = Path(value["pack_night"]["authorization_record"]["path"])
        auth = q.read(auth_path); auth["null_reservation_restore"] = restored
        value["pack_night"]["authorization_record"] = put(auth_path, auth)
        put(path, value)
        plan = night_gate.NightPlan.from_mapping(value)
        q.verify_attempt_restore(plan, writer=True)
        current = q.attempt_record(plan, path, "s1", verdict="NULL", cause_codes=["chain_never_started"], cause_classes=[])
        self.assertEqual(q.checked_history(current, plan)["harvests"], [harvest])
        # Later harvesting replays the preserved seed and dropped native unit;
        # it does not pool the restored attempt ledger with fresh reservation.
        live.write_bytes(raw)
        q.verify_attempt_restore(plan)
        with self.assertRaisesRegex(q.HarvestRefusal, "digest_mismatch"):
            q.verify_attempt_restore(plan, writer=True)
        saved = fixture.custody / "null-reservation-ledger.jsonl"
        saved.write_bytes(saved.read_bytes() + b"{}\n")
        with self.assertRaisesRegex(q.HarvestRefusal, "digest_mismatch"):
            q.verify_attempt_restore(plan)


if __name__ == "__main__":
    unittest.main()
