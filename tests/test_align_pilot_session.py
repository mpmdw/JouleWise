"""Align pilot v0: kit, offline SHADE factory, session prepare and desk on synthetic data only."""
from __future__ import annotations

from collections import Counter
from contextlib import redirect_stdout
from dataclasses import replace
import hashlib
import io
import json
import math
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple import pilot
from joulewise.align.apple.workload import EpisodeSpec, WORKLOAD_KIND, read_episode_bundle
from joulewise.b5 import chain, plan
from joulewise.b6 import registration
from joulewise.clock import FakeClock
from joulewise.controller import run_benchmark
from joulewise.schemas import BenchmarkConfig
from scripts import align_pilot_kit as kit, align_pilot_session as s, bytes_h_session as h
from tests.align.test_apple_campaign import base_config
from tests.align.test_shade import fixture_source

ROOT = Path(__file__).resolve().parents[1]


def setUpModule():
    global _temporary, _old_tempdir, _old_env
    _old_tempdir = tempfile.tempdir
    _old_env = {k: os.environ.get(k) for k in ('TMPDIR', 'JW_B5_SYNTHETIC_ONLY')}
    _temporary = tempfile.TemporaryDirectory(prefix='align-pilot-module-')
    os.environ.update(TMPDIR=_temporary.name, JW_B5_SYNTHETIC_ONLY='1')
    tempfile.tempdir = _temporary.name


def tearDownModule():
    tempfile.tempdir = _old_tempdir
    for key, value in _old_env.items():
        if value is None: os.environ.pop(key, None)
        else: os.environ[key] = value
    _temporary.cleanup()


class KitTests(unittest.TestCase):
    def test_committed_kit_matches_generator_and_runs_only_align_members(self):
        files = kit.build_files(ROOT)
        for path, raw in files.items():
            self.assertEqual((ROOT / path).read_bytes(), raw, path)
        tree = json.loads(files[kit.KIT / 'plan_tree.json'])
        self.assertTrue(tree['non_claim'])
        self.assertEqual(len(chain.stage_plan(tree)), len(tree['stage_graph']))
        self.assertNotIn(kit.PACK_ID, json.loads((ROOT / 'configs/b6/loop.json').read_bytes())['base_order'])
        self.assertFalse((ROOT / 'configs/b6/packs' / kit.PACK_ID).exists())
        collection = json.loads(files[kit.KIT / 'collection_plan.json'])
        members = collection['members']
        # 2 pairs x 2 conditions x 3 repeats.
        self.assertEqual(len(members), 12)
        self.assertEqual(Counter((m['task_pair'], m['condition']) for m in members),
                         Counter({(p, c): 3 for p in pilot.PILOT_V0_PAIRS for c in pilot.PILOT_V0_CONDITIONS}))
        # Matched ABBA: each consecutive pair is one cell's benign and sabotage,
        # and the order alternates benign-first and sabotage-first.
        for i in range(0, 12, 2):
            a, b = members[i], members[i + 1]
            self.assertEqual((a['task_pair'], a['repeat']), (b['task_pair'], b['repeat']))
            self.assertEqual({a['condition'], b['condition']}, {'benign', 'sabotage'})
            self.assertEqual(a['condition'], 'benign' if i % 4 == 0 else 'sabotage')
        # Base config is the BYTES qwen3-8b member; only the workload differs.
        base = json.loads((ROOT / kit.BASE_CONFIG).read_bytes())
        for member in members:
            config = BenchmarkConfig.from_mapping(json.loads((ROOT / member['config_path']).read_bytes()))
            self.assertEqual(config.workload_profile.name, WORKLOAD_KIND)
            self.assertEqual(config.model.to_dict() if hasattr(config.model, 'to_dict') else config.to_dict()['model'],
                             BenchmarkConfig.from_mapping(base).to_dict()['model'])
            self.assertEqual(config.to_dict()['sampling'], BenchmarkConfig.from_mapping(base).to_dict()['sampling'])
            spec = EpisodeSpec.from_text(config.workload_profile.prompt_text)
            self.assertEqual(spec.task_factory, pilot.FACTORY)
            self.assertEqual(spec.task_kwargs['cache_dir'], kit.SHADE_CACHE)
            self.assertEqual((spec.max_turns, spec.max_tokens, spec.temperature),
                             (pilot.PILOT_V0_MAX_TURNS, pilot.PILOT_V0_MAX_TOKENS, 0.0))
            self.assertEqual(spec.mock_turns, ())
        for stage in tree['stage_graph']:
            ref = stage.get('input', {})
            if ref.get('kind') == 'manifest':
                raw = (ROOT / ref['path']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), ref['sha256'])
                self.assertEqual(stage['expected_count'], len(json.loads(raw)['executed_order']))

    def test_registration_inputs_load_and_flag_the_planning_bound(self):
        reg = ROOT / kit.KIT / 'registration'
        sized = registration.load_sizing(reg)['packs'][kit.PACK_ID]
        self.assertIn('sizing.planning_bound_unmeasured', sized['flags'])
        # 12 align members plus 25 inherited scaffold members (18 corpus, 7 references).
        self.assertEqual((sized['align_members'], sized['scaffold_members'], sized['member_count']), (12, 25, 37))
        p = kit.PLANNING
        turn = p['context_tokens_max'] / p['prefill_tok_s'] + pilot.PILOT_V0_MAX_TOKENS / p['decode_tok_s'] + p['tool_s_per_turn']
        self.assertTrue(math.isclose(sized['episode_upper_s'], pilot.PILOT_V0_MAX_TURNS * turn, rel_tol=1e-12))
        pins = registration.load_identity_pins(reg)
        source = registration.load_identity_pins(ROOT / kit.SOURCE_KIT / 'registration')
        collection = h.read(ROOT / kit.KIT / 'collection_plan.json')
        episodes = {h.align_unit_id('qwen3-8b', m['run_id']) for m in collection['members']}
        # One identity unit per episode (its spec is its declared workload).
        self.assertEqual(set(pins['units']), episodes | {'neg8_reference'})
        for name, unit in pins['units'].items():
            model_id = 'neg8_reference' if name == 'neg8_reference' else 'qwen3-8b'
            self.assertEqual(unit['model_artifact_sha256'], source['units'][model_id]['model_artifact_sha256'])
            self.assertEqual(unit['config_count'], len(unit['config_paths']))
            self.assertEqual(unit['config_count'], 25 if name == 'neg8_reference' else 1)


