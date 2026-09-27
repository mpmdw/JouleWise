```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented Round 2 reducer, bracketing, eight window gates, and sweep; V1 and V2 pass, while V3 exposes fixture and environment debt.",
  "workspace": {
    "base_requested": "b859317c",
    "base_mode": "exact",
    "head_start": "b859317c7ea9286a2131ab3dce2e0d4ca9348ba5",
    "head_end": "b859317c7ea9286a2131ab3dce2e0d4ca9348ba5",
    "upstream_end": "b859317c7ea9286a2131ab3dce2e0d4ca9348ba5",
    "branch": "feat/2026-09-26-bfgs-s1-bundles"
  },
  "pathspec": [
    "joulewise/aggregate.py",
    "joulewise/analysis_engine/inputs.py",
    "joulewise/calibration_bracketing.py",
    "joulewise/floor_extraction.py",
    "joulewise/scored_reduce.py",
    "joulewise/whole_window.py",
    "joulewise/window_duration_margins.py",
    "scripts/extract_detection_floors.py",
    "scripts/mint_floor_artifact.py",
    "scripts/run_campaign.py",
    "tests/test_battery_float_consumers.py",
    "tests/test_bfgs_calibration_bracketing.py",
    "tests/test_bfgs_consumer_sweep.py",
    "tests/test_bfgs_window_consumers.py",
    "tests/test_bundle_read.py",
    "tests/test_controller.py",
    "tests/test_scored_reduce.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
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
        "tail": ["----------------------------------------------------------------------", "Ran 416 tests in 1557.546s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_evidence_night tests.test_night_kinds",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["----------------------------------------------------------------------", "Ran 316 tests in 486.530s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_aggregate tests.test_analysis_claims tests.test_analysis_engine tests.test_analysis_finalizer tests.test_analysis_inputs tests.test_analysis_integration tests.test_analysis_manifest tests.test_analysis_manifest_v3 tests.test_analysis_ratio_integration tests.test_audit_amplification tests.test_audit_bundle_validation tests.test_authentication_io tests.test_axi_controller_events tests.test_axi_mock_spec tests.test_axi_request_validation tests.test_bracket_binding_cli tests.test_calibration_bracketing tests.test_calibration_custody_store tests.test_calibration_exits tests.test_calibration_ledger tests.test_calibration_ledger_custody tests.test_calibration_live_three_window tests.test_check_window_provenance tests.test_cli tests.test_cli_run tests.test_collector_analysis_manifest_id tests.test_corpus_strict_validation tests.test_custody_mode_inventory tests.test_d078_reason_registry tests.test_d117_contrast_v5_pack tests.test_d117_decode_contrast_plan tests.test_d117_floor_qwen25_1p5b_plan tests.test_d117_floor_qwen25_7b_plan tests.test_d117_gamma_d139a2_families tests.test_d117_v3_family tests.test_d165_dominance_closeout tests.test_decisive_reference_resolution tests.test_dependence_sensitivity tests.test_detection_floor tests.test_determinism_gate tests.test_envelope_gate tests.test_epoch_equivalence_check tests.test_experiment tests.test_floor_extraction tests.test_floor_mint_estimator tests.test_floor_mint_pinsets_schema tests.test_gate_sensibility_rounding tests.test_identity_pins tests.test_idle_dependence tests.test_issue_calibration_acceptance_generation tests.test_mint_floor_artifact tests.test_mint_floor_artifact_generalized tests.test_nvidia_node_integration tests.test_p2038_production_path tests.test_package_bundle_pack tests.test_paper_reported_energy tests.test_partial_record_enclosure tests.test_phase_share tests.test_pipeline_smoke_tail tests.test_powermetrics tests.test_r4_acceptance_oracle tests.test_reissue_calibration_acceptance tests.test_report tests.test_rpt001_report_slice tests.test_run_campaign tests.test_schemas tests.test_single_count_discipline_matrix tests.test_supersession_cross_consumer tests.test_uncertainty_p2029 tests.test_validate_powermetrics_fiducial_derivation_only tests.test_whole_window tests.test_whole_window_selection tests.test_window_duration_margins",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "WARNING: Benchmarks are run strictly sequentially; energy measurements must not overlap.",
          "Config files to execute:",
          "  /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpdr2swvq_/configs/one.json",
          "WARNING: This campaign needs a quiet machine with no other workloads.",
          "WARNING: Benchmarks are run strictly sequentially; energy measurements must not overlap."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "V3: 2806 tests; 119 failures, 404 errors, 23 skips. The 508 A/B records concern copied or synthetic bundle and calibration fixtures outside Round 2 write scope.",
      "needs": "Round F fixture repair followed by V3 rerun."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Fifteen D records concern process identity or live epoch environment and the pre-existing stale paper supply-map receipt.",
      "needs": "Lead-controlled environment check and receipt refresh after source freeze."
    }
  ]
}
```

## Change

