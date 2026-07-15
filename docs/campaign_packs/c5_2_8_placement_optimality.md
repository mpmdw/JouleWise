# C5-2.8 Pack: Placement-Policy Optimality From Q4 Coefficients

Status: pre-hardware DRAFT and derived-analysis DRAFT. This pack operates over
prior campaign outputs plus held-out split validation runs. It cannot freeze
predictions until AP-1/Q4 coefficients and measured transfer terms exist.

## Pinned Now

- Finite placement candidate set: prefill device, decode device, link,
  boundary label, model, runtime family, prompt shape, and decode shape.
- Formula uses AP-1/Q4 fixed, prompt, and decode coefficients plus measured
  serialize, transfer, and deserialize terms.
- Prediction-freeze artifact must exist before validation cells run.
- Validation matrix reports measured split cells, regret versus measured best,
  and predicted-optimum success or failure.
- If Q4 holdouts fail, downgrade to exploratory placement accounting.

## DRAFT AP Row

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-C5-2.8 / C5-2.8 placement-policy optimality from Q4 coefficients. DRAFT until registry freeze. |
| family_id | FAM-C5-28-PLACEMENT-OPTIMALITY |
| claim_role | primary |
| selection_scope | Frozen placement candidate set over `<<PHASE3.DEVICE_PAIR_SET>>`, prefill device choices, decode device choices, links `<<PHASE3.LINK_SET>>`, boundary labels, one model/runtime family, prompt lengths `<<AP-1.PROMPT_LEVELS_OR_SUBSET>>`, decode lengths `<<AP-1.DECODE_LEVELS_OR_SUBSET>>`, and validation cells `<<PHASE3.MEASURED_SPLIT_VALIDATION_CELLS>>`. Countable contrasts are predicted optimum versus measured best and regret for each frozen placement x workload cell. |
| multiplicity_rule | Holm within FAM-C5-28-PLACEMENT-OPTIMALITY across predeclared predicted-optimum success/failure and regret contrasts for frozen validation cells. Any searched placement, link, workload, or model outside the prediction-freeze manifest is exploratory. |
| Metric + exact window class | Primary: predicted and measured composite split request energy `split_total_energy_j` on composite request windows. Components: AP-1 request coefficients, serialize phase, transfer window, deserialize/cache-load phase, prefill phase, and decode phase. |
| Unit of analysis + dependence structure | Prediction cell and measured composite bundle repetition. Stage components inside a composite split bundle are dependent; validation evidence is at bundle or block level, not item-window level. |
| Estimator/formula | `predicted_split_total_j = AP-1 fixed/prompt/decode terms for prefill and decode placements + measured_serialize_j + measured_transfer_j + measured_deserialize_j + idle_floor_terms_j`. Predicted optimum is the minimum predicted placement in the frozen candidate set. Regret is `measured_energy(predicted_optimum) - measured_energy(measured_best)`. Success requires predicted optimum to match measured best or have regret <= active floor/MDE threshold. |
| Inclusion/exclusion + quality-flag waiver rules | Include only strict-valid source bundles, Q4 coefficient artifact, transfer payload manifests, measured split validation bundles, stack-identity tables, and prediction-freeze artifact with timestamp/hash before validation execution. D-014 quality waivers must be named before registry freeze. |
| Order/blocking/covariates | Validation cells run in counterbalanced placement/link/workload order with start/end sentinels. Include session, device pair, link position, and block covariates only if frozen before validation. |
| Floor gate | pending-P2-015: AP-1 request coefficients consume matching request rows such as `DF-RQ-GROSS-MID`, `DF-RQ-IDLE-MID`, `DF-RQ-GROSS-LONG-PROMPT`, `DF-RQ-IDLE-LONG-PROMPT`, `DF-RQ-GROSS-LONG-DECODE`, `DF-RQ-IDLE-LONG-DECODE`, and `DF-CMP-ABBA-RQ`. Prefill/decode descriptors consume `DF-PH-PREFILL`, `DF-PH-DECODE`, and `DF-CMP-ABBA-PH`. Composite split-total, serialize, transfer, and deserialize claims are capped until P2-015 adds matching rows, a composite row, or the frozen AP names an accepted AP-specific bound. |
| MDE/n sizing + predeclared top-up rule | Preserve n>=5 measured validation repetitions for headline placement cells and n>=3 for non-headline cells. Sizing authority: D-062 + `configs/analysis_registry/<<C528_ANALYSIS_REGISTRY>>.json` (frozen n; no outcome-based top-ups without demotion). |
| Denominator provenance requirement | Q4 coefficient artifact hash, AP-1 holdout verdict, runtime-observed output tokens, stop reason, model artifact hash, quantization, tokenizer identity, sampler/output policy, serialized payload bytes, payload SHA-256, link throughput, serialize/transfer/deserialize markers, and measured split validation bundle hashes. |
| Holdout cells (L3 only) | Frozen validation cells `<<PHASE3.MEASURED_SPLIT_VALIDATION_CELLS>>`; prediction-freeze hash must predate those validation bundles. Prediction error and regret must clear the AP-specific success rule. |
| Claim ceiling + exact forbidden upgrade | `L2/L3`. Forbidden upgrade: `no optimal-placement claim without measured split validation cells`. |
| Disqualifiers + not-resolvable conditions | Missing AP-1/Q4 coefficients, failed Q4 holdouts, no prediction-freeze artifact before validation, missing measured split validation cells, missing transfer/deserialize terms, floor row missing for the claim window, non-equivalent output policy, or placement searched after seeing validation results. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## Manifest/Config Templates

