# ALIGN v4 R1 round 5: infrastructure rulings (lane/2026-11-06-v4-r1-round5-infra)

Date: 2026-11-06. Base: `lane/2026-11-06-v4-r1-integrated@54e844b87`. This is code, kit and test work only. It authorizes no measurement, opens no model weights and changes no v3 kit bytes.

Scope: lead rulings R5-4, R5-6, R5-8, R5-9 and R5-10. R5-1, R5-2, R5-3, R5-5 and R5-7 belong to the parallel science lane, so this lane leaves the runtime's phase ordering alone. The integrator records the rulings verbatim in `LEAD-RULINGS-2.md`.

Finding IDs:
- "exec" is `docs/align/reviews/2026-11-06-r1-round4-executing-review.md`.
- "cold" is `docs/align/reviews/2026-11-06-r1-round4-fable-cold-pass.md`.
- "round-3 exec" is `docs/align/reviews/2026-11-06-r1-integration-executing-review.md`.

## What changed

**R5-4 (a gated D run is never unbudgeted; the kit binds the budget).**
- Runtime: `r1_runtime.gated_budget` refuses (exit 2, before any model work) in three cases:
  - a step-d `B_D` that is not a multiple of 1,024 in [1024, 40960], including the 0 that step-d produces when it floors a small budget;
  - a step-d `B_D` that is not an integer;
  - a `T_dead` that is non-finite, not positive or a bool.

  Previously such a run had no decode cap.
