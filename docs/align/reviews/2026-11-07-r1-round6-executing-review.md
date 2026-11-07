# Executing review: ALIGN v4 R1 round 6 (2026-11-07)

**Verdict: ADMIT_WITH_FIXES.** No BLOCKER and no HIGH. Each ruling R6-1 to R6-8 is implemented as written in `LEAD-RULINGS-2.md` (Round 6), and nothing outside the rulings changes measurement semantics. R6-7 had one non-measuring exit that never restored: the run_night `dead-man`. I fixed it, and one LOW, in `4f2c3283a`, each with a test that fails on `54d584de6`:

- **MEDIUM-1 (fixed).** `run_night dead-man` is the night's last exit in two cases: the night job never launched and the watchdog's J4 restore did not run (watchdog down, deferred or failed), or `run_night` was ended by TERM, HUP or KILL without its close. In both it left a W1 session's High Power at 2. It now restores the marker its own plan's session owns, once it has proved the chain gone, under the same owner and lock rules as the other exits.
- **LOW-1 (fixed; Sol F9).** `restore_owed` checked the marker's owner before it took the night lock, so an install that ran in between could have its fresh marker restored by a late exit of an older plan. It now re-reads the markers under the lock.

Three MEDIUM findings are left for the lead (MEDIUM-2 to MEDIUM-4). Each needs a ruling or a design choice, and none can admit bad data. Two of them are the builder's own open items (Sol F2/F3/F4 in the Round 6 section). MEDIUM-2 is new: `run_night` and the v4 `install` have no TERM/HUP handler, so either signal ends them at once, like SIGKILL. That is what makes the dead-man restore necessary.

- Reviewer: Opus 5.5. This is an executing review, and I did not write any of the code under review.
- Target: `lane/2026-11-06-v4-r1-integrated@54d584de6` against `998ee2ab0` (the lane tip is now `1e3f046bc`, which adds only the round-6 cold pass doc). That is 49 files, +3,501/−347: the science lane `9900f4cd0` + `0633a9c21`, the infra lane `ae26b7c40` + `200ca2555` + `5086e147a`, the merges `c42c39a5f`/`c6f178f0f` and the docs `54d584de6`.
- Read first:
  - the round-5 executing review and the round-5 cold pass (`d5f1b6606`);
  - `LEAD-RULINGS-2.md` (all rounds) and the integration report's round-5 and round-6 sections;
  - `pilot_protocol_v4.md` (:72, :243-253, :450) and the R1 runtime contract.
- Code read line by line (the whole round-6 code diff):
  - `powermode.py`, `r1_runtime.py`, `r1_runtime_contract.py`;
  - `align_r1_rehearsal.py`, `align_v4_kit.py`, `align_v4_session.py`, `run_night.py`, `magistrate_watchdog.py`, `align_v4_wp18_fixtures.py`, `align_v4_w1_synthetic.py`, `validate_align_v4_w1_plan.py`;
  - the config and template hunks.
