import sys, plistlib, statistics
def load(p):
    raw=open(p,'rb').read()
    out=[]
    for chunk in raw.split(b'\x00'):
        chunk=chunk.strip()
        if chunk: out.append(plistlib.loads(chunk))
    return out
for p in sys.argv[1:]:
    ss=load(p)
    el=[s['elapsed_ns']/1e6 for s in ss if 'elapsed_ns' in s][1:]
    el.sort()
    print(f"{p.split('/')[-1]:28s} n={len(el):3d} median={statistics.median(el):7.1f} ms  p05={el[int(.05*len(el))]:7.1f}  p95={el[int(.95*len(el))-1]:7.1f}  max={el[-1]:7.1f}")
