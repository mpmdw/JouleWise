# BETA attempt 1 consult: blind seat answer (Opus 5.5)

(Returned as the agent's final message on 2026-10-10 at about 07:38 PDT; written to this file by the
magistrate, activation cbe4230e. The three programs B, C and D of its last section are summarized, not
copied; program A is `screen_branch_count.py` beside this file, byte for byte as the seat wrote it.)

Read-only throughout. I opened only the permitted files, plus the code and the registration. I ran no program over a restricted file and no project code. Paths under `joulewise/`, `scripts/` and `configs/` are relative to `/Users/edr/code/JouleWise-wt-harvest-cap`.

**Bottom line:** the permitted evidence cannot say which branch emitted `neg8.screen_failed`. One 2-second count program (A, below) settles it and should run before any arm, because one outcome means attempt 1 may be recoverable by a harvest fix. Otherwise I recommend (b): arm BETA attempt 2 today from unchanged code, with a clock fence on later arms.

## Cause

### (a) Every condition that emits `neg8.screen_failed` when the bound is derived and validated, in code order

1. **Verdict file is not a JSON object**: reason `verdict_unreadable` (`joulewise/b5/harvest.py:4769-4778`). An absent verdict emits only `whole_window.verdict_absent` (4759-4763).
2. The screen is deferred until after the physics joins (4802-4805, 5493-5498). `neg8_screen` then labels the stored bracket: `bracket_absent` (4902), `bracket_not_passed` (4904), `neg8_conditions` (4906).
3. **The stored bracket never decides a corpus-18 window.** `neg8_corpus_physics` sets `neg8_clean_bound_required = True` whenever a bound was derived (5385) and sets `neg8_clean_bound` when the first-12 clean bound validates (5474-5476). So `survivors` (4920) is always true, the early return at 4926-4928 is unreachable, and `_neg8_rescreen` always runs (4934-4938). Candidate (iii) therefore reduces to "the re-screen did not run or did not pass".
4. **Re-screen not evaluated** (4953-4956, then 4965). Any one of these problems does it:
   - `bracket_absent` (5242).
   - `conditions_beyond_bound_underived` (5244). Not possible here: a corpus member was physics-dropped, so `loss_rescreen` is true (4922-4923, 5477).
   - `clean_bound_unavailable` or `collected_bound_unavailable` (5247-5254). Not possible here: `clean_bound_validated` is true.
   - `evaluation_time_unrecorded` (5263).
   - A source problem from `verdict_neg8_sources` (5269-5271; names at 1123-1171): `policy_unregistered`, `evaluation_basis_invalid`, `source_manifests_unrecorded`, `source_manifest_path_invalid`, `source_manifest_unauthenticated`, `source_manifest_policy_differs`, `source_manifest_members_invalid`, `evaluation_basis_projection_failed`, `not_point_drift`.
   - `rederivation_failed:<problem>` (5300, 5310). The core's problems are `provenance` (`joulewise/whole_window.py:4937, 4964, 4967, 4981, 4984, 4988, 5088`), `bundle_strict_invalid` (5057) and an energy-evidence problem (5109-5110).
   - `rederivation_invalid` (5302, 5312).
   - `rederivation_differs_from_stored_bracket` (5304-5306; comparison at 1053-1068, with the bound-dependent fields removed at 1007-1010).
   - `rederivation_raised:<Type>` (5314).
5. **Re-screen evaluated but not "passed with no condition"** (4948). Conditions come from `evaluate_neg8_point_drift`:
   - `neg8_drift_bound_underived` and `neg8_idle_sub_drift_bound_underived` (`whole_window.py:2210-2212`).
   - `neg8_drift_bound_stale` (2229). The horizon is 86,400 s (149), so age cannot be the cause in a 6-hour chain; the other trigger is the calibration identity (1385-1425).
   - `neg8_bracket_missing` (2276).
   - `neg8_bracket_reference_invalid` (2278, 2292): fewer than 2 or more than 3 survivors at an endpoint (141, 2267-2275). With a loss behind it, `survivor_screen` is `references_insufficient` (2424-2430), which the harvest copies to `observed.reason` (`harvest.py:4959-4961`).
   - `neg8_bracket_abs_delta_exceeded` (2333) and `neg8_bracket_idle_sub_abs_delta_exceeded` (2340): the statistic exceeded bound(n_s, n_e).
   - For any shape other than (3, 3) the bound is recomputed from the clean artifact's corpus members (1985-2024). That path has never run in a live window: ALPHA attempt 1 was 3/3/1 with no loss. If it returns `None`, `screen_passed` is false (2149-2153) and both "exceeded" codes appear with no drift. I checked that the rebuilt artifact carries the point fields (1609, 1614), so I rate this low.

