"""Battery authentication of every named window member."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from joulewise import battery_float
from joulewise.battery_float import CustodyFailure, CustodyUnreadable
from joulewise.bundle import RunBundleWriter
from joulewise.bundle_read import WindowBatteryRefusal, authenticate_window_members
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
            with self.assertRaisesRegex(CustodyUnreadable, "second"):
                authenticate_window_members((("first", first), ("second", second)))


if __name__ == "__main__":
    unittest.main()
