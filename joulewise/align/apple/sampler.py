"""Bridge the existing Apple telemetry adapter into alignment power records.

The adapter owns capture, parsing and native-second clock anchoring. This
module only changes representation. Every mean stays stamped at its window
end; sample_support_ns retains the native support, including variable widths.
"""

from __future__ import annotations

import json
import math
from dataclasses import replace
from collections import defaultdict
from typing import Any, Mapping, Sequence

from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
from joulewise.align.records import ClockMapping, PowerTrace
from joulewise.clock import Clock, ClockStamp
from joulewise.interfaces import PowerSample, RunContext
from joulewise.schemas import BenchmarkConfig

NS_PER_SECOND = 1_000_000_000
TRACE_DOMAIN = "joulewise.controller.epoch_ns"
HAZARD_UNJUDGED = "hazard.unjudged:battery,ac,thermal,contention"
# quiet_mac_exploratory.json: post_window_sampling_dwell_s, the 1 s minimum.
POST_WINDOW_DWELL_S = 1.0


def _conversion_error_ns(seconds: float) -> float:
    # Multiplication rounds by <= half the spacing of the ns product:
    # 128 ns at an epoch near 1.8e18 ns. round() then costs <= 0.5 ns;
    # the latter vanishes for epoch products already spaced by integer ns.
    product_spacing = math.ulp(seconds * NS_PER_SECOND)
    return product_spacing / 2 + (0.5 if product_spacing < 1 else 0.0)


def seconds_ns(seconds: float) -> int:
    """Convert controller seconds once; price float representation in mapping."""
    return round(seconds * NS_PER_SECOND)


def _stamp_record(stamp: ClockStamp) -> dict[str, int]:
    """Keep the existing paired observation as integer ns in shared records."""
    return {
        "epoch_ns": seconds_ns(stamp.epoch_s),
        "monotonic_before_ns": seconds_ns(stamp.monotonic_before_s),
        "monotonic_after_ns": seconds_ns(stamp.monotonic_after_s),
        "wall_resolution_ns": math.ceil(stamp.wall_resolution_s * NS_PER_SECOND),
        "monotonic_resolution_ns": math.ceil(stamp.monotonic_resolution_s * NS_PER_SECOND),
    }


def _restore_stamp(record: Mapping[str, int]) -> ClockStamp:
    # Integer-ns serialization and division back to seconds each round.
    # Add the original ns-product conversion and half an ulp of the restored
    # quotient to the corresponding clock resolution; never assume 1 ns.
    epoch_s = record["epoch_ns"] / NS_PER_SECOND
    before_s = record["monotonic_before_ns"] / NS_PER_SECOND
    after_s = record["monotonic_after_ns"] / NS_PER_SECOND

    def serialization_error_s(value: float) -> float:
        return _conversion_error_ns(value) / NS_PER_SECOND + math.ulp(value) / 2

    return ClockStamp(
        epoch_s=epoch_s, monotonic_before_s=before_s, monotonic_after_s=after_s,
        wall_resolution_s=record["wall_resolution_ns"] / NS_PER_SECOND + serialization_error_s(epoch_s),
        monotonic_resolution_s=record["monotonic_resolution_ns"] / NS_PER_SECOND
        + max(serialization_error_s(before_s), serialization_error_s(after_s)),
    )


def monotonic_ns(stamp: ClockStamp) -> int:
    """Use the midpoint of the existing paired monotonic bracket."""
    return seconds_ns(
        stamp.monotonic_before_s
        + (stamp.monotonic_after_s - stamp.monotonic_before_s) / 2
    )


