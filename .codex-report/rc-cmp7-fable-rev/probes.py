"""RC-CMP7-FABLE-REV probes at c372211bf, on the lane's own producer-shaped fixture (synthetic only)."""
import copy
import sys

sys.path.insert(0, "/home/user/JouleWise")
from unittest import mock  # noqa: E402

from tests.independent_recompute import test_comparator  # noqa: E402
from tests.independent_recompute.test_comparator import SHA, cmp, item  # noqa: E402
from tests.independent_recompute.test_input_gate import CODED, GateCase  # noqa: E402
from tests.independent_recompute.test_review_fixes import DISCLOSURE  # noqa: E402
from tests.independent_recompute.test_rc_cmp7 import ALPHA_KEPT, find, with_neg8  # noqa: E402

REREDUCED = "rereduced/alpha/run-a.rereduced.json"


class P(GateCase):
    def runTest(self):
        pass


def case():
    c = P()
    c.setUp()
    return c


def run(c):
    try:
        code, err, out = c.exit_code(CODED)
    except cmp.Refusal as exc:
        return 2, f"refused={exc}", {}
    return code, err.strip(), out


def fails(out):
    return {f: n["fail"] for f, n in out.get("counts", {}).items() if n["fail"]} if out and "counts" in out else None


def show(label, c, keys=()):
    code, err, out = run(c)
    extra = ""
    if out and "coverage" in out:
        ub = sorted({(u["path"], u["reason"]) for u in out["coverage"]["unbound"]})[:3]
        if ub:
            extra += f" unbound={ub}"
    for key in keys:
        row = next((r for r in out.get("comparisons", []) if r["key"] == key), None)
        extra += f" row[{key}]={(row['l9'], row['recompute'], row['verdict']) if row else None}"
    print(f"{label}: exit={code} err={err!r} fails={fails(out)}{extra}")
    return code, out


def neg8_screen(c, decision="passed"):
    with_neg8(c, ("alpha",))
    c.files[DISCLOSURE]["window_lines"]["alpha"].append(
        item("neg8_screen", True, f"alpha: NEG-8 screen {decision}", decision=decision))
    c.ours["windows"]["ALPHA"]["neg8"]["screen_decision"] = "passed"
    return c


print("=" * 8, "G7: the run universe")
c = case()
show("G7.0 control (fixture)", c)

c = case()
c.files[ALPHA_KEPT] = test_comparator.kept_units_record("alpha", [])
c.files.pop(REREDUCED)
show("G7.a L9-only drop: kept-units omits run-a, no re-reduced file, recompute selects it", c, ["run/alpha/run-a"])

c = case()
c.files[ALPHA_KEPT] = test_comparator.kept_units_record("alpha", [])
c.files.pop(REREDUCED)
c.ours["members"]["ALPHA"]["run-a"]["selected"] = False
show("G7.b joint drop (shared exclusions): kept-units omits, no re-reduced, recompute unselected", c, ["run/alpha/run-a"])

c = case()
c.files[ALPHA_KEPT] = test_comparator.kept_units_record("alpha", [])
c.files.pop(REREDUCED)
del c.ours["members"]["ALPHA"]["run-a"]
show("G7.b2 joint drop, recompute member absent entirely", c)

c = case()
c.files[ALPHA_KEPT] = test_comparator.kept_units_record("alpha", [])
c.files.pop(REREDUCED)
c.ours["members"]["ALPHA"]["run-a"]["selected"] = False
c.ours["exclusions_rederivation"]["ALPHA"]["status"] = "disagrees"
show("G7.b3 joint drop but the recompute's re-derivation disagrees with the stored exclusions", c)

c = case()
c.files[ALPHA_KEPT] = test_comparator.kept_units_record("alpha", ["run-a", "d117fq31p7-df-ph-decode-abs-r02"])
show("G7.c kept-units wrongly adds a registered science run neither side holds", c,
     ["run/alpha/d117fq31p7-df-ph-decode-abs-r02"])

c = case()
c.files[ALPHA_KEPT]["cells"] = []
show("G7.d kept-units record with cells as a list (malformed): universe silently empty", c, ["run/alpha/run-a"])

c = case()
unit = c.files[ALPHA_KEPT]["cells"][test_comparator.ALPHA_CELLS["absolute"]]["kept"]["repeat"][0]
unit["run_ids"] = "run-a"
show("G7.e kept unit run_ids as a string (iterates characters)", c)

c = case()
del c.ours["members"]["ALPHA"]["run-a"]
show("G7.f recompute member absent, L9 keeps and re-reduces", c, ["run/alpha/run-a"])


