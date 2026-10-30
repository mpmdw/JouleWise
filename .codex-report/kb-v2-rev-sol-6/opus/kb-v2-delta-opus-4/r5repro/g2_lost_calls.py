"""G2: every lost-call position x loss mode; only the lost call's arm may lose its reduction.
Usage: python3.13 -B g2_lost_calls.py /tmp/jw KBDIR  (reuses leafwalk.py's thinned base)."""
import sys
from pathlib import Path
src = (Path(__file__).parent/'leafwalk.py').read_text().split("if __name__")[0]
sys.argv = ['x', sys.argv[1], sys.argv[2], '/dev/null']
exec(src)
base = read(BASE)
ARMS = ('S', 'C1', 'C3', 'C2')
order = ['S', 'C1', 'C3', 'C2', 'C2', 'C3', 'C1', 'S']
modes = {'popped': lambda d, i: d['records'].pop(i), 'empty_record': lambda d, i: d['records'].__setitem__(i, {}),
         'receipt_null': lambda d, i: d['records'][i].__setitem__('receipt', None),
         'repeats_null': lambda d, i: d['records'][i]['receipt'].__setitem__('repeats', None),
         'harvest_null': lambda d, i: d['records'][i].__setitem__('harvest', None),
         'rails_energy_null': lambda d, i: d['records'][i]['harvest']['energy_j'].__setitem__('rails', None)}
bad = 0
for mname, f in modes.items():
    for i in range(8):
        d = deepcopy(BASE); f(d, i); o = read(d)
        for beta in ('rails', 'gpu', 'dc', 'rest'):
            arms = o['boundaries'][beta].get('arms')
            if not isinstance(arms, dict):
                print('NO ARMS', mname, i, beta, o['boundaries'][beta].get('reason')); bad += 1; continue
            needs = (mname != 'rails_energy_null') or beta in ('rails', 'rest')
            for a in ARMS:
                same = arms[a] == base['boundaries'][beta]['arms'][a]
                expect_same = not (needs and a == order[i])
                if same != expect_same:
                    bad += 1; print('MISMATCH', mname, i, beta, a, 'same' if same else 'changed')
        print(f'{mname:18s} pos {i} ({order[i]}): classes', {k: v['class'][:5] for k, v in o['boundaries'].items()},
              'S raw', 'raw_stream_j_per_byte' in o['boundaries']['dc'])
print('G2 mismatches:', bad)
