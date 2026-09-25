"""A291 ownership forgeries at the finalizing seal, independent of replay."""

from collections import Counter
from copy import deepcopy
import json
import os
import time
import unittest
from unittest.mock import patch

from joulewise.scored_packer import PackingRefusal, _seal
from tests.scored_case_generator import generate_case
from tests.scored_ownership_generator import composed_mutants
from tests.scored_ownership_oracle import ownership_violations
from tests.scored_roster_checker import check_roster
from tests.test_scored_packer import _split_route
from tests.test_scored_roster_checker import refresh_derived


def _terminal(block, attempt, item):
    return dict(type='unattributed_overrun', block_id=block['block_id'],
                attempt=attempt, parent_block_id=block['parent_block_id'],
                item_id=item, model=block['model'], level=block['level'])


def _named_witnesses():
    """Type-clean reconstructions of AUD-1, B1, B2 and probe-D."""
    g, p, reg, base = _split_route()
    parent = next(b for b in base['blocks'] if b['superseded'])
    voided = next(e for e in base['envelopes']
                  if parent['block_id'] in e['voided_block_ids'])
    out = {}

    b1 = deepcopy(base)
    e = b1['envelopes'][voided['index']]
    e['voided_block_ids'].remove(parent['block_id'])
    e['blocks'].append(parent['block_id'])
    out['B1'] = b1

    b2 = deepcopy(base)
    pl = [x for x in b2['placements'] if x['block_id'] == parent['block_id']][-1]
    n = len(b2['envelopes'])
    b2['envelopes'].append(dict(index=n, model=parent['model'], kind='loaded',
                                 blocks=[parent['block_id']], voided_block_ids=[],
                                 observations=None))
    b2['placements'].append(dict(pl, envelope_index=n))
    out['B2'] = b2

    aud = deepcopy(base)
    listed = {bid for e in aud['envelopes'] for bid in e['blocks']}
    block = next(b for b in aud['blocks'] if b['block_id'] in listed
                 and b['parent_block_id'] is None and len(b['items']) == 2)
    clone = deepcopy(block)
    clone['block_id'] += ':999'
    aud['blocks'].append(clone)
    pl = next(pl for pl in aud['placements'] if pl['block_id'] == block['block_id']
              and block['block_id'] in aud['envelopes'][pl['envelope_index']]['blocks'])
    n = len(aud['envelopes'])
    aud['envelopes'].append(dict(index=n, model=block['model'], kind='loaded',
                                 blocks=[clone['block_id']], voided_block_ids=[],
                                 observations=None))
    aud['placements'].append(dict(pl, block_id=clone['block_id'], envelope_index=n))
    aud['terminal_refusals'].extend(_terminal(block, pl['attempt'], x)
                                    for x in block['items'])
    out['AUD-1'] = aud

    probe = deepcopy(base)
    listed = {bid for e in probe['envelopes'] for bid in e['blocks']}
    block = next(b for b in probe['blocks'] if b['block_id'] in listed
                 and b['parent_block_id'] is None and len(b['items']) == 2
                 and any(pl['block_id'] == b['block_id']
                         and b['block_id'] in probe['envelopes'][pl['envelope_index']]['voided_block_ids']
                         for pl in probe['placements']))
    pl = next(pl for pl in probe['placements'] if pl['block_id'] == block['block_id']
              and block['block_id'] in probe['envelopes'][pl['envelope_index']]['voided_block_ids'])
    probe['terminal_refusals'].append(_terminal(block, pl['attempt'], block['items'][0]))
    out['probe-D'] = probe

    contrast = deepcopy(base)
    single = next(b for b in contrast['blocks']
                  if b['parent_block_id'] == parent['block_id']
                  and b['items'] == [parent['items'][1]])
    pl = next(pl for pl in contrast['placements'] if pl['block_id'] == single['block_id']
              and single['block_id'] in contrast['envelopes'][pl['envelope_index']]['blocks'])
    e = contrast['envelopes'][pl['envelope_index']]
    e['blocks'].remove(single['block_id'])
    e['voided_block_ids'].append(single['block_id'])
    contrast['terminal_refusals'].append(_terminal(single, pl['attempt'], single['items'][0]))
    out['legal-contrast'] = contrast
    return g, p, reg, out


class CheckerCrash(RuntimeError):
    pass


def _checker_rows(g, roster, predictions):
    try:
        return {v.inv_id for v in check_roster(g, roster, predictions)}
    except Exception as exc:
        raise CheckerCrash(f'{type(exc).__name__}: {exc}') from exc