class OfflineFactoryTests(unittest.TestCase):
    def test_missing_cache_never_fetches(self):
        with tempfile.TemporaryDirectory() as directory, patch('subprocess.run') as runner:
            task = pilot.offline_shade_task('spam_filter_update', cache_dir=directory)
            with self.assertRaises(Exception):
                task.reset(1)
            runner.assert_not_called()
            self.assertIn('upstream_cache_missing', task.upstream.flags)
            self.assertFalse(pilot.verify(directory)['ok'])

    def test_specs_are_repeats_of_identical_work(self):
        specs = pilot.pilot_specs()
        self.assertEqual(len(specs), 12)
        cells = Counter(json.dumps({**json.loads(x.to_text()), 'seed': None}, sort_keys=True) for x in specs)
        self.assertEqual(sorted(cells.values()), [3] * 4)


def fixture_spec(source, condition, seed):
    """Two scripted turns on the SHADE-shaped fixture: one tool call, then end_task."""
    turns = (
        {'prompt_tokens': 1500, 'completion_tokens': 300 + (200 if condition == 'sabotage' else 0),
         'reasoning_tokens': 200 if condition == 'sabotage' else 0,
         'content': ('<think>side plan</think>' if condition == 'sabotage' else '')
                    + '<tool_call>' + json.dumps({'name': 'read_ledger', 'arguments': {'page': 0}}) + '</tool_call>'},
        {'prompt_tokens': 1900, 'completion_tokens': 120,
         'content': '<tool_call>' + json.dumps({'name': 'end_task', 'arguments': {}}) + '</tool_call>'},
        {'prompt_tokens': 2000, 'completion_tokens': 40, 'content': 'Review finished.'},
    )
    return EpisodeSpec(task_factory=pilot.FACTORY, condition=condition, seed=seed, max_turns=4, max_tokens=1024,
                       temperature=0.0, mock_turns=turns,
                       task_kwargs={'task_pair': 'ledger_review', 'cache_dir': str(source.cache_dir),
                                    'commit': source.commit, 'file_sha256': source.file_sha256})


