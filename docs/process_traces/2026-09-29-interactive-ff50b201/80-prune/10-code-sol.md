```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "PRUNE-CODE — read-only census and 52 grouped mechanism assessments; largest estimated savings are restoration proofs, launch ceremony, test migration governance, and broad byte-pin churn.",
  "workspace": {
    "base_requested": "32ff901374024defa97fc3d137c5a699423676e7",
    "base_mode": "exact",
    "head_start": "32ff901374024defa97fc3d137c5a699423676e7",
    "head_end": "32ff901374024defa97fc3d137c5a699423676e7",
    "upstream_end": "32ff901374024defa97fc3d137c5a699423676e7",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "text": "Delete automatic network-time restoration and its capture-absence proof after a cold claim-path check; leaving network time off removes the obligation that generated four fix rounds."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "text": "Thin exemption-parity governance, launch-readiness ceremony, broad source-byte pins, and syntax-level test inventories while retaining their numerical and custody invariants."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "text": "Retire inactive or duplicative machinery, including the inactive quiet-lease engine, staged scheduler, and verified-deletion protocol where fresh preserved namespaces provide the same scientific protection."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD origin/main origin/feat/2026-09-28-ntp-n1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "32ff901374024defa97fc3d137c5a699423676e7",
          "32ff901374024defa97fc3d137c5a699423676e7",
          "36e8ba6e345653e4fb4ac54f711dc49b27c1d30c"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^[0-9a-f]{40}$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --exit-code; git diff --cached --exit-code; git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git show --stat c895f28b",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [" 4 files changed, 258 insertions(+), 15 deletions(-)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "4 files changed, 258 insertions\\(\\+\\), 15 deletions\\(-\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The local origin/feat/2026-09-28-ntp-n1 tracking ref points to 36e8ba6e, not c895f28b. The requested c895f28b object exists and was inspected directly without checkout or fetch.",
      "needs": ""
    },
    {
      "id": "R2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This is a static census and targeted historical review. No test suite, measurement, live hardware probe, or mutation experiment was run. Historical catches are attributed to their records, not claimed as reproduced here.",
      "needs": "Lead cold-checks claim-path DELETE proposals before landing."
    }
  ]
}
```

PRUNE-CODE

## Findings

**F1 — should_fix:** The network-time restore obligation is the clearest overbuild. The setting protects clock-anchor validity; automatic restoration protects no measured number. Leaving it off removes the restoration marker, recovery transaction, and proof that no capture remains before ON.

**F2 — should_fix:** Several necessary scientific checks have accumulated separate systems for proving their execution, preserving their source coordinates, and migrating their fixtures. Keep the numerical checks; thin these surrounding systems.

**F3 — should_fix:** Inactive machinery and destruction proofs should earn their continued presence against a concrete scientific use. Preserving an old namespace and starting a fresh one is cheaper than proving exactly which bytes were destroyed.

### Census and counting rules

The census covered Python source plus text scripts in `joulewise/`, `scripts/`, and `tests/`. It excluded data under directories named exactly `fixtures` and cached bytecode.

| Root | Modules matching the census | Suffix-code occurrences | `*Error` / `*Refusal` raise sites |
|---|---:|---:|---:|
| `joulewise/` | 103 | 998 | 3,645 |
| `scripts/` | 82 | 338 | 1,861 |
| `tests/` | 169 | 1,129 | 477 |

These are **lexical counts**, not counts of independent gates. They include declarations, repeated literals, ordinary validation, and generic strings such as `missing`. Additional AST inspection covered 114 production, 94 script, and 284 test Python files; all parsed successfully. It also found mechanisms the suffix regex misses, including `_need` checks, `UnknownNightKind`, consumer AST guards, and shell exits.

Below, **U/R** means distinct quoted literals ending `refused|missing|stale|mismatch` / matching raise sites. Names are relative to the root; Python extensions are omitted.

<details>
<summary>Per-module production census</summary>

```text
joulewise/
adapters/__init__ 0/1; adapters/mlx_runtime 2/8; adapters/mock_runtime 2/0;
adapters/mock_spec_runtime 0/22; adapters/node_client 0/24; adapters/node_worker 2/26;
adapters/nvidia_smi 0/2; adapters/powermetrics 0/29; adapters/vllm_runtime 0/2;
aggregate 1/1; analysis_engine/__init__ 8/19; analysis_engine/artifact 1/2;
analysis_engine/claim_side_bound 7/15; analysis_engine/claims 20/1;
analysis_engine/distributions 0/12; analysis_engine/estimators 0/40;
analysis_engine/inputs 15/58; analysis_engine/multiplicity 0/12;
analysis_engine/ratio 1/8; analysis_engine/reason_kinds 0/9;
analysis_engine/registry 4/24; analysis_engine/sensitivity 0/15;
analysis_manifest 0/21; analysis_manifest_v3 17/102;
arm_readiness 36/714; arm_readiness_evidence 3/22;
arm_readiness_evidence_t0 20/17; arm_retry 10/1; authentication_io 1/19;
axi_decode_config 0/74; battery_float 2/42; benchmark_import 10/70;
benchmark_import_math 0/51; bundle 1/34; bundle_read 9/33;
calibration_bracketing 7/9; calibration_custody_worker 0/7;
calibration_epoch_continuation 4/3; calibration_exits 9/0;
calibration_ledger 4/200; campaign_generator_core 0/1;
campaign_provenance 0/4; cli 1/21; clock 0/2; clock_reference 0/1;
coldgate_receipt 0/8; controller 2/30; cooldown_anchor 5/0;
corecaptured_loop 0/4; detection_floor 5/62; detection_floor_registry 0/24;
determinism_gate 9/5; doctor 0/1; dominance_closeout 7/36;
envelope_gate 8/2; environment 0/14; environment_admission 1/3;
evidence_night 1/27; floor_extraction 6/34; floor_mint_estimator 0/46;
gensuite/__init__ 0/33; identity_pins 1/158; idle_admission 3/14;
idle_dependence 1/6; interfaces 0/9; kv_size 0/12;
load_transition_alignment 2/57; measurement_liveness 0/9;
model_panel 2/10; night_agent_install 1/44; night_gate 4/121;
night_plan_writer 0/2; output_identity 3/40; paper_custody 9/75;
paper_rendering 1/5; paper_reported_energy 11/45; phase_share 0/11;
powermetrics_fiducial 1/61; publication_privacy 1/58;
quiet_admission 0/34; quiet_guard 7/85; quiet_guard_process 0/52;
quiet_predicate_campaign 3/46; receipt_oracle 0/2; reduce 11/26;
report 0/2; salvage_dangler 0/133; sampler_teardown 0/5;
scheduler_gates 6/67; schemas 2/60; scored_packer 0/6;
scored_reduce 1/1; scored_registration 0/5; suite 0/49;
t0_rehearsal 1/101; uncertainty_evidence 0/12; validation 0/3;
whole_window 20/58; window_duration_margins 3/25;
workload_profile 2/8; workload_sizing 0/6; workloads 0/9;
zero_capture_facts 0/6

scripts/
admit_model_panel_entry 15/4; analyze_phase_share 1/0;
author_arm_evidence_t0 1/1; author_arm_readiness_evidence 1/1;
axi_sb_static_batch_spike 3/3; axi_sc_spec_decode_spike 7/0;
backup_runs.sh 1/0; bench_replay_start_drift 0/8; bridge 1/130;
build_bracket_binding 3/14; build_d165_dominance_closeout 0/5;
build_family_marker 2/0; build_site 1/4; build_v4_histsem_pinset 0/31;
calibration_cadence_report 0/19; calibration_ledger_backfill 0/5;
calibration_ledger_bootstrap 0/19; capture_t0_step 1/3;
characterize_load_transition 0/3; check_campaign_generator_core_parity 0/1;
check_gate_ledger 0/1; check_paper_replay_fence 0/11;
check_paper_round7_artifacts 1/50; check_sealed_bundle_compatibility 0/12;
check_window_provenance 3/1; claims_lint 0/18; corpus_compat_receipt 3/1;
dependence_sensitivity 0/45; derive_estate_anchors 3/0;
epoch_equivalence_check 0/23; fixture_orphan_census 0/9;
floor_reconciliation_receipt 0/9; gen_derivation_night 0/35;
gen_evidence_night 0/7; gen_g2_phase_d 1/6; gen_state 0/1;
generate_arm_readiness 0/4; generate_g2a_probe_inputs 21/89;
generate_matrix 0/11; hydrate_d117_fixture 0/41;
issue_calibration_acceptance_generation 1/100;
issue_dg071_dg075_statistics 5/1; issue_epoch_continuation 0/1;
issue_g2a_prefill_prompt_pin 12/59; launch_window 4/20;
magistrate_watchdog 0/23; mint_floor_artifact 0/149;
mint_floor_artifact_generalized 0/237;
night_chains/calibration_derivation_only.zsh 1/0; pack_capsule 2/43;
package_bundle_pack 0/19; package_d117_fixture 0/32;
paper/partial_record_enclosure 2/15; paper_anchor_correction_quantified 4/2;
paper_excursion_decomposition 0/1; paper_prefill_resolvability_projection 0/1;
paper_renumber_refs 0/7; paper_terms_lint 1/2; quick_suite 0/5;
quiet_guard 1/1; quiet_guard_privileged 2/5; reauthor_clean 6/9;
recover_calibration_ledger 0/6; refresh_receipt_histsem_pinset 2/2;
rehearse_t0_unattended 0/22; reissue_calibration_acceptance 1/17;
release_check 0/7; render_results_fills 1/22; replay_powermetrics_frames 0/1;
reserve_calibration_window_bracket 2/11; run_campaign 28/104;
run_night 3/70; sample_quiet_predicate_evidence 1/33;
select_g2a_prefill_length 1/12; shard_tests 0/37;
sim_acc_25g83_rev5 0/3; spike_mlx_prompt_cache 0/18;
summarize_g2a_prefill_probe 2/73; validate_gate_packet 8/4;
validate_powermetrics_fiducial 5/53; verify_family_marker 2/0;
write_derivation_night_inputs 1/9
```

