```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Amendment 63(a) and the narrowed sweep are implemented; inventory and campaign provenance findings need lead rulings.",
  "workspace": {
    "base_requested": "315364b2",
    "base_mode": "exact",
    "head_start": "315364b2087ce413cc6c36347970838398796157",
    "head_end": "315364b2087ce413cc6c36347970838398796157",
    "upstream_end": "315364b2087ce413cc6c36347970838398796157",
    "branch": "feat/2026-09-26-bfgs-s1-bundles"
  },
  "pathspec": [
    "joulewise/envelope_gate.py",
    "tests/test_bfgs_consumer_sweep.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_controller tests.test_bundle_read tests.test_reduce tests.test_revision_five_b_readers tests.test_scored_reduce tests.test_bfgs_calibration_bracketing tests.test_bfgs_window_consumers tests.test_bfgs_consumer_sweep tests.test_bfgs_publication_privacy tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "",
          "----------------------------------------------------------------------",
          "Ran 470 tests in 2304.162s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)Ran 470 tests .*OK"
      }
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
          "Ran 343 tests in 983.159s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)Ran 343 tests .*OK"
      }
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
      "expected": {
        "exit_code": 0,
        "tail_regex": "forward check: byte-identical entries=69"
      }
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
      "expected": {
        "exit_code": 0,
        "tail_regex": "forward check: byte-identical entries=69"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Two salvage watched reads fit no ruled allowlist class.",
      "needs": "Rule a class or a gated production change; keep A2 red until then."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Eleven raw-capture members parse energy without a qualifying gate; one thermal-pressure member fits no ruled kind.",
      "needs": "Adjudicate BFGS-RAWCAPTURE-01 and the thermal-pressure kind; keep A3 red."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "An executed campaign path reuses a refused bundle's idle_baseline through frozen cooldown provenance; this conflicts with amendment 64(b) for three evaluate_member rows.",
      "needs": "Rule the consumers-form class and the production path."
    },
    {
      "id": "F4",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The detector counts 125 sites/119 rows before and 123 sites/117 rows after amendment 63(a), one fewer site and row than the prototype. The differing row is a nested check_a3 read attributed only to its own scope.",
      "needs": ""
    },
    {
      "id": "F5",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Final V1 has exactly two inventory assertion failures among 470 tests; V2 and both builder checks pass.",
      "needs": "Resolve F1 and F2 before rerunning V1; resolve F3 before acceptance."
    }
  ]
}
```

## Change

[envelope_gate.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/envelope_gate.py:228) has exactly amendment 63(a)’s helper and two call-site substitutions. [test_bfgs_consumer_sweep.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_bfgs_consumer_sweep.py:1) contains the narrowed promise, detector, closed inventories, allowlist, and counterfactual tests. The deliberate-evasion class remains a limitation. Neither cold-gated refuter test-row addition was added.

| Step | Amendment; files/functions | Rows | RED counterfactual evidence | GREEN/current evidence |
|---:|---|---|---|---|
| 1 | 63(a); `envelope_gate._gated_summary`, two callers | R60-3/4/7 | Removing both gates released five energy records from the refused fixture; widening the handler swallowed a custody exception. | Refused output has no energy records; custody raises; pre-edit and edited ordinary outputs equal; `tests.test_envelope_gate` 27/27. |
| 2 | 51(a–e), 57(d)5, 59(a), 62(a), 64(a); sweep scope, path, reference, and dominance functions | R51-1–13, 18–26; R59-1/2/4/5; R57-10 | Synthetic path, shadowing, exception, branch, lambda, module, class-body, and `ref:` counterfactuals are reported. | Ruled gated forms are suppressed; 209 tracked files and 6,594 execution scopes are visited. |
| 3 | 51-27; `run`, `sweep_source` | R51-27 | Counting a path assignment as a read would add a false row. | Before step 1: 125 sites, 119 rows, 88 scopes with sites, 125 source lines. After: 123 sites, 117 rows, 86 scopes with sites, 123 lines; zero rows added by scope coverage and zero `ref:` rows. The prototype’s extra row is `scripts/check_window_provenance.py::_run_assertions`, `direct:_read_object`, `summary_metrics.json`: that read belongs to nested `_run_assertions.check_a3` alone. Equality with the allowlist remains RED for the two salvage returns below. |
| 4 | 57(b,d), 65(b,c); gate, cache, tolerant-definition checks | R57-1–12, including 6b | Fourth gate, pre-verdict cache, content escape, external cache writer, bad binding, changed status, and subclass counterfactuals are detected or reproduce the ruled hole. | Exactly three gate bodies and two tolerant definitions; their current structural checks pass. |
| 5 | 58(b,c,e); reader and journal inventories | R58-1–6b/9 | Removing an accessor gate, adding a public method, or adding a journal energy reader changes the relevant closed inventory. | Thirty public reader methods and four journal energy readers match the tree; tolerant and gated behavior checks pass. |
| 6 | 58(f), 65(a); raw-capture screen | R58-7/8 | New literal and named-constant capture readers are detected and fail inventory equality. | The screen finds the predicted 48 members. Thirty-six have ruled entries; 12 are returned below, so the tree assertion remains RED. |
| 7 | 59(b,c), 62(b); caller and reference checks | R59-3/3b, R51-16, R60-2/2b | Added direct calls, plain references, and `map(extract_rows, …)` are named as unlisted callers. | Existing caller chains match their declared tuples. |
| 8 | 64(b,c); `run_campaign` consumers and dispatch receipt | R51-17/28 | Removing either campaign gate, rebinding `policy_binding`, widening its test, or moving the gate to the other branch fails the consumers check. | The current syntactic check passes and `run_axi_spec_campaign` reads only `batch.admitted_request_count` for the receipt. Executed cooldown provenance contradicts the three semantic consumers-form reasons, returned below. |
| 9 | 51(g), 58(d), 60(a,b,c,e), 64(b); `ALLOWLIST`, `allowlist_violations` | R51-14/15, R58-5, R60-5/6 | Removed or invented rows change equality; an energy-return row assigned `strict_validation` fails; a missing envelope helper gate produces an unlisted read. | 115 declared rows have classes and reasons; no envelope `raw_summary` exemption. The two salvage reads leave A2 RED. |
| 10 | 51(0,h), 61(a,b,d); module docstring and limitations | Text | The ruled deliberate class is explicitly outside the sweep’s promise. | The promise and class text are present; no new evasion rule was added. |
| 11 | Ruled returns | — | Two watched reads, 11 ungated energy members, one member without a kind, and the campaign conflict prevent acceptance. | Independent authorized work is complete; no returned production path was changed. |
| 12 | Suites and A5 fences | — | V1: exactly two inventory failures. | V2: 343/343; builder forward check twice, byte-identical logs; `git diff --check` passes. Frozen files and consumer import fence pass. |

