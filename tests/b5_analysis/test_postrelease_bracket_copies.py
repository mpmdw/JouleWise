"""Synthetic cache-lifetime checks; no archived or measured bundles are read."""
import pickle
from pathlib import Path
import unittest

from joulewise import analysis_run_cache as arc, analysis_verified_store as vdl
from joulewise.b5_analysis import bracket as br


def entry(leaf, root):
    return vdl.Entry(leaf, pickle.dumps({'status': 'succeeded'}),
                     ((str(root), 'a'*64),), (), (), (), (), None)


class TemporaryCopyTests(unittest.TestCase):
    def test_only_temporary_l3_values_expire_on_normal_and_exceptional_exit(self):
        for fail in (False, True):
            with self.subTest(fail=fail), arc.analysis_run_caches({}, vdl_mode=vdl.ON) as caches:
                store = caches.vdl
                store._poisoned.add('retained-poison')
                store._defects.append('retained-defect')
                store._count('retained-counter')
                sentinel = RuntimeError('synthetic evaluation failure')
                try:
                    with br._temporary_members() as root:
                        self.assertTrue(root.is_dir())
                        (root/'copy').mkdir()
                        values = {
                            'temporary': entry('L3_reduce_dict', root/'copy'),
                            'aliased': entry('L3_reduce_dict', str(root/'copy')+'\0'+str(root/'copy')),
                            'sibling': entry('L3_reduce_dict', root.with_name(root.name+'-sibling')/'copy'),
                            'ordinary': entry('L3_reduce_dict', root.parent/'ordinary'),
                            'l1': entry('L1_strict_validation', Path('copy')),
                            'l4': entry('L4_calibration_bracket', Path('copy')),
                        }
                        for key, value in values.items():
                            store._insert(key, value)
                        if fail:
                            raise sentinel
                except RuntimeError as caught:
                    self.assertIs(caught, sentinel)
                self.assertFalse(root.exists())
                for new_only in (False, True):
                    payload = store.export_entries(new_only=new_only)
                    self.assertEqual(set(payload['entries']), {'sibling', 'ordinary', 'l1', 'l4'})
                    self.assertEqual(payload['poisoned'], ['retained-poison'])
                    self.assertEqual(payload['defects'], ['retained-defect'])
                self.assertEqual(store.restricted_counters(), {'retained-counter': 1})

    def test_no_store_still_cleans_the_temporary_directory(self):
        with br._temporary_members() as root:
            self.assertTrue(root.is_dir())
        self.assertFalse(root.exists())
