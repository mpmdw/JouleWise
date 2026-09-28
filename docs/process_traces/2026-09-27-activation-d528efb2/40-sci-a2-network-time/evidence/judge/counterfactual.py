import json, math, statistics
from decimal import Decimal, getcontext
getcontext().prec=40
cand=json.load(open('/Users/edr/code/JouleWise-wt-cg-scia2-d528efb2/docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json'))
B={('w1' if '-w1-' in m['member_id'] else 'w2')+'-'+m['member_id'][-3:]:float(m['b_fiducial_s']) for m in cand['derivation_corpus']['members']}
assert len(B)==12
T995=3.10580651553928100710
def stats(b):
    v=list(b.values()); sd=statistics.stdev(v)
    return dict(min=min(v),max=max(v),rng=max(v)-min(v),mean=statistics.mean(v),sd=sd,q99=T995*sd*math.sqrt(2))
s0=stats(B)
print('as issued      ',{k:round(v*1e6,1) for k,v in s0.items()},'(microseconds)')
# counterfactual A: remove the measured NTP-caused excess from the two touched members
A=dict(B); A['w1-d12']-=40.1e-6; A['w2-d01']-=11.6e-6
sA=stats(A); print('cf A (slews removed)',{k:round(v*1e6,1) for k,v in sA.items()})
print('   change in Q99 (=C): %.2f us ; change in range: %.2f us ; change in max: %.2f us'%((sA['q99']-s0['q99'])*1e6,(sA['rng']-s0['rng'])*1e6,(sA['max']-s0['max'])*1e6))
# counterfactual B: drop the two touched members entirely (diagnostic only; n=10 is below the registered floor of 12)
Bd={k:v for k,v in B.items() if k not in ('w1-d12','w2-d01')}
v=list(Bd.values()); print('cf B (two touched members dropped, n=10, diagnostic): min %.1f max %.1f range %.1f mean %.1f sd %.1f us'%(min(v)*1e6,max(v)*1e6,(max(v)-min(v))*1e6,statistics.mean(v)*1e6,statistics.stdev(v)*1e6))
# span term share of B
caps={c['short']:c for c in json.load(open('captures.json'))}
print('member   B_us   span_us  anchor_bound_us  span/B')
for k,b in B.items():
    c=caps[k]['ca']; print(k,round(b*1e6,1),round(c['wall_minus_monotonic_span_s']*1e6,1),round(c['effective_clock_anchor_bound_s']*1e6,1),'%.1f%%'%(100*c['wall_minus_monotonic_span_s']/b))
# counterfactual C: every member's span term replaced by the largest (1536.8) or by zero -> bounds the whole influence of timed's frequency setting
for label,f in (('all spans set to 0',lambda s:0.0),('all spans set to 1536.8 us',lambda s:1536.8e-6)):
    Cc={k:b-caps[k]['ca']['wall_minus_monotonic_span_s']+f(0) for k,b in B.items()}
    sc=stats(Cc); print('cf C',label,{k:round(v*1e6,1) for k,v in sc.items()})
