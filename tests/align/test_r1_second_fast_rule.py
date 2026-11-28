"""RL-119 step 2 / RL-122 item 7: the second gate key by the fast rule applied a second time.

Repository files only (the saved Part B table, the regenerated table, the
ruling file and the runtime config); no host, journal or study data.
"""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.align.apple import r1_runtime as rt
from scripts import align_r1_followup_kit as kit

ROOT = Path(__file__).resolve().parents[2]
SAVED = ROOT / 'docs/run_reports/2026-11-12-rl89/smoke_part_b.rl89.json'
REGENERATED = ROOT / 'docs/run_reports/2026-11-12-rl122/smoke_part_b.rl122.json'
RULING = ROOT / 'docs/run_reports/2026-11-12-rl122/sensor_ruling_rl122.json'
CONFIG = ROOT / 'configs/align/v4/r1_runtime.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class SecondFastRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved_raw, cls.regen_raw = SAVED.read_bytes(), REGENERATED.read_bytes()
        cls.saved, cls.regen = json.loads(cls.saved_raw), json.loads(cls.regen_raw)
        cls.ruling = json.loads(RULING.read_bytes())
        cls.config, _ = rt.load_config(CONFIG)
        # RL-145 moved the config's s_slow TVh0 -> TV1h. This file tests RL-122's rule (still in the
        # validator, superseded), so it reads the config as RL-122 had it: only s_slow differs.
        cls.config = deepcopy(cls.config)
        cls.config['sensors']['s_slow'] = 'TVh0'

    def validate(self, config=None, ruling=None, table=None):
        # A ruling written for a changed table names that table's own digest.
        table = self.regen if table is None else table
        ruling = deepcopy(self.ruling if ruling is None else ruling)
        ruling['smoke_part_b_sha256'] = sha(kit.table_bytes(table))
        return kit.validate_sensor_ruling(config or self.config, ruling, ruling['smoke_part_b_sha256'], table)

    def test_inputs_are_the_ruled_ones(self):
        self.assertEqual(sha(self.saved_raw), '1fdd980c91ceca6ee3907191b499f0108ca84b8709648a638bd49808a298eba3')
        self.assertEqual(self.saved['classification_table']['classification']['classification_sha256'],
                         kit.SECOND_FAST_RULE_CLASSIFICATION_SHA256)
        self.assertEqual(self.ruling['source_smoke_part_b_sha256'], sha(self.saved_raw))
        self.assertEqual(self.ruling['smoke_part_b_sha256'], sha(self.regen_raw))
        self.assertEqual(self.ruling['sensors'], self.config['sensors'])
        self.assertEqual((self.ruling['research_lead_ruling'], self.ruling['slow_rule']),
                         (kit.SECOND_FAST_RULE_RULING, kit.SECOND_FAST_RULE))

    def test_rule_picks_tvh0(self):
        pick = kit.second_fast_rule_selection(self.saved, self.config)
        self.assertTrue(pick['ok'], pick)
        self.assertEqual((pick['s_fast'], pick['s_slow']), ('TV0h', 'TVh0'))
        self.assertEqual(pick['candidates'][0], 'TVh0')
        self.assertNotIn('TV1h', pick['candidates'])  # the fast pick's alias
        self.assertTrue(all(self.config['r0_classes'][k] == 'die' for k in pick['candidates']))
        # TV0h and TVh0 tie on rise; the fast rule's lexical order gave TV0h the fast role.
        rows = {r['key']: r for r in self.saved['classification_table']['classification']['ranking']}
        self.assertEqual(rows['TV0h']['observed_rise'], rows['TVh0']['observed_rise'])
        self.assertEqual(self.config['sensors']['s_slow'], pick['s_slow'])
        # RL-145 close: the validator no longer accepts this rule (see test_rl145_second_key_rule).
        with self.assertRaisesRegex(ValueError, 'RL-145'):
            self.validate()

    def test_a_hand_pick_of_any_other_key_is_refused(self):
        others = [k for k in self.config['r0_classified_keys'] + ['TVH3', 'Tsyn'] if k not in ('TVh0', 'TV0h')]
        for key in others:
            with self.subTest(key=key):
                config, ruling, table = deepcopy(self.config), deepcopy(self.ruling), deepcopy(self.regen)
                for record in (config['sensors'], ruling['sensors'], table['selection']):
                    record['s_slow'] = key
                with self.assertRaisesRegex(ValueError, 'RL-122'):
                    self.validate(config, ruling, table)

    def test_other_rules_and_rulings_are_refused(self):
        for mutate, message in (
                (lambda r: r.update(slow_rule='longest_return_time'), 'slow rule'),
                (lambda r: r.update(research_lead_ruling='RL-89'), 'slow rule'),
                (lambda r: r.update(classification_sha256='0' * 64), 'slow rule'),
                (lambda r: r.pop('slow_rule'), 'RL-116'),
                (lambda r: r.update(authorizes_night=False), "research lead's ruling")):
            ruling = deepcopy(self.ruling)
            mutate(ruling)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.validate(ruling=ruling)
        # The saved RL-89 table (Th0C) and its ruling no longer fit the policy.
        rl89 = json.loads((SAVED.parent / 'sensor_ruling_rl89.json').read_bytes())
        with self.assertRaises(ValueError):
            kit.validate_sensor_ruling(self.config, rl89, sha(self.saved_raw), self.saved)

    def test_only_the_regenerated_table_bytes_are_accepted(self):
        # PR #752 cold review F2: with the declared classification digest left in
        # place, an edited ranking or coverage would move the pick to Tf48.
        self.assertEqual(sha(self.regen_raw), kit.SECOND_FAST_RULE_TABLE_SHA256)
        def noisy(table):
            for row in table['classification_table']['classification']['ranking']:
                if row['key'] == 'TVh0':
                    row['noise'] = 0.2
        def uncovered(table):
            table['coverage']['phases']['load']['TVh0']['pass'] = False
        for mutate, name in ((noisy, 'TVh0 noise raised'), (uncovered, 'TVh0 fails a smoke phase')):
            table = deepcopy(self.regen)
            mutate(table)
            with self.subTest(name):
                self.assertEqual(table['classification_table']['classification']['classification_sha256'],
                                 kit.SECOND_FAST_RULE_CLASSIFICATION_SHA256)
                moved = kit.second_fast_rule_selection(table, self.config)
                self.assertEqual(moved['s_slow'], 'Tf48')
                config, ruling = deepcopy(self.config), deepcopy(self.ruling)
                for record in (config['sensors'], ruling['sensors'], table['selection']):
                    record['s_slow'] = moved['s_slow']
                with self.assertRaisesRegex(ValueError, 'RL-145'):     # refused outright, not by the table bytes
                    self.validate(config, ruling, table)

    def test_table_regenerates_byte_stable(self):
        raw = kit.regenerate_second_fast_rule_table(self.saved_raw, self.config)
        self.assertEqual(raw, self.regen_raw)
        self.assertEqual(kit.regenerate_second_fast_rule_table(self.saved_raw, self.config), raw)
        self.assertEqual(kit.table_bytes(self.regen), self.regen_raw)
        changed = [line for line in zip(self.saved_raw.splitlines(), raw.splitlines()) if line[0] != line[1]]
        self.assertEqual(changed, [(b'    "s_slow": "Th0C",', b'    "s_slow": "TVh0",')])
        self.assertEqual(len(self.saved_raw.splitlines()), len(raw.splitlines()))
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'table.json'
            printed = io.StringIO()
            with redirect_stdout(printed):
                self.assertEqual(kit.main(['regenerate-table', '--saved-table', str(SAVED), '--output', str(out)]), 0)
            self.assertEqual(printed.getvalue().strip(), sha(self.regen_raw))
            self.assertEqual(out.read_bytes(), self.regen_raw)

    def test_identities_refuse_any_other_change(self):
        kit.second_fast_rule_table_identities(self.saved, self.regen, self.config)
        for mutate, identity in (
                (lambda t: t['classification_table']['classification'].update(classification_sha256='0' * 64), '1'),
                (lambda t: t['coverage'].update(pass_note=1), '2'),
                (lambda t: t['selection'].update(s_slow='Tf48'), '3'),
                (lambda t: t.update(status='SELECTION_FAILED'), '4'),
                (lambda t: t['selection'].update(authority='RL-122'), '4')):
            table = deepcopy(self.regen)
            mutate(table)
            with self.subTest(identity=identity), self.assertRaisesRegex(ValueError, identity + ':'):
                kit.second_fast_rule_table_identities(self.saved, table, self.config)
        with self.assertRaisesRegex(ValueError, 'serialization'):
            kit.regenerate_second_fast_rule_table(self.saved_raw.rstrip(b'\n'), self.config)


if __name__ == '__main__':
    unittest.main()
