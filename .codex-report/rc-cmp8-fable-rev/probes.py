"""RC-CMP8-FABLE-REV probes at 0d317afd4 on the lane's producer-shaped fixture (synthetic only).

Sections: S1 output-derived row constructors (drop and relabel probes), S2 the RC-CMP-7 probes re-run,
S3 over-refusal (sound producer-shaped windows). The leaf-drop sweeps are in sweep.py.
"""
import copy
import sys

sys.path.insert(0, "/home/user/JouleWise")
from unittest import mock  # noqa: E402

from tests.independent_recompute import test_comparator  # noqa: E402
from tests.independent_recompute.test_comparator import DECODE, SHA, cmp, item  # noqa: E402
from tests.independent_recompute.test_input_gate import CODED, GateCase  # noqa: E402
from tests.independent_recompute.test_review_fixes import DISCLOSURE, FILL, VERDICTS  # noqa: E402
from tests.independent_recompute.test_rc_cmp7 import ALPHA_KEPT, find  # noqa: E402
from tests.independent_recompute.test_rc_cmp8 import PROJECTION, with_sensitivity  # noqa: E402

REREDUCED = "rereduced/alpha/run-a.rereduced.json"


class P(GateCase):
    def runTest(self):
        pass


def case(sensitivity=False):
    c = P()
    c.setUp()
    if sensitivity:
        with_sensitivity(c, widened=True)
    return c


def run(c):
    try:
        code, err, out = c.exit_code(CODED)
    except cmp.Refusal as exc:
        return 2, f"refused={exc}", {}
    return code, err.strip(), out


def fails(out):
    return {f: n["fail"] for f, n in out.get("counts", {}).items() if n["fail"]} if out and "counts" in out else None


def show(label, c, keys=(), prefix=None):
    code, err, out = run(c)
    extra = ""
    if out and "coverage" in out:
        ub = sorted({(u["path"], u["reason"]) for u in out["coverage"]["unbound"]})[:3]
        if ub:
            extra += f" unbound={ub}"
    for key in keys:
        row = next((r for r in out.get("comparisons", []) if r["key"] == key), None)
        extra += f" row[{key}]={(row['l9'], row['recompute'], row['verdict']) if row else None}"
    if prefix and out:
        n = sum(r["key"].startswith(prefix) for r in out.get("comparisons", []))
        extra += f" rows[{prefix}*]={n}"
    print(f"{label}: exit={code} err={err!r} fails={fails(out)}{extra}")
    return code, out


def verdict_and_fill(c, cid=DECODE):
    return [next(r for r in rows if r["contrast_id"] == cid)
            for rows in (c.files[VERDICTS]["contrasts"], c.files[FILL]["gamma"]["contrasts"])]


def neg8_screen(c, decision="passed"):
    """RC-CMP-8: the base carries every window's NEG-8 lines; set alpha's screen word on both sides."""
    lines, index = find(c, "neg8_screen")
    lines[index]["decision"] = decision
    c.ours["windows"]["ALPHA"]["neg8"]["screen_decision"] = "passed"
    return c


print("=" * 8, "S1: output-derived row constructors")
c = case(True)
show("S1.0 control (base + with_sensitivity widened)", c, prefix="contrast/ctr-")

for key in ("arm_gates", "resolutions"):
    c = case(True)
    for cid in (DECODE, test_comparator.PREFILL):
        for row in verdict_and_fill(c, cid):
            row["floor"].pop(key)
    show(f"S1.a {key} dropped from the verdict and the fill (both contrasts)", c,
         [f"contrast/{DECODE}/arm/0/condition_family_id", f"contrast/{DECODE}/resolution/0/transport_rule_id"],
         prefix=f"contrast/{DECODE}/{key[:-1] if key == 'resolutions' else 'arm'}/")
    c = case(True)
    for cid in (DECODE, test_comparator.PREFILL):
        verdict_and_fill(c, cid)[0]["floor"].pop(key)
    show(f"S1.b {key} dropped from the verdict only (fill keeps its copy)", c)
    c = case(True)
    for cid in (DECODE, test_comparator.PREFILL):
        verdict_and_fill(c, cid)[1]["floor"].pop(key)
    show(f"S1.c {key} dropped from the fill only (verdict keeps it)", c)
    c = case(True)
    for cid in (DECODE, test_comparator.PREFILL):
        for row in verdict_and_fill(c, cid):
            row["floor"][key + "_x"] = row["floor"].pop(key)
    show(f"S1.d {key} relabelled {key}_x in the verdict and the fill", c)
    c = case(True)
    for cid in (DECODE, test_comparator.PREFILL):
        verdict_and_fill(c, cid)[0]["floor"][key + "_x"] = verdict_and_fill(c, cid)[0]["floor"].pop(key)
    show(f"S1.e {key} relabelled in the verdict only", c)

