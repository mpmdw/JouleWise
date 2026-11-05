# Qwen3.8-Flash-Next weights logistics for the ALIGN measurement Mac

Status: plan only (2026-11-05). Nothing has been downloaded, converted, or
installed. Sizes come from the Hugging Face tree API and from the safetensors
headers of all 131 bf16 shards, fetched with HTTP range requests (headers
only, about 1 MB in total). Quantized sizes are computed from those exact
tensor shapes. They are not estimates from parameter counts.

Target host: the ALIGN measurement Mac (M3 Max, 128 GiB = 137.4 GB unified
memory, GPU working-set limit about 115.4 GB, about 82 GB free disk). The
runtime is the pinned mlx 0.31.2 with mlx-lm 0.31.3 and the JouleWise port,
loaded through the `model_file` hook in `config.json`. Units are decimal GB
unless marked GiB. The free-disk floor in d3_apple_replication.md (40 GiB)
equals 42.9 GB.

## Headline

| Quantity | Value |
|---|---|
| Upstream bf16 checkpoint | 131 shards, 360.00 GB, 180.0 B parameters |
| Of which the n-gram embedding | 102.40 GB (51.2 B parameters, 128 parts of [2500012, 160]) |
| Of which the routed experts | 241.59 GB (48 layers of [512, 1280, 2560] gate_up + [512, 2560, 640] down) |
| Official Qwen quantized variant | FP8 only: Qwen/Qwen3.8-Flash-Next-FP8, 185.52 GB. Qwen publishes no INT4, AWQ or GPTQ variant. |
| MLX core output (experts 4-bit, everything else 8-bit, no MTP or vision) | 73.21 GB (68.18 GiB) |
| N-gram table kept as Qwen's FP8 bytes, separate mmap file | 51.20 GB (47.68 GiB) |
| Recommended output in total | 124.41 GB (115.87 GiB) |
| Recommended download (route A) | 313.06 GB (bf16 260.80 GB + FP8 n-gram shards 52.26 GB) |
| Streaming staging peak | at most 6.87 GB (the two largest consecutive bf16 shards) |
| GPU-wired at runtime | about 73.2 GB of 115.4 GB (the n-gram table is CPU-side mmap) |

The internal disk cannot hold the output under the 40 GiB floor, even with
the n-gram table removed. The core alone (73.2 GB) would leave about 9 GB free.
Either free about 85 GB more on the internal disk (installing 124.4 GB above
the floor needs 167.3 GB free), or stage the conversion and the output on an
external SSD. This is the main logistics constraint.

## (a) Upstream files

`Qwen/Qwen3.8-Flash-Next` at revision `de4b8e4d43b917e7706784d8bb445c9af86a3540`
(last modified 2026-08-27, not gated, license `qwen-community-1.0`):

- `model-00001..00131-of-00131.safetensors`: 360,000,192,888 bytes, all BF16
  except 35 I64 scalars. Shard sizes run from 1.04 to 3.51 GB. Index
  `total_size` is 359,999,963,128.
- Small files: config.json (4,745 B), generation_config.json, chat_template.jinja,
  tokenizer.json (12.8 MB, stored in LFS), tokenizer_config.json, vocab.json,
  merges.txt, preprocessor_config.json, video_preprocessor_config.json,
  model.safetensors.index.json, README.md, LICENSE.
- The twin worktree's `.engine/hf-flashnext/*` files have the same bytes as
  this revision (sha256 checked for config, README, tokenizer_config,
  chat_template, generation_config).

Breakdown by component, from the headers (bf16):

| Component | GB | Note |
|---|---|---|
| Routed experts (48 layers) | 241.59 | fused `gate_up_proj` [E, 2I, H]. Reference: `linear(x, gate_up[e]).chunk(2, -1)` gives rows 0..639 = gate and 640..1279 = up |
| N-gram embedding | 102.40 | 128 parts, `layers.1.ple.ple_embedding.ngram_embedding.shard_K.weight` |
| MTP head (1 layer, its own 512 experts) | 5.21 | not needed for plain decoding |
| Gated DeltaNet (36 layers) | 4.17 | |
| Hyper-connection mixers | 1.28 | |
| embed_tokens and lm_head (untied) | 2.54 | [248320, 2560] each |
| Full attention (12 layers) | 1.20 | |
| Vision tower | 0.90 | in shard 1, alongside 0.14 GB of text weights |
| Shared experts, routers, indexer, PLE projections | 0.70 | |

