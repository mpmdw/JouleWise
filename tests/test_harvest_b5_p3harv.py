"""Gate-prune round 3, lane P3-HARV: the block-5 harvest side of the P3 fixes.

Built on the synthetic window of ``tests/test_harvest_b5_window.py`` (real
strict validation, re-reduction and replays; fakes only at the named seams).

* The battery rule judges the 1 Hz SMC B0AC reads and applies the
  battery-assist ruling of 2026-10-06
  (night-archive/wallmeter-probe/verify/RULING_battery_assist_2026-10-06.md):
  charging, AC loss, a charge accumulator above the limit and missing
  evidence exclude; discharge is ``battery.assist`` (DISCLOSE), decided by the
  measured request only, with its energy in ``withheld/``.
* The calibration captures get the same rule (R3-5: a post capture is covered
  by the SMC reads after it, not by the next 60 s gauge publication).
* The historical calibration custody pass, the NEG-8 drop-reason binding, the
  KM003C meter hook, the NULL-window record (R3-4), the aborted-session desk
  reason (R3-3), the member-stderr marker scan and the mint's refusal to date
  a bound by its own clock (P2-B1 F2).
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise import whole_window
from joulewise.b5 import harvest as h
from tests import test_harvest_b5_window as base

NS = base.NS
T = base.REGISTERED_HARVEST_THRESHOLDS
L1Journal, parsed, battery_values = base.L1Journal, base.parsed, base.battery_values


def setUpModule():  # noqa: N802 (unittest hook)
    # The shared member template may have been removed by the other module's teardown.
    if base._TEMPLATE is not None and not base._TEMPLATE.exists():
        base._TEMPLATE = None


def tearDownModule():  # noqa: N802 (unittest hook)
    base.tearDownModule()
    base._TEMPLATE = None


def smc_values(current_ma: int, counter: int, voltage_mv: int = 12500) -> dict:
    """A ``source: smc`` battery line's values as L1's monitor writes them (``battery.smc_sample``).

    ``counter`` moves PSTR, so each read is a fresh SMC block (a repeated
    block is a frozen SMC and covers nothing).
    """
    return {"source": "smc", "smc": {"values": {"B0AC": current_ma, "B0AV": voltage_mv, "PDTR": 100.0,
                                                "PSTR": 100.0 + counter / 1000, "PPBR": 0.0},
                                     "errors": {}}}


def journal(*, current=lambda second: 0, smc_seconds=range(0, 300), publications=(0, 60, 120, 180, 240),
            registry=None, frozen=False) -> list:
    """A battery journal: gauge publications (registry overrides by second) and one SMC read a second.

    ``current(second)`` gives B0AC in mA; times are seconds on the
    ``base.publication_ns`` grid.
    """
    lines = L1Journal("battery")
    for second in publications:
        effect = base.publication_ns(second)
        values = {"power_telemetry": dict(base.STEADY_TELEMETRY), **(registry or {}).get(second, {})}
        lines.write("reading", effect + 2 * NS, effect + 2 * NS + 1_000,
                    values=battery_values(second + 10_000, **values))
    for second in smc_seconds:
        at = base.publication_ns(second) + 500_000_000
        lines.write("reading", at, at + 1_000, values=smc_values(current(second), 0 if frozen else second))
    return parsed(lines)


def window_ns(start_s: float, stop_s: float) -> list[int]:
    return [base.publication_ns(0) + round(start_s * NS), base.publication_ns(0) + round(stop_s * NS)]


class SmcBatteryRuleTests(unittest.TestCase):
    """Item 1: the harvest's battery rule on SMC B0AC at 1 Hz under the battery-assist ruling."""

    SPAN = window_ns(100, 130)
    REQUEST = window_ns(110, 120)

    def codes(self, readings, span=None, request=None):
        return [code for code, *_ in h.battery_member_flags(span or self.SPAN, readings, T,
                                                            request=request or self.REQUEST)]

    def test_discharge_in_the_request_is_assist_with_its_energy_withheld(self):
        # The module's worked example: 0, -865, -1200, 0 mA one second apart at 12.5 V.
        currents = {112: -865, 113: -1200}
        flags, energy = h.battery_join(self.SPAN, journal(current=lambda s: currents.get(s, 0)), T,
                                       request=self.REQUEST)
        codes = [code for code, *_ in flags]
        self.assertEqual(codes, ["battery.assist"])
        (_code, observed, interval), = flags
        request = observed["phases"]["request"]
        self.assertEqual((request["smc_reads_below"], request["smc_min_ma"], request["smc_duration_below_s"]),
                         (2, -1200, 2.0))
        self.assertTrue(observed["request_assist"])
        self.assertEqual(observed["phases"]["pre_request"]["smc_reads_below"], 0)
        # Each read is timed at its line's finished stamp (1 us after its start).
        self.assertEqual(interval["monotonic_ns"], [window_ns(112.5, 0)[0] + 1_000, window_ns(113.5, 0)[0] + 1_000])
        self.assertAlmostEqual(energy["phases"]["request"]["discharged_energy_j"], 0.865 * 12.5 + 1.2 * 12.5)
        self.assertNotIn("discharged_energy_j", json.dumps(observed))  # energies never reach the flag

    def test_charging_on_smc_excludes(self):
        readings = journal(current=lambda second: 865 if second == 115 else 0)
        flags = h.battery_member_flags(self.SPAN, readings, T, request=self.REQUEST)
        self.assertEqual([code for code, *_ in flags], ["battery.member_span"])
        self.assertEqual(flags[0][1]["violations"][0]["reasons"], ["smc_b0ac_charging_above_limit"])

    def test_assist_outside_the_request_decides_nothing(self):
        readings = journal(current=lambda second: -865 if second in (103, 125) else 0)
        flags = h.battery_member_flags(self.SPAN, readings, T, request=self.REQUEST)
        self.assertEqual([code for code, *_ in flags], ["battery.assist_outside_request"])
        observed = flags[0][1]
        self.assertFalse(observed["request_assist"])
        self.assertEqual({name: phase["smc_reads_below"] for name, phase in observed["phases"].items()},
                         {"pre_request": 1, "request": 0, "post_request": 1})

    def test_the_registry_current_is_not_judged_when_smc_covers_the_span(self):
        for current in (447, -447):
            with self.subTest(current=current):
                readings = journal(registry={60: {"instant_amperage_ma": current, "amperage_ma": current},
                                             120: {"instant_amperage_ma": current, "amperage_ma": current}})
                self.assertEqual(self.codes(readings), [])

    def test_a_gap_in_the_smc_reads_falls_back_to_the_registry(self):
        gap = [second for second in range(0, 300) if not 112 <= second <= 121]
        charging = journal(smc_seconds=gap, registry={120: {"instant_amperage_ma": 447}})
        self.assertEqual(self.codes(charging), ["battery.member_span", "battery.smc_unavailable"])
        discharge = journal(smc_seconds=gap, registry={120: {"instant_amperage_ma": -447}})
        self.assertEqual(self.codes(discharge), ["battery.smc_unavailable", "battery.assist"])

    def test_a_frozen_smc_block_is_not_coverage(self):
        self.assertEqual(self.codes(journal(frozen=True)), ["battery.smc_unavailable"])

    def test_state_still_excludes_with_smc_coverage(self):
        for override in ({"is_charging": True}, {"external_connected": False}):
            with self.subTest(override):
                readings = journal(registry={120: override})
                self.assertEqual(self.codes(readings), ["battery.member_span"])

    def test_a_registry_hole_under_smc_coverage_is_disclosed_not_unmeasured(self):
        # R3-5: the publication after the span was never journaled (the monitor stopped).
        readings = journal(publications=(0, 60), smc_seconds=range(0, 140))
        self.assertEqual(self.codes(readings), ["battery.accumulator_unavailable"])
        # Without SMC the same hole is missing evidence, as before.
        no_smc = journal(publications=(0, 60), smc_seconds=())
        self.assertIn("battery.unmeasured", self.codes(no_smc))

    def test_no_publication_before_the_span_is_missing_evidence_even_with_smc(self):
        readings = journal(publications=(120, 180))
        self.assertEqual(self.codes(readings), ["battery.unmeasured", "battery.accumulator_unavailable"])

    def test_the_discharge_accumulator_is_never_an_excursion(self):
        readings = base.battery_journal([(0, {"power_telemetry": base.JoinTests.EXCURSION[0]}),
                                         (60, {"power_telemetry": base.JoinTests.EXCURSION[1]})], end_s=120)
        codes = [code for code, *_ in h.battery_member_flags([base.publication_ns(10), base.publication_ns(20)],
                                                             readings, T)]
        self.assertNotIn("battery.accumulator_excursion", codes)
        self.assertIn("battery.assist", codes)

    def test_pair_current_only(self):
        self.assertTrue(h.pair_current_only(["pre InstantAmperage exceeds 200 mA"]))
        self.assertTrue(h.pair_current_only(["pre InstantAmperage exceeds 200 mA",
                                             "post InstantAmperage exceeds 200 mA"]))
        for reasons in ([], None, ["pre IsCharging is not No"],
                        ["pre InstantAmperage exceeds 200 mA", "post ExternalConnected is not Yes"],
                        ["pre InstantAmperage exceeds 200 mA", "pair stamps malformed"]):
            self.assertFalse(h.pair_current_only(reasons), reasons)


