import copy, hashlib, io, json, os, sys, unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path('/Users/edr/code/JouleWise-wt-d138-contract2-d528efb2')
SCRATCH = Path('/tmp/d138-contract2-d528efb2')
sys.path.insert(0, str(ROOT))
from scripts import promote_calibration_candidate as p
from scripts.issue_calibration_acceptance_generation import derivation_sha256, derivation_input_sha256
import joulewise.calibration_bracketing as b
import joulewise.calibration_dispositions as d
from tests.test_claim_hold_routes import synthetic_bracket

candidate = p.CANDIDATE.read_bytes()
text = json.loads(p.ISSUANCE_TEXT.read_bytes())
raw = b.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH.read_bytes()
issued = json.loads(raw)
print('PIN', hashlib.sha256(raw).hexdigest())
assert hashlib.sha256(raw).hexdigest() == 'd6de84b854a4c5d7f6d73dfde2ae0f14d71a483355c7289a36882e0dfcccd5ea' == b.ISSUED_ACCEPTANCE_REGISTRY[b.EPOCH_25G83_R1_ACCEPTANCE_ID]['file_sha256']
assert issued['derivation_input_sha256'] == derivation_input_sha256(issued) == 'e7363bdd83af94cad15f0554043d35b646168e005125d3d770e7ba91dc9fb011'
assert issued['derivation_sha256'] == derivation_sha256(issued)
assert p.promote(candidate, p.ISSUANCE_TEXT.read_bytes()) == raw
print('SEALS_AND_REGEN PASS')

mutations = [
 ('P4a', lambda t: t['issuance_record']['rulings'][0].__setitem__('file_sha256', 'f'*64)),
 ('P4b', lambda t: t['issuance_record']['rulings'][0].__setitem__('relative_path', 'does-not-exist')),
 ('P4c', lambda t: t['issuance_record']['disclosures'][7].__setitem__('text', 'x')),
 ('P4d', lambda t: t['network_time_provenance'].__setitem__('text', 'x')),
 ('P4e', lambda t: (t['issuance_record'].pop('claim_eligible_meaning'), t['issuance_record'].pop('hold_enforcement'))),
 ('P4f', lambda t: t['issuance_record']['source_candidate'].__setitem__('relative_path', 'does-not-exist')),
 ('P5a_missing_candidate_path', lambda t: t['issuance_record']['source_candidate'].pop('relative_path')),
 ('P5b_missing_ntp_source_digest', lambda t: (t['network_time_provenance']['source_rulings'][0].pop('file_sha256'), t['network_time_provenance']['source_rulings'][0].__setitem__('relative_path', 'does-not-exist'))),
 ('P5c_bad_ntp_digest', lambda t: t['network_time_provenance']['source_rulings'][0].__setitem__('file_sha256', 'f'*64)),
 ('P5d_bad_log_digest', lambda t: t['network_time_provenance']['preserved_log'].__setitem__('plain_text_sha256', 'f'*64)),
 ('P5e_missing_log', lambda t: t['network_time_provenance'].pop('preserved_log')),
 ('P5f_no_ntp_sources', lambda t: t['network_time_provenance'].pop('source_rulings')),
 ('P5g_missing_h1_text', lambda t: t['issuance_record'].__setitem__('holds', [{'id': 'H1'}])),
 ('P5h_empty_hold_enforcement', lambda t: t['issuance_record'].__setitem__('hold_enforcement', ' \n')),
 ('P5i_outside_root', lambda t: t['issuance_record']['rulings'][0].__setitem__('relative_path', '/tmp/no-citation')),
 ('P5j_joint_D8_replacement', lambda t: (t['issuance_record']['disclosures'][7].__setitem__('text', 'x'), t['network_time_provenance'].__setitem__('text', 'x'))),
]
for name, edit in mutations:
    changed = copy.deepcopy(text)
    edit(changed)
    try:
        output = p.promote(candidate, json.dumps(changed).encode())
    except Exception as e:
        print(name, 'REFUSED', type(e).__name__, str(e))
        if name.startswith('P4'): assert isinstance(e, ValueError)
    else:
        assert not name.startswith('P4'), name
        print(name, 'ACCEPTED', hashlib.sha256(output).hexdigest())
        (SCRATCH / (name+'.json')).write_bytes(json.dumps(changed, indent=2).encode())

