"""Battery authentication of every named window member."""

from __future__ import annotations

import json
import hashlib
import ast
from pathlib import Path
import subprocess
import tempfile
import traceback
import unittest

from joulewise import battery_float
from joulewise.battery_float import CustodyFailure, CustodyUnreadable
from joulewise.bundle import RunBundleWriter
from joulewise.bundle_read import WindowBatteryRefusal, authenticate_window_members
from joulewise.detection_floor import complete_bundle_sha256
from joulewise.clock import FakeClock
from tests.test_bundle_read import load_config


class WindowMembersTests(unittest.TestCase):
    def pair_bundle(self, root: Path, run_id: str, *, charging: bool = False,
                    failed_probe: bool = False) -> Path:
        writer = RunBundleWriter.create(root, load_config(run_id=run_id), FakeClock())
        pair = {}
        for phase, stamps in (("pre", (10, 20)), ("post", (90, 100))):
            relative = f"raw/battery_float.{phase}.ioreg"
            fixture = ("charging-synthetic-from-real.ioreg" if charging and phase == "pre"
                       else "float.ioreg")
            raw = (Path(__file__).parent / "fixtures/battery_float" / fixture).read_bytes()
            if failed_probe and phase == "post":
                raw = b""
            (writer.path / relative).write_bytes(raw)
            ticks = iter(stamps)
            pair[phase], _ = battery_float.observe(
                phase=f"bundle_{phase}", raw_path=relative, session_id=run_id,
                wall_time_s=1790373526, monotonic_ns=lambda ticks=ticks: next(ticks),
                runner=lambda argv, raw=raw: subprocess.CompletedProcess(
                    argv, 1 if failed_probe and phase == "post" else 0, raw, b""
                ),
            )
        writer.write_metadata({"battery_float": pair})
        rows = (
            ("stage_started", "idle_baseline", 30),
            ("stage_completed", "idle_drift_sentinel", 80),
        )
        (writer.path / "events.jsonl").write_text("".join(json.dumps({
            "timestamp_s": float(stamp), "event_type": event_type,
            "phase": phase, "message": "", "metadata": {"monotonic_ns": stamp},
        }) + "\n" for event_type, phase, stamp in rows))
        return writer.path

    def test_passing_pair_returns_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self.pair_bundle(Path(tmp), "passing")
            verdicts = authenticate_window_members((("passing", bundle),))
            self.assertEqual(verdicts["passing"].status, "pass")
            self.assertEqual(len(verdicts["passing"].bundle_sha256), 64)

    def test_confounded_and_probe_missing_both_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            members = (
                ("charging", self.pair_bundle(root, "charging", charging=True)),
                ("probe", self.pair_bundle(root, "probe", failed_probe=True)),
            )
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members(members)
            self.assertEqual(
                [(row["label"], row["status"]) for row in caught.exception.members],
                [("charging", "battery_float_confounded"),
                 ("probe", "battery_float_evidence_missing")],
            )

    def test_missing_recorded_raw_is_custody_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self.pair_bundle(Path(tmp), "lost-raw")
            (bundle / "raw/battery_float.post.ioreg").unlink()
            with self.assertRaises(CustodyFailure):
                authenticate_window_members((("lost-raw", bundle),))

    def test_two_prospective_members_are_both_named(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            members = []
            for label in ("a", "b"):
                bundle = self.pair_bundle(root, label)
                config_path = bundle / "config.json"
                config = json.loads(config_path.read_text())
                config["hardware_target"]["telemetry_backend"] = "powermetrics"
                config_path.write_text(json.dumps(config))
                metadata_path = bundle / "metadata.json"
                metadata = json.loads(metadata_path.read_text())
                metadata["config_sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
                del metadata["battery_float"]
                metadata_path.write_text(json.dumps(metadata))
                members.append((label, bundle))
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members(members)
            self.assertEqual([(row["label"], row["status"], row["bundle_sha256"])
                              for row in caught.exception.members],
                             [(label, "battery_float_evidence_missing", complete_bundle_sha256(path))
                              for label, path in members])

    def test_digest_bound_invalid_config_is_window_status_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = RunBundleWriter.create(
                Path(tmp), load_config(run_id="invalid-bound-window"), FakeClock()
            )
            writer.write_metadata({})
            config_path = writer.path / "config.json"
            config_path.write_text("[]")
            metadata_path = writer.path / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["config_sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
            metadata_path.write_text(json.dumps(metadata))
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members((("invalid-bound-window", writer.path),))
            self.assertEqual(caught.exception.members[0]["label"], "invalid-bound-window")
            self.assertEqual(caught.exception.members[0]["status"], "battery_float_evidence_missing")
            self.assertRegex(
                caught.exception.members[0]["reasons"][0],
                r"^prospective bundle \(config\.json does not re-validate",
            )

    def test_confounded_then_prospective_names_both(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            charging = self.pair_bundle(root, "charging", charging=True)
            prospective = self.pair_bundle(root, "prospective")
            config_path = prospective / "config.json"
            config = json.loads(config_path.read_text())
            config["hardware_target"]["telemetry_backend"] = "powermetrics"
            config_path.write_text(json.dumps(config))
            metadata_path = prospective / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["config_sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
            del metadata["battery_float"]
            metadata_path.write_text(json.dumps(metadata))
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members((("charging", charging), ("prospective", prospective)))
            self.assertEqual([(row["label"], row["status"]) for row in caught.exception.members],
                             [("charging", "battery_float_confounded"),
                              ("prospective", "battery_float_evidence_missing")])

    def test_custody_second_member_has_label_note_and_original_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self.pair_bundle(root, "good")
            second = self.pair_bundle(root, "bad")
            (second / "raw/battery_float.post.ioreg").unlink()
            with self.assertRaises(CustodyFailure) as direct:
                battery_float.authenticate_bundle(second)
            with self.assertRaises(CustodyFailure) as caught:
                authenticate_window_members((("good", first), ("member-7", second)))
            exc = caught.exception
            self.assertIs(type(exc), CustodyFailure)
            self.assertEqual(exc.window_member, "member-7")
            self.assertIn("window member: member-7", exc.__notes__)
            self.assertIn("member-7", "".join(traceback.format_exception(exc)))
            self.assertEqual(exc.failures, direct.exception.failures)

    def test_historical_member_returns_digest_bound_verdict(self) -> None:
        bundle = Path(__file__).parent / "fixtures/d078_r01"
        verdicts = authenticate_window_members((("historical", bundle),))
        self.assertEqual(verdicts["historical"].status, "unobserved_historical")
        self.assertEqual(len(verdicts["historical"].bundle_sha256), 64)

    def test_all_nonpass_members_are_named(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            members = []
            for label in ("mock-a", "mock-b"):
                writer = RunBundleWriter.create(root, load_config(run_id=label), FakeClock())
                writer.write_metadata({"battery_float": {
                    "pre": None, "post": None, "not_applicable": "mock",
                }})
                members.append((label, writer.path))
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members(members)
            self.assertEqual([row["label"] for row in caught.exception.members],
                             ["mock-a", "mock-b"])
            self.assertTrue(all(row["status"] == "not_applicable" and
                                len(row["bundle_sha256"]) == 64
                                for row in caught.exception.members))

    def test_not_reached_has_no_obligation_without_baseline_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = RunBundleWriter.create(Path(tmp), load_config(run_id="early"), FakeClock())
            writer.write_metadata({"battery_float": {
                "pre": None, "post": None, "not_reached": "prepare",
            }})
            self.assertEqual(authenticate_window_members((("early", writer.path),)), {})

    def test_not_reached_with_baseline_start_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = RunBundleWriter.create(Path(tmp), load_config(run_id="late"), FakeClock())
            writer.write_metadata({"battery_float": {
                "pre": None, "post": None, "not_reached": "warmup",
            }})
            (writer.path / "events.jsonl").write_text(json.dumps({
                "timestamp_s": 1.0, "event_type": "stage_started",
                "phase": "idle_baseline", "message": "", "metadata": {"monotonic_ns": 1},
            }) + "\n")
            with self.assertRaises(WindowBatteryRefusal) as caught:
                authenticate_window_members((("late", writer.path),))
            self.assertEqual(caught.exception.members[0]["label"], "late")
            self.assertEqual(caught.exception.members[0]["status"],
                             "battery_float_evidence_missing")

    def test_unreadable_second_metadata_is_custody(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first"
            second = Path(tmp) / "second"
            writer = RunBundleWriter.create(Path(tmp), load_config(run_id="first"), FakeClock())
            writer.write_metadata({"battery_float": {
                "pre": None, "post": None, "not_applicable": "mock",
            }})
            second.mkdir()
            (second / "metadata.json").write_text("{")
            with self.assertRaisesRegex(CustodyUnreadable, "second") as caught:
                authenticate_window_members((("first", first), ("second", second)))
            self.assertEqual(caught.exception.window_member, "second")

    def test_aggregate_authenticates_failed_member_before_numbers(self) -> None:
        from joulewise.aggregate import aggregate_experiment
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.pair_bundle(root, "passing")
            failed = self.pair_bundle(root, "failed", charging=True)
            (failed / "summary_metrics.json").write_text(json.dumps({"status": "failed"}))
            with self.assertRaises(WindowBatteryRefusal) as caught:
                aggregate_experiment(root, {"members": ["passing", "failed"]})
            self.assertEqual([(row["label"], row["status"])
                              for row in caught.exception.members],
                             [("failed", "battery_float_confounded")])

    def test_aggregate_exposes_historical_battery_state(self) -> None:
        from joulewise.aggregate import aggregate_experiment
        fixtures = Path(__file__).parent / "fixtures"
        result = aggregate_experiment(fixtures, {"members": ["d078_r01"]})
        self.assertEqual(result["battery_float_members"],
                         {"d078_r01": "unobserved_historical"})

    def test_campaign_helper_includes_superseded_ordinary_and_axi_attempts(self) -> None:
        from scripts.run_campaign import (
            OrdinaryOccurrenceResolution, WholeWindowMemberSource,
            WholeWindowMembershipResolution, _authenticate_whole_window_members,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selected = self.pair_bundle(root, "selected")
            superseded = self.pair_bundle(root, "superseded", charging=True)
            membership = WholeWindowMembershipResolution(
                sources=(WholeWindowMemberSource(path=selected),),
                source_manifests=(), conditions=(), occurrence_supersessions=(),
                occurrence_resolutions=(OrdinaryOccurrenceResolution(
                    bundle_id="selected", status="selected", present_paths=(selected, superseded)
                ),),
            )
            with self.assertRaises(WindowBatteryRefusal) as caught:
                _authenticate_whole_window_members(membership, root)
            self.assertIn(str(superseded), [row["label"] for row in caught.exception.members])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "axi_attempt_bundles" / "manifest" / "entry"
            (base / "a1").mkdir(parents=True)
            (base / "a2").mkdir(parents=True)
            old = self.pair_bundle(base / "a1", "old", charging=True)
            selected = self.pair_bundle(base / "a2", "selected")
            membership = WholeWindowMembershipResolution(
                sources=(WholeWindowMemberSource(path=selected),),
                source_manifests=(), conditions=(), occurrence_supersessions=(),
            )
            with self.assertRaises(WindowBatteryRefusal) as caught:
                _authenticate_whole_window_members(membership, root)
            self.assertIn(str(old), [row["label"] for row in caught.exception.members])

    def test_eight_consumer_modules_call_reader_gate_without_battery_import(self) -> None:
        root = Path(__file__).resolve().parents[1]
        paths = (
            "joulewise/whole_window.py", "joulewise/analysis_engine/inputs.py",
            "joulewise/floor_extraction.py", "joulewise/aggregate.py",
            "joulewise/window_duration_margins.py", "scripts/mint_floor_artifact.py",
            "scripts/extract_detection_floors.py", "scripts/run_campaign.py",
        )
        for relative in paths:
            with self.subTest(path=relative):
                tree = ast.parse((root / relative).read_text())
                calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                         and ((isinstance(node.func, ast.Name)
                               and node.func.id == "authenticate_window_members")
                              or (isinstance(node.func, ast.Attribute)
                                  and node.func.attr == "authenticate_window_members"))]
                self.assertTrue(calls, relative)
                self.assertFalse(any(
                    (isinstance(node, ast.ImportFrom) and
                     "battery_float" in (node.module or ""))
                    or (isinstance(node, ast.Import) and any(
                        "battery_float" in alias.name for alias in node.names))
                    for node in ast.walk(tree)
                ), relative)


if __name__ == "__main__":
    unittest.main()
