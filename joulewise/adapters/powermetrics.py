"""Apple ``powermetrics`` telemetry adapter (D-002, D-004, D-018).

The parser is pinned to the captured plist stream fixture landed for Slice 2H:
NUL-separated XML plist documents, with Apple SoC power rails under the
top-level ``processor`` dictionary. ``powermetrics`` reports those rail values
in milliwatts; JouleWise emits watts.
"""

from __future__ import annotations

import getpass
import hashlib
import json
import math
import plistlib
import statistics
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.parsers.expat import ExpatError

from joulewise.bundle import BundleError, write_derived_artifact, write_raw_artifact
from joulewise.clock import Clock
from joulewise.interfaces import (
    AdapterFailure,
    AdapterResult,
    PowerSample,
    RunContext,
    ThermalState,
)
from joulewise.schemas import BenchmarkConfig, FailureReason, IdleBaseline, TelemetryBackend
from joulewise.validation import finite_float

POWER_METRICS = "/usr/bin/powermetrics"
RAW_SAMPLES_NAME = "powermetrics.plist"
RAW_IDLE_NAME = "powermetrics_idle.plist"
RICH_TELEMETRY_NAME = "rich_telemetry.jsonl"
RICH_IDLE_NAME = "rich_telemetry_idle.jsonl"
RAIL_MANIFEST = ["cpu_power", "gpu_power", "ane_power"]
SAMPLERS = "cpu_power,gpu_power,ane_power,thermal"
READINESS_TIMEOUT_S = 15.0
READINESS_POLL_S = 0.05
IDLE_GPU_IDLE_RATIO_THRESHOLD = 0.80
IDLE_GPU_LOW_IDLE_FRACTION_THRESHOLD = 0.40
IDLE_GPU_FREQ_MEAN_MHZ_THRESHOLD = 800.0
TIMESTAMP_DERIVATION = (
    "timestamp_s = start_sampling readiness clock.now() UTC epoch seconds + "
    "cumulative elapsed_ns through the current plist document; start_sampling "
    "waits until the first plist document is parseable before returning, so "
    "the reducer's sampling_started marker is emitted only after the sampler "
    "is producing. The plist timestamp is 1-second resolution and is recorded "
    "only as plist_anchor_offset_s evidence."
)


@dataclass(frozen=True)
class PowermetricsRecord:
    timestamp_s: float
    elapsed_ns: int
    rail_power_w: dict[str, float]
    combined_power_w: float
    rail_energy_mj: dict[str, int]
    thermal_pressure: str | None
    metadata: dict[str, Any]


@dataclass(frozen=True)
class _DroppedFrameDiagnostic:
    frame_index: int
    byte_count: int
    sha256: str
    error: str

    def to_metadata(self, *, artifact: str, capture: str) -> dict[str, Any]:
        return {
            "adapter": "powermetrics",
            "artifact": artifact,
            "capture": capture,
            "action": "dropped_final_unparseable_frame",
            "frame_index": self.frame_index,
            "byte_count": self.byte_count,
            "sha256": self.sha256,
            "error": self.error,
        }


