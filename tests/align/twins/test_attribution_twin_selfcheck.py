"""Self-checks of the attribution twin (tests/align/twins/attribution_twin.py).

Closed-form and hand-computable cases, then a production-shaped synthetic
episode run end to end through ``attribute_episode`` on four sensor shapes.
These check the twin against arithmetic done by hand, not against lane A4's
module; the comparison of the two lives elsewhere.

Bars. Every comparison of two float computations uses ``float_bar``: a
first-order bound on accumulated rounding, derived below from the number of
terms and the magnitude. Integers (times, segment boundaries) and flag sets
are compared exactly, since there bit identity is the real property.
"""

from __future__ import annotations

import bisect
import math
import random
import sys
import unittest

from joulewise.align.records import ClockMapping, Episode, PowerTrace, ToolCall, Turn
from tests.align.twins.attribution_twin import (
    EnergyEstimate,
    attribute_episode,
    split_method,
    trace_energy,
)

MS = 1_000_000  # ns per millisecond
S = 1_000_000_000  # ns per second

# One floating-point rounding errs by at most EPS/2 relative to the value rounded.
EPS = sys.float_info.epsilon
# Upper count of rounded operations behind one integrated piece in either
# computation compared: two straight-line interpolations (3 each), the mean of
# the two end values (2), the product with the duration (1), the ns -> s
# division (1), the accumulation into the sum (1) = 11; 12 leaves one spare.
ROUNDINGS_PER_TERM = 12


def float_bar(n_terms: int, magnitude: float) -> float:
    """First-order bound on the rounding difference between two float computations.

    ``n_terms`` pieces, each carrying at most ROUNDINGS_PER_TERM roundings of
    relative size EPS/2 on a value no larger than ``magnitude`` (joules), in
    each of the two computations (factor 2):
    2 * n_terms * ROUNDINGS_PER_TERM * EPS/2 * magnitude.
    """
    return n_terms * ROUNDINGS_PER_TERM * EPS * magnitude


def w_trace(times_ns, watts, *, window_ns=None, resolution=None, domain="host", source="mock",
            channel="gpu0", interval_ns=100 * MS) -> PowerTrace:
    return PowerTrace(source=source, channel=channel, clock_domain=domain, t_ns=tuple(times_ns),
                      values=tuple(float(v) for v in watts), unit="W", nominal_interval_ns=interval_ns,
                      averaging_window_ns=window_ns, resolution=resolution)


def counter_trace(times_ns, joules, *, resolution=None, domain="host", channel="gpu0",
                  interval_ns=100 * MS) -> PowerTrace:
    return PowerTrace(source="nvml_energy", channel=channel, clock_domain=domain, t_ns=tuple(times_ns),
                      values=tuple(float(v) for v in joules), unit="J_cumulative",
                      nominal_interval_ns=interval_ns, resolution=resolution)


def mapping(offset_ns=0, uncertainty_ns=0, trace_domain="host", episode_domain="host") -> ClockMapping:
    return ClockMapping(trace_domain=trace_domain, episode_domain=episode_domain, offset_ns=offset_ns,
                        uncertainty_ns=uncertainty_ns, method="test")


GRID_0_10S = [k * 100 * MS for k in range(101)]  # 0 .. 10 s every 100 ms


def ramp_watts(times_ns, origin_ns=0):
    """P(t) = 50 W + 10 W/s * (t - origin) in seconds."""
    return [50.0 + 10.0 * ((t - origin_ns) / S) for t in times_ns]


def ramp_joules(a_s: float, b_s: float) -> float:
    """Closed form of the ramp's integral over [a, b] seconds."""
    return 50.0 * (b_s - a_s) + 5.0 * (b_s * b_s - a_s * a_s)


