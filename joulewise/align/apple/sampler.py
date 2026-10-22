"""Bridge the existing Apple telemetry adapter into alignment power records.

The adapter owns capture, parsing and native-second clock anchoring. This
module only changes representation. Native averaging supports remain in notes
when their widths vary, since records.v1 has one averaging width per trace.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from typing import Any, Mapping, Sequence

from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
from joulewise.align.records import ClockMapping, PowerTrace
from joulewise.clock import Clock, ClockStamp
from joulewise.interfaces import PowerSample, RunContext
from joulewise.schemas import BenchmarkConfig

NS_PER_SECOND = 1_000_000_000
TRACE_DOMAIN = "joulewise.controller.epoch_ns"


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
    # A second integer/float conversion contributes at most 1 ns rounding,
    # in addition to the float epoch ulp priced by stamp_mapping.
    return ClockStamp(
        epoch_s=record["epoch_ns"] / NS_PER_SECOND,
        monotonic_before_s=record["monotonic_before_ns"] / NS_PER_SECOND,
        monotonic_after_s=record["monotonic_after_ns"] / NS_PER_SECOND,
        wall_resolution_s=(record["wall_resolution_ns"] + 1) / NS_PER_SECOND,
        monotonic_resolution_s=(record["monotonic_resolution_ns"] + 1) / NS_PER_SECOND,
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
    if anchor.get("status") == "bounded":
        lower = min(lower, anchor["wall_minus_monotonic_lower_s"])
        upper = max(upper, anchor["wall_minus_monotonic_upper_s"])
        bound_s = float(anchor["effective_clock_anchor_bound_s"])
        method = str(anchor["method"])
    else:
        bound_s = max(s.wall_resolution_s + s.monotonic_resolution_s for s in stamps)
        method = "paired_clock_bracket_only"
        if evidence is not None:
            flags.append("clock_anchor_unresolved")
    # Float seconds are the existing adapter contract. Include a full ulp of
    # every wall and monotonic value and 1 ns for rounding into integer records.
    representation_s = max(
        math.ulp(value)
        for stamp in stamps
        for value in (
            stamp.epoch_s, stamp.monotonic_before_s, stamp.monotonic_after_s
        )
    )
    uncertainty_ns = math.ceil(
        (bound_s + (upper - lower) / 2 + representation_s) * NS_PER_SECOND
    ) + 1
    return ClockMapping(
        trace_domain=TRACE_DOMAIN,
        episode_domain=episode_domain,
        offset_ns=seconds_ns(-(lower + (upper - lower) / 2)),
        uncertainty_ns=uncertainty_ns,
        method=f"{method}; paired wall/monotonic envelope; outward ns conversion",
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
            if times and timestamp <= times[-1]:
                flags.append(f"nonincreasing_power_timestamp:{channel}")
                continue
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
        self.flags: tuple[str, ...] = ()
        self.clock_mappings: tuple[ClockMapping, ...] = ()
        self.uncertainty_evidence: dict[str, Any] = {}
        self._start: ClockStamp | None = None
        self._active = False

    def start(self) -> None:
        if self._active:
            self.flags += ("sampler_already_started",)
            return
        self.flags = ()
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
                result = self.adapter.stop_sampling_with_evidence(
                    self.config, self.context,
                    sampling_started=start, sampling_stopped=stop,
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
        return traces
