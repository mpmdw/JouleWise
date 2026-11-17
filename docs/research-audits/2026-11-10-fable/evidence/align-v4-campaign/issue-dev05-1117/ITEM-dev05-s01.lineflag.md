<LEAD FILLS: RUN_STATE item number at issue>. **Laptop lead (interactive, Opus 5.5), drafted under RL-171 by the items-rl171 builder 2026-11-15 PST (new draft; the dev-04/05 kits' builder and the Mythos dev-04/05 delta seat supply the facts), ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm the FIRST span of block dev-05 (RL-158 §3; RL-165 §1, §4; RL-171), span `dev-05-s01`, legs L001, L002, L003, L004, L005, L006, kit `cl-dev-05.v1.1` (sha256 `2747381bf1169471d929d1e91510f7d272ff9cbc973da2c99f11673bea53ca1a`), runner kind `cadence-legs-v1.1`, on `2d347f721552fe03bdd19f113e7bad7a7c24908e` checked out detached in a fresh scratch worktree. One span: a fresh soak, then six legs at their cells (L001 first; consumers L002, L003, L005, L006 judge their G0 against L001's capture), decode cap 4,096, Automatic, band q0. They are counted development legs of dev-05. No other span, no queue extension, no session, no W1. EARLIEST: the close interval (RL-171 §6.1) after dev-04's last span (`dev-04-s02`) closed with its fence gone and its Check reported, and not before 00:00:00 PST Wed 18 Nov (epoch 1794988800; this block's t0-date, RL-172 (a)). LAUNCH as soon as every gate holds, at any hour up to 23:59:59 PST Wed 18 Nov (LIMIT, epoch 1795075199; this block's t0-date, RL-172 (a)), except 10:50:00-13:15:00 (the pin's `fence_problems` refuses it under either argument). The batch-window argument follows the launch time (RL-171 §3): `02:00-02:35` from 02:35:00 to 10:50:00 and from 13:15:00 to 18:33:10; `13:14-13:15` from 18:33:11 to 02:34:59. ISSUED AHEAD (RL-173 D): this item names its predecessor `dev-04-s02` and requires that span's clean close receipt, else it is VOID and is not skipped; it EXPIRES 24 h after issue, so its window ends at the earlier of LIMIT and the expiry. The launch is your LAST action and you exit at once. If you cannot, do not launch; mail the lead (the standing F0 item then applies).**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-19T08:17:00-08:00
on_early_or_refused: VOID, so that nothing of this item ever launches (mail the lead; a new item is needed), if `dev-04-s02` closed without a clean receipt (RL-173 D.2) or once 24 h have passed since the issue (RL-173 D.5). Otherwise: any failed line of "Start and check", any launch refusal (rc≠0 or no claimed fence), or a launch that cannot happen inside the bands below (Wed 00:00:00 to Wed 23:59:59 PST, outside 10:50:00-13:15:00): NOTHING of this item launches; mail the lead; a later t0 needs a new item, and the standing F0 item applies meanwhile. A span that ran but ends with any named stop or a receipt rc≠0: nothing relaunches, nothing is re-run, nothing else is queued; mail the lead. Do not retry, do not extend, do not reuse OUT
next_observable: the next activation (after the fence is gone) runs "Check" below and reports, by email to Ed and the lead and as RUN_STATE <LEAD FILLS: the next RUN_STATE Check item number at issue>: the maintenance line, the receipt asserts, the per-leg admitted lines with g0_role and span_reference, the desk bundle, the restore lines, measurement_mode verify again, and the RL-150 R1 / RL-158 Q1 print (gates nothing)
```

- **Issued ahead (RL-173 D; the interim until #800 is admitted; items-1115 builder, Sun 15 Nov 2026 PST).** (1) At most three counted spans are issued ahead of the machine, plus the standing F0. (2) **Predecessor: `dev-04-s02`** (dev-04's second span). This item requires its clean close receipt: `pred_gate` below reads its `runner_receipt.json` (rc, error, roster, leg counts, span_result, close steps, close time) and its desk bundle's `leg_summary.json` files (wall against budget, contaminated redos), never an energy, power or meter value. No receipt yet is WAIT. A receipt that is not clean makes this item VOID: it is not skipped, nothing launches on its authority, and the lead decides. (3) Its date window is Wed 18 Nov (RL-172 (a)), and its own argument choice is `pick_arg` below. (4) Nothing is issued past a class A hand-read or an L002 or L005 gate. **Not issuable ahead of dev-04's L005 gate** (RL-173 D.4): it follows `dev-04-s02`, which is itself behind that gate. (5) It expires 24 h after issue: `expiry_gate` (ISSUED_EPOCH + 86,400 s) runs in Start and check and again just before the launch.
- **Why (RL-158 §3; RL-165 §1; RL-171).** dev-05 follows at its first legal t0 on its own t0-date, Wed 18 Nov (RL-172 (a): each mixed-size block gets its own date; this amends RL-165 §1's "dev-04 and dev-05 follow at their first legal t0"). RL-171 retires the 18:33:10 latest t0 (the 01:50 fence) and the 02:40 starts: this pin's fence check is met by the argument `13:14-13:15` from 18:33:11 (RL-171 §3), so the span arms at any t0 outside 10:50-13:15. The 6 + 6 layout is RL-158 Q6's (the kits' builder, `/Volumes/JW-EXT/scratch/dev04-05/README.md`). A leg's calendar day is the local date of its span's t0.
- **Gate.** All of:
  - dev-04's last span (`dev-04-s02`) closed and checked: RUN_STATE 382: RECEIPT OK, 6/6 legs run and admitted, no named stop, MEASURED_OK / COMPLETE, restore lines all rc 0; close 2026-11-17 05:51:03 PST (epoch 1794923463.33); item 386 confirms desk FINAL at `a5ffa385f`. This historical close does not replace the fresh host close census at the arm.
  - **The cold seat's delta on `cl-dev-05.v1.1`: ADMIT** (Mythos 5.2, Sat 14 Nov 18:25 PST, "neither kit needs a byte changed"; `/Volumes/JW-EXT/scratch/mythos-dev0405-delta/REPORT.md`, evidence/align-v4-campaign/mythos-dev04-05.md, audit branch `da8b855b6` (byte-identical to the scratch report)).
  - **Mythos dev-04/05 F1, the two dev-03 records (RL-150 R5; §2.8 line 8 for these kits):** dev-03's R9 **PASSED** and its class A smoke **MET** (L002 released its G0 against L001's capture and ran its turn), each recorded on its own line: R9 PASSED and class A smoke MET, signed by the lead 2026-11-16 05:38:41 PST, each on its own line in RUN_STATE 365 (the lead's hand-read record); desk evidence `pilot-desk-cq-dev-03-s01-a1/` at `734e7f6be` on audit/2026-11-10-fable. dev-03 ran on `cl-dev-03.v1.1`, not the own-shaped v1.1a fallback; on that fallback this kit may not arm as built (F1) and the case goes to the research lead.
  - **Q6 (RL-158 Q6; RL-161):** on 6 + 6 dev-05 has 6 of its 10 warm legs as consumers (L002, L003, L005, L006 in span 1; L008, L012 in span 2), at least half, and every cut lands on an own-shaped leg (L007). This span's consumers: L002, L003, L005, L006.
  - **dev-04 ran span-shaped to its end:** if dev-04's second span did not arm under the L005 gate (fewer than four of dev-03's consumers released), this item is NOT issued: dev-05 then runs own-shaped (RL-165 §4).
  - Lines 2, 3, 5, 6, 7 and 9 at the arm (below).
  - **Day law (RL-172 (a), which replaces the two-starts default):** a day is the local date of a span's t0. No t0-date holds more than 12 mixed-size development legs (dev-03, dev-04, dev-05) or more than 24 development legs; qualification t0-dates are disjoint from development t0-dates; hp-01, F0, F2 and v4 sessions are outside the count. **This span's t0-date is Wed 18 Nov** (dev-05, 12 mixed-size legs over its two spans); this item's window admits only that date. A span that misses its date is re-dated by the lead with a new item, never doubled up. Planned: Sat 7, Sun 11, Mon 18 (dev-02-s03 and dev-03), Tue 12 (dev-04), Wed 12 (dev-05). Because the queue does not yet enforce dates, `day_gate` counts the development legs already launched on the t0-date from their receipts and refuses this span past either cap; the committed queues' `not_before` values are lower bounds only.
  - **Host gate and R1 reservation, immediately before the launch (Sol items review P1-1, P1-2; RL-165 §7):** the Check of the latest close of ANYTHING on this host reported every restore line OK; no desk fence; no night or smoke agent loaded; no High Power marker; at least GAP seconds since that latest close (RL-171 §6.1, amending RL-155 R-B's 20 minutes: GAP is QUIET_CAMPAIGN_S after a campaign span's close, 300 s, confirmed by RL-172 §0; GAP is 1,200 s after a Part C or F0, F2, a slot session or W1), from the receipt census that stops on a missing root, any lookup error or an empty result (or OTHER_CLOSE_EPOCH); and, after a CAMPAIGN close, that close's journal copy complete and hash-verified, shown by the marker `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok`, written only after the copy is verified (by the lead's Air copy, or by the MBP's own verified encrypted cloud offload, items 347 and 348, which RL-173 A makes the off-host copy permanently; a failed or unverified offload writes no marker and holds the arm, RL-173 A 7) (Sol items-rl171 P1; a missing marker is WAIT; no SSH once a span is armed). Read fresh at the launch: if a v4 slot session is READY and staged for this slot, this span cedes; RL-172 (f) retires RL-165 §7's worst-case reservation: from the lead's record that a v4 session is READY nothing of lower priority arms, and the session takes the next clean close; before that record this span arms as usual.
- **Counted.** The six legs count as development legs of dev-05 under the kit's inclusion rules (RL-149 §2.3, §2.4 as amended by RL-150 R7 and R8; rule 2 against the reference the leg's shape names). The kit has no `pilot_counted` rule (dropped by the builder: it described dev-03's smoke; Mythos delta: right). An excluded leg is refilled only from the reserve under RL-149 §2.4. A re-run is a new span with `attempt` + 1 and `rerun_of`, and it needs a ruling.
- **Queue.** `QUEUE-cl-dev-05-2d347f721.json`: `cq-cl-dev-05`, spans `dev-05-s01` (L001-L006) and `dev-05-s02` (L007-L012), both not_before 2026-11-17 (a lower bound only: dev-05's t0-date is Wed 18 Nov, RL-172 (a), which this item's window encodes), `expires_at` 2026-11-21T23:59:00-08:00 (the items-rl171 copy: the builder's not_before 2026-11-18 moved to 2026-11-17 under the earlier two-starts default, and the expiry moved from 11-22 to 11-21 so that a commit any time from now is within 7 days, Mythos dev-04/05 F2). Do not run `cadence_queue.py next`: `not_before` and the k+2 desk rule are not enforced in code at this pin (Mythos F4); this item and line 9 carry them.
- **Bytes, CI and condition 13.** Measured from `2d347f721552fe03bdd19f113e7bad7a7c24908e` (the dev-03 pin). The kit is `cl-dev-05.v1.1.json` from `fecaf73f3579756c6e735f6a9cc74aab011d293a` (branch `align/2026-11-14-dev04-05-kits`, on #788's head `9cbb365a6`; kit files only), sha256 `2747381bf1169471d929d1e91510f7d272ff9cbc973da2c99f11673bea53ca1a`, master seed 2026111406, copied outside the checkout. Its frozen block, runner, stop_rules, span_template, checklist, looks and desk are byte-identical to `cl-dev-03.v1.1`'s (Mythos delta). Line 2 is dev-03's, one result for the pin (Mythos F5). `verify_r1_executed_sources` must return the full sha. Same bytes as dev-03, so no smoke of its own: dev-03's pilot was the class A smoke (F1).
- **Timing.** Plan for this roster (`plan` at `2d347f721` with both arguments, blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-dev05-s01.txt`): expected 11,680 s, worst case 24,750 s (6 h 52 min 30 s); fence deadline launch + 26,210 s. Budgets: L001 (10000, own, first leg: its capture is the span's reference) 1156; L002 (2000, span, consume) 1467; L003 (19458, span, consume) 1642; L004 (2000, own) 1076; L005 (19458, span, consume) 1642; L006 (10000, span, consume) 1547.
  - **Bands (RL-171 §3; the `pick_arg` function below), on Wed 18 Nov:** 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-18:33:10 `02:00-02:35`; 18:33:11-02:34:59 `13:14-13:15` (which admits six legs up to 05:47:10). Checked: with `02:00-02:35` 18:33:10 accepted and 18:33:11 refused; with `13:14-13:15` 05:47:10 accepted and 05:47:11 refused; 10:50:01 refused under either. `validate-kit` ok with either argument. A mock span at t0 Mon 00:30 with `13:14-13:15` across 02:00-02:35: rc 0, 6 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/dev05s01-alt-00:30/`).
  - Forecast t0 Wed 00:00:00 (dev-05's t0-date, RL-172 (a); the last Tuesday F0 closes 16:25:12), argument `13:14-13:15`: expected end 03:14:40, worst end 06:52:30, fence end 07:16:50 (`/Volumes/JW-EXT/scratch/items-rl171/plans/chain-new.txt`).
  - Pointer deadline = latest fence end (LIMIT + 26,210 s = Thu 07:16:49) + 1 h.
- **Conditions, blinding and the High Power marker:** as the dev-03 items, with `--legs "$LEGS"` written out and `--batch-window "$ARG"` on every `validate-kit`, `plan` and `launch` (chosen once in Start and check by the launch time, re-checked in Run; RL-171 §3); the arm record shows the plan's `batch_windows` and the measurement_mode line (RL-150 §2 F2, F5; RL-161 §3); output root `/Users/edr/campaign-out/cl-dev-05/`. Quiet is the per-leg agent census, process census and rule 5 (RL-171); there is no clock quiet.
- **May run:** this span, once. **May NOT:** any other dev-05 or dev-05 span of dev-04, any session, W1, any filler while this span is armed.

**RL-149 §2.8 arm-record lines (record each, with its evidence):**
1. Kit `ruling` is `RL-149 §2`. `cl-dev-05.v1.1` `2747381b…ca1a` at `2d347f721`: the Mythos 5.2 delta seat against `cl-dev-03.v1.1`, ADMIT (above); dev-03's line 1 (row-1 ADMIT at `17f478675`, Mythos first and delta seats on #788) stands for the shared bytes.
2. As dev-03's line 2 (RL-165 §5's four parts at `2d347f721`; CI run 43664825578 on `9cbb365a6`): CI `ci` run 43664825578 on `9cbb365a6` COMPLETED 2026-11-14 20:47:37 PST, conclusion **failure** (9 of 12 `test` shards red; every other job success). Shard 11 was not stalled: it finished at 3 h because `tests.test_bytes_analysis` took 9,107 s and passed. The final red set is **exactly the 12 tests of `fe907d0d3`'s CI 43600776368, test for test, with no added red** (both sets re-derived from the job logs by the items-1115 builder, Sun 15 Nov 15:03 PST; evidence/align-v4-campaign/item-drafts-1115/evidence/line2-dev03-red-9cbb365a6.txt and line2-base-red-fe907d0d3.txt); one result for dev-03 to dev-05 (Mythos F5).
3. Queue `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-dev-05-2d347f721.json` on audit/2026-11-10-fable at `b7a0d9882` (`b7a0d98822865a01e67fc3cc1833c9b186be2181`; validate-queue re-run ok at `2d347f721` Sun 15 Nov 15:05 PST), sha256 `391f438281af05fece9866ec532e7fdb4b0f478b297e403bd99da6153e2fafbb` (`validate-queue` ok at `2d347f721` with `--kits-root` the dev-04/05 kit checkout at `fecaf73f3`: plan ids `cq-dev-05-s01-a1`, `cq-dev-05-s02-a1`; `/Volumes/JW-EXT/scratch/items-rl171/queue/validate-queue.log`).
4. `validate-kit` passes; OUT is outside every v4 registration and custody root (check below).
5. The per-span checks of design doc §4 and §14 pass at the arm and at the close. Do NOT run `cadence_queue.py checklist` or `next`.
6. No named stop, veto or halt open (the `directive` and `cadence-stop` issues; gh via `launchctl asuser`). By hand: no named stop open from any earlier span, no RESTORE_UNPROVEN and no High Power `revoked` hold: `dev-01-s01` desk `pilot-desk-cq-dev-01-s01-a1/auto/stops.json` = [] (`c73e78227`); `dev-01-s03` desk `desk-cq-dev-01-s03-a1/auto/stops.json` = [] (`8e59f38cd`); `dev-01-s04` desk `desk-cq-dev-01-s04-a1/auto/stops.json` = [] (`c9fc0339d`); `hp-01-s01` desk `desk-cq-hp-01-s01-a1/auto/stops.json` = [] (`e78597784`); `hp-01-s02` desk `desk-cq-hp-01-s02-a1/auto/stops.json` = [] (`37afda2a4`); `hp-01-s03` desk `desk-cq-hp-01-s03-a1/auto/stops.json` = [] (`05c681ac4`); `dev-02-s02` desk `desk-cq-dev-02-s02-a1/auto/stops.json` = [] (`522815544`); `dev-02-s03` desk `desk-cq-dev-02-s03-a1/auto/stops.json` = [] (`4a53c34a4`); `dev-03-s01` desk `pilot-desk-cq-dev-03-s01-a1/auto/stops.json` = [] (`734e7f6be`); `dev-03-s02` desk `desk-cq-dev-03-s02-a1/auto/stops.json` = [] (`38aa22e50`); `dev-04-s01` desk `desk-cq-dev-04-s01-a1/auto/stops.json` = [] (`a8d34609b`); `dev-04-s02` desk `desk-cq-dev-04-s02-a1/auto/stops.json` = [] (`a5ffa385f`); all twelve committed desks read by the preparer 2026-11-17 08:51:49 PST; no RESTORE_UNPROVEN or High Power `revoked` hold recorded in the prior lead fills (items 367/372) and subsequent Checks 380/382/385; item 386 records dev-04 desks re-executed and signed FINAL. This is a document read, not a live host/issue observation; the magistrate still checks current directives, stops, restores and High Power at the arm.
7. Results-ref watcher recorded as a flag: `com.joulewise.air-watch` has been off since 2026-11-17 07:53 PST (RUN_STATE 384); no Actions watcher is wired (RUN_STATE 386; item-drafts-1115/STATUS.md section 5). No live results-ref watcher; `watch_gate` prints the flag and returns 0. This is the requested unissued variant B, pending lead adoption.
8. dev-03's R9 PASSED and its class A smoke MET (Gate above; Mythos F1).
9. Line 9, across blocks in run order (RL-165 §6). Expected: this span is campaign span 13 (RUN_STATE 367/372 line 9 number dev-04-s01/s02 as 11/12), so span 11's desk, `dev-04-s01`, must be FINAL. As run: <fill at arm>. The named two-back desk `dev-04-s01` is FINAL: FINAL (automatic desk = independent hand table, 0 of 114 per-leg and 0 span-level values differ, inclusion included, stops [] both sides), built 2026-11-17 08:40:41.947347 PST, audit `a8d34609b`, `evidence/align-v4-campaign/desk-cq-dev-04-s01-a1/RESULT.json` (`desk_final`) and `auto/stops.json`; re-executed and signed FINAL by magistrate cb24533b, RUN_STATE 386 (08:40-08:50 PST). Q1 completion record: `evidence/cadence-standing/q1/cq-dev-04-s01-a1.json`, recorded 2026-11-17 08:44:15 PST. The committed RESULT/Q1 still say PROPOSED/lead signs; item 386 is the later signature record.

**Start and check (while you are still alive).** From a FRESH scratch worktree detached at the full sha (NOT the canonical clone's checkout, not a dev-01, dev-02 or hp-01 worktree), own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONPATH=.:tests`, `python3.13 -B -m unittest`, one module at a time; all must be OK: `tests.cadence.test_kit_v11`, `tests.cadence.test_span_reference`, `tests.cadence.test_legs_runner`, `tests.cadence.test_kit`, `tests.cadence.test_stops_desk`, `tests.cadence.test_runner_guards`, `tests.cadence.test_launch_cadence_span`, `tests.align.test_r1_smoke_launcher`. (At `2d347f721` the kit files are not in the tree, so `test_kit_v11`'s four committed-kit tests skip; they ran with 0 skips in CI shard 7, line 2 D2. The armed kit is checked by `validate-kit` below.) Any failure: nothing launches; mail the lead.

```sh
git -C /Users/edr/code/JouleWise fetch origin align/2026-11-14-kit-v1-1
git -C /Users/edr/code/JouleWise fetch origin align/2026-11-14-dev04-05-kits   # the kit file (not on the pin)
test -e /Users/edr/code/jw-wt/cadence-dev-05-s01 || git -C /Users/edr/code/JouleWise worktree add --detach /Users/edr/code/jw-wt/cadence-dev-05-s01 2d347f721552fe03bdd19f113e7bad7a7c24908e   # reused on a retry after a WAIT
cd /Users/edr/code/jw-wt/cadence-dev-05-s01
test "$(git rev-parse HEAD)" = 2d347f721552fe03bdd19f113e7bad7a7c24908e || { echo "STOP: HEAD"; exit 1; }
test -z "$(git status --porcelain)" || { echo "STOP: dirty tree"; exit 1; }
REPO="$PWD"
: "${PY:?Set PY to the existing pinned measurement-venv interpreter (do not resolve the symlink)}"
: "${MAGISTRATE_PID:?Set to the PID of this magistrate own claude process}"
ps -o pid=,comm= -p "$MAGISTRATE_PID"                 # must show the claude process
: "${PRIOR_CLOSE_EPOCH:?Set to the later of dev-04 last span (dev-04-s02) runner_receipt ended.epoch_s and the epoch its fence was seen gone}"
# The roster (RL-158 Q6's 6 + 6; the queue's span)
SPAN=dev-05-s01;  LEGS=L001,L002,L003,L004,L005,L006; DEADLINE_S=26210; WORST_S=24750; EXPECT="expected_s 11680, worst_case_s 24750"
QUIET_CAMPAIGN_S=300    # RL-171 §6.1, confirmed by RL-172 §0: 300 s after a campaign close; 1,200 s after F0, F2 or any other close
: "${LAST_CLOSE_KIND:?Set to campaign if the latest close of anything on this host was a campaign span, else other (Part C/F0, F2, slot session, W1)}"
case "$LAST_CLOSE_KIND" in campaign) GAP=$QUIET_CAMPAIGN_S;; other) GAP=1200;; *) echo "STOP: LAST_CLOSE_KIND must be campaign or other"; exit 1;; esac
echo "close interval GAP $GAP s (RL-171 §6.1; 1,200 s after a Part C or F0, F2, a slot session or W1)"
# ONE newest-close selection over both roots, used by the host gate and by copy_gate (Sol RL-172 re-check 1)
close_census() {
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
  CENSUS_EPOCH="$(printf '%s\n' "$CENSUS" | sed -n 1p)"
  NEWEST_RECEIPT="$(printf '%s\n' "$CENSUS" | sed -n 2p)"
  case "$CENSUS_EPOCH" in ''|*[!0-9]*) echo "STOP: the receipt census gave no close epoch"; return 1;; esac
  test -n "$NEWEST_RECEIPT" || { echo "STOP: the receipt census gave no receipt path"; return 1; }
}
# The effective close, computed ONCE per gate (Sol confirm P1): max of the census and OTHER_CLOSE_EPOCH, with its path or label.
# The host gate's GAP and copy_gate's kind check both use EFF_EPOCH / EFF_PATH from the same call.
effective_close() {
  case "${OTHER_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo "STOP: OTHER_CLOSE_EPOCH must be a whole epoch (rounded up) of a session/W1 close, or an explicit 0"; return 1;; esac
  close_census || return 1
  EFF_EPOCH=$CENSUS_EPOCH; EFF_PATH="$NEWEST_RECEIPT"
  if test "$OTHER_CLOSE_EPOCH" -gt "$CENSUS_EPOCH"; then
    EFF_EPOCH=$OTHER_CLOSE_EPOCH; EFF_PATH="OTHER_CLOSE_EPOCH $OTHER_CLOSE_EPOCH (a session or W1 close outside the census roots)"
  fi
}
# Sol items-rl171 P1 and Sol RL-172 re-check 1: the newest close of anything (the census above, or OTHER_CLOSE_EPOCH for a
# session/W1 close outside its roots) must agree with LAST_CLOSE_KIND. After a CAMPAIGN close, that receipt's journal copy must be
# complete and hash-verified off the MBP (the lead's Air copy, or the MBP's verified cloud offload, RL-173 A), and only then is written
# /Users/Shared/JouleWise/desk-copy/<plan-id>.ok (the copy manifest's sha256 and a `date` stamp). No SSH once a span is armed.
# A marker is only ever derived from a campaign receipt path; after a Part C, F0, F2, session or W1 close the Check covers the copy.
copy_gate() (   # a subshell: it reads EFF_PATH (from effective_close) and LAST_CLOSE_KIND and changes nothing the host gate reads
  test -n "${EFF_PATH:-}" || { echo "STOP: copy_gate needs effective_close first"; exit 1; }
  if printf '%s\n' "$EFF_PATH" | grep -Eq '^/Users/edr/campaign-out/cl-[a-z0-9-]+/cq-[a-z0-9-]+-a[0-9]+-[0-9]{8}T[0-9]{6}Z/runner_receipt\.json$'; then
    newkind=campaign
  else
    newkind=other
  fi
  test "$newkind" = "$LAST_CLOSE_KIND" || { echo "STOP: contradictory LAST_CLOSE_KIND ($LAST_CLOSE_KIND): newest close is $EFF_PATH; mail the lead"; exit 1; }
  if test "$newkind" = other; then
    echo "copy gate: newest close is non-campaign ($EFF_PATH); its Check covers the copy"; exit 0
  fi
  plan_id="$(basename "$(dirname "$EFF_PATH")" | sed -E 's/-[0-9]{8}T[0-9]{6}Z$//')"
  case "$plan_id" in cq-*-a[0-9]*) ;; *) echo "STOP: no campaign plan id in $EFF_PATH"; exit 1;; esac
  copy_ok="/Users/Shared/JouleWise/desk-copy/$plan_id.ok"
  test -s "$copy_ok" || { echo "WAIT: no journal-copy marker $copy_ok for the newest close, campaign span $plan_id ($EFF_PATH): the lead's hash-verified copy is not done; retry at the next activation"; exit 1; }
  echo "journal copy of $plan_id: $(cat "$copy_ok")"     # record this line
)
# RL-173 D.5: this item EXPIRES 24 h after issue (ISSUED_EPOCH is the same moment as ISSUED in the heading).
ISSUED_EPOCH=<LEAD FILLS: the issue time as an epoch, from `date +%s` at issue>
EXPIRES_EPOCH=$((ISSUED_EPOCH + 86400))
expiry_gate() {
  test "$(date +%s)" -le "$EXPIRES_EPOCH" || { echo "VOID: this item expired at $(date -r "$EXPIRES_EPOCH" '+%Y-%m-%d %H:%M:%S %Z') (RL-173 D.5: 24 h after issue); nothing of it launches; mail the lead"; return 1; }
  echo "expiry: this item is valid until $(date -r "$EXPIRES_EPOCH" '+%Y-%m-%d %H:%M:%S %Z') (RL-173 D.5)"
}
# RL-173 D.2: the predecessor by span id and its CLEAN close receipt. No receipt yet is WAIT; a receipt that is not clean
# makes this item VOID (never skipped). Reads only the receipt's rc, error, mock, roster, leg counts, span_result, close
# steps and ended time, and each desk-bundle leg_summary's wall_s, budget_s and contaminated_redos (RL-149 §2.4's
# LEG_OVERTIME and CONTAMINATED_REDOS); no energy, power or meter value.
PRED_SPAN=dev-04-s02; PRED_CAMP=cl-dev-04; PRED_ROSTER=L007,L008,L009,L010,L011,L012
pred_gate() {
  PRED_LINE="$("$PY" -I -B - /Users/edr/campaign-out "$PRED_CAMP" "$PRED_SPAN" "$PRED_ROSTER" <<'PY'
import json, math, os, re, sys
root, camp, span, roster = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(",")
d = os.path.join(root, camp)
if not os.path.isdir(d):
    print(f"WAIT: no {d}: the predecessor {span} has not run; retry at the next activation"); sys.exit(1)
pat = re.compile("cq-" + re.escape(span) + r"-a\d+-\d{8}T\d{6}Z")
hits = sorted(n for n in os.listdir(d) if pat.fullmatch(n))
if not hits:
    print(f"WAIT: the predecessor {span} has no output directory under {d}: it has not run; retry at the next activation"); sys.exit(1)
if len(hits) > 1:
    print(f"STOP: the predecessor {span} has {len(hits)} output directories {hits}: a re-run needs the lead; mail the lead"); sys.exit(1)
out = os.path.join(d, hits[0])
p = os.path.join(out, "runner_receipt.json")
if not os.path.isfile(p):
    print(f"WAIT: the predecessor {span} ({out}) has no runner_receipt.json: it has not closed; retry at the next activation"); sys.exit(1)
try:
    r = json.load(open(p))
except (OSError, ValueError):
    print(f"STOP: the predecessor receipt {p} is unreadable; mail the lead"); sys.exit(1)
if not isinstance(r, dict):
    print(f"STOP: the predecessor receipt {p} is unreadable; mail the lead"); sys.exit(1)
num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
bad, n = [], len(roster)
if r.get("rc") != 0: bad.append(f"rc {r.get('rc')!r}")
if r.get("error") not in (None, ""): bad.append("error set")
if r.get("mock") not in (False, None): bad.append("mock receipt")
if r.get("roster") != roster: bad.append(f"roster {r.get('roster')!r}")
if r.get("legs_planned") != n or r.get("legs_finished") != n:
    bad.append(f"legs {r.get('legs_finished')!r} of {r.get('legs_planned')!r}")
sr = r.get("span_result") if isinstance(r.get("span_result"), dict) else {}
if sr.get("outcome") != "MEASURED_OK" or sr.get("chain_outcome") != "COMPLETE" or sr.get("fault") is not False:
    bad.append(f"span_result {sr.get('outcome')!r}/{sr.get('chain_outcome')!r}/fault {sr.get('fault')!r}")
steps = [s for s in (r.get("steps") or []) if isinstance(s, dict)]
close = [s for s in steps if s.get("name") == "restore" or str(s.get("name", "")).startswith(("stop-", "close-"))]
if not any(s.get("name") == "restore" for s in close): bad.append("no restore step")
bad += [f"close step {s.get('name')} rc {s.get('rc')!r}" for s in close if s.get("rc") != 0]
ended = (r.get("ended") or {}).get("epoch_s") if isinstance(r.get("ended"), dict) else None
if not num(ended): bad.append("ended.epoch_s unreadable")
over = redos = 0
for leg in roster:
    sp = os.path.join(out, "desk-bundle", "legs", leg, "leg_summary.json")
    try:
        s = json.load(open(sp))
    except (OSError, ValueError):
        bad.append(f"no readable desk-bundle leg_summary for {leg}"); continue
    w, b, c = s.get("wall_s"), s.get("budget_s"), s.get("contaminated_redos")
    if not (num(w) and num(b) and isinstance(c, int) and not isinstance(c, bool)):
        bad.append(f"{leg} wall_s/budget_s/contaminated_redos unreadable"); continue
    over += w > 1.5 * b
    redos += c
if over >= 2: bad.append(f"LEG_OVERTIME: {over} legs over 1.5 x their budget")
if redos >= 3: bad.append(f"CONTAMINATED_REDOS: {redos} in the span")
if bad:
    print(f"VOID: the predecessor {span} ({out}) did not close clean: {'; '.join(bad)}. RL-173 D.2: this item is VOID and is not skipped; nothing of it launches; mail the lead"); sys.exit(1)
print(f"PRED CLEAN {span} {out}: rc 0, {n} of {n} legs, MEASURED_OK COMPLETE, close steps rc 0, overtime legs {over}, contaminated redos {redos}, close_epoch {math.ceil(ended)}")
PY
)"
  PRED_RC=$?
  printf '%s\n' "$PRED_LINE"      # record this line
  test "$PRED_RC" -eq 0 || return 1
  PRED_CLOSE_EPOCH="$(printf '%s\n' "$PRED_LINE" | sed -n 's/^PRED CLEAN .*close_epoch \([0-9][0-9]*\)$/\1/p')"
  case "$PRED_CLOSE_EPOCH" in ''|*[!0-9]*) echo "STOP: pred_gate gave no close epoch; mail the lead"; return 1;; esac
  if [ -n "${PRIOR_CLOSE_EPOCH:-}" ] && [ "$PRIOR_CLOSE_EPOCH" -lt "$PRED_CLOSE_EPOCH" ]; then
    echo "STOP: PRIOR_CLOSE_EPOCH $PRIOR_CLOSE_EPOCH is before $PRED_SPAN's receipt close $PRED_CLOSE_EPOCH; mail the lead"; return 1
  fi
}
# Line 7 (RL-173 C 5): one watcher observation under 24 h old may serve more than one arm; each arm re-checks it.
WATCH_UNTIL_EPOCH=0    # variant B: no live watcher observation; unused by watch_gate
watch_gate() {
  echo "FLAG: no live results-ref watcher (Air paused, RUN_STATE 384)"
  return 0
}
# RL-172 (a): t0-date caps, counted from the receipts of development spans already launched on this t0-date (today, local).
# From each receipt only `started.epoch_s` and `roster` are read; either one unreadable is STOP, never zero (Sol RL-172 re-check 2).
DAY_MIXED=yes      # mixed-size development block (dev-03, dev-04, dev-05)
day_gate() {
  DAY_ROSTER_N="$(printf '%s\n' "$LEGS" | tr ',' '\n' | grep -c .)"
  "$PY" -I -B - /Users/edr/campaign-out "$(date +%s)" "$DAY_ROSTER_N" "$DAY_MIXED" <<'PY'
import json, os, re, sys, datetime as dt, zoneinfo
TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
root, now, n, mixed = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4] == "yes"
day = dt.datetime.fromtimestamp(now, TZ).date()
DEV = {"cl-dev-01", "cl-dev-02", "cl-dev-03", "cl-dev-04", "cl-dev-05"}
MIX = {"cl-dev-03", "cl-dev-04", "cl-dev-05"}
LEG = re.compile(r"L\d{3}")
dev = mix = 0; seen = []
def started_of(p):
    try:
        r = json.load(open(p))
    except (OSError, ValueError):
        sys.exit(f"STOP: receipt unreadable: {p}; mail the lead")
    if not isinstance(r, dict):
        sys.exit(f"STOP: receipt unreadable: {p}; mail the lead")
    started = r.get("started")
    t0 = started.get("epoch_s") if isinstance(started, dict) else None
    if isinstance(t0, bool) or not isinstance(t0, (int, float)):
        sys.exit(f"STOP: receipt started.epoch_s unreadable: {p}; mail the lead")
    return r, t0
# RL-172 (a) rule 3: a qualification t0-date holds no development span
for camp in sorted(os.listdir(root)):
    if camp.startswith("cl-qual-") and os.path.isdir(os.path.join(root, camp)):
        for d in sorted(os.listdir(os.path.join(root, camp))):
            p = os.path.join(root, camp, d, "runner_receipt.json")
            if os.path.isfile(p) and dt.datetime.fromtimestamp(started_of(p)[1], TZ).date() == day:
                sys.exit(f"STOP: RL-172 (a): {day} is a qualification t0-date ({p}); no development span arms on it")
for camp in sorted(os.listdir(root)):
    if camp not in DEV:
        continue
    for d in sorted(os.listdir(os.path.join(root, camp))):
        p = os.path.join(root, camp, d, "runner_receipt.json")
        if not os.path.isfile(p):
            continue
        r, t0 = started_of(p)
        if dt.datetime.fromtimestamp(t0, TZ).date() != day:
            continue
        roster = r.get("roster")
        if not (isinstance(roster, list) and roster and all(isinstance(x, str) and LEG.fullmatch(x) for x in roster)
                and len(set(roster)) == len(roster)):
            sys.exit(f"STOP: receipt roster unreadable: {p}; mail the lead")
        k = len(roster)
        dev += k; mix += k if camp in MIX else 0; seen.append((d, k))
print(f"t0-date {day}: development legs already launched {dev} (mixed-size {mix}) {seen}; this span {n}, mixed {mixed}")
if dev + n > 24:
    sys.exit("STOP: RL-172 (a): more than 24 development legs on this t0-date; the lead re-dates this span (never doubled up)")
if mixed and mix + n > 12:
    sys.exit("STOP: RL-172 (a): more than 12 mixed-size development legs on this t0-date; the lead re-dates this span (never doubled up)")
PY
}
# The launch bands (EARLIEST 1794988800 Wed 00:00:00; LIMIT 1795075199 Wed 23:59:59, the t0-date (RL-172 (a)); none 10:50:01-13:14:59)
pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3; bands from this pin's own plan)
  n=$1
  if   [ "$n" -ge 1794988800 ] && [ "$n" -le 1794998099 ]; then echo 13:14-13:15   # Wed 18 Nov 00:00:00 .. Wed 18 Nov 02:34:59
  elif [ "$n" -ge 1794998100 ] && [ "$n" -le 1795027800 ]; then echo 02:00-02:35   # Wed 18 Nov 02:35:00 .. Wed 18 Nov 10:50:00
  elif [ "$n" -ge 1795036500 ] && [ "$n" -le 1795055590 ]; then echo 02:00-02:35   # Wed 18 Nov 13:15:00 .. Wed 18 Nov 18:33:10
  elif [ "$n" -ge 1795055591 ] && [ "$n" -le 1795075199 ]; then echo 13:14-13:15   # Wed 18 Nov 18:33:11 .. Wed 18 Nov 23:59:59
  else echo NONE; fi
}
NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval ($GAP s) after the prior close"; exit 1; }
ARG="$(pick_arg "$NOW")"
test "$ARG" != NONE || { echo "STOP: no admitted launch band now (outside this item's window, or inside 10:50-13:15 where this pin cannot launch); mail the lead"; exit 1; }
export ARG; echo "ARG $ARG (RL-171 §3: 02:00-02:35 where this pin's own plan admits the t0, else the data-only 13:14-13:15)"
echo "SPAN $SPAN LEGS $LEGS"
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"   # the watchdog's fence root (fence + launch spec only)
"$PY" -B -c 'from pathlib import Path; import subprocess; from joulewise.align.apple import v4_registration as r; root=Path.cwd(); head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(); print(r.verify_r1_executed_sources(root,{"executed_commit":head}))'
# must print 2d347f721552fe03bdd19f113e7bad7a7c24908e

# Sol P1 and RL-172 (a): before the KIT and OUT exist, so a WAIT here is retried cleanly at the next activation
effective_close || { echo "STOP: the receipt census failed; mail the lead"; exit 1; }
copy_gate || exit 1
day_gate || exit 1
pred_gate || exit 1     # RL-173 D.2
expiry_gate || exit 1   # RL-173 D.5
# The kit: from `fecaf73f3` (branch align/2026-11-14-dev04-05-kits), OUTSIDE the checkout, sha asserted
mkdir -p /Users/edr/campaign-out/kits
KIT=/Users/edr/campaign-out/kits/cl-dev-05.v1.1-fecaf73f3-${SPAN#dev-05-}.json
test ! -e "$KIT" || echo "KIT exists from an earlier Start of this item (a WAIT retry): re-written from git below, sha asserted"
git -C /Users/edr/code/JouleWise show fecaf73f3579756c6e735f6a9cc74aab011d293a:docs/process/cadence/kits/cl-dev-05.v1.1.json > "$KIT"
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = 2747381bf1169471d929d1e91510f7d272ff9cbc973da2c99f11673bea53ca1a || { echo "STOP: kit sha"; exit 1; }
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG"
# must print ok true, campaign_id cl-dev-05, frozen_commit 2d347f721552fe03bdd19f113e7bad7a7c24908e, frozen_paths_verified true,
# kit_sha256 2747381bf1169471d929d1e91510f7d272ff9cbc973da2c99f11673bea53ca1a, legs 12

# The queue: committed bytes on the audit branch, sha asserted
git -C /Users/edr/code/JouleWise fetch origin audit/2026-11-10-fable
QCOMMIT=b7a0d98822865a01e67fc3cc1833c9b186be2181
test "$(git -C /Users/edr/code/JouleWise show "$QCOMMIT":docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-dev-05-2d347f721.json | shasum -a 256 | cut -c1-64)" = 391f438281af05fece9866ec532e7fdb4b0f478b297e403bd99da6153e2fafbb || { echo "STOP: queue sha"; exit 1; }

# Output root outside every v4 registration and custody root
OUT=/Users/edr/campaign-out/cl-dev-05/cq-${SPAN}-a1-$("$PY" -B -c 'import time; print(time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))')
test ! -e "$OUT" || { echo "STOP: OUT exists"; exit 1; }
case "$OUT" in */restricted/*|*/night-*|*/jw-b5-*|"$REPO"/*|*/configs/campaigns/align_v4*) echo "REFUSE OUT"; exit 1;; esac

# measurement_mode (RL-149 §2.4 campaign-scope stop; RL-150 §2 F5): record every FAIL/WARN line
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify; echo "verify rc $?"
# RULE (lead, RL-150 F5 line): proceed only if every FAIL line is the "agent process present" line and every PID it names is
# in MAGISTRATE_PID's own process tree (record the lines); ANY other FAIL line: STOP, mail the lead. WARN lines are recorded, not gates.
sudo -n systemsetup -getusingnetworktime                 # must say Off
# RL-172 (h): the OS daily batch time computed from the boot time (boot + 12 h + 48 s, then every 24 h). PRINT ONLY: it gates nothing
BOOT="$(sysctl -n kern.boottime | sed -E 's/^\{ sec = ([0-9]+),.*$/\1/')"
case "$BOOT" in
  ''|*[!0-9]*) echo "batch print: kern.boottime unreadable";;
  *) NEXT_BATCH=$((BOOT + 43248)); while [ "$NEXT_BATCH" -le "$(date +%s)" ]; do NEXT_BATCH=$((NEXT_BATCH + 86400)); done
     echo "boot $(date -r "$BOOT" '+%Y-%m-%d %H:%M:%S %Z'); next OS batch $(date -r "$NEXT_BATCH" '+%Y-%m-%d %H:%M:%S %Z') (boot + 12 h + 48 s + whole days)";;
esac      # record this line in the arm record
# kernel frequency word: read it as item 308 did; must be 0 (else item 251's remedy, then re-read)
{ test ! -e /Users/Shared/JouleWise/host-power/high-power.marker && test ! -L /Users/Shared/JouleWise/host-power/high-power.marker; } || { echo "STOP: High Power marker"; exit 1; }
lsof -- /Users/Shared/JouleWise/host-power/night.lock 2>/dev/null && { echo "STOP: night.lock has a holder"; exit 1; } || echo "night.lock: no holder"
test ! -e "$CUSTODY/desk_fence.json" || { cat "$CUSTODY/desk_fence.json"; echo "STOP: live fence"; exit 1; }
sudo -n -l /bin/kill >/dev/null; echo "sudo kill rc $?"  # must be 0
pgrep -fl 'b6_r12|r12' || echo "no r12"
pgrep -fl 'claude|codex|mcp-server|mcp_server|modelcontextprotocol' | grep -v "^$MAGISTRATE_PID " || echo "no other agent"
pgrep -fl 'km003c_monitor.py|hazard_monitor.py' || echo "no stray monitor"
pgrep -u root -fl powermetrics || echo "no root powermetrics"
launchctl list | grep -E 'com\.joulewise\.(night|align-r0)' || echo "no night/smoke agent"
pmset -g | grep -i powermode                              # 0
"$PY" -B scripts/launch_align_r0.py preflight --disk-path "$REPO"     # ac_power true

# The plan (record it whole; batch_windows must be ["$ARG"]; runner_kind cadence-legs-v1.1)
"$PY" -B scripts/cadence_legs_runner.py plan --kit "$KIT" --legs "$LEGS" --batch-window "$ARG"
# L001 (10000, own, first leg: its capture is the span's reference) 1156; L002 (2000, span, consume) 1467; L003 (19458, span, consume) 1642; L004 (2000, own) 1076; L005 (19458, span, consume) 1642; L006 (10000, span, consume) 1547;
#   $EXPECT; blackout_clear true
DEADLINE="$("$PY" -B -c 'import time; print(time.time()+'"$DEADLINE_S"')')"
```

NOTE 1 and NOTE 2 as in item 321 and the dev-03 items (ADOPTED by the lead): the measurement_mode agent-line rule above, and the watchdog's fence root with all campaign data under OUT.

**Run (your last action):**

```sh
# HOST GATE, immediately before the launch (P1-1). This is separate from the campaign dependency above: it reads the
# latest close of ANYTHING on this host (campaign span, Part C or F0, slot session, W1), not only this item's predecessor.
: "${HOST_RESTORE_OK:?Set to 1 only if the Check of the latest close of anything on this host reported every restore line OK}"
: "${OTHER_CLOSE_EPOCH:?Set to the close epoch (whole seconds, rounded up) of the latest run whose receipt is outside campaign-out and jw-wt/*/.desk (a slot session or W1), or an explicit 0}"
test "$HOST_RESTORE_OK" = 1 || { echo "STOP: the latest close's restore is not proven (restore unproven holds everything); mail the lead"; exit 1; }
test ! -e "$CUSTODY/desk_fence.json" || { echo "STOP: a desk fence is up"; exit 1; }
launchctl list | grep -qE 'com\.joulewise\.(night|align-r0)' && { echo "STOP: a night or smoke agent is loaded"; exit 1; }
{ test ! -e /Users/Shared/JouleWise/host-power/high-power.marker && test ! -L /Users/Shared/JouleWise/host-power/high-power.marker; } || { echo "STOP: High Power marker"; exit 1; }
case "${OTHER_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo "STOP: OTHER_CLOSE_EPOCH must be a whole epoch (rounded up) or an explicit 0"; exit 1;; esac
# The receipt census: every runner_receipt.json at depth <= 4 under both roots, fractional recorded close epochs, ROUNDED UP.
# Any lookup error, a missing root, or no receipt at all STOPS: missing evidence never becomes 0 (Sol re-check 2, 3).
effective_close || { echo "STOP: the receipt census failed; missing evidence stops the launch; mail the lead"; exit 1; }
HOST_LAST_CLOSE=$EFF_EPOCH    # the effective close (max of the census and OTHER_CLOSE_EPOCH), computed once (Sol confirm P1)
echo "host last close $HOST_LAST_CLOSE"
copy_gate || exit 1
day_gate || exit 1
pred_gate || exit 1     # RL-173 D.2
expiry_gate || exit 1   # RL-173 D.5
test "$(date +%s)" -ge $((HOST_LAST_CLOSE + GAP)) || { echo "WAIT: close interval ($GAP s) after the latest close of anything on this host (RL-171 §6.1)"; exit 1; }
# R1 RESERVATION, fresh at the launch (RL-165 §7; RL-155 R-A; P1-2). Re-read the staged items and RUN_STATE now.
: "${SESSION_READY:?Set to yes if the lead has recorded a v4 session (R1 or W1) as READY, else no (RL-172 (f))}"
test "$SESSION_READY" = no || { echo "CEDE: a READY v4 session takes the next clean close (RL-172 (f); RL-155 R-A); do not launch; mail the lead"; exit 1; }
# RL-172 (f): RL-165 §7's worst-case reservation (launch + worst + 1,200 s <= SESSION_T0) is retired.
# The window and the campaign dependency, last of all
expiry_gate || exit 1; watch_gate || exit 1   # RL-173 D.5 and C 5, last before the launch
NOW=$(date +%s); test "$(pick_arg "$NOW")" = "$ARG" \
  || { echo "STOP: the clock left ARG $ARG's band (or this item's window) since Start and check; do not launch; mail the lead (a re-issue or a re-plan): the argument chosen in Start and check no longer belongs to the launch time"; exit 1; }
test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval after the prior close"; exit 1; }
"$PY" -B scripts/launch_cadence_span.py launch \
  --repo "$REPO" --python-bin "$PY" \
  --kit "$KIT" --legs "$LEGS" --batch-window "$ARG" \
  --output "$OUT" --disk-path "$REPO" \
  --custody-root "$CUSTODY" --magistrate-pid "$MAGISTRATE_PID" \
  --deadline "$DEADLINE" --exit-wait-seconds 180 --start-wait-seconds 30
echo "$OUT"
```

Require exit 0, `"next": "exit the magistrate session now"` with a claimed fence (fence `pid` ≠ `MAGISTRATE_PID`), and the launch output's `plan.batch_windows` equal to `["$ARG"]`, the argument chosen in Start and check (else report it; the span is not counted until the lead rules). The launcher itself refuses a fence end (worst case + 1,460 s) that passes ten minutes before the window in `--batch-window` (01:50 for `02:00-02:35`, 13:04 for `13:14-13:15`), a t0 strictly between 10:50 and 13:15 under either argument, a deadline under the plan's worst case plus reserves, a missing kit and a missing `--batch-window`. Record the pred_gate line (RL-173 D.2), the expiry line (D.5), ARG, LAST_CLOSE_KIND, GAP, the journal-copy line (plan id and marker content), the day_gate line, the batch-time print, SPAN, LEGS, PRIOR_CLOSE_EPOCH, PY, MAGISTRATE_PID, KIT and its sha256, the queue commit and sha, OUT, DEADLINE, HOST_RESTORE_OK, OTHER_CLOSE_EPOCH, the host last close printed, SESSION_READY, the launch time, the measurement_mode lines and the plan in your RUN_STATE item and in `/Users/edr/night-custody/magistrate/cadence-${SPAN}-out-<activation>.txt`. Then exit at once, with no other `claude` or `codex` process running.

**Check (next activation, after the fence is gone):**

**Maintenance line first (RL-171 §5 item 1; as item 331). Print only: it gates nothing and is not a stop.** Set `ARG` to the batch-window argument recorded at the arm (`export ARG=...`); the receipt assert below compares with it. Then one read-only system-log query over the span's interval (from OUT's UTC launch stamp to the receipt's mtime) for the OS maintenance processes, saved BESIDE the journals as `$OUT/maintenance-log.txt`, plus a per-10-minute count printed for the report. Report the counts and which legs' intervals they overlap (from each `leg_summary.json`'s start and end, if present; else say "overlap left to the desk"). A leg hit by a maintenance job is judged by rule 5 as before (RL-171 §2 item 2). With `13:14-13:15` a leg may run through 02:00-02:35 (dasd about 02:08; XProtect to about 02:28): that is the case rule 5 exists for (one redo of about 21 min, quota 2).

```sh
: "${ARG:?Set ARG to the batch-window argument recorded at the arm}"; export ARG
START_UTC="$(basename "$OUT" | sed -E 's/.*-([0-9]{8}T[0-9]{6}Z)$/\1/')"
START_LOCAL="$("$PY" -B -c 'import sys,datetime as d; t=d.datetime.strptime(sys.argv[1],"%Y%m%dT%H%M%SZ").replace(tzinfo=d.timezone.utc); print(t.astimezone().strftime("%Y-%m-%d %H:%M:%S"))' "$START_UTC")"
END_LOCAL="$(date -r "$(stat -f %m "$OUT/runner_receipt.json")" '+%Y-%m-%d %H:%M:%S')"
echo "maintenance window $START_LOCAL .. $END_LOCAL"
sudo -n /usr/bin/log show --style compact --start "$START_LOCAL" --end "$END_LOCAL" \
  --predicate 'process IN {"dasd","XProtect","XprotectService","XProtectPluginService","mds","mds_stores","mdworker","mdworker_shared","backupd","softwareupdated","mobileassetd"}' \
  > "$OUT/maintenance-log.txt" 2>"$OUT/maintenance-log.err"; echo "log show rc $?"
wc -l < "$OUT/maintenance-log.txt"
# per 10-minute bucket and process: "HH:M0 process count"
awk '{ if ($2 ~ /^[0-9][0-9]:[0-9][0-9]/) { b=substr($2,1,4) "0"; for (i=3;i<=NF;i++) if ($i ~ /\[[0-9]+:/) { split($i,a,"["); p=a[1]; break } ; c[b" "p]++ } } END { for (k in c) print k, c[k] }' "$OUT/maintenance-log.txt" | sort
```

The Check proper:

```sh
"$PY" -B - "$OUT" "$LEGS" <<'PY'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1]); roster = sys.argv[2].split(",")
r = json.loads((root / "runner_receipt.json").read_text())
print(json.dumps({k: r.get(k) for k in ("rc", "runner_kind", "roster", "batch_windows", "legs_planned",
                                        "legs_finished", "load_redos_used", "span_result", "meter", "error")},
                 sort_keys=True))
print([(s["name"], s["rc"]) for s in r["steps"]])
assert r["runner_kind"] == "cadence-legs-v1.1" and r["roster"] == roster
assert r["kit"]["sha256"] == "2747381bf1169471d929d1e91510f7d272ff9cbc973da2c99f11673bea53ca1a"
assert r["kit"]["frozen_commit"] == "2d347f721552fe03bdd19f113e7bad7a7c24908e" and r["kit"]["campaign_id"] == "cl-dev-05"
assert r["batch_windows"] == [__import__("os").environ["ARG"]], r["batch_windows"]   # ARG as recorded at the arm (RL-171)
assert r.get("mock") in (False, None)
names = [s["name"] for s in r["steps"]]
assert names.count("soak") == 1 and names.count("frozen") == 1
assert all(s["rc"] == 0 for s in r["steps"] if s["name"] in ("frozen", "condition13", "read_power", "soak", "restore"))
for name, feed in r["feeds"].items():
    assert feed["stop"]["proven_stopped"]
    if name == "meter":
        continue   # RL-150 R8: only the runner hashes KM003C stream files; the magistrate does not open them
    for f in feed["files"]:
        with (root / f["path"]).open("rb") as h:
            assert hashlib.file_digest(h, "sha256").hexdigest() == f["sha256"]
bundle = root / "desk-bundle"
files = sorted(p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file())
assert files == [f"legs/{x}/leg_summary.json" for x in roster] + ["span/meter.json", "span/result.json"], files
for leg in roster:
    s = json.loads((bundle / "legs" / leg / "leg_summary.json").read_text())
    print(leg, "admitted", s.get("admitted"), "g0_role", s.get("g0_role"), "g0_outcome", s.get("g0_outcome"),
          "g0_s", s.get("g0_s"), "span_reference", json.dumps(s.get("span_reference"), sort_keys=True))
    print(leg, json.dumps(s, sort_keys=True))
print("result", (bundle / "span/result.json").read_text().strip())
print("meter", (bundle / "span/meter.json").read_text().strip())
print("RECEIPT OK" if r["rc"] == 0 and r["legs_finished"] == len(roster) else "RECEIPT NOT CLEAN: report in full")
PY
# RL-150 R1 part 3 print with RL-158 Q1's span-reference lines (gates nothing; thermal journal values and leg records only):
# the soak reference; the first leg's capture (its own outputs/align_window_reference.json); for every leg its G0 shape,
# role, outcome and wait, the reference source the runner verified, and its G0 release reading (TV0h, TV1h, Tf08).
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

test ! -e "$CUSTODY/desk_fence.json"; launchctl list | grep -c 'com.joulewise.align-r0' || true   # expect 0
pmset -g | grep -i powermode                                            # 0
sudo -n systemsetup -getusingnetworktime                                # Off
# kernel frequency word: 0 (item 251 remedy if not)
test ! -e /Users/Shared/JouleWise/host-power/high-power.marker
pgrep -fl 'km003c_monitor.py|hazard_monitor.py' || echo "no stray monitor"
pgrep -u root -fl powermetrics || echo "no root powermetrics"
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify; echo "verify rc $?"   # record lines (NOTE 1 applies)
```

The receipt also carries the runner's own close steps (`restore`, `stop-*`, `close-*`); report them as the restore lines. Do not open `hazards/`, any `stream-*.jsonl`, any `powermetrics*` file or any `align_episode.json`.

**Report** (by email to Ed and the lead, and as RUN_STATE <LEAD FILLS: the next RUN_STATE Check item number at issue>):
- SPAN and LEGS; the ARG used; the maintenance line's counts and the legs they overlap;
- the receipt line, the step list and RECEIPT OK (or the receipt in full if not clean);
- each leg's `leg_summary.json` line, with `admitted`, `g0_role`, `g0_outcome`, `g0_s` and `span_reference` called out per leg;
- each consumer's G0 outcome against L001's capture (released or timed out), and the count released;
- `span/result.json` and `span/meter.json`;
- legs run and admitted (of 6); for any excluded leg, the inclusion rule it fell under; whether any named stop would fire (LEG_OVERTIME is two legs over 1.5 x their own budget; a missing L001 reference is a REFUSAL that stops the span, RL-158 Q3);
- the RL-150 R1 / RL-158 Q1 print above, as printed;
- the restore lines and the measurement_mode verify lines; the receipt's close epoch;
- whether the span crossed 00:00 (the `/private/tmp` walk; not a gate).

The magistrate reports; it never decides. Commit nothing from `$OUT`. Nothing is re-run and nothing else is queued.

**After (the lead, at the desk; not the magistrate).**
- **The Air desk (Mythos #788 delta D1; dev-04/05 F8):** from the checkout at `2d347f721` (or `1b20d3b0e`), with the kit; never a checkout at `b4b6aeb19`, `main` or the hp-01 line. Copy the bundle to `/Volumes/JW-EXT/cadence-desk/cq-dev-05-s01-a1/input`.
- **The hand-read print of every v1.1 span (RL-158 Q1):** the soak reference, L001's capture, and each consumer's release reading and G0 wait. Mark "reference from a redo" or "from an excluded leg" from the receipt's `span_reference` (RL-158 Q2; RL-161 §4).
- **The realized consumer count (RL-158 Q6):** consumers released over the block; it goes in the ledger row. A block that ends with fewer than four released consumers comes to the research lead (RL-158 Q6); nothing stops on that.
- This desk must be FINAL before campaign span 15 arms (line 9). **Next:** `dev-05-s02` arms at this close + the close interval on its own item. Ledger: `dev-05` READY to RUNNING.
