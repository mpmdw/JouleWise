from __future__ import annotations

import hashlib
import json
import math
import plistlib
import subprocess
import tempfile
import unittest
from datetime import timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

from joulewise.bundle import BundleError, write_raw_artifact as write_bundle_raw_artifact
from joulewise.adapters import resolve_telemetry
from joulewise.adapters.powermetrics import (
    RAIL_MANIFEST,
    RICH_IDLE_NAME,
    RICH_TELEMETRY_NAME,
    RAW_IDLE_NAME,
    RAW_IDLE_POST_NAME,
    RAW_SAMPLES_NAME,
    SAMPLERS,
    PowermetricsTelemetryAdapter,
    decode_rich_telemetry,
    idle_window_gpu_quality,
    parse_powermetrics_records,
    rich_telemetry_jsonl,
    rich_telemetry_jsonl_from_records,
    samples_from_records,
    sudoers_line,
)
from joulewise.clock import FakeClock
from joulewise.controller import run_benchmark
from joulewise.interfaces import RunContext, TelemetryAdapter
from joulewise.schemas import BenchmarkConfig, FailureReason, RunStatus, TelemetryBackend
from joulewise.uncertainty_evidence import derive_powermetrics_clock_evidence

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


def documents_to_stream(documents: list[dict[str, Any]]) -> bytes:
    return b"\0".join(plistlib.dumps(document) for document in documents)


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
            self.assertEqual(
                {sample.interval_end_s for sample in rows}, {record.timestamp_s}
            )
            self.assertEqual(
                {sample.interval_start_s for sample in rows},
                {record.timestamp_s - record.elapsed_ns / 1_000_000_000.0},
            )

    def test_interval_power_matches_energy_counters_within_ten_microjoules(self) -> None:
        for record in parse_powermetrics_records(FIXTURE.read_bytes()):
            power_energy_j = (
                record.combined_power_w * record.elapsed_ns / 1_000_000_000.0
            )
            counter_energy_j = sum(record.rail_energy_mj.values()) / 1000.0
            self.assertLessEqual(abs(power_energy_j - counter_energy_j), 1e-5)

    def test_thermal_pressure_without_temperature(self) -> None:
        records = parse_powermetrics_records(FIXTURE.read_bytes())
        self.assertEqual({record.thermal_pressure for record in records}, {"Nominal"})
        adapter = PowermetricsTelemetryAdapter(FakeClock(start=123.0))
        adapter._remember_records(records)
        state = adapter.thermal_state(make_config())
        self.assertEqual(state.timestamp_s, 123.0)
        self.assertIsNone(state.temperature_c)
        self.assertEqual(state.thermal_pressure, "Nominal")

    def test_rich_telemetry_jsonl_decodes_fixture_fields(self) -> None:
        lines = rich_telemetry_jsonl(FIXTURE.read_bytes()).splitlines()
        self.assertEqual(len(lines), 5)
        first = json.loads(lines[0])
        self.assertEqual(first["index"], 0)
        self.assertEqual(first["elapsed_ns"], fixture_documents()[0]["elapsed_ns"])
        self.assertAlmostEqual(first["gpu"]["freq_hz"], 338.0, places=12)
        self.assertAlmostEqual(first["gpu"]["idle_ratio"], 0.997924, places=12)
        self.assertEqual(len(first["gpu"]["dvfm_states"]), 13)
        self.assertAlmostEqual(first["gpu"]["active_freq_mhz_weighted"], 338.0, places=9)
        self.assertAlmostEqual(first["processor_combined_power_w"], 1.47572, places=12)
        self.assertEqual([cluster["name"] for cluster in first["clusters"]], [
            "E-Cluster",
            "P0-Cluster",
            "P1-Cluster",
        ])
        self.assertEqual([len(cluster["cpus"]) for cluster in first["clusters"]], [4, 6, 6])
        self.assertAlmostEqual(first["clusters"][0]["freq_hz"], 1_416_230_000.0, places=3)
        self.assertIn("idle_ratio", first["clusters"][1]["cpus"][0])

    def test_rich_telemetry_omits_empty_malformed_state_entries(self) -> None:
        documents = fixture_documents()
        documents[0]["gpu"]["dvfm_states"] = [
            {"freq": {}},
            {"used_ratio": []},
            {"freq": 338, "used_ratio": 1.0},
        ]
        first = json.loads(rich_telemetry_jsonl(documents_to_stream(documents)).splitlines()[0])
        self.assertEqual(first["gpu"]["dvfm_states"], [{"freq": 338, "used_ratio": 1.0}])

    def test_idle_window_gpu_quality_clean_fixture_and_contaminated_sequence(self) -> None:
        clean = idle_window_gpu_quality(decode_rich_telemetry(FIXTURE.read_bytes()))
        self.assertAlmostEqual(clean["gpu_idle_ratio_mean"], 0.9611138, places=12)
        self.assertAlmostEqual(clean["gpu_idle_ratio_min"], 0.846584, places=12)
        self.assertAlmostEqual(clean["gpu_freq_mhz_mean"], 325.9148, places=12)
        self.assertAlmostEqual(clean["gpu_freq_hz_mean"], 325.9148, places=12)
        self.assertIs(clean["idle_window_suspect"], False)

        documents = fixture_documents()
        for document in documents[:3]:
            document["gpu"]["freq_hz"] = 1363.0
            document["gpu"]["idle_ratio"] = 0.0
        contaminated = idle_window_gpu_quality(
            decode_rich_telemetry(documents_to_stream(documents))
        )
        self.assertIs(contaminated["idle_window_suspect"], True)

        documents = fixture_documents()
        documents[0]["gpu"]["freq_hz"] = 338.0
        documents[0]["gpu"]["idle_ratio"] = 0.0
        single_blip = idle_window_gpu_quality(
            decode_rich_telemetry(documents_to_stream(documents))
        )
        self.assertIs(single_blip["idle_window_suspect"], False)

    def test_idle_quality_keeps_rich_records_byte_identical(self) -> None:
        records = decode_rich_telemetry(FIXTURE.read_bytes())
        before = rich_telemetry_jsonl_from_records(records)

        idle_window_gpu_quality(records)

        self.assertEqual(rich_telemetry_jsonl_from_records(records), before)
        first = json.loads(before.splitlines()[0])
        self.assertEqual(first["gpu"]["freq_hz"], 338.0)
        self.assertNotIn("gpu_freq_mhz_mean", first["gpu"])

    def test_idle_window_gpu_quality_absent_gpu_is_unknown(self) -> None:
        documents = fixture_documents()
        for document in documents:
            document.pop("gpu", None)
        quality = idle_window_gpu_quality(decode_rich_telemetry(documents_to_stream(documents)))
        self.assertIsNone(quality["gpu_idle_ratio_mean"])
        self.assertIsNone(quality["gpu_idle_ratio_min"])
        self.assertIsNone(quality["gpu_freq_mhz_mean"])
        self.assertIsNone(quality["gpu_freq_hz_mean"])
        self.assertIsNone(quality["idle_window_suspect"])

    def test_rich_decode_tolerates_missing_optional_gpu_and_cluster_shapes(self) -> None:
        documents = fixture_documents()
        documents[0].pop("gpu", None)
        documents[0]["processor"].pop("clusters", None)
        for key in ("dvfm_states", "sw_state", "sw_requested_state"):
            documents[1]["gpu"].pop(key, None)
        documents[1]["processor"]["clusters"] = [
            "not-a-cluster",
            {"name": "partial", "freq_hz": 123.0},
        ]
        documents[2]["gpu"]["dvfm_states"] = []
        documents[2]["processor"]["clusters"][0]["cpus"] = [
            "not-a-core",
            {"cpu": 0},
            {"freq_hz": 456.0},
        ]

        records = decode_rich_telemetry(documents_to_stream(documents))

        self.assertIsNone(records[0]["gpu"])
        self.assertEqual(records[0]["clusters"], [])
        self.assertEqual(records[1]["gpu"]["dvfm_states"], [])
        self.assertEqual(records[1]["gpu"]["sw_state"], [])
        self.assertEqual(records[1]["gpu"]["sw_requested_state"], [])
        self.assertEqual(len(records[1]["clusters"]), 1)
        self.assertEqual(records[1]["clusters"][0]["name"], "partial")
        self.assertEqual(records[1]["clusters"][0]["cpus"], [])
        self.assertIsNone(records[2]["gpu"]["active_freq_mhz_weighted"])
        self.assertEqual(records[2]["clusters"][0]["cpus"][0]["cpu"], 0)
        self.assertIsNone(records[2]["clusters"][0]["cpus"][0]["freq_hz"])
        self.assertEqual(records[2]["clusters"][0]["cpus"][1]["freq_hz"], 456.0)

    def test_decode_rich_telemetry_drops_garbage_trailing_document(self) -> None:
        records = decode_rich_telemetry(FIXTURE.read_bytes() + b"\0garbage")
        self.assertEqual(len(records), 5)

    def test_complete_final_plist_array_is_not_dropped(self) -> None:
        data = FIXTURE.read_bytes() + b"\0" + plistlib.dumps([])
        with self.assertRaises(ValueError) as ctx:
            parse_powermetrics_records(data)
        self.assertIn("not a dictionary", str(ctx.exception))

    def test_rich_helpers_handle_zero_document_streams(self) -> None:
        self.assertEqual(decode_rich_telemetry(b"\0\0"), [])
        self.assertEqual(rich_telemetry_jsonl(b"\0\0"), "")
        quality = idle_window_gpu_quality([])
        self.assertIsNone(quality["gpu_idle_ratio_mean"])
        self.assertIsNone(quality["gpu_idle_ratio_min"])
        self.assertIsNone(quality["gpu_freq_mhz_mean"])
        self.assertIsNone(quality["gpu_freq_hz_mean"])
        self.assertIsNone(quality["idle_window_suspect"])

    def test_idle_window_gpu_quality_boundary_semantics(self) -> None:
        documents = fixture_documents()
        for document in documents:
            document["gpu"]["freq_hz"] = 338.0
            document["gpu"]["idle_ratio"] = 1.0

        one_low = fixture_documents()
        for document in one_low:
            document["gpu"]["freq_hz"] = 338.0
            document["gpu"]["idle_ratio"] = 1.0
        one_low[0]["gpu"]["idle_ratio"] = 0.0
        self.assertIs(
            idle_window_gpu_quality(
                decode_rich_telemetry(documents_to_stream(one_low))
            )["idle_window_suspect"],
            False,
        )

        two_low = fixture_documents()
        for document in two_low:
            document["gpu"]["freq_hz"] = 338.0
            document["gpu"]["idle_ratio"] = 1.0
        two_low[0]["gpu"]["idle_ratio"] = 0.0
        two_low[1]["gpu"]["idle_ratio"] = 0.0
        self.assertIs(
            idle_window_gpu_quality(
                decode_rich_telemetry(documents_to_stream(two_low))
            )["idle_window_suspect"],
            True,
        )

        exact_idle_threshold = fixture_documents()
        for document in exact_idle_threshold:
            document["gpu"]["freq_hz"] = 338.0
            document["gpu"]["idle_ratio"] = 0.80
        self.assertIs(
            idle_window_gpu_quality(
                decode_rich_telemetry(documents_to_stream(exact_idle_threshold))
            )["idle_window_suspect"],
            False,
        )

        exact_freq_threshold = fixture_documents()
        for document in exact_freq_threshold:
            document["gpu"]["freq_hz"] = 800.0
            document["gpu"]["idle_ratio"] = 1.0
        self.assertIs(
            idle_window_gpu_quality(
                decode_rich_telemetry(documents_to_stream(exact_freq_threshold))
            )["idle_window_suspect"],
            False,
        )

        above_freq_threshold = fixture_documents()
        for document in above_freq_threshold:
            document["gpu"]["freq_hz"] = 800.001
            document["gpu"]["idle_ratio"] = 1.0
        self.assertIs(
            idle_window_gpu_quality(
                decode_rich_telemetry(documents_to_stream(above_freq_threshold))
            )["idle_window_suspect"],
            True,
        )

    def test_rich_telemetry_jsonl_format_round_trips_and_preserves_order(self) -> None:
        documents = fixture_documents()
        lines = rich_telemetry_jsonl(FIXTURE.read_bytes()).splitlines()
        self.assertEqual(len(lines), len(documents))

        parsed = [json.loads(line) for line in lines]
        self.assertEqual(lines, [json.dumps(record, sort_keys=True) for record in parsed])
        self.assertEqual([record["index"] for record in parsed], list(range(len(parsed))))
        self.assertEqual([record["index"] for record in parsed], sorted(record["index"] for record in parsed))

        timestamps = [record["timestamp_s"] for record in parsed]
        self.assertEqual(timestamps, sorted(timestamps))
        self.assertEqual(len(set(timestamps)), len(timestamps))
        first = utc_epoch(documents[0]["timestamp"])
        cumulative_s = 0.0
        expected_timestamps = []
        for document in documents:
            expected_timestamps.append(first + cumulative_s)
            cumulative_s += int(document["elapsed_ns"]) / 1_000_000_000.0
        self.assertEqual(timestamps, expected_timestamps)

        for record in parsed:
            self.assertEqual(
                set(record),
                {
                    "clusters",
                    "combined_power_delta_w",
                    "elapsed_ns",
                    "gpu",
                    "index",
                    "processor_combined_power_w",
                    "rail_sum_power_w",
                    "timestamp_s",
                },
            )
            self.assertIsInstance(record["clusters"], list)
            self.assertTrue(record["gpu"] is None or isinstance(record["gpu"], dict))
            for key in ("combined_power_delta_w", "processor_combined_power_w", "rail_sum_power_w"):
                self.assertTrue(record[key] is None or isinstance(record[key], float))


