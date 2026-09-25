import sys, copy
sys.path.insert(0, sys.argv[1])
from tests.scored_case_generator import generate_case
import joulewise.scored_packer as sp
case = generate_case(291013, 0)
r = copy.deepcopy(case.rosters[-1] if hasattr(case,'rosters') else case.roster)
x = []
cur = x
for _ in range(1200):
    nxt = []; cur.append(nxt); cur = nxt
r['sha256'] = x
for fin in (False,):
    try:
        sp._seal(case.reg if hasattr(case,'reg') else case.registration, r, finalize=fin); print('ACCEPTED')
    except sp.PackingRefusal as e: print('REFUSED', e)
    except RecursionError: print('RecursionError')
