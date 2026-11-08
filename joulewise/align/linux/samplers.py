"""Linux package energy and pluggable AC wall-meter polling, stdlib only.

All query brackets and native readings survive in trace notes. HTTP readings
are receipt-time observations: meter-side latency/averaging is uncalibrated.
NVML's existing ctypes sampler lives in align.power.nvml, unchanged.
"""
from __future__ import annotations

import bisect
import csv
import json
import math
from pathlib import Path
import threading
import time
from typing import Protocol, runtime_checkable
import urllib.parse
import urllib.request

from joulewise.align.records import PowerTrace


@runtime_checkable
class WallMeterAdapter(Protocol):
    """A pluggable adapter returns native AC watts and its raw JSON reading."""

    identity: str

    def read(self) -> tuple[float, object]: ...


class PollingSampler:
    """Synchronous opening/closing readings bracket the episode; bounded stop.

    A failed poll is a gap, never a fabricated zero. read() implementations must
    bound their I/O. A timed-out worker cannot be restarted or raced by stop().
    """

    clock_mappings = ()

    def __init__(self, *, interval_s=1.0, clock_domain="linux:monotonic",
                 clock_ns=time.monotonic_ns, stop_timeout_s=10.0):
        if not math.isfinite(interval_s) or interval_s <= 0:
            raise ValueError("interval_s must be positive and finite")
        self.interval_s = interval_s
        self.clock_domain = clock_domain
        self.clock = clock_ns
        self.stop_timeout_s = stop_timeout_s
        self.thread = None
        self.event = threading.Event()
        self.result = None
        self.rows = []
        self.flags = []
        self.channels = {}
        self.raw = []
        self.lock = threading.Lock()

    def prepare(self):
        pass

    def read(self):
        raise NotImplementedError

    def poll(self):
        start = self.clock()
        raw = None
        try:
            readings, raw = self.read()
            readings = dict(readings)
            if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0
                   for v in readings.values()):
                raise ValueError("readings must be finite nonnegative numbers")
            end = self.clock()
            if end < start:
                raise ValueError("query clock regressed")
            stamp = (start + end) // 2
            with self.lock:
                if self.rows and stamp <= self.rows[-1][0]:
                    raise ValueError("sample clock not increasing")
                self.rows.append((stamp, readings))
                self.raw.append({"start_ns": start, "end_ns": end, "reading": raw})
        except Exception as exc:
            with self.lock:
                self.flags.append("poll_error:" + type(exc).__name__)
                self.raw.append({"start_ns": start, "end_ns": self.clock(),
                                 "reading": raw, "error": str(exc)})

    def _loop(self):
        while not self.event.wait(self.interval_s):
            self.poll()

    def start(self):
        if self.thread is not None and self.thread.is_alive():
            raise RuntimeError("previous sampler worker still active")
        self.rows, self.flags, self.raw, self.result = [], [], [], None
        self.event = threading.Event()
        try:
            self.prepare()
            self.poll()
            self.thread = threading.Thread(target=self._loop, daemon=True,
                                           name=type(self).__name__)
            self.thread.start()
        except Exception as exc:
            self.flags.append("start_error:" + type(exc).__name__)
            self.raw.append({"error": str(exc)})

    def stop(self):
        if self.result is not None:
            return self.result
        self.event.set()
        active = self.thread is not None and self.thread.is_alive()
        if active:
            self.thread.join(self.stop_timeout_s)
        if self.thread is not None and self.thread.is_alive():
            self.flags.append("worker_stop_timeout")
        else:
            self.poll()
        with self.lock:
            notes = json.dumps({"flags": list(dict.fromkeys(self.flags)), "raw": self.raw,
                                "identity": self.identity,
                                "timing": "host monotonic query midpoint; sensor age unknown"})
            self.result = tuple(PowerTrace(
                source, channel, self.clock_domain,
                tuple(t for t, row in self.rows if channel in row),
                tuple(row[channel] for _, row in self.rows if channel in row), unit,
                round(self.interval_s * 1e9), resolution=resolution, notes=notes,
            ) for channel, (source, unit, resolution) in self.channels.items())
        return self.result


class RaplSampler(PollingSampler):
    """Top-level package domains only: never sum package and its subdomains.

    Keep the actual cumulative counter, including decreases. range_uj is raw
    metadata; wrap vs reset is ambiguous and not silently corrected. Sampling
    fast enough to distinguish multiple wraps is a rig qualification gate.
    """

    identity = "rapl:powercap:package"

    def __init__(self, root="/sys/class/powercap", **kwargs):
        super().__init__(**kwargs)
        self.root = Path(root)
        self.domains = []
        self.channels = {"package_unavailable": ("rapl_energy", "J_cumulative", 1e-6)}
        self.previous = {}

    def prepare(self):
        self.domains, self.previous = [], {}
        # Some kernels expose packages directly; others nest them in intel-rapl.
        candidates = sorted(set(self.root.glob("*:*")) | set(self.root.glob("*/*:*")))
        for path in candidates:
            name_path = path / "name"
            if not name_path.exists():
                continue
            name = name_path.read_text().strip()
            if name.startswith("package-"):
                self.domains.append((path, name))
        # sysfs can expose the same domain through multiple symlink aliases.
        self.domains = list({str(p.resolve()): (p, n) for p, n in self.domains}.values())
        if not self.domains:
            raise FileNotFoundError("no readable RAPL package domains")
        self.channels = {p.name + ":" + n: ("rapl_energy", "J_cumulative", 1e-6)
                         for p, n in self.domains}

    def read(self):
        values, raw = {}, []
        for path, name in self.domains:
            energy = int((path / "energy_uj").read_text().strip())
            modulus = int((path / "max_energy_range_uj").read_text().strip())
            if energy < 0 or modulus <= 0 or energy > modulus:
                raise ValueError("invalid RAPL counter/range")
            channel = path.name + ":" + name
            if channel in self.previous and energy < self.previous[channel]:
                self.flags.append("counter_decreased_wrap_or_reset:" + channel)
            self.previous[channel] = energy
            values[channel] = energy / 1e6
            raw.append({"domain": path.name, "name": name, "energy_uj": energy,
                        "max_energy_range_uj": modulus})
        return values, raw