This pack consumes prior artifacts and plans held-out validation. The
`<<AP-1.*>>` placeholders are gated by AP-1/Q4, and `<<PHASE3.*>>`
placeholders are gated by Phase 3/P2-032-style split and KV artifacts.

```json
{
  "schema_version": "0.2",
  "analysis_kind": "placement_prediction_freeze",
  "analysis_id": "c5-2-8-placement-freeze-<<AP-1.COEFFICIENT_ARTIFACT_HASH_SHORT>>",
  "inputs": {
    "q4_coefficients": "<<AP-1.COEFFICIENT_ARTIFACT_PATH>>",
    "q4_holdout_verdict": "<<AP-1.HOLDOUT_VERDICT_PATH>>",
    "transfer_terms": "<<PHASE3.TRANSFER_TERMS_PATH>>",
    "deserialize_terms": "<<PHASE3.DESERIALIZE_TERMS_PATH>>",
    "candidate_manifest": "<<PHASE3.PLACEMENT_CANDIDATE_MANIFEST>>"
  },
  "candidate_set": {
    "model_family": "<<PHASE3.MODEL_FAMILY>>",
    "runtime_family": "<<PHASE3.RUNTIME_FAMILY>>",
    "placements": [
      {
        "placement_id": "<<PHASE3.PLACEMENT_ID>>",
        "prefill_target": "<<PHASE3.PREFILL_TARGET_ID>>",
        "decode_target": "<<PHASE3.DECODE_TARGET_ID>>",
        "link_label": "<<PHASE3.LINK_LABEL>>",
        "boundary_label": "<<PHASE3.BOUNDARY_LABEL>>"
      }
    ],
    "workloads": [
      {
        "prompt_tokens": 2048,
        "decode_tokens": 256
      }
    ]
  },
  "freeze_outputs": {
    "prediction_table": "runs/analysis/c5-2-8/prediction_freeze.csv",
    "prediction_hash": "<<FILLED_AFTER_FREEZE>>"
  }
}
```

Measured validation reuses the split-suite `split_offline` template from
`docs/campaign_packs/split_suite_q1_q2_q3.md`, with validation cells limited
to the frozen `prediction_freeze.csv`.

## Expected Artifacts

```text
runs/analysis/c5-2-8/
  candidate_manifest.json
  prediction_freeze.csv
  prediction_freeze.sha256
  source_artifacts_manifest.json
  validation_matrix.json
  regret_table.csv
runs/<validation_base_run_id>__rN/
  config.json
  metadata.json
  events.jsonl
  transfer/payload_manifest.json
  summary_metrics.json
  nodes/prefill/
  nodes/decode/
```

