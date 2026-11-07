# Cold final pass: ALIGN v4 R1 round-7 integrated head (2026-11-07)

**Verdict: no BLOCKER, no HIGH. One MEDIUM, four LOW.**

On this head:
- nothing admits a night on a host whose AC powermode differs from the plan's;
- nothing restores the mode under a process that holds the host night lock;
- nothing admits a gated run, X-G, cell or bundle that R6-1, R6-2, R7-2, R7-12 or R7-13 says to exclude;
- no v3 kit bytes change.

The findings:
- **MEDIUM-1.** A TERM or HUP to `run_night` *while the chain runs* does not run the restore R7-4 promises. `run_night` exits, the chain keeps measuring with no supervisor and no window deadline, and the host stays in High Power. It returns to Automatic only after the chain ends by itself and a later session start or admission runs. This is no regression: before R7-4, TERM killed `run_night` outright with the same outcome for the chain. But R7-4's real-signal tests cover only a signal before the chain exists, and the docs say the close restores.
- **The LOWs:**
  - an interrupt or exception during a `--dry-arm` restores an armed W1 session's High Power, which the round-6 executing review recorded as "no mode change";
  - R7-12's "does not refuse on that alone" is nominal at realistic decode rates, by arithmetic;
  - R1 reports its thermometry bar as `pass` when the two picks are aliases, which the kit then refuses;
  - two LEAD-RULINGS-2 claims say protocol v4 was updated when only the contract doc was.

I changed no code.

Reviewer: Opus 5.5, cold, with no context beyond the documents below.

Target: `lane/2026-11-06-v4-r1-integrated@915f59446` versus `origin/lane/2026-11-05-align-pilot10-benign@e1a91226e`, which is an ancestor of the target. I focused on the round-7 delta `97714c644..915f59446`:
- the science merge `035624383`;
- the infra merge `9ad3a7d56`;
- the pilot10-benign merge `bed96a99d`;
- the test fix `9541b9dbd`;
- the doc commit.

I also read the admission, close, install and dead-man code that delta relies on.

Documents read:
- the "Round 7 integration" and "Open after round 6" sections of `docs/run_reports/2026-11-06-align-v4-r1-integration.md`;
- the Round 6 and Round 7 sections of `docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md`;
- `LEAD-RULINGS-1.md`;
- `CHAIR.md` ruling 1;
- `docs/align/r1_runtime_contract.md` in full (order, G0 timeout, G0_cap_W1, gated runs, calibration segments, host-level marker and lock, non-measuring exits);
- the R1 and G0 passages of `docs/align/pilot_protocol_v4.md` (:95-140, :230-260, :340-370, :655-670);
- `docs/align/reviews/2026-11-07-r1-round6-cold-pass.md`;
- `docs/align/reviews/2026-11-07-r1-round6-executing-review.md`.

Code read:
- **Line by line, every round-7 hunk of:**
  - `joulewise/align/apple/powermode.py`: `HostLock.acquire`/`release`/`retake`/`pass_fds`, `host_state_dir`, `restore_owed`;
  - `scripts/run_night.py`: `run_night`, `_run_night` up to the hazard branch, `_take_host_lock`, `_admit_ac_powermode`, `_restore_owed_on_exit`, `_close_ac_powermode`, `_own_high_power_marker`, `_install_termination_handlers`, the chain spawn in `_run_chain_once_impl`, `dead_man`;
  - `scripts/align_v4_session.py`: `install`, `_require_night_job_absent`, `_termination_handlers`;
  - `scripts/align_r1_rehearsal.py`: `PowerModeGuard`, `_run`, `segment_bounds`, `runtime_g0_timeout_s`, `night_worst_case_s`, `w1_g0_cap`, `g0_wait_record`, the gated block and X-G in `run`, the teardown;
  - `joulewise/align/apple/r1_runtime.py`: `close_managed_session`, `classify_step`, `alias_groups`, `g0_timeout_s`, `g0_wait_fields`, `Segment.g0_cap_s` and every `gate_policy` call;
  - `joulewise/align/apple/thermal_gates.py`: `validate_gate_policy`, the G0 wait loop;
  - `scripts/align_v4_kit.py`: `check_r1_evidence` aliases, `r1_g0_timeout_s`, `w1_g0_cap`, `ruling_1f_fit`, `check_r1_budget_and_policy`, `gate_policy_fields`, `thermal_policy`;
  - `scripts/magistrate_watchdog.py` `_restore_abandoned_high_power`;
  - `configs/gates/hazard_refusals.json`, `night_gate.py`, `arm_retry.py`;
  - `scripts/validate_align_v4_w1_plan.py`, `night_plan.template.json`.
