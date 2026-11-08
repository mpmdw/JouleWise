#!/usr/bin/env python3
"""Bounded revision-7 review replays; stdlib and synthetic inputs only.

Run one mode at a time with Python 3.13 -I -B. No model or data access.
The author's sampler is used only by author mode. Coupled/gate modes use
the independent Sol1 sampler restored from the previous review branch.
"""
import argparse
import math
import random
import sys
import time
from multiprocessing import get_context
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import power_sim_sol1 as peer


def author(reps):
    import ruling_power_sim as lead
    jobs = lead.jobs_all(reps)
    # One child, not the author's unbounded default Pool.
    with get_context("spawn").Pool(1) as pool:
        results = pool.map(lead.simulate, jobs)
    print("AUTHOR mu rho windows h4pw r miss | H1 H2 H3 H4 | H123", flush=True)
    grid = {}
    for out in results:
        j = out["job"]
        assert out["effective"] == {k: j[k] for k in ("r", "miss", "reps")}
        values = (*out["holm"], out["conj13"])
        print(f"{j['mu']:.2f} {j['rho']:.2f} {j['windows']:2d} {j['h4pw']:2d} "
              f"{j['r']:.3f} {j['miss']:.3f} | "
              + " ".join(f"{p:.4f}" for p in values[:4])
              + f" | {values[4]:.4f}", flush=True)
        if j['windows'] == 28 and j['h4pw'] == 8:
            key = (j['r'], j['miss'], j['rho'])
            mde = grid.setdefault(key, [None] * 5)
            for h, p in enumerate(values):
                if p >= .8 and mde[h] is None:
                    mde[h] = j['mu']
    for key, mde in grid.items():
        print(f"AUTHOR_GRID_MDE r,miss,rho={key}: {mde}", flush=True)
    # Same inputs/output under spawn and sequential execution, including all
    # returned floating-point values; stress and baseline deliberately differ.
    stress = next(j for j in jobs if j['r'] == .05 and j['mu'] == .10)
    spawned = results[jobs.index(stress)]
    assert spawned == lead.simulate(stress)
    baseline = lead.simulate(dict(stress, r=.02, miss=.02))
    assert baseline['holm'] != spawned['holm']
    print("SPAWN sequential == spawned entire result; same-seed baseline != stress", flush=True)
    out = lead.simulate(dict(mu=0., rho=0., windows=28, h4pw=8,
                            reps=reps, seed=99, **lead.BASE))
    print(f"AUTHOR_NULL FWER={out['any']:.4f} reps={reps}", flush=True)


def row(seed, reps, effect, scenario, windows=28, h4pw=8):
    counts, means = peer.power_row(seed, reps, effect, scenario,
                                  peer.roster(windows, h4pw))
    print(f"{scenario.name} delta={effect:.2f} w={windows} h4pw={h4pw}: "
          + " ".join(peer.interval(c, reps) for c in counts)
          + " mean=" + ",".join(f"{m:.4f}" for m in means), flush=True)
    return counts


def coupled(reps):
    print("COUPLED columns H1 H2 H3 H4 H123 strong beyond honest; 95% Wilson MC", flush=True)
    effects = (.05, .06, .07, .08, .09, .10, .11, .12, .13, .14, .15)
    for index, scenario in enumerate(peer.SCENARIOS[:4]):
        mdes = [None] * 5
        for effect in effects:
            seed = 850137 + index * 1000000 + round(effect * 100000)
            hits = row(seed, reps, effect, scenario)
            for h in range(5):
                column = h if h < 4 else 4
                if mdes[h] is None and hits[column] / reps >= .8:
                    mdes[h] = effect
        print(f"COUPLED_GRID_MDE {scenario.name}: {mdes}", flush=True)


def ladder(reps):
    print("LADDER columns H1 H2 H3 H4 H123 strong beyond honest; 95% Wilson MC", flush=True)
    stress = peer.SCENARIOS[3]
    for windows, h4pw in ((28, 8), (28, 10), (36, 8), (44, 8), (52, 8), (60, 8)):
        # Same seed for the 28/8 row as the original independent review.
        row(850137 + 3000000 + 10000, reps, .10, stress, windows, h4pw)
    middle = peer.Scenario("coupled-intermediate", .15, .035, .035)
    for windows in (28, 36, 44):
        row(4850137, reps, .10, middle, windows)
    for scenario in peer.SCENARIOS[4:]:
        index = peer.SCENARIOS.index(scenario)
        row(850137 + index * 1000000 + 10000, reps, .10, scenario)


def binomial_tail(n, p, cutoff):
    return sum(math.comb(n, k) * p**k * (1-p)**(n-k)
               for k in range(cutoff + 1, n + 1))


def gates(reps):
    print("EXACT IID honest-member rates; arbitrary across-rule dependence bounded by union", flush=True)
    for cutoff in (14, 22):
        fail = binomial_tail(280, .05, cutoff)
        print(f"cutoff={cutoff} per_rule_false_fail={fail:.8f} "
              f"six_independent_fail={1-(1-fail)**6:.8f} "
              f"six_independent_pass={(1-fail)**6:.8f} "
              f"six_union_bound={min(1,6*fail):.8f}", flush=True)
    for p in (.05, .075, .08, .10, .125, .15):
        print(f"true_FPR={p:.3f} per_rule_gate_pass="
              f"{1-binomial_tail(280,p,22):.8f}", flush=True)
    width = math.sqrt(math.log(20) / (2*280))
    print(f"Hoeffding width={width:.8f} U(14/280)={14/280+width:.8f} "
          f"U(22/280)={22/280+width:.8f}", flush=True)
    rng = random.Random(7112026)
    failcounts = [0] * 6
    oldpass = newpass = 0
    # Fixed population cutoffs, every rule has exactly .05 marginal FPR.
    cutoffs = (peer.SOLO, peer.SOLO, peer.JOINT, peer.SOLO, peer.JOINT, peer.JOINT)
    for _ in range(reps):
        counts = [0] * 6
        for _ in range(280):
            scores = peer.rules(tuple(rng.random() for _ in range(4)))
            for h in range(6):
                counts[h] += scores[h] > cutoffs[h]
        for h in range(6):
            failcounts[h] += counts[h] > 22
        oldpass += max(counts) <= 14
        newpass += max(counts) <= 22
    print("COUPLED_NOMINAL per-rule false-fail="
          + " ".join(peer.interval(c, reps) for c in failcounts), flush=True)
    print(f"COUPLED_NOMINAL six_rule old_pass={peer.interval(oldpass,reps)} "
          f"new_pass={peer.interval(newpass,reps)}", flush=True)
    # An explicit allowed dependence stress: groups of five identical honest
    # outcomes, with each individual still marginally nominal .05.
    clustered_fail = binomial_tail(56, .05, 4)
    print(f"DATE_CONSTANT_5 nominal per-rule false_fail={clustered_fail:.8f} "
          f"six_independent_fail={1-(1-clustered_fail)**6:.8f}", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("author", "coupled", "ladder", "gates"))
    p.add_argument("--reps", type=int, default=2000)
    args = p.parse_args()
    if args.reps < 1:
        p.error("reps must be positive")
    start = time.monotonic()
    print(f"mode={args.mode} reps={args.reps}", flush=True)
    globals()[args.mode](args.reps)
    print(f"elapsed_s={time.monotonic()-start:.2f}", flush=True)


if __name__ == "__main__":
    main()