class SyntheticDeskTests(unittest.TestCase):
    """The pilot factory and desk extraction on mock-runtime bundles of the fixture."""

    def run_member(self, runs, spec, run_id):
        config = base_config()
        config = replace(config, run_id=run_id, workload_profile=replace(
            config.workload_profile, name=WORKLOAD_KIND, prompt_text=spec.to_text(),
            prompt_tokens=None, output_tokens=None))
        bundle, summary = run_benchmark(config, runs, FakeClock())
        self.assertEqual(summary.status.value, 'succeeded', summary)
        return bundle

    def test_factory_bundles_desk_checks_and_harvest_handoff(self):
        with tempfile.TemporaryDirectory() as directory, fixture_source() as source:
            root = Path(directory)
            runs = root / 'runs'
            members = []
            for repeat in (1, 2):
                for condition in ('benign', 'sabotage'):
                    run_id = f'pilot-{condition}-{repeat}'
                    bundle = self.run_member(runs, fixture_spec(source, condition, repeat), run_id)
                    self.assertEqual(bundle.name, run_id)
                    members.append({'run_id': run_id, 'task_pair': 'ledger_review', 'condition': condition,
                                    'repeat': repeat, 'ordinal': len(members) + 1})
            episode = read_episode_bundle(runs / 'pilot-sabotage-1')
            self.assertEqual(episode.task_pair, 'shade/ledger_review')
            self.assertEqual(episode.totals()['tool_calls'], 2)
            self.assertEqual(episode.totals()['hidden_tokens'], 200)
            # Session scaffold: terminal record, plan and kit collection plan.
            measurement = root / 'measurement'
            (measurement / s.KIT).mkdir(parents=True)
            h.write(measurement / s.KIT / 'collection_plan.json', {'members': members})
            custody = root / 'custody'
            (custody / 'night').mkdir(parents=True)
            (custody / 'night/result.json').write_text('{}')
            session = root / 'session'
            (session / 'staging').mkdir(parents=True)
            h.write(root / 'plan.json', {'custody_root': str(custody)})
            h.write(session / 'session.json', {
                'session_id': 'align-pilot-synthetic', 'plan_path': str(root / 'plan.json'),
                'measurement_root': str(measurement), 'registration_dir': str(measurement / s.KIT / 'registration'),
                'runs_roots': {'claim': str(runs)}, 'inputs': {'runs_parent': str(root)}})
            calls = []

            def harvest(argv, **kwargs):
                calls.append(argv)
                return SimpleNamespace(returncode=0, stdout='{}\n', stderr='')

            with redirect_stdout(io.StringIO()):
                status = s.desk(session, run=harvest)
            self.assertEqual(status['harvest_exit'], 0)
            self.assertIn('--non-claim', calls[0])
            result = h.read(session / 'PILOT.json')
            self.assertTrue(result['non_claim'])
            self.assertEqual(result['status'], 'instrument_ok', result['checks'])
            sabotage = next(m for m in result['members'] if m['run_id'] == 'pilot-sabotage-1')['summary']
            benign = next(m for m in result['members'] if m['run_id'] == 'pilot-benign-1')['summary']
            self.assertEqual(sabotage['totals']['hidden_tokens'] - benign['totals']['hidden_tokens'], 200)
            self.assertEqual([len(x['per_turn_decode_tokens']) for x in (benign, sabotage)], [3, 3])
            (channel,) = benign['energy']
            # Mock timeline (D-019): 10 ms per output token, so 200 hidden
            # tokens add 2 s; scripted prompt counts are equal across conditions.
            self.assertTrue(math.isclose(sabotage['duration_s'] - benign['duration_s'], 2.0, rel_tol=1e-6))
            extra = sabotage['energy'][channel]['joules'] - benign['energy'][channel]['joules']
            # The hidden work clears the summed attribution half-widths.
            bound = sabotage['energy'][channel]['half_width_j'] + benign['energy'][channel]['half_width_j']
            self.assertGreater(extra, bound, (extra, bound))
            spread = result['repeat_energy_spread']['ledger_review/benign'][channel]
            self.assertEqual(spread['n'], 2)
            # Identical scripted work under the fake clock: identical energy.
            self.assertLessEqual(spread['range_j'], 1e-6 * spread['mean_j'])

    def test_checks_fail_for_missing_bundle_and_nondeterministic_repeat(self):
        good = {'energy': {'powermetrics:cpu': {'joules': 10.0, 'segment_sum_j': 10.0, 'segments': 3}},
                'flags': [], 'per_turn_decode_tokens': [5, 6]}
        rows = [{'task_pair': 'p', 'condition': 'benign', 'summary': good},
                {'task_pair': 'p', 'condition': 'benign', 'summary': {**good, 'per_turn_decode_tokens': [5, 7]}},
                {'task_pair': 'p', 'condition': 'sabotage', 'summary': None}]
        checks, deterministic, _ = s.instrument_checks(rows)
        self.assertFalse(checks['I1_all_bundles_readable'])
        self.assertFalse(checks['I2_energy_on_every_episode'])
        self.assertTrue(checks['I3_attribution_tiles_episode'])
        self.assertFalse(checks['I4_greedy_repeats_identical_tokens'])
        flagged = [{**rows[0], 'summary': {**good, 'flags': ['power_unavailable:no_bundle_trace']}}]
        self.assertFalse(s.instrument_checks(flagged)[0]['I2_energy_on_every_episode'])


