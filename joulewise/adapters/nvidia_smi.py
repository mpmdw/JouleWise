"""NVIDIA ``nvidia-smi`` telemetry adapter (Slice 2K B-1, B-3..B-6, B-8).

The node worker owns process control and raw CSV collection. This controller
adapter owns CSV parsing, node-to-controller timestamp conversion, bundle raw
preservation (D-002), and JouleWise telemetry object construction. The raw CSV
timestamp is a naive node-local wall time string; new worker artifacts include
the node UTC offset used to parse it before B-5 clock-domain conversion.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from joulewise.adapters.node_client import (
    NodeTaskResult,
    NodeWorkerClient,
    convert_node_timestamp,
)
from joulewise.bundle import write_raw_artifact
from joulewise.clock import Clock
from joulewise.interfaces import (
    AdapterFailure,
    AdapterResult,
    PowerSample,
    RunContext,
    ThermalState,
)
from joulewise.schemas import BenchmarkConfig, FailureReason, IdleBaseline, TelemetryBackend

RAW_SAMPLES_NAME = "nvidia_smi.csv"
RAW_IDLE_NAME = "nvidia_smi_idle.csv"
WORKER_LOG_NAME = "worker.log"
RAIL_MANIFEST = ["gpu_board"]
QUERY_FIELDS = ["timestamp", "power.draw", "temperature.gpu"]
SOURCE = "nvidia_smi"
BOUNDARY = "NVIDIA GPU board power via nvidia-smi power.draw; host CPU/DRAM excluded"
TIMESTAMP_ASSUMPTION = (
    "nvidia-smi CSV timestamps are parsed as node-local wall time using the "
    "node UTC offset recorded by the worker. Legacy artifacts without an "
    "offset fall back to parser-local timezone with a provenance warning."
)
POWER_NA_POLICY = (
    "Rows whose power.draw field is [N/A] or [Not Supported] are skipped; "
    "raw CSV remains verbatim under raw/."
)


@dataclass(frozen=True)
class NvidiaSmiRow:
    node_timestamp_s: float
    power_w: float
    temperature_c: float


class NvidiaSmiTelemetryAdapter:
    """Telemetry adapter backed by a node-worker managed ``nvidia-smi`` sampler."""

    name = SOURCE

    def __init__(self, clock: Clock, client: NodeWorkerClient) -> None:
        self._clock = clock
        self._client = client
        self._task_counter = 0
        self._last_rows: list[NvidiaSmiRow] = []
        self._last_thermal_timestamp_s: float | None = None
        self._last_temperature_c: float | None = None
        self._clock_alignments: list[dict[str, Any]] = []
        self._last_parse_diagnostics: dict[str, Any] = {}

    def clock_alignments(self) -> list[dict[str, Any]]:
        return [dict(alignment) for alignment in self._clock_alignments]

    def device_metadata(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> dict[str, Any]:
        del context
        return {
            "device": config.hardware_target.id,
            "telemetry": self.name,
            "telemetry_backend": TelemetryBackend.NVIDIA_SMI.value,
            "rail_manifest": list(RAIL_MANIFEST),
            "boundary": BOUNDARY,
            "power_units": "watts from nvidia-smi power.draw",
            "query_fields": list(QUERY_FIELDS),
            "query_format": "csv,noheader,nounits",
            "node_worker_operations": [
                "telemetry/measure_idle",
                "telemetry/start_sampling",
                "telemetry/stop_sampling",
            ],
            "live_probe": "deferred to start_sampling/measure_idle node-worker task",
            "timestamp_assumption": TIMESTAMP_ASSUMPTION,
            "power_na_policy": POWER_NA_POLICY,
        }

    def measure_idle(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> IdleBaseline:
        result = self._run_task(
            "measure_idle",
            config,
            context,
            timeout_s=self._idle_timeout_s(config),
            idle_seconds=config.sampling.idle_seconds,
        )
        self._preserve_worker_log(result, context, "measure_idle")
        if not result.ok:
            self._raise_task_failure(result, "nvidia-smi idle measurement failed")

        data = self._artifact_bytes(result, "nvidia_smi_idle_csv", RAW_IDLE_NAME)
        if context is not None:
            write_raw_artifact(context, RAW_IDLE_NAME, data)
        parse_diagnostics: dict[str, Any] = {}
        rows = parse_nvidia_smi_csv(
            data.decode("utf-8", errors="replace"),
            node_utc_offset_s=self._node_utc_offset(result),
            diagnostics=parse_diagnostics,
        )
        self._last_parse_diagnostics = parse_diagnostics
        self._remember_rows(rows, result)
        powers = [row.power_w for row in rows]
        converted_timestamps = [
            convert_node_timestamp(row.node_timestamp_s, self._offset(result)) for row in rows
        ]
        duration_s = (
            max(0.0, converted_timestamps[-1] - converted_timestamps[0])
            if len(converted_timestamps) > 1
            else 0.0
        )
        return IdleBaseline(
            power_w_mean=statistics.mean(powers) if powers else 0.0,
            power_w_stddev=statistics.stdev(powers) if len(powers) > 1 else 0.0,
            duration_s=duration_s,
            sample_count=len(powers),
            telemetry_backend=TelemetryBackend.NVIDIA_SMI,
        )

    def start_sampling(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        result = self._run_task(
            "start_sampling",
            config,
            context,
            timeout_s=30.0,
        )
        self._preserve_worker_log(result, context, "start_sampling")
        metadata = self._result_metadata(result)
        return AdapterResult(
            ok=result.ok,
            failure_reason=result.failure_reason if not result.ok else None,
            message=result.message,
            metadata=metadata,
        )

    def stop_sampling(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> list[PowerSample]:
        result = self._run_task(
            "stop_sampling",
            config,
            context,
            timeout_s=30.0,
        )
        self._preserve_worker_log(result, context, "stop_sampling")
        if not result.ok:
            self._raise_task_failure(result, "nvidia-smi stop sampling failed")

        data = self._artifact_bytes(result, "nvidia_smi_csv", RAW_SAMPLES_NAME)
        if context is not None:
            write_raw_artifact(context, RAW_SAMPLES_NAME, data)
        parse_diagnostics = {}
        rows = parse_nvidia_smi_csv(
            data.decode("utf-8", errors="replace"),
            node_utc_offset_s=self._node_utc_offset(result),
            diagnostics=parse_diagnostics,
        )
        self._last_parse_diagnostics = parse_diagnostics
        self._remember_rows(rows, result)
        return self._samples_from_rows(rows, result)

    def thermal_state(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> ThermalState:
        del config, context
        return ThermalState(
            timestamp_s=(
                self._last_thermal_timestamp_s
                if self._last_thermal_timestamp_s is not None
                else self._clock.now()
            ),
            temperature_c=self._last_temperature_c,
            thermal_pressure=None,
            metadata={
                "source": self.name,
                "temperature_c_available": self._last_temperature_c is not None,
            },
        )

    def _run_task(
        self,
        operation: str,
        config: BenchmarkConfig,
        context: RunContext | None,
        *,
        timeout_s: float,
        idle_seconds: float | None = None,
    ) -> NodeTaskResult:
        self._task_counter += 1
        telemetry: dict[str, Any] = {
            "backend": self.name,
            "interval_ms": self._interval_ms(config),
            "query_fields": list(QUERY_FIELDS),
            "rail_manifest": list(RAIL_MANIFEST),
        }
        if idle_seconds is not None:
            telemetry["idle_seconds"] = float(idle_seconds)
        task = {
            "task_id": "task-telemetry-%s-%03d" % (operation, self._task_counter),
            "run_id": self._task_run_id(config, context),
            "task_type": "telemetry",
            "operation": operation,
            "node_role": context.node_role if context is not None else None,
            "telemetry": telemetry,
        }
        result = self._client.run_task(task, timeout_s=timeout_s)
        self._record_clock_alignment(result)
        return result

    def _samples_from_rows(
        self,
        rows: list[NvidiaSmiRow],
        result: NodeTaskResult,
    ) -> list[PowerSample]:
        offset = self._offset(result)
        return [
            PowerSample(
                timestamp_s=convert_node_timestamp(row.node_timestamp_s, offset),
                power_w=row.power_w,
                source=self.name,
                rail=RAIL_MANIFEST[0],
            )
            for row in rows
        ]

    def _remember_rows(self, rows: list[NvidiaSmiRow], result: NodeTaskResult) -> None:
        self._last_rows = list(rows)
        if not rows:
            return
        last = rows[-1]
        self._last_temperature_c = last.temperature_c
        self._last_thermal_timestamp_s = convert_node_timestamp(
            last.node_timestamp_s,
            self._offset(result),
        )

    def _artifact_bytes(
        self,
        result: NodeTaskResult,
        artifact_key: str,
        fallback_name: str,
    ) -> bytes:
        if result.artifacts_path is None:
            raise AdapterFailure(
                result.failure_reason or FailureReason.UNKNOWN_ERROR,
                "node task did not return an artifacts path",
                self._result_metadata(result),
            )
        artifacts = result.raw_status.get("artifacts", {}) if result.raw_status else {}
        relative = artifacts.get(artifact_key, fallback_name)
        path = Path(result.artifacts_path) / str(relative)
        try:
            return path.read_bytes()
        except OSError as exc:
            raise AdapterFailure(
                FailureReason.UNKNOWN_ERROR,
                "could not read collected nvidia-smi artifact %s: %s" % (path.name, exc),
                self._result_metadata(result),
            ) from exc

    def _preserve_worker_log(
        self,
        result: NodeTaskResult,
        context: RunContext | None,
        operation: str,
    ) -> None:
        if context is None or result.artifacts_path is None:
            return
        artifacts = result.raw_status.get("artifacts", {}) if result.raw_status else {}
        relative = artifacts.get("worker_log", WORKER_LOG_NAME)
        source = Path(result.artifacts_path) / str(relative)
        task_id = (
            str(result.raw_status.get("task_id"))
            if result.raw_status and result.raw_status.get("task_id")
            else "nvidia-smi-%s" % operation
        )
        safe_task_id = task_id.replace("/", "-")
        try:
            text = source.read_text(encoding="utf-8")
        except OSError:
            return
        (context.logs_dir / ("%s_worker.log" % safe_task_id)).write_text(
            text,
            encoding="utf-8",
        )

    def _raise_task_failure(self, result: NodeTaskResult, fallback: str) -> None:
        raise AdapterFailure(
            result.failure_reason or FailureReason.UNKNOWN_ERROR,
            result.message or fallback,
            self._result_metadata(result),
        )

    def _result_metadata(self, result: NodeTaskResult) -> dict[str, Any]:
        metadata = dict(result.metadata)
        if result.raw_status and isinstance(result.raw_status.get("metadata"), dict):
            metadata["worker_metadata"] = result.raw_status["metadata"]
        metadata["worker_status"] = result.status
        if result.offset_estimate_s is not None:
            metadata["offset_estimate_s"] = result.offset_estimate_s
        if result.offset_bound_s is not None:
            metadata["offset_bound_s"] = result.offset_bound_s
        if self._last_parse_diagnostics:
            metadata["parse_diagnostics"] = dict(self._last_parse_diagnostics)
        return metadata

    def _record_clock_alignment(self, result: NodeTaskResult) -> None:
        alignment = result.metadata.get("clock_alignment")
        if isinstance(alignment, dict):
            self._clock_alignments.append(dict(alignment))

    def _task_run_id(self, config: BenchmarkConfig, context: RunContext | None) -> str:
        if context is not None and context.run_id:
            return context.run_id
        if config.run_id:
            return config.run_id
        raise AdapterFailure(
            FailureReason.UNKNOWN_ERROR,
            "nvidia-smi node task requires a run_id from RunContext or config",
        )

    def _node_utc_offset(self, result: NodeTaskResult) -> float | None:
        if result.raw_status and isinstance(result.raw_status.get("metadata"), dict):
            metadata = result.raw_status["metadata"]
            if "node_utc_offset_s" in metadata:
                return _float_or_none(metadata.get("node_utc_offset_s"))
            pidfile = metadata.get("pidfile_payload")
            if isinstance(pidfile, dict) and "node_utc_offset_s" in pidfile:
                return _float_or_none(pidfile.get("node_utc_offset_s"))
        worker_metadata = result.metadata.get("worker_metadata")
        if isinstance(worker_metadata, dict):
            return _float_or_none(worker_metadata.get("node_utc_offset_s"))
        return None

    @staticmethod
    def _offset(result: NodeTaskResult) -> float:
        return float(result.offset_estimate_s) if result.offset_estimate_s is not None else 0.0

    @staticmethod
    def _interval_ms(config: BenchmarkConfig) -> int:
        return max(1, int(round(1000.0 / config.sampling.power_hz)))

    def _idle_timeout_s(self, config: BenchmarkConfig) -> float:
        nominal_s = max(0.0, float(config.sampling.idle_seconds))
        interval_s = self._interval_ms(config) / 1000.0
        return max(30.0, nominal_s + interval_s + 15.0)


def parse_nvidia_smi_csv(
    text: str,
    *,
    node_utc_offset_s: float | None = None,
    diagnostics: dict[str, Any] | None = None,
) -> list[NvidiaSmiRow]:
    """Parse ``nvidia-smi --format=csv,noheader,nounits`` output.

    Blank lines are ignored. Rows with unsupported power fields are skipped
    rather than represented as partial samples because JouleWise
    ``PowerSample`` requires a numeric watt value and the raw row remains
    preserved verbatim.
    """

    if diagnostics is not None:
        diagnostics.setdefault("truncated_final_rows_skipped", 0)
    rows: list[NvidiaSmiRow] = []
    lines = text.splitlines()
    timestamp_tz = _timestamp_timezone(node_utc_offset_s, diagnostics)
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 3:
            if _is_truncated_final_row(text, lines, index):
                if diagnostics is not None:
                    diagnostics["truncated_final_rows_skipped"] += 1
                continue
            raise ValueError("nvidia-smi CSV row %d has %d fields, expected 3" % (index, len(parts)))
        power_w = _power_or_none(parts[1])
        if power_w is None:
            continue
        try:
            timestamp = datetime.strptime(parts[0], "%Y/%m/%d %H:%M:%S.%f")
            temperature_c = float(parts[2])
        except ValueError as exc:
            if _is_truncated_final_row(text, lines, index):
                if diagnostics is not None:
                    diagnostics["truncated_final_rows_skipped"] += 1
                continue
            raise ValueError("nvidia-smi CSV row %d is not parseable: %s" % (index, exc)) from exc
        if not math.isfinite(power_w) or not math.isfinite(temperature_c):
            continue
        rows.append(
            NvidiaSmiRow(
                node_timestamp_s=timestamp.replace(tzinfo=timestamp_tz).timestamp(),
                power_w=power_w,
                temperature_c=temperature_c,
            )
        )
    return rows


def _power_or_none(value: str) -> float | None:
    normalized = value.strip().strip("[]").strip().lower()
    if normalized in {"n/a", "not supported", "na", ""}:
        return None
    return float(value)


def _timestamp_timezone(
    node_utc_offset_s: float | None,
    diagnostics: dict[str, Any] | None,
) -> timezone | None:
    if node_utc_offset_s is None:
        if diagnostics is not None:
            diagnostics["timestamp_timezone_source"] = "parser_local_legacy_fallback"
            diagnostics.setdefault("warnings", []).append(
                "node UTC offset missing; parsed nvidia-smi timestamps with parser local timezone"
            )
        return None
    if diagnostics is not None:
        diagnostics["timestamp_timezone_source"] = "node_utc_offset_s"
        diagnostics["node_utc_offset_s"] = node_utc_offset_s
    return timezone(timedelta(seconds=float(node_utc_offset_s)))


def _is_truncated_final_row(text: str, lines: list[str], index: int) -> bool:
    return index == len(lines) - 1 and not text.endswith(("\n", "\r"))


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
