"""WP14(a) synthetic regression tests for the single v4 classifier."""
import math
import random
import unittest
from unittest import mock

from joulewise.align.apple import thermal
from joulewise.align.apple.smc_enumeration import rank, select_keys
from tests.align.test_smc_selection import capture


def jittered_capture():
    """Synthetic full-length R0 step; values follow the actual read starts."""
    rng = random.Random(195)
    phases = [("idle", 0, 300), ("load", 300, 1200), ("recovery", 1200, 1800)]
    # Heating/cooling constants in seconds, rise in degC: die t63 ~3 s;
    # heatsink full-rise t63 ~50 s and cooling tau ~120 s, with 8 >= 4 degC.
    specs = {"TDIE": (3, 3, 18), "THEA": (50, 120, 8)}
    samples = []
    for phase, begin, end in phases:
        for tick in range(begin, end):
            # Inclusive measured-shape bounds: 0-150 ms late, 50-400 ms read.
            started = tick * thermal.NS + rng.randint(0, 150_000_000)
            finished = started + rng.randint(50_000_000, 400_000_000)
            t = started / thermal.NS
            values = {}
            for key, (heat, cool, rise) in specs.items():
                response = (0 if phase == "idle" else
                            1 - math.exp(-(t - begin) / heat) if phase == "load" else
                            (1 - math.exp(-900 / heat)) * math.exp(-(t - begin) / cool))
                # Non-stale idle noise stays small relative to both rises.
                values[key] = 30 + rise * response + .1 * math.sin(t * 1.7)
            samples.append({"phase": phase, "elapsed_s": t,
                            "started": {"monotonic_ns": started},
                            "finished": {"monotonic_ns": finished},
                            "values": {"sensors": values, "errors": {}}})
    return {"started": {"monotonic_ns": 0}, "finished": {"monotonic_ns": 1800 * thermal.NS},
            "inventory": {"keys": [{"key": key, "unit": "degC", "data_type": "flt "}
                                     for key in specs]},
            "phases": [{"phase": phase, "start_s": begin, "end_s": end}
                       for phase, begin, end in phases], "samples": samples}