class PowermetricsTelemetryAdapter:
    """Telemetry adapter backed by macOS ``powermetrics`` plist output."""

    name = "powermetrics"

    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._process: subprocess.Popen[bytes] | None = None
        self._capture_path: Path | None = None
        self._clock_start_s: float | None = None
        self._device_metadata = self._base_device_metadata(None)
        self._capability: AdapterResult | None = None
        self._last_records: list[PowermetricsRecord] = []

    def device_metadata(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> dict:
        self._device_metadata.update(self._base_device_metadata(config))
        return self._device_metadata

    def measure_idle(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> IdleBaseline:
        capability = self._ensure_capability()
        if not capability.ok:
            raise AdapterFailure(
                capability.failure_reason or FailureReason.UNKNOWN_ERROR,
                capability.message or "powermetrics idle measurement unavailable",
                capability.metadata,
            )

        count = self._idle_count(config)
        capture_start_s = self._clock.now()
        data = self._run_bounded_capture(config, count=count)
        if context is not None:
            write_raw_artifact(context, RAW_IDLE_NAME, data)
        records, diagnostic = _parse_powermetrics_records(
            data, timestamp_anchor_s=capture_start_s
        )
        self._record_parse_diagnostic(
            diagnostic,
            artifact=f"raw/{RAW_IDLE_NAME}",
            capture="idle_baseline",
        )
        rich_records = decode_rich_telemetry(data)
        if context is not None:
            self._write_rich_artifact(
                context=context,
                name=RICH_IDLE_NAME,
                data=rich_telemetry_jsonl_from_records(rich_records),
                error_key="rich_telemetry_idle_error",
            )
        self._remember_records(records, timestamp_anchor_s=capture_start_s)
        totals = [record.combined_power_w for record in records]
        duration_s = sum(record.elapsed_ns for record in records) / 1_000_000_000.0
        idle_quality = idle_window_gpu_quality(rich_records)
        return IdleBaseline(
            power_w_mean=statistics.mean(totals) if totals else 0.0,
            power_w_stddev=statistics.stdev(totals) if len(totals) > 1 else 0.0,
            duration_s=duration_s,
            sample_count=len(totals),
            telemetry_backend=TelemetryBackend.POWERMETRICS,
            gpu_idle_ratio_mean=idle_quality["gpu_idle_ratio_mean"],
            gpu_idle_ratio_min=idle_quality["gpu_idle_ratio_min"],
            gpu_freq_hz_mean=idle_quality["gpu_freq_hz_mean"],
            idle_window_suspect=idle_quality["idle_window_suspect"],
        )

    def start_sampling(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        capability = self._ensure_capability()
        if not capability.ok:
            return capability
        if self._process is not None:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.UNKNOWN_ERROR,
                message="powermetrics sampling is already active",
            )

        self._capture_path = self._new_capture_path()
        command = self._command(
            config,
            self._capture_path,
            count=None,
            interval_ms=self._interval_ms(config),
        )
        try:
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError as exc:
            self._capture_path.unlink(missing_ok=True)
            self._capture_path = None
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TELEMETRY_UNAVAILABLE,
                message=f"powermetrics launcher unavailable: {exc}",
            )
        ready = self._wait_until_ready(self._process, self._capture_path)
        if not ready.ok:
            self._stop_process(self._process)
            self._process = None
            self._capture_path.unlink(missing_ok=True)
            self._capture_path = None
            return ready
        self._clock_start_s = self._clock.now()
        return AdapterResult(
            ok=True,
            metadata={
                "command": command,
                "raw_artifact": RAW_SAMPLES_NAME,
                "timestamp_derivation": TIMESTAMP_DERIVATION,
                "readiness": ready.metadata,
            },
        )

    def stop_sampling(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> list[PowerSample]:
        process = self._process
        self._process = None
        capture_path = self._capture_path
        self._capture_path = None
        clock_start_s = self._clock_start_s
        self._clock_start_s = None
        if process is not None:
            self._stop_process(process)
        if capture_path is None or not capture_path.exists():
            return []

        data = capture_path.read_bytes()
        capture_path.unlink(missing_ok=True)
        if context is not None:
            write_raw_artifact(context, RAW_SAMPLES_NAME, data)
        records, diagnostic = _parse_powermetrics_records(
            data, timestamp_anchor_s=clock_start_s
        )
        self._record_parse_diagnostic(
            diagnostic,
            artifact=f"raw/{RAW_SAMPLES_NAME}",
            capture="measured_run",
        )
        if context is not None:
            try:
                rich_data = rich_telemetry_jsonl(data)
            except ValueError as exc:
                self._device_metadata["rich_telemetry_error"] = _terse_error(exc)
            else:
                self._write_rich_artifact(
                    context=context,
                    name=RICH_TELEMETRY_NAME,
                    data=rich_data,
                    error_key="rich_telemetry_error",
                )
        self._remember_records(records, timestamp_anchor_s=clock_start_s)
        return samples_from_records(records)

    def _write_rich_artifact(
        self,
        *,
        context: RunContext,
        name: str,
        data: str,
        error_key: str,
    ) -> None:
        try:
            write_derived_artifact(context, name, data)
        except (BundleError, OSError, ValueError) as exc:
            self._device_metadata[error_key] = _terse_error(exc)

    def _record_parse_diagnostic(
        self,
        diagnostic: _DroppedFrameDiagnostic | None,
        *,
        artifact: str,
        capture: str,
    ) -> None:
        if diagnostic is None:
            return
        entries = self._device_metadata.setdefault("parse_diagnostics", [])
        if isinstance(entries, list):
            entries.append(diagnostic.to_metadata(artifact=artifact, capture=capture))

    def thermal_state(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> ThermalState:
        if self._last_records:
            pressure = self._last_records[-1].thermal_pressure
        else:
            pressure = None
        return ThermalState(
            timestamp_s=self._clock.now(),
            temperature_c=None,
            thermal_pressure=pressure,
            metadata={"source": "powermetrics", "temperature_c_available": False},
        )

    def _ensure_capability(self) -> AdapterResult:
        if self._capability is None:
            self._capability = self._probe_capability()
        return self._capability

    def _probe_capability(self) -> AdapterResult:
        capture_path = self._new_capture_path()
        command = self._probe_command(capture_path)
        try:
            completed = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=15.0,
                check=False,
            )
        except FileNotFoundError as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TELEMETRY_UNAVAILABLE,
                message=f"powermetrics unavailable: {exc}",
            )
        except subprocess.TimeoutExpired as exc:
            capture_path.unlink(missing_ok=True)
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.UNKNOWN_ERROR,
                message=f"powermetrics capability probe timed out: {exc}",
            )

        if completed.returncode != 0:
            stderr = completed.stderr.decode("utf-8", errors="replace").strip()
            capture_path.unlink(missing_ok=True)
            self._device_metadata["capability_precheck"] = {
                "ok": False,
                "failure_reason": FailureReason.PERMISSION_DENIED.value,
                "sudoers_line": sudoers_line(),
            }
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.PERMISSION_DENIED,
                message=(
                    "powermetrics requires passwordless non-interactive sudo. "
                    f"Install this sudoers line: {sudoers_line()}"
                    + (f" (probe stderr: {stderr})" if stderr else "")
                ),
                metadata={"command": command, "returncode": completed.returncode},
            )

        if capture_path.exists():
            try:
                data = capture_path.read_bytes()
                records = parse_powermetrics_records(data)
            except ValueError:
                records = []
            self._remember_records(records)
            capture_path.unlink(missing_ok=True)
        self._device_metadata["capability_precheck"] = {"ok": True}
        return AdapterResult(ok=True, metadata={"command": command})

    def _run_bounded_capture(self, config: BenchmarkConfig, *, count: int) -> bytes:
        capture_path = self._new_capture_path()
        command = self._command(config, capture_path, count=count)
        timeout_s = self._capture_timeout_s(config, count)
        try:
            completed = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_s,
                check=False,
            )
            if completed.returncode != 0:
                stderr = completed.stderr.decode("utf-8", errors="replace").strip()
                raise RuntimeError(f"powermetrics capture failed: {stderr}")
            return capture_path.read_bytes()
        finally:
            capture_path.unlink(missing_ok=True)

    def _remember_records(
        self,
        records: list[PowermetricsRecord],
        *,
        timestamp_anchor_s: float | None = None,
    ) -> None:
        self._last_records = records
        if not records:
            return
        metadata = records[0].metadata
        for key in ("hw_model", "kern_osversion", "kern_bootargs", "kern_boottime"):
            value = metadata.get(key)
            if value is not None:
                self._device_metadata[key] = value
        plist_first_timestamp_s = metadata.get("plist_first_timestamp_s")
        if timestamp_anchor_s is not None and isinstance(plist_first_timestamp_s, float):
            self._device_metadata["plist_anchor_offset_s"] = (
                plist_first_timestamp_s - timestamp_anchor_s
            )

    def _base_device_metadata(self, config: BenchmarkConfig | None) -> dict[str, Any]:
        return {
            "device": config.hardware_target.id if config is not None else None,
            "telemetry": self.name,
            "rail_manifest": list(RAIL_MANIFEST),
            "boundary": "Apple SoC CPU + GPU + ANE package power",
            "timestamp_derivation": TIMESTAMP_DERIVATION,
            "power_units": "powermetrics milliwatts converted to watts",
        }

    @staticmethod
    def _interval_ms(config: BenchmarkConfig) -> int:
        return max(1, int(round(1000.0 / config.sampling.power_hz)))

    def _idle_count(self, config: BenchmarkConfig) -> int:
        interval_s = self._interval_ms(config) / 1000.0
        return max(1, int(math.ceil(config.sampling.idle_seconds / interval_s)))

    def _capture_timeout_s(self, config: BenchmarkConfig, count: int) -> float:
        nominal_s = count * (self._interval_ms(config) / 1000.0)
        return max(15.0, nominal_s * 1.5 + 10.0)

    def _command(
        self,
        config: BenchmarkConfig,
        output_path: Path,
        *,
        count: int | None,
        interval_ms: int | None = None,
    ) -> list[str]:
        command = [
            "sudo",
            "-n",
            POWER_METRICS,
        ]
        if count is not None:
            command.extend(["-n", str(count)])
        command.extend(
            [
                "-b",
                "0",
                "-i",
                str(interval_ms if interval_ms is not None else self._interval_ms(config)),
                "--samplers",
                SAMPLERS,
                "--format",
                "plist",
                "-o",
                str(output_path),
            ]
        )
        return command

    @staticmethod
    def _probe_command(output_path: Path) -> list[str]:
        return [
            "sudo",
            "-n",
            POWER_METRICS,
            "-n",
            "1",
            "-b",
            "0",
            "-i",
            "100",
            "--samplers",
            SAMPLERS,
            "--format",
            "plist",
            "-o",
            str(output_path),
        ]

    @staticmethod
    def _new_capture_path() -> Path:
        handle = tempfile.NamedTemporaryFile(
            prefix="joulewise-powermetrics-", suffix=".plist", delete=False
        )
        path = Path(handle.name)
        handle.close()
        path.unlink(missing_ok=True)
        return path

    @staticmethod
    def _wait_until_ready(
        process: subprocess.Popen[bytes],
        capture_path: Path,
    ) -> AdapterResult:
        deadline = time.monotonic() + READINESS_TIMEOUT_S
        last_parse_error: str | None = None
        while time.monotonic() < deadline:
            if capture_path.exists() and capture_path.stat().st_size > 0:
                data = capture_path.read_bytes()
                first_document = data.split(b"\0", 1)[0]
                if first_document.strip():
                    try:
                        parse_powermetrics_records(first_document)
                    except ValueError as exc:
                        last_parse_error = str(exc)
                    else:
                        return AdapterResult(
                            ok=True,
                            metadata={
                                "ready_bytes": len(data),
                                "ready_check": "first_parseable_plist_document",
                            },
                        )
            if process.poll() is not None:
                return AdapterResult(
                    ok=False,
                    failure_reason=FailureReason.UNKNOWN_ERROR,
                    message=(
                        "powermetrics exited before producing a parseable plist "
                        f"document (returncode {process.returncode})"
                    ),
                    metadata={"last_parse_error": last_parse_error},
                )
            # Operational wait for an external process, deliberately outside the
            # benchmark clock discipline: this delay is excluded from the
            # measured window by D-026 because start_sampling has not returned.
            time.sleep(READINESS_POLL_S)
        return AdapterResult(
            ok=False,
            failure_reason=FailureReason.UNKNOWN_ERROR,
            message=(
                "powermetrics did not produce a parseable plist document within "
                f"{READINESS_TIMEOUT_S} s of launch"
            ),
            metadata={"last_parse_error": last_parse_error},
        )

    @staticmethod
    def _stop_process(process: subprocess.Popen[bytes]) -> None:
        if process.poll() is None:
            process.terminate()
        try:
            process.communicate(timeout=10.0)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()


