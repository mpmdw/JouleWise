"""One OSCTX cell; the workload and system reads are injectable for offline tests."""
from __future__ import annotations

import argparse
import ctypes
import dataclasses
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time
import traceback
from types import SimpleNamespace

try:
    from .common import load_config, write_json
except ImportError:
    from common import load_config, write_json

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def qos_class(libc=None) -> dict:
    if libc is None:
        libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
    libc.pthread_self.argtypes = []
    libc.pthread_self.restype = ctypes.c_void_p
    libc.pthread_get_qos_class_np.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_int)]
    libc.pthread_get_qos_class_np.restype = ctypes.c_int
    qos, relative = ctypes.c_uint(), ctypes.c_int()
    result = libc.pthread_get_qos_class_np(libc.pthread_self(), ctypes.byref(qos), ctypes.byref(relative))
    if result:
        raise OSError(result, "pthread_get_qos_class_np failed")
    return {"class": hex(qos.value), "relative_priority": relative.value}


def command_text(argv: list[str]) -> dict:
    try:
        completed = subprocess.run(argv, capture_output=True, text=True, timeout=10, check=False)
        return {"argv": argv, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
    except Exception as exc:
        return {"argv": argv, "status": "unavailable", "error": str(exc)}


def hid_idle_seconds() -> float:
    result = command_text(["/usr/sbin/ioreg", "-c", "IOHIDSystem"])
    match = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', result.get("stdout", ""))
    if not match:
        raise RuntimeError(f"HIDIdleTime unreadable: {result}")
    return int(match.group(1)) / 1e9


def display_state() -> str:
    for argv in (["/usr/sbin/ioreg", "-r", "-c", "IODisplayWrangler"],
                 ["/usr/sbin/ioreg", "-r", "-c", "AppleDisplay"]):
        result = command_text(argv)
        match = re.search(r'"(?:IOPowerManagement|CurrentPowerState)"\s*=\s*(\d+)', result.get("stdout", ""))
        if match:
            return "on" if int(match.group(1)) > 0 else "asleep"
    return "unknown"


def ancestry() -> list[dict]:
    result = []
    pid = os.getpid()
    while pid >= 1 and pid not in {item["pid"] for item in result}:
        info = command_text(["/bin/ps", "-p", str(pid), "-o", "ppid=,comm="])
        parts = info.get("stdout", "").strip().split(maxsplit=1)
        ppid = int(parts[0]) if parts and parts[0].isdigit() else 0
        result.append({"pid": pid, "ppid": ppid, "comm": parts[1] if len(parts) > 1 else "unknown"})
        if pid == 1 or ppid <= 0:
            break
        pid = ppid
    return result


def model_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def output_hash(tokens: list[int]) -> str:
    return hashlib.sha256(json.dumps(tokens, separators=(",", ":")).encode()).hexdigest()


def token_flags(result: dict, expected: int = 256) -> list[str]:
    flags = []
    if result["output_tokens"] != expected or len(result["token_ids"]) != expected:
        flags.append("token_count_mismatch")
    if result.get("finish_reason") != "length":
        flags.append("early_finish")
    return flags


def sampler_command(config: dict, output: Path) -> list[str]:
    from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
    from joulewise.clock import SystemClock
    adapter = PowermetricsTelemetryAdapter(SystemClock(), executable="/usr/bin/powermetrics", privilege_prefix=("sudo", "-n"))
    return adapter._command(SimpleNamespace(sampling=SimpleNamespace(power_hz=1000.0 / config["sampler_interval_ms"])), output, count=None)


def stamp() -> dict:
    from joulewise.clock import SystemClock
    return dataclasses.asdict(SystemClock().stamp())


def wait_for_first_parse(path: Path, process, timeout=15) -> dict:
    from joulewise.adapters.powermetrics import parse_powermetrics_records
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            try:
                parse_powermetrics_records(path.read_bytes())
                return stamp()
            except ValueError:
                pass
        if process.poll() is not None:
            raise RuntimeError("powermetrics exited before first record")
        time.sleep(.05)
    raise TimeoutError("powermetrics produced no parseable record")


def stop_sampler(process) -> int:
    if process.poll() is None:
        process.send_signal(signal.SIGINT)
    try:
        return process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        return process.wait(timeout=5)


class SystemWorkloadBackend:
    def command(self, argv):
        process = None
        try:
            process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(timeout=15)
            result = {"pid": process.pid, "argv": argv, "returncode": process.returncode,
                      "stdout": stdout, "stderr": stderr}
            if process.returncode and argv[1:2] == ["procinfo"]:
                result["status"] = "unavailable"
            return result
        except Exception as exc:
            if process is not None and process.poll() is None:
                process.kill()
                process.wait()
            return {"argv": argv, "status": "unavailable", "error": str(exc)}

    def idle(self):
        return hid_idle_seconds()

    def display(self):
        return display_state()

    def sleep(self, seconds):
        time.sleep(seconds)

    def prepare_model(self, config):
        os.environ["HF_HUB_OFFLINE"] = "1"
        import mlx.core as mx
        from mlx_lm import load, stream_generate
        from mlx_lm.models.cache import make_prompt_cache
        versions = {"mlx": importlib.metadata.version("mlx"), "mlx_lm": importlib.metadata.version("mlx-lm")}
        if versions != config["runtime"]:
            raise RuntimeError(f"runtime pin mismatch: {versions}")
        model, tokenizer = load(config["model"])
        prompt = tokenizer.apply_chat_template([{"role": "user", "content": config["prompt"]}], tokenize=False, add_generation_prompt=True)
        return {"mx": mx, "stream": stream_generate, "cache": make_prompt_cache,
                "model": model, "tokenizer": tokenizer, "prompt": prompt, "versions": versions}

    def generate(self, prepared, max_tokens: int, first_token):
        mx = prepared["mx"]
        tokenizer = prepared["tokenizer"]
        eos = set(getattr(tokenizer, "eos_token_ids", []) or [])
        if not eos and tokenizer.eos_token_id is not None:
            eos = {tokenizer.eos_token_id}
        def mask_eos(tokens, logits):
            if eos:
                logits[:, list(eos)] = -float("inf")
            return logits
        cache = prepared["cache"](prepared["model"])
        ids = []
        final = None
        for response in prepared["stream"](prepared["model"], tokenizer, prompt=prepared["prompt"],
                                            max_tokens=max_tokens, sampler=lambda x: mx.argmax(x, axis=-1),
                                            prompt_cache=cache, logits_processors=[mask_eos]):
            if not ids:
                first_token()
            ids.append(int(response.token))
            final = response
        mx.eval([item.state for item in cache])
        if final is None:
            raise RuntimeError("LM generated no tokens")
        return {"token_ids": ids, "output_tokens": len(ids), "prompt_tps": final.prompt_tps,
                "generation_tps": final.generation_tps, "finish_reason": final.finish_reason,
                "eos_suppressed": True}


def census_sample(backend, state: str, expected_display: str, threshold: float) -> dict:
    record = {"wall_ns": time.time_ns(), "mono_ns": time.monotonic_ns(),
              "ps": backend.command(["/bin/ps", "-Ao", "pid,ppid,time,comm"])}
    try:
        record["hid_idle_seconds"] = backend.idle()
    except Exception as exc:
        record["hid_error"] = str(exc)
    record["display_state"] = backend.display()
    record["interrupted"] = ((state == "U" and record.get("hid_idle_seconds", float("inf")) < threshold) or
                             (record["display_state"] != "unknown" and record["display_state"] != expected_display))
    return record


def run(out: Path, config: dict, state: str, context: str, cell_id: int, *, stage: str = "U1",
        allow_pids: list[int] | None = None, backend=None, no_powermetrics=False) -> None:
    out.mkdir(parents=True, exist_ok=True)
    backend = backend or SystemWorkloadBackend()
    seg = config["segments"]
    metadata = {"state": state, "context": context, "cell_id": cell_id, "stage": stage,
                "pid": os.getpid(), "ancestry": ancestry(), "allow_pids": allow_pids or [],
                "boundaries": [], "repeats": {"lm": [], "cpu": []}, "clock_stamps": {},
                "powermetrics_enabled": not no_powermetrics, "interrupted": False, "flags": []}
    process = None
    stop = threading.Event()
    lock = threading.Lock()
    census_records = []
    expected_display = "asleep" if state == "S" else "on"
    def mark(name, repeat, edge):
        item = {"name": name, "repeat": repeat, "edge": edge, "wall_ns": time.time_ns(), "mono_ns": time.monotonic_ns()}
        metadata["boundaries"].append(item)
        return item
    def measured(name, repeat, fn):
        backend.sleep(seg["guard_seconds"])
        mark(name, repeat, "start")
        try:
            return fn()
        finally:
            mark(name, repeat, "end")
            backend.sleep(seg["guard_seconds"])
    def census_loop():
        count = 0
        while not stop.is_set():
            record = census_sample(backend, state, expected_display, config["hid_idle_seconds"])
            if count % max(1, round(config["assertions_interval_seconds"] / config["census_interval_seconds"])) == 0:
                record["assertions"] = backend.command(["/usr/bin/pmset", "-g", "assertions"])
            with lock:
                census_records.append(record)
                if record["interrupted"]:
                    metadata["interrupted"] = True
            count += 1
            stop.wait(config["census_interval_seconds"])
    census = threading.Thread(target=census_loop, daemon=True)
    try:
        metadata["pre"] = {"qos": qos_class() if isinstance(backend, SystemWorkloadBackend) else None,
                           "display_state": backend.display(), "environment": {k: os.environ.get(k) for k in ("PATH", "HOME", "HF_HUB_OFFLINE")}}
        brightness_read = backend.command(["/usr/libexec/corebrightnessdiag", "status-info"])
        metadata["brightness"] = brightness_read if brightness_read.get("returncode") == 0 else {"status": "unreadable"}
        census.start()
        if not no_powermetrics:
            command = sampler_command(config, out / "powermetrics.plist")
            metadata["powermetrics_argv"] = command
            metadata["clock_stamps"]["pre_spawn"] = stamp()
            with (out / "powermetrics.stderr").open("wb") as stderr:
                process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=stderr)
            metadata["powermetrics_pid"] = process.pid
            metadata["procinfo_powermetrics"] = backend.command(["/bin/launchctl", "procinfo", str(process.pid)])
            metadata["clock_stamps"]["first_parse"] = wait_for_first_parse(out / "powermetrics.plist", process)
        metadata["procinfo_workload"] = backend.command(["/bin/launchctl", "procinfo", str(os.getpid())])
        metadata["clock_stamps"]["sampling_started"] = stamp()
        def preread():
            for path in sorted(Path(config["model"]).glob("*.safetensors")):
                with path.open("rb") as stream:
                    for _ in iter(lambda: stream.read(1024 * 1024), b""):
                        pass
        measured("preread", 1, preread if isinstance(backend, SystemWorkloadBackend) else lambda: backend.preread(config))
        model_file = Path(config["model"]) / config["model_file"]
        metadata["model_sha256"] = model_sha256(model_file) if isinstance(backend, SystemWorkloadBackend) else backend.model_sha256(model_file)
        prepared = measured("model_load", 1, lambda: backend.prepare_model(config))
        metadata["runtime"] = prepared.get("versions")
        metadata["prompt"] = prepared.get("prompt")
        try:
            metadata["qos_after_mlx_import"] = qos_class()
        except Exception as exc:
            metadata["qos_after_mlx_import"] = {"status": "unavailable", "error": str(exc)}
        measured("idle", 1, lambda: backend.sleep(seg["idle_seconds"]))
        for repeat in range(seg["lm_warmups"] + seg["lm_repeats"]):
            timed = repeat >= seg["lm_warmups"]
            number = repeat - seg["lm_warmups"] + 1 if timed else 0
            name = "lm" if timed else "lm_warmup"
            value = measured(name, number, lambda: backend.generate(prepared, seg["lm_tokens"], lambda: mark(name, number, "first_token")))
            value["output_hash"] = output_hash(value["token_ids"])
            value["flags"] = token_flags(value, seg["lm_tokens"])
            value.pop("token_ids")
            edges = [b for b in metadata["boundaries"] if b["name"] == name and b["repeat"] == number]
            value.update({"repeat": number, "seconds": (next(b["mono_ns"] for b in edges if b["edge"] == "end") -
                                                       next(b["mono_ns"] for b in edges if b["edge"] == "start")) / 1e9})
            metadata["repeats"][name] = metadata["repeats"].get(name, [])
            metadata["repeats"][name].append(value)
            metadata["flags"].extend(value["flags"])
        for repeat in range(1, seg["cpu_repeats"] + 1):
            def cpu_probe():
                value = 0
                for number in range(seg["cpu_iterations"]):
                    value += number
                return value
            checksum = measured("cpu", repeat, cpu_probe if isinstance(backend, SystemWorkloadBackend) else lambda: backend.cpu_probe(seg["cpu_iterations"]))
            edges = [b for b in metadata["boundaries"] if b["name"] == "cpu" and b["repeat"] == repeat]
            elapsed = (next(b["mono_ns"] for b in edges if b["edge"] == "end") -
                       next(b["mono_ns"] for b in edges if b["edge"] == "start")) / 1e9
            metadata["repeats"]["cpu"].append({"repeat": repeat, "seconds": elapsed, "checksum": checksum})
            if elapsed < seg["cpu_seconds"]:
                raise RuntimeError(f"CPU probe below registered {seg['cpu_seconds']} s minimum; increase fixed iterations before capture")
        metadata["clock_stamps"]["sampling_stopped"] = stamp()
        if process:
            if process.poll() is not None:
                raise RuntimeError("powermetrics exited during cell")
            metadata["powermetrics_cpu_time"] = backend.command(["/bin/ps", "-p", str(process.pid), "-o", "time="])
            backend.sleep(1)
            metadata["powermetrics_returncode"] = stop_sampler(process)
            process = None
            metadata["clock_stamps"]["post_stop"] = stamp()
    except BaseException:
        write_json(out / "error.json", {"traceback": traceback.format_exc()})
        raise
    finally:
        if process:
            stop_sampler(process)
        stop.set()
        if census.is_alive():
            census.join(timeout=10)
        with (out / "census.jsonl").open("w") as stream:
            for record in census_records:
                stream.write(json.dumps(record) + "\n")
        metadata["interrupted"] = metadata["interrupted"] or any(x["interrupted"] for x in census_records)
        write_json(out / "cell.json", metadata)
        write_json(out / "done.json", {"ok": not (out / "error.json").exists(),
                                       "interrupted": metadata["interrupted"], "wall_ns": time.time_ns()})


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--cell-id", type=int, required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--allow-pid", action="append", type=int, default=[])
    parser.add_argument("--no-powermetrics", action="store_true")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    try:
        run(args.out, config, args.state, args.context, args.cell_id, stage=args.stage,
            allow_pids=args.allow_pid, no_powermetrics=args.no_powermetrics)
        return 0
    except BaseException:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
