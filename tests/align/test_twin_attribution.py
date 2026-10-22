"""Twin agreement for lane A4 attribution: review round 3 after fix round 2b.

The lane (``joulewise/align/attribution.py``) and the independent twin
(``tests/align/twins/attribution_twin.py``) run on the same seeded,
production-shaped agent episodes, and their outputs are compared:

* segmentation (turn, kind, start, end): integers, compared exactly;
* joules of every segment and of the total: each estimate prints a
  half-width, so the bar is 1% of the smaller of the two printed half-widths
  (the orchestrator's bar). Where that half-width is zero or infinite there is
  no usable printed uncertainty and the bar is 1e-6 relative, or 1e-6 J
  absolute below 1 J;
* half-widths: the lane's reading differs from the twin's by terms the lead
  prescribed in fix rounds 2 and 2b (full C1 hold-versus-line difference, C2(a)
  duty-gap and C2(b) query-clipped window-cut sensitivities, counter
  reset-interval sensitivity). The expected lane half-width is rebuilt here
  from the twin's own primitives plus an independent recomputation of the C2
  and reset terms, then compared under the 1e-6 relative rule (a half-width
  has no printed uncertainty of its own);
* flags with the same meaning, as sets, through a name map;
* the duty-uncovered fraction: both are one correctly rounded division of the
  same two integers, so bit identity is the real property.

Readings that differ on purpose (partial-coverage idle, implausible counter
drops, missing traces, overlapping windows, reversed intervals) are pinned in
``KnownReadingDifferences`` with hand-computed numbers.

The worlds: twenty-turn agent episodes (also one-turn and thirty-two-turn
ones) with a long first prefill and 15-120 ms cached-prefix prefills, decode
with a token-rate ripple, tool calls of 0.2-30 s (inside the decode, as the
brief draws them, and after the model call, as the runner records them), short
5-200 ms tools, 1-300 ms client gaps, and finite (at most 0.5 ms) power slews.
True power is piecewise linear, so every true integral is exact.
Sensors: a 1 kHz INA3221 rail; NVML power as a 25 ms window per 100 ms, both
host-polled and as the NVML lane records ``power_instant`` (window ends at the
100 ms sensor cadence, ``nominal_interval_ns`` = the 10 ms poll); a 100 ms
whole-window powermetrics package; powermetrics recorded as window means at
jittered points with no window (the Apple lane's shape); an NVML energy
counter with a restart.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass, replace
import math
import json
import random
import unittest

from joulewise.align.records import ClockMapping, Episode, PowerTrace, ToolCall, Turn
from tests.align.twins import attribution_twin as twin

try:
    from joulewise.align import attribution as lane
except ImportError:  # The twin branch alone carries no lane module.
    lane = None


NS = 1_000_000_000  # Nanoseconds per second, by definition.
ORIGIN = 7 * 10**17  # A host-monotonic epoch at which float64 cannot hold single ns.


# ---------------------------------------------------------------- truth

class Truth:
    """Piecewise-linear true power (knots of integer ns and W), held flat outside."""

    def __init__(self, knots: list[tuple[int, float]]) -> None:
        self.t = [k[0] for k in knots]
        self.p = [k[1] for k in knots]

    def _on(self, i: int, x: int) -> float:
        t0, t1 = self.t[i], self.t[i + 1]
        return self.p[i] + (self.p[i + 1] - self.p[i]) * ((x - t0) / (t1 - t0))

    def value(self, x: int) -> float:
        if x <= self.t[0]:
            return self.p[0]
        if x >= self.t[-1]:
            return self.p[-1]
        return self._on(bisect_right(self.t, x) - 1, x)

    def integral(self, a: int, b: int) -> float:
        """Exact trapezoids of the piecewise-linear truth on [a, b] (J)."""
        if b <= a:
            return 0.0
        terms = []
        if a < self.t[0]:
            terms.append(self.p[0] * (min(b, self.t[0]) - a) / NS)
        if b > self.t[-1]:
            terms.append(self.p[-1] * (b - max(a, self.t[-1])) / NS)
        i = max(0, bisect_right(self.t, a) - 1)
        while i < len(self.t) - 1 and self.t[i] < b:
            u, v = max(a, self.t[i]), min(b, self.t[i + 1])
            if v > u:
                terms.append((self._on(i, u) + self._on(i, v)) / 2 * (v - u) / NS)
            i += 1
        return math.fsum(terms)


# ---------------------------------------------------------------- worlds

PLATFORMS = {
    # (idle/gap, prefill, decode, decode ripple amplitude, tool) in W.
    # Fixture workload levels: an A100-class GPU board, a Jetson VDD_IN rail,
    # an M3-class package. They set the scale of the worlds, not any bar.
    "gpu": ((60.0, 75.0), (320.0, 420.0), (210.0, 290.0), (5.0, 25.0), (75.0, 95.0)),
    "jetson": ((3.0, 3.6), (15.0, 19.0), (10.0, 13.0), (0.5, 1.5), (4.0, 6.0)),
    "mac": ((6.0, 9.0), (38.0, 48.0), (24.0, 32.0), (1.0, 3.0), (10.0, 14.0)),
}


@dataclass
class World:
    episode: Episode
    truth: Truth
    expected: list[tuple[int | None, str, int, int]]  # (turn, kind, start, end), absolute ns
    platform: str


def make_world(seed: int, platform: str, n_turns: int = 20) -> World:
    """A runner-shaped episode and its true power. Times are relative to 0, then ORIGIN."""
    rng = random.Random(seed * 7919 + len(platform))
    lv = {name: rng.uniform(*rng_range) for name, rng_range in
          zip(("gap", "prefill", "decode", "ripple", "tool"), PLATFORMS[platform])}
    phases: list[tuple[int | None, str, int, int]] = []
    cursor = 0

    def add(owner: int | None, kind: str, length: int) -> None:
        nonlocal cursor
        phases.append((owner, kind, cursor, cursor + length))
        cursor += length

    def ms(lo: float, hi: float) -> int:
        return rng.randint(int(lo * 1_000_000), int(hi * 1_000_000))

    add(None, "gap", ms(200, 1500))
    turns = []
    context = rng.randint(1500, 6000)
    for index in range(n_turns):
        start = cursor
        long_prefill = index == 0 or rng.random() < 0.15
        prefill = ms(400, 3000) if long_prefill else ms(15, 120)
        add(index, "prefill", prefill)
        first = cursor
        decode = ms(300, 15000)
        calls = []
        if rng.random() < 0.3:  # The brief's shape: a tool inside the decode.
            head = int(decode * rng.uniform(0.1, 0.6))
            add(index, "decode", head)
            tool = ms(200, 30000) if rng.random() < 0.8 else ms(5, 200)
            calls.append((cursor, cursor + tool))
            add(index, "tool", tool)
            add(index, "decode", decode - head)
        else:
            add(index, "decode", decode)
        end = cursor
        if rng.random() < 0.7:  # The runner's shape: dispatch after the model call.
            add(None, "gap", ms(1, 90))
            tool = ms(200, 30000) if rng.random() < 0.8 else ms(5, 200)
            calls.append((cursor, cursor + tool))
            add(index, "tool", tool)
        add(None, "gap", ms(1, 300))
        # Token counts follow fixture serving rates; attribution never reads them.
        prefill_tokens = prefill * (600 if long_prefill else 6000) // NS + 1
        decode_tokens = decode * 40 // NS + 1
        no_first = rng.random() < 0.05
        tool_calls = tuple(ToolCall("local_exec" if k % 2 else "local_search",
                                    ORIGIN + a, ORIGIN + b, rng.randint(64, 4096),
                                    rng.randint(256, 65536), logged=rng.random() > 0.2)
                           for k, (a, b) in enumerate(calls))
        turns.append(Turn(index, ORIGIN + start, ORIGIN + end, context, prefill_tokens,
                          decode_tokens, hidden_tokens=decode_tokens // 4,
                          first_token_ns=None if no_first else ORIGIN + first,
                          tool_calls=tool_calls, logged=rng.random() > 0.1))
        context += prefill_tokens + decode_tokens
    add(None, "gap", ms(200, 1000))

    # True power: phase levels joined by slews of at most 0.5 ms, with a
    # token-rate triangle ripple on decode (period 30-60 ms).
    knots: list[tuple[int, float]] = [(-3 * NS, lv["gap"])]
    ripple_period = ms(30, 60)
    for owner, kind, a, b in phases:
        h = min(250_000, (b - a) // 4)
        level = lv[kind]
        if kind == "decode":
            knots.append((a + h, level))
            t, sign = a + h + ripple_period // 2, 1
            while t < b - h:
                knots.append((t, level + sign * lv["ripple"]))
                t += ripple_period // 2
                sign = -sign
            knots.append((b - h, level))
        else:
            knots.append((a + h, level))
            knots.append((b - h, level))
    knots.append((cursor + 3 * NS, lv["gap"]))
    clean: list[tuple[int, float]] = []
    for t, p in knots:
        if clean and t <= clean[-1][0]:
            continue
        clean.append((t, p))
    truth = Truth([(ORIGIN + t, p) for t, p in clean])

    # Expected tiling: a turn with no first token is all decode.
    no_first_turns = {t.index for t in turns if t.first_token_ns is None}
    expected: list[tuple[int | None, str, int, int]] = []
    for owner, kind, a, b in phases:
        if owner in no_first_turns and kind == "prefill":
            kind = "decode"
        if expected and expected[-1][:2] == (owner, kind) and expected[-1][3] == ORIGIN + a \
                and kind != "tool":
            expected[-1] = (owner, kind, expected[-1][2], ORIGIN + b)
        else:
            expected.append((owner, kind, ORIGIN + a, ORIGIN + b))
    episode = Episode(f"r3-{platform}-{seed}", "shade/synthetic-agent-loop", "sabotage",
                      "local-open-weight", "mock:local-vllm", seed, "host",
                      ORIGIN, ORIGIN + cursor, tuple(turns), flags=("synthetic.provisional",))
    return World(episode, truth, expected, platform)


# ---------------------------------------------------------------- sensors

def _quantize(value: float, quantum: float, rng: random.Random) -> float:
    # Half-quantum analogue noise, then rounding to the printed quantum.
    return round((value + rng.uniform(-quantum / 2, quantum / 2)) / quantum) * quantum


def sense(world: World, shape: str, seed: int) -> tuple[PowerTrace, tuple[ClockMapping, ...]]:
    """One production-shaped sensor trace of the world's true power."""
    rng = random.Random(seed * 104729 + len(shape))
    e0, e1 = world.episode.start_ns, world.episode.end_ns
    truth = world.truth
    if shape == "ina3221":
        # 1 kHz rail, 40 uV / 5 mOhm * 5 V = 0.04 W quantum, meter clock
        # 3.2 s behind the host, mapped by a 1 ms round trip (0.5 ms half-width).
        period, offset = NS // 1000, 3_200_000_000
        times = [t + rng.randint(-20_000, 20_000)
                 for t in range(e0 - 200 * period + 371_000, e1 + 200 * period, period)]
        values = [_quantize(truth.value(t), 0.04, rng) for t in times]
        trace = PowerTrace("ina3221", "VDD_IN", "jetson", tuple(t - offset for t in times),
                           tuple(values), "W", period, resolution=0.04)
        return trace, (ClockMapping("jetson", "host", offset, 500_000, "round trip"),)
    if shape in ("nvml_host", "nvml_instant"):
        # A100: 25 ms mean ending at each 100 ms sensor update, integer mW.
        # nvml_host: host-polled at the sensor period, host clock, no mapping.
        # nvml_instant: the NVML lane's power_instant record: driver window
        # ends (sensor cadence), nominal_interval_ns = its 10 ms poll, a
        # mapped wall-clock domain with a 1 us + bracket half-width.
        period, window = NS // 10, NS // 40
        phase = rng.randint(0, period)
        times = [t + rng.randint(-2_000_000, 2_000_000) if shape == "nvml_host" else t
                 for t in range(e0 - 3 * period + phase, e1 + 3 * period, period)]
        values = [_quantize(truth.integral(t - window, t) / (window / NS), 0.001, rng)
                  for t in times]
        if shape == "nvml_host":
            return PowerTrace("nvml_power", "gpu0", "host", tuple(times), tuple(values), "W",
                              period, averaging_window_ns=window, duty_fraction=0.25,
                              resolution=0.001), ()
        offset = -1_700_000_000_123
        trace = PowerTrace("nvml_power", "gpu0:power_instant", "nvml-wall", tuple(t - offset for t in times),
                           tuple(values), "W", NS // 100, averaging_window_ns=window,
                           duty_fraction=0.25, resolution=0.001)
        return trace, (ClockMapping("nvml-wall", "host", offset, 41_000, "wall bracket"),)
    if shape == "powermetrics":
        # Back-to-back 100 ms whole windows, integer mW, a 2 ms mapping bracket.
        period = NS // 10
        times = list(range(e0 - 2 * period + rng.randint(0, period), e1 + 3 * period, period))
        values = [_quantize(truth.integral(t - period, t) / 0.1, 0.001, rng) for t in times]
        offset = 123_456_789
        trace = PowerTrace("powermetrics", "package", "mach", tuple(t - offset for t in times),
                           tuple(values), "W", period, averaging_window_ns=period,
                           duty_fraction=1.0, resolution=0.001)
        return trace, (ClockMapping("mach", "host", offset, 1_000_000, "round trip"),)
    if shape == "powermetrics_points":
        # The Apple lane's record when window widths vary: each value is the
        # mean of its own (t_prev, t] window, but no window is recorded.
        period = NS // 10
        times = [e0 - 2 * period]
        while times[-1] < e1 + 2 * period:
            times.append(times[-1] + period + rng.randint(-5_000_000, 5_000_000))
        values = [_quantize(truth.integral(a, b) / ((b - a) / NS), 0.001, rng)
                  for a, b in zip([times[0] - period] + times[:-1], times)]
        return PowerTrace("powermetrics", "package", "host", tuple(times), tuple(values), "W",
                          period, resolution=0.001), ()
    if shape == "nvml_energy":
        # Cumulative integer mJ polled every 100 ms (+-2 ms), one driver
        # restart inside the longest tool, host clock.
        period = NS // 10
        times = [t + rng.randint(-2_000_000, 2_000_000)
                 for t in range(e0 - 3 * period + rng.randint(0, period), e1 + 3 * period, period)]
        tools = [s for s in world.expected if s[1] == "tool"] or world.expected
        longest = max(tools, key=lambda s: s[3] - s[2])
        reset_k = bisect_right(times, (longest[2] + longest[3]) // 2)
        reset_t = (times[reset_k - 1] + times[reset_k]) // 2
        values = []
        running = 4_812_345.0  # Fixture driver baseline, independent of the work.
        for k, t in enumerate(times):
            if k == reset_k:
                running = truth.integral(reset_t, t)  # Restart: only post-reset work.
            elif k:
                running += truth.integral(times[k - 1], t)
            values.append(math.floor(running / 0.001) * 0.001)
        return PowerTrace("nvml_energy", "gpu0", "host", tuple(times), tuple(values),
                          "J_cumulative", period, resolution=0.001,
                          notes=json.dumps({"unknown_sensor_age_bound_ns":0})), ()
    raise ValueError(shape)


SHAPES = {  # shape -> platform of its truth
    "ina3221": "jetson", "nvml_host": "gpu", "nvml_instant": "gpu",
    "powermetrics": "mac", "powermetrics_points": "mac", "nvml_energy": "gpu",
}


def episode_with(world: World, shape: str, seed: int) -> Episode:
    trace, mappings = sense(world, shape, seed)
    return replace(world.episode, power_traces=(trace,), clock_mappings=mappings)


# ---------------------------------------------------------------- independent lane-reading half-width

def lane_reading_half_width(trace: PowerTrace, mapping: ClockMapping | None,
                            t0: int, t1: int) -> float:
    """The lane's half-width under full coverage, rebuilt independently.

    twin half-width (half C1 + clock + resolution) + the twin's own C1 again
    (fix round 2 made C1 the full difference) + C2(a) + C2(b) + reset terms.
    Assumes [t0, t1] inside coverage and no overlapping windows.
    """
    base = twin.trace_energy(trace, t0, t1, mapping=mapping)
    offset = mapping.offset_ns if mapping is not None else 0
    a, b = t0 - offset, t1 - offset  # Work in the trace's own domain.
    times, values = trace.t_ns, trace.values
    extra = []
    if trace.unit == "J_cumulative":
        cumulative, _ = twin._unwrapped(values)
        extra.append(twin._interpolation_term(times, cumulative, a, b, cumulative=True))
        steps = [(times[k], times[k + 1], values[k + 1] - values[k])
                 for k in range(len(times) - 1)]
        peak = max(d / ((y - x) / NS) for x, y, d in steps if d >= 0)
        for x, y, d in steps:
            if d < 0:
                extra.append(peak * max(0, min(b, y) - max(a, x)) / NS)
    else:
        extra.append(twin._interpolation_term(times, values, a, b, cumulative=False))
        w = trace.averaging_window_ns
        if w is not None and w > 0:
            for k in range(1, len(times)):
                gap_lo, gap_hi = times[k - 1], times[k] - w
                if gap_hi > gap_lo:
                    overlap = max(0, min(b, gap_hi) - max(a, gap_lo))
                    extra.append(abs(values[k] - values[k - 1]) * (overlap / NS) / 2)
            cut = set()
            for e in (a, b):
                k = bisect_right(times, e)
                if k < len(times) and times[k] - w < e and k not in cut:
                    cut.add(k)
                    near = values[max(0, k - 1):k + 2]
                    inside = min(b, times[k]) - max(a, times[k] - w)
                    extra.append((max(near) - min(near)) * min(w / 4, inside) / NS)
    expected = base.half_width_j + math.fsum(extra) + knot_interpolation_bound(trace,mapping,t0,t1)
    if trace.source == "powermetrics":
        # D-078 clause 11: attribution limit about 1 J; apply the minimum
        # after summing, as the lane and budget.energy do.
        expected = max(1.0, expected)
    return expected


def knot_interpolation_bound(trace, mapping, t0, t1):
    """Additional endpoint triangles at exact raw-sample knots, independently.

    The unchanged twin suppresses knot comparisons. Enumerate both touching
    intervals and clip their line-minus-left-hold integrals to the query.
    A cumulative counter compares its full held jump with the clipped
    interval increment; it contributes zero only on a whole interval.
    """
    offset=mapping.offset_ns if mapping else 0
    a,b=t0-offset,t1-offset
    ts,vs=trace.t_ns,trace.values
    if trace.unit == "J_cumulative":
        vs,_=twin._unwrapped(vs)
    terms=[]
    for endpoint in (a,b):
        k=bisect_right(ts,endpoint)-1
        if k < 0 or ts[k] != endpoint:
            continue
        for j in (k-1,k):
            if not 0 <= j < len(ts)-1:
                continue
            lo,hi=max(a,ts[j]),min(b,ts[j+1])
            if hi > lo:
                if trace.unit == "J_cumulative":
                    linear=(vs[j+1]-vs[j])*(hi-lo)/(ts[j+1]-ts[j])
                    held=(vs[j+1]-vs[j]) if hi == ts[j+1] else 0.
                    terms.append(abs(linear-held))
                else:
                    # Integral of slope*(t-t_left): dP/(2*dt)*(hi^2-lo^2).
                    terms.append(abs((vs[j+1]-vs[j])/(ts[j+1]-ts[j])
                                     *((hi-ts[j])**2-(lo-ts[j])**2)/2/NS))
    return math.fsum(terms)


FLAG_MAP = {  # lane flag -> twin flag of the same meaning
    "duty.uncovered": "duty.uncovered",
    "trace.partial_coverage": "trace.partial_coverage",
    "counter.wrap": "counter.wrap",
    "resolution.missing": "half_width.missing.resolution",
}
EPISODE_FLAG_MAP = {
    "turn.no_first_token": "turn.no_first_token", "tool.outside_episode": "tool.outside_episode",
    "tool.overlap": "tool.overlap", "turn.overlap": "turn.overlap",
    "trace.missing": "trace.missing", "trace.ambiguous": "trace.ambiguous",
    "clock.episode_domain_mismatch": "clock.mapping_domain_mismatch",
}


def joule_bar(lane_est, twin_est, value: float) -> float:
    """1% of the smaller printed half-width; 1e-6 relative where none is usable."""
    smallest = min(lane_est.half_width_j, twin_est.half_width_j)
    if 0 < smallest < math.inf:
        return 0.01 * smallest
    return 1e-6 * max(1.0, abs(value))


def fraction(method: str) -> float | None:
    for item in method.split(";")[1:]:
        name, value = item.split("=", 1)
        if name in ("duty.uncovered", "duty.uncovered_fraction"):
            return float(value)
    return None


@unittest.skipUnless(lane is not None, "lane module joulewise.align.attribution not on this branch")
class ProductionWorldAgreement(unittest.TestCase):
    # Six seeds per sensor shape; the 1 kHz rail's 0.6 M-sample episodes are
    # slow in pure Python, so it runs two (each still ~100 segments).
    SEEDS = {shape: range(2) if shape == "ina3221" else range(6) for shape in SHAPES}

    def compare(self, record: Episode, idle: float = 0.0) -> dict[str, float]:
        trace = record.power_traces[0]
        mapping = record.clock_mappings[0] if record.clock_mappings else None
        got = lane.attribute_episode(record, source=trace.source, channel=trace.channel,
                                     idle_watts=idle)
        ref = twin.attribute_episode(record, source=trace.source, channel=trace.channel,
                                     idle_watts=idle)
        self.assertEqual([(s.turn, s.kind, s.start_ns, s.end_ns) for s in got.segments],
                         [(s.turn, s.kind, s.start_ns, s.end_ns) for s in ref.segments])
        lane_episode = {f for f in got.flags if f in EPISODE_FLAG_MAP}
        twin_episode = {f for f in ref.flags if f in EPISODE_FLAG_MAP.values()}
        self.assertEqual({EPISODE_FLAG_MAP[f] for f in lane_episode}, twin_episode)
        worst = dict(joule_ratio=0.0, width_rel=0.0, n=0)
        pairs = [(got.total, ref.total, record.start_ns, record.end_ns)]
        pairs += [(g.energy, r.energy, g.start_ns, g.end_ns)
                  for g, r in zip(got.segments, ref.segments)]
        for g, r, t0, t1 in pairs:
            worst["n"] += 1
            bar = joule_bar(g, r, g.joules)
            self.assertLessEqual(abs(g.joules - r.joules), bar, (t0, t1, g, r))
            worst["joule_ratio"] = max(worst["joule_ratio"], abs(g.joules - r.joules) / bar)
            self.assertEqual(g.method.split(";")[0], r.method.split(";")[0])
            self.assertEqual(fraction(g.method), fraction(r.method))  # Same integers, one division.
            self.assertEqual({FLAG_MAP[f] for f in g.flags if f in FLAG_MAP},
                             {f for f in r.flags if f in FLAG_MAP.values()}, (t0, t1))
            # The lane's period flag is exact integer arithmetic on the record.
            self.assertEqual("segment.shorter_than_period" in g.flags,
                             t1 - t0 < trace.nominal_interval_ns)
            expected = lane_reading_half_width(trace, mapping, t0, t1)
            if g is got.total and trace.unit == "W" and trace.averaging_window_ns is None:
                # Independent per-tile reconstruction retains all point phase
                # edges. The episode takes max(own, summed tile bounds).
                expected = max(expected, math.fsum(lane_reading_half_width(
                    trace, mapping, s.start_ns, s.end_ns) for s in ref.segments))
            width_bar = 1e-6 * max(1.0, expected)  # No printed uncertainty: 1e-6 rule.
            self.assertLessEqual(abs(g.half_width_j - expected), width_bar, (t0, t1, g))
            if expected > 0:
                worst["width_rel"] = max(worst["width_rel"],
                                         abs(g.half_width_j - expected) / expected)
        # Segments tile and conserve: the total equals the segment sum up to
        # accumulation, 16 roundings per trace sample and segment (each
        # trapezoid is a handful of operations) times the summed magnitude.
        gamma = 16 * (len(trace.t_ns) + len(got.segments) + 1) * 2.0**-52
        self.assertLessEqual(abs(math.fsum(s.energy.joules for s in got.segments) - got.total.joules),
                             gamma * math.fsum(abs(s.energy.joules) for s in got.segments))
        return worst

    def test_twenty_turn_worlds_every_sensor_shape(self):
        for shape, platform in SHAPES.items():
            for seed in self.SEEDS[shape]:
                with self.subTest(shape=shape, seed=seed):
                    world = make_world(seed, platform)
                    record = episode_with(world, shape, seed)
                    self.assertEqual(
                        [(s.turn, s.kind, s.start_ns, s.end_ns) for s in
                         lane.attribute_episode(record, source=record.power_traces[0].source,
                                                channel=record.power_traces[0].channel).segments],
                        world.expected)
                    self.compare(record)

    def test_idle_subtraction_and_turn_counts(self):
        for shape, platform in SHAPES.items():
            for n_turns in ((1,) if shape == "ina3221" else (1, 32)):
                with self.subTest(shape=shape, turns=n_turns):
                    world = make_world(100 + n_turns, platform, n_turns=n_turns)
                    record = episode_with(world, shape, 100 + n_turns)
                    # The fixture's idle level as idle_watts: full coverage, so
                    # the requested and observed readings coincide.
                    self.compare(record, idle=world.truth.p[0])

    def test_empty_episode_and_constant_power(self):
        for shape, platform in SHAPES.items():
            with self.subTest(shape=shape):
                world = make_world(7, platform, n_turns=0)
                self.assertEqual([s[1] for s in world.expected], ["gap"])
                record = episode_with(world, shape, 7)
                self.compare(record)

    def test_interval_ends_tied_to_samples_and_window_edges(self):
        # Query ends exactly on a sample, on a window start (t_k - w), one
        # nanosecond either side, and both ends inside one sample interval.
        for shape, platform in SHAPES.items():
            if shape == "ina3221":
                continue  # Its ties are the same point-trace code as nvml_energy's spans.
            with self.subTest(shape=shape):
                world = make_world(9, platform)
                record = episode_with(world, shape, 9)
                trace = record.power_traces[0]
                mapping = record.clock_mappings[0] if record.clock_mappings else None
                offset = mapping.offset_ns if mapping is not None else 0
                w = trace.averaging_window_ns or 0
                k = len(trace.t_ns) // 2
                t = [x + offset for x in trace.t_ns]
                ends = sorted({t[k], t[k] - w, t[k] + 1, t[k] - 1, t[k] - w + 1, t[k] - w - 1,
                               (t[k] + t[k + 1]) // 2, t[k + 1] - 1, t[k + 3]})
                for a in ends:
                    for b in ends:
                        if b <= a:
                            continue
                        got = lane.trace_energy(trace, a, b, mapping=mapping)
                        ref = twin.trace_energy(trace, a, b, mapping=mapping)
                        self.assertLessEqual(abs(got.joules - ref.joules), joule_bar(got, ref, got.joules),
                                             (shape, a - t[k], b - t[k]))
                        expected = lane_reading_half_width(trace, mapping, a, b)
                        self.assertLessEqual(abs(got.half_width_j - expected), 1e-6 * max(1.0, expected),
                                             (shape, a - t[k], b - t[k], got, expected))


@unittest.skipUnless(lane is not None, "lane module joulewise.align.attribution not on this branch")
class KnownReadingDifferences(unittest.TestCase):
    """Hand-computed cases where the two readings differ by design."""

    def trace(self, times, values, **kw):
        fields = dict(source="mock", channel="c", clock_domain="host", t_ns=tuple(times),
                      values=tuple(values), unit="W", nominal_interval_ns=NS, resolution=0.001)
        fields.update(kw)
        if fields["source"] == "nvml_energy":
            fields.setdefault("notes",json.dumps({"unknown_sensor_age_bound_ns":0}))
        return PowerTrace(**fields)

    def test_partial_coverage_idle_reading(self):
        # 50 W from 10 s to 20 s, idle 30 W, query [5, 15] s. Observed gross
        # 250 J. Lane subtracts idle over 10 s: -50 J; twin over the 5 s
        # overlap: 100 J. Both print 5 s * 50 W = 250 J of coverage width.
        sensor = self.trace(range(10 * NS, 20 * NS + 1, NS), [50.0] * 11)
        got = lane.trace_energy(sensor, 5 * NS, 15 * NS, idle_watts=30.0)
        ref = twin.trace_energy(sensor, 5 * NS, 15 * NS, idle_watts=30.0)
        self.assertEqual((got.joules, ref.joules), (250.0 - 300.0, 250.0 - 150.0))
        self.assertIn("trace.partial_coverage", got.flags)

    def test_implausible_counter_drop(self):
        # 300 W in 100 ms polls on a 5 MJ baseline, one reading 1 mJ low.
        # The lane counts the dip as no work (decrease); the twin restarts
        # from zero and counts the 5 MJ baseline.
        times = range(0, 2 * NS + 1, NS // 10)
        values = [5e6 + 30.0 * k for k in range(len(times))]
        values[10] = values[9] - 0.001
        sensor = self.trace(times, values, source="nvml_energy", unit="J_cumulative")
        got = lane.trace_energy(sensor, 0, 2 * NS)
        ref = twin.trace_energy(sensor, 0, 2 * NS)
        # Hand count: the dip poll counts 0 J and the recovery poll counts
        # 60.001 J, so the lane sums 600.001 J. No printed width is usable
        # here as a bar (it is one 60 J poll), so the 1e-6 relative rule applies.
        self.assertLessEqual(abs(got.joules - 600.001), 1e-6 * 600.001)
        self.assertIn("counter.decrease", got.flags)
        # The twin's restart reading adds the dip reading itself (5 MJ baseline).
        self.assertGreater(ref.joules, 5e6)

    def test_missing_trace_and_overlap_widths(self):
        record = make_world(3, "gpu").episode
        got = lane.attribute_episode(record, source="nvml_power", channel="absent")
        ref = twin.attribute_episode(record, source="nvml_power", channel="absent")
        self.assertTrue(math.isinf(got.total.half_width_j))
        self.assertEqual(ref.total.half_width_j, 0.0)
        self.assertEqual(got.total.joules, ref.total.joules)


if __name__ == "__main__":
    unittest.main()
