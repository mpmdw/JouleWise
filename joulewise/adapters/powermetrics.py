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
from joulewise.clock import Clock, ClockStamp
from joulewise.interfaces import (
    AdapterFailure,
    AdapterResult,
    DurableCustodyAcknowledgement,
    PowerSample,
    RunContext,
    TelemetryStopResult,
    ThermalState,
)
from joulewise.schemas import BenchmarkConfig, FailureReason, IdleBaseline, TelemetryBackend
from joulewise.validation import finite_float
from joulewise.uncertainty_evidence import (
    derive_idle_drift_evidence,
    derive_powermetrics_clock_evidence,
    unknown_component,
)

POWER_METRICS = "/usr/bin/powermetrics"
RAW_SAMPLES_NAME = "powermetrics.plist"
RAW_IDLE_NAME = "powermetrics_idle.plist"
RAW_IDLE_POST_NAME = "powermetrics_idle_post.plist"
RICH_TELEMETRY_NAME = "rich_telemetry.jsonl"
RICH_IDLE_NAME = "rich_telemetry_idle.jsonl"
RICH_IDLE_POST_NAME = "rich_telemetry_idle_post.jsonl"
RAIL_MANIFEST = ["cpu_power", "gpu_power", "ane_power"]
SAMPLERS = "cpu_power,gpu_power,ane_power,thermal"
READINESS_TIMEOUT_S = 15.0
READINESS_POLL_S = 0.05
POST_MARKER_DRAIN_MARGIN_S = 0.25
POST_MARKER_DRAIN_POLL_S = 0.05
IDLE_GPU_IDLE_RATIO_THRESHOLD = 0.80
IDLE_GPU_LOW_IDLE_FRACTION_THRESHOLD = 0.40
IDLE_GPU_FREQ_MEAN_MHZ_THRESHOLD = 800.0
TIMESTAMP_DERIVATION = (
    "current-era timestamp_s uses the midpoint of a controller-monotonic "
    "pre-spawn/first-parse bracket mapped through the run wall-minus-monotonic "
    "envelope; record 0 is that interval endpoint and records i>0 advance by "
    "elapsed_ns for records 1..i. Whole-second plist dates are consistency-only. "
    "Exact allowlisted legacy bundles retain plist_anchor_offset_s plus the "
    "legacy cumulative-elapsed reconstruction. Each emitted sample carries "
    "its [endpoint-elapsed_ns, endpoint) averaging support."
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

    def __init__(
        self,
        clock: Clock,
        *,
        executable: str = POWER_METRICS,
        privilege_prefix: tuple[str, ...] = ("sudo", "-n"),
    ) -> None:
        self._clock = clock
        self._executable = executable
        self._privilege_prefix = tuple(privilege_prefix)
        self._process: subprocess.Popen[bytes] | None = None
        self._capture_path: Path | None = None
        self._clock_start_s: float | None = None
        self._pre_spawn_stamp: ClockStamp | None = None
        self._first_parse_stamp: ClockStamp | None = None
        self._device_metadata = self._base_device_metadata(None)
        self._capability: AdapterResult | None = None
        self._last_records: list[PowermetricsRecord] = []
        self._pre_idle_records: list[PowermetricsRecord] = []
        self._pre_idle_quality: dict[str, float | bool | None] | None = None
        self._pending_captures: dict[str, Path] = {}

    def device_metadata(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> dict:
        powermetrics = self._device_metadata.get("powermetrics")
        self._device_metadata.update(self._base_device_metadata(config))
        if isinstance(powermetrics, dict) and powermetrics.get("samplers_probe", {}).get("reason") != "not_probed":
            self._device_metadata["powermetrics"] = powermetrics
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
        data = self._run_bounded_capture(
            config,
            count=count,
            artifact_name=RAW_IDLE_NAME,
            context=context,
        )
        if context is not None:
            self._persist_capture(context, RAW_IDLE_NAME, data)
        self._release_capture(RAW_IDLE_NAME)
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
        intervals_s = [record.elapsed_ns / 1_000_000_000.0 for record in records]
        duration_s = math.fsum(intervals_s)
        if len(totals) > 1:
            idle_mean_w, idle_variance_w2 = duration_weighted_mean_and_sample_variance(
                totals, intervals_s
            )
        else:
            idle_mean_w = totals[0] if totals else 0.0
            idle_variance_w2 = 0.0
        idle_quality = idle_window_gpu_quality(rich_records)
        self._pre_idle_records = list(records)
        self._pre_idle_quality = dict(idle_quality)
        return IdleBaseline(
            power_w_mean=idle_mean_w,
            power_w_stddev=math.sqrt(idle_variance_w2),
            duration_s=duration_s,
            sample_count=len(totals),
            telemetry_backend=TelemetryBackend.POWERMETRICS,
            gpu_idle_ratio_mean=idle_quality["gpu_idle_ratio_mean"],
            gpu_idle_ratio_min=idle_quality["gpu_idle_ratio_min"],
            gpu_freq_mhz_mean=idle_quality["gpu_freq_mhz_mean"],
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
        self._pending_captures[RAW_SAMPLES_NAME] = self._capture_path
        self._pre_spawn_stamp = None
        self._first_parse_stamp = None
        command = self._command(
            config,
            self._capture_path,
            count=None,
            interval_ms=self._interval_ms(config),
        )
        pre_spawn_stamp = self._clock.stamp()
        self._pre_spawn_stamp = pre_spawn_stamp
        try:
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError as exc:
            self._release_capture(RAW_SAMPLES_NAME)
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TELEMETRY_UNAVAILABLE,
                message=f"powermetrics launcher unavailable: {exc}",
            )
        ready = self._wait_until_ready(self._process, self._capture_path)
        if not ready.ok:
            self._stop_process(self._process)
            self._process = None
            if context is None:
                self._release_capture(RAW_SAMPLES_NAME)
            return ready
        if self._first_parse_stamp is None:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.UNKNOWN_ERROR,
                message="powermetrics readiness completed without a paired clock stamp",
            )
        self._clock_start_s = self._first_parse_stamp.epoch_s
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
        """Compatibility stop path used by non-controller callers and legacy tests."""

        data, clock_start_s = self._take_measured_capture()
        if data is None:
            return []
        if context is not None:
            self._persist_capture(context, RAW_SAMPLES_NAME, data)
        records, diagnostic = _parse_powermetrics_records(
            data, timestamp_anchor_s=clock_start_s
        )
        self._preserve_measured_capture(data, records, diagnostic, context)
        self._release_capture(RAW_SAMPLES_NAME)
        return samples_from_records(records)

    def stop_sampling_with_evidence(
        self,
        config: BenchmarkConfig,
        context: RunContext | None,
        *,
        sampling_started: ClockStamp,
        sampling_stopped: ClockStamp,
    ) -> TelemetryStopResult:
        """Stop the real sampler and derive current-era clock/phase evidence."""

        try:
            self._drain_until_stop_bracket(
                config,
                sampling_started=sampling_started,
                sampling_stopped=sampling_stopped,
            )
        finally:
            data, _ = self._take_measured_capture()
        if data is None:
            evidence, _ = derive_powermetrics_clock_evidence(
                stamps={}, elapsed_s=[], plist_timestamp_s=[]
            )
            return TelemetryStopResult([], evidence)
        if context is not None:
            self._persist_capture(context, RAW_SAMPLES_NAME, data)
        native_records, diagnostic = _parse_powermetrics_records(data)
        post_parse_stamp = self._clock.stamp()
        stamps: dict[str, ClockStamp] = {
            "sampling_started": sampling_started,
            "sampling_stopped": sampling_stopped,
            "post_parse": post_parse_stamp,
        }
        if self._pre_spawn_stamp is not None:
            stamps["pre_spawn"] = self._pre_spawn_stamp
        if self._first_parse_stamp is not None:
            stamps["first_parse"] = self._first_parse_stamp
        evidence, point_anchor_s = derive_powermetrics_clock_evidence(
            stamps=stamps,
            elapsed_s=[record.elapsed_ns / 1_000_000_000.0 for record in native_records],
            plist_timestamp_s=[
                float(record.metadata["plist_timestamp_s"])
                for record in native_records
            ],
        )
        records = (
            parse_powermetrics_records(data, first_record_endpoint_s=point_anchor_s)
            if point_anchor_s is not None
            else native_records
        )
        self._preserve_measured_capture(data, records, diagnostic, context)
        self._release_capture(RAW_SAMPLES_NAME)
        return TelemetryStopResult(samples_from_records(records), evidence)

    def _drain_until_stop_bracket(
        self,
        config: BenchmarkConfig,
        *,
        sampling_started: ClockStamp,
        sampling_stopped: ClockStamp,
    ) -> None:
        """Bound sampler wind-down by a right-edge sample or two missed intervals."""

        process = self._process
        capture_path = self._capture_path
        if process is None or capture_path is None:
            return
        timeout_s = 2.0 / config.sampling.power_hz + POST_MARKER_DRAIN_MARGIN_S
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline and process.poll() is None:
            if self._capture_brackets_stop(
                capture_path,
                deadline=deadline,
                sampling_started=sampling_started,
                sampling_stopped=sampling_stopped,
            ):
                return
            remaining_s = deadline - time.monotonic()
            if remaining_s <= 0.0:
                return
            # This wait is after the sampling_stopped marker. It only lets the
            # native stream provide the right-edge interval; reducer windows
            # remain marker-bounded and exclude support after that timestamp.
            time.sleep(min(POST_MARKER_DRAIN_POLL_S, remaining_s))

    def _capture_brackets_stop(
        self,
        capture_path: Path,
        *,
        deadline: float,
        sampling_started: ClockStamp,
        sampling_stopped: ClockStamp,
    ) -> bool:
        if time.monotonic() >= deadline:
            return False
        if not capture_path.exists() or capture_path.stat().st_size == 0:
            return False
        if time.monotonic() >= deadline:
            return False
        try:
            data = capture_path.read_bytes()
        except (OSError, ValueError):
            return False
        if time.monotonic() >= deadline:
            return False
        try:
            native_records = parse_powermetrics_records(data)
        except (OSError, ValueError):
            return False
        if time.monotonic() >= deadline:
            return False
        stamps: dict[str, ClockStamp] = {
            "sampling_started": sampling_started,
            "sampling_stopped": sampling_stopped,
            # The final evidence derivation still takes its post_parse stamp
            # after termination. Reusing the stop stamp here is provisional
            # and avoids changing the five-stamp evidence semantics.
            "post_parse": sampling_stopped,
        }
        if self._pre_spawn_stamp is not None:
            stamps["pre_spawn"] = self._pre_spawn_stamp
        if self._first_parse_stamp is not None:
            stamps["first_parse"] = self._first_parse_stamp
        elapsed_s = [
            record.elapsed_ns / 1_000_000_000.0 for record in native_records
        ]
        if time.monotonic() >= deadline:
            return False
        plist_timestamp_s = [
            float(record.metadata["plist_timestamp_s"]) for record in native_records
        ]
        if time.monotonic() >= deadline:
            return False
        _evidence, point_anchor_s = derive_powermetrics_clock_evidence(
            stamps=stamps,
            elapsed_s=elapsed_s,
            plist_timestamp_s=plist_timestamp_s,
        )
        if time.monotonic() >= deadline:
            return False
        if point_anchor_s is None:
            return False
        last_endpoint_s = point_anchor_s + math.fsum(
            record.elapsed_ns / 1_000_000_000.0
            for record in native_records[1:]
        )
        return last_endpoint_s >= sampling_stopped.epoch_s

    def _take_measured_capture(self) -> tuple[bytes | None, float | None]:
        process = self._process
        self._process = None
        capture_path = self._capture_path
        clock_start_s = self._clock_start_s
        if process is not None:
            self._stop_process(process)
        if capture_path is None or not capture_path.exists():
            return None, clock_start_s

        data = capture_path.read_bytes()
        return data, clock_start_s

    def _release_capture(self, artifact_name: str) -> None:
        capture_path = self._pending_captures.pop(artifact_name, None)
        if capture_path is not None:
            capture_path.unlink(missing_ok=True)
        if artifact_name == RAW_SAMPLES_NAME:
            self._capture_path = None
            self._clock_start_s = None
            self._pre_spawn_stamp = None
            self._first_parse_stamp = None

    def salvage_custody(self, context: RunContext) -> list[dict[str, Any]]:
        """Retry every native capture write before releasing its source file."""

        report: list[dict[str, Any]] = []
        for artifact_name, capture_path in list(self._pending_captures.items()):
            if not capture_path.exists():
                continue
            try:
                self._persist_capture(
                    context,
                    artifact_name,
                    capture_path.read_bytes(),
                )
            except Exception as exc:  # noqa: BLE001 - try every independent capture
                report.append(
                    {
                        "artifact": artifact_name,
                        "source": str(capture_path),
                        "acknowledged": False,
                        "error": "%s: %s" % (type(exc).__name__, exc),
                    }
                )
                continue
            self._release_capture(artifact_name)
            report.append(
                {
                    "artifact": artifact_name,
                    "source": str(capture_path),
                    "acknowledged": True,
                    "error": None,
                }
            )
        return report

    def _persist_capture(
        self,
        context: RunContext,
        artifact_name: str,
        data: bytes,
    ) -> DurableCustodyAcknowledgement:
        """Write, fsync-acknowledge, then permit native-capture release."""

        destination = context.raw_dir / artifact_name
        if destination.exists():
            if destination.read_bytes() != data:
                raise BundleError(
                    "existing raw artifact does not match retained native capture: "
                    f"{destination}"
                )
        else:
            write_raw_artifact(context, artifact_name, data)
        token = self._custody_token(artifact_name)
        acknowledgement = context.acknowledge_custody(token, [destination])
        if not self._acknowledgement_is_valid(
            acknowledgement,
            token=token,
            destination=destination,
            bundle_path=context.bundle_path,
        ):
            raise RuntimeError("powermetrics custody acknowledgement is invalid")
        return acknowledgement

    @staticmethod
    def _custody_token(artifact_name: str) -> str:
        safe_name = "".join(
            character if character.isalnum() else "_"
            for character in artifact_name
        )
        return f"powermetrics-{safe_name}"

    @staticmethod
    def _acknowledgement_is_valid(
        acknowledgement: DurableCustodyAcknowledgement,
        *,
        token: str,
        destination: Path,
        bundle_path: Path,
    ) -> bool:
        try:
            payload = json.loads(
                acknowledgement.acknowledgement_path.read_text(encoding="utf-8")
            )
            acknowledgement.acknowledgement_path.resolve().relative_to(
                bundle_path.resolve()
            )
        except (OSError, ValueError, json.JSONDecodeError):
            return False
        return (
            acknowledgement.token == token
            and payload.get("custody_token") == token
            and destination.resolve()
            in {path.resolve() for path in acknowledgement.artifact_paths}
            and destination.is_file()
        )

    def _preserve_measured_capture(
        self,
        data: bytes,
        records: list[PowermetricsRecord],
        diagnostic: _DroppedFrameDiagnostic | None,
        context: RunContext | None,
    ) -> None:
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
        self._remember_records(records)

    def measure_post_run_idle(
        self,
        config: BenchmarkConfig,
        baseline: IdleBaseline,
        context: RunContext | None,
    ) -> dict[str, Any]:
        """Collect the adjudicated short idle sentinel outside the window."""

        interval_s = self._interval_ms(config) / 1000.0
        duration_s = max(3.0 * interval_s, min(5.0, baseline.duration_s))
        count = max(3, int(math.ceil(duration_s / interval_s)))
        try:
            data = self._run_bounded_capture(
                config,
                count=count,
                artifact_name=RAW_IDLE_POST_NAME,
                context=context,
            )
            records, diagnostic = _parse_powermetrics_records(
                data, timestamp_anchor_s=self._clock.now()
            )
            rich_records = decode_rich_telemetry(data)
        except Exception:  # noqa: BLE001 - evidence failure must preserve L0/L1
            return {
                "idle_drift": unknown_component("post_idle_unavailable"),
            }
        if context is not None:
            self._persist_capture(context, RAW_IDLE_POST_NAME, data)
            self._write_rich_artifact(
                context=context,
                name=RICH_IDLE_POST_NAME,
                data=rich_telemetry_jsonl_from_records(rich_records),
                error_key="rich_telemetry_idle_post_error",
            )
        self._release_capture(RAW_IDLE_POST_NAME)
        self._record_parse_diagnostic(
            diagnostic,
            artifact=f"raw/{RAW_IDLE_POST_NAME}",
            capture="post_run_idle",
        )
        post_quality = idle_window_gpu_quality(rich_records)
        pre_quality = self._pre_idle_quality or {}
        evidence, guard, bound_w = derive_idle_drift_evidence(
            pre_power_w=[record.combined_power_w for record in self._pre_idle_records],
            post_power_w=[record.combined_power_w for record in records],
            pre_power_w_mean=baseline.power_w_mean,
            pre_idle_window_suspect=pre_quality.get("idle_window_suspect"),
            post_idle_window_suspect=post_quality["idle_window_suspect"],
        )
        result: dict[str, Any] = {
            "idle_drift": evidence,
            "idle_drift_guard": guard,
            "post_idle_duration_requested_s": duration_s,
        }
        if bound_w is not None:
            result["idle_drift_bound_w"] = bound_w
        self._last_records = records
        return result

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
            self._record_sampler_probe_unavailable("not_found")
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TELEMETRY_UNAVAILABLE,
                message=f"powermetrics unavailable: {exc}",
            )
        except subprocess.TimeoutExpired as exc:
            capture_path.unlink(missing_ok=True)
            self._record_sampler_probe_unavailable("timeout")
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
            self._record_sampler_probe_unavailable(
                f"returncode_{completed.returncode}"
            )
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
        self._device_metadata["powermetrics"]["samplers_available"] = SAMPLERS.split(",")
        self._device_metadata["powermetrics"]["samplers_probe"] = {
            "ok": True,
            "method": "requested_sampler_probe",
        }
        return AdapterResult(ok=True, metadata={"command": command})

    def _run_bounded_capture(
        self,
        config: BenchmarkConfig,
        *,
        count: int,
        artifact_name: str,
        context: RunContext | None,
    ) -> bytes:
        capture_path = self._new_capture_path()
        self._pending_captures[artifact_name] = capture_path
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
        except BaseException:
            if context is None:
                self._release_capture(artifact_name)
            raise

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
            "powermetrics": {
                "samplers_requested": SAMPLERS,
                "samplers_available": "probe-unavailable",
                "samplers_probe": {"ok": False, "reason": "not_probed"},
            },
        }

    def _record_sampler_probe_unavailable(self, reason: str) -> None:
        powermetrics = self._device_metadata.setdefault("powermetrics", {})
        if isinstance(powermetrics, dict):
            powermetrics["samplers_available"] = "probe-unavailable"
            powermetrics["samplers_probe"] = {"ok": False, "reason": reason}

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
        command = [*self._privilege_prefix, self._executable]
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

    def _probe_command(self, output_path: Path) -> list[str]:
        return [
            *self._privilege_prefix,
            self._executable,
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

    def _wait_until_ready(
        self,
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
                        self._first_parse_stamp = self._clock.stamp()
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
    data: bytes,
    *,
    timestamp_anchor_s: float | None = None,
    first_record_endpoint_s: float | None = None,
) -> list[PowermetricsRecord]:
    """Parse a NUL-framed powermetrics plist stream into interval records."""
    records, _diagnostic = _parse_powermetrics_records(
        data,
        timestamp_anchor_s=timestamp_anchor_s,
        first_record_endpoint_s=first_record_endpoint_s,
    )
    return records


def samples_from_raw_powermetrics(
    data: bytes,
    *,
    plist_anchor_offset_s: float | None = None,
    first_record_endpoint_s: float | None = None,
) -> list[PowerSample]:
    """Re-derive ``power_trace.csv`` samples from raw powermetrics evidence.

    ``plist_anchor_offset_s`` is the recorded evidence
    ``plist_first_timestamp_s - timestamp_anchor_s``. The artifact under test
    is never used to infer the anchor.
    """
    if (plist_anchor_offset_s is None) == (first_record_endpoint_s is None):
        raise ValueError(
            "exactly one raw-to-trace anchor mode is required: legacy "
            "plist_anchor_offset_s or current first_record_endpoint_s"
        )
    if first_record_endpoint_s is not None:
        endpoint_s = finite_float(
            first_record_endpoint_s,
            "metadata.uncertainty_evidence.clock_anchor.first_sample_end_point_epoch_s",
        )
        return samples_from_records(
            parse_powermetrics_records(data, first_record_endpoint_s=endpoint_s)
        )
    offset_s = finite_float(
        plist_anchor_offset_s,
        "metadata.device.plist_anchor_offset_s",
    )
    raw_anchor_records = parse_powermetrics_records(data)
    first_timestamp_s = raw_anchor_records[0].metadata["plist_first_timestamp_s"]
    timestamp_anchor_s = first_timestamp_s - offset_s
    return samples_from_records(parse_powermetrics_records(data, timestamp_anchor_s=timestamp_anchor_s))


def _parse_powermetrics_records(
    data: bytes,
    *,
    timestamp_anchor_s: float | None = None,
    first_record_endpoint_s: float | None = None,
) -> tuple[list[PowermetricsRecord], _DroppedFrameDiagnostic | None]:
    """Parse records and return any final-frame drop diagnostic."""
    if timestamp_anchor_s is not None and first_record_endpoint_s is not None:
        raise ValueError("powermetrics timestamp anchor modes are mutually exclusive")
    documents, diagnostic = _powermetrics_documents(data)
    if not documents:
        raise ValueError("powermetrics stream contains no complete plist documents")

    plist_first_timestamp = _timestamp_epoch_utc(
        _required(documents[0], "timestamp", 0)
    )
    anchor_s = plist_first_timestamp if timestamp_anchor_s is None else timestamp_anchor_s
    if first_record_endpoint_s is not None:
        anchor_s = finite_float(first_record_endpoint_s, "first_record_endpoint_s")
    cumulative_elapsed_s = 0.0
    records: list[PowermetricsRecord] = []
    for index, document in enumerate(documents):
        elapsed_ns = _required_int(document, "elapsed_ns", index)
        if first_record_endpoint_s is not None:
            if index > 0:
                cumulative_elapsed_s += elapsed_ns / 1_000_000_000.0
            timestamp_s = anchor_s + cumulative_elapsed_s
        elif timestamp_anchor_s is None:
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
                | {
                    "plist_first_timestamp_s": plist_first_timestamp,
                    "plist_timestamp_s": _timestamp_epoch_utc(
                        _required(document, "timestamp", index)
                    ),
                },
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
            "gpu_freq_mhz_mean": None,
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
        "gpu_freq_mhz_mean": freq_mean,
        # Deprecated legacy alias: preserve the historical MHz-valued number
        # under its old false-Hz name so stored eras remain distinguishable.
        "gpu_freq_hz_mean": freq_mean,
        "idle_window_suspect": suspect,
    }


