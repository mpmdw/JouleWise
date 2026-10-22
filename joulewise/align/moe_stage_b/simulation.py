"""Synthetic Stage B sensor acquisition over an analytic traffic time profile.

No hardware or network calls occur here. Samples average the profile over the
documented trailing acquisition window, then add seeded noise and quantization.
The spine has no sensor_sim module, so this lane owns its local implementation.
"""

from __future__ import annotations

import bisect
import math
import random
from dataclasses import dataclass, replace
from typing import Sequence

from joulewise.align.records import Episode, PowerTrace
from joulewise.align.moe_stage_b.traffic import (
    NS_PER_SECOND, OffloadConfig, TokenWindow, TrafficResult,
    episode_token_windows, model_traffic,
)


@dataclass(frozen=True)
class SensorModel:
    name: str
    source: str
    channel: str
    interval_ns: int
    averaging_window_ns: int
    quantum_w: float
    noise_std_w: float
    phase_ns: int = 0
    notes: str = ""


@dataclass(frozen=True)
class PowerPulse:
    start_ns: int
    end_ns: int
    watts: float


@dataclass(frozen=True)
class SimulatedTrace:
    trace: PowerTrace | None
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class SimulatedEpisode:
    episode: Episode
    traffic: TrafficResult
    flags: tuple[str, ...] = ()


def nvml_sensor(*, noise_std_w: float, quantum_w: float, phase_ns: int = 0) -> SensorModel:
    """The requested 25 ms / 100 ms NVML profile; verify it on the target GPU.

    The shared PowerTrace contract describes this duty profile for A100/H100.
    It is a sensitivity case, not an assertion about every RTX 3080 Ti driver.
    """
    return SensorModel("nvml_100ms_25ms", "nvml_power", "gpu0",
                       100_000_000, 25_000_000, quantum_w, noise_std_w, phase_ns,
                       "synthetic requested NVML duty profile; target cadence requires verification")


def ina3221_sensor(
    *, bus_voltage_v: float, current_a: float, shunt_ohm: float,
    enabled_channels: int, shunt_conversion_ns: int, bus_conversion_ns: int,
    averages: int, poll_interval_ns: int, noise_std_w: float, phase_ns: int = 0,
) -> SensorModel:
    """Derive effective cadence and power quantum from the deployed rail setup.

    TI INA3221 datasheet SBOS576C: shunt LSB 40 uV; bus LSB 8 mV.
    https://www.ti.com/lit/ds/symlink/ina3221.pdf
    A full enabled-channel conversion/averaging frame bounds independent updates.
    A contiguous frame average approximates staggered rail conversions; measure
    the actual transfer function before making a token-spectrum claim.
    """
    frame = enabled_channels * (shunt_conversion_ns + bus_conversion_ns) * averages
    if shunt_ohm <= 0:
        quantum = math.nan
    else:
        # First-order P=VI quantization, including the product of both LSBs.
        delta_i, delta_v = 40e-6 / shunt_ohm, 8e-3
        quantum = abs(bus_voltage_v)*delta_i + abs(current_a)*delta_v + delta_i*delta_v
    return SensorModel("ina3221", "ina3221", "VDD_IN", max(frame, poll_interval_ns),
                       frame, quantum, noise_std_w, phase_ns,
                       "synthetic contiguous-frame approximation; rail conversion staggering unmodelled")


class _Integral:
    """Prefix integral of overlapping rectangular loads, in watt-nanoseconds."""

    def __init__(self, pulses: Sequence[PowerPulse]) -> None:
        changes: dict[int, float] = {}
        for pulse in pulses:
            changes[pulse.start_ns] = changes.get(pulse.start_ns, 0.0) + pulse.watts
            changes[pulse.end_ns] = changes.get(pulse.end_ns, 0.0) - pulse.watts
        self.times = sorted(changes)
        self.rates: list[float] = []
        self.areas: list[float] = []
        rate = area = 0.0
        previous = self.times[0] if self.times else 0
        for time in self.times:
            area += rate*(time-previous)
            rate += changes[time]
            self.areas.append(area)
            self.rates.append(rate)
            previous = time

    def at(self, time: int) -> float:
        i = bisect.bisect_right(self.times, time)-1
        if i < 0:
            return 0.0
        return self.areas[i] + self.rates[i]*(time-self.times[i])

    def between(self, start_ns: int, end_ns: int) -> float:
        return self.at(end_ns)-self.at(start_ns)


