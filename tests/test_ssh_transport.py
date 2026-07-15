"""CI-safe tests for the Slice 2K SSH transport adapter."""

from __future__ import annotations

import subprocess
import unittest
from typing import Any

from joulewise.adapters.ssh_transport import RunnerCompleted, SshTransport
from joulewise.clock import FakeClock
from joulewise.schemas import (
    BenchmarkConfig,
    HardwareTarget,
    ModelConfig,
    QuantizationConfig,
    RuntimeBackend,
    TelemetryBackend,
    TransportKind,
    WorkloadProfile,
    FailureReason,
)


def config() -> BenchmarkConfig:
    return BenchmarkConfig(
        schema_version="1",
        model=ModelConfig(name="m"),
        quantization=QuantizationConfig(name="none"),
        hardware_target=HardwareTarget(
            id="node",
            transport=TransportKind.SSH,
            runtime_backend=RuntimeBackend.VLLM,
            telemetry_backend=TelemetryBackend.NVIDIA_SMI,
            host="gpu box",
        ),
        workload_profile=WorkloadProfile(name="w", prompt_text="hello"),
    )


class CapturingRunner:
    def __init__(self, result: RunnerCompleted | None = None, exc: BaseException | None = None):
        self.result = result or RunnerCompleted(returncode=0)
        self.exc = exc
        self.calls: list[tuple[list[str], float]] = []

    def __call__(self, argv: list[str], *, timeout: float) -> RunnerCompleted:
        self.calls.append((argv, timeout))
        if self.exc is not None:
            raise self.exc
        return self.result


class SshTransportTests(unittest.TestCase):
    def make_transport(self, runner: Any) -> SshTransport:
        return SshTransport(
            FakeClock(),
            "gpu box",
            runner=runner,
            command_timeout_s=12,
            file_timeout_s=13,
        )

    def test_ssh_command_construction_preserves_destination_and_args(self) -> None:
        runner = CapturingRunner()
        transport = self.make_transport(runner)

        result = transport.run_command(config(), ["python3", "-c", "print('x y')"])

        self.assertTrue(result.ok)
        argv, timeout = runner.calls[0]
        self.assertEqual(timeout, 12)
        self.assertEqual(argv[0], "ssh")
        self.assertIn("BatchMode=yes", argv)
        self.assertIn("ConnectTimeout=10", argv)
        self.assertIn("gpu box", argv)
        separator_index = argv.index("--")
        self.assertLess(separator_index, argv.index("gpu box"))
        self.assertEqual(argv[separator_index + 1], "gpu box")
        self.assertEqual(argv[separator_index + 2 :], ["python3", "-c", "print('x y')"])

    def test_run_command_success_returns_stdout_metadata(self) -> None:
        runner = CapturingRunner(RunnerCompleted(returncode=0, stdout=b"ok\n"))
        result = self.make_transport(runner).run_command(config(), ["true"])

        self.assertTrue(result.ok)
        self.assertEqual(result.metadata["returncode"], 0)
        self.assertEqual(result.metadata["stdout"], "ok\n")

    def test_run_command_ssh_255_is_transport_unavailable(self) -> None:
        runner = CapturingRunner(
            RunnerCompleted(returncode=255, stderr=b"ssh: connect to host failed\n")
        )
        result = self.make_transport(runner).run_command(config(), ["true"])

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.TRANSPORT_UNAVAILABLE)
        self.assertEqual(result.metadata["returncode"], 255)
        self.assertEqual(result.metadata["execution_state"], "ambiguous")

    def test_run_command_oserror_is_transport_unavailable(self) -> None:
        runner = CapturingRunner(exc=OSError("missing ssh"))
        result = self.make_transport(runner).run_command(config(), ["true"])

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.TRANSPORT_UNAVAILABLE)
        self.assertIn("missing ssh", result.message or "")

    def test_run_command_timeout_is_transport_unavailable(self) -> None:
        runner = CapturingRunner(exc=subprocess.TimeoutExpired(["ssh"], 1))
        result = self.make_transport(runner).run_command(config(), ["true"])

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.TRANSPORT_UNAVAILABLE)
        self.assertEqual(result.metadata["ssh_error_class"], "timeout")

    def test_run_command_remote_nonzero_is_unknown_error(self) -> None:
        runner = CapturingRunner(RunnerCompleted(returncode=3, stderr=b"remote failed\n"))
        result = self.make_transport(runner).run_command(config(), ["false"])

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertEqual(result.metadata["returncode"], 3)
        self.assertEqual(result.metadata["execution_state"], "completed")
        self.assertIn("remote failed", result.message or "")

    def test_non_255_connection_refused_phrase_is_remote_execution_failure(self) -> None:
        runner = CapturingRunner(
            RunnerCompleted(
                returncode=3,
                stderr=b"application backend connection refused\n",
            )
        )

        result = self.make_transport(runner).run_command(config(), ["worker"])

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertEqual(result.metadata["returncode"], 3)
        self.assertEqual(result.metadata["execution_state"], "completed")

    def test_collect_artifact_failure_is_transport_unavailable(self) -> None:
        runner = CapturingRunner(RunnerCompleted(returncode=1, stderr=b"scp failed\n"))
        transport = self.make_transport(runner)

        result = transport.collect_artifact(config(), "/remote/artifacts", "/local/artifacts")

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.TRANSPORT_UNAVAILABLE)
        argv, timeout = runner.calls[0]
        self.assertEqual(timeout, 13)
        self.assertEqual(argv[0], "scp")
        self.assertIn("-r", argv)
        separator_index = argv.index("--")
        self.assertEqual(argv[separator_index + 1 :], ["gpu box:/remote/artifacts", "/local/artifacts"])
        self.assertIn("gpu box:/remote/artifacts", argv)


if __name__ == "__main__":
    unittest.main()
