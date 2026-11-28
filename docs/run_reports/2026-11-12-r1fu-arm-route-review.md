# Executing cold review: R1 follow-up arm route (PR #741)

- **Target:** `fix/2026-11-12-r1fu-arm-route` @ `683dfe654` into `ops/2026-11-11-w1-presign` (base `bb6394f2b`).
- **Reviewer:** Fable 5.2, cold and executing. I did not build this. Review run 2026-11-12, about 07:10 to 07:30 PST, on the Air.
- **Verdict: ADMIT-WITH-FIXES.** Nothing blocks tonight's arm. The fixes are test gaps, wording and one optional arm-time flag.

## What was established

- The plan this route writes for t0 19:26 PST tonight carries `programmed_span_s` 108,768 and `window_max_s` 126,480, and no `ac_powermode`.
- `origin/main`'s `NightPlan.from_mapping` accepts that plan. With `ac_powermode: 0` added back it rejects it: `plan keys are not exact (missing=[], extra=["'ac_powermode'"])`.
- The four route files in `b5b76b597` are blob-identical to `lane/2026-11-10-r1-g0-rop` @ `da3187e6e`.
- The PR touches no condition-13 file (`v4_registration.R1_EXECUTED_SOURCES`), so it does not call for a repeat smoke on that ground.
- All listed test modules pass at `683dfe654` and on a local three-way merge with #739 and #740.

## Check table

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Sizing is RL-72 E2 | PASS | Recomputed from the phase table: no-redo 58,711.9616 s, largest unit 7,563.9952 s. Floor = ceil(58,711.9616 + 2 × 7,563.9952 + 2 × (7,563.9952 + 5,400)) = 99,768. Span = 99,768 + 9,000 = 108,768. Window = 60 × ceil((108,768 + 3,300 + 7,200 + 7,200) / 60) = 126,480. |
| 1 | Work deadline fits the window | PASS | Driver start is at most t0 + 3,300 + 300 + 1,830 = 5,430 s. Work deadline (start + span − 900) is at most t0 + 113,298; driver end at most t0 + 114,198. Post bookend and final writes bring it to 116,628. The window is enforced at t0 + 126,480 + 300 (`run_night.py:1164`). Margin 9,852 s. |
| 1 | No double count with the driver's 9,000 s | PASS | The driver's `pre_calibration_bracket` / `post_calibration_bracket` are runtime kinds inside the driver (`r1_phase_table.py:51,69`; cap 1,800 each at `align_r1_rehearsal.py:326`) and are excluded from the unit sum (`:1253`). The wrapper's bookends are separate `validate_powermetrics_fiducial.py` runs outside the driver (`r1_arm.wrapper_bytes`). |
| 1 | 11:45 batch handling | PASS, one note (F3) | Crossings are reported and add no time. A 126,480 s window can intersect at most two batch windows, so the "more than two" refusal cannot fire for a real t0. The driver itself refuses a third encounter (`align_r1_rehearsal.py:1026`). |
| 2 | `ac_powermode` drop | PASS | Absent and 0 are treated the same everywhere on presign: admission expects `DEFAULT_AC_POWERMODE` 0 (`run_night.py:4397`); the host lock is taken only for `== 2` (`:4906`). The only difference is the record field `plan_declared` (None instead of 0), which nothing reads. |
| 2 | Who sets and restores High Power | PASS | The R1 driver's `PowerModeGuard` under the host night lock sets the A-B-A legs and restores. Backstops: the chain's EXIT/signal trap and start-up marker restore (`align_r1_rehearsal.zsh`), and `run_night._close_ac_powermode`, which closes every plan including mode-0 R1 chains. |
| 2 | Main's watchdog accepts the plan | PASS | Executed: main's `joulewise/night_gate.py` parsed the real plan written for tonight's t0. `hazard_window` keys match main's exact set. |
| 2 | Any gate requiring the key for R1 | None found | `night_gate.py` is identical on the lane and presign. `w1_prequal`'s `ac_powermode` uses are W1 `runtime_requirements`, not the night plan. |
| 3 | D-7 packet path and sha in `arm.json`; missing flag | PASS | Asserted by the end-to-end test and by `test_plan_pins...`. |
| 3 | Stale packet at arm | Accepted by design (F1) | Executed: a packet with `status: REFUSED`, a zero `executed_commit` and an old mtime was recorded with its sha and no flag. |
| 4 | Faithful port plus the fix | PASS | Blob ids equal for all four files. Lane-only assumptions listed below. |
| 5 | Mutants | 14 of 17 killed | See the mutant table. |
| 6 | Tests | All green | See the test table. |
| 6 | `not_scanned` row for `r1_arm.py` | Not required tonight | See "RL-93 / C09". |
| 7 | Merge-ability | Clean | See "Merge-ability". |

