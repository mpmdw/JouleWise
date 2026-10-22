"""Jetson INA3221 rail acquisition and observed cadence characterization.

Sysfs voltage is mV and current is mA; their product / 1e6 is watts.
Acquisition errors remain flags and missing samples, never zero-power samples.
"""

from __future__ import annotations

import json
import math
import statistics
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from joulewise.align.records import PowerTrace


@dataclass(frozen=True)
class Rail:
    channel: str
    label: str
    device: Path
    voltage: Path
    current: Path


@dataclass(frozen=True)
class RailCharacterization:
    channel: str
    read_latency_ns: tuple[int, ...]
    distinct_periods_ns: tuple[int, ...]
    quantum_w: float | None
    voltage_quantum_mv: float | None
    current_quantum_ma: float | None
    flags: tuple[str, ...] = ()

    @property
    def median_distinct_period_ns(self) -> float | None:
        return statistics.median(self.distinct_periods_ns) if self.distinct_periods_ns else None


@dataclass(frozen=True)
class Characterization:
    rails: tuple[RailCharacterization, ...]
    update_intervals_ms: tuple[tuple[str, int | None], ...]
    flags: tuple[str, ...]


def _step(values: list[float]) -> float | None:
    distinct = sorted(set(values))
    steps = [b - a for a, b in zip(distinct, distinct[1:]) if b > a]
    return min(steps) if steps else None


