"""Independent, stdlib-only oracle for the A291 scored roster wire contract.

No production module is imported.  A malformed value yields violations, never an
exception.  Replay starts from pack-time placements in the supplied roster; it
never chooses the packer's initial search arrangement.
"""
from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy
import hashlib
from itertools import groupby, product
import json
import math
from operator import itemgetter
import re


@dataclass(frozen=True)
class Violation:
    inv_id: str
    code: str
    detail: str


ROWS = {
    'INV-01': 'registration digest binds the roster',
    'INV-02': 'roster digest equals canonical preimage',
    'INV-03': 'record key sets are exact',
    'INV-04': 'flat item digest and level count are derived',
    'INV-05': 'claim readiness follows mode and entry',
    'INV-06': 'selected arm keys and bounds are coherent',
    'INV-07': 'predictions are exact and bounded',
    'INV-08': 'prediction digest matches parent values',
    'INV-09': 'level keys and item identities are exact',
    'INV-10': 'parents are consecutive registered slices',
    'INV-11': 'every model item has one live or terminal owner',
    'INV-12': 'singles partition a superseded parent',
    'INV-14': 'envelopes contain only their model',
    'INV-15': 'empty loaded envelopes have voided history',
    'INV-16': 'idle slots are empty and unreported',
    'INV-17': 'envelope indices equal list positions',
    'INV-18': 'reports increase and new placements are later',
    'INV-19': 'split never reuses its reporting envelope',
    'INV-20': 'all reservations fit capacity',
    'INV-21': 'initial and rescheduled reservations are exact',
    'INV-22': 'whole retries reserve worst sum alone in fresh slot',
    'INV-23': 'single prediction and reservation equal worst',
    'INV-24': 'distinct parents of a cell do not share slots',
    'INV-25': 'root has five parents and five envelopes per cell',
    'INV-26': 'executed spread uses fully counted parents',
    'INV-27': 'planned drift lever is derived',
    'INV-28': 'registered root planned drift is within max gap',
    'INV-29': 'events record every observation in block order',
    'INV-30': 'decisions and late flags follow observations',
    'INV-31': 'innocent initial blocks reschedule to first eligible',
    'INV-32': 'whole block cut offs split into ordered singles',
    'INV-33/43': 'completed culprit singles void their attempts',
    'INV-34': 'event placements take the first eligible slot',
    'INV-35': 'reschedules have culprits and culprit limits hold',
    'INV-36': 'stage histories and attempt increments are legal',
    'INV-37': 'terminal refusals identify voided item attempts',
    'INV-38': 'event log is append only with exact digest chain',
    'INV-41': 'root idle insertion follows odd counts and roles',
    'INV-45': 'executed drift uses counted live windows',
    'INV-46': 'reported loaded envelopes form the first prefix',
    'INV-47': 'observations follow completed cut off not started order',
    'INV-48': 'event elapsed total fits interior',
    'INV-49': 'planned spread shortfall is derived',
    'INV-50': 'role order controls ordered roster lists',
    'INV-51': 'registration has exact schema and domains',
    'INV-52': 'roster field types and domains are valid',
}
NOT_CHECKABLE = {
    'INV-13': 'Moved to A292 item rows; no A291 roster field.',
    'INV-39': 'Re-pack equality needs the future pack implementation.',
    'INV-40': 'Seal call placement is an implementation-source property.',
    'INV-44': 'Constant sweep and duplicate scan need implementation source.',
}
# INV-50's insertion-order permutation clause also needs pack and is excluded
# from the checker predicate, per 31 X-9.

ROSTER_KEYS = set('schema registration_sha256 claim_ready item_set_sha256 n_per_level blocks envelopes placements terminal_refusals events drift_lever_slots planned_spread_shortfall registered_sha256 sha256'.split())
REG_KEYS = set('schema mode registration_id plan_id scorer_id arm arm_to_family role_to_model_id sizing_receipt_sha256 predictions_sha256 alpha n_boot seed floor_j anchor_j cap_tokens block_size item_ids_by_level envelope_s interior_s pitch_s offset_s guard_s s_per_token_upper prefill_s ceiling_s delta_upper_j_per_block_slot budget_j declared_sensitivities'.split())
BLOCK_KEYS = set('block_id model level items predicted_item_s predicted_s attempt retry_stage parent_block_id superseded late'.split())
ENV_KEYS = set('index model kind blocks voided_block_ids observations'.split())
PLACEMENT_KEYS = set('block_id attempt stage reserved_s envelope_index'.split())
OBS_KEYS = set('block_id status elapsed_s decision'.split())
EVENT_KEYS = set('envelope_index block_ids observations placements sha256'.split())
TERM_KEYS = set('type block_id attempt parent_block_id item_id model level'.split())
LEVELS = range(1, 6)
STAGES = {'initial', 'whole_block', 'single_problem', 'single_retry', 'ceiling_violation'}
HEX = re.compile(r'^[0-9a-f]{64}$')


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def canon_sha(value):
    return hashlib.sha256(canon(value)).hexdigest()


def preimage(roster):
    value = deepcopy(roster)
    value.pop('sha256', None)
    value.pop('registered_sha256', None)
    for event in value.get('events', []):
        event.pop('sha256', None)
    return value


def digest(roster):
    return canon_sha(preimage(roster))


def _num(v):
    return type(v) in (int, float) and math.isfinite(v)


def _int(v):
    return type(v) is int


def _hex(v):
    return isinstance(v, str) and HEX.fullmatch(v) is not None


def _bad(out, row, detail, code=None):
    out.append(Violation(row, code or row.lower().replace('-', '_').replace('/', '_'), detail))


def _roles(g):
    x = g['role_to_model_id']
    return (x['8B'], x['1.7B'])


def _items(g):
    return [item for level in LEVELS for item in g['item_ids_by_level'][str(level)]]


def _worst(g, model):
    arm = g['arm']
    return g['cap_tokens'][arm] * g['s_per_token_upper'][model][arm] + g['prefill_s'][model][arm]


def _cap(g):
    return g['interior_s'] - g['guard_s']


