"""Addendum F harvest/history regressions on desk fixtures, never hardware."""
from pathlib import Path
import copy
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import network_time_off, v5_qualification as q
from scripts import capture_t0_step as capture, restore_v5_null_reservation as restore
from scripts import v5_s1_desk_closeout as desk
from tests import test_v5_block4_x7 as x7, test_v5_block4_x2 as x2
from tests import test_v5_s1_desk_closeout as desk_tests
from tests.test_arm_readiness_evidence_t0 import _clock_reference_value


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
            record = x7.attempt(f"null-{index}", prior, occurrence="s2")
            proof = self.history(record)
            self.assertEqual((proof["s2_count"], proof["admission_abort_count"]), (0, 0))
            prior = self.save(record)
        self.assertEqual(self.history(x7.attempt("s2", prior, occurrence="s2", verdict="PASS"))["s2_count"], 1)

    def reharvest(self, verdict, *, number=1, previous=None):
        original = x7.attempt("s1", {"none": True}, verdict="REFUSED", cause_classes=["tooling"])
        unit = self.archive / "attempts/s1"
        source = self.root / "source.json"
        if not source.exists():
            x7.put(source, {"fixture": "immutable attempt bytes"})
            q.archive_sources({"capture": source}, unit)
            self.save(original)
        replay = unit / f"reharvest-{number}"
        q.archive_sources({"capture": source}, replay, previous=previous or unit)
        record = dict(original, verdict=verdict, cause_classes=["tooling"] if verdict == "RECOVER" else [],
                      cause_codes=["named_tooling_fault"] if verdict == "RECOVER" else ["chain_never_started"])
        x7.put(replay / "harvest.json", record)
        plan = SimpleNamespace(plan_id="s1", block_archive_root=str(self.archive))
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

    def test_newest_numeric_reharvest_counts(self):
        self.reharvest("RECOVER", number=2)
        record, plan, unit, replay = self.reharvest("NULL", number=10)
        q.checked_history(record, plan, replay=True)
        self.history(x7.attempt("fresh", q.reference(unit / "harvest.json")))

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

    def test_newest_refused_does_not_fall_back_to_older_null(self):
        self.reharvest("NULL", number=1)
        record, plan, unit, replay = self.reharvest("REFUSED", number=2)
        q.checked_history(record, plan, replay=True)
        with self.assertRaisesRegex(q.HarvestRefusal, "fresh_s1_predecessor_not_rearmable"):
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
