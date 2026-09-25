import collections,random
from probe import MODELS,SEED,envelope,floor,verdict
N=500
for model in MODELS:
 for k in (5,8):
  for w in (.5,1,2):
   rng=random.Random(SEED+2000+MODELS.index(model)*100+k*10+int(w*2));c=collections.Counter()
   for _ in range(N):
    F=floor([envelope(rng,model,6,w) for j in range(k)])
    for effect in (0,2,5):
     v=[envelope(rng,model,6,w,effect) for j in range(k)]
     d,eq,*_=verdict(v,F,w)
     c[effect]+=d
   print(model,k,w,*(f'd{effect}={c[effect]/N:.3f}' for effect in (0,2,5)))
