import collections,ctypes,json,math,os,random,statistics,sys
from pathlib import Path
from models import *
lib=ctypes.CDLL(os.environ['CLAIMGATE_PERM_LIB'])
lib.perm_p.argtypes=[ctypes.POINTER(ctypes.c_double),ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_uint64]
lib.perm_p.restype=ctypes.c_double

def fast_p(rng,old,new):
 # Translation is immaterial to variance and reduces cancellation.
 values=[x-grand for x in old+new]
 return lib.perm_p((ctypes.c_double*len(values))(*values),len(old),len(new),2000,rng.getrandbits(64) or 1)

def windows(old):
 means=[]; i=0
 for n in sizes:means.append(statistics.mean(old[i:i+n]));i+=n
 return means

def ci(c,n):
 z=1.96;p=c/n;d=1+z*z/n;mid=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return [round(mid-h,6),round(mid+h,6)]

def run_claims(N):
 for w in (.5,1.,2.):
  for model in MODELS:
   for k in (5,8):
    rng=random.Random(278910+MODELS.index(model)*100+k+int(w*1000));c=collections.Counter()
    for trial in range(N):
     F=floor([envelope(rng,model,6,w) for _ in range(k)])
     Delta=F+w+2.0  # registered after calibration, before analysis observations
     for delta in (0,2,5):
      vals=[envelope(rng,model,6,w,delta) for _ in range(k)]
      d,eq,_,_,_=verdict(vals,F,w,Delta=Delta)
      c[str(delta)]+=d
      c['equivalence_'+str(delta)]+=eq
     boundary=[envelope(rng,model,6,w,Delta) for _ in range(k)]
     c['equivalence_boundary']+=verdict(boundary,F,w,Delta=Delta)[1]
    print(json.dumps(dict(kind='claim',model=model,k=k,w=w,N=N,counts=dict(c),rates={d:c[d]/N for d in ('0','2','5')},equivalence_rates={d:c['equivalence_'+d]/N for d in ('0','2','5')},equivalence_boundary_false_admission=c['equivalence_boundary']/N,registered_margin_rule='Delta=F_est+B+2sigma',null_CI=ci(c['0'],N))),flush=True)

def run_nights(N):
 sw=statistics.stdev(windows(old_actual));so=statistics.stdev(old_actual);crit=student_t_quantile(.95,9)
 level=32.898493715362
 print(json.dumps(dict(kind='constants',grand=grand,wbar=statistics.mean(windows(old_actual)),sw=sw,so=so,margin=3.5*so,halfwidth=crit*sw*math.sqrt(1.1),within=within,between=between)),flush=True)
 for variant in ('fixed','simulated'):
  for m in (8,12):
   for model in MODELS:
    for state in ('null','boundary','plus3','plus5','times4','times16'):
     n=N if variant=='fixed' and state in ('null','boundary') else max(1000,N//5)
     seed=278911+10000*(variant=='simulated')+1000*m+100*MODELS.index(model)+('null','boundary','plus3','plus5','times4','times16').index(state)
     rng=random.Random(seed);prng=random.Random(seed+800000);c=collections.Counter()
     for trial in range(n):
      old=old_actual if variant=='fixed' else old_draw(rng,model)
      ow=windows(old);s=statistics.stdev(old);margin=3.5*s
      # Simulated variant boundary is its realized margin, as in addendum.
      shift={'null':0,'boundary':margin,'plus3':3*so,'plus5':5*so,'times4':0,'times16':0}[state]
      vm={'times4':4,'times16':16}.get(state,1)
      new=new_draw(rng,model,m,shift,vm)
      loc=abs(statistics.mean(new)-statistics.mean(ow))+crit*statistics.stdev(ow)*math.sqrt(1.1)<margin
      lev=statistics.median(new)<=level
      sp=fast_p(prng,old,new)>=.05
      c['location_fail']+=not loc;c['level_fail']+=not lev;c['spread_fail']+=not sp;c['fail']+=not(loc and lev and sp)
     print(json.dumps(dict(kind='night',variant=variant,model=model,m=m,state=state,N=n,rates={x:c[x]/n for x in ('location_fail','level_fail','spread_fail','fail')},pass_rate=1-c['fail']/n,fail_CI=ci(c['fail'],n),pass_CI=ci(n-c['fail'],n))),flush=True)

if __name__=='__main__':
 if sys.argv[1]=='claims':run_claims(int(sys.argv[2]))
 elif sys.argv[1]=='nights':run_nights(int(sys.argv[2]))
 elif sys.argv[1]=='validate':
  rng=random.Random(7)
  for vm in (1,4,16):
   new=new_draw(rng,'gaussian',12,0,vm)
   slow=permutation_p(random.Random(8),old_actual,new,20000)
   fast=statistics.mean(fast_p(random.Random(8+j),old_actual,new) for j in range(10))
   assert abs(slow-fast)<.025,(slow,fast)
   print('permutation_validation',vm,round(slow,4),round(fast,4))
