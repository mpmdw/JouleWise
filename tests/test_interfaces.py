import json
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.adapters import LocalTransport, MockRuntimeAdapter, MockTelemetryAdapter
from joulewise.clock import FakeClock
from joulewise.interfaces import (
    RuntimeAdapter,
    SuiteRuntimeAdapter,
    TelemetryAdapter,
    TransportAdapter,
    acknowledge_durable_custody,
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

    def test_custody_acknowledgement_is_atomic_bundle_local_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bundle"
            artifact = bundle / "raw" / "native.bin"
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(b"native evidence")

            acknowledgement = acknowledge_durable_custody(
                bundle,
                "token-compatible-001",
                [artifact],
            )

            payload = json.loads(acknowledgement.acknowledgement_path.read_text())
            self.assertEqual(payload["custody_token"], "token-compatible-001")
            self.assertEqual(payload["artifacts"], ["raw/native.bin"])
            self.assertFalse(
                list(acknowledgement.acknowledgement_path.parent.glob("*.tmp"))
            )

            outside = Path(tmp) / "outside.bin"
            outside.write_bytes(b"not bundle custody")
            with self.assertRaisesRegex(ValueError, "inside the run bundle"):
                acknowledge_durable_custody(bundle, "token-002", [outside])

            empty = bundle / "raw" / "empty-collection"
            empty.mkdir()
            with self.assertRaisesRegex(ValueError, "contains no evidence files"):
                acknowledge_durable_custody(bundle, "token-003", [empty])


if __name__ == "__main__":
    unittest.main()
