"""F1 preparation scope, using S3's archived bracket and small member probes.

The mock-adapter kept summary bypass is explicit in this unit test. These
focused preparation tests do not claim production-shaped chain validation.
"""
from dataclasses import replace
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

from joulewise import whole_window as ww
from joulewise.calibration_ledger import CalibrationLedgerSnapshot, LEDGER_SCHEMA
from tests.b5_analysis import fixtures_s3 as fx


class RemovedMemberPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.window = fx.cached("BETA_STD")
        cls.context = fx.context(cls.window)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s10-preparation-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.paths = {}
        for bid in ("kept", "removed"):
            path = self.root / bid
            path.mkdir()
            (path / "summary_metrics.json").write_text('{"synthetic":true}\n')
            (path / "metadata.json").write_text(json.dumps({
                "fault": bid == "removed",
                "uncertainty_evidence": {"clock_anchor": {"method": "retired-s10-probe"}},
                "instrument_calibration": {"verified_effective_b_fiducial_s": .91331},
            }))
            self.paths[bid] = path

    def prepare(self, *, removed=("removed",), survivors=(), context=True, empty=False):
        if empty:
            for path in self.paths["removed"].iterdir():
                path.unlink()
        ctx = replace(self.context, removed_bundle_ids=frozenset(removed),
                      survivor_bundle_ids=frozenset(survivors)) if context else None
        snapshot = CalibrationLedgerSnapshot(LEDGER_SCHEMA, self.root / "ledger", 0, "0" * 64, (), (), ())
        session = ww.AuthenticatedConsumptionSession(self.root, set(self.paths) | {"removed"},
            calibration_ledger_snapshot=snapshot, archive_context=ctx)
        real_pipeline = ww.capture_pipeline_refusal
        def pipeline(metadata):
            return real_pipeline(metadata) if not metadata or metadata.get("fault") else None
        with mock.patch.object(ww, "capture_pipeline_refusal", side_effect=pipeline), \
             mock.patch.object(ww, "_current_strict_summary", return_value=False), \
             mock.patch.object(ww, "calibration_bracket_for_bundles",
                               return_value=(ww._archive_window_assessment(self.context), ())):
            session._prepare(bundle_paths=self.paths, policy=SimpleNamespace(calibration_bracketing=object()))
        return session

    def test_p1_removed_superseded_is_disclosed_and_bound_is_bracket(self):
        session = self.prepare()
        self.assertTrue(session.ready, session.refusal_reasons)
        self.assertIn("removed_member_preparation:capture_pipeline_superseded:removed",
                      session.removed_member_preparation)
        self.assertEqual(session.operative_fiducial_bound_s, self.context.window_bracket["b_fiducial_s"])
        self.assertNotEqual(session.operative_fiducial_bound_s, .91331)

    def test_p2_aborted_member_is_disclosed(self):
        session = self.prepare(empty=True)
        self.assertTrue(session.ready, session.refusal_reasons)
        self.assertTrue(any(line.endswith(":removed") for line in session.removed_member_preparation))

    def test_p3_kept_defect_still_refuses(self):
        session = self.prepare(removed=())
        self.assertFalse(session.ready)
        self.assertEqual(session.refusal_reasons, ("capture_pipeline_superseded",))

    def test_p4_removed_survivor_still_refuses(self):
        session = self.prepare(survivors=("removed",))
        self.assertFalse(session.ready)
        self.assertEqual(session.refusal_reasons, ("capture_pipeline_superseded",))

    def test_p5_without_context_still_refuses(self):
        session = self.prepare(context=False)
        self.assertFalse(session.ready)
        self.assertEqual(session.refusal_reasons, ("capture_pipeline_superseded",))

    def test_p6_removed_summary_and_provenance_are_never_served(self):
        session = self.prepare()
        self.assertTrue(session.ready)
        self.assertIsNone(session.summary_for("removed"))
        self.assertIsNone(session.provenance_for("removed"))

    def test_absent_removed_directory_or_mapping_is_disclosed(self):
        for path in self.paths["removed"].iterdir():
            path.unlink()
        self.paths["removed"].rmdir()
        self.assertTrue(self.prepare().ready)
        self.paths.pop("removed")
        # A referenced removed id absent from bundle_paths is still audited.
        session = self.prepare()
        self.assertTrue(session.ready)
        self.assertIn("removed_member_preparation:capture_pipeline_absent:removed",
                      session.removed_member_preparation)

    def test_strict_instrument_and_reduction_failures_are_isolated(self):
        metadata = json.loads((self.paths["removed"] / "metadata.json").read_bytes())
        metadata["fault"] = False
        (self.paths["removed"] / "metadata.json").write_text(json.dumps(metadata))
        snapshot = CalibrationLedgerSnapshot(LEDGER_SCHEMA, self.root / "ledger", 0, "0" * 64, (), (), ())
        ctx = replace(self.context, removed_bundle_ids=frozenset({"removed"}), survivor_bundle_ids=frozenset())
        for failure in ("strict", "instrument", "reduction"):
            with self.subTest(failure=failure):
                session = ww.AuthenticatedConsumptionSession(self.root, set(self.paths),
                    calibration_ledger_snapshot=snapshot, archive_context=ctx)
                with mock.patch.object(ww, "capture_pipeline_refusal", return_value=None), \
                     mock.patch.object(ww, "_current_strict_summary", side_effect=lambda summary, path:
                         path.name == "removed" and failure != "strict"), \
                     mock.patch.object(ww, "_verify_instrument_calibration", return_value=
                         (None, "instrument_calibration_invalid") if failure == "instrument" else (.01331, None)), \
                     mock.patch.object(ww, "_rederive_summary_for_authenticated_fiducial_bound",
                                       side_effect=ValueError("synthetic failed reduction")):
                    # The metadata scalar must match the authenticated member
                    # bound to reach the actual reduction-failure branch.
                    metadata["instrument_calibration"]["verified_effective_b_fiducial_s"] = .01331
                    (self.paths["removed"] / "metadata.json").write_text(json.dumps(metadata))
                    session._prepare(bundle_paths=self.paths,
                        policy=SimpleNamespace(calibration_bracketing=object()))
                self.assertTrue(session.ready, session.refusal_reasons)
                reason = "whole_window_verdict_provenance_invalid" if failure == "strict" else "instrument_calibration_invalid"
                self.assertIn(f"removed_member_preparation:{reason}:removed", session.removed_member_preparation)
                self.assertIsNone(session.summary_for("removed"))

    def test_only_absent_removed_reference_does_not_fail_preparation(self):
        for path in self.paths["removed"].iterdir():
            path.unlink()
        self.paths["removed"].rmdir()
        self.paths.clear()
        session = self.prepare()
        self.assertTrue(session.ready, session.refusal_reasons)
        self.assertIn("removed_member_preparation:capture_pipeline_absent:removed",
                      session.removed_member_preparation)
        self.assertIsNone(session.summary_for("removed"))


if __name__ == "__main__":
    unittest.main()
