# ALIGN hybrid prompt-cache checkpoints (PROVISIONAL native gate)

This extends `episode_prefix` for mlx-lm's non-rotating `KVCache` /
`ArraysCache` mixture. The serving pins remain mlx 0.31.2 and mlx-lm 0.31.3.
No production model, energy experiment, or measurement-data replay validates
this extension yet. The native numerical unittest must pass before use in a
new ALIGN measurement window.

## Boundary and ownership

At each turn, render the same history without the assistant generation prompt.
Take the token LCP of that closed-history rendering and the actual prompt, capped
to leave one token for native generation. This handles tokenizer merges at the
boundary and excludes the assistant preamble and its mutable thinking markers.
It is a candidate stable boundary, not a prediction about arbitrary templates.
Every eventual restore is independently gated by the **actual next prompt's**
token LCP. Templates that rewrite earlier history can use an older checkpoint;
if none survives, the existing whole-cache rebuild applies. A tokenizer that
does not support a closed-history render needs native integration work.

Prefill to that boundary in chunks of at most 2048 tokens (the pinned native
non-speculative step size), then checkpoint before
feeding the remaining suffix to `stream_generate`. Both this prefill and the
snapshot run inside the existing measured prefill phase. Restores run in
`generation_setup`. Manual prefill and snapshot execute under mlx-lm's
`wired_limit(model, [generation_stream])` and `mx.stream(generation_stream)`;
each evaluated chunk calls `mx.clear_cache()`, matching native prefill.
No extra sampler draws occur. Full prompt and fed-token
counts continue to include the manually prefetched prefix. A checkpoint is
never taken after generation in the hope of rewinding recurrent state later.

Each checkpoint retains an offset for every attention layer and a Python deep
copy of **each entire ArraysCache object**, including auxiliary metadata. Arrays
are evaluated before generation continues. KV tensors remain in the active
cache and are not duplicated. Restore trims every attention layer to its saved
offset and installs a fresh deep copy of every saved recurrent layer; the saved
copy remains reusable. Native offsets must agree with the token ledger before
and after restoration. A partial or failed operation invalidates the episode
cache through the existing endpoint error path.

`EpisodeSpec.hybrid_checkpoint_limit` defaults to **0**, preserving rebuild-only
behavior. A positive integer explicitly enables that many retained checkpoints;
`None` omits the field from serialized specs and execution policy and also
disables checkpointing. Legacy specs lacking the field retain that omission.
An explicit value is hashed in `execution_policy.hybrid_checkpoint_limit`;
enabled hybrid models also record the resolved checkpoint policy. Choose and
fix the value per model for the **whole series before its first measured window**.
Enabling checkpointing splits the prefill and changes the computation schedule
and token trajectory of **every hybrid turn**, including turn zero and turns
without a restore. Enabling it after W1 invalidates exact W1 seed replays.
Identity and endpoint use the same `hybrid_checkpoint_policy(config, limit)`
resolver. A hybrid cache whose config has no policy runs with limit zero;
cache-class detection alone cannot enable checkpoints. The supported nested
types include `qwen3_5_moe_text`, exercised with the review-retained
mlx-community/Qwen3.5-122B-A10B-4bit config at revision `e9c67b08`:
`tests/align/fixtures/qwen35_122b_config.json`, SHA-256
`fc1c3921b5146143cda7a5feed445cc31c8929cc3f164f967ec6340b448086eb`.
That provenance is supplied by the review, not fetched again in this fix round.
Checkpoints above a branch's reused prefix are
discarded before any suffix can overwrite their KV history. Unknown cache
classes, rotating/quantized attention caches, disk persistence, speculative
generation and batched requests are outside this implementation.

## Restore and observations

Let K be represented tokens and P the next prompt. Reuse the ordinary append-only
path when possible. Otherwise, for a hybrid cache choose the newest checkpoint
whose offset is at most `min(LCP(K,P), len(P)-1)`, restore all layers, and prefill
`P[offset:]`. An absent or evicted compatible checkpoint causes a full rebuild.

