"""Hand-built A291 oracle fixtures. No production packer is imported.

# CONTRACT GAPS
# 1. Root reconstruction does not specify its envelope cutoff. Choice: the
#    last initial placement or idle slot fixes it; event-created slots have no
#    initial placement. This follows RD-3 and 31 X-1.
# 2. A roster-only checker cannot observe a removed prior event/placement.
#    Choice: check_transition compares the supplied before/after pair; the
#    single-roster replay checks the surviving chain.
# 3. INV-26 and INV-45 are executed *values*, not refusals. Choice: assert
#    changes in check_executed output at their boundaries, per §4.2/31 X-5.
# 4. §6 gives check_executed a dict return with no invalid-input shape.
#    Choice: invalid inputs return {'violations': list[Violation]}.
# 5. Root claim_ready in registered mode is not explicitly required at pack
#    exit by INV-05's second clause. Choice: reject false on descendant entry.
# 6. R1 case 2 predates FT-14: its stated cut_off B then completed single
#    order is now invalid. Choice: reject the exact probe with INV-47.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import unittest

from tests import scored_roster_checker as c


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def seal(r):
    pre = deepcopy(r)
    pre.pop('sha256', None)
    pre.pop('registered_sha256', None)
    for event in pre['events']:
        event.pop('sha256', None)
    r['sha256'] = sha(pre)
    if r['events']:
        r['events'][-1]['sha256'] = r['sha256']
    else:
        r['registered_sha256'] = r['sha256']
    return r


def fixture(n=5, block_size=1, capacity=100, worst=30, mode='registered'):
    ids = {str(l): [f'L{l}I{i}' for i in range(n)] for l in range(1, 6)}
    flat = [x for l in range(1, 6) for x in ids[str(l)]]
    p = {m: {x: 4.0 for x in flat} for m in ('big', 'small')}
    g = dict(schema='joulewise.scored_registration.v2', mode=mode,
             registration_id='reg', plan_id='plan', scorer_id='scorer', arm='on',
             arm_to_family={'on': 'family'}, role_to_model_id={'8B': 'big', '1.7B': 'small'},
             sizing_receipt_sha256='a'*64 if mode == 'registered' else None,
             predictions_sha256=sha(p) if mode == 'registered' else None,
             alpha=0.05, n_boot=10, seed=0, floor_j=0.0, anchor_j=0.0,
             cap_tokens={'on': 1}, block_size={'on': block_size}, item_ids_by_level=ids,
             envelope_s=capacity, interior_s=capacity, pitch_s=capacity,
             offset_s=0.0, guard_s=0.0,
             s_per_token_upper={m: {'on': float(worst)} for m in p},
             prefill_s={m: {'on': 0.0} for m in p},
             ceiling_s={m: {'on': float(worst)} for m in p},
             delta_upper_j_per_block_slot=1.0 if mode == 'registered' else None,
             budget_j=10000.0 if mode == 'registered' else None,
             declared_sensitivities=['base'])
    blocks, envs, placements = [], [], []
    for level in range(1, 6):
        for model in ('big', 'small'):
            for k, start in enumerate(range(0, n, block_size)):
                items = ids[str(level)][start:start+block_size]
                bid = f'{model}:on:{level}:{k}'
                block = dict(block_id=bid, model=model, level=level, items=items,
                             predicted_item_s=[4.0]*len(items), predicted_s=sum([4.0]*len(items)),
                             attempt=0, retry_stage='initial', parent_block_id=None,
                             superseded=False, late=False)
                blocks.append(block)
                index = len(envs)
                envs.append(dict(index=index, model=model, kind='loaded', blocks=[bid],
                                 voided_block_ids=[], observations=None))
                placements.append(dict(block_id=bid, attempt=0, stage='initial',
                                       reserved_s=block['predicted_s'], envelope_index=index))
    counts = {m: sum(e['model'] == m for e in envs) for m in ('big', 'small')}
    if all(counts[m] % 2 for m in counts):
        envs.append(dict(index=len(envs), model='small', kind='idle_slot', blocks=[],
                         voided_block_ids=[], observations=None))
    short = {f'{m}:{l}': False for m in ('big', 'small') for l in range(1, 6)}
    lever = {str(l): float(n // block_size) for l in range(1, 6)}
    # With level/role/k order and one block per envelope, model means differ
    # by precisely blocks-per-cell.
    r = dict(schema='joulewise.scored_roster.v3', registration_sha256=sha(g),
             claim_ready=mode == 'registered', item_set_sha256=sha(flat), n_per_level=n,
             blocks=blocks, envelopes=envs, placements=placements, terminal_refusals=[],
             events=[], drift_lever_slots=lever, planned_spread_shortfall=short,
             registered_sha256='0'*64, sha256='0'*64)
    return g, seal(r), p


def keep_first(g, r, elapsed=4.0):
    r = deepcopy(r)
    e = r['envelopes'][0]
    bid = e['blocks'][0]
    obs = dict(block_id=bid, status='completed', elapsed_s=elapsed, decision='keep')
    e['observations'] = [deepcopy(obs)]
    if elapsed > r['blocks'][0]['predicted_s']:
        r['blocks'][0]['late'] = True
    r['events'].append(dict(envelope_index=0, block_ids=[bid], observations=[obs], placements=[], sha256='0'*64))
    return seal(r)


def advance_first(g, r, elapsed=10.0):
    r = deepcopy(r)
    e = r['envelopes'][0]
    bid = e['blocks'].pop()
    e['voided_block_ids'].append(bid)
    obs = dict(block_id=bid, status='cut_off', elapsed_s=elapsed, decision='advance')
    e['observations'] = [deepcopy(obs)]
    block = r['blocks'][0]
    block['attempt'] = 1
    block['retry_stage'] = 'whole_block'
    index = len(r['envelopes'])
    r['envelopes'].append(dict(index=index, model=block['model'], kind='loaded', blocks=[bid],
                               voided_block_ids=[], observations=None))
    reserved = min(sum(g['cap_tokens']['on'] * g['s_per_token_upper'][block['model']]['on'] + g['prefill_s'][block['model']]['on'] for _ in block['items']), g['interior_s'] - g['guard_s'])
    pi = len(r['placements'])
    r['placements'].append(dict(block_id=bid, attempt=1, stage='whole_block',
                                reserved_s=reserved, envelope_index=index))
    r['events'].append(dict(envelope_index=0, block_ids=[bid], observations=[obs], placements=[pi], sha256='0'*64))
    # Level 1 parent positions: moved parent at new index, four old big
    # positions 2,4,6,8; small positions 1,3,5,7,9.
    bpc = len(g['item_ids_by_level']['1']) // g['block_size']['on']
    old_big = list(range(1, bpc))
    old_small = list(range(bpc, 2*bpc))
    r['drift_lever_slots']['1'] = abs(sum([index] + old_big)/bpc - sum(old_small)/bpc)
    return seal(r)


def refresh_derived(g, r):
    """Fixture-side arithmetic from visible live item placements, in item order."""
    live = {}
    for e in r['envelopes']:
        for bid in e['blocks']:
            live[bid] = e['index']
    terminal = {(t['model'], t['item_id']) for t in r['terminal_refusals']}
    pos = {}
    short = {}
    for level in range(1, 6):
        for model in ('big', 'small'):
            positions, slots = [], set()
            nonterminal = 0
            for parent in r['blocks']:
                if parent['parent_block_id'] is not None or parent['level'] != level or parent['model'] != model:
                    continue
                fully_nonterminal = all((model, item) not in terminal for item in parent['items'])
                nonterminal += fully_nonterminal
                indices = []
                for item in parent['items']:
                    if (model, item) in terminal:
                        continue
                    owner = parent if not parent['superseded'] else next((b for b in r['blocks'] if b['parent_block_id'] == parent['block_id'] and b['items'] == [item]), None)
                    if owner and owner['block_id'] in live:
                        indices.append(live[owner['block_id']])
                if indices:
                    positions.append(sum(indices) / len(indices))
                if fully_nonterminal and len(indices) == len(parent['items']):
                    slots.update(indices)
            pos[(model, level)] = (positions, nonterminal)
            short[f'{model}:{level}'] = nonterminal < 5 or len(slots) < 5
    r['planned_spread_shortfall'] = short
    r['drift_lever_slots'] = {}
    for level in range(1, 6):
        (a, na), (b, nb) = pos[('big', level)], pos[('small', level)]
        r['drift_lever_slots'][str(level)] = abs(sum(a)/len(a) - sum(b)/len(b)) if na and nb else None
    return r


def report_keep(r, index):
    r = deepcopy(r)
    e = r['envelopes'][index]
    obs = [dict(block_id=bid, status='completed', elapsed_s=4.0, decision='keep') for bid in e['blocks']]
    e['observations'] = deepcopy(obs)
    r['events'].append(dict(envelope_index=index, block_ids=list(e['blocks']), observations=obs, placements=[], sha256='0'*64))
    return seal(r)


def mixed_initial_roster():
    """One initial culprit and one innocent initial mate in a loaded slot."""
    g, root, p = fixture()
    root = deepcopy(root)
    mate = root['envelopes'][10]['blocks'].pop()
    root['envelopes'][0]['blocks'].append(mate)
    root['placements'][10]['envelope_index'] = 0
    root['envelopes'].pop(10)
    root['envelopes'].pop()  # odd-count idle is no longer due
    for i, e in enumerate(root['envelopes']):
        e['index'] = i
    for placement in root['placements']:
        if placement['envelope_index'] > 10:
            placement['envelope_index'] -= 1
    root['placements'].sort(key=lambda placement: placement['envelope_index'])
    refresh_derived(g, root)
    seal(root)
    r = deepcopy(root)
    first, second = r['envelopes'][0]['blocks']
    r['envelopes'][0]['blocks'] = []
    r['envelopes'][0]['voided_block_ids'] = [first, second]
    obs = [dict(block_id=first, status='cut_off', elapsed_s=10.0, decision='advance'),
           dict(block_id=second, status='not_started', elapsed_s=None, decision='reschedule')]
    r['envelopes'][0]['observations'] = deepcopy(obs)
    b1 = next(b for b in r['blocks'] if b['block_id'] == first)
    b2 = next(b for b in r['blocks'] if b['block_id'] == second)
    b1.update(attempt=1, retry_stage='whole_block')
    b2['attempt'] = 1
    fresh = len(r['envelopes'])
    r['envelopes'].append(dict(index=fresh, model='big', kind='loaded', blocks=[first],
                               voided_block_ids=[], observations=None))
    pi1 = len(r['placements'])
    r['placements'].append(dict(block_id=first, attempt=1, stage='whole_block',
                                reserved_s=30.0, envelope_index=fresh))
    r['envelopes'][1]['blocks'].append(second)
    pi2 = len(r['placements'])
    r['placements'].append(dict(block_id=second, attempt=1, stage='initial',
                                reserved_s=4.0, envelope_index=1))
    r['events'].append(dict(envelope_index=0, block_ids=[first, second],
                            observations=obs, placements=[pi1, pi2], sha256='0'*64))
    refresh_derived(g, r)
    return g, root, seal(r), p


def r1_mixed_stage_base():
    """R1's reachable initial parent plus single in one later envelope."""
    g, root, p = fixture(n=10, block_size=2, capacity=50)
    a, b = 'big:on:1:0', 'big:on:2:0'
    for model in p:
        for item in p[model]:
            p[model][item] = 25.0
    for item in g['item_ids_by_level']['1'][:2] + g['item_ids_by_level']['2'][:2]:
        p['big'][item] = 4.0
    g['predictions_sha256'] = sha(p)
    for block in root['blocks']:
        block['predicted_item_s'] = [p[block['model']][item] for item in block['items']]
        block['predicted_s'] = sum(block['predicted_item_s'])
    for placement in root['placements']:
        block = next(x for x in root['blocks'] if x['block_id'] == placement['block_id'])
        placement['reserved_s'] = block['predicted_s']
    root['envelopes'][10]['blocks'].remove(b)
    root['envelopes'][0]['blocks'].append(b)
    root['placements'][10]['envelope_index'] = 0
    root['envelopes'].pop(10)
    root['envelopes'].pop()  # no idle: loaded counts are now 24 and 25
    for i, e in enumerate(root['envelopes']):
        e['index'] = i
    for placement in root['placements']:
        if placement['envelope_index'] > 10:
            placement['envelope_index'] -= 1
    root['registration_sha256'] = sha(g)
    root['placements'].sort(key=lambda placement: placement['envelope_index'])
    refresh_derived(g, root)
    seal(root)
    r = deepcopy(root)
    e = r['envelopes'][0]
    e['blocks'] = []
    e['voided_block_ids'] = [a, b]
    obs = [dict(block_id=a, status='cut_off', elapsed_s=10.0, decision='advance'),
           dict(block_id=b, status='not_started', elapsed_s=None, decision='reschedule')]
    e['observations'] = deepcopy(obs)
    ba = next(x for x in r['blocks'] if x['block_id'] == a)
    bb = next(x for x in r['blocks'] if x['block_id'] == b)
    ba.update(attempt=1, retry_stage='whole_block')
    bb['attempt'] = 1
    ia = len(r['envelopes'])
    r['envelopes'].append(dict(index=ia, model='big', kind='loaded', blocks=[a], voided_block_ids=[], observations=None))
    ib = len(r['envelopes'])
    r['envelopes'].append(dict(index=ib, model='big', kind='loaded', blocks=[b], voided_block_ids=[], observations=None))
    pia = len(r['placements'])
    r['placements'].append(dict(block_id=a, attempt=1, stage='whole_block', reserved_s=50.0, envelope_index=ia))
    pib = len(r['placements'])
    r['placements'].append(dict(block_id=b, attempt=1, stage='initial', reserved_s=8.0, envelope_index=ib))
    r['events'].append(dict(envelope_index=0, block_ids=[a, b], observations=obs, placements=[pia, pib], sha256='0'*64))
    refresh_derived(g, r)
    seal(r)
    for index in range(1, ia):
        r = report_keep(r, index)
    r = deepcopy(r)
    e = r['envelopes'][ia]
    e['blocks'] = []
    e['voided_block_ids'] = [a]
    obs = dict(block_id=a, status='cut_off', elapsed_s=10.0, decision='split')
    e['observations'] = [deepcopy(obs)]
    ba = next(x for x in r['blocks'] if x['block_id'] == a)
    ba['superseded'] = True
    new = []
    for j, item in enumerate(ba['items']):
        sid = f'{a}:single:{j}'
        single = dict(block_id=sid, model='big', level=1, items=[item],
                      predicted_item_s=[4.0], predicted_s=30.0, attempt=2,
                      retry_stage='single_problem', parent_block_id=a,
                      superseded=False, late=False)
        r['blocks'].append(single)
        target = ib if j == 0 else len(r['envelopes'])
        if target == len(r['envelopes']):
            r['envelopes'].append(dict(index=target, model='big', kind='loaded', blocks=[], voided_block_ids=[], observations=None))
        r['envelopes'][target]['blocks'].append(sid)
        pi = len(r['placements'])
        r['placements'].append(dict(block_id=sid, attempt=2, stage='single_problem', reserved_s=30.0, envelope_index=target))
        new.append(pi)
    r['events'].append(dict(envelope_index=ia, block_ids=[a], observations=[obs], placements=new, sha256='0'*64))
    refresh_derived(g, r)
    return g, seal(r), p


