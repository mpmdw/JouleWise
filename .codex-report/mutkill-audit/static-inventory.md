# MUTKILL-AUDIT: static inventory (execution pending)

Date: 2026-10-23 UTC. This is an incomplete static review, not a verified mutation audit. No baseline or mutant test process has run. Every KEPT recommendation below is conditional on a clean baseline, an actual claimed-mutant failure, and production-shaped reachability. DROP duplicates and dead-output findings also require the indicated replay confirmation. Command evidence for every row is **NOT RUN: no usable execution environment**.

Four independent reviewers inspected one PR each; the lead reconciled recommendations and checked all 93 method names against fetched PR diffs. The matrix covers 135 distinct claimed mutant IDs: 34 calibration, 13 harvest, 33 L9, 55 BYTES. It does not independently certify any of those kills. Canonical mutation patch catalogs were not found in remotely inspected PRs; defect shapes below are inferred from docstrings/comments/source, not verified original patch bytes. A local archive search remains outstanding.

Static recommendations: 70 conditional KEPT, 16 FIX, 7 DROP. These are test-method counts; multiple methods may name the same mutant, and one method may cover several mutants.

## calib: PR #564

[PR](https://github.com/mpmdw/JouleWise/pull/564); branch `test/2026-10-22-mutkill-calib`; head `c865d3856d9e1ed691998b7c98ac3c0d2ac1ba1e`; target `main`; base SHA reported by PR metadata `abd9f1597f7244a23a95e0512655fbee14319032`. PR metadata main base is distinct from separately fetched current main `7c23ea4b71622f7a898617a66da48868e20562a3`; merge-base calculation has not run.

B = tests/test_calibration_bracketing_mutants.py; L = tests/test_calibration_ledger_mutants.py; D = tests/test_detection_floor_mutants.py; E = tests/test_floor_extraction_mutants.py; M = tests/test_floor_mint_estimator_mutants.py.

| Module | Test method | Claimed mutant(s) | Provisional disposition | Static rationale / required fix |
|---|---|---|---|---|
| B | `test_larger_pre_endpoint_sets_operative_bound` | M01913 | KEPT | max(pre,post)→post; 0.027+0.010818=0.037818 s versus 0.030818 s. |
| B | `test_earliest_post_wins_in_either_input_order` | M02164 | KEPT | Earliest post endpoint must determine the same selected bound in either delivery order. |
| B | `test_fresh_window_far_from_epoch_zero` | M02503 | KEPT | Freshness admission must be invariant under translating the epoch. |
| B | `test_zero_duration_window_refuses` | M02143 | KEPT | Zero duration is invalid; inclusive/exclusive comparison. |
| B | `test_observed_drift_above_screen_is_applied` | M02283 | KEPT | Operative allowance uses observed 3/16 s instead of screen 1/8 s. |
| B | `test_exact_decimal_budget_is_inclusive` | M01894 | KEPT | Registered budget boundary 1/4 is inclusive. |
| B | `test_capture_at_epoch_zero_is_admitted` | M02309 | FIX | Physics/capture parsers are mocked and event/power files arbitrary. Use physically consistent synthetic capture shifted to epoch zero. |
| L | `test_one_slot_derivation_session_is_admitted` | M03170 | KEPT | Declared one-slot session must remain admissible. |
| L | `test_claim_after_all_slots_finalized_has_typed_conflict` | M03528 | KEPT | Exhausted real legacy receipt chain should give a typed conflict rather than an index error. |
| L | `test_full_tail_is_valid_and_longer_journal_retains_only_64_bytes` | M02866 M03616 | KEPT | Exact 64/80-byte journal inputs and retained bytes/hashes; validate the retention contract, not a measured threshold. |
| L | `test_publication_refuses_replaced_leased_inode` | M03363 | KEPT | Genesis publication holds a different path from the older descriptor-open replacement test; replay needed to establish independence. |
| L | `test_valid_progress_frame_of_eight_kib_is_admitted` | M04101 | DROP | 8192-character locator is not a production-shaped filesystem locator; pins incidental buffer capacity without an output-number witness. |
| L | `test_recognized_worker_refusal_passes_through` | M03736 | FIX | Combine with unknown-reason case as complementary protocol subcases; show the actual consuming/selection consequence before claiming two separately earned tests. |
| L | `test_unknown_worker_reason_is_a_protocol_refusal` | M03736 | FIX | Same claimed mutant as recognized-reason case. Accepted and rejected vocabulary are complementary, but do not constitute two independent mutant kills. |
| L | `test_live_worker_is_terminated_and_reaped` | M02715 | FIX | Fake Process records terminate/join calls. Use a real bounded worker and observable process ownership/orphan count. |
| D | `test_shared_bound_cannot_embed_allowance_twice` | M01010 | KEPT | Exact dyadic recorded/applied allowance inconsistency, avoiding a tiny tolerance probe. |
| D | `test_transport_gate_uses_largest_nonfirst_cell` | M00378 | KEPT | 8 J gate regardless of cell order; older witness puts the maximum first. |
| D | `test_nine_member_residual_corner_floor` | M00860 | KEPT | Independent corner arithmetic gives (76/9)*sqrt(9/8). |
| D | `test_exactly_sixteen_nonzero_widths_are_admitted` | M00074 | FIX | Admission at the 16-corner cap is useful, but add an independently derived floor oracle instead of only non-None. |
| D | `test_negative_mean_zero_width_corner_helper` | M00589 | DROP | Docstring admits public floor is unchanged: public max masks the private negative-mean helper change. |
| D | `test_one_is_a_positive_member_count_on_the_pinset_wire` | M00684 | FIX | Mutates pinset counts to 1 while validating an independent n>=5 artifact. Show a coherent production count/floor consequence. |
| D | `test_config_projection_must_match_the_registered_family` | M00443 | FIX | Projection loader is mocked; use real registered config fixture to demonstrate provenance at a consuming output. |
| E | `test_interpolation_adds_to_member_envelope` | M01678 | KEPT | Real extraction arithmetic gives 1+1/4=5/4 J; custody/strict admission are bypassed, so this is arithmetic-seam evidence. |
| E | `test_quarter_metric_boundary_is_admitted` | M01714 | KEPT | Exact 1.25/5=1/4 admission boundary. |
| E | `test_zero_metric_with_nonzero_envelope_has_typed_refusal` | M01710 | KEPT | Zero metric avoids division and retains the specified refusal. |
| E | `test_exactly_two_launch_lineages_refuse` | M01411 | DROP | Likely duplicate: existing test_absolute_cell_refuses_marker_legacy_or_full_lineage_mix supplies two distinct full lineages and checks launch_lineage_conflict. Confirm by replay. |
| E | `test_uncertainty_dominated_cell_keeps_its_label` | M01508 | DROP | Likely duplicate: existing test_zero_scatter_with_nonzero_admissible_width_is_labelled_extraction asserts the same exact floor_conditions list through real synthetic bundles. Confirm by replay. |
| E | `test_serialized_point_diagnostic_keeps_dominating_prediction` | M01218 M01220 | KEPT | Derived point diagnostic 20.39935058 J versus 12 J; max-collapse witness. |
| E | `test_comparative_anchor_maximum_includes_nonfirst_members` | M01539 | KEPT | Widths 1/8 through 8/8 J must retain 1 J. |
| E | `test_subunit_and_zero_throughput_are_valid` | M01488 | KEPT | Exact 0 and 1/2 throughput survive rather than legacy fallback 99. |
| M | `test_projection_cannot_substitute_screen_for_larger_drift` | M01780 | KEPT | Substituting the screen loses 0.000932 s, over 8%; broad derived mismatch. |
| M | `test_inconsistent_authenticated_session_bound_refuses` | M01801 M01803 | DROP | Mocked ready session is inconsistent by construction. Real whole_window stores bracket b in both compared fields; nearby M01802 was excluded as equivalent for that equality. Need a reachable production witness to overturn. |

## harvest: PR #569

[PR](https://github.com/mpmdw/JouleWise/pull/569); branch `test/2026-10-22-mutkill-harvest`; head `5e50e1c4f848c2fa1137c5aad86705cf732ac83c`; target `main`; base SHA reported by PR metadata `abd9f1597f7244a23a95e0512655fbee14319032`. PR metadata main base is distinct from separately fetched current main `7c23ea4b71622f7a898617a66da48868e20562a3`; merge-base calculation has not run.

H = tests/test_harvest_b5_mutants.py.

| Module | Test method | Claimed mutant(s) | Provisional disposition | Static rationale / required fix |
|---|---|---|---|---|
| H | `test_state_tail_gap_is_strictly_above_the_registered_limit` | M01499 | KEPT | Tail >gap becomes >=gap; registered 120 s has zero holes, +1 integer ns has one. |
| H | `test_discharge_count_excludes_the_exact_negative_limit` | M03998 | KEPT | Current <-limit becomes <=-limit; -199/-200/-201 mA give below-count 0/0/1 while remaining assisted. |
| H | `test_request_ending_with_member_has_no_post_request_phase` | M00516 | FIX | Mutation adds a zero-duration post_request record; asserted 12.5 J and request count 1 appear unchanged. Establish downstream number/selection consequence, otherwise drop. |
| H | `test_discordant_duplicate_keeps_the_larger_rate_in_either_order` | M04091 | KEPT | Duplicate process rates 0.051/0.01 CPU s/s retain the maximum in either order and one offender. |
| H | `test_hole_starts_at_the_latest_ended_interval` | M01535 | KEPT | Nested [0,10],[1,2],[20,30] s yield hole [10,20], not [2,20]. Exact canonical max-collapse edit is unavailable. |
| H | `test_anchor_at_maximum_read_skew_still_emits_its_step` | M02602 | KEPT | Clock skew <=maximum becomes <maximum; persisted step count 1 at registered maximum, 0 at +1 ns. |
| H | `test_negative_step_uses_the_magnitude_and_a_strict_limit` | M04137 | KEPT | abs(step)>limit becomes step>limit; exact negative limit gives zero flags, 1 ns beyond gives one. |
| H | `test_kernel_task_cpu_seconds_are_clipped_to_each_request` | M04888 M07661 M07662 M04889 | KEPT | None-rate guard, both clip edges and accumulation: 0.5 CPU s/s*5 s=2.5 CPU s; 1/3*5 printed at six decimals is 1.666667; absent rate gives no flag. |
| H | `test_two_valid_thermistor_reads_still_disclose_a_rise` | M06707 | KEPT | Valid-count <2 becomes <=2; [3000,failed,3310] centi-C gives (3310-3000)/100=3.1 K, 2 valid/1 failed. |
| H | `test_idle_baseline_wall_fallback_reaches_persisted_assessment` | M03873 | FIX | Asserts only a present two-integer span. Derive and assert its endpoint values/duration; wrong two-integer spans currently satisfy the oracle. |

## l9: PR #566

[PR](https://github.com/mpmdw/JouleWise/pull/566); branch `test/2026-10-22-mutkill-l9`; head `1a347eb7c21f6a9e7a9961da29865de329b39e5e`; target `lane/2026-10-07-l9-analysis`; base SHA reported by PR metadata `730842e05301a90af743873e3356bfa0c5a17181`. PR metadata main base is distinct from separately fetched current main `7c23ea4b71622f7a898617a66da48868e20562a3`; merge-base calculation has not run.

A = tests/b5_analysis/test_archive_mutant_kills.py; B = test_bracket_mutant_kills.py; C = test_context_mutant_kills.py; D = test_disclosures_mutant_kills.py; K = test_kept_units_mutant_kills.py; R = test_reported_cell_mutant_kills.py; S = test_sensitivity_mutant_kills.py; W = test_windows_mutant_kills.py (all under tests/b5_analysis/).

| Module | Test method | Claimed mutant(s) | Provisional disposition | Static rationale / required fix |
|---|---|---|---|---|
| A | `test_two_unlisted_files_have_an_integer_count` | M00140 | KEPT | Exact extras count 2/type int distinguishes a boolean count that count=1 cannot distinguish. |
| A | `test_nested_claim_root_uses_custody_inventory` | M00397 M00398 | KEPT | Real synthetic bytes/digests under nested night-custody/requests exercise root/prefix mapping. |
| A | `test_repeated_census_preserves_result_and_records` | M00409 | FIX | Connect a second authenticated read to real consuming analysis; currently checks repeated census/cache state. |
| B | `test_acceptance_maximum_at_each_part_of_the_corpus` | M08681 | KEPT | Acceptance .090 s at positions 0/12/23 dominates .030 s sources and .040 s ledger peak; relative fallback bar 9e-8 s. |
| C | `test_disjoint_survivors_and_exclusions_have_zero_intersection` | M01153 | KEPT | Set intersection versus union; public counts survivor 7/excluded 0/intersection 0. |
| D | `test_cpu_sums_disjoint_requests_and_clips_both_edges` | M02423 M04013 M04011 | KEPT | 2 CPU s/s*([1,2]+[3,4])=4 CPU s; both edge clips and sum matter. |
| D | `test_restarted_monitor_adds_final_cumulative_session_costs` | M01873 | KEPT | Sum only each session's last cumulative cost: (2+3)+(5+7)=17 CPU s. |
| D | `test_probe_at_phase_end_is_excluded` | M02958 | KEPT | One interior probe counts; phase-right-edge probe does not, yielding exact count 1. |
| D | `test_epoch_events_use_the_member_clock_anchor` | M03440 | KEPT | Epoch 100 anchored at monotonic 1 s locates probe 1.25..1.5 s inside the phase; count 1. |
| D | `test_exact_minimum_and_quad_limited_warning` | M02220 M02717 | KEPT | (n_r,n_b)=(5,5) no warning, (10,4) warning. Cite registered minimum 5 from plan section 5 beside the bar. |
| D | `test_zero_ratio_is_an_outside_band_member` | M02826 | KEPT | Finite rho=0 must be disclosed outside registered 0<rho<=1 band rather than treated as missing. |
| D | `test_historical_counts_default_to_three_one_three` | M01948 | KEPT | Structured and rendered default reference shape (3,1,3), fixed by the historical plan. |
| D | `test_rendered_corpus_includes_nonzero_drop_count` | M01974 | KEPT | Two flagged rows must print reason count 2 in released rendering. |
| D | `test_single_centi_degree_reading_prints_celsius` | M04168 M04119 | KEPT | 3000 centi-C/100=30.00 C; printed precision is the property. |
| D | `test_three_readings_can_form_a_level_plateau` | M04111 | KEPT | Exactly 3 trailing readings [3000,3025,3000] span .25 K below registered .5 K. Cite that registered threshold. |
| D | `test_trailing_range_prevents_false_plateau` | M03509 | KEPT | Trailing [33.5,34,35] C span 1.5 K>.5 K; total rise 5 K>3 K. Cite registered .5/3 K thresholds. |
| K | `test_each_reported_quad_has_its_own_four_ordinals` | M04670 | KEPT | Ten disjoint four-tuples partition integer positions 11..50. |
| K | `test_zero_flag_count_is_a_supported_public_consumer` | M04204 | FIX | Bypasses S0 with previously selected window; S0 omits zero keys. Demonstrate a supported production-shaped consumer for the zero count. |
| K | `test_negative_and_boolean_flag_counts_are_refused` | M04256 | FIX | Bypasses S0 with stale selected handle. Show real consuming path where invalid counts affect data/numbers. |
| R | `test_interior_member_attains_the_attribution_floor` | M05883 | KEPT | Fourth kept member has .5 J, all others .01 J; floor .5 J and its named attainer. |
| S | `test_attainer_may_be_the_terminal_receipt` | M04949 | KEPT | BMax(1/16 s,500,500) includes terminal receipt; exact prefix boundary (arithmetic seam). |
| S | `test_terminal_count_must_be_positive` | M04846 | KEPT | T=0/-1 refuse; prefix terminal count must be positive. |
| S | `test_transported_floor_takes_the_larger_later_source` | M05008 | FIX | Fabricated extractor/resolution closures bypass real extraction/transport. Derived corners (1.5,1.75),(2,3),(1.25,1.5) give (2,3,3) J; add real source fixture through actual extractor. |
| W | `test_attempts_start_at_one` | M05516 | KEPT | Attempt 1 accepts, 0/-1 refuse; history/selection count domain. |
| W | `test_requested_g10_allows_zero_and_one_redraws` | M05590 M05591 | KEPT | Redraws 0/1 accept, -1 refuses; two syntactic mutants share one boundary witness. |
| W | `test_record_reader_revalidates_superseded_paths_on_typed_entries` | M05640 | FIX | no_archive plus dataclass.replace(relative path) tests defensive shape validation. Demonstrate a custody/number consequence or drop. |
| W | `test_positive_epoch_api_includes_the_first_second` | M05490 | DROP | Pins Unix-1970 .5/1.0 s domain without production-shaped L9 witness. Reconsider only with a real supported consumer/number consequence. |

## bytes: PR #570

[PR](https://github.com/mpmdw/JouleWise/pull/570); branch `test/2026-10-22-mutkill-bytes`; head `b83f0719cae2b222ed2fe7100f064f325a915788`; target `lane/2026-10-22-bytes-pass1`; base SHA reported by PR metadata `da27be7b965088b7d2e6697ca48c98512a9b442b`. PR metadata main base is distinct from separately fetched current main `7c23ea4b71622f7a898617a66da48868e20562a3`; merge-base calculation has not run.

1 = tests/test_bytes_analysis_mutants.py; 2 = tests/test_bytes_analysis_mutants_r2.py.

| Module | Test method | Claimed mutant(s) | Provisional disposition | Static rationale / required fix |
|---|---|---|---|---|
| 1 | `test_named_primary_coefficients` | M7ca4b6ba13 | FIX | Derived epsilon=2/intercept=3 is useful, but rho=0 assertions use unexplained absolute 1e-6. Relative fallback alone does not derive an absolute zero bar. |
| 1 | `test_primary_interval_endpoints` | M5bfe141b2f | KEPT | Independent HC3=10/7, OLS=sqrt(2/5), t=sqrt(722/39) determine endpoints. |
| 1 | `test_leave_one_out_predictions_use_the_other_nine_points` | M9320cf871e | KEPT | All nine training points in each fold; hand 2x2 sufficient-statistic prediction. |
| 1 | `test_deviation_uses_the_full_covariance` | Mc44c81c98c | KEPT | Full quadratic form gives prediction half-width 2*sqrt(112/25). |
| 1 | `test_pass_difference_is_signed_in_pass_order` | M7a54107169 | KEPT | Pass2-pass1=+20/-20 J under swapped means and reversed delivery. |
| 1 | `test_combined_attribution_floor_is_worst_pass` | M381d9ca0e1 Me32213db94 | KEPT | max(first,last) collapse; opposite floor orders both retain 4 J. |
| 1 | `test_combined_meter_floor_is_worst_pass` | M96abad714d Mf9872383d4 | KEPT | Opposite meter-floor orders both retain 5 J. |
| 1 | `test_pass_attribution_floor_is_worst_member` | M2b0d65cb43 | KEPT | Last anchor .75 J dominates .125 J anchors. |
| 1 | `test_blinded_secondary_subtracts_each_runs_own_idle_energy` | M50017a0b7b M3fcc328578 Md003ace2ad M47d491a92f Maa40c1f7ea | KEPT | 50-run blinded CSV→load_records→reduce_models→combine_passes; own idle energy gives .2*18+.8*22=21.2 J. |
| 1 | `test_without_assisted_lower_endpoint` | Mf7ce56a8c4 M0421a346f4 M1e2d8592af M8649a2af33 M2764469c3f M2b4a97c71e Ma6293ad65e | KEPT | Lower arithmetic/availability family: 100-1-.5=98.5 J. |
| 1 | `test_without_assisted_upper_endpoint` | M124a7259b5 M34764e0ab8 Mf37183b001 M8a8751d3ff M03c1d567e8 M4d52f54e3a Mb59420ce4e | KEPT | Upper arithmetic/availability family: 100+1+.5=101.5 J. |
| 1 | `test_without_assisted_energy_per_output_token` | M941bc63cc8 | KEPT | 100/512=.1953125 J/token exactly. |
| 1 | `test_without_assisted_sums_all_bounds_with_undefined_variance` | M8508398ca4 M576d952762 M7f7466a914 | KEPT | All bound kinds sum .125+.25+.5=.875 J even when variance half-width is null. |
| 2 | `test_offset_bound_keeps_registered_stratum_weights` | A0a9cde7a8e | KEPT | Registered .2/.8 weights give .2*.2+.8*1.2=1 J, not plain mean 49/45. |
| 2 | `test_pass_offset_bound_is_the_arithmetic_mean` | Ab131190591 | KEPT | Mean pass offset bound 4 J, not min 2 J. |
| 2 | `test_power_support_is_the_ratio_of_pass_means` | N7fb83e8a45 N9f8754fabe Nf4337f66b3 | KEPT | 4 J/3 s=4/3 W; alternatives 3/4,4,12. |
| 2 | `test_named_coefficient_support_uses_slope_response_weights` | A43c663184b A6f129d8feb | KEPT | Coefficient-index/product changes move derived slope support .5 to 1 or 3.3. |
| 2 | `test_named_hc3_offset_endpoints_belong_to_epsilon` | A425e4cc5d5 | KEPT | Named slope HC3 endpoints 2±t*10/7 widened .5. |
| 2 | `test_named_ols_offset_endpoints_belong_to_epsilon` | A3f168e754d | KEPT | Named slope OLS endpoints 2±t*sqrt(2/5) widened .5. |
| 2 | `test_named_sensitivity_normalizes_duration_and_milliseconds` | N66dcefba03 Nf1dec3fc9c Nbd525b83a6 Abfaff8e135 | KEPT | Derived slope sensitivity -.001 versus -.016/-.004/-1000/+.002. |
| 2 | `test_positive_resident_effect_is_not_labelled_adds_nothing` | A6b8b4d4bc5 | FIX | rho=4 with response support .125 is derived; extra lower>3 bar is justified only as 'well above zero'. Derive that bar or remove it. |
| 2 | `test_meter_sensitivity_uses_samples_strictly_before_both_edges` | N68fb78c3a3 N2c5c3172fc N42a7cdbfed N34bd2a0bff Aa5a0256147 | KEPT | Pre-edge sample difference 20-10=10 W; wrong-index/operator alternatives 0/-20/30. |
| 2 | `test_meter_offset_bound_covers_the_larger_edge` | A4b8b9b81b8 | KEPT | max(20,30)*(.1+.007)=3.21 J; first edge alone gives 2.14 J. |
| 2 | `test_ols_return_widens_both_statistical_endpoints` | Ac2c4c25bf7 A7b840b5bc6 | DROP | h2 overwrites these initial ols interval fields; other identified callers use coefficients only. Dynamic unchanged-public-output proof remains outstanding. |

## Limits of these recommendations

- Calibration duplicate candidates are in existing tests/test_floor_extraction.py: test_absolute_cell_refuses_marker_legacy_or_full_lineage_mix and test_zero_scatter_with_nonzero_admissible_width_is_labelled_extraction. Both old and new selectors need baseline/mutant replay before redundancy is empirically confirmed.
- Calibration's negative-mean helper test explicitly says the public floor cannot change. The impossible session-bound mock and fake Process teardown need reachable consumer/process witnesses; a failing mocked guard alone earns no numerical claim.
- L9's disclosure Harness runs real disclosure/rendering arithmetic through fake archive adapters and a rebuilt-roster seam. Its sensitivity PassHarness injects project/extract/contrast consumers; terminal-boundary tests exercise the real sensitivity guard but do not authenticate a receipt-500 prefix. These are seam-level witnesses until a real synthetic archive runs end to end.
- BYTES ols endpoint-sign mutations target initial return fields at bytes_analysis.py:213-216 (PR head). h2 rewrites these at :307-311 before reading them; the other direct ols call consumes coefficients. Source analysis identifies no production reader of those initial values. Compare real h2 outputs under both mutations before finalizing DROP.
- A test killing a protocol/custody mutation is not automatically worthless: exact bytes can be the actual property, and choosing different data can change a number. The retained structural cases still need a concrete consumer/selection explanation and actual replay; schema shape or mock method calls alone are insufficient.
- Most numeric expectations use integer/dyadic arithmetic or a stated 1e-6 relative fallback. BYTES expected-zero rho comparisons instead use 1e-6 absolute without a derivation. The rho lower>3 bar also lacks a derivation. Neither bar was changed by this audit.

## Execution work still required

Obtain a usable runtime; inspect /etc/codex/network-policy.json and repository status; run tools/cloud/seat_setup.sh if present on the base (remote main lookup returned 404); fetch all four branches and their targets; compute merge bases; search local sweep archives for canonical patches; create one isolated scratch tree per PR; save each one-site production patch; run each new test without and with its claimed mutant using JW_B5_SYNTHETIC_ONLY=1 and a unique existing TMPDIR per process; run focused existing duplicate selectors; execute production-shaped synthetic end-to-end witnesses; save exact commands, exit codes, failure assertions, and tails; reconcile this provisional matrix; commit final .codex-report/MUTKILL-AUDIT.md on the authorized report branch only.
