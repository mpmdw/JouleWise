"""Refuter sim for REV6 Q99_within. Pure python. Seed fixed."""
import math, random, statistics as st
from distributions import student_t_quantile as tq

random.seed(20260930)
R = 6000

def Phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def one(sizes, icc, phi=0.0, hetero=None):
    sw = 1.0
    sb = math.sqrt(icc / (1 - icc)) if icc > 0 else 0.0
    wins = []
    for j, m in enumerate(sizes):
        mu = random.gauss(0, sb)
        s = sw * (hetero[j] if hetero else 1.0)
        prev = random.gauss(0, s)
        xs = [mu + prev]
        for _ in range(m - 1):
            prev = phi * prev + math.sqrt(1 - phi * phi) * random.gauss(0, s)
            xs.append(mu + prev)
        wins.append(xs)
    allx = [x for w in wins for x in w]
    n, K = len(allx), len(wins)
    sd = st.stdev(allx)
    ssw = sum((x - st.mean(w)) ** 2 for w in wins for x in w)
    s_w = math.sqrt(ssw / (n - K))
    q = tq(0.995, n - 1) * sd * math.sqrt(2)
    qw = tq(0.995, n - K) * s_w * math.sqrt(2)
    return q, qw

def exceed(C, sig_pair):
    # prob a fresh within-window adjacent pair differs by more than C
    return 2 * (1 - Phi(C / sig_pair))

def row(label, sizes, icc, phi=0.0, hetero=None, claim_state=1.0):
    n, K = sum(sizes), len(sizes)
    bound = math.sqrt((n - 1) / (n - K)) * tq(0.995, n - K) / tq(0.995, n - 1)
    ratios, e5, e6, win = [], 0.0, 0.0, 0
    sig_pair = claim_state * math.sqrt(2 * (1 - phi))
    for _ in range(R):
        q, qw = one(sizes, icc, phi, hetero)
        ratios.append(qw / q)
        e5 += exceed(q, sig_pair)
        e6 += exceed(max(q, qw), sig_pair)
        win += qw > q
    ratios.sort()
    print(f"{label:34s} n={n:2d} K={K} bound={bound:.4f} maxratio={ratios[-1]:.4f} "
          f"p99ratio={ratios[int(.99*R)]:.4f} Qw_wins={win/R:5.1%} "
          f"exceed_rev5={e5/R:.4%} exceed_rev6={e6/R:.4%}")

for K in (2, 3):
    for n in (12, 18, 24, 30, 36):
        if n % K: continue
        sizes = [n // K] * K
        row("indep", sizes, 0.0)
        row("window ICC .3", sizes, 0.3)
        row("window ICC .6", sizes, 0.6)
row("indep unequal 10+2", [10, 2], 0.0)
row("indep unequal 9+2+1", [9, 2, 1], 0.0)
row("serial phi +.5", [12, 12], 0.0, phi=0.5)
row("serial phi -.5", [12, 12], 0.0, phi=-0.5)
row("serial phi -.3 K3", [8, 8, 8], 0.0, phi=-0.3)
row("hetero SD 1,1,2 claim in noisy", [8, 8, 8], 0.0, hetero=[1, 1, 2], claim_state=2.0)
row("hetero SD 1,1,2 claim in calm", [8, 8, 8], 0.0, hetero=[1, 1, 2], claim_state=1.0)
