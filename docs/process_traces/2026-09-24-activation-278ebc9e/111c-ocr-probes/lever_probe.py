import sys, copy, json, hashlib
sys.path.insert(0, '/Users/edr/code/wt-278ebc9e-ocr')
from joulewise import scored_packer as sp, scored_registration as sr
from tests.test_scored_registration import fixture, canon_sha
def run(n, bs, p8, p17, w8, w17, cap, budget=None, delta=None):
    g, _ = fixture(n=n, block_size=bs, mode='pilot', cap=cap, worst=max(w8,w17))
    m8, m17 = 'large', 'small'
    g['s_per_token_upper'] = {m8: {'decode': w8}, m17: {'decode': w17}}
    g['ceiling_s'] = {m8: {'decode': w8}, m17: {'decode': w17}}
    pred = {m8: {i: p8 for v in g['item_ids_by_level'].values() for i in v}, m17: {i: p17 for v in g['item_ids_by_level'].values() for i in v}}
    reg = sr.Registration.from_mapping(g)
    try:
        r = sp.pack(reg, pred)
    except sp.PackingRefusal as e:
        return f"REFUSED {e.code}"
    return dict(env=len(r['envelopes']), lever=r['drift_lever_slots'], bpc=reg.blocks_per_cell)
print('symmetric', run(20, 4, 1.0, 1.0, 2.0, 2.0, 12.0))
print('8B 3x slower', run(20, 4, 3.0, 1.0, 6.0, 2.0, 24.0))
print('8B 2x slower', run(20, 4, 2.0, 1.0, 4.0, 2.0, 24.0))
# level vs night position (within model), symmetric case
g, pred = fixture(n=20, block_size=4, mode='pilot', cap=12.0, worst=2.0, pred=1.0)
reg = sr.Registration.from_mapping(g); r = sp.pack(reg, pred)
bm = {b['block_id']: b for b in r['blocks']}
for m in ('large','small'):
    pos = {L: [e['index'] for e in r['envelopes'] for bid in e['blocks'] if bm[bid]['level']==L and bm[bid]['model']==m] for L in range(1,6)}
    print(m, {L: sum(v)/len(v) for L, v in pos.items()}, 'n_env', len(r['envelopes']))
