# ALIGN checkpoint native follow-up — 2026-11-05

Branch: `lane/2026-11-05-align-cache-checkpoint`; starting head `46eaf3b79`.
This follow-up supersedes the earlier report's dependency-availability finding.
**Native exactness and native timing remain blocked by Metal device access.**
No max-absolute logit difference has been measured; it must not be reported as 0.

## Authority and safety

Continued the user's explicit four-item lane brief. Read repository instructions,
Mission M0, generated stop card (NONE), queue/do-not-do list, workspace/status
pointers, D-009, the existing cache design/report and pilot protocol. Initial
tree was clean. The explicit brief overrides historical queue ordering and the
normal coordination-state/full-suite close-out requirements.

No network, real measurement data, block-5 analysis, production model weights,
tokenizer or quiet-window experiment was accessed. Absolute study paths in
repository prose were treated as text. Only clone-local sources/configs and
the explicitly supplied `/private/tmp/jwsol/venv-mlx` installation were used.
The venv was not modified (commands set `PYTHONDONTWRITEBYTECODE=1`). No agent
was delegated, integration installed, commit pushed, or coordination state edited.

## Item 1 — native gate and installed-source audit

The supplied interpreter reports **mlx 0.31.2 / mlx-lm 0.31.3**. Inspected its
`qwen3_next.py`, `qwen3_5.py`, `gated_delta.py`, `cache.py`, and MLX API stubs.
Qwen3.8's supplied config is outer `qwen3_5`, nested `qwen3_5_text`; the native
`qwen3_5.Model` wrapper constructs its text model without a vision tower.
Both classes use three `ArraysCache` layers per full-attention `KVCache` at
interval four. Recurrent state is `[B, Hv, Dv, Dk]`, explicitly float32 in
`gated_delta_update`; convolution history follows activation dtype. Corrected
the formula's shape docstring (byte arithmetic is unchanged).

The previous tiny test never called `model.eval()`. MLX modules start in training
mode; both model classes pass `use_kernel=not self.training`. The new reusable
gate explicitly enters inference mode and requires a working Metal device.

`scripts/align_cache_checkpoint_native.py` builds four-layer random models from
the installed classes, float32/bf16, with Next MoE and Qwen3.5 dense MLPs.
It synthesizes consecutive turn rewrites of exactly **143, 257, 560 tokens**,
with seven consumed output tokens per turn, repeated restoration and a pristine
independent prefix to check snapshot ownership. No pilot token fixture is read.
It checks runtime payload/dtypes, offsets, finite logits, repeat determinism and
bitwise equality including signed-zero bits via uint8 views.

Two prefix lengths are used: 512 and 73. Fresh references re-prefill every token
with the same prefix/suffix chunk schedule. At prefix 512 that is also ordinary
512-token full prefill. Prefix 73 checks a partial checkpoint boundary. A separate
single-call full prefill reports its actual maximum error; it does **not** get
an invented tolerance or count as bitwise evidence. Changing GEMM/recurrence
chunk shapes is a different computation schedule even with deterministic
kernels. Nondeterminism or a matched-schedule mismatch fails the gate; neither
is silently converted into an allclose pass.

Execution results:

- Existing unittest: 1 attempted, **ERROR** at `mlx.nn` import, before any model
  or logits, with `[metal::load_device] No Metal device available`.
- Selecting `mx.cpu` also fails at the same decorator import; disabling compile
  additionally does not help. These were preflight attempts, not CPU evidence.
- New driver: exit **1**, same Metal error at device preflight; peak process RSS
  **34,258,944 bytes** (32.67 MiB), before any tiny model. `mx.metal.is_available()`
  says True here and is insufficient as a usable-device test.

No sandbox escape, permission bypass or venv change was attempted. The native
model paths are source-audited but **not execution-validated** in this sandbox.

Reproduce in a Metal-visible session, without starting any production workload:

```sh
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  /private/tmp/jwsol/venv-mlx/bin/python -B scripts/align_cache_checkpoint_native.py
```

The driver uses 384 MiB MLX memory and 32 MiB allocator-cache guidelines, tiny
fixed dimensions and a 900 MiB process peak-RSS guard between evaluated stages.
MLX's memory setting is explicitly a **guideline**, not a hard RSS cap. Cases
are sequential. Production-config models are never instantiated.

