# 2026-11-06 — Qwen4 quantization-quality harness

Implemented the compact bf16-reference capture and repeatable quantized-model
scorer requested for the 128 GB Saturday run.  The code reuses gold prompt pins
and gold head outputs, records exact top-1/top-5/NLL metrics, and explicitly
labels the only KL recoverable from top-k plus log-sum-exp as projected KL.

The requested `lane/2026-11-07-qwen4exp-mbp-live` fetch was attempted directly
from the repository URL but this container's CONNECT proxy returned HTTP 403.
The integration is consequently against the stable MLX-LM model load boundary
and the paths/commands expected from that live kit, rather than unverified
branch-specific internals.  Saturday must run the documented fetch first.

Verification and final commit/PR are recorded in the session's Git history.
