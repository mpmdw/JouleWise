# 44d — blind fresh Fable seat: realized-prefill check placement (three-seat consult, trace 43)

## Design

**Principle.** The registered numbers ride in the run config as *typed, hash-bound qualifiers of `prompt_text`*, and three existing seats compare realized-vs-registered in time order: the identity-pin projection (before arming), the campaign runner's per-bundle evaluation (during the night), and the analysis engine's config-vs-realized identity check (at consumption). No new reason codes on the arm side, no new `FailureReason`, no change to `floor_extraction.py` or `analysis_manifest_v3.py`.

### Layer 0 — carrier: two typed fields on `workload_profile` (`joulewise/schemas.py`)

Add to `WorkloadProfile` (schemas.py:830-841):

- `prompt_text_token_ids_sha256: str | None` — the domain-separated hash `prompt_token_ids_sha256(ids)` (provenance.py:58-60), i.e. the same function the adapter uses at run time (mlx_runtime.py:401 → provenance.py:322).
- `prompt_text_token_count: int | None` — the registered exact length (D-122).

Rules, enforced in `_validate_workload_semantics` (schemas.py:286-304) and mirrored in the JSON schema (schemas.py:1200-1226):
- both-or-neither, like `_SUITE_MANIFEST_PAIR` (schemas.py:69, 287-293) → `SchemaError("workload_profile.prompt_text_token_ids_sha256 and prompt_text_token_count are required together")`;
- present only when `prompt_text` is non-null → `SchemaError("workload_profile.prompt_text_token_* require prompt_text")`;
- 64 lowercase hex; positive int.
- Add both names to `_CONFIG_KEYS_BY_PATH["workload_profile"]` (schemas.py:169-183), and **omission-serialize** them in `to_dict()` exactly as D-044 does for the suite fields (schemas.py:1052-1059). That keeps every legacy config's normalized bytes, `scientific_config_sha256` (run_campaign.py:1219-1231), `config_set_sha256` (identity_pins.py:1498-1503) and frozen v3 receipts byte-identical.

Why typed rather than the sketch's free keys: `WorkloadProfile.from_mapping` silently drops unknown keys and only warns (schemas.py:844-879, 1009-1011). Every downstream identity path normalizes through the dataclass — bundle↔pack config binding (run_campaign.py:1264-1279), scientific identity (run_campaign.py:1219-1231), declared identity (identity_pins.py:1231-1248, 1453), analysis identity (inputs.py:2558). Free keys would be invisible to all of them and would fail constraint (3). Also: the expected count must **not** be called `prompt_tokens` — `prompt_tokens` and `prompt_text` are mutually exclusive prompt sources (schemas.py:63-68, 294-304).

### Layer 0′ — generator emits the expectation (pure; constraint 2 holds)

`workload_for()` prefill branch (generate_configs.py:1414-1420) adds `"prompt_text_token_ids_sha256": PREFILL_TOKEN_IDS_SHA256["A"]` and `"prompt_text_token_count": PREFILL_LENGTH`. Both values already exist in memory from the pin load (generate_configs.py:1131-1134, 1138) — no tokenizer, no model. Because `build_tree`'s `declared_identity.workload_profile` is `**workload_for(...)` (generate_configs.py:2666-2675), the declaration follows automatically; because the fields are omission-serialized, decode arms need nothing. Same hash for both arms is correct: the ids list is shared by construction (generate_configs.py:1091) under an enforced shared `tokenizer.json` (generate_configs.py:1016-1022). The *realized* side is still per-bundle, so arm B is checked with its own tokenizer object regardless — no separate registration needed.

### Layer 1 — first catcher, before any joule: identity-pin projection

The projection already loads model + tokenizer on the collection machine, at freeze **and** again at arm-time re-verification (identity_pins.py:1399-1400 via `_runtime_probe_metadata` :1251-1327; re-derive at :2007). Two small changes:

1. `MLXRuntime.identity_projection_metadata` (mlx_runtime.py:315-340): when `config.workload_profile.prompt_text_token_ids_sha256 is not None`, add `"prompt": prompt_provenance(*self._prompt_for_workload(config)[1:2], text=prompt_text)` — i.e. the realized ids hash + `realized_token_count`. Emit only under that condition so legacy packs' `probe_metadata` bytes (→ `projection_input_sha256`, identity_pins.py:1515-1534) are unchanged and v3's frozen receipt still re-verifies.
2. `_derive_projection_units` (identity_pins.py:1432-1465): add `"prompt_realization"` to `identity_checks` (`{sha, count}` from `workload["prompt"]`) and to `expected_checks` (from `declared["workload_profile"]`), only when the declaration carries the fields. Mismatch falls into the existing refusal `readiness_identity_environment_dirty` — "runtime probe differs from pack declaration" (identity_pins.py:1486-1497), which is literally what happened. No new reason code; `observed` already dumps `identity_checks`.

