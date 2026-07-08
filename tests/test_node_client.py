"""CI-safe tests for the shared Slice 2K node-worker client."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from joulewise.adapters.node_client import (
    ClockMarker,
    NodeWorkerClient,
    compute_stage_bound,
    convert_node_timestamp,
)
from joulewise.interfaces import AdapterResult
from joulewise.schemas import FailureReason


class SequencedClock:
    def __init__(self, values: list[float]):
        self.values = list(values)

    def now(self) -> float:
        if not self.values:
            raise AssertionError("clock sequence exhausted")
        return self.values.pop(0)

    def sleep(self, seconds: float) -> None:
        raise AssertionError("sleep should not be used by node client tests")

    def info(self) -> dict[str, Any]:
        return {"kind": "sequenced"}


def valid_telemetry_task(task_id: str = "task-telemetry-idle-001") -> dict[str, Any]:
    return {
        "protocol_version": 1,
        "task_id": task_id,
        "run_id": "run-loopback-001",
        "task_type": "telemetry",
        "operation": "measure_idle",
        "node_role": None,
        "paths": {"state_dir": ""},
        "telemetry": {
            "backend": "nvidia_smi",
            "interval_ms": 100,
            "query_fields": ["timestamp", "power.draw"],
            "rail_manifest": ["gpu_board"],
        },
    }


class LoopbackTransport:
    def __init__(self) -> None:
        self.clock_alignment: dict[str, Any] | None = None

    def run(self, command: list[str], *, timeout_s: float | None = None) -> AdapterResult:
        if command[:2] == ["mkdir", "-p"]:
            for path in command[2:]:
                Path(path).mkdir(parents=True, exist_ok=True)
            return AdapterResult(ok=True, metadata={"returncode": 0, "stdout": ""})
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            timeout=timeout_s,
        )
        stdout = completed.stdout.decode("utf-8", errors="replace")
        stderr = completed.stderr.decode("utf-8", errors="replace")
        metadata = {
            "returncode": completed.returncode,
            "stdout": stdout,
            "stderr_tail": stderr[-1000:],
        }
        if completed.returncode == 0:
            return AdapterResult(ok=True, metadata=metadata)
        return AdapterResult(
            ok=False,
            failure_reason=FailureReason.UNKNOWN_ERROR,
            message=stderr[-1000:] or "remote command failed",
            metadata=metadata,
        )

    def put_file(
        self, source: str, destination: str, *, timeout_s: float | None = None
    ) -> AdapterResult:
        Path(destination).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return AdapterResult(ok=True, metadata={"source": source, "destination": destination})

    def collect(
        self, source: str, destination: str, *, timeout_s: float | None = None
    ) -> AdapterResult:
        shutil.copytree(source, destination)
        return AdapterResult(ok=True, metadata={"source": source, "destination": destination})

    def record_clock_alignment(self, alignment: dict[str, Any]) -> None:
        self.clock_alignment = alignment


class EchoTransport(LoopbackTransport):
    def __init__(self, stdout: str):
        super().__init__()
        self.stdout = stdout

    def run(self, command: list[str], *, timeout_s: float | None = None) -> AdapterResult:
        if "--clock-echo" in command:
            return AdapterResult(ok=True, metadata={"returncode": 0, "stdout": self.stdout})
        return super().run(command, timeout_s=timeout_s)


class FailTransport(LoopbackTransport):
    def __init__(self, fail_at: str):
        super().__init__()
        self.fail_at = fail_at

    def run(self, command: list[str], *, timeout_s: float | None = None) -> AdapterResult:
        if self.fail_at == "worker-run" and "--task" in command:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="ssh down during worker run",
            )
        return super().run(command, timeout_s=timeout_s)

    def put_file(
        self, source: str, destination: str, *, timeout_s: float | None = None
    ) -> AdapterResult:
        if self.fail_at == "ship-worker" and destination.endswith("node_worker.py"):
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="scp down during worker ship",
            )
        return super().put_file(source, destination, timeout_s=timeout_s)

    def collect(
        self, source: str, destination: str, *, timeout_s: float | None = None
    ) -> AdapterResult:
        if self.fail_at == "collect":
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="scp down during collect",
            )
        return super().collect(source, destination, timeout_s=timeout_s)


class MissingStatusTransport(LoopbackTransport):
    def run(self, command: list[str], *, timeout_s: float | None = None) -> AdapterResult:
        if "--task" in command:
            artifacts_dir = Path(command[command.index("--artifacts") + 1])
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            (artifacts_dir / "worker.log").write_text("ran without status\n", encoding="utf-8")
            return AdapterResult(ok=True, metadata={"returncode": 0, "stdout": ""})
        return super().run(command, timeout_s=timeout_s)


class NodeClientTests(unittest.TestCase):
    def make_client(
        self,
        transport: LoopbackTransport,
        clock: SequencedClock,
        remote_root: str,
    ) -> NodeWorkerClient:
        return NodeWorkerClient(
            transport,
            clock,
            run_id="run-loopback-001",
            remote_work_root=remote_root,
            remote_python=sys.executable,
        )

    def test_take_clock_marker_math_is_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            client = self.make_client(
                EchoTransport('{"node_time_s": 110.0, "monotonic_s": 5.0}\n'),
                SequencedClock([100.0, 100.4]),
                str(Path(tmp) / "remote"),
            )

            marker = client.take_clock_marker()

            self.assertIsInstance(marker, ClockMarker)
            assert isinstance(marker, ClockMarker)
            self.assertEqual(marker.controller_before_s, 100.0)
            self.assertEqual(marker.controller_after_s, 100.4)
            self.assertEqual(marker.node_time_s, 110.0)
            self.assertEqual(marker.node_monotonic_s, 5.0)
            self.assertAlmostEqual(marker.offset_estimate_s, 9.8)
            self.assertAlmostEqual(marker.rtt_bound_s, 0.2)

    def test_compute_stage_bound_includes_rtt_and_drift(self) -> None:
        pre = ClockMarker(0.0, 10.0, 1.0, 0.4, 9.8, 0.2)
        post = ClockMarker(2.0, 12.7, 3.0, 2.2, 10.6, 0.1)

        self.assertAlmostEqual(compute_stage_bound(pre, post), 1.0)

    def test_convert_node_timestamp_subtracts_offset(self) -> None:
        self.assertAlmostEqual(convert_node_timestamp(110.0, 9.8), 100.2)

    def test_run_task_loopback_collects_real_worker_unsupported_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            transport = LoopbackTransport()
            client = self.make_client(
                transport,
                SequencedClock([100.0, 100.2, 101.0, 101.2]),
                str(Path(tmp) / "remote"),
            )

            result = client.run_task(valid_telemetry_task(), timeout_s=10)

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "unsupported")
            self.assertEqual(result.failure_reason, FailureReason.UNSUPPORTED_WORKLOAD)
            self.assertIsNotNone(result.pre_marker)
            self.assertIsNotNone(result.post_marker)
            self.assertIsNotNone(result.offset_estimate_s)
            self.assertIsNotNone(result.offset_bound_s)
            self.assertIsNotNone(transport.clock_alignment)
            self.assertIsNotNone(result.artifacts_path)
            assert result.artifacts_path is not None
            self.assertTrue((result.artifacts_path / "status.json").exists())
            self.assertTrue((result.artifacts_path / "worker.log").exists())
            self.assertEqual(result.raw_status["artifacts"]["status_json"], "status.json")

    def test_run_task_transport_failures_are_structured(self) -> None:
        cases = [
            ("ship-worker", [100.0, 100.2, 101.0, 101.2]),
            ("worker-run", [100.0, 100.2]),
            ("collect", [100.0, 100.2, 101.0, 101.2]),
        ]
        for fail_at, clock_values in cases:
            with self.subTest(fail_at=fail_at):
                with tempfile.TemporaryDirectory() as tmp:
                    client = self.make_client(
                        FailTransport(fail_at),
                        SequencedClock(clock_values),
                        str(Path(tmp) / "remote"),
                    )

                    result = client.run_task(valid_telemetry_task(), timeout_s=10)

                    self.assertFalse(result.ok)
                    self.assertEqual(result.status, "failed")
                    self.assertEqual(result.failure_reason, FailureReason.TRANSPORT_UNAVAILABLE)
                    self.assertIn("down", result.message)

    def test_run_task_missing_status_json_is_unknown_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            client = self.make_client(
                MissingStatusTransport(),
                SequencedClock([100.0, 100.2, 101.0, 101.2]),
                str(Path(tmp) / "remote"),
            )

            result = client.run_task(valid_telemetry_task(), timeout_s=10)

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "failed")
            self.assertEqual(result.failure_reason, FailureReason.UNKNOWN_ERROR)
            self.assertIn("status.json", result.message)


if __name__ == "__main__":
    unittest.main()