def stamp_mapping(
    stamps: Sequence[ClockStamp], *, episode_domain: str,
    evidence: Mapping[str, Any] | None = None,
) -> tuple[ClockMapping, tuple[str, ...]]:
    """Map already anchored controller epoch samples into episode monotonic time.

    The native anchor effective bound already includes the wall/monotonic span,
    clock resolutions and numerical padding. We carry that complete bound.
    Unresolved anchors retain observations with an explicit flag; their mapping
    is an observed bracket only and cannot license an attribution claim.
    """
    if not stamps:
        raise ValueError("at least one paired ClockStamp is required")
    lower = min(s.epoch_s - s.monotonic_after_s for s in stamps)
    upper = max(s.epoch_s - s.monotonic_before_s for s in stamps)
    flags: list[str] = []
    anchor = (evidence or {}).get("clock_anchor", {})
    bridge_resolution_s = max(s.wall_resolution_s + s.monotonic_resolution_s for s in stamps)
    if anchor.get("status") == "bounded":
        anchor_lower = float(anchor["wall_minus_monotonic_lower_s"])
        anchor_upper = float(anchor["wall_minus_monotonic_upper_s"])
        # The adapter's effective bound already includes the FULL anchor
        # wall-minus-monotonic span. Charge only observations outside it,
        # rather than adding half that span again.
        outside_s = max(0.0, anchor_lower - lower, upper - anchor_upper)
        lower = min(lower, anchor_lower)
        upper = max(upper, anchor_upper)
        # These episode/serialization observations are distinct from the
        # collector's anchor stamps; their resolution includes restored-record
        # rounding, which must survive even on a bounded native-anchor path.
        bound_s = float(anchor["effective_clock_anchor_bound_s"]) + outside_s + bridge_resolution_s
        method = str(anchor["method"])
    else:
        bound_s = (
            bridge_resolution_s + (upper - lower) / 2
        )
        method = "unmeasured" if evidence is not None else "paired_clock_bracket_only"
        if evidence is not None:
            flags.append("clock_anchor_unresolved")
    offset_s = -(lower + (upper - lower) / 2)
    # Paired clock input representation and subtraction/midpoint arithmetic:
    # each floating operation/read costs at most half its value's ulp.
    representation_ns = max(
        (math.ulp(s.epoch_s) + math.ulp(s.monotonic_before_s)
         + math.ulp(s.monotonic_after_s)) * NS_PER_SECOND / 2
        for s in stamps
    )
    arithmetic_ns = sum(
        math.ulp(value) * NS_PER_SECOND / 2
        for value in (lower, upper, upper - lower, offset_s)
    )
    # Price a trace epoch conversion, a turn monotonic conversion and the
    # offset conversion separately, using spacing at each ns product.
    conversion_ns = max(
        _conversion_error_ns(s.epoch_s)
        + _conversion_error_ns(s.monotonic_before_s
                               + (s.monotonic_after_s - s.monotonic_before_s) / 2)
        for s in stamps
    ) + _conversion_error_ns(offset_s)
    uncertainty_ns = math.ceil(
        bound_s * NS_PER_SECOND + representation_ns + arithmetic_ns + conversion_ns
    )
    return ClockMapping(
        trace_domain=TRACE_DOMAIN, episode_domain=episode_domain,
        offset_ns=seconds_ns(offset_s), uncertainty_ns=uncertainty_ns,
        method=("unmeasured" if method == "unmeasured" else
                f"{method}; paired wall/monotonic envelope; half-ulp ns-product conversions"),
    ), tuple(flags)


def power_records(
    samples: Sequence[PowerSample], *, nominal_interval_ns: int,
    evidence: Mapping[str, Any] | None = None,
) -> tuple[tuple[PowerTrace, ...], tuple[str, ...]]:
    """Project adapter samples without parsing native telemetry a second time."""
    grouped: dict[str, list[PowerSample]] = defaultdict(list)
    for sample in samples:
        grouped[sample.rail or "package"].append(sample)
    traces: list[PowerTrace] = []
    flags: list[str] = []
    for channel, rows in sorted(grouped.items()):
        rows.sort(key=lambda sample: sample.timestamp_s)
        times: list[int] = []
        values: list[float] = []
        supports: list[list[int] | None] = []
        for sample in rows:
            timestamp = seconds_ns(sample.timestamp_s)
            if not math.isfinite(sample.power_w):
                flags.append(f"nonfinite_power:{channel}")
                continue
            if sample.power_w < 0.0:
                flags.append(f"negative_power:{channel}")
            times.append(timestamp)
            values.append(sample.power_w)
            supports.append(
                [seconds_ns(sample.interval_start_s), seconds_ns(sample.interval_end_s)]
                if sample.interval_start_s is not None
                and sample.interval_end_s is not None else None
            )
        widths = {b - a for support in supports if support is not None for a, b in [support]}
        variable = len(widths) > 1 or (
            bool(widths) and any(support is None for support in supports)
        )
        if variable:
            flags.append(f"variable_averaging_support:{channel}")
        # Window means are not instantaneous readings. Keep the native end
        # stamp and support paired, even when their widths differ.
        written_times, written_values, written_supports = [], [], []
        for timestamp, value, support in zip(times, values, supports):
            if written_times and timestamp <= written_times[-1]:
                flags.append(f"nonincreasing_power_timestamp:{channel}")
                continue
            written_times.append(timestamp)
            written_values.append(value)
            written_supports.append(support)
        times, values, supports = written_times, written_values, written_supports
        source = "powermetrics" if any(row.source == "powermetrics" for row in rows) else "mock"
        # Parsing converts mW to W but does not establish sensor quantization.
        # Leave resolution unknown rather than inventing a physical quantum.
        resolution = None
        traces.append(PowerTrace(
            source=source, channel=channel, clock_domain=TRACE_DOMAIN,
            t_ns=tuple(times), values=tuple(values), unit="W",
            nominal_interval_ns=nominal_interval_ns,
            averaging_window_ns=next(iter(widths)) if len(widths) == 1 and not variable else None,
            duty_fraction=1.0 if widths and not any(s is None for s in supports) else None,
            resolution=resolution,
            notes=json.dumps({
                "sample_support_ns": supports,
                "clock_anchor": {
                    "method": (evidence or {}).get("clock_anchor", {}).get("method"),
                    "status": (evidence or {}).get("clock_anchor", {}).get("status", "unknown"),
                    "effective_bound_ns": math.ceil(
                        (evidence or {}).get("clock_anchor", {}).get(
                            "effective_clock_anchor_bound_s", 0.0
                        ) * NS_PER_SECOND
                    ) if (evidence or {}).get("clock_anchor", {}).get("status") == "bounded" else None,
                },
                "flags": [flag for flag in flags if flag.endswith(f":{channel}")],
                "power_scope": "SoC rails; not wall energy",
            }, sort_keys=True),
        ))
    return tuple(traces), tuple(flags)


