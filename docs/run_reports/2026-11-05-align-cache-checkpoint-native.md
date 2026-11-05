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

## Item 4 — suite integration and final review

Replaced the original optional one-family test with four native tests covering
both installed model families and both dtypes. Each runs aligned and partial
boundaries and all three rewrites through the same gate as the executable.
Missing native packages skip; installed-but-unusable Metal fails class setup.
Added three stdlib probe tests for real-config routing, memory projections with
no unmeasured times, and an estimate-only CLI guarded against any MLX import.
Updated the design document to the current gate; removed obsolete unavailable-
dependency wording and prospective, unmeasured allclose tolerances.

Final diff review: eight paths changed across the four items:

- `scripts/align_cache_checkpoint_native.py`: reusable native gate and benchmark.
- `tests/align/test_cache_checkpoint_native.py`: optional native suite integration.
- `tests/align/test_cache_checkpoint_probe.py`: offline probe/config checks.
- `tests/align/test_cache_checkpoint.py`: supplied Next sizing regression.
- `tests/align/fixtures/qwen3_next_config.json`: byte-identical supplied config.
- `joulewise/align/apple/prompt_cache.py`: shape docstring correction only.
- `docs/align/hybrid_cache_checkpoints.md`: current design/evidence limitations.
- This report: coordination handoff and execution evidence.

One local commit per brief item; none pushed:

1. `fd3cd207b` — two-family native gate and Metal blocker.
2. `58a436a13` — Next supplied-config payload calculation.
3. `fdb3ddf03` — resource probe and explicit payload projections.
4. `ALIGN: integrate optional two-family native checkpoint tests` — this final
   suite-integration/report commit; its hash is in the final handoff.

## Verification

Modules were run individually; no full-suite discovery, pipeline or real-data
replay. Final successful selection: **14 tests passed** with the supplied
interpreter (11 mechanics + 3 probe). The four numerical tests did **not** run:
class setup failed before a model was created. The bare interpreter separately
confirmed the missing-dependency skip behavior. Test execution was well below
the 20-minute budget (selected tests and failed preflights total seconds).

For the commands below, `$MLXPY` denotes exactly
`/private/tmp/jwsol/venv-mlx/bin/python`, not a changed venv. Native commands
also set `PYTHONDONTWRITEBYTECODE=1`, `HF_HUB_OFFLINE=1`,
`TRANSFORMERS_OFFLINE=1`, and a scratch `HF_HOME` under `/private/tmp`.

| Command | Final result |
|---|---|
| `PYTHONPATH=. $MLXPY -B -m unittest tests.align.test_cache_checkpoint` | 11 PASS, 0.011 s |
| `PYTHONPATH=. $MLXPY -B -m unittest tests.align.test_cache_checkpoint_probe` | 3 PASS, 0.122 s |
| `PYTHONPATH=. $MLXPY -B -m unittest tests.align.test_cache_checkpoint_native` | ERROR at class setup, 0 tests run, 0.146 s; Metal unavailable |
| `python3.13 -B -m unittest tests.align.test_cache_checkpoint_native` | 4 SKIP; packages absent in this interpreter |
| `PYTHONPATH=. python3.13 -B scripts/align_cache_checkpoint_native.py --estimate-only` | PASS; four config rows, timing null |
| `PYTHONPATH=. $MLXPY -B scripts/align_cache_checkpoint_native.py` | Exit 1; Metal preflight error, no logits |
| `PYTHONPATH=. $MLXPY -B scripts/align_cache_checkpoint_native.py --benchmark` | Exit 1; Metal preflight error, no copy samples |
| `python3.13 -B -m compileall -q joulewise tests scripts/align_cache_checkpoint_native.py` | PASS |
| `git diff --check` | PASS after removing an extra doc EOF blank line |
| `git diff --exit-code 46eaf3b79 -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json tests/test_gen_state.py` | PASS; no protected path changes |

Earlier authoring checks (not additional native evidence):

- `python3.13 -B -m py_compile scripts/align_cache_checkpoint_native.py`: PASS.
- `python3.13 -B -m unittest tests.align.test_cache_checkpoint`: 11 PASS (0.008 s).
- `PYTHONPATH=. python3.13 -B scripts/align_cache_checkpoint_native.py --estimate-only`:
  PASS, four config-only rows. Initial invocation without `PYTHONPATH=.` failed
  to resolve `joulewise`; the documented command above corrects the invocation.
- Supplied interpreter, same driver with `--benchmark`: exit 1, Metal blocked.
- `git diff --check`: PASS.
- Native commands above: blocked/error, not passed or skipped numerical gates.

## Open questions and next exact step

1. **Blocking environment:** why is a Metal device inaccessible to this session
   despite installed MLX? No device-permission bypass is authorized here. Run
   the exact pinned unittest command above from a permitted Metal-visible
   session, followed by the driver with `--benchmark`. Keep the tiny-model
   limits and sequential execution. Fix and rerun any constructor, numerical
   or resource failure; the native path has not yet been execution-validated.
2. **Unmeasured:** restored/full max abs error, kernel determinism, actual
   runtime cache dtype/shape, copy latency and model-loaded peak memory. None
   is inferred from config arithmetic or the failed preflight RSS.
3. **Scope of eventual evidence:** partial-boundary equality is checked against
   a full matched-schedule re-prefill. The one-shot diagnostic cannot establish
   universal equality across schedules, and synthetic rewrites do not validate
   the production chat templates or production quantized weights.
4. **Provenance:** both configs are the user-provided clone-local bytes; upstream
   revision identity has not been independently authenticated without network.

Item 2 is complete and item 4 is integrated with skip/setup behavior checked.
Items 1 and 3 are implemented/attempted but remain **blocked**, rather than
claimed complete. Production readiness remains PROVISIONAL.