def parse_powermetrics_records(
    data: bytes, *, timestamp_anchor_s: float | None = None
) -> list[PowermetricsRecord]:
    """Parse a NUL-framed powermetrics plist stream into interval records."""
    records, _diagnostic = _parse_powermetrics_records(
        data, timestamp_anchor_s=timestamp_anchor_s
    )
    return records


def _parse_powermetrics_records(
    data: bytes, *, timestamp_anchor_s: float | None = None
) -> tuple[list[PowermetricsRecord], _DroppedFrameDiagnostic | None]:
    """Parse records and return any final-frame drop diagnostic."""
    documents, diagnostic = _powermetrics_documents(data)
    if not documents:
        raise ValueError("powermetrics stream contains no complete plist documents")

    plist_first_timestamp = _timestamp_epoch_utc(
        _required(documents[0], "timestamp", 0)
    )
    anchor_s = plist_first_timestamp if timestamp_anchor_s is None else timestamp_anchor_s
    cumulative_elapsed_s = 0.0
    records: list[PowermetricsRecord] = []
    for index, document in enumerate(documents):
        elapsed_ns = _required_int(document, "elapsed_ns", index)
        if timestamp_anchor_s is None:
            timestamp_s = anchor_s + cumulative_elapsed_s
            cumulative_elapsed_s += elapsed_ns / 1_000_000_000.0
        else:
            cumulative_elapsed_s += elapsed_ns / 1_000_000_000.0
            timestamp_s = anchor_s + cumulative_elapsed_s
        processor = document.get("processor")
        if not isinstance(processor, dict):
            raise ValueError(
                f"powermetrics document {index} is missing processor dictionary"
            )
        rail_power_w = {
            rail: _required_float(processor, rail, index) / 1000.0
            for rail in RAIL_MANIFEST
        }
        rail_energy_mj = {
            "cpu_energy": _required_int(processor, "cpu_energy", index),
            "gpu_energy": _required_int(processor, "gpu_energy", index),
            "ane_energy": _required_int(processor, "ane_energy", index),
        }
        records.append(
            PowermetricsRecord(
                timestamp_s=timestamp_s,
                elapsed_ns=elapsed_ns,
                rail_power_w=rail_power_w,
                combined_power_w=sum(rail_power_w.values()),
                rail_energy_mj=rail_energy_mj,
                thermal_pressure=_optional_string(document.get("thermal_pressure")),
                metadata={
                    key: document[key]
                    for key in (
                        "hw_model",
                        "kern_osversion",
                        "kern_bootargs",
                        "kern_boottime",
                    )
                    if key in document
                }
                | {"plist_first_timestamp_s": plist_first_timestamp},
            )
        )
    return records, diagnostic


