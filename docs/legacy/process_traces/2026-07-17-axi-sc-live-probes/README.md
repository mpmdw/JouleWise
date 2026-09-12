# AXI-SC live probe evidence (2026-07-17, lead-run, Metal live)

Feasibility probes only — no energy measurement, no [QUIET-MAC] window.
Commands per the verdict doc §Exact lead live commands; repo venv
(mlx-lm 0.31.3 / mlx 0.31.2).

| File | SHA-256 | probe_outcome |
|---|---|---|
| axi-sc-mlx-draft.jsonl | `559731f48f035b86e6dc2545543f70c7af861705a3b443c52d8483eac0645f11` | unsupported_for_joulewise(event_observability) — target Qwen2.5-1.5B-4bit, draft Qwen2.5-0.5B-4bit: generation works and accepted tokens are directly observable via `GenerationResponse.from_draft`; actual proposal counts, aggregate acceptance rate, and decode-step emission boundaries are absent |
| axi-sc-mtp.jsonl | `f7ab880040ae5f17e58d97db5a2cbe9b492b1dd6b994c0e8b5a7a45d05b44eeb` | unsupported_for_joulewise(native_mtp_generation) — Qwen3.5-122B-A10B-4bit: no native-MTP generation surface (loader discards mtp.* weights) |

Both verdicts derived by the fail-closed controller at stage
controller_evidence_validation (lead-run 2026-07-17).
