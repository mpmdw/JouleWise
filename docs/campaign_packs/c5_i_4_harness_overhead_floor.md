# C5-I.4 Pack: Harness Overhead Floor

Status: verdict-contingent DRAFT. This is an export/shim methodology pack, not
an import pack. It depends directly on P2-022 marker-shim landing and uses the
C-015 external marked-runner contract.

## Pinned Now

- AP row for harness/process overhead as a methodology result.
- P2-022 shim contract fields and verdict branches.
- Overhead decomposition: harness start/end, item start/end, external results
  hash, marker validation, and measured-window inclusion.
- Negative branch: if markers are unsupported, record feasibility verdict and
  make no energy comparison.
- Figures for overhead fraction, marker-validity waterfall, and verdict table.

## DRAFT AP Row

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-C5-I.4 / C5-I.4 harness overhead floor. DRAFT until P2-022 verdict and registry freeze. |
| family_id | FAM-C5I4-HARNESS-OVERHEAD |
| claim_role | primary |
| selection_scope | Frozen external marked-runner harness `<<P2-022.HARNESS_NAME_VERSION>>`, subset `<<P2-022.SUBSET_ID>>`, at least three marked items, shim verdict branch, model/runtime/artifact/quant/tokenizer/sampler/output policy owned by the external harness, and same/calibrated measurement boundary. Countable contrasts are harness-level overhead fraction and item-window inclusion checks for each frozen harness x item/subset cell. |
| multiplicity_rule | Holm within FAM-C5I4-HARNESS-OVERHEAD across predeclared overhead-fraction and marker-validity contrasts when `external_markers_supported` or eligible `partial(<limitation>)` holds. If verdict is `external_markers_unsupported`, analysis is exploratory/no-confirmatory-inference feasibility only. |
| Metric + exact window class | Harness process overhead energy/time on session or request windows; item-window energy only when item markers pair, fall inside measured windows, and P2-015 item floors clear. Components: harness start/end, item start/end, external results hash, marker validation, and measured-window inclusion. |
| Unit of analysis + dependence structure | Marked harness run or bundle repetition. Items within a harness process are nested and not independent replicates unless repeated bundles/blocks are frozen. |
| Estimator/formula | `overhead_fraction = (harness_window_energy_j - sum(valid_item_window_energy_j)) / harness_window_energy_j` when marker coverage supports decomposition. Verdict table records exactly `external_markers_supported`, `partial(<limitation>)`, or `external_markers_unsupported`; every partial verdict must include the limitation payload inside the parentheses. Energy comparisons require strict bundles, repeated runs, and same/calibrated boundary. |
| Inclusion/exclusion + quality-flag waiver rules | Include only strict-valid bundles with C-015 shim fields, paired item markers, monotonic timestamps, markers inside measured window, non-overlap unless declared, external results artifact SHA-256, and reducer success. Unsupported marker verdict records feasibility only and excludes energy comparison. |
| Order/blocking/covariates | External harness order is frozen or recorded from harness output. Record item index, harness process ID, marker timestamp source, block/session, cooldown flags, and any partial verdict limitation. |
| Floor gate | pending-P2-015: consume matching item-window rows such as `DF-ITEM` for item energy, matching request/session rows such as `DF-RQ-GROSS-MID`, `DF-RQ-IDLE-MID`, and `DF-CMP-ABBA-RQ` for harness/request energy, and any marker-jitter/telemetry floor rows added by P2-015. Missing matching floor rows cap overhead-energy claims at L1/descriptive. |
| MDE/n sizing + predeclared top-up rule | P2-022 feasibility needs at least 3 marked items. L2 overhead comparisons require n>=5 repeated harness bundles or accepted repeated-block design; top up to n=10 when overhead fraction CI crosses the active floor, marker-validity verdict changes under leave-one-out, or partial limitation affects the headline cell. |
| Denominator provenance requirement | Shim schema version, harness name/version, command argv hash, environment allowlist, benchmark name/revision, subset ID, external results path and SHA-256, item marker timestamps, timestamp source, item IDs, prompt/output hashes when reported, token counts when reported, boundary label, telemetry backend, and bundle hashes. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L1/L2`. Forbidden upgrade: `no item energy claim when harness overhead dominates unnoticed`. |
| Disqualifiers + not-resolvable conditions | `external_markers_unsupported`, missing external results hash, unpaired markers, non-monotonic timestamps, markers outside measured window, overlapping items undeclared, failed strict validation, no matching floor row, same/calibrated boundary absent for L2 comparison, or accuracy/pass@k/leaderboard interpretation. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## Manifest/Config Templates

The template mirrors `docs/contracts/adapter_contracts.md`. The
`<<P2-022.*>>` fields are filled only after the marker-shim feasibility spike
lands.

```json
{
  "schema_version": "0.1",
  "run_kind": "external_marked_runner",
  "run_id": "c5-i4-overhead-<<P2-022.HARNESS_NAME>>-<<P2-022.SUBSET_ID>>",
  "external_runner": {
    "shim_schema_version": "<<P2-022.SHIM_SCHEMA_VERSION>>",
    "invocation": {
      "harness_name": "<<P2-022.HARNESS_NAME>>",
      "harness_version": "<<P2-022.HARNESS_VERSION>>",
      "command_argv_sha256": "<<P2-022.COMMAND_ARGV_SHA256>>",
      "working_dir_sha256_or_null": "<<P2-022.WORKING_DIR_SHA256_OR_NULL>>",
      "environment_allowlist": "<<P2-022.ENVIRONMENT_ALLOWLIST>>",
      "benchmark_name": "<<P2-022.BENCHMARK_NAME>>",
      "benchmark_revision": "<<P2-022.BENCHMARK_REVISION>>",
      "subset_id": "<<P2-022.SUBSET_ID>>",
      "external_results_path": "<<P2-022.EXTERNAL_RESULTS_PATH>>",
      "external_results_sha256": "<<P2-022.EXTERNAL_RESULTS_SHA256>>"
    },
    "events": {
      "required_event_types": ["harness_start", "harness_end", "item_start", "item_end"],
      "required_top_level_keys": ["timestamp_s", "event_type", "phase", "message", "metadata"],
      "metadata_required": [
        "run_id",
        "harness_item_id",
        "item_index",
        "benchmark_name",
        "subset_id",
        "prompt_sha256_or_null",
        "output_sha256_or_null",
        "external_metric_record_id_or_null",
        "status",
        "error_type_or_null",
        "token_counts_if_reported",
        "timestamp_source"
      ]
    },
    "validation": {
      "require_paired_item_markers": true,
      "require_monotonic_timestamps": true,
      "require_markers_inside_measured_window": true,
      "require_no_overlapping_items_unless_declared": true,
      "require_external_results_hash": true
    }
  },
  "verdict_branch": "<<P2-022.VERDICT: external_markers_supported | partial(<limitation>) | external_markers_unsupported>>",
  "run_metadata": {
    "project": "capstone-joulewise",
    "operator": "ed",
    "tags": ["c5-i.4", "external-marked-runner", "harness-overhead"]
  }
}
```

## Expected Artifacts

```text
runs/<base_run_id>__rN/
  config.json
  metadata.json
  events.jsonl
  summary_metrics.json
  external_runner/
    shim_config.json
    external_results.json
    external_results.sha256
    marker_validation.json
  raw/
