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
        self.git("init", "-q")
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
