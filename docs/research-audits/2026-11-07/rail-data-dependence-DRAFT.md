# Synthetic operand ladder — operator draft

PROVISIONAL desk tooling for the [interp × energy design](interp-weight-edit-energy.md),
§4 block P, and [its checks](interp-weight-edit-energy-checks.md), §10.
No measurement, registered estimator, resolution claim, or hardware validation.
The lead must review native behavior and approve a quiet-Mac lane before use.

From the repository root, safe desk paths are:

```sh
python3 -B scripts/interp_energy/rail_data_dependence.py --plan-only --out tmp/rail-plan
python3 -B scripts/interp_energy/rail_data_dependence.py --dry --out tmp/rail-dry
```

Each output directory must be new. Plan-only needs only the stdlib. Dry needs
NumPy and writes only `plan.json` and `timings.jsonl`: tiny float32 CPU
contractions, including for blocks whose *planned* dtype is bf16/int4/int8.
Dry exercises scheduling and timing serialization, **not** MLX, quantization,
Metal, energy collection, or the target dtype's performance.

The native command below is for a separate, lead-controlled session after
agents are stopped. **Do not execute it during desk/agent work.**

```sh
python3 -B scripts/interp_energy/rail_data_dependence.py --execute \
  --quiet-mac-confirmed --powermetrics --km003c --out tmp/rail-native
```

The flag records operator acknowledgement, not a mechanical quiet predicate.
Existing machine admission, hardware setup, permissions and the study's
priority order still belong to the lead. This tool changes no machine state
or background jobs. It launches only the explicitly selected collectors.
No inputs, model files, weights, or measurement corpora are read.

The default plan uses 2,048³ GEMM and M=1, N=K=4,096 GEMV. It allocates a
ring of at least 1 GiB of distinct weight buffers **per condition** for GEMV,
including packed codes and affine metadata for quantized weights. Estimated
peak resident weight storage is about 13 GiB; allocator caches, temporary
arrays, activations and outputs add memory. Each block logs available MLX
allocator counters. These counters do not prove DRAM residency or exclude
zero-line handling/compression. The ring has distinct allocations even for
constant fills; the matrices within a normal ring have different seeds.

There are four formats: bf16 and fp16 dense matmul, and MLX affine 8-bit and
4-bit packed `uint32` weights with fp16 activations, scales and biases, using
group size 64 and transposed `quantized_matmul`, the `mlx-lm` QuantizedLinear
layout. “int8” is a CLI label for this weight-only format, **not** a signed
int8-by-int8 GEMM. Compare fills within one geometry/format; instruction
counts, representation bytes and hardware kernels differ across formats.
FLOP counts are dense-equivalent 2MNK per dispatch, excluding quantization
and dequantization (both performed before capture).

Only W[N,K] varies; X[M,K] is a fixed normal activation in each block. Fills
are normal (stddev .02), a separately allocated identical copy, all zeros,
constant .02, exact 50% and 90% zero masks, sign flip, scaling by .25 and 4,
low/high Hamming patterns, sorted rows, and a synthetic weight-like normal
bulk with 1% of entries magnified 12×. No distribution was fitted to real
weights. Related fills share the same source samples. The masks are exact
before conversion; quantization can change the fraction of numerical zeros.
Sorted rows preserve the dense histogram, but changing group placement
before quantization can change quantized values and metadata.

Low/high dense patterns are finite IEEE normals: `0x3c00`/`0xbfff` for fp16,
`0x3f80`/`0xbfff` for bf16. Quantized patterns directly fill each code with
1 or (2^bits−2), with equal fp16 scales 1/(2^bits−1) and biases −.5 in both
arms. This preserves the library's packing and affine interpretation while
controlling code popcount exactly. These extreme controls also change
numerical values and sign; they do not isolate a causal Hamming coefficient.
All-zero float buffers are explicitly written, transferred and evaluated;
zero-valued quantized weights need not have all-zero packed codes.

