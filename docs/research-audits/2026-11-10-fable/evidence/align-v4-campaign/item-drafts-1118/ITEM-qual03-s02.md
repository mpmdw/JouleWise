TBD. **Laptop lead, drafted by Sol 6.1; ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm the SECOND span of qualification block `qual-03`, span `qual-03-s02`, legs L007,L008,L009,L010,L011,L012, kit `cl-qual-03.v1.1` (sha256 `85dfa025a84c7bdbcb79ecd0fa87bd52d1ffc7624e40fa94c5877646abd03bf9`), runner kind `cadence-legs-v1.1`, frozen pin `0576ed76d3a74d20ce3c6b6b96711e360775a25f` checked out detached in a fresh staged worktree. A fresh soak, then six conditionless 27B legs, Automatic, band q0; L007 captures the span reference, the five other legs consume it. Short leg: L010 cap 3,151; all other caps 4,096. Expected 12262 s; work worst case 24750 s; launcher deadline reserve includes the additional 1,950 s soak retry and 560 s cleanup reserves. EARLIEST 2026-11-21 00:00:00 PST (epoch 1795248000), LIMIT 2026-11-21 23:59:59 PST (epoch 1795334399), shortened by 24 h after issue. HOLD_FOR_FIT_FREEZE until freeze 2 is committed and verified. Predecessor `qual-03-s01` must close clean or this item is VOID and is never skipped. The pinned runner takes no batch-window argument for qualification. The arm remains subject to RL-175 C.4. Launch is your LAST action; exit at once. Nothing else is authorized.**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-22T08:49:19-08:00
on_early_or_refused: WAIT on an unfilled prerequisite or predecessor not closed. VOID on a dirty predecessor or 24 h expiry; REFUSE outside the date window, on development/qualification date overlap or date cap. Effective READY v4 session: CEDE, do not arm (RL-175 A.2). Any failed native checklist or launcher refusal: nothing launches, report to lead. Never retry, skip a predecessor, extend a queue, reuse OUT, or re-run a leg; follow the missed-date recovery below
next_observable: after fence disappearance, Check below reports operational receipt, all six leg summaries, Q1 reference print, maintenance overlaps, restore/process-group proof and close epoch; lead records desk-final and typed Q1 completion before span k+2 arms
```

- **Issued ahead (RL-173 D).** At most three counted spans ahead plus standing F0. Predecessor `qual-03-s01` in `cl-qual-03`, roster L001,L002,L003,L004,L005,L006; `pred_gate` reads only its receipt and leg-summary projection. Absent receipt = WAIT; any unclean close = VOID, never skipped. The qualification predecessor chain is fixed; no automatic skip or override. This item has its own t0-date and no window argument; `expiry_gate` enforces 24 h and `watch_gate` re-reads the hand-stamped watcher observation at each arm (RL-173 C.5). Nothing is issued across a class A, L002 or L005 hand gate. Not issuable before qual-01-s01's soak hand-read record (RL-172a F1; conservative issue ordering).
- **Why (RL-149 §2.3; RL-155 §5.3; RL-165 §8.1; RL-167 Part B; RL-172 (a),(b)).** Qualification tests the committed fit on held-out dates. This law's 6 + 6 cut keeps each true type-L pair adjacent in one span and gives each span four A legs and one L pair. First leg own-shaped/capture, all five others span-shaped/consume; no T or M. The M slots are ordinary A legs at 19,458. No class A smoke: class B, a mock span, plan and diff check (RL-165 §8.1; RL-172a F1). At the first qualification arm cite RL-172a F1. Its soak's operational fields and reference schema must be hand-compared with dev-05 before qual-01-s02; a difference goes to the research lead. The retry fires on slope or load refusal, once (RL-172a F2); the desk/look read `soak_attempts`, a retried soak forces the sampled hand table, and refusal kind prints "kind not recorded" until a later pin (RL-173 E).
- **Config provenance (RL-167 Part B Q1; Mythos #794 F5).** Record both runtime-config hashes: development `bf2cb2e6503c46373b52b10f32642d95a66a6636a3d7caaad0ce8b2b756781df`, qualification `272aecb8bc0d9e33defd7f686b129ea236b925fdfbf68137697120dd63232f46`. Only the unused `d_n_chunk_status` label differs; `lm-qual-01` prints both and must not require equality for inclusion.
- **Freeze and pin.** `freeze2_gate` implements RL-165 §8.1, RL-172 (i) row 9 and RL-173 E. Full commit/hash/path unfilled = WAIT/HOLD_FOR_FIT_FREEZE. The commit must be an ancestor of freshly fetched audit or main and contain that exact coefficient hash. No forecast or fit-code hash substitutes for it. `qual_pin_gate`: line 1 cold seat ADMIT **per kit**, including RL-167 Part B Q2's same-code capture/five-consumer confirmation; line 2 suite red set at the frozen bytes equals the merged W1-line commit `c3f4bacd8`, test for test, no added red (RL-165 §8.1). Record pointers remain lead fills. Later W1 merges do not move the qualification pin. The frozen child validates the authorized date and exclusive cutoff against its recorded start before span work. HOLD until both admission lines are recorded against the exact successor kit bytes. RL-175 C.4 also requires the separate predicted-batch check at each arm.
- **Day law (RL-174 B.3, RL-175 C.3).** Span dates: qual-01-s01=2026-11-19, qual-01-s02=2026-11-19, qual-02-s01=2026-11-20, qual-02-s02=2026-11-20, qual-03-s01=2026-11-21, qual-03-s02=2026-11-21. Each date holds spans from only one qualification block, with no development leg. Each whole block holds two L pairs. Fewer than three pair-days prints `not_evaluable` for the ±0.10 word (RL-166b §4). Sat 14–Wed 18 Nov are reserved development dates, and `day_gate` also checks moved development spans. Each span's recorded t0-date assigns all six legs even if it closes after midnight. The one-block rule is stricter than the RL-149 §2.3 cap of two blocks and 24 legs with block starts at least 10 h apart. The queues expire **2026-11-23T00:00:00-08:00**. A new expiry requires a new lead-committed queue.
- **Dependent spans (WS 4 and QUEUE-SPEC D8).** The printed s01 LIMIT is 16:32:00 PST at the latest. Reserve 24,750 s for s01 work, 1,950 s for a possible soak retry plus 560 s of cleanup reserve, then 300 s for the campaign close interval before s02. The latest s01 t0 moves earlier if s02's date, item or queue expires before this pair can fit. Use the same bounds in standing-F0 rule 7 while both spans remain outstanding, including planned s02 when its hand gate prevents early issue. Provide the actual s02 issue epoch when issued, or record `unissued` when its hand gate still holds. The plan then assumes a fresh s02 item in time for the planned t0. The actual Check, verified copy, hand-read and remaining gates still govern.
- **Missed-date recovery (RL-175 C.3).** **Untouched block:** move both spans together to an unused legal date. **Partially run block:** retain s01's recorded date and receipts, then schedule only the missing s02 once on the next unused legal date with the same legs and seeds and a fresh soak. Move later untouched blocks whole. Every qualification receipt's recorded date must match its own span entry. A span with an existing t0 cannot arm again. The lead commits the revised finite queue and issues fresh items for the remaining spans.
- **Predicted OS batch (RL-175 C.4).** Start and Run each read the current boot time and use this span's pinned expected close. A planned span that reaches the predicted batch holds until batch start plus 27 minutes. The boot read also refreshes the prediction after a restart. Record the boot, batch, soak and close epochs and the resulting t0 bound from the gate.
- **Host state (RL-174 C).** Freeze 2 proceeds on the host as it is; no visit, hygiene action or restart is a gate. Each arm states four lines: `spotlightknowledged` and updater present/absent (stopped Sun 15 Nov 15:32); `corespotlightd` present/on demand; indexing of `/` off; Time Machine destination none (`backupd` resident). The lead supplies the readback record and a hygiene-state identity, excluding boot time. Nobody changes a hygiene setting from freeze 2 through qual-03 close. An unplanned restart is an event: record it and refresh the four lines at the next arm; it holds nothing. `INCLUSION_RECORD` is filled by **RL-174 B.5**: the six rules stay unchanged and maintenance overlaps are print-only. `lm-qual-01` prints flagged and unflagged errors side by side, with counts by job, description only and no word. The lead appends the by-job count through dev-05 when its desk is final; that count gates nothing. The maintenance print carries the Sun15 15:32 service-stop date.
- **Gates 5–9 (RL-149 §2.8; RL-165 §6; RL-172 (c),(f); RL-173 A–E; RL-174 E.5).** Line 6: no named stop, halt or veto open, lead record of dispositions. Line 7: watcher observed within 24 h, re-read at both gates; this draft uses C.5. For an Actions watcher, RL-174 A.13 requires a scheduled successful completed run on this repository's `main`, started after the previous close; a manual run never serves an arm. Line 9: actual machine order across blocks/queues, desk-final and **typed Q1 completion** through span k−2. In particular qual-01-s01 needs dev-05-s01's desk-final and Q1 records; qual-01-s02 needs dev-05-s02's, span for span. `debt_gate` requires those named rows as well as the full machine-order debt record. No "first span of kit" exception. Automatic desk must satisfy all four RL-172 (c) identity/authentication rules, sampled hand table clear, disagreement holds next arm. Lead/magistrate supply observations and pointers; no default yes.
- **Close and copy (RL-171 §6.1; RL-172 (d); RL-173 A,B).** At least 300 s after a campaign close; 1,200 s after F0/F2/Part C/session/W1, using the **latest close of anything**, its Check and process-group absence, fence gone. Census stops on missing roots, unreadable or ambiguous stamps; `OTHER_CLOSE_EPOCH` covers sessions outside it. `PRIOR_CLOSE_EPOCH` cannot precede predecessor close. After a campaign close, copy marker `.ok` or `.air.ok` for that plan is required; after any other close, its Check/copy proof must bind the exact latest receipt path and close epoch; verified synchronous encrypted cloud offload counts permanently, upload finished before soak, plaintext/ciphertext hashes and size/provider confirmation recorded, key held off MBP, originals retained until verified copy. An unverified offload holds every arm including F0. A sync daemon is interim only; maintenance print includes bird/cloudd/fileproviderd. No marker is written by this item.
- **Quiet, native checks and stops.** Same measurement_mode (RL-149 §2.2/§2.4), Automatic, network time Off, frequency word 0, AC, meter ready, disk ≥40 GiB, no night/smoke agent, High Power marker, night.lock holder, stray monitor, root powermetrics or other agent. Preserve the dev-05 own-process-tree-only measurement_mode exception. Process/load census and rule 5 enforce quiet (RL-171 §2); no builds, analysis, SSH or tests while anything is armed. Named stops stop the next arm, never a running span. REFUSAL/restore/disk/watcher: lead clears; INSTRUMENT_FAULT: research lead; 3 contaminated redos: lead once, then research lead; two legs >1.5× own budget: lead; frozen-path/host-state changes: research lead (RL-149 §2.4). A reference missing at capture is refusal; no consumer proceeds on an invented reference. A v4 READY record preempts when effective under RL-175 A.2. A READY record cannot take effect between the halves of a block.

**Start and check** (magistrate on the MBP only **after issue**; this builder never executes these blocks).

The lead stages a clean detached worktree at the frozen pin and the exact kit and queue bytes committed in this folder. The kit and queue hashes bind the staged copies. Lead fills their authenticated commit and issue-time records. Stage outside every registration/custody root; never run tests on the measurement host while a queue is live (RL-172 (i)4). Host-independent checks are in this folder's evidence.

```sh
set -eu
set -o pipefail
cd /Users/edr/code/jw-wt/cadence-qual-03-s02
REPO="$PWD"
AUTH_REPO=/Users/edr/code/JouleWise
PIN=0576ed76d3a74d20ce3c6b6b96711e360775a25f
test "$(git rev-parse HEAD)" = "$PIN" && test -z "$(git status --porcelain)" || exit 1
git symbolic-ref -q HEAD >/dev/null && exit 1
: "${PY:?pinned measurement-venv interpreter}"
: "${MAGISTRATE_PID:?own magistrate process PID}"
KIT=/Users/edr/campaign-out/kits/cl-qual-03.v1.1-0576ed76d.json
KIT_SHA=85dfa025a84c7bdbcb79ecd0fa87bd52d1ffc7624e40fa94c5877646abd03bf9
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = "$KIT_SHA" || exit 1
QUEUE_PATH=docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-1118/queues/cl-qual-03.queue.json
QUEUE_SHA=699849c697733e8b6415f8c7551239517048dbcc27c9a9498eb17a8cd9ad49e4
QUEUE_FILE=/Users/edr/campaign-out/queues/cl-qual-03.queue.json
test "$(shasum -a 256 "$QUEUE_FILE" | cut -c1-64)" = "$QUEUE_SHA" || exit 1
SPAN=qual-03-s02; CAMP=cl-qual-03; LEGS=L007,L008,L009,L010,L011,L012
PRED_SPAN=qual-03-s01; PRED_CAMP=cl-qual-03; PRED_ROSTER=L001,L002,L003,L004,L005,L006
PRED_KIT_SHA=85dfa025a84c7bdbcb79ecd0fa87bd52d1ffc7624e40fa94c5877646abd03bf9; PRED_PIN=0576ed76d3a74d20ce3c6b6b96711e360775a25f
T0_DATE=2026-11-21; WINDOW_START=1795248000; WINDOW_END=1795334399
DAY_END=1795334399; FIRST_TO_SECOND_S=0
EXPECTED_SPAN_S=12262
QUAL_DATES=qual-01-s01=2026-11-19,qual-01-s02=2026-11-19,qual-02-s01=2026-11-20,qual-02-s02=2026-11-20,qual-03-s01=2026-11-21,qual-03-s02=2026-11-21
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
  "$PY" -I -B - /Users/edr/campaign-out "$(date +%s)" "$T0_DATE" "$QUAL_DATES" "$SPAN" "$CAMP" "$LEGS" <<'PY'
