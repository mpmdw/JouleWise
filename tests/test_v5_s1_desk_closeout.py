"""Post-STOP desk observations on fixture bytes; no hardware qualification."""
from pathlib import Path
import shutil
from types import SimpleNamespace
import subprocess
import tempfile
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, t0_rehearsal as t0
from scripts import produce_t0_rehearsal_bundle as producer
from scripts import v5_s1_desk_closeout as desk
from tests.test_network_time_off import receipt
from tests.test_t0_rehearsal import FixtureBuilder


class DeskCloseoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.custody = FixtureBuilder(self.base).build()
        self.night = self.custody / "night"
        self.stage_dir = self.night / "rehearsal-lifecycle"; self.stage_dir.mkdir()
        self.measurement = self.base / "measurement"; self.measurement.mkdir()
        for relative in ("scripts/backup_runs.sh", desk.RUNSHEET):
            path = self.measurement / relative; path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(producer.REPO_ROOT / relative, path)
        self.pack = self.measurement / "pack"; self.pack.mkdir()
        (self.pack / "config.json").write_text('{"run_id":"fixture"}\n')
        subprocess.run(["git", "init", "-q", str(self.measurement)], check=True)
        subprocess.run(["git", "-C", str(self.measurement), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.measurement), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "-qm", "fixture-only desk sources"], check=True)
        self.head = subprocess.check_output(["git", "-C", str(self.measurement), "rev-parse", "HEAD"], text=True).strip()
        self.sources = {"custody": str(self.custody)}
        for role in ("claim_runs", "bound_runs"):
            root = self.base / role; root.mkdir()
            self.sources[role] = str(root)
            bundle = root / ("science-fixture" if role == "claim_runs" else "bound-fixture"); bundle.mkdir()
            (bundle / "metadata.json").write_bytes(readiness.render_json({"run_id": bundle.name}))
            (bundle / "powermetrics.raw.txt").write_text("fixture sampler bytes")
        self.claim = Path(self.sources["claim_runs"])
        self.log = self.claim / "campaign_log.jsonl"
        self.log.write_bytes(producer.calibration_ledger.canonical_json_bytes({"record_type": "idle_admission_whole_window_verdict"}) + b"\n")
        self.aux = self.measurement / "configs/campaigns/fixture-bound"; self.aux.mkdir(parents=True)
        (self.aux / "bound.json").write_text('{"run_id":"bound-fixture"}\n')
        subprocess.run(["git", "-C", str(self.measurement), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.measurement), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "-qm", "fixture auxiliary"], check=True)
        self.head = subprocess.check_output(["git", "-C", str(self.measurement), "rev-parse", "HEAD"], text=True).strip()
        self.plan_path = self.custody / "night_plan.json"
        producer.write(self.plan_path, {"plan_id": self.custody.name, "fixture_only": True})
        self.go = producer.read(self.night / "go_receipt.json")
        self.go.update(purpose="G2B_SHAKEDOWN", plan_sha256=producer.reference(self.plan_path)["sha256"], repo_head=self.head)
        self.go["authorization"].update(purpose="G2B_SHAKEDOWN", claim_eligible=False)
        (self.night / "go_receipt.json").write_bytes(readiness.render_json(self.go))
        self.destinations = {role: str(self.base / (role + "-backup")) for role in ("claim", "bound")}
        arm = next(self.custody.glob("*/arm_readiness.receipts/arm-0001.json"))
        self.context = producer.read(arm)["arm_context"]
        self.context.update(custody_root=str(self.custody), claim_runs_root=self.sources["claim_runs"], bound_runs_root=self.sources["bound_runs"],
            claim_backup_destination=self.destinations["claim"], bound_backup_destination=self.destinations["bound"])
        value = producer.read(arm); value["arm_context"] = self.context; arm.write_bytes(readiness.render_json(value))
        self.go["arm_receipt"]["sha256"] = producer.reference(arm)["sha256"]
        (self.night / "go_receipt.json").write_bytes(readiness.render_json(self.go))
        self.record = {"schema_version": "joulewise.v5_qualification_plan_record.v1", "occurrence": "s1", "head": self.head,
            "plan": producer.reference(self.plan_path), "window_id": self.custody.name, "desk_sources": self.sources,
            "backup_destinations": self.destinations, "pack_night": {"pack_sha256": "a" * 64}}
        self.record_path = self.custody / "qualification-plan-record.json"; producer.write(self.record_path, self.record)
        self.plan = SimpleNamespace(custody_root=str(self.custody), measurement_root=str(self.measurement), measurement_head=self.head,
            plan_id=self.custody.name, pack_night={"pack_root": str(self.pack), "pack_sha256": "a" * 64})
        for name in ("launch", "capability_consumption", "capture"):
            producer.write(self.stage_dir / (name + ".json"), {"schema_version": t0.QUALIFICATION_STAGE_SCHEMA,
                "stage_id": name, "monotonic_ns": 1})
        producer.write(self.night / "post-bracket-terminal-boundary.json", {"session_state": "finalized", "pin_relation": "physical_ahead",
            "refusal_code": "calibration_ledger_head_mismatch", "terminal_head_pin_candidate": {"fixture": True}})
        self.off_path = self.custody / self.go["pack_id"] / "arm_readiness.t0.inputs/network_time_off.json"
        self.off = receipt(); self.off.update(plan_id=self.custody.name, window_id=self.custody.name, boot_id=self.go["boot_session_id"].lower())
        producer.write(self.off_path, self.off)
        producer.write(self.night / "standdown-observed.json", {"schema_version": producer.STANDDOWN_SCHEMA,
            "boot_session_id": self.go["boot_session_id"], "exits": [{"pid": 123, "observed_exit_monotonic_ns": 1}], "after": {"processes": []}})
        self.observation = {"argv": ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-getusingnetworktime"],
            "exit_code": 0, "stdout": "Network Time: Off\n", "stderr": ""}
        stage = {"stage_id": "bound", "kind": "campaign_collection", "input_ref": {"input_id": "neg8_bound_corpus"},
            "launch": {"commands": [{"argv_template": {"arguments": [{"kind": "repo_path", "value": "configs/campaigns/fixture-bound"}]}}]}}
        for patch in (mock.patch.object(desk.q, "load_plan", return_value=self.plan),
                      mock.patch.object(desk.writer, "pack_roster", return_value=([{"run_id": "science-fixture", "stage_id": "science"}], [], [], [])),
                      mock.patch.object(readiness, "_plan_tree", return_value=({"stage_graph": []}, None)),
                      mock.patch.object(desk.writer, "dispatched_stages", return_value=[stage]),
                      mock.patch.object(readiness, "committed_pack_tree_sha256", return_value="a" * 64),
                      mock.patch.object(producer.t0, "observed_run", return_value=subprocess.CompletedProcess(self.observation["argv"], 0, self.observation["stdout"], "")),
                      mock.patch.dict(desk.os.environ, {}, clear=True)):
            patch.start(); self.addCleanup(patch.stop)

    def close(self):
        return desk.closeout(self.plan_path)

    def test_two_verified_copies_closeout_off_identity_and_observed_restore(self):
        result = self.close()
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(set(result["stages"]), set(desk.DESK_STAGES))
        for name in ("claim_backup", "bound_backup"):
            value = producer.read(self.stage_dir / (name + ".json"))
            self.assertEqual(set(value["copies"]), {"custody", "claim_runs", "bound_runs"})
            for copy in value["copies"].values():
                self.assertEqual(producer.tree_files(Path(copy["destination"])), copy["files"])
        close = producer.read(self.stage_dir / "close_out.json")
        self.assertEqual(close["off_identity"], {key: self.off[key] for key in ("plan_id", "window_id", "boot_id")})
        self.assertEqual(close["phase_g"]["whole_window_verdict_count"], 1)
        restore = producer.read(self.stage_dir / "restore.json")
        self.assertEqual(restore["observation"], self.observation)
        with self.assertRaisesRegex(ValueError, "create-once"):
            self.close()

    def test_equal_and_nested_destinations_refused_before_any_backup(self):
        for destination in (self.destinations["claim"], self.destinations["claim"] + "/nested"):
            context = dict(self.context, bound_backup_destination=destination)
            with self.assertRaisesRegex(ValueError, "backup_destinations_overlap"):
                desk.writer.backup_destinations(context)
        self.assertFalse(Path(self.destinations["claim"]).exists())

    def test_backup_digest_mismatch_refuses(self):
        def corrupt(argv, **kwargs):
            target = Path(argv[-1]) / "runs"; target.parent.mkdir(parents=True); shutil.copytree(argv[-2], target)
            next(p for p in target.rglob("*") if p.is_file()).write_text("tampered")
            return subprocess.CompletedProcess(argv, 0)
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            desk.backup_sources(self.sources, self.base / "bad-backup", self.measurement / "scripts/backup_runs.sh", runner=corrupt)

    def test_phase_g_second_verdict_extra_bundle_scratch_or_modified_pack_refused(self):
        old = self.log.read_bytes()
        self.log.write_bytes(old + old)
        with self.assertRaisesRegex(ValueError, "exactly one"):
            self.close()
        self.log.write_bytes(old)
        extra = self.claim / "extra"; extra.mkdir()
        with self.assertRaisesRegex(ValueError, "extra or missing bundle"):
            self.close()
        extra.rmdir()
        scratch = self.custody / "scratch"; scratch.mkdir()
        with self.assertRaisesRegex(ValueError, "scratch residue"):
            self.close()
        scratch.rmdir()
        (self.pack / "config.json").write_text("tampered")
        with self.assertRaisesRegex(ValueError, "modified measurement checkout"):
            self.close()

    def test_restore_network_time_on_refuses_without_setter(self):
        with mock.patch.object(producer.t0, "observed_run", return_value=subprocess.CompletedProcess([], 0, "Network Time: On\n", "")) as run:
            with self.assertRaisesRegex(ValueError, "OFF observation"):
                self.close()
        self.assertFalse((self.stage_dir / "restore.json").exists())
        self.assertEqual(run.call_args.args[0], self.observation["argv"])

    def test_before_quiet_boundary_or_without_stop_or_inside_night_refuses(self):
        with mock.patch.object(desk.q, "load_plan", side_effect=ValueError("harvest_before_completion_boundary")):
            with self.assertRaisesRegex(ValueError, "completion_boundary"):
                self.close()
        stop = self.night / "post-bracket-terminal-boundary.json"; stop.unlink()
        with self.assertRaisesRegex(ValueError, "STOP boundary"):
            self.close()
        with mock.patch.dict(desk.os.environ, {"V5_QUALIFICATION_OCCURRENCE": "s1"}):
            with self.assertRaisesRegex(ValueError, "inside the night chain"):
                self.close()


if __name__ == "__main__":
    unittest.main()
