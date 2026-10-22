"""Fake sysfs tests use the production discovery and acquisition paths."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.align.interfaces import PowerSampler
from joulewise.align.power.ina3221 import Ina3221Sampler


class Ina3221Test(unittest.TestCase):
    def make_device(self, root, shape, legacy=False):
        device = root / shape
        device.mkdir(parents=True)
        values = ({"rail_name_0": "VDD_IN", "in_voltage0_input": "5000",
                   "in_current0_input": "2000"} if legacy else
                  {"in1_label": "VDD_IN", "in1_input": "5000", "curr1_input": "2000"})
        for name, value in dict(values, name="ina3221", update_interval="1").items():
            (device / name).write_text(value)
        return device

    def test_layouts_and_units(self):
        shapes = (
            ("bus/i2c/drivers/ina3221/1-0040/hwmon/hwmon2", False),
            ("bus/i2c/devices/1-0040/hwmon/hwmon3", False),
            ("devices/platform/bus@0/3160000.i2c/i2c-1/1-0040/hwmon/hwmon4", False),
            ("bus/i2c/drivers/ina3221x/0-0040/iio:device0", True),
        )
        for shape, legacy in shapes:
            with self.subTest(shape=shape), tempfile.TemporaryDirectory() as tmp:
                self.make_device(Path(tmp), shape, legacy)
                sampler = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=1_000_000)
                self.assertIsInstance(sampler, PowerSampler)
                sampler.start()
                trace, = sampler.stop()
                self.assertTrue(trace.values)
                # 5000 mV * 2000 mA / 1e6 = 10 W; no uncertainty, 1e-6 relative.
                self.assertAlmostEqual(trace.values[0], 10, delta=10 * 1e-6)
                self.assertEqual(sampler.update_intervals_ms.popitem()[1], 1)
                self.assertIn("VDD_IN", trace.channel)

    def test_alias_not_double_counted_missing_rail_and_midrun_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            device = self.make_device(root, "bus/i2c/devices/1-0040/hwmon/hwmon3")
            alias = root / "bus/i2c/drivers/ina3221/1-0040/hwmon/hwmon3"
            alias.parent.mkdir(parents=True)
            alias.symlink_to(device, target_is_directory=True)
            (device / "in2_label").write_text("VDD_CPU")
            (device / "in2_input").write_text("1000")
            sampler = Ina3221Sampler(sysfs_root=root, sample_interval_ns=1_000_000)
            self.assertEqual(len(sampler.discover()), 2)
            sampler.sample_once()
            (device / "curr1_input").unlink()
            sampler.sample_once()
            (device / "curr1_input").write_text("3000")
            sampler.sample_once()
            traces = sampler.stop()
            good = next(t for t in traces if "VDD_IN" in t.channel)
            missing = next(t for t in traces if "VDD_CPU" in t.channel)
            self.assertEqual(len(good.values), 2)  # Read failure is a gap, never fabricated zero.
            self.assertEqual(len(missing.values), 0)
            # 5 V * 3 A = 15 W; no uncertainty, 1e-6 relative.
            self.assertAlmostEqual(good.values[-1], 15, delta=15 * 1e-6)
            self.assertTrue(any(f.startswith("rail_read_error") for f in sampler.flags))

    def test_unavailable_and_configuration_refusal_are_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            sampler = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=1_000_000)
            sampler.start()
            trace, = sampler.stop()
            self.assertIn("ina3221_unavailable", trace.notes)
            device = self.make_device(Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
            sampler = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=1_000_000,
                                     update_interval_ms=2)
            with patch.object(Path, "write_text", side_effect=PermissionError):
                sampler.discover()
            self.assertTrue(any("update_interval_refused" in f for f in sampler.flags))
            self.assertEqual((device / "update_interval").read_text(), "1")

    def test_characterization_driver_changes_every_k_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.make_device(Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
            now, count = [0], [0]

            def clock():
                now[0] += 1000  # Each sysfs read pair takes one simulated microsecond.
                return now[0]

            def read(path):
                if path.name == "curr1_input":
                    value = 2000 + (count[0] // 4) * 10
                    count[0] += 1
                    return str(value)
                return path.read_text().strip()

            def sleep(seconds):
                now[0] += round(seconds * 1_000_000_000)

            sampler = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=1_000_000,
                                     clock=clock, read_text=read)
            result = sampler.characterize(reads=40, sleep=sleep)
            rail, = result.rails
            # Four polls per driver update: 4 * (1 ms wait + 2 us clock advance).
            self.assertEqual(rail.distinct_periods_ns, (4_008_000,) * 8)
            self.assertEqual(rail.read_latency_ns, (1000,) * 40)
            # 5 V * 10 mA step = 0.05 W; 1e-6 relative without stated uncertainty.
            self.assertAlmostEqual(rail.quantum_w, 0.05, delta=0.05 * 1e-6)

    def test_interval_restored_and_flat_readings_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            device = self.make_device(Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
            sampler = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=1_000_000,
                                     update_interval_ms=2)
            result = sampler.characterize(reads=4, sleep=lambda _: None)
            self.assertEqual(dict(result.update_intervals_ms)[str(device)], 2)
            self.assertEqual((device / "update_interval").read_text(), "1")
            self.assertIn("insufficient_distinct_changes", result.rails[0].flags)
            self.assertIsNone(result.rails[0].quantum_w)


if __name__ == "__main__":
    unittest.main()
