from tests import restore_factory
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

from joulewise.hazards import network_time as network_time_off; from tests import qualification_factory as q
from joulewise import qualification_readers as restore
from scripts import qualification_harvest_readers as g2b
from tests import qualification_plan_factory as writer
from tests import test_v5_block4_x7 as x7, test_v5_block4_x2 as x2
from tests import test_harvest_v5_g2b_window as harvest_tests








class AdmissionAssessmentTests(unittest.TestCase):
    pass
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













class HistoryTests(unittest.TestCase):
    pass
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
    pass
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
    pass
    def test_retained_pin_digest_mismatch_refuses(self):
        f = x7.NullReservationTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        fixture, live, seed, pin, harvest, raw = f.restore_fixture()
        restored = restore_factory.restore(q.reference(fixture.output), harvest, q.reference(seed),
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
        restored = restore_factory.restore(q.reference(fixture.output), harvest, q.reference(seed),
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
