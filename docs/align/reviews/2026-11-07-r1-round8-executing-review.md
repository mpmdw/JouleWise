# Executing review: ALIGN v4 R1 round 8 (2026-11-07)

**Verdict: ADMIT_WITH_FIXES.** I found no BLOCKER and no HIGH, so I committed no code fix. R8-1 does what it says, and real signals prove it:

- **INT, TERM or HUP while the chain runs.** `run_night` terminates the chain's whole process group, proves it gone and records `chain.exited`. The close then retakes the lock, restores Automatic and clears the marker.
- **INT, TERM or HUP while the runtime runs.** The R1 driver ends the runtime and every descendant it recorded, proves them gone, and only then restores.
- **An unproven termination** restores nothing on either path.
- **A second, third or tenth signal** does not cut the termination or the close short.
- **A process of the night that left the group but holds the lock** sees no restore.
- **The R8-1 code changes no measurement semantics.** Phase order, the gates, the G0 caps and the kit derivations are untouched. R8-4's batch-window bounds feed only the wait before a quiet segment.
- **R8-4's arithmetic** checks out to the last digit.

Two MEDIUM findings are left for the lead. Neither can admit bad data, and neither is on the ALIGN W1 or R1 path as wired today.

- **MEDIUM-1 (new this round, from the Sol latch fix).** `_qualification_observe` catches `BaseException`. It runs the TRANSACTION_PACK s1 HID observation inside the chain loop. A first signal that lands there is swallowed, and since `3d507c8fe` it also latches `closing`, so every later TERM/HUP/INT is swallowed too. Signals then cannot stop that night; only its window deadline can. Before this round only the first signal was lost.
- **MEDIUM-2 (pre-existing, made visible by the Sol fix).** Sol's fix 1 defers the close when an *interrupt's* chain termination is unproven. A census-abort, supervision-stop or window-deadline termination that is unproven still restores whenever the lock can be retaken. That puts a restore under exactly the survivor the fix names: one that does not hold the lock.

Each MEDIUM is pinned by an `expectedFailure` test that fails for the stated reason (checked with the decorator removed). Flip the test when the finding is fixed.

## Scope

- **Reviewer:** Opus 5.5, executing review. I did not write any of the code under review.
- **Target:** `lane/2026-11-06-v4-r1-integrated@a13d6fc99` against `72c7c8a50`, 12 files, +1,258/−59:
  - `191455724`: code and tests;
  - `543c9565d`: docs;
  - `3d507c8fe`: the Sol critique fixes;
  - `a13d6fc99`: the integration report.
- **Read:**
  - the Round 8 section of `LEAD-RULINGS-2.md` (rulings verbatim);
  - `docs/align/r1_runtime_contract.md`;
  - the round-8 section of `docs/run_reports/2026-11-06-align-v4-r1-integration.md`;
  - the full code diff of `scripts/run_night.py`, `scripts/align_r1_rehearsal.py` and `joulewise/align/apple/r1_runtime.py`;
  - the allowlist entry;
  - the code those changes call: `_terminate_process_group`, `_prove_group_absent`, `_WindowDeadline`, `_run_chain_once_impl`, `_close_ac_powermode`, the b5 driver's call into `_run_chain_once`, `PowerModeGuard.restore`, the driver's `stop` handler and teardown, and `scripts/night_chains/align_r1_rehearsal.zsh`.
- **Environment:**
  - worktree `jw-wt/r8rev` (removed at the end);
  - `/private/tmp/jwsol/venv-both/bin/python -B -m unittest`, one module per process, at most two at once, under `nice -n 19 taskpolicy -b`, with `TMPDIR=/private/tmp/jwr8rev-tmp`;
  - fake sudo and pmset only, and no model weights.

## R8-1 against the questions asked

