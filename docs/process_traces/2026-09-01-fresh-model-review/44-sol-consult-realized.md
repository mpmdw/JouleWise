```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Put an atomic per-config prompt expectation in authenticated workload bytes, enforce it once in BundleReader, and make every resulting physics refusal non-waivable.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "exact",
    "head_start": "c84d6f6c7f2d7767e7a35a6b48e2b3207102b5c6",
    "head_end": "49cc86d0125172606f3c7672827a60ea62031cbf",
    "upstream_end": "49cc86d0125172606f3c7672827a60ea62031cbf",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/process_traces/2026-09-01-fresh-model-review/36-luna-delta-27-skeleton.md",
    "docs/process_traces/2026-09-01-fresh-model-review/36b-RULING-skeleton-delta.md",
    "docs/process_traces/2026-09-01-fresh-model-review/42-terra-delta-fiducial.md",
    "docs/process_traces/2026-09-01-fresh-model-review/42b-RULING-fiducial-delta.md"
  ],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The sketched mismatch remains waiverable",
        "detail": "run_campaign currently permits prompt_hash_mismatch, strict_invalid, and scope any through the generic waiver path; merely adding a collection flag would not satisfy D-161 fail-closed physics semantics.",
        "recommendation": "Give prompt-realization registration, evidence, and mismatch codes an explicit non-waivable classification."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "The analysis check belongs at the shared bundle-reader seam",
        "detail": "BundleReader.problems feeds validate_bundle, per-member collection evaluation, floor extraction, mint revalidation, and analysis-engine ingestion.",
        "recommendation": "Implement the comparison once in bundle_read rather than duplicating it in floor_extraction or the manifest finalizer."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "The proposed flat fields are ambiguous and not atomic",
        "detail": "prompt_token_ids_sha256 does not say expected versus realized, and two optional scalars permit half-present registrations unless every reader adds pairing rules.",
        "recommendation": "Use one closed prompt_token_expectation object carrying count, hash, and hash domain."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch 2>/dev/null",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## main\\.\\.\\.origin/main$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --name-only c84d6f6c7f2d7767e7a35a6b48e2b3207102b5c6..49cc86d0125172606f3c7672827a60ea62031cbf -- . ':(exclude)docs/process_traces/**' 2>/dev/null",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "W1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "main advanced during inspection and four transient untracked review files were subsequently committed; the intervening changes were confined to docs/process_traces and did not change any inspected production seam.",
      "needs": ""
    }
  ]
}
```

## Findings

- **F1 — Blocker:** The sketch’s `prompt_hash_mismatch`/strict-failure treatment is currently waiverable, including through waiver scope `any`. A physics mismatch must instead be explicitly non-waivable, or the first mismatch could become “waived” and collection could continue.

- **F2 — Should-fix:** Analysis-specific enforcement in `floor_extraction` or `analysis_manifest_v3` would duplicate a check that naturally belongs in `BundleReader.problems()`. That reader already feeds collection and all relevant evidence consumers.

- **F3 — Should-fix:** Use an atomic, domain-labelled expectation object rather than the two proposed flat fields.

## Design

The generator should add this object only to each `_v5` prefill run’s `workload_profile`:

```json
"prompt_token_expectation": {
  "schema_version": "joulewise.prompt_token_expectation.v1",
  "token_hash_domain": "joulewise.prompt_token_ids.v1",
  "token_count": 512,
  "token_ids_sha256": "<64 lowercase hex>"
}
```

`token_count` is `len(PREFILL_TOKEN_IDS[arm])`; `token_ids_sha256` is `PREFILL_TOKEN_IDS_SHA256[arm]`. The generator merely projects the committed prompt pin—no tokenizer or model access.

The 8B configs should carry their own arm-derived expectation. The shared-tokenizer rule currently makes the two hashes equal, but each authenticated config should remain self-contained and correct if that pair policy is ever revisited.

The generator’s closed-pack validation should refuse:

- `prompt_realization_registration_missing`: any generated prefill config lacks the expectation.
- `prompt_realization_registration_invalid`: malformed object, wrong domain, bad hash/count, or expectation present on a decode config.
- `prompt_realization_registration_inconsistent`: config count/hash disagrees with the corresponding `prompt_candidate.token_count_basis.per_model[]`, or the count disagrees with the prefill condition family’s `prompt_tokens`.

`joulewise/schemas.py` should validate the object as a closed, optional workload field: exact schema/domain, positive non-boolean count, lowercase SHA-256, and legal only with `prompt_text`.

The realized comparison should live in `joulewise/bundle_read.py`, called from `BundleReader.problems()` for a succeeded bundle carrying the expectation. It should require:

```text
expected.token_hash_domain
  == workload_provenance.prompt.token_hash_domain

expected.token_ids_sha256
  == workload_provenance.prompt.token_ids_sha256

expected.token_count
  == workload_provenance.prompt.realized_token_count
  == tokenize phase Window.end_metadata.prompt_tokens
  == prefill phase Window.start_metadata.prompt_tokens
  == workload_observed.token_count - workload_observed.output_token_count
```

It should additionally require:

```text
workload_provenance.prompt.text_sha256
  == SHA256(config.workload_profile.prompt_text UTF-8)
```

The count means the exact adapter input token sequence, including special tokens, matching the pin’s `add_special_tokens=True` convention.

Bundle-reader refusal names:

- `prompt_realization_evidence_missing`: required provenance or count-bearing marker evidence is absent or ill-typed.
- `prompt_realization_evidence_inconsistent`: realized evidence surfaces disagree, or the recorded text hash does not match the authenticated config.
- `prompt_realization_mismatch`: internally coherent realized domain/count/hash differs from the registered expectation.