def r1_case_one(g, base):
    r = deepcopy(base)
    e = r['envelopes'][50]
    b, single = e['blocks']
    e['blocks'] = [b]
    e['voided_block_ids'] = [single]
    obs = [dict(block_id=b, status='completed', elapsed_s=25.0, decision='keep'),
           dict(block_id=single, status='cut_off', elapsed_s=25.0, decision='reschedule')]
    e['observations'] = deepcopy(obs)
    next(x for x in r['blocks'] if x['block_id'] == b)['late'] = True
    sb = next(x for x in r['blocks'] if x['block_id'] == single)
    sb['attempt'] = 3
    target = len(r['envelopes'])
    r['envelopes'].append(dict(index=target, model='big', kind='loaded', blocks=[single], voided_block_ids=[], observations=None))
    pi = len(r['placements'])
    r['placements'].append(dict(block_id=single, attempt=3, stage='single_problem', reserved_s=30.0, envelope_index=target))
    r['events'].append(dict(envelope_index=50, block_ids=[b, single], observations=obs, placements=[pi], sha256='0'*64))
    refresh_derived(g, r)
    return seal(r)


def split_roster(capacity=50):
    g, root, p = fixture(n=10, block_size=2, capacity=capacity)
    r = advance_first(g, root)
    for index in range(1, 50):
        r = report_keep(r, index)
    r = deepcopy(r)
    e = r['envelopes'][51]
    bid = e['blocks'].pop()
    e['voided_block_ids'].append(bid)
    obs = dict(block_id=bid, status='cut_off', elapsed_s=10.0, decision='split')
    e['observations'] = [deepcopy(obs)]
    parent = r['blocks'][0]
    parent['superseded'] = True
    new = []
    for j, item in enumerate(parent['items']):
        sid = f'{bid}:single:{j}'
        single = dict(block_id=sid, model='big', level=1, items=[item],
                      predicted_item_s=[parent['predicted_item_s'][j]], predicted_s=30.0,
                      attempt=2, retry_stage='single_problem', parent_block_id=bid,
                      superseded=False, late=False)
        r['blocks'].append(single)
        target = 52 if j == 0 or capacity >= 60 else 53
        if target == len(r['envelopes']):
            r['envelopes'].append(dict(index=target, model='big', kind='loaded', blocks=[],
                                      voided_block_ids=[], observations=None))
        r['envelopes'][target]['blocks'].append(sid)
        pi = len(r['placements'])
        r['placements'].append(dict(block_id=sid, attempt=2, stage='single_problem',
                                   reserved_s=30.0, envelope_index=target))
        new.append(pi)
    r['events'].append(dict(envelope_index=51, block_ids=[bid], observations=[obs], placements=new, sha256='0'*64))
    refresh_derived(g, r)
    return g, seal(r), p


