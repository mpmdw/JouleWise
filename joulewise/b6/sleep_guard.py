"""Block-6 sleep readings and the driver's independent no-sleep assertion."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import time

# Threshold-proportion council 8.1, S1: strictly more than 1 ms excludes.
SLEEP_EXCLUDE_NS = 1_000_000


def append_record(path: Path, row: dict) -> None:
    """Plain collection records: one O_APPEND write, without custody machinery."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(row, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        if os.write(fd, data) != len(data):
            raise OSError("short collection journal write")
    finally:
        os.close(fd)


def read_sleep_offset(reader=time.clock_gettime_ns) -> dict:
    for _ in range(3):
        first = reader(time.CLOCK_UPTIME_RAW)
        raw = reader(time.CLOCK_MONOTONIC_RAW)
        second = reader(time.CLOCK_UPTIME_RAW)
        if second - first <= 100_000:
            break
    uptime = (first + second) // 2
    return {"uptime_raw_ns": uptime, "monotonic_raw_ns": raw,
            "monotonic_ns": time.monotonic_ns(), "wall_s": time.time(),
            "sleep_offset_ns": raw - uptime, "read_skew_ns": second - first}


def safe_sleep_reading() -> dict:
    try:
        return read_sleep_offset()
    except Exception as error:
        return {"monotonic_ns": time.monotonic_ns(), "wall_s": time.time(),
                "error": f"{type(error).__name__}: {error}"}


def slept_ns(start: dict | None, end: dict | None) -> int | None:
    if not start or not end:
        return None
    a, b = start.get("sleep_offset_ns"), end.get("sleep_offset_ns")
    return b - a if isinstance(a, int) and isinstance(b, int) else None


def run_sleep_flags(start: dict, end: dict, previous_end: dict | None = None) -> list[dict]:
    inside, between = slept_ns(start, end), slept_ns(previous_end, start)
    flags = []
    if inside is None:
        flags.append({"code": "sleep.reading_unmeasured", "observed": {"start": start, "end": end}})
    elif inside > SLEEP_EXCLUDE_NS:
        flags.append({"code": "sleep.in_run", "observed": {"slept_ns": inside}})
    if between is not None and between > SLEEP_EXCLUDE_NS:
        flags.append({"code": "sleep.between_runs", "observed": {"slept_ns": between}})
    return flags


def parse_pmset_assertions(text: str, pid: int) -> bool:
    return any(re.search(rf"\bpid\s+{pid}\s*\(", line)
               and re.search(r"\bPreventUserIdleSystemSleep\b", line)
               for line in text.splitlines())


class KeepAwake:
    def __init__(self, popen=subprocess.Popen, run_command=subprocess.run, pid=None):
        self.popen, self.run_command = popen, run_command
        self.driver_pid = os.getpid() if pid is None else pid
        self.process = None
        self.restarts = 0
        self.error = None
        self.last_loss = False

    def start(self) -> bool:
        try:
            self.process = self.popen(
                ["/usr/bin/caffeinate", "-i", "-s", "-w", str(self.driver_pid)],
                start_new_session=True, stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.error = None
            return True
        except Exception as error:
            self.process = None
            self.error = f"{type(error).__name__}: {error}"
            return False

    def poll(self) -> bool:
        self.last_loss = False
        if self.process is not None and self.process.poll() is None:
            return False
        self.last_loss = self.process is not None
        if self.last_loss:
            self.restarts += 1
        self.start()
        return True

    def verify(self) -> dict:
        pid = getattr(self.process, "pid", None)
        try:
            result = self.run_command(["/usr/bin/pmset", "-g", "assertions"],
                                      capture_output=True, text=True, timeout=10)
            verified = (result.returncode == 0 and pid is not None
                        and parse_pmset_assertions(result.stdout, pid))
            return {"pid": pid, "verified": verified, "error": self.error,
                    "returncode": result.returncode}
        except Exception as error:
            return {"pid": pid, "verified": False, "error": f"{type(error).__name__}: {error}"}

    def stop(self) -> None:
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=10)
