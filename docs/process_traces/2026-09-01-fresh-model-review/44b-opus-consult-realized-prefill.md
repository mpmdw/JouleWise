# 44b — Opus 5 contract seat: realized-prefill check placement (three-seat consult, trace 43)

## Design

**Recommended shape: four layers, but the *stop* moves from the sketch's layer (b) to the strict bundle validator.**

**L0 — registration (generator + schema).** `WorkloadProfile` (`joulewise/schemas.py:830-882`) gains two optional fields:

- `prompt_token_ids_sha256: str | None` — the pin's `prompt_token_ids_sha256`. Domain-compatible by construction: the generator's `_token_ids_sha256` is literally `prompt_token_ids_sha256` from `joulewise/provenance.py` (`configs/campaigns/d117_contrast_v5/generate_configs.py:809-810`), the same function the adapter's `prompt_provenance` calls (`joulewise/provenance.py:318-324`), under domain `joulewise.prompt_token_ids.v1` (`provenance.py:12,55-60`). Apples to apples.
- `expected_prompt_tokens: int | None` — `PREFILL_LENGTH`. It **must** be a distinct name: `prompt_tokens` is a *prompt source*, mutually exclusive with `prompt_text` (`schemas.py:282-304`), so reusing it makes the config unloadable. That exclusivity is exactly why the registered length is unreachable from the prefill config today.

Both are **omission-serialized optionals** under the D-044 pattern already in `to_dict` (`schemas.py:1046-1059`): deleted when `None`, so every existing config serializes byte-identically. `_validate_workload_semantics` (`schemas.py:286-304`) gains: either field present requires `prompt_text` present, and neither may accompany `prompt_tokens`.

Generator: `workload_for()` prefill branch (`generate_configs.py:1404-1411`) emits both, from `PREFILL_TOKEN_IDS_SHA256[arm]` and `PREFILL_LENGTH`. Pure function of the committed pin — `_load_prefill_prompt_pin` is explicitly tokenizer-free (`generate_configs.py:816`). Constraint (2) satisfied.

**L1 — PRIMARY, fail-closed, stops the night: `joulewise/cli.py::_strict_workload_provenance_problems` (707-826), non-suite branch.**

Why here and not `run_campaign`: `scripts/run_campaign.py:7543` runs `validate_bundle(bundle_path, strict=True)` per attempt immediately after the run subprocess returns; any strict problem sets `reason = "strict_bundle_invalid"`, `eligible_for_analysis = False` (`7566-7567`), which falls into the block at `7581` ending in `return 1` at `7615`. **First bad bundle ends the night**, with no new stop mechanism invented. Data is bundle-internal only: `config.json` — written as `json.dumps(config.to_dict())` (`joulewise/bundle.py:950-953`) and proven byte-equal to the registered campaign config by `_bundle_config_binding_problem` (`run_campaign.py:1253-1280`) — plus `metadata.json`. Constraints (3) and (5) satisfied together.

Exact comparisons and named refusals (all gated on the config declaring the field; `None` ⇒ not applicable):

| refusal | compares |
|---|---|
| `prompt_realization_ids_mismatch` | `workload_profile.prompt_token_ids_sha256` vs `metadata.workload_provenance.prompt.token_ids_sha256` |
| `prompt_realization_count_mismatch` | `workload_profile.expected_prompt_tokens` vs `...prompt.realized_token_count` |
| `prompt_realization_text_mismatch` | `sha256(workload_profile.prompt_text)` vs `...prompt.text_sha256` |
| `prompt_realization_unverifiable` | **neither-branch**: expectation declared, prompt block present, but the compared field is absent/null ⇒ refuse, never default-pass |

Compare against `realized_token_count`, **not** `end_metadata.prompt_tokens` — see Dissent (2). It is already a strict-required key (`cli.py:723-747`).

**L2 — campaign label (not the stop): `evaluate_member` (`run_campaign.py:2773-2880`)** adds `prompt_realization_mismatch` to `collection_integrity_flags`, which makes `usable` False (`415-465`) and lands in `to_log()` (`469-482`). Do **not** add it to `VALID_WAIVER_SCOPES` (`630-638`) — under D-161 this is a physics/evidence fence, unwaivable. Do **not** extend `check_prompt_hashes_for_config_bundle` (`2692-2710`): its whole body (`2586-2684`) is sidecar+suite-item shaped (`sidecar["items"]`, `_manifest_text_items`, `outputs/suite_items.jsonl`); a `prompt_text` branch there is a parallel mechanism inside a function that shares none of its machinery.

**L3 — analysis backstop: `joulewise/analysis_engine/inputs.py::_realized_identity_matches_config` (2552-2617).** Its non-suite `else:` branch today checks only `output_policy.requested_tokens == workload_config.output_tokens` (`2604-2608`); add the two prompt comparisons there. It reads the typed config via `_typed_config` → `BenchmarkConfig.from_mapping(...).to_dict()` (`2467-2471`), so the new dataclass fields appear for free. **Reuse the existing `config_hash_mismatch` reason code** (`inputs.py:2772-2773`) rather than minting one: `REASON_CODES` is a closed registry with a precedence table (`analysis_engine/claims.py:219-233`), and the specific diagnosis is already carried by L1's named strict problem. `floor_extraction.py` and `analysis_manifest_v3.py` are not touched.

