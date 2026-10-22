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
    def cadence_ns(self) -> float | None:
        """Endpoint-span cadence: end poll errors cancel across all periods.

        If each endpoint is late by < one poll, the mean error is bounded by
        one actual poll period / number of observed periods. A median instead
        picks a neighboring poll multiple when conversion and poll do not tile.
        """
        return statistics.fmean(self.distinct_periods_ns) if self.distinct_periods_ns else None

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
    measure observed cadence. Driver exposure is carried into every trace. ADC current resolution needs
    the board shunt or a supplied characterization.
    """

    clock_domain = "host.monotonic"

    def __init__(
        self, *, sysfs_root: str | Path = "/sys", sample_interval_ns: int,
        update_interval_ms: int | None = None,
        averaging_window_ns: int | None = None,
        characterization: Characterization | None = None,
        shunt_resistance_ohm: float | None = None,
        clock_domain: str = "host.monotonic",
        clock: Callable[[], int] = time.monotonic_ns,
        read_text: Callable[[Path], str] | None = None,
    ) -> None:
        self.root = Path(sysfs_root)
        self.sample_interval_ns = sample_interval_ns
        self.requested_update_interval_ms = update_interval_ms
        self.averaging_window_ns = averaging_window_ns
        self.characterization = characterization
        self.shunt_resistance_ohm = shunt_resistance_ohm
        self.clock_domain = clock_domain
        self._clock = clock
        self._read = read_text or (lambda path: path.read_text(encoding="utf-8").strip())
        self.flags: list[str] = []
        self.rails: tuple[Rail, ...] = ()
        self.update_intervals_ms: dict[str, int | None] = {}
        self.samples: dict[str, int | None] = {}
        self._health_before: dict[str, int | None] | None = None
        self._health_after: dict[str, int | None] = {}
        self._health_paths: set[Path] = set()
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
                # Mainline in7 is a sum of shunt voltages, not a bus rail:
                # it has no corresponding curr7_input. Keep genuinely missing
                # rail attributes visible (including the existing missing-rail test).
                if not legacy and "sum of shunt" in label.lower():
                    self._flag(f"summation_channel_skipped:{device}:{index}")
                    continue
                channel = f"{device.relative_to(self.root.resolve())}/{index}:{label}"
                rails.append(Rail(channel, label, device, voltage, current))
                if not voltage.exists() or not current.exists():
                    self._flag(f"missing_rail_attribute:{channel}")
            interval_path = device / "update_interval"
            if not interval_path.exists() and (device.parent / "update_interval").exists():
                interval_path = device.parent / "update_interval"
            self._configure_interval(device, interval_path)
            try:
                self.samples[str(device)] = int(self._read(device / "samples"))
            except (OSError, ValueError) as exc:
                self.samples[str(device)] = None
                self._flag(f"samples_unavailable:{device}:{type(exc).__name__}")
        self.rails = tuple(rails)
        if not self.rails:
            self._flag("ina3221_unavailable")
        return self.rails

    def _health_snapshot(self) -> dict[str, int | None]:
        """Read exposed alarms/warnings and the documented L4T OC nodes.

        NVIDIA L4T r36.4.4 Power and Performance / Overcurrent Event Status:
        /sys/class/hwmon/hwmon<x>/oc*_event_cnt. These can belong to a
        separate soctherm hwmon device, so discovery is independent of INA.
        No current limits, throttle enables or alarm controls are written.
        """
        devices = {rail.device for rail in self.rails}
        for rail in self.rails:
            if rail.current.name.startswith("curr"):
                index = rail.current.name.removeprefix("curr").removesuffix("_input")
                self._health_paths.update((rail.device / f"curr{index}_{kind}_alarm").resolve()
                                          for kind in ("crit", "max"))
        for device in devices:
            self._health_paths.update(path.resolve() for path in device.glob("*alarm*"))
            self._health_paths.update(path.resolve() for path in device.glob("*warn*"))
        # Resolve aliases once; do not count a physical counter twice.
        for pattern in ("class/hwmon/hwmon*/oc*_event_cnt",
                        "devices/platform/**/hwmon/hwmon*/oc*_event_cnt"):
            self._health_paths.update(path.resolve() for path in self.root.glob(pattern))
        for device in devices:
            self._health_paths.update(path.resolve() for path in device.glob("oc*_event_cnt"))
        if not any(p.name.endswith("_event_cnt") for p in self._health_paths):
            self._flag("oc_event_counters_unavailable")
        if not any(p.exists() and ("alarm" in p.name or "warn" in p.name)
                   for p in self._health_paths):
            self._flag("alarm_attributes_unavailable")
        snapshot = {}
        for path in sorted(self._health_paths):
            key = str(path.relative_to(self.root.resolve()))
            try:
                value = int(self._read(path))
                snapshot[key] = value
                if not path.name.endswith("_event_cnt") and value:
                    self._flag(f"hardware_alarm_set:{key}")
            except (OSError, ValueError) as exc:
                snapshot[key] = None
                self._flag(f"health_read_error:{key}:{type(exc).__name__}")
        return snapshot

    def _trace_sensor_metadata(self, rail: Rail) -> tuple[int | None, float | None]:
        """Propagate driver exposure and optional measured calibration.

        update_interval already includes the driver's averaging samples;
        multiplying by samples again would count averaging twice. Integer
        sysfs print precision supplies only a lower resolution bound when
        no shunt resistance/calibration is supplied; this is flagged.
        """
        rows = self._rows.get(rail.channel, [])
        configured = self.update_intervals_ms.get(str(rail.device))
        driver_window = configured * 1_000_000 if configured is not None and configured > 0 else None
        calibration = next((r for r in self.characterization.rails if r.channel == rail.channel),
                           None) if self.characterization else None
        if calibration:
            for flag in calibration.flags:
                self._flag(f"characterization:{rail.channel}:{flag}")
        cadence = calibration.cadence_ns if calibration else None
        # Held register values can reveal a slower cadence than the configured
        # integer-ms exposure. This is an observation, confounded by steady
        # loads; keep that limitation visible and prefer supplied calibration.
        changed = [row[0] for previous, row in zip(rows, rows[1:]) if row[1] != previous[1]]
        repeats = sum(a[1] == b[1] for a, b in zip(rows, rows[1:]))
        if (cadence is None and len(changed) >= max(2, math.isqrt(len(rows))) and
                repeats * 2 >= len(rows) - 1):
            cadence = statistics.median(b - a for a, b in zip(changed, changed[1:]))
            self._flag(f"cadence_inferred_from_held_values:{rail.channel}")
        if cadence and driver_window and abs(cadence - driver_window) > self.sample_interval_ns:
            # One poll is the endpoint quantization bound for one cadence
            # interval; disagreement larger than this is observable.
            self._flag(f"driver_characterized_cadence_disagreement:{rail.channel}")
        window = self.averaging_window_ns
        if window is None:
            exposures = [x for x in (driver_window, cadence) if x is not None]
            window = math.ceil(max(exposures)) if exposures else None
        quantum = calibration.quantum_w if calibration else None
        if quantum is None and rows:
            dv = _step([row[2] for row in rows])
            di = _step([row[3] for row in rows])
            # INA3221 bus LSB is 8 mV; shunt LSB is 40 uV (datasheet).
            # Current LSB depends on the actual board shunt, never assumed.
            dv = max(8.0, dv or 0.0)
            resistance = self.shunt_resistance_ohm
            if resistance is not None and resistance > 0 and math.isfinite(resistance):
                di = max(40e-6 / resistance * 1000, di or 0.0)
            else:
                if resistance is not None:
                    self._flag(f"invalid_shunt_resistance:{rail.channel}")
                # Mainline current is printed as integer mA. This bounds
                # print resolution only; it cannot establish the ADC LSB.
                di = max(1.0, di or 0.0)
                self._flag(f"resolution_print_precision_only:{rail.channel}")
            voltage = abs(statistics.median(row[2] for row in rows))
            current = abs(statistics.median(row[3] for row in rows))
            quantum = (voltage * di + current * dv + dv * di) / 1_000_000
        if window is None:
            self._flag(f"averaging_window_unknown:{rail.channel}")
        return window, quantum

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
                        self._original_intervals.setdefault(path, original)
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
        self.samples.clear()
        self._health_paths.clear()
        self._health_after.clear()
        self.discover()
        self._health_before = self._health_snapshot()
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
        # Manual sample_once users also receive a stop snapshot. A missing
        # start snapshot cannot establish a counter delta and is explicit.
        if self._health_before is None:
            self._health_before = self._health_snapshot()
            self._flag("health_start_snapshot_unavailable")
        self._health_after = self._health_snapshot()
        deltas = {}
        for key in sorted(set(self._health_before) | set(self._health_after)):
            if not key.endswith("_event_cnt"):
                continue
            before, after = self._health_before.get(key), self._health_after.get(key)
            deltas[key] = after - before if before is not None and after is not None else None
            if deltas[key] is not None:
                if deltas[key] > 0:
                    self._flag(f"overcurrent_throttle_events:{key}")
                elif deltas[key] < 0:
                    self._flag(f"oc_counter_reset:{key}")
        metadata = {rail.channel: self._trace_sensor_metadata(rail) for rail in self.rails}
        self._restore_intervals()
        channels = [rail.channel for rail in self.rails] or ["unavailable"]
        notes = json.dumps({
            "flags": self.flags, "update_intervals_ms": self.update_intervals_ms,
            "samples": self.samples,
            # Retain voltage extrema and their read-end times for the supply
            # sag preflight; no unexplained voltage-sag cutoff is imposed.
            "voltage_mv_extrema": {
                channel: {"minimum": min((row[2], row[0]) for row in rows),
                          "maximum": max((row[2], row[0]) for row in rows)}
                for channel, rows in self._rows.items() if rows},
            "health_start": self._health_before,
            "health_stop": self._health_after, "oc_event_count_deltas": deltas,
            "timestamps": "end_of_nonatomic_voltage_current_read",
        }, sort_keys=True)
        return tuple(PowerTrace(
            "ina3221", channel, self.clock_domain,
            tuple(row[0] for row in self._rows.get(channel, [])),
            tuple(row[1] for row in self._rows.get(channel, [])), "W",
            max(0, self.sample_interval_ns), metadata.get(channel, (None, None))[0],
            resolution=metadata.get(channel, (None, None))[1], notes=notes,
        ) for channel in channels)

    def characterize(self, *, reads: int, sleep: Callable[[float], None] = time.sleep) -> Characterization:
        """Measure latency, change periods and observed steps; never assume 840 us.

        Stationary/quantized inputs can hide conversions. Voltage/current steps
        are empirical observations, not calibrated LSBs. Watt resolution is
        propagated from those two steps at the observed operating point.
        """
        if self._thread is not None:
            self._flag("characterization_while_sampling")
            return Characterization((), tuple(self.update_intervals_ms.items()), tuple(self.flags))
        try:
            self._rows.clear()
            self.discover()
            if reads <= 0 or self.sample_interval_ns <= 0:
                self._flag("invalid_characterization_parameters")
            else:
                for index in range(reads):
                    if index:
                        sleep(self.sample_interval_ns / 1_000_000_000)
                    self.sample_once()
        except Exception as exc:
            self._flag(f"characterization_error:{type(exc).__name__}")
        finally:
            self._restore_intervals()
        results = []
        for rail in self.rails:
            rows = self._rows.get(rail.channel, [])
            changes = [row[0] for previous, row in zip(rows, rows[1:]) if row[1] != previous[1]]
            flags = [] if len(changes) >= 2 else ["insufficient_distinct_changes"]
            periods = tuple(b - a for a, b in zip(changes, changes[1:]))
            polls = [b[0] - a[0] for a, b in zip(rows, rows[1:])]
            # A change period within one actual poll of the poll interval
            # cannot resolve whether the sensor converted between polls.
            if periods and polls and statistics.median(periods) <= 2 * statistics.median(polls):
                flags.append("cadence_poll_limited")
            dq_v = _step([row[2] for row in rows])
            dq_i = _step([row[3] for row in rows])
            quantum = None
            if rows and (dq_v is not None or dq_i is not None):
                v = statistics.median(row[2] for row in rows)
                i = statistics.median(row[3] for row in rows)
                # P=VI: a simultaneous +1 LSB in each coordinate gives
                # dP=|V|dI+|I|dV+dV*dI, with mV*mA / 1e6 -> W.
                # Differences of VI products can nearly cancel and are NOT LSBs.
                dv, di = dq_v or 0.0, dq_i or 0.0
                quantum = (abs(v) * di + abs(i) * dv + dv * di) / 1_000_000
                if dq_v is None or dq_i is None:
                    flags.append("quantum_one_coordinate_unobserved")
            results.append(RailCharacterization(
                rail.channel, tuple(row[4] for row in rows),
                periods, quantum, dq_v, dq_i, tuple(flags),
            ))
        return Characterization(tuple(results), tuple(self.update_intervals_ms.items()), tuple(self.flags))
