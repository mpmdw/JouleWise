"""Replay the knee consult (47bead35d) verify.py and full noise sweep against the
production knee_scan at the reviewed commit. Usage:
  python3.13 -B consult_replay.py /path/to/JouleWise CONSULT_DIR [trials]
The consult's experiment.py patches the a7a20c197 source by text anchor and cannot
import at 977a5d2df; this file copies its receipt generator verbatim except that the
clock fields use the production receipt names (clock_resolution_s etc.).
"""
from collections import Counter
from fractions import Fraction as F
import json, math, random, sys
from pathlib import Path
root, consult = Path(sys.argv[1]), Path(sys.argv[2])
trials = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
sys.path[:0] = [str(root)]
from scripts import bytes_stream_test as probe

SIZES = [2**k for k in range(14, 36)]
def dram_only(s): return 50e-6+s/331.6e9
def worked5(s):
    k = 64*2**20
    if s <= k//2: return 50e-6+s/1e12
    t32 = 50e-6+(k//2)/1e12; t64 = t32+(k//2)/198.8e9
    return t64+(s-k)/331.6e9
def quantized_stamp(i, rounding):
    v = i*125
    return v//3 if rounding == 'floor' else (v+1)//3
def receipts(model, sigma, rng, rounding='floor'):
    out = []
    for s in SIZES:
        td = model(s); n = math.floor(2/td)
        for j in range(3):
            dur = n*td*(1+rng.gauss(0, sigma))
            phase = rng.random(); index = rng.randrange(24_000_000_000, 48_000_000_000)
            end_index = index+math.floor(phase+dur*1e9/float(F(125, 3)))
            out.append(dict(bytes_per_read=s, repeats=n, start_ns=quantized_stamp(index, rounding),
                end_ns=quantized_stamp(end_index, rounding), clock='CLOCK_MONOTONIC_RAW',
                clock_resolution_s=4.2e-8, clock_tick_num_ns=125, clock_tick_den=3,
                clock_tick_source='synthetic', clock_ns_conversion=rounding,
                clock_ns_conversion_source='synthetic'))
    return out

def exact_reference(rec):  # verify.py, resolution read as exact 42 ns
    times = {}
    for s in sorted({c['bytes_per_read'] for c in rec}):
        calls = [c for c in rec if c['bytes_per_read'] == s]
        ds = [F(c['end_ns']-c['start_ns'], 10**9*c['repeats']) for c in calls]
        t = sum(ds)/len(ds)
        qs = [2*(max(F(42), F(c['clock_tick_num_ns'], c['clock_tick_den']))+1)/(10**9*c['repeats']) for c in calls]
        times[s] = (t, max(abs(d-t) for d in ds)+sum(qs)/len(qs))
    pairs = {}; sizes = sorted(times)
    for lo, hi in zip(sizes, sizes[1:]):
        d = times[hi][0]-times[lo][0]; dd = times[hi][1]+times[lo][1]
        if d > dd:
            pairs[hi] = {'m_bytes_s': F(hi-lo)/d, 'lower': F(hi-lo)/(d+dd), 'upper': F(hi-lo)/(d-dd)}
    c = max(pairs, key=lambda s: (pairs[s]['lower'], -s))
    md, mc = pairs[sizes[-1]], pairs[c]
    h = lambda x, y: 1/(F(63, 64)/x+F(1, 64)/y)
    th = {k: h(md[k], mc[k]) for k in ('m_bytes_s', 'lower', 'upper')}
    out = {}
    for s, p in pairs.items():
        out[s] = dict(p, margin=p['m_bytes_s']-th['m_bytes_s'],
                      bar=p['m_bytes_s']-p['lower']+th['upper']-th['m_bytes_s'], above=p['lower'] > th['upper'])
    return th, out, c

rec = receipts(worked5, 0, random.Random(8))
r = probe.knee_scan(rec)
th, pairs, c = exact_reference(rec)
diff = {}
p = next(x for x in r['pairs'] if x['size'] == 2**25)
for k in ('m_bytes_s', 'lower', 'upper', 'margin', 'bar'):
    diff['pair_'+k] = float(abs(F(p[k])-pairs[2**25][k]))/1e9
for o, k in (('threshold', 'm_bytes_s'), ('threshold_lower', 'lower'), ('threshold_upper', 'upper')):
    diff[o] = float(abs(F(r[o])-th[k]))/1e9
noise = max(diff.values())
print('verify: K', r['K'], 'cache ref', r['cache_reference_size'], 'exact cache ref', c)
print('verify: discrepancies GB/s', json.dumps(diff))
print('verify: max', noise, '1e6*max', 1e6*noise, '< 4.5e-7:', 1e6*noise < 4.5e-7)
print('verify: threshold halfwidth GB/s', r['threshold_uncertainty']/1e9, 'bar', p['bar']/1e9, 'margin', p['margin']/1e9)
# every pair's above flag equals the exact rational flag
mism = [x['size'] for x in r['pairs'] if x['above'] != pairs.get(x['size'], {}).get('above', False)]
print('verify: above-flag mismatches vs rational', mism)
ok = True
for mode in ('floor', 'nearest'):
    bad = sum(probe.knee_scan(receipts(worked5, 0, random.Random(s), mode))['K'] != 2**26 for s in range(400))
    print('verify: phase sweep', mode, 'non-64MiB', bad, '/400'); ok &= bad == 0

# Full sweep, compared trial-for-trial in aggregate with the consult's exact+arms cells.
for rounding in ('floor', 'nearest'):
    recorded = json.loads((consult/f'results-{rounding}.json').read_text())
    cells = {(c['noise_percent'], c['world']): c for c in recorded['cells'] if c['candidate'] == 'exact+arms'}
    for level, sigma in enumerate([0, .0005, .002, .005, .01]):
        for world, model in enumerate([worked5, dram_only]):
            rng = random.Random(20261028+level*10+world)
            cs = Counter()
            for t in range(trials):
                x = probe.knee_scan(receipts(model, sigma, rng, rounding))
                cs[str(x['K']) if x['K'] else x.get('reason', 'refused')] += 1
            name = 'true-knee' if world == 0 else 'DRAM-only'
            want = cells[(sigma*100, name)]['outcomes'] if trials == 2000 else None
            same = (dict(cs) == want) if want is not None else 'n/a'
            print(f'sweep {rounding} {sigma*100:.2f}% {name}: {dict(cs)} identical-to-consult={same}', flush=True)
