from __future__ import annotations

import statistics
import tempfile
import unittest
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from joulewise.adapters.node_client import NodeTaskResult
from joulewise.adapters.nvidia_smi import (
    BOUNDARY,
    RAIL_MANIFEST,
    RAW_IDLE_NAME,
    RAW_SAMPLES_NAME,
    NvidiaSmiTelemetryAdapter,
    parse_nvidia_smi_csv,
)
from joulewise.clock import FakeClock
from joulewise.interfaces import AdapterFailure, RunContext
from joulewise.schemas import BenchmarkConfig, FailureReason, TelemetryBackend

CSV_FIXTURE = (
    "2026/07/07 12:00:00.000, 10.0, 40\n"
    "2026/07/07 12:00:01.000, 12.0, 41\n"
    "2026/07/07 12:00:02.000, [N/A], 42\n"
    "2026/07/07 12:00:03.000, 14.0, 43\n"
    "\n"
)


def make_config(**overrides: Any) -> BenchmarkConfig:
    data: dict[str, Any] = {
        "schema_version": "0.1",
        "run_id": "run-nvidia-test",
        "model": {"name": "mock-model"},
        "quantization": {"name": "none"},
        "hardware_target": {
            "id": "rtx_3050",
            "transport": "ssh",
            "host": "test-node",
            "runtime_backend": "vllm",
            "telemetry_backend": "nvidia_smi",
        },
        "workload_profile": {
            "name": "mock_smoke",
            "prompt_tokens": 32,
            "output_tokens": 8,
        },
        "sampling": {"power_hz": 1.0, "idle_seconds": 3.0},
    }
    for key, value in overrides.items():
        if isinstance(value, dict):
            data[key] = {**data[key], **value}
        else:
            data[key] = value
    return BenchmarkConfig.from_mapping(data)


def make_context(config: BenchmarkConfig, root: Path) -> RunContext:
    raw_dir = root / "raw"
    logs_dir = root / "logs"
    outputs_dir = root / "outputs"
    for path in (raw_dir, logs_dir, outputs_dir):
        path.mkdir(parents=True)
    return RunContext(
        config=config,
        clock=FakeClock(start=1000.0),
        run_id="run-nvidia-test",
        bundle_path=root,
        raw_dir=raw_dir,
        logs_dir=logs_dir,
        outputs_dir=outputs_dir,
    )


def success_result(
    artifact_dir: Path,
    artifact_key: str,
    artifact_name: str,
    text: str,
    *,
    offset: float = 7.0,
    metadata: dict[str, Any] | None = None,
    worker_metadata: dict[str, Any] | None = None,
) -> NodeTaskResult:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / artifact_name).write_text(text, encoding="utf-8")
    raw_status = {
        "status": "succeeded",
        "message": "ok",
        "artifacts": {artifact_key: artifact_name},
        "metadata": {"worker": "fake", **(worker_metadata or {})},
    }
    return NodeTaskResult(
        ok=True,
        status="succeeded",
        failure_reason=None,
        message="ok",
        artifacts_path=artifact_dir,
        raw_status=raw_status,
        offset_estimate_s=offset,
        offset_bound_s=0.5,
        metadata=metadata or {"clock_alignment": {"offset_estimate_s": offset}},
    )


def failure_result(reason: FailureReason) -> NodeTaskResult:
    return NodeTaskResult(
        ok=False,
        status="unsupported" if reason == FailureReason.TELEMETRY_UNAVAILABLE else "failed",
        failure_reason=reason,
        message="fake failure",
        metadata={"clock_alignment": {"offset_estimate_s": 7.0}},
    )


class FakeClient:
    def __init__(self, results: list[NodeTaskResult]):
        self.results = list(results)
        self.tasks: list[dict[str, Any]] = []

    def run_task(self, task: dict[str, Any], *, timeout_s: float) -> NodeTaskResult:
        self.tasks.append({"task": task, "timeout_s": timeout_s})
        if not self.results:
            raise AssertionError("fake client exhausted")
        return self.results.pop(0)


