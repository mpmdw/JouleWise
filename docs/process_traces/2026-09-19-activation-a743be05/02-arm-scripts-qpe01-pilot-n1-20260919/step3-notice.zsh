#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
export ARM_SCRIPT_DIR="${0:A:h}"
cd "$MEASUREMENT_ROOT" || exit 3
"$PY" -B "$ARM_SCRIPT_DIR/evidence-checks.py" candidate --plan "$STAGED_PLAN" --publication-safe
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
from joulewise.quiet_predicate_campaign import PROTOCOL_PATH, CHAIN_PATH
from scripts.run_night import schedule
e=os.environ
raw=Path(e["STAGED_PLAN"]).read_bytes(); p=json.loads(raw)
assert raw==(Path(e["ATTEMPT_DIR"])/"plan.json").read_bytes()
s=schedule(NightPlan.from_mapping(p)); t=p["t0_epoch_s"]
print("To: claude2.glaring610@passmail.net")
print(f'Subject: NIGHT NOTICE — {p["plan_id"]} (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 1')
print("\nEd,\n")
print("Launch needs no action from you unless you reply NO. Your NO overrides.")
print("Arm attempt 1; earlier abort for this new candidate: none.")
print("This is the first idle-variance evidence night: it measures how much the Mac's idle energy varies, to size a later experiment. It does not set or activate a new quietness cutoff.")
print("After 600 seconds to settle, the fixed program records twelve 600-second idle envelopes. Each uses a 480-second interior measured from its scheduled start, after a 60-second offset.")
print("Apple's powermetrics sampler records power every 100 ms. The program also records process-census, AC-power and thermal observations, timing and cleanup evidence, and a busy-cores journal (busy processor seconds per elapsed second). Busy cores are a descriptive covariate only.")
print("The programmed span is 7,800 seconds inside a 9,000-second acquisition window. There is no top-up or automatic repeat. Partial observations and refusals are kept.")
print("No model, load generator, calibration-ledger session or measurement pack runs. The existing scheduler supervises the program and the courier emails the result after it ends.")
print("Git during the night: the program runs exactly one read-only git show in the measurement clone to verify that its chain bytes match the pinned commit before capture; it makes no commit, push, checkout or fetch (ruling 87a F2).")
print("After completed delivery, the next lead reads the envelopes and sizes block two, or records 'no cutoff qualifies'. The evidence remains PROVISIONAL.")
print("plan_id:",p["plan_id"])
print("repo_head = measurement_head = reviewed executor commit:",e["H"])
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
print("No-objection window opens when the mail service accepts this exact notice, recorded in the arm record. Publication follows acceptance with no additional minimum waiting interval. The exclusive install close is printed above; every observed NO stops publication, including a NO on an older thread.")
for f in [e["STAGED_PLAN"],e["NIGHT_ROOT"]+"/chain.zsh",
 e["NIGHT_ROOT"]+"/evidence_manifest.json",
 e["MEASUREMENT_ROOT"]+"/"+CHAIN_PATH,e["MEASUREMENT_ROOT"]+"/"+PROTOCOL_PATH]:
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
print -- "NOTICE BODY: $ATTEMPT_DIR/notice-body.txt"
print -- "SUBJECT: NIGHT NOTICE — $PLAN_ID (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 1"
cat "$ATTEMPT_DIR/notice-body.txt"
print -- "STEP3 PREPARED ONLY: magistrate sends notice and fills notice.json + notice-evidence.txt"
