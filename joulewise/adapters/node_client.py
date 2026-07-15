"""Shared controller-side client for the JouleWise node worker.

This module implements the transport-independent side of the Slice 2K node
worker protocol. It follows D-002/D-003/D-009/D-012 and stream ledger
B-4/B-5/B-7/B-8: a single stdlib worker file is shipped to the node, every
transport problem becomes structured ``transport_unavailable``, worker status
comes from collected ``status.json``, and node timestamps are converted through
explicit clock markers.
"""

from __future__ import annotations

import fcntl
import json
import os
import posixpath
import re
import shutil
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator, Protocol

from joulewise.clock import Clock
from joulewise.interfaces import (
    AdapterResult,
    DurableCustodyAcknowledgement,
    RunContext,
    acknowledge_durable_custody,
)
from joulewise.schemas import FailureReason

PROTOCOL_VERSION = 1
SAFE_IDENTIFIER_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
DEFAULT_REMOTE_WORK_ROOT = "/tmp/joulewise"
DEFAULT_REMOTE_PYTHON = "python3"
WORKER_FILENAME = "node_worker.py"
STATUS_JSON = "status.json"
CLOCK_METHOD = "node_worker_clock_echo"
CLOCK_MARKER_TIMEOUT_S = 30.0
FILE_TRANSFER_TIMEOUT_S = 60.0
RETENTION_MANIFEST_VERSION = 1
MAX_RETAINED_FAILED_PARTIALS = 2
DEFAULT_RETENTION_ROOT = Path(tempfile.gettempdir()) / "joulewise-node-custody"


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
    artifacts: dict[str, bytes] = field(default_factory=dict)
    raw_status: dict[str, Any] | None = None
    pre_marker: ClockMarker | None = None
    post_marker: ClockMarker | None = None
    offset_estimate_s: float | None = None
    offset_bound_s: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    custody_token: str | None = None


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
        retention_root: Path | None = None,
    ) -> None:
        self.transport = transport
        self.clock = clock
        self.run_id = run_id
        if not isinstance(remote_work_root, str) or not posixpath.isabs(remote_work_root):
            raise ValueError("remote_work_root must be an absolute POSIX path")
        self.remote_work_root = posixpath.normpath(remote_work_root)
        self.remote_python = remote_python
        self.remote_worker_path = self._contained_remote_path(WORKER_FILENAME)
        self.retention_root = Path(retention_root or DEFAULT_RETENTION_ROOT)
        self.retention_manifest_path = self.retention_root / "retention-manifest.json"
        self.retention_lock_path = self.retention_manifest_path.with_name(
            self.retention_manifest_path.name + ".lock"
        )
        self._worker_shipped = False
        self._retention_swept = False
        self._cleanup_report: list[dict[str, Any]] = []

    def cleanup_report(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._cleanup_report]

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

    def run_task(
        self,
        task: dict[str, Any],
        *,
        timeout_s: float,
        context: RunContext | None = None,
    ) -> NodeTaskResult:
        try:
            task_id, run_id = self._validate_dispatch_task(task)
        except ValueError as exc:
            return self._task_failure(
                FailureReason.UNKNOWN_ERROR,
                str(exc),
            )

        ship_result = self._ensure_worker_shipped()
        if not ship_result.ok:
            return self._task_failure_from_adapter(ship_result, "ship worker failed")
        if not self._retention_swept:
            self._retention_swept = self._sweep_retained_artifacts()

        paths = self._remote_paths_for_run(run_id)
        dirs_result = self._ensure_run_dirs(paths)
        if not dirs_result.ok:
            return self._task_failure_from_adapter(dirs_result, "create remote run dirs failed")

        custody_token = uuid.uuid4().hex
        prepared_task = self._prepare_task_payload(
            task,
            run_id=run_id,
            paths=paths,
            timeout_s=timeout_s,
            correlation_token=custody_token,
        )
        remote_task_path = self._contained_remote_path(
            run_id,
            "tasks",
            "%s.json" % task_id,
        )
        remote_artifacts_path = self._contained_remote_path(
            run_id,
            "artifacts",
            task_id,
        )
        retention = self._new_retention_record(
            token=custody_token,
            task_id=task_id,
            run_id=run_id,
            prepared_task=prepared_task,
            paths=paths,
            remote_task_path=remote_task_path,
            remote_artifacts_path=remote_artifacts_path,
            context=context,
        )
        self._register_retention(retention)

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
            return self._with_remote_cleanup(
                self._task_failure_from_adapter(put_result, "push task failed"),
                task_id=task_id,
                prepared_task=prepared_task,
                paths=paths,
                remote_task_path=remote_task_path,
                remote_artifacts_path=remote_artifacts_path,
                custody_token=custody_token,
            )

        pre = self.take_clock_marker()
        if isinstance(pre, AdapterResult):
            return self._with_remote_cleanup(
                self._task_failure_from_adapter(pre, "pre-task clock marker failed"),
                task_id=task_id,
                prepared_task=prepared_task,
                paths=paths,
                remote_task_path=remote_task_path,
                remote_artifacts_path=remote_artifacts_path,
                custody_token=custody_token,
            )

        run_result = self.transport.run(
            [
                self.remote_python,
                self.remote_worker_path,
                "--task",
                remote_task_path,
                "--artifacts",
                remote_artifacts_path,
                "--work-root",
                self.remote_work_root,
            ],
            timeout_s=timeout_s,
        )
        execution_state = str(
            run_result.metadata.get(
                "execution_state",
                "completed" if run_result.failure_reason != FailureReason.TRANSPORT_UNAVAILABLE else "ambiguous",
            )
        )
        if execution_state == "not_started":
            return self._with_remote_cleanup(
                self._task_failure_from_adapter(
                    run_result,
                    "worker command did not start",
                    pre_marker=pre,
                ),
                task_id=task_id,
                prepared_task=prepared_task,
                paths=paths,
                remote_task_path=remote_task_path,
                remote_artifacts_path=remote_artifacts_path,
                custody_token=custody_token,
            )

        self._mark_worker_may_have_run(custody_token)
        post = self.take_clock_marker()
        post_marker = post if isinstance(post, ClockMarker) else None
        alignment = None
        if post_marker is not None:
            alignment = self._alignment_record(pre, post_marker)
            alignment["stage"] = self._stage_name(prepared_task)
            recorder = getattr(self.transport, "record_clock_alignment", None)
            if callable(recorder):
                recorder(alignment)

        result_metadata: dict[str, Any] = {
            "worker_returncode": run_result.metadata.get("returncode"),
            "worker_execution_state": execution_state,
            "worker_command_ok": run_result.ok,
        }
        if not run_result.ok:
            result_metadata["worker_command_failure_reason"] = (
                run_result.failure_reason.value if run_result.failure_reason else None
            )
            result_metadata["worker_command_message"] = run_result.message
        if isinstance(post, AdapterResult):
            result_metadata["post_marker_failure"] = post.message or "post-task clock marker failed"
        if alignment is not None:
            result_metadata["clock_alignment"] = alignment

        local_artifacts_path = Path(retention["custody_path"])
        local_artifacts_path.parent.mkdir(parents=True, exist_ok=True)
        collect_result = self.transport.collect(
            remote_artifacts_path,
            str(local_artifacts_path),
            timeout_s=FILE_TRANSFER_TIMEOUT_S,
        )
        if not collect_result.ok:
            result = self._task_failure_from_adapter(
                collect_result,
                "collect artifacts failed",
                pre_marker=pre,
                post_marker=post_marker,
                alignment=alignment,
            )
            result = self._replace_result_metadata(result, result_metadata)
        else:
            status_path = local_artifacts_path / STATUS_JSON
            try:
                raw_status = json.loads(status_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                result = self._task_failure(
                    FailureReason.UNKNOWN_ERROR,
                    "missing or malformed status.json: %s" % exc,
                    pre_marker=pre,
                    post_marker=post_marker,
                    alignment=alignment,
                    metadata={
                        **result_metadata,
                        "retained_evidence_path": str(local_artifacts_path),
                    },
                )
            else:
                try:
                    self._validate_response_identity(raw_status, prepared_task)
                except ValueError as exc:
                    result = self._task_failure(
                        FailureReason.UNKNOWN_ERROR,
                        "node worker response identity mismatch: %s" % exc,
                        pre_marker=pre,
                        post_marker=post_marker,
                        alignment=alignment,
                        metadata={
                            **result_metadata,
                            "retained_evidence_path": str(local_artifacts_path),
                            "response_identity_validated": False,
                        },
                    )
                else:
                    artifacts = self._read_flat_artifacts(local_artifacts_path)
                    self._mark_response_validated(custody_token)
                    status = str(raw_status.get("status", "failed"))
                    failure_reason = self._failure_reason(raw_status.get("failure_reason"))
                    message = str(raw_status.get("message", ""))
                    if isinstance(post, AdapterResult):
                        status = "failed"
                        failure_reason = FailureReason.TRANSPORT_UNAVAILABLE
                        message = post.message or "post-task clock marker failed"
                    result = NodeTaskResult(
                        ok=status == "succeeded",
                        status=status,
                        failure_reason=failure_reason,
                        message=message,
                        artifacts_path=local_artifacts_path,
                        artifacts=artifacts,
                        raw_status=raw_status,
                        pre_marker=pre,
                        post_marker=post_marker,
                        offset_estimate_s=(
                            alignment["offset_estimate_s"] if alignment is not None else None
                        ),
                        offset_bound_s=(
                            alignment["offset_bound_s"] if alignment is not None else None
                        ),
                        metadata={
                            **result_metadata,
                            "node_worker_protocol_version": PROTOCOL_VERSION,
                            "response_identity_validated": True,
                        },
                    )
        return self._with_remote_cleanup(
            result,
            task_id=task_id,
            prepared_task=prepared_task,
            paths=paths,
            remote_task_path=remote_task_path,
            remote_artifacts_path=remote_artifacts_path,
            custody_token=custody_token,
            standalone_bundle_path=(
                Path(str(retention["bundle_path"])) if context is None else None
            ),
        )

    def _read_flat_artifacts(self, artifacts_path: Path) -> dict[str, bytes]:
        artifacts: dict[str, bytes] = {}
        for path in artifacts_path.iterdir():
            if path.is_file():
                artifacts[path.name] = path.read_bytes()
        return artifacts

    def _with_remote_cleanup(
        self,
        result: NodeTaskResult,
        *,
        task_id: str,
        prepared_task: dict[str, Any],
        paths: dict[str, str],
        remote_task_path: str,
        remote_artifacts_path: str,
        custody_token: str,
        standalone_bundle_path: Path | None = None,
    ) -> NodeTaskResult:
        del remote_task_path, remote_artifacts_path
        worker_metadata = (
            result.raw_status.get("metadata")
            if isinstance(result.raw_status, dict)
            else None
        )
        process_survived = (
            isinstance(worker_metadata, dict)
            and worker_metadata.get("process_survived") is True
        )
        if (
            prepared_task.get("task_type") == "runtime"
            and prepared_task.get("operation") == "cleanup"
            and not process_survived
        ):
            self._update_retention_targets(custody_token, [paths["run_dir"]])
        custody_state = "retained_pending_durable_acknowledgement"
        if (
            result.ok
            and standalone_bundle_path is not None
            and result.artifacts_path is not None
        ):
            acknowledgement = acknowledge_durable_custody(
                standalone_bundle_path,
                custody_token,
                [result.artifacts_path],
            )
            released = self.acknowledge_custody(acknowledgement)
            custody_state = (
                "released_after_durable_acknowledgement"
                if released and all(row["removed"] for row in released)
                else "acknowledged_pending_remote_reclamation"
            )
        rows = [
            item
            for item in self._cleanup_report
            if item.get("custody_token") == custody_token
        ]
        metadata = dict(result.metadata)
        metadata["node_cleanup"] = rows
        metadata["custody"] = {
            "token": custody_token,
            "state": custody_state,
        }
        return NodeTaskResult(
            ok=result.ok,
            status=result.status,
            failure_reason=result.failure_reason,
            message=result.message,
            artifacts_path=result.artifacts_path,
            artifacts=dict(result.artifacts),
            raw_status=result.raw_status,
            pre_marker=result.pre_marker,
            post_marker=result.post_marker,
            offset_estimate_s=result.offset_estimate_s,
            offset_bound_s=result.offset_bound_s,
            metadata=metadata,
            custody_token=custody_token,
        )

    def acknowledge_custody(
        self,
        acknowledgement: DurableCustodyAcknowledgement,
    ) -> list[dict[str, Any]]:
        """Release retained remote artifacts only after durable token proof."""

        with self._retention_manifest_lock():
            records = self._load_retention_records()
            record = next(
                (item for item in records if item.get("token") == acknowledgement.token),
                None,
            )
            if record is None:
                return []
            if not self._acknowledgement_is_valid(acknowledgement, record):
                raise ValueError("custody acknowledgement does not match retained task")
            record["acknowledgement_path"] = str(acknowledgement.acknowledgement_path)
            record["acknowledged"] = True
            self._write_retention_records(records)
            return self._cleanup_retention_record(record, records)

    def _new_retention_record(
        self,
        *,
        token: str,
        task_id: str,
        run_id: str,
        prepared_task: dict[str, Any],
        paths: dict[str, str],
        remote_task_path: str,
        remote_artifacts_path: str,
        context: RunContext | None,
    ) -> dict[str, Any]:
        if context is None:
            bundle_path = self.retention_root / "standalone" / token
            custody_path = bundle_path / "raw" / "node-custody"
        else:
            bundle_path = context.bundle_path
            custody_path = context.raw_dir / ".node-custody" / token
        return {
            "token": token,
            "correlation_token": prepared_task.get("correlation_token"),
            "protocol_version": prepared_task.get("protocol_version"),
            "scope": self._retention_scope(),
            "task_id": task_id,
            "run_id": run_id,
            "task_type": prepared_task.get("task_type"),
            "operation": prepared_task.get("operation"),
            "node_role": prepared_task.get("node_role"),
            "run_dir": paths["run_dir"],
            "remote_artifacts_path": remote_artifacts_path,
            "remote_targets": [remote_task_path, remote_artifacts_path],
            "bundle_path": str(bundle_path),
            "custody_path": str(custody_path),
            "worker_may_have_run": False,
            "collection_complete": False,
            "response_identity_validated": False,
            "partial_custody_paths": [],
            "acknowledged": False,
            "acknowledgement_path": None,
        }

    def _register_retention(self, record: dict[str, Any]) -> None:
        with self._retention_manifest_lock():
            records = self._load_retention_records()
            records.append(record)
            self._write_retention_records(records)
        self._cleanup_report.extend(
            {
                "task_id": record["task_id"],
                "scope": "remote",
                "path": target,
                "removed": False,
                "error": None,
                "deferred_for_custody": True,
                "custody_token": record["token"],
            }
            for target in record["remote_targets"]
        )

    def _update_retention_targets(self, token: str, targets: list[str]) -> None:
        with self._retention_manifest_lock():
            records = self._load_retention_records()
            record = next((item for item in records if item.get("token") == token), None)
            if record is None:
                raise RuntimeError("retention record disappeared before custody acknowledgement")
            record["remote_targets"] = list(targets)
            self._write_retention_records(records)
        known = {
            item.get("path")
            for item in self._cleanup_report
            if item.get("custody_token") == token
        }
        for target in targets:
            if target not in known:
                self._cleanup_report.append(
                    {
                        "task_id": record["task_id"],
                        "scope": "remote",
                        "path": target,
                        "removed": False,
                        "error": None,
                        "deferred_for_custody": True,
                        "custody_token": token,
                    }
                )

    def _mark_worker_may_have_run(self, token: str) -> None:
        self._update_retention_field(token, "worker_may_have_run", True)

    def _mark_collection_complete(self, token: str) -> None:
        self._update_retention_field(token, "collection_complete", True)

    def _mark_response_validated(self, token: str) -> None:
        with self._retention_manifest_lock():
            records = self._load_retention_records()
            record = next((item for item in records if item.get("token") == token), None)
            if record is None:
                raise RuntimeError("retention record disappeared before response validation")
            record["collection_complete"] = True
            record["response_identity_validated"] = True
            self._write_retention_records(records)

    def _update_retention_field(self, token: str, key: str, value: Any) -> None:
        with self._retention_manifest_lock():
            records = self._load_retention_records()
            record = next((item for item in records if item.get("token") == token), None)
            if record is None:
                raise RuntimeError("retention record disappeared before state update")
            record[key] = value
            self._write_retention_records(records)

    def _sweep_retained_artifacts(self) -> bool:
        with self._retention_manifest_lock(skip_on_failure=True) as locked:
            if not locked:
                return False
            self._sweep_retained_artifacts_locked()
            return True

    def _sweep_retained_artifacts_locked(self) -> None:
        records = self._load_retention_records()
        for record in list(records):
            if record.get("scope") != self._retention_scope():
                continue
            if record.get("acknowledged"):
                if not self._record_acknowledgement_is_valid(record):
                    self._cleanup_report.append(
                        {
                            "task_id": record["task_id"],
                            "scope": "remote",
                            "path": str(record.get("acknowledgement_path") or ""),
                            "removed": False,
                            "error": "durable custody acknowledgement is missing or invalid",
                            "custody_token": record["token"],
                            "reclamation_sweep": True,
                        }
                    )
                    continue
            else:
                custody_path = Path(str(record["custody_path"]))
                if not record.get("worker_may_have_run"):
                    custody_path.mkdir(parents=True, exist_ok=True)
                    dispatch_record = custody_path / "dispatch-retention.json"
                    dispatch_record.write_text(
                        json.dumps(
                            {
                                "schema_version": 1,
                                "custody_token": record["token"],
                                "task_id": record["task_id"],
                                "run_id": record["run_id"],
                                "worker_may_have_run": False,
                            },
                            indent=2,
                            sort_keys=True,
                        )
                        + "\n",
                        encoding="utf-8",
                    )
                    record["collection_complete"] = True
                    self._write_retention_records(records)
                elif (
                    not record.get("collection_complete")
                    or not record.get("response_identity_validated")
                    or not self._custody_path_has_evidence(custody_path)
                ):
                    partial_paths = record.setdefault("partial_custody_paths", [])
                    if (
                        self._custody_path_has_evidence(custody_path)
                        and str(custody_path) not in partial_paths
                    ):
                        partial_paths.append(str(custody_path))
                    recollection_path = custody_path.parent / (
                        custody_path.name + ".recollect-" + uuid.uuid4().hex
                    )
                    recollection_path.parent.mkdir(parents=True, exist_ok=True)
                    self._validate_retention_record_paths(record)
                    collected = self.transport.collect(
                        str(record["remote_artifacts_path"]),
                        str(recollection_path),
                        timeout_s=FILE_TRANSFER_TIMEOUT_S,
                    )
                    if not collected.ok or not self._custody_path_has_evidence(
                        recollection_path
                    ):
                        superseded_paths = self._retain_failed_recollection(
                            record,
                            original_path=custody_path,
                            recollection_path=recollection_path,
                        )
                        self._write_retention_records(records)
                        for superseded_path in superseded_paths:
                            if superseded_path.is_dir():
                                shutil.rmtree(superseded_path)
                            else:
                                superseded_path.unlink(missing_ok=True)
                        self._cleanup_report.append(
                            {
                                "task_id": record["task_id"],
                                "scope": "remote",
                                "path": str(record["remote_artifacts_path"]),
                                "removed": False,
                                "error": collected.message or "retained artifacts unavailable",
                                "custody_token": record["token"],
                                "reclamation_sweep": True,
                            }
                        )
                        continue
                    try:
                        raw_status = json.loads(
                            (recollection_path / STATUS_JSON).read_text(encoding="utf-8")
                        )
                        self._validate_response_identity(raw_status, record)
                    except (OSError, json.JSONDecodeError, ValueError) as exc:
                        superseded_paths = self._retain_failed_recollection(
                            record,
                            original_path=custody_path,
                            recollection_path=recollection_path,
                        )
                        self._write_retention_records(records)
                        for superseded_path in superseded_paths:
                            if superseded_path.is_dir():
                                shutil.rmtree(superseded_path)
                            else:
                                superseded_path.unlink(missing_ok=True)
                        self._cleanup_report.append(
                            {
                                "task_id": record["task_id"],
                                "scope": "remote",
                                "path": str(record["remote_artifacts_path"]),
                                "removed": False,
                                "error": "retained response identity invalid: %s" % exc,
                                "custody_token": record["token"],
                                "reclamation_sweep": True,
                            }
                        )
                        continue
                    record["custody_path"] = str(recollection_path)
                    custody_path = recollection_path
                    record["collection_complete"] = True
                    record["response_identity_validated"] = True
                    self._write_retention_records(records)
                acknowledgement = acknowledge_durable_custody(
                    Path(str(record["bundle_path"])),
                    str(record["token"]),
                    [custody_path],
                )
                record["acknowledged"] = True
                record["acknowledgement_path"] = str(
                    acknowledgement.acknowledgement_path
                )
                for partial_path_value in record.get("partial_custody_paths", []):
                    partial_path = Path(str(partial_path_value))
                    if partial_path != custody_path and partial_path.exists():
                        if partial_path.is_dir():
                            shutil.rmtree(partial_path)
                        else:
                            partial_path.unlink()
                record["partial_custody_paths"] = []
                self._write_retention_records(records)
            self._cleanup_retention_record(record, records)

    @contextmanager
    def _retention_manifest_lock(
        self,
        *,
        skip_on_failure: bool = False,
    ) -> Iterator[bool]:
        """Serialize retention-manifest read/modify/write critical sections."""

        handle = None
        try:
            self.retention_root.mkdir(parents=True, exist_ok=True)
            handle = self.retention_lock_path.open("a+b")
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        except OSError:
            if handle is not None:
                handle.close()
            if skip_on_failure:
                yield False
                return
            raise
        try:
            yield True
        finally:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            finally:
                handle.close()

    def _cleanup_retention_record(
        self,
        record: dict[str, Any],
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        self._validate_retention_record_paths(record)
        targets = [str(target) for target in record.get("remote_targets", [])]
        if not targets:
            return []
        run_dir = str(record.get("run_dir", ""))
        if targets == [run_dir] and any(
            other is not record
            and other.get("scope") == record.get("scope")
            and other.get("run_id") == record.get("run_id")
            and not other.get("acknowledged")
            for other in records
        ):
            return []
        try:
            cleanup = self.transport.run(
                ["rm", "-rf", "--", *targets],
                timeout_s=FILE_TRANSFER_TIMEOUT_S,
            )
        except BaseException as exc:
            rows = self._cleanup_rows(record, targets, False, "%s: %s" % (type(exc).__name__, exc))
            self._cleanup_report.extend(rows)
            self._write_retention_records(records)
            raise
        error = None if cleanup.ok else (cleanup.message or "remote cleanup failed")
        rows = self._cleanup_rows(record, targets, cleanup.ok, error)
        self._cleanup_report.extend(rows)
        if cleanup.ok:
            self._mark_eventually_removed(targets)
            records.remove(record)
        self._write_retention_records(records)
        return rows

    def _cleanup_rows(
        self,
        record: dict[str, Any],
        targets: list[str],
        removed: bool,
        error: str | None,
    ) -> list[dict[str, Any]]:
        return [
            {
                "task_id": record["task_id"],
                "scope": "remote",
                "path": target,
                "removed": removed,
                "error": error,
                "custody_token": record["token"],
                "after_durable_custody": True,
            }
            for target in targets
        ]

    def _mark_eventually_removed(self, targets: list[str]) -> None:
        for previous in self._cleanup_report:
            previous_path = previous.get("path")
            if previous.get("removed") is not False or not isinstance(previous_path, str):
                continue
            for target in targets:
                try:
                    within_target = posixpath.commonpath([target, previous_path]) == target
                except ValueError:
                    within_target = False
                if within_target:
                    previous["removed"] = True
                    previous["eventually_removed"] = True
                    break

    def _acknowledgement_is_valid(
        self,
        acknowledgement: DurableCustodyAcknowledgement,
        record: dict[str, Any],
    ) -> bool:
        try:
            payload = json.loads(
                acknowledgement.acknowledgement_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            return False
        bundle_path = Path(str(record["bundle_path"])).resolve()
        expected_custody_path = Path(str(record["custody_path"])).resolve()
        try:
            acknowledgement.acknowledgement_path.resolve().relative_to(bundle_path)
        except ValueError:
            return False
        return (
            (
                not record.get("worker_may_have_run")
                or record.get("response_identity_validated") is True
            )
            and record.get("correlation_token") == record.get("token")
            and payload.get("custody_token") == record.get("token")
            and acknowledgement.token == record.get("token")
            and expected_custody_path in {
                path.resolve() for path in acknowledgement.artifact_paths
            }
            and expected_custody_path.exists()
        )

    def _record_acknowledgement_is_valid(self, record: dict[str, Any]) -> bool:
        path_value = record.get("acknowledgement_path")
        if not isinstance(path_value, str) or not path_value:
            return False
        acknowledgement_path = Path(path_value)
        try:
            payload = json.loads(acknowledgement_path.read_text(encoding="utf-8"))
            acknowledgement_path.resolve().relative_to(
                Path(str(record["bundle_path"])).resolve()
            )
        except (OSError, ValueError, json.JSONDecodeError):
            return False
        return (
            (
                not record.get("worker_may_have_run")
                or record.get("response_identity_validated") is True
            )
            and record.get("correlation_token") == record.get("token")
            and payload.get("custody_token") == record.get("token")
            and Path(str(record["custody_path"])).exists()
        )

    @staticmethod
    def _custody_path_has_evidence(path: Path) -> bool:
        return path.is_dir() and any(candidate.is_file() for candidate in path.rglob("*"))

    def _retain_failed_recollection(
        self,
        record: dict[str, Any],
        *,
        original_path: Path,
        recollection_path: Path,
    ) -> list[Path]:
        """Retain only evidence-bearing failed copies, bounded per artifact."""

        partial_paths = [
            str(value)
            for value in record.get("partial_custody_paths", [])
            if self._custody_path_has_evidence(Path(str(value)))
        ]
        original_value = str(original_path)
        if (
            self._custody_path_has_evidence(original_path)
            and original_value not in partial_paths
        ):
            partial_paths.insert(0, original_value)

        if not self._custody_path_has_evidence(recollection_path):
            if recollection_path.is_dir():
                shutil.rmtree(recollection_path)
            else:
                recollection_path.unlink(missing_ok=True)
            record["partial_custody_paths"] = partial_paths
            return []

        recollection_value = str(recollection_path)
        partial_paths = [
            value for value in partial_paths if value != recollection_value
        ]
        partial_paths.append(recollection_value)
        failed_side_paths = [
            value for value in partial_paths if value != original_value
        ]
        superseded = failed_side_paths[:-MAX_RETAINED_FAILED_PARTIALS]
        record["partial_custody_paths"] = [
            value for value in partial_paths if value not in superseded
        ]
        return [Path(value) for value in superseded]

    def _retention_scope(self) -> dict[str, str]:
        destination = getattr(self.transport, "destination", None)
        return {
            "transport": "%s.%s"
            % (type(self.transport).__module__, type(self.transport).__qualname__),
            "destination": destination if isinstance(destination, str) else "",
            "remote_work_root": self.remote_work_root,
        }

    def _load_retention_records(self) -> list[dict[str, Any]]:
        if not self.retention_manifest_path.exists():
            return []
        payload = json.loads(self.retention_manifest_path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != RETENTION_MANIFEST_VERSION:
            raise ValueError("unsupported node custody retention manifest version")
        records = payload.get("records")
        if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
            raise ValueError("node custody retention manifest records must be objects")
        return records

    def _write_retention_records(self, records: list[dict[str, Any]]) -> None:
        self.retention_root.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": RETENTION_MANIFEST_VERSION,
            "records": records,
        }
        handle = tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            prefix=".retention-",
            suffix=".tmp",
            dir=self.retention_root,
            delete=False,
        )
        temporary_path = Path(handle.name)
        try:
            with handle:
                json.dump(payload, handle, indent=2, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, self.retention_manifest_path)
            directory_fd = os.open(self.retention_root, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            temporary_path.unlink(missing_ok=True)

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
        run_dir = self._contained_remote_path(run_id)
        return {
            "run_dir": run_dir,
            "tasks_dir": self._contained_remote_path(run_id, "tasks"),
            "artifacts_dir": self._contained_remote_path(run_id, "artifacts"),
            "state_dir": self._contained_remote_path(run_id, "state"),
        }

    def _prepare_task_payload(
        self,
        task: dict[str, Any],
        *,
        run_id: str,
        paths: dict[str, str],
        timeout_s: float,
        correlation_token: str,
    ) -> dict[str, Any]:
        payload = dict(task)
        payload["protocol_version"] = PROTOCOL_VERSION
        payload["correlation_token"] = correlation_token
        payload["run_id"] = run_id
        payload["timeout_s"] = float(timeout_s)
        task_paths = dict(payload.get("paths") or {})
        task_paths["state_dir"] = paths["state_dir"]
        payload["paths"] = task_paths
        return payload

    def _contained_remote_path(self, *components: str) -> str:
        candidate = posixpath.normpath(
            posixpath.join(self.remote_work_root, *components)
        )
        try:
            common = posixpath.commonpath([self.remote_work_root, candidate])
        except ValueError as exc:
            raise ValueError("remote path is not under remote_work_root") from exc
        if candidate == self.remote_work_root or common != self.remote_work_root:
            raise ValueError("remote path is not a contained non-root path")
        return candidate

    def _validate_dispatch_task(self, task: dict[str, Any]) -> tuple[str, str]:
        version = task.get("protocol_version", PROTOCOL_VERSION)
        if isinstance(version, bool) or not isinstance(version, int) or version != PROTOCOL_VERSION:
            raise ValueError("protocol_version must be integer %d before dispatch" % PROTOCOL_VERSION)
        for key in ("task_id", "run_id"):
            value = task.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError("%s is required before dispatch" % key)
            if SAFE_IDENTIFIER_PATTERN.fullmatch(value) is None:
                raise ValueError("%s must be a safe single path component" % key)
        for key in ("task_type", "operation"):
            value = task.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError("%s is required before dispatch" % key)
        if "node_role" not in task:
            raise ValueError("node_role is required before dispatch")
        if task["node_role"] is not None and not isinstance(task["node_role"], str):
            raise ValueError("node_role must be null or a string before dispatch")
        return str(task["task_id"]), str(task["run_id"])

    def _validate_response_identity(
        self,
        raw_status: Any,
        expected: dict[str, Any],
    ) -> None:
        if not isinstance(raw_status, dict):
            raise ValueError("status.json must contain an object")
        expected_identity = {
            "protocol_version": PROTOCOL_VERSION,
            "correlation_token": expected.get("correlation_token", expected.get("token")),
            "run_id": expected.get("run_id"),
            "task_id": expected.get("task_id"),
            "task_type": expected.get("task_type"),
            "operation": expected.get("operation"),
            "node_role": expected.get("node_role"),
        }
        response_version = raw_status.get("protocol_version")
        if isinstance(response_version, bool) or not isinstance(response_version, int):
            raise ValueError(
                "protocol_version expected integer %d, got %r"
                % (PROTOCOL_VERSION, response_version)
            )
        for key, value in expected_identity.items():
            if key not in raw_status or raw_status[key] != value:
                raise ValueError(
                    "%s expected %r, got %r" % (key, value, raw_status.get(key))
                )

    def _validate_retention_record_paths(self, record: dict[str, Any]) -> None:
        task_id, run_id = self._validate_dispatch_task(record)
        expected_paths = self._remote_paths_for_run(run_id)
        expected_task = self._contained_remote_path(
            run_id,
            "tasks",
            "%s.json" % task_id,
        )
        expected_artifacts = self._contained_remote_path(
            run_id,
            "artifacts",
            task_id,
        )
        if record.get("run_dir") != expected_paths["run_dir"]:
            raise ValueError("retained run_dir does not match safe dispatch path")
        if record.get("remote_artifacts_path") != expected_artifacts:
            raise ValueError("retained artifacts path does not match safe dispatch path")
        targets = [str(value) for value in record.get("remote_targets", [])]
        if targets not in ([expected_task, expected_artifacts], [expected_paths["run_dir"]]):
            raise ValueError("retained cleanup targets do not match safe dispatch paths")

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

    def _replace_result_metadata(
        self,
        result: NodeTaskResult,
        extra: dict[str, Any],
    ) -> NodeTaskResult:
        metadata = dict(result.metadata)
        metadata.update(extra)
        return NodeTaskResult(
            ok=result.ok,
            status=result.status,
            failure_reason=result.failure_reason,
            message=result.message,
            artifacts_path=result.artifacts_path,
            artifacts=dict(result.artifacts),
            raw_status=result.raw_status,
            pre_marker=result.pre_marker,
            post_marker=result.post_marker,
            offset_estimate_s=result.offset_estimate_s,
            offset_bound_s=result.offset_bound_s,
            metadata=metadata,
            custody_token=result.custody_token,
        )

    def _failure_reason(self, value: Any) -> FailureReason | None:
        if value is None:
            return None
        try:
            return FailureReason(value)
        except ValueError:
            return FailureReason.UNKNOWN_ERROR