class PowermetricsAdapterTests(unittest.TestCase):
    def test_device_metadata_declares_manifest_and_timestamp_derivation(self) -> None:
        adapter = PowermetricsTelemetryAdapter(FakeClock())
        metadata = adapter.device_metadata(make_config())
        self.assertEqual(metadata["telemetry"], "powermetrics")
        self.assertEqual(metadata["rail_manifest"], RAIL_MANIFEST)
        self.assertIn("elapsed_ns", metadata["timestamp_derivation"])
        self.assertEqual(metadata["powermetrics"]["samplers_requested"], SAMPLERS)
        self.assertEqual(
            metadata["powermetrics"]["samplers_available"], "probe-unavailable"
        )

    def test_measure_idle_computes_mean_and_stddev_from_fixture(self) -> None:
        fixture = FIXTURE.read_bytes()
        documents = fixture_documents()
        expected_totals = [
            sum(float(document["processor"][rail]) for rail in RAIL_MANIFEST) / 1000.0
            for document in documents
        ]
        intervals_s = [
            int(document["elapsed_ns"]) / 1_000_000_000.0
            for document in documents
        ]
        duration_s = math.fsum(intervals_s)
        weights = [duration / duration_s for duration in intervals_s]
        expected_mean = math.fsum(
            weight * value for weight, value in zip(weights, expected_totals, strict=True)
        )
        q = math.fsum(weight * weight for weight in weights)
        expected_variance = math.fsum(
            weight * (value - expected_mean) ** 2
            for weight, value in zip(weights, expected_totals, strict=True)
        ) / (1.0 - q)

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        adapter = PowermetricsTelemetryAdapter(FakeClock())
        with patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run):
            baseline = adapter.measure_idle(make_config())

        metadata = adapter.device_metadata(make_config())
        self.assertEqual(
            metadata["powermetrics"]["samplers_available"], SAMPLERS.split(",")
        )
        self.assertTrue(metadata["powermetrics"]["samplers_probe"]["ok"])
        self.assertAlmostEqual(baseline.power_w_mean, expected_mean, places=12)
        self.assertAlmostEqual(
            baseline.power_w_stddev,
            math.sqrt(expected_variance),
            places=12,
        )
        self.assertEqual(baseline.sample_count, len(documents))
        self.assertEqual(baseline.telemetry_backend, TelemetryBackend.POWERMETRICS)
        self.assertAlmostEqual(baseline.power_w_mean, 0.46465690457640496, places=12)
        self.assertAlmostEqual(baseline.power_w_stddev, 0.5949163238867929, places=12)
        self.assertAlmostEqual(baseline.duration_s, 5.091935956, places=12)
        self.assertAlmostEqual(baseline.gpu_idle_ratio_min, 0.846584, places=12)
        self.assertAlmostEqual(baseline.gpu_freq_mhz_mean, 325.9148, places=12)
        self.assertAlmostEqual(baseline.gpu_freq_hz_mean, 325.9148, places=12)
        self.assertEqual(baseline.gpu_freq_mhz_mean, baseline.gpu_freq_hz_mean)
        self.assertIs(baseline.idle_window_suspect, False)

    def test_measure_idle_preserves_raw_and_rich_idle_artifacts_with_context(self) -> None:
        fixture = FIXTURE.read_bytes()

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        adapter = PowermetricsTelemetryAdapter(FakeClock(start=200.0))
        config = make_config()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "run"
            root.mkdir()
            context = RunContext(
                config=config,
                clock=FakeClock(start=200.0),
                run_id="run-1",
                bundle_path=root,
                raw_dir=root / "raw",
                logs_dir=root / "logs",
                outputs_dir=root / "outputs",
            )
            with patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run):
                adapter.measure_idle(config, context)

            self.assertEqual((root / "raw" / "powermetrics_idle.plist").read_bytes(), fixture)
            rich_lines = (root / RICH_IDLE_NAME).read_text().splitlines()
            self.assertEqual(len(rich_lines), 5)
            self.assertEqual(json.loads(rich_lines[0])["index"], 0)

    def test_measure_idle_rich_write_failure_does_not_break_baseline(self) -> None:
        fixture = FIXTURE.read_bytes()

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        adapter = PowermetricsTelemetryAdapter(FakeClock(start=200.0))
        config = make_config()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "run"
            root.mkdir()
            context = RunContext(
                config=config,
                clock=FakeClock(start=200.0),
                run_id="run-1",
                bundle_path=root,
                raw_dir=root / "raw",
                logs_dir=root / "logs",
                outputs_dir=root / "outputs",
            )
            with (
                patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
                patch(
                    "joulewise.adapters.powermetrics.write_derived_artifact",
                    side_effect=BundleError("boom"),
                ),
            ):
                baseline = adapter.measure_idle(config, context)

            self.assertEqual(baseline.sample_count, 5)
            self.assertEqual((root / "raw" / "powermetrics_idle.plist").read_bytes(), fixture)
            self.assertIn(
                "BundleError: boom",
                adapter.device_metadata(config)["rich_telemetry_idle_error"],
            )

    def test_measure_idle_rich_write_oserror_does_not_break_baseline(self) -> None:
        fixture = FIXTURE.read_bytes()

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        adapter = PowermetricsTelemetryAdapter(FakeClock(start=200.0))
        config = make_config()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "run"
            root.mkdir()
            context = RunContext(
                config=config,
                clock=FakeClock(start=200.0),
                run_id="run-1",
                bundle_path=root,
                raw_dir=root / "raw",
                logs_dir=root / "logs",
                outputs_dir=root / "outputs",
            )
            with (
                patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
                patch(
                    "joulewise.adapters.powermetrics.write_derived_artifact",
                    side_effect=OSError("disk full"),
                ),
            ):
                baseline = adapter.measure_idle(config, context)

            self.assertEqual(baseline.sample_count, 5)
            self.assertEqual((root / "raw" / "powermetrics_idle.plist").read_bytes(), fixture)
            self.assertIn(
                "OSError: disk full",
                adapter.device_metadata(config)["rich_telemetry_idle_error"],
            )

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
        metadata = adapter.device_metadata(make_config())
        self.assertEqual(
            metadata["powermetrics"]["samplers_available"], "probe-unavailable"
        )
        self.assertEqual(
            metadata["powermetrics"]["samplers_probe"]["reason"], "returncode_1"
        )

    def test_sampler_probe_not_found_records_probe_failure_metadata(self) -> None:
        def fake_run(command, **kwargs):
            raise FileNotFoundError("powermetrics")

        adapter = PowermetricsTelemetryAdapter(FakeClock())
        with patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run):
            result = adapter.start_sampling(make_config())

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.TELEMETRY_UNAVAILABLE)
        metadata = adapter.device_metadata(make_config())
        self.assertEqual(
            metadata["powermetrics"]["samplers_available"], "probe-unavailable"
        )
        self.assertEqual(
            metadata["powermetrics"]["samplers_probe"],
            {"ok": False, "reason": "not_found"},
        )

    def test_sampler_probe_timeout_records_probe_failure_metadata(self) -> None:
        def fake_run(command, **kwargs):
            raise subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])

        adapter = PowermetricsTelemetryAdapter(FakeClock())
        with patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run):
            result = adapter.start_sampling(make_config())

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.UNKNOWN_ERROR)
        metadata = adapter.device_metadata(make_config())
        self.assertEqual(
            metadata["powermetrics"]["samplers_available"], "probe-unavailable"
        )
        self.assertEqual(
            metadata["powermetrics"]["samplers_probe"],
            {"ok": False, "reason": "timeout"},
        )

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
            rich_lines = (root / RICH_TELEMETRY_NAME).read_text().splitlines()
            self.assertEqual(len(rich_lines), 5)
            self.assertAlmostEqual(
                json.loads(rich_lines[0])["processor_combined_power_w"],
                1.47572,
                places=12,
            )
            self.assertEqual(len(samples), 15)
            for offset in range(0, len(samples), 3):
                rows = samples[offset : offset + 3]
                self.assertEqual([sample.rail for sample in rows], RAIL_MANIFEST)
                self.assertEqual(len({sample.timestamp_s for sample in rows}), 1)

    def test_evidence_stop_drains_until_boundary_bracketing_sample(self) -> None:
        documents = fixture_documents()
        config = make_config(sampling={"power_hz": 2.0, "idle_seconds": 5.0})
        clock = FakeClock(start=100.0)
        adapter = PowermetricsTelemetryAdapter(clock)
        operational_now = [0.0]
        instances = []

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(FIXTURE.read_bytes())
            return completed(command)

        class AppendingPopen:
            def __init__(self, command, **kwargs):
                instances.append(self)
                self.path = Path(command[command.index("-o") + 1])
                self.pre_drain_bytes = documents_to_stream(documents[:1])
                self.path.write_bytes(self.pre_drain_bytes)
                self.returncode = None
                self.terminated = False
                self.appended = 0
                self.final_bytes = None

            def poll(self):
                return self.returncode

            def terminate(self):
                self.terminated = True
                self.final_bytes = self.path.read_bytes()
                self.returncode = 0

            def communicate(self, timeout=None):
                self.returncode = 0
                return b"", b""

        def fake_sleep(seconds):
            operational_now[0] += seconds
            process = instances[0]
            process.appended += 1
            process.path.write_bytes(
                documents_to_stream(documents[: 1 + process.appended])
            )

        with (
            patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
            patch("joulewise.adapters.powermetrics.subprocess.Popen", AppendingPopen),
            patch(
                "joulewise.adapters.powermetrics.time.monotonic",
                side_effect=lambda: operational_now[0],
            ),
            patch("joulewise.adapters.powermetrics.time.sleep", side_effect=fake_sleep),
        ):
            self.assertTrue(adapter.start_sampling(config).ok)
            sampling_started = clock.stamp()
            clock.sleep(1.5)
            sampling_stopped = clock.stamp()
            result = adapter.stop_sampling_with_evidence(
                config,
                None,
                sampling_started=sampling_started,
                sampling_stopped=sampling_stopped,
            )

        endpoints = [
            result.samples[index].timestamp_s
            for index in range(0, len(result.samples), len(RAIL_MANIFEST))
        ]
        self.assertEqual(instances[0].appended, 2)
        self.assertTrue(instances[0].terminated)
        expected_final_bytes = documents_to_stream(documents[:3])
        self.assertEqual(instances[0].final_bytes, expected_final_bytes)
        self.assertEqual(
            instances[0].final_bytes[: len(instances[0].pre_drain_bytes)],
            instances[0].pre_drain_bytes,
        )
        final_frames = instances[0].final_bytes.split(b"\0")
        pre_drain_frames = instances[0].pre_drain_bytes.split(b"\0")
        self.assertEqual(final_frames[: len(pre_drain_frames)], pre_drain_frames)
        self.assertEqual(len(final_frames), len(pre_drain_frames) + 2)
        for frame in pre_drain_frames:
            self.assertEqual(final_frames.count(frame), 1)
        self.assertEqual(len(endpoints), 3)
        expected_endpoints = [sampling_started.epoch_s]
        expected_endpoints.extend(
            sampling_started.epoch_s
            + math.fsum(
                int(document["elapsed_ns"]) / 1_000_000_000.0
                for document in documents[1 : index + 1]
            )
            for index in range(1, 3)
        )
        self.assertEqual(endpoints, expected_endpoints)
        self.assertLess(expected_endpoints[-2], sampling_stopped.epoch_s)
        self.assertGreaterEqual(expected_endpoints[-1], sampling_stopped.epoch_s)

    def test_evidence_stop_releases_process_when_drain_polling_raises(self) -> None:
        documents = fixture_documents()
        config = make_config(sampling={"power_hz": 2.0, "idle_seconds": 5.0})
        clock = FakeClock(start=100.0)
        adapter = PowermetricsTelemetryAdapter(clock)
        instances = []

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(FIXTURE.read_bytes())
            return completed(command)

        class PollingExceptionPopen:
            def __init__(self, command, **kwargs):
                instances.append(self)
                Path(command[command.index("-o") + 1]).write_bytes(
                    documents_to_stream(documents[:1])
                )
                self.returncode = None
                self.terminated = False

            def poll(self):
                return self.returncode

            def terminate(self):
                self.terminated = True
                self.returncode = 0

            def communicate(self, timeout=None):
                self.returncode = 0
                return b"", b""

        with (
            patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
            patch(
                "joulewise.adapters.powermetrics.subprocess.Popen",
                PollingExceptionPopen,
            ),
        ):
            self.assertTrue(adapter.start_sampling(config).ok)
            sampling_started = clock.stamp()
            with (
                patch.object(
                    adapter,
                    "_capture_brackets_stop",
                    side_effect=RuntimeError("injected polling failure"),
                ),
                self.assertRaisesRegex(RuntimeError, "injected polling failure"),
            ):
                adapter.stop_sampling_with_evidence(
                    config,
                    None,
                    sampling_started=sampling_started,
                    sampling_stopped=clock.stamp(),
                )

        self.assertTrue(instances[0].terminated)
        self.assertIsNone(adapter._process)

    def test_evidence_stop_deadline_includes_growing_capture_read(self) -> None:
        documents = fixture_documents()
        config = make_config(sampling={"power_hz": 2.0, "idle_seconds": 5.0})
        clock = FakeClock(start=100.0)
        adapter = PowermetricsTelemetryAdapter(clock)
        operational_now = [0.0]
        instances = []

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(FIXTURE.read_bytes())
            return completed(command)

        class GrowingPopen:
            def __init__(self, command, **kwargs):
                instances.append(self)
                self.path = Path(command[command.index("-o") + 1])
                self.path.write_bytes(documents_to_stream(documents[:1]))
                self.returncode = None
                self.terminated = False

            def poll(self):
                return self.returncode

            def terminate(self):
                self.terminated = True
                self.returncode = 0

            def communicate(self, timeout=None):
                self.returncode = 0
                return b"", b""

        original_read_bytes = Path.read_bytes
        consume_drain_read = [False]
        drain_read_consumed = [False]
        parse_calls = []

        def deadline_consuming_read(path):
            data = original_read_bytes(path)
            if (
                consume_drain_read[0]
                and not drain_read_consumed[0]
                and instances
                and path == instances[0].path
            ):
                drain_read_consumed[0] = True
                operational_now[0] += 0.75
                path.write_bytes(documents_to_stream(documents))
            return data

        def tracking_parse(*args, **kwargs):
            parse_calls.append(args[0])
            if (
                consume_drain_read[0]
                and drain_read_consumed[0]
                and instances
                and not instances[0].terminated
            ):
                operational_now[0] += 0.5
            return parse_powermetrics_records(*args, **kwargs)

        def deadline_guarded_derive(*args, **kwargs):
            if instances and not instances[0].terminated:
                raise AssertionError("deadline must skip provisional derivation")
            return derive_powermetrics_clock_evidence(*args, **kwargs)

        with (
            patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
            patch("joulewise.adapters.powermetrics.subprocess.Popen", GrowingPopen),
            patch(
                "joulewise.adapters.powermetrics.time.monotonic",
                side_effect=lambda: operational_now[0],
            ),
            patch.object(Path, "read_bytes", deadline_consuming_read),
            patch(
                "joulewise.adapters.powermetrics.parse_powermetrics_records",
                side_effect=tracking_parse,
            ),
            patch(
                "joulewise.adapters.powermetrics.derive_powermetrics_clock_evidence",
                side_effect=deadline_guarded_derive,
            ),
        ):
            self.assertTrue(adapter.start_sampling(config).ok)
            parse_calls.clear()
            consume_drain_read[0] = True
            result = adapter.stop_sampling_with_evidence(
                config,
                None,
                sampling_started=clock.stamp(),
                sampling_stopped=clock.stamp(),
            )

        self.assertTrue(instances[0].terminated)
        self.assertIsNone(adapter._process)
        self.assertAlmostEqual(operational_now[0], 1.25, places=12)
        self.assertTrue(drain_read_consumed[0])
        self.assertTrue(parse_calls)
        self.assertEqual(parse_calls[0], documents_to_stream(documents[:1]))
        self.assertEqual(set(parse_calls[1:]), {documents_to_stream(documents)})
        self.assertEqual(len(result.samples), len(documents) * len(RAIL_MANIFEST))

    def test_evidence_stop_hard_times_out_on_silent_sampler(self) -> None:
        documents = fixture_documents()
        config = make_config(sampling={"power_hz": 2.0, "idle_seconds": 5.0})
        clock = FakeClock(start=100.0)
        adapter = PowermetricsTelemetryAdapter(clock)
        operational_now = [0.0]
        instances = []

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(FIXTURE.read_bytes())
            return completed(command)

        class SilentPopen:
            def __init__(self, command, **kwargs):
                instances.append(self)
                Path(command[command.index("-o") + 1]).write_bytes(
                    documents_to_stream(documents[:1])
                )
                self.returncode = None
                self.terminated = False

            def poll(self):
                return self.returncode

            def terminate(self):
                self.terminated = True
                self.returncode = 0

            def communicate(self, timeout=None):
                self.returncode = 0
                return b"", b""

        def fake_sleep(seconds):
            operational_now[0] += seconds

        with (
            patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
            patch("joulewise.adapters.powermetrics.subprocess.Popen", SilentPopen),
            patch(
                "joulewise.adapters.powermetrics.time.monotonic",
                side_effect=lambda: operational_now[0],
            ),
            patch("joulewise.adapters.powermetrics.time.sleep", side_effect=fake_sleep),
        ):
            self.assertTrue(adapter.start_sampling(config).ok)
            sampling_started = clock.stamp()
            clock.sleep(2.0)
            result = adapter.stop_sampling_with_evidence(
                config,
                None,
                sampling_started=sampling_started,
                sampling_stopped=clock.stamp(),
            )

        self.assertTrue(instances[0].terminated)
        self.assertEqual(len(result.samples), len(RAIL_MANIFEST))
        self.assertAlmostEqual(operational_now[0], 1.25, places=12)

    def test_evidence_stop_preserves_current_in_window_timestamp_construction(self) -> None:
        documents = fixture_documents()
        initial_documents = documents[:3]
        config = make_config(sampling={"power_hz": 2.0, "idle_seconds": 5.0})
        clock = FakeClock(start=100.0)
        adapter = PowermetricsTelemetryAdapter(clock)

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(FIXTURE.read_bytes())
            return completed(command)

        class BracketedPopen:
            def __init__(self, command, **kwargs):
                Path(command[command.index("-o") + 1]).write_bytes(
                    documents_to_stream(initial_documents)
                )
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
            patch("joulewise.adapters.powermetrics.subprocess.Popen", BracketedPopen),
            patch(
                "joulewise.adapters.powermetrics.time.sleep",
                side_effect=AssertionError("already bracketed capture must not wait"),
            ),
        ):
            self.assertTrue(adapter.start_sampling(config).ok)
            sampling_started = clock.stamp()
            clock.sleep(2.0)
            result = adapter.stop_sampling_with_evidence(
                config,
                None,
                sampling_started=sampling_started,
                sampling_stopped=clock.stamp(),
            )

        endpoints = [
            result.samples[index].timestamp_s
            for index in range(0, len(result.samples), len(RAIL_MANIFEST))
        ]
        expected_endpoints = [100.0]
        expected_endpoints.extend(
            100.0
            + math.fsum(
                int(document["elapsed_ns"]) / 1_000_000_000.0
                for document in initial_documents[1 : index + 1]
            )
            for index in range(1, len(initial_documents))
        )
        self.assertEqual(endpoints, expected_endpoints)

    def test_stop_sampling_rich_write_failure_does_not_break_samples(self) -> None:
        fixture = FIXTURE.read_bytes()
        config = make_config(sampling={"power_hz": 2.0, "idle_seconds": 5.0})
        clock = FakeClock(start=100.0)
        adapter = PowermetricsTelemetryAdapter(clock)

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        class FakePopen:
            def __init__(self, command, **kwargs):
                Path(command[command.index("-o") + 1]).write_bytes(fixture)
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
                patch(
                    "joulewise.adapters.powermetrics.write_derived_artifact",
                    side_effect=BundleError("boom"),
                ),
            ):
                self.assertTrue(adapter.start_sampling(config, context).ok)
                samples = adapter.stop_sampling(config, context)

            self.assertEqual(len(samples), 15)
            self.assertEqual((root / "raw" / RAW_SAMPLES_NAME).read_bytes(), fixture)
            self.assertIn(
                "BundleError: boom",
                adapter.device_metadata(config)["rich_telemetry_error"],
            )

    def test_raw_write_failure_retains_native_capture_until_salvage_ack(self) -> None:
        fixture = FIXTURE.read_bytes()
        config = make_config(sampling={"power_hz": 2.0, "idle_seconds": 5.0})
        adapter = PowermetricsTelemetryAdapter(FakeClock(start=100.0))

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        class FakePopen:
            def __init__(self, command, **kwargs):
                Path(command[command.index("-o") + 1]).write_bytes(fixture)
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
                clock=FakeClock(start=100.0),
                run_id="run-custody",
                bundle_path=root,
                raw_dir=root / "raw",
                logs_dir=root / "logs",
                outputs_dir=root / "outputs",
            )
            with (
                patch(
                    "joulewise.adapters.powermetrics.subprocess.run",
                    side_effect=fake_run,
                ),
                patch("joulewise.adapters.powermetrics.subprocess.Popen", FakePopen),
            ):
                self.assertTrue(adapter.start_sampling(config, context).ok)
                with patch(
                    "joulewise.adapters.powermetrics.write_raw_artifact",
                    side_effect=BundleError("injected raw write failure"),
                ), self.assertRaisesRegex(BundleError, "injected raw write failure"):
                    adapter.stop_sampling(config, context)

            retained = adapter._pending_captures[RAW_SAMPLES_NAME]
            self.assertTrue(retained.is_file())
            self.assertEqual(retained.read_bytes(), fixture)
            self.assertFalse((context.raw_dir / RAW_SAMPLES_NAME).exists())

            report = adapter.salvage_custody(context)

            self.assertTrue(report[0]["acknowledged"])
            self.assertEqual(
                (context.raw_dir / RAW_SAMPLES_NAME).read_bytes(),
                fixture,
            )
            self.assertFalse(retained.exists())

    def test_ack_failure_after_raw_write_retains_native_capture_for_salvage(self) -> None:
        fixture = FIXTURE.read_bytes()
        config = make_config(sampling={"power_hz": 2.0, "idle_seconds": 5.0})
        adapter = PowermetricsTelemetryAdapter(FakeClock(start=100.0))

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        class FakePopen:
            def __init__(self, command, **kwargs):
                Path(command[command.index("-o") + 1]).write_bytes(fixture)
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
                clock=FakeClock(start=100.0),
                run_id="run-ack-interrupt",
                bundle_path=root,
                raw_dir=root / "raw",
                logs_dir=root / "logs",
                outputs_dir=root / "outputs",
            )
            with (
                patch(
                    "joulewise.adapters.powermetrics.subprocess.run",
                    side_effect=fake_run,
                ),
                patch("joulewise.adapters.powermetrics.subprocess.Popen", FakePopen),
            ):
                self.assertTrue(adapter.start_sampling(config, context).ok)
                with patch.object(
                    RunContext,
                    "acknowledge_custody",
                    side_effect=OSError("injected fsync acknowledgement failure"),
                ), self.assertRaisesRegex(OSError, "fsync acknowledgement failure"):
                    adapter.stop_sampling(config, context)

            retained = adapter._pending_captures[RAW_SAMPLES_NAME]
            destination = context.raw_dir / RAW_SAMPLES_NAME
            self.assertTrue(retained.is_file())
            self.assertEqual(destination.read_bytes(), fixture)
            self.assertFalse((context.logs_dir / "custody").exists())

            report = adapter.salvage_custody(context)

            self.assertTrue(report[0]["acknowledged"])
            self.assertFalse(retained.exists())
            acknowledgement = (
                context.logs_dir
                / "custody"
                / "powermetrics-powermetrics_plist.json"
            )
            self.assertTrue(acknowledgement.is_file())
            self.assertEqual(
                json.loads(acknowledgement.read_text())["custody_token"],
                "powermetrics-powermetrics_plist",
            )

    def test_controller_salvages_each_native_capture_after_first_write_failure(self) -> None:
        fixture = FIXTURE.read_bytes()
        config = make_config(
            workload_profile={"output_tokens": 300},
            sampling={"power_hz": 2.0, "idle_seconds": 5.0},
        )
        def fake_run(command, **kwargs):
            if "-o" not in command:
                return completed(command)
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        class FakePopen:
            def __init__(self, command, **kwargs):
                self.path = Path(command[command.index("-o") + 1])
                self.path.write_bytes(fixture)
                self.returncode = None

            def poll(self):
                return self.returncode

            def terminate(self):
                self.returncode = 0

            def communicate(self, timeout=None):
                self.path.write_bytes(fixture)
                self.returncode = 0
                return b"", b""

        for artifact_name in (RAW_IDLE_NAME, RAW_SAMPLES_NAME, RAW_IDLE_POST_NAME):
            with self.subTest(artifact_name=artifact_name), tempfile.TemporaryDirectory() as tmp:
                failed_once = False

                def flaky_write(context, name, data):
                    nonlocal failed_once
                    if name == artifact_name and not failed_once:
                        failed_once = True
                        raise BundleError("injected first custody write failure")
                    return write_bundle_raw_artifact(context, name, data)

                with (
                    patch(
                        "joulewise.adapters.powermetrics.subprocess.run",
                        side_effect=fake_run,
                    ),
                    patch(
                        "joulewise.adapters.powermetrics.subprocess.Popen",
                        FakePopen,
                    ),
                    patch(
                        "joulewise.adapters.powermetrics.write_raw_artifact",
                        side_effect=flaky_write,
                    ),
                    patch(
                        "joulewise.controller._capture_environment",
                        return_value={"capture_scope": "test"},
                    ),
                    patch("joulewise.bundle.platform.platform", return_value="test"),
                    patch("joulewise.bundle._capture_source_state", return_value={"git_commit": "unknown", "tracked": "unknown", "staged": "unknown", "untracked": "unknown", "diff_sha256": "unknown"}),
                ):
                    bundle_path, _summary = run_benchmark(
                        config,
                        Path(tmp),
                        FakeClock(start=10.0),
                    )

                self.assertTrue(failed_once)
                self.assertEqual(
                    (bundle_path / "raw" / artifact_name).read_bytes(),
                    fixture,
                )

    def test_stop_sampling_rich_write_oserror_does_not_break_samples(self) -> None:
        fixture = FIXTURE.read_bytes()
        config = make_config(sampling={"power_hz": 2.0, "idle_seconds": 5.0})
        clock = FakeClock(start=100.0)
        adapter = PowermetricsTelemetryAdapter(clock)

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        class FakePopen:
            def __init__(self, command, **kwargs):
                Path(command[command.index("-o") + 1]).write_bytes(fixture)
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
                patch(
                    "joulewise.adapters.powermetrics.write_derived_artifact",
                    side_effect=OSError("disk full"),
                ),
            ):
                self.assertTrue(adapter.start_sampling(config, context).ok)
                samples = adapter.stop_sampling(config, context)

            self.assertEqual(len(samples), 15)
            self.assertEqual((root / "raw" / RAW_SAMPLES_NAME).read_bytes(), fixture)
            self.assertIn(
                "OSError: disk full",
                adapter.device_metadata(config)["rich_telemetry_error"],
            )

    def test_stop_sampling_drops_trailing_garbage_and_records_diagnostic(self) -> None:
        config = make_config()
        adapter = PowermetricsTelemetryAdapter(FakeClock(start=10.0))
        garbage_stream = FIXTURE.read_bytes() + b"\0garbage"

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(FIXTURE.read_bytes())
            return completed(command)

        class GarbagePopen:
            def __init__(self, command, **kwargs):
                self.path = Path(command[command.index("-o") + 1])
                self.path.write_bytes(FIXTURE.read_bytes())
                self.returncode = None

            def poll(self):
                return self.returncode

            def terminate(self):
                self.returncode = 0

            def communicate(self, timeout=None):
                self.path.write_bytes(garbage_stream)
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
                patch("joulewise.adapters.powermetrics.subprocess.Popen", GarbagePopen),
            ):
                self.assertTrue(adapter.start_sampling(config, context).ok)
                samples = adapter.stop_sampling(config, context)

            self.assertEqual((root / "raw" / RAW_SAMPLES_NAME).read_bytes(), garbage_stream)
            self.assertEqual(len(samples), 15)
            diagnostics = adapter.device_metadata(config)["parse_diagnostics"]
            self.assertEqual(len(diagnostics), 1)
            self.assertEqual(diagnostics[0]["artifact"], f"raw/{RAW_SAMPLES_NAME}")
            self.assertEqual(diagnostics[0]["capture"], "measured_run")
            self.assertEqual(diagnostics[0]["action"], "dropped_final_unparseable_frame")
            self.assertEqual(diagnostics[0]["frame_index"], 5)
            self.assertEqual(diagnostics[0]["byte_count"], len(b"garbage"))
            self.assertEqual(diagnostics[0]["sha256"], hashlib.sha256(b"garbage").hexdigest())
            self.assertTrue((root / RICH_TELEMETRY_NAME).exists())

    def test_run_bundle_metadata_records_dropped_powermetrics_tail_diagnostic(self) -> None:
        fixture = FIXTURE.read_bytes()
        tail = b"<plist"
        truncated_stream = fixture + b"\0" + tail
        config = make_config(
            workload_profile={"output_tokens": 300},
            sampling={"power_hz": 2.0, "idle_seconds": 5.0},
        )

        def fake_run(command, **kwargs):
            if "-o" in command:
                Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        class TruncatedTailPopen:
            def __init__(self, command, **kwargs):
                self.path = Path(command[command.index("-o") + 1])
                self.path.write_bytes(fixture)
                self.returncode = None

            def poll(self):
                return self.returncode

            def terminate(self):
                self.returncode = 0

            def communicate(self, timeout=None):
                self.path.write_bytes(truncated_stream)
                self.returncode = 0
                return b"", b""

        with tempfile.TemporaryDirectory() as tmp:
            with (
                patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
                patch("joulewise.adapters.powermetrics.subprocess.Popen", TruncatedTailPopen),
            ):
                bundle_path, summary = run_benchmark(config, Path(tmp), FakeClock(start=10.0))

            self.assertEqual(summary.status, RunStatus.SUCCEEDED)
            self.assertEqual((bundle_path / "raw" / RAW_SAMPLES_NAME).read_bytes(), truncated_stream)
            self.assertEqual(len((bundle_path / "power_trace.csv").read_text().splitlines()), 16)
            self.assertEqual(
                (bundle_path / "power_trace.csv").read_text().splitlines()[0],
                "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s",
            )
            metadata = json.loads((bundle_path / "metadata.json").read_text())
            diagnostics = metadata["device"]["parse_diagnostics"]
            measured = [
                diagnostic
                for diagnostic in diagnostics
                if diagnostic["artifact"] == f"raw/{RAW_SAMPLES_NAME}"
            ]
            self.assertEqual(len(measured), 1)
            self.assertEqual(measured[0]["capture"], "measured_run")
            self.assertEqual(measured[0]["action"], "dropped_final_unparseable_frame")
            self.assertEqual(measured[0]["frame_index"], 5)
            self.assertEqual(measured[0]["byte_count"], len(tail))
            self.assertEqual(measured[0]["sha256"], hashlib.sha256(tail).hexdigest())

    def test_rich_telemetry_file_is_regenerable_from_preserved_raw_plist(self) -> None:
        fixture = FIXTURE.read_bytes()
        config = make_config(sampling={"power_hz": 2.0, "idle_seconds": 5.0})
        clock = FakeClock(start=100.0)
        adapter = PowermetricsTelemetryAdapter(clock)

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        class FakePopen:
            def __init__(self, command, **kwargs):
                Path(command[command.index("-o") + 1]).write_bytes(fixture)
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
                self.assertTrue(adapter.start_sampling(config, context).ok)
                adapter.stop_sampling(config, context)

            raw_bytes = (root / "raw" / RAW_SAMPLES_NAME).read_bytes()
            self.assertEqual((root / RICH_TELEMETRY_NAME).read_text(), rich_telemetry_jsonl(raw_bytes))

    def test_corrupt_stop_preserves_raw_before_parse_failure(self) -> None:
        config = make_config()
        adapter = PowermetricsTelemetryAdapter(FakeClock(start=10.0))

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(FIXTURE.read_bytes())
            return completed(command)

        class CorruptPopen:
            def __init__(self, command, **kwargs):
                self.path = Path(command[command.index("-o") + 1])
                self.path.write_bytes(FIXTURE.read_bytes())
                self.returncode = None

            def poll(self):
                return self.returncode

            def terminate(self):
                self.returncode = 0

            def communicate(self, timeout=None):
                self.path.write_bytes(CORRUPT_PLIST)
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

    def test_start_sampling_waits_until_first_document_is_parseable(self) -> None:
        fixture = FIXTURE.read_bytes()
        sleep_calls = []

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        class DelayedPopen:
            path: Path | None = None

            def __init__(self, command, **kwargs):
                type(self).path = Path(command[command.index("-o") + 1])
                self.returncode = None

            def poll(self):
                return self.returncode

            def terminate(self):
                self.returncode = 0

            def communicate(self, timeout=None):
                self.returncode = 0
                return b"", b""

        def fake_sleep(seconds):
            sleep_calls.append(seconds)
            if len(sleep_calls) == 2:
                DelayedPopen.path.write_bytes(fixture)

        adapter = PowermetricsTelemetryAdapter(FakeClock(start=200.0))
        with (
            patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
            patch("joulewise.adapters.powermetrics.subprocess.Popen", DelayedPopen),
            patch("joulewise.adapters.powermetrics.time.sleep", side_effect=fake_sleep),
        ):
            result = adapter.start_sampling(make_config())

        self.assertTrue(result.ok)
        self.assertGreaterEqual(len(sleep_calls), 2)
        self.assertEqual(result.metadata["readiness"]["ready_check"], "first_parseable_plist_document")

    def test_start_sampling_readiness_timeout_is_structured_and_terminates(self) -> None:
        instances = []

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(FIXTURE.read_bytes())
            return completed(command)

        class NeverReadyPopen:
            def __init__(self, command, **kwargs):
                instances.append(self)
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

        adapter = PowermetricsTelemetryAdapter(FakeClock())
        with (
            patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
            patch("joulewise.adapters.powermetrics.subprocess.Popen", NeverReadyPopen),
            patch("joulewise.adapters.powermetrics.READINESS_TIMEOUT_S", 0.0),
        ):
            result = adapter.start_sampling(make_config())

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("parseable plist", result.message)
        self.assertTrue(instances[0].terminated)

    def test_start_sampling_readiness_fast_path_does_not_sleep(self) -> None:
        fixture = FIXTURE.read_bytes()

        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return completed(command)

        class ImmediatePopen:
            def __init__(self, command, **kwargs):
                Path(command[command.index("-o") + 1]).write_bytes(fixture)
                self.returncode = None

            def poll(self):
                return self.returncode

        adapter = PowermetricsTelemetryAdapter(FakeClock())
        with (
            patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
            patch("joulewise.adapters.powermetrics.subprocess.Popen", ImmediatePopen),
            patch("joulewise.adapters.powermetrics.time.sleep") as sleep,
        ):
            result = adapter.start_sampling(make_config())

        self.assertTrue(result.ok)
        sleep.assert_not_called()

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