</details>

<details>
<summary>Per-module test census</summary>

```text
tests/
calibration_exits_fixtures/custody_hang 0/3;
calibration_exits_fixtures/fake_sampler 0/1;
night_gate_fixtures/bind_supervision 0/3; owned_process_runner 0/31;
receipt_corpus 0/4; scored_case_generator 0/1; scored_ownership_generator 0/1;
scored_reduce_checker 2/0; scored_roster_checker 0/1;
test_2k_amplification 0/5; test_acc_25g83_rev5 0/1;
test_admit_model_panel_entry 3/0; test_agent_census_concurrency 0/1;
test_aggregate 1/0; test_analysis_claims 7/1; test_analysis_finalizer 4/3;
test_analysis_inputs 1/0; test_analysis_integration 17/5;
test_analysis_manifest_v3 3/0; test_analysis_multiplicity 3/0;
test_analysis_ratio_integration 1/1; test_arm_census 0/1;
test_arm_readiness 9/2; test_arm_readiness_dry_run 3/1;
test_arm_readiness_evidence 2/0; test_arm_readiness_evidence_author 1/0;
test_arm_readiness_evidence_t0 22/3; test_arm_readiness_integration 25/2;
test_arm_readiness_lifecycle 6/2; test_arm_readiness_pack_digest 1/0;
test_arm_readiness_schemas 5/0; test_arm_retry 10/0;
test_audit_bundle_validation 0/1; test_audit_cli_examples 0/1;
test_axi_analysis_manifest 4/0; test_axi_controller_events 1/0;
test_axi_mock_spec 1/0; test_axi_output_identity 3/0;
test_axi_request_validation 7/0; test_axi_sb_spike 3/0;
test_axi_sc_spike 3/0; test_battery_float 3/1; test_benchmark_import 1/0;
test_bracket_binding_cli 3/4; test_bridge 0/1; test_bundle 2/6;
test_bundle_read 3/0; test_calibration_bracketing 7/2;
test_calibration_exits 5/22; test_calibration_ledger 6/7;
test_calibration_ledger_custody 1/4; test_calibration_live_three_window 8/9;
test_calibration_writer_crash_matrix 0/9; test_capture_t0_step 2/1;
test_check_window_provenance 4/2; test_claim_side_bound 9/0;
test_cli 1/0; test_cli_run 3/0; test_codex_app_bridge 0/2;
test_coldgate_receipt 0/1; test_collector_analysis_manifest_id 3/4;
test_controller 2/7; test_custody_mode_inventory 0/4;
test_d117_contrast_v5_pack 14/2; test_d117_decode_contrast_plan 2/7;
test_d117_fixture_transport 1/1; test_d117_floor_qwen25_1p5b_plan 0/2;
test_d117_floor_qwen25_7b_plan 0/2; test_d117_floor_qwen3_v5_generate 3/0;
test_d117_gamma_d139a2_families 0/1; test_d117_v3_family 0/1;
test_d165_dominance_closeout 7/1; test_d165_rationale_census 0/10;
test_dependence_sensitivity 0/1; test_derive_estate_anchors 2/0;
test_detection_floor 8/1; test_determinism_gate 9/2;
test_docs_freshness 0/4; test_environment 0/9; test_epoch_continuation 8/0;
test_evidence_night 2/6; test_experiment 4/3; test_family_marker 15/3;
test_floor_extraction 5/0; test_floor_mint_estimator 1/2;
test_gate_sensibility_rounding 1/0; test_gen_derivation_night 1/1;
test_gen_evidence_night 1/0; test_generate_g2a_probe_inputs 8/1;
test_generate_matrix 1/0; test_identity_pins 1/1; test_idle_admission 3/0;
test_idle_dependence 1/0; test_install_night_agent 3/1;
test_issue_calibration_acceptance_generation 4/1;
test_issue_dg071_dg075_statistics 7/4; test_issue_g2a_prefill_prompt_pin 4/0;
test_launch_window 7/4; test_launcher_argv_regression 1/5;
test_load_transition_alignment 1/0; test_magistrate_watchdog 2/1;
test_measurement_liveness 1/2; test_midcampaign_cure_generation_docs 0/1;
test_mint_analysis_admission 1/0; test_mint_floor_artifact 3/0;
test_mint_floor_artifact_generalized 7/41; test_mlx_runtime 3/5;
test_mock_adapters 2/0; test_model_panel 1/0; test_modularity 1/0;
test_night_agent_install 3/8; test_night_gate 4/1;
test_node_client 0/3; test_node_worker 3/6; test_nvidia_smi 0/1;
test_p2038_production_path 1/0; test_pack_capsule 2/0;
test_paper_comparison_contract 0/26; test_paper_comparison_placements 0/23;
test_paper_custody 9/5; test_paper_excursion_decomposition 0/1;
test_paper_first_use_ledger 0/3; test_paper_rendering 1/0;
test_paper_reported_energy 8/1; test_paper_round7_artifacts 0/2;
test_paper_terms_lint 0/1; test_partial_record_enclosure 2/0;
test_pipeline_smoke_tail 0/1; test_powermetrics 0/5;
test_powermetrics_fiducial 7/2; test_preregistration_chain_digest 0/1;
test_quiet_admission 0/3; test_quiet_guard 7/3;
test_quiet_guard_process 0/2; test_quiet_predicate_campaign 2/6;
test_r4_acceptance_oracle 0/1; test_reauthor_clean 5/0;
test_receipt_histsem 4/4; test_reduce 7/5; test_render_results_fills 2/1;
test_revision_five_b_readers 0/2; test_run_campaign 21/6;
test_run_night 8/13; test_s0_line_audit_guard 0/5;
test_salvage_dangler 1/0; test_sample_quiet_predicate_evidence 3/4;
test_scheduler_gates 7/2; test_schemas 2/0;
test_scored_packer_fuzz 1/0; test_scored_reduce 1/1;
test_select_g2a_prefill_length 1/0; test_shard_tests 0/1;
test_single_count_discipline_census 0/13;
test_single_count_discipline_matrix 2/6; test_suite_control_parity 1/1;
test_summarize_g2a_prefill_probe 0/1; test_supersession_cross_consumer 1/1;
test_t0_rehearsal 2/0; test_validate_gate_packet 10/0;
test_validate_powermetrics_fiducial 2/2;
test_validate_powermetrics_fiducial_derivation_only 2/1;
test_vllm_runtime 0/1; test_whole_window 1/0;
test_whole_window_selection 3/4; test_window_duration_margins 3/0;
test_window_env_allowlist 0/4; test_workload_profile 2/0;
test_zero_capture_facts 1/0; verify_calibration_acceptance_corpus 0/7
```

