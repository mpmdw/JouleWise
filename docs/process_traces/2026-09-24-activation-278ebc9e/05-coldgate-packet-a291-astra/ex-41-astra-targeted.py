import contextlib,io,runpy,copy
from unittest.mock import patch
with contextlib.redirect_stdout(io.StringIO()): q=runpy.run_path('/tmp/278ebc9e/astra-ref/probe.py')
sp=q['sp'];reg=q['reg'];p=q['p'];g=q['g'];reseal=q['reseal'];out=q['outcome'];root=q['root'];ids=q['ids']
r1=reseal(copy.deepcopy(q['mutants']['R1']));r2b=reseal(copy.deepcopy(q['mutants']['R2b']))
print('R1_VERIFY_BASE',out(lambda:sp.verify_executed_roster(reg,r1,p)))
print('R2b_EXACT_BASE',out(lambda:sp.requeue_overrun(reg,r2b,12,[])),ids(g,r2b,p))
def r4b_baseline():
    with patch.object(sp,'_parent_facts',return_value=[dict(parent_id='p',model='large',level=1,n_items=2,n_terminal=0,indices=[])]):sp.requeue_overrun(reg,root,0,[])
print('R4b_BASE',out(r4b_baseline))
from tests.test_scored_roster_checker import r2_four_envelope_roster
rg,rr,rp=r2_four_envelope_roster();rreg=q['sr'].Registration.from_mapping(rg)
print('R4a_SECONDARY',sp._derived(rreg,rr)[1]['1'],'checker',ids(rg,rr,rp))
# Sensitivity: each unsafe mutation's required resealed census can fire in the text model.
print('TEXT_MODEL_CENSUS inv_02 inv_03 inv_11 inv_12 inv_38 inv_39 inv_52 stale_derived')
print('BASELINE_FUZZ_RED census lacks inv_11 and inv_12 on these witnesses; R2 raw ZeroDivisionError')
# Count data and guard populations in the discovered forged roster.
fs=q['facts'](q['rzreg'],q['z']);cell=[f for f in fs if f['model']=='large' and f['level']==1]
print('EMPTY_PARENT_POPULATIONS gate',sum(f['n_terminal']==0 for f in cell),'position',sum(bool(f['indices']) for f in cell),'full_relation',all(len(f['indices'])==f['n_items'] for f in cell if f['n_terminal']==0))
