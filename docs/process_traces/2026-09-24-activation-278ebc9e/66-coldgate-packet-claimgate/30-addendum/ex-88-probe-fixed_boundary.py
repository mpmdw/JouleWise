import math,random,statistics
from probe import MODELS,SEED,old_actual,new_draw,student_t_quantile
so=statistics.stdev(old_actual);mu=statistics.mean(old_actual);margin=3.5*so
for model in MODELS:
 rng=random.Random(SEED+1000+MODELS.index(model));hits=0
 for _ in range(20000):
  new=new_draw(rng,model,12,margin,1);sn=statistics.stdev(new)
  se=math.sqrt(so*so/len(old_actual)+sn*sn/len(new))
  hits+=abs(statistics.mean(new)-mu)+student_t_quantile(.95,11)*se<margin
 print(model,'fixed-old boundary false-equivalence',round(hits/20000,4))