### (b) What is consistent with this window

Three paths ran together for the first time in a live window: a run-time reference loss, a spare with no bundle, and a corpus physics drop. ALPHA attempt 1 exercised none of them. Three branches remain; the percentages are my judgment, not a computed quantity.

- **(i) `references_insufficient` at the end endpoint: about 45%.** Two end references survived run time. One harvest loss code on either (`NEG8_REFERENCE_LOSS_CODES`, `harvest.py:91-127`) leaves one.
  - The contention rule is strict: any outside process above 0.05 CPU-s/s in any journal interval that overlaps the request is `contention.request_overlap` (3213-3229). Only `kernel_task` is exempt (319).
  - The end stage has 13 over-limit intervals of 82. Nine of them fall in the 46 intervals between the stage's settle and the spare's settle: two single intervals, then seven consecutive `syspolicyd` intervals (8 offender rows).
  - Those seven lie inside one continuous stretch where the measurement tree was active, so a reference's cycle was in progress.
- **(ii) Screen ran on (3, 1, 2) and the statistic exceeded bound(3, 2): about 25%.** This fits if the `syspolicyd` burst is what aborted the one member at run time, leaving two clean survivors.
- **(iii)/(iv) Re-screen not evaluated: about 30%.** Any problem in item 4. The registration itself records one known route to `rederivation_differs_from_stored_bracket` that excludes a window without physics (registration lines 1108-1113).

Start-endpoint insufficiency is unlikely: 3 of 3 succeeded, and only 7 of 124 start-stage intervals are over the limit.

### (c) The spare

- **What it is.** A byte copy of the stage's first reference config with its own run id, carrying the slot's role and sentinel position (registration 997-1003). I confirmed this by diffing the end spare against the first end reference in the sealed clone: only `run_id` differs.
- **When it runs.** After a reference stage, the chain counts members whose summary status is `succeeded`. If k = planned − succeeded > 0, it runs the committed spare set of size k once, after a 60 s settle (`joulewise/b5/chain.py:863-893, 1256-1305`; `chain.zsh:844-868`).
- **Could it have counted?** Yes. It has the end role, so the evaluator reads it at the end position (`whole_window.py:4971-4973`; registration 1163-1164).
- **Here it left no bundle.** The harvest counts a spare as planned only when its bundle directory exists (`harvest.py:7682-7684`) and lists it under a roster stage `<stage>.spares` (1861). `harvest.json` has planned 125, present 125 and no `.spares` stage. So it added nothing to the endpoint and nothing to the roster.
- **What rc 1 means.** The runner exited 1 through one of: a failed member, a drained member, a provisional verdict of `blocked` or `invalid`, a failed verdict append (`scripts/run_campaign.py:11398-11404`), or an early return (10334, 10409).
- **It was not a physical refusal.** After the spare's settle, the journal shows one tree-active interval, two idle ones, then a 20-interval run ending in a high-CPU interval. The tail of ALPHA attempt 1, which ran no spare, shows the same shape after its last end reference. So the spare runner lived inside one 10-second interval, too short for an idle-admission measurement.
- **The tripwire cannot see it.** `driver.py:1683-1685` ignores run ids outside the planned set, so "no pre-bundle refusal flagged" says nothing about a spare.
- **The live spare path is unproven.** The registered rehearsal ran spares with a stand-in runner (registration 1786-1803). The alpha-a3 Opus consult (line 136) also mentions a failed start reference "and its failed spare" under the first seal. That is possibly 0 of 2 live spare runs working. I could not find the refusal in the code; program B names it.

### (d) Run-time condition

- **Last science stage, 5 of 20.** 114 of its 379 intervals are over the limit. 77 of those contain `XProtectRemediat`: 90 offender rows, so two processes, all between 05:40 and 06:00. All 20 bundles are present, so the window did not drain (`run_campaign.py:10947-10979` would leave no bundle).
  - The likely mechanism is idle-admission abort after two attempts with no backoff. I take that from the alpha-a3 ruling, item 3 (`controller.py:1949-2002, 2599-2632`); I did not re-read those lines.
