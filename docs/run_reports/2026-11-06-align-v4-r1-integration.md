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

## Round 4 (lane/2026-11-06-v4-r1-round4-fixes, from `a2193446d`)

This round fixes the open findings of the executing review
(`docs/align/reviews/2026-11-06-r1-integration-executing-review.md`) and the
Fable cold pass (`docs/align/reviews/2026-11-06-r1-integration-fable-cold-pass.md`)
that the lead assigned, lands protocol v4 (chair ruling 22) and records two lead
decisions. It authorizes no measurement, opens no weights and changes no v3 kit
bytes. Every behaviour fix has a test that fails without it (table below).

### Merges

| Commit | What |
|---|---|
| merge `lane/2026-11-06-sol-v4-wp20-protocol@fb36bfaa4` | `docs/align/pilot_protocol_v4.md` (WP20 draft plus its Opus review) and `tests/align/test_protocol_v4_doc.py`. The cloud task's stray root `answer.md` was dropped from the merge. |
| merge `lane/2026-11-06-ssd-always-attached@44b99b37d` | `joulewise/align/apple/external_volume.py`, `scripts/align_external_volume.py`, the SSD study, draft amendment and qualification tooling. `configs/align/v4/external_log_volume.json` stays `status: off`. R1 and the v4 arm pin the configuration to `off` in code (`validate_config(None)`), so adopting the SSD amendment needs a code change, not a config edit. |

### Fixes

**HIGH-3 (executing review) / cold pass HIGH-1: host-level power-mode admission.**
- `scripts/run_night.py::_admit_ac_powermode` runs for **every receipt class**,
  right after the initial census and before any class branch (so the
  HAZARD_PACK branch is covered too). It reads the AC-profile `powermode` from
  `pmset -g custom` (exact key in the `AC Power:` block, through the probe
  seam), retried once on a failed read, and refuses with the new driver code
  `night_refused_ac_powermode` unless it equals the plan's declared value.
- Night plans gain an optional `ac_powermode` key (0 or 2; absent means 0) in
  every class (`joulewise/night_gate.py`, `night_plan_writer.py` omits it when
  unset). The code is registered in `NIGHT_DRIVER_REASON_CODES`, the
  arm-retry table (cold-gate disposition, never an auto-retry) and the two
  policy blocks in `NIGHT_HANDBACK.md` and the derivation runbook.
- If `$MEASUREMENT_ROOT/.align-r1-high-power` exists, admission first runs the
  narrow `sudo -n /usr/bin/pmset -c powermode 0`, removes the marker only after
  that succeeds, and reads the mode again. A failed restore refuses and keeps
  the marker.
- The v4 session `install` (W1/D arm) applies the same admission
  (`joulewise/align/apple/powermode.py::admit_ac_powermode`) against the kit's
  frozen series value.
- `joulewise/environment.py::_parse_pmset` now exposes `powermode` (int or
  None) in the snapshot, beside `low_power_mode`, so High Power is visible to
  every consumer. `pmset -g` prints the active profile, which is the AC profile
  on AC power; the admission gate itself reads the AC profile from
  `pmset -g custom`, the exact key ruling 7 names. The generic environment
  policy (`evaluate_environment_policy`) is unchanged, so no existing
  campaign's findings digest moves.
- **Lead attention:** the b5 hazard doctrine (`joulewise/hazards/arm.py`)
  records `pmset -g custom` as a diagnostic and says power mode is not one of
  the six hazards. run_night now refuses a HAZARD_PACK night whose host is not
  at powermode 0 before the hazard branch starts. A host in High Power changes
  the energy numbers, so this protects every campaign, which is the point of
  HIGH-3.

**MEDIUM-1 (ruling 8 load-journal completeness).** Quiet segments must return
`cpu_busy_t_s` (one sample time per `cpu_busy_cores` value; `LoadJournal`
records it). The driver refuses R1 unless the journal has at least
0.9·W − 5 samples over the W wall seconds it measured around the invocation
and no gap over 5 s. Probe P2's one-sample soak now refuses.

**MEDIUM-2 (L1 on the R1 record).** The driver computes lead ruling L1's T_dead
from the step-d I_D and the largest gated-run tail, prints it (`R1 L1: {...}`),
stores it as `l1` in r1_slots (armed, L1 and effective T_dead, member fit for
armed and effective) and judges the duty bar's 40 % share against
min(armed, L1). Probe P3 (700 s tail): L1 = 870.6 s, the armed 1,451 s no
longer fits (2,459 s), and the duty bar now fails (360 s > 348 s).

**MEDIUM-3 (kit binds r1_slots to R1 evidence).** `require_ready` calls
`check_r1_evidence`: schema `joulewise.align.r1_slots.v1`; source
`R1 hardware rehearsal` (the driver's `R1 synthetic rehearsal` only when the
WP22/test harness passes `synthetic=True`; no production caller does);
`inputs.R1.I_D == r1_slots.slots.I_D`; `ac_powermode` follows the A-B-A verdict
(2 only on `adopt`); U5 present with c = 1.0; `max_r1_tail_s` equals the largest
`deadman_budget` tail; every ruling 20 census passed; and the duty bar passed
or carries `duty_bar.lead_fallback = {step: 1-4, authority}` (ruling 1(e)).
The WP22 stand-in is now R1-shaped.

