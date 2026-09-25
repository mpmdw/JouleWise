"""Deterministic composed ownership forgeries for the A291 seal boundary."""

from copy import deepcopy
from itertools import product
import random

from tests.scored_case_generator import generate_case
from tests.test_scored_roster_checker import refresh_derived


CASES = ((291013, 3), (291013, 10), (291014, 3), (291014, 8))
TRIPLE_SAMPLE = 128
TRIPLE_SEED = 291013


def _live(r):
    return [(e, pl) for pl in r['placements']
            for e in r['envelopes']
            if e['index'] == pl['envelope_index'] and pl['block_id'] in e['blocks']]


def _block(r, block_id):
    return next(b for b in r['blocks'] if b['block_id'] == block_id)


def _new_envelope(r, block, placement, block_id=None):
    n = len(r['envelopes'])
    bid = block_id or block['block_id']
    r['envelopes'].append(dict(index=n, model=block['model'], kind='loaded',
                               blocks=[bid], voided_block_ids=[], observations=None))
    r['placements'].append(dict(placement, block_id=bid, envelope_index=n))


def clone_block_new_id(r, rng):
    candidates = _live(r)
    if not candidates:
        return False
    _, pl = rng.choice(candidates)
    original = _block(r, pl['block_id'])
    clone = deepcopy(original)
    used = {b['block_id'] for b in r['blocks']}
    suffix = 999
    while f"{original['block_id']}:{suffix}" in used:
        suffix += 1
    clone['block_id'] = f"{original['block_id']}:{suffix}"
    r['blocks'].append(clone)
    _new_envelope(r, clone, pl)
    return True


def list_live_new_envelope(r, rng):
    # The B2 shape lists a previously voided superseded parent in a new
    # envelope; prefer that target when a split has supplied one.
    candidates = [(e, pl) for pl in r['placements'] for e in r['envelopes']
                  if e['index'] == pl['envelope_index']
                  and pl['block_id'] in e['voided_block_ids']
                  and _block(r, pl['block_id'])['superseded']]
    if not candidates:
        candidates = _live(r)
    if not candidates:
        return False
    _, pl = rng.choice(candidates)
    _new_envelope(r, _block(r, pl['block_id']), pl)
    return True


def void_block(r, rng):
    candidates = _live(r)
    if not candidates:
        return False
    e, pl = rng.choice(candidates)
    e['blocks'].remove(pl['block_id'])
    e['voided_block_ids'].append(pl['block_id'])
    return True


def terminalise_block(r, rng):
    candidates = _live(r)
    if not candidates:
        return False
    _, pl = rng.choice(candidates)
    b = _block(r, pl['block_id'])
    for item in b['items']:
        r['terminal_refusals'].append(dict(
            type='unattributed_overrun', block_id=b['block_id'],
            attempt=pl['attempt'], parent_block_id=b['parent_block_id'],
            item_id=item, model=b['model'], level=b['level']))
    return True


def retarget_terminal(r, rng):
    choices = [(t, b) for t in r['terminal_refusals'] for b in r['blocks']
               if b['model'] == t['model'] and b['block_id'] != t['block_id']]
    if not choices:
        return False
    entry, block = rng.choice(choices)
    entry['block_id'] = block['block_id']
    return True


def revive_voided(r, rng):
    choices = [(e, bid) for e in r['envelopes'] for bid in e['voided_block_ids']]
    if not choices:
        return False
    superseded = [(e, bid) for e, bid in choices if _block(r, bid)['superseded']]
    if superseded:
        choices = superseded
    e, bid = rng.choice(choices)
    e['voided_block_ids'].remove(bid)
    e['blocks'].append(bid)
    return True


def flip_superseded(r, rng):
    live_ids = {pl['block_id'] for _, pl in _live(r)}
    choices = [b for b in r['blocks'] if b['block_id'] in live_ids]
    if not choices:
        return False
    b = rng.choice(choices)
    b['superseded'] = not b['superseded']
    return True


def drop_single(r, rng):
    choices = [b for b in r['blocks'] if b['parent_block_id'] is not None]
    if not choices:
        return False
    r['blocks'].remove(rng.choice(choices))
    return True


OPERATORS = (clone_block_new_id, list_live_new_envelope, void_block,
             terminalise_block, retarget_terminal, revive_voided,
             flip_superseded, drop_single)


def _combinations(arity):
    if arity == 2:
        return list(product(OPERATORS, repeat=2))
    if arity == 3:
        rng = random.Random(TRIPLE_SEED)
        all_combos = list(product(OPERATORS, repeat=3))
        return rng.sample(all_combos, TRIPLE_SAMPLE)
    raise ValueError(arity)


def composed_mutants(arity):
    """Yield every attempted composition, including inapplicable and errors.

    A refresh exception is an explicit outcome, never a silent skip.
    """
    combos = _combinations(arity)
    for seed, i in CASES:
        case = generate_case(seed, i)
        for k, base in enumerate(case.rosters):
            for combo in combos:
                names = tuple(op.__name__ for op in combo)
                rng = random.Random(f'A291-own:{seed}:{i}:{k}:{names}')
                m = deepcopy(base)
                outcome = 'ready'
                for op in combo:
                    try:
                        if not op(m, rng):
                            outcome = f'inapplicable:{op.__name__}'
                            break
                    except Exception as exc:
                        outcome = f'operator_error:{op.__name__}:{type(exc).__name__}:{exc}'
                        break
                if outcome == 'ready':
                    try:
                        refresh_derived(case.g, m)
                    except Exception as exc:
                        outcome = f'refresh_error:{type(exc).__name__}:{exc}'
                    else:
                        m['sha256'] = None
                        if m['events']:
                            m['events'][-1]['sha256'] = ''
                yield case, k, names, m, outcome
