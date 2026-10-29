"""Read-only CI diagnosis; prospective registry rebinding is in memory only."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts import repin
from scripts import digest_pin_census as census
registry=census.load_registry(ROOT)
stale,_=repin.registry_stale(ROOT,registry)
print('current stale rows',len(stale))
plan=json.loads((ROOT/'configs/campaigns/bytes_mac_check/plan_tree.json').read_text())
for entry in registry['files']:
 if entry['path']!='configs/campaigns/bytes_mac_check/plan_tree.json':continue
 for row in entry['rows']:
  if row[0] not in {r.pointer for r in stale}:continue
  i=int(row[0].split('/')[2]);target='file:'+plan['stage_graph'][i]['input']['path']
  if target not in registry['targets']:registry['targets'].append(target)
  row[2]=registry['targets'].index(target)
print('stale rows after in-memory four target rebindings',len(repin.registry_stale(ROOT,registry)[0]))
template=json.loads((ROOT/'configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json').read_text())
by_path={m['manifest']['path']:m['external_input_id'] for m in template['external_inputs']['manifests']}
by_id={m['manifest']['manifest_id']:m['external_input_id'] for m in template['external_inputs']['manifests']}
for i in (2,4,18,24):
 m=plan['stage_graph'][i]['input'];print('stage',i,'path_lookup',by_path.get(m['path'],'MISSING'),'manifest_id_lookup',by_id.get(m['manifest_id'],'MISSING'))
for rev in ('e624d67c7','c748238eb^','c748238eb','a7a20c197','977a5d2df'):
 p=json.loads(subprocess.check_output(['git','-C',str(ROOT),'show',rev+':configs/campaigns/bytes_mac_check/plan_tree.json']))
 print(rev,'stage2',p['stage_graph'][2]['input']['path'])
