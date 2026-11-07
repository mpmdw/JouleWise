# Executing review: ALIGN v4 R1 round 5 (2026-11-06)

**Verdict: ADMIT_WITH_FIXES.** No BLOCKER and no HIGH. Each ruling R5-1 to R5-10 is implemented as written in `LEAD-RULINGS-2.md`. The one integration deviation (the A-B-A leg bound uses I_D = 1,750 s) is recorded there and only waits longer. I fixed two MEDIUM findings and one LOW in `ad9288196`, each with a test that fails on `d1639a0b3`:

- a first signal inside the W1 High Power entry left the host at 2 (found by the Sol critic);
- the ruling 8 batch-window bound for the steps and the designed start states left out the G0 and quiet time that R5-2 moved outside the deadman (found by me and by Sol);
- the gated-run budget check accepted a numeric string `T_dead`.

Five MEDIUM findings are left for the lead. Two are design points, and none of them can admit bad data. The most costly is that step-d and the R + 0 °C designed start state now each follow a full D turn with only their own 600 s G0, and a G0 timeout there still refuses the whole R1 night (MEDIUM-1).

No exit path I could drive leaves the host in High Power where a night that did not declare 2 would admit it. I drove them with real signals, through the driver alone and through the real zsh chain with real runtime subprocesses, including R5-5's new long High Power span (step-d through the planning turns). One path does leave the host at 2: a W1 launch that the watchdog abandons after install. That path fails closed, and the fix belongs in the watchdog (MEDIUM-4).

- Reviewer: Opus 5.5. This is an executing review, and I did not write any of the code under review.
- Target: `lane/2026-11-06-v4-r1-integrated@d1639a0b3` against `c304685d7` (34 files, +4,259/−226; this includes the round-4 fix `105de4588` and review `54e844b87`).
- Read first:
  - the round-4 executing review and the round-4 Fable cold pass;
  - the integration report (its round-5 section);
  - the round-5 infra run report;
  - `LEAD-RULINGS-2.md`, `CHAIR.md`, `LEAD-RULINGS-1.md`, `pilot_protocol_v4.md` :243-253 and the R1 runtime contract.
- Code read line by line (the whole round-5 diff):
  - `r1_runtime.py`, `r1_runtime_contract.py`, `powermode.py`, `external_volume.py`, the `workload.py` hunk;
  - `scripts/align_r1_rehearsal.py`, `align_v4_kit.py`, `align_v4_session.py`, `align_v4_wp18_fixtures.py`, the `run_night.py` and `b5/plan.py` hunks.
- Supporting code read: the `EpisodeDeadman` re-arm path (`budget.py`, `workload.py` G0 entry), `ThermalSession.capture_reference`/`wait` and the J4 launch-abandoned branch of `run_night`.

Nothing restricted was read or touched, no model weights were loaded, and nothing ran on the measurement Mac. Every run used `nice -n 19 taskpolicy -b /private/tmp/jwsol/venv-both/bin/python -B` with a per-process `TMPDIR` under `/private/tmp/jwr5-tmp/exec-review`, one test module per process, at most three at once (two suite workers plus one other job), in the worktree `jw-wt/r5-exec-review`.

## What I executed