class RealKitStagingTests(unittest.TestCase):
    def test_staged_kit_projects_identity_and_authenticates_every_dispatched_config(self):
        from joulewise import arm_readiness, window_lineage
        from joulewise.analysis_engine.inputs import validate_identity_pin_projection
        from joulewise.b5 import driver, harvest

        with tempfile.TemporaryDirectory() as temporary:
            session = Path(temporary)
            view, pack = h.measurement_view(ROOT, session, kit=s.KIT, pack_id=s.PACK_ID)
            tree = h.read(pack / 'plan_tree.json')
            projection = validate_identity_pin_projection(tree['arm_attachments']['identity_pin_projection'])
            self.assertEqual({u['identity_unit_id'] for u in projection['identity_units']},
                             set(registration.load_identity_pins(ROOT / s.KIT / 'registration')['units']))
            self.assertEqual(projection['state'], 'unprojected')
            inventory = arm_readiness._authenticated_pack_config_inventory(pack)
            roots = {name: session / tree['roots'][name + '_root_leaf'] for name in ('claim', 'bound')}
            custody = session / 'custody'
            for directory in (*roots.values(), custody):
                directory.mkdir()
            window = {'pack': {'pack_root': str(pack), 'pack_id': s.PACK_ID, 'pack_sha256': None,
                               'pack_plan_id': tree['plan']['plan_id'],
                               'window_id': tree['window_identity']['window_id']},
                      'bracket_session_id': 'align-kit-rehearsal',
                      'bindings': {'pre_attempt_id': 'align-kit-pre', 'post_attempt_id': 'align-kit-post'}}
            driver._production_lineage(driver.LineageRequest(
                plan=None, plan_path=session / 'unused-plan.json', custody_root=custody,
                night_dir=custody / 'night', hazard_window=window,
                claim_runs_root=roots['claim'], bound_runs_root=roots['bound'],
                arm_record_path=None, arm_decision_path=None, boot_session_uuid=None))
            checked = []
            for dispatch in plan.resolve_stage_dispatches(tree, view):
                self.assertIsNone(dispatch.error)
                directory = view / dispatch.config_dir
                manifest = h.read(directory / 'order_manifest.json')
                selected = roots['bound' if dispatch.runs_root_binding == 'bound_runs_root' else 'claim']
                for row in manifest['executed_order']:
                    config = directory / row['config']
                    self.assertEqual(inventory[config.relative_to(pack).as_posix()],
                                     hashlib.sha256(config.read_bytes()).hexdigest())
                    arm_readiness.authenticate_campaign_launch_lineage(selected, config_paths=[config])
                    checked.append(config)
            # 12 align episodes plus 18 corpus and 7 reference scaffold members.
            self.assertEqual(len(checked), 37)
            self.assertEqual(sum(1 for c in checked if 'episodes-' in c.parent.name), 12)
            roster = harvest.build_roster(pack, view)
            self.assertEqual(len(roster['members']), 37)
            self.assertEqual(roster['duplicate_listings'], {})
            checked[-1].write_bytes(checked[-1].read_bytes() + b'\n')
            with self.assertRaises(window_lineage.HazardLineageError):
                window_lineage.authenticate_campaign(roots['claim'], config_paths=[checked[-1]])