import datetime as dt, json, math, os, re, sys
from pathlib import Path
from zoneinfo import ZoneInfo
root, now, wanted, dates, current, camp, legs = sys.argv[1:]
def stop(s): sys.exit('REFUSE: day law ' + s)
TZ=ZoneInfo('America/Los_Angeles'); day=dt.datetime.fromtimestamp(int(now),TZ).date().isoformat()
spans=[f'qual-{n:02d}-s{i:02d}' for n in (1,2,3) for i in (1,2)]
def block(span): return span.rsplit('-',1)[0]
def roster_for(span):
    start=1 if span.endswith('-s01') else 7
    return [f'L{i:03d}' for i in range(start,start+6)]
try:
    entries=[entry.split('=') for entry in dates.split(',')]
    planned=dict(entries)
    if len(entries)!=len(spans) or set(planned)!=set(spans): stop('six unique span dates required (RL-175 C.3)')
    days_by_span=[planned[span] for span in spans]
    blocks_by_day={}
    for span, date in zip(spans,days_by_span):
        if dt.date.fromisoformat(date).isoformat()!=date: stop('t0-date must use YYYY-MM-DD')
        if '2026-11-14'<=date<='2026-11-18': stop('planned qualification date is a development date')
        if blocks_by_day.setdefault(date,block(span))!=block(span): stop('one qualification block per t0-date (RL-175 C.3)')
    if days_by_span!=sorted(days_by_span): stop('t0 dates must follow span order')
    if day!=wanted or planned[current]!=day: stop('outside this item t0-date; lead re-dates (RL-172 (a)5)')
    if camp!='cl-'+block(current) or legs.split(',')!=roster_for(current): stop('item span, block or roster mismatch')
    if not os.path.isdir(root): stop('receipt root missing')
    recorded=set()
    count=0
    for family in sorted(Path(root).iterdir()):
        if not family.is_dir() or not re.fullmatch(r'cl-(dev|qual)-[a-zA-Z0-9-]+',family.name): continue
        for out in sorted(family.iterdir()):
            if not out.is_dir() or not out.name.startswith('cq-'): continue
            p=out/'runner_receipt.json'
            if not p.is_file(): stop('pending output without receipt '+str(out))
            r=json.loads(p.read_text()); t=r['started']['epoch_s']; roster=r['roster']
            if isinstance(t,bool) or not isinstance(t,(int,float)) or not math.isfinite(t) or t<=0: stop('bad t0 '+str(p))
            if (not isinstance(roster,list) or not roster
                    or not all(isinstance(x,str) and re.fullmatch('L[0-9]{3}',x) for x in roster)
                    or len(set(roster))!=len(roster)): stop('bad roster '+str(p))
            actual=dt.datetime.fromtimestamp(t,TZ).date().isoformat()
            if family.name.startswith('cl-dev-'):
                if actual in blocks_by_day: stop('development receipt on qualification date '+actual+' '+str(p))
            else:
                match=re.fullmatch(r'cq-(qual-0[1-3]-s0[12])-a[1-9][0-9]*-\d{8}T\d{6}Z',out.name)
                if not match or family.name!='cl-'+block(match[1]): stop('unrecognized qualification span output '+str(out))
                span=match[1]
                if roster!=roster_for(span): stop('bad qualification span roster '+str(p))
                if planned[span]!=actual: stop('existing qualification receipt disagrees with its span plan '+str(p))
                if span in recorded: stop('multiple receipts for qualification span '+span)
                recorded.add(span)
                if actual==day:
                    count+=len(roster)
    if current in recorded: stop('qualification span already has a recorded t0 '+current)
    for first, second in zip(spans[::2],spans[1::2]):
        if planned[first]!=planned[second] and first not in recorded:
            stop('untouched qualification block must move whole '+block(first))
    n=len(legs.split(','))
    if count+n>24: stop('more than 24 qualification legs (RL-149 §2.3)')