def r2_four_envelope_roster():
    """FT-2's 3+3+2+2 reschedules with two culprits twice each."""
    g, root, p = fixture(n=20, block_size=4, capacity=120)
    r = advance_first(g, root, elapsed=20.0)
    for index in range(1, 50):
        r = report_keep(r, index)
    r = deepcopy(r)
    whole = r['envelopes'][51]
    parent_id = whole['blocks'].pop()
    whole['voided_block_ids'] = [parent_id]
    obs = dict(block_id=parent_id, status='cut_off', elapsed_s=10.0, decision='split')
    whole['observations'] = [deepcopy(obs)]
    parent = r['blocks'][0]
    parent['superseded'] = True
    target = len(r['envelopes'])
    r['envelopes'].append(dict(index=target, model='big', kind='loaded', blocks=[], voided_block_ids=[], observations=None))
    made = []
    for j, item in enumerate(parent['items']):
        bid = f'{parent_id}:single:{j}'
        r['blocks'].append(dict(block_id=bid, model='big', level=1, items=[item], predicted_item_s=[4.0],
                                predicted_s=30.0, attempt=2, retry_stage='single_problem',
                                parent_block_id=parent_id, superseded=False, late=False))
        r['envelopes'][target]['blocks'].append(bid)
        pi = len(r['placements'])
        r['placements'].append(dict(block_id=bid, attempt=2, stage='single_problem', reserved_s=30.0, envelope_index=target))
        made.append(pi)
    r['events'].append(dict(envelope_index=51, block_ids=[parent_id], observations=[obs], placements=made, sha256='0'*64))
    refresh_derived(g, r)
    seal(r)
    # A twice, then B twice. Each culprit runs first; its mates did not start.
    for reporter, culprit_j in [(52, 0), (53, 0), (54, 1), (55, 1)]:
        r = deepcopy(r)
        e = r['envelopes'][reporter]
        ids = list(e['blocks'])
        culprit = f'{parent_id}:single:{culprit_j}'
        assert ids[0] == culprit
        obs = [dict(block_id=culprit, status='cut_off', elapsed_s=31.0, decision='advance')]
        obs += [dict(block_id=bid, status='not_started', elapsed_s=None, decision='reschedule') for bid in ids[1:]]
        e['blocks'] = []
        e['voided_block_ids'] = ids
        e['observations'] = deepcopy(obs)
        new_ids = []
        for bid in ids:
            block = next(b for b in r['blocks'] if b['block_id'] == bid)
            if bid == culprit and block['retry_stage'] == 'single_retry':
                block['retry_stage'] = 'ceiling_violation'
                r['terminal_refusals'].append(dict(type='ceiling_violation', block_id=bid, attempt=block['attempt'],
                                                    parent_block_id=parent_id, item_id=block['items'][0], model='big', level=1))
            else:
                block['attempt'] += 1
                if bid == culprit:
                    block['retry_stage'] = 'single_retry'
                new_ids.append(bid)
        made = []
        if new_ids:
            target = len(r['envelopes'])
            r['envelopes'].append(dict(index=target, model='big', kind='loaded', blocks=[], voided_block_ids=[], observations=None))
            for bid in new_ids:
                block = next(b for b in r['blocks'] if b['block_id'] == bid)
                r['envelopes'][target]['blocks'].append(bid)
                pi = len(r['placements'])
                r['placements'].append(dict(block_id=bid, attempt=block['attempt'], stage=block['retry_stage'],
                                           reserved_s=30.0, envelope_index=target))
                made.append(pi)
        r['events'].append(dict(envelope_index=reporter, block_ids=ids, observations=obs, placements=made, sha256='0'*64))
        refresh_derived(g, r)
        seal(r)
    return g, r, p


