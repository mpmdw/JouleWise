import difflib,json,re,subprocess
BASE="2aae25f69a6be0b11465129e353d1a27eb63c4cb"
P="docs/process_traces/2026-09-02-hands-free-week/"
H="docs/process/NIGHT_HANDBACK.md"
K="docs/process/state_kernel.json"
IDS=("NIGHT-REHEARSAL-01","NIGHT-GATE-STUB-CHAIN-01","CLONE-READINESS-01")
def git(*args):
    return subprocess.check_output(["git",*args],text=True)
def read(ref,path):
    return git("show",ref+":"+path)
def scopes(ref):
    out={H:read(ref,H)}
    for name in ("21h-rehearsal-20260909-arm-record.md","21i-rehearsal-20260909-harvest-record.md"):
        out[name]=read(ref,P+name)
    durable=read(ref,P+"00-DURABLE-STATE.md")
    _d=durable[durable.index("## ARMED — rehearsal-20260909"):]
    _cut=_d.find("## 2026-09-09 activation 2145630c")
    out["durable-09-09"]=_d if _cut<0 else _d[:_cut]
    run=read(ref,"RUN_STATE.md")
    out["T38d"]="\n".join(l for l in run.splitlines() if l.startswith(("**Current checkpoint: T38d","**T38d (")))
    assert len(out["T38d"].splitlines())==2
    kernel=json.loads(read(ref,K))
    queue=read(ref,"TASK_QUEUE.md")
    for task in IDS:
        out["kernel:"+task]=json.dumps(kernel["tasks"][task],sort_keys=True)
        rows=[l for l in queue.splitlines() if re.match(r"^\| [AE]\d+ \| "+task+r" \|",l)]
        assert len(rows)==2,(task,len(rows))
        out["queue:"+task]="\n".join(rows)
        assert all(kernel["tasks"][task]["status_note"] in l for l in rows)
    rehearsal=kernel["tasks"][IDS[0]]
    deps={d["target"]:d for d in rehearsal["dependencies"]}
    assert deps["POST-WATCHDOG-REHEARSAL-20260909"]["state"]=="satisfied"
    assert deps["POST-WATCHDOG-REHEARSAL-20260909"]["evidence"]
    assert deps[IDS[1]]["state"]=="pending" and rehearsal["status"]=="blocked"
    assert "needs_ruling" in rehearsal["status_note"]
    return out
def tokens(s):
    return [t for t in re.findall(r"[A-Za-z0-9]+(?:\.[0-9]+)?",s) if any(c.isdigit() for c in t)]
head=git("rev-parse","HEAD").strip()
assert subprocess.run(["git","merge-base","--is-ancestor",BASE,head]).returncode==0
assert git("status","--porcelain")==""
expected=scopes(BASE)
old="at `bb7090e2` under review"
new="at `5db38b58` (PR #309) under review"
assert expected[H].count(old)==1
expected[H]=expected[H].replace(old,new)
kold="NIGHT_HANDBACK.md \u00a7Executed records cure branch fix/2026-09-09-night-gate-stub-chain at bb7090e2 with fix round 1 at 5db38b58 (PR #309), under paired review, not yet merged."
knew="Cure branch fix/2026-09-09-night-gate-stub-chain: initial cure bb7090e2, fix round 1 head 5db38b58 (PR #309), under paired review, not yet merged (NIGHT_HANDBACK.md \u00a7Executed names the branch and the fix head)."
import json as _j
kk="kernel:NIGHT-GATE-STUB-CHAIN-01"
assert expected[kk].count(_j.dumps(kold)[1:-1])==1, "kernel old note not found once"
expected[kk]=expected[kk].replace(_j.dumps(kold)[1:-1],_j.dumps(knew)[1:-1])
for q in ("queue:NIGHT-GATE-STUB-CHAIN-01",):
    assert expected[q].count(kold)==2, ("queue old note count", expected[q].count(kold))
    expected[q]=expected[q].replace(kold,knew)
actual=scopes(head)
bad=[]
for name in expected:
    if tokens(expected[name])!=tokens(actual[name]):
        bad.append(name)
        print("FAIL numeric/identity drift:",name)
        for line in difflib.unified_diff(tokens(expected[name]),tokens(actual[name]),fromfile="reviewed expected",tofile="candidate",n=1,lineterm=""):
            print(line)
print("PR308_FACT_GUARD: "+("FAIL" if bad else "PASS")+"; scopes="+str(len(expected))+"; mismatches="+str(len(bad)))
raise SystemExit(bool(bad))
