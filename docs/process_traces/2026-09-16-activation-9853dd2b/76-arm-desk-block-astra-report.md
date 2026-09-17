```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Read-only bench procedure prepared; current timing, probe admission, labels and documentation discrepancies identified.",
  "workspace": {
    "base_requested": "c613e71e37621ddaabda7550b00ac39e5db2ca8c",
    "base_mode": "exact",
    "head_start": "c613e71e37621ddaabda7550b00ac39e5db2ca8c",
    "head_end": "c613e71e37621ddaabda7550b00ac39e5db2ca8c",
    "upstream_end": "c613e71e37621ddaabda7550b00ac39e5db2ca8c",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "Desk preparation", "action": "wait_for", "wait_for": "Reviewed merged H containing revision 3 and this night's handback/inventory"},
      {"row": "Publication and arm", "action": "wait_for", "wait_for": "All desk gates, census clearance, accepted notice and adequate remaining time"},
      {"row": "Acquisition in this session", "action": "do_not_start", "wait_for": "Agent-free scheduled execution"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["c613e71e37621ddaabda7550b00ac39e5db2ca8c"]},
      "expected": {"exit_code": 0, "tail_regex": "^c613e71e37621ddaabda7550b00ac39e5db2ca8c$"}
    }
  ],
  "flags": [
    {"id": "F1", "kind": "residual_risk", "level": "nonblocking", "text": "Runbook and handback contain stale timing, flag-list and arm-block text; corrections are listed below.", "needs": "Use the corrected sequence and recheck it at H."},
    {"id": "F2", "kind": "verification_gap", "level": "nonblocking", "text": "No live custody, network, launchctl, probe, installation or measurement operation was performed. Future H and T0 remain bench inputs.", "needs": "Lead owns bench verification and arm."}
  ]
}
```

## Scheduling matrix

Row | action | wait_for | collision surface
---|---|---|---
Clone and stage | wait_for | Reviewed H; fresh paths; prior-night disposition complete | Ledger provenance, pre-registration, retained custody
Notice and publish | wait_for | Desk checks; no foreign agents, NO or unresolved directive | Watchdog discovery begins at publication
Probe and install | wait_for | Accepted notice; published plan; owner present for probe | Consent, temporary process group, fixed production labels
Record and exit | start_now | Successful install | Finish strictly before `T0−480`
Harvest | wait_for | Completion, delivery and ended-process evidence | Never reopen or mutate an active night

## Critical path

**Bench-only instructions.** Substitute only `<H>` and `<T0>`. H must contain the reviewed revision-3 addendum, abort implementation, this night's handback and production-inventory entry. Do not substitute `c613e71e`: its pre-registration still carries the old chain digest.

The requested unsuffixed clone and `n1-date` identifiers follow the last real arm. Every path must be unused. A collision stops this block; never overwrite, rename a retained clone, or falsify the date. Register `evidence-$PLAN_ID` in the new arm record.

**1. Fresh clone, locked interpreter and ledger.**

