import os, sys, time
sys.path.insert(0, os.getcwd())
from joulewise.arm_census import classify_arm_census, Observation
from joulewise.quiet_guard_process import KernelProcessRecord as K, KernelProcessTable, DarwinProcessRecord as D
from joulewise.night_gate import NightPlan
head="0"*40; t0=(int(time.time())//60-60*24*10)*60
plan = NightPlan.from_mapping(dict(schema="joulewise.night_plan.v2", schema_version=2, plan_id="p",
    receipt_class="DIAGNOSTIC_NO_PACK", t0_epoch_s=float(t0), window_max_s=9000, authored_epoch_s=float(t0-3600),
    repo_head=head, chain_path="chain.zsh", chain_sha256_path="chain.zsh.sha256", custody_root="/private/tmp/x",
    measurement_head=head, measurement_root="/private/tmp/x", registration_path="docs/registration.md"))
rows = [(1,0),(100,1),(200,100),(300,100),(310,300),(400,100),(500,1),(600,1)]
table = KernelProcessTable(tuple(K(p,pp,"t") for p,pp in rows))
recs = (D(100,1,"t","/usr/local/bin/claude",("claude",)), D(200,100,"t","/usr/bin/python3",("python3","-m","joulewise.evidence_night","check")),
        D(300,100,"t","/usr/local/bin/codex",("codex","mcp-server")), D(310,300,"t","/bin/sleep",("sleep","9")),
        D(400,100,"t","/bin/zsh",("zsh",)), D(500,1,"t","/bin/sleep",("sleep","99")), D(600,1,"t","/usr/local/bin/codex",("codex","exec")))
# hit_pids = what `pgrep -lf '[c]odex|[c]laude|[t]3'` would list: argv matches only
obs = Observation(table, recs, hit_pids=(100,300,600), diagnostics=())
v = classify_arm_census(plan, obs, caller_pid=200)
print("own_pids", v.own_pids, "foreign_pids", v.foreign_pids, "diagnostics", v.diagnostics)
print("outside ancestor chain of 200:", [p for p,_ in rows if p not in (100,200)], "-> foreign:", list(v.foreign_pids))
# a hit with no readable record -> not foreign; census diagnostics carry it instead
obs2 = Observation(table, recs, hit_pids=(100,300,600,700), diagnostics=("pid=700 unknown: no exact record",))
v2 = classify_arm_census(plan, obs2, caller_pid=200)
print("unreadable hit 700: foreign", v2.foreign_pids, "diagnostics", v2.diagnostics)
