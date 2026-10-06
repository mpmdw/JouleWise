"""HAZARD_PACK flag path through the bracket reservation (gate-prune core lane VPF).

DESIGN.md (core prune) rows A6-R1, A6-R2/R3 at the reservation, and the PLAN2
erratum s3-reservation-stop (section 2.1 row 4, section 2.3):

- A6-R1: on HAZARD the reservation records the identity vectors it measures
  with the writer's own functions, not the desk-prepared JSON, and flags the
  difference; the writer's kept R1 comparison then compares two measurements.
- A6-R2/R3 + erratum: on HAZARD the reservation skips the committed-pin check
  and the historical custody pass (an evicted or unreadable old capture no
  longer stops the chain at stage 1), and a head pin that the physical chain
  contains but that lags it (the desk pin advance did not run between two
  windows) is recorded instead of refused; the session is appended to the
  physical tail, and the writer judges the slot from the reservation.
- Keepers on HAZARD: rollback, a divergent pin, a malformed ledger and an
  already-open session still refuse.

Legacy (no hazard locator) twins pin today's refusals.  This module imports no
flag code, so it also runs against the base commit, where each HAZARD
assertion fails.
"""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest import mock

from joulewise import calibration_ledger as ledger
from joulewise.calibration_exits import RefusalCode
from scripts import reserve_calibration_window_bracket as reserve
from scripts import validate_powermetrics_fiducial as writer
from tests import test_calibration_exits as exits
from tests import test_validate_powermetrics_fiducial_hazard as vpf_hazard
from tests.calibration_exits_fixtures.custody_hang import BlockedArtifact, CustodyFixture

HAZARD_LOCATOR_SCHEMA = "joulewise.hazard_window_lineage_locator.v1"
LOCATOR_BASENAME = ".joulewise-launch-lineage.json"
WINDOW_PLAN_ID = "hazard-window-plan"
WINDOW_ATTEMPT = 3


def tearDownModule() -> None:
    exits.assert_no_owned_fake_sampler_survivors()


def make_hazard(runs_root: Path, custody: Path) -> None:
    """Turn ``runs_root`` into a HAZARD root whose flags go to ``custody``."""

    custody.mkdir(parents=True, exist_ok=True)
    (custody / "night_plan.json").write_text(json.dumps({
        "plan_id": WINDOW_PLAN_ID, "hazard_window": {"attempt": WINDOW_ATTEMPT},
    }) + "\n", encoding="utf-8")
    runs_root.mkdir(parents=True, exist_ok=True)
    (runs_root / LOCATOR_BASENAME).write_text(json.dumps({
        "schema_version": HAZARD_LOCATOR_SCHEMA,
        "launch_lineage": {"window_context": {"custody_root": str(custody)}},
    }) + "\n", encoding="utf-8")


def flags(custody: Path, writer_name: str = "core-reservation") -> list[dict]:
    path = custody / "flags" / f"{writer_name}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def kinds(custody: Path, writer_name: str = "core-reservation") -> dict[str, dict]:
    return {flag["observed"].get("kind"): flag for flag in flags(custody, writer_name)
            if isinstance(flag.get("observed"), dict)}


def refusal_code(completed) -> str:
    lines = [line for line in completed.stderr.splitlines() if line.startswith("{")]
    codes = [json.loads(line).get("code") for line in lines]
    codes = [code for code in codes if code]
    return codes[-1] if codes else ""


def open_receipt(ledger_path: Path, session_id: str) -> dict:
    rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
    return next(row for row in rows if row.get("event") == ledger.BRACKET_SESSION_OPEN_EVENT
                and row.get("session_id") == session_id)