`scripts/run_campaign.py` should map those exact reader codes into `collection_integrity_flags`, preserve the bundle unchanged, classify the member failed, and explicitly exclude all three from waiver recovery—including waiver scope `any`. With the generated `--max-failures 1`, the first mismatching prefill member stops its stage immediately.

Analysis needs no second semantic implementation. `validate_bundle()` already includes `BundleReader.problems()`, and the real strict validator is injected into floor extraction, mint revalidation, and analysis-engine input loading. The same named problem therefore yields neither-branch exclusion everywhere.

The alternatives lose as follows:

- **Condition family:** Scientifically permissible before collection, but unnecessary. It changes the v1 family schema, both family byte/domain hashes, floor-cell identities, and the heavily reviewed family validator. It also does not directly give the runtime checker a path to the file. The authenticated run config is the correct execution projection.
- **Adapter refusal:** Earlier, but incomplete. It cannot protect later evidence consumption, duplicates the bundle admission rule, and `_prompt_for_workload` failures during warmup currently collapse into `runtime_unavailable`. A typed adapter preflight could be added later as defense-in-depth, but it is not needed to stop after the first member.
- **`check_prompt_hashes_for_config_bundle`:** That function is organized around suite manifests and generator sidecars. Extending it would duplicate the common reader check and inherit the current waiver problem.
- **Floor/manifest finalizer:** Too late for collection and enters reviewed modules without necessity.

## Blast radius

Expected production changes:

- `configs/campaigns/d117_contrast_v5/generate_configs.py`
- `joulewise/schemas.py`
- `joulewise/bundle_read.py`
- `scripts/run_campaign.py`
- `joulewise/publication_privacy.py` for the config-field allowlist

Expected tests/golden changes:

- `tests/test_d117_contrast_v5_pack.py`
- `tests/test_schemas.py`
- `tests/test_bundle_read.py`
- `tests/test_run_campaign.py`
- `tests/test_publication_privacy.py`
- `tests/test_floor_extraction.py` or `tests/test_analysis_inputs.py`
- `tests/goldens/config_schema.json`

No production changes are needed in:

- `joulewise/adapters/mlx_runtime.py`
- `joulewise/cli.py`
- `joulewise/floor_extraction.py`
- `joulewise/analysis_manifest_v3.py`
- `joulewise/analysis_engine/inputs.py`
- `docs/paper/draft-v1.md`

`condition_family_sha256` remains unchanged. The frozen `dominance_criterion_registration()` hash remains unchanged.

Normal regenerated-pack identities do move: prefill config bytes and SHA-256 values, config inventory/identity projections, plan tree, prospective manifest identity, order-side bindings, generator hash, and any subsequently issued freeze receipt.

## Failure modes

- Same tokenizer bytes but changed `mlx_lm`/tokenizer behavior produces different IDs with the same count: the hash comparison catches the first prefill member.

- Tokenization produces a different length: count and normally hash both differ; the first prefill member is non-waivably failed and the stage stops.

- The adapter records one count in provenance but another on phase markers or total-token accounting: `prompt_realization_evidence_inconsistent` fires before interpreting it as honest drift.

- Realized prompt provenance is missing or malformed: `prompt_realization_evidence_missing` fires; absence cannot become a pass.

- Generator projection disagrees with the prompt candidate or family length: pack generation/check refuses before freeze through `prompt_realization_registration_inconsistent`.

- Config bytes are altered after freeze: existing config SHA-256, inventory, and launch-lineage checks fail before this comparison supplies any authority.

- An unrelated runtime failure occurs before a prompt is realized: retain its actual runtime/status failure. Do not mislabel it as a realization mismatch merely because successful-run evidence was never written.

## Tests

- Generate a pack and prove every prefill config’s expectation equals its model’s candidate row and family count; prove every decode config omits it.

- Pin separate A/B fixture rows and prove each model receives its own expectation, even when production’s shared-tokenizer rule makes them equal.

- Reject malformed expectation schema, domain, count, hash, half-registration, and use with a non-`prompt_text` source; prove legacy configs without the object remain valid.

- Start from a valid succeeded single-prompt bundle and mutate all realized count surfaces coherently to `L+1`; require only `prompt_realization_mismatch`.

- Keep count fixed but mutate the realized token hash; require `prompt_realization_mismatch`.

- Mutate only one count-bearing surface; require `prompt_realization_evidence_inconsistent`.

- Delete realized prompt provenance or the required phase-marker count; require `prompt_realization_evidence_missing`.

- Change `prompt_text` without updating realized `text_sha256`; require evidence inconsistency in addition to existing config authentication failures where applicable.

- Run a two-config campaign whose first bundle mismatches; prove the second child is never invoked under `--max-failures 1`.

- Supply both an explicit matching waiver and scope `any`; prove the mismatching member remains failed and the campaign exits nonzero.

- Feed the same mismatching bundle through real `validate_bundle`, floor extraction, and analysis-input admission; require the exact named refusal to survive and the bundle to remain neither-branch.

## Dissent

I agree with the sketch’s central move—copy the pin-derived expectation into each authenticated prefill config—but disagree with both enforcement placements. The current runner flag is waiverable, so it is not yet D-161 fail-closed; and adding a second analysis comparison in `floor_extraction` or the manifest finalizer creates unnecessary semantic duplication. One atomic expectation in the config, one structural comparison in `BundleReader`, and an explicit non-waivable runner classification give earlier collection failure and universal downstream refusal with less reviewed-code exposure.

## Residual risk

Single-prompt bundles retain the realized token-ID hash, not the full realized ID array, so hash correctness ultimately trusts that `prompt_provenance()` hashed the same list passed to generation. The current MLX path does so directly. Persisting all prompt IDs would independently strengthen that claim but is not necessary for the stated honest-drift threat model and would materially enlarge the evidence contract.