class WindowBatteryAssistTests(base.WindowTestCase):
    """Item 1 end to end: an SMC-covered window, one member's request assisted."""

    def test_a_discharge_in_one_request_is_disclosed_and_excludes_nothing(self):
        target = base.MEMBERS[2][0]
        request = base.request_span_ns(target)
        window = self.window(journals={
            "smc_current": lambda moment: -865 if request[0] - NS <= moment < request[0] + 2 * NS else 0})
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED", record["faults"])
        assist = [flag for flag in window.flags() if flag["code"] == "battery.assist"]
        self.assertEqual([flag["scope"]["run_id"] for flag in assist], [target])
        self.assertTrue(assist[0]["observed"]["request_assist"])
        self.assertEqual(assist[0]["observed"]["current_source"], "smc")
        self.assertNotIn("battery.smc_unavailable", window.codes())
        self.assertNotIn("battery.member_span", window.codes())
        self.assertNotIn(target, {row["run_id"] for row in window.exclusions()["members_excluded"]})
        withheld = json.loads((window.archive / "withheld" / "battery-assist.json").read_bytes())
        self.assertGreater(withheld["members"][target]["phases"]["request"]["discharged_energy_j"], 0)
        for path in (window.archive / "derived").iterdir():  # the energy never leaves withheld/
            self.assertNotIn(b"discharged_energy_j", path.read_bytes(), path.name)


