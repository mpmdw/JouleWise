import ast, subprocess, sys
from pathlib import Path
sys.path.insert(0, "tests")
from test_bfgs_consumer_sweep import sweep_source
cases = {
 "V7 lambda": "g = lambda r: r.raw_summary()\n",
 "V8 def under if": "import os\nif os.environ.get('X'):\n    def f(r):\n        return r.raw_summary()\n",
 "V8b def under try": "try:\n    import foo\nexcept ImportError:\n    def f(r):\n        return r.raw_summary()\n",
 "V9 __main__": "import sys\nfrom joulewise.bundle_read import BundleReader\nif __name__ == '__main__':\n    print(BundleReader(sys.argv[1]).raw_summary()['gross_energy_j'])\n",
 "V9b main open": "if __name__ == '__main__':\n    print(open('b/summary_metrics.json').read())\n",
 "control def": "def f(r):\n    return r.raw_summary()\n",
 "B5 map": "def f(rs):\n    return list(map(lambda r: r.raw_summary(), rs))\n",
}
for k, src in cases.items():
    print(f"{k:22s} ->", sweep_source("scripts/zz_new.py", src) or "SILENT")
# tree stats: accident-plausible scopes
paths = subprocess.check_output(["git","ls-files","-z","joulewise","scripts"]).decode().split("\0")
mains=nested_compound=lambdas=partials=maps_fn=getattr_str=0
for p in paths:
    if not p.endswith(".py"): continue
    t = ast.parse(Path(p).read_text())
    for n in ast.walk(t):
        if isinstance(n, ast.If) and isinstance(n.test, ast.Compare) and isinstance(n.test.left, ast.Name) and n.test.left.id=="__name__": mains+=1
        if isinstance(n,(ast.If,ast.Try,ast.With,ast.For,ast.While)):
            for c in ast.walk(n):
                if c is not n and isinstance(c,(ast.FunctionDef,ast.AsyncFunctionDef)): nested_compound+=1; break
        if isinstance(n, ast.Lambda): lambdas+=1
        if isinstance(n, ast.Call):
            nm = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func,"id","")
            if nm=="partial": partials+=1
            if nm=="map" and n.args and isinstance(n.args[0],(ast.Name,ast.Attribute)): maps_fn+=1
            if nm=="getattr" and len(n.args)>=2 and isinstance(n.args[1],ast.Constant): getattr_str+=1
print(dict(files=len([p for p in paths if p.endswith('.py')]), main_blocks=mains, compound_with_nested_def=nested_compound, lambdas=lambdas, partial_calls=partials, map_with_named_fn=maps_fn, getattr_const=getattr_str))