This catches desk→freeze drift at `freeze_projection` and freeze→arm drift at `verify_frozen_projection` — both before decode block 1 runs. Owning modules: `mlx_runtime.py` (emit), `identity_pins.py` (compare).

### Layer 2 — during the night: `scripts/run_campaign.py`

- `ConfigInfo` (run_campaign.py:236-247) gains `prompt_text_token_ids_sha256`, `prompt_text_token_count`, read in `load_config_info` (:1145-1210) from the raw JSON like the sidecar/suite refs.
- New `check_prompt_realization_for_bundle(bundle_dir, info) -> PromptHashCheck`, dispatched **first** in `check_prompt_hashes_for_config_bundle` (:2692-2710) when `info.prompt_text_token_ids_sha256 is not None`. Compares `metadata.json → workload_provenance.prompt.token_ids_sha256` and `.realized_token_count` (written at mlx_runtime.py:401 from controller.py:2198) to the config values.
  - absent/malformed provenance → status `error` (existing flag `prompt_hash_check_error`, :366-367);
  - mismatch → **new status `realization_mismatch` → new flag `prompt_realization_mismatch`** from `collection_integrity_flags()` (:363-369). Any flag makes `usable` False (:437-441) and `failed` True (:461-462); the runner counts it and `--max-failures 1` (generate_configs.py:2093-2094; loop at run_campaign.py:8811) breaks. Do **not** add the flag to `VALID_WAIVER_SCOPES` (:627-636): it is then unwaivable except by scope `any`, which is the fail-closed shape D-161 asks for on evidence defects.
- The `end_metadata.prompt_tokens` marker is the same in-process `len(prompt_token_ids)` as the provenance count (mlx_runtime.py:702, 708, 733 vs provenance.py:320 on the same list, :401), so a second read from `events.jsonl` adds nothing; leave `envelope_gate` E4 untouched.

### Layer 3 — at consumption: `joulewise/analysis_engine/inputs.py`

Extend the non-suite branch of `_realized_identity_matches_config` (inputs.py:2604-2608): when `workload_config` carries the two fields, also require `workload["prompt"]["token_ids_sha256"]` and `["realized_token_count"]` to equal them. A False already yields `config_hash_mismatch` exclusion (inputs.py:2772-2773). This is the exact-shape seat ("config ↔ realized identity"); it reads only the bundle's own `config.json` (manifest-bound by `config_sha256`, analysis_manifest_v3.py:918-928) and `metadata.json`. The family's `prompt_tokens` (generate_configs.py:1429) binds transitively through a desk equality test (below), not through runtime code in `floor_extraction`.

### Why the alternatives lose

- **Expected hash in the condition family**: v1 workload keys are a closed set (floor_extraction.py:724-730, 753-768) → v3 family schema in a gauntlet module, every `condition_family_sha256` moves and the manifest cell keys bind it (analysis_manifest_v3.py:3126, 3294, 3320). A family is not reachable from a bundle without a manifest join. Fails (3) and (4).
- **Adapter refusing at `_prompt_for_workload`**: that call runs inside the measured tokenize window by design (mlx_runtime.py:374-385, 697-701) — no non-workload compute there. The pre-measurement seat would be `warmup` (:351, after idle baseline, controller.py:1206 → telemetry starts :1229), which needs a value in the closed `FailureReason` enum (schemas.py:261-271) and only saves ~one measured window over Layer 2. Layer 1 is earlier and free.
- **Sidecar via `generator_sidecar_ref`** → `prefill_prompt_candidate.json`: `check_prompt_hashes_for_bundle` refuses anything without `items` (run_campaign.py:2596-2605) and pairs on suite manifests; analysis would need an out-of-bundle join; the adapter never sees it. Config carriage makes the bundle self-checking.

## Blast radius

| Module | Change | Notes |
|---|---|---|
| `joulewise/schemas.py` | 2 optional fields, pair/requires rules, allowlist, JSON schema, omission-serialize | Legacy bytes unchanged — pin with a golden-bytes test |
| `configs/campaigns/d117_contrast_v5/generate_configs.py` | 2 lines in `workload_for` | v5 pack not yet emitted/frozen (`configs/campaigns/d117_contrast_v5/` holds only the generator) |
| `joulewise/adapters/mlx_runtime.py` | conditional `prompt` key in projection probe | Legacy configs → byte-identical probe |
| `joulewise/identity_pins.py` | ~8 lines in `_derive_projection_units`; reuses `readiness_identity_environment_dirty` | Arm-critical (D-131) → council trigger by rule 3, but no vocabulary change |
| `scripts/run_campaign.py` | 2 `ConfigInfo` fields, one new check fn, one status/flag | Existing `PromptHashCheck` log shape |
| `joulewise/analysis_engine/inputs.py` | ~6 lines in one boolean | Existing reason code |
| Untouched | `floor_extraction.py`, `analysis_manifest_v3.py`, `cli.py`, `bundle_read.py`, `envelope_gate.py`, `controller.py`, retained corpora, `draft-v1.md` | |

