"""RL-89: the runtime config's R0-classified keys are R0's record, re-derived.

The fixture is the (key, class, eligible) projection of R0's ranking, written
by ``scripts/align_r1_r0_classes_from_r0.py project`` from ``smc/r0.json``
(sha256 pinned). Set JOULEWISE_R0_JSON to a saved copy of that record to also
re-derive from the record itself. Sensor metadata only; no study outcome.
"""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from scripts import align_r1_r0_classes_from_r0 as derive_r0

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'configs/align/v4/r1_runtime.json'
FIXTURE = ROOT / 'tests/align/fixtures/r0_v4_20261108T0550Z_ranking_classes.json'


class R0ClassesTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(CONFIG.read_bytes())
        self.fixture = json.loads(FIXTURE.read_bytes())

    def test_fixture_is_the_pinned_record(self):
        self.assertEqual(self.fixture['schema'], derive_r0.PROJECTION_SCHEMA)
        self.assertEqual(self.fixture['source_sha256'], derive_r0.R0_SHA256)
        self.assertEqual(self.config['sensors']['r0_sha256'], derive_r0.R0_SHA256)
        self.assertEqual(len(self.fixture['ranking']), 403)

    def test_config_equals_derivation(self):
        keys, classes = derive_r0.derive(self.fixture['ranking'])
        self.assertEqual(self.config['r0_classified_keys'], keys)
        self.assertEqual(self.config['r0_classes'], classes)
        self.assertEqual(len(keys), 60)
        self.assertEqual(sorted(classes.values()).count('die'), 16)
        self.assertEqual(sorted(classes.values()).count('heatsink'), 44)
        self.assertEqual(derive_r0.main(['check-fixture', '--fixture', str(FIXTURE), '--config', str(CONFIG)]), 0)

    def test_rl122_pair_and_record_key(self):
        # RL-119/RL-122: s_slow is the fast rule applied a second time (TVh0, R0 die),
        # rebinding RL-89's Th0C; Th0C stays an R0 heatsink key, no longer a gate key.
        sensors = self.config['sensors']
        self.assertEqual((sensors['s_fast'], sensors['s_slow'], sensors['record_keys']), ('TV0h', 'TVh0', ['Tf08']))
        self.assertEqual(self.config['r0_classes']['TV0h'], 'die')
        self.assertEqual(self.config['r0_classes']['TVh0'], 'die')
        self.assertEqual(self.config['r0_classes']['Th0C'], 'heatsink')
        self.assertEqual(self.config['r0_classes']['Tf08'], 'heatsink')
        # RL-94 (2): R0's own pair, fixed beside its record digest, for W1's recorded key.
        self.assertEqual(self.config['r0_picks'], {'s_fast': 'TV0h', 's_slow': 'Tf08'})
        self.assertEqual(self.config['slow_band_floor_c'], 1.0)
        self.assertEqual(self.config['g0_timeout_s'], 1200)
        self.assertIn('RL-89', self.config['r0_classes_authority'])
        self.assertIn(derive_r0.R0_SHA256, self.config['r0_classes_authority'])

    def test_rule_excludes_record_only_and_ineligible_and_keeps_order(self):
        rows = [{'key': 'B', 'class': 'heatsink', 'eligible': True},
                {'key': 'A', 'class': 'record-only', 'eligible': False},
                {'key': 'C', 'class': 'die', 'eligible': False},
                {'key': 'D', 'class': 'die', 'eligible': True}]
        self.assertEqual(derive_r0.derive(rows), (['B', 'D'], {'B': 'heatsink', 'D': 'die'}))
        with self.assertRaises(ValueError):
            derive_r0.derive(rows + [rows[0]])

    def test_check_refuses_wrong_record_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'r0.json'
            path.write_text(json.dumps({'response': {'ranking': self.fixture['ranking']}}))
            with self.assertRaises(SystemExit) as raised:
                derive_r0.main(['check', '--r0', str(path), '--config', str(CONFIG)])
            self.assertIn('REFUSED', str(raised.exception))

    def test_write_touches_only_the_two_lines(self):
        keys, classes = derive_r0.derive(self.fixture['ranking'])
        stale = CONFIG.read_text()
        stale = stale.replace(json.dumps(keys), json.dumps(keys[:6]), 1)
        new = derive_r0.rewrite(stale, keys, classes)
        self.assertEqual(new, CONFIG.read_text())

    @unittest.skipUnless(os.environ.get('JOULEWISE_R0_JSON'), 'saved smc/r0.json not supplied')
    def test_fixture_equals_saved_record(self):
        raw = Path(os.environ['JOULEWISE_R0_JSON']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), derive_r0.R0_SHA256)
        self.assertEqual(derive_r0.project(json.loads(raw)), self.fixture['ranking'])


if __name__ == '__main__':
    unittest.main()
