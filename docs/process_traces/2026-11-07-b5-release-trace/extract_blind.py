"""Blind extraction: emits only identifiers, verdicts, reasons, types, presence and coarse relative-difference buckets."""
import json, math, sys, re
src, out = sys.argv[1], sys.argv[2]
d = json.load(open(src))

def kind(v):
    if v is None: return "null"
    if isinstance(v, bool): return "bool"
    if isinstance(v, (int, float)): return "number"
    if isinstance(v, str): return "string"
    if isinstance(v, list): return "list"
    if isinstance(v, dict): return "dict"
    return "other"

def bucket(a, b):
    if not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (a, b)):
        return None
    if not (math.isfinite(a) and math.isfinite(b)):
        return "nonfinite"
    if a == b:
        return "identical"
    if a == 0 or b == 0:
        return "one_side_zero"
    rel = abs(a - b) / max(abs(a), abs(b))
    if rel < 1e-6: return "<1e-6"
    if rel < 1e-3: return "<1e-3"
    if rel < 1e-1: return "<1e-1"
    return ">=1e-1"

rows = []
for r in d["comparisons"]:
    l9, rc = r.get("l9"), r.get("recompute")
    e = {"family": r["family"], "key": r["key"], "verdict": r["verdict"], "reason": r.get("reason"),
         "l9_type": kind(l9), "rc_type": kind(rc)}
    b = bucket(l9, rc)
    if b is not None:
        e["bucket"] = b
    elif isinstance(l9, str) and isinstance(rc, str):
        e["match"] = (l9 == rc)
    elif kind(l9) == kind(rc) and kind(l9) in ("list", "dict", "bool"):
        e["match"] = (l9 == rc)
    if "within_bar" in r: e["within_bar"] = r["within_bar"]
    if "items" in r: e["items"] = r["items"]
    rows.append(e)
cov = d["coverage"]
meta = {"unmapped": cov["unmapped"], "uncompared": cov["uncompared"],
        "unbound": [{k: u[k] for k in ("family", "key", "path", "reason")} for u in cov["unbound"]],
        "excluded_members": [{k: m[k] for k in ("family", "pack", "reason", "role", "run_id", "selected")} for m in d["excluded_members"]],
        "counts": d["counts"]}
with open(out, "w") as f:
    for e in rows: f.write(json.dumps(e) + "\n")
    f.write(json.dumps({"meta": meta}) + "\n")
