from decimal import Decimal as D, getcontext
import statistics, math, json
getcontext().prec=50
B={'w1-d04':'0.03610911339816257','w1-d05':'0.0247300413330314','w1-d06':'0.02626709931386116','w1-d07':'0.02930916584265009','w1-d10':'0.024377093921897318','w1-d12':'0.02649306058292668','w2-d01':'0.03203051441482298','w2-d03':'0.027705716700833778','w2-d04':'0.03245902112381383','w2-d05':'0.028014781845868017','w2-d09':'0.02952480316956647','w2-d10':'0.03807857930294817'}
t995=3.10580651553928100710; t975=2.20098516009163986788
def stats(b):
    v=list(b.values()); sd=statistics.stdev(v)
    return dict(min=min(v)*1e6,max=max(v)*1e6,range=(max(v)-min(v))*1e6,mean=statistics.mean(v)*1e6,sd=sd*1e6,q99=t995*sd*math.sqrt(2)*1e6,q95=t975*sd*math.sqrt(2)*1e6)
b0={k:float(v) for k,v in B.items()}
print('issued',stats(b0))
r=json.load(open('recon.json'))
b1=dict(b0); b1['w1-d12']-=40.1e-6; b1['w2-d01']-=11.6e-6
s0=stats(b0); s1=stats(b1)
print('cf    ',s1); print('dC us', s1['q99']-s0['q99'])
# alternative: drift term normalized to median freq-> same drift for all members
spans={k:r[k]['span_code_us'] for k in b0}
print('spans',{k:round(v,1) for k,v in spans.items()})
# H6 audit: members with any apply within [start-300, end]
for k in b0:
    v=r[k]; flag=bool(v['inside'] or v['before300'])
    print(k,'H6-excluded' if flag else 'H6-ok', v['inside'], v['before300'])
print('---- drift-term normalisation')
for const in [sum(spans.values())/12, 1434.0, 1505.0, 0.0]:
    b2={k:b0[k]-spans[k]*1e-6+const*1e-6 for k in b0}
    s2=stats(b2); print('const %.1f'%const, 'range %.1f (d %.1f) q99 %.1f (d %.1f) max %.1f min %.1f'%(s2['range'],s2['range']-s0['range'],s2['q99'],s2['q99']-s0['q99'],s2['max'],s2['min']))
