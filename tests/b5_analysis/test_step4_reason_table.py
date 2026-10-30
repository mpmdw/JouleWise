"""L9-STEP4-2 R1: the registered step-4 reason table is the blind table, regenerated.

step4_reason_classes.json copies the mask and tooling lists of
CLASS_TABLE.json at 08ea5c958. step4_reasons/make_table.py is that commit's
generator, byte for byte; rerunning it over this checkout's extractor modules
must reproduce both lists, so a new extractor code literal cannot fall
outside the registered table without this test failing.
"""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

from joulewise.b5_analysis import steps

ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT / 'configs/analysis/b5/step4_reason_classes.json'
GENERATOR = Path(__file__).resolve().parent / 'step4_reasons/make_table.py'


class Step4ReasonTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = json.loads(TABLE.read_bytes())

    def test_R1_table_shape_is_sorted_disjoint_and_pins_its_source(self):
        table = self.table
        self.assertEqual(set(table), {'schema_version', 'source', 'modules', 'mask_rule', 'mask', 'tooling'})
        self.assertEqual(table['schema_version'], 'joulewise.b5_step4_reason_classes.v1')
        self.assertEqual(table['source']['commit'], '08ea5c95849654c066811273807f9ca6bf5327cf')
        for name in ('mask', 'tooling'):
            self.assertEqual(table[name], sorted(set(table[name])))
            self.assertTrue(all(type(code) is str and code for code in table[name]))
        self.assertFalse(set(table['mask']) & set(table['tooling']))
        self.assertEqual((len(table['mask']), len(table['tooling'])), (42, 1898))
        self.assertEqual(steps.step4_reason_classes(), (frozenset(table['mask']), frozenset(table['tooling'])))

    def test_R1_generator_copy_is_the_committed_blind_generator(self):
        digest = hashlib.sha256(GENERATOR.read_bytes()).hexdigest()
        self.assertEqual(digest, self.table['source']['generator_sha256'])
        self.assertEqual(digest, '051c13b267c747f3c4bf88318c819bcb9c5c603ba608160ca04389e817a549d2')

    def test_R1_regenerating_over_the_current_modules_gives_the_registered_lists(self):
        run = subprocess.run([sys.executable, '-I', str(GENERATOR), str(ROOT)],
                             capture_output=True, text=True, check=False)
        self.assertEqual(run.returncode, 0, run.stderr)
        fresh = json.loads(run.stdout)
        self.assertEqual(fresh['mask'], self.table['mask'])
        self.assertEqual(fresh['tooling'], self.table['tooling'])
        self.assertEqual(fresh['mask_rule'], self.table['mask_rule'])
        self.assertEqual(fresh['modules'], self.table['modules'])


if __name__ == '__main__':
    unittest.main()
