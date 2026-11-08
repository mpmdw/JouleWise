# ALIGN v4 registration package: Opus cold cross-family review

Reviewer: Claude Opus 5.5, cold and cross-family (the package was built by Sol 6.1,
reviewed by two Sol seats and fixed by Claude Sonnet 5.5).
Candidate: `origin/align/2026-11-08-v4-r11` @ `353446ad6`.
Scope: `git diff d600baba0..353446ad6` (56 files, +5,659/-386). Earlier history keeps its own gates.
Authority: `origin/main:RUN_STATE.md` items 203, 204, 209, 210, 212, 214-216;
`AGREEMENT-FINAL.md` Track 1 (`align/2026-11-07-squeeze-agreement-final`);
`r11-dispositions.md`; Sol reviews `r11-review-sol{1,2}.md`.
Blinding: no restricted, night-custody, night-archive or `jw-b5-*` path was opened.
No R0, R1 or W1 record, outcome, score or energy value was read.
Everything run here was synthetic, with no MLX.

## Verdict: ADMIT_WITH_FIXES

Science fidelity holds. Nothing in the stack changes the registered estimand (the
GPU-rail residual), the R14 rank or threshold, the roster or calibration counts,
or the SECONDARY, print-only status of the KM003C DC-in channel. No outcome reaches
any gating predicate. The Sonnet fixes are correct as specified.

There is one HIGH. The protocol requires the WP22 synthetic W1 dry run before
registration. That dry run passed at the R10 baseline and is red at the head, and
CI cannot see it. There are four MEDs:

- receipt brittleness;
- a triage list that has no input for a lead ruling or a remedy;
- top-up evidence that is undefined under back-to-back cadence;
- DC sabotage residuals printed before the v5 addendum is registered.

**Fix before the receipt is generated:** HIGH-1 and MED-2. Both touch files the
receipt binds, so fixing them after registration costs a full re-registration. The
other findings are recommended.

## Tests run (one module per process, `python3.13 -B -m unittest`)

All of these modules pass at `353446ad6`:

| Module | Tests |
|---|---|
| test_v4_r11 | 27 |
| test_v4_registration | 20 |
| test_v4_kit | 116 |
| test_w1_kit_r10 | 30 |
| test_v4_estimands | 15 |
| test_thermal_desk | 25 |
| test_v4_w1_synthetic | 18 (14 skipped) |
| test_km003c | 16 |
| test_v4_cadence | 19 |
| test_v4_executed_closure | 2 |
| test_r1_rehearsal | 74 |
| test_r1_round7_science | 18 |
| test_r1_round6_power | 25 |
| test_protocol_v4_doc | 6 |
| test_r11_review_sol1_witnesses | 5 |
| test_r11_review_sol2 | 4 |
| test_window_reference_custody | 5 |
| test_pilot3_cache | 13 |
| test_r1_round8_exec_review | 7 |

The exception is the full window. `JW_WP22_FULL=1 test_v4_w1_synthetic` gives
FAILED (errors=2) at `353446ad6` and FAILED (failures=1, errors=11) at
`199006f16`. At `d600baba0` it is **OK** (1 expected failure). See HIGH-1.

## Findings

### HIGH-1: the WP22 synthetic W1 dry run is red at the head, and CI cannot see it

`pilot_protocol_v4.md:1053-1054` makes "WP22's synthetic W1 dry run" a
pre-registration requirement. At the head the run fails in two stacked places.
Both were introduced by Sol's commits in scope, and the Sonnet round did not touch
either.