## Failure modes (honest drift, which layer catches first)

1. **Pin issuer encodes differently from the adapter** (issuer is unbuilt: trace 16 §3, and the adapter uses `add_special_tokens=True`, mlx_runtime.py:936, 1100-1102): Layer 1 fires at `freeze_projection` on the desk/collection machine — before any night. Not physics, but fail-closed and immediate.
2. **`mlx_lm`/`tokenizers` drift between pin day and freeze**: Layer 1 at freeze, `readiness_identity_environment_dirty`.
3. **Drift between freeze and arm**: Layer 1 at `verify_frozen_projection` (:2007-2020) — also trips `projection_input_sha256` because the probe bytes changed.
4. **Drift between arm and stage 03** (hours): Layer 1 blind → Layer 2 on the first prefill bundle → `failed` → night stops; decode stages 01/02 remain intact.
5. **Layer 2 bypassed** (`any` waiver, foreign evaluator): Layer 3 excludes with `config_hash_mismatch`; the prefill family loses members and the claim fails loudly downstream.
6. **Provenance absent** (mock adapter, older bundle) while config carries expectation: Layer 2 `error` → `prompt_hash_check_error`; Layer 3 False → excluded.
7. **Two model dirs with the same `tokenizer.json` but different `tokenizer_config.json`** (e.g. `add_bos_token`): pins cover only `tokenizer.json` bytes and the chat template (mlx_runtime.py:94-141); arm B's realized ids differ → caught per-bundle by Layer 2/3, and at Layer 1 because `B/prefill_p{L}` is its own identity unit (generate_configs.py:2636-2657).

## Tests

- `tests/test_schemas*`: pair rule, requires-`prompt_text`, hex/positive validation; golden-bytes `to_dict()` of a legacy config unchanged; JSON-schema/dataclass parity.
- `tests/test_d117_contrast_v5_pack.py`: prefill configs' sha == `prompt_candidate()["token_count_basis"]["per_model"][*]["token_ids_sha256"]` == pin sha; count == `PREFILL_LENGTH` == `prefill_family_definition(arm)["workload_profile"]["prompt_tokens"]`; decode configs omit both; `build_tree` declared `workload_profile` == `BenchmarkConfig.from_mapping(config).to_dict()["workload_profile"]` for every prefill config (the projection enforces this live at identity_pins.py:1376-1382 — fail it at the desk instead).
- `tests/test_mlx_runtime*`: probe emits `prompt` iff the field is present; hash equals `prompt_provenance(_encode(...))`; without the field the probe dict is byte-identical to today.
- `tests/test_identity_pins*`: stubbed probe matching → PASS; mismatched sha or count → `readiness_identity_environment_dirty` with `observed.identity.prompt_realization`; legacy declaration unaffected.
- `tests/test_run_campaign*`: fixture bundle → `matched`; mutated hash → `realization_mismatch`, flag `prompt_realization_mismatch`, `usable` False, `failed` True; waiver scope `prompt_hash_mismatch` does not clear it; loop with `--max-failures 1` breaks after that bundle; missing provenance → `error`.
- `tests/test_analysis_engine_inputs*`: `_realized_identity_matches_config` False/True on mismatch/match; suite branch unchanged.
- Drift simulation: fake tokenizer prepends one id → Layer 1 fires; with the projection stubbed to omit `prompt`, Layer 2 fires on the first prefill bundle.
- Mutation-kill: deleting the compare in any one layer must fail exactly that layer's test.

## Dissent

1. Sketch (a) as written does not work: unknown `workload_profile` keys are dropped and only warned about (schemas.py:844-879, 1009-1011), so nothing downstream would see them; `expected_prompt_tokens` is the wrong name because the fields qualify `prompt_text` and must respect the source-exclusivity rule.
2. Sketch (b) alone catches too late — after ten decode blocks. The identity-pin projection already holds the tokenizer at freeze and at arm; that is the first catcher, at near-zero cost, and the sketch omits it.
3. Sketch (c) aims at the two gauntlet modules; the exact-shape seat is `inputs.py:_realized_identity_matches_config` with an existing reason code. Family `prompt_tokens` stays a desk-tested invariant.
4. Do not overload `prompt_hash_mismatch` — it is a named waiver scope (run_campaign.py:635). A distinct, unwaivable flag is the D-161 shape.
5. The larger risk is upstream of this check: the pin issuer does not exist, and the registered ids are only as good as the encode that produced them. Spec the issuer to obtain ids from the real MLX adapter's `_prompt_for_workload` path (or export a public `encode_prompt_text` helper), and run `freeze_projection` immediately after issuing the pin so Layer 1 validates the pin on the collection stack before the night is scheduled.
6. `text_sha256` in provenance is redundant with the byte-bound `config.json`; do not compare it.
