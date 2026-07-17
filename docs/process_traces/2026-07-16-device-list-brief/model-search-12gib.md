```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend a conditional Qwen3-4B primary repin with Qwen3-1.7B as runner-up, and pursue an OLMo-1B conversion spike as the only currently credible dense sibling for OLMoE.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "b6ab05ca8cf100b470eaa55f0301f4e4debe7c13",
    "head_end": "b6ab05ca8cf100b470eaa55f0301f4e4debe7c13",
    "upstream_end": "b6ab05ca8cf100b470eaa55f0301f4e4debe7c13",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "primary-model",
        "action": "needs_ruling",
        "recommendation": "Qwen3-4B conditional winner; Qwen3-1.7B runner-up"
      },
      {
        "row": "olmo-dense-conversion",
        "action": "start_now",
        "recommendation": "Spike original-format OLMo-1B conversion before changing the estimand"
      },
      {
        "row": "cross-family-dense-fallback",
        "action": "do_not_start",
        "recommendation": "Requires an explicit different-estimand ruling and cannot pass current G1/G2"
      },
      {
        "row": "additional-moe-search",
        "action": "wait_for",
        "recommendation": "Dispatch the exact NEEDS-WEB survey below"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## main...origin/main"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## main\\.\\.\\.origin/main"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n '^## D-071|^## D-073|^## 1\\\\. Pair|^## MLX load smokes|^## 8\\\\.' docs/decision_log.md docs/process_traces/2026-07-16-device-list-brief/olmo-verification.md docs/process_traces/2026-07-16-axi-sd-web-verification/memo.md docs/specs/axi/sd_model_pair_scorecard.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["docs/decision_log.md:3795:## D-073: D-016 device-list amendment — Mac + 3080 Ti primary fleet, 12 GiB cap"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "D-073: D-016 device-list amendment"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "python3 -c \"p=30532122624; b=17174780668; print(f'crude_q4_gib={p*0.5/2**30:.3f}'); print(f'artifact_gib={b/2**30:.3f}'); print(f'g10_peak_limit_gib={12-0.15*12:.1f}')\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["crude_q4_gib=14.218", "artifact_gib=15.995", "g10_peak_limit_gib=10.2"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "g10_peak_limit_gib=10\\.2"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Network access was unavailable; volatile adoption, artifact and license facts absent from the repository are labeled NEEDS-WEB.",
      "needs": "Dispatch the three exact web questions in Critical path."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No new model was converted, loaded, generated, or G10-probed; all memory conclusions except the weight-lower-bound failure are estimates.",
      "needs": "Require joined MLX, GGUF, CUDA, G10, KV and license receipts before repinning."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "This scout recommendation does not select a model or amend D-016.",
      "needs": "Ed chooses whether Qwen3-4B advances to the gated repin."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Primary-model shortlist | needs_ruling | NEEDS-WEB P1–P2; three-runtime and G10 receipts | D-016 model pin, tokenizer manifests, §8 ladder, future campaign identity |
| OLMo dense conversion | start_now | Pin original-format source and converter | G4 artifact lineage only; no energy or quiet-Mac work |
| Cross-family dense fallback | do_not_start | Explicit Ed different-estimand ruling | Current G1 family and G2 tokenizer gates |
| Other 7–14B MoE search | wait_for | NEEDS-WEB M1 | Candidate table only |

## Critical path

### 1. Primary model

D-073 raises the G10 cap to 12 GiB, hence `Mpeak≤10.2 GiB`, and explicitly opens 3–4B candidates. [decision_log.md:3795](/Users/edr/code/JouleWise/docs/decision_log.md:3795), [brief.md:90](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-device-list-brief/brief.md:90)

Evidence-weighted rank:

| Rank | Candidate | Adoption / license | Artifacts and policy | G10 / repin cost |
|---|---|---|---|---|
| **1** | **Qwen3-4B** | Adoption count NEEDS-WEB; Apache-2.0 verified | MLX-Q4 plus MLX/llama.cpp/vLLM architecture support recorded; exact GGUF-Q4 and CUDA-Q4 pins NEEDS-WEB. Freeze non-thinking identically across runtimes. [memo.md:223](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-axi-sd-web-verification/memo.md:223) | Strong: ≈2.52 GiB weights + ≈1.14 GiB KV at 8,320 tokens leaves ≈6.54 GiB before the 10.2 GiB ceiling. Medium-high repin cost. [memo.md:174](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-axi-sd-web-verification/memo.md:174) |
| **2** | **Qwen3-1.7B** | ≈5.8M monthly downloads in the dated brief; exact license receipt NEEDS-WEB | Official MLX-Q4, GGUF and native vLLM paths recorded. Same non-thinking complication. [brief.md:98](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-device-list-brief/brief.md:98), [brief.md:101](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-device-list-brief/brief.md:101) | Best expected headroom and lowest-evidence-risk successor; medium repin cost. |
| **3** | Qwen2.5-3B-Instruct control | NEEDS-WEB | Likely lowest-change family control, but no 3B artifact receipts in the repository. No thinking switch. | Strong expected fit; lowest cost only if tokenizer files hash-identically. Still needs new model and ladder receipts. |
| **4** | Gemma-3-4B-IT | Adoption NEEDS-WEB; custom, gated Gemma terms verified | Exact 4B MLX-Q4/GGUF-Q4/CUDA pins NEEDS-WEB. Its multimodal architecture may require `mlx-vlm`, unlike the proven `mlx-lm` adapter. [brief.md:102](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-device-list-brief/brief.md:102) | Strong expected fit, but high adapter/licensing cost. |
| **5** | Phi-4-mini-instruct | Adoption, license and all three artifacts NEEDS-WEB | Evaluate the ordinary instruct model, not a reasoning variant; otherwise output-policy complexity changes. | Strong expected fit; high new-family cost. |
| **6** | Llama-3.2-3B-Instruct | Adoption, current license text and artifacts NEEDS-WEB | No Qwen-style thinking issue, but exact MLX/GGUF/CUDA evidence is absent locally. | Strong expected fit; high new-family and custom-license cost. |

Recommendation: advance **Qwen3-4B** as the conditional primary, with **Qwen3-1.7B** as runner-up. Gemma 4B fits, but it is not the cleaner research pin: gated custom terms create reproducibility and derived-weight redistribution questions, while its multimodal MLX path may add an adapter seam. Until reviewed, G8 remains `NEEDS-VERIFICATION`; publish hashes/recipes, not Gemma-derived weights.

Every repin starts a new evidence era: preserve Qwen2.5 results, regenerate tokenizer-bound manifests, repeat MLX/CUDA/GGUF, G10/KV/batch gates, and rebuild BF16/Q8/Q4 from one source revision. [brief.md:104](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-device-list-brief/brief.md:104), [sd_model_pair_scorecard.md:471](/Users/edr/code/JouleWise/docs/specs/axi/sd_model_pair_scorecard.md:471)

### 2. Dense/MoE pair

Recommend the **OLMo-1B original-format conversion spike**. The mirrored dense/MoE artifacts have byte-identical tokenizer files and an exceptional config-derived active match (`d_active=0.0016`), while OLMoE already generates with one documented default override. [olmo-verification.md:38](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-device-list-brief/olmo-verification.md:38), [olmo-verification.md:80](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-device-list-brief/olmo-verification.md:80)

G-gate risks: G1 needs a 0724-versus-0924 generation ruling; G2 is passed at artifact level; G3 still needs measured routing; G4 is the critical dense conversion plus MLX/GGUF/CUDA parity gate; G5–G8 require one joined local recipe and hashes; G9 may expose base-model quality divergence; G10 looks comfortable—≈3.9 GiB MoE weights plus ≈1.02 GiB KV leaves ≈5.28 GiB for activations—but still needs three smokes; G11/G12 remain Ed-owned. The current HF-format dense artifact is definitively unloadable by mlx-lm 0.31.3 without conversion or a shim. [olmo-verification.md:53](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-device-list-brief/olmo-verification.md:53), [memo.md:97](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-axi-sd-web-verification/memo.md:97)

A cross-family active-matched dense model is a different estimand: it confounds MoE/dense architecture with family, tokenizer and training. It cannot silently pass the scorecard’s within-family G1/G2 fence. [sd_model_pair_scorecard.md:65](/Users/edr/code/JouleWise/docs/specs/axi/sd_model_pair_scorecard.md:65)

Qwen3-30B-A3B still fails outright: its crude Q4 floor is **14.218 GiB**, and the recorded artifact is **15.995 GiB**, both above 10.2 GiB before KV or activations. [memo.md:202](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-axi-sd-web-verification/memo.md:202) Qwen1.5-MoE-A2.7B becomes smoke-admissible by weight under 12 GiB, but ≈8.34 GiB weights + ≈1.5 GiB KV leaves only ≈0.36 GiB, while its dense sibling already fails active matching and has mismatched non-Apache licenses. [memo.md:285](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-axi-sd-web-verification/memo.md:285)

Exact NEEDS-WEB dispatches:

- **P1:** For all six ranked models, what are the 2026-07-16 monthly downloads, exact license/revision/gating, and immutable MLX-Q4, GGUF-Q4 and vLLM-compatible CUDA-Q4 artifact IDs, sizes and revisions?
- **P2:** Do current Gemma terms permit local conversion/mirroring, redistribution of derived quantized weights, and publication of outputs and benchmark measurements; what notices or access restrictions affect a reproducibility pack?
- **M1:** Enumerate public 7.0–14.5B-total decoder MoEs, giving exact active parameters including shared experts, same-release dense sibling/tokenizer/tuning state, license, MLX-lm 0.31.3/GGUF/vLLM support, Q4 byte size, and KV bytes/token at the G10 shape.