</details>

### Mechanism table

**N** = recorded defect in a measured number or primary custody; **E** = defect in enforcement itself; **X** = planted fault, mutation, or synthetic reproduction. **—** means no demonstrated catch located in the inspected record set, not “never caught anything.”

Ordering is an **estimate of historical cost**, largest first. Shared repair campaigns are not additive. “Unknown” costs were not converted into invented hours or seat counts. **CF** means a DELETE touches a claim or claim-custody path and needs a cold Fable check before landing.

| ID | What it is / location | Number protected; failure without it | Actual catches, separated | Cost, historical and ongoing | Cheaper equivalent; loss | Verdict; deciding reason |
|---|---|---|---|---|---|---|
| M01 | Arm readiness proves a registry of prerequisites before issuing and consuming GO. `joulewise/arm_readiness.py:1`, `arm_readiness_evidence*.py`, `t0_rehearsal.py`. | J/request and floors: collection must use the intended pack, boot and machine state. Documentary review membership does not independently change J. | N—; E≥2 permanently present daemon/service false refusals [A]; numerous lineage/receipt mutation catches. | Very high, estimated: 12,898-line owner plus authoring/rehearsal systems; liveness 600→610 s repair; every freeze, ARM, consume and replay. | One sealed plan, authenticated science inputs, fresh physical checks and one-use launch. Cut duplicate review-message, evidence-lifecycle and replay ceremonies; lose fine-grained documentary receipts. | **THIN** — core identity/state checks matter; the full prerequisite bureaucracy is not numerically independent. |
| M02 | Acceptance issuance reconstructs calibration operatives and admits physical identity epochs. `calibration_bracketing.py`, `issue_calibration_acceptance_generation.py`, `reissue_calibration_acceptance.py`, `epoch_equivalence_check.py`. | Calibration S/C and transferred timing allowance: stale physics or selective retained members could understate uncertainty. | N: arithmetic repair history `509335538`; X: derivation/quantile/trigger mutations in `501bde4fa`; E: repeated candidate-schema and trigger repairs. | High, shared issuance campaigns; generation-specific registry, Decimal proofs, sealed inputs and reissuance on changes. | One frozen derivation from complete raw roster, explicit physical epoch, independently checked S/C. Narrow change triggers; lose some automatic field-by-field attestation. | **THIN** — retain derivation and physical transfer; trim attestations unrelated to changed physics. |
| M03 | Two test-only parity switches restore older fixture exemptions by granted test ID. **Branch-only:** `tests/bfgs_fixtures.py`, `f0766620c`. | None directly. The retained battery/mock/config gates protect J from synthetic evidence. | N0 demonstrated on this unmerged route; E: first switch missed the second exemption form; reference “repair” broke NEG-8; X charging/config defects remain red [B]. | Very high: 533 failing outcomes in initial scout; about 510 non-pin failures; multiple repair rounds, four repair seats, helper seats and cold rulings [B,C]. Every granted ID/list change adds governance. | Tests at the actual layer boundary, with one valid fixture factory and explicit test doubles. Remove two interacting exemption registries and per-ID authorization; lose assertion-byte preservation as a universal migration rule. | **THIN** — this preserves old test behavior, not additional measurement truth. |
| M04 | Paper custody authenticates suppliers and manufactures frozen issuing/fixture capabilities. `paper_custody.py:1`, `authentication_io.py`, `paper_rendering.py`. | Published energy, bounds and ratios: a supplier must not substitute unissued, changed or fixture values. | N—; E: bypass/read-routing/capability faults; rounds recorded by `2df32d5c1`, `f2d35b4f7`, `01d005919`, `710b6c776`; X coherent reseals and forged capabilities. | At least six named rounds; five family types, supplier census, issuance registry and renderer grants; every supplier/validator edit. | One authenticated reader, ordinary frozen results, explicit issued-versus-fixture status, numerical replay. Cut custom capability/getattribute machinery and redundant inventories; lose resistance to deliberate same-process object forgery. | **THIN** — provenance matters; a second in-process security architecture is expensive. |
| M05 | The installer proves launchd job state through transactions and typed absence capabilities. `night_agent_install.py:1`, `install_night_agent.sh`. | Capture custody and planned sample coverage: overlapping or surviving jobs can contaminate or duplicate collection. | N—; E: shutdown/signal/state defects through round 8; live launchctl smoke finally passed [D]. | Eight-round arc [D]; 1,405-line installer, 2,400-line test instrument; every installation/uninstallation. | A single install transaction, exact label verification and explicit clean retry. Retain absence checks; reduce interruption/recovery states. Lose elaborate interrupted-install resumption. | **THIN** — job-state truth is necessary; the full recovery algebra is not. |
| M06 | The calibration ledger authenticates every attempt and repeatedly replays custody under deadlines. `calibration_ledger.py:1`, `calibration_custody_worker.py`, reserve/recover tools. | S/C population and calibration custody: omitted attempts, rollback or substituted captures change the accepted distribution. | N—; E: unbounded reads, redundant passes, wrong timeout/refusal transport; X FIFO hang and custody mutations. `b396fdd6e`, `52274fc3a`, `cd0a8d2bd`, `98ad7946e`. | Multiple structural/fix rounds; whole-corpus passes reduced four→two, honest worst case three; every slot still pays replay/budget costs. | Preserve append chain, complete attempts and sealed hashes; authenticate immutable inputs once per operation, invalidate on actual mutation. Lose repeated re-verification of unchanged bytes. | **THIN** — ledger completeness is load-bearing; replay repetition is not a separate invariant. |
| M07 | NTP N1 turns time sync off, later queries logs, restores ON and proves captures absent before restoration. **Branch:** `network_time_window.py`, `run_night.py` at `c895f28b`. | OFF protects anchor/B validity. Automatic ON and its proof protect **no number** once the dedicated Mac remains OFF. | N0 from N1 itself, not launched in inspected ruling; causal diagnosis found four clock-step exclusions. E: continuation parsing, surviving children, empty claims, disagreeing refusal records, ambiguous census [E]. | **Four fix rounds:** `60a8df22e`, `c8995f4b9`, `36e8ba6e3`, `c895f28b`; cold rulings. Relative to main: 2,648 insertions/49 deletions across 10 code/test files. Every night/recovery pays. | Turn OFF and leave OFF; retain existing clock-model rejection and minimum required attestation. Lose automatic restoration and recovery receipts, which the owner does not need. | **DELETE restoration/proof — CF.** The obligation disappears with the cheaper control. |
| M08 | An inactive quiet-lease engine maintains durable leases, registries and kernel recovery. `quiet_guard.py:1`, `scripts/quiet_guard*.py`, `setup_quiet_guard.sh`. | None currently: production lease promotion is explicitly inactive. Shared process primitives have active users elsewhere. | N—; E≥17 initial/follow-up enforcement findings: seven-blocker checkpoint, ten-finding cure, further recovery changes; no demonstrated science catch. | Multiple fixes and redesign: `d48286918` → `e0acaf755` → `1a3f3c1e8` → `84ec5d312` → `0410d3e20`; ongoing inactive-state tests. | Retire the inactive engine and setup clients; retain `quiet_guard_process.py` for active census users. Lose a shelved lease/recovery implementation. | **DELETE engine only** — inactive machinery protects no present number. |
| M09 | Whole-file source hashes and historical fixture pins make code changes trigger refusals or re-derivation. Acceptance estimator pins, mint-core pins, generator head pins. | Mathematical implementation identity protects B and floors; comments, line shifts and unrelated helper edits do not. | N— for cosmetic-byte changes; E: legitimate ledger advancement broke twelve generators; raw-digest improvement hit reducer/bundle pin fences [F,G]. | High recurring churn: 76→176 ledger advance required two fixture rounds; new digest work blocked by pinned files; every byte edit. | Pin a stable scientific computation boundary and its dependencies; keep raw/artifact hashes. Lose detection of scientifically irrelevant source edits. | **THIN** — discriminate changed science from changed file bytes. |
| M10 | Reauthor cleanup proves the exact bytes unlinked through immutable flags, inode/Fd custody and hash-chained events. `scripts/reauthor_clean.py`. | None if old namespaces are preserved and never reused. Its number is a destruction receipt, not a measurement. | N—; E: two repeated hash-then-destroy races and one terminal-replay blocker; `073c8bc47`. | Two refuted rounds → consult → third implementation → delta blocker; 2,389 script lines + 985 test lines at introduction. Every reauthor cleanup. | Rename/preserve the old namespace; create a fresh, uniquely named namespace. Lose verified logical-deletion receipts; retain more disk usage. | **DELETE — CF.** Preservation removes the destructive operation requiring proof. |
| M11 | Whole-window joins recompute admissions, membership, supersessions and NEG-8 evidence. `whole_window.py:1`, `salvage_dangler.py`. | Floors and treatment differences: selective retries, missing members or stale drift allowances can create false effects. | N— located; X custody, omitted membership, supersession and drift mutations; E fixture coupling in [B,C]. | 6,129-line join plus exceptional salvage route; replay at extraction/mint/claims; large fixture migration cost shared with M03. | No equivalent that drops population custody. Keep one authoritative join and explicit rare salvage; consolidate duplicated consumer recomputation. | **KEEP core** — outcome selection and drift directly affect the estimate. |
| M12 | Quiet-predicate evidence campaigns enforce registration, slot timing, exclusions and cleanup. `quiet_predicate_campaign.py`, sample/bench replay tools and evidence chain. | Measured observer-energy relation and any future admission cutoff; partial or contaminated envelopes would distort it. | N— located; E multiple harness/replay repairs, including tests requiring more than the ruled criterion; record `2026-09-19-activation-d0b83820/20-…`. | At least four harness fix rounds in that record; long real-process fixture runs; per-envelope journals and custody. | Registered raw collection plus one reducer implementing the ruled inclusion rule. Remove unrelated harness admissibility conditions; lose auxiliary diagnostics. | **THIN** — preserve the experiment, avoid new evidence gates beyond its registered question. |
| M13 | The magistrate watchdog schedules agent stand-down and releases holds after proved zero-capture refusals. `scripts/magistrate_watchdog.py`. | J and quiet evidence: agents must be absent during capture. Early-release bookkeeping itself protects no number. | N—; E unsafe early-release conditions repaired in `4c76ab697`, `3e27057a9`, `458898850`; X capture-file/symlink cases. | Repeated release fixes; lead timing reached round 4 (`640f7cc4a`); every plan and 10-second resident poll. | One agent stand-down interval with capture-side census; release a failed plan manually or from one authoritative terminal record. Lose automatic early relaunch. | **THIN** — agent exclusion matters; nested scheduling and release machinery can shrink. |
| M14 | Historical-semantics pinsets replay old pack blobs against current consumers. `arm_readiness.py:3318`, `build_v4_histsem_pinset.py`, `verify_receipt_histsem.py`. | Historical floor/claim reproducibility: an old artifact must retain its original interpretation. | N— located; E source-coordinate/pin drift; performance repair `6f4b04112`. | 2,325 blobs across 18 coordinates; batching improved CLI 73.5→59.7 s; identity design took four rounds, consult and cold gate [H]. | Frozen protocol/version dispatch plus numerical replay fixtures. Drop redundant current-coordinate pin layers; lose detailed historical-source correspondence. | **THIN** — preserve historical math, not every historical coordinate. |
| M15 | Calibration-exit tests require a closed refusal inventory, owned executed witnesses and interprocedural provenance. `tests/test_calibration_exits.py`, `receipt_provenance_analyzer.py`. | Typed exits preserve failed attempts; AST witness ownership does not itself determine S/C. | N—; E acknowledgement flakes, torn fixture events, decoy nondeterminism, witness cache falsely executing 0/73 on a second run [G]; related commits `42df510f8`, `88d67d606`. | 6,285-line test module; recorded whole-module runs 488/532 s; repeated fixture fixes; every refusal addition. | End-to-end tests for each consequential exit category, plus complete enum mapping. Remove per-witness AST provenance and duplicate shape inventories; lose exhaustive syntactic proof of witness ownership. | **THIN** — test observable custody/exit behavior rather than a second execution-accounting language. |
| M16 | Identity projection freezes model, prompt, stack and config sets. `identity_pins.py:233`, model/workload loaders and projection tests. | J/request, J/token and comparisons: changed models/prompts or mismatched arms invalidate comparability. | N— located; X swapped sets, tokenizer/config mutations; E repeated roster/projection formulations [H], `d0e593512`, `3ac6cffb1`. | Four-round identity-design arc plus consult/cold gate [H]; every pack/model/tokenizer change. | No equivalent omitting content identity. Use one canonical identity object shared by producer/consumer; cut mirrors. | **KEEP core** — the compared workload must actually be the registered workload. |
| M17 | Single-count metadata has versioned canonical objects, accessor rules and an AST/text reader census. `detection_floor.py:390`, `tests/test_single_count_discipline_census.py`. | Attribution floor and claim uncertainty must both remain present. The object explicitly says `gating:false` and “prospective sizing diagnostic.” | N—; E census repairs and pass-through classification; `a76d30edf`, `973f3827c`, `e2c3e0611`, `9d854b4d7`; X malformed metadata. | 1,190-line census plus corruption matrix, manifest and source pins; every reader/wording change. | Keep numerical composition tests and one canonical producer/validator. Drop normalized-AST/count pins for every metadata reader. Lose syntactic regrowth detection. | **THIN** — arithmetic is load-bearing; exhaustive policing of its explanatory metadata is weaker value. |
| M18 | Arm/process census tests create live decoys and constrain service-basename matching. `arm_census.py`, T0 census tests, `test_agent_census_concurrency.py`. | Agent contamination can raise J. Particular decoy topology and unrelated host-process assertions do not. | N—; E false Apple-service matches, disappearing-hit race and second-snapshot race; final deterministic decoys cured it [A,I]. | Three-round arm-census arc; review→delta→consult→final review for decoys [I]; every regex/platform dialect change. | Committed realistic process snapshots plus a small native positive/negative smoke. Lose exhaustive live decoy combinations and host-race coverage. | **THIN** — keep agent detection; concentrate live tests on the OS seam. |
| M19 | Paper comparison/placement tests mirror exact obligation rows, prose and closed applicability vocabularies. `test_paper_comparison_contract.py`, `test_paper_comparison_placements.py`. | Some labels prevent unsupported claims; mirrored proposal text does not validate the printed quantities. | N—; E major coverage gap: corrupt worked-example literals passed broader placement checks [G]; X proposal/retirement mutations. | Multiple paper repair arcs; every row/phrase change; broader R7F run recorded at about 7.5 minutes [G]. | One adopted claim-to-source map and numeric/label renderer checks. Delete duplicate proposal-agreement and retired-row mirrors. Lose proof that multiple documents repeat identical policy. | **DELETE duplicate mirrors — CF.** Replace them with checks at the published claim boundary. |
| M20 | Cold packets require exact charter/exhibit hashes and durable validator receipts. `validate_gate_packet.py`, `coldgate_receipt.py`, charter tests. | None directly; evidentiary hygiene for adjudication. | N—; E CRLF “byte-equality” test accepted altered bytes; charter typo refused [J]; X directory-swap/collision cases. | Packet preparation on every cold gate; charter candidate/activation work; custom publication durability states. | Frozen packet manifest, one hash verification and ordinary exclusive atomic receipt. Lose some filesystem race diagnostics and duplicate charter-text checks. | **THIN** — retain exact reviewed packet identity; simplify its delivery protocol. |
| M21 | Git-fixture AST rules forbid direct initialization outside exact approved helpers. `test_git_fixture_maintenance.py`, `test_git_fixture_hygiene.py`, `git_fixture.py`. | None/process hygiene; detached Git maintenance can pollute tests or leave agent load. | N—; E guard missed support modules, then exempted nested basename collisions [K]. | Two fix rounds and delta audits; recursive AST/constant-folding checks on every suite. | Shared fixture factory with maintenance disabled and a small direct-init lint. Remove complex command interpretation and exemption machinery. Lose detection of deliberately obfuscated initialization. | **THIN** — keep the safe fixture factory; reduce the policing language. |
| M22 | Arm retry classifies aborts and demands exact notice/head/history conditions for successors. `arm_retry.py:98`. | Sample selection: retries after physics failures must not silently select favorable outcomes. Process-only abort spacing/notice details do not change J. | N—; E three-round policy/guard repairs; [L]. | Three-round arc; every new refusal mirrored in code, handback and tests. | Retry only explicit zero-capture failures; preserve attempt history. One reason table, fewer notice transcriptions and mirrored prose checks. Lose some automatic successor eligibility. | **THIN** — keep selection safeguards; reduce policy duplication. |
| M23 | Backups, custody-store manifests and transport archives verify retained evidence. `backup_runs.sh`, package/hydrate tools, ledger custody-store readers. | Every replayed J/B/floor: missing or substituted raw bytes destroy reproducibility. | N— quantified in read set; E custody destruction/provenance repair history `868fbd608`, `4aff4cb1c`; X archive/path/digest attacks. | Historical three-round retention arc; hashing/storage/transport per corpus. | Content-addressed immutable archive and verified restore. No cheaper equivalent dropping the bytes or digest. | **KEEP** — primary evidence custody is necessary. |
| M24 | Floor extraction and minting authenticate inputs, dispatch the registered estimator and compare recomputed values. `floor_extraction.py`, `floor_mint_estimator.py`, `mint_floor_artifact*.py`. | Published false-effect floor in J: wrong estimator, omitted terms or understated cached values could admit false claims. | N— located; **X3** one-ULP understatement variants refused by exact mint equality; E margin reader rejected legitimate estimator vocabulary [M]. | Large shared authentication surface; 149/237 raise sites in original/generalized mint; extraction/mint replay per issuance. | No equivalent dropping source authentication or exact recomputation. Share one mint core and preserve typed estimator authority. | **KEEP** — directly prevents an understated floor. |
| M25 | Clock/phase evidence requires valid anchor domains, interval support, causal-bound composition and adequate trace tails. `uncertainty_evidence.py`, `reduce.py`, fiducial/alignment modules. | Energy integrals and B: misplaced frames, unweighted intervals or omitted timing terms bias J and uncertainty. | **N≥2 numerical defect classes:** duration weighting (`14eff51cf`) and additive causal composition (`509335538`). Clock stabilization records two failed captures at 5.544/7.769 ms. | D-078 two convergence rounds with five fresh audits recorded in `509335538`; per-bundle checks and pulse replay. | No equivalent that assumes exact timing. Simplify implementation boundaries without changing the inequalities or raw evidence. | **KEEP** — timing errors become energy errors. |
| M26 | Claim evaluation applies paired estimators, both uncertainty gates, fixed multiplicity and sensitivity rules. `analysis_engine/*`. | Published effect, CI, significance/equivalence: unpaired observations or omitted uncertainty/multiplicity overstate support. | N— located; X hand-computed arithmetic and rejection fixtures; floor-consumption attacks [M]. | Per-contrast derivation; frozen families and closed outcome/reason mappings. Historical attributable cost not isolated. | No equivalent dropping registered statistical rules. Keep pure arithmetic and one input boundary. | **KEEP** — these determine the scientific conclusion. |
| M27 | Analysis registries/manifests freeze sample cardinality, order, attempts and finalization attachments. `analysis_manifest*.py`, registry and campaign runner. | Effect/floor estimate: outcome-dependent samples or substituted member sets bias it. | N— located; E finalization fixture digest migration [C]; X missing cover/order/identity attachments. | Large validator surface; prospective→finalized schemas and per-family fixtures; every registration. | A single immutable registration plus complete observed-attempt ledger. Version dispatch can remain; merge redundant validation passes. | **KEEP core** — prevents outcome-driven selection. |
| M28 | Battery float checks exact ioreg bytes, physical predicates, bracketing spans and committed verdicts. `battery_float.py:257`, consumer/sweep tests. | Calibration B/S/C and J: charging state can confound measurements and transfer assumptions. | N— quantified; X nine recorded-type negatives formerly passed, CR/byte and consumer bypass cases [N]; E parser/consumer defects through seat round 6 and 7b. | High parser/consumer arc; frozen function-source tests, AST primitive census, observe/B-reader sweeps; every capture and reader change. | Keep freshness, charging/current predicates, span and raw digest. Parse the required fields strictly; reduce rejection rules for irrelevant properties and duplicate static sweeps. Lose full-document grammar assurance. | **THIN** — physical state is necessary; every unrelated ioreg atom is not equally relevant. |
| M29 | Environment, CPU idle, cooldown and thermal gates reject contaminated runs. `environment*.py`, `idle_admission.py`, controller/cooldown modules, `prewindow_check.sh`. | J/request and floor calibration: background work, screensaver or heat changes energy/throughput. | **N:** screensaver contaminated 43/50 suite bundles, approximately +30% energy/−11% throughput (`RUN_STATE.md`, July-17 checkpoint); XProtect at 94% CPU caused real admission refusal. E D-077 eight-round anchor/enforcement arc. | High historical repair cost; preparation and per-member observations. Prewindow duplicates later admission but saves failed launches. | Disable the known screensaver permanently; retain physical state and load admission. A light readiness warning can replace some duplicate blocking probes. | **KEEP core** — demonstrated contamination of measured numbers. |
| M30 | Sampler ownership, identity, teardown and escape census prevent residual measurement children. `sampler_teardown.py`, telemetry adapters, evidence process journal. | J and raw trace custody: extra samplers/load contaminate later captures; wrong PID signals corrupt ownership. | N— located; X real child/group teardown tests; E NTP’s external proof failures show why owned children matter [E]. | Per sampler start/stop, signal grace, census and journals. | One owned supervisor/process group with explicit stop proof. Keep identity checks; avoid duplicated outer proofs. | **KEEP** — persistent capture processes affect later numbers. |
| M31 | Acquisition markers block status publication while a measurement is live or unknown. `measurement_liveness.py:1`, `window_status.sh`. | J: status Git/network activity during capture adds load. | N— located; E argv classifier retired for marker/identity census (`a2cfb644c`); X liveness mutations. | Rewrite plus registry/identity integration; every status publication and measurement owner. | Queue status writes until capture completion using the same owner state. Lose immediate status availability during capture. | **KEEP core** — prevents known contaminating work from overlapping capture. |
| M32 | Night gate validates plan freshness, checkout, chain bytes, registration, clock and physical state. `night_gate.py:1201`, `run_night.py`. | J/custody: wrong code/plan or out-of-window capture cannot support the intended experiment. Arbitrary plan age and directory placement do not independently correct J. | N— located; E dirty-clone check gap fixed in PR #403; many synthetic malformed-plan/chain cases. | Per-night full preflight and repeated probes; head/path/age failures demand recuts. | Seal executable inputs and use actual launch/capture deadlines. Reduce unrelated directory/age restrictions and duplicate head checks. Lose some uniform operating conventions. | **THIN** — exact experiment identity matters more than ceremonial freshness. |
| M33 | A staged seven-gate scheduler always returns NO-GO because several stages remain unimplemented. `scheduler_gates.py:984`. | None through an active caller found in production/scripts; boot/pack checks already exist elsewhere. | N—; E staged diagnostics/lane repairs in `40bb7a361`, `b1c6beedc`; X staged receipt tests. | 1,078 production lines plus test module, schema and closed vocabulary; maintained without an active launch route found. | Retire the staged façade; keep active gate implementations in the actual launch route. Lose a future scheduler scaffold. | **DELETE — CF** — redundant inactive gate architecture. |
| M34 | Zero-capture facts and successor writers prove no capture happened before retry/release. `zero_capture_facts.py`, watchdog and evidence-night routes. | Sample selection/custody: a “zero capture” retry must not conceal outcomes. | N—; E file/symlink/early-release gaps fixed in `3e27057a9`, `458898850`, `6d1e004ff`; X planted files/markers. | Several fixes and coupled driver/watchdog/retry states; per failed night. | One immutable attempt terminal record written by the capture owner, backed by complete attempt ledger. Lose automatic inference from multiple filesystem namespaces. | **THIN** — preserve the fact, consolidate its producers and consumers. |
| M35 | Family publication markers and launch consumption bind the approved pack and enforce one-use launches. `arm_readiness.py`, family-marker/launch tools. | Floor/effect custody: wrong family or repeated use can mix datasets and authorizations. | N— located; X marker/digest/class/purpose and concurrent-consumption cases; E D-176 integration repairs. | Multiple linked schemas and hash points; every publication and launch. | One sealed pack identity plus atomic consumption and persisted lineage. Cut redundant digest points where the same immutable bytes are reread. | **KEEP core** — approved identity and one-use semantics protect custody. |
| M36 | Pre/post calibration brackets apply registered screens and distribution-transfer assumptions. `calibration_bracketing.py:1965`, bracket-binding tools. | B allowance, then J uncertainty: stale or unmatched instrument calibration can understate it. | N— located; X stale/mismatched bracket and acceptance tests; real clock corrections caused exclusions [E]. | Two captures per governed bracket, bound reconstruction and ledger join. | No equivalent using no transfer evidence. Keep explicit epoch and screen rules. | **KEEP** — calibration cannot silently transfer across changed conditions. |
| M37 | Issuing defaults prohibit backup-root replacement; explicit read-replay opt-ins are censused. Ledger readers; `test_custody_mode_inventory.py`. | Issued S/C/floor custody: replacement bytes must not become newly issued evidence. | N—; **E≥3 recurring issuing-mode leaks** recorded by locator ruling; X valid planted replacement refused after default inversion [O]. | Parts 1–7, cold gates, per-call AST kwargs interpretation and allowlists; every reader refactor. | Separate issuing reader from replay reader, so capability/API choice enforces the boundary. Keep a small integration test; drop kwargs interpretation census. | **THIN** — strong API separation can replace a second static mode system. |
| M38 | Test launch fence blocks real sudo/powermetrics and reports swallowed attempts. **Branch-only:** `sampler_launch_fence.py`, `478f57099`, `069df7193`. | Quiet-machine measurements: a test must not launch real telemetry/load. | **N/custody prevention:** real sampler launches found during whole-module testing, item 124; E missing module coverage; a later sighting was a decoy, item 146 [G]. | 580 added lines initially; follow-up wiring and recorder sweeps. Every test process/module currently installs guards. | One test-runner-level OS-command fence with explicit opt-in for authorized live tests. Lose duplicated module wiring. | **KEEP core** — it caught an actual unsafe hardware launch. |
| M39 | Scored registrations, rosters, retries and reducers preserve item ownership, score rows and capture-window attribution. `scored_registration.py`, `scored_packer.py`, `scored_reduce.py`. | Headline J/correct and accuracy: missing attempts, double ownership or wrong denominators alter both. | N— located; X independent checker, ownership forgeries, resealed fuzz and arithmetic witnesses. | Extensive checker/generator/fuzz/stress system; every pack/requeue/reduction. | No equivalent dropping conservation, complete roster or raw window attribution. Keep independent numerical oracle; reduce duplicate AST placement checks. | **KEEP** — directly protects headline numerator and denominator. |
| M40 | Benchmark/prompt/token/output identity checks bind source examples, tokenizer bytes, realized requests and responses. Benchmark import, suite, output identity, model/workload/profile modules. | J/token, accuracy and paired comparison: wrong token counts, prompts or output association change quantities. | N— located; X tokenizer/prompt/request/hash/count mismatches; E projection/prompt-pin migrations (`e71cf606c`, `e4f52e34f`). | Per-source import and request validation; every tokenizer/prompt/model revision. | One canonical source/request identity shared across layers. No equivalent dropping realized-token evidence. | **KEEP** — token and example identity define the denominator and task. |
| M41 | Duration-margin receipts authenticate a complete pack census and estimate timing headroom. `window_duration_margins.py`, recorder tools. | Capture support/coverage; the margin itself is planning evidence, not the published energy estimate. | N—; **E1** legitimate comparative specs made ALPHA/BETA close-out deterministically impossible; X repinned truncated census passed weak consumers [M]. | Close-out blocking repair, governed-spec exceptions and frozen-census fixtures; every window close. | Runtime slot/capture deadlines plus one plan-duration calculation. Keep complete planned membership; avoid separate post-window authorization receipt. Lose detailed predicted margin tables. | **THIN** — runtime boundaries protect capture; planning receipt machinery duplicates them. |
| M42 | Determinism and envelope gates validate comparable response hashes and affine-smoke evidence. `determinism_gate.py`, `envelope_gate.py`. | Response identity, smoke slope/envelope and comparative validity. | N— located; X malformed/noncomparable response and hand-computed smoke cases. | Per diagnostic evaluation; historical attributable repair spend not isolated. | Keep when those diagnostic quantities are used; otherwise run on demand rather than making unrelated work depend on them. | **KEEP** — protects named diagnostic numbers and comparability. |
| M43 | Publication privacy classifies every field/path and transforms immutable private bundles into verified public copies. `publication_privacy.py:1`, package/report tools. | Public J/B custody must survive transformation; privacy classification itself protects no scientific number. | N— located; E legitimate new governed fields were unclassified (`cb5978547`), provenance/identity repairs (`1902d1601`, `4aff4cb1c`). | Unknown-field refusals on schema additions; transformation and verification per optional publication. | Keep immutable originals, explicit sensitive-field redaction and public numerical equivalence. Reduce duplicated whole-schema inventories. Lose refusal on harmless newly added metadata. | **THIN** — keep privacy and numerical preservation; narrow the classification burden. |
| M44 | Paper numerical suppliers replay energy projections, uncertainty copies and worked examples from custody. `paper_reported_energy.py`, `claim_side_bound.py`, paper replay/derivation scripts. | Paper table means, ratios, deterministic bounds and worked clock values. | N— located; X exact numeral/unit/denominator mutations; E ratio/unit/placement defects repaired in `0d3af314a`, `9760ee535`, `6c34cfe6e`. | Paper supplier fix rounds and source replay; every numeric fill. Replay fence checks 43 comparisons in recorded run [G]. | Direct source-to-render projection with declared rounding, units and issuance. No equivalent dropping numeric readback. | **KEEP** — guards the actual paper quantities. |
| M45 | Claims/editorial linters enforce vocabulary, first use, rationale, branches and placements. `claims_lint.py`, `paper_terms_lint.py`, rationale/first-use/Results tests. | Claim status/labels can prevent overstatement; first-use and exact phrase placement protect no number. | N— located; E R7F/skeleton numeric coverage vacuity and stale selector test [G]; X prose mutations. | Paper-N three-round arc plus follow-up; phrase/row changes repeatedly require tests. | Keep checks for unsupported claim status, units and provenance; make style/term/placement checks advisory. Lose exact editorial-template conformance. | **THIN** — scientific labels matter; typography and mirrored prose should not block science. |
| M46 | PR ledger, generated state and freshness tests enforce workflow tables and current-document consistency. `check_gate_ledger.py`, `gen_state.py`, docs/state tests. | None/process hygiene; prevents stale work selection and absent review records. | N—; E stale moving records repeatedly failed audits; TMPDIR and table-parser defects; `test_check_gate_ledger.py` records the CI TMPDIR catch. | Every PR/session; twelve rows or light-tier four; repeated bookkeeping refresh/reaudit [G]. | Minimal change-specific verification record, final-head review and generated-state validity. Remove ceremonial rows and copied volatile facts. Lose uniform audit-ledger completeness. | **THIN** — retain useful handoff facts, cut universal paperwork. |
| M47 | Immutable line-audit tests pin source ranges and extracted bytes in a historical runsheet. `test_s0_line_audit_guard.py`. | None directly; proves the requested source excerpt was printed. | N—; **E1** same-length shifted range passed; one fix round and delta audit [P]. | Every audited coordinate change requires repinning; historical block plus dedicated shell-test fixtures. | Review the relevant function/diff at a pinned commit; one extraction-presence check. Lose exact coordinate/content excerpt identity. | **DELETE coordinate fortification** — source-reading custody is not measurement custody. |
| M48 | Bridge/agent runners enforce write scopes, report envelopes, host task/IPC ownership and one-hop rules. `scripts/bridge`, `codex-*`, `claude-bridge-mcp.mjs`. | None directly; prevents unauthorized workspace changes and failed handoffs. | N— located; E transport/report/host-task failures in restart history; not a measured-number catch. | Per delegation; multiple execution routes, runtime/version-specific checks and envelope parsing. | One supported runner with scope enforcement and one report format. Retain IPC ownership and sandbox restrictions. Lose old runner compatibility. | **THIN** — maintain bounded authority; retire parallel historical adapters. |
| M49 | Test-only shape systems police public signatures, primitive access, enums, reason partitions and source layout. Authentication/battery guards, `test_reason_code_partition.py`, scored AST tests, schema/registry tests. | Some bypass checks protect B/J custody; syntax, exact first statement and closed emission census are indirect proxies. | N— located; E scanner bypass/allowlist defects; X alias, raw-read, new-emitter and signature mutations. | Recurrent AST maintenance; every refactor/new reason/API. Costs overlap M15/M17/M21/M37. | Behavior tests at authentication/issuance boundaries plus a small API contract check. Retain schema validation; delete redundant AST/layout proofs. Lose detection of some unused syntactic bypasses. | **THIN** — observable boundary guarantees are stronger than prescribed code shape. |
| M50 | Fixture orphan census, process runners and timing/shard policies keep the test bench clean and bounded. `fixture_orphan_census.py`, `owned_process_runner.py`, quick/shard tests. | None directly; orphan load can contaminate a later measurement. | N—; orphan sentinel report stayed PROVISIONAL when ps was denied [L]; E flakes and witness cleanup repairs [G]. | Informational census per handoff; scheduling/timing-map upkeep; no refusal from orphan reporter itself. | Keep centralized owned-process cleanup and one orphan scan; timing maps advisory. Lose detailed signature-specific reporting. | **THIN** — useful cheap hygiene; avoid turning it into another gate hierarchy. |
| M51 | Generic schemas and remote adapters reject invalid domains, unavailable backends and inconsistent wire data. `schemas.py`, `validation.py`, interfaces/workloads/KV helpers, node/runtime/telemetry adapters and spikes. | J, time, token and memory quantities: unit/domain/association errors yield incorrect values or failed collection. | N— isolated; X parser/domain/unit/transport fixtures. Attributable historical cost unknown. | Input validation per operation; remote identity/time conversion and backend-specific checks. | No equivalent accepting malformed or nonfinite inputs. Keep local domain validation; avoid duplicating it at every wrapper. | **KEEP core** — basic domain/unit checks are proportional numerical protection. |
| M52 | Site/capsule/release checks enforce artifact validity, clean source, packaging and platform limits. `build_site.py`, `pack_capsule.py`, `release_check.py`, capstone/figure tools. | Reported numbers require authenticated figure inputs; stylistic/site budgets protect no number. Physical capsule cap protects deployability. | N— located; E release/schema additions and advisory-budget policy mismatch documented in queue; X isolated mock release checks. | Per release/site build; clean snapshot, mock pipeline and capsule pack. | Keep figure input authentication and actual platform cap; advisory budgets and release-only smoke. Lose early failures for stylistic budgets. | **THIN** — scientific input checks survive; presentation constraints stay local to publication. |

