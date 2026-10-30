import json, sys, traceback
from copy import deepcopy
sys.path.insert(0, sys.argv[1])
from scripts import bytes_stream_test as p
base = json.load(open(''+sys.argv[2]+'/input_A_knee_found.json'))
def go(name, f):
    d = deepcopy(base); f(d)
    try:
        r = p.read_known_bytes(d['records'], d['scan']); json.dumps(r, allow_nan=False)
        print(name, 'OK', {k: (v['class'], v.get('halfwidth')) for k, v in r['boundaries'].items()})
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        print(name, type(e).__name__, e, '@', tb.filename.split('/')[-1], tb.lineno, tb.line)
def anchor(d):
    for r in d['records']: r['harvest']['anchor_shift_j'] = 1e308
def bedge(v):
    def f(d):
        for r in d['records']: r['harvest']['battery_edge_j'] = [v, v]
    return f
def gaps(d):
    d['records'][3]['harvest'].update(meter_gaps=[{'span':'stream','missing_samples':50}]*2, adapter_max_w=1e308)
go('tau_s_1e300', lambda d: d['records'][0]['harvest'].update(tau_s=1e300))
go('gap_fsum', gaps)
go('anchor_1e308_all', anchor)
go('anchor_1e308_one', lambda d: d['records'][0]['harvest'].update(anchor_shift_j=1e308))
for v in (-1.0, -10.0, -20.0, -40.0):
    go(f'battery_edge_all_{v}', bedge(v))
go('battery_edge_rec0_-1e6', lambda d: d['records'][0]['harvest'].update(battery_edge_j=[-1e6, 0.0]))