## Mutants

Each mutant was applied to `joulewise/align/r1_arm.py` in a separate worktree and run against `tests.align.test_r1_arm`. No mutant touched process or signal code.

| Mutant | Result | Killed by |
|---|---|---|
| M1 span refusal removed (wrong span accepted) | Killed | `test_sizing_refuses_a_driver_span_other_than_rl72_e2` |
| M2a window = route base (117,768) | Killed | `test_follow_up_sizing_is_rl72_e2_for_every_t0` |
| M2b plan `window_max_s` = base, `arm.json` correct | Killed | `test_plan_pins_single_chain...` |
| M2c window 60 s short | Killed | `test_follow_up_sizing...` |
| M3a crossings add 11,164 s each | Killed | `test_follow_up_sizing...` (08:00 case) |
| M3b refuses at two crossings | Killed | `test_follow_up_sizing...` (08:00 case) |
| M3c crossing count always reported as 0 | **Survived** | No test asserts an exact count |
| M3d crossing clock 13:15 instead of 11:45 | Killed | `test_follow_up_sizing...` |
| M4 `ac_powermode: 0` re-added | Killed | `test_plan_pins_single_chain...` |
| M5a packet sha never recorded | Killed | `test_production_route_completes_with_synthetic_runtime` |
| M5b `prepare_packet` key dropped | Killed | two tests |
| M5c packet read from custody, not the measurement root | Killed | end-to-end test |
| M6 missing-packet flag dropped | Killed | `test_plan_pins_single_chain...` |
| M7 plan `programmed_span_s` left at 100,627 | Killed | `test_plan_pins_single_chain...` |
| M8 `prepare` ignores the checkout's span | **Survived** | No test drives `prepare` with a checkout whose span differs |
| M9 "window covers the wrapper" refusal removed | **Survived** | Equivalent with today's constants: the branch is unreachable |
| M10 one bookend dropped from the terms | Killed | `test_window_covers_wrapper...` |
| Stale packet accepted | **No kill possible** | The unmodified route already accepts it (F1) |

For M8 the real code does refuse. Executed: a checkout whose `r1_runtime.json` has `g0_timeout_s` 1,140 gives span 108,048, and `prepare` raises "driver span 108048 s is not the RL-72 E2 follow-up span 108768 s" before writing custody.

## Tests

Run one module at a time with `nice -n 10 python3.13 -B -m unittest`, TMPDIR on the SSD, 32 GB free on `/` throughout.

