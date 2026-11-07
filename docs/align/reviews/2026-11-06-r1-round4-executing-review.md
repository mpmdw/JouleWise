# Executing review: ALIGN v4 R1 round 4 (2026-11-06)

**Verdict: ADMIT_WITH_FIXES.** Two HIGH findings are fixed and pushed in `105de4588`, each with tests that fail on `da78b2367`. There are four MEDIUM and nine LOW findings, and no BLOCKER. On the round-4 head, no exit path leaves the host in High Power where another night would admit it. I confirmed this with real signals on the real zsh chain, the real driver and real runtime subprocesses. Before R1 is armed, the lead must rule on the Fable cold pass HIGH-2 (`c304685d7`): the gated D runs self-capture a warm reference. I confirmed that finding by reading the code, and I did not change it.

- Reviewer: Opus 5.5. This is an executing review, and I did not write any of the code under review.
- Target: `lane/2026-11-06-v4-r1-integrated@da78b2367` against the previously reviewed tip `a2193446d` (92 files, +13,716/−283).
- Fixes: `105de4588`, on top of the Fable cold final pass `c304685d7`, which landed on the lane during this review.
- Documents read:
  - the integration report (round 4 and its integration);
  - the round-3 executing review and Fable cold pass;
  - `CHAIR.md`, `LEAD-RULINGS-1.md` and `docs/align/r1_runtime_contract.md`;
  - after it landed, the round-4 Fable cold pass.
- Code read line by line:
  - `joulewise/align/apple/r1_runtime.py`, `r1_runtime_contract.py` and `powermode.py`;
  - the `external_volume.py` census and arm check;
  - the `scripts/align_r1_rehearsal.py` diff;
  - `scripts/night_chains/align_r1_rehearsal.zsh`;
  - the admission hunks in `run_night.py`, `night_gate.py` and `environment.py`;
  - `scripts/align_v4_session.py`;
  - the kit's `check_r1_evidence`, `require_ready`, `require_w1_ready` and `derive_sizing`;
  - the `workload.py`, `thermal_desk.py` and `stop_precedence.py` diffs;
  - the supporting code: `controller` interrupt salvage, and `ThermalSession.capture_reference` and `wait`.

Nothing restricted was read or touched, no model weights were loaded, and nothing ran on the measurement Mac. Every run used `nice -n 19 taskpolicy -b /private/tmp/jwsol/venv-both/bin/python -B` with a per-module `TMPDIR` under `/private/tmp/jwr4-tmp/r4rev`, one module per process, in the worktree `jw-wt/r1r4-review`.

## What I executed

| Check | Result |
|---|---|
| Whole `tests/align`, one module per process (113 modules) | All 113 modules rc=0, OK: **Ran 1,458 tests**. 65 modules ran at `da78b2367`; the other 48 ran at the fix commit, after the worktree moved, and those 48 do not touch the files the fix changes. `test_cache_checkpoint_probe` failed once (rc=1) in a first pass that I started by mistake with every module at once (load average 75). I stopped that pass, and the module passed alone. Slowest: `test_moe_calibration` 3,959 s, `test_moe_review` 1,437 s, `test_analysis_metadata_baseline` 1,248 s. |
| Affected modules at the fix commit `105de4588` | `test_r1_runtime_contract` 9, `test_r1_rehearsal` 46, `test_r1_runtime` 15 (+3 new), `test_r1_runtime_e2e` 2 (136 s), `test_v4_kit` 66, `test_protocol_v4_doc` 5: all OK |
| `JW_WP22_FULL=1 tests.align.test_v4_w1_synthetic` | Ran 18 tests in 276 s, OK (expected failures=1, F3), at the fix commit |
| The seven `tests.test_run_night.NightDriverTests` power-mode admission tests | Ran 7, OK |
| `tests.test_environment` 34, `tests.test_arm_retry` 36, `tests.test_night_plan_writer` 10 | OK |
| `tests.test_night_gate` | Ran 112, 1 failure. `test_partial_output_timeout_keeps_status_refusal_evidence` returns `''` for partial stdout on a 0.1 s probe timeout under `nice -n 19 taskpolicy -b`. Fable LOW-5 found the same failure on the base, so it comes from this laptop's environment, not the lane (LOW-8). |
| R1 exit-path harness with real signals (below) | 6 scenarios, all as expected |
| Adversarial probes of my own (below) | 2 HIGH reproduced and fixed; 3 LOW observations |

### R1 exit-path harness: real zsh chain, driver and runtime, real signals

