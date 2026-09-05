# D-166 prompt-0 dependency census

Status: **NEEDS_SCOPE — Phase 2 must not start.**

This is the mandatory pre-edit census for the ratified Q-17-4 amendment. It
was made at requested head `92350cadb4d7cfe0429175d95386ce4c322b83cf` on
branch `feat/2026-09-05-d166-prompt0`, before changing the generator. The
binding rule is ruling 17 §B as replaced by the ratified Q-17-4 text in Git
object `ff82e0dd:docs/process_traces/2026-09-04-peer-audit/43-magistrate-synthesis-gate-17.md`:
every decode block in both model arms uses prompt index 0 of
`real_prompts_v1`; the floor packs and G2-a prefill pin do not change; every
derived identity, digest, projection, custody pin, `expected_pack_paths()`
object, and clone proof must be prospectively superseded before collection.

Exhaustive repository write scope for this seat:

- `configs/campaigns/d117_contrast_v5/**`
- `docs/process_traces/2026-09-05-d166-prompt0/**`

`IN SCOPE` and `OUTSIDE WRITE_SCOPE` below refer only to repository writes.
Read-only inputs and throwaway custody outside the repository are still named
so the digest graph is complete.

## Dependency graph

`decode_prompt_index(block)` currently selects `(block - 1) mod 8`. That value
enters `build_runs()` and `ordered_blocks()`, selects each decode suite
manifest in `config_for()`, and determines the declared suite-manifest census.
Those bytes flow through the following graph:

```text
assignment rule + selected prompt rendering
  -> decode workload registration + suite manifests + decode configs
  -> calibration plan + per-stage/root order manifests
  -> prospective analysis manifest + analysis-semantics projection/digest/id
  -> plan tree + identity-unit config inventories + plan/tree root hashes
  -> identity-pin projection receipt and frozen plan tree
  -> readiness evidence/freeze receipt and pack digest
  -> family marker + successor histsem pinset + step-6 confirmation
  -> arm-verification custody receipts and clone-proof record
```

The frozen floor generators at
`configs/campaigns/d117_floor_qwen3-1p7b_v5/` and
`configs/campaigns/d117_floor_qwen3-8b_v5/`, and the G2-a prefill pin bundle,
are inputs only. Q-17-4 requires no edit to them.

## Artifact census

