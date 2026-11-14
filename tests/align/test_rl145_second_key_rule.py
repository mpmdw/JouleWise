"""RL-145 section 3 / addendum row 4: the second key by the alias-group rule.

Repository files only (the RL-122 Part B table, the regenerated RL-145 table, the
ruling file and the runtime config); no host, journal or study data.
"""
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.align.apple import r1_runtime as rt
from scripts import align_r1_followup_kit as kit

ROOT = Path(__file__).resolve().parents[2]
SAVED = ROOT / 'docs/run_reports/2026-11-12-rl122/smoke_part_b.rl122.json'
REGENERATED = ROOT / 'docs/run_reports/2026-11-13-rl145/smoke_part_b.rl145.json'
RULING = ROOT / 'docs/run_reports/2026-11-13-rl145/sensor_ruling_rl145.json'
CONFIG = ROOT / 'configs/align/v4/r1_runtime.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class AliasSecondKeyRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved_raw, cls.regen_raw = SAVED.read_bytes(), REGENERATED.read_bytes()
        cls.saved, cls.regen = json.loads(cls.saved_raw), json.loads(cls.regen_raw)
        cls.ruling = json.loads(RULING.read_bytes())
        cls.config, _ = rt.load_config(CONFIG)

    def validate(self, config=None, ruling=None, table=None, authorize=True):
        table = self.regen if table is None else table
        ruling = deepcopy(self.ruling if ruling is None else ruling)
        if authorize:
            ruling['authorizes_night'] = True      # the committed file carries the pair only
        ruling['smoke_part_b_sha256'] = sha(kit.table_bytes(table))
        return kit.validate_sensor_ruling(config or self.config, ruling, ruling['smoke_part_b_sha256'], table)

    def test_inputs_are_the_ruled_ones(self):
        self.assertEqual(sha(self.saved_raw), kit.ALIAS_SECOND_KEY_SOURCE_TABLE_SHA256)
        self.assertEqual(sha(self.regen_raw), kit.ALIAS_SECOND_KEY_TABLE_SHA256)
        self.assertEqual(self.ruling['source_smoke_part_b_sha256'], sha(self.saved_raw))
        self.assertEqual(self.ruling['smoke_part_b_sha256'], sha(self.regen_raw))
        self.assertEqual(self.ruling['sensors'], self.config['sensors'])
        self.assertEqual((self.ruling['research_lead_ruling'], self.ruling['slow_rule']),
                         (kit.ALIAS_SECOND_KEY_RULING, kit.ALIAS_SECOND_KEY_RULE))
        self.assertEqual(self.ruling['classification_sha256'], kit.SECOND_FAST_RULE_CLASSIFICATION_SHA256)
        self.assertIs(self.ruling['authorizes_night'], False)   # no night is authorized by this file

    def test_rule_picks_the_lexically_first_other_alias(self):
        pick = kit.alias_second_key_selection(self.saved, self.config)
        self.assertTrue(pick['ok'], pick)
        self.assertEqual((pick['s_fast'], pick['s_slow']), ('TV0h', 'TV1h'))
        self.assertEqual(pick['candidates'], ['TV1h'])
        self.assertEqual(pick['second_key_basis'], 'alias_group_of_fast_key')
        self.assertEqual(self.config['sensors']['s_slow'], pick['s_slow'])
        self.assertEqual(self.validate()['s_slow'], 'TV1h')

    def test_lexical_first_among_several_aliases(self):
        table = deepcopy(self.saved)
        c = table['classification_table']['classification']
        group = next(g for g in c['alias_groups'] if 'TV0h' in g)
        group[:] = ['TV0h', 'TV1h', 'TVz9']
        c['ranking'].append({**next(r for r in c['ranking'] if r['key'] == 'TV1h'), 'key': 'TVz9'})
        self.assertEqual(kit.alias_second_key_selection(table, self.config)['s_slow'], 'TV1h')
        group[:] = ['TV0h', 'TV0a', 'TV1h']
        self.assertEqual(kit.alias_second_key_selection(table, self.config)['s_slow'], 'TV0a')

    def test_no_alias_group_gives_no_pair(self):
        table = deepcopy(self.saved)
        c = table['classification_table']['classification']
        c['alias_groups'] = [g for g in c['alias_groups'] if 'TV0h' not in g]
        pick = kit.alias_second_key_selection(table, self.config)
        self.assertFalse(pick['ok'])
        self.assertIsNone(pick['s_slow'])
        with self.assertRaises(ValueError):
            kit.regenerate_alias_second_key_table(kit.table_bytes(table), self.config)

    def test_inadmissible_fast_key_gives_no_pair(self):
        table = deepcopy(self.saved)
        # The chooser would move to the alias if only TV0h were clamped; with the whole group clamped
        # the fast pick leaves the group and there is no pair.
        for row in table['classification_table']['classification']['ranking']:
            if row['key'] in ('TV0h', 'TV1h'):
                row['clamped'] = True
        self.assertFalse(kit.alias_second_key_selection(table, self.config)['ok'])

    def test_the_committed_ruling_is_not_an_authorization(self):
        with self.assertRaisesRegex(ValueError, "research lead's ruling"):
            self.validate(authorize=False)

    def test_a_hand_pick_of_any_other_key_is_refused(self):
        others = [k for k in self.config['r0_classified_keys'] + ['TVH3', 'Tsyn'] if k not in ('TV1h', 'TV0h')]
        for key in others:
            with self.subTest(key=key):
                config, ruling, table = deepcopy(self.config), deepcopy(self.ruling), deepcopy(self.regen)
                for record in (config['sensors'], ruling['sensors'], table['selection']):
                    record['s_slow'] = key
                with self.assertRaisesRegex(ValueError, 'RL-145'):
                    self.validate(config, ruling, table)

    def test_other_rules_and_rulings_are_refused(self):
        for mutate, message in (
                (lambda r: r.update(slow_rule='longest_return_time'), 'slow rule'),
                (lambda r: r.update(research_lead_ruling='RL-122'), 'slow rule'),
                (lambda r: r.update(classification_sha256='0' * 64), 'slow rule'),
                (lambda r: r.pop('slow_rule'), 'RL-116')):
            ruling = deepcopy(self.ruling)
            mutate(ruling)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.validate(ruling=ruling)
        # RL-122's ruling and table (TVh0) no longer fit the policy.
        rl122 = json.loads((SAVED.parent / 'sensor_ruling_rl122.json').read_bytes())
        with self.assertRaises(ValueError):
            kit.validate_sensor_ruling(self.config, rl122, sha(self.saved_raw), self.saved)
        # The RL-122 table's bytes are not the RL-145 table's.
        ruling = deepcopy(self.ruling)
        ruling.update(authorizes_night=True, smoke_part_b_sha256=sha(self.saved_raw))
        with self.assertRaisesRegex(ValueError, 'regenerated table'):
            kit.validate_sensor_ruling(self.config, ruling, sha(self.saved_raw), self.saved)

    def test_rl78_and_rl84_bars_still_apply(self):
        config = deepcopy(self.config)
        config['slow_band_floor_c'] = 1.5
        with self.assertRaisesRegex(ValueError, 'default'):
            self.validate(config)
        config = deepcopy(self.config)
        config['sensors']['record_keys'] = []
        ruling = deepcopy(self.ruling)
        ruling['sensors'] = config['sensors']
        with self.assertRaisesRegex(ValueError, 'Tf08'):
            self.validate(config, ruling)
        table = deepcopy(self.regen)
        table['selection']['fallback'] = True
        with self.assertRaisesRegex(ValueError, 'regenerated table'):
            self.validate(table=table)

    def test_table_regenerates_byte_stable_from_the_rl122_table(self):
        raw = kit.regenerate_alias_second_key_table(self.saved_raw, self.config)
        self.assertEqual(raw, self.regen_raw)
        self.assertEqual(kit.regenerate_alias_second_key_table(self.saved_raw, self.config), raw)
        changed = [line for line in zip(self.saved_raw.splitlines(), raw.splitlines()) if line[0] != line[1]]
        self.assertEqual(changed, [(b'    "s_slow": "TVh0",', b'    "s_slow": "TV1h",')])
        self.assertEqual(len(self.saved_raw.splitlines()), len(raw.splitlines()))
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'table.json'
            printed = io.StringIO()
            with redirect_stdout(printed):
                self.assertEqual(kit.main(['regenerate-table', '--rule', 'rl145', '--saved-table', str(SAVED),
                                           '--output', str(out)]), 0)
            self.assertEqual(printed.getvalue().strip(), sha(self.regen_raw))
            self.assertEqual(out.read_bytes(), self.regen_raw)

    def test_identities_refuse_any_other_change(self):
        kit.alias_second_key_table_identities(self.saved, self.regen, self.config)
        for mutate, identity in (
                (lambda t: t['classification_table']['classification'].update(classification_sha256='0' * 64), '1'),
                (lambda t: t['coverage'].update(pass_note=1), '2'),
                (lambda t: t['selection'].update(s_slow='Tf48'), '3'),
                (lambda t: t.update(status='SELECTION_FAILED'), '4'),
                (lambda t: t['selection'].update(authority='RL-145'), '4')):
            table = deepcopy(self.regen)
            mutate(table)
            with self.subTest(identity=identity), self.assertRaisesRegex(ValueError, identity + ':'):
                kit.alias_second_key_table_identities(self.saved, table, self.config)


if __name__ == '__main__':
    unittest.main()
