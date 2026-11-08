#!/usr/bin/env python3
"""Synthetic R24 C10--C14 confirmation and stop-relative T sensitivity.

Preserve the R22 seed, grid, chunk size, C1--C12 tape and arithmetic. Append
C13/C14 using a third, independent generator. No measurement/data/model I/O.
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
import time
import unittest

import numpy as np

import simulate_r22_cap_sweep_sol1 as prior
from simulate_sol1 import exact_completion, flatten, mean_ci, probability_ci, ranks

HERE = Path(__file__).resolve().parent
SEED, TRIALS, BATCH = prior.SEED, prior.TRIALS, prior.BATCH
CAPS = (10, 11, 12, 13, 14)
DESIGNS = ('oracle8',) + tuple(f'C{c}' for c in CAPS)
KEYS = prior.KEYS
PREFIX = 'r24-c14-confirm'
HORIZONS = ('fixed_after_C14', 'after_stop')


def tape(rng, suffix_rng, extension_rng, n):
    first = prior.tape(rng, suffix_rng, n)
    suffix = prior.draws(extension_rng, n, 2)
    return tuple(np.concatenate((a, b), axis=2 if a.ndim == 4 else 1)
                 for a, b in zip(first, suffix))


def selectors(barred, member_ok):
    """Stop at eight admitted windows, even on low m; bars alone arm reserves."""
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
    n, _, windows, _ = scores.shape
    result = np.empty((n, len(DESIGNS), 3, 2))
    for d in range(len(DESIGNS)):
        eligible = member_ok & masks[:, d, None, :, None]
        ordered = np.sort(np.where(eligible, scores, np.inf).reshape(n, 2, windows*7), axis=2)
        for r, k in enumerate(ranks(counts[:, d])):
            result[:, d, r] = np.take_along_axis(
                ordered, np.maximum(np.subtract(k, 1), 0)[:, :, None], axis=2)[:, :, 0]
    return result


def future_risk(threshold, attempted, tau, trend, mechanism, bar_p,
                admitted=False, horizon='after_stop'):
    """T1 zero-based position = stop (variable) or 14 (fixed); then T2/T3.

    Reuse the original tail integration and summation order. Its T1 is at
    zero-based 10, so moving T by d means subtracting b*d from the threshold.
    Failed studies have placeholder risks, always excluded by qualification.
    """
    if trend == 0:
        adjusted = threshold
    elif horizon == 'after_stop':
        offset = np.multiply(trend, np.subtract(attempted, 10))[:, :, None, None]
        adjusted = np.subtract(threshold, offset)
    elif horizon == 'fixed_after_C14':
        adjusted = np.subtract(threshold, 4*trend)
    elif horizon == 'after_C12':
        adjusted = np.subtract(threshold, 2*trend)
    elif horizon == 'legacy_C10':
        adjusted = threshold
    else:
        raise ValueError(horizon)
    return prior.original.future_risk(adjusted, tau, trend, mechanism, bar_p, admitted)


def score_rows(key, t, m, ok, attempted, horizon, designs=DESIGNS):
    args = dict(tau=key['tau'], trend=key['trend'], mechanism=key['mechanism'],
                bar_p=key['bar_p'], horizon=horizon)
    risk = future_risk(t, attempted, **args)
    passed = future_risk(t, attempted, **args, admitted=True)
    rows = []
    for d, design in enumerate(designs):
        selected = ok[:, d]
        common = selected & ok[:, 0]
        cap_common = selected & ok[:, 1]
        for r, rule in enumerate(prior.original.RULES):
            for pair, ix in (('spam_filter_update', 0), ('bank_transfer_2', 1), ('pair_mean', None)):
                def aggregate(a):
                    return a.mean(axis=1) if ix is None else a[:, ix]
                fpr = mean_ci(aggregate(risk[selected, d, r]))
                pass_fpr = mean_ci(aggregate(passed[selected, d, r]))
                oracle_pass = mean_ci(aggregate(passed[ok[:, 0], 0, r]))
                c10_pass = mean_ci(aggregate(passed[ok[:, 1], 1, r]))
                reference = np.divide(np.subtract(np.add(m[selected, d], 1),
                    ranks(m[selected, d])[r]), np.add(m[selected, d], 1))
                rows.append(dict(**key, horizon=horizon, design=design, rule=rule, pair=pair,
                    fpr=fpr, future_pass_fpr=pass_fpr,
                    threshold=mean_ci(aggregate(t[selected, d, r])),
                    common_with_oracle=int(common.sum()),
                    delta_threshold_oracle=mean_ci(aggregate(np.subtract(t[common, d, r], t[common, 0, r]))),
                    delta_fpr_oracle=mean_ci(aggregate(np.subtract(risk[common, d, r], risk[common, 0, r]))),
                    delta_future_pass_oracle=mean_ci(aggregate(np.subtract(passed[common, d, r], passed[common, 0, r]))),
                    population_delta_future_pass_oracle=prior.population_delta(pass_fpr, oracle_pass),
                    common_with_C10=int(cap_common.sum()),
                    delta_threshold_C10=mean_ci(aggregate(np.subtract(t[cap_common, d, r], t[cap_common, 1, r]))),
                    delta_future_pass_C10=mean_ci(aggregate(np.subtract(passed[cap_common, d, r], passed[cap_common, 1, r]))),
                    iid_reference=mean_ci(aggregate(reference)),
                    population_delta_future_pass_C10=prior.population_delta(pass_fpr, c10_pass)))
                if key['tau'] == 0 and key['trend'] == 0:
                    error = np.subtract(aggregate(risk[selected, d, r]), aggregate(reference))
                    assert abs(error.mean()) < 7*error.std(ddof=1)/math.sqrt(int(selected.sum()))+1e-5
    return rows


def simulate(mechanism, bar_p, member_p, tau, trend, trials=TRIALS, batch=BATCH,
             seed=SEED, replay=None):
    rng = np.random.default_rng(seed)
    suffix_rng = np.random.default_rng(np.random.SeedSequence([seed, 11, 12]))
    extension_rng = np.random.default_rng(np.random.SeedSequence([seed, 13, 14]))
    t = np.empty((trials, len(DESIGNS), 3, 2))
    m = np.empty((trials, len(DESIGNS), 2), dtype=np.int64)
    ok = np.empty((trials, len(DESIGNS)), dtype=bool)
    attempted = np.empty((trials, len(DESIGNS)), dtype=np.int64)
    for start in range(0, trials, batch):
        n = min(batch, trials-start)
        eps, normal, hot, bar_u, member_u = tape(rng, suffix_rng, extension_rng, n)
        z = normal if mechanism == 'gaussian_independent' else np.divide(
            np.subtract(hot, .25), math.sqrt(.25*.75))
        bp = np.where(hot, 3*bar_p, bar_p/3) if mechanism == 'hot_correlated' else bar_p
        members = member_u >= member_p
        masks, counts, qualified, attempts = selectors(bar_u < bp, members)
        scores = np.add(np.add(eps, np.multiply(tau, z[:, None, :, None])),
                        np.multiply(trend, np.arange(14)[None, None, :, None]))
        out = slice(start, start+n)
        t[out] = thresholds(scores, members, masks, counts)
        m[out], ok[out], attempted[out] = counts, qualified, attempts
    key = dict(zip(KEYS, (mechanism, bar_p, member_p, tau, trend)))
    counts, rows = [], []
    for d, design in enumerate(DESIGNS):
        exact, reserves = (exact_completion(member_p, 8), 0.) if d == 0 else prior.exact_counts(bar_p, member_p, CAPS[d-1])
        n_ok = int(ok[:, d].sum())
        tolerance = 7*math.sqrt(exact*(1-exact)/trials)+7/trials
        assert abs(n_ok/trials-exact) < tolerance, (key, design, n_ok/trials, exact)
        counts.append(dict(**key, design=design, trials=trials, qualified=n_ok,
            success=probability_ci(n_ok, trials), exact_success=exact,
            mean_m=mean_ci(m[ok[:, d], d].mean(axis=1)),
            attempted=mean_ci(attempted[:, d]),
            reserves_attempted=mean_ci(np.subtract(attempted[:, d], 8)),
            exact_reserves_attempted=reserves,
            qualified_stop=mean_ci(attempted[ok[:, d], d])))
    for horizon in HORIZONS:
        rows.extend(score_rows(key, t, m, ok, attempted, horizon))
    if replay is not None:
        # Compatibility calendars are solely replay checks, not candidate
        # schedules for C13/C14. Do not publish their risks as primary results.
        replay.check(counts, 'counts')
        for horizon in prior.HORIZONS:
            replay.check(score_rows(key, t[:, :4], m[:, :4], ok[:, :4],
                                    attempted[:, :4], horizon, prior.DESIGNS), 'scores')
    return counts, rows


class PriorReplay:
    """Compare every serialized old field, not only a selected numerical subset."""
    def __init__(self):
        self.old = {}
        self.fields = 0
        self.rows = dict(counts=0, scores=0)
        self.digests = [hashlib.sha256(), hashlib.sha256()]
        for kind in self.rows:
            with (HERE/f'r22-cap-sweep-{kind}-sol1.csv').open(newline='') as stream:
                self.old[kind] = {self.key(r, kind): r for r in csv.DictReader(stream)}

    @staticmethod
    def key(row, kind):
        fields = KEYS + ('design',) + (('horizon', 'rule', 'pair') if kind == 'scores' else ())
        return tuple(str(row[k]) for k in fields)

    def check(self, rows, kind):
        for row in rows:
            if row['design'] not in prior.DESIGNS:
                continue
            new = {k: str(v) for k, v in flatten(row).items()}
            old = self.old[kind][self.key(new, kind)]
            for field, value in old.items():
                assert new[field] == value, (self.key(new, kind), field, new[field], value)
                for digest, data in zip(self.digests, (new[field], value)):
                    digest.update((data+'\n').encode())
                self.fields += 1
            self.rows[kind] += 1

    def receipt(self):
        assert self.rows == dict(counts=288, scores=5184), self.rows
        return dict(equal_fields=self.fields, equal_rows=self.rows,
                    new_serialized_sha256=self.digests[0].hexdigest(),
                    prior_serialized_sha256=self.digests[1].hexdigest())


class Checks(unittest.TestCase):
    def test_all_16384_bar_tapes(self):
        bars = np.array(list(itertools.product((False, True), repeat=14)))
        masks, _, ok, attempts = selectors(bars, np.ones((len(bars), 2, 14, 7), dtype=bool))
        for i, bar in enumerate(bars):
            for d, cap in enumerate(CAPS, 1):
                expected = [j for j in range(cap) if not bar[j]][:8]
                self.assertEqual(np.flatnonzero(masks[i, d]).tolist(), expected)
                self.assertEqual(bool(ok[i, d]), len(expected) == 8)
                self.assertEqual(attempts[i, d], expected[-1]+1 if len(expected) == 8 else cap)

    def test_no_top_up_and_c13_c14_rescue(self):
        bars = np.zeros((3, 14), dtype=bool)
        bars[1, :5] = True
        bars[2, :6] = True
        members = np.ones((3, 2, 14, 7), dtype=bool)
        members[0, :, :8, :3] = False
        _, m, ok, attempts = selectors(bars, members)
        self.assertEqual(attempts[0].tolist(), [8]*6)
        self.assertEqual(m[0].tolist(), [[32, 32]]*6)
        self.assertFalse(ok[0].any())
        self.assertEqual(ok[1].tolist(), [True, False, False, False, True, True])
        self.assertEqual(ok[2].tolist(), [True, False, False, False, False, True])
        self.assertEqual(attempts[1].tolist(), [8, 10, 11, 12, 13, 13])
        self.assertEqual(attempts[2].tolist(), [8, 10, 11, 12, 13, 14])

    def test_c1_c12_tape_and_threshold_bytes(self):
        generators = lambda: (np.random.default_rng(SEED), np.random.default_rng(
            np.random.SeedSequence([SEED, 11, 12])))
        rng, suffix = generators()
        old_rng, old_suffix = generators()
        extension = np.random.default_rng(np.random.SeedSequence([SEED, 13, 14]))
        for n in (2000, 2000, 17):
            full = tape(rng, suffix, extension, n)
            old = prior.tape(old_rng, old_suffix, n)
            for a, b in zip(full, old):
                a = a[:, :, :12] if a.ndim == 4 else a[:, :12]
                self.assertEqual((a.shape, a.dtype, a.tobytes()), (b.shape, b.dtype, b.tobytes()))
            eps, normal, _, bar_u, member_u = full
            members = member_u >= .2
            masks, m, ok, attempts = selectors(bar_u < .25, members)
            om, oc, oq, oa = prior.selectors(bar_u[:, :12] < .25, members[:, :, :12])
            for trend in (0., .05):
                scores = np.add(np.add(eps, np.multiply(.5, normal[:, None, :, None])),
                                np.multiply(trend, np.arange(14)[None, None, :, None]))
                nt = thresholds(scores, members, masks, m)[:, :4]
                ot = prior.thresholds(scores[:, :, :12], members[:, :, :12], om, oc)
                self.assertEqual(nt.tobytes(), ot.tobytes())
            for a, b in ((m[:, :4], oc), (ok[:, :4], oq), (attempts[:, :4], oa)):
                self.assertEqual((a.shape, a.dtype, a.tobytes()), (b.shape, b.dtype, b.tobytes()))

    def test_exact_probability_and_workload_by_enumeration(self):
        for cap in (13, 14):
            for q in (.125, .25):
                successes, attempts = [], []
                for bars in itertools.product((False, True), repeat=cap):
                    weight = q**sum(bars)*(1-q)**(cap-sum(bars))
                    chosen = [j for j, bar in enumerate(bars) if not bar][:8]
                    successes.append(weight*(len(chosen) == 8))
                    attempts.append(weight*((chosen[-1]+1 if len(chosen) == 8 else cap)-8))
                exact, reserves = prior.exact_counts(q, .1, cap)
                self.assertAlmostEqual(exact, math.fsum(successes)*exact_completion(.1, 8), places=13)
                self.assertAlmostEqual(reserves, math.fsum(attempts), places=13)

    def test_variable_t_against_scalar_tails(self):
        t = np.full((3, 6, 3, 2), 2.1)
        stops = np.tile([8, 9, 10, 11, 13, 14], (3, 1))
        for mechanism in prior.original.MECHANISMS:
            for admitted in (False, True):
                for horizon in HORIZONS:
                    actual = future_risk(t, stops, .5, .05, mechanism, .25, admitted, horizon)
                    for d, stop in enumerate(stops[0]):
                        js = range(stop, stop+3) if horizon == 'after_stop' else range(14, 17)
                        hot_weight = 1/12 if admitted and mechanism == 'hot_correlated' else .25
                        tail = lambda x: .5*math.erfc(x/math.sqrt(2))
                        values = []
                        for j in js:
                            centered = 2.1-.05*j
                            values.append(tail(centered/math.sqrt(1.25)) if mechanism == 'gaussian_independent'
                                else hot_weight*tail(centered-.5*math.sqrt(3))
                                + (1-hot_weight)*tail(centered+.5/math.sqrt(3)))
                        self.assertAlmostEqual(float(actual[0, d, 0, 0]), math.fsum(values)/3, places=15)
        self.assertEqual(t.tobytes(), np.full_like(t, 2.1).tobytes())

    def test_no_drift_horizons_and_c10_stopped_identity(self):
        counts, rows = simulate('hot_correlated', .25, .1, .5, 0., 500, 100)
        left, right = (rows[:len(rows)//2], rows[len(rows)//2:])
        for a, b in zip(left, right):
            self.assertEqual({k: v for k, v in a.items() if k != 'horizon'},
                             {k: v for k, v in b.items() if k != 'horizon'})
        _, rows = simulate('hot_correlated', .25, .1, .5, .05, 500, 100)
        for row in rows:
            if row['design'] != 'oracle8':
                self.assertEqual(row['delta_threshold_C10'], [0.]*3)
                self.assertEqual(row['delta_future_pass_C10'], [0.]*3)

    def test_deterministic_serialized_replay(self):
        args = ('hot_correlated', .25, .1, .5, .05, 500, 100)
        first = json.dumps(simulate(*args), sort_keys=True, allow_nan=False).encode()
        self.assertEqual(first, json.dumps(simulate(*args), sort_keys=True, allow_nan=False).encode())


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
    replay = PriorReplay()
    for setting in prior.scenario_grid():
        c, s = simulate(*setting, replay=replay)
        counts.extend(c)
        scores.extend(s)
        print('completed', *setting, flush=True)
    for name, rows in (('counts', counts), ('scores', scores)):
        prior.write_csv(HERE/f'{PREFIX}-{name}-sol1.csv', rows)
    source_names = (Path(__file__).name, 'simulate_r22_cap_sweep_sol1.py', 'simulate_r22_sol1.py', 'simulate_sol1.py')
    output_names = tuple(f'{PREFIX}-{n}-sol1.csv' for n in ('counts', 'scores'))
    input_names = tuple(f'r22-cap-sweep-{n}-sol1.csv' for n in ('counts', 'scores'))
    hashes = lambda names: {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in names}
    metadata = dict(seed=SEED, suffix_seed_sequence=[SEED, 11, 12], extension_seed_sequence=[SEED, 13, 14],
        trials_per_setting=TRIALS, batch=BATCH, settings=prior.scenario_grid(),
        python=platform.python_version(), numpy=np.__version__, elapsed_seconds=time.monotonic()-started,
        horizons={'fixed_after_C14': [15, 16, 17], 'after_stop': 'stop+1, stop+2, stop+3 (one-based)'},
        caps=CAPS, designs=DESIGNS, rules=prior.original.RULES,
        ci='Pointwise 95% MC; Wilson proportions, whole-study normal means/paired contrasts; own-population differences use conservative Cauchy SE bound.',
        reserve_expectation='Unconditional over all started studies, including failures; barred reserve attempts count.',
        prior_replay=replay.receipt(), source_sha256=hashes(source_names),
        input_sha256=hashes(input_names), output_sha256=hashes(output_names))
    (HERE/f'{PREFIX}-metadata-sol1.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps({'elapsed_seconds': metadata['elapsed_seconds'], 'count_rows': len(counts),
                      'score_rows': len(scores), 'prior_replay': metadata['prior_replay']}, sort_keys=True), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
