"""End-to-end, non-MLX: real stream() with a fake array module -> receipts on disk ->
real `read` CLI on synthetic native harvest streams. Also an independent §5 recompute.

Usage: python3.13 -B e2e.py /tmp/jw OUTDIR
"""
import json, math, os, shutil, subprocess, sys
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

JW, OUT = Path(sys.argv[1]), Path(sys.argv[2])
sys.path[:0] = [str(JW), str(Path(__file__).parent)]
from scripts import bytes_stream_test as p
from joulewise.idle_dependence import estimate_newey_west_bartlett as nw
from scan_cases import receipts as scan_receipts, worked5, dram_only

OUT.mkdir(parents=True, exist_ok=True)
GB = 1e9
THR = 4597412096*512/7.098
IDLE_R, IDLE_DC = .051, (6101.072862-5967.417892)/56.018813
PR_S, PE_S = 223.22/7.098-IDLE_R, 577.210005/11.017813-(IDLE_DC-IDLE_R)
PAY = {'S': 2**32, 'C1': 2**22, 'C3': 2**23, 'C2': 2**24}
ORDER = ('S', 'C1', 'C3', 'C2', 'C2', 'C3', 'C1', 'S')


class FakeMX:
    uint8 = 'uint8'; __version__ = '0.31.2'
    def __init__(self, ns, dispatch_ns): self.ns, self.d, self.sums, self.sleeps = ns, dispatch_ns, 0, []
    def ones(self, shape, dtype): return object()
    def sum(self, data): self.sums += 1; return object()
    def eval(self, v): self.ns += self.d
    def synchronize(self): pass
    def sleep(self, s): self.sleeps.append(s); self.ns += round(s*1e9)


REF, VER = p.registered_stack()
STACK = deepcopy(REF); STACK.update(deepcopy(VER)); STACK['git_commit'] = 'review'
STACK.update({f: 'not_applicable' for f in p.NOT_APPLICABLE})


