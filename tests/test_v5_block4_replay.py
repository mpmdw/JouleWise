"""DESK ONLY: recovery/custody replays and production-component integration.

These tests do not certify a full success replay. The existing positive ARM
and finalizer factories replace nonphysical pack/ARM semantics; they cannot be
combined and called a physical-seams-only producer-to-two-verdict PASS. Each
use of those factories below is explicitly a component control.
"""
from pathlib import Path
from types import SimpleNamespace
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from joulewise import arm_readiness as ar, measurement_liveness as ml, night_gate
from joulewise import t0_rehearsal as t0, v5_qualification as q
from joulewise.night_plan_writer import write_night_plan
from scripts import harvest_v5_g2b_window as g2b, run_night as driver
from scripts import harvest_v5_qualification as qualification
from scripts import produce_t0_rehearsal_bundle as producer


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(ar.render_json(value))
    return q.reference(path)


class StartedOccurrenceReplayTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.pack = self.root / "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
        self.pack.mkdir()
        source = Path(__file__).parent / "fixtures/v5_qualification_harvest/committed_gamma"
        for name in ("calibration_plan.json", "plan_tree.json"):
            shutil.copyfile(source / name, self.pack / name)
        # Real Git custody/digest; no pack-digest authenticator is mocked.
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "add", self.pack.name], check=True)
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=Fixture", "-c",
                        "user.email=fixture@example.invalid", "commit", "-qm", "synthetic desk pack custody"], check=True)
        head = subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()
        digest = ar.committed_pack_tree_sha256(self.pack)
        self.night_custody = self.root / "night-custody"; self.night = self.night_custody / "night"
        self.night.mkdir(parents=True)
        self.custody = self.root / "g2b-custody"; self.runs = self.custody / "runs"; self.runs.mkdir(parents=True)
        self.bound = self.root / "bound"; self.bound.mkdir()
        chain = self.root / "chain.zsh"; chain.write_text("#!/bin/zsh\nexit 0\n")
        sidecar = self.root / "chain.sha256"; sidecar.write_bytes(ar.gnu_sidecar(q.sha(chain), chain.name))
        table = self.root / "table.json"; put(table, {})
        auth = put(self.night_custody / "authorization_record.json", {"purpose": "G2B_SHAKEDOWN",
            "attempt_id": "s1-synthetic/1", "claim_eligible": False, "permitted_blocks": 1,
            "pack_sha256": digest, "permitted_chain_sha256": q.sha(chain), "authority": "D-171 §3"})
        confirmation = put(self.night_custody / "confirmation.json", {"table_path": str(table),
            "table_sha256": q.sha(table), "transcript_sha256": "b" * 64,
            "confirmed_at": {"epoch_s": 0., "iso8601_utc": "1970-01-01T00:00:00.000000Z"}})
        self.plan = night_gate.NightPlan.from_mapping({"schema": night_gate.PACK_PLAN_SCHEMA, "schema_version": 3,
            "plan_id": "s1-synthetic", "receipt_class": "TRANSACTION_PACK", "t0_epoch_s": 0.,
            "window_max_s": 3600, "authored_epoch_s": 0., "repo_head": head, "measurement_root": str(g2b.ROOT),
            "measurement_head": head, "chain_path": str(chain), "chain_sha256_path": str(sidecar),
            "custody_root": str(self.night_custody), "registration_path": None,
            "pack_night": {"pack_id": self.pack.name, "pack_root": str(self.pack), "pack_sha256": digest,
                "attempt_ordinal": 1, "authorization_record": auth, "confirmation_record": confirmation}})
        plan_path = write_night_plan(self.night_custody / "night_plan.json", self.plan, create_once=True)
        # Mock seam: courier delivery acknowledgement, no external transport.
        put(self.night / "courier.sent", {"synthetic_delivery_ack": True})
        process = SimpleNamespace(pid=54321)
        # Mock seam: PID/start identity only; production driver writers execute.
        with mock.patch.object(driver, "observe_identity", return_value=ml.Identity("LIVE", "Mon Oct 5 01:02:03 2026")):
            driver._write_launch_pending(process, self.night, self.plan)
            descriptor = driver._claim_chain_start(self.night)
            driver._complete_chain_start(descriptor, process, self.night)
        driver._record_chain_exit(self.night, 9)
        self.inputs = {"schema": g2b.INPUT_SCHEMA, "occurrence": "s1", "plan": q.reference(plan_path),
            "custody_root": str(self.custody), "policy": put(self.root / "policy.json", {}),
            "acceptance": put(self.root / "acceptance.json", {}), "bound_runs_root": str(self.bound),
            "auxiliary_bundle_ids": [], "bound_bundle_ids": []}
        self.input_path = self.root / "inputs.json"
        self.args = SimpleNamespace(inputs=self.input_path, inputs_sha256=None, archive_root=self.root / "harvest",
            scratch_root=self.root, prepare_desk=False, previous_harvest=None)

    def harvest(self):
        if not self.input_path.exists():
            put(self.input_path, self.inputs)
        self.args.inputs_sha256 = q.sha(self.input_path)
        return g2b.harvest(self.args, now=lambda: 999999.)  # Mock seam: elapsed completion boundary.

    def test_started_crash_archives_and_recovers_without_success_only_records(self):
        before = q.tree_hash(self.night_custody)
        record = self.harvest()
        self.assertEqual(record["verdict"], "RECOVER")
        self.assertIn("started_chain_crashed", record["cause_codes"])
        self.assertIn("terminal_boundary_missing", record["cause_codes"])
        self.assertEqual(q.tree_hash(self.night_custody), before)
        self.assertTrue((self.args.archive_root / "withheld/sources/night-custody/night/chain.started").exists())

    def test_named_pre_science_crash_and_partial_science_have_distinct_dispositions(self):
        started = q.read(self.night / "chain.started")["monotonic_ns"]
        self.inputs["pre_science_tooling_failure"] = put(self.root / "failure.json", {
            "schema": "joulewise.v5_pre_science_tooling_failure.v1", "plan_id": self.plan.plan_id,
            "cause_code": "night_chain_launch_failed", "cause_class": "tooling", "monotonic_ns": started + 1,
            "seam": "launch"})
        record = self.harvest()
        self.assertEqual(record["recovery_classification"], "recover_no_science")
        self.assertFalse(record["consumes_s2"])
        self.assertFalse(record["s2_eligible"])
        self.assertFalse(record["end_state"])
        self.args.archive_root = self.root / "partial-harvest"
        (self.runs / q.read(self.pack / "plan_tree.json")["science"][0]["run_id"]).mkdir()
        record = self.harvest()
        self.assertEqual(record["verdict"], "RECOVER")
        self.assertNotIn("recovery_classification", record)
        self.assertIn("started_chain_incomplete", record["cause_codes"])

    def test_external_event_source_is_retained_on_identical_byte_reharvest(self):
        for name in ("terminal_boundary", "go", "consumption", "battery_boundaries"):
            # Deliberately invalid success artifacts: this is a REFUSED replay
            # custody control, not fabricated positive producer evidence.
            self.inputs[name] = put(self.root / (name + ".json"), {})
        put(self.runs / "bracket-binding.json", {})
        (self.runs / "whole-window-verdict.json").write_text("{}\n")
        self.inputs["desk_producer_events"] = put(self.root / "desk-events.json", {"schema": g2b.ORDER_SCHEMA})
        first = self.harvest()
        self.assertEqual(first["verdict"], "REFUSED")
        self.args.previous_harvest = self.args.archive_root
        self.args.archive_root = self.root / "reharvest"
        second = self.harvest()
        self.assertEqual(second["verdict"], "REFUSED")
        a, b = [q.read(root / "replay-locators.json") for root in (self.args.previous_harvest, self.args.archive_root)]
        self.assertEqual([(r["name"], r["original_path"], r["inventory"]) for r in a["sources"]],
                         [(r["name"], r["original_path"], r["inventory"]) for r in b["sources"]])
        self.assertIn("desk-producer-events", {r["name"] for r in b["sources"]})
        self.args.archive_root = self.root / "changed"
        (self.root / "desk-events.json").write_text("changed")
        with self.assertRaisesRegex(q.HarvestRefusal, "digest_mismatch"):
            self.harvest()

    def test_observation_fault_fails_only_qualification_without_end_state_or_g2b_cause(self):
        from joulewise import battery_float
        from tests.test_battery_float import raw, UPDATE
        observations = {}
        for site in ("arm", "publication", "t0"):
            raw_path = self.root / (site + ".ioreg"); raw_path.write_bytes(raw())
            # Mock seam: recorded battery query bytes and clocks, no ioreg.
            value, _ = battery_float.observe(phase=site, plan_id=self.plan.plan_id, wall_time_s=UPDATE + 1,
                monotonic_ns=lambda: 1, runner=lambda argv: subprocess.CompletedProcess(argv, 0, raw_path.read_bytes(), b""))
            observations[site] = {"record": put(self.root / (site + ".json"), value), "raw": q.reference(raw_path)}
        boundary = self.root / "boundaries.json"
        put(boundary, {"schema": "joulewise.v5_qualification_battery_boundaries.v1", "plan_id": self.plan.plan_id,
                       "observations": observations})
        driver._qualification_observe(self.night, "hid", lambda: (_ for _ in ()).throw(OSError("synthetic producer fault")))
        args = SimpleNamespace(plan=self.night_custody / "night_plan.json", archive_root=self.root / "qualification",
            battery_evidence=boundary, battery_evidence_sha256=q.sha(boundary), replay_source=[], previous_harvest=None)
        verdict = qualification.harvest(args, now=lambda: 999999.)
        self.assertEqual(verdict["verdict"], "FAIL")
        self.assertEqual(verdict["cause_codes"], ["qualification_observation_producer_fault"])
        self.assertFalse(verdict["end_state"])
        structural = self.harvest()
        self.assertNotIn("qualification_observation_producer_fault", structural["cause_codes"])
        self.assertIn("started_chain_crashed", structural["cause_codes"])