def science_universe(custody):
    universe, records = {}, {}
    for pack in cmp.PACKS:
        records[pack] = custody.one(cmp.KEPT_UNITS % pack)
        for rid, role in custody.registry.roles[pack].items():
            if role == "science":
                universe[(pack, rid)] = rid
    return universe, records


c = case()
with mock.patch.object(cmp, "step_2_universe", science_universe):
    code, out = show("G7.g counterfactual: universe = the sealed plan trees' science/* (no exclusions subtracted)", c)
print("   routing_id DISAGREE rows:", sum(r["family"] == "routing_id" and r["verdict"] != "AGREE" for r in out["comparisons"]),
      "of which both sides None:", sum(r["family"] == "routing_id" and r["l9"] is None and r["recompute"] is None
                                       for r in out["comparisons"]))

print("=" * 8, "F2: categorical words on window lines the fixture lacks")
c = neg8_screen(c := case())
show("F2.a control: neg8_screen passed on both sides", c, ["disclosure/alpha/neg8_screen/decision"])
c = neg8_screen(case(), "failed")
show("F2.b wrong word: L9 prints failed, recompute passed", c)
c = neg8_screen(case(), "failed")
lines, index = find(c, "neg8_screen")
lines[index]["line"] = lines[index]["label"] = "adapter_continuity"
show("F2.c wrong word relabelled as adapter_continuity (same producer key set: decision)", c)
c = neg8_screen(case())
lines, index = find(c, "neg8_screen")
lines.pop(index)
show("F2.d neg8_screen line dropped, recompute has a screen decision", c)
c = case()
lines, index = find(c, "below_screen_bound")
lines.pop(index)
show("F2.e below_screen_bound line dropped (alpha), recompute has b_op", c)
c = neg8_screen(case())
c.files[DISCLOSURE]["window_lines"]["alpha"].append(
    item("battery_temperature_sentence", True, "alpha stage s: ...", stage_id="s", rise_k=4.0, neg8="failed"))
show("F2.f battery_temperature_sentence/neg8 differs from the neg8_screen word", c)
c = neg8_screen(case())
c.files[DISCLOSURE]["window_lines"]["alpha"].append(
    item("battery_temperature_sentence", True, "alpha stage s: ...", stage_id="s", rise_k=4.0, neg8="passed"))
show("F2.f2 control: battery_temperature_sentence/neg8 equal", c)

print("=" * 8, "F2: by-construction booleans")
for word in ("mean_and_half_width_equal_primary", "bound_independent_values_equal_primary"):
    c = case()
    c.files[DISCLOSURE]["sensitivity"]["reported_cells"][0][word] = False
    lines, index = find(c, "sensitivity_reported")
    lines[index]["record"][word] = False
    show(f"F2.g {word}=False printed in the sensitivity record and its block-line copy", c)

print("=" * 8, "F2: gate-passing relabel sweep (every fixture line into every word whose producer key set admits it)")
base = neg8_screen(case())
base.files[DISCLOSURE]["window_lines"]["alpha"].append(
    item("battery_temperature_sentence", True, "alpha stage s: ...", stage_id="s", rise_k=4.0, neg8="passed"))
code, _, _ = run(base)
print("sweep base exit:", code)
record = base.files[DISCLOSURE]
sources = [(sec, i, row) for sec in ("cells", "floors", "contrasts", "fixed_sentences", "block_lines")
           for i, row in enumerate(record[sec])]
sources += [(("window_lines", pack), i, row) for pack, rows in record["window_lines"].items() for i, row in enumerate(rows)]
common = set(cmp.LINE_COMMON)
exits, tried = [], 0
for sec, i, row in sources:
    keys = set(row) - common
    for target_sec, words in cmp.LINE_KEYS.items():
        for word in words:
            if (target_sec, word) == (sec[0] if isinstance(sec, tuple) else sec, row["line"]):
                continue
            allowed = set(cmp.LINE_KEYS[target_sec][word])
            if not keys <= allowed or (allowed and not keys & allowed):
                continue
            tried += 1
            c = neg8_screen(case())
            c.files[DISCLOSURE]["window_lines"]["alpha"].append(
                item("battery_temperature_sentence", True, "alpha stage s: ...", stage_id="s", rise_k=4.0, neg8="passed"))
            rec = c.files[DISCLOSURE]
            src_list = rec["window_lines"][sec[1]] if isinstance(sec, tuple) else rec[sec]
            moved = src_list.pop(i)
            moved["line"] = moved["label"] = word
            (rec["window_lines"]["alpha"] if target_sec == "window_lines" else rec[target_sec]).append(moved)
            code, err, out = run(c)
            if code == 0:
                exits.append((sec, row["line"], target_sec, word, sorted(keys)))
print(f"sweep: {tried} gate-passing relabels tried; exit-0 relabels: {len(exits)}")
for e in exits:
    print("   exit 0:", e)