- **End reference, 1 of 3.** Either the over-limit interval at the start of a short tree-active stretch, or the `syspolicyd` run. The journal cannot say which.
- **XProtect did not directly cause the screen failure.** Its last over-limit interval precedes the first end reference by about half an hour. The fence below cures the LOW stage and the disturbed hour, not necessarily the screen.
- **A separate pattern worth a look.** Both windows lost exactly one member in each decode ABBA stage (19/20 and 19/20 in ALPHA attempt 1 and in BETA attempt 1, from both `hazard_result.json` files). Those stages are nearly quiet in BETA: 9 of 310 and 9 of 302 intervals over the limit. Two packs, two times of day, same count: this looks like a member-level cause, not contention.

**What the permitted evidence cannot distinguish:** (i) from (ii) from (iii)/(iv); which end member failed and why; why the spare exited; whether the decode-stage losses are deterministic.

## Recurrence

- **What starts XProtectRemediator.** `/Library/Apple/System/Library/LaunchDaemons/com.apple.XProtect.daemon.scan.plist` and `LaunchAgents/com.apple.XProtect.agent.scan.plist` each register three repeating `com.apple.xpc.activity` jobs: fast (interval 21,600 s, battery allowed), standard (86,400 s) and slow (604,800 s). All are `CPUIntensive`, `DiskIntensive`, priority Utility. One daemon plus one agent explains the two processes.
- **No fixed clock time.** These are scheduler-placed activities with a minimum spacing. The scheduler picks the moment.
- **Scale suggests the daily or weekly scan.** A 20-minute two-process run is too heavy for the fast scan. ALPHA attempt 1 (16:12 to 22:02) showed no `XProtectRemediat` interval, and BETA showed none in its first five hours.
- **Can t0 dodge it?** Not with certainty, but two things help:
  - The standard scan ran at 05:40 today, so it should not be due again before about 05:40 tomorrow. A chain that ends before about 05:00 on 10-11 avoids it.
  - The whole 05:40 to 06:40 hour was disturbed: 127 of 461 intervals over the limit in the last two stages (27.5%), against 101 of 1,691 before them (6.0%). ALPHA attempt 1 overall was 165 of 2,081 (7.9%).
- **Background is not the risk; clustering is.**
  - Run-time loss is about 1 member in 37 (registration 4638).
  - Corpus physics drops are 1 of 36 across the two second-seal windows.
  - Independent double loss at one endpoint is therefore about 1%.
  - `mediaanalysisd` pulses for one interval every 14 to 15 intervals in both windows (76 and 84 intervals). ALPHA attempt 1 was claim-usable with it present.
- **My estimate for an unchanged attempt 2.**
  - About 0.70 (range 0.55 to 0.80) if the chain avoids 05:15 to 06:45.
  - About 0.50 if it spans that hour again.
  - It rests on 1 of 2 second-seal windows, the rates above, and the unproven spare.
  - If program A shows `rederivation_*` or a source problem, the estimate for unchanged code is lower. A harvest defect on the "lost reference plus absent spare" path repeats whenever an end reference is lost at run time.

## Recommendation: (b)

Conditional on step 0, which can turn it into (d).

0. **Before any arm, run program A** (and A2 if it shows an evaluated screen with an "exceeded" code). It takes seconds and changes the decision:
   - `survivor_screen` = `references_insufficient`: cause (i). Go to step 1.
   - Evaluated on (3, 1, 2) with an "exceeded" code and a non-null bound: cause (ii). The screen did its job. Go to step 1.
   - Not evaluated, with a problem code: this is (d). Fix the harvest by the R3 route, pin it by addendum, and re-harvest attempt 1 from identical bytes before deciding to arm.
     - Attempt 1 has no `cell.below_minimum` and a derived bound, so it may be claim-usable.
     - Do not arm attempt 2 first. The analysed window is the first claim-usable attempt in arm order (registration 4622-4629), and arming a second attempt while the first is recoverable buys nothing.
