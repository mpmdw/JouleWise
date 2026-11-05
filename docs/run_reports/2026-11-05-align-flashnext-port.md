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

## Stage 2

Added read-only mmap PLE storage (bf16/fp32, row-affine q4/q8), deduplicated
row gathering and gathered-row-only dequantization. Production-sized PLE
construction without an offload descriptor fails before allocating an
embedding. Disk tables stay outside `parameters()` and the MLX resident set.

`venv-ref/bin/python -B -m unittest tests.align.test_qwen4_exp_tables`:
3 tests PASS (0.178 s). Covers encoding/gathering, byte accounting, invalid
indices/file lengths, EOS segmentation and chunked hashing.

`venv-ref/bin/python -B scripts/align_benchmark_qwen4_ple.py --mib 128
--tokens 128`: PASS (1.44 s), synthetic warm file only. For a 134,217,728-byte
bf16 table: mmap peak RSS 38,617,088 → 70,270,976 bytes; eager worker
36,028,416 → 307,101,696 bytes (includes mapped pages AND eager copy).
Mmap median/p95 44.646/55.342 us per 16-row token; logical bytes/token 8,192;
unique 16-KiB page spans 29,327,360 bytes over 128 requests. Eager median
7.334 us. These are CPU warm-cache synthetic timings, not model tok/s, cold
disk bandwidth, GPU resident memory or whole-machine page-cache residency.
An initial `/bin/ps` RSS probe was sandbox-denied; replaced it with standard
`getrusage` high-water RSS. No permission bypass. `git diff --check` passed.

## Stage 3

Added streaming converter and shared quantization policy/shape inventory.
Mixed profile: routed experts q4, eligible other linears/embeddings q8;
indexer, DeltaNet, routers, convolutions and norms retain bf16. Narrow
low-rank projections that do not divide the group size retain bf16.
N-gram shards stream directly into the separate CPU table. The converter
copies both owned runtime files and tokenizer assets, hashes every payload
file, and writes its completion manifest last. The manifest cannot hash
itself; pin its SHA256 externally (the CLI prints it).

Tiny `transformers.save_pretrained` produced per-expert tensors rather than
the release's fused tensors. Added both layouts, plus nested official
prefixes and sharded PLE. Rejected missing indexer tensors before writing
output. Unquantized conversion requires no working MLX device.

`OMP_NUM_THREADS=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
venv-ref/bin/python -B -m unittest tests.align.test_qwen4_exp_conversion`:
3 tests PASS (6.106 s). Exact fp32/bf16 indexer retention, fused gate split,
per-expert stacking, official prefixes, PLE shards, intentional MTP/vision
omission, manifest tamper detection, and mixed-policy decisions. Initial
failures exposed the saved per-expert layout and tiny rank/group mismatch;
both fixed. Quantized tensor conversion is **PENDING MLX device access**.
`git diff --check` passed. No full suite run, per the explicit machine-load
restriction.

## Stage 4

Added `test_qwen4_exp_parity.py`, a split-interpreter gold gate. The official
194,564-parameter random fixture includes both attention types, QSA budget
overflow, PLE/EOS hashing, nonzero PLE convolution and nonzero norm weights.
It saves through Transformers, converts, then uses the pinned `load_model`
custom-module seam. FP32 acceptance: atol 2e-5 / rtol 2e-4; bf16: atol .004 /
rtol .02. Mixed quantization: atol .04 / rtol .15 plus RMSE <= .012. These
are prospective gates, not measured MLX error bounds.

The MLX worker checks HF prefill/stepwise parity, MLX prefill/stepwise/chunks,
sparse causality, two-row left padding and cached continuation, native disk
snapshot/restore (all recurrent/PLE states), attention-only prefix trim and
re-prefill, QSA-cache quantization refusal and absence of GPU PLE parameters.
The worker must actually run before any of those claims can be made.

Because the provided MLX venv has no Torch, replaced the converter's Torch
reader with a bounded NumPy safetensors reader that preserves bf16 bits.
Conversion tests rerun: 3 PASS (6.938 s).

`JW_QWEN_REF_PYTHON=/private/tmp/jwsol/venv-ref/bin/python
JW_QWEN_MLX_PYTHON=/private/tmp/jwsol/venv-mlx/bin/python
venv-ref/bin/python -B -m unittest tests.align.test_qwen4_exp_parity`:
5 tests in 8.044 s, **2 reference tests PASS / 3 MLX tests SKIPPED** due to
the unavailable Metal device. Official HF prefill vs stepwise max abs error:
fp32 7.450580596923828e-08; bf16 0.0, on [1,11,64] logits. These numbers
are HF self-consistency only. Cross-backend parity, MLX cache correctness and
quantized conversion remain **UNVERIFIED, RELEASE BLOCKING**.

## Stage 5

Added backend-free component memory accounting and a tracked text-config
fixture, so CI does not depend on ignored `.engine` sources. The kit cap is
confirmed as 40,960. Mixed weights estimate 75,239,294,720 bytes; persistent
state 1,248,595,976 bytes. Chunk 256 plus a 3 GB runtime reserve exceeded
the strict 80 GB planning target (80,759,813,384); chunk 64 estimates
79,876,650,248. Converted runtime config now refuses larger chunks and
contexts; generation must explicitly use `prefill_step_size=64`.

The design doc includes per-component 8/6/4/3/mixed tables and physical
file-cache caveats. q4 PLE disk bytes 28,160,135,168; illustrative page-cache
estimate 8.93 GB, conservative page-span bound 21.47 GB. Mixed combined
physical upper estimate 101.35 GB before OS/process headroom. These are
accounting estimates, not measured peaks or a guarantee against swap.

`python3 -B -m unittest tests.align.test_qwen4_exp_memory`: 2 PASS (0.012 s).
Initial budget assertion caught chunk 256 exceeding target; fixed by using
and enforcing chunk 64, without reducing the explicit runtime reserve.
`git diff --check` passed. Full-model memory, allocator reserve adequacy,
file-cache behavior, and swap absence remain target-Mac gates.
