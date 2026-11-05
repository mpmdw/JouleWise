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