**Cold pass MEDIUM-2 (G1 blind waits after an unreleased G0).** When G0 does
not release (timeout X2, unobserved X4, deadman X7), the member ends before its
first turn with `episode.g0_unreleased:0` (stop `episode.g0_unreleased`), after
two sampler periods of zero-generation observation. It stays excluded exactly
as before; admitted members are unaffected. One disclosed cost: protocol v4
keeps X2 members "capability-only", and a G0-timeout X2 member now has no
turns, so it carries no capability score (a G1/H-timeout X2 keeps its partial
transcript). The lead's ruling accepts that; the protocol text says so.
WP22 F2 ("X2 becomes X7") now
passes as an ordinary test: the injected G0 timeout is a succeeded X2 member.
`JW_WP22_FULL=1` run: **Ran 18 tests, OK (expected failures=1)** (only F3).

**Cold pass MEDIUM-5 (ruling 7 arm record).** Every v4 arm writes
`<session>/staging/v4-arm-NNN.json` (create-once) before the shared installer
runs, admitted or not: the admission record with the observed value, every
read, the exact `pmset -g custom` text and any marker restore, plus the
ruling 20 volume census. `session.json` lists the records.

**Ruling 20 (external volumes).** R1 takes a census at t0 (before any
powermode or runtime work), before every runtime invocation and before it
writes r1_slots, and refuses if any external volume is mounted; a final
census is recorded in the terminal record. The v4 arm refuses the same way.
All censuses are recorded (`external_volumes`).

**LOWs.**
- `validate_powermode_members` and `arm_powermode_check` refuse an unfrozen
  series value (None == None no longer matches).
- `output.mkdir` sits inside the driver's `try`: a rerun into an existing
  `align-r1` is a recorded refusal (rc 3), and an earlier `r1_result.json` is
  never overwritten.
- The pmset read is retried once, at the episode-start bundle read and at
  admission.
- A custody-invalid member's energy carries
  `turn_owned_basis: reattributed_without_thermal_intervals`, and the desk
  markdown labels it.
- The stale kit comment on ordinals 17/18 is corrected (the kit is regenerated
  because `plan_tree.json` pins the builder's own SHA-256; `--check` reports
  no drift and still fails closed on the 13 placeholders).
- The ruling 8 batch window uses `zoneinfo` `America/Los_Angeles` and compares
  absolute times; a DST-transition test fails on the fixed-offset code.

### Lead decisions (recorded here and in protocol v4)

**(a) JSON path.** `episode.malformed_tool_call` on the 30B JSON path (anchors
and contrast) is recorded and tabulated but is **not** an exclusion. The
workload now writes `episode.malformed_tool_call.json:<turn>` on that path; the
exclusion code (`calibration_exclusions`, `episode_ineligibility_reasons`) and
the stop classifier match only `episode.malformed_tool_call:`, so the JSON
flag neither excludes nor stops. This keeps anchors and the contrast comparable
with pilots 4-10. On D's XML path a malformed call stays the WP8 F1 exclusion.

**(b) XML path.** Chair ruling 2(d) reads, verbatim:

> (d) Resolve WP8 F1, "a refused XML call is invisible to the desk" (`docs/run_reports/2026-11-06-align-v4-merge-gate.md:18`), before D1.

It requires that a refused XML call be visible to the desk; it does not require
an exclusion (the exclusion was F1's own suggested fix, not the ruling's text).
So `unsupported_tool_call_format` on D's XML path sets
`episode.unsupported_tool_call_format:<turn>`, which is tabulated and not
excluded. The desk report gains `tool_call_flags` (per member: JSON malformed
turns, XML refused turns, XML malformed turns; totals; which kinds exclude), and
the markdown prints it.

### Protocol v4 reconciled with the code

`docs/align/pilot_protocol_v4.md` now states: the W1 roster after ruling 1(g)
(replay 17, development 93 at 18; balance text 5↔17; fit rule drops the last
ordinal); T_dead by L1 with the kit's member-fit assertion; the round-4 G0 rule;
the two tool-call decisions; the round-4 status of the three chair-verified
gaps (deadman bound, power-mode pin, refused XML call); and, in the ruling
table, **Code (round 4)** marks for rulings 1, 7, 8, 16, 20, 22 and 28. The
LEAD-RULINGS-1 pin (`3b3b2a971`) is added. Two new doc tests bind the roster
table to `kit.ROSTER` and the round-4 rules to the text. The blind cold gate
before W1 arm is still owed.

### Still open after round 4

- Cold pass MEDIUM-1: the driver still SIGKILLs the WP15 runtime on the first
  signal (no TERM grace), and the contract says nothing about the runtime's
  TERM obligations. Before W1.
