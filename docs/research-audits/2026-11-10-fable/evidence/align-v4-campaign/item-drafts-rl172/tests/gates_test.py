"""Synthetic tests of close_census + copy_gate (from ITEM-hp01-s01.md) and day_gate (from ITEM-dev02-s02.md / dev03-pilot),
including Sol's four RL-172 re-check replay states. Paths are remapped into a fresh case dir; nothing on the host is read."""
import json, os, re, subprocess, sys, time, datetime as dt, zoneinfo
D = "/Volumes/JW-EXT/scratch/items-rl171"; PY = "/opt/homebrew/opt/python@3.13/bin/python3.13"
TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
RUN = time.strftime("%H%M%S")
def fn(item, start, end_marker):
    s = "\n".join(re.findall(r"```sh\n(.*?)```", open(f"{D}/{item}").read(), re.S))
    a = s.index(start); b = s.index("\n}\n", s.index(end_marker)) + 3
    return s[a:b]
GATES = fn("ITEM-hp01-s01.md", "close_census() {", "copy_gate() {")
DAYG = fn("ITEM-dev03-pilot.md", "DAY_MIXED=", "day_gate() {")
results = []
def case(name, receipts, markers, kind, other="0", expect=None, gate="copy", legs="L001,L002,L003", mixed=None):
    root = f"{D}/tests/cases-{RUN}/{name}"
    co, jw, mk = f"{root}/campaign-out", f"{root}/jw-wt", f"{root}/desk-copy"
    for d in (co, jw, mk): os.makedirs(d)
    now = time.time()
    for rel, age, body in receipts:
        p = f"{root}/{rel}"; os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(body if isinstance(body, str) else json.dumps(body)); os.utime(p, (now - age, now - age))
    for m in markers: open(f"{mk}/{m}", "w").write("manifest-sha256 deadbeef  Sun Nov 15 01:00:00 PST 2026\n")
    text = (GATES if gate == "copy" else DAYG).replace("/Users/edr/campaign-out", co).replace("/Users/edr/code/jw-wt", jw).replace("/Users/Shared/JouleWise/desk-copy", mk)
    if mixed is not None: text = text.replace("DAY_MIXED=yes", f"DAY_MIXED={mixed}")
    open(f"{root}/fn.sh", "w").write(text)
    call = "copy_gate" if gate == "copy" else "day_gate"
    out = {}
    for sh in ("bash", "zsh"):
        r = subprocess.run([sh, "-c", f'PY={PY}; LEGS={legs}; LAST_CLOSE_KIND={kind}; OTHER_CLOSE_EPOCH={other}; . {root}/fn.sh; {call}; echo "rc=$?"'],
                           capture_output=True, text=True)
        o = (r.stdout + r.stderr).strip()
        rc = int(re.findall(r"rc=(\d+)", o)[-1]); first = [l for l in o.splitlines() if l.startswith(("STOP", "WAIT", "copy gate", "journal copy", "t0-date"))]
        out[sh] = (rc, first[-1] if first else o[-160:])
    verdict = "PASS" if out["bash"][0] == 0 else ("WAIT" if out["bash"][1].startswith("WAIT") else "STOP")
    ok = verdict == expect and out["bash"][0] == out["zsh"][0]
    results.append(dict(case=name, expect=expect, got=verdict, ok=ok, bash=out["bash"], zsh=out["zsh"]))
    print(f"{'OK ' if ok else 'BAD'} {name}: expect {expect}, got {verdict} | {out['bash'][1][:150]}")
