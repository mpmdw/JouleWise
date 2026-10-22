# BY-G: independent re-derivation of the BYTES manifest, and the C4 identity pins

Item BY-G of the forward workflow (BYTES item G review, and C4). Seat: Opus 5.5, a different model from item G's
author (Sonnet 5.5). Run on the Mac on 2026-10-21 between 18:00 and 18:45 PDT, with windows paused (RUN_STATE item 64).
No model was loaded or run and no power was captured; the work read safetensors headers, `config.json` files and
model files only.

## Verdict

1. **Manifest:** `configs/bytes/bytes_manifest.json` at `99c9099d8` (sha256 `33352242…afe1c`) matches the
   re-derivation for all ten models, with **zero mismatches** over 302 checks: W, R, KV, b, the six category totals,
   both cache snapshots (occupied and allocated), the count of each cache class, the recurrent-state bytes per
   layer, k and E, shared-expert bytes, tied embeddings, the config and tokenizer hashes, every per-tensor row
   (dtype, shape, stored bytes, category), and the four GB columns.
2. **C4 pins:** the kit's derivation (`derive_identity_pins.py` at `c10b6895f`, unchanged) run over the twelve
   sub-pack trees gives eleven units (ten models plus the reference). Each pin equals the kit's own
   `identity_pins.json` at `c10b6895f`, and it equals my independent hash. Every one of the 47 weight files
   (215,449,636,568 bytes) also hashes to the SHA-256 that Hugging Face recorded for it. The pins are committed as
   `configs/bytes/identity_pins.json` (sha256 `553859a0…c4392f`).
3. Flags (none touches a number, none is a refusal): the manifest stores W, KV and b as JSON floats; Qwen3-8B-8bit's
   revision is still null in the configs and roster; the pins cover weight files only. Details are in "Flags" below.
4. **Run 3 (2026-10-22, 03:17-03:45 PDT, a fresh Opus 5.5 seat after the workflow resumed):** a second reviewer
   script, written from scratch, again finds zero mismatches (310 checks). Its own hash of all 47 weight files gives
   the same eleven pins. Re-running the kit derivation reproduces `configs/bytes/identity_pins.json` byte for byte.
   See "Run 3" below.

## Inputs

| Input | Where |
|---|---|
| Manifest under review | `configs/bytes/bytes_manifest.json` at `99c9099d8` (lane/2026-10-20-bytes-manifest-kv) |
| Definitions | `docs/registrations/bytes_pack_v1.md` §4 (docs/2026-10-20-bytes-registration `91b20d7c2`) |
| Kit derivation and kit pins | `configs/campaigns/bytes_mac_check/registration/derive_identity_pins.py` (sha256 `6652cc07…44766`) and `identity_pins.json` (sha256 `7ac42b6b…28578`), both at `c10b6895f` |
| Sub-pack trees | `configs/campaigns/bytes-sN-pP/plan_tree.json`, N = 1..6, P = 1, 2; byte-identical at `99c9099d8` and `c10b6895f`, as are `bytes_v1/`, the two reference campaigns, `joulewise/provenance.py` and `joulewise/b5/plan.py` |
| Reviewer script | `/Users/edr/night-archive/forward-20261021/BY-G/rederive.py` (untracked, stdlib only, imports nothing from `joulewise/` or `scripts/`; sha256 `66d831bf…db32a`) |
| Pin driver | `/Users/edr/night-archive/forward-20261021/BY-G/byg_derive_pins.py` (untracked; sha256 `14e3f70e…5c55c8`; full text in the appendix) |
| Interpreters | `/opt/homebrew/bin/python3.13 -I` (and `-B` for the kit import). Runtime versions observed from `/Users/edr/code/JouleWise/.venv/bin/python`: Python 3.13.1, mlx 0.31.2, mlx-lm 0.31.3, mlx-metal 0.31.2 |

## Part 1: the bytes

### How each quantity was re-derived

All byte counts come from the safetensors headers. Each header gives every tensor's dtype, shape and byte span. For
every tensor I checked that span = (product of the shape) × (dtype width). For every file I checked that the spans
tile the data region with no gap or overlap, and that 8 + header length + data bytes = the file size. I also checked
that `model.safetensors.index.json` names the same tensors in the same files.

Categories are assigned by tensor name. My rules come from the registration's §4 prose; I did not read them out of
`scripts/bytes_manifest.py`:

- `not_loaded`: the name begins `vision_tower.` or `model.visual.`, or has an `mtp.` segment. mlx-lm 0.31.3 drops
  these in `qwen3_5.Model.sanitize`; only Qwen3.5-122B has any (333 vision tensors).
- `embed`: `model.embed_tokens.*`; `lm_head`: `lm_head.*`. A `language_model.` prefix is stripped first.
- `routed_experts`: `.mlp.switch_mlp.*`. Their leading dimension must equal E from `config.json`.
- `shared_experts`: `.mlp.shared_expert.*`. The one-row `shared_expert_gate` stays always-active.
- `always_active`: everything else.

Then:

