"""Proposed fix for F1, demonstrated in a scratch copy of the comparator: the two window claim rows
(below_screen_bound/below, neg8_screen/decision) are keyed on the registered packs, not on whether L9 printed
the line; the producer prints both lines on every window (disclosures.py 1100 and _reference_lines 952)."""
import importlib.util, sys
sys.path.insert(0, "/home/user/JouleWise")
src = open("/home/user/JouleWise/scripts/compare_b5_recompute.py").read()
old_below = '''        if "below_screen_bound" in claims:
            c.exact("outcome_word", f"disclosure/{pack}/below_screen_bound/below", claims["below_screen_bound"].get("below"),
                    b_op < SCREEN_BOUND_S if finite(b_op) else None)
        if "neg8_screen" in claims:
            c.exact("outcome_word", f"disclosure/{pack}/neg8_screen/decision", claims["neg8_screen"].get("decision"),
                    get(ours, "windows", PACKS[pack], "neg8", "screen_decision"))
'''
new_below = '''        # Keyed on the registered packs (G7 for words): L9 prints both lines on every window.
        c.exact("outcome_word", f"disclosure/{pack}/below_screen_bound/below", get(claims.get("below_screen_bound"), "below"),
                b_op < SCREEN_BOUND_S if finite(b_op) else None)
        c.exact("outcome_word", f"disclosure/{pack}/neg8_screen/decision", get(claims.get("neg8_screen"), "decision"),
                get(ours, "windows", PACKS[pack], "neg8", "screen_decision"))
'''
assert src.count(old_below) == 1
patched = src.replace(old_below, new_below)
old_root = 'CAMPAIGNS = Path(__file__).resolve().parents[1] / "configs/campaigns"'
assert patched.count(old_root) == 1
patched = patched.replace(old_root, 'CAMPAIGNS = Path("/home/user/JouleWise/configs/campaigns")  # scratch copy')
open("/tmp/claude-0/rcfable/cmp_patched.py", "w").write(patched)
spec = importlib.util.spec_from_file_location("cmp_patched", "/tmp/claude-0/rcfable/cmp_patched.py")
cmp2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(cmp2)
from tests.independent_recompute import test_comparator, test_review_fixes, test_input_gate, test_rc_cmp7
for mod in (test_comparator, test_review_fixes, test_input_gate, test_rc_cmp7):
    mod.cmp = cmp2
from tests.independent_recompute.test_comparator import item
from tests.independent_recompute.test_input_gate import CODED, GateCase
from tests.independent_recompute.test_review_fixes import DISCLOSURE
from tests.independent_recompute.test_rc_cmp7 import find, with_neg8

class P(GateCase):
    def runTest(self): pass

def case(decision="passed"):
    c = P(); c.setUp()
    with_neg8(c)  # every pack: the fixture then holds a NEG-8 result on both sides, as a real window does
    for pack in ("alpha", "beta", "gamma"):
        c.files[DISCLOSURE]["window_lines"][pack].append(item("neg8_screen", True, f"{pack}: NEG-8 screen passed",
                                                              decision=decision if pack == "alpha" else "passed"))
        c.ours["windows"][cmp2.PACKS[pack]]["neg8"]["screen_decision"] = "passed"
    return c

def run(label, c):
    try:
        code, err, out = c.exit_code(CODED)
    except cmp2.Refusal as exc:
        code, err, out = 2, f"refused={exc}", {}
    fails = {f: n["fail"] for f, n in out.get("counts", {}).items() if n["fail"]} if "counts" in out else None
    print(f"{label}: exit={code} err={err.strip()!r} fails={fails}")

run("patched control", case())
c = case("failed"); run("patched F2.b wrong word", c)
c = case("failed"); lines, i = find(c, "neg8_screen"); lines[i]["line"] = lines[i]["label"] = "adapter_continuity"
run("patched F2.c relabelled as adapter_continuity", c)
c = case(); lines, i = find(c, "neg8_screen"); lines.pop(i); run("patched F2.d neg8_screen dropped", c)
c = case(); lines, i = find(c, "below_screen_bound"); lines.pop(i); run("patched F2.e below_screen_bound dropped", c)
