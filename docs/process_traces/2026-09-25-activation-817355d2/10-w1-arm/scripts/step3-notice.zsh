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
import hashlib,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
from joulewise.night_gate import NightPlan, D166_REGISTRATION_PATH, D166_REGISTRATION_SHA256
from scripts.run_night import schedule
e=os.environ
raw=Path(e["STAGED_PLAN"]).read_bytes(); p=json.loads(raw)
s=schedule(NightPlan.from_mapping(p)); t=p["t0_epoch_s"]
def digest(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()
registration=Path(e["MEASUREMENT_ROOT"])/D166_REGISTRATION_PATH
print("CHECK: D-166 registration digest equals the gate pin", file=sys.stderr, flush=True)
assert digest(registration)==D166_REGISTRATION_SHA256
print("CHECK: sealed Revision 5 digest equals the arm pin", file=sys.stderr, flush=True)
assert digest(Path(e["MEASUREMENT_ROOT"])/"configs/calibration/preregistration_d079_epoch_25g83_rev1.md")==e["SEALED_REGISTRATION_SHA256"]
render=json.loads((Path(e["STAGE"])/"render-context.json").read_text())
print("CHECK: render evidence contains night and dead-man", file=sys.stderr, flush=True)
assert set(render)=={"com.joulewise.night","com.joulewise.night.deadman"}
for label, item in render.items():
 print(f"CHECK: {label} has Interactive and unchanged rendered digest", file=sys.stderr, flush=True)
 assert item["ProcessType"]=="Interactive" and digest(item["path"])==item["rendered_plist_sha256"]
print("To: claude.ai.copper531@passmail.net")
print(f'Subject: NIGHT NOTICE — {p["plan_id"]} (DIAGNOSTIC_NO_PACK) — attempt 1')
print("\nEd,\n")
print("Launch needs no action from you unless you reply NO. Your NO overrides.")
print("Arm attempt 1; earlier abort for this new candidate: none.")
print("The calibration campaign for macOS 25G83 is now two 12-slot windows at least 6 hours apart, at least 12 retained captures, a third window only on count. July's calibration is not continued: its ceiling was set with shorter sampling frames than the machine now delivers, so the equivalence check you proposed in issue 316 would not be able to tell the two apart. Reply NO to the arm notice to stop.")
print("W1 derivation window one: 600 s settle, 12 slots at 600 s cadence, 480 s capture budgets; window 9000 s.")
print("The arm required the battery to be connected, not charging and within 200 mA of zero current; a window in which any slot records charging is not used for derivation.")
print("No model runs or measurement pack. No member values read before the session is terminal.")
print("receipt_class:",p["receipt_class"],"attempt:",1)
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
print("sealed Revision 5 preregistration sha256:",e["SEALED_REGISTRATION_SHA256"])
print("D-166 registration:",registration,"sha256",D166_REGISTRATION_SHA256)
protocol=Path(e["MEASUREMENT_ROOT"])/"configs/calibration/powermetrics_fiducial/protocol_v3.json"
print("protocol_v3:",protocol,"sha256",digest(protocol))
print("PR-L merge commit:",e["PR_L_COMMIT"])
print("PR-L night/dead-man template sha256:",e["NIGHT_TEMPLATE_SHA256"])
print("PR-L probe template sha256:",e["PROBE_TEMPLATE_SHA256"])
print("evidence_root_id:",e["EVIDENCE_ROOT_ID"])
for f in [e["STAGED_PLAN"],e["CALIBRATION_PLAN"],
 e["NIGHT_ROOT"]+"/chain.zsh",e["NIGHT_ROOT"]+"/identity-epoch.json",
 e["NIGHT_ROOT"]+"/t1-bindings.json",
 e["MEASUREMENT_ROOT"]+"/scripts/night_chains/calibration_derivation_only.zsh",
 e["MEASUREMENT_ROOT"]+"/configs/calibration/preregistration_d079_epoch_25g83_rev1.md"]:
 print(f,"sha256",digest(f))
print("Wrapper sidecar:",e["NIGHT_ROOT"]+"/chain.zsh.sha256")
print("Interactive render-only evidence:")
for label, item in sorted(render.items()):
 print(label,"ProcessType=Interactive",item["path"],"sha256",item["rendered_plist_sha256"])
print("Probe template is Interactive and installer render-only validates all three launch contexts; the probe receipt records all three rendered digests at install.")
print("Close the interactive Claude session joulewise-4b before t0.")
print("Keep agent applications closed and the machine untouched from REQUEST through completion; longer if the night remains active.")
print("Reply NO to stop.")
print("NO may be on this thread or relayed through an owner-authored directive. No reply is required.")
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
print -- "STEP3 prepared only: magistrate sends notice and fills notice.json + notice-evidence.txt"
echo "STEP3 OK"
