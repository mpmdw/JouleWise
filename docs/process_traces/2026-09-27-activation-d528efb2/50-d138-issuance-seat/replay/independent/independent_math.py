# Independent Student-t inversion: integrate the binomial density after
# u=t/sqrt(nu+t^2); pi uses Gauss-Legendre AGM. No repository imports.
from decimal import Decimal as D, getcontext, ROUND_HALF_EVEN
import json, math
from pathlib import Path
getcontext().prec=80;getcontext().rounding=ROUND_HALF_EVEN
x=D(1); y=D(1)/D(2).sqrt(); z=D(1)/4; multiplier=D(1)
for _ in range(9):
 nx=(x+y)/2; y=(x*y).sqrt(); z-=multiplier*(x-nx)**2; x=nx; multiplier*=2
pi=(x+y)**2/(4*z)
def cdf(t):
 u=t/(D(11)+t*t).sqrt()
 # integral_0^u (1-v^2)^(9/2) dv, termwise binomial expansion
 coefficient=D(1); power=u; total=u; j=0
 while True:
  j+=1; coefficient*=-(D('4.5')-j+1)/j;power*=u*u
  term=coefficient*power/(2*j+1);total+=term
  if abs(term)<D('1e-85'):break
  assert j<2000
 return D('.5')+D(256)/(63*pi)*total
def quantile(p):
 lo=D(0);hi=D(10)
 for _ in range(280):
  mid=(lo+hi)/2
  if cdf(mid)<p:lo=mid
  else:hi=mid
 return (lo+hi)/2
root=Path.cwd(); artifact=json.loads((root/'configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json').read_bytes())
b=[D(m['b_fiducial_s']) for m in artifact['derivation_corpus']['members']];assert len(b)==12
mean=sum(b)/len(b);sd=(sum((v-mean)**2 for v in b)/(len(b)-1)).sqrt()
mean_p=mean.quantize(D('1e-18'));sd_p=sd.quantize(D('1e-18'))
st=artifact['decimal_derivation']['source_statistics']; qd=artifact['decimal_derivation']['two_draw_prediction_derivation']
assert str(mean_p)==st['mean_presentation_s']['value'];assert str(sd_p)==st['sample_sd_presentation_s']['value']
print('precision=80; pi AGM=',pi)
print('minimum=',min(b),'maximum=',max(b),'range=',max(b)-min(b),'mean=',mean,'sample_sd=',sd)
preds={}
for p,tag,lab in [(D('.975'),'t_975_quantile','95'),(D('.995'),'t_995_quantile','99')]:
 q=quantile(p);published=q.quantize(D('1e-20'));assert str(published)==qd[tag]
 residual=abs(cdf(q)-p);assert residual<D('1e-75')
 pred=repr(float(q)*float(sd_p)*math.sqrt(2));assert pred==st['prediction_'+lab+'_two_draw_s'];preds[lab]=D(pred)
 print('p=',p,'independent_t=',q,'published=',published,'CDF_residual=',residual,'binary64_prediction=',pred)
pre=json.loads((root/'configs/calibration/calibration_acceptance_d079_v2_n17_r7.json').read_bytes())
S=max((max(b)-min(b)).quantize(D('1e-6')),D('.010818'))
C=max(D(pre['decimal_derivation']['ratified_operatives']['maximum_budgetable_drift_s']),preds['99'],S)
level=max(b).quantize(D('1e-15'))
ops={'bracket_screen_s':S,'maximum_budgetable_drift_s':C,'preflight_level_screen_s':level,'max_budgetable_excess_s':C-S}
for k,v in ops.items():
 assert str(v)==artifact['decimal_derivation']['ratified_operatives'][k],(k,v)
 assert str(v)==artifact['registered_generation_row']['operatives'][k]
 print(k,str(v),'EXACT PRINTED-DIGIT MATCH')
print('iii INDEPENDENT STATISTICS PASS')
