#!/usr/bin/env python3
"""Synthetic R22-2 qualification. No data paths, repo runtime, network or models.

Reuses the B3 Sol1 numerical helpers. Single process, single numerical thread;
all score-generating draws are synthetic. Run --check for bounded unit checks,
--profile for a small measured pilot, or without flags for the declared grid.
Output names are r22-*-sol1.*, leaving the earlier B3 evidence immutable.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
from pathlib import Path
import sys
import time
import unittest

import numpy as np

from simulate_sol1 import (NORMAL_TAIL, exact_completion, mean_ci,
                           probability_ci, ranks, write_csv)

SEED = 202611082201
TRIALS = 100_000
BATCH = 2_000
DESIGNS = ('oracle8', 'fixed8_no_replace', 'old_count6', 'r22')
RULES = ('maximum', 'rank05', 'literal38')
MECHANISMS = ('gaussian_independent', 'hot_independent', 'hot_correlated')
# R22-5 priors divided by hypothetical residual CVs, never measured here:
# CV=1%: .13/.21 s_r; CV=.26%: .5/.807692... s_r.
TAUS = (0., .13, .21, .25, .5, .0021/.0026)
MARGINS = (.1, .2, .3, .4, .5, .75, 1.)
HERE = Path(__file__).resolve().parent


def selectors(barred, member_ok):
    """No score argument. Reserves arm for structural loss only, never low m.

    fixed8 and old_count6 count all unbarred windows in their fixed/prefix
    attempted roster. R22 needs exactly eight admitted windows within ten.
    Returns selected-window masks, counts, qualification, attempted windows.
    """
    b = len(barred)
    ix = np.arange(10)[None, :]
    admitted = ~barred
    fixed = admitted & (ix < 8)
    r22 = admitted & (admitted.cumsum(axis=1) <= 8)
    cumulative = np.multiply(member_ok.sum(axis=3), fixed[:, None, :]).cumsum(axis=2)
    stop = np.full(b, 8, dtype=np.int64)
    for n in (7, 6):
        stop[np.all(cumulative[:, :, n-1] >= 39, axis=1)] = n
    old = fixed & (ix < stop[:, None])
    oracle = np.broadcast_to(ix < 8, (b, 10))
    masks = np.stack((oracle, fixed, old, r22), axis=1)
    counts = np.stack([np.multiply(member_ok.sum(axis=3), m[:, None, :]).sum(axis=2)
                       for m in masks.transpose(1, 0, 2)], axis=1)
    qualified = np.all(counts >= 39, axis=2)
    qualified[:, 3] &= r22.sum(axis=1) == 8
    # Once the eighth admitted window occurs, later windows are unattempted.
    eighth = (admitted.cumsum(axis=1) >= 8).argmax(axis=1)
    attempted_r22 = np.where(r22.sum(axis=1) == 8, np.add(eighth, 1), 10)
    attempted = np.stack((np.full(b, 8), np.full(b, 8), stop, attempted_r22), axis=1)
    return masks, counts, qualified, attempted


def future_risk(threshold, tau, trend, mechanism, bar_p, admitted=False):
    """Expected strict-> FPR in T1/T2/T3, positions 11/12/13 (zero-based 10:13).

    Member exclusion is independent of scores, so it cancels on conditioning.
    `admitted` additionally conditions on passing the whole-window bar gate.
    Future residuals/window states are integrated, avoiding test-draw MC noise.
    """
    result = np.zeros_like(threshold)
    hot_weight = .25
    if admitted and mechanism == 'hot_correlated':
        hot_weight = .25*(1-3*bar_p)/(1-bar_p)
    for j in (10, 11, 12):
        centered = np.subtract(threshold, trend*j)
        if mechanism == 'gaussian_independent':
            value = NORMAL_TAIL(np.divide(centered, math.sqrt(1+tau*tau))).astype(float)
        else:
            hot = NORMAL_TAIL(np.subtract(centered, tau*math.sqrt(3))).astype(float)
            cool = NORMAL_TAIL(np.add(centered, tau/math.sqrt(3))).astype(float)
            value = np.add(np.multiply(hot_weight, hot), np.multiply(1-hot_weight, cool))
        result += np.divide(value, 3)
    return result


def thresholds(scores, member_ok, masks, counts):
    b = len(scores)
    result = np.empty((b, 4, 3, 2))
    for d in range(4):
        eligible = member_ok & masks[:, d, None, :, None]
        ordered = np.sort(np.where(eligible, scores, np.inf).reshape(b, 2, 70), axis=2)
        for r, k in enumerate(ranks(counts[:, d])):
            result[:, d, r] = np.take_along_axis(
                ordered, np.maximum(np.subtract(k, 1), 0)[:, :, None], axis=2)[:, :, 0]
    return result


def exact_probabilities(bar_p, member_p):
    """Independent binomial sums: final member attrition is iid, even when hot.

    Shared structural bars affect both pairs; do not square a marginal window
    completion probability. C9/C10 are at most two *attempts*, not two successes.
    """
    def weight(n, k):
        return math.comb(n, k)*(1-bar_p)**k*bar_p**(n-k)
    fixed = math.fsum(weight(8, k)*exact_completion(member_p, k) for k in range(9))
    eight = math.fsum(weight(10, k) for k in range(8, 11))
    enough = math.fsum(weight(10, k)*exact_completion(member_p, min(k, 8))
                       for k in range(11))
    return dict(oracle8=exact_completion(member_p, 8), fixed8_no_replace=fixed,
                old_count6=fixed, r22=eight*exact_completion(member_p, 8),
                r22_count_only=enough, r22_eight_windows=eight)


def scenario_grid():
    primary = list(itertools.product(MECHANISMS, (.125, .25), (.1,), TAUS, (0., .05)))
    stress = list(itertools.product(('hot_correlated',), (.125, .25), (.2,),
                                    (0., .5, .0021/.0026), (0., .05)))
    return primary + stress


def simulate(mechanism, bar_p, member_p, tau, trend, trials, batch, seed=SEED):
    # Identical random call order across all scenarios and designs. Batches are
    # only memory chunks of synthetic studies, never measured-episode batches.
    rng = np.random.default_rng(seed)
    t = np.empty((trials, 4, 3, 2))
    m = np.empty((trials, 4, 2), dtype=np.int64)
    ok = np.empty((trials, 4), dtype=bool)
    attempted = np.empty((trials, 4), dtype=np.int64)
    admitted_n = np.empty((trials, 4), dtype=np.int64)
    hot_fraction = np.empty((trials, 4))
    for start in range(0, trials, batch):
        b = min(batch, trials-start)
        eps = rng.standard_normal((b, 2, 10, 7))
        normal = rng.standard_normal((b, 10))
        hot = rng.random((b, 10)) < .25
        bar_u = rng.random((b, 10))
        member_u = rng.random((b, 2, 10, 7))
        z = normal if mechanism == 'gaussian_independent' else np.divide(
            np.subtract(hot, .25), math.sqrt(.25*.75))
        bp = np.where(hot, 3*bar_p, bar_p/3) if mechanism == 'hot_correlated' else bar_p
        barred = bar_u < bp
        member_ok = member_u >= member_p
        masks, counts, qualified, attempts = selectors(barred, member_ok)
        scores = np.add(np.add(eps, np.multiply(tau, z[:, None, :, None])),
                        np.multiply(trend, np.arange(10)[None, None, :, None]))
        out = slice(start, start+b)
        t[out] = thresholds(scores, member_ok, masks, counts)
        m[out], ok[out], attempted[out] = counts, qualified, attempts
        admitted_n[out] = masks.sum(axis=2)
        hot_fraction[out] = np.divide(np.multiply(masks, hot[:, None, :]).sum(axis=2),
                                     np.maximum(admitted_n[out], 1))
    args = dict(tau=tau, trend=trend, mechanism=mechanism, bar_p=bar_p)
    risks = future_risk(t, **args)
    pass_risks = future_risk(t, **args, admitted=True)
    exact = exact_probabilities(bar_p, member_p)
    key = dict(mechanism=mechanism, bar_p=bar_p, member_p=member_p, tau=tau, trend=trend)
    count_rows, score_rows, fix_rows = [], [], []
    for d, name in enumerate(DESIGNS):
        selected = ok[:, d]
        n_ok = int(selected.sum())
        tolerance = 7*math.sqrt(exact[name]*(1-exact[name])/trials) + 7/trials
        assert abs(n_ok/trials-exact[name]) < tolerance, (key, name, n_ok/trials, exact[name])
        count_rows.append(dict(**key, design=name, trials=trials, qualified=n_ok,
            success=probability_ci(n_ok, trials), exact_success=exact[name],
            count_goal=probability_ci(int(np.all(m[:, d] >= 39, axis=1).sum()), trials),
            eight_windows=probability_ci(int((admitted_n[:, d] == 8).sum()), trials),
            mean_m=mean_ci(m[selected, d].mean(axis=1)),
            attempted=mean_ci(attempted[:, d]), counted=mean_ci(admitted_n[:, d]),
            hot_fraction=mean_ci(hot_fraction[selected, d])))
        common = selected & ok[:, 0]
        for r, rule in enumerate(RULES):
            # Include separate pair risks and study-level pair-mean, not 2N units.
            for pair, ix in (('spam_filter_update', 0), ('bank_transfer_2', 1), ('pair_mean', None)):
                def aggregate(a):
                    return a.mean(axis=1) if ix is None else a[:, ix]
                fpr = aggregate(risks[selected, d, r])
                reference = np.divide(np.subtract(np.add(m[selected, d], 1),
                    ranks(m[selected, d])[r]), np.add(m[selected, d], 1))
                score_rows.append(dict(**key, design=name, rule=rule, pair=pair,
                    fpr=mean_ci(fpr), future_pass_fpr=mean_ci(aggregate(pass_risks[selected, d, r])),
                    threshold=mean_ci(aggregate(t[selected, d, r])),
                    common_with_oracle=int(common.sum()),
                    delta_threshold_oracle=mean_ci(aggregate(np.subtract(t[common, d, r], t[common, 0, r]))),
                    delta_fpr_oracle=mean_ci(aggregate(np.subtract(risks[common, d, r], risks[common, 0, r]))),
                    iid_reference=mean_ci(aggregate(reference))))
                if tau == 0 and trend == 0:
                    error = np.subtract(fpr, aggregate(reference))
                    assert abs(error.mean()) < 7*error.std(ddof=1)/math.sqrt(n_ok) + 1e-5
    # Paired comparisons remove availability-composition differences.
    common = ok[:, 3] & ok[:, 0]
    baseline = risks[common, 0, :2].mean(axis=2)
    fixed_common = common & ok[:, 1]
    for margin in (0.,) + MARGINS:
        adjusted = future_risk(np.add(t[:, 3, :2], margin), **args).mean(axis=2)
        for r, rule in enumerate(RULES[:2]):
            fix_rows.append(dict(**key, margin=margin, rule=rule,
                fpr=mean_ci(adjusted[ok[:, 3], r]),
                delta_oracle=mean_ci(np.subtract(adjusted[common, r], baseline[:, r])),
                delta_fixed8=mean_ci(np.subtract(adjusted[fixed_common, r],
                                                risks[fixed_common, 1, r].mean(axis=1)))))
    return count_rows, score_rows, fix_rows


class Checks(unittest.TestCase):
    def test_no_reserve_for_low_member_counts(self):
        bars = np.zeros((1, 10), dtype=bool)
        members = np.ones((1, 2, 10, 7), dtype=bool)
        members[:, :, :8, :3] = False
        masks, counts, ok, attempted = selectors(bars, members)
        self.assertEqual(attempted[0, 3], 8)
        self.assertEqual(masks[0, 3].sum(), 8)
        np.testing.assert_array_equal(counts[0, 3], [32, 32])
        self.assertFalse(ok[0, 3])

    def test_replacement_bar_and_cap(self):
        bars = np.zeros((4, 10), dtype=bool)
        bars[1, 0] = True
        bars[2, [0, 8]] = True  # A barred C9 consumes one of the two attempts.
        bars[3, [0, 1, 8]] = True
        masks, counts, ok, attempted = selectors(bars, np.ones((4, 2, 10, 7), dtype=bool))
        np.testing.assert_array_equal(attempted[:, 3], [8, 9, 10, 10])
        np.testing.assert_array_equal(masks[:, 3].sum(axis=1), [8, 8, 8, 7])
        np.testing.assert_array_equal(ok[:, 3], [True, True, True, False])
        self.assertTrue(np.all(counts[3, 3] >= 39))  # Counts alone cannot rescue it.

    def test_scalar_enumeration_of_every_bar_tape(self):
        bars = np.array(list(itertools.product((False, True), repeat=10)))
        masks, _, ok, attempts = selectors(bars, np.ones((1024, 2, 10, 7), dtype=bool))
        for i, tape in enumerate(bars):
            expected = [j for j, bar in enumerate(tape) if not bar][:8]
            self.assertEqual(np.flatnonzero(masks[i, 3]).tolist(), expected)
            self.assertEqual(bool(ok[i, 3]), len(expected) == 8)
            self.assertEqual(attempts[i, 3], expected[-1]+1 if len(expected) == 8 else 10)

    def test_old_count_stop_and_score_ranks(self):
        members = np.ones((1, 2, 10, 7), dtype=bool)
        masks, m, _, attempts = selectors(np.zeros((1, 10), dtype=bool), members)
        np.testing.assert_array_equal(attempts[0], [8, 8, 6, 8])
        scores = np.broadcast_to(np.arange(70).reshape(1, 1, 10, 7), (1, 2, 10, 7))
        t = thresholds(scores, members, masks, m)
        np.testing.assert_array_equal(t[0, 0, :, 0], [55, 54, 37])
        np.testing.assert_array_equal(t[0, 2, :, 0], [41, 40, 37])
        self.assertFalse(37 > t[0, 0, 2, 0])

    def test_exact_probabilities_independent_enumeration(self):
        p = .25
        expected = math.fsum((1-p)**(10-sum(t))*p**sum(t)
                            for t in itertools.product((0, 1), repeat=10) if sum(t) <= 2)
        self.assertAlmostEqual(exact_probabilities(p, 0)['r22'], expected, places=13)
        self.assertAlmostEqual(exact_probabilities(0, .1)['r22'], exact_completion(.1, 8))

    def test_future_population_and_immutability(self):
        t = np.full((100_000, 2), 1.2)
        full = future_risk(t, .5, 0., 'hot_correlated', .25)
        passed = future_risk(t, .5, 0., 'hot_correlated', .25, admitted=True)
        np.testing.assert_array_equal(t, 1.2)
        self.assertTrue(np.all(full > passed))
        reference = .25*.5*math.erfc((1.2-.5*math.sqrt(3))/math.sqrt(2))
        reference += .75*.5*math.erfc((1.2+.5/math.sqrt(3))/math.sqrt(2))
        self.assertAlmostEqual(full[0, 0], reference, places=13)

    def test_no_bars_same_tape_equals_oracle(self):
        rng = np.random.default_rng(23)
        members = rng.random((50, 2, 10, 7)) > .1
        masks, m, _, _ = selectors(np.zeros((50, 10), dtype=bool), members)
        t = thresholds(rng.standard_normal((50, 2, 10, 7)), members, masks, m)
        np.testing.assert_array_equal(t[:, 0], t[:, 3])

    def test_deterministic_replay_bytes(self):
        args = ('hot_correlated', .25, .1, .5, 0., 500, 100)
        first = json.dumps(simulate(*args), sort_keys=True, allow_nan=False)
        second = json.dumps(simulate(*args), sort_keys=True, allow_nan=False)
        self.assertEqual(first.encode(), second.encode())


def fmt(ci, scale=100):
    return f'{scale*ci[0]:.3f}[{scale*ci[1]:.3f},{scale*ci[2]:.3f}]'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--profile', action='store_true')
    parser.add_argument('--trials', type=int, default=TRIALS)
    parser.add_argument('--batch', type=int, default=BATCH)
    args = parser.parse_args()
    check = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
    if not check.wasSuccessful():
        return 1
    if args.check:
        return 0
    if args.profile:
        started = time.monotonic()
        rows = simulate('hot_correlated', .25, .1, .5, 0., 10_000, args.batch)
        print(f'PILOT 10000 synthetic studies {time.monotonic()-started:.3f}s; '
              f'counts={len(rows[0])} scores={len(rows[1])} fixes={len(rows[2])}')
        return 0
    if args.trials < 10_000 or args.batch < 1:
        parser.error('use >=10000 studies and a positive batch')
    started = time.monotonic()
    counts, scores, fixes = [], [], []
    for scenario in scenario_grid():
        c, s, f = simulate(*scenario, args.trials, args.batch)
        counts.extend(c)
        scores.extend(s)
        fixes.extend(f)
        print('completed', *scenario, file=sys.stderr, flush=True)
    for name, rows in (('counts', counts), ('scores', scores), ('fixes', fixes)):
        write_csv(HERE/f'r22-{name}-sol1.csv', rows)
    metadata = dict(seed=SEED, trials_per_scenario=args.trials, batch=args.batch,
        scenarios=len(scenario_grid()), python=platform.python_version(), numpy=np.__version__,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        helper_sha256=hashlib.sha256((HERE/'simulate_sol1.py').read_bytes()).hexdigest(),
        elapsed_seconds=time.monotonic()-started, future_window_positions=[11, 12, 13],
        tau_rel_prior=.0013, tau_rel_stress=.0021, residual_cv_assumptions=[.01, .0026],
        ci='pointwise 95% MC; Wilson proportions; whole-study normal mean/paired intervals',
        design_order=list(DESIGNS), margin_grid=list(MARGINS), slots_per_pair_window=7,
        bar_hot_probability=.25, bar_hot_multiplier=3, bar_cool_multiplier=1/3,
        member_exclusion='iid, score/state/bar independent; .1 primary, .2 sensitivity',
        output_sha256={f'r22-{name}-sol1.csv': hashlib.sha256((HERE/f'r22-{name}-sol1.csv').read_bytes()).hexdigest()
                       for name in ('counts', 'scores', 'fixes')})
    (HERE/'r22-metadata-sol1.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(f'SYNTHETIC ONLY seed={SEED} studies/scenario={args.trials} scenarios={len(scenario_grid())}')
    print('Percent, pointwise 95% MC CIs; dFPR/dthreshold paired on common oracle success.')
    print('Availability: bar_p member_p design P(m>=39 both) P(qualified) E[attempted]')
    for row in counts:
        if row['mechanism'] == 'hot_correlated' and row['tau'] == 0 and row['trend'] == 0:
            print(row['bar_p'], row['member_p'], row['design'], fmt(row['count_goal']),
                  fmt(row['success']), fmt(row['attempted'], 1))
    print('Risk: mechanism bar_p member_p tau trend design maximum rank05 literal38; future ALL windows')
    for scenario in scenario_grid():
        lookup = {(r['design'], r['rule']): r for r in scores
                  if tuple(r[k] for k in ('mechanism','bar_p','member_p','tau','trend')) == scenario and r['pair'] == 'pair_mean'}
        for d in DESIGNS:
            print(*scenario, d, *(fmt(lookup[d, r]['fpr']) for r in RULES))
    print(f'Outputs: r22-{{counts,scores,fixes}}-sol1.csv r22-metadata-sol1.json; elapsed={metadata["elapsed_seconds"]:.1f}s')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