| Check | Result |
|---|---|
| Whole `tests/align`, one module per process (115 modules, `xargs -P 2`) | All 115 modules rc=0, OK: **Ran 1,535 tests** (skipped=35; the integration tail had 1,534, and the extra test is the new `W1HighPowerTests` one). Only `test_moe_calibration` and `test_moe_review` started before my fixes, and they do not touch the files the fixes change; every other module ran on the fix commit's code. Slowest: `test_moe_calibration` 3,576 s, `test_moe_review` 998 s, `test_analysis_metadata_baseline` 786 s. Selected: `test_r1_rehearsal` 62, `test_r1_runtime` 31, `test_r1_runtime_e2e` 2, `test_v4_kit` 88, `test_v4_wp18_fixtures` 11, `test_r1_inventory` 11, `test_r1_runtime_contract` 9, all OK |
| New module `tests.align.test_r1_round5_exec_review` (my adversarial tests, below) | Ran 6, OK at the fix commit. The `T_dead` subtest fails on `d1639a0b3` |
| `tests.align.test_v4_kit.W1HighPowerTests` | Ran 9, OK at the fix commit. The new `test_a_signal_inside_the_high_power_entry_still_restores_automatic` fails on `d1639a0b3` (`2 != 0`) |
| `tests.align.test_r1_rehearsal.Round5RulingTests.test_batch_window_admission_uses_each_segment_s_full_bound` (amended) | OK at the fix commit. It fails on `d1639a0b3`: the bounds were `[…, 2400, 2700, 2700, 2700]` and no 3,300 |
| `tests.align.test_r1_runtime_contract` (after the contract doc edit) | Ran 9, OK |
| `JW_WP22_FULL=1 tests.align.test_v4_w1_synthetic` (WP22 synthetic W1) | Ran 18 tests in 198.7 s, OK (expected failures=1, F3, as in round 4) |
| `scripts/align_v4_kit.py --check` | No drift. Blocked on the same nine leaves as the integration report (WP18 ×4, R0, R1 ×4) |
| `git diff origin/lane/2026-11-05-align-pilot10-benign -- configs/campaigns/align_pilot_v3` | Empty |
| R1 exit-path harness A: the real driver, the test `FakeWorld` as the command boundary (fake sudo/pmset/runtime), real signals | 8 scenarios, all as expected (below) |
| R1 exit-path harness B: the real zsh chain, real driver, real runtime subprocesses on the synthetic backend, fake sudo, real signals to the process group | 5 scenarios, all as expected (below), including a complete adopted run |
| Local Sol 6.1 xhigh as a second critic | 6 findings, triaged below. Audit of its events: **AUDIT CLEAN** (the only custody-path strings are inside repository docs it read: `AGENTS.md`, CHAIR, the infra report; no command named or listed those paths) |

### Exit-path harness A: real driver, real signals, adopted series mode

Scratch harness, not committed: `/private/tmp/claude-501/…/scratchpad/harness/{child,parent}.py`. A child process runs `scripts.align_r1_rehearsal.run` with `_run` replaced by the test `FakeWorld`, which adopts High Power (A1 20 s, B 30 s, A2 21 s). It parks inside the named phase, and the parent delivers real signals. Every row: `r1.run` returned 4 (`aborted`, `KeyboardInterrupt: signal N`), the fake host ended at 0, the marker was gone, `r1_result.json` was written, no `r1_slots.json` was written, and the last powermode records were `restore_automatic` ×2.

| Parked in | Mode while parked | Signals |
|---|---|---|
| `high_power_B` | 2 | TERM |
| step-d (series) | 2 | TERM |
| `D_spam_benign_s1_gated_held_a.precool` | 2 | INT |
| `planning_turn_R_plus_0C` | 2 | HUP |
| `X_G_contrast` | 2 | TERM ×3 |
| `D_bank_benign_s1_gated_held` | 2 | TERM, then TERM after the restore started |
| `D_bank_benign_s1_gated_held`, restore slowed by 1 s | 2 | TERM, then TERM inside the slow `sudo pmset -c powermode 0` |
| step-d, not adopted | 0 | TERM |

Three of these rows are now a committed test (`RealSignalSeriesHighPowerTests`).

### Exit-path harness B: real zsh chain and runtime

This is the round-4 reviewer's harness (`/private/tmp/jwr4-tmp/r4rev/harness/`), copied into my scratchpad and pointed at this worktree, with two changes:

- the synthetic runtime config sets `powermode_file` to the fake-sudo state file, so each member's ruling 7 observation follows the host (R5-5's member checks need this);
- an `ALIGN_R1_RUNTIME` shim runs the real `r1_runtime.main` with a synthetic GPU-clock decline at 30 s in mode 2 and 20 s in mode 0, so the real A-B-A legs adopt High Power.

Signals go to the process group, as `run_night` sends them.

| Scenario | Signal point | Exit / teardown | Host mode | Marker | `r1_result` | Runtime custody | Group left |
|---|---|---|---|---|---|---|---|
| F | none (complete run) | 0 | 0 | removed | complete; `high_power.verdict: adopt`, `ac_powermode: 2`, `slots_ac_powermode: 2`; sudo sequence 0,0,0,2,0,**2** (series),0 (before calibration-post),0,0,0 | every segment complete | none |
| G | TERM inside step-d under the adopted series mode 2 | 130 / 4.2 s | 0 | removed | aborted (signal 15) | step-d: aborted, 15 | none |
| H | TERM, TERM, INT, HUP 0.3 s apart at the first gated-run precool (series 2); the synthetic precool released almost at once, so the burst landed at the segment boundary | 130 / 2.9 s | 0 | removed | aborted (signal 15) | every finished segment complete | none |
| I | `killpg` KILL inside `planning_turn_R_plus_0C` (series 2) | −9 | **2** | **present** | none | earlier segments complete | none |
| E | TERM inside the High Power B leg | 130 / 2.9 s | 0 | removed | aborted (signal 15) | `high_power_B`: aborted, 15 | none |

