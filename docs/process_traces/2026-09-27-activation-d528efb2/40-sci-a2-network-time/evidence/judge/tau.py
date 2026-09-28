import json, math
out=json.load(open('offsets.json')); ev=json.load(open('events.json')); caps={c['short']:c for c in json.load(open('captures.json'))}
def show(short, around=None):
    c=[o for o in out if o['short']==short][0]
    s=c['series']
    print(short,'n',len(s))
    return c,s
# d07: slew -35.939 ms at t_ev ; model: off(t) = a + f_old*t for t<t_ev ; after: a + f_old*t_ev + f_new*(t-t_ev) + A*(1-exp(-(t-t_ev)/tau))
for short,f_old,f_new,A in (('w2-d07',6.199e-6,-244369/65536e6,-35939.097e-6),('w1-d11',6.243e-6,491554/65536e6,4385.948e-6)):
    c,s=show(short)
    cap=caps[short]; t0=cap['stamps']['pre_spawn']['epoch_s']
    e=[x for x in ev if abs(x['adjust']-A)<1e-9][0]
    # series x is monotonic seconds since first stamp (pre_spawn); event time relative
    tev=e['epoch']-t0
    pre=[(x,y) for x,y,r,n in s if x<tev-0.5]
    a=sum(y-f_old*1e6*x for x,y in pre)/len(pre)
    best=None
    for tau10 in range(40,400):
        tau=tau10/10
        sse=0;k=0
        for x,y,r,n in s:
            if x<=tev+0.5: continue
            m=a+f_old*1e6*tev+f_new*1e6*(x-tev)+A*1e6*(1-math.exp(-(x-tev)/tau))
            sse+=(y-m)**2;k+=1
        if best is None or sse<best[0]: best=(sse,tau,k)
    print(short,'event at t0+%.1f s'%tev,'best tau = %.1f s'%best[1],'rms resid = %.1f us over %d points'%(math.sqrt(best[0]/best[2]),best[2]))
    tau=best[1]
    for frac_t in (16,32,64,96,112):
        print('   after %3d s: model fraction delivered %.4f'%(frac_t,1-math.exp(-frac_t/tau)))
# w1-d12 series around the event, and w2-d01 and w1-d01 head
for short in ('w1-d12','w2-d01','w1-d01'):
    c,s=show(short)
    f=c['freq_start_ppm']
    print('   t(s)   offset-minus-freq-line (us)   [first 40 points]')
    base=s[0][1]
    row=[]
    for x,y,r,n in s[:44]:
        row.append('%6.1f:%7.1f'%(x,y-f*x))
    for i in range(0,len(row),6): print('   '+'  '.join(row[i:i+6]))
    tail=[y-f*x for x,y,r,n in s[-10:]]
    print('   last 10 points mean %.1f us'%(sum(tail)/len(tail)))