- Driver: `_check_step_d` runs right after step-d, so the night stops there, before the cooldown, X-G and the gated runs, which saves Mac time. It applies the same `B_D` rule and requires every slot to be finite.
- Kit: `check_r1_evidence` → `check_r1_budget_and_policy` requires:
  - `inputs.R1.B_D` ≤ `r1_slots.slots.B_D`, because the fit rule only lowers it;
  - `thermal_policy.chunk_tokens` = `N_chunk`;
  - `delta_slow_c` = `S6`, where `S6` must equal `S5` unless r1_slots records a lead `s6_tuning`;
  - `turn_cap_s` = `S7`;
  - ruling 1(f), checked by `ruling_1f_fit`:

        max G0 + max (G1 + H) + max (prefill + tool)   [over the gated D runs, r1_slots.deadman_budget]
        + (B_D + turn_cap_tokens) / r_decode            [r1_slots.budget_fit_inputs]
        <= inputs.R1.T_dead

  A turn is admitted while fewer than B_D decode tokens have been spent, and it keeps its full per-turn cap (FD:263). So B_D + cap bounds the episode's decode. The driver now records `budget_fit_inputs`: step-d's measured `r_decode_tok_per_s`, and the per-turn cap the gated runs armed (`turn_cap_tokens`, a new gated-run field). When the check refuses, the message names the largest fitting B_D (`max_fitting_b_d`, the lead's sizing aid).

**R5-6 (W1 under an adopted High Power).**
1. `align_v4_session.py prepare` passes the frozen series value (`collection_plan` `runtime_requirements.ac_powermode`, which comes from r1_slots) to the shared prepare. The b5 window plan writer accepts an optional `ac_powermode` input (0 or 2) and writes it into the HAZARD_PACK night plan.
2. Under 2, `install` writes the High Power marker under the session's measurement root and then runs `sudo -n /usr/bin/pmset -c powermode 2` (`powermode.enter_high_power`; this is the existing narrow rule). It reads the mode back and runs the arm admission against 2. If the arm then refuses for any reason, it restores Automatic (`powermode.restore_automatic`, which reads the mode back before it removes the marker) and records `staging/v4-arm-NNN.restore.json`.
3. `admit_ac_powermode`: when the plan expects 2, the marker is that night's own restore obligation. It is kept, and no restore runs. When the plan expects 0, nothing changes: the marker restores, then the mode is re-read. A host at 2 is never admitted under a plan of 0.
4. `run_night` is now a wrapper around `_run_night`. A night admitted under a declared 2 restores Automatic when it closes, on every exit path, and logs `ac powermode close`. The marker is removed only after the read-back is 0, so a failed restore stays owed to the next night.

**R5-8 (WP18 fixtures, a hard W1 prerequisite).**
- `scripts/align_v4_wp18_fixtures.py` was drafted by local Sol and reviewed here. It reads exactly three operator-named files: the b-e25 and b-e18 `outputs/align_turns.jsonl`, and `p7-PILOT.json`.
- Before writing anything, it validates:
  - the identity: run id, seed index, episode seed, pair and condition, with the member not excluded;
  - the per-turn decode counts;
  - the summary token ids, when present.
- It then writes `configs/campaigns/align_v4/registration/wp18_{x,y}_token_ids.json` (canonical JSON, schema `joulewise.align_v4.wp18_token_fixture.v1`) and the four `inputs.WP18` leaves. `--check` re-derives everything and writes nothing.
- The kit's `require_w1_ready` now calls `validate_wp18_fixtures`. That check requires both files, their sha256, their arm and run id, and `max_turns` equal to the inputs.

**R5-9 (Sol fixes, as triaged).**

| Fix | Source | What it does |
|---|---|---|
| F2 | `sol/burn-wp15rev@657c3ad29` | `write_custody` excludes only DIR's own record and temporaries, not a nested file of the same name. |
| F3 | `sol/burn-wp15rev@657c3ad29` | `Segment.step_d_result` requires that the result bytes are the ones the step-d runtime's own complete `runtime_custody.json` digested. |
| `Segment.close` | triage note | Catches BaseException per session, keeps closing the rest (the powermetrics stop included) and still stops the journals. |
| `require_sizing` provenance | `sol/burn-w1rev@8ce7042ab` | `sizing_b5.json` must name the committed `w1_plan.json` bytes. |
| `hf_pins` receipt | `sol/burn-w1rev@8ce7042ab` | The receipt is bound to the pin file's bytes, in `require_w1_ready` and in `prequal.check_kit`. |

- Two parts of the Sol branches were not taken:
  - The `ManagedSession` rewrite (Sol F1) was left out because the triage rated it overstated.
  - The cosmetic R0 message was left out.
- The disk-gate test hygiene (`disk_path` in the temp dir) was taken.
- The kit was regenerated. `plan_tree.json` and `identity_pins.json` changed only because the generator's sha changed.

**R5-10 (LOWs).**

| LOW | Fix |
|---|---|
| exec LOW-1 | On the 15 s watchdog path, `Termination.expire` runs `on_timeout` first. `main` sets that to `watchdog_teardown`: it sends TERM to every `powermetrics` process in the runtime's own process tree (the `sudo` child relays it), then writes `runtime_custody.json` with `status: aborted` and `watchdog: true`. It digests files only until a 1.5 s deadline and lists the rest as unhashed. It then forces the exit. It skips the write if the normal record was already written. |
| exec LOW-3 | `external_volume.census` retries one failed `diskutil info` per mount, and records `diskutil_failures`. |
| exec LOW-9 | With no rise, `t63_s` is null with `t63_censored`. The classification is null. S2 is null, so the driver refuses at step-d (the thermometry bar fails). |
| round-4 | `t_decline_s: true` (any bool or non-number) refuses. |
| round-4 | "A legs infinite, B finite" is now `not_adopted`. |
| round-3 exec LOW-1 | The A-B-A leg's batch-window wait bound comes from the configured values (`aba_leg_bound_s`): 65 s pre-roll + 600 s G0 cap + step-d I_D + 1.13544 × the runtime config's `step.deadman_s` + 120 s. That is 2,680 s with I_D 101.5 s, against the old assumed 2,400 s. |
| cold LOW-2 | `soak_detrended` takes the reads in the last 1,200 **seconds**, using the new `sensor_series_t_s` contract field, and fits the slope against time. The soak must span ≥ 1,200 s, with ≥ 0.9 reads per second in the window. |
| cold LOW-1 | `DUTY_FALLBACK_STEPS = (1, 2, 3)`. Step 4 ("D screen-only") never admits W1. |
| cold LOW-4 | In the driver's `finally`, signals are ignored before the restore, as they are after a first signal, so the sudo child inherits SIG_IGN. The restore is wrapped, so `r1_result.json` is always written. |

`docs/align/r1_runtime_contract.md` states every one of these.

## Local Sol critique (`99a90e9c6`) and what changed

Local Sol 6.1 xhigh reviewed the first commit adversarially. It ran six modules (206 tests, OK). Its events were audited: no restricted path was accessed; the only hits were `rg` searches for those strings in repo test files. Its findings and their dispositions, fixed in `367bc0b42`:

| Sol finding | Disposition |
|---|---|
| HIGH: install can leave High Power (a failure before the protected span; a re-install of a terminal session) | Fixed. The whole span from the mode change to the handoff restores on any failure. A terminal session is refused before any mode change, and an installed one is not set again. |
| HIGH: ruling 1(f) accepts a subset of gated runs or negative phases | Fixed. Exactly the three named gated runs are required, with finite, non-negative phases. |
| HIGH: the fit's turn cap is unbound | Fixed. It must equal the W1 D members' cap (anchor 1's `max_tokens`, 4,096). |
| HIGH: a soak whose sensor stops reading early passes on an earlier window | Fixed. The window ends at the soak's own end (`sensor_series_end_t_s`, a new contract field). |
| HIGH: watchdog and normal custody writes race | Fixed. The terminal record has one owner. |
| MEDIUM: the watchdog's hashing is not bounded inside a file | Fixed. The deadline is checked per 1 MiB block, and an independent 4 s hard exit backs it up. |
| MEDIUM: an R1 crash marker is taken as the W1 marker | Fixed. W1 markers carry their own text. Admission and install restore any other marker first. |
| MEDIUM: an interrupt in the close masks the night's exit | Fixed. The close catches BaseException, and the night's own result stands. |
| MEDIUM: stale pid identity | Fixed. A second snapshot must show the same parent and command before TERM. |
| MEDIUM: `s6_tuning: {}` authorizes any S6 | Fixed. A receipt {authority, from_c = S5, to_c = S6} is required, with S6 ≤ 2.0 °C. |
| LOW: three tests not discriminating | The close-failure test now asserts the launch and the exit code. The finally-signal test was already tightened in `002ee41ba`. A per-block deadline test was added. |

Every one of these fixes was neutralized on its own as above, and its test fails without it. A full rerun of the round-5 harness at `367bc0b42` again fails every original case without its fix, with two exceptions:
- three anchors that `367bc0b42` rewrote (the S6 receipt, the marker ownership, the install span), which the Sol-fix cases above cover;
- the 1(f) input-validity check, whose test now also feeds a zero and a NaN decode rate. It fails without the check.

## LOWs left, with reasons

| LOW | Reason left |
|---|---|
| exec LOW-2 (a signal in the runtime's own `finally`) | R5-9 makes the teardown complete. A completed segment whose first signal lands in teardown still returns its result, with `teardown_errors`. The driver is stopping in that case anyway. The custody-write window is a few ms. |
| exec LOW-4 (marker removed before the restore is verified) | Only in `PowerModeGuard.restore` and `admit_ac_powermode`. Admission re-reads and refuses on a mismatch, so no wrong admission results. The new `restore_automatic` (R5-6) does verify before unlinking. |
| exec LOW-5 (`ps pcpu` is a decaying average) and LOW-6 (I_D excludes process start-up) | Both need a hardware comparison on the measurement Mac. They are disclosed in the contract. |
| exec LOW-7 (a refused XML call is not named in `primary_stop`) | This is a stop-classification change outside R1 infrastructure. The `tool_call_flags` table shows the call. |
| exec LOW-8 and cold LOW-5 (`test_night_gate` timing on this laptop) | Environment, not code. |
| exec LOW-3, second half (census only at segment boundaries; unmounted attached disks) | The ruling text is "mounted". A per-second census would add host load inside quiet segments. |
| cold LOW-3 (admission runs in `rehearse` mode) | Harmless: it reaches the right end state. |
| cold LOW-6 (journal sampling overhead) | A print-beside-energies item for the R1 report. |
| cold LOW-7 (launcher) | R5-7, science lane. |
| round-3 exec LOW-2, second half (`recovery_curve` rows not shape-checked) | The check sits in the run loop that the science lane is restructuring (R5-1/R5-2). Leave it to that merge. |

## Fail-without-fix

Each fix was neutralized on its own, one hunk at a time, in a scratch worktree at `99a90e9c6`, and its tests were run (`/private/tmp/jwr5-tmp/neutral/harness.py`). Every listed test fails without its fix and passes with it.

| Fix | Test(s) |
|---|---|
| R5-4 runtime B_D/T_dead refusal | `test_r1_runtime.Round5Tests.test_gated_d_never_runs_unbudgeted` |
| R5-4 driver step-d check | `test_r1_rehearsal.test_step_d_without_an_admissible_budget_refuses_before_any_gated_run`, `test_step_d_with_a_null_slot_refuses_right_after_step_d` |
| R5-4 kit B_D ≤ slots, slots B_D admissible, policy binding, S6 tuning, ruling 1(f), 1(f) inputs | `test_v4_kit.R1BudgetBindingTests` (6 tests) |
| R5-6 admission keeps the marker under 2 | `W1HighPowerTests.test_admission_keeps_the_marker_only_when_the_plan_declares_two`, `test_adopted_high_power_is_set_with_the_marker_and_the_arm_admits`, `test_run_night.test_declared_high_power_keeps_the_marker_and_restores_automatic_at_close` |
| R5-6 run_night close restore | `test_run_night.test_declared_high_power_keeps_the_marker_and_restores_automatic_at_close` |
| R5-6 install sets 2 / restores on refusal / prepare declares the mode | `W1HighPowerTests` (3 tests) |
| R5-6 plan writer carries `ac_powermode` | `test_b5_plan.test_declared_ac_powermode_is_carried_into_the_night_plan` |
| R5-8 W1 readiness needs the fixtures; fixture arm and turns | `WP18FixtureBindingTests` (2 tests) |
| R5-9 F2, F3, `Segment.close` | `Round5Tests` (3 tests) |
| R5-9 hf_pins bytes; `require_w1_ready` reads the bytes; sizing provenance | `WP11IdentityTests` (2 tests), `W1SizingTests.test_require_sizing_needs_the_plan_then_the_derived_file` |
| LOW-1 (`expire` runs the teardown; `main` arms it) | `Round5Tests` (2 tests) |
| LOW-3, LOW-9, bool t_decline, A∞/B finite, leg bound, soak by seconds (2 tests), fallback step 4, finally signal | one test each, as named in the commit |

The first finally-signal test passed without its fix, because the wrapped restore caught the interrupt. It now also asserts that there are no `teardown_errors` and exactly three restore records, and it fails without the fix.

One case has no failing-first test: the plan writer's own `ac_powermode` 0/2 validation. Without it, `NightPlan.from_mapping` refuses the same values, so it is defence in depth.

## Kit delivery note for WP18 (magistrate, Mac-side)

Inputs, all read-only:
- The pilot 6-7 offload copy's `align-pilot-v3-episodes-b-e25/outputs/align_turns.jsonl` (X).
- The same copy's `align-pilot-v3-episodes-b-e18/outputs/align_turns.jsonl` (Y).
- The pilot-7 desk summary, `p7-PILOT.json`.

Steps, in a clean measurement checkout at this lane's head (or its merge):

    .venv/bin/python -B scripts/align_v4_wp18_fixtures.py \
        --x-turns <offload>/align-pilot-v3-episodes-b-e25/outputs/align_turns.jsonl \
        --y-turns <offload>/align-pilot-v3-episodes-b-e18/outputs/align_turns.jsonl \
        --pilot <path>/p7-PILOT.json
    .venv/bin/python -B scripts/align_v4_wp18_fixtures.py ... --check     # same arguments; writes nothing
    .venv/bin/python -B scripts/align_v4_kit.py                            # regenerate the kit
    .venv/bin/python -B scripts/validate_align_v4_w1_plan.py --regenerate-template

Then commit:
- `configs/campaigns/align_v4/registration/wp18_x_token_ids.json` and `wp18_y_token_ids.json`;
- `registration/inputs.json`, where only the four WP18 leaves change;
- the regenerated `collection_plan.json`, `plan_tree.json`, `registration/identity_pins.json` and `night_plan.template.json`;
- the eight contrast stage configs (`stages/episodes-a/align-v4-episodes-a-e06`, `-e07`, `-e09`; `stages/episodes-b/align-v4-episodes-b-e10`, `-e12`, `-e13`, `-e15`, `-e16`) and both `order_manifest.json`.

A scratch fill on the laptop changed exactly these files. Before committing, `scripts/align_v4_kit.py --check` should then block only on `R0.reasoning_effort` and the R1 leaves.

Return the printed `max_turns` and sha256 per arm. Any refusal means a source does not authenticate (wrong member, seed, turn count or ids): stop and report the message. Do not edit the files.