runs/analysis/c5-i4-harness-overhead/
  verdict_table.json
  overhead_decomposition.csv
  marker_validity_waterfall.csv
```

`events.jsonl` must contain `harness_start`, `harness_end`, `item_start`, and
`item_end` events with C-015 metadata. Harness-specific metrics remain external
artifacts; JouleWise reports energy for marked windows only.

## Figure Skeletons

F-C5I4-OVERHEAD-FRACTION: overhead fraction vs item energy.

- x-axis: item or subset energy under named boundary.
- y-axis: harness overhead fraction.
- Caption uses capstone single-unit limitation language and full
  token-normalization stack identity fields. It states item energy is
  claim-bearing only when marker and floor gates pass.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

F-C5I4-MARKER-WATERFALL: marker-validity waterfall.

- x-axis: validation stage.
- y-axis: count of items or runs retained.
- Caption names paired markers, monotonic timestamps, measured-window
  inclusion, external results hash, strict validation, and reduction status.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

F-C5I4-VERDICT-TABLE: supported, partial, unsupported verdict table.

- Rows: harness/subset cells.
- Columns: verdict branch, limitation, allowed claim ceiling, and reason.
- Caption states unsupported markers produce feasibility evidence only and no
  energy comparison.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

## Gates

- P2-022 marker shim landing.
- `external_markers_supported` or relevant `partial(<limitation>)`.
- Strict bundle validation and reduction.
- Same/calibrated boundary for any L2 comparison.

## Refusals

- If markers are unsupported, record feasibility verdict and make no energy
  comparison.
- Do not join JouleWise energy to accuracy, pass@k, leaderboard standing, or
  capability interpretation.
- Do not claim item energy when harness overhead dominates unnoticed.

## Plug-In-Day Runbook

Existing commands:

```sh
python3 -m joulewise validate-config configs/campaign_packs/<<C5I4_CONFIG>>.json
python3 scripts/run_campaign.py configs/campaign_packs/<<C5I4_CONFIG_DIR>> --runs-dir runs --log runs/experiments/<<C5I4_EXPERIMENT_ID>>.jsonl --backup
python3 -m joulewise validate-bundle --strict runs/<<BASE_RUN_ID>>__r1
python3 -m joulewise reduce runs/<<BASE_RUN_ID>>__r1
python3 scripts/package_bundle_pack.py --output runs/bundle_packs/<<PACK_ID>> runs/<<BASE_RUN_ID_A>>__r1 runs/<<BASE_RUN_ID_B>>__r1
python3 scripts/package_bundle_pack.py --verify runs/bundle_packs/<<PACK_ID>>
```

PLANNED commands:

```sh
# PLANNED, owner: P2-022 marker-shim feasibility.
python3 -m joulewise external-marked-runner configs/campaign_packs/<<C5I4_CONFIG>>.json --runs-dir runs

# PLANNED, owner: harness-overhead reducer.
python3 -m joulewise harness-overhead-reduce runs/bundle_packs/<<PACK_ID>> --output runs/analysis/c5-i4-harness-overhead
```

Operator sequence:

0. Acquire the no-agent quiet-machine lock (`[QUIET-MAC]`): stop all
   agent/Codex load for the whole measurement session and confirm machine-idle
   state before the first idle baseline.
1. Run or import the P2-022 marker-shim verdict. If unsupported, freeze only a
   feasibility AP branch and stop before energy comparison.
2. Freeze AP row, verdict branch, marker-validation requirements, order
   manifest, external results hash requirement, and boundary label.
3. Execute marked harness runs only when supported or eligible partial verdict
   applies.
4. Strict-validate, reduce, package, and verify bundles.
5. Decompose overhead only for marker-valid runs and report unsupported or
   partial limitations in the verdict table.

Closing cooldown-gate note: the D-014 cooldown gate between repetitions is
runner-automated, but cooldown cap-hit flags must be checked in each member
bundle's measurement quality before analysis.
