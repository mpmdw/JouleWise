"""Shared controller-side client for the JouleWise node worker.

This module implements the transport-independent side of the Slice 2K node
worker protocol. It follows D-002/D-003/D-009/D-012 and stream ledger
B-4/B-5/B-7/B-8: a single stdlib worker file is shipped to the node, every
transport problem becomes structured ``transport_unavailable``, worker status
comes from collected ``status.json``, and node timestamps are converted through
explicit clock markers.
"""

from __future__ import annotations

import json
import posixpath
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol

from joulewise.clock import Clock
from joulewise.interfaces import AdapterResult
from joulewise.schemas import FailureReason

PROTOCOL_VERSION = 1
DEFAULT_REMOTE_WORK_ROOT = "/tmp/joulewise"
DEFAULT_REMOTE_PYTHON = "python3"
WORKER_FILENAME = "node_worker.py"
STATUS_JSON = "status.json"
CLOCK_METHOD = "node_worker_clock_echo"
CLOCK_MARKER_TIMEOUT_S = 30.0
FILE_TRANSFER_TIMEOUT_S = 60.0


class NodeTransport(Protocol):
    def run(self, command: list[str], *, timeout_s: float | None = None) -> AdapterResult:
        """Run a command on the node."""

    def put_file(
        self, source: str, destination: str, *, timeout_s: float | None = None
    ) -> AdapterResult:
        """Copy a local file to the node."""

    def collect(
        self, source: str, destination: str, *, timeout_s: float | None = None
    ) -> AdapterResult:
        """Copy a node artifact path to the controller."""


@dataclass(frozen=True)
class ClockMarker:
    controller_before_s: float
    node_time_s: float
    node_monotonic_s: float
    controller_after_s: float
    offset_estimate_s: float
    rtt_bound_s: float


@dataclass(frozen=True)
class NodeTaskResult:
    ok: bool
    status: str
    failure_reason: FailureReason | None
    message: str
    artifacts_path: Path | None = None
    raw_status: dict[str, Any] | None = None
    pre_marker: ClockMarker | None = None
    post_marker: ClockMarker | None = None
    offset_estimate_s: float | None = None
    offset_bound_s: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def convert_node_timestamp(node_time_s: float, offset_estimate_s: float) -> float:
    """Convert a node epoch timestamp into the controller clock domain."""

    return node_time_s - offset_estimate_s


def compute_stage_bound(pre: ClockMarker, post: ClockMarker) -> float:
    return max(pre.rtt_bound_s, post.rtt_bound_s) + abs(
        post.offset_estimate_s - pre.offset_estimate_s
    )


