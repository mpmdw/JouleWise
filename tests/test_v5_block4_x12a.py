"""Addendum F harvest/history regressions on desk fixtures, never hardware."""
from pathlib import Path
import copy
import io
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import network_time_off, v5_qualification as q
from scripts import capture_t0_step as capture, restore_v5_null_reservation as restore
from scripts import v5_s1_desk_closeout as desk
from scripts import harvest_v5_g2b_window as g2b, harvest_v5_qualification as qualification
from scripts import write_v5_qualification_plan as writer
from tests import test_v5_block4_x7 as x7, test_v5_block4_x2 as x2
from tests import test_v5_s1_desk_closeout as desk_tests
from tests.test_arm_readiness_evidence_t0 import _clock_reference_value
from tests import test_harvest_v5_g2b_window as harvest_tests


def capture_off(path, pack_id, window_id, boot_id, *, epoch=1000., monotonic=1000.):
    """Real R0 capture writer -> immutable OFF receipt; only machine IO is fake."""
    path.unlink(missing_ok=True)
    roots = {}
    for name in ("RUNS_ROOT", "BOUND_RUNS_ROOT", "CUSTODY_ROOT", "QUARANTINE_ROOT"):
        root = path.parent / name.lower()
        root.mkdir(parents=True, exist_ok=True)
        roots[name] = str(root)
    context = SimpleNamespace(input_root=path.parent, repository=path.parent,
        plan_id=pack_id, boot_session_id=boot_id, assignments={**roots, "WINDOW_ID": window_id})
    reference = _clock_reference_value(boot_session_id=boot_id, anchor_monotonic_raw_ns=round(monotonic * 1e9))
    calls = []
    def execute(argv, **kwargs):
        calls.append(tuple(argv))
        if tuple(argv) == network_time_off.OFF_ARGV:
            return subprocess.CompletedProcess(argv, 0, b"Network Time is already off.\n", b"")
        return subprocess.CompletedProcess(argv, 0, q.readiness.render_json(reference), b"")
    reference_argv = capture._command_for_step(context, "clock-reference")
    with mock.patch.object(capture, "_current_boot_session_id", return_value=boot_id), \
         mock.patch.object(capture.time, "time", return_value=epoch):
        capture._arm_reference(context, execute, lambda: round(monotonic * 1e9))
    assert calls == [reference_argv, network_time_off.OFF_ARGV]
    return network_time_off.read_receipt(path, plan_id=pack_id, window_id=window_id)


