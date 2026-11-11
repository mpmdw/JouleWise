#!/usr/bin/env python3
"""Synthetic planning power for agreement item 9; normal location model only."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random


def t95(df):
    # Integrate the Student t density by composite Simpson, then bisect its CDF.
    c = math.exp(math.lgamma((df+1)/2)-math.lgamma(df/2))/math.sqrt(df*math.pi)
    def cdf(x):
        n = 2048
        h = x/n
        density = lambda y: c*(1+y*y/df)**(-(df+1)/2)
        total = density(0)+density(x)
        total += sum((4 if i % 2 else 2)*density(i*h) for i in range(1, n))
        return .5 + h*total/3
    lo, hi = 0., 10.
    for _ in range(50):
        mid = (lo+hi)/2
        if cdf(mid) < .95:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def simulate(seed=20261110, replicates=100000):
    sizes = (22, 20, 16, 11, 6)
    quantiles = {k: t95((k+1)//2-1) for k in sizes}
    passed = dict.fromkeys(sizes, 0)
    lower = .5*math.erfc(.75/2)
    rng = random.Random(seed)
    for _ in range(replicates):
        ranks = []
        for _ in range(22):
            sabotage = rng.gauss(0, 1)
            ranks.append(sum(rng.gauss(0, 1) < sabotage for _ in range(7))/7)
        for k in sizes:
            w = (k+1)//2
            if w < 8:
                continue
            theta = math.fsum(ranks[:k])/k
            se0 = math.sqrt(k*9/84)/k
            errors = [sum(ranks[i:min(i+2, k)]) - min(2, k-i)*theta for i in range(0, k, 2)]
            sew = math.sqrt(w/(w-1)*math.fsum(e*e for e in errors))/k
            radius = max(1.6449*se0, quantiles[k]*sew)
            passed[k] += lower < theta-radius and theta+radius < 1-lower
    return dict(seed=seed, replicates=replicates, model='independent N(0,1) sabotage and seven benign scores per stratum',
                layout='first K_S strata of eleven two-pair windows; consecutive pairs share a window',
                t_quantile_method='Student t density: 2048-panel composite Simpson CDF, 50 bisections',
                equivalence_region=[lower, 1-lower], synthetic_only=True,
                results=[dict(K_S=k, W=(k+1)//2, equivalent=passed[k], power=passed[k]/replicates,
                              monte_carlo_se=math.sqrt(passed[k]/replicates*(1-passed[k]/replicates)/replicates),
                              t95=quantiles[k]) for k in sizes])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--replicates', type=int, default=100000)
    args = p.parse_args()
    result = simulate(replicates=args.replicates)
    result['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result['results']))


if __name__ == '__main__':
    main()
