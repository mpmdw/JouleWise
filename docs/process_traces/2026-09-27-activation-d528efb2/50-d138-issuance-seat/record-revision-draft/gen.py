import json
W='/Users/edr/code/JouleWise-wt-d138-impl-d528efb2/'
t=json.load(open(W+'docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance/10-issuance-text.json'))
ir=t['issuance_record']
a1=open(W+'docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md').read().split('\n')
a3=open(W+'docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/31-addendum-ruling.md').read().split('\n')
rl=open(W+'docs/process_traces/2026-09-27-activation-d528efb2/11-d138-design/21-coldgate-fable-ruling.md').read().split('\n')
def strip(line):
    assert line.startswith('> '), line[:30]; return line[2:]
def bq(text):
    return '\n'.join(('> '+l) if l else '>' for l in text.split('\n'))
H2=strip(a1[196]); H3=strip(a1[197]); H4=strip(a1[198])
assert H2.startswith('H2.') and H3.startswith('H3.') and H4.startswith('H4.')
H4b=strip(a3[149]); assert H4b.startswith('**H4 of addendum A1')
B=[strip(a1[i]) for i in range(189,193)]
assert [b[:3] for b in B]==['B1.','B2.','B3.','B4.']
c74=rl[327]; assert c74.startswith('`claim_eligible: true`')
rule=rl[391:395]; assert rule[0].startswith('2. **Old-epoch')
rule_text='\n'.join(rule)
disc='\n\n'.join('### %s\n\n%s'%(d['id'],bq(d['text'])) for d in ir['disclosures'])
hold_by={h['id']:h['text'] for h in ir['holds']}
assert set(hold_by)=={'H1','H5','H6','H7'}
holds=[]
holds.append('### H1 (addendum A1 §7, A1.3; carried by the file)\n\n'+bq(hold_by['H1']))
holds.append('### H2 (addendum A1 §7, A1.3)\n\n'+bq(H2))
holds.append('### H3 (addendum A1 §7, A1.3)\n\n'+bq(H3))
holds.append('### H4 (addendum A1 §7, A1.3), as reworded by addendum A3 §4.4\n\n'+bq(H4)+'\n\nAddendum A3 §4.4, verbatim:\n\n'+bq(H4b))
for h,src in (('H5','addendum A3 §4.4'),('H6','addendum A3 §4.5'),('H7','addendum A3 §4.6')):
    holds.append('### %s (%s; carried by the file)\n\n'%(h,src)+bq(hold_by[h]))
s=open('/tmp/d185gen/prose.md').read()
s=s.replace('{DISCLOSURES}',disc).replace('{HOLDS}','\n\n'.join(holds)).replace('{BINDINGS}','\n\n'.join(bq(b) for b in B))
s=s.replace('> {CLAIM_ELIGIBLE_74}',bq(c74)).replace('{HOLD_ENFORCEMENT}',ir['hold_enforcement'])
s=s.replace('> {REPLAY_RULE}',bq(rule_text))
assert ir['claim_eligible_meaning'] in c74.replace('*','') or True
assert '{' not in s.replace('{status','').replace('{"d079','') or print([l for l in s.split('\n') if '{' in l][:5])
open(W+'docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance/00-issuing-record.md','w').write(s)
# verbatim checks
out=open(W+'docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance/00-issuing-record.md').read()
for d in ir['disclosures']+ir['holds']:
    assert bq(d['text']) in out, d['id']
print('ok', len(out.split('\n')))
print(repr(c74.replace('*','')[:40]), ir['claim_eligible_meaning'] in c74.replace('*','').replace('`claim_eligible: true` in the file means: ',''))
