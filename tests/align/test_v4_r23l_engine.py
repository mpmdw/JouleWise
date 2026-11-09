"""R23l hand witnesses: bundle config bound to its slot and to the committed plan.

These carry the reviewer's p11 cases, with controls. All inputs are synthetic.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.align.v4_analysis import analyze, engine as e
from joulewise.align.v4_analysis.io import canonical, digest, load, strict_json
from joulewise.align.v4_analysis.synthetic import series
from tests.align.test_v4_r23c_engine import native_payload, write_export


def other_pair(m):
    return next(pair for pair in e.PAIRS if pair != m['slot']['task_pair'])


def spec_edit(m, **changes):
    spec = json.loads(m['config']['workload_profile']['prompt_text'])
    for key, value in changes.items():
        if key == 'task_pair':
            spec['task_kwargs']['task_pair'] = value
        elif value is None:
            spec.pop(key, None)
        else:
            spec[key] = value
    m['config']['workload_profile']['prompt_text'] = canonical(spec).decode()


class ConfigIdentityTests(unittest.TestCase):
    def setUp(self):
        self.p = series(turns=4)
        self.m = copy.deepcopy(self.p['windows'][0]['members'][6])   # held-out benign D

    def screen(self):
        e._screen_member(self.m, self.p['cohort'])
        return self.m

    def test_control_is_eligible(self):
        self.assertTrue(self.screen()['eligible'], self.m['reasons'])

    def test_each_identity_mismatch_excludes_with_its_sub_reason(self):
        cases = {
            'pair': lambda m: spec_edit(m, task_pair=other_pair(m)),
            'condition': lambda m: spec_edit(m, condition='sabotage'),
            'seed': lambda m: spec_edit(m, seed=99),
            'run_id': lambda m: m['config'].__setitem__('run_id', 'align-v4-c1-e09'),
            'model': lambda m: m['config']['run_metadata'].__setitem__('tags', ['align-model=qwen3-30b-a3b']),
        }
        for name, mutate in cases.items():
            with self.subTest(mismatch=name):
                self.setUp()
                mutate(self.m)
                m = self.screen()
                self.assertFalse(m['eligible'])
                self.assertIn('config_identity_differs', m['classes'])
                self.assertIn('config_identity_differs:'+name, m['reasons'])

    def test_sabotage_config_under_benign_slot_never_calibrates(self):
        spec_edit(self.m, condition='sabotage')
        self.assertFalse(self.screen()['eligible'])
        p = series(turns=4)
        target = p['windows'][0]['members'][6]
        spec_edit(target, condition='sabotage')
        fill, _ = analyze(p)
        members = fill['thresholds']['counts_logged/'+e.KEYS[target['slot']['task_pair']]]['calibration_members']
        self.assertNotIn('C1/'+target['slot']['run_id'], members)
        row = fill['windows'][0]['eligibility'][6]
        self.assertIn('config_identity_differs:condition', row['reasons'])

    def test_derived_seed_uses_the_configs_own_pair_and_seed(self):
        # A swapped pair also moves production's derived seed.
        spec_edit(self.m, task_pair=other_pair(self.m))
        m = self.screen()
        self.assertIn('derived_seed_differs', m['reasons'])
        self.setUp()
        spec_edit(self.m, seed=99)
        self.assertIn('derived_seed_differs', self.screen()['reasons'])

    def test_p11_seed_controls_still_hold(self):
        self.m['summary']['seed'] = self.m['slot']['expected_episode_seed']
        self.assertIn('seed_index_differs', self.screen()['reasons'])
        for mutate in (lambda m: spec_edit(m, enable_thinking=False),
                       lambda m: spec_edit(m, enable_thinking=None)):
            self.setUp()
            mutate(self.m)
            self.assertIn('derived_seed_differs', self.screen()['reasons'])

    def test_malformed_or_samplerless_config_excludes_only_that_member(self):
        cases = {
            'sampler removed (nonzero temperature)': lambda m: spec_edit(m, sampler=None),
            'sampler removed (temperature 0)': lambda m: spec_edit(m, sampler=None, temperature=0),
            'prompt text not JSON': lambda m: m['config']['workload_profile'].__setitem__('prompt_text', '{'),
            'unknown spec schema': lambda m: spec_edit(m, schema='other'),
        }
        for label, mutate in cases.items():
            with self.subTest(case=label):
                p = series(turns=4)
                target = p['windows'][0]['members'][6]
                mutate(target)
                fill, _ = analyze(p)        # the series is not refused
                row = fill['windows'][0]['eligibility'][6]
                self.assertEqual(row['reasons'], ['config_invalid'])
                self.assertFalse(row['eligible'])
                self.assertTrue(fill['windows'][0]['eligibility'][7]['eligible'])


class PlannedConfigCustodyTests(unittest.TestCase):
    def export(self, root):
        path = write_export(root, native_payload())
        return path, strict_json(path.read_bytes())

    def rewrite_desk(self, root, document, window_index, edit):
        window = document['windows'][window_index]
        ref = window['residual_source']
        desk = strict_json((root/ref['path']).read_bytes())
        edit(desk)
        data = canonical(desk)
        (root/ref['path']).write_bytes(data)
        for key in ('residual_source', 'thermal_source'):
            window[key]['sha256'] = digest(data)

    def test_control_loads_and_binds_every_captured_member(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _ = self.export(root)
            loaded = load(path, through_window='C2')
        paths = {r['path'] for r in loaded['input_census']}
        self.assertIn('C1_1-plan.json', paths)
        self.assertIn('C1_1-7-kit.json', paths)

    def test_unplanned_configs_refuse(self):
        def other_kit(desk):          # another member's planned kit file
            desk['members'][5]['planned_config'] = desk['members'][6]['planned_config']
        def no_kit(desk):
            desk['members'][5].pop('planned_config')
        def other_bundle(desk):       # another member's bundle config
            desk['members'][5]['config'] = desk['members'][6]['config']
        for label, edit in (('other kit', other_kit), ('no kit', no_kit), ('other bundle', other_bundle)):
            with self.subTest(case=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path, document = self.export(root)
                self.rewrite_desk(root, document, 1, edit)
                with self.assertRaisesRegex(ValueError, 'config_digest_not_planned'):
                    load(path, through_window='C1', document=document)

    def test_plan_digest_or_plan_absence_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, document = self.export(root)
            plan_ref = document['windows'][1]['plan_source']
            plan = strict_json((root/plan_ref['path']).read_bytes())
            plan['members'][5]['config_sha256'] = '0'*64
            data = canonical(plan)
            (root/plan_ref['path']).write_bytes(data)
            altered = copy.deepcopy(document)
            altered['windows'][1]['plan_source']['sha256'] = digest(data)
            with self.assertRaisesRegex(ValueError, 'config_digest_not_planned'):
                load(path, through_window='C1', document=altered)
            missing = copy.deepcopy(document)
            missing['windows'][1].pop('plan_source')
            with self.assertRaisesRegex(ValueError, 'config_digest_not_planned: window lacks plan_source'):
                load(path, through_window='C1', document=missing)

    def test_rewritten_bundle_config_refuses_even_with_a_matching_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, document = self.export(root)
            def edit(desk):
                ref = desk['members'][5]['config']
                config = json.loads((root/ref['path']).read_bytes())
                config['run_metadata']['tags'] = ['align-model=changed']
                data = (json.dumps(config, indent=2, sort_keys=True)+'\n').encode()
                (root/ref['path']).write_bytes(data)
                ref['sha256'] = digest(data)
            self.rewrite_desk(root, document, 1, edit)
            with self.assertRaisesRegex(ValueError, 'bundle config is not the planned config'):
                load(path, through_window='C1', document=document)


if __name__ == '__main__':
    unittest.main()
