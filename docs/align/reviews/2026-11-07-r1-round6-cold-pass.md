# Cold final pass: ALIGN v4 R1 round-6 integrated head (2026-11-07)

**Verdict: no BLOCKER, no HIGH. One MEDIUM, six LOW.**

Nothing on this head admits a night on a host whose AC powermode differs from the plan's. Nothing restores the mode under a night that holds the host night lock. Nothing changes v3 kit bytes.

- The MEDIUM is a science point the R6-1 builder decision "Order" creates. It is not a code bug. With the gated block moved after the designed start states, the two runs of the R1 replay pair follow different predecessors. That pair's |E_a − E_b| is the U5 σ_pair, so the predecessor difference can inflate σ_pair and make U5 lenient. The fix is a one-line reorder, and the lead has to confirm the order in any case.
- The LOWs are:
  - one fail-closed High Power path in the R1 guard, which clears the markers without a read-back;
  - an unbounded signal deferral in exec LOW-3;
  - one arithmetic claim in the docs that round 6 made false;
  - two weak spots in the host-state plumbing (the env override, and a lock-file `OSError`);
  - X-G's status, which the kit never reads.

I changed no code.

Reviewer: Opus 5.5, cold, with no context beyond the documents below.

Target: `lane/2026-11-06-v4-r1-integrated@54d584de6` versus `origin/lane/2026-11-05-align-pilot10-benign` (merge base `c712318e5`). I focused on the round-6 delta `998ee2ab0..54d584de6` (49 files, +3,501/−347), plus the admission, close and install code it relies on.

Documents read:
- the "Round 6 integration" section of `docs/run_reports/2026-11-06-align-v4-r1-integration.md`;
- the Round 6 section of `LEAD-RULINGS-2.md` (R6-1 to R6-8, the builder decisions and the cold LOW-6 numbers);
- `LEAD-RULINGS-1.md` L1 and L2;
- `CHAIR.md` ruling 1;
- `docs/align/r1_runtime_contract.md`;
- the W1 roster and R1 passages of `docs/align/pilot_protocol_v4.md` (:95-140, :230-260, :645-670);
- the round-5 executing review and round-5 cold pass, which round 6 rules on;
- the finding list of the Fable cold pass at `a2193446d`.

Code read:
- **Line by line:**
  - `joulewise/align/apple/powermode.py`;
  - the round-6 hunks of `scripts/align_v4_session.py` (`prepare`, `session_start_restore`, `install`, `arm_checks`);
  - in `scripts/run_night.py`: `_run_night` up to the hazard branch, `_admit_ac_powermode`, `_restore_owed_on_exit`, `_close_ac_powermode`, `_own_high_power_marker` and `_take_host_lock`;
  - `scripts/magistrate_watchdog.py` `_restore_abandoned_high_power`;
  - in `scripts/align_r1_rehearsal.py`: `PowerModeGuard`, `phase_plan`, `_segment`, `_calibration_segment`, `check_w1_schedule`, `_check_schedule`, `schedule_inconclusive_reason`, the `last_d_turn` logic in `run`, `deadman_summary`, `budget_fit_inputs`, `night_worst_case_s`, `u5_verdict`, `projected_mde` and the staged registration;
  - in `joulewise/align/apple/r1_runtime.py`: `g0_timeout_only`, `only_g0_unreleased`, `close_managed_session`, `k_step`, `k_step_d`, `k_gated_d`, `k_planning`, `k_x_g`, `schedule_fields`, `reference_fields` and `s7_for_picks`;
  - `r1_runtime_contract.py`;
  - the round-6 kit diff (`check_r1_evidence`, `check_r1_fast_band`, `check_duty_bar_consistency`, `w1_inter_member_idle_s`, `ruling_1f_fit`, `check_r1_budget_and_policy`, `check_wp18_turn_contents`, `gate_policy_fields`);
  - `scripts/align_v4_wp18_fixtures.py`.
- **Also:** `bytes_h_session.install` (its non-installing returns), the `workload.py` G0-unreleased stop, the powermetrics stop drain bound, and the R1 zsh chain (unchanged in round 6).