The scratch harness is at `/private/tmp/jwr4-tmp/r4rev/harness/` and is not committed. Each scenario starts `scripts/night_chains/align_r1_rehearsal.zsh` as a session leader, as `run_night` does (`start_new_session=True`). The chain runs the real driver. The driver takes the runtime argv from an inputs file (`--runtime-entrypoint`) and runs the real `scripts/align_r1_runtime.py` as subprocesses on the synthetic backend.

Only `sudo` is faked: a PATH shim writes the requested mode to a state file. The driver's `pmset -g custom` query is faked by repointing `PowerModeGuard.QUERY` at a script that prints the state file, because this Air's AC block has no `powermode` key. The ruling 20 censuses use the real `/sbin/mount` and `diskutil info -plist`, which are read-only.

Signals go to the process group, as `run_night` sends them: `killpg` TERM, a 30 s wait, then `killpg` KILL.

| Scenario | Signal point | Exit / teardown | Host mode | Marker | `r1_result` | Runtime custody | Group left |
|---|---|---|---|---|---|---|---|
| A | TERM during the idle soak (sensor segment) | 130 / 3.4 s | 0 | absent | aborted | `idle_soak`: aborted, signal 15 | none |
| B | TERM inside the `step_30b` member | 130 / 6.5 s | 0 | absent | aborted | `step_30b`: aborted, 15; bundle finalized (`summary_metrics.json`, thermal journal ends `session_end`) | none |
| C | TERM, TERM, INT, HUP 0.3 s apart inside step-d | 130 / 6.2 s | 0 | absent | aborted | step-d: aborted, 15 | none |
| D | `kill -KILL 0` from inside `sudo pmset -c powermode 2` (the B leg) | −9 | **2** | **present** | none | earlier segments complete | none |
| E | TERM inside the High Power B leg | 130 / 4.5 s | 0 | removed | aborted | `high_power_B`: aborted, 15 | none |
| F | none (complete run, fix commit) | 0 | 0 | removed | complete; 23 ruling 20 censuses PASS (real `mount`/`diskutil` on this Air); A-B-A `not_adopted`; synthetic U5 `fail`, duty bar fails on X7 (as the integration report says) | every segment complete | none |

After D, `run_night._admit_ac_powermode` ran against the same host state (fake sudo, state-file pmset):

| Plan and host | Admission |
|---|---|
| Plan 0, marker present, restore fails | Refused ("restore failed (exit 1)"); marker kept, mode 2 |
| Plan 2, marker present | Restored to 0, then refused ("0 != expected 2"); marker removed |
| Plan 0, marker present | Restored, re-read 0, admitted; marker removed |
| Plan 0, host at 2, no marker | Refused ("2 != expected 0") |

So a host left in High Power by a SIGKILL or a power loss is never admitted by a night that expects Automatic. It is admitted by a plan that declares 2 only if there is no marker; with the marker present, that plan is refused (fail closed).

### Adversarial probes (my own)

1. **A planning turn whose G0 never releases.** In the synthetic world the PM state was forced non-Nominal for the member, so G0 could only time out.
   - On `da78b2367` the runtime exited 0 with `g0_outcome: timeout`, `energy_j: 0` (the `g0_unreleased` stop leaves no turn) and `g0_release_c: 40.29` against R = 38.0 and δ = 1.0. That is inside R + 2 ± δ, so `planning_temperature_summary` accepts the point, and β_T and U5 are fitted on a zero-energy point.
   - This is HIGH-1. It is now `IncompleteMemberTests.test_planning_turn_with_an_unreleased_g0_fails_the_segment`.
2. **A planning turn cut by the deadman after G0 released.** I used `step.deadman_s = 110`; the synthetic G0 takes about 76 s, because the deadman is armed at G0 entry and pays for the preheat and the G0 wait.
   - On `da78b2367` the runtime exited 0 with the partial turn's energy. This is the Fable HIGH-1 path, and it is now a test as well.
   - The step kinds already refused this case through `status != succeeded` (probe: `member_status:failed`, `episode.deadman:0`). The planning kind had no check at all.
3. **A replay-pair run with an unreleased G0.**
   - Its `energy_j` is 0. With the other run at 9,000 J, σ_pair = 9,000 J, and `u5_verdict` returned **pass** for a 5 J bound. This is HIGH-2.
4. **Host and census edges.**
   - One transient `diskutil info` failure inside an otherwise internal-only census refuses R1 at the next segment (LOW-3).
   - A marker that is a directory makes `admit_ac_powermode` raise, and `run_night` turns that into a refusal record (correct).
   - A restore that "succeeds" (sudo exit 0) while the mode stays 2 removes the marker before the read-back; admission still refuses (LOW-4).

