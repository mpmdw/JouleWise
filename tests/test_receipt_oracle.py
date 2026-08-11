from __future__ import annotations

import unittest
from unittest import mock

import joulewise.calibration_ledger as calibration_ledger
import joulewise.receipt_oracle as receipt_oracle


class ReceiptOracleTests(unittest.TestCase):
    def test_derivation_executes_the_production_session_lifecycle(self) -> None:
        operation_names = [
            calibration_ledger.append_bracket_session_receipt.__name__,
            calibration_ledger.claim_bracket_session_slot.__name__,
            calibration_ledger.finalize_bracket_session_slot.__name__,
        ]
        with (
            mock.patch.object(
                calibration_ledger,
                "append_bracket_session_receipt",
                wraps=calibration_ledger.append_bracket_session_receipt,
            ) as append,
            mock.patch.object(
                calibration_ledger,
                "claim_bracket_session_slot",
                wraps=calibration_ledger.claim_bracket_session_slot,
            ) as claim,
            mock.patch.object(
                calibration_ledger,
                "finalize_bracket_session_slot",
                wraps=calibration_ledger.finalize_bracket_session_slot,
            ) as finalize,
        ):
            oracle = receipt_oracle.derive_bracket_session_receipt_oracle()

        self.assertEqual(append.call_count, 1)
        self.assertEqual(claim.call_count, len(calibration_ledger.BRACKET_SESSION_SLOTS))
        self.assertEqual(
            finalize.call_count,
            len(calibration_ledger.BRACKET_SESSION_SLOTS),
        )
        self.assertEqual(
            oracle["source"]["operation_functions"],
            operation_names,
        )

    def test_oracle_shape_is_recomputed_from_physical_production_rows(self) -> None:
        oracle = receipt_oracle.derive_bracket_session_receipt_oracle()
        shape = oracle["physical_receipt_shape"]
        business = [
            row
            for row in shape
            if row["schema_version"] != calibration_ledger.CONTROL_SCHEMA
        ]

        self.assertEqual(oracle["schema_version"], receipt_oracle.ORACLE_SCHEMA)
        self.assertEqual(oracle["status"], "derived_from_production_model")
        self.assertEqual(oracle["session_terminal_state"], "finalized")
        self.assertEqual(oracle["receipt_count"], len(shape))
        self.assertEqual(oracle["logical_operation_count"], len(business))
        self.assertEqual(
            len(shape),
            len(business) * calibration_ledger.APPEND_RECORDS_PER_OPERATION,
        )
        self.assertEqual(
            oracle["terminal_sequence_rule"]["delta"],
            len(shape),
        )
        self.assertIsNone(oracle["terminal_sequence"])
        self.assertEqual(oracle["arm_time_receipts"], [])

        for offset in range(0, len(shape), calibration_ledger.APPEND_RECORDS_PER_OPERATION):
            intent, target = shape[offset : offset + calibration_ledger.APPEND_RECORDS_PER_OPERATION]
            self.assertEqual(intent["schema_version"], calibration_ledger.CONTROL_SCHEMA)
            self.assertEqual(intent["event"], calibration_ledger.APPEND_INTENT_EVENT)
            self.assertEqual(intent["target_schema_version"], target["schema_version"])
            self.assertEqual(intent["target_event"], target["event"])
            self.assertEqual(intent["slot"], target["slot"])

    def test_derivation_is_deterministic(self) -> None:
        first = receipt_oracle.derive_bracket_session_receipt_oracle()
        second = receipt_oracle.derive_bracket_session_receipt_oracle()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