def _gap(g):
    if g['budget_j'] is None or g['delta_upper_j_per_block_slot'] is None:
        return None
    n = len(g['item_ids_by_level']['1'])
    return g['budget_j'] / (g['delta_upper_j_per_block_slot'] * math.ceil(n / g['block_size'][g['arm']]))


def _check_registration_impl(registration):
    out = []
    g = registration
    if not isinstance(g, dict) or set(g) != REG_KEYS:
        _bad(out, 'INV-51', 'registration key set', 'inv_51')
        return out
    try:
        canon(g)
        for key in ('registration_id', 'plan_id', 'scorer_id', 'arm'):
            assert isinstance(g[key], str) and bool(g[key])
        assert g['schema'] == 'joulewise.scored_registration.v2'
        assert g['mode'] in ('pilot', 'registered')
        assert isinstance(g['arm_to_family'], dict) and g['arm_to_family']
        assert all(isinstance(k, str) and k and isinstance(v, str) and v for k, v in g['arm_to_family'].items())
        assert g['arm'] in g['arm_to_family']
        assert set(g['role_to_model_id']) == {'8B', '1.7B'}
        assert all(isinstance(x, str) and x for x in _roles(g)) and len(set(_roles(g))) == 2
        for key in ('sizing_receipt_sha256', 'predictions_sha256'):
            assert _hex(g[key]) or (g['mode'] == 'pilot' and g[key] is None)
        assert _num(g['alpha']) and 0 < g['alpha'] <= 1
        assert _int(g['n_boot']) and g['n_boot'] >= 1
        assert _int(g['seed']) and g['seed'] >= 0
        assert all(_num(g[k]) and g[k] >= 0 for k in ('floor_j', 'anchor_j', 'offset_s', 'guard_s'))
        assert all(_num(g[k]) and g[k] > 0 for k in ('envelope_s', 'interior_s', 'pitch_s'))
        assert isinstance(g['declared_sensitivities'], list) and bool(g['declared_sensitivities'])
        assert all(isinstance(x, str) and x for x in g['declared_sensitivities'])
        assert (_num(g['delta_upper_j_per_block_slot']) and g['delta_upper_j_per_block_slot'] > 0) or (g['mode'] == 'pilot' and g['delta_upper_j_per_block_slot'] is None)
        assert (_num(g['budget_j']) and g['budget_j'] >= 0) or (g['mode'] == 'pilot' and g['budget_j'] is None)
        assert g['offset_s'] + g['interior_s'] <= g['envelope_s']
        assert g['pitch_s'] >= g['envelope_s']
    except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
        _bad(out, 'INV-51', 'registration domain or coherence')
    levels = g['item_ids_by_level']
    if not isinstance(levels, dict) or set(levels) != {str(i) for i in LEVELS}:
        _bad(out, 'INV-09', 'level keys', 'item_ids_by_level_keys')
    else:
        try:
            assert all(isinstance(v, list) and v and all(isinstance(x, str) and x for x in v) for v in levels.values())
            assert len(set(_items(g))) == len(_items(g))
        except (AssertionError, TypeError):
            _bad(out, 'INV-09', 'item ids must be nonempty and unique')
        if len({len(v) for v in levels.values() if isinstance(v, list)}) != 1:
            _bad(out, 'INV-04', 'unequal level sizes', 'unequal_level_sizes')
    try:
        a = g['arm']
        for key in ('cap_tokens', 'block_size'):
            assert isinstance(g[key], dict) and set(g[key]) == {a}
            assert _int(g[key][a]) and g[key][a] >= 1
        for key in ('s_per_token_upper', 'prefill_s', 'ceiling_s'):
            assert isinstance(g[key], dict) and set(g[key]) == set(_roles(g))
            for m in _roles(g):
                assert isinstance(g[key][m], dict) and set(g[key][m]) == {a}
                x = g[key][m][a]
                assert _num(x) and (x >= 0 if key == 'prefill_s' else x > 0)
        for m in _roles(g):
            assert _worst(g, m) <= g['ceiling_s'][m][a] <= _cap(g)
    except (AssertionError, KeyError, TypeError, ValueError):
        foreign = any(isinstance(g.get(k), dict) and set(g[k]) != {g['arm']} for k in ('cap_tokens', 'block_size'))
        foreign |= any(isinstance(g.get(k), dict) and isinstance(g[k].get(m), dict) and set(g[k][m]) != {g['arm']} for k in ('s_per_token_upper', 'prefill_s', 'ceiling_s') for m in _roles(g))
        _bad(out, 'INV-06', 'selected arm keys or worst/ceiling/cap coherence', 'unselected_arm_entry' if foreign else 'inv_06')
    return out


def _check_predictions(g, p, out):
    try:
        assert isinstance(p, dict) and set(p) == set(_roles(g))
        for m in _roles(g):
            assert isinstance(p[m], dict) and set(p[m]) == set(_items(g))
            assert all(_num(v) and 0 < v <= _worst(g, m) for v in p[m].values())
        canon(p)
    except (AssertionError, KeyError, TypeError, ValueError):
        _bad(out, 'INV-07', 'prediction map domain')


def _parent_id(m, a, level, k):
    return f'{m}:{a}:{level}:{k}'


def _parents(g):
    b = g['block_size'][g['arm']]
    for level in LEVELS:
        ids = g['item_ids_by_level'][str(level)]
        for m in _roles(g):
            for k, start in enumerate(range(0, len(ids), b)):
                yield _parent_id(m, g['arm'], level, k), m, level, ids[start:start+b]


def _parent_of(block):
    return block['parent_block_id'] or block['block_id']


def _window_of(g, r, keys):
    """Map each registered (model, item) to the envelope index that locates it.

    An item is located by the one live listing of a non-superseded block that
    holds it.  Terminal items are never located.  With ``keys`` given, the
    live listing counts only when its (block_id, attempt) is a captured key.
    Anything other than exactly one live listing leaves the item unlocated;
    INV-11 reports that roster separately.
    """
    first = itemgetter(0)
    held = sorted(((b['model'], x), b['block_id']) for b in r['blocks'] if not b['superseded'] for x in b['items'])
    holders = {key: [bid for _, bid in run] for key, run in groupby(held, key=first)}
    shown = sorted((bid, e['index']) for e in r['envelopes'] for bid in e['blocks'])
    slots = {bid: [ix for _, ix in run] for bid, run in groupby(shown, key=first)}
    attempt_at = {(pl['block_id'], pl['envelope_index']): pl['attempt'] for pl in r['placements']}
    refused = set(map(itemgetter('model', 'item_id'), r['terminal_refusals']))
    located = {}
    for model, item in product(_roles(g), _items(g)):
        spots = [] if (model, item) in refused else [(bid, ix) for bid in holders.get((model, item), ()) for ix in slots.get(bid, ())]
        if len(spots) == 1 and (keys is None or (spots[0][0], attempt_at.get(spots[0])) in keys):
            located[model, item] = spots[0][1]
    return located, refused


