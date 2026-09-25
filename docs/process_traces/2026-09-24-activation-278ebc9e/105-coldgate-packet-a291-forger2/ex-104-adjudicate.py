import sys, runpy, json, copy
sys.path.insert(0, '/tmp/forger-278ebc9e-fable')           # joulewise snapshot of 6e2504b1 + forger modules
sys.path.insert(1, '/Users/edr/code/wt-278ebc9e-a291p3')   # tests/ oracle + checker at the integrated head
import forge_common
captured = []
orig = forge_common.reseal
def rec(reg, r):
    res = orig(reg, r)
    captured.append((reg, res[1] if res[0] == 'ACCEPTED' else r, res[0]))
    return res
forge_common.reseal = rec
labels = []; resmaps = []
for mod in ('forge_candidates', 'forge_more'):
    sys.modules.pop(mod, None)
    g = runpy.run_path(f'/tmp/forger-278ebc9e-fable/{mod}.py', init_globals={'reseal': rec}, run_name='__adj__')
    labels += list(g['results'].keys()); resmaps.append(g['results'])
from tests.scored_ownership_oracle import ownership_violations
from tests.scored_roster_checker import check_roster
out = []
byid = {id(c[1]): c for c in captured if c[2]=='ACCEPTED'}
allres = {}
for m in resmaps: allres.update(m)
pairs = []
for label in labels:
    st, o = allres[label]
    if st == 'ACCEPTED':
        c = byid[id(o)]; pairs.append((label, (c[0], o, st)))
    else:
        pairs.append((label, (None, None, st)))
for label, (reg, roster, status) in pairs:
    if status != 'ACCEPTED':
        out.append((label, status[:60], None, None, None)); continue
    g = reg.to_mapping()
    ov = ownership_violations(g, roster)
    try:
        rows = sorted({v.inv_id for v in check_roster(g, roster, forge_common.predictions(reg))})
    except Exception as e:
        rows = [f'CHECKER-CRASH {type(e).__name__}: {e}']
    esc = bool(ov) or any(x in ('INV-10', 'INV-11') for x in rows)
    verdict = 'ESCAPE' if esc else ('OUT_OF_ROUND' if rows else 'OUT_OF_ROUND(no rows)')
    out.append((label, status, [str(v)[:120] for v in ov], rows, verdict))
for o in out:
    print(json.dumps(o))
print('LEN labels', len(labels), 'captured', len(captured))