### Allowlist: 115 declared rows

`†` marks the three campaign rows returned for a semantic ruling. Class counts: 57 `non_claim`, 44 `strict_validation`, eight `behind_gate`, three `gate_body`, two `tolerant_definition`, one `historical`.

| # | Scope | Operation / file | Class | Reason |
|---:|---|---|---|---|
| 1 | `joulewise/analysis_engine/registry.py::validate_attempt_ledger` | `direct:read_authentication_input` / `metadata.json` | `non_claim` | Clause (i): run, launch, and target-model identity fields in the attempt ledger. |
| 2 | `joulewise/analysis_engine/registry.py::validate_manifest_target_evidence` | `direct:read_authentication_input` / `metadata.json` | `non_claim` | Clause (i): `runtime.target_model_artifact_sha256`. |
| 3 | `joulewise/analysis_manifest_v3.py::_derive_arms_and_entries` | `direct:_read_manifest_input` / `metadata.json` | `non_claim` | Clause (i): model artifact, tokenizer, adapters, device, model, and quantization identities. |
| 4 | `joulewise/analysis_manifest_v3.py::_floor_consumer_contexts` | `direct:_read_manifest_input` / `metadata.json` | `non_claim` | Clause (i): machine, platform, adapters, workload/model/tokenizer/sampler/output-policy, device, and quantization identities. |
| 5 | `joulewise/arm_readiness.py::authenticate_bundle_launch_lineage` | `direct:read_bytes` / `metadata.json` | `non_claim` | Clause (i): launch-lineage identity and completion fields. |
| 6 | `joulewise/battery_float.py::authenticate_bundle` | `direct:_required_object` / `metadata.json` | `gate_body` | One of the three closed gate bodies. |
| 7 | `joulewise/bundle.py::RunBundleWriter.write_power_trace` | `direct:open` / `power_trace.csv` | `non_claim` | Clause (i): no field read; writes a new trace. |
| 8 | `joulewise/bundle_read.py::BundleReader.events` | `direct:_strict_json` / `metadata.json` | `non_claim` | Clause (i): `battery_float` presence when the journal is missing. |
| 9 | `joulewise/bundle_read.py::BundleReader.is_complete` | `raw_summary` / `-` | `strict_validation` | Validates summary presence/status; returns boolean. |
| 10 | `joulewise/bundle_read.py::BundleReader.is_event_v2` | `raw_metadata` / `-` | `strict_validation` | Validates event semantics identity; returns boolean. |
| 11 | `joulewise/bundle_read.py::BundleReader.is_frozen_legacy_identity` | `raw_metadata` / `-` | `strict_validation` | Validates frozen legacy identity; returns boolean. |
| 12 | `joulewise/bundle_read.py::BundleReader.metadata` | `direct:_strict_json` / `metadata.json` | `gate_body` | One of the three closed gate bodies. |
| 13 | `joulewise/bundle_read.py::BundleReader.problems` | `direct:read_authentication_text` / `metadata.json` | `strict_validation` | Validates structure; returns problem strings. |
| 14 | `joulewise/bundle_read.py::BundleReader.rail_manifest` | `raw_metadata` / `-` | `non_claim` | Clause (i): rail-manifest identity and labels. |
| 15 | `joulewise/bundle_read.py::BundleReader.raw_metadata` | `direct:_tolerant_json` / `metadata.json` | `tolerant_definition` | Forwards watched metadata; callers are inventoried. |
| 16 | `joulewise/bundle_read.py::BundleReader.raw_summary` | `direct:_tolerant_json` / `summary_metrics.json` | `tolerant_definition` | Forwards watched summary; callers are inventoried. |
| 17 | `joulewise/bundle_read.py::_check_power_trace` | `direct:open_authentication_input` / `power_trace.csv` | `strict_validation` | Validates trace structure; returns problem strings. |
| 18 | `joulewise/bundle_read.py::authenticate_window_members` | `direct:_strict_json` / `metadata.json` | `gate_body` | One of the three closed gate bodies. |
| 19 | `joulewise/bundle_read.py::axi_v2_validation_problems` | `raw_config` / `-` | `strict_validation` | Validates event-v2/AXI bundle; returns problem strings. |
| 20 | `joulewise/bundle_read.py::axi_v2_validation_problems` | `raw_metadata` / `-` | `strict_validation` | Same validator and return. |
| 21 | `joulewise/bundle_read.py::axi_v2_validation_problems` | `raw_summary` / `-` | `strict_validation` | Same validator and return. |
| 22 | `joulewise/calibration_ledger.py::_artifact_hashes_unbounded` | `direct:hash_core` / `power_trace.csv` | `non_claim` | Clause (i): opaque bytes and digests; no parsed field. |
| 23 | `joulewise/calibration_ledger.py::_custody_state_unbounded` | `direct:custody_state` / `power_trace.csv` | `non_claim` | Clause (i): opaque artifact custody and digests. |
| 24 | `joulewise/calibration_ledger.py::_governed_raw_nofollow_unbounded` | `direct:_read_contained_nofollow_unbounded` / `power_trace.csv` | `non_claim` | Clause (i): opaque governed bytes to custody verification. |
| 25 | `joulewise/cli.py::_cmd_reduce` | `direct:read_authentication_text` / `summary_metrics.json` | `non_claim` | Clause (ii): reduced summary goes to stdout; an exit code goes to `main`; no tracked claim writer consumes stdout. |
| 26 | `joulewise/cli.py::_strict_emitted_token_ids_problems` | `raw_metadata` / `-` | `strict_validation` | Validates strict bundle; returns problem strings. |
| 27 | `joulewise/cli.py::_strict_problems` | `raw_config` / `-` | `strict_validation` | Same validator and return. |
| 28 | `joulewise/cli.py::_strict_problems` | `raw_metadata` / `-` | `strict_validation` | Same validator and return. |
| 29 | `joulewise/cli.py::_strict_problems` | `raw_summary` / `-` | `strict_validation` | Same validator and return. |
| 30 | `joulewise/cli.py::_strict_realized_output_problems` | `raw_config` / `-` | `strict_validation` | Validates strict bundle; returns problem strings. |
| 31 | `joulewise/cli.py::_strict_realized_output_problems` | `raw_metadata` / `-` | `strict_validation` | Same validator and return. |
| 32 | `joulewise/cli.py::_strict_reducer_version_dispatch` | `raw_metadata` / `-` | `strict_validation` | Validates strict bundle; returns problem strings. |
| 33 | `joulewise/cli.py::_strict_rich_telemetry_problems` | `raw_metadata` / `-` | `strict_validation` | Validates strict bundle; returns problem strings. |
| 34 | `joulewise/cli.py::_strict_uncertainty_evidence_problems` | `raw_metadata` / `-` | `strict_validation` | Validates strict bundle; returns problem strings. |
| 35 | `joulewise/cli.py::_strict_workload_provenance_problems` | `raw_metadata` / `-` | `strict_validation` | Validates strict bundle; returns problem strings. |
| 36 | `joulewise/cli.py::_verify_nvidia_smi_raw_to_trace` | `raw_metadata` / `-` | `strict_validation` | Validates strict bundle; returns problem strings. |
| 37 | `joulewise/cli.py::_verify_powermetrics_raw_to_trace` | `raw_metadata` / `-` | `strict_validation` | Validates strict bundle; returns problem strings. |
| 38 | `joulewise/controller.py::_experiment_cooldown_anchor` | `direct:read_text` / `metadata.json` | `non_claim` | Clause (i): environment snapshot digest. |
| 39 | `joulewise/controller.py::_experiment_cooldown_reference_eligibility` | `direct:read_text` / `metadata.json` | `non_claim` | Clause (i): admission decision/pass/provenance and policy digest. |
| 40 | `joulewise/controller.py::_member_gap_note` | `direct:read_text` / `metadata.json` | `non_claim` | Clause (i): `extra.preceding_gap_s`. |
| 41 | `joulewise/determinism_gate.py::_check_gate_json_evidence_for_duplicate_keys` | `direct:_load_json_without_duplicate_keys` / `metadata.json` | `strict_validation` | Checks duplicate keys; appends problem strings. |
| 42 | `joulewise/determinism_gate.py::_check_gate_json_evidence_for_duplicate_keys` | `direct:_load_jsonl_without_duplicate_keys` / `metadata.json` | `strict_validation` | Same check and output. |
| 43 | `joulewise/determinism_gate.py::_inspect_strict_valid_bundle` | `raw_config` / `-` | `strict_validation` | Checks duplicate keys; appends problem strings. |
| 44 | `joulewise/envelope_gate.py::_bundle_hashes` | `direct:encode` / `metadata.json` | `non_claim` | Clause (i): hashes opaque artifact bytes. |
| 45 | `joulewise/envelope_gate.py::_bundle_hashes` | `direct:read_bytes` / `metadata.json` | `non_claim` | Same opaque hash operation. |
| 46 | `joulewise/floor_extraction.py::_cpu_admission_bundle_reasons` | `direct:_strict_admission_json_file` / `metadata.json` | `behind_gate` | Callers-form gated chain. |
| 47 | `joulewise/floor_extraction.py::_evaluate_member` | `direct:_strict_admission_json_file` / `metadata.json` | `behind_gate` | Callers-form gated chain. |
| 48 | `joulewise/floor_extraction.py::_read_summary` | `direct:_strict_admission_json_value` / `summary_metrics.json` | `behind_gate` | Callers-form gated chain. |
| 49 | `joulewise/floor_extraction.py::_read_summary` | `direct:read_authentication_input` / `summary_metrics.json` | `behind_gate` | Callers-form gated chain. |
| 50 | `joulewise/idle_dependence.py::derive_idle_mean_uncertainty` | `raw_artifact_bytes` / `-` | `behind_gate` | Callers-form gated chain. |
| 51 | `joulewise/output_identity.py::_bundle_reference` | `direct:_hash_file` / `summary_metrics.json` | `non_claim` | Clause (i): opaque summary bytes and digest. |
| 52 | `joulewise/output_identity.py::_bundle_reference` | `direct:_json_object` / `metadata.json` | `non_claim` | Clause (i): run ID and tokenizer identity. |
| 53 | `joulewise/output_identity.py::_bundle_reference` | `direct:_json_object` / `summary_metrics.json` | `non_claim` | Clause (i): object presence and opaque byte hash; no summary value. |
| 54 | `joulewise/publication_privacy.py::_audit_metadata` | `direct:_load_json_object` / `metadata.json` | `strict_validation` | Validates public privacy schema; returns problems or `None`. |
| 55 | `joulewise/publication_privacy.py::_audit_metadata` | `direct:_unknown_keys` / `metadata.json` | `strict_validation` | Same validator and return. |
| 56 | `joulewise/publication_privacy.py::_audit_summary` | `direct:_load_json_object` / `summary_metrics.json` | `strict_validation` | Same validator and return. |
| 57 | `joulewise/publication_privacy.py::_audit_summary` | `direct:_unknown_keys` / `summary_metrics.json` | `strict_validation` | Same validator and return. |
| 58 | `joulewise/publication_privacy.py::verify_public_bundle` | `direct:_load_json_object` / `metadata.json` | `strict_validation` | Same validator and return. |
| 59 | `joulewise/publication_privacy.py::verify_public_bundle` | `direct:_load_json_object` / `summary_metrics.json` | `strict_validation` | Same validator and return. |
| 60 | `joulewise/reduce.py::_resolve_reducer_version` | `raw_config` / `-` | `strict_validation` | Validates reducer-version identity; returns only that identity. |
| 61 | `joulewise/reduce.py::_resolve_reducer_version` | `raw_summary` / `-` | `strict_validation` | Same validator and return. |
| 62 | `joulewise/reduce.py::_verify_instrument_calibration` | `raw_config` / `-` | `non_claim` | Clause (i): sampler cadence `sampling.power_hz`, used for interval milliseconds. |
| 63 | `joulewise/report.py::_discover_bundles` | `raw_config` / `-` | `non_claim` | Clause (ii): `_Bundle` records go to `generate_report`, which writes static browser HTML and chart PNGs; no tracked paper claim consumes them. |
| 64 | `joulewise/report.py::_discover_bundles` | `raw_metadata` / `-` | `non_claim` | Same outputs and recipient. |
| 65 | `joulewise/report.py::_discover_bundles` | `raw_summary` / `-` | `non_claim` | Same outputs and recipient. |
| 66 | `joulewise/salvage_dangler.py::_inspect_preworkload_abort` | `direct:_read_json_object` / `metadata.json` | `non_claim` | Clause (i): run ID and admission decision, attempts, claim reason. |
| 67 | `joulewise/salvage_dangler.py::inspect_salvage_attempt` | `direct:_read_json_object` / `metadata.json` | `non_claim` | Clause (i): run ID for bundle identity. |
| 68 | `joulewise/whole_window.py::_authenticated_bundle_launch_lineage_set` | `direct:_read_json_object` / `metadata.json` | `strict_validation` | Validates lineage; returns shared identity. |
| 69 | `joulewise/whole_window.py::_consumption_provenance_valid` | `direct:_read_json_object` / `summary_metrics.json` | `strict_validation` | Validates provenance/current strict validity; returns identity, boolean, digest, or problems. |
| 70 | `joulewise/whole_window.py::_current_core_rederivation_reasons` | `direct:_read_json_object` / `metadata.json` | `strict_validation` | Same validation-return restriction. |
| 71 | `joulewise/whole_window.py::_current_core_rederivation_reasons` | `direct:_read_json_object` / `summary_metrics.json` | `strict_validation` | Same validation-return restriction. |
| 72 | `joulewise/whole_window.py::_manifest_bundle_paths` | `direct:_read_json_object` / `summary_metrics.json` | `strict_validation` | Validates bundle identities; returns path identity map. |
| 73 | `joulewise/whole_window.py::_manifest_members` | `direct:_read_json_object` / `summary_metrics.json` | `strict_validation` | Validates bundle identities; returns identity set. |
| 74 | `joulewise/whole_window.py::_row_references_current_strict_member` | `direct:_read_json_object` / `summary_metrics.json` | `strict_validation` | Validates provenance/current strict validity; restricted return. |
| 75 | `joulewise/whole_window.py::_scientific_config_identity` | `direct:_read_json_object` / `metadata.json` | `strict_validation` | Validates scientific config digest/canonicality. |
| 76 | `joulewise/whole_window.py::_validate_row_uncached` | `direct:_read_json_object` / `summary_metrics.json` | `strict_validation` | Validates provenance/current strict validity; restricted return. |
| 77 | `joulewise/whole_window.py::_validated_evaluation_basis` | `direct:read_authentication_input` / `metadata.json` | `non_claim` | Clause (i): opaque metadata bytes hashed against bound digest. |
| 78 | `joulewise/whole_window.py::custody_telemetry_identity` | `direct:_read_json_object` / `metadata.json` | `strict_validation` | Validates telemetry identity; returns class identity/agreement booleans. |
| 79 | `joulewise/whole_window.py::custody_telemetry_identity` | `direct:_read_json_object` / `summary_metrics.json` | `strict_validation` | Same validator and return. |
| 80 | `joulewise/whole_window.py::validate_occurrence_supersession_entry` | `direct:read_authentication_input` / `metadata.json` | `strict_validation` | Validates provenance/current strict validity; restricted return. |
| 81 | `joulewise/whole_window.py::whole_window_refusal_reasons` | `direct:_read_json_object` / `summary_metrics.json` | `strict_validation` | Validates provenance/current strict validity; returns problems. |
| 82 | `scripts/analyze_phase_share.py::analyze_bundle` | `direct:_sha256` / `power_trace.csv` | `non_claim` | Clause (ii): diagnostic sensitivity record goes to `main`, which writes desk diagnostic JSON, not a governed claim artifact. |
| 83 | `scripts/analyze_phase_share.py::analyze_bundle` | `raw_summary` / `-` | `non_claim` | Same output and recipient. |
| 84 | `scripts/build_battery_float_historical_bundles.py::witness` | `direct:_strict_json` / `metadata.json` | `non_claim` | Clause (i): run ID; witness compares names and digests. |
| 85 | `scripts/check_window_provenance.py::_run_assertions.check_a3` | `direct:_read_object` / `summary_metrics.json` | `non_claim` | Clause (ii): assertion string goes to `Reporter.assertion`, then stdout; `_run_assertions` returns exit code to `main`; no tracked claim writer reads stdout. |
| 86 | `scripts/corpus_compat_receipt.py::evaluate_bundle` | `raw_config` / `-` | `non_claim` | Clause (i): no config field read; config is carried but ignored by token provenance. |
| 87 | `scripts/corpus_compat_receipt.py::evaluate_bundle` | `raw_metadata` / `-` | `non_claim` | Clause (i): run/output-token identities and token policy, tokenizer, suite identities. |
| 88 | `scripts/corpus_compat_receipt.py::evaluate_bundle` | `raw_summary` / `-` | `non_claim` | Clause (i): `measurement_quality.token_counts_source`. |
| 89 | `scripts/issue_dg071_dg075_statistics.py::main` | `direct:issue_artifacts` / `power_trace.csv` | `historical` | Amendment 41 pins the pre-directive a10 trace by committed SHA-256. |
| 90 | `scripts/make_figures.py::extract_rows` | `raw_config` / `-` | `non_claim` | Clause (ii): figure rows have no tracked production caller; `main` writes only placeholder figures. |
| 91 | `scripts/make_figures.py::extract_rows` | `raw_metadata` / `-` | `non_claim` | Same output and recipient. |
| 92 | `scripts/make_figures.py::extract_rows` | `raw_summary` / `-` | `non_claim` | Same output and recipient. |
| 93 | `scripts/make_figures.py::gate_inputs` | `raw_summary` / `-` | `non_claim` | Clause (i): summary status. |
| 94 | `scripts/make_figures.py::realized_output_tokens` | `raw_metadata` / `-` | `non_claim` | Clause (i): observed output-token count fields. |
| 95 | `scripts/package_bundle_pack.py::_bundle_id` | `direct:_load_json_file` / `metadata.json` | `non_claim` | Clause (i): run ID. |
| 96 | `scripts/package_bundle_pack.py::_preflight_bundle` | `raw_metadata` / `-` | `non_claim` | Clause (i): source-provenance identity and eligibility fields. |
| 97 | `scripts/package_bundle_pack.py::_summary_status` | `direct:_load_json_file` / `summary_metrics.json` | `non_claim` | Clause (i): summary status. |
| 98 | `scripts/paper_prefill_resolvability_projection.py::scan_corpora` | `direct:read_model` / `metadata.json` | `non_claim` | Clause (i): model name/revision; prefill identifiability label; trace support timestamps; opaque trace digest. |
| 99 | `scripts/paper_prefill_resolvability_projection.py::scan_corpora` | `direct:read_support_intervals` / `power_trace.csv` | `non_claim` | Clause (i): `timestamp_s`, `interval_start_s`, `interval_end_s`; no power value. |
| 100 | `scripts/paper_prefill_resolvability_projection.py::scan_corpora` | `direct:recorded_label` / `summary_metrics.json` | `non_claim` | Clause (i): prefill phase-identifiability label; no energy value. |
| 101 | `scripts/paper_prefill_resolvability_projection.py::scan_corpora` | `direct:sha256_of` / `power_trace.csv` | `non_claim` | Clause (i): opaque trace bytes/digest. |
| 102 | `scripts/run_campaign.py::_axi_discover_finalized_bundles` | `direct:read_bytes` / `metadata.json` | `non_claim` | Clause (i): run/attempt identity for finalized-bundle discovery. |
| 103 | `scripts/run_campaign.py::_basis_member_occurrences` | `direct:read_bytes` / `metadata.json` | `non_claim` | Clause (i): run identity and launch lineage for occurrence binding. |
| 104 | `scripts/run_campaign.py::_run_record_supersession_locked` | `direct:read_bytes` / `metadata.json` | `non_claim` | Clause (i): run identity for supersession. |
| 105 | `scripts/run_campaign.py::authenticate_campaign_child_launch_lineage` | `direct:read_bytes` / `metadata.json` | `non_claim` | Clause (i): launch lineage and completion identity. |
| 106 | `scripts/run_campaign.py::evaluate_member` | `direct:read_text` / `metadata.json` | `behind_gate` † | Ruled consumers form: content should reach only the listed gated campaign chains. |
| 107 | `scripts/run_campaign.py::evaluate_member` | `direct:read_text` / `summary_metrics.json` | `behind_gate` † | Same ruled consumers form. |
| 108 | `scripts/run_campaign.py::evaluate_member` | `direct:summary_status` / `summary_metrics.json` | `behind_gate` † | Same ruled consumers form. |
| 109 | `scripts/run_campaign.py::existing_state` | `direct:summary_status` / `summary_metrics.json` | `non_claim` | Clause (i): summary status only. |
| 110 | `scripts/run_campaign.py::run_axi_spec_campaign` | `direct:read_bytes` / `metadata.json` | `non_claim` | Clause (i): `batch.admitted_request_count` for dispatch receipt. |
| 111 | `scripts/run_campaign.py::suite_order_evidence` | `direct:_load_json_object` / `metadata.json` | `non_claim` | Clause (i): suite order, run identity, seed. |
| 112 | `scripts/summarize_g2a_prefill_probe.py::summarize` | `direct:_load_json` / `metadata.json` | `non_claim` | Clause (i): run ID and prompt token count/digest. |
| 113 | `scripts/summarize_g2a_prefill_probe.py::summarize` | `direct:_load_json` / `summary_metrics.json` | `non_claim` | Clause (i): prefill window in-window sample count. |
| 114 | `scripts/validate_powermetrics_fiducial.py::main` | `direct:_write_text_artifact` / `power_trace.csv` | `non_claim` | Clause (i): no field read; writes a new trace. |
| 115 | `scripts/validate_powermetrics_fiducial.py::main` | `direct:sha256_path` / `power_trace.csv` | `non_claim` | Clause (i): opaque trace hash. |