class ComposedReceiptTests(unittest.TestCase):
    def test_one_attempt_real_capture_harvest_then_desk_closeout(self):
        # Compose both consumers on one night plan, pack and writer-produced
        # receipt. The inherited fixtures isolate launch/physics and pack
        # semantics; receipt publication/readback, preservation and census run
        # through their production implementations without replacements.
        d = desk_tests.DeskCloseoutTests()
        d.setUp()
        self.addCleanup(d.doCleanups)
        f = x2.G2bHarness()
        self.addCleanup(f.close)
        x7.put(d.aux / "bound.json", {"run_id": "bound0"})
        subprocess.run(["git", "-C", str(d.measurement), "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(d.measurement), "-c", "user.name=Fixture", "-c",
            "user.email=fixture@example.invalid", "commit", "-qm", "composed desk fixture"], check=True, capture_output=True)
        head = subprocess.check_output(["git", "-C", str(d.measurement), "rev-parse", "HEAD"], text=True).strip()
        plan_path = f.night_root / "night_plan.json"
        value = q.read(plan_path)
        value.update(measurement_root=str(d.measurement), measurement_head=head, repo_head=head)
        x7.put(plan_path, value)
        f.plan = q.night_gate.NightPlan.from_mapping(value)
        pack = Path(f.plan.pack_night["pack_root"])
        x7.put(pack / "calibration_plan.json", {"plan_id": "frozen"})
        inputs = q.read(f.input_path)
        inputs["plan"] = q.reference(plan_path)
        x7.put(f.input_path, inputs)
        f.args.inputs_sha256 = q.sha(f.input_path)
        context = dict(d.context, claim_runs_root=str(f.case.runs), bound_runs_root=str(f.bound))
        arm_path = f.night_root / f.plan.pack_night["pack_id"] / "arm_readiness.receipts/arm-0001.json"
        x7.put(arm_path, {"arm_context": context})
        go = copy.deepcopy(d.go)
        go.update(plan_id=f.plan.plan_id, plan_sha256=q.sha(plan_path), repo_head=head, pack_id=f.plan.pack_night["pack_id"])
        go["arm_receipt"]["sha256"] = q.sha(arm_path)
        x7.put(f.night / "go_receipt.json", go)
        record = dict(d.record, plan=q.reference(plan_path), head=head, window_id="frozen-window",
            terminal_boundary_path=str(f.terminal), desk_sources={"custody": str(d.arm_root),
                "night_custody": str(f.night_root), "claim_runs": str(f.case.runs), "bound_runs": str(f.bound)})
        x7.put(f.night_root / "qualification-plan-record.json", record)
        shutil.copy2(d.night / "transcript/post-bracket-terminal-boundary.json", f.terminal)
        inputs["terminal_boundary"] = q.reference(f.terminal)
        x7.put(f.input_path, inputs)
        f.args.inputs_sha256 = q.sha(f.input_path)
        stage_dir = f.night / "rehearsal-lifecycle"
        shutil.copytree(d.stage_dir, stage_dir)
        shutil.copy2(d.night / "standdown-observed.json", f.night / "standdown-observed.json")
        f.go["boot_session_id"] = go["boot_session_id"]
        frozen_id = q.read(pack / "calibration_plan.json")["plan_id"]
        capture_off(f.off_path, frozen_id, record["window_id"], go["boot_session_id"].lower())
        roster = [{"run_id": rid, "stage_id": "science"} for rid in f.case.ids]
        with mock.patch.object(q, "load_plan", return_value=f.plan), \
             mock.patch.object(desk.writer, "pack_roster", return_value=(roster, [], [], [])):
            harvested = f.run()
            self.assertEqual(harvested["verdict"], "PASS", harvested)
            self.assertEqual(desk.closeout(plan_path)["status"], "COMPLETE")
        closed = q.read(stage_dir / "close_out.json")
        self.assertEqual(closed["off_receipt"], q.reference(f.off_path))
        self.assertEqual(closed["off_identity"]["plan_id"], frozen_id)
        self.assertNotEqual(f.plan.plan_id, frozen_id)

    def test_real_capture_receipt_through_full_g2b_harvest(self):
        # Existing synthetic physics/launch boundaries remain explicit; the R0
        # writer, OFF reader, full harvest orchestration and census are real.
        f = x2.G2bHarness()
        self.addCleanup(f.close)
        f.go["boot_session_id"] = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
        capture_off(f.off_path, "frozen", "frozen-window", f.go["boot_session_id"])
        self.assertNotEqual(f.plan.plan_id, "frozen")
        result = f.run()
        self.assertEqual(result["verdict"], "PASS", result)
        self.assertEqual(q.read(f.args.archive_root / "harvest.json"), result)
        self.assertTrue((f.args.archive_root / "withheld/network-time.json").is_file())

    def test_real_capture_receipt_through_full_desk_closeout(self):
        f = desk_tests.DeskCloseoutTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        frozen_id = q.read(f.pack / "calibration_plan.json")["plan_id"]
        # Change only the occurrence identity; frozen pack and window stay put.
        f.plan.plan_id += "-attempt-2"
        x7.put(f.plan_path, {"plan_id": f.plan.plan_id, "fixture_only": True})
        f.record["plan"] = q.reference(f.plan_path)
        x7.put(f.record_path, f.record)
        f.go.update(plan_id=f.plan.plan_id, plan_sha256=q.sha(f.plan_path))
        x7.put(f.night / "go_receipt.json", f.go)
        (f.off_path.parent / "clock-reference.json").unlink()
        f.off = capture_off(f.off_path, frozen_id, f.record["window_id"], f.go["boot_session_id"].lower())
        self.assertNotEqual(f.plan.plan_id, frozen_id)
        self.assertEqual(f.close()["status"], "COMPLETE")
        closed = q.read(f.stage_dir / "close_out.json")
        self.assertEqual(closed["off_identity"]["plan_id"], frozen_id)


