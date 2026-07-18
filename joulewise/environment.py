"""Sudo-free per-bundle environment snapshot helpers."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
from dataclasses import asdict, dataclass
from importlib import metadata as importlib_metadata
from typing import Any, Mapping

from joulewise.schemas import EnvironmentGuardPolicy

COMMAND_TIMEOUT_S = 3.0
DEFAULT_SCREENSAVER_DELAY_S = 20 * 60


@dataclass(frozen=True)
class EnvironmentFinding:
    """One deterministic environment-policy predicate result."""

    code: str
    field: str
    status: str
    actual: Any
    required: Any
    critical: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def evaluate_environment_policy(
    snapshot: Mapping[str, Any],
    policy: EnvironmentGuardPolicy | None = None,
) -> dict[str, Any]:
    """Purely evaluate one captured snapshot against the quiet-host policy.

    Doctor and the campaign runner share this evaluator.  The former renders
    the result as advisory evidence; the latter enforces ``eligible``.  Load
    average is copied as evidence only and is deliberately absent from the
    finding predicates.
    """

    selected = policy if policy is not None else EnvironmentGuardPolicy()
    power = snapshot.get("power")
    external_connected = (
        power.get("external_connected") if isinstance(power, Mapping) else None
    )
    checks = (
        (
            selected.require_ac_power,
            "power_source_not_ac",
            "power_source",
            snapshot.get("power_source"),
            "AC Power",
        ),
        (
            selected.require_external_connected,
            "external_power_not_connected",
            "power.external_connected",
            external_connected,
            True,
        ),
        (
            selected.require_low_power_mode_off,
            "low_power_mode_enabled",
            "low_power_mode",
            snapshot.get("low_power_mode"),
            False,
        ),
        (
            selected.require_displays_asleep,
            "display_not_all_asleep",
            "display_power_state",
            snapshot.get("display_power_state"),
            "all_asleep",
        ),
        (
            selected.require_screensaver_disengaged,
            "screensaver_engaged",
            "screensaver_engaged",
            snapshot.get("screensaver_engaged"),
            False,
        ),
        (
            selected.require_thermal_nominal,
            "thermal_not_nominal",
            "thermal_pressure",
            snapshot.get("thermal_pressure"),
            "nominal",
        ),
    )
    findings: list[EnvironmentFinding] = []
    for enabled, code, field, actual, required in checks:
        if not enabled:
            continue
        comparable_actual = actual.lower() if isinstance(actual, str) else actual
        comparable_required = required.lower() if isinstance(required, str) else required
        if actual is None:
            status = "unknown"
        elif comparable_actual == comparable_required:
            status = "pass"
        else:
            status = "fail"
        findings.append(
            EnvironmentFinding(
                code=code,
                field=field,
                status=status,
                actual=actual,
                required=required,
            )
        )
    serialized_findings = [finding.to_dict() for finding in findings]
    blocked = any(finding.status == "fail" for finding in findings) or (
        selected.critical_unknown_fail_closed
        and any(finding.status == "unknown" for finding in findings)
    )
    snapshot_value = dict(snapshot)
    return {
        "schema_version": "joulewise.environment_evaluation.v1",
        "eligible": not blocked,
        "findings": serialized_findings,
        "snapshot_sha256": _canonical_sha256(snapshot_value),
        "findings_sha256": _canonical_sha256(serialized_findings),
        "load_average_evidence": {
            "load_average_1m": snapshot.get("load_average_1m"),
            "load_average_5m": snapshot.get("load_average_5m"),
            "load_average_15m": snapshot.get("load_average_15m"),
            "admission_gate": False,
        },
    }


def probe_thermal_pressure(
    timeout_s: float = COMMAND_TIMEOUT_S,
) -> tuple[str | None, str | None]:
    """Return macOS thermal pressure from the read-only ``pmset`` probe.

    ``pmset -g therm`` does not require sudo.  The stable nominal sentence is
    mapped to ``nominal``; other platform output is retained as ``elevated``
    only when it reports an active warning/limit.  Unknown formats fail soft.
    """
    stdout, error = _run(["pmset", "-g", "therm"], timeout_s)
    if stdout is None:
        return None, error
    normalized = " ".join(stdout.lower().split())
    if "no thermal warning level has been recorded" in normalized:
        return "nominal", None
    limits = [
        int(value)
        for value in re.findall(
            r"(?:speed|scheduler)_limit\s*=\s*(\d+)", normalized
        )
    ]
    if limits:
        return ("elevated" if any(value < 100 for value in limits) else "nominal"), None
    if "thermal warning" in normalized or "thermal level" in normalized:
        return "elevated", None
    return None, "unrecognized_output"


def empty_environment_snapshot() -> dict[str, Any]:
    """Return the nullable environment shape without probing the host."""
    return {
        "power_source": None,
        "battery_percent": None,
        "battery_state": None,
        "low_power_mode": None,
        "display_sleep_prevented": None,
        "display_power_state": None,
        "screensaver_engaged": None,
        "screensaver_module": None,
        "screensaver_delay_s": None,
        "hid_idle_s": None,
        "thermal_pressure": None,
        "thermal_probe_reason": None,
        "memory_free_percent": None,
        "memory_pressure_percent": None,
        "memory": {
            "swap_usage": None,
            "page_size_bytes": None,
            "pages_free": None,
            "pageins": None,
            "pageouts": None,
            "pages_occupied_by_compressor": None,
            "pages_stored_in_compressor": None,
            "compressor_bytes": None,
        },
        "display": {
            "status": None,
            "probe": None,
            "reason": None,
            "active_displays": None,
            "external_display_count": None,
            "built_in_display_count": None,
            "framebuffer_pipes_total": None,
            "framebuffer_pipes_external_capable": None,
        },
        "power": {
            "adapter_watts": None,
            "adapter_description": None,
            "external_connected": None,
            "is_charging": None,
            "fully_charged": None,
        },
        "uptime_s": None,
        "boot_time_s": None,
        "clock_sync": {
            "status": "unavailable",
            "timed_running": None,
            "timed_probe_error": None,
        },
        "python_packages": {
            "mlx": _package_version_record("mlx"),
            "mlx-lm": _package_version_record("mlx-lm"),
            "transformers": _package_version_record("transformers"),
        },
        "load_average_1m": None,
        "load_average_5m": None,
        "load_average_15m": None,
        "product_name": None,
        "product_version": None,
        "build_version": None,
        "hw_model": None,
        "logical_cpu_count": None,
        "cpu_brand": None,
        "errors": {},
    }


def collect_environment_snapshot(timeout_s: float = COMMAND_TIMEOUT_S) -> dict[str, Any]:
    """Return a best-effort machine-wide environment snapshot.

    Every subprocess is sudo-free and independently optional: missing commands,
    nonzero exits, timeouts, and parse failures leave that command's fields as
    ``None`` and add a terse entry to ``errors``. This function never raises.

    ``memory_pressure_percent`` is derived from a free-memory percentage when
    available; it is a pressure proxy, not the kernel's memorystatus level.
    """
    snapshot: dict[str, Any] = empty_environment_snapshot()
    errors: dict[str, str] = {}

    _apply_command(
        snapshot,
        errors,
        "pmset_batt",
        ["pmset", "-g", "batt"],
        _parse_pmset_batt,
        timeout_s,
    )
    _apply_command(
        snapshot,
        errors,
        "pmset",
        ["pmset", "-g"],
        _parse_pmset,
        timeout_s,
    )
    _apply_command(
        snapshot,
        errors,
        "pmset_assertions",
        ["pmset", "-g", "assertions"],
        _parse_pmset_assertions,
        timeout_s,
    )
    memory_ok = _apply_command(
        snapshot,
        errors,
        "memory_pressure",
        ["memory_pressure", "-Q"],
        _parse_memory_pressure,
        timeout_s,
    )
    if not memory_ok:
        vm_stat = _run(["vm_stat"], timeout_s)
        memsize = _run(["sysctl", "-n", "hw.memsize"], timeout_s)
        if vm_stat[0] is None:
            errors["vm_stat"] = vm_stat[1] or "failed"
        if memsize[0] is None:
            errors["sysctl_hw_memsize"] = memsize[1] or "failed"
        if vm_stat[0] is not None and memsize[0] is not None:
            try:
                _parse_vm_stat(snapshot, vm_stat[0], memsize[0])
            except Exception:  # noqa: BLE001 - snapshot collection must never raise
                errors["vm_stat"] = "parse"
    else:
        _apply_command(
            snapshot,
            errors,
            "vm_stat",
            ["vm_stat"],
            _parse_vm_stat_counters,
            timeout_s,
        )
    _apply_command(
        snapshot,
        errors,
        "sysctl_vm_swapusage",
        ["sysctl", "vm.swapusage"],
        _parse_swapusage,
        timeout_s,
    )
    display_ok = _apply_command(
        snapshot,
        errors,
        "system_profiler_spdisplays",
        ["system_profiler", "SPDisplaysDataType", "-json"],
        _parse_system_profiler_displays,
        timeout_s,
    )
    if not display_ok:
        snapshot["display"].update(
            {
                "status": "probe_unavailable",
                "probe": "system_profiler_spdisplays",
                "reason": errors.get("system_profiler_spdisplays", "failed"),
            }
        )
    _apply_command(
        snapshot,
        errors,
        "pmset_systemstate",
        ["pmset", "-g", "systemstate"],
        _parse_pmset_systemstate,
        timeout_s,
    )
    _apply_command(
        snapshot,
        errors,
        "screensaver_defaults",
        ["defaults", "-currentHost", "read", "com.apple.screensaver"],
        _parse_screensaver_defaults,
        timeout_s,
    )
    _apply_command(
        snapshot,
        errors,
        "ioreg_hid_idle",
        ["ioreg", "-c", "IOHIDSystem"],
        _parse_ioreg_hid_idle,
        timeout_s,
    )
    _derive_screensaver_engagement(snapshot)
    _apply_command(
        snapshot,
        errors,
        "ioreg_framebuffer_pipes",
        ["ioreg", "-r", "-c", "IOMobileFramebuffer"],
        _parse_ioreg_framebuffer_pipes,
        timeout_s,
    )
    _apply_command(
        snapshot,
        errors,
        "ioreg_battery",
        ["ioreg", "-r", "-c", "AppleSmartBattery", "-d", "1"],
        _parse_ioreg_battery,
        timeout_s,
    )
    _apply_command(
        snapshot,
        errors,
        "sysctl_kern_boottime",
        ["sysctl", "-n", "kern.boottime"],
        _parse_kern_boottime,
        timeout_s,
    )
    _probe_clock_sync(snapshot, errors, timeout_s)
    thermal_pressure, thermal_reason = probe_thermal_pressure(timeout_s)
    snapshot["thermal_pressure"] = thermal_pressure
    snapshot["thermal_probe_reason"] = thermal_reason
    if thermal_pressure is None:
        errors["pmset_therm"] = thermal_reason or "failed"
    _apply_command(
        snapshot,
        errors,
        "uptime",
        ["uptime"],
        _parse_uptime,
        timeout_s,
    )
    _apply_command(
        snapshot,
        errors,
        "sw_vers",
        ["sw_vers"],
        _parse_sw_vers,
        timeout_s,
    )
    _apply_command(
        snapshot,
        errors,
        "sysctl_host",
        ["sysctl", "-n", "hw.model", "hw.ncpu", "machdep.cpu.brand_string"],
        _parse_sysctl_host,
        timeout_s,
    )

    snapshot["errors"] = errors
    return snapshot


def collect_environment_guard_observation(
    timeout_s: float = COMMAND_TIMEOUT_S,
) -> dict[str, Any]:
    """Capture the lightweight display/screensaver transition surface.

    This post-run observation intentionally omits the expensive full host
    inventory while preserving null-on-failure semantics for every probe.
    """

    observation = {
        "display_power_state": None,
        "screensaver_engaged": None,
        "screensaver_module": None,
        "screensaver_delay_s": None,
        "hid_idle_s": None,
        "errors": {},
    }
    errors: dict[str, str] = observation["errors"]
    _apply_command(
        observation,
        errors,
        "pmset_systemstate",
        ["pmset", "-g", "systemstate"],
        _parse_pmset_systemstate,
        timeout_s,
    )
    _apply_command(
        observation,
        errors,
        "screensaver_defaults",
        ["defaults", "-currentHost", "read", "com.apple.screensaver"],
        _parse_screensaver_defaults,
        timeout_s,
    )
    _apply_command(
        observation,
        errors,
        "ioreg_hid_idle",
        ["ioreg", "-c", "IOHIDSystem"],
        _parse_ioreg_hid_idle,
        timeout_s,
    )
    _derive_screensaver_engagement(observation)
    return observation


def _package_version_record(distribution: str) -> dict[str, str | bool | None]:
    try:
        version = importlib_metadata.version(distribution)
    except importlib_metadata.PackageNotFoundError:
        return {"present": False, "version": None}
    except Exception as exc:  # noqa: BLE001 - environment capture must never raise
        return {"present": False, "version": None, "error": f"{type(exc).__name__}: {exc}"}
    return {"present": True, "version": version}


def _apply_command(
    snapshot: dict[str, Any],
    errors: dict[str, str],
    key: str,
    command: list[str],
    parser,
    timeout_s: float,
) -> bool:
    stdout, error = _run(command, timeout_s)
    if stdout is None:
        errors[key] = error or "failed"
        return False
    try:
        parser(snapshot, stdout)
    except Exception:  # noqa: BLE001 - snapshot collection must never raise
        errors[key] = "parse"
        return False
    return True


def _run(command: list[str], timeout_s: float) -> tuple[str | None, str | None]:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except FileNotFoundError:
        return None, "not_found"
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except Exception:  # noqa: BLE001 - snapshot collection must never raise
        return None, "failed"
    if completed.returncode != 0:
        return None, f"returncode_{completed.returncode}"
    return completed.stdout, None


def _parse_pmset_batt(snapshot: dict[str, Any], text: str) -> None:
    source = re.search(r"Now drawing from '([^']+)'", text)
    percent = re.search(r"(\d+)%", text)
    state = re.search(r"\d+%;\s*([^;]+);", text)
    if not source and not percent and not state:
        raise ValueError("battery status not found")
    if source:
        snapshot["power_source"] = source.group(1)
    if percent:
        snapshot["battery_percent"] = int(percent.group(1))
    if state:
        snapshot["battery_state"] = state.group(1).strip()


def _parse_pmset(snapshot: dict[str, Any], text: str) -> None:
    # Missing lowpowermode is legitimate on some macOS/hardware combinations.
    match = re.search(r"^\s*lowpowermode\s+([01])\s*$", text, re.MULTILINE)
    if match:
        snapshot["low_power_mode"] = match.group(1) == "1"


def _parse_pmset_assertions(snapshot: dict[str, Any], text: str) -> None:
    # Missing display assertion lines are a legitimate machine state.
    match = re.search(
        r"^\s*PreventUserIdleDisplaySleep\s+([01])\s*$",
        text,
        re.MULTILINE,
    )
    if match:
        snapshot["display_sleep_prevented"] = match.group(1) == "1"


def _parse_pmset_systemstate(snapshot: dict[str, Any], text: str) -> None:
    match = re.search(
        r"Current\s+System\s+Capabilities\s*(?:are)?\s*:\s*([^\n]*)",
        text,
        re.IGNORECASE,
    )
    if not match:
        raise ValueError("current system capabilities not found")
    capabilities = {part.lower() for part in re.findall(r"[A-Za-z]+", match.group(1))}
    if "graphics" in capabilities:
        snapshot["display_power_state"] = "any_awake"
        return
    display = snapshot.get("display")
    online_count = (
        display.get("active_displays") if isinstance(display, dict) else None
    )
    # A recognized systemstate record establishes that no display is awake.
    # When the full inventory is available, require at least one online display
    # so an empty/unrecognized profiler result cannot masquerade as asleep.
    if isinstance(display, dict) and online_count in {None, 0}:
        snapshot["display_power_state"] = "unknown"
    else:
        snapshot["display_power_state"] = "all_asleep"


def _parse_screensaver_defaults(snapshot: dict[str, Any], text: str) -> None:
    normalized = text.strip()
    if not normalized:
        raise ValueError("screensaver defaults output is empty")
    module = re.search(r"moduleName\s*=\s*[\"']?([^;\n\"']+)", text)
    delay = re.search(r"(?:^|[;\n{])\s*idleTime\s*=\s*(\d+)\s*;?", text)
    snapshot["screensaver_module"] = module.group(1).strip() if module else None
    snapshot["screensaver_delay_s"] = (
        int(delay.group(1)) if delay else DEFAULT_SCREENSAVER_DELAY_S
    )


def _parse_ioreg_hid_idle(snapshot: dict[str, Any], text: str) -> None:
    match = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', text)
    if not match:
        raise ValueError("HIDIdleTime not found")
    snapshot["hid_idle_s"] = int(match.group(1)) / 1_000_000_000.0


def _derive_screensaver_engagement(snapshot: dict[str, Any]) -> None:
    delay = snapshot.get("screensaver_delay_s")
    hid_idle = snapshot.get("hid_idle_s")
    if delay == 0:
        snapshot["screensaver_engaged"] = False
    elif (
        isinstance(delay, int | float)
        and not isinstance(delay, bool)
        and isinstance(hid_idle, int | float)
        and not isinstance(hid_idle, bool)
    ):
        snapshot["screensaver_engaged"] = float(hid_idle) >= float(delay)
    else:
        snapshot["screensaver_engaged"] = None


def _parse_memory_pressure(snapshot: dict[str, Any], text: str) -> None:
    match = re.search(r"System-wide memory free percentage:\s*(\d+(?:\.\d+)?)%", text)
    if not match:
        raise ValueError("memory free percentage not found")
    free_percent = float(match.group(1))
    snapshot["memory_free_percent"] = free_percent
    snapshot["memory_pressure_percent"] = 100.0 - free_percent


def _parse_vm_stat(snapshot: dict[str, Any], text: str, memsize_text: str) -> None:
    counters = _vm_stat_counters(text)
    page_size = counters.get("page_size_bytes")
    free_pages = counters.get("Pages free")
    if page_size is None or free_pages is None:
        raise ValueError("vm_stat free pages not found")
    memsize = int(memsize_text.strip())
    free_percent = (free_pages * page_size / memsize) * 100.0
    snapshot["memory_free_percent"] = free_percent
    snapshot["memory_pressure_percent"] = 100.0 - free_percent
    _apply_vm_stat_counters(snapshot, counters)


def _parse_vm_stat_counters(snapshot: dict[str, Any], text: str) -> None:
    _apply_vm_stat_counters(snapshot, _vm_stat_counters(text))


def _vm_stat_counters(text: str) -> dict[str, int]:
    page_size_match = re.search(r"page size of (\d+) bytes", text)
    if not page_size_match:
        raise ValueError("vm_stat page size not found")
    counters: dict[str, int] = {"page_size_bytes": int(page_size_match.group(1))}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        match = re.search(r"([\d.]+)", value)
        if match:
            counters[key.strip()] = int(match.group(1).replace(".", ""))
    return counters


def _apply_vm_stat_counters(snapshot: dict[str, Any], counters: dict[str, int]) -> None:
    memory = snapshot["memory"]
    page_size = counters.get("page_size_bytes")
    memory["page_size_bytes"] = page_size
    memory["pages_free"] = counters.get("Pages free")
    memory["pageins"] = counters.get("Pageins")
    memory["pageouts"] = counters.get("Pageouts")
    memory["pages_occupied_by_compressor"] = counters.get("Pages occupied by compressor")
    memory["pages_stored_in_compressor"] = counters.get("Pages stored in compressor")
    if page_size is not None and memory["pages_occupied_by_compressor"] is not None:
        memory["compressor_bytes"] = memory["pages_occupied_by_compressor"] * page_size


def _parse_swapusage(snapshot: dict[str, Any], text: str) -> None:
    match = re.search(
        r"vm\.swapusage:\s+total\s+=\s+([^ ]+)\s+used\s+=\s+([^ ]+)\s+free\s+=\s+([^ ]+)",
        text,
    )
    if not match:
        raise ValueError("swapusage not found")
    snapshot["memory"]["swap_usage"] = {
        "total": match.group(1),
        "used": match.group(2),
        "free": match.group(3).strip(),
    }


def _parse_system_profiler_displays(snapshot: dict[str, Any], text: str) -> None:
    payload = json.loads(text)
    displays: list[dict[str, Any]] = []
    for gpu in payload.get("SPDisplaysDataType", []):
        if isinstance(gpu, dict):
            displays.extend(_online_display_entries(gpu))
    built_in = sum(1 for display in displays if _is_built_in_display(display))
    active = len(displays)
    display = snapshot["display"]
    display["status"] = "ok"
    display["probe"] = "system_profiler_spdisplays"
    display["reason"] = None
    display["active_displays"] = active
    display["built_in_display_count"] = built_in
    display["external_display_count"] = max(0, active - built_in)


def _online_display_entries(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        entries: list[dict[str, Any]] = []
        if _is_display_entry(value) and _is_online_display(value):
            entries.append(value)
        for child in value.values():
            entries.extend(_online_display_entries(child))
        return entries
    if isinstance(value, list):
        entries: list[dict[str, Any]] = []
        for item in value:
            entries.extend(_online_display_entries(item))
        return entries
    return []


def _is_display_entry(value: dict[str, Any]) -> bool:
    return any(
        key in value
        for key in (
            "spdisplays_online",
            "spdisplays_display_type",
            "spdisplays_connection_type",
            "spdisplays_resolution",
        )
    )


def _is_online_display(value: dict[str, Any]) -> bool:
    online = value.get("spdisplays_online")
    if online is None:
        return True
    return online in {True, "spdisplays_yes", "yes", "Yes", "1", 1}


def _is_built_in_display(value: dict[str, Any]) -> bool:
    markers = {
        str(value.get("spdisplays_display_type", "")),
        str(value.get("spdisplays_connection_type", "")),
    }
    return bool(
        markers
        & {
            "spdisplays_built-in",
            "spdisplays_builtin",
            "spdisplays_internal",
            "Internal",
            "Built-In",
        }
    )


def _parse_ioreg_framebuffer_pipes(snapshot: dict[str, Any], text: str) -> None:
    entries = re.findall(
        r"^\+-o\s+\S+\s+<class IOMobileFramebuffer(?:Shim)?,",
        text,
        re.MULTILINE,
    )
    if not entries:
        raise ValueError("no framebuffer entries")
    external = len(re.findall(r'"external"\s+=\s+Yes', text))
    display = snapshot["display"]
    display["framebuffer_pipes_total"] = len(entries)
    display["framebuffer_pipes_external_capable"] = min(external, len(entries))


def _parse_ioreg_battery(snapshot: dict[str, Any], text: str) -> None:
    power = snapshot["power"]
    watts = re.search(r'"Watts"\s*=\s*(\d+)', text)
    description = re.search(r'"Description"\s*=\s*"([^"]+)"', text)
    if watts:
        power["adapter_watts"] = int(watts.group(1))
    if description:
        power["adapter_description"] = description.group(1)
    for raw_key, out_key in (
        ("ExternalConnected", "external_connected"),
        ("IsCharging", "is_charging"),
        ("FullyCharged", "fully_charged"),
    ):
        value = _ioreg_bool(text, raw_key)
        if value is not None:
            power[out_key] = value
    if not any(value is not None for value in power.values()):
        raise ValueError("battery power details not found")


def _ioreg_bool(text: str, key: str) -> bool | None:
    match = re.search(rf'"{re.escape(key)}"\s*=\s*(Yes|No|True|False)', text)
    if not match:
        return None
    return match.group(1) in {"Yes", "True"}


def _parse_kern_boottime(snapshot: dict[str, Any], text: str) -> None:
    match = re.search(r"sec\s*=\s*(\d+)", text)
    if not match:
        raise ValueError("kern.boottime sec not found")
    boot_time_s = int(match.group(1))
    snapshot["boot_time_s"] = boot_time_s
    snapshot["uptime_s"] = max(0.0, time.time() - boot_time_s)


def _probe_clock_sync(
    snapshot: dict[str, Any], errors: dict[str, str], timeout_s: float
) -> None:
    clock_sync = snapshot["clock_sync"]
    clock_sync["status"] = "limited_without_admin"
    try:
        completed = subprocess.run(
            ["pgrep", "-x", "timed"],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except FileNotFoundError:
        clock_sync["timed_running"] = False
        clock_sync["timed_probe_error"] = "not_found"
        errors["pgrep_timed"] = "not_found"
        return
    except subprocess.TimeoutExpired:
        clock_sync["timed_running"] = False
        clock_sync["timed_probe_error"] = "timeout"
        errors["pgrep_timed"] = "timeout"
        return
    except Exception:  # noqa: BLE001 - snapshot collection must never raise
        clock_sync["timed_running"] = False
        clock_sync["timed_probe_error"] = "failed"
        errors["pgrep_timed"] = "failed"
        return
    if completed.returncode == 0:
        clock_sync["timed_running"] = True
        return
    clock_sync["timed_running"] = False
    if completed.returncode != 1:
        reason = f"returncode_{completed.returncode}"
        clock_sync["timed_probe_error"] = reason
        errors["pgrep_timed"] = reason


def _parse_uptime(snapshot: dict[str, Any], text: str) -> None:
    match = re.search(
        r"load averages?:\s*([0-9.]+)[,\s]+([0-9.]+)[,\s]+([0-9.]+)",
        text,
    )
    if not match:
        raise ValueError("load averages not found")
    snapshot["load_average_1m"] = float(match.group(1))
    snapshot["load_average_5m"] = float(match.group(2))
    snapshot["load_average_15m"] = float(match.group(3))


def _parse_sw_vers(snapshot: dict[str, Any], text: str) -> None:
    values = _colon_lines(text)
    product_name = values.get("ProductName")
    product_version = values.get("ProductVersion")
    build_version = values.get("BuildVersion")
    if product_name is None and product_version is None and build_version is None:
        raise ValueError("sw_vers fields not found")
    snapshot["product_name"] = product_name
    snapshot["product_version"] = product_version
    snapshot["build_version"] = build_version


def _parse_sysctl_host(snapshot: dict[str, Any], text: str) -> None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 3:
        raise ValueError("sysctl host output incomplete")
    snapshot["hw_model"] = lines[0]
    snapshot["logical_cpu_count"] = int(lines[1])
    snapshot["cpu_brand"] = lines[2]


def _colon_lines(text: str) -> dict[str, str]:
    values = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values
