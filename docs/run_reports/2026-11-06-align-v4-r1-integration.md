# ALIGN v4 R1 integration (lane/2026-11-06-v4-r1-integrated)

Date: 2026-11-06. This is code, kit and test integration only. It authorizes no
measurement, opens no model weights, and changes no v3 kit bytes.

Starting head: `3ec30af47`. That is the fixed council-r1 `2f7617629` (which
contains the WP7 fixes `9c92e685a` and the WP8 fixes `6d288fc3f`), plus the
r0-dispositions `700ed5eb5`, plus the regenerated WP23 W1 template with L1
T_dead and the validated heavy/per_turn policy.

Final head: see the last commit on the lane. This report is part of that
commit.

## What is in

| Commit | What |
|---|---|
| `0bae940dd` | Check that the WP23 tests fail without their fixes, plus one gap closed (L1 member-fit). |
| `0edb80702` | merge `lane/2026-11-06-v4-r1-fixes-f2f5f6@8ef3c30f4`: WP8 F2 (dead collector fails fast, no holds after X4), F5 (G0 status source), F6 (episode reference only from a released G0). |
| `a22ec6ca5` | merge `lane/2026-11-06-sol-v4-r1-fix2@6de39451c`, reviewed hunk by hunk: accepted, replaced and rejected hunks below. |
| `2bf063b46` | merge `lane/2026-11-06-sol-v4-council-desk@49c1ce2f8` (on council-base `c3e7a35b3`), reviewed: `v4_estimands.py` with one fix and two functions rejected. |
| `f36dd9f52` | `LEAD-RULINGS-1.md` carried byte-for-byte from `lane/2026-11-06-align-v4-design-council@3b3b2a971`. |
| `47c0ce4f8` | merge `lane/2026-11-06-v4-wp22-synthetic-w1@1de342d1e` (WP22 harness, no conflicts). |
| `0d998b6bc` | WP22 adapted to the integrated kit. The desk's U1 now counts a dead-collector member as X4. |

Council rulings applied as given:
- L1: T_dead = min((1750 − I_D)/1.13544, (1800 − I_D − max_R1_tail − 10)/1.13544). The kit and the W1 validator both assert it, and the kit also asserts the member fit.
- L2: U5 c = 1.0 (already on the head from council-r1).
- L3: not applicable here.

## WP23: do the tests fail without their fixes?

The previous agent was cut off during this check. It was redone on the
integrated head: each fix was reverted on its own in a scratch worktree, and
`tests.align.test_v4_w1_plan` was run each time.

| Reverted fix | Result |
|---|---|
| template from `5d4da342b` (stale member bindings) | 6 fail/error, incl. `test_committed_template_is_regenerated_from_the_kit_roster` |
| heavy/per_turn supplied instead of validated | `test_template_thermal_policy_heavy_per_turn_are_validated_not_supplied` fails |
| heavy/per_turn result check removed | same test fails |
| templated `window_reference` accepted | same test fails |
| old T_dead = (1750 − I_D)/1.13544 | `test_t_dead_follows_lead_ruling_l1_and_binds_r1_tail` errors |
| `max_r1_tail_s` not bound to r1_slots | same test fails |
| (869442ae0) run_night schema accepted | `test_template_is_not_mistakable_for_a_run_night_plan` fails |
| (869442ae0) inputs.json mismatch accepted | `test_values_must_equal_the_inputs_the_kit_installs` fails |
| (869442ae0) inputs.json pending accepted | same test fails |
| (869442ae0) canonical gate validator skipped | `test_thermal_policy_uses_the_canonical_gate_validator` fails, plus 3 more |
| **`kit.check_l1_member_fit` removed** | **all 10 passed: a gap** |

The gap is that the T_dead equality accepts a non-positive L1 value when
I_D + max_r1_tail_s + 10 ≥ 1800. `0bae940dd` adds that case (I_D 1700, tail
95 s). The new test fails with the assertion removed and passes on the head.

A full revert of either commit's sources only gives signature errors
(`validate()` takes 3 arguments). That does not test behavior, which is why
each fix was reverted on its own.

## Conflict resolutions

- **f2f5f6, `joulewise/align/apple/workload.py` (G0 entry).** HEAD has council
  ruling 7's `powermode = self._observe_ac_powermode()` after G0. f2f5f6 wraps
  G0 so that a ThermalFault becomes `AdapterFailure(UNKNOWN_ERROR)`. Both are
  kept: the wrapped G0 comes first, then the powermode observation. A member
  that faults at G0 produces no bundle and records no powermode.
