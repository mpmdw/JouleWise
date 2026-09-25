"""Seeded mutation fuzz of the scored packer's entry points against the checker.

Final texts v4, text 7 (ex-10 B8 operators; ex-21 A4/A7).  Bases are the
intermediate rosters of ``generate_case`` runs that still have a pending loaded
envelope; each of ten operators mutates each base once, and each mutant goes
to ``requeue_overrun`` both resealed and unresealed with an all-keep report.
Final (fully reported) rosters are mutated the same way and go instead to
``executed_status`` with a seeded 75 % sample of their placement keys.

The corpus is built once; each property (a)-(f) is its own test so a red run
names the properties that fail.
"""
from collections import Counter
from copy import deepcopy
import random
import unittest

from joulewise.scored_packer import PackingRefusal, executed_status, requeue_overrun
from tests.scored_case_generator import generate_case, pending
from tests.scored_roster_checker import check_roster, digest

# Short runs that still split parents, so operators (5) and (6) have singles;
# 291013:10 and 291014:3 hold cells whose last live parent op (1) can void.
CASES = ((291013, 3), (291013, 10), (291014, 3), (291014, 8))
CENSUS = {'inv_11', 'inv_12', 'inv_38', 'inv_39', 'inv_02'}
REPLAY_CODES = {'inv_38', 'inv_39'}


def _detail(exc):
    return str(exc).partition(": ")[2]


def reseal(r):
    d = digest(r); r["sha256"] = d; (r["events"][-1].__setitem__("sha256", d) if r["events"] else r.__setitem__("registered_sha256", d)); return r


def _live_placements(r):
    return [(pl, i) for i, pl in enumerate(r['placements'])
            if pl['block_id'] in r['envelopes'][pl['envelope_index']]['blocks']]


def op1_live_to_voided(r, rng):
    full = [e for e in r['envelopes'] if e['blocks']]
    if not full:
        return None
    e = rng.choice(full)
    bid = rng.choice(e['blocks'])
    e['blocks'].remove(bid)
    e['voided_block_ids'].append(bid)
    return r


def op2_duplicate_live_placement(r, rng):
    if not _live_placements(r):
        return None
    pl, _ = rng.choice(_live_placements(r))
    n = len(r['envelopes'])
    model = r['envelopes'][pl['envelope_index']]['model']
    r['envelopes'].append(dict(index=n, model=model, kind='loaded', blocks=[pl['block_id']],
                               voided_block_ids=[], observations=None))
    r['placements'].append(dict(pl, envelope_index=n))
    return r


def op3_drop_terminal(r, rng):
    if not r['terminal_refusals']:
        return None
    r['terminal_refusals'].pop(rng.randrange(len(r['terminal_refusals'])))
    return r


def op4_add_terminal(r, rng):
    blocks = {b['block_id']: b for b in r['blocks']}
    if not _live_placements(r):
        return None
    pl, _ = rng.choice(_live_placements(r))
    b = blocks[pl['block_id']]
    r['terminal_refusals'].append(dict(type='unattributed_overrun', block_id=b['block_id'],
                                       attempt=pl['attempt'], parent_block_id=b['parent_block_id'],
                                       item_id=rng.choice(b['items']), model=b['model'], level=b['level']))
    return r


def op5_remove_single(r, rng):
    singles = [j for j, b in enumerate(r['blocks']) if b['parent_block_id'] is not None]
    if not singles:
        return None
    r['blocks'].pop(rng.choice(singles))
    return r


def op6_flip_superseded(r, rng):
    split = [b for b in r['blocks'] if b['superseded']]
    b = rng.choice(split if split and rng.random() < 0.5 else r['blocks'])
    b['superseded'] = not b['superseded']
    return r


def op7_move_placement(r, rng):
    pl = rng.choice(r['placements'])
    others = [e['index'] for e in r['envelopes'] if e['index'] != pl['envelope_index']]
    pl['envelope_index'] = rng.choice(others)
    return r


def op8_flip_late(r, rng):
    b = rng.choice(r['blocks'])
    b['late'] = not b['late']
    return r


def op9_alter_event_digest(r, rng):
    if len(r['events']) < 2:
        return None
    ev = r['events'][rng.randrange(len(r['events']) - 1)]
    ev['sha256'] = ev['sha256'][:-1] + ('0' if ev['sha256'][-1] != '0' else '1')
    return r


def op10_increment_attempt(r, rng):
    rng.choice(r['placements'])['attempt'] += 1
    return r


OPERATORS = (op1_live_to_voided, op2_duplicate_live_placement, op3_drop_terminal, op4_add_terminal,
             op5_remove_single, op6_flip_superseded, op7_move_placement, op8_flip_late,
             op9_alter_event_digest, op10_increment_attempt)


def _keys(r, tag):
    rng = random.Random(tag)
    return {(pl['block_id'], pl['attempt']) for pl in r['placements'] if rng.random() < .75}


