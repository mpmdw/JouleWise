# Qwen4 experimental gold streaming driver — 2026-11-05

Branch: `lane/2026-11-05-qwen4exp-gold-stream`.
Base: `f48da184b63de7eca7f6158a02ef8e5b6de1c3de` (checked-out PR #667 head).
Implementation: `78fe672a1` (`feat(align): add resumable qwen4 gold shard streaming driver`).
This report and [answer.md](../../answer.md) are included in a following local
handoff commit. No push, merge, deployment or external message was performed.

## Intake and scope

Read AGENTS/CLAUDE, Mission M0, restart/queue/stop-card sections, the plan map,
orchestration and targeted D-050/D-064 authority. No active stop card applied.
This is agent-compatible model correctness tooling, not a quiet-machine task.
The direct brief owns this work; per its explicit exception, RUN_STATE.md,
TASK_QUEUE.md, docs/process/state_kernel.json and tests/test_gen_state.py were
preserved, and no task was registered. No subagents or bridge consults were used.

The clone started clean and detached at the requested base; the named branch
was created before edits. Only this clone, allowed Git objects, permitted
temporary environments and the explicitly supplied checkpoint **config/index**
were inspected. No measurement tensors, real restricted directories, study
pipeline or analysis output were read. No network commands were run. The
requested canonical ref was already available at
`65763077aec03235d149517f6c97a7cda987a74c`; it was inspected through Git and
temporary source copies instead of fetching under the no-network rule. It was
not merged or copied into tracked port code.

## Implementation and changed files

| File | Change |
|---|---|
| `scripts/run_qwen4_gold_stream.py` | CLI entry point |
| `joulewise/align/qwen4_gold/stream.py` | HF pins/metadata, disk planning, shard lifecycle, strict retention and explicit restaging policies, durable unit-major coordinator |
| `joulewise/align/qwen4_gold/stream_ple.py` | Official hash planning, raw row/subset copying, sparse Torch/MLX checkpoint shim |
| `joulewise/align/qwen4_gold/stream_convert.py` | Optional canonical per-unit maxfit conversion and full PLE export with restart progress |
| `joulewise/align/qwen4_gold/runner.py` | Work-local offline worker cache, mlx-lm runtime identity, stream request extension |
| `joulewise/align/qwen4_gold/worker.py` | Sparse checkpoint, official PLE-planning and conversion backends |
| `tests/test_qwen4_gold_stream.py` | Twenty offline fixture/reference/native-gated tests |
| `docs/align/qwen4_exp_port/gold_parity.md` | Laptop commands, bounds, timing method and item-5 acceptance |
| `answer.md`, this report | Handoff and outstanding ruling |

The real chain reuses existing per-case reference output files. Each output
contains the flattened residual streams; separate fp32/bf16 chains are recorded
in the stream manifest. Each unit runs all prompts and both real/random modes
before source retirement. A failed component prevents unit completion.

HF config/index are authenticated by Git blob identity; shard digests must be
the pinned revision's LFS SHA256. Partial files count toward disk usage and only
their remaining bytes are reserved. Resume rehashes source files on first use
per invocation, validates derived views and completed evidence, and recovers
interruptions before/after row/subset manifest commits. All caches are local to
work and Xet is disabled. No fixture result is promoted to native validation.

## Required ruling and disk evidence

**NEEDS_RULING:** authorize `--shared-shards restage` for the laptop, or provide
a larger disk while retaining originals.

The default `retain` policy implements the brief literally. The official
checkpoint's alphabetical layer serialization creates distant shared-shard
users, including layers 2/19, 3/29, 4/39 and 5/47. A meta-only official model
constructed from the allowed config, mapped through the allowed index, gives
**25,887,936,256 payload bytes = 24.110 GiB at layer 8**. This excludes all 31
MTP keys absent from the official runtime and safetensors headers, so it is a
lower bound. No real weights were opened for this calculation. Keeping that
amount plus a 25 GiB reserve is incompatible with approximately 40 GB free.
The driver refuses an impossible strict-retention plan before shard downloads.

The recommended opt-in policy authenticates each full source, copies only the
current unit's exact bytes into a separately hashed local view, retires the
original, and re-downloads shared sources for later units. Its raw copy and
restart behavior are fixture-tested. Real staging is estimated near 9 GiB,
plus roughly 3 GiB evidence for the built-in short prompts, but has not been
measured. The staging guard remains 12 GiB. Planning totals are about 360 GB
with retention and about 460 GB with restaging; exact values come from pinned
live HF sizes in `manifest.json`. All 131 physical shards contain text weights;
333 vision and 31 MTP tensors are skipped computationally, without avoiding
their shared physical files.

## Verification

Numerical commands used:

```bash
PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 \
/private/tmp/jwsol/venv-ref/bin/python -B -m unittest tests.test_qwen4_gold_stream

PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 \
/private/tmp/jwsol/venv-ref/bin/python -B -m unittest tests.test_qwen4_gold_parity

PYTHONNOUSERSITE=1 python3.13 -B -m unittest tests.test_qwen4_gold_stream

PYTHONPYCACHEPREFIX=/private/tmp/jw-gold-stream-pycache \
python3.13 -m compileall -q joulewise/align/qwen4_gold \
  scripts/run_qwen4_gold_stream.py tests/test_qwen4_gold_stream.py \
  tests/test_qwen4_gold_parity.py
```

Final streamed module: **20 tests, OK, 2 native-only skips, 57.667 seconds**.
Existing parity module: **20 tests, OK, 0.693 seconds**.
Bare Python: **20 tests, OK, 17 optional-dependency skips**.
Compile, CLI help and diff whitespace checks passed. No full-suite invocation
was made; cumulative targeted unittest time was approximately nine minutes,
within the brief's 20-minute limit while the other analysis job was running.

The end-to-end test uses official save_pretrained tiny weights split into fake
shards, real CPU reference workers, both dtypes and modes, an interrupted case,
and a separate bounded full-tiny-model oracle. All layers/endpoints pass the
existing tolerances, and every real input snapshot equals the persisted
reference predecessor. Candidate traces are copied by an explicit test double;
this is not MLX parity. Sparse table values and independent official tiny PLE
forwards agree exactly; out-of-store ids raise. Complete PLE export reproduces
all rows, discards only uncommitted append bytes on resume, and handles multiple
partitions sharing one physical source without duplicate phase downloads.

One initial fixture test expected a shared buffer/table source to be deleted
early. The fixture grouped pre-sharded official tiny tables incorrectly; it
was corrected to explicit fake shard groups and subsequent runs passed. Final
review added regressions for kills after subset rename and after manifest
commit, before original deletion. None of these tests read real study inputs.

Local final test output is in `/private/tmp/jw-gold-stream-acceptance.log`;
temporary unittest checkpoint/results directories were synthetic and are
removed by their test harnesses. These logs are diagnostics, not committed
native evidence.

## Native gates and exact next step

Native commands, source pins and full CLI flags are in [answer.md](../../answer.md)
and the [run plan](../align/qwen4_exp_port/gold_parity.md#streaming-laptop-run-plan-2026-11-05).
The native combined venv must run:

- `OfficialTinyPLETests.test_native_mlx_sparse_gather`.
- `NativeConversionTests.test_maxfit_uses_canonical_quantization_and_resumes_per_tensor`.
- The full targeted streaming module with explicit canonical paths, then the
  real run with a lead-verified gold/v1 canonical adapter.

No native MLX or real-weight run was possible here. Live HF behavior, real
disk/RSS/Metal peaks and timing remain unverified. Conversion emits unit
fragments, not a loadable assembled model; full bf16 PLE output alone is about
102 GB and full maxfit output about 210 GB. A Dropbox folder on this SSD does
not create that capacity. No cloud API or eviction is implemented. Full-model
assembly and canonical load verification remain later work.

GOAL item 5 remains **PROVISIONAL / not established** until all 51 native units
pass both dtypes and modes with authenticated real weights, unchanged trace
gates and a real adapter. Short prompts do not establish long QSA pruning,
decode/cache behavior, quality or item 11's distinct full-checkpoint Mac gate.
Lead action: rule on restaging, run the native tests, provide/verify the adapter,
inspect metadata preflight, then start the same-command resumable real run.
