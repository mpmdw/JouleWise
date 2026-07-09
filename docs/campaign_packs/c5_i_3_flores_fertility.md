# C5-I.3 Pack: FLORES Tokenizer Fertility Tax

Status: pre-source-session DRAFT. This pack constrains the FLORES/source
session but does not name the final language set, token-matched substitution
method, source-session language IDs, pair IDs, or frozen AP contrast IDs.

FLORES is separate from the generic import family because it depends on
semantic-matched and token-matched legs, token normalization, licensing, and
the deferred D-046/B6 6-vs-8 language decision.

## Pinned Now

- AP row requires semantic-matched and token-matched legs.
- Request energy is primary; tokenizer-scoped J/token is companion-only.
- Required companion denominators: J/char, J/byte, and semantic-pair IDs.
- FLORES source/licensing/hash discipline.
- Claim ceiling: no tokenizer efficiency ranking without semantic and
  token-matched legs.

## Deferred To FLORES/Source Session

- Exact FLORES language set: 6 vs 8 is deferred by D-046/B6.
- Token-matched substitution method.
- Exact source-session language IDs and pair IDs.
- Frozen AP contrast IDs.

## DRAFT AP Row

| Field | Value |
|---|---|
| Plan ID / RQ consumer | DRAFT-AP-C5-I.3 / C5-I.3 FLORES tokenizer fertility tax. DRAFT until FLORES/source-session freeze. |
| family_id | FAM-C5I3-FLORES-FERTILITY |
| claim_role | primary |
| selection_scope | Frozen FLORES subset after source session: language/script set `<<D-046-B6.FLORES_LANGUAGE_SET_DEFERRED>>`, semantic-pair IDs `<<SOURCE_SESSION.SEMANTIC_PAIR_IDS>>`, token-matched control IDs `<<SOURCE_SESSION.TOKEN_MATCHED_PAIR_IDS>>`, model/runtime/artifact/quant/tokenizer/sampler/output policy, and both semantic-matched and token-matched legs. Countable contrasts are language/script energy deltas and fertility-ratio associations for the frozen pair set only. |
| multiplicity_rule | Holm within FAM-C5I3-FLORES-FERTILITY across predeclared semantic-matched and token-matched language/script contrasts. Any extra language, script, substitution method, or post-hoc pair subset is exploratory with no-confirmatory-inference unless frozen by the source session before execution. |
| Metric + exact window class | Primary: request energy or level-window energy for FLORES pairs. Companions: tokenizer-scoped J/token with runtime-observed denominators, J/char, J/byte, fertility ratio, stop reasons, and semantic-pair identifiers. |
| Unit of analysis + dependence structure | Bundle or block-level uncertainty over paired FLORES items. Semantic-matched and token-matched legs are paired by source-session pair IDs; item windows are not independent replicates without a repeated-bundle/block design. |
| Estimator/formula | Semantic leg estimates energy by same-content language/script pair. Token-matched leg estimates energy after source-session token-matching control. Fertility association reports `delta_energy_j` versus tokenizer fertility ratio, with request energy primary and tokenizer-scoped J/token companion-only. |
| Inclusion/exclusion + quality-flag waiver rules | Include only FLORES items with license, archive hash, frozen subset ID, semantic pair ID, token-matched pair ID, source row hash, rendered prompt hash, character/byte counts, tokenizer identity, BOS policy, output policy, and strict-valid bundles. Waivers must be named before registry freeze. |
| Order/blocking/covariates | Interleave language/script pairs and legs in round-robin paired order. Record source language, target language, script, pair ID, token-matched control ID, item index, block, session, and cooldown flags. |
| Floor gate | pending-P2-015: consume matching item, level, or request floor rows such as `DF-ITEM`, `DF-LEVEL`, `DF-RQ-GROSS-MID`, `DF-RQ-IDLE-MID`, and `DF-CMP-ABBA-RQ` when present. Missing matching floor rows cap claims at L1/descriptive. |
| MDE/n sizing + predeclared top-up rule | n>=5 repeated bundles or accepted repeated-block design for L2 language/script contrasts. Top up to n=10 when semantic or token-matched CI crosses the active floor gate, when fertility association direction changes under leave-one-out, or when token-matched controls fail shape tolerance. |
| Denominator provenance requirement | FLORES license, archive hash, frozen subset ID, semantic pair ID, token-matched pair ID, source row hash, rendered prompt hash, runtime-observed tokens, tokenizer identity, prompt source, BOS handling, character count, byte count, stop reason, output policy, and bundle hashes. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | `L2`. Forbidden upgrade: `no tokenizer efficiency ranking without semantic and token-matched legs`. |
| Disqualifiers + not-resolvable conditions | Final language set named before source session, missing semantic-matched leg, missing token-matched leg, no source license/hash, missing J/char or J/byte denominators, cross-tokenizer J/token promoted to efficiency ranking, source pair IDs missing, or item windows treated as independent replicates. |
| Linked manifests/bundle hashes | pending post-execution; filled at registry freeze and final reduction. |

