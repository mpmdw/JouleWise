"""Synthetic regressions for the block-5 harvest mutation survivors.

Thresholds come from the shared fixture's registration 6.9 block; the clock
read-skew bound comes from L1's registered step-to-skew conversion.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.b5 import harvest as h
from joulewise.hazards.clock import window_skew_max_ns
from tests import test_harvest_b5_window as base
from tests.test_harvest_b5_p3harv import journal, window_ns
from tests.test_harvest_b5_window import REGISTERED_HARVEST_THRESHOLDS as T

NS = 1_000_000_000


def setUpModule():  # noqa: N802
    if base._TEMPLATE is not None and not base._TEMPLATE.exists():
        base._TEMPLATE = None


def tearDownModule():  # noqa: N802
    base.tearDownModule()
    base._TEMPLATE = None


class BatteryBoundaryTests(unittest.TestCase):
    def test_state_tail_gap_is_strictly_above_the_registered_limit(self):
        """A state tail at the limit is measured; one ns beyond is not. Kills M01499."""
        readings = journal(publications=(0,), smc_seconds=range(126))
        last_state = next(reading.monotonic_ns for reading in readings
                          if reading.values.get("source") != "smc")
        gap_ns = round(T["battery_unmeasured_gap_s"] * NS)
        for extra_ns, expected_holes in ((0, []), (1, [[last_state, None]])):
            with self.subTest(extra_ns=extra_ns):
                span = [window_ns(3, 0)[0], last_state + gap_ns + extra_ns]
                flags, _energy = h.battery_join(span, readings, T, request=span)
                missing = [observed for code, observed, _interval in flags
                           if code == "battery.unmeasured"]
                # Exact flag presence: bar 0; the mutant adds one exclusion.
                self.assertEqual(len(missing), int(bool(expected_holes)))
                if missing:
                    self.assertEqual(missing[0]["state_holes_monotonic_ns"], expected_holes)

    def test_discharge_count_excludes_the_exact_negative_limit(self):
        """Negative current assists, but only below -limit counts as below. Kills M03998."""
        limit = T["battery_limit_ma"]
        for current, below in ((-limit + 1, 0), (-limit, 0), (-limit - 1, 1)):
            with self.subTest(current=current):
                readings = journal(current=lambda second: current if second == 115 else 0,
                                   smc_seconds=range(140), publications=(0, 60, 120, 180))
                flags, _energy = h.battery_join(window_ns(100, 130), readings, T,
                                               request=window_ns(110, 120))
                self.assertEqual([code for code, *_rest in flags], ["battery.assist"])
                observed = flags[0][1]
                self.assertIs(observed["request_assist"], True)
                phase = observed["phases"]["request"]
                self.assertEqual(phase["smc_reads_negative"], 1)
                # Exact integer count: bar 0; the mutant adds one at equality.
                self.assertEqual(phase["smc_reads_below"], below)

    def test_request_ending_with_member_has_no_post_request_phase(self):
        """An assisted request ending at the member edge has no empty phase. Kills M00516."""
        readings = journal(current=lambda second: -1000 if second == 115 else 0,
                           smc_seconds=range(140), publications=(0, 60, 120, 180))
        span = window_ns(110, 120)
        flags, energy = h.battery_join(span, readings, T, request=span)
        self.assertEqual([code for code, *_rest in flags], ["battery.assist"])
        # Exact key presence: bar 0; the mutant adds post_request to both records.
        self.assertEqual(set(flags[0][1]["phases"]), {"request"})
        self.assertEqual(set(energy["phases"]), {"request"})
        self.assertEqual(flags[0][1]["phases"]["request"]["smc_reads_below"], 1)
        # One second at 1 A and 12.5 V is 12.5 J, exactly representable in binary64.
        self.assertEqual(energy["phases"]["request"]["discharged_energy_j"], 12.5)


class ContentionBoundaryTests(unittest.TestCase):
    def test_discordant_duplicate_keeps_the_larger_rate_in_either_order(self):
        """Duplicate outside-process evidence retains its higher rate. Kills M04091."""
        limit = T["contention_cpu_s_per_s"]
        high, low = limit + 0.001, limit / 5
        for first, second in ((high, low), (low, high)):
            with self.subTest(first=first):
                lines = base.L1Journal("contention")
                values = base.contention_values(0, 10 * NS, kernel_task=0)
                values.update(outside_over_limit=[{"pid": 400, "command": "synthetic", "cpu_s_per_s": first}],
                              outside_listed=[{"pid": 400, "command": "synthetic", "cpu_s_per_s": second}])
                lines.write("interval", 0, 10 * NS, values=values)
                flags = h.contention_member_flags([NS, 9 * NS], base.parsed(lines), T)
                # Exact flag presence: bar 0; retaining the low rate erases it.
                self.assertEqual([code for code, *_rest in flags], ["contention.request_overlap"])
                offender, = flags[0][1]["offenders"]
                self.assertEqual(flags[0][1]["offender_count"], 1)
                # bar: 1e-6 relative (COMMON fallback; no printed half-width).
                # The wrong rate differs by 0.041, over 800,000 times this bar.
                self.assertAlmostEqual(offender["cpu_s_per_s"], high, delta=high * 1e-6)

    def test_hole_starts_at_the_latest_ended_interval(self):
        """A nested interval cannot move the preceding coverage edge back. Kills M01535."""
        lines = base.L1Journal("contention")
        for start, stop in ((0, 10), (1, 2), (20, 30)):
            lines.write("interval", start * NS, stop * NS,
                        values=base.contention_values(start * NS, stop * NS, kernel_task=0))
        flags = h.contention_member_flags([11 * NS, 12 * NS], base.parsed(lines), T)
        self.assertEqual([code for code, *_rest in flags], ["contention.unmeasured"])
        # [0,10] covers farther than [1,2]: the hole is [10,20], all in seconds.
        # Exact integer timestamps: bar 0; the mutant moves the start by 8 s.
        self.assertEqual(flags[0][1]["holes_monotonic_ns"], [[10 * NS, 20 * NS]])
        self.assertEqual(flags[0][2]["monotonic_ns"], [10 * NS, 20 * NS])


class EmittedHarvestTests(unittest.TestCase):
    """Exercise persisted harvest output, with the existing synthetic window builder."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="b5-mutants-", dir=base.REAL_TMP)
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.ordinal = 0
        # This cache runs the real assessment on every distinct bundle's bytes.
        patcher = mock.patch.object(h, "assess_member", base.cached_assess)
        patcher.start()
        self.addCleanup(patcher.stop)

    def window(self):
        self.ordinal += 1
        return base.Window(self.root / str(self.ordinal))

    def clock_flags(self, move_ns, skew_ns):
        window = self.window()
        run_id = base.MEMBERS[0][0]
        start, _end = base.member_span_ns(run_id)
        lines = base.L1Journal("clock")
        for at, move, skew in ((start, 0, 0), (start + NS, move_ns, skew_ns)):
            # A zero frequency word leaves the residual equal to the anchor move.
            raw = at + base.RAW_OFFSET_NS
            anchor = 10**18 + move
            lines.write("reading", at, values={
                "anchor": {"anchor_ns": anchor, "monotonic_raw_ns": raw,
                           "realtime_ns": raw + anchor, "read_skew_ns": skew},
                "frequency": base.frequency_probe(0)})
        lines.dump(window.custody / "hazards/monitor/clock.jsonl")
        window.harvest(run_g3=False)
        return [flag for flag in window.flags()
                if flag["code"] == "clock.step_overlap" and flag["scope"]["run_id"] == run_id]

    def test_anchor_at_maximum_read_skew_still_emits_its_step(self):
        """An anchor at the allowed maximum skew remains usable. Kills M02602."""
        move = T["clock_step_ns"] + 1
        max_skew = window_skew_max_ns(T["clock_step_ns"])
        for skew, expected_count in ((max_skew, 1), (max_skew + 1, 0)):
            with self.subTest(skew=skew):
                flags = self.clock_flags(move, skew)
                # Exact flag presence: bar 0; the mutant hides the step at equality.
                self.assertEqual(len(flags), expected_count)
                if flags:
                    self.assertEqual(flags[0]["observed"]["residual_move_ns"], move)

    def test_negative_step_uses_the_magnitude_and_a_strict_limit(self):
        """A negative residual beyond the limit emits a step; equality does not. Kills M04137."""
        limit = T["clock_step_ns"]
        for move, expected_count in ((-limit, 0), (-limit - 1, 1)):
            with self.subTest(move=move):
                flags = self.clock_flags(move, 0)
                # Exact flag presence: bar 0; the mutant suppresses the negative step.
                self.assertEqual(len(flags), expected_count)
                if flags:
                    self.assertEqual(flags[0]["observed"]["residual_move_ns"], move)

    def place_request(self, window):
        """Give one synthetic member a ten-second request on a whole-second grid.

        Only the monitor-domain stamps change. The real assessment still runs,
        including its disclosures about the seed's independent raw timing.
        """
        run_id = base.MEMBERS[0][0]
        origin_s = base.member_span_ns(run_id)[0] // NS
        path = window.claim / run_id / "metadata.json"
        metadata = json.loads(path.read_bytes())
        stamps = metadata["uncertainty_evidence"]["clock_anchor"]["clock_stamps"]
        for name, seconds in (("pre_spawn", 0), ("sampling_started", 5),
                              ("sampling_stopped", 15), ("post_parse", 20)):
            stamps[name].update(monotonic_before_s=origin_s + seconds,
                                monotonic_after_s=origin_s + seconds)
        base.put(path, metadata)
        return run_id, origin_s * NS

    def test_kernel_task_cpu_seconds_are_clipped_to_each_request(self):
        """Persist clipped kernel CPU-seconds, including missing/fractional rates.

        Kills M04888, M07661, M07662 and M04889 through harvest, not its private helper.
        """
        for start, stop, rate, expected in ((0, 10, 0.5, 2.5), (10, 20, 0.5, 2.5),
                                            (0, 10, 1 / 3, 1.666667), (0, 10, None, None)):
            with self.subTest(interval=(start, stop), rate=rate):
                window = self.window()
                _run_id, origin = self.place_request(window)
                lines = base.L1Journal("contention")
                begin, end = origin + start * NS, origin + stop * NS
                values = base.contention_values(begin, end, kernel_task=rate or 0)
                if rate is None:
                    del values["kernel_task_cpu_s_per_s"]
                lines.write("interval", begin, end, values=values)
                lines.dump(window.custody / "hazards/monitor/contention.jsonl")
                window.harvest(run_g3=False)
                shares = [flag["observed"]["kernel_task_cpu_s_in_requests"] for flag in window.flags()
                          if flag["code"] == "contention.kernel_task_share"]
                # Each interval intersects [5,15] for 5 s: 0.5 x 5 = 2.5 CPU-s.
                # 2.5 is binary64-exact; wrong clipping adds 2.5, subtraction moves 5.
                # Missing rate: exact absence, bar 0 (M04888 erases present-rate flags).
                if expected is None:
                    self.assertEqual(shares, [])
                else:
                    self.assertEqual(len(shares), 1)
                    if rate == 0.5:
                        self.assertEqual(shares[0], 2.5)
                    else:
                        # Five thirds rounded to six emitted decimals is 1.666667.
                        # bar: 1e-6 relative (COMMON fallback; no printed half-width).
                        # Wrong clipping changes it by 1.666666: over 999,999 bars.
                        self.assertAlmostEqual(shares[0], expected, delta=expected * 1e-6)

    def test_two_valid_thermistor_reads_still_disclose_a_rise(self):
        """A failed middle read does not hide the rise between valid endpoints. Kills M06707."""
        window = self.window()
        base.put(window.claim / "campaign_manifests/stage.json", {
            "members": [], "config_dir": "/synthetic/stage",
            h.BATTERY_TEMPERATURE_MANIFEST_KEY: [
                {"temperature_centi_c": value, "error": "failed" if value is None else None}
                for value in (3000, None, 3310)]})
        window.harvest(run_g3=False)
        unmeasured = [flag["observed"] for flag in window.flags()
                      if flag["code"] == "thermal.battery_temperature_unmeasured"]
        self.assertEqual([(row["reason"], row["readings"], row["failed"]) for row in unmeasured],
                         [("readings_failed", 3, 1)])
        rises = [flag["observed"] for flag in window.flags() if flag["code"] == "thermal.stage_battery_rise"]
        # Exact flag count: bar 0; M06707 erases the rise disclosure.
        self.assertEqual(len(rises), 1)
        self.assertEqual(rises[0]["readings"], 2)
        self.assertIs(rises[0]["plateau"], False)
        # (3310 - 3000) hundredths C = 3.1 K; with two endpoints the spread is also 3.1 K.
        # bar: 1e-6 relative (COMMON fallback; no printed half-width).
        self.assertAlmostEqual(rises[0]["rise_k"], 3.1, delta=3.1e-6)
        self.assertAlmostEqual(rises[0]["last_three_spread_k"], 3.1, delta=3.1e-6)

    def test_idle_baseline_wall_fallback_reaches_persisted_assessment(self):
        """A baseline without an explicit monotonic start is still persisted. Kills M03873."""
        window = self.window()
        run_id = base.MEMBERS[0][0]
        window.harvest(run_g3=False)
        assessments = json.loads((window.archive / "withheld/member-assessments.json").read_bytes())
        member = assessments["members"][run_id]
        # The untouched seed has both idle-baseline wall events and a sampling
        # clock pair, so it supplies a complete two-endpoint baseline interval.
        # Exact interval presence/type/count: bar 0; M03873 replaces it with None.
        baseline = member["idle_baseline_span"]
        self.assertIsNotNone(baseline)
        self.assertEqual(len(baseline), 2)
        self.assertEqual([type(edge) for edge in baseline], [int, int])
        self.assertNotIn("idle_baseline_span", member["errors"])


if __name__ == "__main__":
    unittest.main()
