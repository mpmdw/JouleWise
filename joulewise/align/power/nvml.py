"""NVIDIA board-power sampling without a required Python NVML package.

Each device owns one worker and four separate channels. Trace notes are JSON:
call brackets bound query timing, capabilities identify the measurement, and
counter discontinuities remain visible rather than being silently repaired.
The supplied alignment contract's slice model is provisional until checked on
the rented device; an NVML output average is not a single physical window.
"""

from __future__ import annotations

import ctypes
import json
import math
import os
import re
import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from joulewise.align.records import PowerTrace

# ABI, field IDs and output semantics:
# https://github.com/NVIDIA/go-nvml/blob/main/pkg/nvml/nvml.h
POWER_AVERAGE_FIELD = 185
POWER_INSTANT_FIELD = 186
ARCHITECTURES = {
    2: "kepler", 3: "maxwell", 4: "pascal", 5: "volta", 6: "turing",
    7: "ampere", 8: "ada", 9: "hopper", 10: "blackwell",
}
# Keyed by architecture, and restricted to the named devices: do not extend
# an A100 observation to every Ampere GPU. Source is the supplied records
# contract, not a new hardware measurement or a vendor accuracy guarantee.
SENSOR_FACTS = {
    "ampere": {
        "model_pattern": r"\bA100\b", "averaging_window_ns": 25_000_000,
        "period_ns": 100_000_000, "duty_fraction": 0.25,
        "source": "joulewise/align/records.py:PowerTrace (A100 slice assumption)",
    },
    "hopper": {
        "model_pattern": r"\bH100\b", "averaging_window_ns": 25_000_000,
        "period_ns": 100_000_000, "duty_fraction": 0.25,
        "source": "joulewise/align/records.py:PowerTrace (H100 slice assumption)",
    },
}


class NvmlError(RuntimeError):
    """An unavailable NVML entry point or an unsuccessful driver call."""


class _Value(ctypes.Union):
    _fields_ = [
        ("dVal", ctypes.c_double), ("uiVal", ctypes.c_uint),
        ("ulVal", ctypes.c_ulong), ("ullVal", ctypes.c_ulonglong),
        ("sllVal", ctypes.c_longlong), ("siVal", ctypes.c_int),
        ("usVal", ctypes.c_ushort),
    ]


class _FieldValue(ctypes.Structure):
    _fields_ = [
        ("fieldId", ctypes.c_uint), ("scopeId", ctypes.c_uint),
        ("timestamp", ctypes.c_longlong), ("latencyUsec", ctypes.c_longlong),
        ("valueType", ctypes.c_int), ("nvmlReturn", ctypes.c_int), ("value", _Value),
    ]


def _field_number(value: Any) -> float:
    names = {0: "dVal", 1: "uiVal", 2: "ulVal", 3: "ullVal",
             4: "sllVal", 5: "siVal", 6: "usVal"}
    if value.valueType not in names:
        raise NvmlError(f"unknown NVML valueType {value.valueType}")
    return float(getattr(value.value, names[value.valueType]))


