#!/usr/bin/env python3
"""Synthetic B3 sensitivity study; no repo imports, input paths, or data readers.

Python stdlib + NumPy only. One process; bounded batches. The only files read
explicitly are this source (for its digest); outputs go alongside this script.
All ranks are one-based, all alarms strict >, and cap failures have no FPR.
Run: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B <this file>
Check without Monte Carlo: python3 -B <this file> --check
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import sys
import time
import unittest

import numpy as np


SEED = 202611080301
TRIALS = 100_000
BATCH = 2_000
PAIRS = ("spam_filter_update", "bank_transfer_2")
DESIGNS = ("count6", "count7", "fixed8", "count7_margin0.5")
RULES = ("maximum", "rank05", "literal38")
TARGETS = (.025, .05, .05)
NORMAL_TAIL = np.frompyfunc(lambda x: .5 * math.erfc(x / math.sqrt(2)), 1, 1)


def ranks(m):
    """Integer arithmetic avoids floating ceil at exact rank boundaries."""
    # Explicit ufuncs allocate outputs. On this host Python 3.14 + NumPy 2.2.6
    # overloaded arithmetic on large local arrays unexpectedly reused operands.
    rank05 = np.floor_divide(np.add(np.multiply(95, np.add(m, 1)), 99), 100)
    return (m, rank05, np.full_like(m, 38))


def iid_reference(m, k):
    denominator = np.add(m, 1)
    return np.divide(np.subtract(denominator, k), denominator)


def stop_windows(cumulative, minimum):
    """Both pairs, final counts, attempted windows; no scores enter this rule."""
    used = np.full(cumulative.shape[0], 8, dtype=np.int64)
    for n in range(7, minimum - 1, -1):
        used[np.all(cumulative[:, :, n - 1] >= 39, axis=1)] = n
    return used


def binomial_tail(n, p, minimum=39):
    return math.fsum(math.comb(n, k) * p**k * (1-p)**(n-k)
                     for k in range(max(0, minimum), n+1))


def exact_completion(p, n, slots=7, mechanism="iid"):
    if mechanism == "iid":
        return binomial_tail(slots*n, 1-p)**2
    # Shared hot state: conditional on h hot windows, pairs are independent.
    total = 0.0
    for h in range(n+1):
        b = math.fsum(
            math.comb(slots*h, a) * (1-3*p)**a * (3*p)**(slots*h-a)
            * binomial_tail(slots*(n-h), 1-p/3, 39-a)
            for a in range(slots*h+1))
        total += math.comb(n, h) * .25**h * .75**(n-h) * b*b
    return total


def probability_ci(k, n):
    """Wilson 95% Monte Carlo interval, also defined for zero failures."""
    if not n:
        return [None, None, None]
    z = 1.959963984540054
    p = k/n
    den = 1 + z*z/n
    center = (p + z*z/(2*n))/den
    radius = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/den
    return [float(p), max(0.0, center-radius), min(1.0, center+radius)]


def mean_ci(values):
    """One independent MC unit is a whole two-pair calibration study."""
    values = np.asarray(values)
    values = values[np.isfinite(values)]
    if len(values) < 2:
        return [None, None, None]
    mean = float(values.mean())
    half = 1.959963984540054 * float(values.std(ddof=1)) / math.sqrt(len(values))
    return [mean, mean-half, mean+half]


def risk(threshold, *, p, tau, trend, mechanism, eligible=True):
    """Integrate independent future T1/T2/T3 episode scores, equally weighted.

    For each T window a preassigned benign episode is sampled, then condition
    on its eligibility when eligible=True. This is the expected valid-episode
    denominator of a large assigned test roster, NOT equal weighting of
    windows regardless of yield. Gaussian tails integrate future residual and
    (iid case) future Gaussian window state without test-episode MC noise.
    """
    result = np.zeros_like(threshold)
    for j in (9, 10, 11):
        mu = trend*(j-1)
        if mechanism == "iid":
            argument = np.divide(np.subtract(threshold, mu), math.sqrt(1+tau*tau))
            result += np.divide(NORMAL_TAIL(argument).astype(float), 3)
        else:
            # H~Bernoulli(.25), Z=(H-.25)/sqrt(.25*.75); Var(Z)=1.
            hot_weight = .25*(1-3*p)/(1-p) if eligible else .25
            hot_argument = np.subtract(np.subtract(threshold, mu), tau*math.sqrt(3))
            cool_argument = np.add(np.subtract(threshold, mu), tau/math.sqrt(3))
            hot_tail = np.multiply(hot_weight, NORMAL_TAIL(hot_argument).astype(float))
            cool_tail = np.multiply(1-hot_weight, NORMAL_TAIL(cool_argument).astype(float))
            result += np.divide(np.add(hot_tail, cool_tail), 3)
    return result


class Checks(unittest.TestCase):
    def test_large_array_operands_are_preserved(self):
        for _ in range(3):
            m = np.full((100_000, 2), 42, dtype=np.int64)
            k = ranks(m)[0]
            reference = iid_reference(m, k)
            np.testing.assert_array_equal(m, 42)
            np.testing.assert_allclose(reference, 1/43)
            threshold = np.full((100_000, 2), 2.1)
            risk(threshold, p=.1, tau=.5, trend=.05, mechanism='hot')
            np.testing.assert_array_equal(threshold, 2.1)
            delta = np.subtract(threshold, np.full_like(threshold, 1.9))
            np.testing.assert_array_equal(threshold, 2.1)
            np.testing.assert_allclose(delta, .2)

    def test_rank_boundaries_and_ties(self):
        m = np.array([39, 40, 42, 56, 78])
        np.testing.assert_array_equal(ranks(m)[1], [38, 39, 41, 55, 76])
        self.assertEqual((40-38)/40, .05)
        self.assertEqual((57-38)/57, 1/3)
        # A tied test score is not an alarm. No jitter is added to break ties.
        self.assertFalse(1 > sorted([1]*39)[37])

    def test_count_predicate_and_cap(self):
        counts = np.array([[[7]*8, [7]*8], [[7]*8, [6]*8],
                           [[7]*8, [0]*8], [[7]*8, [5]*8]])
        cumulative = counts.cumsum(axis=2)
        np.testing.assert_array_equal(stop_windows(cumulative, 6), [6, 7, 8, 8])
        np.testing.assert_array_equal(stop_windows(cumulative, 7), [7, 7, 8, 8])
        np.testing.assert_array_equal(np.all(cumulative[:, :, -1] >= 39, axis=1),
                                      [True, True, False, True])

    def test_exact_iid_reference_and_tail(self):
        # Published cross-checks quote six decimals, not more precision.
        self.assertAlmostEqual(exact_completion(.1, 6), .147184, places=6)
        self.assertAlmostEqual(exact_completion(.1, 7), .984054, places=6)
        self.assertAlmostEqual(exact_completion(.1, 8), .999990, places=6)
        self.assertAlmostEqual(float(risk(np.array([0.]), p=.1, tau=.5,
                                         trend=0, mechanism="iid")[0]), .5)
        self.assertEqual(binomial_tail(0, .9, 0), 1)
        self.assertEqual(binomial_tail(0, .9, 1), 0)

    def test_exact_discrete_counterexample(self):
        # Independent exact enumeration of Sol2's hot/low-yield example:
        # 90%: 7 scores=0/pair; 10%: 3 scores=1/pair, shared state.
        success = {d: 0. for d in DESIGNS[:3]}
        joint_alarm = dict(success)
        used_mean = dict(success)
        for tape in itertools.product((0, 1), repeat=8):
            probability = .1**sum(tape) * .9**(8-sum(tape))
            for d, minimum in (("count6", 6), ("count7", 7), ("fixed8", 8)):
                n = next((n for n in range(minimum, 9)
                          if sum(7-4*h for h in tape[:n]) >= 39), 8)
                used_mean[d] += probability*n
                if sum(7-4*h for h in tape[:n]) < 39:
                    continue
                success[d] += probability
                joint_alarm[d] += probability * (.1 if not any(tape[:n]) else 0)
        self.assertAlmostEqual(success['count6'], .99956835, places=8)
        self.assertAlmostEqual(joint_alarm['count6'], .0531441, places=8)
        self.assertAlmostEqual(joint_alarm['fixed8']/success['fixed8'], .04306531, places=8)
        self.assertGreater(joint_alarm['count6']/success['count6'], .05)
        self.discrete = {d: dict(success=success[d], fpr=joint_alarm[d]/success[d],
                                 expected_windows=used_mean[d]) for d in success}

    def test_analytic_risk_against_independent_quadrature(self):
        # Stdlib Simpson integration of the Gaussian-state mixture, rather
        # than reusing the closed-form variance identity under test.
        threshold, tau = 2.1, .5
        n, lo, hi = 4000, -9., 9.
        step = (hi-lo)/n
        integrand = lambda z: (.5*math.erfc((threshold-tau*z)/math.sqrt(2))
                              * math.exp(-z*z/2)/math.sqrt(2*math.pi))
        integral = step/3 * math.fsum(
            integrand(lo+i*step)*(1 if i in (0, n) else (4 if i % 2 else 2))
            for i in range(n+1))
        actual = risk(np.array([threshold]), p=.2, tau=tau, trend=0, mechanism="iid")[0]
        self.assertAlmostEqual(actual, integral, places=10)


def simulate_scenario(p, tau, trend, mechanism, trials, batch):
    # Resetting the seed shares latent tapes across parameter sensitivities.
    # Designs within every scenario always share exactly the same C1-C8 tape.
    rng = np.random.default_rng(SEED)
    risks = np.empty((trials, 4, 3, 2))
    thresholds = np.empty_like(risks)
    sizes = np.empty((trials, 3, 2), dtype=np.int64)
    windows = np.empty((trials, 3), dtype=np.int64)
    success = np.empty(trials, dtype=bool)
    for start in range(0, trials, batch):
        b = min(batch, trials-start)
        eps = rng.standard_normal((b, 2, 8, 7))
        normal_state = rng.standard_normal((b, 8))
        hot = rng.random((b, 8)) < .25
        uniforms = rng.random((b, 2, 8, 7))
        if mechanism == "iid":
            z = normal_state
            exclusion = np.full((b, 8), p)
        else:
            z = np.divide(np.subtract(hot, .25), math.sqrt(.25*.75))
            exclusion = np.where(hot, 3*p, p/3)
        eligible = uniforms >= exclusion[:, None, :, None]
        cumulative = eligible.sum(axis=3).cumsum(axis=2)
        ok = np.all(cumulative[:, :, -1] >= 39, axis=1)
        ns = (stop_windows(cumulative, 6), stop_windows(cumulative, 7), np.full(b, 8))
        scores = np.add(np.add(eps, np.multiply(tau, z[:, None, :, None])),
                        np.multiply(trend, np.arange(8)[None, None, :, None]))
        # Prepare all three prefixes, retaining every eligible score in each.
        cutoffs = {}
        for n in (6, 7, 8):
            m = cumulative[:, :, n-1]
            ordered = np.sort(np.where(eligible[:, :, :n], scores[:, :, :n], np.inf)
                              .reshape(b, 2, 7*n), axis=2)
            cutoffs[n] = np.stack([
                np.take_along_axis(ordered, np.maximum(np.subtract(k, 1), 0)[:, :, None], axis=2)[:, :, 0]
                for k in ranks(m)], axis=1)
        out = slice(start, start+b)
        for d, n_used in enumerate(ns):
            t = np.empty((b, 3, 2))
            for n in (6, 7, 8):
                select = n_used == n
                t[select] = cutoffs[n][select]
            t[~ok] = np.nan
            thresholds[out, d] = t
            risks[out, d] = risk(t, p=p, tau=tau, trend=trend, mechanism=mechanism)
            sizes[out, d] = np.take_along_axis(cumulative, np.subtract(n_used[:, None, None], 1), axis=2)[:, :, 0]
            windows[out, d] = n_used
        t = np.add(thresholds[out, 1], .5)
        thresholds[out, 3] = t
        risks[out, 3] = risk(t, p=p, tau=tau, trend=trend, mechanism=mechanism)
        success[out] = ok
    # At success, both-count stopping and fixed8 have identical availability.
    assert np.all(sizes[success] >= 39)
    assert np.all(sizes[:, 0] <= sizes[:, 1]) and np.all(sizes[:, 1] <= sizes[:, 2])
    assert np.all(thresholds[success, 0, 0] <= thresholds[success, 2, 0])
    if tau == 0 and trend == 0:
        # Eligibility is independent of all scores in this negative control,
        # so each random-m rank has an independently known expected FPR.
        for d in range(3):
            m = sizes[success, d]
            for r, k in enumerate(ranks(m)):
                reference = iid_reference(m, k)
                error = np.subtract(risks[success, d, r], reference).mean(axis=1)
                assert abs(error.mean()) < 7*error.std(ddof=1)/math.sqrt(len(error)) + 1e-5, (
                    d, r, float(error.mean()), float(error.std(ddof=1)/math.sqrt(len(error))),
                    float(risks[success, d, r].mean()), float(reference.mean()))
    count_rows, score_rows = [], []
    for d, design in enumerate(DESIGNS):
        base = min(d, 2) if d != 3 else 1
        counts = dict(mechanism=mechanism, exclusion=p, tau=tau, trend=trend, design=design,
                      success=probability_ci(int(success.sum()), trials),
                      n6=probability_ci(int((windows[:, base] == 6).sum()), trials),
                      n7=probability_ci(int((windows[:, base] == 7).sum()), trials),
                      n8=probability_ci(int((windows[:, base] == 8).sum()), trials),
                      expected_windows=mean_ci(windows[:, base]),
                      mean_m=mean_ci(sizes[success, base].mean(axis=1)),
                      exact_completion=[exact_completion(p, n, mechanism=mechanism) for n in (6, 7, 8)])
        count_rows.append(counts)
        for r, rule in enumerate(RULES):
            for pair, ix in ((*[(p, i) for i, p in enumerate(PAIRS)], ("pair_mean", None))):
                x = risks[success, d, r]
                t = thresholds[success, d, r]
                delta = np.subtract(x, risks[success, 2, r])
                dt = np.subtract(t, thresholds[success, 2, r])
                m = sizes[success, base]
                k = ranks(m)[r]
                reference = iid_reference(m, k)
                if ix is None:
                    x, t, delta, dt, reference = (v.mean(axis=1) for v in (x, t, delta, dt, reference))
                else:
                    x, t, delta, dt, reference = (v[:, ix] for v in (x, t, delta, dt, reference))
                score_rows.append(dict(mechanism=mechanism, exclusion=p, tau=tau, trend=trend,
                    design=design, rule=rule, pair=pair, fpr=mean_ci(x),
                    delta_fpr_fixed8=mean_ci(delta), mean_threshold=mean_ci(t),
                    delta_threshold_fixed8=mean_ci(dt), iid_reference=mean_ci(reference),
                    risk_quantiles=np.quantile(x, [.1, .5, .9]).tolist(),
                    probability_risk_exceeds_target=probability_ci(int((x > TARGETS[r]).sum()), len(x))))
    # Exact count probabilities are a genuinely independent audit of the MC.
    for n, exact in zip((6, 7, 8), count_rows[0]['exact_completion']):
        observed = (windows[:, 0] <= n).mean() if n < 8 else success.mean()
        tolerance = 7*math.sqrt(exact*(1-exact)/trials) + 7/trials
        assert abs(observed-exact) < tolerance, (n, observed, exact)
    return count_rows, score_rows


def flatten(row):
    result = {}
    for key, value in row.items():
        if isinstance(value, list):
            suffixes = ('estimate', 'lo', 'hi') if key not in ('risk_quantiles', 'exact_completion') else ('q10', 'q50', 'q90') if key == 'risk_quantiles' else ('n6', 'n7', 'n8')
            result.update({key+'_'+s: v for s, v in zip(suffixes, value)})
        else:
            result[key] = value
    return result


def write_csv(path, rows):
    rows = [flatten(row) for row in rows]
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fmt(ci, scale=100):
    return f'{scale*ci[0]:.3f}[{scale*ci[1]:.3f},{scale*ci[2]:.3f}]'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--trials', type=int, default=TRIALS)
    parser.add_argument('--batch', type=int, default=BATCH)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    check = unittest.TextTestRunner(verbosity=2).run(suite)
    if not check.wasSuccessful():
        return 1
    if args.check:
        return 0
    if args.trials < 10_000 or args.batch < 1:
        parser.error('use at least 10000 independent trials and a positive batch size')
    started = time.monotonic()
    counts, scores = [], []
    for mechanism, p, tau, trend in itertools.product(('iid', 'hot'), (.05, .1, .2), (0., .25, .5), (0., .05)):
        c, s = simulate_scenario(p, tau, trend, mechanism, args.trials, args.batch)
        counts.extend(c)
        scores.extend(s)
        print(f'completed {mechanism} p={p} tau={tau} trend={trend}', file=sys.stderr, flush=True)
    dest = Path(__file__).resolve().parent
    write_csv(dest/'counts-sol1.csv', counts)
    write_csv(dest/'scores-sol1.csv', scores)
    metadata = dict(seed=SEED, trials_per_scenario=args.trials, batch=args.batch,
                    python=platform.python_version(), numpy=np.__version__,
                    source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    elapsed_seconds=time.monotonic()-started,
                    mc_interval='pointwise 95%; Wilson proportions, study-level normal mean intervals',
                    future_windows=[9, 10, 11], hot_probability=.25,
                    hot_exclusion_multiplier=3, cool_exclusion_multiplier=1/3,
                    slots_per_pair_per_window=7, two_pairs=list(PAIRS),
                    attempted_cap=8, count_target_each_pair=39,
                    fit_slot_sensitivity={str(p): {str(n): exact_completion(p, n, slots=5) for n in (6, 7, 8)} for p in (.05, .1, .2)})
    (dest/'metadata-sol1.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(f'SYNTHETIC ONLY seed={SEED} studies/scenario={args.trials} scenarios=36')
    print('FPR intervals are pointwise 95% MC intervals, percent; d=paired count6-fixed8 percentage points.')
    print('Count table: mechanism p P(N=6) P(N=7) P(N=8) E[N] both-pair-success')
    for row in counts:
        if row['design'] == 'count6' and row['tau'] == 0 and row['trend'] == 0:
            print(row['mechanism'], row['exclusion'], *(fmt(row[k], 1 if k == 'expected_windows' else 100) for k in ('n6', 'n7', 'n8', 'expected_windows', 'success')))
    print('Risk table: mech p tau trend max-C6 max-8 d-max rank05-C6 rank05-8 d-rank05 max-C7+.5 rank05-C7+.5')
    for mechanism, p, tau, trend in itertools.product(('iid', 'hot'), (.05, .1, .2), (0., .25, .5), (0., .05)):
        lookup = {(r['design'], r['rule']): r for r in scores
                  if (r['mechanism'], r['exclusion'], r['tau'], r['trend'], r['pair']) == (mechanism, p, tau, trend, 'pair_mean')}
        cells = []
        for rule in RULES[:2]:
            for design, metric in (('count6', 'fpr'), ('fixed8', 'fpr'), ('count6', 'delta_fpr_fixed8')):
                cells.append(fmt(lookup[design, rule][metric]))
        cells.extend(fmt(lookup['count7_margin0.5', r]['fpr']) for r in RULES[:2])
        print(mechanism, p, tau, trend, *cells)
    print(f'Outputs: counts-sol1.csv scores-sol1.csv metadata-sol1.json; elapsed={metadata["elapsed_seconds"]:.1f}s')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
