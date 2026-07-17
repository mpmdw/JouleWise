# AXI-SB live probe evidence (2026-07-16, lead-run)

Lead-executed live probes for the pinned mlx-lm static-batch feasibility
verdict (`docs/specs/axi/sb_static_batch_verdict.md`). Feasibility probes
only — no energy measurement, no [QUIET-MAC] window consumed; agent load
was active on the machine and does not contaminate a functionality check.

Machine: Ed's Mac (Metal live), repo venv `.venv` (mlx-lm 0.31.3 / mlx 0.31.2),
model mirror `/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit`,
worktree `impl/axi-sb` at base `36b4da1`.

Command (per verdict doc §Lead closeout; run once with `--batch-size 2`,
once with `--batch-size 4`):

    .venv/bin/python scripts/axi_sb_static_batch_spike.py \
      --model /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit \
      --batch-size <B> --max-tokens 8 --timeout-seconds 180

| File | SHA-256 | probe_outcome |
|---|---|---|
| `axi-sb-b2.jsonl` | `ba632327dd16940b42d017600f7c7864a2dc8c8ee7a81a2cf072af249ee9f612` | `supported` |
| `axi-sb-b4.jsonl` | `e0e5804dacc1270ee94561988314274fcda1b4159e3e2b2cb436ea448616951b` | `supported` |

Lead verification against the classification (both runs): configured B ==
realized model-call leading dimension (2 and 4 on every model call, prefill
`[B,12/13]` and every decode step `[B,1]`); `insert_call_count` == 1 (one
genuine batched insertion, not a singleton loop); B distinct `request_id`s
each carrying `output_token_ids` + `output_token_ids_sha256`,
`output_token_count`, `stop_reason` (`length`), per-token
`token_timestamps_s`, and all four `phase_hooks`
(prefill/decode started/ended). Memory-fit observations (separate field,
not support semantics): B=2 peak 968,744,980 B fit=true; B=4 peak
1,034,368,392 B fit=true; no failing B tested.