- Supporting code read:
  - every exit of `run_night._run_night` and of `dead_man`;
  - `bytes_h_session.install` (the shared installer's no-op returns);
  - the v4 workload's G0-unreleased stop (`workload.py:440-500`), the gated and X-G runtime kinds and `member_config`;
  - the watchdog stand-down signal paths (which signal the magistrate's own tree, never `run_night`).

Nothing restricted was read or touched, no model weights were loaded, and nothing ran on the measurement Mac.
- Every run used `nice -n 19 taskpolicy -b /private/tmp/jwsol/venv-both/bin/python -B` in the worktree `jw-wt/r6-exec-review`.
- Each test process had its own `TMPDIR` under `/private/tmp/jwr6-tmp/exec-review`.
- One test module ran per process, at most three at once.
- Every test process pointed `JOULEWISE_HOST_STATE_DIR` at a temporary directory, so the real `/Users/Shared/JouleWise/host-power` was never touched (the `tests.align` package and the patched root modules do this).

## What I executed

| Check | Result |
|---|---|
| Whole `tests/align`, one module per process (118 modules), plus the 20 root modules the round touched (`test_run_night`, the six watchdog modules, `test_launch_window*`, the night-agent and installer modules, `test_b5_driver*`, etc.) | `tests/align` all 118 rc=0 (1,612 tests, skipped=35). Root: 14 of 20 rc=0; the six failing modules fail the same way on `998ee2ab0` (environment and timing under `taskpolicy -b`, details below the table) |
| `tests.hazards.test_refusal_allowlist` (the refusal allowlist covers `run_night.py`/`powermode.py`) | Ran 23, OK (skipped=1), at the fix commit |
| New module `tests.align.test_r1_round6_exec_review` (my adversarial tests, below) | Ran 9, OK at the fix commit. Three tests fail on `54d584de6`: the two dead-man restores (`2 != 0`) and the owner recheck |
| `JW_WP22_FULL=1 tests.align.test_v4_w1_synthetic` (WP22 synthetic W1) | Ran 18 tests in 241.8 s, OK (expected failures=1, F3, as in rounds 4 and 5) |
| `scripts/align_v4_kit.py --check` | No drift. Blocked on the same nine leaves (WP18 ×4, R0, R1 ×4) |
| `git diff` of `configs/campaigns/align_pilot_v3` against `998ee2ab0` and against `lane/2026-11-05-align-pilot10-benign` | Empty |
| `night_worst_case_s(None)` (cold LOW-6) | 44,486.99 s with no redo; 49,886.99 s with one batch wait; R6-2 retry allowance 19,200 s; 69,086.99 s in all. These match LEAD-RULINGS-2. `w1_inter_member_idle_s()` = {D: 300, X-G: 300} |
| R1 exit-path harness A: the real driver, `FakeWorld` as the command boundary (fake sudo/pmset/runtime), real signals, the real host lock and host marker in a temp `JOULEWISE_HOST_STATE_DIR`, and a second process trying a session-start restore and a night admission while the driver is parked | 9 scenarios, all as expected (below) |
| R1 exit-path harness B: `run_night` under a plan declaring 2, the `NightDriverTests` fixture (fake probes; fake sudo/pmset with the mode in a file), parked inside the chain spawn after admission, real signals, then `dead-man` in a fresh process | 4 scenarios (below). TERM, HUP and KILL each leave mode 2; the dead-man restores (MEDIUM-1, MEDIUM-2) |
| Local Sol 6.1 xhigh as a second critic (static, mock-only probes) | 12 findings, triaged below. Audit of its events: **AUDIT CLEAN**. The only custody-path strings are `!restricted/**` exclusion globs in its `rg` commands, and text inside repository files it read (the contract doc, LEAD-RULINGS-2, `TASK_QUEUE.md`, `powermode.py`). No command named, listed or read those paths or `/Users/Shared/JouleWise` |

**Suite details.**

**`tests/align`: all 118 modules rc=0, Ran 1,612 tests (skipped=35).**
- Selected: `test_r1_rehearsal` 73, `test_r1_runtime` 33, `test_r1_runtime_e2e` 2, `test_v4_kit` 100, `test_r1_round6_power` 25, `test_r1_round6_lows` 18, `test_r1_runtime_contract` 11, `test_v4_wp18_fixtures` 11.
- Slowest: `test_moe_calibration` 3,215 s.

**Root modules: 14 of 20 rc=0, 1,354 tests in all.** The six watchdog modules (158 + 9 + 7 + 24 + 20 + 10) all passed.
- Six modules failed, and every failure is environmental or timing under `taskpolicy -b`:
  - `test_evidence_night` (25) and 8 of the `test_run_night` failures assert "test interpreter must load the battery fixture in child Pythons". The venv interpreter disables the user site.
  - The other `test_run_night` failures are bind-supervisor and journal tests ("external watchdog (8 s)…"), installer and probe tests.
  - `test_launch_window` 1+2, `test_install_night_agent` 1+3, `test_night_agent_install` 10+1, and `test_b5_driver_p2` 2 (a census count of 3 or 4 versus 5).
- Rerun alone under the same QoS, at the fix commit and at the pre-round-6 base `998ee2ab0`:
  - `test_launch_window`, `test_install_night_agent` and `test_night_agent_install` passed at both;
  - `test_run_night` failed 20 and 22 tests at the two commits, the same set give or take three flaky ones;
  - `test_b5_driver_p2`'s census test failed at both, twice each.
- None of the failures is a powermode, High Power, marker, lock, J4 or dead-man test. At the fix commit, `test_run_night -k powermode -k high_power -k marker -k Automatic -k night_lock -k restore -k dead_man` ran 45 tests, all OK.
- The fixes landed while the suite ran. Only `test_moe_calibration`, `test_moe_review` and `test_analysis_metadata_baseline` started before them, and they do not import the changed files.

### Harness A: R1 driver, real signals, host lock and marker

Scratch harness, not committed: `/private/tmp/claude-501/…/scratchpad/r6harness/{child,parent}.py`.
- A child process runs `scripts.align_r1_rehearsal.run` with `_run` replaced by the test `FakeWorld`. It adopts High Power (A1 20 s, B 30 s, A2 21 s), with `calibration_g0_timeouts` where the row says so, and parks inside the named segment.
- While it is parked, the parent (a separate process) calls `align_v4_session.session_start_restore` and `powermode.admit_ac_powermode(0, …)` against the host marker, then delivers real signals.

In every signalled row:
- the concurrent session start was `deferred_measuring_night`, and the concurrent admission refused with "a measuring night holds the host night lock". There were 0 restore calls from the second process.
- `r1.run` returned 4 (`aborted`, `KeyboardInterrupt: signal N`), the fake host ended at 0, both markers were gone, no `r1_slots.json` was written, the last powermode records were `restore_automatic` ×2, and the lock was free afterwards.

| Parked in | Mode while parked | Signals |
|---|---|---|
| `high_power_B` | 2 | TERM |
| `step_D….precool` (R6-2, series 2) | 2 | INT |
| `step_D….precool_retry` (one step-d G0 timeout) | 2 | TERM |
| `planning_turn_R_plus_2C.precool` | 2 | HUP |
| `planning_turn_R_plus_0C.precool_retry` (one R + 0 timeout) | 2 | INT |
| `D_spam_benign_s1_gated_held_a` (follows the R + 0 turn, R6-1) | 2 | TERM ×3 |
| `X_G_contrast`, restore slowed by 1 s | 2 | TERM, then TERM inside the slow restore |
| `D_bank_benign_s1_gated_held` | 2 | **KILL**: rc −9, mode 2, host marker present, lock free; the next session start restored (`restored`) |
| none (complete run; step-d G0 timeout once, R + 2 twice) | — | exit 0, `complete`, mode 0, markers gone, registration written, `inconclusive_segments` = {`planning_turn_R_plus_2C`} only (step-d recovered on its retry) |

### Harness B: run_night under a declared 2, real signals

Scratch harness, not committed: `/private/tmp/claude-501/…/scratchpad/r6harness/night_{child,parent}.py`.
- `run_night` is admitted under plan `ac_powermode` 2 with this session's W1 host marker. While it is parked in the chain spawn, the parent confirms the night holds the host lock, then sends the signal.
- Afterwards a fresh process runs `dead_man` for the same plan at its completion epoch.

| Signal | `run_night` | Mode / marker after `run_night` | `dead_man` (with the fix) |
|---|---|---|---|
| INT | KeyboardInterrupt; the close ran (`ac powermode close … ok`) | 0 / removed | not needed |
| TERM | killed (rc −15), no close | **2 / present** | restore + read; 0 / removed |
| HUP | killed (rc −1), no close | **2 / present** | restore + read; 0 / removed |
| KILL | killed (rc −9) | **2 / present** | restore + read; 0 / removed |

Without the fix the dead-man left all three at 2. The next session start or night admission still restored them (the R6-7 backstop), but a night that never launched, or a run_night ended by TERM, had no restore of its own.

## Ruling by ruling

**R6-1 (duty bar reproduces W1's D-after-D G0). Implemented.**
- The idle comes from the W1 plan, not a constant. `align_v4_kit.w1_inter_member_idle_s` reads each W1 member config's `sampling.idle_seconds` (300 s for D and X-G), and refuses unless each role has one value. This matches protocol v4 :72 ("300 s configured idle and a fresh process per member").
- `check_w1_schedule` refuses at t0 if the runtime templates for `d_spam`, `d_bank` and `x_g` carry another idle. Each gated run and X-G reports `inter_member_idle_s` (from its template, which `member_config` keeps), and `_check_schedule` refuses a mismatch.
- The kit requires `duty_bar.schedule` with authority R6-1 and the same per-role idle.
- No cool-to-band. The gated precools are gone, and the phase table puts the four runs back to back after the R + 0 planning turn. My `PhaseOrderTests` asserts that every gated run and X-G is preceded directly by a D-turn kind, for both caps and with and without 4-bit.
- The gated runs are non-quiet kinds, so no ruling 8 batch wait or redo release can slip in before them.
- The soak R is still consumed (R5-1), now checked against the soak's `s_slow` value specifically (cold LOW-4).
- A gated G0 timeout gives an INCONCLUSIVE row, never a refusal. The v4 workload ends a member whose G0 did not release with no turn (`workload.py:440-500`, the same code W1 runs). So the builder's "no D work" rule (timed-out G0, or a released G0 with zero decode tokens) correctly makes the next run INCONCLUSIVE too. `r1_slots.x_g` records X-G's status.
- Builder decisions for the lead: I agree with the order, with "the member's own configured idle" as W1's schedule, and with keeping a timed-out run's 600 s in 1(f)'s max-G0 term (a W1 G0 timeout is real, so leaving it out would be the optimistic choice). One observation is LOW-6.

**R6-2 (calibration precools; retry once; then INCONCLUSIVE). Implemented.**
- An `idle-until-soak` precool runs before step-d and before the R + 2 and R + 0 states. The ruling 1(c) `cooldown_after_D` precedes R + 4. The cap is `calibration_precool_cap_s` (1,500 s) from the runtime config, which must be finite and positive.
- A pure G0 timeout is an exit-0 INCONCLUSIVE result:
  - `g0_timeout_only` admits only `turns:0`, `thermal.start_gate_timeout` and `episode.g0_unreleased:*`;
  - any other fault still raises `RuntimeFailure`;
  - the contract's `required_fields(inconclusive=True)` keeps the quiet fields.
- The driver moves the first attempt to `.g0_timeout1`, runs `.precool_retry`, retries once, and then records `inconclusive_segments`.
- An INCONCLUSIVE step-d skips the gated runs and X-G and writes `slots` null. The kit refuses W1 on any entry, step-d with its own message.
- Harness A drove a step-d timeout that recovered on its retry and a planning state that timed out twice, to a complete exit-0 run. It also drove signals inside both retry precools.

**R6-3 (1(f) uses the slowest observed decode rate). Implemented.**
- Gated runs report `decode_tokens` (the sum over admitted turns).
- `deadman_summary` refuses non-int or negative counts, and tokens with zero decode seconds.
- `budget_fit_inputs` records the step-d rate, each run's rate and their minimum. The kit re-derives the minimum from the rows and refuses a recorded rate that differs.
- The last-turn term keeps the full cap. There is no code fallback.

**R6-4 (changed picks bind the R1-pick values). Implemented.**
- With `sensor_pick_changed` true:
  - `turn_cap_s` binds `s7_for_r1_picks.S7`;
  - `delta_slow_c` binds `band_c.s_slow`, unless there is an `s6_tuning` receipt starting from it (≤ 2.0 °C);
  - `delta_fast_c` binds `band_c.s_fast`;
  - the policy sensors must equal `s7_for_r1_picks.keys`;
  - the R0-pick slots are refused.
- The quiet-window reference rule is recorded as ACCEPTED with its authority.

**R6-5 (classification digest). Implemented.** The digest must be 64-hex and equal `thermometry.D.classification_sha256`. `gate_policy_fields` removes it before gate validation and member install, in the kit and in the W1 plan validator.

**R6-6 (`cooldown_after_30b` dropped). Implemented.**
- The phase is gone, and `step_30b` keeps its 600 s recovery observation (R5-5), so the A1 leg still starts after the idle and its own G0 release.
- Nothing else references the phase.
- `ABA_LEG_I_D_BOUND_S` = 1,750 is unchanged (leg bound 4,329.0 s).

**R6-7 (no exit leaves mode 2; never restore under a measuring night). Implemented, with the dead-man exit added (MEDIUM-1).** The exit-path table below is my enumeration. "Backstop" means the host-level marker survives, and the next session start or night admission restores it, never under a held lock.

| Process | Exit | Leaves 2? | Restore under a measuring night? |
|---|---|---|---|
| `prepare` | any (restore runs first; a failed read-back refuses) | no | no: a held lock defers |
| `install` | precheck failures (session JSON, `require_w1_ready`, terminal session) before the lock | no mode change; an older marker waits for the backstop | — |
| `install` | lock held by another | no change | no |
| `install` | entry, arm, disk or installer exception, KeyboardInterrupt included | restored | lock held by install |
| `install` | shared installer's no-op return (launchd holds a job; cold MEDIUM-1) | restored, then refuses | lock held by install |
| `install` | already installed (exit 0) | kept at 2: that armed night closes the span (not a defect; Sol F5) | — |
| `install` | TERM/HUP | **yes, backstop** (MEDIUM-2) | — |
| `run_night` | malformed plan, rerun record, J4 `launch_abandoned` | restored if this plan owns the marker | deferred under a held lock; another session's marker untouched |
| `run_night` | plan 2, lock unavailable | no change | no |
| `run_night` | plan 2, admission refusal (mode mismatch, failed reads) | restored while holding the lock | no (it holds the lock) |
| `run_night` | plan 0 with a marker | restored before admitting | refuses under a held lock |
| `run_night` | every exit after a plan-2 admission (all refusals, chain outcomes, exceptions, INT) | restored by the close, then the lock is released | see MEDIUM-3 (the close does not prove the chain stopped) |
| `run_night` | exception before admission (custody-log or census write) | **yes, backstop**; now also the dead-man (LOW-4) | — |
| `run_night` | TERM, HUP, KILL | **yes**; now the dead-man restores (MEDIUM-1/2) | the lock dies with `run_night` (MEDIUM-3) |
| `run_night` | `dead-man` | **was yes; fixed**: restores this plan's marker after proving the chain gone | refuses while the chain lives; deferred under a held lock |
| `run_night` | `--dry-arm` | no mode change (a desk control; restoring would undo an armed session) | — |
| watchdog | J4 release | restored if this plan owns the marker; deferred or failed falls to the dead-man and the backstop | deferred under a held lock |
| R1 driver | refusals before the lock (existing output dir, bad entrypoint) | no change; a crash marker waits for the R1 night's own admission, which restores first | — |
| R1 driver | every exit after the lock, first INT/TERM/HUP, second signals | restored (harness A) | it holds the lock |
| R1 driver | KILL | **yes, backstop** (harness A row 8) | the lock dies with the driver (MEDIUM-3) |
| R1 chain | EXIT-trap `pmset 0` after the driver released the lock | restores to 0 | no W1 night can be measuring then (LOW-5) |

The contract doc now has the dead-man bullet, and its TERM/HUP wording matches the code.

**R6-8 (LOWs). Implemented, apart from the documented half of cold LOW-6.**
- exec LOW-2: `only_g0_unreleased`; the allowed set depends on the G0 outcome.
- exec LOW-3: `close_managed_session` holds TERM/INT/HUP and re-raises after the close. A failed close stays in `open_sessions`.
- exec LOW-4: `check_wp18_turn_contents`.
- exec LOW-5: `check_duty_bar_consistency`.
- exec LOW-6: the registration is staged, `r1_result.json` is written with its sha256, and only then is `r1_slots.json` replaced atomically. Harness A shows no registration in any aborted row.
- cold LOW-1/LOW-2/LOW-4/LOW-5: as listed in LEAD-RULINGS-2. The WP18 rows are bound by turn index and the seed-law per-turn seed. The summary seed accepts the seed index (Sol F7, round 6), which I checked against `ARMS`.
- `_check_recovery_curve`.
- cold LOW-6: `night_worst_case_s`, numbers re-derived above. I agree with the deviation: no R1 plan template exists in the repo, and W1's 44,640 s cap is not an R1 value.

**Did anything else change measurement semantics?** No. The changes beyond the ruling text are:
- the reorder (gated block after the designed states, X-G after D_bank), which R6-1 requires;
- the post-D cooldown's role as the first state's precool;
- the planning G0 timeout now being an exit-0 INCONCLUSIVE instead of a refusal (R6-2).

All three are stated in the contract doc and in LEAD-RULINGS-2. `S5_fast` is a new recorded slot (cold LOW-1), not a new measurement.

## Findings

### MEDIUM

**MEDIUM-1 (fixed in `4f2c3283a`): the `dead-man` exit never restored a W1 High Power.**
- R6-7 lists "never-launched" among the exits that must restore. The builder implemented it as the watchdog's J4 release, which is the first restore. But `run_night dead-man`, the launchd job that fires at the deadman calendar and couriers the night, had no power handling at all.
- A W1 session armed at 2 therefore stayed at 2 through its own dead-man when:
  - the watchdog was down, or its J4 restore was deferred or failed; or
  - `run_night` was ended by TERM, HUP or KILL after admission. There is no handler, so its close never ran (harness B). Also covered: a driver killed after writing its first record but before the chain (J4 no longer applies; Sol F11).
- Fix: once the dead-man has proved the chain gone, it calls `_restore_owed_on_exit(plan_path, custody_root, probes, "dead_man")`. This sits after the chain-alive, courier-running and pending-launcher refusals and before the census.
  - It is owner-scoped: only a W1 marker this plan's session owns. An R1 crash marker or a retried session's marker is untouched.
  - It is lock-deferred, so it never restores under a measuring night.
  - It never raises, and it logs `ac powermode exit restore (dead_man)`.
- Tests: `DeadManHighPowerTests`:
  - two restores, never launched and after a killed `run_night`, which fail on `54d584de6` with `2 != 0`;
  - three guards: chain alive, a measuring night holding the lock, and another session's marker.
- The contract doc has the new bullet. At the fix commit, the refusal allowlist passes, and so does every power test in `test_run_night`. That module's other failures are environmental and also occur on `998ee2ab0` (see the table).

**MEDIUM-2 (lead): `run_night` and the v4 `install` have no TERM/HUP handler.**
- Python's default action for SIGTERM and SIGHUP ends the process without unwinding. So a TERM or HUP to `run_night` after a plan-2 admission skips the close: the host stays at 2 with the marker, and the lock dies with the process (harness B).
- The same holds for a TERM or HUP to `install` between its High Power entry and its return. One example is the magistrate's terminal closing mid-install.
- With MEDIUM-1 fixed, the dead-man restores the night case once the chain is gone. The R6-7 backstop restores both at the next session start or admission, so nothing is admitted at the wrong mode.
- I did not add handlers. A one-shot handler would route TERM into the INT path, and that path restores without proving the chain stopped (MEDIUM-3). That interaction is a design call.
- Recommendation: handle TERM/HUP in `install` like INT; this is safe, because install holds the lock and has no chain. Decide `run_night` together with MEDIUM-3.

**MEDIUM-3 (lead; the builder's open F2 and F3, Sol F1 and F3): the lock and the close are bound to `run_night`, not to the night's process tree.**
- F2: a SIGKILL of `run_night` alone, or of the R1 driver alone, releases the lock while the chain or the runtime child keeps measuring. A session start would then restore under it. That needs an operator to kill one process and then start a session mid-night. Nothing in the repo does that: the watchdog's stand-down signals the magistrate's own tree.
- F3: the close restores Automatic without proof that the chain stopped. An INT that unwinds supervision leaves the chain (its own session) running at 0 while the plan says 2. The night is aborted and has no terminal record, so nothing is admitted.
- Both need a ruling, and the builder's `pass_fds` option has the costs the builder lists. I would pair F3 with MEDIUM-2: either prove the chain group gone before the close restores (the dead-man already has that proof), or keep the marker and the lock until it is.

**MEDIUM-4 (lead; the builder's open F4, Sol F4a): an install during a running plan-0 night sets mode 2 under it for seconds.**
- Plan-0 nights do not hold the lock. `install` enters High Power before the shared installer's launchd census, and that census is what finds the running night's job loaded.
- So a v4 install during any plan-0 night does the following: enter 2, arm, disk gate, installer no-op, restore. The running night measures at 2 for those seconds, and nothing records it beyond the member's episode-start observation.
- That needs an install while a night is running. It is an operator error, but one that changes a measurement rather than failing closed.
- Recommendation: run the launchd census (`launchctl print gui/<uid>/com.joulewise.night`) before `enter_high_power` and refuse on exit 0. That is the refusal the installer already makes, moved ahead of the mode change.
  - The census needs a test seam, because the existing install tests do not pass `run`. Without one, they would call the real `launchctl`.
  - The alternative is that every admitted night holds the lock.

### LOW

1. **(Fixed in `4f2c3283a`; Sol F9.)** In `restore_owed`, the owner check ran before the lock. If an install ran in between, the late exit restored the install's fresh marker and deleted it. The window is microseconds against a whole install, but the fix is free: re-read presence and ownership after taking the lock. Covered by `test_an_exit_restore_rechecks_the_owner_under_the_lock`, which fails on `54d584de6`.
2. **(Sol F10.)** The R1 `PowerModeGuard.restore` deletes both markers on a 0 exit of `sudo pmset … 0` without a read-back. R6-7's powermode helpers remove markers only after reading 0. If pmset ever exited 0 without applying, the host would be at 2 with no marker. The next plan-0 admission would then refuse on the mode without restoring, and every night after it until a manual restore. Fix: read back before unlinking, as `restore_automatic` does.
3. **(Sol F8.)** A plan-2 admission refusal with no marker present restores nothing (`restore_owed` sees no marker). Separately, a failed marker write after a plan-2 admission is recorded, and the night measures anyway. Both need the marker to be missing or unwritable in a directory whose lock file was just created. If wanted: restore unconditionally on a plan-2 refusal under the lock, and refuse the night if `_own_high_power_marker` fails.
4. **(Sol F6.)** An exception between plan parse and admission (custody-log or census write, for example ENOSPC) leaves an armed session's 2 in place. The dead-man (MEDIUM-1) and the backstop now cover it.
5. **(Sol F4b.)** The R1 chain's EXIT-trap `pmset 0` runs after the driver has released the lock. A W1 night cannot be measuring at that moment: its install would need the single `com.joulewise.night` label, which the R1 night's job still holds, and the shared installer refuses then. No change needed. I record it so a later multi-label installer does not reopen it.
6. **(R6-1 observation, lead; same root as the round-6 cold pass MEDIUM-1.)** `D_spam_benign_s1_gated_held_a` follows one planning turn (a single D turn, preheated to near R), not a full multi-turn D episode. So its G0 is a lighter D-after-D case than a W1 D member after a D member, while runs b and bank follow full gated episodes. This matches "after a D turn" literally.
   - The cold pass draws the sharper consequence: spam a and spam b are the U5 replay pair, so the asymmetric predecessors can inflate σ_pair.
   - Its fix (gated order D_bank, D_spam a, D_spam b, X-G) also removes this point: both replay runs then follow a full gated D episode, and X-G still follows a D turn.
   - I agree with that MEDIUM and that fix. My `PhaseOrderTests` asserts only that each gated run and X-G follows a D-turn kind and that the block follows the R + 0 turn, so the reorder would need its last assertion updated.
7. Cold LOW-6, second half (the R1 plan's `window_max_s`): open, as the builder reports. The R1 night's all-caps wall is 44,487 s, or 69,087 s with every R6-2 retry and one batch wait. The Mac-side plan must cover that or accept a wall-clock cut.

### Sol critic findings not taken

- **F5** (an already-installed session keeps 2, and a re-run arm refusal does not restore): correct as is. That session's night job is installed, and its close owns the span. Restoring here would break the armed night.
- **F7** (R1 refusals before the lock skip crash recovery): the R1 night's own `run_night` admission restores a crash marker before the chain starts. The R1 driver is not a session start.
- **F12** (an own-marker admission under plan 2 does not "restore first"): restore-first applies to an owed marker. R5-6 keeps the night's own W1 marker under expected 2. Restoring it would make W1 under High Power impossible.
- Sol rated F1-F5 and F8 HIGH. I rate F1, F3 and F4a MEDIUM (lead), F2 MEDIUM (mine, MEDIUM-2), and F4b, F8 and F10 LOW, because each needs an operator action outside the protocol or an impossible pmset result, and each fails closed for the data.

## Relation to the round-6 cold pass (`1e3f046bc`)

The cold pass of the same head landed on the lane while this review ran. I read it after finishing my own findings, and my commit is rebased onto it.
- **Its MEDIUM-1** (the replay pair's predecessors): see LOW-6 above. I agree.
- **Its LOW-1** is my LOW-2 (Sol F10), the R1 guard clearing markers without a read-back. It confirmed this with a probe.
- **Its LOW-5** (a lock-file `OSError` refuses with the wrong reason and no restore; exceptions before admission) overlaps my LOW-4.
  - The dead-man fix (MEDIUM-1) now restores the exceptions-before-admission case once the chain is proved gone, because no chain started.
  - The dead-man fix does not cover the unopenable lock file, because `restore_owed` cannot take the lock either. Its proposal (restore without the lock when the lock file itself cannot be opened) is sound.
- **Its LOW-3** is right: 44,487 s is below W1's 44,640 s cap. The R1 window still has to cover the retry case.
- **Its LOW-2** (the unbounded close deferral delays the runtime's 15 s teardown watchdog), **LOW-4** (an exported `JOULEWISE_HOST_STATE_DIR` would split the host state) and **LOW-6** (the kit never reads `x_g`) are points I did not find. I agree with each.
  - LOW-4 interacts with MEDIUM-1 here: the dead-man runs from the LaunchAgent environment, as the night does, so it sees the default directory.
- **Its observation** about the R1 gap: a new runtime process and a model load sit between a D turn and the next G0. That is also W1's case: protocol v4 :72 says "a fresh process per member", and each W1 member is its own `run_benchmark` with its own load. The two match in structure, but neither gap is measured.

## For the lead

- Rule on the gated-block order (cold MEDIUM-1, my LOW-6) before R1's data are read.
- Rule on MEDIUM-2 and MEDIUM-3 together: what the night's close may do while the chain's state is unproven, and whether TERM/HUP should unwind `run_night`.
- MEDIUM-4 is a small change in `align_v4_session.install` (move the launchd census ahead of the High Power entry) plus a test seam.
- The builder's other open points still stand:
  - a designed-state INCONCLUSIVE refuses W1 and needs a ruling after such an R1;
  - an inconclusive gated run's G0 stays in 1(f);
  - the R1 plan's `window_max_s`.
- Nothing in this review contradicts them.
- `/code-review ultra` candidate for Ed: `lane/2026-11-06-v4-r1-integrated` (`powermode.py`, `run_night.py` power paths, `align_v4_session.py`).
