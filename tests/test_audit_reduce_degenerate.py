from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

from joulewise import reduce as reduce_module
from joulewise.bundle import RunBundleWriter
from joulewise.clock import FakeClock
from joulewise.interfaces import PowerSample, RuntimeEvent
from joulewise.schemas import BenchmarkConfig, FailureReason, RunStatus

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"

DEFAULT_IDLE = {
    "power_w_mean": 5.0,
    "power_w_stddev": 0.0,
    "duration_s": 1.0,
    "sample_count": 2,
    "telemetry_backend": "mock",
}


def load_config(run_id: str) -> BenchmarkConfig:
    data = json.loads(EXAMPLE_CONFIG.read_text())
    data["run_id"] = run_id
    return BenchmarkConfig.from_mapping(data)


class ReduceAuditCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self.counter = 0

    def make_writer(self) -> RunBundleWriter:
        self.counter += 1
        return RunBundleWriter.create(
            self.runs_root,
            load_config(f"audit-reduce-{self.counter}"),
            FakeClock(start=100.0),
        )

    def add_window(self, writer: RunBundleWriter, start_s: float, end_s: float) -> None:
        writer.append_event(RuntimeEvent(start_s, "stage_started", "measured_run", "start"))
        writer.append_event(RuntimeEvent(end_s, "stage_completed", "measured_run", "end"))

    def write_metadata(self, writer: RunBundleWriter, *, idle: dict | None = DEFAULT_IDLE, **extra) -> None:
        metadata = {
            "device": {"telemetry": "mock", "rail_manifest": ["mock"]},
            "adapters": {"telemetry": {"name": "mock"}},
        }
        if idle is not None:
            metadata["idle_baseline"] = idle
        metadata.update(extra)
        writer.write_metadata(metadata)


class ReduceDegenerateBugPins(ReduceAuditCase):
    # R2: _idle_baseline(metadata) is called outside the structured-failure try.
    @unittest.expectedFailure
    def test_malformed_idle_baseline_is_structured_failure(self) -> None:
        writer = self.make_writer()
        self.add_window(writer, 0.0, 2.0)
        writer.write_power_trace(
            [PowerSample(0.0, 7.0, "mock", "mock"), PowerSample(1.0, 7.0, "mock", "mock")]
        )
        self.write_metadata(writer, idle={})

        try:
            summary = reduce_module.reduce_bundle(writer.path)
        except KeyError as exc:
            self.fail(f"R2: raw KeyError instead of structured FAILED summary: {exc}")
        except Exception as exc:
            self.fail(f"R2: raw {type(exc).__name__} instead of structured FAILED summary")
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("idle_baseline", summary.failure_message or "")

    # R3: idle_baseline.power_w_mean=NaN yields a succeeded summary with NaN metrics.
    def test_nan_idle_baseline_fails_instead_of_nan_success(self) -> None:
        writer = self.make_writer()
        self.add_window(writer, 0.0, 2.0)
        writer.write_power_trace(
            [
                PowerSample(0.0, 7.0, "mock", "mock"),
                PowerSample(1.0, 7.0, "mock", "mock"),
                PowerSample(2.0, 7.0, "mock", "mock"),
            ]
        )
        self.write_metadata(writer, idle={**DEFAULT_IDLE, "power_w_mean": math.nan})

        summary = reduce_module.reduce_bundle(writer.path)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertFalse(math.isnan(summary.energy_request_j or 0.0))

    # R4: in-window power_trace NaN reduces to succeeded with NaN gross energy.
    def test_nan_power_trace_fails_instead_of_nan_success(self) -> None:
        writer = self.make_writer()
        self.add_window(writer, 0.0, 2.0)
        writer.write_power_trace(
            [
                PowerSample(0.0, 7.0, "mock", "mock"),
                PowerSample(1.0, math.nan, "mock", "mock"),
                PowerSample(2.0, 7.0, "mock", "mock"),
            ]
        )
        self.write_metadata(writer)

        summary = reduce_module.reduce_bundle(writer.path)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertFalse(math.isnan(summary.gross_energy_j or 0.0))

    # R5: nonnumeric thermal metadata raises raw ValueError while building quality.
    @unittest.expectedFailure
    def test_bad_thermal_metadata_is_structured_failure(self) -> None:
        writer = self.make_writer()
        self.add_window(writer, 0.0, 2.0)
        writer.write_power_trace(
            [
                PowerSample(0.0, 7.0, "mock", "mock"),
                PowerSample(1.0, 7.0, "mock", "mock"),
                PowerSample(2.0, 7.0, "mock", "mock"),
            ]
        )
        self.write_metadata(
            writer,
            thermal_pre={"timestamp_s": 0.0, "temperature_c": "hot"},
            thermal_post={"timestamp_s": 2.0, "temperature_c": 42.0},
        )

        try:
            summary = reduce_module.reduce_bundle(writer.path)
        except ValueError as exc:
            self.fail(f"R5: raw ValueError instead of structured FAILED summary: {exc}")
        except Exception as exc:
            self.fail(f"R5: raw {type(exc).__name__} instead of structured FAILED summary")
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)


if __name__ == "__main__":
    unittest.main()
