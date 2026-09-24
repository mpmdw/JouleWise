```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The packets need one reconciled registration design before a sizing pilot can be armed.",
  "workspace": {
    "base_requested": "313efcca",
    "base_mode": "exact",
    "head_start": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "head_end": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "text": "The thinking-on decoding policy is unresolved despite a model-card warning against greedy decoding."},
      {"id": "F2", "severity": "blocker", "text": "Packet B's block packing and packet C's five-bundle inference rule are not yet one executable design."},
      {"id": "F3", "severity": "should_fix", "text": "The pilot, cap outcome, population count, scoring location, and registration scope need reconciliation."},
      {"id": "F4", "severity": "should_fix", "text": "Packet C's problem-only bootstrap does not propagate uncertainty from measured energy blocks."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "nl -ba joulewise/adapters/mlx_runtime.py | sed -n '980,1028p'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["986: kind: greedy; 987: temperature: 0.0"]},
      "expected": {"exit_code": 0, "tail_regex": "greedy"}
    }
  ],
  "flags": [
    {"id": "R1", "kind": "lead_ruling", "level": "nonblocking", "text": "Primary decoding policy and public handling of MATH problem text require Ed's decision before registration.", "needs": "Ed rules on those two publication and risk choices."}
  ]
}
```

## Findings

