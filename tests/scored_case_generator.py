"""Seed-driven scored-night cases for the A291 stress and fuzz modules.

Every choice in a case (registration shape, predictions, and each observation
of each report) is drawn from one ``random.Random`` keyed by ``(seed, i)``, so
two seeds give different histories at the same case index.  Only the packer's
public entries are called.  Observations are legal by construction: completed
prefix, at most one cut off, then not started; positive elapsed values whose
sum fits the interior.
"""
from collections import Counter, namedtuple
import random

from joulewise.scored_packer import pack, requeue_overrun
from joulewise.scored_registration import Registration
from tests.test_scored_registration import fixture

EDGE_NAMES = {
    ('initial', 'advance'): 'E1', ('initial', 'reschedule'): 'E2',
    ('initial', 'unattributed_overrun'): 'E3', ('whole_block', 'split'): 'E4',
    ('whole_block', 'unattributed_overrun'): 'E5',
    ('single_problem', 'advance'): 'E6', ('single_problem', 'reschedule'): 'E7',
    ('single_retry', 'advance'): 'E8', ('single_retry', 'reschedule'): 'E9',
    ('single_problem', 'unattributed_overrun'): 'E10',
    ('single_retry', 'unattributed_overrun'): 'E11',
}
EDGES = tuple(f'E{k}' for k in range(1, 12))
MAX_CALLS = 400

# rosters: pack output first, then the output of every requeue_overrun call.
# reports: the (envelope_index, observations) passed to each call, in order.
Case = namedtuple('Case', 'seed i g p reg rosters reports counts signature')


def pending(roster):
    """Lowest-index loaded envelope still unreported, or None."""
    return next((e for e in roster['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None), None)


def _shape(rng):
    width = rng.choice((1, 1, 2, 2, 3))
    n = 5 * width + rng.randrange(0, 3)
    pred = round(rng.uniform(0.35, 0.95), 3)
    cap = rng.choice([c for c in (1.5, 2.0, 3.0, 4.0, 6.0, 8.0) if c >= max(1.0, width * pred)])
    mode = 'pilot' if rng.random() < 0.2 else 'registered'
    return fixture(n=n, block_size=width, cap=cap, pred=pred, mode=mode)


def _observe(g, reg, roster, rng, trouble):
    """One legal report for the lowest pending envelope."""
    e = pending(roster)
    blocks = {b['block_id']: b for b in roster['blocks']}
    room = g['interior_s']
    phase = 'completed'
    out = []
    for bid in e['blocks']:
        b = blocks[bid]
        worst = reg.worst(b['model'])
        bound = b['predicted_s'] if b['retry_stage'] in ('initial', 'whole_block') else worst
        status, elapsed = 'completed', round(rng.uniform(0.005, 0.05), 4)
        single = b['parent_block_id'] is not None
        if b['retry_stage'] == 'whole_block' and rng.random() < 0.8:
            # Whole-block retries are mostly cut off so singles are common.
            status, elapsed = ('cut_off', round(bound * rng.uniform(0.1, 1.2), 4)) if rng.random() < 0.8 else ('not_started', None)
        elif phase == 'completed' and rng.random() < (max(trouble, 0.6) if single else trouble):
            # Singles lean to culprits so every single-stage edge is reached.
            pick = rng.random()
            late, cut_late, cut_early = (0.35, 0.55, 0.70) if single else (0.20, 0.50, 0.70)
            if pick < late:
                status, elapsed = 'completed', bound + round(rng.uniform(0.01, 0.3), 3)
            elif pick < cut_late:
                status, elapsed = 'cut_off', bound + round(rng.uniform(0.01, 0.3), 3)
            elif pick < cut_early:
                status, elapsed = 'cut_off', round(bound * rng.uniform(0.1, 1.0), 4)
            else:
                status, elapsed = 'not_started', None
        if phase != 'completed':
            status, elapsed = 'not_started', None
        if elapsed is not None and not 0 < elapsed <= room:
            status, elapsed = 'not_started', None
        if status == 'cut_off':
            phase = 'cut_off'
        elif status == 'not_started':
            phase = 'not_started'
        if elapsed is not None:
            room -= elapsed
        out.append(dict(block_id=bid, status=status, elapsed_s=elapsed))
    return e['index'], out


def signature(case):
    """ex-10 B8: (edge-count tuple, calls, final envelope count, event count,
    single count, terminal count)."""
    final = case.rosters[-1]
    return (tuple(case.counts[x] for x in EDGES), len(case.reports), len(final['envelopes']),
            len(final['events']), sum(b['parent_block_id'] is not None for b in final['blocks']),
            len(final['terminal_refusals']))


def generate_case(seed, i):
    rng = random.Random(f'A291:{seed}:{i}')
    g, p = _shape(rng)
    reg = Registration.from_mapping(g)
    roster = pack(reg, p)
    rosters, reports, counts = [roster], [], Counter()
    trouble = rng.uniform(0.1, 0.6)
    while pending(roster) is not None:
        if len(reports) >= MAX_CALLS:
            raise AssertionError(f'case {seed}:{i} exceeded {MAX_CALLS} reports')
        ix, obs = _observe(g, reg, roster, rng, trouble)
        stages = {b['block_id']: b['retry_stage'] for b in roster['blocks']}
        roster = requeue_overrun(reg, roster, ix, obs)
        for o in roster['events'][-1]['observations']:
            edge = EDGE_NAMES.get((stages[o['block_id']], o['decision']))
            if edge:
                counts[edge] += 1
        rosters.append(roster)
        reports.append((ix, obs))
    case = Case(seed, i, g, p, reg, rosters, reports, counts, None)
    return case._replace(signature=signature(case))