Hybrid turns add these observations to the existing `generation` member record:

- `cache_prefill_tokens_saved = len(P) - prefill_tokens`, versus a full rebuild.
- `cache_checkpoint_restore_count` (zero or one) and
  `cache_checkpoint_restore_bytes` (zero on a miss).
- Boundary/restored offsets, retained checkpoint count, latest checkpoint
  payload bytes, total retained payload bytes, limit and policy version.
- A config-derived payload estimate when the prepared model config has the
  required shape fields. Missing shapes are explicitly marked unavailable.

Byte accounting is `array_nbytes_plus_u64_offsets`: copied recurrent arrays,
including auxiliary array attributes, plus eight logical bytes per KV offset.
It is a payload count, not measured allocator residency or bus traffic. Python
object overhead, active model/cache memory and allocator fragmentation are
excluded. Creating a checkpoint can temporarily retain N+1 snapshots before
eviction; restore also needs an active recurrent copy. No energy-model term,
predictor, exclusion rule or stopping rule changes. Non-hybrid execution-policy
identity and generated record/event bytes remain unchanged.

## Config-derived memory

For batch one, with Hk/Hv linear key/value head counts and Dk/Dv head sizes:

```text
convolution history/layer = (kernel-1) * (2*Hk*Dk + Hv*Dv) * conv_itemsize
recurrent state/layer     = Hv * Dk * Dv * state_itemsize
checkpoint payload       = linear_layers * (convolution + recurrent)
                           + full_attention_layers * 8
```

The following estimates assume bf16 convolution history (two bytes) and fp32
recurrent state (four bytes). Weight quantization does not change this assumed
cache precision. The native gate also checks the formula against actual tiny
model arrays; that check has **not run** in the implementation clone.

| Model / evidence | Linear / full layers | Conv bytes/layer | Recurrent bytes/layer | Payload/checkpoint | Two retained |
|---|---:|---:|---:|---:|---:|
| Qwen3.8-27B, clone-provided config fixture | 48 / 16 | 61,440 | 3,145,728 | 153,944,192 B (146.8126 MiB) | 293.6252 MiB |
| Qwen3-Next-80B-A3B, clone-provided mlx-community config fixture | 36 / 12 | 49,152 | 2,097,152 | 77,267,040 B (73.6876 MiB) | 147.3752 MiB |

Qwen3.8 uses Hk=16, Hv=48, Dk=Dv=128, kernel=4 and 64 layers.
`tests/align/fixtures/qwen38_config.json` is a byte-for-byte copy of this clone's
`.hf-qwen38/config.json`, SHA-256
`8f80874ac3ad8fa386d3f6dc0ea85377f703376e009a03dee0360e08e289a25d`.
Its `mamba_ssm_dtype` says float32. External publication/revision provenance was
not independently checked offline.

The Next row is now computed from the user-supplied mlx-community
`.hf-next/config.json`: 48 layers, full attention every fourth layer, Hk=16,
Hv=32, Dk=Dv=128 and kernel=4. The byte-identical retained fixture is
`tests/align/fixtures/qwen3_next_config.json`, SHA-256
`f5a5422b8e3d47733f0073ff22dec1dc4a7832fec5fc1cf36eba31ace03cf0c4`.
The real config confirms the earlier conditional arithmetic. Its upstream
revision/publication provenance was not independently authenticated offline.
Config shape verification does not verify live runtime cache dtypes.

Reproduce both calculations without model or measurement data:

```sh
python3.13 -B - <<'PY'
import json
from pathlib import Path
from joulewise.align.apple.prompt_cache import checkpoint_size_from_config
for name in ('qwen38_config.json', 'qwen3_next_config.json'):
    cfg = json.loads((Path('tests/align/fixtures') / name).read_text())
    print(name, checkpoint_size_from_config(cfg))
PY
```

## Exactness gate and limitations

