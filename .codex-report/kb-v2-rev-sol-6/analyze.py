import json,collections,re,gzip
from pathlib import Path
D=Path(__file__).parent
rows=json.loads((D/'walk-issues.json').read_text() if (D/'walk-issues.json').exists() else gzip.open(D/'walk-issues.json.gz','rt').read())
def key(r):
 path='.'.join(map(str,r['path']));path=re.sub(r'\.\d+(?=\.|$)','.N',path)
 return path,r['mode']
print('diagnostic rows',len(rows),'crashes',sum('crash' in r for r in rows),'shrink flags',sum(bool(r.get('shrunk')) for r in rows))
print('SHRINK GROUPS:')
for k,n in collections.Counter(key(r) for r in rows if r.get('shrunk')).most_common(): print(n,k)
print('UNNAMED AND CLASS CHANGED GROUPS:')
for k,n in collections.Counter(key(r) for r in rows if not r.get('named') and set(r.get('classes',{}).values())!={'RESOLVED'}).most_common(): print(n,k)
print('MALFORMED MODE SHRINKS:',[r for r in rows if r.get('shrunk') and r['mode'] in ('deleted','null','wrong_type','non_finite','wrong_length','huge_int','nan_string','inf','minus_inf','bool','overlap','duplicate_start','empty_interval','reversed_interval','poll_order')])
