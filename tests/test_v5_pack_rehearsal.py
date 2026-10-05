"""DESK_FIXTURE_MAPPING_ONLY; none of these bytes discharge a live G gate."""
from __future__ import annotations
import copy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, t0_rehearsal as t0
from scripts import produce_t0_rehearsal_bundle as producer, rehearse_t0_unattended as reader
from tests.test_t0_rehearsal import FixtureBuilder, fixture_inventory, fixture_replay, _write_json


class ObservedDeskMappingTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.root = FixtureBuilder(self.base).build()
        self.night = self.root / "night"
        self.records = self.root / "records"
        # ARM/GO inputs are intentionally synthetic mapping inputs. Changing
        # the purpose without fresh consumption keeps G5 FAIL, as it must.
        go = producer.read(self.night / "go_receipt.json")
        go["purpose"] = "T0_REHEARSAL"
        go["authorization"]["purpose"] = "T0_REHEARSAL"
        _write_json(self.night / "go_receipt.json", go)
        self.go = go
        namespace = self.root / go["pack_id"]
        original = self.root / "t0-namespace"
        for subdir in ("arm_readiness.t0.inputs", "arm_readiness.t0.sources", "arm_readiness.evidence"):
            shutil.copytree(original / subdir, namespace / subdir, dirs_exist_ok=True)
        clock_path = namespace / "arm_readiness.t0.sources/clock-correct-and-prior-state.json"
        clock = producer.read(clock_path)
        clock["derivation"]["r1_batch_started_monotonic_ns"] = 400
        _write_json(clock_path, clock)
        _write_json(self.night / "hid-idle-observation.json", {
            "schema_version": producer.HID_SCHEMA, "argv": list(producer.HID_ARGV),
            "exit_code": 0, "stdout": '"HIDIdleTime" = 600000000000\n',
            "stderr": "", "started_monotonic_ns": 1100, "finished_monotonic_ns": 1200})
        journal = self.night / "process-observations.jsonl"
        with t0.process_journal(journal):
            result = t0.observed_run([sys.executable, "-B", "-c", "print('observed desk file activity')"],
                                     stdin=subprocess.DEVNULL, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        # The desk fixture supplies dialogue mapping fields explicitly. The
        # real observer deliberately leaves these unknown without transcripts.
        events = [json.loads(line) for line in journal.read_bytes().splitlines()]
        for event in events:
            if event["event"] == "exit":
                event.update(prompt_count=0, eof_refusal=False)
        journal.write_bytes(b"".join(producer.calibration_ledger.canonical_json_bytes(event) + b"\n" for event in events))
        pre = _write_json(self.night / "pre-standdown.json", {"census": {
            "processes": [{"pid": 777, "argv": ["/usr/local/bin/codex", "exec"]}]}})
        _write_json(self.night / "standdown-observed.json", {
            "schema_version": producer.STANDDOWN_SCHEMA,
            "before": producer.reference(self.night / "pre-standdown.json"),
            "exits": [{"pid": 777, "observed_exit_monotonic_ns": 1000}]})
        _write_json(self.night / "chain.started", {"pid": 999, "monotonic_ns": 1001})
        _write_json(self.night / "chain.exited", {"exit_code": 0, "monotonic_ns": 2000})
        t0.append_observation(self.night / "censuses.jsonl", {
            "argv": list(producer.night_gate.AGENT_CENSUS_ARGV), "exit_code": 1,
            "stdout": "", "monotonic_ns": 1500})
        claims, bounds = self.base / "claim-runs", self.base / "bound-runs"
        claims.mkdir(); bounds.mkdir()
        (claims / "activity.txt").write_text("observed lifecycle activity\n")
        (bounds / "activity.txt").write_text("observed lifecycle activity\n")
        stage_dir = self.night / "rehearsal-lifecycle"
        consumption_path = next(self.root.rglob("*.consumed.json"))
        activity_paths = [stage_dir / name for name in ("claim-activity.json", "bound-activity.json")]
        for path in activity_paths:
            _write_json(path, {"schema_version": "joulewise.t0_rehearsal_activity.v1", "claim_eligible": False,
                              "proof_scope": producer.FIXTURE})
        close_path = stage_dir / "ledger-close-out.json"
        _write_json(close_path, {"status": "aborted", "terminal_result": "session_aborted", "proof_scope": producer.FIXTURE})
        for i, stage in enumerate(t0._LIFECYCLE_STAGES):
            facts = {"schema_version": producer.STAGE_SCHEMA, "stage_id": stage, "monotonic_ns": 1001+i}
            if stage == "launch":
                facts["source"] = producer.reference(self.night / "chain.started")
            if stage == "capability_consumption":
                facts["source"] = producer.reference(consumption_path)
            if stage == "capture":
                facts["artifacts"] = [producer.reference(path) for path in activity_paths]
            if stage == "close_out":
                facts.update(sources=[producer.reference(path) for path in activity_paths],
                    ledger_close_out=producer.reference(close_path),
                    backup_records=[producer.reference(stage_dir / (name + ".json"))
                                    for name in ("claim_backup", "bound_backup")])
            if stage.endswith("backup"):
                source = claims if stage == "claim_backup" else bounds
                facts.update(producer.verified_backup(source, self.base / stage))
            if stage == "restore":
                off_path = self.records / "off.json"
                from tests.test_network_time_off import receipt
                _write_json(off_path, receipt())
                facts.update(network_time="OFF", stand_down=True, off_receipt=producer.reference(off_path),
                    observation={"argv": ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-getusingnetworktime"],
                                 "exit_code": 0, "stdout": "Network Time: Off\n"})
            _write_json(stage_dir / (stage + ".json"), facts)
        # Preserve the fixture record as an input; assembly derives fresh records.
        self.positive = self.base / "owner-control-fixture.json"
        shutil.copyfile(self.records / "positive-control.json", self.positive)
        self.raw = self.base / "owner-transcript-fixture.txt"
        self.raw.write_text("DESK_FIXTURE_MAPPING_ONLY; no physical resync\n")
        self.g7_locator = self.base / "g7-locator.json"
        old_manifest = producer.read(self.root / reader.MANIFEST_NAME)
        self.g7 = old_manifest["records"]["g7_control"]
        # G7 binds the modified GO digest, strictly for mapping. This remains
        # synthetic control evidence, never an authenticated live control.
        g7_value = producer.read(Path(self.g7["path"]))
        g7_value["presented"][1]["sha256"] = producer.reference(self.night / "go_receipt.json")["sha256"]
        _write_json(Path(self.g7["path"]), g7_value)
        self.g7["sha256"] = producer.reference(Path(self.g7["path"]))["sha256"]
        _write_json(self.g7_locator, self.g7)
        for name in ("execution.json", "hid-idle.txt", "rehearsal-receipt.json", "process-lineage.json", "lifecycle.json", "falsifier-controls.json", "positive-control.json"):
            (self.records / name).unlink(missing_ok=True)
        (self.root / reader.MANIFEST_NAME).unlink()

    def assemble(self, **options):
        args = dict(positive_control=self.positive,
                    positive_sha256=producer.reference(self.positive)["sha256"],
                    positive_artifacts=[self.raw], g7_locator=self.g7_locator,
                    fixture_mapping=True, home=self.root.parents[1], inventory=fixture_inventory(self.root))
        args.update(options)
        with fixture_replay(self.root):
            return producer.assemble(self.root, **args)

    def test_desk_observation_backup_assembly_and_real_evaluators(self):
        verdict = self.assemble()
        self.assertEqual(verdict["proof_scope"], producer.FIXTURE)
        gates = {g["gate_id"]: g for g in verdict["gates"]}
        for gate in ("G1", "G3", "G6", "G8", "G9", "G10"):
            self.assertEqual(gates[gate]["status"], "PASS", gates[gate])
        # The changed purpose was NOT consumed; canonical G5 kills relabeling.
        self.assertEqual(gates["G5"]["status"], "FAIL")
        manifest = producer.read(self.root / reader.MANIFEST_NAME)
        self.assertEqual(set(manifest["records"]), reader.RECORD_NAMES)
        self.assertEqual(len(producer.read(self.night / "go_receipt.json")), 26)
        self.assertEqual(producer.tree_files(self.base / "claim-runs"), producer.tree_files(self.base / "claim_backup"))
        self.assertEqual(producer.read(self.root / "rehearsal-provenance.json")["proof_scope"], producer.FIXTURE)
        observed = producer.read(self.night / "software-boundary-observations.json")
        self.assertEqual(observed["proof_scope"], "SOFTWARE_BOUNDARY_REPLAY_ONLY")
        for cases in observed["observations"].values():
            self.assertEqual([case["status"] for case in cases], ["PASS", "REFUSE"])

    def test_missing_record_is_killed(self):
        (self.night / "rehearsal-lifecycle/bound_backup.json").unlink()
        with self.assertRaises(ValueError):
            self.assemble()

    def test_swapped_record_is_killed(self):
        path = self.night / "rehearsal-lifecycle/claim_backup.json"
        shutil.copyfile(self.night / "rehearsal-lifecycle/bound_backup.json", path)
        with self.assertRaisesRegex(ValueError, "swapped"):
            self.assemble()

    def test_restore_on_is_killed_at_producer_and_evaluator(self):
        self.assemble()
        path = self.night / "rehearsal-lifecycle/restore.json"
        stage = producer.read(path)
        stage["network_time"] = "ON"
        _write_json(path, stage)
        lifecycle = producer.read(self.records / "lifecycle.json")
        lifecycle["stages"][-1]["evidence"] = producer.reference(path)
        _write_json(self.records / "lifecycle.json", lifecycle)
        bundle = reader.load_evidence_bundle(self.root, home=self.root.parents[1], inventory=fixture_inventory(self.root))
        result = t0.evaluate_g9(bundle)
        self.assertEqual(result.status.value, "FAIL")
        self.assertIn("restore-ON", result.message)

    def test_missing_g7_locator_final_refuses(self):
        with self.assertRaisesRegex(ValueError, "G7 locator"):
            self.assemble(g7_locator=None)

    def test_initial_then_final_are_distinct_immutable_derivations(self):
        self.assemble(initial=True, g7_locator=None)
        old = (self.root / "t0-rehearsal-initial.json").read_bytes()
        self.assemble()
        self.assertEqual((self.root / "t0-rehearsal-initial.json").read_bytes(), old)
        self.assertTrue((self.night / "assembly-final.json").exists())

    def test_fixture_evidence_presented_as_real_is_killed(self):
        self.assemble()
        output = io.BytesIO()
        rc = reader.main(["--custody-root", str(self.root)], stdout=output,
                         home=self.root.parents[1], inventory=fixture_inventory(self.root))
        self.assertEqual(rc, 2)
        self.assertIn("fixture", json.loads(output.getvalue())["load_issues"][0])

    def test_fixture_inputs_cannot_be_relabelled_by_omitting_fixture_switch(self):
        with self.assertRaises(ValueError):
            self.assemble(fixture_mapping=False)

    def test_backup_mutation_killed_after_rehash_of_lifecycle_label(self):
        self.assemble()
        (self.base / "claim_backup/activity.txt").write_text("swapped bytes\n")
        bundle = reader.load_evidence_bundle(self.root, home=self.root.parents[1], inventory=fixture_inventory(self.root))
        self.assertEqual(t0.evaluate_g9(bundle).status.value, "FAIL")

    def test_arbitrary_complete_label_without_capture_artifacts_is_killed(self):
        self.assemble()
        path = self.night / "rehearsal-lifecycle/capture.json"
        stage = producer.read(path)
        del stage["artifacts"]
        _write_json(path, stage)
        lifecycle = producer.read(self.records / "lifecycle.json")
        lifecycle["stages"][2]["evidence"] = producer.reference(path)
        _write_json(self.records / "lifecycle.json", lifecycle)
        bundle = reader.load_evidence_bundle(self.root, home=self.root.parents[1], inventory=fixture_inventory(self.root))
        self.assertEqual(t0.evaluate_g9(bundle).status.value, "FAIL")

    def test_unobserved_exit_is_not_invented(self):
        journal = self.night / "process-observations.jsonl"
        journal.write_bytes(journal.read_bytes().splitlines(keepends=True)[0])
        with self.assertRaisesRegex(ValueError, "observed exit"):
            self.assemble()

    def test_missing_dialogue_observation_cannot_be_inferred_from_exit_zero(self):
        journal = self.night / "process-observations.jsonl"
        events = [json.loads(line) for line in journal.read_bytes().splitlines()]
        for event in events:
            event.pop("prompt_count", None)
            event.pop("eof_refusal", None)
        journal.write_bytes(b"".join(producer.calibration_ledger.canonical_json_bytes(event) + b"\n" for event in events))
        gates = {g["gate_id"]: g for g in self.assemble()["gates"]}
        self.assertEqual(gates["G1"]["status"], "FAIL")


class IsolationRecipeTests(unittest.TestCase):
    def test_foreground_observers_reject_unbounded_timeouts_before_plan_access(self):
        for value in (float("nan"), float("inf"), 0, -1):
            with self.subTest(timeout=value):
                for operation in (producer.observe_standdown, producer.run_driver):
                    with self.assertRaisesRegex(ValueError, "finite and positive"):
                        operation(Path("/nonexistent-plan.json"), value)

    def test_retired_pack_and_chain_are_absent(self):
        root = Path(__file__).resolve().parents[1]
        self.assertFalse((root / "configs/campaigns/v5_pack_rehearsal/generate_configs.py").exists())
        self.assertFalse((root / "scripts/night_chains/v5_pack_rehearsal.zsh").exists())

    def test_observed_descriptor_and_expected_negative_exit_are_retained(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp).resolve() / "journal.jsonl"
            with t0.process_journal(path):
                result = t0.observed_run([sys.executable, "-B", "-c", "raise SystemExit(1)"], stdin=subprocess.DEVNULL, timeout=10)
            self.assertEqual(result.returncode, 1)
            events = [json.loads(line) for line in path.read_bytes().splitlines() if json.loads(line)["event"] != "seal"]
            self.assertEqual([e["event"] for e in events], ["spawn", "exit"])
            self.assertEqual(events[-1]["exit_code"], 1)
            self.assertEqual(events[0]["stdin_fd0_target"], "/dev/null")


if __name__ == "__main__":
    unittest.main()
