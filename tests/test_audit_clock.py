from __future__ import annotations

import math
import unittest

from joulewise.clock import FakeClock


class ClockBugPins(unittest.TestCase):
    # Rank 21: FakeClock.sleep() accepts bool and non-finite durations.
    def test_fake_clock_rejects_bool_sleep_duration(self) -> None:
        with self.assertRaises(ValueError):
            FakeClock().sleep(True)

    def test_fake_clock_rejects_nan_sleep_duration(self) -> None:
        with self.assertRaises(ValueError):
            FakeClock().sleep(math.nan)

    def test_fake_clock_rejects_inf_sleep_duration(self) -> None:
        with self.assertRaises(ValueError):
            FakeClock().sleep(math.inf)


if __name__ == "__main__":
    unittest.main()
