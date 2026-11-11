#!/usr/bin/env python3
"""Opus cold review of Block 5 phase-2 hand checks (RL-38 condition 9).

Written independently of docs/analysis/b5/hand_check_phase2.py: standard library
only, no repository analysis or recompute code, its own Student-t (closed-form
integer-df CDF in Decimal) and its own floor/estimator arithmetic from the
registered text (analysis plan 4, 5, 7.1, 7.3, 8.1, 8.2).

Data-free: it reads the two RL-38 custody roots read-only, hashes each file
before parsing and again at the end, and prints only aggregates at printed
precision, residual signs, counts and verdicts. It writes nothing anywhere.
The printed values it checks are read from the seat's hand_checks_phase2.tsv
(columns key and printed_value only; the seat's re-derived values are ignored).

Usage: python3 -I -B docs/analysis/b5/opus_coldreview_check.py
"""
import csv
import hashlib
import itertools
import json
import math
import sys
from decimal import Decimal, getcontext, ROUND_HALF_EVEN
from pathlib import Path

A = '/Users/edr/jw-b5-custody/dry-m/dry-run/'
B = '/Users/edr/jw-b5-custody/release-check-final-20261108T0942Z/'
FILES = {
    'REC': (A + 'B5-BLIND-DRY-RUN-RECORD.json', '66adc66e89f1a621009dd2ca98bc7c41b202d5c43a26a82af8a633a54c34aa03'),
    'FILL': (A + 'restricted/outputs/a29c6cf296199d70d9154719608ad21c07e08fda077224aa05a914b5ecf1f9b4-results-fill-input.json', 'a29c6cf296199d70d9154719608ad21c07e08fda077224aa05a914b5ecf1f9b4'),
    'CV': (A + 'restricted/outputs/67d8c231eeb5df2e1240cd3d0b965555ab39755042a2b9676f939f1543716f27-claim-verdicts.json', '67d8c231eeb5df2e1240cd3d0b965555ab39755042a2b9676f939f1543716f27'),
    'EXC': (A + 'restricted/finalized/analysed-attempt-exclusions-a9954365ef44c1b8a65603dd0ba52140109b45569fc795783ca6663d54586f46.json', 'a9954365ef44c1b8a65603dd0ba52140109b45569fc795783ca6663d54586f46'),
    'STEP': (A + 'restricted/outputs/b0f80f7265cf84203ded237245ae25cf87adfd987c2265a92b52c96efb1ea5b5.json', 'b0f80f7265cf84203ded237245ae25cf87adfd987c2265a92b52c96efb1ea5b5'),
    'RC': (B + 'recompute.json', 'c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc'),
}
SEEN = {}


def load(alias):
    path, pin = FILES[alias]
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != pin:
        sys.exit(f'{alias}: hash {digest} != RESULTS 0 pin')
    SEEN[alias] = digest
    return json.loads(raw)


# ---- Student t, independent of the seat's incomplete-beta series ----------
getcontext().prec = 80
D = Decimal


def _atan_series(x):
    x = D(x); s = D(0); term = x; k = 0; x2 = x * x
    while True:
        add = term / (2 * k + 1) * (1 if k % 2 == 0 else -1)
        s += add
        if abs(add) < D(10) ** -75:
            return s
        term *= x2; k += 1


PI = 4 * (4 * _atan_series(D(1) / 5) - _atan_series(D(1) / 239))


def _atan(x):
    x = D(x)
    if x < 0:
        return -_atan(-x)
    if x > 1:
        return PI / 2 - _atan(1 / x)
    if x > D('0.4'):
        return 2 * _atan(x / (1 + (1 + x * x).sqrt()))
    return _atan_series(x)


