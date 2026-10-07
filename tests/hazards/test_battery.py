"""Battery hazard: positive controls from archived real ioreg bytes, the
accumulator unit check, and the in-span member rule (plan §3.4)."""
from __future__ import annotations

import json
import sys
from typing import Any
import unittest
import unittest.mock

from joulewise import battery_float
from joulewise.hazards import base, battery, smc
from tests.hazards.fakes import BATTERY, FakeClocks, FakeSmc, Runner, battery_bytes, completed, update_time
from tests.hazards.fakes import ROOT

LIMITS = dict(battery.DEFAULT_THRESHOLDS)
REPO_BATTERY_FLOAT = ROOT / "tests" / "fixtures" / "battery_float"


def measure_bytes(raw: bytes, *, age_s: float = 22.0, returncode: int = 0, smc_ma: int | None = None,
                  smc_read=None, **kwargs):
    """The arm read on recorded ioreg bytes.  ``smc_ma``: a fake SMC reading
    that B0AC (``smc_read`` overrides it); neither: no SMC (the fallback)."""

    clocks = FakeClocks(wall_s=update_time(raw) + age_s if update_time(raw) else 1_791_249_487.0)
    runner = Runner({battery.IOREG_BATTERY_ARGV:
                     lambda argv: completed(argv, raw, returncode=returncode, **kwargs)})
    if smc_read is None and smc_ma is not None:
        smc_read = FakeSmc(clocks, current=lambda t: smc_ma)
    return battery.measure(base.Context(run=runner, clocks=clocks), smc_read=smc_read)


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


class SpanRig:
    """A 60 s gauge built from today's real float bytes, on a test timeline."""

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

    def registry_only(self, readings: list[dict], span: dict) -> list[dict]:
        """The join on a journal without SMC reads: the current falls back to the
        registry rule, disclosed first as battery.smc_unavailable; the rest is returned."""

        found = battery.span_findings(readings, span)
        self.assertEqual(found[0]["code"], battery.SMC_UNAVAILABLE)
        self.assertEqual(found[0]["observed"]["good_reads"], 0)
        return found[1:]

    def smc_lines(self, stop_s: int, *, current: dict[int, Any] | None = None,
                  missing: range = range(0), error_at: range = range(0),
                  frozen: range = range(0)) -> list[dict]:
        """The monitor's 1 s SMC lines from t = 0 to ``stop_s`` (0 mA unless set).

        PSTR changes every second as on the real SMC; inside ``frozen`` the
        whole block repeats the previous second's values."""

        out = []
        for second in range(stop_s + 1):
            if second in missing:
                continue
            mono = self.mono0 + second * 10**9
            stamp = {"wall_ns": (self.t0 - 2) * 10**9 + second * 10**9, "monotonic_ns": mono,
                     "monotonic_raw_ns": mono + 7}
            if second in error_at:
                sample = {"values": {key: None for key in smc.KEYS},
                          "errors": {key: f"{key}: OSError: IOConnectCallStructMethod returned 0xe00002c2"
                                     for key in smc.KEYS}}
                error = sample["errors"]["B0AC"]
            else:
                moment = second if second not in frozen else frozen.start - 1
                sample = {"values": {"B0AC": (current or {}).get(moment, 0), "B0AV": 12180,
                                     "PDTR": 48.1, "PSTR": 49.2 + 0.01 * moment, "PPBR": 0.41},
                          "errors": {}}
                error = None
            out.append({"started": stamp, "finished": stamp, "error": error, "raw": [],
                        "values": {"source": "smc", "smc": sample}})
        return out


