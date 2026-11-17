TBD. **Laptop lead (interactive, Opus 5.5), drafted by the dev02-ready builder, finalized for RL-165 §2 by the items-rl165 drafter 2026-11-14 PST and re-drafted under RL-171 by the items-rl171 builder 2026-11-15 PST, ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm the FIRST HALF of block dev-02 (RL-165 §2, filler P as 6 + 6): span `dev-02-s02`, legs L001 to L006, kit `cl-dev-02`, runner kind `cadence-legs-v1`, on `b4b6aeb192da60d895a7529311b06599efff5be4` checked out detached in a fresh scratch worktree. One span: a fresh soak, then six type-A legs (19,458-token step prompt, decode cap 4,096, Automatic, band q0). They are counted development legs of dev-02 (RL-155 §3.3). No other span, no queue extension, no session, no W1. EARLIEST: the close interval (RL-171 §6.1) after the last close on Sunday (the last hp-01 span that runs on Sunday, or `dev-01-s04` if none does) with its fence gone, and not before 00:00:00 PST Sun 15 Nov (epoch 1794729600). LAUNCH as soon as every gate holds, at any hour of Sun 15 Nov up to 23:59:59 PST (LIMIT, epoch 1794815999: the 6 + 6 split's Sunday half, RL-165 §2; RL-171 retires the 18:33:10 that was the 01:50 fence), except 10:50:00-13:15:00 (this pin's soak path waits out 11:45-13:15 unbudgeted). The batch-window argument follows the launch time (RL-171 §3): `02:00-02:35` from 02:35:00 to 10:50:00 and from 13:15:00 to 19:07:30; `13:14-13:15` before 02:35:00 and after 19:07:30. The launch is your LAST action and you exit at once. If you cannot, do not launch; mail the lead (the standing F0 item then applies).**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-16T08:17:00-08:00
on_early_or_refused: any failed line of "Start and check", any launch refusal (rc≠0 or no claimed fence), or a launch that cannot happen inside (the last Sunday close + the close interval) to 23:59:59 PST Sun 15 Nov (epoch 1794815999), outside 10:50:00-13:15:00: NOTHING of this item launches; there is no Sunday pull and dev-02 runs Monday as queued (`dev-02-s01`, twelve legs, by the Monday item; RL-165 §2); mail the lead, and the standing F0 item applies. A span that ran but ends with any named stop or a receipt rc≠0: nothing relaunches, nothing is re-run, nothing else is queued; mail the lead. Do not retry, do not extend, do not reuse OUT
next_observable: the next activation (after the fence is gone) runs "Check" below and reports, by email to Ed and the lead and as RUN_STATE TBD+1: the receipt asserts, the per-leg admitted lines, the desk bundle, the restore lines, measurement_mode verify again, and the RL-150 R1 start-reference print (gates nothing)
```

- **Why (RL-165 §2).** dev-02 may run as 6 + 6: L001-L006 on Sunday (this span), L007-L012 on Monday (`dev-02-s03`, its own item). RL-171 retires the two clock values in RL-165 §2's sentence: 18:33:10 was the 01:50 fence bound and 02:40 was the quiet's end. The calendar split stays (RL-171 §2: the calendar-day rules stand). RL-155a §1.1's reasoning applies as it did to dev-01: part of the block leaves Monday its span and its day. **6 + 6 only:** if this span cannot launch on Sunday (by 23:59:59), filler P does not take dev-02 on Sunday, and the Monday item arms the twelve-leg `dev-02-s01` instead.
- **Order (RL-165 §2).** Sunday after `dev-01-s04`: the R1 slot session if READY (R-A), then hp-01's three spans, then this pull, then F0. This span arms only when no READY slot session or hp-01 span is staged for the slot. A leg's calendar day is the local date of its span's t0, so these are Sun 15 Nov legs.
- **Day law (RL-172 (a), which replaces the two-starts default):** a day is the local date of a span's t0. No t0-date holds more than 12 mixed-size development legs (dev-03, dev-04, dev-05) or more than 24 development legs; qualification t0-dates are disjoint from development t0-dates; hp-01, F0, F2 and v4 sessions are outside the count. **This span's t0-date is Sun 15 Nov** (dev-02's first half, 6 legs, not mixed-size: Sun 11 with dev-01-s04); this item's window admits only that date. A span that misses its date is re-dated by the lead with a new item, never doubled up. Planned: Sat 7, Sun 11, Mon 18 (dev-02-s03 and dev-03), Tue 12 (dev-04), Wed 12 (dev-05). Because the queue does not yet enforce dates, `day_gate` counts the development legs already launched on the t0-date from their receipts and refuses this span past either cap; the committed queues' `not_before` values are lower bounds only.
- **What dev-02 is (RL-155 §3.3).** An ADDED development block, anchor-only: twelve type-A legs at the anchor shape; the mixed-cell design keeps its 36 legs as dev-03 to dev-05 on kit v1.1, so development is 60 legs in five blocks and the cap is 132 legs. `HOLD_FOR_CELL_LAW` is lifted from `cl-dev-02`. In this span one leg is cold (L001) and five are warm.
- **Gates (RL-165 §2: RL-155 §3.3's four lines and RL-156a §1's sentence, at each arm):** line 1 (Mythos 5.2 delta seat, ADMIT), line 2 (four parts, with RL-156a's sentence), line 3 (the validated append, committed), line 8 (the dev-01 pilot's R9); plus lines 5, 6, 7 and 9.
- **Counted.** The six legs count as development legs of dev-02 under the kit's inclusion rules (RL-149 §2.3, §2.4 as amended by RL-150 R7 and R8). The kit has no `pilot_counted` rule, and RL-150 R9 does not apply: dev-02's pilot is dev-01's (line 8). An excluded leg is refilled only from the reserve under RL-149 §2.4. A re-run is a new span with `attempt` + 1 and `rerun_of`, and it needs a ruling.
- **Queue (RL-165 §2).** The lead appends `dev-02-s02` (L001-L006) and `dev-02-s03` (L007-L012) to the committed one-span queue; additions only. **The twelve-leg span `dev-02-s01` is recorded as WITHDRAWN UNARMED only when this span arms (this arm record does so).** If this span never arms, `dev-02-s01` stays live and arms Monday. Ordering after dev-01 and hp-01 is carried by this item's text and by lines 6 and 9, not by `cadence_queue.py next` (Mythos dev-02 F4). Do not run `next`.
- **Bytes.** Measured from `b4b6aeb192da60d895a7529311b06599efff5be4` (PR #775, branch `align/2026-11-14-campaign-runner`). The kit is NOT the in-tree copy at that commit (an older pin): it is `cl-dev-02.json` from `589748f15` (blob `7e8dc7a2`), sha256 `d963500b39af8867576ab07e2086c22ffd4a176c9e2d6eb60c80f65bc03728a8`, copied outside the checkout. Its `frozen` block is byte-equal to `cl-dev-01`'s (`c76344c5…66d7`; commit `b4b6aeb19`, 37 paths). It differs from `cl-dev-01` only in `campaign_id`, `title`, `seed_law.master_seed` (2026111402), the twelve `legs[].seed` values, and the inclusion rules, where `pilot_counted` is removed. Same frozen bytes as the dev-01 spans: no smoke of its own (RL-155 §3.3 line 8).
- **CI equivalence.** `git diff b4b6aeb19..589748f15` over the 37 frozen paths is empty. The run that stands for `b4b6aeb19` is CI `ci` 43602828989 on #775's head `8bd31ae5a`, whose diff against `b4b6aeb19` over the 37 frozen paths is also empty (line 2).
- **Condition-13 sources are byte-identical to the base** (`v4_registration.R1_EXECUTED_SOURCES`, the ten paths). `verify_r1_executed_sources` must return the full sha.
- **What the runner does** (docs/process/cadence_queue_design.md §13): preflight (HEAD = frozen commit; frozen paths' working-tree bytes = kit; night agents; AC; condition 13; agent census, KM003C and volume feeds; powermode 0 read back; display sleep and 300 s dwell); the plan; ONE fresh soak (cap 1,950 s); L001-L006 in seeded order, each its own G0 under the 1,200 s R1 timeout, then one turn; per-leg load redo (RL-72 E2 rule, quota 2 per span); no leg starts inside the batch-window argument (`$ARG`: 02:00-02:35 or 13:14-13:15, chosen by the launch time, RL-171 §3); close: Automatic restore, feeds stopped and hashed, `runner_receipt.json`, `desk-bundle/`. It reads and writes no energy. Of the KM003C stream it decodes only the header and trailer lines (RL-150 R8).
- **Timing.** Plan for this roster (`plan` at `b4b6aeb19` with both arguments, blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-dev02-s02.txt` and `probe/plan/`): expected 10,656 s (3.0 h), worst case 24,750 s (6.9 h). The fence deadline is launch + 26,210 s (worst case + 560 s reserves + 900 s start slack).
  - **Bands (RL-171 §3; the `pick_arg` function below):** 00:00:00-02:34:59 `13:14-13:15`; 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-19:07:30 `02:00-02:35`; 19:07:31-23:59:59 `13:14-13:15` (`02:00-02:35` refuses six legs from 19:07:31 to 02:34:59; `13:14-13:15` admits them from 13:15:00 to 06:21:30). `validate-kit` is ok with either argument. A mock span at t0 00:30 with `13:14-13:15` (six legs, L003-L005 across 02:00-02:35): rc 0, 6 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/dev02-s02-alt-00:30/`). The mock does not model the soak path's 11:45-13:15 wait.
  - Forecast t0 10:19:27 (hp-01-s03's expected close 10:14:27 + 5 min), argument `02:00-02:35`: expected end 13:17:03, worst end 17:11:57, fence end 17:36:17. With a 20-min interval the forecast t0 (10:44:27 + 20 min) falls in 10:50-13:15 and moves to 13:15:00.
  - t0 23:59:59 (LIMIT), argument `13:14-13:15`: worst end Mon 06:52:29, fence end 07:16:49.
  - No launch between 10:50 and 13:15: RL-171 calls it a defect of this pin, not a rule, but its soak path still waits out 11:45-13:15 unbudgeted (`OS_BATCH_WINDOW_LOCAL` at `b4b6aeb19` is 11:45-13:15).
  - The epoch is the gate, in both the check block and the run block (Mythos dev-02 F2); `not_before` in the queue is format-checked only.
  - Pointer deadline = latest fence end (LIMIT + 26,210 s = 07:16:49 Mon) + 1 h.
- **Conditions.**
  - RL-171 retires Mythos dev-02 F2's "activation not inside 01:30-02:40" with the quiet: quiet is the per-leg agent census, process census and rule 5, and your own checks end before the launch (you exit at once).
  - No agent session on the MBP during the span: you exit at once after the launch. No lead SSH, desk job or R12 process until the fence is gone.
  - Restore before the launch and again in "Check": AC, powermode 0, network time OFF, kernel frequency word 0 (item 251's remedy if not), no stray `km003c_monitor.py` / `hazard_monitor.py` / root `powermetrics`, no High Power marker, `night.lock` with no holder. `sudo -n -l /bin/kill` rc 0. Leave `night.lock` as found. Part C runs and the High Power block ran before this span: the measurement_mode and network-time lines are read afresh, not assumed (Mythos dev-02 F5).
  - Every `validate-kit`, `plan` and `launch` passes `--batch-window "$ARG"` (chosen once in Start and check by the launch time and re-checked in Run; RL-171 §3) and `--legs L001,L002,L003,L004,L005,L006` written out, and the arm record shows the plan's `batch_windows` (RL-150 §2 F2; Mythos dev-02 F5).
  - The arm record states the host is in measurement_mode as applied 11-13 23:47 and network time is off, checked remotely (RL-150 §2 F5).
  - Do NOT run `cadence_queue.py checklist` (line 5).
  - Output root `/Users/edr/campaign-out/cl-dev-02/` is outside every v4 registration and custody root (RL-149 §2.8 line 4; cold check F6).
- **Blinding.** Open no energy, power, meter-sample, transcript or slot file. From each leg bundle read ONLY `outputs/align_window_reference.json` and `outputs/align_thermal.jsonl` (thermal journal values, RL-150 R1 part 3), with the script below. Never print a KM003C stream line; never open `powermetrics*`, `hazards/`, `align_episode.json`, `telemetry*` or anything under `runs/*/outputs/` other than those two files.
- **May run:** this span, once. **May NOT:** `dev-02-s01`, `dev-02-s03`, any dev-01 or hp-01 leg, any session, W1, any filler while this span is armed (RL-155 §4 footprint rule 1).
- **High Power marker:** if `/Users/Shared/JouleWise/host-power/high-power.marker` exists, STOP and report.

- **Host gate and R1 reservation, immediately before the launch (Sol items review P1-1, P1-2; RL-155 R-B; RL-165 §7).** Separate from this item's campaign dependency: the Check of the latest close of ANYTHING on this host (any span, Part C or F0, slot session or W1) reported every restore line OK; no desk fence; no night or smoke agent loaded; no High Power marker; at least GAP seconds since that latest close (RL-171 §6.1, amending RL-155 R-B's 20 minutes: GAP is QUIET_CAMPAIGN_S after a campaign span's close, 300 s, confirmed by RL-172 §0; GAP is 1,200 s after a Part C or F0, F2, a slot session or W1) (the newest `runner_receipt.json` under `/Users/edr/campaign-out` and `/Users/edr/code/jw-wt`, from a census that stops on a missing root, any lookup error or an empty result, with fractional recorded close epochs rounded up; or a session's close given as OTHER_CLOSE_EPOCH, a whole epoch or an explicit 0); and, after a CAMPAIGN close, that close's journal copy complete and hash-verified, shown by the lead's marker `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok`, written only after the copy is verified (Sol items-rl171 P1; a missing marker is WAIT; no SSH once a span is armed). Read fresh at the launch: if a v4 slot session is READY and staged for this slot, this span cedes; RL-172 (f) retires RL-165 §7's worst-case reservation: from the lead's record that a v4 session is READY nothing of lower priority arms, and the session takes the next clean close; before that record this span arms as usual.

**RL-149 §2.8 arm-record lines (record each, with its evidence):**
1. Kit `ruling` is `RL-149 §2`, with the added block ruled by RL-155 §3.3 (the kit cites RL-149 only and stays as built). Cold seat chain: Mythos 5.2 (11-14) on `cl-dev-01` at `efbd0b020`: ADMIT WITH FIXES, F1-F4 closed (RL-150 §2); the kit `c76344c5…` on `b4b6aeb19` (RL-152 §2.1): delta seat ADMIT WITH FIXES, row-1 delta review ADMIT WITH FIXES (test-only). For `cl-dev-02` (`d963500b…`): **Mythos 5.2 delta seat, 11-14 15:06 PST: ADMIT** (RL-155 §3.3 line 1), evidence/align-v4-campaign/mythos-dev02-delta.md, audit branch `108e8f93a`, no finding against the kit. Its findings on the item: F1 (queue expiry) closed in line 3; F2 (epoch gate in both blocks; no activation in the quiet) closed in this item's text and gates; F3 (line 2's module count) closed in line 2; F4 (hand records, lines 6 and 9) closed below; F5 (pilot conditions carried: `--batch-window`, `--legs` written out, no `checklist`, measurement_mode and network time read afresh, fresh detached worktree, kit copied to a new path with its sha asserted, a new OUT outside the v4 roots, a check script for this roster with the meter re-hash skipped) closed in this item's text and scripts; F6 (ledger, standing notice, look manifest) is the lead's, recorded <LEAD FILLS: where>. Plus the `validate-kit` line and the `plan` below. Class B accepted (RL-152 §2.1).
2. Line 2, in RL-165 §5's four parts (RL-152 §2.2 extended to this kit by RL-155 §3.3, read by RL-155a §4 and RL-156a §1): the kit validates at `b4b6aeb19` (`validate-kit` below; Air 2026-11-14: ok, frozen_paths_verified true, `/Volumes/JW-EXT/scratch/items-rl165/evidence/validate-kit-dev02.json`), and the two `frozen` blocks are byte-equal (same commit, same 37 path hashes).
   1. **Same bytes.** The full suite ran on bytes equal to `b4b6aeb19` on all 37 frozen paths: CI `ci` run 43602828989 on `8bd31ae5a` (frozen-path diff against `b4b6aeb19` empty).
   2. **Red set.** It equals `fe907d0d3`'s (CI `ci` run 43600776368, PR #781): the same 12 tests in 10 modules, test for test (RL-155a §4 corrects RL-152's "eight modules": the eight plus `align.test_r1_followup` and `hazards.test_refusal_allowlist`).
   3. **Each red passes at a #777 head:** CI `ci` run 43601158271 on #777 head `ae340d3da` (success, full suite; plus targeted local runs rc 0).
   4. **Recorded diff.** The frozen-path diff against `b4b6aeb19` is empty. The meter driver `joulewise/b5/driver.py` (blob `ff4fd76a`) and `scripts/km003c_monitor.py` (blob `7d6acc98`) are identical at the base, the pilot commit and #777's head.
   Evidence: evidence/align-v4-campaign/rl152-redset/ (LINE2.md, LINE2-added-modules.md) on audit/2026-11-10-fable. The sentence RL-156a §1 rules for this record, verbatim: "Line 2 (RL-155a §4, read by RL-156a §1): the two red modules beyond RL-152's eight test no frozen byte that differs. `align.test_r1_followup` executes frozen `r1_runtime.py` (`261761f1`) and `thermal.py` (`e7cbd680`), and the failing site of `hazards.test_refusal_allowlist` is frozen `launch_align_r0.py` (`d2e8cba0`), each byte-identical at `fe907d0d3`, `b4b6aeb19` and `ae340d3da`; the allowlist red comes from unfrozen `configs/gates/hazard_refusals.json`; the three frozen files #777 changed (`v4_registration.py`, `align_r1_rehearsal.py`, `run_align_r1_smoke.py`) are only imported or scanned by these modules and are identical at the base and at the pilot commit." Its "one limit" is replaced by RL-161 §5 (line 8).
3. Queue `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-dev-02-b4b6aeb19-6plus6-append.json` on audit/2026-11-10-fable at `<LEAD FILLS: commit>`, sha256 `ad0212ae0f57deea871ccb13ce8f8591ff3247ea406dc8e56dddc59f4f91ca2e`. It is the committed `QUEUE-cl-dev-02-b4b6aeb19.json` (`108e8f93a`, sha `d1ffc981…4b77`) with two spans appended and nothing else changed (the base's text up to its last span is a byte prefix): `dev-02-s02` (L001-L006, not_before 2026-11-15) and `dev-02-s03` (L007-L012, not_before 2026-11-16), each attempt 1 and `rerun_of: dev-02-s01`, because the closed schema has no withdrawn field and the validator refuses a repeated leg without `rerun_of`. `validate-queue` ok with `--kits-root` the #775 checkout at `8bd31ae5a` (the `589748f15` kit blob), run from the `b4b6aeb19` tree on the Air 2026-11-14: plan ids `cq-dev-02-s01-a1`, `cq-dev-02-s02-a1`, `cq-dev-02-s03-a1` (`/Volumes/JW-EXT/scratch/items-rl165/evidence/validate-queue-dev02.log`). Finite: `expires_at` 2026-11-20T23:59-08:00, unchanged and within 7 days of the append's commit (Mythos dev-02 F1). `standing_notice` null, so the notice naming queue, kit, legs and expiry is <LEAD FILLS: where posted>. **`dev-02-s01` (L001-L012) is WITHDRAWN UNARMED by this arm record (RL-165 §2); it never ran and never arms.**
4. `validate-kit` passes (its `deny_scan` refuses any condition/slot/instruction key or label); OUT is outside every v4 registration and custody root (check below). RL-150 R6: the constant `benign` inside member-bundle configs is the stated exception.
5. The per-span checks of design doc §4 pass at the arm (Start and check) and at the close (Check). Do NOT run `cadence_queue.py checklist`: its `span_window` line encodes the fixed 13:20 t0 that RL-149 §2.9 item 6.3 removed, and the kit's template still reads 13:20 to 00:45 (cold check reading 4; Mythos dev-02 F5). Do not run `cadence_queue.py next` either.
6. No named stop, veto or halt open: no open `directive` issue by `mpmdw` whose title or first line starts STOP/NO/HALT/VETO, no open `cadence-stop` issue (gh on the MBP runs in the GUI context: `launchctl asuser`). By hand, because dev-02 has its own queue (Mythos dev-02 F4): no named stop is open from `dev-01-s03`, `dev-01-s04` or any hp-01 span that ran, no RESTORE_UNPROVEN and no High Power `revoked` hold: <LEAD FILLS: span ids, their desk `stops.json` result and the time read>.
7. Results-ref watcher live within 24 h: <LEAD FILLS: the Air results watcher (`com.joulewise.air-watch`) heartbeat stamp, which must be under 24 h old at the arm; name pid and commit>.
8. The dev-01 pilot passed (RL-149 §2.9 item 3; RL-150 R9; RL-155 §3.3 line 8): RUN_STATE 318 and the lead's hand-read, item 320: (1) three closes with complete records; (2) admitted 3 of 3; (3) no excluded leg; (4) hand table and desk agree, on inclusion too; no named stop open; VERDICT PASSED, evidence/align-v4-campaign/pilot-desk-cq-dev-01-s01-a1/ at `c73e78227`. Same bytes, so no smoke of its own. **RL-156a §1's condition, as RL-161 §5 restates it:** the cadence-leg kind does not run the R1 ProcessInventory journal, so no sampler ran and the R9 record cannot show sampler starvation or an inventory gap; line 2 holds.
9. Line 9, counted across blocks in the order the machine ran them (RL-165 §6; RL-155 §3.4: Part C, the slot session and fillers do not count). Expected order: 1 dev-01 pilot, 2 `dev-01-s03`, 3 `dev-01-s04`, 4 `hp-01-s01`, 5 `hp-01-s02`, 6 `hp-01-s03`, **7 this span**; so the desk of span 5 must be FINAL. As run: this span is campaign span <LEAD FILLS: N>, and the desk of the span two back, <LEAD FILLS: SPAN ID (expected `hp-01-s02`)>, is FINAL: <LEAD FILLS: the desk's stamp and where it is recorded>.

**Start and check (while you are still alive).** From a FRESH scratch worktree detached at the full sha (NOT the canonical clone's checkout, not another smoke worktree), own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `python3.13 -B -m unittest`, one module at a time; all must be OK: `tests.cadence.test_legs_runner`, `tests.cadence.test_kit`, `tests.cadence.test_stops_desk`, `tests.cadence.test_runner_guards`, `tests.align.test_r1_smoke_launcher`. (At `b4b6aeb19` the in-tree `CommittedKitTests` test the in-tree kit, not the armed one; the armed kit is checked by `validate-kit` below.) Any failure: nothing launches; mail the lead.

```sh
git -C /Users/edr/code/JouleWise fetch origin align/2026-11-14-campaign-runner
test -e /Users/edr/code/jw-wt/cadence-dev02-s02 || git -C /Users/edr/code/JouleWise worktree add --detach /Users/edr/code/jw-wt/cadence-dev02-s02 b4b6aeb192da60d895a7529311b06599efff5be4   # reused on a retry after a WAIT
cd /Users/edr/code/jw-wt/cadence-dev02-s02
test "$(git rev-parse HEAD)" = b4b6aeb192da60d895a7529311b06599efff5be4 || { echo "STOP: HEAD"; exit 1; }
test -z "$(git status --porcelain)" || { echo "STOP: dirty tree"; exit 1; }
REPO="$PWD"
: "${PY:?Set PY to the existing pinned measurement-venv interpreter (do not resolve the symlink)}"
: "${MAGISTRATE_PID:?Set to the PID of this magistrate own claude process}"
ps -o pid=,comm= -p "$MAGISTRATE_PID"                 # must show the claude process
: "${PRIOR_CLOSE_EPOCH:?Set to the later of the last Sunday span runner_receipt ended.epoch_s and the epoch its fence was seen gone}"
SPAN=dev-02-s02; LEGS=L001,L002,L003,L004,L005,L006; DEADLINE_S=26210; EXPECT="expected_s 10656, worst_case_s 24750"
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
# The launch bands (EARLIEST 1794729600 Sun 00:00:00; LIMIT 1794815999 Sun 23:59:59; none 10:50:01-13:14:59)
pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3; bands from this pin's own plan)
  n=$1
  if   [ "$n" -ge 1794729600 ] && [ "$n" -le 1794738899 ]; then echo 13:14-13:15   # Sun 15 Nov 00:00:00 .. Sun 15 Nov 02:34:59
  elif [ "$n" -ge 1794738900 ] && [ "$n" -le 1794768600 ]; then echo 02:00-02:35   # Sun 15 Nov 02:35:00 .. Sun 15 Nov 10:50:00
  elif [ "$n" -ge 1794777300 ] && [ "$n" -le 1794798450 ]; then echo 02:00-02:35   # Sun 15 Nov 13:15:00 .. Sun 15 Nov 19:07:30
  elif [ "$n" -ge 1794798451 ] && [ "$n" -le 1794815999 ]; then echo 13:14-13:15   # Sun 15 Nov 19:07:31 .. Sun 15 Nov 23:59:59
  else echo NONE; fi
}
NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval ($GAP s) after the prior close"; exit 1; }
ARG="$(pick_arg "$NOW")"
test "$ARG" != NONE || { echo "STOP: no admitted launch band now (outside this item's window, or inside 10:50-13:15 where this pin cannot launch); mail the lead"; exit 1; }
export ARG; echo "ARG $ARG (RL-171 §3: 02:00-02:35 where this pin's own plan admits the t0, else the data-only 13:14-13:15)"
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"   # the watchdog's fence root (fence + launch spec only)
"$PY" -B -c 'from pathlib import Path; import subprocess; from joulewise.align.apple import v4_registration as r; root=Path.cwd(); head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(); print(r.verify_r1_executed_sources(root,{"executed_commit":head}))'
# must print b4b6aeb192da60d895a7529311b06599efff5be4

# Sol P1 and RL-172 (a): before the KIT and OUT exist, so a WAIT here is retried cleanly at the next activation
effective_close || { echo "STOP: the receipt census failed; mail the lead"; exit 1; }
copy_gate || exit 1
day_gate || exit 1
# The kit: from PR #775's head, OUTSIDE the checkout, sha asserted
mkdir -p /Users/edr/campaign-out/kits
KIT=/Users/edr/campaign-out/kits/cl-dev-02-589748f15-s02.json
test ! -e "$KIT" || echo "KIT exists from an earlier Start of this item (a WAIT retry): re-written from git below, sha asserted"
git -C /Users/edr/code/JouleWise show 589748f15:docs/process/cadence/kits/cl-dev-02.json > "$KIT"
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = d963500b39af8867576ab07e2086c22ffd4a176c9e2d6eb60c80f65bc03728a8 || { echo "STOP: kit sha"; exit 1; }
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG"
# must print ok true, frozen_commit b4b6aeb192da60d895a7529311b06599efff5be4, frozen_paths_verified true,
# kit_sha256 d963500b39af8867576ab07e2086c22ffd4a176c9e2d6eb60c80f65bc03728a8, legs 12

# The queue: committed bytes on the audit branch, sha asserted (the validate-queue line is the lead's, line 3)
git -C /Users/edr/code/JouleWise fetch origin audit/2026-11-10-fable
QCOMMIT=<LEAD FILLS: the append's commit on audit/2026-11-10-fable>
test "$(git -C /Users/edr/code/JouleWise show "$QCOMMIT":docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-dev-02-b4b6aeb19-6plus6-append.json | shasum -a 256 | cut -c1-64)" = ad0212ae0f57deea871ccb13ce8f8591ff3247ea406dc8e56dddc59f4f91ca2e || { echo "STOP: queue sha"; exit 1; }

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
# expect legs L001 to L006, budget_s 1251 each, $EXPECT, blackout_clear true
DEADLINE="$("$PY" -B -c 'import time; print(time.time()+'"$DEADLINE_S"')')"
```

NOTE 1 (ADOPTED by the lead; the rule is in the verify line above). `measurement_mode.zsh verify` fails a line "agent process present" for ANY `claude`/`codex`/MCP process (`pgrep -x claude`), which includes this magistrate. Rule: proceed only if every FAIL line is that one agent line and the PIDs it names are the magistrate's own process tree (record the lines); any other FAIL means STOP. WARN lines are recorded, not gates.

NOTE 2 (ADOPTED by the lead: the fence root stays the watchdog's; all campaign data under OUT). `--custody-root` is the watchdog's fence root (`/Users/edr/night-custody/magistrate`). All campaign data (soak, legs, receipt, desk bundle) go under OUT.

**Run (your last action):**

```sh
WORST_S=24750
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
  --kit "$KIT" --legs L001,L002,L003,L004,L005,L006 --batch-window "$ARG" \
  --output "$OUT" --disk-path "$REPO" \
  --custody-root "$CUSTODY" --magistrate-pid "$MAGISTRATE_PID" \
  --deadline "$DEADLINE" --exit-wait-seconds 180 --start-wait-seconds 30
echo "$OUT"
```

Require exit 0, `"next": "exit the magistrate session now"` with a claimed fence (fence `pid` ≠ `MAGISTRATE_PID`), and the launch output's `plan.batch_windows` equal to `["$ARG"]`, the argument chosen in Start and check (else report it; the span is not counted until the lead rules). Record ARG, LAST_CLOSE_KIND, GAP, the journal-copy line (plan id and marker content), the day_gate line, the batch-time print, SPAN, LEGS, PRIOR_CLOSE_EPOCH, PY, MAGISTRATE_PID, KIT and its sha256, the queue commit and sha, OUT, DEADLINE, HOST_RESTORE_OK, OTHER_CLOSE_EPOCH, the host last close printed, SESSION_READY, the launch time, the measurement_mode lines, the plan and **"dev-02-s01 WITHDRAWN UNARMED (RL-165 §2)"** in your RUN_STATE item and in `/Users/edr/night-custody/magistrate/cadence-dev02-s02-out-<activation>.txt`. Then exit at once, with no other `claude` or `codex` process running.

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

**Report** (by email to Ed and the lead, and as RUN_STATE TBD+1): the receipt line, the step list and RECEIPT OK (or the receipt in full); each leg's `leg_summary.json` line with `admitted` called out; `span/result.json` and `span/meter.json`; legs run and admitted (of 6) and, for any excluded leg, the inclusion rule it fell under; whether any named stop would fire; the RL-150 R1 print as printed; the restore and measurement_mode lines; the receipt's close epoch; whether the span crossed 00:00. The magistrate reports; it never decides. Commit nothing from `$OUT`. Nothing is re-run and nothing else is queued.

**After (the lead, at the desk; not the magistrate).** Copy the desk bundle to the Air (`/Volumes/JW-EXT/cadence-desk/cq-dev-02-s02-a1/input`) and build the automatic desk table (RL-149 §2.9 item 5 row 3); this desk must be FINAL before campaign span 9 arms (expected: the dev-03 pilot). No hand-read is required. Record `dev-02-s01` WITHDRAWN UNARMED in BLOCK-QUEUE. The standing F0 takes the rest of Sunday on its rules (close leaves no staged item within 2 h 30 min: the next counted span, `dev-02-s03`, is the Monday half and cannot arm before Mon 00:00:00). The Monday item arms `dev-02-s03` (L007-L012).