| Question | Answer | Evidence |
|---|---|---|
| A signal while `run_night`'s chain runs ends the whole group, proves it gone, then restores and clears the markers | **Yes** | `test_r1_round8.NightInterruptTests` (TERM, HUP, and INT on a TERM-ignoring chain and member); my `NightRepeatedSignalTests`. The chain and member are checked from inside `run_night`'s own process. `chain.exited` is written, no `chain.unkilled`, the log shows `"proven": true`, mode 0, marker gone. |
| The same for the R1 driver and runtime | **Yes** | `R1InterruptTests`; my `R1RepeatedSignalTests`: a runtime that *ignores* TERM, with a heater that ignores TERM and holds the runtime's pipes. The driver KILLs the runtime after its grace (`returncode -9`), records the heater as a descendant and KILLs it. The proof is `proven: true`, `survivors: {}`, no `pipes_held_open`. Both pids are gone at every restore call, and the mode reads 0. |
| An unprovable termination never restores (interrupt path) | **Yes** | `run_night`: `_CHAIN_INTERRUPT_UNPROVEN` is set from the outcome, including a deadline that already fired unproven. The close checks it *before* the retake, frees the lock and returns (`NightUnprovenCloseTests`). R1: `PowerModeGuard.restore` refuses when any `_CHILD_TERMINATIONS` entry is unproven, and the teardown's second attempt is skipped on `deferred` (`test_an_unproven_descendant_defers_the_restore`). The non-interrupt paths do *not* have this rule: MEDIUM-2. |
| A second signal cannot cut the close short | **Yes, with one hole (MEDIUM-1)** | `run_night`: the handler latches `closing` before it raises, SIGINT is routed through the same handler, and `_stop_chain_on_interrupt` also calls `closing()`. R1: the `stop` handler sets SIG_IGN on all three signals. My two storm tests send nine more signals during the termination; the termination ran exactly once and the close completed. The hole is a first signal swallowed by a `BaseException` catch on the main thread (MEDIUM-1). |
| No measuring night can see a restore | **Yes for any night whose data can be admitted** | The close restores only after a retake on a fresh descriptor (R7-5), and then only if the interrupt's termination was proven (R8-1). A concurrent measuring night would hold the lock. My `NightLockHoldingEscapeeTests` covers a member that leaves the chain's group (`start_new_session`) but keeps the lock: the group proof passes, the retake fails, the close defers, and the mode stays 2. Survivors of the *aborted* night that hold no lock can still see a restore: MEDIUM-2 (non-interrupt paths), LOW-1 (the R1 chain trap) and LOW-4 (group-escaping samplers). That night's data is never admitted. |
| Hang fix | **Holds** | `_terminate` no longer calls an unbounded `communicate()`. It polls `communicate(timeout ≤ 1 s)` through the grace (re-reading the tree), bounds the reap after a KILL at 30 s, ends the tree, then drains with a 5 s bound and closes the pipes. `TerminateTreeTests` and my stubborn-runtime test, where an orphan holds the pipe, both return promptly. The normal (no-signal) `_run` path still has an unbounded `communicate()`: LOW-3. |
| Nothing else changed measurement semantics | **Confirmed** | No diff in `scripts/align_v4_kit.py`, `configs/campaigns/`, `scripts/night_chains/`, `thermal_gates.py` or `smc_enumeration.py`; `phase_plan` is unchanged. `segment_bounds`/`release_segment_bound_s` feed only `wait_outside_os_batch` (`_segment`, the `bound` local). R8-6 changes only `thermometry.bar`/`flags`/`bar_reason`, never the classification or its digest. R8-3 moves only when the watchdog starts. R8-5 removes a restore from the dry-arm exception path (dry-arm returns before any lock). `align_v4_kit.py --check` is blocked on the same nine leaves as rounds 4 to 7. |

### R8-4 worst-case arithmetic (recomputed by hand)

- **Re-armed member:** 1,750 + 1.13544 × 1,580 + 120 = 1,750 + 1,793.9952 + 120 = **3,663.9952 s**.
- **Step-d:** 3,663.9952 + 1,200 + 300 + 600 = **5,763.9952 s**.
- **Each designed state:** 3,663.9952 + 900 + 1,200 = **5,763.9952 s**.
- **A-B-A leg:** 665 + 1,750 + 1,793.9952 + 120 = 4,328.9952 s (unchanged; `aba_leg_bound_s` now spells the 665 s as `release_segment_bound_s()`).
- **No redo:** 46,886.99 + 4 × (5,763.9952 − 3,900) = 46,886.99 + 7,455.98 = **54,342.97 s**.
- **With one batch-window wait:** + 5,400 s = 59,742.97 s.
- **R6-2 retries:** 4 × (1,500 + 5,763.9952) = **29,055.98 s**.
- **Every retry plus one wait:** 54,342.97 + 29,055.98 + 5,400 = **88,798.95 s**.
- **W1 cap:** 54,342.97 − 44,640 = 9,702.97 s.

Every figure in the ruling, the contract and the tests agrees. Step-30b keeps 3,300 s; see LOW-2.

## Findings

### MEDIUM-1: a signal swallowed on the main thread now disables every later signal

