TBD. **Laptop lead (interactive, Opus 5.5), drafted under RL-171 by the items-rl171 builder 2026-11-15 PST (new draft; the dev-04/05 kits' builder and the Mythos dev-04/05 delta seat supply the facts), ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm the SECOND span of block dev-04 (RL-158 §3; RL-165 §1, §4; RL-171), span `dev-04-s02`, legs L007, L008, L009, L010, L011, L012, kit `cl-dev-04.v1.1` (sha256 `1cc6673d78922a67b381155e24d53744e8515a6ca821e9a4a0ed62943d752228`), runner kind `cadence-legs-v1.1`, on `2d347f721552fe03bdd19f113e7bad7a7c24908e` checked out detached in a fresh scratch worktree. One span: a fresh soak, then six legs at their cells (L007 first; consumers L008, L009, L010, L011, L012 judge their G0 against L007's capture), decode cap 4,096, Automatic, band q0. They are counted development legs of dev-04. No other span, no queue extension, no session, no W1. EARLIEST: the close interval (RL-171 §6.1) after `dev-04-s01` closed with its fence gone and its Check reported, and not before 00:00:00 PST Tue 17 Nov (epoch 1794902400; this block's t0-date, RL-172 (a)). LAUNCH as soon as every gate holds, at any hour up to 23:59:59 PST Tue 17 Nov (LIMIT, epoch 1794988799; this block's t0-date, RL-172 (a)), except 10:50:00-13:15:00 (the pin's `fence_problems` refuses it under either argument). The batch-window argument follows the launch time (RL-171 §3): `02:00-02:35` from 02:35:00 to 10:50:00 and from 13:15:00 to 18:33:10; `13:14-13:15` from 18:33:11 to 02:34:59. The launch is your LAST action and you exit at once. If you cannot, do not launch; mail the lead (the standing F0 item then applies).**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-18T08:17:00-08:00
on_early_or_refused: any failed line of "Start and check", any launch refusal (rc≠0 or no claimed fence), or a launch that cannot happen inside the bands below (Tue 00:00:00 to Tue 23:59:59 PST, outside 10:50:00-13:15:00): NOTHING of this item launches; mail the lead; a later t0 needs a new item, and the standing F0 item applies meanwhile. A span that ran but ends with any named stop or a receipt rc≠0: nothing relaunches, nothing is re-run, nothing else is queued; mail the lead. Do not retry, do not extend, do not reuse OUT
next_observable: the next activation (after the fence is gone) runs "Check" below and reports, by email to Ed and the lead and as RUN_STATE TBD+1: the maintenance line, the receipt asserts, the per-leg admitted lines with g0_role and span_reference, the desk bundle, the restore lines, measurement_mode verify again, and the RL-150 R1 / RL-158 Q1 print (gates nothing)
```

- **Why (RL-158 §3; RL-165 §1; RL-171).** dev-04 follows at its first legal t0 on its own t0-date, Tue 17 Nov (RL-172 (a): each mixed-size block gets its own date; this amends RL-165 §1's "dev-04 and dev-05 follow at their first legal t0"). RL-171 retires the 18:33:10 latest t0 (the 01:50 fence) and the 02:40 starts: this pin's fence check is met by the argument `13:14-13:15` from 18:33:11 (RL-171 §3), so the span arms at any t0 outside 10:50-13:15. The 6 + 6 layout is RL-158 Q6's (the kits' builder, `/Volumes/JW-EXT/scratch/dev04-05/README.md`). A leg's calendar day is the local date of its span's t0.
- **Gate.** All of:
  - `dev-04-s01` closed and checked: <LEAD FILLS: RUN_STATE <n>: RECEIPT OK, legs run and admitted, no named stop open, restore lines clean, close epoch>.
  - **The cold seat's delta on `cl-dev-04.v1.1`: ADMIT** (Mythos 5.2, Sat 14 Nov 18:25 PST, "neither kit needs a byte changed"; `/Volumes/JW-EXT/scratch/mythos-dev0405-delta/REPORT.md`, <LEAD FILLS: its audit-branch copy>).
  - **Mythos dev-04/05 F1, the two dev-03 records (RL-150 R5; §2.8 line 8 for these kits):** dev-03's R9 **PASSED** and its class A smoke **MET** (L002 released its G0 against L001's capture and ran its turn), each recorded on its own line: <LEAD FILLS: both lines and where recorded>. dev-03 ran on `cl-dev-03.v1.1`, not the own-shaped v1.1a fallback; on that fallback this kit may not arm as built (F1) and the case goes to the research lead.
  - **Q6 (RL-158 Q6; RL-161):** on 6 + 6 dev-04 has 6 of its 10 warm legs as consumers (L005 in span 1; L008-L012 in span 2), at least half, and every cut lands on an own-shaped leg (L007). This span's consumers: L008, L009, L010, L011, L012.
  - **The L005 gate (RL-165 §4, amending RL-163 §6; RL-167: "at least four of its five"; Mythos dev-04/05 F3).** If `dev-04-s01`'s L005 **released** its G0, this span arms on its own gates. If L005 **timed out** at G0: this span arms on the lead's record only if dev-03 ended with at least four of its five consumers released (L002, L008, L009, L010, L012); with fewer than four it does NOT arm, and dev-04's L007-L012 and dev-05 run own-shaped (new kits). <LEAD FILLS: L005's G0 outcome from `dev-04-s01`'s Check, and, if it timed out, dev-03's released-consumer count and where recorded>. Mythos F3 (five consumers on one reference in this span) is the research lead's question; it does not hold this arm.
  - Lines 2, 3, 5, 6, 7 and 9 at the arm (below).
  - **Day law (RL-172 (a), which replaces the two-starts default):** a day is the local date of a span's t0. No t0-date holds more than 12 mixed-size development legs (dev-03, dev-04, dev-05) or more than 24 development legs; qualification t0-dates are disjoint from development t0-dates; hp-01, F0, F2 and v4 sessions are outside the count. **This span's t0-date is Tue 17 Nov** (dev-04, 12 mixed-size legs over its two spans); this item's window admits only that date. A span that misses its date is re-dated by the lead with a new item, never doubled up. Planned: Sat 7, Sun 11, Mon 18 (dev-02-s03 and dev-03), Tue 12 (dev-04), Wed 12 (dev-05). Because the queue does not yet enforce dates, `day_gate` counts the development legs already launched on the t0-date from their receipts and refuses this span past either cap; the committed queues' `not_before` values are lower bounds only.
  - **Host gate and R1 reservation, immediately before the launch (Sol items review P1-1, P1-2; RL-165 §7):** the Check of the latest close of ANYTHING on this host reported every restore line OK; no desk fence; no night or smoke agent loaded; no High Power marker; at least GAP seconds since that latest close (RL-171 §6.1, amending RL-155 R-B's 20 minutes: GAP is QUIET_CAMPAIGN_S after a campaign span's close, 300 s, confirmed by RL-172 §0; GAP is 1,200 s after a Part C or F0, F2, a slot session or W1), from the receipt census that stops on a missing root, any lookup error or an empty result (or OTHER_CLOSE_EPOCH); and, after a CAMPAIGN close, that close's journal copy complete and hash-verified, shown by the lead's marker `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok`, written only after the copy is verified (Sol items-rl171 P1; a missing marker is WAIT; no SSH once a span is armed). Read fresh at the launch: if a v4 slot session is READY and staged for this slot, this span cedes; RL-172 (f) retires RL-165 §7's worst-case reservation: from the lead's record that a v4 session is READY nothing of lower priority arms, and the session takes the next clean close; before that record this span arms as usual.
- **Counted.** The six legs count as development legs of dev-04 under the kit's inclusion rules (RL-149 §2.3, §2.4 as amended by RL-150 R7 and R8; rule 2 against the reference the leg's shape names). The kit has no `pilot_counted` rule (dropped by the builder: it described dev-03's smoke; Mythos delta: right). An excluded leg is refilled only from the reserve under RL-149 §2.4. A re-run is a new span with `attempt` + 1 and `rerun_of`, and it needs a ruling.
- **Queue.** `QUEUE-cl-dev-04-2d347f721.json`: `cq-cl-dev-04`, spans `dev-04-s01` (L001-L006) and `dev-04-s02` (L007-L012), both not_before 2026-11-16 (a lower bound only: dev-04's t0-date is Tue 17 Nov, RL-172 (a), which this item's window encodes), `expires_at` 2026-11-21T23:59:00-08:00 (the items-rl171 copy: the builder's not_before 2026-11-17 moved to 2026-11-16, the earliest day the RL-171 chain can need, and the expiry moved from 11-22 to 11-21 so that a commit any time from now is within 7 days, Mythos dev-04/05 F2). Do not run `cadence_queue.py next`: `not_before` and the k+2 desk rule are not enforced in code at this pin (Mythos F4); this item and line 9 carry them.
- **Bytes, CI and condition 13.** Measured from `2d347f721552fe03bdd19f113e7bad7a7c24908e` (the dev-03 pin). The kit is `cl-dev-04.v1.1.json` from `fecaf73f3579756c6e735f6a9cc74aab011d293a` (branch `align/2026-11-14-dev04-05-kits`, on #788's head `9cbb365a6`; kit files only), sha256 `1cc6673d78922a67b381155e24d53744e8515a6ca821e9a4a0ed62943d752228`, master seed 2026111405, copied outside the checkout. Its frozen block, runner, stop_rules, span_template, checklist, looks and desk are byte-identical to `cl-dev-03.v1.1`'s (Mythos delta). Line 2 is dev-03's, one result for the pin (Mythos F5). `verify_r1_executed_sources` must return the full sha. Same bytes as dev-03, so no smoke of its own: dev-03's pilot was the class A smoke (F1).
- **Timing.** Plan for this roster (`plan` at `2d347f721` with both arguments, blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-dev04-s02.txt`): expected 12,071 s, worst case 24,750 s (6 h 52 min 30 s); fence deadline launch + 26,210 s. Budgets: L007 (2000, own, first leg: its capture is the span's reference) 1076; L008 (19458, span, consume) 1642; L009 (10000, span, consume) 1547; L010 (2000, span, consume) 1467; L011 (19458, span, consume) 1642; L012 (10000, span, consume) 1547.
  - **Bands (RL-171 §3; the `pick_arg` function below), on Tue 17 Nov:** 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-18:33:10 `02:00-02:35`; 18:33:11-02:34:59 `13:14-13:15` (which admits six legs up to 05:47:10). Checked: with `02:00-02:35` 18:33:10 accepted and 18:33:11 refused; with `13:14-13:15` 05:47:10 accepted and 05:47:11 refused; 10:50:01 refused under either. `validate-kit` ok with either argument. A mock span at t0 Mon 00:30 with `13:14-13:15` across 02:00-02:35: rc 0, 6 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/dev04s02-alt-00:30/`).
  - Forecast t0 Tue 03:00:07 (dev-04-s01's expected close 02:55:07 + 5 min), argument `02:00-02:35`: expected end 06:21:18, worst end 09:52:37, fence end 10:16:57 (`/Volumes/JW-EXT/scratch/items-rl171/plans/chain-new.txt`).
  - Pointer deadline = latest fence end (LIMIT + 26,210 s = Wed 07:16:49) + 1 h.
- **Conditions, blinding and the High Power marker:** as the dev-03 items, with `--legs "$LEGS"` written out and `--batch-window "$ARG"` on every `validate-kit`, `plan` and `launch` (chosen once in Start and check by the launch time, re-checked in Run; RL-171 §3); the arm record shows the plan's `batch_windows` and the measurement_mode line (RL-150 §2 F2, F5; RL-161 §3); output root `/Users/edr/campaign-out/cl-dev-04/`. Quiet is the per-leg agent census, process census and rule 5 (RL-171); there is no clock quiet.
- **May run:** this span, once. **May NOT:** any other dev-04 or dev-05 span, any session, W1, any filler while this span is armed.

**RL-149 §2.8 arm-record lines (record each, with its evidence):**
1. Kit `ruling` is `RL-149 §2`. `cl-dev-04.v1.1` `1cc6673d…2228` at `2d347f721`: the Mythos 5.2 delta seat against `cl-dev-03.v1.1`, ADMIT (above); dev-03's line 1 (row-1 ADMIT at `17f478675`, Mythos first and delta seats on #788) stands for the shared bytes.
2. As dev-03's line 2 (RL-165 §5's four parts at `2d347f721`; CI run 43664825578 on `9cbb365a6`): <LEAD FILLS: its final conclusion and red set, one result for dev-03 to dev-05 (Mythos F5)>.
3. Queue `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-dev-04-2d347f721.json` on audit/2026-11-10-fable at `<LEAD FILLS: commit>`, sha256 `691319634b268f2d2b9c7c6308fea737d3b0f777bb859a6a14fa1322f1870d72` (`validate-queue` ok at `2d347f721` with `--kits-root` the dev-04/05 kit checkout at `fecaf73f3`: plan ids `cq-dev-04-s01-a1`, `cq-dev-04-s02-a1`; `/Volumes/JW-EXT/scratch/items-rl171/queue/validate-queue.log`).
4. `validate-kit` passes; OUT is outside every v4 registration and custody root (check below).
5. The per-span checks of design doc §4 and §14 pass at the arm and at the close. Do NOT run `cadence_queue.py checklist` or `next`.
6. No named stop, veto or halt open (the `directive` and `cadence-stop` issues; gh via `launchctl asuser`). By hand: no named stop open from any earlier span, no RESTORE_UNPROVEN and no High Power `revoked` hold: <LEAD FILLS: span ids, their desk `stops.json` result and the time read>.
7. Results-ref watcher live within 24 h: <LEAD FILLS: heartbeat stamp, pid and commit>.
8. dev-03's R9 PASSED and its class A smoke MET (Gate above; Mythos F1).
9. Line 9, across blocks in run order (RL-165 §6). Expected: this span is campaign span 12, so span 10's desk, dev-03's remainder (`dev-03-s02`, campaign span 10), must be FINAL. As run: this span is campaign span <LEAD FILLS: N>, and the desk of the span two back, <LEAD FILLS: SPAN ID>, is FINAL: <LEAD FILLS: the desk's stamp and where it is recorded>.

**Start and check (while you are still alive).** From a FRESH scratch worktree detached at the full sha (NOT the canonical clone's checkout, not a dev-01, dev-02 or hp-01 worktree), own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONPATH=.:tests`, `python3.13 -B -m unittest`, one module at a time; all must be OK: `tests.cadence.test_kit_v11`, `tests.cadence.test_span_reference`, `tests.cadence.test_legs_runner`, `tests.cadence.test_kit`, `tests.cadence.test_stops_desk`, `tests.cadence.test_runner_guards`, `tests.cadence.test_launch_cadence_span`, `tests.align.test_r1_smoke_launcher`. (At `2d347f721` the kit files are not in the tree, so `test_kit_v11`'s four committed-kit tests skip; they ran with 0 skips in CI shard 7, line 2 D2. The armed kit is checked by `validate-kit` below.) Any failure: nothing launches; mail the lead.

```sh
git -C /Users/edr/code/JouleWise fetch origin align/2026-11-14-kit-v1-1
git -C /Users/edr/code/JouleWise fetch origin align/2026-11-14-dev04-05-kits   # the kit file (not on the pin)
test -e /Users/edr/code/jw-wt/cadence-dev-04-s02 || git -C /Users/edr/code/JouleWise worktree add --detach /Users/edr/code/jw-wt/cadence-dev-04-s02 2d347f721552fe03bdd19f113e7bad7a7c24908e   # reused on a retry after a WAIT
cd /Users/edr/code/jw-wt/cadence-dev-04-s02
test "$(git rev-parse HEAD)" = 2d347f721552fe03bdd19f113e7bad7a7c24908e || { echo "STOP: HEAD"; exit 1; }
test -z "$(git status --porcelain)" || { echo "STOP: dirty tree"; exit 1; }
REPO="$PWD"
: "${PY:?Set PY to the existing pinned measurement-venv interpreter (do not resolve the symlink)}"
: "${MAGISTRATE_PID:?Set to the PID of this magistrate own claude process}"
ps -o pid=,comm= -p "$MAGISTRATE_PID"                 # must show the claude process
: "${PRIOR_CLOSE_EPOCH:?Set to the later of dev-04-s01 runner_receipt ended.epoch_s and the epoch its fence was seen gone}"
# The roster (RL-158 Q6's 6 + 6; the queue's span)
SPAN=dev-04-s02;  LEGS=L007,L008,L009,L010,L011,L012; DEADLINE_S=26210; WORST_S=24750; EXPECT="expected_s 12071, worst_case_s 24750"
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
# complete and hash-verified on the Air: the lead copies by SSH, verifies, and only then writes
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
# The launch bands (EARLIEST 1794902400 Tue 00:00:00; LIMIT 1794988799 Tue 23:59:59, the t0-date (RL-172 (a)); none 10:50:01-13:14:59)
pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3; bands from this pin's own plan)
  n=$1
  if   [ "$n" -ge 1794902400 ] && [ "$n" -le 1794911699 ]; then echo 13:14-13:15   # Tue 17 Nov 00:00:00 .. Tue 17 Nov 02:34:59
  elif [ "$n" -ge 1794911700 ] && [ "$n" -le 1794941400 ]; then echo 02:00-02:35   # Tue 17 Nov 02:35:00 .. Tue 17 Nov 10:50:00
  elif [ "$n" -ge 1794950100 ] && [ "$n" -le 1794969190 ]; then echo 02:00-02:35   # Tue 17 Nov 13:15:00 .. Tue 17 Nov 18:33:10
  elif [ "$n" -ge 1794969191 ] && [ "$n" -le 1794988799 ]; then echo 13:14-13:15   # Tue 17 Nov 18:33:11 .. Tue 17 Nov 23:59:59
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
# The kit: from `fecaf73f3` (branch align/2026-11-14-dev04-05-kits), OUTSIDE the checkout, sha asserted
mkdir -p /Users/edr/campaign-out/kits
KIT=/Users/edr/campaign-out/kits/cl-dev-04.v1.1-fecaf73f3-${SPAN#dev-04-}.json
test ! -e "$KIT" || echo "KIT exists from an earlier Start of this item (a WAIT retry): re-written from git below, sha asserted"
git -C /Users/edr/code/JouleWise show fecaf73f3579756c6e735f6a9cc74aab011d293a:docs/process/cadence/kits/cl-dev-04.v1.1.json > "$KIT"
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = 1cc6673d78922a67b381155e24d53744e8515a6ca821e9a4a0ed62943d752228 || { echo "STOP: kit sha"; exit 1; }
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG"
# must print ok true, campaign_id cl-dev-04, frozen_commit 2d347f721552fe03bdd19f113e7bad7a7c24908e, frozen_paths_verified true,
# kit_sha256 1cc6673d78922a67b381155e24d53744e8515a6ca821e9a4a0ed62943d752228, legs 12

# The queue: committed bytes on the audit branch, sha asserted
git -C /Users/edr/code/JouleWise fetch origin audit/2026-11-10-fable
QCOMMIT=<LEAD FILLS: the commit of QUEUE-cl-dev-04-2d347f721.json on audit/2026-11-10-fable>
test "$(git -C /Users/edr/code/JouleWise show "$QCOMMIT":docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-dev-04-2d347f721.json | shasum -a 256 | cut -c1-64)" = 691319634b268f2d2b9c7c6308fea737d3b0f777bb859a6a14fa1322f1870d72 || { echo "STOP: queue sha"; exit 1; }

# Output root outside every v4 registration and custody root
OUT=/Users/edr/campaign-out/cl-dev-04/cq-${SPAN}-a1-$("$PY" -B -c 'import time; print(time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))')
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
# L007 (2000, own, first leg: its capture is the span's reference) 1076; L008 (19458, span, consume) 1642; L009 (10000, span, consume) 1547; L010 (2000, span, consume) 1467; L011 (19458, span, consume) 1642; L012 (10000, span, consume) 1547;
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
test "$(date +%s)" -ge $((HOST_LAST_CLOSE + GAP)) || { echo "WAIT: close interval ($GAP s) after the latest close of anything on this host (RL-171 §6.1)"; exit 1; }
# R1 RESERVATION, fresh at the launch (RL-165 §7; RL-155 R-A; P1-2). Re-read the staged items and RUN_STATE now.
: "${SESSION_READY:?Set to yes if the lead has recorded a v4 session (R1 or W1) as READY, else no (RL-172 (f))}"
test "$SESSION_READY" = no || { echo "CEDE: a READY v4 session takes the next clean close (RL-172 (f); RL-155 R-A); do not launch; mail the lead"; exit 1; }
# RL-172 (f): RL-165 §7's worst-case reservation (launch + worst + 1,200 s <= SESSION_T0) is retired.
# The window and the campaign dependency, last of all
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

Require exit 0, `"next": "exit the magistrate session now"` with a claimed fence (fence `pid` ≠ `MAGISTRATE_PID`), and the launch output's `plan.batch_windows` equal to `["$ARG"]`, the argument chosen in Start and check (else report it; the span is not counted until the lead rules). The launcher itself refuses a fence end (worst case + 1,460 s) that passes ten minutes before the window in `--batch-window` (01:50 for `02:00-02:35`, 13:04 for `13:14-13:15`), a t0 strictly between 10:50 and 13:15 under either argument, a deadline under the plan's worst case plus reserves, a missing kit and a missing `--batch-window`. Record ARG, LAST_CLOSE_KIND, GAP, the journal-copy line (plan id and marker content), the day_gate line, the batch-time print, SPAN, LEGS, PRIOR_CLOSE_EPOCH, PY, MAGISTRATE_PID, KIT and its sha256, the queue commit and sha, OUT, DEADLINE, HOST_RESTORE_OK, OTHER_CLOSE_EPOCH, the host last close printed, SESSION_READY, the launch time, the measurement_mode lines and the plan in your RUN_STATE item and in `/Users/edr/night-custody/magistrate/cadence-${SPAN}-out-<activation>.txt`. Then exit at once, with no other `claude` or `codex` process running.

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
assert r["kit"]["sha256"] == "1cc6673d78922a67b381155e24d53744e8515a6ca821e9a4a0ed62943d752228"
assert r["kit"]["frozen_commit"] == "2d347f721552fe03bdd19f113e7bad7a7c24908e" and r["kit"]["campaign_id"] == "cl-dev-04"
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
- SPAN and LEGS; the ARG used; the maintenance line's counts and the legs they overlap;
- the receipt line, the step list and RECEIPT OK (or the receipt in full if not clean);
- each leg's `leg_summary.json` line, with `admitted`, `g0_role`, `g0_outcome`, `g0_s` and `span_reference` called out per leg;
- each consumer's G0 outcome against L007's capture (released or timed out), and the count released;
- `span/result.json` and `span/meter.json`;
- legs run and admitted (of 6); for any excluded leg, the inclusion rule it fell under; whether any named stop would fire (LEG_OVERTIME is two legs over 1.5 x their own budget; a missing L007 reference is a REFUSAL that stops the span, RL-158 Q3);
- the RL-150 R1 / RL-158 Q1 print above, as printed;
- the restore lines and the measurement_mode verify lines; the receipt's close epoch;
- whether the span crossed 00:00 (the `/private/tmp` walk; not a gate).

The magistrate reports; it never decides. Commit nothing from `$OUT`. Nothing is re-run and nothing else is queued.

**After (the lead, at the desk; not the magistrate).**
- **The Air desk (Mythos #788 delta D1; dev-04/05 F8):** from the checkout at `2d347f721` (or `1b20d3b0e`), with the kit; never a checkout at `b4b6aeb19`, `main` or the hp-01 line. Copy the bundle to `/Volumes/JW-EXT/cadence-desk/cq-dev-04-s02-a1/input`.
- **The hand-read print of every v1.1 span (RL-158 Q1):** the soak reference, L007's capture, and each consumer's release reading and G0 wait. Mark "reference from a redo" or "from an excluded leg" from the receipt's `span_reference` (RL-158 Q2; RL-161 §4).
- **The realized consumer count (RL-158 Q6):** consumers released over the block; it goes in the ledger row. A block that ends with fewer than four released consumers comes to the research lead (RL-158 Q6); nothing stops on that.
- This desk must be FINAL before campaign span 14 arms (line 9). **Next:** `dev-05-s01` arms on its own item on its t0-date, Wed 18 Nov (RL-172 (a)); the ladder fills the rest of Tuesday. Ledger: `dev-04` to COLLECTED, then DESK_FINAL when the desk is final.
