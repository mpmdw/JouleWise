import json, re, glob, os, hashlib, datetime, sys
ROOT='/Users/edr/night-custody'
cand=json.load(open('/Users/edr/code/JouleWise-wt-cg-scia2-d528efb2/docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json'))
members={m['member_id']:m for m in cand['derivation_corpus']['members']}
# parse timed applies from my own log pulls
ev=[]
for f in ('timed_w1.txt','timed_w2.txt'):
    for line in open(f,errors='replace'):
        if 'cmd,apply' not in line: continue
        ts=line[:26]
        t=datetime.datetime.strptime(ts,'%Y-%m-%d %H:%M:%S.%f')
        kv=line.split('cmd,apply,')[1].strip().split(',')
        d=dict(zip(kv[0::2],kv[1::2]))
        # PDT = UTC-7
        epoch=(t-datetime.datetime(1970,1,1)).total_seconds()+7*3600
        ev.append(dict(ts=ts,epoch=epoch,src=d['src'],adjust=float(d['adjust']),mach=int(d['mach'])))
ev.sort(key=lambda e:e['epoch'])
json.dump(ev,open('events.json','w'),indent=1)
rows=[]
for w in ('w1','w2'):
    sess=f'd079-epoch-25g83-derivation-{w}-20260927'
    for i in range(1,13):
        cid=f'{sess}-d{i:02d}'
        p=f'{ROOT}/{sess}/runs/instrument_validation/{cid}/instrument_evidence.json'
        raw=open(p,'rb').read()
        sha=hashlib.sha256(raw).hexdigest()
        d=json.loads(raw)
        ca=d.get('clock_anchor',{})
        st=ca.get('clock_stamps',{})
        rows.append(dict(cid=cid,short=f'{w}-d{i:02d}',sha=sha,member=cid in members,
            sha_ok=(members[cid]['instrument_evidence_sha256']==sha) if cid in members else None,
            b=d.get('b_fiducial_s'),status=ca.get('status'),reason=ca.get('reason') or ca.get('unresolved_reason') or ca.get('detail'),
            ca={k:v for k,v in ca.items() if k!='clock_stamps'},stamps=st,
            valid=d.get('valid'),reasons=d.get('reasons')))
json.dump(rows,open('captures.json','w'),indent=1)
def hms(e): return (datetime.datetime(1970,1,1)+datetime.timedelta(seconds=e-7*3600)).strftime('%H:%M:%S.%f')[:-3]
for r in rows:
    st=r['stamps']
    if not st: print(r['short'],'NO STAMPS',r['status']); continue
    t0=st['pre_spawn']['epoch_s']; t1=st['post_parse']['epoch_s']
    inside=[e for e in ev if t0<=e['epoch']<=t1]
    before=[e for e in ev if e['epoch']<t0]
    last=before[-1] if before else None
    lastbig=[e for e in before if abs(e['adjust'])>=1e-3]
    lb=lastbig[-1] if lastbig else None
    print(f"{r['short']} {'MEMBER ' if r['member'] else 'excluded'} sha_ok={r['sha_ok']} {hms(t0)}-{hms(t1)} dur={t1-t0:.1f}s status={r['status']} span={r['ca'].get('wall_minus_monotonic_span_s')} bound={r['ca'].get('effective_clock_anchor_bound_s')}")
    for e in inside:
        print(f"      INSIDE  {e['ts']} {e['src']} {e['adjust']*1e3:+.6f} ms  (t0+{e['epoch']-t0:.1f}s)")
    if lb: print(f"      last ms-scale correction before start: {lb['ts']} {lb['src']} {lb['adjust']*1e3:+.3f} ms, {t0-lb['epoch']:.0f} s before start")
    if last and last is not lb: print(f"      last correction of any size before start: {last['ts']} {last['adjust']*1e6:+.1f} us, {t0-last['epoch']:.0f} s before")
