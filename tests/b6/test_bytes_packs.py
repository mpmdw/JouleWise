"""BYTES drafts: actual schema readers, whole floor modules and fixed-tree replay."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.b5 import chain
from joulewise.b6 import compose, queue
from joulewise.b6.pack_registration import Registration, load, validate
from joulewise.flags.catalog import load_catalog
from joulewise.schemas import BenchmarkConfig
from scripts import bytes_plan_trees as plans

ROOT = Path(__file__).resolve().parents[2]
configs = plans.configs


def read(path):
    return json.loads(path.read_bytes())


class BytesConfigTests(unittest.TestCase):
    def test_500_configs_use_exact_R2_workload_and_null_abba_arms(self):
        seen = set()
        for spec in configs.ROSTER:
            model_id = spec[0]
            rows = []
            for directory in configs.config_dirs(model_id):
                manifest = read(ROOT / directory / 'order_manifest.json')
                self.assertEqual(manifest['planned_n_bundles'], len(manifest['executed_order']))
                for row in manifest['executed_order']:
                    path = ROOT / directory / row['config']
                    raw = path.read_bytes()
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), row['config_sha256'])
                    data = json.loads(raw)
                    parsed = BenchmarkConfig.from_mapping(data)
                    self.assertFalse(parsed.config_warnings)
                    self.assertEqual(parsed.workload_profile.prompt_tokens, 2048)
                    self.assertEqual(parsed.workload_profile.output_tokens, 512)
                    self.assertEqual(parsed.workload_profile.warmup_runs, 1)
                    self.assertEqual(parsed.workload_profile.repetitions, 1)
                    self.assertEqual((parsed.sampling.idle_seconds, parsed.sampling.warmup_seconds), (57.6, 5))
                    self.assertNotIn('df_rq_mid', path.name)
                    self.assertNotIn(row['run_id'], seen)
                    seen.add(row['run_id'])
                    self.assertEqual(data['model']['name'], spec[1])
                    self.assertEqual(data['quantization']['bits'], 8 if model_id == 'qwen3-8b-8bit' else 4)
                    rows.append((row, data))
            self.assertEqual(len(rows), 50)
            self.assertEqual([row['role'] for row, _ in rows[:10]], ['absolute_repeat'] * 10)
            baseline = deepcopy(rows[0][1])
            baseline.pop('run_id')
            baseline.pop('run_metadata')
            for row, data in rows:
                condition = {k: v for k, v in data.items() if k not in ('run_id', 'run_metadata')}
                self.assertEqual(condition, baseline)  # A and B are the identical null workload
            for block in range(10):
                quad = [row for row, _ in rows[10 + block * 4:14 + block * 4]]
                self.assertEqual([row['position'] for row in quad], ['A1', 'B1', 'B2', 'A2'])
                self.assertEqual(len({row['block_id'] for row in quad}), 1)
        self.assertEqual(len(seen), 500)
        roster = read(ROOT / configs.PACK / 'roster.json')
        self.assertEqual([r['model_id'] for r in roster['models'] if r['role'] == 'fit'],
                         ['qwen3-1p7b', 'qwen3-4b', 'qwen3-8b'])
        self.assertEqual(roster['workload']['decode_forward_passes'], 512)
        self.assertEqual(next(r for r in roster['models'] if r['model_id'] == 'qwen3-8b-8bit')['model']['revision'],
                         '48a0b75b1ae72503e21e1558d040bc227510ff06')

    def test_generators_reproduce_committed_bytes_and_write_only_allowed_paths(self):
        first = configs.generate(check=True)
        second = plans.generate(check=True)
        for path in first:
            self.assertTrue(path.is_relative_to(configs.PACK))
        for path in second:
            self.assertTrue(path.is_relative_to(Path('configs/b6/packs'))
                            or path.is_relative_to(Path('configs/campaigns'))
                            or path.as_posix() in ('configs/b6/smoke_keep.json', 'configs/b6/loop.json'))
        with tempfile.TemporaryDirectory() as tmp:
            configs.generate(tmp)
            plans.generate(tmp)
            for path, raw in {**first, **second}.items():
                self.assertEqual((Path(tmp) / path).read_bytes(), raw)


class BytesPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog(ROOT / 'configs/b6/flag_catalog_b6.json')

    def test_twelve_drafts_preserve_ruled_stopping_and_expose_validator_gap(self):
        for n in range(1, 7):
            for pass_number in (1, 2):
                with self.subTest(subpack=n, pass_number=pass_number):
                    reg = load(ROOT / f'configs/b6/packs/bytes-s{n}-p{pass_number}/registration.json')
                    self.assertEqual(validate(reg, self.catalog, root=ROOT), [])
                    expected = 'registered'  # pass 1 gate 2026-10-25; pass 2 §21
                    self.assertEqual((reg.status, reg.kind, reg.session_shape), (expected, 'new', 'fixed'))
                    self.assertEqual((reg.target_sessions, reg.minimum_sessions), (1, 1))
                    self.assertEqual(reg.corpus, {'planned': 18, 'stop_after_valid': 12})
                    self.assertEqual(reg.stopping, {'count': 1, 'end_t0_before': '2026-11-05T00:00:00-08:00', 'precision': None})
                    self.assertEqual(reg.blinding_group, 'bytes')
                    self.assertEqual(reg.blinding, {'hidden_offset': True})
                    self.assertEqual(reg.interleave, 'none')
                    expected = ['bytes-' + m for m in plans.GROUPS[n - 1]]
                    self.assertEqual([m['module_id'] for m in reg.modules], expected if pass_number == 1 else expected[::-1])
                    self.assertNotIn('pass_plan_tree_refs', reg.data)
                    for code in self.catalog.codes:
                        self.assertEqual(reg.flag_effects[code], 'DISCLOSE' if code == 'cell.below_minimum'
                                         else self.catalog.entry(code)['effect'])
                    self.assertEqual(reg.flag_effects['thermal.os_level_nonzero'], 'EXCLUDE_MEMBER')
                    self.assertEqual(reg.flag_effects['thermal.powermetrics_pressure_elevated'], 'EXCLUDE_MEMBER')

    def test_estimators_name_the_analysis_stage_functions_with_the_agreeing_version(self):
        from joulewise import bytes_analysis
        agreeing_sha = hashlib.sha256((ROOT / 'joulewise/bytes_analysis.py').read_bytes()).hexdigest()
        for n in range(1, 7):
            for pass_number in (1, 2):
                with self.subTest(subpack=n, pass_number=pass_number):
                    reg = load(ROOT / f'configs/b6/packs/bytes-s{n}-p{pass_number}/registration.json')
                    expected = deepcopy(plans.ESTIMATORS)
                    for entry in expected:
                        entry['version'] = agreeing_sha
                    self.assertEqual(reg.data['estimators'], expected)
                    for entry in reg.data['estimators']:
                        self.assertTrue(callable(getattr(bytes_analysis, entry['function'])))
                        self.assertEqual(entry['version'], agreeing_sha)
                    self.assertEqual(reg.status, 'registered')
                    self.assertNotIn('draft_notes', reg.data)

    def test_registration_prose_lists_every_slot_and_maps_every_ruling_item(self):
        import re
        text = (ROOT / 'docs/registrations/bytes_pack_v1.md').read_text(encoding='utf-8')
        body, slots = text.split('\n## 18. Marked slots\n')
        slots, mapping = slots.split('\n## 19. ')[0], slots.split('\n## 20. ')[1]
        # The header's convention examples read '⟦MAC: …⟧'; every other slot names its value.
        used = set(re.findall(r'⟦(?:MAC|B2|B4): [^⟧]*⟧', body)) - {'⟦MAC: …⟧', '⟦B2: …⟧', '⟦B4: …⟧'}
        self.assertTrue(used)
        self.assertEqual(sorted(s for s in used if s not in slots), [])
        rows = [line.split('|')[1].strip() for line in mapping.splitlines() if line.startswith('| ')]
        for item in [f'R{i}' for i in range(1, 9)] + [f'Add. {i}' for i in range(1, 9)]:
            self.assertTrue(any(re.match(re.escape(item) + r'\b', row) for row in rows), item)


    def test_both_pass_trees_read_round_trip_and_keep_whole_modules_at_midpoint(self):
        for n in range(1, 7):
            for pass_number in (1, 2):
                with self.subTest(subpack=n, pass_number=pass_number):
                    reg = load(ROOT / f'configs/b6/packs/bytes-s{n}-p{pass_number}/registration.json')
                    path = reg.plan_tree_ref
                    layout = compose.layout(queue.Selection((reg.pack_id,), pass_number), {reg.pack_id: reg}, ROOT)
                    self.assertEqual(layout.campaign_id, reg.pack_id)
                    tree, files = compose.render(layout)
                    self.assertEqual(files['plan_tree.json'], (ROOT / path).read_bytes())
                    self.assertEqual(len(chain.stage_plan(tree)), len(tree['stage_graph']))
                    expected = ['bytes-' + m for m in plans.GROUPS[n - 1]]
                    if pass_number == 2:
                        expected.reverse()
                    self.assertEqual(tree['module_order'], expected)
                    science = [s for s in layout.stages if s['stage_id'].startswith('bytes-') and any(
                        s['stage_id'].startswith(module + '-') for module in expected)]
                    self.assertEqual([s['expected_count'] for s in science], [10, 20, 20] * len(expected))
                    actual_order = [row['module_id'] for row in tree['science']]
                    self.assertEqual(actual_order, [module for module in expected for _ in range(50)])
                    midpoint = next(i for i, s in enumerate(layout.stages) if s['stage_id'].endswith('-reference-midpoint'))
                    before = sum(len(s['entries']) for s in layout.stages[:midpoint] if s in science)
                    self.assertEqual(before, 50 if len(expected) == 2 else 30)
                    corpus = next(s for s in layout.stages if s['stage_id'].endswith('-bound-collection'))
                    self.assertEqual((corpus['expected_count'], len(corpus['entries'])), (18, 18))
                    self.assertEqual(corpus['corpus'], {'planned': 18, 'stop_after_valid': 12})
                    self.assertEqual(tree['b6_layout']['corpus'], reg.corpus)
                    for stage in layout.stages:
                        if not stage['entries']:
                            continue
                        manifest_path = ROOT / stage['input']['path']
                        self.assertEqual(hashlib.sha256(manifest_path.read_bytes()).hexdigest(), stage['input']['sha256'])
                        for entry in stage['entries']:
                            config = ROOT / entry['config_path']
                            self.assertTrue(config.is_file())
                            self.assertEqual(hashlib.sha256(config.read_bytes()).hexdigest(), entry['config_sha256'])
                    collection = read(ROOT / Path(path).parent / tree['plan']['path'])
                    self.assertEqual(collection['plan_id'], reg.pack_id)
                    self.assertEqual(collection['science'], tree['science'])
                    self.assertEqual(tree['plan']['actual_sha256'], hashlib.sha256(
                        (ROOT / Path(path).parent / tree['plan']['path']).read_bytes()).hexdigest())
                    bindings = {arg['value']: '/synthetic/' + arg['value']
                                for stage in tree['stage_graph'] for command in stage['launch']['commands']
                                for arg in command['argv_template']['arguments'] if arg['kind'] in ('binding', 'binding_path')}
                    for stage in chain.stage_plan(tree):
                        chain.stage_argv(stage, bindings, tree, ROOT)
                    self.assertNotIn('d117_floor_qwen3-8b_v5/calibration_plan.json', json.dumps(tree))
                    self.assertEqual(tree['downstream_contract']['extraction_spec']['sha256'], hashlib.sha256(
                        (ROOT / Path(path).parent / 'extraction_spec.json').read_bytes()).hexdigest())

    def test_pass_two_reverses_subpack_order_without_changing_replication_order(self):
        order = read(ROOT / configs.PACK / 'pass_order.json')
        self.assertEqual(order['passes']['1'], [f'bytes-s{n}-p1' for n in range(1, 7)])
        self.assertEqual(order['passes']['2'], [f'bytes-s{n}-p2' for n in range(6, 0, -1)])
        self.assertEqual(order['blinding_group'], 'bytes')
        self.assertIn('replication and GAMMA order unchanged', order['interleaving'])

    def test_loop_selects_each_pass_tree_once_in_registered_order(self):
        # Adapt the executing review's second-session probe: use the actual
        # queue and fixed-layout reader with structure-only counting outcomes.
        loop = read(ROOT / 'configs/b6/loop.json')
        ids = [f'bytes-s{n}-p1' for n in range(1, 7)] + [f'bytes-s{n}-p2' for n in range(6, 0, -1)]
        self.assertEqual(loop['base_order'], ['alpha', 'beta', 'gamma'] + ids)
        regs = {p: load(ROOT / f'configs/b6/packs/{p}/registration.json') for p in ids}
        state = {'round': 1, 'slots': {}, 'base_order': loop['base_order'], 'attempts': []}
        now = 1_792_000_000  # before the registered deadline
        for p in ids:
            selection = queue.next_session(state, regs, now)
            self.assertIsInstance(selection, queue.Selection)
            self.assertEqual(selection.packs, (p,))
            layout = compose.layout(selection, regs, ROOT)
            tree = compose.render(layout)[0]
            self.assertEqual(tree['bytes_pass'], regs[p].bytes_pass)
            self.assertEqual(tree['module_order'], [m['module_id'] for m in regs[p].modules])
            self.assertEqual(layout.campaign_id, p)
            state = queue.consume(state, selection)
            state['attempts'].append({'session_id': layout.session_id, 'packs': [p],
                                      'outcomes': {p: {'status': 'counting', 'cause': None}}})
            self.assertEqual(queue.done_reason(state, regs[p], now), 'target')
        self.assertIsInstance(queue.next_session(state, regs, now), queue.Close)

    def test_fixed_driver_campaign_paths_and_smoke_keep_reach_sizing(self):
        from joulewise.b6 import plan_inputs, registration
        sizing_path = ROOT / 'configs/b6/registration/sizing_b5.json'
        sized = registration.load_sizing(sizing_path.parent)
        identities = {name: {'path': '/synthetic/' + name, 'sha256': 'a' * 64}
                      for name in ('identity-epoch.json', 't1-bindings.json')}
        self.assertEqual({p for p in sized['packs'] if p.startswith('bytes-')},
                         {f'bytes-s{n}-p{q}' for n in range(1, 7) for q in (1, 2)})
        # Registration §21 item 1: each pass-2 row is its pass-1 row with only the pack id changed.
        for n in range(1, 7):
            row = dict(sized['packs'][f'bytes-s{n}-p2'], pack_id=f'bytes-s{n}-p1')
            self.assertEqual(row, sized['packs'][f'bytes-s{n}-p1'])
        for n in range(1, 7):
            for pass_number in (1, 2):
                p = f'bytes-s{n}-p{pass_number}'
                with self.subTest(pack=p):
                    reg = load(ROOT / f'configs/b6/packs/{p}/registration.json')
                    layout = compose.layout(queue.Selection((p,), pass_number), {p: reg}, ROOT)
                    campaign = ROOT / 'configs/campaigns' / layout.campaign_id
                    self.assertEqual(campaign / 'plan_tree.json', ROOT / reg.plan_tree_ref)
                    self.assertTrue((campaign / 'plan_tree.json').is_file())
                    expected = {f'{p}-reference-start': 1,
                                **{m['module_id'] + '-absolute': 1 for m in reg.modules},
                                f'{p}-reference-end': 1}
                    self.assertEqual(compose.smoke_keep(layout), expected)
                    inputs = plan_inputs.build(ROOT, sizing_path.parent, p, layout.session_id, identities,
                                               custody_root='/x', runs_parent='/x', claim_backup='/x',
                                               bound_backup='/x', head='a' * 40)
                    row = sized['packs'][p]
                    for key in ('programmed_span_s', 'T_stream_max_s'):
                        self.assertEqual(inputs[key], {'seconds': row[key],
                            'source': {'path': sizing_path.relative_to(ROOT).as_posix(),
                                       'sha256': hashlib.sha256(sizing_path.read_bytes()).hexdigest()},
                            'source_pointer': f'/packs/{p}/{key}'})
                    self.assertEqual(inputs['pack_root'], str(campaign))
                    self.assertEqual(inputs['disk_budget']['member_count'], 125 if n <= 4 else 75)
                    self.assertEqual(inputs['disk_budget']['required_free_bytes'],
                                     row['disk_derivation']['required_free_bytes'])
                    self.assertEqual(inputs['disk_budget']['derivation'], row['disk_derivation'])


class BytesHarvestAcceptanceTests(unittest.TestCase):
    def test_all_pass_rosters_and_registered_stratum_minimum(self):
        from collections import Counter
        from dataclasses import replace
        from joulewise.b5.harvest import build_roster, l4_exclusion_inputs
        from joulewise.b6.acceptance import ACCEPTANCE
        from joulewise.b6 import precheck
        from tests.b6.support import IDENTITY
        for n in range(1, 7):
            for p in (1, 2):
                pack = ROOT / f'configs/campaigns/bytes-s{n}-p{p}'
                with self.subTest(pack=pack.name):
                    roster = build_roster(pack, ROOT)
                    census = Counter(m['role'] for m in roster['members'])
                    models = len(plans.GROUPS[n - 1])
                    self.assertEqual(census, {'absolute_repeat': 10 * models,
                        'comparative_abba_member': 40 * models, 'neg8_bound': 18,
                        'start_reference': 3, 'midpoint_reference': 1, 'end_reference': 3})
                    l4, _ = l4_exclusion_inputs(roster, {}, plan_id=None, attempt=None)
                    self.assertEqual(len(l4['cells']), models)
                    for cell in l4['cells']:
                        self.assertEqual(cell['strata'], ['quad', 'repeat'])
                        for stratum in cell['strata']:
                            units = {u['unit_id'] for m in l4['members'] for u in m['units']
                                     if u['cell_id'] == cell['cell_id'] and u['stratum'] == stratum}
                            self.assertEqual(len(units), 10)  # registration §6: ten planned units per stratum
                    print(pack.name, dict(census), l4['cells'], '10 repeat + 10 quad units per model')
                    prepared = ACCEPTANCE.prepare(ledger_path=Path('/nonexistent-synthetic-ledger'),
                        plan_tree=read(pack / 'plan_tree.json'), registration_dir=ROOT / 'configs/b6/registration',
                        code_identity={'repo_root': str(ROOT)}, pack_root=pack, ledger_rows=[])
                    rows = [{'disposition': 'valid', 'sequence': i, 'exact_bound_lexeme_s':
                             prepared.registration['calibration']['acceptance_corpus'][0]} for i in range(24)]
                    runtime = {**IDENTITY, 'packages': prepared.expected_model['runtime_versions']['packages']}
                    evidence = precheck.synthetic_session(pack, ROOT, rows, runtime)
                    nominal = ACCEPTANCE.evaluate(prepared, evidence)
                    self.assertEqual(nominal.verdict, 'ACCEPT')
                    quads = [m for m in roster['members'] if m['role'] == 'comparative_abba_member']
                    first = quads[0]
                    model = first['run_id'].split('-null-')[0]
                    block_ids = list(dict.fromkeys(m['block_id'] for m in quads if m['run_id'].startswith(model + '-null-')))
                    for lost, verdict in (({first['run_id']}, 'ACCEPT'),
                        ({m['run_id'] for m in quads if m['run_id'].startswith(model + '-null-')
                          and m['block_id'] in block_ids[:6]}, 'ACCEPT')):
                        altered = replace(evidence, stages=tuple(replace(s, members=tuple(
                            replace(m, status='failed') if m.run_id in lost else m for m in s.members))
                            for s in evidence.stages))
                        result = ACCEPTANCE.evaluate(prepared, altered)
                        self.assertEqual(result.verdict, verdict)
                        self.assertEqual(result.counting, verdict == 'ACCEPT')
                        self.assertNotIn('cell.below_minimum', result.reasons)
                        if len(lost) > 1:
                            self.assertIn('cell.below_minimum', result.flags)
                        print(pack.name, 'lost members', len(lost), result.verdict, result.counting, result.reasons)
