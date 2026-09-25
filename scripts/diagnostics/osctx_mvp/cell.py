"""Launch-context wrapper around unmodified JouleWise production runs."""
from __future__ import annotations

import argparse
import copy
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import traceback

try:
    from .common import load_config, write_json
except ImportError:
    from common import load_config, write_json

ROOT = Path(__file__).resolve().parents[3]
TAGS = ["osctx-mvp-diagnostic", "df-condition=sw-decode-b-qwen25-7b"]


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


DISPLAY_ON_ASSERTION = "Prevent sleep while display is on"


def display_state() -> str:
    # Verified live on Mac15,9 / 25G83 (2026-09-24, record 21): the
    # IOMobileFramebuffer CurrentPowerState stays 1 through display sleep, and
    # IODisplayWrangler does not exist on Apple silicon. powerd holds this
    # named assertion exactly while the display is on (present -> absent after
    # `pmset displaysleepnow` -> present after `caffeinate -u`).
    result = command_text(["/usr/bin/pmset", "-g", "assertions"])
    stdout = result.get("stdout", "")
    if result.get("returncode") != 0 or "Assertion status" not in stdout:
        return "unknown"
    return "on" if DISPLAY_ON_ASSERTION in stdout else "asleep"


def ancestry(pid=None) -> list[dict]:
    result = []
    current = pid or os.getpid()
    while current >= 1 and current not in {item["pid"] for item in result}:
        info = command_text(["/bin/ps", "-p", str(current), "-o", "ppid=,comm="])
        parts = info.get("stdout", "").strip().split(maxsplit=1)
        ppid = int(parts[0]) if parts and parts[0].isdigit() else 0
        result.append({"pid": current, "ppid": ppid, "comm": parts[1] if len(parts) > 1 else "unknown"})
        if current == 1 or ppid <= 0:
            break
        current = ppid
    return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def materialize_config(source: Path, destination: Path, run_id: str) -> dict:
    original = json.loads(source.read_text())
    copied = copy.deepcopy(original)
    copied["run_id"] = run_id
    copied["run_metadata"]["tags"] = list(TAGS)
    expected = copy.deepcopy(copied)
    expected["run_id"] = original["run_id"]
    expected["run_metadata"]["tags"] = original["run_metadata"]["tags"]
    if expected != original:
        raise AssertionError("materialized config changes fields besides run_id and run_metadata.tags")
    write_json(destination, copied)
    actual = json.loads(destination.read_text())
    if actual != copied:
        raise AssertionError("materialized config failed round trip")
    return {"source_sha256": sha256(source), "materialized_sha256": sha256(destination), "run_id": run_id}


def production_command(python: str, cfg: Path, out: Path) -> list[str]:
    return [python, "-m", "joulewise", "run", str(cfg), "--runs-dir", str(out / "runs"),
            "--post-window-sampling-dwell-s", "60"]


class SystemBackend:
    def command(self, argv):
        return command_text(argv)

    def idle(self):
        return hid_idle_seconds()

    def display(self):
        return display_state()

    def sleep(self, seconds):
        time.sleep(seconds)

    def production(self, argv, log):
        # Powermetrics names its -o capture with tempfile.NamedTemporaryFile.
        # Keep that path under this cell so an orphaned sampler remains identifiable.
        capture_dir = log.parent / "runs"
        capture_dir.mkdir(parents=True, exist_ok=True)
        environment = os.environ.copy()
        environment["TMPDIR"] = str(capture_dir.resolve())
        with log.open("w") as stream:
            process = subprocess.Popen(argv, cwd=ROOT, env=environment,
                                       stdout=stream, stderr=subprocess.STDOUT)
            child = {"pid": process.pid,
                     "ps": self.command(["/bin/ps", "-p", str(process.pid), "-o", "pid,pri,nice,comm"]),
                     "ancestry": ancestry(process.pid)}
            child["returncode"] = process.wait()
            return child

    def preread(self, model):
        paths = sorted(Path(model).glob("*.safetensors"))
        if not paths:
            raise FileNotFoundError(f"no model weights in {model}")
        for path in paths:
            with path.open("rb") as stream:
                for _ in iter(lambda: stream.read(1024 * 1024), b""):
                    pass
        return [str(path) for path in paths]

    def cpu_probe(self, iterations):
        value = 0
        for number in range(iterations):
            value += number
        return value