### Record anchors used above

- **[A]** [Readiness L9 census](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-08-15-readiness-council/seat-reports/L9-environmental-controls-census-report.md>): resident-daemon false refusal, missed active agents, physical-control census.
- **[B]** [Parity pilot ruling](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/83-coldgate-pilot-ruling.md>): two exemption forms, 19 switched sites, 42/57 repaired outcomes, charging/config controls.
- **[C]** [S1 repair returns ruling](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/31-coldgate-returns-ruling.md>) and [escalation ruling](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/50-escalation/21-coldgate-fable-ruling.md>): failure counts, fixture coupling, mock-config fail-open introduced by S1.
- **[D]** [Installer round 8 and live smoke](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-15-interactive-b0ae8462/08k-round-8-landed-and-live-smoke.md>).
- **[E]** [Network-time science ruling](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/21-ruling.md>), [N1 fix-2 cold ruling](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-27-activation-d528efb2/71-ntp-design/38-coldgate-fix2-ruling.md>), [A2 contract refuter](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-27-activation-d528efb2/71-ntp-design/48-a2-contract-refuter-opus.md>).
- **[F]** [Head-pin repair round 2](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-19-activation-d0b83820/26-brief-head-pin-fix-round-2.md>) and its [seat report](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-19-activation-d0b83820/26-head-pin-fix-round-2-astra.md>).
- **[G]** [Activation record](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-27-activation-d528efb2/00-activation-record.md>): items 124/132/136/146 sampler fence; 141 witness cache; 143/145/148 parity repair; 147 byte-pin blockage; 154–156 paper-number coverage.
- **[H]** [Decode identity terminal review](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-02-decode-identity-set/59-magistrate-terminal-review.md>): four rounds, consult, cold gate.
- **[I]** [Census review sequence](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-27-activation-3ba66eeb/50-census/11-sol-review.md>), [delta](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-27-activation-3ba66eeb/50-census/12-sol-delta.md>), [consult](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-27-activation-3ba66eeb/50-census/13-sol-consult.md>), [final](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-27-activation-3ba66eeb/50-census/14-sol-final-review.md>).
- **[J]** [Charter refuter](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-04-fanout/CHARTER-V3-PACKET-INPUTS-01/02-refuter-merge-base.md>).
- **[K]** [Git-fixture first refuter](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-04-fanout/GIT-FIXTURE-MAINTENANCE-SWEEP-01/02-refuter-merge-base.md>) and [round-1 delta](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-04-fanout/GIT-FIXTURE-MAINTENANCE-SWEEP-01/04-delta-reaudit-round-1.md>).
- **[L]** [Retry round 3](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-15-interactive-b0ae8462/03j-a172-fix-round-3-report.md>), [arm census bench round 3](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-15-interactive-b0ae8462/04l-a173-fix-round-3-bench.md>), [orphan sentinel report](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-15-interactive-b0ae8462/17-a208-fixture-sentinel-report.md>).
- **[M]** [Quantitative pipeline L4](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-08-15-readiness-council/seat-reports/L4-quantitative-claim-pipeline-report.md>): exact floor rejection and broken margin close-out.
- **[N]** [Battery parser seat round 6](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/19-fix-seat-report-r6.md>).
- **[O]** [Custody locator cold ruling](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-08-handoff-redo/99ak-coldgate-packet-locator-boundary/10-coldgate-fable-ruling.md>).
- **[P]** [Line-audit refuter](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-04-fanout/LINE-AUDIT-GUARD-01/02-refuter-merge-base.md>) and [fix report](</Users/edr/code/JouleWise-wt-prune-ff50b201/docs/process_traces/2026-09-04-fanout/LINE-AUDIT-GUARD-01/03-sol-fix-round-1-report.md>).

