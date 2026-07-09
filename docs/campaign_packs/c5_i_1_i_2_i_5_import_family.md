# C5-I.1/C5-I.2/C5-I.5 Pack: Benchmark Import Family

Status: pre-substrate DRAFT. First executable milestone is HumanEval L0-L1
only. The manifest reserves a second-family placeholder to show discipline
generalizes, but this pack names no second source. MMLU and tinyBenchmarks
remain rejected as first import targets per C-015, and FLORES stays separate
in `c5_i_3_flores_fertility.md`.

## Pinned Now

- Three AP rows for family energy signatures, published-difficulty association,
  and prompt-template energy sensitivity.
- `benchmark_import` source-manifest discipline: license, archive hash, frozen
  subset, never latest split.
- HumanEval-first plumbing with no pass@k, accuracy, coding capability,
  leaderboard join, or benchmark-score normalization.
- Matched shape/output policy and source/license manifests.
- Difficulty metadata quarantine for C5-I.2.
- Prompt-template pair design for C5-I.5: same source item, canonical versus
  JouleWise-rendered prompt, template hash, rendered prompt hash, and
  BOS/template-token policy.

## DRAFT AP Row: C5-I.1

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-C5-I.1 / C5-I.1 external benchmark energy signatures. DRAFT until registry freeze. |
| family_id | FAM-C5I1-IMPORT-ENERGY-SIGNATURES |
| claim_role | primary |
| selection_scope | Frozen HumanEval import subset `<<P2-023.HUMANEVAL_SUBSET_ID>>`, reserved unnamed second-family placeholder `<<LATER_SOURCE_SESSION.SECOND_FAMILY_PLACEHOLDER>>` with no executable source, model/runtime/artifact/quant/tokenizer/sampler/output policy, matched shape set `{256,512}` completion caps or narrower frozen subset, source family labels, and request/item/level windows. Countable contrasts are family-level energy signatures for frozen families and shapes only. |
| multiplicity_rule | Holm within FAM-C5I1-IMPORT-ENERGY-SIGNATURES across predeclared family x shape energy-signature contrasts. The reserved second-family placeholder generates no claim-bearing contrasts in this pack. Any added source, latest split, live dataset fetch, or post-hoc family subset is exploratory with no-confirmatory-inference. |
| Metric + exact window class | Primary: request or level-window energy for imported-suite blocks; item-window descriptors only when P2-015 item floors clear. Companions: runtime-observed output tokens, stop reasons, J/output-token within tokenizer scope, and source-manifest denominators. |
| Unit of analysis + dependence structure | Bundle or block-level uncertainty over imported-suite items. Item windows are not independent replicates unless a repeated-bundle/block design is frozen. |
| Estimator/formula | Family energy signature is the frozen family mean or contrast after matching shape and output policy. Report item distributions descriptively; L2 family contrasts require repeated strict-valid bundles and active floor clearance. |
| Inclusion/exclusion + quality-flag waiver rules | Include only frozen source-manifest items with license, archive hash, source row hash, frozen subset ID, contamination/quarantine fields, prompt/render hash, matched output policy, and strict-valid bundles. Waivers must be named before registry freeze. |
| Order/blocking/covariates | Interleave imported items by source family and shape using suite manifest order policy. Record block, item index, source family, shape, prompt template, and cooldown/session covariates. |
| Floor gate | pending-P2-015: consume `DF-ITEM` or matching item-window rows for item descriptors when available, `DF-LEVEL` or matching level-window rows for suite/block energy when available, and request rows such as `DF-RQ-GROSS-MID`, `DF-RQ-IDLE-MID`, and `DF-CMP-ABBA-RQ` for request-shaped imports. Missing item/level floor rows cap claims at L1/descriptive. |
| MDE/n sizing + predeclared top-up rule | HumanEval smoke may remain L0-L1 with n dictated by plumbing. L2 family energy signatures require n>=5 repeated bundles or an accepted repeated-block design; top up before L2 wording when family contrast CI crosses the active floor gate or source-family verdict changes under leave-one-out. |
| Denominator provenance requirement | Source manifest hash, license, archive hash, frozen subset ID, source row SHA-256, prompt/render hash, runtime-observed emitted tokens, stop reason, tokenizer identity, prompt source, BOS handling, output policy, model artifact hash, and contamination/quarantine fields. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L2`. Forbidden upgrade: `no benchmark capability or accuracy claim`. |
| Disqualifiers + not-resolvable conditions | Live/latest split, missing source license/hash, missing source row hash, unmatched shape/output policy, no P2-023 HumanEval plumbing, no active item/level floor for L2, or any attempt to infer accuracy, pass@k, coding capability, leaderboard standing, or benchmark score. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## DRAFT AP Row: C5-I.2

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-C5-I.2 / C5-I.2 published-difficulty strata versus energy. DRAFT until registry freeze. |
| family_id | FAM-C5I2-DIFFICULTY-ASSOCIATION |
| claim_role | secondary |
| selection_scope | Frozen HumanEval imported subset with quarantined difficulty metadata fields, optional later second-family placeholder with no source named, matched shape/output policy, and predeclared strata `<<P2-023.DIFFICULTY_STRATA_OR_NONE>>`. Countable contrasts are descriptive association summaries across frozen source-provided strata only. |
| multiplicity_rule | Holm within FAM-C5I2-DIFFICULTY-ASSOCIATION for predeclared repeated-bundle L2 stratum contrasts when such bundles exist; otherwise exploratory/no-confirmatory-inference for L1 association summaries. BH item-level sweeps at q=0.10 are limited to metadata/correctness summaries and cannot carry item-energy inference. |
| Metric + exact window class | Energy on request, item, or level windows as supported by the import run; stop-reason and token distributions are companions. Difficulty labels are source metadata, not causal treatments. |
| Unit of analysis + dependence structure | Bundle or block-level uncertainty by difficulty stratum. Individual items are metadata observations, not independent energy replicates unless repeated bundles are frozen. |
| Estimator/formula | Descriptive association between source-provided difficulty stratum and bundle/block energy, controlling for matched shape and output policy when frozen. No causal estimator is allowed. |
| Inclusion/exclusion + quality-flag waiver rules | Include only imported items with quarantined difficulty source, difficulty label or explicit `none/source_not_provided`, source hash, prompt/render hash, and strict-valid bundle evidence. Heterogeneous difficulty taxonomies must remain named and cannot be merged silently. |
| Order/blocking/covariates | Interleave strata within shape where feasible; record source family, stratum, item index, prompt template, block, and session covariates. |
| Floor gate | pending-P2-015: consume matching item, level, or request rows such as `DF-ITEM`, `DF-LEVEL`, `DF-RQ-GROSS-MID`, `DF-RQ-IDLE-MID`, and `DF-CMP-ABBA-RQ` when present. Missing matching floor rows or absent repeated bundles cap C5-I.2 at L1 association. |
| MDE/n sizing + predeclared top-up rule | L1 summaries may use HumanEval smoke evidence. Any L2 stratum contrast requires preplanned repeated bundles with n>=5 per stratum/block or an accepted repeated-block design; top up to n=10 when stratum CI crosses the floor or association direction changes under leave-one-out. |
| Denominator provenance requirement | Source difficulty label, difficulty source, source row hash, frozen subset ID, prompt/render hash, runtime-observed tokens, stop reason, tokenizer identity, output policy, and quarantine metadata. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L1 association; L2 only if preplanned repeated bundles`. Forbidden upgrade: `no difficulty causes energy`. |
| Disqualifiers + not-resolvable conditions | Heterogeneous labels merged into causal difficulty language, no repeated-bundle design for L2, missing source difficulty provenance, shape/output mismatch, item windows treated as independent replicates, or benchmark-score normalization. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## DRAFT AP Row: C5-I.5

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-C5-I.5 / C5-I.5 prompt-template energy sensitivity. DRAFT until registry freeze. |
| family_id | FAM-C5I5-PROMPT-TEMPLATE-PAIRS |
| claim_role | primary |
| selection_scope | Frozen HumanEval source items `<<P2-023.HUMANEVAL_SUBSET_ID>>`, paired canonical and JouleWise-rendered prompt templates for the same source item, template hashes, rendered prompt hashes, BOS/template-token policy, one model/runtime/artifact/quant/tokenizer/sampler/output policy, and completion caps `{256,512}` or narrower frozen subset. Countable contrasts are paired template deltas per frozen item x shape cell. |
| multiplicity_rule | Holm within FAM-C5I5-PROMPT-TEMPLATE-PAIRS across predeclared canonical-vs-JouleWise template paired deltas. Any additional template, prompt rewrite, source family, or post-hoc item subset is exploratory. |
| Metric + exact window class | Primary: paired request or item/level-window energy under matched output policy. Companions: runtime-observed emitted tokens, stop reasons, tokenizer-scoped J/output-token, and rendered prompt token counts. |
| Unit of analysis + dependence structure | Paired source item within bundle/block; canonical and JouleWise-rendered prompts are dependent paired observations for the same source item. Repeated bundles provide uncertainty. |
| Estimator/formula | Paired delta `delta_template_j = energy_joulewise_rendered - energy_canonical` within source item and shape. Aggregate with paired/block intervals; no prompt-quality or capability inference. |
| Inclusion/exclusion + quality-flag waiver rules | Include only source items with both prompt renderings, source row hash, template hash, rendered prompt hash, BOS/template-token policy, matched output policy, and strict-valid bundle evidence. Exclude pairs where either side fails validation or output policy diverges. |
| Order/blocking/covariates | Pair order is counterbalanced ABBA where feasible: canonical, rendered, rendered, canonical across blocks. Record item, pair position, template ID, block, session, and cooldown flags. |
| Floor gate | pending-P2-015: consume matching request/item/level floor rows including `DF-RQ-GROSS-MID`, `DF-RQ-IDLE-MID`, `DF-CMP-ABBA-RQ`, `DF-ITEM`, and `DF-LEVEL` when available. Missing matching item/level floor rows cap paired template energy claims at L1/descriptive. |
| MDE/n sizing + predeclared top-up rule | n>=5 paired repeated bundles for L2 template sensitivity. Top up to n=10 when paired CI crosses the active floor gate, when leave-one-out changes the direction, or when token/stop distributions diverge enough to require sensitivity wording. |
| Denominator provenance requirement | Source item ID, source row hash, canonical template hash, JouleWise template hash, rendered prompt hashes, BOS policy, prompt source, runtime-observed emitted tokens, stop reason, tokenizer identity, output policy, and bundle hashes. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L2`. Forbidden upgrade: `no prompt-quality or capability claim`. |
| Disqualifiers + not-resolvable conditions | Missing paired rendering, template hash drift, unmatched output policy, BOS/template-token policy not recorded, no repeated-bundle uncertainty for L2, below-floor paired delta, or prompt quality/capability interpretation. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## Manifest/Config Templates

`benchmark_import` manifests are source-provenance artifacts, not live dataset
fetch instructions. The first executable source is HumanEval under P2-023.
The second-family placeholder is reserved for a later source session and names
no benchmark here.

```json
{
  "schema_version": "0.1",
  "import_kind": "benchmark_import",
  "import_id": "humaneval-p2-023-<<P2-023.SUBSET_ID>>",
  "source": {
    "benchmark_name": "HumanEval",
    "benchmark_revision": "<<P2-023.HUMANEVAL_REVISION>>",
    "license": "MIT",
    "archive_sha256": "<<P2-023.ARCHIVE_SHA256>>",
    "frozen_subset_id": "<<P2-023.SUBSET_ID>>",
    "latest_split_allowed": false,
    "live_fetch_allowed": false
  },
  "quarantine": {
    "contamination_known": true,
    "scorer_allowed": false,
    "accuracy_claim_allowed": false,
    "pass_at_k_allowed": false
  },
  "rendering": {
    "canonical_template_id": "<<P2-023.CANONICAL_TEMPLATE_ID>>",
    "joulewise_template_id": "<<P2-023.JOULEWISE_TEMPLATE_ID>>",
    "template_sha256": "<<P2-023.TEMPLATE_SHA256>>",
    "bos_policy": "<<P2-023.BOS_POLICY>>",
    "completion_caps": [256, 512],
    "output_policy": "<<P2-023.OUTPUT_POLICY>>"
  },
  "items": [
    {
      "suite_item_id": "<<P2-023.SUITE_ITEM_ID>>",
      "source_item_id": "<<P2-023.SOURCE_ITEM_ID>>",
      "source_row_sha256": "<<P2-023.SOURCE_ROW_SHA256>>",
      "difficulty_label": "none/source_not_provided",
      "difficulty_source": "source_not_provided",
      "canonical_render_sha256": "<<P2-023.CANONICAL_RENDER_SHA256>>",
      "joulewise_render_sha256": "<<P2-023.JOULEWISE_RENDER_SHA256>>"
    }
  ],
  "reserved_second_family_placeholder": {
    "source_name": null,
    "status": "reserved_for_later_source_session",
    "claim_bearing": false
  }
}
```

Suite execution uses the existing itemized-suite substrate after P2-023 lands:

```json
{
  "schema_version": "0.1",
  "run_id": "c5-i-import-humaneval-<<P2-023.SUBSET_ID>>",
  "suite_manifest": "<<P2-023.SUITE_MANIFEST_PATH>>",
  "source_manifest": "<<P2-023.BENCHMARK_IMPORT_MANIFEST_PATH>>",
  "workload_profile": {
    "name": "humaneval_import_smoke",
    "suite_id": "<<P2-023.SUITE_ID>>",
    "repetitions": 5,
    "warmup_runs": 1
  },
  "run_metadata": {
    "project": "capstone-joulewise",
    "operator": "ed",
    "tags": ["c5-i.1", "c5-i.2", "c5-i.5", "benchmark-import", "humaneval"]
  }
}
```

## Expected Artifacts

```text
runs/import_manifests/
  humaneval-p2-023-<subset>.json