- **Also:**
  - `joulewise/b5/driver.py`: `run_hazard_night`, the chain call through `rt._run_chain_once`, `dry_arm`, `run_bounded`, `Seams.popen`;
  - `bytes_h_session.install` (its launchd census);
  - `workload.py`: the G0 stop;
  - the R1 zsh chain (unchanged in round 7).

Nothing restricted was opened, no weights were loaded and nothing touched the measurement Mac. Every run used `nice -n 19 taskpolicy -b /private/tmp/jwsol/venv-both/bin/python -B` with `TMPDIR` under `/private/tmp/jwr7-tmp/cold`, one module per process, in a worktree under `jw-wt/`. The only exceptions are two timing reruns without `taskpolicy -b`, noted in the table. Every test and probe pointed `JOULEWISE_HOST_STATE_DIR` at a temporary directory. The probes are scratch files outside the repo and are not committed.

## What I executed

| Check | Result |
|---|---|
| `tests.align.test_r1_round7_science` | Ran 16, OK |
| `tests.align.test_r1_round7_power` | Ran 29, OK |
| `tests.align.test_r1_round7_install` | Ran 6, OK |
| `tests.align.test_r1_round7_close_deferral` | Ran 3, OK (skipped=1, the child-only helper class) |
| `tests.align.test_v4_kit` | Ran 114, OK |
| `tests.align.test_r1_rehearsal` | Ran 73, OK |
| `tests.align.test_r1_round5_exec_review` | Ran 7, OK (the `9541b9dbd` read-back expectation) |
| `tests.align.test_r1_round6_power` | Ran 25, OK |
| `tests.align.test_v4_w1_plan` | Ran 12, OK |
| `tests.align.test_r1_runtime_contract` | Ran 11, OK |
| `tests.test_magistrate_watchdog` | Ran 158, OK |
| `tests.hazards.test_refusal_allowlist` | Ran 23, OK (skipped=1) |
| `tests.test_run_night` (whole module; the integration did not rerun it) | Ran 318, FAILED (failures=17), all in the environment classes round 6 recorded:<br>8 `NightDriverTests` installer tests ("test interpreter must load the battery fixture in child Pythons");<br>8 `BindSupervisionProcessTests`;<br>1 `QuietDriverIntegrationTests.test_supervised_worker_is_reaped_on_cancellation`.<br>Without `taskpolicy -b`, `BindSupervisionProcessTests` gives Ran 22, OK and the quiet test gives Ran 1, OK. Every powermode, marker, lock and R7 test in the module passes. |
| **Probe W** (in-process): `night_worst_case_s(None)`, `r1_g0_timeout_s()`, `d_turn_cap_tokens()` | no_redo 46,886.99 s; one batch wait 52,286.99; R6-2 retries 21,600; all 73,886.99; `g0_timeout_s` 1,200. These match LEAD-RULINGS-2 R7-2 and R7-9. The D turn cap is 4,096 tokens. |
| **Probe M** (`NightDriverTests` fixture, plan 2, own W1 marker). The chain is a real child that inherited the lock fd and keeps running; the first in-window census raises `KeyboardInterrupt`, which is what the R7-4 handler raises on TERM. | `run_night` re-raises `KeyboardInterrupt('signal 15')`. The chain is **still alive**, and `_terminate_process_group` is **never called**. The host stays at **mode 2** with the marker. The log has `ac powermode close deferred`, and there is no `night/result.json` (MEDIUM-1). |
| **Probe D** (same fixture, plan 2, own W1 marker, host at 2). `run_night(..., dry_arm=True)`; a `KeyboardInterrupt` lands in the dry-arm branch after the plan parse, standing in for an operator's Ctrl-C or any exception there. | **`restore` runs; the host goes to 0 and the marker is removed** (LOW-1). |
| `git diff --stat origin/lane/2026-11-05-align-pilot10-benign HEAD -- smc_enumeration.py ssd_qualification.py test_smc_quiet.py tests/hazards/test_smc_enumeration.py configs/campaigns/align_pilot_v3` | empty |
| `origin/lane/2026-11-06-v4-r1-integrated` re-fetched before commit | still `915f59446` |

