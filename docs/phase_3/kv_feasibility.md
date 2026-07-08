# KV Persistence Feasibility Verdicts (Stage 3.0)

Verdict registry for the Stage 3.0 spikes, per `docs/phase_3/phase_3_plan.md`.
Codes: `replay_supported`, `replay_unsupported`, `partial(<limitation>)`.
Per-item status authority remains `docs/phase_3/phase_3_exit_checklist.md`
(D-023); this document holds the evidence.

| Stage | Runtime | Verdict | Date |
|---|---|---|---|
| 3.0.1 | mlx-lm 0.31.3 (Mac/Metal) | `replay_supported` | 2026-07-07 |
| 3.0.2 | llama.cpp | pending | |
| 3.0.3 | vLLM | pending | |

---

## 3.0.1 mlx-lm prompt-cache spike

Verdict: **`replay_supported`**

- Runtime: mlx-lm 0.31.3, mlx 0.31.2 (repo venv, Python 3.13.1)
- Hardware: M3 Max (Metal), single machine, fresh-process split
- Model: local mirror `~/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit`
  (4-bit weights; KV cache is unquantized bf16/fp16-width — `dtype_bytes=2`
  in the size model)
- Spike script: `scripts/spike_mlx_prompt_cache.py`

### What was tested

Prefill, cache persist, and resume-decode each run as a **separate OS
process** (`subprocess.run([sys.executable, ...])`); the only state crossing
the prefill→decode boundary is `prompt_cache.safetensors` plus a
`prompt_tokens.json` carrying the exact prompt token ids (the decode process
does not re-tokenize, so tokenizer drift cannot confound the identity check).
Decode is greedy (mlx-lm's default argmax sampler), 64 tokens, compared
token-by-token against a monolithic greedy run in its own third process.

Installed-API surface (verified against the venv source, not memory):
`mlx_lm.models.cache.make_prompt_cache` / `save_prompt_cache` /
`load_prompt_cache` / `trim_prompt_cache` / `can_trim_prompt_cache`, and
`mlx_lm.generate.generate_step(prompt, model, *, max_tokens, prompt_cache)`.

Resume boundary (load-bearing detail): `generate_step` bulk-prefills
`prompt[:-1]` and then steps the final prompt token, which also advances the
cache — so a cache saved after a `max_tokens=0` prefill sits at
`offset == len(prompt)`. The decode process therefore trims one token
(`trim_prompt_cache(cache, 1)` → offset `len(prompt)-1`) and feeds only
`prompt[-1:]`. Feeding the last token without the trim double-counts it and
corrupts the logits. Offsets are asserted at every step.

### Commands

```sh
# headline (fresh-process, subprocess-orchestrated; prints JSON report)
.venv/bin/python3 scripts/spike_mlx_prompt_cache.py run --prompt-len 1024 --decode 64

# size-model prediction for the same model/length
.venv/bin/python3 -m joulewise kv-size ~/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit/config.json --prompt-tokens 1024
```

### Results (2026-07-07, M3 Max)

| prompt_len | measured cache | predicted (`kv-size`) | delta | tokens identical |
|---|---|---|---|---|
| 1024 | 29,365,473 B (28.01 MiB) | 29,360,128 B (28 MiB) | +5,345 B (+0.018%) | yes (64/64, no divergence) |
| 2048 | 58,725,623 B (56.01 MiB) | 58,720,256 B (56 MiB) | +5,367 B (+0.009%) | yes (64/64, no divergence) |

The overhead is a near-constant ~5.3 KiB safetensors header/metadata, i.e.
the Stage 3.0.0 size model needs **no calibration factor** for mlx-lm beyond
"+~5 KiB fixed"; payload-sweep planning can use the formula directly.

Timings (1024-token run; feasibility indication only, not benchmark data):
prefill 0.28 s, cache save 0.014 s, cache load 0.0004 s, resumed decode
(64 tok) 0.32 s vs monolithic prefill+decode 0.54 s; model load ~0.35 s per
process. Full reports: the `run` verb writes `spike_report.json` per run.

Offsets observed: prefill saved at 1024 (2048); resume loaded 1024 (2048),
post-trim 1023 (2047) — exactly as designed.

### Verdict basis and caveats

`replay_supported` is computed by the script from the measured data (token
identity AND size within 2% of prediction), not asserted — a regression
flips it to `partial(...)`/`replay_unsupported` with the failing reason.

Caveats:

- Same machine, same venv both "ends"; this satisfies D-015's same-runtime
  rule but does not test cross-machine portability (that is llama.cpp's
  3.0.2 question; mlx-lm cross-Mac portability would need its own check
  before any two-Mac pairing is planned).
- Greedy decode only; sampled decode identity is neither expected nor
  required by the acceptance bar.
- KV cache saved unquantized. mlx-lm supports quantized KV
  (`kv_bits`/`kv_group_size`); if a Stage 3.2+ transfer wants smaller
  payloads, size and identity would need re-verification under quantization.
- Residual shared state across processes (OS page cache, mlx kernel caches)
  can affect timings but not the token-identity correctness claim; timings
  here are indicative only.