except (OSError,ValueError,KeyError,TypeError,OverflowError) as e: stop('unreadable/contradictory receipt or plan '+str(e))
print('DAY OK',day,current,'already',count,'plus',n,'one block on this date (RL-175 C.3); RL-149 §2.3 cap applies')
PY
}
queue_gate() {
  filled "$QUEUE_COMMIT" || { echo 'WAIT: lead records queue commit (RL-149 §2.8 line 3)'; return 1; }
  QUEUE_EXPIRES_EPOCH="$("$PY" -I -B - "$AUTH_REPO" "$QUEUE_COMMIT" "$QUEUE_PATH" "$QUEUE_SHA" "$SPAN" "$LEGS" "$T0_DATE" "$KIT_SHA" "$(date +%s)" <<'PY'
import hashlib, json, re, subprocess, sys
repo, commit, path, sha, span, legs, day, kit_sha, now=sys.argv[1:]; now=int(now)
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
    entries=[s for s in q['spans'] if s['span_id']==span]; assert len(entries)==1
    entry=entries[0]
    assert entry['legs']==legs.split(',') and entry['not_before']==day and entry['kit']['sha256']==kit_sha and entry['attempt']==1
except (OSError,ValueError,KeyError,TypeError,AssertionError,subprocess.CalledProcessError): sys.exit('STOP: queue commit/hash/roster/span date/kit/attempt/seven-day expiry (RL-149 §2.8 line 3; RL-175 C.3)')
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
batch_gate() {
  # Fresh boot read at both Start and Run. Carry the next hold boundary to the child.
  BATCH_BOOT="$(sysctl -n kern.boottime)" || { echo 'STOP: boot time unavailable (RL-175 C.4)'; return 1; }
  ARM_BEFORE_EPOCH="$("$PY" -I -B - "$BATCH_BOOT" "$(date +%s)" "$EXPECTED_SPAN_S" "$ARM_BEFORE_EPOCH" <<'PY'
import re, sys
raw, now, expected, cutoff = sys.argv[1:]
boot = re.fullmatch(r'\{\s*sec\s*=\s*([0-9]+),\s*usec\s*=\s*[0-9]+\s*\}.*',raw)
if not boot or not all(v.isascii() and v.isdecimal() for v in (now,expected,cutoff)):
    sys.exit('STOP: unreadable boot time or qualification plan (RL-175 C.4)')
boot, now, expected, cutoff = int(boot[1]), int(now), int(expected), int(cutoff)
soak_s, cooldown_s, day_s = 1950, 27*60, 86400
if not 0<boot<=now or not soak_s<=expected<day_s-cooldown_s or now>=cutoff:
    sys.exit('STOP: invalid boot time, span duration or t0 cutoff (RL-175 C.4)')
# The existing prediction is anchored to boot, with the observed 48 s offset.
first = boot + 43248
occurrences = max(0,(now-first)//day_s + 1)
upcoming = first + occurrences*day_s
previous = upcoming-day_s if occurrences else None
expected_close = now+expected
held = previous if previous is not None and now<previous+cooldown_s else None
if held is None and upcoming<=expected_close:
    held = upcoming
if held is not None:
    sys.exit(f'WAIT: RL-175 C.4 predicted OS batch {held}; arm at or after {held+cooldown_s}')
before = min(cutoff,upcoming-expected)
print(f'BATCH OK RL-175 C.4 boot {boot}; next OS batch {upcoming}; soak end {now+soak_s}; '
      f'expected close {expected_close}; authorized t0 before {before}',file=sys.stderr)
print(before)
PY
)" || return 1
}
all_gates() {
  expiry_gate && watch_gate && freeze2_gate && qual_pin_gate && host_event_gate && v4_gate \
    && admission_gate && queue_gate && debt_gate && pred_gate && close_gate && day_gate && window_gate \
    && arm_bound_gate && batch_gate
}
# END TESTABLE GATES

# Fresh refs for the hash/ancestry gate; repeat in Run. No network remains after launch.
git -C "$AUTH_REPO" fetch -q origin audit/2026-11-10-fable main || exit 1
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"
native_checks() {
  unset CHECKLIST_OK
  test ! -e "$CUSTODY/desk_fence.json" || return 1
  { test ! -e /Users/Shared/JouleWise/host-power/high-power.marker && test ! -L /Users/Shared/JouleWise/host-power/high-power.marker; } || return 1
  lsof -- /Users/Shared/JouleWise/host-power/night.lock 2>/dev/null && return 1 || true
  sudo -n -l /bin/kill >/dev/null || return 1
  sudo -n systemsetup -getusingnetworktime || return 1   # Off; any other readback STOPS
  pmset -g | grep -i powermode || return 1               # 0; frequency word 0 as item 308/251
  pgrep -fl 'b6_r12|r12' || echo 'no r12'
  pgrep -fl 'claude|codex|mcp-server|mcp_server|modelcontextprotocol' | grep -v "^$MAGISTRATE_PID " || echo 'no other agent'
  pgrep -fl 'km003c_monitor.py|hazard_monitor.py' || echo 'no stray monitor'
  pgrep -u root -fl powermetrics || echo 'no root powermetrics'
  launchctl list | grep -E 'com\.joulewise\.(night|align-r0)' || echo 'no night/smoke agent'
  MODE_RC=0
  zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify || MODE_RC=$?
  echo "measurement_mode verify rc $MODE_RC"
  # Inspect every FAIL: only own-process-tree agent lines allowed. Any other FAIL STOPS; WARN is recorded.
  "$PY" -B scripts/launch_align_r0.py preflight --disk-path "$REPO" || return 1   # AC true, disk >=40 GiB; checklist includes meter
  "$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" || return 1
  test -n "${CHECKLIST_OBSERVATIONS:-}" || return 1
  "$PY" -B scripts/cadence_queue.py checklist --kit "$KIT" --kit-sha256 "$KIT_SHA" --observations "$CHECKLIST_OBSERVATIONS" || return 1
  CHECKLIST_OK=yes
}
native_checks || exit 1
all_gates || exit 1
"$PY" -B scripts/cadence_legs_runner.py plan --kit "$KIT" --legs "$LEGS" || exit 1
# Plan must print expected_s 12262, worst_case_s 24750, batch_windows [], runner_kind cadence-legs-v1.1.
# Record HEAD, kit frozen.commit, all identities and every native checklist line, meter presence and veto read.
OUT=/Users/edr/campaign-out/cl-qual-03/cq-${SPAN}-a1-$(date -u '+%Y%m%dT%H%M%SZ')
test ! -e "$OUT" || exit 1
case "$OUT" in */restricted/*|*/night-*|"$REPO"/*|*/configs/campaigns/align_v4*) exit 1;; esac
```

Lead/magistrate supplies the current observations listed in `evidence/record-shapes.md`. `CHECKLIST_OK=yes` is set only **after** every native read above and the kit's complete checklist passes; each call clears any supplied yes before running the checks. Disk, meter, process census, no halt/veto and all restore lines are mandatory.

**Run (your last action).** Re-read stops, veto, watcher, typed desk/Q1 debt, host-state identity, v4 READY record and current boot time. Verify the current kit/queue hashes again and fetch refs before the last gate. Pass the date and tightened t0 cutoff from the fresh gates to the child. The pinned runner checks its native checklist and per-leg process census. The LaunchAgent holds the **shared desk fence** until close. The launch omits `--batch-window`.

```sh
git -C "$AUTH_REPO" fetch -q origin audit/2026-11-10-fable main || exit 1
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = "$KIT_SHA" || exit 1
test "$(shasum -a 256 "$QUEUE_FILE" | cut -c1-64)" = "$QUEUE_SHA" || exit 1
native_checks || exit 1
all_gates || exit 1
test ! -e "$CUSTODY/desk_fence.json" || exit 1
# Frozen plan launch minimum includes the one-soak retry; extra 900 s is start/preflight slack.
DEADLINE="$("$PY" -I -B -c 'import time; print(time.time()+28160)')"
"$PY" -B scripts/launch_cadence_span.py launch \
  --repo "$REPO" --python-bin "$PY" --kit "$KIT" --legs "$LEGS" \
  --output "$OUT" --disk-path "$REPO" --custody-root "$CUSTODY" \
  --magistrate-pid "$MAGISTRATE_PID" --deadline "$DEADLINE" \
  --authorized-t0-date "$T0_DATE" --t0-before "$ARM_BEFORE_EPOCH" \
  --exit-wait-seconds 180 --start-wait-seconds 30 || exit 1