class SmcClassifierV4Tests(unittest.TestCase):
    def test_production_jitter_resolves_both_picks_only_with_cell_tolerance(self):
        data = jittered_capture()
        coverage_type = thermal.Coverage

        def narrow_coverage(*args, **kwargs):
            kwargs["tolerance_ns"] = thermal.NS // 10
            return coverage_type(*args, **kwargs)

        for stage in ("r0", "r1"):
            with self.subTest(stage=stage):
                # Force the previous one-tenth-period window through real rank.
                with mock.patch.object(thermal, "Coverage", side_effect=narrow_coverage):
                    before = rank(data, stage=stage)
                for sensor in before["ranking"]:
                    for fraction in sensor["phase_coverage"].values():
                        # The unchanged quality bar requires 99% occupied cells.
                        self.assertLess(fraction, .99)
                self.assertEqual(before["selection"], {"s_fast": None, "s_slow": None})
                self.assertEqual(before["status"], "inconclusive")

                after = rank(data, stage=stage)
                for sensor in after["ranking"]:
                    for fraction in sensor["phase_coverage"].values():
                        # Every tick is present; jitter must clear the same 99% bar.
                        self.assertGreaterEqual(fraction, .99)
                self.assertEqual(after["selection"], {"s_fast": "TDIE", "s_slow": "THEA"})
                self.assertEqual(after["status"], "pass")
                sensors = {row["key"]: row for row in after["ranking"]}
                self.assertEqual(sensors["TDIE"]["class"], "die")
                self.assertEqual(sensors["THEA"]["class"], "heatsink")
                # A 3 s exponential reaches 63.2% at ~3 s; allow one sample period.
                self.assertAlmostEqual(sensors["TDIE"]["t63_s"], 3, delta=1)
                # Full-rise t63 is ~50 s. One period plus noise/slope
                # (0.1 / (8 / (50*e)) ~= 1.7 s) fits within three seconds.
                self.assertAlmostEqual(sensors["THEA"]["t63_end_s"], 50, delta=3)
                # Cooling tau is 120 s; one period plus noise/slope
                # (0.1 / (8 / (120*e)) ~= 4.1 s) fits within six seconds.
                self.assertAlmostEqual(sensors["THEA"]["tau_s"], 120, delta=6)
                # The synthetic 8 degC rise exceeds the brief's 4 degC floor.
                self.assertGreaterEqual(sensors["THEA"]["observed_rise"], 4)

    def test_two_percent_missing_load_cells_still_refuse_selection(self):
        data = jittered_capture()
        # Remove every 50th load tick: 900 / 50 = 18 missing of 900 (2%).
        # Interior removals leave the phase's first-reading grid unchanged.
        data["samples"] = [row for row in data["samples"]
                           if row["phase"] != "load" or int(row["elapsed_s"]) % 50 != 25]
        result = rank(data)
        for sensor in result["ranking"]:
            # 882 occupied / 900 expected cells = 98%, below the 99% bar.
            self.assertAlmostEqual(sensor["phase_coverage"]["load"], 882 / 900)
            self.assertLess(sensor["phase_coverage"]["load"], .99)
            self.assertEqual(sensor["class"], "record-only")
            self.assertIn("insufficient phase coverage", sensor["reason"])
        self.assertEqual(result["selection"], {"s_fast": None, "s_slow": None})
        self.assertEqual(result["status"], "inconclusive")

    def test_two_pole_die_uses_sixty_second_rise(self):
        data = capture({'TDIE': (1.5, 200, 40, .1)})
        for row in data['samples']:
            if row['phase'] == 'load':
                t = row['elapsed_s'] - 300
                row['values']['sensors']['TDIE'] = 30 + 20*(1-math.exp(-t/1.5)) + 20*(1-math.exp(-t/200))
        result = rank(data, stage='r1')
        sensor = result['ranking'][0]
        self.assertEqual(sensor['class'], 'die')
        self.assertLessEqual(sensor['t63_s'], 5)
        self.assertGreater(sensor['t63_end_s'], 5)

    def test_heatsink_longest_cooling_wins_and_null_never_falls_back(self):
        result = rank(capture({'TDIE': (2, 2, 18, .1), 'TH90': (60, 90, 8, .1),
                               'T250': (60, 250, 8, .1), 'T600': (60, 600, 8, .1)}), stage='r1')
        self.assertEqual(result['s_slow'], 'T250')
        self.assertEqual(next(r for r in result['ranking'] if r['key'] == 'T600')['class'], 'record-only')
        only_die = rank(capture({'TDIE': (2, 2, 18, .1)}), stage='r0')
        self.assertIsNone(only_die['s_slow'])
        self.assertEqual(only_die['status'], 'inconclusive')

    def test_classes_are_disjoint_property(self):
        random.seed(14)
        for _ in range(200):
            t63 = random.uniform(.1, 20)
            tau = random.uniform(1, 500)
            cls = 'die' if t63 <= 5 and tau <= 300 else 'heatsink' if t63 > 5 and 30 < tau <= 300 else 'record-only'
            rows = [{'key': 'TKEY', 'class': cls, 'observed_rise': 10, 'tau_s': tau}]
            picks = select_keys(rows)
            self.assertFalse(picks['s_fast'] and picks['s_slow'])

    def test_non_temperature_and_one_percent_errors_are_record_only(self):
        data = capture({'F0Ac': (2, 2, 18, .1), 'TDIE': (2, 2, 18, .1)})
        data['inventory']['keys'][0]['unit'] = 'rpm'
        for row in data['samples'][300:306]:
            row['values']['errors']['TDIE'] = 'failed'
        result = rank(data, stage='r1')
        self.assertIsNone(result['s_fast'])


if __name__ == '__main__':
    unittest.main()
