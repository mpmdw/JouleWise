"""Synthetic knee consult. Run from repo root, Python 3.13, no hardware.
All mutations are in-memory copies of production knee_scan; production is unchanged.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import inspect
import json
import math
from pathlib import Path
import random
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts import bytes_stream_test as probe
sys.path.insert(0, str(Path(__file__).parent / 'reviewer'))
saved_argv = sys.argv
sys.argv = [sys.argv[0], str(ROOT)]
from scan_cases import SIZES, worked5, dram_only
sys.argv = saved_argv

OUT = Path(__file__).parent
TICK = Fraction(125, 3)  # ns, lead measurement, not Linux clock
RES = 42  # ns, lead's reported clock_getres
SOURCE = inspect.getsource(probe.knee_scan)


def replace(src, old, new):
    if src.count(old) != 1:
        raise RuntimeError('production source anchor changed: '+old)
    return src.replace(old, new)


def compile_scan(src):
    ns = dict(vars(probe))
    exec(src, ns)
    return ns['knee_scan']


def candidates():
    f1 = replace(SOURCE, 'peak = max(defined, key=lambda p: p["m_bytes_s"])',
                 'peak = max(defined, key=lambda p: p["m_bytes_s"]-p["dm_bytes_s"])')
    f2 = replace(f1, '1e-9/c["repeats"]', '2*c["clock_resolution_ns"]*1e-9/c["repeats"]')
    adjacent = replace(f2, 'if not above:',
                       'if not any(a["above"] and b["above"] for a,b in zip(pairs,pairs[1:])):')
    frontier = replace(f2, 'if not above:',
                       'if not above or not any(p["size"] == max(above)//2 and p["above"] for p in pairs):')
    return {'current': probe.knee_scan, 'F1': compile_scan(f1), 'F1+F2': compile_scan(f2),
            'F1+F2+adjacent': compile_scan(adjacent),
            'F1+F2+frontier': compile_scan(frontier), 'exact+arms': exact_arms}


def exact_arms(receipts):
    # Reuse production grouping, mean/spread and pair definition through in-memory copy.
    # Replacing q is the only change before computing exact reciprocal endpoints.
    r = EXACT_BASE(receipts)
    pairs = r['pairs']
    defined = [p for p in pairs if p['m_bytes_s'] is not None]
    for p in defined:
        d, dd = p['difference_s'], p['uncertainty_s']
        a = p['size']/2
        p.update(lower=a/(d+dd), upper=a/(d-dd))
    for key in ('B','Bc1','Bc3','Bc2','phi','reason'):
        r.pop(key,None)
    r.update(status='knee not found', K=None, threshold=None, threshold_uncertainty=None)
    if pairs[-1]['m_bytes_s'] is None:
        r['reason'] = 'top pair undefined'
        return r
    cache = max(defined, key=lambda p:p['lower'])
    dram = pairs[-1]
    def h(x,y): return 1/((63/64)/x+(1/64)/y)
    low, high = h(dram['lower'], cache['lower']), h(dram['upper'], cache['upper'])
    nominal=h(dram['m_bytes_s'],cache['m_bytes_s'])
    r.update(threshold=nominal, threshold_uncertainty=max(nominal-low,high-nominal),
             threshold_lower=low, threshold_upper=high, cache_reference_size=cache['size'])
    for p in pairs:
        p.pop('margin',None); p.pop('bar',None)
        p['above'] = p['m_bytes_s'] is not None and p['lower'] > high
        if p['m_bytes_s'] is not None:
            p.update(margin=p['m_bytes_s']-nominal,
                     bar=(p['m_bytes_s']-p['lower'])+(high-nominal))
    above = [p['size'] for p in pairs if p['above']]
    k = next((s for s in sorted(r['sizes'])[1:] if not any(a >= s for a in above)), None)
    bysize = {p['size']:p for p in pairs}
    if not above:
        r['reason'] = 'no resolved cache evidence'
    elif k is None or 64*k > max(r['sizes']):
        r['reason'] = '64 K > s_max'
    elif not all(bysize.get(s, {}).get('above',False) for s in (k//8,k//4)):
        r['reason'] = 'cache arm pairs not both resolved'
    else:
        r.update(status='knee found', K=k, B=max(2**32,64*k), Bc1=k//16,
                 Bc3=k//8,Bc2=k//4,phi=k/max(2**32,64*k))
        r.pop('reason',None)
    return r

EXACT_BASE = probe.knee_scan


def quantized_stamp(tick_index, rounding):
    value = tick_index*125
    return value//3 if rounding == 'floor' else (value+1)//3


def receipts(model, sigma, rng, rounding='floor'):
    out=[]
    for s in SIZES:
        td=model(s)
        n=math.floor(2/td)
        for j in range(3):
            dur=n*td*(1+rng.gauss(0,sigma))
            # Random phase in one physical tick, at random integer tick epoch.
            # Integer arithmetic for the large epoch avoids floating cancellation.
            phase=rng.random()
            index=rng.randrange(24_000_000_000,48_000_000_000)
            end_index=index+math.floor(phase+dur*1e9/float(TICK))
            start=quantized_stamp(index,rounding)
            end=quantized_stamp(end_index,rounding)
            out.append(dict(bytes_per_read=s,repeats=n,start_ns=start,end_ns=end,
                clock_resolution_ns=RES,clock_tick_num_ns=125,clock_tick_den=3,
                clock_ns_conversion=rounding))

    for c in out: c.update(clock='CLOCK_MONOTONIC_RAW', clock_resolution_s=4.2e-8, clock_tick_num_ns=125, clock_tick_den=3, clock_tick_source='synthetic lead 2026-10-28 tick', clock_ns_conversion='unknown', clock_ns_conversion_source='synthetic replay')
    return out


def reviewer_replays():
    logs={}
    for name in ['knee_noise_diag','scan_cases','knee_fix_check','dram_noise','tick_quant']:
        p=subprocess.run([sys.executable,'-B',name+'.py',str(ROOT)],cwd=OUT/'reviewer',
                         check=True,text=True,capture_output=True)
        logs[name]=p.stdout
    (OUT/'reviewer-replays.txt').write_text('\n\n'.join(k+'\n'+v for k,v in logs.items()))
    return logs


exact_arms = probe.knee_scan
candidates = lambda: {"round4": probe.knee_scan}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--trials',type=int,default=2000)
    parser.add_argument('--rounding',choices=['floor','nearest'],default='floor')
    parser.add_argument('--replay-reviewer',action='store_true')
    args=parser.parse_args()
    if args.replay_reviewer:
        reviewer_replays()
    scans=candidates()
    result={'base':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'production_source_sha256':hashlib.sha256(SOURCE.encode()).hexdigest(),
            'python':sys.version,'trials_per_cell':args.trials,'rounding':args.rounding,
            'tick_ns':'125/3','resolution_ns':RES,'seed_scheme':'20261028 + level*10 + world',
            'cells':[]}
    for level,sigma in enumerate([0,.0005,.002,.005,.01]):
        for world,model in enumerate([worked5,dram_only]):
            rng=random.Random(20261028+level*10+world)
            counts={name:Counter() for name in scans}
            for trial in range(args.trials):
                rec=receipts(model,sigma,rng,args.rounding)
                for name,scan in scans.items():
                    r=scan(rec)
                    counts[name][str(r['K']) if r['K'] else r.get('reason','refused')]+=1
            for name,cs in counts.items():
                found=sum(v for k,v in cs.items() if k.isdigit())
                cell=dict(noise_percent=sigma*100,world='true-knee' if world==0 else 'DRAM-only',
                    candidate=name,found=found,refused=args.trials-found,
                    wrong_k=sum(v for k,v in cs.items() if k.isdigit() and int(k)!=2**26),
                    outcomes=dict(cs))
                result['cells'].append(cell)
            print(sigma,world,{name:dict(cs) for name,cs in counts.items()},flush=True)
    (OUT/('results-'+args.rounding+'.json')).write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__': main()
