# Cold final pass: ALIGN v4 R1 round-5 integrated head (2026-11-06)

**Verdict: no BLOCKER, no HIGH. Three MEDIUM, six LOW.**

Nothing on this head corrupts R1 or W1 energy data. Nothing admits a night on a host whose AC powermode differs from the plan's. Nothing changes v3 kit bytes.

- Two MEDIUMs are new R5-6 paths that leave the measurement Mac in High Power with no restore. They fail closed: the next plan-0 night refuses on the mode. But they lose that night and need a manual `sudo -n pmset -c powermode 0`, and one of them contradicts the runtime contract's own R5-6 text.
- The third MEDIUM is a divergence from protocol v4 :247-251. When R1 changes the R0 sensor picks, the kit cannot admit the R1-pick S7 that the protocol asks W1 to use.

I changed no code.

Reviewer: Opus 5.5, cold, with no context beyond the documents below.

Target: `lane/2026-11-06-v4-r1-integrated@d1639a0b3` versus `origin/lane/2026-11-05-align-pilot10-benign` (merge base `c712318e5`). I focused on the round-5 delta `54e844b87..d1639a0b3` (33 files, +3,914/−226), plus the earlier admission and close code it relies on.

Documents read:
- the round-5 section of `docs/run_reports/2026-11-06-align-v4-r1-integration.md`;
- `docs/run_reports/2026-11-06-align-v4-r1-round5-infra.md`;
- `LEAD-RULINGS-1.md`, `LEAD-RULINGS-2.md` and `CHAIR.md` rulings 1, 6, 7 and 16;
- `docs/align/r1_runtime_contract.md`;
- the R1 passages of `docs/align/pilot_protocol_v4.md` (:230-260, :550-575, :650-680);
- the round-4 executing review and Fable cold pass, whose findings LEAD-RULINGS-2 rules on;
- the Fable cold pass at `a2193446d`.

Code read:
- line by line: `scripts/align_r1_rehearsal.py` (`run`, `_segment`, `aba_adoption`, the U5, duty and soak helpers); `joulewise/align/apple/r1_runtime.py` (the kinds, hooks, `Segment.close`, `step_d_result`, `gated_budget`, the slot derivation and the watchdog); `joulewise/align/apple/powermode.py`; `scripts/align_v4_session.py`; the round-5 kit diff (`check_r1_evidence`, `check_r1_budget_and_policy`, `ruling_1f_fit`, `validate_wp18_fixtures`, `check_window_reference_roles`); `scripts/run_night.py`, from `run_night`/`_run_night` up to the hazard branch, with `_admit_ac_powermode` and `_close_ac_powermode`; `scripts/align_v4_wp18_fixtures.py`; `scripts/night_chains/align_r1_rehearsal.zsh`;
- also: `bytes_h_session.prepare`/`install`/`measurement_view`, `b5/plan.py` (ac_powermode), the `workload.py` and `external_volume.py` hunks, and `b5/driver.run_hazard_night` (to confirm the night is synchronous, so the close restore runs only after the window).

Nothing restricted was opened, no weights were loaded and nothing touched the measurement Mac. Every run used `nice -n 19 taskpolicy -b /private/tmp/jwsol/venv-both/bin/python -B` with `TMPDIR=/private/tmp/jwr5-tmp/cold`, one module per process, in a worktree under `jw-wt/`.

## What I executed

| Check | Result |
|---|---|
| `tests.align.test_r1_rehearsal` | Ran 62, OK |
| `tests.align.test_v4_kit` | Ran 87, OK |
| `tests.align.test_v4_powermode_record` | Ran 9, OK |
| `tests.align.test_r1_runtime_contract` | Ran 9, OK |
| `tests.align.test_v4_wp18_fixtures` | Ran 11, OK |
| `tests.align.test_r1_inventory` | Ran 11, OK |
| `tests.align.test_external_volume` | Ran 23, OK |
| `tests.test_b5_plan` | Ran 29, OK |
| `tests.test_run_night` (full, run twice) | Ran 305: failures 13, then 14. All are in classes this laptop fails for environment reasons, and none reaches admission or close: the 8 `test_installer_*`/launch-agent tests ("test interpreter must load the battery fixture in child Pythons"); `BindSupervisionProcessTests` timing (3, then 5, under load); `QuietDriverIntegrationTests.test_supervised_worker_is_reaped_on_cancellation` (second run only). The infra report records 11 of the same classes on its head. The integration report says this module "was not rerun here", so these are the first tails on `d1639a0b3`. |
| `tests.test_run_night -k powermode -k high_power -k marker -k close_restore -k Automatic` | Ran 18, OK |
| Probe K (scratch, in-process, using `test_v4_kit.ready_inputs`) | (1) R1 changed the picks, lead verification recorded, W1 policy on the R1 picks with `turn_cap_s` set to `s7_for_r1_picks.S7 = 60`: **refused**, "`turn_cap_s 60.0 differs from r1_slots.slots.S7 120.0`". The same policy with the R0-pick S7 of 120 is **admitted** (MEDIUM-3). (2) `delta_fast_c = 25.0` is **admitted** (LOW-1). (3) Picks unchanged, but the policy's `s_fast` names a die-list key that is not the pick: **admitted** (LOW-2). |
| Probe I (scratch, fake sudo/pmset from `test_v4_kit.FakeArmHost`; `launchctl print` stubbed to return 0) | `align_v4_session.install` under plan `ac_powermode` 2 prints "launchd already holds the night job; installer not called" and returns `{}`. Afterwards the host mode is **2** and the W1 marker exists. No restore ran (MEDIUM-1). |
| `origin/lane/2026-11-06-v4-r1-integrated` re-fetched before commit | still `d1639a0b3` |

