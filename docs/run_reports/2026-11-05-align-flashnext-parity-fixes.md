# Flash-Next parity fixes

Authority: Ed's 2026-11-05 brief, on the already checked-out named branch
`lane/2026-11-05-align-flashnext-port`, base `18e9325a9`. M0: no active stop
card; targeted restart, queue, manual holds, playbook, AGENTS/CLAUDE and D-009
read; clean initial worktree. This explicit bounded request overrides queue
selection and the usual coordination writes. RUN_STATE, TASK_QUEUE, state
kernel and test_gen_state remain untouched. No network, measurements, real
restricted paths, real checkpoints, full suite or external agents used.

The requested `git show
origin/lane/2026-11-05-align-flashnext-realparity:docs/align/qwen4_exp_real_layer_parity_L2_L3.md`
failed: that ref is absent locally. Only the port ref is available. A commit
SHA was requested for a possible offline object-store read. Implementation
therefore uses the explicit findings in the brief and the official reference
source in the existing `/private/tmp/jwsol/venv-ref` environment; no real-weight
parity results are claimed or reconstructed.

## Item 1: deterministic QSA

`qsa_topk` now selects/emits complete blocks in exact score-descending,
block-index-ascending order. A cutoff count detects straddling ties without
floating-point perturbation. The unique-cut path retains argpartition and
sorts K entries; any straddling row uses full stable argsort. MLX's installed
API stub documents argsort stability. Cost: O(N + K log K) versus O(N log N)
fallback, plus one boolean host synchronization. Masked -inf ties also count;
early prefill rows can force a full-batch fallback. Native timing is pending.

Added native synthetic selection tests for many exact zeros, positive ties,
masked entries, nearby distinct scores, unique-cut fast-path use and repeated
25-token prefill/chunk/step selection. Added a split-interpreter parity
variant with zero QSA projections: actual MLX selection is exported to JSON,
then the official reference's Tensor.topk and torch.topk indices are forced
to that order in QSA alone. Compares prefill/chunk/step logits with existing
fp32 tolerances, retaining unmodified routing and ordinary parity tests.

CPU replay validates the test plumbing, not MLX parity. Torch 2.15.0's default
zero-tie order happens to match ascending indices on this small CPU fixture,
so a first assertion expecting default-vs-forced differences failed. Corrected
the test to compare an explicitly different admissible tied subset instead:
max logit difference **0.06364019215106964**. This makes the fixture
discriminating without depending on a particular Torch tie implementation.

Verification (serial, optional native stack absent in selected interpreter):

- `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
  /private/tmp/jwsol/venv-ref/bin/python -B -m unittest
  tests.align.test_qwen4_exp_qsa`: **2 PASS, 3 MLX SKIP**, 4.427 s.
- `JW_QWEN_REF_PYTHON=/private/tmp/jwsol/venv-ref/bin/python
  JW_QWEN_MLX_PYTHON=/private/tmp/jwsol/venv-ref/bin/python
  /private/tmp/jwsol/venv-ref/bin/python -B -m unittest
  tests.align.test_qwen4_exp_parity`: **2 PASS, 6 MLX SKIP**, 16.079 s.
- `python3.13 -m compileall -q` on the model and the three changed/new test
  modules: PASS. `git diff --check`: PASS.

Files for item 1: `joulewise/align/models/qwen4_exp.py`,
`tests/align/qwen4_exp_reference.py`, `tests/align/test_qwen4_exp_parity.py`,
new `tests/align/test_qwen4_exp_qsa.py`, `docs/align/qwen4_exp_port.md`, this
report. First commit contains item 1 only; commit IDs appear in the final
handoff / local Git log.

Native lead gate: run `tests.align.test_qwen4_exp_qsa.TestNativeQSA` in the
pinned native MLX environment and `tests.align.test_qwen4_exp_parity` with the
documented split interpreters, serially, with zero native skips. Cross-backend agreement,
all native cache behaviors and stable-selection latency remain UNVERIFIED.

## Item 2: optional bf16 promotion

Item 1 commit: `efae852c1`. Item 2 adds the boolean config flag
`jw_bf16_fp32_ops`, default **true** for both direct construction and config
loading, with a flat/outer override over nested text config. The converter
validates and explicitly persists it; source false remains false. Existing
artifacts default on when loaded with this new runtime. Rebuild and re-pin
artifacts rather than mutating an already verified artifact.

Only bf16 hyper-stream means and sigmoid evaluation promote to fp32 and cast
back afterward. Covers hyper mixing/injection, attention, shared-expert and
PLE gates, plus DeltaNet beta. GatedNorm was already fp32. The optional beta
path uses pinned mlx-lm 0.31.3's existing compute_g / ops / kernel dispatch
with the rounded promoted sigmoid; the disabled and non-bf16 cases call the
original gated_delta_update. No external library was edited. SiLU, products,
projections and other dtypes preserve their previous operations; fp32 gets
no new arithmetic or casts from this flag.

Expected gain, **not measured here**: if the affected operations' reported
1.2–1.6× Torch error reduces to Torch-like error on matched bf16 inputs,
relative error reduction would be `1 - 1/1.2` to `1 - 1/1.6`, approximately
**17–38%**. This is an operation-level expectation, not a layer/logit bound.
BF16 output rounding, unchanged SiLU and matmul error remain. Actual accuracy,
transient fp32 workspace and performance need native measurements; no result
from real weights or the missing PR report is inferred.

Six native tests cover config precedence/validation, bf16 sigmoid and
four-stream mean RMSE against matched-input fp64 oracles, exact output dtype,
the disabled original hyper graph, both beta dispatch paths with masking and
state, bitwise fp32 flag equivalence across all three inference modes and
bf16 mode parity with either flag. These tests are written normally and
gated on MLX importability. They were **not executed natively** here.

Item 2 files: `joulewise/align/models/qwen4_exp.py`,
`scripts/align_convert_qwen4_exp.py`, `tests/align/test_qwen4_exp_conversion.py`,
new `tests/align/test_qwen4_exp_precision.py`, `docs/align/qwen4_exp_port.md`,
this report.

Verification (serial):

- `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
  /private/tmp/jwsol/venv-ref/bin/python -B -m unittest
  tests.align.test_qwen4_exp_conversion`: **6 PASS**, 7.519 s, including
  persisted default-on and explicit-off config plus existing manifest,
  tensor inventory and exact weight checks.
- `/private/tmp/jwsol/venv-ref/bin/python -B -m unittest
  tests.align.test_qwen4_exp_precision`: **6 MLX SKIP**, 0.000 s.
- `python3.13 -m compileall -q joulewise/align/models/qwen4_exp.py
  scripts/align_convert_qwen4_exp.py tests/align/test_qwen4_exp_conversion.py
  tests/align/test_qwen4_exp_precision.py`: PASS.
- `git diff --check`: PASS. Diff against `18e9325a9` for all four protected
  coordination/test paths: empty. Full suite deliberately not run because
  of the explicit machine load restriction. No MLX numerical pass is claimed.

Next exact step: outside this sandbox, serially run
`tests.align.test_qwen4_exp_qsa.TestNativeQSA` (3 tests) and
`tests.align.test_qwen4_exp_precision` (6 tests) in the pinned native MLX
interpreter, and the expanded `tests.align.test_qwen4_exp_parity` (8 tests)
with both split interpreters. Require zero native skips and retain the
single-op RMSE and reference replay metrics. Then the lead repeats the
real-layer comparison, measures selection/cast costs and adjudicates native
failures. The unavailable real-parity report, native bitwise compatibility,
actual bf16 gain and native performance remain explicit open items.
