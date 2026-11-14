"""RL-145 section 3 / addendum row 3: the session confirms the alias pair.

Repository files only: the saved Part B D classification (alias group
['TV0h', 'TV1h']) stands in for a D step's; no host or study data.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from joulewise.align.apple import r1_runtime as rt

ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT / 'docs/run_reports/2026-11-12-rl122/smoke_part_b.rl122.json'
CONFIG = ROOT / 'configs/align/v4/r1_runtime.json'


class NightConfirmationTests(unittest.TestCase):
    def setUp(self):
        self.config, _ = rt.load_config(CONFIG)
        self.keys, self.classes = self.config['r0_classified_keys'], self.config['r0_classes']
        self.c = json.loads(TABLE.read_bytes())['classification_table']['classification']

    def confirm(self, c, fast='TV0h', slow='TV1h'):
        return rt.night_confirmation(c, {'s_fast': fast, 's_slow': slow}, self.keys, self.classes)

    def row(self, c, key):
        return next(r for r in c['ranking'] if r['key'] == key)

    def test_the_configured_pair_is_the_alias_group_and_is_ok(self):
        self.assertEqual((self.config['sensors']['s_fast'], self.config['sensors']['s_slow']), ('TV0h', 'TV1h'))
        self.assertIn(['TV0h', 'TV1h'], self.c['alias_groups'])
        result = self.confirm(self.c)
        self.assertEqual((result['ok'], result['reasons']), (True, []))
        self.assertEqual((result['authority'], result['second_key_rule'], result['second_key_basis']),
                         ('RL-78', 'RL-145', 'alias_group_of_fast_key'))
        self.assertEqual((result['s_fast'], result['s_slow']), ('TV0h', 'TV1h'))
        # Today's RL-78 test still refuses the same pair (Part B and selection are unchanged).
        self.assertFalse(rt.sensor_admissibility(self.c, {'s_fast': 'TV0h', 's_slow': 'TV1h'}, self.keys)['ok'])

    def test_fast_key_inadmissible_refuses(self):
        for field, value in (('clamped', True), ('noise', 0.5), ('resolving', False), ('t_band_s', 400.0)):
            c = deepcopy(self.c)
            self.row(c, 'TV0h')[field] = value
            with self.subTest(field=field):
                result = self.confirm(c)
                self.assertFalse(result['ok'])
                self.assertTrue(any(r.startswith('s_fast: TV0h') for r in result['reasons']), result)

    def test_alias_second_key_is_one_thermometer_and_is_not_tested_separately(self):
        c = deepcopy(self.c)
        self.row(c, 'TV1h')['clamped'] = True
        self.assertTrue(self.confirm(c)['ok'])

    def test_group_formed_but_second_key_outside_it_refuses(self):
        for slow in ('TVh0', 'Tf48'):
            result = self.confirm(self.c, slow=slow)
            self.assertFalse(result['ok'], slow)
            self.assertTrue(any('alias group' in r for r in result['reasons']), result)

    def test_group_not_formed_needs_an_admissible_die_key(self):
        c = deepcopy(self.c)
        c['alias_groups'] = [g for g in c['alias_groups'] if 'TV0h' not in g]
        ok = self.confirm(c, slow='TVh0')
        self.assertEqual((ok['ok'], ok['second_key_basis']), (True, 'admissible_die_key'), ok)
        # Not a die key.
        self.assertFalse(self.confirm(c, slow='Th0C')['ok'])
        self.assertTrue(any('R0 die key' in r for r in self.confirm(c, slow='Th0C')['reasons']))
        # A die key that fails the quality clauses.
        bad = deepcopy(c)
        self.row(bad, 'TVh0')['clamped'] = True
        self.assertFalse(self.confirm(bad, slow='TVh0')['ok'])
        # TV1h itself is just another key when no group formed: identical rows still pass as a die key.
        self.assertTrue(self.confirm(c, slow='TV1h')['ok'])

    def test_same_key_twice_and_a_classification_reason_refuse(self):
        self.assertFalse(self.confirm(self.c, slow='TV0h')['ok'])
        c = deepcopy(self.c)
        c['reason'] = 'quiet_not_observed'
        result = self.confirm(c)
        self.assertEqual((result['ok'], result['reasons']), (False, ['quiet_not_observed']))


if __name__ == '__main__':
    unittest.main()