### Ranked THIN/DELETE: top 15

Ranking uses **estimated savings C, 1–5**, multiplied by **subjective confidence p that the named removed portion adds no numerical protection once its replacement exists**. These scores are prioritization judgments, not measured hours or statistical probabilities.

| Rank | Proposed cut | C × p | Retained control / required check |
|---:|---|---:|---|
| 1 | **M07 DELETE** restore-ON, pending marker, recovery and capture-absence proof | 5 × .99 = **4.95** | Leave OFF; preserve clock validity. **Cold Fable claim-path check.** |
| 2 | **M03 THIN** parity ID grants, second-switch registry and migration rule system | 5 × .90 = **4.50** | Layer-specific fixtures; real battery/mock/config gates and targeted acceptance/refusal tests. |
| 3 | **M01 THIN** documentary ARM rows, duplicate evidence lifecycles and review-message membership | 5 × .85 = **4.25** | Sealed experiment identity, physical state, raw custody and one-use launch. |
| 4 | **M08 DELETE** inactive quiet-lease engine and setup clients | 4 × .99 = **3.96** | Preserve shared Darwin process primitives used by active callers. |
| 5 | **M04 THIN** custom paper capability anti-forgery and overlapping read inventories | 5 × .75 = **3.75** | Authenticated issued inputs, numerical replay and fixture/production distinction. |
| 6 | **M09 THIN** whole-file pins and automatic re-derivation for irrelevant byte edits | 5 × .70 = **3.50** | Stable scientific computation/dependency identity and raw hashes. |
| 7 | **M10 DELETE** verified logical-deletion protocol | 4 × .85 = **3.40** | Preserve old namespace; use a fresh one. **Cold Fable custody-path check.** |
| 8 | **M33 DELETE** unused staged scheduler façade | 3 × .99 = **2.97** | Actual launch-route checks. **Cold Fable claim-path check.** |
| 9 | **M17 THIN** single-count reader AST/count/text census | 3 × .90 = **2.70** | Direct floor-plus-uncertainty composition tests and canonical metadata validation. |
| 10 | **M14 THIN** historical current-coordinate/source correspondence layers | 4 × .65 = **2.60** | Frozen version dispatch and numerical replay of historical artifacts. |
| 11 | **M15 THIN** refusal-witness provenance analyzer and per-witness execution bookkeeping | 3 × .85 = **2.55** | End-to-end consequential exit/custody tests and complete enum mapping. |
| 12 | **M19 DELETE** duplicate paper proposal/placement/retirement mirrors | 3 × .80 = **2.40** | Adopted source map, labels and numeric readback. **Cold Fable claim-path check.** |
| 13 | **M20 THIN** charter delivery and receipt durability layers | 2 × .98 = **1.96** | Exact frozen packet hash and exclusive atomic receipt. |
| 14 | **M21 THIN** Git-command AST interpreter and exemption machinery | 2 × .95 = **1.90** | Shared safe fixture initializer and small lint. |
| 15 | **M18 THIN** live decoy combinations and unrelated host-process assertions | 2 × .85 = **1.70** | Realistic snapshots plus a bounded native OS-seam smoke. |