def _call(fn):
    """('ok', None, None), ('refused', code, detail) or ('crash', type name, text)."""
    try:
        fn()
    except PackingRefusal as exc:
        return ('refused', exc.code, _detail(exc))
    except Exception as exc:  # property (a) forbids every other exception
        return ('crash', type(exc).__name__, str(exc)[:120])
    return ('ok', None, None)


def _submit(case, base_ix, m):
    """Submit mutant m of the roster at case.rosters[base_ix]."""
    if base_ix < len(case.reports):
        ix = case.reports[base_ix][0]
        keep = [dict(block_id=bid, status='completed', elapsed_s=0.01) for bid in m['envelopes'][ix]['blocks']]
        return _call(lambda: requeue_overrun(case.reg, m, ix, keep))
    keys = _keys(m, f'fuzz-keys:{case.seed}:{case.i}')
    return _call(lambda: executed_status(case.reg, m, case.p, keys))


def build_corpus():
    legal, rows = [], []
    for seed, i in CASES:
        try:
            case = generate_case(seed, i)
        except PackingRefusal as exc:  # a legal report refused: property (f)
            legal.append(dict(seed=seed, i=i, entry='requeue_overrun', outcome=('refused', exc.code, _detail(exc))))
            continue
        except Exception as exc:  # property (a) on the legal corpus
            legal.append(dict(seed=seed, i=i, entry='requeue_overrun', outcome=('crash', type(exc).__name__, str(exc)[:120])))
            continue
        final = case.rosters[-1]
        legal.append(dict(seed=seed, i=i, entry='executed_status',
                          outcome=_call(lambda: executed_status(case.reg, final, case.p,
                                                                _keys(final, f'legal-keys:{seed}:{i}')))))
        for k, base in enumerate(case.rosters):
            is_final = k == len(case.rosters) - 1
            if not is_final:
                assert pending(base)['index'] == case.reports[k][0]
            for op in OPERATORS:
                m = op(deepcopy(base), random.Random(f'fuzz:{seed}:{i}:{k}:{op.__name__}'))
                if m is None:
                    continue
                for sealed in (True, False):
                    sub = reseal(deepcopy(m)) if sealed else deepcopy(m)
                    try:
                        found = check_roster(case.g, sub, case.p)
                    except Exception as exc:  # the checker must never raise
                        found = [('checker-crash', type(exc).__name__)]
                    rows.append(dict(op=op.__name__, seed=seed, i=i, k=k, final=is_final, sealed=sealed,
                                     checker=sorted({getattr(v, 'inv_id', str(v)) for v in found}),
                                     outcome=_submit(case, k, sub)))
    return legal, rows


class ScoredPackerFuzzTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.legal, cls.rows = build_corpus()
        census = Counter(r['outcome'][1] for r in cls.rows if r['outcome'][0] == 'refused')
        print(f'FUZZ cases={len(CASES)} submissions={len(cls.rows)} census={dict(sorted(census.items()))}')

    def _fail_rows(self, bad, label):
        if bad:
            self.fail(f'{label}: {len(bad)} rows; first: ' + '; '.join(
                f"({r['op']}, {r['seed']}:{r['i']}, k={r['k']}, sealed={r['sealed']}, final={r['final']}, "
                f"outcome={r['outcome']}, checker={r['checker'][:6]})" for r in bad[:6]))

    def test_a_entry_points_return_or_raise_packing_refusal(self):
        self._fail_rows([r for r in self.rows if r['outcome'][0] == 'crash'], 'non-PackingRefusal exception')
        self.assertEqual([], [r for r in self.rows if any(v == 'checker-crash' for v in r['checker'])])

    def test_b_checker_violation_implies_refusal(self):
        self._fail_rows([r for r in self.rows if r['checker'] and r['outcome'][0] != 'refused'],
                        'checker reports violations but the entry point did not refuse')

    def test_c_every_operator_has_a_resealed_non_digest_refusal(self):
        missing = [op.__name__ for op in OPERATORS
                   if not any(r['op'] == op.__name__ and r['sealed'] and r['outcome'][0] == 'refused'
                              and r['outcome'][1] != 'inv_02' for r in self.rows)]
        self.assertEqual([], missing)

    def test_d_refusal_census(self):
        census = {r['outcome'][1] for r in self.rows if r['outcome'][0] == 'refused'}
        self.assertEqual(set(), CENSUS - census, sorted(census))

    def test_e_checker_clean_refusals_are_replay_codes_only(self):
        bad = [r for r in self.rows if not r['checker'] and r['outcome'][0] == 'refused'
               and r['outcome'][1] not in REPLAY_CODES]
        self.assertEqual([], sorted({(r['op'], r['seed'], r['i'], r['outcome'][1]) for r in bad}))

    def test_f_internal_never_fires_and_legal_corpus_is_accepted(self):
        self.assertEqual([], [x for x in self.legal if x['outcome'][0] != 'ok'])
        internal = [r for r in self.rows if r['outcome'][0] == 'refused' and r['outcome'][2].startswith('internal:')]
        self._fail_rows(internal, 'internal: refusal')


if __name__ == '__main__':
    unittest.main()
