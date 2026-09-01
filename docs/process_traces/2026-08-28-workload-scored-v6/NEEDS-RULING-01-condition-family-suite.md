# NEEDS-RULING-01 — a suite workload cannot be named by the frozen condition-family schema (WORKLOAD-SCORED-01, unit 4)

Filed 2026-08-28 by the WORKLOAD-SCORED-01 director. Desk finding; nothing was
hacked around. The `_v6` scored leg (D-166 R-3) needs floor cells and an
analysis-manifest arm whose workload is *a suite manifest*, not a
(prompt_tokens, output_tokens) pair. Two frozen contracts refuse that today.

## Obstacle 1 — condition-family workload profile is integer-only

`joulewise/floor_extraction.py:712-718` fixes the exact key set
`{name, prompt_tokens, output_tokens, repetitions, warmup_runs}` and
`:795-810` requires each of the four numeric keys to be a positive integer.
`CONDITION_FAMILY_DEFINITION_SCHEMA_VERSION = "joulewise.condition_family_definition.v1"`
(`:148`). Every floor cell binds one such definition per arm
(`_validate_spec_condition_family`, `:869-935`), e.g.
`configs/campaigns/d117_floor_qwen25_1p5b_v3/condition_families/condition_family_df_ph_decode.json`
(`prompt_tokens: 128, output_tokens: 512`).

A GSM8K k=8 suite has eight *different* realized prompt lengths and
`output_policy: natural_eos` under a cap; the run-level config already
represents this correctly — `config.workload_profile` for a suite bundle is
`{prompt_tokens: null, output_tokens: null, suite_manifest_ref, suite_manifest_sha256, repetitions, warmup_runs}`
(`runs_recal_20260718/p2015-df-su-sentinel-abs-r05/config.json`; authenticated in
`joulewise/controller.py:635-687`). The floor-cell side has no such branch.

## Obstacle 2 — analysis-engine identity check compares a null against a sum

`joulewise/analysis_engine/inputs.py:2590`:
`output_policy.get("requested_tokens") == workload_config.get("output_tokens")`.
For a suite bundle `metadata.workload_provenance.output_policy.requested_tokens`
is the *suite total* (1280 for the 5-item sentinel bundle above) while the
config's `output_tokens` is `null`, so `_realized_identity_matches_config`
returns False and the bundle is excluded before any floor/contrast logic runs.
Under `natural_eos` the suite total requested is still fixed by design
(8 × 384 = 3072) but emitted varies — the identity that should be pinned is
the suite manifest hash plus per-item planned budgets, not a scalar.

## What is NOT being asked

- No change to `_v5` (D-166 R-1/R-2): the `_v5` decode/prefill arms stay on
  the forced-budget, integer-shape path.
- No relaxation of D-041 (P2-022/P2-023 remain BLOCKED as written; the `_v6`
  leg is ruled by D-166 R-3, which is the AP row/authority for `benchmark_import`
  being un-deferred on the *suite manifest* — that un-deferral does not touch
  the condition-family contract and is done in this stream).

## Proposed minimal amendment (for the magistrate to rule; not implemented)

1. New `joulewise.condition_family_definition.v2` (v1 stays valid and
   byte-stable; existing `condition_family_sha256` values do not move):
   `workload_profile` gains an exact alternative key set
   `{name, suite_manifest_sha256, suite_item_count, output_cap_tokens, output_policy, repetitions, warmup_runs}`
   with `suite_manifest_sha256` a 64-hex digest, `suite_item_count` and
   `output_cap_tokens` positive integers, `output_policy ∈ {fixed_budget_exact, natural_eos}`.
   Validator rule: a definition carries EITHER the v1 integer pair OR the
   suite set, never both; the schema_version string selects which.
   Files: `floor_extraction.py:148-150, 712-718, 795-810` (+ the
   `condition_family_sha256` canonicalisation must include the new keys).
2. `inputs.py:2590`: when `workload_config.suite_manifest_sha256` is present,
   the identity test becomes
   `metadata.workload_provenance.suite.manifest_sha256 == workload_config.suite_manifest_sha256`
   AND `requested_tokens == suite_item_count × output_cap_tokens`; the scalar
   comparison is kept unchanged for non-suite configs.
3. The `_v6` calibration plan / analysis manifest sibling (S15's
   `analysis_manifest_v5` family or its `_v6` sibling) then names the cell as
   `(model, suite_manifest_sha256)`; the floor-cell metric stays
   `phase_energy_j.decode` (suite-total decode phase via multi-interval pairing,
   `reduce.py:2643-2647`), consistent with the Fable seat's registered
   quantity 1.

Ruling needed on (a) v2-vs-extend-v1, (b) whether the identity fix in
`inputs.py` is a `_v6`-only branch or a general one, (c) who owns the
analysis-manifest sibling for `_v6` (S15 currently owns `_v5` only).
Until ruled, this stream ships the producer, scorer, profiles and the
determinism check; no floor cell or manifest arm for `_v6` is created.