## Findings

### MEDIUM

**MEDIUM-1 (b, e): `install` leaves the host in High Power when the shared installer declines without raising.**

- **Where:** `scripts/align_v4_session.py:153-158` sets mode 2 (`enter_high_power`) before `_arm_and_install`. The restore runs only in the `except BaseException` arm (`:163-172`). `_arm_and_install` ends with `return pilot.install(session, **kwargs)` (`:202`).
- **What goes wrong:** `bytes_h_session.install` returns normally, without installing anything, when `launchctl print` finds a loaded `com.joulewise.night` job (`scripts/bytes_h_session.py:409-412`: "launchd already holds the night job; installer not called").
- **Consequence:** probe I shows the host left at 2 with the marker, and `install` returning success-shaped output. If the loaded job belongs to another session (a stale or earlier night, which is how this branch is normally reached), that night's plan declares 0. It refuses on the mode, and its own measurement view cannot see this session's marker. So a night is lost and a manual restore is needed. If the job is this session's own (a crash after bootstrap and before the install was recorded), the outcome is correct.
- **Contradiction:** `docs/align/r1_runtime_contract.md:114` says "If the arm then refuses for any reason, it restores Automatic". This branch is a non-installing return that the restore guard does not treat as a refusal.
- **Fix:** restore Automatic unless `pilot.install` returned an install record with `exit_code == 0`. Test it with the probe above, which fails on the head.

**MEDIUM-2 (b): a W1 High Power night that never reaches post-admission is never restored, and the "owed to the next night" safety net does not exist across sessions.**

- **Where:** `_close_ac_powermode` is registered only after a successful admission under 2 (`scripts/run_night.py:4125-4131`). After `install` has set mode 2, every earlier exit returns with the host at 2:
  - a plan that does not parse (`:4083-4087`);
  - a rerun or J4 `launch_abandoned.json` record (`:4100-4111`);
  - an admission refusal (`:4125`), for example two failed `pmset` reads, where `observed` is None.

  So does a night that never launches at all: launchd does not fire, or the operator abandons the session after arming.
- **Why there is no safety net:** `_close_ac_powermode`'s docstring (`:4029`) and the infra report (`2026-11-06-align-v4-r1-round5-infra.md:39`) say a failed restore "stays owed to the next night". But the marker lives in `<session>/measurement/` (`bytes_h_session.measurement_view`, `:129`: a fresh directory of symlinks per session, made at prepare). A later session's view never contains it. The test `test_failed_close_restore_keeps_the_marker_for_the_next_night` (`tests/test_run_night.py:846`) only shows that the marker survives inside the same view.
- **Severity:** the contract (`:116-118`) states the real behaviour for a SIGKILL or power loss: the next plan-0 night refuses on the mode alone, which fails closed. The pre-admission exits and the never-launched night are a wider set than that, and they are not stated. No data is at risk. The cost is Mac time (a lost night) and a manual restore. This is exactly the "leave the Mac in High Power" class.
- **Options for the lead:**
  - (a) move the High Power set from `install` to `run_night` itself, after admission against the plan's declared 2, under the same closer;
  - (b) write the W1 marker at a host-stable path (the source checkout, or a fixed path every view and the R1 chain read), so that the next admission really restores;
  - (c) at minimum, register the closer before the pre-admission exits whenever the plan declares 2.

  Option (a) also shortens the time the host idles in High Power between arm and T0.

**MEDIUM-3 (d): with changed sensor picks, the kit forces W1's turn cap (and delta_slow) to the R0-pick values, against protocol v4 :247-251.**