## Item 2 — supplied-config sizing

Retained a byte-identical `.hf-next/config.json` copy at
`tests/align/fixtures/qwen3_next_config.json` (22,138 bytes), SHA-256
`f5a5422b8e3d47733f0073ff22dec1dc4a7832fec5fc1cf36eba31ace03cf0c4`.
User identifies the source as mlx-community; no upstream revision was verified
without network. Qwen3.8's supplied config still matches the earlier fixture
hash `8f80874ac3ad8fa386d3f6dc0ea85377f703376e009a03dee0360e08e289a25d`.

For Next: 36 recurrent / 12 full-attention layers, Hk=16, Hv=32, Dk=Dv=128,
convolution kernel=4. bf16 history + fp32 recurrence gives:

- Convolution: **49,152 B/layer**; recurrence: **2,097,152 B/layer**.
- Recurrent arrays: **77,266,944 B**; twelve logical u64 offsets: **96 B**.
- One checkpoint: **77,267,040 B = 73.6875916 MiB**.
- Two retained: **154,534,080 B = 147.3751831 MiB**.
- fp32 convolution sensitivity: **79,036,512 B/checkpoint**.

Updated the design's conditional Next row to supplied-config evidence and added
a fixture-backed regression. Qwen3.8 remains **153,944,192 B/checkpoint**,
**293.6252441 MiB/two**. These are payload estimates, not measured residency.
Neither weights' quantization nor config precision proves cache dtype; the
Metal-blocked native runtime dtype check remains outstanding.

## Item 3 — resource probe, attempt and extrapolation

Added `--benchmark` and MLX-free `--estimate-only` modes to the native driver.
The benchmark measures synchronous `_snapshot`/`_restore`, three warmups then
25 samples, with suffix mutation outside timing. It excludes duplicate snapshot
no-ops and reports operation-local active MLX memory, raw wall times, allocator
cache and process peak RSS. It never constructs a model from a real config.

Benchmark execution: **exit 1**, same Metal initialization error, before any
timed operation. Peak process RSS at failure was **36,634,624 B (34.94 MiB)**.
This is measured failed-preflight resource use, **not** tiny-model or copy cost.
No native wall time, allocated snapshot memory or timing extrapolation is
available. The long seven-worker job was not inspected or modified.

Config-only estimate mode: **PASS**, four family/dtype rows, timing fields null.
bf16-history projections (all state recurrence float32):

| Quantity | Next | Qwen3.8 / qwen3_5 |
|---|---:|---:|
| Tiny copied recurrent arrays | 26,880 B | 39,744 B |
| Real copied recurrent arrays | 77,266,944 B | 153,944,064 B |
| Real/tiny byte ratio | 2,874.5143 | 3,873.3913 |
| Three snapshot array sets during replacement | 231,800,832 B | 461,832,192 B |
| Four sets including active recurrence, conservative allowance | 309,067,776 B | 615,776,256 B |

Two-retained payload is listed under item 2. Three/four-set figures exclude
weights, KV, offsets, Python/allocator overhead and kernel workspace; they are
not RSS bounds. Real-layer counts are 12× and 16× the three-linear-layer tiny
models, so fixed object overhead also scales differently from array bytes.
Future timing output includes `tiny_median_ms × real_state_bytes / tiny_state_bytes`
as an explicit byte-proportional scenario, not a prediction or confidence bound.
Under the current blocker it correctly reports no timing numbers.

## Verification / remaining work

- `python3.13 -B -m py_compile scripts/align_cache_checkpoint_native.py`: PASS.
- `python3.13 -B -m unittest tests.align.test_cache_checkpoint`: 11 PASS (0.008 s).
- `PYTHONPATH=. python3.13 -B scripts/align_cache_checkpoint_native.py --estimate-only`:
  PASS, four config-only rows. Initial invocation without `PYTHONPATH=.` failed
  to resolve `joulewise`; the documented command above corrects the invocation.
- Supplied interpreter, same driver with `--benchmark`: exit 1, Metal blocked.
- `git diff --check`: PASS.
- Native commands above: blocked/error, not passed or skipped numerical gates.

Item 4 (suite integration) follows in a separate commit. Metal-visible execution is required
before any numerical exactness, measured native cost or production claim.
