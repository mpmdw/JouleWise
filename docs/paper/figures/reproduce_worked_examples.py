#!/usr/bin/env python3
"""Reproduce paper-M numerical examples; no collection and no evidence writes.

Run from the repository root with --corpus-root and --output-dir. Outputs
are JSON and Markdown tables; source fingerprints are checked before use.
"""
from __future__ import annotations
import argparse
import csv
from dataclasses import asdict
from decimal import Decimal
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def bound(values):
    from joulewise.aggregate import student_t_critical_95
    return max(max(map(abs, values)), abs(statistics.mean(values)) +
               student_t_critical_95(len(values)-1)*statistics.stdev(values)*math.sqrt(1+1/len(values)))


def synthetic():
    from joulewise.detection_floor import absolute_false_effect_floor, comparative_false_effect_floor
    fixture = ROOT / 'tests/fixtures/fcm_r4_real_blocks/measured_pair.json'
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == 'ba9398bf74829d0dbf00dc19b6bb14c4119efc750e132dfef1daab0fc2808ea4'
    fixture_data = json.loads(fixture.read_text())
    blocks = fixture_data['blocks']
    timing_bound = fixture_data['operative_bound_s']
    inputs=[]
    for b in blocks:
        d,z=b['delta_j'],b['zero_point_contrast_j']
        onset,offset=b['onset_sweep_j'],b['offset_sweep_j']
        lo=min(onset)+min(offset)-2*z; hi=max(onset)+max(offset)-2*z
        from joulewise.floor_extraction import BundleReader, TracePoint, _integrate
        integrals=[]; fingerprints={}
        for member in b['members']:
            directory=fixture.parent/member['bundle_id']
            for name in ('power_trace.csv','events.jsonl','metadata.json','summary_metrics.json'):
                fingerprints[member['bundle_id']+'/'+name]=hashlib.sha256((directory/name).read_bytes()).hexdigest()
            reader=BundleReader(directory);curve=reader.summed_curve();window=reader.phase_windows()['decode'][0]
            origin=curve[0].t
            relative=[TracePoint(t=r.t-origin,power_w=r.power_w,support_start_s=r.support_start_s-origin,support_end_s=r.support_end_s-origin) for r in curve]
            integrals.append(_integrate(relative,window.start_s-origin-timing_bound,window.end_s-origin+timing_bound))
        assert math.fsum(.5*v for v in integrals)==b['member_envelope_integral_sum_j']
        inputs.append(dict(member_integrals=integrals,fixture_fingerprints=fingerprints,timing_bound_s=timing_bound,delta=d,zero=z,onset=onset,offset=offset,d_lower=lo,d_upper=hi,
                           q=max(abs(lo),abs(hi))+abs(z-d),
                           residuals=b['bundle_residual_half_widths_j'],
                           local=sum(b['bundle_residual_half_widths_j'])/2,
                           envelope_integral_sum=b['member_envelope_integral_sum_j']))
    cases=[]
    for s in (-1,1):
        for e in itertools.product((-1,1),repeat=2):
            values=[b['delta']+s*b['q']+sign*b['local'] for b,sign in zip(inputs,e)]
            cases.append(dict(signs=[s,*e],deltas=values,mean=statistics.mean(values),
                              sd=statistics.stdev(values),bound=bound(values)))
    zero=[0.0]*5;width=[0.5]*5
    return dict(blocks=inputs,cases=cases,
                composition_absolute=asdict(absolute_false_effect_floor(zero,admissible_half_widths_j=width)),
                composition_comparative=asdict(comparative_false_effect_floor(zero,admissible_half_widths_j=width)),
                point_absolute=asdict(absolute_false_effect_floor([8.,9.,10.,11.,12.],admissible_half_widths_j=[0.]*5)),
                point_comparative=asdict(comparative_false_effect_floor([0.,1.,2.,3.,4.],admissible_half_widths_j=[0.]*5)),
                corner_example=[dict(deltas=list(v),bound=bound(v)) for v in itertools.product((-1.,1.),(1.,3.))])