After I, `run_night._admit_ac_powermode` against the same host (fake sudo, state-file pmset): a plan expecting 0 restored Automatic, re-read 0 and admitted (marker removed); with the crash state recreated, a plan declaring 2 restored, then refused (`AC powermode 0 != expected 2`). So the R1 crash marker (written by the driver, never mistaken for the W1 marker) is honoured by both plan classes, and a SIGKILL during R5-5's long High Power span is never admitted by a night that expects 0.

## Ruling by ruling

**R5-1 (gated runs use the soak R; bounded precool; timeout INCONCLUSIVE). Implemented.**
- `k_gated_d` and `k_x_g` install the soak R through `reference_hook` before warmup. `capture_reference` returns early when a reference is set, so no warm self-capture happens (`thermal_gates.py:391`).
- The driver refuses a run whose `reference_source`/`reference_c` is not the soak's.
- Each gated run is preceded by `idle-until-soak` (cap 1,500 s) on the one-sided band S_slow ≤ R + δ_slow. X-G's precool is `cooldown_after_D`.
- `deadman_summary(precool_released=False)` makes that row `inconclusive`. `duty_verdict` gives FAIL over INCONCLUSIVE over PASS. My test shows an inconclusive run never masks a failing one, and that a bank-run precool timeout leaves U5 alone.
- One side effect: the post-D cooldown's band also became one-sided (it was |S_slow − R| ≤ δ). That is consistent with G0 and the ruling text, and it only shortens a wait on a host colder than the soak. See MEDIUM-2 for the design point the builder raised.

**R5-2 (deadman covers the decode only; start-state order). Implemented.**
- `planning_hook` pops the deadman from the G0 wait, so the G0 runs on its own 600 s cap. The preheat runs inside the hook (900 s cap). `rearm_deadman` resets `deadline_ns` in the `finally` after both.
- `EpisodeDeadman` reads `deadline_ns` on every check, so the re-arm takes effect. `token_budget.deadline_origin` records it.
- The builder also re-arms the deadman for step-30b and step-d, after the G0 and the 300 s quiet. That follows from R5-5's quiet window. It does not change I_D, because `derive_step_d_slots` measures the episode from the G0 start.
- The order is R + 4, R + 2, R + 0, recorded in the contract doc and in `planning_temperature.run_order_offsets_c`. See MEDIUM-1 for what the order cannot fix.

**R5-3 (a leg without its own G0 release is INCONCLUSIVE; R1 continues). Implemented.**
- `k_step(leg=True)` returns `leg_status: inconclusive`, `g0_released: false`, `t_decline_s: null`, with exit 0.
- `aba_adoption` gives `inconclusive` with rule `not_evaluated`. The series stays Automatic, and R1 continues.
- See LOW-2 (Sol F2) for the ordering of this check against the completeness check.

**R5-4 (no unbudgeted gated D; the kit binds the budget and the policy; ruling 1(f)). Implemented.**
- `gated_budget` (runtime) and `_check_step_d` (driver, right after step-d) refuse any B_D that is not an int multiple of 1,024 in [1024, 40960]. My test drove 10 non-evidence values (0, 1023, 1025, 4608, 41984, 8192.0, `true`, `"8192"`, null, NaN) through both: the driver refused before any gated run was invoked.
- `T_dead` accepted `"1200"` (LOW-1, fixed).
- `check_r1_budget_and_policy` binds `inputs.R1.B_D` ≤ the slots' B_D and `chunk_tokens`/`delta_slow_c`/`turn_cap_s` = N_chunk/S6/S7, with the S6 ≠ S5 receipt rule. It asserts 1(f) over the three named gated runs, with per-term maxima. My test checks the per-term maxima, the bool/NaN/negative/zero-rate/wrong-cap/duplicate-name refusals, and that `max_fitting_b_d` never names a non-fitting budget.
- See MEDIUM-5 on the decode rate the 1(f) term uses.