class AdmissionAssessmentTests(unittest.TestCase):
    def setUp(self):
        f = self.fixture = harvest_tests.G2bStructureTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        self.root = f.runs
        self.success = f.runs / f.ids[1]
        x7.AttemptHistoryTests.admission(self, f.ids[2], {"none": True})
        for run_id in (f.ids[0], f.ids[3]):
            shutil.rmtree(f.runs / run_id)
        self.custody = f.base / "admission-night"
        self.night = self.custody / "night"
        x7.put(self.night / "chain.started", {"pgid": 99999999, "pid": 99999999})
        chain = f.base / "admission-chain.zsh"
        chain.write_text("export V5_QUALIFICATION_OCCURRENCE=s1\nexit 1\n")
        self.plan_path = self.custody / "night_plan.json"
        self.plan = x7.bind_history_fixture(self.plan_path, SimpleNamespace(
            plan_id="admission-attempt", custody_root=str(self.custody), chain_path=str(chain),
            chain_sha256_path=str(chain) + ".sha256", pack_night={
                "pack_id": writer.GAMMA, "pack_root": str(f.pack)}), f.base / "block-archive")
        self.bound = f.base / "bound"
        self.bound.mkdir()
        self.refs = {name: x7.put(f.base / (name + ".json"), {})
                     for name in ("policy", "acceptance", "go", "consumption", "battery_boundaries")}
        inputs = f.base / "inputs.json"
        x7.put(inputs, {"schema": g2b.INPUT_SCHEMA, "occurrence": "s1", "plan": q.reference(self.plan_path),
            "custody_root": str(f.custody), "bound_runs_root": str(self.bound), **self.refs})
        self.args = SimpleNamespace(inputs=inputs, inputs_sha256=q.sha(inputs),
            archive_root=Path(self.plan.block_archive_root) / "attempts" / self.plan.plan_id,
            scratch_root=f.base, prepare_desk=False, previous_harvest=None)
        # Only external launch/battery validation and strict fixture shape are
        # adapters. Native abort replay, shared member/clock assessment,
        # disposition, immutable archive and history run their real code.
        for obj, name, value in ((q, "load_plan", self.plan), (g2b, "authenticate_launch", {}),
                                (q, "battery_boundaries", True),
                                (g2b, "battery_attempts", (True, [])), (g2b, "validate_bundle", [])):
            patch = mock.patch.object(obj, name, return_value=value)
            patch.start()
            self.addCleanup(patch.stop)

    def harvest(self):
        return g2b.harvest(self.args, clear=lambda *a, **kw: True)

    def test_unbounded_success_then_admission_abort_is_physics_end_state(self):
        metadata = q.read(self.success / "metadata.json")
        metadata["uncertainty_evidence"]["clock_anchor"]["status"] = "unbounded"
        x7.put(self.success / "metadata.json", metadata)
        result = self.harvest()
        self.assertEqual(result["verdict"], "RECOVER", result)
        self.assertIn("member_not_strict_valid_bounded_success", result["cause_codes"])
        self.assertEqual(result["cause_classes"], ["instrument_physics"])
        self.assertTrue(result["end_state"])
        self.assertEqual(result["next_step"], "design_consult_cold_gate")
        self.assertFalse(q.is_admission_abort(result))
        self.assertEqual(result["members"][0]["clock_anchor_status"], "unbounded")
        prior = q.reference(self.args.archive_root / "harvest.json")
        with self.assertRaisesRegex(q.HarvestRefusal, "fresh_s1_predecessor_not_rearmable"):
            q.attempt_history(x7.attempt("fresh", prior), self.plan.block_archive_root)

    def test_observer_write_fault_only_affects_qualification(self):
        (self.night / "producer-faults.jsonl").write_text(
            '{"producer":"HID_observer","fault":"fixture observation write error"}\n')
        result = self.harvest()
        self.assertEqual(result["verdict"], "RECOVER", result)
        self.assertEqual(result["cause_codes"], [q.ADMISSION_ABORT_CODE])
        self.assertFalse(result["end_state"])
        self.assertTrue(q.is_admission_abort(result))
        self.assertIn("fresh_s1", result["next_step"])
        args = SimpleNamespace(plan=self.plan_path, archive_root=self.args.archive_root / "qualification",
            battery_evidence=Path(self.refs["battery_boundaries"]["path"]),
            battery_evidence_sha256=self.refs["battery_boundaries"]["sha256"], previous_harvest=None)
        qualified = qualification.harvest(args, clear=lambda *a, **kw: True)
        self.assertEqual(qualified["verdict"], "FAIL", qualified)
        self.assertEqual(qualified["cause_codes"], ["qualification_observation_producer_fault"])
        self.assertEqual(qualified["cause_classes"], ["tooling"])
        self.assertFalse(qualified["end_state"])
        prior = q.reference(self.args.archive_root / "harvest.json")
        proof = q.attempt_history(x7.attempt("fresh", prior), self.plan.block_archive_root)
        q.authenticate_attempt_record(result, Path(self.plan.block_archive_root))
        self.assertEqual(proof["admission_abort_count"], 1)

    def test_both_harvesters_refuse_lower_number_before_archive_publication(self):
        self.harvest()
        attempt = self.args.archive_root
        # A reserved replay without a verdict still consumes its number.
        (attempt / "reharvest-10").mkdir()
        lower = attempt / "reharvest-2"
        self.args.archive_root = lower
        self.args.previous_harvest = attempt
        args = SimpleNamespace(plan=self.plan_path, archive_root=lower,
            battery_evidence=Path(self.refs["battery_boundaries"]["path"]),
            battery_evidence_sha256=self.refs["battery_boundaries"]["sha256"],
            previous_harvest=attempt / "qualification")
        for harvest in (self.harvest, lambda: qualification.harvest(args, clear=lambda *a, **kw: True)):
            with self.subTest(harvest=harvest):
                with self.assertRaisesRegex(q.HarvestRefusal, "attempt_reharvest_number_not_increasing"):
                    harvest()
                self.assertFalse(lower.exists())


