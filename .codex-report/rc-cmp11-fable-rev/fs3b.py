"""RC-CMP10-FABLE-REV: the proposed FS3 closure (BI2) as a one-line change to Comparison.atom: a test whose number
and threshold are bit-identical on both sides is decided (both sides evaluate the same test on the same binary64
values; no family prints at reduced precision, recompute_bars.json has no printed_decimals). Battery: sound windows,
the 8 wrong words of fs3.py B, the full-size b10 flip, the b10 identical case, holm at alpha, below at the bound;
then the existing WithinBarTests / SensitivityFixtureTests / ConditionalFamilyTests / LeaveOneOutTests under BI2."""
import io
import sys
import unittest
from unittest import mock

sys.path.insert(0, "/home/user/JouleWise")
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fs3  # noqa: E402  (runs the fs3 battery again on import; its output precedes this)
from tests.independent_recompute import test_rc_cmp8, test_rc_cmp10  # noqa: E402
from tests.independent_recompute.test_comparator import BLOCKS, DECODE, cmp  # noqa: E402

ORIG_ATOM = fs3.ORIG_ATOM


def atom_bi2(self, name, family, key, l9, ours, threshold, test, l9_threshold=cmp.MISSING):
    a = ORIG_ATOM(self, name, family, key, l9, ours, threshold, test, l9_threshold)
    lt = threshold if l9_threshold is cmp.MISSING else l9_threshold
    if a["within"] and cmp.finite(l9) and cmp.finite(ours) and l9 == ours and lt == threshold:
        a["within"] = False  # bit-identical numbers and thresholds: both sides evaluate the same test
    return a


print("=" * 8, "E. BI2 (bit-identical numbers decide): the same battery")
with mock.patch.object(cmp.Comparison, "atom", atom_bi2):
    for widened in (True, False):
        code, err, out = fs3.run(fs3.case(widened))
        und = [r for r in out["comparisons"] if r.get("reason") == "within_bar_undetermined"]
        print(f"E BI2 sound widened={widened}: exit={code} err={err!r} undetermined rows={len(und)}")
    caught = 0
    for (widened, section, index, word, closure), head in fs3.results.items():
        if closure != "head" or head[0] != 0 or head[2] == head[3]:
            continue
        c = fs3.case(widened)
        if section == "windows":
            fs3.flip_widened(c, index)
        else:
            fs3.flip(c, section, index, word)
        code = fs3.run(c)[0]
        caught += code != 0
        print(f"E BI2 wrong word widened={widened} {section}[{index}].{word}: exit={code}")
    print(f"E BI2 catches {caught} of 8 wrong words")
    c = fs3.case(); test_rc_cmp10.set_loo(c, BLOCKS[DECODE][9], 3.55e-15, -1.78e-15, ["estimate_sign"])
    code, err, out = fs3.run(c)
    r = next((r for r in out.get("comparisons", []) if r["key"] == f"{DECODE}/loo/b10/influence_triggers/0"), {})
    print(f"E BI2 full-size b10 flip inside the bar: exit={code} row={r.get('verdict')}/{r.get('reason')}")
    c = fs3.case(); test_rc_cmp10.set_loo(c, BLOCKS[DECODE][9], 3.55e-15, 3.55e-15, [])
    print(f"E BI2 b10 identical +3.55e-15 both sides, L9 prints no trigger: exit={fs3.run(c)[0]}")
    c = fs3.case(); test_rc_cmp10.set_loo(c, BLOCKS[DECODE][9], 3.55e-15, 3.55e-15, ["estimate_sign"])
    print(f"E BI2 b10 identical +3.55e-15 both sides, both print the trigger: exit={fs3.run(c)[0]}")
    c = fs3.case(); test_rc_cmp10.set_loo(c, BLOCKS[DECODE][9], 3.55e-15, 3.5500000000000004e-15, [])
    print(f"E BI2 b10 one ulp apart (+3.55e-15 vs +3.5500000000000004e-15), L9 prints no trigger: exit={fs3.run(c)[0]}")
    print("=" * 8, "F. the existing tests under BI2 (a failure marks a test that encodes a wrong word passing)")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (test_rc_cmp10.WithinBarTests, test_rc_cmp10.ConditionalFamilyTests, test_rc_cmp10.LeaveOneOutTests,
                test_rc_cmp8.SensitivityFixtureTests):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    print(f"F ran={result.testsRun} failures={len(result.failures)} errors={len(result.errors)}")
    for test, trace in result.failures + result.errors:
        print("F FAIL:", test.id())
        print("   ", trace.strip().splitlines()[-1][:300])
