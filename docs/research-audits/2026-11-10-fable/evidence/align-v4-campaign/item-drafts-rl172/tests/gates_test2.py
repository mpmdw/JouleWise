"""Synthetic gate tests on the BUILT items (Sol confirm P1 included), in bash and zsh. Paths remapped into fresh case dirs;
`date +%s` is a shell function returning a fixed FAKE_NOW, so the 299/300 and 1,199/1,200 s boundaries are exact.
Part A: copy_gate + effective_close (Sol's four states and more). Part B: the Run host-gate excerpt of hp01-s01 and dev02-s02
(effective_close -> HOST_LAST_CLOSE -> copy_gate [-> day_gate] -> the GAP check). Part C: day_gate validation."""
import json, os, re, subprocess, time
D = "/Volumes/JW-EXT/scratch/items-rl171"; PY = "/opt/homebrew/opt/python@3.13/bin/python3.13"
RUN = time.strftime("%H%M%S"); NOW = int(time.time()) - 60
results = []
def blocks(item): return "\n".join(re.findall(r"```sh\n(.*?)```", open(f"{D}/{item}").read(), re.S))
def defs(item):
    s = blocks(item); a = s.index("close_census() {"); b = s.index("\n)\n", s.index("copy_gate() (")) + 3
    out = s[a:b]
    if "day_gate() {" in s:
        c = s.index("DAY_MIXED="); e = s.index("\n}\n", s.index("day_gate() {")) + 3; out += "\n" + s[c:e]
    return out
def run_excerpt(item):
    s = blocks(item); a = s.index('effective_close || { echo "STOP: the receipt census failed; missing evidence stops the launch; mail the lead"; exit 1; }')
    b = s.index("\n", s.index('test "$(date +%s)" -ge $((HOST_LAST_CLOSE + GAP))', a)); return s[a:b]
def case(name, receipts, markers, kind, other="0", expect=None, item="ITEM-hp01-s01.md", body="effective_close && copy_gate", legs="L001,L002,L003,L004,L005,L006"):
    root = f"{D}/tests/cases2-{RUN}/{item[5:-3]}-{name}"
    co, jw, mk = f"{root}/campaign-out", f"{root}/jw-wt", f"{root}/desk-copy"
    for d in (co, jw, mk): os.makedirs(d)
    for rel, age, js in receipts:
        p = f"{root}/{rel}"; os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(js if isinstance(js, str) else json.dumps(js)); os.utime(p, (NOW - age, NOW - age))
    for m in markers: open(f"{mk}/{m}", "w").write("manifest-sha256 deadbeef  Sun Nov 15 01:00:00 PST 2026\n")
    remap = lambda t: t.replace("/Users/edr/campaign-out", co).replace("/Users/edr/code/jw-wt", jw).replace("/Users/Shared/JouleWise/desk-copy", mk)
    if body == "RUN":
        body = remap(run_excerpt(item)) + '\necho "REACHED-LAUNCH"'
    open(f"{root}/fn.sh", "w").write(remap(defs(item)))
    open(f"{root}/body.sh", "w").write(body)
    pre = (f'date() {{ if [ "$1" = "+%s" ]; then echo {NOW}; else command date "$@"; fi; }}; PY={PY}; LEGS={legs}; '
           f'LAST_CLOSE_KIND={kind}; OTHER_CLOSE_EPOCH={other}; QUIET_CAMPAIGN_S=300; '
           'case "$LAST_CLOSE_KIND" in campaign) GAP=$QUIET_CAMPAIGN_S;; other) GAP=1200;; esac; HOST_LAST_CLOSE=SENTINEL; ')
    out = {}
    for sh in ("bash", "zsh"):
        r = subprocess.run([sh, "-c", pre + f". {root}/fn.sh; ( . {root}/body.sh ); echo \"rc=$?\""], capture_output=True, text=True)
        o = r.stdout + r.stderr; rc = int(re.findall(r"rc=(\d+)", o)[-1])
        tag = [l for l in o.splitlines() if l.startswith(("STOP", "WAIT", "copy gate", "journal copy", "REACHED"))]
        v = "PASS" if rc == 0 else ("WAIT" if any(t.startswith("WAIT") for t in tag) else "STOP")
        out[sh] = (v, tag[-1][:140] if tag else o.strip()[-140:])
    ok = out["bash"][0] == out["zsh"][0] == expect
    results.append(dict(item=item, case=name, expect=expect, bash=out["bash"], zsh=out["zsh"], ok=ok))
    print(f"{'OK ' if ok else 'BAD'} {item[5:-3]:<9} {name:<46} expect {expect:<4} bash {out['bash'][0]:<4} zsh {out['zsh'][0]:<4} | {out['bash'][1][:95]}")
