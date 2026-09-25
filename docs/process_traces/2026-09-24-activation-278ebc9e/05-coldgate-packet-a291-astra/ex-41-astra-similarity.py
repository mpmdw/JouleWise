import ast, inspect, io, keyword, tokenize
from collections import Counter
from joulewise import scored_packer as sp
from tests import scored_roster_checker as ck
from tests.test_scored_roster_checker import refresh_derived

def lines(fn, canonical=False):
    src=inspect.getsource(fn)
    if canonical: src=ast.unparse(ast.parse(src))
    result=[]; row=[]
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        t,s,*_=tok
        if t in (tokenize.NEWLINE, tokenize.NL):
            if row: result.append(' '.join(row)); row=[]
        elif t in (tokenize.INDENT,tokenize.DEDENT,tokenize.COMMENT,tokenize.ENDMARKER): continue
        else: row.append('N' if t==tokenize.NAME and not keyword.iskeyword(s) else '#' if t==tokenize.NUMBER else s)
    return result

def ratio(a,b,canonical=False):
    x,y=lines(a,canonical),set(lines(b,canonical))
    return sum(v in y for v in x),len(x)
for canonical in (False,True):
    for a,b in ((ck._derived,sp._derived),(ck._derived,sp.executed_status),(ck._derived,sp._structure),(ck.check_executed,sp.executed_status),(ck.check_executed,sp._structure),(refresh_derived,sp._derived),(refresh_derived,sp._structure)):
        n,d=ratio(a,b,canonical)
        print(f'SIM canonical={canonical} checker={a.__name__} packer={b.__name__} {n}/{d}={n/d:.6f}')
