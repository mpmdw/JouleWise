"""Round-5 targeted probes (synthetic). Usage: python3.13 -B probes.py /tmp/jw KBDIR
KBDIR holds input_A_knee_found.json from kb-v2-delta-opus-2/r3/e2e.py (real stream() receipts).
Each case runs the real `read` or `scan` CLI in a fresh subprocess."""
import json, subprocess, sys, tempfile
from copy import deepcopy
from pathlib import Path
JW, KB = Path(sys.argv[1]), Path(sys.argv[2])
CLI = [sys.executable, '-B', str(JW/'scripts/bytes_stream_test.py')]
base = json.loads((KB/'input_A_knee_found.json').read_text())

def run(mode, payload, text=None):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d)/'in.json'; f.write_text(text if text is not None else json.dumps(payload))
        p = subprocess.run(CLI+[mode, str(f)], capture_output=True, text=True)
    if p.returncode:
        return p.returncode, (p.stderr.strip().splitlines() or ['?'])[-1], None
    return 0, '', json.loads(p.stdout)

def summary(r):
    b = r['boundaries']
    return {k: (v['class'], v.get('halfwidth') if isinstance(v.get('halfwidth'), float) else None) for k, v in b.items()}

rc, err, B = run('read', base)
print('baseline', rc, summary(B))
def case(name, mutate, mode='read', text=None):
    inp = deepcopy(base); mutate(inp)
    rc, err, r = run(mode, inp, text)
    if rc:
        print(f'[{name}] CLI rc={rc} TRACEBACK: {err}'); return
    if mode == 'scan':
        print(f'[{name}] rc=0 status={r["status"]} reason={r.get("reason")}'); return
    s = summary(r)
    shrunk = [k for k in s if s[k][1] is not None and B['boundaries'][k].get('halfwidth') and s[k][1] < B['boundaries'][k]['halfwidth']]
    print(f'[{name}] rc=0 calls={len(r["calls"])} {s} shrunk={shrunk}')
    for k in s:
        if s[k][0] == 'UNDETERMINED':
            print(f'    {k}: {r["boundaries"][k]["reason"][:150]}')
    return r

def setp(path, value):
    def f(inp):
        o = inp
        for k in path[:-1]: o = o[k]
        o[path[-1]] = value
    return f

# 1. integers beyond binary64 (valid JSON) reach math.isfinite
case('huge_int_start_ns_rec0', setp(['records',0,'receipt','start_ns'], 10**400))
case('huge_int_idle_stamp', setp(['records',2,'harvest','idle','pre','meter',0,'stamp_ns'], 10**400))
case('huge_int_scan_K', setp(['scan','K'], 10**400))
receipts = [json.loads(p.read_text()) for p in sorted(KB.glob('receipt_*.json'))]
sc = deepcopy(receipts[:6])
for i, s in enumerate((16, 32)):
    for j in range(3): sc[3*i+j].update(bytes_per_read=s)
sc[0]['start_ns'] = 10**400
rc, err, r = run('scan', None, json.dumps(sc)); print('[huge_int_scan_receipt]', rc, err or (r['status'], r.get('reason')))
sc[0]['start_ns'] = 0; sc[0]['repeats'] = 10**400
rc, err, r = run('scan', None, json.dumps(sc)); print('[huge_int_scan_repeats]', rc, err or (r['status'], r.get('reason')))

# 2. finite inputs whose arithmetic overflows
case('power_1e308_idle_rails', lambda i: [row.update(power_w=1e308) for row in i['records'][1]['harvest']['idle']['pre']['rails']])
case('energy_1e308_dc_meter', setp(['records',1,'harvest','energy_j','meter'], 1.7e308))

# 3. physically fixed signs and orders the accessor does not check
def rev_rail(i):
    row = i['records'][1]['harvest']['idle']['pre']['rails'][5]
    row['start_ns'], row['end_ns'] = row['end_ns'], row['start_ns']
case('idle_rails_row_end_before_start', rev_rail)
case('idle_rails_negative_power', lambda i: [row.update(power_w=-row['power_w']) for row in i['records'][1]['harvest']['idle']['pre']['rails']])
case('energy_rails_negative', setp(['records',0,'harvest','energy_j','rails'], -50.0))
case('idle_pre_end_before_start', lambda i: i['records'][1]['receipt'].update(idle_pre_end_ns=i['records'][1]['receipt']['idle_pre_start_ns']-1))
case('battery_edge_negative', setp(['records',0,'harvest','battery_edge_j'], [-1.0, 0.0]))
# 4. bool and empty-string leaves
case('repeats_true', setp(['records',3,'receipt','repeats'], True))
case('adapter_source_blank', lambda i: i['records'][3]['harvest'].update(meter_gaps=[{'span':'stream','missing_samples':1}], adapter_source='  '))
case('rails_label_empty_list', setp(['records',4,'harvest','capture_stack','measurement_boundary_label','rails'], []))
case('rails_label_no_gpu_rec7', setp(['records',7,'harvest','capture_stack','measurement_boundary_label','rails'], ['cpu_power','ane_power']))
# 5. top-level containers
case('scan_is_list', setp(['scan'], []))
case('records_is_dict', setp(['records'], {}))
rc, err, r = run('read', None, '[]'); print('[input_is_list]', rc, err or summary(r))
rc, err, r = run('read', None, 'NaN'); print('[input_is_NaN]', rc, err or summary(r))

# 6. orders the physics fixes, inside one call (leaf-walk 'silent'/'shrunk' classes, full-size data)
def bounds(r):
    return {k: r['boundaries'][k].get('halfwidth') for k in r['boundaries']}
def start_before_idle(i):
    i['records'][0]['receipt']['start_ns'] = i['records'][0]['receipt']['idle_pre_start_ns']
r = case('rec0_start_ns_at_idle_pre_start', start_before_idle)
print('    deltas', {k: r['boundaries'][k].get('delta') for k in r['boundaries']}, 'baseline', {k: B['boundaries'][k].get('delta') for k in B['boundaries']})
def rail_end_zero(i):
    i['records'][1]['harvest']['idle']['pre']['rails'][-1]['end_ns'] = 0
r = case('idle_rails_last_row_end_ns_0', rail_end_zero)
print('    call1 rails baseline_bound_j', r['calls'][1]['boundaries']['rails']['baseline_bound_j'], 'baseline', B['calls'][1]['boundaries']['rails']['baseline_bound_j'],
      'pre rails sample_count', r['calls'][1]['native_idle']['pre']['rails']['sample_count'], 'baseline', B['calls'][1]['native_idle']['pre']['rails']['sample_count'])