- **fix2, `configs/campaigns/align_v4/plan_tree.json` and
  `registration/identity_pins.json` (generated).** Resolved by regenerating
  the whole kit (`scripts/align_v4_kit.py`) after the code review edits, then
  the W1 template (`validate_align_v4_w1_plan.py --regenerate-template`). The
  contrast deadman change re-hashes the 8 contrast configs. `--check` reports
  no drift.
- council-desk and WP22 had no textual conflicts.

## fix2 (6de39451c, cloud Sol, unreviewed until now): hunk review

Accepted:
- `stop_precedence.py`: a malformed call ranks below runner error, thermal
  censoring and budget cuts.
- `workload.py`: a turn cut by its own token budget is not
  `episode.malformed_tool_call`. Budget truncation is registered censoring.
- `workload.py`: `unsupported_tool_call_format` is tabulated, not a malformed
  stop. **This narrows WP8 F1 as the cold pass worded it. For lead
  confirmation.** Reason: the flag is a marker heuristic (`"name"`,
  `"arguments"`, `<tool`, …) that ordinary JSON or prose answers can set. On
  the JSON path it would exclude anchors and contrast runs that pilots 4-10
  counted. Final design 658 already gates D on zero unsupported flags at
  qualification.
- `thermal_desk.py`: a dead collector is also X4 in `calibration_exclusions`.
- `align_r1_rehearsal.py`: the High Power marker is written before
  `pmset powermode 2`.
- `align_r1_rehearsal.zsh`: the marker moves to `$MEASUREMENT_ROOT`, which
  run_night exports and which is stable across nights. Test added.
- `align_v4_thermal_desk.py`: a roster member with no artifact stays as an
  excluded row (`member.artifact_missing`), and unresolved reference ids are
  refused. Test added.
- `test_history_rendering.py`: repairs
  `test_untyped_xml_arguments_match_the_emitted_prefix_exactly`, which
  **errors on `3ec30af47`**.

Replaced:
- **The contrast deadman.** WP7's 330 s and the lane's 1585 s are both wrong.
  The deadman arms at G0 entry and covers G0, G1 and the pilot-7-count
  episode.
  - 330 s is shorter than the planned X-G episode alone (558 s), so the G arms
    end in deadman and lose pilot-7 token identity.
  - 1585 s = 1800/1.13544 ignores the member intercept: 516.6 + 1.13544·1585 =
    2316 s, which is past the runner's 1,800 s kill (FD:153).
  - Now `CONTRAST_DEADMAN_S = (1750 − 516.575)/1.13544 = 1086.30 s`. This is
    FD:270's T_dead,m with the pilot-3 30B intercept (`sizing_b5.json`
    `member_law.intercept_s`).
  - The test pins the intercept to that file, the 1,750 s fit and coverage of
    each arm's planned episode. It fails with 330 and with 1585.

Rejected:
- **`workload.py` break on `episode.malformed_tool_call`.** On the XML path a
  refused turn already has no calls. The break acts only on the JSON path (30B
  anchors and contrast), where it would end trajectories that pilots 4-9 and
  pilot 7 continued. That breaks anchor comparability and the contrast's
  pilot-7 token identity. It had no test.
- **`workload.py` deleting `episode.malformed_tool_call` after an H
  timeout.** The precedence already ranks thermal first, and the member is
  excluded either way. Deleting the flag loses information. It had no test.

Every accepted source hunk fails its own test when reverted (checked file by
file).

## council-desk (49c1ce2f8, cloud Sol, unreviewed until now)

`v4_estimands.py` is standalone: nothing on the registered path imports it.

Accepted:
- `subturn_h_star` (2a), `residual_by_hold_count` (2e);
- `u6_stability` (6; the sandwich algebra was checked);
- `d_turn_position_means`, `u4_reference`, `acceptance_labels` (6);
- `contrast_delivery` (9a; direct test added);
- `d_configuration_assertion` (10), `conformal_threshold_diagnostics` (12),
  `sentinel_admissibility` (15), `warm_reference_diagnostic` (18).

Fixed:
- **`benign_carrier_curve` (2b).** It used rank ⌈.95(m−1)⌉ clamped to n. The
  correct threshold is rank ⌈.95m⌉ of the other m − 1 carriers, which is the
  registered conformal rank (19(n+1)+19)//20, with no threshold above n
  (ruling 3). The test fails on the lane's code.