1. **Arm BETA attempt 2 from the same sealed clone, unchanged, at the earliest permitted t0 today.** After the 60-minute dwell, t0 must be at or before 17:15. The chain is about 6 h 05 min, so it ends by about 23:20, clear of the midnight job and of tomorrow's scan.
2. **Rule for later arms.** No chain may be running between 05:15 and 06:45 local: t0 at or after 06:50 and at or before 17:15. Keep this until program D shows the scan is not daily near 05:40. It changes nothing a window reads.
3. **Check that the fence worked.** After the window, tally the contention journal: zero `XProtectRemediat` intervals, and an over-limit share of the last two stages near the background (below about 10%, against 27.5% here).
4. **Run program B on the spare.** If it shows a refusal that is not a failed measurement, record it as a deviation: the registered spare retry did not run live. Reproduce it off-window on a rehearsal root.
   - Do not hold the arm for it. The spare only restores margin.
   - A fix touches code a window executes, so it belongs with any later (c).
5. **No (c) now.** One event does not justify losing the claim-usable ALPHA window. If attempt 2 is removed again in the NEG8 family, registration 7.3 sends the next spend to a consult. That is the point to bundle a working spare path, a retry that can replace a harvest-found loss, and more end references, in one erratum.

**GAMMA before BETA: no.** The registration fixes the order, not only the brief: "then the next pack in the fixed order ALPHA, BETA, GAMMA arms" (registration 4627-4629, section 7.2). Running GAMMA first would not select on an outcome, so it is not unsound in itself. But it needs a prospective erratum, GAMMA has open "before GAMMA-1 arms" items (registration 1203, 1957), and it saves no time on a dedicated machine where BETA can arm today.

## Least sure

- **Which of the three branches fired.** Program A's `rescreen.evaluated`, `survivor_screen` and `problems` is the one fact that changes my answer: not evaluated means (d) and a possible recovery of attempt 1; evaluated means (b).
- **Whether the 05:40 scan is daily at a stable hour.** I have one observation. Program D tests it.
- **Whether the spare path is deterministically broken.** I could not find the refusal by reading; program B names it.
- **The run-time mechanism of the science losses.** Idle-admission abort is inferred from the alpha-a3 ruling's reading of the controller, not from my own.

## Counts I would want

**A. The screen's branch.** Reads `derived/neg8-screen.json`. Prints closed-list words and counts only. The program is `screen_branch_count.py` beside this file. Why no field can carry an energy: every printed word is tested against a literal list taken from the code and otherwise prints `other`; counts are integers of references; run ids are never printed (values are tallied by code); no bound, statistic or operand is read. The "exceeded" condition names reveal only the outcome of the reference screen, which `neg8.screen_failed` already implies; they are derived from reference energies, not science energies. The magistrate should judge whether that outcome word is releasable.

**A2. Only if A shows an evaluated screen with an "exceeded" code.** Reads `withheld/neg8-rescreen-bracket.json`. For each of the two claim families it prints `endpoint_counts` (three integers) and the single boolean `derived_repeatability_bound_j is None`. It prints a null test only, never a value.

**B. The spare.** Reads the claim runs root's `campaign_log.jsonl`. It takes the spare run ids from the plan-time file `configs/campaigns/window_reference_spares_v5/end_triplet_spares_1/order_manifest.json` in the sealed clone. For log rows whose `run_id` is one of them it prints: the row count; `status` if it is in {ok, failed, timeout, drained, config_error, skipped, waived}, else `other`; `exit_code` as an integer or null; `blocked_before_invoke` as a boolean; for `child_refusal`: `absent`, or the token if it is in `arm_readiness.LAUNCH_LINEAGE_REASON_CODES`, else `present_other`; whether `<runs root>/<spare id>` exists, as a boolean. No duration and no error text. If the row count is 0, the runner returned before its member loop (`run_campaign.py:10334` or `10409`). Run the same program on the first-seal attempt whose start spare failed, to test whether a spare has ever run live.

**C. Science-stage losses.** For each roster stage, count members whose stored `summary_metrics.json` `status` is not `succeeded`, grouped by the closed failure-reason code in the bundle's own record (admission abort, timeout, other). Print counts per stage only. Also print one integer: the number of (stage, position in stage) pairs lost in both ALPHA attempt 1 and BETA attempt 1. A count of 2 means the decode-stage losses are deterministic.

**D. XProtect by clock hour.** Over the contention journals of the earlier block-5 attempts and blocks 3 and 4: for each journal, the number of intervals whose `outside_over_limit` contains `XProtectRemediat`, bucketed by local hour, plus the journal's local start and end hours. Names and integers only. It decides whether the 05:15 to 06:45 fence is right or should move.
