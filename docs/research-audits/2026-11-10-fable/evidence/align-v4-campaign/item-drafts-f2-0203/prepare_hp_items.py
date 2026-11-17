"""Render conditional hp-02 drafts. No measurement or host action occurs here."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE=Path(__file__).resolve().parent
TZ=ZoneInfo('America/Los_Angeles')
PIN='dd206025abb30fd5c07515cd4b34b3e653174810'
DATE='2026-11-21'  # A qualification t0-date, never hp-01's Nov15 date.

GATES=r'''hp_gate() {
  now=$(date +%s)
  for proof in "HP_LOOK_RUN:${HP_LOOK_RUN:-}" "HP_DELTA_OK:${HP_DELTA_OK:-}" "HP01_SMOKE_PASS:${HP01_SMOKE_PASS:-}" "LINE2_OK:${LINE2_OK:-}" "LINE9_OK:${LINE9_OK:-}" "CHECKLIST_OK:${CHECKLIST_OK:-}" "STOPS_CLEAR:${STOPS_CLEAR:-}" "HOST_STATE_RECORDED:${HOST_STATE_RECORDED:-}" "COPY_TYPED_OK:${COPY_TYPED_OK:-}" "HOST_RESTORE_OK:${HOST_RESTORE_OK:-}" "GROUPS_ABSENT:${GROUPS_ABSENT:-}"; do
    case "$proof" in HP_LOOK_RUN:no|*:yes) ;; *) echo "STOP: missing/failed hp-02 admission $proof"; return 1;; esac
  done
  test "${HP_LOOK_RUN:-}" = no || { echo 'VOID: lm-hp-01 already run or unknown'; return 1; }
  test -n "${HP_LOOK_RECORD:-}" && test -n "${COPY_EVIDENCE:-}" && test -n "${HP01_DATES_RECORD:-}" || { echo 'STOP: evidence pointers required'; return 1; }
  for val in "${ISSUED_EPOCH:-}" "${KIT_ISSUED_EPOCH:-}" "${WATCH_UNTIL_EPOCH:-}" "${QUAL_CLOSE_EPOCH:-}" "${LATEST_CLOSE_EPOCH:-}" "${PRIOR_CLOSE_EPOCH:-}" "${NEXT_COUNTED_EPOCH:-}"; do
    case "$val" in ''|*[!0-9]*) echo 'STOP: missing/invalid epoch'; return 1;; esac
  done
  test "$ISSUED_EPOCH" -le "$now" && test "$now" -lt $((ISSUED_EPOCH+86400)) && test "$now" -lt 1795420800 || { echo 'VOID: item/queue expiry'; return 1; }
  test "$KIT_ISSUED_EPOCH" -le "$now" && test "$now" -lt $((KIT_ISSUED_EPOCH+604800)) || { echo 'VOID: seven-day kit expiry'; return 1; }
  test "$now" -lt "$WATCH_UNTIL_EPOCH" && test "$WATCH_UNTIL_EPOCH" -le $((now+86400)) || { echo 'STOP: watcher stale/future'; return 1; }
  today=$("$PY" -I -B -c 'import datetime,sys; from zoneinfo import ZoneInfo; print(datetime.datetime.fromtimestamp(int(sys.argv[1]),ZoneInfo("America/Los_Angeles")).date())' "$now") || return 1
  test "${QUAL_DATE:-}" = "$today" && test "$QUAL_CLOSE_EPOCH" -lt "$now" && test "${QUAL_CLEAN:-}" = yes && test -n "${QUAL_RECORD:-}" || { echo 'WAIT: a clean qualification span on this t0-date must precede hp-02'; return 1; }
  qday=$("$PY" -I -B -c 'import datetime,sys; from zoneinfo import ZoneInfo; print(datetime.datetime.fromtimestamp(int(sys.argv[1]),ZoneInfo("America/Los_Angeles")).date())' "$QUAL_CLOSE_EPOCH") || return 1
  # QUAL_DATE is the qualification SPAN t0-date, not its close date. A close may cross midnight.
  case ",${HP01_T0_DATES:-}," in *",$today,"*) echo 'VOID: hp-01 leg on same t0-date'; return 1;; esac
  test -n "${HP01_T0_DATES:-}" || { echo 'STOP: hp-01 date census required'; return 1; }
  for proof in "SESSION_READY:${SESSION_READY:-}" "COUNTED_READY:${COUNTED_READY:-}" "F2_READY:${F2_READY:-}"; do
    case "$proof" in *:no) ;; *:yes) echo "CEDE: higher rung $proof"; return 1;; *) echo 'STOP: priority unknown'; return 1;; esac
  done
  test "${F0_ELIGIBLE:-}" = no || { echo 'CEDE: F0 eligible/unknown'; return 1; }
  case "${F0_REASON:-}" in spacing|daily_cap|launch_window) ;; *) echo 'STOP: unsafe F0 refusal'; return 1;; esac
  test -n "${PRIORITY_RECORD:-}" || { echo 'STOP: priority census missing'; return 1; }
  if test "$NEXT_COUNTED_EPOCH" != 0 && test "$NEXT_COUNTED_EPOCH" -lt $((now+PROTECTED_S)); then echo 'CEDE: protected counted start'; return 1; fi
  case "${LAST_CLOSE_KIND:-}" in campaign) gap=300;; other) gap=1200;; *) echo 'STOP: close kind unknown'; return 1;; esac
  test "$LATEST_CLOSE_EPOCH" -ge "$QUAL_CLOSE_EPOCH" && test "$now" -ge $((LATEST_CLOSE_EPOCH+gap)) && test "$now" -ge $((PRIOR_CLOSE_EPOCH+gap)) || { echo 'WAIT: latest-close interval'; return 1; }
  test -n "${LATEST_CLOSE_RECORD:-}" || { echo 'STOP: latest-close receipt census record required'; return 1; }
  test "${PREDECESSOR_CLEAN:-}" = yes && test -n "${PREDECESSOR_RECORD:-}" || { echo 'VOID: predecessor not clean; never skip'; return 1; }
  picked=$(pick_arg "$now")
  test "$picked" != NONE && test "$picked" = "$ARG" || { echo 'STOP: date/band/argument changed'; return 1; }
  echo 'HP02 GATES PASS (record-backed operational observations only)'
}
'''

CHECK=r'''import json, sys
from pathlib import Path
out=Path(sys.argv[1]); roster=sys.argv[2].split(',')
r=json.loads((out/'runner_receipt.json').read_text())
assert r.get('mock') in (None,False), 'synthetic receipt is not live evidence'
assert r['runner_kind']=='cadence-legs-v1' and r['roster']==roster
assert r['batch_windows']==[sys.argv[3]]
assert r['kit']['campaign_id']=='cl-hp-02' and r['kit']['sha256']=='@SHA@'
assert r['kit']['frozen_commit']=='dd206025abb30fd5c07515cd4b34b3e653174810'
assert r['rc']==0 and not r.get('error') and r['legs_finished']==len(roster)==r['legs_planned']
assert r['span_result']['outcome']=='MEASURED_OK' and r['span_result']['chain_outcome']=='COMPLETE'
hp=r['high_power']; proof=hp['close_proof']
assert proof['proven'] is True and proof['ac_powermode']==0 and proof['host_marker_present'] is False
assert not hp.get('revoked'), 'HP admission revoked: hold for the research lead'
assert set(r['feeds'])=={'agents','meter','volumes'}
assert all(f['stop']['proven_stopped'] is True for f in r['feeds'].values())
assert all(sum(s['name']==name for s in r['steps'])==1 for name in ('restore','stop-agents','stop-meter','stop-volumes','power_proof','host_lock_release'))
assert all(s['rc']==0 for s in r['steps'] if s['name']=='restore' or s['name'].startswith(('stop-','close-','power_','host_lock_release')))
span=json.loads((out/'desk-bundle/span/result.json').read_text()); assert span['restore_proven'] is True
print('operational receipt',r['rc'],r['legs_finished'],r['ended'],'power close',proof)
for leg in roster:
    rec=json.loads((out/'legs'/leg/'leg_record.json').read_text())
    result=rec.get('result') or {}
    summary=json.loads((out/'desk-bundle/legs'/leg/'leg_summary.json').read_text())
    print(leg,{k:result.get(k) for k in ('leg_status','g0_outcome','g0_wait_s','decode_tokens','decode_cap_reached','prefill_tokens','ac_powermode')},
          {k:summary.get(k) for k in ('admitted','wall_s','budget_s','contaminated_redos','g0_outcome')})
print('RECEIPT OK; this is operational verification, never an energy read')
'''

def main(repo):
    build=json.loads((HERE/'evidence/kit-build.json').read_text())
    r=next(x for x in build['kits'] if x['name']=='cl-hp-02')
    folder=HERE/'hp-02'; sha=r['sha256']
    qa={'schema':'joulewise.cadence_queue.v1','queue_id':'cq-hp-02-a',
        'expires_at':'2026-11-23T00:00:00-08:00','halt':None,'standing_notice':None,'spans':[]}
    items=[]
    for n,ids in enumerate((range(1,4),range(4,8),range(8,13)),1):
        roster=[f'L{i:03d}' for i in ids]; legs=','.join(roster); span=f'hp-02-s{n:02d}'
        qa['spans'].append({'seq':n,'span_id':span,'block_id':'hp-02',
            'kit':{'path':'hp-02/cl-hp-02.json','sha256':sha},'legs':roster,'attempt':1,
            'not_before':DATE,'rerun_of':None})
        p=next(x['plan'] for x in r['plans'] if x['piece']==n and x['argument']=='02:00-02:35')
        worst=p['worst_case_s']; expected=p['expected_s']; deadline=worst+1460
        # Retain hp-01's 00:30 unattended work-end bound, RL-165 §7 / RL-171 §2.
        a=int(dt.datetime.fromisoformat(DATE).replace(tzinfo=TZ).timestamp())
        latest=a+86400+1800-worst
        bands=[(a,a+9299,'13:14-13:15'),(a+9300,a+39000,'02:00-02:35'),(a+47700,latest,'02:00-02:35')]
        probes=[]
        for lo,hi,arg in bands:
            for t in (lo,hi):
                result=subprocess.run([sys.executable,'-B','scripts/cadence_legs_runner.py','plan',
                    '--kit',str(folder/'cl-hp-02.json'),'--legs',legs,'--t0',str(t),'--batch-window',arg],
                    cwd=repo,text=True,capture_output=True)
                assert result.returncode==0,(n,t,arg,result.stdout,result.stderr)
                q=json.loads(result.stdout); assert q['blackout_clear']
                probes.append({'epoch':t,'argument':arg,'rc':result.returncode})
        pick='pick_arg() {\n  n=$1\n'
        for i,(lo,hi,arg) in enumerate(bands):
            pick+=f'  {"if" if i==0 else "elif"} [ "$n" -ge {lo} ] && [ "$n" -le {hi} ]; then echo {arg}\n'
        pick+='  else echo NONE; fi\n}\n'
        pred='qual-03-s02' if n==1 else f'hp-02-s{n-1:02d}'
        check=CHECK.replace('@SHA@',sha)
        text=f'''TBD. **Laptop lead; Sol 6.1 builder draft, NOT ISSUED. ISSUED <LEAD FILLS from `date`>. MAGISTRATE: arm `{span}` once, kit `cl-hp-02` sha256 `{sha}`, runner cadence-legs-v1 at detached `{PIN}`. Roster {legs}. Automatic soak, then High Power legs, q0, 19,458 prefill / 4,096 decode; close restores Automatic and proves no marker. Expected {expected:,} s; work worst {worst:,} s; deadline {deadline:,} s. Predecessor `{pred}` must close clean; never skip it. Date {DATE} only; item expires 24 h after issue; kit voids seven days after kit issue. Launch is the last action; exit immediately.**

```pointer
owner: magistrate
wait: none
deadline: {dt.datetime.fromtimestamp(latest+deadline+3600,TZ).isoformat()}
on_early_or_refused: WAIT on missing operational evidence or a higher rung; VOID on a failed predecessor, expired item or missed date. No retry, queue extension, changed roster or reused OUT. Any restore-unproven state holds everything; LEG_OVERTIME goes to the research lead (RL-157 §5).
next_observable: next activation after the shared fence is gone runs Check and reports operational receipt/restore/desk lines to the lead; no streams are opened
```

RL-174 B.1 and hp-02 conditions admit this second descriptive block **only while lm-hp-01 has not run**. The admission basis is [HP-ADMISSION.md](../HP-ADMISSION.md); the lead rechecks it at issue and the magistrate at both gates. The future lm-hp-01 manifest must list hp-01 AND hp-02 by kit/receipt identities before any High Power energy is read. Never enter a fit, frozen coefficient, A-B-A verdict or series-mode decision. No reserve or replacement leg (RL-157 §4).

This is hp-01's kit with a new name, seed and ruling; frozen block, model, mode, budgets, runner and all other fields are unchanged. Its source is bbd34dc87, pin dd206025a (RL-174's same-pin condition; **not** F2's 2d347f721). One independent executing delta check is required; the builder's checks do not fill HP_DELTA_OK. hp-01's class A smoke is already recorded in main item338, and is not manufactured anew. The 3+4+5 split preserves hp-01's as-run cold positions L001/L004/L008 and RL-157's span-position matching. The old kit prose names hp-01/the interim look/a reserve; RL-157 and RL-167 §3 and RL-174 supersede those literals externally.

**Same-date gate.** This date is a qualification t0-date in the default plan. Require a qualification span with that SAME t0-date to have run and closed clean before EVERY hp-02 span. QUAL_DATE is its t0-date, never inferred from its close date. The hp-01 t0-date census (main items334–344: Nov15) must exclude this date. A slip of qualification to Sun22 requires a newly dated hp item/queue; this item never grants an extra qualification run to make itself fit. The forecasts reserve no slot: no READY v4, counted work, eligible F0, or any READY F2 inst-01/02/03 may be displaced. A lack of room is a lawful unrun filler.

**Inherited High Power safety.** RL-157 applies in full. The runner writes the host marker before changing AC mode; no child writes mode; an unproven child is never admitted. The close restores Automatic even under an unproven child; REFUSAL remains until the lead proves the pid/start-time group gone and reads AC mode 0 again. RESTORE_UNPROVEN, a marker or a host-state stop holds every arm. Never run restore-owed at an arm or while any fence is live. LEG_OVERTIME goes to the research lead; fewer than nine included legs is reported before the High Power read. Print seconds from high_power step end to first G0 and every wall/budget, gating nothing.

**Arm-record lines.** Lead fills evidence pointers for per-kit independent delta ADMIT; inherited hp-01 line2 (CI 43673985768 at 2a8deb7b9 = fe907d0d3's twelve-red set, frozen equality); committed queue path/hash; validate-kit; operational checklist; no named stop/revocation; watcher under 24 h (or qualifying scheduled-main Actions success after previous close); hp-01 smoke record; and actual cross-block k−2 desk/Q1 debt under the lead's campaign classification. Do not infer a new campaign ordinal from this draft. HP_LOOK_RECORD, QUAL_RECORD, HP01_DATES_RECORD, PREDECESSOR_RECORD, LATEST_CLOSE_RECORD, COPY_EVIDENCE and PRIORITY_RECORD are current signed/issued operational records, never a bare yes. The latest-close census covers campaign-out, f2-out and jw-wt (plus out-of-census session closes), rounds up fractional times, and refuses errors, missing roots or ambiguity; LAST_CLOSE_KIND must agree with that selected receipt. Copy evidence is a typed verified marker with RL-173 A.2 fields, and RL-174 A.12's migration/reverification; a legacy one-line ok is insufficient. A failed offload holds the next soak.

**Start and check** (magistrate on MBP only after lead issue; builder never executes this block).

The lead stages the exact committed kit and queue with stage_mbp_span.py, in a clean close interval. Staging does no test, launch or measurement. Never stage BLOCK-QUEUE blocks[] for a filler. All real command paths below are reviewable drafts, not builder authority.

```sh
set -eu
set -o pipefail
cd /Users/edr/code/jw-wt/cadence-{span}
PIN={PIN}
test "$(git rev-parse HEAD)" = "$PIN" && test -z "$(git status --porcelain)" || exit 1
git symbolic-ref -q HEAD >/dev/null && exit 1
REPO="$PWD"
: "${{PY:?existing pinned measurement interpreter}}"
: "${{MAGISTRATE_PID:?own magistrate process PID}}"
KIT=/Users/edr/campaign-out/kits/cl-hp-02-RL174B.json
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = {sha} || exit 1
: "${{QUEUE_FILE:?staged committed hp-02 queue}}"; : "${{QUEUE_SHA:?its committed hash}}"
test "$(shasum -a 256 "$QUEUE_FILE" | cut -c1-64)" = "$QUEUE_SHA" || exit 1
SPAN={span}; LEGS={legs}; PROTECTED_S={worst+560+1200}
# BEGIN TESTABLE GATES
{pick}{GATES}# END TESTABLE GATES
# Fill ISSUED_EPOCH/KIT_ISSUED_EPOCH/WATCH_UNTIL_EPOCH and evidence observations from the lead's issued record.
ARG="$(pick_arg "$(date +%s)")"; export ARG
hp_gate || exit 1
CUSTODY="${{MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}}"
test ! -e "$CUSTODY/desk_fence.json" || exit 1
test ! -e /Users/Shared/JouleWise/host-power/high-power.marker && test ! -L /Users/Shared/JouleWise/host-power/high-power.marker || exit 1
test -z "${{JOULEWISE_HOST_STATE_DIR:-}}" || exit 1
sudo -n -l  # record both pmset -c powermode 0 and 2 rules; either absent is STOP
pmset -g custom  # AC powermode 0, AC, not charging; never switch mode at this preflight
sudo -n systemsetup -getusingnetworktime  # Off; frequency word 0, no night.lock holder
MODE_VERIFY_RC=0
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify || MODE_VERIFY_RC=$?
echo "measurement_mode verify rc $MODE_VERIFY_RC"
# Every FAIL stops except the magistrate's own process tree agent census (record those exact PIDs).
# Print RL-174 C's four host lines and no pending iCloud transfer. No hygiene setting changes freeze2 through qual03 close.
export TMPDIR="$(mktemp -d /tmp/jw-hp02-preflight.XXXXXX)" JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=.:tests
for module in tests.cadence.test_high_power tests.cadence.test_legs_runner tests.cadence.test_kit tests.cadence.test_stops_desk tests.cadence.test_runner_guards tests.align.test_r1_smoke_launcher; do
  python3.13 -B -m unittest "$module" || exit 1
done
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG" || exit 1
"$PY" -B scripts/cadence_legs_runner.py plan --kit "$KIT" --legs {legs} --batch-window "$ARG" || exit 1
# Assert expected_s {expected}, worst_case_s {worst}, blackout_clear true, batch_windows [ARG].
OUT=/Users/edr/campaign-out/cl-hp-02/cq-{span}-a1-$(date -u '+%Y%m%dT%H%M%SZ')
test ! -e "$OUT" || exit 1
```

**Run.** Re-read all arm-record observations now, including no High Power read, same-date qualification, full higher-rung census, latest-close/restore/group and typed copy, watcher and predecessor. Nothing of the lead runs on the MBP while armed. Exit immediately after launch.

```sh
hp_gate || exit 1
test ! -e "$CUSTODY/desk_fence.json" || exit 1
DEADLINE="$("$PY" -I -B -c 'import time; print(time.time()+{deadline})')"
"$PY" -B scripts/launch_cadence_span.py launch \\
  --repo "$REPO" --python-bin "$PY" --kit "$KIT" --legs {legs} --batch-window "$ARG" \\
  --output "$OUT" --disk-path "$REPO" --custody-root "$CUSTODY" \\
  --magistrate-pid "$MAGISTRATE_PID" --deadline "$DEADLINE" \\
  --exit-wait-seconds 180 --start-wait-seconds 30
```

**Check.** Only after the fence is gone, read the operational runner_receipt, span/result, leg_record and desk-bundle leg_summary projection; never any stream, member output, slot or custody content. Verify exact kit hash/pin/roster, rc/error, leg counts and span_result; power close proof restore_proven=true, AC mode0, marker absent, every feed proven stopped and close step rc0; print any high_power.revoked entry as a hold. The lead records no open named stop and the fresh native process-group/AC0/no-marker/network-time-off/frequency0 readback. Do not silently clear REFUSAL on restore proof alone. Record actual close/fence-gone times and typed verified off-host copy before any next soak. The lead's pinned desk reads only the projection. Any incomplete/short/G0-unreleased leg is kept/flagged under the kit rules, never replaced; it is no energy read. Report wall/budget and mode-to-first-G0 delay, description only. No next span is authorized by this item.

```sh
"$PY" -I -B - "$OUT" "$LEGS" "$ARG" <<'PY'
{check}PY
pmset -g custom  # require AC powermode0; no host marker or link, no lock holder
sudo -n systemsetup -getusingnetworktime  # Off; frequency word0; prove all receipt-named groups gone
MODE_VERIFY_RC=0
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify || MODE_VERIFY_RC=$?
echo "measurement_mode verify rc $MODE_VERIFY_RC"  # own-agent-tree exception only, as Start
```

**Staging and queue.** queue-a.json is a DRAFT of all three finite spans, 3+4+5, at this date, no automatic retry. No new class A smoke is claimed; hp-01's same-byte smoke and the independent delta gate supply admission (RL-174 B). The lead settles the inherited smoke/counting prose with the delta seat before issue; this builder assigns no campaign ordinal or cap ruling. On any failed predecessor the item is VOID, never skipped; new unrun-only queues need lead authority. The look's manifest and all outputs come to the research lead; this item cannot read or modify them.
'''
        (folder/f'ITEM-{span}.md').write_text(text)
        items.append({'item':span,'span':span,'piece':n,'date':DATE,'legs':roster,'predecessor':pred,
                      'expected_s':expected,'worst_case_s':worst,'deadline_s':deadline,
                      'bands':bands,'plan_endpoints':probes,'pin':PIN,'kit_sha':sha})
    (folder/'queue-a.json').write_text(json.dumps(qa,indent=1)+'\n')
    (folder/'items.json').write_text(json.dumps(items,indent=2)+'\n')
    (folder/'gates.sh').write_text(GATES)
    print('Rendered three conditional hp-02 drafts; NOT ISSUED')

if __name__=='__main__': main(Path(sys.argv[1]).resolve())
