"""Stored minted rows are selected by archive identity, not consumer semantics.

Uses committed S0 bytes and S3's explicit adapter/ready-session test support;
the row validator and allowance reader themselves remain real.
"""
import json
from dataclasses import replace
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import whole_window as ww
from tests.b5_analysis import fixtures_s3 as fx


class RowSelectionContextTests(unittest.TestCase):
    def setUp(self):
        self.case = fx.Case("BETA_STD")
        self.addCleanup(self.case.close)
        self.case.row["consumption_semantics_id"] = ww.MINTED_CONSUMPTION_SEMANTICS_ID
        self.case.row["evaluation_basis"].pop("consumption_semantics_id", None)
        self.case.rehash_basis()
        self.case.bind_row()
        self.log = self.case.window.claim / "campaign_log.jsonl"
        self.original = self.log.read_bytes()
        self.addCleanup(self.log.write_bytes, self.original)
        rows = [json.loads(line) for line in self.original.splitlines() if line.strip()]
        rows = [self.case.row if row.get("record_type") == "idle_admission_whole_window_verdict"
                else row for row in rows]
        self.log.write_text("".join(json.dumps(row) + "\n" for row in rows))
        self.session = self.case.session()
        self.kwargs = dict(evaluation_basis_sha256=self.case.row["evaluation_basis"]["sha256"],
            consumption_session=self.session,
            consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID)

    def refusals(self):
        return ww.whole_window_refusal_reasons(self.case.window.claim,
            set(self.case.row["bundle_ids"]), **self.kwargs)

    def allowances(self):
        return ww.whole_window_drift_allowances(self.case.window.claim,
            set(self.case.row["bundle_ids"]), **self.kwargs)

    def test_s1_named_minted_row_reaches_real_validator(self):
        with fx.adapter_projection(self.case), mock.patch.object(ww, "_validate_row", wraps=ww._validate_row) as validate:
            result = self.refusals()
        self.assertEqual(result, ())
        validate.assert_called_once()
        self.assertEqual(validate.call_args.args[0], self.case.row)
        self.assertIs(validate.call_args.kwargs["consumption_session"], self.session)

    def test_s2_no_context_preserves_missing_triple(self):
        self.session._archive_context = None
        with fx.adapter_projection(self.case):
            self.assertEqual(self.refusals(), ("whole_window_neg8_verdict_missing",
                "adapter_continuity_evidence_missing", "cpu_admission_core_missing"))
            self.assertEqual(self.allowances().status, "absent")

    def test_s3_basis_cannot_replace_named_digest(self):
        record = self.case.read(ww.NEG8_HARVEST_ALLOWANCE_RECORD)
        record["verdict"]["row_sha256"] = "f" * 64
        self.case.write(ww.NEG8_HARVEST_ALLOWANCE_RECORD, record)
        with fx.adapter_projection(self.case), mock.patch.object(ww, "_validate_row", wraps=ww._validate_row) as validate:
            self.assertEqual(self.refusals(), ("whole_window_verdict_provenance_invalid",))
            self.assertEqual(self.allowances().status, "absent")
        validate.assert_not_called()

    def test_s4_archive_allowances_are_returned(self):
        with fx.adapter_projection(self.case):
            result = self.allowances()
            bracket, problem = ww.harvest_neg8_allowance_bracket(self.case.archive, self.case.row)
        self.assertIsNone(problem)
        self.assertEqual(result, ww._bracket_drift_allowances(bracket, self.case.row["evaluation_basis"]))
        self.assertEqual(result.status, "allowances")

    def test_s5_session_semantics_must_match_request(self):
        self.kwargs["consumption_semantics_id"] = ww.MINTED_CONSUMPTION_SEMANTICS_ID
        with fx.adapter_projection(self.case):
            self.assertEqual(self.refusals(), ("whole_window_verdict_provenance_invalid",))
            self.assertEqual(self.allowances().status, "absent")

    def test_context_default_snapshot_is_owned_by_archive(self):
        from joulewise.analysis_engine.inputs import archive_snapshot
        with mock.patch.object(ww, "load_calibration_ledger_snapshot", side_effect=AssertionError("live ledger read")) as live:
            session = ww.AuthenticatedConsumptionSession(self.case.window.claim,
                set(self.case.row["bundle_ids"]), archive_context=self.case.context)
        live.assert_not_called()
        self.assertEqual(session.calibration_ledger_snapshot, archive_snapshot(self.case.context))

    def test_explicit_failed_snapshot_still_refuses(self):
        from joulewise.analysis_engine.inputs import archive_snapshot
        snapshot = replace(archive_snapshot(self.case.context), refusal_reasons=("calibration_ledger_baseline_missing",))
        session = ww.AuthenticatedConsumptionSession(self.case.window.claim,
            set(self.case.row["bundle_ids"]), archive_context=self.case.context,
            calibration_ledger_snapshot=snapshot)
        session._prepare(bundle_paths={bid:self.case.window.claim/bid for bid in self.case.row["bundle_ids"]},
            policy=SimpleNamespace(calibration_bracketing=object()))
        self.assertFalse(session.ready)
        self.assertEqual(session.refusal_reasons, ("calibration_ledger_baseline_missing",))


if __name__ == "__main__":
    unittest.main()
