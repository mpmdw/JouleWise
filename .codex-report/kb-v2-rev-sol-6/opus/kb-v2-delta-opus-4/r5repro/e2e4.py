"""Round-4 end-to-end probe (round-5 copy: absent display fields print <absent> instead of stopping) (synthetic only). Usage:
  python3.13 -B e2e4.py /tmp/jw KBOUT OUTDIR
KBOUT is the directory written by r3/e2e.py (real stream() receipts + harvest rows).
Part 1: real stream() with a fake array module whose clock advances on a 125/3 ns
tick and converts by floor or nearest; the real clock_metadata() runs its macOS branch
against a fake mach_timebase_info (125/3) and patched clock_getres (4.2e-8 s).
Receipts are written, reloaded, and the real `scan` CLI is run in a subprocess.
Part 2: variants of the knee-found input through the real `read` CLI in a subprocess.
"""
import json, math, random, subprocess, sys
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
JW, KB, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.path[:0] = [str(JW)]
from scripts import bytes_stream_test as p
OUT.mkdir(parents=True, exist_ok=True)
CLI = [sys.executable, '-B', str(JW/'scripts/bytes_stream_test.py')]
TICK = F(125, 3)

def dram_only(s): return 50e-6+s/331.6e9
def worked5(s):
    k = 64*2**20
    if s <= k//2: return 50e-6+s/1e12
    t32 = 50e-6+(k//2)/1e12; t64 = t32+(k//2)/198.8e9
    return t64+(s-k)/331.6e9
def late(s):  # isolated late above pair at 128 MiB
    if 2**26 < s <= 2**27: return worked5(2**26)+(s-2**26)/1e12
    return worked5(s)

class Mach:
    def __call__(self, ptr):
        ptr._obj.numer, ptr._obj.denom = 125, 3
        return 0
class Lib: mach_timebase_info = Mach()

class TickMX:
    """Each eval advances true time by td; stamps = physical tick floor, then integer ns conversion."""
    uint8 = 'uint8'; __version__ = '0.31.2'
    def __init__(self, td, rounding, rng):
        self.t = F(rng.randrange(24_000_000_000, 48_000_000_000))*TICK + F(rng.random())*TICK  # ns
        self.td, self.rounding = F(td*1e9), rounding
    def ones(self, shape, dtype): return object()
    def sum(self, d): return object()
    def eval(self, v): self.t += self.td
    def synchronize(self): pass
    def clock(self):
        ticks = math.floor(self.t/TICK); v = ticks*125
        return v//3 if self.rounding == 'floor' else (v+1)//3

def scan_cli(model, rounding, seed):
    rng = random.Random(seed)
    ref, ver = p.registered_stack(); stack = {**ref, **ver}
    recs = []
    d = OUT/f'scan_{model.__name__}_{rounding}'; d.mkdir(exist_ok=True)
    for s in (2**k for k in range(14, 36)):
        for j in range(3):
            mx = TickMX(model(s), rounding, rng); n = math.floor(2/model(s))
            with patch.object(p, 'collect_stack', return_value=stack), \
                 patch.object(p.sys, 'platform', 'darwin'), patch('ctypes.CDLL', return_value=Lib()), \
                 patch.object(p.time, 'clock_getres', return_value=4.2e-8):
                r = p.stream(s, n, device='macbook_m3_max', idle_s=0, settle_s=0, mx=mx, clock_ns=mx.clock, sleep=lambda _: None)
            f = d/f'{s}-{j}.json'; f.write_text(json.dumps(r, allow_nan=False)); recs.append(json.loads(f.read_text()))
    (d/'scan.json').write_text(json.dumps(recs))
    cp = subprocess.run(CLI+['scan', str(d/'scan.json')], capture_output=True, text=True)
    if cp.returncode: print('SCAN CLI FAILED', cp.stderr[-400:]); return None
    out = json.loads(cp.stdout); (d/'scan_out.json').write_text(cp.stdout)
    return out, recs

print('== Part 1: real stream() -> receipts -> scan CLI (125/3 ns tick, real clock_metadata macOS branch)')
for model in (worked5, dram_only, late):
    for rounding in ('floor', 'nearest'):
        res = scan_cli(model, rounding, 8)
        if res is None: continue
        r, recs = res
        c = recs[0]
        above = [x['size'] for x in r['pairs'] if x['above']]
        print(f"{model.__name__:9s} {rounding:7s}: status={r['status']} K={r['K']} candidate={r['candidate_K']} reason={r.get('reason')} "
              f"pairs={len(r['pairs'])} above_MiB={[a//2**20 for a in above]} arm_checks={[(a['size']//2**20, a['above'], a['reason']) for a in r['arm_checks']]} "
              f"clock=({c['clock_resolution_s']},{c['clock_tick_num_ns']}/{c['clock_tick_den']},{c['clock_ns_conversion']},bound={c['clock_duration_bound_ns']})")
        if model is worked5 and rounding == 'floor':
            pr = next(x for x in r['pairs'] if x['size'] == 2**25)
            print(f"   16->32 MiB margin {pr['margin']/1e9:.6f} GB/s bar {pr['bar']/1e9:.3g} GB/s; T={r['threshold']/1e9:.4f} GB/s "
                  f"T half-width {r['threshold_uncertainty']/1e9:.2g} GB/s; cache_ref={r['cache_reference_size']} cache_reference.above={r['cache_reference']['above']} "
                  f"(pairs entry above={next(x for x in r['pairs'] if x['size']==r['cache_reference_size'])['above']})")
            json.dump({'scan': r}, open(OUT/'scan_worked_floor.json', 'w'))

print('== Part 2: read CLI variants on the knee-found production-shaped input')
base = json.load(open(KB/'input_A_knee_found.json'))
def read(name, records=None, scan=None, show=()):
    d = {'records': base['records'] if records is None else records, 'scan': base['scan'] if scan is None else scan}
    f = OUT/f'read_{name}.json'; f.write_text(json.dumps(d, allow_nan=False))
    cp = subprocess.run(CLI+['read', str(f)], capture_output=True, text=True)
    if cp.returncode:
        print(f'[{name}] CLI rc={cp.returncode} TRACEBACK: ' + cp.stderr.strip().splitlines()[-1]); return None
    r = json.loads(cp.stdout)
    cls = {b: v['class']+(f" ({v['reason']})" if 'reason' in v and v['class'] == 'UNDETERMINED' else '') for b, v in r['boundaries'].items()}
    print(f"[{name}] calls={len(r['calls'])} records_retained={r['input_records']==d['records']} classes={cls}")
    print(f"    contrasts={r['printed']['contrasts']}")
    for k in show:
        try: v = eval(k, {"r": r})
        except (KeyError, TypeError, IndexError) as e: v = f'<absent: {type(e).__name__} {e}>'
        print(f'    {k}: {v}')
    return r
def mod(fn):
    rs = deepcopy(base['records']); fn(rs); return rs
read('A_baseline')
def gap(h, **kw):
    h['meter_gaps'] = [{'span': 'stream', 'missing_samples': 1}]; h.update(kw)
read('F4_unnamed_adapter_source', mod(lambda rs: gap(rs[3]['harvest'], adapter_source='')))
read('F4_unnamed_battery_source', mod(lambda rs: gap(rs[3]['harvest'], battery_source=None)))
read('F4_missing_adapter_rating', mod(lambda rs: (gap(rs[3]['harvest']), rs[3]['harvest'].pop('adapter_max_w'))))
read('F4_lost_call_7_records', base['records'][:3]+base['records'][4:], show=("r['boundaries']['rails'].get('arms')",))
read('F4_lost_call_empty_record', mod(lambda rs: rs.__setitem__(3, {})), show=("r['boundaries']['rails'].get('arms')", "r['calls'][0]['boundaries']['rails']"))
read('F4_missing_r_max', mod(lambda rs: rs[0]['harvest'].pop('r_max_s')))
for k in ('rails', 'gpu', 'meter', 'battery'):
    read(f'F4_missing_integral_{k}', mod(lambda rs, k=k: rs[0]['harvest']['energy_j'].pop(k)))
read('F4_missing_tau', mod(lambda rs: rs[0]['harvest'].pop('tau_s')))
read('F4_missing_battery_samples', mod(lambda rs: rs[0]['harvest'].pop('battery_samples')))
read('F4_missing_idle_block', mod(lambda rs: rs[0]['harvest'].pop('idle')))
read('F4_missing_capture_stack', mod(lambda rs: rs[0]['harvest'].pop('capture_stack')))
read('F4_missing_receipt_settle', mod(lambda rs: rs[0]['receipt'].pop('settle_s')))
read('F4_harvest_missing', mod(lambda rs: rs[0].pop('harvest')))
# Edge-power contract: two values required (§4 "meter_edge_w (two edge powers)").
read('EDGE_meter_edge_empty_list', mod(lambda rs: rs[0]['harvest'].__setitem__('meter_edge_w', [])),
     show=("r['calls'][0]['boundaries']['dc']['edge_bound_j']", "r['boundaries']['dc']['halfwidth']"))
read('EDGE_meter_edge_one_value', mod(lambda rs: rs[0]['harvest'].__setitem__('meter_edge_w', [83.8])),
     show=("r['calls'][0]['boundaries']['dc']['edge_bound_j']",))
read('EDGE_meter_edge_scalar', mod(lambda rs: rs[0]['harvest'].__setitem__('meter_edge_w', 83.8)))
read('EDGE_battery_edge_scalar', mod(lambda rs: rs[0]['harvest'].__setitem__('battery_edge_j', 0)))
read('EDGE_anchor_shift_string', mod(lambda rs: rs[0]['harvest'].__setitem__('anchor_shift_j', 'n/a')))
read('GAP_entry_not_object', mod(lambda rs: rs[3]['harvest'].__setitem__('meter_gaps', [1])))
read('GAP_negative_adapter', mod(lambda rs: gap(rs[3]['harvest'], adapter_max_w=-140)), show=("r['calls'][3]['meter_gaps'].get('bound_j')",))
read('GAP_string_adapter', mod(lambda rs: gap(rs[3]['harvest'], adapter_max_w='140')))
# F5 duplicated stamps
for s in ('meter', 'battery'):
    def dup(rs, s=s):
        rows = rs[0]['harvest']['idle']['pre'][s]; rows[1]['stamp_ns'] = rows[0]['stamp_ns']
    read(f'F5_duplicate_{s}_stamp', mod(dup), show=(f"{{k:r['calls'][0]['native_idle']['pre']['{s}'][k] for k in ('sample_count','duplicate_stamp_count','native_interval_ns','lag_count')}}",
                                                       f"'variance_w2' in r['calls'][0]['native_idle']['pre']['{s}']"))
def alldup(rs):
    rows = rs[0]['harvest']['idle']['pre']['battery']
    for x in rows: x['stamp_ns'] = rows[0]['stamp_ns']
read('F5_all_battery_stamps_identical', mod(alldup))
# F6 rails boundary label
read('F6_rails_label_differs', mod(lambda rs: rs[5]['harvest']['capture_stack']['measurement_boundary_label'].__setitem__('rails', ['cpu_power', 'gpu_power'])))
read('F6_rails_label_no_gpu', mod(lambda rs: rs[5]['harvest']['capture_stack']['measurement_boundary_label'].__setitem__('rails', ['cpu_power', 'ane_power'])))
# F8: no knee
sc = deepcopy(base['scan']); sc.update(K=None, status='knee not found', B=None, Bc1=None, Bc3=None, Bc2=None, phi=None)
read('F8_knee_not_found', scan=sc, show=("r['share']", "r['gpu_power_contrast_w']", "r['phi']", "r['sizes']", "{k: r['boundaries']['rails'].get(k) for k in ('delta','arms','epsilon_flip')}"))
# Zero-width interval and F9 formats (hand-set; the reader cannot produce a zero half-width from these inputs)
for v, hw in ((0., 0.), (0.1+0.2, 0.), (0., .000996), (0.0003, 0.00057), (5., 150.)):
    c = p.classify(v, hw, 1/64)
    pr = p.printed_record({'share': {'f': 'x'}, 'stack_comparisons': [], 'boundaries': {'rails': {'delta': v, 'halfwidth': hw, **c}}})
    print(f'[F9 hand-set {v} ± {hw}] class={c["class"]} contrast={pr["contrasts"]["rails"]!r} line={pr["claim_lines"].get("rails")}')
