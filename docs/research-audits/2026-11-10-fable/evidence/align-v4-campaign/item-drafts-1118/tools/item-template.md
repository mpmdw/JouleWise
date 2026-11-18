TBD. **Laptop lead, drafted by Sol 6.2; ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm the @@ORDINAL@@ span of qualification block `@@BLOCK@@`, span `@@SPAN@@`, legs @@LEGS@@, kit `@@CAMP@@.v1.1` (sha256 `@@KIT_SHA@@`), runner kind `cadence-legs-v1.1`, frozen pin `@@PIN@@` checked out detached in a fresh staged worktree. A fresh soak, then six conditionless 27B legs, Automatic, band q0; @@FIRST@@ captures the span reference, the five other legs consume it. Short leg: @@SHORT@@; all other caps 4,096. Expected @@EXPECTED@@ s; work worst case @@WORST@@ s; launcher deadline reserve includes the additional 1,950 s soak retry and 560 s cleanup reserves. EARLIEST @@DATE@@ 00:00:00 PST (epoch @@START@@), LIMIT @@DATE@@ @@LIMIT_HMS@@ PST (epoch @@END@@). HOLD_FOR_FIT_FREEZE until freeze 2 is committed and verified. Predecessor `@@PRED@@` must close clean or this item is VOID and is never skipped. The pinned runner takes no batch-window argument for qualification. The arm remains subject to RL-175 C.4. Launch is your LAST action; exit at once. Nothing else is authorized.**

```pointer
owner: magistrate
wait: none
deadline: @@POINTER_DEADLINE@@
on_early_or_refused: WAIT on an unfilled prerequisite or predecessor not closed. VOID on a dirty predecessor; REFUSE outside the date window or on development/qualification date overlap. Effective READY v4 session: CEDE, do not arm (RL-175 A.2). Report a failed native checklist or launcher refusal to the lead and follow the close Check recovery below if an attempt was published. Never retry, skip a predecessor, extend a queue, reuse OUT, or re-run a leg; follow the missed-date recovery below
next_observable: after fence disappearance, Check below reports operational receipt, all six leg summaries, Q1 reference print, maintenance overlaps, restore/process-group proof and close epoch; lead records desk-final and typed Q1 completion before a look reads this span
```