class Ina3221Sampler:
    """PowerSampler for hwmon and legacy L4T iio layouts.

    The polling interval is a caller-selected scheduler target, not a claim
    about sensor conversion time. Use characterize() under changing load to
    measure observed cadence. No ADC resolution or averaging window is assumed.
    """

    clock_domain = "host.monotonic"

    def __init__(
        self, *, sysfs_root: str | Path = "/sys", sample_interval_ns: int,
        update_interval_ms: int | None = None,
        averaging_window_ns: int | None = None,
        clock_domain: str = "host.monotonic",
        clock: Callable[[], int] = time.monotonic_ns,
        read_text: Callable[[Path], str] | None = None,
    ) -> None:
        self.root = Path(sysfs_root)
        self.sample_interval_ns = sample_interval_ns
        self.requested_update_interval_ms = update_interval_ms
        self.averaging_window_ns = averaging_window_ns
        self.clock_domain = clock_domain
        self._clock = clock
        self._read = read_text or (lambda path: path.read_text(encoding="utf-8").strip())
        self.flags: list[str] = []
        self.rails: tuple[Rail, ...] = ()
        self.update_intervals_ms: dict[str, int | None] = {}
        self._original_intervals: dict[Path, str] = {}
        self._rows: dict[str, list[tuple[int, float, float, float, int]]] = {}
        self._event = threading.Event()
        self._thread: threading.Thread | None = None

    def _flag(self, message: str) -> None:
        if message not in self.flags:
            self.flags.append(message)

    def discover(self) -> tuple[Rail, ...]:
        """Discover once per physical device, including sysfs symlink aliases."""
        patterns = (
            "bus/i2c/drivers/ina3221*/*/hwmon/hwmon*",
            "bus/i2c/drivers/ina3221*/*/iio:device*",
            "bus/i2c/devices/*/hwmon/hwmon*",
            "bus/i2c/devices/*/iio:device*",
            "devices/platform/**/hwmon/hwmon*",
            "devices/platform/**/iio:device*",
        )
        found: dict[Path, Path] = {}
        for pattern in patterns:
            for path in sorted(self.root.glob(pattern)):
                if not path.is_dir():
                    continue
                try:
                    name = self._read(path / "name").lower() if (path / "name").exists() else ""
                    driver_path = "ina3221" in str(path).lower()
                    if driver_path or "ina3221" in name:
                        found.setdefault(path.resolve(), path)
                except (OSError, ValueError) as exc:
                    self._flag(f"discovery_read_error:{path}:{type(exc).__name__}")
        rails = []
        for device in sorted(found):
            labels = sorted(device.glob("in*_label")) + sorted(device.glob("rail_name_*"))
            for label_path in labels:
                legacy = label_path.name.startswith("rail_name_")
                index = (label_path.name.removeprefix("rail_name_") if legacy else
                         label_path.name.removeprefix("in").removesuffix("_label"))
                if not index.isdigit():
                    continue
                voltage = device / (f"in_voltage{index}_input" if legacy else f"in{index}_input")
                current = device / (f"in_current{index}_input" if legacy else f"curr{index}_input")
                try:
                    label = self._read(label_path)
                except OSError as exc:
                    label = label_path.stem
                    self._flag(f"label_read_error:{label_path}:{type(exc).__name__}")
                channel = f"{device.relative_to(self.root.resolve())}/{index}:{label}"
                rails.append(Rail(channel, label, device, voltage, current))
                if not voltage.exists() or not current.exists():
                    self._flag(f"missing_rail_attribute:{channel}")
            interval_path = device / "update_interval"
            if not interval_path.exists() and (device.parent / "update_interval").exists():
                interval_path = device.parent / "update_interval"
            self._configure_interval(device, interval_path)
        self.rails = tuple(rails)
        if not self.rails:
            self._flag("ina3221_unavailable")
        return self.rails

    def _configure_interval(self, device: Path, path: Path) -> None:
        try:
            original = self._read(path)
            observed = int(original)
            if self.requested_update_interval_ms is not None:
                requested = self.requested_update_interval_ms
                if requested <= 0:
                    self._flag("invalid_update_interval_ms")
                else:
                    try:
                        path.write_text(str(requested), encoding="utf-8")
                        self._original_intervals[path] = original
                        observed = int(self._read(path))
                        if observed != requested:
                            self._flag(f"update_interval_clamped:{device}:{observed}")
                    except (OSError, ValueError) as exc:
                        self._flag(f"update_interval_refused:{device}:{type(exc).__name__}")
            self.update_intervals_ms[str(device)] = observed
        except (OSError, ValueError) as exc:
            self.update_intervals_ms[str(device)] = None
            self._flag(f"update_interval_unavailable:{device}:{type(exc).__name__}")

    def _restore_intervals(self) -> None:
        for path, original in self._original_intervals.items():
            try:
                path.write_text(original, encoding="utf-8")
            except OSError as exc:
                self._flag(f"update_interval_restore_error:{path}:{type(exc).__name__}")
        self._original_intervals.clear()

    def sample_once(self) -> None:
        """Acquire every rail through the production read path; useful for probes."""
        for rail in self.rails:
            before = self._clock()
            try:
                voltage = float(self._read(rail.voltage))
                current = float(self._read(rail.current))
                watts = voltage * current / 1_000_000  # mV * mA -> W.
                after = self._clock()
                if not all(math.isfinite(x) for x in (voltage, current, watts)):
                    self._flag(f"nonfinite_read:{rail.channel}")
                    continue
                rows = self._rows.setdefault(rail.channel, [])
                if rows and after <= rows[-1][0]:
                    self._flag(f"nonincreasing_clock:{rail.channel}")
                    continue
                rows.append((after, watts, voltage, current, after - before))
            except (OSError, ValueError) as exc:
                self._flag(f"rail_read_error:{rail.channel}:{type(exc).__name__}")

    def start(self) -> None:
        if self._thread is not None:
            self._flag("sampler_already_started")
            return
        self.flags.clear()
        self._rows.clear()
        self.update_intervals_ms.clear()
        self.discover()
        self._event.clear()
        if self.sample_interval_ns <= 0:
            self._flag("invalid_sample_interval_ns")
            return
        # Acquire the first sample synchronously so short episodes have coverage.
        self.sample_once()
        self._thread = threading.Thread(target=self._run, name="ina3221", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        deadline = time.monotonic_ns() + self.sample_interval_ns
        while not self._event.wait(max(0, deadline - time.monotonic_ns()) / 1_000_000_000):
            self.sample_once()
            now = time.monotonic_ns()
            deadline += self.sample_interval_ns
            if deadline < now:
                self._flag("sampler_overrun")
                deadline = now + self.sample_interval_ns

    def stop(self) -> tuple[PowerTrace, ...]:
        self._event.set()
        if self._thread is not None:
            self._thread.join()
            self._thread = None
        self._restore_intervals()
        channels = [rail.channel for rail in self.rails] or ["unavailable"]
        notes = json.dumps({"flags": self.flags, "update_intervals_ms": self.update_intervals_ms,
                            "timestamps": "end_of_nonatomic_voltage_current_read"}, sort_keys=True)
        return tuple(PowerTrace(
            "ina3221", channel, self.clock_domain,
            tuple(row[0] for row in self._rows.get(channel, [])),
            tuple(row[1] for row in self._rows.get(channel, [])), "W",
            max(0, self.sample_interval_ns), self.averaging_window_ns,
            notes=notes,
        ) for channel in channels)

    def characterize(self, *, reads: int, sleep: Callable[[float], None] = time.sleep) -> Characterization:
        """Measure latency, change periods and observed steps; never assume 840 us.

        Stationary/quantized inputs can hide conversions. Minimum distinct step
        is only an observed upper bound on ADC quantum. No-change is flagged.
        """
        if self._thread is not None:
            self._flag("characterization_while_sampling")
            return Characterization((), tuple(self.update_intervals_ms.items()), tuple(self.flags))
        self._rows.clear()
        self.discover()
        if reads <= 0 or self.sample_interval_ns <= 0:
            self._flag("invalid_characterization_parameters")
        else:
            for index in range(reads):
                if index:
                    sleep(self.sample_interval_ns / 1_000_000_000)
                self.sample_once()
        results = []
        for rail in self.rails:
            rows = self._rows.get(rail.channel, [])
            changes = [row[0] for previous, row in zip(rows, rows[1:]) if row[1] != previous[1]]
            flags = () if len(changes) >= 2 else ("insufficient_distinct_changes",)
            results.append(RailCharacterization(
                rail.channel, tuple(row[4] for row in rows),
                tuple(b - a for a, b in zip(changes, changes[1:])),
                _step([row[1] for row in rows]), _step([row[2] for row in rows]),
                _step([row[3] for row in rows]), flags,
            ))
        self._restore_intervals()
        return Characterization(tuple(results), tuple(self.update_intervals_ms.items()), tuple(self.flags))