## Findings

### HIGH (fixed in `105de4588`)

**HIGH-1: the runtime returned incomplete planning-turn members, so a zero or partial energy entered β_T and decided U5.** This overlaps the round-4 Fable HIGH-1; the fix covers both.
- `r1_runtime.py` `k_planning` checked neither the G0 outcome nor the member's completeness.
- After round 4's `episode.g0_unreleased` stop (cold MEDIUM-2), a designed start state whose G0 timed out returns:
  - no turn;
  - `energy_j = turn_owned_j = 0`;
  - as `g0_release_c`, the G0 row's `release` field, which on a timeout is only the last sample (`thermal_gates.py`, `values = release or latest`).
- The contract defines `g0_release_c` as "the S_slow **measured** at release", so this was also a dishonest contract field.
- A deadman-cut turn returned a partial energy. That is likely on hardware: the 1,580 s step deadman also pays for the preheat (up to 900 s) and the G0 wait (up to 600 s).
- **Fix:**
  - `k_planning` fails the segment (exit 3) unless the G0 released.
  - A new `incomplete_member_reasons` requires exactly one turn, status `succeeded` and none of `INCOMPLETE_MEMBER_FLAGS` (deadman, decode budget, `g0_unreleased`, time guard, context limit, endpoint or episode error, G0/G1/H timeouts, state unobserved, collector failed, custody invalid, status source missing).
  - The same rule applies to the planning kinds, `step-30b`, `step-d`, `d-4bit` and the A-B-A legs.
  - Malformed or refused tool-call flags do not cut the decode and are not counted; the synthetic D stream sets `episode.malformed_tool_call:0` on the step task.
  - The gated D runs and X-G are exempt, because their truncation is the duty-bar evidence.
  - The contract doc states the rule.
