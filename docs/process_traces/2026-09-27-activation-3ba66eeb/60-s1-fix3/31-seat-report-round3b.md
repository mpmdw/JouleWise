```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "All eleven ordered test-only steps are implemented and V1, V2, and both builder checks are green; R72-2 needs a ruling on its stated counterfactual.",
  "workspace": {
    "base_requested": "8953c7a5",
    "base_mode": "exact",
    "head_start": "8953c7a5e1df7de0734933639739852af0213a37",
    "head_end": "8953c7a5e1df7de0734933639739852af0213a37",
    "upstream_end": "8953c7a5e1df7de0734933639739852af0213a37",
    "branch": "feat/2026-09-26-bfgs-s1-bundles"
  },
  "pathspec": ["tests/test_bfgs_consumer_sweep.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_controller tests.test_bundle_read tests.test_reduce tests.test_revision_five_b_readers tests.test_scored_reduce tests.test_bfgs_calibration_bracketing tests.test_bfgs_window_consumers tests.test_bfgs_consumer_sweep tests.test_bfgs_publication_privacy tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".............................................................................................................................................................................................................................................................................................................................",
          "----------------------------------------------------------------------",
          "Ran 477 tests in 2992.293s",
          "",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 477 tests in .*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_evidence_night tests.test_night_kinds tests.test_envelope_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".......................................................................................................................................................................................................................................................................................................................................................",
          "----------------------------------------------------------------------",
          "Ran 343 tests in 489.464s",
          "",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 343 tests in .*\\n\\nOK"}
    },
    {
      "id": "B1",
      "kind": "build",
      "cmd": "python3 scripts/build_battery_float_historical_bundles.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "listed_population sw7bfloor-df-ph-decode-abs-r07 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "listed_population sw7bfloor-df-ph-decode-abs-r08 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "listed_population sw7bfloor-df-ph-decode-abs-r09 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "listed_population sw7bfloor-df-ph-decode-abs-r10 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "forward check: byte-identical entries=69"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "forward check: byte-identical entries=69"}
    },
    {
      "id": "B2",
      "kind": "build",
      "cmd": "python3 scripts/build_battery_float_historical_bundles.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "listed_population sw7bfloor-df-ph-decode-abs-r07 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "listed_population sw7bfloor-df-ph-decode-abs-r08 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "listed_population sw7bfloor-df-ph-decode-abs-r09 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "listed_population sw7bfloor-df-ph-decode-abs-r10 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "forward check: byte-identical entries=69"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "forward check: byte-identical entries=69"}
    }
  ],
  "flags": [
    {
      "id": "R72-2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Removing only the _MEASURAND_FIELDS test does not license gross_energy_j: the independent unknown-nonnull-field check still refuses it. The row goes RED on its exact refusal message, but its stated counterfactual outcome cannot occur.",
      "needs": "Rule whether refusal-message RED satisfies R72-2, or amend the counterfactual to remove both guards."
    }
  ]
}
```

## Change

Completed orders **1–11** in [tests/test_bfgs_consumer_sweep.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_bfgs_consumer_sweep.py). No production file was edited.