class MemberSpanTests(SpanRig, unittest.TestCase):
    """The in-force publication rule and the accumulator rule on a 60 s gauge."""

    def test_clean_float_gives_no_finding(self):
        self.assertEqual(self.registry_only(self.series(10), self.span(130, 250)), [])

    def test_minus_447_ma_publication_inside_the_span_is_assist_not_exclusion(self):
        # Ruling 2026-10-06: discharge on AC is disclosed (battery.assist), never excluded.
        readings = self.series(10, special={3: {"instant": -447}})
        found = self.registry_only(readings, self.span(130, 250))
        self.assertEqual([f["code"] for f in found], [battery.ASSIST])
        observed = found[0]["observed"]
        self.assertEqual((observed["current_source"], observed["request_assist"]),
                         ("smc_partial_registry_fallback", True))
        self.assertEqual((observed["phases"]["span"]["registry_publications_below"],
                          observed["phases"]["span"]["registry_min_ma"]), (1, -447))

    def test_plus_447_ma_charging_publication_inside_the_span_flags_the_member(self):
        readings = self.series(10, special={3: {"instant": 447}})
        found = self.registry_only(readings, self.span(130, 250))
        self.assertEqual([f["code"] for f in found], ["battery.member_span"])
        self.assertIn("InstantAmperage +447 mA > +200 mA (charging)", found[0]["detail"])

    def test_publication_after_the_span_is_in_force(self):
        readings = self.series(10, special={5: {"instant": 447}})  # publication at +300 s
        found = self.registry_only(readings, self.span(200, 280))
        self.assertEqual([f["code"] for f in found], ["battery.member_span"])
        # ...but the one after that is not in force for an earlier span
        self.assertEqual(self.registry_only(readings, self.span(10, 110)), [])

    def test_discharge_accumulator_mean_above_200_ma_times_volts_is_assist(self):
        # 20 discharge ticks averaging -3 W between two publications that both read 0 mA.
        readings = self.series(10, special={3: {"ticks": 20, "energy": -60_000}})
        found = self.registry_only(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], [battery.ASSIST])
        self.assertEqual(found[0]["observed"]["phases"]["span"]["accumulator_intervals_over_limit"], 1)
        self.assertNotIn("discharge_energy_mw_ticks", json.dumps(found[0]["observed"]))

    def test_charge_accumulator_mean_above_200_ma_times_volts_flags_the_member(self):
        readings = self.series(10)
        base_telemetry = readings[3]["values"]["power_telemetry"]
        for item in readings[3:]:
            item["values"]["power_telemetry"] = dict(
                item["values"]["power_telemetry"],
                BatteryPowerAccumulatorCount=base_telemetry["BatteryPowerAccumulatorCount"] + 20,
                AccumulatedBatteryPower=base_telemetry["AccumulatedBatteryPower"] + 60_000)
        found = self.registry_only(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], ["battery.member_span"])
        self.assertIn("charge accumulator mean +3000.0 mW", found[0]["detail"])

    def test_small_assist_is_disclosed_not_excluding(self):
        readings = self.series(10, special={3: {"ticks": 21, "energy": -2927}})
        found = self.registry_only(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], ["battery.accumulator_activity"])

    def test_no_publication_for_more_than_120_s_is_unmeasured(self):
        readings = self.series(10)
        del readings[3:6]  # publications at +180, +240, +300 never observed
        codes = [f["code"] for f in self.registry_only(readings, self.span(200, 260))]
        self.assertIn("battery.unmeasured", codes)


