# C5-3.1/C5-3.5 Pack: Second-Unit And Cross-Lab Replication

Status: pre-hardware and pre-coordination DRAFT. C5-3.1 waits on an actual
second M-series unit. C5-3.5 waits on external-lab coordination and starts
with the smallest suite that proves method transfer, following the P2-027
bundle-pack pattern. The high-value promoted bundle is iteration two.

## Pinned Now

- Two DRAFT AP rows: second-unit variance/generalizability floor and cross-lab
  replication.
- Frozen source campaign bundle/config list and artifact-transfer manifest.
- Replication acceptance matrix: same stack where possible, named deviations
  otherwise.
- Bundle hashes, environment capture, and stack-identity table.
- Local quiet-machine rule for second-unit runs and external-lab preflight.

## DRAFT AP Row: C5-3.1

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-C5-3.1 / C5-3.1 machine-to-machine variance and generalizability floor. DRAFT until registry freeze. |
| family_id | FAM-C5-31-SECOND-UNIT-VARIANCE |
| claim_role | primary |
| selection_scope | Frozen source campaign bundle/config list `<<C531.SOURCE_BUNDLE_PACK>>`, two M-series physical units `<<C531.UNIT_A>>` and `<<C531.UNIT_B>>`, matched model/runtime/artifact/quant/tokenizer/sampler/output policy where possible, same boundary label, and the smallest workload subset that covers the promoted source claim. Countable contrasts are unit-to-unit deltas for each frozen workload x metric x boundary cell. |
| multiplicity_rule | Holm within FAM-C5-31-SECOND-UNIT-VARIANCE across predeclared unit-to-unit variance contrasts and source-claim replication checks. Any added workload, model, unit, or metric after seeing results is exploratory. |
| Metric + exact window class | Request energy `gross_energy_j` and `energy_request_j` on gross and idle-subtracted request windows; optional phase descriptors only where matching floor rows exist. |
| Unit of analysis + dependence structure | Bundle repetition within unit x workload cell, blocked by physical unit and session. Replication verdicts compare cell-level estimates, not individual telemetry samples. |
| Estimator/formula | Estimate unit delta `delta_unit = metric(unit_b) - metric(unit_a)` and variance relative to the active P2-015 floor. Source-claim replication has exactly three outcomes: `replicated` (the original direction/verdict survives on the second unit under the frozen contrast rule), `contradicted` (the second-unit contrast is resolvable and reverses the original verdict), and `inconclusive` (the second-unit contrast is below floor or otherwise `not resolvable`). `inconclusive` is never reported as successful replication. A `practically equivalent` verdict is available only via a predeclared equivalence margin and equivalence test frozen in the registry before execution. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid bundles only. Include only cells with stack-identity tables, physical unit identity, same or explicitly named runtime/model deviations, boundary label, environment capture, and source bundle hashes. Waivers must be named before registry freeze. |
| Order/blocking/covariates | Repeat the frozen source campaign order where feasible, with start/end sentinels bracketing each hardware session. Record unit, session, order position, thermal/cooldown flags, and any unavoidable stack deviation. |
| Floor gate | pending-P2-015: consume matching request rows `DF-RQ-GROSS-MID`, `DF-RQ-IDLE-MID`, `DF-RQ-GROSS-LONG-PROMPT`, `DF-RQ-IDLE-LONG-PROMPT`, `DF-RQ-GROSS-LONG-DECODE`, `DF-RQ-IDLE-LONG-DECODE`, and `DF-CMP-ABBA-RQ`; consume `DF-PH-PREFILL`, `DF-PH-DECODE`, and `DF-CMP-ABBA-PH` only for eligible phase descriptors. Missing matching floor rows cap claims at L1/descriptive. |
| MDE/n sizing + predeclared top-up rule | Preserve the source campaign n or n>=5 per replication cell, whichever is larger. Sizing authority: D-062 + `configs/analysis_registry/<<C531_ANALYSIS_REGISTRY>>.json` (frozen n; no outcome-based top-ups without demotion). |
| Denominator provenance requirement | Runtime-observed output tokens, stop reason, model artifact hash, quantization, tokenizer identity, sampler/output policy, physical unit ID, OS/version, runtime/library, boundary label, telemetry backend, environment capture, source bundle hash, and replicated config hash. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L4 enabler`. Forbidden upgrade: `no population claim from one unit`. |
| Disqualifiers + not-resolvable conditions | No second physical unit, model/runtime/artifact drift hidden instead of named, boundary mismatch without calibration, missing source bundle hash, missing P2-015 floor row, failed strict validation, or single-unit evidence used for population wording. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## DRAFT AP Row: C5-3.5

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-C5-3.5 / C5-3.5 cross-lab replication. DRAFT until registry freeze and lab preflight. |
| family_id | FAM-C5-35-CROSS-LAB-REPLICATION |
| claim_role | secondary |
| selection_scope | Smallest frozen suite that proves method transfer: source bundle/config pack `<<C535.SOURCE_BUNDLE_PACK>>`, exported configs, reduction scripts, expected environment capture, and external-lab target stack `<<C535.EXTERNAL_LAB_STACK>>`. Countable contrasts are original-vs-external-lab agreement checks for each frozen metric x workload x boundary cell in that smallest suite. |
| multiplicity_rule | Holm within FAM-C5-35-CROSS-LAB-REPLICATION across predeclared cross-lab agreement checks. Broader promoted-bundle replication is iteration two and remains exploratory until separately frozen. |
| Metric + exact window class | Boundary-labeled request energy and validation/reduction agreement on gross or idle-subtracted request windows; optional method-transfer feasibility metrics include strict validation pass/fail, reducer reproducibility, and artifact completeness. |
| Unit of analysis + dependence structure | Bundle repetition and lab-level replication cell. Original and external-lab bundles are independent lab executions but share frozen configs and reduction scripts. |
| Estimator/formula | Agreement check compares external-lab estimate to original estimate under the frozen tolerance: direction/verdict agreement plus absolute delta relative to active floor/MDE. Method-transfer success also requires strict validation and reproducible reduction from transferred artifacts. |
| Inclusion/exclusion + quality-flag waiver rules | Include only transferred configs, source manifests, bundle-pack hashes, environment captures, strict-valid external-lab bundles, and named stack deviations. External lab cannot silently change model, quant, tokenizer, sampler/output policy, boundary, or reduction script. |
| Order/blocking/covariates | External lab follows transferred order manifest where feasible; any forced order change is recorded before execution and analyzed as a named deviation. Local preflight and external preflight both record environment and tool versions. |
| Floor gate | pending-P2-015: consume the same floor rows as the source campaign for matching request or phase windows, including `DF-RQ-GROSS-MID`, `DF-RQ-IDLE-MID`, `DF-CMP-ABBA-RQ`, `DF-PH-PREFILL`, `DF-PH-DECODE`, and `DF-CMP-ABBA-PH` where applicable. Missing matching floor rows cap claims at L1/method-transfer evidence. |
| MDE/n sizing + predeclared top-up rule | Preserve the smallest first cross-lab suite with n matching the transferred bundle pattern. Sizing authority: D-062 + `configs/analysis_registry/<<C535_ANALYSIS_REGISTRY>>.json` (frozen n; no outcome-based top-ups without demotion). |
| Denominator provenance requirement | Transferred config hash, source bundle-pack hash, external-lab bundle hashes, runtime-observed token denominators, stop reasons, stack-identity table, lab identity, environment capture, reduction script hash, and boundary label. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L4 enabler`. Forbidden upgrade: `no public benchmark credibility claim without replication`. |
| Disqualifiers + not-resolvable conditions | No external-lab agreement, unrecorded stack deviation, changed reduction script, missing transferred bundle hash, failed strict validation, missing floor row, or attempt to promote public benchmark credibility from local-only data. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## Manifest/Config Templates