def historical(corpus):
    from joulewise.adapters.powermetrics import parse_powermetrics_records, anchor_records_from_powermetrics
    from joulewise.uncertainty_evidence import stamp_from_mapping, derive_powermetrics_anchor_v3
    import joulewise.powermetrics_fiducial as f
    directory=corpus/'runs_window_a_20260722/instrument_validation/20260722T145535-e941c821'
    evidence=json.loads((directory/'instrument_evidence.json').read_text())
    raw=(directory/'raw/powermetrics.plist').read_bytes();events=(directory/'events.jsonl').read_bytes()
    for name,data in [('raw/powermetrics.plist',raw),('events.jsonl',events)]:
        assert hashlib.sha256(data).hexdigest()==evidence['artifact_sha256'][name]
    native=parse_powermetrics_records(raw)
    anchor=derive_powermetrics_anchor_v3(stamps={k:stamp_from_mapping(v) for k,v in evidence['clock_anchor']['clock_stamps'].items()},records=anchor_records_from_powermetrics(native))
    records=parse_powermetrics_records(raw,first_record_endpoint_s=anchor['first_sample_end_point_epoch_s'])
    intervals=[f.TraceInterval(r.timestamp_s-r.elapsed_ns/1e9,r.timestamp_s,r.rail_power_w['gpu_power']) for r in records]
    rows=[json.loads(line) for line in events.decode().splitlines() if line.strip()]
    on=[r['metadata']['clock_stamp'] for r in rows if r.get('event_type')=='pulse_command_on']
    off=[r['metadata']['clock_stamp'] for r in rows if r.get('event_type')=='pulse_command_off']
    pulses=[f.CommandedPulse(a['epoch_s'],b['epoch_s'],f.clock_stamp_half_width_s(stamp_from_mapping(a)),f.clock_stamp_half_width_s(stamp_from_mapping(b))) for a,b in zip(on,off)]
    warm_end=max(r['metadata']['clock_stamp']['epoch_s'] for r in rows if r.get('event_type')=='warmup_command_off')
    trimmed=[i for i in intervals if i.start_s>=warm_end]
    baseline,sigma,outside=f._baseline_stats(trimmed,pulses)
    pulse=pulses[9]
    fit=f._fit_pulse(9,pulse,trimmed,baseline,sigma,f._ProjectionWorkBudget(165000,120.0))
    local=[]
    for idx,(r,n,i) in enumerate(zip(records,native,intervals)):
        if min(i.end_s,pulse.off_s+.75)>max(i.start_s,pulse.on_s-.75):
            pred=baseline+fit.amplitude_w*f._overlap_fraction(i,pulse.on_s+fit.delta_on_s,pulse.off_s+fit.delta_off_s)
            loss=f._huber((i.power_w-pred)/sigma)
            local.append(dict(index=idx,native_end_label=n.metadata["plist_timestamp_s"],elapsed_ns=r.elapsed_ns,start_s=i.start_s,end_s=i.end_s,
                              gpu_w=i.power_w,predicted_w=pred,loss=loss))
    loss=math.fsum(r['loss'] for r in local);flat=math.fsum(f._huber((r['gpu_w']-baseline)/sigma) for r in local)
    q=0;labels=[]
    for idx,n in enumerate(native):
        if idx:q+=n.elapsed_ns
        labels.append(dict(index=idx,q_ns=q,elapsed_ns=n.elapsed_ns,native_end_label_s=n.metadata["plist_timestamp_s"]))
    pop_path=ROOT/'docs/process_traces/2026-08-09-prefill-phase-proof/results.json'
    pop=json.loads(pop_path.read_text());members=[b for b in pop['bundles'] if b['stack']=='1.5B']
    chosen=[next(b for b in members if b['bundle']=='p2015-df-ph-decode-abs-r03'),next(b for b in members if b['power']['prefill_overlap_sample_count']==3)]
    geometry=[]
    for b in chosen:
        path=corpus/Path(b['corpus_root']).name/b['bundle']
        csvraw=(path/'power_trace.csv').read_bytes()
        assert hashlib.sha256(csvraw).hexdigest()==b['streams']['power_trace.csv']['sha256']
        assert hashlib.sha256((path/'events.jsonl').read_bytes()).hexdigest()==b['streams']['events.jsonl']['sha256']
        pairs=sorted({(Decimal(r['interval_start_s']),Decimal(r['interval_end_s'])) for r in csv.DictReader(csvraw.decode().splitlines())})
        start=Decimal(str(b['boundary']['prefill_start_s']));end=Decimal(str(b['boundary']['prefill_end_s']))
        touched=[i for i,(a,z) in enumerate(pairs) if min(end,z)>max(start,a)]
        origin=int(start)
        neighbors=[]
        for i in range(max(0,min(touched)-1),min(len(pairs),max(touched)+2)):
            a,z=pairs[i];neighbors.append(dict(index=i,start=str(a-origin),end=str(z-origin),overlap=str(max(Decimal(0),min(end,z)-max(start,a)))))
        geometry.append(dict(bundle=b['bundle'],corpus=Path(b['corpus_root']).name,origin=origin,start=str(start-origin),end=str(end-origin),records=neighbors,source_fingerprints=b['streams']))
    return dict(capture=directory.name,source_fingerprints={**evidence['artifact_sha256'],'instrument_evidence.json':hashlib.sha256((directory/'instrument_evidence.json').read_bytes()).hexdigest()},
                anchor=anchor,clock_stamps=evidence['clock_anchor']['clock_stamps'],native_constraints=labels,
                command_on=on[9],command_off=off[9],baseline_w=baseline,sigma_w=sigma,fit=asdict(fit),
                local_records=local,best_loss=loss,flat_loss=flat,loss_limit=loss+max(1,.05*loss),
                record0=asdict(native[0]),old_anchor_pulse0=dict(anchor=evidence['clock_anchor']['first_sample_end_point_epoch_s'],fit=evidence['pulses'][0],on=on[0],off=off[0]),
                geometry=geometry,population_sha256=hashlib.sha256(pop_path.read_bytes()).hexdigest())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus-root',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    data=dict(synthetic=synthetic(),historical=historical(args.corpus_root))
    (out/'worked-examples.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    h=data['historical'];lines=['| Native record i | Native end label (epoch s) | Start − 1784757381 (s) | End − 1784757381 (s) | GPU (W) | Predicted (W) | Huber loss |','|---|---|---:|---:|---:|---:|---:|']
    for r in h['local_records']:
        lines.append(f"| {r['index']} | {r['native_end_label']:.0f} | {r['start_s']-1784757381:.9f} | {r['end_s']-1784757381:.9f} | {r['gpu_w']:.8f} | {r['predicted_w']:.8f} | {r['loss']:.6f} |")
    (out/'pulse-table.md').write_text('\n'.join(lines)+'\n')
    print('REPLAYED synthetic compositions, 8 sign cases, current pulse 9, record 0, old pulse 0, and 2 overlap geometries')
    print('PRIMARY FINGERPRINTS MATCH; wrote worked-examples.json and pulse-table.md')


if __name__=='__main__':main()
