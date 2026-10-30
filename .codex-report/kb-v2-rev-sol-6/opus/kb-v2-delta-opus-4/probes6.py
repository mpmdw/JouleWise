"""Round-6 probes (synthetic). Usage: python3.13 -B probes6.py /tmp/jw KBDIR
KBDIR: output of r5repro/r3/e2e_nonneg.py (real stream() receipts, non-negative native idle rows).
Every case runs the real `read` CLI in a fresh subprocess on full-size data."""
import json, subprocess, sys, tempfile
from copy import deepcopy
from pathlib import Path
JW, KB = Path(sys.argv[1]), Path(sys.argv[2])
CLI = [sys.executable, '-B', str(JW/'scripts/bytes_stream_test.py')]
base = json.loads((KB/'input_A_knee_found.json').read_text())


def run(payload):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d)/'in.json'; f.write_text(json.dumps(payload))
        p = subprocess.run(CLI+['read', str(f)], capture_output=True, text=True)
    if p.returncode:
        return None, (p.stderr.strip().splitlines() or ['?'])[-1]
    return json.loads(p.stdout), None


B, _ = run(base)
HW = {k: v['halfwidth'] for k, v in B['boundaries'].items()}
print('baseline', {k: (v['class'], v['halfwidth']) for k, v in B['boundaries'].items()})


def case(name, mutate):
    inp = deepcopy(base); mutate(inp)
    r, err = run(inp)
    if err:
        print(f'[{name}] TRACEBACK rc!=0: {err}'); return None
    s = {k: (v['class'], v['halfwidth'] if isinstance(v.get('halfwidth'), float) else None) for k, v in r['boundaries'].items()}
    shrunk = [k for k in s if s[k][1] is not None and s[k][1] < HW[k]]
    print(f'[{name}] rc=0 calls={len(r["calls"])} {s} shrunk={shrunk}')
    for k in s:
        if s[k][0] != B['boundaries'][k]['class']:
            print(f'    {k}: {r["boundaries"][k].get("reason", "")[:160]}')
    return r


def rec(i, *path, value):
    def f(d):
        o = d['records'][i]
        for k in path[:-1]: o = o[k]
        o[path[-1]] = value
    return f


# A. finite accepted inputs whose arithmetic overflows outside idle_statistics
case('tau_s_1e300_rec0', rec(0, 'harvest', 'tau_s', value=1e300))
case('settle_s_1e300_rec0', rec(0, 'receipt', 'settle_s', value=1e300))
def gaps_overflow(d):
    h = d['records'][3]['harvest']
    h.update(meter_gaps=[{'span': 'stream', 'missing_samples': 50}]*2, adapter_max_w=1e308)
case('gap_fsum_overflow_rec3', gaps_overflow)
def anchor_all(d):
    for r in d['records']: r['harvest']['anchor_shift_j'] = 1e308
case('anchor_shift_1e308_all', anchor_all)
case('meter_edge_1e308_rec0', rec(0, 'harvest', 'meter_edge_w', value=[1e308, 1e308]))
case('r_max_1e308_rec0', rec(0, 'harvest', 'r_max_s', value=1e308))
case('energy_rails_1e308_rec0', rec(0, 'harvest', 'energy_j', 'rails', value=1.7e308))

# B. native rails/GPU row overlap with non-decreasing starts and start < end (H2 wording: recorded order)
def overlap(kind, i, row):
    def f(d):
        rows = d['records'][i]['harvest']['idle']['pre'][kind]
        rows[row]['start_ns'] = rows[row-1]['start_ns']   # duplicate start, overlaps previous row fully
    return f
case('rails_row_overlap_prev_rec1', overlap('rails', 1, 300))
case('gpu_row_overlap_prev_rec1', overlap('gpu', 1, 300))
def rails_long_row(d):
    rows = d['records'][1]['harvest']['idle']['pre']['rails']
    rows[0]['end_ns'] = rows[-1]['end_ns']               # row 0 covers the whole span, overlapping all others
case('rails_row0_covers_span_rec1', rails_long_row)

# C. receipt stamps that keep the order but leave the native support short
def pre_start_zero(d):
    d['records'][1]['receipt']['idle_pre_start_ns'] = 0
case('idle_pre_start_ns_0_rec1', pre_start_zero)
def post_end_far(d):
    r = d['records'][1]['receipt']; r['idle_post_end_ns'] = r['idle_post_end_ns']+10**15
case('idle_post_end_far_rec1', post_end_far)