- **R** = the sum of every category except `not_loaded`.
- **W** = always_active + shared_experts + the whole output layer + one embedding row + (k/E) × routed_experts.
  The output layer is `lm_head`, or the embedding itself when `tie_word_embeddings` is true (Qwen3-1.7B, Qwen3-4B).
  One embedding row is each embedding tensor's bytes divided by its row count, summed over weight, scales and biases.
  For Qwen3-1.7B the hidden size is 2,048, so one row is 1,024 B of packed 4-bit weight, 32 bf16 scales (64 B) and
  32 bf16 biases (64 B), 1,152 B in all. In integer arithmetic the routed share is (routed bytes / E) × k, and each
  routed total divides by E exactly.
- **Quantization**: for every packed U32 weight I took the bits from `config.json`, with the per-module overrides
  where they exist. The implied input width (packed columns × 32 / bits) must equal the scale columns × the group
  size. Qwen3-8B-8bit: all 254 packed weights are 8 bits, group 64, which agrees with its config.json
  (`{'group_size': 64, 'bits': 8}`). Qwen3-Next-80B: 446 are 4 bits and 96 are 8 bits (the router gates and the
  shared-expert gates: 50,429,952 B of 8-bit weight). Every other model is all 4 bits, group 64.

**KV**, from `config.json`, per architecture. Here a = the activation width in bytes. a = 2 for every model: the
embedding scales are BF16, or F16 for Llama, and MLX's dequantized embedding output takes the scales' dtype.

- Every layer full attention (`qwen3`, `qwen3_moe`, `llama`):
  per-token bytes = L × 2 (K and V) × n_kv × head_dim × a, and there is no constant term.
  - Qwen3-30B-A3B: 48 × 2 × 4 × 128 × 2 = 98,304 B per token. Its experts change W, not the cache.
  - Llama-3.3-70B: 80 × 2 × 8 × 128 × 2 = 327,680 B per token.
  - Qwen3-8B-4bit and 8B-8bit: 36 × 2 × 8 × 128 × 2 = 147,456 B per token for both. Their two config.json files
    differ only in the quantization block, and the cache holds activations, not weights.
- Hybrid (`qwen3_next`, `qwen3_5_moe_text`): a layer i is full attention when (i + 1) mod `full_attention_interval`
  = 0. For Qwen3.5 this agrees with `layer_types`. Every other layer is gated-delta linear attention, whose cache is
  a fixed-size state.
  - Full-attention part: L_fa × 2 × n_kv × head_dim × a per token.
  - Each linear layer's state = conv state (K − 1) × conv_dim × a, plus recurrent state Hv × Dv × Dk × 4.
    conv_dim = 2 × Hk × Dk + Hv × Dv. The recurrent state is float32 (`mlx_lm/models/gated_delta.py`:
    `mx.zeros((B, Hv, Dv, Dk), dtype=mx.float32)`). The conv state takes the input dtype
    (`qwen3_next.py`, `qwen3_5.py`). Qwen3.5's config also says `mamba_ssm_dtype: float32`.
  - Qwen3-Next-80B: 12 full layers × 2 × 2 × 256 × 2 = 24,576 B per token. 36 linear layers, each
    3 × 8,192 × 2 + 32 × 128 × 128 × 4 = 49,152 + 2,097,152 = 2,146,304 B, so the constant is 77,266,944 B.
  - Qwen3.5-122B-A10B: 12 full layers × 2 × 2 × 256 × 2 = 24,576 B per token. 36 linear layers, each
    3 × 12,288 × 2 + 64 × 128 × 128 × 4 = 73,728 + 4,194,304 = 4,268,032 B, so the constant is 153,649,152 B.
- Cache size at n positions = n_alloc(n) × per-token bytes + constant, where n_alloc(n) = ceil(n / 256) × 256
  (mlx-lm `KVCache.step = 256`). At 2,048 and 2,560 positions, allocated equals occupied.
  KV = (cache(2,048) + cache(2,560)) / 2 = 2,304 × per-token bytes + constant (§4).

Negative control: in a copy of the manifest I added 1 B to Qwen3-Next's KV, 2 B to one of its tensor rows and
0.5 B to Qwen3-8B-8bit's W. `compare` then reported exactly those three mismatches. The copy was deleted afterwards.

### Table 1: W, R and KV, re-derived against the manifest (bytes)

The manifest columns are shown exactly as the JSON stores them. "Diff" is re-derived minus manifest, over W, R, KV
and b.

