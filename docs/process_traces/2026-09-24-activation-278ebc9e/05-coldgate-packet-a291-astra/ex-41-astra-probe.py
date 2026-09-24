import copy, inspect, ast
from unittest.mock import patch
from joulewise import scored_packer as sp, scored_registration as sr
from tests.scored_roster_checker import check_roster, digest
from tests.test_scored_registration import fixture

def reseal(r):
    d=digest(r);r['sha256']=d
    if r['events']: r['events'][-1]['sha256']=d
    else: r['registered_sha256']=d
    return r

def pending(r): return next(e for e in r['envelopes'] if e['kind']=='loaded' and e['observations'] is None)
def keep(e): return [dict(block_id=b,status='completed',elapsed_s=.01) for b in e['blocks']]
def outcome(fn):
    try: fn();return 'RETURN'
    except Exception as e: return f'{type(e).__name__}:{getattr(e,"code","")}:{e}'
def ids(g,r,p): return sorted({v.inv_id for v in check_roster(g,r,p)})

g,p=fixture(n=10,block_size=2,cap=6.0);reg=sr.Registration.from_mapping(g);root=sp.pack(reg,p)
r=root; states=[r]; split=None
while any(e['kind']=='loaded' and e['observations'] is None for e in r['envelopes']):
    e=pending(r);bm={b['block_id']:b for b in r['blocks']};obs=[]
    for j,bid in enumerate(e['blocks']):
        b=bm[bid];status='completed';elapsed=.01
        if not r['events']:status='cut_off' if j==0 else 'not_started';elapsed=1.3 if j==0 else None
        elif b['retry_stage']=='whole_block':status='cut_off';elapsed=.1
        elif bid=='large:decode:1:0:single:0':elapsed=reg.worst(b['model'])*1.01
        obs.append(dict(block_id=bid,status=status,elapsed_s=elapsed))
    r=sp.requeue_overrun(reg,r,e['index'],obs);states.append(r)
    if any(x['decision']=='split' for x in r['events'][-1]['observations']):split=r
final=r
print('ROUTE split_events',len(split['events']),'pending',pending(split)['index'],'final_events',len(final['events']))
print('R4a baseline',final['drift_lever_slots']['1'],'hand',abs(sum([13,2,4,6,8])/5-sum([1,3,5,7,9])/5),'fully_nonterminal_counterfactual',0.0,'shortfall',final['planned_spread_shortfall']['large:1'],'checker',ids(g,final,p))

mutants={}
x=copy.deepcopy(root);pl=x['placements'][0];n=len(x['envelopes']);x['envelopes'].append(dict(index=n,model='large',kind='loaded',blocks=[pl['block_id']],voided_block_ids=[],observations=None));x['placements'].append(dict(pl,envelope_index=n));mutants['R1']=x
x=copy.deepcopy(root);bids={b['block_id'] for b in x['blocks'] if b['model']=='large' and b['level']==1}
for e in x['envelopes']:
    moved=[bid for bid in e['blocks'] if bid in bids];e['blocks']=[bid for bid in e['blocks'] if bid not in bids];e['voided_block_ids']+=moved
mutants['R2']=x
x=copy.deepcopy(split);next(b for b in x['blocks'] if b['block_id']=='large:decode:1:0')['superseded']=False;mutants['R2b']=x
# Ten concrete operators, use non-root split or terminal final when needed.
x=copy.deepcopy(root);e=x['envelopes'][0];bid=e['blocks'].pop(0);e['voided_block_ids'].append(bid);mutants['op1']=x
mutants['op2']=copy.deepcopy(mutants['R1'])
x=copy.deepcopy(final);x['terminal_refusals'].pop();mutants['op3']=x
x=copy.deepcopy(root);b=x['blocks'][0];x['terminal_refusals'].append(dict(type='unattributed_overrun',block_id=b['block_id'],attempt=0,parent_block_id=None,item_id=b['items'][0],model=b['model'],level=b['level']));mutants['op4']=x
x=copy.deepcopy(split);x['blocks'].remove(next(b for b in x['blocks'] if b['parent_block_id'] is not None));mutants['op5']=x
mutants['op6']=copy.deepcopy(mutants['R2b'])
x=copy.deepcopy(root);x['placements'][0]['envelope_index']=1;mutants['op7']=x
x=copy.deepcopy(root);x['blocks'][0]['late']=True;mutants['op8']=x
x=copy.deepcopy(split);x['events'][0]['sha256']='0'*64;mutants['op9']=x
x=copy.deepcopy(root);x['placements'][0]['attempt']+=1;mutants['op10']=x

