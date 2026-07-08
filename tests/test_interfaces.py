import json
import sys
import unittest
from pathlib import Path

from joulewise.adapters import LocalTransport, MockRuntimeAdapter, MockTelemetryAdapter
from joulewise.clock import FakeClock
from joulewise.interfaces import (
    RuntimeAdapter,
    SuiteRuntimeAdapter,
    TelemetryAdapter,
    TransportAdapter,
)
from joulewise.schemas import BenchmarkConfig, TelemetryBackend


ROOT = Path(__file__).resolve().parents[1]


class InterfaceTests(unittest.TestCase):
    """Protocol-conformance checks against the shipped adapters (Slice 2B)."""

    def setUp(self) -> None:
        data = json.loads((ROOT / "configs" / "examples" / "mock_local.json").read_text())
        self.config = BenchmarkConfig.from_mapping(data)
        self.clock = FakeClock(start=1000.0)

    def test_mock_runtime_satisfies_protocol(self) -> None:
        runtime = MockRuntimeAdapter(self.clock)
        self.assertIsInstance(runtime, RuntimeAdapter)
        result = runtime.run_workload(self.config)
        self.assertEqual(result.output_token_count, 8)
        self.assertEqual(result.events[0].event_type, "phase_start")
        self.assertEqual(result.events[0].phase, "prefill")

    def test_mock_runtime_satisfies_suite_protocol(self) -> None:
        self.assertIsInstance(MockRuntimeAdapter(self.clock), SuiteRuntimeAdapter)

    def test_mock_telemetry_satisfies_protocol(self) -> None:
        telemetry = MockTelemetryAdapter(self.clock)
        self.assertIsInstance(telemetry, TelemetryAdapter)
        idle = telemetry.measure_idle(self.config)
        self.assertTrue(telemetry.start_sampling(self.config).ok)
        self.clock.sleep(1.0)
        samples = telemetry.stop_sampling(self.config)
        self.assertEqual(idle.telemetry_backend, TelemetryBackend.MOCK)
        self.assertGreaterEqual(len(samples), 2)

    def test_local_transport_satisfies_protocol(self) -> None:
        transport = LocalTransport()
        self.assertIsInstance(transport, TransportAdapter)
        result = transport.run_command(self.config, [sys.executable, "-c", "pass"])
        self.assertTrue(result.ok)


if __name__ == "__main__":
    unittest.main()