`source_artifacts_manifest.json` records Q4 coefficient hash, holdout verdict,
transfer/deserialization artifact hashes, split-suite bundle hashes, and the
freeze timestamp. `validation_matrix.json` records predicted optimum,
measured best, regret, floor/MDE threshold, and success/failure verdict.

## Figure Skeletons

F-C528-PREDICTED-MEASURED: predicted vs measured placement energy.

- x-axis: predicted composite split request energy.
- y-axis: measured composite split request energy.
- Caption uses capstone single-unit limitation language and full
  token-normalization stack identity fields; it states that placement winners
  are validation-cell claims, not generic optimal placement.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

F-C528-REGRET: regret by validation cell.

- x-axis: frozen validation workload and placement candidate.
- y-axis: regret in joules versus measured best.
- Caption names the active floor/MDE threshold and marks below-threshold
  regret as unresolved, not as proof of equality.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

F-C528-OPTIMAL-MAP: optimal-placement map.

- x-axis: prompt length.
- y-axis: link/device-pair cell.
- Fill: predicted optimum and measured-best agreement status.
- Caption states whether Q4 holdouts cleared; if not, this is exploratory
  placement accounting.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

## Gates

- AP-1/Q4 coefficients from Window B.
- Transfer, serialize, and deserialize terms from Phase 3/P2-032-style
  split/KV artifacts.
- Measured split validation cells.
- Registry forbids optimal-placement claims without measured validation cells.

## Refusals

- Do not call a coefficient-derived winner `optimal` before measured split
  validation cells.
- Do not freeze predictions after validation cells run.
- Do not promote this pack beyond exploratory placement accounting if Q4
  holdouts fail.

## Plug-In-Day Runbook

Existing commands:

```sh
python3 scripts/package_bundle_pack.py --verify runs/bundle_packs/<<SOURCE_PACK_ID>>
python3 -m joulewise validate-config configs/campaign_packs/<<C528_VALIDATION_CONFIG>>.json
python3 scripts/run_campaign.py configs/campaign_packs/<<C528_VALIDATION_CONFIG_DIR>> --runs-dir runs --log runs/experiments/<<C528_VALIDATION_EXPERIMENT_ID>>.jsonl --backup
python3 -m joulewise validate-bundle --strict runs/<<VALIDATION_BASE_RUN_ID>>__r1
python3 -m joulewise reduce runs/<<VALIDATION_BASE_RUN_ID>>__r1
python3 scripts/package_bundle_pack.py --output runs/bundle_packs/<<C528_VALIDATION_PACK_ID>> runs/<<VALIDATION_BASE_RUN_ID_A>>__r1 runs/<<VALIDATION_BASE_RUN_ID_B>>__r1
python3 scripts/package_bundle_pack.py --verify runs/bundle_packs/<<C528_VALIDATION_PACK_ID>>
```

PLANNED commands:

```sh
# PLANNED, owner: C5-2.8 derived analysis after AP-1 and Phase 3 artifacts exist.
python3 -m joulewise placement-freeze configs/campaign_packs/<<C528_ANALYSIS_CONFIG>>.json --output runs/analysis/c5-2-8

# PLANNED, owner: C5-2.8 validation reducer.
python3 -m joulewise placement-validate runs/analysis/c5-2-8/prediction_freeze.csv runs/bundle_packs/<<C528_VALIDATION_PACK_ID>> --output runs/analysis/c5-2-8/validation_matrix.json
```

Operator sequence:

0. Acquire the no-agent quiet-machine lock (`[QUIET-MAC]`) before any held-out
   validation run and confirm machine-idle state before the first idle
   baseline.
1. Verify AP-1/Q4 coefficients and holdout verdict. If holdouts fail, freeze
   only exploratory placement-accounting language.
2. Assemble candidate manifest from Phase 3 transfer/KV/split artifacts and
   write `prediction_freeze.csv` before validation cells run.
3. Freeze AP row, contrast IDs, validation cells, and source artifact hashes.
4. Execute only the frozen validation cells.
5. Strict-validate, reduce, package, and verify validation bundles, then
   compute regret and success/failure verdicts.

Closing cooldown-gate note: the D-014 cooldown gate between repetitions is
runner-automated, but cooldown cap-hit flags must be checked in each member
bundle's measurement quality before analysis.
