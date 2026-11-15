"""Replay detail for gates whose B1 replay disagrees (F0 run 1): runs deskf0.py in-process (same inputs, same code)
and prints, for each disagreeing gate only, the recorded and replayed outcome/duration/exit sample and the journal
rows (time from gate start, finish time from gate start, TV0h, TV1h, os_level, pm_state) between the two exit samples. Thermal values only.
Usage: python3.13 -B replay_detail.py OUT_COPY SCRATCH_JSON"""
import json, runpy, sys
NS = 10**9
g = runpy.run_path(str(__import__('pathlib').Path(__file__).with_name('deskf0.py')), run_name='__main__')
val, J = g['val'], g['J']
for r in val['rows']:
    if r['agree']:
        continue
    j = J[r['member']]
    gate = next(x for x in j.gates if x['kind'] == r['kind'] and x['turn'] == r['turn'])
    lo = min(e for e in (r['recorded'][2], r['replayed'][2]) if e is not None) - 3 * NS
    hi = max(e for e in (r['recorded'][2], r['replayed'][2]) if e is not None) + NS
    rows = [{'t_from_gate_start_s': round((x['monotonic_ns'] - gate['start_ns']) / NS, 3),
             'finished_from_gate_start_s': round((f - gate['start_ns']) / NS, 3),
             'TV0h': x['sensors'].get('TV0h'), 'TV1h': x['sensors'].get('TV1h'),
             'os_level': (x.get('status') or {}).get('os_level'), 'pm_state': (x.get('status') or {}).get('pm_state'),
             'is_recorded_exit': x['monotonic_ns'] == r['recorded'][2], 'is_replayed_exit': x['monotonic_ns'] == r['replayed'][2]}
            for x, f in zip(j.rows, j.fin) if lo <= x['monotonic_ns'] <= hi]
    print(json.dumps({'member': r['member'], 'kind': r['kind'], 'turn': r['turn'], 'recorded': r['recorded'],
                      'replayed': r['replayed'], 'exit_diff_s': None if None in (r['recorded'][2], r['replayed'][2]) else (r['recorded'][2] - r['replayed'][2]) / NS,
                      'reference_fast_c': gate['reference']['fast_c'], 'band_c': [1.0, 1.0], 'rows': rows}, indent=1))