def submit(x):
    es=[e for e in x['envelopes'] if e['kind']=='loaded' and e['observations'] is None]
    if es: return sp.requeue_overrun(reg,x,es[0]['index'],keep(es[0]))
    import random
    rng=random.Random(291013);keys={(pl['block_id'],pl['attempt']) for pl in x['placements'] if rng.random()<.75}
    return sp.executed_status(reg,x,p,keys)
for name,x in mutants.items():
    for sealed in (False,True):
        y=copy.deepcopy(x)
        if sealed:reseal(y)
        sp._TRUSTED_OUTPUTS.clear()
        print('BASE',name,'resealed',sealed,outcome(lambda:submit(y)),'checker',ids(g,y,p))
# R5a intentionally calls production finalize, as its defining witness requires.
x=copy.deepcopy(root);x['blocks'][0]['late']=True;x['sha256']=None
print('R5a finalize',outcome(lambda:sp._seal(reg,x,finalize=True)),'cached_requeue',outcome(lambda:submit(x)))
sp._TRUSTED_OUTPUTS.clear();print('R5a uncached_requeue',outcome(lambda:submit(x)))
print('R4c baseline derived_body',len(ast.parse(inspect.getsource(sp._derived)).body[0].body),'has_live',hasattr(sp,'_live'))
print('R5b baseline trusted_container',hasattr(sp,'_TRUSTED_OUTPUTS'))

# Literal model of new INV-11/12, fact builder, and lever; NOT a delivered implementation.
def new_rows(reg,r):
    bm={b['block_id']:b for b in r['blocks']};terms={(t['model'],t['item_id']) for t in r['terminal_refusals']}
    count=lambda b:sum(b['block_id'] in e['blocks'] for e in r['envelopes'])
    for m in sp._roles(reg):
        for item in sp._items(reg):
            blocks=[b for b in r['blocks'] if b['model']==m and item in b['items']]
            a=sum(not b['superseded'] and not all((m,i) in terms for i in b['items']) and count(b)==1 for b in blocks)==1
            b=sum(t['model']==m and t['item_id']==item for t in r['terminal_refusals'])==1 and not any(count(b) for b in blocks)
            sp._need(a!=b,'inv_11','item conservation')
    for b in r['blocks']:
        if b['parent_block_id'] is not None:
            parent=bm.get(b['parent_block_id'])
            sp._need(parent is not None and parent['superseded'] and len(b['items'])==1 and parent['model']==b['model'] and parent['level']==b['level'] and any(b['block_id']==f"{parent['block_id']}:single:{j}" and b['items']==[it] for j,it in enumerate(parent['items'])),'inv_12','single relation')
        elif b['superseded']:
            singles=[s for s in r['blocks'] if s['parent_block_id']==b['block_id']]
            sp._need([s['items'][0] for s in singles]==b['items'],'inv_12','partition')
def facts(reg,r,keys=None):
    live={}
    for e in r['envelopes']:
        for bid in e['blocks']:
            sp._need(bid not in live,'inv_11',f'duplicate live placement {bid}')
            live[bid]=next(pl for pl in r['placements'] if pl['block_id']==bid and pl['envelope_index']==e['index'])
    terms={(t['model'],t['item_id']) for t in r['terminal_refusals']};out=[]
    for b in r['blocks']:
        if b['parent_block_id'] is not None:continue
        ix=[]
        for item in b['items']:
            if (b['model'],item) in terms:continue
            owner=b if not b['superseded'] else next((s for s in r['blocks'] if s['parent_block_id']==b['block_id'] and s['items']==[item]),None)
            pl=live.get(owner['block_id']) if owner is not None else None
            if pl is not None and (keys is None or (pl['block_id'],pl['attempt']) in keys):ix.append(pl['envelope_index'])
        out.append(dict(parent_id=b['block_id'],model=b['model'],level=b['level'],n_items=len(b['items']),n_terminal=sum((b['model'],i) in terms for i in b['items']),indices=ix))
    return out