# D. zero stamps on first native rows
case('meter_row0_stamp_0_rec1', rec(1, 'harvest', 'idle', 'pre', 'meter', 0, 'stamp_ns', value=0))
case('rails_row0_start_0_rec1', rec(1, 'harvest', 'idle', 'pre', 'rails', 0, 'start_ns', value=0))
case('battery_samples_row0_0_rec1', rec(1, 'harvest', 'battery_samples', 0, 'stamp_ns', value=0))
case('battery_idle_row0_0_rec1', rec(1, 'harvest', 'idle', 'pre', 'battery', 0, 'stamp_ns', value=0))
case('meter_post_row0_0_rec1', rec(1, 'harvest', 'idle', 'post', 'meter', 0, 'stamp_ns', value=0))

# E. signs
case('battery_edge_neg_small_rec0', rec(0, 'harvest', 'battery_edge_j', value=[-1.0, 0.0]))
def bedge_all(d):
    for r in d['records']: r['harvest']['battery_edge_j'] = [-40.0, -40.0]
r = case('battery_edge_neg_all_calls', bedge_all)
if r: print('    dc halfwidth', r['boundaries']['dc']['halfwidth'], 'baseline', HW['dc'], 'printed', r['printed']['contrasts']['dc'])
case('battery_idle_power_neg_rec0', lambda d: [x.update(power_w=x['power_w']-1) for x in d['records'][0]['harvest']['idle']['pre']['battery']])
case('energy_battery_neg_rec0', rec(0, 'harvest', 'energy_j', 'battery', value=-123.0))
case('energy_gpu_neg_rec0', rec(0, 'harvest', 'energy_j', 'gpu', value=-1.0))
case('energy_meter_neg_rec0', rec(0, 'harvest', 'energy_j', 'meter', value=-1.0))
case('meter_edge_neg_rec0', rec(0, 'harvest', 'meter_edge_w', value=[-1.0, 1.0]))
case('gpu_power_zero_rec0', lambda d: [x.update(power_w=0) for x in d['records'][0]['harvest']['idle']['pre']['gpu']])

# F. H5 disclosure / physical leaves
for leaf, path in [('python', ('receipt', 'stack', 'python')), ('numpy', ('receipt', 'stack', 'packages', 'numpy')),
                   ('kernel_library', ('receipt', 'stack', 'kernel_library')),
                   ('telemetry_backend', ('harvest', 'capture_stack', 'telemetry_backend'))]:
    for val in (None, 7, ''):
        r = case(f'disclosure_{leaf}={val!r}_rec2', rec(2, *path, value=val))
        if r: print('    stack_comparison disclosure', [x for x in r['stack_comparisons'][2]['disclosure_differences']])
def del_stack(d): d['records'][2]['receipt']['stack'] = None
case('stack_null_rec2', del_stack)
case('hardware_unit_str_rec2', rec(2, 'receipt', 'stack', 'hardware_unit', value='m3'))
case('packages_mlx_null_rec2', rec(2, 'receipt', 'stack', 'packages', 'mlx', value=None))
case('runtime_version_name_null_rec2', rec(2, 'receipt', 'stack', 'runtime_version', 'name', value=None))
case('capture_stack_null_rec2', rec(2, 'harvest', 'capture_stack', value=None))
case('mbl_null_rec2', rec(2, 'harvest', 'capture_stack', 'measurement_boundary_label', value=None))
case('rails_label_elem_null_rec2', rec(2, 'harvest', 'capture_stack', 'measurement_boundary_label', 'rails', 1, value=None))

# G. scan status
def scan_set(k, v):
    def f(d): d['scan'][k] = v
    return f
case('scan_status_null', scan_set('status', None))
case('scan_status_7', scan_set('status', 7))
case('scan_status_list', scan_set('status', ['knee found']))
case('scan_status_absent', lambda d: d['scan'].pop('status'))
case('scan_status_knee_not_found_with_K', scan_set('status', 'knee not found'))
def refused_bad(d): d['scan'].update(status='knee not found', K=None)
case('scan_refused_K_null', refused_bad)
def refused_status_null(d): d['scan'].update(status=None, K=None)
case('scan_status_null_K_null', refused_status_null)
# H. inconsistent but individually valid scan sizes
case('scan_B_equals_K', lambda d: d['scan'].update(B=d['scan']['K']))
case('scan_Bc1_equals_Bc2', lambda d: d['scan'].update(Bc1=d['scan']['Bc2']))
