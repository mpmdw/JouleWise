# ALIGN hybrid prompt-cache checkpoints

This extends `episode_prefix` for mlx-lm's non-rotating `KVCache` /
`ArraysCache` mixture. The serving pins remain mlx 0.31.2 and mlx-lm 0.31.3.
The PR #657 review reports the pre-fix native gate passing **4/4** on those pins,
with bitwise matched-schedule restored logits at boundaries 512 and 73 for both
families and dtypes; its benchmark also passed. This fix round cannot run MLX.
The revised 2048-token/context path and new native context test require a lead
rerun. Production-model/template and measurement readiness remain PROVISIONAL.
Amendment 1's W1 contains Qwen3.8-27B only; Next is dropped and Flash-Next is
later. Next code/tests here are historical implementation coverage.

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

With limit zero/None, the endpoint does not render or encode closed history.
Enabled checkpoints still pay for a second full-history render/encode inside
`generation_setup`. Its cost as context grows has not been measured. R1 must
quantify that overhead before enabled use in a measurement window; the U6
turn-index residual cannot be assumed unaffected. A constant-suffix boundary
optimization is deferred until it can be verified against the actual templates.

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

The prefill callback is ALIGN-local in `apple/endpoint.py`'s stream observer.
`apple/generation.py` passes an explicit runtime view to the unchanged core
generation method; it does not replace methods or swap the prepared runtime's
native module. The view retains the full delta for core accounting while the
observer feeds only its remaining suffix to the native stream. Per the ALIGN
v4 plan ruling 4, the complete `joulewise/adapters/mlx_runtime.py` file is restored
to pilot-10 `83e2dac59`; no new pinned-core rebind is needed. Boundary tests pin
that complete file and compare disabled-checkpoint output/event/provenance
bytes with the prior dispatch for both `None` and `0`.

Each checkpoint retains an offset for every attention layer and deep-copies
the Python containers of **each entire ArraysCache object**, including auxiliary
metadata. In MLX 0.31.2, `deepcopy(mx.array)` retains the underlying buffer by
reference under immutable-array value semantics; it does not copy array bytes.
Retained references prevent buffer donation while a snapshot uses the value.
Arrays are evaluated before generation continues. KV tensors remain in the
active cache. Restore trims attention layers and installs independent recurrent
containers retaining the saved arrays; the snapshot remains reusable.
Native offsets must agree with the token ledger before
and after restoration. A partial or failed operation invalidates the episode
cache through the existing endpoint error path.

`EpisodeSpec.hybrid_checkpoint_limit` defaults to **None**, preserving legacy
serialized bytes and rebuild-only behavior. A positive integer explicitly
enables that many retained checkpoints; `None` omits the field from serialized
specs and execution policy and also disables checkpointing. The v4 kit must
set **0** explicitly for Qwen3.8; legacy specs retain their omission.
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
- `cache_checkpoint_count`, `cache_checkpoint_bytes` and
  `cache_checkpoint_retained_bytes` retain their setup-time values in both the
  event and generation record. Separate `*_after_prefill` fields report the
  post-snapshot values, including when prefill does not create a snapshot.
- A config-derived payload estimate when the prepared model config has the
  required shape fields. Missing shapes are explicitly marked unavailable.

Byte accounting is `array_nbytes_plus_u64_offsets`: retained recurrent arrays,
including auxiliary array attributes, plus eight logical bytes per KV offset.
It is a payload count, not measured allocator residency or bus traffic. Python
object overhead, active model/cache memory and allocator fragmentation are
excluded. Creating a checkpoint can temporarily retain N+1 snapshots before
eviction; active recurrence can later allocate new storage. Shared buffers make
logical payload totals different from incremental allocator bytes. No energy-model term,
predictor, exclusion rule or stopping rule changes. Legacy specs omitting the
new field retain their execution-policy identity. Specs with an explicit limit
(including zero) include it in identity for every model. Disabled and
non-hybrid runtime record/event bytes retain the existing cache behavior.

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
model arrays; the review reports it passed on tiny models. The production
runtime dtypes remain unverified by this fix round.

