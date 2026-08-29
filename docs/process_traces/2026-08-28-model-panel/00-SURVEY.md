# Model panel survey for the `_v5` generation (and the D-164 production pair)

Date: 2026-08-28. Author: Fable (survey agent). Status: DRAFT for Ed's pick.
Branch `docs/model-panel-survey`. Nothing here is a decision; D-016/D-073/
D-074 remain the admission rules and Ed picks.

How every fact in this file was obtained, so the reader can redo it:

- **Catalogue and revisions** — the Hugging Face model API
  (`https://huggingface.co/api/models/<repo>?blobs=true`), queried
  2026-08-28. "Revision" below is the `sha` field, the git commit the repo's
  `main` branch pointed at on that date. Pin that string, not `main`.
- **4-bit weight size** — the sum of every `*.safetensors` file's byte size
  from the same API response, in decimal GB (1e9 bytes). The local mirror's
  `du -sh` prints GiB, so 0.87 GB here is the "839M" of D-016.
- **Architecture fields** — the repo's `config.json` at that revision
  (`model_type`, `vocab_size`, `num_hidden_layers`, `sliding_window`,
  `layer_types`, MoE expert count, MTP head count, `quantization`).
- **Tokenizer identity** — the SHA-256 of the repo's `tokenizer.json` (from
  the API's LFS record, or hashed after download when the file is not LFS).
  The current Qwen2.5 pair shares `a8506e71…`; this is the value the
  `generate_configs.py` `SHARED_TOKENIZER_JSON_SHA256` regression checks,
  and I re-hashed the three local mirrors to confirm it (all three match).
- **Already mirrored?** — `ls /Users/edr/jw_models/mlx-community` on
  2026-08-28: `Qwen2.5-0.5B-Instruct-4bit`, `Qwen2.5-1.5B-Instruct-4bit`,
  `Qwen2.5-7B-Instruct-4bit`, `Qwen3-4B-4bit`, `Qwen3.5-122B-A10B-4bit`
  (plus `allenai/OLMo-1B-0724-hf` and `allenai/OLMoE-1B-7B-0924`, not MLX
  4-bit). Everything else must be fetched and pinned (D-016 criterion 4).

Two facts about the instrument that decide most of what follows:

1. **The harness forces the decode length.** `joulewise/adapters/
   mlx_runtime.py:294-303` calls `mlx_lm.stream_generate` with
   `max_tokens = output_tokens` (512 in every floor/contrast pack:
   `configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py:153`)
   and `suppress_eos=True`. The model cannot stop early. So a "thinking
   mode" toggle cannot change how many tokens are decoded; it can only
   change *which* tokens. There is also no `apply_chat_template` call
   anywhere in `joulewise/` (grep, 2026-08-28): prompts go in as raw text,
   so a chat template's thinking switch is never even reached. Thinking
   therefore matters for output identity (D-074 battery, repeat-to-repeat
   token equality), not for decode length.
2. **The 256-token prefill prompt is frozen as TEXT, not as tokens.**
   `generate_configs.py:603-611` loads `prompt_text` and checks its UTF-8
   SHA-256 (`P256_PROMPT_UTF8_SHA256`). The "256" is the count that text
   produces under the Qwen2.5 tokenizer. A different tokenizer will turn
   the same text into a different number of tokens, so the label
   `df_ph_prefill_p256` stops being true. Any non-`a8506e71` tokenizer
   needs a re-derived prompt text (trimmed or regenerated until that
   tokenizer yields exactly 256 tokens) and a new frozen hash; the `_v5`
   manifest must then pin both the text hash and the measured token
   count, per tokenizer.

## §0 THE PAIR (D-164: the production campaign's small/large pair)

Selection rule applied, in the order the rules bind: same family and same
generation; `tokenizer.json` byte-identical across the two sizes (so the
`SHARED_TOKENIZER_JSON_SHA256` regression pattern survives); dense (no
mixture-of-experts, so "parameters" means parameters actually multiplied
per token); no linear-attention or multi-token-prediction novelty in the
decode path; size class matching 1.5B / 7B; Apache-2.0 or equivalent open
licence; text-only `model_type` that `mlx-lm` already serves.

### Recommended: Qwen3-1.7B-4bit / Qwen3-8B-4bit

