"""Exercise the real ctypes binding and sampler against a driver-shaped stub."""

from __future__ import annotations

import ctypes
import importlib.util
import json
import math
import threading
import time
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.align.interfaces import PowerSampler
from joulewise.align.power.nvml import (
    CtypesNvml, NvmlSampler, POWER_AVERAGE_FIELD, POWER_INSTANT_FIELD, open_nvml,
)
from joulewise.align.records import PowerTrace, from_json, to_json


class FakeNvmlLibrary:
    """C ABI-shaped fake: output pointers, status codes and field structs.

    Default idle/load levels (50/250 W) model a whole accelerator. The 200 W
    load contrast dwarfs the 0.2 W idle ripple and the 0.001 W API quantum.
    It is intentionally absent in the no-movement control.
    """

    def __init__(self, *, count: int = 1, architecture: int = 7,
                 name: str = "NVIDIA A100-SXM4-40GB",
                 state_file: Path | None = None, moves: bool = True) -> None:
        self.count = count
        self.architecture = architecture
        self.name = name
        self.state_file = state_file
        self.moves = moves
        self.virtualization = 0
        self.mig_slice = 0
        self.mig_mode = (0, 0)
        self.init_status = 0
        self.shutdown_status = 0
        self.unsupported_fields: set[int] = set()
        self.energy_supported = True
        self.constant_field_timestamp: int | None = None
        self.energy_sequence: list[int] | None = None
        self.power_calls = 0
        self.energy_calls = 0
        self.field_calls = 0
        self.init_calls = 0
        self.shutdown_calls = 0
        self.seen_devices: set[int] = set()
        self.sampled = threading.Event()
        self._lock = threading.Lock()
        self._started = time.monotonic_ns()

    @staticmethod
    def _put(pointer: object, scalar: type, value: int) -> None:
        ctypes.cast(pointer, ctypes.POINTER(scalar))[0] = value

    @staticmethod
    def _string(buffer: object, text: str) -> int:
        buffer.value = text.encode()
        return 0

    def nvmlInit_v2(self) -> int:
        self.init_calls += 1
        return self.init_status

    def nvmlShutdown(self) -> int:
        self.shutdown_calls += 1
        return self.shutdown_status

    def nvmlDeviceGetCount_v2(self, output: object) -> int:
        self._put(output, ctypes.c_uint, self.count)
        return 0

    def nvmlDeviceGetHandleByIndex_v2(self, index: int, output: object) -> int:
        if not 0 <= index < self.count:
            return 2  # NVML_ERROR_INVALID_ARGUMENT.
        self._put(output, ctypes.c_void_p, index + 1)
        return 0

    def nvmlSystemGetDriverVersion(self, buffer: object, length: int) -> int:
        return self._string(buffer, "550.54.15")

    def nvmlSystemGetNVMLVersion(self, buffer: object, length: int) -> int:
        return self._string(buffer, "12.550.54")

    def nvmlSystemGetCudaDriverVersion_v2(self, output: object) -> int:
        self._put(output, ctypes.c_int, 12040)  # NVML encoding: CUDA driver API 12.4.
        return 0

    def nvmlDeviceGetName(self, handle: object, buffer: object, length: int) -> int:
        return self._string(buffer, self.name)

    def nvmlDeviceGetUUID(self, handle: object, buffer: object, length: int) -> int:
        prefix = "MIG-" if self.mig_slice else "GPU-"
        return self._string(buffer, prefix + f"synthetic-{ctypes.cast(handle, ctypes.c_void_p).value}")

    def nvmlDeviceGetVbiosVersion(self, handle: object, buffer: object, length: int) -> int:
        return self._string(buffer, "92.00.45.00.03")

    def nvmlDeviceGetArchitecture(self, handle: object, output: object) -> int:
        self._put(output, ctypes.c_uint, self.architecture)
        return 0

    def nvmlDeviceGetVirtualizationMode(self, handle: object, output: object) -> int:
        self._put(output, ctypes.c_uint, self.virtualization)
        return 0

    def nvmlDeviceIsMigDeviceHandle(self, handle: object, output: object) -> int:
        self._put(output, ctypes.c_uint, self.mig_slice)
        return 0

    def nvmlDeviceGetMigMode(self, handle: object, current: object, pending: object) -> int:
        self._put(current, ctypes.c_uint, self.mig_mode[0])
        self._put(pending, ctypes.c_uint, self.mig_mode[1])
        return 0

    def _power_mw(self, count: int) -> int:
        active = self.state_file is not None and self.state_file.exists()
        baseline = 250_000 if active and self.moves else 50_000
        return baseline + (-200 if count % 2 else 200)

    def nvmlDeviceGetPowerUsage(self, handle: object, output: object) -> int:
        with self._lock:
            self.power_calls += 1
            self.seen_devices.add(ctypes.cast(handle, ctypes.c_void_p).value - 1)
            value = self._power_mw(self.power_calls)
            self._put(output, ctypes.c_uint, value)
            self.sampled.set()
        return 0

    def nvmlDeviceGetTotalEnergyConsumption(self, handle: object, output: object) -> int:
        with self._lock:
            if not self.energy_supported:
                return 3  # NVML_ERROR_NOT_SUPPORTED.
            index = self.energy_calls
            self.energy_calls += 1
            if self.energy_sequence:
                value = self.energy_sequence[min(index, len(self.energy_sequence)-1)]
            else:
                elapsed_s = (time.monotonic_ns() - self._started) / 1_000_000_000
                value = 100_000 + int(50_000 * elapsed_s)  # mW*s = mJ.
            self._put(output, ctypes.c_ulonglong, value)
        return 0

    def nvmlDeviceGetFieldValues(self, handle: object, count: int, values: object) -> int:
        with self._lock:
            self.field_calls += 1
            for index in range(count):
                value = values[index]
                value.nvmlReturn = 3 if value.fieldId in self.unsupported_fields else 0
                value.valueType = 1  # NVML_VALUE_TYPE_UNSIGNED_INT.
                value.value.uiVal = self._power_mw(self.field_calls)
                value.timestamp = (self.constant_field_timestamp if
                    self.constant_field_timestamp is not None else time.time_ns() // 1000)
                value.latencyUsec = 10
        return 0


def collect(library: FakeNvmlLibrary, *, samples: int = 4, **kwargs: object) -> tuple[PowerTrace, ...]:
    sampler = NvmlSampler(library=library, interval_ns=1_000_000, **kwargs)
    sampler.start()
    # A deadline is an operational deadlock guard. The test waits for an
    # integer number of actual driver observations, not a timing tolerance.
    deadline = time.monotonic() + 2.0
    while library.power_calls < samples and time.monotonic() < deadline:
        library.sampled.wait(timeout=0.01)
        library.sampled.clear()
    return sampler.stop()


class NvmlSamplerTests(unittest.TestCase):
    def test_ctypes_binding_inventory_and_si_conversion(self) -> None:
        library = FakeNvmlLibrary()
        binding = CtypesNvml(library)
        binding.nvmlInit()
        handle = binding.nvmlDeviceGetHandleByIndex(0)
        self.assertEqual(binding.nvmlDeviceGetName(handle), library.name)
        self.assertEqual(binding.nvmlSystemGetCudaDriverVersion(), 12040)
        self.assertEqual(binding.nvmlDeviceGetArchitecture(handle), 7)
        self.assertEqual(binding.nvmlDeviceGetMigMode(handle), (0, 0))
        fields = binding.nvmlDeviceGetFieldValues(handle, [POWER_INSTANT_FIELD, POWER_AVERAGE_FIELD])
        self.assertEqual([value.fieldId for value in fields], [186, 185])
        traces = collect(library)
        self.assertEqual(len(traces), 4)
        power = next(trace for trace in traces if trace.channel.endswith(":power_usage"))
        self.assertTrue(power.values)
        # Half an mW is the rounded-power quantum; a 1e-6 relative
        # conversion bar is smaller and is the brief's no-uncertainty bar.
        self.assertTrue(math.isclose(power.values[0], 49.8, rel_tol=1e-6))
        self.assertEqual(power.averaging_window_ns, 25_000_000)
        self.assertEqual(power.duty_fraction, 0.25)
        self.assertEqual(json.loads(power.notes)["sensor_facts"]["period_ns"], 100_000_000)
        self.assertEqual(from_json(PowerTrace, to_json(power)), power)
        energy = next(trace for trace in traces if trace.unit == "J_cumulative")
        metadata = json.loads(energy.notes)
        for raw, value in zip(metadata["raw_energy_mj"], energy.values):
            self.assertTrue(math.isclose(value, raw / 1000, rel_tol=1e-6))

    def test_protocol_thread_per_device_and_stop_idempotence(self) -> None:
        library = FakeNvmlLibrary(count=2)
        sampler = NvmlSampler(library=library, interval_ns=1_000_000)
        self.assertIsInstance(sampler, PowerSampler)
        sampler.start()
        traces = sampler.stop()
        self.assertEqual(library.seen_devices, {0, 1})
        self.assertEqual(len(sampler._devices), 2)
        self.assertTrue(all(device.thread is not None for device in sampler._devices))
        self.assertTrue(all(not device.thread.is_alive() for device in sampler._devices))
        self.assertEqual(len(traces), 8)
        self.assertIs(sampler.stop(), traces)  # Cached result identity is the property.
        self.assertEqual(library.shutdown_calls, 1)

    def test_reused_sampler_returns_fresh_episode_traces(self) -> None:
        library = FakeNvmlLibrary()
        sampler = NvmlSampler(library=library, interval_ns=1_000_000)
        sampler.start()
        first = sampler.stop()
        first_json = tuple(to_json(trace) for trace in first)
        with mock.patch.object(library, "_power_mw", return_value=250_000):
            sampler.start()
            second = sampler.stop()
        self.assertIsNot(second, first)
        self.assertIs(sampler.stop(), second)
        self.assertEqual(library.init_calls, 2)
        self.assertEqual(library.shutdown_calls, 2)
        self.assertEqual(tuple(to_json(trace) for trace in first), first_json)
        for earlier, later in zip(first, second):
            self.assertTrue(later.values)
            self.assertGreater(min(later.t_ns), max(earlier.t_ns))
            if later.unit == "W":
                # 1e-6 relative is the specified agreement bar when no
                # measurement uncertainty is asserted by this exact ABI input.
                self.assertTrue(all(math.isclose(value, 250.0, rel_tol=1e-6)
                                    for value in later.values))
                # Declared 200 W contrast minus 0.2 W idle ripple and
                # two half-quantum endpoints gives this detectable lower bar.
                contrast_bar_w = 250.0-50.0-0.2-later.resolution
                self.assertGreater(
                    math.fsum(later.values)/len(later.values) -
                    math.fsum(earlier.values)/len(earlier.values), contrast_bar_w)

    def test_thread_start_failure_keeps_native_cleanup_balanced(self) -> None:
        library = FakeNvmlLibrary()
        sampler = NvmlSampler(library=library, interval_ns=1_000_000)
        with mock.patch.object(threading.Thread, "start", side_effect=RuntimeError(
                "synthetic worker creation failure")):
            sampler.start()
        first = sampler.stop()
        self.assertTrue(any(trace.values for trace in first))
        self.assertTrue(any("worker_join_failed" in flag
                            for trace in first for flag in json.loads(trace.notes)["flags"]))
        self.assertEqual(library.init_calls, 1)
        self.assertEqual(library.shutdown_calls, 1)
        sampler.start()
        second = sampler.stop()
        self.assertTrue(any(trace.values for trace in second))
        self.assertIsNot(first, second)
        self.assertEqual(library.init_calls, 2)
        self.assertEqual(library.shutdown_calls, 2)

    def test_call_midpoints_and_odd_bracket_rounding(self) -> None:
        lock = threading.Lock()
        ticks = 0

        def clock() -> int:
            nonlocal ticks
            with lock:
                ticks += 2001
                return ticks

        traces = collect(FakeNvmlLibrary(), clock_ns=clock)
        for trace in traces:
            metadata = json.loads(trace.notes)
            # Integer midpoint ceil(2001/2)=1001 ns exactly bounds the call.
            self.assertTrue(all(value == 1001 for value in metadata["timing_half_width_ns"]))
            self.assertTrue(all(b > a for a, b in zip(trace.t_ns, trace.t_ns[1:])))

    def test_capability_failures_are_empty_explanatory_traces(self) -> None:
        library = FakeNvmlLibrary()
        library.unsupported_fields = {POWER_AVERAGE_FIELD}
        library.energy_supported = False
        traces = collect(library)
        unsupported = [trace for trace in traces if trace.channel.endswith((":power_average", ":energy"))]
        self.assertEqual(len(unsupported), 2)
        for trace in unsupported:
            self.assertFalse(trace.values)
            self.assertFalse(json.loads(trace.notes)["supported"])
            self.assertTrue(json.loads(trace.notes)["failures"])
        self.assertTrue(next(trace for trace in traces if trace.channel.endswith(":power_usage")).values)

    def test_unknown_architecture_has_no_guessed_sensor_facts(self) -> None:
        traces = collect(FakeNvmlLibrary(architecture=0xffffffff, name="Synthetic future GPU"))
        for trace in traces:
            self.assertIsNone(trace.averaging_window_ns)
            self.assertIsNone(trace.duty_fraction)
            self.assertIn("sensor_averaging_unknown", json.loads(trace.notes)["flags"])

    def test_hopper_legacy_and_average_are_not_single_windows(self) -> None:
        traces = collect(FakeNvmlLibrary(architecture=9, name="NVIDIA H100 80GB HBM3"))
        instant = next(trace for trace in traces if trace.channel.endswith(":power_instant"))
        self.assertEqual(instant.averaging_window_ns, 25_000_000)
        self.assertNotIn("output_average_not_single_window", json.loads(instant.notes)["flags"])
        for trace in traces:
            if trace.channel.endswith((":power_usage", ":power_average")):
                notes = json.loads(trace.notes)
                self.assertIn("output_average_not_single_window", notes["flags"])
                self.assertEqual(notes["output_averaging_window_ns"], 1_000_000_000)

    def test_cached_field_values_do_not_fabricate_new_measurements(self) -> None:
        library = FakeNvmlLibrary()
        library.constant_field_timestamp = 1_000_000
        traces = collect(library)
        for trace in traces:
            if trace.channel.endswith((":power_instant", ":power_average")):
                self.assertEqual(len(trace.values), 1)
                self.assertGreater(json.loads(trace.notes)["duplicate_field_reads"], 0)

    def test_counter_reset_and_wrap_candidates_preserve_raw_readings(self) -> None:
        for sequence, flag in (
            ([100_000, 100_050, 4, 50], "counter_reset_or_driver_reload"),
            ([2**64 - 100, 2**64 - 50, 4, 50], "counter_wrap_candidate"),
        ):
            with self.subTest(flag=flag):
                library = FakeNvmlLibrary()
                library.energy_sequence = sequence
                traces = collect(library)
                trace = next(value for value in traces if value.unit == "J_cumulative")
                notes = json.loads(trace.notes)
                self.assertIn(flag, notes["flags"])
                self.assertEqual(notes["raw_energy_mj"][:4], sequence)
                self.assertEqual(notes["counter_discontinuities"][0]["index"], 2)
                # uint64 mJ near wrap cannot retain every mJ in a float J;
                # the exact raw integers above are the required evidence.
                self.assertGreater(trace.values[1], trace.values[2])

    def test_start_stop_failures_do_not_raise(self) -> None:
        for started in (False, True):
            library = FakeNvmlLibrary()
            library.init_status = 9
            sampler = NvmlSampler(library=library)
            if started:
                sampler.start()
            traces = sampler.stop()
            self.assertTrue(traces)
            self.assertTrue(all(not trace.values for trace in traces))
            self.assertTrue(all(json.loads(trace.notes)["flags"] for trace in traces))
        library = FakeNvmlLibrary()
        library.shutdown_status = 9
        self.assertTrue(any("shutdown_failed" in flag for trace in collect(library)
                            for flag in json.loads(trace.notes)["flags"]))

    def test_nonincreasing_clock_is_flagged_without_invented_timestamps(self) -> None:
        traces = collect(FakeNvmlLibrary(), clock_ns=lambda: 100)
        for trace in traces:
            self.assertEqual(trace.t_ns, (100,))
            self.assertIn("nonincreasing_call_clock", json.loads(trace.notes)["flags"])

    def test_missing_architecture_entry_point_preserves_collected_channels(self) -> None:
        library = FakeNvmlLibrary()
        library.nvmlDeviceGetArchitecture = None
        traces = collect(library)
        self.assertEqual(len(traces), 4)
        self.assertTrue(all(trace.values for trace in traces))
        self.assertTrue(all("sensor_averaging_unknown" in json.loads(trace.notes)["flags"]
                            for trace in traces))

    def test_driver_timestamp_mapping_and_declared_repeat_label(self) -> None:
        library = FakeNvmlLibrary()
        library.constant_field_timestamp = time.time_ns()//1000-300_000
        traces = collect(library, repeat_group="phase-zero")
        for trace in traces:
            notes = json.loads(trace.notes)
            self.assertEqual(notes["repeat_group"], "phase-zero")
            if trace.channel.endswith((":power_instant", ":power_average")):
                self.assertEqual(len(notes["window_end_ns"]), len(trace.values))
                # The declared 300 ms sensor age exceeds one 100 ms period,
                # and must remain visible rather than becoming query latency.
                self.assertLess(notes["window_end_ns"][0], trace.t_ns[0]-100_000_000)
                self.assertGreaterEqual(notes["window_timing_half_width_ns"][0], 1000)

    def test_native_worker_timeout_defers_shutdown_until_call_returns(self) -> None:
        class BlockingLibrary(FakeNvmlLibrary):
            def __init__(self) -> None:
                super().__init__()
                self.entered, self.release = threading.Event(), threading.Event()

            def nvmlDeviceGetPowerUsage(self, handle: object, output: object) -> int:
                if self.power_calls:
                    self.entered.set()
                    self.release.wait()
                return super().nvmlDeviceGetPowerUsage(handle, output)

        library = BlockingLibrary()
        sampler = NvmlSampler(library=library, interval_ns=1_000_000, stop_timeout_s=0)
        try:
            sampler.start()
            self.assertTrue(library.entered.wait(timeout=2))
            traces = sampler.stop()
            self.assertEqual(library.shutdown_calls, 0)
            self.assertTrue(any("shutdown_deferred_worker_active" in json.loads(trace.notes)["flags"]
                                for trace in traces))
            sampler.start()
            blocked = sampler.stop()
            self.assertTrue(all(not trace.values for trace in blocked))
            self.assertTrue(all("restart_blocked_by_previous_workers" in
                                json.loads(trace.notes)["flags"] for trace in blocked))
            self.assertIsNot(blocked, traces)
            self.assertEqual(library.init_calls, 1)
            self.assertTrue(sampler._event.is_set())
        finally:
            library.release.set()
            if sampler._cleanup_thread is not None:
                sampler._cleanup_thread.join(timeout=2)
        self.assertEqual(library.shutdown_calls, 1)
        sampler._stop_timeout_s = 2.0  # Operational join guard, not a measured tolerance.
        sampler.start()
        resumed = sampler.stop()
        self.assertTrue(any(trace.values for trace in resumed))
        self.assertEqual(library.init_calls, 2)
        self.assertEqual(library.shutdown_calls, 2)

    def test_restart_releases_reference_after_cleanup_thread_creation_failure(self) -> None:
        class BlockingLibrary(FakeNvmlLibrary):
            def __init__(self) -> None:
                super().__init__()
                self.entered, self.release = threading.Event(), threading.Event()

            def nvmlDeviceGetPowerUsage(self, handle: object, output: object) -> int:
                if self.power_calls:
                    self.entered.set()
                    self.release.wait()
                return super().nvmlDeviceGetPowerUsage(handle, output)

        library = BlockingLibrary()
        sampler = NvmlSampler(library=library, interval_ns=1_000_000, stop_timeout_s=0)
        try:
            sampler.start()
            self.assertTrue(library.entered.wait(timeout=2))
            with mock.patch.object(threading.Thread, "start", side_effect=RuntimeError(
                    "synthetic cleanup owner creation failure")):
                first = sampler.stop()
            self.assertTrue(sampler._initialized)
            self.assertEqual(library.shutdown_calls, 0)
            self.assertTrue(any("stop_failed" in json.loads(trace.notes)["flags"]
                                for trace in first))
        finally:
            library.release.set()
            for device in sampler._devices:
                device.thread.join(timeout=2)
        sampler._stop_timeout_s = 2.0  # Operational join guard.
        sampler.start()
        second = sampler.stop()
        self.assertTrue(any(trace.values for trace in second))
        self.assertEqual(library.init_calls, 2)
        self.assertEqual(library.shutdown_calls, 2)
        self.assertIsNot(first, second)

    @unittest.skipUnless(importlib.util.find_spec("pynvml") is not None,
                         "optional nvidia-ml-py is not installed; ctypes path is tested")
    def test_optional_pynvml_uses_the_same_sampler_path(self) -> None:
        import pynvml
        from joulewise.align.power import preflight
        library = FakeNvmlLibrary()

        def resolve(name: str) -> object:
            # Only the C ABI is replaced. All pynvml Python function bodies,
            # including its c_uint MIG return, run without replacements.
            if name == "nvmlInitWithFlags":
                return lambda flags: library.nvmlInit_v2()
            if name == "nvmlDeviceGetName_v2":
                return library.nvmlDeviceGetName
            return getattr(library, name)

        with mock.patch.object(pynvml, "_nvmlGetFunctionPointer", side_effect=resolve):
            self.assertIs(open_nvml(prefer_pynvml=True), pynvml)
            sampler = NvmlSampler(nvml=pynvml)
            sampler.start()
            traces = sampler.stop()
            self.assertEqual(len(traces), 4)
            self.assertTrue(all(trace.values for trace in traces))
            self.assertTrue(all("stop_failed" not in json.loads(trace.notes)["flags"]
                                for trace in traces))
            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory)/"preflight.json"
                # A zero-span CLI world checks native scalar serialization;
                # the load/no-load worlds separately test movement physics.
                with mock.patch.object(preflight, "open_nvml", return_value=pynvml), \\
                        mock.patch.object(preflight.importlib.util, "find_spec", return_value=None):
                    self.assertEqual(preflight.main([
                        "--out", str(output), "--idle-seconds", "0",
                        "--load-seconds", "0", "--recovery-seconds", "0"]), 0)
                report = json.loads(output.read_text())
                self.assertIs(type(report["devices"][0]["is_mig_slice"]), int)
                self.assertTrue(all(row["sample_count"] > 0 for row in report["capabilities"]))


if __name__ == "__main__":
    unittest.main()
