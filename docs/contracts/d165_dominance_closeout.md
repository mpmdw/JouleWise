# D-165 dominance replay and close-out contract

Status: stage-1 contract, 2026-09-01. The two JSON schemas are
`joulewise.d165_dominance_replay.v1` and
`joulewise.d165_dominance_closeout.v1`.

This document defines every field that stage 1 reads or writes. A **cell** is
one model and one phase, for example the small model's decode phase. Each cell
has an **absolute component**, which measures repeated-run scatter within one
condition, and a **comparative component**, which measures A/B/B/A blocks. An
**A/B/B/A block** is four measurements ordered A1, B1, B2, A2; that order lets
the comparative estimator cancel a slow linear drift.

An **ordinary dominance ratio**, written R, divides the corner-widened
unguarded floor by the point unguarded floor. A **corner** selects an allowed
low or high endpoint for every uncertainty. “Unguarded” means the small-sample
safety multiplier has not been applied. The registered predicate is R >= 2.0;
exact equality passes.

A **common-mode error** is one timing-edge error whose sign is shared by every
comparative block. Each block also has a **local error**, whose sign is allowed
to vary independently. The comparative common-mode ratio, written R_cm,
replays one shared sign and all combinations of local signs. There is no
absolute R_cm: a uniform shared shift cancels when the absolute estimator
subtracts its mean. Absolute R_cm is therefore the text value
`not_applicable`, never a number.

## Shared arithmetic

`joulewise.dominance_closeout.dominance_ratio` is the only production
implementation of R >= 2.0. It accepts the numerator
`corner_widened_unguarded_floor_j` and denominator
`point_unguarded_floor_j`. Both are finite, nonnegative numbers in joules. A
zero denominator raises `dominance_ratio_zero_denominator`; infinity and
not-a-number values are never emitted.

`joulewise.dominance_closeout.split_common_mode_block_width` is the only
production implementation that separates one comparative block's uncertainty
into `shared_width_j` and `local_width_j`. The calculation is the arithmetic
formerly written inside
`joulewise.floor_extraction._common_mode_block_half_width`: the same
`math.fsum`, extrema padding, four-step outward rounding, and residual sum are
preserved. Governed extraction calls the shared split and then performs its
unchanged outward-rounded final sum. Thus existing aggregate floors keep the
same meaning and bits while the two terms become available to the sidecar.

`joulewise.dominance_closeout.replay_common_mode_dominance` authenticates the
shared-edge bound, validates every four-member window, calculates every split,
holds one shared sign across the blocks, enumerates every local-sign
combination, and calls the existing comparative false-effect floor. A
false-effect floor is the smallest energy difference the registered noise
calculation can distinguish from zero. The supplied shared-edge bound must
match the authenticated bound with zero relative tolerance and an absolute
tolerance of exactly `1e-12` seconds. The exact-corner cap is exactly 16 blocks:
the implementation reads `MAX_EXACT_ADMISSIBLE_CORNER_N`, whose registered
value is 16, and rejects 17 or more.

For an ordinary point floor, the close-out builder calls
`joulewise.detection_floor._point_floor_diagnostic` on the floor artifact's
unconditional parents. It does not copy that function's maximum calculation.
The absolute parent is `max_abs_residual_j`; the comparative parent is
`max_abs_delta_j`; both use `prediction_component_j` as the other input.

## Replay sidecar: `joulewise.d165_dominance_replay.v1`

The sidecar is a JSON object with exactly these top-level fields:

| Field | Type | Meaning and producer |
|---|---|---|
| `schema_version` | string | Exact value `joulewise.d165_dominance_replay.v1`; the stage-2 mint writes it. |
| `sidecar_id` | nonempty string | Mint-issued identity for this replay sidecar. |
| `cells` | nonempty array of cell objects | One record for each cell emitted by the mint. The standalone validator permits a one-cell diagnostic sidecar; the close-out requires exactly the four floor cells. |

Each cell object has exactly `cell_id` (nonempty string), `absolute` (object),
and `comparative` (object). `cell_id` comes from the matching
`joulewise.detection_floor_artifact.v2` cell and must be unique.

### Independent ratio record

Both `absolute.independent` and `comparative.independent` have exactly these
fields:

| Field | Type | Unit | Meaning and source |
|---|---|---:|---|
| `status` | `complete` or `refused` | none | The stage-2 record builder sets `complete` after `dominance_ratio`; a zero point floor sets `refused`. |
| `ratio_id` | string | none | Exact value `attribution_dominance_ratio.v1`. |
| `point_unguarded_floor_j` | finite number | J | Produced through `_point_floor_diagnostic` from `max_abs_residual_j` plus `prediction_component_j` for absolute, or `max_abs_delta_j` plus `prediction_component_j` for comparative. |
| `corner_widened_unguarded_floor_j` | finite number | J | Copied from the matching floor-artifact component. |
| `ratio` | finite number or null | dimensionless | `dominance_ratio` output when complete; null when refused. “Dimensionless” means the joules in numerator and denominator cancel. |
| `threshold` | number | dimensionless | Exact value `2.0`. |
| `comparison` | string | none | Exact value `greater_than_or_equal`. |
| `passes` | Boolean or null | none | `ratio >= 2.0` when complete; null when refused. |
| `refusal_reason` | string or null | none | Null when complete; `dominance_ratio_zero_denominator` for the registered zero-denominator refusal. |

