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

Prefill to that boundary in chunks of at most 512 tokens, then checkpoint before
feeding the remaining suffix to `stream_generate`. Both this prefill and the
snapshot run inside the existing measured prefill phase. Restores run in
`generation_setup`. No extra sampler draws occur. Full prompt and fed-token
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

The default ring keeps the last **two** checkpoints. The internal constructor's
`checkpoint_limit=N` accepts nonnegative integers; zero preserves rebuild-only
behavior. The endpoint uses the fixed default, recorded in the hybrid model's
execution-policy identity. Checkpoints above a branch's reused prefix are
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

`tests.align.test_cache_checkpoint` uses a synthetic in-place recurrence to
check isolation, repeated restoration, correct checkpoint selection, eviction,
fallback, offsets, per-turn accounting, identity and prefill-phase integration.
Its non-hybrid regression compares complete endpoint result, event, provenance,
identity, flags and native-input bytes against the untouched cache implementation
from base commit c9a0a3943. This is structural/synthetic evidence, not real-model
logit evidence.

`tests.align.test_cache_checkpoint_native` builds a tiny random four-layer
Qwen3-Next from mlx-lm's own `Model`/`ModelArgs`, with small vocabulary and four
experts, without loading any weights or tokenizer. It exercises float32 and
bf16, repeated restores after differing suffixes, independent snapshot state,
and config/runtime byte agreement. It is designed to stay far below 1 GB;
resource use has not been measured because the dependencies are absent.

For identical prefill chunks and evaluation barriers, repeat fresh runs first
establish kernel determinism. If deterministic, restored logits must be bitwise
identical. Only demonstrated nondeterminism permits an allclose comparison.
A separate one-shot full re-prefill comparison uses `atol=rtol=1e-5` for float32
and `atol=rtol=0.015625` for bf16, because splitting prefill can change matmul
shapes and recurrent reduction order. These are prospective test bounds, not
measured errors or an assertion of token equality under near-tied logits.
The test prints determinism, bitwise status and maximum absolute bulk error.

Neither Python 3.13 nor the default Python in this clone has mlx-lm installed.
No vendored mlx-lm source was found. Implementation references were the pinned
`env/mac-measurement-lock.txt`, the existing native cache adapter and spike,
and `docs/align/pilot_protocol_v2.md`; no new upstream source/API audit was
possible. Consequently native constructor/API compatibility, deep-copy behavior,
cache shapes/dtypes, numerical exactness and resource use remain **PROVISIONAL**.
Run this module in a clone-local offline installation of the exact pins, fix
any failure, and review the numerical output before a lead-controlled live gate:

```sh
python3.13 -B -m unittest tests.align.test_cache_checkpoint_native
```
