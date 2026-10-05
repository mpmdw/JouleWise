"""Ruling-76 desk controls. No test is live machine qualification."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, t0_rehearsal as t0
from scripts import produce_t0_rehearsal_bundle as producer, rehearse_t0_unattended as loader
from tests import test_t0_rehearsal as historical


class QualificationSubsetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = historical.FixtureBuilder(Path(self.temp.name).resolve()).build()

    def put(self, name, value):
        path = self.root / name
        path.write_bytes(readiness.render_json(value))

    def bundle(self):
        return historical.fixture_bundle(self.root)

    def g1_record(self, exit_code=1, stdout=""):
        rows = [{"role": "top_level", "pid": 1, "argv": ["driver"],
                 "stdin_fd0_target": "/dev/null", "state": "EXITED", "exit_code": 0,
                 "timed_out": False, "expected_outcome": {"exit_code": 0}, "stdout": None},
                {"role": "governed_subprocess", "pid": 2,
                 "argv": list(producer.night_gate.AGENT_CENSUS_ARGV),
                 "stdin_fd0_target": "/dev/null", "state": "EXITED", "exit_code": exit_code,
                 "timed_out": False, "expected_outcome": {"exit_code": 1, "stdout": ""}, "stdout": stdout}]
        return {"schema_version": t0.QUALIFICATION_EXECUTION_SCHEMA, "sequence_completed": True, "processes": rows}

    def test_g1_exact_empty_pgrep_one_passes_zero_or_nonempty_fails(self):
        for code, stdout, expected in ((1, "", "PASS"), (0, "", "FAIL"), (1, "42 claude", "FAIL"), (2, "", "FAIL")):
            self.put("records/execution.json", self.g1_record(code, stdout))
            with self.subTest(code=code, stdout=stdout):
                self.assertEqual(t0.evaluate_g1(self.bundle()).status.value, expected)

    def test_g1_outcomes_are_registered_not_caller_overrides(self):
        for key, value in (("expected_outcome", {"exit_code": 0}), ("stdin_fd0_target", "tty"), ("timed_out", True)):
            record = self.g1_record(0 if key == "expected_outcome" else 1)
            record["processes"][1][key] = value
            self.put("records/execution.json", record)
            self.assertEqual(t0.evaluate_g1(self.bundle()).status.value, "FAIL")
        record = self.g1_record(); record["sequence_completed"] = False
        self.put("records/execution.json", record)
        self.assertEqual(t0.evaluate_g1(self.bundle()).status.value, "FAIL")
        record = self.g1_record(); record["processes"][0]["exit_code"] = 1
        self.put("records/execution.json", record)
        self.assertEqual(t0.evaluate_g1(self.bundle()).status.value, "FAIL")

    def test_subset_delegates_eight_gates_and_g6_g7_never_pass(self):
        bundle = self.bundle()
        go = copy.deepcopy(bundle.record("d149_go").value)
        go.update(purpose="G2B_SHAKEDOWN")
        go["authorization"].update(purpose="G2B_SHAKEDOWN", claim_eligible=False)
        self.put("night/go_receipt.json", go)
        self.put("records/execution.json", self.g1_record())
        life = json.loads((self.root / "records/lifecycle.json").read_bytes())
        life["schema_version"] = t0.QUALIFICATION_LIFECYCLE_SCHEMA
        self.put("records/lifecycle.json", life)
        calls = []
        def evaluator(index):
            def run(bundle):
                calls.append(index)
                if index in (6, 7): raise AssertionError("retired evaluator called")
                return t0._result(f"G{index}", "fixture spy", t0.GateStatus.PASS, "fixture")
            return run
        with mock.patch.object(t0, "GATE_EVALUATORS", tuple(evaluator(i) for i in range(1, 11))):
            result = t0.evaluate_qualification(self.bundle())
        self.assertEqual(calls, [1, 2, 3, 4, 5, 8, 9, 10])
        self.assertEqual(result["overall_verdict"], "PASS")
        self.assertEqual(result["gate_counts"]["PASS"], 8)
        for row in result["gates"][5:7]:
            self.assertEqual(row["status"], "NOT_APPLICABLE")
            self.assertEqual(row["basis"], "retired_by_ruling_76")
        with self.assertRaisesRegex(ValueError, "requires G2B"):
            t0.evaluate_qualification(self.bundle(), purpose="T0_REHEARSAL")

    def test_historical_ten_gate_bytes_are_unchanged(self):
        with historical.fixture_replay(self.root):
            result = t0.evaluate_rehearsal(self.bundle())
        self.assertEqual(result["gate_counts"], {"PASS": 10, "FAIL": 0, "UNRULED": 0})
        self.assertEqual(result["schema_version"], "joulewise.t0_unattended_rehearsal_verdict.v1")
        self.assertNotIn("NOT_APPLICABLE", readiness.render_json(result).decode())

    def test_observed_driver_seams_keep_nonzero_exit_and_no_dialogue_invention(self):
        journal = Path(self.temp.name).resolve() / "process-observations.jsonl"
        with t0.process_journal(journal, observe_only=True):
            result = t0.observed_run([sys.executable, "-B", "-c", "raise SystemExit(7)"],
                                     stdin=subprocess.DEVNULL, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 7)
        events = [json.loads(line) for line in journal.read_bytes().splitlines()]
        self.assertEqual(events[0]["event"], "spawn")
        self.assertEqual(events[1]["exit_code"], 7)
        self.assertEqual(events[0]["stdin_fd0_target"], "/dev/null")
        self.assertNotIn("prompt_count", events[1])

    def test_journal_write_exception_cannot_change_child_rc(self):
        journal = Path(self.temp.name).resolve() / "process-observations.jsonl"
        with mock.patch.object(t0, "append_observation", side_effect=OSError("fixture disk fault")):
            with t0.process_journal(journal, observe_only=True):
                result = t0.observed_run([sys.executable, "-B", "-c", "raise SystemExit(9)"], stdin=subprocess.DEVNULL)
        self.assertEqual(result.returncode, 9)
        self.assertFalse(journal.exists())

    def test_descriptor_and_event_producer_faults_cannot_change_child_rc(self):
        for operation in (mock.patch.object(t0.os, "fstat", side_effect=OSError("fixture fd observation")),
                          mock.patch.object(t0._ProcessJournal, "emit", side_effect=OSError("fixture queue fault")),
                          mock.patch.object(t0._ProcessJournal, "emit", side_effect=SystemExit(19))):
            with self.subTest(operation=operation):
                journal = Path(self.temp.name).resolve() / "process-observations.jsonl"
                with operation, t0.process_journal(journal, observe_only=True):
                    result = t0.observed_run([sys.executable, "-B", "-c", "raise SystemExit(11)"], stdin=subprocess.DEVNULL)
                self.assertEqual(result.returncode, 11)
                self.assertTrue(journal.with_name("producer-faults.jsonl").exists())

    def test_supervisor_origin_fault_still_runs_driver_without_observer_timeout(self):
        from types import SimpleNamespace
        night = self.root / "night"
        auth = self.root / "authorization.json"
        auth.write_bytes(readiness.render_json({"purpose": "G2B_SHAKEDOWN"}))
        plan = SimpleNamespace(custody_root=str(self.root), measurement_root=str(self.root),
            pack_night={"authorization_record": {"path": str(auth)}})
        with mock.patch.object(producer, "plan_at", return_value=plan), mock.patch.object(
                producer.t0, "observed_run", return_value=subprocess.CompletedProcess(["fixture-driver"], 17)) as run:
            self.assertEqual(producer.run_driver(self.root / "fixture-plan.json", 0.1), 17)
        self.assertNotIn("timeout", run.call_args.kwargs)
        self.assertTrue((night / "producer-faults.jsonl").exists())

    def test_internal_workers_do_not_invent_multiple_top_level_drivers(self):
        command = ["python", "-B", "/checkout/scripts/run_night.py"]
        self.assertEqual(producer.qualification_process_role(command + ["run", "--plan", "/plan.json"]), "top_level")
        for worker in ("_bind-worker", "_probe-worker", "probe", "schedule"):
            self.assertEqual(producer.qualification_process_role(command + [worker, "--plan", "/plan.json"]), "governed_subprocess")

    def test_g10_physical_control_not_substituted_by_retirement(self):
        self.put("records/positive-control.json", {})
        with historical.fixture_replay(self.root):
            self.assertEqual(t0.evaluate_g10(self.bundle()).status.value, "FAIL")

    def qualified_lifecycle(self):
        from tests.test_network_time_off import receipt
        from scripts.produce_t0_rehearsal_bundle import verified_backup
        stage_dir = self.root / "records/qualification-stages"; stage_dir.mkdir()
        self.put("night/chain.started", {"pid": 777, "monotonic_ns": 10})
        metadata = self.root / "records/capture/metadata.json"
        metadata.parent.mkdir()
        metadata.write_bytes(readiness.render_json({"run_id": "fixture-only"}))
        raw = metadata.with_name("powermetrics.raw.txt"); raw.write_text("fixture-only sampler bytes")
        completion = self.root / "records/observed-completion.json"
        completion.write_bytes(readiness.render_json({"lifecycle_event": "completion", "proof_scope": producer.FIXTURE}))
        off = self.root / "records/off.json"; off.write_bytes(readiness.render_json(receipt()))
        consumption = next(self.root.rglob("*.consumed.json"))
        stages = []
        for index, name in enumerate(t0._LIFECYCLE_STAGES):
            value = {"schema_version": t0.QUALIFICATION_STAGE_SCHEMA, "stage_id": name, "monotonic_ns": index + 100}
            if name == "launch": value["source"] = producer.reference(self.root / "night/chain.started")
            elif name == "capability_consumption": value["source"] = producer.reference(consumption)
            elif name == "capture": value.update(artifacts=[producer.reference(metadata)], sampler_artifacts=[producer.reference(raw)])
            elif name.endswith("backup"):
                source = Path(self.temp.name).resolve() / (name + "-source"); source.mkdir()
                (source / "member.txt").write_text("fixture-only backup bytes")
                value.update(verified_backup(source, source.with_name(name + "-destination")))
            elif name == "close_out": value["source"] = producer.reference(completion)
            elif name == "restore": value.update(network_time="OFF", stand_down=True, off_receipt=producer.reference(off),
                observation={"argv": ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-getusingnetworktime"],
                             "exit_code": 0, "stdout": "Network Time: Off"})
            path = stage_dir / (name + ".json"); path.write_bytes(readiness.render_json(value))
            stages.append({"stage_id": name, "status": "COMPLETE", "evidence": producer.reference(path)})
        return {"schema_version": t0.QUALIFICATION_LIFECYCLE_SCHEMA, "stages": stages,
                "operator_actions_at_t0": 0, "human_interventions": []}

    def test_missing_s1_backup_or_closeout_cannot_pass_g9(self):
        life = self.qualified_lifecycle()
        self.put("records/lifecycle.json", life)
        # A supplied launch-completion fixture cannot invent s1's counterpart.
        baseline = t0.evaluate_g9(self.bundle())
        self.assertEqual(baseline.status.value, "FAIL")
        self.assertIn("close-out counterpart has not been ruled", baseline.message)
        for stage in ("claim_backup", "bound_backup", "close_out"):
            altered = copy.deepcopy(life)
            next(row for row in altered["stages"] if row["stage_id"] == stage)["status"] = "MISSING"
            self.put("records/lifecycle.json", altered)
            result = t0.evaluate_g9(self.bundle())
            self.assertEqual(result.status.value, "FAIL")
            self.assertIn("stage " + stage + " is not complete", result.message)

    def test_s1_producer_observes_sources_and_flags_missing_runsheet_counterparts(self):
        go = producer.read(self.root / "night/go_receipt.json")
        go["purpose"] = "G2B_SHAKEDOWN"; go["authorization"]["purpose"] = "G2B_SHAKEDOWN"
        self.put("night/go_receipt.json", go)
        self.put("night/chain.started", {"pid": 777, "monotonic_ns": 10})
        arm_path = next(self.root.glob("*/arm_readiness.receipts/arm-0001.json"))
        arm = producer.read(arm_path)
        for role in ("claim_runs_root", "bound_runs_root"):
            source = self.root / role; source.mkdir()
            (source / "metadata.json").write_bytes(readiness.render_json({"run_id": "fixture-only"}))
            (source / "powermetrics.raw.txt").write_text("fixture-only sampler bytes")
            arm["arm_context"][role] = str(source)
        arm_path.write_bytes(readiness.render_json(arm))
        from types import SimpleNamespace
        plan = SimpleNamespace(custody_root=str(self.root), plan_id=self.root.name)
        with mock.patch.object(producer.t0, "observed_run", side_effect=AssertionError("no machine query in desk test")):
            result_path = producer.observe_s1_lifecycle(plan)
        gaps = producer.read(result_path)["missing_stages"]
        self.assertEqual(gaps["close_out"], "physical_ahead_stop_forbids_launch_completion")
        self.assertEqual(gaps["claim_backup"], "no_two_backup_sequence_in_g2b_chain_or_runsheet")
        self.assertEqual(gaps["bound_backup"], "no_two_backup_sequence_in_g2b_chain_or_runsheet")
        for stage in ("launch", "capability_consumption", "capture"):
            self.assertTrue((self.root / "night/rehearsal-lifecycle" / (stage + ".json")).exists())
        self.assertFalse((self.root / "night/rehearsal-lifecycle/close_out.json").exists())
        self.assertFalse((self.root / "night/rehearsal-lifecycle/claim_backup.json").exists())

    def test_s1_assembly_emits_seven_record_subset_from_observed_fixture_mapping(self):
        from tests.test_v5_pack_rehearsal import ObservedDeskMappingTests
        fixture = ObservedDeskMappingTests('test_desk_observation_backup_assembly_and_real_evaluators')
        fixture.setUp()
        try:
            go = producer.read(fixture.night / "go_receipt.json")
            go["purpose"] = "G2B_SHAKEDOWN"; go["authorization"]["purpose"] = "G2B_SHAKEDOWN"
            (fixture.night / "go_receipt.json").write_bytes(readiness.render_json(go))
            journal = fixture.night / "process-observations.jsonl"
            events = [json.loads(line) for line in journal.read_bytes().splitlines()]
            for event in events:
                if event["event"] in {"spawn", "exit"}:
                    event["argv"] = ["python", "-B", "/fixture/run_night.py", "run", "--plan", "/fixture/plan.json"]
            spawn = copy.deepcopy(events[0]); spawn.update(pid=123456, argv=list(producer.night_gate.AGENT_CENSUS_ARGV))
            spawn["spawned_monotonic_ns"] += 1; spawn["monotonic_ns"] += 1
            exit_event = dict(spawn, event="exit", exit_code=1)
            output = {"schema_version": t0.PROCESS_EVENT_SCHEMA, "event": "output", "pid": spawn["pid"],
                "spawned_monotonic_ns": spawn["spawned_monotonic_ns"], "journal_id": spawn["journal_id"], "stdout": ""}
            events[-1]["record_count"] += 3
            journal.write_bytes(b"".join(producer.calibration_ledger.canonical_json_bytes(event) + b"\n"
                for event in [*events[:-1], spawn, exit_event, output, events[-1]]))
            stage_dir = fixture.night / "rehearsal-lifecycle"
            for name in ("launch", "capability_consumption", "restore"):
                path = stage_dir / (name + ".json")
                value = producer.read(path); value["schema_version"] = t0.QUALIFICATION_STAGE_SCHEMA
                path.write_bytes(readiness.render_json(value))
            for name in ("capture", "claim_backup", "bound_backup", "close_out"):
                (stage_dir / (name + ".json")).unlink()
            result = fixture.assemble(g7_locator=None)
            rows = {row["gate_id"]: row for row in result["gates"]}
            self.assertEqual(rows["G1"]["status"], "PASS")
            self.assertEqual(rows["G9"]["status"], "FAIL")
            self.assertEqual(rows["G6"]["basis"], "retired_by_ruling_76")
            self.assertEqual(rows["G7"]["status"], "NOT_APPLICABLE")
            manifest = producer.read(fixture.root / loader.QUALIFICATION_MANIFEST_NAME)
            self.assertEqual(set(manifest["records"]), loader.RECORD_NAMES - {"g7_control", "rehearsal_receipt"})
            execution = producer.read(fixture.records / "execution.json")
            self.assertEqual(execution["schema_version"], t0.QUALIFICATION_EXECUTION_SCHEMA)
            self.assertEqual(execution["processes"][1]["expected_outcome"], {"exit_code": 1, "stdout": ""})
            with self.assertRaisesRegex(loader.BundleLoadError, "fixture|observed"):
                loader.load_evidence_bundle(fixture.root, manifest_name=loader.QUALIFICATION_MANIFEST_NAME, require_observed=True)
        finally:
            fixture.doCleanups()



if __name__ == "__main__":
    unittest.main()
