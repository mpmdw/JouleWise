# L9 ruling addendum: cold passes and silly-numbers review dispositioned (lead, activation 6cff3515, 2026-10-20)

Amends `docs/process_traces/2026-10-20-magistrate-4b350f47/L9-RULING.md` (main 0ae81071e). Where they differ, this wins.

Inputs, all on JouleWise-data, all executing on synthetic fixtures and tracked sealed config only (no real-window value):
- Cold Fable 5.1, `claude/l9-ruling-cold-fable` 22d1cc7, `reports/l9-ruling-cold/fable.md`: ACCEPT WITH CHANGES on all four.
- Cold Opus 5.5, `claude/l9-ruling-cold-opus-p52emy` 5437f4a, `reports/l9-ruling-cold/opus.md` (+ `opus-probes/`): ACCEPT WITH
  CHANGES on all four.
- Executing review of `lane/2026-10-20-l9-silly-numbers` 090a398bb, Opus 5.5, `claude/l9-silly-review-wcjrz5` e88d85a,
  `reports/l9-silly-review/REPORT.md`: no blocker; 2 medium, 5 nits.

Neither cold seat refused. Every change below either keeps a refusal that guards an inapplicable number, or carries a
limitation to where it prints. No registered arithmetic, threshold, exclusion or kept-unit count changes.

## C. Common: limitations reach the fill (both seats)

Today `inputs.limitations` stops at the claim verdict; `grep limitations` over the fill path is empty. The fill builder
copies each contrast's limitations and its floor source cell id from the verdict into the fill input, and the existing
`results_fill_contrast_census_mismatch` / `results_fill_floor_mismatch` checks compare them (exact list and string equality).
Every limitation string names its scope (`:<family>`, `:<plan_id>`, `:<cell_id>` suffixes are mandatory).

## R. Q-RENDERER

1. The note is one registered string `results_rendering_not_run_no_block5_template` added to `FLAGS`
   (`joulewise/b5_analysis/dry_run.py` near 203), not a new record key (Opus; `StepRecord` stays closed).
2. R3's step-11 subtest moves to `results-fill-input.json`; T20 asserts no renderer capture and no `outputs/results-fills.md`.
3. Declared deviation, appended to `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md` as the text in §S below
   (Opus). A Results renderer written after release must print every row of the validated fill input's contrast census,
   with its issued status, so no number is selected after the data are seen.

## L. Q-LINEAGE

1. The null-entry rule applies only to the aggregate call (`_common_minted_artifact_launch_lineage` reached near 3455).
   The per-producer call (near 3385-3388) still raises on a split producer and on mixed marker/legacy provenance within
   one producer. Test both (Opus cases 4 and 5).
2. `validate_claim_verdicts` (`analysis_engine/artifact.py` near 1080-1092) re-derives the limitations from
   `authenticate_floor_artifact_bytes` and compares them with the verdict's `inputs.limitations` by exact list equality;
   a verdict that drops `floor_launch_lineage_unauthenticated:*` fails validation (Fable).

## E. Q-EXACTSTACK

1. On the group-served route, the request-side equality `binding.cell_scientific_identity_sha256[cell] == consumer
   scientific identity` (`inputs.py` near 4686-4700) is replaced by: family admission (id and sha256) plus stack identity
   (eleven fields incl. `model_artifact_sha256`). The request is the exact request (`consumer_stress={}`). Both seats
   executed it: the floor pack's and contrast pack's identity units are disjoint, so keeping the equality refuses every
   GAMMA arm.
2. "Phase and length match" names its sources: phase is `measurement_target.metric`, length is
   `workload_profile.prompt_tokens` / `output_tokens` of the two condition-family definitions, each authenticated by its
   `condition_family_sha256`, compared exactly (Opus).
3. Status `exact` makes no stress-envelope comparison; that is what sealed `exact_stack_only.v1` registers. The
   limitation text says so: `floor_cell_from_floor_pack:<F>:<cell_id>:no_envelope_comparison` (Fable).