class CtypesNvml:
    """Small pynvml-shaped binding; library may be a ctypes-shaped test stub."""

    def __init__(self, library: Any | None = None) -> None:
        self.library = library if library is not None else ctypes.CDLL(
            "nvml.dll" if os.name == "nt" else "libnvidia-ml.so.1"
        )

    def _call(self, names: str | tuple[str, ...], args: tuple[Any, ...] = (),
              types: tuple[Any, ...] = ()) -> None:
        choices = (names,) if isinstance(names, str) else names
        function = next((getattr(self.library, name) for name in choices
                         if hasattr(self.library, name)), None)
        if function is None:
            raise NvmlError(f"entry point unavailable: {choices[0]}")
        # Actual ctypes functions get an ABI declaration. Plain Python stubs
        # accept the same pointer objects but need no function attributes.
        if isinstance(function, ctypes._CFuncPtr):
            function.argtypes = list(types)
            function.restype = ctypes.c_int
        status = function(*args)
        if status != 0:  # NVML_SUCCESS is the ABI integer zero.
            raise NvmlError(f"{choices[0]} returned NVML status {status}")

    def nvmlInit(self) -> None:
        self._call(("nvmlInit_v2", "nvmlInit"))

    def nvmlShutdown(self) -> None:
        self._call("nvmlShutdown")

    def _uint(self, name: str | tuple[str, ...], handle: Any | None = None,
              wide: bool = False, signed: bool = False) -> int:
        scalar = ctypes.c_ulonglong if wide else (ctypes.c_int if signed else ctypes.c_uint)
        output = scalar()
        args = (ctypes.byref(output),) if handle is None else (handle, ctypes.byref(output))
        types = (ctypes.POINTER(scalar),) if handle is None else (
            ctypes.c_void_p, ctypes.POINTER(scalar))
        self._call(name, args, types)
        return int(output.value)

    def _text(self, name: str, handle: Any | None = None) -> str:
        # 96 bytes covers the header's 96-byte device-name buffer, as well as
        # its shorter driver/NVML-version, UUID and VBIOS strings.
        buffer = ctypes.create_string_buffer(96)
        args = (buffer, len(buffer)) if handle is None else (handle, buffer, len(buffer))
        types = (ctypes.c_char_p, ctypes.c_uint) if handle is None else (
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint)
        self._call(name, args, types)
        return buffer.value.decode("utf-8", errors="replace")

    def nvmlDeviceGetCount(self) -> int:
        return self._uint(("nvmlDeviceGetCount_v2", "nvmlDeviceGetCount"))

    def nvmlDeviceGetHandleByIndex(self, index: int) -> Any:
        handle = ctypes.c_void_p()
        self._call(("nvmlDeviceGetHandleByIndex_v2", "nvmlDeviceGetHandleByIndex"),
                   (index, ctypes.byref(handle)),
                   (ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p)))
        return handle

    def nvmlSystemGetDriverVersion(self) -> str:
        return self._text("nvmlSystemGetDriverVersion")

    def nvmlSystemGetNVMLVersion(self) -> str:
        return self._text("nvmlSystemGetNVMLVersion")

    def nvmlSystemGetCudaDriverVersion(self) -> int:
        return self._uint(("nvmlSystemGetCudaDriverVersion_v2",
                           "nvmlSystemGetCudaDriverVersion"), signed=True)

    def nvmlDeviceGetName(self, handle: Any) -> str:
        return self._text("nvmlDeviceGetName", handle)

    def nvmlDeviceGetUUID(self, handle: Any) -> str:
        return self._text("nvmlDeviceGetUUID", handle)

    def nvmlDeviceGetVbiosVersion(self, handle: Any) -> str:
        return self._text("nvmlDeviceGetVbiosVersion", handle)

    def nvmlDeviceGetArchitecture(self, handle: Any) -> int:
        return self._uint("nvmlDeviceGetArchitecture", handle)

    def nvmlDeviceGetVirtualizationMode(self, handle: Any) -> int:
        return self._uint("nvmlDeviceGetVirtualizationMode", handle)

    def nvmlDeviceIsMigDeviceHandle(self, handle: Any) -> int:
        return self._uint("nvmlDeviceIsMigDeviceHandle", handle)

    def nvmlDeviceGetMigMode(self, handle: Any) -> tuple[int, int]:
        current, pending = ctypes.c_uint(), ctypes.c_uint()
        self._call("nvmlDeviceGetMigMode", (handle, ctypes.byref(current), ctypes.byref(pending)),
                   (ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)))
        return int(current.value), int(pending.value)

    def nvmlDeviceGetPowerUsage(self, handle: Any) -> int:
        return self._uint("nvmlDeviceGetPowerUsage", handle)

    def nvmlDeviceGetTotalEnergyConsumption(self, handle: Any) -> int:
        return self._uint("nvmlDeviceGetTotalEnergyConsumption", handle, wide=True)

    def nvmlDeviceGetFieldValues(self, handle: Any, fields: Sequence[int]) -> list[Any]:
        values = (_FieldValue * len(fields))()
        for value, field_id in zip(values, fields):
            value.fieldId = field_id
        self._call("nvmlDeviceGetFieldValues", (handle, len(values), values),
                   (ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(_FieldValue)))
        return list(values)