class PendingIdentityReplayTests(unittest.TestCase):
    def test_driver_and_harvest_agree_on_reuse_without_probing_replacement_group(self):
        with tempfile.TemporaryDirectory() as directory:
            night = Path(directory).resolve()
            plan = SimpleNamespace(plan_id="s1-reuse")
            old, new = ml.Identity("LIVE", "Mon Oct 5 01:02:03 2026"), ml.Identity("LIVE", "Mon Oct 5 09:08:07 2026")
            with mock.patch.object(driver, "observe_identity", return_value=old):
                driver._write_launch_pending(SimpleNamespace(pid=54321), night, plan)
            with mock.patch.object(driver, "observe_identity", return_value=new), mock.patch.object(driver.os, "killpg") as syscall:
                self.assertIsNone(driver._pending_launch_refusal(night))
                self.assertTrue(q.group_clear(night, plan_id=plan.plan_id, observer=lambda pid: new, killpg=syscall))
                syscall.assert_not_called()
                self.assertFalse(q.group_clear(night, plan_id=plan.plan_id, observer=lambda pid: old, killpg=syscall))
                self.assertFalse(q.group_clear(night, plan_id=plan.plan_id, observer=lambda pid: ml.Identity("DEAD"), killpg=syscall))
            self.assertFalse((night / "launch.resolved").exists())


