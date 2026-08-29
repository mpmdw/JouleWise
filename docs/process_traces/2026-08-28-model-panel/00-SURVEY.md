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

