"""TRANSFER-FIDUCIAL-01 reason-partition smoke pins."""

from __future__ import annotations

import inspect
import unittest

from joulewise.analysis_engine.claims import REASON_CODES
from joulewise.analysis_engine.reason_kinds import (
    CONTRACT_REASON_CODES,
    DATA_REASON_CODES,
    DEAD_REASON_CODES,
    LOCK_REASON_CODES,
    assert_data_reason_only,
)


class TransferReasonPartitionSmokeTests(unittest.TestCase):
    def test_transfer_reason_codes_partition_exactly_once(self) -> None:
        partitions = (
            DATA_REASON_CODES,
            CONTRACT_REASON_CODES,
            DEAD_REASON_CODES,
            LOCK_REASON_CODES,
        )
        expected = {
            "transfer_fiducial_claim_ineligible": LOCK_REASON_CODES,
            "transfer_fiducial_class_inconsistent": CONTRACT_REASON_CODES,
        }
        for code, owner in expected.items():
            with self.subTest(code=code):
                self.assertIn(code, REASON_CODES)
                self.assertIn(code, owner)
                self.assertEqual(sum(code in values for values in partitions), 1)

    def test_assert_data_reason_only_default_lock_is_unchanged(self) -> None:
        default = inspect.signature(assert_data_reason_only).parameters[
            "expect_lock"
        ].default
        self.assertEqual(default, "mock_telemetry_claim_ineligible")


if __name__ == "__main__":
    unittest.main()

