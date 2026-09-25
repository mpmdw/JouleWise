import ast
from pathlib import Path
from probe_r3 import PACKET
p=Path('tests/test_scored_packer.py')
t=ast.parse(p.read_text())
k={'tests.scored_roster_checker','tests.test_scored_roster_checker','tests.test_scored_packer_fuzz','tests.scored_case_generator'}
imports=[n.module for n in ast.walk(t) if isinstance(n,ast.ImportFrom)]
print('P direct K-owned imports=',sorted(set(imports)&k))
print('R3 refresh_derived module=tests.test_scored_roster_checker K-owned=True')
scopes_k={'tests/scored_roster_checker.py','tests/test_scored_roster_checker.py','tests/test_scored_packer_fuzz.py','tests/scored_case_generator.py'}
scopes_p={'joulewise/scored_packer.py','tests/test_scored_packer.py'}
print('WRITE scope overlap=',sorted(scopes_k&scopes_p))
r3=(PACKET/'20-coldgate-fable-esc2-ruling.md').read_text().split('### K5 (E-5)')[1].split('### K6')[0]
print('FORGER checker-input-granted=', '`tests/scored_roster_checker.py`' in r3)
print('FORGER scratch-path-declared=', '/tmp/' in r3)
print('FORGER inconclusive-outcome-declared=', 'inconclusive' in r3.lower())
print('STOP closed-ownership-only-trigger-declared=', 'closed form' in r3.split('Stop rule')[1])
print('DEPENDENCY and gate probes complete')
