"""WP14(a) synthetic regression tests for the single v4 classifier."""
import math
import random
import unittest

from joulewise.align.apple.smc_enumeration import rank, select_keys
from tests.align.test_smc_selection import capture


class SmcClassifierV4Tests(unittest.TestCase):
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
