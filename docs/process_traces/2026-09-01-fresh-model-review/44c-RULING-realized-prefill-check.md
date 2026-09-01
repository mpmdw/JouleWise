# Ruling 44c — realized-prefill check placement (three-seat consult on trace 43)

Magistrate synthesis, 2026-09-01. Seats: Sol xhigh (`44-sol-consult-realized.md`), Opus 5
contract lens (`44b-opus-consult-realized-prefill.md`), blind fresh Fable (`44d-fable-blind-consult-realized-prefill.md`).
Forcing problem (trace 43): no consumer compares a `_v5` prefill run's realized token count /
ids hash with the registered length / hash; an honest `mlx_lm`/tokenizer change between the
desk day and the night would silently measure the wrong prefill length.

## Where the three seats agree (adopted without further argument)

1. The registered expectation rides in each prefill run config's `workload_profile` as a
   **typed, closed-schema, omission-serialized** field (D-044 pattern): legacy configs and
   every retained bundle's `config.json` serialize byte-identically. Free keys are inert
   (`WorkloadProfile.from_mapping` drops unknown keys; `to_dict` never writes them) — the
   magistrate's sketch (a) as written would have done nothing. The expected count must NOT be
   named `prompt_tokens` (that is a prompt *source*, exclusive with `prompt_text`).
2. The generator projects the committed pin (`PREFILL_TOKEN_IDS_SHA256[arm]`, `len(ids)`) —
   no tokenizer, no model. Emitted **per config, per arm** (identical today under the shared
   tokenizer rule; self-contained if that rule is ever relaxed).
3. NOT in the condition family (closed v1 key set; moves every `condition_family_sha256` and
   enters `floor_extraction.py`). NOT in the adapter (`_prompt_for_workload` runs inside the
   measured tokenize window; a raise loses the inspectable bundle). NOT in
   `check_prompt_hashes_for_config_bundle` (suite/sidecar-shaped machinery). NOT in
   `floor_extraction.py` or `analysis_manifest_v3.py`.
4. The night-stop is the existing per-attempt `validate_bundle(bundle_path, strict=True)` →
   `strict_bundle_invalid` → `return 1` (`scripts/run_campaign.py:7544-7615`) — verified at the
   bench: no waiver is consulted on that path. The refusal must additionally be **unwaivable in
   `evaluate_member`, including scope `any`** (Sol F1): a physics/evidence fence under D-161.
5. The frozen registration hash (`dominance_criterion_registration()` only) does not move;
   the regenerated prefill configs' own bytes do, as expected on the desk day.

## Where they differ, and the ruling

