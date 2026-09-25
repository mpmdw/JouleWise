import math,random,statistics
from probe import MODELS,SEED,old_draw,new_draw,student_t_quantile,old_actual
for model in MODELS:
 rng=random.Random(SEED+900+MODELS.index(model));hit=bad=0
 shift=3.5*statistics.stdev(old_actual)
 for _ in range(10000):
  old=old_draw(rng,model);new=new_draw(rng,model,12,shift,1)
  so=statistics.stdev(old);sn=statistics.stdev(new)
  if shift>=3.5*so:
   bad+=1
   se=math.sqrt(so*so/len(old)+sn*sn/len(new))
   hit+=abs(statistics.mean(new)-statistics.mean(old))+student_t_quantile(.95,11)*se<3.5*so
 print(model,'adverse',bad,'loc_false_equiv',round(hit/bad,4) if bad else None)
