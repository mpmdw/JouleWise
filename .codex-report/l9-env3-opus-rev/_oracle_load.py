"""Load e1b3a0510:joulewise/reduce.py as an independent module (no repo edits)."""
import hashlib, importlib.util, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_e1b():
    src = subprocess.run(["git", "show", "e1b3a0510:joulewise/reduce.py"], cwd=ROOT,
                         check=True, capture_output=True).stdout
    name = "_opusrev_e1b_reduce"
    if name in sys.modules:
        return sys.modules[name], hashlib.sha256(src).hexdigest()
    spec = importlib.util.spec_from_loader(name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = str(ROOT / "joulewise/reduce.py")
    sys.modules[name] = mod
    exec(compile(src, "e1b3a0510:joulewise/reduce.py", "exec"), mod.__dict__)
    return mod, hashlib.sha256(src).hexdigest()
