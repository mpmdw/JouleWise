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

## Verification / remaining work

- `python3.13 -B -m py_compile scripts/align_cache_checkpoint_native.py`: PASS.
- `git diff --check`: PASS.
- Native commands above: blocked/error, not passed or skipped numerical gates.

Item 2 (config sizing), item 3 (resource probe/extrapolation), and item 4 (suite
integration) follow in separate commits. Metal-visible execution is required
before any numerical exactness, measured native cost or production claim.
