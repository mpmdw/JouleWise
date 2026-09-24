"""Named paths and typed refusals for the A291 scored packer."""
import ast
import copy
import inspect
import unittest

from joulewise import scored_packer as sp, scored_registration as sr
from tests.scored_roster_checker import check_roster, check_transition, check_executed
from tests.test_scored_registration import fixture
from tests.test_scored_packer_stress import run_case
import random


class ScoredPackerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.edge_counts = {}
        for mode in range(8):
            cls.edge_counts[mode] = run_case(mode, random.Random(291013))[0]

    def test_p_pack_root_checker(self):
        g, p = fixture()
        reg = sr.Registration.from_mapping(g)
        roster = sp.pack(reg, p)
        self.assertEqual(check_roster(g, roster, p), [])
        self.assertEqual(roster['sha256'], roster['registered_sha256'])
        self.assertEqual(roster['events'], [])

    def test_e1_initial_whole_block(self): self.assertGreater(self.edge_counts[0]['E1'], 0)
    def test_e2_initial_reschedule(self): self.assertGreater(self.edge_counts[0]['E2'], 0)
    def test_e3_initial_unattributed(self): self.assertGreater(self.edge_counts[1]['E3'], 0)
    def test_e4_whole_split(self): self.assertGreater(self.edge_counts[0]['E4'], 0)
    def test_e5_whole_unattributed(self): self.assertGreater(self.edge_counts[2]['E5'], 0)
    def test_e6_single_problem_retry(self): self.assertGreater(self.edge_counts[0]['E6'], 0)
    def test_e7_single_problem_reschedule(self): self.assertGreater(self.edge_counts[7]['E7'], 0)
    def test_e8_single_retry_ceiling(self): self.assertGreater(self.edge_counts[0]['E8'], 0)
    def test_e9_single_retry_reschedule(self): self.assertGreater(self.edge_counts[6]['E9'], 0)
    def test_e10_single_problem_unattributed(self): self.assertGreater(self.edge_counts[3]['E10'], 0)
    def test_e11_single_retry_unattributed(self): self.assertGreater(self.edge_counts[4]['E11'], 0)

    def test_r_verify_and_executed(self):
        g, p = fixture()
        reg = sr.Registration.from_mapping(g)
        roster = sp.pack(reg, p)
        self.assertEqual(check_roster(g, roster, p), [])
        for e in list(roster['envelopes']):
            if e['kind'] != 'loaded':
                continue
            current = next(x for x in roster['envelopes'] if x['index'] == e['index'])
            obs = [dict(block_id=bid, status='completed', elapsed_s=.1) for bid in current['blocks']]
            prior = roster
            roster = sp.requeue_overrun(reg, roster, current['index'], obs)
            self.assertEqual(check_roster(g, roster, p), [])
            self.assertEqual(check_transition(g, prior, roster, p), [])
        self.assertIsNone(sp.verify_executed_roster(reg, roster, p))
        keys = {(pl['block_id'], pl['attempt']) for pl in roster['placements']}
        value = sp.executed_status(reg, roster, p, keys)
        self.assertFalse(any(value['spread_exceeded'].values()))

    def test_inv50_role_mapping_permutation(self):
        g, p = fixture()
        reordered = copy.deepcopy(g)
        reordered['role_to_model_id'] = {'1.7B': 'small', '8B': 'large'}
        a = sp.pack(sr.Registration.from_mapping(g), p)
        b = sp.pack(sr.Registration.from_mapping(reordered), p)
        self.assertEqual(a, b)
        self.assertEqual(check_roster(g, a, p), [])
        self.assertEqual(check_roster(reordered, b, p), [])

    def test_inv39_tampered_root_repack_refused(self):
        g, p = fixture()
        reg = sr.Registration.from_mapping(g)
        root = sp.pack(reg, p)
        self.assertEqual(check_roster(g, root, p), [])
        bad = copy.deepcopy(root)
        same = [e for e in bad['envelopes'] if e['kind'] == 'loaded' and e['model'] == 'large']
        a, b = same[0], same[1]
        ids_a, ids_b = list(a['blocks']), list(b['blocks'])
        a['blocks'], b['blocks'] = ids_b, ids_a
        for placement in bad['placements']:
            if placement['block_id'] in ids_a:
                placement['envelope_index'] = b['index']
            elif placement['block_id'] in ids_b:
                placement['envelope_index'] = a['index']
        bad['placements'].sort(key=lambda placement: placement['envelope_index'])
        bad['planned_spread_shortfall'], bad['drift_lever_slots'] = sp._derived(reg, bad)
        bad['sha256'] = None
        sp._seal(reg, bad, finalize=True)
        self.assertEqual(check_roster(g, bad, p), [])
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.verify_executed_roster(reg, bad, p)
        self.assertEqual(caught.exception.code, 'inv_39')

    def test_inv40_ast_seal_placement(self):
        tree = ast.parse(inspect.getsource(sp))
        functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        for name in ('pack', 'requeue_overrun'):
            returns = [n for n in ast.walk(functions[name]) if isinstance(n, ast.Return)]
            self.assertTrue(returns)
            for node in returns:
                self.assertIsInstance(node.value, ast.Call)
                self.assertIsInstance(node.value.func, ast.Name)
                self.assertEqual(node.value.func.id, '_seal')
        for name in ('requeue_overrun', 'verify_executed_roster'):
            first = functions[name].body[0]
            self.assertIsInstance(first.value, ast.Call)
            self.assertEqual(first.value.func.id, '_seal')
        callers = [fn.name for fn in functions.values() if fn.name != '_seal' for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == '_digest']
        self.assertEqual(callers, [])
        self.assertIn('_digest', [n.func.id for n in ast.walk(functions['_seal']) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)])

    def test_inv44_constants_are_module_pinned(self):
        self.assertEqual(sr.LEVELS, [1, 2, 3, 4, 5])
        self.assertEqual(sr.MERGE_ORDER, [[5, 4], [4, 3], [1, 2], [2, 3]])
        self.assertEqual((sr.MIN_CORRECT, sr.HOLM_M, sr.CAP_BOUND_FRACTION), (3, 5, .20))
        source = inspect.getsource(sp)
        self.assertNotIn('0.20', source)
        self.assertNotIn('[[5, 4]', source)
        self.assertNotIn('"joulewise.scored_roster.v3"', source)

    def test_typed_pack_refusals(self):
        g, p = fixture()
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.pack(g, p)
        self.assertEqual(caught.exception.code, 'inv_51')
        cases = []
        badp = copy.deepcopy(p); badp['large'].pop(next(iter(badp['large'])))
        cases.append((g, badp, 'inv_07'))
        badp = copy.deepcopy(p); badp['large'][next(iter(badp['large']))] = 1.1
        cases.append((g, badp, 'inv_07'))
        badp = copy.deepcopy(p); badp['large'][next(iter(badp['large']))] = .7
        cases.append((g, badp, 'inv_08'))
        badg, badp = fixture(n=4)
        cases.append((badg, badp, 'spread_minima'))
        badg, badp = fixture(block_size=2, n=10, cap=1.0)
        cases.append((badg, badp, 'inv_20'))
        badg, badp = fixture(); badg['budget_j'] = 0
        cases.append((badg, badp, 'inv_28'))
        for regmap, pred, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(sp.PackingRefusal) as caught:
                    sp.pack(sr.Registration.from_mapping(regmap), pred)
                self.assertEqual(caught.exception.code, code)

    def test_typed_report_refusals(self):
        g, p = fixture()
        reg = sr.Registration.from_mapping(g)
        root = sp.pack(reg, p)
        self.assertEqual(check_roster(g, root, p), [])
        e = next(e for e in root['envelopes'] if e['kind'] == 'loaded')
        valid = [dict(block_id=bid, status='completed', elapsed_s=.1) for bid in e['blocks']]
        variants = [
            (len(root['envelopes']) + 1, valid, 'report_order'),
            (e['index'], valid[:-1], 'inv_29'),
            (e['index'], [dict(x, elapsed_s=0) for x in valid], 'invalid_elapsed'),
            (e['index'], [dict(x, elapsed_s=reg.interior_s) for x in valid], 'invalid_elapsed'),
        ]
        if len(valid) >= 2:
            order = copy.deepcopy(valid); order[0]['status'] = 'not_started'; order[0]['elapsed_s'] = None
            variants.append((e['index'], order, 'invalid_observation_order'))
        for index, obs, code in variants:
            with self.subTest(code=code):
                with self.assertRaises(sp.PackingRefusal) as caught:
                    sp.requeue_overrun(reg, root, index, obs)
                self.assertEqual(caught.exception.code, code)

    def test_typed_seal_and_reduce_refusals(self):
        g, p = fixture()
        reg = sr.Registration.from_mapping(g)
        root = sp.pack(reg, p)
        self.assertEqual(check_roster(g, root, p), [])
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.verify_executed_roster(reg, root, p)
        self.assertEqual(caught.exception.code, 'unreported_envelope')
        bad = copy.deepcopy(root)
        bad['blocks'][0]['items'] = None
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.requeue_overrun(reg, bad, 0, [])
        self.assertEqual(caught.exception.code, 'inv_52')
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.executed_status(reg, root, p, [])
        self.assertEqual(caught.exception.code, 'unreported_envelope')
        cases = [
            (lambda x: x.update(unknown=1), 'inv_03'),
            (lambda x: x.update(registration_sha256='0'*64), 'inv_01'),
            (lambda x: x.update(n_per_level=1), 'inv_04'),
            (lambda x: x.update(claim_ready=False), 'inv_05'),
            (lambda x: x['drift_lever_slots'].update({'1': 999}), 'stale_derived'),
            (lambda x: x['placements'][0].update(reserved_s=.2), 'inv_02'),
        ]
        for mutate, code in cases:
            with self.subTest(code=code):
                bad = copy.deepcopy(root)
                mutate(bad)
                with self.assertRaises(sp.PackingRefusal) as caught:
                    sp.requeue_overrun(reg, bad, 0, [])
                self.assertEqual(caught.exception.code, code)

    def test_typed_event_digest_and_window_key_refusals(self):
        g, p = fixture()
        reg = sr.Registration.from_mapping(g)
        roster = sp.pack(reg, p)
        while any(e['kind'] == 'loaded' and e['observations'] is None for e in roster['envelopes']):
            e = next(e for e in roster['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None)
            observations = [dict(block_id=bid, status='completed', elapsed_s=.1) for bid in e['blocks']]
            roster = sp.requeue_overrun(reg, roster, e['index'], observations)
            self.assertEqual(check_roster(g, roster, p), [])
        bad = copy.deepcopy(roster)
        bad['events'][-1]['sha256'] = '0' * 64
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.verify_executed_roster(reg, bad, p)
        self.assertEqual(caught.exception.code, 'inv_38')
        earlier = copy.deepcopy(roster)
        earlier['events'][0]['sha256'] = '0' * 64
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.requeue_overrun(reg, earlier, 0, [])
        self.assertEqual(caught.exception.code, 'inv_38')
        unsealed = copy.deepcopy(roster)
        unsealed['sha256'] = None
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.requeue_overrun(reg, unsealed, 0, [])
        self.assertEqual(caught.exception.code, 'inv_02')
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.executed_status(reg, roster, p, {('bad', True)})
        self.assertEqual(caught.exception.code, 'inv_52')

    def test_checker_executed_voided_attempt_counterexample(self):
        g, p = fixture(n=5, cap=6.0)
        reg = sr.Registration.from_mapping(g)
        roster = sp.pack(reg, p)
        first = next(e for e in roster['envelopes'] if e['kind'] == 'loaded')
        observations = [dict(block_id=bid, status='completed' if j == 0 else 'not_started', elapsed_s=.7 if j == 0 else None) for j, bid in enumerate(first['blocks'])]
        roster = sp.requeue_overrun(reg, roster, first['index'], observations)
        self.assertEqual(check_roster(g, roster, p), [])
        rescheduled = roster['events'][0]['observations'][1]['block_id']
        self.assertEqual(roster['events'][0]['observations'][1]['decision'], 'reschedule')
        while any(e['kind'] == 'loaded' and e['observations'] is None for e in roster['envelopes']):
            e = next(e for e in roster['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None)
            obs = [dict(block_id=bid, status='completed', elapsed_s=.1) for bid in e['blocks']]
            roster = sp.requeue_overrun(reg, roster, e['index'], obs)
            self.assertEqual(check_roster(g, roster, p), [])
        live = {bid for e in roster['envelopes'] for bid in e['blocks']}
        keys = {(x['block_id'], x['attempt']) for x in roster['placements'] if x['block_id'] in live and x['block_id'] != rescheduled}
        keys.add((rescheduled, 0))  # Its voided attempt is captured; the live attempt is not.
        actual = sp.executed_status(reg, roster, p, keys)
        oracle = check_executed(g, roster, p, keys)
        self.assertNotIn('violations', oracle)
        cell = f"large:{next(b['level'] for b in roster['blocks'] if b['block_id'] == rescheduled)}"
        self.assertTrue(actual['spread_exceeded'][cell])
        self.assertFalse(oracle['spread_exceeded'][cell])

    def test_typed_static_invariant_refusals(self):
        g, p = fixture(n=5)
        reg = sr.Registration.from_mapping(g)
        root = sp.pack(reg, p)
        self.assertEqual(check_roster(g, root, p), [])
        def empty_loaded(x):
            ids = set(x['envelopes'][0]['blocks'])
            x['envelopes'][0]['blocks'] = []
            x['placements'] = [pl for pl in x['placements'] if pl['block_id'] not in ids]
        def occupied_idle(x):
            idle = next(e for e in x['envelopes'] if e['kind'] == 'idle_slot')
            bid = next(e['blocks'][0] for e in x['envelopes'] if e['model'] == idle['model'] and e['kind'] == 'loaded')
            idle['blocks'].append(bid)
            pl = next(pl for pl in x['placements'] if pl['block_id'] == bid)
            x['placements'].append(dict(pl, envelope_index=idle['index']))
        cases = [
            (lambda x: x['blocks'][1].update(block_id=x['blocks'][0]['block_id']), 'inv_10'),
            (lambda x: x['blocks'][0].update(predicted_s=.5), 'inv_21'),
            (lambda x: x['envelopes'][0].update(index=99), 'inv_17'),
            (empty_loaded, 'inv_15'),
            (occupied_idle, 'inv_16'),
            (lambda x: x['envelopes'][0].update(model='small'), 'inv_14'),
            (lambda x: next(b for b in x['blocks'] if b['block_id'] == x['envelopes'][0]['blocks'][1]).update(level=1), 'inv_24'),
        ]
        for mutate, code in cases:
            with self.subTest(code=code):
                bad = copy.deepcopy(root)
                mutate(bad)
                with self.assertRaises(sp.PackingRefusal) as caught:
                    sp._seal(reg, bad)
                self.assertEqual(caught.exception.code, code)

    def test_typed_event_invariant_refusals(self):
        g, p = fixture(n=5)
        reg = sr.Registration.from_mapping(g)
        root = sp.pack(reg, p)
        self.assertEqual(check_roster(g, root, p), [])
        e = root['envelopes'][0]
        observations = [dict(block_id=bid, status='completed' if j == 0 else 'not_started', elapsed_s=.7 if j == 0 else None) for j, bid in enumerate(e['blocks'])]
        reported = sp.requeue_overrun(reg, root, 0, observations)
        self.assertEqual(check_roster(g, reported, p), [])
        def edit_obs(x, change):
            change(x['events'][0]['observations'])
            x['envelopes'][0]['observations'] = copy.deepcopy(x['events'][0]['observations'])
        def remove_culprit(x):
            edit_obs(x, lambda obs: obs[0].update(elapsed_s=.1))
        def too_many_reschedules(x):
            edit_obs(x, lambda obs: obs[0].update(decision='reschedule'))
        def duplicate_culprit(x):
            def change(obs):
                obs[1].update(block_id=obs[0]['block_id'], status='completed', elapsed_s=.7, decision='keep')
                for later in obs[2:]:
                    later.update(status='not_started', elapsed_s=None)
            edit_obs(x, change)
            x['events'][0]['block_ids'][1] = x['events'][0]['block_ids'][0]
        cases = [
            (remove_culprit, 'reschedule_without_culprit'),
            (too_many_reschedules, 'inv_35c'),
            (duplicate_culprit, 'culprit_limit'),
            (lambda x: x['events'][0].update(placements=[0]), 'inv_18'),
        ]
        for mutate, code in cases:
            with self.subTest(code=code):
                bad = copy.deepcopy(reported)
                mutate(bad)
                with self.assertRaises(sp.PackingRefusal) as caught:
                    sp._seal(reg, bad)
                self.assertEqual(caught.exception.code, code)
