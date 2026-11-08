import math
# (window, arm, T_request_s, n_exposed, contention_flags)
cells=[('ALPHA','1.7B dec',2.08,48,0),('ALPHA','1.7B pre',2.96,50,3),
       ('BETA','8B dec',6.77,49,4),('BETA','8B pre',9.82,49,4),
       ('GAMMA','1.7B dec',2.08,20,0),('GAMMA','8B dec',6.77,19,2),('GAMMA','1.7B pre',2.96,18,1),('GAMMA','8B pre',9.82,19,3)]
refs=[('ALPHA','refs+corpus',1.6,25,1),('BETA','refs+corpus',1.6,25,5),('GAMMA','refs+corpus',1.6,27,4)]
def ll(lam,c,cells):
    s=0
    for w,a,T,n,k in cells:
        p=1-math.exp(-lam*(T+c)); p=min(max(p,1e-12),1-1e-12)
        s+=k*math.log(p)+(n-k)*math.log(1-p)
    return s
def mle(c,cells):
    best=max(((ll(l/100000,c,cells),l/100000) for l in range(1,20000)))
    return best
for c in [0,2,5,10]:
    L,lam=mle(c,cells)
    # profile 95% CI
    ci=[l/100000 for l in range(1,20000) if ll(l/100000,c,cells)>=L-1.92]
    print(f'offset c={c:2d}s: lambda={lam:.5f}/s  CI[{ci[0]:.5f},{ci[-1]:.5f}] logL={L:.3f}')
    for w,a,T,n,k in cells: pass
L0,lam0=mle(0,cells)
print('pred vs obs (c=0):')
agg={}
for w,a,T,n,k in cells:
    agg.setdefault(a,[0,0,T]); agg[a][0]+=n; agg[a][1]+=k
for a,(n,k,T) in agg.items(): print(f'  {a}: obs {k}/{n}={k/n:.3f} pred {1-math.exp(-lam0*T):.3f}')
# free c
best=max((ll(l/100000,c/2,cells),l/100000,c/2) for l in range(100,3000,5) for c in range(0,41))
print('free offset MLE: logL %.3f lambda %.5f c %.1f'%best)
# test: refs at 1.6 s under c=0 lambda
p=1-math.exp(-lam0*1.6); n=sum(r[3] for r in refs); k=sum(r[4] for r in refs)
from math import comb
pv=sum(comb(n,j)*p**j*(1-p)**(n-j) for j in range(k,n+1))
print(f'refs+corpus: obs {k}/{n}={k/n:.3f}; pred {p:.4f}; P(>= {k}) = {pv:.2e}')
# per-window lambda c=0
for W in ['ALPHA','BETA','GAMMA']:
    sub=[c for c in cells if c[0]==W]; L,lam=mle(0,sub)
    ci=[l/100000 for l in range(1,20000) if ll(l/100000,0,sub)>=L-1.92]
    print(W,'lambda %.5f CI[%.5f,%.5f]'%(lam,ci[0],ci[-1]))
# 1.7B vs 8B per-second rates
for grp in [('1.7B',),('8B',)]:
    sub=[c for c in cells if c[1].startswith(grp[0])]; L,lam=mle(0,sub)
    ci=[l/100000 for l in range(1,20000) if ll(l/100000,0,sub)>=L-1.92]
    print(grp[0],'lambda %.5f CI[%.5f,%.5f]'%(lam,ci[0],ci[-1]), 'member-seconds', sum(c[2]*c[3] for c in sub), 'flags', sum(c[4] for c in sub))