def open_nvml(*, library: Any | None = None, prefer_pynvml: bool = False) -> Any:
    """Return an uninitialized binding; optional pynvml is imported only here."""
    if library is not None:
        return CtypesNvml(library)
    if prefer_pynvml:
        import pynvml
        return pynvml
    try:
        return CtypesNvml()
    except OSError:
        try:
            import pynvml
        except ImportError as exc:
            raise NvmlError("NVML library unavailable; optional pynvml is not installed") from exc
        return pynvml


def _scalar_int(value: Any) -> int:
    """Normalize Python and ctypes integral results before JSON or arithmetic."""
    return int(getattr(value, "value", value))


def _decoded(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (tuple, list)):
        return [_decoded(item) for item in value]
    if hasattr(value, "value"):
        return _scalar_int(value)
    return value


def device_inventory(nvml: Any, index: int) -> dict[str, Any]:
    """Read device identity and isolation evidence, retaining unavailable fields."""
    result: dict[str, Any] = {"index": index, "flags": []}
    try:
        handle = nvml.nvmlDeviceGetHandleByIndex(index)
    except Exception as exc:
        result["flags"].append(f"device_unavailable: {exc}")
        return result
    methods = {
        "name": "nvmlDeviceGetName", "uuid": "nvmlDeviceGetUUID",
        "architecture_id": "nvmlDeviceGetArchitecture", "vbios": "nvmlDeviceGetVbiosVersion",
        "mig_mode": "nvmlDeviceGetMigMode", "is_mig_slice": "nvmlDeviceIsMigDeviceHandle",
        "virtualization_mode": "nvmlDeviceGetVirtualizationMode",
    }
    for key, method in methods.items():
        try:
            result[key] = _decoded(getattr(nvml, method)(handle))
        except Exception as exc:
            result[key] = None
            result["flags"].append(f"{key}_unavailable: {exc}")
    result["architecture"] = ARCHITECTURES.get(result.get("architecture_id"), "unknown")
    facts = SENSOR_FACTS.get(result["architecture"])
    if facts is not None and re.search(facts["model_pattern"], result.get("name") or ""):
        result["sensor_facts"] = dict(facts)
    else:
        result["sensor_facts"] = None
        result["flags"].append("sensor_averaging_unknown")
    return result


@dataclass
class _Channel:
    kind: str
    source: str
    unit: str
    supported: bool | None = None
    times: list[int] = field(default_factory=list)
    values: list[float] = field(default_factory=list)
    brackets: list[int] = field(default_factory=list)
    raw_mj: list[int] = field(default_factory=list)
    field_timestamps_us: list[int] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    discontinuities: list[dict[str, Any]] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    duplicate_field_reads: int = 0
    window_ends: list[int | None] = field(default_factory=list)
    window_brackets: list[int | None] = field(default_factory=list)
    sample_flags: list[list[str]] = field(default_factory=list)


@dataclass
class _Device:
    index: int
    handle: Any
    inventory: dict[str, Any]
    channels: list[_Channel]
    lock: Any = field(default_factory=threading.Lock)
    thread: Any = None


