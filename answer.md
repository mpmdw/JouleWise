# Canonical gold adapter handoff — 2026-11-05

Implemented on `lane/2026-11-05-qwen4exp-gold-adapter`, based on
`a6f9df9b3b31344e19ebcc819bd409945091f0a4`. Implementation commit:
`e42910830` (`feat(align): add gold/v1 adapter for the canonical qwen4_exp port`).
The companion commit (`test(align): normalize fixture paths and record gold adapter handoff`)
records this report and normalizes temporary fixture paths for macOS aliases.
Nothing was pushed or merged.

The adapter covers embeddings and stream replication, both decoder types and
their MoE, sparse PLE at zero-based layer 1, the final mixer/norm, and chunked
vocabulary projection. It calls the canonical forward methods, including their
bf16 RoPE, fp32 router ranking and DeltaNet eps adapter. Routed storage dispatch
calls the canonical `FusedSwitchGLU` with one expert resident at a time.

`--adapter-dependency` must declare **both** `qwen4_exp.py` and
`canonical_converter.py` (or `align_convert_qwen4_exp.py`). The coordinator now
passes their absolute paths/digests to workers and records them explicitly in
`provenance.json`. The adapter imports the verified file bytes using importlib
module specs, checks the converter's module/stack pins, reuses `sources()` and
`target_shape()`, and records both source SHA256s in worker metadata. The module
pin is `f4ec75d16f0af0517b63e202abeef704c9a775e9111949ab003250d51d982c37`.
There is no package-tree model import or copied model math.

Files touched:

- `joulewise/align/qwen4_gold/canonical_adapter.py` — new adapter.
- `joulewise/align/qwen4_gold/runner.py` — dependency request/provenance plumbing.
- `tests/test_qwen4_gold_canonical_adapter.py` — CPU checks and three native tests.
- `tests/test_qwen4_gold_stream.py` — require `mlx.core` and explicit native opt-in for sparse-gather testing.
- `docs/align/qwen4_exp_port/gold_parity.md` — exact adapter and native commands.
- `answer.md` and `docs/run_reports/2026-11-05-qwen4exp-gold-adapter.md` — handoff.

## What ran here

Each unittest module ran separately, with no full-suite invocation. For the
first three commands the environment was:

```bash
export PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
```

| Command | Final result |
|---|---|
| `/private/tmp/jwsol/venv-both/bin/python -B -m unittest -v tests.test_qwen4_gold_canonical_adapter` | 10 tests, 7 passed, 3 native tests skipped; 6.001 s |
| `/private/tmp/jwsol/venv-both/bin/python -B -m unittest -v tests.test_qwen4_gold_parity` | 20 passed; 0.800 s |
| `/private/tmp/jwsol/venv-both/bin/python -B -m unittest -v tests.test_qwen4_gold_stream` | 20 tests, 18 passed, 2 native tests skipped; 123.016 s |
| `python3.13 -B -m unittest -v tests.test_qwen4_gold_canonical_adapter` | Bare interpreter: 3 passed, 7 optional/native tests skipped |
| `python3.13 -m compileall -q joulewise tests` | Passed |
| `git diff --check` / `git diff --cached --check` | Passed |

CPU checks covered every official tiny-index name, canonical parameter paths,
packed/unpacked expert shapes, ignoring unrelated shards, checkpoint I64 hash
buffers in both hash paths, dependency mutation rejection, and provenance/request
digests. The existing streaming chain/oracle test uses a trace-copy candidate;
its result is harness evidence, not MLX parity.

Earlier checks found a missing constant in the test's host-only AST extraction
(fixed) and an existing sparse native test that attempted Metal in the sandbox
(failed with `No Metal device available`; fixed the opt-in gate and reran the
module successfully). Including those attempts, test time remained under five
minutes. No commands targeted real measurement inputs, the block-5 pipeline,
network access, or user data paths outside the authorized clone/shared Git
objects. Coordination-state files were preserved as instructed.

## Exact native commands — next step for the lead

Run from this clone in a native Metal session, with the pinned Transformers
5.22.1, MLX 0.31.2 and mlx-lm 0.31.3 stack. These commands use only synthetic
checkpoints and local shard serving; neither downloads weights.

```bash
GOLD_ADAPTER="$PWD/joulewise/align/qwen4_gold/canonical_adapter.py"
GOLD_CANONICAL=/private/tmp/jw-gold-canonical-65763077
mkdir -p "$GOLD_CANONICAL"
git show 65763077aec03235d149517f6c97a7cda987a74c:joulewise/align/models/qwen4_exp.py > "$GOLD_CANONICAL/qwen4_exp.py"
git show 65763077aec03235d149517f6c97a7cda987a74c:scripts/align_convert_qwen4_exp.py > "$GOLD_CANONICAL/canonical_converter.py"

JW_GOLD_CANONICAL_MODULE="$GOLD_CANONICAL/qwen4_exp.py" \
JW_GOLD_CANONICAL_CONVERTER="$GOLD_CANONICAL/canonical_converter.py" \
PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 \
/private/tmp/jwsol/venv-both/bin/python -B -m unittest -v tests.test_qwen4_gold_canonical_adapter

JW_GOLD_CANONICAL_MODULE="$GOLD_CANONICAL/qwen4_exp.py" \
JW_GOLD_CANONICAL_CONVERTER="$GOLD_CANONICAL/canonical_converter.py" \
PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 \
/private/tmp/jwsol/venv-both/bin/python -B -m unittest -v tests.test_qwen4_gold_stream
```

The new native tests assert PASS for every required trace of all seven tiny
units, fp32/bf16 and real/random inputs, through actual `--make-tiny` parity
workers. The third test runs the streaming driver with sparse PLE, restaging,
and completed-run resume. The run plan supplies both source files as repeatable
`--adapter-dependency` arguments for subsequent lead-controlled runs.
All three native tests must actually execute; a skipped run does not satisfy
the native gate. Python 3.11 was not exercised in this sandbox.

## Risks and open questions

- **Native numerical parity is unverified.** All three new MLX tests skipped
  here. MLX/Metal execution and the one-expert storage dispatch still need the
  native command above; no real-weight or MLX PASS is claimed.
- Canonical router/QSA tie rules can differ from Torch's unspecified tied
  `topk` order. The existing exact-set/mask gates remain unchanged and fail
  closed. No tolerance or reference-semantic adjustment was made.
- Backend reduction/rounding, especially bf16 attention and expert dispatch,
  must satisfy the existing gates natively; CPU mapping tests cannot establish
  this. Real-scale peak memory and elapsed time are unmeasured.
- The adapter selects the canonical prefill mask path to export `qsa.mask`;
  performance dispatch and decode/cache parity are outside this harness's scope.
- No new ruling was needed for implementation. The streaming plan's existing
  lead-owned shared-shard ruling remains a prerequisite to a real laptop run.
