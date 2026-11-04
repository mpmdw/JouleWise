from pathlib import Path
import json, os, shutil
from scripts import align_pilot_session as s
from scripts import bytes_h_session as h
source=Path('/Users/edr/night-align/pilot-v2-20261103T035512Z')
target=Path(os.environ['TMPDIR'])/'session'
target.mkdir()
state=h.read(source/'session.json')
state['plan_path']=str(target/'plan.json')
h.write(target/'plan.json',h.read(h.read(source/'session.json')['plan_path']))
h.write(target/'session.json',state)
for name in ('archive/derived/exclusions.json','archive/derived/flags.jsonl','archive/withheld/battery-assist.json'):
 p=source/name
 if p.is_file():
  (target/name).parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(p,target/name)
status=s.desk(target,harvest=False)
pilot=h.read(Path(status['pilot']))
assert len(pilot['members'])==24
assert all(m['summary'] for m in pilot['members'])
assert all(c['replay_identity']=='not_evaluated' for c in pilot['I4_prime'].values())
assert pilot['repeat_energy_spread']=={}
assert len(pilot['residual_analysis'])==2
assert all('counts_logged_headline' in c['scopes']['registered'] and 'counts_withheld' in c['scopes']['registered'] for c in pilot['residual_analysis'])
print('REAL_PILOT3_DESK_OK members=24 configurations=2 sampled_replays=not_evaluated')
print('REPORT_PATH='+status['pilot'])