echo "$OUT"
```

Require exit 0, `"next": "exit the magistrate session now"`, a claimed desk fence whose pid differs from MAGISTRATE_PID, and launch plan `batch_windows == []`. Record every gate print, all record pointers, date-rule/cap reading, predecessor/host close epochs and kind, GAP, issue/expiry/watch stamps, freeze-2 commit/path/hash, host-state identity, worktree HEAD, kit/queue commit/hash, six legs and their caps, OUT, DEADLINE, native readbacks and plan. Then exit at once. Any refusal is reported; nothing is re-armed on this authority.

**Check (next activation, after the fence is gone).** Maintenance first, print only under RL-174 B.5: one system-log query over this span, save beside journals, count by 10-minute bucket and process, associate leg intervals from summaries if available. No additional exclusion. Keep `bird`, `cloudd` and `fileproviderd` in the print permanently (RL-174 D.1).

```sh
echo 'maintenance context: spotlightknowledged and updater stopped 2026-11-15 15:32 PST (RL-174 C)'
START_UTC="$(basename "$OUT" | sed -E 's/.*-([0-9]{8}T[0-9]{6}Z)$/\1/')"
START_LOCAL="$("$PY" -B -c 'import sys,datetime as d; t=d.datetime.strptime(sys.argv[1],"%Y%m%dT%H%M%SZ").replace(tzinfo=d.timezone.utc); print(t.astimezone().strftime("%Y-%m-%d %H:%M:%S"))' "$START_UTC")"
END_LOCAL="$(date -r "$(stat -f %m "$OUT/runner_receipt.json")" '+%Y-%m-%d %H:%M:%S')"
echo "maintenance window $START_LOCAL .. $END_LOCAL"
sudo -n /usr/bin/log show --style compact --start "$START_LOCAL" --end "$END_LOCAL" \
  --predicate 'process IN {"dasd","XProtect","XprotectService","XProtectPluginService","mds","mds_stores","mdworker","mdworker_shared","backupd","softwareupdated","mobileassetd","bird","cloudd","fileproviderd"}' \
  > "$OUT/maintenance-log.txt" 2>"$OUT/maintenance-log.err"; echo "log show rc $?"
