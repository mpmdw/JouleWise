TBD. **Laptop lead, drafted by Sol 6.1; ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm the @@ORDINAL@@ span of qualification block `@@BLOCK@@`, span `@@SPAN@@`, legs @@LEGS@@, kit `@@CAMP@@.v1.1` (sha256 `@@KIT_SHA@@`), runner kind `cadence-legs-v1.1`, frozen pin `@@PIN@@` checked out detached in a fresh staged worktree. A fresh soak, then six conditionless 27B legs, Automatic, band q0; @@FIRST@@ captures the span reference, the five other legs consume it. Short leg: @@SHORT@@; all other caps 4,096. Expected @@EXPECTED@@ s; work worst case @@WORST@@ s; launcher deadline reserve includes the additional 1,950 s soak retry and 560 s cleanup reserves. EARLIEST @@DATE@@ 00:00:00 PST (epoch @@START@@), LIMIT @@DATE@@ 23:59:59 PST (epoch @@END@@), shortened by 24 h after issue. HOLD_FOR_FIT_FREEZE until freeze 2 is committed and verified. Predecessor `@@PRED@@` must close clean or this item is VOID and is never skipped. No clock exclusion, batch-window argument or clock fence at this pin (RL-171 §3; RL-172a). Launch is your LAST action; exit at once. Nothing else is authorized.**

```pointer
owner: magistrate
wait: none
deadline: @@POINTER_DEADLINE@@
on_early_or_refused: WAIT on an unfilled prerequisite or predecessor not closed. VOID on a dirty predecessor or 24 h expiry; REFUSE outside the date window, on development/qualification date overlap or date cap. READY v4 session: CEDE, do not arm. Any failed native checklist or launcher refusal: nothing launches, report to lead. Never retry, skip a predecessor, extend a queue, reuse OUT, or re-run a leg; a missed date requires a new lead item
next_observable: after fence disappearance, Check below reports operational receipt, all six leg summaries, Q1 reference print, maintenance overlaps, restore/process-group proof and close epoch; lead records desk-final and typed Q1 completion before span k+2 arms
```