class HttpJsonWallMeter:
    """GET a JSON object; power_field is a dotted key path in watts.

    Adapters for actual meters can implement WallMeterAdapter instead. No
    redirects or ambient proxies: avoid moving a measurement to another host.
    Optional timestamp_field enables stale/duplicate source-time detection.
    """

    def __init__(self, url, *, power_field="power_w", timestamp_field=None,
                 timeout_s=2.0, fetch=None):
        parsed = urllib.parse.urlsplit(url)
        if (parsed.scheme not in {"http", "https"} or not parsed.hostname
                or parsed.username or parsed.password or parsed.fragment):
            raise ValueError("invalid meter URL")
        if not math.isfinite(timeout_s) or timeout_s <= 0:
            raise ValueError("meter timeout must be positive and finite")
        self.url, self.power_field, self.timestamp_field = url, power_field, timestamp_field
        self.timeout_s, self.fetch = timeout_s, fetch
        self.identity = "http_json_ac_wall_meter"
        self.last_source_time = None

    def read(self):
        if self.fetch:
            raw = self.fetch(self.url, self.timeout_s)
        else:
            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, *args, **kwargs):
                    return None
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
            with opener.open(self.url, timeout=self.timeout_s) as response:
                raw = response.read(1_048_577)
            if len(raw) > 1_048_576:
                raise ValueError("meter response exceeds 1 MiB")
            raw = json.loads(raw)
        def field(key):
            value = raw
            for part in key.split("."):
                value = value[part]
            return value
        power = field(self.power_field)
        if type(power) not in (int, float) or not math.isfinite(power) or power < 0:
            raise ValueError("meter watts must be finite and nonnegative")
        if self.timestamp_field:
            stamp = field(self.timestamp_field)
            if (type(stamp) not in (int, float) or not math.isfinite(stamp)
                    or (self.last_source_time is not None and stamp <= self.last_source_time)):
                raise ValueError("stale or invalid meter source timestamp")
            self.last_source_time = stamp
        return float(power), raw


class CsvReplayWallMeter:
    """Replay elapsed_s,power_w rows against a supplied monotonic clock.

    Linear interpolation is synthetic test evidence. Never label a replay as
    live AC measurement. An exhausted stream fails instead of holding forever.
    """

    identity = "csv_replay_ac_wall_meter:SYNTHETIC"

    def __init__(self, path, *, clock_ns=time.monotonic_ns):
        with Path(path).open(newline="") as handle:
            self.rows = [(float(r["elapsed_s"]), float(r["power_w"])) for r in csv.DictReader(handle)]
        if (not self.rows or self.rows[0][0] != 0 or
                any(not math.isfinite(t) or not math.isfinite(p) or t < 0 or p < 0 for t, p in self.rows)
                or any(b[0] <= a[0] for a, b in zip(self.rows, self.rows[1:]))):
            raise ValueError("CSV requires increasing finite elapsed_s from zero and nonnegative watts")
        self.times = [r[0] for r in self.rows]
        self.clock = clock_ns
        self.origin = None

    def read(self):
        now = self.clock()
        if self.origin is None:
            self.origin = now
        elapsed = (now - self.origin) / 1e9
        if elapsed < 0 or elapsed > self.times[-1]:
            raise EOFError("replay exhausted or clock regressed")
        index = bisect.bisect_right(self.times, elapsed) - 1
        watts = self.rows[index][1]
        if index + 1 < len(self.rows):
            t0, p0 = self.rows[index]
            t1, p1 = self.rows[index + 1]
            watts = p0 + (p1 - p0) * (elapsed - t0) / (t1 - t0)
        return watts, {"elapsed_s": elapsed, "power_w": watts, "synthetic": True}


class WallMeterSampler(PollingSampler):
    """Always supplied to Linux episodes, including when no meter is configured."""

    def __init__(self, adapter: WallMeterAdapter | None, **kwargs):
        super().__init__(**kwargs)
        self.adapter = adapter
        self.identity = getattr(adapter, "identity", "wall_meter:missing")
        self.channels = {"ac_wall": ("wall_meter", "W", None)}

    def read(self):
        if self.adapter is None:
            raise RuntimeError("wall meter not configured")
        power, raw = self.adapter.read()
        return {"ac_wall": power}, raw
