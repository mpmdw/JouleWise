TBD. **Laptop lead, drafted by Sol 6.1; ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm F2 instrument-characterization piece 1 only, span `f2-inst-03-p1`, kit `f2-inst-03.v1.1` (sha256 `286842217313e13ac5f8f25917b3325e3e512cd621b90b78b6201d331e9dcf25`), runner `cadence-legs-v1.1`, detached pin `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Roster L001,L002,L003: L001 2,000 tokens, L002 256 tokens, L003 19,458 tokens; own-shaped G0, q600, decode cap 256, Automatic. Fresh soak, then three legs; expected 7,377 s, worst case 11,250 s. These are instrument legs, outside every campaign count and look. Predecessor `f2-inst-02-p4` must have a clean close receipt or this item is VOID and never skipped. EARLIEST Sun 22 Nov 2026 00:00:00 PST (1795334400); LIMIT Sun 22 Nov 23:59:59 PST (1795420799), shortened by 24 h after issue. F2 is a filler: it cedes to all armable counted work and a READY v4 session; use the complete priority trigger below. Launch is the last action; exit immediately. Nothing else is authorized.**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-23T04:31:49-08:00
on_early_or_refused: WAIT if predecessor has not closed or a higher rung can arm; VOID if predecessor is not clean, the date window is missed, or 24 h has elapsed since issue. No retry after a launcher/runner refusal; report to the lead. Never skip a predecessor, reuse OUT, re-run a leg, or queue another piece on this item's authority
next_observable: after the fence is gone, Check below reports operational receipt/leg records, feeds, restore and copy; piece 1's hand-read is lead-owned
```

