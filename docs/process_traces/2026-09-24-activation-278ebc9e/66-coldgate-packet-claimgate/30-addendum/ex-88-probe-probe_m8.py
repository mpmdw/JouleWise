import collections, functools, json, math, pathlib, random, statistics, sys
sys.path.insert(0,'/Users/edr/code/wt-278ebc9e-cg-sol')
sys.dont_write_bytecode=True
from joulewise.analysis_engine.estimators import PairedObservation,DeterministicBoundTerm,estimate_paired_blocks,tost_p_value
from joulewise.analysis_engine import estimators
from joulewise.analysis_engine.distributions import student_t_quantile,student_t_cdf
from joulewise.analysis_engine.multiplicity import holm_adjust
from joulewise.detection_floor import small_sample_guard_factor
estimators.student_t_quantile=functools.lru_cache(None)(estimators.student_t_quantile)
student_t_quantile=functools.lru_cache(None)(student_t_quantile)
MODELS=('gaussian','heavy_t3','linear_drift','shared_local')
SEED=278013

def local(rng,model,n):
 if model=='heavy_t3': x=[rng.gauss(0,1)/math.sqrt(rng.gammavariate(1.5,2/3)*3) for _ in range(n)]
 else: x=[rng.gauss(0,1) for _ in range(n)]
 if model=='linear_drift': x=[v+1.5*(i-(n-1)/2)/max(n-1,1) for i,v in enumerate(x)]
 if model=='shared_local': x=[v/math.sqrt(2) for v in x]
 return x

def envelope(rng,model,n,w,delta=0):
 shock=rng.gauss(0,1/math.sqrt(2) if model=='shared_local' else 0.5)
 timing=rng.uniform(-w/2,w/2) if model=='shared_local' else 0
 xs=local(rng,model,n)
 if model=='shared_local':xs=[x+rng.uniform(-w/2,w/2) for x in xs]
 return delta+statistics.mean(xs)+shock+timing

def floor(cal):
 n=len(cal);return small_sample_guard_factor(n)*(abs(statistics.mean(cal))+student_t_quantile(.975,n-1)*statistics.stdev(cal)/math.sqrt(n))

def verdict(vals,F,w,m=5,Delta=3):
 obs=[PairedObservation(str(i),0,x,deterministic_terms=(DeterministicBoundTerm('timing',0,w),)) for i,x in enumerate(vals)]
 e=estimate_paired_blocks(obs);h=student_t_quantile(.975,e.df)*e.se_total;h90=student_t_quantile(.95,e.df)*e.se_total
 hp=holm_adjust({'target':e.raw_p,**{f'miss{i}':None for i in range(1,m)}},m=m)['target']
 direction=hp<.05 and e.estimate-h-w>0 and e.estimate>F
 eqp=tost_p_value(e.estimate,e.se_total,e.df,Delta-F)[2] if Delta>F else 1
 eqa=holm_adjust({'target':eqp,**{f'miss{i}':None for i in range(1,m)}},m=m)['target']
 equivalence=Delta>=F+w and abs(e.estimate)+h90+w<Delta-F and eqa<.05
 return direction,equivalence,e,F,h

def claims(trials=1000):
 print('CLAIM trials/cell',trials,'seed',SEED,'w=0.5; cal_k=analysis_k; six blocks/envelope; Holm m=5 target plus 4 missing')
 for model in MODELS:
  for k in (5,8):
   rng=random.Random(SEED+MODELS.index(model)*100+k)
   c=collections.Counter(); floor_sum=0
   for _ in range(trials):
    cal=[envelope(rng,model,6,.5) for _ in range(k)];F=floor(cal);floor_sum+=F
    for delta in (0,2,3,5):
     vals=[envelope(rng,model,6,.5,delta) for _ in range(k)]
     d,eq,e,_,_=verdict(vals,F,.5)
     c[f'd{delta}']+=d;c[f'e{delta}']+=eq
   print(model,k,'mean_F',round(floor_sum/trials,3),*(f'{key}={c[key]/trials:.3f}' for key in ('d0','d2','d5','e0','e3','e5')))