class CaptureBatteryAssistTests(unittest.TestCase):
    """Item 2 (R3-5): calibration captures judged on the SMC reads, under the same ruling."""

    def join(self, capture, readings):
        ledger = h.FlagLedger(plan_id="p", attempt=1, catalog=h.Catalog.load(base.FIXTURES / "flag_catalog.json"),
                              boot_session_uuid=None)
        fake = SimpleNamespace(capture_assessments={"post-attempt": capture}, flags=ledger, emit=ledger.emit,
                               battery_assist={"members": {}, "captures": {}},
                               _record_error=lambda *args, **kwargs: None)
        return fake, ledger

    def run_join(self, capture, readings):
        fake, ledger = self.join(capture, readings)
        h._Harvest._capture_battery_joins(fake, readings, T)
        return [record["code"] for record in ledger.records], fake

    def test_a_post_capture_after_the_last_publication_is_covered_by_the_smc_reads(self):
        # The monitor stopped 6 s after the capture: no gauge publication after it.
        readings = journal(publications=(0, 60), smc_seconds=range(0, 136))
        capture = {"slot": "post", "battery_pair": "battery_float_evidence_missing", "span": window_ns(100, 130)}
        codes, _fake = self.run_join(capture, readings)
        self.assertEqual(codes, [])

    def test_charging_over_a_capture_removes_the_window_and_discharge_is_disclosed(self):
        capture = {"slot": "post", "battery_pair": "pass", "span": window_ns(100, 130)}
        codes, _fake = self.run_join(capture, journal(current=lambda second: 865 if second == 115 else 0))
        self.assertEqual(codes, ["calibration.capture_battery_span"])
        codes, fake = self.run_join(capture, journal(current=lambda second: -865 if second == 115 else 0))
        self.assertEqual(codes, ["calibration.capture_battery_assist"])
        self.assertAlmostEqual(fake.battery_assist["captures"]["post-attempt"]["phases"]["span"]
                               ["discharged_energy_j"], 0.865 * 12.5)

    def test_a_pair_that_failed_on_its_current_alone_is_disclosed_when_the_smc_shows_discharge(self):
        for current, expected in ((-865, ["calibration.capture_battery_assist",
                                          "calibration.capture_battery_pair_assist"]),
                                  (865, ["calibration.capture_battery_pair_failed",
                                         "calibration.capture_battery_span"])):
            with self.subTest(current=current):
                readings = journal(current=lambda second, current=current: current if second == 115 else 0)
                capture = {"slot": "post", "battery_pair": "battery_float_confounded", "span": window_ns(100, 130)}
                fake, ledger = self.join(capture, readings)
                record = ledger.emit("calibration.capture_battery_pair_failed", level="window",
                                     collector="calibration",
                                     observed={"slot": "post", "reasons": ["post InstantAmperage exceeds 200 mA"]})
                capture["pair_current_only_flag_id"] = record["flag_id"]
                h._Harvest._capture_battery_joins(fake, readings, T)
                self.assertEqual(sorted(item["code"] for item in ledger.records), expected)

    def test_without_smc_coverage_the_pair_exclusion_stands(self):
        readings = base.battery_journal([(0, {}), (60, {}), (120, {}), (180, {})])
        capture = {"slot": "pre", "battery_pair": "battery_float_confounded",
                   "span": [base.publication_ns(70), base.publication_ns(100)]}
        fake, ledger = self.join(capture, readings)
        record = ledger.emit("calibration.capture_battery_pair_failed", level="window", collector="calibration",
                             observed={"slot": "pre", "reasons": ["pre InstantAmperage exceeds 200 mA"]})
        capture["pair_current_only_flag_id"] = record["flag_id"]
        h._Harvest._capture_battery_joins(fake, readings, T)
        self.assertEqual([item["code"] for item in ledger.records], ["calibration.capture_battery_pair_failed"])