**R5-5 (slots under the adopted series mode; full-inventory journals; 600 s recovery). Implemented.**
- The legs precede step-d.
- Each model member after the decision must record the series mode as an observed int. `slots_ac_powermode` must equal `ac_powermode` (kit).
- `InventoryJournal` covers both steps from before the member through the 600 s recovery. `classify_step` refuses an unobserved quiet or recovery. The thermometry bar is required by the kit.
- I agree with the builder that it fits the night. The new costs are described in MEDIUM-1.

**R5-6 (W1 under an adopted High Power, end to end). Implemented, with one gap fixed and one left.**
- Implemented: `prepare` writes plan `ac_powermode` 2; `install` writes the W1 marker and then sets 2 through the narrow rule and reads it back; admission keeps a W1 marker only under expected 2; `run_night` restores at close on every exit path after admission.
- Fixed: a signal inside `enter_high_power` escaped the restore (MEDIUM-3).
- Left: an abandoned launch leaves the host at 2 (MEDIUM-4).

**R5-7 (WP15 sign-offs; launcher). Implemented.**
- S1-S4 carry the key names and the class checks.
- A no-rise t63 is null and censored, and `t_decline_censored` is set.
- `s6_tuning` is a TODO with the median G1/H waits.
- `collection_plan` names member 5 as capture and the others as consume, drops `launcher`, and `--check` refuses other roles.

**R5-8 (WP18 fixtures). Implemented.**
- `scripts/align_v4_wp18_fixtures.py` authenticates the member identity, seed, condition, the per-turn decode counts and any recorded token ids, then writes both fixtures and the four leaves atomically. `--check` writes nothing.
- `require_w1_ready` calls `validate_wp18_fixtures`.
- See LOW-4 (Sol F6) on what the kit then re-checks.

**R5-9 (Sol fixes). Implemented.**
- Implemented: F2 (nested-name digest), F3 (the step-d result bound to its complete custody digest), `Segment.close` under BaseException (heaters, inventory, every session, then the journals), the `require_sizing` provenance and the `hf_pins` byte receipt. Each has a test.
- The close test fails without the BaseException widening, as the integration report says.
- See LOW-3 (Sol F1) for a separate, older hole in the *normal* per-session close.

**R5-10 (LOWs). Implemented.** Every listed LOW has code and a test:
- the watchdog teardown;
- the diskutil retry;
- the null t63;
- the bool t_decline;
- A-infinite/B-finite read as not adopted;
- the configured leg bound;
- the soak window by time;
- fallback step 4 not admitting;
- the finally-signal path.

I re-ran the finally-signal path with real signals (harness A, slow-restore row). The LOWs left are listed with reasons in `LEAD-RULINGS-2.md`, and I agree with them.

**Did anything else change measurement semantics?** No change goes beyond the rulings, as far as I can find. The incidental changes are:
- the post-D cooldown's one-sided band (R5-1's G0 band);
- the step members' 300 s quiet and post-G0 deadman (R5-5/R5-2);
- the step-d recovery is now a fixed 600 s observation rather than "until recovered" (R5-5).

Each follows from a ruling, and the contract doc states each.

## Findings

### MEDIUM

**MEDIUM-1: step-d and the R + 0 °C start state each follow a full D turn with only their own 600 s G0, and a G0 timeout there still refuses the whole R1 night.**
- R5-5 moved the A-B-A legs before step-d. `phase_plan` now runs `high_power_A2` (one full 10k-prefill, 4,096-token D turn) straight into `step_D_prefill_10k_decode_4096` with no cooldown. In round 4 step-d followed the 600 s `cooldown_after_30b`.
- R5-2's warmest-first order puts R + 0 straight after the R + 2 planning turn (the heater is clamped at 0 when hot).
- In both cases a G0 timeout is fatal:
  - step-d's G0 timeout gives `episode.g0_unreleased`, which `incomplete_member_reasons` rejects (exit 3);
  - a planning G0 timeout raises `designed start state not reached`;
  - the driver does not redo heavy segments on a timeout, so R1 refuses: at step-d after roughly 2-3 h of the night,
    at R + 0 after roughly 6-8 h (my reading of the phase caps, not a measured schedule).
