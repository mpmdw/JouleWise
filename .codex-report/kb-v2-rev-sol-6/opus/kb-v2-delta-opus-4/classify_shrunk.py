"""Classify leafwalk shrink flags. Usage: python3.13 -B classify_shrunk.py leafwalk6.json"""
import json, re, sys, collections
rs = json.load(open(sys.argv[1]))
rs = rs if isinstance(rs, list) else rs.get('results', rs)
def kind(leaf, mode):
    if 'battery_edge_j' in leaf and mode == 'negative': return 'DEFECT finding 1: negative battery edge energy'
    if re.search(r'idle\.(pre|post)\.(rails|gpu)$', leaf) and mode == 'long': return 'DEFECT finding 3: duplicated rails/GPU interval (overlap)'
    if re.fullmatch(r'records\.\d+', leaf): return 'artefact: index-wise comparison after deleting a record'
    if mode == 'zero': return 'valid zero'
    return 'changed collection (row dropped, duplicate poll stamp, gap list changed, short list)'
c = collections.Counter(kind(r['leaf'], r['mode']) for r in rs if r.get('shrunk'))
for k, v in c.most_common(): print(f'{v:5d} {k}')
print('total', sum(c.values()))