| Model / evidence | Linear / full layers | Conv bytes/layer | Recurrent bytes/layer | Payload/checkpoint | Two retained |
|---|---:|---:|---:|---:|---:|
| Qwen3.8-27B, clone-provided config fixture | 48 / 16 | 61,440 | 3,145,728 | 153,944,192 B (146.8126 MiB) | 293.6252 MiB |
| Qwen3-Next-80B-A3B, clone-provided mlx-community config fixture | 36 / 12 | 49,152 | 2,097,152 | 77,267,040 B (73.6876 MiB) | 147.3752 MiB |

Qwen3.8 uses Hk=16, Hv=48, Dk=Dv=128, kernel=4 and 64 layers.
`tests/align/fixtures/qwen38_config.json` is a byte-for-byte copy of this clone's
`.hf-qwen38/config.json`, SHA-256
`8f80874ac3ad8fa386d3f6dc0ea85377f703376e009a03dee0360e08e289a25d`.
Its `mamba_ssm_dtype` says float32. The review verified these bytes against
mlx-community/Qwen3.8-27B-8bit at revision `815b83c0`.

The Next row is now computed from the user-supplied mlx-community
`.hf-next/config.json`: 48 layers, full attention every fourth layer, Hk=16,
Hv=32, Dk=Dv=128 and kernel=4. The byte-identical retained fixture is
`tests/align/fixtures/qwen3_next_config.json`, SHA-256
`f5a5422b8e3d47733f0073ff22dec1dc4a7832fec5fc1cf36eba31ace03cf0c4`.
The real config confirms the earlier conditional arithmetic. The review
verified these bytes against mlx-community/Qwen3-Next-80B-A3B-Thinking-4bit at
revision `9a2b4634`. This offline fix round checked equality with the review's
retained configs; it did not repeat network authentication.
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

**2026-11-05 review update:** the review reports the original native exactness
gate and benchmark passed with mlx 0.31.2 / mlx-lm 0.31.3, and restored logits
were bitwise equal to matched-schedule full re-prefill (max absolute difference
zero in that comparison). This supersedes the earlier sandbox-blocked evidence,
without turning the earlier failed attempts into passes. These are supplied
review results. They do not validate this fix round's revised schedule/context,
quantized production trajectories or energy behavior. See the run reports for
the evidence split and exact lead rerun commands.

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
suffix schedule. No tolerance is accepted. Prefix lengths 2048 and 73 exercise
both aligned and partial boundaries; at 2048 the reference is also ordinary
2048-token chunked full prefill. A separate one-call full prefill reports bitwise
status and actual maximum absolute difference as a diagnostic. Deterministic
kernels alone do not imply equality across different chunk/matmul shapes.
This gate cannot establish arbitrary chunk-schedule equality, real-template
stability or production-weight behavior.

The five native tests skip only when MLX/MLX-LM packages are absent. Installed
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
For bf16 history / fp32 recurrence, the tiny retained-state payloads are 26,880 B
(Next) and 39,744 B (Qwen3.5). The real/tiny array-byte ratios describe payload
only. **No byte-proportional timing projection is valid** for reference-retaining
snapshots; the probe leaves that legacy field null even when given measured
timings. The review's benchmark reported zero extra active array bytes for
snapshot/restore, while its retained-memory probe confirmed the saved buffers
stay live. These are review-supplied results, not rerun in this sandbox.

For real configs, two retained snapshots occupy the table's payload. Snapshot
replacement can briefly retain three generations of recurrent array values:
231,800,832 B (Next), 461,832,192 B (Qwen3.8). Including the active recurrence
gives a conservative four-set planning allowance of 309,067,776 B and
615,776,256 B, respectively. This excludes weights, KV arrays, Python objects,
allocator overhead, offsets and kernel workspaces, so it is not process RSS.
Buffers can be shared across these logical sets. The four-set figure is a
conservative planning allowance, not an allocation or measured restore peak.
Real models were not loaded.
