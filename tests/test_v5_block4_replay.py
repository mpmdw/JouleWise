"""DESK ONLY: real committed-GAMMA preparation and explicit replay stop points.

The joined acceptance cases are SKIPPED, not certified by component controls:
main's GAMMA has no D-134 freeze pin. The real writer and ARM issuer refuse it.
No ARM, plan loader, pack authenticator, census or evaluator is replaced here.
The independent started-occurrence controls below do not bypass that stop to
claim a completed writer/ARM/driver/closeout/two-harvest occurrence.
"""
import inspect
from pathlib import Path
from types import SimpleNamespace
import subprocess
import sys
import tempfile
import unittest

from joulewise import arm_readiness as ar, night_gate
from joulewise import v5_qualification as q
from joulewise.night_plan_writer import write_night_plan
from scripts import harvest_v5_g2b_window as g2b, run_night as driver
from scripts import harvest_v5_qualification as qualification
from scripts import write_v5_qualification_plan as writer
from tests.test_kernel_clock import frequency_probe


SCRATCH = (Path(tempfile.gettempdir()) / "v5-block4-replay").resolve()
PACK_RELATIVE = "configs/campaigns/" + writer.GAMMA
PACK_SOURCE_COMMIT = "c88565c48fe7a8f0a1e6973cba3e03dfaeaacdab"


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(ar.render_json(value))
    return q.reference(path)