| Authority | Files and functions | RED at `b859317c`; counterfactual | GREEN |
|---|---|---|---|
| Text 9 | [scored_reduce.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/scored_reduce.py:92): `_check_battery_evidence`, six-argument `reduce`; fixture producer in [test_scored_reduce.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_scored_reduce.py:145) | New six-argument test raised `TypeError: reduce() takes 5 positional arguments but 6 were given`. Removing the precheck admits missing evidence; duplicating a digest defeats `window_bundle_duplicate`. | Four new battery-evidence tests and V1 pass. Malformed windows still reach their established refusal codes; identical bundle digests refuse before `_check_window`. |
| Text 10 | [calibration_bracketing.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/calibration_bracketing.py:1814): digest-bound capture classification, discovery and registered-universe exclusion, candidate reauthentication, historical cutoff | Baseline lacked `_battery_exclusion_for_observation`; the confounded discovery witness returned both candidates instead of only the passing one. Deleting a raw file is the custody counterfactual; a late window with a historical endpoint is the cutoff counterfactual. | Eight new bracketing tests and V1 pass. The committed head is sequence `176`; merge committer time is `1790462247`. Without a ledger snapshot, evaluation returns `calibration_ledger_snapshot_required` before a candidate can bear a claim. |
| Text 12; amendments 26 and 42 | Window gates in [whole_window.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/whole_window.py:679), [inputs.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/analysis_engine/inputs.py:3130), [floor_extraction.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/floor_extraction.py:2879), [aggregate.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/aggregate.py:104), [window_duration_margins.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/window_duration_margins.py:948), [mint_floor_artifact.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/scripts/mint_floor_artifact.py:378), [extract_detection_floors.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/scripts/extract_detection_floors.py:142), and [run_campaign.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/scripts/run_campaign.py:6197) | The baseline eight-module test failed for all eight missing gate calls; an aggregate with a failed member did not raise `WindowBatteryRefusal`. Removing a gate is detected by the structural test and the read sweep. | Fifteen window-consumer tests, the reader/controller tests, and V1 pass. Outputs carry member battery status; the gate names all refused members and retains custody as an exception. |
| Text 12 sweep; amendment 41 | [test_bfgs_consumer_sweep.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_bfgs_consumer_sweep.py:1) | At baseline the sweep found 15 ungated read sites. Its self-test finds `joulewise/cli.py:423` at the pre-S1 head. Removing a named exemption or adding an ungated direct read makes the sweep fail. | Three sweep tests and V1 pass. The `scripts/issue_dg071_dg075_statistics.py::build_payload` direct `power_trace.csv` read has a named `historical` row. |
| Amendment 36 guard | [test_battery_float_consumers.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_battery_float_consumers.py:31) | Baseline guard expected 13 replace rows and failed against the required 14th. The existing forgery self-test rejects `replace(verdict, status='pass')`. | Guard count is 14; its type and pre-S1 provenance tests pass in V2. |

The exact added guard row is:

```python
("joulewise/calibration_bracketing.py", "_candidate_from_observation",
 "replace(candidate, relative_path=observation.custody_locator, attempt_id=observation.attempt_id, content_id=observation.content_id, ledger_receipt_digest=observation.receipt_digest, bracket_session_id=observation.bracket_session_id, bracket_slot=observation.bracket_slot, bracket_window_id=observation.bracket_window_id, bracket_plan_id=observation.bracket_plan_id, bracket_plan_sha256=observation.bracket_plan_sha256, bracket_evidence_root_id=observation.bracket_evidence_root_id, bracket_runs_root=observation.bracket_runs_root)"): REPLACE_REASON,
```

The replaced value is `CalibrationCandidate`: its dataclass is at [calibration_bracketing.py:610](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/calibration_bracketing.py:610), the loader return type at line 1521, and the assignment to `candidate` at line 1686. The provenance guard confirms that exact call predates S1.

## Verification notes

The `rg -l` import search identified 83 test modules. V1/V2 cover 10; V3 ran the other 73, listed in its replay command above. `git diff --check` passed. All 17 changed paths are in `WRITE_SCOPE`; the excluded pin paths and `joulewise/battery_float.py` have no diff. No commit was made.

**Exact last five lines of V1:**

```text
................................................................................................................................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 416 tests in 1557.546s

OK
```

**Exact last five lines of V2:**

```text
............................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 316 tests in 486.530s

OK
```

**Exact last five lines of V3:**

```text
WARNING: Benchmarks are run strictly sequentially; energy measurements must not overlap.
Config files to execute:
  /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpdr2swvq_/configs/one.json
WARNING: This campaign needs a quiet machine with no other workloads.
WARNING: Benchmarks are run strictly sequentially; energy measurements must not overlap.
```

V3’s unittest summary precedes those buffered test prints: `Ran 2806 tests in 1962.661s` and `FAILED (failures=119, errors=404, skipped=23)`. Its fresh A/B/C/D index is:

| Class | Records | Modules and cause |
|---|---:|---|
| A | 146 | Bare prospective refusals from copied or synthetic non-MOCK bundles, including `test_analysis_finalizer` (15), `test_bracket_binding_cli` (19), `test_check_window_provenance` (25), `test_d165_dominance_closeout` (48), and mixed cases in `test_analysis_integration`, `test_floor_extraction`, `test_run_campaign`, and `test_whole_window_selection`. Inherited A IDs from the prior triage remain A when a later assertion masks the refusal. |
| B | 362 | Fixtures with missing metadata, an unbound MOCK config, or synthetic capture evidence without a valid pair. Largest groups: `test_aggregate` (27), `test_analysis_integration` (40), `test_calibration_live_three_window` (20), `test_cli_run` (25), `test_floor_extraction` (25), `test_run_campaign` (89), and `test_window_duration_margins` (24). Other affected fixture modules are named by the V3 command. |
| C | 0 | **No V3 case established an unruled S1 production behavior defect.** |
| D | 15 | `test_axi_controller_events` (2), `test_axi_mock_spec` (2), `test_collector_analysis_manifest_id` (9), `test_issue_calibration_acceptance_generation` (1), and `test_paper_reported_energy` (1): process identity or live epoch environment, and the stale supply-map receipt. |

## Residual risk

V3 cannot become green in this round without editing older fixture files outside `WRITE_SCOPE`; amendment 38 assigns that work to Round F. The D cases require lead-controlled environment and receipt handling after the source changes are frozen.