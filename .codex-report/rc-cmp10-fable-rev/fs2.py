"""RC-CMP10-FABLE-REV FS2 probes at 1affc4208 (synthetic only): the p42 code route (question 3)."""
import copy
import sys

sys.path.insert(0, "/home/user/JouleWise")
from tests.independent_recompute import producer_fixtures, test_comparator, test_rc_cmp10  # noqa: E402
from tests.independent_recompute.test_comparator import cmp  # noqa: E402
from tests.independent_recompute.test_input_gate import CODED  # noqa: E402
from tests.independent_recompute.test_rc_cmp8 import FAMILY, PROJECTION, REPORTED, SENSITIVITY  # noqa: E402
from tests.independent_recompute.test_review_fixes import DISCLOSURE  # noqa: E402

P42 = "df-ph-prefill-p42-qwen3-1p7b"


class P(test_rc_cmp10.Case):
    def runTest(self):
        pass


def case():
    c = P(); c.base(); return c


def run(c):
    try:
        code, err, out = c.exit_code(CODED)
    except cmp.Refusal as exc:
        return 2, f"refused={exc}", {}
    return code, err.strip(), out


def show(label, c):
    code, err, out = run(c)
    bad = [r for r in out.get("comparisons", []) if r["verdict"] != "AGREE"][:4]
    print(f"{label}: exit={code} err={err!r}" + (" rows: " + "; ".join(r["key"] for r in bad) if bad else ""))
    return code


def copies(c, code, which=None):
    test_rc_cmp10.P42CodeTests.copies(c, code, which)


def p42_rows(c):
    rec = next(r for r in c.files[SENSITIVITY]["reported_cells"] if r["cell_id"].find("-p42-") >= 0)
    proj = next(r for r in c.files[PROJECTION]["refused_cells"] if r["cell_id"].find("-p42-") >= 0)
    return rec, proj


c = case()
rec, proj = p42_rows(c)
print("control: p42 cell", rec["cell_id"], "status", rec["status"], "code", rec["code"], "| issuer's code:", producer_fixtures.p42_refusal_code())
show("S0 control", c)
c = case(); copies(c, cmp.BELOW_MINIMUM_CODE)
show("S1 p42 code = the below-minimum code in every copy (a member code for a different exit)", c)
zero = []
for code in cmp.REPORTED_REFUSAL_CODES:
    c = case(); copies(c, code)
    if run(c)[0] == 0:
        zero.append(code)
print(f"S2 every member code in every copy: {len(zero)} of {len(cmp.REPORTED_REFUSAL_CODES)} exit 0")
c = case(); copies(c, "paper_reported_energy_not_a_code")
show("S3 a non-member code in every copy", c)
c = case(); copies(c, "paper_reported_energy_schema_invalid", "projection")
show("S4 the projection copy differs from the record copies", c)
c = case()
proj = c.files[PROJECTION]
proj["refused_cells"] = [r for r in proj["refused_cells"] if "-p42-" not in r["cell_id"]]
show("S5 the projection lists no refused p42 cell (record copies keep the code)", c)
c = case()
proj = c.files[PROJECTION]
proj["cells"].append(dict(copy.deepcopy(proj["cells"][0]), cell_id=p42_rows(c)[1]["cell_id"]))
show("S6 the p42 cell also printed as a computed projection cell", c)
c = case()
rec, _ = p42_rows(c)
for record in (c.files[SENSITIVITY], c.files[DISCLOSURE]["sensitivity"]):
    row = next(r for r in record["reported_cells"] if "-p42-" in r["cell_id"])
    row.pop("code", None)
for line in c.files[DISCLOSURE]["block_lines"]:
    if line["line"] == "sensitivity_reported" and "-p42-" in line["record"].get("cell_id", ""):
        line["record"].pop("code", None)
show("S7 the record copies print no code (projection keeps it)", c)
c = case()
c.ours["p42"][P42]["status"] = "computed"
show("S8 the recompute's p42 status is not expected_unresolvable", c)
c = case()
rec, _ = p42_rows(c)
for record in (c.files[SENSITIVITY], c.files[DISCLOSURE]["sensitivity"]):
    row = next(r for r in record["reported_cells"] if "-p42-" in r["cell_id"])
    row["status"] = "computed"
for line in c.files[DISCLOSURE]["block_lines"]:
    if line["line"] == "sensitivity_reported" and "-p42-" in line["record"].get("cell_id", ""):
        line["record"]["status"] = "computed"
show("S9 the record copies say status computed (projection still refuses)", c)
# A non-p42 (extractable) cell refused on both sides must carry the below-minimum code, not just any member.
c = case(); test_rc_cmp10.l9_reported_refused(c); test_rc_cmp10.ours_reported_refused(c)
show("S10 control: decode reported cell refused on both sides with the below-minimum code", c)
c = case(); test_rc_cmp10.l9_reported_refused(c); test_rc_cmp10.ours_reported_refused(c)
for name in (PROJECTION,):
    for row in c.files[name]["refused_cells"]:
        if row["cell_id"] == REPORTED:
            row["code"] = "paper_reported_energy_record_invalid"
for record in (c.files[SENSITIVITY], c.files[DISCLOSURE]["sensitivity"]):
    for row in record["reported_cells"]:
        if row["cell_id"] == REPORTED:
            row["code"] = "paper_reported_energy_record_invalid"
for line in c.files[DISCLOSURE]["block_lines"]:
    if line["line"] == "sensitivity_reported" and line["record"].get("cell_id") == REPORTED:
        line["record"]["code"] = "paper_reported_energy_record_invalid"
show("S11 the same with a member code that is not the below-minimum code in every copy", c)