- **Admission and authority (RL-174 B.2; RL-169; RL-169a).** Data only; frozen pin and all 38 path hashes unchanged. The drafted queue a in this folder contains this piece only. The lead records its actual commit and SHA before staging. Require the independent executing re-check, dev-03's first span closed on this same pin with all restore lines passed, line 2 carried from the dev-03 item by frozen-path equality (RL-165 §5), every applicable checklist line, watcher line 7 and campaign line-9 debt. F2 neither adds to nor pays down line 9. Record the evidence for each `*_OK` value below; a yes without its evidence is not authority. STATUS.md lists unfilled prerequisites. Nothing is issued across a class A, L002 or L005 hand gate (RL-173 D.4).
- **Issued ahead (RL-173 D).** Own predecessor `f2-inst-02-p4`, own date and own `pick_arg`; expires 24 h after ISSUED_EPOCH, checked twice. At most three counted spans ahead plus standing F0. No F2 item grants standing authority or authority to issue another item. Pieces 2–4 are not issuable before the piece-1 hand gate and queue-b commit.
- **Exact ladder.** RL-174 B replaces the order with READY v4, counted work, F0, F2 inst-01 then inst-02 then inst-03, hp-02, DESIGN_QUEUE_LOW. hp-02 does not precede F2. The inherited HP_READY observation refers only to higher-priority counted hp-01, if any.  READY v4 session takes the next clean close from the lead's READY record (RL-172 (f); no reservation at a merely intended session t0). Preserve the applicable counted development order: dev-03 pilot/remainder and dev-04/dev-05 dated spans are never displaced. RL-174 B's current ladder is READY v4, counted work (including qualification), F0, F2 (inst-01, -02, -03), hp-02, then DESIGN_QUEUE_LOW. The historical hp-01/P work must also be closed or unavailable; no pending higher rung is displaced. F2 is eligible only when no counted item can arm within its worst case and ensuing close, hp-01 and P cannot arm, and F0 is ineligible under its own spacing, daily-cap or launch-window rule. `priority_gate` encodes that trigger and blocks unknown state, unresolved refusal, open F2 stop, or pending host-event disposition. Re-read all current issued/staged counted items and READY counted work awaiting staging twice; set NEXT_COUNTED_EPOCH to the earliest legal arm including the next day's spans. Do not omit a known item merely because staging is pending. Unknown gate readiness stops the arm. An explicit 0 requires a recorded complete empty census. This conservative check protects 13,010 s: 11,250 work + 560 launcher/runner reserve + 1,200 close; it also clears the 12,710 s fence. A new READY record before launch cedes immediately. Nothing aborts an already running span.
- **Day law.** F2 may run on any date, including a qualification date; it is outside development/day/cap counts (RL-172 (a); RL-174 B). This item's date is a bounded scheduling choice, not a new development date; a missed window needs a newly dated item from the lead. No shortening/re-cutting of the admitted four-piece layout is needed for the forecast gaps.
- **Bands verified at the pin:** 00:00:00–02:34:59 alternate `13:14-13:15`; 02:35:00–10:50:00 default `02:00-02:35`; 10:50:01–13:14:59 no launch; 13:15:00–22:18:10 default; 22:18:11–23:59:59 alternate. RL-171 retires RL-169a's 22:13:10/02:40 clock rules. The pin admits exactly 10:50:00; both arguments refuse one second later. `evidence/verify-f2-p01.txt` checks endpoints and adjacent seconds, including the alternate's 09:32:10/09:32:11 limit. All validate-kit, plan and launch commands name the same argument and explicit roster.
- **Close and copy.** 300 s after a campaign span close; **1,200 s after F2, F0 or any other close**, from the actual close with fence gone (RL-171 §6.1; RL-172 (d)). The latest close census reads only each receipt's recorded ended.epoch_s, selects its identity before rounding fractional epochs up, and stops on missing roots, unreadable/missing/invalid close stamps, equal latest epochs or no receipt. File mtime never selects a marker. Latest-close restore and process-group absence are proven. After a campaign close require that exact span's verified encrypted cloud offload `.ok` or Air `.air.ok` marker; after F0/F2/Part C/session/W1 the non-campaign Check covers the copy, with NONCAMPAIGN_COPY_OK=yes, NONCAMPAIGN_COPY_CLOSE_EPOCH equal to EFF_EPOCH, NONCAMPAIGN_COPY_RECEIPT equal to EFF_PATH and NONCAMPAIGN_COPY_RECORD pointing to the actual Check and verified copy. No F0 marker is manufactured; a failed/unverified offload holds every next arm, F0 included (RL-173 A). The writer guarantees plaintext manifest hash, ciphertext hash/size and provider confirmation, upload finished before soak; the key is safe off the MBP and originals retained. This item never manufactures a marker. For an out-of-census session supply OTHER_CLOSE_EPOCH and the same Check/copy proof with NONCAMPAIGN_COPY_RECEIPT=OTHER. A mere `.ok` existence is trusted only because the authorized writer writes it after verification, as in the dev-03 pilot.
- **Quiet and host event.** RL-174 C settles the host event: no restart/visit is required. Print the four host lines at each arm: spotlightknowledged/updater present or absent, corespotlightd present, indexing / off, Time Machine destination none. From freeze 2 through qual-03 close no hygiene setting changes; an unplanned restart is recorded and does not hold the arm. HOST_STATE_RECORDED means this record, not a new restart gate.  Quiet is agent/process census and rule 5, not the retired night clock. No MBP agent, SSH, analysis, build or test during a span. Same measurement_mode, Automatic, network time OFF, frequency word 0, no night/smoke job, monitor, High Power marker, lock holder or desk fence. RL-172 (h), amended by RL-173 and RL-174 C: the host runs as it is; no completed restart/service-stop is required. A pending/unresolved event still holds the arm; no password/physical step by an agent; the four host lines are printed; RL-174 C has disposed the planned host event. Each arm prints boot + 12 h + 48 s batch time, a print only.
- **Blinding.** RL-174 B.2: the frozen lm-inst-01 manifest lists all THREE kits by identity/hash before ANY F2 energy is opened, and prints per kit.  F2 measures only its own instrument streams. Neither this magistrate item nor its tests read campaign/v4 energy, power, meter samples, powermetrics, transcripts, slots or custody. F2's own energy is sealed until freeze 2; only the single analyst using frozen `lm-inst-01` may read it once. The operational Check reads only receipts, leg records and leg-summary projections. Recovery beyond the rails' 1 s tail is censored per RL-169a; no F2 number enters a fit, coefficient, threshold or score.
- **Stops.** Any F2 REFUSAL, INSTRUMENT_FAULT, CONTAMINATED_REDOS (three loaded legs) or LEG_OVERTIME (two above 1.5× budget) stops its queue; an open cadence-stop holds every queue. A G0 timeout alone, or one/two loaded legs, is recorded. No running span is aborted. Only the lead disposes a stop under RL-169a §4, with a new queue for unrun pieces; no member-bearing leg is repeated and unbundled legs of a stopped piece are dropped. Second stops go to the research lead. Restore unproven holds everything. A failed piece-1 hand-read leaves queue b uncommitted.