**F1 — Make the thinking-on policy a decision before the pilot.** [A §7 R4](</Users/edr/code/wt-1d3796d5-bk/docs/process_traces/2026-09-23-activation-1d3796d5/08-headline-packet-a-math-importer.md>) recommends greedy; [B §7 R3](</Users/edr/code/wt-1d3796d5-bk/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md>) leaves greedy versus sampling open; [C §3](</Users/edr/code/wt-1d3796d5-bk/docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md>) assumes greedy. This is serious for the proposed primary arm: both [Qwen3 model cards](https://huggingface.co/Qwen/Qwen3-8B/blob/c4991a667c9137cff07024144d448d2afe76abc4/README.md?code=true) warn that greedy thinking can degrade performance and loop, and recommend temperature 0.6, top-p 0.95, top-k 20. The current [MLX adapter](/Users/edr/code/wt-1d3796d5-consult2/joulewise/adapters/mlx_runtime.py:984) pins temperature zero.

Greedy plus a cap and repetition label is a valid *greedy-policy* result, but a crossover driven by loops or caps would be weak evidence about model size. Card-style sampling with pinned seeds and repeated attempts better serves Ed’s paper question; it requires a sampler change, stochastic correctness analysis, and roughly 2× or 3× capture for two or three seeds. Thinking-off primary preserves the existing deterministic path and budget, but changes the headline. **I recommend sampled thinking-on primary, subject to a measured pilot budget; if unaffordable, make thinking-off primary rather than presenting a loop-bound greedy crossover as the headline.** Ed owns that risk and scope choice.

**F2 — Reconcile the measurement unit before building the packer.** B §2 proposes two 32-item sub-blocks for a 64-item 8B level and permits several level windows in one envelope. C §2b requires **at least five distinct strict-valid bundles per cell** to meet [L2’s n ≥ 5 per condition](/Users/edr/code/wt-1d3796d5-consult2/docs/contracts/claims_ladder.md:63). Two sub-blocks cannot meet five bundles. At n=64, five nonempty slices need a maximum balanced slice of 13 items; at n=128, 26. B §2 also allows sub-block size by model while saying item slices are identical across models. Register common problem slices, spread each cell over at least five envelopes, and then let the pilot determine packing and the revised window count.

B and C agree on **gross energy between the outer markers of a contiguous level block**, excluding envelope offset, tail, and slack; C calls this a block, B a level window. Use that definition and sum its windows per cell. B’s net-idle alternative should remain secondary: the [gross-first contract](/Users/edr/code/wt-1d3796d5-consult2/docs/contracts/token_normalization.md:20) and [AP-5](/Users/edr/code/wt-1d3796d5-consult2/docs/contracts/analysis_plans.md:267) support gross. Per-item energy remains audit evidence, never an independent energy replicate.

**F3 — Freeze one coherent pilot and scoring contract.** A §2 and C §3 specify **16 pilot problems total**: four at Level 5 and three at each other level. B §7 R4 recommends **16 per level**. That is 64 versus 320 generation attempts across two models and two arms; three observations at a level cannot credibly set its p95 length or cap-hit rate. Choose 16 per level, disjoint from test items, and re-budget the pilot. A and C agree on test n ∈ {64,128}, shared across cells; B’s 64 is only a planning case. Freeze n by a registered runtime rule before test execution.

B §2 says a capped item is truncated **when no answer parses**; A §3 and C §3 say **every cap hit is incorrect**, even with a box. Choose the latter prospectively and retain parsed text for sensitivity analysis. All three use **>20%** cap hits as “cap-bound,” so that threshold is a shared proposal, not a packet conflict; register it with the cap ladder. B §4 places scoring in the executor “at harvest,” while A §6 supplies a pure outcome-table scorer. Resolve this as post-capture, desk-side harvest scoring from immutable item rows; an in-night courier may show provisional counts. C’s two Holm families of five match a thinking-on primary and separately labelled thinking-off secondary. If both arms can carry one headline claim, use one family of ten instead.

**F4 — Repair inference and the factual record.** C §3 assigns each item an estimated share of measured block energy, then bootstraps only problems. That allocation is useful for decomposition, but it treats estimated item energies as fixed and omits between-envelope energy variation. Bootstrap paired problems **and** capture blocks, or use a block-aware interval with instrument bounds; keep the five-bundle gate. Calibrate the directional p-value procedure before calling the Holm results confirmatory.

Three load-bearing checks:

- A §1–2 says 5,000 minus **two excluded duplicate rows**, 954 non-rational rows, and five comma rows leaves 4,040. The arithmetic is **4,039**. Its level totals instead sum to 4,999 before the latter two exclusions and 4,040 after them. Specify whether one duplicate is deduplicated or both rows are excluded, then regenerate hashes.
- B §2’s capped-with-parse rule follows the existing [GSM8K scorer](/Users/edr/code/wt-1d3796d5-consult2/joulewise/benchmark_import.py:950); it does **not** implement A/C’s proposed MATH rule.
- C §7 calls MATH-500’s Level-1 count unverified, while A §1 reports **43** from its downloaded source. Forty-three cannot supply 64 distinct Level-1 items. A’s full-split source is required if its count is reproduced. The current [model panel](/Users/edr/code/wt-1d3796d5-consult2/configs/model_panels/qwen3_4bit.json:71) also contains only a thinking-off rendering pinset, confirming a prerequisite rather than an already ready thinking-on arm.

## Order and rulings

**Work that can start now:** implement and audit the MATH source receipts, eligibility and scorer fixtures; factor the night-kind table; draft AP-5M; design the pure packer, harvest join, figure code, and bench replay. Then integrate the scored worker and reducer, perform the full bench dry run through harvest, cold-gate the pilot registration, run the sizing pilot, and freeze the headline roster and analysis. The [synthesis item 3](/Users/edr/code/wt-1d3796d5-consult2/docs/process_traces/2026-09-23-interactive-7ec32e8b/04-throughput-lane-synthesis.md:31) also requires **one headline registration packet covering both arms and both MATH and affine ladders**; C’s AP-5M alone does not supply it. Before arming, bind weight-tree digests for the already present model directories, thinking-on rendering, source custody, caps, scorer and audit protocol, rail and floor identity, overrun replacement, dry-run receipt, harvest code, and reproducible figures. None is supplied as an executable whole by the packets.

**Minimal rulings:** Ed decides (1) public full problem text versus hash-only custody—recommend hash-only, A §7 R1; and (2) sampled thinking-on primary versus greedy-policy or thinking-off primary—recommend sampled if pilot cost fits. Ed should also approve the resulting extra budget. The magistrate and cold gate can settle (3) rational-only versus broader answer population—recommend rational-only with retention disclosed; (4) 80-problem versus 16-problem pilot—recommend 80; (5) gross versus net—gross; (6) all-cap-hits-incorrect versus parsed-cap credit—all incorrect; (7) five distinct envelopes and block-aware inference versus a claims-ladder amendment—five envelopes; (8) two Holm families of five versus one of ten—two only while thinking-off is explicitly secondary; and (9) cap ladder, >20% label, energy rail/floor match, scorer-audit additions, and same-night versus successor overrun replacement—freeze each mechanically before capture. [C §7](</Users/edr/code/wt-1d3796d5-bk/docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md>) supplies the proposed policy choices; [B §7](</Users/edr/code/wt-1d3796d5-bk/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md>) supplies the operational ones.

## Residual risk

This was read-only inspection. Source-file receipts and source-derived counts were not independently recomputed, and no tests or live measurements were run.