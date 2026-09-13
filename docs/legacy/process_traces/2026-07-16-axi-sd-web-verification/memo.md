# AXI-SD web-verification memo — dense/MoE candidate pairs + §8 ladder subject

Date: 2026-07-16. Agent: Fable web-verification subagent (read-only; no repo files edited).
Scope: fills NEEDS-VERIFICATION *factual* cells of
`docs/specs/axi/sd_model_pair_scorecard.md` (§6 candidate table, §8 ladder subject) with
primary-source evidence. This memo adjudicates **nothing** in §7 and passes **no** gate:
G2 (tokenizer byte-identity), G3 (measured routing probe), G4–G8 (join key), G9–G12 all
still require local receipts. Every number below sourced from Hugging Face configs/API or
upstream runtime source trees at fetch time (2026-07-16); revisions cited are the `main`
head SHAs returned by the HF API at fetch time and should be re-resolved and pinned at
mirror time per §8.2.

Confidence legend:
- **HIGH** — read directly from a primary machine artifact (config.json, HF API JSON, runtime source file).
- **MED** — arithmetic derived from HIGH inputs (shown in full); or config-implied value that the scorecard requires to be *measured* (e.g. top-k dispatch).
- **UNVERIFIED** — could not be confirmed from a primary source; never guessed.

## 0. Summary table

| Pair / subject | Dense repo (rev) | MoE repo (rev) | d_active (config-derived, MED) | 4-bit weight lower bound vs 6.8 GiB allowed peak | License | Verdict (informative) |
|---|---|---|---|---|---|---|
| `olmo-1b__olmoe-1b7b` | `allenai/OLMo-1B-0724-hf` @ `d7cbab7` (alt: `OLMo-1B-hf` @ `aee7752`) | `allenai/OLMoE-1B-7B-0924` @ `6d84c48` | **0.0016** (0724) / 0.086 (0224) | dense ~0.95 GiB, MoE ~3.9 GiB → both PASS lower bound | Apache-2.0 both (HIGH) | **Viable on verified facts**; risks: G1 generation wording, no instruct dense variant, MLX dense-OLMo load path UNVERIFIED |
| `qwen3-4b__qwen3-30b-a3b` | `Qwen/Qwen3-4B` @ `1cfa9a7` | `Qwen/Qwen3-30B-A3B` @ `ad44e77` | **0.181** | dense ~2.5 GiB PASS; MoE ~15–17 GiB → **FAIL(weight_lower_bound)** for any 8 GiB target | Apache-2.0 both (HIGH) | Likely-FAIL G10 on d016-cross-target; viable only for `axi-mac-only` |
| `qwen1.5-4b__qwen1.5-moe-a2.7b` | `Qwen/Qwen1.5-4B` @ `a66363a` | `Qwen/Qwen1.5-MoE-A2.7B` @ `1a758c5` | **0.380** → FAIL(active_mismatch) if measurement confirms | dense ~2.9 GiB PASS; MoE ~8.3 GiB (recipe) / 6.67 GiB (crude floor) → **likely FAIL(weight_lower_bound)** | dense: tongyi-qianwen-research; MoE: tongyi-qianwen ("other") — **not Apache; mismatched licenses** | Likely-FAIL G3 (and G8 risk, G10 risk) |
| §8 ladder subject | `Qwen/Qwen2.5-1.5B-Instruct` @ `989aa79` | — | — | ~0.9 GiB at Q4_G64 | Apache-2.0 (HIGH) | Viable ladder source; community 4/8-bit+bf16 MLX artifacts exist as discovery evidence |

Allowed-peak context used throughout: proposed §4.2 rule on an 8 GiB-class target gives
`C_t = 8 GiB`, reserve `max(1 GiB, 0.15×8 GiB) = 1.2 GiB`, so `M_peak ≤ 6.8 GiB`; raw
quantized weight bytes exceeding 6.8 GiB is `FAIL(weight_lower_bound)` without a smoke.
This rule is still PROPOSED-FOR-ED; the FAIL labels below are conditional on it (or any
rule of similar magnitude).