- **Issued ahead (RL-173 D).** At most three counted spans ahead plus standing F0. Predecessor `@@PRED@@` in `@@PRED_CAMP@@`, roster @@PRED_LEGS@@; `pred_gate` reads only its receipt and leg-summary projection. Absent receipt = WAIT; any unclean close = VOID, never skipped. @@PRED_NOTE@@ This item has its own t0-date and no window argument; `expiry_gate` enforces 24 h and `watch_gate` re-reads the hand-stamped watcher observation at each arm (RL-173 C.5). Nothing is issued across a class A, L002 or L005 hand gate. @@HAND_NOTE@@
- **Why (RL-149 §2.3; RL-155 §5.3; RL-165 §8.1; RL-167 Part B; RL-172 (a),(b)).** Qualification tests the committed fit on held-out dates. This law's 6 + 6 cut keeps each true type-L pair adjacent in one span and gives each span four A legs and one L pair. First leg own-shaped/capture, all five others span-shaped/consume; no T or M. The M slots are ordinary A legs at 19,458. No class A smoke: class B, a mock span, plan and diff check (RL-165 §8.1; RL-172a F1). At the first qualification arm cite RL-172a F1. Its soak's operational fields and reference schema must be hand-compared with dev-05 before qual-01-s02; a difference goes to the research lead. The retry fires on slope or load refusal, once (RL-172a F2); the desk/look read `soak_attempts`, a retried soak forces the sampled hand table, and refusal kind prints "kind not recorded" until a later pin (RL-173 E).
- **Config provenance (RL-167 Part B Q1; Mythos #794 F5).** Record both runtime-config hashes: development `bf2cb2e6503c46373b52b10f32642d95a66a6636a3d7caaad0ce8b2b756781df`, qualification `272aecb8bc0d9e33defd7f686b129ea236b925fdfbf68137697120dd63232f46`. Only the unused `d_n_chunk_status` label differs; `lm-qual-01` prints both and must not require equality for inclusion.
- **Freeze and pin.** `freeze2_gate` implements RL-165 §8.1, RL-172 (i) row 9 and RL-173 E. Full commit/hash/path unfilled = WAIT/HOLD_FOR_FIT_FREEZE. The commit must be an ancestor of freshly fetched audit or main and contain that exact coefficient hash. No forecast or fit-code hash substitutes for it. `qual_pin_gate`: line 1 cold seat ADMIT **per kit**, including RL-167 Part B Q2's same-code capture/five-consumer confirmation; line 2 suite red set at the frozen bytes equals the merged W1-line commit `c3f4bacd8`, test for test, no added red (RL-165 §8.1). Record pointers remain lead fills. Later W1 merges do not move the qualification pin. Builder's mock checks grant no admission.
- **Day law (RL-174 B.3).** Dates: @@DATES@@. **Three distinct t0-dates, one block each**, none with a development leg. Each block holds two L pairs; fewer than three pair-days prints `not_evaluable` for the ±0.10 word (RL-166b §4). Sat 14–Wed 18 Nov are reserved development dates, and `day_gate` also checks moved development spans. The local t0-date assigns all six legs, including excluded legs and a close after midnight. RL-149 §2.3's cap **applies**: at most two blocks and 24 legs on a date, block starts at least 10 h apart. It is not used by this plan and cannot remedy a slip. A missed date requires the lead to re-date and re-commit the queues; they expire **Mon 23 Nov 00:00 PST** (RL-174 E.4). No automatic extension.
- **Host state (RL-174 C).** Freeze 2 proceeds on the host as it is; no visit, hygiene action or restart is a gate. Each arm states four lines: `spotlightknowledged` and updater present/absent (stopped Sun 15 Nov 15:32); `corespotlightd` present/on demand; indexing of `/` off; Time Machine destination none (`backupd` resident). The lead supplies the readback record and a hygiene-state identity, excluding boot time. Nobody changes a hygiene setting from freeze 2 through qual-03 close. An unplanned restart is an event: record it and refresh the four lines at the next arm; it holds nothing. `INCLUSION_RECORD` is filled by **RL-174 B.5**: the six rules stay unchanged and maintenance overlaps are print-only. `lm-qual-01` prints flagged and unflagged errors side by side, with counts by job, description only and no word. The lead appends the by-job count through dev-05 when its desk is final; that count gates nothing. The maintenance print carries the Sun15 15:32 service-stop date.
- **Gates 5–9 (RL-149 §2.8; RL-165 §6; RL-172 (c),(f); RL-173 A–E; RL-174 E.5).** Line 6: no named stop, halt or veto open, lead record of dispositions. Line 7: watcher observed within 24 h, re-read at both gates; this draft uses C.5. For an Actions watcher, RL-174 A.13 requires a scheduled successful completed run on this repository's `main`, started after the previous close; a manual run never serves an arm. Line 9: actual machine order across blocks/queues, desk-final and **typed Q1 completion** through span k−2. In particular qual-01-s01 needs dev-05-s01's desk-final and Q1 records; qual-01-s02 needs dev-05-s02's, span for span. `debt_gate` requires those named rows as well as the full machine-order debt record. No "first span of kit" exception. Automatic desk must satisfy all four RL-172 (c) identity/authentication rules, sampled hand table clear, disagreement holds next arm. Lead/magistrate supply observations and pointers; no default yes.
- **Close and copy (RL-171 §6.1; RL-172 (d); RL-173 A,B).** At least 300 s after a campaign close; 1,200 s after F0/F2/Part C/session/W1, using the **latest close of anything**, its Check and process-group absence, fence gone. Census stops on missing roots, unreadable or ambiguous stamps; `OTHER_CLOSE_EPOCH` covers sessions outside it. `PRIOR_CLOSE_EPOCH` cannot precede predecessor close. After a campaign close, copy marker `.ok` or `.air.ok` for that plan is required; after any other close, its Check/copy proof must bind the exact latest receipt path and close epoch; verified synchronous encrypted cloud offload counts permanently, upload finished before soak, plaintext/ciphertext hashes and size/provider confirmation recorded, key held off MBP, originals retained until verified copy. An unverified offload holds every arm including F0. A sync daemon is interim only; maintenance print includes bird/cloudd/fileproviderd. No marker is written by this item.
- **Quiet, native checks and stops.** Same measurement_mode (RL-149 §2.2/§2.4), Automatic, network time Off, frequency word 0, AC, meter ready, disk ≥40 GiB, no night/smoke agent, High Power marker, night.lock holder, stray monitor, root powermetrics or other agent. Preserve the dev-05 own-process-tree-only measurement_mode exception. Process/load census and rule 5 enforce quiet (RL-171 §2); no builds, analysis, SSH or tests while anything is armed. Named stops stop the next arm, never a running span. REFUSAL/restore/disk/watcher: lead clears; INSTRUMENT_FAULT: research lead; 3 contaminated redos: lead once, then research lead; two legs >1.5× own budget: lead; frozen-path/host-state changes: research lead (RL-149 §2.4). A reference missing at capture is refusal; no consumer proceeds on an invented reference. A READY v4 record preempts immediately (RL-172 (f)); no intended-session-time reservation.

**Start and check** (magistrate on the MBP only **after issue**; this builder never executes these blocks).

The lead stages a clean detached worktree at the frozen pin, the exact kit bytes from `6010985a3`, and this folder's committed queue. Queues do not exist on #794's branch; these finite draft queues are validated here, not issued by being committed. Lead fills their authenticated commit and issue-time records. Stage outside every registration/custody root; never run tests on the measurement host while a queue is live (RL-172 (i)4). Host-independent checks are in this folder's evidence.

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
KIT=/Users/edr/campaign-out/kits/@@CAMP@@.v1.1-6010985a3.json
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
all_gates || exit 1
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"
test ! -e "$CUSTODY/desk_fence.json" || exit 1
{ test ! -e /Users/Shared/JouleWise/host-power/high-power.marker && test ! -L /Users/Shared/JouleWise/host-power/high-power.marker; } || exit 1
lsof -- /Users/Shared/JouleWise/host-power/night.lock 2>/dev/null && exit 1 || true
sudo -n -l /bin/kill >/dev/null || exit 1
sudo -n systemsetup -getusingnetworktime   # Off; any other readback STOPS
pmset -g | grep -i powermode               # 0; frequency word 0 as item 308/251
pgrep -fl 'b6_r12|r12' || echo 'no r12'
pgrep -fl 'claude|codex|mcp-server|mcp_server|modelcontextprotocol' | grep -v "^$MAGISTRATE_PID " || echo 'no other agent'
pgrep -fl 'km003c_monitor.py|hazard_monitor.py' || echo 'no stray monitor'
pgrep -u root -fl powermetrics || echo 'no root powermetrics'
launchctl list | grep -E 'com\.joulewise\.(night|align-r0)' || echo 'no night/smoke agent'
MODE_RC=0
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify || MODE_RC=$?
echo "measurement_mode verify rc $MODE_RC"
# Inspect every FAIL: only own-process-tree agent lines allowed. Any other FAIL STOPS; WARN is recorded.
"$PY" -B scripts/launch_align_r0.py preflight --disk-path "$REPO"   # AC true, disk >=40 GiB; checklist includes meter
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" || exit 1
: "${CHECKLIST_OBSERVATIONS:?fresh native checklist observations JSON, recorded by magistrate}"
"$PY" -B scripts/cadence_queue.py checklist --kit "$KIT" --kit-sha256 "$KIT_SHA" --observations "$CHECKLIST_OBSERVATIONS" || exit 1
"$PY" -B scripts/cadence_legs_runner.py plan --kit "$KIT" --legs "$LEGS" || exit 1
# Plan must print expected_s @@EXPECTED@@, worst_case_s @@WORST@@, batch_windows [], runner_kind cadence-legs-v1.1.
# Record HEAD, kit frozen.commit, all identities and every native checklist line, meter presence and veto read.
BOOT="$(sysctl -n kern.boottime | sed -E 's/^\{ sec = ([0-9]+),.*$/\1/')"
case "$BOOT" in ''|*[!0-9]*) echo 'batch print: boot unreadable';; *) NEXT_BATCH=$((BOOT+43248)); while [ "$NEXT_BATCH" -le "$(date +%s)" ]; do NEXT_BATCH=$((NEXT_BATCH+86400)); done; echo "next OS batch epoch $NEXT_BATCH (boot + 12 h + 48 s + whole days)";; esac
OUT=/Users/edr/campaign-out/@@CAMP@@/cq-${SPAN}-a1-$(date -u '+%Y%m%dT%H%M%SZ')
test ! -e "$OUT" || exit 1
case "$OUT" in */restricted/*|*/night-*|"$REPO"/*|*/configs/campaigns/align_v4*) exit 1;; esac
```

Lead/magistrate supplies the current observations listed in `evidence/record-shapes.md`. `CHECKLIST_OK=yes` is set only **after** every native read above and the kit's complete checklist passes; an earlier supplied yes does not bypass a failed read. Disk, meter, process census, no halt/veto and all restore lines are mandatory.

**Run (your last action).** Re-read stops, veto, watcher, typed desk/Q1 debt, host-state identity and v4 READY record now, refreshing the observations. No cached eligibility answer. Verify the current kit/queue hashes again; fetch refs before the last gate. The pinned runner checks its native checklist and per-leg process census. It has no launch-time fence rule; the LaunchAgent's **shared desk fence still exists** until close. No `--batch-window` argument is passed.

```sh
git -C "$AUTH_REPO" fetch -q origin audit/2026-11-10-fable main || exit 1
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = "$KIT_SHA" || exit 1
test "$(shasum -a 256 "$QUEUE_FILE" | cut -c1-64)" = "$QUEUE_SHA" || exit 1
"$PY" -B scripts/cadence_queue.py checklist --kit "$KIT" --kit-sha256 "$KIT_SHA" --observations "$CHECKLIST_OBSERVATIONS" || exit 1
all_gates || exit 1
test ! -e "$CUSTODY/desk_fence.json" || exit 1
# Frozen plan launch minimum includes the one-soak retry; extra 900 s is start/preflight slack.
DEADLINE="$("$PY" -I -B -c 'import time; print(time.time()+@@DEADLINE_SECONDS@@)')"
"$PY" -B scripts/launch_cadence_span.py launch \
  --repo "$REPO" --python-bin "$PY" --kit "$KIT" --legs "$LEGS" \
  --output "$OUT" --disk-path "$REPO" --custody-root "$CUSTODY" \
  --magistrate-pid "$MAGISTRATE_PID" --deadline "$DEADLINE" \
  --exit-wait-seconds 180 --start-wait-seconds 30