class MemberPairAssistTests(unittest.TestCase):
    """Ruling item 4 for members: a #421 pair failed on its current alone, with SMC-covered discharge."""

    def run_pair(self, codes):
        ledger = h.FlagLedger(plan_id="p", attempt=1, catalog=h.Catalog.load(base.FIXTURES / "flag_catalog.json"),
                              boot_session_uuid=None)
        record = ledger.emit("battery.capture_pair_failed", level="member", run_id="m1", collector="members",
                             observed={"status": "battery_float_confounded",
                                       "reasons": ["pre InstantAmperage exceeds 200 mA"]})
        fake = SimpleNamespace(pair_current_only={"m1": record["flag_id"]}, flags=ledger, emit=ledger.emit)
        h._Harvest._pair_assist(fake, {"m1": set(codes)}, {})
        return [item["code"] for item in ledger.records]

    def test_replaced_only_when_the_journal_shows_no_exclusion(self):
        self.assertEqual(self.run_pair({"battery.assist"}), ["battery.capture_pair_assist"])
        self.assertEqual(self.run_pair(set()), ["battery.capture_pair_assist"])
        for codes in ({"battery.member_span"}, {"battery.unmeasured"}, {"battery.accumulator_excursion"},
                      {"battery.smc_unavailable", "battery.assist"}):
            with self.subTest(codes):
                self.assertEqual(self.run_pair(codes), ["battery.capture_pair_failed"])