- Illustrative estimate, not a measurement: S_slow cools as R + E·e^(−t/τ), with τ ≈ 300 s (the S4 class bound), δ_slow ≈ 1 °C and a D-turn rise of about 4 °C.
  - step-d after A2: about 300·ln(4.5/1) ≈ 450 s of the 600 s cap, before model load and warmup are subtracted;
  - R + 0 after R + 2: about 300·ln(6/1) ≈ 540 s;
  - warmest-first is still better than coldest-first, whose worst G0 was about 620 s.
- Ruling 1's own premise is that a D-after-D G0 takes 300-600 s. The gated runs got a precool for exactly this reason (R5-1). The A-B-A legs got a release segment, and R5-3 made their G0 timeouts INCONCLUSIVE.
- Recommendation (lead): give step-d and the R + 0 state (or all three states) the same `idle-until-soak` precool the gated runs have. This costs at most 1,500 s each, and on the estimate above about 450-550 s each. Alternatively, make those G0 timeouts INCONCLUSIVE for their downstream verdicts (slots cannot be inconclusive, so for step-d the precool is the only real option).

**MEDIUM-2 (design, lead): with cool-to-band precools, the duty bar's G0 still does not test W1's D-after-D G0.**
- I agree with the builder's design point. The precool ends at S_slow ≤ R + δ_slow, so the gated run's G0 only sheds the warmup's own heat. W1's D members after a D member get the fixed 300 s idle, not a cool-to-band.
- The bar now tests G1/H against the right reference (the R5-1 gain). But its G0 share is still close to uninformative for ruling 1's CRITICAL concern, which is what R5-1's stated reason wanted to test.
- If the bar should reproduce W1, a fixed 300 s idle before each gated run (with the soak R kept) is the exact W1 case. A G0 timeout would then count against the run, as it would in W1.
- Otherwise, record in protocol v4 that the W1 D-after-D G0 is predicted from the ruling 1(c) recovery curve (`cooldown_after_D`), not from the bar.

**MEDIUM-3 (fixed in `ad9288196`; Sol critic F4): a first signal inside the W1 High Power entry left the host at 2.**
- `install` called `powermode.enter_high_power` before the `try` whose `except BaseException` restores Automatic, and `high` was still `None` there.
- A SIGINT after `sudo pmset -c powermode 2` returned (for example, during the read-back) escaped with the host at 2 and the W1 marker in place.
- The fix moves the entry inside the `try` and restores whenever the entry was attempted.
- Test: `W1HighPowerTests.test_a_signal_inside_the_high_power_entry_still_restores_automatic` (fails on `d1639a0b3`: `2 != 0`).

