"""Native grouped-export reproduction; campaign replay is separate from chain.py harvest."""
import sys, os, tempfile, json, copy, hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
os.environ['JW_B5_SYNTHETIC_ONLY']='1'
from tests.test_bytes_analysis import archive_campaign
from tests.b6.test_bytes_p2_thermal_window import thermal_journal, NS
from scripts import bytes_thermal_lines as t
from joulewise import bytes_analysis as ba

def put(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v))
def get(p): return json.loads(p.read_bytes())
def run():
 with tempfile.TemporaryDirectory() as tmp:
  root=Path(tmp)
  skipped=[f'bytes-s{s}-p{p}' for s in range(1,7) for p in (1,2) if s not in (2,5)]
  manifest=archive_campaign(root,non_claim=False,subpack_sessions=True,uncollected_sessions=skipped,release='none')
  import shutil
  private=root/'private-keys/bytes/blinding'; released=root/'released-keys/bytes/blinding'; released.mkdir(parents=True,exist_ok=True)
  for path in private.glob('*.json'): shutil.copyfile(path,released/path.name)
  print('NATIVE_CAMPAIGN_GENERATED',flush=True)
  for session in manifest['sessions']:
   a=Path(session['archive']); p=session['pass_id']; sid=session['session_id']; exp=root/'export'/sid
   roster=get(a/'derived/roster.json'); science=[m for m in roster['members'] if m['role']=='science']
   for m in roster['members']: m['kind']='science' if m['role']=='science' else 'external_input'
   put(a/'derived/roster.json',roster)
   target=next(m for m in science if m['units'][0]['stratum']=='quad' and (sid.startswith('bytes-s5') or m['run_id'].startswith('qwen3-8b-4bit'))); runid=target['run_id']
   if p==2:
    put(a/'withheld/member-assessments.json',{'members':{m['run_id']:{t.FIELD:{'excluded':m is target,'journal_available':True}} for m in science}})
   else:
    ac=get(a/'derived/b6-acceptance.json');ac['excluding'].append({'scope':'member','run_id':runid,'code':t.CODE});put(a/'derived/b6-acceptance.json',ac)
    put(a/'withheld/spans.json',{'spans':{m['run_id']:{'member':[20*NS,100*NS],'request':[40*NS,80*NS]} for m in science}})
    put(a/'derived/harvest-thresholds.json',{'values':{'thermal_unmeasured_gap_s':6}})
    j=a/'sources/night-custody/hazards/monitor/thermal.jsonl';j.parent.mkdir(parents=True,exist_ok=True);thermal_journal(range(0,126,5),{90}).dump(j)
    # update the actual public OR withheld exported target's code, preserving native layout
    import csv
    side=get(exp/(sid+'.session.json')); paths=[exp/(sid+'.runs.csv'),exp/side['blinding']['withheld']['path']]
    for path in paths:
     with path.open(newline='') as f: reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
     for row in rows:
      if row['run_id']==runid: row['exclusion_codes']=t.CODE
     with path.open('w',newline='') as f: writer=csv.DictWriter(f,fields);writer.writeheader();writer.writerows(rows)
   # Archive ingress' historical default is export/bytes even for grouped packs.
   legacy=root/'export/bytes';legacy.mkdir(exist_ok=True)
   import shutil
   shutil.copyfile(exp/(sid+'.runs.csv'),legacy/(sid+'.runs.csv'))
   side=get(exp/(sid+'.session.json'));side['blinding']['withheld']['path']=str((exp/side['blinding']['withheld']['path']).resolve());put(legacy/(sid+'.session.json'),side)
   mode='hull-p2' if p==2 else 'request-end-p1'; out=root/(sid+'-line')
   record=t.transform(mode,a,out)
   local=copy.deepcopy(manifest);local['sessions']=[copy.deepcopy(session)];local['sessions'][0]['released_key_dir']=str((a/session['released_key_dir']).resolve())
   source_hashes={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in a.rglob('*') if path.is_file()}
   for label,path in [('source',a),('output',out)]:
    rec=ba.load_records(path,local,stage='all'); models=ba.reduce_models(rec,local,boundaries=('rails',))
    selected=[r for r in rec if r['model']==next(x['model'] for x in manifest['models'] if target['units'][0]['cell_id'] in x['cell_ids'])]
    print('INVALID',sid,label,[(r['run_id'],r.get('unusable_reason')) for r in selected if r['status']!='succeeded'][:2],flush=True)
    print('ARCHIVE',sid,label,[(r['stratum'],r['unit_id'],r['run_id']) for r in selected if r['excluded']],[(x['model'],x['status'],x.get('n_r'),x.get('n_b'),x.get('reason')) for x in models if x['model']==selected[0]['model']],flush=True)
   assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha for path,sha in source_hashes.items())
   print('ANALYSIS_SOURCE_UNCHANGED',sid,flush=True)
   try:
    t.transform(mode,a,root/(sid+'-csv-line'),exp)
    print('CSV_TRANSFORM',sid,'success',flush=True)
   except ValueError as exc: print('CSV_TRANSFORM',sid,'REFUSED',str(exc),flush=True)
   # Change one linked synthetic reduction after publication: recorded hashes must detect this.
   if sid=='bytes-s2-p2':
    mutation_run='qwen3-8b-4bit-0'
    before_records=ba.load_records(out,local,stage='all')
    before_models=ba.reduce_models(before_records,local,boundaries=('rails',))
    previous=next(x for x in before_records if x['run_id']==mutation_run)['rails_j']
    summary_path=a/'withheld/reductions'/(mutation_run+'.summary_metrics.rereduced.json')
    summary=get(summary_path); summary['phase_energy_j']['decode'] *= 2; put(summary_path,summary)
    after_records=ba.load_records(out,local,stage='all')
    current=next(x for x in after_records if x['run_id']==mutation_run)['rails_j']
    print('PUBLISHED_REDUCTIONS_CHANGED',before_models!=ba.reduce_models(after_records,local,boundaries=('rails',)),flush=True)
    print('ANALYSIS_LINK_MUTATION',previous!=current,'ALL_RECORDED_HASHES_MATCH',all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==v for p,v in record['source_sha256'].items()),flush=True)
   # Isolate one session, retaining native sidecar paths via originals for the source.
   source=ba.load_records(exp,local,stage='blinded',stage1_commit='synthetic-committed')
   print('BLINDED_SOURCE_CENSUS',sid,len(source),'model_rows',len([r for r in source if r['model']==selected[0]['model']]),flush=True)
   if (root/(sid+'-csv-line')).is_dir():
    changed=ba.load_records(root/(sid+'-csv-line/export'),local,stage='blinded',stage1_commit='synthetic-committed')
    print('BLINDED_OUTPUT_CENSUS',sid,len(changed),flush=True)
    print('BLINDED_OUTPUT_MODELS',sid,[(x['model'],x['status'],x.get('n_b'),x.get('reason')) for x in ba.reduce_models(changed,local,boundaries=('rails',)) if x['model']==selected[0]['model']],flush=True)
  print('CAMPAIGN_DONE',flush=True)
if __name__=='__main__':run()