`absolute.common_mode` has exactly `status` and `reason`. `status` is
`not_applicable`. `reason` is the registered cancellation explanation returned
by `ABSOLUTE_COMMON_MODE_REASON`. No numeric R_cm field is allowed.

### Comparative common-mode replay

`comparative.common_mode_replay` has exactly `inputs` and `result`.
`inputs` has exactly:

| Field | Type | Unit | Meaning and evidence |
|---|---|---:|---|
| `calibration_bracket` | object | mixed, internally suffixed | The authenticated calibration-bracket object used by `registered_common_mode_operative_bound`; it comes from the cell's mint evidence. |
| `calibration_bracket_sha256` | 64-character lowercase hexadecimal string | none | SHA-256 of the bracket's canonical JSON. SHA-256 is a 256-bit content digest; canonical JSON means UTF-8 JSON with sorted object keys, no insignificant spaces, and no non-finite numbers. |
| `shared_edge_bound_s` | finite positive number | s | The once-widened operative shared timing-edge bound. `registered_common_mode_operative_bound(calibration_bracket)` must reproduce it within the registered absolute tolerance. |
| `blocks` | array, length 1 through `MAX_EXACT_ADMISSIBLE_CORNER_N` | none | Raw replay inputs reconstructed by extraction from the authenticated bundle evidence. |

Every block has exactly these fields:

| Field | Type | Unit | Producer and evidence |
|---|---|---:|---|
| `block_id` | nonempty string | none | The finalized manifest's comparative block identity. |
| `delta_j` | finite number | J | The zero-shift A/B/B/A contrast from the authenticated block evidence. |
| `onset_sweep_j` | nonempty array of finite numbers | J | Energy contrasts obtained by replaying the registered onset-shift grid. |
| `offset_sweep_j` | nonempty array of finite numbers | J | Energy contrasts obtained by replaying the registered offset-shift grid. |
| `zero_point_contrast_j` | finite number | J | The explicitly evaluated zero-shift contrast; it must belong to both sweep arrays and agree with `delta_j` inside the registered provenance tolerance. |
| `bundle_residual_half_widths_j` | array of exactly four finite nonnegative numbers | J | One local residual half-width for A1, B1, B2, and A2, reconstructed from their authenticated bundle evidence. |
| `member_window_bounds_s` | array of exactly four `[start_s, end_s]` pairs | s | The four member phase-window bounds reconstructed from events; every interval must remain strictly noncollapsed after applying the authenticated shared-edge bound. |
| `member_envelope_integral_sum_j` | finite nonnegative number | J | Sum of the four member envelope integrals reconstructed from their power traces and uncertainty evidence. |
| `derived_split` | object | none | Output of `split_common_mode_block_width`; it has exactly the two fields below. |

`derived_split.shared_width_j` and `derived_split.local_width_j` are finite
nonnegative numbers in joules. The first is the timing excursion held to one
sign across all blocks. The second is half the sum of the four bundle-local
residual widths and gets an independent sign in each block.

`result` has exactly:

| Field | Type | Unit | Producer |
|---|---|---:|---|
| `rule_id` | string | none | Exact value `d165_shared_sign_local_corner_replay.v1`. |
| `point_unguarded_floor_j` | finite nonnegative number | J | `replay_common_mode_dominance`, using the block deltas with zero added widths. |
| `common_mode_corner_widened_unguarded_floor_j` | finite nonnegative number | J | `replay_common_mode_dominance`, taking the maximum floor over the shared/local sign enumeration. |
| `ratio` | finite nonnegative number | dimensionless | `dominance_ratio` over the preceding two fields. |
| `threshold` | number | dimensionless | Exact value `2.0`. |
| `comparison` | string | none | Exact value `greater_than_or_equal`. |
| `passes` | Boolean | none | True exactly when `ratio >= 2.0`. |

`validate_d165_replay_sidecar` rejects missing or extra keys, duplicate cell
or block identities, non-finite numbers, a block count above the named cap,
incorrect derived splits, a bracket digest mismatch, an unauthenticated bound,
invalid member windows, or a stored result that differs from a fresh replay.

### Stage-2 mint interface

`joulewise.dominance_closeout.d165_replay_blocks_from_mint_inputs` is the only
sanctioned constructor for sidecar block records. It accepts exactly the three
values the mint holds at the call to
`floor_extraction._common_mode_floor_from_block_inputs`: the finalized block
identities, the block deltas in joules, and the extraction-owned
`_CommonModeBlockInputs` records:

```python
def d165_replay_blocks_from_mint_inputs(
    block_ids: Sequence[str],
    block_deltas_j: Sequence[float],
    block_inputs: Sequence[_CommonModeBlockInputs],
) -> list[dict[str, Any]]:
    ...
```

