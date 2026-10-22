"""Run a provider-neutral GPU session and preserve every outcome in a bundle.

A custom runner command is an argv template, not shell text. The default uses
the provisional runner-format adapter and documented CLI. Missing runner,
sampler or router capture stays visible while the parallel lanes integrate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import xml.etree.ElementTree as ET
import uuid
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence
from urllib.error import URLError
from urllib.request import urlopen

from joulewise.align.gpukit.matrix import expand, load_matrix
from joulewise.align.gpukit.cost import calibration_slice
from joulewise.align.gpukit.throttle import snapshot, compare
from joulewise.align.gpukit.runner_adapter import write_runner_matrix
from joulewise.align.records import read_episodes

VLLM_VERSION = "0.10.2"  # Operator-selected reproducibility pin; no hardware compatibility claim.


class IsolationError(RuntimeError):
    """MIG/vGPU is explicitly excluded by the campaign brief."""


@dataclass(frozen=True)
class SessionOptions:
    matrix: Path
    output: Path
    runner_command: tuple[str, ...]
    ready_timeout_s: float
    poll_s: float
    command_timeout_s: float
    runner_timeout_s: float
    monitor_placement: str
    preflight_command: tuple[str, ...] = ()
    ready_command: tuple[str, ...] = ()
    vllm_command: tuple[str, ...] = ("vllm",)
    gpu_index: int = 0
    port: int = 8000
    destination: str | None = None
    copy_kind: str = "rsync"
    runner_settings: Path | None = None
    gpu_indices: tuple[int, ...] = ()
    monitor_base_url: str | None = None
    judge_base_url: str | None = None
    monitor_gpu_index: int | None = None
    monitor_port: int | None = None
    calibration_slice: bool = False


def whole_gpu(*, gpu_index: int, timeout_s: float) -> dict[str, Any]:
    """Inspect the selected physical GPU; retain unavailable evidence as flags."""
    evidence: dict[str, Any] = {"gpu_index": gpu_index, "flags": []}
    try:
        raw = subprocess.run(["nvidia-smi", "-i", str(gpu_index), "-q", "-x"],
                             capture_output=True, text=True, timeout=timeout_s, check=False)
        if raw.returncode:
            evidence["flags"].append("gpu_inventory_command_failed")
            return evidence
        root = ET.fromstring(raw.stdout)
        gpu = root.find("gpu")
        if gpu is None:
            evidence["flags"].append("gpu_inventory_missing")
            return evidence
        evidence.update(name=gpu.findtext("product_name"), uuid=gpu.findtext("uuid"),
                        driver=root.findtext("driver_version"),
                        mig=gpu.findtext("mig_mode/current_mig"),
                        virtualization=gpu.findtext("gpu_virtualization_mode/virtualization_mode"))
        mig = (evidence["mig"] or "").strip().lower()
        virtualization = "".join(c for c in (evidence["virtualization"] or "").lower() if c.isalnum())
        if mig == "enabled" or "mig-" in (evidence["uuid"] or "").lower():
            raise IsolationError("MIG enabled: whole GPU required")
        if virtualization in ("vgpu", "hostvgpu", "guestvgpu") or "vgpu" in virtualization:
            raise IsolationError("vGPU detected: whole GPU required")
        if mig not in ("disabled", "n/a", "[n/a]"):
            evidence["flags"].append("gpu_mig_state_unverified")
        if virtualization not in ("none", "passthrough"):
            evidence["flags"].append("gpu_virtualization_unverified")
    except (OSError, subprocess.TimeoutExpired, ET.ParseError) as exc:
        evidence["flags"].append(f"gpu_inventory_unavailable:{type(exc).__name__}")
    return evidence


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
                    encoding="utf-8")


def _command(argv: Sequence[str], log: Path, *, timeout_s: float) -> int:
    """Capture command output without ever expanding shell substitutions."""
    try:
        with log.open("wb") as handle:
            result = subprocess.run(list(argv), stdout=handle, stderr=subprocess.STDOUT,
                                    timeout=timeout_s, check=False)
        return result.returncode
    except (OSError, subprocess.TimeoutExpired) as exc:
        with log.open("ab") as handle:
            handle.write((f"command_failed:{type(exc).__name__}\n").encode())
        return -1


def _healthy(url: str, timeout_s: float) -> bool:
    try:
        with urlopen(url, timeout=timeout_s) as response:
            return response.status == 200
    except (OSError, URLError):
        return False


def wait_ready(process: subprocess.Popen, endpoint: str, *, timeout_s: float,
               poll_s: float, ready_command: Sequence[str], log: Path,
               probe: Callable[[str, float], bool] = _healthy) -> tuple[str, ...]:
    """Bound readiness by caller-supplied load timeout and polling cadence."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return ("endpoint_exited_before_ready",)
        if ready_command:
            # Poll cadence is not a subprocess-startup deadline. A readiness
            # command gets the remaining model-load budget, then cadence applies.
            remaining = max(0.0, deadline - time.monotonic())
            if _command(ready_command, log, timeout_s=remaining) == 0:
                return ()
        elif probe(endpoint + "/health", min(poll_s, timeout_s)):
            return ()
        time.sleep(poll_s)
    return ("endpoint_readiness_timeout",)


