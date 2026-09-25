import math,random,statistics
from probe import MODELS,SEED,old_actual,new_draw,student_t_quantile,permutation_p
so=statistics.stdev(old_actual);mu=statistics.mean(old_actual);margin=3.5*so;N=500
for model in MODELS:
 rng=random.Random(SEED+1100+MODELS.index(model));location=spread=joint=0
 for _ in range(N):
  new=new_draw(rng,model,12,margin,1);sn=statistics.stdev(new)
  se=math.sqrt(so*so/len(old_actual)+sn*sn/len(new))
  l=abs(statistics.mean(new)-mu)+student_t_quantile(.95,11)*se<margin
  s=permutation_p(rng,old_actual,new,2000)>=.05
  location+=l;spread+=s;joint+=l and s
 print(model,'fixed-old boundary',f'location={location/N:.3f}',f'spread_pass={spread/N:.3f}',f'joint_false_PASS={joint/N:.3f}')
