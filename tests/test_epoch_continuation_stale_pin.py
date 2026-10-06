"""Gate prune 2, P2-VPF (vpf review Sol F2): continued epochs past a stale pin.

On the HAZARD_PACK path a head pin that lags the window's own reservation is a
record (erratum s3-reservation-stop): the reservation appends to the physical
tail and the writer judges the extension shape from the reservation.  Before
this change the writer's continued-epoch authentication still demanded the
pin-anchored shape, so a stale pin silently dropped every continued epoch and
the writer refused a machine in a continued epoch (acceptance_artifact_epoch_
mismatch).  ``allow_stale_pin`` accepts the reservation-anchored shape; every
session-row cross-check is unchanged, and the default keeps today's refusal.
All ledgers and captures are synthetic.
"""

from __future__ import annotations

from dataclasses import replace
import unittest

from joulewise import calibration_bracketing as bracket
from joulewise import calibration_epoch_continuation as continuation
from joulewise.calibration_ledger import (
    abort_bracket_session, append_bracket_session_receipt, load_calibration_ledger_snapshot,
)
from scripts import validate_powermetrics_fiducial as writer
from tests.fixtures.epoch_bootstrap.build import TARGET_EPOCH, T1_BINDINGS
from tests import test_epoch_continuation as base_tests

SUCCESSOR_EPOCH = base_tests.SUCCESSOR_EPOCH


def _reserve(fixture: dict, session_id: str, **kwargs) -> None:
    runs = fixture["runs"]
    append_bracket_session_receipt(
        fixture["ledger"], session_id=session_id, window_id=f"{session_id}-window",
        plan_id=f"{session_id}-plan", plan_sha256="a" * 64, evidence_root_id=f"{session_id}-evidence",
        runs_root=runs,
        slots={name: {"attempt_id": f"{session_id}-{name}",
                      "custody_locator": str(runs / "instrument_validation" / f"{session_id}-{name}"),
                      "identity_epoch": TARGET_EPOCH, "t1_bindings": T1_BINDINGS}
               for name in ("pre", "post")},
        head_pin_path=fixture["pin"], repo_root=fixture["root"], **kwargs,
    )


def stale_pin_open_capture(fixture: dict):
    """A previous window aborted past the committed pin, then this window reserved.

    The desk pin advance did not run between the two windows, so the pin lags
    the physical head; the reservation recorded the relation and appended to
    the physical tail (the HAZARD reservation path).
    """

    _reserve(fixture, "previous-window", require_committed_pin=True)
    abort_bracket_session(fixture["ledger"], session_id="previous-window", reason="previous window")
    record: dict = {}
    _reserve(fixture, "capture-in-flight", require_committed_pin=False, pin_relation_record=record)
    assert record["relation"] == "physical_ahead", record
    return load_calibration_ledger_snapshot(
        fixture["ledger"], fixture["pin"], require_committed_pin=False,
        verify_custody=False, mode="issuing", repo_root=fixture["root"],
    )


