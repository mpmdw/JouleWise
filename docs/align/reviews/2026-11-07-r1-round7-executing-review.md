# Executing review: ALIGN v4 R1 round 7 (2026-11-07)

**Verdict: ADMIT_WITH_FIXES.** No BLOCKER and no HIGH. Each ruling R7-1 to R7-14 is implemented as written in `LEAD-RULINGS-2.md` (Round 7). Nothing outside the rulings changes measurement semantics. The pilot10-benign merge left the R0/SMC code and the v3 kit as pilot10-benign has them.

I fixed two MEDIUM findings and one LOW in `e51156033`. Each has a test that fails on `915f59446`:

- **MEDIUM-1 (fixed).** The R1 driver's teardown undid its own R7-5 deferral. When the guard's close deferred, the driver's second, "idempotent" restore in `finally` ran anyway. That call bypasses the retake and the W1-ownership check, so it restored Automatic and deleted a W1 session's marker. The deferral in question is the one for a W1 session's marker found after the retake (the round-7 infra Sol F4 branch).
- **MEDIUM-2 (fixed; R7-7).** Under a plan declaring 2, `admit_ac_powermode` admitted the night when the owed Automatic restore of an R1 marker did not read back 0. The markers were kept, but the mode then equalled the plan's 2. R7-7 says "keep the markers and refuse". It now refuses.
- **LOW-1 (fixed).** On its `not_owner` return, `run_night`'s close kept the host night lock it had just retaken.

Two MEDIUM findings are left for the lead (MEDIUM-3 and MEDIUM-4). Neither can admit bad data.
- **MEDIUM-3** is the round-7 cold pass's MEDIUM-1, confirmed by my harness: a TERM or HUP while the chain runs defers the restore, as R7-5 requires, but nothing stops the chain.
- **MEDIUM-4** is new, from local Sol: below `run_campaign`, the measuring members do not inherit the lock.

The R7-2 science is sound. The driver and the kit derive the same G0_cap_W1 on 500 random records and at the rounding boundaries. A G0 cut short by a deadman can only raise the cap, never lower it.

## Scope

