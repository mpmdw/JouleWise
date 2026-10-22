"""Native plist and anchor evidence pass through the production Apple sampler."""

from __future__ import annotations

import json
import math
import plistlib
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
from joulewise.align.apple.sampler import ApplePowerSampler, power_records
from joulewise.align.interfaces import PowerSampler
from joulewise.clock import ClockStamp
from joulewise.interfaces import AdapterResult, PowerSample
from joulewise.schemas import FailureReason
from tests.align.test_apple_campaign import base_config
from tests.test_uncertainty_evidence import (
    EPOCH_SCALE_ANCHOR_NS, epoch_scale_stamps,
)


class CaptureClock:
    """Use recorded bracket stamps while the collector boundary is injected."""

    def __init__(self, stamps: list[ClockStamp]) -> None:
        self.stamps = list(stamps)

    def stamp(self) -> ClockStamp:
        return self.stamps.pop(0)


def native_stream(*, delta: bool = True) -> bytes:
    documents = []
    # Sixty seconds at the production 100 ms cadence gives the rate-aware
    # estimator its required 60 s baseline; 601 endpoints include both ends.
    for index in range(601):
        elapsed_ns = 999_000_000 if index == 0 else 100_000_000
        endpoint_ns = EPOCH_SCALE_ANCHOR_NS + index * 100_000_000
        native_second = endpoint_ns // 1_000_000_000
        # 0.2 W oscillations model quiet-machine rail noise, represented in
        # integer mW. This is a world parameter, not an acceptance threshold.
        cpu_mw = 4000 + round(200 * math.sin(index))
        gpu_mw = 28000 + round(200 * math.cos(index))
        ane_mw = 300
        processor = {
            "cpu_power": cpu_mw, "gpu_power": gpu_mw, "ane_power": ane_mw,
            "cpu_energy": round(cpu_mw * elapsed_ns / 1e9),
            "gpu_energy": round(gpu_mw * elapsed_ns / 1e9),
            "ane_energy": round(ane_mw * elapsed_ns / 1e9),
        }
        documents.append({
            "timestamp": datetime.fromtimestamp(native_second, timezone.utc).replace(tzinfo=None),
            "elapsed_ns": elapsed_ns, "processor": processor,
            "is_delta": delta, "thermal_pressure": "Nominal",
        })
    return b"\0".join(plistlib.dumps(document) for document in documents)


class AppleSamplerTests(unittest.TestCase):
    def capture(self, *, delta: bool = True):
        stamps = epoch_scale_stamps()
        clock = CaptureClock([
            stamps["sampling_started"], stamps["sampling_stopped"], stamps["post_parse"],
        ])
        adapter = PowermetricsTelemetryAdapter(clock)
        adapter._pre_spawn_stamp = stamps["pre_spawn"]
        adapter._first_parse_stamp = stamps["first_parse"]
        sampler = ApplePowerSampler(
            base_config(), clock, episode_domain="synthetic.monotonic", adapter=adapter
        )
        with (
            patch.object(adapter, "start_sampling", return_value=AdapterResult(ok=True)),
            patch.object(adapter, "_drain_until_stop_bracket", return_value=None),
            patch.object(adapter, "_take_measured_capture", return_value=(native_stream(delta=delta), None)),
        ):
            sampler.start()
            traces = sampler.stop()
        return sampler, traces

    def test_native_parser_and_current_anchor_are_reused(self) -> None:
        sampler, traces = self.capture()
        self.assertIsInstance(sampler, PowerSampler)
        self.assertEqual(len(traces), 3)
        self.assertEqual({trace.channel for trace in traces}, {"cpu_power", "gpu_power", "ane_power"})
        self.assertEqual({len(trace.t_ns) for trace in traces}, {601})
        anchor = sampler.uncertainty_evidence["clock_anchor"]
        self.assertEqual(anchor["status"], "bounded")
        mapping = sampler.clock_mappings[0]
        expected_first_monotonic_ns = 101 * 1_000_000_000
        # Compare the known physical endpoint to the mapped estimate using
        # the returned half-width itself, including float representation.
        self.assertLessEqual(
            abs(traces[0].t_ns[0] + mapping.offset_ns - expected_first_monotonic_ns),
            mapping.uncertainty_ns,
        )
        self.assertGreaterEqual(
            mapping.uncertainty_ns,
            math.ceil(anchor["effective_clock_anchor_bound_s"] * 1e9),
        )  # never drop any term of the adapter's physical bound.
        supports = json.loads(traces[0].notes)["sample_support_ns"]
        # Two float epoch endpoints each cost at most an ulp plus ns rounding.
        # This representation bar is below 1% of the millisecond anchor bound.
        representation_ns = 2 * math.ceil(math.ulp(traces[0].t_ns[1] / 1e9) * 1e9) + 2
        self.assertLessEqual(abs(supports[1][1] - supports[1][0] - 100_000_000), representation_ns)
        self.assertIsNone(traces[0].averaging_window_ns)  # first native support is 999 ms
        self.assertIn("variable_averaging_support:cpu_power", sampler.flags)

    def test_unresolved_anchor_keeps_trace_and_flags(self) -> None:
        sampler, traces = self.capture(delta=False)
        self.assertIn("clock_anchor_unresolved", sampler.flags)
        self.assertEqual({len(trace.t_ns) for trace in traces}, {601})
        self.assertEqual(sampler.uncertainty_evidence["clock_anchor"]["status"], "unknown")

    def test_permission_denied_is_a_noted_empty_trace(self) -> None:
        stamps = epoch_scale_stamps()
        clock = CaptureClock([stamps["sampling_started"], stamps["sampling_stopped"]])
        adapter = PowermetricsTelemetryAdapter(clock)
        sampler = ApplePowerSampler(
            base_config(), clock, episode_domain="synthetic.monotonic", adapter=adapter
        )
        with patch.object(adapter, "start_sampling", return_value=AdapterResult(
            ok=False, failure_reason=FailureReason.PERMISSION_DENIED, message="synthetic denial"
        )):
            sampler.start()
            traces = sampler.stop()
        self.assertEqual(len(traces), 1)
        self.assertEqual(traces[0].t_ns, ())
        self.assertIn("synthetic denial", traces[0].notes)

    def test_bad_sample_is_flagged_without_removing_other_channels(self) -> None:
        traces, flags = power_records([
            PowerSample(1.0, 4.0, "powermetrics", "cpu_power", 0.9, 1.0),
            PowerSample(1.1, float("nan"), "powermetrics", "cpu_power", 1.0, 1.1),
            PowerSample(1.2, 4.0, "powermetrics", "cpu_power", 1.1, 1.2),
            PowerSample(1.0, 28.0, "powermetrics", "gpu_power", 0.9, 1.0),
        ], nominal_interval_ns=100_000_000)
        self.assertIn("nonfinite_power:cpu_power", flags)
        self.assertEqual(len(traces), 2)
        self.assertEqual(len(traces[0].values), 2)