class ContinuedEpochPastStalePinTests(unittest.TestCase):
    # The continuation fixture machinery of tests/test_epoch_continuation.py.
    # Borrowed through the module so that class is not collected a second time here.
    setUp = base_tests.EpochContinuationTests.setUp
    build = base_tests.EpochContinuationTests.build
    args = base_tests.EpochContinuationTests.args
    run_cli = base_tests.EpochContinuationTests.run_cli
    prepare = base_tests.EpochContinuationTests.prepare
    candidate = base_tests.EpochContinuationTests.candidate
    issued = base_tests.EpochContinuationTests.issued

    def stale_snapshot(self):
        # Call inside ``self.issued()``: the candidate is prepared from the
        # terminal derivation night first, then the ledger moves past the pin.
        snapshot = stale_pin_open_capture(self.fixture)
        self.assertEqual(set(snapshot.refusal_reasons), {
            "calibration_ledger_bracket_session_open", "calibration_ledger_head_mismatch"})
        self.assertFalse(snapshot.is_governed_open_bracket_extension)
        self.assertTrue(snapshot.is_open_bracket_extension_past_stale_pin)
        return snapshot

    def load(self, snapshot, **kwargs):
        details: list = []
        loaded = continuation.load_epoch_continuations(
            self.artifact, snapshot, refusal_details=details, **kwargs)
        return loaded, details

    def test_default_still_drops_the_continuation_past_a_stale_pin(self):
        self.build()
        with self.issued():
            snapshot = self.stale_snapshot()
            loaded, details = self.load(snapshot)
        self.assertEqual(loaded, ())
        self.assertEqual(details[0]["detail"], "ledger_snapshot_invalid")

    def test_hazard_path_authenticates_the_continuation_past_a_stale_pin(self):
        self.build()
        with self.issued():
            snapshot = self.stale_snapshot()
            loaded, details = self.load(snapshot, allow_stale_pin=True)
            epochs = continuation.acceptance_judged_epochs(
                self.artifact, snapshot, allow_stale_pin=True)
        self.assertEqual(details, [])
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].ledger_cross_check,
                         "verified_terminal_derivation_session_past_stale_pin")
        self.assertIn(SUCCESSOR_EPOCH, [dict(epoch) for epoch in epochs])

    def test_the_writer_accepts_a_continued_epoch_past_a_stale_pin_only_on_the_hazard_path(self):
        path = bracket.ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH
        self.build()
        with self.issued():
            snapshot = self.stale_snapshot()
            with self.assertRaises(writer._AcceptancePreflightError) as caught:
                writer._derive_preflight_systematic_screen_s(
                    SUCCESSOR_EPOCH, acceptance_path=path, ledger_snapshot=snapshot,
                    allow_stale_code=True)
            self.assertEqual(caught.exception.reason, "acceptance_artifact_epoch_mismatch")
            record: dict = {}
            screen = writer._derive_preflight_systematic_screen_s(
                SUCCESSOR_EPOCH, acceptance_path=path, ledger_snapshot=snapshot,
                preflight_record=record, allow_stale_code=True, allow_stale_pin=True)
        self.assertEqual(str(screen), self.rule["level_screen_s"])
        self.assertIn(SUCCESSOR_EPOCH, record["judged_epochs"])
        self.assertEqual(record["continuation_refusals"], [])

    def test_the_session_row_cross_check_still_runs_past_a_stale_pin(self):
        self.build()
        with self.issued():
            snapshot = self.stale_snapshot()
            # A finalized row of the continuation's session that disagrees with
            # the issued file still refuses.
            session = next(item for item in snapshot.bracket_sessions
                           if item.state != "open" and item.session_kind == "derivation")
            name, row = next(iter(session.finalized_slots.items()))
            tampered_row = replace(row, exact_bound_lexeme_s="0.099")
            tampered_session = replace(session, finalized_slots={
                **session.finalized_slots, name: tampered_row})
            tampered = replace(
                snapshot,
                bracket_sessions=tuple(tampered_session if item is session else item
                                       for item in snapshot.bracket_sessions),
                observations=tuple(tampered_row if item == row else item
                                   for item in snapshot.observations))
            loaded, details = self.load(tampered, allow_stale_pin=True)
        self.assertEqual(loaded, ())
        self.assertEqual(details[0]["detail"], "acknowledged_row_disagrees")

    def test_integrity_reasons_and_a_divergent_pin_still_refuse_with_the_flag(self):
        self.build()
        with self.issued():
            snapshot = self.stale_snapshot()
            for reason in ("calibration_ledger_malformed", "calibration_ledger_rollback",
                           "calibration_ledger_custody_invalid", "calibration_ledger_pending"):
                with self.subTest(reason=reason):
                    tainted = replace(snapshot, refusal_reasons=tuple(
                        sorted(set(snapshot.refusal_reasons) | {reason})))
                    loaded, details = self.load(tainted, allow_stale_pin=True)
                    self.assertEqual(loaded, ())
                    self.assertEqual(details[0]["detail"], "ledger_snapshot_invalid")
            divergent = replace(snapshot, committed_head_digest="e" * 64)
            loaded, details = self.load(divergent, allow_stale_pin=True)
            self.assertEqual(loaded, ())
            self.assertEqual(details[0]["detail"], "ledger_snapshot_invalid")
            second = next(item for item in snapshot.bracket_sessions if item.state == "open")
            two_open = replace(snapshot, bracket_sessions=(
                *snapshot.bracket_sessions, replace(second, session_id="another-open")))
            loaded, details = self.load(two_open, allow_stale_pin=True)
            self.assertEqual(loaded, ())
            self.assertEqual(details[0]["detail"], "ledger_snapshot_invalid")

    def test_an_exact_pin_is_unchanged_by_the_flag(self):
        from tests.fixtures.epoch_continuation.build import append_open_capture_session

        self.build()
        with self.issued():
            snapshot = append_open_capture_session(self.fixture)
            for kwargs in ({}, {"allow_stale_pin": True}):
                with self.subTest(**kwargs):
                    loaded, details = self.load(snapshot, **kwargs)
                    self.assertEqual(details, [])
                    self.assertEqual(loaded[0].ledger_cross_check,
                                     "verified_terminal_derivation_session")


if __name__ == "__main__":
    unittest.main()
