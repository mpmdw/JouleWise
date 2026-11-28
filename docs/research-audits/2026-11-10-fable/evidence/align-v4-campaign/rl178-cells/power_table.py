"""RL-178: superiority power under P4's normal location model at p_sup <= alpha. Exact convolution; rank pmf by quadrature. Synthetic."""
import math
from math import comb
def phi(x): return math.exp(-x*x/2)/math.sqrt(2*math.pi)
def Phi(x): return .5*math.erfc(-x/math.sqrt(2))
def rank_pmf(delta, n=7, lo=-10., hi=10., m=4000):
    pmf=[0.]*(n+1); h=(hi-lo)/m
    for i in range(m+1):
        x=lo+i*h; w=h*(1 if i in (0,m) else 4 if i%2 else 2)/3
        p=Phi(x); d=phi(x-delta)
        for j in range(n+1): pmf[j]+=w*d*comb(n,j)*p**j*(1-p)**(n-j)
    return pmf
def conv(pmf,k):
    out=[1.]
    for _ in range(k):
        new=[0.]*(len(out)+len(pmf)-1)
        for i,a in enumerate(out):
            for j,b in enumerate(pmf): new[i+j]+=a*b
        out=new
    return out
null=rank_pmf(0.)
for K in (22,20,16,11,6):
    n0=conv(null,K)
    row=[]
    for alpha in (.025,.0125):
        tail=0.; c=len(n0)
        for s in range(len(n0)-1,-1,-1):
            if tail+n0[s]<=alpha: tail+=n0[s]; c=s
            else: break
        pw=[sum(conv(rank_pmf(d),K)[c:]) for d in (.5,.75,1.)]
        row.append((alpha,c,round(tail,5),[round(x,3) for x in pw]))
    print(K,row)
