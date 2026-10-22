"""Closed-form and record-level checks of the real attribution API."""

from dataclasses import replace
from pathlib import Path
import math
import subprocess
import sys
import unittest
from unittest.mock import patch

from joulewise.align import attribution

from joulewise.align.attribution import attribute_episode, trace_energy
from joulewise.align.records import ClockMapping, Episode, PowerTrace, ToolCall, Turn


NS = 1_000_000_000  # Nanoseconds in a second by definition.


def trace(values=(100.0, 100.0, 100.0), *, times=(0, NS, 2 * NS), **overrides):
    # Mock readings print one decimal W, defining their 0.1 W quantum.
    fields = dict(source="mock", channel="package", clock_domain="meter",
                  t_ns=times, values=values, unit="W", nominal_interval_ns=NS, resolution=0.1)
    fields.update(overrides)
    return PowerTrace(**fields)


def mapping(offset=0, uncertainty=10_000_000):
    # A 20 ms synchronization round-trip bracket has a 10 ms half-width.
    return ClockMapping("meter", "host", offset, uncertainty, "synthetic round-trip bracket")


def episode(turns=(), **overrides):
    fields = dict(episode_id="synthetic", task_pair="shade/synthetic",
                  condition="sabotage", agent_model="local-open-weight",
                  endpoint="mock:local", seed=0, clock_domain="host",
                  start_ns=0, end_ns=10 * NS, turns=turns,
                  power_traces=(trace(times=(0, 10 * NS), values=(100.0, 100.0)),),
                  clock_mappings=(mapping(),))
    fields.update(overrides)
    return Episode(**fields)


def turn(index=0, start=NS, end=9 * NS, first=2 * NS, calls=(), **overrides):
    fields = dict(index=index, start_ns=start, end_ns=end, context_tokens=4096,
                  prefill_tokens=512, decode_tokens=256, first_token_ns=first,
                  tool_calls=calls)
    fields.update(overrides)
    return Turn(**fields)