def completed_culprit_single(g, split):
    r = deepcopy(split)
    e = r['envelopes'][52]
    bid = e['blocks'].pop(0)
    e['voided_block_ids'].append(bid)
    obs = dict(block_id=bid, status='completed', elapsed_s=31.0, decision='advance')
    e['observations'] = [deepcopy(obs)]
    single = next(b for b in r['blocks'] if b['block_id'] == bid)
    single.update(attempt=3, retry_stage='single_retry', late=True)
    target = len(r['envelopes'])
    r['envelopes'].append(dict(index=target, model='big', kind='loaded', blocks=[bid],
                              voided_block_ids=[], observations=None))
    pi = len(r['placements'])
    r['placements'].append(dict(block_id=bid, attempt=3, stage='single_retry',
                               reserved_s=30.0, envelope_index=target))
    r['events'].append(dict(envelope_index=52, block_ids=[bid], observations=[obs], placements=[pi], sha256='0'*64))
    refresh_derived(g, r)
    return seal(r)


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.g, self.r, self.p = fixture()

    def assertRow(self, row, g=None, r=None, p=None):
        got = c.check_roster(g if g is not None else self.g,
                             r if r is not None else self.r,
                             p if p is not None else self.p)
        self.assertIn(row, {x.inv_id for x in got}, got)

    def test_base_and_row_inventory(self):
        self.assertEqual([], c.check_roster(self.g, self.r, self.p))
        contract = Path(__file__).resolve().parents[1] / 'docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md'
        ids = set(re.findall(r'^\*\*(INV-\d+(?:/\d+)?)\b', contract.read_text(), re.M))
        self.assertEqual(ids, set(c.ROWS) | set(c.NOT_CHECKABLE))
        self.assertFalse(set(c.ROWS) & set(c.NOT_CHECKABLE))

    def test_witness_inventory(self):
        groups = {
            'test_registration_rows': {'INV-04', 'INV-05', 'INV-06', 'INV-09', 'INV-28', 'INV-51'},
            'test_root_mutation_rows': {'INV-01', 'INV-02', 'INV-03', 'INV-04', 'INV-07', 'INV-08', 'INV-10', 'INV-11', 'INV-12', 'INV-14', 'INV-15', 'INV-16', 'INV-17', 'INV-20', 'INV-21', 'INV-24', 'INV-25', 'INV-27', 'INV-37', 'INV-41', 'INV-49', 'INV-50', 'INV-52'},
            'test_event_mutation_rows': {'INV-18', 'INV-22', 'INV-29', 'INV-30', 'INV-34', 'INV-35', 'INV-36', 'INV-38', 'INV-46', 'INV-47', 'INV-48'},
            'test_split_and_completed_single_rows': {'INV-19', 'INV-23', 'INV-32', 'INV-33/43'},
            'test_INV_31_innocent_initial_reschedule': {'INV-31', 'INV-34'},
            'test_executed_values_INV_26_INV_45': {'INV-26', 'INV-45'},
        }
        self.assertEqual(set(c.ROWS), set().union(*groups.values()))
        self.assertTrue(all(hasattr(self, name) for name in groups))

    def test_typed_codes_and_pure_interfaces(self):
        bad = deepcopy(self.r)
        bad['planned_spread_shortfall']['big:1'] = True
        seal(bad)
        self.assertIn(('INV-49', 'stale_derived'), {(v.inv_id, v.code) for v in c.check_roster(self.g, bad, self.p)})
        bad = keep_first(self.g, self.r)
        bad['events'][0]['observations'][0]['elapsed_s'] = 0.0
        seal(bad)
        self.assertIn(('INV-29', 'invalid_elapsed'), {(v.inv_id, v.code) for v in c.check_roster(self.g, bad, self.p)})
        unreported = c.check_executed(self.g, self.r, self.p, set())
        self.assertIn(('INV-46', 'unreported_envelope'), {(v.inv_id, v.code) for v in unreported['violations']})
        self.assertIn('INV-51', {v.inv_id for v in c.check_registration({'schema': 'bad'})})
        self.assertIn('INV-03', {v.inv_id for v in c.check_roster(self.g, [], self.p)})
        bad = keep_first(self.g, self.r)
        next_roster = report_keep(bad, 1)
        self.assertEqual([], c.check_transition(self.g, bad, next_roster, self.p))
        changed = deepcopy(next_roster)
        changed['envelopes'][0]['blocks'] = []
        seal(changed)
        self.assertIn('INV-18', {v.inv_id for v in c.check_transition(self.g, bad, changed, self.p)})

    def test_registration_rows(self):
        for row, change in [
            ('INV-51', lambda g: g.update(alpha=0)),
            ('INV-04', lambda g: g['item_ids_by_level']['5'].pop()),
            ('INV-09', lambda g: g['item_ids_by_level'].update({'6': []})),
            ('INV-06', lambda g: g['cap_tokens'].update({'off': 1})),
        ]:
            with self.subTest(row=row):
                g = deepcopy(self.g)
                change(g)
                self.assertRow(row, g=g)
        self.assertEqual([], c.check_registration(self.g))
        gp, rp, pp = fixture(mode='pilot')
        rp['claim_ready'] = True
        seal(rp)
        self.assertRow('INV-05', g=gp, r=rp, p=pp)
        gd = deepcopy(self.g); gd['budget_j'] = 0.0
        rd = deepcopy(self.r); rd['registration_sha256'] = sha(gd); seal(rd)
        self.assertRow('INV-28', g=gd, r=rd)

    def test_root_mutation_rows(self):
        mutations = {
            'INV-01': lambda r: r.update(registration_sha256='0'*64),
            'INV-02': lambda r: r.update(sha256='0'*64),
            'INV-03': lambda r: r.update(models=['big', 'small']),
            'INV-04': lambda r: r.update(n_per_level=6),
            'INV-07': lambda r: r['blocks'][0]['predicted_item_s'].__setitem__(0, 31.0),
            'INV-08': lambda r: r['blocks'][0]['predicted_item_s'].__setitem__(0, 5.0),
            'INV-10': lambda r: r['blocks'][0].update(block_id='bad'),
            'INV-11': lambda r: r['envelopes'][0]['blocks'].clear(),
            'INV-12': lambda r: r['blocks'][0].update(superseded=True),
            'INV-14': lambda r: r['envelopes'][0].update(model='small'),
            'INV-15': lambda r: r['envelopes'][0]['blocks'].clear(),
            'INV-16': lambda r: r['envelopes'][-1].update(observations=[]),
            'INV-17': lambda r: r['envelopes'][0].update(index=1),
            'INV-20': lambda r: r['placements'][0].update(reserved_s=101.0),
            'INV-21': lambda r: r['placements'][0].update(reserved_s=5.0),
            'INV-24': lambda r: (r['envelopes'][0]['blocks'].append(r['envelopes'][2]['blocks'].pop()), r['placements'][2].update(envelope_index=0)),
            'INV-25': lambda r: r['envelopes'][4].update(blocks=[], voided_block_ids=['big:on:1:4']),
            'INV-27': lambda r: r['drift_lever_slots'].__setitem__('1', 999.0),
            'INV-37': lambda r: r['terminal_refusals'].append(dict(type='ceiling_violation', block_id='big:on:1:0', attempt=0, parent_block_id=None, item_id='L1I0', model='big', level=1)),
            'INV-41': lambda r: r['envelopes'][-1].update(kind='loaded'),
            'INV-49': lambda r: r['planned_spread_shortfall'].__setitem__('big:1', True),
            'INV-50': lambda r: (r['blocks'].__setitem__(0, r['blocks'][5]), r['blocks'].__setitem__(5, self.r['blocks'][0])),
            'INV-52': lambda r: r['blocks'][0].update(late=1),
        }
        for row, mutate in mutations.items():
            with self.subTest(row=row):
                r = deepcopy(self.r)
                mutate(r)
                if row != 'INV-02':
                    seal(r)
                self.assertRow(row, r=r)

    def test_event_mutation_rows(self):
        a = advance_first(self.g, self.r)
        self.assertEqual([], c.check_roster(self.g, a, self.p))
        k = keep_first(self.g, self.r)
        self.assertEqual([], c.check_roster(self.g, k, self.p))
        mutations = {
            'INV-18': (a, lambda r: r['placements'][-1].update(envelope_index=0)),
            'INV-22': (a, lambda r: r['placements'][-1].update(reserved_s=29.0)),
            'INV-29': (k, lambda r: r['events'][0]['block_ids'].clear()),
            'INV-30': (k, lambda r: r['events'][0]['observations'][0].update(decision='advance')),
            'INV-34': (a, lambda r: r['placements'][-1].update(envelope_index=1)),
            'INV-35': (k, lambda r: r['events'][0]['observations'][0].update(decision='reschedule')),
            'INV-36': (a, lambda r: r['placements'][-1].update(attempt=2)),
            'INV-38': (k, lambda r: r['events'][0].update(sha256='f'*64)),
            'INV-46': (k, lambda r: r['events'][0].update(envelope_index=2)),
            'INV-47': (k, lambda r: r['events'][0]['observations'].extend([dict(block_id='extra1', status='not_started', elapsed_s=None, decision='advance'), dict(block_id='extra2', status='cut_off', elapsed_s=1.0, decision='advance')])),
            'INV-48': (k, lambda r: r['events'][0]['observations'][0].update(elapsed_s=101.0)),
        }
        for row, (base, mutate) in mutations.items():
            with self.subTest(row=row):
                r = deepcopy(base)
                mutate(r)
                if row != 'INV-38':
                    seal(r)
                self.assertRow(row, r=r)

    def test_executed_values_INV_26_INV_45(self):
        reported = deepcopy(self.r)
        for index in range(50):
            reported = report_keep(reported, index)
        self.assertEqual([], c.check_roster(self.g, reported, self.p))
        keys = {(p['block_id'], p['attempt']) for p in reported['placements']}
        full = c.check_executed(self.g, reported, self.p, keys)
        self.assertFalse(any(full['spread_exceeded'].values()))
        self.assertFalse(any(full['drift_exceeded'].values()))
        missing = set(keys)
        missing.remove(('big:on:1:0', 0))
        partial = c.check_executed(self.g, reported, self.p, missing)
        self.assertTrue(partial['spread_exceeded']['big:1'])
        empty = c.check_executed(self.g, reported, self.p, set())
        self.assertIsNone(empty['executed_drift_lever_slots']['1'])
        self.assertFalse(empty['drift_exceeded']['1'])
        g, r, _ = fixture()
        g['budget_j'] = 26.0
        r['registration_sha256'] = sha(g)
        seal(r)
        for index in range(50):
            r = report_keep(r, index)
        lower = set(keys); lower.remove(('small:on:1:0', 0))
        flagged = c.check_executed(g, r, self.p, lower)
        self.assertTrue(flagged['drift_exceeded']['1'])

    def test_executed_uses_only_live_reschedule_and_advance_attempts(self):
        gm, _, rescheduled, pm = mixed_initial_roster()
        ga, root, pa = fixture()
        advanced = advance_first(ga, root)
        for label, g, roster, predictions, moved, level, expected in (
            ('reschedule', gm, rescheduled, pm, 'big:on:2:0', '2',
             abs(sum([1, 10, 11, 12, 13])/5 - sum(range(14, 19))/5)),
            ('advance', ga, advanced, pa, 'big:on:1:0', '1',
             abs(sum([51, 1, 2, 3, 4])/5 - sum(range(5, 10))/5)),
        ):
            with self.subTest(label=label):
                for index in range(1, len(roster['envelopes'])):
                    if roster['envelopes'][index]['kind'] == 'loaded':
                        roster = report_keep(roster, index)
                self.assertEqual([], c.check_roster(g, roster, predictions))
                keys = {(pl['block_id'], pl['attempt']) for pl in roster['placements']
                        if pl['block_id'] in roster['envelopes'][pl['envelope_index']]['blocks']}
                actual = c.check_executed(g, roster, predictions, keys)
                self.assertFalse(actual['spread_exceeded'][f'big:{level}'])
                self.assertEqual(expected, actual['executed_drift_lever_slots'][level])
                voided = next((pl['block_id'], pl['attempt']) for pl in roster['placements']
                              if pl['block_id'] == moved and
                              pl['block_id'] in roster['envelopes'][pl['envelope_index']]['voided_block_ids'])
                self.assertEqual(actual, c.check_executed(g, roster, predictions, keys | {voided}))

    def test_executed_partly_counted_parent_position(self):
        g, split, p = split_roster(capacity=90)
        complete = report_keep(split, 52)
        self.assertEqual([], c.check_roster(g, complete, p))
        live = {(pl['block_id'], pl['attempt']) for pl in complete['placements']
                if pl['block_id'] in complete['envelopes'][pl['envelope_index']]['blocks']}
        partial = live - {('big:on:1:0:single:0', 2)}
        result = c.check_executed(g, complete, p, partial)
        self.assertTrue(result['spread_exceeded']['big:1'])
        # One counted item places parent 0 at 52; four other big parents
        # remain at 1..4. The small parents remain at 5..9.
        self.assertEqual(abs(sum([52, 1, 2, 3, 4])/5 - sum(range(5, 10))/5),
                         result['executed_drift_lever_slots']['1'])

    def test_executed_single_advance_uses_retry_attempt(self):
        g, split, p = split_roster(capacity=50)
        roster = completed_culprit_single(g, split)
        for index in (53, 54):
            roster = report_keep(roster, index)
        next(b for b in roster['blocks'] if b['block_id'] == 'big:on:1:0:single:0')['late'] = False
        seal(roster)
        self.assertEqual([], c.check_roster(g, roster, p))
        keys = {(pl['block_id'], pl['attempt']) for pl in roster['placements']
                if pl['block_id'] in roster['envelopes'][pl['envelope_index']]['blocks']}
        result = c.check_executed(g, roster, p, keys)
        self.assertFalse(result['spread_exceeded']['big:1'])
        # The retried single is at 54 and its sibling at 53; each has one
        # counted item, so their parent position is (54+53)/2.
        expected = abs(sum([(54+53)/2, 1, 2, 3, 4])/5 - sum(range(5, 10))/5)
        self.assertEqual(expected, result['executed_drift_lever_slots']['1'])
        self.assertEqual(result, c.check_executed(g, roster, p,
                         keys | {('big:on:1:0:single:0', 2)}))

    def test_INV_31_innocent_initial_reschedule(self):
        g, root, r, p = mixed_initial_roster()
        self.assertEqual([], c.check_roster(g, root, p))
        self.assertEqual([], c.check_roster(g, r, p))
        self.assertEqual([], c.check_transition(g, root, r, p))
        wrong = deepcopy(r)
        wrong['placements'][-1]['envelope_index'] = 2
        seal(wrong)
        self.assertRow('INV-31', g=g, r=wrong, p=p)
        self.assertRow('INV-34', g=g, r=wrong, p=p)

    def test_split_and_completed_single_rows(self):
        g, split, p = split_roster()
        self.assertEqual([], c.check_roster(g, split, p))
        mutations = {
            'INV-19': lambda r: r['placements'][-1].update(envelope_index=51),
            'INV-23': lambda r: r['blocks'][-1].update(predicted_s=29.0),
            'INV-32': lambda r: r['blocks'][0].update(superseded=False),
        }
        for row, change in mutations.items():
            with self.subTest(row=row):
                wrong = deepcopy(split)
                change(wrong)
                seal(wrong)
                self.assertRow(row, g=g, r=wrong, p=p)
        single = completed_culprit_single(g, split)
        self.assertEqual([], c.check_roster(g, single, p))
        self.assertTrue(single['blocks'][-2]['late'])
        wrong = deepcopy(single)
        wrong['blocks'][-2]['late'] = False
        seal(wrong)
        self.assertRow('INV-33/43', g=g, r=wrong, p=p)

    def test_refuter_R1_cases_1_and_2(self):
        g, mixed, p = r1_mixed_stage_base()
        self.assertEqual([], c.check_roster(g, mixed, p))
        accepted = r1_case_one(g, mixed)
        self.assertEqual([], c.check_roster(g, accepted, p))
        self.assertEqual('reschedule', accepted['events'][-1]['observations'][1]['decision'])
        self.assertFalse(any(t['item_id'] == 'L1I0' for t in accepted['terminal_refusals']))
        # The exact case-2 order in R1 is cut_off B then completed single.
        # FT-14, adopted afterward, rejects that physical execution order.
        rejected = deepcopy(mixed)
        e = rejected['envelopes'][50]
        b, single = e['blocks']
        obs = [dict(block_id=b, status='cut_off', elapsed_s=5.0, decision='reschedule'),
               dict(block_id=single, status='completed', elapsed_s=45.0, decision='advance')]
        e['observations'] = deepcopy(obs)
        rejected['events'].append(dict(envelope_index=50, block_ids=[b, single], observations=obs, placements=[], sha256='0'*64))
        seal(rejected)
        self.assertRow('INV-47', g=g, r=rejected, p=p)
        minimal = deepcopy(accepted)
        minimal['events'][-1]['observations'][0]['status'] = 'cut_off'
        minimal['envelopes'][50]['observations'][0]['status'] = 'cut_off'
        seal(minimal)
        self.assertRow('INV-47', g=g, r=minimal, p=p)

    def test_refuter_R2_four_envelopes(self):
        g, roster, p = r2_four_envelope_roster()
        self.assertEqual([], c.check_roster(g, roster, p))
        tail = roster['events'][-4:]
        self.assertEqual([3, 3, 2, 2], [sum(o['decision'] == 'reschedule' for o in e['observations']) for e in tail])
        self.assertEqual(10, sum(o['decision'] == 'reschedule' for e in tail for o in e['observations']))
        self.assertEqual(2, sum(t['type'] == 'ceiling_violation' for t in roster['terminal_refusals']))
        self.assertEqual('ceiling_violation', roster['blocks'][50]['retry_stage'])
        self.assertEqual('ceiling_violation', roster['blocks'][51]['retry_stage'])
        # Parent 0 still has two live singles at 56; RD-4 positions it at
        # (56+56)/2. The remaining big parents are at 1..4, small at 5..9.
        self.assertEqual(abs(sum([56, 1, 2, 3, 4])/5 - sum(range(5, 10))/5),
                         roster['drift_lever_slots']['1'])
        self.assertTrue(roster['planned_spread_shortfall']['big:1'])
        # A third culprit observation for A crosses FT-2's per-item limit.
        wrong = deepcopy(roster)
        probe = deepcopy(tail[0]); probe['envelope_index'] = 56
        wrong['events'].append(probe)
        seal(wrong)
        self.assertRow('INV-35', g=g, r=wrong, p=p)

    def test_gate_45_P5b_P5c_and_PC_empty_envelope(self):
        g, split, p = split_roster(capacity=50)
        self.assertEqual([], c.check_roster(g, split, p))
        retry = split['placements'][50]
        self.assertEqual(50.0, retry['reserved_s'])  # W: min(60, 50)
        self.assertEqual(8.0, split['blocks'][0]['predicted_s'])
        e = split['envelopes'][51]  # PC: reported, empty, voided whole retry
        self.assertEqual([], e['blocks'])
        self.assertEqual(['big:on:1:0'], e['voided_block_ids'])
        self.assertNotIn('INV-15', {v.inv_id for v in c.check_roster(g, split, p)})
        g90, siblings, p90 = split_roster(capacity=90)
        self.assertEqual([], c.check_roster(g90, siblings, p90))
        self.assertEqual(2, len(siblings['envelopes'][52]['blocks']))  # P5b
        cross = deepcopy(siblings)
        cross['blocks'][-1]['parent_block_id'] = 'big:on:1:1'  # P5c
        seal(cross)
        self.assertRow('INV-24', g=g90, r=cross, p=p90)

    def test_INV_35a_reschedule_without_culprit_code(self):
        g, _, roster, p = mixed_initial_roster()
        wrong = deepcopy(roster)
        observations = wrong['events'][0]['observations']
        observations[0].update(status='cut_off', elapsed_s=4.0, decision='reschedule')
        observations[1]['decision'] = 'keep'  # Only one reschedule: INV-35(c) stays quiet.
        wrong['envelopes'][0]['observations'] = deepcopy(observations)
        seal(wrong)
        found = {(v.inv_id, v.code) for v in c.check_roster(g, wrong, p)}
        self.assertIn(('INV-35', 'reschedule_without_culprit'), found)
        self.assertNotIn(('INV-35', 'inv_35c'), found)

    def test_INV_35c_excess_reschedules_code(self):
        g, _, roster, p = mixed_initial_roster()
        wrong = deepcopy(roster)
        wrong['events'][0]['observations'][0]['decision'] = 'reschedule'
        wrong['envelopes'][0]['observations'] = deepcopy(wrong['events'][0]['observations'])
        seal(wrong)
        found = {(v.inv_id, v.code) for v in c.check_roster(g, wrong, p)}
        self.assertIn(('INV-35', 'inv_35c'), found)
        self.assertNotIn(('INV-35', 'reschedule_without_culprit'), found)

    def test_eligibility_excludes_whole_block_and_same_cell_parent(self):
        g, root, _ = fixture()
        advanced = advance_first(g, root)
        parent = next(b for b in advanced['blocks'] if b['block_id'] == 'big:on:1:0')
        # Envelope 2 has another level-1 parent; envelope 10 is the first fit.
        self.assertEqual(10, c._eligible(g, advanced, 0, parent, 4.0))
        for index in range(1, 50):
            advanced = report_keep(advanced, index)
        other_level = next(b for b in advanced['blocks'] if b['block_id'] == 'big:on:2:0')
        # Envelope 50 is idle; 51 has a whole-block retry, so use fresh 52.
        self.assertEqual(52, c._eligible(g, advanced, 50, other_level, 4.0))

    def test_culprit_strict_elapsed_boundary(self):
        block = self.r['blocks'][0]
        at_bound = dict(block_id=block['block_id'], status='cut_off',
                        elapsed_s=block['predicted_s'])
        self.assertEqual('unattributed_overrun', c._decide(self.g, block, at_bound, False))

    def test_planned_shortfall_requires_five_distinct_envelopes(self):
        roster = deepcopy(self.r)
        moved = roster['envelopes'][2]['blocks'].pop()
        roster['envelopes'][0]['blocks'].append(moved)
        roster['placements'][2]['envelope_index'] = 0
        # Deliberately isolate the derived predicate from static M8/INV-15.
        short, _ = c._derived(self.g, roster)
        self.assertTrue(short['big:1'])
        refresh_derived(self.g, roster)
        self.assertTrue(roster['planned_spread_shortfall']['big:1'])

    def test_planned_lever_null_with_zero_nonterminal_parents(self):
        g, roster, _ = fixture(n=10, block_size=2)
        roster = deepcopy(roster)
        for parent in roster['blocks']:
            if parent['model'] == 'big' and parent['level'] == 1:
                roster['terminal_refusals'].append(dict(model='big', item_id=parent['items'][0]))
        # Every big parent still has a positioned item, but none is non-terminal.
        _, lever = c._derived(g, roster)
        self.assertIsNone(lever['1'])
        refresh_derived(g, roster)
        self.assertIsNone(roster['drift_lever_slots']['1'])

    def test_registered_descendant_requires_claim_ready(self):
        descendant = keep_first(self.g, self.r)
        descendant['claim_ready'] = False
        seal(descendant)
        self.assertRow('INV-05', r=descendant)


if __name__ == '__main__':
    unittest.main()