- **Reviewer:** Opus 5.5. This is an executing review, and I did not write any of the code under review.
- **Target:** `lane/2026-11-06-v4-r1-integrated@915f59446` against `97714c644`. That is 57 files, +4,751/−347:
  - the science lane: `92cf83226` and `aa4cbfc6e`;
  - the infra lane: `0ed43d4e2` and `d0a6d509f`;
  - the pilot10-benign merge `bed96a99d` (`e1a91226e`, PR #691);
  - the integration test fix `9541b9dbd` and the doc commit.
  - The lane tip moved to `d20ccd829` while I worked. That commit adds only the round-7 cold pass doc. My fix commit sits on top of it.
- **Read first:**
  - both round-6 reviews;
  - `LEAD-RULINGS-2.md`, Rounds 6 and 7 and their builder deviations;
  - the integration report's round-6 and round-7 sections;
  - `pilot_protocol_v4.md` (the R1 and G0 passages) and `docs/align/r1_runtime_contract.md`;
  - after it landed, the round-7 cold pass (`d20ccd829`).
- **Code read line by line** (every round-7 code hunk):
  - `powermode.py`, `r1_runtime.py`, `r1_runtime_contract.py`, `thermal_gates.py`;
  - `align_r1_rehearsal.py`, `align_v4_kit.py`, `align_v4_session.py`, `run_night.py`, `magistrate_watchdog.py`, `align_v4_w1_synthetic.py`, `validate_align_v4_w1_plan.py`;
  - `hazard_refusals.json`, `night_gate.py`, `arm_retry.py`;
  - the config and template hunks.
- **Supporting code read:**
  - `run_night._run_night` from the plan parse to the hazard branch;
  - the chain spawn in `_run_chain_once_impl`;
  - `ThermalSession.wait`, `episode_phases`, `k_gated_d`, `k_x_g` and `k_g0_release_soak`;
  - the `run_campaign` member launches (`:2014`, `:4388`).

Nothing restricted was read or touched, no model weights were loaded, and nothing ran on the measurement Mac.
- Every run used `nice -n 19 taskpolicy -b /private/tmp/jwsol/venv-both/bin/python -B` in the worktree `jw-wt/r7-exec-review`.
- Each test process had its own `TMPDIR` under `/private/tmp/jwr7-tmp/exec-review`.
- One test module ran per process, with at most three test processes at once.
- Every process pointed `JOULEWISE_HOST_STATE_DIR` at a temporary directory, so the real `/Users/Shared/JouleWise/host-power` was never touched.

## What I executed

| Check | Result |
|---|---|
| Whole `tests/align`, one module per process, plus `tests.hazards.test_refusal_allowlist`, `tests.hazards.test_smc_enumeration` and six root modules (`test_run_night`, `test_arm_retry`, `test_night_gate`, `test_magistrate_watchdog`, `test_magistrate_watchdog_cli`, `test_bytes_h_session`) | `tests/align`: all 123 modules rc=0, 1,784 tests. The two hazards modules rc=0 (23 with skipped=1, and 16). Root: 5 of 6 rc=0; `test_run_night` failed 12 of 318, all in the environment classes below |
| My adversarial module `tests.align.test_r1_round7_exec_review` (below) | Ran 6. Three fail on `915f59446`: the R1 W1-deferral bypass, the plan-2 read-back admission and the close's lock leak. All 6 pass at `e51156033` |
| Directly affected modules rerun after the fix | All OK: `test_r1_round7_power` 29, `test_r1_round6_power` 25, `test_r1_round5_exec_review` 7, `test_r1_round6_exec_review` 9, `test_r1_rehearsal` 73, `tests.hazards.test_refusal_allowlist` 23 (skipped=1; one entry added for the new refusal site) |
| `tests.test_run_night -k powermode -k high_power -k marker -k Automatic -k night_lock -k restore -k dead_man -k lock`, after the fix | Ran 62, 59 OK. The 3 failures are `BindSupervisionProcessTests` (8 s `communicate` timeouts under `taskpolicy -b`), which `-k lock` matched through "blocking". The round-6 review and the round-7 cold pass recorded the same environmental class, and the cold pass found it passes without `taskpolicy -b` |
| `JW_WP22_FULL=1 tests.align.test_v4_w1_synthetic` (WP22 synthetic W1) | Ran 18 tests in 94.3 s, OK (expected failures=1, F3, as in rounds 4 to 6) |
| `night_worst_case_s(None)` | 46,886.99 s no redo; 52,286.99 s with one batch wait; 21,600 s R6-2 retry allowance; 73,886.99 s in all; `g0_timeout_s` 1,200. Step-d and each designed state are bounded at 3,900 s, and the gated runs and X-G at 1,800 s. `w1_inter_member_idle_s()` = {D: 300, X-G: 300}. These match LEAD-RULINGS-2 R7-2 and R7-9 (46,887 − 44,640 = 2,247 s) |
| `scripts/align_v4_kit.py --check` | No drift. Blocked on the same nine leaves (WP18 ×4, R0, R1 ×4) |
| pilot10-benign merge fidelity | For `r0.py`, `r0_host.py`, `smc_enumeration.py` and the four R0/SMC test modules, the change `97714c644..HEAD` equals pilot10-benign's own change since the merge base `c712318e5`, line for line. `ssd_qualification.py`, `align_ssd_qualification.py` and `test_ssd_qualification.py` are byte-identical to `e1a91226e`. The only R0 bytes that differ from pilot10-benign are the integrated lane's earlier report-only W1-requirement row (`b35f1bc6d`), which predates round 7 and was kept |
| v3 kit | `git diff 97714c644..HEAD -- configs/campaigns/align_pilot_v3` is empty, and so is the diff against pilot10-benign |
| R1 exit-path harness A (below) | 11 scenarios, all as expected |
| run_night exit-path harness B (below) | 7 scenarios, all as expected |
| Local Sol 6.1 xhigh as a second critic (static; its sandbox refused `nice`/`taskpolicy`, so it ran nothing) | 5 findings, triaged below. Audit of its events: **AUDIT CLEAN**. The only custody-path strings are `!restricted/**` exclusion globs in one `rg` command, and text inside repository files it read (`TASK_QUEUE.md`, the `powermode.py` diff, `magistrate_watchdog.py` constants). No command named, listed or read those paths or `/Users/Shared/JouleWise`, and its worktree was left clean |

**Suite details.**

- Every module except three started after my fixes (05:08 to 05:10 local). The three that started earlier, `test_moe_calibration`, `test_moe_review` and `test_analysis_metadata_baseline`, do not import the changed files.
- **Selected `tests/align` modules:**
  - `test_r1_rehearsal` 73, `test_r1_runtime` 33, `test_r1_runtime_e2e` 2, `test_r1_runtime_contract` 11, `test_v4_kit` 114;
  - `test_r1_round7_power` 29, `test_r1_round7_science` 16, `test_r1_round7_install` 6, `test_r1_round7_close_deferral` 3 (skipped=1);
  - `test_thermal_gate` 44;
  - the pilot10-benign R0/SMC modules: `test_r0_host` 44, `test_smc_quiet` 19, `test_ssd_qualification` 26. `tests.hazards.test_smc_enumeration` ran 16, OK.
- **Root modules:** `test_magistrate_watchdog` 158, `test_magistrate_watchdog_cli` 7, `test_night_gate` 112, `test_arm_retry` 36, `test_bytes_h_session` 36, all OK.
- **`test_run_night`'s 12 failures** are all in the classes the round-6 review and the round-7 cold pass recorded under `taskpolicy -b`:
  - 8 `NightDriverTests` installer tests ("test interpreter must load the battery fixture in child Pythons");
  - 3 `BindSupervisionProcessTests`;
  - 1 `QuietDriverIntegrationTests.test_supervised_worker_is_reaped_on_cancellation`.
  - None is a powermode, marker, lock or R7 test. The cold pass ran the same module at `915f59446` and got 17 failures in these classes.
- **Slowest:** `test_moe_calibration` 1,867 s and `test_bytes_h_session` 1,496 s.

### Harness A: R1 driver, real signals, host lock and marker

This is the round-6 harness carried forward. The scratch files are not committed: `/private/tmp/claude-501/…/scratchpad/r7harness/{child,parent}.py`.
- A child process runs `scripts.align_r1_rehearsal.run` with `_run` replaced by the test `FakeWorld` (fake sudo, pmset and runtime). The child adopts High Power and parks inside the named segment.
- While it is parked, a second process attempts a session-start restore and a night admission. Then the parent delivers real signals.

Across all 11 rows:
- In the 10 rows that park, the concurrent session start was `deferred_measuring_night`. The concurrent admission refused with "a measuring night holds the host night lock". The second process made 0 restore calls.

| Parked in (R7-1 order) | Signal | Outcome |
|---|---|---|
| `high_power_B` | TERM | rc 4 `aborted`; mode 0; both markers gone; lock free; no `r1_slots.json` |
| `step_D….precool` | INT | same |
| `step_D….precool_retry` (one step-d G0 timeout) | TERM | same |
| `planning_turn_R_plus_2C.precool` | HUP | same |
| `planning_turn_R_plus_0C.precool_retry` | INT | same |
| `D_spam_benign_s1_gated_held_a` (after D_bank) | TERM ×3 | same |
| `D_spam_benign_s1_gated_held_b` (after D_spam a) | HUP | same |
| `X_G_contrast` | TERM, then TERM inside a slow restore | same; the second TERM did not interrupt the restore |
| `D_bank_benign_s1_gated_held` | KILL | mode 2 with the host marker; lock free; the next session start restores |
| **New (R7-5):** `D_bank`, with a real "runtime child" that inherited the driver's lock (`pass_fds`) and survives | TERM | rc 4; **`restore_deferred`**; mode stays 2; both markers kept; lock still held. A session start while the holder lives: `deferred_measuring_night`. After the holder is killed: `restored` |
| Complete, adopted; step-d 1 G0 timeout, R+2 2 timeouts | none | rc 0 `complete`; mode 0; R+2 in `inconclusive_segments`; `g0_cap_w1.value_s` = 600 |

### Harness B: run_night under a declared 2, real signals

This uses the `NightDriverTests` fixture: fake probes, and fake sudo/pmset with the mode kept in a file. `run_night` parks inside the chain spawn after admission, holding the lock with its close registered. The spawn records the `pass_fds` it was given. In every row it was `[3]`, the host night lock, so R7-5 hands the lock to the chain.

| Signal | Outcome |
|---|---|
| INT, TERM, HUP | The close runs (R7-4): mode 0 and the marker gone. The log has "ac powermode close: restore Automatic". A later dead-man finds nothing to do |
| TERM, then TERM + HUP while the close's restore is in progress | The close completes (mode 0, marker gone, rc 0). Signals during the close are swallowed |
| KILL | Mode 2 with the marker. The dead-man restores (calls: restore, read) |
| **New:** TERM while a real child that inherited the lock (the "chain") keeps running | Close **deferred** ("the host night lock could not be retaken"): mode 2, marker kept. The dead-man while the holder lives does nothing (mode 2). After the holder is killed, the dead-man restores |

In the first run of the double-signal row, the second TERM arrived only after `run_night` had finished its close and restored the default handlers, so it ended the process (rc −15) after a correct close. I reran it with the second signal synchronised to the restore (the row above).

## Ruling by ruling

**R7-1 (order).** As written. `phase_plan` runs the designed states warmest first, then `planning_turn_R_plus_0C`, `D_bank`, `D_spam a`, `D_spam b`, `X_G_contrast`. `last_d_turn` gives D_bank the planning turn, D_spam a D_bank and D_spam b D_spam a. X-G gets D_spam b, which is W1's D → X transition. Each predecessor counts only with a released G0 and decode tokens > 0, so both runs of the replay pair follow a full gated D episode, and an inconclusive predecessor makes U5 inconclusive. Harness A parked in each of them in that order.

**R7-2 (G0 timeout, G0_cap_W1).** As written. One reading is for the lead to confirm (below).
- **One constant.** `configs/align/v4/r1_runtime.json` sets `g0_timeout_s` = 1,200.
  - The driver refuses at t0, before any power or runtime work, when that value is missing, outside [600, 1,200], or different from the committed value the kit reads.
  - The runtime arms it through the gate policy's optional `g0_cap_s`, for exactly `step-d`, `x-g`, the three gated kinds and the planning kinds.
  - `ThermalSession.wait` uses `policy.get('g0_cap_s', 600)`. Step-30b, the A-B-A legs, `g0-release-soak`, `d-4bit` and every v3 policy keep 600.
  - I traced the value from the config through `Segment.g0_cap_s`, `gate_policy` and `validate_gate_policy` to the `ThermalSession` policy. No member config, member cap or driver subprocess timeout cuts a 1,200 s G0 earlier, except the member deadman (below).
- **Every G0 wait is recorded.** Every kind that runs a G0 records `g0_wait_s` and `g0_timeout_s` as contract fields. `r1_slots.g0_waits` lists them in run order, superseded attempts and the release before each included.
- **G0_cap_W1.**
  - The driver (`w1_g0_cap`) and the kit (`align_v4_kit.w1_g0_cap`) both compute clamp(ceil(1.25 × max), 600, 1,200) over D_bank, D_spam a, D_spam b and X-G. A non-released G0 (`timeout`, `deadman`, `unobserved`) counts at 1,200, and so does an X-G that is not `measured` (R7-12).
  - On 500 random records (outcomes, waits with 0-3 decimals, X-G measured or inconclusive with any outcome) and at the boundaries 480.0 → 600, 480.0001 → 601, 959.2 → 1,199 and 960.0 → 1,200, the two agree on `value_s`, `waits_s`, `censored`, `max_g0_s`, `x_g_fallback`, `floor_s`, `factor` and `r1_g0_timeout_s`. That is the check the kit applies field by field (`G0CapAgreementTests`).
  - `inputs.R1.thermal_policy.g0_cap_s` must equal `value_s`, and `gate_policy_fields` copies it into every W1 member's thermal policy. Ruling 1(f)'s G0 term is `value_s` (`ruling_1f_fit`, and through it `max_fitting_b_d`).
- **The member deadman.** A gated run arms its 1,200 s G0 inside T_dead, and X-G inside its 1,086 s contrast deadman. This is W1's own structure, which R6-1 reproduces, so R1 cannot observe a G0 longer than the deadman. Sol rated this HIGH; I rate it LOW, open, because it can only make the cap more conservative:
  - Any release later than 960 s gives a cap of 1,200 anyway.
  - A deadman cut counts at 1,200.
  - So a truncated wait can never lower G0_cap_W1. It matters only if T_dead < 960 s, which needs I_D > about 660 s.
  - X-G's deadman (1,086 s) exceeds 960 s, so for X-G it never changes the value.
  - The builder already reported this as open.
- **The worst-case table** is recomputed and matches.
- **Builder interpretation, for the lead to confirm:** "the R6-2 precool/retry segments" was read as step-d and the designed start states (first attempt and retry) arming 1,200 s. The `idle-until-soak` precools keep their 1,500 s cap. The precools are band waits, not G0s, so I read it the same way.

**R7-3.** As written. Both `inconclusive_segments` refusals name the R1 re-run and the magistrate's call.

**R7-4 (TERM/HUP).** As written for `install` and for `run_night` before the chain exists or after it exits (harness B, and the install's real-signal tests). While the chain runs, see MEDIUM-3.

**R7-5 (lock lifetime).** As written for the chain and the R1 runtime child (harnesses A and B):
- `release` never calls `LOCK_UN`;
- `retake` closes the descriptor, then locks a fresh one without waiting;
- `pass_fds` moves the descriptor off FD 198.

Two gaps remain:
- The R1 driver's teardown undid a deferral (MEDIUM-1, fixed).
- The lock stops at `run_campaign`'s member launches (MEDIUM-4, open).

**R7-6.** As written. The launchd census runs before the session-start restore and before any `pmset`. It uses the shared installer's argv, its 10 s budget and its exact-absent-line rule.

**R7-7 (read-back).** `PowerModeGuard.restore`, `restore_automatic`, `restore_owed` (through `restore_automatic`) and the `run_night` close all read back before clearing a marker. One admission path kept the markers but did not refuse (MEDIUM-2, fixed).

**R7-8.** As written. Held signals reach the previous handler on the main thread at most 10 s after the first is held. The timer and the normal completion are serialised, so no extra signal follows a completed close. Sol F2 (the watchdog can fire after the driver's 20 s kill) stays open, as recorded.

**R7-9.** The corrections at LEAD-RULINGS-2:301 and in the integration report (:958, :1087) carry the true round-7 figures.

**R7-10.** As written. All four production `__main__`s call `mark_production_entry`. An override then refuses everywhere it is used, which `run_night` turns into an admission refusal for every plan. The path is in the admission record and log, the arm record, the session-start records and `r1_result.json`. The deviation recorded under R7-10 (the path is not in `receipt.json`/`result.json`) stands.

**R7-11.** As written:
- EWOULDBLOCK/EAGAIN alone counts as another holder;
- `night_refused_host_lock_error` is registered in `night_gate`, `arm_retry` and the allowlist;
- an exception before admission runs the restore path, under the night's lock when it holds one;
- a failed marker write after a plan-2 admission refuses before the chain, and the registered close restores.

**R7-12.** As written. An X-G that is not `measured` counts at 1,200 with `x_g_fallback: true`, and that alone never refuses. As the integration note and the cold pass (LOW-2) say, this sets the single G0 term to 1,200, so at realistic decode rates 1(f) will refuse W1 anyway.

**R7-13.** As written:
- The runtime records `alias_groups` inside the classification digest.
- The driver registers them.
- The kit refuses a missing or malformed group list, identical picks, and picks in one group.
- `smc_enumeration` is untouched.

R1 still reports its thermometry bar `pass` for aliased picks (cold LOW-3). I agree, LOW.

**R7-14.** Documentation only, and present in the contract doc.

## Findings

### MEDIUM

**MEDIUM-1 (fixed in `e51156033`): the R1 driver's teardown restored after a deferred guard restore.**

- **Where:** `scripts/align_r1_rehearsal.py`, the `finally` of `run` (`if host_lock.held: guard.restore()`).
- **The two deferrals:**
  - **No retake.** The guard drops its descriptor, so `host_lock.held` is False and the second call is skipped. Correct.
  - **W1 marker after the retake** (the infra lane's Sol F4 branch). The retake succeeded, so `host_lock.held` is True. The guard had set `armed = False`, so the second `guard.restore()` skipped both the retake and the W1-marker check. It ran `pmset … powermode 0`, read 0 back and unlinked both markers, including the W1 session's.
- **Consequence:** the W1 night that owned the span then meets mode 0 and refuses at admission. It fails closed, but the night is lost, and the code defeats the protection it adds.
- **Reachability:** this needs a W1 install to land inside the driver's release/retake gap. R7-14 notes that the single launchd label makes that unlikely today. Sol rated it HIGH; I rate it MEDIUM because it is reachable only in that narrow window and fails closed.
- **Fix:** the second attempt runs only when the guard did not defer. `r1_result.restore_deferred` now carries the guard's own deferral reason.
- **Test:** `R1FinalRestoreTests.test_the_finally_never_undoes_a_deferred_w1_span` runs the real `run` with `FakeWorld`. A W1 session's marker and mode 2 land at the harvest. The test asserts no AUTO after that, mode 2, the marker still owned by that session, and the lock free afterwards. It fails on `915f59446`.

**MEDIUM-2 (fixed in `e51156033`; R7-7): a plan-2 admission admitted after an R1 marker restore that did not read back 0.**

- **Where:** `joulewise/align/apple/powermode.py` `admit_ac_powermode`, in the branch that restores a non-W1 marker (an R1 crash).
- **What happened:**
  - With `expected` 0, a read-back of 2 refused through the mode comparison.
  - With `expected` 2, sudo exiting 0 while the mode still read 2 kept the markers, but the final comparison (2 == 2) admitted.
  - A working restore refuses in this case (0 != 2), so only a broken restore admitted, with a stale R1 marker and a restore path known not to work. The night's own close would then fail to restore too.
- **Rule:** R7-7 says "If the readback is not AC powermode 0, keep the markers and refuse."
- **Fix:** under any `expected` other than 0, a read-back that is not 0 refuses ("… did not read back 0 …; markers kept (lead ruling R7-7)"). The `expected` 0 path and its reason text are unchanged. The new refusal site is allowlisted in `hazard_refusals.json`.
- **Tests:** `AdmissionReadBackTests` covers both cases:
  - a stuck restore refuses with the markers kept (fails on `915f59446`);
  - a working restore still refuses on the mode and clears the marker.
- Sol found this one (its finding 4). It predates round 7, but R7-7's text covers it.

**MEDIUM-3 (open, for the lead; = round-7 cold pass MEDIUM-1): a TERM or HUP while the chain runs defers the restore and leaves the chain running.**

- My harness B "TERM with a surviving lock holder" row reproduces the outcome the cold pass describes:
  - the close cannot retake the lock and defers, as R7-5 requires;
  - the mode stays 2 with the marker;
  - the dead-man does nothing while the holder lives, and restores once it is gone.
- In the real chain wait loop, nothing calls `_terminate_process_group` on a `KeyboardInterrupt`, so the chain runs on without its deadline thread. That is the cold pass's probe M, which I did not repeat.
- It fails closed and is no regression: before R7-4, TERM killed `run_night` with the same outcome for the chain.
- But R7-4's "run their normal close (High Power restore included)" holds only before the chain spawns or after it exits.
- I agree with the cold pass's two options:
  - **(A)** terminate and prove the chain group gone on an interrupt after launch, before the closers run (the deadline path's own code);
  - **(B)** document the deferral.
- I did not fix it. Stopping a measuring chain from the signal path is a design choice, and the rulings do not settle it.

**MEDIUM-4 (open, for the lead; Sol finding 3): the lock stops at `run_campaign`'s member launches.**

- **Where:** `run_night` passes the lock to the chain, but `run_campaign` starts members with `subprocess.run(command)` (`:2014`) and `subprocess.Popen(list(command), …)` (`:4388`). Both use the default `close_fds=True`, so the members do not hold the lock.
- **Scenario:** a SIGKILL of `run_night`, the zsh chain and `run_campaign`, while a member survives.
  - The dead-man's group census still sees the member, because members stay in the chain's process group.
  - But a session start or admission tests only the lock, and can restore Automatic under the orphaned member.
- **Why MEDIUM, not higher:** that member's night has already lost its supervisor and custody, so no admitted number can come from it.
- **Relation to R7-5:** R7-5's text ("pass the lock fd to the chain") is met, but not its aim ("as long as the night's process tree"). This is the same class as infra Sol F1 for the R1 runtime's own children, which is already open.
- **Fix (a lead call):** pass the inherited descriptor through `run_campaign`'s member launches. That touches shared B5 infrastructure, so I left it.

### LOW

**LOW-1 (fixed in `e51156033`): `run_night`'s close kept the retaken lock on its `not_owner` return.**

- **Where:** `run_night._close_ac_powermode`. The `not_owner` branch (a W1 marker another session owns after the retake) returned before the `finally` that releases the lock.
- **Consequence:** in production the CLI process exits at once, so the impact is small. A long-lived caller would hold an unreachable lock that blocks every later session.
- **Test:** `NightCloseLockTests.test_the_not_owner_close_frees_the_retaken_lock` fails on `915f59446`.

**LOW-2 (open; = builder's open R7-2 item, Sol finding 1, rated HIGH by Sol): R1 cannot observe a gated or X-G G0 longer than the member deadman.** This is conservative by construction; see R7-2 above.

**LOW-3 (concur with the round-7 cold pass):** cold LOW-1 (`--dry-arm` restores on an interrupt), LOW-3 (R1's thermometry bar `pass` for aliased picks) and LOW-4 (the "protocol v4 updated" claims under R7-1 and R7-3). I did not re-derive them.

### Sol critic findings, triage

| Sol | Severity (Sol → mine) | Disposition |
|---|---|---|
| 1. A 1,200 s G0 inside a shorter deadman (gated, X-G) | HIGH → LOW | Open; already reported by the builder; conservative (LOW-2) |
| 2. R1 final restore bypasses the W1-marker check | HIGH → MEDIUM | Fixed (MEDIUM-1). I had found the same path independently |
| 3. The lock does not reach `run_campaign`'s members | HIGH → MEDIUM | Open (MEDIUM-4) |
| 4. A plan-2 admission after an R1 restore that reads back 2 | MEDIUM | Fixed (MEDIUM-2) |
| 5. The `not_owner` close keeps the lock | LOW | Fixed (LOW-1) |

## Relation to the round-7 cold pass (`d20ccd829`)

- **Cold MEDIUM-1** is my MEDIUM-3, and my harness reproduces it.
- **Cold LOW-1, LOW-3 and LOW-4:** I agree with all three (my LOW-3).
- **Cold LOW-2** (R7-12 nominal): agreed, under R7-12 above.
- **"The second idempotent attempt in the teardown runs under the retaken lock":** this holds only when the guard did not defer. When it deferred on a W1 marker, that attempt bypassed the check (my MEDIUM-1, fixed).
- **R7-7 "sound":** this missed the plan-2 admission path (my MEDIUM-2, fixed).

## For the lead

- **MEDIUM-3:** choose (A), terminate the chain on an interrupt after launch, or (B), document the deferral. Before a W1 arm under an adopted High Power, (A) is the safer choice.
- **MEDIUM-4:** pass the host night lock through `run_campaign`'s member launches, or accept the gap, as for infra Sol F1.
- **Confirm the builder's reading** of "the R6-2 precool/retry segments" (step-d and the designed states arm 1,200 s; the precools keep 1,500 s).
- **The R7-2 1(f) consequence:** with a G0 term of at least 600 s (1,200 s whenever X-G is inconclusive or any gated G0 times out), 1(f) will likely refuse W1 at about 20 tok/s. The ruling 1(e) fallback is still unruled.
- **R1 can be armed on this head.** None of the findings touches R1's evidence path, and the R1 night runs under plan 0 with the driver holding the lock.
