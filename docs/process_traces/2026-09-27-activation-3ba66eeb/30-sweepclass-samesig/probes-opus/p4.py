# Which tolerant calls / watched-file reads in the tree lie in scopes the repo detector never visits?
import ast, subprocess, sys
from pathlib import Path
sys.path.insert(0,"tests")
import test_bfgs_consumer_sweep as S
paths=[p for p in subprocess.check_output(["git","ls-files","-z","joulewise","scripts"]).decode().split("\0") if p.endswith(".py")]
extra=[]; total=0
for p in paths:
    t=ast.parse(Path(p).read_text()); seen=set()
    for q,fn in S._qualified_functions(t):
        for n in S._function_nodes(fn): seen.add(id(n))
    for n in ast.walk(t):
        if isinstance(n,ast.Call):
            nm=S._name(n)
            hit = nm in S.TOLERANT or (nm in S.READS and any(isinstance(c,ast.Constant) and c.value in S.FILES for c in ast.walk(n)))
            if hit:
                total+=1
                if id(n) not in seen: extra.append((p,n.lineno,nm))
print("watched call sites:",total,"in unvisited scopes:",len(extra)); print(extra)
