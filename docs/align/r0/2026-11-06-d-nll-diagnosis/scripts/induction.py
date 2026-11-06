"""Induction / copy check on per-token losses: split targets into 'copyable' (the n-gram of the last
n-1 context tokens + target already occurred earlier in the context) vs 'novel', per variant."""
import json, sys
import numpy as np
ids = json.load(open(sys.argv[1])); res = json.load(open(sys.argv[2])); n = int(sys.argv[3]) if len(sys.argv) > 3 else 4
def classes(seq):
    seen = set(); cls = []
    for t in range(1, len(seq)):
        g = tuple(seq[max(0, t - n + 1):t + 1])
        cls.append(len(g) == n and g in seen)
        if len(g) == n: seen.add(g)
    return np.array(cls)
out = {}
for key, seq in (("start_0", ids), ("start_nothink", ids[:3] + ids[41:])):
    c = classes(seq)
    for v, r in res["variants"].items():
        if key not in r or "per_token" not in r[key]: continue
        l = np.array(r[key]["per_token"])
        o = {}
        for lo, hi in ((0, 900), (900, len(l))):
            cc = c[lo:hi]; ll = l[lo:hi]
            o[f"{lo}-{hi}"] = {"copyable_n": int(cc.sum()), "copyable_mean": round(float(ll[cc].mean()), 3),
                               "novel_n": int((~cc).sum()), "novel_mean": round(float(ll[~cc].mean()), 3),
                               "copyable_frac_gt5nats": round(float((ll[cc] > 5).mean()), 3)}
        out[f"{key}/{v}"] = o
print(json.dumps(out, indent=1))
