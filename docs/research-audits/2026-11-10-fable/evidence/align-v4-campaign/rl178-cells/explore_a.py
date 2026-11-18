"""RL-178 research-lead exploration. Synthetic only. Reuses the analyst seat's rl177.py (pinned simulator) unchanged."""
import sys, json, math, random, time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, "/Volumes/JW-EXT/scratch/astra-rl177-cells/tmp")
import rl177 as R
sim, base, cell, gate = R.sim, R.base, R.cell, R.gate

# (name, drift, kappa, lengths, effect, reference)
SETTINGS = [
    ("R1o d2 counted",        .020, 0., (0., 0.), 0., False),
    ("R1p d2 reference",      .020, 0., (0., 0.), 0., True),
    ("R3b k+.2",              .016, .2, (0., 0.), 0., False),
    ("R3a k-.2",              .016, -.2, (0., 0.), 0., False),
    ("R4e d2 +30/+30",        .020, 0., (.3, .3), 0., False),
    ("R4e-ref d2 +30/+30 benign size", .020, 0., (.3, .3), 0., True),
    ("R5b eff .5%",           .016, 0., (0., 0.), .005, False),
    ("R1i d1.6 counted",      .016, 0., (0., 0.), 0., False),
    ("X k+.2 d2 +30/+30",     .020, .2, (.3, .3), 0., False),
    ("X2 d2 -30/-30",         .020, 0., (-.3, -.3), 0., False),
    ("R3b-ref k+.2 benign size", .016, .2, (0., 0.), 0., True),
    ("R4b d1.6 +30/+30",      .016, 0., (.3, .3), 0., False),
]
DESIGNS = {
    "d3":  lambda C, P, D: (1., D/1e3, ((C+P)*D + D*D/2)/1e7),
    "d4s": lambda C, P, D: (1., D/1e3, (C+P)*D/1e7, D*D/1e7),
    "d4p": lambda C, P, D: (1., D/1e3, ((C+P)*D + D*D/2)/1e7, P*D/1e7),
    "d5":  lambda C, P, D: (1., D/1e3, C*D/1e7, P*D/1e7, D*D/1e7),
    "d6":  lambda C, P, D: (1., D/1e3, C*D/1e7, P*D/1e7, D*D/1e7, (((C+P+D)/1e4)**3 - ((C+P)/1e4)**3)),
}
NAMES = ["pf"] + list(DESIGNS)
ALPHAS = (.025, .020, .0175, .015, .0125, .010)

def scores_for(members, f):
    rows = [[(f(c, p, d), y) for _, c, p, d, y in m] for m in members]
    k = len(f(0, 1, 1))
    out = []
    for j, held in enumerate(rows):
        tr = [r for i, rs in enumerate(rows) if i != j for r in rs]
        if not held or len(tr) < max(6, k+2):
            out.append(None); continue
        gram = [[sum(x[a]*x[b] for x, _ in tr) for b in range(k)] for a in range(k)]
        fac = sim.chol_n(gram)
        if fac is None:
            out.append(None); continue
        coef = sim.solve_n(fac, [sum(x[a]*y for x, y in tr) for a in range(k)])
        rss = sum((y - sum(v*b for v, b in zip(x, coef)))**2 for x, y in tr)
        if rss <= 0:
            out.append(None); continue
        s2 = rss/(len(tr)-k)
        sx = [sum(x[a] for x, _ in held) for a in range(k)]
        lev = sum(a*b for a, b in zip(sx, sim.solve_n(fac, sx)))
        var = s2*(len(held)+lev) + 3*len(held)*sim.CFG["edge_j"]**2
        out.append((sum(y for _, y in held) - sum(a*b for a, b in zip(sx, coef)))/math.sqrt(var))
    return out

def sim_member(cfg, draws, profile, inst):
    o = R.simulate(cfg, draws, profile, inst, None)
    cuts = o["cut"]
    return base.stats(cuts, None, sim.h2_rows(cfg, len(cuts))), o["decode_rows"]

def pvals(entered):
    ns, obs, th = [], 0, 0.
    for ss, bs in entered:
        n = len(bs)
        u2 = sum(2 if b < ss else 1 if b == ss else 0 for b in bs)
        ns.append(n); obs += u2*(420//n); th += u2/(2*n)
    ps, pi = base.tails(ns, obs)
    return ps, pi, th/len(entered)

def chunk(job):
    first, stop = job
    T = [[Counter() for _ in NAMES] for _ in SETTINGS]
    for rep in range(first, stop):
        rng = random.Random(gate.SEED*1000003 + rep)
        ent = [[[] for _ in NAMES] for _ in SETTINGS]
        for k in range(sim.N_STRATA):
            w, tid = divmod(k, 2)
            task = cell.TASKS[tid]
            slot = rng.randrange(sim.N_MEMBERS)
            draws = [sim.draw_member(rng) for _ in range(sim.N_MEMBERS)]
            small, large = gate.PAIRS[tid]
            ben = {}
            for si, (nm, drift, kappa, lengths, eff, ref) in enumerate(SETTINGS):
                cfg = dict(cell.CFG, drift=drift, hot=-.09, kappa=kappa, threshold=small/cell.CFG["r_p"], m=0., decode_effect=0.)
                key = (drift, kappa)
                if key not in ben:
                    ben[key] = [None if j == slot else sim_member(cfg, d, task+"_short", False) for j, d in enumerate(draws)]
                st = ben[key].copy()
                cfg.update(length=lengths[tid], decode_effect=eff)
                st[slot] = sim_member(cfg, draws[slot], task+("_short" if ref else "_long"), True)
                pfst = [s[0] for s in st]
                allsc = [base.loo_scores(pfst, [s[5] > 0 for s in pfst])]
                dec = [s[1] for s in st]
                allsc += [scores_for(dec, f) for f in DESIGNS.values()]
                for ni, sc in enumerate(allsc):
                    bs = [s for j, s in enumerate(sc) if j != slot and s is not None]
                    if sc[slot] is not None and bs:
                        ent[si][ni].append((sc[slot], bs))
        for si in range(len(SETTINGS)):
            for ni in range(len(NAMES)):
                e = ent[si][ni]
                t = T[si][ni]
                t["n"] += 1; t["strata"] += len(e)
                if e:
                    ps, pi, th = pvals(e)
                    t["theta"] += th
                    for a in ALPHAS:
                        t[f"up{a}"] += ps <= a
                        t[f"lo{a}"] += pi <= a
    return T

if __name__ == "__main__":
    n = int(sys.argv[1]); workers = int(sys.argv[2]); out = sys.argv[3]
    first = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    jobs = [(i, min(i+10, first+n)) for i in range(first, first+n, 10)]
    tot = [[Counter() for _ in NAMES] for _ in SETTINGS]
    t0 = time.monotonic()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for part in pool.map(chunk, jobs):
            for a, b in zip(tot, part):
                for x, y in zip(a, b):
                    x.update(y)
    res = {s[0]: {nm: dict(c) for nm, c in zip(NAMES, row)} for s, row in zip(SETTINGS, tot)}
    json.dump(dict(n=n, first=first, seed=gate.SEED, seconds=time.monotonic()-t0, res=res), open(out, "w"), indent=1)
    for s, row in res.items():
        print(s)
        for nm, c in row.items():
            N = c["n"]
            print(f"  {nm:4s} up " + " ".join(f"{c.get(f'up{a}',0)/N:.4f}" for a in ALPHAS) + "  lo " + " ".join(f"{c.get(f'lo{a}',0)/N:.4f}" for a in ALPHAS) + f"  th {c['theta']/N:.4f} K {c['strata']/N:.2f}")