- **Tests:** `tests/align/test_r1_runtime.py` `IncompleteMemberTests` (unreleased G0; deadman-cut turn after a released G0; the helper's flag rules). All three fail on `da78b2367`: 2 failures (exit 0 ≠ 3) and 1 error.

**HIGH-2: a turnless replay run made U5 a false PASS.**
- `u5_verdict` takes σ_pair = max(|E_a − E_b|, 2.97 J) from the two spam/benign replay runs and never looks at whether they ran.
- A replay run whose G0 did not release ends with no turn and `energy_j = 0`, so σ_pair becomes the other run's whole energy (thousands of J) and the bar cannot fail. That is a PASS on the R1-blocking U5 item (ruling 6 / L2), and the kit admits it.
- The duty bar does catch the same run (`admitted_turns` < 3), but a lead fallback step lets W1 proceed with the false U5 PASS on the record.
- **Fix:**
  - When either replay run has `admitted_turns == 0`, the verdict is INCONCLUSIVE, with `sigma_pair_valid: false` and the reason.
  - INCONCLUSIVE rather than a refusal keeps the rest of the R1 record and the ruling 1(e) fallback path.
  - The contract doc states it.
- **Test:** the replay-pair case in `test_r1_rehearsal.test_u5_is_declared_with_c_equal_one_and_evaluated`. It fails on `da78b2367` (the verdict is `pass`).

### MEDIUM

**MEDIUM-1: an A-B-A leg whose own G0 does not release refuses the whole R1 instead of taking ruling 16's INCONCLUSIVE path.**
- Ruling 16 (contract: "If any accepted leg's release timed out (`released: false`), adoption is INCONCLUSIVE") keys on the separate `g0-release-soak`.
- Each leg is also a step member with its own G0 against the soak R (`step_member` → `reference_hook`).
- After a timed-out release the host is still warm, so the leg's G0 will usually time out as well. Since round 4 that leg has no turn and exits 3. On `da78b2367` the message was "step member has no turn"; with `105de4588` it is the completeness reason. The driver then refuses R1 at the last phase, after about 10 h, and writes no registration.
- This is fail-closed and was already true before my fix, but the INCONCLUSIVE outcome the ruling asks for is effectively unreachable.
- Lead call: either do not gate the leg's own G0, because the release precedes it, or map a leg-level G0 timeout to `released: false` and INCONCLUSIVE.

**MEDIUM-2: the kit binds I_D, T_dead, the tail and the power mode to `r1_slots`, but not B_D or the thermal policy.** This partly overlaps Fable MEDIUM-2.
- `check_r1_evidence` and `require_ready` check `inputs.R1.B_D` only for range and `thermal_policy` only for shape (heavy, per-turn).
- Nothing requires B_D ≤ `r1_slots.slots.B_D` (A1's fit rule only lowers it), or the policy's `chunk_tokens` = `N_chunk`, `delta_slow_c` = S5/S6 and `turn_cap_s` = S7.
- A transcription slip in the four hand-filled R1 leaves is therefore admitted. S6 is still the lead's to tune after the gated runs, so an equality check on S6 is a lead decision. The other three are mechanical.

**MEDIUM-3: W1 under an adopted High Power has no end-to-end path.**
- If A-B-A adopts, the kit freezes `ac_powermode 2`, and the v4 arm requires the host at 2.
- No code sets the host to High Power for W1. No installer writes `ac_powermode: 2` into the W1 night plan: `NightPlan.ac_powermode` is set by no writer, so `run_night` expects 0.
- The result is that every W1 night refuses (`night_refused_ac_powermode`). A stale R1 marker would also restore 0 under a plan that declares 2, and that night refuses too (harness D).
- All of this is fail-closed, and it blocks W1 only if B is adopted.

**MEDIUM-4: the planning-turn deadman pays for the preheat, so designed start states are likely to be cut, and now refuse R1.**
- The deadman is armed at G0 entry (`workload.py`). The designed state preheats inside the wrapped G0 for up to 900 s, then waits up to 600 s for the G0, all against a 1,580 s `deadman_s`. That leaves less than one 4,096-token decode, which takes about 370 s (FD:145, as the Fable pass cites).
- With HIGH-1 fixed this ends in an exit-3 refusal of R1 instead of a bad β_T point. That is the right side to fail on, but it costs a night.
- Either arm the step deadman after the preheat, or size `deadman_s` for preheat + G0 + step. This joins Fable MEDIUM-3, which reports the coldest-first ordering right after the hottest member.

### LOW

1. **The runtime's 15 s watchdog skips the terminal record.**
   - The contract says `runtime_custody.json` "is written last on every exit path". The `os._exit` watchdog, which fires if salvage takes more than 15 s, writes none, and skips any unfinished controller salvage, including the stop of a root-owned `powermetrics` that a non-root `killpg` cannot signal (round-3 cold pass).
   - State the exception in the contract. The `run_night` runbook should check for a surviving `powermetrics` after such an abort.
2. **A signal inside the runtime's own `finally`.**
   - After a completed segment, a first TERM during `segment.close()` is recorded as a teardown error and the result is still printed with exit 0.
   - During `write_custody` it leaves no custody record.
   - This is a narrow window, and the driver discards the result on its own stop path either way.
3. **Ruling 20 census fragility and coverage.**
   - One failed `diskutil info` on an internal volume (a transient refusal) refuses R1 at the next segment. A single retry, as `pmset` has, would avoid losing a night.
   - The census runs only at segment boundaries, so a volume mounted and unmounted inside a segment is not seen.
   - The ruling text names `diskutil list external`; the code uses `mount` plus `diskutil info` per mount. That is adequate for "mounted", but it does not see an attached disk that is not mounted.
4. **The marker is removed before the restore is verified.** `PowerModeGuard.restore` and `admit_ac_powermode` unlink the marker on `sudo` exit 0 without reading back 0. Admission still refuses (it re-reads), but the durable evidence that a restore was owed is gone. The next night refuses on the mode alone.
5. **The load journal measures something other than "per second".**
   - macOS `ps -o pcpu` is a decaying average over up to about a minute, not a per-second load, so the 60 s sustained > 0.5-core rule runs on a smoothed series.
   - System processes that respond to the measured GPU work (`kernel_task`, `WindowServer`) count as background, which risks redo loops on heavy segments.
   - This needs a hardware check on the measurement Mac. The contract should say what the series is.
6. **I_D does not include member process start-up.** It is the runtime's `run_benchmark` wall minus the episode from G0 entry, so it excludes the interpreter start and imports of a W1 member process. L1's 10 s margin absorbs this only if it is small. Compare it once on hardware against a runner-measured W1 member wall.
7. **A refused XML call (lead decision (b)) ends the D episode as a natural stop.** It produces no tool calls, so the turn loop breaks. `primary_stop` does not name it, and it is visible only in the new `tool_call_flags` table. The decision is consistent with ruling 2(d) (visibility, not exclusion). The stop table could still name it.
8. **`tests.test_night_gate` timing test.** `test_partial_output_timeout_keeps_status_refusal_evidence` fails on this laptop under `taskpolicy -b` (environment). The same as Fable LOW-5.
9. **`step_response` with no rise.** It reports `t63_s = 0.0` with a `no_rise` flag, so `slot_detail.classification.s_fast_t63_le_5s` reads true. Make it null or censored.

## Focus items

- **Does the WP15 runtime measure through the production collectors and custody?** Yes, by reading and execution.
  - Model segments run `run_benchmark` with `ThermalRegistry` (SMC sidecar, G0/G1/H, PM status), the episode deadman, the powermetrics adapter, the bundle writer and the ruling 7 powermode reader.
  - Sensor segments run `ThermalSession`.
  - Read-back uses `read_episode_bundle`, `read_bundle_record`, `native_pm_samples` and `attribute_episode`.
  - The synthetic backend replaces only the transports.
  - Two weaknesses remain. HIGH-1 (fixed): read-back did not check completeness. Fable HIGH-2 (open): the gated runs self-capture a warm reference (`k_gated_d` and `k_x_g` run with no reference hook while `gate_policy` installs `role: capture`).
- **TERM handling.**
  - Driver: TERM → 20 s → KILL. Runtime: one-shot `SystemExit`, controller salvage, 15 s watchdog, terminal record.
  - Chain: further signals ignored, restore on signal and at EXIT.
  - Harness A-C and E: teardown 3.4-6.5 s, well inside `run_night`'s 30 s; nothing left in the group; custody records "aborted, 15"; the bundle is finalized.
- **Contract fields correct and honest.** Correct at the seam, except:
  - `g0_release_c` on a timeout (fixed);
  - σ_pair from a turnless run (fixed);
  - LOW-1 (the watchdog exit path) and LOW-5 (`cpu_busy_cores` semantics), which should be disclosed.
  - The driver checks the gated runs' armed T_dead, journal completeness and L1 as claimed.
- **Host-level power-mode admission.**
  - It applies to every plan class, before any branch.
  - It uses the exact AC `powermode` key, one read retry, the marker restore through the narrow sudo rule, and a re-read.
  - A failed restore keeps the marker and refuses (harness D).
  - No path admits a host left in High Power under a plan that expects 0. The only gap is MEDIUM-3 (adopted High Power for W1), which fails closed.
- **External-volume refusal.** It is pinned to status `off` and checked at t0, before every runtime invocation (releases and redos included) and before registration. The terminal census is recorded. The v4 arm refuses and records. LOW-3 covers fragility and coverage.
- **The kit's `r1_slots` binding.**
  - Bound: source, I_D, the A-B-A verdict to the power mode, the tail, U5 with c = 1.0, passing censuses, and the duty bar or a recorded fallback.
  - Not bound: B_D and the thermal policy (MEDIUM-2).
  - I agree with Fable LOW-1 that fallback step 4 ("D screen-only") should not admit W1.
- **W1 blockers.**
  - `install` requires `--w1-disk-config` and runs `w1_disk_gate` after the arm checks.
  - `sizing_b5.json` is derived only from a validated R1-filled `w1_plan.json`.
  - `require_w1_ready` validates WP11 D identity against the HF LFS pins. The kit tests (66) pass.
  - An empty `offloads` list passes the disk gate. That is per the runbook ("configured" offloads), so the pilots 8-10 receipts are an operator duty, as the integration report says.
- **Lead decisions on `malformed_tool_call`.**
  - (a) The JSON-path flag is `episode.malformed_tool_call.json:`. It matches none of the exclusion or stop prefixes (`calibration_exclusions`, `episode_ineligibility_reasons`, `primary_stop`, the workload's `incomplete`) and is tabulated.
  - (b) `episode.unsupported_tool_call_format:` on the XML path is tabulated and not excluded.
  - Both are as recorded in protocol v4. The flag was introduced in v4 (WP8 F1, `6d288fc3f`), so (a) restores pilots 4-10 behaviour. See LOW-7 for the stop classification.

## For the R1 arm item

Admit with `105de4588`. Before R1 is armed:
- the lead rules on Fable HIGH-2 (warm self-captured reference in the gated runs);
- the lead rules on MEDIUM-4 (planning deadman vs. preheat; it now fails closed) together with Fable MEDIUM-3 (ordering).

MEDIUM-1 should be decided before R1, because it decides whether a hot A-B-A leg costs the whole night. MEDIUM-2 and MEDIUM-3 are W1 items. The LOWs are cleanups or disclosures.