def make_pin_stale(fixture: CustodyFixture, *, session_id: str = "session-previous-window") -> dict:
    """A previous window's session opened and aborted past the committed pin.

    This is the back-to-back state the erratum names: the desk pin advance did
    not run, so the physical ledger is ahead of a committed pin it contains.
    """

    pin_before = json.loads(fixture.pin.read_text(encoding="utf-8"))
    fixture.witness._open_session(session_id)
    ledger.abort_bracket_session(fixture.ledger, session_id=session_id, reason="previous window")
    snapshot = ledger.load_calibration_ledger_snapshot(
        fixture.ledger, fixture.pin, require_committed_pin=False, verify_custody=False,
        repo_root=fixture.repo)
    assert ledger._pin_relation(snapshot) is ledger.PinRelation.PHYSICAL_AHEAD
    assert set(snapshot.refusal_reasons) == {"calibration_ledger_head_mismatch"}
    return {"pin": pin_before, "physical_sequence": snapshot.head_sequence}


class _ReservationCase(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = CustodyFixture().__enter__()
        self.addCleanup(self.fixture.__exit__, None, None, None)
        self.runs_root = self.fixture.repo / "runs" / self.fixture.state["session_id"]
        self.custody = self.fixture.repo / "custody-reservation"

    def hazard(self) -> None:
        make_hazard(self.runs_root, self.custody)

    def reserve(self, *, extra=(), budget: float = 3.0):
        completed, _elapsed = self.fixture.reservation(budget=budget, extra=extra)
        return completed

    def assert_reserved(self, completed) -> dict:
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        output = json.loads(completed.stdout)
        self.assertEqual(output["status"], "reserved")
        return output


class HistoricalCustodyAtReservationTests(_ReservationCase):
    """A6-R2/R3 at the reservation, erratum s3-reservation-stop."""

    def test_evicted_historical_capture_refuses_legacy_and_reserves_on_hazard(self) -> None:
        # An old capture file gone from disk (evicted to iCloud and not
        # rehydrated, or deleted).
        (self.fixture.custodies[0] / "events.jsonl").unlink()
        legacy = self.reserve()
        self.assertNotEqual(legacy.returncode, 0)
        self.assertEqual(refusal_code(legacy), RefusalCode.LEDGER_CUSTODY_INVALID.value)
        self.assertEqual(flags(self.custody), [])

        self.hazard()
        self.assert_reserved(self.reserve())
        flag = kinds(self.custody)["historical_custody_unverified"]
        self.assertEqual(flag["code"], "calibration.writer_record_flagged")
        self.assertEqual(flag["scope"]["level"], "window")
        self.assertEqual(flag["scope"]["plan_id"], WINDOW_PLAN_ID)
        self.assertEqual(flag["scope"]["attempt"], WINDOW_ATTEMPT)
        self.assertEqual(flag["observed"]["writer"], "reservation")
        self.assertEqual(flag["blinding"], "STRUCTURE")

    def test_unreadable_historical_capture_times_out_legacy_and_is_never_read_on_hazard(self) -> None:
        # An old capture whose read never completes (an iCloud download that
        # stalls): today the 120 s budget expires and the chain stops at exit 10.
        artifact = self.fixture.custodies[0] / "events.jsonl"
        with BlockedArtifact(artifact) as fifo:
            legacy = self.reserve()
            self.assertEqual(refusal_code(legacy), RefusalCode.LEDGER_CUSTODY_TIMEOUT.value)
            self.assertTrue(fifo.entered.is_set())
        with BlockedArtifact(artifact) as fifo:
            self.hazard()
            self.assert_reserved(self.reserve())
            self.assertFalse(fifo.entered.is_set())
        self.assertIn("historical_custody_unverified", kinds(self.custody))

    def test_uncommitted_pin_refuses_legacy_and_reserves_on_hazard(self) -> None:
        pin = json.loads(self.fixture.pin.read_text(encoding="utf-8"))
        self.fixture.pin.write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")
        legacy = self.reserve()
        self.assertEqual(refusal_code(legacy), RefusalCode.LEDGER_HEAD_UNCOMMITTED.value)
        self.hazard()
        self.assert_reserved(self.reserve())


class StalePinAtReservationTests(_ReservationCase):
    """Erratum: ``append_bracket_session_receipt``'s own pin equality is a record on HAZARD."""

    def test_stale_pin_refuses_legacy_and_appends_to_the_physical_tail_on_hazard(self) -> None:
        stale = make_pin_stale(self.fixture)
        legacy = self.reserve()
        self.assertEqual(refusal_code(legacy), RefusalCode.RESERVATION_HEAD_MISMATCH.value)

        self.hazard()
        self.assert_reserved(self.reserve())
        receipt = open_receipt(self.fixture.ledger, self.fixture.state["session_id"])
        # Appended after the previous window's rows (its own append intent, a
        # control row, comes first), never at the pin.
        self.assertGreater(receipt["sequence"], stale["physical_sequence"])
        flag = kinds(self.custody)["head_pin_stale"]
        self.assertEqual(flag["code"], "calibration.writer_record_flagged")
        self.assertEqual(flag["observed"]["relation"], "physical_ahead")
        self.assertEqual(flag["observed"]["pin_sequence"], stale["pin"]["sequence"])
        self.assertEqual(flag["observed"]["physical_sequence"], stale["physical_sequence"])
        self.assertEqual(flag["source"]["legacy_code"],
                         RefusalCode.RESERVATION_HEAD_MISMATCH.value)
        # The pin file is never rewritten by the reservation.
        self.assertEqual(json.loads(self.fixture.pin.read_text(encoding="utf-8")), stale["pin"])

    def test_exact_pin_on_hazard_writes_no_stale_flag(self) -> None:
        self.hazard()
        self.assert_reserved(self.reserve())
        self.assertNotIn("head_pin_stale", kinds(self.custody))

    def test_rollback_still_refuses_on_hazard(self) -> None:
        # Keeper: a pin AHEAD of the physical ledger is rollback.
        pin = json.loads(self.fixture.pin.read_text(encoding="utf-8"))
        self.fixture.pin.write_text(json.dumps(dict(pin, sequence=pin["sequence"] + 5)) + "\n",
                                    encoding="utf-8")
        self.hazard()
        completed = self.reserve()
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(refusal_code(completed), RefusalCode.LEDGER_ROLLBACK.value)

    def test_divergent_pin_still_refuses_on_hazard(self) -> None:
        # Keeper: a pin the physical chain does not contain (same sequence,
        # another digest) is a divergent chain, never a stale pin.
        make_pin_stale(self.fixture)
        pin = json.loads(self.fixture.pin.read_text(encoding="utf-8"))
        self.fixture.pin.write_text(json.dumps(dict(pin, head_digest="b" * 64)) + "\n",
                                    encoding="utf-8")
        self.hazard()
        completed = self.reserve()
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(refusal_code(completed), RefusalCode.RESERVATION_HEAD_MISMATCH.value)
        self.assertNotIn("head_pin_stale", kinds(self.custody))

    def test_malformed_ledger_still_refuses_on_hazard(self) -> None:
        with self.fixture.ledger.open("ab") as handle:
            handle.write(b'{"torn": \n')
        self.hazard()
        completed = self.reserve()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(refusal_code(completed), {RefusalCode.LEDGER_MALFORMED.value,
                                                RefusalCode.LEDGER_RECOVERY_REQUIRED.value})

    def test_open_session_still_refuses_on_hazard(self) -> None:
        # Keeper: exactly one open session per window.
        self.fixture.witness._open_session("session-still-open")
        self.hazard()
        completed = self.reserve()
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(refusal_code(completed), RefusalCode.PRE_RESERVE_NOT_READY.value)


class StalePinAppendTests(unittest.TestCase):
    """The ledger function itself: only a pin the physical chain contains is accepted."""

    def setUp(self) -> None:
        self.fixture = CustodyFixture().__enter__()
        self.addCleanup(self.fixture.__exit__, None, None, None)

    def append(self, session_id: str, **kwargs):
        w = self.fixture.witness
        runs_root = self.fixture.repo / "runs" / session_id
        return ledger.append_bracket_session_receipt(
            self.fixture.ledger, session_id=session_id, window_id=f"window-{session_id}",
            plan_id=f"plan-{session_id}", plan_sha256="c" * 64,
            evidence_root_id=f"evidence-{session_id}", runs_root=runs_root,
            slots={slot: {"attempt_id": f"{session_id}-{slot}",
                          "custody_locator": str(runs_root / "instrument_validation"
                                                 / f"{session_id}-{slot}"),
                          "identity_epoch": w.epoch, "t1_bindings": w.t1}
                   for slot in ("pre", "post")},
            head_pin_path=self.fixture.pin, require_committed_pin=False,
            repo_root=self.fixture.repo, **kwargs)

    def test_divergent_pin_refuses_even_with_a_relation_record(self) -> None:
        make_pin_stale(self.fixture)
        pin = json.loads(self.fixture.pin.read_text(encoding="utf-8"))
        self.fixture.pin.write_text(json.dumps(dict(pin, head_digest="d" * 64)) + "\n",
                                    encoding="utf-8")
        record: dict = {}
        with self.assertRaises(ledger.CalibrationLedgerError) as caught:
            self.append("session-divergent", pin_relation_record=record)
        self.assertEqual(caught.exception.code, RefusalCode.RESERVATION_HEAD_MISMATCH)
        self.assertEqual(record, {})

    def test_past_stale_pin_shape_keeps_its_integrity_terms(self) -> None:
        import dataclasses

        make_pin_stale(self.fixture)
        record: dict = {}
        self.append("session-window", pin_relation_record=record)
        self.assertEqual(record["relation"], "physical_ahead")
        snapshot = ledger.load_calibration_ledger_snapshot(
            self.fixture.ledger, self.fixture.pin, require_committed_pin=False,
            verify_custody=False, repo_root=self.fixture.repo)
        self.assertFalse(snapshot.is_governed_open_bracket_extension)
        self.assertTrue(snapshot.is_open_bracket_extension_past_stale_pin)
        # Any other ledger reason (malformed, broken chain, rollback, custody)
        # still fails the shape.
        for reason in ("calibration_ledger_malformed", "calibration_ledger_rollback"):
            with self.subTest(reason):
                tainted = dataclasses.replace(
                    snapshot, refusal_reasons=tuple(snapshot.refusal_reasons) + (reason,))
                self.assertFalse(tainted.is_open_bracket_extension_past_stale_pin)
        # A pin the chain does not contain fails it.
        divergent = dataclasses.replace(snapshot, committed_head_digest="e" * 64)
        self.assertFalse(divergent.is_open_bracket_extension_past_stale_pin)
        # A second open session fails it.
        open_session = next(item for item in snapshot.bracket_sessions if item.state == "open")
        two_open = dataclasses.replace(snapshot, bracket_sessions=tuple(snapshot.bracket_sessions) + (
            dataclasses.replace(open_session, session_id="session-second-open"),))
        self.assertFalse(two_open.is_open_bracket_extension_past_stale_pin)

    def test_stale_pin_without_a_relation_record_refuses_as_before(self) -> None:
        make_pin_stale(self.fixture)
        with self.assertRaises(ledger.CalibrationLedgerError) as caught:
            self.append("session-legacy")
        self.assertEqual(caught.exception.code, RefusalCode.RESERVATION_HEAD_MISMATCH)


class StalePinAtWriterTests(unittest.TestCase):
    """The writer judges a session reserved past a stale pin from the reservation."""

    def test_stale_pin_refuses_legacy_writer_and_captures_on_hazard(self) -> None:
        with CustodyFixture() as fixture:
            stale = make_pin_stale(fixture)
            # Reserve the window's session at the physical tail, as the HAZARD
            # reservation does, while the committed pin stays stale.
            pin_raw = fixture.pin.read_bytes()
            snapshot = ledger.load_calibration_ledger_snapshot(
                fixture.ledger, fixture.pin, require_committed_pin=False, verify_custody=False,
                repo_root=fixture.repo)
            fixture.pin.write_text(json.dumps({
                "sequence": snapshot.head_sequence, "head_digest": snapshot.head_digest,
                "ledger_schema": ledger.LEDGER_SCHEMA}) + "\n", encoding="utf-8")
            rig = vpf_hazard.HazardWriterRig(fixture.witness)
            state = rig.real_writer_state("session-stale-writer")
            fixture.pin.write_bytes(pin_raw)
            self.assertEqual(json.loads(pin_raw)["sequence"], stale["pin"]["sequence"])

            legacy = rig.run_writer(state)
            self.assertEqual(legacy.returncode, 2, legacy.stdout + legacy.stderr)
            self.assertEqual(refusal_code(legacy), RefusalCode.RESERVED_SLOT_MISMATCH.value)

            rig.hazard(state)
            completed = rig.run_writer(state)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["status"], "valid")
            flag = next(flag for flag in rig.flags(state)
                        if flag["observed"].get("kind") == "head_pin_stale")
            self.assertEqual(flag["observed"]["pin_sequence"], stale["pin"]["sequence"])
            self.assertEqual(flag["observed"]["writer"], "fiducial")


