"""Independent rational recomputation of the worked scan's large-pair comparison.
No production arithmetic is used on the reference side.
"""
from fractions import Fraction as F
import json
from pathlib import Path
import experiment_round4 as e


def exact_reference(rec):
    times={}
    for s in sorted({c['bytes_per_read'] for c in rec}):
        calls=[c for c in rec if c['bytes_per_read']==s]
        ds=[F(c['end_ns']-c['start_ns'],10**9*c['repeats']) for c in calls]
        t=sum(ds)/len(ds)
        qs=[2*(max(F(c['clock_resolution_ns']), F(c['clock_tick_num_ns'],c['clock_tick_den']))+1)
            / (10**9*c['repeats']) for c in calls]
        times[s]=(t,max(abs(d-t) for d in ds)+sum(qs)/len(qs))
    pairs={}
    sizes=sorted(times)
    for lo,hi in zip(sizes,sizes[1:]):
        d=times[hi][0]-times[lo][0]
        dd=times[hi][1]+times[lo][1]
        if d>dd:
            pairs[hi]={'m_bytes_s':F(hi-lo)/d,'lower':F(hi-lo)/(d+dd),'upper':F(hi-lo)/(d-dd)}
    c=max(pairs,key=lambda s:pairs[s]['lower'])
    md,mc=pairs[sizes[-1]],pairs[c]
    h=lambda x,y:1/(F(63,64)/x+F(1,64)/y)
    th={key:h(md[key],mc[key]) for key in ('m_bytes_s','lower','upper')}
    target=pairs[2**25]
    target.update(margin=target['m_bytes_s']-th['m_bytes_s'],
                  bar=target['m_bytes_s']-target['lower']+th['upper']-th['m_bytes_s'])
    return th,target


def verify():
    rec=e.receipts(e.worked5,0,e.random.Random(8))
    result=e.exact_arms(rec)
    th,pair=exact_reference(rec)
    actual=next(p for p in result['pairs'] if p['size']==2**25)
    differences={}
    for key in ('m_bytes_s','lower','upper','margin','bar'):
        differences['pair_'+key]=float(abs(F(actual[key])-pair[key]))/1e9
    for outkey,key in [('threshold','m_bytes_s'),('threshold_lower','lower'),('threshold_upper','upper')]:
        differences[outkey]=float(abs(F(result[outkey])-th[key]))/1e9
    noise=max(differences.values())
    # H2: the smaller of the two printed uncertainty widths is threshold's 0.000045 GB/s.
    printed_uncertainty=F(45,10**6)
    agreement=float(printed_uncertainty/100)
    if not 10**6*noise < agreement:
        raise AssertionError('no admissible agreement bar for these printed quantities')
    if not all(d < agreement for d in differences.values()):
        raise AssertionError('independent arithmetic disagreement')
    # Integer categorical output identity, not numerical floating agreement.
    if result['K'] != 2**26:
        raise AssertionError('wrong discrete knee output')
    for mode in ('floor','nearest'):
        for seed in range(400):
            r=e.exact_arms(e.receipts(e.worked5,0,e.random.Random(seed),mode))
            if r['K'] != 2**26:
                raise AssertionError('worked example lost in phase sweep')
    summary=dict(K_bytes=result['K'],threshold_GBs=result['threshold']/1e9,
        threshold_lower_GBs=result['threshold_lower']/1e9,
        threshold_upper_GBs=result['threshold_upper']/1e9,
        pair_m_GBs=actual['m_bytes_s']/1e9,pair_lower_GBs=actual['lower']/1e9,
        pair_upper_GBs=actual['upper']/1e9,margin_GBs=actual['margin']/1e9,
        bar_GBs=actual['bar']/1e9,threshold_halfwidth_GBs=result['threshold_uncertainty']/1e9,
        independent_discrepancies_GBs=differences,float_noise_GBs=noise,
        million_times_float_noise_GBs=1e6*noise,agreement_bar_GBs=agreement,
        worked_phase_confirmations_per_conversion=400)
    (Path(__file__).parent/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': verify()
