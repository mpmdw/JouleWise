# Flash-Next owned MLX port — implementation record

Task authority: Ed's 2026-11-05 brief in this session. Base `c9a0a3943`
(`origin/lane/2026-11-05-align-pilot9-benign`); branch
`lane/2026-11-05-align-flashnext-port`. The explicit brief overrides normal
queue selection and coordination bookkeeping. RUN_STATE, TASK_QUEUE, the state
kernel and test_gen_state are lead-owned and untouched. M0: no active stop
card, clean detached checkout matching base, targeted restart/queue/authority
read. D-009 optional backend rule applies. No measurements, restricted paths,
network, pin changes, external agents or real checkpoint data are involved.

## Stage 1

Added the owned text architecture, native-cache subclasses, HF name mapping,
CPU int64 n-gram hashing and configuration validation. Official reference is
authoritative; text CausalLM has no MTP dependency. Norms preserve raw HF
zero-centered weights and compute `1 + w` in fp32. This avoids ambiguous
folding and supports idempotent sanitization. QSA gathers selected KV per
query, retains raw keys, and fails closed on cache quantization/automatic
BatchGenerator merge. Explicit initial left-padded batches are supported.

Static check: Python 3.13 `py_compile` on both new modules and `git diff
--check` passed. Numerical validation is **PENDING**, not inferred from
compilation. Pinned MLX imports report 0.31.2 / mlx-lm 0.31.3, but allocating
an array fails with `[metal::load_device] No Metal device available`, including
after `mx.set_default_device(mx.cpu)`. The sandbox offers no approval route;
no bypass attempted. Torch 2.15.0 / transformers 5.22.1 import successfully.
Do not deploy this model until the gold tests pass on a device-capable Mac.