| Artifact / exact path | Producer and prompt-selection dependency | Scope |
|---|---|---|
| `configs/campaigns/d117_contrast_v5/generate_configs.py` | Hand-authored generator. Owns `decode_prompt_index`, the assignment objects, suite census, configs, and all transitive hashes. | **IN SCOPE** |
| `configs/campaigns/d117_contrast_v5/d166_decode_prompt_assignment_supersession.json` (proposed new record) | Phase-2 hand-authored prospective record. It must name `d166_block_prompt_cycle.v1` as superseded, name the new fixed-zero rule, carry this census, and precede collection. | **IN SCOPE** |
| `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/**` | `_generate()` / `generate()` in the source generator. The production pack is absent at this head. The configured pack root is a D-138 successor identity (`target_ordinal == 5 >= 2`) and binds `SUCCESSOR_ACCEPTANCE`; it must be newly generated, never substituted by rewriting an earlier frozen pack. Every closed-inventory object is enumerated below. | **OUTSIDE WRITE_SCOPE** |
| `tests/test_d117_contrast_v5_pack.py` | Contrast-generator test module. The required new regression belongs here beside the existing rotation/census tests. It must assert prompt index 0 for all ten decode blocks and both arms, plus the old rule ID in the supersession record. | **OUTSIDE WRITE_SCOPE** |
| `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/identity_pin_projection.receipts/projection-0001.json` and `.sha256`; the frozen rewrite of `plan_tree.json` and `plan_tree.sha256` | `scripts/project_identity_pins.py` -> `joulewise.identity_pins.freeze_projection()`. The receipt hashes the ordered identity units, raw config inventory, authenticated suite manifests, prompt realizations, config-set identities, and runtime/stack pins. A fresh pack starts at receipt ordinal 0001. | **OUTSIDE WRITE_SCOPE** |
| `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.sources/{acceptance-owner,doctrine-pin,estimator-identity,mint-trust,multicell-mint,pack-authentication,pack-family,reason-code-coverage,receipt-oracle,recovery-ledger-test,three-window-regression}.json` | `scripts/author_arm_readiness_evidence.py` -> `joulewise.arm_readiness_evidence.author_arm_readiness_evidence()`. Source rows bind the newly generated pack coordinate and are inputs to the evidence receipts. | **OUTSIDE WRITE_SCOPE** |
| Same pack root under `arm_readiness.evidence/evidence-{acceptance-owner,doctrine-pin,estimator-identity,mint-trust,multicell-mint,pack-authentication,pack-family,reason-code-coverage,receipt-oracle,recovery-ledger-test,three-window-regression}.json` and each adjacent `.sha256` | Same authoring path. These receipts bind the pack/config/plan hashes used at readiness freeze. | **OUTSIDE WRITE_SCOPE** |
| Same pack root under `arm_readiness.freeze.receipts/freeze-NNNN.json` and `.sha256` (the current v5 registry declares `freeze-0004`) | `scripts/generate_arm_readiness.py freeze` -> `joulewise.arm_readiness.generate_freeze_receipt()`. Its pack identity includes the generated pack digest, plan ID/SHA, evidence set, and identity-projection receipt. | **OUTSIDE WRITE_SCOPE** |
| `<window_custody_root>/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/receipts/<bracket_session_id>/identity-pin-arm-verify.json` and `.sha256` | `joulewise.identity_pins.verify_frozen_projection()`. Re-derives and compares the projection at arm time. | **OUTSIDE repository / OUTSIDE WRITE_SCOPE** |
| `<window_custody_root>/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/{arm_readiness.t0.inputs,arm_readiness.t0.receipts,arm_readiness.receipts,arm_readiness.consumptions}/**` | `scripts/capture_t0_step.py`, `scripts/generate_arm_readiness.py`, and `scripts/launch_window.py`. These records carry the pack ID/digest, freeze receipt, plan coordinate, and launch lineage, so a regenerated pack requires fresh custody. | **OUTSIDE repository / OUTSIDE WRITE_SCOPE** |
| `<family_publication_custody>/d117_family_publication_v5.json` and `.sha256` | `scripts/build_family_marker.py` -> `joulewise.arm_readiness.build_family_publication_marker()`. The GAMMA member contains the prompt-dependent pack SHA and freeze-receipt SHA. | **OUTSIDE repository / OUTSIDE WRITE_SCOPE** |
| `configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json` | `scripts/build_v4_histsem_pinset.py`. Its GAMMA row carries current/historical pack SHA, plan SHA, plan-tree SHA, freeze receipt, and evidence receipts. It is absent at this head but is required by the v5 family publication/clone chain. The producer returns its SHA in stdout; this artifact has no tracked sidecar. | **OUTSIDE WRITE_SCOPE** |
| `<family_publication_custody>/d117_step6_confirmation_table_v5.json` and `.sha256`, plus out-of-band `hC` | Magistrate exact-byte confirmation under `docs/contracts/d117_step6_confirmation_table.md`. The table binds the family marker digest `hM` and successor-pinset digest `hS`; its GAMMA member repeats the prompt-dependent pack and freeze-receipt digests. `hC` remains outside every repository allowlist. | **OUTSIDE repository / OUTSIDE WRITE_SCOPE** |
| Throwaway estate-12 clone: `$CLONE/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/**`; `$CUSTODY/{estate-12-anchor-map.json,estate-12-anchor-spec.json,transcripts/**}`; clone-local identity/readiness/family/confirmation receipts | `docs/process_traces/2026-08-30-t28-estate11/estate-12-delta-template.md`, `scripts/derive_estate_anchors.py`, the contrast generator/checker, identity projection, readiness freeze/arm, marker, histsem, and confirmation tools. It must run from a fresh full clone at the reviewed cut and prove the newly generated bytes; no measurement checkout is involved. | **OUTSIDE repository / OUTSIDE WRITE_SCOPE** |
| `docs/process_traces/2026-09-05-d166-prompt0/02-seat-report.md` and any clone-proof transcript/digest record placed under this trace directory | This seat's report/clone-proof record. It may record external throwaway evidence but cannot stand in for the out-of-scope production pack, test, pinset, or custody objects. | **IN SCOPE**, but blocked |

## Exact `expected_pack_paths()` pack-level set