### Raw-capture screen: 48 members

The mapping holds 15 `custody`, 15 `names`, two `timing`, and four gated `energy` entries. “No gate; returned” members are intentionally absent from its keys.

| # | Scope | Semantic kind | Gate / disposition |
|---:|---|---|---|
| 1 | `joulewise/calibration_bracketing.py::_load_calibration_candidate_unbounded` | `energy` | No gate; returned |
| 2 | `joulewise/calibration_ledger.py::_artifact_hashes_unbounded` | `custody` | — |
| 3 | `joulewise/calibration_ledger.py::_custody_state` | `custody` | — |
| 4 | `joulewise/calibration_ledger.py::_custody_state_unbounded` | `custody` | — |
| 5 | `joulewise/calibration_ledger.py::_custody_store_manifest_projection` | `names` | — |
| 6 | `joulewise/calibration_ledger.py::_custody_store_reasons` | `custody` | — |
| 7 | `joulewise/calibration_ledger.py::_governed_raw_nofollow_unbounded` | `custody` | — |
| 8 | `joulewise/calibration_ledger.py::_historical_import_table` | `names` | — |
| 9 | `joulewise/calibration_ledger.py::_inspect_historical_candidate` | `custody` | — |
| 10 | `joulewise/calibration_ledger.py::artifact_hashes` | `custody` | — |
| 11 | `joulewise/calibration_ledger.py::resume_finalize_bracket_session` | `custody` | — |
| 12 | `joulewise/cli.py::_strict_rich_telemetry_problems` | `energy` | No gate; returned |
| 13 | `joulewise/cli.py::_strict_uncertainty_evidence_problems` | `energy` | No gate; returned |
| 14 | `joulewise/cli.py::_verify_powermetrics_raw_to_trace` | `energy` | No gate; returned |
| 15 | `joulewise/controller.py::_load_instrument_calibration_attachment` | `energy` | No preceding gate; returned |
| 16 | `joulewise/environment_admission.py::_window_thermal_pressure_refusals` | No ruled kind fits | Returned |
| 17 | `joulewise/idle_dependence.py::_base_payload` | `names` | — |
| 18 | `joulewise/idle_dependence.py::derive_idle_mean_uncertainty` | `energy` | Gated callers |
| 19 | `joulewise/powermetrics_fiducial.py::instrument_evidence` | `names` | — |
| 20 | `joulewise/publication_privacy.py::_audit_idle_mean_uncertainty` | `names` | — |
| 21 | `joulewise/publication_privacy.py::_path_policy` | `names` | — |
| 22 | `joulewise/receipt_oracle.py::derive_bracket_session_receipt_oracle` | `names` | — |
| 23 | `joulewise/reduce.py::_derive_anchor_context` | `energy` | Gated callers |
| 24 | `joulewise/reduce.py::_verify_instrument_calibration` | `energy` | No gate; returned |
| 25 | `joulewise/salvage_dangler.py::_expected_idle_artifact_sets` | `names` | — |
| 26 | `joulewise/schemas.py::SummaryMetrics.json_schema` | `names` | — |
| 27 | `joulewise/uncertainty_evidence.py::derive_idle_drift_evidence` | `names` | — |
| 28 | `joulewise/window_duration_margins.py::_observe_member` | `custody` | — |
| 29 | `scripts/calibration_cadence_report.py::capture_paths` | `custody` | — |
| 30 | `scripts/calibration_cadence_report.py::report_window` | `timing` | — |
| 31 | `scripts/check_paper_replay_fence.py::derive_from_artifacts` | `energy` | No gate; returned |
| 32 | `scripts/check_paper_replay_fence.py::locate_raw_powermetrics` | `custody` | — |
| 33 | `scripts/check_paper_round7_artifacts.py::_required_corpus_paths` | `names` | — |
| 34 | `scripts/floor_reconciliation_receipt.py::_anchored_records` | `energy` | Gated caller |
| 35 | `scripts/floor_reconciliation_receipt.py::_bundle_row` | `energy` | Gate in function |
| 36 | `scripts/floor_reconciliation_receipt.py::build_receipt` | `custody` | — |
| 37 | `scripts/hydrate_d117_fixture.py::_validate_archive` | `names` | — |
| 38 | `scripts/hydrate_d117_fixture.py::load_descriptor` | `names` | — |
| 39 | `scripts/issue_calibration_acceptance_generation.py::_derivation_frame_cadence` | `timing` | — |
| 40 | `scripts/package_d117_fixture.py::load_census_bytes` | `names` | — |
| 41 | `scripts/paper_anchor_correction_quantified.py::analyse_capture` | `energy` | No gate; returned |
| 42 | `scripts/paper_anchor_correction_quantified.py::locate_raw_powermetrics` | `custody` | — |
| 43 | `scripts/paper_excursion_decomposition.py::build_payload` | `names` | — |
| 44 | `scripts/paper_excursion_decomposition.py::locate_raw_powermetrics` | `custody` | — |
| 45 | `scripts/paper_excursion_decomposition.py::rederive` | `energy` | No gate; returned |
| 46 | `scripts/run_campaign.py::assert_production_uncertainty` | `custody` | — |
| 47 | `scripts/validate_powermetrics_fiducial.py::main` | `energy` | No gate; returned |
| 48 | `scripts/validate_powermetrics_fiducial.py::rederive_artifact` | `energy` | No gate; returned |