def decode_rich_telemetry(
    data: bytes, *, timestamp_anchor_s: float | None = None
) -> list[dict[str, Any]]:
    """Decode additive per-sample powermetrics fields from a plist stream."""
    documents, _diagnostic = _powermetrics_documents(data)
    if not documents:
        return []

    plist_first_timestamp = _timestamp_epoch_utc(
        _required(documents[0], "timestamp", 0)
    )
    anchor_s = plist_first_timestamp if timestamp_anchor_s is None else timestamp_anchor_s
    cumulative_elapsed_s = 0.0
    rich_records: list[dict[str, Any]] = []
    for index, document in enumerate(documents):
        elapsed_ns = _required_int(document, "elapsed_ns", index)
        if timestamp_anchor_s is None:
            timestamp_s = anchor_s + cumulative_elapsed_s
            cumulative_elapsed_s += elapsed_ns / 1_000_000_000.0
        else:
            cumulative_elapsed_s += elapsed_ns / 1_000_000_000.0
            timestamp_s = anchor_s + cumulative_elapsed_s
        processor = document.get("processor")
        processor_combined_power_w = None
        rail_sum_power_w = None
        combined_delta_w = None
        if isinstance(processor, dict):
            combined_mw = _number_or_none(processor.get("combined_power"))
            if combined_mw is not None:
                processor_combined_power_w = combined_mw / 1000.0
            rail_values = [
                _number_or_none(processor.get(rail)) for rail in RAIL_MANIFEST
            ]
            if all(value is not None for value in rail_values):
                rail_sum_power_w = sum(value for value in rail_values if value is not None) / 1000.0
                if processor_combined_power_w is not None:
                    combined_delta_w = processor_combined_power_w - rail_sum_power_w
        rich_records.append(
            {
                "index": index,
                "timestamp_s": timestamp_s,
                "elapsed_ns": elapsed_ns,
                "gpu": _rich_gpu(document.get("gpu")),
                "clusters": _rich_clusters(processor.get("clusters") if isinstance(processor, dict) else None),
                "processor_combined_power_w": processor_combined_power_w,
                "rail_sum_power_w": rail_sum_power_w,
                "combined_power_delta_w": combined_delta_w,
            }
        )
    return rich_records


