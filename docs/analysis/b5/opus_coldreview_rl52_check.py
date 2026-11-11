#!/usr/bin/env python3
"""Opus cold review of the RL-52 Block 5 ledger extension (rows 540-1420) and its
RL-55 delta (round 4, rows 1421-1845; CMP added to the pinned files).

Written independently of hand_check_phase2.py, hand_check_rl52.py and
hand_check_rl52_round2.py: standard library only, no repository analysis,
recompute, comparator or checker code. Formulas are taken from the registered
text (analysis plan 4, 5, 6, 8.1, 8.2; the disclosure producer's own
bound_formula line) and written here from scratch.

Data-free. It reads, read-only, six pinned custody files under the two RL-38
roots, hashes each before parsing and again at the end, and prints only counts,
words, row numbers and residuals at two significant figures. It writes nothing.

For every new ledger row it does two things:
  source  - resolves the row's key path in the named pinned file and compares
            the printed value with that leaf;
  hand    - where the quantity can be recomputed from member values or stored
            flags, compares the printed value with this script's own value.
Words: exact / within-rounding / MISMATCH. A row with no independent
computation is reported as source-only.

Usage: python3 -I -B docs/analysis/b5/opus_coldreview_rl52_check.py [--seed N] [--sample K]
Add --repo-only to check the frozen reviewed ledger and residual precision
without opening custody or rerunning source/recompute checks.
"""
import argparse
import csv
import hashlib
import itertools
import json
import math
import random
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = '/Users/edr/jw-b5-custody/'
A = 'dry-m/dry-run/restricted/'
FILES = {
    'RC': ('release-check-final-20261108T0942Z/recompute.json',
           'c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc'),
    'FILL': (A + 'outputs/a29c6cf296199d70d9154719608ad21c07e08fda077224aa05a914b5ecf1f9b4-results-fill-input.json',
             'a29c6cf296199d70d9154719608ad21c07e08fda077224aa05a914b5ecf1f9b4'),
    'DISC': (A + 'disclosures/77be1a3ed3a851206a0762334cbdeaab5b40e83e3d9fcdbcf404da5e4d871f6a.json',
             '77be1a3ed3a851206a0762334cbdeaab5b40e83e3d9fcdbcf404da5e4d871f6a'),
    'EXC': (A + 'finalized/analysed-attempt-exclusions-a9954365ef44c1b8a65603dd0ba52140109b45569fc795783ca6663d54586f46.json',
            'a9954365ef44c1b8a65603dd0ba52140109b45569fc795783ca6663d54586f46'),
    'PROJ-A': (A + 'outputs/ed3cadb1f0ac2fc137efab3f4528702c704055ffa5bdf24399c335081570f5bf-projection-alpha.json',
               'ed3cadb1f0ac2fc137efab3f4528702c704055ffa5bdf24399c335081570f5bf'),
    'PROJ-B': (A + 'outputs/db6d525129f90ef24bb46f83ab5e66283424970c743f35d322c8961f9b683e2e-projection-beta.json',
               'db6d525129f90ef24bb46f83ab5e66283424970c743f35d322c8961f9b683e2e'),
    # round 4 (RL-55) only; pinned in RESULTS.md 0
    'CMP': ('release-check-final-20261108T0942Z/comparison.json',
            'b12b7e1b32b27159be894221dcde7e334784061314fe91a39166faa36f72f4c9'),
}
LEDGER = Path(__file__).resolve().parent / 'rederivation.tsv'
REVIEWED_COMMIT = 'a1f916e9b2ef645e2768ff916a7ffafcacedccb4'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(alias):
    rel, pin = FILES[alias]
    p = Path(ROOT + rel)
    if p.is_symlink():
        sys.exit(f'{alias}: symlink refused')
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != pin:
        sys.exit(f'{alias}: hash differs from pin')
    return json.loads(raw)