**Start and check** (on the MBP only after issue, by the magistrate; the builder never executes these blocks).

The lead stages `python3 -B ../stage_mbp_span.py --commit <LEAD FILLS committed draft source> --admission <LEAD FILLS administrative admission JSON> f2-inst-03-p1` in a clean close interval and supplies the arm-record observations used below. Stage and reuse one detached v1.1 worktree only; never stage the v1.1a variant. `QUEUE_FILE` is the staged queue path and `QUEUE_SHA` its committed hash. For piece 1 use queue-a's committed bytes; for later pieces use the lead's post-hand-read queue b. The watcher placeholders below are exactly the dev-03 pilot's. This item uses the hand-stamped watcher observation of RL-173 C.5, re-read at every arm; an API watcher would instead require C.4's completed run newer than the previous close.

```sh
set -eu
set -o pipefail
cd /Users/edr/code/jw-wt/cadence-f2-inst-03-p1
PIN=2d347f721552fe03bdd19f113e7bad7a7c24908e
test "$(git rev-parse HEAD)" = "$PIN" && test -z "$(git status --porcelain)" || exit 1
git symbolic-ref -q HEAD >/dev/null && exit 1
REPO="$PWD"
: "${PY:?existing pinned measurement-venv interpreter}"
: "${MAGISTRATE_PID:?this magistrate own process PID}"
KIT=/Users/edr/campaign-out/kits/f2-inst-03.v1.1-RL174B.json
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = 286842217313e13ac5f8f25917b3325e3e512cd621b90b78b6201d331e9dcf25 || exit 1
QUEUE_FILE=/Users/edr/campaign-out/queues/f2-inst-03-queue-a.json
QUEUE_SHA=b9d91855c4704772e7b75378d085e3c9032821cc538481b1b9b33727d07c604c
test "$(shasum -a 256 "$QUEUE_FILE" | cut -c1-64)" = "$QUEUE_SHA" || exit 1
PIECE=1; SPAN=f2-inst-03-p1; LEGS=L001,L002,L003; PRED_CAMP=f2-inst-02; PRED_SPAN=f2-inst-02-p4; PRED_KIT_SHA=cfd03677e3629b34a8bcd794a623ee3eaae1033408492eb1d1ddb3229273ed65; PRED_ROSTER=L010,L011,L012
pick_arg() {
  n=$1
  if [ "$n" -ge 1795334400 ] && [ "$n" -le 1795343699 ]; then echo 13:14-13:15
  elif [ "$n" -ge 1795343700 ] && [ "$n" -le 1795373400 ]; then echo 02:00-02:35
  elif [ "$n" -ge 1795382100 ] && [ "$n" -le 1795414690 ]; then echo 02:00-02:35
  elif [ "$n" -ge 1795414691 ] && [ "$n" -le 1795420799 ]; then echo 13:14-13:15
  else echo NONE; fi
}
# Included verbatim in each item by build_items.py; no production command runs here.
# BEGIN TESTABLE GATES
ISSUED_EPOCH=<LEAD FILLS: the issue time as an epoch, from `date +%s` at issue>
WATCH_UNTIL_EPOCH=<LEAD FILLS: line 7's watcher observation stamp + 86,400 s, as an epoch>
EXPIRES_EPOCH=$((ISSUED_EPOCH + 86400))
expiry_gate() {
  now=$(date +%s)
  test "$ISSUED_EPOCH" -le "$now" && test "$now" -lt "$EXPIRES_EPOCH" && test "$now" -lt 1795420800 \
    || { echo 'VOID: future issue, 24 h expiry, or kit expiry (RL-173 D.5; RL-169a)'; return 1; }
}
watch_gate() {
  now=$(date +%s)
  test "$now" -lt "$WATCH_UNTIL_EPOCH" && test "$WATCH_UNTIL_EPOCH" -le $((now + 86400)) \
    || { echo 'STOP: watcher observation missing, stale or in the future (RL-173 C.5)'; return 1; }
}
pred_gate() {
  pred_root=/Users/edr/f2-out
  if test "$PRED_CAMP" = f2-inst-01; then pred_root=/Users/edr/campaign-out; fi
  PRED_LINE="$("$PY" -I -B - "$pred_root" "$PRED_CAMP" "$PRED_SPAN" "$PRED_ROSTER" "$PRED_KIT_SHA" <<'PY'
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
  CENSUS="$("$PY" -I -B - /Users/edr/campaign-out /Users/edr/code/jw-wt /Users/edr/f2-out <<'PY'
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
  test "${COPY_TYPED_OK:-}" = yes && test -n "${COPY_EVIDENCE:-}" || { echo "STOP: typed verified copy evidence required (RL-174 A.12)"; return 1; }
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
rl174_gate() {
  for proof in "INST01_HAND_READ:${INST01_HAND_READ:-}" "KIT_DELTA_OK:${KIT_DELTA_OK:-}" "HOST_STATE_RECORDED:${HOST_STATE_RECORDED:-}"; do
    case "$proof" in INST01_HAND_READ:PASS|KIT_DELTA_OK:yes|HOST_STATE_RECORDED:yes) ;; *) echo "WAIT: RL-174 B/C prerequisite $proof"; return 1;; esac
  done
  case "${KIT_ISSUED_EPOCH:-}" in ''|*[!0-9]*) echo 'WAIT: lead kit issue time required'; return 1;; esac
  now=$(date +%s)
  test "$now" -ge "$KIT_ISSUED_EPOCH" && test "$now" -lt $((KIT_ISSUED_EPOCH + 604800)) || { echo 'VOID: seven days after kit issue'; return 1; }
}
all_gates() {
  rl174_gate && expiry_gate && watch_gate && admission_gate && pred_gate && close_gate && priority_gate && window_gate
}
# END TESTABLE GATES

ARG="$(pick_arg "$(date +%s)")"; export ARG
all_gates || exit 1
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"
test ! -e "$CUSTODY/desk_fence.json" || exit 1
test ! -e /Users/Shared/JouleWise/host-power/high-power.marker || exit 1
test ! -L /Users/Shared/JouleWise/host-power/high-power.marker || exit 1
sudo -n -l /bin/kill >/dev/null || exit 1
sudo -n systemsetup -getusingnetworktime  # Off
pmset -g | grep -i powermode             # 0; frequency word 0, AC power checked by checklist
MODE_VERIFY_RC=0
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify || MODE_VERIFY_RC=$?
echo "measurement_mode verify rc $MODE_VERIFY_RC"
# Only own-process-tree agent FAIL lines may be present, as dev-03's arm record; any other FAIL stops.
# Inspect the exit status and lines; CHECKLIST_OK=yes is set only with every applicable line proven.
export TMPDIR="$(mktemp -d /tmp/jw-f2-preflight.XXXXXX)" JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=.:tests
for module in tests.cadence.test_kit_v11 tests.cadence.test_span_reference tests.cadence.test_legs_runner tests.cadence.test_kit tests.cadence.test_stops_desk tests.cadence.test_runner_guards tests.cadence.test_launch_cadence_span tests.align.test_r1_smoke_launcher; do
  python3.13 -B -m unittest "$module" || exit 1
done
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG" || exit 1
# validate-queue during staging uses the kit at its committed relative path in a temporary kits-root.
# Here compare the staged committed queue hash/roster: never run `next` or `checklist` to grant authority.
"$PY" -B scripts/cadence_legs_runner.py plan --kit "$KIT" --legs L001,L002,L003 --batch-window "$ARG" || exit 1
# expected_s 7377, worst_case_s 11250, blackout_clear true, batch_windows [ARG]. Record complete output.
BOOT="$(sysctl -n kern.boottime | sed -E 's/^\{ sec = ([0-9]+),.*$/\1/')"
case "$BOOT" in ''|*[!0-9]*) echo 'batch print: boot unreadable';; *) NEXT_BATCH=$((BOOT+43248)); while [ "$NEXT_BATCH" -le "$(date +%s)" ]; do NEXT_BATCH=$((NEXT_BATCH+86400)); done; echo "next OS batch epoch $NEXT_BATCH";; esac
OUT=/Users/edr/f2-out/f2-inst-03/cq-${SPAN}-a1-$(date -u '+%Y%m%dT%H%M%SZ')
test ! -e "$OUT" || exit 1
```

