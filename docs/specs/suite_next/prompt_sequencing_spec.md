# Prompt sequencing spec

Status: draft. Scope: suite generation, prompt sequencing, sidecars, and
campaign order policy.

## Current lanes

### Affine smoke

`affine_smoke_v1` is the scored-workload smoke profile. Its current shape is
three levels `{1, 8, 64}` x eight ordinary items, plus a dedicated sentinel
item executed at suite start and suite end. The manifest has 25 distinct item
IDs and 26 executions.

Correctness remains quarantined in annotations/sidecars. The manifest must not
grow ad hoc scoring fields until a schema change is reviewed.

### `jw_mixed_v1`

`jw_mixed_v1` is the common-shape synthetic suite. It currently spans six
categories:

- `jw.chat`
- `jw.code`
- `jw.summ`
- `jw.reason`
- `jw.json`
- `jw.multiling`

The active real-tokenizer manifests target a 512 prompt / 256 output
fixed-budget stratum against the pinned Qwen2.5-1.5B tokenizer file manifest.
Generated manifests and sidecars must regenerate byte-identically under the
same seed and tokenizer files.

### Content sentinels

`jw_sentinel_v1` is the AP-6 content-sensitivity sentinel suite. It uses five
ids-native, BOS-less conditions at literal equal shape:

- repeated seed
- random token
- natural prose
- code-like
- multilingual

These results do not generalize to text-path prompts with BOS/template
handling unless a bridge suite is added.

## Manifest and sidecar rules

The suite manifest schema is intentionally closed. New metadata should use
existing fields where possible:

- `difficulty`
- `shape`
- `source`
- `grouping`
- `tags`
- generator annotations sidecars

Sidecars are the preferred home for:

- generator parameters and truthful semantic annotations
- tokenizer audit rows
- expected token hashes for text-path generated items
- ground truth / scorer inputs
- category-specific provenance
- deterministic parse/evaluation traces

Deferred manifest fields such as `scoring`, `pair_id`, `holdout_role`, and
benchmark-import fields remain rejected until explicitly promoted.

Prompt sources are mutually exclusive per item:

- `source.prompt_text`
- `source.prompt_token_ids`
- synthetic prompt tokens where the substrate supports them

Ids-native item length must equal `shape.planned_prompt_tokens`. Text-path
items must record enough sidecar provenance for post-window realized-vs-expected
hash and count checks.

## Sequencing rules

Historical note, superseded 2026-07-09 below: runtime execution was manifest
order. `order_seed` was derived and recorded, but runtimes did not use it to
reorder items.

Therefore, any claim of round-robin, Latin-square, level rotation, or
condition-balancing across repeated suite bundles must be implemented as one of:

1. Per-repetition generated manifests with distinct effective manifest hashes
   and explicit order metadata.
2. A real suite execution policy implemented in the runtime adapters and
   reflected in the manifest hash / run identity.
3. A campaign-level order policy over whole configs, using `order_manifest.json`
   rather than changing item order inside a suite.

Before 2026-07-09, until one of those was implemented, specs and reports had
to say `manifest_order`.

### 2026-07-09 (P2-030): operational suite order policies

`execution_policy.order_policy` is now a closed operational policy name:

- `manifest_order`: execute manifest item order exactly. This is the
  back-compatible default and the required wording when rotation is absent.
- `block_round_robin_v1`: rotate the non-sentinel contiguous block runs by
  `order_row`.
- `block_latin_square_v1`: use the Williams row-balanced order over the
  non-sentinel contiguous block runs; even block counts complete in `N` rows,
  odd block counts use the standard `2N` paired rows.

The rotation unit is the contiguous block run. Blocks whose items all carry the
`sentinel` tag are anchored in their manifest positions and never rotate. Blocks
and levels therefore remain contiguous by construction. Within-block item
rotation is deferred; if needed, it must be a new named policy and revisit this
spec.

`order_row` is controller-derived: `0` for single runs and the one-based `__rN`
suffix for experiment members. The row used is `order_row mod n_rows`.
`order_seed` derivation and recording are unchanged and remain audit material;
the runtime never chooses either value. Non-`manifest_order` bundles must record
`order_row` in `suite_start` metadata and `metadata.suite`; strict validation
must recompute the expected permutation and fail closed on mismatch.

`item_index` means manifest index everywhere. `position` means realized
execution ordinal. `prev_item` is the previous realized item ID, or `null` for
the first realized item. `block_index` is the realized block encounter ordinal
and may vary across rows; `block_id` is the stable cross-bundle block key.
`outputs/suite_items.jsonl` remains keyed by `item_index`, preserving
expected-vs-realized prompt-hash checks.

Blocks and levels must be contiguous runs. Naive interleaving such as
`L01, L08, L01` inside a single block is invalid under the current validator.
If future analysis needs interleaving, it should use block boundaries that keep
each block/level contiguous or promote a schema/validator change.

The controller must not loop over suite items during the measured window. The
runtime adapter emits markers inside a single `run_suite` call.

Campaign sequencing outside suites is handled by `order_manifest.json`.
Absence may fall back to sorted order, but any scientific campaign should
carry an explicit order manifest and log its block/position covariates.

## Text-path hash guard

Before any text-path suite campaign, implement or require the P2-025 guard:

- expected token-ID hash and expected realized token count from the generator
  sidecar
- realized `outputs/suite_items.jsonl` token-ID hash and token count after
  runtime execution
- fail-closed mismatch handling in the campaign runner or strict validation
- hash-domain awareness so text hashes, source hashes, and token-ID hashes are
  not confused

Ids-native items already have stronger strict-validation closure; text-path
items need this campaign-level guard before scale.

## Acceptance criteria

- Generated manifests validate via `SuiteManifest.from_mapping`.
- Manifest and sidecar regeneration is byte-identical under the same seed and
  tokenizer file manifest.
- `suite_manifest_sha256` in config matches the canonical effective manifest.
- Active `jw_mixed_v1` and sentinel manifests realize exactly 512 prompt tokens
  on the pinned tokenizer.
- Affine smoke keeps 26 executions, 25 distinct item IDs, two tagged sentinel
  entries, and eight non-sentinel items per level.
- Mock and MLX suite runs produce strict-valid bundles with
  `outputs/suite_items.jsonl`, not `response.txt`.
- Any campaign report states whether item order was `manifest_order`,
  per-repetition manifest order, or implemented execution-policy order.

## Rationale

The shipped substrate is strong because manifest bytes, prompt hashes, runtime
outputs, and suite markers form an evidence chain. Sequencing claims can break
that chain if reports imply item-order policies that the runtime does not
perform. The safest near-term path is to treat manifest order as the execution
truth and move balancing either into generated manifests or whole-config
campaign order.

Rejected alternatives:

- Let `order_seed` imply reordering. Rejected because it is recorded but not
  currently operational.
- Put all generator annotations into the manifest. Rejected because the
  manifest schema intentionally rejects deferred scoring/import fields and
  would become unstable.
- Launch text-path campaigns before P2-025. Rejected because silent
  off-grid tokenization would be detected too late for quiet-window scale.

## Revisit triggers

- P2-025 lands and changes the strict-validation surface.
- A real non-`manifest_order` suite execution policy is implemented.
- Full affine ladder or benchmark imports need fields that sidecars cannot
  carry honestly.
