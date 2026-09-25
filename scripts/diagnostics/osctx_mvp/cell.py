"""One in-context OSCTX measurement cell. Invoked as a launchd ProgramArgument."""
from __future__ import annotations

import argparse
import ctypes
import dataclasses
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import traceback
from types import SimpleNamespace

try:
    from .common import load_config, write_json
except ImportError:  # direct ProgramArguments execution
    from common import load_config, write_json

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def qos_class(libc=None) -> dict:
    """Read this thread's QoS using pointer-correct Darwin ctypes signatures."""
    if libc is None:
        libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
    libc.pthread_self.argtypes = []
    libc.pthread_self.restype = ctypes.c_void_p
    libc.pthread_get_qos_class_np.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_int)
    ]
    libc.pthread_get_qos_class_np.restype = ctypes.c_int
    qos, relative = ctypes.c_uint(), ctypes.c_int()
    result = libc.pthread_get_qos_class_np(libc.pthread_self(), ctypes.byref(qos), ctypes.byref(relative))
    if result:
        raise OSError(result, "pthread_get_qos_class_np failed")
    return {"class": hex(qos.value), "relative_priority": relative.value}


def command_text(argv: list[str]) -> dict:
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=10, check=False)
        return {"argv": argv, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    except Exception as exc:
        return {"argv": argv, "error": str(exc)}


def hid_idle_seconds() -> float:
    result = command_text(["/usr/sbin/ioreg", "-c", "IOHIDSystem"])
    match = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', result.get("stdout", ""))
    if not match:
        raise RuntimeError(f"HIDIdleTime unreadable: {result}")
    return int(match.group(1)) / 1e9


def brightness() -> dict:
    for argv in (["/usr/libexec/corebrightnessdiag", "status-info"], ["/usr/sbin/ioreg", "-r", "-c", "AppleARMBacklight"]):
        result = command_text(argv)
        if result.get("returncode") == 0 and result.get("stdout", "").strip():
            return result
    return {"status": "unreadable"}


def snapshot() -> dict:
    result = {"wall_ns": time.time_ns(), "mono_ns": time.monotonic_ns(), "ppid": os.getppid()}
    for key, fn in (
        ("hid_idle_seconds", hid_idle_seconds),
        ("qos", qos_class),
        ("nice", lambda: os.getpriority(os.PRIO_PROCESS, 0)),
    ):
        try:
            result[key] = fn()
        except Exception as exc:
            result[key] = {"error": str(exc)}
    result["assertions"] = command_text(["/usr/bin/pmset", "-g", "assertions"])
    result["thermal"] = command_text(["/usr/bin/pmset", "-g", "therm"])
    result["processes"] = command_text(["/bin/ps", "-Ao", "pid,ppid,pcpu,pmem,comm", "-r"])
    if "stdout" in result["processes"]:
        result["processes"]["stdout"] = "\n".join(result["processes"]["stdout"].splitlines()[:16])
    result["brightness"] = brightness()
    return result


def boundary(name: str, repeat: int, edge: str) -> dict:
    return {"name": name, "repeat": repeat, "edge": edge, "wall_ns": time.time_ns(), "mono_ns": time.monotonic_ns()}


def measured(name: str, repeat: int, boundaries: list[dict], fn):
    boundaries.append(boundary(name, repeat, "start"))
    try:
        return fn()
    finally:
        boundaries.append(boundary(name, repeat, "end"))


def cpu_work(iterations: int) -> int:
    value = 0
    for i in range(iterations):
        value += i
    return value


def sampler_command(config: dict, output: Path) -> list[str]:
    from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
    from joulewise.clock import SystemClock
    adapter = PowermetricsTelemetryAdapter(SystemClock(), executable="/usr/bin/powermetrics", privilege_prefix=("sudo", "-n"))
    sampling = SimpleNamespace(power_hz=1000.0 / config["sampler_interval_ms"])
    return adapter._command(SimpleNamespace(sampling=sampling), output, count=None)


def stamp() -> dict:
    from joulewise.clock import SystemClock
    return dataclasses.asdict(SystemClock().stamp())


def wait_for_first_parse(path: Path, process: subprocess.Popen, timeout: float = 15) -> dict:
    from joulewise.adapters.powermetrics import parse_powermetrics_records
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            data = path.read_bytes()
            try:
                parse_powermetrics_records(data)
                return stamp()
            except ValueError:
                pass
        if process.poll() is not None:
            raise RuntimeError(f"powermetrics exited before first record: {process.returncode}")
        time.sleep(.05)
    raise TimeoutError("powermetrics produced no parseable record")


def stop_sampler(process: subprocess.Popen) -> int:
    if process.poll() is None:
        process.send_signal(signal.SIGINT)
    try:
        return process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        return process.wait(timeout=5)


def run(out: Path, config: dict, state: str, context: str, cell_id: int, *, no_powermetrics: bool = False) -> None:
    out.mkdir(parents=True, exist_ok=True)
    config = json.loads(json.dumps(config))
    seg = config["segments"]
    metadata = {"state": state, "context": context, "cell_id": cell_id, "config": config,
                "pid": os.getpid(), "boundaries": [], "repeats": {}, "clock_stamps": {},
                "powermetrics_enabled": not no_powermetrics}
    process = None
    try:
        metadata["pre"] = snapshot()
        write_json(out / "cell.json", metadata)
        if not no_powermetrics:
            command = sampler_command(config, out / "powermetrics.plist")
            metadata["powermetrics_argv"] = command
            metadata["clock_stamps"]["pre_spawn"] = stamp()
            with (out / "powermetrics.stderr").open("wb") as stderr:
                process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=stderr)
            metadata["powermetrics_pid"] = process.pid
            metadata["clock_stamps"]["first_parse"] = wait_for_first_parse(out / "powermetrics.plist", process)
        metadata["clock_stamps"]["sampling_started"] = stamp()
        boundaries = metadata["boundaries"]
        measured("idle", 1, boundaries, lambda: time.sleep(seg["idle_seconds"]))
        metadata["repeats"]["cpu"] = []
        for repeat in range(1, seg["cpu_repeats"] + 1):
            start = time.perf_counter()
            value = measured("cpu", repeat, boundaries, lambda: cpu_work(seg["cpu_iterations"]))
            metadata["repeats"]["cpu"].append({"repeat": repeat, "seconds": time.perf_counter() - start, "checksum": value})
        import mlx.core as mx
        matrix = mx.random.normal((seg["gpu_dimension"], seg["gpu_dimension"]), dtype=mx.float16)
        mx.eval(matrix)
        def gpu_work():
            for _ in range(seg["gpu_matmuls"]):
                result = matrix @ matrix
                mx.eval(result)
        for _ in range(seg["gpu_warmups"]):
            gpu_work()
        metadata["repeats"]["gpu"] = []
        for repeat in range(1, seg["gpu_repeats"] + 1):
            start = time.perf_counter()
            measured("gpu", repeat, boundaries, gpu_work)
            metadata["repeats"]["gpu"].append({"repeat": repeat, "seconds": time.perf_counter() - start})
        os.environ["HF_HUB_OFFLINE"] = "1"
        from mlx_lm import load, stream_generate
        model, tokenizer = load(config["model"])
        def lm_work():
            final = None
            for response in stream_generate(model, tokenizer, prompt=config["prompt"], max_tokens=seg["lm_max_tokens"]):
                final = response
            if final is None:
                raise RuntimeError("LM generated no tokens")
            return {"output_tokens": final.generation_tokens, "prefill_tps": final.prompt_tps,
                    "decode_tps": final.generation_tps, "finish_reason": final.finish_reason}
        for _ in range(seg["lm_warmups"]):
            lm_work()
        metadata["repeats"]["lm"] = []
        for repeat in range(1, seg["lm_repeats"] + 1):
            start = time.perf_counter()
            value = measured("lm", repeat, boundaries, lm_work)
            metadata["repeats"]["lm"].append({"repeat": repeat, "seconds": time.perf_counter() - start, **value})
        metadata["clock_stamps"]["sampling_stopped"] = stamp()
        if process:
            if process.poll() is not None:
                raise RuntimeError(f"powermetrics exited during workloads: {process.returncode}")
            time.sleep(1)
            metadata["powermetrics_returncode"] = stop_sampler(process)
            process = None
            metadata["clock_stamps"]["post_parse"] = stamp()
        metadata["post"] = snapshot()
        write_json(out / "cell.json", metadata)
    except BaseException:
        if process:
            stop_sampler(process)
        try:
            metadata["post"] = snapshot()
        except Exception as exc:
            metadata["post"] = {"error": str(exc)}
        write_json(out / "cell.json", metadata)
        write_json(out / "error.json", {"traceback": traceback.format_exc()})
        raise
    finally:
        # The runner waits for this marker, including when the cell fails.
        write_json(out / "done.json", {"ok": not (out / "error.json").exists(), "wall_ns": time.time_ns()})


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--cell-id", type=int, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--no-powermetrics", action="store_true")
    parser.add_argument("--lm-repeats", type=int)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.state not in config["states"] or args.context not in config["contexts"]:
        parser.error("unknown state or context")
    if args.lm_repeats is not None:
        config["segments"]["lm_repeats"] = args.lm_repeats
    try:
        run(args.out, config, args.state, args.context, args.cell_id, no_powermetrics=args.no_powermetrics)
        return 0
    except BaseException:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
