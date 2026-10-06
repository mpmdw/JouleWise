"""Fakes at the hardware seams of joulewise.hazards: clocks, probe children, ps.

Nothing here replaces hazard code: every fake stands where a kernel clock, a
probe binary or the process table would answer.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from joulewise.hazards import base

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "hazards"
BATTERY = FIXTURES / "battery"
INSTRUMENT = FIXTURES / "instrument"
FAKE_POWERMETRICS = INSTRUMENT / "fake_powermetrics.py"
NS = 1_000_000_000
FREQUENCY_SCALE = 1 << 16


def ppm_word(ppm: float) -> int:
    return int(round(ppm * FREQUENCY_SCALE))


class FakeClocks:
    """Three clocks on one simulated timeline.

    RAW advances with simulated time; ``time.monotonic_ns`` runs at a fixed
    offset from RAW (no sleep is simulated); REALTIME = RAW + anchor, where
    the anchor drifts at ``drift_word`` (ntp_adjtime units) and jumps by any
    injected step.  ``sleep`` advances time; every read advances it by
    ``read_cost_ns`` so reads are ordered.
    """

    def __init__(self, *, wall_s: float = 1_791_249_487.0, drift_word: int = ppm_word(-3.17),
                 read_cost_ns: int = 200, skew_ns: int = 0) -> None:
        self.raw_ns = 1_000_000 * NS
        self.start_raw_ns = self.raw_ns
        self.mono_offset_ns = -400 * NS
        self.anchor0_ns = int(wall_s * NS) - self.raw_ns
        self.drift_word = drift_word
        self.steps: list[tuple[int, int]] = []  # (raw_ns at which, step_ns)
        self.read_cost_ns = read_cost_ns
        self.skew_ns = skew_ns  # extra RAW time inside each REALTIME read
        self.sleeps: list[float] = []

    # time base
    def advance(self, seconds: float) -> None:
        self.raw_ns += int(round(seconds * NS))

    def step_at(self, after_s: float, step_ns: int) -> None:
        self.steps.append((self.start_raw_ns + int(after_s * NS), step_ns))

    def anchor_ns(self, raw_ns: int) -> int:
        elapsed = raw_ns - self.start_raw_ns
        drift = self.drift_word * elapsed // (FREQUENCY_SCALE * 1_000_000)
        return self.anchor0_ns + drift + sum(step for at, step in self.steps if raw_ns >= at)

    # the SystemClocks interface
    def _tick(self) -> int:
        self.raw_ns += self.read_cost_ns
        return self.raw_ns

    def monotonic_raw_ns(self) -> int:
        return self._tick()

    def monotonic_ns(self) -> int:
        return self._tick() + self.mono_offset_ns

    def realtime_ns(self) -> int:
        raw = self._tick()
        self.raw_ns += self.skew_ns
        return raw + self.anchor_ns(raw)

    def clock_gettime_ns(self, clock_id: int) -> int:
        if clock_id == time.CLOCK_REALTIME:
            return self.realtime_ns()
        if clock_id == time.CLOCK_MONOTONIC_RAW:
            return self.monotonic_raw_ns()
        raise AssertionError(f"unexpected clock id {clock_id}")

    def stamp(self) -> base.Stamp:
        raw = self.monotonic_raw_ns()
        mono = self.monotonic_ns()
        wall = self.realtime_ns()
        return base.Stamp(wall_ns=wall, monotonic_ns=mono, monotonic_raw_ns=raw)

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        if seconds > 0:
            self.advance(seconds)

    @property
    def wall_s(self) -> float:
        return (self.raw_ns + self.anchor_ns(self.raw_ns)) / NS


def frequency_probe(raw_word: int) -> dict[str, Any]:
    """A valid ``kernel_clock`` probe record for a given word (its raw bytes included)."""

    from joulewise import kernel_clock
    value = kernel_clock.Timex()
    value.freq = raw_word
    value.status = 5
    raw = bytes(value)
    return {"schema_version": kernel_clock.PROBE_SCHEMA, "modes": 0, "raw_word": raw_word,
            "ppm": raw_word / FREQUENCY_SCALE, "call_status": 5, "timex_status": 5,
            "errno": 0, "raw_hex": raw.hex()}


class FrequencyReader:
    """ntp_adjtime at the seam: the word comes from the fake clocks (changeable)."""

    def __init__(self, clocks: FakeClocks, *, fail: bool = False) -> None:
        self.clocks = clocks
        self.fail = fail
        self.calls = 0

    def __call__(self) -> dict[str, Any]:
        self.calls += 1
        if self.fail:
            raise OSError("ntp_adjtime failed")
        return frequency_probe(self.clocks.drift_word)


BOOT_UUID = "8a1c39f4-3c3e-4b8e-9f4e-0d2b6f3f8a11"


def completed(argv: Sequence[str], stdout: bytes = b"", *, returncode: int = 0,
              stderr: bytes = b"", timed_out: bool = False, error: str | None = None) -> base.Completed:
    return base.Completed(tuple(argv), returncode, stdout, stderr, timed_out, error)


class Runner:
    """Probe children at the seam.  ``handlers`` maps argv tuples (or argv[0])
    to a callable(argv) -> Completed.  Unknown argv fail the test loudly,
    except the instrument child (the real Python executable), which runs for real."""

    def __init__(self, handlers: Mapping[Any, Callable[[tuple[str, ...]], base.Completed]] = (),
                 *, real_python: bool = True) -> None:
        self.handlers = dict(handlers)
        self.calls: list[tuple[str, ...]] = []
        self.real_python = real_python

    def __call__(self, argv: Sequence[str], timeout_s: float) -> base.Completed:
        argv = tuple(str(item) for item in argv)
        self.calls.append(argv)
        handler = self.handlers.get(argv) or self.handlers.get(argv[0])
        if handler is not None:
            return handler(argv)
        if self.real_python and argv[0] == sys.executable:
            return base.run_probe(argv, timeout_s)
        raise AssertionError(f"unexpected probe argv {argv}")


def battery_bytes(name: str) -> bytes:
    return (BATTERY / name).read_bytes()


def update_time(raw: bytes) -> int:
    from joulewise.hazards import battery
    return battery.update_time(raw)


def registry_values(raw: bytes) -> dict[str, Any]:
    """The six top-level AppleSmartBattery properties as the IO registry holds
    them (what ``battery.RegistryReader.read`` returns), read off ioreg's text:
    Yes/No as booleans, integers signed 64-bit."""

    import re
    from joulewise.hazards import battery
    out: dict[str, Any] = {}
    for key in battery.REGISTRY_KEYS:
        match = re.search(rb'^ {6}"' + key.encode() + rb'" = (Yes|No|[0-9]{1,20})$', raw, re.M)
        if match is None:
            out[key] = None
        elif match.group(1) in (b"Yes", b"No"):
            out[key] = match.group(1) == b"Yes"
        else:
            value = int(match.group(1))
            out[key] = value - 2 ** 64 if value >= 2 ** 63 else value
    return out


class FakeRegistry:
    """``battery.RegistryReader`` at the seam: the same fake gauge ioreg reads.

    ``source()`` returns the bytes ioreg would print now; ``fail`` makes reads
    raise as a missing service does.
    """

    def __init__(self, source: Callable[[], bytes]) -> None:
        self.source = source
        self.calls = 0
        self.fail = False

    def read(self) -> dict[str, Any]:
        self.calls += 1
        if self.fail:
            raise OSError("no AppleSmartBattery service in the IO registry")
        return registry_values(self.source())


class FakeSmc:
    """``smc.Reader`` at the seam: B0AC from ``current(t)`` on the fake clocks'
    timeline (t in seconds since construction; 0 mA unless a test sets one).

    ``fail`` makes every key unreadable, as a missing AppleSMC service does.
    """

    def __init__(self, clocks: "FakeClocks", *, current: Callable[[float], int] = lambda t: 0) -> None:
        self.clocks = clocks
        self.start_raw_ns = clocks.raw_ns
        self.current = current
        self.fail = False
        self.calls = 0

    def elapsed_s(self) -> float:
        return (self.clocks.raw_ns - self.start_raw_ns) / NS

    def read(self, keys: Sequence[str] = ("B0AC", "B0AV", "PDTR", "PSTR", "PPBR")) -> dict[str, Any]:
        self.calls += 1
        if self.fail:
            return {"values": {key: None for key in keys},
                    "errors": {key: f"{key}: OSError: no AppleSMC service in the IO registry"
                               for key in keys}}
        # PSTR moves with time as the real block does (it republishes about once a second)
        values = {"B0AC": self.current(self.elapsed_s()), "B0AV": 12180, "PDTR": 48.1,
                  "PSTR": round(49.2 + 0.001 * self.elapsed_s(), 6), "PPBR": 0.41}
        return {"values": {key: values.get(key) for key in keys}, "errors": {}}

    def __call__(self) -> dict[str, Any]:  # the arm's ``smc_read`` seam
        return self.read()


# --------------------------------------------------------------------------
# ps


class Process:
    def __init__(self, pid: int, ppid: int, command: str, *, cpu_per_s: float = 0.0,
                 start_epoch: float = 1_790_000_000.0, cpu0: float = 1.0) -> None:
        self.pid, self.ppid, self.command = pid, ppid, command
        self.cpu_per_s = cpu_per_s
        self.start_epoch = start_epoch
        self.cpu = cpu0
        self.schedule: list[tuple[float, float, float]] = []  # (from_s, to_s, rate)

    def rate_at(self, t: float) -> float:
        for start, stop, rate in self.schedule:
            if start <= t < stop:
                return rate
        return self.cpu_per_s


class FakeProcessTable:
    """A process table whose cumulative CPU grows with the fake clocks' time.

    ``ps`` output is rendered in the exact layout of ``ps -Ao
    pid,ppid,lstart,time,ucomm`` under LC_ALL=C.
    """

    def __init__(self, clocks: FakeClocks, *, driver_pid: int = 4000) -> None:
        self.clocks = clocks
        self.driver_pid = driver_pid
        self.t0_raw = clocks.raw_ns
        self.last_raw = clocks.raw_ns
        self.processes: dict[int, Process] = {}
        self.add(Process(1, 0, "launchd", cpu_per_s=0.004, cpu0=24000.0))
        self.add(Process(driver_pid, 1, "Python", cpu_per_s=0.02))
        self.add(Process(310, 1, "WindowServer", cpu_per_s=0.01))
        self.add(Process(320, 1, "mds_stores", cpu_per_s=0.001))
        self.add(Process(330, 1, "backupd", cpu_per_s=0.0))
        self.add(Process(340, 1, "fseventsd", cpu_per_s=0.002))
        self.add(Process(350, 1, "mediaanalysisd", cpu_per_s=0.0))
        self.add(Process(360, 1, "XprotectService", cpu_per_s=0.0))
        self.next_pid = 9000
        # The host's CPU, as host_processor_info counts it: every listed process's
        # time plus ``hidden_cpu_per_s`` of work ps never lists (processes that
        # start and exit between snapshots, kernel threads).
        self.hidden_cpu_per_s = 0.0
        self.host_busy_s = 0.0
        self.cpus = 16

    def add(self, process: Process) -> Process:
        self.processes[process.pid] = process
        return process

    def elapsed_s(self) -> float:
        return (self.clocks.raw_ns - self.t0_raw) / NS

    def _advance(self) -> None:
        now = self.clocks.raw_ns
        a, b = (self.last_raw - self.t0_raw) / NS, (now - self.t0_raw) / NS
        if b > a:
            for process in self.processes.values():
                # integrate the piecewise-constant rate over [a, b] at 0.1 s resolution
                steps = max(1, int((b - a) / 0.1))
                width = (b - a) / steps
                used = sum(process.rate_at(a + (i + 0.5) * width) for i in range(steps)) * width
                process.cpu += used
                self.host_busy_s += used
            self.host_busy_s += self.hidden_cpu_per_s * (b - a)
        self.last_raw = now

    def host_cpu(self) -> list[list[int]]:
        """``contention.read_host_cpu`` at the seam: one row per logical CPU,
        [user, system, idle, nice] ticks at 100 per CPU-second."""

        self._advance()
        busy = int(round(self.host_busy_s * 100))
        total = int(round(self.elapsed_s() * 100)) * self.cpus + 10**9
        rows = [[0, 0, 0, 0] for _ in range(self.cpus)]
        rows[0][0] = busy % (1 << 32)
        rows[0][2] = max(0, total - busy) % (1 << 32)
        return rows

    def ps(self, argv: Sequence[str]) -> base.Completed:
        self._advance()
        # the ps child itself is a short-lived descendant of the driver
        lines = ["  PID  PPID STARTED                           TIME UCOMM"]
        ps_pid = self.next_pid
        self.next_pid += 1
        rows = list(self.processes.values()) + [Process(ps_pid, self.driver_pid, "ps",
                                                        start_epoch=self.clocks.wall_s, cpu0=0.0)]
        for process in sorted(rows, key=lambda item: item.pid):
            start = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(process.start_epoch))
            minutes, seconds = divmod(process.cpu, 60)
            lines.append(f"{process.pid:5d} {process.ppid:5d} {start}  {int(minutes):5d}:{seconds:05.2f} "
                         f"{process.command:<16s}")
        return completed(argv, ("\n".join(lines) + "\n").encode())


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value))