class MemberSpanGapTests(SpanRig, unittest.TestCase):
    """Review findings (gate-prune L1 review): the gauge-averaged Amperage rule
    and the accumulator rule when one of its inputs cannot be read."""

    def test_gauge_averaged_amperage_above_200_ma_is_judged_even_at_zero_instant_current(self):
        readings = self.series(10)
        readings[3]["values"]["amperage_ma"] = 300  # InstantAmperage stays 0
        self.assertEqual(readings[3]["values"]["instant_amperage_ma"], 0)
        found = self.registry_only(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], ["battery.member_span"])
        self.assertIn("Amperage +300 mA > +200 mA", found[0]["detail"])
        readings[3]["values"]["amperage_ma"] = -300
        found = self.registry_only(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], [battery.ASSIST])
        self.assertEqual(found[0]["observed"]["phases"]["span"]["registry_min_ma"], -300)

    def test_unreadable_charge_counter_still_judges_discharge_and_discloses(self):
        # -3 W of discharge between two 0 mA publications, while the charge
        # counter is missing at the later one: the discharge rule must still run.
        readings = self.series(10, special={3: {"ticks": 20, "energy": -60_000}})
        readings[3]["values"]["power_telemetry"]["BatteryPowerAccumulatorCount"] = None
        found = self.registry_only(readings, self.span(130, 170))
        codes = [f["code"] for f in found]
        self.assertIn(battery.ASSIST, codes)
        self.assertIn("battery.accumulator_unavailable", codes)
        disclosed = next(f for f in found if f["code"] == "battery.accumulator_unavailable")
        self.assertIn("charge", disclosed["observed"]["unavailable"])
        self.assertNotIn("discharge", disclosed["observed"]["unavailable"])

    def test_counter_reset_is_disclosed_not_silently_passed(self):
        readings = self.series(10, special={3: {"ticks": -30_000, "energy": 0}})
        found = self.registry_only(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], ["battery.accumulator_unavailable"])
        self.assertIn("went backward", found[0]["detail"])

    def test_absent_power_telemetry_is_disclosed(self):
        readings = self.series(10)
        for item in readings:
            item["values"]["power_telemetry"] = {name: None for name in battery.ACCUMULATOR_FIELDS}
        found = self.registry_only(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], ["battery.accumulator_unavailable"])

    def test_each_sign_is_read_on_its_own(self):
        pre = {"power_telemetry": {"AccumulatedBatteryDischarge": -100, "BatteryDischargeAccumulatorCount": 10}}
        post = {"power_telemetry": {"AccumulatedBatteryDischarge": -3100, "BatteryDischargeAccumulatorCount": 11}}
        delta = battery.accumulator_interval(pre, post)
        self.assertFalse(delta["available"])
        self.assertIsNotNone(delta["charge_unavailable"])
        self.assertIsNone(delta["discharge_unavailable"])
        self.assertEqual(delta["discharge_mean_mw"], -3000)