## Manifest/Config Templates

Every `<<SOURCE_SESSION.*>>` placeholder is intentionally unresolved until the
FLORES/source session. The template records what must be decided there.

```json
{
  "schema_version": "0.1",
  "import_kind": "benchmark_import",
  "import_id": "flores-fertility-<<SOURCE_SESSION.SUBSET_ID>>",
  "source": {
    "benchmark_name": "FLORES",
    "benchmark_revision": "<<SOURCE_SESSION.FLORES_REVISION>>",
    "license": "<<SOURCE_SESSION.FLORES_LICENSE>>",
    "archive_sha256": "<<SOURCE_SESSION.ARCHIVE_SHA256>>",
    "frozen_subset_id": "<<SOURCE_SESSION.SUBSET_ID>>",
    "latest_split_allowed": false,
    "live_fetch_allowed": false
  },
  "language_set": {
    "decision_status": "deferred_by_D-046_B6",
    "count": "<<SOURCE_SESSION.LANGUAGE_COUNT_6_OR_8>>",
    "language_ids": "<<SOURCE_SESSION.LANGUAGE_IDS>>",
    "script_labels": "<<SOURCE_SESSION.SCRIPT_LABELS>>"
  },
  "pairing": {
    "semantic_matched_required": true,
    "token_matched_required": true,
    "token_matched_method": "<<SOURCE_SESSION.TOKEN_MATCHED_METHOD>>",
    "pair_ids": "<<SOURCE_SESSION.PAIR_IDS>>"
  },
  "denominators": {
    "runtime_observed_tokens_required": true,
    "char_count_required": true,
    "byte_count_required": true,
    "semantic_pair_id_required": true
  }
}
```

Suite execution uses the itemized-suite substrate after the source manifest is
materialized:

```json
{
  "schema_version": "0.1",
  "run_id": "c5-i3-flores-<<SOURCE_SESSION.SUBSET_ID>>",
  "suite_manifest": "<<SOURCE_SESSION.FLORES_SUITE_MANIFEST_PATH>>",
  "source_manifest": "<<SOURCE_SESSION.FLORES_IMPORT_MANIFEST_PATH>>",
  "workload_profile": {
    "name": "flores_fertility",
    "suite_id": "<<SOURCE_SESSION.SUITE_ID>>",
    "repetitions": 5,
    "warmup_runs": 1
  },
  "run_metadata": {
    "project": "capstone-joulewise",
    "operator": "ed",
    "tags": ["c5-i.3", "flores", "fertility", "token-normalization"]
  }
}
```

## Expected Artifacts

```text
runs/import_manifests/
  flores-fertility-<subset>.json
runs/<base_run_id>__rN/
  config.json
  metadata.json
  events.jsonl
  summary_metrics.json
  outputs/
    suite_items.jsonl
    item_outputs.jsonl
  source/
    flores_import_manifest.json
runs/analysis/c5-i3-flores/
  semantic_matched_energy.csv
  token_matched_control.csv
  fertility_denominators.csv
  language_pair_manifest.json
```

