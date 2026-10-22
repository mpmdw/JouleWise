"""Review regressions for cadence quantization and physical power resolution."""

import itertools
import tempfile
import unittest
from pathlib import Path

from joulewise.align.power.ina3221 import Ina3221Sampler
from tests.align.test_power_ina3221 import Ina3221Test


class CharacterizationReviewTest(unittest.TestCase):
    def test_mainline_shunt_sum_is_not_a_bus_rail(self):
        with tempfile.TemporaryDirectory() as tmp:
            dev = Ina3221Test().make_device(Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
            (dev / "in7_label").write_text("sum of shunt voltages")
            (dev / "in7_input").write_text("32")
            sampler = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=1_000_000)
            self.assertEqual(len(sampler.discover()), 1)  # Exactly one physical V/I pair.
            self.assertTrue(any(f.startswith("summation_channel_skipped") for f in sampler.flags))
            self.assertFalse(any(f.startswith("missing_rail_attribute") for f in sampler.flags))

    def test_cadence_uses_endpoint_span_and_flags_poll_limit(self):
        for poll in (100_000, 300_000, 500_000, 1_000_000):
            with self.subTest(poll=poll), tempfile.TemporaryDirectory() as tmp:
                Ina3221Test().make_device(Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
                now = [0]
                conversion = 840_000  # Datasheet minimum: 140 us * bus/shunt * 3 rails.
                def clock():
                    now[0] += 5_000  # Scenario input: two clock reads cost 10 us.
                    return now[0]
                def read(path):
                    if path.name == "curr1_input":
                        return str(2000 + 8 * ((now[0] // conversion) % 7))
                    return path.read_text().strip()
                def sleep(sec):
                    now[0] += round(sec * 1e9)
                sampler = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=poll,
                                         clock=clock, read_text=read)
                rail, = sampler.characterize(reads=3000, sleep=sleep).rails
                if poll < conversion:
                    # End poll errors differ by < one actual poll period;
                    # dividing by observed periods gives the cadence error bound.
                    bound = (poll + 10_000) / len(rail.distinct_periods_ns)
                    self.assertLessEqual(abs(rail.cadence_ns - conversion), bound)
                else:
                    self.assertIn("cadence_poll_limited", rail.flags)

    def test_watt_resolution_propagates_both_lattices(self):
        with tempfile.TemporaryDirectory() as tmp:
            Ina3221Test().make_device(Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
            seq = iter(itertools.product(range(6), range(40)))
            current = [None]
            now = [0]
            def clock():
                now[0] += 20_000  # Explicit simulated read cost.
                return now[0]
            def read(path):
                if path.name == "in1_input":
                    a, b = next(seq)
                    current[0] = (5000 - 8 * a, 2000 + 8 * b)
                    return str(current[0][0])
                if path.name == "curr1_input":
                    return str(current[0][1])
                return path.read_text().strip()
            rail, = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=1_000_000,
                                    clock=clock, read_text=read).characterize(
                                        reads=240, sleep=lambda _: None).rails
            # One bus-voltage LSB at 2 A is 8 mV * 2 A = 0.016 W;
            # combined resolution must include this rather than VI cancellation.
            self.assertGreaterEqual(rail.quantum_w, 0.016)
            expected = (4980 * 8 + 2156 * 8 + 8 * 8) / 1e6
            # No printed uncertainty: required relative agreement bar.
            self.assertAlmostEqual(rail.quantum_w, expected, delta=expected * 1e-6)


if __name__ == "__main__":
    unittest.main()
