"""RC-CMP9-FABLE-REV leaf-drop sweep at f9f86869e (answer 1): delete each leaf (dict member or list item) of each L9
input and of the recompute's output, one at a time, on the producer-complete base (with_sensitivity widened), and
record the exit. An exit 0 after a deletion is a value, word, object or line the comparator never required.
Synthetic only. Same walk as review/2026-10-29-rc-cmp8-fable-rev sweep.py, run in parallel; the output format is
identical so classify.py applies unchanged.
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, "/home/user/JouleWise")

from tests.independent_recompute.test_comparator import cmp  # noqa: E402
from tests.independent_recompute.test_input_gate import CODED, GateCase  # noqa: E402
from tests.independent_recompute.test_rc_cmp8 import with_sensitivity  # noqa: E402


class P(GateCase):
    def runTest(self):
        pass


def case():
    c = P()
    c.setUp()
    with_sensitivity(c, widened=True)
    return c


def run(c):
    try:
        code, err, out = c.exit_code(CODED)
    except cmp.Refusal as exc:
        return 2, f"refused={exc}", {}
    return code, err.strip(), out


def paths(value, prefix=()):
    """Every deletable position: (path to container, key)."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield prefix, key
            yield from paths(item, prefix + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield prefix, index
            yield from paths(item, prefix + (index,))


def delete(root, path, key):
    node = root
    for step in path:
        node = node[step]
    del node[key]


def label(root_name, path, key):
    return root_name + ":" + "/".join(str(p) for p in path + (key,))


def one(job):
    root_name, name, path, key = job
    c = case()
    try:
        delete(c.files[name] if name else c.ours, path, key)
    except (KeyError, IndexError, TypeError):
        return None
    code, err, out = run(c)
    try:
        c.tmp.cleanup()
    except Exception:
        pass
    return label(root_name, path, key), code, err[:200]


if __name__ == "__main__":
    base = case()
    code, err, _ = run(base)
    print("base exit:", code, err)
    targets = [("l9:" + name, name) for name in sorted(base.files)] + [("recompute", None)]
    jobs = []
    for root_name, name in targets:
        root = base.files[name] if name else base.ours
        for path, key in paths(root):
            jobs.append((root_name, name, path, key))
    print("positions:", len(jobs), flush=True)
    zero, total, by_code = [], 0, {}
    with ProcessPoolExecutor(max_workers=int(os.environ.get("WORKERS", "4"))) as pool:
        for result in pool.map(one, jobs, chunksize=8):
            if result is None:
                continue
            lab, code, err = result
            total += 1
            by_code[code] = by_code.get(code, 0) + 1
            if code == 0:
                zero.append(lab)
    print(f"deletions tried: {total}; exits: {by_code}")
    print(f"exit-0 deletions: {len(zero)}")
    for z in zero:
        print("  exit 0:", z)