| Model | type | W re-derived | W manifest | R re-derived | R manifest | KV per token | KV constant | cache @2048 | cache @2560 | KV re-derived | KV manifest | b = W + KV | Diff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-1.7B-4bit | qwen3 | 968,002,688 | 968002688.0 | 968,001,536 | 968001536 | 114,688 | 0 | 234,881,024 | 293,601,280 | 264,241,152 | 264241152.0 | 1,232,243,840 | 0 |
| Qwen3-4B-4bit | qwen3 | 2,262,921,632 | 2262921632.0 | 2,262,920,192 | 2262920192 | 147,456 | 0 | 301,989,888 | 377,487,360 | 339,738,624 | 339738624.0 | 2,602,660,256 | 0 |
| Qwen3-8B-4bit | qwen3 | 4,257,673,472 | 4257673472.0 | 4,607,731,712 | 4607731712 | 147,456 | 0 | 301,989,888 | 377,487,360 | 339,738,624 | 339738624.0 | 4,597,412,096 | 0 |
| Qwen3-8B-8bit | qwen3 | 8,041,724,160 | 8041724160.0 | 8,702,945,280 | 8702945280 | 147,456 | 0 | 301,989,888 | 377,487,360 | 339,738,624 | 339738624.0 | 8,381,462,784 | 0 |
| Qwen3-14B-4bit | qwen3 | 7,870,210,880 | 7870210880.0 | 8,307,783,680 | 8307783680 | 163,840 | 0 | 335,544,320 | 419,430,400 | 377,487,360 | 377487360.0 | 8,247,698,240 | 0 |
| Qwen3-32B-4bit | qwen3 | 17,992,094,528 | 17992094528.0 | 18,429,667,328 | 18429667328 | 262,144 | 0 | 536,870,912 | 671,088,640 | 603,979,776 | 603979776.0 | 18,596,074,304 | 0 |
| Llama-3.3-70B-Instruct-4bit | llama | 39,097,356,800 | 39097356800.0 | 39,688,355,840 | 39688355840 | 327,680 | 0 | 671,088,640 | 838,860,800 | 754,974,720 | 754974720.0 | 39,852,331,520 | 0 |
| Qwen3-30B-A3B-4bit | qwen3_moe | 1,711,355,008 | 1711355008.0 | 17,174,622,208 | 17174622208 | 98,304 | 0 | 201,326,592 | 251,658,240 | 226,492,416 | 226492416.0 | 1,937,847,424 | 0 |
| Qwen3-Next-80B-A3B-Instruct-4bit | qwen3_next | 2,031,833,728 | 2031833728.0 | 44,844,060,160 | 44844060160 | 24,576 | 77,266,944 | 127,598,592 | 140,181,504 | 133,890,048 | 133890048.0 | 2,165,723,776 | 0 |
| Qwen3.5-122B-A10B-4bit | qwen3_5_moe_text | 5,070,253,248 | 5070253248.0 | 68,690,732,544 | 68690732544 | 24,576 | 153,649,152 | 203,980,800 | 216,563,712 | 210,272,256 | 210272256.0 | 5,280,525,504 | 0 |

The lead's record says Qwen3-8B-8bit's KV is 339,738,624 B, equal to Qwen3-8B-4bit's. Confirmed:
147,456 × 2,304 = 339,738,624.

### Table 2: category totals and the W terms (bytes, all equal to the manifest)

| Model | always_active | embed | lm_head | routed | shared | not_loaded | 1 embed row | k/E | k/E × routed | tied | bits/group (count) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-1.7B-4bit | 792,971,264 | 175,030,272 | 0 | 0 | 0 | 0 | 1,152 | - | 0 | yes | 4b/64g (197) |
| Qwen3-4B-4bit | 2,044,132,352 | 218,787,840 | 0 | 0 | 0 | 0 | 1,440 | - | 0 | yes | 4b/64g (253) |
| Qwen3-8B-4bit | 3,907,610,624 | 350,060,544 | 350,060,544 | 0 | 0 | 0 | 2,304 | - | 0 | no | 4b/64g (254) |
| Qwen3-8B-8bit | 7,380,494,336 | 661,225,472 | 661,225,472 | 0 | 0 | 0 | 4,352 | - | 0 | no | 8b/64g (254) |
| Qwen3-14B-4bit | 7,432,632,320 | 437,575,680 | 437,575,680 | 0 | 0 | 0 | 2,880 | - | 0 | no | 4b/64g (282) |
| Qwen3-32B-4bit | 17,554,515,968 | 437,575,680 | 437,575,680 | 0 | 0 | 0 | 2,880 | - | 0 | no | 4b/64g (450) |
| Llama-3.3-70B-Instruct-4bit | 38,506,348,544 | 591,003,648 | 591,003,648 | 0 | 0 | 0 | 4,608 | - | 0 | no | 4b/64g (562) |
| Qwen3-30B-A3B-4bit | 517,107,712 | 175,030,272 | 175,030,272 | 16,307,453,952 | 0 | 0 | 1,152 | 8/128 | 1,019,215,872 | no | 4b/64g (386) |
| Qwen3-Next-80B-A3B-Instruct-4bit | 922,521,088 | 175,030,272 | 175,030,272 | 43,486,543,872 | 84,934,656 | 0 | 1,152 | 10/512 | 849,346,560 | no | 4b/64g (446), 8b/64g (96) |
| Qwen3.5-122B-A10B-4bit | 2,347,918,848 | 429,096,960 | 429,096,960 | 65,229,815,808 | 254,803,968 | 902,581,728 | 1,728 | 8/256 | 2,038,431,744 | no | 4b/64g (614) |

