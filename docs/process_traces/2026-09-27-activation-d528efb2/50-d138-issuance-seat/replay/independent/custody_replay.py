import hashlib,json,os,shlex,subprocess
from pathlib import Path
R=Path.cwd();O=Path('/tmp/d138-replay-d528efb2/independent');P='/opt/homebrew/bin/python3'
I=R/'configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json'
C=R/'docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json'
A=json.loads(I.read_bytes()); root=Path('/Users/edr/night-custody')
ledger=root/'measurement/JouleWise-measurement-20260927-derivation-w2/runs/calibration_observation_ledger.jsonl'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def snapshot():
 result={}
 for m in A['derivation_corpus']['members']:
  directory=root/m['source_directory'];files=sorted(p for p in directory.rglob('*') if p.is_file())
  assert files
  for p in files:result[str(p)]=digest(p)
  for name,key in [('manifest.json','manifest_sha256'),('instrument_evidence.json','instrument_evidence_sha256')]:assert result[str(directory/name)]==m[key]
 result[str(ledger)]=digest(ledger)
 return result
before=snapshot();(O/'custody-before.json').write_text(json.dumps(before,indent=2,sort_keys=True)+'\n')
print('before custody files',len(before)-1,'ledger',before[str(ledger)],flush=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(O))
cmd=[P,'-B','scripts/issue_calibration_acceptance_generation.py','verify-members','--artifact',str(I),'--corpus-root',str(root)]
print('COMMAND',shlex.join(cmd),flush=True)
r=subprocess.run(cmd,capture_output=True,text=True,env=env);(O/'verify-members.log').write_text(r.stdout+r.stderr);print(r.stdout,r.stderr,flush=True)
after_verify=snapshot();assert before==after_verify
assert r.returncode==0 and r.stdout.count(': PASS')==12 and ': FAIL' not in r.stdout
print('iv PASS 12 members; all custody digests equal immediately after verification',flush=True)
# D3: recorded original argv, changing interpreter/output and explicitly locating
# the same real ledger because a detached code worktree has no runs directory.
args=shlex.split((C.parent/'run1-command.txt').read_text())
args[:1]=[P,'-B'];args[args.index('--out')+1]=str(O/'D3-candidate.json')
args.extend(['--ledger',str(ledger)])
print('COMMAND',shlex.join(args),flush=True)
r=subprocess.run(args,capture_output=True,text=True,env=env);(O/'D3.log').write_text(r.stdout+r.stderr);print(r.stdout,r.stderr,flush=True)
after=snapshot();(O/'custody-after.json').write_text(json.dumps(after,indent=2,sort_keys=True)+'\n')
assert before==after,'custody changed'
assert r.returncode==0,('D3',r.returncode)
out=O/'D3-candidate.json';assert out.read_bytes()==C.read_bytes()
print('v D3 PASS byte_equal=True sha256='+digest(out),flush=True)
print('custody files unchanged',len(before)-1,'ledger unchanged=True',flush=True)
print('CUSTODY AND D3 PASS',flush=True)
