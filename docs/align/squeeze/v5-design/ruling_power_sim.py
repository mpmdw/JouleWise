#!/usr/bin/env python3
"""Attempt-level betting power simulation for the v5 ruling (revision 7).

Stdlib only. Synthetic laws only: no repository module, data file or
measurement is read. Reproduces the MDE and sizing tables in RULING-DRAFT.md
section 4e.

Revision 7 fix: every law parameter (regression rate r, missing rate miss,
replications) travels in the job dict, and each worker echoes the values it
actually used. Revision 5 mutated module globals in the parent and lost them
under macOS spawn, so its "stress" rows ran at r = miss = 0.02.
test_ruling_power_sim.py checks parameter transport under spawn.

Model (per hypothesis Hk, per assigned attempt i, in sealed chronological order):
  delta_i = +1 (rescue)     with probability p_plus_w = (mu + r) * g_w, capped,
          = -1 (regression) with probability r,
          =  0 otherwise.
  g_w is a window-level multiplier (Gamma, mean 1) shared by all four streams in
  window w; its shape is set so the rescue indicator's intraclass correlation
  is about rho (the cap at 1 - r clips the upper tail slightly).
  A fraction miss of attempts has an unknown side outcome; the adverse bound
  turns a would-be +1 into 0 (a -1 stays -1).
Capital: K_0 = 1, K_i = K_{i-1} (1 + lam_i delta_i), lam_i predictable in [0, c].
Stake (aGRAPA-type): lam_i = clip((N0*M0 + sum d) / (N0*S0 + sum d^2), 0, c).
p_k = min(1, 1/K_n) at the fixed horizon n. Holm at alpha = 0.05 over H1-H4.
H1-H3 use all attacks (12 per window); H4 uses h4pw per window. The four
streams are drawn independently given g_w (not literally coupled; see the
independent coupled simulators power_sim_sol{1,2}.py).
"""
import math
import random
import sys
from multiprocessing import get_context

ALPHA = 0.05
C_CAP = 0.5
N0, M0, S0 = 20, 0.05, 0.12

BASE = dict(r=0.02, miss=0.02)
STRESS = dict(r=0.05, miss=0.05)


def gamma_shape(pbar, rho):
    if rho <= 0:
        return None
    return pbar / (rho * (1.0 - pbar))


def run_stream(rng, n_per_window, windows, mu, r, miss, gws):
    logk = 0.0
    sum_d = 0.0
    sum_d2 = 0.0
    for w in range(windows):
        pplus = min(1.0 - r, (mu + r) * gws[w])
        for _ in range(n_per_window):
            lam = (sum_d + N0 * M0) / (sum_d2 + N0 * S0)
            lam = 0.0 if lam < 0 else (C_CAP if lam > C_CAP else lam)
            u = rng.random()
            if u < pplus:
                d = 1
            elif u < pplus + r:
                d = -1
            else:
                d = 0
            if d == 1 and rng.random() < miss:
                d = 0
            if lam > 0 and d != 0:
                logk += math.log1p(lam * d)
            sum_d += d
            sum_d2 += d * d
    return logk


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda k: pvals[k])
    rej = [False] * len(pvals)
    m = len(pvals)
    for j, k in enumerate(order):
        if pvals[k] <= ALPHA / (m - j):
            rej[k] = True
        else:
            break
    return rej


def simulate(job):
    """job = dict(mu, rho, windows, h4pw, r, miss, reps, seed)."""
    rng = random.Random(job["seed"])
    mu, rho, windows, h4pw = job["mu"], job["rho"], job["windows"], job["h4pw"]
    r, miss, reps = job["r"], job["miss"], job["reps"]
    shape = gamma_shape(mu + r, rho)
    holm_n = [0, 0, 0, 0]
    conj13 = 0
    anyrej = 0
    for _ in range(reps):
        gws = [1.0] * windows if shape is None else [
            rng.gammavariate(shape, 1.0 / shape) for _ in range(windows)]
        pv = []
        for k in range(4):
            npw = 12 if k < 3 else h4pw
            logk = run_stream(rng, npw, windows, mu, r, miss, gws)
            pv.append(min(1.0, math.exp(-logk)))
        rej = holm(pv)
        for k in range(4):
            holm_n[k] += rej[k]
        conj13 += rej[0] and rej[1] and rej[2]
        anyrej += any(rej)
    return {
        "job": job,
        "effective": {"r": r, "miss": miss, "reps": reps},  # echoed by the worker
        "holm": [c / reps for c in holm_n],
        "conj13": conj13 / reps,
        "any": anyrej / reps,
    }


def jobs_all(reps=2000):
    jobs = []
    seed = 20261108

    def add(mu, rho, windows, h4pw, law):
        nonlocal seed
        seed += 1
        jobs.append(dict(mu=mu, rho=rho, windows=windows, h4pw=h4pw,
                         reps=reps, seed=seed, **law))
    for rho in (0.0, 0.05, 0.15):                       # baseline law
        for mu in (0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12):
            add(mu, rho, 28, 8, BASE)
    for mu in (0.08, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16):   # stress law
        add(mu, 0.30, 28, 8, STRESS)
    for windows in (36, 44, 52, 60):                    # sizing under stress
        add(0.10, 0.30, windows, 8, STRESS)
    add(0.10, 0.30, 28, 10, STRESS)                     # H4 reallocation
    for windows in (28, 36, 44):                        # intermediate law
        add(0.10, 0.15, windows, 8, dict(r=0.035, miss=0.035))
    return jobs


def main():
    jobs = jobs_all()
    with get_context("spawn").Pool() as pool:
        res = pool.map(simulate, jobs)
    print("mu rho windows h4pw r miss | Holm H1 H2 H3 H4 | H1-H3 conj")
    for out in res:
        j, e = out["job"], out["effective"]
        assert (e["r"], e["miss"]) == (j["r"], j["miss"])
        h = out["holm"]
        print(f"{j['mu']:.2f} {j['rho']:.2f} {j['windows']:2d} {j['h4pw']:2d} "
              f"{e['r']:.3f} {e['miss']:.3f} | {h[0]:.3f} {h[1]:.3f} {h[2]:.3f} "
              f"{h[3]:.3f} | {out['conj13']:.3f}")
    null = simulate(dict(mu=0.0, rho=0.0, windows=28, h4pw=8, reps=2000,
                         seed=99, **BASE))
    print(f"NULL mu=0 rho=0 r=0.02 miss=0.02 FWER (any Holm rejection): "
          f"{null['any']:.4f} over 2000 reps")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
