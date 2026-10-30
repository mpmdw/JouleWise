import sys; sys.path.insert(0, sys.argv[1])
from joulewise.b5_analysis.steps import classify_step4_exit as c, step4_reason_classes
mask, tool = step4_reason_classes()
M, T = sorted(mask)[0], sorted(tool)[0]
spec = {"cells": [{"cell_id": "a", "kind": "absolute", "condition_family_id": "f-p42-x"},
                  {"cell_id": "b", "kind": "absolute", "condition_family_id": "f-p17-x"},
                  {"cell_id": "c", "kind": "comparative", "condition_family_id": "f-p17-y"}]}
def rep(a=None, b=None, cc=None):
    def cell(i, v):
        d = {"cell_id": i, "extractable": True, "refusal_reasons": [], "floor": 1.0}
        if v is not None: d = {"cell_id": i, "extractable": False, **v}
        return d
    return {"cells": [cell("a", a), cell("b", b), cell("c", cc)], "spec_membership_refusals": []}
class S(str): pass
cases = {
 "b tooling only": dict(b={"refusal_reasons": [T], "floor": None}),
 "b mixed mask+tooling": dict(b={"refusal_reasons": [M, T], "floor": None}),
 "b unlisted": dict(b={"refusal_reasons": ["zzz_new_code"], "floor": None}),
 "b empty-string reason": dict(b={"refusal_reasons": [""], "floor": None}),
 "b mask, c tooling": dict(b={"refusal_reasons": [M], "floor": None}, cc={"refusal_reasons": [T], "floor": None}),
 "b mask dup": dict(b={"refusal_reasons": [M, M], "floor": None}),
 "b empty, floor None": dict(b={"refusal_reasons": [], "floor": None}),
 "b empty, floor 0.0": dict(b={"refusal_reasons": [], "floor": 0.0}),
 "b empty, floor False": dict(b={"refusal_reasons": [], "floor": False}),
 "b empty, no floor key": dict(b={"refusal_reasons": []}),
 "b mask, floor present": dict(b={"refusal_reasons": [M], "floor": 3.0}),
 "b reasons None": dict(b={"refusal_reasons": None, "floor": None}),
 "b reasons tuple": dict(b={"refusal_reasons": (M,), "floor": None}),
 "b reasons str": dict(b={"refusal_reasons": M, "floor": None}),
 "b reasons dict": dict(b={"refusal_reasons": {M: 1}, "floor": None}),
 "b reasons [int]": dict(b={"refusal_reasons": [1], "floor": None}),
 "b reasons [str-subclass mask]": dict(b={"refusal_reasons": [S(M)], "floor": None}),
 "b reasons [None]": dict(b={"refusal_reasons": [None], "floor": None}),
 "b no reasons key": dict(b={"floor": None}),
 "a p42 tooling only": dict(a={"refusal_reasons": [T], "floor": None}),
 "a p42 malformed": dict(a={"refusal_reasons": None}),
 "a p42 tooling + b tooling": dict(a={"refusal_reasons": [T], "floor": None}, b={"refusal_reasons": [T], "floor": None}),
 "a p42 tooling + b mask": dict(a={"refusal_reasons": [T], "floor": None}, b={"refusal_reasons": [M], "floor": None}),
 "a p42 mask + b tooling": dict(a={"refusal_reasons": [M], "floor": None}, b={"refusal_reasons": [T], "floor": None}),
 "b mask + reason w/ whitespace": dict(b={"refusal_reasons": [M, T + " "], "floor": None}),
}
for name, kw in cases.items():
    print(f"{name:34s} exit1={c(1, rep(**kw), spec):34s} exit0={c(0, rep(**kw), spec)}")
# extractable True cell carrying tooling reasons while b refused with mask
r = rep(b={"refusal_reasons": [M], "floor": None}); r["cells"][2]["refusal_reasons"] = [T]
print("c extractable w/ tooling + b mask   ", c(1, r, spec))
