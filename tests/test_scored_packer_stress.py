"""Seeded, checker-verified scored roster reporting sequences."""
from collections import Counter
import random
import unittest

from joulewise.scored_registration import Registration
from joulewise.scored_packer import pack, requeue_overrun, verify_executed_roster, executed_status
from tests.scored_roster_checker import check_roster
from tests.test_scored_registration import fixture

SEEDS = (291013,)
EDGE_NAMES = {
    ('initial', 'advance'): 'E1', ('initial', 'reschedule'): 'E2',
    ('initial', 'unattributed_overrun'): 'E3', ('whole_block', 'split'): 'E4',
    ('whole_block', 'unattributed_overrun'): 'E5',
    ('single_problem', 'advance'): 'E6', ('single_problem', 'reschedule'): 'E7',
    ('single_retry', 'advance'): 'E8', ('single_retry', 'reschedule'): 'E9',
    ('single_problem', 'unattributed_overrun'): 'E10',
    ('single_retry', 'unattributed_overrun'): 'E11',
}


def _report(reg, roster, mode, rng):
    e = next(e for e in roster['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None)
    bm = {b['block_id']: b for b in roster['blocks']}
    obs = []
    phase = 0
    first_single = False
    first = not roster['events']
    for j, bid in enumerate(e['blocks']):
        b = bm[bid]
        stage = b['retry_stage']
        status, elapsed = 'completed', 0.01
        if first:
            if mode == 1:
                status, elapsed = 'not_started', None
            elif j == 0:
                status, elapsed = 'cut_off', b['predicted_s'] + 0.1
            elif mode == 7 and j == 1:
                status, elapsed = 'not_started', None
        elif stage == 'whole_block':
            status, elapsed = ('not_started', None) if mode == 2 else ('cut_off', 0.1)
        elif stage in ('single_problem', 'single_retry'):
            if mode == 3:
                status, elapsed = 'not_started', None
            elif mode == 4 and stage == 'single_retry':
                status, elapsed = 'not_started', None
            elif mode == 6 and stage == 'single_retry':
                status, elapsed = ('cut_off', reg.worst(b['model']) + 0.1) if j == 0 else ('not_started', None)
            elif mode == 7:
                status, elapsed = ('cut_off', reg.worst(b['model']) + 0.1) if not first_single else ('not_started', None)
                first_single = True
            else:
                status, elapsed = 'completed', reg.worst(b['model']) + 0.1
        # The event must be a completed prefix, one cut off, then not started.
        if phase == 2 or phase == 1:
            status, elapsed = 'not_started', None
        elif status == 'cut_off':
            phase = 1
        elif status == 'not_started':
            phase = 2
        obs.append(dict(block_id=bid, status=status, elapsed_s=elapsed))
    # A random legal completed-only report after the crafted branch.
    if not first and all(bm[x]['retry_stage'] == 'initial' for x in e['blocks']) and rng.random() < 0.25:
        obs = [dict(block_id=bid, status='completed', elapsed_s=0.01) for bid in e['blocks']]
    return e['index'], obs


def run_case(i, rng, check=True):
    size = 1 if i % 4 < 2 else 2
    n = (5 + i % 2) if size == 1 else (10 + i % 2)
    cap = (2.0 if size == 1 else 4.0) if i % 25 == 0 else (4.0 if size == 1 else 8.0)
    g, p = fixture(n=n, block_size=size, cap=cap, pred=0.5 + rng.random() * 0.2)
    reg = Registration.from_mapping(g)
    roster = pack(reg, p)
    counts = Counter()
    checked = 0
    calls = 0
    if check:
        assert not check_roster(g, roster, p), check_roster(g, roster, p)
        checked += 1
    mode = i % 8
    while any(e['kind'] == 'loaded' and e['observations'] is None for e in roster['envelopes']):
        ix, obs = _report(reg, roster, mode, rng)
        before = roster
        stages = {b['block_id']: b['retry_stage'] for b in before['blocks']}
        roster = requeue_overrun(reg, before, ix, obs)
        calls += 1
        for observation in roster['events'][-1]['observations']:
            edge = EDGE_NAMES.get((stages[observation['block_id']], observation['decision']))
            if edge:
                counts[edge] += 1
        if check:
            violations = check_roster(g, roster, p)
            assert not violations, (i, ix, violations[:5])
            checked += 1
    verify_executed_roster(reg, roster, p)
    keys = {(x['block_id'], x['attempt']) for x in roster['placements'] if rng.random() < .75}
    result = executed_status(reg, roster, p, keys)
    return counts, calls, checked


class ScoredPackerStressTests(unittest.TestCase):
    def test_seeded_300_registration_sequences(self):
        rng = random.Random(SEEDS[0])
        totals = Counter()
        calls = checked = 0
        for i in range(300):
            edge_counts, n_calls, n_checked = run_case(i, rng)
            totals.update(edge_counts)
            calls += n_calls
            checked += n_checked
        print(f'STRESS seeds={SEEDS} registrations=300 calls={calls} rosters_checked={checked} violations=0 edges={dict(sorted(totals.items()))}')
        self.assertEqual(set(totals), {f'E{i}' for i in range(1, 12)})
