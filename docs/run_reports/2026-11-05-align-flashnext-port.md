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

## Stage 6 / final handoff

Completed the design/deviation/source derivation document and target-Mac
admission plan. Added externally pinned manifest verification before custom
module execution, stack checks, bytecode suppression, and the top-level
40,960 position limit read by the existing endpoint. Indexer/trim derivation
comments cite the peer lines and authoritative official rules. No peer code
was imported or executed. No independent fresh review was available/run;
that remains a lead-owned pre-release obligation.

Extended the bounded synthetic benchmark to q4 at the actual 160-element
row width. Command: `/private/tmp/jwsol/venv-ref/bin/python -B
scripts/align_benchmark_qwen4_ple.py --mib 32 --tokens 128 --storage q4
--dim 160`. PASS, 1.16 s. 33,554,400-byte file; mmap peak RSS
38,600,704 → 62,390,272 bytes vs eager 37,961,728 → 105,168,896 bytes.
Identical decoder/checksum: mmap median/p95 68.1255/161.7984 us, eager
38.896/51.0813 us, logical bytes/token 1,408. Unique 16-KiB page span
21,004,288 bytes. Warm file only; no claim of cold physical read latency.

Final serial checks (`REF=/private/tmp/jwsol/venv-ref/bin/python`):

| Command | Result |
|---|---|
| `$REF -B -m unittest tests.align.test_qwen4_exp_tables` | 3 PASS, 0.159 s |
| `OMP_NUM_THREADS=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 $REF -B -m unittest tests.align.test_qwen4_exp_conversion` | 3 PASS, 5.861 s |
| `python3 -B -m unittest tests.align.test_qwen4_exp_memory` | 2 PASS, 0.012 s |
| `JW_QWEN_REF_PYTHON=$REF JW_QWEN_MLX_PYTHON=/private/tmp/jwsol/venv-mlx/bin/python $REF -B -m unittest tests.align.test_qwen4_exp_parity` | 2 PASS / 3 SKIP, 12.312 s |
| `python3 -B -m unittest tests.align.test_pilot3_cache` | 12 PASS, 1.490 s; synthetic existing integration regression only |
| `python3 -m compileall -q` on the new model directory, two scripts, reference helper and four new test modules | PASS |
| `git diff --check` | PASS |

A separate `resource.getrusage`-instrumented conversion-module run passed
all 3 tests (5.109 s), peak process RSS **339,230,720 bytes**, well under the
2 GB safety bound. No full suite or live job was started. New tests total
10 passing / 3 skipped; with existing cache regression: 22 passing / 3
skipped. Explicitly skipped MLX numerical gates are not passing evidence.

Files touched (14):

- `joulewise/align/models/__init__.py`
- `joulewise/align/models/qwen4_exp.py`
- `joulewise/align/models/qwen4_exp_tables.py`
- `joulewise/align/models/qwen4_exp_memory.py`
- `scripts/align_convert_qwen4_exp.py`
- `scripts/align_benchmark_qwen4_ple.py`
- `tests/align/fixtures/qwen4_exp_text_config.json`
- `tests/align/qwen4_exp_reference.py`
- `tests/align/test_qwen4_exp_tables.py`
- `tests/align/test_qwen4_exp_conversion.py`
- `tests/align/test_qwen4_exp_parity.py`
- `tests/align/test_qwen4_exp_memory.py`
- `docs/align/qwen4_exp_port.md`
- this run report

Final runtime source SHA256:
`qwen4_exp.py`: `4f3163af0d2dd143d200cc0e69088d84225ccb9c6442708c1a5f36c41dae7ac6`;
`qwen4_exp_tables.py`: `256465fdee44f039371b01541f15776e8db2274f1aa888eae7bca9ae1a7b83c6`.

Stage commits: `9145fd4ce` architecture; `6c6c44af0` mmap;
`3f80d5531` conversion; `6599011fe` gold tests; `fa1a417e5` memory;
stage 6 is the commit containing this final handoff. Local only; no push.
Coordination paths are unchanged against the base; anchor stack pins and
runtime code are unchanged.

**Next exact step:** run the documented split-venv parity command on a
device-capable Mac; require five passes and zero skips, inspect every worker
metric and fix any failures before real conversion. Then obtain a fresh
review. Resolve the immutable HF revision, model-specific warmup/stream
prefill option wiring, real-reference NLL acceptance and reference-host/
offload strategy before admission. Real-model coherence/NLL, runtime cache
correctness, q4 conversion, actual memory reserve/peak, page-cache pressure,
no-swap operation and tok/s remain OPEN. The implementation is reviewable
but is **not yet demonstrated to run correctly on the pinned MLX stack**.