class ApplePowerSampler:
    """PowerSampler over PowermetricsTelemetryAdapter with no new capture path."""

    def __init__(
        self, config: BenchmarkConfig, clock: Clock, *, episode_domain: str,
        context: RunContext | None = None,
        adapter: Any | None = None,
    ) -> None:
        self.config = config
        self.clock = clock
        self.context = context
        self.episode_domain = episode_domain
        self.clock_domain = TRACE_DOMAIN
        self.adapter = adapter if adapter is not None else PowermetricsTelemetryAdapter(clock)
        self.flags: tuple[str, ...] = (HAZARD_UNJUDGED,)
        self.clock_mappings: tuple[ClockMapping, ...] = ()
        self.uncertainty_evidence: dict[str, Any] = {}
        self._start: ClockStamp | None = None
        self._active = False

    def start(self) -> None:
        if self._active:
            self.flags += ("sampler_already_started",)
            return
        self.flags = (HAZARD_UNJUDGED,)
        self.clock_mappings = ()
        self.uncertainty_evidence = {}
        try:
            result = self.adapter.start_sampling(self.config, self.context)
            self._active = result.ok
            if not result.ok:
                self.flags += (f"power_unavailable:{result.message}",)
        except Exception as exc:
            self.flags += (f"power_unavailable:{type(exc).__name__}:{exc}",)
        self._start = self.clock.stamp()

    def stop(self) -> tuple[PowerTrace, ...]:
        stop = self.clock.stamp()
        start = self._start or stop
        samples: list[PowerSample] = []
        if self._active:
            try:
                # Keep the measured stop marker fixed while collecting the
                # policy's 1 s right-edge support; dwell is outside the episode.
                self.clock.sleep(POST_WINDOW_DWELL_S)
                result = self.adapter.stop_sampling_with_evidence(
                    self.config, self.context,
                    sampling_started=start, sampling_stopped=stop,
                    required_post_window_tail_s=POST_WINDOW_DWELL_S,
                )
                samples = result.samples
                self.uncertainty_evidence = result.uncertainty_evidence
            except Exception as exc:
                self.flags += (f"power_unavailable:{type(exc).__name__}:{exc}",)
            finally:
                self._active = False
        else:
            self.flags += ("power_unavailable:sampler_not_active",)
        mapping, flags = stamp_mapping(
            (start, stop), episode_domain=self.episode_domain,
            evidence=self.uncertainty_evidence,
        )
        self.clock_mappings = (mapping,)
        traces, trace_flags = power_records(
            samples, nominal_interval_ns=round(NS_PER_SECOND / self.config.sampling.power_hz),
            evidence=self.uncertainty_evidence,
        )
        self.flags += flags + trace_flags
        if not traces:
            # Protocol requires an explanation in trace.notes, even without
            # samples. A failed collector never fabricates zero-watt readings.
            traces = (PowerTrace(
                source="powermetrics", channel="package", clock_domain=TRACE_DOMAIN,
                t_ns=(), values=(), unit="W",
                nominal_interval_ns=round(NS_PER_SECOND / self.config.sampling.power_hz),
                notes=json.dumps({"flags": self.flags, "paired_stamps_ns": [_stamp_record(start), _stamp_record(stop)]}),
            ),)
        # Every trace (including unavailable/empty traces) carries the absence
        # of hazard judgment. A caller need not know this sampler's properties.
        noted = []
        for trace in traces:
            notes = json.loads(trace.notes)
            # Channel diagnostics belong only to their own rail. Global capture
            # and hazard diagnostics still accompany every trace.
            own_flags = [flag for flag in self.flags
                         if flag not in trace_flags or flag.endswith(f":{trace.channel}")]
            notes["flags"] = list(dict.fromkeys([*notes.get("flags", ()), *own_flags]))
            noted.append(replace(trace, notes=json.dumps(notes, sort_keys=True)))
        return tuple(noted)
