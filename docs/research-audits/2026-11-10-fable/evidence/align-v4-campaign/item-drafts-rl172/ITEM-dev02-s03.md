TBD. **Laptop lead (interactive, Opus 5.5), drafted by the dev02-ready builder, finalized for RL-165 §2 by the items-rl165 drafter 2026-11-14 PST and re-drafted under RL-171 by the items-rl171 builder 2026-11-15 PST, ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm the REST of block dev-02 on Mon 16 Nov, kit `cl-dev-02`, runner kind `cadence-legs-v1`, on `b4b6aeb192da60d895a7529311b06599efff5be4` checked out detached in a fresh scratch worktree. The roster follows Sunday: **if `dev-02-s02` (L001-L006) ran on Sunday, arm `dev-02-s03` = L007-L012; if it never armed, arm `dev-02-s01` = L001-L012 (the queued twelve-leg span).** EARLIEST: 00:00:00 PST Mon 16 Nov (epoch 1794816000; this is dev-02's Monday span, RL-165 §2) and the close interval after the latest close (RL-171 §6.1). LAUNCH as soon as every gate holds, at any hour of Mon 16 Nov up to 23:59:59 PST (LIMIT, epoch 1794902399), except 10:50:00-13:15:00 (this pin's soak path waits out 11:45-13:15 unbudgeted) and, for twelve legs only, 01:51:31-02:34:59 (both arguments refuse it). The batch-window argument follows the launch time and the roster (RL-171 §3; bands below). One span: a fresh soak, then six or twelve type-A legs (19,458-token step prompt, decode cap 4,096, Automatic, band q0). They are counted development legs of dev-02 (RL-155 §3.3). No other span, no queue extension, no session, no W1. Never launch between 10:50 and 13:15. The launch is your LAST action and you exit at once. If you cannot, do not launch; mail the lead (the standing F0 item then applies).**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-17T12:47:00-08:00
on_early_or_refused: any failed line of "Start and check", any launch refusal (rc≠0 or no claimed fence), or a launch that cannot happen inside the chosen roster's bands on Mon 16 Nov (00:00:00 to 23:59:59 outside 10:50:00-13:15:00; twelve legs also not 01:51:31-02:34:59): NOTHING of this item launches (a later t0 needs a new item; RL-165 §7: dev-02 has no Monday cutoff, it takes the first legal t0 after whatever holds the machine); mail the lead, and the standing F0 item applies. If `dev-02-s02` ended with a named stop or a receipt rc≠0, this item is not issued until the lead clears it. A span that ran but ends with any named stop or a receipt rc≠0: nothing relaunches, nothing is re-run, nothing else is queued; mail the lead. Do not retry, do not extend, do not reuse OUT
next_observable: the next activation (after the fence is gone) runs "Check" below and reports, by email to Ed and the lead and as RUN_STATE TBD+1: the receipt asserts, the per-leg admitted lines, the desk bundle, the restore lines, measurement_mode verify again, and the RL-150 R1 start-reference print (gates nothing)
```

- **Why (RL-165 §2; RL-155 §2 slot 6).** dev-02 runs as 6 + 6 when Sunday's pull ran: L007-L012 here, on Monday (RL-171 retires the 02:40 start; the calendar split stays). If the Sunday pull did not run (Sunday missed, or the append was refused), dev-02 runs Monday as queued: the twelve-leg `dev-02-s01`. A leg's calendar day is the local date of its span's t0, so these are Mon 16 Nov legs.
- **Sunday's span (the gate):** <LEAD FILLS: `dev-02-s02` ran (RUN_STATE <n>): RECEIPT OK or not, legs run and admitted of 6, no named stop open, restore lines clean; OR `dev-02-s02` never armed (why), so RAN=none>. If the standing F0 or any other run closed after it, its fence is gone and its restore lines passed (a "restore unproven" holds this span).
- **Day law (RL-172 (a), which replaces the two-starts default):** a day is the local date of a span's t0. No t0-date holds more than 12 mixed-size development legs (dev-03, dev-04, dev-05) or more than 24 development legs; qualification t0-dates are disjoint from development t0-dates; hp-01, F0, F2 and v4 sessions are outside the count. **This span's t0-date is Mon 16 Nov** (dev-02's second half, 6 legs (or dev-02-s01, 12, if RAN=none), not mixed-size: Mon 18 with dev-03); this item's window admits only that date. A span that misses its date is re-dated by the lead with a new item, never doubled up. Planned: Sat 7, Sun 11, Mon 18 (dev-02-s03 and dev-03), Tue 12 (dev-04), Wed 12 (dev-05). Because the queue does not yet enforce dates, `day_gate` counts the development legs already launched on the t0-date from their receipts and refuses this span past either cap; the committed queues' `not_before` values are lower bounds only.
- **What dev-02 is (RL-155 §3.3).** An ADDED development block, anchor-only, twelve type-A legs at the anchor shape, one cell. `HOLD_FOR_CELL_LAW` is lifted from `cl-dev-02`. The cap is 132 legs.
- **Gates (RL-165 §2: RL-155 §3.3's four lines and RL-156a §1's sentence, at each arm):** line 1 (Mythos 5.2 delta seat, ADMIT), line 2 (four parts, with RL-156a's sentence), line 3 (the queue), line 8 (the dev-01 pilot's R9); plus lines 5, 6, 7 and 9.
- **Counted.** The legs count as development legs of dev-02 under the kit's inclusion rules (RL-149 §2.3, §2.4 as amended by RL-150 R7 and R8). The kit has no `pilot_counted` rule, and RL-150 R9 does not apply: dev-02's pilot is dev-01's (line 8). An excluded leg is refilled only from the reserve under RL-149 §2.4. A re-run is a new span with `attempt` + 1 and `rerun_of`, and it needs a ruling.
- **Queue.** `dev-02-s03` is the second span of the 6 + 6 append (`rerun_of: dev-02-s01`); `dev-02-s01` was WITHDRAWN UNARMED by `dev-02-s02`'s arm record. If `dev-02-s02` never armed, `dev-02-s01` is live and `dev-02-s02`/`dev-02-s03` are WITHDRAWN UNARMED by this arm record. Ordering is carried by this item's text and lines 6 and 9, not by `cadence_queue.py next` (Mythos dev-02 F4). Do not run `next`.
- **Bytes.** Measured from `b4b6aeb192da60d895a7529311b06599efff5be4` (PR #775, branch `align/2026-11-14-campaign-runner`). The kit is `cl-dev-02.json` from `589748f15` (blob `7e8dc7a2`), sha256 `d963500b39af8867576ab07e2086c22ffd4a176c9e2d6eb60c80f65bc03728a8`, copied outside the checkout; its `frozen` block is byte-equal to `cl-dev-01`'s (`b4b6aeb19`, 37 paths). Same frozen bytes as the dev-01 spans: no smoke of its own (RL-155 §3.3 line 8).
- **CI equivalence.** `git diff b4b6aeb19..589748f15` over the 37 frozen paths is empty. The run that stands for `b4b6aeb19` is CI `ci` 43602828989 on #775's head `8bd31ae5a` (frozen-path diff empty) (line 2).
- **Condition-13 sources are byte-identical to the base.** `verify_r1_executed_sources` must return the full sha.
- **What the runner does** (docs/process/cadence_queue_design.md §13): as for every v1 span: preflight, the plan, ONE fresh soak (cap 1,950 s), the roster's legs in seeded order, each its own G0 under the 1,200 s R1 timeout then one turn, per-leg load redo (quota 2), no leg starts inside the batch-window argument (`$ARG`: 02:00-02:35 or 13:14-13:15, chosen by the launch time, RL-171 §3), close with Automatic restore, feeds stopped and hashed, `runner_receipt.json`, `desk-bundle/`. It reads and writes no energy. Of the KM003C stream it decodes only the header and trailer lines (RL-150 R8).
- **Timing.** Plans at `b4b6aeb19` with both arguments (blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-dev02-s03.txt`, `verify-dev02-s01.txt` and `probe/plan/`):
  - `dev-02-s03`, L007-L012: expected 10,656 s (3.0 h), worst case 24,750 s (6.9 h); fence deadline launch + 26,210 s. Bands: 00:00:00-02:34:59 `13:14-13:15`; 02:35:00-10:50:00 `02:00-02:35`; 13:15:00-19:07:30 `02:00-02:35`; 19:07:31-23:59:59 `13:14-13:15`. Forecast t0 00:00:00 (the last Sunday F0's expected close 23:20:57 + 20 min, then the calendar), argument `13:14-13:15`: expected end 02:57:36, worst end 06:52:30, fence end 07:16:50. A mock span at t0 00:30 with `13:14-13:15` (L009-L011 across 02:00-02:35): rc 0, 6 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/dev02-s03-alt-00:30/`).
  - `dev-02-s01`, L001-L012: expected 18,162 s (5.0 h), worst case 40,950 s (11.4 h); fence deadline launch + 42,410 s (790 s under the launcher's 43,200 s ceiling). Bands: 00:00:00-01:51:30 `13:14-13:15` (it refuses 01:51:31 on, the worst case meeting 13:14 the same day); none 01:51:31-02:34:59 (`02:00-02:35` refuses it too); 02:35:00-10:50:00 `02:00-02:35`; 13:15:00-14:37:30 `02:00-02:35`; 14:37:31-23:59:59 `13:14-13:15`. RL-171 retires the 14:03:10 (the 01:50 fence). A mock span at t0 00:30 with `13:14-13:15` (twelve legs): rc 0, 12 legs, no stops (`/Volumes/JW-EXT/scratch/items-rl171/mock/dev02-s01-alt-00:30/`).
  - No launch between 10:50 and 13:15: RL-171 calls it a defect of this pin, not a rule, but its soak path still waits out 11:45-13:15 unbudgeted. The epoch is the gate, in both blocks (Mythos dev-02 F2).
  - Pointer deadline = latest fence end (LIMIT 23:59:59 + 42,410 s for twelve legs = Tue 11:46:49) + 1 h.
- **Conditions.**
  - RL-171 retires Mythos dev-02 F2's "activation no earlier than 02:40" with the quiet: quiet is the per-leg agent census, process census and rule 5, and your own checks end before the launch (you exit at once). The epoch gate in "Start and check" still fails a start before Mon 00:00:00.
  - No agent session on the MBP during the span: you exit at once after the launch. No lead SSH, desk job or R12 process until the fence is gone.
  - Restore before the launch and again in "Check": AC, powermode 0, network time OFF, kernel frequency word 0 (item 251's remedy if not), no stray `km003c_monitor.py` / `hazard_monitor.py` / root `powermetrics`, no High Power marker, `night.lock` with no holder. `sudo -n -l /bin/kill` rc 0. Leave `night.lock` as found. Part C runs, F0 and the High Power block may have run since the pilot: the measurement_mode and network-time lines are read afresh, not assumed (Mythos dev-02 F5).
  - Every `validate-kit`, `plan` and `launch` passes `--batch-window "$ARG"` (chosen once in Start and check by the launch time and the roster, re-checked in Run; RL-171 §3) and `--legs` written out, and the arm record shows the plan's `batch_windows` (RL-150 §2 F2; Mythos dev-02 F5).
  - The arm record states the host is in measurement_mode as applied 11-13 23:47 and network time is off, checked remotely (RL-150 §2 F5).
  - Do NOT run `cadence_queue.py checklist` (line 5).
  - Output root `/Users/edr/campaign-out/cl-dev-02/` is outside every v4 registration and custody root (RL-149 §2.8 line 4; cold check F6).
- **Blinding.** Open no energy, power, meter-sample, transcript or slot file. From each leg bundle read ONLY `outputs/align_window_reference.json` and `outputs/align_thermal.jsonl` (thermal journal values, RL-150 R1 part 3), with the script below. Never print a KM003C stream line; never open `powermetrics*`, `hazards/`, `align_episode.json`, `telemetry*` or anything under `runs/*/outputs/` other than those two files.
- **May run:** this span, once, with the roster RAN selects. **May NOT:** the other roster, any dev-01, hp-01 or dev-03 leg, any session, W1, any filler while this span is armed (RL-155 §4 footprint rule 1).
- **High Power marker:** if `/Users/Shared/JouleWise/host-power/high-power.marker` exists, STOP and report.

- **Host gate and R1 reservation, immediately before the launch (Sol items review P1-1, P1-2; RL-155 R-B; RL-165 §7).** Separate from this item's campaign dependency: the Check of the latest close of ANYTHING on this host (any span, Part C or F0, slot session or W1) reported every restore line OK; no desk fence; no night or smoke agent loaded; no High Power marker; at least GAP seconds since that latest close (RL-171 §6.1, amending RL-155 R-B's 20 minutes: GAP is QUIET_CAMPAIGN_S after a campaign span's close, 300 s, confirmed by RL-172 §0; GAP is 1,200 s after a Part C or F0, F2, a slot session or W1) (the newest `runner_receipt.json` under `/Users/edr/campaign-out` and `/Users/edr/code/jw-wt`, from a census that stops on a missing root, any lookup error or an empty result, with fractional mtimes rounded up; or a session's close given as OTHER_CLOSE_EPOCH, a whole epoch or an explicit 0); and, after a CAMPAIGN close, that close's journal copy complete and hash-verified, shown by the lead's marker `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok`, written only after the copy is verified (Sol items-rl171 P1; a missing marker is WAIT; no SSH once a span is armed). Read fresh at the launch: if a v4 slot session is READY and staged for this slot, this span cedes; RL-172 (f) retires RL-165 §7's worst-case reservation: from the lead's record that a v4 session is READY nothing of lower priority arms, and the session takes the next clean close; before that record this span arms as usual.

**RL-149 §2.8 arm-record lines (record each, with its evidence):**
1. As `dev-02-s02`'s item, line 1: Mythos 5.2 delta seat on `cl-dev-02` (`d963500b…`), 11-14 15:06 PST: **ADMIT** (RL-155 §3.3 line 1), evidence/align-v4-campaign/mythos-dev02-delta.md, audit branch `108e8f93a`; its F1 to F5 closed in this item's text and scripts (F2: the epoch gate in both blocks (its "no activation before 02:40" is retired by RL-171); F4: lines 6 and 9 by hand; F5: `--batch-window`, `--legs` written out, no `checklist`, measurement_mode afresh, fresh worktree, kit copied to a new path with its sha asserted, a new OUT, a check script for the roster with the meter re-hash skipped); F6 is the lead's, recorded <LEAD FILLS: where>. The cold-seat chain for `c76344c5` (RL-150 §2, RL-152 §2.1) stands. Class B accepted (RL-152 §2.1).
2. Line 2, in RL-165 §5's four parts, exactly as `dev-02-s02`'s line 2: (1) CI `ci` 43602828989 on `8bd31ae5a`, frozen-path diff against `b4b6aeb19` empty; (2) red set = `fe907d0d3`'s 12 tests in 10 modules, test for test (CI 43600776368); (3) each red passes at #777 head `ae340d3da` (CI 43601158271); (4) frozen-path diff against `b4b6aeb19` empty; meter blobs `ff4fd76a` and `7d6acc98` identical at the base, the pilot commit and #777's head. RL-156a §1's sentence, verbatim: "Line 2 (RL-155a §4, read by RL-156a §1): the two red modules beyond RL-152's eight test no frozen byte that differs. `align.test_r1_followup` executes frozen `r1_runtime.py` (`261761f1`) and `thermal.py` (`e7cbd680`), and the failing site of `hazards.test_refusal_allowlist` is frozen `launch_align_r0.py` (`d2e8cba0`), each byte-identical at `fe907d0d3`, `b4b6aeb19` and `ae340d3da`; the allowlist red comes from unfrozen `configs/gates/hazard_refusals.json`; the three frozen files #777 changed (`v4_registration.py`, `align_r1_rehearsal.py`, `run_align_r1_smoke.py`) are only imported or scanned by these modules and are identical at the base and at the pilot commit."
3. Queue: for `dev-02-s03`, `QUEUE-cl-dev-02-b4b6aeb19-6plus6-append.json` on audit/2026-11-10-fable at `<LEAD FILLS: commit>`, sha256 `ad0212ae0f57deea871ccb13ce8f8591ff3247ea406dc8e56dddc59f4f91ca2e` (validate-queue ok, plan ids `cq-dev-02-s01-a1`, `cq-dev-02-s02-a1`, `cq-dev-02-s03-a1`); for `dev-02-s01`, the committed `QUEUE-cl-dev-02-b4b6aeb19.json` at `108e8f93a`, sha256 `d1ffc981f4d597d567ba251b4a01fb9490e717719ac4c33ee698bf63b51f4b77` (or the append, which holds it unchanged). Finite: `expires_at` 2026-11-20T23:59-08:00. `standing_notice` null; the notice is <LEAD FILLS: where posted>.
4. `validate-kit` passes (its `deny_scan` refuses any condition/slot/instruction key or label); OUT is outside every v4 registration and custody root (check below). RL-150 R6: the constant `benign` inside member-bundle configs is the stated exception.
5. The per-span checks of design doc §4 pass at the arm (Start and check) and at the close (Check). Do NOT run `cadence_queue.py checklist` (its `span_window` line encodes the fixed 13:20 t0; the kit's template still reads 13:20 to 00:45) or `cadence_queue.py next`.
6. No named stop, veto or halt open: no open `directive` issue by `mpmdw` whose title or first line starts STOP/NO/HALT/VETO, no open `cadence-stop` issue (gh on the MBP runs in the GUI context: `launchctl asuser`). By hand (Mythos dev-02 F4): no named stop open from `dev-01-s04`, any hp-01 span or `dev-02-s02`, no RESTORE_UNPROVEN and no High Power `revoked` hold: <LEAD FILLS: span ids, their desk `stops.json` result and the time read>.
7. Results-ref watcher live within 24 h: <LEAD FILLS: the Air results watcher (`com.joulewise.air-watch`) heartbeat stamp, under 24 h old at the arm; pid and commit>.
8. The dev-01 pilot passed: RUN_STATE 318 and item 320 (R9: three closes, admitted 3 of 3, no excluded leg, hand table and desk agree; VERDICT PASSED; evidence/align-v4-campaign/pilot-desk-cq-dev-01-s01-a1/ at `c73e78227`). RL-156a §1's condition as RL-161 §5 restates it: no sampler ran in any cadence leg, so the R9 record cannot show sampler starvation or an inventory gap; line 2 holds.
9. Line 9, across blocks in run order (RL-165 §6). Expected: `dev-02-s03` is campaign span 8 (1 dev-01 pilot, 2 `dev-01-s03`, 3 `dev-01-s04`, 4-6 hp-01's three spans, 7 `dev-02-s02`), so span 6's desk (expected `hp-01-s03`) must be FINAL. As run: this span is campaign span <LEAD FILLS: N>, and the desk of the span two back, <LEAD FILLS: SPAN ID>, is FINAL: <LEAD FILLS: the desk's stamp and where it is recorded>.

**Start and check (while you are still alive).** From a FRESH scratch worktree detached at the full sha (NOT the canonical clone's checkout, not another smoke worktree), own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `python3.13 -B -m unittest`, one module at a time; all must be OK: `tests.cadence.test_legs_runner`, `tests.cadence.test_kit`, `tests.cadence.test_stops_desk`, `tests.cadence.test_runner_guards`, `tests.align.test_r1_smoke_launcher`. Any failure: nothing launches; mail the lead.

```sh
# The launch bands (EARLIEST 1794816000 Mon 00:00:00; LIMIT 1794902399 Mon 23:59:59; none 10:50:01-13:14:59)
pick_arg6() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3; bands from this pin's own plan)
  n=$1
  if   [ "$n" -ge 1794816000 ] && [ "$n" -le 1794825299 ]; then echo 13:14-13:15   # Mon 16 Nov 00:00:00 .. Mon 16 Nov 02:34:59
  elif [ "$n" -ge 1794825300 ] && [ "$n" -le 1794855000 ]; then echo 02:00-02:35   # Mon 16 Nov 02:35:00 .. Mon 16 Nov 10:50:00
  elif [ "$n" -ge 1794863700 ] && [ "$n" -le 1794884850 ]; then echo 02:00-02:35   # Mon 16 Nov 13:15:00 .. Mon 16 Nov 19:07:30
  elif [ "$n" -ge 1794884851 ] && [ "$n" -le 1794902399 ]; then echo 13:14-13:15   # Mon 16 Nov 19:07:31 .. Mon 16 Nov 23:59:59
  else echo NONE; fi
}
pick_arg12() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3; bands from this pin's own plan)
  n=$1
  if   [ "$n" -ge 1794816000 ] && [ "$n" -le 1794822690 ]; then echo 13:14-13:15   # Mon 16 Nov 00:00:00 .. Mon 16 Nov 01:51:30
  elif [ "$n" -ge 1794825300 ] && [ "$n" -le 1794855000 ]; then echo 02:00-02:35   # Mon 16 Nov 02:35:00 .. Mon 16 Nov 10:50:00
  elif [ "$n" -ge 1794863700 ] && [ "$n" -le 1794868650 ]; then echo 02:00-02:35   # Mon 16 Nov 13:15:00 .. Mon 16 Nov 14:37:30
  elif [ "$n" -ge 1794868651 ] && [ "$n" -le 1794902399 ]; then echo 13:14-13:15   # Mon 16 Nov 14:37:31 .. Mon 16 Nov 23:59:59
  else echo NONE; fi
}
pick_arg() { "$PICK" "$1"; }
QUIET_CAMPAIGN_S=300    # RL-171 §6.1, confirmed by RL-172 §0: 300 s after a campaign close; 1,200 s after F0, F2 or any other close
: "${LAST_CLOSE_KIND:?Set to campaign if the latest close of anything on this host was a campaign span, else other (Part C/F0, F2, slot session, W1)}"
case "$LAST_CLOSE_KIND" in campaign) GAP=$QUIET_CAMPAIGN_S;; other) GAP=1200;; *) echo "STOP: LAST_CLOSE_KIND must be campaign or other"; exit 1;; esac
echo "close interval GAP $GAP s (RL-171 §6.1; 1,200 s after a Part C or F0, F2, a slot session or W1)"
# ONE newest-close selection over both roots, used by the host gate and by copy_gate (Sol RL-172 re-check 1)
close_census() {
  CENSUS="$("$PY" -I -B - /Users/edr/campaign-out /Users/edr/code/jw-wt <<'PY'
import math, os, sys
def fail(e):
    raise e
newest, path, count = None, None, 0
for root in sys.argv[1:]:
    if not os.path.isdir(root):
        sys.exit(f"STOP: receipt root missing: {root}")
    base = root.rstrip("/").count("/")
    for dirpath, dirnames, filenames in os.walk(root, onerror=fail):
        if dirpath.count("/") - base >= 3:
            dirnames[:] = []          # receipts at depth <= 4, as `find -maxdepth 4`
        if "runner_receipt.json" in filenames:
            p = os.path.join(dirpath, "runner_receipt.json")
            m = os.stat(p).st_mtime
            count += 1
            if newest is None or m > newest:
                newest, path = m, p
if count == 0:
    sys.exit("STOP: the receipt census found no runner_receipt.json; receipts are expected on this host")
if "\n" in path:
    sys.exit("STOP: newline in a receipt path")
print(math.ceil(newest))
print(path)
print(f"census: {count} receipts, newest mtime {newest!r} {path}", file=sys.stderr)
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
DAY_MIXED=no      # mixed-size development block (dev-03, dev-04, dev-05)
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
: "${RAN:?Set RAN to dev-02-s02 if Sunday span dev-02-s02 closed RECEIPT OK with no stop open, or none if it never armed}"
case "$RAN" in
  dev-02-s02) SPAN=dev-02-s03; LEGS=L007,L008,L009,L010,L011,L012; PICK=pick_arg6; DEADLINE_S=26210; WORST_S=24750; EXPECT="expected_s 10656, worst_case_s 24750";;
  none)       SPAN=dev-02-s01; LEGS=L001,L002,L003,L004,L005,L006,L007,L008,L009,L010,L011,L012; PICK=pick_arg12; DEADLINE_S=42410; WORST_S=40950; EXPECT="expected_s 18162, worst_case_s 40950";;
  *) echo "STOP: RAN must be dev-02-s02 or none"; exit 1;;
esac
NOW=$(date +%s)
ARG="$(pick_arg "$NOW")"
test "$ARG" != NONE || { echo "STOP: no admitted launch band now (outside this item's window, or inside 10:50-13:15 where this pin cannot launch); mail the lead"; exit 1; }
export ARG; echo "ARG $ARG (RL-171 §3: 02:00-02:35 where this pin's own plan admits the t0, else the data-only 13:14-13:15)"
echo "SPAN $SPAN LEGS $LEGS"
git -C /Users/edr/code/JouleWise fetch origin align/2026-11-14-campaign-runner
test -e /Users/edr/code/jw-wt/cadence-${SPAN} || git -C /Users/edr/code/JouleWise worktree add --detach /Users/edr/code/jw-wt/cadence-${SPAN} b4b6aeb192da60d895a7529311b06599efff5be4   # reused on a retry after a WAIT
cd /Users/edr/code/jw-wt/cadence-${SPAN}
test "$(git rev-parse HEAD)" = b4b6aeb192da60d895a7529311b06599efff5be4 || { echo "STOP: HEAD"; exit 1; }
test -z "$(git status --porcelain)" || { echo "STOP: dirty tree"; exit 1; }
REPO="$PWD"
: "${PY:?Set PY to the existing pinned measurement-venv interpreter (do not resolve the symlink)}"
: "${MAGISTRATE_PID:?Set to the PID of this magistrate own claude process}"
ps -o pid=,comm= -p "$MAGISTRATE_PID"                 # must show the claude process
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"   # the watchdog's fence root (fence + launch spec only)
"$PY" -B -c 'from pathlib import Path; import subprocess; from joulewise.align.apple import v4_registration as r; root=Path.cwd(); head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(); print(r.verify_r1_executed_sources(root,{"executed_commit":head}))'
# must print b4b6aeb192da60d895a7529311b06599efff5be4

# Sol P1 and RL-172 (a): before the KIT and OUT exist, so a WAIT here is retried cleanly at the next activation
effective_close || { echo "STOP: the receipt census failed; mail the lead"; exit 1; }
copy_gate || exit 1
day_gate || exit 1
# The kit: from PR #775's head, OUTSIDE the checkout, sha asserted
mkdir -p /Users/edr/campaign-out/kits
KIT=/Users/edr/campaign-out/kits/cl-dev-02-589748f15-${SPAN#dev-02-}.json
test ! -e "$KIT" || echo "KIT exists from an earlier Start of this item (a WAIT retry): re-written from git below, sha asserted"
git -C /Users/edr/code/JouleWise show 589748f15:docs/process/cadence/kits/cl-dev-02.json > "$KIT"
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = d963500b39af8867576ab07e2086c22ffd4a176c9e2d6eb60c80f65bc03728a8 || { echo "STOP: kit sha"; exit 1; }
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG"
# must print ok true, frozen_commit b4b6aeb192da60d895a7529311b06599efff5be4, frozen_paths_verified true,
# kit_sha256 d963500b39af8867576ab07e2086c22ffd4a176c9e2d6eb60c80f65bc03728a8, legs 12

# The queue: committed bytes on the audit branch, sha asserted
git -C /Users/edr/code/JouleWise fetch origin audit/2026-11-10-fable
QDIR=docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign
test "$(git -C /Users/edr/code/JouleWise show 108e8f93a:$QDIR/QUEUE-cl-dev-02-b4b6aeb19.json | shasum -a 256 | cut -c1-64)" = d1ffc981f4d597d567ba251b4a01fb9490e717719ac4c33ee698bf63b51f4b77 || { echo "STOP: base queue sha"; exit 1; }
if test "$RAN" = dev-02-s02; then
  QCOMMIT=<LEAD FILLS: the append's commit on audit/2026-11-10-fable>
  test "$(git -C /Users/edr/code/JouleWise show "$QCOMMIT":$QDIR/QUEUE-cl-dev-02-b4b6aeb19-6plus6-append.json | shasum -a 256 | cut -c1-64)" = ad0212ae0f57deea871ccb13ce8f8591ff3247ea406dc8e56dddc59f4f91ca2e || { echo "STOP: append sha"; exit 1; }
fi

# Output root outside every v4 registration and custody root
OUT=/Users/edr/campaign-out/cl-dev-02/cq-${SPAN}-a1-$("$PY" -B -c 'import time; print(time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))')
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

# The plan (record it whole; batch_windows must be ["$ARG"])
"$PY" -B scripts/cadence_legs_runner.py plan --kit "$KIT" --legs "$LEGS" --batch-window "$ARG"
# expect the roster in $LEGS, budget_s 1251 each, $EXPECT, blackout_clear true
DEADLINE="$("$PY" -B -c 'import time; print(time.time()+'"$DEADLINE_S"')')"
```

NOTE 1 and NOTE 2 as in `dev-02-s02`'s item (ADOPTED by the lead): the measurement_mode agent-line rule above, and the watchdog's fence root with all campaign data under OUT.

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
# The receipt census: every runner_receipt.json at depth <= 4 under both roots, fractional mtimes, ROUNDED UP.
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
# The band, last of all (do NOT switch rosters after the plan)
NOW=$(date +%s); test "$(pick_arg "$NOW")" = "$ARG" \
  || { echo "STOP: the clock left ARG $ARG's band (or this item's window) since Start and check; do not launch; mail the lead (a re-issue or a re-plan): the argument chosen in Start and check no longer belongs to the launch time"; exit 1; }
"$PY" -B scripts/launch_cadence_span.py launch \
  --repo "$REPO" --python-bin "$PY" \
  --kit "$KIT" --legs "$LEGS" --batch-window "$ARG" \
  --output "$OUT" --disk-path "$REPO" \
  --custody-root "$CUSTODY" --magistrate-pid "$MAGISTRATE_PID" \
  --deadline "$DEADLINE" --exit-wait-seconds 180 --start-wait-seconds 30
echo "$OUT"
```

Require exit 0, `"next": "exit the magistrate session now"` with a claimed fence (fence `pid` ≠ `MAGISTRATE_PID`), and the launch output's `plan.batch_windows` equal to `["$ARG"]`, the argument chosen in Start and check (else report it; the span is not counted until the lead rules). Record ARG, LAST_CLOSE_KIND, GAP, the journal-copy line (plan id and marker content), the day_gate line, the batch-time print, RAN, SPAN, LEGS, PY, MAGISTRATE_PID, KIT and its sha256, the queue commit(s) and sha(s), OUT, DEADLINE, HOST_RESTORE_OK, OTHER_CLOSE_EPOCH, the host last close printed, SESSION_READY, the launch time, the measurement_mode lines, the plan, and the spans withdrawn unarmed by this arm (none if RAN is `dev-02-s02`; `dev-02-s02` and `dev-02-s03` if RAN is none) in your RUN_STATE item and in `/Users/edr/night-custody/magistrate/cadence-${SPAN}-out-<activation>.txt`. Then exit at once, with no other `claude` or `codex` process running.

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
root = Path(sys.argv[1])
r = json.loads((root / "runner_receipt.json").read_text())
print(json.dumps({k: r.get(k) for k in ("rc", "runner_kind", "roster", "batch_windows", "legs_planned",
                                        "legs_finished", "load_redos_used", "span_result", "meter", "error")},
                 sort_keys=True))
print([(s["name"], s["rc"]) for s in r["steps"]])
assert r["runner_kind"] == "cadence-legs-v1" and r["roster"] == sys.argv[2].split(",")
assert r["kit"]["sha256"] == "d963500b39af8867576ab07e2086c22ffd4a176c9e2d6eb60c80f65bc03728a8"
assert r["kit"]["frozen_commit"] == "b4b6aeb192da60d895a7529311b06599efff5be4"
assert r["batch_windows"] == [__import__("os").environ["ARG"]], r["batch_windows"]   # ARG as recorded at the arm (RL-171)
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
assert files == [f"legs/{x}/leg_summary.json" for x in sys.argv[2].split(",")] + ["span/meter.json", "span/result.json"], files
for leg in sys.argv[2].split(","):
    s = json.loads((bundle / "legs" / leg / "leg_summary.json").read_text())
    print(leg, json.dumps(s, sort_keys=True))
print("result", (bundle / "span/result.json").read_text().strip())
print("meter", (bundle / "span/meter.json").read_text().strip())
print("RECEIPT OK" if r["rc"] == 0 and r["legs_finished"] == len(sys.argv[2].split(",")) else "RECEIPT NOT CLEAN: report in full")
PY
# RL-150 R1 part 3 print (gates nothing): soak reference; each leg's own reference; its G0 release reading;
# TV0h, TV1h, Tf08. Thermal journal values only: soak_reference.json, the soak's sensors journal,
# each leg's outputs/align_window_reference.json and outputs/align_thermal.jsonl. Nothing else is opened.
"$PY" -I -B - "$OUT" "$LEGS" <<'PY'
import json, statistics, sys
from pathlib import Path
root = Path(sys.argv[1])
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
for leg in sys.argv[2].split(","):
    rec = json.loads((root / "legs" / leg / "leg_record.json").read_text())
    bname = (rec.get("result") or {}).get("bundle")
    if not bname:
        print(leg, json.dumps({"no_bundle": True, "leg_status": rec.get("leg_status")})); continue
    out = root / "legs" / leg / "runtime" / bname / "outputs"
    j = rows(out / "align_thermal.jsonl")
    reads = [reading(d) for d in j if d["kind"] == "reading"]
    ref = json.loads((out / "align_window_reference.json").read_text())
    lo, hi = ref["span_ns"]
    ref_tf08 = [s["Tf08"] for t, s in reads if lo <= t <= hi and isinstance(s.get("Tf08"), (int, float))]
    g0 = next((d["values"]["gate"] for d in j if d["kind"] == "align_thermal_gate"
               and d["values"].get("gate", {}).get("kind") == "G0"), None)
    at = next((s for t, s in reads if g0 and t == g0.get("exit_sample_ns")), {})
    print(leg, json.dumps({
        "own_reference": {"status": ref["status"], "TV0h": ref["fast_c"], "TV1h": ref["slow_c"],
                          "Tf08_median": statistics.median(ref_tf08) if ref_tf08 else None},
        "g0": None if g0 is None else {"outcome": g0["outcome"], "duration_s": g0["duration_s"],
                                       "row_reference": g0.get("reference"), "row_release": g0.get("release"),
                                       "release": {k: at.get(k) for k in KEYS}}}, sort_keys=True))
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

**Report** (by email to Ed and the lead, and as RUN_STATE TBD+1): the receipt line, the step list and RECEIPT OK (or the receipt in full); each leg's `leg_summary.json` line with `admitted` called out; `span/result.json` and `span/meter.json`; legs run and admitted (of 6 or 12) and, for any excluded leg, the inclusion rule it fell under; whether any named stop would fire; the RL-150 R1 print as printed; the restore and measurement_mode lines; the receipt's close epoch; whether the span crossed 00:00. The magistrate reports; it never decides. Commit nothing from `$OUT`. Nothing is re-run and nothing else is queued.

**After (the lead, at the desk; not the magistrate).** Copy the desk bundle to the Air (`/Volumes/JW-EXT/cadence-desk/cq-<SPAN>-a1/input`) and build the automatic desk table (RL-149 §2.9 item 5 row 3); this desk must be FINAL before campaign span 10 arms (expected: dev-03's remainder). No hand-read is required. Move `dev-02` in BLOCK-QUEUE to COLLECTED, then DESK_FINAL when the desk is final; `qual-01` depends on `dev-05` (RL-155 §3.3), and the ledger entries for dev-02 to dev-05 and the look manifest's block list are the lead's (Mythos dev-02 F6). **Next (RL-165 §1):** the dev-03 pilot arms at this span's close + the close interval (RL-171 §6.1) with no further word from the lead, if v1.1 was READY and its item, queue and worktree were staged on the MBP by Sun 23:30; Monday's order after dev-02 closes is the slot session if READY (R-A), then the dev-03 pilot, then hp-01's unrun spans, then P, then the standing F0.
