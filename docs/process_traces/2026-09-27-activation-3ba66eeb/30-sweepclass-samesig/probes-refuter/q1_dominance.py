# Enclosing branches of the AXI gate (7848) vs the consumers-form consuming calls, run_axi_spec_campaign @315364b2
import ast
src=open('scripts/run_campaign.py').read(); t=ast.parse(src)
fn=[n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name=='run_axi_spec_campaign'][0]
def chain(node,target,path):
    for field,val in ast.iter_fields(node):
        for c in (val if isinstance(val,list) else [val]):
            if isinstance(c,ast.AST):
                if c is target: return path
                r=chain(c,target,path+[(type(node).__name__,field,getattr(node,'lineno',None))])
                if r is not None: return r
for ln in (7686,7848,8034,8047,8115):
    c=[n for n in ast.walk(fn) if isinstance(n,ast.Call) and n.lineno==ln][0]
    print(ln,[(a,b,l) for a,b,l in chain(fn,c,[]) if a in ('If','For','While','Try','With','IfExp','BoolOp','ExceptHandler','Match')])