Nothing restricted was opened, no weights were loaded and nothing touched the measurement Mac. Every run used `nice -n 19 taskpolicy -b /private/tmp/jwsol/venv-both/bin/python -B` with `TMPDIR=/private/tmp/jwr6-tmp/opus`, one module per process, in a worktree under `jw-wt/`. Each probe set `JOULEWISE_HOST_STATE_DIR` to a scratch directory.

## What I executed

| Check | Result |
|---|---|
| `tests.align.test_r1_round6_power` | Ran 25, OK |
| `tests.align.test_r1_round6_lows` | Ran 18, OK |
| `tests.align.test_r1_rehearsal` | Ran 73, OK |
| `tests.align.test_v4_kit` | Ran 100, OK |
| `tests.align.test_r1_runtime_contract` | Ran 11, OK |
| `tests.align.test_v4_powermode_record` | Ran 9, OK |
| `tests.test_run_night -k powermode -k high_power -k marker -k Automatic -k night_lock -k restore` | Ran 31, OK |
| `tests.test_magistrate_watchdog -k high_power -k abandoned` | Ran 3, OK |
| **Probe W** (in-process): `w1_inter_member_idle_s()`, `check_w1_schedule(None)`, `night_worst_case_s(None)` | Idle is `{'D': 300.0, 'X-G': 300.0}`, and the d_spam, d_bank and x_g templates each have 300 s.<br>no_redo **44,486.99 s**; one batch wait 49,886.99; R6-2 retries 19,200; all 69,086.99. These match LEAD-RULINGS-2's 44,487 / 49,887 / 19,200 / 69,087.<br>The phase order is: …, `planning_turn_R_plus_0C`, `D_spam_benign_s1_gated_held_a`, `D_spam_benign_s1_gated_held_b`, `D_bank_benign_s1_gated_held`, `X_G_contrast` (MEDIUM-1). |
| **Probe K** (in-process, `test_v4_kit.ready_inputs`) | `thermal_policy.sensors` set to None, a string or a list: refused.<br>A per-run and an overall duty verdict of `inconclusive` with no lead fallback: refused.<br>`inconclusive_segments` missing: refused.<br>Two gated rows, or a duplicated run name: refused.<br>`x_g.status: inconclusive`: **admitted** (LOW-6). |
| **Probe G** (in-process, fake runner: `sudo -n pmset -c powermode 0` exits 0, but `pmset -g custom` still reads 2) | `PowerModeGuard.restore()` returns True and **removes both markers** with the mode still at 2. The next plan-0 `admit_ac_powermode` then refuses ("AC powermode 2 != expected 0") and runs **no restore**. `powermode.restore_automatic` under the same runner keeps its marker (LOW-1). |
| `origin/lane/2026-11-06-v4-r1-integrated` re-fetched before commit | still `54d584de6` |

## Findings

### MEDIUM

**MEDIUM-1 (a, d): under the R6-1 order, the U5 replay pair's two runs follow different predecessors, so σ_pair can carry predecessor variance and U5 can pass leniently.**

- **Where:**
  - `scripts/align_r1_rehearsal.py:289-290` runs the gated block as `GATED_D_RUNS` (`:46`: spam a, spam b, bank), then X-G, right after `planning_turn_R_plus_0C`.
  - `REPLAY_PAIR` (`:51`) is (spam a, spam b).
  - `u5_verdict` (`:450-461`) takes σ_pair = max(|E_a − E_b|, 2.97 J). `projected_mde` uses the same difference.
- **What changed:**
  - Under R5-1 both replay runs started from a precool to the G0 band of R, the same defined state.
  - Under R6-1 there is no precool. Each run follows its predecessor with only the 300 s idle:
    - spam a follows the R + 0 °C planning turn: one 10k-prefill + 4,096-decode turn, heater-preheated to R;
    - spam b follows spam a: a full gated, held D episode of up to T_dead.
  - The G0 still releases both at S_slow ≤ R + δ_slow. But the G0 wait, the die and package state at release, and the first turns' thermal trajectory differ systematically between the two.
