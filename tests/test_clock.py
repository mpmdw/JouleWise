import unittest

from joulewise.clock import Clock, FakeClock, SystemClock


class ClockTests(unittest.TestCase):
    def test_system_clock_satisfies_protocol(self) -> None:
        clock = SystemClock()
        self.assertIsInstance(clock, Clock)
        before = clock.now()
        clock.sleep(0.001)
        self.assertGreaterEqual(clock.now(), before)
        self.assertEqual(clock.info()["kind"], "system")
        self.assertIn("monotonic_minus_wall_s", clock.info())
        stamp = clock.stamp()
        self.assertLessEqual(stamp.monotonic_before_s, stamp.monotonic_after_s)
        self.assertGreater(stamp.epoch_s, 0.0)

    def test_fake_clock_advances_instantly(self) -> None:
        clock = FakeClock(start=100.0)
        self.assertIsInstance(clock, Clock)
        self.assertEqual(clock.now(), 100.0)
        clock.sleep(30.0)
        self.assertEqual(clock.now(), 130.0)
        self.assertEqual(clock.stamp().epoch_s, 130.0)
        self.assertEqual(clock.info(), {"kind": "fake", "start_s": 100.0})

    def test_fake_clock_rejects_negative_sleep(self) -> None:
        clock = FakeClock()
        with self.assertRaises(ValueError):
            clock.sleep(-1.0)


if __name__ == "__main__":
    unittest.main()
