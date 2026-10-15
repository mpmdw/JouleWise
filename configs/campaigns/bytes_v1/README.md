# BYTES configuration drafts

Build authority: `docs/design/bytes_pack_design.md` at `7a3cea2e0` (R1, R2,
R4, R6 and R8 items 1–2). These files are drafts, not permission to collect.
No inference, model download, power capture or measurement was run to build them.

Regenerate and verify with Python 3.13:

```sh
python3.13 -B configs/campaigns/bytes_v1/generate_configs.py
python3.13 -B scripts/bytes_plan_trees.py
python3.13 -B configs/campaigns/bytes_v1/generate_configs.py --check
python3.13 -B scripts/bytes_plan_trees.py --check
```

There are 50 run configs per R1 model: ten absolute repeats, then ten identical
null ABBA quads in A1/B1/B2/A2 order, split into two five-quad manifests.
`roster.json` records the fit/held-out roles and workload. `pass_order.json`
records the six BYTES slots and their reverse in pass two. The six primary fixed
trees are `configs/b6/packs/bytes-sN/plan_tree.json`; their second-pass trees are
`pass2/plan_tree.json`. Registration drafts contain both paths.

## Manifest commands

The portable `scripts/bytes_manifest.py headers --model-dir DIR --out JSON`
reads headers and config only. Supply `--revision REVISION` for a pinned local
model directory without a Hugging Face snapshot revision or `_commit_hash`.
The script rejects unsupported architectures, unknown tensors, invalid stored
spans, duplicate tensors and inconsistent expert/tied-embedding metadata.

The separate `kv --model-dir DIR --out JSON` command is Mac-only and **does run
inference**. It was not executed for this build. It uses the runtime's exact
synthetic prompt, a four-token warmup on that prompt, the inherited five-second
settle, and one 512-token greedy generation without EOS stopping. Explicit
forwards avoid a streaming generator's possible look-ahead: snapshots follow
2,048 prefill tokens and 511 decode forwards (occupied full-cache length 2,559).
The returned 512th output token is not fed back through the model.

`merge --headers HEADER_JSON ... --kv KV_JSON ...` writes
`configs/bytes/bytes_manifest.json` by default; `--out` selects another path.
Header/KV revision, config and tokenizer identities must agree. Merge requires
revision and tokenizer pins. It prints W minus the pilot's `read_meas_GB` in
bytes, since that pilot column excludes KV. A model absent from the pilot has
null comparison values, not zero differences. The build did not create an
actual manifest or invent Mac KV observations.

## Decisions I made

- Use D-117's ten-repeat/ten-null-quad convention and its first decode absolute
  run as the run-config template. The ruling names the runtime prompt helper,
  but no particular run-config file; the selected source is recorded in
  `roster.json`. Preserve 57.6 seconds idle capture and five seconds settle;
  replace chat/suite inputs with `prompt_tokens: 2048`, `output_tokens: 512`.
- Preserve quantization weight, scale and bias storage by dtype and shape.
  W counts one embedding row, the whole output projection (the whole embedding
  matrix when tied), all dense/shared tensors and k/E of routed tensors.
  R counts every classified stored tensor once. GB means decimal 10^9 bytes.
- KV uses occupied cache-state array bytes, matching the pilot's `cache.state`
  accounting. Record backing array bytes/capacity independently; recurrent
  state has null sequence capacity/offset when its cache exposes none. Do not
  approximate hybrid state with the all-attention formula or pilot end scaling.
- Preserve available pilot/model-panel revisions; use the existing pinned
  example for Qwen3.5-122B. Leave the new 8B-8bit revision null pending R8 item 5.
  All C4 tokenizer/artifact/runtime identity issuance remains deferred.
- Generate one primary tree and one pass-two tree per sub-pack through
  `compose.layout` and `compose.render`. Paired models get their shared midpoint
  at the module boundary; single-model packs use compose's existing boundary
  between the two quad halves. Do not interleave quads or reverse runs inside a
  module. Reference original manifests so the fixed reader can read the result.
- Remove inherited BETA workload/calibration identities, downstream contracts,
  sizing and arm attachments from the draft trees. Supply a BYTES draft
  collection-membership plan so every launch pointer resolves. Keep the shared reference
  and calibration launch scaffold. The trees do not claim BETA's authority.
- Keep `blinding: {hidden_offset: true}` valid and record top-level
  `blinding_group: bytes`, which the current validator permits. Runtime group
  enforcement and subset unblinding remain C6/C7, not implemented here.
- Planning module minutes use pilot maximum request time plus inherited
  idle/settle, 50 members and a 20% margin. The new 8B-8bit uses R1's 150-minute
  planning estimate. These are not measured session footprints or arm limits.

## Ruling/code disagreements and remaining gates

- R6 inclusion needs a ruling: “catalog unchanged” preserves the current
  catalog's 43 EXCLUDE_MEMBER and 19 EXCLUDE_WINDOW effects, including nonthermal
  codes, while “the rest are flags” can mean nonthermal disclosure only.
  Drafts retain the existing effects and explicitly record this unresolved
  question; changing them changes which data count. Recommendation: retain the
  catalog unchanged. Block registration on this choice, not config generation.
- Stage 1's fixed layout always reads `plan_tree_ref`; it does not consume the
  new `pass_plan_tree_refs`, reverse BYTES slots, or enforce their interleaving
  after replication rounds. Both orders are committed data; the later driver
  must select them before pass two. Never collect pass two with pass one's tree.
- The validator permits a top-level blinding group, but existing blinding code
  does not enforce one group across all six packs or two-stage subset unblinding.
- The pilot used text-file tokenization and a truncated 64-token warmup. R2
  instead requires exact synthetic ids and warmup on the full prompt; both the
  configs and the new KV command follow R2. Pilot KV was an end-only cache-state
  count, while the manifest requires the two actual endpoint snapshots.
- The inherited bracket reservation named BETA's calibration plan. Each tree
  now names its own draft `collection_plan.json` with the exact BYTES membership
  and a bound digest. The existing reservation authenticates the plan id and
  digest without requiring the old floor-plan schema. Every launch pointer
  resolves through the existing chain reader in tests.
- C4/C5, the Mac download/KV/resolvability/sizing/clock/contention/disk work,
  registered analysis/twin/estimators, the registration cold gate and smoke
  fingerprints remain R8's later tasks. No live readiness is asserted here.

Registries touched: none required by the passing census/inventory checks.
The existing Block-6 pack discovery automatically sees `*/registration.json`
and keeps these six packs closed because their status is `draft`.