def rich_telemetry_jsonl(
    data: bytes, *, timestamp_anchor_s: float | None = None
) -> str:
    return rich_telemetry_jsonl_from_records(
        decode_rich_telemetry(data, timestamp_anchor_s=timestamp_anchor_s)
    )


def rich_telemetry_jsonl_from_records(records: list[dict[str, Any]]) -> str:
    if not records:
        return ""
    return "".join(json.dumps(record, sort_keys=True) + "\n" for record in records)


def idle_window_gpu_quality(records: list[dict[str, Any]]) -> dict[str, float | bool | None]:
    """Return the idle-window GPU quality stats and suspect flag.

    Thresholds are pinned to the fixture and C-004 contamination evidence:
    the clean-ish fixture has min GPU idle_ratio 0.846584 and mean reported GPU
    freq 325.9 MHz, while the observed contaminated idle pattern held the GPU
    near 1363 MHz with low/zero idle_ratio. A single low-idle blip in the
    5-sample fixture is 0.2 of the window and is not suspect; the C-004
    half-window contamination is 0.5 and is suspect.
    """
    idle_ratios: list[float] = []
    freqs: list[float] = []
    for record in records:
        gpu = record.get("gpu")
        if not isinstance(gpu, dict):
            continue
        idle_ratio = _number_or_none(gpu.get("idle_ratio"))
        freq = _number_or_none(gpu.get("freq_hz"))
        if idle_ratio is not None:
            idle_ratios.append(idle_ratio)
        if freq is not None:
            freqs.append(freq)
    if not idle_ratios and not freqs:
        return {
            "gpu_idle_ratio_mean": None,
            "gpu_idle_ratio_min": None,
            "gpu_freq_hz_mean": None,
            "idle_window_suspect": None,
        }
    idle_mean = statistics.mean(idle_ratios) if idle_ratios else None
    idle_min = min(idle_ratios) if idle_ratios else None
    freq_mean = statistics.mean(freqs) if freqs else None
    low_idle_fraction = (
        sum(1 for ratio in idle_ratios if ratio < IDLE_GPU_IDLE_RATIO_THRESHOLD)
        / len(idle_ratios)
        if idle_ratios
        else 0.0
    )
    suspect = (
        (
            idle_ratios
            and low_idle_fraction >= IDLE_GPU_LOW_IDLE_FRACTION_THRESHOLD
        )
        or (
            freq_mean is not None
            and freq_mean > IDLE_GPU_FREQ_MEAN_MHZ_THRESHOLD
        )
    )
    return {
        "gpu_idle_ratio_mean": idle_mean,
        "gpu_idle_ratio_min": idle_min,
        "gpu_freq_hz_mean": freq_mean,
        "idle_window_suspect": suspect,
    }