class NodeWorkerClient:
    """Controller-side client for one remote worker shipment.

    Task JSON owns run identity. The shipped worker lives at the remote work
    root, while each task's ``run_id`` derives isolated task, artifact, and
    state directories under that root.
    """

    def __init__(
        self,
        transport: NodeTransport,
        clock: Clock,
        *,
        run_id: str | None = None,
        remote_work_root: str = DEFAULT_REMOTE_WORK_ROOT,
        remote_python: str = DEFAULT_REMOTE_PYTHON,
    ) -> None:
        self.transport = transport
        self.clock = clock
        self.run_id = run_id
        self.remote_work_root = remote_work_root.rstrip("/") or "/"
        self.remote_python = remote_python
        self.remote_worker_path = posixpath.join(self.remote_work_root, WORKER_FILENAME)
        self._worker_shipped = False

    def take_clock_marker(self) -> ClockMarker | AdapterResult:
        ship_result = self._ensure_worker_shipped()
        if not ship_result.ok:
            return ship_result

        before = self.clock.now()
        result = self.transport.run(
            [self.remote_python, self.remote_worker_path, "--clock-echo"],
            timeout_s=CLOCK_MARKER_TIMEOUT_S,
        )
        after = self.clock.now()
        if not result.ok:
            return self._transport_failure_from_result(result, "clock marker failed")

        try:
            payload = self._parse_clock_echo(result.metadata.get("stdout", ""))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="clock marker output was not parseable JSON: %s" % exc,
                metadata={"stdout": result.metadata.get("stdout", "")},
            )
        midpoint = (before + after) / 2.0
        node_time_s = float(payload["node_time_s"])
        return ClockMarker(
            controller_before_s=before,
            node_time_s=node_time_s,
            node_monotonic_s=float(payload["monotonic_s"]),
            controller_after_s=after,
            offset_estimate_s=node_time_s - midpoint,
            rtt_bound_s=(after - before) / 2.0,
        )

    def run_task(self, task: dict[str, Any], *, timeout_s: float) -> NodeTaskResult:
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip():
            return self._task_failure(
                FailureReason.UNKNOWN_ERROR,
                "task_id is required before dispatch",
            )
        run_id = task.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            return self._task_failure(
                FailureReason.UNKNOWN_ERROR,
                "run_id is required before dispatch",
            )

        ship_result = self._ensure_worker_shipped()
        if not ship_result.ok:
            return self._task_failure_from_adapter(ship_result, "ship worker failed")

        paths = self._remote_paths_for_run(run_id)
        dirs_result = self._ensure_run_dirs(paths)
        if not dirs_result.ok:
            return self._task_failure_from_adapter(dirs_result, "create remote run dirs failed")

        prepared_task = self._prepare_task_payload(task, run_id=run_id, paths=paths, timeout_s=timeout_s)
        remote_task_path = posixpath.join(paths["tasks_dir"], "%s.json" % task_id)
        remote_artifacts_path = posixpath.join(paths["artifacts_dir"], task_id)

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as tmp:
            json.dump(prepared_task, tmp, indent=2, sort_keys=True)
            tmp.write("\n")
            local_task_path = tmp.name
        try:
            put_result = self.transport.put_file(
                local_task_path,
                remote_task_path,
                timeout_s=FILE_TRANSFER_TIMEOUT_S,
            )
        finally:
            try:
                Path(local_task_path).unlink()
            except OSError:
                pass
        if not put_result.ok:
            return self._task_failure_from_adapter(put_result, "push task failed")

        pre = self.take_clock_marker()
        if isinstance(pre, AdapterResult):
            return self._task_failure_from_adapter(pre, "pre-task clock marker failed")

        run_result = self.transport.run(
            [
                self.remote_python,
                self.remote_worker_path,
                "--task",
                remote_task_path,
                "--artifacts",
                remote_artifacts_path,
            ],
            timeout_s=timeout_s,
        )
        if (
            not run_result.ok
            and run_result.failure_reason == FailureReason.TRANSPORT_UNAVAILABLE
        ):
            return self._task_failure_from_adapter(
                run_result,
                "worker command transport failed",
                pre_marker=pre,
            )

        post = self.take_clock_marker()
        if isinstance(post, AdapterResult):
            return self._task_failure_from_adapter(
                post,
                "post-task clock marker failed",
                pre_marker=pre,
            )

        alignment = self._alignment_record(pre, post)
        alignment["stage"] = self._stage_name(prepared_task)
        recorder = getattr(self.transport, "record_clock_alignment", None)
        if callable(recorder):
            recorder(alignment)

        local_parent = Path(tempfile.mkdtemp(prefix="joulewise-node-artifacts-"))
        local_artifacts_path = local_parent / task_id
        collect_result = self.transport.collect(
            remote_artifacts_path,
            str(local_artifacts_path),
            timeout_s=FILE_TRANSFER_TIMEOUT_S,
        )
        if not collect_result.ok:
            return self._task_failure_from_adapter(
                collect_result,
                "collect artifacts failed",
                pre_marker=pre,
                post_marker=post,
                alignment=alignment,
            )

        status_path = local_artifacts_path / STATUS_JSON
        try:
            raw_status = json.loads(status_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return self._task_failure(
                FailureReason.UNKNOWN_ERROR,
                "missing or malformed status.json: %s" % exc,
                artifacts_path=local_artifacts_path,
                pre_marker=pre,
                post_marker=post,
                alignment=alignment,
            )

        status = str(raw_status.get("status", "failed"))
        failure_reason = self._failure_reason(raw_status.get("failure_reason"))
        message = str(raw_status.get("message", ""))
        return NodeTaskResult(
            ok=status == "succeeded",
            status=status,
            failure_reason=failure_reason,
            message=message,
            artifacts_path=local_artifacts_path,
            raw_status=raw_status,
            pre_marker=pre,
            post_marker=post,
            offset_estimate_s=alignment["offset_estimate_s"],
            offset_bound_s=alignment["offset_bound_s"],
            metadata={
                "clock_alignment": alignment,
                "worker_returncode": run_result.metadata.get("returncode"),
            },
        )

    def _ensure_worker_shipped(self) -> AdapterResult:
        if self._worker_shipped:
            return AdapterResult(ok=True)
        mkdir_result = self.transport.run(
            [
                "mkdir",
                "-p",
                self.remote_work_root,
            ],
            timeout_s=FILE_TRANSFER_TIMEOUT_S,
        )
        if not mkdir_result.ok:
            return self._transport_failure_from_result(mkdir_result, "create remote work dir failed")

        worker_path = Path(__file__).with_name(WORKER_FILENAME)
        put_result = self.transport.put_file(
            str(worker_path),
            self.remote_worker_path,
            timeout_s=FILE_TRANSFER_TIMEOUT_S,
        )
        if not put_result.ok:
            return self._transport_failure_from_result(put_result, "ship worker failed")
        self._worker_shipped = True
        return AdapterResult(ok=True)

    def _ensure_run_dirs(self, paths: dict[str, str]) -> AdapterResult:
        mkdir_result = self.transport.run(
            [
                "mkdir",
                "-p",
                paths["run_dir"],
                paths["tasks_dir"],
                paths["artifacts_dir"],
                paths["state_dir"],
            ],
            timeout_s=FILE_TRANSFER_TIMEOUT_S,
        )
        if not mkdir_result.ok:
            return self._transport_failure_from_result(mkdir_result, "create remote run dirs failed")
        return AdapterResult(ok=True)

    def _remote_paths_for_run(self, run_id: str) -> dict[str, str]:
        run_dir = posixpath.join(self.remote_work_root, run_id)
        return {
            "run_dir": run_dir,
            "tasks_dir": posixpath.join(run_dir, "tasks"),
            "artifacts_dir": posixpath.join(run_dir, "artifacts"),
            "state_dir": posixpath.join(run_dir, "state"),
        }

    def _prepare_task_payload(
        self,
        task: dict[str, Any],
        *,
        run_id: str,
        paths: dict[str, str],
        timeout_s: float,
    ) -> dict[str, Any]:
        payload = dict(task)
        payload.setdefault("protocol_version", PROTOCOL_VERSION)
        payload["run_id"] = run_id
        payload["timeout_s"] = float(timeout_s)
        task_paths = dict(payload.get("paths") or {})
        task_paths["state_dir"] = paths["state_dir"]
        payload["paths"] = task_paths
        return payload

    def _parse_clock_echo(self, stdout: Any) -> dict[str, Any]:
        if not isinstance(stdout, str):
            raise TypeError("stdout metadata must be a string")
        line = stdout.strip().splitlines()[-1]
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError("clock marker payload must be an object")
        if "node_time_s" not in payload or "monotonic_s" not in payload:
            raise KeyError("node_time_s and monotonic_s are required")
        return payload

    def _alignment_record(self, pre: ClockMarker, post: ClockMarker) -> dict[str, Any]:
        offset_estimate_s = (pre.offset_estimate_s + post.offset_estimate_s) / 2.0
        return {
            "method": CLOCK_METHOD,
            "pre": asdict(pre),
            "post": asdict(post),
            "offset_estimate_s": offset_estimate_s,
            "offset_bound_s": compute_stage_bound(pre, post),
        }

    def _stage_name(self, task: dict[str, Any]) -> str:
        task_type = str(task.get("task_type", "task"))
        operation = str(task.get("operation", "unknown"))
        return "%s.%s" % (task_type, operation)

    def _transport_failure_from_result(self, result: AdapterResult, fallback: str) -> AdapterResult:
        return AdapterResult(
            ok=False,
            failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
            message=result.message or fallback,
            metadata=dict(result.metadata),
        )

    def _task_failure_from_adapter(
        self,
        result: AdapterResult,
        fallback: str,
        *,
        pre_marker: ClockMarker | None = None,
        post_marker: ClockMarker | None = None,
        alignment: dict[str, Any] | None = None,
    ) -> NodeTaskResult:
        reason = result.failure_reason or FailureReason.TRANSPORT_UNAVAILABLE
        if reason != FailureReason.TRANSPORT_UNAVAILABLE:
            reason = FailureReason.TRANSPORT_UNAVAILABLE
        return self._task_failure(
            reason,
            result.message or fallback,
            pre_marker=pre_marker,
            post_marker=post_marker,
            alignment=alignment,
            metadata=dict(result.metadata),
        )

    def _task_failure(
        self,
        reason: FailureReason,
        message: str,
        *,
        artifacts_path: Path | None = None,
        pre_marker: ClockMarker | None = None,
        post_marker: ClockMarker | None = None,
        alignment: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> NodeTaskResult:
        payload_metadata = dict(metadata or {})
        if alignment is not None:
            payload_metadata["clock_alignment"] = alignment
        return NodeTaskResult(
            ok=False,
            status="failed",
            failure_reason=reason,
            message=message,
            artifacts_path=artifacts_path,
            pre_marker=pre_marker,
            post_marker=post_marker,
            offset_estimate_s=alignment.get("offset_estimate_s") if alignment else None,
            offset_bound_s=alignment.get("offset_bound_s") if alignment else None,
            metadata=payload_metadata,
        )

    def _failure_reason(self, value: Any) -> FailureReason | None:
        if value is None:
            return None
        try:
            return FailureReason(value)
        except ValueError:
            return FailureReason.UNKNOWN_ERROR
