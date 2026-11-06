#!/usr/bin/env python3
"""Print-only Monte Carlo operating characteristics for ALIGN v4 (ruling 6).

This module is deliberately independent of every registered analysis path.  It
simulates prospective operating characteristics; it never reads a run bundle.
"""
from __future__ import annotations

import argparse, json, math, random, statistics

SEED = 20261106
EXCLUSION_RATES = (0.05, 0.10, 0.14)
SIGMAS = (2.1, 3.0, 4.5)
DELTAS = (0.0, 6.0, 10.0, 15.0)
PAIR_SD = 2.97
# RUN_STATE main items 174--175, pilots 8--10 (spam, bank), copied by ruling.
S_R = (4.511563, 4.029927)

def binomial_tail(n: int, p: float, at_least: int) -> float:
    return sum(math.comb(n, k)*p**k*(1-p)**(n-k) for k in range(at_least,n+1))

def conformal_rank_coverage(n: int, alpha: float) -> float:
    """Finite-sample split-conformal coverage from its ceiling rank."""
    return min(1.0, math.ceil((n+1)*(1-alpha))/(n+1))

def verdict(delta_hat: float, half_width: float) -> str:
    lo, hi = delta_hat-half_width, delta_hat+half_width
    if lo >= 10.0: return "pass"
    if hi <= 6.0: return "fail"
    return "inconclusive"

def extension_prob(rate: float, stage: int, target: int) -> float:
    # Ruling 3: 20 initial pairs, add two after D3, D4 and D5, stopping at 26.
    n = 20 + 2*stage
    return binomial_tail(n, 1-rate, target)

def simulate(draws: int=100_000, seed: int=SEED) -> dict:
    rng=random.Random(seed)
    contrast={}
    for sigma in SIGMAS:
      for delta in DELTAS:
       for indicator in (False,True):
        counts=dict(pass_=0,inconclusive=0,fail=0)
        # eight observations; 4 df without, 3 df with the stage nuisance.
        se=sigma*math.sqrt(2/4); crit=2.132 if not indicator else 2.353
        for _ in range(draws):
            estimate=rng.gauss(delta,se)
            key=verdict(estimate,crit*se)
            counts["pass_" if key=="pass" else key]+=1
        contrast[f"delta={delta:g},sigma={sigma:g},stage={str(indicator).lower()}"]={
          "pass":counts["pass_"]/draws,"inconclusive":counts["inconclusive"]/draws,"fail":counts["fail"]/draws}
    # Criterion-level nominal null: bars are chosen so each false-fails at 2%.
    # U3 uses its ruled 3*max(pair SD, relative term); U5 uses 0.1*smaller s_r.
    criterion={f"U{i}":{"pass":.98,"inconclusive":0.0,"fail":.02} for i in range(1,7)}
    whole_fail=1-.98**6
    whole={"pass":.98**6,"inconclusive":0.0,"fail":whole_fail}
    ext={}
    for rate in EXCLUSION_RATES:
      ext[str(rate)]={f"D{stage+2}":{f"m>={t}":extension_prob(rate,stage,t) for t in (19,21)} for stage in (1,2,3)}
    # Chair §C ranges: n 19..26 and sigma 2.1..5 J; MDE is 10 J plus
    # the two-sided 90% margin for a balanced four-versus-four contrast.
    mdes=[]
    for _ in range(draws):
        n=rng.randint(19,26); sigma=rng.uniform(2.1,5.0)
        mdes.append(10+1.645*sigma*math.sqrt(2/n))
    mdes.sort()
    q=lambda p: mdes[min(len(mdes)-1,int(p*len(mdes)))]
    return {"schema":"joulewise.align_v4_oc.print_only.v1","seed":seed,"draws":draws,
      "inputs":{"pair_sd_j":PAIR_SD,"within_window_sigma_j":[2.1,5.0],"s_r_j":S_R,"exclusion_rates":EXCLUSION_RATES},
      "criteria":criterion,"series":whole,"extension":ext,"contrast":contrast,
      "proposed_bars":{"per_criterion_false_fail":.02,"series_false_fail":whole_fail,
       "U3_j":3*PAIR_SD,"U5_j":.1*min(S_R)},
      "mde_j":{"p05":q(.05),"median":q(.5),"p95":q(.95),"min":mdes[0],"max":mdes[-1]}}

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--draws",type=int,default=100_000); p.add_argument("--seed",type=int,default=SEED)
    a=p.parse_args(); print(json.dumps(simulate(a.draws,a.seed),sort_keys=True,indent=2))
if __name__ == "__main__": main()
