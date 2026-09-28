import json, sys, copy
import os; REPO=os.getcwd(); sys.path.insert(0, REPO)
from joulewise import floor_extraction as fe
g=json.load(open(REPO+"/tests/fixtures/d117_postcollection_trust/extraction_report.json"))
ids=[m["bundle_id"] for c in g["cells"] for m in c["members"]]
def v(label, mutate):
    r=copy.deepcopy(g); mutate(r); print(f"{label}: {fe.validate_d117_mint_consumption_report(r)}")
v("1 key absent (report written before S1)", lambda r: None)
v("2 every member pass", lambda r: r.update(battery_float_members={i:"pass" for i in ids}))
v("3 one member unobserved_historical", lambda r: r.update(battery_float_members={**{i:"pass" for i in ids}, ids[0]:"unobserved_historical"}))
v("4 one member not_applicable", lambda r: r.update(battery_float_members={**{i:"pass" for i in ids}, ids[0]:"not_applicable"}))
v("5 one member battery_float_confounded", lambda r: r.update(battery_float_members={**{i:"pass" for i in ids}, ids[1]:"battery_float_confounded"}))
v("6 one cell member has no status", lambda r: r.update(battery_float_members={i:"pass" for i in ids[1:]}))
v("7 value is a list", lambda r: r.update(battery_float_members=["pass"]))
v("8 extra window member not in any cell", lambda r: r.update(battery_float_members={**{i:"pass" for i in ids}, "window-extra":"pass"}))
v("9 unknown key still refused", lambda r: r.update(floor_mint_postcollection={}))
v("10 a cell member whose bundle_id is a list", lambda r: (r.update(battery_float_members={i:"pass" for i in ids}), r["cells"][0]["members"][0].update(bundle_id=["x"])))
