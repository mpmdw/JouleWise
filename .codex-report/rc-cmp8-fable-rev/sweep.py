"""RC-CMP8-FABLE-REV leaf-drop sweep at 0d317afd4: delete each leaf (dict member or list item) of each L9 input and of
the recompute's output, one at a time, on the producer-shaped base (with_sensitivity widened), and record the exit.
An exit 0 after a deletion is a value or word the comparator never required. Synthetic only.
"""
import copy
import sys

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


base = case()
code, err, _ = run(base)
print("base exit:", code, err)
targets = [("l9:" + name, name) for name in sorted(base.files)] + [("recompute", None)]
zero, total, by_code = [], 0, {}
for root_name, name in targets:
    root = base.files[name] if name else base.ours
    positions = list(paths(root))
    for path, key in positions:
        c = case()
        try:
            delete(c.files[name] if name else c.ours, path, key)
        except (KeyError, IndexError, TypeError):
            continue
        total += 1
        code, err, out = run(c)
        by_code[code] = by_code.get(code, 0) + 1
        if code == 0:
            zero.append(label(root_name, path, key))
print(f"deletions tried: {total}; exits: {by_code}")
print(f"exit-0 deletions: {len(zero)}")
for z in zero:
    print("  exit 0:", z)
