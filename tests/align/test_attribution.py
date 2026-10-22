"""Closed-form and record-level checks of the real attribution API."""

from dataclasses import replace
import math
import subprocess
import sys
import unittest

from joulewise.align.attribution import attribute_episode, trace_energy
from joulewise.align.records import ClockMapping, Episode, PowerTrace, ToolCall, Turn


NS = 1_000_000_000  # Nanoseconds in a second by definition.


def trace(values=(100.0, 100.0, 100.0), *, times=(0, NS, 2 * NS), **overrides):
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
        # Start: half integral of 10t on [.25,1] = 2.34375 J.
        # End: half integral of 10(t-1) on [1,1.75] = 1.40625 J.
        self.close(estimate.half_width_j, 2.34375 + 1.40625 + (20 + 30) * 0.01 + 0.1 * 1.5)

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
        # Half of the 50 J and 100 J partial counter increments, clock slopes
        # (100+200) W * 1 ms, and two 1 mJ counter quanta.
        self.close(estimate.half_width_j, 25 + 50 + 0.3 + 0.002)
        self.assertEqual(estimate.method, "counter_J")

    def test_counter_wrap_is_flagged_without_guessing_modulus(self):
        sensor = trace(times=(0, NS, 2 * NS, 3 * NS), values=(950.0, 990.0, 5.0, 45.0),
                       source="nvml_energy", unit="J_cumulative", resolution=0.001)
        estimate = trace_energy(sensor, 0, 3 * NS, mapping=mapping())
        self.close(estimate.joules, 45 - 950, half_width=estimate.half_width_j)
        self.assertIn("counter.wrap", estimate.flags)
        self.assertIn("energy.negative", estimate.flags)

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
        self.close(estimate.half_width_j, 0.0, scale=100.0)
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

    def test_malformed_overlap_is_flagged_and_tiles_once(self):
        calls = (ToolCall("pre", 0, 3 * NS, 64, 512),
                 ToolCall("overlap", 2 * NS, 5 * NS, 64, 512),
                 ToolCall("past", 8 * NS, 10 * NS, 64, 512))
        record = episode((turn(calls=calls), turn(index=1, start=7 * NS, end=10 * NS, first=8 * NS)))
        result = attribute_episode(record, source="mock", channel="package")
        self.tile(result, record)
        for flag in ("tool.outside_turn", "tool.prefill_overlap", "tool.overlap", "turn.overlap"):
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
        self.assertIn("clock.mapping_missing", attribute_episode(bad, source="mock", channel="package").flags)

    def test_zero_duration_and_invalid_idle_are_reported(self):
        estimate = trace_energy(trace(), NS, NS, mapping=mapping())
        self.close(estimate.joules, 0.0, scale=100.0)
        self.assertNotIn("trace.partial_coverage", estimate.flags)
        bad = trace_energy(trace(), 0, NS, idle_watts=math.nan)
        self.assertIn("idle.nonfinite", bad.flags)

    def test_import_works_without_site_packages(self):
        result = subprocess.run([sys.executable, "-S", "-c",
                                 "from joulewise.align.attribution import trace_energy"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
