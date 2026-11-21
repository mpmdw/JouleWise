# Numerical audit: mlx-vlm `qwen4_exp` (Qwen3.8-Flash-Next) vs the official transformers reference and our Sol port

Date: 2026-11-05. Auditor: Opus 5.5 subagent. Execution approved by Ed on 2026-11-05 ("you have my approval"): released mlx-vlm in an isolated venv, on tiny random configs only, with no real weights. This is the numerical companion to `audit_mlx_vlm_static.md` (commit 7d9f20b9e). Its tests were prioritized as T1–T6.

## Verdict: **DEFECTS FOUND**

| ID | Severity | Status | Summary |
|---|---|---|---|
| **D1** | **HIGH** for batched serving; **none** for single requests | **Confirmed on the real user path** (`BatchGenerator`, the engine behind `batch_generate` and the server's continuous batching). **Unreported, not fixed on main, not a documented trade-off** (evidence in §D1) | In any batch where one row is left-padded, every QSA layer computes the sparse selection and then discards it, attending densely. Every row of that batch diverges from its single-request result, **including the unpadded row**, once a row's visible context exceeds `indexer_budget + compress_ratio` (2052 tokens on the real config). The tiny config shows greedy tokens changing and logprob errors of 0.06–0.2. A two-function patch restores exact parity (≤ 7.7e-7 fp32). |
| F1 | LOW (fails loudly) | Confirmed | Every checkpoint re-saved by transformers 5.22.1 fails to load: `ValueError: Unsupported Qwen4-Exp layer types: {'indexed_attention'}`. A transformers-default `output_gate_type=None` is also rejected. The official checkpoint is unaffected. |
| P5 | LOW (path not documented, but silently wrong) | Confirmed | A left-padded batch scored **without a cache** (`lm(ids, attention_mask=mask)`) ignores the padding. The padded row is off by 0.61–0.89 in logits, and nothing is raised. |
| P3 | Minor deviation (implementation-defined) | Confirmed and characterized | QSA top-k at exact-zero (relu) score ties: mlx-vlm keeps the higher block indices, while `torch.topk` uses its own unspecified order. That order is **not** "lowest index first" either (see §P3). This is the only source of fp32 mismatch in single-request runs. |
| P1 | Minor (bf16 only) | Confirmed, small | The router's softmax output is bf16 (`precise=True` still returns bf16). With bf16 logits, only ~1.3 % of tokens at logit scale σ = 0.5, and 0 % at σ ≥ 1, pick a different top-10 set **because of** bf16 rounding of the softmax output. Exact ties already present in bf16 logits are far more common: about 14 % of tokens with 512 experts. Those make the reference itself tie-order dependent. |
| P2 | Minor (bf16 only) | Confirmed, **no drift** | DeltaNet `softplus(a + dt_bias)` and the q/k L2 norm run in bf16. The state error against the fp32 truth plateaus: 6.6e-3 → 7.9e-3 from T = 512 to 8192, against 6.2e-3 → 6.6e-3 for our port and 4.4e-3 → 4.1e-3 for the reference's own bf16. It does not grow, so it is not a bug. |

**The single-request text path (what JouleWise would use) is FAITHFUL.**

- fp32 ≤ 1.0e-6 max-abs logits vs transformers on the tie-free configs, for:
  - full prefill (with and without a cache);
  - stepwise decoding through the batch-invariant decode path;
  - chunked prefill crossing the sparse boundary;
  - speculative-rollback "trim" (commit 2 of 5);
  - the per-expert and fused-expert checkpoint layouts.
- bf16 is within bf16 noise of the reference and of our port.
- **Our Sol port** matches the reference at ≤ 1.0e-6 fp32 on every scenario and every config, including D1's ragged continuation.

## Versions (isolated venv `/private/tmp/jwsol/venv-mlxvlm`, Python 3.13.18)

| Package | Version |
|---|---|
| mlx-vlm | **0.7.12** (PyPI latest; released 2026-11-04) |
| mlx / mlx-metal | 0.32.4 / 0.32.4 (pulled in by mlx-vlm) |
| torch | 2.15.0 |
| transformers | 5.22.1 |
| safetensors | 0.8.0 |
| numpy | 2.5.4 |
| (also pulled in) | mlx-audio 0.6.4; mlx-lm **not** installed |

- **The installed source is current main.** Git blob SHAs of the installed `qwen4_exp/language.py` (9a9bee24), `qwen3_5/language.py` (e595e886) and `qwen3_5/speculative_verifier.py` (44790ad7) equal `Neywa-Labs/mlx-vlm@main` 5cdc659b, fetched 2026-11-05 via the contents API.
- **Reference**: `/private/tmp/jwsol/venv-ref` (torch 2.15.0, transformers 5.22.1, eager attention).
- **Our port**: `jw-wt/sol-flashnext-port`, branch `lane/2026-11-05-align-flashnext-port`, HEAD 28d153449 (model files last changed at 7704dd2cc). It runs on the pinned mlx 0.31.2 / mlx-lm 0.31.3 (`/private/tmp/jwsol/venv-mlx`).
- **Resources**:
  - peak RSS: reference 385 MB, mlx-vlm suite 466 MB, T3 425 MB, port 140 MB;
  - venv 1.7 GB, scratch about 0.15 GB (`/private/tmp/jwmlxvlm-tmp`);
  - run with nice 10–20, `OMP_NUM_THREADS=2`.
- Community mlx-lm PR #1788 was not executed. No restricted paths were read. Nothing was posted to GitHub (`gh` was used only for read-only API GETs).

## Method

**Checkpoints.** `ref_gen.py` builds tiny random `Qwen4ExpForCausalLM` models in transformers. It then saves them through `Qwen4ExpForConditionalGeneration.save_pretrained` in the **real checkpoint layout**:

- `model.language_model.*` keys, `ngram_embedding.shard_i` and a tiny vision tower;
- a second copy with the **fused** `experts.gate_up_proj` [E, 2I, H] / `experts.down_proj` that the official shards use.

As in our gold harness, norms are perturbed from zero (which exercises `1 + w`), the PLE conv is nonzero, and the DeltaNet gated-norm weight is set to `1 + 0.1·N`. Each fp32 checkpoint and its bf16 cast are run separately.

**Configs:**

- **A**: exactly the Sol gold tiny config. 2 layers [DeltaNet with PLE, QSA]; hc 2; budget 4, ratio 2; 11 tokens with an EOS inside.
- **B**: a discriminating config.
  - Real layer pattern [lin, lin(PLE at one-indexed layer 2), lin, QSA].
  - GQA 4/2; DeltaNet 2 key heads × 6 value heads (ratio 3, like the real 16 → 48); hc 4; 8 experts, top 3.
  - The real `rope_parameters` with an `mrope_section`; budget 8, **ratio 4** (sparse from 12 visible tokens); 40 tokens with two EOS.
- **C**: B with 16 indexer heads (`indexer_n_heads=16`, so no exact-zero QSA ties) and every Linear in-dimension a multiple of 64 (so everything is quantizable). C carries T1.

**Sources compared:** `ref` (transformers), `port` (Sol port, via its own converter), `vlm` (mlx-vlm `load_model`), and `vlmP` (mlx-vlm with the D1 patch).

**Scenarios:**

- `prefill`;
- `stepwise` (token-by-token with the cache, which is mlx-vlm's batch-invariant decode path);
- `chunked` (prefill L/2+1, then 4-token chunks);
- `spec_rollback` (prefill L/2, speculate 5, `commit(2)`, continue; mlx-vlm's hybrid-cache trim);
- `padded_batch_valid` (a left-padded batch of 3 rows, pads [0, 4, L/3+1], built exactly as `BatchGenerator` builds it: `_make_cache(lm, left_padding)` plus the per-row zero-left-padded `position_ids` and the `rope_deltas` it forwards);
- `padded_continuation` (3 cached decode steps after that batch).

**Ground truth.** Every scenario is compared with the reference's **unpadded single-row prefill**. The reference's own scenario outputs (stepwise, padded with HF positions) match that truth to ≤ 7.5e-8 (A) and ≤ 5.6e-7 (B/C).

**Metrics:**

- **max abs** logit difference.
- **rel** = max abs / max|truth|.
- **cos** = cosine over all logits.
- For bf16, also **p50** (the median over positions of the per-position max abs, which is robust to one discrete flip) and **top-1** argmax agreement.

## Results

Cells are `max abs / rel / cosine`. "vs ref" means against the reference single-row truth. Full table: `scripts/audit_mlxvlm/results/compare_table.md`.

### fp32

| case | scenario | port vs ref | mlx-vlm vs ref | mlx-vlm vs port | mlx-vlm + D1 patch vs ref |
|---|---|---|---|---|---|
| A | prefill | 5.2e-08 / 1.9e-07 / 1.000000 | 6.0e-08 / 2.2e-07 / 1.000000 | 4.5e-08 / 1.6e-07 / 1.000000 | 6.0e-08 / 2.2e-07 / 1.000000 |
| A | stepwise | 7.5e-08 / 2.7e-07 / 1.000000 | 6.7e-08 / 2.5e-07 / 1.000000 | 3.7e-08 / 1.4e-07 / 1.000000 | 6.7e-08 / 2.5e-07 / 1.000000 |
| A | chunked | 6.7e-08 / 2.5e-07 / 1.000000 | 6.0e-08 / 2.2e-07 / 1.000000 | 4.5e-08 / 1.6e-07 / 1.000000 | 6.0e-08 / 2.2e-07 / 1.000000 |
| A | spec_rollback | n/a | 6.0e-08 / 2.2e-07 / 1.000000 | n/a | 6.0e-08 / 2.2e-07 / 1.000000 |
| A | padded_batch_valid | 5.2e-08 / 1.9e-07 / 1.000000 | 4.5e-08 / 1.6e-07 / 1.000000 | 4.5e-08 / 1.6e-07 / 1.000000 | 4.5e-08 / 1.6e-07 / 1.000000 |
| A | **padded_continuation** | 6.0e-08 / 2.6e-07 / 1.000000 | **3.0e-02 / 1.3e-01 / 0.993967** | 3.0e-02 / 1.3e-01 / 0.993967 | 6.0e-08 / 2.6e-07 / 1.000000 |
| B | prefill | 5.4e-07 / 7.5e-07 / 1.000000 | 1.2e-01 / 1.7e-01 / 0.998460 ᵗ | 1.2e-01 / 1.7e-01 / 0.998460 ᵗ | 1.2e-01 / 1.7e-01 / 0.998460 ᵗ |
| B | stepwise | 7.5e-07 / 1.0e-06 / 1.000000 | 1.2e-01 / 1.7e-01 / 0.998460 ᵗ | 1.2e-01 / 1.7e-01 / 0.998460 ᵗ | 1.2e-01 / 1.7e-01 / 0.998460 ᵗ |
| B | chunked | 6.1e-07 / 8.6e-07 / 1.000000 | 1.2e-01 / 1.7e-01 / 0.998460 ᵗ | 1.2e-01 / 1.7e-01 / 0.998460 ᵗ | 1.2e-01 / 1.7e-01 / 0.998460 ᵗ |
| B | spec_rollback | n/a | 1.2e-01 / 1.7e-01 / 0.998380 ᵗ | n/a | 1.2e-01 / 1.7e-01 / 0.998380 ᵗ |
| B | padded_batch_valid | 6.9e-07 / 9.6e-07 / 1.000000 | 1.2e-01 / 1.7e-01 / 0.998193 ᵗ | 1.2e-01 / 1.7e-01 / 0.998193 ᵗ | 1.2e-01 / 1.7e-01 / 0.998193 ᵗ |
| B | **padded_continuation** | 6.4e-07 / 1.0e-06 / 1.000000 | **1.4e-01 / 2.3e-01 / 0.978880** | 1.4e-01 / 2.3e-01 / 0.978880 | 6.7e-07 / 1.1e-06 / 1.000000 |
| C | prefill | 8.3e-07 / 1.0e-06 / 1.000000 | 7.3e-07 / 9.0e-07 / 1.000000 | 5.1e-07 / 6.3e-07 / 1.000000 | 7.3e-07 / 9.0e-07 / 1.000000 |
| C | stepwise | 9.7e-07 / 1.2e-06 / 1.000000 | 9.5e-07 / 1.2e-06 / 1.000000 | 3.3e-07 / 4.0e-07 / 1.000000 | 9.5e-07 / 1.2e-06 / 1.000000 |
| C | chunked | 8.5e-07 / 1.0e-06 / 1.000000 | 6.6e-07 / 8.2e-07 / 1.000000 | 4.8e-07 / 5.9e-07 / 1.000000 | 6.6e-07 / 8.2e-07 / 1.000000 |
| C | spec_rollback | n/a | 6.6e-07 / 8.2e-07 / 1.000000 | n/a | 6.6e-07 / 8.2e-07 / 1.000000 |
| C | padded_batch_valid | 8.8e-07 / 1.1e-06 / 1.000000 | 7.3e-07 / 9.0e-07 / 1.000000 | 5.7e-07 / 7.1e-07 / 1.000000 | 7.3e-07 / 9.0e-07 / 1.000000 |
| C | **padded_continuation** | 4.8e-07 / 7.5e-07 / 1.000000 | **1.5e-01 / 2.4e-01 / 0.982456** | 1.5e-01 / 2.4e-01 / 0.982456 | 4.8e-07 / 7.5e-07 / 1.000000 |

ᵗ = P3 (exact-zero QSA tie) only.

- In B, 2 of the 40 positions differ (queries 12 and 13 of the QSA layer, §P3). The per-position median is 3.3e-7, and top-1 agreement is 1.000.
- Prefill without a cache and the per-expert checkpoint layout give results identical to `prefill` in every case (`results/compare_table.md`).

### bf16 (each source vs the fp32 reference truth; `max abs / p50 / top-1 / cosine`)

The yardstick is the reference's own bf16 error.

| case | scenario | ref bf16 | port bf16 | mlx-vlm bf16 | mlx-vlm + D1 bf16 |
|---|---|---|---|---|---|
| A | prefill | 1.4e-03 / 1.1e-03 / 1.000 / 0.99999 | 1.4e-03 / 1.1e-03 / 1.000 / 0.99999 | 1.5e-03 / 1.3e-03 / 1.000 / 0.99998 | same |
| A | stepwise | 1.4e-03 / 1.1e-03 / 1.000 / 0.99999 | 1.4e-03 / 1.1e-03 / 1.000 / 0.99999 | 1.8e-03 / 1.3e-03 / 1.000 / 0.99998 | same |
| A | padded_continuation | 1.2e-03 / 9.2e-04 / 1.000 / 0.99999 | 1.5e-03 / 1.1e-03 / 1.000 / 0.99999 | **3.0e-02 / 1.9e-02 / 1.000 / 0.99399** | 2.5e-03 / 1.0e-03 / 1.000 / 0.99996 |
| B | prefill | 2.6e-02 / 7.4e-03 / 0.950 / 0.99986 | 2.7e-02 / 7.3e-03 / 0.975 / 0.99982 | 1.2e-01ᵗ / 1.0e-02 / 0.975 / 0.99794 | same |
| B | padded_continuation | 1.3e-02 / 7.8e-03 / 1.000 / 0.99989 | 1.9e-02 / 8.4e-03 / 1.000 / 0.99977 | **1.4e-01 / 1.1e-01 / 0.667 / 0.97857** | 2.1e-02 / 1.4e-02 / 1.000 / 0.99964 |
| C | prefill | 1.6e-01 / 8.7e-03 / 1.000 / 0.99815 | 2.3e-01 / 9.2e-03 / 1.000 / 0.99694 | 2.2e-01 / 1.2e-02 / 0.975 / 0.99693 | same |
| C | stepwise | 1.6e-01 / 8.7e-03 / 1.000 / 0.99815 | 2.3e-01 / 9.6e-03 / 1.000 / 0.99694 | 2.2e-01 / 1.2e-02 / 0.975 / 0.99693 | same |
| C | padded_batch_valid | 1.6e-01 / 9.0e-03 / 1.000 / 0.99833 | 2.3e-01 / 9.9e-03 / 1.000 / 0.99709 | 2.2e-01 / 1.2e-02 / 0.971 / 0.99707 | same |
| C | padded_continuation | 8.0e-03 / 7.1e-03 / 0.889 / 0.99991 | 1.5e-01 / 8.1e-03 / 0.667 / 0.99425 | **1.5e-01 / 9.9e-02 / 0.556 / 0.98180** | 1.7e-01 / 1.0e-02 / 0.889 / 0.99193 |

**Reading the bf16 table.**

- In B and C, every bf16 implementation, **including the reference itself**, has max-abs errors of 0.16–0.23 against the fp32 truth. These are discrete bf16 flips: QSA block selection, MoE routing and near-tied argmax. Max abs is therefore not a usable bf16 criterion here.
- On the robust median, mlx-vlm sits at 1.0–1.2e-2, against 7–10e-3 for the reference and our port. That is within bf16 noise, slightly above the other two, and consistent with P1/P2.
- Direct mlx-vlm vs port (bf16): A 9.8e-4; C 3.0e-2 / p50 1.2e-2 / cosine 0.99966.
- D1 is the only bf16 deviation of a different class: p50 ×10.

## D1: ragged-batch QSA drops the sparse selection (confirmed bug, real user path)

**T1, logits level** (`t1_ragged.py`, config C).

- Setup:
  - prompts of 20 and 17 tokens, left padding [0, 3], built exactly as `BatchGenerator` builds them;
  - 4 teacher-forced greedy decode steps (the reference's greedy tokens);
  - then a 3-token verify through `LanguageModel.speculative_verify_logits` (the MTP verifier);
  - an equal-length batch [A, A] as the control.
- Cells are max |Δlogit| against the reference. Results are identical through the batch-invariant decode path and the main path.

| fp32 | prompt | decode 1–4 | verify 1–3 |
|---|---|---|---|
| single request A / B | 4.2e-07 / 6.7e-07 | ≤ 6.6e-07 | ≤ 5.4e-07 |
| equal-length control, both rows | 4.2e-07 | ≤ 6.6e-07 | ≤ 7.7e-07 |
| **ragged row 0 (pad 0, unpadded!)** | 4.2e-07 | **1.3e-01, 1.1e-01, 6.9e-02, 1.3e-01** | **1.2e-01, 9.1e-02, 8.8e-02** |
| **ragged row 1 (pad 3)** | 6.7e-07 | **1.0e-01, 8.1e-02, 1.9e-01, 8.6e-02** | **1.0e-01, 6.5e-02, 1.2e-01** |
| ragged rows 0 / 1, **D1 patch** (monkeypatch or source diff) | 4.2e-07 / 6.7e-07 | ≤ 6.6e-07 / ≤ 6.1e-07 | ≤ 7.7e-07 / ≤ 5.4e-07 |

In bf16, the patched ragged rows equal the single-request bf16 errors (1e-2 class). Unpatched, they are off by 0.05–0.14.

**T1, real entry point** (`t1_batchgen.py`).

- This test replicates `mlx_vlm.generate.ar.batch_generate`'s text-only body verbatim:
  - `get_input_embeddings` on the padded batch with its mask;
  - per-row prompt kwargs;
  - `BatchGenerator.insert(attention_mask=…)`;
  - the `gen.next()` loop, with greedy sampling and `compute_logprobs`.
- Only the processor is a stub, because the tiny model has no tokenizer.

| row | released 0.7.12 | with the D1 patch |
|---|---|---|
| single request A / B | 7/7 tokens = reference; max \|Δlogprob\| 3.5e-7 / 4.1e-7 | same |
| equal-length control | 7/7; 3.5e-7 | same |
| **ragged row 0 (A, pad 0)** | **5/7 tokens agree (diverges at token 6)**; max \|Δlogprob\| **0.077** | 7/7; 3.5e-7 |
| **ragged row 1 (B, pad 3)** | **6/7 tokens agree**; max \|Δlogprob\| **0.061** | 7/7; 4.1e-7 |

**Trigger and impact.**

- With a ragged batch cache, decode (and the batched multi-token verify) runs dense attention over each row's unpadded keys.
- Dense attention equals QSA only while every row has `complete blocks ≤ block_topk`. On the real config that means visible context ≤ 2051 tokens.
- Above that, every QSA layer (12 of 48) attends to all keys instead of top-512 blocks plus the tail. The effect is silent, affects all rows (the unpadded one too), and compounds token by token.
- Real exposure: `mlx_vlm.server` continuous batching or `batch_generate` with prompts of different lengths and long context. This is the agent-workload regime.
- JouleWise is unaffected while it serves one request at a time. **It must not enable mlx-vlm batching for Flash-Next until this is fixed.**

**Root cause** (mlx-vlm 0.7.12 = main):

1. `Qwen4ExpAttention.__call__` (`qwen4_exp/language.py:1099-1122`) runs the indexer, then for any string mask other than "causal" (that is, `"left_padded_decode"`, which `_create_qwen3_5_attention_mask` returns for L = 1 with left padding) returns `super().__call__(...)`. That discards `selection`.
2. `Qwen4ExpBatchInvariantForward._qsa_attention` is the decode path actually used (`:1869-1893`). It builds `qsa_mask` but merges it only into `None`, `"causal"` or array masks. It then calls `_attention`, which routes `"left_padded_decode"` and every padded L > 1 call to `_qwen3_5_left_padded_attention`.
3. `_qwen3_5_left_padded_attention` never reads its `mask` argument (`qwen3_5/language.py:878-940`; `speculative_verifier.py:97-112`).
4. Prefill is unaffected because it runs row by row on unpadded rows (`:1624-1711`).

**Upstream status: is it a deliberate trade-off, already fixed, or reported?** (read-only `gh api`, 2026-11-05)

- **Introduced by merged PR #2126** ("Optimize Qwen4 QSA cache reuse and batched parity", Blaizzy, merged 2026-09-04, d68a25e71).
  - Its diff adds the delegation together with the comment *"Qwen3.5 owns specialized string modes such as `left_padded_decode`. The indexer state is already updated; delegate only the Q/K/V attention path to the parent."* The intent was to keep QSA semantics and delegate only the Q/K/V computation.
  - The PR body says *"QSA selection follows the Transformers block-pooling, ReLU scoring, top-k…"* and *"Ragged, masked, decode, short-context, and unsupported cases retain the **dense reference path**"*. Here "dense reference path" means the materialized selected-token-mask SDPA, as opposed to the new indexed Metal kernel. It does not mean dropping the selection.
  - Its parity evidence covers only equal-length rows:
    - `test_batched_qsa_cache_decode_matches_singleton_rows` uses two 10-token prompts;
    - `test_ragged_qsa_batch_retains_explicit_mask` checks only the prefill mask shape;
    - the real-model table uses 16K equal-context batches.
  - Ragged *decode* parity was never tested. So D1 is **not a documented trade-off**; it is an unintended regression introduced by that PR.
- **Not fixed.** `qwen4_exp/language.py` last changed 2026-10-13 (#2273); main HEAD is 5cdc659b (2026-11-05T02:18Z), blob-identical to 0.7.12.
- **Not reported.** Issue/PR searches ("qwen4 left_padded_decode", "QSA ragged", "QSA left padding", "qwen4_exp batch decode", "Qwen3.8 batch", "qwen4 sparse attention batch") find only unrelated items:
  - #2345, closed unmerged: Qwen3.5 decode skipping the left-padding mask after a right-padded prefill, a stale-metadata problem.
  - #2197, open: `BatchQSAKVCache` ragged speculative *rollback* crashing on `c.keys`.
  - #2039, closed: QSA cache conversion.
  - #2581 / #2630: DFlash on qwen4_exp.
  - None concerns the QSA selection being dropped.
- **Classification: confirmed bug on a real user path, unreported and unfixed.** It is a clean candidate for Ed's first upstream contribution. The reproducer needs only mlx-vlm, and the fix is small and local.

**Patch draft.** `scripts/audit_mlxvlm/d1_qsa_left_padding.patch`, 87 lines, which `git apply -p1` accepts at the mlx-vlm repo root.

- In `Qwen4ExpAttention.__call__`, `"left_padded_decode"` now builds `self.indexer.build_mask(selection)` and continues into the existing masked-SDPA dispatch. `build_mask` already offsets blocks by each row's left padding and excludes pad columns.
- In `_qsa_attention`, `"left_padded_decode"` is merged like `"causal"`. Padded calls then go through a new `_masked_attention` (Q/K/V projection, `_prepare_projected_qkv`, masked SDPA, `o_proj`) instead of the mask-ignoring ragged helper.
- Dense prefixes (`selection is None`) keep the existing exact ragged path.
- Validated as a source overlay (no venv change):
  - T1 fp32 ≤ 7.7e-7, both paths and verify;
  - bf16 at single-request level;
  - `BatchGenerator` tokens 7/7 with logprobs ≤ 4.1e-7;
  - the standalone reproducer exact.
- Cost: one boolean mask over [B, L, keys] and a masked SDPA per padded decode step, the same as the module's existing `DENSE_MASKED` fallback. An indexed-kernel variant with per-row left padding would be the optimized follow-up.

## P3 (T4): QSA top-k tie order at exact-zero scores (recorded; implementation-defined)

`bisect_layers.py` and then `bisect_qsa.py` on B, fp32. Every DeltaNet, MoE, PLE and hyper-connection sub-module matches at ≤ 2.4e-7, and so does every QSA query except two.

| query | block scores (Σ relu over 2 heads / √16) | reference selects | mlx-vlm selects |
|---|---|---|---|
| 12 | [1.7097, **0, 0**] | blocks {0, 1} | blocks {0, 2} |
| 13 | [**0**, 1.1673, **0**] | blocks {0, 1} | blocks {1, 2} |

Those two queries differ by 0.057 and 0.043 in attention output; all others match at ≤ 4.5e-8.

- **mlx-vlm** (`argpartition(scores, kth=-k)[..., -k:]`) systematically keeps the **later** zero-score blocks.
- **`torch.topk` on CPU** (torch 2.15.0) is not "lowest index first" either:
  - [0,0,5,0,0], k=2 → {1,2};
  - [0,0,0,0,5], k=2 → {1,4};
  - [1,0,0,2,0,0,0], k=3 → {0,2,3};
  - all zeros, k=3 → {0,1,2}.
- With 2 indexer heads, exact-zero scores are common: a block is zero whenever all head dots are negative. With 16 heads (config C) the effect disappears.
- On the real model (4 heads), a zero tie at the cut needs fewer than 512 positive-score blocks while there are more than 512 complete blocks. That happens at about 2–3K-token contexts and with sparse learned indexers.
- **Relevance to our port** (the lane may want this): Sol's efae852c1 made QSA top-k deterministic as "score descending, then lowest block index". That is reproducible, but **it will not always match `torch.topk`**, because of the CPU tie order above.
- **Gold harnesses need tie-free fixtures** (like config C) or tie-aware comparison, meaning selection sets equal modulo equal-score swaps. Otherwise they can fail spuriously, or pass by luck as config A does.

## P1 (T2): router top-k on bf16 softmax output

- **Unit test** (`t_misc.py`):
  - logits `[3.0]×9 + [0.5, 0.50390625] + [−1.0]×501` (bf16), 512 experts, top 10;
  - softmax output dtype: **bf16** (confirmed);
  - experts 9 and 10 round to the identical bf16 probability, 0.0044860840. In fp32 they are 0.0044755861 and 0.0044931029;
  - selected set on the main path, the decode path and the reference: all {0–8, 10}. On this MLX build, argpartition happened to resolve the exact tie the reference's way.
- **Synthetic rate**: 20k tokens of N(0, σ) logits, rounded to bf16 because both implementations see bf16 router logits.

| σ | top-10 set differs (mlx-vlm vs reference) | of which: exact tie already in fp32 (tie order) | of which: bf16 rounding created the tie (**P1 proper**) | max \|Δweight\| (same set) |
|---|---|---|---|---|
| 0.5 | 8.9 % | 7.6 % | **1.3 %** | 0.0017 |
| 1 | 7.3 % | 7.3 % | 0 % | 0.0027 |
| 2 | 7.5 % | 7.5 % | 0 % | 0.0046 |
| 4 | 7.4 % | 7.4 % | 0 % | 0.0040 |

- P1 proper is minor. Fix: softmax in fp32, as in the reference and our port.
- The larger effect: about 14 % of tokens carry an **exact bf16 tie** at the rank-10/11 boundary already in the logits. The reference itself is then tie-order dependent, so expect discrete routing mismatches in any bf16 cross-implementation comparison, ours included.
- Recommendation for P4 real-weight parity: compare routing in fp32, or tie-aware.

## P2 (T3): DeltaNet bf16 gating and normalization; no long-context drift

- Setup (`t3_deltanet.py`):
  - layer 0 of B (2 × 6 heads), identical bf16 inputs, 8192 tokens in 512-token chunks through each cache;
  - truth = transformers fp32 on the same weights.
- The relative Frobenius error of the recurrent state:

| | T = 512 | 2048 | 8192 | out max\|Δ\|/rms (first / last window) |
|---|---|---|---|---|
| transformers bf16 | 4.4e-3 | 4.1e-3 | 4.1e-3 | 0.042 / 0.041 |
| **mlx-vlm bf16** | 6.6e-3 | 7.4e-3 | 7.9e-3 | 0.082 / 0.067 |
| mlx-vlm + P2 fp32 gating/norm (`p2_patch.py`) | 6.2e-3 | 7.1e-3 | 7.0e-3 | 0.081 / 0.047 |
| Sol port bf16 | 6.2e-3 | 6.1e-3 | 6.6e-3 | 0.081 / 0.051 |

- The error plateaus; it does not grow with T. mlx-vlm is ≤ 1.2× our port and under 2× the reference's own bf16 error, so the static audit's bug threshold (> 2× and growing) is not met.
- The P2 patch closes about half of the gap to our port. The rest, shared by both MLX ports, is MLX bf16 matmul/conv rounding.
- **Classification: minor deviation, not a defect.** `p2_patch.py` is kept as an optional fidelity improvement; no `.patch` is needed.

## P5 (T6): left-padded batch without a cache

- `lm(ids[2, L], attention_mask=mask)` with no cache:
  - tiny config C checkpoint: unpadded row 1.0e-6, **padded row 0.61** max abs;
  - standalone reproducer: unpadded row 7.2e-7, **padded row 0.89**;
  - nothing is raised.
- Cause: `LanguageModel.__call__` uses the mask only for RoPE positions. Padding is honoured only through a batch cache's `left_padding`, so attention is causal over pads and the PLE hashes pad ids.
- Generation is unaffected because it always uses a cache. Scoring-style callers are exposed.
- Patch draft `p5_padded_no_cache.patch` fails loudly with `NotImplementedError`. A row-wise scoring fallback is the fuller fix.

## F1: transformers-saved configs are rejected

- `Qwen4ExpTextConfig` rewrites the checkpoint's `"full_attention"` to `"indexed_attention"` and writes that on `save_pretrained`. mlx-vlm maps only `"full_attention"` and raises `ValueError`.
- Once that is fixed, transformers' default `output_gate_type=None` is rejected next: `"must be 'sigmoid' or 'silu'"`. mlx-vlm's own gated norm already handles `None` via `hidden_act`.
- Affects: any fine-tuned, merged or re-saved Flash-Next checkpoint, and every tiny test model.
- Patch draft `f1_indexed_attention_layer_type.patch` (config.py, 2 hunks).
  - Validated: the transformers-saved C checkpoint loads unmodified and matches the reference at 7.3e-7 fp32.
  - The default-config model matches transformers to 6e-8 in dense mode; one P3 tie position appears in sparse mode.
  - The audit itself loaded mlx-vlm through a symlinked view whose config used `full_attention`, with identical weights.

## Quantization path (mlx-vlm `convert(quantize=True)`, config C bf16)

- `mlx_vlm.convert.convert` ran without a tokenizer: "Quantized model with 5.048 bits per weight" at 4-bit.
- Quantization status of the **82** quantized modules:
  - **QSA indexer `index_qk_proj`: quantized at the global width** (4b g64, or 6b g64);
  - **router `mlp.gate` and `shared_expert_gate`: 8b g64**;
  - hyper-connection `input_mix_weight_{down,up}` and `block_inject_weight`: global width;
  - DeltaNet `in_proj_*` and `out_proj`, attention projections, `switch_mlp` experts, PLE `key_proj`/`value_proj`, `embed_tokens` and `lm_head`: global width;
  - **left in float**: only the n-gram PLE shards (16-wide rows fit neither g64 nor the g32 fallback).
- Logits (the tiny random weights are not quantization-friendly, so treat these as a status check, not a quality estimate):

| | 4-bit g64 | 6-bit g64 |
|---|---|---|
| vs mlx-vlm bf16 (max / p50 / top-1) | 0.45 / 0.23 / 0.475 | 0.22 / 0.058 / 0.825 |
| quantized stepwise vs quantized prefill | 0.13 / 9.8e-3 / 0.925 | 0.053 / 1.5e-2 / 0.900 |

- The quantized model's decode and prefill disagree far more than the bf16 model's do (bf16: p50 0, max 3.9e-3). This is the shape-dependent quantized-GEMM rounding that upstream tracks as NEY-130 (PR #2126 follow-up), amplified by discrete QSA and MoE choices.
- The GOAL's precision target (6-bit experts, everything else bf16) cannot be expressed with mlx-vlm's default predicate (static audit L1). It needs a custom `quant_predicate`.

## Other notes

- **N4 (API hazard, LOW).** Calling `LanguageModel` on a left-padded batch cache **without** the `position_ids` and `rope_deltas` that `BatchGenerator` forwards is not safe:
  - row-wise prefill RoPEs the padded row at physical columns `pad..W-1`, but decode uses real offsets;
  - the padded row then stays wrong (about 0.1) even with the D1 patch;
  - `LanguageModel.__call__`'s own left-padding mask fallback never fires for batch caches, because `cache_offsets` is set.
  - The real entry point passes the metadata, so this is a latent hazard for direct callers.
- **Eagle3/DFlash** call `lm(..., speculative_verify=True)`, which routes Qwen4 into the Qwen3.5 verifier. That verifier has no hyper-connections. This is already reported upstream as #2581, with open fix PR #2630, so it was not re-tested.
- **T5** (APC right-padding, P4 of the static audit) was skipped as instructed.

## Artifacts (`scripts/audit_mlxvlm/`)

**Harness:**

- `ref_gen.py`: reference checkpoints and logits (venv-ref).
- `run_vlm.py [--patched]`: the mlx-vlm suite.
- `run_port.py`: our port (venv-mlx).
- `compare.py`: the three-way tables.

**T-tests:**

- `t1_ragged.py`, `t1_batchgen.py`: D1 at logits level and through `BatchGenerator`.
- `t_misc.py`: T2, T6, F1.
- `t3_deltanet.py`: P2.
- `t_quant.py`: the quantization path.
- `bisect_layers.py`, `bisect_qsa.py`: P3 localization.

**Reproducers (standalone, mlx-vlm only):**

- `repro_d1_ragged_qsa.py [--patched]`
- `repro_p5_padded_no_cache.py`
- `repro_f1_indexed_attention.py OUT_DIR` (also needs transformers)

**Patch drafts (draft only; nothing posted):**

- `d1_qsa_left_padding.patch`, plus the `d1_patch.py` monkeypatch used in tests.
- `f1_indexed_attention_layer_type.patch`.
- `p5_padded_no_cache.patch`.
- `p2_patch.py` (optional fidelity patch, monkeypatch form).

**Results:** `results/` holds `compare_table.md`/`compare.json`, the T1/T2/T3/T6/quant JSON, P3 bisection output, and reference/mlx-vlm metadata.

**Rerun** (scratch in `/private/tmp/jwmlxvlm-tmp`):

```
REF=/private/tmp/jwsol/venv-ref/bin/python VLM=/private/tmp/jwsol/venv-mlxvlm/bin/python MLX=/private/tmp/jwsol/venv-mlx/bin/python
$REF -I ref_gen.py WORK; $MLX -I run_port.py WORK SOL_CLONE; $VLM run_vlm.py WORK; $VLM run_vlm.py WORK --patched
$MLX -I compare.py WORK; $VLM t1_ragged.py WORK/C_fp32 [--patched]; $VLM t1_batchgen.py WORK/C_fp32 [--patched]
$VLM t_misc.py WORK; $VLM t_quant.py WORK 4 64; t3_deltanet.py {ref|vlm|port|cmp} ...; $VLM repro_d1_ragged_qsa.py [--patched]
```
