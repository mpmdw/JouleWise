"""Candidate closed ownership table: one pass, every listing counted, no filtered subsets."""
from tests.scored_case_generator import generate_case
def ownership(r, models, items):
    blocks={b['block_id']:b for b in r['blocks']}
    live={}  # (model,item) -> [(bid, env)]
    for e in r['envelopes']:
        for bid in e['blocks']:
            b=blocks[bid]
            for x in b['items']: live.setdefault((b['model'],x),[]).append((bid,e['index']))
    term={}
    for t in r['terminal_refusals']: term.setdefault((t['model'],t['item_id']),[]).append(t)
    bad=[]
    for m in models:
        for x in items:
            L=live.get((m,x),[]); T=term.get((m,x),[])
            if (len(L),len(T)) not in ((1,0),(0,1)): bad.append(('count',m,x,len(L),len(T))); continue
            if L and blocks[L[0][0]]['superseded']: bad.append(('superseded-live',m,x))
    return bad
if __name__=='__main__':
    n=0; viol=0
    for seed in (291013,291014,291015,291016):
        for i in range(12):
            c=generate_case(seed,i)
            models=list(c.g['role_to_model_id'].values()); items=[x for l in '12345' for x in c.g['item_ids_by_level'][l]]
            for r in c.rosters:
                n+=1; b=ownership(r,models,items); viol+=bool(b)
                if b: print('LEGAL VIOLATION',seed,i,b[:2])
    print('legal rosters',n,'violations',viol)