p=pathlib.Path('/Users/edr/code/wt-278ebc9e-cg-sol/configs/calibration/calibration_acceptance_d079_v2_n17_r7.json')
rows=json.loads(p.read_text())['derivation_corpus']['members'];groups=collections.defaultdict(list)
for row in rows:groups[pathlib.Path(row['source_directory']).parts[0]].append(float(row['b_fiducial_s'])*1000)
sizes=[len(v) for v in groups.values()];old_actual=[v for vs in groups.values() for v in vs]
within=sum((len(v)-1)*statistics.variance(v) for v in groups.values() if len(v)>1)/(len(old_actual)-len(groups))
grand=statistics.mean(old_actual);msb=sum(len(v)*(statistics.mean(v)-grand)**2 for v in groups.values())/(len(groups)-1)
n0=(len(old_actual)-sum(n*n for n in sizes)/len(old_actual))/(len(groups)-1)
between=max(0,(msb-within)/n0)

def old_draw(rng,model):
 out=[]
 for n in sizes:
  shock=rng.gauss(0,math.sqrt(between));xs=local(rng,model,n)
  out.extend(grand+shock+math.sqrt(within)*x for x in xs)
 return out

def new_draw(rng,model,m,shift=0,var_mult=1):
 shock=rng.gauss(0,math.sqrt(between));xs=local(rng,model,m)
 # variance multiplier applies to both between-window shock and local term.
 return [grand+shift+math.sqrt(var_mult)*(shock+math.sqrt(within)*x) for x in xs]

def var(xs):
 n=len(xs);avg=sum(xs)/n;return sum((x-avg)**2 for x in xs)/(n-1)

def permutation_p(rng,old,new,reps):
 n=len(old);pooled=old+new;observed=math.log(var(new)/var(old));hits=0
 for _ in range(reps):
  rng.shuffle(pooled)
  if math.log(var(pooled[n:])/var(pooled[:n]))>=observed-1e-12:hits+=1
 return (hits+1)/(reps+1)

def night(trials=500,perms=2000):
 print('R7 layout',sizes,'within_sd',round(math.sqrt(within),4),'between_sd',round(math.sqrt(between),4),'old_sd',round(statistics.stdev(old_actual),4),'margin',round(3.5*statistics.stdev(old_actual),4))
 print('NIGHT trials/cell',trials,'perms',perms,'m=8; old simulated 10-window random effects; new one window; p=(1+hits)/(1+perms)')
 for model in MODELS:
  rng=random.Random(SEED+400+MODELS.index(model));counts=collections.Counter()
  for state,shift,vm in [('null',0,1),('plus3',3*statistics.stdev(old_actual),1),('plus5',5*statistics.stdev(old_actual),1),('times4',0,4),('times16',0,16)]:
   for _ in range(trials):
    old=old_draw(rng,model);new=new_draw(rng,model,8,shift,vm)
    so=statistics.stdev(old);sn=statistics.stdev(new);se=math.sqrt(so*so/len(old)+sn*sn/len(new));df=min(len(old)-1,len(new)-1)
    loc=abs(statistics.mean(new)-statistics.mean(old))+student_t_quantile(.95,df)*se<3.5*so
    spread=permutation_p(rng,old,new,perms)<.05
    counts[state+'_locpass']+=loc;counts[state+'_spreadfail']+=spread;counts[state+'_fail']+=not loc or spread
   print(model,state,*(f'{key}={counts[state+key]/trials:.3f}' for key in ('_locpass','_spreadfail','_fail')))

if __name__=='__main__':
 claims(int(sys.argv[1]) if len(sys.argv)>1 else 1000)
 night(int(sys.argv[2]) if len(sys.argv)>2 else 500,int(sys.argv[3]) if len(sys.argv)>3 else 2000)
