"""Run mutants in a /tmp git worktree: apply, run the two seat modules, restore.

usage: mutation_runner.py WORKTREE NAME [NAME ...]   (prints one line per mutant)
"""
import os, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mutants import MUTANTS
tree = Path(sys.argv[1])
env = dict(os.environ, JW_B5_SYNTHETIC_ONLY="1", PYTHONDONTWRITEBYTECODE="1",
           TMPDIR=os.environ.get("TMPDIR", "/tmp/lnine-env5/tmp"))
MODULES = ["tests.test_whole_window_inverted_corner_clamp", "tests.test_whole_window_analysis_clamp_flag"]
for name in sys.argv[2:]:
    originals = {}
    try:
        for rel, old, new in MUTANTS[name]:
            path = tree / rel
            src = originals.setdefault(rel, path.read_text(encoding="utf-8"))
            cur = path.read_text(encoding="utf-8")
            assert cur.count(old) == 1, (name, rel, cur.count(old))
            path.write_text(cur.replace(old, new), encoding="utf-8")
        t = time.time()
        r = subprocess.run([sys.executable, "-m", "unittest", *MODULES], cwd=tree, env=env,
                           capture_output=True, text=True, timeout=3600)
        lines = r.stderr.splitlines()
        ran = next((l for l in reversed(lines) if l.startswith("Ran ")), "")
        last = lines[-1] if lines else ""
        failed = sorted({l.split(" ")[1] for l in lines if l.startswith(("FAIL: ", "ERROR: "))})
        verdict = "SURVIVED" if r.returncode == 0 else "KILLED"
        print(f"{name} | {verdict} | {ran} | {last} | {','.join(failed)}", flush=True)
    finally:
        for rel, src in originals.items():
            (tree / rel).write_text(src, encoding="utf-8")
    assert subprocess.run(["git", "-C", str(tree), "diff", "--quiet"]).returncode == 0
