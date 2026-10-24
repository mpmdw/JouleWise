"""Clock hazard: positive controls for the frequency gate, the dwell residual,
steps, skew, frequency-word changes, reboots and probe failure."""
from __future__ import annotations

import os
import sys
import unittest
import unittest.mock
from fractions import Fraction

from joulewise import kernel_clock
from joulewise.hazards import base, clock
from tests.live_hw import LiveHardwareTestCase
from tests.hazards.fakes import (
    BOOT_UUID, FakeClocks, FrequencyReader, Runner, completed, frequency_probe, ppm_word,
)

LIMITS = dict(clock.DEFAULT_THRESHOLDS)


def boot_runner(uuid_text: str = BOOT_UUID) -> Runner:
    return Runner({clock.BOOT_ARGV: lambda argv: completed(argv, (uuid_text + "\n").encode())})


def dwell(clocks: FakeClocks, seconds: int, *, reader=None, boot_end: str = BOOT_UUID):
    """Sample the fake clocks at 1 Hz for ``seconds`` through the production sampler."""

    ctx = base.Context(run=boot_runner(), clocks=clocks)
    reader = reader or FrequencyReader(clocks)
    started = ctx.stamp()
    samples = [clock.sample(ctx, frequency_reader=reader)]
    for _ in range(seconds):
        clocks.sleep(1.0)
        samples.append(clock.sample(ctx, frequency_reader=reader))
    return clock.series(samples, boot_start=BOOT_UUID, boot_end=boot_end, started=started,
                        finished=ctx.stamp())


class FrequencyGateTests(unittest.TestCase):
    def test_today_minus_3p17_ppm_passes_at_4p846_ms(self):
        gate = clock.frequency_bound(ppm_word(-3.17), LIMITS)
        self.assertTrue(gate["passes"])
        self.assertAlmostEqual(gate["bound_ms"], 4.8457, places=3)

    # Retain the historical physics-coverage id; the ruled result is now PASS.
    def test_frequency_3p7_ppm_at_335_s_refuses(self):
        clocks = FakeClocks(drift_word=ppm_word(3.7))
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        verdict = clock.judge(clock.measure(ctx, frequency_reader=FrequencyReader(clocks)), LIMITS)
        self.assertEqual(verdict.status, base.PASS)
        self.assertEqual(verdict.reasons, ())
        self.assertGreater(verdict.observed["frequency_gate"]["bound_ms"], 5.0)

    def test_limit_is_3p63_ppm_and_matches_kernel_clock(self):
        gate = clock.frequency_bound(ppm_word(-3.17), LIMITS)
        self.assertAlmostEqual(gate["max_abs_frequency_ppm"], 3.6306, places=4)
        for ppm in (-3.17, 3.6, 3.63, 3.64, 3.7, 0.0):
            word = ppm_word(ppm)
            ours = clock.frequency_bound(word, LIMITS)
            theirs = kernel_clock.frequency_gate(frequency_probe(word), LIMITS["t_stream_max_s"])
            self.assertEqual(ours["passes"], theirs["passes"], ppm)
            self.assertAlmostEqual(ours["bound_ms"], theirs["bound_ms"], places=9)


    def test_block6_flag_band_and_exact_kernel_word_boundary(self):
        from fractions import Fraction
        from joulewise.b6.plan_inputs import CLOCK_THRESHOLDS
        limits = {**LIMITS, **CLOCK_THRESHOLDS}
        edge = int((Fraction(5000, 335) - Fraction(1, 4)) * clock.FREQUENCY_SCALE)
        for sign in (-1, 1):
            for word, passes, flags in ((ppm_word(3.6), True, []),
                                        (ppm_word(4), True, ["clock.rate_above_budget"]),
                                        (edge, True, ["clock.rate_above_budget"]),
                                        (edge + 1, False, [])):
                gate = clock.frequency_bound(sign * word, limits)
                self.assertEqual(gate["passes"], passes)
                self.assertEqual([flag["code"] for flag in clock.rate_flags(gate)], flags)
        self.assertEqual(clock.rate_flags(clock.frequency_bound(ppm_word(4), LIMITS)), [])