class SmcArmJudgeTests(unittest.TestCase):
    """The arm's current rule reads SMC B0AC; the registry InstantAmperage is the
    cross-check, judged only when B0AC cannot be read (battery.smc_unavailable)."""

    def test_float_with_b0ac_zero_passes_on_the_smc_source(self):
        measurement = measure_bytes(battery_bytes("float-20261005-desk.ioreg"), smc_ma=0)
        verdict = battery.judge(measurement, LIMITS)
        self.assertEqual(verdict.status, base.PASS, verdict.reasons)
        self.assertEqual((verdict.observed["current_source"], verdict.observed["smc_current_ma"]),
                         ("smc", 0))
        self.assertEqual(verdict.observed["flags"], [])
        self.assertEqual(verdict.observed["instant_amperage_ma"], 0)  # the cross-check is kept
        self.assertEqual(measurement.values["smc"]["values"]["B0AV"], 12180)
        for key in ("started", "finished"):
            base.Stamp.from_json(measurement.values["smc"][key])

    def test_a_discharge_burst_the_registry_does_not_show_refuses(self):
        # The probe's 10-06 burst: B0AC -865 mA while every registry value read 0.
        verdict = battery.judge(measure_bytes(battery_bytes("float-20261005-desk.ioreg"), smc_ma=-865),
                                LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertEqual(verdict.reasons, ("|SMC B0AC| 865 mA > 200 mA",))

    def test_charging_current_above_the_limit_refuses_and_200_ma_does_not(self):
        raw = battery_bytes("float-20261005-desk.ioreg")
        self.assertEqual(battery.judge(measure_bytes(raw, smc_ma=201), LIMITS).status, base.REFUSE)
        self.assertEqual(battery.judge(measure_bytes(raw, smc_ma=200), LIMITS).status, base.PASS)
        self.assertEqual(battery.judge(measure_bytes(raw, smc_ma=-200), LIMITS).status, base.PASS)

    def test_a_stale_registry_current_is_the_cross_check_when_b0ac_reads(self):
        # The registry's -447 mA is up to 60 s old; B0AC now reads 0: the rule is on B0AC.
        verdict = battery.judge(measure_bytes(battery_bytes("discharge-minus447ma-synthetic-from-real.ioreg"),
                                              smc_ma=0), LIMITS)
        self.assertEqual(verdict.status, base.PASS, verdict.reasons)
        self.assertEqual(verdict.observed["instant_amperage_ma"], -447)

    def test_state_is_still_judged_from_the_registry(self):
        verdict = battery.judge(measure_bytes(battery_bytes("on-battery-synthetic-from-real.ioreg"),
                                              smc_ma=0), LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("on battery", verdict.reasons[0])

    def test_no_smc_falls_back_to_instant_amperage_and_discloses(self):
        for smc_read in (None, FakeSmc(FakeClocks()), lambda: 1 / 0):
            if isinstance(smc_read, FakeSmc):
                smc_read.fail = True
            with self.subTest(smc_read=smc_read):
                measurement = measure_bytes(battery_bytes("discharge-minus447ma-synthetic-from-real.ioreg"),
                                            smc_read=smc_read)
                verdict = battery.judge(measurement, LIMITS)
                self.assertEqual(verdict.reasons, ("|InstantAmperage| 447 mA > 200 mA",))
                self.assertEqual(verdict.observed["current_source"], "registry")
                self.assertEqual([flag["code"] for flag in verdict.observed["flags"]],
                                 [battery.SMC_UNAVAILABLE])
                self.assertIsNotNone(measurement.values["smc_unavailable"])

    def test_smc_read_failure_never_makes_the_reading_unmeasured(self):
        clocks_smc = FakeSmc(FakeClocks())
        clocks_smc.fail = True
        verdict = battery.judge(measure_bytes(battery_bytes("float-20261005-desk.ioreg"),
                                              smc_read=clocks_smc), LIMITS)
        self.assertEqual(verdict.status, base.PASS)


class SmcMemberSpanTests(SpanRig, unittest.TestCase):
    """The 200 mA member rule on the monitor's 1 s SMC B0AC reads (plan §3.4)."""

    def test_clean_float_with_smc_gives_no_finding(self):
        readings = self.series(10) + self.smc_lines(600)
        self.assertEqual(battery.span_findings(readings, self.span(130, 250)), [])

    def test_a_minus_865_ma_burst_between_clean_publications_is_assist_not_exclusion(self):
        # The probe's 10-06 burst.  Ruling 2026-10-06: disclosed, never excluded.
        readings = self.series(10) + self.smc_lines(600, current={150: -865, 151: -352})
        found = battery.span_findings(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], [battery.ASSIST])
        observed = found[0]["observed"]
        self.assertEqual((observed["current_source"], observed["request_assist"]), ("smc", True))
        self.assertEqual(observed["phases"]["span"],
                         {"smc_reads_in_force": 41, "smc_reads_below": 2, "smc_min_ma": -865,
                          "smc_duration_below_s": 2.0, "decides": True, "registry_publications_below": 0,
                          "registry_min_ma": None, "accumulator_intervals_over_limit": 0})
        # -865 mA x 12.18 V for 1 s plus -352 mA x 12.18 V for 1 s, withheld
        self.assertAlmostEqual(found[0]["withheld"]["phases"]["span"]["discharged_energy_j"],
                               (865 + 352) * 12180 / 1e6, places=9)
        self.assertNotIn("discharged_energy_j", json.dumps(found[0]["observed"]))
        self.assertEqual(found[0]["interval"]["monotonic_ns"],
                         [self.mono0 + 150 * 10**9, self.mono0 + 151 * 10**9])
        # a member a minute later is clean: B0AC is judged where it was read
        self.assertEqual(battery.span_findings(readings, self.span(200, 240)), [])

    def test_a_plus_865_ma_charging_burst_flags_the_member(self):
        readings = self.series(10) + self.smc_lines(600, current={150: 865, 151: 352})
        found = battery.span_findings(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], ["battery.member_span"])
        observed = found[0]["observed"]
        self.assertEqual((observed["source"], observed["rule"], observed["over_count"],
                          observed["max_abs_ma"]), ("smc", "charging", 2, 865))

    def test_assist_is_reported_per_phase_and_outside_the_request_decides_nothing(self):
        # Assist in warm-up (140 s) and in the request (160-161 s); the request is [150, 165].
        readings = self.series(10) + self.smc_lines(600, current={140: -900, 160: -500, 161: -500})
        request = {"monotonic_ns": self.span(150, 165)["monotonic_ns"]}
        found = battery.span_findings(readings, self.span(130, 170), request=request)
        self.assertEqual([f["code"] for f in found], [battery.ASSIST])
        phases = found[0]["observed"]["phases"]
        self.assertEqual(sorted(phases), ["post_request", "pre_request", "request"])
        self.assertEqual((phases["pre_request"]["smc_reads_below"], phases["pre_request"]["smc_min_ma"],
                          phases["pre_request"]["decides"]), (1, -900, False))
        self.assertEqual((phases["request"]["smc_reads_below"], phases["request"]["smc_min_ma"],
                          phases["request"]["smc_duration_below_s"], phases["request"]["decides"]),
                         (2, -500, 2.0, True))
        self.assertEqual(phases["post_request"]["smc_reads_below"], 0)
        self.assertAlmostEqual(found[0]["withheld"]["phases"]["request"]["discharged_energy_j"],
                               2 * 500 * 12180 / 1e6, places=9)
        # Assist in warm-up only: disclosed apart, not the member's assist marker.
        readings = self.series(10) + self.smc_lines(600, current={140: -900})
        found = battery.span_findings(readings, self.span(130, 170), request=request)
        self.assertEqual([f["code"] for f in found], [battery.ASSIST_OUTSIDE_REQUEST])
        self.assertFalse(found[0]["observed"]["request_assist"])
        # A request window not inside the span: the whole span decides.
        found = battery.span_findings(readings, self.span(130, 170),
                                      request={"monotonic_ns": self.span(120, 165)["monotonic_ns"]})
        self.assertEqual([f["code"] for f in found], [battery.ASSIST])
        self.assertEqual(list(found[0]["observed"]["phases"]), ["span"])

    def test_the_read_in_force_at_the_start_and_at_the_stop_counts(self):
        readings = self.series(10) + self.smc_lines(600, current={129: 250})
        self.assertEqual([f["code"] for f in battery.span_findings(readings, self.span(129.5, 170))],
                         ["battery.member_span"])
        self.assertEqual(battery.span_findings(readings, self.span(130.5, 170)), [])
        readings = self.series(10) + self.smc_lines(600, current={171: 250})
        self.assertEqual([f["code"] for f in battery.span_findings(readings, self.span(130, 170.5))],
                         ["battery.member_span"])
        readings = self.series(10) + self.smc_lines(600, current={171: -250})
        self.assertEqual([f["code"] for f in battery.span_findings(readings, self.span(130, 170.5))],
                         [battery.ASSIST])

    def test_the_registry_current_is_not_judged_when_smc_covers_the_span(self):
        # A -447 mA InstantAmperage and a -300 mA Amperage publication, B0AC 0 throughout.
        readings = self.series(10, special={3: {"instant": -447}}) + self.smc_lines(600)
        readings[3]["values"]["amperage_ma"] = -300
        self.assertEqual(battery.span_findings(readings, self.span(130, 250)), [])

    def test_registry_state_is_judged_even_when_smc_covers_the_span(self):
        readings = self.series(10) + self.smc_lines(600)
        readings[3]["values"]["is_charging"] = True
        found = battery.span_findings(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], ["battery.member_span"])
        self.assertIn("IsCharging", found[0]["detail"])

    def test_a_state_change_read_between_publications_flags_the_member(self):
        # The monitor re-reads ioreg when a polled field changes; a line with the
        # same UpdateTime is not a new publication, but its state is judged
        # where it was read (the harvest copy's per-poll rule).
        readings = self.series(10) + self.smc_lines(600)
        for field, value, text in (("is_charging", True, "IsCharging is Yes"),
                                   ("external_connected", False, "ExternalConnected is No")):
            with self.subTest(field=field):
                changed = json.loads(json.dumps(readings[3]))
                changed["values"][field] = value
                stamp = {"wall_ns": changed["started"]["wall_ns"] + 20 * 10**9,
                         "monotonic_ns": self.mono0 + 150 * 10**9, "monotonic_raw_ns": 0}
                changed["started"] = changed["finished"] = stamp
                found = battery.span_findings(readings + [changed], self.span(130, 170))
                self.assertEqual([f["code"] for f in found], ["battery.member_span"])
                self.assertIn(text, found[0]["detail"])
                self.assertEqual(battery.span_findings(readings + [changed], self.span(160, 200)), [])

    def test_an_unread_state_at_a_publication_is_missing_evidence_and_excludes(self):
        readings = self.series(10) + self.smc_lines(600)
        readings[3]["values"]["external_connected"] = None
        found = battery.span_findings(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], ["battery.member_span"])

    def test_the_accumulator_rule_still_runs_with_smc(self):
        readings = self.series(10, special={3: {"ticks": 20, "energy": -60_000}}) + self.smc_lines(600)
        found = battery.span_findings(readings, self.span(130, 170))
        # With SMC coverage the 1 s B0AC reads decide the marker; they read 0,
        # so the accumulator's interval mean is disclosed apart.
        self.assertEqual([f["code"] for f in found], [battery.ASSIST_OUTSIDE_REQUEST])
        self.assertEqual(found[0]["observed"]["phases"]["span"]["accumulator_intervals_over_limit"], 1)

    def test_a_gap_in_smc_reads_falls_back_to_the_registry_and_discloses(self):
        readings = (self.series(10, special={3: {"instant": -447}})
                    + self.smc_lines(600, missing=range(140, 150)))
        found = battery.span_findings(readings, self.span(130, 250))
        self.assertEqual([f["code"] for f in found], [battery.SMC_UNAVAILABLE, battery.ASSIST])
        self.assertEqual(found[0]["observed"]["gap_monotonic_ns"],
                         [self.mono0 + 139 * 10**9, self.mono0 + 150 * 10**9])
        self.assertEqual(found[1]["observed"]["phases"]["span"]["registry_min_ma"], -447)
        # a 5 s gap is still covered (the limit is "more than 5 s")
        readings = self.series(10) + self.smc_lines(600, missing=range(141, 145))
        self.assertEqual(battery.span_findings(readings, self.span(130, 250)), [])

    def test_unreadable_b0ac_counts_as_a_gap_and_names_the_error(self):
        readings = self.series(10) + self.smc_lines(600, error_at=range(100, 300))
        found = battery.span_findings(readings, self.span(130, 250))
        self.assertEqual([f["code"] for f in found], [battery.SMC_UNAVAILABLE])
        self.assertIn("0xe00002c2", found[0]["detail"])

    def test_a_burst_inside_a_gap_covered_span_still_flags(self):
        # SMC does not cover the span, but the reads it has are still judged.
        readings = self.series(10) + self.smc_lines(600, missing=range(160, 200), current={140: 865})
        codes = [f["code"] for f in battery.span_findings(readings, self.span(130, 250))]
        self.assertEqual(codes, ["battery.member_span", battery.SMC_UNAVAILABLE])
        readings = self.series(10) + self.smc_lines(600, missing=range(160, 200), current={140: -865})
        codes = [f["code"] for f in battery.span_findings(readings, self.span(130, 250))]
        self.assertEqual(codes, [battery.SMC_UNAVAILABLE, battery.ASSIST])

    def test_200_ma_either_way_is_within_the_limit_and_201_is_not(self):
        for value, codes in ((200, []), (-200, []), (201, ["battery.member_span"]),
                             (-201, [battery.ASSIST])):
            with self.subTest(value=value):
                readings = self.series(10) + self.smc_lines(600, current={150: value})
                self.assertEqual([f["code"] for f in battery.span_findings(readings, self.span(130, 170))],
                                 codes)

    def test_a_boolean_or_errored_b0ac_is_not_a_reading(self):
        readings = self.series(10) + self.smc_lines(600, current={second: True for second in range(601)})
        self.assertEqual([f["code"] for f in battery.span_findings(readings, self.span(130, 170))][:1],
                         [battery.SMC_UNAVAILABLE])
        # an integer beside a B0AC error is not trusted either
        readings = self.series(10) + self.smc_lines(600)
        for line in readings[10:]:
            line["values"]["smc"]["errors"] = {"B0AC": "B0AC: OSError: short reply"}
        found = battery.span_findings(readings, self.span(130, 170))
        self.assertEqual(found[0]["code"], battery.SMC_UNAVAILABLE)
        self.assertIn("short reply", found[0]["detail"])

    def test_reads_must_continue_past_the_stop_and_start_before_the_start(self):
        # The edge clauses of coverage_gap: a mutation of their > to >= is equivalent
        # (the gap to the next read is never shorter), so these pin presence instead.
        readings = self.series(10) + self.smc_lines(169)  # the stream ended before the stop
        self.assertEqual([f["code"] for f in battery.span_findings(readings, self.span(130, 175))][:1],
                         [battery.SMC_UNAVAILABLE])
        readings = self.series(10) + self.smc_lines(600, missing=range(0, 131))  # started late
        self.assertEqual([f["code"] for f in battery.span_findings(readings, self.span(124.5, 170))][:1],
                         [battery.SMC_UNAVAILABLE])
        self.assertEqual(battery.span_findings(readings, self.span(131, 170)), [])

    def test_a_frozen_smc_block_is_not_coverage(self):
        # The SMC answers but its block stops changing for 20 s: a repeat, not a reading.
        readings = (self.series(10, special={3: {"instant": -447}})
                    + self.smc_lines(600, frozen=range(140, 160)))
        found = battery.span_findings(readings, self.span(130, 170))
        self.assertEqual([f["code"] for f in found], [battery.SMC_UNAVAILABLE, battery.ASSIST])
        self.assertIn("repeated the previous SMC block", found[0]["detail"])
        self.assertEqual(found[0]["observed"]["gap_monotonic_ns"],
                         [self.mono0 + 139 * 10**9, self.mono0 + 160 * 10**9])
        # four frozen seconds are still covered
        readings = self.series(10) + self.smc_lines(600, frozen=range(140, 144))
        self.assertEqual(battery.span_findings(readings, self.span(130, 170)), [])

    def test_a_frozen_block_over_the_limit_still_flags(self):
        readings = self.series(10) + self.smc_lines(600, current={139: 900}, frozen=range(140, 160))
        codes = [f["code"] for f in battery.span_findings(readings, self.span(130, 170))]
        self.assertEqual(codes, ["battery.member_span", battery.SMC_UNAVAILABLE])
        readings = self.series(10) + self.smc_lines(600, current={139: -900}, frozen=range(140, 160))
        codes = [f["code"] for f in battery.span_findings(readings, self.span(130, 170))]
        self.assertEqual(codes, [battery.SMC_UNAVAILABLE, battery.ASSIST])

    def test_the_smc_read_attached_to_an_ioreg_line_counts(self):
        readings = self.series(10)
        sample = {"values": {"B0AC": -600, "B0AV": 12180}, "errors": {},
                  "finished": dict(readings[3]["finished"])}
        readings[3]["values"]["smc"] = sample
        samples = battery.smc_samples(readings)
        self.assertEqual([(entry["monotonic_ns"], entry["current_ma"]) for entry in samples],
                         [(readings[3]["finished"]["monotonic_ns"], -600)])


