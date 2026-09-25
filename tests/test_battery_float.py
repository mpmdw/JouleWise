"""Battery float parser and production-gate regressions from one real ioreg read."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import battery_float, night_gate
from tests.test_night_gate import FakeProbeSource, REGISTRATION_TEXT, make_plan, result

FIXTURES = Path(__file__).parent / "fixtures/battery_float"
UPDATE = 1790373525


def raw(name="float.ioreg"):
    return (FIXTURES / name).read_bytes()


def edit(source: bytes, old: bytes, new: bytes) -> bytes:
    assert source.count(old) == 1
    return source.replace(old, new)


class ParserTests(unittest.TestCase):
    def test_real_and_charging_fixtures(self):
        self.assertTrue(battery_float.parse(raw(), UPDATE + 179)["passed"])
        self.assertFalse(battery_float.parse(raw("charging-synthetic-from-real.ioreg"), UPDATE + 1)["passed"])

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


class GateTests(unittest.TestCase):
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
                        b'"UpdateTime" = 1790373525', b'"UpdateTime" = 1000').decode()
        for dynamic in (False, True):
            source = FakeProbeSource()
            source.results[night_gate.IOREG_BATTERY_ARGV] = result(
                night_gate.IOREG_BATTERY_ARGV, stdout=charging)
            receipt = self.evaluate(source, dynamic=dynamic)
            self.assertEqual(receipt.verdict, "REFUSED")
            self.assertEqual(receipt.refusal.reason, "night_refused_battery_float")
            battery = receipt.conditions[2].measured["battery_float"]
            self.assertEqual(battery["raw_stdout"], charging)
            self.assertFalse(battery["passed"])

    def test_stale_is_probe_error_and_fresh_passes(self):
        for age, expected in ((181, "night_probe_error"), (179, None)):
            source = FakeProbeSource()
            fresh = edit(raw(), b'"UpdateTime" = 1790373525',
                         f'"UpdateTime" = {1005 - age}'.encode())
            source.results[night_gate.IOREG_BATTERY_ARGV] = result(
                night_gate.IOREG_BATTERY_ARGV, stdout=fresh.decode())
            receipt = self.evaluate(source)
            self.assertEqual(receipt.refusal.reason if receipt.refusal else None, expected)


class WindowTests(unittest.TestCase):
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
            self.assertEqual(battery_float.validate_window(session)["status"], "battery_float_evidence_missing")

    def test_confounded_takes_precedence_over_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            session, _ = self.make_session(tmp, raw("charging-synthetic-from-real.ioreg"), None)
            self.assertEqual(battery_float.validate_window(session)["status"], "battery_float_confounded")

    def test_stale_at_harvest(self):
        with tempfile.TemporaryDirectory() as tmp:
            session, _ = self.make_session(tmp, raw(), raw(), wall=UPDATE + 181)
            self.assertEqual(battery_float.validate_window(session)["status"], "battery_float_evidence_missing")