wc -l < "$OUT/maintenance-log.txt"
# per 10-minute bucket and process: "HH:M0 process count"
awk '{ if ($2 ~ /^[0-9][0-9]:[0-9][0-9]/) { b=substr($2,1,4) "0"; for (i=3;i<=NF;i++) if ($i ~ /\[[0-9]+:/) { split($i,a,"["); p=a[1]; break } ; c[b" "p]++ } } END { for (k in c) print k, c[k] }' "$OUT/maintenance-log.txt" | sort

```

The Check proper reads only operational receipts, leg records and projected summaries; never open stream/energy/power/meter samples, transcript, member output or custody content as an agent.

```sh
"$PY" -I -B - "$OUT" "$LEGS" <<'PY'
import json, sys
from pathlib import Path
root=Path(sys.argv[1]); roster=sys.argv[2].split(',')
r=json.loads((root/'runner_receipt.json').read_text())
assert r['runner_kind']=='cadence-legs-v1.1' and r['roster']==roster
assert r['kit']['sha256']=='85dfa025a84c7bdbcb79ecd0fa87bd52d1ffc7624e40fa94c5877646abd03bf9' and r['kit']['frozen_commit']=='0576ed76d3a74d20ce3c6b6b96711e360775a25f' and r['kit']['campaign_id']=='cl-qual-03'
assert r['batch_windows']==[] and r.get('mock') in (None,False)
print({k:r.get(k) for k in ('rc','error','legs_planned','legs_finished','span_result','ended','soak_attempts')})
print('steps',[(s['name'],s['rc']) for s in r['steps']])
assert r.get('feeds') and all(f.get('stop',{}).get('proven_stopped') is True for f in r['feeds'].values())
assert any(s['name']=='restore' for s in r['steps'])
assert all(s['rc']==0 for s in r['steps'] if s['name']=='restore' or s['name'].startswith(('stop-','close-')))
print('feed-stop proofs',{k:f.get('stop') for k,f in r['feeds'].items()})
print('meter operational',{k:(r.get('meter') or {}).get(k) for k in ('present','proven_stopped','bad_polls','usb_errors')})
for leg in roster:
    s=json.loads((root/'desk-bundle'/'legs'/leg/'leg_summary.json').read_text())
    print(leg,{k:s.get(k) for k in ('admitted','g0_role','g0_outcome','g0_s','span_reference','wall_s','budget_s','contaminated_redos')})
    rec=json.loads((root/'legs'/leg/'leg_record.json').read_text()); result=rec.get('result') or {}
    print('cap',leg,(rec.get('spec') or {}).get('decode_tokens'),result.get('decode_cap'),result.get('decode_tokens'))
