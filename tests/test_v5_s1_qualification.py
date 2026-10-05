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
from tests.git_fixture import init_git_fixture


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

    def test_g1_registered_table_covers_all_native_absence_probes(self):
        from joulewise import arm_readiness_evidence_t0 as author
        argv_roster = [list(producer.night_gate.AGENT_CENSUS_ARGV),
                      ["/usr/bin/pgrep", "-x", "caffeinate"],
                      ["/usr/bin/pgrep", "-lf", author._BROWSER_CENSUS_PATTERN],
                      ["/usr/bin/pgrep", "-lf", author._MONITOR_CENSUS_PATTERN],
                      ["/usr/bin/pgrep", "-lf", "-g", "12345", "."]]
        for argv in argv_roster:
            for code, stdout, expected in ((1, "", "PASS"), (0, "", "FAIL"),
                                           (1, None, "FAIL"), (1, "42 process", "FAIL"), (2, "", "FAIL")):
                record = self.g1_record(code, stdout)
                record["processes"][1]["argv"] = argv
                self.put("records/execution.json", record)
                with self.subTest(argv=argv, code=code, stdout=stdout):
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

    def test_delivered_courier_journal_assembles_with_observed_exit_and_timeout(self):
        from tests.test_run_night import CourierReapingTests
        from tests.test_v5_pack_rehearsal import ObservedDeskMappingTests
        for hang in (False, True):
            with self.subTest(still_running=hang):
                courier = CourierReapingTests()
                courier.setUp()
                mapping = ObservedDeskMappingTests()
                try:
                    outcome = courier.delivered_child(hang=hang, budget=0.2 if hang else 2)
                    mapping.setUp()
                    go = producer.read(mapping.night / "go_receipt.json")
                    go["purpose"] = go["authorization"]["purpose"] = "G2B_SHAKEDOWN"
                    (mapping.night / "go_receipt.json").write_bytes(readiness.render_json(go))
                    for stage_id in t0._LIFECYCLE_STAGES:
                        path = mapping.night / "rehearsal-lifecycle" / (stage_id + ".json")
                        stage = producer.read(path)
                        stage["schema_version"] = t0.QUALIFICATION_STAGE_SCHEMA
                        path.write_bytes(readiness.render_json(stage))
                    (mapping.night / "process-observations.jsonl").write_bytes(courier.journal.read_bytes())
                    mapping.assemble(g7_locator=None)
                    execution = producer.read(mapping.records / "execution.json")
                    observed = execution["processes"][0]
                    self.assertEqual(observed["state"], "EXITED")
                    self.assertEqual(observed["exit_code"], outcome["exit_code"])
                    self.assertEqual(observed["timed_out"], hang)
                    self.assertEqual(execution["sequence_completed"], not hang)
                finally:
                    mapping.doCleanups()
                    courier.doCleanups()

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

    def qualified_lifecycle(self, *, head_extension=None, measurement_root=None, occurrence="s1"):
        from tests.test_network_time_off import receipt
        stage_dir = self.root / "records/qualification-stages"; stage_dir.mkdir()
        self.put("night/chain.started", {"pid": 777, "monotonic_ns": 10})
        metadata = stage_dir / "capture/metadata.json"; metadata.parent.mkdir()
        metadata.write_bytes(readiness.render_json({"run_id": "fixture-only"}))
        raw = metadata.with_name("powermetrics.raw.txt"); raw.write_text("fixture-only sampler bytes")
        off_value = receipt(); go = producer.read(self.root / "night/go_receipt.json")
        off_value.update(plan_id=self.root.name, window_id=self.root.name, boot_id=go["boot_session_id"].lower())
        off = stage_dir / "off.json"; off.write_bytes(readiness.render_json(off_value))
        plan = self.root / "night_plan.json"; plan.write_bytes(readiness.render_json({"plan_id": self.root.name,
            **({"measurement_root": str(measurement_root)} if measurement_root is not None else {})}))
        if head_extension is not None:
            go["repo_head"] = head_extension["armed_head"]
        go["plan_sha256"] = producer.reference(plan)["sha256"]
        self.put("night/go_receipt.json", go)
        arm_root = Path(self.temp.name).resolve() / "desk-arm-custody"
        arm_root.mkdir(); (arm_root / "member.txt").write_text("fixture-only ARM custody bytes")
        sources = {"custody": str(arm_root), "night_custody": str(self.root)}
        (self.root / "records/lifecycle.json").unlink()
        for role in ("claim_runs", "bound_runs"):
            root = Path(self.temp.name).resolve() / ("backup-" + role); root.mkdir()
            (root / "member.txt").write_text("fixture-only backup bytes")
            sources[role] = str(root)
        destinations = {role: str(Path(self.temp.name).resolve() / (role + "-destination")) for role in ("claim", "bound")}
        arm_path = next(self.root.glob("*/arm_readiness.receipts/arm-0001.json"))
        arm = producer.read(arm_path)
        arm["arm_context"].update(custody_root=sources["custody"], claim_runs_root=sources["claim_runs"], bound_runs_root=sources["bound_runs"],
            claim_backup_destination=destinations["claim"], bound_backup_destination=destinations["bound"])
        arm_path.write_bytes(readiness.render_json(arm))
        context_path = arm_path.parent.parent / "arm_readiness.t0.inputs/arm-context.json"
        context_path.write_bytes(readiness.render_json(arm["arm_context"]))
        chain = self.root / "night/window-chain.zsh"
        chain.write_text(f"export V5_QUALIFICATION_OCCURRENCE={occurrence}\nexport NIGHT_ARM_CONTEXT_SHA256="
                         + producer.reference(context_path)["sha256"] + "\n")
        plan_value = producer.read(plan)
        plan_value.update(custody_root=str(self.root), chain_path=str(chain), pack_night={"pack_id": go["pack_id"]})
        plan.write_bytes(readiness.render_json(plan_value))
        go["plan_sha256"] = producer.reference(plan)["sha256"]
        go["window_chain_sha256"] = producer.reference(chain)["sha256"]
        go["arm_receipt"]["sha256"] = producer.reference(arm_path)["sha256"]
        self.put("night/go_receipt.json", go)
        record = stage_dir / "plan-record.json"
        record.write_bytes(readiness.render_json({"schema_version": "joulewise.v5_qualification_plan_record.v1",
            "occurrence": occurrence, "head": go["repo_head"], "plan": producer.reference(plan),
            "window_id": self.root.name, "desk_sources": sources, "backup_destinations": destinations,
            "pack_night": {"pack_sha256": "a" * 64}}))
        stop = stage_dir / "stop.json"; stop.write_bytes(readiness.render_json({"session_state": "finalized",
            "pin_relation": "physical_ahead", "refusal_code": "calibration_ledger_head_mismatch", "terminal_head_pin_candidate": head_extension["terminal_head_pin"] if head_extension else {"fixture": True}}))
        runsheet = producer.copy_record(producer.REPO_ROOT / "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md", stage_dir / "runsheet.md")
        log = stage_dir / "campaign_log.jsonl"; log.write_bytes(producer.calibration_ledger.canonical_json_bytes({"record_type": "idle_admission_whole_window_verdict"}) + b"\n")
        standdown = stage_dir / "standdown.json"; standdown.write_bytes(readiness.render_json({
            "schema_version": producer.STANDDOWN_SCHEMA, "boot_session_id": go["boot_session_id"],
            "exits": [{"pid": 123, "observed_exit_monotonic_ns": 1}], "after": {"processes": []}}))
        consumption = next(self.root.rglob("*.consumed.json"))
        stages = []
        for index, name in enumerate(t0._LIFECYCLE_STAGES):
            value = {"schema_version": t0.QUALIFICATION_STAGE_SCHEMA, "stage_id": name, "monotonic_ns": index + 100}
            if name == "launch": value["source"] = producer.reference(self.root / "night/chain.started")
            elif name == "capability_consumption": value["source"] = producer.reference(consumption)
            elif name == "capture": value.update(artifacts=[producer.reference(metadata)], sampler_artifacts=[producer.reference(raw)])
            else: value["plan_record"] = producer.reference(record)
            if name.endswith("backup"):
                role = "claim" if name == "claim_backup" else "bound"
                copies = {}
                for source_role, source in sources.items():
                    dest = Path(destinations[role]) / source_role / "runs"; dest.parent.mkdir(parents=True)
                    copies[source_role] = producer.verified_backup(Path(source), dest)
                value.update(destination=destinations[role], copies=copies)
            elif name == "close_out": value.update(stop=producer.reference(stop), runsheet=producer.reference(runsheet),
                off_receipt=producer.reference(off), off_identity={key: off_value[key] for key in ("plan_id", "window_id", "boot_id")},
                phase_g={"whole_window_verdict_count": 1, "campaign_log": producer.reference(log),
                    "expected_bundles": {"claim_runs": [], "bound_runs": []}, "runs_tree": {"claim_runs": ["member.txt"], "bound_runs": ["member.txt"]},
                    "custody_files": producer.tree_files(Path(sources["custody"])), "git_status": "## fixture\n",
                    "head": head_extension["head"] if head_extension else go["repo_head"],
                    **({"head_extension": head_extension} if head_extension else {}),
                    "pack_sha256": "a" * 64, "no_extra_bundles": True,
                    "no_scratch_residue": True, "pack_unchanged": True})
            elif name == "restore": value.update(network_time="OFF", stand_down=True, off_receipt=producer.reference(off),
                standdown=producer.reference(standdown), observation={"argv": ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "off"],
                             "exit_code": 0, "stdout": "Network Time is already off."})
            path = stage_dir / (name + ".json"); path.write_bytes(readiness.render_json(value))
            stages.append({"stage_id": name, "status": "COMPLETE", "evidence": producer.reference(path)})
        return {"schema_version": t0.QUALIFICATION_LIFECYCLE_SCHEMA, "stages": stages,
                "operator_actions_at_t0": 0, "human_interventions": []}

    def mutate_stage(self, life, name, mutate):
        row = next(row for row in life["stages"] if row["stage_id"] == name)
        path = Path(row["evidence"]["path"])
        value = producer.read(path); mutate(value)
        path.write_bytes(readiness.render_json(value))
        row["evidence"] = producer.reference(path)
        self.put("records/lifecycle.json", life)

    def test_g9_requires_exact_registered_copies_and_authenticated_two_roots(self):
        life = self.qualified_lifecycle(); self.put("records/lifecycle.json", life)
        result = t0.evaluate_g9(self.bundle())
        self.assertEqual(result.status.value, "PASS", result.message)
        row = next(row for row in life["stages"] if row["stage_id"] == "claim_backup")
        stage_path = Path(row["evidence"]["path"])
        original = producer.read(stage_path)
        for change in ("missing", "extra", "wrong_plan_root"):
            value = copy.deepcopy(original)
            if change == "missing":
                value["copies"].pop("night_custody")
            elif change == "extra":
                value["copies"]["unregistered"] = value["copies"]["custody"]
            else:
                value["copies"]["night_custody"]["source"] = value["copies"]["custody"]["source"]
            stage_path.write_bytes(readiness.render_json(value))
            row["evidence"] = producer.reference(stage_path); self.put("records/lifecycle.json", life)
            with self.subTest(change=change):
                self.assertEqual(t0.evaluate_g9(self.bundle()).status.value, "FAIL")
        stage_path.write_bytes(readiness.render_json(original))
        row["evidence"] = producer.reference(stage_path); self.put("records/lifecycle.json", life)
        plan_record = producer.read(original["plan_record"]["path"])
        plan = producer.read(plan_record["plan"]["path"])
        native = self.root / plan["pack_night"]["pack_id"] / "arm_readiness.t0.inputs/arm-context.json"
        # Editing only the input (without its chain pin) cannot redefine ARM roots.
        context = producer.read(native); context["custody_root"] = str(self.root)
        native.write_bytes(readiness.render_json(context))
        self.assertEqual(t0.evaluate_g9(self.bundle()).status.value, "FAIL")

    def test_s2_desk_preservation_replays_and_mislabeled_occurrence_refuses(self):
        life = self.qualified_lifecycle(occurrence="s2")
        self.put("records/lifecycle.json", life)
        result = t0.evaluate_g9(self.bundle())
        self.assertEqual(result.status.value, "PASS", result.message)
        stage = producer.read(next(row["evidence"]["path"] for row in life["stages"]
                                   if row["stage_id"] == "claim_backup"))
        record_path = Path(stage["plan_record"]["path"])
        record = producer.read(record_path)
        record["occurrence"] = "s1"
        record_path.write_bytes(readiness.render_json(record))
        for row in life["stages"]:
            if row["stage_id"] in {"claim_backup", "bound_backup", "close_out", "restore"}:
                stage_path = Path(row["evidence"]["path"])
                value = producer.read(stage_path)
                value["plan_record"] = producer.reference(record_path)
                stage_path.write_bytes(readiness.render_json(value))
                row["evidence"] = producer.reference(stage_path)
        self.put("records/lifecycle.json", life)
        result = t0.evaluate_g9(self.bundle())
        self.assertEqual(result.status.value, "FAIL")
        self.assertIn("occurrence differs", result.message)

    def test_missing_s1_backup_or_closeout_cannot_pass_g9(self):
        life = self.qualified_lifecycle(); self.put("records/lifecycle.json", life)
        result = t0.evaluate_g9(self.bundle())
        self.assertEqual(result.status.value, "PASS", result.message)
        for name in t0._LIFECYCLE_STAGES:
            altered = copy.deepcopy(life)
            next(row for row in altered["stages"] if row["stage_id"] == name)["status"] = "MISSING"
            self.put("records/lifecycle.json", altered)
            self.assertEqual(t0.evaluate_g9(self.bundle()).status.value, "FAIL")
            altered = copy.deepcopy(life)
            next(row for row in altered["stages"] if row["stage_id"] == name)["evidence"]["sha256"] = "0" * 64
            self.put("records/lifecycle.json", altered)
            self.assertEqual(t0.evaluate_g9(self.bundle()).status.value, "FAIL", name)

    def test_unverified_backup_digest_mismatch_fails(self):
        life = self.qualified_lifecycle(); self.put("records/lifecycle.json", life)
        stage = producer.read(next(row["evidence"]["path"] for row in life["stages"] if row["stage_id"] == "claim_backup"))
        Path(stage["copies"]["bound_runs"]["destination"], "member.txt").write_text("tampered")
        result = t0.evaluate_g9(self.bundle())
        self.assertEqual(result.status.value, "FAIL"); self.assertIn("digest mismatch", result.message)

    def test_same_backup_destination_twice_fails(self):
        life = self.qualified_lifecycle()
        claim = producer.read(next(row["evidence"]["path"] for row in life["stages"] if row["stage_id"] == "claim_backup"))
        self.mutate_stage(life, "bound_backup", lambda value: value.update(destination=claim["destination"]))
        self.assertEqual(t0.evaluate_g9(self.bundle()).status.value, "FAIL")

    def test_closeout_missing_off_identity_fails(self):
        life = self.qualified_lifecycle()
        self.mutate_stage(life, "close_out", lambda value: value.pop("off_identity"))
        result = t0.evaluate_g9(self.bundle())
        self.assertEqual(result.status.value, "FAIL"); self.assertIn("OFF identity", result.message)

    def test_g9_authenticates_h_pin_against_real_git_objects_and_stop(self):
        from joulewise import v5_qualification as q, calibration_ledger as ledger
        repository = Path(self.temp.name).resolve() / "head-replay"; repository.mkdir()
        pin = repository / "configs/calibration/calibration_ledger_head.json"; pin.parent.mkdir(parents=True)
        pin.write_bytes(readiness.render_json({"ledger_schema": ledger.LEDGER_SCHEMA, "sequence": 0, "head_digest": ledger.GENESIS_DIGEST}))
        def git(*args):
            return subprocess.check_output(["git", "-C", str(repository), *args], text=True, stderr=subprocess.PIPE).strip()
        def commit(message):
            git("add", "."); git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", message)
        init_git_fixture(repository, "-q"); commit("fixture H")
        armed = git("rev-parse", "HEAD")
        pin.write_bytes(readiness.render_json({"ledger_schema": ledger.LEDGER_SCHEMA, "sequence": 3, "head_digest": "a" * 64}))
        commit("fixture H_pin"); head_pin = git("rev-parse", "HEAD")
        extension = q.pin_only_head_extension(repository, armed, head_pin)
        life = self.qualified_lifecycle(head_extension=extension, measurement_root=repository)
        self.put("records/lifecycle.json", life)
        result = t0.evaluate_g9(self.bundle())
        self.assertEqual(result.status.value, "PASS", result.message)
        # Replay the preserved H_pin from a later desk head; HEAD is irrelevant.
        (repository / "later-record.md").write_text("fixture later desk record")
        commit("fixture later head")
        self.assertEqual(t0.evaluate_g9(self.bundle()).status.value, "PASS")

    def test_g9_rejects_setter_that_had_to_turn_network_time_off(self):
        life = self.qualified_lifecycle()
        self.mutate_stage(life, "restore", lambda value: value["observation"].update(stdout="setUsingNetworkTime: Off"))
        self.put("records/lifecycle.json", life)
        self.assertEqual(t0.evaluate_g9(self.bundle()).status.value, "FAIL")

    def test_restore_network_time_on_fails(self):
        life = self.qualified_lifecycle()
        self.mutate_stage(life, "restore", lambda value: value.update(network_time="ON"))
        self.assertEqual(t0.evaluate_g9(self.bundle()).status.value, "FAIL")

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
        self.assertEqual(gaps["close_out"], "post_STOP_desk_closeout_required")
        self.assertEqual(gaps["claim_backup"], "post_STOP_desk_closeout_required")
        self.assertEqual(gaps["bound_backup"], "post_STOP_desk_closeout_required")
        for stage in ("launch", "capability_consumption", "capture"):
            self.assertTrue((self.root / "night/rehearsal-lifecycle" / (stage + ".json")).exists())
        self.assertFalse((self.root / "night/rehearsal-lifecycle/close_out.json").exists())
        self.assertFalse((self.root / "night/rehearsal-lifecycle/claim_backup.json").exists())

    def test_s1_assembly_requires_all_four_desk_stage_records(self):
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
            with self.assertRaises((OSError, ValueError)):
                fixture.assemble(g7_locator=None)
        finally:
            fixture.doCleanups()



if __name__ == "__main__":
    unittest.main()