c = case(True)
verdict, fill = verdict_and_fill(c)
verdict["floor"]["arm_gates"][0]["condition_family_id"] = "wrong-condition"
fill["floor"]["arm_gates"][0]["condition_family_id"] = "wrong-condition"
show("S1.f control: a wrong arm-gate condition on both copies", c, [f"contrast/{DECODE}/arm/0/condition_family_id"])
c = case(True)
verdict, fill = verdict_and_fill(c)
verdict["floor"]["resolutions"][0]["transport_rule_id"] = "other_rule.v9"
fill["floor"]["resolutions"][0]["transport_rule_id"] = "other_rule.v9"
show("S1.g control: a wrong transport_rule_id on both copies", c, [f"contrast/{DECODE}/resolution/0/transport_rule_id"])
c = case(True)
verdict, fill = verdict_and_fill(c)
verdict["floor"]["resolutions"][0]["transport_rule_id"] = "other_rule.v9"
fill["floor"]["resolutions"][0]["transport_rule_id"] = "other_rule.v9"
for row in (verdict, fill):
    row["floor"]["resolutions"] = []
show("S1.h resolutions emptied on both copies (list present, no rows)", c, prefix=f"contrast/{DECODE}/resolution/")
c = case(True)
for row in verdict_and_fill(c):
    row["floor"]["arm_gates"] = []
show("S1.i arm_gates emptied on both copies", c, [f"contrast/{DECODE}/arm/0/condition_family_id"])

print("-" * 4, "refused p42 cells of the projection")
P42 = "d117-reported-mean-ph-prefill-p42-qwen3-1p7b"
c = case(True)
c.files[PROJECTION]["refused_cells"] = [{"cell_id": P42, "code": "p42_expected_unresolvable"}]
show("S1.j control: alpha projection lists its refused p42 cell", c, ["alpha/projection/p42"])
c = case(True)
c.files[PROJECTION]["refused_cells"] = [{"cell_id": P42, "code": "p42_expected_unresolvable"}]
c.ours["p42"]["df-ph-prefill-p42-qwen3-1p7b"]["status"] = "computed"
show("S1.k recompute p42 computed, projection refused: the row disagrees (and the extraction row)", c, ["alpha/projection/p42"])
c = case(True)
c.files[PROJECTION].pop("refused_cells")
show("S1.l refused_cells key dropped from the projection", c, ["alpha/projection/p42"])
c = case(True)
c.files[PROJECTION]["refused_cells"] = [{"cell_id": "d117-reported-mean-ph-decode-qwen3-1p7b", "code": "x"}]
show("S1.m refused cell relabelled to the decode reported cell id (no p42 cell listed)", c, ["alpha/projection/p42"])
c = case(True)
c.files[PROJECTION]["refused_cells"] = {"cell_id": P42}
show("S1.n refused_cells as an object", c, ["alpha/projection/p42"])

print("-" * 4, "disclosure lines dropped whole (every line of a word), base + with_sensitivity")
base = case(True)
record = base.files[DISCLOSURE]
words = sorted({(sec, row["line"]) for sec in ("cells", "floors", "contrasts", "fixed_sentences", "block_lines")
                for row in record[sec]} | {("window_lines", row["line"]) for rows in record["window_lines"].values()
                                           for row in rows})
zero = []
for sec, word in words:
    c = case(True)
    rec = c.files[DISCLOSURE]
    if sec == "window_lines":
        for pack in rec["window_lines"]:
            rec["window_lines"][pack] = [r for r in rec["window_lines"][pack] if r["line"] != word]
    else:
        rec[sec] = [r for r in rec[sec] if r["line"] != word]
    code, err, out = run(c)
    print(f"  drop {sec}/{word}: exit={code} err={err!r} fails={fails(out)}")
    if code == 0:
        zero.append((sec, word))
print("line words whose whole-line drop exits 0:", zero)

print("=" * 8, "S2: the RC-CMP-7 probes at this head")
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
show("G7.b joint drop (shared exclusions)", c, ["run/alpha/run-a"])
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
show("G7.b3 joint drop but the recompute's re-derivation disagrees", c)
c = case()
c.files[ALPHA_KEPT] = test_comparator.kept_units_record("alpha", ["run-a", "d117fq31p7-df-ph-decode-abs-r02"])
show("G7.c kept-units wrongly adds a registered science run neither side holds", c,
     ["run/alpha/d117fq31p7-df-ph-decode-abs-r02"])
c = case()
c.files[ALPHA_KEPT]["cells"] = []
show("G7.d kept-units record with cells as a list (malformed)", c, ["run/alpha/run-a"])
c = case()
unit = c.files[ALPHA_KEPT]["cells"][test_comparator.ALPHA_CELLS["absolute"]]["kept"]["repeat"][0]
unit["run_ids"] = "run-a"
show("G7.e kept unit run_ids as a string", c)
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
    code, out = show("G7.g counterfactual: universe = the sealed plan trees' science/*", c)
print("   routing_id DISAGREE rows:", sum(r["family"] == "routing_id" and r["verdict"] != "AGREE" for r in out["comparisons"]),
      "of which both sides None:", sum(r["family"] == "routing_id" and r["l9"] is None and r["recompute"] is None
                                       for r in out["comparisons"]))