- **Where:** `scripts/run_night.py`, `_install_termination_handlers.handler` (the latch from `3d507c8fe`), together with `_qualification_observe` (`except BaseException: … return None`).
- **Path:** `_qualification_observe` runs on the main thread inside the chain loop, as the s1 HID observation (`_s1_observation_enabled`: TRANSACTION_PACK with `V5_QUALIFICATION_OCCURRENCE` s1/s2). It also runs after the chain, as the G2B lifecycle observation.
- **What happens:** a first TERM/HUP/INT that lands inside it raises `KeyboardInterrupt`, which is swallowed as an "observation failure". The latch has already set `closing`, so every later signal is swallowed as well. The chain is neither stopped nor supervised by a signal any more; it runs on to its window deadline.
- **Before this round:** the first signal was lost, but the next one worked.
- **Not on the ALIGN W1 or R1 path:** neither is a TRANSACTION_PACK plan. It is shared Block-5 code.
- **Reproduced:** `test_r1_round8_exec_review.SwallowedSignalLatchTests` (`expectedFailure`; it fails with "KeyboardInterrupt not raised").
- **Suggested fix:** in `_qualification_observe`, record the fault and re-raise `KeyboardInterrupt` and `SystemExit`. An interrupt is not an observation failure. With that change the latch is correct as it stands.

### MEDIUM-2: an unproven non-interrupt termination still restores when the lock can be retaken

- **Where:** `scripts/run_night.py`, `_close_ac_powermode`; `_CHAIN_INTERRUPT_UNPROVEN` is set only in `_run_chain_once`'s `except KeyboardInterrupt`.
- **The other unproven paths:** when `_run_chain_once` *returns* `termination_proven=False` (a census abort, a supervision stop, a fired window deadline, or the launcher-refusal path), `_run_night` refuses the night and withholds the courier.
- **What happens:** the close then retakes the lock and, if it can, restores. Members do not hold the lock (R8-2). So a member that survived the group KILL (in uninterruptible I/O, for example) sees Automatic restored under it. That is the case Sol's fix 1 was written to prevent, but the fix covers only the interrupt path.
- **No data consequence:** the night is REFUSED, and its data is never admitted.
- **Reproduced:** `NightUnprovenNonInterruptCloseTests` (`expectedFailure`; it fails with `'restore' unexpectedly found in ['read', 'restore', 'read']` after `chain.unkilled` was written).
- **Suggested fix:** set the flag from `_run_night` whenever `termination_proven` is False, and rename it `_CHAIN_TERMINATION_UNPROVEN`. The close already defers on it.

### LOW-1: under the production chain, the R1 chain's trap restores after a deferred driver close

`scripts/night_chains/align_r1_rehearsal.zsh` has `trap 'restore_automatic' EXIT` and `on_signal` → `restore_automatic`. Neither checks the lock or a proof, and `set -e` makes any non-zero driver exit reach the EXIT trap.

zsh runs the signal trap only after its foreground child exits; I checked this on this host, where the trap ran 4 s later, when `sleep 4` ended. So the order is: run_night's `killpg` TERM → the driver's proof and close (deferred if unproven) → the chain's `pmset 0` anyway. R8-1's "the guard restores nothing" is true for the guard, but not for the R1 night as run.

R7-14 accepted this trap for the W1-overlap question, and the R1 run's data is never admitted on an interrupt. Record it beside R7-14: R8-1's R1 deferral protects only against the driver's own restore.

### LOW-2: step-30b keeps the round-5 bound under the same underbound argument

The builder flagged this. Step-30b's deadman is also re-armed after its G0 and quiet, so the argument of R8-4 applies to it. The cost of an underbound is small, because a segment that overlaps the OS batch window is caught by `os_load_verdict` and redone. Even so, the lead should either extend R8-4 to step-30b or say why not.

### LOW-3: the normal `_run` path still has an unbounded `communicate()`

If a runtime exits normally and leaves an orphan holding its stdout, the driver blocks until the orphan ends. A signal breaks the block: `_terminate` then finds the pipes held, the proof fails, and the restore defers. This is pre-existing and fails safe. A bounded drain plus `_stop_tree` on the normal path would close it.

### LOW-4: the group proof covers the chain's process group only, not every process of the night

The contract says that on an interrupt R8-1 "terminates those processes and proves them gone". That is exact for processes in the chain's group, which includes every `run_campaign` member, because members are started without a new session.

It is not exact for any process in a member's tree that starts its own session. The repository has such spawns (`smc_enumeration.py:393`, `flags/collect.py:1344`, `sampler_teardown`'s setpgid). If such a process holds no lock it is outside the proof, the R8-2 class, and its night is aborted.

Tighten the wording to "the chain's process group", or have the census follow sessions. My escapee test shows that the lock still protects such a process when it does hold the lock.

### LOW-5: worst-case R1 driver teardown versus `run_night`'s group termination