echo "$OUT"
```

Require exit 0, `"next": "exit the magistrate session now"`, a claimed desk fence whose pid differs from MAGISTRATE_PID, and launch plan `batch_windows == []`. Record every gate print, all record pointers, date-rule/cap reading, predecessor/host close epochs and kind, GAP, issue/expiry/watch stamps, freeze-2 commit/path/hash, host-state identity, worktree HEAD, kit/queue commit/hash, six legs and their caps, OUT, DEADLINE, native readbacks and plan. Then exit at once. Any refusal is reported; nothing is re-armed on this authority.

**Check (next activation, after the fence is gone).** Maintenance first, print only under RL-174 B.5: one system-log query over this span, save beside journals, count by 10-minute bucket and process, associate leg intervals from summaries if available. No additional exclusion. Keep `bird`, `cloudd` and `fileproviderd` in the print permanently (RL-174 D.1).

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
# RL-150 R1 / RL-158 Q1: reference and release values only; gates nothing before the k+2 completion debt.
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

**After (the lead, at the desk; not the magistrate).** Use this kit and the frozen pin `@@PIN@@` for deterministic desk, off-host or controller-only during a clean close interval (RL-173 B). Check exact roster/attempt/reference/kit/plan identities and authenticated nonempty table (RL-172 (c)). Record desk FINAL and the separate typed Q1 completion in actual machine order before k+2; hand-read first kit/G0-shape group and every redo/exclusion/schema-change span (RL-173 E). First qualification close: compare soak operational fields/reference schema to dev-05 and record SAME before qual-01-s02 (RL-172a F1); difference goes to research lead. Mark retried soaks for sampled hand-read; no missing refusal-kind field is invented. Update ledger `@@BLOCK@@` RUNNING/COLLECTED/DESK_FINAL. @@NEXT@@ Qualification energy stays sealed for its separately frozen look; no change to fit coefficients or score is authorized.
