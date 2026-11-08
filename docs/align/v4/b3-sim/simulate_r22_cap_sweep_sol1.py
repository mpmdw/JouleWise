#!/usr/bin/env python3
"""Synthetic-only R22 C10/C11/C12 sweep; no data/runtime/model/network access.

The original R22 simulator and helpers are unchanged. Preserve its entire C10
random stream, seed, chunk size and arithmetic; append independent C11/C12
draws. Main calendar: common T positions 13--15, after all potential reserves.
Also emit the old 11--13 horizon as a compatibility diagnostic (not a feasible
sequential calendar for C11/C12). All intervals use whole two-pair studies.
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

import simulate_r22_sol1 as original
from simulate_sol1 import exact_completion, flatten, mean_ci, probability_ci, ranks

HERE = Path(__file__).resolve().parent
SEED, TRIALS, BATCH = original.SEED, original.TRIALS, original.BATCH
CAPS = (10, 11, 12)
DESIGNS = ('oracle8', 'C10', 'C11', 'C12')
TAUS = (0., .5, .0021/.0026)  # .8077 is the original rounded grid label.
HORIZONS = {'after_C12': (13, 14, 15), 'legacy_C10': (11, 12, 13)}
KEYS = ('mechanism', 'bar_p', 'member_p', 'tau', 'trend')
PREFIX = 'r22-cap-sweep'


def scenario_grid():
    return list(itertools.product(original.MECHANISMS, (.125, .25), (.1, .2),
                                  TAUS, (0., .05)))


def draws(rng, n, windows):
    # EXACT original call order and shapes for windows=10. Do not interleave
    # suffix draws into this generator: that would change later C10 chunks.
    return (rng.standard_normal((n, 2, windows, 7)),
            rng.standard_normal((n, windows)), rng.random((n, windows)) < .25,
            rng.random((n, windows)), rng.random((n, 2, windows, 7)))


def tape(rng, suffix_rng, n):
    first, suffix = draws(rng, n, 10), draws(suffix_rng, n, 2)
    return tuple(np.concatenate((a, b), axis=2 if a.ndim == 4 else 1)
                 for a, b in zip(first, suffix))


def selectors(barred, member_ok):
    """First eight unbarred windows; neither scores nor m can arm a reserve."""
    n, windows = barred.shape
    ix = np.arange(windows)[None, :]
    admitted = ~barred
    prefix = admitted.cumsum(axis=1)
    masks = [np.broadcast_to(ix < 8, (n, windows))]
    attempts = [np.full(n, 8, dtype=np.int64)]
    for cap in CAPS:
        chosen = admitted & (prefix <= 8) & (ix < cap)
        masks.append(chosen)
        complete = chosen.sum(axis=1) == 8
        eighth = (prefix[:, :cap] >= 8).argmax(axis=1)
        attempts.append(np.where(complete, np.add(eighth, 1), cap))
    masks = np.stack(masks, axis=1)
    counts = np.stack([np.multiply(member_ok.sum(axis=3), m[:, None, :]).sum(axis=2)
                       for m in masks.transpose(1, 0, 2)], axis=1)
    qualified = np.all(counts >= 39, axis=2) & (masks.sum(axis=2) == 8)
    return masks, counts, qualified, np.stack(attempts, axis=1)


def thresholds(scores, member_ok, masks, counts):
    """Same rank/sort arithmetic as original; only the roster width changes."""
    n, _, windows, _ = scores.shape
    result = np.empty((n, 4, 3, 2))
    for d in range(4):
        eligible = member_ok & masks[:, d, None, :, None]
        ordered = np.sort(np.where(eligible, scores, np.inf).reshape(n, 2, windows*7), axis=2)
        for r, k in enumerate(ranks(counts[:, d])):
            result[:, d, r] = np.take_along_axis(
                ordered, np.maximum(np.subtract(k, 1), 0)[:, :, None], axis=2)[:, :, 0]
    return result


def future_risk(threshold, tau, trend, mechanism, bar_p, admitted=False,
                positions=HORIZONS['after_C12']):
    # Reuse original integration, including summation order. Moving every T
    # position by d is exactly shifting its threshold by -b*d in this model.
    if positions == HORIZONS['legacy_C10'] or trend == 0:
        adjusted = threshold
    else:
        assert positions == HORIZONS['after_C12']
        adjusted = np.subtract(threshold, 2*trend)
    return original.future_risk(adjusted, tau, trend, mechanism, bar_p, admitted)


def exact_counts(q, e, cap):
    structural = math.fsum(math.comb(cap, k)*(1-q)**k*q**(cap-k)
                           for k in range(8, cap+1))
    reserves = math.fsum(math.fsum(math.comb(8+r-1, k)*(1-q)**k*q**(8+r-1-k)
                                  for k in range(8)) for r in range(1, cap-7))
    return structural*exact_completion(e, 8), reserves


def population_delta(a, b):
    # Conservative pointwise asymptotic Cauchy SE bound for dependent means
    # conditional on different qualification populations. Not a paired CI.
    half = a[2]-a[0] + b[2]-b[0]
    delta = a[0]-b[0]
    return [delta, delta-half, delta+half]


def simulate(mechanism, bar_p, member_p, tau, trend, trials=TRIALS, batch=BATCH, seed=SEED):
    rng = np.random.default_rng(seed)
    suffix_rng = np.random.default_rng(np.random.SeedSequence([seed, 11, 12]))
    t = np.empty((trials, 4, 3, 2))
    m = np.empty((trials, 4, 2), dtype=np.int64)
    ok = np.empty((trials, 4), dtype=bool)
    attempted = np.empty((trials, 4), dtype=np.int64)
    for start in range(0, trials, batch):
        n = min(batch, trials-start)
        eps, normal, hot, bar_u, member_u = tape(rng, suffix_rng, n)
        z = normal if mechanism == 'gaussian_independent' else np.divide(
            np.subtract(hot, .25), math.sqrt(.25*.75))
        bp = np.where(hot, 3*bar_p, bar_p/3) if mechanism == 'hot_correlated' else bar_p
        members = member_u >= member_p
        masks, counts, qualified, attempts = selectors(bar_u < bp, members)
        scores = np.add(np.add(eps, np.multiply(tau, z[:, None, :, None])),
                        np.multiply(trend, np.arange(12)[None, None, :, None]))
        out = slice(start, start+n)
        t[out] = thresholds(scores, members, masks, counts)
        m[out], ok[out], attempted[out] = counts, qualified, attempts
    key = dict(zip(KEYS, (mechanism, bar_p, member_p, tau, trend)))
    counts, rows = [], []
    for d, design in enumerate(DESIGNS):
        exact, reserves = (exact_completion(member_p, 8), 0.) if d == 0 else exact_counts(bar_p, member_p, CAPS[d-1])
        n_ok = int(ok[:, d].sum())
        tolerance = 7*math.sqrt(exact*(1-exact)/trials)+7/trials
        assert abs(n_ok/trials-exact) < tolerance, (key, design, n_ok/trials, exact)
        counts.append(dict(**key, design=design, trials=trials, qualified=n_ok,
            success=probability_ci(n_ok, trials), exact_success=exact,
            mean_m=mean_ci(m[ok[:, d], d].mean(axis=1)),
            attempted=mean_ci(attempted[:, d]),
            reserves_attempted=mean_ci(np.subtract(attempted[:, d], 8)),
            exact_reserves_attempted=reserves))
    risk_args = dict(tau=tau, trend=trend, mechanism=mechanism, bar_p=bar_p)
    for horizon, positions in HORIZONS.items():
        risk = future_risk(t, **risk_args, positions=positions)
        passed = future_risk(t, **risk_args, admitted=True, positions=positions)
        for d, design in enumerate(DESIGNS):
            selected = ok[:, d]
            common = selected & ok[:, 0]
            cap_common = selected & ok[:, 1]
            for r, rule in enumerate(original.RULES):
                for pair, ix in (('spam_filter_update', 0), ('bank_transfer_2', 1), ('pair_mean', None)):
                    def aggregate(a):
                        return a.mean(axis=1) if ix is None else a[:, ix]
                    fpr = mean_ci(aggregate(risk[selected, d, r]))
                    pass_fpr = mean_ci(aggregate(passed[selected, d, r]))
                    oracle_pass = mean_ci(aggregate(passed[ok[:, 0], 0, r]))
                    reference = np.divide(np.subtract(np.add(m[selected, d], 1),
                        ranks(m[selected, d])[r]), np.add(m[selected, d], 1))
                    rows.append(dict(**key, horizon=horizon, design=design, rule=rule, pair=pair,
                        fpr=fpr, future_pass_fpr=pass_fpr,
                        threshold=mean_ci(aggregate(t[selected, d, r])),
                        common_with_oracle=int(common.sum()),
                        delta_threshold_oracle=mean_ci(aggregate(np.subtract(t[common, d, r], t[common, 0, r]))),
                        delta_fpr_oracle=mean_ci(aggregate(np.subtract(risk[common, d, r], risk[common, 0, r]))),
                        delta_future_pass_oracle=mean_ci(aggregate(np.subtract(passed[common, d, r], passed[common, 0, r]))),
                        population_delta_future_pass_oracle=population_delta(pass_fpr, oracle_pass),
                        common_with_C10=int(cap_common.sum()),
                        delta_threshold_C10=mean_ci(aggregate(np.subtract(t[cap_common, d, r], t[cap_common, 1, r]))),
                        delta_future_pass_C10=mean_ci(aggregate(np.subtract(passed[cap_common, d, r], passed[cap_common, 1, r]))),
                        iid_reference=mean_ci(aggregate(reference))))
                    if tau == 0 and trend == 0:
                        error = np.subtract(aggregate(risk[selected, d, r]), aggregate(reference))
                        assert abs(error.mean()) < 7*error.std(ddof=1)/math.sqrt(int(selected.sum()))+1e-5
    return counts, rows


def write_csv(path, rows):
    # LF from the outset; no after-the-fact evidence normalization needed.
    flat = [flatten(r) for r in rows]
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(flat[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(flat)


def original_replay_audit(counts, scores):
    """Byte-for-byte matching serialized numerical fields at every old setting.

    Original e=.20 covers only hot_correlated; the extended grid adds the
    other mechanisms without pretending they were in the earlier evidence.
    """
    def read(name):
        with (HERE/name).open(newline='') as stream:
            return list(csv.DictReader(stream))
    def key(r):
        return tuple(str(r[k]) for k in KEYS)
    old_counts = {(key(r), r['design']): r for r in read('r22-counts-sol1.csv')}
    old_scores = {(key(r), r['design'], r['rule'], r['pair']): r for r in read('r22-scores-sol1.csv')}
    checks = 0
    hashes = [hashlib.sha256(), hashlib.sha256()]
    for new_rows, old_lookup, fields in (
        (counts, old_counts, ('trials', 'qualified', 'success_estimate', 'success_lo', 'success_hi',
                             'exact_success', 'mean_m_estimate', 'mean_m_lo', 'mean_m_hi',
                             'attempted_estimate', 'attempted_lo', 'attempted_hi')),
        (scores, old_scores, tuple(f'{field}_{suffix}'
            for field in ('fpr', 'future_pass_fpr', 'threshold', 'delta_threshold_oracle', 'delta_fpr_oracle', 'iid_reference')
            for suffix in ('estimate', 'lo', 'hi')) + ('common_with_oracle',))):
        for r in new_rows:
            if r['design'] not in ('oracle8', 'C10') or r.get('horizon', 'legacy_C10') != 'legacy_C10':
                continue
            design = 'r22' if r['design'] == 'C10' else 'oracle8'
            lookup_key = (key(r), design) + ((r['rule'], r['pair']) if 'rule' in r else ())
            if lookup_key not in old_lookup:
                continue
            old = old_lookup[lookup_key]
            new = {k: str(v) for k, v in flatten(r).items()}
            for field in fields:
                assert new[field] == old[field], (lookup_key, field, new[field], old[field])
                for digest, data in zip(hashes, (new[field], old[field])):
                    digest.update((data+'\n').encode())
                checks += 1
    assert checks > 0
    return dict(equal_numeric_fields=checks, new_serialized_sha256=hashes[0].hexdigest(),
                original_serialized_sha256=hashes[1].hexdigest())


class Checks(unittest.TestCase):
    def assert_array_bytes(self, actual, expected):
        # The available Python 3.14/NumPy 2.2.6 combination has broken large
        # ndarray comparison temporaries. Compare shape/dtype and raw bytes;
        # this is also stricter evidence for preservation of the C10 tape.
        self.assertEqual(actual.shape, expected.shape)
        self.assertEqual(actual.dtype, expected.dtype)
        self.assertEqual(actual.tobytes(), expected.tobytes())

    def test_every_bar_tape_all_caps(self):
        bars = np.array(list(itertools.product((False, True), repeat=12)))
        masks, _, ok, attempts = selectors(bars, np.ones((len(bars), 2, 12, 7), dtype=bool))
        for i, bar in enumerate(bars):
            for d, cap in enumerate(CAPS, 1):
                expected = [j for j in range(cap) if not bar[j]][:8]
                self.assertEqual(np.flatnonzero(masks[i, d]).tolist(), expected)
                self.assertEqual(bool(ok[i, d]), len(expected) == 8)
                self.assertEqual(attempts[i, d], expected[-1]+1 if len(expected) == 8 else cap)

    def test_no_top_up_and_failed_late_reserves(self):
        members = np.ones((2, 2, 12, 7), dtype=bool)
        members[0, :, :8, :3] = False
        bars = np.zeros((2, 12), dtype=bool)
        bars[1, [0, 1, 2, 10]] = True
        _, m, ok, attempts = selectors(bars, members)
        np.testing.assert_array_equal(attempts[0], [8, 8, 8, 8])
        np.testing.assert_array_equal(m[0], 32)
        self.assertFalse(ok[0].any())
        np.testing.assert_array_equal(attempts[1], [8, 10, 11, 12])
        np.testing.assert_array_equal(ok[1], [True, False, False, True])

    def test_original_prefix_selection_thresholds_and_draws(self):
        rng, old_rng = np.random.default_rng(SEED), np.random.default_rng(SEED)
        suffix = np.random.default_rng(np.random.SeedSequence([SEED, 11, 12]))
        for n in (2000, 2000, 17):
            full = tape(rng, suffix, n)
            old = draws(old_rng, n, 10)
            for a, b in zip(full, old):
                self.assert_array_bytes(a[:, :, :10] if a.ndim == 4 else a[:, :10], b)
            eps, _, _, bar_u, member_u = full
            members = member_u >= .2
            masks, m, ok, attempts = selectors(bar_u < .25, members)
            om, oc, oq, oa = original.selectors(bar_u[:, :10] < .25, members[:, :, :10])
            ot = original.thresholds(eps[:, :, :10], members[:, :, :10], om, oc)
            nt = thresholds(eps, members, masks, m)
            for d, od in ((0, 0), (1, 3)):
                self.assert_array_bytes(m[:, d], oc[:, od])
                self.assert_array_bytes(ok[:, d], oq[:, od])
                self.assert_array_bytes(attempts[:, d], oa[:, od])
                self.assert_array_bytes(nt[:, d], ot[:, od])

    def test_exact_probabilities_and_reserve_attempts(self):
        for q in (.125, .25):
            for cap in CAPS:
                bars = list(itertools.product((False, True), repeat=cap))
                weights = [q**sum(b)*(1-q)**(cap-sum(b)) for b in bars]
                successes, reserves = [], []
                for b in bars:
                    chosen = [j for j, barred in enumerate(b) if not barred][:8]
                    successes.append(len(chosen) == 8)
                    reserves.append((chosen[-1]+1 if len(chosen) == 8 else cap)-8)
                prob, attempted = exact_counts(q, 0, cap)
                self.assertAlmostEqual(prob, math.fsum(w*s for w, s in zip(weights, successes)), places=13)
                self.assertAlmostEqual(attempted, math.fsum(w*r for w, r in zip(weights, reserves)), places=13)
                self.assertAlmostEqual(exact_counts(q, .2, cap)[0], prob*exact_completion(.2, 8))
        self.assertLess(exact_counts(.25, .1, 13)[0], .95)
        self.assertGreater(exact_counts(.25, .1, 14)[0], .95)

    def test_future_horizon_and_populations(self):
        t = np.array([1.2, 2.5])
        for mechanism in original.MECHANISMS:
            result = future_risk(t, .5, .05, mechanism, .25, True)
            hot_weight = 1/12 if mechanism == 'hot_correlated' else .25
            expected = []
            for threshold in t:
                tails = []
                for j in (12, 13, 14):
                    centered = threshold-.05*j
                    tail = lambda x: .5*math.erfc(x/math.sqrt(2))
                    tails.append(tail(centered/math.sqrt(1.25)) if mechanism == 'gaussian_independent'
                                 else hot_weight*tail(centered-.5*math.sqrt(3))
                                 + (1-hot_weight)*tail(centered+.5/math.sqrt(3)))
                expected.append(math.fsum(tails)/3)
            np.testing.assert_allclose(result, expected, atol=1e-15, rtol=0)
        np.testing.assert_array_equal(t, [1.2, 2.5])

    def test_deterministic_serialized_replay(self):
        args = ('hot_correlated', .25, .1, .5, .05, 500, 100)
        first = json.dumps(simulate(*args), sort_keys=True, allow_nan=False).encode()
        second = json.dumps(simulate(*args), sort_keys=True, allow_nan=False).encode()
        self.assertEqual(first, second)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--profile', action='store_true')
    args = parser.parse_args()
    if args.check:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
        return 0 if result.wasSuccessful() else 1
    if args.profile:
        started = time.monotonic()
        simulate('hot_correlated', .25, .1, .5, .05, 10_000)
        print(f'PILOT 10000 studies {time.monotonic()-started:.3f}s; one process/thread; no speed optimization')
        return 0
    started = time.monotonic()
    counts, scores = [], []
    for setting in scenario_grid():
        c, s = simulate(*setting)
        counts.extend(c)
        scores.extend(s)
        print('completed', *setting, flush=True)
    replay = original_replay_audit(counts, scores)
    for name, rows in (('counts', counts), ('scores', scores)):
        write_csv(HERE/f'{PREFIX}-{name}-sol1.csv', rows)
    source_names = (Path(__file__).name, 'simulate_r22_sol1.py', 'simulate_sol1.py')
    output_names = tuple(f'{PREFIX}-{n}-sol1.csv' for n in ('counts', 'scores'))
    metadata = dict(seed=SEED, suffix_seed_sequence=[SEED, 11, 12], trials_per_setting=TRIALS,
        batch=BATCH, settings=scenario_grid(), python=platform.python_version(), numpy=np.__version__,
        elapsed_seconds=time.monotonic()-started, horizons=HORIZONS, caps=CAPS,
        designs=DESIGNS, rules=original.RULES,
        ci='Pointwise 95% Monte Carlo; Wilson proportions, whole-study normal means/paired contrasts; own-population difference uses conservative Cauchy SE bound.',
        reserve_expectation='Unconditional over all started studies, including failures; barred reserve attempts count.',
        original_replay=replay,
        source_sha256={name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in source_names},
        output_sha256={name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in output_names})
    (HERE/f'{PREFIX}-metadata-sol1.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps({'elapsed_seconds': metadata['elapsed_seconds'], 'count_rows': len(counts),
                      'score_rows': len(scores), 'original_replay': replay}, sort_keys=True), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