class AttributionChecks(unittest.TestCase):
    def close(self, actual, expected, *, scale=None, half_width=None):
        scale = abs(expected) if scale is None else scale
        # No-uncertainty agreement uses the brief's 1e-6 relative rule.
        bar = 1e-6 * scale
        if half_width is not None:
            # Stay below 1% of the smallest compared printed half-width.
            bar = min(bar, 0.01 * half_width)
        # Verify the bar also clears one million ulps at this magnitude.
        self.assertGreaterEqual(bar, 1e6 * math.ulp(scale))
        self.assertLessEqual(abs(actual - expected), bar)

    def tile(self, result, record):
        self.assertEqual(result.segments[0].start_ns, record.start_ns)
        self.assertEqual(result.segments[-1].end_ns, record.end_ns)
        for left, right in zip(result.segments, result.segments[1:]):
            self.assertEqual(left.end_ns, right.start_ns)
        for segment in result.segments:
            self.assertGreater(segment.end_ns, segment.start_ns)
        values = [segment.energy.joules for segment in result.segments]
        # Each segment contributes one addition; allow sixteen rounded
        # operations per trace span/segment for interpolation and quadrature.
        operations = 16 * (sum(len(t.t_ns) for t in record.power_traces) + len(values) + 1)
        gamma = operations * sys.float_info.epsilon / (1 - operations * sys.float_info.epsilon)
        self.assertLessEqual(abs(math.fsum(values) - result.total.joules),
                             gamma * math.fsum(abs(v) for v in values))

    def test_constant_idle_and_three_uncertainty_terms(self):
        estimate = trace_energy(trace(), NS // 4, 7 * NS // 4,
                                mapping=mapping(), idle_watts=20.0)
        self.close(estimate.joules, (100 - 20) * 1.5, half_width=estimate.half_width_j)
        # Two ends * 100 W * 10 ms, plus 0.1 W * 1.5 s; constant interpolation is zero.
        self.close(estimate.half_width_j, 2 * 100 * 0.01 + 0.1 * 1.5)
        self.assertEqual(estimate.method, "trapezoid_W")
        self.assertFalse(estimate.flags)

    def test_ramp_partial_intervals_are_not_snapped(self):
        estimate = trace_energy(trace(values=(10.0, 20.0, 30.0)), NS // 4, 7 * NS // 4,
                                mapping=mapping())
        # Integral of 10 + 10t from .25 to 1.75 is 30 J.
        self.close(estimate.joules, 30.0, half_width=estimate.half_width_j)
        # C1 start: integral of 10t on [.25,1] = 4.6875 J.
        # C1 end: integral of 10(t-1) on [1,1.75] = 2.8125 J.
        self.close(estimate.half_width_j, 4.6875 + 2.8125 + (20 + 30) * 0.01 + 0.1 * 1.5)

    def test_square_pulse_point_reconstruction(self):
        # A 200 W plateau and two 100 ms linear edges above 50 W.
        pulse = trace(values=(50.0, 50.0, 200.0, 200.0, 50.0, 50.0),
                      times=(0, NS, 11 * NS // 10, 29 * NS // 10, 3 * NS, 4 * NS))
        estimate = trace_energy(pulse, 0, 4 * NS, mapping=mapping())
        # Baseline 50*4 plus excess 150*(1.8 + .1) = 485 J.
        self.close(estimate.joules, 485.0, half_width=estimate.half_width_j)

    def test_whole_window_square_is_interval_supported(self):
        sensor = trace(times=(NS, 2 * NS, 3 * NS, 4 * NS),
                       values=(50.0, 200.0, 200.0, 50.0),
                       averaging_window_ns=NS, duty_fraction=1.0)
        estimate = trace_energy(sensor, NS // 2, 7 * NS // 2, mapping=mapping())
        self.close(estimate.joules, 50 * 0.5 + 200 * 2 + 50 * 0.5,
                   half_width=estimate.half_width_j)
        self.assertEqual(estimate.method, "window_average_W")
        self.assertNotIn("duty.uncovered", estimate.flags)

    def test_duty_gap_fraction_and_linear_bridge(self):
        sensor = trace(times=(0, NS // 10), values=(100.0, 200.0),
                       averaging_window_ns=NS // 40, duty_fraction=0.25)
        estimate = trace_energy(sensor, 0, NS // 10, mapping=mapping())
        # A 75 ms bridge of mean 150 W, then a 25 ms window at 200 W.
        self.close(estimate.joules, 150 * 0.075 + 200 * 0.025,
                   half_width=estimate.half_width_j)
        self.assertEqual(estimate.method, "window_average_W;duty.uncovered_fraction=0.75")
        self.assertIn("duty.uncovered", estimate.flags)
        cut = trace_energy(sensor, NS // 40, NS // 20, mapping=mapping())
        # The linear bridge is 133 1/3 to 166 2/3 W on these 25 ms.
        self.close(cut.joules, 150 * 0.025, half_width=cut.half_width_j)
        self.assertEqual(cut.method, "window_average_W;duty.uncovered_fraction=1.0")

    def test_c2_duty_gap_sensitivity_applies_to_total_and_partial_overlap(self):
        sensor = trace(times=(0, NS // 10), values=(100.0, 200.0),
                       averaging_window_ns=NS // 40, duty_fraction=0.25)
        full = trace_energy(sensor, 0, NS // 10, mapping=mapping(uncertainty=0))
        # Endpoint knots have no C1 or window-cut term. The 75 ms gap
        # contributes |200-100| W * .075 s/2; resolution is .1 W * .1 s.
        self.close(full.half_width_j, 100 * 0.075 / 2 + 0.1 * 0.1)
        cut = trace_energy(sensor, NS // 40, NS // 20, mapping=mapping(uncertainty=0))
        # The raw 100..200 W bracket has slope 1000 W/s. Its line-minus-
        # hold integral on [.025,.05] s is .9375 J at EACH end (C1);
        # only 25 ms of the duty gap overlaps, contributing 100*.025/2.
        self.close(cut.half_width_j, 2 * 0.9375 + 100 * 0.025 / 2 + 0.1 * 0.025)

    def test_c2_bounds_one_step_allocation_inside_window(self):
        period = NS // 10  # Whole 100 ms powermetrics reporting window.
        edge = 37 * NS // 1000  # Explicit 37 ms fixture edge, off the grid.
        sensor = trace(times=(0, period, 2 * period), values=(0.0, 63.0, 100.0),
                       nominal_interval_ns=period, averaging_window_ns=period,
                       resolution=0.001)  # Integer mW reporting quantum.
        estimate = trace_energy(sensor, edge, period, mapping=mapping(uncertainty=0))
        # True power jumps from 0 to 100 W at 37 ms: the [0,100] ms
        # window reports 100 * 63/100 = 63 W, but its final 63 ms used 6.3 J.
        exact = 100 * ((period - edge) / NS)
        self.close(estimate.joules, 63 * 0.063, half_width=estimate.half_width_j)
        # Raw means interpolate from 0 to 63 W. On [37,100] ms the
        # line's integral is (23.31 + 63)/2 * .063 = 2.718765 J.
        # Full C1 comparison plus C2's neighbouring range 100 W * .1 s/4.
        self.close(estimate.half_width_j, 2.718765 + 100 * 0.1 / 4 + 0.001 * 0.063)
        self.assertLessEqual(abs(exact - estimate.joules), estimate.half_width_j)
        self.assertIn("window.edge_allocation_unresolved", estimate.flags)

    def test_single_window_covers_time_before_its_timestamp(self):
        estimate = trace_energy(trace(times=(NS,), values=(60.0,), averaging_window_ns=NS),
                                0, NS, mapping=mapping())
        self.close(estimate.joules, 60.0, half_width=estimate.half_width_j)
        self.assertNotIn("trace.partial_coverage", estimate.flags)

    def test_counter_interpolates_and_uses_joule_resolution(self):
        sensor = trace(times=(0, NS, 2 * NS), values=(0.0, 100.0, 300.0),
                       source="nvml_energy", unit="J_cumulative", resolution=0.001)
        estimate = trace_energy(sensor, NS // 2, 3 * NS // 2,
                                mapping=mapping(uncertainty=1_000_000))
        self.close(estimate.joules, 150.0, half_width=estimate.half_width_j)
        # Full 50 J and 100 J partial counter differences, clock slopes
        # (100+200) W * 1 ms, and two 1 mJ counter quanta.
        self.close(estimate.half_width_j, 50 + 100 + 0.3 + 0.002)
        self.assertEqual(estimate.method, "counter_J")

    def test_counter_wrap_is_flagged_without_guessing_modulus(self):
        sensor = trace(times=(0, NS, 2 * NS, 3 * NS), values=(950.0, 990.0, 5.0, 45.0),
                       source="nvml_energy", unit="J_cumulative", resolution=0.001)
        estimate = trace_energy(sensor, 0, 3 * NS, mapping=mapping())
        # Positive increments 40 J + restart reading 5 J + 40 J.
        self.close(estimate.joules, 40 + 5 + 40, half_width=estimate.half_width_j)
        self.assertIn("counter.wrap", estimate.flags)
        self.assertIn("counter.reset", estimate.flags)
        self.assertNotIn("energy.negative", estimate.flags)

    def test_counter_reset_recovers_work_without_inflating_peak(self):
        period = NS // 10  # One 100 ms NVML counter poll.
        times = tuple(range(0, 4 * NS + 1, period))
        # At 300 W each step is 30 J. At 2 s the driver resets, then records
        # the full step's 30 J: restart-from-zero must recover 1200 J exactly.
        values = tuple(5_000_000.0 + 30 * k if k < 20 else 30.0 * (k - 19)
                       for k in range(len(times)))
        sensor = trace(times=times, values=values, source="nvml_energy",
                       unit="J_cumulative", resolution=0.001)
        estimate = trace_energy(sensor, 0, 4 * NS)
        self.close(estimate.joules, 300 * 4, half_width=estimate.half_width_j)
        self.assertIn("counter.reset_interval", estimate.flags)
        # One 100 ms interval at the observed 300 W peak, plus two mJ quanta.
        self.close(estimate.half_width_j, 300 * 0.1 + 2 * 0.001)
        before = trace_energy(sensor, -NS, 0)
        # One uncovered second at 300 W, not the pre-reset megajoule baseline.
        self.close(before.half_width_j, 300 * 1 + 2 * 0.001)

    def test_counter_dip_cannot_masquerade_as_a_restart(self):
        period = NS // 10  # A 100 ms counter poll at fixture power 300 W.
        times = tuple(range(0, 4 * NS + 1, period))
        poll_j = 300 * (period / NS)
        quantum = 0.001  # NVML reports integer mJ.
        values = [5_000_000.0 + poll_j * k for k in range(len(times))]
        middle = len(times) // 2
        values[middle] = values[middle - 1] - quantum
        sensor = trace(times=times, values=tuple(values), source="nvml_energy",
                       unit="J_cumulative", resolution=quantum)
        result = trace_energy(sensor, 0, 4 * NS)
        self.assertIn("counter.decrease", result.flags)
        self.assertIn("counter.decrease_interval", result.flags)
        self.assertNotIn("counter.reset", result.flags)
        # Ignoring the dip loses one 30 J poll; the recovery step contains
        # two polls plus the 1 mJ dip. Net error is therefore just 1 mJ.
        self.close(result.joules, 300 * 4 + quantum, half_width=result.half_width_j)
        self.assertLessEqual(abs(result.joules - 300 * 4), result.half_width_j)
        # The largest NON-reset step is the 60.001 J recovery. It sets
        # peak = recovery_J/.1 s; one ambiguous poll plus two quanta follows.
        recovery_j = 2 * poll_j + quantum
        self.close(result.half_width_j, recovery_j + 2 * quantum)
        before = trace_energy(sensor, -NS, 0)
        # One missing second uses the recovery's observed power, never the
        # counter's multi-megajoule baseline.
        self.close(before.half_width_j, recovery_j / (period / NS) + 2 * quantum)

    def test_counter_first_drop_exceeding_poll_work_is_a_decrease(self):
        period = NS // 10  # 300 W * .1 s = 30 J per fixture poll.
        times = tuple(range(0, 4 * NS + 1, period))
        values = tuple(5_000_000.0 if k == 0 else 30.0 * (k + 1)
                       for k in range(len(times)))
        result = trace_energy(trace(times=times, values=values, source="nvml_energy",
                                    unit="J_cumulative", resolution=0.001), 0, 4 * NS)
        self.assertIn("counter.decrease", result.flags)
        # The implausible first 60 J is ignored; 39 remaining polls deliver
        # 1170 J. One 30 J poll of sensitivity covers the 1200 J truth.
        self.close(result.joules, 300 * 4 - 300 * 0.1, half_width=result.half_width_j)
        self.close(result.half_width_j, 300 * 0.1 + 2 * 0.001)
        self.assertLessEqual(abs(result.joules - 300 * 4), result.half_width_j)

    def test_all_decreasing_counter_has_no_observed_peak(self):
        sensor = trace(times=(0, NS, 2 * NS), values=(100.0, 80.0, 60.0),
                       source="nvml_energy", unit="J_cumulative", resolution=0.001)
        result = trace_energy(sensor, 0, 2 * NS)
        # Identically absent accepted increments yield bit-exact zero.
        self.assertEqual(result.joules, 0.0)
        self.assertTrue(math.isinf(result.half_width_j))
        self.assertIn("counter.peak_missing", result.flags)
        self.assertIn("counter.decrease", result.flags)
        outside = trace_energy(sensor, -NS, 0)
        self.assertTrue(math.isinf(outside.half_width_j))
        self.assertIn("coverage.peak_missing", outside.flags)

    def test_counter_hold_includes_jump_at_partial_start_interval_end(self):
        sensor = trace(times=(0, NS, 2 * NS), values=(0.0, 100.0, 300.0),
                       source="nvml_energy", unit="J_cumulative", resolution=0.001)
        estimate = trace_energy(sensor, NS // 4, 3 * NS // 2,
                                mapping=mapping(uncertainty=0))
        self.close(estimate.joules, 175.0, half_width=estimate.half_width_j)
        # At the start: full |100 J held jump - 75 J linear| = 25 J.
        # At the stop: full |0 J held increment - 100 J linear| = 100 J.
        self.close(estimate.half_width_j, 25 + 100 + 2 * 0.001)

    def test_short_interval_uncertainty_uses_only_its_own_support(self):
        sensor = trace(times=(0, NS), values=(0.0, 100.0))
        estimate = trace_energy(sensor, 4 * NS // 10, NS // 2,
                                mapping=mapping(uncertainty=0))
        self.close(estimate.joules, 4.5, half_width=estimate.half_width_j)
        # Left sample holds at 0 W; the line integrates to 4.5 J. Each end
        # compares on the same requested 100 ms support: 2 * 4.5 + .1*.1.
        self.close(estimate.half_width_j, 2 * 4.5 + 0.1 * 0.1)
        empty = trace_energy(sensor, NS // 2, NS // 2)
        self.assertEqual((empty.joules, empty.half_width_j), (0.0, 0.0))

    def test_missing_trace_never_subtracts_idle_from_unobserved_energy(self):
        result = attribute_episode(episode(), source="mock", channel="absent", idle_watts=70.0)
        for estimate in (result.total, *(s.energy for s in result.segments)):
            self.assertEqual(estimate.joules, 0.0)
            self.assertTrue(math.isinf(estimate.half_width_j))
            self.assertIn("trace.missing", estimate.flags)

    def test_mapping_translation_preserves_integer_nanoseconds(self):
        origin = 10**18  # An epoch at which binary64 cannot retain individual ns.
        original = trace(values=(10.0, 30.0), times=(0, 10))
        shifted = replace(original, t_ns=(origin, origin + 10))
        a = trace_energy(original, 2, 7, mapping=mapping(uncertainty=0))
        b = trace_energy(shifted, 2, 7, mapping=mapping(offset=-origin, uncertainty=0))
        # Bit identity is appropriate: after integer mapping, the exact same
        # code receives identical integration inputs.
        self.assertEqual(a, b)
        self.close(a.joules, 19 * 5 / NS, half_width=a.half_width_j)

    def test_partial_coverage_and_full_interval_idle_subtraction(self):
        estimate = trace_energy(trace(), -NS, 3 * NS, mapping=mapping(), idle_watts=20.0)
        self.close(estimate.joules, 100 * 2 - 20 * 4, half_width=estimate.half_width_j)
        # Two uncovered seconds * peak 100 W; clock 2 J; resolution .4 J.
        self.close(estimate.half_width_j, 200 + 2 + 0.4)
        self.assertIn("trace.partial_coverage", estimate.flags)

    def test_missing_terms_and_reversed_interval_are_flags(self):
        estimate = trace_energy(trace(resolution=None), 0, NS)
        self.assertIn("resolution.missing", estimate.flags)
        self.assertIn("clock.uncertainty_missing", estimate.flags)
        # Zero is exact here: all three terms are absent or identically zero.
        self.assertEqual(estimate.half_width_j, 0.0)
        empty = trace_energy(trace(times=(), values=()), 0, NS)
        self.assertIn("trace.insufficient_samples", empty.flags)
        self.assertIn("coverage.peak_missing", empty.flags)
        reversed_interval = trace_energy(trace(), NS, 0)
        self.assertIn("interval.reversed", reversed_interval.flags)
        self.assertTrue(math.isinf(reversed_interval.half_width_j))

    def test_nonfinite_sample_and_invalid_metadata_are_flags(self):
        sensor = trace(values=(100.0, math.nan, 100.0), resolution=-1.0,
                       averaging_window_ns=0, duty_fraction=0.25)
        estimate = trace_energy(sensor, 0, 2 * NS, mapping=mapping(uncertainty=-1))
        self.close(estimate.joules, 200.0)
        for flag in ("trace.nonfinite_samples", "resolution.invalid", "window.invalid",
                     "duty.window_missing", "clock.uncertainty_invalid"):
            self.assertIn(flag, estimate.flags)

    def test_overlapping_windows_do_not_double_count(self):
        sensor = trace(times=(NS, 2 * NS), values=(50.0, 100.0), averaging_window_ns=2 * NS)
        estimate = trace_energy(sensor, -NS, 2 * NS, mapping=mapping())
        self.close(estimate.joules, 50 * 2 + 100, half_width=estimate.half_width_j)
        self.assertIn("window.overlap", estimate.flags)

    def test_turn_tool_and_gap_tiling_includes_tampered_work(self):
        calls = (ToolCall("local_search", 3 * NS, 4 * NS, 128, 2048, logged=False),
                 ToolCall("local_exec", 6 * NS, 8 * NS, 64, 1024))
        record = episode((turn(calls=calls, logged=False),), flags=("tamper.turn_deleted",))
        result = attribute_episode(record, source="mock", channel="package", idle_watts=20.0)
        self.tile(result, record)
        self.assertEqual([(s.kind, s.start_ns // NS, s.end_ns // NS) for s in result.segments],
                         [("gap", 0, 1), ("prefill", 1, 2), ("decode", 2, 3),
                          ("tool", 3, 4), ("decode", 4, 6), ("tool", 6, 8),
                          ("decode", 8, 9), ("gap", 9, 10)])
        self.assertIn("tamper.turn_deleted", result.flags)
        self.close(result.total.joules, 800.0, half_width=result.total.half_width_j)

    def test_runner_tools_overlay_gaps_and_other_turns(self):
        calls = (ToolCall("search", 4 * NS, 7 * NS, 128, 2048, logged=False),
                 ToolCall("exec", 7 * NS, 8 * NS, 64, 1024))
        record = episode((turn(end=4 * NS, calls=calls, logged=False),
                          turn(index=1, start=6 * NS, end=9 * NS, first=7 * NS)))
        result = attribute_episode(record, source="mock", channel="package")
        self.tile(result, record)
        self.assertEqual([(s.turn, s.kind, s.start_ns // NS, s.end_ns // NS)
                          for s in result.segments],
                         [(None, "gap", 0, 1), (0, "prefill", 1, 2),
                          (0, "decode", 2, 4), (0, "tool", 4, 7),
                          (0, "tool", 7, 8), (1, "decode", 8, 9),
                          (None, "gap", 9, 10)])
        # Four tool seconds at the fixture's constant 100 W.
        self.close(math.fsum(s.energy.joules for s in result.segments if s.kind == "tool"),
                   4 * 100.0, half_width=result.total.half_width_j)
        self.assertNotIn("tool.outside_turn", result.flags)
        self.assertNotIn("tool.outside_episode", result.flags)

    def test_tool_clips_only_at_episode_edges(self):
        calls = (ToolCall("early", -NS, NS, 64, 512),
                 ToolCall("late", 9 * NS, 11 * NS, 64, 512))
        record = episode((turn(calls=calls),))
        result = attribute_episode(record, source="mock", channel="package")
        self.tile(result, record)
        self.assertEqual([(s.start_ns, s.end_ns) for s in result.segments if s.kind == "tool"],
                         [(0, NS), (9 * NS, 10 * NS)])
        self.assertIn("tool.outside_episode", result.flags)

    def test_unknown_first_token_still_carves_tools(self):
        record = episode((turn(first=None, calls=(ToolCall("local", 3 * NS, 4 * NS, 64, 512),)),))
        result = attribute_episode(record, source="mock", channel="package")
        self.tile(result, record)
        self.assertEqual([s.kind for s in result.segments], ["gap", "decode", "tool", "decode", "gap"])
        self.assertIn("turn.no_first_token", result.flags)

    def test_empty_episode_is_a_gap(self):
        record = episode()
        result = attribute_episode(record, source="mock", channel="package")
        self.tile(result, record)
        self.assertEqual([s.kind for s in result.segments], ["gap"])

    def test_zero_duration_turn_does_not_duplicate_gap_support(self):
        record = episode((turn(start=5 * NS, end=5 * NS, first=5 * NS),))
        result = attribute_episode(record, source="mock", channel="package")
        self.tile(result, record)
        self.assertEqual([(s.turn, s.kind, s.start_ns, s.end_ns) for s in result.segments],
                         [(None, "gap", 0, 10 * NS)])
        self.close(result.total.joules, 100 * 10,
                   half_width=result.total.half_width_j)

    def test_malformed_overlap_is_flagged_and_tiles_once(self):
        calls = (ToolCall("pre", 0, 3 * NS, 64, 512),
                 ToolCall("overlap", 2 * NS, 5 * NS, 64, 512),
                 ToolCall("past", 8 * NS, 10 * NS, 64, 512))
        record = episode((turn(calls=calls), turn(index=1, start=7 * NS, end=10 * NS, first=8 * NS)))
        result = attribute_episode(record, source="mock", channel="package")
        self.tile(result, record)
        for flag in ("tool.prefill_overlap", "tool.overlap", "turn.overlap"):
            self.assertIn(flag, result.flags)

    def test_selection_flags_and_episode_clock_mapping(self):
        record = episode((turn(),))
        ambiguous = replace(record, power_traces=record.power_traces * 2,
                            clock_mappings=record.clock_mappings * 2)
        result = attribute_episode(ambiguous, source="mock", channel="package")
        self.tile(result, ambiguous)
        self.assertIn("trace.ambiguous", result.flags)
        self.assertIn("clock.mapping_ambiguous", result.flags)
        missing = attribute_episode(record, source="mock", channel="absent")
        self.assertIn("trace.missing", missing.flags)
        self.assertEqual(len(missing.segments), len(result.segments))
        # A records-valid mapping may target the wrong episode domain.
        bad = replace(record, clock_mappings=(replace(mapping(), episode_domain="other"),))
        # A known translation is retained even if its destination is mislabeled.
        shifted = replace(bad, power_traces=(replace(record.power_traces[0],
                          t_ns=tuple(t - NS for t in record.power_traces[0].t_ns)),),
                          clock_mappings=(replace(bad.clock_mappings[0], offset_ns=NS),))
        malformed = attribute_episode(shifted, source="mock", channel="package")
        self.assertNotIn("clock.mapping_missing", malformed.flags)
        self.assertIn("clock.episode_domain_mismatch", malformed.flags)
        self.close(malformed.total.joules, result.total.joules,
                   half_width=min(malformed.total.half_width_j, result.total.half_width_j))

    def test_zero_duration_and_invalid_idle_are_reported(self):
        estimate = trace_energy(trace(), NS, NS, mapping=mapping())
        # Identical limits have exactly zero measure, energy and uncertainty.
        self.assertEqual(estimate.joules, 0.0)
        self.assertEqual(estimate.half_width_j, 0.0)
        self.assertNotIn("trace.partial_coverage", estimate.flags)
        bad = trace_energy(trace(), 0, NS, idle_watts=math.nan)
        self.assertIn("idle.nonfinite", bad.flags)

    def test_cold_point_query_builds_only_its_requested_spans_and_reuses_preparation(self):
        period = NS // 1000  # A 1 kHz rail sampled for this 10 s fixture.
        times = tuple(range(0, 10 * NS + 1, period))
        sensor = trace(times=times, values=tuple(12.0 for _ in times),
                       nominal_interval_ns=period)
        a, b = 2 * NS, 2 * NS + NS // 10
        with patch.object(attribution, "_Trace", wraps=attribution._Trace) as prepare:
            with patch.object(attribution, "_Span", wraps=attribution._Span) as span:
                first = trace_energy(sensor, a, b)
                # One span per overlapping sample interval, plus the two
                # endpoint comparisons. A cold call must not build all 10 s.
                self.assertLessEqual(span.call_count, (b - a) // period + 2)
            second = trace_energy(sensor, a + NS, b + NS)
            self.assertEqual(prepare.call_count, 1)  # Exactly one immutable trace preparation.
            translated = trace_energy(sensor, a + NS, b + NS,
                                      mapping=mapping(offset=NS, uncertainty=0))
            self.assertEqual(prepare.call_count, 2)  # A different mapping needs a preparation.
        self.close(first.joules, 12 * (b - a) / NS, half_width=first.half_width_j)
        for result in (second, translated):
            self.close(result.joules, first.joules, half_width=min(
                result.half_width_j, first.half_width_j))
            self.close(result.half_width_j, first.half_width_j)

    def test_import_works_without_site_packages(self):
        result = subprocess.run([sys.executable, "-S", "-c",
                                 "from joulewise.align.attribution import trace_energy"],
                                cwd=Path(__file__).resolve().parents[2],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