- Executing review MEDIUM-4: no contract field for ruling 4(b)'s battery drain
  rate and charge-resume SoC.
- Executing review LOWs 1-3 (A-B-A leg wait bound, `t_decline_s: true`,
  "A legs ∞, B finite" reported inconclusive) and cold pass LOW 3 (runtime argv
  is one executable).
- The open W1 items listed above (ruling 9 in `deciding_experiment`, the
  count-level full-omission variant).

### Fail-without-fix (round 4)

Each fix was neutralized on its own in a scratch worktree at the code head
(a one-hunk edit, then restored), and its tests run with and without it.

| Neutralized fix | Tests | Without fix | With fix |
|---|---|---|---|
| HIGH-3: run_night admission stubbed to admitted | 4 run_night admission tests | 4 failures | OK |
| HIGH-3: pmset read retry off (`READ_RETRIES = 0`) | `test_one_failed_pmset_read_is_retried_and_two_refuse` | fails | OK |
| HIGH-3: plan `ac_powermode` validation off | `test_plan_declared_powermode_must_be_zero_or_two` | 4 subtest failures | OK |
| HIGH-3: snapshot `powermode` not set | `test_powermode_value_is_exposed_for_the_admission_gate` | error | OK |
| MEDIUM-1: gap and sample-count checks off | journal unit test, journal-gap R1 run | 2 failures | OK |
| MEDIUM-2: duty bar on the armed T_dead | `test_l1_is_evaluated_on_the_r1_record_and_bounds_the_duty_share` | fails | OK |
| Ruling 20 (R1): volume verdict ignored | t0 and mid-R1 volume tests | 2 failures | OK |
| LOW 2: `mkdir(exist_ok=True)` outside the guard | `test_rerun_into_an_existing_output_is_a_refusal_not_a_traceback` | fails | OK |
| LOW 8: window boundaries in the moment's own (fixed) offset | `test_batch_window_is_pacific_wall_time_across_a_dst_change` | fails (the `a2193446d` driver waits 0.0 s and starts at 23:00 PST) | OK |
| MEDIUM-3: `check_r1_evidence` not called | `R1EvidenceBindingTests` (8 tests) | 13 (sub)test failures | OK |
| LOW 1: `observed != expected` only | `test_powermode_members_refuse_an_unfrozen_series_value` | fails | OK |
| MEDIUM-5 / arm: `arm_checks` replaced by a bare read | 3 v4 arm tests (record, volume, marker) | 1 failure, 2 errors | OK |
| Cold MEDIUM-2: `g0_unreleased = False` | 2 G0-timeout workload tests | 2 failures | OK |
| Decision (a): JSON path writes `episode.malformed_tool_call:` | `test_json_path_malformed_call_is_recorded_not_excluded` | fails | OK |
| Decision (b): no XML refused-call flag | `test_xml_path_refused_call_is_flagged_and_tabulated_not_excluded` | fails | OK |
| LOW 4: one episode read only | `test_one_transient_read_failure_is_retried` | fails | OK |
| LOW 5: label always `attributed` | `test_desk_excludes_invalid_custody_without_aborting` | fails | OK |
| Ruling 22: protocol roster in A1's order | `test_w1_roster_matches_the_kit_after_ruling_1g` | fails | OK |

The first DST test used the fall-back transition and passed on the old code,
because the wait loop re-evaluates after its first sleep. It was replaced by
the spring-forward case, which the `a2193446d` driver gets wrong.

### Suite tail (round 4)

Every run used `/private/tmp/jwsol/venv-both/bin/python` under
`nice -n 19 taskpolicy -b`, `TMPDIR=/private/tmp/jwr4-tmp`, one module per
process, targeted modules only, on a laptop also running a blinded analysis
and a GPU job.

All rc=0, OK:
- align: `test_r1_rehearsal` (41), `test_r1_runtime_contract` (8),
  `test_v4_kit` (49), `test_v4_powermode_record` (9), `test_v4_w1_plan` (10),
  `test_thermal_gate` (40), `test_thermal_desk` (24), `test_attribution_holds`
  (6), `test_stop_precedence` (4), `test_xml_tool_calls` (25),
  `test_apple_endpoint` (9), `test_apple_campaign` (12), `test_endpoints` (15),
  `test_endpoints_fixround` (15), `test_cache_checkpoint` (16),
  `test_r0_integration` (3), `test_r0_checks`, `test_thermal_sidecar` (9),
  `test_history_rendering` (11, 2 skipped), `test_pilot4` (18, 1 skipped),
  `test_v4_estimands` (14), `test_window_reference_custody` (4),
  `test_r0_dispositions` (3), `test_external_volume` (22),
  `test_ssd_qualification` (19), `test_protocol_v4_doc` (5);
  `tests.test_align_pilot_session` (16).
- `JW_WP22_FULL=1 tests.align.test_v4_w1_synthetic`: **Ran 18 tests in
  118.2 s, OK (expected failures=1)**; only F3 remains an expected failure.