```zsh
set -euo pipefail
export H='<H>' T0_EPOCH_S='<T0>'
export TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
export NIGHT_DATE="$(date -r "$T0_EPOCH_S" +%Y%m%d)"
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export MEASUREMENT_ROOT="/Users/edr/JouleWise-measurement-$NIGHT_DATE-derivation"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export PLAN_ID="d079-epoch-25g83-derivation-n1-$NIGHT_DATE"
export SESSION_ID="$PLAN_ID" EVIDENCE_ROOT_ID="evidence-$PLAN_ID"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export PLAN="$NIGHT_ROOT/night_plan.json"
export CALIBRATION_PLAN="$NIGHT_ROOT/calibration_plan.json"
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json"
export LEDGER_SOURCE=/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl

remote_main="$(git ls-remote --exit-code "$REMOTE_URL" refs/heads/main)"
test "${remote_main%%$'\t'*}" = "$H"
for p in "$MEASUREMENT_ROOT" "$NIGHT_ROOT" "$STAGE"; do
  test ! -e "$p"
  test ! -L "$p"
done
git clone --no-hardlinks "$REMOTE_URL" "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout --detach "$H"
cd "$MEASUREMENT_ROOT"
test "$(git rev-parse HEAD)" = "$H"

python3.13 --version
python3.13 -m venv .venv
"$PY" -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"
"$PY" -m pip install -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) \
  <("$PY" -m pip freeze --exclude-editable | sort)
export PATH="$MEASUREMENT_ROOT/.venv/bin:$PATH"

mkdir -p "$MEASUREMENT_ROOT/runs"
test ! -e "$CALIBRATION_LEDGER"
test ! -L "$CALIBRATION_LEDGER"
rsync -a --checksum "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
cmp "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
shasum -a 256 "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
root=Path(os.environ["MEASUREMENT_ROOT"])
pin=Path(os.environ["LEDGER_HEAD_PIN"])
p=json.loads(pin.read_text())
s=load_calibration_ledger_snapshot(
    Path(os.environ["CALIBRATION_LEDGER"]), pin, repo_root=root,
    require_committed_pin=True, verify_custody=True, mode="read_replay")
assert not s.refusal_reasons, s.refusal_reasons
assert (s.head_sequence,s.head_digest)==(p["sequence"],p["head_digest"])
print("authenticated head-equals-pin",s.head_sequence,s.head_digest)
PY
git status --porcelain=v1 --untracked-files=all
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

The venv recipe comes from §0.2's cited record 12 and the last arm's `20-clone.zsh`; the recorded interpreter was Python 3.13.1. Keep the absolute `$PY` pin. Copy **only the ledger file**; the committed head pin comes from H. Copy no custody directories and rewrite no absolute iCloud locator.

**2. Desk checks, staged plan, wrapper and validation.**

Before creating the root: finish prior harvest/uninstall/discovery retirement as authorized; retained production custody stays retained. No unresolved ownership, STOP, standdown, NO or directive may remain. This discovery command must print nothing:

```zsh
print -rl -- /Users/edr/night-custody/*/night_plan.json(N)
```

Run and retain both epoch-watch outputs; rc 3 is expected **only with the explained OS/sampler mismatch**, matching hardware/MLX, authenticated ledger and matching pre-registration sampler. Any other error stops.

```zsh
set +e
"$PY" scripts/issue_calibration_acceptance_generation.py check
check_rc=$?
"$PY" scripts/issue_calibration_acceptance_generation.py check \
  --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md
prereg_rc=$?
set -e
test "$check_rc" -eq 3
test "$prereg_rc" -eq 3

shasum -a 256 scripts/night_chains/calibration_derivation_only.zsh \
  configs/calibration/preregistration_d079_epoch_25g83_rev1.md
git rev-parse "${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md"

mkdir -p "$NIGHT_ROOT" "$STAGE"
test "$(stat -f %d "$NIGHT_ROOT")" = "$(stat -f %d "$STAGE")"
cp configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json "$CALIBRATION_PLAN"
cmp configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json "$CALIBRATION_PLAN"
"$PY" scripts/write_derivation_night_inputs.py --out-dir "$NIGHT_ROOT"

"$PY" -B - <<'PY'
import hashlib, os, time
from pathlib import Path
from joulewise.night_gate import NightPlan,D166_REGISTRATION_PATH,D166_REGISTRATION_SHA256
from joulewise.night_plan_writer import write_night_plan
e=os.environ
a=int(time.time()); t=int(e["T0_EPOCH_S"])
assert t%60==0 and 0<=t-a<=129600 and a<t-600
assert hashlib.sha256((Path(e["MEASUREMENT_ROOT"])/D166_REGISTRATION_PATH).read_bytes()).hexdigest()==D166_REGISTRATION_SHA256
p=NightPlan.from_mapping({
 "schema":"joulewise.night_plan.v2","schema_version":2,
 "plan_id":e["PLAN_ID"],"receipt_class":"DIAGNOSTIC_NO_PACK",
 "t0_epoch_s":t,"window_max_s":9000,"authored_epoch_s":a,
 "repo_head":e["H"],"measurement_root":e["MEASUREMENT_ROOT"],
 "measurement_head":e["H"],"chain_path":e["NIGHT_ROOT"]+"/chain.zsh",
 "chain_sha256_path":e["NIGHT_ROOT"]+"/chain.zsh.sha256",
 "custody_root":e["NIGHT_ROOT"],"registration_path":D166_REGISTRATION_PATH})
target=Path(e["STAGED_PLAN"])
assert not target.exists() and not target.is_symlink()
print(write_night_plan(target,p))
PY

gen() {
  "$PY" -B scripts/gen_derivation_night.py --plan "$1" \
    --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" \
    --calibration-plan "$CALIBRATION_PLAN" \
    --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" \
    --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" "${@:2}"
}
gen "$STAGED_PLAN"
gen "$STAGED_PLAN" --verify
/bin/zsh -n "$NIGHT_ROOT/chain.zsh"
python3 scripts/run_night.py preflight --plan "$STAGED_PLAN"
scripts/install_night_agent.sh --plan "$STAGED_PLAN" --python "$PY" \
  --render-only "$STAGE/rendered-agents"
"$PY" -B scripts/run_night.py schedule --plan "$STAGED_PLAN" > "$STAGE/schedule.json"
cat "$STAGE/schedule.json"
```

Here `python3` resolves through the explicitly prepended venv PATH. Expect preflight success JSON, `emitted … sha256=…`, `VERIFIED … sha256=…`, and syntax/render exit 0.

This preserves §1.1b's five dependencies: clone/inputs → staged plan → generation → byte verification → syntax check/arm. No `--repo-root`, timing override or pack block. `registration_path` resolves to `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`, **not** the scientific pre-registration.

Night-root files: `calibration_plan.json`, `identity-epoch.json`, `t1-bindings.json`, `chain.zsh`, `chain.zsh.sha256`, advisory `chain.zsh.chain-source.sha256`; publication later adds `night_plan.json`. Captures go in `runs/instrument_validation/$SESSION_ID-dNN/`; chain log in `operator_logs/derivation-chain.log`; driver records in `night/`, driver log in `night.log`. Only the plan is staged.

**Arithmetic:** `600 + 11×600 + 480 = 7680`; generator minimum `7980`; allocation `9000`. Install must **finish before `T0−600`** inside the selected local span, currently `[00:00,24:00)`. REQUEST/exit is **`T0−480`**, TERM `T0−360`, KILL `T0−300`. Acquisition ends `T0+9000`; completion is `T0+9300`; dead-man is `60×ceil((T0+12900)/60)`, hence `T0+12900` for this minute-aligned plan, daily at that local hour/minute. Shutdown grace does not extend acquisition.

Require `0≤now−authored≤129600` and `0≤T0−authored≤129600`. Leave enough time for the 600-second probe, installation and handback; never refresh timestamps on an approved candidate to extend its budget.

**3. Attempt evidence and exact notice template.**

Stop own seats and Codex/MCP children through their real controls. Run:

```zsh
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN"
export ARM_ATTEMPT=1
export ATTEMPT_DIR="$STAGE/arm-attempts/000001"
mkdir -p "$STAGE/arm-attempts"
mkdir "$ATTEMPT_DIR"
cp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
printf '[]\n' > "$ATTEMPT_DIR/attempts.json"
```

For this real class, census exit 0 is diagnostic: inspect `foreign_pids`, descendants and diagnostics; it does not authorize publication over a foreign hit.

Generate the email from the actual staged bytes:

```zsh
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
```

Send with the activation's authorized mail tool, using that recipient, subject and body; reuse an available notice thread. **Accepted email → publication → probe → install.** Record the actual NO relay and any unreadable-thread limitation; do not claim unread replies were checked.

Before publication, write `notice-evidence.txt` with actual acceptance/time/message/thread IDs and fresh observation evidence. Write `notice.json` with these exact keys:

`accepted`, `message_id`, `thread_id`, `sent_epoch_s`, `attempt`, `plan_id`, `receipt_class`, `measurement_head`, `plan_sha256`, `prerequisites_clear`, `veto_clear`, `blocking_causes`, `latest_no_epoch_s`, `latest_abort_epoch_s`.

Populate from actual accepted delivery and observed checks, never presumed success. Initially `attempt=1`, history empty, latest abort null; latest NO is null only when no standing NO was observed. SHA-256 is the exact plan bytes; H is separate. A changed fingerprint/head, later abort/NO or previous-attempt notice invalidates it.

**4. Final checks and publication.**

Refresh authorized directive/STOP/standdown/watchdog/NO observations, retain them, and update the notice's clearance fields from those observations:

```zsh
gh issue list --repo mpmdw/JouleWise --label directive
test -s "$ATTEMPT_DIR/notice-evidence.txt"
test "$(git rev-parse HEAD)" = "$H"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
git fetch origin main
git merge-base --is-ancestor "$H" origin/main
cmp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
gen "$STAGED_PLAN" --verify
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN"
```

Inspect the final census before proceeding. Then:

```zsh
"$PY" -B - <<'PY'
import json,os,time
from pathlib import Path
from joulewise.arm_retry import retry_allowed
from joulewise.night_gate import NightPlan,PLAN_MAX_AGE_S
from scripts.run_night import install_close_epoch
e=os.environ; d=Path(e["ATTEMPT_DIR"]); raw=Path(e["STAGED_PLAN"]).read_bytes()
p=NightPlan.from_mapping(json.loads(raw))
n=json.loads((d/"notice.json").read_text())
assert n["attempt"]==int(e["ARM_ATTEMPT"])
r=retry_allowed(time.time(),dict(
 plan_bytes=raw,saved_plan_bytes=(d/"plan.json").read_bytes(),
 reviewed_head=e["H"],install_close_epoch_s=install_close_epoch(p),
 plan_max_age_s=PLAN_MAX_AGE_S),json.loads((d/"attempts.json").read_text()),n)
assert r.allowed,r.reason
target=Path(e["PLAN"])
assert not target.exists() and not target.is_symlink()
os.replace(e["STAGED_PLAN"],target)
PY
gen "$PLAN" --verify
```

**5. Required launchd probe, then installation.**

From the clone, with the owner present:

```zsh
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY" --launchd-probe
"$PY" -B - <<'PY'
import json,os
from pathlib import Path
r=json.loads((Path(os.environ["NIGHT_ROOT"])/"night_probe_receipt.json").read_text())
print(json.dumps({k:r[k] for k in
 ("custody_elapsed_s","observations","custody_passes","outcome") if k in r},sort_keys=True))
assert r["outcome"]=="ok"
assert r["custody_elapsed_s"]*3*1.5<=r["custody_budget_s"]
PY
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY"
```

Probe success: exit 0 and `launchd probe ok; bootout and process census clear: com.joulewise.night-probe.$PLAN_ID`. Receipt is **`$NIGHT_ROOT/night_probe_receipt.json`**, not inside `night/`. Pending receipt alone is insufficient.

Record the entire receipt plus `custody_elapsed_s`, `observations`, `outcome`, and `custody_passes` **if present**. Current constant is **3**, headroom **1.5**, budget **120 s**: exact limit **120/4.5 = 26.666666… s**; do not round admission upward to 26.67. Observations must be positive when finalized ledger observations exist. Finish-time and file-age limits are strictly under 21600 s; bindings must match both interpreters, inputs, code, ledger and H.

A refusal stops installation; preserve its exact field/code and cleanup evidence. After a consent dialog, repeat successfully without interaction; an interpreter replacement invalidates the probe. Never enlarge the custody budget to force admission.

Install success is exit 0, preflight success JSON and `validated pins: repo_head=… measurement_root=… measurement_head=…`.

**6. Verify, record and exit.**

```zsh
launchctl print "gui/$(id -u)/com.joulewise.night"
launchctl print "gui/$(id -u)/com.joulewise.night.deadman"
plutil -p /Users/edr/Library/LaunchAgents/com.joulewise.night.plist
plutil -p /Users/edr/Library/LaunchAgents/com.joulewise.night.deadman.plist
"$PY" -B scripts/run_night.py schedule --plan "$PLAN"
cmp "$PLAN" "$ATTEMPT_DIR/plan.json"
"$PY" -B - <<'PY'
import json,os,plistlib
from pathlib import Path
from joulewise.night_gate import NightPlan
from scripts.run_night import schedule
e=os.environ; s=schedule(NightPlan.from_mapping(json.loads(Path(e["PLAN"]).read_text())))
for label,key,mode in [
 ("com.joulewise.night","night_calendar","run"),
 ("com.joulewise.night.deadman","deadman_calendar","dead-man")]:
 p=plistlib.loads((Path("/Users/edr/Library/LaunchAgents")/(label+".plist")).read_bytes())
 assert p["StartCalendarInterval"]==s[key]
 assert p["WorkingDirectory"]==e["MEASUREMENT_ROOT"]
 assert p["RunAtLoad"] is False
 assert p["ProgramArguments"][:5]==[
  e["PY"],e["MEASUREMENT_ROOT"]+"/scripts/run_night.py",mode,"--plan",e["PLAN"]]
 print(label,p["ProgramArguments"])
n=Path(e["NIGHT_ROOT"])/"night"
print("night baseline",[(p.name,p.lstat().st_size,p.lstat().st_mtime_ns) for p in sorted(n.iterdir())])
print("frozen triple",json.dumps(dict(plan_id=e["PLAN_ID"],root=e["MEASUREMENT_ROOT"],head=e["H"])))
PY
```

Verify the remaining courier argv too. Night calendar uses Month/Day/Hour/Minute; dead-man uses Hour/Minute only. No `com.joulewise.night.$PLAN_ID` production label exists.

In the authorized bookkeeping worktree, retain commands/return codes, clean-tree/lock checks, ledger sequence/digest, epoch outputs, scientific pre-registration digest/blob/H, D-102 rule commit, runbook revision/commit, calibration-plan identity/hash, D-166 path/hash, input/wrapper/source hashes, evidence-root registration, all schedule boundaries, notice/attempt evidence, probe receipt, installed plist dumps and `night/` baseline. Record power/powermode and timer evidence. Preserve every attempt separately.

Leave the exact durable triple **`(PLAN_ID, MEASUREMENT_ROOT, H)`**, arm result, plan digest, completion and harvest pointer. Commit/push the authorized arm record and pointer, then terminate the magistrate activation **strictly before `T0−480`**.

The production gate's exact census is:

```zsh
/usr/bin/pgrep -lf 'codex|claude|t3'
```

Empty output with exit 1 means no match. By REQUEST, this magistrate's own `claude -p`, its Codex children/MCP servers, seats, background shells/helpers, interactive sessions and matching desktop-app helpers must be gone. Arm-time ancestry exemption does not survive into the production census. Quit ChatGPT/Claude desktop apps; announcing completion does not terminate an interactive process. Never signal foreign processes.

**Refusal routing — one action per cause.**

Stage/cause | Action
---|---
Clone collision, dirty tree, H/lock mismatch | Stop and obtain a fresh reviewed clone; preserve existing paths.
Epoch check 0; unexplained mismatch; acceptance/ledger/pre-registration refusal | Stop for the named scientific/custody review; no derivation arm.
Desk-input refusal: wrong interpreter, empty fields, absent output directory, invalid acceptance | Correct that desk prerequisite before authoring; no `--force` over pinned inputs.
Existing desk inputs or generator `--verify` mismatch | Preserve and explain drift; do not overwrite the discrepancy.
Generator missing flags, malformed/class/path/sidecar/window/slot/census-substring/input refusal; syntax/preflight failure | Correct the named defect under ordinary planning before notice; retain 12/600/600/480 and 9000.
`arm_idle_interactive` | Wait for the evidenced idle session to close; repeat unchanged census.
`arm_notice_mismatch` | Recheck unchanged candidate/fixed inputs, then send a newly accepted notice.
`arm_watchdog_uncertain` | Let watchdog clear itself: two sane clock samples or successful network positive control with stop absent.
`arm_transport` | Restore named transport; after publication require positive noncommit plus uninstall/preservation/comparison/unpublication proof.
`install_span_closed`, `plan_t0_in_the_past` | Preserve failure and author a new future plan.
`install_outside_span` | Wait for an allowed span before cutoff; never switch spans within a transaction.
`night_agent_already_loaded`, retained prior plist | Complete documented harvest/uninstall; UNKNOWN requires human resolution.
`plan_outside_custody_root` | Use the prescribed publication path.
`night_plan_malformed`, `plan_schedule_unrepresentable`, `plan_t0_not_minute_aligned`, `plan_t0_ambiguous_local_time` | Correct through fresh valid planning.
`install_spans_unresolvable_on_day` | Stop for resolution; never silently alter spans.
Unsupported plist destination; render directory equals launch directory | Resolve the destination/use a separate render directory.
Probe missing/invalid/stale/mismatched receipt, failed outcome, bad observations/headroom, timeout or unproven cleanup | Preserve exact refusal; no install or automatic science retry; resolve the named cause.
Installer committed/0 | Record and exit.
Installer restored/nonzero | Record original failure; classify it before any retry.
Installer retained/4, teardown/restoration failure, lost/unknown result | Preserve files and stop for human resolution.

The handback assigns **all** these gate/driver causes to the cold path, never the four-event arm-retry exception:

`night_refused_agent_present`, `night_refused_not_quiet`, `night_refused_hid_idle`, `night_refused_boot_clock`, `night_refused_registration`, `night_window_expired`, `night_plan_stale`, `night_plan_malformed`, `night_chain_digest_mismatch`, `launch_go_receipt_missing`, `launch_go_receipt_invalid`, `night_refused_class_unbuilt`, `night_receipt_class_invalid`, `night_probe_error`, `night_aborted_agent_present`, `night_chain_already_started`, `night_chain_alive`, `night_chain_launch_failed`, `night_courier_running`, `night_courier_unavailable`, `night_plan_overruns_deadman`, `night_record_exists`, `night_calibration_refused`, `night_window_exceeded`; likewise `HOLD_CENSUS`, `slot_refused`, unknown/mixed causes and concurrent scientific refusals.

Preserve/harvest first, respect live-process ownership, then follow the named review/recovery route. §Next lane permits the three machine-state refusals to become **new plans after harvest/uninstall**, never same-plan re-arms. Physics/evidence/pre-registration refusals go to the cold gate/Ed. A refused probe grants no recovery authority.

After any post-publication failure, uninstall first:

```zsh
scripts/install_night_agent.sh --plan "$PLAN" --uninstall
```

Only with exit 0 **and positive noncommit/no-invocation evidence**, preserve and compare before unpublishing:

```zsh
test ! -e "$ATTEMPT_DIR/failed-night_plan.json"
cp "$PLAN" "$ATTEMPT_DIR/failed-night_plan.json"
cmp "$ATTEMPT_DIR/failed-night_plan.json" "$ATTEMPT_DIR/plan.json"
rm "$PLAN"
```

Eligible retries preserve original bytes, use the next exclusive six-digit attempt directory, retain `outcome.json` and chronological history, wait at least 60 seconds between attempt starts, and obtain a fresh notice. No attempt cap or extra notice-age interval; cutoff and 36-hour bounds still apply. Never clear an earlier NO by changing threads.

**Text/code discrepancies at c613e71e.**

- §1.4a/handback definitions still say 25-minute span and 85-minute cutoff; code and §1.3 use **8 and 10 minutes**.
- §0.2 omits venv creation/install commands; its cited record supplies the recipe above. Current generic naming adds `WINDOW_ID`; this brief explicitly requests the prior arm's unsuffixed naming.
- §1.4's final foreground block omits the required probe. Its flag inventory omits `--launchd-probe`, `--probe-timeout-s`, `--probe-max-age-s`, and accepted matching `--hour`/`--minute`. Use no calendar overrides.
- §1.1a says four driver environment variables; code supplies seven, including `JOULEWISE_NIGHT_PLAN_ID`, `NIGHT_DIR`, `CUSTODY_BUDGET_S`.
- Scientific pre-registration still pins `b8bf5b0a…`; tracked chain is `b5beea464d39…`. Revision 3 must resolve this at H. The gate directly checks wrapper/sidecar equality; the old Markdown digest is not itself that executable check.
- The handback specifies notice contents, not an exact subject string. The template above uses the historical `NIGHT NOTICE` prefix.
- Nominal completion remains `T0+9300`; a deadline-aborted chain can require another 70 seconds for termination proof and courier time. Completion alone never authorizes harvest over a live or indeterminate chain.