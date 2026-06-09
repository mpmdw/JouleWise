# Hailo Feasibility Checklist

Status: pending.

The Raspberry Pi 5 + Hailo-8L path is a feasibility investigation, not a
headline dependency. If it cannot run an LLM-shaped autoregressive workload,
that outcome should be documented as a hardware applicability result.

## Questions To Resolve

- Can the Hailo toolchain compile any autoregressive decoder-only model?
- Does the supported operator set cover attention and KV-cache access patterns?
- Is there a supported runtime path for repeated token-by-token decode?
- Can power be measured at useful resolution with available equipment?
- If no LLM path exists, what exact blocker applies?

## Verdict Codes

- `supported`: include in Phase 2/3 backend work.
- `runtime_unavailable`: no runtime path for LLM inference.
- `format_unavailable`: no viable model conversion path.
- `unsupported_workload`: accelerator cannot support autoregressive decode.
- `telemetry_unavailable`: workload may run but energy cannot be measured.
- `pending`: unresolved.

## Current Verdict

`pending`
