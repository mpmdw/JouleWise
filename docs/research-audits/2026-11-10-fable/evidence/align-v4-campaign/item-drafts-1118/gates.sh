# Included verbatim in each item by build_items.py; no production command runs here.
# BEGIN TESTABLE GATES
ISSUED_EPOCH="<LEAD FILLS: ISSUED_EPOCH>"
WATCH_UNTIL_EPOCH="<LEAD FILLS: WATCH_OBSERVED_EPOCH + 86400>"
expiry_gate() {
  case "$ISSUED_EPOCH" in ''|*[!0-9]*) echo 'WAIT: issue epoch unfilled (RL-173 D.5)'; return 1;; esac
  now=$(date +%s); EXPIRES_EPOCH=$((ISSUED_EPOCH + 86400))
  test "$ISSUED_EPOCH" -le "$now" && test "$now" -lt "$EXPIRES_EPOCH" \
    || { echo 'VOID: future issue or 24 h expiry (RL-173 D.5)'; return 1; }
}
watch_gate() {
  case "$WATCH_UNTIL_EPOCH" in ''|*[!0-9]*) echo 'WAIT: watcher stamp unfilled (RL-173 C.5)'; return 1;; esac
  now=$(date +%s)
  test "$now" -lt "$WATCH_UNTIL_EPOCH" && test "$WATCH_UNTIL_EPOCH" -le $((now + 86400)) \
    || { echo 'STOP: watcher stale or observation in future (RL-173 C.5)'; return 1; }
}
pred_gate() {
  PRED_LINE="$("$PY" -I -B - /Users/edr/campaign-out "$PRED_CAMP" "$PRED_SPAN" "$PRED_ROSTER" "$PRED_KIT_SHA" "$PRED_PIN" <<'PY'
import json, math, os, re, sys
root, camp, span, roster, kit_sha, pin = sys.argv[1:]; roster = roster.split(',')
def stop(s): sys.exit(s)
d = os.path.join(root, camp)
if not os.path.isdir(d): stop('WAIT: predecessor has not run')
pat = re.compile('cq-' + re.escape(span) + r'-a\d+-\d{8}T\d{6}Z')
hits = sorted(n for n in os.listdir(d) if pat.fullmatch(n))
if not hits: stop('WAIT: predecessor has not run')
if len(hits) != 1: stop('STOP: multiple predecessor outputs; lead must resolve')
out = os.path.join(d, hits[0]); p = os.path.join(out, 'runner_receipt.json')
if not os.path.isfile(p): stop('WAIT: predecessor has not closed')
try:
    r = json.load(open(p)); bad = []
    num = lambda x: isinstance(x, (float, int)) and not isinstance(x, bool) and math.isfinite(x)
    if r.get('rc') != 0 or r.get('error') not in (None, '') or r.get('mock') not in (None, False): bad.append('receipt status/mock')
    if r.get('roster') != roster or r.get('legs_planned') != len(roster) or r.get('legs_finished') != len(roster): bad.append('roster/count')
    k = r.get('kit') or {}
    if (r.get('runner_kind') != 'cadence-legs-v1.1' or k.get('campaign_id') != camp or k.get('sha256') != kit_sha
            or k.get('frozen_commit') != pin): bad.append('kit/runner identity')
    sr = r['span_result']
    if sr.get('outcome') != 'MEASURED_OK' or sr.get('chain_outcome') != 'COMPLETE' or sr.get('fault') is not False: bad.append('span result')
    steps = r['steps']; close = [s for s in steps if s['name'] == 'restore' or s['name'].startswith(('stop-', 'close-'))]
    if any(sum(s['name'] == name for s in close) != 1 for name in ('restore','stop-agents','stop-meter','stop-volumes')) or any(s['rc'] != 0 for s in close): bad.append('restore/close')
    if set(r.get('feeds') or {}) != {'agents','meter','volumes'} or any(f.get('stop', {}).get('proven_stopped') is not True for f in r['feeds'].values()): bad.append('feed stop unproven')
    m = r.get('meter') or {}
    if m.get('present') is not True or m.get('proven_stopped') is not True or m.get('bad_polls') != 0 or m.get('usb_errors') != 0: bad.append('meter operational fault')
    ended = r['ended']['epoch_s']
    if not num(ended) or ended <= 0: bad.append('close stamp')
    over = redos = 0
    for leg in roster:
        s = json.load(open(os.path.join(out, 'desk-bundle', 'legs', leg, 'leg_summary.json')))
        w, b, c = s['wall_s'], s['budget_s'], s['contaminated_redos']
        if not (num(w) and w >= 0 and num(b) and b > 0 and type(c) is int and c >= 0): raise ValueError('summary fields')
        over += w > 1.5 * b; redos += c
    if over >= 2: bad.append('LEG_OVERTIME')
    if redos >= 3: bad.append('CONTAMINATED_REDOS')
except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
    stop('VOID: unreadable predecessor operational evidence: ' + str(e))
if bad: stop('VOID: predecessor did not close clean: ' + ', '.join(bad) + '; never skip (RL-173 D.2)')
print(math.ceil(ended))
PY
)" || return 1
  PRED_CLOSE_EPOCH=$PRED_LINE
  case "${PRIOR_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo 'STOP: PRIOR_CLOSE_EPOCH must be an epoch'; return 1;; esac
  test "$PRIOR_CLOSE_EPOCH" -ge "$PRED_CLOSE_EPOCH" || { echo 'STOP: PRIOR before predecessor close'; return 1; }
  echo "PRED CLEAN $PRED_SPAN close_epoch $PRED_CLOSE_EPOCH"
}
effective_close() {
  case "${OTHER_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo 'STOP: OTHER_CLOSE_EPOCH required, explicit 0 if none'; return 1;; esac
  CENSUS="$("$PY" -I -B - /Users/edr/campaign-out /Users/edr/code/jw-wt <<'PY'
import json, math, os, sys
def fail(e): raise e
found = []
for root in sys.argv[1:]:
    if not os.path.isdir(root): sys.exit('STOP: missing receipt root: ' + root)
    base = root.rstrip('/').count('/')
    for d, dirs, files in os.walk(root, onerror=fail):
        if d.count('/') - base >= 3: dirs[:] = []
        if 'runner_receipt.json' in files:
            p = os.path.join(d, 'runner_receipt.json')
            if '\n' in p: sys.exit('STOP: bad receipt path')
            try:
                with open(p) as handle: ended = json.load(handle)['ended']['epoch_s']
                if (isinstance(ended, bool) or not isinstance(ended, (int, float))
                        or not math.isfinite(ended) or ended <= 0):
                    raise ValueError('invalid ended.epoch_s')
            except (OSError, ValueError, KeyError, TypeError) as e:
                sys.exit('STOP: unreadable receipt close stamp: ' + p + ': ' + str(e))
            found.append((ended, p))
if not found: sys.exit('STOP: empty receipt census')
latest = max(t for t, p in found)
newest = [p for t, p in found if t == latest]
if len(newest) != 1: sys.exit('STOP: ambiguous newest receipt close epoch')
print(math.ceil(latest)); print(newest[0])
PY
)" || return 1
  EFF_EPOCH="$(printf '%s\n' "$CENSUS" | sed -n 1p)"
  EFF_PATH="$(printf '%s\n' "$CENSUS" | sed -n 2p)"
  if test "$OTHER_CLOSE_EPOCH" -gt "$EFF_EPOCH"; then
    EFF_EPOCH=$OTHER_CLOSE_EPOCH; EFF_PATH=OTHER
  fi
}
copy_gate() (
  # RL-171 §6.1/RL-173 A: campaign marker, or exact latest non-campaign Check's copy proof.
  case "$EFF_PATH" in
    /Users/edr/campaign-out/cl-*/cq-*/runner_receipt.json)
      id="$(basename "$(dirname "$EFF_PATH")" | sed -E 's/-[0-9]{8}T[0-9]{6}Z$//')";;
    *)
      test "${NONCAMPAIGN_COPY_OK:-}" = yes && test "${NONCAMPAIGN_COPY_CLOSE_EPOCH:-}" = "$EFF_EPOCH" \
        && test "${NONCAMPAIGN_COPY_RECEIPT:-}" = "$EFF_PATH" && filled "${NONCAMPAIGN_COPY_RECORD:-}" \
        || { echo 'WAIT: exact latest non-campaign Check/copy proof missing (RL-171 §6.1; RL-173 A)'; exit 1; }
      echo "COPY CHECK VERIFIED receipt $EFF_PATH close $EFF_EPOCH: $NONCAMPAIGN_COPY_RECORD"; exit 0;;
  esac
  case "$id" in ''|*[!a-zA-Z0-9_.-]*) echo 'STOP: missing/invalid copy plan id'; exit 1;; esac
  for marker in "/Users/Shared/JouleWise/desk-copy/$id.ok" "/Users/Shared/JouleWise/desk-copy/$id.air.ok"; do
    if test -s "$marker"; then echo "COPY VERIFIED $id: $(cat "$marker")"; exit 0; fi
  done
  echo "WAIT: no verified cloud .ok or Air .air.ok copy marker for $id (RL-173 A)"; exit 1
)
close_gate() {
  test "${HOST_RESTORE_OK:-}" = 1 && test "${GROUPS_ABSENT:-}" = 1 \
    || { echo 'STOP: restore or process-group absence unproven'; return 1; }
  effective_close || return 1
  copy_gate || return 1
  case "$EFF_PATH" in
    /Users/edr/campaign-out/cl-*/cq-*/runner_receipt.json) actual=campaign; gap=300;;
    *) actual=other; gap=1200;;
  esac
  test "${LAST_CLOSE_KIND:-}" = "$actual" || { echo 'STOP: contradictory LAST_CLOSE_KIND'; return 1; }
  # Even though the F2 files live in campaign-out, F2 is OTHER: always 1,200 s.
  now=$(date +%s)
  test "$now" -ge $((EFF_EPOCH + gap)) && test "$now" -ge $((PRIOR_CLOSE_EPOCH + gap)) \
    || { echo "WAIT: close interval $gap s"; return 1; }
  echo "CLOSE OK latest $EFF_EPOCH kind $actual interval $gap"
}
# RL-165 §8.1; RL-172 (i) row 9; RL-173 E: freeze 2 is the committed coefficient hash.
FREEZE2_COMMIT="<LEAD FILLS: FREEZE2_COMMIT>"
FREEZE2_COEF_SHA256="<LEAD FILLS: FREEZE2_COEF_SHA256>"
FREEZE2_COEF_PATH="<LEAD FILLS: FREEZE2_COEF_PATH>"
COLD_SEAT_RECORD="<LEAD FILLS: per-kit cold seat ADMIT and RL-167 Part B Q2 confirmation>"
LINE2_RECORD="<LEAD FILLS: qual-pin suite red set equals c3f4bacd8 test for test>"
HOST_EVENT_RECORD="<LEAD FILLS: four host-state lines under RL-174 C, with readback>"
HOST_STATE_ID="<LEAD FILLS: qualification host-state identity frozen before freeze 2>"
INCLUSION_RECORD="RL-174 B.5 at ebff15ad27e831499dd65796b3727d8c5d451e21: six rules unchanged; maintenance overlaps print-only (RESEARCH-LEAD-DECISIONS.md)"
QUEUE_COMMIT="<LEAD FILLS: authenticated audit commit containing this queue>"
filled() {
  case "${1:-}" in ''|*'<LEAD '*) return 1;; *) return 0;; esac
}
freeze2_gate() {
  filled "$FREEZE2_COMMIT" && filled "$FREEZE2_COEF_SHA256" && filled "$FREEZE2_COEF_PATH" \
    || { echo 'WAIT: HOLD_FOR_FIT_FREEZE (RL-165 §8.1; RL-172 (i)9; RL-173 E)'; return 1; }
  "$PY" -I -B - "$AUTH_REPO" "$FREEZE2_COMMIT" "$FREEZE2_COEF_PATH" "$FREEZE2_COEF_SHA256" <<'PY'
import hashlib, re, subprocess, sys
repo, commit, path, sha = sys.argv[1:]
def git(*args): return subprocess.check_output(['git','-C',repo,*args],stderr=subprocess.DEVNULL)
def stop(s): sys.exit('STOP: freeze 2 ' + s)
if not re.fullmatch('[0-9a-f]{40}',commit) or not re.fullmatch('[0-9a-f]{64}',sha): stop('full commit/hash required')
if path.startswith('/') or any(p in ('..','restricted','campaign-out') or p.startswith('night-') for p in path.split('/')): stop('coefficient path not permitted')
try:
    refs = [git('rev-parse','--verify',r+'^{commit}').decode().strip() for r in ('origin/audit/2026-11-10-fable','origin/main')]
    if not any(subprocess.run(['git','-C',repo,'merge-base','--is-ancestor',commit,r],capture_output=True).returncode==0 for r in refs): stop('commit is not ancestor of fetched audit or main')
    blob = git('cat-file','blob',commit+':'+path)
    if hashlib.sha256(blob).hexdigest() != sha: stop('coefficient sha256 mismatch')
except (OSError,subprocess.CalledProcessError): stop('commit/ref/coefficient unreadable')
print('FREEZE2 COMMITTED',commit,path,'sha256',sha)
PY
}
qual_pin_gate() {
  filled "$COLD_SEAT_RECORD" && filled "$LINE2_RECORD" \
    || { echo 'WAIT: qual-pin line 1 / line 2 record pointers unfilled (RL-165 §8.1)'; return 1; }
  test "${QUAL_COLD_SEAT:-}" = ADMIT && test "${LINE2_EQUAL:-}" = yes \
    && test "${LINE2_PIN:-}" = "$PIN" && test "${LINE2_BASE:-}" = c3f4bacd8013ca98c19cf8d41f830c701930cd41 \
    && test "${COLD_SEAT_KIT_SHA:-}" = "$KIT_SHA" && test "${FIRST_CAPTURE_CONFIRMED:-}" = yes \
    || { echo 'STOP: qual admission identity/equality/first-capture proof (RL-165 §8.1; RL-167 Part B Q2)'; return 1; }
  echo "QUAL PIN ADMITTED $KIT_SHA; $COLD_SEAT_RECORD; $LINE2_RECORD"
}
host_event_gate() {
  filled "$HOST_EVENT_RECORD" && filled "$HOST_STATE_ID" \
    || { echo 'WAIT: four host-state lines/readback unfilled (RL-174 C); no restart or hygiene action required'; return 1; }
  case "${HOST_EVENT_DISPOSITION:-}" in done|waived|deferred) ;; *) echo 'WAIT: host-event disposition absent'; return 1;; esac
  # Identity covers hygiene settings, not boot time. RL-174 C permits an unplanned restart.
  test "${CURRENT_HOST_STATE_ID:-}" = "$HOST_STATE_ID" && test "${FREEZE2_HOST_STATE_ID:-}" = "$HOST_STATE_ID" \
    || { echo 'WAIT: record current host state under RL-174 C; an unplanned restart needs an event and four fresh lines, not a new hygiene gate'; return 1; }
  filled "$INCLUSION_RECORD" || { echo 'WAIT: research-lead maintenance-flag disposition at freeze 2 (RL-171 §5.3)'; return 1; }
  # The kit is not silently amended. A changed inclusion rule requires its own lead/research-lead disposition.
  test "${QUAL_INCLUSION_UNCHANGED:-}" = yes \
    || { echo 'WAIT: changed maintenance inclusion needs research-lead disposition and new draft'; return 1; }
  echo "HOST EVENT $HOST_EVENT_DISPOSITION; state $HOST_STATE_ID; $HOST_EVENT_RECORD; $INCLUSION_RECORD"
}
v4_gate() {
  filled "${SESSION_RECORD:-}" || { echo 'WAIT: fresh v4 READY record census required (RL-172 (f))'; return 1; }
  case "${SESSION_READY:-}" in no) echo "V4 not READY: $SESSION_RECORD";; yes) echo 'CEDE: READY v4 session; DO NOT ARM (RL-172 (f))'; return 1;; *) echo 'STOP: unknown v4 readiness'; return 1;; esac
}
day_gate() {
  "$PY" -I -B - /Users/edr/campaign-out "$(date +%s)" "$T0_DATE" "$QUAL_DATES" "$CAMP" "$LEGS" <<'PY'
import datetime as dt, json, math, os, re, sys
from pathlib import Path
from zoneinfo import ZoneInfo
root, now, wanted, dates, camp, legs = sys.argv[1:]
def stop(s): sys.exit('REFUSE: day law ' + s)
TZ=ZoneInfo('America/Los_Angeles'); day=dt.datetime.fromtimestamp(int(now),TZ).date().isoformat()
try:
    planned=dict(x.split('=') for x in dates.split(','))
    if set(planned)!= {'qual-01','qual-02','qual-03'} or len(set(planned.values())) != 3: stop('three distinct dates, one block each (RL-174 B.3)')
    for date in planned.values(): dt.date.fromisoformat(date)
    if day != wanted or planned[camp.removeprefix('cl-')] != day: stop('outside this item t0-date; lead re-dates (RL-172 (a)5)')
    if '2026-11-14' <= day <= '2026-11-18': stop('known development date Sat14-Wed18 (RL-172 (a)3)')
    if any('2026-11-14'<=d<='2026-11-18' for d in planned.values()): stop('planned qualification date is a development date')
    if not os.path.isdir(root): stop('receipt root missing')
    count=0; blocks=set(); firsts={}; seen=[]
    for family in sorted(Path(root).iterdir()):
        if not family.is_dir() or not re.fullmatch(r'cl-(dev|qual)-[a-zA-Z0-9-]+',family.name): continue
        for out in sorted(family.iterdir()):
            if not out.is_dir() or not out.name.startswith('cq-'): continue
            p=out/'runner_receipt.json'
            if not p.is_file(): stop('pending output without receipt '+str(out))
            r=json.loads(p.read_text()); t=r['started']['epoch_s']; roster=r['roster']
            if isinstance(t,bool) or not isinstance(t,(int,float)) or not math.isfinite(t): stop('bad t0 '+str(p))
            if not isinstance(roster,list) or not roster or len(set(roster)) != len(roster) or not all(isinstance(x,str) and re.fullmatch('L[0-9]{3}',x) for x in roster): stop('bad roster '+str(p))
            actual=dt.datetime.fromtimestamp(t,TZ).date().isoformat()
            if family.name.startswith('cl-dev-'):
                if actual in planned.values(): stop('development receipt on qualification date '+actual+' '+str(p))
            else:
                block=family.name.removeprefix('cl-')
                if block in planned and planned[block] != actual: stop('existing qualification receipt disagrees with date plan '+str(p))
                if actual==day:
                    count+=len(roster); blocks.add(block); firsts[block]=min(firsts.get(block,t),t); seen.append((out.name,len(roster)))
    n=len(legs.split(',')); blocks.add(camp.removeprefix('cl-'))
    if count+n > 24: stop('25th leg / >24 qualification legs; RL-174 B.3 / RL-149 §2.3 cap applies')
    if len(blocks)>2: stop('more than two qualification blocks; RL-174 B.3 / RL-149 §2.3 cap applies')
    firsts.setdefault(camp.removeprefix('cl-'),int(now))
    if len(firsts)==2 and abs(max(firsts.values())-min(firsts.values()))<36000: stop('two block starts less than 10 h apart; RL-174 B.3 / RL-149 §2.3 cap applies')
    if len(blocks)>1: stop('one qualification block per t0-date; cap is not a slip remedy (RL-174 B.3)')
except (OSError,ValueError,KeyError,TypeError,OverflowError) as e: stop('unreadable/contradictory receipt or plan '+str(e))
print('DAY OK',day,'already',count,'plus',n,'blocks',sorted(blocks),'RL-174 B.3: three dates/one block each; <=24/two blocks/10h cap applies, never a slip remedy',seen)
PY
}
queue_gate() {
  filled "$QUEUE_COMMIT" || { echo 'WAIT: lead records queue commit (RL-149 §2.8 line 3)'; return 1; }
  QUEUE_EXPIRES_EPOCH="$("$PY" -I -B - "$AUTH_REPO" "$QUEUE_COMMIT" "$QUEUE_PATH" "$QUEUE_SHA" "$SPAN" "$LEGS" "$(date +%s)" <<'PY'
import hashlib, json, re, subprocess, sys
repo, commit, path, sha, span, legs, now=sys.argv[1:]; now=int(now)
def git(*a): return subprocess.check_output(['git','-C',repo,*a],stderr=subprocess.DEVNULL)
try:
    assert re.fullmatch('[0-9a-f]{40}',commit)
    assert subprocess.run(['git','-C',repo,'merge-base','--is-ancestor',commit,'origin/audit/2026-11-10-fable'],capture_output=True).returncode==0
    raw=git('cat-file','blob',commit+':'+path); assert hashlib.sha256(raw).hexdigest()==sha
    q=json.loads(raw); from datetime import datetime
    expiry=datetime.fromisoformat(q['expires_at']).timestamp()
    assert expiry.is_integer()
    committed=int(git('show','-s','--format=%ct',commit))
    assert committed <= now < expiry <= committed+7*86400
    assert q['halt'] is None
    entries=[s for s in q['spans'] if s['span_id']==span]; assert len(entries)==1 and entries[0]['legs']==legs.split(',')
except (OSError,ValueError,KeyError,AssertionError,subprocess.CalledProcessError): sys.exit('STOP: queue commit/hash/roster/seven-day expiry (RL-149 §2.8 line 3)')
print(int(expiry))
PY
)" || return 1
  echo "QUEUE COMMITTED $QUEUE_COMMIT finite expiry $QUEUE_EXPIRES_EPOCH"
}
debt_gate() {
  filled "${LINE9_RECORD:-}" || { echo 'WAIT: typed desk/Q1 debt record (RL-165 §6; RL-172 (c); RL-173 E Q1)'; return 1; }
  "$PY" -I -B - "$LINE9_RECORD" "$SPAN" "$PRED_SPAN" <<'PY'
import json, sys
try:
    r=json.load(open(sys.argv[1])); order=r['machine_order']; ids=[s['span_id'] for s in order]
    assert r['next_span']==sys.argv[2] and len(ids)>=2 and len(set(ids))==len(ids) and ids[-1]==sys.argv[3]
    for s in order: assert s['runner_kind'] in ('cadence-legs-v1','cadence-legs-v1.1')
    for s in order[:-1]:
        assert isinstance(s['desk_final_record'],str) and s['desk_final_record'].strip() and '<LEAD ' not in s['desk_final_record']
        if s['runner_kind']=='cadence-legs-v1.1':
            assert isinstance(s['q1_complete_record'],str) and s['q1_complete_record'].strip() and '<LEAD ' not in s['q1_complete_record']
    # RL-174 E.5: retain the named dev-05 debt even if a supplied census omits it.
    if sys.argv[2] in ('qual-01-s01','qual-01-s02'):
        required='dev-05-'+sys.argv[2].rsplit('-',1)[1]
        rows=[s for s in order if s['span_id']==required]
        assert len(rows)==1 and rows[0]['runner_kind']=='cadence-legs-v1.1'
        for key in ('desk_final_record','q1_complete_record'):
            value=rows[0].get(key)
            assert isinstance(value,str) and value.strip() and '<LEAD ' not in value
    assert r['authenticated_roster_identity_checks']=='RL-172 (c)'
except (OSError,ValueError,KeyError,TypeError,AssertionError): sys.exit('WAIT: line 9 desk-final or typed Q1 record absent/contradictory; debt counts across blocks')
print('LINE9 PAID through',ids[-2],'; Q1 completion through same span (RL-173 E); next',sys.argv[2])
PY
}
admission_gate() {
  # Lines 5/6/8, sampled hand-read and veto: current lead records, never default yes.
  for key in STOPS_CLEAR VETO_CLEAR CHECKLIST_OK PILOT_PASSED SAMPLE_HAND_CLEAR COPY_KEY_SAFE OFFLOAD_CLEAR; do
    eval 'value=${'"$key"':-}'
    test "$value" = yes || { echo "WAIT: $key evidence absent (RL-149 §2.4/§2.8; RL-172 (c); RL-173 A)"; return 1; }
  done
  for key in LINE6_RECORD CHECKLIST_RECORD VETO_RECORD SAMPLE_HAND_RECORD; do
    eval 'value=${'"$key"':-}'
    filled "$value" || { echo "WAIT: $key pointer required"; return 1; }
  done
  if test "$SPAN" != qual-01-s01; then
    test "${QUAL01_SOAK_HAND_READ:-}" = SAME && filled "${QUAL01_SOAK_RECORD:-}" \
      || { echo 'WAIT: qual-01-s01 soak fields/reference schema compared with dev-05 before s02 (RL-172a F1)'; return 1; }
  fi
}
window_gate() {
  now=$(date +%s)
  test "$now" -ge "$WINDOW_START" && test "$now" -le "$WINDOW_END" \
    || { echo 'REFUSE: outside item t0-date or LIMIT; follow missed-date recovery (RL-172 (a)5)'; return 1; }
}
arm_bound_gate() {
  # Date/window end is inclusive to the printed second. Item and queue expiries are exclusive.
  ARM_BEFORE_EPOCH=$((WINDOW_END + 1))
  for expires in "$EXPIRES_EPOCH" "$QUEUE_EXPIRES_EPOCH"; do
    if test "$expires" -lt "$ARM_BEFORE_EPOCH"; then ARM_BEFORE_EPOCH=$expires; fi
  done
  if test "$FIRST_TO_SECOND_S" -gt 0; then
    second_before=$((DAY_END + 1))
    if test "$QUEUE_EXPIRES_EPOCH" -lt "$second_before"; then second_before=$QUEUE_EXPIRES_EPOCH; fi
    case "${S02_ISSUED_EPOCH:-}" in
      unissued) ;;
      ''|*[!0-9]*) echo 'WAIT: record the actual s02 issue epoch or unissued'; return 1;;
      *) second_expires=$((S02_ISSUED_EPOCH + 86400))
         if test "$second_expires" -lt "$second_before"; then second_before=$second_expires; fi;;
    esac
    pair_before=$((second_before - FIRST_TO_SECOND_S))
    if test "$pair_before" -lt "$ARM_BEFORE_EPOCH"; then ARM_BEFORE_EPOCH=$pair_before; fi
  fi
  test "$(date +%s)" -lt "$ARM_BEFORE_EPOCH" || {
    echo "REFUSE: effective t0 cutoff $ARM_BEFORE_EPOCH (date, item/queue expiry, dependent span)"
    return 1
  }
  echo "AUTHORIZED T0 $T0_DATE before $ARM_BEFORE_EPOCH"
}
all_gates() {
  expiry_gate && watch_gate && freeze2_gate && qual_pin_gate && host_event_gate && v4_gate \
    && admission_gate && queue_gate && debt_gate && pred_gate && close_gate && day_gate && window_gate && arm_bound_gate
}
# END TESTABLE GATES
