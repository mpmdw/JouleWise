"""Review regressions for cadence quantization and physical power resolution."""

import itertools
import json
import tempfile
import unittest
from pathlib import Path

from joulewise.align.power.ina3221 import Characterization, Ina3221Sampler, RailCharacterization
from tests.align import test_power_ina3221 as fixtures


class CharacterizationReviewTest(unittest.TestCase):
    def test_real_sysfs_path_through_detector_with_held_conversions(self):
        from joulewise.align.phase_detect import detect_phases, match_tool_calls
        from joulewise.align.sensor_sim import timeline_from_episode
        from tests.align.test_sensor_sim import model, world
        episode = world(5, 250_000_000)
        timeline = timeline_from_episode(episode, model())
        conversion = 4_000_000  # Scenario conversion every four 1 ms polls.
        with tempfile.TemporaryDirectory() as tmp:
            dev = fixtures.Ina3221Test().make_device(
                Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
            (dev / "samples").write_text("1")
            now = [episode.start_ns]
            def read(path):
                if path.name == "curr1_input":
                    timestamp = (now[0] // conversion) * conversion
                    watts = (timeline.integral(timestamp - conversion, timestamp) / conversion
                             if timestamp > conversion else timeline.power_at(now[0]))
                    return str(round(watts / 5.0 * 1000))  # Integer mA on a 5 V rail.
                return path.read_text().strip()
            sampler = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=1_000_000,
                                     clock=lambda: now[0], read_text=read)
            sampler.discover()
            while now[0] < episode.end_ns:
                now[0] += 1_000_000
                sampler.sample_once()
            trace, = sampler.stop()
            self.assertGreaterEqual(trace.averaging_window_ns, conversion)
            self.assertIsNotNone(trace.resolution)
            self.assertIn("driver_characterized_cadence_disagreement", trace.notes)
            for sd in (None, .005):
                with self.subTest(noise_sd_w=sd):
                    match = match_tool_calls(detect_phases(trace, noise_sd_w=sd), episode)
                    self.assertEqual(match.matched_count, 3)
                    self.assertEqual(len(match.unlogged_candidates), 0)
                    # Poll plus actual conversion is the minimum timing bound.
                    self.assertGreaterEqual(match.tolerance_ns, 1_000_000 + conversion)

    def test_mainline_shunt_sum_is_not_a_bus_rail(self):
        with tempfile.TemporaryDirectory() as tmp:
            dev = fixtures.Ina3221Test().make_device(Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
            (dev / "in7_label").write_text("sum of shunt voltages")
            (dev / "in7_input").write_text("32")
            sampler = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=1_000_000)
            self.assertEqual(len(sampler.discover()), 1)  # Exactly one physical V/I pair.
            self.assertTrue(any(f.startswith("summation_channel_skipped") for f in sampler.flags))
            self.assertFalse(any(f.startswith("missing_rail_attribute") for f in sampler.flags))

    def test_cadence_uses_endpoint_span_and_flags_poll_limit(self):
        for poll in (100_000, 300_000, 500_000, 1_000_000):
            with self.subTest(poll=poll), tempfile.TemporaryDirectory() as tmp:
                fixtures.Ina3221Test().make_device(Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
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
                    # Slower-than-poll conversions remain resolved even
                    # when their period is below twice the poll interval.
                    self.assertNotIn("cadence_poll_limited", rail.flags)
                else:
                    self.assertIn("cadence_poll_limited", rail.flags)

    def test_watt_resolution_propagates_both_lattices(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixtures.Ina3221Test().make_device(Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
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

    def test_driver_metadata_and_characterization_disagreement(self):
        with tempfile.TemporaryDirectory() as tmp:
            dev = fixtures.Ina3221Test().make_device(Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
            (dev / "samples").write_text("4")
            sampler = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=1_000_000)
            rail, = sampler.discover()
            sampler.characterization = Characterization((
                RailCharacterization(rail.channel, (), (4_000_000, 4_000_000),
                                     0.04, 8.0, 8.0),), (), ())
            sampler.sample_once()
            trace, = sampler.stop()
            # Driver reports 1 ms; measured conversion/averaging takes 4 ms.
            self.assertEqual(trace.averaging_window_ns, 4_000_000)
            self.assertAlmostEqual(trace.resolution, 0.04, delta=0.04 * 1e-6)
            self.assertIn("driver_characterized_cadence_disagreement", trace.notes)
            self.assertEqual(json.loads(trace.notes)["samples"][str(dev)], 4)

    def test_alarm_clear_set_missing_and_separate_throttle_counter(self):
        for value in (None, "0", "1"):
            with self.subTest(alarm=value), tempfile.TemporaryDirectory() as tmp:
                dev = fixtures.Ina3221Test().make_device(Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
                if value is not None:
                    (dev / "curr1_crit_alarm").write_text(value)
                    (dev / "curr1_max_alarm").write_text("0")
                    (dev / "in1_warning").write_text("0")
                # NVIDIA documents OC counters in class/hwmon, including a
                # separate soctherm hwmon. No INA name is required there.
                thermal = Path(tmp) / "class/hwmon/hwmon8"
                thermal.mkdir(parents=True)
                counter = thermal / "oc3_event_cnt"
                counter.write_text("7")
                sampler = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=1_000_000)
                sampler.start()
                counter.write_text("9")
                trace, = sampler.stop()
                notes = json.loads(trace.notes)
                key = "class/hwmon/hwmon8/oc3_event_cnt"
                self.assertEqual(notes["health_start"][key], 7)
                self.assertEqual(notes["health_stop"][key], 9)
                self.assertEqual(notes["oc_event_count_deltas"][key], 2)
                self.assertTrue(any(f.startswith("overcurrent_throttle_events") for f in notes["flags"]))
                alarm_set = any(f.startswith("hardware_alarm_set") for f in notes["flags"])
                self.assertEqual(alarm_set, value == "1")
                if value is None:
                    self.assertIn("alarm_attributes_unavailable", notes["flags"])

    def test_health_attribute_read_loss_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            dev = fixtures.Ina3221Test().make_device(Path(tmp), "bus/i2c/devices/1-0040/hwmon/hwmon1")
            alarm = dev / "curr1_max_alarm"
            alarm.write_text("0")
            sampler = Ina3221Sampler(sysfs_root=tmp, sample_interval_ns=1_000_000)
            sampler.start()
            alarm.unlink()
            trace, = sampler.stop()
            self.assertIn("health_read_error", trace.notes)
            key = str(alarm.relative_to(Path(tmp)))
            self.assertIsNone(json.loads(trace.notes)["health_stop"][key])


if __name__ == "__main__":
    unittest.main()
