```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Mac plus 3080 Ti can support the core program with a 12 GiB cap, while dropping Jetson mainly sacrifices the explicit edge/8 GiB cell; a Qwen3 repin should be conditional on three-runtime evidence.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "3736c941db0734fa73f2c73db2dfeff619c24295",
    "head_end": "3736c941db0734fa73f2c73db2dfeff619c24295",
    "upstream_end": "3736c941db0734fa73f2c73db2dfeff619c24295",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "should_fix", "title": "Separate edge-specific questions from generic two-node and CUDA requirements"},
      {"id": "F2", "severity": "should_fix", "title": "Choose explicitly among the three device-list and cap contracts"},
      {"id": "F3", "severity": "should_fix", "title": "Treat model repinning as a new evidence era rather than rewriting Qwen2.5 history"},
      {"id": "F4", "severity": "should_fix", "title": "Preferred combined path is 12 GiB cross-target plus a gated Qwen3 successor"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --quiet && git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## main...origin/main"]},
      "expected": {"exit_code": 0, "tail_regex": "## main\\.\\.\\.origin/main"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n '^## D-016|^## D-070|^## D-071|8 GiB capacity cap|Model-family direction' docs/decision_log.md && rg -n '^## 7\\.|^## 8\\.|same pinned runtime|identical model artifact' docs/specs/axi/sd_model_pair_scorecard.md docs/campaign_packs/split_suite_q1_q2_q3.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs/specs/axi/sd_model_pair_scorecard.md:423:## 7. Ed decision required — D-016 8 GB-fit conflict",
          "docs/specs/axi/sd_model_pair_scorecard.md:471:## 8. C5-1.12 quantization ladder",
          "docs/campaign_packs/split_suite_q1_q2_q3.md:353:- Same pinned runtime and identical model artifact on both split ends for real"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "same pinned runtime and identical model artifact"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No candidate was downloaded, converted, loaded, or memory-probed; artifact availability is desk-verified only.",
      "needs": "Require joined MLX, GGUF, CUDA, license, KV, and G10 receipts before amending D-016."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The exact Jetson SKU, usable memory, link topology, and Mac-to-CUDA cache portability remain unknown.",
      "needs": "Resolve P1-004/P1-006 facts before freezing the split matrix."
    }
  ]
}
```

## Findings

### F1 — What each tier contributes