| Order | Step | Amendment | Rows | RED evidence under counterfactual | GREEN evidence |
|---:|---:|---|---|---|---|
| 1 | 20 | 72 | R72-1–3 | A power-derived license field changes when `power_w` changes; removing `_MEASURAND_FIELDS` changes the exact refusal; a reason lacking `test:` fails. **R72-2’s claimed license outcome needs the ruling below.** | Salvage licenses remain equal after `power_w × 1000 + 7`; `gross_energy_j: 12.5` is refused; **117** core allowlist keys match. |
| 2 | 21 | 73 | R73-1 | In-memory `-> list[float]` annotation is rejected. | All four `validation` members have the ruled return shapes. |
| 3 | 22 | 74 | R74-1–4 | Removing or weakening the controller capture refusal, naming a raw capture before it, removing the adjacent calibration exclusion, adding an outside caller, removing the window gate, or changing the validator return shape fails. With battery exclusion patched away, both R74-4 calibration tests failed. | The three capture-gate declarations pass; both existing R74-4 tests pass in V1. |
| 4 | 23 | 75 | R75-1–2; R58-7–8 | A sixth lane member, an in-memory change to a pinned lane file, and either new literal or named raw-capture reader are detected. | The four lane files match main; raw-capture keys equal the **48**-member inventory. |
| 5 | 13 | 68(a–d) | R61-1–2 | `tools/zz_new.py` fails the closed-root check; a new paper function reading `gross_energy_j` is reported. | The four swept roots pass; the five closed lists remain scoped to `joulewise/` and `scripts/`. |
| 6 | 14 | 68(e) | R51-27 | Omitting either paper key makes inventory equality fail. | Exactly the two granted paper rows appear: **119** keys, 125 sites, 88 scopes, 125 source lines. |
| 7 | 15 | 66(c–d), 67, 76 | R51-17b–e, R76-1; R51-17 | New producer call/reference, omitted `evaluate_members`, missing `collection_uses`, old exclusive reason, and removed or weakened campaign gates fail. | All three campaign rows have `consumers`, `collection_uses`, `producers`, and amendment 76’s reason. |
| 8 | 16 | 69 | R51-23b–c | In-memory lambda-gate and nested-scope omission mutants hide their reads and go RED. | Both reads are reported despite the outer gate. |
| 9 | 17 | 71 | R51-28(e); R60-7 | A nested `nonlocal policy_binding` reset breaks the consumers dominance check. | The unmodified check passes; commit `315364b2` is present, so R60-7 executed rather than skipped. |
| 10 | 18 | 68, 70, 72, 75 | Text | Text review: the amended promise, deliberate class, stop rule, `non_claim` clause, lane limitation, and 58(f)6 wording are present. | The sweep imports and V1 passes. |
| 11 | 19 | — | V1, V2, builder, A5 | No failure counterfactual assigned. | V1 477/477; V2 343/343; both builder checks report `byte-identical entries=69`; A5 fences pass. |

**Counts:** core read sites 123, core allowlist keys 117; expanded read sites 125, expanded allowlist keys 119. The only added expanded-root keys are the two `docs/paper/figures/reproduce_worked_examples.py` rows below. Allowlist classes: 61 `non_claim`, 44 `strict_validation`, eight `behind_gate`, three `gate_body`, two `tolerant_definition`, one `historical`. Raw-capture kinds: 15 `custody`, 15 `names`, 12 `energy`, four `validation`, two `timing`. `custody` is a raw-capture kind here, never a battery verdict status.

### Allowlist: class and reason for every row

