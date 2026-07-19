"""Read-only machine and configuration preflight for JouleWise campaigns.

The live probe layer only reads files, filesystem statistics, and unprivileged
command output.  In particular, the sudo probe uses ``sudo -n -l`` to inspect
policy; it never launches ``powermetrics`` and never changes sudoers state.
The report builder accepts a complete probe fixture so tests need no host
access and downstream callers can reuse the config-warning gate independently.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import warnings
from dataclasses import dataclass
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Sequence

from joulewise.adapters.powermetrics import POWER_METRICS, SAMPLERS
from joulewise.environment import (
    collect_environment_snapshot,
    evaluate_environment_policy,
)
from joulewise.schemas import BenchmarkConfig, ConfigKeyWarning


SCHEMA_VERSION = "joulewise.doctor.v1"
CHECK_ORDER = (
    "config",
    "versions_arch",
    "model_tokenizer_identity",
    "powermetrics",
    "samplers",
    "thermal_pressure",
    "backup_destination",
    "quiet_machine",
)
STATUS_ORDER = {"pass": 0, "warn": 1, "fail": 2}
MIN_BACKUP_FREE_BYTES = 10 * 1024**3
COMMAND_TIMEOUT_S = 3.0


@dataclass(frozen=True)
class DoctorProbeFixture:
    """All machine-derived values consumed by :func:`build_doctor_report`."""

    python_version: str
    os_name: str
    os_version: str
    architecture: str
    hardware_model: str | None
    cpu_brand: str | None
    logical_cpu_count: int | None
    package_versions: dict[str, dict[str, str | bool | None]]
    powermetrics_path: str
    powermetrics_present: bool
    powermetrics_executable: bool
    sudo_probe_ok: bool
    sudo_probe_reason: str | None
    thermal_pressure: str | None
    thermal_probe_reason: str | None
    backup_destination: str | None
    backup_present: bool | None
    backup_free_bytes: int | None
    backup_probe_reason: str | None
    power_source: str | None
    low_power_mode: bool | None
    load_average_1m: float | None
    display_active_count: int | None
    environment_errors: dict[str, str]
    external_connected: bool | None = None
    display_power_state: str | None = None
    screensaver_engaged: bool | None = None
    screensaver_module: str | None = None
    screensaver_delay_s: float | None = None
    hid_idle_s: float | None = None


def _package_version(distribution: str) -> dict[str, str | bool | None]:
    try:
        return {"present": True, "version": importlib_metadata.version(distribution)}
    except importlib_metadata.PackageNotFoundError:
        return {"present": False, "version": None}
    except Exception as exc:  # noqa: BLE001 - doctor is best-effort and read-only
        return {
            "present": False,
            "version": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _sudo_policy_probe(
    powermetrics_path: str, timeout_s: float
) -> tuple[bool, str | None]:
    """Inspect non-interactive sudo policy without running a privileged tool."""
    try:
        completed = subprocess.run(
            ["sudo", "-n", "-l", powermetrics_path],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except FileNotFoundError:
        return False, "sudo_not_found"
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception:  # noqa: BLE001 - live doctor probes never raise
        return False, "probe_failed"
    if completed.returncode == 0:
        return True, None
    return False, f"returncode_{completed.returncode}"


def collect_live_probe(
    backup_destination: Path | None,
    *,
    timeout_s: float = COMMAND_TIMEOUT_S,
) -> DoctorProbeFixture:
    """Collect a non-mutating best-effort machine snapshot."""
    environment = collect_environment_snapshot(timeout_s=timeout_s)
    powermetrics = Path(POWER_METRICS)
    present = powermetrics.is_file()
    executable = present and os.access(powermetrics, os.X_OK)
    if present:
        sudo_ok, sudo_reason = _sudo_policy_probe(str(powermetrics), timeout_s)
    else:
        sudo_ok, sudo_reason = False, "powermetrics_not_found"

    thermal_pressure = environment.get("thermal_pressure")
    thermal_reason = environment.get("thermal_probe_reason")

    destination_text = str(backup_destination) if backup_destination is not None else None
    backup_present: bool | None = None
    backup_free_bytes: int | None = None
    backup_reason: str | None = "not_configured"
    if backup_destination is not None:
        backup_present = backup_destination.is_dir()
        if not backup_present:
            backup_reason = "not_found"
        else:
            try:
                backup_free_bytes = shutil.disk_usage(backup_destination).free
                backup_reason = None
            except OSError as exc:
                backup_reason = f"{type(exc).__name__}: {exc}"

    display = environment.get("display", {})
    packages = dict(environment.get("python_packages", {}))
    packages["joulewise"] = _package_version("joulewise")
    return DoctorProbeFixture(
        python_version=platform.python_version(),
        os_name=str(environment.get("product_name") or platform.system()),
        os_version=str(environment.get("product_version") or platform.release()),
        architecture=platform.machine(),
        hardware_model=environment.get("hw_model"),
        cpu_brand=environment.get("cpu_brand"),
        logical_cpu_count=environment.get("logical_cpu_count"),
        package_versions=packages,
        powermetrics_path=str(powermetrics),
        powermetrics_present=present,
        powermetrics_executable=executable,
        sudo_probe_ok=sudo_ok,
        sudo_probe_reason=sudo_reason,
        thermal_pressure=thermal_pressure,
        thermal_probe_reason=thermal_reason,
        backup_destination=destination_text,
        backup_present=backup_present,
        backup_free_bytes=backup_free_bytes,
        backup_probe_reason=backup_reason,
        power_source=environment.get("power_source"),
        low_power_mode=environment.get("low_power_mode"),
        load_average_1m=environment.get("load_average_1m"),
        display_active_count=(
            display.get("active_displays") if isinstance(display, dict) else None
        ),
        environment_errors=dict(environment.get("errors", {})),
        external_connected=(
            environment.get("power", {}).get("external_connected")
            if isinstance(environment.get("power"), dict)
            else None
        ),
        display_power_state=environment.get("display_power_state"),
        screensaver_engaged=environment.get("screensaver_engaged"),
        screensaver_module=environment.get("screensaver_module"),
        screensaver_delay_s=environment.get("screensaver_delay_s"),
        hid_idle_s=environment.get("hid_idle_s"),
    )


def inspect_configs(config_paths: Sequence[Path]) -> dict[str, Any]:
    """Read and validate configs, retaining stable machine-readable warnings."""
    configs: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    warning_rows: list[dict[str, str]] = []
    for path in sorted(config_paths, key=lambda item: str(item)):
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(
                {"config": str(path), "message": f"failed to read config {path}: {exc}"}
            )
            continue
        try:
            raw = json.loads(source)
        except json.JSONDecodeError as exc:
            errors.append(
                {
                    "config": str(path),
                    "message": f"config is not valid JSON: {path}: {exc}",
                }
            )
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConfigKeyWarning)
                config = BenchmarkConfig.from_mapping(raw)
        except Exception as exc:  # noqa: BLE001 - report all config failures together
            errors.append(
                {
                    "config": str(path),
                    "message": f"{type(exc).__name__}: {exc}",
                }
            )
            continue
        for warning in config.config_warnings:
            warning_rows.append({"config": str(path), **warning})
        configs.append({"path": path, "config": config})
    warning_rows.sort(key=lambda row: (row["config"], row["path"], row["code"]))
    return {"configs": configs, "errors": errors, "warnings": warning_rows}


def config_warning_gate(
    config_paths: Sequence[Path], *, acknowledge: bool, mode: str = "campaign"
) -> dict[str, Any]:
    """Return the doctor-owned warning acknowledgement gate for a caller."""
    if mode not in {"inspection", "campaign"}:
        raise ValueError("doctor mode must be 'inspection' or 'campaign'")
    inspection = inspect_configs(config_paths)
    warning_rows = inspection["warnings"]
    required = mode == "campaign" and bool(warning_rows)
    acknowledgement = {
        "scope": "config_warnings",
        "mode": mode,
        "required": required,
        "acknowledged": bool(acknowledge and warning_rows),
        "mechanism": "--ack-config-warnings" if acknowledge and warning_rows else None,
        "warning_count": len(warning_rows),
        "warnings": warning_rows,
    }
    if inspection["errors"]:
        status = "fail"
        summary = f"{len(inspection['errors'])} config(s) failed validation"
    elif required and not acknowledge:
        status = "fail"
        summary = (
            f"{len(warning_rows)} config warning(s) require explicit acknowledgement"
        )
    elif warning_rows:
        status = "warn"
        summary = f"{len(warning_rows)} ignored config key warning(s)"
    elif config_paths:
        status = "pass"
        summary = f"{len(config_paths)} config(s) valid with no ignored keys"
    else:
        status = "warn"
        summary = "no config supplied; config-specific checks are limited"
    return {
        "status": status,
        "summary": summary,
        "details": {
            "config_count": len(config_paths),
            "errors": inspection["errors"],
            "acknowledgement": acknowledgement,
        },
        "inspection": inspection,
    }


def _identity_rows(inspection: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    models: list[dict[str, Any]] = []
    tokenizers: list[dict[str, Any]] = []
    for row in inspection["configs"]:
        path: Path = row["path"]
        config: BenchmarkConfig = row["config"]
        model = config.model
        models.append(
            {
                "config": str(path),
                "name": model.name,
                "source": model.source,
                "revision": model.revision,
                "weight_format": model.weight_format,
            }
        )
        tokenizer_row: dict[str, Any] = {
            "config": str(path),
            "backend": config.hardware_target.runtime_backend.value,
            "identifier": model.source,
            "revision": model.revision,
            "suite_manifest_ref": config.workload_profile.suite_manifest_ref,
            "suite_tokenizer_id": None,
        }
        manifest_ref = config.workload_profile.suite_manifest_ref
        if manifest_ref is not None:
            tokenizer_row["suite_tokenizer_id"] = _suite_tokenizer_id(Path(manifest_ref))
        tokenizers.append(tokenizer_row)
    return models, tokenizers


def _suite_tokenizer_id(path: Path) -> str | None:
    """Extract the tokenizer-scoped suite identity without importing a runtime."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    direct = raw.get("tokenizer_id")
    if isinstance(direct, str) and direct:
        return direct
    tokenizer = raw.get("tokenizer")
    if isinstance(tokenizer, dict):
        direct = tokenizer.get("tokenizer_id")
        if isinstance(direct, str) and direct:
            return direct
    source = raw.get("source_manifest")
    if isinstance(source, dict):
        source_id = source.get("source_id")
        if isinstance(source_id, str) and ":tokfiles_" in source_id:
            return source_id.split(":", 1)[1]
    return None