class TrapezoidClosedForm(unittest.TestCase):

    def test_constant_power(self):
        est = trace_energy(w_trace(GRID_0_10S, [100.0] * 101), 250 * MS, 7600 * MS)
        # 100 W over 7.35 s; 75 sample intervals plus 2 partial pieces.
        self.assertLessEqual(abs(est.joules - 735.0), float_bar(80, 735.0))
        self.assertLessEqual(abs(est.half_width_j), float_bar(4, 100.0 * 0.1))  # interpolation of a constant is 0
        self.assertEqual(est.method, "trapezoid_W")
        self.assertEqual(set(est.flags), {"half_width.missing.clock", "half_width.missing.resolution"})

    def test_ramp_energy_and_every_half_width_term(self):
        trace = w_trace(GRID_0_10S, ramp_watts(GRID_0_10S), resolution=0.01)
        est = trace_energy(trace, 350 * MS, 8720 * MS, mapping=mapping(uncertainty_ns=1 * MS))
        expected = ramp_joules(0.35, 8.72)  # 798.0795 J; the trapezoid is exact on a line
        self.assertLessEqual(abs(est.joules - expected), float_bar(90, 900.0))
        # (ii) start end 0.35 s in [0.3, 0.4]: hold-minus-line over [0.35, 0.4] is
        # slope*((0.1)^2 - (0.05)^2)/2 = 10*0.0075/2 = 0.0375 J, half 0.01875 J;
        # stop end 8.72 s in [8.7, 8.8]: 10*(0.02)^2/2 = 0.002 J, half 0.001 J.
        interpolation = 0.01875 + 0.001
        # (i) adjacent samples 53 W, 54 W and 137 W, 138 W; 1 ms each end.
        clock = (54.0 + 138.0) * 0.001
        # (iii) 0.01 W over 8.37 s.
        resolution = 0.01 * 8.37
        # Magnitude: the largest intermediate is one hold energy, 138 W * 0.1 s.
        self.assertLessEqual(abs(est.half_width_j - (interpolation + clock + resolution)), float_bar(10, 13.8))
        self.assertEqual(est.flags, ())

    def test_clock_term_takes_three_samples_when_an_end_is_on_a_sample(self):
        # Samples 10, 40, 20, 30 W at 0, 1, 2, 3 s; interval [1 s, 2.5 s], 10 ms uncertainty.
        trace = w_trace([0, 1 * S, 2 * S, 3 * S], [10, 40, 20, 30], interval_ns=S)
        est = trace_energy(trace, 1 * S, 2500 * MS, mapping=mapping(uncertainty_ns=10 * MS))
        # Energy: [1, 2] s: (40+20)/2 = 30 J; [2, 2.5] s: (20+25)/2*0.5 = 11.25 J.
        self.assertLessEqual(abs(est.joules - 41.25), float_bar(4, 41.25))
        # Clock: end 1 s is sample 1 -> samples {0, 1, 2} -> 40 W; end 2.5 s -> {2, 3} -> 30 W.
        clock = (40.0 + 30.0) * 0.010
        # Interpolation: start on a sample -> 0; stop end piece [2, 2.5]: hold 20*0.5 = 10 J,
        # line 11.25 J, half the difference 0.625 J.
        self.assertLessEqual(abs(est.half_width_j - (clock + 0.625)), float_bar(6, 40.0))
        self.assertEqual(est.flags, ("half_width.missing.resolution",))

    def test_both_ends_in_one_sample_interval_count_twice(self):
        trace = w_trace([0, 1 * S, 2 * S, 3 * S], [10, 40, 20, 30], interval_ns=S)
        est = trace_energy(trace, 2200 * MS, 2600 * MS)
        # P(2.2) = 22 W, P(2.6) = 26 W: 24 W * 0.4 s = 9.6 J. Hold 20 W * 0.4 s = 8 J,
        # difference 1.6 J, half 0.8 J at each end (R8) -> 1.6 J.
        self.assertLessEqual(abs(est.joules - 9.6), float_bar(2, 9.6))
        self.assertLessEqual(abs(est.half_width_j - 1.6), float_bar(4, 9.6))

    def test_zero_length_interval(self):
        est = trace_energy(w_trace(GRID_0_10S, [100.0] * 101), 5 * S, 5 * S)
        self.assertEqual(est.joules, 0.0)  # no reading taken: exact zero by construction (R9)
        self.assertEqual(est.half_width_j, 0.0)

    def test_reversed_interval_raises(self):
        with self.assertRaises(ValueError):
            trace_energy(w_trace(GRID_0_10S, [100.0] * 101), 5 * S, 4 * S)


