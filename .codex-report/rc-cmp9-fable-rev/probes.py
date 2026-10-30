"""RC-CMP9-FABLE-REV probes at f9f86869e (synthetic only), on the producer-complete base (with_sensitivity widened).

P1-P4  the table's conditional entries: both sides say the registered condition is false (over-refusal), and each
       side alone says so (must be non-zero);
P5     the one output-text selector (@ratio);
P6-P8  verdict-only values the table requires as keys but no row binds (sampling words, block flags, identity pins);
P9-P10 the closed lists: an invented line word; a duplicated registered line;
P11    a leave-one-out row dropped from every copy and the recompute (joint drop);
P12    an unregistered item added to a closed list;
P13    over-refusal baseline: with_neg8 + with_references + with_sensitivity, widened and unwidened.
"""
import copy
import sys

sys.path.insert(0, "/home/user/JouleWise")

from tests.independent_recompute import test_comparator  # noqa: E402
from tests.independent_recompute.test_comparator import ALPHA_CELLS, DECODE, PREFILL, cmp, item  # noqa: E402
from tests.independent_recompute.test_input_gate import CODED, GateCase  # noqa: E402
from tests.independent_recompute.test_rc_cmp7 import find, with_neg8, with_references  # noqa: E402
from tests.independent_recompute.test_rc_cmp8 import FAMILY, PROJECTION, REPORTED, SENSITIVITY, with_sensitivity  # noqa: E402
from tests.independent_recompute.test_review_fixes import DISCLOSURE, FILL, VERDICTS  # noqa: E402

CELL_WORDS = cmp.CELL_WORDS


class P(GateCase):
    def runTest(self):
        pass


def case(widened=True):
    c = P()
    c.setUp()
    with_sensitivity(c, widened=widened)
    return c


def run(c):
    try:
        code, err, out = c.exit_code(CODED)
    except cmp.Refusal as exc:
        return 2, f"refused={exc}", {}
    return code, err.strip(), out


def fails(out):
    return {f: n["fail"] for f, n in out.get("counts", {}).items() if n["fail"]} if out and "counts" in out else None


def show(label, c, limit=6):
    code, err, out = run(c)
    extra = ""
    rows = out.get("comparisons", []) if out else []
    bad = [r for r in rows if r["verdict"] != "AGREE"]
    table = [r for r in bad if r["key"].startswith("expected/")]
    other = [r for r in bad if not r["key"].startswith("expected/")]
    if table:
        extra += f"\n    table rows DISAGREE ({len(table)}): " + "; ".join(
            r["key"][9:] + (" missing=" + ",".join(r.get("missing", []))[:160] if r.get("missing") else "") for r in table[:limit])
    if other:
        extra += f"\n    other rows DISAGREE ({len(other)}): " + "; ".join(
            f"{r['key']}=({r['l9']!r:.30},{r['recompute']!r:.30})" for r in other[:limit])
    if out and "coverage" in out:
        ub = sorted({(u["path"], u["reason"]) for u in out["coverage"]["unbound"]})[:3]
        if ub:
            extra += f"\n    unbound={ub}"
    print(f"{label}: exit={code} err={err!r} fails={fails(out)}{extra}")
    return code, out


def rows_of(c, cid=DECODE):
    return [next(r for r in rows if r["contrast_id"] == cid)
            for rows in (c.files[VERDICTS]["contrasts"], c.files[FILL]["gamma"]["contrasts"])]


def l9_reported_refused(c):
    """L9 says ALPHA's decode reported cell is refused (below the registered minimum) in every copy."""
    proj = c.files[PROJECTION]
    proj["cells"] = [x for x in proj["cells"] if x["cell_id"] != REPORTED]
    proj["refused_cells"].append({"cell_id": REPORTED, "code": "paper_reported_energy_kept_units_below_minimum"})
    refused = {"pack": "alpha", "cell_id": REPORTED, "status": "refused", "code": "paper_reported_energy_kept_units_below_minimum"}
    for record in (c.files[SENSITIVITY], c.files[DISCLOSURE]["sensitivity"]):
        record["reported_cells"] = [refused if r["cell_id"] == REPORTED else r for r in record["reported_cells"]]
    for line in c.files[DISCLOSURE]["block_lines"]:
        if line["line"] == "sensitivity_reported" and line["record"].get("cell_id") == REPORTED:
            line["record"] = dict(refused)
    c.files[DISCLOSURE]["cells"] = [x for x in c.files[DISCLOSURE]["cells"]
                                    if not (x.get("cell_id") == REPORTED and x["line"] in CELL_WORDS)]