Rejected:
- **`contrast_verdict`.** It is a second verdict path that drops FD §2.5's CI
  conditions, uses |d| < 10 J instead of ≤ 6 J for REJECTED, and drops
  token-identity and exclusion filtering. Ruling 9 (delivery, stage term,
  d > 0) belongs in `thermal_desk.deciding_experiment`. **Open W1 item.**
- **`full_omission_rows` (2c).** It deletes every later P/C row and the omitted
  turn's decode row, where it should subtract the omitted reasoning tokens
  from later P/C counts. **Open; needs a count-level implementation.**

## WP22 synthetic W1 dry run (kit → 18 members → gates/holds → attribution → desk)

The harness was adapted to the integrated kit:
- r1_slots stand-in: ac_powermode 0, max_r1_tail_s 30;
- L1 T_dead;
- ruling 1(g)'s 17↔18 swap (replay 17, development 93 at 18);
- a contrast-deadman test replacing the 330 s pin.

The injected window found one desk divergence, and it is fixed. D U1 counted
one thermal exclusion where the design counts two: 8 (X2) and 18 (collector
death). Since WP8 F2 a dead collector fails the member fast, so its flags carry
`thermal.collector_failed`, not `thermal.state_unobserved`. `thermal_exclusions`
(U1(b)), the observed/coverage set and the U3 pair filter now share
`collector_lost()`. The test fails without the change.

`JW_WP22_FULL=1 python -m unittest tests.align.test_v4_w1_synthetic`:
**18 tests OK (expected failures = 2)**.
- **Clean window:** all 18 members succeed with no exclusions. Desk
  turn-owned energy matches the independent world integral. U1, U3, U4-U6, the
  consequence and the contrast verdict match the design oracle.
- **Injected window:**
  - X1 (13): os_level is detected.
  - malformed XML (11): stopped and excluded.
  - X7 deadman (14): detected.
  - D U1 fails ("thermal protocol not met"), as designed.
  - 30B U1 passes with 1 exclusion.
  - The contrast verdict matches the oracle.
- **The two remaining expected failures are design divergences:**
  - F2: a 600 s G0 timeout on D consumes T_dead, so X2 becomes X7. This is
    open under ruling 1's duty bar and fallback order.
  - F3: a dead collector fails the member fast (WP8 F2) rather than taking
    FD §2.6's timed wait. Accepted; the member is still X4 at the desk.

## Kit checks

- `git diff origin/lane/2026-11-05-align-pilot10-benign -- configs/campaigns/align_pilot_v3`
  is empty, against both the worktree and HEAD.
- `scripts/align_v4_kit.py --check` reports no drift (all generated bytes
  equal the build). It exits 1, fail-closed. On the committed inputs it
  blocks on: WP11.identity_unit, WP11.artifact_inventory,
  WP11.local_file_verification, WP18.X/Y max_turns and token_fixture_sha256,
  R0.reasoning_effort, R1.B_D, R1.I_D, R1.T_dead, R1.thermal_policy and
  WP15.runtime_entrypoint.
- A `require_ready` probe with every non-R1 input filled (the WP22 synthetic
  values) refuses only on R1-measured inputs:
  - first `R1.B_D, R1.I_D, R1.T_dead, R1.thermal_policy`;
  - then the r1_slots `ac_powermode`;
  - then the r1_slots `max_r1_tail_s`;
  - each R1 leaf on its own.

  It admits once all of those are filled. So the gate is fail-closed only on
  R1-measured inputs **once WP11, WP18, R0 and WP15 have been supplied**. They
  are not supplied on this lane yet.

## Suite tail (integrated head)

All runs are on `0d998b6bc` (the code head; this report adds only docs).
Every run used `/private/tmp/jwsol/venv-both/bin/python` under
`nice -n 19 taskpolicy -b` with `TMPDIR=/private/tmp/jwwf-tmp`.

- **Whole `tests/align`, one module per process (105 modules, 3 at a time):**
  every module is rc=0, for a total of **Ran 1297 tests, OK (skipped=32)**.
  The modules add up to 7,570 s. The slowest were:
  - test_moe_calibration: 1,941 s
  - test_analysis_metadata_baseline: 848 s
  - test_moe_review: 729 s
  - test_analysis_budget_pilot: 514 s
  - test_power_duty: 336 s
  - test_energy_residual_regressions: 297 s

  Selected module lines:
  ```
  test_r0_checks rc=0 Ran 29 tests in 2.464s OK
  test_r0_mlx rc=0 Ran 5 tests in 0.195s OK
  test_r0_mlx_native rc=0 Ran 1 test in 233.503s OK
  test_v4_estimands rc=0 Ran 14 tests in 0.003s OK
  test_v4_w1_synthetic rc=0 Ran 18 tests OK (skipped=14)   # the full windows are gated by JW_WP22_FULL
  ```
