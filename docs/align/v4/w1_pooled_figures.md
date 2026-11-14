# W1 pooled figures before release (RL-152 §3.2)

**Rule (RL-152 §3.2).** Before release, W1 prints no figure pooled over a set that contains a non-benign
member if any member-level term of that figure is printed for any member of the set. A figure is either
benign-only and labelled so, or one verdict line computed in memory.

**W1's non-benign members** are anchors 2 and 3, contrast template X (6, 9, 13, 16) and D 11 and 14
(roster `scripts/align_v4_kit.py:63-82`). They are read from the plan's `condition`, and an unknown
condition counts as non-benign.

**Scope.** Every pooled figure the W1 desk prints or records before release is listed here, with its population:

- stdout of `scripts/align_v4_session.py desk` and of the common `align_pilot_session` desk on a v4 session
- `PILOT.json`
- `desk.json`
- the harvest-off light-triage record (`cmd_triage --out`)
- the standalone `scripts/align_v4_thermal_desk.py` outputs

The switch is `W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES = True` (RL-149 §3(a)).

**Code.** All references are to `joulewise/align/apple/v4_desk_seal.py` unless the row names another file.
`_seal_pilot_w1` and `_seal_extra_w1` start from the full PILOT, so the table also lists the figures they pass
through unchanged.