r7 = b.load_calibration_acceptance_bound()
assert r7['acceptance_id'] == b.ANCHOR_V3_R7_ACCEPTANCE_ID
print('DEFAULT', r7['acceptance_id'], 'EPOCHS', [r7['identity_epoch']['os_build']])
assert b.load_calibration_acceptance_bound(b.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH) is None
assert b.load_calibration_acceptance_bound(b.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH, allow_claim_held=True) == issued
print('HOLD_DEFAULT_AND_OPTIN PASS')

variants = {'identical_copy':raw, 'trailing_space':raw+b' ', 'reserialized':json.dumps(issued).encode(), 'candidate':candidate}
for name, edit in [
 ('member_resealed', lambda v:v['derivation_corpus']['members'][0].__setitem__('b_fiducial_s','0.9')),
 ('notes_deleted_resealed',lambda v: v['derivation_notes'].pop('issuance_record')),
 ('new_relabelled_r7',lambda v:v.__setitem__('acceptance_id',b.ANCHOR_V3_R7_ACCEPTANCE_ID)),
]:
    v=copy.deepcopy(issued); edit(v)
    v['derivation_input_sha256']=derivation_input_sha256(v); v['derivation_sha256']=derivation_sha256(v)
    variants[name]=(json.dumps(v,indent=2)+'\n').encode()
v=copy.deepcopy(r7); v['acceptance_id']=b.EPOCH_25G83_R1_ACCEPTANCE_ID
v['derivation_sha256']=derivation_sha256(v)
variants['r7_relabelled_new']=(json.dumps(v,indent=2)+'\n').encode()
for name, data in variants.items():
    path=SCRATCH/(name+'.json'); path.write_bytes(data)
    accepted=b.load_calibration_acceptance_bound(path,allow_claim_held=True) is not None
    assert accepted == (name=='identical_copy'),name
    print('AUTH',name,'LOADED' if accepted else 'REFUSED')

registry_raw=d.DISPOSITION_REGISTRY_PATH.read_bytes()
parsed=d.parse_disposition_registry(registry_raw,expected_sha256=d.DISPOSITION_REGISTRY_SHA256)
assert len(parsed)==11
rows=json.loads(registry_raw); rows.pop(); edited=json.dumps(rows).encode()
for label, data, pin, table in [
 ('edited_file_old_pin',edited,d.DISPOSITION_REGISTRY_SHA256,d.DISPOSITION_DECISIONS),
 ('edited_file_new_pin',edited,hashlib.sha256(edited).hexdigest(),d.DISPOSITION_DECISIONS),
 ('edited_table_old_file',registry_raw,d.DISPOSITION_REGISTRY_SHA256,{k:{**v,'content_ids':v['content_ids']|{'f'*64}} for k,v in d.DISPOSITION_DECISIONS.items()}),
]:
    with patch.object(d,'DISPOSITION_REGISTRY_SHA256',pin),patch.object(d,'DISPOSITION_DECISIONS',table):
        try:d.parse_disposition_registry(data,expected_sha256=pin)
        except d.DispositionRegistryError as e:print('TABLE',label,'REFUSED',str(e))
        else:raise AssertionError(label)

with patch.dict(b.CLAIM_HELD_ACCEPTANCE_IDS,{},clear=True):
    for count in [1,2,4,11,12,13]:
        result,reasons=synthetic_bracket(issued,dict(issued['identity_epoch']),count,explicit=True)
        triggers=result['acceptance']['prospective_rederivation']['observed_triggers']
        assert ('corpus_doubles_from_12_to_24' in triggers)==(count>=12)
        print('DOUBLING',count, 'triggers='+repr(triggers), 'reasons='+repr(reasons))
for count in [3,4]:
    result,reasons=synthetic_bracket(r7,dict(r7['identity_epoch']),count)
    triggers=result['acceptance']['prospective_rederivation']['observed_triggers']
    assert ('corpus_doubles_from_17_to_34' in triggers)==(count>=4)
    print('R7_DOUBLING',30+count, 'triggers='+repr(triggers))
print('PROBES_COMPLETE')
