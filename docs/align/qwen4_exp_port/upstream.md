# Upstream readiness: `qwen4_exp` for ml-explore/mlx-lm (GOAL item 10)

Status, 2026-11-05: **preparation only.** Nothing has been posted to GitHub. The
PR to ml-explore/mlx-lm opens only with Ed's go (GOAL item 10), and the comment
for #1788 below is a set of talking points that Ed writes himself (see §1.1).

Contents:

1. Upstream rules that bind us
2. Community PR #1788: state, every request raised in it, and how ours differs
3. Etiquette decision: coordinate or open a separate PR
4. Requirement checklist mapped to evidence
5. Planned file layout in mlx-lm style
6. Convert and quantization predicates
7. PR description fact sheet (for Ed to write from)
8. Talking points for a comment on #1788 (for Ed to write from)
9. Licensing check
10. Test status and how to run it
11. Open issues

Sources read: the pinned mlx-lm v0.31.3 source in `.engine/mlx-lm-v0.31.3/`
(CONTRIBUTING, `tests/test_models.py`, `utils.py`, `generate.py`,
`models/cache.py`, `models/qwen3_5*.py`, `models/deepseek_v32.py`); live
`ml-explore/mlx-lm@main` (fetched read-only with `gh api` on 2026-11-05: CONTRIBUTING,
the PR templates, the workflows, `tests/models/`, `utils.py`, `generate.py`,
`cache.py`); merged PRs #441 and #453 (Qwen3-Next), #869, #928 and #1623 (Qwen3.5
and the norm fold), #836 (Step 3.5), #819 (LongCat n-gram), #512 (DeepSeek V3.2
indexer), #1823 (gated-delta HF-reference test), #1559, #1626 (Kimi K3), #1012
(Mistral 4), #1410 and #1997 (DSA indexer), #1801, #1862, #1749 and #1770 (repo
policy); open PR #1821 and issue #1924; and PR #1788's description, its 23
comments, its single review and its commit list, **read as text only**. No
#1788 code was fetched or run. Raw API dumps are in the session scratchpad, not
the repo.

## 1. Upstream rules that bind us

### 1.1 AI usage policy (added 2026-08-21, #1770). This is the main constraint.

From live `CONTRIBUTING.md`:

> AI-generated code is allowed. What is not allowed is submitting code you do
> not understand. You are 100% responsible for every line, however it was
> produced, and must explicitly disclose the manner in which AI was employed.
>
> It is strictly prohibited to use AI to write your posts for you (bug reports,
> feature requests, pull request descriptions, Github discussions, responding
> to humans, ...).

Both PR templates start with "☑️ I understand it is strictly prohibited to use AI
to write PR description" and an "AI usage disclosure:" line. Consequences:

- **Ed writes the PR description and every comment himself.** §7 and §8 are
  therefore fact sheets and talking points: inputs for Ed, not text to paste.
  Pasting agent-written prose would break the policy. The policy is enforced
  socially; one contributor (pierre427 on #1821) says AI contributions led to a
  "shadowban/prohibitions" for them.
- **Ed must understand every line of `qwen4_exp.py` before submission.** This
  is a review task for Ed, beyond the agent reviews in GOAL item 9.
- The disclosure must say how AI was used: two independent agent ports (Sol 6.1
  and Opus 5.5), agent review loops, and agent-written tests. It must also say
  what Ed did himself.

### 1.2 New-model PR template (required)

`.github/PULL_REQUEST_TEMPLATE/new_model.md` is mandatory. Its sections are
Requirements, Model information, Supported checkpoints, Verification (an
`mlx_lm.generate ... -p "The secret to baking a good cake is" -m 1024` output)
and Reference output (a transformers pipeline output, "if you have access to
CUDA hardware"). On #1626 the maintainer zcbenz asked for a rewrite to this
template because "it would help me verify the implementation much quicker."

### 1.3 PR limit (#1749, mirroring ml-explore/mlx#4320)

GitHub's pull-request limit is enabled. External contributors bypass it only
with more than 2 merged PRs in the last year, fewer than 5 open PRs, and a
merge rate above 50 %. The MLX version of the rule sets the limit to 1 open PR.
Ed's account (`mpmdw`) has no mlx-lm PRs, so **Ed can most likely have only one
open PR at a time.** A follow-up (paging, kernels) waits until the first PR
merges.

### 1.4 Engineering conventions

- Formatting: `pre-commit` with black (25.1) and isort (`--profile=black`); run
  `uvx pre-commit run --all` before submission.
- Tests: "Make sure new code is covered by tests … and confirm the new tests
  fail in the main branch." Since 2026-10-23 (#1997) **model-specific tests go
  in `tests/models/test_<model>.py`**; the shared `test_all_models` list in
  `tests/test_models.py` still takes one config entry per model.
- Performance claims need scripts and reproduction steps.
- "Search for existing pull requests first": #1788 exists (§3).
- Main requires `mlx>=0.32.3` and Python 3.11+. CI runs `unittest discover`
  on a self-hosted Mac and a 2-process `mlx.launch` parallel test.
- Main now refuses `config["model_file"]` unless `trust_remote_code=True`.
  JouleWise's pinned 0.31.3 `model_file` route (GOAL item 4) is unaffected,
  but a future pin bump must pass the flag, or rely on the upstreamed module.

### 1.5 What maintainers asked for on comparable PRs

| Ask | Where |
|---|---|
| Config defaults and `__post_init__` must match the transformers config: `attention_bias` default, `layer_types` derived from `full_attention_interval`, `head_dim` | #441 |
| `sanitize` drops `mtp.*` (and vision) weights | #441, #869 |
| Bake `1 + w` into weights in `sanitize`, not at runtime | awni on #836; restated on #1788 |
| `sanitize` runs at convert **and** at load: no double `+1`; use a reliable "already converted" signal | awni on #869 (bug), #928 (fix), #1623 (the structural raw-`conv1d`-layout signal replaces the MTP-presence heuristic) |
| State lives in a real cache object, not a model attribute (prompt caching); batch generation must work with it | awni on #819 |
| A model test is required | #819, CONTRIBUTING |
| Reuse existing components where they fit | zcbenz on #1626 |
| VLM-shaped checkpoints: nest the text model under `language_model` like `qwen3_5`, instead of renaming every key | angeloskath on #1012 |
| Check lazy loading (`lazy=True`) | angeloskath on #1012 |
| Get indexer details right (RoPE `traditional` flag, sum over heads) | #512 |
| Pin numerics against the HF reference implementation in tests | #1823 (merged, NumPy port of the HF recurrence) |
| Parity verified by a maintainer before merge ("verified the parity, it matches") | michalk8 on #1012; the `await verification` label |

## 2. Community PR #1788

State on 2026-11-05: open since 2026-08-26 by `eauchs`. The head is `2097324`
(2026-09-26), with 9 commits touching 2 files (`mlx_lm/models/qwen4_exp.py`
+1201, `tests/test_models.py` +189). There are 23 issue comments and 0 inline
review comments. The only review is an APPROVED from a non-member (association
NONE) on an older commit, `1e5e0fca8`. Collaborator `nastya236` added the label
`await verification` ("This pull request is non-trivial and requires a human
expert to verify its correctness") on 2026-08-29 and wrote that review "may take
sometime". The last activity was 2026-10-04. The merge state is `blocked`.
The thread says mlx-vlm merged its own `qwen4_exp` (Blaizzy/mlx-vlm #2028/#2032).
We have not verified that independently.

### 2.1 Every blocker and reviewer request raised, and what a new PR must satisfy

The status column describes **the thread's account**. We did not run #1788.

| # | Request / defect (who) | Thread status | Requirement for any qwen4_exp PR | Our test |
|---|---|---|---|---|
| R1 | Official checkpoint has `mtp.*`; strict load fails (Sofille65) | fixed in thread | drop `mtp.*`, `model.visual.*` | `test_sanitize_official_checkpoint` |
| R2 | Keys nested as `model.language_model.layers…` (Sofille65) | fixed | accept the official prefix | same |
| R3 | Fused experts `gate_up_proj [E,2I,H]`, `down_proj [E,H,I]` (Sofille65) | fixed | split gate = first half along dim -2 | same + pinned logits |
| R4 | Non-gated RMSNorms are zero-centred (`1+w`); gated DeltaNet norm is conventional (Sofille65: "the critical fix") | fixed | fold `+1` for zero-centred norms only | pinned logits (`0.2·u` norms) |
| R5 | `offset` can be an `mx.array` (per-row offsets from `BatchGenerator`) (Sofille65) | fixed | positions helper for int or array offsets | `test_left_padding` |
| R6 | QSA causality: queries with fewer than `compress_ratio` visible tokens got a fully masked row → uniform softmax over future keys (eauchs) | fixed (6f007f5) | per-query tail, causal intersection | pinned logits (cached and prefill) |
| R7 | `quant_predicate` must accept `(path, module)`; 3-arg form crashed convert on 0.31.3 (Sofille65) | fixed (8a36d1e) | 2-arg predicate | `test_quant_predicate_convention` |
| R8 | Bake `+1` in `sanitize` instead of at runtime (kernelpool, citing awni #836/#869) | done, gated on the `model.language_model.` prefix | bake once; a convert→load round trip must not refold | `test_sanitize_converted_weights_is_identity`, `test_quantize_save_load` |
| R9 | Conversions from before the bake carry unbaked norms, which load silently degraded (Sofille65) | documented, not detected | a structural "raw HF" signal (#1623 uses raw `conv1d` layout), never a filename or prefix heuristic | same |
| R10 | n-gram hash `seed` defaulted to 0; the reference default 1234 is load-bearing because `config.json` has no `seed` (beatakouchnir, sje397) | fixed (2097324) | default 1234 | pinned logits (config has no `seed`) |
| R11 | Verify the rebuilt n-gram constants against the checkpoint's copies at load, and raise on mismatch (beatakouchnir, sje397) | added (2097324) | fail closed | `test_sanitize_rejects_inconsistent_hash_constants` |
| R12 | `test_qwen4_exp` red at head on one setup: prefill vs stepwise 1.07e-3 against a 1e-4 tolerance (sje397); author and xunlinkx could not reproduce (M3 Max 0.31.2, M3 Pro 0.32.3) | unresolved | prefill = stepwise ≤1e-4 fp32, on many seeds and on more than one machine | `test_matches_reference_cached` (against transformers, not self-consistency) |
| R13 | Quantized packs nest shards as `…ngram_embedding.shards.N` with `scales`/`biases`; the PR expects flat `shard_N` (Teejer) | changed in da1148f ("accept both key layouts") | the n-gram table must be an `nn.Module` tree that `nn.quantize` converts (QuantizedEmbedding per shard) | `test_quantize_save_load` |
| R14 | Per-module quant overrides keyed by checkpoint names miss after `sanitize` renames keys (sje397, issue #1924) | partly fixed on main by #1482 (`infer_quant_config`) | do not rely on checkpoint-keyed overrides; our convert writes post-sanitize paths | `test_quantize_save_load` (save → `load_model`) |
| R15 | oMLX-layout packs: global `ngram_embedding.weight_scale`, a flat `language_model.*` layout with raw zero-centred norms, and the fold gate missing them (mukhanov) | not in PR | decide scope: support official HF and our own conversions; refuse unknown layouts rather than guessing | not tested (out of scope, §11) |
| R16 | `--kv-bits`: `_AttnCache.to_quantized` drops the indexer, so QSA silently loses history (PR description) | unresolved | QSA caches must survive or refuse KV quantization | design: `CacheList` has no `to_quantized`, so it is skipped |
| R17 | Raw left-padded `ids`: n-gram hash and shift read padding tokens (5.7e-1) (PR description) | unresolved, "not reachable" | padded ids → EOS for PLE and masked PLE conv, as the reference does (`ple_input_ids = where(mask, ids, eos)`) | `test_left_padding` |
| R18 | Private cache classes (`_AttnCache`, `_BatchAttnCache`, `_LayerCache`) are not in `mlx_lm.models.cache`, so `load_prompt_cache` cannot rebuild them; the indexer state was lost across `merge` until fixed (feasibility review; PR description) | partly fixed (merge) | standard cache classes only | `test_layer_types_and_cache_classes`, `test_prompt_cache_save_load` |
| R19 | No reference output: "no CUDA hardware; the 180B checkpoint does not fit" (PR description) | open; this is what blocks `await verification` | provide reference evidence that does not need CUDA | pinned transformers logits + real-weight layer parity (GOAL 5, 11) |
| R20 | Branch `setup.py` requires `mlx>=0.32.1` (feasibility review) | n/a | target main and its pins | open issue: needs a main-branch venv (§11) |

### 2.2 How ours differs

1. **Reference-derived.** Written against the official transformers 5.22.1
   `models/qwen4_exp` (and checked against the official `config.json` and
   `model.safetensors.index.json`), not against mlx-vlm or #1788. Our process
   rule is never to execute #1788.
2. **Gold parity.** A torch-free test pins logits from the official
   `Qwen4ExpForCausalLM` on a tiny closed-form checkpoint in the **official
   layout**, covering every layer type. QSA selection is active, and the routing
   and selection margins have no near-ties. Separately, GOAL items 5 and 11 run
   per-layer parity on the real bf16 weights against transformers. Together these
   give maintainers the "human expert verification" the `await verification`
   label asks for, without CUDA.
3. **Paged n-gram.** For the 128 GB measurement Mac, JouleWise pages the
   51 B-parameter n-gram table from disk (GOAL item 6). **Upstream should not
   start there:** reviewers expect parameters in the module tree, quantizable by
   `mlx_lm.convert`. Plan: the upstream module keeps the table as `nn.Embedding`
   shards, which are quantizable and lazily loaded by `mx.load`. Paging stays a
   JouleWise runtime option or becomes a later PR with benchmarks (one open PR
   at a time, §1.3).
4. **Standard caches.** We use `ArraysCache` and `CacheList(KVCache, KVCache)`
   only. Batching, prompt-cache persistence, `merge`, and safe `--kv-bits`
   behaviour then come from mlx-lm without new cache code.

## 3. Etiquette decision: coordinate first

**Recommendation: coordinate on #1788 first. Offer our verification assets to
help it land. Open a separate PR only if the author and maintainers prefer it,
or if #1788 stalls.** Reasons:

- CONTRIBUTING says "search for existing pull requests first", and the PR limit
  exists because duplicate PRs "burden the team too much". A competing PR for
  the same model as a first contribution would read badly.
- #1788 is blocked on **verification**, not on code volume. Our differentiator
  is verification evidence: reference-pinned tests and real-weight parity. That
  evidence is most useful attached to whichever PR lands.
- The author has been responsive. They merged two community fix PRs into their
  branch (`eauchs/mlx-lm#1`, `#2`) and credited reporters.
- The bar for a separate PR is a design difference reviewers would care about.
  We have one in caches (R16, R18) and in the norm-fold discriminator (R9),
  where #1623 shows maintainers want a structural signal. Raise those as
  questions, not as a takeover.

Constraint to state openly: **we will not run #1788's code** (our own rule).
So we cannot report results on their branch. We can only hand over tests the
author (or a maintainer) can run.

Decision points for Ed:

- (a) Post a coordination comment (Ed-written, §8). Offer the torch-free
  reference test as a PR into `eauchs/mlx-lm` or as a standalone file.
- (b) If after about 2 weeks there is no response, or the author and maintainers
  prefer a fresh implementation: open our PR with Ed's go, link #1788, and
  credit the thread's reporters for the issues they found (R1–R17).
- (c) Either way, Ed's single open-PR slot (§1.3) is spent on the qwen4_exp PR
  itself, not on a side fix.

## 4. Requirement checklist mapped to evidence

Legend: **done** = exists and passes now; **ready** = test exists, awaiting the
canonical module; **planned** = GOAL phase not yet run.

| Requirement | Source | Evidence | Status |
|---|---|---|---|
| New-model template; Ed-written description; AI disclosure | §1.1–1.2 | §7 fact sheet | planned (Ed) |
| Ed understands every line | CONTRIBUTING | Ed's review pass of `qwen4_exp.py` | planned (Ed) |
| File named after `model_type` (`qwen4_exp.py`) | CONTRIBUTING | §5 | planned (P3) |
| `ModelArgs.from_dict` on nested official config (vision block ignored) | #869 style | `test_qwen4_exp`, `test_all_models_entry` | ready |
| `layer_types`: `full_attention`, `indexed_attention`, interval fallback | #441, ref config | `test_layer_types_and_cache_classes` | ready |
| `model.model_type == "qwen4_exp"` | `model_test_runner` | `test_qwen4_exp` | ready |
| fp32/fp16 forward, cache, batch 2, deepcopy | `model_test_runner` | `test_qwen4_exp` | ready |
| Matches transformers on prefill (fp32 ≤1e-4) | GOAL 2, R19 | `test_matches_reference_prefill` | done for the Sol snapshot |
| Matches transformers on chunked + stepwise decoding | GOAL 2, R12 | `test_matches_reference_cached` | done for the Sol snapshot |
| Official layout loads strictly; mtp/visual dropped | R1–R3 | `test_sanitize_official_checkpoint` | done for the Sol snapshot |
| `save_pretrained` (per-expert) layout loads identically | transformers' reverse mapping | `test_sanitize_save_pretrained_layout` | done for the Sol snapshot |
| No double fold / transpose on converted weights | #869, #1623, R8–R9 | `test_sanitize_converted_weights_is_identity` | done for the Sol snapshot |
| Seed 1234 default; inconsistent constants raise | R10–R11 | `test_sanitize_rejects_inconsistent_hash_constants` | done for the Sol snapshot |
| Left padding equals unpadded (PLE included) | R5, R17, GOAL 2 | `test_left_padding` | ready (harness validated on mlx-lm `qwen3_5`) |
| Standard cache classes only | #819, R18 | `test_layer_types_and_cache_classes` | ready |
| Prompt cache save/load round trip | R18 | `test_prompt_cache_save_load` | ready (harness validated on `qwen3_5`) |
| Snapshot/restore of recurrent state is exact | GOAL 2 | `test_snapshot_restore` | done for the Sol snapshot |
| Trim exact or refused atomically | GOAL 2 | `test_trim` | done for the Sol snapshot |
| Quantize → save → `load_model`; n-gram table quantized | R13–R14, #836 | `test_quantize_save_load` | ready (save/load half validated on Sol) |
| Predicate signature `(path, module)` | R7 | `test_quant_predicate_convention` | done for both snapshots |
| bf16 cast honours `cast_predicate` | convert.py | `test_bf16_cast` | done for the Sol snapshot |
| Real-weight layer parity vs transformers | R19, GOAL 5/11 | gold-parity harness (`lane/2026-11-05-align-flashnext-gold-parity`) | planned (P4) |
| Generation on the official checkpoint for the template | template | `mlx_lm.generate` on the Mac | planned (P7) |
| Reuse `gated_delta_update`, `SwitchGLU`, the sigmoid-gate RMSNorm kernel on main | #1626, #1823 | §5 | planned (P3/P5) |
| black/isort clean; tests in `tests/models/` | §1.4 | `pre-commit` on the PR branch | planned |
| New tests fail on main | CONTRIBUTING | trivially true (no `qwen4_exp` on main) | n/a |
| Runs on main (`mlx>=0.32.3`) | §1.4 | main-branch venv | blocked on approval (§11) |

## 5. Planned file layout in mlx-lm style

```
mlx_lm/models/qwen4_exp.py        # the whole model, one file
tests/models/test_qwen4_exp.py    # from tests/align/test_qwen4_exp_upstream_shape.py
tests/test_models.py              # + UPSTREAM_TEST_ALL_MODELS_ENTRY in test_all_models
mlx_lm/utils.py                   # optional, see §6: MODEL_REMAPPING
                                  #   "qwen4_exp_text" -> "qwen4_exp"; predicate group size
```

No changes to `cache.py`, `generate.py`, `server.py`, or the tool parsers. The
chat template uses the Qwen3-Coder XML tool format
(`<tool_call><function=…><parameter=…>`), which the existing `qwen3_coder`
parser covers, plus a `reasoning_effort` template kwarg. LoRA needs no model
list on main.

Layout of `qwen4_exp.py`. Names follow `qwen3_5.py` and `qwen3_next.py`, and
the tree mirrors the checkpoint so `sanitize` stays small:

- `TextModelArgs(BaseModelArgs)`: every `Qwen4ExpTextConfig` field, with the
  **same defaults** (`seed=1234`, `split_ngram_parts=512`, `ple_embed_dim=None →
  hidden_size`, `output_gate_type=None → hidden_act`). `__post_init__` maps
  `full_attention`/`indexed_attention`, derives `layer_types` from
  `full_attention_interval`, and raises `ValueError` on the reference's
  `validate_architecture` conditions. `ModelArgs(model_type, text_config)` with
  `from_dict` accepting flat configs, like `qwen3_5`.
- `GatedDeltaNet`: as `qwen3_5.GatedDeltaNet`, through `gated_delta_update`
  with the documented q pre-scaling contract (#1823). Its gated norm uses
  `output_gate_type` (sigmoid). On main, reuse `kernels/rms_norm_sigmoid_gate`.
- `QSAIndexer` and `Attention`: doubled `q_proj` with a sigmoid output gate,
  q/k norms, partial non-traditional RoPE (text positions make mRoPE collapse
  to plain RoPE). The indexer stores **raw** keys in the second `KVCache` of a
  `CacheList` (the `deepseek_v32` pattern). It mean-pools complete blocks of
  visible tokens (anchored on the first visible token, so left padding is
  correct), applies `k_layernorm`, ropes each pooled key at its block-start
  position, scores `sum_h relu(q·k)/sqrt(d)`, takes the top
  `budget/compress_ratio` blocks, and unions in each query's partial tail.
- `SparseMoeBlock`: `SwitchGLU`, softmax router, top-k with renormalisation,
  and a sigmoid-gated shared expert. This matches `Qwen3NextSparseMoeBlock`;
  reuse it.
- `GatedResidual` (hyper-connections, `hc_count` streams): grouped RMSNorm,
  low-rank SiLU/sigmoid read gates averaged over streams, `2·sigmoid` write gates.
  The final mixer has no injection and doubles as the final norm (the reference
  has no separate final norm).
- `NGramEmbedding` and `PLELayer`: int64 multiply/XOR/remainder hashing with
  EOS segment resets, and a list of `nn.Embedding` shards (row-sharded like the
  checkpoint, so each shard quantizes). Key/query RMS gating, value projection,
  and a dilated depthwise conv (`kernel 4`, `dilation = ngram_size`).
- `Model`: `sanitize`, `make_cache`, `layers`, `quant_predicate`,
  `cast_predicate`. `shard()` and `PipelineMixin` are follow-ups.

`sanitize` contract (each item is tested):

1. Drop `mtp.*`, `model.visual.*`, `vision_tower*`.
2. Map `model.language_model.` (official) and `model.` (save_pretrained) into
   the module tree. A converted MLX checkpoint is already in the tree and passes
   through unchanged.
3. Experts: fused `gate_up_proj [E,2I,H]` → `switch_mlp.gate_proj` (first `I`
   rows) and `up_proj`. Per-expert `experts.{e}.*` are stacked.
4. `conv1d.weight` `[C,1,K]` → `[C,K,1]` (DeltaNet and PLE). The raw layout is
   **the** signal that weights are unconverted (#1623). Only then fold `+1` into
   the zero-centred norms (`hc_norm`, `q_norm`, `k_norm`, `q_layernorm`,
   `k_layernorm`, `norm_key`, `norm_query`, `norm_conv`), never
   `linear_attn.norm`.
5. n-gram: `ngram_embedding.shard_N.weight` → shard list. Recompute the hash
   constants from the config, compare them with `layer_multipliers`,
   `ngram_heads_vocab_sizes` and `ngram_heads_offsets`, raise `ValueError` on any
   mismatch, then drop them.

`make_cache`: DeltaNet layer `ArraysCache(size=2)`; the PLE layer (also DeltaNet)
`ArraysCache(size=4)` (conv, recurrent state, PLE conv tail, last
`ngram_size-1` token ids); QSA layer `CacheList(KVCache(), KVCache())`.

## 6. Convert and quantization predicates

- `quant_predicate(path, module)` (2 args, R7): 8-bit for `mlp.gate` and
  `mlp.shared_expert_gate` (the `qwen3_5` MoE pattern). n-gram shards at group
  32: rows are `ple_embed_dim / ((ngram_size-1)·heads_per_ngram)` = 2560/16 =
  **160** wide, divisible by 32 but not by 64. Everything else uses the CLI
  defaults.
- **Trap on 0.31.3 and main:** `quantize_model.wrapped_predicate` checks
  `weight.shape[-1] % group_size` against the **global** group size *before*
  consulting the model predicate. With the default `--q-group-size 64`, the
  51 B-parameter table is silently left in bf16 (about 102 GB), whatever the
  predicate says. Options:
  - (i) document `--q-group-size 32`. This works today, but costs extra
    scale/bias bytes on every matrix (about +0.5 bit per weight at 4-bit).
  - (ii) a small `utils.py` change: when the predicate returns a dict, merge it
    over the global params and test divisibility against the effective group
    size. Add a test that fails on main.

  Recommend (ii) inside the qwen4_exp PR, flagged in the description as a
  maintainer decision. Fall back to (i) if they object.
- `cast_predicate`: keep `A_log` (and any integer buffers) uncast, as in
  `qwen3_5`.
- `--kv-bits`: `CacheList` has no `to_quantized` on 0.31.3 or main, so
  `maybe_quantize_kv_cache` skips QSA layers and quantizes nothing in this
  model. That is safe (R16) but saves no memory. Say so in the PR.
- Converted packs from other tools (oMLX `weight_scale`, mlx-vlm `shards.N`
  naming, pre-fold #1788 conversions): out of scope for v1. With strict loading
  they fail rather than load silently wrong. List them in the PR as known
  unsupported.

## 7. PR description fact sheet (Ed writes the text)

Policy reminder (§1.1): every sentence posted must be Ed's own. This sheet
lists facts and placeholders in template order.

- **Requirements / AI disclosure (facts to state in Ed's words):**
  - Two independent implementations were written with AI agents (Sol 6.1 via
    Codex; Claude Opus 5.5), blind to each other, then converged into one module.
  - The tests and the reference-pinning script were agent-written.
  - Agent review loops, one Fable 5.1 cold pass, and `/code-review ultra`.
  - Ed reviewed and understands every line [Ed confirms].
- **Model information:**
  - Name: Qwen3.8-Flash-Next.
  - Homepage: `https://huggingface.co/Qwen/Qwen3.8-Flash-Next`.
  - Reference: transformers `models/qwen4_exp` (5.22.1; sha256 of
    `modeling_qwen4_exp.py` `e57b3617…f1f5df`).
- **Supported checkpoints:** the official bf16 checkpoint (131 shards, fused
  experts, `shard_N` n-gram parts), plus conversions made with this PR. List
  the unsupported layouts (§6).
- **Verification:**
  - [paste `mlx_lm.generate --model <converted> -p "The secret to baking a good
    cake is" -m 1024` output from the Mac, with peak memory and the recipe used].
  - [Optionally: NLL on a fixed text, and the tool-call round trip (GOAL 7)].
- **Reference output (no CUDA; offer instead):**
  - (1) the torch-free test pinning transformers logits on a tiny official-layout
    checkpoint, every layer type, with the QSA budget active;
  - (2) per-layer real-weight parity against transformers on the full bf16
    checkpoint [link the report: max abs error and cosine per layer, fp32 and
    bf16];
  - (3) the pin script, to reproduce (1) with transformers.
- **Notes for reviewers:**
  - #1788 and the thread's reporters, credited by issue (R1–R17).
  - The `utils.py` group-size change (§6), as a decision for maintainers.
  - `--kv-bits` behaviour; trimming refused (as for `qwen3_5`).
  - MTP and vision out of scope.
  - QSA tie semantics (§11).

## 8. Talking points for a comment on #1788 (Ed writes the text)

- Thank the author and the testers by contribution: official-checkpoint fixes,
  the seed/constant check, the reproducibility runs, the bake-vs-runtime point.
- Context, one line: JouleWise needs Flash-Next on a 128 GB M3 Max for research.
- What we can contribute toward `await verification`:
  - a test, needing no CUDA and no download, that pins logits from the official
    transformers 5.22.1 `Qwen4ExpForCausalLM` on a tiny checkpoint in the
    official layout (fused experts, `shard_N`, hash buffers, `mtp`/`visual`
    extras), with every layer type and QSA selection active;
  - soon, per-layer parity against transformers on the real bf16 weights.
- Offer: open it as a PR into `eauchs/mlx-lm`, or post it as a standalone file.
  Say plainly that we have not run #1788 ourselves, so any results on the
  branch come from whoever runs it.
- Questions:
  - Would the author like the test in this PR?
  - Are maintainers open to the cache design (`CacheList(KVCache, KVCache)`
    instead of private cache classes, which also makes `load_prompt_cache` and
    `--kv-bits` safe)?
  - Are they open to the conv-layout fold discriminator from #1623?
- Avoid:
  - claims about #1788's behaviour from our own testing (we have none);
  - performance claims without scripts;
  - mentions of anyone beyond the author and, if needed, the collaborator who
    applied the label.

## 9. Licensing check

| Item | License | Implication |
|---|---|---|
| mlx-lm | MIT (© 2023 Apple Inc.) | Contributions are licensed under MIT (CONTRIBUTING). |
| Our port code (JouleWise) | MIT (© 2026 Ed R, `mpmdw`) | Ed can relicense or contribute under MIT. The contributor is Ed. |
| transformers `qwen4_exp` reference | Apache-2.0 (© Qwen Team and HuggingFace) | We re-implement the algorithm in MLX; this is mlx-lm's usual practice. Do **not** copy docstrings or comments verbatim. Constants such as splitmix64 and the hash recipe are functional facts. If any substantial code text were copied, Apache §4 notice terms would apply. Avoid that. |
| Qwen3.8-Flash-Next weights, config, template | **Qwen Community License 1.0** (`license: other`, `qwen-community-1.0`; text fetched 2026-11-05, sha256 `a0dc4225…676c08`) | MIT-like grant covering weights, configs and "inference code", with two conditions: (1) keep the notice, and products above 100 M MAU or US$20 M monthly revenue must display the model name; (2) a **"Model as a Service" or "AI Work Assistant" business needs a separate license for commercial use** (internal use is exempt). |
| What enters mlx-lm | — | Code and tests only. **No Qwen weights, configs or templates are vendored.** The test checkpoint is synthetic (a counter hash). `REAL_NGRAM_TEXT_CONFIG` holds 6 hyperparameter integers used to check the hash constants (facts, not "substantial portions"). |
| Converted weights (e.g. an mlx-community upload) | Qwen Community License | Uploads must carry the LICENSE and notice. Hosting `mlx_lm.server` for third parties as a commercial MaaS needs Qwen's separate license. That is the user's concern, but the PR can mention it in one line. |
| JouleWise's own use | — | Local research inference with no third-party access is "internal Use": allowed. |
| #1788 code (MIT via the repo) | — | Not read, copied or run by this lane. The canonical module must stay reference-derived so attribution stays clean. |
| mlx-vlm `qwen4_exp` | MIT | Not used. |

## 10. Test status and how to run it

`tests/align/test_qwen4_exp_upstream_shape.py` (unittest, upstream style) holds
18 tests. The module under test is pluggable via `JW_QWEN4_EXP_MODULE`: a
dotted name, or a path to a `model_file`-style `.py`. The default is
`mlx_lm.models.qwen4_exp`. If that is absent, the MLX tests skip. If the
variable names a module that fails to import, that is an error.

```sh
# JouleWise CI shape (no MLX): 2 helper tests run, the MLX class skips
python3 -m unittest tests.align.test_qwen4_exp_upstream_shape

# against a port (approved MLX venv, laptop limits)
JW_QWEN4_EXP_MODULE=/abs/path/to/qwen4_exp.py TMPDIR=/private/tmp/jwsupport-tmp \
OMP_NUM_THREADS=2 nice -n 10 /private/tmp/jwsol/venv-mlx/bin/python -B \
  -m unittest tests.align.test_qwen4_exp_upstream_shape -v

# re-pin the reference (approved reference venv), after changing the generator
TMPDIR=/private/tmp/jwsupport-tmp OMP_NUM_THREADS=2 HF_HUB_OFFLINE=1 \
TRANSFORMERS_OFFLINE=1 nice -n 10 /private/tmp/jwsol/venv-ref/bin/python -I -B \
  scripts/align_qwen4_exp_upstream_pin.py --write
```

Pin provenance (in the file): transformers 5.22.1, torch 2.15.0, sdpa (eager
agrees to 3.6e-7). transformers' own `from_pretrained` loader gives logits
identical (0.0) to our key mapping. Reference stepwise = prefill to 1.8e-6. Min
router top-k logit gap 8.9e-3. Min QSA block-score gap 0.10 over 20 selecting
queries. The hash constants were checked against the reference buffers (tiny)
and the reference functions (real config).

Results on 2026-11-05, against snapshots of the in-progress ports (not the
canonical module; neither port was modified):

| Snapshot | Pass | Fail/error (reason) |
|---|---|---|
| Sol `fa1a417e5:joulewise/align/models/qwen4_exp.py` (+ `qwen4_exp_tables.py`), sha256 `0fa36f0a…` | 13/18, including **both transformers-parity tests**, all four sanitize tests, snapshot, trim, bf16 | `model.model_type` is `qwen4_exp_text`; custom `Qwen4ExpAttentionCache`/recurrent cache classes (not batchable via `_make_cache`, `save_prompt_cache` raises `std::bad_cast`); n-gram table not in the quantizable tree |
| Opus twin working tree `qwen4_exp_twin.py`, sha256 `da2ca8c3…` | 6/18 (sanitize layout tests, predicate signature) | n-gram table lives outside the parameter tree ("no n-gram table registered … convert with scripts/align_convert_qwen4_exp_twin.py"), so no forward runs from in-tree weights; inconsistent hash constants are not rejected |

The cache harness itself was checked on mlx-lm's own `qwen3_5` (standard
classes): left padding 1.4e-6, exact prompt-cache round trip. The quantize →
save → `load_model` half reloads the Sol snapshot bit-exactly (8-bit, g32,
cosine 0.9997 against fp32). These failures are the upstream-shape gaps P3 must
close. They are not harness bugs.

## 11. Open issues

1. **Cannot test on mlx-lm main.** Main needs `mlx>=0.32.3`; our approved venvs
   pin 0.31.2/0.31.3. Before the PR, Ed must approve a third, isolated venv
   (main checkout + its pins) to run `unittest discover`, `pre-commit` and the
   2-process parallel test.
2. **QSA ties at zero.** `relu` makes the scores of all-negative blocks exactly
   0. When fewer than `budget/ratio` blocks score positive, `torch.topk` breaks
   the tie among zero blocks in an implementation-defined order. Observed with
   2 indexer heads: scores `[0,0,0,0.0097]` selected blocks `[3,1]`, not
   `[3,0]`. The pinned fixture uses 4 heads (as in the real model) and verifies
   there is no boundary tie. Real long contexts can hit this. GOAL items 2/5/11
   need a stated tie rule, or tie-tolerant comparison. This should go to the
   PR's reviewers (and possibly to transformers).
3. **Two reference copies differ.** The installed transformers 5.22.1
   `modeling_qwen4_exp.py` (sha256 `e57b3617…`) differs from
   `.engine/transformers-qwen4_exp/modeling_qwen4_exp.py` (`3424f1b7…`) in eager
   float-mask handling. The `.engine` copy uses `masked_fill`; 5.22.1 adds
   `finfo.min`, which can give NaN on fully masked rows, e.g. padded queries,
   and `0·NaN` then leaks into the DeltaNet state. Configuration files are
   identical. The pins use 5.22.1 with sdpa and no padding, where the two agree.
   Record which copy is "the" authority for GOAL 2's left-padding parity.
4. **Paged n-gram vs upstream.** The upstream module keeps the table in-tree
   (§2.2). The canonical JouleWise module needs the paging as an option that
   leaves the parameter tree, and so this test, unchanged.
5. **`utils.py` group-size fix** (§6): needs a maintainer decision. Until then,
   `--q-group-size 32` is the documented route.
6. **`qwen4_exp_text` remap.** Loading transformers `save_pretrained`
   text-only checkpoints (flat config, `model_type: qwen4_exp_text`) needs
   `MODEL_REMAPPING["qwen4_exp_text"] = "qwen4_exp"` in `utils.py`. The module
   side is already tested (flat config, `indexed_attention`).
7. **R12 reproducibility.** The thread's 1.07e-3 prefill-vs-stepwise report was
   on an unknown chip. Before submission, run the cached reference test on both
   the M4 Air and the M3 Max with a seed sweep (GOAL 2).
8. **Etiquette sequencing.** The coordination comment (§8) is Ed's to write and
   post. If he chooses a separate PR, wait about 2 weeks for a response first.