The transfer manifest mirrors the P2-027 bundle-pack pattern: exact configs,
source bundle hashes, expected outputs, and allowed-deviation fields travel as
one unit.

```json
{
  "schema_version": "0.1",
  "replication_pack_id": "c5-3-replication-<<SOURCE_PACK_ID>>",
  "source": {
    "bundle_pack": "<<C531_OR_C535.SOURCE_BUNDLE_PACK>>",
    "bundle_pack_sha256": "<<C531_OR_C535.SOURCE_BUNDLE_PACK_SHA256>>",
    "configs_sha256": "<<C531_OR_C535.CONFIGS_SHA256>>",
    "reduction_script_sha256": "<<C531_OR_C535.REDUCTION_SCRIPT_SHA256>>"
  },
  "replication_target": {
    "mode": "<<C531_SECOND_UNIT_OR_C535_EXTERNAL_LAB>>",
    "lab_or_unit_id": "<<C531_OR_C535.TARGET_ID>>",
    "required_same_fields": [
      "model_artifact_hash",
      "quantization",
      "tokenizer_identity",
      "sampler_output_policy",
      "boundary_label",
      "reduction_script"
    ],
    "allowed_deviations": [
      {
        "field": "<<C531_OR_C535.DEVIATION_FIELD_OR_NONE>>",
        "reason": "<<C531_OR_C535.DEVIATION_REASON>>",
        "claim_effect": "downgrade_or_named_sensitivity"
      }
    ]
  },
  "acceptance_matrix": {
    "strict_validation_required": true,
    "reduction_reproducibility_required": true,
    "agreement_rule": "<<FROZEN_BEFORE_EXECUTION>>"
  }
}
```