def R(roster=("L008", "L009", "L010", "L011", "L012"), age=0): return {"started": {"epoch_s": NOW - 10000}, "roster": list(roster)}
CAMP = "campaign-out/cl-dev-01/cq-dev-01-s04-a1-20261115T082000Z/runner_receipt.json"
F0_CO = "campaign-out/partc/r1-partc-f0-20261115T090000Z/runner_receipt.json"
F0_JW = "jw-wt/partc/notes/r1-partc-f0/runner_receipt.json"
MK = ["cq-dev-01-s04-a1.ok"]
for item in ("ITEM-hp01-s01.md", "ITEM-dev02-s02.md"):
    # A: Sol's four states and more (copy_gate alone)
    case("sol1-newest-f0-wrong-kind-old-marker", [(CAMP, 4000, R()), (F0_CO, 400, {})], MK, "campaign", expect="STOP", item=item)
    case("sol2-newest-f0-wrong-kind-wrong-marker", [(CAMP, 4000, R()), (F0_CO, 400, {})], ["r1-partc-f0-20261115T090000Z.ok", "r1-partc-f0.ok"], "campaign", expect="STOP", item=item)
    case("sol3-newest-jwwt-f0-stale-kind", [(CAMP, 4000, R()), (F0_JW, 400, {})], MK, "campaign", expect="STOP", item=item)
    case("sol4-newest-f0-correct-other", [(CAMP, 4000, R()), (F0_JW, 1300, {})], [], "other", expect="PASS", item=item)
    case("campaign-marker", [(CAMP, 400, R())], MK, "campaign", expect="PASS", item=item)
    case("campaign-no-marker", [(CAMP, 400, R())], [], "campaign", expect="WAIT", item=item)
    case("session-newer-kind-campaign", [(CAMP, 4000, R())], MK, "campaign", other=str(NOW - 100), expect="STOP", item=item)
    # B: the Run host gate excerpt: boundaries
    case("run-campaign-299s", [(CAMP, 299, R())], MK, "campaign", expect="WAIT", item=item, body="RUN")
    case("run-campaign-300s", [(CAMP, 300, R())], MK, "campaign", expect="PASS", item=item, body="RUN")
    case("run-other-close-1s", [(CAMP, 5000, R())], MK, "other", other=str(NOW - 1), expect="WAIT", item=item, body="RUN")
    case("run-other-close-1199s", [(CAMP, 5000, R())], MK, "other", other=str(NOW - 1199), expect="WAIT", item=item, body="RUN")
    case("run-other-close-1200s", [(CAMP, 5000, R())], MK, "other", other=str(NOW - 1200), expect="PASS", item=item, body="RUN")
    case("run-f0-receipt-1199s", [(CAMP, 5000, R()), (F0_JW, 1199, {})], MK, "other", expect="WAIT", item=item, body="RUN")
    case("run-f0-receipt-1200s", [(CAMP, 5000, R()), (F0_JW, 1200, {})], MK, "other", expect="PASS", item=item, body="RUN")
    case("run-other-close-kind-campaign", [(CAMP, 5000, R())], MK, "campaign", other=str(NOW - 1300), expect="STOP", item=item, body="RUN")
# C: day_gate (dev items)
RQ = "campaign-out/cl-qual-01/cq-qual-01-s01-a1-20261119T110000Z/runner_receipt.json"
R1 = "campaign-out/cl-dev-03/cq-dev-03-s01-a1-20261116T110000Z/runner_receipt.json"
def T(roster=..., started=...):
    d = {"started": {"epoch_s": NOW - 600} if started is ... else started}
    if started is None: d.pop("started")
    if roster is not ...: d["roster"] = roster
    return d
for nm, rr, exp in (("valid", ["L001", "L002", "L003"], "PASS"), ("missing", ..., "STOP"), ("null", None, "STOP"), ("dict", {}, "STOP"),
                    ("string", "L001", "STOP"), ("empty", [], "STOP"), ("dup", ["L001", "L001"], "STOP"), ("bad-id", ["X01"], "STOP")):
    case(f"day-roster-{nm}", [(R1, 300, T(rr))], [], "x", item="ITEM-dev03-pilot.md", body="day_gate", legs="L004", expect=exp)
for nm, st in (("missing", None), ("string", {"epoch_s": "1794"}), ("bool", {"epoch_s": True})):
    case(f"day-started-{nm}", [(R1, 300, T(["L001"], st))], [], "x", item="ITEM-dev03-pilot.md", body="day_gate", legs="L004", expect="STOP")
case("day-mixed-cap", [(R1, 300, T([f"L{i:03d}" for i in range(1, 10)]))], [], "x", item="ITEM-dev03-pilot.md", body="day_gate", legs="L010,L011,L012,L013", expect="STOP")
case("day-qualification-same-date", [(RQ, 300, T(["L001"]))], [], "x", item="ITEM-dev03-pilot.md", body="day_gate", legs="L004", expect="STOP")
json.dump(results, open(f"{D}/tests/gates2-results-{RUN}.json", "w"), indent=1)
print("ALL OK" if all(r["ok"] for r in results) else "SOME BAD", len(results), "cases")