| Question | Sol | Opus | Fable | Ruling |
|---|---|---|---|---|
| Carrier shape | atomic object `prompt_token_expectation {schema_version, token_hash_domain, token_count, token_ids_sha256}` | two flat fields | two flat fields, both-or-neither rule | **Sol's atomic object.** Both-or-neither and the hash domain become structural instead of a validation rule; the domain label makes "apples to apples" with `joulewise/provenance.py` explicit. |
| Comparison home | `BundleReader.problems()` (`joulewise/bundle_read.py`), succeeded bundles carrying the expectation | `cli.py::_strict_workload_provenance_problems` | identity-pin projection + `run_campaign` + `inputs.py` | **`BundleReader.problems()` — one home.** Bench-verified: `validate_bundle()` = `reader.problems()` + `_strict_problems` (`joulewise/cli.py:392-412`), and `validate_bundle` is the injected validator for floor extraction (`floor_extraction.py:46-56`) and analysis inputs (`inputs.py:5`). One implementation therefore stops the night AND refuses at every consumer; Opus's `inputs.py` backstop and Fable's `inputs.py` change would be duplicates and are struck. |
| Refusal names | `prompt_realization_evidence_missing`, `prompt_realization_evidence_inconsistent`, `prompt_realization_mismatch` | `..._ids_mismatch`, `..._count_mismatch`, `..._text_mismatch`, `..._unverifiable` | reuse `config_hash_mismatch` / `readiness_identity_environment_dirty` | **Sol's three**, with the mismatch problem text naming which of count/hash/domain differed (Opus's granularity inside Sol's names). Absence is never a pass (`evidence_missing` is the neither-branch case). |
| Realized surfaces compared | provenance domain/hash/count + tokenize `end_metadata.prompt_tokens` + prefill `start_metadata.prompt_tokens` + `observed.token_count − output_token_count` + `text_sha256` vs config text | provenance `realized_token_count` + hash + text hash | provenance only; markers are the same in-process `len()` | **Provenance count/hash/domain and `text_sha256` are MANDATORY.** The marker and observed-token surfaces are consistency checks (`evidence_inconsistent`) that the fixer enables only after showing, in the report, that each surface is present in a real retained succeeded single-prompt bundle (`runs*/`, read-only); any surface absent from legitimate bundles is dropped with a note. |
| Earliest catcher | first prefill member of the night | first prefill bundle (strict) | identity-pin projection at freeze/arm (before any joule) — `mlx_runtime.identity_projection_metadata` + `identity_pins._derive_projection_units` | **Deferred to a second row**, `V5-PREFILL-REALIZED-PROJECTION-02`: it enters arm-critical `identity_pins.py` (D-131 → council trigger) and buys "before the night" over "first prefill bundle". Worth having — a lost night costs Ed a week — but it is defense-in-depth, not the fence, and must not delay row 01. |
| Generator closed-pack validation | `prompt_realization_registration_{missing,invalid,inconsistent}` | test 8 only | desk equality tests | **Sol's three generator refusals** (config ↔ `prompt_candidate.token_count_basis.per_model[]` ↔ family `prompt_tokens`), plus the desk equality tests. |
| Pin `special_token_policy` field | — | add to pin v2 closed schema (recommended) | issuer must encode via the adapter path | **Already satisfied on the probe branch**: `scripts/issue_g2a_prefill_prompt_pin.py:107` encodes with `add_special_tokens=True` through `_encode`. Opus's explicit field is a should-fix for the probe stream's next round (records the policy the ids were produced under); not this row. |

## Kernel row

`V5-PREFILL-REALIZED-IDS-CHECK-01` — goal: a `_v5` prefill bundle whose realized prompt
token count, ids hash, or hash domain differs from the registered expectation in its own
`config.json` is refused by `BundleReader.problems()` with a named reason, stops the night on
first occurrence, is unwaivable, and is excluded neither-branch at every consumer. Depends on
nothing unlanded (the pin fields it projects exist in `_load_prefill_prompt_pin` today).
Follow-up row `V5-PREFILL-REALIZED-PROJECTION-02` (identity-projection catcher; council
trigger; after 01).

## Implementation brief (Sol xhigh, new worktree off main)

WRITE_SCOPE: `joulewise/schemas.py`, `joulewise/bundle_read.py`, `scripts/run_campaign.py`,
`joulewise/publication_privacy.py`, `configs/campaigns/d117_contrast_v5/generate_configs.py`,
`tests/test_schemas.py`, `tests/test_bundle_read.py`, `tests/test_run_campaign.py`,
`tests/test_publication_privacy.py`, `tests/test_d117_contrast_v5_pack.py` (new tests only;
`PINNED_DOMINANCE_CRITERION_BYTES` and every golden readback untouched — full diff shown),
`tests/goldens/config_schema.json`, `docs/process/state_kernel.json`, `RUN_STATE.md`,
`TASK_QUEUE.md` (kernel-generated interiors only, via `scripts/gen_state.py`).
Tests: Sol's list in report 44 §Tests verbatim, plus Opus's test 5 (legacy config
`to_dict()` golden bytes unchanged) and test 6 (no `ConfigKeyWarning`). Refuters: Opus contract
lens + luna execution/mutation lens; delta by terra.