## Expected Artifacts

```text
runs/replication_packs/<replication_pack_id>/
  source_manifest.json
  transferred_configs/
  bundle_hashes.txt
  reduction_script_hashes.txt
  acceptance_matrix.json
  allowed_deviations.json
runs/<replication_run_id>__rN/
  config.json
  metadata.json
  events.jsonl
  summary_metrics.json
  raw/
runs/analysis/c5-3-replication/
  original_vs_replica.csv
  variance_floor_table.csv
  cross_lab_agreement.json
  stack_identity_table.csv
```

The stack-identity table must name concrete values or `unknown` for every
required field in `docs/contracts/token_normalization.md`.

## Figure Skeletons

F-C531-UNIT-DELTAS: original vs second-unit deltas.

- x-axis: original unit estimate.
- y-axis: second-unit estimate or delta.
- Caption uses capstone single-unit limitation language and states whether the
  result is still an L4 enabler rather than a population claim.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

F-C531-VARIANCE-FLOOR: variance relative to floor.

- x-axis: workload/metric cell.
- y-axis: unit-to-unit variance or delta divided by active floor.
- Caption names P2-015 floor rows and reports `not resolvable` where the floor
  absorbs the contrast.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

F-C535-CROSS-LAB-AGREEMENT: cross-lab agreement table.

- Rows: frozen smallest-suite cells.
- Columns: original verdict, external-lab verdict, allowed deviations, and
  agreement status.
- Caption includes full stack identity, transferred bundle hashes, and
  boundary labels.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

## Gates

- C5-3.1: actual second M-series unit.
- C5-3.5: external-lab coordination and preflight.
- P2-015 floor rows matching the source campaign metrics/windows.
- L4/general-population wording only after replication evidence; these packs
  are enablers, not standalone population proof.

## Refusals

- Do not make a population claim from one unit.
- Do not make a public benchmark credibility claim without replication.
- Do not silently accept stack drift; name deviations and downgrade when they
  affect the claim.

## Plug-In-Day Runbook

### External-Lab Cold-Start Preflight