- night and host: `test_night_gate` (112), `test_arm_retry` (36),
  `test_night_plan_writer` (10), `test_network_time_off` (15), `test_b5_driver`,
  `test_b5_driver_p2` (46), `test_launch_window` (39), `test_environment` (34),
  `test_doctor` (9), `test_controller_hazard_flags` (58), `test_experiment`
  (39), `test_reduce` (134), `test_p2_ctl_guard_probe` (8),
  `test_window_lineage` (52), `test_collector_analysis_manifest_id`,
  `test_hazard_whole_window_verdict` (21), `tests.hazards.test_refusal_allowlist`
  (23, 1 skipped; the new sites are listed), `tests.hazards.test_import_graph`
  (6), `test_docs_freshness` (31), `test_window_env_allowlist` (4).

`tests.test_run_night`: head **Ran 301 tests, failures=14**; the base
`a2193446d` in the same environment, same hour: **Ran 294 tests,
failures=15**. Twelve failures are common to both: eight installer tests ("test
interpreter must load the battery fixture in child Pythons") and four
bind-supervision timing tests. The rest differ run to run: on the head
`test_signalled_child_cannot_hold_cleanup_past_budget` and
`test_pre_send_local_timeout_and_late_global_expiry`; on the base three other
supervision timing tests. Rerun alone, alternating head and base,
`test_signalled_child...` failed on both (its bound is 1.05 s; observed 1.05-1.08 s
on both) and `test_pre_send...` passed 2/2 on both. None of them reaches the new
admission code: the bind bench calls `bind_until_quiet` directly. The seven new
admission tests pass.

Kit: `scripts/align_v4_kit.py --check` reports no drift and exits 1 on the same
13 placeholders; `validate_align_v4_w1_plan.py` on the committed template still
refuses its PENDING_R1 placeholders; `git diff a2193446d HEAD --
configs/campaigns/align_pilot_v3` is empty.

## Round 4 integration (three lanes onto `a2193446d`)

Code and kit integration only: no measurement, no model weights, no v3 kit
bytes. Three `--no-ff` merges, in this order; each merge message records its
conflict resolutions.

| Merge | Lane @ head | What landed |
|---|---|---|
| `e72cc09fe` (1/3) | `lane/2026-11-06-v4-r1-wp15-runtime@f1864e314` | The WP15 R1 runtime (`joulewise/align/apple/r1_runtime.py`, `scripts/align_r1_runtime.py`, `configs/align/v4/r1_runtime.json`) behind the driver seam; `inputs.WP15.runtime_entrypoint` committed as an argv list; driver TERM → 20 s → KILL grace and the runtime's TERM obligations in the contract (closes cold pass MEDIUM-1); `battery_drain_pct_per_h` and the charge-resume SoC in the contract and `r1_slots.battery` (closes executing review MEDIUM-4); the argv rule written once in the contract (closes cold pass LOW-3). No conflicts. |
| `1c1a64557` (2/3) | `lane/2026-11-06-v4-r1-round4-fixes@0cdd1071b` | The round-4 fixes and decisions above (host power-mode admission, load-journal completeness, L1 on the record, kit-to-R1 evidence binding, G0-unreleased stop, arm records, ruling 20 census), protocol v4, the SSD census tooling. Conflicts in the contract doc, the driver's registration record, and two test modules: union of both sides (details in the merge message). |
| `d9c709ee5` (3/3) | `lane/2026-11-06-v4-w1-blockers@b2e60ebda` | W1 readiness: `w1_disk_gate` wired into `align_v4_session.py install` (`--w1-disk-config`), `sizing_b5.json` derived from the R1-filled `registration/w1_plan.json` (`kit.derive_sizing`), WP11 D identity inputs supplied, the R0 load reference (PR #686) and the off-Mac prequal runner. Conflicts in `align_v4_kit.py`, `align_v4_session.py` and `test_v4_kit.py`: union; the install order is `require_w1_ready` → round-4 `arm_checks` (+ `staging/v4-arm-NNN.json`) → `arm_powermode_check` → `w1_disk_check` (+ `staging/w1_disk_gate.json`) → shared installer. |

Generated files (`plan_tree.json`, `registration/identity_pins.json`) were
regenerated with `scripts/align_v4_kit.py` after merges 2 and 3. Rerunning the
generator on the final tree changes nothing (`git status` clean); the W1
template is unchanged.

### Kit check on the integrated head

- `git diff origin/lane/2026-11-05-align-pilot10-benign -- configs/campaigns/align_pilot_v3`
  is empty, against both the worktree and HEAD.
- `scripts/align_v4_kit.py --check`: no drift, **exit 1**, blocked on exactly
  nine leaves (WP11 and WP15 are now supplied, so 13 → 9):
  - `WP18.X.max_turns`, `WP18.X.token_fixture_sha256`, `WP18.Y.max_turns`,
    `WP18.Y.token_fixture_sha256`;
  - `R0.reasoning_effort`;
  - `R1.B_D`, `R1.I_D`, `R1.T_dead`, `R1.thermal_policy`.

  So `--check` does **not** yet block only on R0 and R1: the four WP18 leaves
  still block. They are Mac-side (the pilot-7 b-e25 / b-e18
  `align_turns.jsonl` and `p7-PILOT.json`, lead + magistrate) and cannot be
  derived off the Mac.
- Probe (scratch, committed inputs plus synthetic values): with WP18 filled,
  pending is `R0.reasoning_effort` + the four R1 leaves; with WP18 and R0
  filled, only the four R1 leaves; with every input filled and the committed
  `r1_slots.json`, `require_ready` refuses `R1 r1_slots must freeze AC
  powermode 0 or 2`; with an R1-driver-shaped hardware record it admits. So
  once WP18 and R0 are supplied the gate is fail-closed only on R1-measured
  values.
- `validate_align_v4_w1_plan.py` on the committed template refuses its
  `PENDING_R1` placeholders (B_D, I_D, T_dead, effort, max_r1_tail_s, the 18
  `member_s`, the thermal policy, plan_id, window_max_s).

### Suite tail (round 4 integration, code head `d9c709ee5`)

Every run used `/private/tmp/jwsol/venv-both/bin/python` under
`nice -n 19 taskpolicy -b`, `TMPDIR=/private/tmp/jwr4-tmp/integ`, one module
per process, three at a time, on a laptop also running a blinded analysis, a
GPU job and other sessions' tests (load average 15-19, so walls are about 3×
the earlier run's).

- **Whole `tests/align`, one module per process (113 modules):** every module
  rc=0, OK; **Ran 1455 tests, skipped=35** in total. Slowest walls:
  test_moe_calibration 7,570 s, test_moe_review 2,860 s,
  test_analysis_metadata_baseline 2,676 s, test_r0_mlx_native 1,035 s,
  test_analysis_budget_pilot 901 s.

  Selected module tails:
  ```
  test_r1_rehearsal         Ran 46 tests in 10.694s   OK
  test_r1_runtime_contract  Ran 9 tests in 0.008s     OK
  test_r1_runtime           Ran 12 tests in 111.031s  OK
  test_r1_runtime_e2e       Ran 2 tests in 139.999s   OK
  test_v4_kit               Ran 66 tests in 23.299s   OK
  test_v4_w1_plan           Ran 10 tests in 1.514s    OK
  test_v4_prequal           OK (skipped=3)
  test_protocol_v4_doc      Ran 5 tests in 1.358s     OK
  test_r0_mlx               Ran 7 tests in 0.868s     OK
  test_r0_mlx_native        Ran 1 test in 1031.094s   OK
  test_v4_w1_synthetic      Ran 18 tests in 6.485s    OK (skipped=14)
  ```
- **`JW_WP22_FULL=1 tests.align.test_v4_w1_synthetic`:** Ran 18 tests in
  238.940s, OK (expected failures=1). Only F3 remains expected; F2 passes.
- **`tests.test_align_pilot_session`:** Ran 16 tests in 663.745s, OK.
- **R1 exit-path harness:** the executing review's real-process harness was
  scratch and is not committed or present; its scenarios are covered by the
  committed zsh-chain tests in `test_r1_rehearsal` (signal burst restores
  Automatic, marker survives into the next night, sudo listing, inputs
  entrypoint), which passed above, and by `test_r1_runtime_e2e`'s TERM test
  (the runtime closes its custody before exit).
- Scratch probe of the full synthetic R1 through the runtime on this head:
  R1 rc 0, `status: complete`, every segment custody closed; the three gated D
  runs fail with X7 (see "Still open").

### Lead decisions in this round

- Recorded in protocol v4 and above: (a) the 30B JSON-path malformed call is
  tabulated, not excluded; (b) the refused XML call on D is flagged and
  tabulated, not excluded (chair ruling 2(d) asks for visibility only); the
  G0-unreleased stop and its disclosed cost (a G0-timeout X2 member has no
  capability score); run_night's power-mode admission also covers HAZARD_PACK
  nights.
- Integration calls made here: the merged install order above; `require_ready`
  keeps the round-4 signature `(inputs, r1_slots=None, *, synthetic=False)`;
  the W1 lane's `observe_powermode` hook is superseded by the round-4
  admission runner; the registration record is the union (`l1`,
  `max_r1_tail_s`, `external_volumes`, `battery`).

### Waiting on lead sign-off (from the WP15 builder; not decided here)

- `r1_slots` S1-S4 are finite step-response numbers (fast-key ΔT and t63,
  slow-key ΔT and τ); the key names and FD 2.6 class checks are in
  `slot_detail`. Either sign off on that mapping or change the `r1_slots`
  schema.
- A censored `t_decline` (S9 = observed decode length, `t_decline_censored`)
  when no decline occurs; missing PM clock support refuses.
- S6 = δ_slow until the lead applies the FD 2.6 S6 tuning after the gated
  runs; the runtime's T_dead is L1's first term and the kit applies
  `max_r1_tail_s`.
- The W1 launcher in `collection_plan` `runtime_requirements.launcher` is the
  R1 runtime argv; confirm that is the intended W1 launcher.

### Review findings closed by the combination

The WP15 lane did not touch the cold pass HIGH-1 or the executing review /
cold pass MEDIUMs; on the integrated head they are closed by one lane or the
other:

| Finding | Closed by |
|---|---|
| Cold pass HIGH-1 / executing HIGH-3 (powermode 2 survives a crash) | round-4 fixes: run_night admission restores the marker on every night class |
| Cold pass MEDIUM-1 (driver SIGKILLs the runtime, no TERM duty) | WP15: TERM → 20 s → KILL, runtime TERM obligations in the contract |
| Cold pass MEDIUM-2 (blind G1 after unreleased G0) | round-4 fixes: `episode.g0_unreleased` stop |
| Cold pass MEDIUM-3 (JSON malformed / refused XML) | lead decisions (a) and (b) |
| Cold pass MEDIUM-4 (protocol v4 not on head) | round-4 fixes: protocol v4 merged and reconciled |
| Cold pass MEDIUM-5 (arm records nothing) | round-4 fixes: `staging/v4-arm-NNN.json` |
| Cold pass LOW-3 (argv is one executable) | WP15: the argv rule is stated once in the contract |
| Executing MEDIUM-1, -2, -3, -5 | round-4 fixes (journal completeness, L1 on record, evidence binding, volume census) |
| Executing MEDIUM-4 (battery outputs) | WP15: `battery_drain_pct_per_h`, `r1_slots.battery` |

So the round-4 "Still open" list above is superseded for cold pass MEDIUM-1,
executing MEDIUM-4 and cold pass LOW-3.

### Still open after the integration

- On the synthetic world the three gated D runs end in X7 (H ≈ 250 s and
  decode ≈ 850 s against T_dead 1,262 s), so the synthetic duty bar fails
  (probe on this head, R1 rc 0). The synthetic world's timings are not
  hardware, but this is the same shape as WP22 F2 and stays open under
  ruling 1's duty bar and fallback order until R1 measures it.
- The designed start states (ruling 6) use a proportional MLX heater child
  (`ProcessHeater`) that has run only on the synthetic world: it needs a
  hardware check on the measurement Mac (the driver refuses any release
  outside the band).
- `calibration-pre`/`-post` record a read-only host snapshot only; the meter
  calibration comes from the R1 night plan's scaffold. `harvest` writes a
  SHA-256 manifest; it does not run `harvest_b6_session`.
- Executing review LOWs 1-3 (A-B-A leg wait bound assumes 1,800 + 600 s;
  `t_decline_s: true` accepted as 1 s; "A legs infinite, B finite" reported
  inconclusive where ruling 16 reads not-adopt).
- Protocol v4's blind Fable + Opus cold gate before W1 arm is still owed.
- W1 items: ruling 9 changes in `deciding_experiment`; the count-level
  full-omission variant; `sizing_b5.json` exists only once the R1-filled
  `registration/w1_plan.json` is committed (prepare refuses with the
  FINAL-DESIGN B8 reason until then); install needs `--w1-disk-config`
  pointing at the Mac's R0 desk config, whose offloads list must name the
  pilots 8-10 offload receipts (chair ruling 20); the disk gate reruns on every
  install call (read-only); one live sibling prequal run on the Air for the
  sibling load check (tested with fakes only); the sibling 0.4669 reference
  takes upstream `Qwen/Qwen3.5-0.8B` main head `2fc06364` as its basis.
- `tests.test_run_night`: 12 failures also present on base `a2193446d` on this
  laptop (eight installer battery-fixture tests, four bind-supervision timing
  tests), not caused by these lanes.

### What still blocks arming R1

1. **R0 passing on the Mac**: `inputs.R0.reasoning_effort`, and R0's SMC sensor
   selection in `configs/align/v4/r1_runtime.json` (`"sensors": "PENDING_R0"`);
   then regenerate the kit. The runtime refuses (exit 2) until both are set.
2. **WP18 (Mac-side, lead + magistrate)**: the R1 X-G contrast run needs
   `WP18.X.max_turns` in the generated x-g template (the runtime refuses with
   "x-g template carries a PENDING WP18 X max_turns"), so WP18 X must be
   supplied and the kit regenerated before R1, not only before W1.
3. **Ed-visible items**: the lead sign-offs listed above (S1-S4 mapping, S6,
   W1 launcher); the R1 night plan (`MEASUREMENT_ROOT`, `NIGHT_DIR`, the two
   `sudo -n pmset -c powermode 0|2` rules, avoiding 11:45-13:15); the
   hardware check of the heater start-state loop on the first R1 night.

## Round 5 integration (two lanes onto `54e844b87`)

This is code and kit integration only. No measurement ran, no model weights were loaded and no v3 kit bytes changed. The rulings are recorded verbatim, with the commits that implemented each one, in `docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md`. There were two `--no-ff` merges, in this order:

| Merge | Lane @ head | What landed |
|---|---|---|
| `e3e52ce5a` (1/2) | `lane/2026-11-06-v4-r1-round5-science@e8bfd4ed5` | R5-1 (gated runs and X-G consume the soak R; bounded cool-to-band precool; a timeout is INCONCLUSIVE), R5-2 (planning deadman armed after preheat + G0; start states warmest first), R5-3 (a leg without its own G0 release is INCONCLUSIVE), R5-5 (A-B-A before step-d; slots under the adopted series mode; full-inventory journals; 600 s recovery; thermometry bar in the kit), R5-7 (S6 TODO; member 5 captures and the others consume). No conflicts. |
| `e7aec1ea9` (2/2) | `lane/2026-11-06-v4-r1-round5-infra@70986d5c9` | R5-4 (no unbudgeted gated D; the kit binds B_D and the thermal policy and asserts ruling 1(f)), R5-6 (W1 under an adopted High Power), R5-8 (`scripts/align_v4_wp18_fixtures.py`), R5-9 (Sol F2/F3, `Segment.close`, sizing provenance, hf_pins bytes), R5-10 (the LOW set). Conflicts in the driver, runtime, synthetic stand-in, contract doc, three test modules and two generated files. |

Conflict resolutions (full list in the `e7aec1ea9` message):

- **Driver run loop.** The science lane moved the A-B-A legs into the phase loop, before step-d (R5-5). The infra lane's standalone A-B-A block after the loop is dropped. Science's `aba_adoption` handles the release timeout and R5-3, and it calls infra's stricter `high_power_adoption`. After step-d, the driver checks in this order:
  1. the member powermode (science);
  2. the soak-reference consumption (science);
  3. `_check_step_d` (infra).

  The registration record is the union: `thermometry`, `s6_tuning` and `x_g` from science, `budget_fit_inputs` from infra.
- **A-B-A batch-window bound (an integration decision).** Infra's `aba_leg_bound_s` read step-d's I_D. Under the R5-5 order step-d has not run when the legs start, so every night would have refused at A1. The bound now uses `ABA_LEG_I_D_BOUND_S = 1750`, the largest I_D the runtime admits:

      65 + 600 + 1750 + 1.13544 × 1580 + 120 ≈ 4,329 s

  The legs keep G0-entry arming (no re-arm), so the formula still holds. A larger bound only waits longer for the 11:45-13:15 window. The infra test now asserts this value and that the legs precede step-d. With the infra function, the run refuses at A1, so the test fails.
- **`Segment.close`.** The science lane's `stop_inventory` was caught with `except Exception`. A TERM there would have skipped every session close (powermetrics included) and the journals, against R5-9. It is widened to BaseException. The extended close test fails without this (`SystemExit: 143`).
- **Test fixtures, made consistent with the other lane:**
  - Science's soak-reference runtime test writes the step-d complete custody, which F3 requires.
  - Science's precool-timeout test fills `inputs.R1.thermal_policy` from the slots (R5-4), so that only the duty bar refuses.
  - Infra's close test sets the inventory attributes.
  - The FakeWorld, `r1_record` and WP22 r1_slots stand-ins are unions.
- **Generated files.** `plan_tree.json` and `identity_pins.json` were regenerated with `scripts/align_v4_kit.py`. `validate_align_v4_w1_plan.py --regenerate-template` leaves the template unchanged. Rerunning the generator changes nothing.

### Kit check on the round-5 head

- `git diff origin/lane/2026-11-05-align-pilot10-benign -- configs/campaigns/align_pilot_v3` is empty, both against HEAD and against the worktree.
- `scripts/align_v4_kit.py --check` reports no drift and exits **1**. It is blocked on exactly nine leaves, the same set as in round 4:
  - `WP18.X.max_turns`, `WP18.X.token_fixture_sha256`, `WP18.Y.max_turns`, `WP18.Y.token_fixture_sha256`. These clear once the magistrate runs `scripts/align_v4_wp18_fixtures.py` on the Mac and commits its outputs (kit-delivery note in the infra run report).
  - `R0.reasoning_effort`.
  - `R1.B_D`, `R1.I_D`, `R1.T_dead`, `R1.thermal_policy`.

  After WP18, the leaves left are R0 and R1 only. Beyond the leaves, `require_ready` now also needs:
  - an r1_slots record whose slots were measured under the adopted mode;
  - a passing thermometry bar;
  - `inputs.R1.B_D` ≤ `slots.B_D`;
  - a thermal policy equal to N_chunk/S6/S7;
  - ruling 1(f) fitting T_dead.

  `require_w1_ready` also needs both WP18 fixture files.
- `validate_align_v4_w1_plan.py` on the committed template still refuses its `PENDING_R1` placeholders.

### Suite tail (round 5 integration, code head `e7aec1ea9`)

Every run used `/private/tmp/jwsol/venv-both/bin/python -B` under `nice -n 19 taskpolicy -b`, one module per process. `xargs -P 3` ran three at a time, the slowest modules first, with a per-module `TMPDIR` under `/private/tmp/jwr5-tmp/suite`. The commits after `e7aec1ea9` are docs only.

- **Whole `tests/align`, one module per process (115 modules):** every module rc=0, OK. In total, **Ran 1534 tests, skipped=27**. Slowest walls:
  - test_moe_calibration 3,348 s;
  - test_moe_review 991 s;
  - test_analysis_metadata_baseline 831 s;
  - test_r0_mlx_native 522 s;
  - test_analysis_budget_pilot 515 s.

  Selected module tails:
  ```
  test_r1_rehearsal         Ran 62 tests in 9.325s    OK
  test_r1_runtime           Ran 31 tests in 58.277s   OK
  test_r1_runtime_e2e       Ran 2 tests in 74.707s    OK
  test_r1_runtime_contract  Ran 9 tests in 0.005s     OK
  test_r1_inventory         Ran 11 tests in 0.953s    OK
  test_v4_kit               Ran 87 tests in 11.072s   OK
  test_v4_wp18_fixtures     Ran 11 tests in 0.178s    OK
  test_v4_w1_plan           Ran 10 tests in 0.855s    OK
  test_v4_prequal           Ran 33 tests in 5.885s    OK (skipped=3)
  test_v4_powermode_record  Ran 9 tests in 0.352s     OK
  test_external_volume      Ran 23 tests in 0.024s    OK
  test_protocol_v4_doc      Ran 5 tests in 0.613s     OK
  test_r0_mlx_native        Ran 1 test in 520.330s    OK
  test_v4_w1_synthetic      Ran 18 tests in 3.436s    OK (skipped=14)   # full windows gated by JW_WP22_FULL
  ```
- **`JW_WP22_FULL=1 tests.align.test_v4_w1_synthetic` (the WP22 synthetic W1 dry run):** Ran 18 tests in 217.342s, OK (expected failures=1). Only F3 is expected to fail, as in round 4.
- **`tests.test_align_pilot_session`:** Ran 16 tests in 369.915s, OK.
- `tests.test_run_night` and the other non-align modules the infra lane touched were not rerun here. The infra lane's report has their tails on its head, and the merge did not touch those files.

### Open after round 5 (for the lead)

- **R5-1 design point.** A gated run's G0 starts from the soak band, but W1's D-after-D G0 follows only the 300 s inter-member idle. The duty bar's G0 share may be lower than W1 will see. The alternative is a fixed 300 s idle before each gated run instead of cool-to-band.
- **Ruling 1(f) will likely bind on hardware.** At about 11 tok/s, (6,144 + 4,096)/11 ≈ 930 s against T_dead ≈ 1,200-1,280 s, which leaves about 270-350 s for worst G0 + (G1 + H) + prefill + tool. A non-fit refuses W1 and names the largest fitting B_D. The lead then needs either ruling 1(e)'s fallback order or a ruling on the "last admitted turn" term.
- **Classification digest not bound.** Protocol v4 asks WP16 to bind `thermometry.D.classification_sha256` into the frozen inputs. No lane does yet: the kit checks the lists, the bar and the pick verification, but not that `inputs.R1.thermal_policy` carries the digest.
- **Inventory journal on hardware.** Coverage can fail closed if a T*/F* sweep takes more than about 200 ms. A second SMC reader runs beside the sidecar during the steps, which is untested on hardware. Check the sweep durations in `inventory/inventory_journal.jsonl` on the first R1 night.
- **Changed-pick S7.** It uses the quiet-window median as R, not the soak. The lead's verification should confirm this.
- **`cooldown_after_30b` (600 s).** It is kept, although step-30b now ends with a 600 s recovery. Dropping it would save 600 s per night.
- **S6 tuning record.** The science `s6_tuning` TODO record is not the kit's tuning receipt. A tuning must record `{authority, from_c = S5, to_c = S6 ≤ 2.0}`.
- **W1 High Power marker.** If `run_night` is SIGKILLed on a W1 High Power night, the next night refuses on the mode alone (fails closed), and a manual `sudo -n pmset -c powermode 0` is needed.
- **Inconclusive scope.** Only an A-B-A leg whose own G0 did not release is INCONCLUSIVE. Other incomplete legs still refuse R1.
- **LOWs left, with reasons.** These are listed in `LEAD-RULINGS-2.md` under R5-10. The round-3 `recovery_curve` row-shape check is still open: neither lane added it.
- **Integration slip.** On this run the first suite launcher's concurrency cap did not work: `jobs` inside a command substitution sees no jobs. About 115 test modules started at once for roughly two minutes, and the load average reached about 48. I stopped them by process tree and by cwd; neither protected process (61827, 89849) was touched. I then reran the whole suite under `xargs -P 3`. Every tail below comes from that rerun.
