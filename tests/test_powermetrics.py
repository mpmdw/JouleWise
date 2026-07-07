from __future__ import annotations

import json
import plistlib
import statistics
import subprocess
import tempfile
import unittest
from datetime import timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

from joulewise.adapters import resolve_telemetry
from joulewise.adapters.powermetrics import (
    RAIL_MANIFEST,
    RAW_SAMPLES_NAME,
    PowermetricsTelemetryAdapter,
    parse_powermetrics_records,
    samples_from_records,
    sudoers_line,
)
from joulewise.clock import FakeClock
from joulewise.controller import run_benchmark
from joulewise.interfaces import RunContext, TelemetryAdapter
from joulewise.schemas import BenchmarkConfig, FailureReason, RunStatus, TelemetryBackend

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "powermetrics_sample.plist"
CORRUPT_PLIST = b"<?xml version='1.0'?><plist><dict><key>timestamp</key>"


def make_config(**overrides: Any) -> BenchmarkConfig:
    data: dict[str, Any] = {
        "schema_version": "0.1",
        "model": {"name": "mock-model"},
        "quantization": {"name": "none"},
        "hardware_target": {
            "id": "macbook_m3_max",
            "transport": "local",
            "runtime_backend": "mock",
            "telemetry_backend": "powermetrics",
        },
        "workload_profile": {
            "name": "mock_smoke",
            "prompt_tokens": 32,
            "output_tokens": 8,
        },
        "sampling": {"power_hz": 1.0, "idle_seconds": 5.0},
    }
    for key, value in overrides.items():
        if isinstance(value, dict):
            data[key] = {**data[key], **value}
        else:
            data[key] = value
    return BenchmarkConfig.from_mapping(data)


def fixture_documents() -> list[dict[str, Any]]:
    data = FIXTURE.read_bytes()
    return [plistlib.loads(part) for part in data.split(b"\0") if part.strip()]


def utc_epoch(value) -> float:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).timestamp()


def completed(command: list[str], returncode: int = 0, stderr: bytes = b""):
    return subprocess.CompletedProcess(command, returncode, stdout=b"", stderr=stderr)