**MEDIUM-4: an abandoned W1 launch leaves the host in High Power.**
- `install` sets 2 when it arms, and `run_night` registers the close restore only after admission.
- For a HAZARD_PACK plan (W1's class), the J4 branch returns `EXIT_REFUSED` before admission when `night/launch_abandoned.json` exists (`run_night.py:4104`). The host then stays at 2, and the W1 marker sits in that session's measurement view, which later sessions do not see.
- If launchd never fires at all, nothing restores either.
- This fails closed: the next night that expects 0 refuses on the mode. But the night is lost unless someone runs `sudo -n pmset -c powermode 0`.
- I reproduced it as a `NightDriverTests` case (plan `ac_powermode` 2, host 2, W1 marker, `_existing_record` pinned to the J4 marker): after `run_night` the host was still at 2. The patch is at `/private/tmp/jwr5-tmp/exec-review/abandoned_test.patch`; it is not committed because it fails on this head.
- I did not fix it in `run_night`. A late launchd fire of a released plan can coincide with a retried W1 night that is measuring under High Power, and a restore there would change the mode mid-measurement.
- Recommendation: the magistrate watchdog's J4 release (which knows that no driver ran, and runs before any retry is armed) restores Automatic for a plan that declares 2. The retry's own `install` re-enters High Power.

**MEDIUM-5 (design, lead): ruling 1(f)'s decode term uses step-d's fresh-context decode rate.**
- `ruling_1f_fit` charges `(B_D + turn_cap) / r_decode`, with `r_decode` from step-d: one 4,096-token decode after a 10k prefill, from a quiet start.
- Gated D episodes decode their later turns at longer contexts and after heat soak, both of which are slower. So the 1(f) "worst case" is optimistic in its largest term.
- The builder already expects 1(f) to bind at about 11 tok/s, so a slower rate makes that more likely, not less.
- Recommendation: record decode tokens per gated run (`deadman.phases_s.decode` already gives the seconds), and use the minimum of step-d's rate and the gated runs' observed rates.

### LOW

1. **(Fixed in `ad9288196`.)** `gated_budget` accepted `T_dead: "1200"`, because `float("1200")` succeeds and only bools were excluded. It now requires a JSON number. Covered by `BudgetTests.test_no_non_evidence_b_d_reaches_a_gated_run`. The step-d slots are always floats, so this was not reachable from a real step-d.
2. **(Sol F2.)** In `k_step(leg=True)` the INCONCLUSIVE return for an unreleased G0 comes before `incomplete_member_reasons`. A leg that also failed (for example `telemetry_failed`, `thermal.custody_invalid`) becomes INCONCLUSIVE instead of refusing. The outcome is the conservative one (no adoption, Automatic), and the reasons are kept in `incomplete_reasons`. But it is wider than the builder's stated scope ("any other incomplete leg still exits 3"). Fix: return INCONCLUSIVE only when the incomplete reasons are a subset of the unreleased-G0 flags.
3. **(Sol F1, rated HIGH by Sol; I rate it LOW.)** This is older code, from `f1864e314`, not round 5. `Segment.close_session` removes the session from `open_sessions` before it closes it. A first TERM that lands inside the powermetrics adapter's stop, after it clears its process reference and before it terminates the process, leaves no handle for `Segment.close` to retry. The runtime then exits 143 and cancels its watchdog, and powermetrics may keep running. The window is a few bytecodes inside one stop call on a night that is already aborting. Fix: block TERM/INT/HUP (`pthread_sigmask`) around each session close, or close before removing and make the adapter's stop idempotent.
4. **(Sol F6.)** `validate_wp18_fixtures` checks the schema, arm, run id, `max_turns`, the list length and the sha256 against `inputs.json`, but not the turn contents. A fixture of `[{}] * max_turns` whose digest is also written into the inputs passes. The fixtures come from the authenticating script, so this needs a wrong commit, not a bad measurement. Fix: re-check that each turn has `turn` = its index and non-empty int `prompt_token_ids`/`output_token_ids`, and that `sources` holds two digests.
5. **(Sol F3.)** The kit trusts `duty_bar.pass`. It does not re-derive it from the per-run `duty_bar.verdict` rows that `ruling_1f_fit` already requires by name. A hand-edited `r1_slots` with an inconclusive row and `pass: true` is admitted. The driver writes it consistently. Fix: require `duty_bar.verdict` = FAIL > INCONCLUSIVE > PASS over the rows, and `pass` = (verdict = pass).
6. A first signal after `r1_slots.json` is written but before `run` returns records `status: aborted` (and exit 4) beside a complete registration. The kit reads only `r1_slots`. The magistrate should treat `r1_result.status` as the authority for committing it. Alternatively, write the registration after the terminal record.

### Sol critic F5

F5 is the planning batch-window bound. It is the same finding as my ruling 8 bound fix: the bound was 2,700 s against caps of 900 + 600 + 1,580 = 3,080 s, and Sol's fake-clock admission at 10:59 ended at 11:47. It is fixed in `ad9288196`.
- Steps: 1,800 + 600 G0 + 300 quiet + 600 recovery = 3,300 s.
- Designed states: 1,800 + 900 + 600 = 3,300 s.
- The amended test asserts that each bound covers the runtime's own caps around the re-armed deadman (600 + 300 + 1.13544 × 1,580 + 600 for the steps; 900 + 600 + 1.13544 × 1,580 for the states).
- The 1,800 s base predates round 5 and does not itself include I_D; a larger bound only waits longer.

## For the lead

- Rule on MEDIUM-1 (precool step-d and the R + 0 state, about 450-550 s each on the estimate) and MEDIUM-2 (a 300 s idle or cool-to-band before the gated runs). Both change the R1 schedule, so they are protocol calls.
- MEDIUM-4 belongs in the magistrate watchdog's J4 release. MEDIUM-5 is a 1(f) input change in the driver and the kit. LOW-2 to LOW-6 are small and can ride with any of them.
- The builder's open items in the integration report still stand: the unbound classification digest, the inventory sweep duration on hardware, changed-pick S7, `cooldown_after_30b`, the S6 receipt shape and the SIGKILL marker case. Nothing in this review closes or contradicts them.
- `/code-review ultra` candidate for Ed on this lane: `lane/2026-11-06-v4-r1-integrated` (driver, runtime and kit).