def _derived(g, r, keys=None):
    """Return (cell flags, lever) from registered items, per A291-POP-1.

    The outer walk is over (model, item).  An item's parent is its registered
    slice ``position // block_size`` within its level.  Planned mode (keys is
    None): a parent passes the gate when none of its items is refused; the
    flags are planned_spread_shortfall.  Executed mode: a parent passes the
    gate when every item is located by a captured window; the flags are
    spread_exceeded.  A parent with at least one located item has a position,
    the mean of its located indices in item order.
    """
    located, refused = _window_of(g, r, keys)
    width = g['block_size'][g['arm']]
    flags, means, gated = {}, {}, {}
    for level in LEVELS:
        ids = g['item_ids_by_level'][str(level)]
        for model in _roles(g):
            slices = [[] for _ in range(math.ceil(len(ids) / width))]
            clean = [True] * len(slices)
            for q, item in enumerate(ids):
                if (model, item) in located:
                    slices[q // width].append(located[(model, item)])
                if (keys is None and (model, item) in refused) or (keys is not None and (model, item) not in located):
                    clean[q // width] = False
            passing = [k for k in range(len(slices)) if clean[k]]
            occupied = {slot for k in passing for slot in slices[k]}
            flags[f'{model}:{level}'] = len(passing) < 5 or len(occupied) < 5
            spots = [sum(s) / len(s) for s in slices if s]
            means[(model, level)] = sum(spots) / len(spots) if spots else None
            gated[(model, level)] = bool(passing)
    lever = {}
    for level in LEVELS:
        big, small = (means[(model, level)] for model in _roles(g))
        both = all(gated[(model, level)] for model in _roles(g))
        # A gated model without any position exists only when INV-11 fails.
        lever[str(level)] = abs(big - small) if both and big is not None and small is not None else None
    return flags, lever


def _root_from_final(g, r):
    event_indices = {i for ev in r['events'] for i in ev['placements']}
    initial = [(i, p) for i, p in enumerate(r['placements']) if i not in event_indices]
    if any(p['stage'] != 'initial' for _, p in initial):
        raise ValueError('root placement stage')
    # Every pack-time loaded envelope owns an initial placement; the sole idle
    # slot is pack-time too. Event-created envelopes own no initial placement.
    initial_envs = [p['envelope_index'] for _, p in initial]
    initial_envs += [i for i, e in enumerate(r['envelopes']) if e['kind'] == 'idle_slot']
    root_count = max(initial_envs, default=-1) + 1
    root = deepcopy(r)
    root['events'] = []
    root['terminal_refusals'] = []
    root['placements'] = [deepcopy(p) for _, p in initial]
    root['blocks'] = []
    byid = {b['block_id']: b for b in r['blocks']}
    for bid, _, _, _ in _parents(g):
        b = deepcopy(byid[bid])
        b.update(attempt=0, retry_stage='initial', superseded=False, late=False)
        root['blocks'].append(b)
    root['envelopes'] = deepcopy(r['envelopes'][:root_count])
    for e in root['envelopes']:
        e['blocks'] = []
        e['voided_block_ids'] = []
        e['observations'] = None
    for p in root['placements']:
        root['envelopes'][p['envelope_index']]['blocks'].append(p['block_id'])
    root['planned_spread_shortfall'], root['drift_lever_slots'] = _derived(g, root)
    root['sha256'] = digest(root)
    root['registered_sha256'] = root['sha256']
    return root


def _decide(g, block, obs, any_culprit):
    stage, status = block['retry_stage'], obs['status']
    culprit = _num(obs['elapsed_s']) and obs['elapsed_s'] > (block['predicted_s'] if stage in ('initial', 'whole_block') else _worst(g, block['model']))
    if status == 'completed':
        return 'advance' if culprit and stage in ('single_problem', 'single_retry') else 'keep'
    if stage == 'whole_block':
        return 'split' if status == 'cut_off' else 'unattributed_overrun'
    if culprit:
        return 'advance'
    return 'reschedule' if any_culprit else 'unattributed_overrun'


def _eligible(g, r, reporter, block, reserve):
    cap = _cap(g)
    last = max((ev['envelope_index'] for ev in r['events']), default=-1)
    for e in r['envelopes']:
        if e['index'] <= max(reporter, last) or e['observations'] is not None or e['kind'] != 'loaded' or e['model'] != block['model']:
            continue
        ids = e['blocks'] + e['voided_block_ids']
        bm = {b['block_id']: b for b in r['blocks']}
        if any(bm[x]['retry_stage'] == 'whole_block' for x in ids):
            continue
        if any(bm[x]['level'] == block['level'] and _parent_of(bm[x]) != _parent_of(block) for x in ids):
            continue
        if sum(p['reserved_s'] for p in r['placements'] if p['envelope_index'] == e['index']) + reserve > cap:
            continue
        return e['index']
    return len(r['envelopes'])


def _append_placement(r, block, target, reserve, indices):
    if target == len(r['envelopes']):
        r['envelopes'].append(dict(index=target, model=block['model'], kind='loaded', blocks=[], voided_block_ids=[], observations=None))
    p = dict(block_id=block['block_id'], attempt=block['attempt'], stage=block['retry_stage'], reserved_s=reserve, envelope_index=target)
    indices.append(len(r['placements']))
    r['placements'].append(p)
    r['envelopes'][target]['blocks'].append(block['block_id'])


def _apply(g, r, event):
    r = deepcopy(r)
    ix = event['envelope_index']
    e = r['envelopes'][ix]
    ids = list(e['blocks'])
    bm = {b['block_id']: b for b in r['blocks']}
    obs = deepcopy(event['observations'])
    anyc = any(_num(o['elapsed_s']) and o['elapsed_s'] > (bm[o['block_id']]['predicted_s'] if bm[o['block_id']]['retry_stage'] in ('initial', 'whole_block') else _worst(g, bm[o['block_id']]['model'])) for o in obs)
    created = []
    recorded = []
    for bid, o in zip(ids, obs):
        b = bm[bid]
        oldstage = b['retry_stage']
        oldp = next(p for p in reversed(r['placements']) if p['block_id'] == bid)
        dec = _decide(g, b, o, anyc)
        rec = dict(block_id=bid, status=o['status'], elapsed_s=o['elapsed_s'], decision=dec)
        recorded.append(rec)
        b['late'] = o['status'] == 'completed' and _num(o['elapsed_s']) and o['elapsed_s'] > (b['predicted_s'] if oldstage in ('initial', 'whole_block') else _worst(g, b['model']))
        if dec == 'keep':
            continue
        e['blocks'].remove(bid)
        e['voided_block_ids'].append(bid)
        if dec in ('unattributed_overrun', 'advance') and (dec == 'unattributed_overrun' or oldstage == 'single_retry'):
            kind = 'unattributed_overrun' if dec == 'unattributed_overrun' else 'ceiling_violation'
            if kind == 'ceiling_violation':
                b['retry_stage'] = 'ceiling_violation'
            for item in b['items']:
                r['terminal_refusals'].append(dict(type=kind, block_id=bid, attempt=oldp['attempt'], parent_block_id=b['parent_block_id'], item_id=item, model=b['model'], level=b['level']))
        elif dec == 'split':
            b['superseded'] = True
            for j, item in enumerate(b['items']):
                s = dict(block_id=f'{bid}:single:{j}', model=b['model'], level=b['level'], items=[item], predicted_item_s=[b['predicted_item_s'][j]], predicted_s=_worst(g, b['model']), attempt=b['attempt'] + 1, retry_stage='single_problem', parent_block_id=bid, superseded=False, late=False)
                r['blocks'].append(s)
                reserve = _worst(g, s['model'])
                _append_placement(r, s, _eligible(g, r, ix, s, reserve), reserve, created)
        elif dec in ('advance', 'reschedule'):
            b['attempt'] += 1
            if dec == 'advance':
                b['retry_stage'] = {'initial': 'whole_block', 'single_problem': 'single_retry'}[oldstage]
            reserve = (min(sum(_worst(g, b['model']) for _ in b['items']), _cap(g)) if b['retry_stage'] == 'whole_block' and dec == 'advance' else _worst(g, b['model']) if dec == 'advance' else oldp['reserved_s'])
            target = len(r['envelopes']) if b['retry_stage'] == 'whole_block' and dec == 'advance' else _eligible(g, r, ix, b, reserve)
            _append_placement(r, b, target, reserve, created)
    e['observations'] = recorded
    r['planned_spread_shortfall'], r['drift_lever_slots'] = _derived(g, r)
    r['events'].append(dict(envelope_index=ix, block_ids=ids, observations=recorded, placements=created, sha256=''))
    r['sha256'] = digest(r)
    r['events'][-1]['sha256'] = r['sha256']
    return r


def _schema(r, out):
    if not isinstance(r, dict) or set(r) != ROSTER_KEYS:
        _bad(out, 'INV-03', 'top-level roster keys')
        return False
    shapes = [('blocks', BLOCK_KEYS), ('envelopes', ENV_KEYS), ('placements', PLACEMENT_KEYS), ('terminal_refusals', TERM_KEYS), ('events', EVENT_KEYS)]
    for name, keys in shapes:
        if not isinstance(r[name], list):
            _bad(out, 'INV-52', f'{name} is not a list')
            return False
        for i, row in enumerate(r[name]):
            if not isinstance(row, dict) or set(row) != keys:
                _bad(out, 'INV-03', f'{name}[{i}] keys')
                return False
    for e in r['envelopes']:
        if e['observations'] is not None:
            if not isinstance(e['observations'], list):
                _bad(out, 'INV-52', 'envelope observations type')
                return False
            for o in e['observations']:
                if not isinstance(o, dict) or set(o) != OBS_KEYS:
                    _bad(out, 'INV-03', 'envelope observation keys')
                    return False
    for ev in r['events']:
        if not isinstance(ev['observations'], list):
            _bad(out, 'INV-52', 'event observations type')
            return False
        for o in ev['observations']:
            if not isinstance(o, dict) or set(o) != OBS_KEYS:
                _bad(out, 'INV-03', 'event observation keys')
                return False
    return True


def _types(g, r, out):
    try:
        canon(r)
        assert r['schema'] == 'joulewise.scored_roster.v3'
        assert _hex(r['registration_sha256']) and _hex(r['item_set_sha256'])
        assert _hex(r['registered_sha256']) and _hex(r['sha256'])
        assert type(r['claim_ready']) is bool and _int(r['n_per_level'])
        assert isinstance(r['drift_lever_slots'], dict) and set(r['drift_lever_slots']) == {str(i) for i in LEVELS}
        assert all(x is None or _num(x) for x in r['drift_lever_slots'].values())
        assert isinstance(r['planned_spread_shortfall'], dict) and set(r['planned_spread_shortfall']) == {f'{m}:{i}' for m in _roles(g) for i in LEVELS}
        assert all(type(x) is bool for x in r['planned_spread_shortfall'].values())
        for b in r['blocks']:
            assert isinstance(b['block_id'], str) and isinstance(b['model'], str) and b['model'] in _roles(g)
            assert _int(b['level']) and b['level'] in LEVELS
            assert isinstance(b['items'], list) and all(isinstance(x, str) for x in b['items'])
            assert isinstance(b['predicted_item_s'], list) and len(b['predicted_item_s']) == len(b['items']) and all(_num(x) for x in b['predicted_item_s'])
            assert _num(b['predicted_s']) and _int(b['attempt']) and b['attempt'] >= 0
            assert b['retry_stage'] in STAGES and (b['parent_block_id'] is None or isinstance(b['parent_block_id'], str))
            assert type(b['superseded']) is bool and type(b['late']) is bool
        for e in r['envelopes']:
            assert _int(e['index']) and e['model'] in _roles(g) and e['kind'] in ('loaded', 'idle_slot')
            assert isinstance(e['blocks'], list) and isinstance(e['voided_block_ids'], list)
            assert all(isinstance(x, str) for x in e['blocks'] + e['voided_block_ids'])
        for p in r['placements']:
            assert isinstance(p['block_id'], str) and _int(p['attempt']) and p['attempt'] >= 0
            assert p['stage'] in STAGES - {'ceiling_violation'} and _num(p['reserved_s']) and p['reserved_s'] > 0
            assert _int(p['envelope_index']) and 0 <= p['envelope_index'] < len(r['envelopes'])
        for t in r['terminal_refusals']:
            assert t['type'] in ('ceiling_violation', 'unattributed_overrun')
            assert isinstance(t['block_id'], str) and _int(t['attempt']) and t['attempt'] >= 0
            assert t['parent_block_id'] is None or isinstance(t['parent_block_id'], str)
            assert isinstance(t['item_id'], str) and t['model'] in _roles(g) and _int(t['level']) and t['level'] in LEVELS
        for ev in r['events']:
            assert _int(ev['envelope_index']) and 0 <= ev['envelope_index'] < len(r['envelopes'])
            assert isinstance(ev['block_ids'], list) and all(isinstance(x, str) for x in ev['block_ids'])
            assert isinstance(ev['placements'], list) and all(_int(x) and 0 <= x < len(r['placements']) for x in ev['placements'])
            assert _hex(ev['sha256'])
        for o in [o for e in r['envelopes'] if e['observations'] is not None for o in e['observations']] + [o for ev in r['events'] for o in ev['observations']]:
            assert isinstance(o['block_id'], str) and o['status'] in ('completed', 'cut_off', 'not_started')
            assert o['decision'] in ('keep', 'advance', 'split', 'reschedule', 'unattributed_overrun')
            if not ((o['elapsed_s'] is None) if o['status'] == 'not_started' else (_num(o['elapsed_s']) and o['elapsed_s'] > 0)):
                _bad(out, 'INV-29', 'invalid observation elapsed', 'invalid_elapsed')
                return False
    except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
        _bad(out, 'INV-52', 'record type or domain')
        return False
    return True


def _static_checks(g, r, p, out):
    models = _roles(g)
    ids = _items(g)
    if r['registration_sha256'] != canon_sha(g):
        _bad(out, 'INV-01', 'registration digest')
    if r['item_set_sha256'] != canon_sha(ids) or r['n_per_level'] != len(g['item_ids_by_level']['1']):
        _bad(out, 'INV-04', 'derived item identity')
    if g['mode'] == 'pilot' and r['claim_ready'] or g['mode'] != 'pilot' and not r['claim_ready'] and r['events']:
        _bad(out, 'INV-05', 'claim_ready')
    if r['sha256'] != digest(r):
        _bad(out, 'INV-02', 'self digest')
    if p is not None:
        _check_predictions(g, p, out)
    if g['predictions_sha256'] is not None:
        try:
            pred = {m: {} for m in models}
            for b in r['blocks']:
                if b['parent_block_id'] is None:
                    pred[b['model']].update(zip(b['items'], b['predicted_item_s']))
            if canon_sha(pred) != g['predictions_sha256'] or p is not None and canon_sha(p) != g['predictions_sha256']:
                _bad(out, 'INV-08', 'prediction digest')
        except (TypeError, ValueError):
            _bad(out, 'INV-08', 'prediction digest construction')
    expected = list(_parents(g))
    parents = [b for b in r['blocks'] if b['parent_block_id'] is None]
    if len(parents) != len(expected) or any((b['block_id'], b['model'], b['level'], b['items']) != x for b, x in zip(parents, expected)):
        _bad(out, 'INV-10', 'parent order, id, model, level or slice')
    bm = {b['block_id']: b for b in r['blocks']}
    if len(bm) != len(r['blocks']):
        _bad(out, 'INV-10', 'duplicate block ids')
    for b in parents:
        if p is not None and b['model'] in p and all(x in p[b['model']] for x in b['items']):
            if b['predicted_item_s'] != [p[b['model']][i] for i in b['items']]:
                _bad(out, 'INV-07', 'parent prediction differs from supplied map')
        if any(not _num(v) or v <= 0 or v > _worst(g, b['model']) for v in b['predicted_item_s']):
            _bad(out, 'INV-07', 'parent prediction bound')
        if b['predicted_s'] != sum(b['predicted_item_s']):
            _bad(out, 'INV-21', 'parent predicted sum')
    for b in r['blocks']:
        if b['parent_block_id'] is not None:
            parent = bm.get(b['parent_block_id'])
            if parent is None or not parent['superseded'] or len(b['items']) != 1 or b['model'] != parent['model'] or b['level'] != parent['level'] or not any(b['block_id'] == f"{parent['block_id']}:single:{j}" and b['items'] == [item] and b['predicted_item_s'] == [parent['predicted_item_s'][j]] for j, item in enumerate(parent['items'])):
                _bad(out, 'INV-12', f"single relation {b['block_id']}")
            if b['predicted_s'] != _worst(g, b['model']):
                _bad(out, 'INV-23', 'single predicted_s')
    for b in parents:
        singles = [x for x in r['blocks'] if x['parent_block_id'] == b['block_id']]
        if b['superseded'] and [x['items'][0] for x in singles] != b['items'] or not b['superseded'] and singles:
            _bad(out, 'INV-12', 'single partition')
    if [b['block_id'] for b in r['blocks'][:len(parents)]] != [x[0] for x in expected]:
        _bad(out, 'INV-50', 'parent list role order')
    live_ids = [x for e in r['envelopes'] for x in e['blocks']]
    if any(live_ids.count(x) != 1 for x in set(live_ids)):
        _bad(out, 'INV-11', 'live block appears in multiple envelopes')
    if len({(p['block_id'], p['envelope_index']) for p in r['placements']}) != len(r['placements']):
        _bad(out, 'INV-03', 'duplicate block/envelope placement')
    event_placement_ids = {i for event in r['events'] for i in event['placements']}
    initial_indices = [i for i in range(len(r['placements'])) if i not in event_placement_ids]
    initial_envelopes = [r['placements'][i]['envelope_index'] for i in initial_indices]
    if initial_indices != list(range(len(initial_indices))) or initial_envelopes != sorted(initial_envelopes):
        _bad(out, 'INV-38', 'pack-time placements not first in envelope order')
    # INV-11 (v4.1 closed form): count every live (block, envelope) listing,
    # including superseded blocks, and retain terminal-entry multiplicity.
    live = {}
    for e in r['envelopes']:
        for bid in e['blocks']:
            block = bm[bid]
            for item in set(block['items']):
                live.setdefault((block['model'], item), []).append((block, e))
    terms = {}
    for entry in r['terminal_refusals']:
        terms.setdefault((entry['model'], entry['item_id']), []).append(entry)
    for m in models:
        for item in ids:
            holders = live.get((m, item), ())
            named = terms.get((m, item), ())
            owned = (len(holders), len(named)) == (1, 0)
            if owned:
                block = holders[0][0]
                owned = (not block['superseded'] and
                         not any(terms.get((m, held)) for held in block['items']))
            refused = (len(holders), len(named)) == (0, 1)
            if not (owned or refused):
                _bad(out, 'INV-11', f'item ownership {m}:{item}')
    for i, e in enumerate(r['envelopes']):
        if e['index'] != i:
            _bad(out, 'INV-17', f'envelope index {i}')
        if e['kind'] == 'idle_slot':
            if e['blocks'] or e['voided_block_ids'] or e['observations'] is not None or any(x['envelope_index'] == i for x in r['placements']):
                _bad(out, 'INV-16', f'idle slot {i}')
        elif not e['blocks'] and not e['voided_block_ids']:
            _bad(out, 'INV-15', f'empty loaded envelope {i}')
        listed = e['blocks'] + e['voided_block_ids']
        pl = [x for x in r['placements'] if x['envelope_index'] == i]
        if len(set(listed)) != len(listed) or len(pl) != len(listed) or set(listed) != {x['block_id'] for x in pl}:
            _bad(out, 'INV-03', f'placement and envelope ids {i}')
        if any(bm[x['block_id']]['model'] != e['model'] for x in pl if x['block_id'] in bm):
            _bad(out, 'INV-14', f'model homogeneity {i}')
        if sum(x['reserved_s'] for x in pl) > _cap(g):
            _bad(out, 'INV-20', f'capacity {i}')
        for lv in LEVELS:
            distinct = [_parent_of(bm[x['block_id']]) for x in pl if x['block_id'] in bm and bm[x['block_id']]['level'] == lv]
            if len(set(distinct)) > 1:
                _bad(out, 'INV-24', f'M8 {i}:{lv}')
    by_block = {}
    for placement in r['placements']:
        by_block.setdefault(placement['block_id'], []).append(placement)
    for b in r['blocks']:
        history = by_block.get(b['block_id'], [])
        if not history or b['attempt'] != history[-1]['attempt']:
            _bad(out, 'INV-36', f"latest attempt {b['block_id']}")
        elif b['parent_block_id'] is None:
            if history[0]['stage'] != 'initial' or history[0]['attempt'] != 0 or any(y['attempt'] != x['attempt'] + 1 for x, y in zip(history, history[1:])):
                _bad(out, 'INV-36', f"parent attempt history {b['block_id']}")
        else:
            parent_history = by_block.get(b['parent_block_id'], [])
            if not parent_history or history[0]['attempt'] != parent_history[-1]['attempt'] + 1 or history[0]['stage'] != 'single_problem' or any(y['attempt'] != x['attempt'] + 1 for x, y in zip(history, history[1:])):
                _bad(out, 'INV-36', f"single attempt history {b['block_id']}")
    for i, placement in enumerate(r['placements']):
        b = bm.get(placement['block_id'])
        if b is None:
            _bad(out, 'INV-11', f'unknown placement block {i}')
            continue
        if placement['stage'] == 'initial' and placement['attempt'] == 0 and placement['reserved_s'] != b['predicted_s']:
            _bad(out, 'INV-21', f'initial reservation {i}')
        if placement['stage'] in ('single_problem', 'single_retry') and placement['reserved_s'] != _worst(g, b['model']):
            _bad(out, 'INV-23', f'single reservation {i}')
        if placement['stage'] == 'whole_block':
            expect = min(sum(_worst(g, b['model']) for _ in b['items']), _cap(g))
            if placement['reserved_s'] != expect or len([x for x in r['placements'] if x['envelope_index'] == placement['envelope_index']]) != 1:
                _bad(out, 'INV-22', f'whole retry reservation/solitude {i}')
    for t in r['terminal_refusals']:
        b = bm.get(t['block_id'])
        if b is None or t['item_id'] not in b['items'] or t['model'] != b['model'] or t['level'] != b['level'] or t['parent_block_id'] != b['parent_block_id'] or not any(x['block_id'] == t['block_id'] and x['attempt'] == t['attempt'] and t['block_id'] in r['envelopes'][x['envelope_index']]['voided_block_ids'] for x in r['placements']):
            _bad(out, 'INV-37', 'terminal does not name voided item attempt')
    if len(terms) != len(r['terminal_refusals']):
        _bad(out, 'INV-37', 'duplicate terminal item')
    short, lever = _derived(g, r)
    if r['planned_spread_shortfall'] != short:
        _bad(out, 'INV-49', 'stale planned spread', 'stale_derived')
    if canon(r['drift_lever_slots']) != canon(lever):
        _bad(out, 'INV-27', 'stale planned drift')
    if not r['events']:
        if any(short.values()):
            _bad(out, 'INV-25', 'root spread minima', 'spread_minima')
        gap = _gap(g)
        if g['mode'] == 'registered' and gap is not None and any(x is not None and x > gap for x in lever.values()):
            _bad(out, 'INV-28', 'root planned drift exceeds max gap')
        # Root counts ignore an idle slot and are based on loaded envelopes.
        counts = [sum(e['kind'] == 'loaded' and e['model'] == m for e in r['envelopes']) for m in models]
        idle = [e for e in r['envelopes'] if e['kind'] == 'idle_slot']
        if len(idle) != int(all(x % 2 for x in counts)) or any(e['model'] != models[1] for e in idle):
            _bad(out, 'INV-41', 'root idle insertion')
        if idle and idle[0]['model'] != models[1]:
            _bad(out, 'INV-50', 'idle role')
    return bm


def _event_checks(g, r, out):
    reported = [e['envelope_index'] for e in r['events']]
    if reported != sorted(set(reported)):
        _bad(out, 'INV-18', 'event indices not strictly increasing', 'report_order')
    loaded = [i for i, e in enumerate(r['envelopes']) if e['kind'] == 'loaded']
    if reported != loaded[:len(reported)]:
        _bad(out, 'INV-46', 'reports are not the first loaded prefix', 'report_order')
    # FT-2 counts culprit observations, without a total-reschedule cap.
    culprit_counts = {}
    final_blocks = {b['block_id']: b for b in r['blocks']}
    for ev in r['events']:
        for obs in ev['observations']:
            b = final_blocks.get(obs['block_id'])
            if b is None or not _num(obs['elapsed_s']):
                continue
            if b['parent_block_id'] is not None and obs['elapsed_s'] > _worst(g, b['model']):
                key = (b['model'], b['items'][0])
                culprit_counts[key] = culprit_counts.get(key, 0) + 1
                if culprit_counts[key] > 2:
                    _bad(out, 'INV-35', f'single culprit limit {key}', 'culprit_limit')
            elif b['parent_block_id'] is None and any(p['block_id'] == b['block_id'] and p['envelope_index'] == ev['envelope_index'] and p['stage'] == 'initial' for p in r['placements']) and obs['elapsed_s'] > b['predicted_s']:
                key = (b['model'], b['block_id'])
                culprit_counts[key] = culprit_counts.get(key, 0) + 1
                if culprit_counts[key] > 1:
                    _bad(out, 'INV-35', f'parent initial culprit limit {key}', 'culprit_limit')
    for ev in r['events']:
        ix = ev['envelope_index']
        if r['envelopes'][ix]['kind'] != 'loaded' or r['envelopes'][ix]['observations'] != ev['observations']:
            _bad(out, 'INV-29', f'event/envelope observation mismatch {ix}')
        if ev['block_ids'] != [o['block_id'] for o in ev['observations']]:
            _bad(out, 'INV-29', f'event block order {ix}')
        phase = 0
        for o in ev['observations']:
            next_phase = {'completed': 0, 'cut_off': 1, 'not_started': 2}[o['status']]
            if next_phase < phase or next_phase == 1 and phase == 1:
                _bad(out, 'INV-47', f'observation order {ix}', 'invalid_observation_order')
                break
            phase = next_phase
        if sum(o['elapsed_s'] or 0 for o in ev['observations']) > g['interior_s']:
            _bad(out, 'INV-48', f'elapsed sum {ix}', 'invalid_elapsed')
        if sum(o['decision'] == 'reschedule' for o in ev['observations']) > len(ev['block_ids']) - 1:
            _bad(out, 'INV-35', f'reschedule count {ix}', 'inv_35c')
        for pi in ev['placements']:
            if r['placements'][pi]['envelope_index'] <= ix:
                _bad(out, 'INV-18', f'placement at or below reporter {ix}')
                if any(o['decision'] == 'split' for o in ev['observations']):
                    _bad(out, 'INV-19', f'split reused reporter {ix}')
    for i, e in enumerate(r['envelopes']):
        if e['kind'] == 'loaded' and (e['observations'] is None) != (i not in reported):
            _bad(out, 'INV-46', f'report completeness {i}')
    try:
        state = _root_from_final(g, r)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        _bad(out, 'INV-38', f'cannot reconstruct root: {exc}')
        return
    if state['sha256'] != r['registered_sha256']:
        _bad(out, 'INV-38', 'root digest differs from registered digest')
    root_out = []
    _static_checks(g, state, None, root_out)
    for v in root_out:
        if v.inv_id in ('INV-25', 'INV-28', 'INV-41'):
            out.append(v)
    for k, ev in enumerate(r['events']):
        ix = ev['envelope_index']
        if ix >= len(state['envelopes']) or state['envelopes'][ix]['kind'] != 'loaded' or state['envelopes'][ix]['observations'] is not None or ix != next((i for i, e in enumerate(state['envelopes']) if e['kind'] == 'loaded' and e['observations'] is None), None):
            _bad(out, 'INV-46', f'event {k} violates lowest unreported index', 'report_order')
            return
        if ev['block_ids'] != state['envelopes'][ix]['blocks']:
            _bad(out, 'INV-29', f'event {k} block_ids differ from pre-call blocks')
            return
        bm = {b['block_id']: b for b in state['blocks']}
        anyc = any(_num(o['elapsed_s']) and o['elapsed_s'] > (bm[o['block_id']]['predicted_s'] if bm[o['block_id']]['retry_stage'] in ('initial', 'whole_block') else _worst(g, bm[o['block_id']]['model'])) for o in ev['observations'])
        for o in ev['observations']:
            b = bm[o['block_id']]
            decision = _decide(g, b, o, anyc)
            if o['decision'] != decision:
                row = 'INV-32' if b['retry_stage'] == 'whole_block' else 'INV-33/43' if b['retry_stage'] in ('single_problem', 'single_retry') else 'INV-30'
                _bad(out, row, f"{o['block_id']}: {o['decision']} != {decision}")
            if o['decision'] == 'reschedule' and not anyc:
                _bad(out, 'INV-35', 'reschedule without culprit', 'reschedule_without_culprit')
        next_state = _apply(g, state, ev)
        expected = next_state['events'][-1]
        if ev['observations'] != expected['observations']:
            _bad(out, 'INV-30', f'event {k} recorded decisions')
        if ev['placements'] != expected['placements']:
            _bad(out, 'INV-34', f'event {k} placement indices')
        for pi in expected['placements']:
            if pi < len(r['placements']) and r['placements'][pi] != next_state['placements'][pi]:
                actual = r['placements'][pi]
                want = next_state['placements'][pi]
                b = next(b for b in next_state['blocks'] if b['block_id'] == want['block_id'])
                row = ('INV-22' if want['stage'] == 'whole_block' else 'INV-23' if b['parent_block_id'] is not None and want['stage'] == 'single_problem' else 'INV-31' if b['parent_block_id'] is None and want['stage'] == 'initial' else 'INV-34')
                _bad(out, row, f'event {k} placement {pi}: {actual} != {want}')
                if actual['envelope_index'] != want['envelope_index']:
                    _bad(out, 'INV-34', f'event {k} target for placement {pi}')
                if actual['attempt'] != want['attempt'] or actual['stage'] != want['stage']:
                    _bad(out, 'INV-36', f'event {k} stage/attempt for placement {pi}')
        if ev['sha256'] != next_state['sha256']:
            _bad(out, 'INV-38', f'event {k} digest')
        if k == len(r['events']) - 1 and next_state != r:
            if any(o['decision'] == 'split' for o in ev['observations']):
                _bad(out, 'INV-32', f'event {k} split effect')
            if any(o['status'] == 'completed' and o['decision'] == 'advance' and bm[o['block_id']]['parent_block_id'] is not None for o in ev['observations']):
                _bad(out, 'INV-33/43', f'event {k} completed culprit single effect')
            if any(o['decision'] == 'reschedule' and bm[o['block_id']]['parent_block_id'] is None for o in ev['observations']):
                _bad(out, 'INV-31', f'event {k} initial reschedule effect')
        state = next_state
    if state != r:
        if state['terminal_refusals'] != r['terminal_refusals']:
            _bad(out, 'INV-37', 'terminal refusal effects differ from replay')
        expected_blocks = {b['block_id']: b for b in state['blocks']}
        for block in r['blocks']:
            prior = expected_blocks.get(block['block_id'])
            if prior and block['late'] != prior['late']:
                _bad(out, 'INV-30', f"late flag {block['block_id']}")
            if prior and (block['attempt'], block['retry_stage']) != (prior['attempt'], prior['retry_stage']):
                _bad(out, 'INV-36', f"stage/attempt {block['block_id']}")
        _bad(out, 'INV-38', 'replayed final roster differs field for field')


def check_roster(registration, roster, predicted_decode_s):
    out = check_registration(registration)
    if out:
        return out
    if not _schema(roster, out) or not _types(registration, roster, out):
        return out
    try:
        _static_checks(registration, roster, predicted_decode_s, out)
        _event_checks(registration, roster, out)
    except (AssertionError, KeyError, IndexError, TypeError, ValueError, OverflowError, ZeroDivisionError) as exc:
        _bad(out, 'INV-52', f'cross-record structure: {type(exc).__name__}: {exc}')
    return list(dict.fromkeys(out))


def check_transition(registration, before, after, predicted_decode_s):
    out = check_roster(registration, before, predicted_decode_s) + check_roster(registration, after, predicted_decode_s)
    if not isinstance(before, dict) or not isinstance(after, dict):
        _bad(out, 'INV-38', 'transition operands must be rosters')
        return out
    try:
        if after['events'][:len(before['events'])] != before['events'] or len(after['events']) != len(before['events']) + 1:
            _bad(out, 'INV-38', 'events not append-only')
        if after['placements'][:len(before['placements'])] != before['placements']:
            _bad(out, 'INV-38', 'placements not append-only')
        if after['terminal_refusals'][:len(before['terminal_refusals'])] != before['terminal_refusals']:
            _bad(out, 'INV-37', 'terminal refusals not append-only')
        if [b['block_id'] for b in after['blocks'][:len(before['blocks'])]] != [b['block_id'] for b in before['blocks']]:
            _bad(out, 'INV-10', 'blocks not append-only by id')
        if after['registered_sha256'] != before['registered_sha256']:
            _bad(out, 'INV-38', 'root digest changed')
        if after['envelopes'][:len(before['envelopes'])] and any(a != b for a, b in zip(after['envelopes'], before['envelopes']) if b['observations'] is not None):
            _bad(out, 'INV-18', 'reported envelope changed')
        if after['events'] and after['events'][-1]['envelope_index'] != next(i for i, e in enumerate(before['envelopes']) if e['kind'] == 'loaded' and e['observations'] is None):
            _bad(out, 'INV-46', 'transition skipped lowest unreported envelope', 'report_order')
    except (KeyError, IndexError, StopIteration, TypeError) as exc:
        _bad(out, 'INV-38', f'transition structure: {exc}')
    return list(dict.fromkeys(out))


def _unreported(r):
    return [e['index'] for e in r['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None]


def _window_keys_ok(keys):
    return isinstance(keys, (set, frozenset)) and all(type(k) is tuple and len(k) == 2 and isinstance(k[0], str) and _int(k[1]) for k in keys)


def check_executed(registration, roster, predicted_decode_s, captured_window_keys):
    """Return the 31 X-5 executed-status shape; invalid rosters return violations.

    The public interface's return type is a dict, so input violations are exposed
    under ``violations`` while valid inputs use exactly the three ruled keys.
    """
    violations = check_roster(registration, roster, predicted_decode_s)
    if not violations and _unreported(roster):
        _bad(violations, 'INV-46', 'executed roster has unreported loaded envelope', 'unreported_envelope')
    if not _window_keys_ok(captured_window_keys):
        _bad(violations, 'INV-52', 'captured window keys must be a set of (block_id, attempt) pairs')
    if violations:
        return {'violations': violations}
    spread, lever = _derived(registration, roster, captured_window_keys)
    gap = _gap(registration)
    # drift_exceeded is false for a null lever and whenever max_gap is undefined (02d §4.2).
    return {'spread_exceeded': spread, 'executed_drift_lever_slots': lever,
            'drift_exceeded': {level: gap is not None and value is not None and value > gap for level, value in lever.items()}}


def check_registration(registration):
    try:
        return _check_registration_impl(registration)
    except (AssertionError, KeyError, IndexError, TypeError, ValueError, OverflowError, ZeroDivisionError) as exc:
        return [Violation('INV-51', 'inv_51', f'registration structure: {type(exc).__name__}: {exc}')]