class FrozenGrammarRegistrationTests(unittest.TestCase):
    """The consumer guard of tests/test_battery_float_consumers.py (review BLOCKER).

    The guard walks every production file and refuses any reference to the
    grammar's primitives outside registered sites.  This package reads the
    grammar at exactly one site whose call text is the registered form, and
    writes no primitive name as a string."""

    SITE = ("joulewise/hazards/battery.py", "_grammar", "battery_float.parse(raw, wall_time_s)")
    # The coverage map's battery rows for the frozen module, pinned here because
    # battery.py reads them from the map (it may not write the parser's name).
    FROZEN_ROWS = {
        ("joulewise/battery_float.py", "_unsigned", "ProbeError malformed unsigned integer", 1),
        ("joulewise/battery_float.py", "_unsigned", "ProbeError integer exceeds 64 bits", 1),
        ("joulewise/battery_float.py", "_recorded_values", "ProbeError required <key>", 1),
        ("joulewise/battery_float.py", "_recorded_values", "ProbeError boolean <key>", 1),
        ("joulewise/battery_float.py", "_recorded_values", "ProbeError uint64 <key>", 1),
        ("joulewise/battery_float.py", "parse", "ProbeError UpdateTime stale: N s", 1),
        ("joulewise/battery_float.py", "parse", "reason 'ExternalConnected is not Yes'", 1),
        ("joulewise/battery_float.py", "parse", "reason 'IsCharging is not No'", 1),
        ("joulewise/battery_float.py", "parse", "reason 'InstantAmperage exceeds 200 mA'", 1),
        ("joulewise/battery_float.py", "require_pass", "require_pass ProbeError (probe_error)", 1),
        ("joulewise/battery_float.py", "require_pass", "require_pass ValueError (predicate failed)", 1),
    }

    def lane_files(self):
        return sorted((ROOT / "joulewise" / "hazards").glob("*.py")) + [ROOT / "scripts" / "hazard_monitor.py"]

    def test_the_package_meets_the_guard_with_one_registered_raw_boundary_site(self):
        from tests import test_battery_float_consumers as guard
        registered = set(guard.RAW_BOUNDARY_PARSE_CALLS) | {self.SITE}
        found = []
        with unittest.mock.patch.object(guard, "RAW_BOUNDARY_PARSE_CALLS", registered):
            for path in self.lane_files():
                relative = path.relative_to(ROOT).as_posix()
                found += guard.violations(relative, path.read_text())
        self.assertEqual(found, [])

    def test_the_single_site_is_the_registered_call_text(self):
        import ast
        tree = ast.parse((ROOT / self.SITE[0]).read_text())
        calls = [(function.name, ast.unparse(node)) for function in ast.walk(tree)
                 if isinstance(function, ast.FunctionDef) for node in ast.walk(function)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                 and isinstance(node.func.value, ast.Name) and node.func.value.id == "battery_float"
                 and node.func.attr == "parse"]
        self.assertEqual(calls, [self.SITE[1:]])

    def test_protects_carries_the_frozen_grammar_rows(self):
        loaded = {key for key in battery.PROTECTS if key[0] == "joulewise/battery_float.py"}
        self.assertEqual(loaded, self.FROZEN_ROWS)
        self.assertEqual(set(battery.frozen_grammar_rows()), self.FROZEN_ROWS)
        self.assertEqual(len(battery.PROTECTS), len(set(battery.PROTECTS)))

    def test_parse_reading_keeps_its_contract(self):
        raw = battery_bytes("float-20261005-desk.ioreg")
        stale = battery.parse_reading(raw, update_time(raw) + 400.0)
        self.assertEqual(stale["update_age_s"], 400.0)
        self.assertEqual(stale["instant_amperage_ma"], 0)
        with self.assertRaises(battery.ProbeError):
            battery.parse_reading(battery_bytes("malformed-synthetic-from-real.ioreg"),
                                  update_time(raw) + 1.0)