- **What the protocol says:** "If R1 changes R0's picks … S6 tuning and S7 recovery are computed for the R1 picks from the full-inventory journals and verified by the lead before W1 freeze."
- **What the runtime does:** it computes `s7_for_r1_picks` (`r1_runtime.py:1499-1502`), and the driver carries it into `r1_slots.thermometry.D` (`align_r1_rehearsal.py:539-550`).
- **What the kit does:** `check_r1_budget_and_policy` requires `thermal_policy.turn_cap_s == slots.S7` and `delta_slow_c == slots.S6` (`scripts/align_v4_kit.py:343-346`). Both come from the R0-pick soak band and recovery (`r1_runtime.py:638-644`). The only escape is an `s6_tuning` receipt for S6. There is none for S7, and `lead_verification` (`:225-230`) is a free-text authority that changes no binding.
- **Probe K(1):** W1 on the R1 picks with the R1-pick S7 refuses. W1 on the R1 picks with the R0-pick S7 is admitted.
- **Severity:** in the changed-pick case, the only admissible W1 policy gates new keys with the old keys' recovery cap and band. Data are not corrupted, and the lead's verification is required, but the kit makes the protocol's own path impossible.
- **Fix:** when `sensor_pick_changed` is true and the policy names the R1 picks, bind `turn_cap_s` to `thermometry.D.s7_for_r1_picks.S7`. Bind S6 to a tuned value from the R1 picks' quiet-window band, under the lead receipt. Alternatively, the lead amends the protocol to "W1 keeps R0's S6/S7 when picks change" and logs it.

### LOW

**LOW-1 (c): `thermal_policy.delta_fast_c` is bound to nothing.**
- R5-4 binds `chunk_tokens`, `delta_slow_c` and `turn_cap_s` (`align_v4_kit.py:343`). `delta_fast_c` flows into every W1 D member's G1/H gate (`thermal_policy`, `:670`) unchecked; probe K(2) admitted 25 °C.
- The runtime's `bands_c` gives S5's fast twin, `delta_fast = max(1.0, 3 SD_fast)`, but `r1_slots.slots` does not record it.
- Record it, then bind it the same way as `delta_slow_c`.

**LOW-2 (c): the policy's sensor keys need only be members of R1's candidate lists, not R1's picks.**
- `align_v4_kit.py:220-224` checks `s_fast ∈ die_candidates` and `s_slow ∈ heatsink_candidates`. With `sensor_pick_changed: false`, probe K(3) admitted a policy that gates on a listed key that is not the pick, so S1-S7 describe a different key.
- The protocol's "refuse keys outside R1's die/heatsink lists" is met literally. The intent (gate on what was characterized) is not.
- Fix: bind `sensors` to `thermometry.D.s_fast`/`s_slow`.

**LOW-3 (e): wording.**
- `_close_ac_powermode`'s docstring (`run_night.py:4029`), the infra report (`:39`) and the test name at `tests/test_run_night.py:846` all say a failed close restore is "owed to the next night". Across sessions it is not (see MEDIUM-2).
- The contract's `:116-118` wording is the accurate one. Align the other three with it.

**LOW-4 (c): `_check_soak_reference_consumed` accepts any soak sensor's mean.**
- `align_r1_rehearsal.py:965` accepts a `reference_c` that equals any soak sensor's mean, including the fast key's, not specifically `sensors_c[s_slow]`.
- The runtime always reports `reference["slow_c"]`, so this is a weak check, not a live hole.

**LOW-5 (c), plausible: WP18 fixture provenance for the `align_turns.jsonl` files rests on per-turn decode counts.**
- `build_fixture` (`scripts/align_v4_wp18_fixtures.py:50-109`) authenticates the member identity from `p7-PILOT.json`. It ties an operator-named `align_turns.jsonl` to that member only through `per_turn_decode_tokens` and, when present, the summary's `per_turn_{prompt,output}_token_ids`. The rows' own run id and seed are not checked.
- If the p7 summaries do not carry the token-id lists (this cannot be checked off the Mac), a wrong file with coincidentally equal per-turn decode counts would be accepted.
- Have the Mac run print whether the summary id lists were present.

**LOW-6 (e): "It fits the R1 night budget" (LEAD-RULINGS-2 :73) carries no numbers.**
- R5-5 asked for numbers if it did not fit. The claim that it fits has none, and no R1 night plan (`window_max_s`) is in the repo to compare against.
- From the code's caps (soak 1,800; 30B and step-d 2,400 each; 600 cooldown; three A-B-A legs up to 4,329 each; post-D cooldown 1,500; X-G ≈ 1,800; three precools of 1,500 plus gated runs of ≈ 1,800; three planning turns up to 2,700), the all-caps worst case is about 41,500 s ≈ 11.5 h. That is before batch-window waits (up to 1.5 h), quiet redos and calibration.
- The nominal night is much shorter. Put the expected and worst-case walls next to the R1 plan's `window_max_s` in the R1 arm item.

## Already open, not re-reported