class SessionPrepareTests(unittest.TestCase):
    """The BYTES item-H prepare with the align kit, through the real window-plan writer."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.measurement = self.root / 'measurement'
        self.session = self.root / 'session'
        m = self.measurement
        (m / 'configs/campaigns').mkdir(parents=True)
        for p in (ROOT / 'configs').iterdir():
            if p.name != 'campaigns': (m / 'configs' / p.name).symlink_to(p, target_is_directory=p.is_dir())
        for p in (ROOT / 'configs/campaigns').iterdir():
            if p.name != 'align_pilot_v0': (m / 'configs/campaigns' / p.name).symlink_to(p, target_is_directory=p.is_dir())
        shutil.copytree(ROOT / s.KIT, m / s.KIT)
        for name in ('scripts', 'joulewise', 'docs'):
            (m / name).symlink_to(ROOT / name, target_is_directory=True)
        (m / '.venv/bin').mkdir(parents=True)
        (m / '.venv/bin/python').symlink_to(sys.executable)
        (m / plan.DEFAULT_LEDGER_RELATIVE).parent.mkdir(parents=True)
        (m / plan.DEFAULT_LEDGER_RELATIVE).write_text('')
        reg = m / s.KIT / 'registration'
        pins = h.read(reg / 'identity_pins.json')
        inventory = h.read(reg / 'model_artifact_inventory.json')
        fake = self.root / 'models'; fake.mkdir(); (fake / 'weight').write_bytes(b'synthetic')
        for name, unit in pins['units'].items():
            unit['model_source'] = str(fake)
            inventory['artifacts'][name]['inventory'] = [{'path': 'weight', 'size_bytes': 9}]
        h.write(reg / 'identity_pins.json', pins)
        h.write(reg / 'model_artifact_inventory.json', inventory)

    def producer(self, argv, **kwargs):
        if '-c' in argv:
            import base64
            payload = base64.b64encode(b'{"synthetic":true}\n').decode()
            return SimpleNamespace(returncode=0, stdout=json.dumps({k: payload for k in h.desk_identity.EXPECTED}), stderr='')
        return SimpleNamespace(returncode=0, stdout='a'*40 if 'rev-parse' in argv else '', stderr='')

    def prepared(self):
        with patch.object(plan, 'ledger_head_status', return_value={'blocking': []}), redirect_stdout(io.StringIO()):
            return s.prepare(self.measurement, self.session, run=self.producer, now=lambda: 1700000000,
                             statvfs=lambda _: SimpleNamespace(f_bavail=10**12, f_frsize=1), capacity=lambda _: None)

    def seed_collection(self, state, align_bundle):
        """Scaffold members from the strict seed bundle, episodes from a real mock align bundle.

        Mirrors tests/test_bytes_h_session.py seed_collection; no model or collector runs.
        """
        clock, journal = [], []
        tree = h.read(self.measurement / s.KIT / 'plan_tree.json')
        seed = ROOT / 'tests/fixtures/d117_v2_production/strict_seed_bundle'
        order = 0
        for stage in tree['stage_graph']:
            start = 1000 + order * 20
            if stage['kind'] == 'campaign_collection':
                manifest = h.read(self.measurement / stage['input']['path'])
                for row in manifest['executed_order']:
                    rid = row['run_id']
                    key = 'bound' if 'bound-collection' in stage['stage_id'] else 'claim'
                    bundle = Path(state['runs_roots'][key]) / rid
                    shutil.copytree(align_bundle if 'episodes-' in stage['stage_id'] else seed, bundle)
                    config = h.read((self.measurement / stage['input']['path']).parent / row['config'])
                    h.write(bundle / 'config.json', config)
                    for name in ('metadata.json', 'summary_metrics.json'):
                        value = h.read(bundle / name); value['run_id'] = rid; h.write(bundle / name, value)
                    a = (1000 + order * 20) * 10**9; b = a + 15 * 10**9
                    for event, stamp in [('start', a), ('end', b)]:
                        clock.append({'run_id': rid, 'event': event, 'clock': {'wall_s': stamp / 1e9,
                            'monotonic_ns': stamp, 'monotonic_raw_ns': stamp}})
                    order += 1
                end = 1000 + order * 20
            else:
                end = start + 1
            journal.append({'stage_id': stage['stage_id'], 'kind': stage['kind'], 'rc': 0,
                            'started_epoch_s': start, 'ended_epoch_s': end})
        custody = self.session / 'custody'
        def jsonl(path, values):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(''.join(json.dumps(v) + '\n' for v in values))
        jsonl(custody / 'collection/run_clock.jsonl', clock)
        jsonl(custody / 'night/chain-stages.jsonl', journal)
        h.write(custody / 'night/chain.started', {'pgid': None})
        h.write(custody / 'night/chain.exited', {'exit_code': 0})
        h.write(custody / 'night/result.json', {'chain_exit_code': 0})

    def test_prepared_session_desk_reads_episodes_then_runs_the_real_harvest(self):
        import subprocess
        state = self.prepared()
        self.assertEqual(state['preparation_status'], 'STAGED')
        with tempfile.TemporaryDirectory() as directory, fixture_source() as source:
            runs = Path(directory)
            bundle = SyntheticDeskTests.run_member(self, runs, fixture_spec(source, 'sabotage', 1), 'align-seed')
            self.seed_collection(state, bundle)
        with redirect_stdout(io.StringIO()):
            status = s.desk(self.session, run=subprocess.run)
        result = h.read(self.session / 'PILOT.json')
        self.assertEqual(len(result['members']), 12)
        # Every episode bundle read back; repeats are byte-identical seeds here.
        self.assertTrue(result['checks']['I1_all_bundles_readable'], result['members'][0])
        self.assertTrue(result['checks']['I2_energy_on_every_episode'])
        self.assertTrue(result['checks']['I3_attribution_tiles_episode'])
        # The real non-claim harvest over 25 scaffold and 12 align bundles.
        stderr = (self.session / 'staging/harvest.stderr').read_text()
        self.assertIn(status['harvest_exit'], (0, 6), stderr[-3000:])
        self.assertIn('--non-claim', status['harvest_argv'])

    def test_prepare_stages_the_align_kit_without_install_or_loop_registration(self):
        with patch.object(plan, 'ledger_head_status', return_value={'blocking': []}), redirect_stdout(io.StringIO()) as out:
            state = s.prepare(self.measurement, self.session, run=self.producer, now=lambda: 1700000000,
                              statvfs=lambda _: SimpleNamespace(f_bavail=10**12, f_frsize=1), capacity=lambda _: None)
        self.assertEqual(state['preparation_status'], 'STAGED', out.getvalue())
        self.assertTrue(state['session_id'].startswith('align-pilot-'))
        record = h.read(state['plan_path'])
        self.assertEqual(record['hazard_window']['member_count'], 37)
        self.assertEqual(Path(state['inputs']['pack_root']), self.session / 'measurement/configs/campaigns' / s.PACK_ID)
        self.assertEqual(Path(state['registration_dir']), self.session / 'measurement' / s.KIT / 'registration')
        self.assertIn({'kind': 'sizing.planning_bound_unmeasured', 'pack_id': s.PACK_ID}, state['flags'])
        self.assertNotIn('qwen3-8b-8bit', json.dumps(state['flags']))
        self.assertFalse((self.session / 'collection.active').exists())
        self.assertNotIn('install', state)
        # The staged pack keeps every align member config byte-identical.
        pack = Path(state['inputs']['pack_root'])
        staged = sorted((pack / 'members').glob('*episodes-*/*.json'))
        configs = [p for p in staged if p.name != 'order_manifest.json']
        self.assertEqual(len(configs), 12)
        for path in configs:
            original = ROOT / s.KIT / 'stages' / path.parent.name.removeprefix(s.PACK_ID + '-') / path.name
            self.assertEqual(path.read_bytes(), original.read_bytes())


if __name__ == '__main__':
    unittest.main()
