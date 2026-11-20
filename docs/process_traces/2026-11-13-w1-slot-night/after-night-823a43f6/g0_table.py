import json, sys, glob, os
root = sys.argv[1]
def journal(member_dir):
    fs = glob.glob(os.path.join(member_dir, "runs", "*", "outputs", "align_thermal.jsonl"))
    rows = []
    for f in fs:
        for l in open(f):
            o = json.loads(l)
            if o.get("kind") != "reading": continue
            t = o["finished"]["monotonic_ns"]
            rd = o["values"]["readings"]
            rows.append((t, {k: (v.get("value") if v.get("error") is None else None) for k, v in rd.items()}))
    rows.sort(key=lambda r: r[0]); return rows
def gates(member_dir):
    out = []
    for f in glob.glob(os.path.join(member_dir, "runs", "*", "events.jsonl")):
        for l in open(f):
            o = json.loads(l)
            if o.get("event_type") == "phase_end" and o.get("phase") == "align_thermal_gate":
                out.append(o["metadata"])
    return out
members = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)) and d not in ("harvest",))
J = {m: journal(os.path.join(root, m)) for m in members}
def mean_over(rows, key, a, b):
    v = [r[1].get(key) for r in rows if a <= r[0] <= b and r[1].get(key) is not None]
    return sum(v) / len(v) if v else None
def at(rows, key, t):
    best = None
    for r in rows:
        if r[0] <= t and r[1].get(key) is not None: best = r
    return best[1][key] if best else None
# map source member name -> dir
srcmap = {}
for m in members:
    for f in glob.glob(os.path.join(root, m, "runs", "*")):
        srcmap[os.path.basename(f)] = m
for m in members:
    rows = J[m]
    first_tf08 = rows[0][1].get("Tf08") if rows else None
    for g in gates(os.path.join(root, m)):
        ref = g.get("reference") or {}; rel = g.get("release") or {}
        span = ref.get("span_ns"); src = srcmap.get(ref.get("source_member"), m)
        tf08_ref = mean_over(J.get(src, []), "Tf08", *span) if span else None
        ex = g.get("exit_sample_ns") or g.get("end_ns")
        tf08_rel = at(rows, "Tf08", ex) if g.get("outcome") == "released" else None
        # band-entry: last time either key was outside band before exit
        last_clause = None
        if g.get("outcome") == "released" and ref.get("fast_c") is not None:
            band_out_last = None
            for t, rd in rows:
                if g["start_ns"] <= t <= ex:
                    f_, s_ = rd.get("TV0h"), rd.get("TVh0")
                    if f_ is None or s_ is None or f_ > ref["fast_c"] + 1.0 or s_ > ref["slow_c"] + 1.0:
                        band_out_last = t
            if band_out_last is None: last_clause = "both at entry"
            else:
                gap = (ex - band_out_last) / 1e9
                last_clause = f"band (in-band {gap:.1f}s before release)" if gap <= 1.5 else f"slope (band held {gap:.1f}s before release)"
        d = lambda a, b: None if a is None or b is None else round(a - b, 3)
        print(json.dumps({"member": m, "gate": g.get("kind"), "turn": g.get("turn"), "outcome": g.get("outcome"),
            "dur_s": round(g.get("duration_s", 0), 1), "ref_src": ref.get("source_member"),
            "rel-ref TV0h": d(rel.get("fast_c"), ref.get("fast_c")), "rel-ref TVh0": d(rel.get("slow_c"), ref.get("slow_c")),
            "rel-ref Tf08": d(tf08_rel, tf08_ref), "slope": g.get("slope_c_per_min"), "last_clause": last_clause,
            "Tf08 start-minus-ref": d(first_tf08, tf08_ref) if g.get("kind") == "G0" else None}))