CAMP = "campaign-out/cl-dev-01/cq-dev-01-s04-a1-20261115T082000Z/runner_receipt.json"
F0_CO = "campaign-out/r1-partc-f0/runner_receipt.json"
F0_JW = "jw-wt/partc/notes/r1-partc-f0/runner_receipt.json"
# Sol's four replay states
case("sol1-newest-f0-wrong-kind-old-marker", [(CAMP, 4000, {}), (F0_CO, 400, {})], ["cq-dev-01-s04-a1.ok"], "campaign", expect="STOP")
case("sol2-newest-f0-wrong-kind-wrong-marker", [(CAMP, 4000, {}), (F0_CO, 400, {})], ["r1-partc-f0.ok"], "campaign", expect="STOP")
case("sol3-newest-jwwt-f0-stale-kind", [(CAMP, 4000, {}), (F0_JW, 400, {})], ["cq-dev-01-s04-a1.ok"], "campaign", expect="STOP")
case("sol4-newest-f0-correct-other", [(CAMP, 4000, {}), (F0_JW, 1300, {})], [], "other", expect="PASS")
# more
case("campaign-with-marker", [(CAMP, 400, {}), (F0_JW, 9000, {})], ["cq-dev-01-s04-a1.ok"], "campaign", expect="PASS")
case("campaign-no-marker", [(CAMP, 400, {})], ["r1-partc-f0.ok"], "campaign", expect="WAIT")
case("other-kind-but-newest-campaign", [(CAMP, 400, {}), (F0_JW, 9000, {})], ["cq-dev-01-s04-a1.ok"], "other", expect="STOP")
case("noncampaign-dir-under-campaign-out-kind-campaign", [("campaign-out/kits/runner_receipt.json", 300, {}), (CAMP, 4000, {})], ["runner_receipt.ok", "kits.ok", "cq-dev-01-s04-a1.ok"], "campaign", expect="STOP")
case("session-newer-kind-other", [(CAMP, 4000, {})], ["cq-dev-01-s04-a1.ok"], "other", other=str(int(time.time()) - 100), expect="PASS")
case("session-newer-kind-campaign", [(CAMP, 4000, {})], ["cq-dev-01-s04-a1.ok"], "campaign", other=str(int(time.time()) - 100), expect="STOP")
case("other-close-epoch-unset", [(CAMP, 400, {})], ["cq-dev-01-s04-a1.ok"], "campaign", other="''", expect="STOP")
case("empty-census", [], [], "campaign", expect="STOP")
# day_gate roster and started validation (a same-date dev receipt; now = today local)
today = time.time() - 600
def rec(roster=..., started=...):
    d = {}
    if started is not ...: d["started"] = started
    else: d["started"] = {"epoch_s": today}
    if roster is not ...: d["roster"] = roster
    return d
R1 = "campaign-out/cl-dev-03/cq-dev-03-s01-a1-20261116T110000Z/runner_receipt.json"
case("day-valid", [(R1, 300, rec(["L001", "L002", "L003"]))], [], "x", gate="day", legs="L004,L005,L006,L007,L008,L009", expect="PASS")
case("day-valid-cap-exceeded", [(R1, 300, rec([f"L{i:03d}" for i in range(1, 10)]))], [], "x", gate="day", legs="L010,L011,L012,L013", expect="STOP")
for nm, rr in (("missing", ...), ("null", None), ("dict", {}), ("string", "L001"), ("empty", []), ("dup", ["L001", "L001"]), ("bad-id", ["X01"]), ("int", [1])):
    case(f"day-roster-{nm}", [(R1, 300, rec(rr))], [], "x", gate="day", legs="L004", expect="STOP")
for nm, st in (("missing", None), ("no-epoch", {}), ("string", {"epoch_s": "1794"}), ("bool", {"epoch_s": True})):
    body = rec(["L001"]); body.pop("started") if nm == "missing" else body.__setitem__("started", st)
    case(f"day-started-{nm}", [(R1, 300, body)], [], "x", gate="day", legs="L004", expect="STOP")
case("day-other-date-ignored", [(R1, 300, rec(["L001"] * 1, {"epoch_s": today - 3 * 86400}))], [], "x", gate="day", legs="L004", expect="PASS")
case("day-notjson", [(R1, 300, "not json")], [], "x", gate="day", legs="L004", expect="STOP")
json.dump(results, open(f"{D}/tests/gates-results-{RUN}.json", "w"), indent=1)
print("ALL OK" if all(r["ok"] for r in results) else "SOME BAD", len(results), "cases")
# RL-172 (a) rule 3 (added after Sol's diagnostic): a same-date qualification receipt refuses a development span
RQ = "campaign-out/cl-qual-01/cq-qual-01-s01-a1-20261119T110000Z/runner_receipt.json"
case("day-qualification-same-date", [(RQ, 300, rec(["L001"]))], [], "x", gate="day", legs="L004", expect="STOP")
case("day-qualification-other-date", [(RQ, 300, rec(["L001"], {"epoch_s": today - 3 * 86400}))], [], "x", gate="day", legs="L004", expect="PASS")
json.dump(results, open(f"{D}/tests/gates-results-{RUN}.json", "w"), indent=1)
print("ALL OK" if all(r["ok"] for r in results) else "SOME BAD", len(results), "cases (with qualification)")
