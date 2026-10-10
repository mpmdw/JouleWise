# Prints key names, value types and container lengths of a whole-window verdict file. No values.
import json, sys
def shape(v, depth, prefix):
    if isinstance(v, dict):
        for k in sorted(v):
            x = v[k]
            t = type(x).__name__ + (("[%d]" % len(x)) if isinstance(x, (list, dict, str)) and not isinstance(x, str) else "")
            print("  " * depth + str(k)[:60], t)
            if depth < 2 and isinstance(x, dict): shape(x, depth + 1, prefix)
            if depth < 2 and isinstance(x, list) and x and isinstance(x[0], dict):
                print("  " * (depth + 1) + "[0] keys:", sorted(x[0])[:25])
for plan in sys.argv[1:]:
    p = json.load(open("/Users/edr/night-custody/%s/night_plan.json" % plan))["hazard_window"]["runs_roots"]["claim"]
    raw = open(p + "/whole-window-verdict.json").read()
    print("==", plan, "bytes", len(raw))
    try: d = json.loads(raw)
    except ValueError: print("not json"); continue
    print("top type", type(d).__name__)
    shape(d if isinstance(d, dict) else {"list0": d[0] if d else None, "len": len(d)}, 0, "")
