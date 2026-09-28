"""Counterfactual checks for the S1 evidence-forward fixture helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from joulewise import battery_float
from joulewise.bundle import RunBundleWriter
from joulewise.bundle_read import BundleReader, WindowBatteryRefusal, authenticate_window_members
from joulewise.cli import validate_bundle
from joulewise.clock import FakeClock
from tests.bfgs_fixtures import (
    FIXTURES, injected_battery_runner, injected_battery_runner_at, rebind_config,
    produce_strict_bundle, write_capture_evidence, write_charging_pair,
    write_passing_pair,
)
from tests.test_bundle_read import load_config


class BfgsFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def bundle(self, run_id: str) -> Path:
        writer = RunBundleWriter.create(self.root, load_config(run_id=run_id), FakeClock())
        writer.write_metadata({"device": {"telemetry": "mock"}})
        return writer.path

    def test_rebound_passing_pair_passes_window_gate(self) -> None:
        bundle = self.bundle("fixture-pass")
        rebind_config(bundle)
        self.assertEqual(json.loads((bundle / "metadata.json").read_text())["device"]["telemetry"],
                         "powermetrics")
        write_passing_pair(bundle)
        verdict = authenticate_window_members((("member", bundle),))["member"]
        self.assertEqual(verdict.status, "pass")
        reader = BundleReader(bundle)
        reader.metadata()
        self.assertEqual(reader.battery_float_status, "pass")

    def test_raw_byte_flip_raises_custody_failure(self) -> None:
        bundle = self.bundle("fixture-corrupt")
        rebind_config(bundle)
        write_passing_pair(bundle)
        raw = bundle / "raw/battery_float.pre.ioreg"
        body = raw.read_bytes()
        raw.write_bytes(bytes([body[0] ^ 1]) + body[1:])
        with self.assertRaises(battery_float.CustodyFailure):
            authenticate_window_members((("member", bundle),))

    def test_charging_pair_refuses_as_confounded(self) -> None:
        bundle = self.bundle("fixture-charging")
        rebind_config(bundle)
        write_charging_pair(bundle)
        with self.assertRaises(WindowBatteryRefusal) as caught:
            authenticate_window_members((("charging", bundle),))
        self.assertEqual(caught.exception.members[0]["status"], "battery_float_confounded")

    def test_config_changed_after_binding_refuses_without_writes(self) -> None:
        bundle = self.bundle("fixture-stale")
        rebind_config(bundle)
        metadata_before = (bundle / "metadata.json").read_bytes()
        (bundle / "config.json").write_bytes((bundle / "config.json").read_bytes() + b" ")
        for writer in (write_passing_pair, write_charging_pair):
            with self.subTest(writer=writer.__name__):
                with self.assertRaisesRegex(ValueError, "^config not bound$"):
                    writer(bundle)
                self.assertEqual((bundle / "metadata.json").read_bytes(), metadata_before)
                self.assertEqual(list((bundle / "raw").glob("battery_float.*")), [])

    def test_h5_mock_bound_pair_writers_refuse_without_writes(self) -> None:
        bundle = self.bundle("fixture-mock")
        metadata_before = (bundle / "metadata.json").read_bytes()
        for writer in (write_passing_pair, write_charging_pair):
            with self.subTest(writer=writer.__name__):
                with self.assertRaisesRegex(ValueError, "^battery pair on mock config$"):
                    writer(bundle)
                self.assertEqual((bundle / "metadata.json").read_bytes(), metadata_before)
                self.assertEqual(list((bundle / "raw").glob("battery_float.*")), [])

    def test_h6_rebind_then_pair_passes_and_has_new_digest(self) -> None:
        bundle = self.bundle("fixture-h6")
        (bundle / "summary_metrics.json").write_text(json.dumps({
            "idle_baseline": {"telemetry_backend": "mock"},
        }))
        old_digest = json.loads((bundle / "metadata.json").read_text())["config_sha256"]
        rebind_config(bundle)
        metadata = json.loads((bundle / "metadata.json").read_text())
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        self.assertEqual(metadata["device"]["telemetry"], "powermetrics")
        self.assertEqual(summary["idle_baseline"]["telemetry_backend"], "powermetrics")
        self.assertNotEqual(metadata["config_sha256"], old_digest)
        self.assertEqual(metadata["config_sha256"],
                         hashlib.sha256((bundle / "config.json").read_bytes()).hexdigest())
        write_passing_pair(bundle)
        self.assertEqual(authenticate_window_members((("member", bundle),))["member"].status,
                         "pass")

    def test_capture_pair_and_digest_authenticate(self) -> None:
        root = self.root / "capture"
        digest = write_capture_evidence(
            root, validation_id="validation-1", session_id="session-1", slot="slot-1",
            evidence={"protocol_id": "fixture-protocol"},
        )
        self.assertEqual(digest, hashlib.sha256((root / "instrument_evidence.json").read_bytes()).hexdigest())
        self.assertEqual(json.loads((root / "instrument_evidence.json").read_text())["protocol_id"],
                         "fixture-protocol")
        self.assertEqual(battery_float.authenticate_capture(root, expected={
            "attempt_id": "validation-1", "session_id": "session-1", "slot": "slot-1",
        }).status, "pass")

    def test_runner_is_deterministic_and_rejects_other_argv(self) -> None:
        runner = injected_battery_runner()
        self.assertEqual(runner(battery_float.IOREG_BATTERY_ARGV).stdout,
                         runner(battery_float.IOREG_BATTERY_ARGV).stdout)
        with self.assertRaises(AssertionError):
            runner(("/usr/bin/true",))

    def test_h8_produced_bundle_passes_gate_and_strict_validation(self) -> None:
        bundle = produce_strict_bundle(self.root, "strict-h8")
        self.assertEqual(authenticate_window_members((("member", bundle),))["member"].status,
                         "pass")
        self.assertEqual(validate_bundle(bundle, strict=True), [])
        metadata = json.loads((bundle / "metadata.json").read_text())
        self.assertEqual(set(metadata["battery_float"]), {"pre", "post"})

    def test_h9_produced_bundle_with_charging_reading_is_confounded(self) -> None:
        bundle = produce_strict_bundle(self.root, "strict-h9")
        rebind_config(bundle)
        write_charging_pair(bundle)
        with self.assertRaises(WindowBatteryRefusal) as caught:
            authenticate_window_members((("member", bundle),))
        self.assertEqual(caught.exception.members[0]["label"], "member")
        self.assertEqual(caught.exception.members[0]["status"],
                         "battery_float_confounded")

    def test_h10_missing_raw_powermetrics_refuses_strict_validation(self) -> None:
        bundle = produce_strict_bundle(self.root, "strict-h10")
        (bundle / "raw" / "powermetrics.plist").unlink()
        self.assertTrue(validate_bundle(bundle, strict=True))

    def test_h11_mock_mutation_refused_before_bundle_creation(self) -> None:
        def set_mock(config):
            config["hardware_target"]["telemetry_backend"] = "mock"

        with self.assertRaisesRegex(ValueError, "^strict bundle on mock backend$"):
            produce_strict_bundle(self.root, "strict-h11", mutate_config=set_mock)
        self.assertFalse((self.root / "strict-h11").exists())

    def test_h12_stale_reading_fails_the_controller_run(self) -> None:
        with self.assertRaisesRegex(AssertionError, "strict bundle run failed"):
            produce_strict_bundle(self.root, "strict-h12",
                                  clock_start=1790373526.0 + 3600)

    def test_h13_runner_at_rewrites_only_the_update_time_line(self) -> None:
        runner = injected_battery_runner_at(lambda: 1790568378.9)
        stamped = runner(battery_float.IOREG_BATTERY_ARGV).stdout
        committed = (FIXTURES / "float.ioreg").read_bytes()
        changed = [
            (old, new)
            for old, new in zip(committed.splitlines(), stamped.splitlines())
            if old != new
        ]
        self.assertEqual(len(committed.splitlines()), len(stamped.splitlines()))
        self.assertEqual(len(changed), 1)
        self.assertIn(b'"UpdateTime" = ', changed[0][0])
        self.assertTrue(changed[0][1].endswith(b'"UpdateTime" = 1790568378'))

    def test_h14_runner_at_refuses_any_other_command_line(self) -> None:
        runner = injected_battery_runner_at(lambda: 1790568378.9)
        with self.assertRaises(AssertionError):
            runner(("/usr/bin/true",))


if __name__ == "__main__":
    unittest.main()