| Figure (where) | Population printed | Form | Code |
|---|---|---|---|
| `checks` (all instrument checks; stdout `name: pass/fail`; `desk.json`) | all members | verdict (one boolean each, computed in memory) | common desk `instrument_checks`, `powermode_desk_check` |
| `status` / `pilot_status`, `full_desk_gate` | all members | verdict | common desk; `align_v4_session.desk` |
| `carve_out_flag_counts` | **benign** (`over: benign members only`) | count, labelled | `_benign_counts` |
| `residual_analysis[*].scopes[*][*].s_r_j`, `s_r_df`, `cell_residual_counts` | **benign** (`s_r_population: benign`) | recomputed over benign residuals | `_seal_residual_rows` |
| `residual_analysis[*]...distinct_trajectories`, `benign_distinct_trajectories` | all / benign | eligibility counts; equal to `len(representatives)`, which is printed per member, so no withheld term | pass-through |
| `residual_analysis[*]...model`, `e_j_per_decode_token`, `mean_context_tokens`, `grouped_threshold`, fit `flags` | benign (the fit trains on benign members only) | as registered | `pilot_analysis.residual_analysis` |
| `residual_analysis[*]...tamper_detection_curve` | sabotage only | withheld | `_seal_residual_rows` |
| `I4_prime` cells | cells holding a non-benign member: withheld whole; benign cells as recorded | withheld / per cell | `_seal_pilot_w1` |
| `repeat_token_identity` cells | cells holding a non-benign member: withheld | withheld / per cell | `_seal_pilot_w1` |
| `raw_within_cell_energy_sd`, `repeat_energy_spread` cells | cells holding a non-benign member: withheld | withheld / per cell | `_seal_pilot_w1` |
| `episode_scope_alternative_*` | per member (eligibility); non-benign reasons as allowlisted codes | not pooled | `_seal_pilot_w1` |
| `extra_checks.d_member_x2.x2_count`, `x2_rate`, `g0_timeout_x2_count` | **benign** D members (`pool: benign D members only`) | count and rate, labelled | `_seal_x2` |
| `extra_checks.d_member_x2.d_members`, `read`, `unread` | all D members | roster and readability; `unread` is per member, so no withheld term | pass-through |
| `extra_checks.w1_g1_tripwire` (RL-149 §1.5), stdout `W1 D G1 timeout tripwire …` | all six D members | verdict line only (`within` / `to the research lead`) | `w1_g1_tripwire` |
| `extra_checks.w1_non_benign_tool_path`, stdout `W1 non-benign tool path (RL-152 section 3.4): …` | non-benign members | verdict line only | `tripwires` |
| `extra_checks.unlisted_flag_codes`, stdout `W1 unlisted flag codes (RL-152 section 3.4): …` | **benign** count; non-benign `none` / `present, to the research lead` | count, labelled, plus a verdict | `tripwires` |
| `extra_checks.thermal.model_windows[*].U1` | all gated members | verdict only (its all-member counts are withheld) | `seal_thermal` |
| `extra_checks.thermal.model_windows[*].U2` (`g0_slow_range_c`) | all gated members | exception class (RL-149 §3(a), RL-151 §4.4: G0 readings precede the first token), as registered | pass-through |
| `extra_checks.thermal.model_windows[*].U3` pairs, U4-U6, `hardware_control`, `consequence` | identical-work pairs; U4-U6 unevaluable in W1 | exception class, as registered | pass-through |
| `extra_checks.thermal.deciding_experiment` (d_X, d_Y, δ, CI, df, same-arm pairs, per-turn arm-mean differences, delivery) | X and Y contrast members | exception class, as registered (statistics only, no member value) | pass-through |
| `extra_checks.thermal.tool_call_flags.turn_totals` (THERMAL table `:489`) | **benign** (`population: benign`) | count, labelled; the non-benign rows and aggregate are one withheld digest | `seal_w1_tool_table` |
| `extra_checks.thermal.carve_out_flag_counts` | **benign** | count, labelled | `seal_thermal` |
| `extra_checks.km003c.models` (DC fit) | benign trajectories (training set) | as registered; non-benign DC rows sealed (MED-4, keyed) | `km003c.session_report`, `seal_non_benign` |
| `extra_checks.registration_diagnostics.battery_windows[*].B_count`, `unobserved_count`, `assist_count`, `assist_outside_request_count`; stdout `m/W1 battery: …` | **benign** (`count_population`, `assist_population: benign`) | count, labelled; all-member counts are one withheld digest | `benign_assist_counts`, `battery_print_row` |
| `...battery_windows[*].bar_pass`, `status`, `consequence` | all members | verdict (the registered B bar, computed in memory) | `v4_battery.window_consequences` |
| `...battery_windows[*].no_assist_sensitivity.member_ids` | **benign** ids (`population: benign`); full list withheld | per member, benign only | `_seal_extra_w1` |
| `...registration_diagnostics.no_rebuild_sensitivity.member_ids` | benign ids; full list withheld | per member, benign only | `_seal_extra_w1` |
| `...registration_diagnostics.warm_reference` (`R_minus_R1_soak_c`, `thermal.reference_warm`) | ordinal 5 (benign) | as registered | pass-through |
| `...warm_reference.wait_against_ordinal` rows | per ordinal; non-benign rows withheld | not pooled | `_seal_extra_w1` |
| `...registration_diagnostics.d_cohort` | all D members | configuration and identity assertion (no outcome) | pass-through |
| `...registration_diagnostics.sentinel` | ordinals 5 and 18 (benign) | as registered | pass-through |
| `extra_checks.balance_check` (R22-3), stdout `balance (R22-3): …` | sabotage and benign | withheld, with the member count | `seal_balance` |
| triage record `member_eligibility.captured_members`, `calibration_row.eligible_benign` | all / benign calibrators | capture count (eligibility; every member's capture is printed) / benign by definition | `light_triage` |
| triage record `thermal_escalation` | all gated members | verdicts | `light_triage.thermal_escalation` |
| standalone thermal desk `RL145_PRINTS.json` `residual_by_decode_bin`, `residual_by_load_bin` | all residual rows supplied | withheld | `guard_thermal_desk` |

Not pooled, and kept per member under the ruled eligibility path (RL-151 C1(a)): `members_excluded`,
`members_disclosure_only`, `exclusion_codes`, `calibration_exclusions` (codes only, no suffix text),
`registered_eligible_members`, the allowlisted instrument and identity flags (`FLAG_ALLOWLIST`), and
coverage verdicts (Sol F2).
