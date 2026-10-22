"""Inventory and exercise a rented whole NVIDIA GPU before collecting episodes.

This module is stdlib-only unless its optional CUDA matmul load is selected.
A virtual GPU or MIG slice is a physical measurement hazard and is refused.
Missing capabilities, unavailable loads and failed clock commands are flags.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import shlex
import signal
import statistics
import subprocess
import tempfile
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Sequence

from joulewise.align.power.duty import _student_quantile
from joulewise.align.power.nvml import NvmlSampler, device_inventory, open_nvml
from joulewise.align.records import PowerTrace, to_jsonable


def _command(argv: Sequence[str], timeout_s: float) -> dict[str, Any]:
    try:
        result = subprocess.run(list(argv), capture_output=True, text=True,
                                timeout=timeout_s, check=False)
        return {"argv": list(argv), "returncode": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr}
    except (OSError, subprocess.SubprocessError) as exc:
        return {"argv": list(argv), "returncode": None, "stdout": "", "stderr": str(exc)}


def _smi_inventory(index: int, timeout_s: float) -> dict[str, Any]:
    xml_result = _command(["nvidia-smi", "-i", str(index), "-q", "-x"], timeout_s)
    result: dict[str, Any] = {"xml_query": xml_result, "flags": []}
    if xml_result["returncode"] == 0:
        try:
            root = ET.fromstring(xml_result["stdout"])
            gpu = root.find("gpu") if root.tag != "gpu" else root
            if gpu is not None:
                result["name"] = gpu.findtext("product_name")
                result["uuid"] = gpu.findtext("uuid")
                result["mig_mode"] = gpu.findtext("mig_mode/current_mig")
                result["virtualization_mode"] = gpu.findtext(
                    "gpu_virtualization_mode/virtualization_mode")
                result["driver_version"] = root.findtext("driver_version")
        except ET.ParseError as exc:
            result["flags"].append(f"smi_xml_unparseable: {exc}")
    else:
        result["flags"].append("smi_inventory_unavailable")
    # Reuse the established parser for its timestamp/power/temperature CSV
    # format; these wall-clock rows are inventory snapshots, never episode
    # monotonic samples or substitutes for NVML call brackets.
    snapshot = _command([
        "nvidia-smi", "-i", str(index),
        "--query-gpu=timestamp,power.draw,temperature.gpu",
        "--format=csv,noheader,nounits"], timeout_s)
    result["snapshot_query"] = snapshot
    if snapshot["returncode"] == 0:
        try:
            from joulewise.adapters.nvidia_smi import parse_nvidia_smi_csv
            diagnostics: dict[str, Any] = {}
            # nvidia-smi's displayed timezone is unknown here. The existing
            # parser records that provenance warning; no wall-time mapping
            # from this snapshot enters a PowerTrace.
            rows = parse_nvidia_smi_csv(snapshot["stdout"], diagnostics=diagnostics)
            result["snapshot_power_w"] = [row.power_w for row in rows]
            result["snapshot_parse"] = diagnostics
        except (ValueError, TypeError) as exc:
            result["flags"].append(f"smi_snapshot_unparseable: {exc}")
    return result


def _hazards(device: dict[str, Any], smi: dict[str, Any]) -> list[str]:
    hazards = []
    name = " ".join(str(value or "") for value in
                    (device.get("name"), device.get("uuid"), smi.get("name"), smi.get("uuid")))
    if device.get("is_mig_slice") or "MIG-" in name or " MIG " in f" {name} ":
        hazards.append("mig_slice_hides_board_power")
    mode = device.get("virtualization_mode")
    smi_mode = str(smi.get("virtualization_mode") or "").lower()
    # NVML enum: NONE=0, PASSTHROUGH=1, VGPU=2, HOST_VGPU=3,
    # HOST_VGPU_DEVICE=4. Passthrough is compatible with a whole GPU.
    if mode in (2, 3, 4) or ("vgpu" in name.lower()) or (
            smi_mode and smi_mode not in ("none", "pass through", "passthrough", "n/a", "not supported")):
        hazards.append("virtual_gpu_hides_or_shares_board_power")
    return hazards


def _spaced_values(trace: PowerTrace, start: int, end: int) -> list[float]:
    notes = json.loads(trace.notes)
    facts = notes.get("sensor_facts") or {}
    spacing = max(trace.nominal_interval_ns, facts.get("period_ns") or 0,
                  notes.get("output_averaging_window_ns") or 0)
    selected = []
    last: int | None = None
    for timestamp, value in zip(trace.t_ns, trace.values):
        if start <= timestamp < end and math.isfinite(value):
            if last is None or timestamp - last >= spacing:
                selected.append(value)
                last = timestamp
    return selected


def assess_power_movement(traces: Sequence[PowerTrace], idle_interval: tuple[int, int],
                          load_interval: tuple[int, int], *,
                          false_alarm_rate: float) -> dict[str, Any]:
    """Compare load peaks with idle mean plus a stated predictive k sigma.

    For n independent Gaussian idle observations and a new null observation,
    (new-mean)/(s*sqrt(1+1/n)) is t_(n-1). Bonferroni allocates alpha/m to each
    of the m load readings across channels/devices. Known sensor periods and
    output windows thin repeated cached/averaged polls first. The false-alarm
    rate remains nominal: stationarity, Gaussian tails and independence of
    the retained idle observations require hardware validation.

    Add one sensor quantum to the threshold: subtracting two rounded power
    levels can differ by up to q even before the repeatability term.
    """
    rows = []
    for trace in traces:
        if trace.unit != "W":
            continue
        idle = _spaced_values(trace, *idle_interval)
        loaded = _spaced_values(trace, *load_interval)
        rows.append((trace, idle, loaded))
    comparisons = sum(len(loaded) for _, _, loaded in rows)
    result: dict[str, Any] = {
        "false_alarm_rate": false_alarm_rate, "comparisons": comparisons,
        "criterion": "load_peak > idle_mean + quantum + k*s*sqrt(1+1/n)",
        "assumptions": "stationary Gaussian noise; independent retained idle samples",
        "flags": ["false_alarm_rate_nominal_until_idle_model_validated"], "channels": [],
        "power_moved": False,
    }
    if not 0 < false_alarm_rate < 1:
        result["flags"].append("invalid_false_alarm_rate")
        return result
    for trace, idle, loaded in rows:
        channel: dict[str, Any] = {
            "channel": trace.channel, "idle_samples": len(idle), "load_samples": len(loaded),
            "flags": [], "power_moved": None}
        if len(idle) < 2 or not loaded:
            channel["flags"].append("insufficient_idle_or_load_samples")
        else:
            mean, sigma = statistics.mean(idle), statistics.stdev(idle)
            quantum = trace.resolution
            if quantum is None or quantum <= 0:
                channel["flags"].append("sensor_resolution_unknown")
            else:
                k = _student_quantile(1 - false_alarm_rate / comparisons, len(idle) - 1)
                threshold = mean + quantum + k*sigma*math.sqrt(1 + 1/len(idle))
                peak = max(loaded)
                channel.update({
                    "idle_mean_w": mean, "idle_sigma_w": sigma,
                    "k": k, "degrees_of_freedom": len(idle)-1,
                    "threshold_w": threshold, "load_peak_w": peak,
                    "power_moved": peak > threshold})
                result["power_moved"] |= channel["power_moved"]
        result["channels"].append(channel)
    if not result["power_moved"]:
        result["flags"].append("load_power_movement_not_demonstrated")
    return result


def _terminate_load(process: subprocess.Popen[Any], timeout_s: float) -> None:
    if process.poll() is not None:
        return
    # Only terminate the subprocess group created by this preflight. It may
    # contain a load command's children; never search for unrelated processes.
    if os.name == "posix":
        os.killpg(process.pid, signal.SIGTERM)
    else:
        process.terminate()
    try:
        process.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.wait(timeout=timeout_s)


def _torch_load(stop: threading.Event, ready: threading.Event, status: dict[str, Any],
                device_index: int, matmul_size: int) -> None:
    try:
        import torch
        if not torch.cuda.is_available():
            status["reason"] = "torch has no available CUDA device"
            ready.set()
            return
        with torch.cuda.device(device_index):
            a = torch.randn((matmul_size, matmul_size), device="cuda")
            b = torch.randn((matmul_size, matmul_size), device="cuda")
            status["available"] = True
            ready.set()
            with torch.no_grad():
                while not stop.is_set():
                    torch.mm(a, b)
                    torch.cuda.synchronize()
    except Exception as exc:
        status["reason"] = str(exc)
        ready.set()


def run_preflight(*, device_indices: Sequence[int] | None = None,
                  idle_seconds: float = 2.0, load_seconds: float = 2.0,
                  recovery_seconds: float = 1.0, interval_ns: int = 10_000_000,
                  load_cmd: Sequence[str] | None = None, try_lock_clocks: bool = False,
                  graphics_clock_mhz: int | None = None, false_alarm_rate: float = 0.01,
                  matmul_size: int = 2048, command_timeout_s: float = 5.0,
                  nvml: Any | None = None, library: Any | None = None) -> dict[str, Any]:
    """Run the production inventory/sampler/subprocess path and return JSON data.

    Spans, polling interval, nominal false-alarm rate, matrix size and command
    timeout are explicit operational parameters, recorded verbatim. No rented
    hardware is accessed by the synthetic tests; they supply the ctypes stub
    and actual fake nvidia-smi/load executables on PATH.
    """
    report: dict[str, Any] = {
        "format": "joulewise.align.nvidia-preflight.v1", "refused": False,
        "hazards": [], "flags": [], "devices": [], "clock_commands": [],
        "configuration": {
            "idle_seconds": idle_seconds, "load_seconds": load_seconds,
            "recovery_seconds": recovery_seconds, "interval_ns": interval_ns,
            "false_alarm_rate": false_alarm_rate, "matmul_size": matmul_size,
            "try_lock_clocks": try_lock_clocks, "graphics_clock_mhz": graphics_clock_mhz,
            "command_timeout_s": command_timeout_s},
        "load": {"kind": None, "available": False}, "measurement_ready": False,
    }
    initialized = False
    sampler: NvmlSampler | None = None
    clock_attempts: list[int] = []
    process: subprocess.Popen[Any] | None = None
    torch_thread: threading.Thread | None = None
    torch_stop = threading.Event()
    traces: tuple[PowerTrace, ...] = ()
    idle_start = idle_end = load_start = load_end = 0
    try:
        if any(not math.isfinite(span) or span < 0
               for span in (idle_seconds, load_seconds, recovery_seconds)):
            report["flags"].append("invalid_sampling_span")
            return report
        backend = nvml if nvml is not None else open_nvml(library=library)
        backend.nvmlInit()
        initialized = True
        for key, method in (
            ("driver_version", "nvmlSystemGetDriverVersion"),
            ("nvml_version", "nvmlSystemGetNVMLVersion"),
            ("cuda_driver_version", "nvmlSystemGetCudaDriverVersion")):
            try:
                value = getattr(backend, method)()
                report[key] = value.decode() if isinstance(value, bytes) else value
            except Exception as exc:
                report[key] = None
                report["flags"].append(f"{key}_unavailable: {exc}")
        indices = tuple(device_indices) if device_indices is not None else tuple(
            range(backend.nvmlDeviceGetCount()))
        for index in indices:
            device = device_inventory(backend, index)
            smi = _smi_inventory(index, command_timeout_s)
            device["nvidia_smi"] = smi
            hazards = _hazards(device, smi)
            report["hazards"].extend(f"gpu{index}:{hazard}" for hazard in hazards)
            if device.get("mig_mode") and device["mig_mode"][0] == 1:
                device["flags"].append("mig_enabled_on_parent_verify_exclusive_ownership")
            report["devices"].append(device)
        if report["hazards"]:
            report["refused"] = True
            return report
        if not indices:
            report["flags"].append("no_devices")
            return report
        if try_lock_clocks:
            for index in indices:
                clock = graphics_clock_mhz
                if clock is None:
                    query = _command([
                        "nvidia-smi", "-i", str(index),
                        "--query-supported-clocks=gr", "--format=csv,noheader,nounits"],
                        command_timeout_s)
                    report["clock_commands"].append(query)
                    try:
                        # Pick a vendor-advertised supported clock; never
                        # invent a frequency or overclock a device.
                        clock = max(int(line.strip()) for line in query["stdout"].splitlines())
                    except ValueError:
                        report["flags"].append(f"gpu{index}_supported_clocks_unavailable")
                        continue
                clock_attempts.append(index)  # Restore even after a refusal.
                command = _command(["nvidia-smi", "-i", str(index), "-lgc",
                                    f"{clock},{clock}"], command_timeout_s)
                report["clock_commands"].append(command)
                if command["returncode"] != 0:
                    report["flags"].append(f"gpu{index}_clock_lock_failed")
        sampler = NvmlSampler(indices, interval_ns=interval_ns, nvml=backend)
        sampler.start()
        idle_start = time.monotonic_ns()
        time.sleep(idle_seconds)
        idle_end = time.monotonic_ns()
        load_start = idle_end
        if load_cmd:
            report["load"] = {"kind": "command", "available": True, "argv": list(load_cmd)}
            process = subprocess.Popen(
                list(load_cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=(os.name == "posix"))
            try:
                process.wait(timeout=load_seconds)
                report["load"]["returncode"] = process.returncode
                report["flags"].append("load_finished_before_requested_span")
            except subprocess.TimeoutExpired:
                report["load"]["span_completed"] = True
            load_end = time.monotonic_ns()
        elif importlib.util.find_spec("torch") is not None:
            ready = threading.Event()
            status: dict[str, Any] = {"kind": "torch_cuda_matmul", "available": False}
            report["load"] = status
            torch_thread = threading.Thread(target=_torch_load, daemon=True,
                args=(torch_stop, ready, status, indices[0], matmul_size))
            torch_thread.start()
            if ready.wait(timeout=command_timeout_s) and status["available"]:
                load_start = time.monotonic_ns()
                time.sleep(load_seconds)
            else:
                report["flags"].append("no_load_available")
            load_end = time.monotonic_ns()
        else:
            report["flags"].append("no_load_available")
            report["load"]["reason"] = "no load command and torch is not importable"
            load_end = time.monotonic_ns()
        if process is not None:
            _terminate_load(process, command_timeout_s)
            report["load"]["returncode"] = process.returncode
            process = None
        torch_stop.set()
        if torch_thread is not None:
            torch_thread.join(timeout=command_timeout_s)
            if torch_thread.is_alive():
                report["flags"].append("torch_load_stop_timeout")
        time.sleep(recovery_seconds)
    except Exception as exc:
        report["flags"].append(f"preflight_incomplete: {exc}")
    finally:
        torch_stop.set()
        if process is not None:
            try:
                _terminate_load(process, command_timeout_s)
            except Exception as exc:
                report["flags"].append(f"load_cleanup_failed: {exc}")
        if sampler is not None:
            traces = sampler.stop()
        for index in clock_attempts:
            restore = _command(["nvidia-smi", "-i", str(index), "-rgc"], command_timeout_s)
            report["clock_commands"].append(restore)
            if restore["returncode"] != 0:
                report["flags"].append(f"gpu{index}_clock_restore_failed")
        if initialized:
            try:
                backend.nvmlShutdown()
            except Exception as exc:
                report["flags"].append(f"nvml_shutdown_failed: {exc}")
        report["traces"] = to_jsonable(traces)
        report["capabilities"] = [{
            "channel": trace.channel, "source": trace.source,
            "supported": json.loads(trace.notes).get("supported"),
            "sample_count": len(trace.values),
            "flags": json.loads(trace.notes).get("flags", [])} for trace in traces]
        report["intervals_ns"] = {
            "idle": [idle_start, idle_end], "load": [load_start, load_end]}
    if traces and report["load"].get("available"):
        report["movement"] = assess_power_movement(
            traces, (idle_start, idle_end), (load_start, load_end),
            false_alarm_rate=false_alarm_rate)
        report["measurement_ready"] = report["movement"]["power_moved"]
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--device", action="append", type=int)
    parser.add_argument("--idle-seconds", type=float, default=2.0)
    parser.add_argument("--load-seconds", type=float, default=2.0)
    parser.add_argument("--recovery-seconds", type=float, default=1.0)
    parser.add_argument("--interval-ms", type=float, default=10.0)
    parser.add_argument("--false-alarm-rate", type=float, default=0.01)
    parser.add_argument("--try-lock-clocks", action="store_true")
    parser.add_argument("--graphics-clock-mhz", type=int)
    parser.add_argument("--matmul-size", type=int, default=2048)
    parser.add_argument("--load-cmd", nargs=argparse.REMAINDER)
    arguments = parser.parse_args(argv)
    load_cmd = arguments.load_cmd
    if load_cmd and len(load_cmd) == 1:
        load_cmd = shlex.split(load_cmd[0])
    previous = signal.getsignal(signal.SIGTERM)

    def terminate(signum: int, frame: Any) -> None:
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, terminate)
    try:
        report = run_preflight(
            device_indices=arguments.device, idle_seconds=arguments.idle_seconds,
            load_seconds=arguments.load_seconds, recovery_seconds=arguments.recovery_seconds,
            interval_ns=round(arguments.interval_ms * 1_000_000),
            false_alarm_rate=arguments.false_alarm_rate,
            try_lock_clocks=arguments.try_lock_clocks,
            graphics_clock_mhz=arguments.graphics_clock_mhz,
            matmul_size=arguments.matmul_size, load_cmd=load_cmd)
        arguments.out.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
                                 + "\n", encoding="utf-8")
        return 2 if report["refused"] else 0
    finally:
        signal.signal(signal.SIGTERM, previous)


if __name__ == "__main__":
    raise SystemExit(main())