## Verification notes

V1’s only failures are `test_all_supported_ungated_reads_have_checked_reasons` (the two salvage rows) and `test_raw_capture_inventory` (the 12 returned members). These are deliberate visible failures, not green acceptance. V2 passed. Both builder outputs are byte-identical. The final diff has only the two `pathspec` files and passes `git diff --check`.

Exact last five lines of **V1**:

```text

----------------------------------------------------------------------
Ran 470 tests in 2304.162s

FAILED (failures=2)
```

Exact last five lines of **V2**:

```text
.......................................................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 343 tests in 983.159s

OK
```

Exact last five lines of **builder check 1**:

```text
listed_population sw7bfloor-df-ph-decode-abs-r07 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r08 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r09 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r10 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
forward check: byte-identical entries=69
```

Exact last five lines of **builder check 2**:

```text
listed_population sw7bfloor-df-ph-decode-abs-r07 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r08 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r09 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
listed_population sw7bfloor-df-ph-decode-abs-r10 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest
forward check: byte-identical entries=69
```

A5 fences: `battery_float.py` hashes to `4b4d7bb206250cc0078d2a6b0b34d4e7e6305ff1d3a8b72f93528016d935e7e5`; it, `reduce.py`, and `bundle.py` are byte-identical to `1417c0c4`. The eight named consumers have no `battery_float` import. The protected FT §E pin test passed. No commit, push, full suite, quiet-window measurement, or out-of-scope repository edit occurred.