def lever(reg,fs,executed=False):
    gate=lambda f:len(f['indices'])==f['n_items'] if executed else f['n_terminal']==0
    for f in fs:
        if gate(f):sp._need(len(f['indices'])==f['n_items'],'inv_11',f"gate parent without full live positions {f['parent_id']}")
    flags={};positions={};counts={}
    for lv in sr.LEVELS:
        for m in sp._roles(reg):
            cell=[f for f in fs if f['model']==m and f['level']==lv];gs=[f for f in cell if gate(f)]
            positions[m,lv]=[sum(f['indices'])/len(f['indices']) for f in cell if f['indices']]
            counts[m,lv]=len(gs);flags[f'{m}:{lv}']=len(gs)<sr.MIN_PARENT_BLOCKS or len({i for f in gs for i in f['indices']})<sr.MIN_ENVELOPES
    result={}
    for lv in sr.LEVELS:
        a,b=sp._roles(reg);xs,ys=positions[a,lv],positions[b,lv]
        result[str(lv)]=abs(sum(xs)/len(xs)-sum(ys)/len(ys)) if counts[a,lv] and counts[b,lv] else None
    return flags,result
oldstructure=sp._structure

def text_seal(reg,r):
    try:
        d=sp._digest(r);sp._need(r['sha256']==d,'inv_02','digest mismatch')
        sp._need(r['registered_sha256']==(d if not r['events'] else r['registered_sha256']),'inv_38','root digest')
        if r['events']:sp._need(r['events'][-1]['sha256']==d,'inv_38','event digest')
        oldstructure(reg,r);new_rows(reg,r);short,lv=lever(reg,facts(reg,r))
    except sp.PackingRefusal:raise
    except (KeyError,TypeError,ValueError,IndexError,StopIteration,AttributeError) as exc:raise sp.PackingRefusal('inv_52','malformed roster') from exc
    except ArithmeticError as exc:raise sp.PackingRefusal('inv_52',f'internal:{type(exc).__name__}') from exc
    sp._need(r['planned_spread_shortfall']==short and r['drift_lever_slots']==lv,'stale_derived','derived values')
    # These probes use legal roots or changed roots with otherwise unchanged root minima.
    sp._replay_roster(reg,r)
for name,x in mutants.items():
    print('TEXT_MODEL',name,'resealed',outcome(lambda x=x:text_seal(reg,reseal(copy.deepcopy(x)))),'unresealed',outcome(lambda x=x:text_seal(reg,copy.deepcopy(x))))
print('R4b TEXT_MODEL',outcome(lambda:lever(reg,[dict(parent_id='p',model='large',level=1,n_items=2,n_terminal=0,indices=[])])))
print('R4a TEXT_MODEL',lever(reg,facts(reg,final))[1]['1'])
# Produce a legal final roster with no nonterminal large parents.
gz,pz=fixture(n=5,block_size=1,cap=6.0);rzreg=sr.Registration.from_mapping(gz);z=sp.pack(rzreg,pz)
while any(e['kind']=='loaded' and e['observations'] is None for e in z['envelopes']):
    e=pending(z);obs=[dict(block_id=bid,status='not_started' if e['model']=='large' else 'completed',elapsed_s=None if e['model']=='large' else .01) for bid in e['blocks']]
    z=sp.requeue_overrun(rzreg,z,e['index'],obs)
print('EMPTY_PARENT legal_base_checker',ids(gz,z,pz),'base_lever',z['drift_lever_slots']['1'])
empty=copy.deepcopy(z['blocks'][0]);empty.update(block_id='large:decode:1:999',items=[],predicted_item_s=[],predicted_s=0,attempt=0,retry_stage='initial',superseded=False,late=False)
z['blocks'].append(empty);reseal(z)
print('EMPTY_PARENT structure',outcome(lambda:oldstructure(rzreg,z)),'INV11_12',outcome(lambda:new_rows(rzreg,z)),'fact',facts(rzreg,z)[-1])
print('EMPTY_PARENT baseline',outcome(lambda:sp._seal(rzreg,z)),'TEXT_MODEL',outcome(lambda:text_seal(rzreg,z)),'checker',ids(gz,z,pz))
