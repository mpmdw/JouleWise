# Literature scan: output length, window length and baselines in LLM energy measurement

Fable research seat, 2026-09-24 evening, web sources with URLs. Filed by the lead, condensed. The seat says where it could not verify a claim, and those caveats are kept.

## Fixed output length

Fixed output length (ignore EOS) is **standard for systems comparisons**:
- `vllm bench serve --ignore-eos` (https://docs.vllm.ai/en/latest/cli/bench/serve/);
- NVIDIA's guide says ignore_eos "should be set to True … to obtain consistent measurement" (https://developer.nvidia.com/blog/llm-benchmarking-fundamental-concepts/);
- LLMPerf (https://github.com/ray-project/llmperf);
- a GPU energy-characterisation paper disables EOS "so that each request generates exactly N output tokens" (https://arxiv.org/html/2608.28044).

It is **inappropriate for real-task energy per query**. ML.ENERGY (https://arxiv.org/html/2505.06371v1) and MLPerf LLM tasks honour EOS, because verbosity is part of the model's cost. The known distortion is post-EOS looping text. No paper quantifying its energy effect was found.

## Measurement windows

- **Zeus/ML.ENERGY:** ~1 s windows are "vulnerable to sampling noise", and energy "stabilizes from 5 seconds onward" at ~100 ms updates (https://ml.energy/blog/energy/measurement/thermally-stable-profiling-for-accurate-gpu-energy-measurement/).
- **MLPerf:** a 600 s performance run and a 60 s power loop minimum (https://github.com/mlcommons/inference_policies; https://arxiv.org/html/2410.12032).
- **Words to Watts:** 100 ms sampling; energy per token barely changes between 512 and 1024 max tokens (https://arxiv.org/pdf/2310.03003).

## Apple silicon

- **Intelligence per Watt:** powermetrics at 50 ms with numerical integration (https://arxiv.org/html/2511.07885v1).
- **apple-silicon-llm-bench:** powermetrics at `-i 100`; discards the first "since boot" sample; fixed tg128/256/512 budgets; no idle subtraction (https://github.com/john-rocky/apple-silicon-llm-bench).
- **An M2 Ultra runtime study:** 10 interleaved trials per cell (https://arxiv.org/pdf/2511.05502v1).

## Baselines

Practice splits between no subtraction on a quiet machine (ML.ENERGY, Luccioni, GreenBench) and a measured idle baseline with net energy (https://arxiv.org/html/2512.01644; https://arxiv.org/html/2608.00008).

## Recommendation

- Keep the fixed-length greedy workload for this systems question, and label the results fixed-workload J/token.
- Use windows of ≥ 5 s (production's 6.4 s request qualifies).
- Interleave repeats, and report gross and net.
- Use the pre/post idle drift as the background-daemon check.

## Relation to the paper

The paper's headline (energy per correct answer, natural lengths) is the per-query case, where EOS must be honoured.