class Neg8BindingTests(unittest.TestCase):
    def test_the_accepted_drop_reasons_are_the_cores_own_set(self):
        """Item 4: one source, imported, so the harvest and the mint cannot drift apart."""
        self.assertIs(h.NEG8_ACCEPTED_DROP_REASONS, whole_window.NEG8_MINT_DROP_REASONS)

    def test_the_mint_never_dates_a_bound_by_its_own_clock(self):
        """Item 8 (P2-B1 F2): no kept member with a measured window end is a refusal."""
        with self.assertRaisesRegex(ValueError, "no kept member has a measured window end"):
            whole_window._hazard_bound_derived_at_s([{"span_end_s": None}, {}])
        self.assertEqual(whole_window._hazard_bound_derived_at_s([{"span_end_s": 5.0}, {"span_end_s": None},
                                                                  {"span_end_s": 7.5}]), 7.5)


class Neg8FixtureTests(base.WindowTestCase):
    def test_the_hazard_fixture_bound_is_dated_by_its_corpus_measurement(self):
        """Item 8: the harvest fixtures' corpus members have measured windows; the bound carries the latest end."""
        window = self.window()
        base.LineageFindingTests.publish(self, window)
        with base.hazard_member_gates(), base.mint_drops_patch([]):
            base.neg8_corpus_in_process(window)
        artifact = json.loads((window.bound / "neg8-drift-bound.json").read_bytes())
        self.assertEqual(artifact["freshness"]["derived_at_s"],
                         base.CORPUS_MEASURED_END_S + len(base.CORPUS_IDS) - 1)


class HistoricalCustodyTests(base.WindowTestCase):
    """Item 3: P2-VPF's historical_custody_report in the harvest."""

    def report(self, status, **extra):
        value = {"schema_version": "joulewise.calibration_historical_custody_report.v1", "status": status,
                 "observations": 3, "verified": 1, "mismatched": [], "unmeasured": [], "ledger_reasons": [],
                 "excluded_observations": 2, **extra}
        return mock.patch("joulewise.calibration_ledger.historical_custody_report", return_value=value)

    def test_own_session_only_is_unmeasured_and_disclosed(self):
        window = self.window()
        window.harvest()
        (flag,) = [flag for flag in window.flags() if flag["code"].startswith("calibration.historical_custody")]
        self.assertEqual((flag["code"], flag["observed"]["reason"]),
                         ("calibration.historical_custody_unmeasured", "no_observations_checked"))
        self.assertNotIn("calibration.historical_custody_unmeasured", window.exclusions()["reasons"])
        report = json.loads((window.archive / "derived" / "historical-custody.json").read_bytes())
        self.assertEqual(report["excluded_session_id"], base.SESSION_ID)

    def test_a_mismatch_removes_the_window(self):
        window = self.window()
        with self.report("mismatch", mismatched=[{"attempt_id": "old-pre", "reasons": ["x"]}]):
            window.harvest()
        (flag,) = [flag for flag in window.flags() if flag["code"] == "calibration.historical_custody_mismatch"]
        self.assertEqual(flag["observed"]["attempt_ids"], ["old-pre"])
        self.assertIn("calibration.historical_custody_mismatch", window.exclusions()["reasons"])

    def test_verified_emits_nothing(self):
        window = self.window()
        with self.report("verified"):
            window.harvest()
        self.assertFalse({code for code in window.codes() if code.startswith("calibration.historical_custody")})


class NullWindowTests(base.WindowTestCase):
    """R3-4: a NULL window says why it never launched."""

    def test_the_arm_error_is_a_flag(self):
        window = self.window()
        (window.custody / "night" / "chain.started").unlink()
        base.put(window.custody / "night" / "arm_decision.json", {
            "schema": "joulewise.b5_arm_decision.v1", "plan_id": base.PLAN_ID, "go": False,
            "verdicts": {"battery": "UNMEASURED"}, "not_pass": ["battery"],
            "reasons": ["the hazard arm raised: AssertionError: rig gap 42"],
            "arm_error": "AssertionError: rig gap 42"})
        record = window.harvest()
        self.assertEqual(record["verdict"], "NULL")
        (flag,) = [flag for flag in window.flags() if flag["code"] == "records.window_not_launched"]
        observed = flag["observed"]
        self.assertEqual((observed["arm_decision"], observed["go"], observed["arm_error_type"]),
                         ("read", False, "AssertionError"))
        self.assertEqual(observed["arm_error"], "AssertionError: rig gap ##")
        self.assertEqual(observed["not_pass"], ["battery"])

    def test_without_records_the_flag_says_so(self):
        window = self.window()
        (window.custody / "night" / "chain.started").unlink()
        window.harvest()
        (flag,) = [flag for flag in window.flags() if flag["code"] == "records.window_not_launched"]
        self.assertEqual((flag["observed"]["arm_decision"], flag["observed"]["hazard_result"]), ("absent", "absent"))