def package_results(directory: Path) -> tuple[Path, Path]:
    """Hash every regular output file, then tar it with its SHA-256 manifest.

    The manifest cannot hash itself. The detached archive hash covers both the
    manifest and the payload. Symlinks are flagged by the session, never followed.
    """
    directory = directory.resolve()
    rows = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and not path.is_symlink() and path != directory / "manifest.json":
            raw = path.read_bytes()
            rows.append({"path": path.relative_to(directory).as_posix(),
                         "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    _json(directory / "manifest.json", {"algorithm": "sha256", "files": rows})
    archive = directory.with_name(directory.name + ".tar.gz")
    checksum = archive.with_name(archive.name + ".sha256")
    # Exclusive creation preserves earlier sessions and their raw evidence.
    with archive.open("xb") as stream:
        with tarfile.open(fileobj=stream, mode="w:gz") as bundle:
            for row in rows:
                bundle.add(directory / row["path"], arcname=directory.name + "/" + row["path"],
                           recursive=False)
            bundle.add(directory / "manifest.json", arcname=directory.name + "/manifest.json")
    checksum.write_text(hashlib.sha256(archive.read_bytes()).hexdigest() + "  " + archive.name + "\n",
                        encoding="ascii")
    return archive, checksum


def verify_manifest(directory: Path) -> tuple[str, ...]:
    """Verify inventory and bytes after extraction without trusting manifest paths."""
    directory = directory.resolve()
    flags: list[str] = []
    try:
        data = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        expected = set()
        for row in data["files"]:
            relative = Path(row["path"])
            if relative.is_absolute() or ".." in relative.parts:
                flags.append("manifest_path_invalid")
                continue
            path = directory / relative
            expected.add(relative.as_posix())
            if path.is_symlink() or not path.is_file():
                flags.append(f"manifest_file_missing:{relative}")
                continue
            raw = path.read_bytes()
            if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
                flags.append(f"manifest_bytes_changed:{relative}")
        actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*")
                  if p.is_file() and p != directory / "manifest.json"}
        if actual != expected:
            flags.append("manifest_inventory_changed")
    except (OSError, ValueError, KeyError, TypeError):
        flags.append("manifest_unreadable")
    return tuple(sorted(set(flags)))


def copy_back(paths: Sequence[Path], *, kind: str, destination: str,
              log: Path, timeout_s: float) -> tuple[str, ...]:
    """Copy archive and detached hash using ambient operator authentication."""
    if kind == "local":
        try:
            target = Path(destination)
            target.mkdir(parents=True, exist_ok=True)
            for path in paths:
                shutil.copy2(path, target / path.name)
            return ()
        except OSError as exc:
            return (f"copy_failed:{type(exc).__name__}",)
    if kind == "rsync":
        command = ["rsync", "--archive", "--", *(str(p) for p in paths), destination]
        code = _command(command, log, timeout_s=timeout_s)
    elif kind == "s3":
        codes = [_command(["aws", "s3", "cp", str(path),
                           destination.rstrip("/") + "/" + path.name],
                          log.with_name(log.stem + "-" + str(i) + log.suffix),
                          timeout_s=timeout_s) for i, path in enumerate(paths)]
        code = next((c for c in codes if c), 0)
    else:
        return ("copy_kind_unknown",)
    return () if code == 0 else ("copy_failed",)


# Runner failures use dotted names. Usage/clock/tool failures also invalidate a
# physical work record; monitor/score errors are retained but do not erase the
# agent/power product (off-box scoring can be deferred).
def _incomplete_flag(flag: str) -> bool:
    return (flag.startswith(("endpoint_", "runner_", "episode_", "model_run_failed",
                             "budget_runner_", "endpoint.error.", "runner.error.",
                             "factory.error.", "task.setup_error.", "sampler.",
                             "usage.", "clock.", "tool.", "token_counter.error."))
            or ".factory_error." in flag
            or flag in {"episode.interrupted", "episode.max_turns",
                        "power.empty", "condition.unknown"}) and flag != "runner_adapter_provisional"


def _validate_output(path: Path, *, expected_count: int, router: bool, model: str,
                     expected_coordinates: Sequence[tuple[str, str, int]] = (),
                     measured_devices: Sequence[int] = ()) -> tuple[str, ...]:
    """Check coordinates, usable turns and non-mock power spanning each episode."""
    flags: list[str] = []
    try:
        episodes = read_episodes(path)
        if len(episodes) != expected_count:
            flags.append("runner_episode_count_mismatch")
        if len({e.episode_id for e in episodes}) != len(episodes):
            flags.append("runner_duplicate_episode_ids")
        actual = Counter((e.task_pair, e.condition, e.seed) for e in episodes)
        if expected_coordinates and actual != Counter(expected_coordinates):
            flags.append("runner_episode_coordinates_mismatch")
        for episode in episodes:
            # ChatEndpoint guarantees identity, not a .model attribute; the runner
            # may therefore put a serving identity containing the model ID here.
            identity = episode.agent_model
            if identity != model and not any(
                    model + separator in identity for separator in ("@", ":", "|", " ")):
                if not identity.endswith(model):
                    flags.append("runner_episode_model_mismatch")
            flags.extend(episode.flags)
            if not episode.turns:
                flags.append("episode_turns_missing")
            if not episode.power_traces:
                flags.append("episode_power_missing")
            for device in measured_devices:
                if not any(re.match(r"^gpu" + str(device) + r"(?=$|[^0-9])", t.channel)
                           and t.source != "mock" for t in episode.power_traces):
                    flags.append("episode_measured_device_power_missing:" + str(device))
            for trace in episode.power_traces:
                if trace.source == "mock":
                    flags.append("episode_power_mock")
                if not trace.t_ns:
                    flags.append("episode_power_missing")
                    continue
                offset = 0
                if trace.clock_domain != episode.clock_domain:
                    mappings = [m for m in episode.clock_mappings
                                if m.trace_domain == trace.clock_domain
                                and m.episode_domain == episode.clock_domain]
                    if not mappings:
                        flags.append("episode_power_clock_unmapped")
                        continue
                    offset = mappings[0].offset_ns
                # A sensor polled at interval I with averaging window W has a
                # reading within I + W of a boundary. This is the coverage bar,
                # not an arbitrary duration fraction or an interpolation claim.
                slack = trace.nominal_interval_ns + (trace.averaging_window_ns or 0)
                if (trace.nominal_interval_ns <= 0 or slack < 0
                        or trace.t_ns[0] + offset > episode.start_ns + slack
                        or trace.t_ns[-1] + offset < episode.end_ns - slack):
                    flags.append("episode_power_coverage_incomplete")
            if router and episode.router_log is None:
                flags.append("episode_router_log_missing")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        flags.append(f"runner_output_unreadable:{type(exc).__name__}")
    return tuple(sorted(set(flags)))


def _stop_group(process: subprocess.Popen, *, grace_s: float) -> None:
    """Terminate the serving/runner session including children of an exited parent."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=grace_s)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        pass
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def _runner_command(argv: Sequence[str], log: Path, *, timeout_s: float,
                    grace_s: float) -> tuple[int, bool]:
    """A runner owns a process group; a timeout must stop its samplers too."""
    with log.open("wb") as handle:
        process = subprocess.Popen(list(argv), stdout=handle, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        timed_out = False
        try:
            code = process.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            timed_out = True
            code = -1
        finally:
            _stop_group(process, grace_s=grace_s)
    return code, timed_out


def _serve_argv(options: SessionOptions, model: dict[str, Any], port: int) -> list[str]:
    argv = [*options.vllm_command, "serve", model.get("checkpoint", model["id"]),
            "--host", "127.0.0.1", "--port", str(port),
            "--served-model-name", model["id"],
            "--tensor-parallel-size", str(model.get("tensor_parallel_size", 1)),
            "--dtype", "bfloat16", "--enable-auto-tool-choice",
            "--tool-call-parser", "hermes"]
    if model.get("weight_precision", "bf16") == "fp8":
        argv += ["--quantization", "fp8"]
    if model["id"].startswith("Qwen/"):
        argv += ["--reasoning-parser", "qwen3"]
    if model.get("revision"):
        argv += ["--revision", model["revision"]]
    return argv


def run_session(options: SessionOptions, *,
                probe: Callable[[str, float], bool] = _healthy) -> dict[str, Any]:
    """Run serial agent models with an explicitly placed, unsampled monitor.

    MIG/vGPU and absent/refused NVML preflight refuse before any model starts.
    Other unavailable integration is recorded and raw results are still sealed.
    """
    output = options.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    flags: list[str] = []
    receipt: dict[str, Any] = {
        "schema": "joulewise.align.gpukit.session.v2", "status": "incomplete",
        "session_id": uuid.uuid4().hex, "flags": flags, "models": [],
        "data_complete": False, "start_ns": time.monotonic_ns(),
        "data_complete_meaning": "Every planned coordinate exactly once per model, usable turns without runner failures, and non-mock power covering every measured device and episode; scoring may be deferred.",
        "monitor_placement": options.monitor_placement,
    }
    monitor_process = None
    monitor_log = None
    try:
        matrix, matrix_flags = load_matrix(options.matrix)
        if options.calibration_slice and matrix and not matrix_flags:
            matrix = calibration_slice(matrix)
            receipt["calibration_slice"] = "All models and task/condition strata, first seed; no throughput assumption."
        flags.extend(matrix_flags)
        settings: dict[str, Any] = {}
        if options.runner_settings:
            try:
                settings = json.loads(options.runner_settings.read_text(encoding="utf-8"))
                if not isinstance(settings, dict):
                    settings = {}
                    flags.append("runner_settings_invalid")
            except (OSError, ValueError) as exc:
                flags.append(f"runner_settings_unreadable:{type(exc).__name__}")
        runner_command = options.runner_command or (
            sys.executable, "-m", "joulewise.align", "run", "--matrix", "{runner_matrix}")
        if not options.runner_command and not settings:
            flags.append("runner_settings_missing")
            matrix_flags = (*matrix_flags, "runner_settings_missing")
        for argv, name in (([sys.executable, "-m", "pip", "freeze"], "packages"),
                           (["git", "rev-parse", "HEAD"], "repository-head")):
            if _command(argv, output / (name + ".log"), timeout_s=options.command_timeout_s):
                flags.append(name + "_provenance_unavailable")
        if matrix:
            _json(output / "matrix.json", matrix)
            flags.extend(matrix.get("flags", ()))
        maximum = max((m.get("tensor_parallel_size", 1) for m in matrix.get("models", [])), default=1)
        measured = list(options.gpu_indices or tuple(range(options.gpu_index, options.gpu_index + maximum)))
        receipt["measured_gpu_indices"] = measured
        if len(set(measured)) != len(measured) or len(measured) < maximum:
            flags.append("runner_measured_gpu_layout_invalid")
            matrix_flags = (*matrix_flags, "runner_measured_gpu_layout_invalid")
        placement = options.monitor_placement
        monitor_endpoint = None
        judge_endpoint = None
        monitor_gpu = options.monitor_gpu_index
        monitor_model = {"id": matrix.get("monitor_model", ""), "tensor_parallel_size": 1}
        if placement == "external":
            monitor_endpoint = options.monitor_base_url
            judge_endpoint = options.judge_base_url or monitor_endpoint
            if not monitor_endpoint:
                flags.append("monitor_external_url_missing")
        elif placement == "gpu":
            if monitor_gpu is None or options.monitor_port is None or options.monitor_port == options.port:
                flags.append("monitor_gpu_settings_missing")
            elif monitor_gpu in measured:
                flags.append("monitor_measured_gpu_overlap")
            else:
                monitor_endpoint = f"http://127.0.0.1:{options.monitor_port}"
                judge_endpoint = monitor_endpoint
        elif placement != "none":
            flags.append("monitor_placement_unknown")
        inventory = []
        indices = measured + ([monitor_gpu] if placement == "gpu" and monitor_gpu is not None else [])
        try:
            for device in dict.fromkeys(indices):
                row = whole_gpu(gpu_index=device, timeout_s=options.command_timeout_s)
                inventory.append(row)
                flags.extend(row["flags"])
        except IsolationError as exc:
            flags.append("whole_gpu_required")
            receipt.update(status="refused", isolation_reason=str(exc))
        receipt["hardware"] = inventory
        receipt["throttle_start"] = [snapshot(gpu_index=i, directory=output,
                                              label="session-start", timeout_s=options.command_timeout_s)
                                     for i in measured]
        for row in receipt["throttle_start"]:
            flags.extend(row["flags"])
        preflight_path = output / "preflight.json"
        preflight = [*(options.preflight_command or (
            sys.executable, "-m", "joulewise.align.power.preflight")), "--out", str(preflight_path)]
        for device in measured:
            preflight += ["--device", str(device)]
        receipt["preflight_argv"] = preflight
        if receipt["status"] != "refused":
            code = _command(preflight, output / "preflight.log", timeout_s=options.command_timeout_s)
            receipt["preflight_returncode"] = code
            try:
                report = json.loads(preflight_path.read_text(encoding="utf-8"))
                if not isinstance(report, dict) or type(report.get("refused")) is not bool:
                    raise ValueError("preflight verdict missing")
                receipt["preflight"] = {k: report.get(k) for k in ("refused", "measurement_ready", "flags")}
                flags.extend(report.get("flags", ()))
                if report["refused"]:
                    flags.append("nvml_preflight_refused")
                    receipt["status"] = "refused"
                elif code:
                    flags.append("nvml_preflight_command_failed_with_report")
            except (OSError, ValueError, TypeError):
                flags.append("nvml_preflight_unavailable")
                receipt["status"] = "refused"
        executable = bool(matrix and not matrix_flags and receipt["status"] != "refused")
        if executable and placement == "gpu" and monitor_endpoint is not None:
            monitor_log = (output / "monitor-server.log").open("wb")
            monitor_argv = _serve_argv(options, monitor_model, options.monitor_port)
            receipt["monitor_server"] = {"argv": monitor_argv, "gpu_index": monitor_gpu}
            try:
                monitor_process = subprocess.Popen(
                    monitor_argv, stdout=monitor_log, stderr=subprocess.STDOUT,
                    env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(monitor_gpu)), start_new_session=True)
                ready = wait_ready(monitor_process, monitor_endpoint,
                                   timeout_s=options.ready_timeout_s, poll_s=options.poll_s,
                                   ready_command=options.ready_command,
                                   log=output / "monitor-readiness.log", probe=probe)
                flags.extend("monitor_" + f for f in ready)
                if ready:
                    monitor_endpoint = judge_endpoint = None
            except OSError as exc:
                flags.append("monitor_server_failed:" + type(exc).__name__)
                monitor_endpoint = judge_endpoint = None
        receipt["monitor_base_url"] = monitor_endpoint
        receipt["judge_base_url"] = judge_endpoint
        if monitor_endpoint is None:
            flags.extend(("monitoring_deferred", "judging_deferred"))
        if executable:
            for index, model in enumerate(matrix["models"]):
                model_dir = output / f"model-{index}"
                model_dir.mkdir()
                devices = measured[:model.get("tensor_parallel_size", 1)]
                endpoint = f"http://127.0.0.1:{options.port}"
                model_receipt: dict[str, Any] = {
                    "model": model["id"], "flags": [], "measured_gpu_indices": devices}
                receipt["models"].append(model_receipt)
                runner_path = model_dir / "runner-matrix.json"
                if settings or not options.runner_command:
                    adapter_flags = write_runner_matrix(
                        runner_path, matrix, model=model["id"], endpoint=endpoint,
                        output_dir=model_dir, settings=settings, session_id=receipt["session_id"],
                        monitor_endpoint=monitor_endpoint, judge_endpoint=judge_endpoint,
                        device_indices=devices)
                    model_receipt["flags"].extend(adapter_flags)
                    if any(f != "runner_adapter_provisional" for f in adapter_flags):
                        flags.extend(model_receipt["flags"])
                        continue
                before = [snapshot(gpu_index=i, directory=model_dir, label="before",
                                   timeout_s=options.command_timeout_s) for i in devices]
                model_receipt["throttle_before"] = before
                argv = _serve_argv(options, model, options.port)
                model_receipt["server_argv"] = argv
                if not model.get("revision"):
                    model_receipt["flags"].append("model_revision_unpinned")
                process = None
                try:
                    with (model_dir / "server.log").open("wb") as server_log:
                        process = subprocess.Popen(
                            argv, stdout=server_log, stderr=subprocess.STDOUT,
                            env=dict(os.environ, CUDA_VISIBLE_DEVICES=",".join(map(str, devices))),
                            start_new_session=True)
                        ready = wait_ready(process, endpoint, timeout_s=options.ready_timeout_s,
                                           poll_s=options.poll_s, ready_command=options.ready_command,
                                           log=model_dir / "readiness.log", probe=probe)
                        model_receipt["flags"].extend(ready)
                        if not ready:
                            mapping = {
                                "matrix": str(output / "matrix.json"), "model": model["id"],
                                "runner_matrix": str(runner_path), "endpoint": endpoint,
                                "output": str(model_dir / "episodes.jsonl"),
                                "sample_interval_ns": str(matrix["sampling"]["interval_ns"]),
                                "router_logging": str(matrix["kind"] == "moe_stage_a").lower(),
                                "monitor_base_url": monitor_endpoint or "",
                                "judge_base_url": judge_endpoint or "",
                                "device_indices": json.dumps(devices),
                                "session_id": receipt["session_id"]}
                            command = [part.format_map(mapping) for part in runner_command]
                            code, timed_out = _runner_command(
                                command, model_dir / "runner.log",
                                timeout_s=options.runner_timeout_s, grace_s=options.poll_s)
                            model_receipt["runner_returncode"] = code
                            if code:
                                model_receipt["flags"].append("runner_command_failed")
                            if timed_out:
                                model_receipt["flags"].append("runner_timeout")
                            expected = matrix.get("measured_episode_count", matrix["episode_count"])
                            expected //= len(matrix["models"])
                            model_receipt["flags"].extend(_validate_output(
                                model_dir / "episodes.jsonl", expected_count=expected,
                                router=matrix["kind"] == "moe_stage_a", model=model["id"],
                                measured_devices=devices, expected_coordinates=[(r.task_pair, r.condition, r.seed)
                                                      for r in expand(matrix) if r.model == model["id"]]))
                except (OSError, ValueError, KeyError) as exc:
                    model_receipt["flags"].append(f"model_run_failed:{type(exc).__name__}")
                finally:
                    if process is not None:
                        _stop_group(process, grace_s=options.poll_s)
                        model_receipt["server_returncode"] = process.returncode
                after = [snapshot(gpu_index=i, directory=model_dir, label="after",
                                  timeout_s=options.command_timeout_s) for i in devices]
                model_receipt["throttle_after"] = after
                model_receipt["throttle_changes"] = [compare(a, b) for a, b in zip(before, after)]
                for change in model_receipt["throttle_changes"]:
                    model_receipt["flags"].extend(change["flags"])
                flags.extend(model_receipt["flags"])
        elif receipt["status"] != "refused":
            flags.append("matrix_not_executable")
        if any(p.is_symlink() for p in output.rglob("*")):
            flags.append("output_symlink_omitted")
        receipt["data_complete"] = bool(
            executable and len(receipt["models"]) == len(matrix["models"])
            and all("runner_returncode" in m and not any(_incomplete_flag(f) for f in m["flags"])
                    for m in receipt["models"]))
        if receipt["status"] != "refused":
            receipt["status"] = "completed_with_flags" if flags else "completed"
    except Exception as exc:
        flags.append(f"session_failed:{type(exc).__name__}")
    finally:
        if monitor_process is not None:
            _stop_group(monitor_process, grace_s=options.poll_s)
            receipt["monitor_server"]["returncode"] = monitor_process.returncode
        if monitor_log is not None:
            monitor_log.close()
    receipt["end_ns"] = time.monotonic_ns()
    receipt["flags"] = sorted(set(flags))
    _json(output / "receipt.json", receipt)
    archive, checksum = package_results(output)
    transfer_flags = (copy_back((archive, checksum), kind=options.copy_kind,
                               destination=options.destination, log=archive.with_suffix(".copy.log"),
                               timeout_s=options.command_timeout_s)
                      if options.destination else ("copy_destination_not_supplied",))
    _json(archive.with_suffix(".transfer.json"), {"flags": transfer_flags, "archive": archive.name})
    return {**receipt, "archive": str(archive), "transfer_flags": transfer_flags}


def _argv(value: str) -> tuple[str, ...]:
    data = json.loads(value)
    if not isinstance(data, list) or any(not isinstance(x, str) for x in data):
        raise argparse.ArgumentTypeError("command must be a JSON array of strings")
    return tuple(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--runner-command", type=_argv, default=())
    parser.add_argument("--runner-settings", type=Path)
    parser.add_argument("--calibration-slice", action="store_true")
    parser.add_argument("--preflight-command", type=_argv, default=())
    parser.add_argument("--ready-command", type=_argv, default=())
    parser.add_argument("--vllm-command", type=_argv, default=("vllm",))
    # Timeouts and cadence are operator policy, with no scientific cutoff implied.
    parser.add_argument("--ready-timeout-s", type=float, required=True)
    parser.add_argument("--command-timeout-s", type=float, required=True)
    parser.add_argument("--poll-s", type=float, required=True)
    parser.add_argument("--runner-timeout-s", type=float, required=True)
    parser.add_argument("--monitor-placement", choices=("external", "gpu", "none"), required=True)
    parser.add_argument("--monitor-base-url")
    parser.add_argument("--judge-base-url")
    parser.add_argument("--monitor-gpu-index", type=int)
    parser.add_argument("--monitor-port", type=int)
    parser.add_argument("--gpu-indices", type=lambda s: tuple(int(i) for i in s.split(",")), default=())
    parser.add_argument("--gpu-index", type=int, default=0)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--destination")
    parser.add_argument("--copy-kind", choices=("rsync", "s3", "local"), default="rsync")
    args = parser.parse_args(argv)
    if any(not (0 < x < float("inf")) for x in (
            args.ready_timeout_s, args.command_timeout_s, args.runner_timeout_s, args.poll_s)):
        parser.error("timeouts and poll cadence must be finite and positive")
    options = SessionOptions(**vars(args))
    result = run_session(options)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 2 if result["status"] == "refused" else 0


if __name__ == "__main__":
    raise SystemExit(main())