class _FakeMlx:
    def __enter__(self):
        core = types.ModuleType("mlx.core")
        core.__version__ = "test-mlx-1"
        package = types.ModuleType("mlx")
        package.core = core
        self._patch = mock.patch.dict(sys.modules, {"mlx": package, "mlx.core": core})
        self._patch.__enter__()
        return self

    def __exit__(self, *exc):
        return self._patch.__exit__(*exc)


class DeskIdentityTests(unittest.TestCase):
    """A6-R1: the reservation records measured identity vectors on HAZARD."""

    LIVE = {"kern.osversion": "25G83", "hw.model": "Mac15,9"}

    def setUp(self) -> None:
        self.w = exits.PublicGovernedExitWitnessTests(methodName="runTest")
        self.w.setUp()
        self.addCleanup(self.w.doCleanups)
        self.addCleanup(self.w.tearDown)
        epoch, t1 = self.w._actual_writer_bindings()
        self.measured_epoch = epoch
        self.session_id = "session-r1"
        self.runs_root = self.w.repo / "runs" / self.session_id
        self.custody = self.w.repo / "custody-r1"
        inputs = self.w.repo / "desk"
        inputs.mkdir()
        self.desk_epoch = inputs / "epoch.json"
        self.desk_epoch.write_text(json.dumps(dict(epoch, os_build="00X000")) + "\n")
        self.desk_t1 = inputs / "t1.json"
        self.desk_t1.write_text(json.dumps(dict(t1, os_build="00X000")) + "\n")
        self.plan = inputs / "plan.json"
        self.plan.write_text(json.dumps({"plan_id": f"plan-{self.session_id}"}) + "\n")
        self.sysctl_calls: list[str] = []

    def _sysctl(self, name: str) -> str:
        self.sysctl_calls.append(name)
        return self.LIVE[name]

    def main(self, *extra: str) -> tuple[int, str, str]:
        import hashlib

        s = self.session_id
        argv = [
            "--ledger", str(self.w.ledger), "--head-pin", str(self.w.pin),
            "--session-id", s, "--window-id", f"window-{s}", "--plan-id", f"plan-{s}",
            "--plan-sha256", hashlib.sha256(self.plan.read_bytes()).hexdigest(),
            "--plan", str(self.plan), "--evidence-root-id", f"evidence-{s}",
            "--runs-root", str(self.runs_root),
            "--pre-attempt-id", f"{s}-pre", "--post-attempt-id", f"{s}-post",
            "--pre-custody-locator", str(self.runs_root / "instrument_validation" / f"{s}-pre"),
            "--post-custody-locator", str(self.runs_root / "instrument_validation" / f"{s}-post"),
            "--identity-epoch-json", str(self.desk_epoch),
            "--t1-bindings-json", str(self.desk_t1), "--execute", *extra,
        ]
        stdout, stderr = io.StringIO(), io.StringIO()
        with _FakeMlx(), \
                mock.patch.object(writer, "_sysctl_identity", self._sysctl), \
                mock.patch.object(reserve, "HAZARD_SAMPLER_BINARY", self.w.fake_sampler, create=True), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = reserve.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_legacy_reservation_records_the_desk_bytes(self) -> None:
        # The sandbox pin is committed in the sandbox repository, not in this
        # checkout, so the legacy run uses the existing test-only pin switch.
        code, out, err = self.main("--allow-uncommitted-pin-for-test")
        self.assertEqual(code, 0, out + err)
        slot = open_receipt(self.w.ledger, self.session_id)["slots"]["pre"]
        self.assertEqual(slot["identity_epoch"]["os_build"], "00X000")
        self.assertEqual(self.sysctl_calls, [])
        self.assertEqual(flags(self.custody), [])

    def test_hazard_reservation_records_measured_vectors_and_the_writer_passes_r1(self) -> None:
        make_hazard(self.runs_root, self.custody)
        code, out, err = self.main()
        self.assertEqual(code, 0, out + err)
        slot = open_receipt(self.w.ledger, self.session_id)["slots"]["pre"]
        self.assertEqual(slot["identity_epoch"], self.measured_epoch)
        self.assertEqual(slot["t1_bindings"]["os_build"], "25G83")
        self.assertEqual(sorted(self.sysctl_calls), ["hw.model", "kern.osversion"])
        flag = kinds(self.custody)["desk_identity_differs"]
        self.assertEqual(flag["code"], "calibration.writer_record_flagged")
        self.assertEqual(flag["observed"]["fields"], ["os_build"])
        self.assertEqual(flag["observed"]["desk"], {"os_build": "00X000"})
        self.assertEqual(flag["observed"]["measured"], {"os_build": "25G83"})
        self.assertEqual(flag["observed"]["unreadable"], [])
        self.assertEqual(flag["source"]["legacy_code"], RefusalCode.RESERVED_SLOT_MISMATCH.value)

        # The writer's kept R1 comparison now compares two measurements.
        rig = vpf_hazard.HazardWriterRig(self.w)
        identity = self.w.repo / "writer-fixtures" / "r1-identity.json"
        identity.parent.mkdir(parents=True, exist_ok=True)
        identity.write_text(json.dumps(self.measured_epoch) + "\n", encoding="utf-8")
        state = {"session_id": self.session_id, "epoch": self.measured_epoch,
                 "identity_path": identity,
                 "output_root": self.runs_root / "instrument_validation",
                 "custody_locator": str(self.runs_root / "instrument_validation"
                                        / f"{self.session_id}-pre")}
        rig.custody = lambda _state: self.custody  # flags of this window's custody
        completed = rig.run_writer(state)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "valid")

    def test_unreadable_field_keeps_the_desk_value_and_is_flagged(self) -> None:
        make_hazard(self.runs_root, self.custody)

        def failing(name: str) -> str:
            if name == "hw.model":
                raise OSError("sysctl unavailable")
            return self.LIVE[name]

        self.LIVE = dict(self.LIVE)
        with mock.patch.object(self, "_sysctl", failing):
            code, out, err = self.main()
        self.assertEqual(code, 0, out + err)
        slot = open_receipt(self.w.ledger, self.session_id)["slots"]["pre"]
        self.assertEqual(slot["identity_epoch"]["hardware_model"], "Mac15,9")  # the desk value
        self.assertEqual(slot["identity_epoch"]["os_build"], "25G83")
        flag = kinds(self.custody)["desk_identity_differs"]
        self.assertEqual(flag["observed"]["unreadable"], ["hardware_model"])


if __name__ == "__main__":
    unittest.main()