Official variants. A search of the Hub by author shows only
`Qwen/Qwen3.8-Flash-Next-FP8` (revision `236dfdf285828023ca3bcd3f37366c58a3469b13`,
185.52 GB, 131 shards). It uses block-wise E4M3 128x128 with `weight_scale_inv`
for every expert, split per expert into gate_proj, up_proj and down_proj. The
n-gram table is stored as E4M3 with a single per-tensor BF16 `weight_scale` [1].
Attention, DeltaNet, routers, shared experts and embeddings stay BF16. Qwen
publishes no INT4, AWQ or GPTQ variant. The NVFP4 and FP4-Local builds
(nvidia/, RadixArk/) come from vendors or third parties, not Qwen. All MLX,
GGUF and AWQ builds are community work, and the INDEPENDENCE rule excludes
the community MLX build from this work.

Can the FP8 variant convert directly? Mechanically, yes: mlx 0.31.2 reads
F8_E4M3 safetensors as uint8 and `mx.from_fp8` decodes them (checked locally
on a synthetic file). For the experts, however, FP8 to 4-bit is a double
quantization: block FP8 rounding first, then affine 4-bit. The n-gram table is
a different case. There the FP8 bytes are Qwen's own 8-bit precision and can
be used verbatim (route A below).

## (b) N-gram embedding storage

- The table holds 320,001,536 rows x 160 columns: 2 orders (bigram, trigram)
  x 8 heads x a 20 M base vocabulary, padded and split into
  `split_ngram_parts = 128` parts of 2,500,012 rows. 16 heads x 160 =
  `ple_embed_dim` 2560.
- In bf16 the 128 parts total 102.40 GB across 33 shards (5 through 37). Shards
  6 to 36 hold only n-gram parts (31 shards). Shards 5 and 37 also carry
  1.76 GB and 0.14 GB of other weights.
- `layer_multipliers` [3], `ngram_heads_offsets` [16] and `ngram_heads_vocab_sizes` [16]
  are I64 and sit in shards 5 and 37.
- `layers.1` in the tensor names is the same layer as `ple_layer_ids = [2]` in
  the config. The reference uses `layer_idx + 1`, so the config index is 1-based.
- Part order is numeric. The reference loader concatenates `shard_*` in
  `dot_natural_key` order, so shard_2 precedes shard_11. A lexical sort would
  scramble rows. The converter must record the order explicitly.
- FP8 variant: the same 128 parts as E4M3 (51.20 GB), plus one BF16 scalar
  `ngram_embedding.weight_scale`, in FP8 shards 5 to 37 (52.26 GB in total).
- Access per token: 16 rows. A decode step reads 16 x 160 B = 2.5 KB from the
  FP8 table, but each row lands in a different 16 KiB page.

## (c) Streaming download and convert

