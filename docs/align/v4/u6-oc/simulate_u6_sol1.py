#!/usr/bin/env python3
"""Synthetic U6 OC, Python stdlib only; no data/config/weight readers or network.

Run from the clone root with Python 3.13 -B. Output goes to stdout. Only
--check imports the two pure repository estimators, on in-memory fixtures.
The Monte Carlo itself uses exact Gaussian trajectory sufficient statistics.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
from pathlib import Path
import random
import sys

Z90 = 1.645  # Match v4_estimands.py:224 exactly, including CR0 (no correction).
Z95 = 1.959963984540054
DRIFTS = (0.0, 0.25, 0.5, 1.0)
SCALES = (0.7, 1.0, 1.3)


@dataclass(frozen=True)
class Episode:
    pair: int
    trajectory: tuple[int, int]
    window: int
    turns: int
    late: bool = False


def roster(windows, per_pair=7, turns=3, *, retained=None, sentinels=False):
    """Fresh benign only, with optional repeated spam seed-1 sentinels.

    W1/anchors/contrasts/sabotage never supply fresh calibration members.
    Per-pair member order is chronological; exact within-window interleaving
    is immaterial to this function's within-pair split. retained=39 drops
    the last three fresh members of each pair from the six-window plan.
    """
    episodes = []
    for pair in range(2):
        group = []
        fresh = 0
        for window in range(windows):
            if sentinels and pair == 0:
                group.append(Episode(pair, (pair, -1), window, turns))
            for _ in range(per_pair):
                if retained is None or fresh < retained:
                    group.append(Episode(pair, (pair, fresh), window, turns))
                fresh += 1
            if sentinels and pair == 0:
                group.append(Episode(pair, (pair, -1), window, turns))
        middle = len(group) // 2
        episodes.extend(Episode(r.pair, r.trajectory, r.window, r.turns, i >= middle)
                        for i, r in enumerate(group))
    return episodes


def contrast(episodes, means):
    """Algebraic reduction of the registered per-turn OLS cluster sandwich.

    Each episode's turn sum is L*mean. For cluster g its late-coefficient
    score is sum_late L*(mean-mu_late)/n_late minus the early counterpart.
    Repeated trajectory ids share one score, including across halves.
    """
    totals, ns = [0.0, 0.0], [0, 0]
    for r, y in zip(episodes, means):
        h = int(r.late)
        totals[h] += r.turns * y
        ns[h] += r.turns
    mus = [totals[h] / ns[h] for h in range(2)]
    scores = {}
    for r, y in zip(episodes, means):
        h = int(r.late)
        score = (1 if h else -1) * r.turns * (y - mus[h]) / ns[h]
        scores[r.trajectory] = scores.get(r.trajectory, 0.0) + score
    return mus[1] - mus[0], math.sqrt(sum(s*s for s in scores.values()))


def verdict(effect, se, scale, *, ci_fail=False):
    margin = 0.5 * scale
    if abs(effect) > margin + (Z90 * se if ci_fail else 0.0):
        return 1  # FAIL
    if abs(effect) + Z90 * se <= margin:
        return 0  # PASS
    return 2  # INCONCLUSIVE: calibration unresolved: imprecise


def wilson(k, n):
    p = k / n
    denom = 1 + Z95**2 / n
    center = (p + Z95**2 / (2*n)) / denom
    radius = Z95 * math.sqrt(p*(1-p)/n + Z95**2/(4*n*n)) / denom
    return max(0.0, center-radius), min(1.0, center+radius)


def rate(k, n):
    lo, hi = wilson(k, n)
    return f'{100*k/n:.2f} [{100*lo:.2f},{100*hi:.2f}]'


def fixture_check():
    # Import only local source; never the kit builder or any session/data reader.
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
    from joulewise.align.apple.thermal_desk import monitoring_stability_v4
    from joulewise.align.apple.v4_estimands import u6_stability, d_turn_position_means

    cases = 0
    for episodes in (roster(1), roster(6, retained=39), roster(6, sentinels=True)):
        rng = random.Random(873)
        records, flat, positions, means = [], [], [], []
        for i, r in enumerate(episodes):
            # Ragged lengths and pair/id collisions exercise weighting/clustering.
            values = [rng.gauss(0, 1) + .4*r.late for _ in range(1 + i % 5)]
            means.append(sum(values)/len(values))
            records.append(dict(pair=r.pair, trajectory=r.trajectory[1],
                                start_ns=i, residual_j=values))
        # The desk splits records again. Ragged lengths do not change halves.
        ragged = [Episode(r.pair, r.trajectory, r.window, len(row['residual_j']), r.late)
                  for r, row in zip(episodes, records)]
        for r, row in zip(ragged, records):
            for p, y in enumerate(row['residual_j']):
                flat.append(dict(trajectory=r.trajectory, half='late' if r.late else 'early', residual_j=y))
                positions.append(dict(trajectory=r.trajectory, turn_position=p, residual_j=y))
        effect, se = contrast(ragged, means)
        helper = u6_stability(flat, cell_residual_sd=1.0)
        for scale in SCALES:
            desk = monitoring_stability_v4(records, cell_residual_sd=scale,
                                          split_rule='within_pair_episode_order')
            assert math.isclose(desk['effect_j'], effect, abs_tol=1e-12)
            assert math.isclose(desk['trajectory_clustered_se_j'], se, abs_tol=1e-12)
            assert math.isclose(helper['trajectory_clustered_se_j'], se, abs_tol=1e-12)
            assert ('pass', 'fail', 'inconclusive')[verdict(effect, se, scale)] == desk['status']
            assert desk['turn_position_residual_means'] == d_turn_position_means(positions)
            cases += 1
    # Deterministic classification boundaries and a positive boundary failure.
    assert verdict(.5, 0, 1) == 0
    assert verdict(.500001, 0, 1) == 1
    assert verdict(.49, .1, 1) == 2
    assert verdict(.51, .1, 1, ci_fail=True) == 2
    assert verdict(.7, .1, 1, ci_fail=True) == 1
    assert wilson(0, 20000)[1] > 0  # Never print zero uncertainty for zero events.
    print(f'CHECK: {cases} full-desk/helper equivalence fixtures; boundaries PASS')


def simulate(name, episodes, rho, trials, seed, *, eta=0.0, ci_fail=False):
    """Per-turn var=1; within-episode ICC=rho; between-trajectory/window=eta.

    Residual = sqrt(eta)*W_window + sqrt(rho-eta)*U_trajectory
               + sqrt(1-rho)*epsilon_turn.
    For fresh trajectories, average residual is exactly normal with variance
    rho-eta+(1-rho)/L, plus its window effect. Sentinel reruns share U.
    Half-step drift is added analytically; CR0 is invariant to that shift.
    """
    assert 0 <= eta <= rho <= 1
    rng = random.Random(seed)
    counts = {(d, s): [0, 0, 0] for d in DRIFTS for s in SCALES}
    clusters = {r.trajectory for r in episodes}
    repeated = len(clusters) < len(episodes)
    ses = []
    for _ in range(trials):
        offsets = {w: rng.gauss(0, math.sqrt(eta)) for w in {r.window for r in episodes}} if eta else {}
        if repeated:
            shared = {c: rng.gauss(0, math.sqrt(rho-eta)) for c in sorted(clusters)}
            means = [offsets.get(r.window, 0.0) + shared[r.trajectory]
                     + rng.gauss(0, math.sqrt((1-rho)/r.turns)) for r in episodes]
        else:
            means = [offsets.get(r.window, 0.0)
                     + rng.gauss(0, math.sqrt(rho-eta+(1-rho)/r.turns)) for r in episodes]
        effect, se = contrast(episodes, means)
        ses.append(se)
        for d in DRIFTS:
            for s in SCALES:
                counts[d, s][verdict(effect+d, se, s, ci_fail=ci_fail)] += 1
    print(f'\nPROFILE {name}: episodes={len(episodes)}, clusters={len(clusters)}, '
          f'turns={sorted({r.turns for r in episodes})}, rho={rho}, eta={eta}, '
          f'mean_se={sum(ses)/trials:.5f}, fail_rule={"CI outside" if ci_fail else "point outside"}')
    print('| drift/s_true | s_used/s_true | PASS % [95% MC] | FAIL % [95% MC] | IMPRECISE % [95% MC] |')
    print('|---:|---:|---:|---:|---:|')
    for (d, s), c in counts.items():
        print(f'| {d:g} | {s:g} | ' + ' | '.join(rate(k, trials) for k in c) + ' |')


def stopping(trials, seed):
    print('\nCOUNT-ONLY STOP (synthetic, independent of residual draws):')
    for member_loss, window_loss in ((0, 0), (.10, 0), (.15, 0), (.05, .10)):
        rng = random.Random(seed)
        counts = {6: 0, 7: 0, 8: 0, 'cap_unresolved': 0}
        for _ in range(trials):
            eligible = [0, 0]
            for w in range(1, 9):
                if rng.random() >= window_loss:
                    for p in range(2):
                        eligible[p] += sum(rng.random() >= member_loss for _ in range(7))
                if w >= 6 and min(eligible) >= 39:
                    counts[w] += 1
                    break
            else:
                counts['cap_unresolved'] += 1
        print(f'member_loss={member_loss:g}, window_loss={window_loss:g}: '
              + '; '.join(f'{k}={rate(v, trials)}' for k, v in counts.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='run in-memory estimator equivalence checks only')
    parser.add_argument('--trials', type=int, default=20000)
    parser.add_argument('--seed', type=int, default=20261108)
    args = parser.parse_args()
    if args.check:
        fixture_check()
        return
    if args.trials < 1:
        parser.error('--trials must be positive')
    print(f'U6 OC sol1 | synthetic only | seed={args.seed} | trials/profile={args.trials}')
    print('s_true=1 per turn; delta=late-minus-early mean step; normal random intercept + noise.')
    print('All intervals: pointwise Wilson 95% Monte Carlo, not hardware uncertainty.')
    print('FAIL = abs(point)>0.5*s_used; PASS = whole 90% CR0 CI inside; remainder IMPRECISE.')
    profiles = [
        ('D-single', roster(1), .5, 0, False),
        ('C6-m42', roster(6), .5, 0, False),
        ('C7-m49', roster(7), .5, 0, False),
        ('C8-m56', roster(8), .5, 0, False),
        ('C6-eligible-m39', roster(6, retained=39), .5, 0, False),
        ('C6-rho0', roster(6), 0, 0, False),
        ('C6-rho09', roster(6), .9, 0, False),
        ('C6-one-turn', roster(6, turns=1), .5, 0, False),
        ('C6-six-turns', roster(6, turns=6), .5, 0, False),
        ('C6-ceiling-12-turns', roster(6, turns=12), .5, 0, False),
        ('C6-plus-sentinels', roster(6, sentinels=True), .5, 0, False),
        ('C6-window-correlation', roster(6), .5, .2, False),
        ('T3-if-same-shape', roster(3), .5, 0, False),
        ('proposal-14-per-pair-window', roster(6, per_pair=14), .5, 0, False),
        ('proposal-36-per-pair-window-rho09', roster(6, per_pair=36), .9, 0, False),
        ('proposal-CI-fail-C6', roster(6), .5, 0, True),
    ]
    for i, (name, episodes, rho, eta, ci_fail) in enumerate(profiles):
        simulate(name, episodes, rho, args.trials, args.seed+i, eta=eta, ci_fail=ci_fail)
    stopping(args.trials, args.seed+100)
    print('\nEND: No product code or coordination state changed; prospective candidates are not adopted.')


if __name__ == '__main__':
    main()