class InstantJudgeTests(unittest.TestCase):
    def test_instant_reading_passes_and_records_three_stamps(self):
        clocks = FakeClocks()
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        measurement = clock.measure(ctx, frequency_reader=FrequencyReader(clocks))
        verdict = clock.judge(measurement, LIMITS)
        self.assertEqual(verdict.status, base.PASS, verdict.reasons)
        self.assertEqual(measurement.values["boot_session_uuid"], BOOT_UUID)
        for stamp in (measurement.started, measurement.finished):
            self.assertGreater(stamp.wall_ns, 1_700_000_000 * 10**9)
            self.assertNotEqual(stamp.monotonic_ns, stamp.monotonic_raw_ns)
        self.assertEqual(measurement.raw[0].name, "timex.bin")

    def test_read_skew_over_1ms_refuses(self):
        clocks = FakeClocks(skew_ns=1_500_000)
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        verdict = clock.judge(clock.measure(ctx, frequency_reader=FrequencyReader(clocks)), LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("skew", verdict.reasons[0])

    def test_frequency_probe_failure_is_unmeasured(self):
        clocks = FakeClocks()
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        verdict = clock.judge(clock.measure(ctx, frequency_reader=FrequencyReader(clocks, fail=True)),
                              LIMITS)
        self.assertEqual(verdict.status, base.UNMEASURED)

    def test_boot_probe_failure_is_unmeasured(self):
        clocks = FakeClocks()
        runner = Runner({clock.BOOT_ARGV: lambda argv: completed(argv, b"", returncode=1)})
        verdict = clock.judge(clock.measure(base.Context(run=runner, clocks=clocks),
                                            frequency_reader=FrequencyReader(clocks)), LIMITS)
        self.assertEqual(verdict.status, base.UNMEASURED)

    def test_corrupted_timex_bytes_are_unmeasured(self):
        clocks = FakeClocks()

        def reader():
            probe = frequency_probe(ppm_word(-3.17))
            probe["raw_word"] += 1  # interpretation no longer matches the raw bytes
            return probe

        verdict = clock.judge(clock.measure(base.Context(run=boot_runner(), clocks=clocks),
                                            frequency_reader=reader), LIMITS)
        self.assertEqual(verdict.status, base.UNMEASURED)


class DwellResidualTests(unittest.TestCase):
    def test_skew_rejected_sample_keeps_the_measured_rate_judgment_and_flag(self):
        for ppm, status in ((0, base.PASS), (40, base.REFUSE)):
            measured = dwell(FakeClocks(drift_word=ppm_word(ppm)), 60)
            samples = [dict(item) for item in measured.values["samples"]]
            samples[30].update(anchor=None, error="clock.unmeasured: anchor read skew above bound")
            changed = clock.series(samples, boot_start=BOOT_UUID, boot_end=BOOT_UUID,
                                   started=measured.started, finished=measured.finished)
            verdict = clock.judge(changed, LIMITS)
            self.assertEqual(verdict.status, status)
            self.assertEqual(verdict.observed["anchored_samples"], 60)
            self.assertIn({"code": "clock.unmeasured", "sample_index": 30,
                           "error": samples[30]["error"]}, verdict.observed["flags"])
            if ppm:
                self.assertTrue(any("measured rate gate" in reason for reason in verdict.reasons))

    def test_rejected_edge_samples_and_two_remaining_anchors(self):
        measured = dwell(FakeClocks(), 60)
        samples = [dict(item, anchor=None, error="skew rejected") for item in measured.values["samples"]]
        for index in (1, 59):
            samples[index] = measured.values["samples"][index]
        changed = clock.series(samples, boot_start=BOOT_UUID, boot_end=BOOT_UUID,
                               started=measured.started, finished=measured.finished)
        verdict = clock.judge(changed, LIMITS)
        self.assertEqual(verdict.status, base.PASS)
        self.assertEqual(verdict.observed["anchored_samples"], 2)
        self.assertEqual(len(verdict.observed["flags"]), 59)
        samples[59] = dict(samples[59], anchor=None)
        changed = clock.series(samples, boot_start=BOOT_UUID, boot_end=BOOT_UUID,
                               started=measured.started, finished=measured.finished)
        self.assertEqual(clock.judge(changed, LIMITS).status, base.UNMEASURED)

    def test_step_uses_adjacent_remaining_anchors_across_a_rejected_sample(self):
        clocks = FakeClocks()
        clocks.step_at(90.5, 1_100_000)
        measured = dwell(clocks, 180)
        samples = [dict(item) for item in measured.values["samples"]]
        samples[90].update(anchor=None, error="skew rejected")
        changed = clock.series(samples, boot_start=BOOT_UUID, boot_end=BOOT_UUID,
                               started=measured.started, finished=measured.finished)
        verdict = clock.judge(changed, LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertTrue(any("dwell step" in reason for reason in verdict.reasons))

    def test_measured_rate_refuses_even_when_kernel_word_is_zero(self):
        clocks = FakeClocks(drift_word=ppm_word(100))
        verdict = clock.judge(dwell(clocks, 60, reader=lambda: frequency_probe(0)), LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertTrue(any('measured rate gate' in r for r in verdict.reasons))
        self.assertGreater(verdict.observed['measured_rate_gate']['rate_ppm'], 99)

    def test_missing_frequency_never_hides_a_measured_rate_hazard(self):
        def absent():
            raise OSError("frequency unavailable")
        for reader in (absent, lambda: frequency_probe(0)):
            measured = dwell(FakeClocks(drift_word=ppm_word(40)), 60, reader=reader)
            verdict = clock.judge(measured, LIMITS)
            self.assertEqual(verdict.status, base.REFUSE)
            self.assertTrue(any("measured rate gate" in reason for reason in verdict.reasons))

    def test_mid_dwell_step_above_one_ms_refuses_under_the_fit_residual_limit(self):
        clocks = FakeClocks()
        clocks.step_at(90.5, 1_100_000)
        verdict = clock.judge(dwell(clocks, 180), LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertLess(verdict.observed["max_abs_residual_ns"], LIMITS["residual_max_ns"])
        self.assertTrue(any("dwell step" in reason for reason in verdict.reasons))

    def test_rate_bound_exact_equality_and_precheck_use_the_same_fit(self):
        from fractions import Fraction
        from joulewise.b6 import precheck
        limits = {**LIMITS, 'h_ms': 0, 't_stream_max_s': 200, 'series_min_s': 50}
        edge = Fraction(5000, 200) - Fraction(1, 4)
        self.assertTrue(clock.measured_rate_bound(edge, limits)['passes'])
        self.assertFalse(clock.measured_rate_bound(edge + Fraction(1, 10**9), limits)['passes'])
        measured = dwell(FakeClocks(drift_word=ppm_word(4)), 60)
        reading, codes = precheck.clock_rate(measured.values['samples'], BOOT_UUID, BOOT_UUID, limits)
        judged = clock.judge(measured, limits)
        self.assertEqual(reading['rate_ppm'], judged.observed['measured_rate_gate']['rate_ppm'])
        self.assertEqual(reading['bound_ms'], judged.observed['measured_rate_gate']['bound_ms'])
        self.assertEqual(codes, [])

    def test_minus_3p17_ppm_drift_over_1600_s_passes_under_the_residual_form(self):
        clocks = FakeClocks(drift_word=ppm_word(-3.17))
        series = dwell(clocks, 1600)
        verdict = clock.judge(series, LIMITS)
        self.assertEqual(verdict.status, base.PASS, verdict.reasons)
        # The raw anchor itself moved about -5.07 ms: a plain movement check would refuse.
        self.assertLess(verdict.observed["anchor_movement_ns"], -5_000_000)
        self.assertLess(verdict.observed["max_abs_residual_ns"], 10_000)

    def test_injected_6ms_step_refuses(self):
        clocks = FakeClocks(drift_word=ppm_word(-3.17))
        clocks.step_at(300.5, 6_000_000)
        verdict = clock.judge(dwell(clocks, 600), LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertTrue(any("residual" in reason for reason in verdict.reasons))

    # Historical coverage id; the frequency change is now diagnostic.
    def test_changed_frequency_word_refuses(self):
        clocks = FakeClocks(drift_word=ppm_word(-3.17))
        reader = FrequencyReader(clocks)
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        started = ctx.stamp()
        samples = [clock.sample(ctx, frequency_reader=reader)]
        for second in range(600):
            clocks.sleep(1.0)
            if second == 400:
                clocks.drift_word = ppm_word(-3.20)
            samples.append(clock.sample(ctx, frequency_reader=reader))
        series = clock.series(samples, boot_start=BOOT_UUID, boot_end=BOOT_UUID,
                              started=started, finished=ctx.stamp())
        verdict = clock.judge(series, LIMITS)
        self.assertEqual(verdict.status, base.PASS)
        self.assertTrue(verdict.observed["frequency_word_changed"])

    def test_boot_session_change_refuses(self):
        clocks = FakeClocks()
        verdict = clock.judge(dwell(clocks, 30, boot_end="0f6b5c4a-0000-4000-8000-000000000001"),
                              LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("boot session changed", verdict.reasons[0])

    def test_one_dwell_sample_with_read_skew_above_1ms_refuses(self):
        clocks = FakeClocks()
        series = dwell(clocks, 30)
        samples = [dict(item, anchor=dict(item["anchor"])) for item in series.values["samples"]]
        samples[12]["anchor"]["read_skew_ns"] = 1_000_001
        changed = clock.series(samples, boot_start=BOOT_UUID, boot_end=BOOT_UUID,
                               started=series.started, finished=series.finished)
        self.assertEqual(clock.judge(series, LIMITS).status, base.PASS)
        verdict = clock.judge(changed, LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertEqual(verdict.reasons, ("anchor read skew 1000001 ns exceeds 1000000 ns",))

    def test_failed_frequency_read_keeps_the_dwell_anchors_measured(self):
        clocks = FakeClocks()
        reader = FrequencyReader(clocks)
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        started = ctx.stamp()
        samples = [clock.sample(ctx, frequency_reader=reader)]
        reader.fail = True
        samples.append(clock.sample(ctx, frequency_reader=reader))
        series = clock.series(samples, boot_start=BOOT_UUID, boot_end=BOOT_UUID, started=started,
                              finished=ctx.stamp())
        self.assertEqual(clock.judge(series, LIMITS).status, base.PASS)
        self.assertTrue(clock.judge(series, LIMITS).observed["frequency_word_absent"])

    def test_residual_arithmetic_is_exact(self):
        first = {"anchor_ns": 0, "monotonic_raw_ns": 0}
        later = {"anchor_ns": -5_072_000, "monotonic_raw_ns": 1600 * 10**9}
        word = ppm_word(-3.17)
        expected = Fraction(word * 1600 * 10**9, 65536 * 10**6)
        self.assertEqual(clock.residual_ns(first, later, word), Fraction(-5_072_000) - expected)


class WindowEventTests(unittest.TestCase):
    def journal(self, clocks, seconds, reader):
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        samples = []
        for second in range(seconds):
            samples.append(clock.sample(ctx, frequency_reader=reader if second % 5 == 0 else None))
            clocks.sleep(1.0)
        return samples

    def test_step_inside_a_member_span_is_flagged_and_outside_is_not(self):
        clocks = FakeClocks()
        clocks.step_at(100.5, 2_000_000)
        samples = self.journal(clocks, 200, FrequencyReader(clocks))
        events = clock.window_events(samples)
        self.assertEqual([event["code"] for event in events], ["clock.step"])
        a, b = events[0]["interval"]["monotonic_ns"]
        inside = {"monotonic_ns": [a - 5 * 10**9, b + 5 * 10**9]}
        outside = {"monotonic_ns": [b + 20 * 10**9, b + 40 * 10**9]}
        self.assertEqual([f["code"] for f in clock.span_findings(samples, inside)],
                         ["clock.step_overlap"])
        self.assertEqual(clock.span_findings(samples, outside), [])

    def test_frequency_change_in_window_is_an_event(self):
        clocks = FakeClocks()
        reader = FrequencyReader(clocks)
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        samples = []
        for second in range(60):
            if second == 30:
                clocks.drift_word += 100
            samples.append(clock.sample(ctx, frequency_reader=reader if second % 5 == 0 else None))
            clocks.sleep(1.0)
        codes = [event["code"] for event in clock.window_events(samples)]
        self.assertEqual(codes, ["clock.frequency_changed"])

    def journal_with_failure(self, step_ns: int, *, fail_anchor: bool):
        """1 Hz samples, f every 5 s; at 100.5 s the wall clock steps by ``step_ns``
        and the sample at 100 s fails (its f read, or its anchor read too)."""

        clocks = FakeClocks()
        clocks.step_at(100.5, step_ns)
        reader = FrequencyReader(clocks)
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        samples = []
        for second in range(200):
            if second == 100:
                reader.fail = True
                item = clock.sample(ctx, frequency_reader=reader)  # anchor read, then f fails
                reader.fail = False
                self.assertIsNotNone(item["error"])
                if fail_anchor:
                    item["anchor"] = None
                samples.append(item)
            else:
                samples.append(clock.sample(ctx, frequency_reader=reader if second % 5 == 0 else None))
            clocks.sleep(1.0)
        return samples

    def test_step_across_a_failed_f_read_is_still_seen(self):
        # Review finding: a 2 ms step (inside the 1-5 ms band the per-member
        # anchor bound does not catch) straddling a sample whose f read failed.
        samples = self.journal_with_failure(2_000_000, fail_anchor=False)
        self.assertEqual([event["code"] for event in clock.window_events(samples)], ["clock.step"])
        mid = samples[100]["finished"]["monotonic_ns"]
        span = {"monotonic_ns": [mid - 3 * 10**9, mid + 3 * 10**9]}
        # The prior f still supports the existing step comparison, but
        # the failed refresh must also disclose incomplete f coverage.
        self.assertEqual([f["code"] for f in clock.span_findings(samples, span)],
                         ["clock.step_overlap", "clock.unmeasured"])

    def test_step_across_a_failed_anchor_read_is_compared_across_the_gap(self):
        samples = self.journal_with_failure(2_000_000, fail_anchor=True)
        events = clock.window_events(samples)
        self.assertEqual([event["code"] for event in events], ["clock.step"])
        a, b = events[0]["interval"]["monotonic_ns"]
        self.assertEqual(a, samples[99]["started"]["monotonic_ns"])
        self.assertEqual(b, samples[101]["finished"]["monotonic_ns"])
        # The 2 s anchor gap is under the existing 3 s bound, but this
        # sample also failed its f read: frequency coverage is unmeasured.
        span = {"monotonic_ns": [a - 10**9, b + 10**9]}
        self.assertEqual([f["code"] for f in clock.span_findings(samples, span)],
                         ["clock.step_overlap", "clock.unmeasured"])

    def test_no_step_no_event_across_failed_samples(self):
        clocks = FakeClocks()
        reader = FrequencyReader(clocks)
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        samples = []
        for second in range(120):
            reader.fail = second in (40, 41, 77)
            samples.append(clock.sample(ctx, frequency_reader=reader if second % 5 == 0 or reader.fail
                                        else None))
            clocks.sleep(1.0)
        self.assertEqual(clock.window_events(samples), [])

    def test_gap_in_the_journal_is_unmeasured(self):
        clocks = FakeClocks()
        samples = self.journal(clocks, 20, FrequencyReader(clocks))
        clocks.sleep(30)
        samples += self.journal(clocks, 20, FrequencyReader(clocks))
        span = {"monotonic_ns": [samples[15]["finished"]["monotonic_ns"],
                                 samples[25]["finished"]["monotonic_ns"]]}
        self.assertIn("clock.unmeasured", [f["code"] for f in clock.span_findings(samples, span)])


class FrequencyCoverageTests(unittest.TestCase):
    def journal(self, *, failed, seconds=11):
        from joulewise.hazards.monitor import DEFAULT_CADENCE

        clocks = FakeClocks()
        # Twice the registered step threshold: a real 2 ms wall step in
        # the 1-5 ms band, with 1 Hz anchors and the production f cadence.
        clocks.step_at(4.5, 2 * LIMITS["step_ns"])
        reader = FrequencyReader(clocks)
        ctx = base.Context(clocks=clocks)
        samples = []
        for second in range(seconds):
            reader.fail = failed(second)
            samples.append(clock.sample(ctx, frequency_reader=(
                reader if second % DEFAULT_CADENCE["frequency_s"] == 0 else None)))
            clocks.sleep(DEFAULT_CADENCE["clock_s"])
        return samples

    def member(self, samples, start, stop):
        # Use observed integer timestamps, with a successful anchor on
        # either side; only frequency evidence can leave this unmeasured.
        span = {"monotonic_ns": [samples[start]["finished"]["monotonic_ns"],
                                 samples[stop]["finished"]["monotonic_ns"]]}
        return clock.span_findings(samples, span)

    def test_failed_frequency_from_startup_is_unmeasured_not_a_step(self):
        samples = self.journal(failed=lambda second: True)
        self.assertEqual(clock.window_events(samples), [])
        self.assertEqual([item["code"] for item in self.member(samples, 1, 9)],
                         ["clock.unmeasured"])

    def test_failed_refresh_before_member_makes_frequency_stale(self):
        samples = self.journal(failed=lambda second: second > 0)
        self.assertEqual([item["code"] for item in self.member(samples, 6, 9)],
                         ["clock.unmeasured"])

    def test_successful_refresh_restores_coverage(self):
        samples = self.journal(failed=lambda second: 0 < second < 10, seconds=16)
        self.assertEqual(self.member(samples, 11, 14), [])


class PreemptedReadTests(unittest.TestCase):
    """Mock rehearsal round 3, R3-1: a ps child preempted the monitor's anchor
    read (RAW, REALTIME, RAW) for 3.9-8.3 ms, and the anchor error read as a
    false clock.step / clock.step_overlap.  No wall-clock step happens here."""

    def journal(self, preempt: dict[int, list[int]], seconds: int = 60):
        clocks = FakeClocks()
        reader = FrequencyReader(clocks)
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        samples = []
        for second in range(seconds):
            clocks.preempt_ns = list(preempt.get(second, ()))
            samples.append(clock.sample(ctx, frequency_reader=reader if second % 5 == 0 else None))
            clocks.preempt_ns = []
            clocks.sleep(1.0)
        return samples

    def test_the_bound_is_a_quarter_of_the_step_threshold(self):
        self.assertEqual(clock.window_skew_max_ns(LIMITS["step_ns"]), 250_000)
        self.assertEqual(clock.WINDOW_SKEW_MAX_NS, 250_000)
        self.assertLess(clock.WINDOW_SKEW_MAX_NS, LIMITS["step_ns"])

    def test_a_preempted_anchor_read_is_re_read_and_gives_no_step(self):
        # One 8.3 ms preemption at 30 s (the rehearsal's worst): the second read is clean.
        samples = self.journal({30: [8_300_000]})
        self.assertEqual(clock.window_events(samples), [])
        self.assertEqual([read["read_skew_ns"] for read in samples[30]["rejected_anchors"]],
                         [8_300_400])
        self.assertLessEqual(samples[30]["anchor"]["read_skew_ns"], clock.WINDOW_SKEW_MAX_NS)
        self.assertIsNone(samples[30]["error"])
        mid = samples[30]["finished"]["monotonic_ns"]
        span = {"monotonic_ns": [mid - 5 * 10**9, mid + 5 * 10**9]}
        self.assertEqual(clock.span_findings(samples, span), [])

    def test_every_read_preempted_is_unmeasured_never_a_step(self):
        samples = self.journal({30: [3_900_000, 8_300_000, 5_000_000, 4_000_000, 6_000_000]})
        self.assertIsNone(samples[30]["anchor"])
        self.assertTrue(samples[30]["error"].startswith("clock.unmeasured"))
        self.assertEqual(len(samples[30]["rejected_anchors"]), clock.ANCHOR_TRIES)
        self.assertEqual(clock.window_events(samples), [])
        mid = samples[30]["finished"]["monotonic_ns"]
        span = {"monotonic_ns": [mid - 5 * 10**9, mid + 5 * 10**9]}
        found = clock.span_findings(samples, span)
        self.assertEqual([f["code"] for f in found], ["clock.unmeasured"])
        self.assertEqual(found[0]["observed"]["rule"], "read_skew")
        # a member clear of the preempted sample is clean
        clear = {"monotonic_ns": [mid + 10 * 10**9, mid + 20 * 10**9]}
        self.assertEqual(clock.span_findings(samples, clear), [])

    def test_a_recorded_anchor_over_the_bound_is_never_compared(self):
        # A journal written before the re-read (or by any other writer): the
        # 8.3 ms anchor stays in the record but is skipped, not read as a step.
        # The anchor is 4.15 ms low, as an 8.3 ms preemption after the REALTIME read leaves it.
        samples = self.journal({})
        samples[30] = dict(samples[30], anchor=dict(samples[30]["anchor"],
                                                   anchor_ns=samples[30]["anchor"]["anchor_ns"] - 4_150_000,
                                                   read_skew_ns=8_300_400))
        self.assertEqual(clock.window_events(samples), [])
        mid = samples[30]["finished"]["monotonic_ns"]
        span = {"monotonic_ns": [mid - 5 * 10**9, mid + 5 * 10**9]}
        self.assertEqual([f["code"] for f in clock.span_findings(samples, span)], ["clock.unmeasured"])

    def test_a_real_step_next_to_a_preempted_read_is_still_seen(self):
        clocks = FakeClocks()
        clocks.step_at(30.5, 2_000_000)
        reader = FrequencyReader(clocks)
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        samples = []
        for second in range(60):
            clocks.preempt_ns = [8_000_000] * clock.ANCHOR_TRIES if second == 30 else []
            samples.append(clock.sample(ctx, frequency_reader=reader if second % 5 == 0 else None))
            clocks.preempt_ns = []
            clocks.sleep(1.0)
        events = clock.window_events(samples)
        self.assertEqual([event["code"] for event in events], ["clock.step"])
        self.assertAlmostEqual(events[0]["observed"], 2_000_000, delta=1_000)

    def test_the_monitor_journals_the_preempted_reads(self):
        from joulewise.hazards import monitor
        lines = [{"kind": "reading", "started": item["started"], "finished": item["finished"],
                  "values": {"anchor": item["anchor"], "frequency": item["frequency"],
                             **({"rejected_anchors": item["rejected_anchors"]}
                                if item.get("rejected_anchors") else {})},
                  "error": item["error"]}
                 for item in self.journal({30: [8_300_000] * clock.ANCHOR_TRIES})]
        samples = monitor.clock_samples(lines)
        self.assertEqual(len(samples[30]["rejected_anchors"]), clock.ANCHOR_TRIES)
        self.assertEqual(clock.window_events(samples), [])

    def test_the_arm_dwell_keeps_its_own_1_ms_bound(self):
        clocks = FakeClocks()
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        clocks.preempt_ns = [600_000]  # over the in-window bound, under the arm's
        item = clock.sample(ctx, frequency_reader=FrequencyReader(clocks),
                            max_skew_ns=LIMITS["skew_max_ns"])
        self.assertEqual(item["anchor"]["read_skew_ns"], 600_400)
        self.assertNotIn("rejected_anchors", item)
        # the instant read re-reads a preempted anchor against 1 ms too
        clocks.preempt_ns = [3_000_000]
        measurement = clock.measure(ctx, frequency_reader=FrequencyReader(clocks))
        self.assertEqual(clock.judge(measurement, LIMITS).status, base.PASS)
        self.assertEqual(measurement.values["rejected_anchors"][0]["read_skew_ns"], 3_000_400)


class PreemptedReadReviewTests(unittest.TestCase):
    """P3-HAZ final review (Sol 6.1): F5, F6 and the coverage and journaling
    mutations M9 and M14 that the shipped tests did not kill."""

    journal = PreemptedReadTests.journal

    def test_an_f_read_beside_a_rejected_anchor_still_records_the_change(self):
        # F5: sample 30 read a new f but its anchor was preempted (8.3 ms
        # skew, 4.15 ms low).  The change and the change back are recorded;
        # the preempted anchor is never compared.
        samples = self.journal({})
        new_word = samples[0]["frequency"]["raw_word"] + 65_536
        samples[30] = dict(samples[30], frequency=dict(samples[30]["frequency"], raw_word=new_word),
                           anchor=dict(samples[30]["anchor"],
                                       anchor_ns=samples[30]["anchor"]["anchor_ns"] - 4_150_000,
                                       read_skew_ns=8_300_400))
        samples[35] = dict(samples[35], frequency=dict(samples[35]["frequency"],
                                                       raw_word=samples[0]["frequency"]["raw_word"]))
        events = clock.window_events(samples)
        self.assertEqual([(event["code"], event["observed"]) for event in events],
                         [("clock.frequency_changed", new_word),
                          ("clock.frequency_changed", samples[0]["frequency"]["raw_word"])])

    def test_rejected_reads_survive_a_later_read_that_raises(self):
        # F6: the first read is preempted (8.3 ms), the second raises.
        clocks = FakeClocks()
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        preempted = {"realtime_ns": 1, "monotonic_raw_ns": 2, "read_skew_ns": 8_300_400, "anchor_ns": -1}
        with unittest.mock.patch.object(clock, "_anchor_record",
                                        side_effect=[preempted, OSError("clock_gettime failed")]):
            item = clock.sample(ctx, frequency_reader=None)
        self.assertIsNone(item["anchor"])
        self.assertIn("OSError: clock_gettime failed", item["error"])
        self.assertEqual(item["rejected_anchors"], [preempted])
        with unittest.mock.patch.object(clock, "_anchor_record",
                                        side_effect=[dict(preempted, read_skew_ns=3_000_400),
                                                     OSError("clock_gettime failed")]):
            measurement = clock.measure(ctx, frequency_reader=FrequencyReader(clocks))
        self.assertIn("OSError", measurement.error)
        self.assertEqual(measurement.values["rejected_anchors"][0]["read_skew_ns"], 3_000_400)
        self.assertEqual(clock.judge(measurement, LIMITS).status, base.UNMEASURED)

    def test_anchors_over_the_bound_are_not_coverage(self):
        # M9: six recorded anchors over the bound leave a 7 s hole in the
        # 1 Hz journal; the coverage rule sees the hole as well as the samples.
        samples = self.journal({})
        for second in range(28, 34):
            samples[second] = dict(samples[second], anchor=dict(samples[second]["anchor"],
                                                                read_skew_ns=8_300_400))
        mid = samples[30]["finished"]["monotonic_ns"]
        span = {"monotonic_ns": [mid - 1 * 10**9, mid + 1 * 10**9]}
        found = clock.span_findings(samples, span)
        self.assertEqual([f["code"] for f in found], ["clock.unmeasured", "clock.unmeasured"])
        self.assertEqual(found[0]["observed"], [samples[27]["finished"]["monotonic_ns"],
                                                samples[34]["finished"]["monotonic_ns"]])
        inside = sum(1 for second in range(28, 34)
                     if span["monotonic_ns"][0] <= samples[second]["finished"]["monotonic_ns"]
                     <= span["monotonic_ns"][1])
        self.assertGreaterEqual(inside, 1)
        self.assertEqual((found[1]["observed"]["rule"], found[1]["observed"]["samples"]), ("read_skew", inside))

    def test_the_running_monitor_journals_rejected_reads(self):
        # M14: the production monitor writes the rejected reads and no anchor.
        import tempfile
        from pathlib import Path
        from joulewise.hazards import monitor
        from tests.hazards.test_monitor import FakeMac
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            mac = FakeMac(Path(tmp))
            instance = mac.monitor()
            instance.open_session(["test"])
            mac.clocks.preempt_ns = [8_000_000] * clock.ANCHOR_TRIES
            instance.run(max_seconds=3)
            instance.close_session("test end")
            lines = [line for line in monitor.load_journals(mac.custody)["clock"] if line["kind"] == "reading"]
        preempted = [line for line in lines if (line["values"] or {}).get("rejected_anchors")]
        self.assertEqual(len(preempted), 1)
        self.assertIsNone(preempted[0]["values"]["anchor"])
        self.assertEqual(len(preempted[0]["values"]["rejected_anchors"]), clock.ANCHOR_TRIES)
        self.assertTrue(preempted[0]["error"].startswith("clock.unmeasured"))
        self.assertTrue(all(line["values"]["anchor"] for line in lines if line is not preempted[0]))


@unittest.skipUnless(sys.platform == "darwin", "reads the real kernel clock (macOS)")
class LiveReadOnlyTests(LiveHardwareTestCase):
    def test_real_anchor_frequency_and_boot_read_without_privileges(self):
        measurement = clock.measure(base.Context())
        self.assertIsNone(measurement.error)
        self.assertEqual(measurement.values["frequency"]["modes"], 0)
        self.assertEqual(clock.read_boot_session_inprocess(),
                         measurement.values["boot_session_uuid"])
        self.assertLess(measurement.values["anchor"]["read_skew_ns"], 1_000_000)


class AnchorSkewFrequencyCoverageTests(unittest.TestCase):
    def journal(self, *, rejected_second, fail_frequency=False):
        from joulewise.hazards.monitor import DEFAULT_CADENCE

        clocks = FakeClocks()
        reader = FrequencyReader(clocks)
        ctx = base.Context(clocks=clocks)
        samples = []
        for second in range(16):
            # Twice the registered anchor skew bound rejects every try.
            clocks.preempt_ns = ([2 * clock.WINDOW_SKEW_MAX_NS] * clock.ANCHOR_TRIES
                                 if second == rejected_second else [])
            reader.fail = fail_frequency and second == rejected_second
            samples.append(clock.sample(ctx, frequency_reader=(
                reader if second % DEFAULT_CADENCE['frequency_s'] == 0 else None)))
            clocks.preempt_ns = []
            clocks.sleep(DEFAULT_CADENCE['clock_s'])
        return samples

    def test_anchor_only_skew_does_not_invalidate_last_successful_frequency(self):
        samples = self.journal(rejected_second=7)
        span = {'monotonic_ns': [samples[8]['finished']['monotonic_ns'],
                                  samples[9]['finished']['monotonic_ns']]}
        self.assertEqual(clock.span_findings(samples, span), [])
        around = {'monotonic_ns': [samples[6]['finished']['monotonic_ns'], span['monotonic_ns'][1]]}
        found = clock.span_findings(samples, around)
        self.assertEqual([f['code'] for f in found], ['clock.unmeasured'])
        self.assertEqual(found[0]['observed']['rule'], 'read_skew')

    def test_rejected_anchor_and_failed_scheduled_frequency_still_invalidates(self):
        samples = self.journal(rejected_second=10, fail_frequency=True)
        span = {'monotonic_ns': [samples[11]['finished']['monotonic_ns'],
                                  samples[14]['finished']['monotonic_ns']]}
        found = clock.span_findings(samples, span)
        self.assertEqual([f['code'] for f in found], ['clock.unmeasured'])
        self.assertIn('failed refresh', found[0]['detail'])


if __name__ == "__main__":
    unittest.main()