The seed controls a shuffled comparator order in each round and randomly
oriented ABBA/BAAB quads, always comparing normal to one other fill. A/A′ is
normal versus the identical copy. All operands are prepared and prewarmed
before capture. Three whole-reference-ring timings set an integer number
of full-ring cycles, frozen for **every** slot in that geometry/format.
Every matmul creates a fresh graph and evaluates its output; no constant
closure is compiled. Shapes, activations, dtype and dispatch count are
identical across fills. Slots aim for 10 seconds, but their work count is
fixed: faster conditions finish earlier rather than performing extra work.
Rounded whole-ring cycles can miss the requested slot duration.

Default sizing: 8 geometry/format blocks × 12 comparisons × 4 slots = 384
slots; 3,840 s target work + 192 s gaps + 240 s idle brackets + 600 s setup
reserve = **4,872 s (81.2 min)** in a 90-minute budget. Collector startup,
statistics scans over many GiB, slow hardware and timing differences can
exceed the reserve. The runner checks its elapsed budget and projected work,
then preserves an aborted partial schedule if it cannot fit. A running GPU
dispatch cannot be interrupted by this budget check. There is no automatic
retry or evidence overwrite. Resize prospectively with `--geometries`,
`--dtypes`, `--conditions`, `--rounds`, `--slot-seconds`, `--window-seconds`.
Each selection must include normal and at least one comparator. For a
smaller first window, use `--geometries gemm`; do not relabel it as a GEMV
residency check. One round is a pilot, not a powered equivalence experiment.

`timings.jsonl` contains setup statistics/calibration, slot start/end stamps
(paired epoch/monotonic and, where supported, MONOTONIC_RAW), actual elapsed
time, dispatch/FLOP counts, median timing ratios, and completion or abort.
Statistics describe numerical zeros separately from exact storage popcounts,
including IEEE sign/exponent bits, plus XOR density between corresponding
positions in successive complete C-order tiles. Defaults are 256 storage
elements per tile; the trailing incomplete tile is excluded, and pooling
never compares across matrix boundaries. Insufficient comparisons produce
null, not zero. This is a host placement proxy; hardware tile traversal,
bus encodings and physical bit flips are unknown. Quantized code, scale and
bias statistics are reported separately on the actual dequantized operands.

Capture hooks reuse `PowermetricsTelemetryAdapter.start_sampling` and
`stop_sampling_with_evidence` with a synthetic cadence config and RunContext,
preserving native plist/rich telemetry and current-era clock evidence. They
launch **the existing** `scripts/km003c_monitor.py` with 200 ms polling/rate 2
and require its streaming header before work. Failure to start is retained
and aborts; shutdown targets only the processes this invocation started.
Collectors enclose 15-second idle baselines, slot spans and half-second gaps.
Per-block `capture.json` retains readiness, stop and error metadata; raw
streams remain under that block's `raw/`. No energy reduction or independent
IOReport collector was added. Independent IOReport comparison, if desired,
still requires the lead's approved tool; powermetrics alone is not two meters.

Before interpreting a future run, review A/A′, time ratios, raw frequency,
residency, thermal state, CPU contention and clock/collector validity. A fill
that changes throughput is not an isolated switching-power contrast.
Absent/invalid DC data cannot establish whether a null rail is blind to
operand values. Keep the study's three instrument outcomes open: both move,
DC only moves, neither resolves. This draft implements no new significance,
equivalence or summed-bound rule, and transfers no published noise floor.

Native validation the lead must run on Metal, with MLX and NumPy installed,
using tiny synthetic operands (software validation, not a quiet measurement):

```sh
python3.13 -B -m unittest tests.interp_energy.test_mlx_native
```

It covers every fill/format, materialization and finite output, quantized
matmul versus dequantized dense matmul, numerical-zero behavior, popcount
ordering, A/A′ equality of packed/affine components, and bf16 host encoding
versus native rounding. The present sandbox has no MLX or Metal validation.
