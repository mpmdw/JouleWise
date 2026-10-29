"""Independent leaf walk of the round-5 reader (synthetic). Usage:
  python3.13 -B leafwalk.py /tmp/jw KBDIR OUT.json [--cli-every N]
KBDIR: output of kb-v2-delta-opus-2/r3/e2e.py (eight records whose receipts come from the real
stream() with a fake array module, written and reloaded). Idle native rows are thinned to a
12-row, 4.8 s cadence (>= three 10 s bandwidths) so each read takes milliseconds; battery_samples
keeps every 50th real row. Every node of all eight records (receipt and harvest, read or not) and
of the scan object is mutated; lists of rows are visited at rows {0, 1, mid, last}. A second base
adds two meter_gaps rows to record 3 to reach the gap rows and adapter fields.
Checks per case: no exception; JSON with allow_nan=False; one call per record; no defined bound
below the baseline; and 'silent' = a printed contrast changed while all four classes stayed as in
the baseline and no reason names the leaf (the value was consumed without validation)."""
import json, math, subprocess, sys, tempfile, traceback
from copy import deepcopy
from multiprocessing import Pool
from pathlib import Path
JW, KB, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
CLI_EVERY = int(sys.argv[sys.argv.index('--cli-every')+1]) if '--cli-every' in sys.argv else 0
sys.path[:0] = [str(JW)]
from scripts import bytes_stream_test as p

def thin(data):
    for rec in data['records']:
        r, h = rec['receipt'], rec['harvest']
        for span in ('pre', 'post'):
            start = r['idle_'+span+'_start_ns']
            for kind, rows in h['idle'][span].items():
                mean = math.fsum(x['power_w'] for x in rows)/len(rows)
                step = 4_800_000_000
                h['idle'][span][kind] = [dict({'stamp_ns': start+i*step} if kind in ('meter', 'battery') else
                    {'start_ns': start+i*step, 'end_ns': start+(i+1)*step}, power_w=mean*(1+0.001*((i % 3)-1)))
                    for i in range(12)]
        h['battery_samples'] = h['battery_samples'][::50]
    return data

BASE = thin(json.loads((KB/'input_A_knee_found.json').read_text()))
GAPS = deepcopy(BASE)
GAPS['records'][3]['harvest']['meter_gaps'] = [{'span': 'stream', 'missing_samples': 1}, {'span': 'pre', 'missing_samples': 2}]

def read(data):
    out = p.read_known_bytes(deepcopy(data.get('records')), deepcopy(data.get('scan')))
    json.dumps(out, allow_nan=False)
    return out

