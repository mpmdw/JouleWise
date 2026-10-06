"""Clock hazard: positive controls for the frequency gate, the dwell residual,
steps, skew, frequency-word changes, reboots and probe failure."""
from __future__ import annotations

import sys
import unittest
from fractions import Fraction

from joulewise import kernel_clock
from joulewise.hazards import base, clock
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

    def test_frequency_3p7_ppm_at_335_s_refuses(self):
        clocks = FakeClocks(drift_word=ppm_word(3.7))
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        verdict = clock.judge(clock.measure(ctx, frequency_reader=FrequencyReader(clocks)), LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("frequency gate", verdict.reasons[0])
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
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertTrue(any("frequency word changed" in reason for reason in verdict.reasons))

    def test_boot_session_change_refuses(self):
        clocks = FakeClocks()
        verdict = clock.judge(dwell(clocks, 30, boot_end="0f6b5c4a-0000-4000-8000-000000000001"),
                              LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("boot session changed", verdict.reasons[0])

    def test_failed_sample_makes_the_dwell_unmeasured(self):
        clocks = FakeClocks()
        reader = FrequencyReader(clocks)
        ctx = base.Context(run=boot_runner(), clocks=clocks)
        started = ctx.stamp()
        samples = [clock.sample(ctx, frequency_reader=reader)]
        reader.fail = True
        samples.append(clock.sample(ctx, frequency_reader=reader))
        series = clock.series(samples, boot_start=BOOT_UUID, boot_end=BOOT_UUID, started=started,
                              finished=ctx.stamp())
        self.assertEqual(clock.judge(series, LIMITS).status, base.UNMEASURED)

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

    def test_gap_in_the_journal_is_unmeasured(self):
        clocks = FakeClocks()
        samples = self.journal(clocks, 20, FrequencyReader(clocks))
        clocks.sleep(30)
        samples += self.journal(clocks, 20, FrequencyReader(clocks))
        span = {"monotonic_ns": [samples[15]["finished"]["monotonic_ns"],
                                 samples[25]["finished"]["monotonic_ns"]]}
        self.assertIn("clock.unmeasured", [f["code"] for f in clock.span_findings(samples, span)])


@unittest.skipUnless(sys.platform == "darwin", "reads the real kernel clock (macOS)")
class LiveReadOnlyTests(unittest.TestCase):
    def test_real_anchor_frequency_and_boot_read_without_privileges(self):
        measurement = clock.measure(base.Context())
        self.assertIsNone(measurement.error)
        self.assertEqual(measurement.values["frequency"]["modes"], 0)
        self.assertEqual(clock.read_boot_session_inprocess(),
                         measurement.values["boot_session_uuid"])
        self.assertLess(measurement.values["anchor"]["read_skew_ns"], 1_000_000)


if __name__ == "__main__":
    unittest.main()