class OwnershipForgeryTests(unittest.TestCase):
    def test_legal_corpus(self):
        count = 0
        for seed in range(291013, 291017):
            seed_count = 0
            for i in range(12):
                case = generate_case(seed, i)
                for roster in case.rosters:
                    bad = ownership_violations(case.g, roster)
                    self.assertEqual([], bad, f'{seed}:{i}, roster {seed_count}')
                    seed_count += 1
            count += seed_count
            print(f'LEGAL seed={seed} cases=12 rosters={seed_count}', flush=True)
        self.assertEqual(1868, count)
        print(f'LEGAL total_cases=48 rosters={count} violations=0', flush=True)

    def test_named_regressions(self):
        g, _, _, witnesses = _named_witnesses()
        for name in ('AUD-1', 'B1', 'B2', 'probe-D'):
            bad = ownership_violations(g, witnesses[name])
            self.assertTrue(bad, name)
            print(f'NAMED {name} oracle=REJECT first={bad[0]}', flush=True)
        self.assertEqual([], ownership_violations(g, witnesses['legal-contrast']))
        print('NAMED legal-contrast oracle=ACCEPT', flush=True)

    def test_checker_exception_is_failure(self):
        g, p, _, witnesses = _named_witnesses()
        with patch('tests.test_scored_ownership_forgery.check_roster',
                   side_effect=TypeError('injected checker crash')):
            with self.assertRaisesRegex(CheckerCrash, 'TypeError: injected checker crash'):
                _checker_rows(g, witnesses['B1'], p)

    def test_named_seal_regressions(self):
        g, _, reg, witnesses = _named_witnesses()
        outcomes = {}
        for name, roster in witnesses.items():
            refresh_derived(g, roster)
            roster['sha256'] = None
            if roster['events']:
                roster['events'][-1]['sha256'] = ''
            try:
                _seal(reg, roster, finalize=True)
            except PackingRefusal as exc:
                outcomes[name] = f'refused:{exc.code}'
            else:
                outcomes[name] = 'accepted'
        print('NAMED_SEAL ' + json.dumps(outcomes, sort_keys=True), flush=True)
        for name in ('AUD-1', 'B1', 'B2', 'probe-D'):
            self.assertTrue(outcomes[name].startswith('refused:'), (name, outcomes[name]))
        self.assertEqual('accepted', outcomes['legal-contrast'])

    def _seal_property(self, arity):
        started = time.monotonic()
        totals = Counter()
        pair_counts = Counter()
        escapes = []
        checker_crashes = []
        seal_crashes = []
        inconclusive = []
        log_path = os.environ.get('A291_ESCAPE_LOG')
        log = open(log_path, 'w', encoding='utf-8') if log_path else None
        inconclusive_path = os.environ.get('A291_INCONCLUSIVE_LOG')
        inconclusive_log = open(inconclusive_path, 'w', encoding='utf-8') if inconclusive_path else None
        try:
            for case, k, combo, m, outcome in composed_mutants(arity):
                totals[outcome.split(':', 1)[0]] += 1
                if outcome != 'ready':
                    if outcome.startswith(('operator_error:', 'refresh_error:')):
                        record = dict(operators=combo, seed=case.seed, case=case.i,
                                      roster=k, outcome=outcome)
                        if len(inconclusive) < 10:
                            inconclusive.append(record)
                        if inconclusive_log:
                            inconclusive_log.write(json.dumps(record, sort_keys=True) + '\n')
                    continue
                pair_counts[combo, 'ready'] += 1
                bad = ownership_violations(case.g, m)
                if not bad:
                    continue
                pair_counts[combo, 'oracle_rejects'] += 1
                try:
                    _checker_rows(case.g, m, case.p)
                except CheckerCrash as exc:
                    checker_crashes.append((combo, case.seed, case.i, k, str(exc)))
                    continue
                try:
                    _seal(case.reg, m, finalize=True)
                except PackingRefusal:
                    continue
                except Exception as exc:
                    seal_crashes.append((combo, case.seed, case.i, k,
                                         type(exc).__name__, str(exc)))
                    continue
                pair_counts[combo, 'escapes'] += 1
                detail = dict(operators=combo, seed=case.seed, case=case.i,
                              roster=k, counts=[dict(model=v.model, item=v.item,
                                                       live=v.live, terminal=v.terminal,
                                                       reason=v.reason) for v in bad])
                escapes.append(detail)
                if log:
                    log.write(json.dumps(detail, sort_keys=True) + '\n')
        finally:
            if log:
                log.close()
            if inconclusive_log:
                inconclusive_log.close()
        print(f'FORGER arity={arity} ready={totals["ready"]} '
              f'inapplicable={totals["inapplicable"]} '
              f'operator_errors={totals["operator_error"]} '
              f'refresh_errors={totals["refresh_error"]} '
              f'escapes={len(escapes)} checker_crashes={len(checker_crashes)} '
              f'seal_crashes={len(seal_crashes)} runtime_s={time.monotonic()-started:.3f}',
              flush=True)
        if inconclusive:
            print('INCONCLUSIVE first=' + json.dumps(inconclusive, sort_keys=True), flush=True)
        for combo in sorted({key[0] for key in pair_counts}):
            print(f'COMBO {"+".join(combo)} ready={pair_counts[combo,"ready"]} '
                  f'oracle_rejects={pair_counts[combo,"oracle_rejects"]} '
                  f'escapes={pair_counts[combo,"escapes"]}', flush=True)
        self.assertFalse(checker_crashes, f'checker crashes: {checker_crashes[:10]}')
        self.assertFalse(seal_crashes, f'seal crashes: {seal_crashes[:10]}')
        self.assertFalse(escapes, f'{len(escapes)} seal escapes; first 20: '
                         + json.dumps(escapes[:20], sort_keys=True))

    def test_pairwise_seal_property(self):
        self._seal_property(2)

    def test_sampled_triples_seal_property(self):
        self._seal_property(3)
