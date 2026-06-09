import json
import unittest
from pathlib import Path

from joulewise.interfaces import (
    AdapterResult,
    PowerSample,
    RuntimeAdapter,
    RuntimeEvent,
    RuntimeResult,
    TelemetryAdapter,
    ThermalState,
    TransportAdapter,
)
from joulewise.schemas import BenchmarkConfig, IdleBaseline, TelemetryBackend


ROOT = Path(__file__).resolve().parents[1]


class MockRuntime:
    name = "mock"

    def prepare(self, config: BenchmarkConfig) -> AdapterResult:
        return AdapterResult(ok=True)

    def warmup(self, config: BenchmarkConfig) -> AdapterResult:
        return AdapterResult(ok=True)

    def run_workload(self, config: BenchmarkConfig) -> RuntimeResult:
        return RuntimeResult(
            events=[
                RuntimeEvent(
                    timestamp_s=0.0,
                    event_type="phase_start",
                    phase="decode",
                    message="mock decode started",
                )
            ],
            token_count=40,
            output_token_count=8,
        )

    def cleanup(self, config: BenchmarkConfig) -> AdapterResult:
        return AdapterResult(ok=True)


class MockTelemetry:
    name = "mock"

    def device_metadata(self, config: BenchmarkConfig) -> dict:
        return {"device": config.hardware_target.id}

    def measure_idle(self, config: BenchmarkConfig) -> IdleBaseline:
        return IdleBaseline(
            power_w_mean=5.0,
            power_w_stddev=0.1,
            duration_s=1.0,
            sample_count=2,
            telemetry_backend=TelemetryBackend.MOCK,
        )

    def start_sampling(self, config: BenchmarkConfig) -> AdapterResult:
        return AdapterResult(ok=True)

    def stop_sampling(self, config: BenchmarkConfig) -> list[PowerSample]:
        return [
            PowerSample(timestamp_s=0.0, power_w=7.0, source="mock"),
            PowerSample(timestamp_s=1.0, power_w=7.5, source="mock"),
        ]

    def thermal_state(self, config: BenchmarkConfig) -> ThermalState:
        return ThermalState(timestamp_s=0.0, temperature_c=42.0)


class MockTransport:
    name = "local"

    def connection_metadata(self, config: BenchmarkConfig) -> dict:
        return {"transport": "local"}

    def run_command(self, config: BenchmarkConfig, command: list[str]) -> AdapterResult:
        return AdapterResult(ok=True, metadata={"command": command})

    def collect_artifact(self, config: BenchmarkConfig, source: str, destination: str) -> AdapterResult:
        return AdapterResult(ok=True, metadata={"source": source, "destination": destination})


class InterfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        data = json.loads((ROOT / "configs" / "examples" / "mock_local.json").read_text())
        self.config = BenchmarkConfig.from_mapping(data)

    def test_mock_runtime_satisfies_protocol(self) -> None:
        runtime = MockRuntime()
        self.assertIsInstance(runtime, RuntimeAdapter)
        result = runtime.run_workload(self.config)
        self.assertEqual(result.output_token_count, 8)
        self.assertEqual(result.events[0].phase, "decode")

    def test_mock_telemetry_satisfies_protocol(self) -> None:
        telemetry = MockTelemetry()
        self.assertIsInstance(telemetry, TelemetryAdapter)
        idle = telemetry.measure_idle(self.config)
        samples = telemetry.stop_sampling(self.config)
        self.assertEqual(idle.telemetry_backend, TelemetryBackend.MOCK)
        self.assertEqual(len(samples), 2)

    def test_mock_transport_satisfies_protocol(self) -> None:
        transport = MockTransport()
        self.assertIsInstance(transport, TransportAdapter)
        result = transport.run_command(self.config, ["echo", "ok"])
        self.assertTrue(result.ok)


if __name__ == "__main__":
    unittest.main()
