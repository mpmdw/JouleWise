# ALIGN v4 W1 candidate rehearsal C · 2026-11-20

This rehearsal assembles the W1 signing candidate from issued PR #734 using synthetic tests on the Air and GitHub Actions. Both PRs are CI-only drafts marked **do not merge**. Variant 2 results are **provisional** while PR #897 is in review. Variant 3 results are **provisional** while both PR #897 and PR #809 await independent acceptance.

## Assembly

| Order | Component | Intake head |
|---:|---|---|
| 0 | Issued W1 and R1 pin, PR #734 | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` |
| 1 | PR #826 desk-seal successor | `1fc28324d51f8057fa6228e6e7d42b5ea331d52c` |
| 2 | PR #839 step-4 restore proof | `70b795954a4876c828cb6d6b3de7941e9d726768` |
| 3 | PR #831 W1-line S-row landing | `b38cef8286c7772e970760103debf187174fbad6` |
| 4 | PR #813 S/Q amendment | `82542232dbb7459b0320c37380925e9372afb7e8` |
| 5 | PR #897 contrast writer | `f32326af2b902fe7060d98b3a28240d0665bc4fa` |
| 6 | W1 Part C twin | `09b1ddbd515bcea1ecf2384cbc885bd2c137817c` |
| 6, source | PR #809 Part C main-targeting source | `2bb72f23aa547c8049a9df5a029a2d1b56b249c0` |

PRs #826, #839, #831, #813 and #897 and the Part C twin matched the pins in the brief. PR #809 had advanced from `d4b484475` to `2bb72f23aa54`, including `60bdbc458` for the audit's raw-evidence findings and `586e77959` for the frozen driver decisions.