The contract says the driver "waits at most 20 s (inside run_night's 30 s)". Under `run_night` the zsh leader stays alive (its trap waits for the driver), so `run_night`'s `wait(30)` applies. The driver's worst case is now:

- 20 s of grace;
- the KILL, then `_stop_tree`: up to 2 × 5 s plus `ps` calls of up to 5 s each;
- a 5 s drain;
- the sudo restore.

With a runtime that ignores TERM *and* a descendant that ignores TERM, that can pass 30 + 5 s. The group KILL then cuts the driver's restore and `r1_result.json`, and the markers stay for the next admission. It fails safe.

With the WP15 runtime the case is unlikely: its watchdog exits by 19 s, and its descendants already received `run_night`'s group TERM. State the bound in the contract, or cap `_stop_tree` so that the total stays under 30 s.

## Adversarial tests (`tests/align/test_r1_round8_exec_review.py`)

| Test | Kind | Result |
|---|---|---|
| `NightRepeatedSignalTests.test_signals_during_the_termination_do_not_cut_it_short` | Real TERM, then 9 × HUP/INT/TERM at 0.4 s spacing while a TERM-ignoring chain and member are being terminated | pass: one `KeyboardInterrupt: signal 15`, one termination line, proven, restored, both gone |
| `NightLockHoldingEscapeeTests.test_an_escapee_that_holds_the_lock_sees_no_restore` | Real TERM; a member in its own session that keeps the lock FD | pass: group proven, retake fails, `close deferred`, mode 2 and marker kept, escapee alive |
| `R1RepeatedSignalTests.test_signals_during_the_runtime_kill_do_not_cut_the_close_short` | Real TERM then 9 × INT/HUP/TERM; the runtime ignores TERM, and its heater ignores TERM and holds the pipes | pass: runtime KILLed after a 2 s grace, heater recorded and killed, proven, both gone at every restore, mode 0 |
| `SwallowedSignalLatchTests` (MEDIUM-1) | Real signals | expected failure |
| `NightUnprovenNonInterruptCloseTests` (MEDIUM-2) | Census abort with an unproven group | expected failure |

## Test runs (this head, `a13d6fc99`, plus my test module)

```
tests.align.test_r1_round8_exec_review     Ran 5 tests in 36.089s    OK (expected failures=2)
tests.align.test_r1_round8                 Ran 21 tests in 27.044s   OK
tests.align.test_r1_round7_science         Ran 16 tests in 0.292s    OK
tests.align.test_r1_round6_power           Ran 25 tests in 0.479s    OK
tests.align.test_r1_round7_power           Ran 29 tests in 5.970s    OK
tests.align.test_r1_round7_close_deferral  Ran 3 tests in 2.928s     OK (skipped=1)
tests.align.test_r1_rehearsal              Ran 73 tests in 8.044s    OK
tests.align.test_r1_runtime                Ran 33 tests in 80.900s   OK
tests.align.test_r1_runtime_e2e            Ran 2 tests in 73.364s    OK
tests.align.test_r1_runtime_contract       Ran 11 tests in 0.002s    OK
tests.align.test_r1_round7_exec_review     Ran 6 tests in 0.651s     OK
tests.align.test_r1_round7_install         Ran 6 tests in 2.285s     OK
tests.align.test_r1_round6_lows            Ran 18 tests in 4.489s    OK
tests.align.test_r1_round5_exec_review     Ran 7 tests in 4.720s     OK
tests.align.test_r1_round6_exec_review     Ran 9 tests in 1.245s     OK
tests.align.test_v4_w1_plan                Ran 12 tests in 1.277s    OK
tests.align.test_v4_kit                    Ran 114 tests in 11.676s  OK
tests.align.test_protocol_v4_doc           Ran 5 tests in 0.491s     OK
tests.hazards.test_refusal_allowlist       Ran 23 tests in 30.467s   OK (skipped=1)
tests.test_run_night -k close -k signal -k interrupt -k termination -k powermode -k dry_arm
                                           Ran 16 tests in 12.150s   FAILED (failures=1) under taskpolicy -b:
                                           the bind_supervision timing fixture (1.078 s > 1.05 s budget), the
                                           known environment class; rerun under nice only: Ran 16 tests in 6.778s OK
```

## Recommendation

- **Admit round 8.** R8-1's requirement before any W1 arm under High Power is met.
- **Fix MEDIUM-1 and MEDIUM-2** in the next round. Each is a few lines, and each comes with its pinned test.
- **Record LOW-1, LOW-4 and LOW-5 in the contract.**
- **Rule on LOW-2.**