@unittest.skipUnless(sys.platform == "darwin", "reads the real gauge (macOS)")
class LiveReadOnlyTests(unittest.TestCase):
    def test_live_ioreg_parses_and_carries_accumulators(self):
        measurement = battery.measure(base.Context())
        self.assertIsNone(measurement.error)
        self.assertIsNotNone(measurement.values["power_telemetry"]["BatteryPowerAccumulatorCount"])

    def test_the_in_process_poll_reads_what_ioreg_prints(self):
        """RegistryReader's six fields equal the grammar's fields on ioreg bytes
        read between two polls that saw the same publication (and the test
        fake's reading of the same bytes, so the fake stands where the registry
        does)."""
        import time
        from tests.hazards.fakes import registry_values
        reader = battery.RegistryReader()
        self.addCleanup(reader.close)
        for _attempt in range(3):
            before = reader.read()
            completed_ioreg = base.run_probe(battery.IOREG_BATTERY_ARGV, battery.PROBE_TIMEOUT_S)
            after = reader.read()
            if before == after:
                break
        self.assertEqual(before, after, "the gauge published during every attempt")
        self.assertTrue(completed_ioreg.ok)
        values = battery.parse_reading(completed_ioreg.stdout, time.time())
        self.assertEqual(before, {"UpdateTime": values["update_time_s"],
                                  "ExternalConnected": values["external_connected"],
                                  "IsCharging": values["is_charging"],
                                  "InstantAmperage": values["instant_amperage_ma"],
                                  "Amperage": values["amperage_ma"], "Voltage": values["voltage_mv"]})
        self.assertEqual(before, registry_values(completed_ioreg.stdout))


if __name__ == "__main__":
    unittest.main()
