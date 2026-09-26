"""Battery float parser and production-gate regressions from one real ioreg read."""
from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock

from joulewise import battery_float, night_gate
from tests import battery_float_corpus as corpus
from tests.git_fixture import init_git_fixture
from tests.test_night_gate import FakeProbeSource, REGISTRATION_TEXT, make_plan, result

FIXTURES = Path(__file__).parent / "fixtures/battery_float"
UPDATE = 1790373525

# Source bytes at the requested S0 base (64e39bb9). A309 changes only its
# own row after rebase; the lead regenerates this one table then.
FROZEN_FUNCTION_SOURCE_SHA256 = {
    "parse": "ccd50dd168b5ce128127a4f6f9e454b7715a4dcb01229bbe34cd03ecef23e865",
    "_structure": "988e36bb5acb54737e10183e26ff46e5dd1a1a7130156931fa7111f03dab9a60",
    "_recorded_values": "82256b7fa221253727d55b39feb793ef5e71e87d87ee707802e09d5f882f7468",
    "observe": "188a5709f352361b5364a703853a2bd02fc4a5e57fa1c74b274dea4b1f1b5d2e",
    "require_pass": "28c04bf25d88d342ceca917a801dfa5a12d191f4db5ea56c89a222b9d83045fe",
    "validate_window": "cda762184be73c6853c98679bac375e96fc44c8dd7a200b5f53a4c89079fcb4d",
    "predates_battery_float": "a387371550b0ac3f18b709ff5fa0288bf6e743660c52d402fb54ae413bb2fcee",
    "authenticate_committed_verdict": "1a4d783b9937e6d5dee26e1b02295898abd2170ef5b354573e2a88b7cad73522",
    "load_committed_verdict": "d1e9bc2257d908734a8433368fb8097ad769cea8bc1210b228025e0818a5809c",
    "compare_verdict": "d375ca6c5d514a2d2c62fd3ce999a3679936677463771b13cdb210ec677fa143",
}

# Exact canonical record from observe() at 64e39bb9 with a fixed clock and
# the committed float.ioreg fixture. Only the phase lexeme changes per call.
OBSERVE_GOLDEN = r'''{"amperage_ma":0,"apple_raw_current_capacity_mah":7591,"apple_raw_max_capacity_mah":7591,"argv":["/usr/sbin/ioreg","-r","-c","AppleSmartBattery"],"attempt_id":null,"current_capacity_pct":100,"exit_code":0,"external_connected":true,"external_connected_raw":"Yes","fully_charged":true,"instant_amperage_ma":0,"instant_amperage_raw":"0","is_charging":false,"is_charging_raw":"No","limit_ma":200,"max_update_age_s":180,"monotonic_after_ns":20,"monotonic_before_ns":10,"object_count":1,"passed":true,"phase":"arm_check","plan_id":"plan-1","policy_id":"bfg-01","probe_error":false,"property_lines":["      \"ExternalConnected\" = Yes","      \"IsCharging\" = No","      \"InstantAmperage\" = 0","      \"UpdateTime\" = 1790373525","      \"Amperage\" = 0","      \"Voltage\" = 12909","      \"Temperature\" = 3031","      \"FullyCharged\" = Yes","      \"CurrentCapacity\" = 100","      \"AppleRawCurrentCapacity\" = 7591","      \"AppleRawMaxCapacity\" = 7591"],"raw_path":"raw/battery_float.pre.ioreg","raw_stdout_sha256":"b42eb919dad653bc42dffac24df0512a4f9b315edbc928f79a1d31bd5b0766b4","reasons":[],"schema":"joulewise.battery_float.v1","session_id":"session-1","slot":null,"stderr":"","temperature_raw":3031,"timed_out":false,"update_age_s":1,"update_time_raw":"1790373525","update_time_s":1790373525,"voltage_mv":12909,"wall_time_s":1790373526}'''


def raw(name="float.ioreg"):
    return (FIXTURES / name).read_bytes()


def edit(source: bytes, old: bytes, new: bytes) -> bytes:
    assert source.count(old) == 1
    return source.replace(old, new)