- **Counted predecessor.** Predecessor `@@PRED@@` in `@@PRED_CAMP@@`, roster @@PRED_LEGS@@; `pred_gate` reads only its receipt and leg-summary projection. Absent receipt = WAIT; any unclean close = VOID, never skipped. @@PRED_NOTE@@@@HAND_NOTE@@
- **Why (RL-149 §2.3; RL-155 §5.3; RL-165 §8.1; RL-167 Part B; RL-172 (a),(b)).** Qualification tests the committed fit on held-out dates. This law's 6 + 6 cut keeps each true type-L pair adjacent in one span and gives each span four A legs and one L pair. First leg own-shaped/capture, all five others span-shaped/consume; no T or M. The M slots are ordinary A legs at 19,458. No class A smoke: class B, a mock span, plan and diff check (RL-165 §8.1; RL-172a F1). At the first qualification arm cite RL-172a F1. The RL-172a F1 soak comparison with dev-05 may come from the first same-pin filler hand-read (RL-181 §4(a)); a difference goes to the research lead. The retry fires on slope or load refusal, once (RL-172a F2); the desk/look read `soak_attempts`, a retried soak forces the sampled hand table, and refusal kind prints "kind not recorded" until a later pin (RL-173 E).
- **Config provenance (RL-167 Part B Q1; Mythos #794 F5).** Record both runtime-config hashes: development `bf2cb2e6503c46373b52b10f32642d95a66a6636a3d7caaad0ce8b2b756781df`, qualification `272aecb8bc0d9e33defd7f686b129ea236b925fdfbf68137697120dd63232f46`. Only the unused `d_n_chunk_status` label differs; `lm-qual-01` prints both and must not require equality for inclusion.
- **Freeze and pin.** `freeze2_gate` implements RL-165 §8.1, RL-172 (i) row 9 and RL-173 E. Full commit/hash/path unfilled = WAIT/HOLD_FOR_FIT_FREEZE. The commit must be an ancestor of freshly fetched audit or main and contain that exact coefficient hash. No forecast or fit-code hash substitutes for it. `qual_pin_gate`: line 1 cold seat ADMIT **per kit**, including RL-167 Part B Q2's same-code capture/five-consumer confirmation; line 2 suite red set at the frozen bytes equals the merged W1-line commit `c3f4bacd8`, test for test, no added red (RL-165 §8.1). Record pointers remain lead fills. Later W1 merges do not move the qualification pin. The frozen child validates the authorized date and exclusive cutoff against its recorded start before span work. HOLD until both admission lines are recorded against the exact successor kit bytes. RL-175 C.4 also requires the separate predicted-batch check at each arm.
- **Day law (RL-174 B.3, RL-175 C.3).** Span dates: @@DATES@@. Each date holds spans from only one qualification block, with no development leg. Each whole block holds two L pairs. Sat 14–Wed 18 Nov are reserved development dates, and `day_gate` also checks moved development spans. Each span's recorded t0-date assigns all six legs even if it closes after midnight. The queues expire **@@QUEUE_EXPIRY@@**. A new expiry requires a new lead-committed queue.
- **Dependent spans (WS 4 and QUEUE-SPEC D8).** The printed s01 LIMIT is 16:32:00 PST at the latest. Reserve 24,750 s for s01 work, 1,950 s for a possible soak retry and 560 s for cleanup. The latest s01 t0 moves earlier if the queue expires before the pair can fit. RL-179 F-2 allows s02 once the close is proven and the other gates pass.
- **Missed-date recovery (RL-175 C.3).** **Untouched block:** move both spans together to an unused legal date. **Partially run block:** retain s01's recorded date and receipts, then schedule only the missing s02 once on the next unused legal date with the same legs and seeds and a fresh soak. Move later untouched blocks whole. Every qualification receipt's recorded date must match its own span entry. A span with an existing t0 cannot arm again. The lead commits the revised finite queue and issues fresh items for the remaining spans.
- **Predicted OS batch (RL-175 C.4).** Start and Run each read the current boot time and use this span's pinned expected close. A planned span that reaches the predicted batch, including during soak, holds until batch start plus 27 minutes. The boot read also refreshes the prediction after a restart. Record the boot, batch, soak and close epochs and the resulting t0 bound from the gate.
- **Host state (RL-174 C).** Freeze 2 proceeds on the host as it is; no visit, hygiene action or restart is a gate. Each arm states four lines: `spotlightknowledged` and updater present/absent (stopped Sun 15 Nov 15:32); `corespotlightd` present/on demand; indexing of `/` off; Time Machine destination none (`backupd` resident). The lead supplies the readback record and a hygiene-state identity, excluding boot time. Nobody changes a hygiene setting from freeze 2 through qual-03 close. An unplanned restart is an event: record it and refresh the four lines at the next arm; it holds nothing. `INCLUSION_RECORD` is filled by **RL-174 B.5**: the six rules stay unchanged and maintenance overlaps are print-only. `lm-qual-01` prints flagged and unflagged errors side by side, with counts by job, description only and no word. The lead appends the by-job count through dev-05 when its desk is final; that count gates nothing. The maintenance print carries the Sun15 15:32 service-stop date.
- **Named stops and hand checks (RL-179 F-3 and F-6).** Line 6 requires the lead’s dispositions for applicable stops, halts and vetoes. Automatic desk must satisfy the RL-172 (c) identity and authentication rules. An automatic desk failure, a failed consumer gate or a sampled hand-table disagreement holds the affected kit. Lead and magistrate supply the applicable observations and pointers.
- **Close proven (RL-179 F-2).** Supply the complete launch/start-plan ledger for the host, including attempted spans without close records. Seed the ledger in observed launch order with a unique positive integer `sequence` on every row, starting at 1. The gate selects the highest sequence. For the latest pre-qualification attempt (dev-05-s02 or a filler on an older pin), the lead supplies that attempt’s identity-bound close Check with matching `span_id`, exact close stamp and all-true `restore_readbacks`; the old runner receipt lacks `span_id`. [Record shapes](evidence/record-shapes.md) give the Check fields and ledger binding. Verify stopped feeds, process absence and fence disappearance. The copy check binds to the selected proof. The successor can arm once the proof and other gates pass.
- **Quiet, native checks and stops.** Same measurement_mode (RL-149 §2.2/§2.4), Automatic, network time Off, frequency word 0, AC, meter ready, disk ≥40 GiB, no night/smoke agent, High Power marker, night.lock holder, stray monitor, root powermetrics or other agent. Preserve the dev-05 own-process-tree-only measurement_mode exception. Process/load census and rule 5 enforce quiet (RL-171 §2); no builds, analysis, SSH or tests while anything is armed. Named stops stop the next arm, never a running span. REFUSAL/restore/disk: lead clears; INSTRUMENT_FAULT: research lead; 3 contaminated redos: lead once, then research lead; two legs >1.5× own budget: lead; frozen-path/host-state changes: research lead (RL-149 §2.4). A reference missing at capture is refusal; no consumer proceeds on an invented reference. A v4 READY record preempts when effective under RL-175 A.2. A READY record cannot take effect between the halves of a block.

**Start and check** (magistrate on the MBP only **after issue**; this builder never executes these blocks).

The lead stages a clean detached worktree at the frozen pin and the exact kit and queue bytes committed in this folder. The kit and queue hashes bind the staged copies. Lead fills their authenticated commit and issue-time records. Stage outside every registration/custody root; never run tests on the measurement host while a queue is live (RL-172 (i)4). Host-independent checks are in this folder's evidence.

```sh
set -eu
set -o pipefail
cd /Users/edr/code/jw-wt/cadence-@@SPAN@@
REPO="$PWD"
AUTH_REPO=/Users/edr/code/JouleWise
PIN=@@PIN@@
test "$(git rev-parse HEAD)" = "$PIN" && test -z "$(git status --porcelain)" || exit 1
git symbolic-ref -q HEAD >/dev/null && exit 1
: "${PY:?pinned measurement-venv interpreter}"
: "${MAGISTRATE_PID:?own magistrate process PID}"
KIT=/Users/edr/campaign-out/kits/@@CAMP@@.v1.1-@@PIN_SHORT@@.json
KIT_SHA=@@KIT_SHA@@
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = "$KIT_SHA" || exit 1
QUEUE_PATH=@@QUEUE_PATH@@
QUEUE_SHA=@@QUEUE_SHA@@
QUEUE_FILE=/Users/edr/campaign-out/queues/@@CAMP@@.queue.json
test "$(shasum -a 256 "$QUEUE_FILE" | cut -c1-64)" = "$QUEUE_SHA" || exit 1
@@CONFIG@@
@@GATES@@
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
# Plan must print expected_s @@EXPECTED@@, worst_case_s @@WORST@@, batch_windows [], runner_kind cadence-legs-v1.1.
# Record HEAD, kit frozen.commit, all identities and every native checklist line, meter presence and veto read.
OUT=/Users/edr/campaign-out/@@CAMP@@/cq-${SPAN}-a1-$(date -u '+%Y%m%dT%H%M%SZ')
test ! -e "$OUT" || exit 1
case "$OUT" in */restricted/*|*/night-*|"$REPO"/*|*/configs/campaigns/align_v4*) exit 1;; esac
```

Lead/magistrate supplies the current observations listed in `evidence/record-shapes.md`. `CHECKLIST_OK=yes` is set only **after** every native read above and the kit's complete checklist passes; each call clears any supplied yes before running the checks. Disk, meter, process census, no halt/veto and all restore lines are mandatory.

**Run (your last action).** Re-read stops, veto, host-state identity, v4 READY record and current boot time. Verify the current kit/queue hashes again and fetch refs before the last gate. Pass the authorized date, pinned clock anchor, whole-second window, issue, queue and batch bounds, and the exact close bound in epoch nanoseconds. The child applies both lower bounds to its wall sample and projected start interval. With the shared desk fence locked, the launcher rechecks the same proof and publishes the new attempt before bootstrap.

```sh
git -C "$AUTH_REPO" fetch -q origin audit/2026-11-10-fable main || exit 1
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = "$KIT_SHA" || exit 1
test "$(shasum -a 256 "$QUEUE_FILE" | cut -c1-64)" = "$QUEUE_SHA" || exit 1
native_checks || exit 1
all_gates || exit 1
test ! -e "$CUSTODY/desk_fence.json" || exit 1
# Frozen plan launch minimum includes the one-soak retry; extra 900 s is start/preflight slack.
DEADLINE="$("$PY" -I -B -c 'import time; print(time.time()+@@DEADLINE_SECONDS@@)')"
"$PY" -B scripts/launch_cadence_span.py launch \
  --repo "$REPO" --python-bin "$PY" --kit "$KIT" --legs "$LEGS" \
  --output "$OUT" --disk-path "$REPO" --custody-root "$CUSTODY" \
  --magistrate-pid "$MAGISTRATE_PID" --deadline "$DEADLINE" \
  --span-id "$SPAN" --attempt-ledger "$ATTEMPT_LEDGER" --previous-close-receipt "$EFF_PATH" \
  --authorized-t0-date "$T0_DATE" --t0-not-before "$ARM_NOT_BEFORE_EPOCH" \
  --t0-not-before-ns "$EFF_CLOSE_NS" \
  --t0-before "$ARM_BEFORE_EPOCH" --t0-anchor "$ARM_T0_ANCHOR" \
  --exit-wait-seconds 180 --start-wait-seconds 30 || exit 1
echo "$OUT"
```

Require exit 0, `"next": "exit the magistrate session now"`, a claimed desk fence whose pid differs from MAGISTRATE_PID, and launch plan `batch_windows == []`. Record every gate print, all record pointers, date-rule reading, close proof and epochs, issue and queue expiry stamps, freeze-2 commit/path/hash, host-state identity, worktree HEAD, kit/queue commit/hash, six legs and their caps, OUT, DEADLINE, native readbacks and plan. Then exit at once. Report any refusal and await fresh authority before re-arming.

**Check (next activation, after the fence is gone).** If the child refused its t0 authority at rc 3, the attempt was published but there is no runner receipt. Keep the attempt and its sequence. The lead verifies the refusal, fence disappearance, restore readbacks, stopped feeds and process absence, then writes that attempt’s identity-bound close Check with the exact close epoch. Under the shared desk fence lock, bind that row’s `close_receipt` to the Check and supply the matching close and copy proof. The successor stays held until that proof passes. The lead applies the applicable stop disposition and authorizes a new attempt only under the date and predecessor rules. See [record shapes](evidence/record-shapes.md).

Maintenance first for a run with a receipt, print only under RL-174 B.5: one system-log query over this span, save beside journals, count by 10-minute bucket and process, associate leg intervals from summaries if available. No additional exclusion. Keep `bird`, `cloudd` and `fileproviderd` in the print permanently (RL-174 D.1).

```sh
echo 'maintenance context: spotlightknowledged and updater stopped 2026-11-15 15:32 PST (RL-174 C)'
@@MAINTENANCE@@
```

The Check proper reads only operational receipts, leg records and projected summaries; never open stream/energy/power/meter samples, transcript, member output or custody content as an agent.

```sh
"$PY" -I -B - "$OUT" "$LEGS" <<'PY'
import json, sys
from pathlib import Path
root=Path(sys.argv[1]); roster=sys.argv[2].split(',')
r=json.loads((root/'runner_receipt.json').read_text())
assert r['runner_kind']=='cadence-legs-v1.1' and r['roster']==roster
assert r['kit']['sha256']=='@@KIT_SHA@@' and r['kit']['frozen_commit']=='@@PIN@@' and r['kit']['campaign_id']=='@@CAMP@@'
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
# RL-150 R1 / RL-158 Q1: reference and release values for the look (RL-179 F-3).
@@Q1@@
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

Report SPAN/LEGS, six caps (short leg @@SHORT@@), receipt/restore and feed-stop lines, named stops, admitted count and exclusions under the six fixed rules, each consumer's release or timeout against @@FIRST@@, whether the reference came from a redo/excluded leg, maintenance overlaps, retry count (`soak_refusals`: kind not recorded), Q1 print, close epoch/fence-gone time, verified copy/offload marker and all native readbacks. Do not print power or energy. No commit from OUT. The magistrate reports; it never decides.

**After (the lead, at the desk; not the magistrate).** Use this kit and the frozen pin `@@PIN@@` for deterministic desk, off-host or controller-only during a clean close interval (RL-173 B). Check exact roster/attempt/reference/kit/plan identities and authenticated nonempty table (RL-172 (c)). Record desk FINAL, typed Q1 completion and the sampled hand table before a look reads this span (RL-179 F-3). On qual-01-s01 close, complete any outstanding RL-172a F1 soak comparison and RL-181 §4(a) leg-type hand-read before qual-01-s02 arms. Mark retried soaks for sampled hand-read; no missing refusal-kind field is invented. Update ledger `@@BLOCK@@` RUNNING/COLLECTED/DESK_FINAL. @@NEXT@@ Qualification energy stays sealed for its separately frozen look; no change to fit coefficients or score is authorized.