def p_two_sided(t, nu):
    """P(|T| > t) for integer nu by the closed-form CDF (even/odd nu)."""
    t = abs(D(t)); r = (nu + t * t).sqrt(); s = t / r; c = D(nu).sqrt() / r
    if nu % 2 == 0:
        tot = D(0); ck = D(1)
        for k in range(nu // 2):
            tot += ck * c ** (2 * k); ck *= D(2 * k + 1) / (2 * k + 2)
        return 1 - s * tot
    tot = D(0); dk = D(1)
    for k in range((nu - 1) // 2):
        tot += dk * c ** (2 * k); dk *= D(2 * k + 2) / (2 * k + 3)
    return (2 / PI) * (_atan(D(nu).sqrt() / t) - (s * c * tot if nu > 1 else 0))


def t975(nu):
    lo, hi = D(1), D(20)
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if p_two_sided(mid, nu) > D('0.05') else (lo, mid)
    return float((lo + hi) / 2)


def mean(x):
    return math.fsum(x) / len(x)


def sd(x):
    m = mean(x)
    return math.sqrt(math.fsum((v - m) ** 2 for v in x) / (len(x) - 1))


def median(x):
    x = sorted(x); n = len(x)
    return x[n // 2] if n % 2 else (x[n // 2 - 1] + x[n // 2]) / 2


# ---- computations ----------------------------------------------------------
def compute():
    rc, exc, fill, cv, step = (load(a) for a in ('RC', 'EXC', 'FILL', 'CV', 'STEP'))
    V = {}
    G = rc['members']['GAMMA']
    gid = lambda stage, b, r: f'd117c-qwen3-1p7b-vs-qwen3-8b-v5-{stage}-contrast-{b}-{r}'
    CT = {'ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b': ('decode', 'decode', 512),
          'ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b': ('prefill-p2048', 'prefill', 2048)}
    allow_g = rc['windows']['GAMMA']['neg8']['allowance_j']
    LOAD = {'thermal.os_level_nonzero', 'thermal.powermetrics_pressure_elevated', 'contention.request_overlap'}
    checks = {}
    for cid, (stage, ph, T) in CT.items():
        cell = next(c for c in exc['cells'] if c['cell_id'] == cid)
        dropped = {u['unit_id'][-3:]: u['codes'] for u in cell['dropped_units']}
        kept = [f'b{i:02d}' for i in range(1, 11) if f'b{i:02d}' not in dropped]
        checks[cid + ' kept quads EXC == RC'] = kept == [q[-3:] for q in rc['contrasts'][cid]['kept_quads']]
        def diffs(quads):
            out = []
            for b in quads:
                E = {r: G[gid(stage, b, r)]['E_j'][ph] for r in ('a1', 'a2', 'b1', 'b2')}
                out.append((E['b1'] + E['b2']) / 2 - (E['a1'] + E['a2']) / 2)
            return out
        d = diffs(kept); n = len(d); m = mean(d); s = sd(d); se = s / math.sqrt(n)
        ts = round(t975(n - 1), 3); lo, hi = m - ts * se, m + ts * se
        clock = mean([(G[gid(stage, b, 'a1')]['a_bop_j'][ph] + G[gid(stage, b, 'a2')]['a_bop_j'][ph]) / 2
                      + (G[gid(stage, b, 'b1')]['a_bop_j'][ph] + G[gid(stage, b, 'b2')]['a_bop_j'][ph]) / 2 for b in kept])
        Dt = clock + 0.0 + allow_g
        rho = [math.log(((G[gid(stage, b, 'b1')]['E_j'][ph] + G[gid(stage, b, 'b2')]['E_j'][ph]) / 2)
                        / ((G[gid(stage, b, 'a1')]['E_j'][ph] + G[gid(stage, b, 'a2')]['E_j'][ph]) / 2)) for b in kept]
        hr = t975(n - 1) * sd(rho) / math.sqrt(n)
        loo = [mean(d[:i] + d[i + 1:]) for i in range(n)]
        x = {'mean': m, 'sd': s, 'se': se, 'df': n - 1, 't': ts, 'lower': lo, 'upper': hi,
             'clock': clock, 'drift': allow_g, 'D': Dt, 'decision_lower': lo - Dt, 'decision_upper': hi + Dt,
             'p': float(p_two_sided(m / se, n - 1)), 'loo_min': min(loo), 'loo_max': max(loo),
             'ratio': math.exp(mean(rho)), 'ratio_lower': math.exp(mean(rho) - hr), 'ratio_upper': math.exp(mean(rho) + hr),
             'per_token': m / T, 'ci_token_lower': lo / T, 'ci_token_upper': hi / T,
             'di_token_lower': (lo - Dt) / T, 'di_token_upper': (hi + Dt) / T}
        for i, v in enumerate(d):
            x[f'd_k[{i}]'] = v
        for k, v in x.items():
            V[f'{cid}.{k}'] = v
        # load-correlated sensitivity: restore quads whose codes are all load codes
        restored = [b for b, codes in dropped.items() if set(codes) <= LOAD]
        dl = diffs(sorted(kept + restored)); nl = len(dl); ml = mean(dl); sel = sd(dl) / math.sqrt(nl)
        tl = round(t975(nl - 1), 3)
        V.update({f'load.{cid}.mean': ml, f'load.{cid}.lower': ml - tl * sel, f'load.{cid}.upper': ml + tl * sel,
                  f'load.{cid}.n': nl})
        checks[cid + ' stage-opening causes b01,b06'] = [dropped.get('b01'), dropped.get('b06')]
    ps = sorted(CT, key=lambda c: V[c + '.p'])
    a1 = min(1, 2 * V[ps[0] + '.p']); V[ps[0] + '.adjusted_p'] = a1
    V[ps[1] + '.adjusted_p'] = min(1, max(a1, V[ps[1] + '.p']))

    # reported cells, cross-window deltas, whole-machine cells
    CELLS = {'df-ph-decode-qwen3-1p7b': ('ALPHA', 'd117fq31p7', 'decode', 'decode', 512, 'Qwen3-1.7B-4bit'),
             'df-ph-prefill-p2048-qwen3-1p7b': ('ALPHA', 'd117fq31p7', 'prefill-p2048', 'prefill', 2048, 'Qwen3-1.7B-4bit'),
             'df-ph-decode-qwen3-8b': ('BETA', 'd117fq38', 'decode', 'decode', 512, 'Qwen3-8B-4bit'),
             'df-ph-prefill-p2048-qwen3-8b': ('BETA', 'd117fq38', 'prefill-p2048', 'prefill', 2048, 'Qwen3-8B-4bit')}
    WM = rc['disclosures']['whole_machine']['windows']
    for cell, (win, pre, stage, ph, T, model) in CELLS.items():
        M = rc['members'][win]; ku = rc['reported_cells'][cell]['kept_units']
        reps = ku['repeat']
        quads = [[f'{pre}-df-cmp-abba-ph-{stage}-{q[-3:]}-{r}' for r in ('a1', 'a2', 'b1', 'b2')] for q in ku['quad']]
        ids = reps + [i for q in quads for i in q]
        assert all(M[i]['model'] == model for i in ids)
        def strat(f):
            r = [f(i) for i in reps]; b = [mean([f(i) for i in q]) for q in quads]
            m = 0.2 * mean(r) + 0.8 * mean(b)
            h = t975(min(len(r), len(b)) - 1) * math.sqrt(0.04 * sd(r) ** 2 / len(r) + 0.64 * sd(b) ** 2 / len(b))
            return m, h, len(r), len(b)
        m, h, nr, nb = strat(lambda i: M[i]['E_j'][ph])
        Bt = math.fsum([0.2 * mean([M[i]['a_bop_j'][ph] for i in reps])
                        + 0.8 * mean([M[i]['a_bop_j'][ph] for q in quads for i in q]),
                        0.0, rc['windows'][win]['neg8']['allowance_j'] / 2])
        cidx = 'ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b' if ph == 'decode' else 'ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b'
        arms = ('a1', 'a2') if model == 'Qwen3-1.7B-4bit' else ('b1', 'b2')
        gv = [G[gid(stage, q[-3:], a)]['E_j'][ph] for q in rc['contrasts'][cidx]['kept_quads'] for a in arms]
        V.update({f'{cell}.mean': m, f'{cell}.lower': m - h - Bt, f'{cell}.upper': m + h + Bt, f'{cell}.h': h,
                  f'{cell}.B': Bt, f'{cell}.n_r': nr, f'{cell}.n_b': nb, f'{cell}.per_token': m / T,
                  f'{cell}.attribution': max(M[i]['a_bop_j'][ph] for i in ids),
                  f'{cell}.cross_delta': mean(gv) - m})
        WMm = WM[win]['members']
        mm, mh, _, _ = strat(lambda i: WMm[i]['phases'][ph]['energy_J'])
        V.update({f'machine.{cell}.mean': mm, f'machine.{cell}.h': mh,
                  f'machine.{cell}.share': median([M[i]['E_j'][ph] / WMm[i]['phases'][ph]['energy_J'] for i in ids])})

    # floors (absolute widths rebuilt from member a_bop_j; local widths from member r_j)
    TT = {n: round(t975(n - 1), 3) for n in range(5, 17)}
    def pf_abs(v):
        n = len(v); mu = mean(v); dev = [x - mu for x in v]
        return max(max(abs(x) for x in dev), TT[n] * sd(dev) * math.sqrt(1 + 1 / n))
    def pf_cmp(v):
        n = len(v)
        return max(max(abs(x) for x in v), abs(mean(v)) + TT[n] * sd(v) * math.sqrt(1 + 1 / n))
    guard = lambda n: 1.0 if n >= 10 else math.sqrt(9 / (n - 1))
    def corners(v, w, pf):
        return max(pf([x + s * ww for x, s, ww in zip(v, sg, w)]) for sg in itertools.product((-1, 1), repeat=len(v)))
    width_checks = []
    for model, (win, pre) in {'Qwen3-1.7B-4bit': ('ALPHA', 'd117fq31p7'), 'Qwen3-8B-4bit': ('BETA', 'd117fq38')}.items():
        M = rc['members'][win]; allow = rc['windows'][win]['neg8']['allowance_j']
        for phk, stage, ph in (('decode', 'decode', 'decode'), ('prefill', 'prefill-p2048', 'prefill')):
            fa = rc['floors'][f'{model}/{phk}/absolute']
            v = [M[i]['E_j'][ph] for i in fa['kept_units']]; w = [M[i]['a_bop_j'][ph] for i in fa['kept_units']]
            width_checks.append(max(abs(a - b) for a, b in zip(w, fa['widths_j'])))
            op = max(pf_abs(v), corners(v, w, pf_abs)); g = guard(len(v))
            V[f'floor.{model}/{phk}/absolute.guarded'] = g * op
            V[f'floor.{model}/{phk}/absolute.minted'] = g * op + allow
            fc = rc['floors'][f'{model}/{phk}/comparative']
            d, loc = [], []
            for q in fc['kept_units']:
                mm_ = {r: M[f'{pre}-df-cmp-abba-ph-{stage}-{q[-3:]}-{r}'] for r in ('a1', 'a2', 'b1', 'b2')}
                d.append((mm_['b1']['E_j'][ph] + mm_['b2']['E_j'][ph] - mm_['a1']['E_j'][ph] - mm_['a2']['E_j'][ph]) / 2)
                loc.append(math.fsum(mm_[r]['r_j'][ph] for r in mm_) / 2)
            width_checks.append(max(abs(a - b) for a, b in zip(loc, fc['local_j'])))
            sh = fc['shared_j']  # stored trace-sweep input; not derivable from member scalars
            point = pf_cmp(d)
            op = max(point, corners(d, [a + b for a, b in zip(sh, loc)], pf_cmp)); g = guard(len(d))
            V[f'floor.{model}/{phk}/comparative.guarded'] = g * op
            V[f'floor.{model}/{phk}/comparative.minted'] = g * op + allow
            num = max(pf_cmp([x + S * s_ + e * l for x, s_, e, l in zip(d, sh, sg, loc)])
                      for S in (-1, 1) for sg in itertools.product((-1, 1), repeat=len(d)))
            V[f'floor.{model}/{phk}/comparative.R_cm'] = num / point
    checks['max |rebuilt width - stored width| (abs from a_bop_j, local from r_j)'] = max(width_checks)

    # request-level rail shares (GAMMA, all members) and the hard band
    by = {}; bad = 0
    for v in WM['GAMMA']['members'].values():
        r = v['phases']['request']; dm = r['meter']['delta_J'] + r['battery']['delta_J']; rho = r['rail_delta_J'] / dm
        bad += not (0 < rho <= 1 and dm - r['rail_delta_J'] >= 0)
        by.setdefault(v['model'], []).append(rho)
    for model, x in by.items():
        V.update({f'request.{model}.median': median(x), f'request.{model}.minimum': min(x),
                  f'request.{model}.maximum': max(x)})
    checks['GAMMA request members outside hard band / total'] = (bad, sum(map(len, by.values())))
    # contention counts from stored member codes (no raw re-detection)
    for w in ('ALPHA', 'BETA', 'GAMMA'):
        V[f'flags.{w}.contention'] = sum(c == 'contention.request_overlap'
                                         for m in rc['exclusions_rederivation'][w]['rederived']['members_excluded'] for c in m['codes'])
    checks['GAMMA contention from EXC.members_excluded'] = sum(c == 'contention.request_overlap' for m in exc['members_excluded'] for c in m['codes'])

    # held S rows: scaled allowance, factor = max(1, E/E_ref, T/T_ref)
    sa = rc['disclosures']['scaled_allowance']
    ref = {}
    for w in ('ALPHA', 'BETA', 'GAMMA'):
        ids = sa['windows'][w]['reference_ids']
        ref[w] = (mean([rc['members'][w][i]['E_j']['request'] for i in ids]),
                  mean([WM[w]['members'][i]['phases']['request']['duration_s'] for i in ids]))
    S = {}
    for cid, (stage, ph, T) in CT.items():
        kept = [q[-3:] for q in rc['contrasts'][cid]['kept_quads']]
        side = {}
        for s_, arms in (('a', ('a1', 'a2')), ('b', ('b1', 'b2'))):
            ids = [gid(stage, b, r) for b in kept for r in arms]
            side[s_] = (mean([G[i]['E_j'][ph] for i in ids]) / ref['GAMMA'][0],
                        mean([WM['GAMMA']['members'][i]['phases']['request']['duration_s'] for i in ids]) / ref['GAMMA'][1])
        fb = max(1, side['b'][0])
        established = side['b'][1] < fb and max(side['a']) < fb  # request duration bounds phase duration
        Dsc = V[cid + '.clock'] + allow_g * fb
        S[cid] = {'E-ratio b': side['b'][0], 'T-ratio upper bound b': side['b'][1], 'factor fixed by bound': established,
                  'D': Dsc, 'decision_lower': V[cid + '.lower'] - Dsc, 'decision_upper': V[cid + '.upper'] + Dsc}
        gates = []
        for model, w, cell in (('Qwen3-1.7B-4bit', 'ALPHA', f'df-ph-{stage}-qwen3-1p7b'), ('Qwen3-8B-4bit', 'BETA', f'df-ph-{stage}-qwen3-8b')):
            pre = 'd117fq31p7' if w == 'ALPHA' else 'd117fq38'; ku = rc['reported_cells'][cell]['kept_units']
            dur = lambda i: WM[w]['members'][i]['phases'][ph]['duration_s']
            Tm = 0.2 * mean([dur(i) for i in ku['repeat']]) + 0.8 * mean(
                [dur(f'{pre}-df-cmp-abba-ph-{stage}-{q[-3:]}-{r}') for q in ku['quad'] for r in ('a1', 'a2', 'b1', 'b2')])
            f = max(1, V[f'{cell}.mean'] / ref[w][0], Tm / ref[w][1])
            S[cid].setdefault('floor factor basis', []).append(
                (w, 'E' if f == V[f'{cell}.mean'] / ref[w][0] else ('T' if f > 1 else '1'),
                 round(V[f'{cell}.mean'] / ref[w][0], 3), round(Tm / ref[w][1], 3)))
            al = rc['windows'][w]['neg8']['allowance_j']
            phk = 'decode' if ph == 'decode' else 'prefill'
            gates.append(max(V[f'floor.{model}/{phk}/absolute.guarded'], V[f'floor.{model}/{phk}/comparative.guarded']) + al * f)
        S[cid]['floor_gate'] = max(gates)

    # DLE-5 count: scalar instances vs normalized paths (lists -> *)
    inst = []
    def leaves(x, path):
        if isinstance(x, dict):
            for k, v in x.items():
                leaves(v, path + [k])
        elif isinstance(x, list):
            for v in x:
                leaves(v, path + ['*'])
        else:
            inst.append('/'.join(path))
    for c in fill['gamma']['contrasts']:
        leaves(c['floor'].get('point_floor_diagnostics', {}), ['contrasts', '*', 'floor', 'point_floor_diagnostics'])
        for r in c['floor'].get('resolutions', []):
            leaves(r.get('point_floor_diagnostics', {}), ['contrasts', '*', 'floor', 'resolutions', '*', 'point_floor_diagnostics'])
        leaves(c['claim_evaluation']['floor_limit'], ['contrasts', '*', 'claim_evaluation', 'floor_limit'])
    checks['DLE-5 groups: scalar leaf instances / distinct normalized paths'] = (len(inst), len(set(inst)))
    checks['stored whole-window verdicts'] = sorted(v['stored_verdict']['status'] for v in step['windows'].values())
    checks['CV included bundles with 512 runtime-observed tokens'] = sum(
        1 for b in cv['bundle_audit'] if b.get('inclusion_status') == 'included'
        and b['token_provenance'].get('output_tokens') == 512 and b['token_provenance'].get('token_count_source') == 'runtime_observed')
    checks['windows with a window-level meter flag'] = sum(
        any(f.get('scope', {}).get('level') == 'window' for f in WM[w]['meter_flags']) for w in WM)
    checks['max |E_j - stored_E_j| over all members'] = max(
        abs(m['E_j'][k] - m['stored_E_j'][k]) for w in rc['members'].values() for m in w.values()
        for k in m['E_j'] if isinstance(m['E_j'][k], float) and isinstance(m['stored_E_j'].get(k), float))
    return V, checks, S


def at_printed(printed, value):
    s = printed.strip().replace('−', '-').lstrip('+')
    if s.endswith('%'):
        s, value = s[:-1], value * 100
    if 'e' in s.lower():
        mant, exp = s.lower().split('e'); nd = len(mant.split('.')[1]) if '.' in mant else 0
        q = Decimal(repr(value)).scaleb(-int(exp)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_EVEN)
        return q == Decimal(mant), value - float(s)
    nd = len(s.split('.')[1]) if '.' in s else 0
    q = Decimal(repr(float(value))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_EVEN)
    return q == Decimal(s), float(value) - float(s)


def main():
    V, checks, S = compute()
    tsv = Path(__file__).with_name('hand_checks_phase2.tsv')
    rows = list(csv.DictReader(tsv.open(), delimiter='\t'))
    agree = refuted = exact = 0
    for r in rows:
        ok, diff = at_printed(r['printed_value'], V[r['key']])
        agree += ok; refuted += not ok; exact += ok and diff == 0
        if not ok:
            print('REFUTED', r['ledger_row'], r['key'], r['printed_value'])
    print(f'hand-check rows: {len(rows)}; confirmed {agree} ({exact} exact, {agree - exact} within-rounding); refuted {refuted}')
    held = {388: ('ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b', 'D', '9.345'),
            389: ('ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b', 'decision_lower', '137.095'),
            390: ('ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b', 'decision_upper', '156.164'),
            391: ('ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b', 'floor_gate', '15.228'),
            392: ('ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b', 'D', '8.045'),
            393: ('ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b', 'decision_lower', '93.395'),
            394: ('ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b', 'decision_upper', '110.224'),
            395: ('ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b', 'floor_gate', '11.685')}
    for row, (cid, k, printed) in held.items():
        ok, _ = at_printed(printed, S[cid][k])
        basis = (f'floor factors (window, binding term, E-ratio, T-ratio from meter-side phase durations) = {S[cid]["floor factor basis"]}'
                 if k == 'floor_gate' else f'contrast factor fixed by request-duration bound = {S[cid]["factor fixed by bound"]}')
        print(f'S row {row}: {k} printed {printed} agree={ok}; {basis}')
    for cid, s in S.items():
        print(cid, 'E-ratio b %.3f, T-ratio upper bound b %.3f' % (s['E-ratio b'], s['T-ratio upper bound b']))
    for k, v in checks.items():
        print(k, '=', v)
    for alias, before in SEEN.items():
        after = hashlib.sha256(Path(FILES[alias][0]).read_bytes()).hexdigest()
        print(f'{alias} sha256 before=after: {before == after}')


if __name__ == '__main__':
    main()
