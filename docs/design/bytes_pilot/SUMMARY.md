# BYTES pilot summary (agent return, saved by the orchestrator 2026-10-14)

I could not write `/Users/edr/night-archive/pilots/bytes/SUMMARY.md`: the harness blocks subagents from writing report files, so the full content is below instead. All ten models loaded and ran cleanly in MLX. Free disk at the end is 202 GiB, and the whole pilot took about 1 h 05 min of the 4 h budget. Nothing in the brief was cut.

**BYTES pilot: decode throughput and bytes read per token, M3 Max 128 GB, no power capture**

How the numbers were taken:
- **Runs:** each model ran in its own process: load, a short warmup, then 3 repetitions of a 2,048-token raw-text prompt plus 512 greedy tokens. End-of-text was ignored, so every run decoded exactly 512 tokens.
- **Units:** speeds (tok/s) are medians of the 3 runs. GB means 10^9 bytes.
- **Bytes read per decoded token ("measured"):** summed from the stored size of the loaded weights, including the 4-bit scales and offsets. It counts all weights every token uses, one row of the input embedding, the whole output layer, and k/E of the expert weights (k experts used per token out of E).
- **Formula column:** active parameters × 4 / 8, as briefed. It leaves out the scales and offsets (about +12%) and any 8-bit weights; gpt-oss stores its embeddings and attention at 8-bit, so the formula undercounts it by 22%.
- **KV column:** the KV cache holds the stored keys and values of earlier tokens, which attention reads at every decode step. The estimate is the cache size at the end × 0.9 (mean context over the decode). It is approximate for models with linear-attention or sliding-window layers.
- **Bandwidth:** effective bandwidth = measured bytes × decode tok/s. The M3 Max nominal figure is 400 GB/s.

| Model | Kind (k/E) | Total B | Active B | Disk GB | Resident GB | Read/tok formula GB | Read/tok measured GB | KV/tok GB | Load s | Peak RSS GB | MLX peak GB | Prefill tok/s | Decode tok/s | 512-tok decode s | Full run s | BW weights GB/s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-1.7B-4bit | dense | 1.72 | 1.72 | 1.0 | 1.0 | 0.86 | 0.97 | 0.26 | 0.4 | 1.3 | 1.9 | 3630 | 215.6 | 2.4 | 2.9 | 209 |
| Qwen3-4B-4bit | dense | 4.02 | 4.02 | 2.3 | 2.3 | 2.01 | 2.26 | 0.34 | 0.4 | 2.6 | 3.3 | 1349 | 114.0 | 4.5 | 6.0 | 258 |
| Qwen3-8B-4bit | dense | 8.19 | 8.19 | 4.6 | 4.6 | 4.10 | 4.26 | 0.34 | 0.8 | 5.0 | 5.6 | 666 | 66.4 | 7.7 | 10.8 | 283 |
| Qwen3-14B-4bit | dense | 14.77 | 14.77 | 8.3 | 8.3 | 7.38 | 7.87 | 0.38 | 0.6 | 8.7 | 9.3 | 391 | 40.2 | 12.7 | 18.0 | 316 |
| Qwen3-32B-4bit | dense | 32.76 | 32.76 | 18.4 | 18.4 | 16.38 | 17.99 | 0.60 | 0.8 | 18.8 | 19.8 | 163 | 18.1 | 28.3 | 40.8 | 325 |
| Llama-3.3-70B-Instruct-4bit | dense | 70.55 | 70.55 | 39.7 | 39.7 | 35.28 | 39.10 | 0.75 | 3.8 | 40.1 | 41.2 | 75 | 8.8 | 58.1 | 85.1 | 344 |
| Qwen3-30B-A3B-4bit | MoE 8/128 | 30.53 | 3.35 | 17.2 | 17.2 | 1.68 | 1.71 | 0.23 | 0.9 | 17.5 | 18.1 | 1440 | 92.1 | 5.6 | 7.0 | 158 |
| Qwen3-Next-80B-A3B-Instruct-4bit | MoE 10/512 + shared | 79.67 | 3.87 | 44.9 | 44.8 | 1.94 | 2.03 | 0.13 | 4.2 | 45.2 | 47.0 | 1082 | 64.0 | 8.0 | 9.9 | 130 |
| gpt-oss-120b-MXFP4-Q8 | MoE 4/128 | 116.83 | 5.71 | 63.4 | 63.4 | 2.86 | 3.65 | 0.09 | 7.4 | 55.8 | 64.3 | 680 | 63.4 | 8.1 | 11.1 | 231 |
| Qwen3.5-122B-A10B-4bit (pinned jw_models copy, read only) | MoE 8/256 + shared | 122.11 | 9.77 | 69.6 | 68.7 | 4.89 | 5.07 | 0.19 | 11.8 | 53.5 | 71.5 | 417 | 42.6 | 12.0 | 16.8 | 216 |

**Run conditions**
- **GPU wired-memory limit:** `iogpu.wired_limit_mb` is 0 (system default). MLX reports a recommended working set of 115.4 GB (107.5 GiB). The largest MLX peak was 71.5 GB (Qwen3.5-122B), 62% of that, so no model came close.
- **RSS:** peak RSS is lower than the weight size for the two largest MoE models because macOS does not count all GPU-wired pages in RSS. Use the MLX peak for memory planning.
- **Contention:** other agents' unit tests kept about 4 CPU cores busy throughout. Each model's bench from 30B-A3B through 14B also overlapped the next download. Run-to-run decode spread was 3% or less, except Llama 70B (8.4–8.9 tok/s).
- **gpt-oss output:** its greedy output on the raw-text prompt degenerated into repeated quote characters. It needs its own chat format (harmony) for meaningful text; throughput is unaffected.
- **Added rows:** I benched 1.7B, 4B, 8B, 14B and the pinned Qwen3.5-122B beyond the brief, to fill the dense ladder and the high-memory MoE slot.