class AbortedSessionDeskTests(unittest.TestCase):
    """R3-3: the desk says the session was aborted, not a generic identity mismatch."""

    def problem(self, state):
        inputs = SimpleNamespace(ledger_path=Path("ledger.jsonl"), head_pin_path=Path("pin.json"),
                                 bracket_session_id="s1", measurement_root=Path("."))
        snapshot = SimpleNamespace(refusal_reasons=(), committed_head_sequence=5, committed_head_digest="d",
                                   bracket_session_by_id={"s1": SimpleNamespace(state=state)})
        with mock.patch("joulewise.calibration_ledger.terminal_head_pin_for_session",
                        return_value={"sequence": 5, "head_digest": "d"}), \
                mock.patch("joulewise.calibration_ledger.load_calibration_ledger_snapshot", return_value=snapshot):
            return h._Harvest._desk_pin_problem(SimpleNamespace(inputs=inputs))

    def test_an_aborted_session_is_named(self):
        self.assertEqual(self.problem("aborted")["reason"], "session_aborted")
        self.assertIsNone(self.problem("finalized"))


class MemberStderrMarkerTests(base.WindowTestCase):
    """Item 7: members' stderr copies are scanned for unwritten-flag markers."""

    def test_a_marker_line_in_a_member_stderr_copy_is_recovered(self):
        window = self.window()
        run_id = base.MEMBERS[0][0]
        line = base.UnwrittenCoreFlagTests.unwritten_line(
            "instrument.binary_identity_unmeasured", level="member", run_id=run_id,
            observed={"device_metadata": "no executable_sha256"})
        stderr_dir = window.custody / "operator-logs" / "member-stderr"
        stderr_dir.mkdir(parents=True)
        (stderr_dir / f"07-b5t-science--{run_id}.stderr").write_text(f"child output\n{line}\n")
        (stderr_dir / "ignored.txt").write_text(f"{line}\n")
        window.harvest()
        recovered = [flag for flag in window.flags() if flag["code"] == "instrument.binary_identity_unmeasured"]
        self.assertEqual([flag["scope"]["run_id"] for flag in recovered], [run_id])
        self.assertNotIn("records.malformed_flag", window.codes())