Worked example (Qwen3-30B-A3B): W = 517,107,712 + 0 + 175,030,272 + 1,152 + 16,307,453,952 / 128 × 8 =
1,711,355,008, the manifest's value.

### Why some manifest values are floats, and the 4.77e-7 bytes

- The comparison bar is exact equality. Byte counts are integers, and bit identity is the property being checked.
- `W_bytes`, `KV_bytes` and `b_bytes` are JSON floats (`968002688.0`). `R_bytes` is an int.
  `scripts/bytes_manifest.py` computes W with true division (`cats["embed"] / vocab`,
  `cats["routed_experts"] * (k / experts)`) and KV as `(start + end) / 2`. Every one of these values is a whole
  number and equals my integer exactly, so no rounding happened. The reasons:
  - The dividends divide exactly.
  - Every E here (128, 512, 256) is a power of two, so k/E is exact in binary.
  - All values are far below 2^53.
  - Flag only: the registration says the counts are integers. If a future model had an E that is not a power of
    two, W could pick up float rounding. Emitting the integers would remove the question.
- Qwen3-8B-4bit's printed difference from the pilot, `W_minus_pilot_bytes = 4.76837158203125e-07`, is not a byte
  difference. The pilot column stores 4.257673472 GB. The nearest double is 4.2576734719999995704…, and that × 1e9
  rounds to 4,257,673,471.9999995. That is exactly one unit in the last place (2^-21 = 4.77e-7) below the integer
  4,257,673,472. W / 1e9 == 4.257673472 is True, and so is the same test for the other eight pilot rows.
  Qwen3-8B-8bit has no pilot row, so its difference is null.

### By-products for other slots (not asked; same manifest)

These are the registration's §2 printed ranges, if the ten-model roster stands:
max b / min b = 39,852,331,520 / 1,232,243,840 = 32.34, so `32`-fold (Llama-70B over Qwen3-1.7B).
max R / min R = 68,690,732,544 / 968,001,536 = 70.96, so `71`-fold (Qwen3.5-122B over Qwen3-1.7B).

## Part 2: the C4 identity pins (fills `⟦MAC: C4 pins⟧`)

### How

1. **Kit derivation.** `derive()` from the kit script at `c10b6895f` was imported unchanged and run once per sub-pack
   tree, with its module global `KIT` set to `configs/campaigns/bytes-sN-pP`. It resolves every
   `campaign_collection` stage from its own argv. It reads each stage's `order_manifest.json` up to
   `expected_count`. It hashes each model source with `joulewise.provenance.model_artifact_identity`: every
   `*.safetensors` (and other weight suffixes) found under the source directory without following directory
   symlinks, each file read through its symlink, folded as sha256("joulewise.model_artifact_identity.v1" NUL
   canonical JSON of {lexical path: sha256}). This is Addendum 5 item 5's "hash through the symlinks". The driver
   memoised the identity function, so each source was hashed once per call. It ran as six calls (sN-p1 and sN-p2
   together), 2 to 31 s each, and then a merge. The merge joins the per-pack unit tables. It refuses if a unit name
   maps to two sources, names, revisions or digests. It writes `configs/bytes/identity_pins.json` in the kit's schema
   (`joulewise.b5_identity_pins.v1`; required keys checked).
2. **Independent hash** (`rederive.py hash` and `fold`, stdlib only). It walks the same files, takes their SHA-256s
   and folds them the same way. It also checks each file against what Hugging Face recorded for it:
   - An HF-cache snapshot file is a symlink to a blob named by its LFS SHA-256.
   - A `jw_models` local-dir download keeps the revision and the etag (the LFS SHA-256) in
     `.cache/huggingface/download/<file>.metadata`.
3. **Independent member counts** (`rederive.py sources`). The same stage argv and order manifests were read with no
   joulewise code. They give 50 configs per science model per pack and 25 reference configs per pack (18 bound
   corpus + 3 start + 1 midpoint + 3 end), which equals the derive counts.

### Table 3: C4 pins

"Configs" is the number of planned members over the packs. "= kit" compares with the kit's `identity_pins.json`
at `c10b6895f`. "= indep." compares with my independent fold. "HF hash" means every file's SHA-256 equals Hugging
Face's recorded hash.

