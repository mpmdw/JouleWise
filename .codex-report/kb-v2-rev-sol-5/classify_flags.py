import json,collections,gzip
from pathlib import Path
R=Path(__file__).resolve().parent;data=json.loads((R/'leafwalk.json').read_text()) if (R/'leafwalk.json').exists() else json.load(gzip.open(R/'leafwalk.json.gz','rt'))
flags=[x for x in data if 'shrunk' in x]
print('cases',len(data),'crashes',sum('crash' in x for x in data),'lost_calls',sum('lost_calls' in x for x in data),'shrunk',len(flags))
print('shrunk modes',dict(collections.Counter(x['mode'] for x in flags)))
groups={}
for x in flags:
 leaf,mode=x['leaf'],x['mode']
 # Inspect a distinct representative per family rather than trust the flag name.
 group='.'.join(k for k in leaf.split('.') if not k.isdigit())+' '+mode
 groups.setdefault(group,x)
for k,x in groups.items():print(k,':',x['shrunk'][:2],x['classes'])
assert not any('crash' in x or 'lost_calls' in x or x.get('cli_rc',0) or x.get('cli_same_classes') is False for x in data)