## I. Q-CONSUMERID (seats split; lead's call)

Fable: the `unauthenticated` flag hides no wrong number because `_read_bundle` (`inputs.py` near 3214-3240) excludes a
bundle whose config.json bytes or typed config differ from the sealed plan's source config (`config_hash_mismatch`) before
any floor request. Opus executed `_floor_request_or_refusal` directly and showed that, without the subset test, an arm
differing in workload or phase reaches a `FloorRequest`; Opus accepts the flag if a named replacement check binds each arm's
workload and phase to the sealed registration, with a test. Both are right about their own probe. Decision:

1. The justification is the `config_hash_mismatch` binding, not "the floor match on scientific identity". The seat first
   writes the pinning test: one bundle per variant (workload `suite_manifest_sha256`, `output_tokens`, `measurement-arm`
   tag, `df-condition` tag, `decode-prompt` tag) whose config differs from the plan's source config, driven through the
   real `_read_bundle` path, each excluded as `config_hash_mismatch` before `_floor_request_or_refusal` is reached.
2. If every variant is excluded, `consumer_identity_set_unauthenticated:<family>` is a limitation as ruled. If any variant
   reaches the floor request, `consumer_identity_set_unauthenticated` stays a refusal (Opus's change 1) and the seat
   reports which variant got through.
3. `consumer_identity_recording_difference:<family>` is built from a closed allowlist (Opus): a difference is a recording
   difference only if it lies wholly in fields named one by one in code, each with the reason it cannot reach a
   measurement (start: `hardware_target.notes`, `run_metadata.project`, `run_metadata.operator`). Every `run_metadata.tags`
   entry and every other field refuses `consumer_identity_undeclared`.
4. When the declaration is unauthenticated and the arm carries more than one consumer identity, `consumer_identity` is None
   and no exact match forms: this refuses, never falls to transport (Fable); test it.

## Z. Silly-numbers review findings

- M1 (bar below the project's lower edge above S of about 1e4 J): the zero-point predicate becomes
  `math.isclose(a, b, rel_tol=0.0, abs_tol=max(1e-6, 1e6 * 2**-53 * S))`. Derivation (comment beside it): 1e-6 J is the
  project's absolute agreement bar; 1e6 times the float noise of a value of size S (u = 2**-53) is the band's lower edge;
  at production S (at most about 2.5e6 J in the replay) the bar is at most 2.8e-4 J, so a 1e-3 J divergence is caught
  up to S of about 9e6 J and the bar stays under 1% of the ~1 J attribution limit up to S of about 9e7 J. `rel_tol` is
  dropped: S includes |zero point|, so the absolute term already scales with it (N1 resolved).
- M2: `scripts/floor_mint_pinsets/schema_v2.json` loses the `not const "7.377086"` clause (review diff P2). Check the
  schema-structure tests first.
- N5: each changed test bar gets a one-line derivation comment (values from the review's table).
- N2, N3, N4: no change (recorded; N4's mismatch is re-derived and recorded at mint).
- `tests/test_r4_acceptance_oracle.py`: the ten subtests that place a divergence just past the retired 1e-12 band are
  rewritten to place it just past the new predicate's bar; a gross divergence (well above the bar) still refuses.

## S. Text appended to the block-5 seal record

> **Declared deviation (2026-10-20, lead activation 6cff3515; L9 ruling Q-RENDERER).** Plan §3 row 11 names
> `render_results_fills.py --validate-rendered` with output "validated Markdown". The block-5 dry run ends step 11 at the
> validated fill input (`results-fill-input.json`); the renderer is not run, because the only renderer is the retired
> Window-A template, and its step record carries `results_rendering_not_run_no_block5_template`. No registered arithmetic
> changes. Obligation fixed now, before release: any block-5 Results renderer written after release prints every row of
> the validated fill input's contrast census with its issued status (unsupported and refused included), selects none, and
> its validator checks row-for-row correspondence with the fill input. It passes the Results cold gate before any number
> it prints is used.
