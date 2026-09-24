"""Seal-boundary oracle: checker-dirty (static, non-history rows) but _seal accepts, after refresh_derived+reseal."""
import random, itertools, sys
from copy import deepcopy
from collections import Counter
from joulewise import scored_packer as sp
from tests import test_scored_packer_fuzz as F
from tests.scored_case_generator import generate_case
from tests.test_scored_roster_checker import refresh_derived
from tests.scored_roster_checker import check_roster
HIST = {'INV-32','INV-36','INV-38','INV-39','INV-30','INV-31','INV-34','INV-35','INV-29'}  # history/replay-ish rows, reported separately
def clone_block(r, rng):
    """New id for a copy of a live block, placed live in a fresh envelope (AUD-1 shape, no terminal yet)."""
    live=[(pl,i) for pl,i in F._live_placements(r)]
    if not live: return None
    pl,_=rng.choice(live); b=next(x for x in r['blocks'] if x['block_id']==pl['block_id'])
    c=deepcopy(b); c['block_id']=b['block_id']+':999'; r['blocks'].append(c); n=len(r['envelopes'])
    r['envelopes'].append(dict(index=n,model=b['model'],kind='loaded',blocks=[c['block_id']],voided_block_ids=[],observations=None))
    r['placements'].append(dict(pl,block_id=c['block_id'],envelope_index=n)); return r
def terminalise_live(r, rng):
    """Terminal entries for every item of a live block, naming that block (op4 applied block-wide)."""
    live=F._live_placements(r)
    if not live: return None
    pl,_=rng.choice(live); b=next(x for x in r['blocks'] if x['block_id']==pl['block_id'])
    for it in b['items']:
        if not any(t['model']==b['model'] and t['item_id']==it for t in r['terminal_refusals']):
            r['terminal_refusals'].append(dict(type='unattributed_overrun',block_id=b['block_id'],attempt=pl['attempt'],parent_block_id=b['parent_block_id'],item_id=it,model=b['model'],level=b['level']))
    return r
def revive_voided(r, rng):
    cand=[(e,v) for e in r['envelopes'] for v in e['voided_block_ids']]
    if not cand: return None
    e,v=rng.choice(cand); e['voided_block_ids'].remove(v); e['blocks'].append(v); return r
OPS = list(F.OPERATORS)+[clone_block, terminalise_live, revive_voided]
def seal_ok(reg, m):
    try: sp._seal(reg, m, finalize=True); sp._seal(reg, m); return None
    except sp.PackingRefusal as x: return x.code
    except Exception as x: return 'CRASH:'+type(x).__name__
arity = int(sys.argv[1])
gap = Counter(); tried = Counter(); rows = Counter()
for seed,i in F.CASES:
    case = generate_case(seed,i)
    for k,base in enumerate(case.rosters):
        for combo in itertools.product(OPS, repeat=arity):
            m = deepcopy(base); rng = random.Random(f'{seed}:{i}:{k}:{[o.__name__ for o in combo]}')
            for op in combo:
                try: m = op(m, rng) if m is not None else None
                except Exception: m = None
            if m is None: continue
            try: refresh_derived(case.g, m)
            except Exception: continue
            m['sha256']=None
            if m['events']: m['events'][-1]['sha256']=''
            key=tuple(o.__name__ for o in combo); tried[key]+=1
            sealed=deepcopy(m)
            if seal_ok(case.reg, sealed) is not None: continue
            try: found={v.inv_id for v in check_roster(case.g, sealed, case.p)}
            except Exception as x: found={'CHK-CRASH'}
            static = found - HIST
            if static:
                gap[key]+=1; rows.update(static)
print('arity',arity,'mutants',sum(tried.values()),'seal-accepts-checker-static-dirty',sum(gap.values()))
for k,v in gap.most_common(12): print(' ',v,'/',tried[k],k)
print('static rows the seal missed:',dict(rows.most_common()))