These are listed in the round-5 "Open after round 5" section and still hold on this head:
- the classification digest is not bound into `inputs.R1.thermal_policy`;
- the R5-1 G0 design point;
- ruling 1(f) is likely to bind on hardware;
- the inventory-journal coverage, and the second SMC reader;
- `cooldown_after_30b`;
- the S6 TODO, which is not a kit receipt;
- the SIGKILL High Power case;
- the inconclusive scope;
- the `recovery_curve` row shape.

## Checked and found sound

- **Order (R5-5).** The run order is: A-B-A immediately after the 30B step's cooldown; `series_mode` set from `aba_adoption`; step-d and every later model member checked against it (`_check_member_powermode`); Automatic restored before `calibration-post`; `slots_ac_powermode` recorded and bound by the kit. This matches the contract's order paragraph (`:89`).
- **Gated-run precools and X-G (R5-1).** Each gated D run has its own `idle-until-soak` precool against the one-sided band. The duty row is `inconclusive` on a timeout, the overall verdict is fail > inconclusive > pass, and U5 is inconclusive for an uncooled replay run. X-G is preceded by the post-D cooldown. Both consume the soak R through `reference_hook`, and the driver refuses otherwise.
- **Planning deadman (R5-2).** The deadman is popped before the G0 wait and re-armed after the preheat and G0, in `finally` (`r1_runtime.py:1285-1315`). The order is +4, +2, +0. The batch-window bound adds 900 s.
- **Leg without its own G0 release (R5-3).** The leg returns `g0_released: false` with `t_decline_s: null`, and the driver never reads that null as infinite: `legs[label] = None` only feeds `not_evaluated`. A leg whose G0 released but whose t_decline is `unobserved` still refuses (`k_aba_leg`, `:1531-1534`), so a missing PM clock is never ∞. Ruling 16's cases (`high_power_adoption`) match CHAIR :191, including "A legs ∞, B finite → not adopted" and bool rejection.
- **Budgets (R5-4).** `gated_budget` refuses B_D 0 or out of range, and a non-finite T_dead, before model work. `_check_step_d` stops the night right after step-d. The ruling 1(f) arithmetic and `max_fitting_b_d` match the stated rule. `budget_fit_inputs` requires one shared turn cap, and the kit ties it to the anchor's `max_tokens`.
- **High Power plumbing (R5-6).** The marker is written before `pmset -c powermode 2`. A W1 marker is distinguished from the R1 chain's text. An R1 crash marker is restored before `install` takes ownership. A terminal session is refused. A re-install does not set the mode again. `run_night` admits 2 only for a declared 2, and the close restore runs on every post-admission exit and cannot replace the night's exit code. `run_hazard_night` is synchronous, so the close never lands inside the window.
- **`Segment.close` (R5-9).** It catches BaseException for the heaters, the inventory stop, the sessions and the journals. F3 binds step-d bytes to its complete custody. The F2 exclusion is DIR-only.
- **Watchdog (R5-10).** The watchdog budget is 15 s + 4 s hard, inside the driver's 20 s grace. One diskutil retry is recorded. The soak window is 1,200 s by time and ends at the segment's end. Step 4 of the duty fallback no longer admits.
- **Kit and v3.** The kit regenerates unchanged, as the integration report states. The window-reference roles (member 5 captures) are refused if wrong. No v3 kit bytes differ: `git diff origin/lane/2026-11-05-align-pilot10-benign -- configs/campaigns/align_pilot_v3` is empty.

## Claims in the integration report and the reviews

- The integration report's round-5 tails for the align modules I reran match (62/87/9/9/11/11/23).
- Its statement that `tests.test_run_night` "was not rerun here" is now covered by the table above: the failures are environment-only, and the power-mode subset passes.
- The R5-10 deviation (I_D bound 1,750 s, ≈ 4,329 s per leg) is as stated: 65 + 600 + 1,750 + 1.13544 × 1,580 + 120 = 4,329.0.
- The only report text this pass contradicts is the "owed to the next night" wording (LOW-3) and, through MEDIUM-1, the contract's "restores Automatic … for any reason" at `:114`.

## Verdict for the R1 arm item

**R1 can be armed on this head.** None of the findings touches the R1 rehearsal's own power-mode handling: the guard, the chain traps and the marker at `$MEASUREMENT_ROOT`. None touches its evidence path.

Before a W1 arm under an adopted High Power, the lead should:
1. rule on MEDIUM-1 and MEDIUM-2. The smallest safe change is to set High Power inside `run_night` after admission, rather than at `install`;
2. decide MEDIUM-3, either with code or with a logged protocol amendment, before freezing W1's policy if R1 changes the picks.

With an Automatic series (A-B-A not adopted), MEDIUM-1 and MEDIUM-2 do not arise.