**Run.** Re-read the issued/staged counted items, NEXT_COUNTED_EPOCH, v4 READY record, hp-01/P/F0 eligibility, all stop/restore records, copy marker and the watcher observation now. Update the observations; do not reuse a cached eligibility answer. A prior date's expired item is never counted as armable. Run once, then exit immediately.

```sh
all_gates || exit 1
test ! -e "$CUSTODY/desk_fence.json" || exit 1
# The pinned launcher rechecks host/checklist state, condition-13 and its process census under its lock.
DEADLINE="$("$PY" -I -B -c 'import time; print(time.time()+12710)')"
"$PY" -B scripts/launch_cadence_span.py launch \
  --repo "$REPO" --python-bin "$PY" --kit "$KIT" --legs L001,L002,L003 --batch-window "$ARG" \
  --output "$OUT" --disk-path "$REPO" --custody-root "$CUSTODY" \
  --magistrate-pid "$MAGISTRATE_PID" --deadline "$DEADLINE" \
  --exit-wait-seconds 180 --start-wait-seconds 30
echo "$OUT"
```

**Check.** Only on the next activation, after the shared fence is gone. Read no stream, member output, feed file or custody content. This operational print is not the analyst read and never prints measured power/energy. All queue stops are judged by the pinned desk's operational projection and the lead; nothing is automatically re-armed.