def nodes(value, path=()):
    yield path, value
    if isinstance(value, dict):
        for k, v in value.items():
            yield from nodes(v, path+(k,))
    elif isinstance(value, list):
        idx = sorted({0, 1, len(value)//2, len(value)-1}) if len(value) > 4 else range(len(value))
        for i in idx:
            if 0 <= i < len(value):
                yield from nodes(value[i], path+(i,))

def modes(v):
    m = [('deleted', None), ('null', None)]
    if isinstance(v, bool):
        m += [('wrong_type', 'x')]
    elif isinstance(v, (int, float)):
        m += [('wrong_type', 'x'), ('nan', float('nan')), ('inf', float('inf')), ('-inf', float('-inf')),
              ('negative', -abs(v)-1), ('zero', 0), ('bool', True), ('huge_int', 10**400)]
    elif isinstance(v, str):
        m += [('wrong_type', 7), ('empty', '')]
    elif isinstance(v, list):
        m += [('wrong_type', 7), ('empty', []), ('short', v[:1]), ('long', v+v[-1:])]
    elif isinstance(v, dict):
        m += [('wrong_type', 7), ('empty', {})]
    return m

def bounds(out):
    b = {}
    for k, v in out['boundaries'].items():
        if isinstance(v.get('halfwidth'), (int, float)):
            b[('B', k)] = v['halfwidth']
    for i, c in enumerate(out['calls']):
        g = (c.get('meter_gaps') or {}).get('bound_j')
        if isinstance(g, (int, float)):
            b[('gap', i)] = g
        for k, row in c.get('boundaries', {}).items():
            for f in ('bound_j', 'edge_bound_j', 'baseline_bound_j'):
                if isinstance(row.get(f), (int, float)):
                    b[(f, i, k)] = row[f]
    return b

BASELINES = {}
def baseline(name):
    if name not in BASELINES:
        out = read(BASE if name == 'base' else GAPS)
        BASELINES[name] = (out, bounds(out))
    return BASELINES[name]

def apply(data, path, mode, value):
    if not path:
        return value if mode != 'deleted' else None
    o = data
    for k in path[:-1]:
        o = o[k]
    if mode == 'deleted':
        del o[path[-1]]
    else:
        o[path[-1]] = value
    return data

def job(args):
    n, base, path, mode, value = args
    data = apply(deepcopy(BASE if base == 'base' else GAPS), path, mode, value)
    leaf = '.'.join(map(str, path))
    res = {'n': n, 'base': base, 'leaf': leaf, 'mode': mode}
    try:
        out = read(data)
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        res['crash'] = f'{type(e).__name__}: {e} @ {Path(tb.filename).name}:{tb.lineno}'
        return res
    b0, bb = baseline(base)
    if len(out['calls']) != len(data['records'] if isinstance(data, dict) and isinstance(data.get('records'), list) else []):
        res['lost_calls'] = len(out['calls'])
    nb = bounds(out)
    shr = [f'{k}: {nb[k]!r} < {bb[k]!r}' for k in nb if k in bb and nb[k] < bb[k]]
    if shr:
        res['shrunk'] = shr
    cls = {k: v['class'] for k, v in out['boundaries'].items()}
    name = next((str(k) for k in reversed(path) if isinstance(k, str)), leaf)
    named = any(name in r for r in out['reasons'])
    if cls == {k: v['class'] for k, v in b0['boundaries'].items()} and not named:
        diff = [k for k in out['boundaries'] if out['boundaries'][k].get('delta') != b0['boundaries'][k].get('delta')
                or out['boundaries'][k].get('halfwidth') != b0['boundaries'][k].get('halfwidth')]
        if diff:
            res['silent'] = {k: (b0['boundaries'][k].get('delta'), out['boundaries'][k].get('delta'),
                                 b0['boundaries'][k].get('halfwidth'), out['boundaries'][k].get('halfwidth')) for k in diff}
    res['classes'] = cls
    if CLI_EVERY and n % CLI_EVERY == 0:
        with tempfile.TemporaryDirectory() as d:
            f = Path(d)/'in.json'
            f.write_text(json.dumps(data))
            pr = subprocess.run([sys.executable, '-B', str(JW/'scripts/bytes_stream_test.py'), 'read', str(f)],
                                capture_output=True, text=True)
        res['cli_rc'] = pr.returncode
        if pr.returncode == 0:
            res['cli_same_classes'] = {k: v['class'] for k, v in json.loads(pr.stdout)['boundaries'].items()} == cls
    return res

if __name__ == '__main__':
    jobs, n = [], 0
    for base, data in (('base', BASE), ('gaps', GAPS)):
        roots = [('records', i) for i in range(8)] + [('scan',)] if base == 'base' else [('records', 3, 'harvest')]
        for root in roots:
            o = data
            for k in root:
                o = o[k]
            for sub, v in nodes(o):
                for mode, value in modes(v):
                    jobs.append((n, base, root+sub, mode, value)); n += 1
    print('cases', len(jobs), flush=True)
    b0, _ = baseline('base'); g0, _ = baseline('gaps')
    print('baseline classes', {k: (v['class'], v.get('halfwidth')) for k, v in b0['boundaries'].items()})
    print('gaps baseline classes', {k: (v['class'], v.get('halfwidth')) for k, v in g0['boundaries'].items()},
          'gap bound', g0['calls'][3]['meter_gaps'].get('bound_j'))
    with Pool(4) as pool:
        results = pool.map(job, jobs, chunksize=50)
    OUT.write_text(json.dumps(results, default=str))
    crash = [r for r in results if 'crash' in r]
    print('crashes', len(crash), 'shrunk', sum('shrunk' in r for r in results), 'lost_calls',
          sum('lost_calls' in r for r in results), 'silent', sum('silent' in r for r in results),
          'cli checked', sum('cli_rc' in r for r in results), 'cli rc!=0', sum(r.get('cli_rc', 0) != 0 for r in results),
          'cli class mismatch', sum(r.get('cli_same_classes') is False for r in results))
    from collections import Counter
    import re
    def norm(leaf):
        return re.sub(r'records\.\d+', 'records.*', re.sub(r'\.\d+(?=\.|$)', '.#', leaf))
    print('crash kinds:')
    for (k, m), c in Counter((r['crash'].split(' @')[0][:70]+' @'+r['crash'].split(' @')[1], r['mode']) for r in crash).most_common():
        print(f'  {c:5d} {m:9s} {k}')
    print('crash leaves (normalized):', sorted({(norm(r['leaf']), r['mode']) for r in crash}))
    print('silent (normalized):')
    for key, c in Counter((norm(r['leaf']), r['mode']) for r in results if 'silent' in r).most_common():
        print(f'  {c:4d} {key}')
    ex = {}
    for r in results:
        if 'silent' in r:
            ex.setdefault((norm(r['leaf']), r['mode']), r)
    for k, r in list(ex.items())[:40]:
        print('  e.g.', r['leaf'], r['mode'], r['silent'])
    for r in results:
        if 'shrunk' in r or 'lost_calls' in r:
            print('  BAD', r)