class MeterHookTests(base.WindowTestCase):
    """Item 5: the KM003C stream, disclosed; dE_machine and rho to withheld/ only."""

    def test_no_stream_is_a_disclosure_never_a_fault(self):
        window = self.window()
        record = window.harvest()
        self.assertNotEqual(record["verdict"], h.HARVEST_FAULT)
        (flag,) = [flag for flag in window.flags() if flag["code"] == "meter.absent"]
        self.assertEqual(flag["observed"]["streams"], 0)
        self.assertNotIn("meter.absent", window.exclusions()["reasons"])

    def test_a_stream_gives_the_member_cross_check_in_withheld(self):
        from tests.external.test_km003c_parse import Synthetic
        window = self.window()
        run_id = base.MEMBERS[0][0]
        baseline_start = base.member_span_ns(run_id)[0] - 5 * NS  # well before the idle baseline stage
        stream = Synthetic(start_ns=baseline_start + base.RAW_OFFSET_NS)
        busy = range(*[(edge - baseline_start) // (200 * 10**6) for edge in base.request_span_ns(run_id)])
        for index in range(60):  # 12 s of 200 ms polls at 50 SPS
            stream.poll(10, watts=90.0 if index in busy or index - 1 in busy else 60.0,
                        smc={"B0AC": -500 if index in busy else 0, "B0AV": 12500, "PDTR": 60.0, "PSTR": 60.0,
                             "PPBR": 0.0})
        stream.lines[0].update(start_raw_ns=base.RAW_OFFSET_NS, start_mono_ns=0)
        stream.lines.append({"k": "t", "end_raw_ns": base.RAW_OFFSET_NS, "end_mono_ns": 0, "utime_s": 0.1,
                             "stime_s": 0.1, "elapsed_s": 12.0})
        directory = window.custody / "hazards" / "meter"
        directory.mkdir(parents=True)
        stream.write(directory, "stream-001.jsonl")
        window.harvest()
        meter = json.loads((window.archive / "withheld" / h.METER_RECORD_NAME).read_bytes())
        row = meter["members"][run_id]
        self.assertEqual((row["stream"], row["offset_source"]), ("stream-001.jsonl", "stream"))
        self.assertGreater(row["machine"]["delta_J"], 0)
        self.assertTrue(row["machine"]["battery_term_available"])
        self.assertIsNotNone(row["rail_delta_J"])
        flags = [flag for flag in window.flags() if flag["code"].startswith("meter.")]
        activity = [flag for flag in flags if flag["code"] == "meter.battery_activity"]
        self.assertEqual([flag["scope"]["run_id"] for flag in activity], [run_id])
        self.assertNotIn("window_ns", activity[0]["observed"])
        catalog = h.Catalog.load(base.FIXTURES / "flag_catalog.json")
        self.assertEqual({catalog.effect(flag["code"]) for flag in flags}, {"DISCLOSE"})
        for flag in flags:  # structure only: no energy reaches a flag
            self.assertNotIn("delta_J", json.dumps(flag))


class P3CodeRegistrationTests(unittest.TestCase):
    """Every P3-HARV code classified alike in the draft, the fixture and the harvest."""

    EXPECTED = {
        "battery.smc_unavailable": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
        "battery.assist": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
        "battery.assist_outside_request": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
        "battery.capture_pair_assist": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
        "calibration.capture_battery_assist": ("CALIBRATION", "PHYSICS", "DISCLOSE"),
        "calibration.capture_battery_pair_assist": ("CALIBRATION", "PHYSICS", "DISCLOSE"),
        "calibration.historical_custody_mismatch": ("CALIBRATION", "NUMBER", "EXCLUDE_WINDOW"),
        "calibration.historical_custody_unmeasured": ("CALIBRATION", "NUMBER", "DISCLOSE"),
        "records.window_not_launched": ("RECORDS", "REPRESENTATION", "DISCLOSE"),
        **{code: ("DIAGNOSTIC", "PHYSICS", "DISCLOSE") for code in (
            "meter.absent", "meter.drops_excess", "meter.duplicates", "meter.clock_fit_residual",
            "meter.pdtr_gain_out_of_band", "meter.battery_activity", "meter.vbus_out_of_contract")},
    }

    def test_every_round_three_code_is_classified_everywhere(self):
        from joulewise.external import km003c_parse
        from joulewise.flags.catalog import DRAFT_CODES
        fixture = json.loads((base.FIXTURES / "flag_catalog.json").read_bytes())["codes"]
        self.assertEqual(set(self.EXPECTED), set(h.PRUNE3_CODES))
        self.assertLessEqual(set(km003c_parse.CODES), set(h.PRUNE3_CODES))
        for code, expected in self.EXPECTED.items():
            with self.subTest(code):
                self.assertEqual((DRAFT_CODES[code]["family"], DRAFT_CODES[code]["klass"],
                                  DRAFT_CODES[code]["effect"]), expected)
                self.assertEqual((fixture[code]["family"], fixture[code]["klass"], fixture[code]["effect"]),
                                 expected)
                self.assertEqual((h.CODES[code].family, h.CODES[code].klass), expected[:2])

    def test_no_discharge_only_exclusion_remains(self):
        """Ruling item 4 (Sol): the exclusion codes the battery rule emits are charging, AC loss or missing evidence."""
        self.assertEqual(h.BATTERY_EXCLUDING_CODES,
                         {"battery.member_span", "battery.accumulator_excursion", "battery.unmeasured"})


if __name__ == "__main__":
    unittest.main()
