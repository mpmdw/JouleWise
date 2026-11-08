import math, random
from math import comb
lam=0.01206; lo,hi=0.00720,0.01874
ep_s=(1800-516.575)/1.13544; act=ep_s-300
print('episode_s %.0f, active (minus 300 s idle) %.0f'%(ep_s,act))
for T in [act, 600, 300, 60, 30, 10]:
    print(f'T={T:6.0f}s  P(flag under B5 0.05/10s rule)={1-math.exp(-lam*T):.4f}  [{1-math.exp(-lo*T):.4f},{1-math.exp(-hi*T):.4f}]')
def pbin(n,p,k): return sum(comb(n,j)*(1-p)**j*p**(n-j) for j in range(k,n+1))
print('P(m>=39 of 56) per pair, iid member loss p:')
for p in [0,0.02,0.05,0.10,0.1375,0.15,0.20,0.25,0.30,0.35,0.5,0.99]:
    a=pbin(56,p,39); print(f'  p={p:.4f}: one pair {a:.4f}  both pairs (indep) {a*a:.4f}')
# whole-window loss probability w (U1 bar or lost window) plus iid p
def sim(p,w,N=200000,seed=1):
    r=random.Random(seed); ok=0
    for _ in range(N):
        good=True
        lostw=[r.random()<w for _ in range(8)]
        for pair in range(2):
            m=sum(sum(1 for _ in range(7) if r.random()>=p) for k in range(8) if not lostw[k])
            if m<39: good=False
        ok+=good
    return ok/N
for p,w in [(0.05,0.0),(0.05,1/8),(0.10,1/8),(0.10,0.25),(0.1375,1/8),(0.05,0.25),(0.0,0.25),(0.0,3/8)]:
    print(f'p={p} window-loss w={w:.3f}: P(both pairs >=39)={sim(p,w,40000):.3f}')