All routes stream shard by shard. Each safetensors tensor lies wholly inside
one file, and the largest single tensor is 3.36 GB (one layer's gate_up).
Before conversion, each shard is fetched by `hf_hub_download(repo_id,
filename, revision=<40-hex>, local_dir=<staging>)` (huggingface_hub 2.4.0 is
already in the pinned venv), and its sha256 is checked against the pins. Its
tensors are quantized, or copied byte for byte, into the output. The shard is
deleted once the hash of the consumed bytes matches. The next shard downloads
while the current one converts. Set `HF_HOME`, `HF_XET_CACHE` and `TMPDIR` on
the staging volume, or disable the xet chunk cache, so that nothing grows
silently under `~/.cache`.

Source routes:

| Route | Download | Notes |
|---|---|---|
| A (recommended): bf16 for everything except the n-gram table; n-gram table verbatim from the official FP8 repo | 313.06 GB (100 bf16 shards + 33 FP8 shards) | Experts are quantized once from bf16. The n-gram table keeps Qwen's own 8-bit bytes. The two n-gram parts inside bf16 shards 5 and 37 give a free check that the two repos agree. |
| B: bf16 only, with the n-gram table quantized by JouleWise | 360.00 GB | One provenance. The n-gram precision is our choice (sizes in (d)). |
| C: FP8 only | 185.52 GB | Smallest download, but double-quantizes the experts. Not recommended. |

Peak disk by placement (route A; the final output is 124.41 GB):

| Option | Peak on measurement-Mac internal disk | Other peak | Verdict |
|---|---|---|---|
| C1. Stream on the measurement Mac to its internal disk | 131.3 GB (output + 6.9 GB staging), so 174.2 GB free is needed with the floor | none | Not feasible at 82 GB free |
| C2. Stream on the measurement Mac to an external SSD | about 0 | SSD 131.3 GB (a 256 GB disk is the minimum; 500 GB or more recommended) | Feasible now |
| C3. Stream on another Apple Silicon Mac, transfer only the output | 124.4 GB if installed internally, 0 if run from the SSD | 131.3 GB on that host | Feasible. This laptop is excluded (24 GB RAM, 54 GiB free, busy) |
| C4. Download everything, then convert (not streaming) | 437.5 GB (A) or 484.4 GB (B) | none | Do not use |

Conversion memory: about 8 GB RSS per shard if experts are quantized in
per-expert slices. Fine on the measurement Mac. Conversion time is dominated
by the download: route A takes about 52 min at 100 MB/s, about 3.5 h at
25 MB/s. Run it outside measurement windows. The converter is JouleWise code,
so run it from a reviewed commit and record that commit in the manifest.

Determinism finding. In mlx 0.31.2, `mx.quantize` on the CPU stream and on the
GPU stream give different bits for the same bf16 input. In a test with a
[640, 2560] tensor at 4 bits, group 64, 21 of 25,600 groups got different
scales (up to 11% relative) and 2,604 packed words differed. The quantization
device is therefore part of the artifact identity. Pin it to `mx.cpu` in the
converter, record it in the manifest, and treat C3 output as valid only after
the cross-host check in (f).

## (d) Expected MLX output size

Recipe. Routed experts use affine 4-bit, group 64. These layers use affine
8-bit, group 64: attention q/k/v/o, DeltaNet in_proj_qkv/z/a/b and out_proj,
indexer `index_qk_proj`, routers `mlp.gate`, shared experts and
`shared_expert_gate`, hyper-connection input_mix down/up, PLE key/value
projections, embed_tokens and lm_head. Norms, `A_log`, `dt_bias`, conv1d,
`block_inject` and the I64 tables stay at source precision. MLX does not
quantize 1-D norm vectors, so "norms at 8 bits" becomes "norms kept bf16".
That totals 0.013 GB.

| Part | GB | GiB |
|---|---|---|
| Experts, 4-bit g64 | 67.95 | 63.28 |
| Dense, 8-bit g64 | 5.25 | 4.89 |
| Kept at source precision | 0.01 | 0.01 |
| Core in total (`model-*.safetensors`) | 73.21 | 68.18 |
| Optional: MTP layer (same recipe) | +1.52 | |
| Optional: vision tower in bf16 | +0.90 | |
| Alternative: experts in mxfp4 instead of affine 4-bit | 64.17 for the experts | |

N-gram table, stored separately (`ngram_embedding.safetensors`):

| Precision | GB | Core + table | Notes |
|---|---|---|---|
| FP8 E4M3, Qwen's bytes verbatim (route A) | 51.20 | 124.41 | Recommended. Rows are dequantized with `mx.from_fp8` x scale after the gather. |
| mxfp8, group 32 | 52.80 | 126.01 | |
| affine 8-bit, group 32 | 57.60 | 130.81 | Group 64 is impossible: 160 is not divisible by 64 (checked) |
| affine 4-bit, group 32 | 32.00 | 105.21 | Small enough to be GPU-resident |
| mxfp4, group 32 | 27.20 | 100.41 | |
| bf16 | 102.40 | 175.61 | Does not fit |

Memory at runtime. The core is wired (about 73.2 GB of the 115.4 GB GPU
limit). KV for the 12 full-attention layers is about 24.6 KB per token, and
the DeltaNet state is about 0.11 GB, so GPU headroom stays about 40 GB. The
FP8 table is a numpy memmap with a CPU gather, so only touched pages enter the
page cache. Fully faulting in all 51.2 GB would push unified memory to about
124.4 + 3 GB (process) of 137.4 GB, leaving roughly 10 GB for macOS. Do not
force-prefault the whole table by default. Instead, record major page faults
(`ru_majflt` delta) and `vm_stat` pageins for each bracket, and disclose
nonzero values as a hazard. If in-bracket page-ins turn out to be common,
fall back to the 4-bit table resident on the GPU (105.2 GB wired in total).
That is a precision change and must be registered as one.

Loader facts from the installed mlx-lm 0.31.3 (`utils.load_model`):

- It loads only `model*.safetensors` files. The table therefore must not
  match that glob, or it would be pulled into the weights dict and the GPU.
- It imports `config["model_file"]` from the model directory, so the module
  can find its sibling table through `Path(__file__).parent`.
- It applies `config["quantization"]` with per-path overrides, so the 4/8-bit
  mix needs no loader change.
- `strict=True` means the table must stay outside the module parameter tree.

## (e) License: qwen-community-1.0

The LICENSE text (identical in the bf16 and FP8 repos, sha256 `a0dc4225...6c08`)
grants use, copying, modification, publication, distribution and derivative
works free of charge, under two conditions:

1. Include the copyright and permission notice in all copies or substantial
   portions. This applies to our MLX conversion: ship `LICENSE` inside the
   model directory and with any shared copy. The rule that the model name must
   be shown in the UI applies only to commercial products above 100 M MAU or
   US$20 M monthly revenue. Not applicable.
2. Commercial Model-as-a-Service or AI Work Assistant use needs a separate
   license from Qwen. Internal use is exempt. Not applicable to academic
   measurement.

Research measurement and publication of energy results, token traces and
model outputs are permitted. The license places no restriction on outputs,
and no separate acceptable-use policy is attached. If we ever release the
converted weights, include the LICENSE and label them a JouleWise derivative,
not an official Qwen artifact. Default: do not release them. Secondary sources
agree that the license is "Qwen Community License 1.0", not Apache-2.0
([HF discussion](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/discussions/18),
[aiagent-navi](https://aiagent-navi.com/news/qwen-3-8-flash-next-release/)).
This is not legal advice. The LICENSE file in the repo is authoritative.

## (f) sha256 pinning and verification

The existing practice stays in place: `joulewise.provenance.model_artifact_identity`
hashes every `MODEL_WEIGHT_SUFFIXES` file under the model directory, folds the
hashes under `joulewise.model_artifact_identity.v1`, and does not traverse
directory symlinks. The kit's `derive_identity_pins.py` writes that hash into
`identity_pins.json` as `model_artifact_sha256`, next to
`runtime_versions(...)` (package metadata only). The plan adds the following.

1. Freeze the upstream pins before any download.
   `docs/align/flashnext_source_pins.json` (written alongside this plan, sha256
   `cbe253d6100f080a0812504518f578c8ae7aad16db82de053a5d0add47b79d25`) lists,
   for both repos at their 40-hex revisions, every file's size, git blob oid
   and sha256. For LFS files the sha256 is the oid; small files were fetched
   at the pinned revision and hashed. Status:
   `PLANNING_PIN_NOT_YET_VERIFIED_BY_DOWNLOAD`.
2. Verify each download. Fetch only `resolve/<revision>/<path>` URLs. Check
   size and sha256 locally against the pin rather than relying on the hub
   client's own check. On mismatch, delete and retry once, then abort.
3. Hash what the converter reads. The converter hashes the bytes it actually
   reads, using the same fstat-before/after guard as `_stable_file_sha256`,
   and refuses a shard whose consumed hash differs from its pin.
4. Write a conversion manifest. `jw_conversion_manifest.json` in the output
   directory records:
   - both upstream repos and revisions, and the sha256 of the source-pins file
   - every input shard's sha256
   - the converter's git commit, plus the sha256 of the converter and of the
     `model_file` .py
   - `runtime_versions` of the converting interpreter, and the quantization
     device (`cpu`)
   - the per-path recipe, and the explicit numeric n-gram part order
   - each output file's sha256 and size
   - for the 128 n-gram tensors, the sha256 of each tensor's raw bytes, which
     must equal the same span in the pinned FP8 source shards (proof of a
     verbatim copy)
   - the bf16-vs-FP8 agreement check on the two n-gram parts in bf16 shards
     5 and 37: max relative error within E4M3 rounding of about 2^-4
5. Cover the n-gram table by the folded identity. Name it
   `ngram_embedding.safetensors`: the `.safetensors` suffix is in
   `MODEL_WEIGHT_SUFFIXES`, and the name does not match mlx-lm's
   `model*.safetensors` glob. Keep real files, not HF-cache symlinks. If the
   SSD is the home, the directory itself lives there; do not use a directory
   symlink.
6. Close the support-file gap. The folded identity omits `config.json`, which
   carries `model_file` and the quantization overrides. It also omits the
   port's `.py`, the tokenizer files and the chat template, and for a
   `model_file` port these define behaviour. Add a `support_files_sha256` map
   to the ALIGN identity unit, folded under a new domain such as
   `joulewise.model_support_files.v1`. Require the `.py` in the model
   directory to be byte-identical to the git-tracked port file at the kit
   commit. Do not widen `MODEL_WEIGHT_SUFFIXES`: that would change the folded
   digest of every already-pinned model, because each one has a config.json.
7. Set the revision explicitly. A converted directory has no
   `.cache/huggingface/download` metadata, so `recorded_download_revisions`
   returns []. Set `model_revision` to the bf16 revision, and carry the FP8
   revision and the manifest sha256 in the unit's derivation block.
8. Pin the runtime. The conversion host must report mlx 0.31.2,
   mlx-metal 0.31.2 and mlx-lm 0.31.3, the measurement-Mac pins. The local
   venv-mlx has numpy 2.5.4, while the ALIGN pins have 2.5.1. Keep numpy out
   of the numerics (byte memmap only), or pin it too. The measurement Mac's
   transformers is 5.12.1 and has no `qwen4_exp`. Tokenizer loading should go
   through `tokenizer_class: Qwen2Tokenizer`, but verify that before the kit
   build.
9. Check reproducibility across hosts (C3 only). Re-quantize a sample on the
   measurement Mac with the same device pin: shards 2, 40 and 131, plus one
   FP8 n-gram shard. Byte equality with the transferred output is required.
   On any mismatch, re-convert on the measurement Mac.
10. Re-hash at kit time. `derive_identity_pins.py --runtime-python ...` re-hashes
    the 124.4 GB directory, which takes minutes and is bounded by SSD read
    speed and sha256 throughput. Do this outside brackets. It also warms the
    page cache.

## Recommended route

1. Use route A for sources: the bf16 repo for everything except the n-gram
   table, and the official FP8 n-gram bytes verbatim.
2. Convert on the measurement Mac with the streaming converter, device pinned
   to CPU, and the staging, xet cache and output on an external SSD (C2). Peak
   internal disk is about 0, and the SSD peak is 131.3 GB.
3. Produce 73.21 GB of core plus the 51.20 GB `ngram_embedding.safetensors`,
   124.41 GB in total. Drop MTP and vision unless the protocol needs them
   (+1.52 GB and +0.90 GB).
4. Choose the home for runtime:
   - Preferred: the internal disk, after freeing about 85 GB so that 124.4 GB
     fits above the 40 GiB floor. Bracket energy then excludes external-drive
     power and USB I/O.
   - Fallback: run from the SSD and disclose it. A bus-powered SSD adds to
     system total (PSTR), though not to the processor rails, and n-gram page
     faults go to USB.
5. Pin and verify as in (f) before any kit uses the model.

Open decisions for the port lead:

- The n-gram precision (FP8 verbatim is recommended; 4-bit on the GPU is the
  fallback).
- Whether to keep the fused gate_up layout. Groups run along the 2560 input
  dimension, so splitting rows commutes with quantization.
- Where to free the 85 GB on the measurement Mac.