### KEEP list: the number each protects

These include the numerical cores retained inside THIN mechanisms.

| Keep | Quantity protected |
|---|---|
| Clock anchors, frame interval support, causal timing-bound composition and tail support | Gross/net/phase energy in J; calibration B |
| Fiducial raw replay, acceptance S/C derivation, physical epoch and pre/post transfer bracket | Calibration S, C and operative timing allowance |
| Immutable raw evidence, artifact digests, complete attempt ledger and issuing/replay separation | Every reconstructed J, B, floor and paper quantity |
| Registered sample/order/cardinality, complete window membership and governed supersession | Floor and treatment-effect estimates without outcome selection |
| Exact floor estimator dispatch, required attribution terms and mint recomputation | Published false-effect floor in J |
| Paired estimator, CI/bound composition, both-gates decision and multiplicity | Effect size, interval and supported/equivalent conclusion |
| Actual model/prompt/tokenizer/request/output identity | J/request, J/token, accuracy and comparison identity |
| Score-roster conservation, retry custody and window attribution | Accuracy denominator and headline J/correct |
| Environment, battery, thermal, CPU admission and sampler teardown | Unconfounded energy and calibration observations |
| One-use launch, approved pack identity and persisted launch lineage | Dataset custody and intended sample population |
| Agent/capture exclusion and **centralized test sampler fence** | Quiet-window energy; prevention of actual test-triggered hardware capture |
| Paper numerical supplier replay, units, declared rounding and numeric readback | Paper means, ratios, uncertainty terms and worked-example values |
| Public-copy numerical equivalence with immutable private originals | Published bundle/report numbers after redaction |
| Basic finite/domain/unit/schema and remote clock conversion checks | Energy, duration, token, memory and transport-associated values |

## Residual risk

This is an exhaustive lexical census with grouped static assessments, not a proof that every dynamic refusal path was exercised. Historical catches and costs come from targeted record reads and Git history; an absent catch entry is not evidence that a mechanism never helped.

The parity helper and sampler fence are branch mechanisms, absent from `32ff9013`. NTP was assessed at the requested `c895f28b` object; the local remote-tracking ref still points to `36e8ba6e`.

No files changed. No tests, live probes or measurements ran. The next exact step is a cold Fable check of **M07’s restoration-only deletion**, with the retained OFF/clock-validity path explicitly identified.