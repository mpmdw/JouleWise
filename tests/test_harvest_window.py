"""Synthetic finished-window harvests; all machine actions are injected."""
from __future__ import annotations

import argparse
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts import harvest_window as harvest
from joulewise.measurement_liveness import Census
from tests.fixtures.epoch_bootstrap import build


class HarvestWindowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.calls = []
        self.uninstall_rc = 0

    def fixture(self, slots=None, *, verdict_records=True, manual_bad=False,
                fill_slots=None, abort_reason=None, no_recording=False):
        self.plan_bytes = harvest.json_bytes({"plan_id": "plan-derivation"})
        original_write = build._write_bundle
        original_append = build.append_bracket_session_receipt

        def write_bundle(path, attempt, slot):
            original_write(path, attempt, slot)
            if no_recording:
                (path / "raw/powermetrics.plist").unlink()
            if manual_bad:
                evidence = json.loads((path / "instrument_evidence.json").read_bytes())
                evidence["battery_float"]["pre"]["probe_error"] = True
                evidence["battery_float"]["post"]["passed"] = False
                (path / "instrument_evidence.json").write_bytes(harvest.json_bytes(evidence))
            artifacts = {name: harvest.digest((path / name).read_bytes()) for name in
                         ("events.jsonl", "instrument_evidence.json", "raw/powermetrics.plist")
                         if (path / name).is_file()}
            (path / "manifest.json").write_bytes(harvest.json_bytes({"artifacts": artifacts}))

        def append(*a, **kw):
            kw["plan_sha256"] = harvest.digest(self.plan_bytes)
            return original_append(*a, **kw)

        with mock.patch.object(build, "_write_bundle", write_bundle), mock.patch.object(
                build, "append_bracket_session_receipt", append):
            self.f = build.build_derivation_ledger(
                self.base / "measurement", slots or [build.Slot("0.02", native_frames=True)],
                custody_parent=self.base / "night-custody", verdict_records=verdict_records,
                fill_slots=fill_slots, abort_reason=abort_reason)
        self.night = self.base / "night-custody" / build.SESSION_ID
        (self.night / "calibration_plan.json").write_bytes(self.plan_bytes)
        self.head = subprocess.run(["git", "-C", str(self.f["root"]), "rev-parse", "HEAD"],
                                   check=True, capture_output=True, text=True).stdout.strip()
        exports = {"SESSION_ID": build.SESSION_ID, "PLAN_ID": "plan-derivation",
                   "PLAN": str(self.night / "calibration_plan.json"),
                   "PLAN_SHA256": harvest.digest(self.plan_bytes),
                   "RUNS_ROOT": str(self.night / "runs"),
                   "WINDOW_CUSTODY_ROOT": str(self.night),
                   "CALIBRATION_LEDGER": str(self.f["ledger"]), "LEDGER_HEAD_PIN": str(self.f["pin"])}
        wrapper = "\n".join(f"export {key}='{value}'" for key, value in exports.items()) + "\n"
        (self.night / "chain.zsh").write_text(wrapper)
        (self.night / "chain.zsh.sha256").write_text(harvest.digest(wrapper.encode()) + "  chain.zsh\n")
        self.plan = {"schema": "joulewise.night_plan.v2", "schema_version": 2,
                     "plan_id": build.SESSION_ID, "receipt_class": "DIAGNOSTIC_NO_PACK",
                     "t0_epoch_s": 100.0, "authored_epoch_s": 50.0, "window_max_s": 9000,
                     "repo_head": self.head, "measurement_head": self.head,
                     "measurement_root": str(self.f["root"]), "custody_root": str(self.night),
                     "chain_path": str(self.night / "chain.zsh"),
                     "chain_sha256_path": str(self.night / "chain.zsh.sha256"),
                     "registration_path": str(build.REPO_ROOT / "configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json")}
        (self.night / "night_plan.json").write_bytes(harvest.json_bytes(self.plan))
        (self.night / "night").mkdir()
        (self.night / "night/courier.sent").write_text("sent\n")
        (self.night / "night/chain.started").write_text('{"pid":123}')
        (self.night / "night/chain.exited").write_text('{"exit_code":0,"epoch_s":9000,"monotonic_ns":1}')
        self.args = argparse.Namespace(plan=self.night / "night_plan.json", custody=self.base / "archive",
                                       preregistration=build.REPO_ROOT / "configs/calibration/preregistration_d079_epoch_25g83_rev1.md",
                                       preregistration_sha256=build.PREREGISTRATION_SHA256, session_ids=None)
        return self.args

    def runner(self, argv, **kw):
        self.calls.append(argv)
        if argv[0] == "git":
            return subprocess.CompletedProcess(argv, 0, self.head + "\n", "")
        self.assertEqual(argv, [str(self.f["root"] / "scripts/install_night_agent.sh"),
                                "--plan", str(self.args.plan), "--uninstall"])
        return subprocess.CompletedProcess(argv, self.uninstall_rc, "", "")

    def run_harvest(self, **kw):
        return harvest.harvest(self.args, runner=self.runner, census=lambda **_: Census(),
                               now=lambda: 10000, **kw)

    def revision6_fixture(self, slots=None, **kw):
        self.fixture(slots, **kw)
        start = {"schema": "joulewise.revision6.start_conditions.v1",
                 "session_id": build.SESSION_ID, "plan_id": json.loads(self.plan_bytes)["plan_id"],
                 "result": "admitted", "refusal_reason": None, "evidence": {},
                 "boot_id": "synthetic-boot", "written_epoch_s": 100,
                 "written_monotonic_s": 50,
                 "chain_start_admitted": {"epoch_s": 100.0, "monotonic_s": 50.0}}
        (self.night / "night/start_conditions.json").write_bytes(harvest.json_bytes(start))
        (self.night / "night/chain.exited").write_bytes(harvest.json_bytes(
            {"exit_code": 0, "epoch_s": 9000.25, "monotonic_ns": 1234567890123}))

    def replay_result(self, *, cells=2, frame=125.0, disposition="valid", trigger=None):
        return {"cells": cells, "median_frame_ms": frame, "ratio": cells / 100 if cells is not None else None,
                "disposition": disposition, "trigger": trigger, "replay_failed": frame is None,
                # Counterfactual input: even future accidental harness fields
                # cannot cross the harvest's explicitly enumerated projection.
                "b_fiducial_s": 987654321.012345, "exact_bound": 987654321.012345,
                "stored B reproduced": True, "elapsed_s": 999.0}

    def archived_r9(self, record):
        custody = Path(record["custody_root"])
        path = custody / record["r9_window"]["path"]
        self.assertEqual(harvest.digest(path.read_bytes()), record["r9_window"]["sha256"])
        return json.loads(path.read_bytes())

    def assert_blind_records(self, *records):
        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    lowered = key.lower()
                    self.assertFalse(lowered == "b" or "bound" in lowered
                                     or "b_fiducial" in lowered or "stored b" in lowered, key)
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)
        for record in records:
            walk(record)
            self.assertNotIn("987654321", harvest.json_bytes(record).decode())

    def test_revision6_record_schema_counts_and_authenticated_timing(self):
        self.revision6_fixture([build.Slot("987654321.012345", native_frames=True,
                                           disposition="ordinary-invalid" if i == 1 else "valid")
                                for i in range(12)])
        frames = [100.0, 150.0, 120.0, 99.0, 151.0] + [125.0] * 7
        replies = [self.replay_result(cells=0 if i == 2 else 2, frame=frame,
                                     disposition="ordinary-invalid" if i == 1 else "valid")
                   for i, frame in enumerate(frames)]
        before = harvest.inventory(self.night)
        with mock.patch.object(harvest.cap_replay_harness, "replay_capture", side_effect=replies) as replay:
            record = self.run_harvest()
        r9 = self.archived_r9(record)
        self.assertEqual(set(r9), {"schema", "session_id", "slots", "captures", "counted", "valid",
                                   "harness_sha256", "rule_ref"})
        self.assertEqual(r9["schema"], "joulewise.revision6.r9_window.v1")
        self.assertEqual((r9["session_id"], r9["slots"], r9["counted"], r9["valid"]),
                         (build.SESSION_ID, 12, 9, 11))
        self.assertEqual(r9["harness_sha256"], harvest.digest(Path(harvest.cap_replay_harness.__file__).read_bytes()))
        self.assertEqual(r9["rule_ref"], "CAP-COUNCIL-25G83-01 R9 as amended; Revision 6 §4")
        self.assertEqual([row["slot"] for row in r9["captures"]], list(range(1, 13)))
        for row, call in zip(r9["captures"], replay.call_args_list):
            self.assertEqual(set(row), {"slot", "capture_id", "content_id", "has_recording", "cells",
                                       "median_frame_ms", "ratio", "disposition", "cap_trigger",
                                       "median_frame_reported", "counted"})
            self.assertEqual(call.args, (self.night / "runs/instrument_validation" / row["capture_id"], "REPORT"))
            self.assertRegex(row["content_id"], r"^[0-9a-f]{64}$")
            self.assertTrue(row["has_recording"])
            self.assertTrue(row["median_frame_reported"])
        self.assertTrue(r9["captures"][1]["counted"])  # Invalid can still be counted.
        self.assertEqual(record["stop_flags"], [])
        self.assertEqual(record["window_end"], {"epoch_s": 9000.25, "monotonic_s": 1234.567890123,
                         "source": {"path": "night/chain.exited", "sha256": before["night/chain.exited"]["sha256"]}})
        self.assertEqual(record["start_conditions"], {"path": "night/start_conditions.json",
                         "sha256": before["night/start_conditions.json"]["sha256"]})
        self.assertEqual(record["boot_id"], "synthetic-boot")
        self.assertEqual(Path(record["custody_root"]), self.args.custody / "custody-root")
        self.assertEqual(before, harvest.inventory(self.night))
        for reference in (record["start_conditions"], record["window_end"]["source"]):
            self.assertEqual(harvest.digest((Path(record["custody_root"]) / reference["path"]).read_bytes()),
                             reference["sha256"])
        self.assert_blind_records(record, r9)
        with mock.patch.object(harvest.cap_replay_harness, "replay_capture", side_effect=replies):
            self.assertEqual(self.run_harvest(), record)
        self.assertEqual(len([argv for argv in self.calls if "--uninstall" in argv]), 1)

    def test_revision6_missing_reported_frame_flags_stop(self):
        self.revision6_fixture()
        with mock.patch.object(harvest.cap_replay_harness, "replay_capture",
                               return_value=self.replay_result(cells=None, frame=None)):
            record = self.run_harvest()
        r9 = self.archived_r9(record)
        self.assertEqual(record["stop_flags"], ["STOP-R9-FRAME"])
        self.assertEqual(record["next_window"]["verdict"], "STOP_TO_REVIEW")
        self.assertEqual((r9["counted"], r9["valid"]), (0, 1))
        self.assertFalse(r9["captures"][0]["median_frame_reported"])
        self.assertIsNone(r9["captures"][0]["median_frame_ms"])
        self.assertEqual(record["retained_captures"], 0)
        self.assert_blind_records(record, r9)

    def test_revision6_sampler_loss_or_mismatch_is_frame_stop(self):
        self.revision6_fixture([build.Slot("0.02", native_frames=True), build.Slot("0.03", native_frames=True)])
        raw_paths = sorted(self.night.glob("runs/instrument_validation/*/raw/powermetrics.plist"))
        raw_paths[0].unlink()
        raw_paths[1].write_bytes(b"tampered")
        record = self.run_harvest()  # Real REPORT input checks, no detector work.
        r9 = self.archived_r9(record)
        self.assertEqual(record["stop_flags"], ["STOP-R9-FRAME"])
        self.assertEqual(r9["counted"], 0)
        self.assertTrue(all(row["has_recording"] and not row["median_frame_reported"] for row in r9["captures"]))

    def test_revision6_no_recording_does_not_fire_frame_stop(self):
        self.revision6_fixture([build.Slot("0.02", disposition="ordinary-invalid", native_frames=True)], no_recording=True)
        with mock.patch.object(harvest.cap_replay_harness, "replay_capture",
                               return_value=self.replay_result(cells=None, frame=None, disposition="ordinary-invalid")):
            record = self.run_harvest()
        r9 = self.archived_r9(record)
        self.assertFalse(r9["captures"][0]["has_recording"])
        self.assertEqual(r9["captures"][0]["disposition"], "ordinary-invalid")
        self.assertEqual((r9["counted"], r9["valid"]), (0, 0))
        self.assertEqual(record["stop_flags"], [])

    def test_revision6_adverse_window_contributes_no_counts(self):
        self.revision6_fixture([build.Slot("0.02", native_frames=True, battery_mode="charging")])
        with mock.patch.object(harvest.cap_replay_harness, "replay_capture", return_value=self.replay_result(frame=None)):
            record = self.run_harvest()
        r9 = self.archived_r9(record)
        self.assertEqual((r9["counted"], r9["valid"]), (0, 0))
        self.assertEqual(record["stop_flags"], ["STOP-R9-FRAME"])

    def test_revision6_cap_triggers_are_preserved(self):
        self.revision6_fixture([build.Slot("0.02", native_frames=True)] * 3)
        replies = [self.replay_result(trigger="evaluated_cell_budget"),
                   self.replay_result(trigger="wall_deadline"), self.replay_result(cells=60)]
        with mock.patch.object(harvest.cap_replay_harness, "replay_capture", side_effect=replies):
            record = self.run_harvest()
        self.assertEqual(record["stop_flags"], [])
        self.assertEqual([row["cap_trigger"] for row in self.archived_r9(record)["captures"]],
                         ["evaluated_cell_budget", "wall_deadline", None])

    def test_revision6_malformed_exit_time_refuses(self):
        self.revision6_fixture()
        (self.night / "night/chain.exited").write_text('{"epoch_s":9000}')
        self.assert_refuses()

    def test_revision6_r9_tampering_refuses_immutable_retry(self):
        self.revision6_fixture()
        with mock.patch.object(harvest.cap_replay_harness, "replay_capture", return_value=self.replay_result()):
            record = self.run_harvest()
            path = Path(record["custody_root"]) / record["r9_window"]["path"]
            path.write_text("tampered")
            with self.assertRaisesRegex(harvest.HarvestRefusal, "overwrite"):
                self.run_harvest()
            self.assertEqual(path.read_text(), "tampered")

    def test_revision6_r9_directory_symlink_cannot_write_outside_archive(self):
        self.revision6_fixture()
        target = self.base / "protected-custody"
        target.mkdir()
        (target / "sentinel").write_bytes(b"unchanged")
        (self.night / "harvest").symlink_to(target, target_is_directory=True)
        before = harvest.inventory(target)
        with mock.patch.object(harvest.cap_replay_harness, "replay_capture", return_value=self.replay_result()):
            self.assert_refuses()
        self.assertEqual(harvest.inventory(target), before)

    def test_bound_leak_counterfactual_fails_blind_assertion(self):
        for key in ("B", "b_fiducial_s", "exact_bound", "stored B reproduced"):
            with self.subTest(key=key), self.assertRaises(AssertionError):
                self.assert_blind_records({"captures": [{key: 1}]})

    def assert_refuses(self):
        with self.assertRaises((ValueError, harvest.issuer.PrepareRefusal,
                                harvest.battery_float.CustodyFailure,
                                harvest.battery_float.BatteryVerdictRefusal)):
            self.run_harvest()
        self.assertFalse(self.args.custody.exists())
        self.assertFalse(any("--uninstall" in argv for argv in self.calls))

    def test_success_preserves_sources_copies_and_publishes_one_record(self):
        self.fixture([build.Slot("0.02", native_frames=True),
                      build.Slot("0.03", native_frames=True, disposition="ordinary-invalid")])
        before = harvest.inventory(self.night)
        result = self.run_harvest()
        self.assertEqual(result["valid_captures"], 1)
        self.assertEqual(result["retained_captures"], 1)
        self.assertEqual(result["registration_check"]["exit_code"], 0)
        self.assertEqual(result["next_window"]["verdict"], "COUNTS_ONLY")
        self.assertEqual(result["sessions"][0]["captures"][0]["clock"], "resolved")
        self.assertTrue(harvest.copy_matches(before, harvest.inventory(self.args.custody / "custody-root")))
        self.assertEqual(before, harvest.inventory(self.night))
        self.assertEqual(json.loads((self.args.custody / "harvest.json").read_bytes()), result)
        self.assertEqual(len([argv for argv in self.calls if "--uninstall" in argv]), 1)
        calls = len(self.calls)
        self.assertEqual(self.run_harvest(), result)
        self.assertEqual(len(self.calls), calls + 1)  # HEAD read only on retry

    def test_tampered_raw_refuses_without_publication_or_uninstall(self):
        self.fixture()
        raw = next(self.night.glob("runs/instrument_validation/*/raw/powermetrics.plist"))
        raw.write_bytes(raw.read_bytes() + b"tampered")
        self.assert_refuses()

    def test_missing_capture_refuses(self):
        self.fixture()
        shutil.rmtree(next(self.night.glob("runs/instrument_validation/*")))
        self.assert_refuses()

    def test_missing_battery_raw_refuses(self):
        self.fixture()
        next(self.night.glob("runs/instrument_validation/*/raw/battery_float.pre.ioreg")).unlink()
        self.assert_refuses()

    def test_no_bound_field_access_or_output_counterfactual(self):
        self.fixture([build.Slot("987654321.012345", native_frames=True)])
        reader = harvest.issuer._read_member_evidence

        class BlindEvidence(dict):
            def get(self, key, *args):
                if key == "b_fiducial_s":
                    raise AssertionError("bound was accessed")
                return super().get(key, *args)

            def __getitem__(self, key):
                if key == "b_fiducial_s":
                    raise AssertionError("bound was accessed")
                return super().__getitem__(key)

        def blind_reader(observation):
            evidence, manifest = reader(observation)
            return BlindEvidence(evidence), manifest

        with mock.patch.object(harvest.issuer, "_read_member_evidence", blind_reader):
            output = harvest.json_bytes(self.run_harvest()).decode()
        self.assertNotIn("b_fiducial", output.lower())
        self.assertNotIn("987654321", output)
        self.assertNotIn("exact_bound", output)
        self.assertEqual(json.loads(output)["valid_captures"], 1)

    def test_independent_probe_error_and_passed_crosscheck_is_recorded(self):
        self.fixture(manual_bad=True)
        result = self.run_harvest()
        self.assertEqual(result["sessions"][0]["manual_crosscheck"], "fail")
        self.assertEqual(result["retained_captures"], 0)
        self.assertEqual(result["sessions"][0]["captures"][0]["probe_error_false"], [False, True])
        self.assertEqual(result["sessions"][0]["captures"][0]["passed_true"], [True, False])

    def test_missing_committed_verdict_refuses_before_publication_or_uninstall(self):
        self.fixture(verdict_records=False)
        with mock.patch.object(harvest.cap_replay_harness, "replay_capture") as replay, self.assertRaisesRegex(
                harvest.battery_float.BatteryVerdictRefusal, "missing or uncommitted"):
            self.run_harvest()
        replay.assert_not_called()
        self.assertFalse(self.args.custody.exists())
        self.assertFalse(any("--uninstall" in argv for argv in self.calls))

    def test_uncommitted_verdict_refuses_before_replay_publication_or_uninstall(self):
        self.revision6_fixture(verdict_records=False)
        build.write_verdict_record(self.f, build.SESSION_ID)
        with mock.patch.object(harvest.cap_replay_harness, "replay_capture") as replay, self.assertRaisesRegex(
                harvest.battery_float.BatteryVerdictRefusal, "missing or uncommitted"):
            self.run_harvest()
        replay.assert_not_called()
        self.assertFalse(self.args.custody.exists())
        self.assertFalse(any("--uninstall" in argv for argv in self.calls))

    def test_open_window_refuses(self):
        self.fixture([build.Slot("0.02", native_frames=True), build.Slot("0.03", native_frames=True)], fill_slots=1)
        self.assert_refuses()

    def test_uninstall_failure_does_not_publish_partial_archive(self):
        self.fixture()
        self.uninstall_rc = 1
        with self.assertRaisesRegex(harvest.HarvestRefusal, "uninstall"):
            self.run_harvest()
        self.assertFalse(self.args.custody.exists())
        self.assertFalse(self.args.custody.with_name("archive.harvest-lock").exists())
        self.uninstall_rc = 0
        self.assertEqual(self.run_harvest()["valid_captures"], 1)

    def test_existing_corrupt_archive_never_overwritten(self):
        self.fixture()
        self.run_harvest()
        path = self.args.custody / "harvest.json"
        path.write_text("tampered")
        self.calls.clear()
        with self.assertRaisesRegex(harvest.HarvestRefusal, "overwrite"):
            self.run_harvest()
        self.assertEqual(path.read_text(), "tampered")
        self.assertFalse(any("--uninstall" in argv for argv in self.calls))

    def test_completion_boundary_and_ownership_refuse(self):
        self.fixture()
        for extra in ({"now": lambda: 9400}, {"census": lambda **_: Census(refusals=["owned"])}):
            with self.assertRaises(harvest.HarvestRefusal):
                harvest.harvest(self.args, runner=self.runner, now=extra.get("now", lambda: 10000),
                                census=extra.get("census", lambda **_: Census()))
        self.assertFalse(self.args.custody.exists())

    def test_registration_rule_uses_plan_pointer_and_counts(self):
        self.fixture()
        plan = harvest.NightPlan.from_mapping(self.plan)
        rows = [{"declared": 12, "valid": 6, "battery": "pass", "manual_crosscheck": "pass",
                 "median_of_capture_medians_ms": 132}]
        self.assertEqual(harvest.next_window(plan, self.args.preregistration, rows)["verdict"], "COUNTS_ONLY")
        self.plan["registration_path"] = str(self.args.preregistration)
        plan = harvest.NightPlan.from_mapping(self.plan)
        self.assertEqual(harvest.next_window(plan, self.args.preregistration, rows), {"verdict": "GO", "next": "W2"})
        rows[0]["valid"] = 5
        self.assertEqual(harvest.next_window(plan, self.args.preregistration, rows)["verdict"], "NO_GO")
        rows[0]["valid"] = 6
        self.assertEqual(harvest.next_window(plan, self.args.preregistration, rows * 2), {"verdict": "NO_GO", "next": "W3"})
        rows[0]["valid"] = 5
        self.assertEqual(harvest.next_window(plan, self.args.preregistration, rows * 2), {"verdict": "GO", "next": "W3"})

    def test_cli_error_does_not_leak_primary_content(self):
        self.fixture()
        output, errors = io.StringIO(), io.StringIO()
        argv = ["--plan", str(self.args.plan), "--custody", str(self.args.custody),
                "--preregistration", str(self.args.preregistration),
                "--preregistration-sha256", self.args.preregistration_sha256]
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            rc = harvest.main(argv, runner=self.runner, census=lambda **_: Census(), now=lambda: 10000)
        self.assertEqual(rc, 0)
        self.assertEqual(output.getvalue(), "valid_captures=1 next_window=COUNTS_ONLY\n")
        self.assertEqual(errors.getvalue(), "")
        next(self.night.glob("runs/instrument_validation/*/raw/powermetrics.plist")).write_bytes(b"B=987654321")
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            rc = harvest.main(argv, runner=self.runner, census=lambda **_: Census(), now=lambda: 10000)
        self.assertEqual(rc, 3)
        self.assertNotIn("987654321", output.getvalue() + errors.getvalue())

    def test_publication_failure_keeps_source_and_no_partial_destination(self):
        self.fixture()
        before = harvest.inventory(self.night)
        with mock.patch.object(harvest.os, "rename", side_effect=OSError("publication failed")):
            with self.assertRaises(OSError):
                self.run_harvest()
        self.assertEqual(harvest.inventory(self.night), before)
        self.assertFalse(self.args.custody.exists())
        self.assertEqual(self.run_harvest()["valid_captures"], 1)

    def test_source_mutation_during_courier_refuses_before_uninstall(self):
        self.fixture()
        original_copy = harvest.shutil.copytree

        def changing_copy(source, destination, *a, **kw):
            result = original_copy(source, destination, *a, **kw)
            if Path(source) == self.night:
                next(self.night.glob("runs/instrument_validation/*/raw/powermetrics.plist")).write_bytes(b"changed")
            return result

        with mock.patch.object(harvest.shutil, "copytree", changing_copy):
            self.assert_refuses()

    def test_aborted_window_counts_unused_slots_without_inventing_capture(self):
        self.fixture([build.Slot("0.02", native_frames=True), build.Slot("0.03", native_frames=True)],
                     fill_slots=1, abort_reason="window_exhausted")
        row = self.run_harvest()["sessions"][0]
        self.assertEqual((row["declared"], row["filled"], row["valid"]), (2, 1, 1))


if __name__ == "__main__":
    unittest.main()
