"""H4: with each single arm lost, every central coefficient whose prerequisite arms are complete is
printed and is bit-identical to the no-loss value; the rest are absent; r/halfwidth/eps are 'not defined'.
Usage: python3.13 -B h4_arms.py /tmp/jw KBDIR   (KBDIR from r5repro/r3/e2e_nonneg.py)"""
import json, sys
from copy import deepcopy
sys.path.insert(0, sys.argv[1])
from scripts import bytes_stream_test as p
base = json.load(open(sys.argv[2]+'/input_A_knee_found.json'))
B = p.read_known_bytes(deepcopy(base['records']), base['scan'])
ORDER = ['S', 'C1', 'C3', 'C2', 'C2', 'C3', 'C1', 'S']
NEEDS = {'gamma_c': {'C1', 'C2'}, 'alpha': {'C1', 'C2'}, 'gamma_d': {'C1', 'C2', 'S'}, 'delta': {'C1', 'C2', 'S'}}
UNDEF = ('r', 'halfwidth', 'epsilon_flip', 'epsilon_flip_over_alpha')
modes = {'empty_record': lambda d, i: d['records'].__setitem__(i, {}),
         'receipt_null': lambda d, i: d['records'][i].__setitem__('receipt', None),
         'repeats_null': lambda d, i: d['records'][i]['receipt'].__setitem__('repeats', None),
         'rails_energy_null': lambda d, i: d['records'][i]['harvest']['energy_j'].__setitem__('rails', None),
         'meter_energy_null': lambda d, i: d['records'][i]['harvest']['energy_j'].__setitem__('meter', None)}
bad = checked = 0
def check(tag, d, lost):
    global bad, checked
    o = p.read_known_bytes(d['records'], d['scan'])
    json.dumps(o, allow_nan=False)
    for beta, arms_lost in lost.items():
        v = o['boundaries'][beta]
        for key, need in NEEDS.items():
            checked += 1
            if need & arms_lost:
                if isinstance(v.get(key), float):
                    bad += 1; print('UNEXPECTED VALUE', tag, beta, key, v.get(key))
            elif v.get(key) != B['boundaries'][beta][key]:
                bad += 1; print('MISSING/DIFFERENT', tag, beta, key, v.get(key), B['boundaries'][beta][key])
        if arms_lost:
            for key in UNDEF:
                checked += 1
                if not (isinstance(v.get(key), str) and v[key].startswith('not defined (')):
                    bad += 1; print('NOT UNDEFINED', tag, beta, key, v.get(key))
            if v['class'] != 'UNDETERMINED':
                bad += 1; print('CLASS', tag, beta, v['class'])
        printed = o['printed']['contrasts'][beta]
        if 'delta' in v and isinstance(v['delta'], float) and arms_lost and not printed.startswith(str(v['delta'])):
            bad += 1; print('PRINTED', tag, beta, printed[:80])
for mname, f in modes.items():
    for i in range(8):
        d = deepcopy(base); f(d, i)
        arm = {ORDER[i]}
        lost = ({b: arm for b in ('rails', 'gpu', 'dc', 'rest')} if mname in ('empty_record', 'receipt_null', 'repeats_null')
                else {'rails': arm, 'rest': arm, 'gpu': set(), 'dc': set()} if mname == 'rails_energy_null'
                else {'dc': arm, 'rest': arm, 'rails': set(), 'gpu': set()})
        check(f'{mname}@{i}', d, lost)
# two arms lost at once
for i, j in ((0, 2), (2, 1), (5, 0)):
    d = deepcopy(base); d['records'][i] = {}; d['records'][j] = {}
    check(f'empty@{i},{j}', d, {b: {ORDER[i], ORDER[j]} for b in ('rails', 'gpu', 'dc', 'rest')})
print('H4 checks', checked, 'failures', bad)
print('example C3 lost rails printed:', end=' ')
d = deepcopy(base); d['records'][2] = {}
o = p.read_known_bytes(d['records'], d['scan'])
print(o['printed']['contrasts']['rails'][:200])
print({k: o['boundaries']['rails'].get(k) for k in ('gamma_c', 'alpha', 'gamma_d', 'delta', 'r', 'halfwidth', 'class')})
