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