**Why the alternatives lose**

- **Condition family.** `_CONDITION_FAMILY_V1_WORKLOAD_KEYS` (`floor_extraction.py:724-730`) is enforced as an *exact* key set by `_exact_mapping_keys` (`813-826`). Adding a key means editing a gauntlet module and either bumping the family schema version or breaking every v1 family — the two decode families and both floor packs share the v1 shape. It also moves `condition_family_byte_sha256` / `condition_family_domain_sha256` for all four families (`generate_configs.py:1608-1615`), not just prefill. Loses on constraint (4), and the family is the wrong owner anyway: the family describes the *condition*, the run config describes the *instance*.
- **Adapter refusal at `_prompt_for_workload`** (`mlx_runtime.py:930-947`). The precedent exists — `_suite_prompt_closure_problem` (`1133-1167`) does exactly this comparison for suite items and is consumed as fatal at `572-582`. But (i) it puts pack semantics in the adapter, (ii) it covers only the MLX adapter, (iii) L1 already stops at the same granularity (one run), so earliness buys one process exit, and (iv) an adapter raise loses evidence: a strict failure leaves a finalized, inspectable bundle with the mismatched hash recorded, which is what the post-mortem needs. Note also that the suite precedent tolerates `source_hash in {realized_hash, text_hash}` (`1147`) — a prefill check must *not* copy that OR, since text equality is precisely what fails to catch tokenizer drift.
- **Raw unknown keys in `workload_profile` (sketch (a) as literally written).** Inert: `from_mapping` ignores unknown keys (`schemas.py:843-879`), `_unknown_config_key_warnings` (`192-203`) against the hand-maintained `_CONFIG_KEYS_BY_PATH["workload_profile"]` (`169-183`) emits a `ConfigKeyWarning`, and `to_dict` drops them before `config.json` is written (`bundle.py:950-953`). No downstream checker would ever see them.
- **8B arm's own hash.** Not a distinct *value*: `token_ids = {arm: list(prefill_pin["prompt_token_ids"]) for arm in ("A","B")}` (`generate_configs.py:1091`) gives both arms the identical list, loaded under one shared tokenizer sha (`1084-1088`) that `pair_tokenizer_identity_mismatch` forces equal (`1016-1022`). Still emit it **per config** rather than as a pack constant — identical cost, survives any future relaxation of the pair rule.

## Blast radius

- `joulewise/schemas.py`: `WorkloadProfile` (830-882), `to_dict` omission list (1049-1059), `_CONFIG_KEYS_BY_PATH["workload_profile"]` (169-183), `_validate_workload_semantics` (286-304).
- `joulewise/cli.py`: `_strict_workload_provenance_problems` (707-826) only.
- `scripts/run_campaign.py`: `evaluate_member` (2773-2880). Nothing at 2586-2710.
- `joulewise/analysis_engine/inputs.py`: the `else:` branch at 2604-2608.
- `configs/campaigns/d117_contrast_v5/generate_configs.py`: `workload_for()` (1404-1411).

**No byte drift anywhere else.** Because the fields are omission-serialized, every existing config and every retained bundle's `config.json` serializes byte-identically: `config_sha256`, `_scientific_config_sha256` (`run_campaign.py:1219-1230`), and analysis-manifest config pins are unchanged. **`condition_family_sha256` does not move.** **The frozen registration hash does not move** — `PINNED_DOMINANCE_CRITERION_BYTES` covers `dominance_criterion_registration()` only (`tests/test_d117_contrast_v5_pack.py:518-524`). Reviewed modules entered: `cli.py` strict validator and `analysis_engine/inputs.py`; **`floor_extraction.py` and `analysis_manifest_v3.py` are not entered.** Regenerating the pack moves the prefill configs' own bytes — expected on the desk day.

## Failure modes

Honest drift = an `mlx_lm`/tokenizer upgrade between desk day and collection, so `_encode(tokenizer, prompt_text, add_special_tokens=True)` (`mlx_runtime.py:936`) yields different ids.

