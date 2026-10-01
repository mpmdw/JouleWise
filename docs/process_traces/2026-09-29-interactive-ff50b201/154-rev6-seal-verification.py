"""Read-only seal verification; external authorities use the lead-supplied paths."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root))
from scripts import issue_calibration_acceptance_generation as issuer
from joulewise import powermetrics_fiducial
from joulewise.calibration_ledger import canonical_json_bytes, receipt_core
reg=root/'configs/calibration/preregistration_d079_epoch_25g83_rev1.md'
text=reg.read_text(); block=issuer.revision_six_declaration(text)
source=root/'docs/process_traces/2026-09-29-interactive-ff50b201/110-rev6-gate/32-revision6-sealable-e1.md'
assert source.read_text().count('TO BE PINNED AT SEAL')==20
assert 'TO BE PINNED AT SEAL' not in text
original=subprocess.check_output(['git','show','46643f1d21d875f06a7349b6c6298f7ffcd163db:configs/calibration/preregistration_d079_epoch_25g83_rev1.md'],cwd=root)
assert reg.read_bytes().startswith(original+b'\n')
for pattern in (issuer._PREREGISTRATION_OS_BUILD,issuer._PREREGISTRATION_POWERMETRICS,r'\bchain digest\s+([0-9a-f]{64})\b',r'^Chain digest in force \(revision 3\): ([0-9a-f]{64})$'):
 assert len(re.findall(pattern,text) if hasattr(pattern,"findall") else re.findall(pattern,text,re.M))==1
entries=[]
def pin(label,path,expected): entries.append((label,Path(path),expected))
record=root/'docs/process_traces/2026-09-29-interactive-ff50b201'
for label,name in [('ruling','21-coldgate-fable-ruling.md'),('erratum','31-coldgate-erratum.md')]:
 path=record/'110-rev6-gate'/name
 value=hashlib.sha256(path.read_bytes()).hexdigest()
 assert f'sha256 `{value}`' in text
 pin(label,path,value)
pin('P8 file (prose + JSON)',root/block['predecessor']['path'],block['predecessor']['file_sha256'])
p8=json.loads((root/block['predecessor']['path']).read_bytes())
assert issuer.derivation_sha256(p8)==p8['derivation_sha256']==block['predecessor']['derivation_sha256']
def canonical_shasum(value):
 raw=json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
 return subprocess.check_output(['shasum','-a','256'],input=raw).decode().split()[0]
assert canonical_shasum({key:value for key,value in p8.items() if key!='derivation_sha256'})==p8['derivation_sha256']
assert f"`derivation_sha256`: `{p8['derivation_sha256']}`" in text
science=Path('/Users/edr/code/JouleWise-wt-bk-ff50b201/docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate')
for name in ['21-science-gate-ruling.md','22-opus-refuter.md','31-addendum-ruling.md']:
 value=re.search(re.escape(name)+r'`, sha256 `([0-9a-f]{64})`',text).group(1)
 pin('diagnostic seat '+name,science/name,value)
for key,path in [('chain','scripts/night_chains/calibration_derivation_only.zsh'),('validator','scripts/validate_powermetrics_fiducial.py'),('prewindow_check','scripts/prewindow_check.sh'),('harness','scripts/cap_replay_harness.py')]:
 pin(key,root/path,block['pins'][key+'_sha256'])
for path,value in block['pins']['estimator_code_sha256'].items():
 pin(path,root/path,value)
assert block['pins']['estimator_code_sha256']==p8['prospective_rederivation']['estimator_code_sha256']
pin('cap_rule_text','/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/20-cap-council/31-addendum-ruling.md',block['pins']['cap_rule_text_sha256'])
pin('roster',record/'130-cap-roster.md',block['pins']['roster_sha256'])
pin('disposition registry',root/'configs/calibration/observation_dispositions.json',block['disposition_registry_sha256'])
for path,value in zip(['configs/launchd/com.joulewise.night.plist.template','configs/launchd/com.joulewise.night-probe.plist.template'],block['pins']['launch_template_sha256']):
 pin('launch template '+path,root/path,value)
head=json.loads((root/'configs/calibration/calibration_ledger_head.json').read_bytes())
assert block['pins']['ledger_head_pin_at_first_window']=={'sequence':head['sequence'],'digest':head['head_digest']}
archived=Path('/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/measurement-runs/calibration_observation_ledger.jsonl')
rows=[json.loads(line) for line in archived.read_text().splitlines()]
assert len(rows)==head['sequence'] and rows[-1]['receipt_digest']==head['head_digest']
assert subprocess.check_output(['shasum','-a','256'],input=canonical_json_bytes(receipt_core(rows[-1]))).decode().split()[0]==head['head_digest']
assert type(block['pins']['cap_cells']) is int and block['pins']['cap_cells']==1710000==powermetrics_fiducial.DETECTION_PROJECTION_CELL_BUDGET
output=subprocess.check_output(['shasum','-a','256',*[str(p) for _,p,_ in entries]],text=True)
actual=[line.split()[0] for line in output.splitlines()]
for (label,path,value),found in zip(entries,actual):
 assert value==found,(label,value,found)
 print(label+' | '+value+' | fresh shasum PASS')
print('P8 derivation (prose + JSON) | '+p8['derivation_sha256']+' | issuer canonical hash and fresh shasum PASS')
print('cap_cells | 1710000 | production constant and integer type PASS')
print('ledger sequence | '+str(head['sequence'])+' | head pin and archived receipt count PASS')
print('ledger digest | '+head['head_digest']+' | head pin and archived receipt canonical shasum PASS')
print('preregistration_sha256 | '+hashlib.sha256(reg.read_bytes()).hexdigest())
print('REVISION_SIX_POLICY_SHA256 | '+issuer.REVISION_SIX_POLICY_SHA256)
assert canonical_shasum({key:block[key] for key in ['sessions','start_state_conditions','start_condition_evidence','definitions','count_rule','stop_lines','sampling_dependence']})==issuer.REVISION_SIX_POLICY_SHA256
print('PASS: 20 slots; JSON; unique issuer and chain regexes; historical prefix unchanged; all new digest pins verified')