- **Why it matters:**
  - L2 defines σ_pair as identical-work pair noise.
  - The code already treats an inflated |E_a − E_b| as a false-PASS risk for U5 (`:467-471`, round-4 HIGH-2), and asymmetric predecessors are a second source of the same inflation.
  - CHAIR 1(g) (`CHAIR.md:40`) swapped W1 ordinals 17 and 18 precisely so that W1's replay follows the same predecessor class as its original.
  - No data are corrupted, and the duty bar is unaffected: every gated run must pass, and b and bank are the D-after-D cases.
- **Cheap fix (for the lead, who must confirm the builder's "Order" decision in any case):**
  - Run the gated block as **D_bank, D_spam a, D_spam b, X-G**.
  - Each replay run then follows a full gated D episode with the same idle. D_bank takes the planning-turn predecessor, and it is not in the pair.
  - X-G still follows a D turn (spam b), so it keeps W1's D → X transition.
  - The 1(f) and duty arithmetic is unchanged.
- **Otherwise:** record in the deviation log that R1's σ_pair includes predecessor variance.

### LOW

**LOW-1 (b, e): the R1 guard clears both High Power markers on a zero `sudo` exit, without reading the mode back.**
- **Where:** `PowerModeGuard.restore` (`align_r1_rehearsal.py:200-210`) unlinks `$MEASUREMENT_ROOT/.align-r1-high-power` and, new in round 6, the host-level marker when `sudo -n pmset -c powermode 0` exits 0. `__exit__` (`:245`) adds no query.
- **The ruling and its implementation say otherwise:**
  - R6-7 says "restore first, then re-check".
  - The infra lane's F6 is recorded in LEAD-RULINGS-2 as "markers are removed only after the read-back is 0", and `powermode.restore_automatic` does read back.
- **Probe G:** a restore that exits 0 but leaves the mode at 2 erases the obligation. The next plan-0 night then refuses on the mode and never restores, so a manual restore is needed.
- **Severity:** this fails closed, and a zero-exit `pmset` that does not apply the mode is unlikely.
- **Fix:** query after the AUTO, and unlink only on a read-back of 0. Alternatively, call `powermode.restore_automatic` for the host marker.

**LOW-2 (b), plausible: exec LOW-3's signal deferral is unbounded, and it delays the runtime's own 15 s watchdog.**
- **Where:**
  - `close_managed_session` (`r1_runtime.py:135-164`) swaps TERM, INT and HUP to `hold` until `managed.close()` returns.
  - The runtime's teardown watchdog is armed only inside the real handler (`:835`, `threading.Timer`).
- **What can go wrong:** a first TERM that lands during a session close starts no watchdog until the close returns. If the close takes longer than the driver's 20 s grace, the driver SIGKILLs the runtime. That loses:
  - the watchdog's own `powermetrics` TERM;
  - the `aborted, watchdog: true` custody record.
- **How likely:** the powermetrics drain is bounded to a few seconds (`powermetrics.py:623-628`), so a close that long needs an unusually slow parse or stop.
- **Fix:** give the deferral a bound, for example deliver the held signal after about 10 s even if the close has not returned. Alternatively, have `hold` arm the same watchdog timer.

**LOW-3 (e): one window claim is no longer true on the round-6 numbers.**
- LEAD-RULINGS-2 `:301` and the integration report `:958` say W1's `window_cap_s` of 44,640 s "is below even the no-redo R1 worst case".
- The round-6 no-redo case is 44,487 s (probe W), which is below 44,640 s.
- The claim held for round 5's 45,087 s. It holds now only with the +1,200 s idle caveat (45,687 s).
- The conclusion (the template gives no R1 `window_max_s` to copy) still stands. Correct the sentence when the lead sets the R1 plan's window.

**LOW-4 (b): the host state directory is set only by an environment variable, and nothing records or cross-checks it.**
- **Where:** `powermode.host_state_dir` (`powermode.py:90-93`) reads `$JOULEWISE_HOST_STATE_DIR`. The LaunchAgent the installer writes does not carry it (`install_night_agent.sh` sets no `EnvironmentVariables`).
- **What can go wrong:** a shell that exported the variable, for example left over from a manual test, splits the state. `install` would write the W1 marker and take its lock in one directory, while the night, the watchdog's J4 restore and later admissions use the default. Their marker and lock would then not interact.
- **How it would show:** the night writes its own marker at admission, so a SIGKILL is still caught. But a never-launched W1 would stay at 2 until a session start in the same shell.
- **Fix:** refuse a non-default host state directory outside tests, or record it in the arm record and the plan, and refuse at admission if they differ.

**LOW-5 (b): a plan-2 night that cannot create the lock file refuses with the wrong reason and with no restore.**
- **Where:**
  - `_take_host_lock` (`run_night.py:4115-4126`) swallows the `OSError` from `HostLock.acquire`.
  - The caller then refuses with "another night holds the host night lock" (`:4218`) and skips the restore, which runs only while it holds the lock.
- **Consequence:** the host stays at 2. The next session start's `restore_owed` then fails on the same `OSError` (action `error`), so `session_start_restore` refuses.
- This fails closed, but it needs a manual restore and the record names the wrong cause.
- A related gap: exceptions before admission (for example a failed `night_dir.mkdir` or `_existing_record`) also return without a restore.
- **Fix:** record the real cause. Attempt `restore_automatic` with no lock when the lock file itself is unavailable: no other night can hold a lock that cannot be opened.

**LOW-6 (c), for the lead: the kit never reads `r1_slots.x_g`.**
- **Probe K:** `x_g.status: inconclusive` is admitted.
- This was also true before round 6, so it is not a regression.
- **Why it now matters:**
  - Under R6-1, X-G is R1's only D → X G0 observation (it follows D_bank).
  - CHAIR 1(c) asks the lead to "predict G0 for D → X and D → D transitions" before freezing W1, and protocol v4 :655 lists "one X-G identity run".
- **Decide one of:**
  - an inconclusive X-G is acceptable for W1 and the prediction comes from the ruling 1(c) recovery curve; record that;
  - the kit requires `x_g.status == "measured"`.

## Already open, not re-reported

These are listed in "Open after round 6" and still hold on this head:
- Sol F2: the lock lives only as long as `run_night` or the R1 driver, not their process trees;
- Sol F3: the W1 close restores before the chain is proven stopped;
- Sol F4: plan-0 nights do not hold the lock;
- the R6-1 builder decisions: order (see MEDIUM-1), "schedule = the member's own idle", "no D work", and the gated G0 cap in 1(f);
- R6-2: any `inconclusive_segments` entry refuses W1;
- the fail-closed consequence of a session start during an armed High Power session;
- the R1 plan `window_max_s` (see LOW-3);
- the WP18 F7 Mac check;
- exec LOW-3's main-thread scope;
- the three hardware checks carried over from round 5.

One observation, not verified: under R6-1 the only thing between a D turn and the next member's G0 is meant to be W1's schedule.
- In R1 the gap also includes a new runtime process, a model load and session start-up.
- Whether a W1 member has the same overhead (its `run_benchmark` per member) is not recorded anywhere I read.
- If W1's per-member overhead is shorter, R1's G0 is slightly cooler and less conservative. The magistrate's first R1 night can measure the gap: the planning turn's last decode to D_spam a's `idle_baseline` start.

## Checked and found sound

- **R6-1:**
  - The idle comes from the W1 plan template's member configs (one value per role, otherwise `ValueError`), not a literal. The driver checks the runtime templates against it at t0, before any power or model work. The kit binds `duty_bar.schedule` to the same reading.
  - There is no precool or batch-window wait before a gated run or X-G: they are not quiet kinds, so `_segment` neither waits nor releases.
  - A G0 timeout stops the member before turn 0 (`workload.py:444-500`). So "no D work" (a timed-out G0, or zero decode tokens) correctly makes the next run INCONCLUSIVE.
  - `last_d_turn` resets after X-G and the 30B steps. Precools do not count as model segments.
- **R6-2:**
  - The precools sit before step-d and before the R + 2 and R + 0 °C states, and the post-D cooldown precedes R + 4 °C. Each cap is the runtime config's 1,500 s.
  - The retry runs exactly once. It is preceded by a fresh `idle-until-soak`, and its recovery curve is row-checked (`_check_precool` → `_check_recovery_curve`).
  - The first attempt is moved to `.g0_timeout1`, and the rejected and release names never collide (`_fresh_name`).
  - Only a pure G0 timeout counts as INCONCLUSIVE (`g0_timeout_only`); any other incompleteness still fails the segment.
  - An INCONCLUSIVE step-d skips the gated runs and X-G, writes `slots` null, and the kit refuses it.
- **R6-3:**
  - The driver's rate is tokens over `phases_s.decode` per gated run, and the minimum includes step-d.
  - The kit re-derives the minimum and refuses a stale recorded rate. The last-turn term keeps the full cap, and there is no code fallback.
- **R6-4 / cold LOW-1 / LOW-2:**
  - With changed picks, `turn_cap_s`, `delta_slow_c` (with an S6 tuning receipt from the R1-pick band) and `delta_fast_c` bind to `s7_for_r1_picks`, and both roles' bands are computed (`r1_runtime.py:724-754`).
  - The policy sensors must equal the R1 picks and `s7_for_r1_picks.keys`.
  - The accepted quiet-window reference rule is recorded.
- **R6-5:** the digest must be 64-hex and equal to the R1 record's. It is stripped before gate-policy validation and member install (`gate_policy_fields`).
- **R6-6:** `cooldown_after_30b` is gone. Its only reader was the phase table, and step-30b keeps its 600 s recovery observation.
- **R6-7:**
  - The host marker is written before every mode-2 set: by `enter_high_power`, the R1 `high()` and admission without a marker.
  - Every mode-2 holder holds the lock: `install` for its whole arm, `run_night` from before its admission read to its close, and the R1 driver for its run.
  - `restore_owed` and `admit_ac_powermode` never restore while another process holds the lock (they take it with LOCK_NB, or use the caller's).
  - The non-measuring exits are covered: malformed plan, rerun, J4 `launch_abandoned`, admission refusal (mode mismatch or failed read), the installer's no-op return, the watchdog J4 release, and `prepare`/`install` session starts.
  - Each restore is owner-scoped where a retried night could be harmed.
  - The R1 teardown restores only while it holds the lock. `admit_ac_powermode` removes markers only after a read-back of 0. The flock is per open-file description, non-inheritable, and dies with its holder.
  - No R1 night can run its unconditional `pmset 0` under a W1 High Power night: plan-0 admission refuses there, on the mode or on the lock.
- **R6-8:**
  - The registration is committed atomically, only beside a `complete` terminal record. `with guard:` closes before the slots are built, so a failed restore turns the status into `refused`.
  - The duty bar is re-derived FAIL > INCONCLUSIVE > PASS.
  - The WP18 rows are bound to their turn index and the seed-law per-turn seed. This matches `endpoint.py:708` (`turn_seed(seed, turn_index)`) and the `pilot_analysis.py:139-141` check.
  - The soak-reference check now reads the soak's `sensor_roles.s_slow`.
- **Kit and v3:** the kit's suite passes. `git diff origin/lane/2026-11-05-align-pilot10-benign -- configs/campaigns/align_pilot_v3` is empty, as the integration report states.

## Claims in the integration report and the reviews

- The round-6 tails for the modules I reran match: 73 / 100 / 18 / 25 / 11 / 9.
- The cold LOW-6 numbers match probe W to the second.
- "The R1 chain zsh is unchanged" is true for round 6.
- "Markers are removed only after the read-back is 0" (F6) holds for `powermode.py` and `run_night`, but not for the R1 guard (LOW-1).
- "Below even the no-redo R1 worst case" is false on the round-6 numbers (LOW-3).
- Nothing else in the integration section, the Round 6 rulings record or the contract's R6-7 text contradicts the code.

## Verdict for the R1 arm item

**R1 can be armed on this head.** None of the findings touches R1's evidence path or its power-mode handling, apart from LOW-1, which fails closed.

Before R1's data are read, the lead should rule on the gated-block order (MEDIUM-1). It is one line in `phase_plan`, and it is cheaper to fix before the night than to explain U5 after it.

Before a W1 arm under an adopted High Power, LOW-1, LOW-4 and LOW-5 are worth closing alongside Sol F2/F3/F4. Each of them fails closed, but each costs a lost night and a manual `sudo -n pmset -c powermode 0`.
