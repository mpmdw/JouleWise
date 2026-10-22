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
import sys
import tempfile
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Sequence

from joulewise.align.power.duty import _student_quantile
from joulewise.align.power.nvml import NvmlSampler, _decoded, _scalar_int, device_inventory, open_nvml
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
    if mode in (2, 3, 4) or "vgpu" in name.lower() or "vgpu" in smi_mode:
        hazards.append("virtual_gpu_hides_or_shares_board_power")
    return hazards


def _spaced_values(trace: PowerTrace, start: int, end: int) -> list[float]:
    notes = json.loads(trace.notes)
    facts = notes.get("sensor_facts") or {}
    spacing = max(trace.nominal_interval_ns, facts.get("period_ns") or 0,
                  notes.get("output_averaging_window_ns") or 0)
    timestamps = trace.t_ns
    brackets = notes.get("window_timing_half_width_ns", notes.get("timing_half_width_ns"))
    if brackets is None:
        if any(flag in notes.get("flags", ()) for flag in (
                "sensor_update_phase_unreported", "driver_field_timestamp_is_wall_clock")):
            return []
        brackets = [0]*len(trace.values)
    if brackets is None or len(timestamps) != len(trace.values) or len(brackets) != len(trace.values):
        return []
    width = notes.get("output_averaging_window_ns") or trace.averaging_window_ns or 0
    selected = []
    last: int | None = None
    for timestamp, value, bracket in zip(timestamps, trace.values, brackets):
        # All of a physical observation's support and endpoint uncertainty
        # must belong to the phase; cached idle means cannot prove load work.
        if bracket is not None and start <= timestamp-width-bracket and timestamp+bracket < end and math.isfinite(value):
            if last is None or timestamp-last >= spacing:
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


def _terminate_load(process: subprocess.Popen[Any], timeout_s: float) -> dict[str, Any]:
    receipt: dict[str, Any] = {"group": process.pid, "kill_escalated": False}
    if os.name != "posix":
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=timeout_s)
            except subprocess.TimeoutExpired:
                receipt["kill_escalated"] = True
                process.kill()
        process.wait(timeout=timeout_s)
        return receipt

    def present() -> bool:
        try:
            os.killpg(process.pid, 0)
            return True
        except ProcessLookupError:
            return False

    # The session/group was created by this exact Popen, so its identity is
    # retained even if the leader exited before a child. Do not use leader
    # poll() as evidence that all owned GPU work stopped.
    if present():
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.monotonic()+timeout_s
    while present() and time.monotonic() < deadline:
        process.poll()  # Reap an exited leader while waiting for its children.
        threading.Event().wait(min(0.01, max(0.0, deadline-time.monotonic())))
    if present():
        receipt["kill_escalated"] = True
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=timeout_s)
    receipt["group_present_after_kill"] = present()
    # A surviving group can consist of zombies awaiting the host's reaper;
    # preserve this diagnostic rather than claiming verified disappearance.
    return receipt