1. **Different ids, same count.** Adapter: silent. **L1 catches first** (`prompt_realization_ids_mismatch`), run N's bundle is strict-invalid, night exits 1. Today: nothing catches it ever — the prefill arm measures a different token sequence at the registered length, and the claim is "prefill energy at L tokens".
2. **Different count** (BOS policy change, merge-table change). L1 raises both count and ids refusals. Today: nothing. An off-by-one is negligible energy; an off-by-k from a merge change is not.
3. **Config text drift** (prompt_text edited without re-pinning). `_bundle_config_binding_problem` (`run_campaign.py:1264-1279`) already catches config-vs-bundle disagreement; `prompt_realization_text_mismatch` catches pin-vs-emitted-text.
4. **Provenance present but null.** Existing strict key/shape checks (`cli.py:723-747`) refuse a missing hash; the neither-branch covers the declared-expectation case.
5. **Retained corpora and pre-change bundles.** Neither field present ⇒ both comparisons `None`-gated ⇒ not applicable. No retroactive refusal, correct for a pre-registration fence.
6. **Bundle collected outside `run_campaign`.** L1 still fires (bundle-local); L2/L3 would not. Another reason L1 is the right owner.

First-catch order: **L1** (same night, run N, exit 1) → L2 (member log, `usable=False`) → L3 (analysis desk, exclusion). The sketch put the stop at L2; L2 does not stop.

## Tests

Defect-shaped, fixture-only, no tokenizer:

1. `test_strict_refuses_prefill_ids_hash_drift` — counts **equal**, hashes differ ⇒ `prompt_realization_ids_mismatch`. Kills the count-only mutant.
2. `test_strict_reports_both_count_and_ids_refusals` — both differ ⇒ **both** problems present. Kills the first-problem short-circuit.
3. `test_strict_refuses_when_expectation_declared_and_provenance_null` ⇒ `prompt_realization_unverifiable`. Kills the `if realized is not None:` default-pass — the classic neither-branch defect.
4. `test_strict_passes_when_config_declares_nothing` — retained-corpus shape ⇒ zero new problems. Kills retroactive refusal.
5. `test_config_bytes_unchanged_when_new_fields_are_none` — `BenchmarkConfig.from_mapping(old).to_dict()` byte-identical to a pre-change golden. **This is the test that protects every retained bundle**; kills a D-044 omission-serialization regression.
6. `test_unknown_key_warning_registry_covers_new_fields` — no `ConfigKeyWarning` for a config carrying them. Kills the forgotten `_CONFIG_KEYS_BY_PATH` edit.
7. `test_workload_semantics_rejects_expectation_without_prompt_text` and `..._rejects_prompt_tokens_plus_expected_prompt_tokens`.
8. `test_v5_prefill_config_carries_pin_hash_and_length` — both arms: emitted hash `== prompt_token_ids_sha256(pin["prompt_token_ids"])`, `expected_prompt_tokens == PREFILL_LENGTH`, A value `==` B value. Kills a hard-coded-arm-A mutant.
9. `test_night_stops_on_first_prompt_realization_mismatch` — stubbed dispatch: attempt 1 finalizes a mismatched bundle ⇒ ledger row carries `strict_bundle_invalid`, process returns 1, attempt 2 never dispatched. **The constraint-(5) test, and the one most likely to be skipped.**
10. `test_analysis_excludes_prefill_bundle_with_prompt_realization_mismatch` — `inputs.py` backstop.
11. Pin-side precondition test — see Dissent (4).

## Dissent

**(1) The stop belongs in the strict bundle validator, not in `check_prompt_hashes_for_config_bundle`.** `collection_integrity_flags` do not stop a night: per-member evaluation at `run_campaign.py:7619-7640` records provenance and continues, and the flags are consumed only by the end-of-window verdict (`7862-7880`). The single per-attempt short-circuit is `validate_bundle(..., strict=True)` at `7543` → `strict_bundle_invalid` at `7566` → `return 1` at `7615`. Sketch (b) as written would have logged the mismatch and finished the night.

**(2) Compare `realized_token_count`, not `end_metadata.prompt_tokens`.** `prompt_provenance` emits `realized_token_count` (`provenance.py:318-324`); `end_metadata.prompt_tokens` is the suite-item / envelope-window field (`envelope_gate.py:371`), not the single-run prompt block.

**(3) Sketch (a) as literally written is inert.** Raw `workload_profile` keys never reach the bundle: `config.json` is `json.dumps(config.to_dict())` (`bundle.py:950-953`). Real dataclass fields with D-044 omission-serialization are mandatory, not cosmetic.

**(4) A gap the sketch does not name: the pin's closed schema has no special-token policy field.** `_load_prefill_prompt_pin`'s key set (`generate_configs.py:834-855`) records `prompt_token_ids`, `prompt_tokens`, `generation_method`, but never states that the ids are the `add_special_tokens=True` encoding — which is exactly what the adapter hard-codes (`mlx_runtime.py:936`). Land this check and the desk-day probe must encode under that policy or the first prefill run of the night fails: correctly, but at the cost of a night. Two options: (i) cheap — a runsheet precondition plus a test asserting the fixture ids carry the BOS; (ii) durable — add `special_token_policy: "add_special_tokens=true"` to the pin's v2 closed schema and assert it in the loader. **I recommend (ii)**: a one-line addition to a closed schema in a file being regenerated anyway, and it converts a night-losing surprise into a desk-day refusal. It is the one place I would spend beyond the sketch.