- **The same suite as one `unittest discover -s tests/align -t .` process,**
  under a 5,400 s guard, was killed by the guard (rc=124) while still in the
  MoE calibration Monte Carlo. No F/E marks and no traceback appeared up to
  that point. This is why the per-module run above is the suite of record.
  Background QoS limits the work to the efficiency cores, so the
  single-process run cannot fit 90 min.
- **`JW_WP22_FULL=1 tests.align.test_v4_w1_synthetic`:** Ran 18 tests in
  136.420s, OK (expected failures=2).
- **`tests.test_align_pilot_session`:** Ran 16 tests in 375.421s, OK.
- **The known isolation issue.** `tests.align.test_r0_checks` alone: Ran 29
  tests in 2.066s, OK. `test_r0_mlx test_r0_mlx_native test_r0_checks` in one
  process: Ran 35 tests in 388.421s, OK. `test_r0_mlx test_r0_checks`: Ran 34
  tests, OK. The error did not reproduce on this head.

## Remaining R1 prerequisites (what the R1 arm item must still supply)

Before R1 can arm:
1. **WP15 runtime.** `ALIGN_R1_RUNTIME`: an operator-pinned argv implementing
   `docs/align/r1_runtime_contract.md` (`KIND_FIELDS` and `QUIET_FIELDS`:
   CPU-load journal and census for ruling 8). WP15 also supplies
   `inputs.WP15.runtime_entrypoint`.
2. **R0.** `inputs.R0.reasoning_effort` (the rung that R1's D runs use). The
   ruling 21 proxy rule is recorded before the ladder output is read, if it is
   used.
3. **WP11.** The D identity unit, artifact inventory and local file
   verification for the pinned 8-bit artifact.
4. **WP18.** The X (b-e25 / idx 16) and Y (b-e18 / idx 14) pilot-7 turn counts
   and token-fixture SHA-256, and ruling 9(d)'s laptop render of Y's token
   ids.
5. **A run_night plan for R1.** It exports `MEASUREMENT_ROOT` (now required by
   the chain for the High Power marker) and `NIGHT_DIR`. The host has the two
   `sudo -n` rules for `pmset -c powermode 0|2`. Scheduling avoids
   11:45-13:15 local (ruling 8).

R1 itself must then produce:
- `registration/r1_slots.json`:
  - S1-S9, B_D, I_D, T_dead, N_chunk, t_decline and class;
  - `ac_powermode`, the A-B-A outcome under ruling 16;
  - `max_r1_tail_s`, the largest tail over the 3 gated D runs;
  - deadman consumption by phase, the duty bar verdict (ruling 1a/d) and the
    projected MDE (28).
- `registration/inputs.json` R1:
  - B_D, a multiple of 1024 in [6144, 40960], sized so that the worst-case G0,
    holds and last turn fit T_dead;
  - I_D;
  - T_dead equal to L1 with that tail, and passing the member-fit assertion;
  - thermal_policy: R0-bound sensor keys, δ_fast/δ_slow (δ_slow ≤ 2.0 °C under
    the ruling 1(e) fallback), turn_cap_s ≤ 300, chunk_tokens a multiple of 256,
    heavy and per_turn true.
- The U5 inputs: D's planning-turn step from 3 start states (R, R+2, R+4 °C),
  σ_pair = max(R1 replay-pair SD, 2.97 J), and c = 1.0 (L2).
- The battery drain rate and charge-resume SoC (ruling 4b).

After R1:
- regenerate the kit (`--check` must then pass);
- fill and validate a copy of the W1 template with
  `validate_align_v4_w1_plan.py <copy>`, which reads inputs and r1_slots.

Open items that are not R1-blocking but are W1 items:
- ruling 9 changes in `deciding_experiment`;
- a count-level full-omission variant;
- lead confirmation of the `unsupported_tool_call_format` narrowing;
- F1's `episode.malformed_tool_call` now also flags 30B JSON-path anchors and
  contrast runs, an exclusion pilots 4-10 did not have, for lead
  confirmation;
- the 30B contrast deadman uses the pilot-3 intercept transfer (516.575 s), and
  R1 does not re-measure it.

Process note: `3ec30af47`, `5d4da342b`, `c5cef0066` and `2f7617629` carry author/committer `Edr`, not `mpmdw`. They are already on
origin and are not rewritten (no force push). Every commit from `0bae940dd`
on is mpmdw/mpmdw.
