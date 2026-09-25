import ast, inspect, io, keyword, tokenize
from joulewise import scored_packer as sp
from tests import scored_roster_checker as ck

def normal(src):
    result=[];row=[]
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type in (tokenize.NEWLINE,tokenize.NL):
            if row:result.append(' '.join(row));row=[]
        elif t.type in (tokenize.INDENT,tokenize.DEDENT,tokenize.COMMENT,tokenize.ENDMARKER):continue
        else:row.append('N' if t.type==tokenize.NAME and not keyword.iskeyword(t.string) else '#' if t.type==tokenize.NUMBER else t.string)
    return result

def metric(src,ref):
    xs=normal(src);ys=set(normal(ref));n=sum(x in ys for x in xs);return f'{n}/{len(xs)}={n/len(xs):.6f}'
# Pure formatting rewrite: parenthesize each expression and put each token on
# its own physical line inside the parentheses. No executable behavior changes.
class Wrap(ast.NodeTransformer):
    def visit(self,node):
        node=super().visit(node)
        if isinstance(node,ast.expr) and not isinstance(node,(ast.Starred,ast.Slice)):
            # Only wrap whole statement expressions below; token splitting is enough.
            pass
        return node
src=inspect.getsource(ck._derived);tree=ast.parse(src)
# Parenthesize complete RHS expressions in assignments, return and if guards.
for n in ast.walk(tree):
    if isinstance(n,ast.Assign) and isinstance(n.value,ast.expr):
        pass
chunks=src.splitlines(keepends=True)
def offset(line,col): return sum(map(len,chunks[:line-1]))+col
replacements=[]
for node in ast.walk(tree):
    if isinstance(node,ast.Assign):
        v=node.value
        expr=ast.get_source_segment(src,v)
        toks=[t.string for t in tokenize.generate_tokens(io.StringIO(expr).readline) if t.type not in (tokenize.NEWLINE,tokenize.NL,tokenize.INDENT,tokenize.DEDENT,tokenize.ENDMARKER)]
        replacements.append((offset(v.lineno,v.col_offset),offset(v.end_lineno,v.end_col_offset),'(\n'+'\n'.join(toks)+'\n)'))
wrapped=src
for start,end,value in sorted(replacements,reverse=True):wrapped=wrapped[:start]+value+wrapped[end:]
print('FORMAT AST_IDENTICAL',ast.dump(ast.parse(src),include_attributes=False)==ast.dump(ast.parse(wrapped),include_attributes=False))
for fn in (sp._derived,sp.executed_status,sp._structure):
    print('FORMAT checker=_derived packer='+fn.__name__,metric(wrapped,inspect.getsource(fn)))
print('BASE control',metric(src,inspect.getsource(sp._structure)))