Quant-recipe bit-cost model used for estimates (from §3.2 frozen MLX recipe: INT4 g64,
FP16 scale+bias per group): `4 + 2×16/64 = 4.5 bits/weight` for quantized classes
(`attention`, `dense_mlp`, `expert_mlp`, `shared_experts`); `embeddings`, `router`,
`norms`, `head`, biases retained BF16 (16 bits). Q8_G64: `8 + 0.5 = 8.5 bits/weight`.
These are estimates (MED), not artifact manifests.

---

## 1. Pair `olmo-1b__olmoe-1b7b`

### 1.1 Repositories and variants (HIGH)

MoE member — `allenai/OLMoE-1B-7B-0924`:
- Exists, public, not gated, license `apache-2.0`, main SHA `6d84c48581ece794365f2b8e9cfb043c68ade9c5`, safetensors total **6,919,161,856** BF16 params. Source: https://huggingface.co/api/models/allenai/OLMoE-1B-7B-0924
- Instruct variant exists: `allenai/OLMoE-1B-7B-0924-Instruct` (SHA `7f1c97f440f06ce36705e4f2b843edb5925f4498`, apache-2.0, 6.919B). Source: https://huggingface.co/api/models/allenai/OLMoE-1B-7B-0924-Instruct — and an SFT variant `allenai/OLMoE-1B-7B-0924-SFT` (search hit: https://huggingface.co/allenai/OLMoE-1B-7B-0924-SFT).
- Later generation exists: `allenai/OLMoE-1B-7B-0125` (SHA `9b0c1aa87e34a20052389dce1f0cf01da783f654`, apache-2.0, F32, 6,919,161,856 params, same architecture/vocab per its config). Sources: https://huggingface.co/api/models/allenai/OLMoE-1B-7B-0125 , https://huggingface.co/allenai/OLMoE-1B-7B-0125/raw/main/config.json