def samples_from_records(records: list[PowermetricsRecord]) -> list[PowerSample]:
    samples: list[PowerSample] = []
    for record in records:
        for rail in RAIL_MANIFEST:
            samples.append(
                PowerSample(
                    timestamp_s=record.timestamp_s,
                    power_w=record.rail_power_w[rail],
                    source="powermetrics",
                    rail=rail,
                )
            )
    return samples


def _powermetrics_documents(
    data: bytes,
) -> tuple[list[dict[str, Any]], _DroppedFrameDiagnostic | None]:
    documents: list[dict[str, Any]] = []
    parts = [part for part in data.split(b"\0") if part.strip()]
    diagnostic: _DroppedFrameDiagnostic | None = None
    for index, part in enumerate(parts):
        try:
            document = plistlib.loads(part)
        except (ExpatError, plistlib.InvalidFileException, ValueError, TypeError) as exc:
            message = f"powermetrics document {index} is not a valid plist: {exc}"
            if index == len(parts) - 1 and documents:
                diagnostic = _DroppedFrameDiagnostic(
                    frame_index=index,
                    byte_count=len(part),
                    sha256=hashlib.sha256(part).hexdigest(),
                    error=message,
                )
                break
            raise ValueError(message) from exc
        if not isinstance(document, dict):
            message = f"powermetrics document {index} is not a dictionary"
            if index == len(parts) - 1 and documents:
                diagnostic = _DroppedFrameDiagnostic(
                    frame_index=index,
                    byte_count=len(part),
                    sha256=hashlib.sha256(part).hexdigest(),
                    error=message,
                )
                break
            raise ValueError(message)
        documents.append(document)
    return documents, diagnostic


