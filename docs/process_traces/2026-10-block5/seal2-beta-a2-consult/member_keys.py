# Prints key names and value TYPES only of one member assessment. No values.
import json,sys
m=json.load(open(sys.argv[1]+'/withheld/member-assessments.json'))
print(sorted(m.keys()))
ms=m['members']; k=next(iter(ms)); 
def shape(v,d=0):
    if isinstance(v,dict): return {a:shape(b,d+1) for a,b in v.items()} if d<2 else 'dict'
    if isinstance(v,list): return 'list[%d]'%len(v)
    return type(v).__name__
print(json.dumps(shape(ms[k]),indent=1,sort_keys=True))