| Question family | Actual hardware need |
|---|---|
| Q1–Q3 split; C5-2.3 KV economics | Need two powered nodes and measured links, not an edge-class node specifically. Real replay additionally requires the same runtime and identical artifact at both ends; synthetic transfer does not. [docs/research_question_registry.md:39](/Users/edr/code/JouleWise/docs/research_question_registry.md:39), [docs/campaign_packs/split_suite_q1_q2_q3.md:349](/Users/edr/code/JouleWise/docs/campaign_packs/split_suite_q1_q2_q3.md:349) |
| Q4–Q6 | Q4 is fitted per target; Q5’s cross-device extension merely benefits from more targets; Q6 needs the wall meter, not Jetson. [docs/research_question_bank.md:16](/Users/edr/code/JouleWise/docs/research_question_bank.md:16), [docs/research_question_bank.md:24](/Users/edr/code/JouleWise/docs/research_question_bank.md:24) |
| C5-2.1/2.2/2.5/2.6 | Need appropriate runtime support. CUDA batching/coalescing benefits from the 3080 Ti, but the Mac batch leg is already independently minted and speculative decoding may use MLX. None logically needs 8 GiB. [docs/research_question_bank.md:819](/Users/edr/code/JouleWise/docs/research_question_bank.md:819), [docs/research_question_bank.md:826](/Users/edr/code/JouleWise/docs/research_question_bank.md:826), [docs/research_question_bank.md:853](/Users/edr/code/JouleWise/docs/research_question_bank.md:853) |
| C5-2.7 | This is the one RQ explicitly written around M3 Max/3050/Orin/**3080 Ti**. Dropping Jetson removes its edge/SoC cell; Mac+3080 retains only a narrower two-stack comparison. [docs/research_question_bank.md:865](/Users/edr/code/JouleWise/docs/research_question_bank.md:865) |
| C5-2.8 | Needs measured split-validation cells and the present Phase-3/borrow-window plan, hence the 3080 Ti under the actual fleet. [docs/research_question_bank.md:873](/Users/edr/code/JouleWise/docs/research_question_bank.md:873) |
| D-016/G10 | The 8 GiB tier is required only if Ed retains the explicit smallest-target deployment promise. It is a selection constraint, not a prerequisite inherent in Q1–Q6. [docs/decision_log.md:803](/Users/edr/code/JouleWise/docs/decision_log.md:803), [docs/decision_log.md:3753](/Users/edr/code/JouleWise/docs/decision_log.md:3753) |

Mac + 3080 Ti can be the two physical split nodes. They cannot perform claim-bearing MLX-prefill → vLLM-decode replay: cross-runtime cache portability is out of scope. A shared llama.cpp build plus the same GGUF artifact could qualify only after the cross-machine portability spike passes. [PROJECT_STATUS.md:455](/Users/edr/code/JouleWise/PROJECT_STATUS.md:455), [PROJECT_STATUS.md:521](/Users/edr/code/JouleWise/PROJECT_STATUS.md:521)

### F2 — Device-list options

| Option | Cap constant and D-016 amendment | Research/advisor consequence |
|---|---|---|
| Keep an 8 GiB Jetson tier | `Ccap=8 GiB`; ratified reserve gives `Mpeak≤6.8 GiB`. Amend only the primary-target examples/closure roster to name Mac + 3080 Ti + selected Jetson; retain criterion 2 and G10. | Keeps constrained-memory failure-frontier evidence and C5-2.7’s edge cell, but restricts every cross-target model to the least-capable target and adds runtime/telemetry work. |
| Mac + 3080 Ti; re-floor to 12 GiB | `Ccap=12 GiB`; reserve is 1.8 GiB, so `Mpeak≤10.2 GiB`. Amend D-016 criterion 1 to the two named targets, criterion 2 from 8→12 GiB, the candidate roster, and closure receipts; propagate the new cap into G10. | Loses the explicit edge/8 GiB claim but gains a wider mid-model and quantization candidate set, CUDA serving work, and an actual two-node path. C5-2.7 becomes a narrower two-stack question. |
| Mac-first; NVIDIA PROVISIONAL | No cross-target cap: `Ct` is runtime-usable Mac unified memory; at exactly 128 GiB, the reserve would be 19.2 GiB and `Mpeak≤108.8 GiB`. Amend D-016 criteria 1–2 so Mac is the sole primary target and move CUDA/GGUF loads from closure requirements to a separately promoted replication track. | Maximizes Mac AXI, large-model, dense/MoE, and quantization work, but Q1–Q3 remain analytical/synthetic until NVIDIA promotion. This materially narrows the project from heterogeneous measurement to Mac characterization. |

The advisor’s energy-proportionality argument does **not** logically require three devices: it establishes why gross energy must retain fixed/idle costs. A diverse fleet strengthens the empirical story, but Mac versus a discrete 3080 Ti is already a substantial proportionality contrast. The more important limitation is unlike measurement boundaries; a wall-calibration bridge matters more than adding a third uncalibrated target. [docs/axi-handoff.md:52](/Users/edr/code/JouleWise/docs/axi-handoff.md:52), [PROJECT_STATUS.md:397](/Users/edr/code/JouleWise/PROJECT_STATUS.md:397), [PROJECT_STATUS.md:415](/Users/edr/code/JouleWise/PROJECT_STATUS.md:415)

### F3 — Model-family reality and repinning cost

Current Hugging Face monthly downloads are an imperfect but concrete usage proxy: Qwen2.5-1.5B-Instruct ≈12.65M, Qwen3-1.7B ≈5.8M, and Gemma-3-1B-IT ≈4.07M. Thus the present pin is not a model “nobody uses.” All three have formal technical reports; no volatile citation-count ranking is asserted here. [Qwen2.5 model](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct), [Qwen3 model](https://huggingface.co/Qwen/Qwen3-1.7B), [Gemma 3 model](https://huggingface.co/google/gemma-3-1b-it), [Qwen2.5 report](https://arxiv.org/abs/2412.15115), [Qwen3 report](https://arxiv.org/abs/2505.09388), [Gemma 3 report](https://arxiv.org/abs/2503.19786).

- **Qwen2.5-1.5B:** strongest JouleWise receipt—mirrored MLX artifact, real generation, energy bundles and KV row—but CUDA/GGUF closure is still missing. [docs/decision_log.md:830](/Users/edr/code/JouleWise/docs/decision_log.md:830)
- **Qwen3-1.7B:** best drop-in successor. Official MLX-4bit and GGUF artifacts exist, and vLLM has native Qwen3 support. It needs an explicit non-thinking output policy. [Qwen MLX artifact](https://huggingface.co/Qwen/Qwen3-1.7B-MLX-4bit), [Qwen GGUF artifact](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF), [vLLM support](https://docs.vllm.ai/en/latest/models/supported_models/)
- **Gemma-3-1B:** MLX, GGUF and vLLM paths exist, but weights are access-gated under custom Gemma terms. The 1B text model and 4B multimodal model also make the preferred same-family small/mid comparison less clean than Qwen3. [Gemma MLX artifact](https://huggingface.co/mlx-community/gemma-3-1b-it-4bit), [Google GGUF artifact](https://huggingface.co/google/gemma-3-1b-it-qat-q4_0-gguf), [Gemma terms](https://ai.google.dev/gemma/terms)

A repin creates a new evidence era:

- Preserve the existing Qwen2.5 bundles and `RQ-QWEN25-SMOKE` as immutable L1 legacy; do not rewrite or compare them as though they used the new model. [docs/research_question_registry.md:57](/Users/edr/code/JouleWise/docs/research_question_registry.md:57)
- Keep the synthetic generator logic and model-independent software goldens, but generate new tokenizer-bound 48-item and five-item manifests, sidecars, IDs and hashes. [docs/specs/suite_next/prompt_sequencing_spec.md:30](/Users/edr/code/JouleWise/docs/specs/suite_next/prompt_sequencing_spec.md:30), [configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1754](/Users/edr/code/JouleWise/configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1754)
- Re-run model-specific Mac/CUDA/GGUF loads, G10, KV sizing/replay, batch feasibility, and every future claim-bearing campaign.
- Rebuild §8’s BF16/Q8/Q4 ladder from one newly frozen source revision; community conversions are discovery evidence, not acceptable lineage. [docs/specs/axi/sd_model_pair_scorecard.md:471](/Users/edr/code/JouleWise/docs/specs/axi/sd_model_pair_scorecard.md:471), [docs/specs/axi/sd_model_pair_scorecard.md:508](/Users/edr/code/JouleWise/docs/specs/axi/sd_model_pair_scorecard.md:508)

### F4 — Recommended combined path

Present Ed with **Mac + 3080 Ti as the primary cross-target fleet, a 12 GiB cap, and Jetson retained only as optional non-cap-setting replication**. Pair that with a **conditional Qwen3-1.7B repin before Window A**:

1. Require immutable source/license, derived MLX-Q4/GGUF-Q4/CUDA artifact receipts, three-runtime generation, G10, KV, and no-thinking-policy evidence.
2. Regenerate tokenizer-bound manifests and the quant ladder.
3. If any cross-target gate fails, retain Qwen2.5 as primary rather than weakening the contract.

This uses Ed’s actual main hardware, preserves the differentiating split/CUDA program, and takes advantage of the fact that claim-bearing Window-A/2M execution has not yet started. It is a recommendation for Ed’s ruling, not a decision. [docs/decision_log.md:3757](/Users/edr/code/JouleWise/docs/decision_log.md:3757), [RUN_STATE.md:90](/Users/edr/code/JouleWise/RUN_STATE.md:90)

## Residual risk

Artifact listings and download counts are current desk evidence, not successful JouleWise loads. Qwen3.5-2B is newer than Qwen3-1.7B, but its visible MLX artifact currently targets `mlx-vlm`, not the repository’s proven `mlx-lm` adapter; treating it as a drop-in “current Qwen” would require a separate adapter-parity spike. [Qwen3.5 MLX artifact](https://huggingface.co/mlx-community/Qwen3.5-2B-4bit)