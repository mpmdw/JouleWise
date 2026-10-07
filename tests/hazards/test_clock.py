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
        self.assertEqual([f["code"] for f in clock.span_findings(samples, span)],
                         ["clock.step_overlap"])

    def test_step_across_a_failed_anchor_read_is_compared_across_the_gap(self):
        samples = self.journal_with_failure(2_000_000, fail_anchor=True)
        events = clock.window_events(samples)
        self.assertEqual([event["code"] for event in events], ["clock.step"])
        a, b = events[0]["interval"]["monotonic_ns"]
        self.assertEqual(a, samples[99]["started"]["monotonic_ns"])
        self.assertEqual(b, samples[101]["finished"]["monotonic_ns"])
        # a 2 s gap is under the 3 s coverage bound: no clock.unmeasured
        span = {"monotonic_ns": [a - 10**9, b + 10**9]}
        self.assertEqual([f["code"] for f in clock.span_findings(samples, span)],
                         ["clock.step_overlap"])

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