def simulate_trace(
    traffic: TrafficResult, sensor: SensorModel, *, start_ns: int, end_ns: int,
    clock_domain: str, baseline_w: float, loads: Sequence[PowerPulse] = (),
    seed: int = 0, episode_bias_w: float = 0.0,
) -> SimulatedTrace:
    """Sample exact pulse-window overlaps; no fine-grid approximation is needed.

    episode_bias_w is correlated within the episode and does not average down.
    noise_std_w is independent noise after acquisition averaging. Seeds are local.
    """
    flags = list(traffic.flags)
    invalid = (end_ns <= start_ns or sensor.interval_ns <= 0
               or sensor.averaging_window_ns <= 0
               or not 0 <= sensor.phase_ns < sensor.interval_ns
               or sensor.source not in ("ina3221", "nvml_power", "mock")
               or not math.isfinite(sensor.quantum_w) or sensor.quantum_w <= 0
               or not math.isfinite(sensor.noise_std_w) or sensor.noise_std_w < 0
               or not math.isfinite(baseline_w) or not math.isfinite(episode_bias_w))
    if invalid:
        return SimulatedTrace(None, tuple(dict.fromkeys(flags + ["invalid_sensor_or_profile"])))
    if any(p.end_ns <= p.start_ns or not math.isfinite(p.watts) for p in loads):
        return SimulatedTrace(None, tuple(dict.fromkeys(flags + ["invalid_power_pulse"])))
    pulses = list(loads)
    for pulse in traffic.pulses:
        duration = pulse.end_ns-pulse.start_ns
        if duration <= 0 or not math.isfinite(pulse.energy_j):
            return SimulatedTrace(None, tuple(dict.fromkeys(flags + ["invalid_transfer_pulse"])))
        pulses.append(PowerPulse(pulse.start_ns, pulse.end_ns,
                                 pulse.energy_j*NS_PER_SECOND/duration))
        if pulse.end_ns > end_ns or pulse.start_ns < start_ns:
            flags.append("traffic_outside_episode")
    integral = _Integral(pulses)
    rng = random.Random(seed)
    times: list[int] = []
    values: list[float] = []
    # Include one reading beyond the end if needed to reconstruct the final cell.
    t = start_ns + sensor.phase_ns
    last = end_ns + sensor.interval_ns
    while t < last:
        watts = (baseline_w + episode_bias_w
                 + integral.between(t-sensor.averaging_window_ns, t)/sensor.averaging_window_ns
                 + rng.gauss(0.0, sensor.noise_std_w))
        values.append(round(watts/sensor.quantum_w)*sensor.quantum_w)
        times.append(t)
        t += sensor.interval_ns
    if sensor.averaging_window_ns < sensor.interval_ns:
        flags.append("sensor_duty_gaps")
    if sensor.averaging_window_ns > sensor.interval_ns:
        flags.append("overlapping_acquisition_windows")
    flags.append("synthetic_power_trace")
    trace = PowerTrace(
        source=sensor.source, channel=sensor.channel, clock_domain=clock_domain,
        t_ns=tuple(times), values=tuple(values), unit="W",
        nominal_interval_ns=sensor.interval_ns,
        averaging_window_ns=sensor.averaging_window_ns,
        duty_fraction=min(1.0, sensor.averaging_window_ns/sensor.interval_ns),
        resolution=sensor.quantum_w,
        notes="; ".join((sensor.name, sensor.notes, *dict.fromkeys(flags))),
    )
    return SimulatedTrace(trace, tuple(dict.fromkeys(flags)))


def simulate_episode(
    episode: Episode, config: OffloadConfig, sensor: SensorModel, *,
    baseline_w: float, prefill_load_w: float, decode_load_w: float,
    tool_load_w: float, seed: int = 0, episode_bias_w: float = 0.0,
    windows: Sequence[TokenWindow] | None = None,
) -> SimulatedEpisode:
    """RouterLog -> traffic -> sensor windows -> shared Episode/PowerTrace.

    Loads are above baseline and supplied independently of route identity.
    Explicit token windows bypass only the uniform timing adapter, not traffic
    or sensor simulation. All input episode flags survive.
    """
    flags = list(episode.flags)
    if episode.router_log is None:
        flags.append("missing_router_log")
        return SimulatedEpisode(replace(episode, flags=tuple(dict.fromkeys(flags))),
                                TrafficResult((), (), ("missing_router_log",)), tuple(flags))
    if windows is None:
        timing = episode_token_windows(episode, prefill_batch_tokens=config.prefill_batch_tokens)
        flags.extend(timing.flags)
        windows = timing.windows
    traffic = model_traffic(episode.router_log, config, windows=windows)
    flags.extend(traffic.flags)
    loads: list[PowerPulse] = []
    for turn in episode.turns:
        if turn.first_token_ns is not None:
            for start, end, watts in ((turn.start_ns, turn.first_token_ns, prefill_load_w),
                                       (turn.first_token_ns, turn.end_ns, decode_load_w)):
                if end > start:
                    loads.append(PowerPulse(start, end, watts))
        for call in turn.tool_calls:
            if call.end_ns > call.start_ns:
                loads.append(PowerPulse(call.start_ns, call.end_ns, tool_load_w))
    sampled = simulate_trace(traffic, sensor, start_ns=episode.start_ns,
                             end_ns=episode.end_ns, clock_domain=episode.clock_domain,
                             baseline_w=baseline_w, loads=loads, seed=seed,
                             episode_bias_w=episode_bias_w)
    flags.extend(sampled.flags)
    result = replace(episode,
                     power_traces=episode.power_traces + ((sampled.trace,) if sampled.trace else ()),
                     flags=tuple(dict.fromkeys(flags)))
    return SimulatedEpisode(result, traffic, result.flags)