| Module | At `683dfe654` | On the three-way merge |
|---|---|---|
| `tests.align.test_r1_arm` | 10 OK | 10 OK |
| `tests.test_host_command_guard` | 15 OK | 15 OK |
| `tests.hazards.test_refusal_allowlist` | 24 OK, 1 skipped | 24 OK, 1 skipped |
| `tests.align.test_w1_prequal.RouteTests` | 3 OK | 3 OK |
| `tests.align.test_v4_registration` | 24 OK | 24 OK |
| `tests.align.test_v4_dynamic_closure` | 10 OK | 10 OK |
| `tests.align.test_v4_executed_closure` | 6 OK | 6 OK |
| `tests.align.test_r1_followup` | 12 OK | 12 OK |
| `tests.test_powermetrics_reap` (from #739) | n/a | 9 OK |

`tests/test_w1_prequal.py` does not exist; the module is `tests/align/test_w1_prequal.py`.

## Merge-ability

- `git merge-tree --write-tree` is clean for #741 + #739, #741 + #740 and #739 + #740. The three change disjoint file sets.
- A local three-way merge (683dfe654, then `2b2defd74`, then `05e4b5974`; tree `09bc361c8`) passes every module above. It was not pushed.

## Lane-only assumptions checked on presign

- **Chain argv.** Presign's `align_r1_rehearsal.zsh` adds the fixed packet path and `--prepare-packet`. The wrapper pins the chain source by sha, so this is carried. The packet check sits in the inner chain, after the dwell and the pre bookend: a missing packet costs the arm, the dwell and one bookend before exit 2. The arm flag is what catches it earlier.
- **Hazard driver interface.** Presign's driver refuses `meter_not_sampling` unless the KM003C is live at the arm and its stream is ready. On the lane the meter was a disclosed diagnostic. This is the measurement Mac's physical state, not this PR, but the arm item should name it.
- **Untracked packet in `$M`.** The packet is not gitignored. The HAZARD_PACK path does not run `night_gate`'s C5 clean-checkout refusal (`evaluate_night` refuses HAZARD_PACK plans outright; the hazard driver only records `status_clean`). So the packet does not refuse the night. Any `test -z "$(git status --porcelain)"` step in the arm item must run before the kit's `prepare` writes the packet.
- **Paths.** `$M/.venv/bin/python`, `scripts/install_night_agent.sh`, `scripts/b6_courier.sh` and `validate_powermetrics_fiducial.py` with its four flags all exist on presign.
- **Span source.** `driver_span_s(measurement)` uses the running checkout's driver code with the measurement checkout's config. They are the same thing only when `arm_align_r1.py` is run from `$M`, as the runbook does.

## RL-93 / C09: a `not_scanned` row for `r1_arm.py`

- Not required before tonight. The census test passes at this commit and on the merge: no scanned module depends on `r1_arm.py` or `arm_align_r1.py`.
- RL-93 names the driver, the kit and the runtime, and says its registry wording "gates neither the smoke nor tonight's arm".
- If a row is added later, `desk` alone would not be a true reason. `_display-dwell` and `_bookend` run inside the window; they always return 0 and cannot stop collection. I did not check whether the census test accepts a row for a file nothing scanned depends on.

## Findings

None is blocking.

**F1 (medium, D-7). The arm records whatever file is at the packet path.** A packet from another commit, a `REFUSED` packet, or one left by an earlier night of the same commit is recorded with its sha and no flag.
- A wrong-commit or refused packet is then refused by the driver, after the arm, the dwell and the pre bookend. The night is lost; no bad data.
- A same-commit stale packet is accepted by the driver too. Only the contract's procedure catches it: delete, `prepare`, arm, compare the sha.
- Tonight the arm item must carry those three steps, and must also check that `arm.json` `flags` has no `r1.prepare_packet_absent_at_arm`.
- Optional follow-up: `r1_arm.py` is not a condition-13 file, so `prepare` could flag a packet whose `status` is not `FOR_LEAD_ARM` or whose `executed_commit` is not the measurement head. A flag, not a refusal.

**F2 (low, tests). Three survivors.**
- M3c: restore exact crossing counts in `test_follow_up_sizing...` (1 for 19:26 and 13:30; 2 for 08:00).
- M8: add a `prepare` case on a checkout whose config gives another span; assert the refusal and that no custody directory is written.
- M9: unreachable today. Either drop the branch or test it with patched constants.

**F3 (low). A batch window already open at t0 is not disclosed.** `batch_crossings` counts 11:45 starts in `[t0, t0 + window)`. For t0 at 12:00 it reports one crossing, though the driver can meet two windows. The count is disclosure only and the driver enforces its own quota. Not tonight's case: t0 19:26 gives one crossing, Friday 11:45, and the window ends Saturday 06:34.

**F4 (low). `latest_driver_end_offset_s` omits the arm's return grace.** The hazard driver waits `t0_stage_cap_s` + `ARM_RETURN_GRACE_S` (300 s) for the arm, then starts the monitor and meter. Add about 400 s to 114,198. The 9,852 s margin covers it.

**F5 (low, wording).** Runbook section 1 still fetches `lane/2026-11-08-r1-arm`; the new header says the RUN_STATE arm item supersedes it. `docs/align/v4/W1-SMOKE.md:44-45` still says the R1 route is pinned in `arm_routes.json`.

**F6 (advisory, for the lead; not a defect in this PR). The 19:26 bound and the wrapper's prefix.**
- 11:45:00 minus the no-redo subtotal (16 h 18 min 32 s) is 19:26:28. RL-72's "t0 no later than 19:26" looks like that subtraction; this is my inference, the ruling does not say.
- The driver starts after the hazard arm, the 300 s dwell and the pre bookend: up to 5,430 s after t0. Its own pre bracket (up to 1,800 s) is also outside the no-redo subtotal.
- So at t0 19:26 a no-redo night is likely to reach Friday's 11:45 window and take one encounter: a wait to 13:15. That is inside the span's budget (two encounters) and the window still holds. An earlier t0 avoids the wait.

**Observation (not this PR).** The wrapper's pre bookend is a powermetrics capture under a kill-on-budget helper. If it timed out, RL-91's orphan question would apply to a sampler started before the driver. #739's adapter change does not obviously cover `validate_powermetrics_fiducial.py`; I did not trace it.

## What I did not do

- No host-changing command, no MBP access, no real sudo. The end-to-end route test uses the repo's fakes.
- I did not run the full test suite, only the modules listed.
- I did not read RL-64 or RL-84 beyond the passages that bear on sizing, `ac_powermode` and D-7.
