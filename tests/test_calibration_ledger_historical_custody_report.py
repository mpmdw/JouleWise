"""Gate prune 2, P2-VPF S5: the harvest's one full historical custody pass.

``calibration_ledger.historical_custody_report`` re-hashes every governed
artifact of every historical observation, judges each observation separately,
and never raises.  The fixture ledger holds three committed, finalized
historical observations (``CustodyFixture``).
"""

from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest import mock

from joulewise import calibration_ledger as ledger
from tests.calibration_exits_fixtures.custody_hang import CustodyFixture


def tearDownModule() -> None:
    from tests import test_calibration_exits as exits

    exits.assert_no_owned_fake_sampler_survivors()


class HistoricalCustodyReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = CustodyFixture().__enter__()
        self.addCleanup(self.fixture.__exit__, None, None, None)

    def report(self, **kwargs):
        return ledger.historical_custody_report(
            self.fixture.ledger, repo_root=self.fixture.repo, **kwargs)

    def test_a_clean_ledger_verifies_every_observation(self):
        report = self.report()
        self.assertEqual(report["schema_version"], ledger.HISTORICAL_CUSTODY_REPORT_SCHEMA)
        self.assertEqual(report["status"], "verified", report)
        self.assertEqual((report["observations"], report["verified"]), (3, 3))
        self.assertEqual((report["mismatched"], report["unmeasured"]), ([], []))
        self.assertEqual(report["ledger_reasons"], [])
        inspection = ledger.inspect_calibration_ledger(self.fixture.ledger)
        self.assertEqual((report["head_sequence"], report["head_digest"]),
                         (inspection.head_sequence, inspection.head_digest))

    def test_each_changed_or_missing_capture_is_named_and_the_rest_still_verify(self):
        # Refusal census 2026-10-06: a missing file is evicted (unmeasured);
        # only present bytes that differ are a mismatch (EXCLUDE_WINDOW).
        (self.fixture.custodies[0] / "events.jsonl").unlink()
        trace = self.fixture.custodies[2] / "power_trace.csv"
        trace.write_bytes(trace.read_bytes() + b"\n")
        report = self.report()
        self.assertEqual(report["status"], "mismatch")
        self.assertEqual(report["verified"], 1)
        self.assertEqual(len(report["mismatched"]), 1, report)
        (changed,) = report["mismatched"]
        self.assertEqual(Path(changed["custody_locator"]).name, self.fixture.custodies[2].name)
        self.assertEqual(changed["reasons"], ["calibration_ledger_custody_invalid"])
        (evicted,) = report["unmeasured"]
        self.assertEqual(Path(evicted["custody_locator"]).name, self.fixture.custodies[0].name)
        self.assertIs(evicted["evicted"], True)

    def test_census_an_evicted_capture_is_unmeasured_not_a_mismatch(self):
        # At ba0e0c72e an evicted historical capture (a file or the whole
        # capture directory gone, e.g. offloaded to iCloud) was "mismatch",
        # which the harvest turns into calibration.historical_custody_mismatch
        # (EXCLUDE_WINDOW) for every later window.
        import shutil

        (self.fixture.custodies[0] / "events.jsonl").unlink()
        shutil.rmtree(self.fixture.custodies[1])
        report = self.report()
        self.assertEqual(report["status"], "unmeasured", report)
        self.assertEqual(report["mismatched"], [])
        self.assertEqual(report["verified"], 1)
        self.assertEqual({Path(item["custody_locator"]).name for item in report["unmeasured"]},
                         {self.fixture.custodies[0].name, self.fixture.custodies[1].name})
        self.assertTrue(all(item["evicted"] is True for item in report["unmeasured"]))

    def test_census_a_changed_capture_beside_an_evicted_file_is_still_a_mismatch(self):
        (self.fixture.custodies[0] / "events.jsonl").unlink()
        trace = self.fixture.custodies[0] / "power_trace.csv"
        trace.write_bytes(trace.read_bytes() + b"\n")
        report = self.report()
        self.assertEqual(report["status"], "mismatch", report)
        self.assertEqual([Path(item["custody_locator"]).name for item in report["mismatched"]],
                         [self.fixture.custodies[0].name])

    def test_an_unreadable_ledger_is_unmeasured_and_never_raises(self):
        report = ledger.historical_custody_report(self.fixture.repo / "absent.jsonl")
        self.assertEqual(report["status"], "unmeasured")
        self.assertIn("error", report)
        self.assertEqual(report["observations"], 0)

    def test_under_the_night_budget_marker_rows_are_unmeasured_not_verified(self):
        with mock.patch.dict(os.environ, {ledger.NIGHT_CUSTODY_BUDGET_ENV: "120"}):
            report = self.report()
        self.assertEqual(report["status"], "unmeasured")
        self.assertEqual(len(report["unmeasured"]), 3)
        self.assertEqual(report["verified"], 0)

    def _two_sessions(self):
        observations = ledger.load_calibration_ledger_snapshot(
            self.fixture.ledger, self.fixture.pin, repo_root=self.fixture.repo,
            verify_custody=False).observations
        return [replace_session(observations[0], "own-window"),
                *(replace_session(row, "earlier-window") for row in observations[1:])]

    def test_one_session_can_be_left_out_and_only_that_session(self):
        # Review M8: excluding one session must keep every other session's rows.
        with mock.patch.object(ledger, "_custody_observations",
                               return_value=self._two_sessions()):
            report = self.report(exclude_session_id="own-window")
        self.assertEqual(report["status"], "verified", report)
        self.assertEqual((report["observations"], report["verified"]), (2, 2))
        self.assertEqual(report["excluded_observations"], 1)

    def test_a_left_out_session_mismatch_does_not_hide_another_sessions(self):
        trace = self.fixture.custodies[2] / "power_trace.csv"
        trace.write_bytes(trace.read_bytes() + b"\n")
        with mock.patch.object(ledger, "_custody_observations",
                               return_value=self._two_sessions()):
            report = self.report(exclude_session_id="own-window")
        self.assertEqual(report["status"], "mismatch", report)
        self.assertEqual([item["bracket_session_id"] for item in report["mismatched"]],
                         ["earlier-window"])

    def test_every_row_left_out_is_unmeasured_not_verified(self):
        # Review R4: nothing re-hashed is never "verified".
        with mock.patch.object(ledger, "_custody_observations",
                               return_value=[replace_session(row, "own-window")
                                             for row in self._two_sessions()]):
            report = self.report(exclude_session_id="own-window")
        self.assertEqual((report["status"], report["observations"]), ("unmeasured", 0))
        self.assertEqual(report["unmeasured_reason"], "no_observations_checked")
        self.assertEqual(report["excluded_observations"], 3)

    def test_an_empty_ledger_is_unmeasured_not_verified(self):
        # Review R4: a zero-byte (fully truncated) ledger parses to no receipts.
        empty = self.fixture.repo / "empty-ledger.jsonl"
        empty.write_bytes(b"")
        report = ledger.historical_custody_report(empty, repo_root=self.fixture.repo)
        self.assertEqual(report["status"], "unmeasured", report)
        self.assertEqual(report["unmeasured_reason"], "no_observations_checked")
        self.assertEqual((report["observations"], report["verified"]), (0, 0))


def replace_session(observation, session_id):
    from dataclasses import replace

    return replace(observation, bracket_session_id=session_id)


if __name__ == "__main__":
    unittest.main()
