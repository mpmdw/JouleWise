import ast, subprocess, collections
files=['tests/test_run_night.py','tests/test_network_time_window.py','tests/test_launch_window.py']
for f in files:
    old=ast.parse(subprocess.check_output(['git','show','3ad82b43:'+f],text=True))
    new=ast.parse(open(f).read())
    def methods(tree):
        out={}
        for cls in tree.body:
            if isinstance(cls,ast.ClassDef):
                for fn in cls.body:
                    if isinstance(fn,ast.FunctionDef) and fn.name.startswith('test_'):
                        out[cls.name+'.'+fn.name]=collections.Counter(ast.dump(n,include_attributes=False) for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and (n.func.attr.startswith('assert') or n.func.attr=='fail'))
        return out
    a,b=methods(old),methods(new)
    print(f,'old',len(a),'new',len(b))
    for name in sorted(a):
        if name not in b: print('REMOVED_OR_RENAMED',name)
        else:
            delta=a[name]-b[name]
            if delta: print('CHANGED_ASSERTIONS',name,sum(delta.values()))
print('ASSERTION_CENSUS_COMPLETE')