def ours_reported_refused(c):
    """The recompute says the same cell is below_minimum (independent_recompute_b5 reported cell status)."""
    c.ours["reported_cells"][FAMILY] = {"status": "below_minimum", "n_r": 2, "n_b": 2}
    c.ours["disclosures"]["sensitivity_bound"]["reported_cells"][FAMILY] = {"status": "below_minimum"}
    c.ours["disclosures"]["battery_assist"].pop(FAMILY, None)
    c.ours["disclosures"]["cross_window"].pop("Qwen3-1.7B-4bit/decode", None)


print("=" * 8, "P0 control")
show("P0 control (base + with_sensitivity widened)", case())

print("=" * 8, "P1/P2 reported_computed (a registered condition: the cell is computed on either side)")
c = case(); l9_reported_refused(c); ours_reported_refused(c)
show("P1 both sides refuse ALPHA's decode reported cell (condition false on both sides; the table must pass; OPEN ISSUE 1 expected elsewhere)", c, 12)
c = case(); l9_reported_refused(c)
show("P2.a L9 refuses, the recompute computes (must be non-zero)", c)
c = case(); ours_reported_refused(c)
show("P2.b L9 computes, the recompute refuses (must be non-zero)", c)

print("=" * 8, "P3 floor_computed (extraction floor below the minimum on both sides)")
EXTRACTION = f"mint/{test_comparator.SHA}-extraction-alpha.json"
KEY = "Qwen3-1.7B-4bit/decode/absolute"


def l9_floor_refused(c):
    for cell in c.files[EXTRACTION]["cells"]:
        if cell["cell_id"] == ALPHA_CELLS["absolute"]:
            cell.pop("operative_floor_j", None); cell.pop("n_admitted", None); cell["floor"] = None
    c.files[DISCLOSURE]["floors"] = [x for x in c.files[DISCLOSURE]["floors"]
                                     if not (x["line"] == "floor_composition" and x["cell_id"] == ALPHA_CELLS["absolute"])]


def ours_floor_refused(c):
    c.ours["floors"][KEY] = {"status": "below_minimum", "n": 2}


c = case(); l9_floor_refused(c); ours_floor_refused(c)
show("P3 both sides: the decode absolute floor is below the minimum (condition false both sides)", c, 12)
c = case(); l9_floor_refused(c)
show("P3.a L9 omits the floor, the recompute computes it (must be non-zero)", c)
c = case(); ours_floor_refused(c)
show("P3.b L9 prints the floor, the recompute refuses it (must be non-zero)", c)

print("=" * 8, "P4 ratio_computable (magnitude ratio not computable on both sides)")


def l9_ratio_bare(c):
    lines, index = find(c, "magnitude_ratio", lambda row: row["contrast_id"] == DECODE)
    for key in ("log_mean", "log_sd", "ratio", "lower", "upper"):
        lines[index].pop(key)
    lines[index]["text"] = DECODE + ": registered descriptive estimates: ratio not computable"


def ours_ratio_none(c):
    c.ours["descriptive"][DECODE].update(ratio=None, ratio_interval=None)


c = case(); l9_ratio_bare(c); ours_ratio_none(c)
show("P4 both sides: ratio not computable", c)
c = case(); l9_ratio_bare(c)
show("P4.a L9 bare line, recompute has a ratio (must be non-zero)", c)
c = case(); ours_ratio_none(c)
show("P4.b L9 prints estimates, recompute has none (must be non-zero)", c)

print("=" * 8, "P5 the @ratio text selector (the one selector read from printed text)")
c = case()
lines, index = find(c, "dominance_ratio", lambda row: row["component"] == "absolute")
lines[index]["text"] = lines[index]["text"].replace(": R ", ": R_cm ")
show("P5.a an independent ratio line's text says R_cm (its entry must be MISSING; the common-mode entry duplicated)", c)
c = case()
lines, index = find(c, "dominance_ratio", lambda row: row["component"] == "absolute")
lines[index]["text"] = "no ratio word here"
show("P5.b the text carries no ratio word", c)

