#!/usr/bin/env python3
"""Synthetic U6 OC, sol2. Stdlib only; never opens input data or model paths.

Run from the repository root with python3.13 -B. Output is deterministic for
the same Python random implementation. Roster/source citations and limitations
are in U6-OC-sol2.md. Per-episode sufficient statistics exactly reproduce the
turn-level CR0 sandwich, including clusters that span both chronological halves.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
import random
from statistics import NormalDist
import sys


@dataclass(frozen=True)
class Episode:
    pair: int
    window: int
    trajectory: str
    turns: int = 3
    half: int = 0


def roster(counts, *, turns=3, sentinels=False, w1=False, seed_clusters=False):
    """Counts are fresh eligible benign per pair/window; no score-based stop.

    Additional records are membership/ID sensitivities, not additions to m.
    W1's two spam seed-1 replays and bank seeds 1/93 follow kit order.
    """
    result = []
    for pair in (0, 1):
        group = []
        if w1:
            for rep in (0, 1):
                identity = 'seed1' if pair == 0 or rep == 0 else 'seed93'
                if not seed_clusters:
                    identity = f'w1-{pair}-{rep}'
                group.append(Episode(pair, 0, identity, turns))
        for window, count in enumerate(counts, 1):
            if pair == 0 and sentinels:
                identity = 'seed1' if seed_clusters else f'sentinel-{window}-early'
                group.append(Episode(pair, window, identity, turns))
            for j in range(count):
                # Distinct physical episodes/held-out seed identities, per pair.
                length = (1, 3, 6)[j % 3] if turns == 0 else turns
                group.append(Episode(pair, window, f'fresh-{window}-{j}', length))
            if pair == 0 and sentinels:
                identity = 'seed1' if seed_clusters else f'sentinel-{window}-late'
                group.append(Episode(pair, window, identity, turns))
        middle = len(group) // 2
        result.extend(Episode(e.pair, e.window, e.trajectory, e.turns,
                              int(i >= middle)) for i, e in enumerate(group))
    return result


def statistic(episodes, means):
    """Exact reduction of y ~ intercept + late, CR0, no df correction."""
    n = [sum(e.turns for e in episodes if e.half == h) for h in (0, 1)]
    fitted = [sum(e.turns*y for e, y in zip(episodes, means) if e.half == h)/n[h]
              for h in (0, 1)]
    influence = {}
    for e, y in zip(episodes, means):
        key = (e.pair, e.trajectory)
        influence[key] = influence.get(key, 0.) + (
            (1 if e.half else -1)*e.turns*(y-fitted[e.half])/n[e.half])
    return fitted[1]-fitted[0], math.sqrt(sum(x*x for x in influence.values()))


def verdict(effect, se, scale):
    margin = .5*scale
    if abs(effect) > margin:
        return 1  # FAIL is a point rule, even when the interval overlaps margin.
    if effect-1.645*se >= -margin and effect+1.645*se <= margin:
        return 0
    return 2  # "calibration unresolved: imprecise" -> INCONCLUSIVE.


def wilson(count, n):
    z = NormalDist().inv_cdf(.975)
    p = count/n
    den = 1+z*z/n
    center = (p+z*z/(2*n))/den
    radius = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return f'{100*p:.2f}[{100*(center-radius):.2f},{100*(center+radius):.2f}]'


def oracle_check():
    """Check reduction against the actual v4 route on synthetic arrays only.

    Includes unequal lengths, odd/unbalanced pair counts, reused trajectory IDs,
    non-unit s_r, and shuffled input. No production reader is called.
    """
    root = Path(__file__).resolve().parents[4]
    sys.path.insert(0, str(root))
    from joulewise.align.apple import thermal_desk
    rng = random.Random(901)
    checks = 0
    for reused in (False, True):
        episodes = roster([3, 4], sentinels=True, w1=True, seed_clusters=reused)
        episodes = [Episode(e.pair, e.window, e.trajectory, 1+i % 6, e.half)
                    for i, e in enumerate(episodes)]
        raw = [[rng.gauss(0, 1) for _ in range(e.turns)] for e in episodes]
        means = [sum(values)/len(values) for values in raw]
        effect, se = statistic(episodes, means)
        rows = [dict(pair=e.pair, start_ns=i, trajectory=e.trajectory, residual_j=values)
                for i, (e, values) in enumerate(zip(episodes, raw))]
        rng.shuffle(rows)
        for drift in (0., .25, .5, 1.):
            shifted = [{**r, 'residual_j': [y+drift*episodes[r['start_ns']].half
                                            for y in r['residual_j']]} for r in rows]
            for scale in (.7, 1., 1.3):
                got = thermal_desk.monitoring_stability_v4(
                    shifted, cell_residual_sd=scale, split_rule='within_pair_episode_order')
                assert math.isclose(got['effect_j'], effect+drift, abs_tol=1e-12)
                assert math.isclose(got['trajectory_clustered_se_j'], se, abs_tol=1e-12)
                assert got['status'] == ('pass', 'fail', 'inconclusive')[verdict(effect+drift, se, scale)]
                checks += 1
        positions = got['turn_position_residual_means']
        for position in range(6):
            expected = len({(e.pair, e.trajectory) for e in episodes if e.turns > position})
            assert positions['trajectory_counts'][position] == expected
            assert positions['evaluable'][position] == (expected >= 6)
    print(f'ORACLE: {checks} route comparisons + position counts/evaluability OK')


def simulate(name, episodes, *, rho, repetitions, seed, scales=(1.,), window_share=0.,
             opposite=False):
    """Gaussian random-intercept model, true per-turn s_r=1.

    Var(episode mean) = rho+(1-rho)/turns for independent episodes.
    window_share gives a shared cross-pair window component of marginal variance.
    With reused IDs, the trajectory intercept is also shared across repeats.
    """
    rng = random.Random(seed+int.from_bytes(hashlib.sha256(name.encode()).digest()[:8], 'big'))
    clusters = list(dict.fromkeys((e.pair, e.trajectory) for e in episodes))
    windows = sorted({e.window for e in episodes})
    unique = len(clusters) == len(episodes)
    deltas = (1.,) if opposite else (0., .25, .5, 1.)
    counts = {(d, s): [0, 0, 0] for d in deltas for s in scales}
    coverage = 0
    for _ in range(repetitions):
        win = {w: math.sqrt(window_share)*rng.gauss(0, 1) for w in windows} if window_share else {}
        if unique:
            means = [win.get(e.window, 0.) + math.sqrt((1-window_share)*(rho+(1-rho)/e.turns))
                     * rng.gauss(0, 1) for e in episodes]
        else:
            shared = {c: math.sqrt((1-window_share)*rho)*rng.gauss(0, 1) for c in clusters}
            means = [win.get(e.window, 0.)+shared[e.pair, e.trajectory]
                     + math.sqrt((1-window_share)*(1-rho)/e.turns)*rng.gauss(0, 1)
                     for e in episodes]
        if opposite:
            means = [y+e.half*(1 if e.pair == 0 else -1) for e, y in zip(episodes, means)]
        effect, se = statistic(episodes, means)
        coverage += abs(effect) <= 1.645*se
        for d in deltas:
            for s in scales:
                counts[d, s][verdict(effect if opposite else effect+d, se, s)] += 1
    print(f'\n{name}: episodes={len(episodes)}, clusters={len(clusters)}, rho={rho}, window_share={window_share}')
    print('drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]')
    for (d, s), (passed, failed, imprecise) in counts.items():
        print(f'{d:.2f} {s:.2f} | '+ ' '.join(wilson(k, repetitions) for k in
                                            (passed, failed, imprecise, repetitions-failed)))
    print(f'CI90 coverage of true pooled contrast: {wilson(coverage, repetitions)}%')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repetitions', type=int, default=20000)
    parser.add_argument('--seed', type=int, default=20261108)
    args = parser.parse_args()
    if args.repetitions < 100:
        parser.error('use at least 100 replicates')
    print(f'U6 synthetic OC sol2; Python {sys.version.split()[0]}; stdlib only; seed={args.seed}; N={args.repetitions}')
    print('s_r_true=1; drift=late-minus-early half contrast; scale=s_r_used/s_r_true')
    print('Wilson 95% pointwise Monte Carlo intervals; NO_FAIL=PASS+IMPRECISE (miss for adverse drift only)')
    oracle_check()
    designs = [
        ('D6_m42', [7]*6), ('D7_m49', [7]*7), ('D8_m56', [7]*8),
        ('eligible_floor_m39', [7, 6, 7, 6, 7, 6]),
    ]
    for name, counts in designs:
        simulate(name, roster(counts), rho=.5, scales=(.7, 1., 1.3),
                 repetitions=args.repetitions, seed=args.seed)
    for name, counts, turns, rho in [
        ('D6_rho0', [7]*6, 3, 0.), ('D6_rho09', [7]*6, 3, .9),
        ('D8_rho0', [7]*8, 3, 0.), ('D8_rho09', [7]*8, 3, .9),
        ('D6_one_turn', [7]*6, 1, .5), ('D6_six_turns', [7]*6, 6, .5),
        ('D6_mixed_lengths_1_3_6', [7]*6, 0, .5),
        ('D_single_window', [7], 3, .5),
    ]:
        simulate(name, roster(counts, turns=turns), rho=rho,
                 repetitions=args.repetitions, seed=args.seed)
    for seed_ids in (False, True):
        simulate('W1_D6_all_benign_'+('seed_ids' if seed_ids else 'episode_ids'),
                 roster([7]*6, sentinels=True, w1=True, seed_clusters=seed_ids), rho=.5,
                 repetitions=args.repetitions, seed=args.seed)
    simulate('D6_shared_window_stress', roster([7]*6), rho=.5, window_share=.2,
             repetitions=args.repetitions, seed=args.seed)
    simulate('D6_opposite_pair_drifts_plus_minus_1', roster([7]*6), rho=.5, opposite=True,
             repetitions=args.repetitions, seed=args.seed)
    # Prospective sizing demonstration; never an instruction to extend R12.
    simulate('PROPOSED_10_windows_m70', roster([7]*10), rho=.5,
             repetitions=args.repetitions, seed=args.seed)
    simulate('PROPOSED_29_windows_m203_worst_scale', roster([7]*29), rho=.9, scales=(.7,),
             repetitions=args.repetitions, seed=args.seed)
    print('\nNormal planning formula for 95% null PASS: m_per_pair >= ceil(2*v*((1.645+z.975)/(.5*scale))**2).')
    for rho, scale in ((.5, 1.), (.9, 1.), (.5, .7), (.9, .7)):
        v = rho+(1-rho)/3
        m = math.ceil(2*v*((1.645+NormalDist().inv_cdf(.975))/(.5*scale))**2)
        print(f'rho={rho}, scale={scale}: m>={m}/pair, round to {math.ceil(m/7)} intact default windows')


if __name__ == '__main__':
    main()