class RepeatedNullWriterTests(unittest.TestCase):
    def setUp(self):
        self.fixture = x7.WriterHistoryTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def two_nulls(self, first_codes, second_codes):
        f = self.fixture.fixture
        first = self.fixture.prior("NULL")
        record = q.read(Path(first["path"]))
        first = x7.put(Path(first["path"]), dict(record, cause_codes=first_codes))
        path = f.root / "prior-2/night_plan.json"
        chain = f.root / "prior-2-chain.zsh"
        chain.write_text("export V5_QUALIFICATION_OCCURRENCE=s1\nexit 0\n")
        plan = x7.bind_history_fixture(path, SimpleNamespace(plan_id="prior-2", custody_root=str(path.parent),
            chain_path=str(chain), chain_sha256_path=str(chain) + ".sha256", pack_night={
                "pack_id": f.pack.name, "pack_root": str(f.pack)}),
            Path(f.input["block_archive_root"]), previous=first)
        second = x7.put(Path(plan.block_archive_root) / "attempts/prior-2/harvest.json",
            q.attempt_record(plan, path, "s1", verdict="NULL", cause_codes=second_codes, cause_classes=[]))
        f.input["previous_attempt"] = second
        return f

    def test_same_null_code_set_refuses_third_writer_before_authorization(self):
        f = self.two_nulls(["t0_refused", "chain_never_started"], ["chain_never_started", "t0_refused"])
        with self.assertRaisesRegex(q.HarvestRefusal, "same_refusal_twice") as refusal:
            f.write()
        self.assertEqual(refusal.exception.refusal_codes, ["chain_never_started", "t0_refused"])
        self.assertFalse((f.custody / "authorization_record.json").exists())
        self.assertFalse(f.output.exists())

    def test_same_null_codes_are_named_by_writer_cli(self):
        f = self.two_nulls(["chain_never_started"], ["chain_never_started"])
        f.bind_clock_sizing()
        inputs = f.root / "third-inputs.json"
        x7.put(inputs, f.input)
        output = io.BytesIO()
        with mock.patch.object(writer.sys, "stdout", SimpleNamespace(buffer=output)):
            status = writer.main(["s1", "--inputs", str(inputs), "--output", str(f.output)])
        self.assertEqual(status, 2)
        result = q.readiness.parse_json_bytes(output.getvalue())
        self.assertEqual(result["reason_code"], "same_refusal_twice", result)
        self.assertEqual(result["cause_codes"], ["chain_never_started"])
        self.assertFalse((f.custody / "authorization_record.json").exists())

    def test_different_second_null_code_permits_third_writer(self):
        f = self.two_nulls(["chain_never_started"], ["different_t0_refusal"])
        f.write()
        self.assertTrue((f.custody / "authorization_record.json").is_file())
        self.assertEqual(q.read(f.output)["previous_attempt"], f.input["previous_attempt"])


