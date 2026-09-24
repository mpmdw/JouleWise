# Calibration-night 32k desk smoke — blocked preflight

This is a **desk feasibility** record at HEAD `63d67e4a80867a8b69ff52984f5876ff6f322585` on branch `docs/2026-09-24-278ebc9e-smoke`, macOS 26.6.2 build 25G83. It contains **no model timings, memory measurements, or energy numbers**. The model panel SHA-256 is `78875a0e8b2c6d9f573cd42b0d27de6498cdfc8de57af4b4a502e1f93a02513a`.

The operator read `01-registration-draft.md` and `03-desk-smoke-plan.md`, checked the two admitted local model directories and tokenizer hashes, then ran:

```sh
python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/smoke.py
```

The command exited 1 at preflight: `ModuleNotFoundError: No module named 'mlx'`. The available Homebrew Python 3.11–3.14 installations all lack MLX; the worktree has no MLX virtual environment. No model was loaded. The script enforces local-only model paths and offline Hugging Face mode and is ready to replay under an authorized MLX environment. It records each repetition and rung, the provisional token-ID prompt digest, load and timing boundaries, 512-token output count, resident and Metal peak memory, and an 8192-token sustained-prefill probe when the runtime is present. The prompt remains provisional and is not a sealed capture prompt.

The sandbox also refused `sysctl -n hw.memsize`, `sysctl vm.swapusage`, and `ps -axo pid,pcpu,comm -r` with `Operation not permitted`. A start snapshot from `uptime` was `11:15  2 users, load averages: 4.60 4.51 3.47`; no timing has an associated load snapshot because no timing ran. The script preserves probe errors in `results.json` rather than inventing RAM, swap, or CPU observations. The fenced battery, meter, and quiet-measurement operations were not attempted.

## Results

Every cell below has three explicit failed preflight rows in `results.json`. `—` means **unmeasured**, not zero. The 32,768 + 512 token length fits the panel's 40,960-token declared context, but generation was not attempted.

| Model | Input tokens | Reps 1/2/3 | Prefill s | Decode 512 s | Decode tokens/s | Peak RSS / Metal | 600 s fit |
|---|---:|---|---:|---:|---:|---|---|
| qwen3-1p7b | 512 | fail/fail/fail | — | — | — | — | unknown |
| qwen3-1p7b | 2,048 | fail/fail/fail | — | — | — | — | unknown |
| qwen3-1p7b | 8,192 | fail/fail/fail | — | — | — | — | unknown |
| qwen3-1p7b | 16,384 | fail/fail/fail | — | — | — | — | unknown |
| qwen3-1p7b | 32,768 | fail/fail/fail | — | — | — | — | unknown |
| qwen3-8b | 512 | fail/fail/fail | — | — | — | — | unknown |
| qwen3-8b | 2,048 | fail/fail/fail | — | — | — | — | unknown |
| qwen3-8b | 8,192 | fail/fail/fail | — | — | — | — | unknown |
| qwen3-8b | 16,384 | fail/fail/fail | — | — | — | — | unknown |
| qwen3-8b | 32,768 | fail/fail/fail | — | — | — | — | unknown |

The draft's budget is collective: initial 30 s idle, 30 s after each retained rung, at least 60 s of active sustained prefill, 30 s final idle, observed rung times, observed load and overhead, and at least 30 s remaining in the 600 s envelope. Its projected-total gate is **≤570 s**. With no rung, load, or sustained-prefill timings, neither model's total can be computed. The 80%-of-physical-RAM and no-swap-growth gates are also untested. No evidence supports dropping 16,384 or 32,768; **no rung-set decision was made**. The 512-token decode ≤50 s check for the proposed stopwatch band is untested. Logger 0.5 s receipts and payload close were not benchmarked.

**Verdict: NO-GO for sealing or arming from this smoke.** Replay in an authorized environment with MLX available and working RAM, swap, and process-load probes, then assess the draft's drop order using the measured upper times. This desk record is not quiet-machine evidence.