**2026-11-05 follow-up:** the pinned installation is now available at
`/private/tmp/jwsol/venv-mlx/bin/python`, but this sandbox cannot obtain a Metal
device. Both exactness and timing stop before model creation. See
`docs/run_reports/2026-11-05-align-cache-checkpoint-native.md` for attempted
commands and the two-family inference-mode gate. Max absolute logit difference,
runtime cache shapes/dtypes and native resource cost remain **unmeasured**.

`tests.align.test_cache_checkpoint` provides synthetic mechanics and complete
non-hybrid endpoint-byte regression against base c9a0a3943. These checks do not
provide real-model logit evidence.

`tests.align.test_cache_checkpoint_native` now uses the reusable driver and
mlx-lm's own `qwen3_next.Model` and `qwen3_5.Model`, four layers each, float32
and bf16, Next MoE and Qwen3.5 dense. It explicitly calls `model.eval()` to use
the inference recurrence kernel. Consecutive synthetic turns discard exactly
143, 257 and 560 tokens, matching pilot 2's documented trim counts without
reading its token/data fixtures. It checks snapshot independence, repeated
restoration, native offsets, cache dtype/payload and finite logits.

Repeat full re-prefills establish determinism. Restored suffix logits must be
bitwise identical (uint8 views) to full fresh re-prefills using the same prefix/
suffix schedule. No tolerance is accepted. Prefix lengths 512 and 73 exercise
both aligned and partial boundaries; at 512 the reference is also ordinary
512-token chunked full prefill. A separate one-call full prefill reports bitwise
status and actual maximum absolute difference as a diagnostic. Deterministic
kernels alone do not imply equality across different chunk/matmul shapes.
This gate cannot establish arbitrary chunk-schedule equality, real-template
stability or production-weight behavior.

The four native tests skip only when MLX/MLX-LM packages are absent. Installed
but unusable packages, pin mismatch or Metal device denial fail setup. A skip
or setup failure is not numerical evidence. The stdlib-only probe tests check
real-config model-family routing and memory arithmetic, and ensure estimation
cannot import a native backend.

```sh
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  /private/tmp/jwsol/venv-mlx/bin/python -B -m unittest tests.align.test_cache_checkpoint_native
```

## Resource probe and extrapolation

The offline driver also accepts `--benchmark`. It times actual `_snapshot` and
`_restore` calls on each tiny model/dtype, with explicit synchronization before
and after, three warmups and 25 samples (maximum selectable 100). Prefix and
suffix forwards occur outside each timed operation. Duplicate-offset no-op
snapshots are excluded. Output includes raw samples, median/min/max, active
MLX memory before/after, operation-local peak extra active memory, allocator
cache and process peak RSS. A seven-token decode is part of the exactness gate;
the benchmark uses a 17-token suffix to mutate state between restores.

```sh
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  /private/tmp/jwsol/venv-mlx/bin/python -B scripts/align_cache_checkpoint_native.py --benchmark
PYTHONPATH=. python3.13 -B scripts/align_cache_checkpoint_native.py --estimate-only
```

The second command imports no MLX and reads only the retained config fixtures.
For bf16 history / fp32 recurrence, the tiny state payloads are 26,880 B (Next)
and 39,744 B (Qwen3.5). The corresponding real/tiny array-byte ratios are
2,874.5143 and 3,873.3913. Multiplying a measured tiny copy time by this ratio
is only a **byte-proportional scenario**, not a production prediction or bound:
Python layer overhead, allocator behavior, copy bandwidth and contention differ.
Timing projections remain null until actual timings exist.

For real configs, two retained snapshots occupy the table's payload. Snapshot
replacement can briefly retain three copied sets of recurrent arrays:
231,800,832 B (Next), 461,832,192 B (Qwen3.8). Including the active recurrence
gives a conservative four-set planning allowance of 309,067,776 B and
615,776,256 B, respectively. This excludes weights, KV arrays, Python objects,
allocator overhead, offsets and kernel workspaces, so it is not process RSS.
Restoration copies layers successively; four whole sets are a conservative
planning allowance, not a measured restore peak. Real models were not loaded.