def _torch_command(device_index: int, matmul_size: int, ready_path: Path) -> list[str]:
    # CUDA initialization and allocations occur in a killable owned process,
    # never in an unkillable thread in the preflight controller.
    code = """
import json, os, sys
from pathlib import Path
ready = Path(sys.argv[1])
def publish(value):
    pending = ready.with_suffix(".pending")
    pending.write_text(json.dumps(value))
    os.replace(pending, ready)
try:
    import torch
    if not torch.cuda.is_available():
        publish({"available": False, "reason": "torch has no CUDA device"})
        raise SystemExit(0)
    with torch.cuda.device(int(sys.argv[2])):
        size = int(sys.argv[3])
        a = torch.randn((size, size), device="cuda")
        b = torch.randn((size, size), device="cuda")
        torch.cuda.synchronize()
        publish({"available": True})
        with torch.no_grad():
            while True:
                torch.mm(a, b)
                torch.cuda.synchronize()
except Exception as exc:
    publish({"available": False, "reason": str(exc)})
"""
    return [sys.executable, "-c", code, str(ready_path), str(device_index), str(matmul_size)]


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
        "clock_restore_policy": "driver_defaults_via_rgc",
    }
    initialized = False
    sampler: NvmlSampler | None = None
    clock_attempts: list[int] = []
    process: subprocess.Popen[Any] | None = None
    load_directory: tempfile.TemporaryDirectory[str] | None = None
    traces: tuple[PowerTrace, ...] = ()
    idle_start = idle_end = load_start = load_end = 0
    try:
        if any(not math.isfinite(span) or span < 0
               for span in (idle_seconds, load_seconds, recovery_seconds)):
            report["flags"].append("invalid_sampling_span")
            return report
        if interval_ns <= 0 or command_timeout_s <= 0 or matmul_size <= 0:
            report["flags"].append("invalid_operational_parameter")
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
                report[key] = _decoded(value)
            except Exception as exc:
                report[key] = None
                report["flags"].append(f"{key}_unavailable: {exc}")
        indices = tuple(device_indices) if device_indices is not None else tuple(
            range(_scalar_int(backend.nvmlDeviceGetCount())))
        for index in indices:
            device = device_inventory(backend, index)
            smi = _smi_inventory(index, command_timeout_s)
            device["nvidia_smi"] = smi
            smi_mode = str(smi.get("virtualization_mode") or "").lower()
            if device.get("virtualization_mode") not in (None, 0, 1, 2, 3, 4):
                device["flags"].append("virtualization_mode_unknown")
            if smi_mode and smi_mode not in (
                    "none", "pass through", "passthrough", "n/a", "not supported") and "vgpu" not in smi_mode:
                device["flags"].append("virtualization_evidence_unknown")
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
            report["flags"].append("prior_clock_lock_unobservable_restore_to_driver_defaults")
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
        command: list[str] | None = list(load_cmd) if load_cmd else None
        if command:
            report["load"] = {"kind": "command", "available": True, "argv": command}
        elif importlib.util.find_spec("torch") is not None:
            load_directory = tempfile.TemporaryDirectory(prefix="joulewise-preflight-load-")
            ready_path = Path(load_directory.name)/"ready.json"
            command = _torch_command(indices[0], matmul_size, ready_path)
            report["load"] = {"kind": "torch_cuda_matmul", "available": False}
        else:
            report["flags"].append("no_load_available")
            report["load"]["reason"] = "no load command and torch is not importable"
        if command is not None:
            process = subprocess.Popen(
                command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=(os.name == "posix"))
            if report["load"]["kind"] == "torch_cuda_matmul":
                ready_deadline = time.monotonic()+command_timeout_s
                while not ready_path.exists() and process.poll() is None and time.monotonic() < ready_deadline:
                    threading.Event().wait(interval_ns/1_000_000_000)
                if ready_path.exists():
                    report["load"].update(json.loads(ready_path.read_text()))
                else:
                    report["load"]["reason"] = "CUDA load did not become ready"
                if not report["load"]["available"]:
                    report["flags"].append("no_load_available")
            if report["load"]["available"]:
                load_start = time.monotonic_ns()
                try:
                    process.wait(timeout=load_seconds)
                    report["flags"].append("load_finished_before_requested_span")
                    if process.returncode != 0:
                        report["flags"].append("load_command_failed")
                        report["load"]["available"] = False
                except subprocess.TimeoutExpired:
                    report["load"]["span_completed"] = True
                load_end = time.monotonic_ns()
            report["load"]["cleanup"] = _terminate_load(process, command_timeout_s)
            report["load"]["returncode"] = process.returncode
            process = None
        else:
            load_end = time.monotonic_ns()
        time.sleep(recovery_seconds)
    except Exception as exc:
        report["flags"].append(f"preflight_incomplete: {exc}")
    finally:
        if process is not None:
            try:
                report["load"]["cleanup"] = _terminate_load(process, command_timeout_s)
            except Exception as exc:
                report["flags"].append(f"load_cleanup_failed: {exc}")
        if load_directory is not None:
            load_directory.cleanup()
        if sampler is not None:
            traces = sampler.stop()
        for index in clock_attempts:
            restore = _command(["nvidia-smi", "-i", str(index), "-rgc"], command_timeout_s)
            report["clock_commands"].append(restore)
            if restore["returncode"] != 0:
                report["flags"].append(f"gpu{index}_clock_restore_failed")
        if initialized:
            cleanup = sampler._cleanup_thread if sampler is not None else None
            cleanup_active = cleanup is not None and cleanup.is_alive()
            workers = ([device.thread for device in sampler._devices
                        if device.thread is not None and device.thread.is_alive()]
                       if sampler is not None else [])
            # A sampler fallback can still own its init reference, including
            # when creating its deferred cleanup thread failed. Transfer that
            # reference together with preflight's own; never shut down under
            # an outstanding native call merely because its owner did not start.
            references = 1 + int(sampler is not None and sampler._initialized)

            def finish_shutdown() -> None:
                if cleanup_active:
                    cleanup.join()
                for worker in workers:
                    worker.join()
                for _ in range(references):
                    try:
                        backend.nvmlShutdown()
                    except Exception as exc:
                        report["flags"].append(f"nvml_shutdown_failed: {exc}")

            if workers or cleanup_active:
                report["flags"].append("preflight_shutdown_deferred_worker_active")
                try:
                    owner = threading.Thread(
                        target=finish_shutdown, daemon=True,
                        name="joulewise-preflight-nvml-cleanup")
                    owner.start()
                except Exception as exc:
                    # Exhausted thread resources cannot justify racing a
                    # blocked driver. Retain the native references and report
                    # them; process exit remains the final resource owner.
                    report["flags"].append(f"native_references_retained: {references}; {exc}")
                else:
                    if sampler is not None:
                        sampler._initialized = False
            else:
                finish_shutdown()
                if sampler is not None:
                    sampler._initialized = False
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
        moved = {row["channel"].split(":")[0] for row in report["movement"]["channels"]
                 if row["power_moved"]}
        report["measurement_ready"] = all(f"gpu{index}" in moved for index in indices)
        for index in indices:
            if f"gpu{index}" not in moved:
                report["flags"].append(f"gpu{index}_load_power_movement_not_demonstrated")
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