class StageDigestTests(unittest.TestCase):
    def test_single_row_substitution_refused_by_digest_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            path = root / "before_midpoint_stages.txt"
            original = b"configs/campaigns/science\n"
            chain = ('test "$(/usr/bin/shasum -a 256 "$1/before_midpoint_stages.txt" | '
                     "/usr/bin/awk '{print $1}')\" = \"" + q.readiness.sha256_bytes(original) + '"\n').encode()
            path.write_bytes(original)
            self.assertEqual(q.readiness.authenticated_stage_list(root, chain), q.reference(path))
            # Still one unique, relative configs/ row with a canonical newline.
            # Only authentication against the chain's digest can reject it.
            path.write_bytes(b"configs/campaigns/other\n")
            with self.assertRaisesRegex(ValueError, "differs from its authenticated chain"):
                q.readiness.authenticated_stage_list(root, chain)


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.archive = self.root / "block-harvests"
        self.archive.mkdir()

    def save(self, record):
        return x7.put(self.archive / "attempts" / record["plan_id"] / "harvest.json", record)

    def history(self, record):
        return q.attempt_history(record, self.archive)

    def tooling(self, name, previous):
        return x7.attempt(name, previous, verdict="RECOVER", cause_codes=["named_tooling_fault"], cause_classes=["tooling"])

    def test_cold_pass_four_line_matrix(self):
        first = self.save(self.tooling("s1-a", {"none": True}))
        null_s2 = self.save(x7.attempt("s2-b", first, occurrence="s2"))
        # The cold pass's four lines, with addendum F.4's ruled outcomes:
        # control: fresh s1 straight after s1 RECOVER(tooling): REFUSED
        # second s2 after s2 NULL:                            ALLOWED
        # fresh s1 after s1 RECOVER(tooling) -> s2 NULL:      REFUSED
        # s2 after that launched s1 (third block launch):    REFUSED
        with self.assertRaisesRegex(q.HarvestRefusal, "fresh_s1_predecessor_not_rearmable"):
            self.history(x7.attempt("s1-c", null_s2))
        proof = self.history(x7.attempt("s2-c", null_s2, occurrence="s2", verdict="REFUSED"))
        self.assertEqual((proof["s2_count"], proof["admission_abort_count"]), (1, 0))
        Path(null_s2["path"]).unlink()
        with self.assertRaisesRegex(q.HarvestRefusal, "fresh_s1_predecessor_not_rearmable"):
            self.history(x7.attempt("s1-control", first))
        null_s2 = self.save(x7.attempt("s2-b", first, occurrence="s2"))
        launched = self.save(self.tooling("s1-c", null_s2))
        with self.assertRaisesRegex(q.HarvestRefusal, "fresh_s1_predecessor_not_rearmable"):
            self.history(x7.attempt("s2-d", launched, occurrence="s2", verdict="REFUSED"))

    def test_multiple_null_s2_spend_nothing(self):
        prior = self.save(self.tooling("s1", {"none": True}))
        for index in range(3):
            record = x7.attempt(f"null-{index}", prior, occurrence="s2", cause_codes=[f"different_refusal_{index}"])
            proof = self.history(record)
            self.assertEqual((proof["s2_count"], proof["admission_abort_count"]), (0, 0))
            prior = self.save(record)
        self.assertEqual(self.history(x7.attempt("s2", prior, occurrence="s2", verdict="PASS"))["s2_count"], 1)

    def test_two_nulls_report_repeated_codes_before_blocking_next_spend(self):
        first = self.save(x7.attempt("first", {"none": True}, cause_codes=["t0_refused", "chain_never_started"]))
        second = x7.attempt("second", first, cause_codes=["chain_never_started", "t0_refused"])
        proof = self.history(second)
        self.assertTrue(proof["same_refusal_twice"])
        self.assertEqual(proof["same_refusal_codes"], ["chain_never_started", "t0_refused"])
        self.assertEqual((proof["s2_count"], proof["admission_abort_count"]), (0, 0))
        prior = self.save(second)
        with self.assertRaisesRegex(q.HarvestRefusal, "same_refusal_twice"):
            self.history(x7.attempt("third", prior))

    def test_nonadjacent_matching_null_codes_do_not_trigger_consult(self):
        first = self.save(x7.attempt("first", {"none": True}, cause_codes=["refusal_a"]))
        second = self.save(x7.attempt("second", first, cause_codes=["refusal_b"]))
        proof = self.history(x7.attempt("third", second, cause_codes=["refusal_a"]))
        self.assertFalse(proof["same_refusal_twice"])
        self.assertEqual(proof["same_refusal_codes"], [])

    def reharvest(self, verdict, *, number=1, previous=None):
        original = x7.attempt("s1", {"none": True}, verdict="REFUSED", cause_classes=["tooling"])
        unit = self.archive / "attempts/s1"
        source = self.root / "source.json"
        if not source.exists():
            x7.put(source, {"fixture": "immutable attempt bytes"})
            q.archive_sources({"capture": source}, unit)
            self.save(original)
        replay = unit / f"reharvest-{number}"
        plan = SimpleNamespace(plan_id="s1", block_archive_root=str(self.archive))
        q.attempt_destination(plan, replay, replay=previous or unit)
        q.archive_sources({"capture": source}, replay, previous=previous or unit)
        record = dict(original, verdict=verdict, cause_classes=["tooling"] if verdict == "RECOVER" else [],
                      cause_codes=["named_tooling_fault"] if verdict == "RECOVER" else ["chain_never_started"])
        x7.put(replay / "harvest.json", record)
        return record, plan, unit, replay

    def test_refused_then_null_reharvest_allows_fresh_s1(self):
        record, plan, unit, replay = self.reharvest("NULL")
        original = (unit / "harvest.json").read_bytes()
        self.assertEqual(q.checked_history(record, plan, replay=True)["s2_count"], 0)
        self.assertEqual(self.history(x7.attempt("fresh", q.reference(unit / "harvest.json")))["s2_count"], 0)
        self.assertEqual((unit / "harvest.json").read_bytes(), original)

    def test_refused_then_tooling_reharvest_allows_s2(self):
        record, plan, unit, replay = self.reharvest("RECOVER")
        q.checked_history(record, plan, replay=True)
        self.assertEqual(self.history(x7.attempt("s2", q.reference(unit / "harvest.json"), occurrence="s2", verdict="PASS"))["s2_count"], 1)

    def test_first_non_refused_numeric_reharvest_counts(self):
        first, _, _, _ = self.reharvest("RECOVER", number=2)
        record, plan, unit, replay = self.reharvest("NULL", number=10)
        q.checked_history(record, plan, replay=True)
        self.assertEqual(q.counted_attempt(q.read(unit / "harvest.json"), unit / "harvest.json"), first)
        with self.assertRaisesRegex(q.HarvestRefusal, "fresh_s1_predecessor_not_rearmable"):
            self.history(x7.attempt("fresh", q.reference(unit / "harvest.json")))
        self.assertEqual(self.history(x7.attempt("s2", q.reference(unit / "harvest.json"),
                                               occurrence="s2", verdict="PASS"))["s2_count"], 1)

    def test_lower_number_written_later_refuses_before_publication(self):
        record, plan, unit, replay = self.reharvest("RECOVER", number=2)
        physics = dict(record, cause_classes=["instrument_physics"],
                       cause_codes=["member_not_strict_valid_bounded_success"], end_state=True)
        x7.put(replay / "harvest.json", physics)
        q.checked_history(physics, plan, replay=True)
        before = {path: path.read_bytes() for path in unit.rglob("*") if path.is_file()}
        with self.assertRaisesRegex(q.HarvestRefusal, "attempt_reharvest_number_not_increasing"):
            self.reharvest("NULL", number=1)
        self.assertFalse((unit / "reharvest-1").exists())
        self.assertEqual({path: path.read_bytes() for path in unit.rglob("*") if path.is_file()}, before)
        self.assertEqual(q.counted_attempt(q.read(unit / "harvest.json"), unit / "harvest.json"), physics)
        with self.assertRaisesRegex(q.HarvestRefusal, "fresh_s1_predecessor_not_rearmable"):
            self.history(x7.attempt("fresh", q.reference(unit / "harvest.json"), verdict="REFUSED"))

    def test_lower_number_pending_path_refuses_before_archiving(self):
        record, plan, unit, replay = self.reharvest("RECOVER", number=2)
        physics = dict(record, cause_classes=["instrument_physics"],
                       cause_codes=["member_not_strict_valid_bounded_success"], end_state=True)
        x7.put(replay / "harvest.json", physics)
        q.checked_history(physics, plan, replay=True)
        with self.assertRaisesRegex(q.HarvestRefusal, "attempt_reharvest_number_not_increasing"):
            self.reharvest("RECOVER", number=1)
        self.assertFalse((unit / "reharvest-1").exists())
        with self.assertRaisesRegex(q.HarvestRefusal, "s2_not_after_named_tooling_recover"):
            self.history(x7.attempt("s2", q.reference(unit / "harvest.json"), occurrence="s2", verdict="REFUSED"))

    def test_reharvest_number_reserves_unpublished_and_qualification_directories(self):
        _, plan, unit, _ = self.reharvest("REFUSED", number=2)
        for number, verdict_kind in ((7, None), (10, "qualification")):
            reserved = unit / f"reharvest-{number}"
            reserved.mkdir()
            if verdict_kind:
                x7.put(reserved / "harvest.json", {"verdict_kind": verdict_kind, "verdict": "REFUSED"})
            with self.subTest(number=number, verdict_kind=verdict_kind):
                for candidate in (number - 1, number):
                    with self.assertRaisesRegex(q.HarvestRefusal, "attempt_reharvest_number_not_increasing"):
                        q.attempt_destination(plan, unit / f"reharvest-{candidate}", replay=unit)
                higher = unit / f"reharvest-{number + 1}"
                self.assertEqual(q.attempt_destination(plan, higher, replay=unit), unit)
                self.assertFalse(higher.exists())

    def test_refused_reharvest_then_null_counts_null(self):
        self.reharvest("REFUSED", number=1)
        record, plan, unit, replay = self.reharvest("NULL", number=2)
        q.checked_history(record, plan, replay=True)
        self.assertEqual(q.counted_attempt(q.read(unit / "harvest.json"), unit / "harvest.json"), record)
        self.history(x7.attempt("fresh", q.reference(unit / "harvest.json")))

    def test_cold_pass_reharvest_real_verdict_is_final(self):
        record, plan, unit, replay = self.reharvest("RECOVER", number=1)
        physics = dict(record, cause_classes=["instrument_physics"],
                       cause_codes=["member_not_strict_valid_bounded_success"], end_state=True)
        x7.put(replay / "harvest.json", physics)
        original = (unit / "harvest.json").read_bytes()
        prior = q.reference(unit / "harvest.json")
        q.checked_history(physics, plan, replay=True)
        # Cold-pass matrix: physics re-harvest blocks both launches; later
        # NULL and tooling verdicts of the same bytes cannot reopen them.
        with self.assertRaisesRegex(q.HarvestRefusal, "fresh_s1_predecessor_not_rearmable"):
            self.history(x7.attempt("fresh", prior, verdict="REFUSED"))
        with self.assertRaisesRegex(q.HarvestRefusal, "s2_not_after_named_tooling_recover"):
            self.history(x7.attempt("s2", prior, occurrence="s2", verdict="REFUSED"))
        record, plan, unit, replay = self.reharvest("NULL", number=2)
        q.checked_history(record, plan, replay=True)
        with self.assertRaisesRegex(q.HarvestRefusal, "fresh_s1_predecessor_not_rearmable"):
            self.history(x7.attempt("fresh", prior, verdict="REFUSED"))
        record, plan, unit, replay = self.reharvest("RECOVER", number=3)
        q.checked_history(record, plan, replay=True)
        with self.assertRaisesRegex(q.HarvestRefusal, "s2_not_after_named_tooling_recover"):
            self.history(x7.attempt("s2", prior, occurrence="s2", verdict="REFUSED"))
        self.assertEqual((unit / "harvest.json").read_bytes(), original)

    def test_cold_pass_original_real_verdict_is_final(self):
        _, _, unit, _ = self.reharvest("NULL")
        original = dict(q.read(unit / "harvest.json"), verdict="RECOVER",
                        cause_classes=["instrument_physics"],
                        cause_codes=["member_not_strict_valid_bounded_success"], end_state=True)
        self.save(original)
        with self.assertRaisesRegex(q.HarvestRefusal, "fresh_s1_predecessor_not_rearmable"):
            self.history(x7.attempt("fresh", q.reference(unit / "harvest.json"), verdict="REFUSED"))

    def test_reharvest_changed_source_bytes_refuse(self):
        record, plan, unit, replay = self.reharvest("NULL")
        (replay / "withheld/sources/capture").write_text("different capture bytes")
        with self.assertRaisesRegex(q.HarvestRefusal, "reharvest_source_bytes_changed"):
            q.checked_history(record, plan, replay=True)

    def test_self_consistent_reharvest_of_different_source_bytes_refuses(self):
        record, plan, unit, replay = self.reharvest("NULL")
        source = self.root / "source.json"
        x7.put(source, {"fixture": "different attempt bytes"})
        changed = unit / "reharvest-2"
        q.archive_sources({"capture": source}, changed)
        x7.put(changed / "harvest.json", record)
        with self.assertRaisesRegex(q.HarvestRefusal, "reharvest_source_bytes_changed"):
            q.checked_history(record, plan, replay=True)

    def test_reharvest_changed_identity_refuses(self):
        record, plan, unit, replay = self.reharvest("NULL")
        x7.put(replay / "harvest.json", dict(record, occurrence="s2"))
        with self.assertRaisesRegex(q.HarvestRefusal, "attempt_reharvest_identity_mismatch"):
            q.checked_history(record, plan, replay=True)

    def test_pending_reharvest_authenticates_census_before_publication(self):
        record, plan, unit, replay = self.reharvest("NULL")
        (replay / "harvest.json").unlink()
        q.checked_history(record, plan, replay=True, reharvest=replay)
        (replay / "withheld/sources/capture").write_text("different bytes")
        with self.assertRaisesRegex(q.HarvestRefusal, "reharvest_source_bytes_changed"):
            q.checked_history(record, plan, replay=True, reharvest=replay)

    def test_later_refused_does_not_supersede_first_null(self):
        self.reharvest("NULL", number=1)
        record, plan, unit, replay = self.reharvest("REFUSED", number=2)
        q.checked_history(record, plan, replay=True)
        self.history(x7.attempt("fresh", q.reference(unit / "harvest.json")))