print('RECEIPT OK' if r['rc']==0 and r['legs_finished']==6 else 'NOT CLEAN: report to lead; no retry')
PY
# RL-150 R1 / RL-158 Q1: reference and release values only; gates nothing before the k+2 completion debt.
"$PY" -I -B - "$OUT" "$LEGS" <<'PY'
import json, statistics, sys
from pathlib import Path
root = Path(sys.argv[1]); roster = sys.argv[2].split(",")
KEYS = ("TV0h", "TV1h", "Tf08")
def rows(path):
    out = []
    for line in path.read_text().splitlines():
        d = json.loads(line)
        if d.get("module") == "temperature" and d.get("kind") in ("reading", "align_thermal_gate"):
            out.append(d)
    return out
def reading(d):
    return d["started"]["monotonic_ns"], (d["values"].get("sensors") or {})
soak = json.loads((root / "soak" / "soak_reference.json").read_text())
sj = [reading(d) for d in rows(root / "soak" / "idle_soak" / "sensors" / "align_thermal.jsonl") if d["kind"] == "reading"]
end = sj[-1][0]
tail = [s for t, s in sj if t > end - 1200 * 10**9]
tf08 = [s["Tf08"] for s in tail if isinstance(s.get("Tf08"), (int, float))]
print("soak_reference", {k: soak["sensors_c"].get(k) for k in ("TV0h", "TV1h")},
      "Tf08_last1200s_mean", statistics.fmean(tf08) if tf08 else None)
