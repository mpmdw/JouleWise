import sys, json, subprocess
def keys(o, depth=0, maxdepth=6):
    if isinstance(o, dict):
        return {k: keys(v, depth+1) if depth < maxdepth else '...' for k, v in o.items()}
    if isinstance(o, list):
        return [keys(o[0], depth+1)] if o else []
    return type(o).__name__
mode = sys.argv[1]; p = sys.argv[2]
if mode == 'rich':
    out = subprocess.run(['zstd','-dc',p],capture_output=True).stdout.decode().splitlines()
    print(len(out)); print(json.dumps(keys(json.loads(out[0])),indent=1)); print(json.dumps(keys(json.loads(out[-1])))[:300])
elif mode == 'events':
    ev=[json.loads(l) for l in open(p)]
    print(len(ev)); 
    seen=set()
    for e in ev:
        k=json.dumps(keys(e),sort_keys=True)
        if k not in seen: seen.add(k); print(k)
elif mode == 'clock':
    m=json.load(open(p))
    print(json.dumps(keys(m['uncertainty_evidence']['clock_anchor']),indent=1))
    print(list(m.keys()))
