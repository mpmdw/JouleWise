from __future__ import annotations

import math
import plistlib
import unittest
from datetime import datetime

from joulewise.adapters.powermetrics import parse_powermetrics_records


def plist_document(**processor_overrides) -> bytes:
    processor = {
        "cpu_power": 1000.0,
        "gpu_power": 2000.0,
        "ane_power": 3000.0,
        "cpu_energy": 10,
        "gpu_energy": 20,
        "ane_energy": 30,
    }
    processor.update(processor_overrides)
    return plistlib.dumps(
        {
            "timestamp": datetime(2026, 7, 7, 0, 0, 0),
            "elapsed_ns": 1_000_000_000,
            "processor": processor,
        }
    )


class PowermetricsParserBugPins(unittest.TestCase):
    # A1: a trailing truncated plist tail rejects the whole capture instead of salvaging complete frames.
    @unittest.expectedFailure
    def test_parser_ignores_trailing_truncated_document_after_valid_frames(self) -> None:
        try:
            records = parse_powermetrics_records(plist_document() + b"\0<plist")
        except ValueError as exc:
            self.fail(f"A1: trailing truncated plist tail rejected the complete frame: {exc}")
        self.assertEqual(len(records), 1)

    # A5: rail power values can parse to NaN and contaminate downstream power samples.
    @unittest.expectedFailure
    def test_parser_rejects_non_finite_power_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite"):
            parse_powermetrics_records(plist_document(cpu_power=math.nan))


if __name__ == "__main__":
    unittest.main()