| Unit | Model | Revision | Source | Files | Weight bytes | C4 pin (`model_artifact_sha256`) | Packs (configs) | = kit | = indep. | HF hash |
|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-1p7b | Qwen3-1.7B-4bit | `3b1b1768f8f8` | HF cache snapshot | 1 | 968,080,210 | `e1a4505d32a97bb080eac1d2046b6c99ef46f4483a4323484aaf9b4c546b7f4a` | s1-p1, s1-p2 (100) | yes | yes | yes |
| qwen3-4b | Qwen3-4B-4bit | `4dcb3d101c2a` | HF cache snapshot | 1 | 2,263,022,529 | `188703e30302cb32feff0022d979d507bd8bd6d46bfe89aa9cdd858d38053c7f` | s1-p1, s1-p2 (100) | yes | yes | yes |
| qwen3-8b | Qwen3-8B-4bit | `545dc4251c05` | HF cache snapshot | 1 | 4,607,835,174 | `3e0fb77e7ce1ecb7ec844be3ef8856a23643e05317a55054a63d6af62252be31` | s2-p1, s2-p2 (100) | yes | yes | yes |
| qwen3-30b-a3b | Qwen3-30B-A3B-4bit | `d388dead1515` | HF cache snapshot | 4 | 17,174,780,668 | `3f6468de52bbc126f2853eab947ea44c265dd6c5d88e8da599bd631745326d6f` | s2-p1, s2-p2 (100) | yes | yes | yes |
| qwen3-14b | Qwen3-14B-4bit | `a4d9b2df59d2` | HF cache snapshot | 2 | 8,307,898,514 | `0941a38e0fa5bc183df4b7c8f37adff5161c0c7803b1bec49929252c0b59cd57` | s3-p1, s3-p2 (100) | yes | yes | yes |
| qwen3-next-80b | Qwen3-Next-80B-A3B-Instruct-4bit | `d8a069bfa8ae` | HF cache snapshot | 9 | 44,844,286,500 | `5cc91648a8fe6268c370da36efc941d895f8833db4f0cae25e1a447b4477fa7a` | s3-p1, s3-p2 (100) | yes | yes | yes |
| qwen3-32b | Qwen3-32B-4bit | `bcaaf7f538ad` | HF cache snapshot | 4 | 18,429,850,874 | `b23493623baed462c8f85a87d9d729c5b438fd3203143530438d6fa07999b7f5` | s4-p1, s4-p2 (100) | yes | yes | yes |
| qwen3-8b-8bit | Qwen3-8B-8bit | null in configs (files: `48a0b75b1ae7`) | `jw_models` local-dir | 2 | 8,703,048,996 | `d4f5fe85e4b0dccc49a48098978f39540cfb6f52baafb6f78656cdbacba2a753` | s4-p1, s4-p2 (100) | yes | yes | yes |
| llama-70b | Llama-3.3-70B-Instruct-4bit | `de2dfaf56839` | HF cache snapshot | 8 | 39,688,567,605 | `39ba19aafdadde1f292976e6a62ada8485f60e438eb6b4d6d23aaabc4bf3f31c` | s5-p1, s5-p2 (100) | yes | yes | yes |
| qwen35-122b | Qwen3.5-122B-A10B-4bit | `e9c67b088999` | `jw_models` local-dir | 14 | 69,593,636,939 | `613c0db8682be57b905d889a019d25946dd1e6dbd4319269b9eedd7beba1c524` | s6-p1, s6-p2 (100) | yes | yes | yes |
| neg8_reference | Qwen2.5-1.5B-Instruct-4bit | `8b403126fc14` | `jw_models` local-dir | 1 | 868,628,559 | `fea4cb940b54448a693c95a0734949cbdca21a39dda990d669b7f615e4a7c712` | all 12 packs (300) | yes | yes | yes |

Full source paths, per-file digests, sizes and resolved blob paths are in `configs/bytes/identity_pins.json`
(`units`, `model_artifact_inventory`). The tree path and sha256 of each pack are under `packs`.

### Revision evidence

- **HF-cache sources:** the snapshot directory name is the revision, and every weight file links to a blob named by
  its SHA-256.
- **`jw_models` sources:** every `download/*.metadata` file names a single revision:
  - Qwen3-8B-8bit: `48a0b75b1ae72503e21e1558d040bc227510ff06`;
  - Qwen3.5-122B: `e9c67b08899964be5fdd069bb1b4bc8907fe68f5`;
  - the reference: `8b403126fc14f14cfc99bb4cfa72ecbc129ea677`.
- **Non-weight files:** `config.json`, `tokenizer.json` and `tokenizer_config.json` match their recorded upstream
  hash (git blob SHA-1, or LFS SHA-256 for `tokenizer.json`) for all eleven sources. The `config.json` and tokenizer
  SHA-256s equal the manifest's `config_sha256` and `tokenizer` hashes.
- **Item G's missing-snapshot finding is resolved.** The finding (RUN.md, 16:17 addendum) was that the configs'
  HF snapshot paths for Qwen3-1.7B, 4B and 8B-4bit did not exist. They exist now (created 2026-10-21 01:19). Their
  weight files, config.json and tokenizer files are byte-identical to the `jw_models` copies the manifest read
  (same SHA-256s). So the manifest's header numbers apply to the files the sessions load.

## Flags (recorded, not refusals)

1. **8B-8bit revision.** The bytes_v1 configs and `roster.json` still carry `revision: null` and
   `revision_status: pending_download_R8_5` for Qwen3-8B-8bit, so its pin carries `model_revision: null`. The files'
   own download metadata name `48a0b75b1ae72503e21e1558d040bc227510ff06`, and both shards' SHA-256s equal HF's etags
   at that revision. The slot `⟦MAC: revision (R8 item 5)⟧` can be filled with that hash. Changing the configs and
   roster is outside this item's write scope; it goes to BY-MERGE or the lead.
