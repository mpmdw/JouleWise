# Above-bar field NAMES and COUNTS only; never prints a, t, abs or bar.
import json, sys, collections as C
d = json.load(open(sys.argv[1]))
ab = [r for r in d if r['status'] == 'above_bar']
print('compared', len(d), C.Counter(r['status'] for r in d))
print('above_bar', len(ab), 'by stage', dict(C.Counter(r['stage'] for r in ab)))
print('--- keys', C.Counter(r['key'] for r in ab).most_common())
for g, n in sorted(C.Counter('/'.join(r['group'].split('/')[:4]) for r in ab).items()):
    print(n, g)
print('--- key by kind')
byk = C.defaultdict(C.Counter)
for r in ab:
    p = r['group'].split('/'); k = p[3] if p[0] == 'cell' else p[0] + '/' + p[1]
    byk[k][r['key']] += 1
for k in sorted(byk): print(k, dict(byk[k]))