## Findings

### MEDIUM

**MEDIUM-1 (b, e): a TERM or HUP while the chain runs leaves High Power on, with the chain running unsupervised past its window.**

- **Where:**
  - `scripts/run_night.py:4205-4229`: the R7-4 handler raises `KeyboardInterrupt` wherever the main thread is, including the chain wait loop.
  - `:1171-1320`: that loop has no `try`/`finally` that stops the chain on an exception. Only the census abort (`:1249`), the supervision stop (`:1301`), the start refusal (`:1128`) and the deadline (`:907`) call `_terminate_process_group`.
  - `:873`: the window deadline thread is a daemon, so it dies with `run_night`.
  - `:4108-4123`: the close then cannot retake the lock, because the chain inherited it (R7-5), so it defers.
  - `:4929-4965`: the dead-man refuses while the chain group is alive, and returns before its restore.
  - The HAZARD_PACK path is the same. `b5/driver.py:2615-2623` catches `Exception`, not `KeyboardInterrupt`, so the hazard monitor and meter are orphaned too.
- **Probe M:** after the interrupt the chain is alive, nothing terminates it, the mode stays 2 with the marker, and the log says `close deferred`.
- **Consequence:**
  - The chain measures on at High Power with no census aborts and no wall-clock stop at `t0 + window_max_s + grace`.
  - The host returns to Automatic only once the chain ends by itself and a later session start or night admission runs. Until then the dead-man refuses `chain_alive`, and every restore defers to the lock.
  - Nothing is admitted: there is no terminal `result.json`, and the dead-man writes `chain_alive`.
  - A later plan-2 night refuses on the lock, and a plan-0 night restores only once the lock is free. So it fails closed, but it can cost the next window and leave the Mac at 2 for hours.
- **Relation to the rulings:**
  - R7-5 makes the deferral correct: no restore runs while the chain holds the lock.
  - But R7-4 says TERM and HUP "run their normal close (High Power restore included)". The contract (`r1_runtime_contract.md:124`, item 4) and LEAD-RULINGS-2 R7-4 repeat this.
  - That is true only before the chain is spawned or after it exits. The R7-4 tests (`test_r1_round7_power.py:309-364`, and the install tests) park the signal inside `Popen`, before any chain exists.
  - This is the case the round-6 executing review raised with MEDIUM-3 (F3): "prove the chain group gone before the close restores, or keep the marker and the lock until it is". R7-5 took the second option, which leaves the chain running.
