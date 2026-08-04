"""CI-safe tests for the shared Slice 2K node-worker client."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from joulewise.adapters.node_client import (
    ClockMarker,
    NodeWorkerClient,
    compute_stage_bound,
    convert_node_timestamp,
)
from joulewise.interfaces import AdapterResult, acknowledge_durable_custody
from joulewise.schemas import FailureReason

REMOVE_STATUS_FIELD = object()


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
        "operation": "bogus_operation",
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
        self.put_destinations: list[str] = []
        self.collect_sources: list[str] = []

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
        self.put_destinations.append(destination)
        return AdapterResult(ok=True, metadata={"source": source, "destination": destination})

    def collect(
        self, source: str, destination: str, *, timeout_s: float | None = None
    ) -> AdapterResult:
        shutil.copytree(source, destination)
        self.collect_sources.append(source)
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
                metadata={"execution_state": "not_started"},
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


class SuccessfulWorkerTransport(LoopbackTransport):
    def __init__(self) -> None:
        super().__init__()
        self.correlation_tokens: list[str] = []

    def run(
        self,
        command: list[str],
        *,
        timeout_s: float | None = None,
    ) -> AdapterResult:
        if "--task" in command:
            task_path = Path(command[command.index("--task") + 1])
            artifacts_dir = Path(command[command.index("--artifacts") + 1])
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            task = json.loads(task_path.read_text(encoding="utf-8"))
            self.correlation_tokens.append(task["correlation_token"])
            (artifacts_dir / "worker.log").write_text("succeeded\n", encoding="utf-8")
            (artifacts_dir / "status.json").write_text(
                json.dumps(
                    {
                        "protocol_version": 1,
                        "correlation_token": task["correlation_token"],
                        "task_id": task["task_id"],
                        "run_id": task["run_id"],
                        "task_type": task["task_type"],
                        "operation": task["operation"],
                        "node_role": task["node_role"],
                        "status": "succeeded",
                        "failure_reason": None,
                        "message": "",
                        "artifacts": {
                            "status_json": "status.json",
                            "worker_log": "worker.log",
                        },
                        "metadata": {},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            return AdapterResult(ok=True, metadata={"returncode": 0, "stdout": ""})
        return super().run(command, timeout_s=timeout_s)


class MutatingStatusTransport(SuccessfulWorkerTransport):
    def __init__(self, field: str, value: Any) -> None:
        super().__init__()
        self.field = field
        self.value = value

    def run(self, command: list[str], *, timeout_s: float | None = None) -> AdapterResult:
        result = super().run(command, timeout_s=timeout_s)
        if "--task" in command:
            artifacts_dir = Path(command[command.index("--artifacts") + 1])
            status_path = artifacts_dir / "status.json"
            payload = json.loads(status_path.read_text(encoding="utf-8"))
            if self.value is REMOVE_STATUS_FIELD:
                payload.pop(self.field, None)
            else:
                payload[self.field] = self.value
            status_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        return result


class NonzeroPhraseWorkerTransport(SuccessfulWorkerTransport):
    def run(self, command: list[str], *, timeout_s: float | None = None) -> AdapterResult:
        result = super().run(command, timeout_s=timeout_s)
        if "--task" in command:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.UNKNOWN_ERROR,
                message="application reported connection refused",
                metadata={
                    "returncode": 3,
                    "stderr_tail": "application reported connection refused",
                    "execution_state": "completed",
                },
            )
        return result


class InterruptAfterDispatchTransport(SuccessfulWorkerTransport):
    """Starts the worker and writes evidence, then loses the caller to Ctrl-C."""

    def __init__(self) -> None:
        super().__init__()
        self.interrupt_worker_once = True

    def run(self, command: list[str], *, timeout_s: float | None = None) -> AdapterResult:
        result = super().run(command, timeout_s=timeout_s)
        if self.interrupt_worker_once and "--task" in command:
            self.interrupt_worker_once = False
            raise KeyboardInterrupt("interrupted after remote dispatch")
        return result


class RecoverableWorkerTransport(LoopbackTransport):
    """Leaves real remote evidence once, then permits a later-session sweep."""

    def __init__(self) -> None:
        super().__init__()
        self.fail_worker_once = True
        self.fail_orphan_collect_once = True

    def run(self, command: list[str], *, timeout_s: float | None = None) -> AdapterResult:
        if self.fail_worker_once and "--task" in command:
            self.fail_worker_once = False
            task_path = Path(command[command.index("--task") + 1])
            task = json.loads(task_path.read_text(encoding="utf-8"))
            artifacts_dir = Path(command[command.index("--artifacts") + 1])
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            (artifacts_dir / "worker.log").write_text(
                "worker completed while transport disappeared\n",
                encoding="utf-8",
            )
            (artifacts_dir / "status.json").write_text(
                json.dumps(
                    {
                        "protocol_version": 1,
                        "correlation_token": task["correlation_token"],
                        "task_id": task["task_id"],
                        "run_id": task["run_id"],
                        "task_type": task["task_type"],
                        "operation": task["operation"],
                        "node_role": task["node_role"],
                        "status": "failed",
                        "failure_reason": "unknown_error",
                        "message": "orphaned result",
                        "artifacts": {"worker_log": "worker.log"},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="connection lost after worker wrote evidence",
                metadata={"returncode": 255, "execution_state": "ambiguous"},
            )
        return super().run(command, timeout_s=timeout_s)

    def collect(
        self, source: str, destination: str, *, timeout_s: float | None = None
    ) -> AdapterResult:
        if self.fail_orphan_collect_once and source.endswith("task-orphaned"):
            self.fail_orphan_collect_once = False
            destination_path = Path(destination)
            destination_path.mkdir(parents=True, exist_ok=True)
            shutil.copy2(Path(source) / "worker.log", destination_path / "worker.log")
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="connection lost during partial reclamation collect",
            )
        return super().collect(source, destination, timeout_s=timeout_s)


class TwiceFailingRecollectionTransport(RecoverableWorkerTransport):
    """First retry leaves evidence; second retry fails before copying bytes."""

    def __init__(self) -> None:
        super().__init__()
        self.recollection_attempts = 0

    def collect(
        self, source: str, destination: str, *, timeout_s: float | None = None
    ) -> AdapterResult:
        if self.fail_orphan_collect_once and source.endswith("task-orphaned"):
            self.fail_orphan_collect_once = False
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="connection lost during initial recovery collect",
            )
        if source.endswith("task-orphaned") and self.recollection_attempts < 2:
            self.recollection_attempts += 1
            if self.recollection_attempts == 1:
                destination_path = Path(destination)
                destination_path.mkdir(parents=True, exist_ok=True)
                shutil.copy2(Path(source) / "worker.log", destination_path / "worker.log")
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="connection lost during repeated partial recollection",
            )
        return LoopbackTransport.collect(self, source, destination, timeout_s=timeout_s)


class PersistentlyFailingPartialCollectTransport(LoopbackTransport):
    """Every collection attempt leaves a distinct evidence-bearing partial."""

    def __init__(self) -> None:
        super().__init__()
        self.collect_attempts = 0

    def collect(
        self, source: str, destination: str, *, timeout_s: float | None = None
    ) -> AdapterResult:
        self.collect_attempts += 1
        destination_path = Path(destination)
        destination_path.mkdir(parents=True, exist_ok=True)
        destination_path.joinpath("worker.log").write_text(
            "partial collection %d\n" % self.collect_attempts,
            encoding="utf-8",
        )
        return AdapterResult(
            ok=False,
            failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
            message="persistent partial collection failure",
        )


class ManifestAppendingSweepClient(NodeWorkerClient):
    """Minimal sweep simulation used to force an interleaved manifest write."""

    def __init__(
        self,
        *args,
        token: str,
        entered: threading.Event,
        release: threading.Event,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.token = token
        self.entered = entered
        self.release = release

    def _sweep_retained_artifacts_locked(self) -> None:
        records = self._load_retention_records()
        self.entered.set()
        if not self.release.wait(timeout=5):
            raise AssertionError("timed out waiting to complete sweep simulation")
        records.append({"token": self.token})
        self._write_retention_records(records)


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
            retention_root=Path(remote_root).parent / "retention",
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
            self.assertTrue(result.artifacts_path.is_dir())
            self.assertIn("status.json", result.artifacts)
            self.assertIn("worker.log", result.artifacts)
            self.assertEqual(result.raw_status["artifacts"]["status_json"], "status.json")
            cleanup = client.cleanup_report()
            self.assertTrue(cleanup)
            self.assertTrue(all(not row["removed"] for row in cleanup), cleanup)
            self.assertTrue(all(row["deferred_for_custody"] for row in cleanup))
            self.assertTrue(client.retention_manifest_path.is_file())

            assert result.custody_token is not None
            acknowledgement = acknowledge_durable_custody(
                result.artifacts_path.parents[1],
                result.custody_token,
                [result.artifacts_path],
            )
            released = client.acknowledge_custody(acknowledgement)

            self.assertTrue(released)
            self.assertTrue(all(row["removed"] for row in released), released)
            self.assertTrue(result.artifacts_path.is_dir())

    def test_successful_standalone_collection_deletes_cleanup_run_inline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            client = self.make_client(
                SuccessfulWorkerTransport(),
                SequencedClock(
                    [100.0, 100.2, 101.0, 101.2, 102.0, 102.2, 103.0, 103.2]
                ),
                str(root / "remote"),
            )

            first = client.run_task(valid_telemetry_task(), timeout_s=10)
            result = client.run_task(
                {
                    "protocol_version": 1,
                    "task_id": "task-runtime-cleanup",
                    "run_id": "run-loopback-001",
                    "task_type": "runtime",
                    "operation": "cleanup",
                    "node_role": None,
                    "runtime": {},
                },
                timeout_s=10,
            )

            self.assertTrue(first.ok, first)
            self.assertTrue(result.ok, result)
            self.assertEqual(
                result.metadata["custody"]["state"],
                "released_after_durable_acknowledgement",
            )
            self.assertFalse((root / "remote" / "run-loopback-001").exists())
            self.assertTrue(client.cleanup_report())
            self.assertTrue(
                all(row["removed"] for row in client.cleanup_report()),
                client.cleanup_report(),
            )
            manifest = json.loads(client.retention_manifest_path.read_text())
            self.assertEqual(manifest["records"], [])
            assert result.custody_token is not None
            acknowledgement = (
                result.artifacts_path.parents[1]
                / "logs"
                / "custody"
                / (result.custody_token + ".json")
            )
            self.assertTrue(acknowledgement.is_file())

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

    def test_transport_unavailable_retention_is_reclaimed_next_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote_root = str(root / "remote")
            retention_root = root / "retention"
            transport = RecoverableWorkerTransport()
            first = NodeWorkerClient(
                transport,
                SequencedClock([100.0, 100.2, 101.0, 101.2]),
                remote_work_root=remote_root,
                remote_python=sys.executable,
                retention_root=retention_root,
            )
            orphaned_task = valid_telemetry_task("task-orphaned")

            orphaned = first.run_task(orphaned_task, timeout_s=10)

            self.assertEqual(
                orphaned.failure_reason,
                FailureReason.TRANSPORT_UNAVAILABLE,
            )
            assert orphaned.custody_token is not None
            manifest = json.loads(first.retention_manifest_path.read_text())
            self.assertEqual(
                [record["token"] for record in manifest["records"]],
                [orphaned.custody_token],
            )
            remote_orphan = root / "remote" / "run-loopback-001" / "artifacts" / "task-orphaned"
            self.assertTrue(remote_orphan.is_dir())

            transport.fail_orphan_collect_once = True
            second = NodeWorkerClient(
                transport,
                SequencedClock([101.0, 101.2, 102.0, 102.2]),
                remote_work_root=remote_root,
                remote_python=sys.executable,
                retention_root=retention_root,
            )
            current = second.run_task(
                valid_telemetry_task("task-current"),
                timeout_s=10,
            )

            self.assertTrue(remote_orphan.is_dir())
            manifest = json.loads(second.retention_manifest_path.read_text())
            orphan_record = next(
                record
                for record in manifest["records"]
                if record["token"] == orphaned.custody_token
            )
            self.assertFalse(orphan_record["collection_complete"])

            third = NodeWorkerClient(
                transport,
                SequencedClock([103.0, 103.2, 104.0, 104.2]),
                remote_work_root=remote_root,
                remote_python=sys.executable,
                retention_root=retention_root,
            )
            latest = third.run_task(
                valid_telemetry_task("task-latest"),
                timeout_s=10,
            )

            self.assertFalse(remote_orphan.exists())
            manifest = json.loads(third.retention_manifest_path.read_text())
            self.assertNotIn(
                orphaned.custody_token,
                [record["token"] for record in manifest["records"]],
            )
            self.assertNotIn(
                current.custody_token,
                [record["token"] for record in manifest["records"]],
            )
            self.assertIn(
                latest.custody_token,
                [record["token"] for record in manifest["records"]],
            )
            acknowledgement = (
                retention_root
                / "standalone"
                / orphaned.custody_token
                / "logs"
                / "custody"
                / (orphaned.custody_token + ".json")
            )
            self.assertTrue(acknowledgement.is_file())
            reclaimed = [
                row
                for row in third.cleanup_report()
                if row.get("custody_token") == orphaned.custody_token
                and row.get("after_durable_custody") is True
            ]
            self.assertTrue(reclaimed)
            self.assertTrue(all(row["removed"] for row in reclaimed))

    def test_interrupt_after_dispatch_cannot_create_dispatch_only_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote_root = str(root / "remote")
            retention_root = root / "retention"
            transport = InterruptAfterDispatchTransport()
            first = NodeWorkerClient(
                transport,
                SequencedClock([100.0, 100.2]),
                remote_work_root=remote_root,
                remote_python=sys.executable,
                retention_root=retention_root,
            )

            with self.assertRaisesRegex(
                KeyboardInterrupt, "interrupted after remote dispatch"
            ):
                first.run_task(
                    valid_telemetry_task("task-interrupted"), timeout_s=10
                )

            manifest = json.loads(first.retention_manifest_path.read_text())
            self.assertEqual(len(manifest["records"]), 1)
            interrupted = manifest["records"][0]
            self.assertIs(interrupted["worker_may_have_run"], True)
            self.assertIs(interrupted["collection_complete"], False)
            remote_artifacts = (
                root
                / "remote"
                / "run-loopback-001"
                / "artifacts"
                / "task-interrupted"
            )
            self.assertTrue(remote_artifacts.is_dir())

            second = NodeWorkerClient(
                transport,
                SequencedClock([101.0, 101.2, 102.0, 102.2]),
                remote_work_root=remote_root,
                remote_python=sys.executable,
                retention_root=retention_root,
            )
            current = second.run_task(
                valid_telemetry_task("task-current"), timeout_s=10
            )

            self.assertTrue(current.ok, current)
            self.assertFalse(remote_artifacts.exists())
            manifest = json.loads(second.retention_manifest_path.read_text())
            self.assertNotIn(
                interrupted["token"],
                [record["token"] for record in manifest["records"]],
            )
            acknowledgement = (
                retention_root
                / "standalone"
                / interrupted["token"]
                / "logs"
                / "custody"
                / (interrupted["token"] + ".json")
            )
            self.assertTrue(acknowledgement.is_file())
            self.assertFalse(
                (
                    retention_root
                    / "standalone"
                    / interrupted["token"]
                    / "raw"
                    / "node-custody"
                    / "dispatch-retention.json"
                ).exists()
            )

    def test_interleaved_sweeps_cannot_lose_a_manifest_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            retention_root = Path(tmp) / "retention"
            first_entered = threading.Event()
            second_entered = threading.Event()
            first_release = threading.Event()
            second_release = threading.Event()
            second_release.set()
            clients = [
                ManifestAppendingSweepClient(
                    LoopbackTransport(),
                    SequencedClock([]),
                    remote_work_root=str(Path(tmp) / "remote"),
                    retention_root=retention_root,
                    token="first",
                    entered=first_entered,
                    release=first_release,
                ),
                ManifestAppendingSweepClient(
                    LoopbackTransport(),
                    SequencedClock([]),
                    remote_work_root=str(Path(tmp) / "remote"),
                    retention_root=retention_root,
                    token="second",
                    entered=second_entered,
                    release=second_release,
                ),
            ]
            threads = [
                threading.Thread(target=client._sweep_retained_artifacts)
                for client in clients
            ]

            threads[0].start()
            self.assertTrue(first_entered.wait(timeout=5))
            threads[1].start()
            self.assertFalse(second_entered.wait(timeout=0.1))
            first_release.set()
            for thread in threads:
                thread.join(timeout=5)
                self.assertFalse(thread.is_alive())

            records = json.loads(clients[0].retention_manifest_path.read_text())[
                "records"
            ]
            self.assertEqual(
                [record["token"] for record in records],
                ["first", "second"],
            )

    def test_sweep_skips_when_retention_lock_acquisition_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            client = self.make_client(
                LoopbackTransport(),
                SequencedClock([]),
                str(Path(tmp) / "remote"),
            )
            with (
                patch(
                    "joulewise.adapters.node_client.fcntl.flock",
                    side_effect=OSError("injected lock failure"),
                ),
                patch.object(
                    client,
                    "_sweep_retained_artifacts_locked",
                ) as unlocked_sweep,
            ):
                swept = client._sweep_retained_artifacts()

            self.assertFalse(swept)
            unlocked_sweep.assert_not_called()

    def test_second_recollection_failure_preserves_first_partial_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote_root = str(root / "remote")
            retention_root = root / "retention"
            transport = TwiceFailingRecollectionTransport()
            first = NodeWorkerClient(
                transport,
                SequencedClock([100.0, 100.2, 101.0, 101.2]),
                remote_work_root=remote_root,
                remote_python=sys.executable,
                retention_root=retention_root,
            )
            orphaned = first.run_task(
                valid_telemetry_task("task-orphaned"),
                timeout_s=10,
            )
            assert orphaned.custody_token is not None

            second = NodeWorkerClient(
                transport,
                SequencedClock([]),
                remote_work_root=remote_root,
                remote_python=sys.executable,
                retention_root=retention_root,
            )
            second._sweep_retained_artifacts()
            manifest = json.loads(second.retention_manifest_path.read_text())
            record = next(
                item
                for item in manifest["records"]
                if item["token"] == orphaned.custody_token
            )
            first_partial = Path(record["partial_custody_paths"][-1])
            self.assertEqual(
                first_partial.joinpath("worker.log").read_text(),
                "worker completed while transport disappeared\n",
            )

            third = NodeWorkerClient(
                transport,
                SequencedClock([]),
                remote_work_root=remote_root,
                remote_python=sys.executable,
                retention_root=retention_root,
            )
            third._sweep_retained_artifacts()

            self.assertEqual(
                first_partial.joinpath("worker.log").read_text(),
                "worker completed while transport disappeared\n",
            )
            manifest = json.loads(third.retention_manifest_path.read_text())
            record = next(
                item
                for item in manifest["records"]
                if item["token"] == orphaned.custody_token
            )
            self.assertEqual(record["partial_custody_paths"], [str(first_partial)])
            self.assertFalse(record["collection_complete"])

            fourth = NodeWorkerClient(
                transport,
                SequencedClock([]),
                remote_work_root=remote_root,
                remote_python=sys.executable,
                retention_root=retention_root,
            )
            fourth._sweep_retained_artifacts()

            self.assertFalse(first_partial.exists())
            manifest = json.loads(fourth.retention_manifest_path.read_text())
            self.assertNotIn(
                orphaned.custody_token,
                [item["token"] for item in manifest["records"]],
            )

    def test_failed_recollections_keep_original_and_newest_two_partials(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote_root = str(root / "remote")
            retention_root = root / "retention"
            transport = PersistentlyFailingPartialCollectTransport()
            first = NodeWorkerClient(
                transport,
                SequencedClock([100.0, 100.2, 101.0, 101.2]),
                remote_work_root=remote_root,
                remote_python=sys.executable,
                retention_root=retention_root,
            )
            result = first.run_task(
                valid_telemetry_task("task-persistent-partials"),
                timeout_s=10,
            )
            assert result.custody_token is not None
            records = json.loads(first.retention_manifest_path.read_text())["records"]
            record = next(
                item for item in records if item["token"] == result.custody_token
            )
            original_path = Path(record["custody_path"])
            self.assertTrue(original_path.joinpath("worker.log").is_file())

            for _ in range(5):
                client = NodeWorkerClient(
                    transport,
                    SequencedClock([]),
                    remote_work_root=remote_root,
                    remote_python=sys.executable,
                    retention_root=retention_root,
                )
                client._sweep_retained_artifacts()

            manifest = json.loads(first.retention_manifest_path.read_text())
            record = next(
                item
                for item in manifest["records"]
                if item["token"] == result.custody_token
            )
            retained = [Path(value) for value in record["partial_custody_paths"]]
            self.assertEqual(len(retained), 3)
            self.assertEqual(retained[0], original_path)
            self.assertEqual(
                [path.joinpath("worker.log").read_text() for path in retained],
                [
                    "partial collection 1\n",
                    "partial collection 5\n",
                    "partial collection 6\n",
                ],
            )
            self.assertEqual(
                len(
                    list(
                        original_path.parent.glob(
                            original_path.name + ".recollect-*"
                        )
                    )
                ),
                2,
            )

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

    def test_unsafe_run_and_task_ids_are_rejected_before_shipping(self) -> None:
        unsafe_values = ["/absolute", "../traversal", ".", "nested/component"]
        for field in ("run_id", "task_id"):
            for value in unsafe_values:
                with self.subTest(field=field, value=value):
                    with tempfile.TemporaryDirectory() as tmp:
                        transport = LoopbackTransport()
                        client = self.make_client(
                            transport,
                            SequencedClock([]),
                            str(Path(tmp) / "remote"),
                        )
                        task = valid_telemetry_task()
                        task[field] = value

                        result = client.run_task(task, timeout_s=10)

                        self.assertFalse(result.ok)
                        self.assertIn("safe single path component", result.message)
                        self.assertEqual(transport.put_destinations, [])
                        self.assertFalse((Path(tmp) / "remote").exists())

    def test_matching_stale_response_with_wrong_correlation_token_is_retained(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            client = self.make_client(
                MutatingStatusTransport(
                    "correlation_token", "f" * 32
                ),
                SequencedClock([100.0, 100.2, 101.0, 101.2]),
                str(root / "remote"),
            )

            result = client.run_task(valid_telemetry_task(), timeout_s=10)

            self.assertFalse(result.ok)
            self.assertIn("correlation_token", result.message)
            self.assertFalse(result.metadata["response_identity_validated"])
            self.assertTrue(Path(result.metadata["retained_evidence_path"]).is_dir())
            self.assertTrue((root / "remote" / "run-loopback-001").is_dir())
            self.assertTrue(client.cleanup_report())
            self.assertTrue(all(not row["removed"] for row in client.cleanup_report()))

    def test_other_response_identity_collisions_are_rejected(self) -> None:
        cases = [
            ("protocol_version", 2, "future-version"),
            ("protocol_version", True, "boolean-version"),
            ("run_id", "run-collided", "run-id"),
            ("task_id", "task-collided", "task-id"),
            ("task_type", "runtime", "task-type"),
            ("operation", "cleanup", "operation"),
            ("node_role", "decode", "node-role"),
            ("node_role", REMOVE_STATUS_FIELD, "missing-null-node-role"),
        ]
        for field, value, name in cases:
            with self.subTest(field=field, name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    client = self.make_client(
                        MutatingStatusTransport(field, value),
                        SequencedClock([100.0, 100.2, 101.0, 101.2]),
                        str(Path(tmp) / "remote"),
                    )

                    result = client.run_task(valid_telemetry_task(), timeout_s=10)

                    self.assertFalse(result.ok)
                    self.assertIn(field, result.message)
                    self.assertTrue(all(not row["removed"] for row in client.cleanup_report()))

    def test_nonzero_connection_refused_worker_exit_still_recovers_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            transport = NonzeroPhraseWorkerTransport()
            client = self.make_client(
                transport,
                SequencedClock([100.0, 100.2, 101.0, 101.2]),
                str(Path(tmp) / "remote"),
            )

            result = client.run_task(valid_telemetry_task(), timeout_s=10)

            self.assertTrue(result.ok, result)
            self.assertEqual(result.metadata["worker_returncode"], 3)
            self.assertEqual(result.metadata["worker_execution_state"], "completed")
            self.assertTrue(transport.collect_sources)
            self.assertEqual(result.metadata["node_worker_protocol_version"], 1)

    def test_repeated_task_identity_gets_a_unique_correlation_token_per_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            transport = SuccessfulWorkerTransport()
            client = self.make_client(
                transport,
                SequencedClock(
                    [100.0, 100.2, 101.0, 101.2, 102.0, 102.2, 103.0, 103.2]
                ),
                str(Path(tmp) / "remote"),
            )
            task = valid_telemetry_task()

            first = client.run_task(task, timeout_s=10)
            second = client.run_task(task, timeout_s=10)

            self.assertTrue(first.ok, first)
            self.assertTrue(second.ok, second)
            self.assertEqual(len(transport.correlation_tokens), 2)
            self.assertNotEqual(
                transport.correlation_tokens[0], transport.correlation_tokens[1]
            )
            self.assertTrue(
                all(len(token) == 32 for token in transport.correlation_tokens)
            )

    def test_run_task_uses_each_task_run_id_for_remote_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            transport = LoopbackTransport()
            client = self.make_client(
                transport,
                SequencedClock([100.0, 100.2, 101.0, 101.2, 102.0, 102.2, 103.0, 103.2]),
                str(Path(tmp) / "remote"),
            )
            task_one = valid_telemetry_task(task_id="task-one")
            task_one["run_id"] = "run-one"
            task_two = valid_telemetry_task(task_id="task-two")
            task_two["run_id"] = "run-two"

            result_one = client.run_task(task_one, timeout_s=10)
            result_two = client.run_task(task_two, timeout_s=10)

            self.assertFalse(result_one.ok)
            self.assertFalse(result_two.ok)
            task_puts = [path for path in transport.put_destinations if path.endswith(".json")]
            self.assertTrue(any("/run-one/tasks/task-one.json" in path for path in task_puts), task_puts)
            self.assertTrue(any("/run-two/tasks/task-two.json" in path for path in task_puts), task_puts)
            self.assertTrue(
                any("/run-one/artifacts/task-one" in path for path in transport.collect_sources),
                transport.collect_sources,
            )
            self.assertTrue(
                any("/run-two/artifacts/task-two" in path for path in transport.collect_sources),
                transport.collect_sources,
            )
            self.assertTrue((Path(tmp) / "remote" / "node_worker.py").exists())
            self.assertTrue((Path(tmp) / "remote" / "run-one" / "state").is_dir())
            self.assertTrue((Path(tmp) / "remote" / "run-two" / "state").is_dir())

    def test_run_task_without_task_run_id_fails_before_shipping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            transport = LoopbackTransport()
            client = NodeWorkerClient(
                transport,
                SequencedClock([]),
                remote_work_root=str(Path(tmp) / "remote"),
                remote_python=sys.executable,
                retention_root=Path(tmp) / "retention",
            )
            task = valid_telemetry_task()
            del task["run_id"]

            result = client.run_task(task, timeout_s=10)

            self.assertFalse(result.ok)
            self.assertEqual(result.failure_reason, FailureReason.UNKNOWN_ERROR)
            self.assertIn("run_id is required", result.message)
            self.assertEqual(transport.put_destinations, [])


if __name__ == "__main__":
    unittest.main()
