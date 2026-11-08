#!/usr/bin/env python3
"""Attempt-level betting power simulation for the v5 ruling (revision 5).

Stdlib only. Synthetic laws only: no repository module, data file or
measurement is read. Reproduces the MDE table in RULING-DRAFT.md section 4e.

Model (per hypothesis Hk, per assigned attempt i, in sealed chronological order):
  delta_i = +1 (rescue)  with probability p_plus_w = (mu + r) * g_w, capped,
          = -1 (regression) with probability r,
          =  0 otherwise.
  g_w is a window-level multiplier (Gamma, mean 1) shared by all four streams in
  window w, giving within-window correlation; its shape is set so the
  intraclass correlation of the rescue indicator is about rho.
  A fraction miss of attempts has an unknown side outcome; the adverse bound
  turns a would-be +1 into 0 (a -1 stays -1).
Capital: K_0 = 1, K_i = K_{i-1} (1 + lam_i delta_i), lam_i predictable in [0, c].
Stake (aGRAPA-type): lam_i = clip(m_hat / s_hat, 0, c), with m_hat, s_hat the
  running mean and second moment of earlier deltas, shrunk toward a frozen
  development prior (n0 pseudo-observations at m0, s0).
p_k = min(1, 1/K_n) at the fixed horizon n. Holm at alpha = 0.05 over H1-H4.
H1-H3 use all attacks; H4 uses the phased subset (8 of 12 per window).
"""
import math
import random
import sys
from multiprocessing import Pool

ALPHA = 0.05
C_CAP = 0.5           # stake cap (keeps 1 + lam*delta >= 0.5)
N0, M0, S0 = 20, 0.05, 0.12   # frozen development prior for the stake
R_REG = 0.02          # regression probability
MISS = 0.02           # unknown side-outcome fraction (adverse bound)
REPS = 2000


def gamma_shape(pbar, rho):
    if rho <= 0:
        return None
    return pbar / (rho * (1.0 - pbar))


def run_stream(rng, n_per_window, windows, mu, r, gws):
    """Return final capital for one hypothesis stream."""
    logk = 0.0
    sum_d = 0.0
    sum_d2 = 0.0
    i = 0
    for w in range(windows):
        pplus = min(1.0 - r, (mu + r) * gws[w])
        for _ in range(n_per_window):
            m_hat = (sum_d + N0 * M0) / (i + N0)
            s_hat = (sum_d2 + N0 * S0) / (i + N0)
            lam = m_hat / s_hat if s_hat > 0 else 0.0
            lam = 0.0 if lam < 0 else (C_CAP if lam > C_CAP else lam)
            u = rng.random()
            if u < pplus:
                d = 1
            elif u < pplus + r:
                d = -1
            else:
                d = 0
            if d == 1 and rng.random() < MISS:
                d = 0
            if lam > 0 and d != 0:
                logk += math.log1p(lam * d)
            sum_d += d
            sum_d2 += d * d
            i += 1
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


def simulate(args):
    mus, rho, windows, h4_per_window, seed = args
    rng = random.Random(seed)
    pbar = max(mus) + R_REG
    shape = gamma_shape(pbar, rho)
    counts = [0, 0, 0, 0]
    bonf = [0, 0, 0, 0]
    conj13 = 0
    anyrej = 0
    for _ in range(REPS):
        gws = [1.0] * windows if shape is None else [
            rng.gammavariate(shape, 1.0 / shape) for _ in range(windows)]
        pv = []
        for k in range(4):
            npw = 12 if k < 3 else h4_per_window
            logk = run_stream(rng, npw, windows, mus[k], R_REG, gws)
            pv.append(min(1.0, math.exp(-logk)))
        rej = holm(pv)
        for k in range(4):
            counts[k] += rej[k]
            bonf[k] += pv[k] <= ALPHA / 4
        conj13 += rej[0] and rej[1] and rej[2]
        anyrej += any(rej)
    return (args, [c / REPS for c in counts], [b / REPS for b in bonf], conj13 / REPS, anyrej / REPS)


def main():
    global R_REG, MISS
    if len(sys.argv) > 1 and sys.argv[1] == "--stress":
        # stress: more regressions and missingness, strong window shocks
        R_REG, MISS = 0.05, 0.05
        jobs = []
        seed = 20261208
        for rho in (0.05, 0.30):
            for mu in (0.06, 0.08, 0.10, 0.12, 0.15):
                seed += 1
                jobs.append(((mu, mu, mu, mu), rho, 28, 8, seed))
        with Pool() as pool:
            res = pool.map(simulate, jobs)
        print("STRESS r=0.05 miss=0.05 | mu rho | Holm H1 H2 H3 H4 | conj")
        for (mus, rho, w, h, _), hp, bp, conj, _a in res:
            print(f"{mus[0]:.2f} {rho:.2f} | {hp[0]:.3f} {hp[1]:.3f} {hp[2]:.3f} {hp[3]:.3f} | {conj:.3f}")
        return
    grid = [0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12, 0.15]
    jobs = []
    seed = 20261108
    for rho in (0.0, 0.05, 0.15):
        for mu in grid:
            seed += 1
            jobs.append(((mu, mu, mu, mu), rho, 28, 8, seed))
    for windows in (36, 44):
        for mu in (0.06, 0.08, 0.10):
            seed += 1
            jobs.append(((mu, mu, mu, mu), 0.05, windows, 8, seed))
    for mu in (0.08, 0.10):  # reallocation: 10 H4 per window (2 cover-only)
        seed += 1
        jobs.append(((mu, mu, mu, mu), 0.05, 28, 10, seed))
    with Pool() as pool:
        res = pool.map(simulate, jobs)
    print("mu rho windows h4pw | Holm H1 H2 H3 H4 | alpha/4 H1 H4 | Holm H1-H3 conj")
    for (mus, rho, windows, h4pw, _), holm_p, bonf_p, conj, _any in res:
        print(f"{mus[0]:.2f} {rho:.2f} {windows:2d} {h4pw:2d} | "
              f"{holm_p[0]:.3f} {holm_p[1]:.3f} {holm_p[2]:.3f} {holm_p[3]:.3f} | "
              f"{bonf_p[0]:.3f} {bonf_p[3]:.3f} | {conj:.3f}")
    # size regression check under the conditional null: mu = 0, rho = 0
    # (rescue probability = regression probability in every window)
    null = simulate(((0.0, 0.0, 0.0, 0.0), 0.0, 28, 8, 99))
    print(f"NULL mu=0 rho=0 FWER (any Holm rejection): {null[4]:.4f} over {REPS} reps")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
