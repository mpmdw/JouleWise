# Literal prototype of the refuter's proposed B-2 (iii) and B-3 text, run on "round-3" forms.
import ast
GATE={"authenticate_window_members","BundleReader","bundle_read","battery_float"}
MODS={"joulewise.bundle_read","joulewise.battery_float"}
def last(e):
    if isinstance(e,ast.Name): return e.id
    if isinstance(e,ast.Attribute): return e.attr
    return None
def dotted(e):
    parts=[]
    while isinstance(e,ast.Attribute): parts.append(e.attr); e=e.value
    if isinstance(e,ast.Name): parts.append(e.id); return ".".join(reversed(parts))
    return None
def b2_b3(src):
    t=ast.parse(src); bound=set(); hits=[]
    for n in ast.walk(t):
        if isinstance(n,ast.Import):
            for a in n.names:
                if a.name in MODS: bound.add(a.asname or a.name.split(".")[0])
        if isinstance(n,ast.ImportFrom) and n.module=="joulewise":
            for a in n.names:
                if a.name in {"bundle_read","battery_float"}: bound.add(a.asname or a.name)
    def bad(e): return last(e) in GATE or last(e) in bound or dotted(e) in MODS
    for n in ast.walk(t):
        tg=[]
        if isinstance(n,(ast.Assign,ast.Delete)): tg=n.targets
        if isinstance(n,(ast.AugAssign,ast.AnnAssign)): tg=[n.target]
        for x in tg:
            if isinstance(x,ast.Attribute) and bad(x.value): hits.append(("store",n.lineno))
            if isinstance(x,ast.Attribute) and x.attr=="_path" and not (isinstance(x.value,ast.Name) and x.value.id=="self"): hits.append(("_path",n.lineno))
        if isinstance(n,ast.Call) and last(n.func) in {"setattr","delattr","__setattr__"} and n.args:
            if bad(n.args[0]): hits.append(("setattr",n.lineno))
            if len(n.args)>1 and isinstance(n.args[1],ast.Constant) and n.args[1].value=="_path": hits.append(("setattr_path",n.lineno))
    return hits
C={
 "control V1 battery_float.authenticate_bundle = f":"from joulewise import battery_float\nbattery_float.authenticate_bundle = f\n",
 "W1 importlib.import_module(...).authenticate_bundle = f":"import importlib\nimportlib.import_module('joulewise.battery_float').authenticate_bundle = f\n",
 "W2 sys.modules[...].authenticate_bundle = f":"import sys\nsys.modules['joulewise.battery_float'].authenticate_bundle = f\n",
 "W3 m = battery_float; m.authenticate_bundle = f":"from joulewise import battery_float\nm = battery_float\nm.authenticate_bundle = f\n",
 "W4 battery_float.authenticate_bundle.__code__ = g.__code__":"from joulewise import battery_float\nbattery_float.authenticate_bundle.__code__ = g.__code__\n",
 "W5 vars(battery_float)['authenticate_bundle'] = f":"from joulewise import battery_float\nvars(battery_float)['authenticate_bundle'] = f\n",
 "W6 r.__dict__['_path'] = b":"def f(r,b):\n    r.metadata()\n    r.__dict__['_path'] = b\n    return r.trace_rows()\n",
 "control V6 r._path = b":"def f(r,b):\n    r.metadata()\n    r._path = b\n    return r.trace_rows()\n",
}
for k,s in C.items(): print(f"{k:58s}", b2_b3(s) or "SILENT")