At this pre-edit head, after configuring Qwen3-1.7B vs Qwen3-8B and a selected
prefill length `P`, `expected_pack_paths()` contains exactly **115 files**.
All resolve below the absent production root
`configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/`, which is outside
the write scope.

Top-level objects (11), all produced by `_generate()`:

1. `README.md`
2. `calibration_plan.json`
3. `calibration_plan.sha256`
4. `order_manifest.json`
5. `plan_tree.json`
6. `plan_tree.sha256`
7. `analysis_manifest_v3.json`
8. `consumer_family_declaration.json`
9. `decode_workload_candidate.json`
10. `prefill_prompt_candidate.json`
11. `generate_configs.py`

Condition-family objects (4), produced by `build_condition_families()`:

- `condition_families/condition_family_sw_decode_a_qwen3-1p7b.json`
- `condition_families/condition_family_sw_decode_b_qwen3-8b.json`
- `condition_families/condition_family_sw_prefill_pP_a_qwen3-1p7b.json`
- `condition_families/condition_family_sw_prefill_pP_b_qwen3-8b.json`

Decode suite manifests (16), produced by `decode_suite_manifest()` and written
by `_generate()`: for each model directory `qwen3-1p7b` and `qwen3-8b`,

- `decode_prompt_manifests/<model>/01_sky_color.json`
- `decode_prompt_manifests/<model>/02_weather_climate.json`
- `decode_prompt_manifests/<model>/03_kyoto_itinerary.json`
- `decode_prompt_manifests/<model>/04_interest_math.json`
- `decode_prompt_manifests/<model>/05_plant_diagnosis.json`
- `decode_prompt_manifests/<model>/06_web_request.json`
- `decode_prompt_manifests/<model>/07_falsifiability.json`
- `decode_prompt_manifests/<model>/08_pantry_dinner.json`

The fixed-zero implementation must recompute the closed manifest census. If
the amended `expected_pack_paths()` retains zero-use manifests, their zero-use
status must validate; if the closed inventory narrows to prompt 0, the attached
generated inventory must explicitly supersede these 16 current paths. The
eight-prompt workload/profile and rendering pinset remain authenticated inputs
either way; only collection assignment changes.

Per-stage order manifests (4), produced in `_generate()`:

- `01_decode_contrast_blocks_01_05/order_manifest.json`
- `02_decode_contrast_blocks_06_10/order_manifest.json`
- `03_prefill_pP_contrast_blocks_01_05/order_manifest.json`
- `04_prefill_pP_contrast_blocks_06_10/order_manifest.json`

Run configurations (80), produced by `config_for()` and `_generate()`:

- 40 decode configs: for `b01` through `b05` under stage `01`, and `b06`
  through `b10` under stage `02`, every block has suffixes `a1`, `b1`, `b2`,
  `a2` and filename
  `d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-bNN-<suffix>.json`.
- 40 prefill configs: the same ten blocks and four suffixes under stages `03`
  and `04`, with filename
  `d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-pP-contrast-bNN-<suffix>.json`.

The 40 decode configs change directly because their suite reference/digest and
`decode-prompt=` tag are selected by the rule. The calibration plan records all
ten fixed assignments. Stage/root manifests carry each config SHA. The
analysis manifest carries the plan SHA, root/stage manifest SHAs, all 80 config
SHAs, its calculated manifest ID, and the result of
`analysis_semantics_projection_v1`. The plan tree carries the generator SHA,
plan/analysis/decode-workload SHAs, config inventories, and root science
entries. `calibration_plan.sha256` and `plan_tree.sha256` are their root-hash
sidecars. Because D-138 requires a prospective successor identity and the
generator is embedded/threaded into that identity, the superseded set is the
entire 115-file closed inventory, not only the directly changed decode files.

## Scope ruling

Phase 2 requires repository writes outside the exhaustive allowlist. The
minimum immediate expansion is:

1. `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/**` — generated
   successor pack, plan/tree root hashes, identity projection, readiness
   evidence, and freeze pins;
2. `tests/test_d117_contrast_v5_pack.py` — required fixed-zero and superseded
   rule-ID regression;
3. `configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json` —
   successor/clone-proof pinset once the three-pack estate reaches that gate.

External custody remains outside the repository and must be freshly created by
the named tools; it is not a request to widen repository scope. No production
pack, test, pinset, custody artifact, generator byte, or Phase-2 report was
changed in this seat.
