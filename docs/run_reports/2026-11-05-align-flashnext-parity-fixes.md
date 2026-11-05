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