Maintenance is print-only (RL-174 B.5 and D.1). Query the span's interval for the same processes as qualification. Earlier checks whose predicates lacked the three cloud jobs recorded them as unobserved.

```sh
(
  START_UTC="$(basename "$OUT" | sed -E 's/.*-([0-9]{8}T[0-9]{6}Z)$/\1/')"
  START_LOCAL="$("$PY" -B -c 'import sys,datetime as d; t=d.datetime.strptime(sys.argv[1],"%Y%m%dT%H%M%SZ").replace(tzinfo=d.timezone.utc); print(t.astimezone().strftime("%Y-%m-%d %H:%M:%S"))' "$START_UTC")" || exit 1
  END_LOCAL="$(date -r "$(stat -f %m "$OUT/runner_receipt.json")" '+%Y-%m-%d %H:%M:%S')" || exit 1
  echo "maintenance window $START_LOCAL .. $END_LOCAL"
  sudo -n /usr/bin/log show --style compact --start "$START_LOCAL" --end "$END_LOCAL" \
    --predicate 'process IN {"dasd","XProtect","XprotectService","XProtectPluginService","mds","mds_stores","mdworker","mdworker_shared","backupd","softwareupdated","mobileassetd","bird","cloudd","fileproviderd"}' \
    > "$OUT/maintenance-log.txt" 2>"$OUT/maintenance-log.err" || exit 1
  wc -l < "$OUT/maintenance-log.txt" || exit 1
  # per 10-minute bucket and process: "HH:M0 process count"
  awk '{ if ($2 ~ /^[0-9][0-9]:[0-9][0-9]/) { b=substr($2,1,4) "0"; for (i=3;i<=NF;i++) if ($i ~ /\[[0-9]+:/) { split($i,a,"["); p=a[1]; break } ; c[b" "p]++ } } END { for (k in c) print k, c[k] }' "$OUT/maintenance-log.txt" | sort
) || echo 'maintenance log unavailable; record as unobserved'
```