class AuthorityTests(unittest.TestCase):
    def test_s2_authority_replays_nearest_non_null_s1(self):
        f = x7.WriterHistoryTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        f.s2()
        fixture = f.fixture
        plan = q.night_gate.NightPlan.from_mapping(q.read(fixture.output))
        null = q.attempt_record(plan, fixture.output, "s2", verdict="NULL", cause_classes=[], cause_codes=["chain_never_started"])
        null_pointer = x7.put(Path(plan.block_archive_root) / "attempts" / plan.plan_id / "harvest.json", null)
        authority = q.read(Path(fixture.input["s2_authority"]["path"]))
        authority["new_plan_id"] = "rearmed-s2"
        reference = x7.put(fixture.root / "rearmed-authority.json", authority)
        q.authenticate_s2_authority(reference, "rearmed-s2", null_pointer)
        provisional = x7.attempt("rearmed-s2", null_pointer, occurrence="s2", verdict="REFUSED")
        self.assertEqual(q.attempt_history(provisional, plan.block_archive_root)["s2_count"], 1)
        # The authority still names the counted s1's stable original pointer.
        bad = x7.put(fixture.root / "wrong-authority.json", dict(authority, s1_harvest=null_pointer))
        with self.assertRaisesRegex(q.HarvestRefusal, "s2_not_authorized_tooling_cure"):
            q.authenticate_s2_authority(bad, "rearmed-s2", null_pointer)

    def test_writer_counts_null_reharvest_of_refused_original(self):
        f = x7.WriterHistoryTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        prior = f.prior("REFUSED")
        path = Path(prior["path"])
        original = q.read(path)
        path.unlink()
        path.parent.rmdir()
        q.archive_sources({"plan": Path(original["plan"]["path"])}, path.parent)
        x7.put(path, original)
        replay = path.parent / "reharvest-1"
        q.archive_sources({"plan": Path(original["plan"]["path"])}, replay, previous=path.parent)
        x7.put(replay / "harvest.json", dict(original, verdict="NULL"))
        self.assertEqual(q.reference(path), prior)
        f.fixture.write()
        self.assertEqual(q.read(f.fixture.output)["previous_attempt"], prior)