Before execution, the external lab must start from a pinned source artifact and
return enough provenance to prove that the same contract was run.

Required artifact and install checks:

```sh
tar -xf <<JOULEWISE_SOURCE_ARTIFACT>> -C <<EXTERNAL_LAB_WORKDIR>>
cd <<EXTERNAL_LAB_WORKDIR>>/<<JOULEWISE_SOURCE_DIR>>
python3 -m pip install -e .
python3 -m joulewise --help
python3 scripts/package_bundle_pack.py --verify runs/bundle_packs/<<SOURCE_PACK_ID>>
```

Required config transfer and validation checks:

```sh
mkdir -p configs/campaign_packs/replication_transferred
cp <<TRANSFERRED_CONFIG_DIR>>/*.json configs/campaign_packs/replication_transferred/
for cfg in configs/campaign_packs/replication_transferred/*.json; do
  python3 -m joulewise validate-config "$cfg"
done
python3 scripts/run_campaign.py configs/campaign_packs/replication_transferred --runs-dir runs --log runs/experiments/<<REPLICATION_EXPERIMENT_ID>>.jsonl --dry-run
```

Environment and telemetry checks before the first real run:

- Record source artifact path, source artifact SHA-256, git commit if present,
  install command output, `python3 -m joulewise --help` output, Python version,
  OS/version, hardware unit identity, runtime/backend versions, and telemetry
  backend/version or command semantics.
- Confirm telemetry backend availability, power-trace write permission, clock
  state, quiet-machine lock, idle baseline readiness, and bundle output path.
- Return the transferred config directory hash, per-config SHA-256 values,
  `validate-config` outputs, dry-run plan output, source bundle-pack verify
  output, environment capture, telemetry check evidence, and any deviations
  from the frozen acceptance matrix.

Existing commands:

```sh
python3 scripts/package_bundle_pack.py --verify runs/bundle_packs/<<SOURCE_PACK_ID>>
python3 scripts/run_campaign.py configs/campaign_packs/<<REPLICATION_CONFIG_DIR>> --runs-dir runs --log runs/experiments/<<REPLICATION_EXPERIMENT_ID>>.jsonl --backup
python3 -m joulewise validate-bundle --strict runs/<<REPLICATION_RUN_ID>>__r1
python3 -m joulewise reduce runs/<<REPLICATION_RUN_ID>>__r1
python3 scripts/package_bundle_pack.py --output runs/bundle_packs/<<REPLICATION_PACK_ID>> runs/<<REPLICATION_RUN_ID_A>>__r1 runs/<<REPLICATION_RUN_ID_B>>__r1
python3 scripts/package_bundle_pack.py --verify runs/bundle_packs/<<REPLICATION_PACK_ID>>
```

PLANNED commands:

```sh
# PLANNED, owner: replication-pack reducer.
python3 -m joulewise replication-compare runs/replication_packs/<<REPLICATION_PACK_ID>> runs/bundle_packs/<<REPLICATION_OUTPUT_PACK_ID>> --output runs/analysis/c5-3-replication
```

Operator sequence:

0. For local second-unit runs, acquire the no-agent quiet-machine lock
   (`[QUIET-MAC]`) and confirm machine-idle state before the first idle
   baseline. For external-lab runs, complete preflight for environment,
   artifact transfer, and expected validation commands before execution.
1. Select the frozen source bundle/config list. For C5-3.5, choose the
   smallest suite that proves method transfer.
2. Freeze AP rows, acceptance matrix, allowed deviations, source bundle hashes,
   and order manifest.
3. Execute local second-unit or external-lab replication without changing
   configs except for named target/environment fields.
4. Strict-validate, reduce, package, verify, and compare against the frozen
   acceptance matrix.

Closing cooldown-gate note: the D-014 cooldown gate between repetitions is
runner-automated, but cooldown cap-hit flags must be checked in each member
bundle's measurement quality before analysis.
