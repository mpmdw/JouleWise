# Run the first judge's amendment-51 prototype (sweep59) on tracked docs/paper and configs Python, outside the sweep's file scope.
import sys, subprocess
sys.path.insert(0, "/tmp/cg_sw_erratum"); sys.path.insert(0, ".")
import sweep59
from pathlib import Path
rows, g = sweep59.run(".")
paths = [p for p in subprocess.check_output(["git","ls-files","-z","docs/paper","configs"]).decode().split("\0") if p.endswith(".py")]
for p in paths:
    out = sweep59.sweep(p, Path(p).read_text(), g)
    for r in sorted({tuple(r[:4]) + (r[-1],) for r in out}): print(r)
print("files:", len(paths))