2. **Manifest floats.** W, KV and b are stored as integer-valued floats (see Part 1). This is representation only.
3. **What the pins cover.** C4 here is the kit derivation's quantity: weight files only, with `stack_identity` empty
   and flagged `runtime_stack_unobserved`, because no model was executed. The tokenizer and config hashes are
   recorded above and in the manifest, but they are not part of `model_artifact_sha256`.
4. **Label.** `derive()` labels each per-pack document `non_claim` / `NON_CLAIM_FILE_IDENTITIES_ONLY` because it
   was written for the item-H kit. The merged file carries `status: FILE_IDENTITIES_ONLY` and states this in
   `derivation.per_pack_label_note`. The file identities are the same quantity whichever tree dispatches the model.

## Run 3: a second independent pass (2026-10-22)

The workflow was resumed after the Claude usage limit stopped it, and BY-G ran again. This seat did not reuse run 1's
script. It wrote `/Users/edr/night-archive/forward-20261021/BY-G/run3/byg3.py` (untracked, stdlib only, imports
nothing from `joulewise/` or `scripts/`; sha256 `d702eb389160b2683fc9355fd8114e8f7b9994593c91cfaf3e7026171798f5a0`).
The category rules come from §4 of the registration, and the KV formulas are the ones in Part 1.

- **Bytes:** 31 checks per model, 310 in all, against the manifest at `99c9099d8` (sha256 `33352242…afe1c`). There
  are **0 mismatches**. Each model is checked on:
  - W, R, KV and b, with float-stored counts required to be integer-valued and equal;
  - the six category totals, k, E, tied embeddings and the shared-expert bytes;
  - the config and tokenizer SHA-256s;
  - the four GB columns, compared bit for bit with bytes / 1e9;
  - both cache snapshots, total and per layer (class, allocated bytes, capacity, occupied length, state shapes);
  - every tensor row (dtype, shape, stored bytes, category).

  The header checks also pass: each span equals shape × dtype width, the spans tile each file, and the index agrees.
  The quantization check passes too: Qwen3-8B-8bit has 254 packed weights at 8 bits with group 64.
- **Negative control:** a copy of the manifest had five values changed: W of 8B-8bit +0.5 B, KV of Next-80B +1 B,
  one Next-80B layer's allocated bytes +2 B, one tensor row +2 B, and Llama-70B's `R_GB` moved by one unit in the last
  place. The script reported exactly those five (seven lines, because a layer or row mismatch also shows in its
  count). The copy was deleted.
- **Pins:** `byg3.py hash` covered the same 47 weight files (215,449,636,568 B), one call per model, 4 to 102 s
  each. Every file's SHA-256 equals Hugging Face's recorded hash: the blob name for an HF-cache file, or the etag in
  the download metadata for a `jw_models` file. Folding them gives all eleven pins in Table 3. Each equals both
  `configs/bytes/identity_pins.json` at `10f3e4f15` and the kit's `identity_pins.json` at `c10b6895f`
  (11 of 11, 0 unequal).
- **Kit derivation re-run:** the derivation was run again, per sub-pack pair, through the kit's `derive()` at
  `c10b6895f` (driver `byg_derive_pins.py`, sha256 `14e3f70e…5c55c8`, unchanged). The pairs took 21 s to 4 min 28 s.
  The re-run gave the same units and config counts: 50 per science model per pack, which is 10 repeats + 10 quads ×
  4, and 25 reference members per pack, which is 18 + 3 + 1 + 3. After the merge, the output is byte-identical to the
  committed file (sha256 `553859a07578869ed4afe7b4b406462897b561d684b64a8e29ee33f800c4392f`).
- The twelve sub-pack trees, `bytes_v1/`, `joulewise/provenance.py` and `joulewise/b5/plan.py` have no diff
  between `c10b6895f` and `99c9099d8`. So the pins apply to this branch's trees.

One-model re-run with the run-3 script (Qwen3-8B-8bit; about 1 s for the bytes and 20 s for the hash):

```sh
/opt/homebrew/bin/python3.13 -I /Users/edr/night-archive/forward-20261021/BY-G/run3/byg3.py bytes --manifest /Users/edr/night-archive/forward-20261021/BY-G/run3/manifest.99c9099d8.json --model Qwen3-8B-8bit --out /Users/edr/night-archive/forward-20261021/BY-G/run3/lead-8b8-bytes.json
/opt/homebrew/bin/python3.13 -I /Users/edr/night-archive/forward-20261021/BY-G/run3/byg3.py hash --model-dir /Users/edr/jw_models/mlx-community/Qwen3-8B-8bit --out /Users/edr/night-archive/forward-20261021/BY-G/run3/lead-8b8-hash.json
/opt/homebrew/bin/python3.13 -I /Users/edr/night-archive/forward-20261021/BY-G/run3/byg3.py fold --parts /Users/edr/night-archive/forward-20261021/BY-G/run3/lead-8b8-hash.json
```

Expected: `{"checks": 31, "mismatches": 0, ...}`; then `folded_sha256`
`d4f5fe85e4b0dccc49a48098978f39540cfb6f52baafb6f78656cdbacba2a753` with `upstream_all_match` true.