class NvmlSampler:
    """Implement PowerSampler with one background worker per device.

    interval_ns is a polling choice, not a claim about sensor update rate.
    Each start/stop cycle owns fresh traces. A timed-out prior worker blocks
    restart with an explanatory empty trace until deferred cleanup finishes.
    resolution is the NVML integer mW/mJ quantum, not an accuracy guarantee.
    power_bound_w, when provided, is a caller-justified bound on instantaneous
    board power, including transients; an enforced *average* power limit alone
    does not establish such a bound.
    """

    def __init__(self, device_indices: Sequence[int] | None = None, *,
                 interval_ns: int = 10_000_000, clock_domain: str | None = None,
                 nvml: Any | None = None, library: Any | None = None,
                 power_bound_w: float | None = None, repeat_group: str | int | None = None,
                 clock_ns: Callable[[], int] = time.monotonic_ns,
                 wall_clock_ns: Callable[[], int] = time.time_ns,
                 stop_timeout_s: float = 5.0,
                 wall_clock_slew_ppm: float = 500.0) -> None:
        self.device_indices = tuple(device_indices) if device_indices is not None else None
        self.interval_ns = interval_ns
        self.clock_domain = clock_domain or f"{socket.gethostname()}:monotonic"
        self._nvml = nvml
        self._library = library
        self.power_bound_w = power_bound_w
        self.repeat_group = repeat_group
        self._clock = clock_ns
        self._wall_clock = wall_clock_ns
        self._cleanup_thread: threading.Thread | None = None
        self._stop_timeout_s = stop_timeout_s
        # Linux adjtimex MAXFREQ is 500 ppm (include/uapi/linux/timex.h;
        # man7.org/linux/man-pages/man2/adjtimex.2.html). Other clock disciplines
        # can supply their own nonnegative maximum slew rate.
        self.wall_clock_slew_ppm = wall_clock_slew_ppm
        self._event = threading.Event()
        self._devices: list[_Device] = []
        self._flags: list[str] = []
        self._initialized = False
        self._started = False
        self._result: tuple[PowerTrace, ...] | None = None

    @staticmethod
    def _channels() -> list[_Channel]:
        return [_Channel("power_usage", "nvml_power", "W"),
                _Channel("power_instant", "nvml_power", "W"),
                _Channel("power_average", "nvml_power", "W"),
                _Channel("energy", "nvml_energy", "J_cumulative")]

    def start(self) -> None:
        if self._started and self._result is None:
            self._flags.append("start_while_running")
            return
        if self._result is not None:
            active_workers = any(device.thread is not None and device.thread.is_alive()
                                 for device in self._devices)
            cleanup_active = (self._cleanup_thread is not None and
                              self._cleanup_thread.is_alive())
            if active_workers or cleanup_active:
                # Keep the old stop event set: replacing it while an old worker
                # is inside a native call could revive that worker on return.
                # A new episode receives no stale samples from the old cycle.
                self._result = (PowerTrace(
                    "nvml_power", "unavailable", self.clock_domain, (), (), "W",
                    self.interval_ns, notes=json.dumps({
                        "flags": ["restart_blocked_by_previous_workers"],
                        "reason": "previous sampling or deferred shutdown is still active"})),)
                return
            if self._initialized:
                # A failed cleanup-thread creation can leave this cycle owning
                # the native reference. All old workers are now quiescent.
                try:
                    self._nvml.nvmlShutdown()
                except Exception as exc:
                    self._flags.append(f"shutdown_failed: {exc}")
                self._initialized = False
            previous_cleanup_flags = [
                flag for flag in self._flags
                if flag.startswith(("shutdown_failed:", "deferred_shutdown_failed:"))]
            self._event = threading.Event()
            self._devices = []
            self._flags = previous_cleanup_flags
            self._initialized = False
            self._started = False
            self._cleanup_thread = None
            self._result = None
        self._started = True
        try:
            if not isinstance(self.interval_ns, int) or self.interval_ns <= 0:
                raise NvmlError("interval_ns must be a positive integer")
            if not math.isfinite(self.wall_clock_slew_ppm) or self.wall_clock_slew_ppm < 0:
                self._flags.append("invalid_wall_clock_slew_rate")
                return
            if self.power_bound_w is not None and (
                    not math.isfinite(self.power_bound_w) or self.power_bound_w <= 0):
                self._flags.append("invalid_power_bound_ignored")
                self.power_bound_w = None
            if self.repeat_group is not None and (isinstance(self.repeat_group, bool) or
                    not isinstance(self.repeat_group, (str, int))):
                self._flags.append("invalid_repeat_group_ignored")
                self.repeat_group = None
            if self._nvml is None:
                self._nvml = open_nvml(library=self._library)
            self._nvml.nvmlInit()
            self._initialized = True
            indices = self.device_indices
            if indices is None:
                indices = tuple(range(_scalar_int(self._nvml.nvmlDeviceGetCount())))
            if not indices:
                self._flags.append("no_devices")
            for index in dict.fromkeys(indices):
                inventory = device_inventory(self._nvml, index)
                try:
                    handle = self._nvml.nvmlDeviceGetHandleByIndex(index)
                except Exception as exc:
                    self._flags.append(f"gpu{index}_unavailable: {exc}")
                    handle = None
                device = _Device(index, handle, inventory, self._channels())
                self._devices.append(device)
                if handle is not None:
                    # Probe each capability before starting the worker. The
                    # probe is also retained as the first real observation.
                    self._sample(device, probe=True)
                    device.thread = threading.Thread(
                        target=self._worker, args=(device,), daemon=True,
                        name=f"joulewise-nvml-gpu{index}")
                    device.thread.start()
        except Exception as exc:
            self._flags.append(f"sampler_unavailable: {exc}")

    def _read(self, device: _Device, channel: _Channel) -> tuple[int, int | None]:
        if channel.kind == "energy":
            return _scalar_int(self._nvml.nvmlDeviceGetTotalEnergyConsumption(device.handle)), None
        if channel.kind == "power_usage":
            return _scalar_int(self._nvml.nvmlDeviceGetPowerUsage(device.handle)), None
        field_id = POWER_INSTANT_FIELD if channel.kind == "power_instant" else POWER_AVERAGE_FIELD
        value = self._nvml.nvmlDeviceGetFieldValues(device.handle, [field_id])[0]
        if value.nvmlReturn != 0:
            raise NvmlError(f"field {field_id} returned NVML status {value.nvmlReturn}")
        return _field_number(value), _scalar_int(value.timestamp)

    def _sample(self, device: _Device, *, probe: bool = False) -> None:
        for channel in device.channels:
            if channel.supported is False:
                continue
            before = self._clock()
            try:
                raw, field_timestamp = self._read(device, channel)
            except Exception as exc:
                after = self._clock()
                with device.lock:
                    if probe:
                        channel.supported = False
                    # Keep distinct failure reasons, without growing a trace
                    # indefinitely on every failed poll of a lost GPU.
                    message = str(exc)
                    if message not in channel.failures:
                        channel.failures.append(message)
                    channel.flags.append("read_failed") if "read_failed" not in channel.flags else None
                continue
            after = self._clock()
            window_end: int | None = None
            window_bracket: int | None = None
            sample_flags: list[str] = []
            if field_timestamp is not None and field_timestamp > 0:
                # Map the driver's Unix-microsecond timestamp into this host's
                # monotonic clock through an independent wall-clock bracket.
                # PowerTrace.t_ns is the sensor window end when known; the
                # query midpoint and bracket are retained separately in notes.
                map_before = self._clock()
                wall_ns = self._wall_clock()
                map_after = self._clock()
                window_end = field_timestamp*1000 + (map_before+map_after)//2 - wall_ns
                # A full microsecond covers unknown timestamp rounding mode;
                # the other term is the monotonic/Unix mapping bracket.
                window_bracket = (map_after-map_before+1)//2 + 1000
                if window_end > after + window_bracket:
                    window_end = window_bracket = None
                    sample_flags.append("field_timestamp_after_call")
                else:
                    # The mapping uses wall time now, but the field timestamp
                    # is older. Slew over that measured age also changes the
                    # offset; include both brackets in the age bound.
                    age_bound_ns = max(0, map_after-window_end) + window_bracket
                    window_bracket += math.ceil(age_bound_ns*self.wall_clock_slew_ppm/1_000_000)
            midpoint = (before + after) // 2
            # ceil(bracket/2) covers the odd-nanosecond integer midpoint.
            half_width = (after - before + 1) // 2
            with device.lock:
                channel.supported = True
                if not math.isfinite(raw) or raw < 0:
                    channel.flags.append("invalid_reading")
                    continue
                if channel.times and midpoint <= channel.times[-1]:
                    channel.flags.append("nonincreasing_call_clock")
                    continue
                if field_timestamp is not None and field_timestamp > 0:
                    if channel.field_timestamps_us and field_timestamp == channel.field_timestamps_us[-1]:
                        channel.duplicate_field_reads += 1
                        continue
                    if channel.field_timestamps_us and field_timestamp < channel.field_timestamps_us[-1]:
                        channel.flags.append("field_timestamp_reset")
                if channel.kind == "energy":
                    if channel.raw_mj and raw < channel.raw_mj[-1]:
                        # A drop over half the uint64 range has a unique
                        # shorter modular forward increment: wrap candidate.
                        # Smaller drops are reset candidates; no continuity is
                        # invented, because the cause is not identifiable.
                        kind = ("counter_wrap_candidate" if channel.raw_mj[-1] - raw > 2**63
                                else "counter_reset_or_driver_reload")
                        channel.flags.append(kind)
                        channel.discontinuities.append({
                            "index": len(channel.values), "kind": kind,
                            "before_mj": channel.raw_mj[-1], "after_mj": raw})
                    channel.raw_mj.append(raw)
                if field_timestamp is not None:
                    channel.field_timestamps_us.append(field_timestamp)
                channel.times.append(midpoint)
                channel.brackets.append(half_width)
                channel.window_ends.append(window_end)
                channel.window_brackets.append(window_bracket)
                channel.sample_flags.append(sample_flags)
                channel.flags.extend(sample_flags)
                # NVML exposes mW and mJ; dividing by 1000 converts SI prefixes.
                channel.values.append(raw / 1000.0)

    def _worker(self, device: _Device) -> None:
        try:
            while not self._event.wait(self.interval_ns / 1_000_000_000):
                self._sample(device)
        except Exception as exc:
            with device.lock:
                for channel in device.channels:
                    channel.flags.append(f"worker_failed: {exc}")

    def _trace(self, device: _Device, channel: _Channel) -> PowerTrace:
        facts = device.inventory.get("sensor_facts") or {}
        flags = list(self._flags) + list(device.inventory.get("flags", ())) + channel.flags
        is_power = channel.unit == "W"
        architecture_id = device.inventory.get("architecture_id")
        output_average = channel.kind == "power_average" or (
            channel.kind == "power_usage" and isinstance(architecture_id, int) and architecture_id >= 7
            and not (device.inventory.get("architecture") == "ampere" and facts))
        if is_power:
            flags.append("resolution_is_quantum_not_accuracy")
            if output_average:
                flags.append("output_average_not_single_window")
            if channel.kind == "power_usage":
                flags.append("sensor_update_phase_unreported")
            else:
                flags.append("driver_field_timestamp_is_wall_clock")
        # Internal arrays retain acquisition order. A single unmappable field
        # gets a query-clock proxy only for itself. Sort power observations by
        # their reported endpoint so its proxy cannot discard other known ends.
        order = sorted(range(len(channel.times)), key=lambda i: (
            channel.window_ends[i] if is_power and channel.window_ends[i] is not None
            else channel.times[i]))
        times = [channel.window_ends[i] if is_power and channel.window_ends[i] is not None
                 else channel.times[i] for i in order]
        # Equal mapped endpoints denote the same sensor instant; retain one
        # reading and record this exceptional clock-mapping collision.
        retained = [i for j, i in enumerate(order) if j == 0 or times[j] != times[j-1]]
        if len(retained) != len(order):
            flags.append("duplicate_mapped_endpoint")
        order = retained
        times = [channel.window_ends[i] if is_power and channel.window_ends[i] is not None
                 else channel.times[i] for i in order]
        period = facts.get("period_ns")
        # With no timestamp, the latest update can be one sensor period old
        # plus one poll lag. Output averages can update as slowly as their
        # one-second span. This is a declared age bound, not measured latency.
        age_bound = (max(period, 1_000_000_000 if output_average else period)
                     + self.interval_ns) if period else None
        if is_power and any(channel.window_ends[i] is None for i in order):
            flags.append("sensor_age_unknown")
            if age_bound is None:
                flags.append("sensor_age_bound_unknown")
        window_brackets = [
            channel.window_brackets[i] if channel.window_brackets[i] is not None
            else channel.brackets[i]+age_bound if age_bound is not None else None
            for i in order]
        notes = {
            "format": "joulewise.align.nvml.v1", "measurement": channel.kind,
            "supported": channel.supported, "flags": sorted(set(flags)),
            "failures": list(channel.failures),
            "timing_half_width_ns": [channel.brackets[i] for i in order],
            "query_midpoint_ns": [channel.times[i] for i in order],
            "sample_flags": [channel.sample_flags[i] for i in order],
            "timing_rule": "t_ns is mapped sensor window end when known; query midpoint otherwise",
            "unknown_sensor_age_bound_ns": age_bound if is_power else None,
            "wall_clock_slew_ppm": self.wall_clock_slew_ppm,
            "sensor_facts": facts or None,
            "output_averaging_window_ns": 1_000_000_000 if output_average else None,
            "duplicate_field_reads": channel.duplicate_field_reads,
            "field_timestamps_us": ([channel.field_timestamps_us[i] for i in order]
                                    if channel.field_timestamps_us else []),
            "counter_discontinuities": list(channel.discontinuities),
            "raw_energy_mj": list(channel.raw_mj) if not is_power else None,
            "power_bound_w": self.power_bound_w,
            "repeat_group": self.repeat_group,
            "device": device.inventory,
        }
        if is_power:
            notes["window_end_ns"] = [channel.window_ends[i] for i in order]
            notes["window_timing_half_width_ns"] = window_brackets
            notes["window_clock_mapping"] = (
                "driver Unix microseconds mapped by bracketed time.time_ns; "
                "rounding plus mapping bracket plus slew over timestamp age; "
                "None endpoints use query midpoint with period-plus-poll age bound")
        return PowerTrace(
            source=channel.source, channel=f"gpu{device.index}:{channel.kind}",
            clock_domain=self.clock_domain, t_ns=tuple(times),
            values=tuple(channel.values[i] for i in order), unit=channel.unit,
            nominal_interval_ns=self.interval_ns,
            averaging_window_ns=(1_000_000_000 if output_average and facts else
                                 facts.get("averaging_window_ns") if is_power else None),
            # Disjoint slices inside a one-second output cannot be represented
            # as one duty window; None plus the output flag avoids that claim.
            duty_fraction=facts.get("duty_fraction") if is_power and not output_average else None,
            resolution=0.001,  # Integer mW or mJ NVML API quantum, converted to SI.
            notes=json.dumps(notes, sort_keys=True, allow_nan=False))

    def _shutdown_after_workers(self, workers: Sequence[threading.Thread]) -> None:
        for worker in workers:
            worker.join()
        try:
            self._nvml.nvmlShutdown()
        except Exception as exc:
            self._flags.append(f"deferred_shutdown_failed: {exc}")

    def stop(self) -> tuple[PowerTrace, ...]:
        """Return measurements or explanatory empty traces; never raise on failure."""
        if self._result is not None:
            return self._result
        self._event.set()
        try:
            if not self._started:
                self._flags.append("not_started")
            for device in self._devices:
                if device.thread is not None:
                    try:
                        device.thread.join(timeout=self._stop_timeout_s)
                    except RuntimeError as exc:
                        # Thread.start() can fail after NVML initialization.
                        # Joining that unstarted thread must not bypass shutdown.
                        self._flags.append(f"gpu{device.index}_worker_join_failed: {exc}")
                    if device.thread.is_alive():
                        self._flags.append(f"gpu{device.index}_worker_stop_timeout")
            if self._initialized:
                active_workers = [device.thread for device in self._devices
                                  if device.thread is not None and device.thread.is_alive()]
                if active_workers:
                    # No shutdown may race an in-flight native call. A separate
                    # cleanup owner waits; it never samples another device.
                    self._flags.append("shutdown_deferred_worker_active")
                    self._cleanup_thread = threading.Thread(
                        target=self._shutdown_after_workers, args=(active_workers,),
                        daemon=True, name="joulewise-nvml-cleanup")
                    self._cleanup_thread.start()
                else:
                    try:
                        self._nvml.nvmlShutdown()
                    except Exception as exc:
                        self._flags.append(f"shutdown_failed: {exc}")
                self._initialized = False
            if not self._devices:
                self._devices.append(_Device(
                    0, None, {"flags": ["no_device_measurement"]}, self._channels()))
            traces = []
            for device in self._devices:
                with device.lock:
                    traces.extend(self._trace(device, channel) for channel in device.channels)
            self._result = tuple(traces)
        except Exception as exc:
            # Even a malformed injected backend or clock cannot turn stop()
            # into a runner crash. No fabricated samples escape this fallback.
            self._result = (PowerTrace(
                "nvml_power", "unavailable", self.clock_domain, (), (), "W",
                self.interval_ns, notes=json.dumps({
                    "flags": self._flags + ["stop_failed"], "reason": str(exc)})),)
        return self._result


__all__ = ["NvmlSampler", "CtypesNvml", "NvmlError", "open_nvml",
           "device_inventory", "SENSOR_FACTS", "POWER_INSTANT_FIELD", "POWER_AVERAGE_FIELD"]