`fertility_denominators.csv` must include tokenizer identity, runtime-observed
tokens, characters, bytes, semantic pair ID, token-matched pair ID, and output
policy for every item.

## Figure Skeletons

F-C5I3-SEMANTIC: semantic-matched energy by language/script.

- x-axis: language/script pair.
- y-axis: request or level-window energy.
- Caption uses capstone single-unit limitation language and full
  token-normalization stack identity fields. It names semantic pair IDs and
  says request energy is primary.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

F-C5I3-TOKEN-MATCHED: token-matched control.

- x-axis: token-matched control pair.
- y-axis: request energy and companion tokenizer-scoped J/token.
- Caption co-displays J/char and J/byte and states token counts are
  tokenizer-scoped companion metrics.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

F-C5I3-FERTILITY: fertility ratio vs energy delta.

- x-axis: tokenizer fertility ratio.
- y-axis: semantic-matched and token-matched energy delta.
- Caption states no tokenizer efficiency ranking is allowed unless both legs
  are present and floor-cleared.
- Caption includes/cites the full token-normalization stack-identity table,
  including tokenizer name/revision/class/vocab size, `prompt_source`,
  `bos_present` wherever per-token metrics appear, batching/concurrency,
  boundary, and telemetry backend.

## Gates

- FLORES/source session resolves D-046/B6 6-vs-8 language count.
- Source session freezes token-matched substitution method and pair IDs.
- P2-015 item, level, or request floors.
- Token-normalization caption compliance for every table or figure containing
  J/token.

## Refusals

- Do not name the final FLORES language set today.
- Do not make a tokenizer efficiency ranking without both semantic-matched and
  token-matched legs.
- Do not let J/token replace request energy as the primary metric.

## Plug-In-Day Runbook

Existing commands:

```sh
python3 -m joulewise validate-config configs/campaign_packs/<<C5I3_FLORES_CONFIG>>.json
python3 scripts/run_campaign.py configs/campaign_packs/<<C5I3_FLORES_CONFIG_DIR>> --runs-dir runs --log runs/experiments/<<C5I3_FLORES_EXPERIMENT_ID>>.jsonl --backup
python3 -m joulewise validate-bundle --strict runs/<<BASE_RUN_ID>>__r1
python3 -m joulewise reduce runs/<<BASE_RUN_ID>>__r1
python3 scripts/package_bundle_pack.py --output runs/bundle_packs/<<PACK_ID>> runs/<<BASE_RUN_ID_A>>__r1 runs/<<BASE_RUN_ID_B>>__r1
python3 scripts/package_bundle_pack.py --verify runs/bundle_packs/<<PACK_ID>>
```

PLANNED commands:

```sh
# PLANNED, owner: FLORES/source session import plumbing.
python3 -m joulewise benchmark-import configs/campaign_packs/<<FLORES_IMPORT_MANIFEST>>.json --output configs/campaign_packs/<<FLORES_SUITE_MANIFEST>>.json

# PLANNED, owner: FLORES fertility reducer.
python3 -m joulewise flores-fertility-reduce runs/bundle_packs/<<PACK_ID>> --output runs/analysis/c5-i3-flores
```

Operator sequence:

0. Acquire the no-agent quiet-machine lock (`[QUIET-MAC]`): stop all
   agent/Codex load for the whole measurement session and confirm machine-idle
   state before the first idle baseline.
1. Run the FLORES/source session first. Resolve language set, token-matched
   method, language IDs, and pair IDs there, not in this pack.
2. Freeze AP row, source manifest, pair manifest, denominator fields, and
   order manifest.
3. Execute semantic-matched and token-matched legs in paired round-robin order.
4. Strict-validate, reduce, package, and verify bundles.
5. Report request energy first and J/token only as tokenizer-scoped companion
   beside J/char, J/byte, and pair IDs.

Closing cooldown-gate note: the D-014 cooldown gate between repetitions is
runner-automated, but cooldown cap-hit flags must be checked in each member
bundle's measurement quality before analysis.
