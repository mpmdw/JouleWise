"""A fake meter proves exact hold exclusion and I3 energy/time tiling."""
from dataclasses import asdict, replace
import json
import unittest

from joulewise.align.attribution import attribute_episode
from joulewise.align.energy_residual import turn_energy_from_attribution
from joulewise.align.apple.thermal_desk import member_record
from tests.align.test_attribution import episode, trace, turn, mapping, NS


def gate(kind, a, b, index=0):
    return {'kind': kind, 'turn': index, 'start_ns': a, 'end_ns': b,
            'entry_stamp': {'epoch_ns': a+123*NS, 'monotonic_before_ns': a, 'monotonic_after_ns': a},
            'exit_stamp': {'epoch_ns': b+123*NS, 'monotonic_before_ns': b, 'monotonic_after_ns': b},
            'outcome': 'released', 'release': {'fast_c': 40., 'slow_c': 40.},
            'reference': {'fast_c': 40., 'slow_c': 40.}, 'exit_sample_ns': b}


class HoldAttributionTests(unittest.TestCase):
    def test_constant_fake_meter_excludes_holds_from_turn_and_owned_episode(self):
        ep = episode(turns=(turn(),), hardware={'thermal': {'intervals': [gate('H', 4*NS, 7*NS)]}})
        result = attribute_episode(ep, source='mock', channel='package')
        self.assertEqual(result.total.joules, 1000)  # gross includes all intervals
        self.assertEqual(turn_energy_from_attribution(result)[0][0], 500)  # 800 - 300
        self.assertEqual(sum(s.energy.joules for s in result.segments if s.turn is not None), 500)
        hold = next(s for s in result.segments if s.kind == 'hold')
        self.assertEqual((hold.start_ns, hold.end_ns, hold.turn, hold.energy.joules), (4*NS, 7*NS, None, 300))
        self.assertEqual(sum(s.energy.joules for s in result.segments), result.total.joules)
        for a, b in zip(result.segments, result.segments[1:]):
            self.assertEqual(a.end_ns, b.start_ns)

    def test_fractional_boundaries_mapped_to_meter_without_snapping(self):
        # Linear ramp 10->110 W over 10s; exact trapezoid over a fractional hold.
        ep = episode(turns=(turn(start=0, first=NS, end=10*NS),),
                     power_traces=(trace(times=(123*NS, 133*NS), values=(10., 110.)),),
                     clock_mappings=(mapping(offset=-123*NS),),
                     hardware={'thermal': {'intervals': [gate('H', 2250000000, 6750000000)]}})
        result = attribute_episode(ep, source='mock', channel='package')
        gross = 600
        held = 4.5*(32.5+77.5)/2
        self.assertAlmostEqual(result.total.joules, gross)
        self.assertAlmostEqual(turn_energy_from_attribution(result)[0][0], gross-held)
        hold = next(s for s in result.segments if s.kind == 'hold')
        self.assertEqual(hold.start_ns, 2250000000)

    def test_g1_is_unowned_and_g0_is_before_episode(self):
        ep = episode(turns=(turn(end=3*NS), turn(index=1, start=6*NS, first=7*NS)),
                     hardware={'thermal': {'intervals': [gate('G0', -5*NS, 0), gate('G1', 3*NS, 6*NS, 1)]}})
        result = attribute_episode(ep, source='mock', channel='package')
        self.assertEqual(sum(s.energy.joules for s in result.segments if s.kind == 'gate'), 300)
        self.assertTrue(all(s.turn is None for s in result.segments if s.kind == 'gate'))

    def test_no_hold_reconstruction_and_turn_energies_are_byte_identical(self):
        ep = episode(turns=(turn(),))
        baseline = attribute_episode(ep, source='mock', channel='package')
        empty = attribute_episode(replace(ep, hardware={'thermal': {'intervals': []}}), source='mock', channel='package')
        self.assertEqual(json.dumps(asdict(baseline), sort_keys=True), json.dumps(asdict(empty), sort_keys=True))
        self.assertEqual(json.dumps(turn_energy_from_attribution(baseline), sort_keys=True),
                         json.dumps(turn_energy_from_attribution(empty), sort_keys=True))

    def test_malformed_or_misowned_hold_is_refused(self):
        for intervals in ([gate('H', NS, 3*NS)], [gate('H', 4*NS, 6*NS), gate('H', 5*NS, 7*NS)],
                          [gate('H', 9*NS, 11*NS)], [gate('G1', 4*NS, 6*NS)]):
            with self.subTest(intervals=intervals), self.assertRaises(ValueError):
                attribute_episode(episode(turns=(turn(),), hardware={'thermal': {'intervals': intervals}}),
                                  source='mock', channel='package')

    def test_desk_excludes_invalid_custody_without_aborting(self):
        from tests.align.test_thermal_gate import policy
        ep = episode(turns=(turn(),), hardware={'thermal': {'policy': policy(),
            'intervals': [gate('H', NS, 3*NS)]}})
        record = member_record(ep, [], os_readings=[], pm_samples=[], pm_period_s=1,
                               source='mock', channel='package')
        self.assertIn('thermal.custody_invalid', record['flags'])
        from joulewise.align.apple.thermal_desk import calibration_exclusions
        self.assertIn('thermal.custody_invalid', calibration_exclusions(record))


if __name__ == '__main__':
    unittest.main()