| | Small | Large |
|---|---|---|
| HF repo | `mlx-community/Qwen3-1.7B-4bit` | `mlx-community/Qwen3-8B-4bit` |
| Revision (`sha`, 2026-08-28) | `3b1b1768f8f8cf8351c712464f906e86c2b8269e` | `545dc4251c05440727734bcd94334791f6ab0192` |
| Last modified | 2025-04-28 | 2025-04-28 |
| Mirrored locally? | **No** | **No** (only `Qwen3-4B-4bit` is) |
| 4-bit weights | 0.97 GB | 4.61 GB |
| Layers × hidden | 28 × 2048 | 36 × 4096 |
| `model_type` / vocab | `qwen3` / 151936 | `qwen3` / 151936 |
| `tokenizer.json` SHA-256 | `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4` | same |
| Quantization | 4-bit, group 64 (same as current pair) | same |
| Sliding window / MoE / MTP | none / none / none | none / none / none |
| Licence | Apache-2.0 | Apache-2.0 |

Why this pair: it is the direct successor of the current pair. Same
vendor, same tokenizer family (both `Qwen2TokenizerFast`), same
quantization recipe as the mirrored Qwen2.5 artifacts, and the byte
ratio of the two weight files (4.61 / 0.97 = 4.8×) matches the current
pair's (4.28 / 0.87 = 4.9×), so the "small vs large" contrast keeps the
same size gap. The two Qwen3 sizes also share one `vocab_size`
(151936), whereas Qwen2.5-7B carries 152064 (embedding padding) — one
fewer thing for the `_v5` manifest to special-case. The `qwen3`
architecture has already passed through this project's mirroring path
(`Qwen3-4B-4bit`, 2026-07-16, D-074 conditional repin), so the mlx-lm
loader is known to accept it on this machine.

Determinism-gate concerns (`joulewise/determinism_gate.py:88` compares
tokenizer `backend, identifier, revision, class, vocab_size`;
`analysis_manifest_v3.py:98,150` hard-codes `vocab_size: 151643`):

- The reported tokenizer `vocab_size` for Qwen3 will differ from the
  151643 the v3 manifest pins (Qwen3 adds think-delimiter tokens). The
  `_v5` manifest sibling must read the value at pin time from the mirrored
  tokenizer and freeze that, not inherit 151643.
- Thinking mode: the two Qwen3 April-2025 models are "hybrid thinking"
  models. Under this harness (raw prompt, no chat template,
  `suppress_eos=True`, 512 forced tokens) the toggle is never consulted,
  so decode length is invariant by construction. Pin it anyway: record
  `chat_template_applied: false` and `enable_thinking: not_applicable` in
  the model stanza, and let the D-074 battery's repeat-equality check
  prove the emitted token IDs are the same across repetitions. If Ed
  wants a non-thinking build instead, only Qwen3-4B-Instruct-2507 exists
  in this family at these sizes (no 1.7B or 8B "-2507" repo in
  mlx-community on 2026-08-28), which is why the pair uses the April
  models.
- The p256 prefill prompt must be re-derived for the Qwen3 tokenizer
  (see fact 2 above). Expect a near-identical count — the vocabulary is
  the same 151k merges plus a few added tokens — but "near" is not 256;
  re-tokenize, trim, re-freeze, and pin the count.