## Residual risk

**NEEDS_RULING — watched reads.** Neither row fits the ruled classes:

| Scope and read | What it returns | Callers |
|---|---|---|
| `joulewise/salvage_dangler.py::_inspect_preworkload_abort`, `summary_metrics.json` | A salvage license dict with numeric failure/telemetry times and teardown. It checks measurand fields, so `non_claim` (i) fails; the license reaches an exclusion decision, so (ii) fails. | `inspect_preworkload_abort`, `inspect_salvage_attempt` → `load_salvage_closure` → `authorize_salvage_dangler_exclusion` → `run_campaign`. |
| `joulewise/salvage_dangler.py::_telemetry_timestamp_bounds`, `power_trace.csv` | Numeric `(first_timestamp, last_timestamp)` after parsing and checking `power_w`; its return is not restricted to validation types. | `_inspect_preworkload_abort`, then the salvage exclusion chain above. |

**NEEDS_RULING — raw captures.** These 12 members remain outside `RAW_CAPTURE_READERS`; the 11 marked `energy` have no qualifying preceding gate.

| Scope | What it returns or writes | Callers |
|---|---|---|
| `joulewise/calibration_bracketing.py::_load_calibration_candidate_unbounded` | `CalibrationCandidate` with a rederived fiducial bound, or `None`. | `load_calibration_candidate.inspect` → custody probe / calibration candidate loader. |
| `joulewise/cli.py::_strict_rich_telemetry_problems` | Rich-telemetry problem strings derived from raw power. | `_strict_problems`. |
| `joulewise/cli.py::_strict_uncertainty_evidence_problems` | Uncertainty-evidence problem strings derived from raw power. | `_strict_problems`. |
| `joulewise/cli.py::_verify_powermetrics_raw_to_trace` | Raw-to-trace problem strings derived from raw power. | `RAW_TO_TRACE_VERIFIERS` → `_strict_raw_to_trace_problems` → strict checks, including the window-duration observer. |
| `joulewise/controller.py::_load_instrument_calibration_attachment` | Calibration attachment with `verified_effective_b_fiducial_s`; it reads raw capture before its capture verdict. | `run_benchmark`. |
| `joulewise/reduce.py::_verify_instrument_calibration` | Numeric fiducial bound or refusal detail. | `_derive_anchor_context`; `AuthenticatedConsumptionSession._prepare`; `_current_core_rederivation_reasons`. |
| `scripts/check_paper_replay_fence.py::derive_from_artifacts` | Replayed calibration metrics payload. | `main`. |
| `scripts/paper_anchor_correction_quantified.py::analyse_capture` | Per-capture correction row. | `build_payload`. |
| `scripts/paper_excursion_decomposition.py::rederive` | Detection, anchor, and evidence data. | `main`. |
| `scripts/validate_powermetrics_fiducial.py::main` | Writes derived capture/evidence artifacts and returns an exit code. | Script entry point. |
| `scripts/validate_powermetrics_fiducial.py::rederive_artifact` | Re-emitted validation payload. | `main`. |
| `joulewise/environment_admission.py::_window_thermal_pressure_refusals` | Admission refusal tuple, including `thermal_pressure_elevated_in_window`. It parses pressure as well as times; no ruled `names`, `custody`, `timing`, or `energy` kind fits. | `current_environment_refusals`, then floor, whole-window, reduction, and campaign admission paths. |

