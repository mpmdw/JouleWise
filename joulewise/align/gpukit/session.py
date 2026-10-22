"""Run a provider-neutral GPU session and preserve every outcome in a bundle.

The runner command is an argv template, not shell text. It consumes this lane's
matrix format and writes shared Episode JSONL. This adapter keeps a missing
runner, sampler or router capture visible while the parallel lanes integrate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence
from urllib.error import URLError
from urllib.request import urlopen

from joulewise.align.gpukit.matrix import load_matrix
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
    preflight_command: tuple[str, ...] = ()
    ready_command: tuple[str, ...] = ()
    vllm_command: tuple[str, ...] = ("vllm",)
    gpu_index: int = 0
    port: int = 8000
    destination: str | None = None
    copy_kind: str = "rsync"


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
        virtualization = (evidence["virtualization"] or "").strip().lower()
        if mig == "enabled" or "mig-" in (evidence["uuid"] or "").lower():
            raise IsolationError("MIG enabled: whole GPU required")
        if virtualization in ("vgpu", "host vgpu", "guest vgpu") or "vgpu" in virtualization:
            raise IsolationError("vGPU detected: whole GPU required")
        if mig not in ("disabled", "n/a", "[n/a]"):
            evidence["flags"].append("gpu_mig_state_unverified")
        if virtualization not in ("none", "passthrough", "pass through"):
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
            if _command(ready_command, log, timeout_s=min(poll_s, timeout_s)) == 0:
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


def _validate_output(path: Path, *, expected_count: int, router: bool, model: str) -> tuple[str, ...]:
    flags: list[str] = []
    try:
        episodes = read_episodes(path)
        if len(episodes) != expected_count:
            flags.append("runner_episode_count_mismatch")
        if len({e.episode_id for e in episodes}) != len(episodes):
            flags.append("runner_duplicate_episode_ids")
        for episode in episodes:
            if episode.agent_model != model:
                flags.append("runner_episode_model_mismatch")
            flags.extend(episode.flags)
            if not episode.power_traces or any(not t.t_ns for t in episode.power_traces):
                flags.append("episode_power_missing")
            if router and episode.router_log is None:
                flags.append("episode_router_log_missing")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        flags.append(f"runner_output_unreadable:{type(exc).__name__}")
    return tuple(sorted(set(flags)))


def run_session(options: SessionOptions, *,
                probe: Callable[[str, float], bool] = _healthy) -> dict[str, Any]:
    """Run serial model campaigns, preflight, bundle and optional copy-back.

    Every operational failure is a flag and is packaged. MIG/vGPU is the explicit
    isolation refusal required by the brief. This function never rents hardware.
    """
    output = options.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    flags: list[str] = []
    receipt: dict[str, Any] = {"schema": "joulewise.align.gpukit.session.v1",
                             "status": "incomplete", "flags": flags,
                             "models": [], "data_complete": False,
                             "start_ns": time.monotonic_ns()}
    try:
        matrix, matrix_flags = load_matrix(options.matrix)
        flags.extend(matrix_flags)
        if not options.runner_command:
            flags.append("runner_command_missing")
            matrix_flags = (*matrix_flags, "runner_command_missing")
        if _command([sys.executable, "-m", "pip", "freeze"], output / "packages.log",
                    timeout_s=options.command_timeout_s):
            flags.append("package_provenance_unavailable")
        if _command(["git", "rev-parse", "HEAD"], output / "repository-head.log",
                    timeout_s=options.command_timeout_s):
            flags.append("repository_provenance_unavailable")
        if matrix:
            _json(output / "matrix.json", matrix)
            flags.extend(matrix.get("flags", ()))
        try:
            receipt["hardware"] = whole_gpu(gpu_index=options.gpu_index,
                                             timeout_s=options.command_timeout_s)
            flags.extend(receipt["hardware"]["flags"])
        except IsolationError as exc:
            flags.append("whole_gpu_required")
            receipt["isolation_reason"] = str(exc)
            receipt["status"] = "refused"
            matrix_flags = (*matrix_flags, "isolation_refused")
        preflight = options.preflight_command or (
            sys.executable, "-m", "joulewise.align.power.preflight")
        if receipt["status"] != "refused":
            code = _command(preflight, output / "preflight.log",
                            timeout_s=options.command_timeout_s)
            receipt["preflight_returncode"] = code
            if code:
                flags.append("nvml_preflight_failed")
        if matrix and not matrix_flags:
            for index, model in enumerate(matrix["models"]):
                model_dir = output / f"model-{index}"
                model_dir.mkdir()
                endpoint = f"http://127.0.0.1:{options.port}"
                model_receipt: dict[str, Any] = {"model": model["id"], "flags": []}
                receipt["models"].append(model_receipt)
                argv = [*options.vllm_command, "serve", model["id"],
                        "--host", "127.0.0.1", "--port", str(options.port),
                        "--served-model-name", model["id"],
                        "--enable-auto-tool-choice", "--tool-call-parser", "hermes"]
                if model["id"].startswith("Qwen/"):
                    argv += ["--reasoning-parser", "qwen3"]
                if model.get("revision"):
                    argv += ["--revision", model["revision"]]
                else:
                    model_receipt["flags"].append("model_revision_unpinned")
                process = None
                try:
                    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(options.gpu_index))
                    with (model_dir / "server.log").open("wb") as server_log:
                        process = subprocess.Popen(argv, stdout=server_log,
                                                   stderr=subprocess.STDOUT, env=env, start_new_session=True)
                        ready = wait_ready(process, endpoint, timeout_s=options.ready_timeout_s,
                                           poll_s=options.poll_s, ready_command=options.ready_command,
                                           log=model_dir / "readiness.log", probe=probe)
                        model_receipt["flags"].extend(ready)
                        if not ready:
                            mapping = {"matrix": str(output / "matrix.json"), "model": model["id"],
                                       "endpoint": endpoint,
                                       "output": str(model_dir / "episodes.jsonl"),
                                       "sample_interval_ns": str(matrix["sampling"]["interval_ns"]),
                                       "router_logging": str(matrix["kind"] == "moe_stage_a").lower()}
                            command = [part.format_map(mapping) for part in options.runner_command]
                            if command:
                                code = _command(command, model_dir / "runner.log",
                                                timeout_s=options.command_timeout_s)
                                model_receipt["runner_returncode"] = code
                                if code:
                                    model_receipt["flags"].append("runner_command_failed")
                            else:
                                model_receipt["flags"].append("runner_command_missing")
                            # Budget drivers must export fresh generation episodes, not
                            # reused deletion trial views, to avoid counting energy twice.
                            expected = matrix.get("measured_episode_count", matrix["episode_count"])
                            expected //= len(matrix["models"])
                            model_receipt["flags"].extend(_validate_output(
                                model_dir / "episodes.jsonl", expected_count=expected,
                                router=matrix["kind"] == "moe_stage_a", model=model["id"]))
                except (OSError, ValueError, KeyError) as exc:
                    model_receipt["flags"].append(f"model_run_failed:{type(exc).__name__}")
                finally:
                    if process is not None:
                        if process.poll() is None:
                            os.killpg(process.pid, signal.SIGTERM)
                            try:
                                process.wait(timeout=options.poll_s)
                            except subprocess.TimeoutExpired:
                                os.killpg(process.pid, signal.SIGKILL)
                                process.wait()
                        # A serving parent can exit before worker processes. Signal
                        # the group even after reaping the parent, without touching
                        # unrelated system processes.
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        model_receipt["server_returncode"] = process.returncode
                flags.extend(model_receipt["flags"])
        elif receipt["status"] != "refused":
            flags.append("matrix_not_executable")
        if any(p.is_symlink() for p in output.rglob("*")):
            flags.append("output_symlink_omitted")
        receipt["data_complete"] = bool(
            matrix and not matrix_flags and len(receipt["models"]) == len(matrix["models"])
            and all(not any(f.startswith(("endpoint_", "runner_", "episode_", "model_run_failed"))
                            for f in model["flags"]) for model in receipt["models"]))
        if receipt["status"] != "refused":
            receipt["status"] = "completed_with_flags" if flags else "completed"
    except Exception as exc:
        flags.append(f"session_failed:{type(exc).__name__}")
    receipt["end_ns"] = time.monotonic_ns()
    receipt["flags"] = sorted(set(flags))
    _json(output / "receipt.json", receipt)
    archive, checksum = package_results(output)
    # Transfer happens after sealing. Keep its receipt beside the immutable bundle.
    transfer_flags = (copy_back((archive, checksum), kind=options.copy_kind,
                               destination=options.destination, log=archive.with_suffix(".copy.log"),
                               timeout_s=options.command_timeout_s)
                      if options.destination else ("copy_destination_not_supplied",))
    _json(archive.with_suffix(".transfer.json"), {"flags": transfer_flags,
                                                "archive": archive.name})
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
    parser.add_argument("--preflight-command", type=_argv, default=())
    parser.add_argument("--ready-command", type=_argv, default=())
    parser.add_argument("--vllm-command", type=_argv, default=("vllm",))
    # Timeouts and cadence are operator policy, with no scientific cutoff implied.
    parser.add_argument("--ready-timeout-s", type=float, required=True)
    parser.add_argument("--command-timeout-s", type=float, required=True)
    parser.add_argument("--poll-s", type=float, required=True)
    parser.add_argument("--gpu-index", type=int, default=0)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--destination")
    parser.add_argument("--copy-kind", choices=("rsync", "s3", "local"), default="rsync")
    args = parser.parse_args(argv)
    if any(not (0 < x < float("inf")) for x in (
            args.ready_timeout_s, args.command_timeout_s, args.poll_s)):
        parser.error("timeouts and poll cadence must be finite and positive")
    options = SessionOptions(**vars(args))
    result = run_session(options)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 2 if result["status"] == "refused" else 0


if __name__ == "__main__":
    raise SystemExit(main())