receipt_legs = {l["leg_id"]: l for l in json.loads((root / "runner_receipt.json").read_text()).get("legs", [])}
for leg in roster:
    rec = json.loads((root / "legs" / leg / "leg_record.json").read_text())
    res = rec.get("result") or {}
    line = {k: res.get(k) for k in ("g0_shape", "g0_role", "g0_outcome", "g0_released", "g0_wait_s",
                                    "g0_reference_source", "g0_reference_record_sha256", "prefill_tokens",
                                    "decode_tokens", "leg_status")}
    line["span_reference"] = (receipt_legs.get(leg) or {}).get("span_reference")
    bname = res.get("bundle")
    if not bname:
        line["no_bundle"] = True; print(leg, json.dumps(line, sort_keys=True)); continue
    out = root / "legs" / leg / "runtime" / bname / "outputs"
    j = rows(out / "align_thermal.jsonl")
    reads = [reading(d) for d in j if d["kind"] == "reading"]
    refp = out / "align_window_reference.json"
    if refp.is_file():
        ref = json.loads(refp.read_text()); lo, hi = ref["span_ns"]
        ref_tf08 = [s["Tf08"] for t, s in reads if lo <= t <= hi and isinstance(s.get("Tf08"), (int, float))]
        line["own_reference"] = {"status": ref["status"], "TV0h": ref["fast_c"], "TV1h": ref["slow_c"],
                                 "Tf08_median": statistics.median(ref_tf08) if ref_tf08 else None}
    else:
        line["own_reference"] = None     # a consumer reads the first leg's capture
    g0 = next((d["values"]["gate"] for d in j if d["kind"] == "align_thermal_gate"
               and d["values"].get("gate", {}).get("kind") == "G0"), None)
    at = next((s for t, s in reads if g0 and t == g0.get("exit_sample_ns")), {})
    line["g0"] = None if g0 is None else {"outcome": g0["outcome"], "duration_s": g0["duration_s"],
                                          "row_reference": g0.get("reference"), "row_release": g0.get("release"),
                                          "release": {k: at.get(k) for k in KEYS}}
    print(leg, json.dumps(line, sort_keys=True))