runs/<base_run_id>__rN/
  config.json
  metadata.json
  events.jsonl
  summary_metrics.json
  outputs/
    suite_items.jsonl
    item_outputs.jsonl
  source/
    benchmark_import_manifest.json
runs/analysis/c5-i-import-family/
  family_energy_signatures.csv
  difficulty_association_quarantine.csv
  prompt_template_pairs.csv
  source_manifest_hashes.json
```

`outputs/suite_items.jsonl` must retain prompt source, BOS handling, rendered
prompt hash, runtime-observed token counts, stop reason, and source item ID.
Difficulty metadata remains quarantined and named by source.

## Figure Skeletons

F-C5I1-FAMILY-SIGNATURES: imported-family energy signatures.

- x-axis: matched shape/output-policy cell.
- y-axis: request or level-window energy.
- Caption uses capstone single-unit limitation language and full
  token-normalization stack identity fields. It states HumanEval is a plumbing
  smoke unless repeated strict-valid bundles support a later L2 contrast.

F-C5I2-DIFFICULTY-ASSOCIATION: difficulty-stratum descriptive association.

- x-axis: source-provided difficulty stratum or `none/source_not_provided`.
- y-axis: energy or stop/token distribution summary.
- Caption states that labels are heterogeneous source metadata and do not
  support `difficulty causes energy`.

F-C5I5-PROMPT-PAIRS: prompt-template paired deltas.

- x-axis: source item or pair block.
- y-axis: canonical-vs-JouleWise rendered energy delta.
- Caption names template hashes, rendered prompt hashes, BOS policy, tokenizer
  identity, request energy, and any tokenizer-scoped companion metric.

## Gates

- P2-023 HumanEval import plumbing.
- P2-022 where external marked-runner/export evidence is used.
- P2-015 suite item/level floors.
- Any L2 C5-I.2 language requires preplanned repeated bundles; otherwise it
  remains L1 association.

## Refusals

- Do not add MMLU or tinyBenchmarks as first import targets.
- Do not name a second source in this pack; reserve only the placeholder.
- Do not make pass@k, accuracy, coding-capability, leaderboard, benchmark-score
  normalization, prompt-quality, or capability claims.
- Do not upgrade heterogeneous published difficulty labels into causal
  difficulty-energy language.

## Plug-In-Day Runbook

Existing commands:

```sh
python3 -m joulewise validate-config configs/campaign_packs/<<C5I_IMPORT_CONFIG>>.json
python3 scripts/run_campaign.py configs/campaign_packs/<<C5I_IMPORT_CONFIG_DIR>> --runs-dir runs --log runs/experiments/<<C5I_IMPORT_EXPERIMENT_ID>>.jsonl --backup
python3 -m joulewise validate-bundle --strict runs/<<BASE_RUN_ID>>__r1
python3 -m joulewise reduce runs/<<BASE_RUN_ID>>__r1
python3 scripts/package_bundle_pack.py --output runs/bundle_packs/<<PACK_ID>> runs/<<BASE_RUN_ID_A>>__r1 runs/<<BASE_RUN_ID_B>>__r1
python3 scripts/package_bundle_pack.py --verify runs/bundle_packs/<<PACK_ID>>
```

PLANNED commands:

```sh
# PLANNED, owner: P2-023 HumanEval import plumbing.
python3 -m joulewise benchmark-import configs/campaign_packs/<<HUMANEVAL_IMPORT_MANIFEST>>.json --output configs/campaign_packs/<<HUMANEVAL_SUITE_MANIFEST>>.json

# PLANNED, owner: import-family reducers after P2-023.
python3 -m joulewise import-family-reduce runs/bundle_packs/<<PACK_ID>> --output runs/analysis/c5-i-import-family
```

Operator sequence:

0. Acquire the no-agent quiet-machine lock (`[QUIET-MAC]`): stop all
   agent/Codex load for the whole measurement session and confirm machine-idle
   state before the first idle baseline.
1. Fill only the HumanEval P2-023 manifest fields. Leave the second-family
   placeholder source-null and non-claim-bearing.
2. Freeze AP rows, source manifest hash, suite manifest, template hashes, and
   order manifest before execution.
3. Execute the import smoke or repeated-bundle campaign according to the frozen
   claim level.
4. Strict-validate, reduce, package, and verify bundles.
5. Keep HumanEval L0-L1 unless repeated strict-valid bundles, floor rows, and
   frozen contrasts support a later L2 import-family claim.

Closing cooldown-gate note: the D-014 cooldown gate between repetitions is
runner-automated, but cooldown cap-hit flags must be checked in each member
bundle's measurement quality before analysis.