class PairAuthenticationTests(unittest.TestCase):
    def pair(self, root, pre=None, post=None):
        directory = Path(root)
        (directory / "raw").mkdir(exist_ok=True)
        record = {}
        for phase, body in (("pre", raw() if pre is None else pre),
                            ("post", raw() if post is None else post)):
            path = f"raw/battery_float.{phase}.ioreg"
            (directory / path).write_bytes(body)
            clock = iter((10, 20) if phase == "pre" else (80, 90))
            observed, _ = battery_float.observe(
                phase=f"quiet_{phase}", raw_path=path, session_id="session-1",
                wall_time_s=UPDATE + 1, monotonic_ns=lambda: next(clock),
                runner=lambda argv, body=body: subprocess.CompletedProcess(argv, 0, body, b""))
            record[phase] = observed
        return record

    def authenticate(self, record, root, *, span=None):
        return battery_float.authenticate_pair(
            record, root, phases=("quiet_pre", "quiet_post"), identity="session-1", span=span)

    def test_custody_raises_before_confounded_or_missing_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = self.pair(tmp, pre=raw("charging-synthetic-from-real.ioreg"))
            record["post"]["exit_code"] = 2
            (Path(tmp) / "raw/battery_float.post.ioreg").unlink()
            with self.assertRaises(battery_float.CustodyFailure) as caught:
                self.authenticate(record, tmp)
            self.assertEqual(caught.exception.failures[0]["artifact"], "post")

    def test_structure_is_checked_before_raw_custody(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = self.pair(tmp)
            record["pre"]["phase"] = "wrong"
            (Path(tmp) / "raw/battery_float.pre.ioreg").unlink()
            result = self.authenticate(record, tmp)
            self.assertEqual(result.status, "battery_float_evidence_missing")
            self.assertIn("phase mismatch", result.reasons[0])

    def test_probe_failure_precedes_parse(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = self.pair(tmp, pre=b"invalid ioreg\n")
            record["pre"]["exit_code"] = 2
            result = self.authenticate(record, tmp)
            self.assertEqual(result.status, "battery_float_evidence_missing")
            self.assertIn("probe failed", result.reasons[0])
            self.assertNotIn("header", str(result.reasons))

    def test_parse_failure_precedes_predicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = self.pair(tmp, pre=b"invalid ioreg\n")
            record["pre"]["passed"] = True
            result = self.authenticate(record, tmp)
            self.assertEqual(result.status, "battery_float_evidence_missing")
            self.assertIn("header", result.reasons[0])

    def test_predicate_precedes_span_and_stored_pass_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = self.pair(tmp, pre=raw("charging-synthetic-from-real.ioreg"))
            record["pre"]["passed"] = True
            record["post"]["passed"] = False
            result = self.authenticate(record, tmp, span=(15, 100))
            self.assertEqual(result.status, "battery_float_confounded")
            self.assertTrue(any("IsCharging" in reason for reason in result.reasons))
            self.assertTrue(any("outside measured span" in reason for reason in result.reasons))

    def test_span_is_checked_after_passing_predicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = self.pair(tmp)
            self.assertEqual(self.authenticate(record, tmp, span=(20, 80)).status, "pass")
            result = self.authenticate(record, tmp, span=(15, 85))
            self.assertEqual(result.status, "battery_float_evidence_missing")
            self.assertEqual(sum("outside measured span" in r for r in result.reasons), 2)

    def test_future_update_time_passes_pair_today(self):
        future = edit(raw(), b'"UpdateTime" = 1790373525',
                      b'"UpdateTime" = 1790374525')
        with tempfile.TemporaryDirectory() as tmp:
            record = self.pair(tmp, pre=future, post=future)
            self.assertTrue(record["pre"]["passed"])
            result = self.authenticate(record, tmp)
            self.assertEqual(result.status, "pass")
            self.assertEqual((result.pre_update_age_s, result.post_update_age_s), (-999, -999))

    def test_quiet_wrapper_binds_session_span_and_round_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = self.pair(tmp)
            root = Path(tmp)
            (root / "session.json").write_text(json.dumps({
                "session": "session-1", "battery_float": record,
                "start_stamp": {"monotonic_before_s": 30e-9},
                "end_stamp": {"monotonic_after_s": 70e-9},
            }))
            hashes = {record[phase]["raw_path"]: record[phase]["raw_stdout_sha256"]
                      for phase in ("pre", "post")}
            (root / "rounds.jsonl").write_text(json.dumps({"raw": {"sha256": hashes}}) + "\n")
            self.assertEqual(battery_float.authenticate_quiet_session(root).status, "pass")
            hashes["raw/battery_float.post.ioreg"] = "0" * 64
            (root / "rounds.jsonl").write_text(json.dumps({"raw": {"sha256": hashes}}) + "\n")
            with self.assertRaises(battery_float.CustodyFailure):
                battery_float.authenticate_quiet_session(root)

    def test_capture_wrapper_uses_instrument_evidence_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = self.pair(tmp)
            for phase in ("pre", "post"):
                record[phase]["phase"] = f"slot_{phase}"
            (Path(tmp) / "instrument_evidence.json").write_text(json.dumps({"battery_float": record}))
            self.assertEqual(battery_float.authenticate_capture(tmp).status, "pass")


class BundleAuthenticationTests(unittest.TestCase):
    @staticmethod
    def event(phase, event_type, monotonic_ns):
        return {"timestamp_s": 100, "event_type": event_type, "phase": phase,
                "message": "stage boundary", "metadata": {"monotonic_ns": monotonic_ns}}

    def bundle(self, root, *, pre=None, post=None, events=None):
        directory = Path(root)
        (directory / "raw").mkdir(exist_ok=True)
        pair = {}
        for phase, body in (("pre", raw() if pre is None else pre),
                            ("post", raw() if post is None else post)):
            path = f"raw/battery_float.{phase}.ioreg"
            (directory / path).write_bytes(body)
            clock = iter((10, 20) if phase == "pre" else (80, 90))
            pair[phase], _ = battery_float.observe(
                phase=f"bundle_{phase}", raw_path=path, session_id="run-1",
                wall_time_s=UPDATE + 1, monotonic_ns=lambda: next(clock),
                runner=lambda argv, body=body: subprocess.CompletedProcess(argv, 0, body, b""))
        (directory / "metadata.json").write_text(json.dumps({
            "run_id": "run-1", "battery_float": pair,
        }))
        if events is None:
            events = [self.event("idle_baseline", "stage_started", 20),
                      self.event("idle_drift_sentinel", "stage_completed", 80)]
        (directory / "events.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in events))
        return pair

    def test_span_passes_at_inclusive_probe_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.bundle(tmp)
            verdict = battery_float.authenticate_bundle(tmp)
            self.assertEqual((verdict.kind, verdict.status, verdict.reasons),
                             ("bundle", "pass", ()))

    def test_pre_outside_span_is_evidence_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.bundle(tmp, events=[self.event("idle_baseline", "stage_started", 19),
                                     self.event("idle_drift_sentinel", "stage_completed", 80)])
            verdict = battery_float.authenticate_bundle(tmp)
            self.assertEqual(verdict.status, "battery_float_evidence_missing")
            self.assertEqual(verdict.reasons,
                             ("pre evidence missing: bundle_pre outside measured span",))

    def test_post_outside_span_is_evidence_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.bundle(tmp, events=[self.event("idle_baseline", "stage_started", 20),
                                     self.event("idle_drift_sentinel", "stage_completed", 81)])
            verdict = battery_float.authenticate_bundle(tmp)
            self.assertEqual(verdict.status, "battery_float_evidence_missing")
            self.assertEqual(verdict.reasons,
                             ("post evidence missing: bundle_post outside measured span",))

    def test_missing_event_or_field_refuses_as_unavailable_span(self):
        start = self.event("idle_baseline", "stage_started", 20)
        end = self.event("idle_drift_sentinel", "stage_completed", 80)
        cases = (("start event", [end]), ("end event", [start]),
                 ("start field", [{**start, "metadata": {}}, end]),
                 ("end field", [start, {**end, "metadata": {}}]))
        for name, events in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                self.bundle(tmp, events=events)
                verdict = battery_float.authenticate_bundle(tmp)
                self.assertEqual(verdict.status, "battery_float_evidence_missing")
                self.assertEqual(verdict.reasons, ("bundle span unavailable",))

    def test_invalid_or_reversed_monotonic_bounds_refuse(self):
        for start_value, end_value in ((-1, 80), (True, 80), (20.0, 80),
                                       ("20", 80), (20, -1), (20, False),
                                       (20, 80.0), (20, "80"), (81, 80)):
            with self.subTest(bounds=(start_value, end_value)), tempfile.TemporaryDirectory() as tmp:
                self.bundle(tmp, events=[self.event("idle_baseline", "stage_started", start_value),
                                         self.event("idle_drift_sentinel", "stage_completed", end_value)])
                verdict = battery_float.authenticate_bundle(tmp)
                self.assertEqual(verdict.status, "battery_float_evidence_missing")
                self.assertEqual(verdict.reasons, ("bundle span unavailable",))

    def test_first_start_and_last_end_govern_repeated_stages(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.bundle(tmp, events=[
                self.event("idle_baseline", "stage_started", 20),
                self.event("idle_baseline", "stage_started", 25),
                self.event("idle_drift_sentinel", "stage_completed", 75),
                self.event("idle_drift_sentinel", "stage_completed", 80),
            ])
            self.assertEqual(battery_float.authenticate_bundle(tmp).status, "pass")
        with tempfile.TemporaryDirectory() as tmp:
            self.bundle(tmp, events=[
                self.event("idle_baseline", "stage_started", 19),
                self.event("idle_baseline", "stage_started", 20),
                self.event("idle_drift_sentinel", "stage_completed", 80),
                self.event("idle_drift_sentinel", "stage_completed", 81),
            ])
            verdict = battery_float.authenticate_bundle(tmp)
            self.assertEqual(verdict.status, "battery_float_evidence_missing")
            self.assertEqual(len(verdict.reasons), 2)

    def test_custody_precedes_unavailable_span(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.bundle(tmp, events=[])
            (Path(tmp) / "raw/battery_float.post.ioreg").unlink()
            with self.assertRaises(battery_float.CustodyFailure):
                battery_float.authenticate_bundle(tmp)

    def test_probe_and_parse_precede_unavailable_span(self):
        with tempfile.TemporaryDirectory() as tmp:
            pair = self.bundle(tmp, events=[])
            pair["pre"]["exit_code"] = 2
            (Path(tmp) / "metadata.json").write_text(json.dumps({
                "run_id": "run-1", "battery_float": pair,
            }))
            verdict = battery_float.authenticate_bundle(tmp)
            self.assertEqual(verdict.status, "battery_float_evidence_missing")
            self.assertIn("probe failed", verdict.reasons[0])
        with tempfile.TemporaryDirectory() as tmp:
            self.bundle(tmp, pre=b"invalid ioreg\n", events=[])
            verdict = battery_float.authenticate_bundle(tmp)
            self.assertEqual(verdict.status, "battery_float_evidence_missing")
            self.assertIn("header", verdict.reasons[0])

    def test_predicate_precedes_unavailable_span(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.bundle(tmp, pre=raw("charging-synthetic-from-real.ioreg"), events=[])
            verdict = battery_float.authenticate_bundle(tmp)
            self.assertEqual(verdict.status, "battery_float_confounded")
            self.assertTrue(any("IsCharging" in reason for reason in verdict.reasons))


class S0FreezeTests(unittest.TestCase):
    def test_frozen_function_sources_match_base(self):
        for name, pinned in FROZEN_FUNCTION_SOURCE_SHA256.items():
            with self.subTest(name=name):
                actual = hashlib.sha256(inspect.getsource(getattr(battery_float, name)).encode()).hexdigest()
                self.assertEqual(actual, pinned)

    def test_observe_seven_old_phases_match_pre_s0_bytes(self):
        for phase in ("arm_check", "publish_install", "t0", "validate_install",
                      "t0_power_row", "slot_pre", "slot_post"):
            with self.subTest(phase=phase):
                clock = iter((10, 20))
                record, stdout = battery_float.observe(
                    phase=phase, runner=lambda argv: subprocess.CompletedProcess(argv, 0, raw(), b""),
                    wall_time_s=UPDATE + 1, monotonic_ns=lambda: next(clock),
                    raw_path="raw/battery_float.pre.ioreg", session_id="session-1", plan_id="plan-1")
                encoded = json.dumps(record, sort_keys=True, separators=(",", ":"))
                self.assertEqual(encoded.encode(), OBSERVE_GOLDEN.replace(
                    '"phase":"arm_check"', f'"phase":"{phase}"').encode())
                self.assertEqual(stdout, raw())


class ParserTests(unittest.TestCase):
    def test_object_structure_rejects_missing_brace_wrong_class_and_nested_properties(self):
        original = raw()
        cases = (
            original.rsplit(b"}", 1)[0],
            original.replace(b"+-o AppleSmartBattery  <", b"+-o OtherBattery  <", 1),
            b'+-o AppleSmartBattery  <class AppleSmartBattery, id 0x1>\n'
            b'    {\n      "Nested" = {\n'
            b'        "ExternalConnected" = Yes\n        "IsCharging" = No\n'
            b'        "InstantAmperage" = 0\n        "UpdateTime" = 1790373525\n'
            b'      }\n    }\n',
            original + b"unexpected trailer\n",
        )
        for changed in cases:
            with self.subTest(case=cases.index(changed)):
                with self.assertRaises(battery_float.ProbeError):
                    battery_float.parse(changed, UPDATE + 1)
                observed, _ = battery_float.observe(
                    phase="t0", runner=lambda argv: subprocess.CompletedProcess(argv, 0, changed, b""),
                    wall_time_s=UPDATE + 1)
                self.assertTrue(observed["probe_error"])

    def test_real_and_charging_fixtures(self):
        self.assertTrue(battery_float.parse(raw(), UPDATE + 179)["passed"])
        self.assertFalse(battery_float.parse(raw("charging-synthetic-from-real.ioreg"), UPDATE + 1)["passed"])

    def test_future_update_time_is_currently_a_pass(self):
        future = edit(raw(), b'"UpdateTime" = 1790373525',
                      b'"UpdateTime" = 1790374525')
        self.assertEqual(battery_float.parse(future, UPDATE)["update_age_s"], -1000)
        self.assertTrue(battery_float.parse(future, UPDATE)["passed"])

    def test_signed_lexemes_and_exact_boundaries(self):
        original = raw()
        for lexeme, expected, passed in ((b"18446744073709551458", -158, True),
                                         (b"200", 200, True), (b"18446744073709551416", -200, True),
                                         (b"201", 201, False), (b"18446744073709551415", -201, False)):
            with self.subTest(lexeme=lexeme):
                parsed = battery_float.parse(edit(original, b'"InstantAmperage" = 0',
                                                  b'"InstantAmperage" = ' + lexeme), UPDATE + 1)
                self.assertEqual(parsed["instant_amperage_raw"], lexeme.decode())
                self.assertEqual(parsed["instant_amperage_ma"], expected)
                self.assertEqual(parsed["passed"], passed)
        self.assertFalse(battery_float.parse(edit(original, b'"IsCharging" = No',
                                                  b'"IsCharging" = Yes'), UPDATE + 1)["passed"])

    def test_missing_duplicate_nested_alias_truncated_and_stale_fail_closed(self):
        original = raw()
        cases = [
            edit(original, b'      "InstantAmperage" = 0\n', b''),
            edit(original, b'      "InstantAmperage" = 0\n', b'      "InstantAmperage" = 0\n' * 2),
            edit(original, b'      "InstantAmperage" = 0\n', b'      "Amperage" = 0\n'),
            original + original,
            original[:100],
            edit(original, b'      "InstantAmperage" = 0\n', b'      "ChargingCurrent"=0\n'),
            edit(original, b'      "ExternalConnected" = Yes\n', b'      "AppleRawExternalConnected" = Yes\n'),
            raw("malformed-synthetic-from-real.ioreg"),
        ]
        for changed in cases:
            with self.subTest(case=cases.index(changed)):
                with self.assertRaises(battery_float.ProbeError):
                    battery_float.parse(changed, UPDATE + 1)
        self.assertTrue(battery_float.parse(original, UPDATE + 179)["passed"])
        with self.assertRaises(battery_float.ProbeError):
            battery_float.parse(original, UPDATE + 181)

    def test_probe_exit_timeout_and_staleness_are_errors(self):
        for runner in (
            lambda argv: subprocess.CompletedProcess(argv, 2, raw(), b"failed"),
            lambda argv: (_ for _ in ()).throw(subprocess.TimeoutExpired(argv, 10)),
        ):
            observation, _ = battery_float.observe(phase="t0", runner=runner, wall_time_s=UPDATE + 1)
            self.assertTrue(observation["probe_error"])
            self.assertFalse(observation["passed"])
        stale, _ = battery_float.observe(
            phase="t0", runner=lambda argv: subprocess.CompletedProcess(argv, 0, raw(), b""),
            wall_time_s=UPDATE + 181)
        self.assertEqual(stale["update_age_s"], 181)
        self.assertTrue(stale["probe_error"])

    def test_any_runner_failure_is_a_recorded_probe_error_never_a_pass(self):
        # A site's runner may raise its own error type (night_gate.ProbeError
        # is a RuntimeError); every site must still see a probe error.
        for error in (night_gate.ProbeError("runner"), FileNotFoundError("/usr/sbin/ioreg"),
                      RuntimeError("runner")):
            with self.subTest(error=type(error).__name__):
                def runner(argv, error=error):
                    raise error
                observation, stdout = battery_float.observe(phase="arm_check", runner=runner,
                                                            wall_time_s=UPDATE + 1)
                self.assertTrue(observation["probe_error"])
                self.assertFalse(observation["passed"])
                self.assertEqual(stdout, b"")
                with self.assertRaises(battery_float.ProbeError):
                    battery_float.require_pass(observation)
        mismatched, _ = battery_float.observe(
            phase="t0", wall_time_s=UPDATE + 1,
            runner=lambda argv: subprocess.CompletedProcess(("/bin/echo",), 0, raw(), b""))
        self.assertTrue(mismatched["probe_error"])

    def test_record_carries_the_ruled_schema_fields(self):
        observation, _ = battery_float.observe(
            phase="slot_pre", raw_path="raw/battery_float.pre.ioreg", session_id="s", slot="d01",
            attempt_id="s-d01", wall_time_s=UPDATE + 38,
            runner=lambda argv: subprocess.CompletedProcess(argv, 0, raw(), b""))
        ruled = {
            "schema", "policy_id", "limit_ma", "max_update_age_s", "phase", "plan_id", "session_id",
            "slot", "attempt_id", "wall_time_s", "monotonic_before_ns", "monotonic_after_ns", "argv",
            "exit_code", "timed_out", "stderr", "raw_stdout_sha256", "raw_path", "object_count",
            "property_lines", "external_connected_raw", "is_charging_raw", "instant_amperage_raw",
            "update_time_raw", "external_connected", "is_charging", "instant_amperage_ma",
            "update_time_s", "update_age_s", "amperage_ma", "voltage_mv", "temperature_raw",
            "fully_charged", "current_capacity_pct", "apple_raw_current_capacity_mah",
            "apple_raw_max_capacity_mah", "passed", "reasons",
        }
        self.assertLessEqual(ruled, set(observation))
        self.assertEqual(set(observation) - ruled, {"probe_error"})
        self.assertEqual((observation["schema"], observation["policy_id"], observation["limit_ma"],
                          observation["max_update_age_s"]), ("joulewise.battery_float.v1", "bfg-01", 200, 180))
        self.assertEqual(observation["update_age_s"], 38)
        self.assertEqual(observation["apple_raw_current_capacity_mah"], 7591)
        self.assertEqual(observation["apple_raw_max_capacity_mah"], 7591)
        self.assertTrue(observation["passed"])
        self.assertEqual(observation["argv"], ["/usr/sbin/ioreg", "-r", "-c", "AppleSmartBattery"])
        self.assertEqual(battery_float.PROBE_TIMEOUT_S, 10)


class GateTests(unittest.TestCase):
    def test_wrong_object_structure_is_night_probe_error_at_both_gate_entries(self):
        original = raw()
        cases = (
            original.rsplit(b"}", 1)[0],
            original.replace(b"+-o AppleSmartBattery  <", b"+-o OtherBattery  <", 1),
            b'+-o AppleSmartBattery  <class AppleSmartBattery, id 0x1>\n'
            b'    {\n      "Nested" = {\n'
            b'        "ExternalConnected" = Yes\n        "IsCharging" = No\n'
            b'        "InstantAmperage" = 0\n        "UpdateTime" = 1000\n'
            b'      }\n    }\n',
            original + b"unexpected trailer\n",
        )
        for changed in cases:
            for dynamic in (False, True):
                with self.subTest(case=cases.index(changed), dynamic=dynamic):
                    source = FakeProbeSource()
                    source.results[night_gate.IOREG_BATTERY_ARGV] = result(
                        night_gate.IOREG_BATTERY_ARGV, stdout=changed)
                    receipt = self.evaluate(source, dynamic=dynamic)
                    self.assertIsNotNone(receipt.refusal)
                    self.assertEqual(receipt.refusal.reason, "night_probe_error")

    def evaluate(self, source, *, dynamic=False):
        plan = make_plan()
        if dynamic:
            from dataclasses import replace
            from tests.test_quiet_admission import POLICY
            plan = replace(plan, window_max_s=9600, quiet_admission=dict(POLICY))
        with mock.patch.object(night_gate, "D166_REGISTRATION_SHA256",
                               hashlib.sha256(REGISTRATION_TEXT.encode()).hexdigest()):
            if dynamic:
                static = night_gate.evaluate_static(plan, source.probes())
                self.assertIsNone(static.refusal)
                return night_gate.evaluate_dynamic_hard(plan, source.probes(), static)
            return night_gate.evaluate_night(plan, source.probes())

    def test_charging_refuses_both_gate_paths_with_c3_raw_text(self):
        charging = edit(raw("charging-synthetic-from-real.ioreg"),
                        b'"UpdateTime" = 1790373525', b'"UpdateTime" = 1000')
        for dynamic in (False, True):
            source = FakeProbeSource()
            source.results[night_gate.IOREG_BATTERY_ARGV] = result(
                night_gate.IOREG_BATTERY_ARGV, stdout=charging)
            receipt = self.evaluate(source, dynamic=dynamic)
            self.assertEqual(receipt.verdict, "REFUSED")
            self.assertEqual(receipt.refusal.reason, "night_refused_battery_float")
            battery = receipt.conditions[2].measured["battery_float"]
            self.assertEqual(battery["raw_stdout"], charging.decode())
            self.assertFalse(battery["passed"])

    def test_stale_is_probe_error_and_fresh_passes(self):
        for age, expected in ((181, "night_probe_error"), (179, None)):
            source = FakeProbeSource()
            fresh = edit(raw(), b'"UpdateTime" = 1790373525',
                         f'"UpdateTime" = {1005 - age}'.encode())
            source.results[night_gate.IOREG_BATTERY_ARGV] = result(
                night_gate.IOREG_BATTERY_ARGV, stdout=fresh)
            receipt = self.evaluate(source)
            self.assertEqual(receipt.refusal.reason if receipt.refusal else None, expected)


class WindowTests(unittest.TestCase):
    def test_future_update_time_passes_derivation_window_today(self):
        future = edit(raw(), b'"UpdateTime" = 1790373525',
                      b'"UpdateTime" = 1790374525')
        with tempfile.TemporaryDirectory() as tmp:
            session, _ = self.make_session(tmp, future, future, wall=UPDATE)
            self.assertEqual(battery_float.validate_window(session)["status"], "pass")

    def test_wrong_object_structure_is_evidence_missing_in_window(self):
        original = raw()
        cases = (
            original.rsplit(b"}", 1)[0],
            original.replace(b"+-o AppleSmartBattery  <", b"+-o OtherBattery  <", 1),
            b'+-o AppleSmartBattery  <class AppleSmartBattery, id 0x1>\n'
            b'    {\n      "Nested" = {\n'
            b'        "ExternalConnected" = Yes\n        "IsCharging" = No\n'
            b'        "InstantAmperage" = 0\n        "UpdateTime" = 1790373525\n'
            b'      }\n    }\n',
            original + b"unexpected trailer\n",
        )
        for changed in cases:
            with self.subTest(case=cases.index(changed)), tempfile.TemporaryDirectory() as tmp:
                session, _ = self.make_session(tmp, changed, changed)
                self.assertEqual(battery_float.validate_window(session)["status"],
                                 "battery_float_evidence_missing")

    def make_session(self, root, pre, post, *, wall=UPDATE + 1):
        custody = Path(root) / "attempt"
        (custody / "raw").mkdir(parents=True)
        battery = {}
        for phase, body in (("pre", pre), ("post", post)):
            path = f"raw/battery_float.{phase}.ioreg"
            if body is not None:
                (custody / path).write_bytes(body)
                record, _ = battery_float.observe(
                    phase=f"slot_{phase}", raw_path=path, wall_time_s=wall,
                    runner=lambda argv, body=body: subprocess.CompletedProcess(argv, 0, body, b""))
                battery[phase] = record
        evidence = json.dumps({"battery_float": battery}).encode()
        (custody / "instrument_evidence.json").write_bytes(evidence)
        observation = SimpleNamespace(custody_locator=str(custody), attempt_id="a01",
                                      artifact_sha256={"instrument_evidence.json": hashlib.sha256(evidence).hexdigest()})
        return SimpleNamespace(finalized_slots={"s01": observation}, declared_slots=("s01", "s02"),
                               abort_reason="window_exhausted"), custody

    def test_diagnostic_delta_and_unused_slot(self):
        with tempfile.TemporaryDirectory() as tmp:
            pre = edit(raw(), b'"AppleRawCurrentCapacity" = 7591', b'"AppleRawCurrentCapacity" = 7516')
            session, _ = self.make_session(tmp, pre, raw())
            result = battery_float.validate_window(session)
            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["slots"][0]["delta_q_mah"], 75)
            self.assertEqual(len(result["slots"]), 1)

    def test_missing_post_and_tampering_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            session, custody = self.make_session(tmp, raw(), None)
            self.assertEqual(battery_float.validate_window(session)["status"], "battery_float_evidence_missing")
            (custody / "raw/battery_float.pre.ioreg").write_bytes(b"tampered")
            # Obligations v1.1 §4.1 / A10: recorded bytes that no longer match
            # their digest are a custody failure, never a verdict.
            with self.assertRaisesRegex(battery_float.CustodyFailure, r"s01/pre expected [0-9a-f]{64} observed"):
                battery_float.validate_window(session)

    def test_confounded_takes_precedence_over_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            session, _ = self.make_session(tmp, raw("charging-synthetic-from-real.ioreg"), None)
            self.assertEqual(battery_float.validate_window(session)["status"], "battery_float_confounded")

    def test_stale_at_harvest(self):
        with tempfile.TemporaryDirectory() as tmp:
            session, _ = self.make_session(tmp, raw(), raw(), wall=UPDATE + 181)
            self.assertEqual(battery_float.validate_window(session)["status"], "battery_float_evidence_missing")


def custody_session(root, slots, *, wall=UPDATE + 1):
    """A finalized session whose rows authenticate their evidence files.

    ``slots`` maps slot -> {phase: (stdout, returncode)}; an absent phase is
    unrecorded.  Each recorded phase's raw bytes are written exactly as the
    capture writer writes them (unconditionally, possibly empty).
    """
    finalized = {}
    for slot, phases in slots.items():
        custody = Path(root) / slot
        (custody / "raw").mkdir(parents=True)
        battery = {}
        for phase, (body, code) in phases.items():
            path = f"raw/battery_float.{phase}.ioreg"
            (custody / path).write_bytes(body)
            record, _ = battery_float.observe(
                phase=f"slot_{phase}", raw_path=path, wall_time_s=wall,
                runner=lambda argv, body=body, code=code: subprocess.CompletedProcess(argv, code, body, b""))
            battery[phase] = record
        evidence = json.dumps({"battery_float": battery}).encode()
        (custody / "instrument_evidence.json").write_bytes(evidence)
        finalized[slot] = SimpleNamespace(
            custody_locator=str(custody), attempt_id=f"W-{slot}",
            identity_epoch={"os_build": "25G83"},
            artifact_sha256={"instrument_evidence.json": hashlib.sha256(evidence).hexdigest()})
    return SimpleNamespace(session_id="W1", session_kind="derivation", state="finalized",
                           finalized_slots=finalized, declared_slots=tuple(slots))


def clean_phases():
    return {"pre": (raw(), 0), "post": (raw(), 0)}


class CustodyRuleTests(unittest.TestCase):
    """Obligations v1.1 §4.1 / §4.10 item 1 (a)-(g), at `validate_window`."""

    build = staticmethod(custody_session)

    def clean(self):
        return clean_phases()

    def test_a_deleted_recorded_raw_file_is_a_custody_failure_naming_slot_and_phase(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = self.build(tmp, {"d03": self.clean()})
            (Path(tmp) / "d03/raw/battery_float.post.ioreg").unlink()
            with self.assertRaises(battery_float.CustodyFailure) as caught:
                battery_float.validate_window(session)
            self.assertIn("d03/post expected ", str(caught.exception))
            self.assertIn(" observed absent", str(caught.exception))
            [failure] = caught.exception.failures
            self.assertEqual((failure["slot"], failure["attempt_id"], failure["artifact"],
                              failure["observed_sha256"]), ("d03", "W-d03", "post", None))
            self.assertNotIsInstance(caught.exception, (OSError, KeyError, TypeError, ValueError))

    def test_b_one_appended_byte_is_a_custody_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = self.build(tmp, {"d01": self.clean()})
            path = Path(tmp) / "d01/raw/battery_float.pre.ioreg"
            path.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaisesRegex(battery_float.CustodyFailure, r"d01/pre expected "):
                battery_float.validate_window(session)

    def test_c_altered_evidence_file_is_a_custody_failure_naming_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = self.build(tmp, {"d01": self.clean()})
            path = Path(tmp) / "d01/instrument_evidence.json"
            path.write_bytes(path.read_bytes().replace(b"{", b'{"x": 1, ', 1))
            with self.assertRaisesRegex(battery_float.CustodyFailure,
                                        r"d01/instrument_evidence\.json expected [0-9a-f]{64} observed [0-9a-f]{64}"):
                battery_float.validate_window(session)
            path.unlink()
            with self.assertRaisesRegex(battery_float.CustodyFailure,
                                        r"d01/instrument_evidence\.json expected [0-9a-f]{64} observed absent"):
                battery_float.validate_window(session)

    def test_d_a_phase_absent_from_the_evidence_is_evidence_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = self.build(tmp, {"d01": {"pre": (raw(), 0)}})
            result = battery_float.validate_window(session)
            self.assertEqual(result["status"], "battery_float_evidence_missing")
            self.assertIsNone(result["slots"][0]["post_raw_sha256"])

    def test_e_failed_probe_is_evidence_missing_until_its_recorded_empty_file_is_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = self.build(tmp, {"d01": {"pre": (raw(), 0), "post": (b"", 1)}})
            empty = Path(tmp) / "d01/raw/battery_float.post.ioreg"
            self.assertEqual(empty.read_bytes(), b"")
            self.assertEqual(battery_float.validate_window(session)["status"],
                             "battery_float_evidence_missing")
            empty.unlink()
            with self.assertRaisesRegex(battery_float.CustodyFailure, r"d01/post expected "):
                battery_float.validate_window(session)

    def test_f_stale_bytes_matching_their_digest_are_evidence_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = self.build(tmp, {"d01": self.clean()}, wall=UPDATE + 181)
            result = battery_float.validate_window(session)
            self.assertEqual(result["status"], "battery_float_evidence_missing")
            self.assertIsNone(result["slots"][0]["pre_update_age_s"])

    def test_g_custody_precedes_every_verdict_across_slots(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = self.build(tmp, {
                "d01": {"pre": (raw("charging-synthetic-from-real.ioreg"), 0), "post": (raw(), 0)},
                "d02": self.clean(),
            })
            self.assertEqual(battery_float.validate_window(session)["status"], "battery_float_confounded")
            (Path(tmp) / "d02/raw/battery_float.pre.ioreg").unlink()
            with self.assertRaisesRegex(battery_float.CustodyFailure, r"^custody failure: d02/pre expected "):
                battery_float.validate_window(session)

    def test_slot_carries_evidence_digest_and_update_ages(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = self.build(tmp, {"d01": self.clean()}, wall=UPDATE + 38)
            [slot] = battery_float.validate_window(session)["slots"]
            self.assertEqual(slot["instrument_evidence_sha256"],
                             session.finalized_slots["d01"].artifact_sha256["instrument_evidence.json"])
            self.assertEqual((slot["pre_update_age_s"], slot["post_update_age_s"]), (38, 38))


class CommittedVerdictTests(unittest.TestCase):
    """§4.10 item 1 (h): `load_committed_verdict` in a scratch Git repository."""

    PREREG = "d" * 64

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        init_git_fixture(self.repo, "-q")
        self.session = custody_session(Path(self.tmp.name) / "custody", {"d01": clean_phases()})
        self.record = battery_float.verdict_record(
            self.session, snapshot=SimpleNamespace(head_sequence=24, head_digest="e" * 64),
            preregistration_sha256=self.PREREG, tool_commit="f" * 40, module_sha256="a" * 64,
            wall_time_s=UPDATE + 60.0)
        self.rel = battery_float.verdict_relative_path("W1")
        self.path = self.repo / self.rel

    def git(self, *argv):
        subprocess.run(("git", "-C", str(self.repo), "-c", "user.email=t@example.invalid",
                        "-c", "user.name=t", *argv), check=True, capture_output=True)

    def write(self, record=None):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(battery_float.render_verdict(record or self.record))
        pin = self.repo / "configs/calibration/calibration_ledger_head.json"
        pin.parent.mkdir(parents=True, exist_ok=True)
        pin.write_text(json.dumps({"sequence": 24, "head_digest": "e" * 64,
                                   "ledger_schema": "joulewise.calibration_observation_ledger.v1"}) + "\n")

    def commit(self, message="c"):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def load(self, prereg=PREREG):
        return battery_float.load_committed_verdict(
            self.repo, "W1", session=self.session, preregistration_sha256=prereg)

    def assert_no_record(self, reason):
        with self.assertRaises(battery_float.NoRecord) as caught:
            self.load()
        self.assertIn(reason, caught.exception.reason)
        self.assertIsInstance(caught.exception, ValueError)

    def test_record_fields_are_the_ruled_schema(self):
        self.assertEqual(set(self.record), {
            "schema", "policy_id", "session_id", "session_kind", "session_state",
            "identity_epoch", "preregistration_sha256", "ledger_head", "computed_wall_time_s",
            "tool_commit", "battery_float_module_sha256", "status", "slots"})
        self.assertEqual(self.record["schema"], "joulewise.battery_float_verdict.v1")
        self.assertEqual(self.record["ledger_head"], {"sequence": 24, "head_digest": "e" * 64})
        self.assertEqual(set(self.record["slots"][0]), {
            "slot", "attempt_id", "verdict", "reasons", "pre_raw_sha256", "post_raw_sha256",
            "pre_update_age_s", "post_update_age_s", "delta_q_mah", "instrument_evidence_sha256"})

    def test_honest_add_authenticates(self):
        self.write()
        self.commit("harvest")
        record = self.load()
        self.assertEqual(dict(record), json.loads(self.path.read_text()))
        self.assertEqual(record.file_sha256, hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertRegex(record.commit, r"^[0-9a-f]{40}$")
        self.assertIsNone(battery_float.compare_verdict(record, battery_float.validate_window(self.session)))

    def test_verdict_added_separately_from_pin_is_no_record(self):
        self.write()
        self.git("add", "configs/calibration/calibration_ledger_head.json")
        self.git("commit", "-q", "-m", "pin first")
        self.git("add", self.rel)
        self.git("commit", "-q", "-m", "verdict later")
        self.assert_no_record("verdict not committed with its ledger head pin")

    def test_verdict_commit_with_wrong_pin_head_is_no_record(self):
        self.write()
        pin = self.repo / "configs/calibration/calibration_ledger_head.json"
        pin.write_text(json.dumps({"sequence": 23, "head_digest": "e" * 64,
                                   "ledger_schema": "joulewise.calibration_observation_ledger.v1"}) + "\n")
        self.commit("wrong pin")
        self.assert_no_record("verdict not committed with its ledger head pin")

    def test_delete_and_re_add_is_no_record(self):
        self.write()
        self.commit("harvest")
        self.git("rm", "-q", self.rel)
        self.commit("remove")
        self.write({**self.record, "status": "battery_float_evidence_missing"})
        self.commit("re-add")
        self.assert_no_record("path history is not a single adding commit (3 commits, 2 adding)")

    def test_modify_in_place_is_no_record(self):
        self.write()
        self.commit("harvest")
        self.write({**self.record, "status": "battery_float_evidence_missing"})
        self.commit("modify")
        self.assert_no_record("path history is not a single adding commit (2 commits, 1 adding)")

    def test_merge_branch_modify_then_restore_is_no_record(self):
        self.write()
        self.commit("harvest")
        original_branch = subprocess.check_output(
            ("git", "-C", str(self.repo), "symbolic-ref", "--short", "HEAD"), text=True).strip()
        self.git("checkout", "-q", "-b", "tamper")
        self.write({**self.record, "status": "battery_float_evidence_missing"})
        self.commit("modify")
        self.write()
        self.commit("restore")
        self.git("checkout", "-q", original_branch)
        self.git("merge", "--no-ff", "-q", "tamper")
        self.assert_no_record("path history is not a single adding commit")

    def test_uncommitted_edit_is_no_record(self):
        self.write()
        self.commit("harvest")
        self.write({**self.record, "status": "battery_float_evidence_missing"})
        self.assert_no_record("working tree differs from HEAD")

    def test_absent_and_uncommitted_are_no_record(self):
        (self.repo / "README").write_text("x")
        self.commit("genesis")
        self.assert_no_record("absent or uncommitted")
        self.write()
        self.assert_no_record("absent or uncommitted")

    def test_wrong_registration_digest_is_identity_mismatch(self):
        self.write()
        self.commit("harvest")
        with self.assertRaisesRegex(battery_float.NoRecord, "identity mismatch: preregistration_sha256"):
            self.load(prereg="0" * 64)

    def test_altered_evidence_digest_is_slot_binding_mismatch(self):
        altered = json.loads(json.dumps(self.record))
        altered["slots"][0]["instrument_evidence_sha256"] = "0" * 64
        self.write(altered)
        self.commit("harvest")
        self.assert_no_record("slot binding mismatch: d01")

    def test_compare_verdict_names_the_first_difference(self):
        recomputed = battery_float.validate_window(self.session)
        self.assertIsNone(battery_float.compare_verdict(self.record, recomputed))
        changed = json.loads(json.dumps(self.record))
        changed["slots"][0]["post_raw_sha256"] = None
        self.assertIn("d01.post_raw_sha256", battery_float.compare_verdict(changed, recomputed))
        changed = {**self.record, "status": "battery_float_confounded"}
        self.assertIn("status", battery_float.compare_verdict(changed, recomputed))
        changed = json.loads(json.dumps(self.record))
        changed["slots"][0]["reasons"] = ["ignored"]
        self.assertIsNone(battery_float.compare_verdict(changed, recomputed))


class AuthenticatedVerdictSeamTests(unittest.TestCase):
    """Consumer-drift final texts v1.1 §3.1-§3.2 and §3.12 (v), (vii): the one consumer entry."""

    PREREG = CommittedVerdictTests.PREREG
    setUp = CommittedVerdictTests.setUp
    git = CommittedVerdictTests.git
    write = CommittedVerdictTests.write
    commit = CommittedVerdictTests.commit

    def authenticate(self, prereg=PREREG):
        return battery_float.authenticate_committed_verdict(
            self.repo, session=self.session, preregistration_sha256=prereg)

    def refusal(self, prereg=PREREG):
        with self.assertRaises(battery_float.BatteryVerdictRefusal) as caught:
            self.authenticate(prereg)
        self.assertEqual(caught.exception.session_id, "W1")
        self.assertNotIsInstance(caught.exception, (ValueError, OSError))
        return caught.exception

    def test_v_a_missing_or_malformed_digest_refuses_before_any_io(self):
        self.write()
        self.commit("harvest")
        for prereg in (None, "", "d" * 63):
            with self.subTest(prereg=prereg), \
                    mock.patch.object(battery_float, "_git", side_effect=AssertionError("git read")) as git, \
                    mock.patch.object(battery_float, "validate_window",
                                      side_effect=AssertionError("custody read")) as replay:
                refusal = self.refusal(prereg)
                self.assertEqual(refusal.code, "registration_digest_required")
                self.assertEqual(str(refusal), "battery-float registration digest missing or invalid for W1")
                git.assert_not_called()
                replay.assert_not_called()

    def test_v_the_loader_never_returns_a_record_without_a_digest(self):
        self.write()
        self.commit("harvest")
        with self.assertRaisesRegex(battery_float.NoRecord, "identity mismatch: preregistration_sha256"):
            battery_float.load_committed_verdict(self.repo, "W1", session=self.session,
                                                 preregistration_sha256=None)

    def test_v_b_a_record_without_a_digest_never_loads_against_none(self):
        # Final delta (Astra R3): a committed record that omits the field must
        # not authenticate against an absent caller digest (None == None).
        record = dict(self.record)
        record.pop("preregistration_sha256", None)
        self.write(record)
        self.commit("harvest")
        with self.assertRaisesRegex(battery_float.NoRecord, "identity mismatch: preregistration_sha256"):
            battery_float.load_committed_verdict(self.repo, "W1", session=self.session,
                                                 preregistration_sha256=None)

    def test_vii_custody_failure_code_text_and_cause(self):
        self.write()
        self.commit("harvest")
        raw_path = Path(self.session.finalized_slots["d01"].custody_locator) / "raw/battery_float.post.ioreg"
        expected = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        raw_path.unlink()
        refusal = self.refusal()
        self.assertEqual(refusal.code, "custody_failure")
        self.assertEqual(refusal.detail, f"d01/post expected {expected} observed absent")
        self.assertEqual(str(refusal), f"battery-float custody failure for W1: d01/post expected {expected} "
                                       "observed absent; restore the custody bytes byte-exact from the "
                                       "harvest archive")
        self.assertIsInstance(refusal.__cause__, battery_float.CustodyFailure)

    def test_vii_record_unauthenticated_code_text_and_cause(self):
        (self.repo / "README").write_text("x")
        self.commit("genesis")
        refusal = self.refusal()
        self.assertEqual((refusal.code, refusal.detail), ("record_unauthenticated", "absent or uncommitted"))
        self.assertEqual(str(refusal), "battery-float harvest verdict missing or uncommitted for W1: "
                                       "absent or uncommitted")
        self.assertIsInstance(refusal.__cause__, battery_float.NoRecord)
        from joulewise import authentication_io
        self.write()
        self.commit("harvest")
        failure = authentication_io.V2AuthenticationInputError("grammar", "duplicate JSON key")
        with mock.patch.object(authentication_io, "ingest_git_authentication_input", side_effect=failure):
            refusal = self.refusal()
        self.assertEqual((refusal.code, refusal.detail), ("record_unauthenticated", "grammar: duplicate JSON key"))
        self.assertIs(refusal.__cause__, failure)

    def test_vii_verdict_mismatch_code_and_text(self):
        self.write({**self.record, "status": "battery_float_confounded"})
        self.commit("harvest")
        refusal = self.refusal()
        self.assertEqual((refusal.code, refusal.detail),
                         ("verdict_mismatch", "status recorded battery_float_confounded recomputed pass"))
        self.assertEqual(str(refusal), "battery-float harvest verdict for W1 cannot be re-established from raw "
                                       "bytes (status recorded battery_float_confounded recomputed pass); "
                                       "custody failure")

    def test_vii_the_refusal_class_has_exactly_four_codes(self):
        self.assertEqual(set(battery_float.REFUSAL_TEXT), {
            "registration_digest_required", "custody_failure", "record_unauthenticated", "verdict_mismatch"})

    def test_vii_the_result_is_frozen_and_built_from_the_record(self):
        record = json.loads(json.dumps(self.record))
        # Fields `compare_verdict` does not compare: the result must carry the record's.
        record["slots"][0]["reasons"] = ["from the record"]
        record["slots"][0]["pre_update_age_s"] = 12.5
        self.write(record)
        self.commit("harvest")
        verdict = self.authenticate()
        self.assertIsInstance(verdict, battery_float.AuthenticatedVerdict)
        self.assertEqual((verdict.session_id, verdict.preregistration_sha256, verdict.status),
                         ("W1", self.PREREG, "pass"))
        [slot] = verdict.slots
        self.assertIsInstance(slot, battery_float.AuthenticatedSlot)
        self.assertEqual((slot.slot, slot.reasons, slot.pre_update_age_s), ("d01", ("from the record",), 12.5))
        self.assertEqual(verdict.file_sha256, hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertRegex(verdict.commit, r"^[0-9a-f]{40}$")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            verdict.status = "battery_float_confounded"
        with self.assertRaises(dataclasses.FrozenInstanceError):
            slot.verdict = "battery_float_confounded"
        self.assertNotIsInstance(verdict, dict)

    def test_vii_status_is_the_record_s_not_the_recomputation(self):
        record = json.loads(json.dumps(self.record))
        record["status"] = "battery_float_confounded"
        record["slots"][0]["verdict"] = "battery_float_confounded"
        self.write(record)
        self.commit("harvest")
        with mock.patch.object(battery_float, "compare_verdict", return_value=None):
            verdict = self.authenticate()
        self.assertEqual(verdict.status, "battery_float_confounded")
        self.assertEqual(verdict.slots[0].verdict, "battery_float_confounded")


# ex-03's own UpdateTime; the gate fixture's clock is 1005 s, so the gate site
# re-stamps the corpus to 1000.
REAL_UPDATE = 1790394405
GATE_UPDATE = 1000


class GrammarCorpusTests(unittest.TestCase):
    """Ruling BFG-D-PARSER-ESC-01 §4 corpus at the four sites (R2-1, R2-8)."""

    evaluate = GateTests.evaluate
    make_session = WindowTests.make_session

    def test_real_capture_fixture_is_ex03(self):
        raw = (FIXTURES / corpus.REAL).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), corpus.REAL_SHA256)
        self.assertEqual((len(raw), raw.count(b"\n"), raw.count(b"\r")), (17337, 64, 0))
        self.assertEqual(len(battery_float._structure(raw)), 59)

    def test_positives_are_accepted_by_the_grammar(self):
        for name, raw in corpus.positives(REAL_UPDATE).items():
            with self.subTest(name=name):
                battery_float._recorded_values(battery_float._structure(raw))
                if name == "stale_fixture":
                    with self.assertRaisesRegex(battery_float.ProbeError, "UpdateTime stale"):
                        battery_float.parse(raw, REAL_UPDATE + 1)
                    continue
                parsed = battery_float.parse(raw, REAL_UPDATE + 1)
                self.assertEqual(parsed["passed"], name != "charging_fixture")
        minus = battery_float.parse(corpus.positives(REAL_UPDATE)["signed_minus_158"], REAL_UPDATE + 1)
        self.assertEqual(minus["instant_amperage_ma"], -158)
        shadow = battery_float.parse(corpus.positives(REAL_UPDATE)["nested_shadow_names"], REAL_UPDATE + 1)
        self.assertEqual((shadow["external_connected_raw"], shadow["is_charging_raw"],
                          shadow["instant_amperage_raw"]), ("Yes", "No", "0"))

    def test_real_capture_records_every_registered_property(self):
        parsed = battery_float.parse(corpus.positives(REAL_UPDATE)["real_capture_ex03"], REAL_UPDATE + 38)
        self.assertEqual(len(parsed["property_lines"]), 11)
        self.assertEqual((parsed["amperage_ma"], parsed["voltage_mv"], parsed["temperature_raw"],
                          parsed["fully_charged"], parsed["current_capacity_pct"],
                          parsed["apple_raw_current_capacity_mah"], parsed["apple_raw_max_capacity_mah"],
                          parsed["update_age_s"]), (0, 12899, 3034, True, 100, 7585, 7585, 38))

    def test_red_set_is_a_subset_of_the_corpus(self):
        # Executed at faf0ea01 (seat report 19): these returned passed=True there.
        self.assertLessEqual(corpus.RED, set(corpus.negatives(REAL_UPDATE)))
        self.assertEqual(len(corpus.RED), 68)

    def test_negatives_refused_by_parse_and_observe(self):
        for name, raw in corpus.negatives(REAL_UPDATE).items():
            with self.subTest(name=name):
                with self.assertRaises(battery_float.ProbeError):
                    battery_float.parse(raw, REAL_UPDATE + 1)
                observed, stdout = battery_float.observe(
                    phase="t0", wall_time_s=REAL_UPDATE + 1,
                    runner=lambda argv, raw=raw: subprocess.CompletedProcess(argv, 0, raw, b""))
                self.assertEqual((observed["probe_error"], observed["passed"]), (True, False))
                self.assertEqual(stdout, raw)
                self.assertEqual(observed["raw_stdout_sha256"], hashlib.sha256(raw).hexdigest())

    def test_negatives_are_night_probe_error_at_both_gate_entries(self):
        control = corpus.positives(GATE_UPDATE)["real_capture_ex03"]
        for dynamic in (False, True):
            source = FakeProbeSource()
            source.results[night_gate.IOREG_BATTERY_ARGV] = result(night_gate.IOREG_BATTERY_ARGV, stdout=control)
            receipt = self.evaluate(source, dynamic=dynamic)
            self.assertIsNone(receipt.refusal)
        for name, raw in corpus.negatives(GATE_UPDATE).items():
            for dynamic in (False, True):
                with self.subTest(name=name, dynamic=dynamic):
                    source = FakeProbeSource()
                    source.results[night_gate.IOREG_BATTERY_ARGV] = result(
                        night_gate.IOREG_BATTERY_ARGV, stdout=raw)
                    receipt = self.evaluate(source, dynamic=dynamic)
                    self.assertIsNotNone(receipt.refusal)
                    self.assertEqual(receipt.refusal.reason, "night_probe_error")

    def test_negatives_are_evidence_missing_in_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = corpus.positives(REAL_UPDATE)["real_capture_ex03"]
            session, _ = self.make_session(tmp, control, control, wall=REAL_UPDATE + 1)
            self.assertEqual(battery_float.validate_window(session)["status"], "pass")
        for name, raw in corpus.negatives(REAL_UPDATE).items():
            for bad in ("pre", "post"):
                with self.subTest(name=name, phase=bad), tempfile.TemporaryDirectory() as tmp:
                    pre, post = (raw, control) if bad == "pre" else (control, raw)
                    session, _ = self.make_session(tmp, pre, post, wall=REAL_UPDATE + 1)
                    self.assertEqual(battery_float.validate_window(session)["status"],
                                     "battery_float_evidence_missing")


def _structural_raise_sites(tree: ast.Module) -> list[ast.Raise]:
    [stage] = [node for node in tree.body
               if isinstance(node, ast.FunctionDef) and node.name == "_structure"]
    return [node for node in ast.walk(stage) if isinstance(node, ast.Raise)
            and isinstance(node.exc, ast.Call) and getattr(node.exc.func, "id", None) == "ProbeError"]


class _Relax(ast.NodeTransformer):
    """Replace one refusal with one relaxation of it.

    ``pass`` deletes the refusal.  In the line loop, ``continue`` skips the
    offending line (the faf0ea01 failure shape).  In a cursor helper
    (``value``/``string``/``container``), ``return len(text)`` consumes the
    rest of the value.
    """

    def __init__(self, target: ast.Raise, relaxation: str) -> None:
        self.target = target
        self.relaxation = relaxation

    def visit_Raise(self, node):
        if node is not self.target:
            return node
        replacement = {
            "pass": ast.Pass(),
            "continue": ast.Continue(),
            "consume": ast.Return(ast.Call(ast.Name("len", ast.Load()), [ast.Name("text", ast.Load())], [])),
        }[self.relaxation]
        return ast.copy_location(replacement, node)


def _relaxations(tree: ast.Module) -> list[tuple[ast.Raise, tuple[str, ...]]]:
    """Each structural refusal with the relaxations that fit where it sits."""
    [stage] = [node for node in tree.body
               if isinstance(node, ast.FunctionDef) and node.name == "_structure"]
    helpers = {id(raise_) for helper in stage.body if isinstance(helper, ast.FunctionDef)
               for raise_ in ast.walk(helper)}
    in_loop = {id(raise_) for loop in stage.body if isinstance(loop, ast.For)
               for raise_ in ast.walk(loop)}
    return [(site, ("pass", "consume") if id(site) in helpers else
             ("pass", "continue") if id(site) in in_loop else ("pass",))
            for site in _structural_raise_sites(tree)]


def _relaxed_module(index: int, relaxation: str) -> ModuleType:
    source = Path(battery_float.__file__).read_text()
    tree = ast.parse(source)
    site, _ = _relaxations(tree)[index]
    tree = ast.fix_missing_locations(_Relax(site, relaxation).visit(tree))
    module = ModuleType(f"battery_float_relaxed_{index}_{relaxation}")
    module.__file__ = battery_float.__file__
    # Registered while it executes: the module's dataclasses resolve their
    # postponed annotations through ``sys.modules``.
    sys.modules[module.__name__] = module
    try:
        exec(compile(tree, battery_float.__file__, "exec"), module.__dict__)
    finally:
        del sys.modules[module.__name__]
    return module


def _accepted(module: ModuleType, raw: bytes) -> bool:
    try:
        module.parse(raw, REAL_UPDATE + 1)
    except Exception:
        return False
    return True


class GrammarMutationTests(unittest.TestCase):
    """Ruling §4 test list (refuter N-1): every structural refusal is load-bearing.

    For each ``raise ProbeError`` in ``_structure``, enumerated by AST, some
    relaxation of that one refusal must let at least one corpus negative be
    accepted, so a future "helpful" relaxation cannot pass unnoticed.
    """

    def test_every_structural_refusal_site_is_caught_by_the_corpus(self):
        sites = _relaxations(ast.parse(Path(battery_float.__file__).read_text()))
        # Enumerated by AST, not by a hand count: the ruling's classes as coded.
        self.assertEqual(len(sites), 20)
        negatives = corpus.negatives(REAL_UPDATE)
        for index, (site, relaxations) in enumerate(sites):
            with self.subTest(line=site.lineno, refusal=ast.unparse(site.exc)):
                caught = [(relaxation, name) for relaxation in relaxations
                          for name, raw in negatives.items()
                          if _accepted(_relaxed_module(index, relaxation), raw)]
                self.assertTrue(caught)


# Obligation R2-9 (refuter M-2).  The battery grammar is frozen for the
# Revision-5 epoch: every harvest consumer re-parses the committed raw bytes
# with the current module and demands zero `compare_verdict` differences, and
# a verdict path is added exactly once, so a grammar change after a verdict is
# committed can strand that window or flip a gate outcome after the fact.  A
# change to `_structure` or `_recorded_values` must, in the same PR, replay
# every committed Revision-5 verdict with zero differences and update this
# pin; otherwise it is a registration amendment needing an owner ruling.
STRUCTURAL_STAGE_SHA256 = "1a9c32970aec07423f1c05930c689cfa248b428214bde066167f13b52c395d4f"


def structural_stage_sha256(module: ModuleType) -> str:
    text = "".join(inspect.getsource(getattr(module, name)) for name in ("_structure", "_recorded_values"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class GrammarFreezeTests(unittest.TestCase):
    def test_structural_stage_is_pinned(self):
        self.assertEqual(structural_stage_sha256(battery_float), STRUCTURAL_STAGE_SHA256)

    def test_mutating_the_structural_stage_fails_the_pin(self):
        source = Path(battery_float.__file__).read_text()
        mutations = (
            ("max_bytes, max_line, max_depth = 1_048_576, 262_144, 64",
             "max_bytes, max_line, max_depth = 1_048_576, 262_144, 65"),
            ('atom = re.compile(rb"Yes|No|[0-9]+")', 'atom = re.compile(rb"Yes|No|-?[0-9]+")'),
            ('        if name in values and values[name] not in ("Yes", "No"):',
             '        if name in values and values[name] not in ("Yes", "No", "yes"):'),
        )
        for old, new in mutations:
            with self.subTest(mutation=new), tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(source.count(old), 1)
                path = Path(tmp) / "battery_float_mutant.py"
                path.write_text(source.replace(old, new))
                spec = importlib.util.spec_from_file_location("battery_float_mutant", path)
                mutant = importlib.util.module_from_spec(spec)
                # Registered while it executes: the module's dataclasses resolve
                # their postponed annotations through ``sys.modules``.
                sys.modules[spec.name] = mutant
                try:
                    spec.loader.exec_module(mutant)
                finally:
                    del sys.modules[spec.name]
                self.assertNotEqual(structural_stage_sha256(mutant), STRUCTURAL_STAGE_SHA256)


class BytesFeederTests(unittest.TestCase):
    """Obligation R2-11 (refuter M-4) at the shared entry point."""

    def test_observe_refuses_text_stdout_and_never_re_encodes(self):
        text = corpus.positives(REAL_UPDATE)["real_capture_ex03"].decode("ascii")
        observed, stdout = battery_float.observe(
            phase="arm_check", wall_time_s=REAL_UPDATE + 1,
            runner=lambda argv: subprocess.CompletedProcess(argv, 0, text, ""))
        self.assertEqual((observed["probe_error"], observed["passed"]), (True, False))
        self.assertEqual(observed["reasons"], ["ProbeError: probe stdout is not bytes"])
        self.assertEqual(stdout, b"")
        with self.assertRaises(battery_float.ProbeError):
            battery_float.parse(text, REAL_UPDATE + 1)

    def test_default_runner_captures_bytes_without_text_mode(self):
        smuggle = corpus.negatives(REAL_UPDATE)["cr_smuggled_required"]
        from tests import battery_float_fixture
        seen = []
        original = subprocess.run
        def run(argv, *args, **kwargs):
            seen.append(kwargs)
            return battery_float_fixture.smuggling_run(original, smuggle)(argv, *args, **kwargs)
        with mock.patch.object(battery_float.subprocess, "run", side_effect=run):
            observed, stdout = battery_float.observe(phase="slot_pre", wall_time_s=REAL_UPDATE + 1)
        self.assertNotIn("text", seen[0])
        self.assertEqual(stdout, smuggle)
        self.assertEqual(observed["raw_stdout_sha256"], hashlib.sha256(smuggle).hexdigest())
        self.assertTrue(observed["probe_error"])
