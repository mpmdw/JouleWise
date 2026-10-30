"""usage: runner.py WORKTREE SEAT_MUTANTS_PY NAME [NAME ...]; same protocol as the seat's mutation_runner.py."""
import importlib.util, os, subprocess, sys, time
from pathlib import Path
here = Path(__file__).resolve().parent
def load(p):
    s = importlib.util.spec_from_file_location(Path(p).stem, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
tree = Path(sys.argv[1]); M = dict(load(sys.argv[2]).MUTANTS); M.update(load(here / "own_mutants.py").OWN)
env = dict(os.environ, JW_B5_SYNTHETIC_ONLY="1", PYTHONDONTWRITEBYTECODE="1")
MODULES = ["tests.test_whole_window_inverted_corner_clamp", "tests.test_whole_window_analysis_clamp_flag"]
for name in sys.argv[3:]:
    originals = {}
    try:
        for rel, old, new in M[name]:
            path = tree / rel
            cur = originals.setdefault(rel, path.read_text(encoding="utf-8"))
            cur = path.read_text(encoding="utf-8")
            assert cur.count(old) == 1, (name, rel, cur.count(old))
            path.write_text(cur.replace(old, new), encoding="utf-8")
        r = subprocess.run([sys.executable, "-m", "unittest", *MODULES], cwd=tree, env=env, capture_output=True, text=True, timeout=3600)
        lines = r.stderr.splitlines()
        ran = next((l for l in reversed(lines) if l.startswith("Ran ")), "")
        failed = sorted({l.split(" ")[1] for l in lines if l.startswith(("FAIL: ", "ERROR: "))})
        print(f"{name} | {'SURVIVED' if r.returncode == 0 else 'KILLED'} | {ran} | {lines[-1] if lines else ''} | {','.join(failed)}", flush=True)
    finally:
        for rel, src in originals.items():
            (tree / rel).write_text(src, encoding="utf-8")
    assert subprocess.run(["git", "-C", str(tree), "diff", "--quiet"]).returncode == 0
