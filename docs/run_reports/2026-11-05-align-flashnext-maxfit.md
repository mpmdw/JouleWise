# Flash-Next maxfit precision profiles (2026-11-05)

Authority: Ed's task brief, quoting the lead's GOAL.md decision: only routed
`switch_mlp` experts use affine quantization (maxfit: 6 bits; maxfit5: 5 bits;
group size 64). Every other floating weight and the offloaded PLE disk table
use native bf16. The cited `origin/port/qwen4-exp-mlx` ref is unavailable in
this clone; no network lookup was attempted.

Work is local on the requested, already checked-out
`lane/2026-11-05-align-flashnext-port` branch, one commit per brief item.
Preserved the pre-existing untracked `scripts/qwen4exp_real_layer_parity.py`.
No measurement data, Block-5 pipeline, network, coordination-state edits,
kernel registration, or full test suite. Targeted tests only, serially, while
the machine's separate analysis job continues. All fixtures are synthetic.

## Item 1 — profiles and converter policy

Added maxfit/maxfit5 to the shared policy and converter CLI. Both enforce
group size 64 and bf16 PLE; incompatible overrides fail before checkpoint
access. Expert widths that cannot meet the group size fail instead of silently
retaining unquantized experts. Existing profiles keep their defaults.

Validation: `/private/tmp/jwsol/venv-ref/bin/python -B -m unittest
tests.align.test_qwen4_exp_conversion`: **5 PASS**, 7.161 s. Includes all tensor
names/shapes in tiny and release configs, bf16 conversion, fused experts,
input PLE shards, strict inventory and manifest tampering. Policy coverage is
backend independent; native maxfit packing/numerical fidelity is not validated
in this sandbox.

Tests use offline environment variables and place HF/Torch/cache state under
`/private/tmp/jwsol/port-maxfit/tmp`, with OMP/MKL thread counts set to one.

## Item 2 — memory as a hardware constraint

Removed the 80 GB flag. `memory_model` returns a JSON-serializable
`MemoryReport` with `fits_gpu_working_set(limit_bytes)`, plus the selected
limit, fit result and signed headroom in its JSON fields. The CLI reports both
new profiles and accepts `--gpu-working-set-bytes`. Maxfit defaults to and
requires bf16 PLE storage, using the same policy as conversion.

Release-config estimates at context 40,960, chunk 64, batch 1, group 64,
including the existing unmeasured 3 GB runtime reserve (decimal GB):

| Profile | Resident weights | Estimated GPU peak | Headroom vs 115.4 GB | Physical upper estimate |
|---|---:|---:|---:|---:|
| maxfit | 108.042110720 | 112.679466248 | 2.720533752 | 134.154302728 |
| maxfit5 | 92.942616320 | 97.579971848 | 17.820028152 | 119.054808328 |

Both use 102,400,491,520 disk bytes for PLE. Its illustrative uniform-access
page-cache estimate is 10,193,642,156 bytes; the page-span upper bound is
21,474,836,480 bytes. GPU fit does not prove physical fit or zero swap:
maxfit's physical upper estimate exceeds 128 GB, before OS/other processes.
These are accounting estimates, not native measurements or admission results.

Validation: `python3.13 -B -m unittest tests.align.test_qwen4_exp_memory`:
**3 PASS**, 0.039 s, including exact expert and non-expert byte counts,
bf16 PLE, hardware-limit boundaries, negative headroom and JSON serialization.

## Item 3 — bounded bf16 PLE streaming

The converter maps one numeric input shard at a time and copies bounded row
slices into the output mmap file. BF16 source payloads pass through unchanged
as uint16 bits, avoiding fp32 expansion and re-rounding (also for retained
model weights). Non-bf16 sources are still rounded into bf16 by bounded slices.
One flat row-major file per PLE layer preserves the existing mmap reader;
the completion manifest now includes each table's descriptor, total bytes,
and every input shard's output row and byte span. Input/output hashes remain
in the same manifest, written only after successful conversion.

Synthetic validation forces 32-byte chunks across shuffled, separate input
shard files, checks numeric order, exact bits including signed zero/infinities/
NaN payloads, and refuses both concatenation and encoding on the bf16 copy
path. Full tiny bf16 conversion checks every retained tensor's dtype and
manifest coverage. The mmap test independently supplies raw bf16 payloads and
checks exact fp32 bit expansion, deduplicated gather bytes, no affine metadata,
and a copied result. BF16 lookup does **no affine dequantization**; it expands
only gathered rows to fp32 for transfer to MLX.

- Offline reference Python `-B -m unittest tests.align.test_qwen4_exp_conversion`:
  **6 PASS**, 13.334 s.
- Reference Python `-B -m unittest tests.align.test_qwen4_exp_tables`:
  **4 PASS**, 0.185 s.

The 102.4 GB release table was not materialized or read here. Bounded behavior
is demonstrated on synthetic shards; native target-Mac performance remains open.

## Item 4 — native precision and numerical gates

Extended the split-interpreter parity suite with independent maxfit and
maxfit5 native workers. They convert the deterministic tiny HF bf16 model,
load through the pinned/verified native loader, and compare full logits to
the unquantized MLX bf16 baseline. Prospective acceptance bounds:

| Profile | Absolute tolerance | Relative tolerance | Maximum logit RMSE |
|---|---:|---:|---:|
| maxfit | .008 | .03 | .002 |
| maxfit5 | .016 | .06 | .004 |

Each native worker also checks exhaustive serialized/loaded inventories,
every non-expert's bf16 dtype and bitwise equality to baseline, expert uint32
packing/shapes, bf16 scales/biases, module bits/group size, expert-only
quantization records, and bf16 PLE file lengths. Existing cached/chunked,
causal, padded, snapshot/restore and indexer-retention gates run for both new
profiles. Missing MLX imports/devices skip explicitly through the existing
isolated capability probe; numerical failures never skip.

Offline reference interpreter with `JW_QWEN_REF_PYTHON` set to itself and
`JW_QWEN_MLX_PYTHON=/opt/homebrew/bin/python3.13` (no MLX): `-B -m unittest
tests.align.test_qwen4_exp_parity`: **2 PASS / 5 SKIP**, 11.703 s. HF reference
prefill/stepwise max absolute errors: fp32 7.450580596923828e-08; bf16 0.0.
The five native workers, including both maxfit tests, remain **NOT VALIDATED**.
No MLX inference/quantization or CPU fallback was attempted in this sandbox.

The lead must rerun `tests.align.test_qwen4_exp_parity` on a Metal-capable
machine with native mlx 0.31.2 / mlx-lm 0.31.3 and the reference interpreter
set separately if required. The new bounds have not been calibrated against
native observations; treat a failing gate as an unresolved finding.
