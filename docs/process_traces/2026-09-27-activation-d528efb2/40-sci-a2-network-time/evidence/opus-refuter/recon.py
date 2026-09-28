import json, glob, os, re, datetime, math
OUT='/tmp/cg-scia2-d528efb2/opus-refuter/'
# parse timed applies and freq
ev=[]
for f in ['log_w1.txt','log_w2.txt']:
    for l in open(OUT+f):
        m=re.match(r'(\S+ \S+?)([-+]\d{4}) .*?cmd,(apply|ntp_adjtime:in),(.*)',l)
        if not m: continue
        ts=datetime.datetime.strptime(m.group(1)+m.group(2),'%Y-%m-%d %H:%M:%S.%f%z').timestamp()
        kv=m.group(4).split(',')
        d=dict(zip(kv[0::2],kv[1::2]))
        if m.group(3)=='apply':
            ev.append(('apply',ts,d['src'],float(d['adjust'])))
        else:
            ev.append(('freq',ts,None,int(d['freq_scaled'])/65536.0))
ev.sort(key=lambda x:x[1])
applies=[e for e in ev if e[0]=='apply']
freqs=[e for e in ev if e[0]=='freq']
def hm(t): return datetime.datetime.fromtimestamp(t).strftime('%H:%M:%S.%f')[:-3]
res={}
for sess in ['w1','w2']:
    base=f'/Users/edr/night-custody/d079-epoch-25g83-derivation-{sess}-20260927/runs/instrument_validation/'
    for d in sorted(glob.glob(base+'*')):
        slot=d[-3:]
        ie=json.load(open(d+'/instrument_evidence.json')) if os.path.exists(d+'/instrument_evidence.json') else {}
        st=[]
        ca=ie.get('clock_anchor') or {}
        for k,v in (ca.get('clock_stamps') or {}).items():
            st.append((v['epoch_s'],(v['monotonic_before_s']+v['monotonic_after_s'])/2,k))
        if os.path.exists(d+'/events.jsonl'):
            for l in open(d+'/events.jsonl'):
                e=json.loads(l); cs=(e.get('metadata') or {}).get('clock_stamp')
                if cs: st.append((cs['epoch_s'],(cs['monotonic_before_s']+cs['monotonic_after_s'])/2,e['event_type']))
        st.sort(key=lambda x:x[1])
        if not st:
            print(sess,slot,'NO STAMPS',ie.get('status'),ie.get('reasons')); continue
        t0,t1=st[0][0],st[-1][0]
        m0=st[0][1]
        xs=[s[1]-m0 for s in st]; ys=[(s[0]-s[1])*1e6 for s in st]
        y0=ys[0]; ys=[y-y0 for y in ys]
        n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
        sxx=sum((x-mx)**2 for x in xs); sxy=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
        b=sxy/sxx; a=my-b*mx
        maxdev=max(abs(y-(a+b*x)) for x,y in zip(xs,ys))
        fr=[f for f in freqs if f[1]<=t0]; fnow=fr[-1][3] if fr else None
        frin=[f for f in freqs if t0<f[1]<=t1]
        pred=fnow*(xs[-1]) if fnow is not None else None
        inside=[a_ for a_ in applies if t0<=a_[1]<=t1]
        before=[a_ for a_ in applies if t0-300<=a_[1]<t0]
        prev=[a_ for a_ in applies if a_[1]<t0]
        prevms=[a_ for a_ in prev if abs(a_[3])>=1e-3]
        res[f'{sess}-{slot}']=dict(status=ie.get('status'),reasons=ie.get('reasons'),start=hm(t0),end=hm(t1),n=n,span_s=xs[-1],
            moved_us=ys[-1],pred_us=pred,excess_us=(ys[-1]-pred) if pred is not None else None,maxdev_us=maxdev,
            inside=[(hm(x[1]),x[2],round(x[3]*1e6,1)) for x in inside],
            before300=[(hm(x[1]),x[2],round(x[3]*1e6,1),round(t0-x[1],1)) for x in before],
            last_ms=(hm(prevms[-1][1]),round(prevms[-1][3]*1e6,1),round(t0-prevms[-1][1],1)) if prevms else None,
            freq_ppm=fnow, freq_changes_inside=[(hm(f[1]),f[3]) for f in frin],
            span_code_us=(ca.get('wall_minus_monotonic_span_s') or 0)*1e6, eff_bound_us=(ca.get('effective_clock_anchor_bound_s') or 0)*1e6,
            allowance=ca.get('model_departure_allowance_s'), B=ie.get('b_fiducial_s'), clock_status=ca.get('status'))
json.dump(res,open(OUT+'recon.json','w'),indent=1)
for k,v in res.items():
    print(k, v['status'], v['clock_status'], v['start'],'-',v['end'], 'n',v['n'], 'mv %.1f pred %.1f ex %.1f dev %.1f'%(v['moved_us'],v['pred_us'],v['excess_us'],v['maxdev_us']),
          'span %.1f eb %.1f'%(v['span_code_us'],v['eff_bound_us']), 'B',v['B'])
    print('    inside',v['inside'],'| before300',v['before300'],'| last_ms',v['last_ms'],'| freq',round(v['freq_ppm'],3), v['freq_changes_inside'], v['reasons'])