class NvidiaSmiParserTests(unittest.TestCase):
    def test_parser_skips_na_power_and_emits_monotonic_rows(self) -> None:
        rows = parse_nvidia_smi_csv(CSV_FIXTURE)

        self.assertEqual(len(rows), 3)
        self.assertEqual(RAIL_MANIFEST, ["gpu_board"])
        self.assertEqual([row.power_w for row in rows], [10.0, 12.0, 14.0])
        self.assertEqual([row.temperature_c for row in rows], [40.0, 41.0, 43.0])
        self.assertTrue(rows[0].node_timestamp_s < rows[1].node_timestamp_s < rows[2].node_timestamp_s)
        self.assertEqual(
            rows[0].node_timestamp_s,
            datetime.strptime("2026/07/07 12:00:00.000", "%Y/%m/%d %H:%M:%S.%f").timestamp(),
        )

    def test_parser_uses_node_utc_offset_not_controller_timezone(self) -> None:
        old_tz = os.environ.get("TZ")
        os.environ["TZ"] = "America/Los_Angeles"
        if hasattr(time, "tzset"):
            time.tzset()
        try:
            rows = parse_nvidia_smi_csv(
                "2026/07/07 12:00:00.000, 10.0, 40\n",
                node_utc_offset_s=0.0,
            )
        finally:
            if old_tz is None:
                os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = old_tz
            if hasattr(time, "tzset"):
                time.tzset()

        self.assertEqual(rows[0].node_timestamp_s, 1783425600.0)

    def test_parser_records_legacy_timezone_warning_when_offset_missing(self) -> None:
        diagnostics: dict[str, Any] = {}

        parse_nvidia_smi_csv(
            "2026/07/07 12:00:00.000, 10.0, 40\n",
            diagnostics=diagnostics,
        )

        self.assertEqual(
            diagnostics["timestamp_timezone_source"],
            "parser_local_legacy_fallback",
        )
        self.assertIn("node UTC offset missing", diagnostics["warnings"][0])

    def test_parser_skips_only_malformed_final_truncated_row(self) -> None:
        diagnostics: dict[str, Any] = {}

        rows = parse_nvidia_smi_csv(
            "2026/07/07 12:00:00.000, 10.0, 40\n"
            "2026/07/07 12:00:01.000, 11",
            node_utc_offset_s=0.0,
            diagnostics=diagnostics,
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(diagnostics["truncated_final_rows_skipped"], 1)

    def test_parser_rejects_malformed_interior_row(self) -> None:
        with self.assertRaises(ValueError):
            parse_nvidia_smi_csv(
                "2026/07/07 12:00:00.000, 10\n"
                "2026/07/07 12:00:01.000, 11.0, 41\n",
                node_utc_offset_s=0.0,
            )


class NvidiaSmiAdapterTests(unittest.TestCase):
    def test_device_metadata_records_manifest_and_boundary(self) -> None:
        adapter = NvidiaSmiTelemetryAdapter(FakeClock(), FakeClient([]))

        metadata = adapter.device_metadata(make_config())

        self.assertEqual(metadata["telemetry"], "nvidia_smi")
        self.assertEqual(metadata["rail_manifest"], ["gpu_board"])
        self.assertEqual(metadata["boundary"], BOUNDARY)
        self.assertIn("host CPU/DRAM excluded", metadata["boundary"])
        self.assertEqual(metadata["query_fields"], ["timestamp", "power.draw", "temperature.gpu"])

    def test_measure_idle_happy_path_writes_raw_and_computes_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = make_config()
            context = make_context(config, root)
            client = FakeClient(
                [success_result(root / "artifacts", "nvidia_smi_idle_csv", RAW_IDLE_NAME, CSV_FIXTURE)]
            )
            adapter = NvidiaSmiTelemetryAdapter(FakeClock(start=100.0), client)

            baseline = adapter.measure_idle(config, context)

            self.assertEqual(baseline.telemetry_backend, TelemetryBackend.NVIDIA_SMI)
            self.assertEqual(baseline.sample_count, 3)
            self.assertEqual(baseline.power_w_mean, 12.0)
            self.assertEqual(baseline.power_w_stddev, statistics.stdev([10.0, 12.0, 14.0]))
            self.assertEqual(baseline.duration_s, 3.0)
            self.assertEqual((context.raw_dir / RAW_IDLE_NAME).read_text(encoding="utf-8"), CSV_FIXTURE)
            task = client.tasks[0]["task"]
            self.assertEqual(task["operation"], "measure_idle")
            self.assertEqual(task["telemetry"]["rail_manifest"], ["gpu_board"])
            self.assertEqual(task["telemetry"]["idle_seconds"], 3.0)

    def test_measure_idle_uses_worker_node_utc_offset_not_host_timezone(self) -> None:
        old_tz = os.environ.get("TZ")
        os.environ["TZ"] = "America/Los_Angeles"
        if hasattr(time, "tzset"):
            time.tzset()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                config = make_config()
                context = make_context(config, root)
                csv_text = (
                    "2026/01/02 03:04:05.000, 21.0, 45\n"
                    "2026/01/02 03:04:07.000, 23.0, 46\n"
                )
                client = FakeClient(
                    [
                        success_result(
                            root / "artifacts",
                            "nvidia_smi_idle_csv",
                            RAW_IDLE_NAME,
                            csv_text,
                            offset=0.0,
                            worker_metadata={
                                "node_utc_offset_s": 5.5 * 3600,
                                "node_tzname": "IST",
                            },
                        )
                    ]
                )
                adapter = NvidiaSmiTelemetryAdapter(FakeClock(start=100.0), client)

                baseline = adapter.measure_idle(config, context)
                thermal = adapter.thermal_state(config)
        finally:
            if old_tz is None:
                os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = old_tz
            if hasattr(time, "tzset"):
                time.tzset()

        self.assertEqual(baseline.duration_s, 2.0)
        self.assertEqual(thermal.timestamp_s, 1767303247.0)

    def test_measure_idle_failure_raises_adapter_failure(self) -> None:
        adapter = NvidiaSmiTelemetryAdapter(
            FakeClock(),
            FakeClient([failure_result(FailureReason.TELEMETRY_UNAVAILABLE)]),
        )

        with self.assertRaises(AdapterFailure) as caught:
            adapter.measure_idle(make_config())

        self.assertEqual(caught.exception.failure_reason, FailureReason.TELEMETRY_UNAVAILABLE)

    def test_start_sampling_surfaces_clock_alignment(self) -> None:
        alignment = {"method": "node_worker_clock_echo", "offset_estimate_s": 7.0}
        adapter = NvidiaSmiTelemetryAdapter(
            FakeClock(),
            FakeClient(
                [
                    NodeTaskResult(
                        ok=True,
                        status="succeeded",
                        failure_reason=None,
                        message="started",
                        offset_estimate_s=7.0,
                        offset_bound_s=0.25,
                        metadata={"clock_alignment": alignment},
                    )
                ]
            ),
        )

        result = adapter.start_sampling(make_config())

        self.assertTrue(result.ok)
        self.assertEqual(result.message, "started")
        self.assertEqual(result.metadata["clock_alignment"], alignment)
        self.assertEqual(result.metadata["offset_estimate_s"], 7.0)

    def test_stop_sampling_parses_samples_converts_timestamps_and_writes_raw(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = make_config()
            context = make_context(config, root)
            client = FakeClient(
                [success_result(root / "artifacts", "nvidia_smi_csv", RAW_SAMPLES_NAME, CSV_FIXTURE, offset=7.0)]
            )
            adapter = NvidiaSmiTelemetryAdapter(FakeClock(start=100.0), client)
            rows = parse_nvidia_smi_csv(CSV_FIXTURE)

            samples = adapter.stop_sampling(config, context)

            self.assertEqual(len(samples), 3)
            self.assertEqual(samples[0].rail, "gpu_board")
            self.assertEqual(samples[0].source, "nvidia_smi")
            self.assertEqual(samples[0].power_w, 10.0)
            self.assertEqual(samples[0].timestamp_s, rows[0].node_timestamp_s - 7.0)
            self.assertEqual((context.raw_dir / RAW_SAMPLES_NAME).read_text(encoding="utf-8"), CSV_FIXTURE)
            thermal = adapter.thermal_state(config)
            self.assertEqual(thermal.temperature_c, 43.0)
            self.assertEqual(thermal.timestamp_s, rows[-1].node_timestamp_s - 7.0)

    def test_stop_sampling_uses_worker_node_utc_offset_not_host_timezone(self) -> None:
        old_tz = os.environ.get("TZ")
        os.environ["TZ"] = "America/Los_Angeles"
        if hasattr(time, "tzset"):
            time.tzset()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                config = make_config()
                context = make_context(config, root)
                csv_text = (
                    "2026/01/02 03:04:05.000, 21.0, 45\n"
                    "2026/01/02 03:04:07.000, 23.0, 46\n"
                )
                adapter = NvidiaSmiTelemetryAdapter(
                    FakeClock(start=100.0),
                    FakeClient(
                        [
                            success_result(
                                root / "artifacts",
                                "nvidia_smi_csv",
                                RAW_SAMPLES_NAME,
                                csv_text,
                                offset=0.0,
                                worker_metadata={
                                    "node_utc_offset_s": 5.5 * 3600,
                                    "node_tzname": "IST",
                                },
                            )
                        ]
                    ),
                )

                samples = adapter.stop_sampling(config, context)
        finally:
            if old_tz is None:
                os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = old_tz
            if hasattr(time, "tzset"):
                time.tzset()

        self.assertEqual([sample.timestamp_s for sample in samples], [1767303245.0, 1767303247.0])

    def test_stop_sampling_failure_raises_adapter_failure(self) -> None:
        adapter = NvidiaSmiTelemetryAdapter(
            FakeClock(),
            FakeClient([failure_result(FailureReason.UNKNOWN_ERROR)]),
        )

        with self.assertRaises(AdapterFailure) as caught:
            adapter.stop_sampling(make_config())

        self.assertEqual(caught.exception.failure_reason, FailureReason.UNKNOWN_ERROR)

    def test_timestamp_domain_conversion_subtracts_offset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            single = "2026/07/07 12:00:00.000, 21.5, 45\n"
            row = parse_nvidia_smi_csv(single)[0]
            adapter = NvidiaSmiTelemetryAdapter(
                FakeClock(),
                FakeClient([success_result(root / "artifacts", "nvidia_smi_csv", RAW_SAMPLES_NAME, single, offset=12.5)]),
            )

            sample = adapter.stop_sampling(make_config())[0]

            self.assertEqual(sample.timestamp_s, row.node_timestamp_s - 12.5)

    def test_thermal_state_without_samples_is_unknown(self) -> None:
        adapter = NvidiaSmiTelemetryAdapter(FakeClock(start=123.0), FakeClient([]))

        thermal = adapter.thermal_state(make_config())

        self.assertEqual(thermal.timestamp_s, 123.0)
        self.assertIsNone(thermal.temperature_c)
        self.assertFalse(thermal.metadata["temperature_c_available"])


if __name__ == "__main__":
    unittest.main()