## Reproduce (the lead re-runs on one model)

The manifest bytes for one model take about 1 s. The example is Qwen3-8B-8bit, from a scratch output directory:

```sh
/opt/homebrew/bin/python3.13 -I /Users/edr/night-archive/forward-20261021/BY-G/rederive.py bytes --model-dir /Users/edr/jw_models/mlx-community/Qwen3-8B-8bit --out /Users/edr/night-archive/forward-20261021/BY-G/lead-8b8.json
/opt/homebrew/bin/python3.13 -I /Users/edr/night-archive/forward-20261021/BY-G/rederive.py compare --manifest /Users/edr/night-archive/forward-20261021/BY-G/bytes_manifest.99c9099d8.json --records /Users/edr/night-archive/forward-20261021/BY-G/lead-8b8.json
```

Expected: `"total_mismatches": 0`. The `compare` step picks the manifest row whose `model_dir` equals `--model-dir`,
so pass the manifest's own path for the model.

The independent pin for one model takes about 5 s for 8.7 GB:

```sh
/opt/homebrew/bin/python3.13 -I /Users/edr/night-archive/forward-20261021/BY-G/rederive.py hash --model-dir /Users/edr/jw_models/mlx-community/Qwen3-8B-8bit --out /Users/edr/night-archive/forward-20261021/BY-G/lead-8b8-hash.json
/opt/homebrew/bin/python3.13 -I /Users/edr/night-archive/forward-20261021/BY-G/rederive.py fold --parts /Users/edr/night-archive/forward-20261021/BY-G/lead-8b8-hash.json
```

Expected: `folded_sha256` `d4f5fe85e4b0dccc49a48098978f39540cfb6f52baafb6f78656cdbacba2a753` and
`upstream_all_match` true. A model too large for one 10-minute call can be hashed in parts
(`hash --only <file1>,<file2> --out partN.json`), then joined with `fold --parts part1.json part2.json …`.

The kit derivation for one pass pair (here s4), then the merge. The kit root is a checkout at `c10b6895f`:

```sh
/opt/homebrew/bin/python3.13 -I -B /Users/edr/night-archive/forward-20261021/BY-G/byg_derive_pins.py derive --kit-root <checkout at c10b6895f> --runtime-python /Users/edr/code/JouleWise/.venv/bin/python --packs bytes-s4-p1 bytes-s4-p2 --out s4.json
/opt/homebrew/bin/python3.13 -I -B /Users/edr/night-archive/forward-20261021/BY-G/byg_derive_pins.py merge --partials s1.json s2.json s3.json s4.json s5.json s6.json --kit-pins <checkout at c10b6895f>/configs/campaigns/bytes_mac_check/registration/identity_pins.json --out configs/bytes/identity_pins.json
```

## Appendix: pin driver text (`byg_derive_pins.py`, sha256 `14e3f70eb13471aa7337cd0201589012645edfbb7398f1cdbe5b594f655c55c8`)

<details><summary>byg_derive_pins.py</summary>