def samples_from_records(records: list[PowermetricsRecord]) -> list[PowerSample]:
    samples: list[PowerSample] = []
    for record in records:
        interval_end_s = record.timestamp_s
        interval_start_s = interval_end_s - record.elapsed_ns / 1_000_000_000.0
        for rail in RAIL_MANIFEST:
            samples.append(
                PowerSample(
                    timestamp_s=record.timestamp_s,
                    power_w=record.rail_power_w[rail],
                    source="powermetrics",
                    rail=rail,
                    interval_start_s=interval_start_s,
                    interval_end_s=interval_end_s,
                )
            )
    return samples


def duration_weighted_mean_and_sample_variance(
    values: list[float] | tuple[float, ...],
    durations_s: list[float] | tuple[float, ...],
) -> tuple[float, float]:
    """Return the WO-005 duration-weighted mean and sample variance.

    Durations are reliability weights. The variance denominator ``1-q``
    makes equal-duration inputs reduce to the ordinary sample variance.
    """
    if len(values) != len(durations_s) or len(values) < 2:
        raise ValueError("duration weighting requires equally sized inputs of length >= 2")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("duration-weighted values must be finite")
    if any(not math.isfinite(duration) or duration <= 0.0 for duration in durations_s):
        raise ValueError("duration weights must be finite and > 0")
    total_duration_s = math.fsum(durations_s)
    weights = tuple(duration / total_duration_s for duration in durations_s)
    mean = math.fsum(weight * value for weight, value in zip(weights, values, strict=True))
    q = math.fsum(weight * weight for weight in weights)
    if q >= 1.0:
        raise ValueError("duration-weighted sample variance requires effective count > 1")
    variance = math.fsum(
        weight * (value - mean) * (value - mean)
        for weight, value in zip(weights, values, strict=True)
    ) / (1.0 - q)
    return mean, variance


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
