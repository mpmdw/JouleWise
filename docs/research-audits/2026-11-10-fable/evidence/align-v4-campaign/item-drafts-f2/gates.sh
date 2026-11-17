# Included verbatim in each item by build_items.py; no production command runs here.
# BEGIN TESTABLE GATES
ISSUED_EPOCH=<LEAD FILLS: the issue time as an epoch, from `date +%s` at issue>
WATCH_UNTIL_EPOCH=<LEAD FILLS: line 7's watcher observation stamp + 86,400 s, as an epoch>
EXPIRES_EPOCH=$((ISSUED_EPOCH + 86400))
expiry_gate() {
  now=$(date +%s)
  test "$ISSUED_EPOCH" -le "$now" && test "$now" -lt "$EXPIRES_EPOCH" && test "$now" -lt 1795325340 \
    || { echo 'VOID: future issue, 24 h expiry, or kit expiry (RL-173 D.5; RL-169a)'; return 1; }
}
watch_gate() {
  now=$(date +%s)
  test "$now" -lt "$WATCH_UNTIL_EPOCH" && test "$WATCH_UNTIL_EPOCH" -le $((now + 86400)) \
    || { echo 'STOP: watcher observation missing, stale or in the future (RL-173 C.5)'; return 1; }
}
pred_gate() {
  PRED_LINE="$("$PY" -I -B - /Users/edr/campaign-out "$PRED_CAMP" "$PRED_SPAN" "$PRED_ROSTER" "$PRED_KIT_SHA" <<'PY'
import json, math, os, re, sys
root, camp, span, roster, kit_sha = sys.argv[1:]; roster = roster.split(',')
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
            or k.get('frozen_commit') != '2d347f721552fe03bdd19f113e7bad7a7c24908e'): bad.append('kit/runner identity')
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
        && test "${NONCAMPAIGN_COPY_RECEIPT:-}" = "$EFF_PATH" && test -n "${NONCAMPAIGN_COPY_RECORD:-}" \
        || { echo 'WAIT: exact latest non-campaign Check/copy proof missing (RL-171 §6.1; RL-173 A)'; exit 1; }
      case "$NONCAMPAIGN_COPY_RECORD" in *'<LEAD '*) echo 'WAIT: unfilled non-campaign Check/copy record'; exit 1;; esac
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
priority_gate() {
  # Freshly read the lead's current items/READY records at EACH invocation.
  # NEXT_COUNTED_EPOCH covers ALL issued/staged counted items and READY counted
  # work awaiting staging, including next-date dev-03/04/05. Do not omit a known
  # item just because staging is pending. Unknown gate readiness stops; 0 requires
  # an explicit complete no-armable-span record.
  for pair in "SESSION_READY:${SESSION_READY:-}" "HP_READY:${HP_READY:-}" "P_READY:${P_READY:-}"; do
    case "$pair" in *:no) ;; *:yes) echo "CEDE: higher-priority $pair"; return 1;; *) echo "STOP: unknown $pair"; return 1;; esac
  done
  test "${F0_ELIGIBLE:-}" = no || { echo 'CEDE: eligible or unknown F0'; return 1; }
  case "${F0_REASON:-}" in spacing|daily_cap|launch_window) ;; *) echo 'STOP: F0 ineligibility needs a lawful reason'; return 1;; esac
  test "${OUTSTANDING_REFUSAL:-}" = none && test "${F2_STOPS_CLEAR:-}" = yes \
    || { echo 'STOP: unresolved refusal or F2 cadence-stop'; return 1; }
  test "${RESTART_PENDING:-}" = no || { echo 'STOP: host-event disposition/readback pending'; return 1; }
  case "${NEXT_COUNTED_EPOCH:-}" in ''|*[!0-9]*) echo 'STOP: counted armable-time census required'; return 1;; esac
  test -n "${PRIORITY_EVIDENCE:-}" || { echo 'STOP: missing priority evidence record'; return 1; }
  now=$(date +%s)
  # Work worst case 11,250 + runner/launcher reserves 560 + close interval 1,200.
  # This also clears the pin's fence end (t0 + 12,710).
  if test "$NEXT_COUNTED_EPOCH" != 0 && test "$NEXT_COUNTED_EPOCH" -lt $((now + 13010)); then
    echo 'CEDE: a counted span can arm within F2 worst case and close interval'; return 1
  fi
  echo "F2 TRIGGER: no higher-priority arm; F0 $F0_REASON; $PRIORITY_EVIDENCE"
}
admission_gate() {
  for proof in "F2_RECHECK_OK:${F2_RECHECK_OK:-}" "DEV03_SMOKE_CLOSED:${DEV03_SMOKE_CLOSED:-}" "LINE2_OK:${LINE2_OK:-}" "LINE9_OK:${LINE9_OK:-}" "CHECKLIST_OK:${CHECKLIST_OK:-}" "QUEUE_AUTHORIZED:${QUEUE_AUTHORIZED:-}" "COPY_KEY_SAFE:${COPY_KEY_SAFE:-}"; do
    case "$proof" in *:yes) ;; *) echo "STOP: admission/checklist evidence absent: $proof"; return 1;; esac
  done
  if test "$PIECE" -gt 1; then
    test "${F2_HAND_READ:-}" = PASS && test "${QUEUE_B_COMMITTED:-}" = yes \
      || { echo 'WAIT: piece-1 hand-read and lead-committed queue b required'; return 1; }
  fi
}
window_gate() {
  now=$(date +%s)
  picked="$(pick_arg "$now")"
  test "$picked" != NONE && test "$picked" = "$ARG" \
    || { echo 'STOP: outside date/launch band or argument changed; re-plan'; return 1; }
}
all_gates() {
  expiry_gate && watch_gate && admission_gate && pred_gate && close_gate && priority_gate && window_gate
}
# END TESTABLE GATES