class WindowClosedForm(unittest.TestCase):

    def test_square_wave_whole_window_is_exact(self):
        # 0/200 W square wave, high on [2m+1, 2m+2) s; 100 ms whole-window sensor
        # (duty 1) sampling at 0.1 .. 6.0 s, so every window lies inside one level.
        times = [k * 100 * MS for k in range(1, 61)]
        watts = [200.0 if ((t - 50 * MS) // S) % 2 == 1 else 0.0 for t in times]
        est = trace_energy(w_trace(times, watts, window_ns=100 * MS), 50 * MS, 5550 * MS)
        # High parts inside [0.05, 5.55] s: [1, 2], [3, 4], [5, 5.55] = 2.55 s at 200 W.
        self.assertLessEqual(abs(est.joules - 510.0), float_bar(60, 510.0))
        self.assertEqual(est.method, "window_average_W")
        self.assertNotIn("duty.uncovered", est.flags)
        # Start end 0.05 s precedes the first sample (no partial sample interval);
        # stop end 5.55 s lies between two 200 W samples, where hold equals line.
        self.assertLessEqual(abs(est.half_width_j), float_bar(2, 200.0 * 0.1))

    def test_quarter_duty_constant_power(self):
        # NVML-like: 100 ms period, 25 ms window ending at each sample.
        times = [k * 100 * MS for k in range(1, 101)]
        est = trace_energy(w_trace(times, [100.0] * 100, window_ns=25 * MS), 100 * MS, 10 * S)
        self.assertLessEqual(abs(est.joules - 990.0), float_bar(200, 990.0))
        # Windows of samples 2..100 lie inside [0.1, 10] s: 99 * 25 ms = 2.475 s of 9.9 s,
        # uncovered 7.425/9.9 = 0.75 exactly (both are integers of ns; the ratio is exact).
        self.assertEqual(est.method, "window_average_W;duty.uncovered=0.75")
        self.assertEqual(split_method(est.method), ("window_average_W", {"duty.uncovered": 0.75}))
        self.assertIn("duty.uncovered", est.flags)

    def test_two_samples_hand_computed(self):
        # Samples 10 W at 100 ms and 30 W at 200 ms, 25 ms windows: pieces are
        # [75, 100] 10 W held, [100, 175] line 10 -> 30 W (uncovered), [175, 200] 30 W held.
        trace = w_trace([100 * MS, 200 * MS], [10, 30], window_ns=25 * MS)
        whole = trace_energy(trace, 75 * MS, 200 * MS)
        # 10*0.025 + 20*0.075 + 30*0.025 = 0.25 + 1.5 + 0.75 = 2.5 J; uncovered 75/125 = 0.6.
        self.assertLessEqual(abs(whole.joules - 2.5), float_bar(3, 2.5))
        self.assertEqual(split_method(whole.method)[1], {"duty.uncovered": 75 / 125})
        self.assertNotIn("trace.partial_coverage", whole.flags)  # starts exactly at the first window

        inner = trace_energy(trace, 90 * MS, 180 * MS)
        # 10*0.010 + 1.5 + 30*0.005 = 1.75 J; uncovered 75/90.
        self.assertLessEqual(abs(inner.joules - 1.75), float_bar(3, 2.5))
        self.assertEqual(split_method(inner.method)[1], {"duty.uncovered": 75 / 90})
        # Interpolation on the raw samples: stop end 180 ms in [100, 200] ms; piece
        # [100, 180]: hold 10*0.08 = 0.8 J, line (10+26)/2*0.08 = 1.44 J, half 0.32 J.
        self.assertLessEqual(abs(inner.half_width_j - 0.32), float_bar(4, 1.44))

    def test_overlapping_windows_count_each_instant_once(self):
        # 150 ms windows on a 100 ms period: sample 1 holds only (100, 200] ms.
        trace = w_trace([100 * MS, 200 * MS], [10, 30], window_ns=150 * MS)
        est = trace_energy(trace, -50 * MS, 200 * MS)
        # 10 W over [-50, 100] ms + 30 W over [100, 200] ms = 1.5 + 3.0 = 4.5 J.
        self.assertLessEqual(abs(est.joules - 4.5), float_bar(2, 4.5))
        self.assertEqual(est.method, "window_average_W")

    def test_partial_coverage_before_the_first_window(self):
        trace = w_trace([100 * MS, 200 * MS], [10, 30], window_ns=25 * MS)
        est = trace_energy(trace, 74 * MS, 200 * MS)
        self.assertIn("trace.partial_coverage", est.flags)
        # The uncovered 1 ms adds 1 ms * peak 30 W = 0.03 J to the 0 J interpolation term
        # (start end before the first sample, stop end on a sample).
        self.assertLessEqual(abs(est.half_width_j - 0.03), float_bar(2, 0.03))
        self.assertLessEqual(abs(est.joules - 2.5), float_bar(3, 2.5))


class CounterClosedForm(unittest.TestCase):

    def test_constant_power_counter(self):
        joules = [1000.0 + 100.0 * (t / S) for t in GRID_0_10S]  # 100 W from 1000 J
        trace = counter_trace(GRID_0_10S, joules, resolution=0.001)
        est = trace_energy(trace, 350 * MS, 8720 * MS)
        # Magnitude: the counter's own value (about 1.9 kJ) is what is rounded.
        self.assertLessEqual(abs(est.joules - 837.0), float_bar(4, 2000.0))
        self.assertEqual(est.method, "counter_J")
        # Interpolation: start piece [0.35, 0.4] of a 10 J step: hold 10 J, line 5 J, half 2.5 J;
        # stop piece [8.7, 8.72]: hold 0 J, line 2 J, half 1.0 J. Resolution: 2 * 0.001 J.
        self.assertLessEqual(abs(est.half_width_j - (2.5 + 1.0 + 0.002)), float_bar(6, 2000.0))

        timed = trace_energy(trace, 350 * MS, 8720 * MS, mapping=mapping(uncertainty_ns=1 * MS))
        # Clock: the step touching each end runs at 100 W; 1 ms each end adds 0.1 J twice.
        self.assertLessEqual(abs(timed.half_width_j - (3.502 + 0.2)), float_bar(8, 2000.0))

    def test_counter_restart_is_flagged_and_read_as_restart_from_zero(self):
        trace = counter_trace([0, S, 2 * S, 3 * S, 4 * S], [100, 200, 300, 50, 150], interval_ns=S)
        whole = trace_energy(trace, 0, 4 * S)
        # Steps 100, 100, 50 (restart: the later reading), 100 J -> 350 J.
        self.assertLessEqual(abs(whole.joules - 350.0), float_bar(4, 450.0))
        self.assertIn("counter.wrap", whole.flags)
        inner = trace_energy(trace, 500 * MS, 3500 * MS)
        # Unwrapped series 100, 200, 300, 350, 450: U(3.5) - U(0.5) = 400 - 150 = 250 J.
        self.assertLessEqual(abs(inner.joules - 250.0), float_bar(4, 450.0))

    def test_counter_partial_coverage(self):
        trace = counter_trace([0, S, 2 * S, 3 * S, 4 * S], [100, 200, 300, 50, 150], interval_ns=S)
        est = trace_energy(trace, -1 * S, 5 * S)
        self.assertLessEqual(abs(est.joules - 350.0), float_bar(4, 450.0))
        self.assertIn("trace.partial_coverage", est.flags)
        # 2 s uncovered at the peak step power 100 W; both covered ends sit on samples.
        self.assertLessEqual(abs(est.half_width_j - 200.0), float_bar(2, 200.0))


class MappingAndCoverage(unittest.TestCase):

    def test_positive_offset(self):
        trace = w_trace(GRID_0_10S, ramp_watts(GRID_0_10S), domain="meter")
        m = mapping(offset_ns=5 * S, uncertainty_ns=0, trace_domain="meter")
        est = trace_energy(trace, 5350 * MS, 13720 * MS, mapping=m)
        self.assertLessEqual(abs(est.joules - ramp_joules(0.35, 8.72)), float_bar(90, 900.0))
        self.assertLessEqual(abs(est.half_width_j - (0.01875 + 0.001)), float_bar(4, 13.8))
        self.assertEqual(est.flags, ("half_width.missing.resolution",))  # u = 0 is a value, not a gap

    def test_negative_offset_at_monotonic_clock_scale(self):
        # The meter's clock reads 2 h since boot where the episode's reads 1 h.
        origin = 7200 * S
        times = [origin + k * 100 * MS for k in range(101)]
        trace = w_trace(times, ramp_watts(times, origin), domain="meter")
        m = mapping(offset_ns=-3600 * S, uncertainty_ns=0, trace_domain="meter")
        est = trace_energy(trace, 3600 * S + 350 * MS, 3600 * S + 8720 * MS, mapping=m)
        self.assertLessEqual(abs(est.joules - ramp_joules(0.35, 8.72)), float_bar(90, 900.0))

    def test_partial_coverage_and_idle(self):
        times = [S + k * 100 * MS for k in range(81)]  # 1 .. 9 s
        trace = w_trace(times, [100.0] * 81)
        est = trace_energy(trace, 0, 10 * S)
        self.assertLessEqual(abs(est.joules - 800.0), float_bar(80, 800.0))
        self.assertLessEqual(abs(est.half_width_j - 200.0), float_bar(2, 200.0))  # 2 s * 100 W
        self.assertIn("trace.partial_coverage", est.flags)
        idle = trace_energy(trace, 0, 10 * S, idle_watts=20.0)
        # Idle over the 8 s overlap (R6): 800 - 160 = 640 J.
        self.assertLessEqual(abs(idle.joules - 640.0), float_bar(82, 800.0))
        outside = trace_energy(trace, 10 * S, 12 * S)
        self.assertEqual(outside.joules, 0.0)  # empty overlap: nothing integrated (exact by construction)
        self.assertLessEqual(abs(outside.half_width_j - 200.0), float_bar(2, 200.0))

    def test_idle_subtraction_full_coverage(self):
        est = trace_energy(w_trace(GRID_0_10S, [100.0] * 101), 0, 10 * S, idle_watts=30.0)
        self.assertLessEqual(abs(est.joules - 700.0), float_bar(102, 1000.0))

    def test_empty_trace(self):
        est = trace_energy(w_trace([], []), 0, S)
        self.assertEqual(est.joules, 0.0)
        self.assertEqual(est.half_width_j, 0.0)
        self.assertTrue({"trace.empty", "trace.partial_coverage", "half_width.missing.coverage"} <= set(est.flags))

    def test_mapping_for_another_domain_is_flagged(self):
        trace = w_trace(GRID_0_10S, [100.0] * 101, domain="meter")
        est = trace_energy(trace, 0, S, mapping=mapping(trace_domain="other"))
        self.assertIn("clock.mapping_domain_mismatch", est.flags)


def _turn(index, start, end, first=None, calls=()):
    return Turn(index=index, start_ns=start, end_ns=end, context_tokens=100 * index, prefill_tokens=100,
                decode_tokens=50, first_token_ns=first, tool_calls=tuple(calls))


def _call(start, end, name="tool"):
    return ToolCall(name=name, start_ns=start, end_ns=end, args_bytes=10, result_bytes=100)


def _episode(turns, traces, mappings=(), start=0, end=10 * S):
    return Episode(episode_id="ep-test", task_pair="shade/synthetic", condition="benign", agent_model="synthetic",
                   endpoint="mock", seed=0, clock_domain="host", start_ns=start, end_ns=end, turns=tuple(turns),
                   power_traces=tuple(traces), clock_mappings=tuple(mappings))


def _layout(attr):
    return [(s.kind, s.turn, s.start_ns, s.end_ns) for s in attr.segments]


class AttributeEpisodeHand(unittest.TestCase):

    TURNS = (
        _turn(0, 1 * S, 4 * S, first=1500 * MS, calls=[_call(2 * S, 2500 * MS)]),
        _turn(1, 5 * S, 8 * S, first=None, calls=[_call(8500 * MS, 9 * S)]),
    )
    LAYOUT = [
        ("gap", None, 0, 1 * S),
        ("prefill", 0, 1 * S, 1500 * MS),
        ("decode", 0, 1500 * MS, 2 * S),
        ("tool", 0, 2 * S, 2500 * MS),
        ("decode", 0, 2500 * MS, 4 * S),
        ("gap", None, 4 * S, 5 * S),
        ("decode", 1, 5 * S, 8 * S),
        ("gap", None, 8 * S, 8500 * MS),
        ("tool", 1, 8500 * MS, 9 * S),
        ("gap", None, 9 * S, 10 * S),
    ]

    def test_layout_and_constant_power(self):
        trace = w_trace(GRID_0_10S, [100.0] * 101, source="nvml_power")
        attr = attribute_episode(_episode(self.TURNS, [trace]), source="nvml_power", channel="gpu0")
        self.assertEqual(_layout(attr), self.LAYOUT)
        self.assertEqual(attr.flags, ("turn.no_first_token",))
        self.assertEqual((attr.episode_id, attr.channel), ("ep-test", "gpu0"))
        for seg in attr.segments:
            expected = 100.0 * (seg.end_ns - seg.start_ns) / S
            self.assertLessEqual(abs(seg.energy.joules - expected), float_bar(40, 1000.0))
        self.assertLessEqual(abs(attr.total.joules - 1000.0), float_bar(102, 1000.0))

    def test_ramp_segments_match_closed_form_and_sum_to_total(self):
        trace = w_trace([2 * S + t for t in GRID_0_10S], ramp_watts(GRID_0_10S), domain="meter",
                        source="nvml_power")
        m = ClockMapping(trace_domain="meter", episode_domain="host", offset_ns=-2 * S, uncertainty_ns=1 * MS,
                         method="test")
        attr = attribute_episode(_episode(self.TURNS, [trace], [m]), source="nvml_power", channel="gpu0",
                                 idle_watts=40.0)
        self.assertEqual(_layout(attr), self.LAYOUT)
        for seg in attr.segments:
            a, b = seg.start_ns / S, seg.end_ns / S
            expected = ramp_joules(a, b) - 40.0 * (b - a)
            self.assertLessEqual(abs(seg.energy.joules - expected), float_bar(40, 1000.0))
            # Clock term is present at every segment end (1 ms * adjacent peak).
            self.assertNotIn("half_width.missing.clock", seg.energy.flags)
        expected_total = ramp_joules(0.0, 10.0) - 400.0  # 1000 - 400 = 600 J
        self.assertLessEqual(abs(attr.total.joules - expected_total), float_bar(102, 1400.0))
        # Sum of 10 segment energies against the total: 10 sums plus 100 sample intervals
        # plus 2 partial pieces per segment.
        summed = sum(s.energy.joules for s in attr.segments)
        self.assertLessEqual(abs(summed - attr.total.joules), float_bar(130, 1400.0))

    def test_tool_precedence_overlap_and_clipping(self):
        turns = (
            _turn(0, 1 * S, 4 * S, first=1500 * MS,
                  calls=[_call(1200 * MS, 1400 * MS), _call(3 * S, 3600 * MS), _call(3500 * MS, 3800 * MS)]),
            _turn(1, 5 * S, 8 * S, first=6 * S, calls=[_call(9500 * MS, 11 * S), _call(7 * S, 7 * S)]),
        )
        trace = w_trace(GRID_0_10S, [100.0] * 101, source="nvml_power")
        attr = attribute_episode(_episode(turns, [trace]), source="nvml_power", channel="gpu0")
        self.assertEqual(_layout(attr), [
            ("gap", None, 0, 1 * S),
            ("prefill", 0, 1 * S, 1200 * MS),
            ("tool", 0, 1200 * MS, 1400 * MS),
            ("prefill", 0, 1400 * MS, 1500 * MS),
            ("decode", 0, 1500 * MS, 3 * S),
            ("tool", 0, 3 * S, 3600 * MS),
            ("tool", 0, 3600 * MS, 3800 * MS),
            ("decode", 0, 3800 * MS, 4 * S),
            ("gap", None, 4 * S, 5 * S),
            ("prefill", 1, 5 * S, 6 * S),
            ("decode", 1, 6 * S, 8 * S),  # the zero-length call at 7 s leaves no segment
            ("gap", None, 8 * S, 9500 * MS),
            ("tool", 1, 9500 * MS, 10 * S),  # clipped at the episode end
        ])
        self.assertEqual(set(attr.flags), {"tool.overlap", "tool.outside_episode"})

    def test_missing_trace_is_a_flag(self):
        attr = attribute_episode(_episode(self.TURNS, []), source="nvml_power", channel="gpu0")
        self.assertEqual(_layout(attr), self.LAYOUT)
        self.assertIn("trace.missing", attr.flags)
        self.assertEqual(attr.total, EnergyEstimate(0.0, 0.0, "none", ("trace.missing",)))


# ---------------------------------------------------------------- production-shaped world

BASE_WATTS = {"gap": 70.0, "tool": 90.0, "prefill": 380.0, "decode": 260.0}  # synthetic GPU levels


def _log_uniform_ns(rng, lo_ns, hi_ns):
    return int(math.exp(rng.uniform(math.log(lo_ns), math.log(hi_ns))))


class _World:
    """A twenty-turn agent episode with a known piecewise-constant true power timeline."""

    def __init__(self, seed: int):
        rng = random.Random(seed)
        self.e0 = 3600 * S + rng.randrange(S)  # monotonic clock about an hour after boot
        self.tiles: list[list] = []  # [kind, turn, start, end]
        self.t = self.e0
        turns = []
        self._tile("gap", None, rng.randrange(500 * MS, 2 * S))
        for i in range(20):
            start = self.t
            prefill_tokens = rng.randrange(200, 4000)
            self._tile("prefill", i, prefill_tokens * rng.randrange(50_000, 200_000))  # 50-200 us per token
            first = self.t
            decode_tokens = rng.randrange(40, 600)
            decode_ns = decode_tokens * rng.randrange(20 * MS, 40 * MS)  # 20-40 ms per token
            calls = []
            if rng.random() < 0.25:  # a call made while the turn is still generating
                split = rng.randrange(decode_ns // 4, 3 * decode_ns // 4)
                self._tile("decode", i, split)
                calls.append(self._call(i, _log_uniform_ns(rng, 200 * MS, 2 * S)))
                self._tile("decode", i, decode_ns - split)
            else:
                self._tile("decode", i, decode_ns)
            end = self.t
            if rng.random() < 0.8:  # the usual case: the agent runs a tool between model calls
                self._tile("gap", None, rng.randrange(5 * MS, 50 * MS))
                calls.append(self._call(i, _log_uniform_ns(rng, 200 * MS, 30 * S)))
            self._tile("gap", None, rng.randrange(5 * MS, 50 * MS))
            turns.append(Turn(index=i, start_ns=start, end_ns=end, context_tokens=1000 * i,
                              prefill_tokens=prefill_tokens, decode_tokens=decode_tokens, first_token_ns=first,
                              tool_calls=tuple(calls)))
        self._tile("gap", None, rng.randrange(500 * MS, 2 * S))
        self.e1 = self.t
        self.turns = tuple(turns)
        self.levels = [BASE_WATTS[kind] * (1.0 + rng.uniform(-0.1, 0.1)) for kind, _, _, _ in self.tiles]
        self.starts = [tile[2] for tile in self.tiles]
        self.rng = rng

    def _tile(self, kind, turn, duration_ns):
        if kind == "gap" and self.tiles and self.tiles[-1][0] == "gap":
            self.tiles[-1][3] += duration_ns
        else:
            self.tiles.append([kind, turn, self.t, self.t + duration_ns])
        self.t += duration_ns

    def _call(self, turn, duration_ns):
        start = self.t
        self._tile("tool", turn, duration_ns)
        return ToolCall(name="search", start_ns=start, end_ns=self.t, args_bytes=120, result_bytes=4000)

    def watts_at(self, t):
        """True power at instant t (right-continuous; first/last level held outside the episode)."""
        i = min(max(bisect.bisect_right(self.starts, t) - 1, 0), len(self.tiles) - 1)
        return self.levels[i]

    def joules(self, x, y):
        """Exact integral of the true power over [x, y] ns."""
        total = 0.0
        for i, (_, _, start, end) in enumerate(self.tiles):
            lo = max(x, -math.inf if i == 0 else start)
            hi = min(y, math.inf if i == len(self.tiles) - 1 else end)
            if hi > lo:
                total += self.levels[i] * (hi - lo) / S
        return total

    def sample_times(self, interval_ns, phase_ns):
        first = self.e0 - S + phase_ns
        return list(range(first, self.e1 + S, interval_ns))

    def traces(self):
        rng = self.rng
        ina_skew, mac_skew = 123_456_789, -987_654_321  # trace clock minus host clock, ns
        ina_host = self.sample_times(1 * MS, rng.randrange(1 * MS))
        nvml_host = self.sample_times(100 * MS, rng.randrange(100 * MS))
        pm_host = self.sample_times(100 * MS, rng.randrange(100 * MS))
        energy_host = self.sample_times(100 * MS, rng.randrange(100 * MS))
        counter_base = 2.5e6  # J already on the counter (about a day at 30 W)
        ina = PowerTrace(source="ina3221", channel="VDD_IN", clock_domain="jetson",
                         t_ns=tuple(t + ina_skew for t in ina_host),
                         values=tuple(self.watts_at(t) for t in ina_host), unit="W",
                         nominal_interval_ns=1 * MS, resolution=0.04)  # synthetic quantum; bars do not use it
        nvml = PowerTrace(source="nvml_power", channel="gpu0", clock_domain="host", t_ns=tuple(nvml_host),
                          values=tuple(self.joules(t - 25 * MS, t) / 0.025 for t in nvml_host), unit="W",
                          nominal_interval_ns=100 * MS, averaging_window_ns=25 * MS, duty_fraction=0.25,
                          resolution=0.001)  # NVML reports integer milliwatts
        pm = PowerTrace(source="powermetrics", channel="package", clock_domain="mac",
                        t_ns=tuple(t + mac_skew for t in pm_host),
                        values=tuple(self.joules(t - 100 * MS, t) / 0.1 for t in pm_host), unit="W",
                        nominal_interval_ns=100 * MS, averaging_window_ns=100 * MS, duty_fraction=1.0,
                        resolution=0.001)  # powermetrics prints integer milliwatts
        energy = PowerTrace(source="nvml_energy", channel="gpu0", clock_domain="host", t_ns=tuple(energy_host),
                            values=tuple(counter_base + self.joules(energy_host[0], t) for t in energy_host),
                            unit="J_cumulative", nominal_interval_ns=100 * MS, resolution=0.001)  # mJ counter
        mappings = (
            ClockMapping("jetson", "host", -ina_skew, 50_000, "synthetic"),
            ClockMapping("mac", "host", -mac_skew, 1 * MS, "synthetic"),
        )
        return (ina, nvml, pm, energy), mappings

    def episode(self):
        traces, mappings = self.traces()
        return Episode(episode_id="ep-world", task_pair="shade/synthetic", condition="benign",
                       agent_model="synthetic", endpoint="mock", seed=0, clock_domain="host", start_ns=self.e0,
                       end_ns=self.e1, turns=self.turns, power_traces=traces, clock_mappings=mappings)


class ProductionShapedEndToEnd(unittest.TestCase):

    SEEDS = (11, 12)
    SENSORS = (("ina3221", "VDD_IN"), ("nvml_power", "gpu0"), ("powermetrics", "package"), ("nvml_energy", "gpu0"))

    def test_world_through_attribute_episode(self):
        for seed in self.SEEDS:
            world = _World(seed)
            episode = world.episode()
            duration_s = (world.e1 - world.e0) / S
            expected_layout = [tuple(tile) for tile in world.tiles]
            self.assertEqual(len(episode.turns), 20)
            for source, channel in self.SENSORS:
                with self.subTest(seed=seed, source=source):
                    trace = next(t for t in episode.power_traces if t.source == source)
                    attr = attribute_episode(episode, source=source, channel=channel, idle_watts=60.0)
                    # Tiling is integer bookkeeping: exact.
                    self.assertEqual(_layout(attr), expected_layout)
                    # D-078 clause 11 adds a diagnostic only to finite
                    # powermetrics episode totals, not to segment queries.
                    floor_flags = (("powermetrics.attribution_floor",)
                                   if source == "powermetrics" and math.isfinite(attr.total.half_width_j)
                                   else ())
                    self.assertEqual(attr.flags, floor_flags)
                    self.assertNotIn("trace.partial_coverage", attr.total.flags)
                    # Sum of segments against the total (brief: "derive the bar from the number of
                    # terms and the magnitude"). Terms: every sample interval in the episode plus
                    # two partial pieces and one sum per segment. Magnitude: for power traces the
                    # largest |power| (gross or idle) times the duration bounds every partial sum;
                    # for the counter the counter value itself is what is rounded.
                    interval_s = trace.nominal_interval_ns / S
                    n_terms = int(duration_s / interval_s) + 2 + 3 * len(attr.segments)
                    if trace.unit == "J_cumulative":
                        magnitude = max(abs(v) for v in trace.values) * 2
                    else:
                        magnitude = (max(abs(v) for v in trace.values) + 60.0) * duration_s
                    summed = sum(s.energy.joules for s in attr.segments)
                    self.assertLessEqual(abs(summed - attr.total.joules), float_bar(n_terms, magnitude))
                    if source == "nvml_power":
                        base, companions = split_method(attr.total.method)
                        self.assertEqual(base, "window_average_W")
                        # 25 ms windows every 100 ms leave exactly 75 ms of each whole 100 ms
                        # stretch uncovered; only the two stretches cut by the episode ends can
                        # depart from 75 %, each by at most its own length (0.1 s), so the
                        # fraction is within 2 * 0.1 s / duration of 0.75.
                        self.assertLessEqual(abs(companions["duty.uncovered"] - 0.75), 2 * 0.1 / duration_s)

    def test_exact_identities_on_the_world(self):
        world = _World(13)
        episode = world.episode()
        traces = {t.source: t for t in episode.power_traces}
        maps = {m.trace_domain: m for m in episode.clock_mappings}
        duration_s = (world.e1 - world.e0) / S
        true_total = world.joules(world.e0, world.e1)
        peak = max(world.levels)

        # Whole-window sensor over whole windows: the window means reproduce the true
        # integral exactly, whatever the true waveform does inside a window.
        pm = traces["powermetrics"]
        offset = maps["mac"].offset_ns
        host = [t + offset for t in pm.t_ns]
        first = next(k for k, t in enumerate(host) if t - 100 * MS >= world.e0)
        last = max(k for k, t in enumerate(host) if t <= world.e1)
        a, b = host[first] - 100 * MS, host[last]
        est = trace_energy(pm, a, b, mapping=maps["mac"])
        # Bar: one term per window in the twin, one per tile in each truth sum (the window
        # means and the reference), all bounded by peak power times the duration.
        n_terms = last - first + 2 + 2 * len(world.tiles)
        self.assertLessEqual(abs(est.joules - world.joules(a, b)), float_bar(n_terms, peak * duration_s))

        # Energy counter: exact at every sample; the steps holding the episode ends lie in
        # gaps of at least 500 ms, where true power is constant, so the linear
        # interpolation there is exact too.
        # Bar: four counter interpolations on values up to max|U|, plus the truth's own
        # tile sums (one term per tile, up to the true total) on both sides.
        energy = attribute_episode(episode, source="nvml_energy", channel="gpu0").total
        bar = float_bar(4, max(traces["nvml_energy"].values)) + float_bar(len(world.tiles), true_total)
        self.assertLessEqual(abs(energy.joules - true_total), bar)

        # 1 kHz instantaneous sensor: the only error is at each step of the true power,
        # where the line between the two straddling samples misplaces at most
        # |step| * (1 ms)/2 of energy.
        ina = attribute_episode(episode, source="ina3221", channel="VDD_IN").total
        steps = sum(abs(b - a) for a, b in zip(world.levels, world.levels[1:]))
        step_bound = steps * 0.001 / 2
        n_ina = int(duration_s * 1000) + 2
        self.assertLessEqual(abs(ina.joules - true_total), step_bound + float_bar(n_ina, peak * duration_s))


class PowermetricsPrintedFloor(unittest.TestCase):
    def test_only_episode_total_gets_the_printed_minimum(self):
        trace = w_trace(GRID_0_10S, [4.]*len(GRID_0_10S), source="powermetrics",
                        resolution=0.)
        turns = (Turn(0, S, 2*S, 0, 1, 1, first_token_ns=S+S//2),
                 Turn(1, 2*S, 3*S, 0, 1, 1, first_token_ns=2*S+S//2))
        episode = Episode("floor", "t", "benign", "m", "e", 0, "host", S, 3*S,
                          turns, power_traces=(trace,))
        result = attribute_episode(episode, source="powermetrics", channel="gpu0")
        # Constant power and zero resolution have exactly zero modeled
        # sensitivity; D-078 clause 11 adds 1 J only to the printed total.
        self.assertEqual(result.total.half_width_j, 1.)
        self.assertIn("powermetrics.attribution_floor", result.total.flags)
        self.assertIn("powermetrics.attribution_floor", result.flags)
        for segment in result.segments:
            self.assertEqual(segment.energy.half_width_j, 0.)
            self.assertNotIn("powermetrics.attribution_floor", segment.energy.flags)
        self.assertEqual(trace_energy(trace, S, 3*S).half_width_j, 0.)


if __name__ == "__main__":
    unittest.main()
