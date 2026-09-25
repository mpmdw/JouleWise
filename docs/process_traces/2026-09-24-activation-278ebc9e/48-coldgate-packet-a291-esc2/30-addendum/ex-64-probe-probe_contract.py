import ast, inspect, itertools, re
from pathlib import Path
from copy import deepcopy
from collections import defaultdict
from unittest.mock import patch
from probe_r3 import witnesses, closed, seal, PACKET
from joulewise import scored_packer as sp
from tests.scored_roster_checker import check_roster, digest

src=inspect.getsource(sp); tree=ast.parse(src)
functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
names={'_structure','_ownership','_live_index','_seal','_predictions'}
codes=defaultdict(list)
for name in sorted(names & functions.keys()):
    for n in ast.walk(functions[name]):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_need' and len(n.args)>1 and isinstance(n.args[1],ast.Constant): codes[n.args[1].value].append((name,n.lineno))
print('AST mandated missing registration codes', sorted({'inv_06','inv_09'}-set(codes)))
for code in ('inv_38','invalid_observation_order','invalid_elapsed','culprit_limit','inv_35c','reschedule_without_culprit'):
    print('AST replay-row overlap',code,codes.get(code))
banned={'blocks','placements','terminal_refusals','envelopes'}
allowed={'_ownership','_live_index','_replay_roster','pack','_place','_new_envelope','requeue_overrun'}
violations=defaultdict(list)
for name,f in functions.items():
    if name in allowed:continue
    for n in ast.walk(f):
        value=None
        if isinstance(n,ast.Subscript) and isinstance(n.slice,ast.Constant): value=n.slice.value
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='get' and n.args and isinstance(n.args[0],ast.Constant):value=n.args[0].value
        if value in banned and not(name=='_structure' and n.lineno<=192): violations[name].append((n.lineno,value))
for name,uses in violations.items():print('AST confinement',name,sorted(uses))
print('AST owner-view counterexample',ast.dump(ast.parse('owner["blocks"]',mode='eval').body,include_attributes=False))
contract=(PACKET/'ex-02d-contract-v4.md').read_text()
rows=set(re.findall(r'^\*\*(INV-[0-9]+(?:/[0-9]+)?)\b.*\(F:',contract,re.M))
explicit={'INV-'+x for x in ('01','02','03','04','05','06','07','08','51','09','10','11','12','14','15','16','17','18','20','21','24','37','52','30','31','32','33/43','35','36','38','39','46','47','48','22','23','25','41','50','26','45','49','29')}
print('MAP headed rows with no explicit disposition', sorted(rows-explicit))
# Exhaust every 2-item/2-block membership, listing, superseded and terminal-count state.
count=0; differ=0
for memberships in itertools.product(((),('a',),('b',),('a','b')),repeat=2):
 for listings in itertools.product(range(3),repeat=2):
  for superseded in itertools.product((False,True),repeat=2):
   for terms in itertools.product(range(3),repeat=2):
    live={x:[j for j,items in enumerate(memberships) for _ in range(listings[j]) if x in items] for x in ('a','b')}
    c1=all((len(live[x]),terms[j]) in ((1,0),(0,1)) for j,x in enumerate(('a','b')))
    c2=all(len(live[x])!=1 or not superseded[live[x][0]] for x in ('a','b'))
    c3=all(len(live[x])!=1 or all(terms[('a','b').index(y)]==0 for y in memberships[live[x][0]]) for x in ('a','b'))
    count+=1; differ+=(c1 and c2)!=(c1 and c2 and c3)
print(f'MUTATION third-clause deletion states={count} distinguishing={differ}')
assert differ==0
# Structurally valid terminal contrast necessarily triggers the checker replay part of INV-37.
g,p,reg,ws=witnesses(); m=ws['legal-contrast']; print('MAP legal-contrast seal',seal(reg,m))
print('MAP legal-contrast INV-37 details',[v.detail for v in check_roster(g,m,p) if v.inv_id=='INV-37'])
# Type-incomplete judge-D cannot reach checker INV-11 even if that row is fixed.
d=deepcopy(ws['probe-D-type-clean']); d['terminal_refusals'][0]['type']='terminal'; d['sha256']=digest(d); d['events'][-1]['sha256']=d['sha256']
print('CHECKER malformed-terminal short-circuit',[(v.inv_id,v.detail) for v in check_roster(g,d,p)])
# K1 + R3-1 structural INV-37 do not check terminal level/parent fields; row 52 types do not repair it.
m=deepcopy(ws['legal-contrast']); m['sha256']=None; m['events'][-1]['sha256']=''; m['terminal_refusals'][0]['level']=2 if m['terminal_refusals'][0]['level']!=2 else 3
blocks={b['block_id']:b for b in m['blocks']}
provenance=all(any(pl['block_id']==t['block_id'] and pl['attempt']==t['attempt'] and t['block_id'] in m['envelopes'][pl['envelope_index']]['voided_block_ids'] and t['item_id'] in blocks[t['block_id']]['items'] for pl in m['placements']) for t in m['terminal_refusals'])
print('PROVENANCE wrong-level literal=',provenance,'closed=',not closed(g,m),'seal=',seal(reg,m))
print('PROVENANCE wrong-level checker=',[(v.inv_id,v.detail) for v in check_roster(g,m,p) if v.inv_id=='INV-37'])
# Inspect the scopes/mandatory stress change by parsing the binding source texts.
ruling=(PACKET/'20-coldgate-fable-esc2-ruling.md').read_text(); v4=(PACKET/'ex-14-a291-final-texts-v4.md').read_text()
assert 'the stress module keeps `test_seeded_300_registration_sequences` and gains one new test' in v4
scope_line=next(x for x in ruling.splitlines() if 'Scopes: K ' in x)
print('SCOPE stress-required=True stress-allowlisted=', 'tests/test_scored_packer_stress.py' in scope_line)
print('FIXTURE judge_probe.py present=',bool(list(PACKET.glob('*judge_probe*'))))
print('CONTRACT probes complete')