class PowermetricsParserTests(unittest.TestCase):
    def test_fixture_framing_and_plist_documents(self) -> None:
        data = FIXTURE.read_bytes()
        parts = [part for part in data.split(b"\0") if part.strip()]
        self.assertEqual(data.count(b"\0"), 4)
        self.assertEqual(len(parts), 5)
        for part in parts:
            self.assertIsInstance(plistlib.loads(part), dict)

    def test_parser_emits_manifest_rails_in_watts(self) -> None:
        documents = fixture_documents()
        records = parse_powermetrics_records(FIXTURE.read_bytes())
        self.assertEqual(len(records), len(documents))

        doc2 = documents[2]["processor"]
        expected_doc2_w = sum(float(doc2[rail]) for rail in RAIL_MANIFEST) / 1000.0
        self.assertAlmostEqual(expected_doc2_w, 0.537877, places=12)
        self.assertAlmostEqual(records[2].combined_power_w, expected_doc2_w, places=12)
        self.assertEqual(set(records[2].rail_power_w), set(RAIL_MANIFEST))
        self.assertAlmostEqual(records[2].rail_power_w["cpu_power"], 0.484971, places=12)
        self.assertAlmostEqual(records[2].rail_power_w["gpu_power"], 0.052906, places=12)
        self.assertAlmostEqual(records[2].rail_power_w["ane_power"], 0.0, places=12)
        self.assertEqual(
            records[2].rail_energy_mj,
            {
                "cpu_energy": int(doc2["cpu_energy"]),
                "gpu_energy": int(doc2["gpu_energy"]),
                "ane_energy": int(doc2["ane_energy"]),
            },
        )

    def test_timestamps_are_utc_anchor_plus_cumulative_elapsed_ns(self) -> None:
        documents = fixture_documents()
        records = parse_powermetrics_records(FIXTURE.read_bytes())
        first = utc_epoch(documents[0]["timestamp"])
        expected = []
        cumulative_s = 0.0
        for document in documents:
            cumulative_s += int(document["elapsed_ns"]) / 1_000_000_000.0
            expected.append(first + cumulative_s)
            self.assertIsInstance(document["elapsed_ns"], int)

        records = parse_powermetrics_records(FIXTURE.read_bytes(), timestamp_anchor_s=first)
        actual = [record.timestamp_s for record in records]
        self.assertEqual(actual, expected)
        self.assertEqual(actual, sorted(actual))
        self.assertEqual(len(set(actual)), len(actual))
        self.assertAlmostEqual(first, 1_783_394_101.0, places=6)
        self.assertAlmostEqual(actual[2], 1_783_394_104.0524974, places=6)

    def test_samples_align_all_rails_on_each_timestamp_for_d027(self) -> None:
        records = parse_powermetrics_records(FIXTURE.read_bytes())
        samples = samples_from_records(records)
        self.assertEqual(len(samples), len(records) * len(RAIL_MANIFEST))
        for record in records:
            rows = [sample for sample in samples if sample.timestamp_s == record.timestamp_s]
            self.assertEqual([sample.rail for sample in rows], RAIL_MANIFEST)
            self.assertEqual({sample.timestamp_s for sample in rows}, {record.timestamp_s})
            self.assertAlmostEqual(
                sum(sample.power_w for sample in rows),
                record.combined_power_w,
                places=12,
            )

    def test_thermal_pressure_without_temperature(self) -> None:
        records = parse_powermetrics_records(FIXTURE.read_bytes())
        self.assertEqual({record.thermal_pressure for record in records}, {"Nominal"})
        adapter = PowermetricsTelemetryAdapter(FakeClock(start=123.0))
        adapter._remember_records(records)
        state = adapter.thermal_state(make_config())
        self.assertEqual(state.timestamp_s, 123.0)
        self.assertIsNone(state.temperature_c)
        self.assertEqual(state.thermal_pressure, "Nominal")