print("-" * 4, "F2: window claim words (RC-CMP-7 F1, fixed in RC-CMP-8)")
c = neg8_screen(case())
show("F2.a control: neg8_screen passed on both sides", c, ["disclosure/alpha/neg8_screen/decision"])
c = neg8_screen(case(), "failed")
show("F2.b wrong word: L9 prints failed, recompute passed", c)
c = neg8_screen(case(), "failed")
lines, index = find(c, "neg8_screen")
lines[index]["line"] = lines[index]["label"] = "adapter_continuity"
show("F2.c wrong word relabelled as adapter_continuity", c, ["disclosure/alpha/neg8_screen/decision"])
c = neg8_screen(case())
lines, index = find(c, "neg8_screen")
lines.pop(index)
show("F2.d neg8_screen line dropped, recompute has a screen decision", c, ["disclosure/alpha/neg8_screen/decision"])
c = case()
lines, index = find(c, "below_screen_bound")
lines.pop(index)
show("F2.e below_screen_bound line dropped (alpha), recompute has b_op", c, ["disclosure/alpha/below_screen_bound/below"])
c = neg8_screen(case())
c.files[DISCLOSURE]["window_lines"]["alpha"].append(
    item("battery_temperature_sentence", True, "alpha stage s: ...", stage_id="s", rise_k=4.0, neg8="failed"))
show("F2.f battery_temperature_sentence/neg8 differs from the neg8_screen word", c)
c = neg8_screen(case())
c.files[DISCLOSURE]["window_lines"]["alpha"].append(
    item("battery_temperature_sentence", True, "alpha stage s: ...", stage_id="s", rise_k=4.0, neg8="passed"))
show("F2.f2 control: battery_temperature_sentence/neg8 equal", c)
print("-" * 4, "F2.g: by-construction booleans (RC-CMP-7 F2, fixed in RC-CMP-8)")
for word in ("mean_and_half_width_equal_primary", "bound_independent_values_equal_primary"):
    c = case(True)
    section = "reported_cells" if word.startswith("mean") else "contrasts"
    line = "sensitivity_reported" if word.startswith("mean") else "sensitivity_contrast"
    c.files[DISCLOSURE]["sensitivity"][section][-1][word] = False
    c.files["outputs/" + "1" * 64 + ".json"][section][-1][word] = False
    lines, index = find(c, line)
    lines[index]["record"][word] = False
    show(f"F2.g {word}=False in the record, the disclosure copy and the block line", c)

print("-" * 4, "gate-passing relabel sweep (every fixture line into every word whose producer key set admits it)")
base = neg8_screen(case(True))
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
            c = neg8_screen(case(True))
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

print("=" * 8, "S3: over-refusal on sound producer-shaped windows")
for widened in (True, False):
    c = case()
    with_sensitivity(c, widened=widened)
    code, out = show(f"S3.a with_sensitivity(widened={widened})", c)
    rel = [r for r in out["comparisons"] if r["family"] == "outcome_word" and r["key"].startswith("sensitivity/")]
    print("   sensitivity outcome_word rows:", len(rel), "non-AGREE:", [r["key"] for r in rel if r["verdict"] != "AGREE"])
c = case(True)
for row in c.files[DISCLOSURE]["block_lines"]:
    if row["line"] == "dominance_ratio" and row["component"] == "absolute":
        for key in ("ratio", "numerator_j", "denominator_j"):
            row.pop(key, None)
        row["status"] = "refused"
for row in c.files["finalized/outputs/closeout.ratio-table.json"]["ratios"]:
    if row["component"] == "absolute":
        for key in ("ratio", "numerator_j", "denominator_j"):
            row.pop(key, None)
        row["status"] = "refused"
for key, ratio in c.ours["dominance"]["ratios"].items():
    if key.endswith("/absolute"):
        ratio.pop("R", None)
show("S3.b refused dominance ratios without ratio keys on the line and the table (gate must pass; OPEN ISSUE 2 over-refusal expected)", c)
c = case(True)
for row in c.files[DISCLOSURE]["contrasts"]:
    if row["line"] == "battery_assist_contrast" and row["contrast_id"] == DECODE:
        for key in ("mean_j", "s_d", "se", "t_star", "lower_j", "upper_j"):
            row.pop(key, None)
        row.update(status="not_computable", n=0, assist_quads=9)
c.ours["disclosures"]["battery_assist"][DECODE] = {"n": 0, "assist_quads": 9, "assist_members_by_stratum": {}}
show("S3.c battery_assist_contrast not_computable (n=0) without estimates", c)
c = case(True)
for row in c.files[DISCLOSURE]["window_lines"]["alpha"]:
    if row["line"] == "machine_summary":
        for key in ("median", "minimum", "maximum", "q25", "q75", "spread", "central_band"):
            row.pop(key, None)
show("S3.d machine_summary with model only (no finite rho) [no-op if the base has no such line]", c)
