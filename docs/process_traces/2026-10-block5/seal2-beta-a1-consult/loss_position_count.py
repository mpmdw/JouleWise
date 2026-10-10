# Prints, for each harvest reference loss, only (position, closed-list code) tallies. No ids, no values.
import json, glob, os, collections
R='/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18/configs/campaigns/window_references_v5'
REASON={'contention.request_overlap','member.admission_aborted','battery.member_span','thermal.os_level_nonzero','member.timeout','status_not_succeeded'}
pos={}
for sub in sorted(os.listdir(R)):
    p=os.path.join(R,sub)
    if not os.path.isdir(p): continue
    label='start' if 'start' in sub else 'end' if 'end' in sub else 'midpoint' if 'mid' in sub else 'other'
    for f in glob.glob(p+'/**/*.json',recursive=True)+glob.glob(p+'/**/*.yaml',recursive=True):
        try: t=open(f).read()
        except OSError: continue
        pos.setdefault(label,[]).append(t)
d=json.load(open('/Users/edr/night-archive/harvest-v5-b5-beta-a1-20261010T0742Z/derived/neg8-screen.json'))
c=collections.Counter()
for rid,code in (d.get('harvest_reference_losses') or {}).items():
    hits=sorted({l for l,ts in pos.items() if any(rid in t for t in ts)})
    c[('+'.join(hits) or 'unmapped', code if code in REASON else 'other')]+=1
print(sorted(c.items()))