class PowermetricsAdapterTests(unittest.TestCase):
    def test_device_metadata_declares_manifest_and_timestamp_derivation(self) -> None:
        adapter = PowermetricsTelemetryAdapter(FakeClock())
        metadata = adapter.device_metadata(make_config())
        self.assertEqual(metadata["telemetry"], "powermetrics")
        self.assertEqual(metadata["rail_manifest"], RAIL_MANIFEST)
        self.assertIn("elapsed_ns", metadata["timestamp_derivation"])

    def test_measure_idle_computes_mean_and_stddev_from_fixture(self) -> None:
        fixture = FIXTURE.read_bytes()
        documents = fixture_documents()
        expected_totals = [
            sum(float(document["processor"][rail]) for rail in RAIL_MANIFEST) / 1000.0
            for document in documents
        ]

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        adapter = PowermetricsTelemetryAdapter(FakeClock())
        with patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run):
            baseline = adapter.measure_idle(make_config())

        self.assertAlmostEqual(baseline.power_w_mean, statistics.mean(expected_totals), places=12)
        self.assertAlmostEqual(
            baseline.power_w_stddev,
            statistics.stdev(expected_totals),
            places=12,
        )
        self.assertEqual(baseline.sample_count, len(documents))
        self.assertEqual(baseline.telemetry_backend, TelemetryBackend.POWERMETRICS)
        self.assertAlmostEqual(baseline.power_w_mean, 0.466464226, places=12)
        self.assertAlmostEqual(baseline.power_w_stddev, 0.5963032492730296, places=12)
        self.assertAlmostEqual(baseline.duration_s, 5.091935956, places=12)

    def test_start_sampling_permission_denied_names_exact_sudoers_line(self) -> None:
        def fake_run(command, **kwargs):
            return completed(command, returncode=1, stderr=b"sudo: a password is required\n")

        adapter = PowermetricsTelemetryAdapter(FakeClock())
        with patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run):
            result = adapter.start_sampling(make_config())

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.PERMISSION_DENIED)
        self.assertIn(sudoers_line(), result.message)
        self.assertIn("sudo", result.message)

    def test_run_fails_at_idle_without_fabricated_baseline_or_warmup(self) -> None:
        def fake_run(command, **kwargs):
            return completed(command, returncode=1, stderr=b"sudo: a password is required\n")

        with tempfile.TemporaryDirectory() as tmp:
            with patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run):
                bundle_path, summary = run_benchmark(make_config(), Path(tmp), FakeClock())

            self.assertEqual(summary.status, RunStatus.FAILED)
            self.assertEqual(summary.failure_reason, FailureReason.PERMISSION_DENIED)
            self.assertIsNone(summary.idle_baseline)
            metadata = json.loads((bundle_path / "metadata.json").read_text())
            self.assertNotIn("idle_baseline", metadata)
            events = [
                json.loads(line)
                for line in (bundle_path / "events.jsonl").read_text().splitlines()
                if line.strip()
            ]
            self.assertNotIn(
                ("stage_started", "warmup"),
                [(event["event_type"], event["phase"]) for event in events],
            )

    def test_start_stop_preserves_raw_file_and_returns_aligned_samples(self) -> None:
        fixture = FIXTURE.read_bytes()
        config = make_config(sampling={"power_hz": 2.0, "idle_seconds": 5.0})
        clock = FakeClock(start=100.0)
        adapter = PowermetricsTelemetryAdapter(clock)

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        class FakePopen:
            command: list[str] | None = None

            def __init__(self, command, **kwargs):
                type(self).command = command
                Path(command[command.index("-o") + 1]).write_bytes(fixture)
                self.returncode = None
                self.terminated = False

            def poll(self):
                return self.returncode

            def terminate(self):
                self.terminated = True
                self.returncode = 0

            def kill(self):
                self.returncode = -9

            def communicate(self, timeout=None):
                self.returncode = 0
                return b"", b""

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "run"
            root.mkdir()
            context = RunContext(
                config=config,
                clock=clock,
                run_id="run-1",
                bundle_path=root,
                raw_dir=root / "raw",
                logs_dir=root / "logs",
                outputs_dir=root / "outputs",
            )
            with (
                patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
                patch("joulewise.adapters.powermetrics.subprocess.Popen", FakePopen),
            ):
                start = adapter.start_sampling(config, context)
                self.assertTrue(start.ok)
                samples = adapter.stop_sampling(config, context)

            self.assertIn("-i", FakePopen.command)
            self.assertEqual(FakePopen.command[FakePopen.command.index("-i") + 1], "500")
            self.assertEqual((root / "raw" / RAW_SAMPLES_NAME).read_bytes(), fixture)
            self.assertEqual(len(samples), 15)
            for offset in range(0, len(samples), 3):
                rows = samples[offset : offset + 3]
                self.assertEqual([sample.rail for sample in rows], RAIL_MANIFEST)
                self.assertEqual(len({sample.timestamp_s for sample in rows}), 1)

    def test_corrupt_stop_preserves_raw_before_parse_failure(self) -> None:
        config = make_config()
        adapter = PowermetricsTelemetryAdapter(FakeClock(start=10.0))

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(FIXTURE.read_bytes())
            return completed(command)

        class CorruptPopen:
            def __init__(self, command, **kwargs):
                Path(command[command.index("-o") + 1]).write_bytes(CORRUPT_PLIST)
                self.returncode = None

            def poll(self):
                return self.returncode

            def terminate(self):
                self.returncode = 0

            def communicate(self, timeout=None):
                self.returncode = 0
                return b"", b""

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "run"
            root.mkdir()
            context = RunContext(
                config=config,
                clock=FakeClock(start=10.0),
                run_id="run-1",
                bundle_path=root,
                raw_dir=root / "raw",
                logs_dir=root / "logs",
                outputs_dir=root / "outputs",
            )
            with (
                patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
                patch("joulewise.adapters.powermetrics.subprocess.Popen", CorruptPopen),
            ):
                self.assertTrue(adapter.start_sampling(config, context).ok)
                with self.assertRaises(ValueError):
                    adapter.stop_sampling(config, context)

            self.assertEqual((root / "raw" / RAW_SAMPLES_NAME).read_bytes(), CORRUPT_PLIST)

    def test_probe_succeeds_with_corrupt_output_does_not_escape(self) -> None:
        class FakePopen:
            def __init__(self, command, **kwargs):
                Path(command[command.index("-o") + 1]).write_bytes(FIXTURE.read_bytes())
                self.returncode = 0

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(CORRUPT_PLIST)
            return completed(command)

        adapter = PowermetricsTelemetryAdapter(FakeClock())
        with (
            patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
            patch("joulewise.adapters.powermetrics.subprocess.Popen", FakePopen),
        ):
            self.assertTrue(adapter.start_sampling(make_config()).ok)

    def test_probe_timeout_is_structured_unknown_error(self) -> None:
        def fake_run(command, **kwargs):
            raise subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])

        adapter = PowermetricsTelemetryAdapter(FakeClock())
        with patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run):
            result = adapter.start_sampling(make_config())
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.UNKNOWN_ERROR)

    def test_probe_missing_binary_is_telemetry_unavailable(self) -> None:
        def fake_run(command, **kwargs):
            raise FileNotFoundError("sudo")

        adapter = PowermetricsTelemetryAdapter(FakeClock())
        with patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run):
            result = adapter.start_sampling(make_config())
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.TELEMETRY_UNAVAILABLE)

    def test_stop_sampling_without_start_returns_empty(self) -> None:
        adapter = PowermetricsTelemetryAdapter(FakeClock())
        self.assertEqual(adapter.stop_sampling(make_config()), [])

    def test_stop_sampling_without_context_skips_raw_write(self) -> None:
        config = make_config()
        adapter = PowermetricsTelemetryAdapter(FakeClock())

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(FIXTURE.read_bytes())
            return completed(command)

        class FakePopen:
            def __init__(self, command, **kwargs):
                Path(command[command.index("-o") + 1]).write_bytes(FIXTURE.read_bytes())
                self.returncode = None

            def poll(self):
                return self.returncode

            def terminate(self):
                self.returncode = 0

            def communicate(self, timeout=None):
                self.returncode = 0
                return b"", b""

        with (
            patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
            patch("joulewise.adapters.powermetrics.subprocess.Popen", FakePopen),
        ):
            self.assertTrue(adapter.start_sampling(config).ok)
            samples = adapter.stop_sampling(config, context=None)
        self.assertEqual(len(samples), 15)

    def test_idle_count_and_timeout_use_rounded_interval(self) -> None:
        fixture = FIXTURE.read_bytes()
        capture_calls = []

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            capture_calls.append((command, kwargs["timeout"]))
            return completed(command)

        config = make_config(sampling={"power_hz": 600.0, "idle_seconds": 60.0})
        adapter = PowermetricsTelemetryAdapter(FakeClock())
        with patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run):
            adapter.measure_idle(config)

        command, timeout = capture_calls[-1]
        count_flag_index = [index for index, value in enumerate(command) if value == "-n"][1]
        self.assertEqual(command[command.index("-i") + 1], "2")
        self.assertEqual(command[count_flag_index + 1], "30000")
        self.assertEqual(timeout, 100.0)

    def test_parser_normalizes_missing_keys_and_truncated_xml(self) -> None:
        document = fixture_documents()[0]
        del document["processor"]["cpu_power"]
        with self.assertRaisesRegex(ValueError, "document 0.*cpu_power"):
            parse_powermetrics_records(plistlib.dumps(document))
        with self.assertRaisesRegex(ValueError, "document 0.*valid plist"):
            parse_powermetrics_records(CORRUPT_PLIST)

    def test_registry_resolves_powermetrics_lazily(self) -> None:
        adapter, failure = resolve_telemetry(make_config(), FakeClock())
        self.assertIsNone(failure)
        self.assertIsInstance(adapter, TelemetryAdapter)
        self.assertEqual(adapter.name, "powermetrics")


if __name__ == "__main__":
    unittest.main()