**NEEDS_RULING — amendment 64(b) conflict.** The three `scripts/run_campaign.py::evaluate_member` rows are syntactically checked as `behind_gate`, but their “only to listed gated chains” reason is false on an executed code path. `evaluate_member` retains `summary["idle_baseline"]` in a `MemberEvaluation` even for a bundle whose battery gate refuses it. `_first_eligible_cooldown_anchor` freezes that value; `prior_campaign_cooldown_anchor` reads it from the authenticated campaign catalog without authenticating the source bundle; `campaign_cooldown_before_member` passes it to `cooldown_gate`; `_member_readiness_reasons` can add `cooldown_cap_hit`. The executed probe used a charging fixture and stubbed the cooldown result to isolate the path:

```text
source_gate=REFUSED battery_float_confounded
anchor_reused= True selection= frozen_clean_anchor gate_baseline= 5.0 result= cap_hit
readiness_has_cap_hit= True
```

The probe establishes propagation and the admission-reason route; it is not a hardware cooldown measurement. No campaign production code was changed.

**Question for the lead:** rule the salvage class or gated treatment, the raw-capture energy gates and thermal-pressure kind, and the campaign consumers-form contradiction. The options are targeted production changes in newly authorized lanes or an explicit amendment to the class contract. I recommend keeping A2–A4 red and ruling each returned path before acceptance. The blocked next step is a green V1 and merge-candidate refuter pass.