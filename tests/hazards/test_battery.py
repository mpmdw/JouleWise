"""Battery hazard: positive controls from archived real ioreg bytes, the
accumulator unit check, and the in-span member rule (plan §3.4)."""
from __future__ import annotations

import json
import sys
import unittest

from joulewise import battery_float
from joulewise.hazards import base, battery
from tests.hazards.fakes import BATTERY, FakeClocks, Runner, battery_bytes, completed, update_time
from tests.hazards.fakes import ROOT

LIMITS = dict(battery.DEFAULT_THRESHOLDS)
REPO_BATTERY_FLOAT = ROOT / "tests" / "fixtures" / "battery_float"


def measure_bytes(raw: bytes, *, age_s: float = 22.0, returncode: int = 0, **kwargs):
    clocks = FakeClocks(wall_s=update_time(raw) + age_s if update_time(raw) else 1_791_249_487.0)
    runner = Runner({battery.IOREG_BATTERY_ARGV:
                     lambda argv: completed(argv, raw, returncode=returncode, **kwargs)})
    return battery.measure(base.Context(run=runner, clocks=clocks))


class ArmJudgeTests(unittest.TestCase):
    def test_todays_float_reading_passes(self):
        measurement = measure_bytes(battery_bytes("float-20261005-desk.ioreg"))
        verdict = battery.judge(measurement, LIMITS)
        self.assertEqual(verdict.status, base.PASS, verdict.reasons)
        self.assertEqual(verdict.observed["adapter_watts"], 140)
        self.assertEqual(measurement.values["voltage_mv"], 12180)
        self.assertEqual(measurement.raw[0].sha256,
                         base.sha256_hex(battery_bytes("float-20261005-desk.ioreg")))

    def test_charging_1716_ma_of_0925_refuses(self):
        verdict = battery.judge(measure_bytes(battery_bytes("charging-1716ma-synthetic-from-real.ioreg")),
                                LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertTrue(any("IsCharging" in reason for reason in verdict.reasons))
        self.assertTrue(any("1716 mA" in reason for reason in verdict.reasons))

    def test_minus_447_ma_on_ac_of_0930_0555Z_refuses(self):
        measurement = measure_bytes(battery_bytes("discharge-minus447ma-synthetic-from-real.ioreg"))
        verdict = battery.judge(measurement, LIMITS)
        self.assertEqual(measurement.values["instant_amperage_ma"], -447)
        self.assertTrue(measurement.values["external_connected"])
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertEqual(verdict.reasons, ("|InstantAmperage| 447 mA > 200 mA",))

    def test_on_battery_refuses(self):
        verdict = battery.judge(measure_bytes(battery_bytes("on-battery-synthetic-from-real.ioreg")),
                                LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("on battery", verdict.reasons[0])

    def test_reading_older_than_180_s_refuses(self):
        verdict = battery.judge(measure_bytes(battery_bytes("float-20261005-desk.ioreg"), age_s=240),
                                LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("stale", verdict.reasons[0])

    def test_grammar_refusal_is_unmeasured(self):
        verdict = battery.judge(measure_bytes(battery_bytes("malformed-synthetic-from-real.ioreg")),
                                LIMITS)
        self.assertEqual(verdict.status, base.UNMEASURED)

    def test_ioreg_timeout_and_exit_are_unmeasured(self):
        raw = battery_bytes("float-20261005-desk.ioreg")
        self.assertEqual(battery.judge(measure_bytes(raw, timed_out=True), LIMITS).status,
                         base.UNMEASURED)
        self.assertEqual(battery.judge(measure_bytes(raw, returncode=1), LIMITS).status,
                         base.UNMEASURED)
        self.assertEqual(battery.judge(measure_bytes(b"", error="FileNotFoundError"), LIMITS).status,
                         base.UNMEASURED)

    def test_frozen_grammar_is_reused_not_edited(self):
        self.assertIs(battery.IOREG_BATTERY_ARGV, battery_float.IOREG_BATTERY_ARGV)
        self.assertEqual(LIMITS["limit_ma"], battery_float.LIMIT_MA)
        self.assertEqual(LIMITS["max_update_age_s"], battery_float.MAX_UPDATE_AGE_S)


class AccumulatorUnitTests(unittest.TestCase):
    """The lane L1 unit check (module docstring), re-run on committed real bytes."""

    def test_line_reader_reads_power_telemetry_from_real_bytes(self):
        values = battery.read_accumulators(battery_bytes("float-20261005-desk.ioreg"))
        telemetry = values["power_telemetry"]
        self.assertEqual(telemetry["BatteryPowerAccumulatorCount"], 4727)
        self.assertEqual(telemetry["AccumulatedBatteryPower"], 71942641)
        self.assertEqual(telemetry["BatteryDischargeAccumulatorCount"], 23390)
        self.assertLess(telemetry["AccumulatedBatteryDischarge"], 0)  # two's complement decoded
        self.assertEqual(values["adapter_watts"], 140)

    def test_system_power_in_is_milliwatts_of_volts_times_amps(self):
        table = json.loads((BATTERY / "publications-20260925-20261005.json").read_text())
        rows = table["publications"]
        self.assertGreaterEqual(len(rows), 60)
        for row in rows:
            telemetry = row["power_telemetry"]
            product = telemetry["SystemVoltageIn"] * telemetry["SystemCurrentIn"] / 1000
            self.assertLess(abs(product - telemetry["SystemPowerIn"]) / telemetry["SystemPowerIn"],
                            0.02, row["update_time_s"])

    def test_load_minus_input_equals_minus_battery_accumulators_on_every_interval(self):
        rows = json.loads((BATTERY / "publications-20260925-20261005.json").read_text())["publications"]
        intervals = 0
        for earlier, later in zip(rows, rows[1:]):
            a, b = earlier["power_telemetry"], later["power_telemetry"]
            load_minus_in = ((b["AccumulatedSystemLoad"] - a["AccumulatedSystemLoad"])
                             - (b["AccumulatedSystemPowerIn"] - a["AccumulatedSystemPowerIn"]))
            battery_sum = ((b["AccumulatedBatteryDischarge"] - a["AccumulatedBatteryDischarge"])
                           + (b["AccumulatedBatteryPower"] - a["AccumulatedBatteryPower"]))
            self.assertEqual(load_minus_in, -battery_sum, (earlier["update_time_s"],
                                                            later["update_time_s"]))
            ticks = b["SystemPowerInAccumulatorCount"] - a["SystemPowerInAccumulatorCount"]
            elapsed = later["update_time_s"] - earlier["update_time_s"]
            self.assertTrue(0.97 <= ticks / elapsed <= 1.0, (ticks, elapsed))
            intervals += 1
        self.assertGreaterEqual(intervals, 60)

    def test_instant_battery_power_sign_from_the_one_nonzero_publication(self):
        post = battery.read_accumulators(battery_bytes("c2-d06-post-20261001.ioreg"))["power_telemetry"]
        self.assertEqual(post["BatteryPower"], -134)
        self.assertEqual(post["SystemLoad"], post["SystemPowerIn"] - post["BatteryPower"])

    def test_the_0555Z_minus_447_ma_episode_is_visible_in_the_discharge_accumulator(self):
        before = battery.parse_reading((ROOT / "tests/fixtures/battery_float/float-2026-09-25-2047.ioreg")
                                       .read_bytes(), 1790394405.0)
        after = battery.parse_reading(battery_bytes("c1-d01-pre-20261001.ioreg"), 1790836641.0)
        delta = battery.accumulator_interval(before, after)
        self.assertEqual(delta["discharge_ticks"], 22670 - 7627)
        gauge_mw = -447 * 12180 / 1000  # the archived 10-01 04:24:54Z reading
        self.assertAlmostEqual(delta["discharge_mean_mw"] / gauge_mw, 1.0, delta=0.006)

    def test_calibration_capture_assist_is_far_below_the_rule(self):
        pre = battery.parse_reading(battery_bytes("c2-d06-pre-20261001.ioreg"),
                                    update_time(battery_bytes("c2-d06-pre-20261001.ioreg")) + 1.0)
        post = battery.parse_reading(battery_bytes("c2-d06-post-20261001.ioreg"),
                                     update_time(battery_bytes("c2-d06-post-20261001.ioreg")) + 1.0)
        delta = battery.accumulator_interval(pre, post)
        self.assertEqual(delta["discharge_ticks"], 21)
        self.assertAlmostEqual(delta["discharge_mean_mw"], -139.38, places=2)
        self.assertEqual(delta["charge_ticks"], 0)
        self.assertIsNone(delta["charge_mean_mw"])
        self.assertEqual(pre["instant_amperage_ma"], 0)
        self.assertEqual(post["instant_amperage_ma"], 0)


def reading(raw: bytes, *, update: int, mono_ns: int, wall_offset_ns: int = 0,
            instant: int | None = None, telemetry: dict | None = None, error=None) -> dict:
    """A monitor journal reading built from real bytes, re-stamped on a test timeline."""

    values = battery.parse_reading(raw, float(update))
    values["update_time_s"] = update
    if instant is not None:
        values["instant_amperage_ma"] = instant
    if telemetry:
        values["power_telemetry"] = {**values["power_telemetry"], **telemetry}
    wall = update * 10**9 + 2 * 10**9 + wall_offset_ns
    stamp = {"wall_ns": wall, "monotonic_ns": mono_ns, "monotonic_raw_ns": mono_ns + 7}
    return {"started": stamp, "finished": stamp, "values": values, "error": error,
            "raw": [{"path": "monitor/raw/battery/x.ioreg", "sha256": "0" * 64}]}


class MemberSpanTests(unittest.TestCase):
    """The in-force publication rule and the accumulator rule on a 60 s gauge."""

    def setUp(self):
        self.raw = battery_bytes("float-20261005-desk.ioreg")
        self.t0 = 1_791_249_441
        self.mono0 = 5_000 * 10**9

    def series(self, count: int, *, special: dict[int, dict] | None = None) -> list[dict]:
        out = []
        base_telemetry = battery.read_accumulators(self.raw)["power_telemetry"]
        discharge = dict(count=base_telemetry["BatteryDischargeAccumulatorCount"],
                         total=base_telemetry["AccumulatedBatteryDischarge"])
        for index in range(count):
            extra = (special or {}).get(index, {})
            discharge["count"] += extra.get("ticks", 0)
            discharge["total"] += extra.get("energy", 0)
            update = self.t0 + 60 * index
            out.append(reading(self.raw, update=update,
                               mono_ns=self.mono0 + (update - self.t0 + 2) * 10**9,
                               instant=extra.get("instant"),
                               telemetry={"BatteryDischargeAccumulatorCount": discharge["count"],
                                          "AccumulatedBatteryDischarge": discharge["total"]}))
        return out

    def span(self, start_s: float, stop_s: float) -> dict:
        return {"monotonic_ns": [self.mono0 + int(start_s * 10**9), self.mono0 + int(stop_s * 10**9)]}

    def test_clean_float_gives_no_finding(self):
        self.assertEqual(battery.span_findings(self.series(10), self.span(130, 250)), [])

    def test_minus_447_ma_publication_inside_the_span_flags_the_member(self):
        readings = self.series(10, special={3: {"instant": -447}})
        codes = [f["code"] for f in battery.span_findings(readings, self.span(130, 250))]
        self.assertEqual(codes, ["battery.member_span"])

    def test_publication_after_the_span_is_in_force(self):
        readings = self.series(10, special={5: {"instant": -447}})  # publication at +300 s
        found = battery.span_findings(readings, self.span(200, 280))
        self.assertEqual([f["code"] for f in found], ["battery.member_span"])
        # ...but the one after that is not in force for an earlier span
        self.assertEqual(battery.span_findings(readings, self.span(10, 110)), [])

    def test_accumulator_mean_above_200_ma_times_volts_flags_between_clean_publications(self):
        # 20 discharge ticks averaging -3 W between two publications that both read 0 mA.
        readings = self.series(10, special={3: {"ticks": 20, "energy": -60_000}})
        found = battery.span_findings(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], ["battery.member_span"])
        self.assertIn("discharge accumulator mean -3000.0 mW", found[0]["detail"])

    def test_small_assist_is_disclosed_not_excluding(self):
        readings = self.series(10, special={3: {"ticks": 21, "energy": -2927}})
        found = battery.span_findings(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], ["battery.accumulator_activity"])

    def test_no_publication_for_more_than_120_s_is_unmeasured(self):
        readings = self.series(10)
        del readings[3:6]  # publications at +180, +240, +300 never observed
        codes = [f["code"] for f in battery.span_findings(readings, self.span(200, 260))]
        self.assertIn("battery.unmeasured", codes)


@unittest.skipUnless(sys.platform == "darwin", "reads the real gauge (macOS)")
class LiveReadOnlyTests(unittest.TestCase):
    def test_live_ioreg_parses_and_carries_accumulators(self):
        measurement = battery.measure(base.Context())
        self.assertIsNone(measurement.error)
        self.assertIsNotNone(measurement.values["power_telemetry"]["BatteryPowerAccumulatorCount"])


if __name__ == "__main__":
    unittest.main()