def _rich_gpu(value: object) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    dvfm_states = _state_entries(value.get("dvfm_states"), ("freq", "used_ns", "used_ratio"))
    # powermetrics labels this GPU field freq_hz, but observed Apple GPU values
    # are reported in MHz; cluster/core freq_hz values are reported in Hz.
    return {
        "freq_hz": _number_or_none(value.get("freq_hz")),
        "idle_ratio": _number_or_none(value.get("idle_ratio")),
        "idle_ns": _int_or_none(value.get("idle_ns")),
        "gpu_energy": _int_or_none(value.get("gpu_energy")),
        "active_freq_mhz_weighted": _weighted_freq(dvfm_states),
        "dvfm_states": dvfm_states,
        "sw_state": _state_entries(value.get("sw_state"), ("sw_state", "used_ns", "used_ratio")),
        "sw_requested_state": _state_entries(
            value.get("sw_requested_state"),
            ("sw_req_state", "used_ns", "used_ratio"),
        ),
    }


def _rich_clusters(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    clusters = []
    for item in value:
        if not isinstance(item, dict):
            continue
        clusters.append(
            {
                "name": _optional_string(item.get("name")),
                # Unlike GPU freq_hz, cluster/core freq_hz values are reported
                # in Hz; preserve every frequency field verbatim.
                "freq_hz": _number_or_none(item.get("freq_hz")),
                "idle_ratio": _number_or_none(item.get("idle_ratio")),
                "down_ratio": _number_or_none(item.get("down_ratio")),
                "online_ratio": _number_or_none(item.get("online_ratio")),
                "dvfm_states": _state_entries(
                    item.get("dvfm_states"),
                    ("freq", "used_ns", "used_ratio"),
                ),
                "cpus": _rich_cpus(item.get("cpus")),
            }
        )
    return clusters


def _rich_cpus(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    cpus = []
    for item in value:
        if not isinstance(item, dict):
            continue
        cpus.append(
            {
                "cpu": _int_or_none(item.get("cpu")),
                "freq_hz": _number_or_none(item.get("freq_hz")),
                "idle_ratio": _number_or_none(item.get("idle_ratio")),
                "down_ratio": _number_or_none(item.get("down_ratio")),
                "online_ratio": _number_or_none(item.get("online_ratio")),
            }
        )
    return cpus


def _state_entries(value: object, keys: tuple[str, ...]) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    entries = []
    for item in value:
        if not isinstance(item, dict):
            continue
        entry = {
            key: _json_scalar(item[key])
            for key in keys
            if key in item and _json_scalar(item[key]) is not None
        }
        if entry:
            entries.append(entry)
    return entries


def _weighted_freq(states: list[dict[str, Any]]) -> float | None:
    weighted = 0.0
    total = 0.0
    for state in states:
        freq = _number_or_none(state.get("freq"))
        ratio = _number_or_none(state.get("used_ratio"))
        if freq is None or ratio is None:
            continue
        weighted += freq * ratio
        total += ratio
    if total <= 0:
        return None
    return weighted / total


def _json_scalar(value: object) -> str | int | float | bool | None:
    if isinstance(value, bool | str | int | float) or value is None:
        return value
    return None


def _terse_error(exc: Exception) -> str:
    message = str(exc).strip()
    if not message:
        return type(exc).__name__
    return f"{type(exc).__name__}: {message}"


def sudoers_line() -> str:
    return f"{getpass.getuser()} ALL=(root) NOPASSWD: {POWER_METRICS}"


def _timestamp_epoch_utc(value: object) -> float:
    if not isinstance(value, datetime):
        raise ValueError(f"powermetrics timestamp is not a datetime: {value!r}")
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.timestamp()


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _number_or_none(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _int_or_none(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return int(value)
    return None


def _required(mapping: dict[str, Any], key: str, document_index: int) -> Any:
    try:
        return mapping[key]
    except KeyError as exc:
        raise ValueError(
            f"powermetrics document {document_index} is missing key {key!r}"
        ) from exc


def _required_int(mapping: dict[str, Any], key: str, document_index: int) -> int:
    value = _required(mapping, key, document_index)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"powermetrics document {document_index} key {key!r} is not an integer: "
            f"{value!r}"
        ) from exc


def _required_float(mapping: dict[str, Any], key: str, document_index: int) -> float:
    value = _required(mapping, key, document_index)
    try:
        return finite_float(value, f"powermetrics document {document_index} key {key!r}")
    except ValueError as exc:
        raise ValueError(
            f"powermetrics document {document_index} key {key!r} is not a finite number: "
            f"{value!r}"
        ) from exc