class RestoreTests(unittest.TestCase):
    def test_retained_pin_digest_mismatch_refuses(self):
        f = x7.NullReservationTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        fixture, live, seed, pin, harvest, raw = f.restore_fixture()
        restored = restore.restore(q.reference(fixture.output), harvest, q.reference(seed),
            output=fixture.custody / "null-reservation-restore.json")
        record = q.read(Path(restored["path"]))
        Path(record["head_pin_copy"]["path"]).write_text("changed retained pin bytes")
        with self.assertRaisesRegex(q.HarvestRefusal, "locator_digest_mismatch"):
            restore.verify_restore(restored, harvest)

    def test_pin_advance_does_not_void_restored_attempt_history(self):
        f = x7.NullReservationTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        fixture, live, seed, pin, harvest, raw = f.restore_fixture()
        restored = restore.restore(q.reference(fixture.output), harvest, q.reference(seed),
            output=fixture.custody / "null-reservation-restore.json")
        pin_before = q.reference(pin)
        plan = q.night_gate.NightPlan.from_mapping(q.read(fixture.output))
        path = fixture.root / "fresh/night_plan.json"
        chain = fixture.root / "fresh-chain.zsh"
        chain.write_text(f"export CALIBRATION_LEDGER={live}\nexport LEDGER_HEAD_PIN={pin}\nexit 0\n")
        current_plan = x7.bind_history_fixture(path, SimpleNamespace(plan_id="fresh", custody_root=str(path.parent),
            chain_path=str(chain), chain_sha256_path=str(fixture.root / "fresh-chain.sha256"), pack_night=plan.pack_night),
            Path(plan.block_archive_root), previous=harvest)
        value = q.read(path)
        value["null_reservation_restore"] = restored
        auth_path = Path(value["pack_night"]["authorization_record"]["path"])
        auth = q.read(auth_path)
        auth["null_reservation_restore"] = restored
        value["pack_night"]["authorization_record"] = x7.put(auth_path, auth)
        x7.put(path, value)
        current_plan = q.night_gate.NightPlan.from_mapping(value)
        x7.put(pin, dict(f.pin, sequence=2, head_digest=f.row["receipt_digest"]))
        self.assertNotEqual(q.reference(pin), pin_before)
        self.assertEqual(restore.verify_restore(restored, harvest)["head_pin"], pin_before)
        current = q.attempt_record(current_plan, path, "s1", verdict="NULL", cause_classes=[], cause_codes=["chain_never_started"])
        self.assertEqual(q.checked_history(current, current_plan)["harvests"], [harvest])


if __name__ == "__main__":
    unittest.main()