| Variant | Assembly commit used for checks | Assembly tree | Condition 13 | Draft |
|---|---|---|---|---|
| 1 · four components | `5fddbb29435e3cf69c02803e033b4358876a5b8a` | `3652381ee416a621ac76388bc54d48abb11efc4e` | PASS 10/10 | Local |
| 2 · add PR #897, **provisional** | `0046d9cb73751deb1b279167e0195735ea4595f5` | `7b5ce9560758909fe3693afdee5b1c4039155d53` | PASS 10/10 | [PR #901](https://github.com/mpmdw/JouleWise/pull/901) |
| 3 · add Part C, **provisional** | `3615c68cfb6cc84c9f63266bfa30898ca0ba298d` | `4fee78e19f11abf11b93e7bd0b34eee5285ad08c` | PASS 10/10 | [PR #902](https://github.com/mpmdw/JouleWise/pull/902) |

Replaying the pinned snapshot produced all three tree IDs and ten-blob counts again. The previews and staged merges agreed at every step. There were zero merge conflicts and zero unions. GitHub's generated merge commits `bf868bdf156241e6e5c0c784f996374d94a46939` and `b5660176432f5bdbea9b1aabc447834db1a29181` have the issued first parent and the exact variant 2 and 3 assembly trees. The PR bodies were read back and match the seat copies. The branch history inherits PR #813's existing public unsigned template blob with its two empty S/Q artifact declarations, as in rehearsal B. The assembler checks those blob identities without inspecting their contents. The release branches and PR #824 and PR #886 stayed outside the rehearsal changes.

### W1 Part C port

The W1 twin's suite digest was `73fb8fd38e16d3cf653bb808a3d06ec39dfb7a564408f94072d85f36fa075e2a`. The commit `211d53549c0ed3ddad48a9b0c6bff0bc3dfefdbf` applies the scoped delta from `3f7f7c849` to the pushed PR #809 head. All four preimages matched on the twin. Every hunk applied cleanly and the resulting files match pushed PR #809 byte for byte.

| Ported path | Role |
|---|---|
| `scripts/align_r1_part_c.py` | Evaluator, judged invoker and frozen driver decisions |
| `scripts/align_r1_part_c_evidence.py` | Return ledger, descriptor binding and evidence verification |
| `tests/align/test_partc_frozen_differential.py` | Frozen v2, SHA-256 `f35c7bb08814785079008acd3a47a3c85993083da1e7ba731e7d2bee486d768d` |
| `tests/test_part_c_evidence_ledger.py` | Descriptor, raw-evidence, soak and frozen-driver regressions |
| `tests/align/test_rl145_part_c.py` | W1-only synthetic launcher fixture in `3615c68cf` |

The final fixture path exists on the W1 twin and is absent from the pushed main-targeting tree. It follows PR #809's public W1 handoff by redirecting descriptor observations to a temporary synthetic mirror. The existing W1-side `scripts/run_align_r1_smoke.py`, `scripts/align_r1_followup_kit.py` and gate tests supply the launcher handoff. The scoped upstream delta contains zero changes to those paths. The judged invoker resolves the source from the row-zero bound runtime configuration using the frozen loader, then records the descriptor witness at member return. [RL-183 §1](https://github.com/mpmdw/JouleWise/blob/71a83f666024c26e89cdce09dfb7a7e80d299794/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20084) · [RL-189 §1](https://github.com/mpmdw/JouleWise/blob/71a83f666024c26e89cdce09dfb7a7e80d299794/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22078)

## Local checks

The laptop ran Python 3.13.18 with `nice -n 10`, a private TMPDIR per run, offline model caches and the repository's host-command guard. The seat guard denies access to non-synthetic slot files and external model descriptors. The synthetic WP22 harness uses its own invented slot bytes for the raw-copy step. The step-4 restore wrapper uses invented roster IDs. Launcher process-inventory verdicts come from hosted CI.

The guarded checkout initially refused the stock S6 read for `ChainScriptTests.test_steps_one_to_three_run_for_real_on_a_synthetic_lane_record` on all four trees. Feeding the same synthetic S6 value used by the frozen Part C harness allowed the full chain test to run. The issued and variant 1 chain modules passed all six tests. The variant 2 and 3 chain modules passed all fifteen tests, including all nine PR #897 writer regressions. The writer code is `66a8302477f876f7fd8e9078b07c75edee4fcd74`, and the audit regression fixture is `426da3e89`.

The full differential run was started before the fixture-only commit. Frozen v2 uses the fixture at its own Git pin and imports the evaluator and evidence helper from the candidate. Those files and the suite are byte-identical before and after the fixture commit. The descriptor-only run was executed on the exact updated variant 3 head.
| Check | Issued W1 | Variant 1 | Variant 2 | Variant 3 |
|---|---|---|---|---|
| desk-release | RUNNING | RUNNING | RUNNING | RUNNING |
| dynamic-closure | PASS | FAIL | FAIL | FAIL |
| executed-closure | PASS | PASS | PASS | FAIL |
| opus-cold-witness | PASS | PASS | PASS | PASS |
| r1-frozen-named | PASS | PASS | PASS | PASS |
| registration | FAIL | FAIL | FAIL | FAIL |
| w1-reliability | FAIL | FAIL | FAIL | FAIL |
| w1-synthetic | FAIL | PASS | FAIL | PASS |
| wp22-full | FAIL | — | — | — |
| PREQUAL ordinary / stack | PASS | PASS | PASS | PASS |
| PREQUAL ordinary / r0-config | PASS | PASS | PASS | PASS |
| PREQUAL ordinary / d-pin-verifier | PASS | PASS | PASS | PASS |
| PREQUAL ordinary / template-rewrites | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary / checkpoint-native | PASS | PASS | PASS | PASS |
| sharded | RUNNING | — | — | — |
| contrast-writer | PASS | — | — | — |
| dynamic-live | FAIL | — | — | — |
| w1-minimal | PASS | — | — | — |
| canonical | — | — | — | RUNNING |
| desk-release (repeat) | — | — | — | RUNNING |
| partc-attack-repros | — | — | — | PASS |
| partc-rl145 | — | — | — | RUNNING |
| Refusal census | PASS | PASS | PASS | FAIL |
| S/Q and S-row modules | — | PASS | PASS | PASS |
| Contrast chain with synthetic S6 | PASS | PASS | PASS | PASS |

### Exceptions by test ID

| Check | Test ID | Issued W1 | Variant 1 | Variant 2 | Variant 3 |
|---|---|---|---|---|---|
| PREQUAL ordinary | `d-pins` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `d-tokenizer-files` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `generated` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `kit` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `launcher` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `load` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `model-load` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `nll-fixture-ids` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `template-render` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `tool-roundtrip` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary | `w1-plan` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL ordinary / checkpoint-native | `checkpoint-native` | FAIL | — | — | — |
| PREQUAL ordinary / stack | `stack` | FAIL | — | — | — |
| PREQUAL ordinary / template-rewrites | `template-rewrites` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `deadline` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `kit-ready` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `receipt` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `series-manifest` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| PREQUAL w1 | `w1-window-max` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| Refusal census | `hazards.test_refusal_allowlist.RefusalAllowlistTests.test_every_refusal_site_is_listed_with_its_exact_count.test_every_refusal_site_is_listed_with_its_exact_count` | PASS | PASS | PASS | FAIL |
| Refusal census | `hazards.test_refusal_allowlist.RefusalAllowlistTests.test_the_scan_covers_every_module_the_hazard_path_imports.test_the_scan_covers_every_module_the_hazard_path_imports` | PASS | PASS | PASS | FAIL |
| S/Q and S-row modules | `align.test_s_rows.Step0WorldTests.test_deadman_bundles_give_rows_from_runtime_events.test_deadman_bundles_give_rows_from_runtime_events` | ABSENT | SKIP | SKIP | SKIP |
| S/Q and S-row modules | `align.test_s_rows.Step0WorldTests.test_desk_reads_every_ending.test_desk_reads_every_ending` | ABSENT | SKIP | SKIP | SKIP |
| S/Q and S-row modules | `align.test_s_rows.Step0WorldTests.test_g1_timeout_member_is_kept_on_its_rows.test_g1_timeout_member_is_kept_on_its_rows` | ABSENT | SKIP | SKIP | SKIP |
| S/Q and S-row modules | `align.test_s_rows.Step0WorldTests.test_prefill_deadman_turn_gives_no_row.test_prefill_deadman_turn_gives_no_row` | ABSENT | SKIP | SKIP | SKIP |
| dynamic-closure | `align.test_v4_dynamic_closure.LiveTraceTests.test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace.test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace` | FAIL/PASS | FAIL | FAIL | FAIL |
| dynamic-live | `align.test_v4_dynamic_closure.LiveTraceTests.test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace.test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace` | FAIL | FAIL | FAIL | FAIL |
| executed-closure | `align.test_v4_executed_closure.ExecutedClosureBindingTests.test_every_executed_module_and_script_is_in_the_receipt_artifact_set.test_every_executed_module_and_script_is_in_the_receipt_artifact_set` | PASS | PASS | PASS | FAIL |
| registration | `align.test_v4_registration.RegistrationTests.test_d_max_turns_is_part_of_frozen_kit.test_d_max_turns_is_part_of_frozen_kit` | FAIL | FAIL | FAIL | FAIL |
| signing | `R0 binding` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| signing | `step4-exporter-selection-roster` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| signing | `stored F0-run-11 replay` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| signing | `stored counted-Part-C replay` | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT | NEEDS-REAL-INPUT |
| w1-reliability | `test_w1_reliability.TerminalDeliveryTests.test_actual_program_courier_parses_prompt_and_pushes_to_local_remote.test_actual_program_courier_parses_prompt_and_pushes_to_local_remote` | FAIL | FAIL | FAIL | FAIL |
| w1-reliability | `test_w1_reliability.TerminalDeliveryTests.test_repeat_snapshot_fast_forwards_and_preserves_byte_identical_result.test_repeat_snapshot_fast_forwards_and_preserves_byte_identical_result` | PASS | FAIL | PASS | PASS |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_all_members_succeed_without_exclusions.test_all_members_succeed_without_exclusions` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_clean_window_passes_the_signed_battery_consequence.test_clean_window_passes_the_signed_battery_consequence` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_desk_energy_matches_independent_world_integral.test_desk_energy_matches_independent_world_integral` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.CleanWindowTests.test_u1_u3_and_contrast_match_design.test_u1_u3_and_contrast_match_design` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_30b_u1_counts_the_x1_member_and_passes.test_30b_u1_counts_the_x1_member_and_passes` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_clean_members_succeed.test_clean_members_succeed` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_collector_death_is_x4_and_episode_continues.test_collector_death_is_x4_and_episode_continues` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_contrast_verdict_matches_design_rule.test_contrast_verdict_matches_design_rule` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_d_u1_counts_two_thermal_exclusions_and_fails.test_d_u1_counts_two_thermal_exclusions_and_fails` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_deadman_is_x7.test_deadman_is_x7` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_desk_runs_on_a_window_with_failed_members.test_desk_runs_on_a_window_with_failed_members` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_g0_timeout_ends_the_member_promptly_as_x2.test_g0_timeout_ends_the_member_promptly_as_x2` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_malformed_xml_stops_and_is_excluded.test_malformed_xml_stops_and_is_excluded` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_os_level_nonzero_is_x1.test_os_level_nonzero_is_x1` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.InjectedWindowTests.test_u4_to_u6_inconclusive_in_w1.test_u4_to_u6_inconclusive_in_w1` | SKIP | SKIP | SKIP | SKIP |
| w1-synthetic | `align.test_v4_w1_synthetic.KitBridgeTests.test_consumer_custody_rebinds_to_synthesized_capture_bytes.test_consumer_custody_rebinds_to_synthesized_capture_bytes` | FAIL | PASS | FAIL | FAIL |
| w1-synthetic | `align.test_v4_w1_synthetic.KitBridgeTests.test_contrast_deadman_follows_the_30b_member_law_and_admits_a_g0_timeout.test_contrast_deadman_follows_the_30b_member_law_and_admits_a_g0_timeout` | FAIL | PASS | FAIL | FAIL |
| w1-synthetic | `align.test_v4_w1_synthetic.KitBridgeTests.test_synthetic_inputs_pass_admission_and_roster_is_a1.test_synthetic_inputs_pass_admission_and_roster_is_a1` | FAIL | PASS | FAIL | FAIL |
| w1-synthetic | `align.test_v4_w1_synthetic.KitBridgeTests.test_synthetic_t_dead_is_bound_by_l1_and_the_r1_tail.test_synthetic_t_dead_is_bound_by_l1_and_the_r1_tail` | FAIL | PASS | FAIL | FAIL |
| w1-synthetic | `align.test_v4_w1_synthetic.MinimalDryRunTests.test_minimal_synthetic_w1_reaches_the_desk.test_minimal_synthetic_w1_reaches_the_desk` | FAIL | PASS | FAIL | FAIL |
| w1-synthetic | `align.test_v4_w1_synthetic.MinimalDryRunTests.test_the_synthetic_contrast_is_rederived_after_the_wp18_update.test_the_synthetic_contrast_is_rederived_after_the_wp18_update` | FAIL | PASS | FAIL | FAIL |
| wp22-full | `align.test_v4_opus_cold_witnesses.Wp22DryRunReachesTheDesk.test_minimal_synthetic_w1_produces_a_desk_record.test_minimal_synthetic_w1_produces_a_desk_record` | FAIL | PASS | PASS | PASS |
| wp22-full | `align.test_v4_w1_synthetic.CleanWindowTests` | FAIL | — | — | — |
| wp22-full | `align.test_v4_w1_synthetic.InjectedWindowTests` | FAIL | — | — | — |
| wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_consumer_custody_rebinds_to_synthesized_capture_bytes.test_consumer_custody_rebinds_to_synthesized_capture_bytes` | FAIL | PASS | FAIL | FAIL/PASS |
| wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_contrast_deadman_follows_the_30b_member_law_and_admits_a_g0_timeout.test_contrast_deadman_follows_the_30b_member_law_and_admits_a_g0_timeout` | FAIL | PASS | FAIL | FAIL/PASS |
| wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_synthetic_inputs_pass_admission_and_roster_is_a1.test_synthetic_inputs_pass_admission_and_roster_is_a1` | FAIL | PASS | FAIL | FAIL/PASS |
| wp22-full | `align.test_v4_w1_synthetic.KitBridgeTests.test_synthetic_t_dead_is_bound_by_l1_and_the_r1_tail.test_synthetic_t_dead_is_bound_by_l1_and_the_r1_tail` | FAIL | PASS | FAIL | FAIL/PASS |
| wp22-full | `align.test_v4_w1_synthetic.MinimalDryRunTests.test_minimal_synthetic_w1_reaches_the_desk.test_minimal_synthetic_w1_reaches_the_desk` | FAIL | PASS | FAIL | FAIL/PASS |
| wp22-full | `align.test_v4_w1_synthetic.MinimalDryRunTests.test_the_synthetic_contrast_is_rederived_after_the_wp18_update.test_the_synthetic_contrast_is_rederived_after_the_wp18_update` | FAIL | PASS | FAIL | FAIL/PASS |

### Frozen v2 outcome

- `clean control verdict=pass; descriptor rows PASS (4/4) ; 2760 decision sites in frozen call-graph closure`
- `generated 19477 case IDs`
- The unfiltered synthetic run remains in progress. Last recorded count `progress 400 / 19477 {'REFUSED': 381, 'OTHER_REFUSAL': 14, 'AGREES_PASS': 5}`.
- The exact updated variant 3 tree completed the separate 16-case descriptor run.

| Member | False passes | Wrong verdicts | Harness errors |
|---|---:|---:|---:|
| `idle` | 0 | 0 | 0 |
| `capture-predecessor-30b` | 0 | 0 | 0 |
| `step-d` | 0 | 0 | 0 |
| `d-bank-benign-s1` | 0 | 0 | 0 |
| `x-g` | 0 | 0 | 0 |

| Descriptor case | Result |
|---|---|
| `capture-predecessor-30b/descriptor/consistent-40961` | AGREES_PASS |
| `capture-predecessor-30b/descriptor/mirror-40961-claim-40960` | REFUSED |
| `capture-predecessor-30b/descriptor/no-binding` | REFUSED |
| `capture-predecessor-30b/descriptor/rewritten-after-return` | REFUSED |
| `d-bank-benign-s1/descriptor/consistent-40961` | AGREES_PASS |
| `d-bank-benign-s1/descriptor/mirror-40961-claim-40960` | REFUSED |
| `d-bank-benign-s1/descriptor/no-binding` | REFUSED |
| `d-bank-benign-s1/descriptor/rewritten-after-return` | REFUSED |
| `step-d/descriptor/consistent-40961` | AGREES_PASS |
| `step-d/descriptor/mirror-40961-claim-40960` | REFUSED |
| `step-d/descriptor/no-binding` | REFUSED |
| `step-d/descriptor/rewritten-after-return` | REFUSED |
| `x-g/descriptor/consistent-40961` | AGREES_PASS |
| `x-g/descriptor/mirror-40961-claim-40960` | REFUSED |
| `x-g/descriptor/no-binding` | REFUSED |
| `x-g/descriptor/rewritten-after-return` | REFUSED |
## GitHub Actions

Status captured at 2026-11-20 02:50:06 PST.

| Workflow | Status | Jobs |
|---|---|---|
| [variant2](https://github.com/mpmdw/JouleWise/actions/runs/44714672257) | in_progress | 9 in_progress, 12 success |
| [variant3](https://github.com/mpmdw/JouleWise/actions/runs/44715774772) | queued | 10 in_progress, 2 queued, 9 success |
| [variant3-initial](https://github.com/mpmdw/JouleWise/actions/runs/44714678802) | cancelled | 9 cancelled |
| [ledger2](https://github.com/mpmdw/JouleWise/actions/runs/44714672194) | skipped | 1 skipped |
| [ledger3](https://github.com/mpmdw/JouleWise/actions/runs/44715774928) | skipped | 1 skipped |
| [ledger3-sync](https://github.com/mpmdw/JouleWise/actions/runs/44715774607) | skipped | 1 skipped |
| [ledger3-initial](https://github.com/mpmdw/JouleWise/actions/runs/44714679151) | skipped | 1 skipped |

| Workflow | Job | State |
|---|---|---|
| variant2 | [align-templates](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941351) | success |
| variant2 | [build](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136214890706) | success |
| variant2 | [calibration-exits-exclusive (3.13)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941387) | success |
| variant2 | [calibration-writer-crash-matrix-exclusive (3.13, 1)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941389) | success |
| variant2 | [calibration-writer-crash-matrix-exclusive (3.13, 2)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941572) | success |
| variant2 | [changes](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136214890781) | success |
| variant2 | [fences](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136214890365) | success |
| variant2 | [installed-wheel](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215671392) | success |
| variant2 | [quick](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941238) | success |
| variant2 | [test (3.13, 1)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941705) | in_progress |
| variant2 | [test (3.13, 10)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941653) | in_progress |
| variant2 | [test (3.13, 11)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941617) | in_progress |
| variant2 | [test (3.13, 12)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941714) | success |
| variant2 | [test (3.13, 2)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941620) | success |
| variant2 | [test (3.13, 3)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941640) | in_progress |
| variant2 | [test (3.13, 4)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941631) | in_progress |
| variant2 | [test (3.13, 5)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941728) | in_progress |
| variant2 | [test (3.13, 6)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941626) | success |
| variant2 | [test (3.13, 7)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941757) | in_progress |
| variant2 | [test (3.13, 8)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941725) | in_progress |
| variant2 | [test (3.13, 9)](https://github.com/mpmdw/JouleWise/actions/runs/44714672257/job/136215941660) | in_progress |
| variant3 | [align-templates](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624714) | success |
| variant3 | [build](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136218673855) | success |
| variant3 | [calibration-exits-exclusive (3.13)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624789) | success |
| variant3 | [calibration-writer-crash-matrix-exclusive (3.13, 1)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624944) | success |
| variant3 | [calibration-writer-crash-matrix-exclusive (3.13, 2)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624724) | success |
| variant3 | [changes](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136218674143) | success |
| variant3 | [fences](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136218674123) | success |
| variant3 | [installed-wheel](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136222381880) | success |
| variant3 | [quick](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624658) | success |
| variant3 | [test (3.13, 1)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624940) | in_progress |
| variant3 | [test (3.13, 10)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625216) | in_progress |
| variant3 | [test (3.13, 11)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625111) | in_progress |
| variant3 | [test (3.13, 12)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625179) | queued |
| variant3 | [test (3.13, 2)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625011) | in_progress |
| variant3 | [test (3.13, 3)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624999) | in_progress |
| variant3 | [test (3.13, 4)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624986) | in_progress |
| variant3 | [test (3.13, 5)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625036) | in_progress |
| variant3 | [test (3.13, 6)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624937) | in_progress |
| variant3 | [test (3.13, 7)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625147) | queued |
| variant3 | [test (3.13, 8)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223624928) | in_progress |
| variant3 | [test (3.13, 9)](https://github.com/mpmdw/JouleWise/actions/runs/44715774772/job/136223625017) | in_progress |
| variant3-initial | [align-templates](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136218672693) | cancelled |
| variant3-initial | [build](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136214914613) | cancelled |
| variant3-initial | [calibration-exits-exclusive](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136218672103) | cancelled |
| variant3-initial | [calibration-writer-crash-matrix-exclusive](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136218672006) | cancelled |
| variant3-initial | [changes](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136214914497) | cancelled |
| variant3-initial | [fences](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136214914201) | cancelled |
| variant3-initial | [installed-wheel](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136218672021) | cancelled |
| variant3-initial | [quick](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136218673633) | cancelled |
| variant3-initial | [test](https://github.com/mpmdw/JouleWise/actions/runs/44714678802/job/136218671701) | cancelled |
| ledger2 | [gate-ledger](https://github.com/mpmdw/JouleWise/actions/runs/44714672194/job/136214893237) | skipped |
| ledger3 | [gate-ledger](https://github.com/mpmdw/JouleWise/actions/runs/44715774928/job/136218670939) | skipped |
| ledger3-sync | [gate-ledger](https://github.com/mpmdw/JouleWise/actions/runs/44715774607/job/136218682796) | skipped |
| ledger3-initial | [gate-ledger](https://github.com/mpmdw/JouleWise/actions/runs/44714679151/job/136214992351) | skipped |

## Refetch checkpoint

The scoped refetch matched the intake snapshot for all seven component heads. The issued W1 base and protected R1 line match their intake values. The final fetch follows the exact-tree verification.
## Signing closure and lead handoff

- Update the approved executed inventory in `joulewise/align/apple/v4_registration.py`, including a strict artifact entry for `scripts/align_r1_part_c_evidence.py`. The executed-closure test identifies that helper as the missing path on variant 3. The two S/Q artifacts already have template declarations.
- Regenerate `docs/align/v4/dynamic_closure_trace.json` using `scripts/align_v4_dynamic_trace.py` and the full synthetic scenarios on the approved bytes. Bind the regenerated trace and any new strictly executed path.
- Regenerate and sign `configs/campaigns/align_v4/registration/registration_receipt.json` against the final approved code, dynamic trace and lead-owned inputs. Recheck the executed artifact keys and strict binding at the signing pin.
- Refresh the approved evaluator's refusal census in `configs/gates/hazard_refusals.json`. Variant 3 fails the refusal-site counts and executed import-scope checks. Both checks pass at issued W1 and on variants 1 and 2. The final step-4 exporter, selection and roster comparison is against the recorded step-4 checkout and the proposed signing pin.

RL-182 §1.5 places the named C1 release caller and the binding of the caller, `s_rows.py`, `rl176.py` and `rl176_phases.py` at the C1 arm gate. [RL-182 §1.5](https://github.com/mpmdw/JouleWise/blob/71a83f666024c26e89cdce09dfb7a7e80d299794/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19776)

The lead owns PR #886, the R0 binding, the recorded step-4 comparison, the two stored replays of the counted Part C and F0 run 11, final acceptance, closure regeneration, signatures and promotion. RL-183 requires the two replay verdicts and failing check names. RL-189 labels their archived native limit unattested.

### Lead rerun

From any JouleWise worktree once the component heads are final:

```sh
seat=/Volumes/JW-EXT/scratch/d-w1-candidate-rehearsal-c
run="$seat/lead-$(date +%Y%m%d-%H%M%S)"
"$seat/assemble.sh" --output "$run"
cat "$run/heads.json" "$run/variants.json"
```

For exact replay of the reviewed snapshot, use `"$seat/assemble.sh" --heads "$seat/intake/heads.json" --output "$run"` in a new output directory. The assembler produces a detached checkout and records each merge parent and tree. It stops on a protected input delta or a non-union conflict. The final lead promotion uses the accepted component objects and the recorded signing inputs.

## NEEDS_SPEC

- PR #809 round 1 used a v1 audit brief while RL-189 requires frozen v2 for the descriptor witness. This rehearsal uses the exact RL-189 v2 digest. The lead owns the next audit brief and admission decision. [PR #809](https://github.com/mpmdw/JouleWise/pull/809)
- PR #897 remains provisional until its independent fix-round disposition. [PR #897](https://github.com/mpmdw/JouleWise/pull/897)