| # | Key | Class | Reason |
|---:|---|---|---|
| 1 | `docs/paper/figures/reproduce_worked_examples.py::historical · direct:read_bytes · power_trace.csv` | `non_claim` | clause (i), fields read: interval_start_s, interval_end_s; bytes are hashed against `docs/process_traces/2026-08-09-prefill-phase-proof/results.json` |
| 2 | `docs/paper/figures/reproduce_worked_examples.py::synthetic · direct:read_bytes · power_trace.csv` | `non_claim` | clause (i), fields read: none; bytes are hashed into `fixture_fingerprints` |
| 3 | `joulewise/analysis_engine/registry.py::validate_attempt_ledger · direct:read_authentication_input · metadata.json` | `non_claim` | clause (i), run ID, launch and target-model identities |
| 4 | `joulewise/analysis_engine/registry.py::validate_manifest_target_evidence · direct:read_authentication_input · metadata.json` | `non_claim` | clause (i), target-model artifact digest |
| 5 | `joulewise/analysis_manifest_v3.py::_derive_arms_and_entries · direct:_read_manifest_input · metadata.json` | `non_claim` | clause (i), model, tokenizer, adapter, device and quantization identities |
| 6 | `joulewise/analysis_manifest_v3.py::_floor_consumer_contexts · direct:_read_manifest_input · metadata.json` | `non_claim` | clause (i), machine, platform, adapter, model, tokenizer, sampler and output-policy identities |
| 7 | `joulewise/arm_readiness.py::authenticate_bundle_launch_lineage · direct:read_bytes · metadata.json` | `non_claim` | clause (i), launch-lineage identity and completion fields |
| 8 | `joulewise/battery_float.py::authenticate_bundle · direct:_required_object · metadata.json` | `gate_body` | one of the three closed gate bodies |
| 9 | `joulewise/bundle.py::RunBundleWriter.write_power_trace · direct:open · power_trace.csv` | `non_claim` | clause (i), write-only open of a new trace |
| 10 | `joulewise/bundle_read.py::BundleReader.events · direct:_strict_json · metadata.json` | `non_claim` | clause (i), battery-float presence when events are missing |
| 11 | `joulewise/bundle_read.py::BundleReader.is_complete · raw_summary · -` | `strict_validation` | summary presence and status; boolean |
| 12 | `joulewise/bundle_read.py::BundleReader.is_event_v2 · raw_metadata · -` | `strict_validation` | event semantics identity; boolean |
| 13 | `joulewise/bundle_read.py::BundleReader.is_frozen_legacy_identity · raw_metadata · -` | `strict_validation` | frozen legacy identity; boolean |
| 14 | `joulewise/bundle_read.py::BundleReader.metadata · direct:_strict_json · metadata.json` | `gate_body` | one of the three closed gate bodies |
| 15 | `joulewise/bundle_read.py::BundleReader.problems · direct:read_authentication_text · metadata.json` | `strict_validation` | bundle structure; problem strings |
| 16 | `joulewise/bundle_read.py::BundleReader.rail_manifest · raw_metadata · -` | `non_claim` | clause (i), rail identity and labels |
| 17 | `joulewise/bundle_read.py::BundleReader.raw_metadata · direct:_tolerant_json · metadata.json` | `tolerant_definition` | forwards metadata without a gate; callers inventoried |
| 18 | `joulewise/bundle_read.py::BundleReader.raw_summary · direct:_tolerant_json · summary_metrics.json` | `tolerant_definition` | forwards summary without a gate; callers inventoried |
| 19 | `joulewise/bundle_read.py::_check_power_trace · direct:open_authentication_input · power_trace.csv` | `strict_validation` | trace structure; problem strings |
| 20 | `joulewise/bundle_read.py::authenticate_window_members · direct:_strict_json · metadata.json` | `gate_body` | one of the three closed gate bodies |
| 21 | `joulewise/bundle_read.py::axi_v2_validation_problems · raw_config · -` | `strict_validation` | event-v2 and AXI validity; problem strings |
| 22 | `joulewise/bundle_read.py::axi_v2_validation_problems · raw_metadata · -` | `strict_validation` | event-v2 and AXI validity; problem strings |
| 23 | `joulewise/bundle_read.py::axi_v2_validation_problems · raw_summary · -` | `strict_validation` | event-v2 and AXI validity; problem strings |
| 24 | `joulewise/calibration_ledger.py::_artifact_hashes_unbounded · direct:hash_core · power_trace.csv` | `non_claim` | clause (i), opaque bytes and digests |
| 25 | `joulewise/calibration_ledger.py::_custody_state_unbounded · direct:custody_state · power_trace.csv` | `non_claim` | clause (i), opaque custody state and digests |
| 26 | `joulewise/calibration_ledger.py::_governed_raw_nofollow_unbounded · direct:_read_contained_nofollow_unbounded · power_trace.csv` | `non_claim` | clause (i), opaque artifact bytes for custody verification |
| 27 | `joulewise/cli.py::_cmd_reduce · direct:read_authentication_text · summary_metrics.json` | `non_claim` | clause (ii), reduced JSON to stdout; CLI exit code to `main`; no tracked claim consumer of stdout |
| 28 | `joulewise/cli.py::_strict_emitted_token_ids_problems · raw_metadata · -` | `strict_validation` | strict bundle validity; problem strings |
| 29 | `joulewise/cli.py::_strict_problems · raw_config · -` | `strict_validation` | strict bundle validity; problem strings |
| 30 | `joulewise/cli.py::_strict_problems · raw_metadata · -` | `strict_validation` | strict bundle validity; problem strings |
| 31 | `joulewise/cli.py::_strict_problems · raw_summary · -` | `strict_validation` | strict bundle validity; problem strings |
| 32 | `joulewise/cli.py::_strict_realized_output_problems · raw_config · -` | `strict_validation` | strict bundle validity; problem strings |
| 33 | `joulewise/cli.py::_strict_realized_output_problems · raw_metadata · -` | `strict_validation` | strict bundle validity; problem strings |
| 34 | `joulewise/cli.py::_strict_reducer_version_dispatch · raw_metadata · -` | `strict_validation` | strict bundle validity; problem strings |
| 35 | `joulewise/cli.py::_strict_rich_telemetry_problems · raw_metadata · -` | `strict_validation` | strict bundle validity; problem strings |
| 36 | `joulewise/cli.py::_strict_uncertainty_evidence_problems · raw_metadata · -` | `strict_validation` | strict bundle validity; problem strings |
| 37 | `joulewise/cli.py::_strict_workload_provenance_problems · raw_metadata · -` | `strict_validation` | strict bundle validity; problem strings |
| 38 | `joulewise/cli.py::_verify_nvidia_smi_raw_to_trace · raw_metadata · -` | `strict_validation` | strict bundle validity; problem strings |
| 39 | `joulewise/cli.py::_verify_powermetrics_raw_to_trace · raw_metadata · -` | `strict_validation` | strict bundle validity; problem strings |
| 40 | `joulewise/controller.py::_experiment_cooldown_anchor · direct:read_text · metadata.json` | `non_claim` | clause (i), environment snapshot digest |
| 41 | `joulewise/controller.py::_experiment_cooldown_reference_eligibility · direct:read_text · metadata.json` | `non_claim` | clause (i), admission, reference-provenance and policy identity fields |
| 42 | `joulewise/controller.py::_member_gap_note · direct:read_text · metadata.json` | `non_claim` | clause (i), preceding gap duration |
| 43 | `joulewise/determinism_gate.py::_check_gate_json_evidence_for_duplicate_keys · direct:_load_json_without_duplicate_keys · metadata.json` | `strict_validation` | duplicate-key validation; problem strings |
| 44 | `joulewise/determinism_gate.py::_check_gate_json_evidence_for_duplicate_keys · direct:_load_jsonl_without_duplicate_keys · metadata.json` | `strict_validation` | duplicate-key validation; problem strings |
| 45 | `joulewise/determinism_gate.py::_inspect_strict_valid_bundle · raw_config · -` | `strict_validation` | duplicate-key validation; problem strings |
| 46 | `joulewise/envelope_gate.py::_bundle_hashes · direct:encode · metadata.json` | `non_claim` | clause (i), opaque artifact hash |
| 47 | `joulewise/envelope_gate.py::_bundle_hashes · direct:read_bytes · metadata.json` | `non_claim` | clause (i), opaque artifact hash |
| 48 | `joulewise/floor_extraction.py::_cpu_admission_bundle_reasons · direct:_strict_admission_json_file · metadata.json` | `behind_gate` | listed gated caller chain |
| 49 | `joulewise/floor_extraction.py::_evaluate_member · direct:_strict_admission_json_file · metadata.json` | `behind_gate` | listed gated caller chain |
| 50 | `joulewise/floor_extraction.py::_read_summary · direct:_strict_admission_json_value · summary_metrics.json` | `behind_gate` | listed gated caller chain |
| 51 | `joulewise/floor_extraction.py::_read_summary · direct:read_authentication_input · summary_metrics.json` | `behind_gate` | listed gated caller chain |
| 52 | `joulewise/idle_dependence.py::derive_idle_mean_uncertainty · raw_artifact_bytes · -` | `behind_gate` | listed gated caller chain |
| 53 | `joulewise/output_identity.py::_bundle_reference · direct:_hash_file · summary_metrics.json` | `non_claim` | clause (i), opaque summary hash |
| 54 | `joulewise/output_identity.py::_bundle_reference · direct:_json_object · metadata.json` | `non_claim` | clause (i), run and tokenizer identities |
| 55 | `joulewise/output_identity.py::_bundle_reference · direct:_json_object · summary_metrics.json` | `non_claim` | clause (i), object presence and opaque hash |
| 56 | `joulewise/publication_privacy.py::_audit_metadata · direct:_load_json_object · metadata.json` | `strict_validation` | public-bundle privacy schema; problem strings or `None` |
| 57 | `joulewise/publication_privacy.py::_audit_metadata · direct:_unknown_keys · metadata.json` | `strict_validation` | public-bundle privacy schema; problem strings or `None` |
| 58 | `joulewise/publication_privacy.py::_audit_summary · direct:_load_json_object · summary_metrics.json` | `strict_validation` | public-bundle privacy schema; problem strings or `None` |
| 59 | `joulewise/publication_privacy.py::_audit_summary · direct:_unknown_keys · summary_metrics.json` | `strict_validation` | public-bundle privacy schema; problem strings or `None` |
| 60 | `joulewise/publication_privacy.py::verify_public_bundle · direct:_load_json_object · metadata.json` | `strict_validation` | public-bundle privacy schema; problem strings or `None` |
| 61 | `joulewise/publication_privacy.py::verify_public_bundle · direct:_load_json_object · summary_metrics.json` | `strict_validation` | public-bundle privacy schema; problem strings or `None` |
| 62 | `joulewise/reduce.py::_resolve_reducer_version · raw_config · -` | `strict_validation` | reducer-version identity |
| 63 | `joulewise/reduce.py::_resolve_reducer_version · raw_summary · -` | `strict_validation` | reducer-version identity |
| 64 | `joulewise/reduce.py::_verify_instrument_calibration · raw_config · -` | `non_claim` | clause (i), sampling cadence used for sampling interval |
| 65 | `joulewise/report.py::_discover_bundles · raw_config · -` | `non_claim` | clause (ii), static browser records and charts; no tracked paper-claim consumer |
| 66 | `joulewise/report.py::_discover_bundles · raw_metadata · -` | `non_claim` | clause (ii), static browser records and charts; no tracked paper-claim consumer |
| 67 | `joulewise/report.py::_discover_bundles · raw_summary · -` | `non_claim` | clause (ii), static browser records and charts; no tracked paper-claim consumer |
| 68 | `joulewise/salvage_dangler.py::_inspect_preworkload_abort · direct:_read_json_object · metadata.json` | `non_claim` | clause (i), run and admission identities |
| 69 | `joulewise/salvage_dangler.py::_inspect_preworkload_abort · direct:_read_json_object · summary_metrics.json` | `non_claim` | clause (i), `failure_reason` leaves; `status`, all 17 `_MEASURAND_FIELDS` and other keys are tested and dropped for failed status, null measurands and allowed non-null keys |
| 70 | `joulewise/salvage_dangler.py::_telemetry_timestamp_bounds · direct:open_authentication_input · power_trace.csv` | `non_claim` | clause (i), timestamp and interval bounds leave; `power_w`, `source`, `rail` are tested and dropped for finite power and absence of workload markers |
| 71 | `joulewise/salvage_dangler.py::inspect_salvage_attempt · direct:_read_json_object · metadata.json` | `non_claim` | clause (i), run ID for bundle identity |
| 72 | `joulewise/whole_window.py::_authenticated_bundle_launch_lineage_set · direct:_read_json_object · metadata.json` | `strict_validation` | launch-lineage identity; returns shared identity |
| 73 | `joulewise/whole_window.py::_consumption_provenance_valid · direct:_read_json_object · summary_metrics.json` | `strict_validation` | provenance and strict validity; identity, boolean, digest or problems |
| 74 | `joulewise/whole_window.py::_current_core_rederivation_reasons · direct:_read_json_object · metadata.json` | `strict_validation` | provenance and strict validity; identity, boolean, digest or problems |
| 75 | `joulewise/whole_window.py::_current_core_rederivation_reasons · direct:_read_json_object · summary_metrics.json` | `strict_validation` | provenance and strict validity; identity, boolean, digest or problems |
| 76 | `joulewise/whole_window.py::_manifest_bundle_paths · direct:_read_json_object · summary_metrics.json` | `strict_validation` | bundle identities; path identity map |
| 77 | `joulewise/whole_window.py::_manifest_members · direct:_read_json_object · summary_metrics.json` | `strict_validation` | bundle identities; identity set |
| 78 | `joulewise/whole_window.py::_row_references_current_strict_member · direct:_read_json_object · summary_metrics.json` | `strict_validation` | provenance and strict validity; identity, boolean, digest or problems |
| 79 | `joulewise/whole_window.py::_scientific_config_identity · direct:_read_json_object · metadata.json` | `strict_validation` | config digest and canonicality |
| 80 | `joulewise/whole_window.py::_validate_row_uncached · direct:_read_json_object · summary_metrics.json` | `strict_validation` | provenance and strict validity; identity, boolean, digest or problems |
| 81 | `joulewise/whole_window.py::_validated_evaluation_basis · direct:read_authentication_input · metadata.json` | `non_claim` | clause (i), opaque metadata hash against bound digest |
| 82 | `joulewise/whole_window.py::custody_telemetry_identity · direct:_read_json_object · metadata.json` | `strict_validation` | telemetry source identity; class identity and agreement booleans |
| 83 | `joulewise/whole_window.py::custody_telemetry_identity · direct:_read_json_object · summary_metrics.json` | `strict_validation` | telemetry source identity; class identity and agreement booleans |
| 84 | `joulewise/whole_window.py::validate_occurrence_supersession_entry · direct:read_authentication_input · metadata.json` | `strict_validation` | provenance and strict validity; identity, boolean, digest or problems |
| 85 | `joulewise/whole_window.py::whole_window_refusal_reasons · direct:_read_json_object · summary_metrics.json` | `strict_validation` | provenance and strict validity; problem strings |
| 86 | `scripts/analyze_phase_share.py::analyze_bundle · direct:_sha256 · power_trace.csv` | `non_claim` | clause (ii), diagnostic sensitivity JSON to `main`; no governed claim artifact |
| 87 | `scripts/analyze_phase_share.py::analyze_bundle · raw_summary · -` | `non_claim` | clause (ii), diagnostic sensitivity JSON to `main`; no governed claim artifact |
| 88 | `scripts/build_battery_float_historical_bundles.py::witness · direct:_strict_json · metadata.json` | `non_claim` | clause (i), run ID; compares bundle names and digests |
| 89 | `scripts/check_window_provenance.py::_run_assertions.check_a3 · direct:_read_object · summary_metrics.json` | `non_claim` | clause (ii), assertion to stdout and exit code to `main`; no tracked claim writer |
| 90 | `scripts/corpus_compat_receipt.py::evaluate_bundle · raw_config · -` | `non_claim` | clause (i), config carried but ignored by token provenance |
| 91 | `scripts/corpus_compat_receipt.py::evaluate_bundle · raw_metadata · -` | `non_claim` | clause (i), run, token-policy, tokenizer and suite identities |
| 92 | `scripts/corpus_compat_receipt.py::evaluate_bundle · raw_summary · -` | `non_claim` | clause (i), token-count source |
| 93 | `scripts/issue_dg071_dg075_statistics.py::main · direct:issue_artifacts · power_trace.csv` | `historical` | amendment 41 pins the pre-directive trace by committed SHA-256 |
| 94 | `scripts/make_figures.py::extract_rows · raw_config · -` | `non_claim` | clause (ii), placeholder figures; no tracked production caller |
| 95 | `scripts/make_figures.py::extract_rows · raw_metadata · -` | `non_claim` | clause (ii), placeholder figures; no tracked production caller |
| 96 | `scripts/make_figures.py::extract_rows · raw_summary · -` | `non_claim` | clause (ii), placeholder figures; no tracked production caller |
| 97 | `scripts/make_figures.py::gate_inputs · raw_summary · -` | `non_claim` | clause (i), summary status |
| 98 | `scripts/make_figures.py::realized_output_tokens · raw_metadata · -` | `non_claim` | clause (i), observed output-token counts |
| 99 | `scripts/package_bundle_pack.py::_bundle_id · direct:_load_json_file · metadata.json` | `non_claim` | clause (i), run ID |
| 100 | `scripts/package_bundle_pack.py::_preflight_bundle · raw_metadata · -` | `non_claim` | clause (i), source-provenance identity and eligibility |
| 101 | `scripts/package_bundle_pack.py::_summary_status · direct:_load_json_file · summary_metrics.json` | `non_claim` | clause (i), summary status |
| 102 | `scripts/paper_prefill_resolvability_projection.py::scan_corpora · direct:read_model · metadata.json` | `non_claim` | clause (i), model and prefill labels, trace support times and opaque digest |
| 103 | `scripts/paper_prefill_resolvability_projection.py::scan_corpora · direct:read_support_intervals · power_trace.csv` | `non_claim` | clause (i), model and prefill labels, trace support times and opaque digest |
| 104 | `scripts/paper_prefill_resolvability_projection.py::scan_corpora · direct:recorded_label · summary_metrics.json` | `non_claim` | clause (i), model and prefill labels, trace support times and opaque digest |
| 105 | `scripts/paper_prefill_resolvability_projection.py::scan_corpora · direct:sha256_of · power_trace.csv` | `non_claim` | clause (i), model and prefill labels, trace support times and opaque digest |
| 106 | `scripts/run_campaign.py::_axi_discover_finalized_bundles · direct:read_bytes · metadata.json` | `non_claim` | clause (i), run and attempt identities |
| 107 | `scripts/run_campaign.py::_basis_member_occurrences · direct:read_bytes · metadata.json` | `non_claim` | clause (i), run identity and launch lineage |
| 108 | `scripts/run_campaign.py::_run_record_supersession_locked · direct:read_bytes · metadata.json` | `non_claim` | clause (i), run identity |
| 109 | `scripts/run_campaign.py::authenticate_campaign_child_launch_lineage · direct:read_bytes · metadata.json` | `non_claim` | clause (i), launch lineage and completion identity |
| 110 | `scripts/run_campaign.py::evaluate_member · direct:read_text · metadata.json` | `behind_gate` | consumers form: verdict uses gated; collection uses listed; cooldown anchor crosses campaigns in BFGS-COOLDOWN-ANCHOR-01 |
| 111 | `scripts/run_campaign.py::evaluate_member · direct:read_text · summary_metrics.json` | `behind_gate` | consumers form: verdict uses gated; collection uses listed; cooldown anchor crosses campaigns in BFGS-COOLDOWN-ANCHOR-01 |
| 112 | `scripts/run_campaign.py::evaluate_member · direct:summary_status · summary_metrics.json` | `behind_gate` | consumers form: verdict uses gated; collection uses listed; cooldown anchor crosses campaigns in BFGS-COOLDOWN-ANCHOR-01 |
| 113 | `scripts/run_campaign.py::existing_state · direct:summary_status · summary_metrics.json` | `non_claim` | clause (i), summary status |
| 114 | `scripts/run_campaign.py::run_axi_spec_campaign · direct:read_bytes · metadata.json` | `non_claim` | clause (i), admitted request count for dispatch receipt |
| 115 | `scripts/run_campaign.py::suite_order_evidence · direct:_load_json_object · metadata.json` | `non_claim` | clause (i), suite order, run identity and seed |
| 116 | `scripts/summarize_g2a_prefill_probe.py::summarize · direct:_load_json · metadata.json` | `non_claim` | clause (i), run ID and prompt-token count/digest |
| 117 | `scripts/summarize_g2a_prefill_probe.py::summarize · direct:_load_json · summary_metrics.json` | `non_claim` | clause (i), prefill in-window sample count |
| 118 | `scripts/validate_powermetrics_fiducial.py::main · direct:_write_text_artifact · power_trace.csv` | `non_claim` | clause (i), writes a new trace |
| 119 | `scripts/validate_powermetrics_fiducial.py::main · direct:sha256_path · power_trace.csv` | `non_claim` | clause (i), opaque trace hash |

## Verification notes

- A5 fences pass: `joulewise/battery_float.py` SHA-256 is `4b4d7bb206250cc0078d2a6b0b34d4e7e6305ff1d3a8b72f93528016d935e7e5`; it, `joulewise/reduce.py`, and `joulewise/bundle.py` are byte-identical to `1417c0c4`. The FT §E protected-path pin test passes.
- The eight named consumers have zero `battery_float` imports. `git diff --check` passes. No commit, push, full suite, production edit, or quiet-window measurement occurred.
- Both V1 and V2 used `/opt/homebrew/bin/python3`. Their exact last five lines, and those of both builder checks, are in the envelope.

## Residual risk

**NEEDS_RULING — R72-2 only.** An executed fixture probe gave:

```text
tree failed attempt contains measurand bytes
without_MEASURAND_test unknown non-null failed-summary fields: gross_energy_j
```

The test is RED on the required specific refusal when `_MEASURAND_FIELDS` is disabled, and GREEN on the tree. The ruling’s stronger statement that removing that test *returns a license* is contradicted by the second guard. Recommend accepting refusal-message RED, or amending the counterfactual to remove both guards. No scope expansion is requested; there are no other returned members.