Dense member — two real candidates, both base-only:
- `allenai/OLMo-1B-0724-hf`: SHA `d7cbab742d80589e714b1a2d7f838dcd21cbe143`, apache-2.0, not gated, safetensors **1,279,787,008** F32 params. Source: https://huggingface.co/api/models/allenai/OLMo-1B-0724-hf
- `allenai/OLMo-1B-hf` (Feb-2024 gen): SHA `aee7752d9c08ee4775e9b0091426d8410e8f6a89`, apache-2.0, not gated, safetensors **1,176,764,416** F32 params. Source: https://huggingface.co/api/models/allenai/OLMo-1B-hf
- **No instruct/SFT variant of any first-gen OLMo-1B was found** (allenai instruct variants at 1B start with OLMo-2: `OLMo-2-0425-1B-Instruct`). Searches returned only 7B instruct/SFT for gen-1 and OLMo-2/3 families. Sources: https://huggingface.co/allenai/OLMo-7B-SFT , https://allenai.org/olmo/release-notes . Absence claim — treat as UNVERIFIED-negative (no primary "does not exist" receipt possible).
- OLMo-2 dense 1B is **not** tokenizer-compatible with OLMoE: `allenai/OLMo-2-0425-1B` config has `vocab_size 100352`, `eos_token_id 100257` (source: https://huggingface.co/allenai/OLMo-2-0425-1B/raw/main/config.json) vs OLMoE's 50304/50279 → an OLMo-2 dense arm would hard-FAIL G2 against either OLMoE generation.

Consequence (HIGH): the only tuning-state-consistent pairing is **base–base**
(OLMo-1B-0724-hf + OLMoE-1B-7B-0924). Instruct–instruct is impossible on the dense side.

### 1.2 Architecture facts (HIGH) and active-param arithmetic (MED)

`OLMo-1B-0724-hf` config (https://huggingface.co/allenai/OLMo-1B-0724-hf/raw/main/config.json):
`OlmoForCausalLM`, model_type `olmo`, 16 layers, hidden 2048, intermediate 8192,
16 heads / 16 KV heads, vocab 50304, `tie_word_embeddings: false`, eos 50279,
max_position 4096, torch_dtype float32.
(Older `OLMo-1B-hf`: same dims but `tie_word_embeddings: true`, max_position 2048 —
source: https://huggingface.co/allenai/OLMo-1B-hf/raw/main/config.json. The ~103.0M
param difference between the two = exactly one 50304×2048 embedding matrix, consistent
with untying.)

`OLMoE-1B-7B-0924` config (https://huggingface.co/allenai/OLMoE-1B-7B-0924/raw/main/config.json):
`OlmoeForCausalLM`, model_type `olmoe`, 16 layers, hidden 2048, expert intermediate 1024,
**64 experts, 8 per token, no shared-expert fields**, 16 heads / 16 KV heads, vocab 50304,
untied, eos 50279, max_position 4096.

Active-param arithmetic for OLMoE (config top-k; scorecard G3 requires *measured*
dispatch, so this is a precheck value only):
```
embeddings   50304×2048                    = 103,022,592
head (untied) 2048×50304                   = 103,022,592
attention    16 layers × 4×(2048×2048)     = 268,435,456   (+ q/k norms, negligible)
router       16 × (2048×64)                =   2,097,152
routed top-8 16 × 8 × 3×(2048×1024)        = 805,306,368   (gate+up+down per expert = 6,291,456)
norms        ~0.1M
P_active_moe ≈ 1,281.9M
Cross-check total: A(≈476.7M) + 64 experts×16×6,291,456 = 6,442,450,944 → 6,919.2M ✓ equals API total exactly.
```
Dense: `P_active_dense = 1,279.8M` (OLMo-1B-0724-hf API total; the API total itself
cross-checks: 103.0+103.0+268.4+16×3×(2048×8192)=805.3M → 1,279.7M, and OLMo gen-1 uses
non-parametric layernorm so norms add ≈0).

```
d_active = 2×|1279.8 − 1281.9| / (1279.8 + 1281.9) = 4.2/2561.7 = 0.0016   (vs gate 0.30)
```
With the older tied `OLMo-1B-hf`: `d_active = 2×105.1/2458.7 = 0.086`. Both pass the
precheck by an enormous margin. Confidence MED (config-derived top-k, not measured).

### 1.3 Memory arithmetic at 4-bit (MED)

```
OLMoE-0924, frozen MLX recipe:
  BF16-retained: emb 103.0 + head 103.0 + router 2.1 + norms ~0.1 ≈ 208.2M × 2 B = 0.416 GB = 0.388 GiB
  quantized:     6,919.2M − 208.2M = 6,711.0M × 4.5/8 B            = 3.775 GB = 3.516 GiB
  weight lower bound ≈ 3.90 GiB  ≤ 6.8 GiB allowed  → PASSES lower bound; ~2.9 GiB left
  KV at fit shape: 16 layers × 2(k,v) × (16×128) × 2 B = 131,072 B/token = 128 KiB/token
                   → 8,192-token prompt ≈ 1.00 GiB KV (fp16) → still ≈1.9 GiB slack before activations.
OLMo-1B-0724: retained (emb+head) 206.0M×2 = 0.412 GB; quantized 1,073.7M×0.5625 = 0.604 GB
  → lower bound ≈ 0.95 GiB → trivially passes. KV = 128 KiB/token as well (same dims).
```
Full §4.2 smoke still required; this only clears the `weight_lower_bound` screen.

### 1.4 Runtime and artifact availability

- **MLX, MoE arm:** `mlx_lm/models/olmoe.py` exists upstream (HIGH — listed at
  https://github.com/ml-explore/mlx-lm/tree/main/mlx_lm/models). mlx-community has an
  OLMoE collection, but **only the 0125 generation**: `mlx-community/OLMoE-1B-7B-0125`
  {,-Instruct}{,-4bit,-6bit,-8bit} (source: https://huggingface.co/collections/mlx-community/olmoe).
  `mlx-community/OLMoE-1B-7B-0125-4bit` config: `{"group_size": 64, "bits": 4}`, no
  per-module overrides (https://huggingface.co/mlx-community/OLMoE-1B-7B-0125-4bit/raw/main/config.json).
  **No mlx-community conversion of 0924 was found** (UNVERIFIED-negative). Not blocking:
  the frozen recipe requires local conversion from the frozen source anyway.
- **MLX, dense arm — RISK (HIGH evidence, adverse):** upstream
  `mlx_lm/models/olmo.py` targets the *original* AI2 OLMo config schema (`d_model`,
  `n_layers`, `mlp_hidden_size`, `weight_tying`) and requires `pip install ai2-olmo`
  (`hf_olmo`) — it does **not** parse the `-hf` converted `OlmoForCausalLM` config keys
  (source: https://raw.githubusercontent.com/ml-explore/mlx-lm/main/mlx_lm/models/olmo.py).
  mlx-lm dispatches on `model_type`, and `OLMo-1B-0724-hf` declares `model_type: "olmo"`,
  so an MLX load of the HF-format dense arm may fail or require the original-format
  `allenai/OLMo-1B-0724` checkpoint + ai2-olmo. **G4 MLX load for the dense arm is
  UNVERIFIED and is the pair's main runtime risk — needs a local load smoke before any
  freeze.** No mlx-community dense OLMo-1B conversion was found (UNVERIFIED-negative).
- **llama.cpp:** `llama-arch.cpp` contains both `LLM_ARCH_OLMO` ("olmo") and
  `LLM_ARCH_OLMOE` ("olmoe") (source: https://raw.githubusercontent.com/ggml-org/llama.cpp/master/src/llama-arch.cpp).
  allenai even publishes `allenai/OLMoE-1B-7B-0924-GGUF` (search hit: https://huggingface.co/allenai/OLMoE-1B-7B-0924-GGUF).
- **vLLM:** supported-models page lists `OlmoForCausalLM` (example `allenai/OLMo-1B-hf`)
  and `OlmoeForCausalLM` (example `allenai/OLMoE-1B-7B-0924`) —
  https://docs.vllm.ai/en/latest/models/supported_models.html . Note the dense entry is
  via the *Transformers modeling backend* table, not native vLLM — flags a runtime-parity
  nuance for G4 on CUDA.

### 1.5 License (HIGH)

Both arms `apache-2.0` per HF API (URLs above). Academic benchmarking and local
mirroring are compatible with Apache-2.0; the license *file* snapshot/hash for G8 must
still be taken locally.

### 1.6 Open items for this pair

Tokenizer byte-identity (both declare vocab 50304 / eos 50279 and NeoX-style tokenizers,
but §3.1 requires local subtree hashes — UNVERIFIED); G1 wording "same release
generation" for OLMo-1B-0724 (July 2024, Dolma 1.7) vs OLMoE-0924 (Sept 2024, OLMoE-mix)
is an Ed/G1 judgment, not a web fact; measured routing dispatch (G3); dense-arm MLX
path (above); F32→BF16 source conversion step (both dense checkpoints and OLMoE-0125 are
stored F32/F32/F32 — 0924 MoE is BF16 — the §3.2 "BF16 source" step must record this
downcast for the dense arm).

---

## 2. Pair `qwen3-4b__qwen3-30b-a3b`

### 2.1 Repositories and variants (HIGH)

- `Qwen/Qwen3-4B`: SHA `1cfa9a7208912126459214e8b04321603b3df60c`, apache-2.0, not
  gated, safetensors **4,022,468,096** BF16. https://huggingface.co/api/models/Qwen/Qwen3-4B
- `Qwen/Qwen3-30B-A3B`: SHA `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`, apache-2.0, not
  gated, safetensors **30,532,122,624** BF16. https://huggingface.co/api/models/Qwen/Qwen3-30B-A3B
- Matching base variants exist for both: `Qwen/Qwen3-4B-Base` (SHA `906bfd4b…8539`,
  4,022,468,096, apache-2.0; https://huggingface.co/api/models/Qwen/Qwen3-4B-Base) and
  `Qwen/Qwen3-30B-A3B-Base` (SHA `1b75feb7…a4f9`, 30.5B, apache-2.0;
  https://huggingface.co/api/models/Qwen/Qwen3-30B-A3B-Base). So both instruct(hybrid)
  and base pairings are available — good for G1.

### 2.2 Architecture facts (HIGH) and active-param arithmetic (MED)

`Qwen3-4B` config (https://huggingface.co/Qwen/Qwen3-4B/raw/main/config.json):
`Qwen3ForCausalLM`, 36 layers, hidden 2560, intermediate 9728, 32 heads / 8 KV heads,
head_dim 128, vocab 151936, **tie_word_embeddings: true**, eos 151645.

`Qwen3-30B-A3B` config (https://huggingface.co/Qwen/Qwen3-30B-A3B/raw/main/config.json):
`Qwen3MoeForCausalLM`, 48 layers, hidden 2048, moe_intermediate 768, **128 experts,
8 per token, decoder_sparse_step 1, mlp_only_layers []**, 32 heads / 4 KV heads,
head_dim 128, vocab 151936, tie_word_embeddings false, **no shared-expert fields**.
Qwen3-MoE having *no shared experts* is corroborated by the Qwen3 Technical Report
("the Qwen3-MoE design excludes shared experts", https://arxiv.org/html/2505.09388v1)
and by upstream mlx-lm `qwen3_moe.py`, whose MoE block is routed-experts-only with a
plain `nn.Linear` gate (https://raw.githubusercontent.com/ml-explore/mlx-lm/main/mlx_lm/models/qwen3_moe.py).

```
Per-expert per-layer: 3×(2048×768)          = 4,718,592
All experts: 4,718,592 × 128 × 48           = 28,991,029,248
A = total − experts = 30,532,122,624 − 28,991,029,248 = 1,541,093,376
  (contains emb 151936×2048 = 311,164,928; untied head 311,164,928; attention
   48×[2×(2048×4096) + 2×(2048×512)] = 48×18,874,368 = 905,969,664; router
   48×(2048×128) = 12,582,912; norms ≈ 0.2M — sums to 1,541.1M ✓)
routed_capacity (config top-8): 8 × 4,718,592 × 48 = 1,812,135,936
P_active_moe = 1,541,093,376 + 1,812,135,936 = 3,353,229,312  (≈3.35B; "A3B" label ✓)
P_active_dense = 4,022,468,096
d_active = 2×669,238,784 / 7,375,697,408 = 0.181
```
**Comfortably inside the 0.30 gate — NOT "near the gate" as the scorecard recalled**
(see Anomalies). Confidence MED (config top-k, not measured dispatch).

### 2.3 Memory arithmetic at 4-bit (MED) — the decisive fact

```
Crude floor (every param at exactly 4 bits): 30,532,122,624 × 0.5 B = 15.27 GB = 14.22 GiB
Frozen-recipe estimate: retained BF16 ≈ 635.1M×2 = 1.27 GB = 1.18 GiB
                        quantized 29,897.0M × 4.5/8 = 16.82 GB = 15.66 GiB
                        → ≈ 16.8 GiB weight lower bound
Empirical corroboration: mlx-community/Qwen3-30B-A3B-4bit weight shards total
  17,174,780,668 bytes = 16.00 GiB (4-bit, g64, embeddings also quantized there)
  — https://huggingface.co/api/models/mlx-community/Qwen3-30B-A3B-4bit/tree/main
Allowed peak on an 8 GiB-class target: 6.8 GiB.  14.2–16.8 GiB ≫ 6.8 GiB
  → FAIL(weight_lower_bound), no smoke needed, for EVERY 8 GiB D-016 target.
```
The scorecard's recalled "~15 GB ⇒ 8 GB FAIL" prediction is **confirmed** (actual
artifact 17.17 GB ≈ 16.0 GiB; crude 4-bit floor 15.27 GB). Dense arm is fine:
retained tied emb 311.2M×2 = 0.62 GB + quantized 3,710.9M×0.5625 = 2.09 GB → ≈2.52 GiB.

On the named large-memory Mac (`axi-mac-only` track), ~16–17 GiB weights + KV
(96 KiB/token × 8,192 ≈ 0.75 GiB) is plausible on a ≥32 GiB machine — that track's `C_t`
is the Mac's actual capacity, so no web-side verdict is possible.

### 2.4 Runtime artifacts (HIGH)

- `mlx-community/Qwen3-4B-4bit`: SHA `4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25`,
  apache-2.0, quantization `{"group_size": 64, "bits": 4}` —
  https://huggingface.co/mlx-community/Qwen3-4B-4bit/raw/main/config.json
- `mlx-community/Qwen3-30B-A3B-4bit`: SHA `d388dead1515f5e085ef7a0431dd8fadf0886c57`,
  apache-2.0, quantization `{"group_size": 64, "bits": 4}` —
  https://huggingface.co/mlx-community/Qwen3-30B-A3B-4bit/raw/main/config.json
  (Note: these community artifacts quantize embeddings too, which does NOT match the
  §3.2 module policy — discovery evidence only; local conversion still required.)
- mlx-lm upstream supports `qwen3_moe` (file fetched above) — a directory listing fetch
  that suggested otherwise was truncated/wrong; the raw file exists.
- llama.cpp: `LLM_ARCH_QWEN3` and `LLM_ARCH_QWEN3MOE` present in `llama-arch.cpp` (URL above).
- vLLM: `Qwen3ForCausalLM` and `Qwen3MoeForCausalLM` natively supported (supported-models URL above).

### 2.5 License (HIGH)

Apache-2.0 on all four repos (API receipts above). No gating.

---

## 3. Pair `qwen1.5-4b__qwen1.5-moe-a2.7b`

### 3.1 Repositories and variants (HIGH)

- `Qwen/Qwen1.5-4B`: SHA `a66363a0c24e2155c561e4b53c658b1d3965474e`, license
  **other / tongyi-qianwen-research**, not gated, safetensors **3,950,369,280** BF16.
  https://huggingface.co/api/models/Qwen/Qwen1.5-4B
- `Qwen/Qwen1.5-MoE-A2.7B`: SHA `1a758c50ecb6350748b9ce0a99d2352fd9fc11c9`, license
  **other / tongyi-qianwen**, not gated, safetensors **14,315,784,192** BF16.
  https://huggingface.co/api/models/Qwen/Qwen1.5-MoE-A2.7B
- Chat variants exist for both: `Qwen1.5-4B-Chat` (SHA `a7a4d494…`, tongyi-qianwen-research)
  and `Qwen1.5-MoE-A2.7B-Chat` (SHA `ec052fda…`, tongyi-qianwen). API URLs:
  https://huggingface.co/api/models/Qwen/Qwen1.5-4B-Chat ,
  https://huggingface.co/api/models/Qwen/Qwen1.5-MoE-A2.7B-Chat

### 3.2 Architecture facts (HIGH) and active-param arithmetic (MED)

`Qwen1.5-4B` config (https://huggingface.co/Qwen/Qwen1.5-4B/raw/main/config.json):
`Qwen2ForCausalLM`, 40 layers, hidden 2560, intermediate 6912, 20 heads / 20 KV heads,
vocab 151936, untied.

`Qwen1.5-MoE-A2.7B` config (https://huggingface.co/Qwen/Qwen1.5-MoE-A2.7B/raw/main/config.json):
`Qwen2MoeForCausalLM`, 24 layers, hidden 2048, **60 experts, 4 per token,
moe_intermediate 1408, shared_expert_intermediate 5632 (one always-on shared expert +
shared-expert gate), decoder_sparse_step 1**, 16 heads / 16 KV heads, vocab 151936, untied.

```
Per routed expert per layer: 3×(2048×1408)            = 8,650,752
All routed experts: 8,650,752 × 60 × 24               = 12,457,082,880
A + shared = 14,315,784,192 − 12,457,082,880          = 1,858,701,312
  (emb 311.2M + head 311.2M + attention-with-bias 24×16.79M ≈ 403.0M
   + shared expert 24×3×(2048×5632) = 830,472,192 + router 24×(2048×60+2048) ≈ 3.0M ✓)
routed (config top-4): 4 × 8,650,752 × 24             =    830,472,192
P_active_moe = 1,858,701,312 + 830,472,192            =  2,689,173,504  (≈2.69B; "A2.7B" ✓)
P_active_dense = 3,950,369,280
d_active = 2×1,261,195,776 / 6,639,542,784 = 0.380  →  > 0.30
```
If measured routing confirms top-4 + always-on shared expert, this is
**FAIL(active_mismatch)** (scorecard's conditional "~0.39" recall was close; computed
0.38). Confidence MED.

### 3.3 Memory arithmetic at 4-bit (MED)

```
Crude floor: 14,315,784,192 × 0.5 B = 7.158 GB = 6.666 GiB   (vs 6.8 GiB allowed — 0.13 GiB "room")
Frozen-recipe estimate: retained ≈ 625.6M×2 = 1.251 GB = 1.165 GiB
                        quantized 13,690.2M × 0.5625 B = 7.701 GB = 7.172 GiB
                        → ≈ 8.34 GiB lower bound  > 6.8 GiB  → FAIL(weight_lower_bound)
KV at fit shape: 24×2×(16×128)×2 B = 196,608 B/token = 192 KiB/token → 8,192 tokens = 1.5 GiB.
```
Under the actual frozen recipe the MoE arm fails the weight lower bound outright; even
at a hypothetical uniform 4.0 bits it leaves ~0.13 GiB for 1.5 GiB of KV plus
activations — certain smoke failure. Dense arm: retained 622.3M×2 = 1.24 GB + quantized
3,328.0M×0.5625 = 1.87 GB → ≈2.90 GiB, fine.

### 3.4 Runtime artifacts and license

- MLX conversions exist: `mlx-community/Qwen1.5-MoE-A2.7B-4bit` and
  `…-Chat-4bit` (search hits: https://huggingface.co/mlx-community/Qwen1.5-MoE-A2.7B-4bit ,
  https://huggingface.co/mlx-community/Qwen1.5-MoE-A2.7B-Chat-4bit); mlx-lm has
  `qwen2_moe.py`; llama.cpp has `LLM_ARCH_QWEN2MOE`; vLLM lists `Qwen2MoeForCausalLM`
  natively (URLs above). Quantization configs of these community artifacts: UNVERIFIED
  (not fetched — pair already fails two screens).
- **License anomaly (HIGH):** the two arms are under *different* non-Apache licenses —
  dense = Tongyi Qianwen *RESEARCH* license, MoE = Tongyi Qianwen license. Research-only
  terms likely permit academic benchmarking, but redistribution/mirroring terms are
  **UNVERIFIED** (license texts not reviewed); G8 would need a full license-text
  snapshot and reading. Combined with d_active 0.38 and the weight bound, this pair is
  triply disfavored.

Matched-total note (§6 fallback, informative only): `d_total` for Qwen1.5-14B-vs-MoE was
not computed here; `Qwen/Qwen1.5-14B` exists but its API metadata was not fetched —
UNVERIFIED. The OLMo matched-total hypothesis (OLMo-7B ≈ 6.9B?) also not fetched —
UNVERIFIED. Neither is evaluable without Ed's Option-D authorization anyway.

---

## 4. §8 ladder subject — `Qwen/Qwen2.5-1.5B-Instruct`

- Source repo: `Qwen/Qwen2.5-1.5B-Instruct`, SHA at fetch time
  **`989aa7980e4cf806f80c7fef2b1adb7bc71aa306`** (lastModified 2024-09-25), license
  `apache-2.0`, not gated, safetensors **1,543,714,304** BF16.
  https://huggingface.co/api/models/Qwen/Qwen2.5-1.5B-Instruct
- Config (https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/raw/main/config.json):
  `Qwen2ForCausalLM`, 28 layers, hidden 1536, intermediate 8960, 12 heads / 2 KV heads,
  vocab 151936, **tie_word_embeddings: true**, bfloat16.
- Ladder feasibility: mlx-lm's converter natively supports BF16 pass-through and
  affine quantization with `--q-bits {8,4}` and `--q-group-size 64` for `qwen2`-type
  models, evidenced by the existing mlx-community trio derived from this exact model:
  - `mlx-community/Qwen2.5-1.5B-Instruct-bf16` — SHA `4ae77cb209f06199b8df1c94e21ff341332a3a89` (https://huggingface.co/api/models/mlx-community/Qwen2.5-1.5B-Instruct-bf16)
  - `mlx-community/Qwen2.5-1.5B-Instruct-8bit` — SHA `c7e1ff25efda4a2c8f7ee312380557fb42e145a2` (https://huggingface.co/api/models/mlx-community/Qwen2.5-1.5B-Instruct-8bit)
  - `mlx-community/Qwen2.5-1.5B-Instruct-4bit` — SHA `8b403126fc14f14cfc99bb4cfa72ecbc129ea677` (https://huggingface.co/api/models/mlx-community/Qwen2.5-1.5B-Instruct-4bit)
  These are **discovery evidence only** (per §8: not ladder lineage; group sizes of the
  8-bit artifact UNVERIFIED — not fetched). The ladder must re-derive BF16/Q8_G64/Q4_G64
  locally from ONE frozen revision.
- Recommended freeze candidate: pin `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` (current
  main head, stable since 2024-09) as the single source revision for all three levels.
- Size estimates (MED): tied emb stored once. BF16 ≈ 1,543.7M×2 = 3.09 GB = 2.88 GiB;
  Q8_G64 ≈ 0.233 GB retained (emb 116.7M... see note) — simpler: quantized classes
  ≈ 1,427.0M → Q8: 1.516 GB + retained 0.233 GB ≈ 1.75 GB = 1.63 GiB;
  Q4: 1,427.0M×0.5625 = 0.803 GB + 0.233 GB ≈ 1.04 GB = 0.97 GiB. All trivially inside
  any 8 GiB budget (retained = tied emb 151936×1536 = 233.4M×... stored once at 2 B =
  0.467 GB; corrected totals: Q8 ≈ 1.98 GB = 1.85 GiB, Q4 ≈ 1.27 GB = 1.18 GiB).

---

## 5. Anomalies vs the scorecard's recalled numbers

1. **Qwen3 pair is NOT "near the 0.30 gate."** Scorecard §6 recalls "about 4B vs 3B
   active, near the 0.30 gate." Config-derived values are 4.022B vs 3.353B →
   d_active = 0.181 — passes with ~40% margin. The recall understated MoE active params
   (3.35B incl. the always-on 1.54B non-expert trunk, not 3.0B).
2. **Scorecard's ~15 GB 4-bit prediction for the 30B MoE: CONFIRMED and slightly
   understated.** Crude 4-bit floor = 15.27 GB; the real mlx-community 4-bit artifact is
   17.17 GB (16.0 GiB); the frozen recipe (BF16 embeddings/head/router) would be ~18 GB.
   FAIL(weight_lower_bound) on any 8 GiB target stands a fortiori.
3. **Qwen1.5 pair d_active: 0.380 computed vs "~0.39" recalled.** Same conclusion
   (FAIL if measured), slightly different number — the recall was approximately right.
4. **Qwen1.5 licenses are neither Apache nor uniform:** dense arm is
   `tongyi-qianwen-research`, MoE arm is `tongyi-qianwen`. The scorecard did not recall
   this; it is an additional G8 burden unique to this pair.
5. **OLMoE recalled as "1B-active/7B-total" checks out with unusual precision:** exact
   totals 6,919,161,856; config-derived active 1.282B. Against `OLMo-1B-0724-hf`
   (1,279,787,008) the pair is active-matched to **0.16%** — far better than any other
   candidate. The scorecard's generic "about 1B vs 1B" undersold this.
6. **The dense OLMo arm has a real MLX runtime gap** (mlx-lm `olmo.py` serves the
   original AI2 format and demands `ai2-olmo`; no mlx-community dense OLMo-1B conversion
   found). None of the scorecard's recalled facts flagged this; it is the OLMo pair's
   principal G4 risk and needs a local smoke.
7. **No first-gen OLMo-1B instruct variant exists**, so the OLMo pair can only be
   base–base; and OLMo-2's 1B (which does have Instruct) is tokenizer-incompatible with
   OLMoE (100352 vs 50304 vocab) — closing off the obvious "upgrade" pairing.
8. Minor: `OLMo-1B-hf` (0224) is **tied**-embedding, 1.177B; `OLMo-1B-0724-hf` is
   **untied**, 1.280B. Any G3 ledger must not conflate the two dense generations.

## 6. Residual UNVERIFIED items (needing local or Ed action)

- Tokenizer/chat-template byte-identity for every pair (G2) — requires local subtree hashes.
- Measured routing dispatch, shared-expert execution, exhaustive tensor ledger (G3) — local probe.
- MLX load of HF-format dense OLMo; exact mlx-lm/llama.cpp/vLLM version pins (G4).
- Qwen1.5 license texts' redistribution/mirroring terms (G8) — texts not reviewed.
- Matched-total candidates (`Qwen1.5-14B`, OLMo-7B-class vs OLMoE) — not fetched.
- mlx-community 8-bit artifact group sizes (§8 discovery context only).
- All revisions cited are fetch-time `main` heads; they are candidates for pinning, not
  frozen receipts. Nothing here passes any gate by itself.
