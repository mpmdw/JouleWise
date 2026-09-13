# DSpark/DFlash MLX feasibility smokes (2026-07-17, lead-run, Metal)

Vendored ARahim3/mlx-dspark @ 2facf79 + LOCAL VENDOR PATCH (gemma4 import guarded; see VENDOR_PATCH_NOTES.md in clone); dedicated venv (mlx-vlm 0.6.5); target /Users/edr/jw_models/mlx-community/Qwen3-4B-4bit; drafter deepseek-ai/dspark_qwen3_4b_block7 (auto-fetched); --no-lookup-drafts pinned; seed 7; 24 new tokens; feasibility smokes, NOT energy measurements or claims.

| mode | tok/s | accept/round | target fwds |
|---|---|---|---|
| dspark | 45.8 | 2.60 | 11 |
| dflash | 40.4 | 2.45 | 12 |
| baseline greedy | 113.0 | — | 24 |

VERDICT: both methods RUN NATIVELY on MLX with per-round acceptance observability (accept/round + target-forward counts surfaced — the surface pinned mlx-lm lacks per the AXI-SC negative). OBSERVATION (hypothesis-generating only; thinking-mode engaged, unmatched outputs): baseline greedy outpaced both spec modes at this small-target/short-output point — drafter-overhead economics (draft row C5-2.5c) is live and needs ENERGY measurement, not tok/s, to adjudicate. Measured spec-on/off runs belong to the exploratory block under quiet-window discipline; Qwen3 thinking-policy pin (D-074) required.
