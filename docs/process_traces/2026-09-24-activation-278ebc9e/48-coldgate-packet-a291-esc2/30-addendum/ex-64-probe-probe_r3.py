import ast, inspect, itertools, json, sys
from copy import deepcopy
from pathlib import Path
from joulewise import scored_packer as sp
from tests.test_scored_packer import _split_route
from tests.test_scored_roster_checker import refresh_derived
from tests.scored_roster_checker import check_roster
from tests.scored_case_generator import generate_case

PACKET=Path('/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/48-coldgate-packet-a291-esc2')

def closed(g,r,omit=None):
    blocks={b['block_id']:b for b in r['blocks']}
    live={}; terms={}
    for e in r['envelopes']:
        for bid in e['blocks']:
            b=blocks[bid]
            # Membership, per K1; one pair per block/envelope, not per duplicate item.
            for item in set(b['items']):
                live.setdefault((b['model'],item),[]).append((bid,e['index']))
    for t in r['terminal_refusals']:
        terms.setdefault((t['model'],t['item_id']),[]).append(t)
    bad=[]
    for model in g['role_to_model_id'].values():
        for item in itertools.chain.from_iterable(g['item_ids_by_level'][str(l)] for l in range(1,6)):
            L=live.get((model,item),[]); T=terms.get((model,item),[])
            if omit!='counts' and (len(L),len(T)) not in ((1,0),(0,1)):
                bad.append(('counts',model,item))
            if len(L)==1:
                b=blocks[L[0][0]]
                if omit!='superseded' and b['superseded']:
                    bad.append(('superseded',model,item))
                if omit!='terminal-holder' and any((model,x) in terms for x in b['items']):
                    bad.append(('terminal-holder',model,item))
    return bad

def term(b,attempt,item=None,kind='unattributed_overrun'):
    return dict(type=kind,block_id=b['block_id'],attempt=attempt,parent_block_id=b['parent_block_id'],item_id=item or b['items'][0],model=b['model'],level=b['level'])

def witnesses():
    g,p,reg,r=_split_route(); out={}
    par=next(b for b in r['blocks'] if b['superseded'])
    e=next(e for e in r['envelopes'] if par['block_id'] in e['voided_block_ids'])
    b1=deepcopy(r); ee=b1['envelopes'][e['index']]; ee['voided_block_ids'].remove(par['block_id']); ee['blocks'].append(par['block_id']); out['B1']=b1
    b2=deepcopy(r); n=len(b2['envelopes']); pl=[x for x in b2['placements'] if x['block_id']==par['block_id']][-1]
    b2['envelopes'].append(dict(index=n,model=par['model'],kind='loaded',blocks=[par['block_id']],voided_block_ids=[],observations=None)); b2['placements'].append(dict(pl,envelope_index=n)); out['B2']=b2
    a=deepcopy(r); live={bid for e in a['envelopes'] for bid in e['blocks']}; b=next(b for b in a['blocks'] if b['block_id'] in live and b['parent_block_id'] is None and len(b['items'])==2)
    c=deepcopy(b); c['block_id']+=':999'; a['blocks'].append(c); n=len(a['envelopes']); pl=next(pl for pl in a['placements'] if pl['block_id']==b['block_id'] and b['block_id'] in a['envelopes'][pl['envelope_index']]['blocks'])
    a['envelopes'].append(dict(index=n,model=b['model'],kind='loaded',blocks=[c['block_id']],voided_block_ids=[],observations=None)); a['placements'].append(dict(pl,block_id=c['block_id'],envelope_index=n)); a['terminal_refusals'].extend(term(b,pl['attempt'],item) for item in b['items']); out['AUD-1']=a
    d=deepcopy(r); live={bid for e in d['envelopes'] for bid in e['blocks']}; b=next(b for b in d['blocks'] if b['block_id'] in live and b['parent_block_id'] is None and len(b['items'])==2 and any(pl['block_id']==b['block_id'] and b['block_id'] in d['envelopes'][pl['envelope_index']]['voided_block_ids'] for pl in d['placements']))
    pl=next(pl for pl in d['placements'] if pl['block_id']==b['block_id'] and b['block_id'] in d['envelopes'][pl['envelope_index']]['voided_block_ids']); d['terminal_refusals'].append(term(b,pl['attempt'])); out['probe-D-type-clean']=d
    lc=deepcopy(r); b=next(b for b in lc['blocks'] if b['parent_block_id']==par['block_id'] and b['items']==[par['items'][1]])
    pl=next(pl for pl in lc['placements'] if pl['block_id']==b['block_id'] and b['block_id'] in lc['envelopes'][pl['envelope_index']]['blocks']); ee=lc['envelopes'][pl['envelope_index']]; ee['blocks'].remove(b['block_id']); ee['voided_block_ids'].append(b['block_id']); lc['terminal_refusals'].append(term(b,pl['attempt'])); out['legal-contrast']=lc
    r2=deepcopy(r); next(b for b in r2['blocks'] if b['superseded'])['superseded']=False; out['R2b']=r2
    for m in out.values():
        refresh_derived(g,m); m['sha256']=None
        if m['events']: m['events'][-1]['sha256']=''
    return g,p,reg,out

def formation(g,r):
    for model in g['role_to_model_id'].values():
        for level in range(1,6):
            ids=g['item_ids_by_level'][str(level)]; size=g['block_size'][g['arm']]
            expected=[ids[j:j+size] for j in range(0,len(ids),size)]
            actual=[b['items'] for b in r['blocks'] if b['model']==model and b['level']==level and b['parent_block_id'] is None]
            if actual!=expected: return False
    return True

def seal(reg,m):
    try: sp._structure(reg,m); sp._seal(reg,m,finalize=True); sp._seal(reg,m); return 'ACCEPT'
    except Exception as exc: return str(exc)

def named():
    g,p,reg,ws=witnesses()
    for name,m in ws.items():
        bad=closed(g,m); baseline=seal(reg,m)
        # Checker needs a type-clean digest even when the seal refuses.
        from tests.scored_roster_checker import digest
        m['sha256']=digest(m); m['events'][-1]['sha256']=m['sha256']
        rows=sorted({v.inv_id for v in check_roster(g,m,p)})
        ordered='inv_10 formation' if not formation(g,m) else 'inv_11 item conservation' if bad else 'passes INV-10/11'
        print(f'{name}: closed={"REFUSE" if bad else "PASS"}; baseline={baseline}; ordered_R3={ordered}; checker={rows}')
    assert all(closed(g,ws[n]) for n in ('AUD-1','B1','B2','probe-D-type-clean'))
    assert not closed(g,ws['legal-contrast']) and not closed(g,ws['R2b'])
    print('NAMED predicate expectations PASS; AUD-1 ordered-code conflict REPRODUCED')

def corpus():
    n=0; bad=0; clauses_equal=True
    for seed in range(291013,291017):
        count=0
        for i in range(12):
            c=generate_case(seed,i)
            for r in c.rosters:
                n+=1; count+=1; found=closed(c.g,r); bad+=bool(found)
                clauses_equal &= bool(found)==bool(closed(c.g,r,omit='terminal-holder'))
                if found: print('LEGAL-REFUSAL',seed,i,found[:2])
        print(f'CORPUS seed={seed} cases=12 rosters={count}',flush=True)
    print(f'CORPUS total_cases=48 rosters={n} violations={bad} removal_third_same={clauses_equal}')
    assert bad==0

if __name__=='__main__':
    {'named':named,'corpus':corpus}[sys.argv[1]]()