The adapter checks aligned lengths, unique nonempty block identities, the
16-block cap, and finite deltas. It copies the six fields held by each
`_CommonModeBlockInputs` record, adds `block_id` and `delta_j`, and computes
`derived_split` through `split_common_mode_block_width`. Stage 2 may wrap those
records with the cell's independent records, authenticated bracket, bound,
result, `schema_version`, and `sidecar_id`; it may not hand-build or rewrite a
block record. Sidecar emission itself remains a separate mint stream and does
not change the floor-artifact schema.

## Close-out: `joulewise.d165_dominance_closeout.v1`

The close-out is a JSON object with exactly these top-level fields:

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | string | Exact value `joulewise.d165_dominance_closeout.v1`. |
| `sources` | object | SHA-256 bindings for the finalized manifest, floor artifact, and replay sidecar. |
| `independent_ratios` | array of exactly eight records | Four cells times absolute and comparative components. |
| `comparative_common_mode_ratios` | array of exactly four records | One comparative R_cm slot for each cell; there are no absolute R_cm records. |
| `all_independent_pass` | Boolean or null | True only when all eight completed ordinary ratios pass; false when all complete and at least one fails; null on a stop. |
| `all_required_common_mode_pass` | Boolean or null | True only when all four completed comparative R_cm values pass; false when all complete and at least one fails; null on a stop. |
| `branch` | `A`, `B`, or null | Branch A, branch B, or neither branch after a stop. |
| `dominance_sentence_licensed` | Boolean | True only in branch A. “Licensed” means downstream prose is allowed to print the sentence. |
| `subtitle_licensed` | Boolean | True only in branch A. |
| `refusal_reason` | nonempty string or null | First deterministic stop reason, or null for branches A and B. |

`sources` has exactly `finalized_manifest`, `floor_artifact`, and
`replay_sidecar`. Each source reference has exactly:

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | string | The source's exact schema version. |
| `identity` | nonempty string | `manifest_id`, `artifact_id`, or `sidecar_id`, respectively. |
| `canonical_json_sha256` | 64-character lowercase hexadecimal string | SHA-256 of the complete source object's canonical JSON. `validate_d165_closeout` requires the three source objects and recomputes every digest. |

Every `independent_ratios[]` record is the sidecar independent-ratio record
plus `cell_id` and `component`. `component` is `absolute` or `comparative`.
The census must contain each of the four cell identities exactly twice, once
per component. The close-out builder reads the operands again from the floor
artifact rather than trusting the sidecar copy.

Every `comparative_common_mode_ratios[]` record has exactly:

| Field | Type | Unit | Meaning |
|---|---|---:|---|
| `cell_id` | nonempty string | none | Matching floor and sidecar cell. |
| `component` | string | none | Exact value `comparative`. |
| `status` | `complete` or `refused` | none | Whether the required replay result exists and is authenticated. |
| `ratio_id` | string | none | Exact value `attribution_dominance_ratio_common_mode.v1`. |
| `point_unguarded_floor_j` | finite number or null | J | Sidecar replay point floor when complete; null when refused. |
| `common_mode_corner_widened_unguarded_floor_j` | finite number or null | J | Sidecar common-mode corner floor when complete; null when refused. |
| `ratio` | finite number or null | dimensionless | R_cm when complete; null when refused. |
| `threshold` | number | dimensionless | Exact value `2.0`. |
| `comparison` | string | none | Exact value `greater_than_or_equal`. |
| `passes` | Boolean or null | none | `ratio >= 2.0` when complete; null when refused. |
| `refusal_reason` | string or null | none | Null when complete; a named stop reason when refused. |

## Branch and stop rules

Branch A requires all eight ordinary ratios and all four comparative R_cm
values to be complete and at least 2.0. Both prose licenses are true.

Branch B requires all twelve values to be complete and at least one value to
be below 2.0. Both prose licenses are false. A completed mix of passing and
failing cells therefore selects B, not a stop.

Neither branch is selected when a result cannot be truthfully completed. The
builder sets both `all_*_pass` fields and `branch` to null, both licenses to
false, and `refusal_reason` to the first deterministic reason. Stop conditions
are:

- a zero ordinary or comparative denominator;
- a missing, duplicate, or extra sidecar cell relative to the four floor
  cells;
- missing or extra schema keys;
- a non-finite physical value or ratio;
- a bracket digest mismatch or an unauthenticated shared-edge bound;
- a derived split or replay result that does not reproduce;
- any of the three close-out source identities or SHA-256 digests failing to
  match the supplied source object.

A floor artifact with other than four unique complete cells cannot support the
required eight-record ordinary census. The builder refuses to emit a close-out
at all; this is also a neither-branch stop, not branch B.

`validate_d165_closeout` rejects missing or extra keys, a census other than
eight ordinary plus four comparative common-mode records, non-finite completed
values, inconsistent ratios or pass flags, incorrect branch fields, source
operand/result drift, or a source-hash mismatch. Validation is fail-closed: an
empty error list is required before a close-out can be consumed.