# ---- Student t: own integer-df CDF (closed form) and bisection ------------
def t_cdf_upper2(t, nu):
    """P(|T| > t), integer nu, closed form (Abramowitz-Stegun 26.7.3/26.7.4)."""
    th = math.atan(abs(t) / math.sqrt(nu))
    s, c = math.sin(th), math.cos(th)
    if nu % 2 == 1:
        acc, term = 0.0, c
        for k in range(1, (nu - 1) // 2 + 1):
            if k > 1:
                term *= c * c * (2 * k - 2) / (2 * k - 1)
            acc += term
        a = (2 / math.pi) * (th + (s * acc if nu > 1 else 0.0))
    else:
        acc, term = 1.0, 1.0
        for k in range(1, nu // 2):
            term *= c * c * (2 * k - 1) / (2 * k)
            acc += term
        a = s * acc
    return 1 - a


def tq(nu):
    lo, hi = 0.5, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if t_cdf_upper2(mid, nu) > 0.05 else (lo, mid)
    return (lo + hi) / 2


T_EXACT = {n: tq(n) for n in range(1, 30)}
T_TABLE = {n: round(T_EXACT[n], 3) for n in T_EXACT}  # registered 3-place table


def mean(x):
    return math.fsum(x) / len(x)


def sd(x):
    m = mean(x)
    return math.sqrt(math.fsum((v - m) ** 2 for v in x) / (len(x) - 1))


def median(x):
    x = sorted(x); n = len(x)
    return x[n // 2] if n % 2 else (x[n // 2 - 1] + x[n // 2]) / 2


def pct(x, p):  # linear interpolation between order statistics
    x = sorted(x); h = (len(x) - 1) * p; lo = math.floor(h)
    return x[lo] + (h - lo) * (x[min(lo + 1, len(x) - 1)] - x[lo])


LOAD = {'thermal.os_level_nonzero', 'thermal.powermetrics_pressure_elevated', 'contention.request_overlap'}
MODELS = {'ALPHA': ('Qwen3-1.7B-4bit', 'd117fq31p7', 'qwen3-1p7b'), 'BETA': ('Qwen3-8B-4bit', 'd117fq38', 'qwen3-8b')}
PHASES = (('decode', 'decode', 'decode'), ('prefill', 'prefill-p2048', 'prefill'))  # key, stage, E_j field


def compute(src):
    rc, disc, exc = src['RC'], src['DISC'], src['EXC']
    V = {}  # semantic id -> value
    WM = rc['disclosures']['whole_machine']['windows']
    fam = {}
    for p in disc['window_lines'].values():
        for x in p:
            if x.get('label') == 'flag_count':
                fam[x['code']] = x['family']

    # ---- member exclusions (stored flags) -> unit codes, kept units ----------
    mcodes = {}
    for w in ('ALPHA', 'BETA'):
        for m in rc['exclusions_rederivation'][w]['rederived']['members_excluded']:
            mcodes[(w, m['run_id'])] = set(m['codes'])
    for m in exc['members_excluded']:
        mcodes[('GAMMA', m['run_id'])] = set(m['codes'])
        V[f'EXC.member.{m["run_id"]}.codes'] = sorted(m['codes'])
        V[f'EXC.member.{m["run_id"]}.families'] = sorted({fam[c] for c in m['codes']})

    def units(w, pre, stage):
        reps = [f'{pre}-df-ph-{stage}-abs-r{i:02d}' for i in range(1, 11)]
        quads = {f'b{i:02d}': [f'{pre}-df-cmp-abba-ph-{stage}-b{i:02d}-{r}' for r in ('a1', 'a2', 'b1', 'b2')]
                 for i in range(1, 11)}
        return reps, quads

    def strat(M, reps, quads, f, tt):
        r = [f(M[i]) for i in reps]; b = [mean([f(M[i]) for i in q]) for q in quads]
        m = 0.2 * mean(r) + 0.8 * mean(b)
        h = tt(min(len(r), len(b)) - 1) * math.sqrt(0.04 * sd(r) ** 2 / len(r) + 0.64 * sd(b) ** 2 / len(b))
        return m, h

    cellinfo = {}
    for w, (model, pre, short) in MODELS.items():
        M = rc['members'][w]; allow = rc['windows'][w]['neg8']['allowance_j']
        for phk, stage, ph in PHASES:
            cell = f'df-ph-{stage}-{short}'
            reps, quads = units(w, pre, stage)
            ucodes = {}
            for rid in reps:
                c = mcodes.get((w, rid), set())
                if c:
                    ucodes[rid] = c
            for b, q in quads.items():
                c = set().union(*[mcodes.get((w, i), set()) for i in q])
                if c:
                    ucodes[f'd117-df-cmp-abba-ph-{stage}-{short}-{b}'] = c
            kr = [r for r in reps if r not in ucodes]
            kq = [q for b, q in quads.items() if f'd117-df-cmp-abba-ph-{stage}-{short}-{b}' not in ucodes]
            stored = rc['reported_cells'][cell]['kept_units']
            V[f'chk.{cell}.kept_units_match_stored'] = (kr == stored['repeat'] and
                                                         [q[0][-6:-3] for q in kq] == [u[-3:] for u in stored['quad']])
            # reported cell
            m, h = strat(M, kr, kq, lambda x: x['E_j'][ph], lambda n: T_EXACT[n])
            k0 = 0.2 * mean([M[i]['a_bop_j'][ph] for i in kr]) + 0.8 * mean([M[i]['a_bop_j'][ph] for q in kq for i in q])
            kinds = [k0, 0.0, allow / 2]
            B = math.fsum(kinds)
            kept_ids = kr + [i for q in kq for i in q]
            af = max(kept_ids, key=lambda i: M[i]['a_bop_j'][ph])
            V.update({f'{cell}.mean': m, f'{cell}.h': h, f'{cell}.B': B, f'{cell}.lower': m - h - B,
                      f'{cell}.upper': m + h + B, f'{cell}.n_r': len(kr), f'{cell}.n_b': len(kq),
                      f'{cell}.kind0': kinds[0], f'{cell}.kind1': kinds[1], f'{cell}.kind2': kinds[2],
                      f'{cell}.af_by': af, f'{cell}.af_min': min(M[i]['a_bop_j'][ph] for i in kept_ids),
                      f'{cell}.removed_count': len(ucodes),
                      f'{cell}.load_trigger_count': sum(1 for c in ucodes.values() if c & LOAD)})
            for u, c in ucodes.items():
                V[f'{cell}.unit.{u}.codes'] = sorted(c)
                V[f'{cell}.unit.{u}.families'] = sorted({fam[x] for x in c})
            # battery-assist "without" line: assist counts are recorded (0), so no unit leaves
            V.update({f'{cell}.without.{k}': V[f'{cell}.{k}'] for k in ('mean', 'h', 'B', 'lower', 'upper')})
            # load-correlated line: restore units whose every code is load-correlated
            rest = {u for u, c in ucodes.items() if c <= LOAD}
            if any(c & LOAD for c in ucodes.values()):
                lr = [r for r in reps if r not in ucodes or r in rest]
                lq = [q for b, q in quads.items() if f'd117-df-cmp-abba-ph-{stage}-{short}-{b}' not in ucodes
                      or f'd117-df-cmp-abba-ph-{stage}-{short}-{b}' in rest]
                lm, lh = strat(M, lr, lq, lambda x: x['E_j'][ph], lambda n: T_EXACT[n])
                lk = 0.2 * mean([M[i]['a_bop_j'][ph] for i in lr]) + 0.8 * mean([M[i]['a_bop_j'][ph] for q in lq for i in q])
                lB = math.fsum([lk, 0.0, allow / 2])
                V.update({f'{cell}.load.mean': lm, f'{cell}.load.h': lh, f'{cell}.load.B': lB,
                          f'{cell}.load.lower': lm - lh - lB, f'{cell}.load.upper': lm + lh + lB,
                          f'{cell}.load.n_r': len(lr), f'{cell}.load.n_b': len(lq),
                          f'{cell}.load.restored': len(rest),
                          f'{cell}.load.restored_repeat': sum(1 for u in rest if '-abs-' in u),
                          f'{cell}.load.restored_quad': sum(1 for u in rest if '-abs-' not in u)})
            V[f'{cell}.load.present'] = int(any(c & LOAD for c in ucodes.values()))
            cellinfo[cell] = (w, model, phk, stage, ph, kr, kq)

    # ---- floors, dominance (analysis plan 5 and 6) --------------------------
    guard = lambda n: 1.0 if n >= 10 else math.sqrt(9 / (n - 1))

    def pf_abs(v):
        n = len(v); mu = mean(v); dev = [x - mu for x in v]
        return max(max(abs(x) for x in dev), T_TABLE[n - 1] * sd(dev) * math.sqrt(1 + 1 / n))

    def pf_cmp(v):
        n = len(v)
        return max(max(abs(x) for x in v), abs(mean(v)) + T_TABLE[n - 1] * sd(v) * math.sqrt(1 + 1 / n))

    def corner(v, wid, pf):
        return max(pf([x + s * ww for x, s, ww in zip(v, sg, wid)])
                   for sg in itertools.product((-1, 1), repeat=len(v)))

    failed_cm = 0; all_pass = True
    for w, (model, pre, short) in MODELS.items():
        M = rc['members'][w]; allow = rc['windows'][w]['neg8']['allowance_j']
        for phk, stage, ph in PHASES:
            cell = f'df-ph-{stage}-{short}'
            _, _, _, _, _, kr, kq = cellinfo[cell]
            # absolute form over the kept repeats; widths from member a_bop_j
            fa = rc['floors'][f'{model}/{phk}/absolute']
            V[f'chk.{model}/{phk}.abs_units_match'] = fa['kept_units'] == kr
            v = [M[i]['E_j'][ph] for i in kr]; wd = [M[i]['a_bop_j'][ph] for i in kr]
            pt = pf_abs(v); cw = max(pt, corner(v, wd, pf_abs))
            key = f'{model}/{phk}/absolute'
            V.update({f'{key}.num': cw, f'{key}.den': pt, f'{key}.n': len(v), f'{key}.R': cw / pt,
                      f'{key}.pass': cw / pt >= 2})
            all_pass &= cw / pt >= 2
            # comparative form over the kept quads; local from member r_j, shared = pinned trace-sweep input
            fc = rc['floors'][f'{model}/{phk}/comparative']
            V[f'chk.{model}/{phk}.cmp_units_match'] = [u[-3:] for u in fc['kept_units']] == [q[0][-6:-3] for q in kq]
            d = [(M[q[2]]['E_j'][ph] + M[q[3]]['E_j'][ph] - M[q[0]]['E_j'][ph] - M[q[1]]['E_j'][ph]) / 2 for q in kq]
            loc = [math.fsum(M[i]['r_j'][ph] for i in q) / 2 for q in kq]
            sh = fc['shared_j']
            pt = pf_cmp(d); cw = max(pt, corner(d, [a + b for a, b in zip(sh, loc)], pf_cmp))
            key = f'{model}/{phk}/comparative'
            V.update({f'{key}.num': cw, f'{key}.den': pt, f'{key}.n': len(d), f'{key}.R': cw / pt,
                      f'{key}.pass': cw / pt >= 2,
                      f'{key}.minted': guard(len(d)) * cw + allow})
            all_pass &= cw / pt >= 2
            num = max(pf_cmp([x + S * s_ + e * l for x, s_, e, l in zip(d, sh, sg, loc)])
                      for S in (-1, 1) for sg in itertools.product((-1, 1), repeat=len(d)))
            V.update({f'{model}/{phk}.cm.num': num, f'{model}/{phk}.cm.den': pt, f'{model}/{phk}.cm.n': len(d),
                      f'{model}/{phk}.cm.R': num / pt, f'{model}/{phk}.cm.pass': num / pt >= 2})
            failed_cm += num / pt < 2
    V['dom.failed_R'] = sum(1 for k, x in list(V.items()) if re.search(r'/(absolute|comparative)\.pass$', k) and not x)
    V['dom.failed_cm'] = failed_cm
    V['dom.branch'] = 'A' if all_pass and failed_cm == 0 else 'B'
    V['dom.sentence_licensed'] = V['dom.branch'] == 'A'

    # ---- cross-window rule (analysis plan 8.1) ------------------------------
    G = rc['members']['GAMMA']
    for w, (model, pre, short) in MODELS.items():
        for phk, stage, ph in PHASES:
            cid = f'ctr-d117-{stage}-qwen3-1p7b-vs-qwen3-8b'
            arms = ('a1', 'a2') if w == 'ALPHA' else ('b1', 'b2')
            kept = [q[-3:] for q in rc['contrasts'][cid]['kept_quads']]
            side = [mean([G[f'd117c-qwen3-1p7b-vs-qwen3-8b-v5-{stage}-contrast-{b}-{a}']['E_j'][ph] for a in arms])
                    for b in kept]
            n = len(side); g = mean(side); hg = T_EXACT[n - 1] * sd(side) / math.sqrt(n)
            cell = f'df-ph-{stage}-{short}'
            dlt = g - V[f'{cell}.mean']; hf = V[f'{cell}.h']
            agree = abs(dlt) <= math.hypot(hg, hf)
            V.update({f'xw.{model}/{phk}.delta': dlt, f'xw.{model}/{phk}.hG': hg, f'xw.{model}/{phk}.hF': hf,
                      f'xw.{model}/{phk}.agree': agree, f'xw.{model}/{phk}.word': 'agree' if agree else 'differ'})

    # ---- contrast removal codes (EXC, union of member codes) ----------------
    for cid in ('ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b', 'ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b'):
        stage = 'decode' if 'decode' in cid else 'prefill-p2048'
        for i in range(1, 11):
            ids = [f'd117c-qwen3-1p7b-vs-qwen3-8b-v5-{stage}-contrast-b{i:02d}-{r}' for r in ('a1', 'a2', 'b1', 'b2')]
            c = set().union(*[mcodes.get(('GAMMA', x), set()) for x in ids])
            if c:
                u = f'd117-{stage}-contrast-b{i:02d}'
                V[f'ctr.{u}.codes'] = sorted(c); V[f'ctr.{u}.families'] = sorted({fam[x] for x in c})

    # ---- whole-machine request share rho (analysis plan 8.2) ----------------
    names = {'qwen3-1p7b': 'Qwen3-1.7B-4bit', 'qwen3-8b': 'Qwen3-8B-4bit'}
    for w in ('ALPHA', 'BETA', 'GAMMA'):
        by = {}
        for v in WM[w]['members'].values():
            r = v['phases']['request']
            dm = r['meter']['delta_J'] + r['battery']['delta_J']; rho = r['rail_delta_J'] / dm
            ok = 0 < rho <= 1 and dm - r['rail_delta_J'] >= 0
            by.setdefault(v['model'], []).append((rho, ok))
        for model, xs in by.items():
            x = [a for a, _ in xs]; good = [a for a, ok in xs if ok]
            sp = (max(good) - min(good)) / median(good)
            V.update({f'rho.{w}.{model}.median': median(x), f'rho.{w}.{model}.min': min(x),
                      f'rho.{w}.{model}.max': max(x), f'rho.{w}.{model}.q25': pct(x, 0.25),
                      f'rho.{w}.{model}.q75': pct(x, 0.75), f'rho.{w}.{model}.spread': sp,
                      f'rho.{w}.{model}.n': len(x), f'rho.{w}.{model}.out': len(x) - len(good),
                      f'rho.{w}.{model}.consistency': 'consistent' if sp <= 0.2 else 'not consistent'})

    # ---- NEG-8: both families, counts, corpus (registration 5.3; DISC bound_formula) ----
    for w in ('ALPHA', 'BETA'):
        M = rc['members'][w]; n8 = rc['windows'][w]['neg8']; Wm = WM[w]['members']
        surv = n8['survivor_ids']
        slots = {'start': [i for i in surv if '-start-' in i], 'midpoint': [i for i in surv if 'midpoint' in i],
                 'end': [i for i in surv if '-end-' in i]}
        planned = {'start': 3, 'midpoint': 1, 'end': 3}
        corpus_all = sorted(i for i in M if 'refcorpus' in i)
        status = [i for i in corpus_all if mcodes.get((w, i), set()) & {'member.admission_aborted', 'member.strict_validation_failed'}]
        inwin = [i for i in corpus_all if i not in status]
        phys = [i for i in inwin if any(fam.get(c) == 'PHYSICS_IN_SPAN' for c in mcodes.get((w, i), set()))]
        clean = [i for i in inwin if i not in phys]
        deciding, cap = clean[:12], clean[12:]
        V.update({f'n8.{w}.corpus_n': len(deciding), f'n8.{w}.corpus_match': deciding == n8['corpus_ids'],
                  f'n8.{w}.collected': len(corpus_all), f'n8.{w}.in_window': len(inwin), f'n8.{w}.deciding': len(deciding),
                  f'n8.{w}.desk_cap': cap, f'n8.{w}.drop.desk_cap': len(cap), f'n8.{w}.drop.status': len(status),
                  f'n8.{w}.drop.contention': sum('contention.request_overlap' in mcodes.get((w, i), set()) for i in phys),
                  f'n8.{w}.deciding_references': len(surv), f'n8.{w}.deciding_spares': 0})
        lost = [i for i in (f'neg8-window-{s}-r{k}' for s in ('start', 'end') for k in (1, 2, 3)) if i not in surv]
        V[f'n8.{w}.lost'] = lost
        for s in slots:
            V[f'n8.{w}.counts.{s}'] = len(slots[s]); V[f'n8.{w}.planned.{s}'] = planned[s]
        V[f'n8.{w}.midpoint_lost'] = len(slots['midpoint']) == 0
        for famname, f in (('gross_energy', lambda i: M[i]['E_j']['request']),
                           ('idle_subtracted_energy', lambda i: Wm[i]['phases']['request']['rail_delta_J'])):
            c = sorted(f(i) for i in deciding)
            ns, ne = len(slots['start']), len(slots['end'])
            env = max(mean(c[-ns:]) - mean(c[:ne]), mean(c[-ne:]) - mean(c[:ns]))
            pred = T_TABLE[len(c) - 1] * sd(c) * math.sqrt(1 / ns + 1 / ne)
            bound = max(env, pred)
            st, en, mid = mean([f(i) for i in slots['start']]), mean([f(i) for i in slots['end']]), mean([f(i) for i in slots['midpoint']])
            stat = abs(en - st)
            exc_ = max(abs(en - st), abs(mid - st), abs(mid - en))
            V.update({f'n8.{w}.{famname}.env': env, f'n8.{w}.{famname}.pred': pred, f'n8.{w}.{famname}.bound': bound,
                      f'n8.{w}.{famname}.stat': stat, f'n8.{w}.{famname}.excursion': exc_,
                      f'n8.{w}.{famname}.allowance': max(bound, exc_),
                      f'n8.{w}.{famname}.screen': 'passed' if stat <= bound else 'failed'})
        V[f'n8.{w}.screen'] = 'passed' if all(V[f'n8.{w}.{x}.screen'] == 'passed'
                                              for x in ('gross_energy', 'idle_subtracted_energy')) else 'failed'
        # physics-in-span counts over stored member codes
        pc = Counter(c for (ww, _), cs in mcodes.items() if ww == w for c in cs if fam.get(c) == 'PHYSICS_IN_SPAN')
        for c, k in pc.items():
            V[f'phys.{w}.{c}'] = k

    # ---- stage battery temperature (analysis plan 8.1) from stored readings --
    for p in ('alpha', 'beta'):
        for i, x in enumerate(disc['window_lines'][p]):
            if x.get('label') != 'battery_temperature':
                continue
            r = x['readings_centi_c']
            rise = (r[-1] - r[0]) / 100 if len(r) >= 2 else None
            plat = len(r) >= 3 and max(r[-3:]) - min(r[-3:]) <= 50
            V.update({f'temp.{p}.{i}.rise': None if rise is None else round(rise, 2), f'temp.{p}.{i}.plateau': plat,
                      f'temp.{p}.{i}.producer': rise is not None and rise > 3 and not plat,
                      f'temp.{p}.{i}.unmeasured': len(r) == 0})
            V[f'temp.{p}.{i}.differs'] = V[f'temp.{p}.{i}.producer'] != x['harvest_flag']

    # ---- attempt history counts and causes over stored attempt lines --------
    bl = disc['block_lines']
    an = {WM[w]['identifier']: w for w in WM}
    for i, x in enumerate(bl):
        if x.get('label') != 'attempt_count':
            continue
        hist = []
        for y in bl[i + 1:]:
            if y.get('label') == 'attempt_count' or y.get('label') == 'superseded_history':
                break
            if y.get('label') == 'attempt_history':
                hist.append(y)
        V[f'att.{i}.count'] = len(hist)
        for j, y in enumerate(bl):  # analysed attempts: recount succeeded / planned from member records
            if y in hist and y.get('plan_id') in an:
                w = an[y['plan_id']]
                V[f'att.{j}.collected'] = len(WM[w]['members']); V[f'att.{j}.planned'] = len(rc['members'][w])
        V[f'att.{i}.causes'] = sorted(set('None' if h['cause_key'] is None else h['cause_key'] for h in hist))
        for c, k in Counter('None' if h['cause_key'] is None else h['cause_key'] for h in hist).items():
            V[f'att.{i}.cause.{c}'] = k
    return V


# ---- round 4 (RL-55): rows 1421-1845 -----------------------------------
def round4(src, V):
    """Independent values for the round-4 rows, keyed by the exact ledger key."""
    rc, disc, exc, cmp_ = src['RC'], src['DISC'], src['EXC'], src['CMP']
    W = {}
    WM = rc['disclosures']['whole_machine']['windows']
    pk = {'alpha': 'ALPHA', 'beta': 'BETA', 'gamma': 'GAMMA'}
    fam = {x['code']: x['family'] for p in disc['window_lines'].values() for x in p if x.get('label') == 'flag_count'}
    rec = {'ALPHA': rc['exclusions_rederivation']['ALPHA']['rederived'],
           'BETA': rc['exclusions_rederivation']['BETA']['rederived'], 'GAMMA': exc}
    mc = {w: {m['run_id']: set(m['codes']) for m in r['members_excluded']} for w, r in rec.items()}
    for p, w in pk.items():
        by = rec[w]['flag_counts']['by_code']  # a second stored record, not the DISC line
        for c in ('battery.assist', 'battery.assist_outside_request', 'battery.capture_pair_assist',
                  'battery.smc_unavailable', 'calibration.capture_battery_assist',
                  'calibration.capture_battery_pair_assist'):
            W[f'DISC.window_lines.{p}[label=battery_counts].counts.{c}'] = by.get(c, 0)
        W[f'DERIVE(DISC.window_lines.{p}).arm_unmeasured_count'] = sum(
            v for c, v in by.items() if c.endswith('.arm_unmeasured'))
    # GAMMA physics counts, references, corpus, NEG-8 (same rules as rounds 1-2)
    pc = Counter(c for cs in mc['GAMMA'].values() for c in cs if fam.get(c) == 'PHYSICS_IN_SPAN')
    for i, x in enumerate(disc['window_lines']['gamma']):
        if x.get('label') == 'physics_counts':
            for c in x['counts']:
                W[f'DISC.window_lines.gamma[{i}].counts.{c}'] = pc.get(c, 0)
    M = rc['members']['GAMMA']; n8 = rc['windows']['GAMMA']['neg8']; Wm = WM['GAMMA']['members']
    surv = n8['survivor_ids']
    planned = {'start': [f'neg8-window-start-r{k}' for k in (1, 2, 3)], 'midpoint': ['neg8-window-midpoint'],
               'end': [f'neg8-window-end-r{k}' for k in (1, 2, 3)]}
    slots = {s_: [i for i in ids if i in surv] for s_, ids in planned.items()}
    g = 'DISC.window_lines.gamma'
    for s_ in planned:
        W[f'{g}[label=reference_counts].counts.{s_}'] = len(slots[s_])
        W[f'{g}[label=reference_counts].planned.{s_}'] = len(planned[s_])
    lost = [(s_, i) for s_, ids in planned.items() for i in ids if i not in surv]
    for s_, i in lost:
        W[f'{g}[label=reference_lost,run_id={i}].run_id'] = i
        W[f'{g}[label=reference_lost,run_id={i}].slot'] = s_
        W[f'{g}[label=reference_lost,run_id={i}].reason'] = sorted(mc['GAMMA'].get(i, set()))
    W[f'count({g}[label=reference_lost])'] = len(lost)
    W[f'count({g}[label=reference_spare])'] = 0
    W[f'DERIVE({g}[label=reference_counts]).midpoint_lost'] = not slots['midpoint']
    W[f'{g}[label=deciding_membership].deciding_references'] = len(surv)
    W[f'{g}[label=deciding_membership].deciding_spares'] = 0
    corpus = sorted(i for i in M if 'refcorpus' in i)
    status = [i for i in corpus if mc['GAMMA'].get(i, set()) & {'member.admission_aborted', 'member.strict_validation_failed'}]
    inwin = [i for i in corpus if i not in status]
    phys = [i for i in inwin if any(fam.get(c) == 'PHYSICS_IN_SPAN' for c in mc['GAMMA'].get(i, set()))]
    clean = [i for i in inwin if i not in phys]
    W.update({f'{g}[label=corpus_counts].collected': len(corpus), f'{g}[label=corpus_counts].in_window': len(inwin),
              f'{g}[label=corpus_counts].deciding': len(clean[:12]), f'{g}[label=corpus_counts].desk_cap': clean[12:],
              f'{g}[label=corpus_counts].drop_counts.desk_cap': len(clean[12:]),
              f'{g}[label=corpus_counts].drop_counts.status': len(status),
              f'{g}[label=corpus_counts].drop_counts.contention.request_overlap':
                  sum('contention.request_overlap' in mc['GAMMA'][i] for i in phys)})
    for i in phys:
        W[f'{g}[label=corpus_physics_drop,run_id={i}].codes'] = sorted(mc['GAMMA'][i])
    W['chk.gamma.corpus_ids'] = clean[:12] == n8['corpus_ids']
    for fm, f in (('gross_energy', lambda i: M[i]['E_j']['request']),
                  ('idle_subtracted_energy', lambda i: Wm[i]['phases']['request']['rail_delta_J'])):
        c = sorted(f(i) for i in clean[:12]); ns, ne = len(slots['start']), len(slots['end'])
        env = max(mean(c[-ns:]) - mean(c[:ne]), mean(c[-ne:]) - mean(c[:ns]))
        pred = T_TABLE[len(c) - 1] * sd(c) * math.sqrt(1 / ns + 1 / ne); bound = max(env, pred)
        st, en, mid = (mean([f(i) for i in slots[k]]) for k in ('start', 'end', 'midpoint'))
        stat = abs(en - st); exc_ = max(abs(en - st), abs(mid - st), abs(mid - en))
        b = f'{g}[label=neg8_allowance].values_j[bracket.claim_families.{fm}.'
        W.update({b + 'bound_envelope_j]': env, b + 'bound_prediction_j]': pred,
                  b + 'derived_repeatability_bound_j]': bound, b + 'screen_statistic_j]': stat,
                  b + 'trajectory_excursion_max_j]': exc_, b + 'drift_allowance_j]': max(bound, exc_),
                  f'DERIVE({g}[label=neg8_allowance].values_j.bracket.claim_families.{fm}).screen_decision':
                      'passed' if stat <= bound else 'failed'})
    W[f'{g}[label=neg8_screen].decision'] = 'passed' if all(
        W[f'DERIVE({g}[label=neg8_allowance].values_j.bracket.claim_families.{fm}).screen_decision'] == 'passed'
        for fm in ('gross_energy', 'idle_subtracted_energy')) else 'failed'
    W['chk.gamma.allowance_equals_RC'] = abs(W[f'{g}[label=neg8_allowance].values_j[bracket.claim_families.gross_energy.drift_allowance_j]'] - n8['allowance_j']) < 1e-9
    # GAMMA stage temperatures from stored readings
    for i, x in enumerate(disc['window_lines']['gamma']):
        if x.get('label') == 'battery_temperature':
            r = x['readings_centi_c']; rise = (r[-1] - r[0]) / 100 if len(r) >= 2 else None
            plat = len(r) >= 3 and max(r[-3:]) - min(r[-3:]) <= 50
            prod = rise is not None and rise > 3 and not plat
            W.update({f'{g}[{i}].rise_k': None if rise is None else round(rise, 2), f'{g}[{i}].plateau': plat,
                      f'{g}[{i}].producer_flag': prod, f'{g}[{i}].temperature_unmeasured': len(r) == 0,
                      f'{g}[{i}].differs_from_harvest_flag': prod != x['harvest_flag']})
    # GAMMA attempt line (rows 9-10): count, causes, and recounted collected / planned
    W['DISC.block_lines[9].count'] = V['att.9.count']; W['DISC.block_lines[9].causes'] = V['att.9.causes']
    W['DISC.block_lines[9].cause_counts[cause=None]'] = V.get('att.9.cause.None', 0)
    W['DISC.block_lines[10].collected'] = len(WM['GAMMA']['members']); W['DISC.block_lines[10].planned'] = len(M)
    # removed-unit structure: positions and stratum from the stored exclusion records (RC rederived, EXC)
    for w, r in rec.items():
        for cell in r['cells']:
            for u in cell['dropped_units']:
                cid = cell['cell_id']
                if w == 'GAMMA':
                    base = f'DISC.contrasts[label=removed unit,cell_id={cid},unit_id={u["unit_id"]}]'
                else:
                    base = f'DISC.cells[label=removed unit,cell_id=d117-reported-mean-{cid[3:]},unit_id={u["unit_id"]}]'
                W[base + '.positions'] = [str(x) for x in u['positions']]
                W[base + '.stratum'] = u['stratum']; W[base + '.unit_id'] = u['unit_id']
    # comparator summary from the comparison rows themselves
    fams = sorted(cmp_['counts'])
    for f in fams:
        rows_ = [x for x in cmp_['comparisons'] if x['family'] == f]
        d = f'DERIVE(CMP.comparisons[family={f}])'
        W[d + '.compared'] = len(rows_)
        W[d + '.agreement_word'] = ('not-compared' if not rows_ else
                                    'AGREE' if all(x['verdict'] == 'AGREE' for x in rows_) else 'DISAGREE')
        num = [abs(x['l9'] - x['recompute']) for x in rows_
               if isinstance(x.get('l9'), (int, float)) and isinstance(x.get('recompute'), (int, float))
               and not isinstance(x.get('l9'), bool)]
        if num:
            W[d + '.largest_absolute_difference'] = max(num)
        W[f'CMP.counts.{f}.pass'] = sum(x['verdict'] == 'AGREE' for x in rows_)
        W[f'CMP.counts.{f}.fail'] = sum(x['verdict'] != 'AGREE' for x in rows_)
    W['chk.cmp.families_with_no_rows'] = [f for f in fams if not any(x['family'] == f for x in cmp_['comparisons'])]
    return W


# ---- ledger key -> (independent id) --------------------------------------
CELL_OF = lambda s: 'df-' + s.split('d117-reported-mean-')[1] if 'reported-mean' in s else s
MP = {'qwen3-1p7b': 'Qwen3-1.7B-4bit', 'qwen3-8b': 'Qwen3-8B-4bit'}


def hand_id(key, disc):
    m = re.fullmatch(r'(?:RC\.dominance\.ratios)\[(.+)/(absolute|comparative)\]\.(R|numerator_j|denominator_j|n|pass)', key)
    if m:
        return f'{m[1]}/{m[2]}.' + {'R': 'R', 'numerator_j': 'num', 'denominator_j': 'den', 'n': 'n', 'pass': 'pass'}[m[3]]
    m = re.fullmatch(r'RC\.dominance\.common_mode\[(.+)\]\.(R_cm|numerator_j|denominator_j|n|pass)', key)
    if m:
        return f'{m[1]}.cm.' + {'R_cm': 'R', 'numerator_j': 'num', 'denominator_j': 'den', 'n': 'n', 'pass': 'pass'}[m[2]]
    m = re.fullmatch(r'RC\.floor_cells\[(.+)\]\.floor_cmp_j', key)
    if m:
        return f'{m[1]}/comparative.minted'
    if key == 'RC.dominance.branch' or key.endswith('[label=dominance_branch].branch'):
        return 'dom.branch'
    if key.endswith('dominance_sentence_licensed'):
        return 'dom.sentence_licensed'
    if key == 'count(RC.dominance.ratios[*].pass=false)':
        return 'dom.failed_R'
    if key == 'RL52.dominance.failed_common_mode_n':
        return 'dom.failed_cm'
    m = re.fullmatch(r'DISC\.block_lines\[(\d+)\]\.(ratio|numerator_j|denominator_j|n)', key)
    if m:
        x = disc['block_lines'][int(m[1])]
        mm = re.match(r'd117-(qwen3-1p7b|qwen3-8b)-(decode|prefill)', x['cell_id'])
        base = f'{MP[mm[1]]}/{mm[2]}'
        f = {'ratio': 'R', 'numerator_j': 'num', 'denominator_j': 'den', 'n': 'n'}[m[2]]
        return f'{base}.cm.{f}' if int(m[1]) >= 43 else f'{base}/{x["component"]}.{f}'
    m = re.fullmatch(r'DISC\.floors\[(\d+)\]\.minted_j', key)
    if m:
        x = disc['floors'][int(m[1])]
        mm = re.search(r'(decode|prefill)-p?2?0?4?8?-?(qwen3-1p7b|qwen3-8b)', x['cell_id'])
        return f'{MP[mm[2]]}/{mm[1]}/comparative.minted'
    m = re.fullmatch(r'(?:RC\.reported_cells\[(df-[^\]]+)\]|PROJ-[AB]\.cells\[cell_id=([^\]]+)\])\.(.+)', key)
    if m:
        cell = m[1] or CELL_OF(m[2]); rest = m[3]
        tbl = {'interval.kind_averages_j[0]': 'kind0', 'interval.kind_averages_j[1]': 'kind1',
               'interval.kind_averages_j[2]': 'kind2',
               'interval.kind_averages_j.E_clock_anchor_shift_bound_j': 'kind0',
               'interval.kind_averages_j.E_interpolation_joint_edge_bound_j': 'kind1',
               'interval.kind_averages_j.E_whole_window_drift_allowance_j': 'kind2',
               'attribution_floor.attained_by': 'af_by', 'attribution_floor.minimum_j': 'af_min',
               'removed_units.count': 'removed_count', 'removed_units.load_trigger_count': 'load_trigger_count'}
        if rest in tbl:
            return f'{cell}.{tbl[rest]}'
        mm = re.fullmatch(r'removed_units\[unit_id=(.+)\]\.codes', rest)
        if mm:
            return f'{cell}.unit.{mm[1]}.codes'
    m = re.fullmatch(r'RC\.disclosures\.battery_assist\[(df-[^\]]+)\]\.(.+)', key)
    if m:
        return {'kept_units.repeat.count': f'{m[1]}.n_r', 'kept_units.quad.count': f'{m[1]}.n_b',
                'mean_j': f'{m[1]}.without.mean', 'lower_j': f'{m[1]}.without.lower',
                'upper_j': f'{m[1]}.without.upper'}.get(m[2])
    m = re.fullmatch(r'RC\.disclosures\.load_sensitivity\[(df-[^\]]+)\]\.(.+)', key)
    if m:
        return {'n_r': f'{m[1]}.load.n_r', 'n_b': f'{m[1]}.load.n_b', 'mean_j': f'{m[1]}.load.mean',
                'lower_j': f'{m[1]}.load.lower', 'upper_j': f'{m[1]}.load.upper',
                'restored_count': f'{m[1]}.load.restored'}.get(m[2])
    m = re.fullmatch(r'RC\.disclosures\.cross_window\[(.+)\]\.(delta_j|h_G_j|h_F_j|agree)', key)
    if m:
        return f'xw.{m[1]}.' + {'delta_j': 'delta', 'h_G_j': 'hG', 'h_F_j': 'hF', 'agree': 'agree'}[m[2]]
    m = re.fullmatch(r'DISC\.cells\[label=([^,\]]+),cell_id=([^,\]]+)(?:,unit_id=([^\]]+))?\]\.(.+)', key)
    if m:
        lab, cell, unit, rest = m[1], CELL_OF(m[2]), m[3], m[4]
        mm = re.search(r'(decode|prefill)-?p?2?0?4?8?-(qwen3-1p7b|qwen3-8b)', m[2])
        mk = f'{MP[mm[2]]}/{mm[1]}'
        if lab == 'removed unit':
            return f'{cell}.unit.{unit}.{rest}'
        if lab == 'battery_assist_cell':
            mm = re.fullmatch(r'(primary|without)\.(mean|h|B|lower|upper)_j', rest)
            if mm:
                return f'{cell}.{mm[2]}' if mm[1] == 'primary' else f'{cell}.without.{mm[2]}'
            return {'n_r': f'{cell}.n_r', 'n_b': f'{cell}.n_b'}.get(rest)
        if lab == 'cross_window':
            return {'delta_j': f'xw.{mk}.delta', 'h_G_j': f'xw.{mk}.hG', 'h_F_j': f'xw.{mk}.hF',
                    'agree': f'xw.{mk}.agree', 'agree_or_differ_word': f'xw.{mk}.word'}.get(rest)
        if lab == 'load_correlated_cell':
            mm = re.fullmatch(r'values\.(mean|h|B|lower|upper)_j', rest)
            if mm:
                return f'{cell}.load.{mm[1]}'
            return {'restored_counts.repeat': f'{cell}.load.restored_repeat',
                    'restored_counts.quad': f'{cell}.load.restored_quad'}.get(rest)
    m = re.fullmatch(r'count\(DISC\.cells\[label=load_correlated_cell,cell_id=([^\]]+)\]\)', key)
    if m:
        return f'{CELL_OF(m[1])}.load.present'
    m = re.fullmatch(r'DERIVE\(DISC\.cells\[label=load_correlated_cell,cell_id=([^\]]+)\]\)\.(n_r|n_b)', key)
    if m:
        return f'{CELL_OF(m[1])}.load.{m[2]}'
    m = re.fullmatch(r'(?:RC\.exclusions_rederivation\.GAMMA\.rederived|EXC)\.cells\[cell_id=[^\]]+\]\.dropped_units\[unit_id=([^\]]+)\]\.(codes|families)', key)
    if m:
        return f'ctr.{m[1]}.{m[2]}'
    m = re.fullmatch(r'EXC\.members_excluded\[run_id=([^\]]+)\]\.(codes|families)', key)
    if m:
        return f'EXC.member.{m[1]}.{m[2]}'
    m = re.fullmatch(r'RC\.disclosures\.whole_machine\.request_cross_check\.windows\.(\w+)\.models\[(.+)\]\.(.+)', key)
    if m:
        f = {'rho_median': 'median', 'rho_min': 'min', 'rho_max': 'max', 'rho_iqr[0]': 'q25', 'rho_iqr[1]': 'q75',
             'within_model_spread': 'spread', 'n_members': 'n', 'outside_hard_band.count': 'out',
             'consistency': 'consistency'}[m[3]]
        return f'rho.{m[1]}.{m[2]}.{f}'
    m = re.fullmatch(r'DISC\.window_lines\.(alpha|beta)\[(\d+)\]\.(median|minimum|maximum|q25|q75|spread)', key)
    if m:
        x = disc['window_lines'][m[1]][int(m[2])]
        model = {'qwen3-1p7b': 'Qwen3-1.7B-4bit', 'qwen3-8b': 'Qwen3-8B-4bit'}.get(x['model'], x['model'])
        return f'rho.{m[1].upper()}.{model}.' + {'minimum': 'min', 'maximum': 'max'}.get(m[3], m[3])
    m = re.fullmatch(r'RC\.windows\.(ALPHA|BETA)\.neg8\.(.+)', key)
    if m:
        w = m[1]
        return {'corpus_n': f'n8.{w}.corpus_n', 'n_start': f'n8.{w}.counts.start', 'n_mid': f'n8.{w}.counts.midpoint',
                'n_end': f'n8.{w}.counts.end', 'bound_envelope_j': f'n8.{w}.gross_energy.env',
                'bound_prediction_j': f'n8.{w}.gross_energy.pred', 'bound_j': f'n8.{w}.gross_energy.bound',
                'spread_j': f'n8.{w}.gross_energy.excursion', 'allowance_j': f'n8.{w}.gross_energy.allowance'}[m[2]]
    m = re.fullmatch(r'DISC\.window_lines\.(alpha|beta)\[label=neg8_allowance\]\.values_j\[bracket\.(?:claim_families|drift_bound_artifact\.claim_family_bounds)\.(\w+)\.(.+)\]', key)
    if m:
        w = m[1].upper()
        return f'n8.{w}.{m[2]}.' + {'bound_envelope_j': 'env', 'estimator.replicated_endpoint_sample_range_j': 'env',
                                    'bound_prediction_j': 'pred', 'estimator.prediction_two_endpoint_means_j': 'pred',
                                    'derived_repeatability_bound_j': 'bound', 'screen_statistic_j': 'stat',
                                    'trajectory_excursion_max_j': 'excursion', 'drift_allowance_j': 'allowance'}[m[3]]
    m = re.fullmatch(r'DERIVE\(DISC\.window_lines\.(alpha|beta)\[label=neg8_allowance\]\.values_j\.bracket\.claim_families\.(\w+)\)\.screen_decision', key)
    if m:
        return f'n8.{m[1].upper()}.{m[2]}.screen'
    m = re.fullmatch(r'DISC\.window_lines\.(alpha|beta)\[label=([a-z0-9_]+)(?:,run_id=([^\]]+))?\]\.(.+)', key)
    if m:
        w, lab, rest = m[1].upper(), m[2], m[4]
        if lab == 'neg8_screen':
            return f'n8.{w}.screen'
        if lab == 'reference_counts':
            return f'n8.{w}.{rest}'
        if lab == 'deciding_membership':
            return f'n8.{w}.{rest}'
        if lab == 'corpus_counts':
            return {'collected': f'n8.{w}.collected', 'in_window': f'n8.{w}.in_window', 'deciding': f'n8.{w}.deciding',
                    'desk_cap': f'n8.{w}.desk_cap', 'drop_counts.desk_cap': f'n8.{w}.drop.desk_cap',
                    'drop_counts.status': f'n8.{w}.drop.status',
                    'drop_counts.contention.request_overlap': f'n8.{w}.drop.contention'}.get(rest)
        if lab == 'corpus_physics_drop':
            return f'EXCW.{w}.{m[3]}.codes'
        if lab == 'reference_lost' and rest == 'reason':
            return f'EXCW.{w}.{m[3]}.codes'
    m = re.fullmatch(r'count\(DISC\.window_lines\.(alpha|beta)\[label=reference_(spare|lost)\]\)', key)
    if m:
        return f'n8.{m[1].upper()}.n_{m[2]}'
    m = re.fullmatch(r'DERIVE\(DISC\.window_lines\.(alpha|beta)\[label=reference_counts\]\)\.midpoint_lost', key)
    if m:
        return f'n8.{m[1].upper()}.midpoint_lost'
    m = re.fullmatch(r'DISC\.window_lines\.(alpha|beta)\[(\d+)\]\.(rise_k|plateau|producer_flag|temperature_unmeasured|differs_from_harvest_flag)', key)
    if m:
        return f'temp.{m[1]}.{m[2]}.' + {'rise_k': 'rise', 'plateau': 'plateau', 'producer_flag': 'producer',
                                         'temperature_unmeasured': 'unmeasured',
                                         'differs_from_harvest_flag': 'differs'}[m[3]]
    m = re.fullmatch(r'DISC\.window_lines\.(alpha|beta)\[156\]\.counts\.(.+)', key)
    if m:
        return f'phys.{m[1].upper()}.{m[2]}'
    m = re.fullmatch(r'DISC\.block_lines\[(\d+)\]\.(collected|planned)', key)
    if m:
        return f'att.{m[1]}.{m[2]}'
    m = re.fullmatch(r'DISC\.block_lines\[(\d+)\]\.(count|causes)', key)
    if m:
        return f'att.{m[1]}.{m[2]}'
    m = re.fullmatch(r'DISC\.block_lines\[(\d+)\]\.cause_counts\[cause=(.+)\]', key)
    if m:
        return f'att.{m[1]}.cause.{m[2]}'
    return None


# ---- source resolution ----------------------------------------------------
def split_path(p):
    out, i, buf = [], 0, ''
    while i < len(p):
        ch = p[i]
        if ch == '.':
            if buf:
                out.append(('k', buf)); buf = ''
        elif ch == '[':
            if buf:
                out.append(('k', buf)); buf = ''
            j = p.index(']', i); out.append(('b', p[i + 1:j])); i = j
        else:
            buf += ch
        i += 1
    if buf:
        out.append(('k', buf))
    return out


def resolve(src, key):
    m = re.fullmatch(r'(count|DERIVE)\((.+)\)(.*)', key)
    if m or key.startswith('RL52'):
        return KeyError
    alias, _, path = key.partition('.')
    if alias not in src:
        return KeyError
    cur = src[alias]
    toks = split_path(path); i = -1
    while i + 1 < len(toks):
        i += 1; kind, tok = toks[i]
        if kind == 'k':
            if tok == 'count' and isinstance(cur, list):
                cur = len(cur); continue
            if isinstance(cur, dict) and tok in cur:
                cur = cur[tok]; continue
            j, joined = i, tok  # a dict key that itself contains dots (e.g. counts.battery.assist)
            while isinstance(cur, dict) and j + 1 < len(toks) and toks[j + 1][0] == 'k' and joined not in cur:
                j += 1; joined += '.' + toks[j][1]
            if isinstance(cur, dict) and joined in cur:
                cur = cur[joined]; i = j; continue
            return KeyError
        if isinstance(cur, list) and re.fullmatch(r'\d+', tok):
            cur = cur[int(tok)]; continue
        if isinstance(cur, dict) and tok in cur:
            cur = cur[tok]; continue
        if isinstance(cur, dict) and tok.startswith('cause='):
            return KeyError
        if isinstance(cur, list) and '=' in tok:
            conds = dict(c.split('=', 1) for c in tok.split(','))
            hits = [x for x in cur if isinstance(x, dict) and all(str(x.get(k)) == v for k, v in conds.items())]
            if len(hits) != 1:
                return KeyError
            cur = hits[0]; continue
        if isinstance(cur, dict) and '=' in tok and len(tok.split('=')) == 2:
            return KeyError
        return KeyError
    return cur


# ---- comparison ----------------------------------------------------------
def norm_items(v):
    if isinstance(v, list):
        return sorted('None' if x is None else (x['code'] if isinstance(x, dict) and 'code' in x else str(x)) for x in v)
    return None


def compare(printed, value):
    """-> (word, residual or None)."""
    p = printed.strip().replace('−', '-').lstrip('+')
    if value is KeyError:
        return None, None
    if isinstance(value, bool):
        return ('exact' if p == str(value).lower() else 'MISMATCH'), None
    if value is None:
        return ('exact' if p.lower() in ('none', 'null', '') else 'MISMATCH'), None
    if isinstance(value, list):
        got = norm_items(value)
        want = sorted(x for x in p.split(',') if x) if p else []
        return ('exact' if got == want else 'MISMATCH'), None
    if isinstance(value, (int, float)):
        try:
            pv = float(p)
        except ValueError:
            return 'MISMATCH', None
        if pv == value:
            return 'exact', 0.0
        dec = len(p.split('.')[1]) if '.' in p and 'e' not in p.lower() else 0
        if 'e' in p.lower():
            mant = p.lower().split('e')[0]; dec = len(mant.split('.')[1]) if '.' in mant else 0
            tol = 0.5 * 10 ** (int(p.lower().split('e')[1]) - dec)
        else:
            tol = 0.5 * 10 ** -dec
        r = value - pv
        return ('within-rounding' if abs(r) <= tol * (1 + 1e-9) else 'MISMATCH'), r
    return ('exact' if p == str(value) else 'MISMATCH'), None


def sig2(x):
    if x is None or x == 0:
        return '0'
    return f'{x:.1e}'


def residual_sig_ok(s):
    s = s.strip()
    if s in ('', '0'):
        return True
    digits = re.sub(r'[eE][-+]?\d+$', '', s).lstrip('-+').replace('.', '').lstrip('0')
    return len(digits) <= 2


def repository_check():
    """Verify the reviewed bytes; this does not replay the custody review."""
    raw = b''.join(LEDGER.read_bytes().splitlines(keepends=True)[:1420])
    frozen = subprocess.run(['git', 'show', f'{REVIEWED_COMMIT}:docs/analysis/b5/rederivation.tsv'],
                            cwd=LEDGER.parents[3], check=True, capture_output=True).stdout
    if raw != frozen:
        raise ValueError('ledger differs from frozen Opus-reviewed bytes')
    rows = list(csv.DictReader(raw.decode('utf-8').splitlines(), delimiter='\t'))
    bad_residuals = [n for n, row in enumerate(rows, 2) if n >= 540 and not residual_sig_ok(row['difference'])]
    if bad_residuals:
        raise ValueError(f'extension residuals exceed two significant figures: {bad_residuals}')
    print(json.dumps({'mode':'repository-only; no custody source/recompute checks rerun',
                      'scope':'physical rows 1-1420; later appends outside this historical review',
                      'reviewed_bytes_identical':True, 'opened_custody':[]}, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=20261111)
    ap.add_argument('--sample', type=int, default=40)
    ap.add_argument('--repo-only', action='store_true', help='check frozen reviewed bytes; never open custody')
    a = ap.parse_args()
    if a.repo_only:
        repository_check()
        return
    before = {k: sha(ROOT + v[0]) for k, v in FILES.items()}
    assert all(before[k] == FILES[k][1] for k in FILES), 'pin drift before'
    src = {k: load(k) for k in FILES}
    V = compute(src)
    # EXCW: corpus physics drops (ALPHA/BETA members' stored codes)
    for w in ('ALPHA', 'BETA'):
        for m in src['RC']['exclusions_rederivation'][w]['rederived']['members_excluded']:
            V[f'EXCW.{w}.{m["run_id"]}.codes'] = sorted(m['codes'])
        for kind in ('spare', 'lost'):
            V[f'n8.{w}.n_{kind}'] = 0 if kind == 'spare' else len(V[f'n8.{w}.lost'])

    rows = list(csv.reader(LEDGER.read_text(encoding='utf-8').splitlines()[:1420], delimiter='\t', quoting=csv.QUOTE_NONE))
    hdr = rows[0]; col = {h: i for i, h in enumerate(hdr)}
    words = Counter(); src_words = Counter(); seat = Counter(); out = []; bad_resid = []
    hand_rows = {}
    for n, r in enumerate(rows, start=1):
        if n < 540:
            continue
        key, printed, sword, sdiff = r[col['key/leaf']], r[col['printed_value']], r[col['match']], r[col['difference']]
        seat[sword] += 1
        if not residual_sig_ok(sdiff):
            bad_resid.append(n)
        sv = resolve(src, key)
        if key.endswith('.causes') and isinstance(sv, list):
            sv = sorted(set('None' if x is None else x for x in sv))
        sw, _ = compare(printed, sv)
        src_words[sw or 'n/a'] += 1
        hid = hand_id(key, src['DISC'])
        hw, hr = (None, None)
        if hid is not None and hid in V:
            hw, hr = compare(printed, V[hid])
            hand_rows[n] = (hw, hr, sword)
        words[hw or ('source-only' if sw else 'unchecked')] += 1
        if sw == 'MISMATCH' or hw == 'MISMATCH':
            out.append((n, key, sw, hw, sig2(hr)))
        if hw and sword in ('exact', 'within-rounding') and hw != sword and not (hw == 'exact' and sword == 'within-rounding'):
            out.append((n, key, 'seat-word', f'{sword}->{hw}', sig2(hr)))
        if sw is None and hw is None:
            out.append((n, key, 'no-source', 'no-hand', ''))

    print('seat words, new rows:', dict(seat))
    print('source equality:', dict(src_words))
    print('independent recompute:', dict(words))
    print('residuals with more than 2 significant figures:', bad_resid)
    print('structural checks:', {k: v for k, v in V.items() if k.startswith('chk.') and v is not True} or 'all true')
    print('NEG-8 deciding corpus equals RC corpus_ids:', V['n8.ALPHA.corpus_match'], V['n8.BETA.corpus_match'])
    for o in out:
        print('FLAG', *o)
    # seeded sample of disclosure rows (607-802, 885-1420)
    pool = [n for n in range(607, 803)] + [n for n in range(885, 1421)]
    rnd = random.Random(a.seed); samp = sorted(rnd.sample(pool, a.sample))
    sc = Counter()
    for n in samp:
        r = rows[n - 1]; key, printed = r[col['key/leaf']], r[col['printed_value']]
        hw = hand_rows.get(n, (None,))[0]
        sw = compare(printed, resolve(src, key))[0]
        sc[hw or (f'source-{sw}' if sw else 'unchecked')] += 1
    print(f'sample seed={a.seed} k={a.sample}:', dict(sc))
    print('sample rows:', samp)
    targets = {'R/R_cm/terms/n/pass (540-603, 803-862)': list(range(540, 604)) + list(range(803, 863)),
               'comparative floors (550,566,582,598,865-868)': [550, 566, 582, 598, 865, 866, 867, 868],
               'B kind averages (607-609,627-629,657-659,684-686,950-952,980-982,1022-1024,1066-1068)':
                   [607, 608, 609, 627, 628, 629, 657, 658, 659, 684, 685, 686, 950, 951, 952, 980, 981, 982,
                    1022, 1023, 1024, 1066, 1067, 1068],
               'XWIN (623-626,653-656,680-683,709-712,974-978,1006-1010,1054-1058,1096-1100)':
                   [623, 624, 625, 626, 653, 654, 655, 656, 680, 681, 682, 683, 709, 710, 711, 712,
                    974, 975, 976, 977, 978, 1006, 1007, 1008, 1009, 1010, 1054, 1055, 1056, 1057, 1058,
                    1096, 1097, 1098, 1099, 1100]}
    for name, ns in targets.items():
        print(name, dict(Counter(hand_rows.get(n, ('NOT-COMPUTED',))[0] for n in ns)))
    # residual agreement: seat's 2-s.f. residual vs this script's residual, rounded the same way
    agree_r = Counter()
    for n, (hw, hr, _) in hand_rows.items():
        sd_ = rows[n - 1][col['difference']].strip()
        if hr is None or sd_ in ('', '0') and hr == 0:
            agree_r['zero/none'] += 1; continue
        try:
            ok = abs(float(sd_) - hr) <= max(abs(hr), 1e-12) * 0.051 + 1e-15
        except ValueError:
            ok = False
        agree_r['agree' if ok else 'differ'] += 1
    print('seat residual vs own residual (2 s.f.):', dict(agree_r))
    # seat 12's printed rows against the matching new rows (equal printed strings)
    PAIRS = {133: (961, 619), 134: (964, 620), 135: (965, 621), 136: (962,), 137: (963,), 139: (971, 617), 140: (972, 618),
             142: (993, 670), 143: (996, 671), 144: (997, 672), 145: (994,), 146: (995,), 148: (1003, 668), 149: (1004, 669),
             151: (1041, 643), 152: (1044, 644), 153: (1045, 645), 154: (1042,), 155: (1043,), 157: (1051, 641), 158: (1052, 642),
             160: (1083, 699), 161: (1086, 700), 162: (1087, 701), 163: (1084,), 164: (1085,), 166: (1093, 697), 167: (1094, 698),
             169: (623, 974), 170: (680, 1006), 171: (709, 1096), 172: (653, 1054),
             276: (554, 843), 277: (570, 848), 278: (586, 853), 279: (602, 858)}
    num = lambda x: float(x.replace('−', '-').lstrip('+'))
    pc = Counter()
    for o, ns in PAIRS.items():
        for n in ns:
            pc['equal' if num(rows[o - 1][col['printed_value']]) == num(rows[n - 1][col['printed_value']]) else 'DIFFER'] += 1
    print('seat-12 printed rows vs new rows:', dict(pc))
    allw = Counter(r[col['match']] for r in rows[1:])
    print('whole-ledger words:', dict(allw), 'MISMATCH rows:',
          [i for i, r in enumerate(rows, start=1) if i > 1 and r[col['match']] == 'MISMATCH'])
    # ---- round 4 (RL-55): rows 1421-1845 ----
    W = round4(src, V)
    r4 = list(csv.reader(LEDGER.read_text(encoding='utf-8').splitlines(), delimiter='\t', quoting=csv.QUOTE_NONE))
    s4, h4, seat4, fl4, hr4 = Counter(), Counter(), Counter(), [], {}
    for n in range(1421, len(r4) + 1):
        r = r4[n - 1]; key, printed, sword = r[col['key/leaf']], r[col['printed_value']], r[col['match']]
        seat4[sword] += 1
        if not residual_sig_ok(r[col['difference']]):
            fl4.append((n, 'residual>2sf'))
        sv = resolve(src, key)
        if key.endswith('.causes') and isinstance(sv, list):
            sv = sorted(set('None' if x is None else x for x in sv))
        sw = compare(printed, sv)[0]
        hw, hr = compare(printed, W[key]) if key in W else (None, None)
        s4[sw or 'n/a'] += 1; h4[hw or ('source-only' if sw else 'unchecked')] += 1
        hr4[n] = hw or (f'source-{sw}' if sw else 'unchecked')
        if 'MISMATCH' in (sw, hw) or (sw is None and hw is None):
            fl4.append((n, key, sw, hw, sig2(hr)))
    print('ROUND 4 rows:', len(r4) - 1420, 'seat words:', dict(seat4))
    print('ROUND 4 source equality:', dict(s4))
    print('ROUND 4 independent recompute:', dict(h4))
    print('ROUND 4 checks:', {k: v for k, v in W.items() if k.startswith('chk.')})
    for f in fl4:
        print('FLAG4', *f)
    groups = {'battery counts': lambda k: 'battery_counts' in k or 'arm_unmeasured' in k,
              'GAMMA': lambda k: '.gamma' in k or 'block_lines[9]' in k or 'block_lines[10]' in k
              or 'ctr-d117' in k}
    for gname, pred in groups.items():
        ns = [n for n in range(1421, len(r4) + 1) if pred(r4[n - 1][col['key/leaf']])]
        print(f'ROUND 4 {gname}: {len(ns)} rows', dict(Counter(hr4[n] for n in ns)))
    rest = [n for n in range(1421, len(r4) + 1)
            if not any(p(r4[n - 1][col['key/leaf']]) for p in groups.values())]
    samp4 = sorted(random.Random(a.seed + 4).sample(rest, min(40, len(rest))))
    print(f'ROUND 4 sample of the rest (seed {a.seed + 4}, k={len(samp4)} of {len(rest)}):',
          dict(Counter(hr4[n] for n in samp4)), samp4)
    print('ROUND 4 rest, all rows:', dict(Counter(hr4[n] for n in rest)))
    after = {k: sha(ROOT + v[0]) for k, v in FILES.items()}
    print('hashes before = after = pin:', all(before[k] == after[k] == FILES[k][1] for k in FILES))
    for k in FILES:
        print(' ', k, after[k])


if __name__ == '__main__':
    main()