- **(a) A stale contrast fixture (`7895b9e7e`).**
  - `scripts/align_v4_w1_synthetic.py:99-100` computes `contrast_fit` at import for
    WP18 X `max_turns=5`.
  - `collect` then re-measures the X turn count from the synthetic pilot-7
    reference and rewrites `inputs['WP18']` (`:260`) before `build_kit` (`:263`).
  - The kit therefore refuses at `scripts/align_v4_kit.py:942` ("R11
    contrast_fit/contrast_g0_cap_s must bind ...").
  - `KitBridgeTests` stays green only because it builds from the import-time
    inputs.
- **(b) The desk aborts on a PENDING U3 (`659cea924`).**
  - Recomputing the contrast after the WP18 update clears (a). The run then gets
    to the desk and crashes with `ValueError: v4 desk requires registered
    u3_bar.json`.
  - The cause is `scripts/align_v4_thermal_desk.py:21-29`.
    `registration_evidence` calls `v4_registration.validate_u3`, which raises
    unconditionally (`v4_registration.py:375-379`).
  - The session desk takes the same route. It returns at
    `align_v4_session.py:169-173` with only `v4_registration_evidence: False`,
    before computing U1/U2, the contrast, the cohort or the B diagnostics.
  - Meanwhile `acceptance()` already turns a pending bar into U3 `inconclusive`
    (`thermal_desk.py` `identical_pair` with `u3_margin`). So the abort is
    stricter than the desk it guards.

**Failure scenario.**

- The registration gate admits a package whose new desk wiring has never run end
  to end. That wiring covers the U6 v4 route, contrast delivery and the stage
  term, cohort identity, the B bar, the KM003C session report and the
  registration diagnostics.
- The four full-window classes skip unless `JW_WP22_FULL=1`
  (`tests/align/test_v4_w1_synthetic.py:100`), so CI and both Sol seats saw the
  module as OK.

**Fix.**

- Recompute `contrast_fit` in `collect` after the WP18 update.
- Do one of the following:
  - let the desk take a PENDING U3 as a U3-inconclusive input (arm stays refused
    through `require_registration`);
  - give the dry run an explicit synthetic U3 seam.
- Add the `JW_WP22_FULL=1` run to the Stage A gate checklist.

**Witness.** `tests/align/test_v4_opus_cold_witnesses.py` runs a minimal dry run
(`--inject none --members 5`, about 4 s). It fails at `353446ad6` and passes at
`d600baba0`.

### MED-1: the executed-closure receipt makes any later fix a full re-registration

`v4_registration.ARTIFACTS` binds 221 paths, 188 of them from the static closure.
These include 40 `joulewise/b5`/`b6` modules, the mock adapters, `cli.py` and
`doctor.py`.

- `validate_receipt` (`v4_registration.py:315-327`) requires current working bytes
  to equal the receipt digests for every one of them.
- `require_w1_ready` runs it on every install, through
  `kit.generate(check=True)`.
- On `origin/main`, 41 commits touched these paths in the last 14 days and 98 in
  the last 30.

**Failure scenario.**

1. W1 refuses at quiet admission because of an infrastructure bug, say in
   `joulewise/b6/idle_wait.py`.
2. The magistrate fixes it in place (memory: "frozen is not sacred").
3. Every later W1 arm now refuses until there is a new receipt, with a lead
   signature and two fresh blind ADMIT gate reports.

R12 B2 assumes the opposite. Its `code_or_config_changed` path to a full desk gate
(`v4_cadence.py:61-64`, protocol "R12 B2") treats a code change between windows as
routine. The closure is correct about what executes. The cost is
disproportionate for files that bear no science.

**Fix.** Use two tiers.

- **Strict tier: re-registration on change.** The protocol, deviations,
  estimands, desk, kit, registration inputs and the episode path (endpoint,
  sampling, generation, `prompt_cache`).
- **Amendment tier: the rest of the closure.** A change is admitted through a
  lead-signed amendment row in the receipt (path, old and new blob, reason,
  deviation-log entry). `validate_receipt` verifies the row, and the R12
  full-desk gate runs.

### MED-2: the frozen triage has no input for a lead ruling or a remedy

These two failures can stop the series for good.

**(a) The `escalate_to_lead` deadlock.**

- After two consecutive zero-capture refusals, `calibration_stop` returns
  `escalate_to_lead` (`v4_cadence.py:223-224`) on every later evaluation.
- No row type records the lead's ruling, so a "re-arm" ruling still refuses.
- The only ways forward are to drop rows from the packet (an unrecorded
  deviation) or to change code. The code is receipt-bound (MED-1).

**(b) `meter_samples_clock` is phrased as a data predicate over the previous window.**

- The check reads "KM003C samples present and clock coverage for every member"
  (`v4_cadence.py:39-40`, protocol table "R12 B2"). It is not a tabulation, unlike
  `capture_faults` and `member_eligibility`.
- `km003c.capture_member` treats any dropped counter or restart inside a member as
  missing (`km003c.py:92`).
- One dropout makes an honest packet `fail`. The previous window cannot change
  until an arm succeeds, so every later arm refuses. This includes **W1 behind R1**:
  `first_window_na=False`, and R1 runs with the meter through HAZARD_PACK.
- So a SECONDARY channel can halt v4. That contradicts the protocol ("Missing
  coverage or one dropped counter makes that member's DC channel missing and never
  changes powermetrics eligibility").

**Fix.**

- Add a `lead_ruling` row, carrying a ruling id, that `calibration_stop` consumes
  to reset the trailing zero-capture count.
- Reword the meter check: the previous window's coverage is tabulated with gaps
  listed, and the meter is verified live before this arm.

Make both changes before the receipt is generated.

### MED-3: under B1 cadence, the 1800 s top-up evidence is either friction or fiction

The 1800 s hard bound (`v4_registration.py:388-425`) is applied to a free operator
timestamp, `--topup-completed-at` with `--topup-source`
(`align_v4_session.py:276-278`, `:582`).

- With OBC off on AC, the battery floats at 100% between windows.
- The only "completion" event is the end of the post-window recharge. That event
  comes before the cool-down (about 15-25 min), the record push and the
  off-MBP triage.

**Failure scenario.** The magistrate faces two bad options:

- cite the true completion time, which is often more than 30 min before the arm,
  so the arm refuses and no remedy exists short of discharging the battery;
- cite "now" with the source "floating at 100%", in which case the rule checks
  nothing.

The protocol (`pilot_protocol_v4.md:603-617`) does not say which source counts.

**Fix.** The bound stays at 1800 s. The lead defines the admissible evidence: a
scripted pre-arm ioreg/`pmset -g log` sample showing a completed charge, or
continuous float (≥99%, not charging) since the last charge. Its timestamp is the
latest qualifying observation. The arm reads it from the script, not from a hand
entry.

### MED-4: v5 blinding: per-member DC residuals of sabotage members are printed at every desk

- `align_v4_session.py:155-161` prints `dc_in_residual_j` for every plan member.
  That includes W1's sabotage D members (ordinals 11 and 14) and, in D windows,
  2 sabotage per calibration window.
- The protocol (`:745-750`) makes the whole-member DC-in integral the squeeze's
  authority for small effects. It seals transcripts until the v5 addendum
  registers, and the v5 design competition is running now.
- The Sol seats read R11-3 as authorizing the print, which is correct for v4. They
  did not weigh v5.

**Failure scenario.** The v5 designers see the DC sabotage effect of interest
before the v5 endpoint and threshold are frozen.

**Fix.**

- Print DC status, coverage and integrals for every member, and the DC residual
  for benign members only.
- Seal sabotage-member DC rows (hash only) until v5 registration.

The shared pilot desk's pre-existing GPU-residual print for sabotage members in
calibration windows is a separate call for the lead.

### LOW

- **L1.** `backfill_turn_counts` (`align_w1_budget_procedure.py:234-272`) binds the
  sha of a hand-made export, which is self-referential. Nothing checks it against
  the R1 bundle bytes. Add a small extractor that reads each gated run's
  `outputs/align_turns.jsonl` and records the bundle file digests. Then the lead
  does not transcribe counts by hand.
- **L2.** The arm record keeps the triage evaluation, not the packet
  (`align_v4_session.py:312`). The `calibration_windows` rows are lost, yet the
  protocol says "the arm retains it". Store the packet bytes and their sha.
- **L3.** The triage packet is not bound to the committed record of the previous
  window. Add `record_commit` and check it exists, as B1 requires: arm "from the
  committed record".
- **L4.** U6's trajectory-clustered SE is CR0 with z = 1.645
  (`v4_estimands.py:194-228`). With about 14 trajectories per D window this is
  anti-conservative, so "imprecise" comes up less often. U6 is reported and does
  not gate (`protocol:504`). Consider CR1 with t(G-1).
- **L5.** `powermode_desk_check` hardcodes `window='W1'`
  (`align_v4_session.py:186`). That is correct today, but it would mislabel D
  windows if reused before the D kit lands.
- **L6.** The closure walker follows imports only. Scripts launched as subprocesses
  are unbound: `scripts/launch_window.py`, and `scripts/km003c_monitor.py` with
  `joulewise/external/km003c_usb.py`.
- **L7.** There is no template or builder for the triage packet, so the headless
  magistrate hand-writes 11 checks as JSON. Add an `--emit-triage-template`.
- **L8.** A nonzero exit from `pmset -g batt` refuses the arm
  (`align_v4_session.py:289`), although the ioreg predicate already decides. Keep
  it as retained evidence and do not gate on it (proportionality).
- **L9.** `subturn_h_star` accepts bool scores (`float(True)`). Off-grid actual doses
  leave H* undefined. This is documented and correct under the "exact" rule. Note
  it in the desk text.

## Focus answers

**1. Science fidelity.**

- **Estimand.** The GPU-rail residual is untouched (`energy_residual.py` and
  `pilot_analysis.py` are unchanged; the legacy note is added in
  `energy_residual.md`).
- **Rank and threshold.** `calibration_cutoff` uses exact `Fraction` ranks.
  - At m=39, alpha .05 gives rank 38 with a bound of 2/40, and .025 gives rank 39
    (the maximum) with 1/40.
  - The alarm uses strict `>`.
  - `conformal_threshold_diagnostics` defaults to the maximum.
  - The public `energy-tripwire.html` matches.
- **B3 counts.** It reads only status and counts: 7 per pair per window, 39 per
  pair, minimum 6, cap 8, every eligible member in the prefix. No residual, score
  or energy value enters.
- **Exclusions.** The only new exclusions are the named B
  (`battery.member_span`, chair 4) and D-14b-1. D-14b-1 refuses consumers when the
  reference is lost; those members were X4-excluded anyway, so eligibility does
  not change.
- **KM003C.**
  - Every DC path is inside a broad `except`.
  - It never enters `checks`.
  - It is labelled SECONDARY and `print_only`.
  - `require_enabled` gates only the plan declaration.
- **Leakage.** I found no outcome leakage into gates. MED-4 is a v5-blinding
  matter, not a v4 estimand change.

**2. The Sonnet fixes.** All are correct as specified. Each line gives the change,
then the finding it carries, if any.

- **U6 v4 route.** It uses ±0.5 s_r, (pair, trajectory) clusters, chronological
  halves within pair, position means evaluable at ≥6 trajectories and no slope
  gate. `acceptance(v4)` refuses legacy-shaped U6. Finding: L4.
- **1800 s top-up.** It refuses missing, future or stale evidence. Finding: MED-3,
  which is about the evidence definition, not the code.
- **H\*.** It is strict `>`, refuses non-integer, duplicate and non-finite rows,
  leaves a missing earlier grid dose undefined and reports off-grid doses.
- **Receipt binding.** The batched `cat-file` parse handles missing objects. The
  closure test recomputes the closure. Finding: MED-1, with L6 for its limits.
- **WP19 zero-turn.** A zero-turn run gives `fail` + INCONCLUSIVE only, never pass
  or complete.
- **Triage.** The list has 14 entries, `arm_checks` supplies the three
  arm-computed ones, and a self-supplied ARM id refuses. Finding: MED-2.
- **`calibration_stop`.** It matches RUN_STATE 216: zero-capture windows are not
  counted, `pending` applies from 6, the cap is 8, the outcome is
  `insufficient_calibration`, and an over-run history raises. Finding: MED-2(a).
- **R1 sizing.** 56,206.96 + (5,763.9952 + 5,400) = 67,370.96 (ceil 67,371), and
  + 29,055.98 = 96,426.94 (ceil 96,427). Both are stated as floors, which is
  correct. A night over 24 h meets two blackouts by construction, which "size from
  the installed plan" covers.
- **`backfill-turn-counts`.** It never overwrites, and the sum and length are
  cross-checked against the driver row. Finding: L1.

**3. Operability.**

- **W1.** W1 cannot arm on this kit, by design. These items must all land first:
  1. a U3 derivation and code (`validate_u3` is unconditional);
  2. the signed receipt with Stage A/B ADMIT reports;
  3. the WP19 receipt from the native X-G;
  4. the R1 inputs, with:
     - `backfill-x-g` and `backfill-turn-counts`;
     - `R0.record_sha256` equal to `sensors.r0_sha256`;
     - a passing duty bar, where a fail now means an R1 re-run with no fallback
       step (R08);
     - ≥3 turns admitted at B_D;
  5. a lead-signed offload freshness policy and the by-day receipt;
  6. the triage packet, top-up evidence and OBC attestation;
  7. the B3 simulation, the C/T manifest, the U5 consequence and the margin.
- **D1.** D1 also needs the B window consequence (`v4_B_bar` is always False, so
  the full desk cannot pass after W1), Ed's charge hold and a D kit.
- **R1's record.** Nothing in it is unrecoverable, provided custody keeps
  `r1_result.json` and each gated run's `outputs/align_turns.jsonl`. The
  `x7`/`admitted_turns` fields are already on the lane rows. The strand risk is
  MED-2(b): any KM003C gap in R1 blocks W1's triage.
- **Proportionality.** MED-1, MED-3 and L8 add friction without protecting
  blinding or prereg fidelity in their current form. The registration receipt,
  U3 stop, WP19 non-veto, B3 counts-only stop and the triage itself do protect
  them, and should stay.