- **Not a regression:** on `97714c644` a TERM killed `run_night` at once (Python's default), with the same outcome for the chain and the deadline thread. A SIGINT always behaved this way.
- **Fix (a lead call):**
  - **Option A.** On an interrupt after launch, run the deadline's own termination proof (`_terminate_process_group`, then `chain.exited` or `chain.unkilled`) before the closers run. The close's retake then succeeds and restores.
  - **Option B.** Document mid-window TERM/HUP as "close deferred to the next session start, chain unsupervised". Correct the R7-4 wording in the contract and LEAD-RULINGS-2 to match.

### LOW

**LOW-1 (b, e): an interrupt or exception during `run_night --dry-arm` restores an armed W1 session's High Power.**

- **Where:** `scripts/run_night.py:4246-4260`. The R7-11 / Sol F3 branch runs whenever `"plan_path" not in stage`. The dry-arm branch returns (`:4314-4322`) before `stage.update` (`:4325`), so any exception or Ctrl-C inside it lands in the "before the plan parse" branch. So does one in its initial agent census. That branch calls `_restore_owed_on_exit` for the marker this plan owns.
- **Probe D:** host 2 with an armed session's own marker; a `KeyboardInterrupt` in the dry-arm branch; `restore` runs, the host goes to 0 and the marker is removed.
- **Why it matters:**
  - The round-6 executing review recorded `--dry-arm` as "no mode change (a desk control; restoring would undo an armed session)" (`2026-11-07-r1-round6-executing-review.md:165`).
  - The malformed-plan dry-arm branch (`:4302-4304`) still returns before its restore, so it keeps that invariant.
  - A dry-arm of a W1 plan after its install is a natural desk check. A Ctrl-C during it, or an `OSError` under the custody root, would make that night refuse at admission (expected 2, observed 0). It fails closed, but the night is lost.
- **Fix:** record `stage["dry_arm"] = True` (or test `dry_arm`) and skip the restore in both pre-admission branches.

**LOW-2 (d), for the lead: R7-12's "does not refuse on that alone" holds only on paper.**

- An INCONCLUSIVE X-G sets G0_cap_W1, and with it ruling 1(f)'s G0 term, to 1,200 s. The integration note under R7-12 says so.
- The largest T_dead L1 allows is 1,750 / 1.13544 = 1,541.2 s (I_D = 0).
- That leaves at most 341 s for (B_D + 4,096) / r_decode plus holds, prefill and tool.
- So 1(f) needs r_decode ≥ 15.0 tok/s even at the smallest B_D the kit accepts (1,024), with zero holds, prefill and I_D. It needs about 30 tok/s at the 6,144 floor the builder names.
- At the roughly 20 tok/s the builder expects, an INCONCLUSIVE X-G therefore refuses W1 through 1(f).
- `test_inconclusive_x_g_falls_back_and_is_admitted_when_1f_fits` admits only because it sets 80 tok/s (`test_v4_kit.py:952`).
- If the lead meant X-G's fallback to touch only W1's D → X transition, this needs a separate X-G cap. Otherwise, record that an INCONCLUSIVE X-G is in practice a W1 refusal pending the ruling 1(e) fallback, which is already open under R7-2.

**LOW-3 (c, e): R1 calls its thermometry bar `pass` when its two picks are aliases; only the kit refuses, after the night.**

- **Where:**
  - `r1_runtime.py:290-298` records `alias_groups`, but `status` stays `pass` whenever both picks are non-null.
  - `align_r1_rehearsal.py:1598` copies that status into `thermometry.bar`.
  - The kit refuses aliased `s_fast`/`s_slow` (`align_v4_kit.py:253-257`), and it also requires the policy sensors to equal R1's picks (R6-8 cold LOW-2).
- **Consequence:** if WP14(a) picks two keys of one alias group, no admissible `thermal_policy` exists. The fix needs the classifier change (PR #692) and an R1 re-run, but the R1 report says `pass`.
- **Fix:** flag `r1.picks_aliased` and set the bar to `fail` at R1, so the magistrate learns it from the R1 night rather than at `require_ready`. Nothing is admitted wrongly; this is about when the failure is reported.

**LOW-4 (e): two LEAD-RULINGS-2 claims about protocol v4 are false.**

- R7-1 says "The contract doc and protocol v4 are updated". R7-3 says "The contract doc and protocol v4 record the confirmations".
- Protocol v4's only round-7 text is the R7-2 G0 paragraph (`pilot_protocol_v4.md:359-365`). It states no gated-block order (its R1 roster at `:660-664` is order-free) and nothing about R7-3.
- The contract doc does carry both (`r1_runtime_contract.md:90`, `:96-97`).
- Correct the two sentences, or add the order and the confirmations to protocol v4.

## Already open, not re-reported

These are listed in "Open after round 7" or in LEAD-RULINGS-2 Round 7, and still hold on this head:
- **R7-2:** the likely 1(f) refusal, the "precool/retry segments" interpretation, and X-G's inability to observe a full 1,200 s G0 inside its 1,086 s deadman;
- **science Sol MEDIUM-1:** the step-d and designed-state batch-window bounds (3,900 s) omit member start-up, so a near-cap step-d can cross 11:45. This is the one open item that bears on data, as an OS-batch confound;
- **R7-13:** the exact-match limits of the alias rule;
- **infra Sol F1:** the R1 runtime's own children do not inherit the lock. A runtime SIGKILLed by the driver's 20 s kill can leave the heater running after the restore. The next night's quiet and contention guards would refuse on it;
- **infra Sol F2:** the 10 s deferral plus the 15 s watchdog fire after the driver's 20 s kill;
- **R7-10:** the partial deviation (the path is not in `receipt.json`/`result.json`);
- **R7-11:** an unopenable lock file needs a manual restore, and exec LOW-3's first half is unchanged;
- the R1 plan `window_max_s` (46,887 / 52,287 / 73,887 s; W1's `window_cap_s` of 44,640 s is below the no-redo case);
- the WP18 F7 check on the Mac;
- exec LOW-3's main-thread scope;
- the round-6 cold observation on R1's D → gated-run start-up gap;
- the three hardware checks carried over from round 5.

## Checked and found sound

- **R7-1:**
  - `phase_plan` runs `planning_turn_R_plus_0C`, `D_bank`, `D_spam a`, `D_spam b`, `X_G_contrast`.
  - `last_d_turn` gives D_bank the planning turn, D_spam a D_bank, D_spam b D_spam a, and X-G D_spam b. Each counts only with a released G0 and decode tokens > 0, so both replay runs follow a full gated D episode.
  - An inconclusive predecessor makes the follower INCONCLUSIVE, and `u5_verdict` then makes U5 inconclusive.
- **R7-2:**
  - **One constant.** It is the runtime config's `g0_timeout_s`.
    - The driver refuses at t0, before power or runtime work, when the value is missing, out of [600, 1,200], or different from the committed config the kit reads (`align_r1_rehearsal.py:1436-1446`).
    - `validate_gate_policy` accepts `g0_cap_s` only in [600, 1,200]. Absent, the G0 cap is 600 (`thermal_gates.py:485`), so v3 and every other G0 are unchanged.
    - `G0_TIMEOUT_KINDS` covers exactly step-d, X-G, the gated kinds and the planning kinds. Step-30b, the A-B-A legs and `g0-release-soak` keep 600.
  - **The driver and kit derivations agree.** I compared `align_r1_rehearsal.w1_g0_cap` and `align_v4_kit.w1_g0_cap` term by term:
    - censored waits count at the timeout, and a measured X-G must have a released G0;
    - `max_g0_s`, the clamp, `value_s` (an int) and the sorted `censored` list are compared field by field;
    - a released G0 that overshoots the cap by up to one poll still clamps to the same `value_s` on both sides;
    - `g0_outcome` takes only the four values `thermal_gates` emits.
  - **W1 arms it.** `inputs.R1.thermal_policy.g0_cap_s` must equal `value_s`. `gate_policy_fields` copies it into every W1 member's thermal policy, and the W1 plan template and validator carry it as `PENDING_R1`. `workload.py`'s G0 stays inside the member deadman, so no member cap grows.
  - **Every G0 wait is recorded.** `g0_waits` includes superseded attempts and the release before each.
- **R7-3:** both `inconclusive_segments` refusals carry the remedy text.
- **R7-4 (install):** the install has no chain, holds the lock and restores in its `except`. Its TERM/HUP path is sound.
- **R7-5:**
  - `release` only closes a descriptor, never `LOCK_UN`, and `retake` reopens and locks without waiting.
  - The lock is passed to the HAZARD_PACK chain too: `rt._run_chain_once` with a claim reaches `_run_chain_once_impl`, which reads `_CHAIN_HOST_LOCK` at call time.
  - The lock is moved off FD 198.
  - The hazard monitor, meter, `run_bounded` and Python grandchildren use `close_fds`, and the rendered b5 chain starts no background jobs. So an orphan that holds the lock is unlikely.
  - The R1 driver's `_run` terminates its child on an interrupt before the guard retakes, which is the step `run_night` lacks (MEDIUM-1).
- **R7-6:** the census runs before the session-start restore and before any `pmset`. It uses the same argv, 10 s budget and exact-absent-line rule as `bytes_h_session.install`. In production, `runner` is `None` and `subprocess.run` captures the output.
- **R7-7:** `PowerModeGuard.restore` reads back after the AUTO, and keeps the markers (so `__exit__` refuses) on anything but 0. The second idempotent attempt in the teardown runs under the retaken lock.
- **R7-10:**
  - All four production `__main__`s mark themselves.
  - Under an override, `host_state_dir()` raises. In `run_night` that becomes an admission refusal for every plan (fail closed), and `_restore_owed_on_exit` traps it.
  - The watchdog's J4 restore catches it.
  - The path is recorded in the admission record and log, the arm record, the session-start record and `r1_result.json`.
- **R7-11:**
  - Only EWOULDBLOCK/EAGAIN counts as another holder.
  - `night_refused_host_lock_error` is registered in `night_gate`, `arm_retry` and the allowlist.
  - An exception between the lock and the close registration restores under the night's lock and frees it.
  - A failed marker write refuses before the chain, and the registered close restores.
- **R7-13:**
  - `alias_groups` reads the inventory journal's real row shape (`values.sensors`) and sits inside the classification digest (`r1_runtime.py:304`).
  - The kit refuses a missing or malformed group list and aliased or identical picks.
- **R7-14:** the R1 chain is unchanged, and no W1 night can hold the single label then.
- **The pilot10-benign merge:** the R0/SMC files are byte-identical to pilot10-benign, and v3 is untouched.

## Claims in the integration report and the reviews

- The round-7 tails for every module I reran match the report: 16 / 29 / 6 / 3 / 114 / 73 / 7 / 25 / 12 / 11.
- The R7-2 and R7-9 worst-case numbers match probe W, and 46,887 − 44,640 = 2,247 s.
- "The rule pilot10-benign wins for R0/SMC code needed no resolution" is true (the diff is empty).
- "`tests.test_run_night` ... not rerun": I reran it. Only the recorded environment classes fail.
- The R7-4 wording in LEAD-RULINGS-2, the contract (:124) and the run report ("the normal close (the Automatic restore) runs") holds only before the chain spawns or after it exits (MEDIUM-1).
- The "protocol v4 updated" claims under R7-1 and R7-3 are false (LOW-4).
- The round-6 executing review's `--dry-arm` row no longer holds (LOW-1).
- Nothing else in the Round 7 rulings record, the integration section or the contract contradicts the code.

## Verdict for the R1 arm item

**R1 can be armed on this head.** No finding touches R1's evidence path. The R1 night runs under plan 0, the driver holds the lock and kills its own child on a signal, and the chain's EXIT trap still restores.

Before a W1 arm under an adopted High Power, the lead should pick an option for MEDIUM-1 (terminate the chain on an interrupt, or document the deferral) and close LOW-1. Each fails closed, but each can cost a W1 night and leave a manual `sudo -n pmset -c powermode 0`.
