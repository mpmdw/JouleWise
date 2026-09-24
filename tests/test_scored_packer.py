"""Named paths and typed refusals for the A291 scored packer."""
import ast
import copy
import inspect
import unittest
from unittest.mock import patch

from joulewise import scored_packer as sp, scored_registration as sr
from tests.scored_roster_checker import check_roster, check_transition, check_executed, digest
from tests.test_scored_registration import fixture
from tests.test_scored_roster_checker import r2_four_envelope_roster
from tests.test_scored_packer_stress import run_case
import random


def reseal(r):
    d = digest(r)
    r["sha256"] = d
    (r["events"][-1].__setitem__("sha256", d) if r["events"] else r.__setitem__("registered_sha256", d))
    return r


def _detail(exc):
    return str(exc).partition(": ")[2]


def _split_route():
    g, p = fixture(n=10, block_size=2, cap=6.0)
    reg = sr.Registration.from_mapping(g)
    roster = sp.pack(reg, p)
    first = roster['envelopes'][0]
    roster = sp.requeue_overrun(reg, roster, 0, [
        dict(block_id=bid, status='cut_off' if j == 0 else 'not_started',
             elapsed_s=1.3 if j == 0 else None)
        for j, bid in enumerate(first['blocks'])])
    while not any(o['decision'] == 'split' for o in roster['events'][-1]['observations']):
        envelope = next(e for e in roster['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None)
        stages = {b['block_id']: b['retry_stage'] for b in roster['blocks']}
        whole = any(stages[bid] == 'whole_block' for bid in envelope['blocks'])
        observations = [dict(block_id=bid, status='cut_off' if whole else 'completed',
                             elapsed_s=.1 if whole else .01) for bid in envelope['blocks']]
        roster = sp.requeue_overrun(reg, roster, envelope['index'], observations)
    return g, p, reg, roster


def _missing_live_roster():
    g, p = fixture(n=10, block_size=2, cap=6.0)
    reg = sr.Registration.from_mapping(g)
    r = sp.pack(reg, p)
    model = g['role_to_model_id']['8B']
    targets = {b['block_id'] for b in r['blocks'] if b['model'] == model and b['level'] == 1}
    for envelope in r['envelopes']:
        moved = [bid for bid in envelope['blocks'] if bid in targets]
        envelope['blocks'] = [bid for bid in envelope['blocks'] if bid not in targets]
        envelope['voided_block_ids'].extend(moved)
    pending = next(e for e in r['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None)
    all_keep = [dict(block_id=bid, status='completed', elapsed_s=.01) for bid in pending['blocks']]
    return reg, r, pending['index'], all_keep


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
        reseal(bad)
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
                if code == 'stale_derived':
                    reseal(bad)
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
        self.assertEqual(actual, oracle)
        self.assertTrue(oracle['spread_exceeded'][cell])

    def test_r2_partly_terminal_parent_planned_position(self):
        g, roster, predictions = r2_four_envelope_roster()
        reg = sr.Registration.from_mapping(g)
        self.assertEqual(check_roster(g, roster, predictions), [])
        shortfall, lever = sp._derived(reg, roster)
        # Two live singles of parent 0 occupy envelope 56. The other big
        # parents occupy 1..4; the small parents occupy 5..9.
        expected = abs(sum([56, 1, 2, 3, 4]) / 5 - sum([5, 6, 7, 8, 9]) / 5)
        self.assertEqual(expected, 6.199999999999999)
        self.assertEqual(lever['1'], expected)
        self.assertEqual(roster['drift_lever_slots']['1'], expected)
        self.assertTrue(shortfall['big:1'])
        self.assertEqual(shortfall, roster['planned_spread_shortfall'])

    def test_executed_partly_counted_parent_position(self):
        g, predictions = fixture(n=10, block_size=2, cap=6.0)
        reg = sr.Registration.from_mapping(g)
        roster = sp.pack(reg, predictions)
        first = roster['envelopes'][0]
        observations = [dict(block_id=bid, status='cut_off' if j == 0 else 'not_started',
                             elapsed_s=1.3 if j == 0 else None)
                        for j, bid in enumerate(first['blocks'])]
        roster = sp.requeue_overrun(reg, roster, 0, observations)
        while any(e['kind'] == 'loaded' and e['observations'] is None for e in roster['envelopes']):
            envelope = next(e for e in roster['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None)
            stages = {b['block_id']: b['retry_stage'] for b in roster['blocks']}
            whole = any(stages[bid] == 'whole_block' for bid in envelope['blocks'])
            observations = [dict(block_id=bid, status='cut_off' if whole else 'completed',
                                 elapsed_s=.1 if whole else .01) for bid in envelope['blocks']]
            roster = sp.requeue_overrun(reg, roster, envelope['index'], observations)
        self.assertEqual(check_roster(g, roster, predictions), [])
        keys = {(p['block_id'], p['attempt']) for p in roster['placements']
                if p['block_id'] in roster['envelopes'][p['envelope_index']]['blocks']}
        keys.remove(('large:decode:1:0:single:0', 2))
        actual = sp.executed_status(reg, roster, predictions, keys)
        expected = abs(sum([13, 2, 4, 6, 8]) / 5 - sum([1, 3, 5, 7, 9]) / 5)
        self.assertEqual(actual['executed_drift_lever_slots']['1'], expected)
        self.assertTrue(actual['spread_exceeded']['large:1'])
        self.assertEqual(actual, check_executed(g, roster, predictions, keys))

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
                reseal(bad)
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
                reseal(bad)
                with self.assertRaises(sp.PackingRefusal) as caught:
                    sp._seal(reg, bad)
                self.assertEqual(caught.exception.code, code)

    def test_r1_duplicate_live_placement(self):
        g, p = fixture(n=10, block_size=2, cap=6.0)
        reg = sr.Registration.from_mapping(g)
        r = sp.pack(reg, p)
        placement0 = r['placements'][0]
        n = len(r['envelopes'])
        block = next(b for b in r['blocks'] if b['block_id'] == placement0['block_id'])
        r['envelopes'].append(dict(index=n, model=block['model'], kind='loaded',
                                   blocks=[placement0['block_id']], voided_block_ids=[], observations=None))
        r['placements'].append(dict(placement0, envelope_index=n))
        reseal(r)
        pending = next(e for e in r['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None)
        all_keep = [dict(block_id=bid, status='completed', elapsed_s=.01) for bid in pending['blocks']]
        for call in (lambda: sp.requeue_overrun(reg, r, pending['index'], all_keep),
                     lambda: sp.verify_executed_roster(reg, r, p)):
            with self.assertRaises(sp.PackingRefusal) as caught:
                call()
            self.assertEqual(caught.exception.code, 'inv_11')

    def test_r3_unresealed_missing_live_positions(self):
        reg, r, pending, all_keep = _missing_live_roster()
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.requeue_overrun(reg, r, pending, all_keep)
        self.assertEqual(caught.exception.code, 'inv_02')

    def test_r2_resealed_missing_live_positions(self):
        reg, r, pending, all_keep = _missing_live_roster()
        reseal(r)
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.requeue_overrun(reg, r, pending, all_keep)
        self.assertEqual(caught.exception.code, 'inv_11')

    def test_r2b_parent_relation_precedes_derived(self):
        g, p, reg, r = _split_route()
        self.assertEqual(len(r['events']), 11)
        parent_id = next(o['block_id'] for o in r['events'][-1]['observations'] if o['decision'] == 'split')
        parent = next(b for b in r['blocks'] if b['block_id'] == parent_id)
        parent['superseded'] = False
        reseal(r)
        self.assertIn('INV-12', {v.inv_id for v in check_roster(g, r, p)})
        self.assertNotIn('INV-11', {v.inv_id for v in check_roster(g, r, p)})
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.requeue_overrun(reg, r, 12, [])
        self.assertEqual(caught.exception.code, 'inv_12')

    def test_r4a_partly_terminal_parent_uses_live_position(self):
        g, p, reg, r = _split_route()
        model = g['role_to_model_id']['8B']
        while any(e['kind'] == 'loaded' and e['observations'] is None for e in r['envelopes']):
            envelope = next(e for e in r['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None)
            blocks = {b['block_id']: b for b in r['blocks']}
            observations = []
            for bid in envelope['blocks']:
                block = blocks[bid]
                culprit = bid.endswith(':single:0') and block['retry_stage'] in ('single_problem', 'single_retry')
                observations.append(dict(block_id=bid, status='completed',
                                         elapsed_s=reg.worst(block['model']) + .1 if culprit else .01))
            r = sp.requeue_overrun(reg, r, envelope['index'], observations)
        self.assertEqual(check_roster(g, r, p), [])
        self.assertTrue(any(t['type'] == 'ceiling_violation' for t in r['terminal_refusals']))
        live = {bid: e['index'] for e in r['envelopes'] for bid in e['blocks']}
        parent = next(b for b in r['blocks'] if b['model'] == model and b['level'] == 1 and b['superseded'])
        sibling = next(b for b in r['blocks'] if b['parent_block_id'] == parent['block_id'] and b['block_id'].endswith(':single:1'))
        self.assertEqual(live[sibling['block_id']], 13)
        fact = next(f for f in sp._parent_facts(reg, r) if f['parent_id'] == parent['block_id'])
        self.assertEqual(fact['indices'], [13])
        self.assertEqual((fact['n_items'], fact['n_terminal']), (2, 1))
        expected = abs(sum([13, 2, 4, 6, 8]) / 5 - sum([1, 3, 5, 7, 9]) / 5)
        self.assertEqual(expected, 1.5999999999999996)
        self.assertEqual(r['drift_lever_slots']['1'], expected)
        self.assertTrue(r['planned_spread_shortfall'][f'{model}:1'])

    def _patched_fact_refusal(self, n_items, code, prefix):
        g, p = fixture(n=5, block_size=1, cap=6.0)
        reg = sr.Registration.from_mapping(g)
        r = sp.pack(reg, p)
        model = g['role_to_model_id']['8B']
        pending = next(e for e in r['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None)
        observations = [dict(block_id=bid, status='completed', elapsed_s=.01) for bid in pending['blocks']]
        fact = dict(parent_id='p', model=model, level=1, n_items=n_items, n_terminal=0, indices=[])
        with patch.object(sp, '_parent_facts', return_value=[fact]):
            with self.assertRaises(sp.PackingRefusal) as caught:
                sp.requeue_overrun(reg, r, pending['index'], observations)
        self.assertEqual(caught.exception.code, code)
        self.assertTrue(_detail(caught.exception).startswith(prefix))

    def test_r4b_gate_relation(self):
        self._patched_fact_refusal(2, 'inv_11', 'gate parent without full live positions')

    def test_r4d_empty_fact(self):
        self._patched_fact_refusal(0, 'inv_10', 'empty parent')

    def test_r4d_empty_block_precondition(self):
        g, p = fixture(n=5, block_size=1, cap=6.0)
        reg = sr.Registration.from_mapping(g)
        z = sp.pack(reg, p)
        model = g['role_to_model_id']['8B']
        while any(e['kind'] == 'loaded' and e['observations'] is None for e in z['envelopes']):
            envelope = next(e for e in z['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None)
            observations = [dict(block_id=bid,
                                 status='not_started' if envelope['model'] == model else 'completed',
                                 elapsed_s=None if envelope['model'] == model else .01)
                            for bid in envelope['blocks']]
            z = sp.requeue_overrun(reg, z, envelope['index'], observations)
        self.assertEqual(check_roster(g, z, p), [])
        self.assertIsNone(z['drift_lever_slots']['1'])
        z['blocks'].append(dict(z['blocks'][0], block_id=f"{model}:{g['arm']}:1:999", model=model,
                                level=1, items=[], predicted_item_s=[], predicted_s=0, attempt=0,
                                retry_stage='initial', parent_block_id=None, superseded=False, late=False))
        reseal(z)
        self.assertIn('INV-10', {v.inv_id for v in check_roster(g, z, p)})
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.verify_executed_roster(reg, z, p)
        self.assertEqual(caught.exception.code, 'inv_10')
        self.assertEqual(_detail(caught.exception), 'empty block')

    def test_r5a_resealed_output_still_replays(self):
        g, p = fixture(n=5)
        reg = sr.Registration.from_mapping(g)
        r = sp.pack(reg, p)
        r['blocks'][0]['late'] = True
        r['sha256'] = None
        sp._seal(reg, r, finalize=True)
        pending = next(e for e in r['envelopes'] if e['kind'] == 'loaded')
        observations = [dict(block_id=bid, status='completed', elapsed_s=.01) for bid in pending['blocks']]
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.requeue_overrun(reg, r, pending['index'], observations)
        self.assertIn(caught.exception.code, ('inv_38', 'inv_39'))

    def test_r4c_derived_structure_ast(self):
        tree = ast.parse(inspect.getsource(sp))
        functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        derived = functions['_derived']
        self.assertEqual(len(derived.body), 1)
        self.assertIsInstance(derived.body[0], ast.Return)
        self.assertIsInstance(derived.body[0].value, ast.Call)
        self.assertIsInstance(derived.body[0].value.func, ast.Name)
        self.assertEqual(derived.body[0].value.func.id, '_lever')
        self.assertNotIn('roster', [a.arg for a in functions['_lever'].args.args])
        guarded = ('_lever', '_derived', '_checked_derived', '_seal', 'executed_status')
        keys = {'blocks', 'placements', 'terminal_refusals', 'envelopes'}
        for name in guarded:
            for node in ast.walk(functions[name]):
                if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
                    self.assertNotIn(node.slice.value, keys, name)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'get' and node.args and isinstance(node.args[0], ast.Constant):
                    self.assertNotIn(node.args[0].value, keys, name)
        for name, fn in functions.items():
            for node in ast.walk(fn):
                if isinstance(node, ast.Div):
                    self.assertEqual(name, '_lever')
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in ('_live_index', '_live'):
                    self.assertEqual(name, '_parent_facts')
        self.assertFalse(hasattr(sp, '_live'))

    def test_r5b_no_trusted_mutable_cache_ast(self):
        source = inspect.getsource(sp)
        self.assertFalse('_TRUSTED_OUTPUTS' in source)
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                names = ([t.id for t in node.targets if isinstance(t, ast.Name)] if isinstance(node, ast.Assign)
                         else [node.target.id] if isinstance(node.target, ast.Name) else [])
                value = node.value
                mutable = isinstance(value, (ast.Dict, ast.List, ast.Set)) or (
                    isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and
                    value.func.id in ('deque', 'dict', 'list', 'set'))
                if mutable:
                    self.assertEqual(names, ['_REPLAYING'])
            if isinstance(node, ast.FunctionDef):
                self.assertFalse(any(isinstance(d, ast.Name) and d.id in ('lru_cache', 'cache') for d in node.decorator_list))
                defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d is not None]
                self.assertFalse(any(isinstance(d, (ast.Dict, ast.List, ast.Set)) for d in defaults))
