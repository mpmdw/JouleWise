from copy import deepcopy
from joulewise import scored_packer as sp
from tests.test_scored_packer import _split_route, reseal
from tests.test_scored_roster_checker import refresh_derived
from tests.scored_roster_checker import check_roster
g,p,reg,r=_split_route()
par=next(b for b in r['blocks'] if b['superseded'])
e=next(e for e in r['envelopes'] if par['block_id'] in e['voided_block_ids'])
print('parent',par['block_id'],'voided in env',e['index'],'reported',e['observations'] is not None)
def attempt(label,mut):
    m=deepcopy(r); mut(m); refresh_derived(g,m); m['sha256']=None
    try:
        sp._structure(reg,m); sp._seal(reg,m,finalize=True); sp._seal(reg,m); s='SEAL ACCEPT'
    except sp.PackingRefusal as x: s='SEAL '+str(x)
    live=[(b['block_id'],ee['index']) for b in m['blocks'] if par['items'][0] in b['items'] and b['model']==par['model'] for ee in m['envelopes'] if b['block_id'] in ee['blocks']]
    print(label,s,'| live owners of',par['items'][0],live,'| CHECKER',sorted({v.inv_id for v in check_roster(g,m,p)}))
    return m
# B1: revive the superseded parent's voided placement (move voided->live in its envelope)
def b1(m):
    ee=m['envelopes'][e['index']]; ee['voided_block_ids'].remove(par['block_id']); ee['blocks'].append(par['block_id'])
attempt('B1 revive-voided-superseded',b1)
# B2: new unreported envelope holding the superseded parent live with a fresh placement
def b2(m):
    n=len(m['envelopes']); pl=[x for x in m['placements'] if x['block_id']==par['block_id']][-1]
    m['envelopes'].append(dict(index=n,model=par['model'],kind='loaded',blocks=[par['block_id']],voided_block_ids=[],observations=None))
    m['placements'].append(dict(pl,envelope_index=n))
attempt('B2 superseded-parent-new-envelope',b2)
import sys; sys.path.insert(0,'/tmp/278ebc9e/esc2-opus'); from closed_own import ownership
models=list(g['role_to_model_id'].values()); items=[x for l in '12345' for x in g['item_ids_by_level'][l]]
m=deepcopy(r); b1(m); print('closed table B1',ownership(m,models,items)[:2])
m=deepcopy(r); b2(m); print('closed table B2',ownership(m,models,items)[:2])
