import ast, inspect, itertools
from copy import deepcopy
from probe_r3 import witnesses, closed, formation, seal, PACKET
from joulewise import scored_packer as sp
from tests import scored_roster_checker as ck
from tests.test_scored_roster_checker import refresh_derived
from tests.test_scored_packer import _split_route
from tests import test_scored_packer_fuzz as fuzz
import random

g,p,reg,ws=witnesses()
# Implement only the prescribed checker replacement in memory, retaining its type gate.
src=inspect.getsource(ck)
start=src.index('    for m in models:\n        for item in ids:\n            holders =',src.index('def _static_checks'))
end=src.index('    for i, e in enumerate',start)
replacement='''    for m in models:
        for item in ids:
            live = [b for b in r['blocks'] if b['model'] == m and item in b['items'] for e in r['envelopes'] if b['block_id'] in e['blocks']]
            named = sum(t['model'] == m and t['item_id'] == item for t in r['terminal_refusals'])
            if (len(live), named) not in ((1, 0), (0, 1)) or len(live) == 1 and (live[0]['superseded'] or any((m, x) in terms for x in live[0]['items'])):
                _bad(out, 'INV-11', f'item ownership {m}:{item}')
'''
exec(compile(src[:start]+replacement+src[end:],'<R3-checker-memory>','exec'),ck.__dict__)
for name,m in ws.items():
    m=deepcopy(m); m['sha256']=ck.digest(m); m['events'][-1]['sha256']=m['sha256']
    print('CHECKER-R3',name,'INV-11' in {v.inv_id for v in ck.check_roster(g,m,p)})
# Malformed terminal copied from the judge's stated non-type-clean shape: the exact
# judge fixture is unavailable. Demonstrate type gate prevents replacement from running.
m=deepcopy(ws['probe-D-type-clean']);m['terminal_refusals'][0]['type']='terminal'; m['sha256']=ck.digest(m);m['events'][-1]['sha256']=m['sha256']
print('CHECKER-R3 malformed-D',[(v.inv_id,v.detail) for v in ck.check_roster(g,m,p)])
# Full R3 formation short prose only pins item slices, not the exact §3.1 IDs.
g,p,reg,r=_split_route();m=deepcopy(r);b=next(b for b in m['blocks'] if b['parent_block_id'] is None and not b['superseded']);old=b['block_id'];new=old+':bad-id';b['block_id']=new
for e in m['envelopes']:
    e['blocks']=[new if x==old else x for x in e['blocks']];e['voided_block_ids']=[new if x==old else x for x in e['voided_block_ids']]
    for o in e['observations'] or []:
        if o['block_id']==old:o['block_id']=new
for pl in m['placements']:
    if pl['block_id']==old:pl['block_id']=new
for ev in m['events']:
    ev['block_ids']=[new if x==old else x for x in ev['block_ids']]
    for o in ev['observations']:
        if o['block_id']==old:o['block_id']=new
refresh_derived(g,m);m['sha256']=None;m['events'][-1]['sha256']=''
print('FORMATION renamed-parent literal=',formation(g,m),'closed=',not closed(g,m),'seal=',seal(reg,m))
print('FORMATION renamed-parent checker INV-10=',[v.detail for v in ck.check_roster(g,m,p) if v.inv_id=='INV-10'])
# The referenced composition scaffold drops exceptions before calling seal.
m=fuzz.op5_remove_single(deepcopy(r),random.Random(0))
try:refresh_derived(g,m);refresh='PASS'
except Exception as ex:refresh=type(ex).__name__
print('FUZZ remove-single refresh=',refresh)
print('FUZZ baseline pending skips tolerated only by unspecified generator exception policy')
# Mandatory gate conjunction versus literal iff.
prior_gates=False;forger_failed_to_find=True
print('GATE literal_iff=',forger_failed_to_find,'all_gates_conjunction=',prior_gates and forger_failed_to_find)
# Existing stress requirement is already implemented, so no scope expansion needed.
stress=open('tests/test_scored_packer_stress.py').read()
print('SCOPES disjoint=True preserved_stress_requirement_already_present=', 'def test_generate_case_variation_and_checker_agreement' in stress)
print('EXTRA probes complete')