print("=" * 8, "P6-P8 verdict-only words the table requires as keys")
c = case()
verdict, _ = rows_of(c)
verdict["sampling"]["removed_block_ids"] = []
show("P6.a verdict sampling/removed_block_ids emptied (fill copy intact)", c)
c = case()
verdict, _ = rows_of(c)
verdict["sampling"]["kept_n"] = 5
show("P6.b verdict sampling/kept_n = 5 against n = 9", c)
c = case()
verdict, _ = rows_of(c)
verdict["bundle_blocks"]["blocks"][0]["included"] = None
show("P7.a the not-kept block's included word set to null (engine forbids a non-bool)", c)
c = case()
verdict, _ = rows_of(c)
verdict["bundle_blocks"]["blocks"][0]["block_id"] = "d117-decode-contrast-b99"
show("P7.b the not-kept block relabelled to an unregistered id", c)
c = case()
c.files[FILL]["gamma"]["finalized_manifest"]["file_sha256"] = "9" * 64
show("P8 fill finalized_manifest/file_sha256 differs from the registry's manifest pin (identity, declared uncovered)", c)

print("=" * 8, "P9-P10 closed lists")
c = case()
c.files[DISCLOSURE]["cells"].append(item("invented_cell_line", True, "alpha x: 1 J", pack="alpha", cell_id=REPORTED, value_j=1.0))
show("P9.a an invented line word in cells (not in CELL_WORDS)", c)
c = case()
c.files[DISCLOSURE]["cells"].append(item("load_correlated_cell", True, "alpha x: sensitivity", pack="alpha", cell_id=REPORTED,
                                         restored_counts={}, families=[], values={}))
show("P9.b a producer-conditional load_correlated_cell line (uncovered LOAD_LINE)", c)
c = case()
lines, index = find(c, "neg8_screen")
lines.append(copy.deepcopy(lines[index]))
show("P10.a alpha's neg8_screen line printed twice (DUPLICATE selector)", c)
c = case()
c.files[PROJECTION]["cells"].append(copy.deepcopy(c.files[PROJECTION]["cells"][0]))
show("P10.b ALPHA's decode projection cell printed twice", c)

print("=" * 8, "P11 joint leave-one-out drop (kept block b03, both copies and the recompute)")
c = case()
block = test_comparator.KEPT[DECODE][1]
for row in rows_of(c):
    row["loo"]["rows"] = [r for r in row["loo"]["rows"] if r["omitted_block_id"] != block]
position = test_comparator.BLOCKS[DECODE].index(block) + 1
c.ours["contrasts"][DECODE]["loo"] = [r for r in c.ours["contrasts"][DECODE]["loo"] if r["block_number"] != position]
show("P11.a b03's row dropped from the verdict, the fill and the recompute (block still kept)", c)
c = case()
for row in rows_of(c):
    row["loo"]["rows"] = [r for r in row["loo"]["rows"] if r["omitted_block_id"] != block]
show("P11.b b03's row dropped from the verdict and the fill only", c)

print("=" * 8, "P12 an item outside the table")
c = case()
c.files[FILL]["gamma"]["contrasts"].append(copy.deepcopy(c.files[FILL]["gamma"]["contrasts"][0]))
c.files[FILL]["gamma"]["contrasts"][-1]["contrast_id"] = "ctr-unregistered"
show("P12.a an unregistered contrast row added to the fill", c)
c = case()
c.files[SENSITIVITY]["floor_cells"].append(dict(c.files[SENSITIVITY]["floor_cells"][0], cell_id="d117-unregistered-floor"))
c.files[DISCLOSURE]["sensitivity"] = copy.deepcopy(c.files[SENSITIVITY])
show("P12.b an unregistered floor cell row added to the record and its copy", c)

print("=" * 8, "P13 over-refusal baseline")
for widened in (True, False):
    c = case(widened)
    with_neg8(c); with_references(c)
    code, out = show(f"P13 with_neg8 + with_references + with_sensitivity(widened={widened})", c)
    rows = out.get("comparisons", [])
    print(f"    rows={len(rows)} non-AGREE={sum(r['verdict'] != 'AGREE' for r in rows)} "
          f"table rows={sum(r['key'].startswith('expected/') for r in rows)}")
