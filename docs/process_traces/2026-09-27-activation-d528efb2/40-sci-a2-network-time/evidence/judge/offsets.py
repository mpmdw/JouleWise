import json, datetime, sys
from fractions import Fraction
ROOT='/Users/edr/night-custody'
caps=json.load(open('captures.json')); ev=json.load(open('events.json'))
# timed frequency settings in force (freq_scaled / 65536 = ppm), parsed from my log pulls
freqs=[]
for f in ('timed_w1.txt','timed_w2.txt'):
    for line in open(f,errors='replace'):
        if 'cmd,ntp_adjtime:in' in line:
            t=datetime.datetime.strptime(line[:26],'%Y-%m-%d %H:%M:%S.%f')
            epoch=(t-datetime.datetime(1970,1,1)).total_seconds()+7*3600
            kv=line.split('cmd,ntp_adjtime:in,')[1].strip().split(',')
            d=dict(zip(kv[0::2],kv[1::2]))
            freqs.append((epoch,int(d['freq_scaled'])/65536.0,int(d['offset_us'])))
freqs.sort()
def freq_at(e):
    b=[f for f in freqs if f[0]<=e]
    return b[-1][1] if b else None
out=[]
for c in caps:
    sess=c['cid'][:-4]
    p=f"{ROOT}/{sess}/runs/instrument_validation/{c['cid']}/events.jsonl"
    pts=[]
    for l in open(p):
        e=json.loads(l); cs=e['metadata'].get('clock_stamp')
        if cs: pts.append((e['event_type'],cs))
    for k,cs in c['stamps'].items(): pts.append(('anchor:'+k,cs))
    series=[]
    for name,cs in pts:
        m=(cs['monotonic_before_s']+cs['monotonic_after_s'])/2
        hw=(cs['monotonic_after_s']-cs['monotonic_before_s'])/2+max(cs['wall_resolution_s'],cs['monotonic_resolution_s'])
        series.append((m,cs['epoch_s']-m,hw,name,cs['epoch_s']))
    series.sort()
    m0=series[0][0]; o0=series[0][1]
    xs=[s[0]-m0 for s in series]; ys=[(s[1]-o0) for s in series]
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    sl=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)
    ic=my-sl*mx
    res=[y-(sl*x+ic) for x,y in zip(xs,ys)]
    t0=series[0][4]; t1=series[-1][4]
    fin=freq_at(t0); fend=freq_at(t1)
    total=ys[-1]-ys[0]
    pred=fin*1e-6*(xs[-1]-xs[0]) if fin is not None else None
    inside=[e for e in ev if t0<=e['epoch']<=t1]
    c2=dict(short=c['short'],member=c['member'],n=n,dur=xs[-1],slope_ppm=sl*1e6,freq_start_ppm=fin,freq_end_ppm=fend,
        total_drift_us=total*1e6,pred_drift_us=pred*1e6 if pred is not None else None,
        max_abs_resid_us=max(abs(r) for r in res)*1e6,max_hw_us=max(s[2] for s in series)*1e6,
        span_term_us=(c['ca'].get('wall_minus_monotonic_span_s') or float('nan'))*1e6,
        bound_us=(c['ca'].get('effective_clock_anchor_bound_s') or float('nan'))*1e6,
        inside=[(e['ts'][11:23],e['src'],e['adjust']*1e6) for e in inside], series=[(x,y*1e6,r*1e6,nm) for x,y,r,(_,_,_,nm,_) in zip(xs,ys,res,series)])
    out.append(c2)
json.dump(out,open('offsets.json','w'))
print(f"{'cap':7} {'mem':3} {'n':>3} {'slope ppm':>9} {'timed freq ppm':>14} {'drift us':>10} {'freq*dur us':>11} {'drift-pred':>10} {'max|resid| us':>13} {'span term us':>12} {'anchor bound us':>15}  corrections inside")
for c in out:
    print(f"{c['short']:7} {'M' if c['member'] else '-':3} {c['n']:3d} {c['slope_ppm']:9.3f} {c['freq_start_ppm']:14.3f} {c['total_drift_us']:10.1f} {c['pred_drift_us']:11.1f} {c['total_drift_us']-c['pred_drift_us']:10.1f} {c['max_abs_resid_us']:13.1f} {c['span_term_us']:12.1f} {c['bound_us']:15.1f}  {[(a,b,round(x,1)) for a,b,x in c['inside']]}")
