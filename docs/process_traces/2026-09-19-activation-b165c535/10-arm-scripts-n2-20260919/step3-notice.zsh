#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
cd "$MEASUREMENT_ROOT" || exit 3
mkdir -p "$STAGE/arm-attempts"
mkdir "$ATTEMPT_DIR"
cp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
print '[]' > "$ATTEMPT_DIR/attempts.json"
print -- "CHECK: attempt 000001 created exclusively; staged bytes copied"
print -- "CHECK: byte equality" "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
cmp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/arm-census-1.json"
sleep 30
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/arm-census-2.json"
# rc 0 is diagnostic for this real class; the magistrate reviews foreign PIDs.
set +e
/usr/bin/pgrep -lf 'codex|claude|t3' > "$ATTEMPT_DIR/raw-pgrep.txt"
pgrep_rc=$?
set -e
cat "$ATTEMPT_DIR/raw-pgrep.txt"
print -- "CHECK: raw pgrep rc=$pgrep_rc (1 means empty; 0 requires ancestry review)"
[[ "$pgrep_rc" -eq 0 || "$pgrep_rc" -eq 1 ]] || exit 3
"$PY" -B - <<'PY' > "$ATTEMPT_DIR/notice-body.txt"
import hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
from joulewise.night_gate import NightPlan
from scripts.run_night import schedule
e=os.environ
raw=Path(e["STAGED_PLAN"]).read_bytes(); p=json.loads(raw)
s=schedule(NightPlan.from_mapping(p)); t=p["t0_epoch_s"]
print("To: claude.ai.copper531@passmail.net")
print(f'Subject: NIGHT NOTICE — {p["plan_id"]} (DIAGNOSTIC_NO_PACK) — attempt 1')
print("\nEd,\n")
print("Launch needs no action from you unless you reply NO. Your NO overrides.")
print("Arm attempt 1; earlier abort for this new candidate: none.")
print("Why this night: night one (d079-epoch-25g83-derivation-n1-20260919, 00:00 PDT today) completed GO with 4 of 12 captures valid; the desk tool returned EPOCH_EQUIVALENCE INCONCLUSIVE (m = 4 < 6). Directive issue 316 and runbook section 2.5 name exactly one next action: one more equivalence night under a fresh plan. This is that night. Ledger head pin 126 / ffd12051 (advanced at the desk after night one).")
print("Diagnostic (no decision taken on it): night one's misses trace to a coarser powermetrics sample cadence on 25G83 (about 0.245 s versus 0.120 s for the r6 corpus); see record 03 on the bookkeeping branch. If you would rather wait until you have read it, reply NO.")
print("One equivalence night: 600 s settle, 12 slots at 600 s cadence, 480 s capture budgets; window 9000 s.")
print("No model runs or measurement pack. No member values read before the session is terminal.")
print("plan_id:",p["plan_id"])
print("repo_head = measurement_head = handback commit:",e["H"])
print("H again:",e["H"])
print("clone:",e["MEASUREMENT_ROOT"])
print("custody:",e["NIGHT_ROOT"],"\nruns:",e["NIGHT_ROOT"]+"/runs")
print("plan sha256:",hashlib.sha256(raw).hexdigest())
print("authored_epoch_s:",p["authored_epoch_s"])
def stamp(k,v):
 print(k,datetime.fromtimestamp(v).astimezone().isoformat(),
       datetime.fromtimestamp(v,timezone.utc).isoformat(),"epoch",v)
for k,v in [("install close EXCLUDED",t-600),("REQUEST / exit BEFORE",t-480),
 ("TERM",t-360),("KILL",t-300),("t0",t),("window end",t+9000),
 ("completion / courier deadline",t+9300),("daily dead-man",s["deadman_epoch_s"])]:
 stamp(k,v)
for i,(a,b) in enumerate(s["install_spans_today"],1):
 stamp(f"install span {i} open",a); stamp(f"install span {i} close EXCLUDED",b)
print("Notice-send open: actual acceptance of this message, retained in the arm record.")
for f in [e["STAGED_PLAN"],e["CALIBRATION_PLAN"],
 e["NIGHT_ROOT"]+"/chain.zsh",e["NIGHT_ROOT"]+"/identity-epoch.json",
 e["NIGHT_ROOT"]+"/t1-bindings.json",
 e["MEASUREMENT_ROOT"]+"/scripts/night_chains/calibration_derivation_only.zsh",
 e["MEASUREMENT_ROOT"]+"/configs/calibration/preregistration_d079_epoch_25g83_rev1.md"]:
 print(f,"sha256",hashlib.sha256(Path(f).read_bytes()).hexdigest())
print("Wrapper sidecar:",e["NIGHT_ROOT"]+"/chain.zsh.sha256")
print("Keep agent applications closed and the machine untouched from REQUEST through completion; longer if the night remains active.")
print("Reply NO on this thread or relay NO through an owner-authored directive. No reply is required.")
print("The magistrate checks readable NO/directive/stop channels before publication and exits before REQUEST.")
PY
# TEMPLATE ONLY: this step neither sends mail nor claims acceptance/clearance.
"$PY" -B - <<'PY'
import hashlib, json, os
from pathlib import Path
d=Path(os.environ["ATTEMPT_DIR"]); raw=(d/"plan.json").read_bytes(); p=json.loads(raw)
n=dict(accepted=False,attempt=1,blocking_causes=[],latest_abort_epoch_s=None,
       latest_no_epoch_s=None,measurement_head=p["measurement_head"],
       message_id="__MESSAGE_ID__",thread_id="__THREAD_ID__",
       plan_id=p["plan_id"],plan_sha256=hashlib.sha256(raw).hexdigest(),
       prerequisites_clear=False,receipt_class=p["receipt_class"],
       sent_epoch_s="__ACCEPTED_EPOCH__",veto_clear=False)
with (d/"notice.json").open("x") as f:
    json.dump(n,f,indent=2); f.write("\n")
print("WROTE notice.json TEMPLATE; record actual Gmail acceptance and fresh checks before step 4")
PY
cat "$ATTEMPT_DIR/notice-body.txt"
print -- "STEP3 PREPARED ONLY: magistrate sends notice and fills notice.json + notice-evidence.txt"