def census_sample(backend, state: str, expected_display: str, threshold: float) -> dict:
    record = {"wall_ns": time.time_ns(), "mono_ns": time.monotonic_ns(),
              "ps": backend.command(["/bin/ps", "-Ao", "pid,ppid,time,comm"])}
    try:
        record["hid_idle_seconds"] = backend.idle()
    except Exception as exc:
        record["hid_error"] = str(exc)
    try:
        record["display_state"] = backend.display()
    except Exception as exc:
        record["display_state"] = "unknown"
        record["display_error"] = str(exc)
    record["interrupted"] = ((state == "U" and
                              (not isinstance(record.get("hid_idle_seconds"), (int, float)) or
                               not math.isfinite(record["hid_idle_seconds"]) or
                               record["hid_idle_seconds"] < threshold)) or
                             (state in ("U", "S") and record["display_state"] != expected_display))
    return record


def run(out: Path, config: dict, state: str, context: str, cell_id: int, *, stage: str = "U1",
        allow_pids: list[int] | None = None, backend=None, python=sys.executable) -> None:
    out.mkdir(parents=True, exist_ok=True)
    backend = backend or SystemBackend()
    os.environ["HF_HUB_OFFLINE"] = "1"
    source = ROOT / config["source_config"]
    metadata = {"state": state, "context": context, "cell_id": cell_id, "stage": stage,
                "pid": os.getpid(), "ancestry": ancestry() if isinstance(backend, SystemBackend) else [],
                "qos": qos_class() if isinstance(backend, SystemBackend) else None,
                "allow_pids": allow_pids or [], "runs": [], "cpu": [], "interrupted": False, "flags": []}
    stop = threading.Event()
    census_records = []
    expected_display = "asleep" if state == "S" else "on"
    def census_loop():
        count = 0
        while not stop.is_set():
            record = census_sample(backend, state, expected_display, config["hid_idle_seconds"])
            if count % max(1, round(config["assertions_interval_seconds"] / config["census_interval_seconds"])) == 0:
                record["assertions"] = backend.command(["/usr/bin/pmset", "-g", "assertions"])
            census_records.append(record)
            if record["interrupted"]:
                metadata["interrupted"] = True
            count += 1
            stop.wait(config["census_interval_seconds"])
    census = threading.Thread(target=census_loop, daemon=True)
    try:
        try:
            initial_display = backend.display()
        except Exception as exc:
            initial_display = "unknown"
            metadata["flags"].append(f"initial_display_unreadable:{exc}")
        if state in ("U", "S") and initial_display != expected_display:
            metadata["interrupted"] = True
        metadata["pre"] = {"display_state": initial_display,
                           "environment": {k: os.environ.get(k) for k in ("PATH", "HOME", "HF_HUB_OFFLINE")}}
        census.start()
        metadata["preread_files"] = backend.preread(config["model"])
        match = re.fullmatch(r"(.+)\.(\d+)\.(D|I|SH|B)\.a\d+", out.name)
        cell_name = f"{match.group(1)}-{match.group(2)}".lower() if match else f"cell-{cell_id}"
        for number in range(1, config["runs_per_cell"][stage] + 1):
            run_id = f"osctx-{stage.lower()}-{cell_name}-{context.lower()}-r{number}"
            cfg = out / f"run-r{number}.json"
            digests = materialize_config(source, cfg, run_id)
            argv = production_command(python, cfg, out)
            child = backend.production(argv, out / f"run-r{number}.log")
            metadata["runs"].append({**digests, "config": str(cfg), "bundle": str(out / "runs" / run_id),
                                     "argv": argv, "child": child})
            if child["returncode"]:
                raise RuntimeError(f"production run failed: {run_id}: {child['returncode']}")
        seg = config["segments"]
        for number in range(1, seg["cpu_repeats"] + 1):
            start = time.monotonic()
            checksum = backend.cpu_probe(seg["cpu_iterations"])
            elapsed = time.monotonic() - start
            metadata["cpu"].append({"repeat": number, "seconds": elapsed, "checksum": checksum})
            if elapsed < seg["cpu_seconds"]:
                raise RuntimeError(f"CPU probe below {seg['cpu_seconds']} s minimum")
        backend.sleep(seg["settle_seconds"])
    except BaseException:
        write_json(out / "error.json", {"traceback": traceback.format_exc()})
        raise
    finally:
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
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--allow-pid", action="append", type=int, default=[])
    args = parser.parse_args(argv)
    try:
        run(args.out, load_config(args.config), args.state, args.context, args.cell_id,
            stage=args.stage, allow_pids=args.allow_pid, python=args.python)
        return 0
    except BaseException:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