def _check(check_id: str, status: str, summary: str, details: Any) -> dict[str, Any]:
    return {"id": check_id, "status": status, "summary": summary, "details": details}


def _required_powermetrics(inspection: dict[str, Any]) -> bool:
    return any(
        row["config"].hardware_target.telemetry_backend.value == "powermetrics"
        for row in inspection["configs"]
    )


def build_doctor_report(
    config_paths: Sequence[Path],
    *,
    probe: DoctorProbeFixture,
    mode: str = "inspection",
    acknowledge_config_warnings: bool = False,
) -> dict[str, Any]:
    """Build the stable doctor report from explicit config and probe inputs."""
    config_gate = config_warning_gate(
        config_paths,
        acknowledge=acknowledge_config_warnings,
        mode=mode,
    )
    inspection = config_gate.pop("inspection")
    checks: list[dict[str, Any]] = [
        _check("config", config_gate["status"], config_gate["summary"], config_gate["details"])
    ]

    version_details = {
        "python": probe.python_version,
        "os": {"name": probe.os_name, "version": probe.os_version},
        "architecture": probe.architecture,
        "hardware_model": probe.hardware_model,
        "cpu_brand": probe.cpu_brand,
        "logical_cpu_count": probe.logical_cpu_count,
        "packages": probe.package_versions,
    }
    version_status = "pass" if probe.architecture and probe.python_version else "warn"
    checks.append(
        _check(
            "versions_arch",
            version_status,
            f"{probe.os_name} {probe.os_version}; {probe.architecture}; Python {probe.python_version}",
            version_details,
        )
    )

    models, tokenizers = _identity_rows(inspection)
    identity_missing = any(
        row["source"] is None or row["revision"] is None for row in models
    ) or any(row["identifier"] is None for row in tokenizers)
    identity_status = "warn" if not models or identity_missing else "pass"
    identity_summary = (
        f"{len(models)} model and {len(tokenizers)} tokenizer identity record(s)"
        if models
        else "model/tokenizer identity unavailable without a valid config"
    )
    checks.append(
        _check(
            "model_tokenizer_identity",
            identity_status,
            identity_summary,
            {"models": models, "tokenizers": tokenizers},
        )
    )

    powermetrics_required = _required_powermetrics(inspection)
    powermetrics_ok = (
        probe.powermetrics_present
        and probe.powermetrics_executable
        and probe.sudo_probe_ok
    )
    if powermetrics_required and not powermetrics_ok:
        powermetrics_status = "fail"
    elif not powermetrics_ok:
        powermetrics_status = "warn"
    else:
        powermetrics_status = "pass"
    checks.append(
        _check(
            "powermetrics",
            powermetrics_status,
            "powermetrics and inspect-only sudo policy available"
            if powermetrics_ok
            else "powermetrics capability is incomplete",
            {
                "required_by_config": powermetrics_required,
                "path": probe.powermetrics_path,
                "present": probe.powermetrics_present,
                "executable": probe.powermetrics_executable,
                "sudo_noninteractive_policy": probe.sudo_probe_ok,
                "sudo_probe": "sudo -n -l <powermetrics-path>",
                "sudo_probe_reason": probe.sudo_probe_reason,
                "privileged_command_invoked": False,
            },
        )
    )

    sampler_rows = [
        {
            "config": str(row["path"]),
            "telemetry_backend": row["config"].hardware_target.telemetry_backend.value,
            "power_hz": row["config"].sampling.power_hz,
            "idle_seconds": row["config"].sampling.idle_seconds,
            "warmup_seconds": row["config"].sampling.warmup_seconds,
        }
        for row in inspection["configs"]
    ]
    checks.append(
        _check(
            "samplers",
            "pass" if sampler_rows else "warn",
            f"{len(sampler_rows)} sampling configuration(s); powermetrics requests {SAMPLERS}",
            {
                "powermetrics_samplers_requested": SAMPLERS.split(","),
                "sampling": sampler_rows,
            },
        )
    )

    thermal = (probe.thermal_pressure or "").lower()
    if not thermal:
        thermal_status = "warn"
    elif thermal in {"nominal", "normal"}:
        thermal_status = "pass"
    else:
        thermal_status = "warn"
    checks.append(
        _check(
            "thermal_pressure",
            thermal_status,
            f"thermal pressure: {probe.thermal_pressure or 'unavailable'}",
            {
                "thermal_pressure": probe.thermal_pressure,
                "probe_reason": probe.thermal_probe_reason,
            },
        )
    )

    if probe.backup_present is True and probe.backup_free_bytes is not None:
        backup_status = (
            "pass" if probe.backup_free_bytes >= MIN_BACKUP_FREE_BYTES else "warn"
        )
        backup_summary = (
            f"backup destination present with {probe.backup_free_bytes} free bytes"
        )
    elif probe.backup_present is False:
        backup_status = "warn"
        backup_summary = "backup destination is not present"
    else:
        backup_status = "warn"
        backup_summary = "backup destination was not configured"
    checks.append(
        _check(
            "backup_destination",
            backup_status,
            backup_summary,
            {
                "path": probe.backup_destination,
                "present": probe.backup_present,
                "free_bytes": probe.backup_free_bytes,
                "preferred_minimum_free_bytes": MIN_BACKUP_FREE_BYTES,
                "probe_reason": probe.backup_probe_reason,
            },
        )
    )

    quiet_reasons = [
        "doctor cannot certify machine quietness; stop agents and unrelated workloads before measurement"
    ]
    environment_evaluation = evaluate_environment_policy(
        {
            "power_source": probe.power_source,
            "power": {"external_connected": probe.external_connected},
            "low_power_mode": probe.low_power_mode,
            "display_power_state": probe.display_power_state,
            "screensaver_engaged": probe.screensaver_engaged,
            "screensaver_module": probe.screensaver_module,
            "screensaver_delay_s": probe.screensaver_delay_s,
            "hid_idle_s": probe.hid_idle_s,
            "thermal_pressure": probe.thermal_pressure,
            "load_average_1m": probe.load_average_1m,
        }
    )
    finding_messages = {
        "power_source_not_ac": "power source is not AC Power",
        "external_power_not_connected": "external power is not connected",
        "low_power_mode_enabled": "low power mode is enabled",
        "display_not_all_asleep": "online displays are not all asleep",
        "screensaver_engaged": "screensaver is engaged",
        "thermal_not_nominal": "thermal pressure is not nominal",
    }
    for finding in environment_evaluation["findings"]:
        if finding["status"] == "pass":
            continue
        if (
            finding["code"] == "power_source_not_ac"
            and finding["actual"] is not None
        ):
            message = f"power source is {finding['actual']}"
        else:
            message = finding_messages[finding["code"]]
        if finding["status"] == "unknown":
            message += " (probe unknown)"
        quiet_reasons.append(message)
    if (
        probe.load_average_1m is not None
        and probe.logical_cpu_count is not None
        and probe.load_average_1m > max(1.0, probe.logical_cpu_count * 0.25)
    ):
        quiet_reasons.append(
            f"1-minute load average {probe.load_average_1m} exceeds the quiet-warning threshold"
        )
    if probe.display_active_count not in {None, 0}:
        quiet_reasons.append(f"{probe.display_active_count} display(s) are active")
    checks.append(
        _check(
            "quiet_machine",
            "warn",
            f"{len(quiet_reasons)} quiet-machine warning(s)",
            {
                "warnings": quiet_reasons,
                "power_source": probe.power_source,
                "low_power_mode": probe.low_power_mode,
                "load_average_1m": probe.load_average_1m,
                "logical_cpu_count": probe.logical_cpu_count,
                "display_active_count": probe.display_active_count,
                "display_power_state": probe.display_power_state,
                "external_connected": probe.external_connected,
                "screensaver_engaged": probe.screensaver_engaged,
                "screensaver_module": probe.screensaver_module,
                "screensaver_delay_s": probe.screensaver_delay_s,
                "hid_idle_s": probe.hid_idle_s,
                "environment_policy_evaluation": environment_evaluation,
                "environment_probe_errors": probe.environment_errors,
            },
        )
    )

    assert tuple(check["id"] for check in checks) == CHECK_ORDER
    verdict = max(checks, key=lambda check: STATUS_ORDER[check["status"]])["status"]
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "verdict": verdict,
        "checks": checks,
    }