```python
#!/usr/bin/env python3
"""BY-G driver: run the kit's derive() (configs/campaigns/bytes_mac_check/registration/derive_identity_pins.py
at c10b6895f, unchanged) over the twelve BYTES sub-pack plan trees instead of the kit tree.

  derive --kit-root K --runtime-python P --packs bytes-sN-p1 bytes-sN-p2 --out partial.json
  merge  --partials a.json b.json ... --kit-pins K/configs/campaigns/bytes_mac_check/registration/identity_pins.json --out pins.json

derive() reads the module global KIT for the tree path, so each pack sets KIT to configs/campaigns/<pack>.
Each local model source is hashed once per process (the identity function is memoised; derive() accepts
it as a parameter). merge joins the per-pack unit tables and refuses if one unit name maps to two sources,
names, revisions or digests.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

PACKS = [f"bytes-s{n}-p{p}" for n in range(1, 7) for p in (1, 2)]
SCRIPT = Path("configs/campaigns/bytes_mac_check/registration/derive_identity_pins.py")


def load(kit_root):
    spec = importlib.util.spec_from_file_location("derive_identity_pins", kit_root / SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cmd_derive(a):
    kit_root = Path(a.kit_root).resolve()
    mod = load(kit_root)
    cache = {}

    def identity(source):
        if source not in cache:
            cache[source] = mod.model_artifact_identity(source)
        return cache[source]

    out = {"kit_script_sha256": hashlib.sha256((kit_root / SCRIPT).read_bytes()).hexdigest(), "packs": {}, "artifacts": {}}
    for pack in a.packs:
        mod.KIT = Path("configs/campaigns") / pack
        doc, art = mod.derive(kit_root, a.runtime_python, identity=identity)
        out["packs"][pack] = doc
        for name, artifact in art["artifacts"].items():
            prev = out["artifacts"].setdefault(name, artifact)
            if prev.get("folded_sha256") != artifact.get("folded_sha256"):
                raise SystemExit(f"{pack}: {name} digest differs between packs")
        print(pack, {n: (u["model_artifact_sha256"], u["config_count"]) for n, u in doc["units"].items()})
    Path(a.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return 0


def cmd_merge(a):
    parts = [json.loads(Path(p).read_text()) for p in a.partials]
    packs, artifacts, script_sha = {}, {}, {p["kit_script_sha256"] for p in parts}
    if len(script_sha) != 1:
        raise SystemExit("partials from different kit scripts")
    for p in parts:
        for pack, doc in p["packs"].items():
            if pack in packs:
                raise SystemExit("pack twice: " + pack)
            packs[pack] = doc
        for name, art in p["artifacts"].items():
            prev = artifacts.setdefault(name, art)
            if prev.get("folded_sha256") != art.get("folded_sha256"):
                raise SystemExit("digest differs across partials: " + name)
    if sorted(packs) != sorted(PACKS):
        raise SystemExit(f"packs missing: {sorted(set(PACKS) - set(packs))}")
    runtime = {json.dumps(packs[p]["runtime_versions"], sort_keys=True) for p in PACKS}
    pythons = {packs[p]["runtime_python_observed"] for p in PACKS}
    if len(runtime) != 1 or len(pythons) != 1:
        raise SystemExit("runtime observations differ between packs")
    units = {}
    for pack in PACKS:
        for name, u in packs[pack]["units"].items():
            m = units.setdefault(name, {"model_source": u["model_source"], "model_name": u["model_name"],
                                        "model_revision": u["model_revision"], "model_artifact_sha256": u["model_artifact_sha256"],
                                        "stack_identity": u["stack_identity"], "flags": u["flags"],
                                        "packs": [], "config_count": 0, "config_paths": []})
            for k in ("model_source", "model_name", "model_revision", "model_artifact_sha256"):
                if m[k] != u[k]:
                    raise SystemExit(f"{name}: {k} differs in {pack}")
            m["packs"].append(pack)
            m["config_count"] += u["config_count"]
            m["config_paths"].extend(u["config_paths"])
    kit = json.loads(Path(a.kit_pins).read_text())
    comparison = {}
    for name, u in units.items():
        k = kit["units"].get(name)
        comparison[name] = None if k is None else {
            f: (u[f] == k[f]) for f in ("model_source", "model_name", "model_revision", "model_artifact_sha256")}
    first = packs[PACKS[0]]
    doc = {
        "schema": "joulewise.b5_identity_pins.v1",
        "status": "FILE_IDENTITIES_ONLY",
        "scope": "C4 model file identities for the twelve BYTES sub-packs bytes-s1-p1 .. bytes-s6-p2 (R8 item 7; registration section 5)",
        "runtime_python_observed": first["runtime_python_observed"],
        "runtime_versions": first["runtime_versions"],
        "units": units,
        "packs": {p: {"tree_path": packs[p]["derivation"]["tree_path"], "tree_sha256": packs[p]["derivation"]["tree_sha256"],
                      "units": sorted(packs[p]["units"])} for p in PACKS},
        "comparison_with_kit_pins": {"path": "configs/campaigns/bytes_mac_check/registration/identity_pins.json",
                                     "commit": "c10b6895f", "fields_equal": comparison},
        "model_artifact_inventory": artifacts,
        "derivation": {
            "generator": SCRIPT.as_posix() + " at c10b6895f, derive() unchanged, called once per sub-pack plan tree "
                         "(module global KIT set to configs/campaigns/<pack>); driver text in "
                         "docs/process_traces/2026-10-22-forward/BY-G-MANIFEST-REDERIVATION.md",
            "generator_sha256": script_sha.pop(),
            "model_artifact_sha256": first["derivation"]["model_artifact_sha256"],
            "runtime_versions": first["derivation"]["runtime_versions"],
            "stack_identity": first["derivation"]["stack_identity"],
            "config_count": "number of dispatched planned members for this source, summed over the twelve packs, including reference members",
            "per_pack_label_note": "derive() labels each per-pack document non_claim/NON_CLAIM_FILE_IDENTITIES_ONLY because it was written "
                                   "for the item-H kit; the file identities are the same quantity whichever tree dispatches the model, "
                                   "and this merged document carries status FILE_IDENTITIES_ONLY: no model executed, no runtime stack observed.",
        },
    }
    Path(a.out).write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(json.dumps({n: [u["model_artifact_sha256"], u["config_count"], u["packs"], comparison[n]] for n, u in units.items()}, indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sp = ap.add_subparsers(dest="cmd", required=True)
    d = sp.add_parser("derive"); d.add_argument("--kit-root", required=True); d.add_argument("--runtime-python", required=True)
    d.add_argument("--packs", nargs="+", required=True); d.add_argument("--out", required=True)
    m = sp.add_parser("merge"); m.add_argument("--partials", nargs="+", required=True); m.add_argument("--kit-pins", required=True)
    m.add_argument("--out", required=True)
    a = ap.parse_args()
    return {"derive": cmd_derive, "merge": cmd_merge}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
```

</details>
