TBD. **Laptop lead (interactive, Opus 5.5), drafted by the items-rl165 drafter 2026-11-14 PST and re-drafted under RL-171 by the items-rl171 builder 2026-11-15 PST, ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm the REST of block dev-03 (RL-158 §2, §3; RL-161 §4; RL-165 §1), kit `cl-dev-03.v1.1` (sha256 `0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b`), runner kind `cadence-legs-v1.1`, on `2d347f721552fe03bdd19f113e7bad7a7c24908e` checked out detached in a fresh scratch worktree. **The roster is L004-L012 (span `dev-03-s02`, nine legs) at every launch time.** RL-171 §3's argument route admits nine legs at every t0 outside 10:50-13:15, so RL-161's 3 + 3 + 6 alternate, which existed only for the 01:50 fence, is not used: `dev-03-s02b` and `dev-03-s03b` are WITHDRAWN UNARMED by this arm record. One span: a fresh soak, then the roster's legs at their cells (L004 captures the span's reference; on nine legs L008, L009, L010 and L012 consume it), decode cap 4,096, Automatic, band q0. They are counted development legs of dev-03. No other span, no queue extension, no session, no W1. EARLIEST: the close interval (RL-171 §6.1) after the dev-03 pilot closed with its fence gone, and only once the lead's hand-read is recorded with L002's G0 released (this item is issued only then); not before 00:00:00 PST Mon 16 Nov (epoch 1794816000; this block's t0-date, RL-172 (a)). LAUNCH as soon as every gate holds, at any hour up to 23:59:59 PST Mon 16 Nov (LIMIT, epoch 1794902399; this block's t0-date, RL-172 (a)), except 10:50:00-13:15:00 (the pin's `fence_problems` refuses it under either argument). The batch-window argument follows the launch time (RL-171 §3): `02:00-02:35` from 02:35:00 to 10:50:00 and from 13:15:00 to 16:18:10; `13:14-13:15` from 16:18:11 to 02:34:59. ISSUED AHEAD (RL-173 D): this item names its predecessor `dev-03-s01` and requires that span's clean close receipt, else it is VOID and is not skipped; it EXPIRES 24 h after issue, so its window ends at the earlier of LIMIT and the expiry. The launch is your LAST action and you exit at once. If you cannot, do not launch; mail the lead (the standing F0 item then applies).**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-17T10:32:00-08:00
on_early_or_refused: VOID, so that nothing of this item ever launches (mail the lead; a new item is needed), if `dev-03-s01` closed without a clean receipt (RL-173 D.2) or once 24 h have passed since the issue (RL-173 D.5). Otherwise: any failed line of "Start and check", any launch refusal (rc≠0 or no claimed fence), or a launch that cannot happen inside the bands below (Mon 00:00:00 to Mon 23:59:59 PST, outside 10:50:00-13:15:00): NOTHING of this item launches; mail the lead; a later t0 needs a new item, and the standing F0 item applies meanwhile. A span that ran but ends with any named stop or a receipt rc≠0: nothing relaunches, nothing is re-run, nothing else is queued; mail the lead. Do not retry, do not extend, do not reuse OUT
next_observable: the next activation (after the fence is gone) runs "Check" below and reports, by email to Ed and the lead and as RUN_STATE TBD+1: the receipt asserts, the per-leg admitted lines with g0_role and span_reference, the desk bundle, the restore lines, measurement_mode verify again, and the RL-150 R1 / RL-158 Q1 print (gates nothing)
```

- **Issued ahead (RL-173 D; the interim until #800 is admitted; items-1115 builder, Sun 15 Nov 2026 PST).** (1) At most three counted spans are issued ahead of the machine, plus the standing F0. (2) **Predecessor: `dev-03-s01`** (the dev-03 pilot). This item requires its clean close receipt: `pred_gate` below reads its `runner_receipt.json` (rc, error, roster, leg counts, span_result, close steps, close time) and its desk bundle's `leg_summary.json` files (wall against budget, contaminated redos), never an energy, power or meter value. No receipt yet is WAIT. A receipt that is not clean makes this item VOID: it is not skipped, nothing launches on its authority, and the lead decides. (3) Its date window is Mon 16 Nov (RL-172 (a)), and its own argument choice is `pick_arg` below. (4) Nothing is issued past a class A hand-read or an L002 or L005 gate. **Not issuable ahead:** it is issued only after the lead's hand-read records the pilot's R9 PASSED and its class A smoke MET (L002 released its G0), RL-173 D.4. (5) It expires 24 h after issue: `expiry_gate` (ISSUED_EPOCH + 86,400 s) runs in Start and check and again just before the launch.
- **Why (RL-165 §1; RL-158 §3; RL-171).** The remainder arms once the hand-read is recorded and L002 released. RL-165 §1 gave it Monday before 10:50 or 13:15-16:18:10, and after 16:18:10 the 3 + 3 + 6 alternate or nine legs at Tue 02:40. RL-171 retires the 01:50 fence and the 02:40 start, and the pin's fence check is met by the argument `13:14-13:15` after 16:18:10 (RL-171 §3), so **nine legs arm at the first t0 outside 10:50-13:15**. dev-03's remainder stays one span of nine (RL-158 §3: an exception to "at most six", which keeps 5 of 10 consumers and saves a soak; RL-171 §6.4 favours the longer span). A leg's calendar day is the local date of its span's t0.
- **Gate (RL-158 §2; RL-161 §2).**
  - The pilot (`dev-03-s01`) closed and checked: <LEAD FILLS: RUN_STATE <n>: RECEIPT OK, legs run and admitted of 3, no named stop open, restore lines clean, close epoch>.
  - **R9 (pilot) recorded as PASSED:** <LEAD FILLS: admitted count, any excluded leg and its rule, hand table and desk agree (inclusion included); where recorded>. R9's own allowance stands: two of three admitted passes when the one exclusion fell under rule 2 or 5 and its other conditions hold (RL-150 R9). This item needs R9 PASSED and the smoke line MET (below), not three admitted legs.
  - **The class A smoke line, recorded separately:** <LEAD FILLS: "L002 released its G0 against L001's capture in <g0_wait_s> s and ran its turn: MET"; with Q1's print attached; any MARK (reference from a redo / from an excluded leg)>. **If L002 timed out at G0, this item is NOT issued** (RL-165 §4, below).
  - Lines 5, 6, 7 and 9 at the arm; the remainder's queue entry appended after the hand-read and committed (line 3).
- **RL-165 §4: the two contingencies, decided now.**
  - **L002 timed out at G0:** nothing span-shaped arms until the research lead rules: not this remainder, not dev-04 or dev-05 on v1.1. The machine goes straight to the ladder: the slot session if READY, hp-01's unrun spans, then the standing F0. Q1's print goes to the research lead. Own-shaped legs may arm without the research lead: dev-03's L004-L012 on `cl-dev-03.v1.1a` (pin `1b20d3b0e`, kit `4bf7f294…d133`; Air `plan` at `1b20d3b0e`: expected 13,599 s, worst 32,850 s, the same window as nine legs here), by its own item, only if a cold seat has confirmed its cells and seeds equal v1.1's leg for leg and its line 2 holds (RL-165 §5). If they are not equal, that comes to the research lead. dev-04 and dev-05 then need the builder's own-shaped kits.
  - **dev-04's L005 times out at G0 (RL-163 §6 as amended):** if dev-03 ended with at least four of its consumers released, dev-04's second span arms on the lead's record; if fewer than four, it does not, and dev-04's L007-L012 and dev-05 run own-shaped. This span's consumer count therefore goes in its hand-read (After).
- **Day law (RL-172 (a), which replaces the two-starts default):** a day is the local date of a span's t0. No t0-date holds more than 12 mixed-size development legs (dev-03, dev-04, dev-05) or more than 24 development legs; qualification t0-dates are disjoint from development t0-dates; hp-01, F0, F2 and v4 sessions are outside the count. **This span's t0-date is Mon 16 Nov** (dev-03, 12 mixed-size legs over the pilot and this remainder); this item's window admits only that date. A span that misses its date is re-dated by the lead with a new item, never doubled up. Planned: Sat 7, Sun 11, Mon 18 (dev-02-s03 and dev-03), Tue 12 (dev-04), Wed 12 (dev-05). Because the queue does not yet enforce dates, `day_gate` counts the development legs already launched on the t0-date from their receipts and refuses this span past either cap; the committed queues' `not_before` values are lower bounds only.
- **Counted.** The legs count as development legs of dev-03 under the kit's inclusion rules (RL-149 §2.3, §2.4 as amended by RL-150 R7 and R8; rule 2 against the reference the leg's shape names). A chosen cut lands on an own-shaped leg (RL-161 §1); nine legs in one span make no cut. An excluded leg is refilled only from the reserve under RL-149 §2.4. A re-run is a new span with `attempt` + 1 and `rerun_of`, and it needs a ruling.
- **Queue.** `QUEUE-cl-dev-03-2d347f721-append-both.json`: the committed pilot queue with three spans appended, additions only: `dev-03-s02` (L004-L012), `dev-03-s02b` (L004-L006) and `dev-03-s03b` (L007-L012), the last two `rerun_of: dev-03-s02` because the closed schema has no withdrawn field. Only `dev-03-s02` runs; `dev-03-s02b` and `dev-03-s03b` are WITHDRAWN UNARMED by this arm record (RL-171 removes the reason for 3 + 3 + 6). Do not run `cadence_queue.py next`.
- **Bytes, CI and condition 13:** as the pilot's item (the same kit file and pin): kit `cl-dev-03.v1.1.json` from `9cbb365a6`, sha `0f535774…e14b`, frozen at `2d347f721` (38 paths); line 2 in RL-165 §5's four parts (arm-record line 2); `verify_r1_executed_sources` must return the full sha. Same bytes as the pilot, so no smoke of its own: the pilot was the class A smoke.
- **Timing.** Plans at `2d347f721` with both arguments (blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-dev03-s02.txt`):
  - Nine legs, L004-L012: expected 15,163 s (4.2 h), worst case 32,850 s (9.1 h); fence deadline launch + 34,310 s.
  - **Bands (RL-171 §3; the `pick_arg` function below), on Mon 16 Nov:** 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-16:18:10 `02:00-02:35`; 16:18:11-02:34:59 `13:14-13:15` (which admits nine legs up to 03:32:10). Checked: with `02:00-02:35` 16:18:10 accepted and 16:18:11 refused; with `13:14-13:15` 03:32:10 accepted and 03:32:11 refused; 10:50:01 refused under either. A mock span at t0 Mon 00:30 with `13:14-13:15` (L006-L008 across 02:00-02:35): rc 0, 9 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/dev03-s02-alt-00:30/`).
  - Forecast t0 Mon 05:19:40 (the pilot's expected close 04:59:40 + a 20-min hand-read), argument `02:00-02:35`: expected end 09:32:23, worst end 14:27:10, fence end 14:51:30.
  - If the hand-read ends inside 10:50-13:15, the nine legs arm from 13:15.
  - Pointer deadline = latest fence end (LIMIT + 34,310 s = Tue 09:31:49) + 1 h.
- **Conditions, blinding and the High Power marker:** as the pilot's item, with `--legs "$LEGS"` written out and `--batch-window "$ARG"` on every `validate-kit`, `plan` and `launch` (chosen once in Start and check by the launch time, re-checked in Run; RL-171 §3); output root `/Users/edr/campaign-out/cl-dev-03/`.
- **May run:** this span, once, nine legs. **May NOT:** `dev-03-s02b`, `dev-03-s03b`, dev-04, dev-05, any session, W1, any filler while this span is armed.

- **Host gate and R1 reservation, immediately before the launch (Sol items review P1-1, P1-2; RL-155 R-B; RL-165 §7).** Separate from this item's campaign dependency: the Check of the latest close of ANYTHING on this host (any span, Part C or F0, slot session or W1) reported every restore line OK; no desk fence; no night or smoke agent loaded; no High Power marker; at least GAP seconds since that latest close (RL-171 §6.1, amending RL-155 R-B's 20 minutes: GAP is QUIET_CAMPAIGN_S after a campaign span's close, 300 s, confirmed by RL-172 §0; GAP is 1,200 s after a Part C or F0, F2, a slot session or W1) (the newest `runner_receipt.json` under `/Users/edr/campaign-out` and `/Users/edr/code/jw-wt`, from a census that stops on a missing root, any lookup error or an empty result, with fractional recorded close epochs rounded up; or a session's close given as OTHER_CLOSE_EPOCH, a whole epoch or an explicit 0); and, after a CAMPAIGN close, that close's journal copy complete and hash-verified, shown by the marker `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok`, written only after the copy is verified (by the lead's Air copy, or by the MBP's own verified encrypted cloud offload, items 347 and 348, which RL-173 A makes the off-host copy permanently; a failed or unverified offload writes no marker and holds the arm, RL-173 A 7) (Sol items-rl171 P1; a missing marker is WAIT; no SSH once a span is armed). Read fresh at the launch: if a v4 slot session is READY and staged for this slot, this span cedes; RL-172 (f) retires RL-165 §7's worst-case reservation: from the lead's record that a v4 session is READY nothing of lower priority arms, and the session takes the next clean close; before that record this span arms as usual.

**RL-149 §2.8 arm-record lines (record each, with its evidence):**
1. As the pilot's line 1 (kit `0f535774…e14b`; row-1 ADMIT at `17f478675`; Mythos first seat at `4c38dce3b` and delta seat ADMIT at `5b8d23727`; RL-161 §3's F7 table, with the stop sentence carried; F11 by hand).
2. As the pilot's line 2 (RL-165 §5's four parts; CI run 43664825578 on `9cbb365a6`: CI `ci` run 43664825578 on `9cbb365a6` COMPLETED 2026-11-14 20:47:37 PST, conclusion **failure** (9 of 12 `test` shards red; every other job success). Shard 11 was not stalled: it finished at 3 h because `tests.test_bytes_analysis` took 9,107 s and passed. The final red set is **exactly the 12 tests of `fe907d0d3`'s CI 43600776368, test for test, with no added red** (both sets re-derived from the job logs by the items-1115 builder, Sun 15 Nov 15:03 PST; evidence/align-v4-campaign/item-drafts-1115/evidence/line2-dev03-red-9cbb365a6.txt and line2-base-red-fe907d0d3.txt); D2: `test_kit_v11` 0 skipped in shard 7).
3. Queue `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-dev-03-2d347f721-append-both.json` on audit/2026-11-10-fable at `b7a0d9882` (`b7a0d98822865a01e67fc3cc1833c9b186be2181`; committed Sun 15 Nov 00:22 PST, before the hand-read: see the items-1115 STATUS note on RL-161 §2), sha256 `366662cecb9794b9d13dbc67dd5721acd2bdf00b5055cc8df70861c07b593fbb` (the items-rl171 copy: `dev-03-s03b`'s not_before moved from 2026-11-17 to 2026-11-16, nothing else; `validate-queue` ok, `/Volumes/JW-EXT/scratch/items-rl171/queue/validate-queue.log`) (`validate-queue` ok at `2d347f721` with `--kits-root` the #788 head checkout: plan ids `cq-dev-03-s01-a1`, `cq-dev-03-s02-a1`, `cq-dev-03-s02b-a1`, `cq-dev-03-s03b-a1`; `/Volumes/JW-EXT/scratch/items-rl165/evidence/validate-queue-dev03.log`). Its text up to the pilot span is the committed pilot queue's (sha `403e53f9…7da2`). `expires_at` 2026-11-21T23:59-08:00.
4. `validate-kit` passes; OUT is outside every v4 registration and custody root (check below).
5. The per-span checks of design doc §4 and §14 pass at the arm and at the close. Do NOT run `cadence_queue.py checklist` or `next`.
6. No named stop, veto or halt open (the `directive` and `cadence-stop` issues; gh via `launchctl asuser`). By hand: no named stop open from the pilot or any earlier span, no RESTORE_UNPROVEN and no High Power `revoked` hold: <LEAD FILLS: span ids, their desk `stops.json` result and the time read>.
7. Results-ref watcher live within 24 h (RL-173 C 5: one observation under 24 h old may serve more than one arm; `watch_gate` re-checks WATCH_UNTIL_EPOCH at this arm; a GitHub Actions watcher meeting RL-173 C 1-4 may stand instead, by a re-issue that reads its latest completed run): <LEAD FILLS: heartbeat stamp, pid and commit>.
8. The pilot's R9 verdict is PASSED (two of three admitted allowed under R9) and the class A smoke is MET (Gate above): <LEAD FILLS: both lines and where recorded>.
9. Line 9, across blocks in run order (RL-165 §6). Expected: this span is campaign span 10 (9 = the dev-03 pilot), so span 8's desk (expected `dev-02-s03`, or `dev-02-s01` if Sunday's pull did not run) must be FINAL. As run: this span is campaign span <LEAD FILLS: N>, and the desk of the span two back, <LEAD FILLS: SPAN ID>, is FINAL: <LEAD FILLS: the desk's stamp and where it is recorded>.

**Start and check (while you are still alive).** From a FRESH scratch worktree detached at the full sha (NOT the canonical clone's checkout, not a dev-01, dev-02 or hp-01 worktree), own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONPATH=.:tests`, `python3.13 -B -m unittest`, one module at a time; all must be OK: `tests.cadence.test_kit_v11`, `tests.cadence.test_span_reference`, `tests.cadence.test_legs_runner`, `tests.cadence.test_kit`, `tests.cadence.test_stops_desk`, `tests.cadence.test_runner_guards`, `tests.cadence.test_launch_cadence_span`, `tests.align.test_r1_smoke_launcher`. (At `2d347f721` the kit files are not in the tree, so `test_kit_v11`'s four committed-kit tests skip; they ran with 0 skips in CI shard 7, line 2 D2. The armed kit is checked by `validate-kit` below.) Any failure: nothing launches; mail the lead.

```sh
git -C /Users/edr/code/JouleWise fetch origin align/2026-11-14-kit-v1-1
test -e /Users/edr/code/jw-wt/cadence-dev03-rest || git -C /Users/edr/code/JouleWise worktree add --detach /Users/edr/code/jw-wt/cadence-dev03-rest 2d347f721552fe03bdd19f113e7bad7a7c24908e   # reused on a retry after a WAIT
cd /Users/edr/code/jw-wt/cadence-dev03-rest
test "$(git rev-parse HEAD)" = 2d347f721552fe03bdd19f113e7bad7a7c24908e || { echo "STOP: HEAD"; exit 1; }
test -z "$(git status --porcelain)" || { echo "STOP: dirty tree"; exit 1; }
REPO="$PWD"
: "${PY:?Set PY to the existing pinned measurement-venv interpreter (do not resolve the symlink)}"
: "${MAGISTRATE_PID:?Set to the PID of this magistrate own claude process}"
ps -o pid=,comm= -p "$MAGISTRATE_PID"                 # must show the claude process
: "${PRIOR_CLOSE_EPOCH:?Set to the later of the dev-03 pilot runner_receipt ended.epoch_s and the epoch its fence was seen gone}"
# The roster: nine legs at every launch time (RL-171 §3; dev-03-s02b and dev-03-s03b are withdrawn unarmed)
SPAN=dev-03-s02;  LEGS=L004,L005,L006,L007,L008,L009,L010,L011,L012; DEADLINE_S=34310; WORST_S=32850; EXPECT="expected_s 15163, worst_case_s 32850"
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
PRED_SPAN=dev-03-s01; PRED_CAMP=cl-dev-03; PRED_ROSTER=L001,L002,L003
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
WATCH_UNTIL_EPOCH=<LEAD FILLS: line 7's watcher observation stamp + 86,400 s, as an epoch>
watch_gate() {
  test "$(date +%s)" -le "$WATCH_UNTIL_EPOCH" || { echo "STOP: line 7's results-watcher observation is over 24 h old (RL-173 C 5); do not launch; mail the lead"; return 1; }
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
# The launch bands (EARLIEST 1794816000 Mon 00:00:00; LIMIT 1794902399 Mon 23:59:59, the t0-date (RL-172 (a)); none 10:50:01-13:14:59)
pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3; bands from this pin's own plan)
  n=$1
  if   [ "$n" -ge 1794816000 ] && [ "$n" -le 1794825299 ]; then echo 13:14-13:15   # Mon 16 Nov 00:00:00 .. Mon 16 Nov 02:34:59
  elif [ "$n" -ge 1794825300 ] && [ "$n" -le 1794855000 ]; then echo 02:00-02:35   # Mon 16 Nov 02:35:00 .. Mon 16 Nov 10:50:00
  elif [ "$n" -ge 1794863700 ] && [ "$n" -le 1794874690 ]; then echo 02:00-02:35   # Mon 16 Nov 13:15:00 .. Mon 16 Nov 16:18:10
  elif [ "$n" -ge 1794874691 ] && [ "$n" -le 1794902399 ]; then echo 13:14-13:15   # Mon 16 Nov 16:18:11 .. Mon 16 Nov 23:59:59
  else echo NONE; fi
}
NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval ($GAP s) after the prior close"; exit 1; }
ARG="$(pick_arg "$NOW")"
test "$ARG" != NONE || { echo "STOP: no admitted launch band now (outside this item's window, or inside 10:50-13:15 where this pin cannot launch); mail the lead"; exit 1; }
export ARG; echo "ARG $ARG (RL-171 §3: 02:00-02:35 where this pin's own plan admits the t0, else the data-only 13:14-13:15)"
echo "SPAN $SPAN LEGS $LEGS"   # record it; dev-03-s02b and dev-03-s03b are withdrawn unarmed by this arm
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"   # the watchdog's fence root (fence + launch spec only)
"$PY" -B -c 'from pathlib import Path; import subprocess; from joulewise.align.apple import v4_registration as r; root=Path.cwd(); head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(); print(r.verify_r1_executed_sources(root,{"executed_commit":head}))'
# must print 2d347f721552fe03bdd19f113e7bad7a7c24908e

# Sol P1 and RL-172 (a): before the KIT and OUT exist, so a WAIT here is retried cleanly at the next activation
effective_close || { echo "STOP: the receipt census failed; mail the lead"; exit 1; }
copy_gate || exit 1
day_gate || exit 1
pred_gate || exit 1     # RL-173 D.2
expiry_gate || exit 1   # RL-173 D.5
# The kit: from PR #788's head, OUTSIDE the checkout, sha asserted
mkdir -p /Users/edr/campaign-out/kits
KIT=/Users/edr/campaign-out/kits/cl-dev-03.v1.1-9cbb365a6-${SPAN#dev-03-}.json
test ! -e "$KIT" || echo "KIT exists from an earlier Start of this item (a WAIT retry): re-written from git below, sha asserted"
git -C /Users/edr/code/JouleWise show 9cbb365a6957c3737617d8604ba6d06071ab018c:docs/process/cadence/kits/cl-dev-03.v1.1.json > "$KIT"
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = 0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b || { echo "STOP: kit sha"; exit 1; }
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG"
# must print ok true, campaign_id cl-dev-03, frozen_commit 2d347f721552fe03bdd19f113e7bad7a7c24908e, frozen_paths_verified true,
# kit_sha256 0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b, legs 12

# The queue: committed bytes on the audit branch, sha asserted
git -C /Users/edr/code/JouleWise fetch origin audit/2026-11-10-fable
QCOMMIT=b7a0d98822865a01e67fc3cc1833c9b186be2181
test "$(git -C /Users/edr/code/JouleWise show "$QCOMMIT":docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-dev-03-2d347f721-append-both.json | shasum -a 256 | cut -c1-64)" = 366662cecb9794b9d13dbc67dd5721acd2bdf00b5055cc8df70861c07b593fbb || { echo "STOP: queue sha"; exit 1; }

# Output root outside every v4 registration and custody root
OUT=/Users/edr/campaign-out/cl-dev-03/cq-${SPAN}-a1-$("$PY" -B -c 'import time; print(time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))')
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
# nine legs: L004 (10000, span, capture) 1156, L005 1076, L006 1251, L007 1156, L008 (consume) 1467, L009 (consume) 1642,
#   L010 (consume) 1467, L011 1251, L012 (consume) 1547; $EXPECT; blackout_clear true
DEADLINE="$("$PY" -B -c 'import time; print(time.time()+'"$DEADLINE_S"')')"
```

NOTE 1 and NOTE 2 as in item 321 (ADOPTED by the lead): the measurement_mode agent-line rule above, and the watchdog's fence root with all campaign data under OUT.

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

Require exit 0, `"next": "exit the magistrate session now"` with a claimed fence (fence `pid` ≠ `MAGISTRATE_PID`), and the launch output's `plan.batch_windows` equal to `["$ARG"]`, the argument chosen in Start and check (else report it; the span is not counted until the lead rules). The launcher itself refuses a fence end (worst case + 1,460 s) that passes ten minutes before the window in `--batch-window` (01:50 for `02:00-02:35`, 13:04 for `13:14-13:15`), a t0 strictly between 10:50 and 13:15 under either argument, a deadline under the plan's worst case plus reserves, a missing kit and a missing `--batch-window`. Record the pred_gate line (RL-173 D.2), the expiry line (D.5), ARG, LAST_CLOSE_KIND, GAP, the journal-copy line (plan id and marker content), the day_gate line, the batch-time print, SPAN, LEGS, PRIOR_CLOSE_EPOCH, PY, MAGISTRATE_PID, KIT and its sha256, the two spans withdrawn unarmed (`dev-03-s02b`, `dev-03-s03b`), the queue commit and sha, OUT, DEADLINE, HOST_RESTORE_OK, OTHER_CLOSE_EPOCH, the host last close printed, SESSION_READY, the launch time, the measurement_mode lines and the plan in your RUN_STATE item and in `/Users/edr/night-custody/magistrate/cadence-${SPAN}-out-<activation>.txt`. Then exit at once, with no other `claude` or `codex` process running.

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
assert r["kit"]["sha256"] == "0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b"
assert r["kit"]["frozen_commit"] == "2d347f721552fe03bdd19f113e7bad7a7c24908e" and r["kit"]["campaign_id"] == "cl-dev-03"
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

**Report** (by email to Ed and the lead, and as RUN_STATE TBD+1):
- SPAN and LEGS; the receipt line, the step list and RECEIPT OK (or the receipt in full if not clean);
- each leg's `leg_summary.json` line, with `admitted`, `g0_role`, `g0_outcome`, `g0_s` and `span_reference` called out per leg;
- each consumer's G0 outcome against L004's capture (released or timed out), and the count released;
- `span/result.json` and `span/meter.json`;
- legs run and admitted (of 9); for any excluded leg, the inclusion rule it fell under; whether any named stop would fire (LEG_OVERTIME is two legs over 1.5 x their own budget; a missing L004 reference is a REFUSAL that stops the span, RL-158 Q3);
- the RL-150 R1 / RL-158 Q1 print above, as printed;
- the restore lines and the measurement_mode verify lines; the receipt's close epoch;
- whether the span crossed 00:00 (the `/private/tmp` walk; not a gate).

The magistrate reports; it never decides. Commit nothing from `$OUT`. Nothing is re-run and nothing else is queued.

**After (the lead, at the desk; not the magistrate).**
- **The Air desk (Mythos #788 delta D1):** from the checkout at `2d347f721` (or `1b20d3b0e`), with the kit; never a checkout at `b4b6aeb19`, `main` or the hp-01 line. Copy the bundle to `/Volumes/JW-EXT/cadence-desk/cq-<SPAN>-a1/input`.
- **The hand-read print of every v1.1 span (RL-158 Q1):** the soak reference, L004's capture, and each consumer's release reading and G0 wait. Mark "reference from a redo" or "from an excluded leg" from the receipt's `span_reference` (RL-158 Q2; RL-161 §4).
- **The realized consumer count (RL-158 Q6):** consumers released over the whole block (L002 plus this span's). It goes in the ledger row. **It holds dev-04 only if dev-04's L005 times out at G0 (RL-165 §4; Sol items review P2-7):** then, at least four released, dev-04's second span arms on the lead's record; fewer than four, it does not, and dev-04's L007-L012 and dev-05 run own-shaped. If L005 releases, the count holds nothing: dev-04's second span arms on its own gates. Separately, a block that ends with fewer than four released consumers comes to the research lead (RL-158 Q6), and nothing stops on that.
- **RL-158 Q4:** revisit the 600 s span budget once, from dev-03's consumers' G0 waits; a change only if the expected times were off by more than 20 minutes a span (a change means a new pin).
- This desk must be FINAL before campaign span 12 arms (expected: dev-04's second span). **Next (RL-165 §1; RL-158 §3):** dev-04's first span arms on its t0-date, Tue 17 Nov (RL-172 (a)), at its first legal t0 after this close + the close interval, on its own item, with its gates (the cold seat's delta ADMIT on `cl-dev-04`, the Q6 count on 6 + 6, the dev-03 pilot's desk final, and Mythos dev-04/05 F1's two records: dev-03's R9 passed and its class A smoke met).
