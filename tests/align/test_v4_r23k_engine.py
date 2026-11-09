"""R23k producer identity and frozen naming witnesses. Synthetic inputs only."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.align.apple.sampling import episode_seed, seed_inputs
from joulewise.align.v4_analysis import analyze, engine as e, raw
from joulewise.align.v4_analysis.io import canonical, digest, load, strict_json
from joulewise.align.v4_analysis.synthetic import member_config, series
from joulewise.schemas import BenchmarkConfig
from tests.align.test_v4_r23c_engine import native_payload, write_export

FROZEN = Path(__file__).resolve().parents[1] / 'fixtures/align_v4/r24_series_manifest.json'


class SeedIdentityTests(unittest.TestCase):
    def setUp(self):
        self.p = series(turns=4)
        self.m = self.p['windows'][0]['members'][5]
        self.m['config'] = member_config(self.m['slot'])
        # workload.py writes spec.seed (the index) into Episode.seed.
        self.m['summary']['seed'] = self.m['slot']['seed_index']

    def screen(self):
        e._screen_member(self.m, self.p['cohort'])
        return self.m

    def test_producer_seed_index_and_config_derivation_stay_eligible(self):
        config = BenchmarkConfig.from_mapping(self.m['config'])
        self.assertEqual(episode_seed(*seed_inputs(config, True),
            'shade/'+self.m['slot']['task_pair'], self.m['slot']['seed_index']),
            self.m['slot']['expected_episode_seed'])
        self.assertTrue(self.screen()['eligible'])
        self.assertNotIn('seed_identity_differs', self.m['reasons'])

    def test_derived_seed_in_episode_is_excluded_as_index_mismatch(self):
        self.m['summary']['seed'] = self.m['slot']['expected_episode_seed']
        self.assertFalse(self.screen()['eligible'])
        self.assertIn('seed_identity_differs', self.m['classes'])
        self.assertIn('seed_index_differs', self.m['reasons'])
        self.assertNotIn('derived_seed_differs', self.m['reasons'])

    def test_changed_config_is_excluded_as_derived_seed_mismatch(self):
        self.m['config']['run_metadata']['tags'] = ['align-model=changed-synthetic-model']
        self.assertFalse(self.screen()['eligible'])
        self.assertIn('seed_identity_differs', self.m['classes'])
        self.assertIn('derived_seed_differs', self.m['reasons'])
        self.assertNotIn('seed_index_differs', self.m['reasons'])

    def test_thinking_change_and_two_independent_mismatches(self):
        spec = strict_json(self.m['config']['workload_profile']['prompt_text'])
        spec['enable_thinking'] = False
        self.m['config']['workload_profile']['prompt_text'] = canonical(spec).decode()
        self.m['summary']['seed'] += 1
        self.assertFalse(self.screen()['eligible'])
        self.assertEqual(self.m['reasons'],
            ['derived_seed_differs', 'seed_identity_differs', 'seed_index_differs'])

    def test_production_model_name_fallback_and_integer_index(self):
        # R23l: v4 binds the align-model tag itself; production's model.name
        # fallback no longer qualifies a member.
        self.m['config']['run_metadata']['tags'] = []
        self.m['config']['model']['name'] = self.m['slot']['model_id']
        self.assertFalse(self.screen()['eligible'])
        self.assertIn('config_identity_differs:model', self.m['reasons'])
        self.m['config']['run_metadata']['tags'] = ['align-model='+self.m['slot']['model_id']]
        self.assertTrue(self.screen()['eligible'])
        # A bool is not a recorded integer seed, even for seed index 1.
        self.m['slot']['seed_index'] = 1
        self.m['summary']['seed'] = True
        self.screen()
        self.assertIn('seed_index_differs', self.m['reasons'])


class RawBundleSeedTests(unittest.TestCase):
    def setUp(self):
        # This fixture constructs all Episode/config/plist bytes from scratch.
        # It executes neither a controller nor a model nor a data-reading pipeline.
        from scripts.benchmark_v4_r21 import fixture
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'raw'
        path, _ = fixture(self.root, 64, windows=1)
        self.p = strict_json(path.read_bytes())
        window = self.p['windows'][0]
        self.slot = window['roster'][5]
        self.source = strict_json((self.root/window['raw_source']['path']).read_bytes())['members'][5]

    def screen(self):
        m = raw.member(self.root, self.slot, self.source)
        e._screen_member(m, self.p['cohort'])
        return m

    def test_real_producer_shaped_episode_with_bound_config_is_eligible(self):
        m = self.screen()
        self.assertEqual(m['summary']['seed'], self.slot['seed_index'])
        self.assertTrue(m['eligible'], m['reasons'])
        self.assertEqual(m['config_source'], self.source['config'])

    def test_episode_carrying_derived_seed_is_excluded(self):
        ref = self.source['episode']
        ep = strict_json((self.root/ref['path']).read_bytes())
        ep['seed'] = self.slot['expected_episode_seed']
        data = canonical(ep)
        (self.root/ref['path']).write_bytes(data)
        ref['sha256'] = digest(data)
        m = self.screen()
        self.assertFalse(m['eligible'])
        self.assertEqual(m['reasons'], ['seed_identity_differs', 'seed_index_differs'])

    def test_changed_bound_config_is_excluded_and_unbound_change_refuses(self):
        ref = self.source['config']
        config = strict_json((self.root/ref['path']).read_bytes())
        spec = strict_json(config['workload_profile']['prompt_text'])
        spec['enable_thinking'] = False
        config['workload_profile']['prompt_text'] = canonical(spec).decode()
        data = canonical(config)
        (self.root/ref['path']).write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'source digest differs'):
            self.screen()
        ref['sha256'] = digest(data)
        m = self.screen()
        self.assertFalse(m['eligible'])
        self.assertEqual(m['reasons'], ['derived_seed_differs', 'seed_identity_differs'])

    def test_captured_raw_member_requires_config_reference(self):
        self.source.pop('config')
        with self.assertRaisesRegex(ValueError, 'digest-bound config reference'):
            self.screen()


class DeskConfigBindingTests(unittest.TestCase):
    def test_release_config_digest_inventory_and_seed_screen(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_export(root, native_payload())
            loaded = load(path, through_window='C1')
            m = loaded['windows'][1]['members'][5]
            e._screen_member(m, loaded['cohort'])
            self.assertTrue(m['eligible'], m['reasons'])
            self.assertIn(m['config_source'], loaded['input_census'])
            # A new digest-bound config reaches the derived-seed screen; old
            # hashes refuse before the member can be used.
            ref = m['config_source']
            config = copy.deepcopy(m['config'])
            config['run_metadata']['tags'] = ['align-model=changed-synthetic-model']
            data = canonical(config)
            (root/ref['path']).write_bytes(data)
            with self.assertRaisesRegex(ValueError, 'source digest differs'):
                load(path, through_window='C1')
            document = strict_json(path.read_bytes())
            window = document['windows'][1]
            desk_ref = window['residual_source']
            desk = strict_json((root/desk_ref['path']).read_bytes())
            desk['members'][5]['config']['sha256'] = digest(data)
            data = canonical(desk)
            (root/desk_ref['path']).write_bytes(data)
            for key in ('residual_source', 'thermal_source'):
                window[key]['sha256'] = digest(data)
            # R23l: a re-digested config that is not the planned config refuses.
            with self.assertRaisesRegex(ValueError, 'config_digest_not_planned'):
                load(path, through_window='C1', document=document)

    def test_release_desk_member_requires_config_reference(self):
        for value in (None, member_config(e.roster('C1')[5])):
            with self.subTest(config=value), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path = write_export(root, native_payload())
                document = strict_json(path.read_bytes())
                window = document['windows'][1]
                ref = window['residual_source']
                desk = strict_json((root/ref['path']).read_bytes())
                if value is None:
                    desk['members'][5].pop('config')
                else:
                    desk['members'][5]['config'] = value
                data = canonical(desk)
                (root/ref['path']).write_bytes(data)
                for key in ('residual_source', 'thermal_source'):
                    window[key]['sha256'] = digest(data)
                with self.assertRaisesRegex(ValueError, 'digest-bound config reference'):
                    load(path, through_window='C1', document=document)


class RosterIdentityTests(unittest.TestCase):
    def test_all_374_slots_match_frozen_allocation_and_production_names(self):
        data = FROZEN.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), e.R24_SERIES_MANIFEST_SHA256)
        actual, expected = [], []
        for window in json.loads(data)['windows']:
            if window['id'] == 'W1':
                continue
            for m, slot in zip(window['members'], e.roster(window['id']), strict=True):
                # The frozen manifest stores allocations, not run IDs. Apply
                # r11 align_v4_series.build_files' registered naming to each
                # allocation; anchors retain the W1-kit capture IDs.
                run = (f"align-pilot-v3-episodes-a-e{m['ordinal']:02}" if m['pool'] == 'anchor'
                       else f"align-v4-{window['id'].lower()}-e{m['ordinal']:02}")
                expected.append(dict(ordinal=m['ordinal'], task_pair=m['pair'],
                    condition=m['condition'], model_id=m['model_id'], seed_index=m['seed_index'],
                    expected_episode_seed=m['episode_seed'], run_id=run,
                    held_out=m['pool'] not in ('anchor', 'sentinel'),
                    series_role=m['pool'] if m['pool'] in ('anchor', 'sentinel') else m['condition']))
                actual.append(slot)
        self.assertEqual(len(actual), 374)
        self.assertEqual(canonical(actual), canonical(expected))

    def test_real_production_names_pass_and_old_episodes_names_refuse(self):
        p = native_payload()
        p['windows'] = p['windows'][:2]  # W1, C1; full frozen C/T manifest retained.
        for m in p['windows'][1]['members'][4:]:
            m['slot']['run_id'] = m['thermal']['id'] = f"align-v4-c1-e{m['slot']['ordinal']:02}"
        fill, _ = analyze(p)
        self.assertEqual(fill['ledger'][0]['eligible_benign'], dict(spam=7, bank=7))
        for ordinal, stage in ((6, 'a'), (12, 'b')):
            for change_manifest in (False, True):
                with self.subTest(ordinal=ordinal, manifest=change_manifest):
                    old = copy.deepcopy(p)
                    m = old['windows'][1]['members'][ordinal-1]
                    run = f'align-v4-c1-episodes-{stage}-e{ordinal:02}'
                    m['slot']['run_id'] = m['thermal']['id'] = run
                    if change_manifest:
                        old['series_manifest']['windows'][1]['members'][ordinal-1]['run_id'] = run
                    with self.assertRaisesRegex(ValueError, 'roster differs'):
                        analyze(old)

    def test_supplemental_sentinels_use_production_names(self):
        self.assertEqual([s['run_id'] for s in e.roster('C3', escalated=True)[22:]],
                         ['align-v4-c3-e23', 'align-v4-c3-e24'])


if __name__ == '__main__':
    unittest.main()