class CommittedGammaJoinedReplayTests(unittest.TestCase):
    """Run preparation without semantic mocks, stopping at missing authority."""

    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="joined-", dir=SCRATCH)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.pack = writer.REPO_ROOT / PACK_RELATIVE
        self.head = subprocess.check_output(
            ["git", "-C", str(writer.REPO_ROOT), "rev-parse", "HEAD"], text=True).strip()
        # Real committed pack bytes, including all configs and sidecars; no
        # two-file pack stand-in and no replacement digest authenticator.
        self.digest = ar.committed_pack_tree_sha256(self.pack)
        self.roster, self.auxiliary, self.brackets, self.nonsampling = writer.pack_roster(self.pack, "s1")
        self.sizing = writer.read_object(writer.REPO_ROOT /
            "configs/campaigns/v5_qualification_25g83/sizing_allowances.json")
        self.sized = writer.size_window("s1", self.sizing, roster=self.roster,
            auxiliary=self.auxiliary, brackets=self.brackets, nonsampling=self.nonsampling)
        self.template = self.root / "reviewed-chain.zsh"
        self.template.write_text(writer.g2b_body(writer.REPO_ROOT))
        self.chain = self.root / "chain.zsh"
        self.t0 = 1000.0  # Authored desk input, not an observed clock assertion.
        self.rendered = writer.render_qualification_chain("s1", self.template, self.sizing,
            self.pack, self.t0, self.chain)

    def test_complete_pack_bytes_roster_and_reviewed_chain_are_real(self):
        def tree_at(commit):
            return subprocess.check_output(["git", "-C", str(writer.REPO_ROOT),
                "ls-tree", "-r", commit, "--", PACK_RELATIVE])
        self.assertEqual(tree_at(PACK_SOURCE_COMMIT), tree_at(self.head))
        self.assertEqual(len(ar._plan_tree(self.pack)[0]["science"]), 80)
        self.assertEqual([r["position"] for r in self.roster], ["A1", "B1", "B2", "A2"])
        self.assertEqual((len(self.auxiliary), len(self.brackets), len(self.nonsampling)), (5, 2, 1))
        self.assertIn(writer.g2b_body(writer.REPO_ROOT), self.chain.read_text())
        self.assertEqual(self.rendered["chain"], writer.locator(self.chain))
        self.assertEqual(self.rendered["window_max_s"], self.sized["window_max_s"])
        # Parse only: executing this chain would invoke physical tools.
        result = subprocess.run(["/bin/zsh", "-n", str(self.chain)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())

    def inputs(self, occurrence):
        from tests.test_arm_readiness_schemas import arm_context
        from tests.test_family_marker import confirmation
        custody = self.root / occurrence
        custody.mkdir()
        # Schema-only diagnostic input. These fixture table hashes are not
        # publication evidence, and this table must NEVER authorize a launch.
        # It permits reaching the real freeze authenticator; no table validator
        # or freeze/ARM semantic function is mocked to get past it.
        table = self.root / (occurrence + "-schema-only-confirmation.json")
        put(table, confirmation())
        table.with_name(table.name + ".sha256").write_bytes(ar.gnu_sidecar(q.sha(table), table.name))
        ar._authenticate_confirmation_table(table, q.sha(table))
        transcript = self.root / (occurrence + "-schema-only-transcript.txt")
        transcript.write_text("DESK SCHEMA INPUT ONLY " + q.sha(table) + "\n")
        confirm = self.root / (occurrence + "-confirmation-record.json")
        put(confirm, {"table_path": str(table), "table_sha256": q.sha(table),
            "transcript_sha256": q.sha(transcript),
            "confirmed_at": {"epoch_s": 0.0, "iso8601_utc": "1970-01-01T00:00:00.000000Z"}})
        context = arm_context(custody)
        context["custody_root"] = str(custody)
        plan_id = ar._pack_record(self.pack)["plan_id"]
        end = self.t0 + self.sized["window_max_s"]
        binding = {"schema": night_gate.PACK_PLAN_SCHEMA, "schema_version": 3,
            "plan_id": plan_id, "receipt_class": "TRANSACTION_PACK", "t0_epoch_s": self.t0,
            "window_max_s": self.sized["window_max_s"], "authored_epoch_s": 0.0,
            "repo_head": self.head, "measurement_root": str(writer.REPO_ROOT),
            "measurement_head": self.head, "chain_path": str(self.chain),
            "chain_sha256_path": self.rendered["sidecar"]["path"], "custody_root": str(custody),
            "registration_path": None}
        prospective = night_gate.NightPlan.from_mapping({**binding,
            "pack_night": {"pack_id": self.pack.name, "pack_root": str(self.pack),
                "pack_sha256": self.digest, "attempt_ordinal": 1,
                "authorization_record": {"path": str(custody / "authorization_record.json"), "sha256": "0" * 64},
                "confirmation_record": {"path": str(custody / "step6_confirmation_record.json"), "sha256": "0" * 64}}})
        return {"schema_version": writer.INPUT_SCHEMA, "head": self.head, "plan": binding,
            "kernel_frequency": frequency_probe(),
            "pack": {"root": str(self.pack), "sha256": self.digest, "attempt_ordinal": 1},
            "authorization": {"purpose": "G2B_SHAKEDOWN", "attempt_id": plan_id + "/1",
                "claim_eligible": False, "permitted_blocks": 1, "pack_sha256": self.digest,
                "permitted_chain_sha256": q.sha(self.chain), "authority": "D-171 §3; DESK DIAGNOSTIC ONLY"},
            "confirmation": {"record": q.reference(confirm), "transcript": q.reference(transcript),
                "expected_confirmation_digest": q.sha(table)}, "sizing": self.sizing,
            "deadlines": {"latest_chain_start_epoch_s": self.rendered["latest_chain_start_epoch_s"],
                "shutdown_epoch_s": end + driver.WINDOW_SHUTDOWN_GRACE_S,
                "courier_epoch_s": end + driver.WINDOW_SHUTDOWN_GRACE_S + driver.COURIER_DEADLINE_S,
                "deadman_epoch_s": driver.deadman_epoch(prospective)},
            "other_custody_roots": [], "arm_context": context, "prerequisites": {}}

    def test_a1_a2_s1_real_writers_stop_at_unfrozen_pack_without_publishing(self):
        before = self.digest
        for occurrence in ("a1", "a2", "s1"):
            with self.subTest(occurrence=occurrence):
                inputs = self.inputs(occurrence)
                output = Path(inputs["plan"]["custody_root"]) / "plan.json"
                with self.assertRaises(ar.ArmReadinessError) as caught:
                    writer.write_qualification(occurrence, inputs, output)
                self.assertEqual(caught.exception.reason_code, "readiness_row_registry_mismatch")
                self.assertFalse(output.exists())
                self.assertEqual(list(output.parent.iterdir()), [])
        self.assertEqual(ar.committed_pack_tree_sha256(self.pack), before)

    def test_real_arm_issuer_also_stops_before_authorizing(self):
        from tests.test_arm_readiness_schemas import arm_context
        inputs = self.inputs("arm-diagnostic")
        confirmation = q.read(Path(inputs["confirmation"]["record"]["path"]))
        with self.assertRaises(ar.ArmReadinessError) as caught:
            ar.generate_arm_receipt(self.pack, arm_context(self.root),
                inputs["plan"]["custody_root"], step6_confirmation_table=confirmation["table_path"],
                expected_confirmation_digest=inputs["confirmation"]["expected_confirmation_digest"])
        self.assertEqual(caught.exception.reason_code, "readiness_row_registry_mismatch")
        self.assertFalse(list(self.root.rglob("arm_readiness.receipts/arm-*.json")))

    def joined_stop(self):
        tree, _ = ar._plan_tree(self.pack)
        if tree["arm_attachments"]["arm_readiness"]["freeze_receipt"] is not None:
            self.fail("freeze is now available: implement the joined replay; do not keep this stop")
        lines, start = inspect.getsourcelines(ar._load_freeze_reference)
        line = start + next(i for i, value in enumerate(lines) if '"readiness_freeze_receipt_unreadable"' in value)
        self.skipTest(f"FLAG joulewise/arm_readiness.py:{line}: committed GAMMA lacks freeze authority; "
            "writer/ARM cannot continue. No nonphysical semantic shortcut is allowed.")

    def test_joined_success_qualification_and_structural_pass(self):
        self.joined_stop()

    def test_joined_observation_exception_preserves_chain_rc_and_structural_verdict(self):
        self.joined_stop()

    def test_joined_launch_crash_recovers_no_science(self):
        self.joined_stop()

    def test_joined_agent_capture_is_live_gate_fail_end_state(self):
        self.joined_stop()


class StartedOccurrenceReplayTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="started-", dir=SCRATCH)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.pack = writer.REPO_ROOT / PACK_RELATIVE
        # Component input: an already-started occurrence, not a writer/ARM
        # success fixture. Authenticate the COMPLETE actual committed pack.
        head = subprocess.check_output(["git", "-C", str(writer.REPO_ROOT), "rev-parse", "HEAD"], text=True).strip()
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
        # Retained component input only: not proof of real courier delivery.
        put(self.night / "courier.sent", {"desk_fixture_delivery_ack": True})
        process = subprocess.Popen([sys.executable, "-B", "-c",
            "import sys; sys.stdin.read(); sys.exit(9)"], stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            # Real OS child and driver record writers. No PID/start-time or
            # process-group semantic mock; no science/privileged command.
            driver._write_launch_pending(process, self.night, self.plan)
            descriptor = driver._claim_chain_start(self.night)
            self.assertIsNotNone(descriptor)
            driver._complete_chain_start(descriptor, process, self.night)
            process.communicate(timeout=10)
            self.assertEqual(process.returncode, 9)
            driver._record_chain_exit(self.night, process.returncode)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)
            if process.stdin is not None:
                process.stdin.close()
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
        retained_rc = q.read(self.night / "chain.exited")["exit_code"]
        structural_before = self.harvest()
        self.args.archive_root = self.root / "structural-after-observation-fault"
        observations = {}
        for site in ("arm", "publication", "t0"):
            raw_path = self.root / (site + ".ioreg"); raw_path.write_bytes(raw())
            # Physical seams: ioreg battery read, wall and monotonic clocks.
            value, _ = battery_float.observe(phase=site, plan_id=self.plan.plan_id, wall_time_s=UPDATE + 1,
                monotonic_ns=lambda: 1, runner=lambda argv: subprocess.CompletedProcess(argv, 0, raw_path.read_bytes(), b""))
            observations[site] = {"record": put(self.root / (site + ".json"), value), "raw": q.reference(raw_path)}
        boundary = self.root / "boundaries.json"
        put(boundary, {"schema": "joulewise.v5_qualification_battery_boundaries.v1", "plan_id": self.plan.plan_id,
                       "observations": observations})
        driver._qualification_observe(self.night, "hid", lambda: (_ for _ in ()).throw(OSError("synthetic producer fault")))
        args = SimpleNamespace(plan=self.night_custody / "night_plan.json", archive_root=self.root / "qualification",
            battery_evidence=boundary, battery_evidence_sha256=q.sha(boundary), replay_source=[], previous_harvest=None)
        # Mock seam: wall clock after the completion/harvest boundary.
        verdict = qualification.harvest(args, now=lambda: 999999.)
        self.assertEqual(verdict["verdict"], "FAIL")
        self.assertEqual(verdict["cause_codes"], ["qualification_observation_producer_fault"])
        self.assertFalse(verdict["end_state"])
        structural = self.harvest()
        self.assertEqual(q.read(self.night / "chain.exited")["exit_code"], retained_rc)
        for field in ("verdict", "cause_codes", "cause_classes"):
            self.assertEqual(structural[field], structural_before[field])
        self.assertNotIn("qualification_observation_producer_fault", structural["cause_codes"])
        self.assertIn("started_chain_crashed", structural["cause_codes"])



if __name__ == "__main__":
    unittest.main()
