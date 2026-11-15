"""Synthetic test of the RL-173 gates (pred_gate, expiry_gate, watch_gate) as written in a finalized item.
Builds fake campaign-out roots from the items-rl171 MOCK spans (synthetic; mock flag cleared), never a real receipt."""
import json, os, re, shutil, subprocess, sys, tempfile, time
ITEM = sys.argv[1]; MOCK = sys.argv[2]; CAMP, PRED, ROSTER = sys.argv[3], sys.argv[4], sys.argv[5].split(",")
PY = "/opt/homebrew/opt/python@3.13/bin/python3.13"
t = open(ITEM).read()
sh = "\n".join(re.findall(r"```sh\n(.*?)```", t, re.S))
a = sh.index("# RL-173 D.5: this item EXPIRES"); b = sh.index("# RL-172 (a): t0-date caps")
funcs = sh[a:b]
base = tempfile.mkdtemp(dir=os.environ["TMPDIR"])
root = os.path.join(base, "campaign-out")
funcs = funcs.replace("/Users/edr/campaign-out", root)
now = int(time.time())
def run(setup, env_extra, shell="bash", issued=None, watch=None):
    shutil.rmtree(root, ignore_errors=True); os.makedirs(root)
    setup()
    f = funcs.replace("ISSUED_EPOCH=<LEAD FILLS: the issue time as an epoch, from `date +%s` at issue>", f"ISSUED_EPOCH={issued if issued is not None else now - 100}")
    f = f.replace("WATCH_UNTIL_EPOCH=<LEAD FILLS: line 7's watcher observation stamp + 86,400 s, as an epoch>", f"WATCH_UNTIL_EPOCH={watch if watch is not None else now + 3600}")
    assert "<LEAD FILLS" not in f
    script = f"PY={PY}\n{env_extra}\n{f}\npred_gate; echo \"pred rc $? close=${{PRED_CLOSE_EPOCH:-}}\"\nexpiry_gate; echo \"expiry rc $?\"\nwatch_gate; echo \"watch rc $?\"\n"
    r = subprocess.run([shell], input=script, text=True, capture_output=True)
    return r.stdout + r.stderr
def span_dir(name="cq-%s-a1-20261116T080000Z" % PRED, mutate=None, receipt=True):
    d = os.path.join(root, CAMP, name); shutil.copytree(MOCK, d)
    p = os.path.join(d, "runner_receipt.json"); r = json.load(open(p)); r["mock"] = False
    if mutate: mutate(r, d)
    json.dump(r, open(p, "w"))
    if not receipt: os.remove(p)
def summ(d, leg, **kw):
    p = os.path.join(d, "desk-bundle", "legs", leg, "leg_summary.json"); s = json.load(open(p)); s.update(kw); json.dump(s, open(p, "w"))
cases = [
 ("no campaign dir -> WAIT", lambda: None, "", {}, "WAIT", 1),
 ("clean -> PRED CLEAN", lambda: span_dir(), "", {}, "PRED CLEAN", 0),
 ("rc 1 -> VOID", lambda: span_dir(mutate=lambda r, d: r.update(rc=1)), "", {}, "VOID", 1),
 ("legs 5 of 6 -> VOID", lambda: span_dir(mutate=lambda r, d: r.update(legs_finished=len(ROSTER) - 1)), "", {}, "VOID", 1),
 ("restore rc 1 -> VOID", lambda: span_dir(mutate=lambda r, d: [s.update(rc=1) for s in r["steps"] if s["name"] == "restore"]), "", {}, "VOID", 1),
 ("fault -> VOID", lambda: span_dir(mutate=lambda r, d: r["span_result"].update(fault=True)), "", {}, "VOID", 1),
 ("mock receipt -> VOID", lambda: span_dir(mutate=lambda r, d: r.update(mock=True)), "", {}, "VOID", 1),
 ("two legs overtime -> VOID", lambda: span_dir(mutate=lambda r, d: [summ(d, l, wall_s=99999.0) for l in ROSTER[:2]]), "", {}, "LEG_OVERTIME", 1),
 ("one leg overtime -> clean", lambda: span_dir(mutate=lambda r, d: summ(d, ROSTER[0], wall_s=99999.0)), "", {}, "PRED CLEAN", 0),
 ("3 contaminated redos -> VOID", lambda: span_dir(mutate=lambda r, d: summ(d, ROSTER[0], contaminated_redos=3)), "", {}, "CONTAMINATED_REDOS", 1),
 ("two output dirs -> STOP", lambda: (span_dir(), span_dir(name="cq-%s-a2-20261116T090000Z" % PRED)), "", {}, "STOP", 1),
 ("dir without receipt -> WAIT", lambda: span_dir(receipt=False), "", {}, "WAIT", 1),
 ("look-alike name ignored -> WAIT", lambda: span_dir(name="cq-%sb-a1-20261116T080000Z" % PRED), "", {}, "WAIT", 1),
 ("PRIOR before pred close -> STOP", lambda: span_dir(), "PRIOR_CLOSE_EPOCH=1", {}, "STOP: PRIOR_CLOSE_EPOCH", 1),
 ("PRIOR after pred close -> clean", lambda: span_dir(), "PRIOR_CLOSE_EPOCH=9999999999", {}, "PRED CLEAN", 0),
 ("expired -> VOID", lambda: span_dir(), "", {"issued": now - 86401}, "expiry rc 1", None),
 ("watch stale -> STOP", lambda: span_dir(), "", {"watch": now - 1}, "watch rc 1", None),
]
fails = 0
for shell in ("bash", "zsh"):
    for name, setup, extra, kw, want, rc in cases:
        out = run(setup, extra, shell, **kw)
        ok = want in out and (rc is None or f"pred rc {rc} " in out)
        if name.startswith(("clean", "one leg", "PRIOR after")):
            ok = ok and "expiry rc 0" in out and "watch rc 0" in out and re.search(r"close=\d+", out) is not None
        fails += not ok
        print(("PASS" if ok else "FAIL"), shell, name, "|", out.strip().replace("\n", " / ")[:230])
shutil.rmtree(base)
print("FAILS", fails); sys.exit(1 if fails else 0)
