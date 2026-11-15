TBD. **Laptop lead (interactive, Opus 5.5), drafted by the items-rl165 drafter 2026-11-14 PST and re-drafted under RL-171 by the items-rl171 builder 2026-11-15 PST, ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm the COUNTED PILOT of block dev-03, which is kit v1.1's class A smoke (RL-150 R5, RL-158 §2, RL-165 §1): kit `cl-dev-03.v1.1` (sha256 `0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b`), legs L001, L002, L003 only, span `dev-03-s01`, runner kind `cadence-legs-v1.1`, on `2d347f721552fe03bdd19f113e7bad7a7c24908e` checked out detached in a fresh scratch worktree. One span: a fresh soak, then three legs, one per prompt size: L001 2,000 tokens own-shaped (it captures the span's reference), L002 19,458 tokens span-shaped (the one consumer: its G0 is judged against L001's capture), L003 10,000 tokens own-shaped; decode cap 4,096, Automatic, band q0. They are counted development legs of dev-03 (kit rule `pilot_counted`). No other span, no queue extension, no session, no W1. EARLIEST: the close interval (RL-171 §6.1) after its predecessor `dev-02-s03` (dev-02's last span: Sunday's `dev-02-s02` ran and closed clean, RUN_STATE 345 and 349, so `dev-02-s01` is withdrawn unarmed) closed clean with its fence gone, with no further word from the lead (RL-165 §1), and not before 00:00:00 PST Mon 16 Nov (epoch 1794816000; this block's t0-date, RL-172 (a)). LAUNCH as soon as every gate holds, at any hour up to 23:59:59 PST Mon 16 Nov (LIMIT, epoch 1794902399; this block's t0-date, RL-172 (a)), except 10:50:00-13:15:00 (the pin's `fence_problems` refuses it under either argument). The batch-window argument follows the launch time (RL-171 §3): `02:00-02:35` from 02:35:00 to 10:50:00 and from 13:15:00 to 20:48:10; `13:14-13:15` from 20:48:11 to 02:34:59. ISSUED AHEAD (RL-173 D): this item names its predecessor `dev-02-s03` and requires that span's clean close receipt, else it is VOID and is not skipped; it EXPIRES 24 h after issue, so its window ends at the earlier of LIMIT and the expiry. The launch is your LAST action and you exit at once. If you cannot, do not launch; mail the lead (the standing F0 item then applies).**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-17T06:02:00-08:00
on_early_or_refused: VOID, so that nothing of this item ever launches (mail the lead; a new item is needed), if `dev-02-s03` closed without a clean receipt (RL-173 D.2) or once 24 h have passed since the issue (RL-173 D.5). Otherwise: any failed line of "Start and check", any launch refusal (rc≠0 or no claimed fence), or a launch that cannot happen inside (dev-02's close + the close interval) to 23:59:59 PST Mon 16 Nov (epoch 1794902399), outside 10:50:00-13:15:00: NOTHING of this item launches (a later t0 needs a new item); mail the lead, and the standing F0 item applies. A span that ran but ends with any named stop or a receipt rc≠0: nothing relaunches, nothing is re-run, nothing else is queued; mail the lead. Do not retry, do not extend, do not reuse OUT. The remainder (L004-L012) is NOT in this item: it arms only by its own item after the lead's hand-read records L002's G0 release (RL-158 §2)
next_observable: the next activation (after the fence is gone) runs "Check" below and reports, by email to Ed and the lead and as RUN_STATE TBD+1: the receipt asserts, the per-leg admitted lines with g0_role and span_reference, the desk bundle, the restore lines, measurement_mode verify again, and the RL-150 R1 / RL-158 Q1 print (gates nothing)
```

- **Issued ahead (RL-173 D; the interim until #800 is admitted; items-1115 builder, Sun 15 Nov 2026 PST).** (1) At most three counted spans are issued ahead of the machine, plus the standing F0. (2) **Predecessor: `dev-02-s03`** (dev-02's Monday half, issued ahead with this item). This item requires its clean close receipt: `pred_gate` below reads its `runner_receipt.json` (rc, error, roster, leg counts, span_result, close steps, close time) and its desk bundle's `leg_summary.json` files (wall against budget, contaminated redos), never an energy, power or meter value. No receipt yet is WAIT. A receipt that is not clean makes this item VOID: it is not skipped, nothing launches on its authority, and the lead decides. (3) Its date window is Mon 16 Nov (RL-172 (a)), and its own argument choice is `pick_arg` below. (4) Nothing is issued past a class A hand-read or an L002 or L005 gate. **Issuable now, with ITEM-dev02-s03** (two counted spans ahead plus the standing F0): no hand-read or L002/L005 gate lies before it; its own class A hand-read comes after it and holds everything span-shaped behind it. (5) It expires 24 h after issue: `expiry_gate` (ISSUED_EPOCH + 86,400 s) runs in Start and check and again just before the launch.
- **Why (RL-165 §1).** dev-03 arms as soon as its gate holds, on Monday if it can: RL-158 §3's "Tue 17 Nov" was a forecast, not a rule. **Two times.** If dev-03 is READY with this item, its queue and its worktree staged on the MBP by **Sun 23:30** (staging: `stage_mbp_span.sh dev-03-s01`, run by the lead over SSH in a close interval, evidence/align-v4-campaign/item-drafts-1115/stage_mbp_span.sh), this pilot arms at dev-02's close + the close interval (RL-171 §6.1) with no further word from the lead. If READY later, the lead stages it in a close interval and the pilot takes the first legal t0 (RL-171 retires the Mon 20:48:10 bound, which was the 01:50 fence; this item's window runs to Mon 23:59:59, its t0-date). RL-158 §2's cut-off stays Mon 18:00; v1.1a is not chosen earlier to fill Monday. A leg's calendar day is the local date of its span's t0, so these are Mon 16 Nov legs.
- **Order (RL-165 §1).** Monday after dev-02 closes: the R1 slot session if READY (R-A), then this pilot, then hp-01's unrun spans, then P, then the standing F0. <LEAD FILLS: "the R1 slot session is not READY at issue (<why>)", or "it ran and closed at <epoch>; PRIOR below is its close">.
- **READY: RL-158 §2's four lines, each recorded below (no line shortened to make Monday, RL-165 §1).**
  1. **Row-1 review passes:** ADMIT at `17f478675` (`/Volumes/JW-EXT/scratch/rev788/REVIEW.md`, two low-severity notes, no required fix). The cold-seat fixes that moved the pin to `2d347f721` were read by the Mythos delta seat (line 2). **No separate row-1 delta reading at `2d347f721` is recorded** (searched by the items-1115 builder, Sun 15 Nov: PR #788 has no review or comment; the audit branch's evidence holds only the two Mythos seats on #788; `/Volumes/JW-EXT/scratch/rev788/REVIEW.md` is the `17f478675` review). The precedent is item 334 (hp-01 at `dd206025a`): the lead recorded the Mythos delta seat as row 1's delta reading. Executed evidence at this pin: CI 43664825578 on the frozen-identical head `9cbb365a6` (`test_kit_v11` 30 tests, 0 skipped, line 2 D2) and the Air `validate-kit` and `plan` at `2d347f721` (items-rl171 `probe/`). <LEAD FILLS: the lead's decision: "the Mythos delta seat (ADMIT, `5b8d23727`) stands as row 1's delta reading for `2d347f721`, as item 334", or a row-1 delta seat is ordered and this item waits for it>.
  2. **The Mythos cold seat has no open finding and confirms `thermal_gates.py` and `r1_runtime.py` unchanged:** first seat ADMIT WITH FIXES (evidence/align-v4-campaign/mythos-kit-v11-788.md, audit `4c38dce3b`); delta seat on `2d347f721`, 18:04 PST: **ADMIT**, no finding needing a new pin or kit text, both modules unchanged from `b4b6aeb19` (evidence/align-v4-campaign/mythos-kit-v11-788-delta.md, audit `5b8d23727`). Its two owed record items are closed here: **D1** (the Air desk's checkout is named: this line's `desk.py`, see "After") and **D2** (line 2's run id and the identity tests' skip count, arm-record line 2). RL-161 §3's F7 table is recorded in arm-record line 1.
  3. **CI on the pinned commit:** arm-record line 2, in RL-165 §5's four parts.
  4. **Q6 and the queue (RL-158 Q6; RL-161 §1, §2):** on the 3 + 9 layout, consumers are **5 of the 10 warm legs** (L002, L008, L009, L010, L012; L004 is first in its span and captures), at least half; the count goes in the ledger row. The layout is committed; the first queue holds the pilot span only, and the remainder's entry is appended after the hand-read (RL-161 §2). The Air `plan` at `2d347f721` gives the same roles: pilot consumer L002; remainder consumers L008, L009, L010, L012.
- **Day law (RL-172 (a), which replaces the two-starts default):** a day is the local date of a span's t0. No t0-date holds more than 12 mixed-size development legs (dev-03, dev-04, dev-05) or more than 24 development legs; qualification t0-dates are disjoint from development t0-dates; hp-01, F0, F2 and v4 sessions are outside the count. **This span's t0-date is Mon 16 Nov** (dev-03, 12 mixed-size legs over the pilot and the remainder); this item's window admits only that date. A span that misses its date is re-dated by the lead with a new item, never doubled up. Planned: Sat 7, Sun 11, Mon 18 (dev-02-s03 and dev-03), Tue 12 (dev-04), Wed 12 (dev-05). Because the queue does not yet enforce dates, `day_gate` counts the development legs already launched on the t0-date from their receipts and refuses this span past either cap; the committed queues' `not_before` values are lower bounds only.
- **Two separate records after this span (RL-161 §2).** R9 decides whether the pilot's legs count. The class A smoke of the span-reference leg is met only when **L002 released its G0 against L001's capture and ran its turn.** The lead records both, on separate lines.
- **Counted.** The three legs count as development legs of dev-03 under the kit's inclusion rules (RL-149 §2.3, §2.4 as amended by RL-150 R7 and R8; rule 2 against the reference its kit shape names). An excluded leg is refilled only from the reserve under RL-149 §2.4. A re-run is a new span with `attempt` + 1 and `rerun_of`, and it needs a ruling.
- **Bytes.** Measured from `2d347f721552fe03bdd19f113e7bad7a7c24908e` (PR #788, branch `align/2026-11-14-kit-v1-1`, cold-seat fixes F3, F4, F6, F8 and dev-01 F5, F8). The kit is NOT read from that commit: it is `cl-dev-03.v1.1.json` from the PR head `9cbb365a6957c3737617d8604ba6d06071ab018c` (the re-pinned draft), sha256 `0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b`, copied outside the checkout. Its `frozen` block names `2d347f721` and 38 paths; `git diff 2d347f721 9cbb365a6` over them is empty. Master seed 2026111403 (unchanged, RL-161 §4). **No rebase onto a #777 commit (RL-165 §5):** the base-equality reading of line 2 extends to this pin and ends at the qualification re-pin, so this pin keeps both of RL-155a §3's bounds in code: RL-171 §3 moves off the fence by the argument `13:14-13:15`, and the 10:50-13:15 refusal stays until the qualification pin.
- **What is new in these bytes (class A).** The span-reference leg: a consumer reads the span's reference from the first leg's accepted attempt (`<this span>/legs/L001/runtime`), verified by `thermal_gates.load_window_reference` (unchanged); a missing or unobserved reference is a REFUSAL that stops the span (RL-158 Q3). The free t0, with the launch bounds in code (v1.1 F4): `legs.fence_problems` refuses a fence end that passes ten minutes before the window passed in `--batch-window` (01:50:00 for `02:00-02:35`; 13:04:00 for `13:14-13:15`) and, under either argument, any t0 strictly between 10:50 and 13:15 (it reads the soak window from `OS_BATCH_WINDOW_LOCAL`, 11:45-13:15 at this pin, not from the argument). Air `plan` at `2d347f721`, 2026-11-15: with `02:00-02:35` 20:48:10 accepted, 20:48:11 refused, 10:50:00 accepted, 10:50:01 refused; with `13:14-13:15` 08:02:10 accepted, 08:02:11 refused, 13:15:00 accepted (`/Volumes/JW-EXT/scratch/items-rl171/probe/plan/dev03-s01-*`). `--batch-window` is required. The desk's `admitted` column and the cell section with the MARK lines (dev-01 F8; #788 F3).
- **Condition-13 sources are byte-identical to the base** (`v4_registration.R1_EXECUTED_SOURCES`; the Mythos delta seat confirms `cadence_leg_runtime.py`, `r1_runtime.py`, `thermal_gates.py`, `workload.py`, `align_r1_rehearsal.py`, `run_align_r1_smoke.py` are the same blobs at `b4b6aeb19` and `2d347f721`). `verify_r1_executed_sources` must return the full sha.
- **Timing.** Plan for this roster (`plan` at `2d347f721` with both arguments, blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-dev03-s01.txt`): expected 7,024 s (2.0 h), worst case 16,650 s (4.6 h), budgets L001 1,076 s, L002 1,642 s, L003 1,156 s. Fence deadline launch + 18,110 s.
  - **Bands (RL-171 §3; the `pick_arg` function below), on Mon 16 Nov:** 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-20:48:10 `02:00-02:35`; 20:48:11-02:34:59 `13:14-13:15` (which admits three legs up to 08:02:10). A mock span at t0 Mon 00:30 with `13:14-13:15` (L003 across 02:00): rc 0, 3 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/dev03-s01-alt-00:30/`).
  - Forecast t0 Mon 03:02:36 (dev-02-s03's expected close 02:57:36 + 5 min), argument `02:00-02:35`: expected end 04:59:40, worst end 07:40:06, fence end 08:04:26.
  - The remainder (nine legs) can then take any t0 outside 10:50-13:15 by the same argument rule (ITEM-dev03-rest).
  - Pointer deadline = latest fence end (LIMIT + 18,110 s = Tue 05:01:49) + 1 h.
- **Conditions.**
  - RL-171 retires "activation not inside 01:30-02:40" with the quiet: quiet is the per-leg agent census, process census and rule 5.
  - No agent session on the MBP during the span: you exit at once after the launch. No lead SSH, desk job or R12 process until the fence is gone.
  - Restore before the launch and again in "Check": AC, powermode 0, network time OFF, kernel frequency word 0 (item 251's remedy if not), no stray `km003c_monitor.py` / `hazard_monitor.py` / root `powermetrics`, no High Power marker, `night.lock` with no holder. `sudo -n -l /bin/kill` rc 0. Leave `night.lock` as found.
  - Every `validate-kit`, `plan` and `launch` passes `--batch-window "$ARG"` (chosen once in Start and check by the launch time, re-checked in Run; RL-171 §3) and `--legs L001,L002,L003` written out; the arm record shows the plan's `batch_windows` (RL-150 §2 F2; Mythos #788 delta D4: the code accepts any `HH:MM-HH:MM`, so the record shows the value).
  - The arm record carries the measurement_mode line and states the host is in measurement_mode as applied 11-13 23:47 with network time off, checked remotely (RL-150 §2 F5; RL-161 §3).
  - Do NOT run `cadence_queue.py checklist` or `next`.
  - Output root `/Users/edr/campaign-out/cl-dev-03/` is a new path outside every v4 registration and custody root (RL-149 §2.8 line 4; dev-01 F6 as deferred by RL-161 §3).
- **Blinding.** Open no energy, power, meter-sample, transcript or slot file. From each leg bundle read ONLY `outputs/align_window_reference.json` (where present: the capture leg) and `outputs/align_thermal.jsonl`, and from each leg directory `leg_record.json`, with the scripts below. Never print a KM003C stream line; never open `powermetrics*`, `hazards/`, `align_episode.json`, `telemetry*` or anything under `runs/*/outputs/` other than those two files.
- **May run:** this span, once. **May NOT:** L004-L012 (any span of them), dev-04, dev-05, any other span, any session, W1, any filler while this span is armed.
- **High Power marker:** if `/Users/Shared/JouleWise/host-power/high-power.marker` exists, STOP and report.

- **Host gate and R1 reservation, immediately before the launch (Sol items review P1-1, P1-2; RL-155 R-B; RL-165 §7).** Separate from this item's campaign dependency: the Check of the latest close of ANYTHING on this host (any span, Part C or F0, slot session or W1) reported every restore line OK; no desk fence; no night or smoke agent loaded; no High Power marker; at least GAP seconds since that latest close (RL-171 §6.1, amending RL-155 R-B's 20 minutes: GAP is QUIET_CAMPAIGN_S after a campaign span's close, 300 s, confirmed by RL-172 §0; GAP is 1,200 s after a Part C or F0, F2, a slot session or W1) (the newest `runner_receipt.json` under `/Users/edr/campaign-out` and `/Users/edr/code/jw-wt`, from a census that stops on a missing root, any lookup error or an empty result, with fractional mtimes rounded up; or a session's close given as OTHER_CLOSE_EPOCH, a whole epoch or an explicit 0); and, after a CAMPAIGN close, that close's journal copy complete and hash-verified, shown by the marker `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok`, written only after the copy is verified (by the lead's Air copy, or by the MBP's own verified encrypted cloud offload, items 347 and 348, which RL-173 A makes the off-host copy permanently; a failed or unverified offload writes no marker and holds the arm, RL-173 A 7) (Sol items-rl171 P1; a missing marker is WAIT; no SSH once a span is armed). Read fresh at the launch: if a v4 slot session is READY and staged for this slot, this span cedes; RL-172 (f) retires RL-165 §7's worst-case reservation: from the lead's record that a v4 session is READY nothing of lower priority arms, and the session takes the next clean close; before that record this span arms as usual.

**RL-149 §2.8 arm-record lines (record each, with its evidence):**
1. Kit `ruling` is `RL-149 §2`; the cell law and span-reference leg are ruled by RL-158 and RL-161. Kit `cl-dev-03.v1.1` `0f535774…e14b` on `2d347f721`: row-1 ADMIT at `17f478675` (READY line 1); Mythos 5.2 first seat ADMIT WITH FIXES and delta seat ADMIT (READY line 2); `validate-kit` below (Air, 2026-11-14: ok, frozen_paths_verified true, 12 legs, `/Volumes/JW-EXT/scratch/items-rl165/evidence/validate-kit-dev03-v11.json`). **RL-161 §3's F7 table:** dev-01 F5 (the campaign-scope stop sentence) is in the kit's `stop_rules.notes`, and because the validator does not check `notes` this line carries it: "RL-149 §2.4: REFUSAL, restore unproven, disk or watcher down (span; the lead clears); INSTRUMENT_FAULT (span; the research lead clears); CONTAMINATED_REDOS, 3 in a span (the lead once, then the research lead); LEG_OVERTIME, two legs over 1.5 x their budget in a span (the lead); …" (the kit's text, in full at the arm); dev-01 F6 deferred: the output root is named and outside the v4 roots, and line 7 carries the watcher stamp; dev-01 F8 (`admitted` column) rides this pin in `desk.py`; **dev-01 F11, by hand:** `kit.model` `mlx-community/Qwen3.8-27B-8bit` agrees with the frozen `configs/campaigns/align_v4/registration/inputs.json` (`model_source` /Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit) and `configs/align/v4/qwen38-27b-8bit-hf-pins.json` (`repo` mlx-community/Qwen3.8-27B-8bit) at `2d347f721`; F7, F9, F10, F12 need nothing in the kit.
2. Line 2, in RL-165 §5's four parts (the base-equality reading, extended to this pin; it ends at the qualification re-pin):
   1. **Same bytes.** CI `ci` run 43664825578 on the PR #788 head `9cbb365a6`, whose diff against `2d347f721` over the kit's 38 frozen paths is empty (the head adds only the two kit files and three lines of `tests/cadence/test_kit_v11.py`). CI `ci` run 43664825578 on `9cbb365a6` COMPLETED 2026-11-14 20:47:37 PST, conclusion **failure** (9 of 12 `test` shards red; every other job success). Shard 11 was not stalled: it finished at 3 h because `tests.test_bytes_analysis` took 9,107 s and passed. The final red set is **exactly the 12 tests of `fe907d0d3`'s CI 43600776368, test for test, with no added red** (both sets re-derived from the job logs by the items-1115 builder, Sun 15 Nov 15:03 PST; evidence/align-v4-campaign/item-drafts-1115/evidence/line2-dev03-red-9cbb365a6.txt and line2-base-red-fe907d0d3.txt).
   2. **Red set.** It equals `fe907d0d3`'s (CI 43600776368), the 12 tests of RL-155a §4, test for test: final, all 12 shards: the 12 base reds and no other (the twelfth, `align.test_v4_dynamic_closure.LiveTraceTests.test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace`, failed in shard 11 as it did in the base); no added red. **An added red is fixed and re-run, not accepted on an explanation** (RL-165 §5).
   3. **Each of the 12 passes at a #777 head:** CI 43601158271 on `ae340d3da` (success, full suite).
   4. **Recorded diff (RL-165 §5 part 4).** Against `b4b6aeb19`, over the 38 frozen paths, seven files differ: `joulewise/align/apple/cadence_leg.py`, `joulewise/cadence/desk.py`, `kit.py`, `kit_v11.py` (new), `legs.py`, `scripts/cadence_legs_runner.py` and `scripts/launch_cadence_span.py` (683 insertions, 44 deletions). The meter driver `joulewise/b5/driver.py` (`ff4fd76a`) and `scripts/km003c_monitor.py` (`7d6acc98`) are identical at `fe907d0d3`, `b4b6aeb19`, `2d347f721`, `1b20d3b0e` and `9cbb365a6`. Evidence: `/Volumes/JW-EXT/scratch/items-rl165/evidence/frozen-path-diffs-vs-b4b6aeb19.txt`.
   - **D2 (Mythos #788 delta):** `tests.cadence.test_kit_v11` ran in shard 7 of run 43664825578 with 30 tests, 0 failures, **0 skipped** (`/Volumes/JW-EXT/scratch/dev03-line2/logs/A-shard7.log`), so the frozen-hash and leg-byte identity tests ran against both pins.
3. Queue `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-dev-03-2d347f721.json` on audit/2026-11-10-fable at `b7a0d9882` (`b7a0d98822865a01e67fc3cc1833c9b186be2181`, Sun 15 Nov 00:22 PST; validate-queue re-run ok at `2d347f721` on the committed bytes, Sun 15 Nov 15:05 PST, evidence/align-v4-campaign/item-drafts-1115/evidence/validate-queue-1115.log), sha256 `403e53f91df6f34589a538b506cf57739e5f9d16770adc1e30c5a2a5ea527da2`: queue `cq-cl-dev-03`, one span (`dev-03-s01`, L001-L003, attempt 1, not_before 2026-11-16, plan id `cq-dev-03-s01-a1`), pinning `cl-dev-03.v1.1` by sha `0f535774…e14b`, `expires_at` 2026-11-21T23:59-08:00 (within 7 days only for a commit at or after Sun 15 Nov 00:00 PST). `validate-queue` ok at `2d347f721` with `--kits-root` the #788 head checkout (`/Volumes/JW-EXT/scratch/items-rl165/evidence/validate-queue-dev03.log`). The remainder's entry is appended after the hand-read (RL-161 §2). Do NOT run `cadence_queue.py next`.
4. `validate-kit` passes (its `deny_scan` refuses any condition/slot/instruction key or label); OUT is outside every v4 registration and custody root (check below).
5. The per-span checks of design doc §4 and §14 pass at the arm (Start and check) and at the close (Check). Do NOT run `cadence_queue.py checklist` (Mythos #788 delta D5: it reads its soak window from `kit.OS_BATCH_WINDOW`; this item's epoch gates and the launcher's code bounds are the check).
6. No named stop, veto or halt open: no open `directive` issue by `mpmdw` whose title or first line starts STOP/NO/HALT/VETO, no open `cadence-stop` issue (gh on the MBP runs in the GUI context: `launchctl asuser`). By hand: no named stop open from any dev-02 or hp-01 span, no RESTORE_UNPROVEN and no High Power `revoked` hold: <LEAD FILLS: span ids, their desk `stops.json` result and the time read>.
7. Results-ref watcher live within 24 h (RL-173 C 5: one observation under 24 h old may serve more than one arm; `watch_gate` re-checks WATCH_UNTIL_EPOCH at this arm; a GitHub Actions watcher meeting RL-173 C 1-4 may stand instead, by a re-issue that reads its latest completed run): <LEAD FILLS: the Air results watcher (`com.joulewise.air-watch`) heartbeat stamp, under 24 h old at the arm; pid and commit>.
8. Not applicable: this span is dev-03's pilot and kit v1.1's class A smoke (RL-150 R5, RL-158 §2). Its R9 and its smoke line gate the remainder.
9. Line 9, across blocks in run order (RL-165 §6). Expected: this pilot is campaign span 9 (1 dev-01 pilot, 2 `dev-01-s03`, 3 `dev-01-s04`, 4-6 hp-01's three spans, 7 `dev-02-s02`, 8 `dev-02-s03`), so span 7's desk (expected `dev-02-s02`) must be FINAL. As run: this span is campaign span <LEAD FILLS: N>, and the desk of the span two back, <LEAD FILLS: SPAN ID>, is FINAL: <LEAD FILLS: the desk's stamp and where it is recorded>.

**Start and check (while you are still alive).** From a FRESH scratch worktree detached at the full sha (NOT the canonical clone's checkout, not a dev-01, dev-02 or hp-01 worktree), own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONPATH=.:tests`, `python3.13 -B -m unittest`, one module at a time; all must be OK: `tests.cadence.test_kit_v11`, `tests.cadence.test_span_reference`, `tests.cadence.test_legs_runner`, `tests.cadence.test_kit`, `tests.cadence.test_stops_desk`, `tests.cadence.test_runner_guards`, `tests.cadence.test_launch_cadence_span`, `tests.align.test_r1_smoke_launcher`. (At `2d347f721` the kit files are not in the tree, so `test_kit_v11`'s four committed-kit tests skip; they ran with 0 skips in CI shard 7, line 2 D2. The armed kit is checked by `validate-kit` below.) Any failure: nothing launches; mail the lead.

```sh
git -C /Users/edr/code/JouleWise fetch origin align/2026-11-14-kit-v1-1
test -e /Users/edr/code/jw-wt/cadence-dev03-s01 || git -C /Users/edr/code/JouleWise worktree add --detach /Users/edr/code/jw-wt/cadence-dev03-s01 2d347f721552fe03bdd19f113e7bad7a7c24908e   # reused on a retry after a WAIT
cd /Users/edr/code/jw-wt/cadence-dev03-s01
test "$(git rev-parse HEAD)" = 2d347f721552fe03bdd19f113e7bad7a7c24908e || { echo "STOP: HEAD"; exit 1; }
test -z "$(git status --porcelain)" || { echo "STOP: dirty tree"; exit 1; }
REPO="$PWD"
: "${PY:?Set PY to the existing pinned measurement-venv interpreter (do not resolve the symlink)}"
: "${MAGISTRATE_PID:?Set to the PID of this magistrate own claude process}"
ps -o pid=,comm= -p "$MAGISTRATE_PID"                 # must show the claude process
: "${PRIOR_CLOSE_EPOCH:?Set to the later of dev-02 last span runner_receipt ended.epoch_s and the epoch its fence was seen gone (or the slot session close, if it ran first)}"
SPAN=dev-03-s01; LEGS=L001,L002,L003; DEADLINE_S=18110; EXPECT="expected_s 7024, worst_case_s 16650"
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
PRED_SPAN=dev-02-s03; PRED_CAMP=cl-dev-02; PRED_ROSTER=L007,L008,L009,L010,L011,L012
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
  elif [ "$n" -ge 1794863700 ] && [ "$n" -le 1794890890 ]; then echo 02:00-02:35   # Mon 16 Nov 13:15:00 .. Mon 16 Nov 20:48:10
  elif [ "$n" -ge 1794890891 ] && [ "$n" -le 1794902399 ]; then echo 13:14-13:15   # Mon 16 Nov 20:48:11 .. Mon 16 Nov 23:59:59
  else echo NONE; fi
}
NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval ($GAP s) after the prior close"; exit 1; }
ARG="$(pick_arg "$NOW")"
test "$ARG" != NONE || { echo "STOP: no admitted launch band now (outside this item's window, or inside 10:50-13:15 where this pin cannot launch); mail the lead"; exit 1; }
export ARG; echo "ARG $ARG (RL-171 §3: 02:00-02:35 where this pin's own plan admits the t0, else the data-only 13:14-13:15)"
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
KIT=/Users/edr/campaign-out/kits/cl-dev-03.v1.1-9cbb365a6-s01.json
test ! -e "$KIT" || echo "KIT exists from an earlier Start of this item (a WAIT retry): re-written from git below, sha asserted"
git -C /Users/edr/code/JouleWise show 9cbb365a6957c3737617d8604ba6d06071ab018c:docs/process/cadence/kits/cl-dev-03.v1.1.json > "$KIT"
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = 0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b || { echo "STOP: kit sha"; exit 1; }
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG"
# must print ok true, campaign_id cl-dev-03, frozen_commit 2d347f721552fe03bdd19f113e7bad7a7c24908e, frozen_paths_verified true,
# kit_sha256 0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b, legs 12

# The queue: committed bytes on the audit branch, sha asserted
git -C /Users/edr/code/JouleWise fetch origin audit/2026-11-10-fable
QCOMMIT=b7a0d98822865a01e67fc3cc1833c9b186be2181
test "$(git -C /Users/edr/code/JouleWise show "$QCOMMIT":docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-dev-03-2d347f721.json | shasum -a 256 | cut -c1-64)" = 403e53f91df6f34589a538b506cf57739e5f9d16770adc1e30c5a2a5ea527da2 || { echo "STOP: queue sha"; exit 1; }

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
# expect L001 (2000, capture) budget 1076, L002 (19458, span, consume) 1642, L003 (10000) 1156; $EXPECT; blackout_clear true
DEADLINE="$("$PY" -B -c 'import time; print(time.time()+'"$DEADLINE_S"')')"
```

NOTE 1 and NOTE 2 as in item 321 (ADOPTED by the lead): the measurement_mode agent-line rule above, and the watchdog's fence root with all campaign data under OUT.

**Run (your last action):**

```sh
WORST_S=16650
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
  --kit "$KIT" --legs L001,L002,L003 --batch-window "$ARG" \
  --output "$OUT" --disk-path "$REPO" \
  --custody-root "$CUSTODY" --magistrate-pid "$MAGISTRATE_PID" \
  --deadline "$DEADLINE" --exit-wait-seconds 180 --start-wait-seconds 30
echo "$OUT"
```

Require exit 0, `"next": "exit the magistrate session now"` with a claimed fence (fence `pid` ≠ `MAGISTRATE_PID`), and the launch output's `plan.batch_windows` equal to `["$ARG"]`, the argument chosen in Start and check (else report it; the span is not counted until the lead rules). The launcher itself refuses a fence end (worst case + 1,460 s) that passes ten minutes before the window in `--batch-window` (01:50 for `02:00-02:35`, 13:04 for `13:14-13:15`), a t0 strictly between 10:50 and 13:15 under either argument, a deadline under the plan's worst case plus reserves, a missing kit and a missing `--batch-window`. Record the pred_gate line (RL-173 D.2), the expiry line (D.5), ARG, LAST_CLOSE_KIND, GAP, the journal-copy line (plan id and marker content), the day_gate line, the batch-time print, SPAN, LEGS, PRIOR_CLOSE_EPOCH, PY, MAGISTRATE_PID, KIT and its sha256, the queue commit and sha, OUT, DEADLINE, HOST_RESTORE_OK, OTHER_CLOSE_EPOCH, the host last close printed, SESSION_READY, the launch time, the measurement_mode lines and the plan in your RUN_STATE item and in `/Users/edr/night-custody/magistrate/cadence-dev03-s01-out-<activation>.txt`. Then exit at once, with no other `claude` or `codex` process running.

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
- the receipt line, the step list and RECEIPT OK (or the receipt in full if not clean);
- each leg's `leg_summary.json` line, with `admitted`, `g0_role`, `g0_outcome`, `g0_s` and `span_reference` called out per leg;
- **L002's line in full: did its G0 release against L001's capture, and did it run its turn?** (the class A smoke line, RL-161 §2);
- `span/result.json` and `span/meter.json`;
- legs run and admitted (of 3); for any excluded leg, the inclusion rule it fell under; whether any named stop would fire (the Air desk builds `stops.json` from the bundle);
- the RL-150 R1 / RL-158 Q1 print above, as printed;
- the restore lines and the measurement_mode verify lines; the receipt's close epoch;
- whether the span crossed 00:00 (the `/private/tmp` walk; not a gate).

The magistrate reports; it never decides. Commit nothing from `$OUT`. Nothing is re-run and nothing else is queued.

**After (the lead, at the desk; not the magistrate).**
- **The Air desk (Mythos #788 delta D1).** Copy the desk bundle to the Air (`/Volumes/JW-EXT/cadence-desk/cq-dev-03-s01-a1/input`) and build the table from a checkout of THIS line, at `2d347f721` (or `1b20d3b0e`: `desk.py` is one blob on both), with the kit copied outside the checkout. An Air desk at `b4b6aeb19`, `main` or the hp-01 line refuses every dev-03 bundle (`desk._project` refuses the four new `leg_summary` keys). The arm record of every dev-03 span names the desk's checkout: `/Volumes/JW-EXT/jw-wt/desk-final-pin-2d347f721` (detached at `2d347f721`, clean; checked by the items-1115 builder Sun 15 Nov), or, under RL-173 B, the MBP's deterministic desk at the same commit in the close interval, named in the arm record.
- **The hand-read (RL-150 R5; RL-158 Q1, Q2; RL-161 §2, §4).** Read the journal table once by hand beside the automatic desk, with Q1's print: the soak reference, L001's capture, and L002's release reading and G0 wait. Mark the span "reference from a redo" or "reference from an excluded leg" if the receipt's `span_reference` says so. Report any leg whose realized prefill count is more than 5 % from its nominal (RL-158 Q5).
- **Two lines, recorded separately (RL-161 §2):** (1) R9: three closes with complete records, the admitted count, any excluded leg and its rule, hand table and desk agree (inclusion included): VERDICT; (2) the class A smoke: L002 released its G0 against L001's capture and ran its turn: MET or NOT MET.
- **The remainder's gate is the two recorded verdicts, nothing more and nothing less (Sol items review P2-6):** R9 **PASSED** and the class A smoke **MET**. R9 keeps its own allowance: it can pass with two of three legs admitted when the one excluded leg fell under rule 2 or 5 and its other conditions hold (RL-150 R9), so for example L003 timing out at G0 does not by itself hold the remainder if L002's smoke line is met.
- **If R9 PASSED and L002 released its G0 (smoke MET):** the remainder arms on the lead's record (RL-158 §2). Append the remainder to the queue: `QUEUE-cl-dev-03-2d347f721-append-both.json` (sha256 `366662cecb9794b9d13dbc67dd5721acd2bdf00b5055cc8df70861c07b593fbb`, re-written by the items-rl171 builder with `dev-03-s03b`'s not_before 2026-11-17 moved to 2026-11-16; `dev-03-s02` L004-L012, and the 3 + 3 + 6 pair `dev-03-s02b` L004-L006 / `dev-03-s03b` L007-L012, each `rerun_of: dev-03-s02`, which ITEM-dev03-rest withdraws unarmed; validate-queue ok at `2d347f721`, four plan ids, `/Volumes/JW-EXT/scratch/items-rl171/queue/validate-queue.log`), committed after this hand-read, and issue ITEM-dev03-rest.
- **If L002 timed out at G0 (RL-158 §2; RL-165 §4):** the remainder does not arm, and Q1's print goes to the research lead. **Nothing span-shaped arms until the research lead rules:** not dev-03's remainder, not dev-04 or dev-05 on v1.1. The machine goes straight to the ladder: the slot session if READY, hp-01's unrun spans, then the standing F0. **Own-shaped legs may arm without the research lead:** the next campaign span is dev-03's L004-L012 on `cl-dev-03.v1.1a` (pin `1b20d3b0e`, kit `4bf7f294…d133`), only if a cold seat has confirmed that its cells and seeds equal v1.1's leg for leg and its line 2 holds under RL-165 §5 (CI `ci` run 43664975416 on `1b20d3b0e` completed with conclusion failure; its red set must equal the base's, test for test); that span needs its own item. If the cells or seeds are not equal, that comes to the research lead. dev-04 and dev-05 then need the builder's own-shaped kits (RL-165 §4).
- **If R9 does not pass, or a named stop is open:** the remainder does not arm; the lead's diagnosis goes as R9 says (RL-155 §3.2), and the ladder takes the machine.
- Record the realized consumer count in the ledger row (RL-158 Q6). This desk must be FINAL before campaign span 11 arms (expected: dev-04's first span). Ledger: `dev-03` READY to RUNNING.