def shapes():
    out = {}
    for kind, step, se in [('rails', 100_000_000, math.sqrt(1.2037e-4)), ('gpu', 100_000_000, math.sqrt(1.2037e-4)/2),
                           ('meter', 20_000_000, .05), ('battery', 200_000_000, .01)]:
        n = 57_600_000_000//step
        vals = [(-1)**i for i in range(n)]
        var = nw(vals, 10_000_000_000//step, [57.6/n]*n).governed_variance_of_mean_w2
        out[kind] = (step, [v*se/math.sqrt(var) for v in vals])
    return out


SH = shapes()


def make_receipts(stack=STACK, repo_root=None):
    recs, ns = [], 10**12
    for i, arm in enumerate(ORDER):
        size = PAY[arm]
        td = 50e-6+size/(THR if arm == 'S' else 1e12)
        n = math.floor((500 if arm == 'S' else 250)/td)
        mx = FakeMX(ns, round(td*1e9))
        kw = {'repo_root': repo_root} if repo_root else {}
        if stack is None:
            r = p.stream(size, n, device='macbook_m3_max', mx=mx, clock_ns=lambda: mx.ns, sleep=mx.sleep, **kw)
        else:
            with patch.object(p, 'collect_stack', return_value=deepcopy(stack)):
                r = p.stream(size, n, device='macbook_m3_max', mx=mx, clock_ns=lambda: mx.ns, sleep=mx.sleep, **kw)
        assert mx.sums == n+1 and mx.sleeps == [3, 57.6, 3, 3, 57.6]
        ns = mx.ns + 10_000_000_000  # allocation/exit between calls
        path = OUT/f'receipt_{i+1}_{arm}.json'
        path.write_text(json.dumps(r, indent=2, allow_nan=False)+'\n')
        recs.append(json.loads(path.read_text()))  # every class is computed from the written receipt
    return recs


def harvest(r, arm, rails_above=None):
    t = r['duration_s']
    pr, pe = (PR_S, PE_S) if arm == 'S' else (28., 25.)
    if rails_above is not None:
        pr = rails_above(arm)
    h = {'energy_j': {'rails': (IDLE_R+pr)*t, 'gpu': (pr/2)*t, 'meter': (IDLE_DC+pr+pe)*t, 'battery': 0.0},
         'idle': {}, 'anchor_shift_j': .5388, 'r_max_s': .017762388, 'tau_s': 2.302,
         'operative_timing_bound_s': .001, 'meter_edge_w': [IDLE_DC+pr+pe]*2, 'battery_edge_j': [0, 0],
         'capture_stack': {k: deepcopy(REF[k]) for k in ('telemetry_backend', 'measurement_boundary_label')},
         'adapter_max_w': 140, 'adapter_source': 'H adapter nameplate 140 W',
         'battery_source': 'native battery polls (synthetic)', 'meter_gaps': []}
    for name, sign in (('pre', 1), ('post', -1)):
        start = r['idle_'+name+'_start_ns']; h['idle'][name] = {}
        for kind, (step, vals) in SH.items():
            mean = {'rails': IDLE_R+sign*.002, 'gpu': .02, 'meter': IDLE_DC+sign*.05, 'battery': 0.}[kind]
            h['idle'][name][kind] = [dict({'stamp_ns': start+i*step} if kind in ('meter', 'battery') else
                                          {'start_ns': start+i*step, 'end_ns': start+(i+1)*step}, power_w=mean+v)
                                     for i, v in enumerate(vals)]
    # battery polls through the whole call, measured maximum discharge 0 W (charging/at adapter)
    h['battery_samples'] = [{'stamp_ns': s, 'power_w': 0.0} for s in
                            range(r['idle_pre_start_ns'], r['idle_post_end_ns'], 200_000_000)]
    return h


def read_cli(name, scan, records):
    path = OUT/f'input_{name}.json'
    path.write_text(json.dumps({'scan': scan, 'records': records}, allow_nan=False))
    pr = subprocess.run([sys.executable, '-B', str(JW/'scripts/bytes_stream_test.py'), 'read', str(path)],
                        capture_output=True, text=True)
    if pr.returncode:
        return {'error': pr.stderr.strip().splitlines()[-1]}
    res = json.loads(pr.stdout)
    (OUT/f'output_{name}.json').write_text(pr.stdout)
    return res


def summary(name, res):
    if 'error' in res:
        print(f'[{name}] REFUSED: {res["error"]}'); return
    b = res['boundaries']
    cls = {k: b[k]['class']+(f" ({b[k]['reason']})" if b[k].get('reason') else '') for k in b}
    print(f'[{name}] contrasts={res["printed"]["contrasts"]} share={res["printed"]["share"]}')
    print(f'   classes={cls}')
    for k, line in res['printed']['claim_lines'].items():
        print(f'   claim[{k}]: {line}')


def indep_5():
    """Independent §3 arithmetic from §5 inputs (no program code)."""
    se_r = math.sqrt(2*1.2037e-4)/2
    se_dc = .05/math.sqrt(2)+.01/math.sqrt(2)
    out = {}
    for beta in ('rails', 'dc', 'rest'):
        x, dx, xi = {}, {}, {}
        for arm, size in PAY.items():
            td = 50e-6+size/(THR if arm == 'S' else 1e12)
            n = math.floor((500 if arm == 'S' else 250)/td); t = n*td
            pr, pe = (PR_S, PE_S) if arm == 'S' else (28., 25.)
            above = {'rails': pr, 'dc': pr+pe, 'rest': pe}[beta]
            br = .5388+t*(.002+2*se_r)
            bd = 2*(pr+pe+IDLE_DC)*(.017762388+.020)+t*(.05+2*se_dc)
            b = {'rails': br, 'dc': bd, 'rest': br+bd}[beta]
            x[arm] = above*t/n; dx[arm] = b/n  # two equal calls: sums cancel
        gc = (x['C2']-x['C1'])/(PAY['C2']-PAY['C1']); a = x['C1']-gc*PAY['C1']
        r = x['C3']-a-gc*PAY['C3']; gd = (x['S']-a)/PAY['S']
        dgc = (dx['C1']+dx['C2']+abs(r))/(PAY['C2']-PAY['C1']); da = dx['C1']+abs(r)+dgc*PAY['C1']
        out[beta] = ((gd-gc)*GB, ((dx['S']+da+abs(a))/PAY['S']+dgc)*GB, a*1e3, gc*GB, gd*GB)
    f = out['rails'][0]/out['dc'][0]
    df = (out['rails'][1]+abs(f)*out['dc'][1])/abs(out['dc'][0])
    return out, f, df


if __name__ == '__main__':
    ind, f, df = indep_5()
    for k, v in ind.items():
        print(f'indep §5 {k}: alpha={v[2]:.4f} mJ gc={v[3]:.5f} gd={v[4]:.5f} Delta={v[0]:.9f} dDelta={v[1]:.9f}')
    print(f'indep §5 f={f:.6f} df={df:.6f}')

    scan = p.knee_scan(scan_receipts(worked5, True))
    recs = make_receipts()
    base = [{'receipt': r, 'harvest': harvest(r, a)} for r, a in zip(recs, ORDER)]
    res = read_cli('A_knee_found', scan, base); summary('A knee found (§5)', res)
    for k in ('rails', 'dc', 'rest'):
        v = res['boundaries'][k]
        print(f'   program-indep {k}: dDelta {v["delta"]-ind[k][0]:+.2e} dHalf {v["halfwidth"]-ind[k][1]:+.2e} J/GB')
    print('   stamped envelope s:', res['stamped_envelope_s'], ' hour_as_run:', res['hour_as_run_s'])
    print('   receipt reference_check status per unit:', {s['status'] for s in recs[0]['reference_check']['units'].values()},
          'errors', recs[0]['reference_check']['errors'])

    for q in (False, True):
        sc = p.knee_scan(scan_receipts(dram_only, q))
        summary(f'B DRAM-only scan quantized={q} -> {sc["status"]} ({sc.get("reason")})', read_cli(f'B{int(q)}', sc, base))

    g = deepcopy(base); g[3]['harvest']['meter_gaps'] = [{'span': 'stream', 'missing_samples': 1}]
    res = read_cli('C_gap', scan, g); summary('C one stream counter gap, call 4', res)
    print('   gap term:', {k: res['calls'][3]['meter_gaps'][k] for k in ('bound_j', 'P_max_w', 'adapter_source', 'battery_source')},
          'halfwidths', {k: round(res['boundaries'][k]['halfwidth'], 8) for k in ('dc', 'rest')})
    g = deepcopy(base); g[3]['harvest']['meter_gaps'] = [{'span': 'pre', 'missing_samples': 1}]
    res = read_cli('C2_gap_pre', scan, g)
    print('   pre-idle gap bound J:', res['calls'][3]['meter_gaps']['bound_j'], 'expected', 2.8*g[3]['receipt']['duration_s']/(2*57.6))

    for fld, val in (('packages.mlx-metal', '0.31.3'), ('packages.numpy', '2.5.2'), ('python', '3.13.2')):
        st = deepcopy(STACK)
        if fld.startswith('packages.'): st['packages'][fld[9:]] = val
        else: st[fld] = val
        d = [{'receipt': r, 'harvest': harvest(r, a)} for r, a in zip(make_receipts(st), ORDER)]
        res = read_cli('D_'+fld, scan, d)
        sc = res['stack_comparisons'][0]
        summary(f'D stack difference in {fld}', res)
        print('   physical:', sc['physical_differences'], 'disclosure:', sc['disclosure_differences'])
    d = deepcopy(base); d[2]['harvest']['capture_stack']['telemetry_backend'] = 'other'
    res = read_cli('D_capture', scan, d); summary('D capture telemetry_backend differs', res)
    print('   disclosure:', res['stack_comparisons'][2]['disclosure_differences'])

    zero = [{'receipt': r, 'harvest': harvest(r, a, rails_above=lambda arm: 0.)} for r, a in zip(recs, ORDER)]
    summary('E zero rails contrast (rails above idle = 0 in every arm)', read_cli('E_zero', scan, zero))
    # negative: cache arms burn more per byte than DRAM on every boundary
    neg = []
    for r, a in zip(recs, ORDER):
        h = harvest(r, a); t = r['duration_s']
        if a == 'S':
            h['energy_j']['rails'] = (IDLE_R+5.)*t; h['energy_j']['meter'] = (IDLE_DC+5.)*t
        neg.append({'receipt': r, 'harvest': h})
    summary('E negative contrast', read_cli('E_neg', scan, neg))
    # exactly-zero Delta_DC
    print('   describe_share(DC zero valid?):', p.describe_share({'delta': 0., 'halfwidth': .001}, {'delta': 0., 'halfwidth': 0.}))

    # Running checkout diverging from the embedded 6731d5249 reference
    alt = OUT/'alt_checkout'
    if alt.exists(): shutil.rmtree(alt)
    for rel in p.REFERENCE_SOURCES:
        (alt/rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy(JW/rel, alt/rel)
    pins = json.loads((alt/'configs/b6/registration/identity_pins.json').read_text())
    first = next(iter(pins['units'])); pins['units'][first]['stack_identity']['os_version'] = 'macOS-27.0'
    (alt/'configs/b6/registration/identity_pins.json').write_text(json.dumps(pins))
    bp = json.loads((alt/'configs/bytes/identity_pins.json').read_text()); bp['runtime_versions']['packages']['mlx'] = '0.32.0'
    (alt/'configs/bytes/identity_pins.json').write_text(json.dumps(bp))
    subprocess.run(['git', 'init', '-q', str(alt)]); subprocess.run(['git', '-C', str(alt), 'add', '.'])
    subprocess.run(['git', '-C', str(alt), '-c', 'user.name=r', '-c', 'user.email=r@example.invalid', 'commit', '-qm', 'x'])
    dv = make_receipts(repo_root=alt)
    rc = dv[0]['reference_check']
    print('[F divergent checkout] receipt written; unit diffs:',
          {u: c['differences'] for u, c in rc['units'].items() if c['differences']}, '| versions diffs:', rc['versions']['differences'])
    res = read_cli('F_divergent', scan, [{'receipt': r, 'harvest': harvest(r, a)} for r, a in zip(dv, ORDER)])
    summary('F divergent checkout', res)
    (alt/'configs/bytes/identity_pins.json').write_text('{not json')
    dv = make_receipts(repo_root=alt)
    print('[F2 unreadable versions file] errors:', dv[0]['reference_check']['errors'])
    # Unpatched collect_stack on this Linux seat (real runtime_versions, real git)
    un = make_receipts(stack=None)
    print('[G unpatched collect_stack] stack_check differences:', un[0]['stack_check']['differences'])