```sh
"$PY" -I -B - "$OUT" "$LEGS" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1]); roster = sys.argv[2].split(',')
r = json.loads((root/'runner_receipt.json').read_text())
assert r['roster'] == roster and r['runner_kind'] == 'cadence-legs-v1.1'
assert r['kit']['sha256'] == '286842217313e13ac5f8f25917b3325e3e512cd621b90b78b6201d331e9dcf25' and r['kit']['frozen_commit'] == '2d347f721552fe03bdd19f113e7bad7a7c24908e'
assert r['kit']['campaign_id'] == 'f2-inst-03' and r.get('mock') in (False,None)
print({k:r.get(k) for k in ('rc','error','legs_planned','legs_finished','span_result','ended','batch_windows')})
print('steps', [(x['name'],x['rc']) for x in r['steps']])
print('feed stops', {k:v.get('stop') for k,v in r['feeds'].items()})
print('meter operational', r.get('meter'))
assert r.get('feeds') and all(f.get('stop',{}).get('proven_stopped') is True for f in r['feeds'].values())
assert any(s['name']=='restore' for s in r['steps'])
assert all(s['rc']==0 for s in r['steps'] if s['name']=='restore' or s['name'].startswith(('stop-','close-')))
for leg in roster:
    rec = json.loads((root/'legs'/leg/'leg_record.json').read_text())
    result = rec.get('result') or {}
    keys = ('leg_status','g0_outcome','g0_wait_s','quiet_spans_ns','decode_tokens','decode_cap_reached','prefill_tokens')
    print(leg, {k:result.get(k) for k in keys}, 'attempt walls', [a.get('wall_s') for a in rec.get('attempts',[])])
    summary = json.loads((root/'desk-bundle'/'legs'/leg/'leg_summary.json').read_text())
    print(leg, {k:summary.get(k) for k in ('wall_s','budget_s','contaminated_redos','admitted','g0_outcome')})
print('RECEIPT OK' if r['rc']==0 and r['legs_finished']==3 else 'NOT CLEAN: report to lead; no retry')
PY
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify
sudo -n systemsetup -getusingnetworktime   # Off
pmset -g | grep -i powermode               # 0; report frequency word 0 and process-group absence
```

Report receipt/desk lines, named stops, actual close/fence-gone epochs, every restore line, feed-stop proof, copy/offload status, watcher observation, and the host-mode readback. Never hash/open stream files as an agent. The lead's deterministic desk uses `2d347f721552fe03bdd19f113e7bad7a7c24908e` and the leg-summary projection only. The lead records Check and the verified copy before any next soak. No commit from OUT.

**After (lead).** Kit expiry is seven days after the lead's kit issue, independently of the 24-hour item expiry. Queue expiry Nov23 00:00 is a conservative upper bound; never issue before Nov16. Queue b is still uncommitted until THIS kit's first-piece PASS. The unchanged kit title/inclusion prose names inst-01/512/old expiry; this item and RL-174 B supersede those historical literals only.  Piece 1's hand-read uses only leg_record and runner_receipt: every leg complete or g0_unreleased, at least two complete; each complete leg has a quiet span ≥600 s and reached 256; meter present/clean, all feeds stopped and restore passed. Record each wall against 2,700 s and the 256-token leg's realized prefill. Keep and flag any short decode; a short 256 leg goes to the research lead before queue b. Only a PASS permits the lead to commit queue b and issue pieces 2–4. This item cannot cross that gate. Later pieces run once in order under their own issued items; after piece 4 F2 leaves the ladder. An issue after 24 h or a missed date needs a new item. No early energy read; `lm-inst-01` and its cold pass gate only the later analyst read, not these runs.
