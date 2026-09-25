"""A291 ownership forgeries at the finalizing seal, independent of replay."""

from collections import Counter
from copy import deepcopy
import json
import os
import time
import unittest
from unittest.mock import patch

from joulewise.scored_packer import PackingRefusal, _seal, requeue_overrun
from tests.scored_case_generator import generate_case
from tests.scored_ownership_generator import composed_mutants
from tests.scored_ownership_oracle import ownership_violations
from tests.scored_roster_checker import check_roster
from tests.test_scored_packer import _split_route, reseal
from tests.test_scored_roster_checker import refresh_derived


def _terminal(block, attempt, item):
    return dict(type='unattributed_overrun', block_id=block['block_id'],
                attempt=attempt, parent_block_id=block['parent_block_id'],
                item_id=item, model=block['model'], level=block['level'])


def _named_witnesses():
    """Type-clean ownership and formation witnesses."""
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

    m = deepcopy(b1)
    singles = {b['block_id'] for b in m['blocks']
               if b['parent_block_id'] == parent['block_id']}
    for e in m['envelopes']:
        for bid in list(e['blocks']):
            if bid in singles:
                e['blocks'].remove(bid)
                e['voided_block_ids'].append(bid)
    out['B1-singles-voided'] = m

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

    reordered = deepcopy(base)
    parents = [(i, b) for i, b in enumerate(reordered['blocks'])
               if b['parent_block_id'] is None]
    left, right = next(((i, j) for i, a in parents for j, b in parents
                        if a['model'] != b['model'] and a['level'] == b['level']))
    reordered['blocks'][left], reordered['blocks'][right] = (
        reordered['blocks'][right], reordered['blocks'][left])
    out['cross-model-reorder'] = reordered
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
        g, p, _, witnesses = _named_witnesses()
        for name in ('AUD-1', 'B1', 'B2', 'probe-D', 'B1-singles-voided'):
            bad = ownership_violations(g, witnesses[name])
            self.assertTrue(bad, name)
            if name == 'B1-singles-voided':
                self.assertIn('superseded_live', [v.reason for v in bad])
            self.assertIn('INV-11', _checker_rows(g, witnesses[name], p), name)
            print(f'NAMED {name} oracle=REJECT first={bad[0]}', flush=True)
        for name in ('legal-contrast', 'cross-model-reorder'):
            self.assertEqual([], ownership_violations(g, witnesses[name]), name)
            self.assertNotIn('INV-11', _checker_rows(g, witnesses[name], p), name)
            print(f'NAMED {name} oracle=ACCEPT', flush=True)

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
        for name in ('AUD-1', 'B1', 'B2', 'probe-D', 'B1-singles-voided'):
            self.assertEqual('refused:inv_11', outcomes[name], name)
        self.assertEqual('refused:inv_10', outcomes['cross-model-reorder'])
        self.assertEqual('accepted', outcomes['legal-contrast'])

    def test_entry_path_witness_inv_23(self):
        g, p, reg, base = _split_route()
        self.assertEqual(set(), _checker_rows(g, base, p))
        roster = deepcopy(base)
        single = next(b for b in roster['blocks'] if b['parent_block_id'] is not None)
        single['predicted_s'] = 29.0
        reseal(roster)
        self.assertIn('INV-23', _checker_rows(g, roster, p))
        # Listed code: inv_23; the resealed entry raises inv_38 on event replay.
        with self.assertRaises(PackingRefusal) as caught:
            requeue_overrun(reg, roster, 0, [])
        self.assertEqual('inv_38', caught.exception.code)

    def test_entry_path_witness_inv_36(self):
        g, p, reg, base = _split_route()
        self.assertEqual(set(), _checker_rows(g, base, p))
        roster = deepcopy(base)
        advanced = next(pl for pl in roster['placements']
                        if pl['stage'] == 'whole_block' and pl['attempt'] == 1)
        advanced['attempt'] = 2
        reseal(roster)
        self.assertIn('INV-36', _checker_rows(g, roster, p))
        # Listed code: inv_36; the resealed entry raises inv_38 on event replay.
        with self.assertRaises(PackingRefusal) as caught:
            requeue_overrun(reg, roster, 0, [])
        self.assertEqual('inv_38', caught.exception.code)

    def test_entry_path_witness_inv_37(self):
        case = generate_case(291013, 0)
        roster = deepcopy(case.rosters[0])
        self.assertEqual(set(), _checker_rows(case.g, roster, case.p))
        block = roster['blocks'][0]
        roster['terminal_refusals'].append(dict(
            type='ceiling_violation', block_id=block['block_id'], attempt=0,
            parent_block_id=None, item_id=block['items'][0],
            model=block['model'], level=block['level']))
        reseal(roster)
        self.assertIn('INV-37', _checker_rows(case.g, roster, case.p))
        # Listed code: inv_37; the live/terminal ownership conflict raises inv_11.
        with self.assertRaises(PackingRefusal) as caught:
            requeue_overrun(case.reg, roster, 0, [])
        self.assertEqual('inv_11', caught.exception.code)

    def test_legal_corpus_seal(self):
        count = 0
        for seed in range(291013, 291017):
            for i in range(12):
                case = generate_case(seed, i)
                for roster in case.rosters:
                    m = deepcopy(roster)
                    refresh_derived(case.g, m)
                    m['sha256'] = None
                    if m['events']:
                        m['events'][-1]['sha256'] = ''
                    _seal(case.reg, m, finalize=True)
                    count += 1
        self.assertEqual(1868, count)
        print(f'LEGAL_SEAL rosters={count} accepted={count}', flush=True)

    def _seal_property(self, arity):
        started = time.monotonic()
        totals = Counter()
        pair_counts = Counter()
        escapes = []
        checker_crashes = []
        seal_crashes = []
        checker_disagreements = []
        refresh_seal_failures = []
        refusal_codes = Counter()
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
                    if outcome.startswith('refresh_error:'):
                        try:
                            _seal(case.reg, m, finalize=True)
                        except PackingRefusal:
                            pass
                        except Exception as exc:
                            refresh_seal_failures.append((combo, case.seed, case.i, k,
                                                          type(exc).__name__, str(exc)))
                        else:
                            refresh_seal_failures.append((combo, case.seed, case.i, k,
                                                          'accepted'))
                    continue
                pair_counts[combo, 'ready'] += 1
                bad = ownership_violations(case.g, m)
                if not bad:
                    continue
                pair_counts[combo, 'oracle_rejects'] += 1
                try:
                    rows = _checker_rows(case.g, m, case.p)
                except CheckerCrash as exc:
                    checker_crashes.append((combo, case.seed, case.i, k, str(exc)))
                    continue
                if 'INV-52' not in rows and 'INV-11' not in rows:
                    checker_disagreements.append((combo, case.seed, case.i, k,
                                                  sorted(rows)))
                try:
                    _seal(case.reg, m, finalize=True)
                except PackingRefusal as exc:
                    refusal_codes[exc.code] += 1
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
              f'seal_crashes={len(seal_crashes)} '
              f'checker_disagreements={len(checker_disagreements)} '
              f'refusal_codes={json.dumps(refusal_codes, sort_keys=True)} '
              f'runtime_s={time.monotonic()-started:.3f}',
              flush=True)
        if inconclusive:
            print('INCONCLUSIVE first=' + json.dumps(inconclusive, sort_keys=True), flush=True)
        for combo in sorted({key[0] for key in pair_counts}):
            print(f'COMBO {"+".join(combo)} ready={pair_counts[combo,"ready"]} '
                  f'oracle_rejects={pair_counts[combo,"oracle_rejects"]} '
                  f'escapes={pair_counts[combo,"escapes"]}', flush=True)
        self.assertFalse(checker_crashes, f'checker crashes: {checker_crashes[:10]}')
        self.assertFalse(seal_crashes, f'seal crashes: {seal_crashes[:10]}')
        self.assertEqual(0, totals['operator_error'], f'operator errors: {inconclusive[:10]}')
        self.assertEqual(0, totals['refresh_error'], f'refresh errors: {inconclusive[:10]}')
        self.assertFalse(refresh_seal_failures,
                         f'refresh-error mutants accepted or crashed: {refresh_seal_failures[:10]}')
        self.assertFalse(checker_disagreements,
                         f'checker disagreements: {checker_disagreements[:10]}')
        self.assertFalse(escapes, f'{len(escapes)} seal escapes; first 20: '
                         + json.dumps(escapes[:20], sort_keys=True))

    def test_pairwise_seal_property(self):
        self._seal_property(2)

    def test_triple_seal_property(self):
        self._seal_property(3)