PY
test ! -e "$CUSTODY/desk_fence.json"
launchctl list | grep -c 'com.joulewise.align-r0' || true
pmset -g | grep -i powermode
sudo -n systemsetup -getusingnetworktime
# Record frequency word 0; every restore line and leg-child process group proven absent.
test ! -e /Users/Shared/JouleWise/host-power/high-power.marker
pgrep -fl 'km003c_monitor.py|hazard_monitor.py' || echo 'no stray monitor'
pgrep -u root -fl powermetrics || echo 'no root powermetrics'
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify
```

Report SPAN/LEGS, six caps (short leg L010 cap 3,151), receipt/restore and feed-stop lines, named stops, admitted count and exclusions under the six fixed rules, each consumer's release or timeout against L007, whether the reference came from a redo/excluded leg, maintenance overlaps, retry count (`soak_refusals`: kind not recorded), Q1 print, close epoch/fence-gone time, verified copy/offload marker and all native readbacks. Do not print power or energy. No commit from OUT. The magistrate reports; it never decides.

**After (the lead, at the desk; not the magistrate).** Use this kit and the frozen pin `0576ed76d3a74d20ce3c6b6b96711e360775a25f` for deterministic desk, off-host or controller-only during a clean close interval (RL-173 B). Check exact roster/attempt/reference/kit/plan identities and authenticated nonempty table (RL-172 (c)). Record desk FINAL and the separate typed Q1 completion in actual machine order before k+2; hand-read first kit/G0-shape group and every redo/exclusion/schema-change span (RL-173 E). First qualification close: compare soak operational fields/reference schema to dev-05 and record SAME before qual-01-s02 (RL-172a F1); difference goes to research lead. Mark retried soaks for sampled hand-read; no missing refusal-kind field is invented. Update ledger `qual-03` RUNNING/COLLECTED/DESK_FINAL. All 36 qualification legs collected; the lead owns look readiness. Qualification energy stays sealed for its separately frozen look; no change to fit coefficients or score is authorized.
