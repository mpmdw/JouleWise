"""Native plist and anchor evidence pass through the production Apple sampler."""

from __future__ import annotations

import json
import math
import plistlib
import unittest
from datetime import datetime, timezone
from fractions import Fraction
from unittest.mock import patch

from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
from joulewise.align.apple.sampler import (
    ApplePowerSampler, HAZARD_UNJUDGED, POST_WINDOW_DWELL_S, power_records,
    stamp_mapping, seconds_ns, _conversion_error_ns, _stamp_record, _restore_stamp,
)
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

    def sleep(self, seconds: float) -> None:
        self.dwell_s = seconds


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
        self.assertEqual(sampler.clock.dwell_s, POST_WINDOW_DWELL_S)  # exact requested policy constant
        for trace in traces:
            self.assertIn(HAZARD_UNJUDGED, json.loads(trace.notes)["flags"])
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
        # Support width subtracts two epoch conversions; each input also
        # costs half an ulp in seconds. This is below 1% of the anchor bound.
        epoch_s = traces[0].t_ns[1] / 1e9
        representation_ns = math.ceil(2 * (
            _conversion_error_ns(epoch_s) + math.ulp(epoch_s) * 1e9 / 2
        ))
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
        self.assertIn(HAZARD_UNJUDGED, json.loads(traces[0].notes)["flags"])

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

    def test_epoch_conversion_pricing_and_bounded_span_is_not_counted_twice(self) -> None:
        # Near 1.8e18 ns the product spacing is 256 ns, so its half-width
        # must be 128 ns rather than the old unphysical 1 ns.
        stamp = ClockStamp(1_800_000_000.125, 1000.0, 1000.002, 1e-9, 1e-9)
        exact_ns = Fraction.from_float(stamp.epoch_s) * 1_000_000_000
        conversion_error = abs(Fraction(seconds_ns(stamp.epoch_s)) - exact_ns)
        self.assertLessEqual(conversion_error, Fraction(_conversion_error_ns(stamp.epoch_s)))
        # The exact-rational oracle is above the old 1 ns representation
        # allowance, so a return to that under-pricing fails this control.
        self.assertGreater(conversion_error, 1)
        restored = _restore_stamp(_stamp_record(stamp))
        self.assertGreaterEqual(restored.wall_resolution_s * 1e9,
                                _conversion_error_ns(stamp.epoch_s))
        bracket, _ = stamp_mapping((stamp,), episode_domain="test")
        self.assertGreaterEqual(
            bracket.uncertainty_ns,
            _conversion_error_ns(stamp.epoch_s) + _conversion_error_ns(-stamp.epoch_s),
        )  # trace and epoch-scale offset both undergo ns-product rounding.
        lower = stamp.epoch_s - stamp.monotonic_after_s
        upper = stamp.epoch_s - stamp.monotonic_before_s
        bound_s = 0.010  # world parameter: 10 ms calibrated bound containing a 2 ms bridge.
        mapping, _ = stamp_mapping((stamp,), episode_domain="test", evidence={"clock_anchor": {
            "status": "bounded", "method": "synthetic",
            "wall_minus_monotonic_lower_s": lower,
            "wall_minus_monotonic_upper_s": upper,
            "effective_clock_anchor_bound_s": bound_s,
        }})
        self.assertGreaterEqual(mapping.uncertainty_ns, math.ceil(bound_s * 1e9))
        self.assertLess(mapping.uncertainty_ns, math.ceil((bound_s + (upper-lower)/2) * 1e9))
        # Adding half the already-covered 2 ms span would violate this bar.
