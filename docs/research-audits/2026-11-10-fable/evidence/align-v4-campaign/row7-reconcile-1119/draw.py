"""Row-7 sampled hand-table draw (sha256-hand-sample-v3, seed 2026111501, rate 4; desk_final.hand_sample at
origin/align/2026-11-15-desk-final 3747167f4) for the 11 roster spans + hp-01. Reads only queue JSON and kit JSON
(leg ids and g0_shape) from git objects. Usage: python3 -I -B draw.py REPO"""
import hashlib, json, subprocess, sys
repo = sys.argv[1]
AUD = "origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/"
def show(spec):
    return subprocess.run(["git", "-C", repo, "show", spec], check=True, capture_output=True).stdout
QUEUES = {"dev-01": "QUEUE-cl-dev-01-b4b6aeb19-s03s04-both.json", "dev-02": "QUEUE-cl-dev-02-b4b6aeb19-6plus6-append.json",
          "dev-03": "QUEUE-cl-dev-03-2d347f721-append-both.json", "dev-04": "QUEUE-cl-dev-04-2d347f721.json",
          "dev-05": "QUEUE-cl-dev-05-2d347f721.json", "hp-01": "QUEUE-cl-hp-01-dd206025a-append-mirror-4plus5.json"}
KITC = {"dev-01": "589748f15", "dev-02": "589748f15", "dev-03": "9cbb365a6", "dev-04": "fecaf73f3", "dev-05": "fecaf73f3", "hp-01": "bbd34dc87"}
ROSTER = ["dev-01-s01", "dev-01-s03", "dev-01-s04", "dev-02-s02", "dev-02-s03", "dev-03-s01", "dev-03-s02",
          "dev-04-s01", "dev-04-s02", "dev-05-s01", "dev-05-s02", "hp-01-s01", "hp-01-s02", "hp-01-s03"]
out = []
for sid in ROSTER:
    camp = sid.rsplit("-", 1)[0]
    q = json.loads(show(AUD + QUEUES[camp]))
    s = next(x for x in q["spans"] if x["span_id"] == sid)
    kb = show(f"{KITC[camp]}:{s['kit']['path']}")
    ksha = hashlib.sha256(kb).hexdigest()
    kit = json.loads(kb)
    shapes = {l["leg_id"]: l.get("g0_shape", "own") for l in kit["legs"]}
    shape = "span" if any(shapes.get(x) == "span" for x in s["legs"][1:]) else "own"
    v = int(hashlib.sha256(f"2026111501|{s['kit']['sha256']}|{shape}|{sid}".encode()).hexdigest(), 16) % 4
    out.append({"span_id": sid, "queue": q["queue_id"], "seq": s["seq"], "kit_path": s["kit"]["path"], "kit_commit": KITC[camp],
                "kit_sha256": s["kit"]["sha256"], "kit_bytes_match": ksha == s["kit"]["sha256"], "kit_schema": kit.get("schema"),
                "legs": s["legs"], "shape": shape, "value": v, "hash_selected": v == 0})
print(json.dumps(out, indent=1))