def doctor_report(
    config_paths: Sequence[Path],
    *,
    backup_destination: Path | None,
    mode: str = "inspection",
    acknowledge_config_warnings: bool = False,
) -> dict[str, Any]:
    probe = collect_live_probe(backup_destination)
    return build_doctor_report(
        config_paths,
        probe=probe,
        mode=mode,
        acknowledge_config_warnings=acknowledge_config_warnings,
    )


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def _human_detail(check: dict[str, Any]) -> str:
    details = check["details"]
    check_id = check["id"]
    if check_id == "config":
        acknowledgement = details["acknowledgement"]
        warnings_text = ", ".join(
            f"{row['config']}:{row['path']}" for row in acknowledgement["warnings"]
        )
        errors_text = ", ".join(
            f"{row['config']}:{row['message']}" for row in details["errors"]
        )
        suffix = warnings_text or errors_text or "no ignored keys"
        return (
            f"{check['summary']}; acknowledged={acknowledgement['acknowledged']}; "
            f"{suffix}"
        )
    if check_id == "versions_arch":
        packages = ",".join(
            f"{name}={record.get('version') if record.get('present') else 'absent'}"
            for name, record in sorted(details["packages"].items())
        )
        return (
            f"{check['summary']}; model={details['hardware_model']}; "
            f"cpu={details['cpu_brand']}; packages={packages}"
        )
    if check_id == "model_tokenizer_identity":
        models = ", ".join(
            f"{row['config']} model={row['name']} source={row['source']} revision={row['revision']}"
            for row in details["models"]
        )
        tokenizers = ", ".join(
            f"{row['config']} tokenizer={row['suite_tokenizer_id'] or row['identifier']} "
            f"revision={row['revision']}"
            for row in details["tokenizers"]
        )
        return "; ".join(part for part in (models, tokenizers) if part) or check["summary"]
    if check_id == "powermetrics":
        return (
            f"path={details['path']}; present={details['present']}; "
            f"executable={details['executable']}; "
            f"sudo_noninteractive_policy={details['sudo_noninteractive_policy']}; "
            f"reason={details['sudo_probe_reason']}"
        )
    if check_id == "samplers":
        requested = ",".join(details["powermetrics_samplers_requested"])
        configured = ", ".join(
            f"{row['config']} backend={row['telemetry_backend']} power_hz={row['power_hz']} "
            f"idle_seconds={row['idle_seconds']} warmup_seconds={row['warmup_seconds']}"
            for row in details["sampling"]
        )
        return f"requested={requested}; {configured or 'no config sampling fields'}"
    if check_id == "thermal_pressure":
        return (
            f"thermal_pressure={details['thermal_pressure']}; "
            f"reason={details['probe_reason']}"
        )
    if check_id == "backup_destination":
        return (
            f"path={details['path']}; present={details['present']}; "
            f"free_bytes={details['free_bytes']}; reason={details['probe_reason']}"
        )
    if check_id == "quiet_machine":
        return "; ".join(details["warnings"])
    return check["summary"]


def render_human(report: dict[str, Any]) -> str:
    """Render a stable-order, fixed-column human table."""
    rows = [("CHECK", "STATUS", "DETAIL")]
    rows.extend(
        (check["id"], check["status"].upper(), _human_detail(check))
        for check in report["checks"]
    )
    check_width = max(len(row[0]) for row in rows)
    status_width = max(len(row[1]) for row in rows)
    lines = [
        f"JouleWise doctor: mode={report['mode']} verdict={report['verdict'].upper()}",
        f"{rows[0][0]:<{check_width}}  {rows[0][1]:<{status_width}}  {rows[0][2]}",
        f"{'-' * check_width}  {'-' * status_width}  {'-' * len(rows[0][2])}",
    ]
    lines.extend(
        f"{check:<{check_width}}  {status:<{status_width}}  {summary}"
        for check, status, summary in rows[1:]
    )
    return "\n".join(lines) + "\n"


def exit_code(report: dict[str, Any]) -> int:
    return 1 if report["verdict"] == "fail" else 0