Prior for the decode ratio. No JouleWise measurement of any Qwen3 model
exists. The closest thing to an a9/a10-style prior is the retained
Qwen2.5 diagnostic: 7B absolute-cell member mean 192.386 J for 512 tokens
= 0.376 J/token, and 1.5B ≈ 0.098 J/token (`CLAIMS_STATUS.md:116`;
`docs/process_traces/2026-08-28-ladder-consult/01-sol-seat.md:24`), a
3.8× decode-energy ratio for a 4.9× weight-byte ratio. Because Qwen3
1.7B/8B has the same 4.8× byte ratio and the same dense decoder shape,
the working expectation is a decode ratio in the same 3.5–4× band, i.e.
a per-block contrast of roughly 140 J at 512 tokens — far above the ~5 J
effective bar (D-078 cl.11). This is an expectation, not a measurement;
the `_v5` floors mint it. Published tok/s for Qwen3-8B 4-bit on Apple
silicon exist only for other chips (an M4 Max figure of ~62 tok/s,
[markaicode](https://markaicode.com/benchmarks/hugging-face-qwen-3-m4-max-throughput-benchmark/));
they do not transfer to energy and are not used here.

### Alternate 1: Ministral-3-3B / Ministral-3-8B Instruct 2512

| | Small | Large |
|---|---|---|
| HF repo | `mlx-community/Ministral-3-3B-Instruct-2512-4bit` | `mlx-community/Ministral-3-8B-Instruct-2512-4bit` |
| Revision | `a962dcb09eee4169c890e544c9eb938f1113fdee` | `182f003f01daa75f9de0f2c4d379722fd0bc1c61` |
| Last modified | 2025-12-03 | 2025-12-06 |
| Mirrored? | No | No |
| 4-bit weights | 2.75 GB | 5.60 GB |
| Layers × hidden | 26 × 3072 | 34 × 4096 |
| `model_type` / vocab | `mistral3` / 131072 | `mistral3` / 131072 |
| `tokenizer.json` SHA-256 | `286acad9b0e27fce778ac429763536accf618ccb6ed72963b6f94685e531c5c7` | same |
| Licence | Apache-2.0 | Apache-2.0 |

The newest same-family, tokenizer-identical, dense, plainly non-thinking
Instruct pair in the catalogue. Two costs: the small member is 3B, so the
weight-byte gap is only 2.0× (the contrast shrinks to roughly half the
Qwen3 pair's), and `mistral3` is the multimodal Mistral-3 wrapper class —
the 4-bit sizes are larger than the parameter counts suggest, consistent
with a bundled vision tower, and text-only loading through mlx-lm must be
demonstrated in the D-074 battery before admission.

### Alternate 2: Llama-3.2-3B-Instruct / Llama-3.1-8B-Instruct

| | Small | Large |
|---|---|---|
| HF repo | `mlx-community/Llama-3.2-3B-Instruct-4bit` | `mlx-community/Meta-Llama-3.1-8B-Instruct-4bit` |
| Revision | `7f0dc925e0d0afb0322d96f9255cfddf2ba5636e` | `241a666dad6cb93c8ff213d39a7f34a36bf26db4` |
| Last modified | 2025-03-05 | 2024-11-26 |
| Mirrored? | No | No |
| 4-bit weights | 1.81 GB | 4.52 GB |
| Layers × hidden | 28 × 3072 | 32 × 4096 |
| `model_type` / vocab | `llama` / 128256 | `llama` / 128256 |
| `tokenizer.json` SHA-256 | `6b9e4e7fb171f92fd137b777cc2714bf87d11576700a1dcd7a399e7bbe39537b` (17.2 MB) | `bbc1904d35169c542dffbe1f7589a5994ec7426d9e5b609d07bab876f32e97ab` (9.1 MB) |
| Licence | Llama 3.2 community | Llama 3.1 community |

Dense, non-thinking, the most-cited family in the energy literature. But
the two are different Llama generations, and their `tokenizer.json`
files are NOT byte-identical (same 128256 vocabulary; the files differ in
serialisation and embedded chat template), so the single-shared-hash
regression cannot be reused: the manifest must pin one tokenizer hash
per model and additionally prove vocabulary equality by comparing the
`vocab` maps, not the file bytes. The Llama community licence permits
academic benchmarking (D-016 criterion 4) but is not Apache.

### Considered and set aside for the pair (kept for the panel below)

- **Qwen3.5-2B / 9B** (`mlx-community/Qwen3.5-{2B,9B}-4bit`, revisions
  `674aaa72…` / `8b2b98c0…`, 2026-03-02): the newest Qwen, but
  `config.json` declares `layer_types` mixing `full_attention` and
  `linear_attention` and an MTP head (`mtp_num_hidden_layers: 1`), vocab
  248320, `model_type qwen3_5`. That is exactly the north-star mechanism
  work (KDA/MTP, fenced by D-041) — not a production pair for a metrology
  paper whose instrument was validated on a plain dense decoder.
- **Gemma-3 1B / 4B**: 1B is `gemma3_text`, 4B is multimodal `gemma3`,
  sliding windows differ (512 vs 1024), Gemma licence; D-074 already
  rejected Gemma-3-4B on the licence + multimodal seam.
- **Qwen2.5-3B / 14B**: tokenizer-identical to today's pair
  (`a8506e71…`, verified via API), zero novelty risk, but "newer" was the
  brief; they remain the cheapest ladder rungs (§2).

## §1 Candidate panel (0.5–14B, 4-bit, mlx-community, verified 2026-08-28)

How the last two columns were estimated, so they can be redone or
replaced by measurement:

- **Decode rate (tok/s).** At 4-bit on Apple silicon, generating one token
  means reading every weight byte once from memory, so tokens per second
  is roughly (memory bandwidth) ÷ (weight bytes). The one JouleWise
  measurement is Qwen2.5-1.5B-Instruct-4bit at 257 tok/s
  (`runs/example-mac-mlx-local__r1/summary_metrics.json`,
  `throughput_tokens_s`; 265.8 in D-016) with 0.87 GB of weights. Every
  other rate here is 257 × 0.87 ÷ (that model's GB): a first-order
  estimate for a dense decoder, off by up to ~1.5× for models whose
  attention/KV work is unusually large (long sliding windows, big
  vocabularies) — treat as a planning number only.
- **Decode-only floor time (hours).** A floor pack has 50 decode members
  (10 absolute + ten A/B/B/A blocks of 4: `d117_floor_qwen25_7b_v3/
  README.md:7`), each 512 tokens. The 7B pack's decode-only time is 3.1 h
  (D-163 ruling, converged), i.e. 223 s per member, of which 512 tokens
  at ~52 tok/s is only ~10 s. The remaining ~213 s per member is settle,
  idle and window overhead that does not depend on the model. So floor
  hours = 50 × (213 s + 512 ÷ tok/s) ÷ 3600. **The conclusion is that a
  floor night costs the same for every model in this range: 2.97 h for
  0.6B up to 3.22 h for 14B.** Model choice moves the night by minutes,
  not hours; the night count is set by how many floors and contrasts the
  design needs, not by which models it uses.

| Model (repo under `mlx-community/`) | Params | 4-bit GB | Revision (`sha`, 12 chars) | Modified | `model_type` / vocab | `tokenizer.json` sha (8) | Architecture notes for the instrument | Determinism-gate risk | est. tok/s | est. floor h |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-0.6B-4bit | 0.6B | 0.34 | `73e3e38d9813` | 2025-04-28 | qwen3 / 151936 | `aeb13307` | dense; tied embeddings; hybrid-thinking (moot: forced 512, no template) | low — same class as pair | 658 | 2.97 |
| Qwen3-1.7B-4bit | 1.7B | 0.97 | `3b1b1768f8f8` | 2025-04-28 | qwen3 / 151936 | `aeb13307` | dense; tied embeddings | low (§0) | 231 | 2.99 |
| Qwen3-4B-Instruct-2507-4bit | 4B | 2.26 | `50d427756c6b` | 2026-01-02 | qwen3 / 151936 | `aeb13307` | dense; the only non-thinking Qwen3 build at these sizes; `Qwen3-4B-4bit` (`4dcb3d101c2a`) is the mirrored April build | low; note it is a different fine-tune generation from 1.7B/8B | 99 | 3.03 |
| Qwen3-8B-4bit | 8B | 4.61 | `545dc4251c05` | 2025-04-28 | qwen3 / 151936 | `aeb13307` | dense; untied embeddings | low (§0) | 49 | 3.10 |
| Qwen3-14B-4bit | 14B | 8.31 | `a4d9b2df59d2` | 2025-04-29 | qwen3 / 151936 | `aeb13307` | dense; 40 layers | low; largest same-family rung | 27 | 3.22 |
| Qwen3.5-4B-4bit | 4B | 3.03 | `0e7ffd5c629e` | 2026-03-02 | qwen3_5 / 248320 | `87a7830d` | **hybrid**: `layer_types` full + linear attention; **MTP head** (1); affine quant; thinking default | HIGH — new attention kernel path and an MTP head the harness has never pinned; vocab 248k | 74 | 3.05 |
| Qwen3.5-9B-4bit | 9B | 5.95 | `8b2b98c00a6b` | 2026-03-02 | qwen3_5 / 248320 | `87a7830d` | as above | HIGH (same) | 38 | 3.15 |
| Llama-3.2-3B-Instruct-4bit | 3B | 1.81 | `7f0dc925e0d0` | 2025-03-05 | llama / 128256 | `6b9e4e7f` | dense; tied | low; tokenizer bytes differ from 3.1-8B | 124 | 3.02 |
| Meta-Llama-3.1-8B-Instruct-4bit | 8B | 4.52 | `241a666dad6c` | 2024-11-26 | llama / 128256 | `bbc1904d` | dense; the literature's reference 8B | low; Llama community licence | 49 | 3.10 |
| gemma-3-4b-it-qat-4bit | 4B | 3.00 | `3d9ef2891114` | 2025-04-21 | gemma3 / 262208 | `4667f208` | multimodal wrapper; **sliding window 1024** on local layers; 262k vocab (large output head) | MEDIUM — multimodal seam (D-074 rejection), Gemma licence | 75 | 3.05 |
| gemma-4-12B-it-4bit | 12B | 6.74 | `73bcf09092aa` | 2026-06-08 | gemma4_unified / 262144 | `cc8d3a0c` | `layer_types` full + sliding (1024); unified multimodal | MEDIUM-HIGH — newest loader class; licence tag absent on the repo | 33 | 3.17 |
| Ministral-3-8B-Instruct-2512-4bit | 8B | 5.60 | `182f003f01da` | 2025-12-06 | mistral3 / 131072 | `286acad9` | dense text decoder inside the Mistral-3 multimodal class; non-thinking | MEDIUM — text-only load must be shown | 40 | 3.14 |
| Mistral-7B-Instruct-v0.3-4bit | 7B | 4.08 | `a4b8f870474b` | 2024-06-18 | mistral / 32768 | `e553af6f` | dense; **32k vocab** (smallest head; tokens are ~1.3× more numerous per word than Qwen's) | low; old | 55 | 3.09 |
| phi-4-4bit | 14B | 8.25 | `fc0f8f23d369` | 2025-01-12 | phi3 / 100352 | `c612e57b` | dense; MIT | low | 27 | 3.22 |
| Phi-4-mini-instruct-4bit | 3.8B | 2.16 | `ac1c269cb422` | 2025-03-05 | phi3 / 200064 | `382cc235` | dense; 200k vocab; tied | low | 104 | 3.03 |
| SmolLM3-3B-4bit | 3B | 1.73 | `d3a7e0594d66` | 2025-07-08 | smollm3 / 128256 | `7b6a500b` | dense; NoPE layers; dual-mode think/no-think (moot here) | low-medium — `smollm3` loader | 129 | 3.01 |
| DeepSeek-R1-0528-Qwen3-8B-4bit | 8B | 4.61 | `b9b5af4fa18f` | 2025-05-30 | qwen3 / 151936 | `93d5fd6d` | same architecture as Qwen3-8B, reasoning fine-tune; **tokenizer.json differs from Qwen3's** | low arch / MEDIUM tokenizer | 49 | 3.10 |
| Olmo-3-7B-Instruct-4bit | 7B | 4.11 | `d732c91ae02e` | 2025-11-20 | olmo3 / 100278 | `7738a25c` | `layer_types` full + sliding (4096); fully open data/training | MEDIUM — sliding path | 54 | 3.09 |
| NVIDIA-Nemotron-3-Nano-4B-4bit | 4B | 2.24 | `c4d79ba1901d` | 2026-03-20 | nemotron_h / 131072 | `623c3456` | **Mamba-2 / attention hybrid** (`nemotron_h`) | HIGH — state-space layers, no attention-only baseline | 100 | 3.03 |
| granite-4.1-8b-4bit | 8B | 5.24 | `08fb1e272f7b` | 2026-05-03 | granite / 100352 | `24665f28` | dense; **group_size 32** (different quant recipe from every other row) | MEDIUM — quant recipe mismatch | 43 | 3.12 |
| Qwen2.5-3B-Instruct-4bit | 3B | 1.74 | `4f83f8f146fd` | 2024-09-18 | qwen2 / 151936 | **`a8506e71`** | today's family; rung between 1.5B and 7B | none new; licence tag `other` (Qwen research licence for 3B) | 128 | 3.01 |
| Qwen2.5-14B-Instruct-4bit | 14B | 8.31 | `dad510143ae5` | 2024-09-18 | qwen2 / 152064 | **`a8506e71`** | today's family; top rung | none new | 27 | 3.22 |

Not tabled: Llama-4 (Scout is 109B-A17B MoE, 4-bit ~60 GB — fits the
128 GB machine but is far outside the 0.5–14B brief and is MoE);
Llama-3.3 exists only at 70B; Qwen3-30B-A3B / Qwen3.5-35B-A3B /
gemma-4-26B-A4B are MoE (north-star C5-1.9 material, D-041-fenced);
"OptiQ"/"DWQ" variants are alternative quantizers, not the group-64
affine recipe the current floors were minted under.

Cross-family tokenizer rule (what the manifest must pin when the pair's
byte-identical-tokenizer assumption is dropped): one `tokenizer.json`
SHA-256 **per model**, the reported `vocab_size` per model, the tokenizer
class per model, the p256 prompt text hash **and its measured token count
per tokenizer**, and an explicit statement in the claim sentence that
"per token" means per decoded token of that model's tokenizer — the
forced 512-token decode makes the decode phase comparable across
tokenizers in tokens, but 512 Mistral tokens and 512 Qwen tokens are not
the same amount of text.

## §2 Three panel shapes with night arithmetic

Night arithmetic used throughout (D-163 converged figures): a floor is
≈ 3.1 h decode-only, a contrast ≈ 2.8 h decode-only, and each night pays
≈ 75 min of fixed overhead that never amortises. An overnight window of
≈ 8 h therefore holds two floors (75 + 2 × 186 = 447 min ≈ 7.5 h) or two
contrasts (75 + 2 × 168 = 411 min ≈ 6.9 h) or one of each (≈ 7.2 h).
"Reused" means the production `_v5` pair (§0) already minted it.

### A — same-family newer ladder: Qwen3 0.6B / 1.7B / 4B / 8B

Floors: 4 (1.7B, 8B reused from production → 2 new: 0.6B, 4B = 1 night).
Contrasts, adjacent decode-only: 0.6–1.7, 1.7–4, 4–8 (1.7–8 is the
production contrast and stays in) = 3 new = 2 nights (2 + 1). **Total 3
nights**, 2 if 1.7–4 is dropped. Figure: 512-token decode energy against
parameter count, one family, one tokenizer, four points — C5-1.1 in its
permitted pairwise form (registry row 64), every adjacent step resolved
(expected steps: Qwen2.5 measured 0.098 → 0.376 J/token over 1.5→7B; the
Qwen3 rungs sit at similar byte ratios). Caveat: the only non-thinking
4B is the `-2507` fine-tune generation; use the April `Qwen3-4B-4bit`
(already mirrored) for generation-consistency, since thinking is moot
here.

### B — cross-family same-size (~8B): Qwen3-8B / Llama-3.1-8B / Ministral-3-8B / Olmo-3-7B

Floors: 4 (Qwen3-8B reused → 3 new = 2 nights, one slot spare).
Contrasts: each family against Qwen3-8B as the fixed reference = 3 = 2
nights. **Total 4 nights** (3 if the spare floor slot takes a contrast).
Figure: "joules per 512 decoded tokens at ~8B, by family" — the figure a
practitioner wants. Costs: four tokenizers, so four p256 prompt
re-derivations and per-model tokenizer pins (§1 rule); Olmo-3's sliding
attention and Ministral's multimodal class each need a D-074 battery
pass before the night. Swap Mistral-7B-v0.3 (`a4b8f870474b`, plain
dense, Apache) for Ministral-3 if the `mistral3` text-only load fails.

### C — hybrid: production pair + one rung down + one cross-family peer

Models: Qwen3-1.7B / 8B (production), Qwen3-0.6B, Llama-3.1-8B.
Floors: 2 new (0.6B, Llama-8B) = 1 night. Contrasts: 0.6–1.7 (ladder
bottom) and Llama-8B vs Qwen3-8B (cross-family) = 1 night. **Total 2
nights.** Yields a 3-point same-family ladder (0.6/1.7/8) AND one
cross-family 8B contrast against the most-cited open model, with a
single extra tokenizer to pin.

## §3 Recommendation

Shape **C** for the week after `_v4`, with **A** as the follow-on if a
third and fourth night open up (its two extra floors/contrasts slot in
without re-planning). B is the most attractive figure but the most
instrument work (three new loader classes, four tokenizers) for a week
whose priority is the paper; run B only after A, or if Ed rules the
practitioner figure outranks the ladder.