**What the numbers say for the pack**
1. **The two hypotheses predict opposite results on pairs that run cleanly here.**
   - *Same memory footprint, very different bytes read:* Qwen3-32B dense reads 18.0 GB per token with 18.4 GB resident; Qwen3-30B-A3B reads 1.71 GB with 17.2 GB resident (10.5× the read, same family and tokenizer). Llama-70B (39.1 / 39.7) against Qwen3-Next-80B (2.03 / 44.9) is a 19× gap.
   - *Similar bytes read, very different footprint:* 1.7B (0.97 / 1.0), 30B-A3B (1.71 / 17.2), Next-80B (2.03 / 44.9) and 4B (2.26 / 2.3) read within 2.3× of each other across a 45× range of resident memory.
2. **MoE decode is slow for its byte count.** Dense models reach 209–344 GB/s effective bandwidth; MoE models reach 130–231 GB/s. For example, Next-80B reads 0.9× the bytes of Qwen3-4B but decodes at 0.56× its speed. An energy fit therefore needs a time term (power × seconds) separate from the bytes term. This also helps: it lets the pack separate energy per byte moved from energy per second.
3. **KV reads matter at 2k context.** They add 27% to the weight bytes for 1.7B, 15% for 4B, 13% for 30B-A3B and 2% for 70B. Either hold context fixed and record KV bytes as a second variable, or shorten the prompt for the small models.
4. **Use the measured bytes column, not the formula.**
5. **Test decode, not prefill.** A 2,048-token prefill sends tokens to nearly every expert, so MoE prefill touches almost all resident weights.

**Recommendation**
- **Dense ladder:** six models in roughly 2× steps, 0.97 to 39.1 GB read per token: Qwen3-1.7B, 4B, 8B, 14B and 32B (one family, one tokenizer), topped by Llama-3.3-70B. Llama is a different family, but it is the only clean 70B-class dense model here. Decode time for 512 tokens: 2.4, 4.5, 7.7, 12.7, 28.3 and 58.1 s.
- **MoE set:** three models:

  | Model | Read GB | Resident GB | 512-token decode s |
  |---|---|---|---|
  | Qwen3-30B-A3B | 1.71 | 17.2 | 5.6 |
  | Qwen3-Next-80B-A3B | 2.03 | 44.9 | 8.0 |
  | Qwen3.5-122B-A10B (pinned copy) | 5.07 | 68.7 | 12.0 |

- **Drop gpt-oss-120b.** It runs cleanly, but:
  - it fills the same high-memory MoE slot that the pinned Qwen3.5-122B already fills at no disk cost;
  - it mixes weight formats (MXFP4 experts with 8-bit embeddings and attention);
  - it needs its own chat format;
  - keeping it with the other four new models left free disk at 150.6 GiB, right on the floor.

  If you want a second model family in the MoE arm, swap it in for Llama-70B. The re-download takes about 12 minutes.
- **Session planning:** one warm run of 2,048 prompt tokens plus 512 decoded tokens takes 2.9 s (1.7B) to 85 s (70B). Loading takes 0.4–12 s (about 6 GB/s from a cold disk). Load one model at a time.

**Cache state**
- **Kept in `~/.cache/huggingface/hub`:**

  | Model | Size GB |
  |---|---|
  | Qwen3-30B-A3B-4bit | 17.2 |
  | Qwen3-32B-4bit | 18.4 |
  | Qwen3-Next-80B-A3B-Instruct-4bit | 44.9 |
  | Llama-3.3-70B-Instruct-4bit | 39.7 |
  | Qwen3-14B-4bit | 8.3 |
  | **Total** | **128.5 (119.7 GiB)** |

- **Deleted:** gpt-oss-120b (63.4 GB), and the cache copies of Qwen3-1.7B, 4B and 8B. The pinned copies of those three are already in `/Users/edr/jw_models`. 1.7B and 8B were benched at the same revisions the panel pins (3b1b1768, 545dc425); 4B was benched at revision 4dcb3d10, which I did not check against the pinned copy.
- **Left as found:** the models that were in the cache at the start (listed in `hf_cache_at_start.txt`). Qwen3-4B's entry is back to its original state with no weights. `/Users/edr/jw_models` was only read, never written or moved.

**Not done:** cold-load timing for the cached models (their files were still in memory right after download), and a Llama-family dense ladder below 70B.

On the question that started this run: this pilot alone does not answer "bytes and difficulty by end of November". It shows that every bytes model runs cleanly here and that a full pass over all nine recommended models costs only minutes of compute per repetition set. Whether the work finishes in time depends on the measured-pack schedule and the difficulty pilot's findings.

Files are in /Users/edr/night-archive/pilots/bytes:
- bench.py
- fetch.py
- pipeline.sh
- summarize.py
- summary_rows.json
- r_*.json (raw runs, one per model)
- downloads.jsonl
- hf_cache_at_start.txt