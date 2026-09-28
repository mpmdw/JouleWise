import json,glob,os
def stamps(d):
    st=[]
    ie=json.load(open(d+'/instrument_evidence.json'))
    for k,v in ((ie.get('clock_anchor') or {}).get('clock_stamps') or {}).items():
        st.append((v['epoch_s'],(v['monotonic_before_s']+v['monotonic_after_s'])/2))
    for l in open(d+'/events.jsonl'):
        e=json.loads(l); cs=(e.get('metadata') or {}).get('clock_stamp')
        if cs: st.append((cs['epoch_s'],(cs['monotonic_before_s']+cs['monotonic_after_s'])/2))
    st.sort(key=lambda x:x[1]); m0=st[0][1]; y0=st[0][0]-st[0][1]
    return [(s[1]-m0,(s[0]-s[1]-y0)*1e6) for s in st]
def minimax(pts):
    # ternary search over slope of max residual range/2
    def f(b):
        r=[y-b*x for x,y in pts]; return (max(r)-min(r))/2
    lo,hi=-100,100
    for _ in range(200):
        m1=lo+(hi-lo)/3; m2=hi-(hi-lo)/3
        if f(m1)<f(m2): hi=m2
        else: lo=m1
    return f((lo+hi)/2),(lo+hi)/2
for g in ['w1-20260927-d01','w1-20260927-d12','w2-20260927-d01','w1-20260927-d04','w1-20260927-d11','w2-20260927-d07']:
    sess=g[:-4]
    d=f'/Users/edr/night-custody/d079-epoch-25g83-derivation-{sess}/runs/instrument_validation/d079-epoch-25g83-derivation-{g}'
    p=stamps(d); e,b=minimax(p)
    # first-minute bend: deviation from freq line
    print(g,'minimax half-range %.1f us slope %.4f ppm'%(e,b))