class DeskLifecycleComponentReplayTests(unittest.TestCase):
    def test_real_closeout_producer_feeds_complete_g9_and_all_stage_defects_fail(self):
        # This factory's synthetic config/authentication patches are explicitly
        # nonphysical component seams. It is not the requested full replay.
        from tests.test_v5_s1_desk_closeout import DeskCloseoutTests
        from tests.test_t0_rehearsal import fixture_bundle
        fixture = DeskCloseoutTests(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        night, stage_dir = fixture.night, fixture.stage_dir
        # The real desk path assembles this derived record after close-out.
        # Remove the factory's preassembled record before its immutable census.
        (fixture.custody / "records/lifecycle.json").unlink()
        put(night / "chain.started", {"monotonic_ns": 1, "pid": 54321})
        consumed = next(fixture.custody.rglob("*.consumed.json"))
        source = fixture.claim / "science-fixture"
        retained = fixture.custody / "records/replay-capture"
        metadata = producer.copy_record(source / "metadata.json", retained / "metadata.json")
        sampler = producer.copy_record(source / "powermetrics.raw.txt", retained / "powermetrics.raw.txt")
        values = {"launch": {"source": producer.reference(night / "chain.started")},
            "capability_consumption": {"source": producer.reference(consumed)},
            "capture": {"artifacts": [producer.reference(metadata)],
                        "sampler_artifacts": [producer.reference(sampler)]}}
        for name, facts in values.items():
            put(stage_dir / (name + ".json"), {"schema_version": t0.QUALIFICATION_STAGE_SCHEMA,
                "stage_id": name, "monotonic_ns": 2, **facts})
        self.assertEqual(fixture.close()["status"], "COMPLETE")
        life = {"schema_version": t0.QUALIFICATION_LIFECYCLE_SCHEMA,
            "stages": [{"stage_id": name, "status": "COMPLETE", "evidence": producer.reference(stage_dir / (name + ".json"))}
                       for name in t0._LIFECYCLE_STAGES], "operator_actions_at_t0": 0, "human_interventions": []}
        target = fixture.custody / "records/lifecycle.json"; put(target, life)
        gate = t0.evaluate_g9(fixture_bundle(fixture.custody))
        self.assertEqual(gate.status.value, "PASS", gate.message)
        for row in life["stages"]:
            row["status"] = "MISSING"; put(target, life)
            self.assertEqual(t0.evaluate_g9(fixture_bundle(fixture.custody)).status.value, "FAIL", row["stage_id"])
            row["status"] = "COMPLETE"
            old = row["evidence"]["sha256"]; row["evidence"]["sha256"] = "0" * 64; put(target, life)
            self.assertEqual(t0.evaluate_g9(fixture_bundle(fixture.custody)).status.value, "FAIL", row["stage_id"])
            row["evidence"]["sha256"] = old


if __name__ == "__main__":
    unittest.main()
