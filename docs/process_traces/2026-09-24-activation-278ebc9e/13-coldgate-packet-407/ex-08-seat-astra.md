```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Astra 6 recommends a boundary check first, a smaller budget experiment, and corrections to the proposed scientific interpretations.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "7cd1124f394599fe8508e5802a8b134587a5f97e",
    "head_end": "7cd1124f394599fe8508e5802a8b134587a5f97e",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"Q1","severity":"should_fix","title":"A3 cannot decide whether energy per correct answer is scientifically informative."},
      {"id":"Q2","severity":"should_fix","title":"USB-C input versus software rails is a boundary comparison, not an accuracy calibration."},
      {"id":"Q3","severity":"should_fix","title":"Budget manipulation is useful; a full budget-by-voting expansion is premature."},
      {"id":"Q4","severity":"should_fix","title":"Validate timing and statistical semantics before changing claim rules."},
      {"id":"Q5","severity":"should_fix","title":"Review tiers must follow scientific impact rather than filenames."}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"inspection",
      "cmd":"git status --short --branch\ngit rev-parse HEAD",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","7cd1124f394599fe8508e5802a8b134587a5f97e"]},
      "expected":{"exit_code":0,"tail_regex":"7cd1124f394599fe8508e5802a8b134587a5f97e$"}
    }
  ],
  "flags": [
    {
      "id":"F1",
      "kind":"verification_gap",
      "level":"nonblocking",
      "text":"Source inspection and planning arithmetic only; no model loads, measurements, or Monte Carlo replay.",
      "needs":"Validate physical feasibility and operating characteristics before claim-bearing collection."
    }
  ]
}
```

## Findings

### Astra 6

Citation abbreviations below denote these exact files:

- **R**: `docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md`
- **AP**: `docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md`
- **PC**: `docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md`

### Q1 — POSITION: NO to A3 as the prerequisite first model night

**Decisive argument.** The premise is wrong. Even if energy equals a model-specific constant times tokens, measuring that constant establishes the conversion needed to compare models. Flatness within one model does not establish equality across models, workloads, or measurement boundaries. Nor does constant power imply constant J/token: token latency can change. A3 can test context dependence; it cannot decide whether MATH energy-per-correct “is about energy.” That claimed implication appears explicitly in R:128–131.

A single growing trace also confounds context position with elapsed time, heat, and generated content. Fitting its cumulative energy to a quadratic creates strongly dependent residuals. A nonsignificant quadratic term does not demonstrate practically constant J/token.

The admitted pair has 40,960-token contexts, but this establishes capacity on paper, not throughput (`configs/model_panels/qwen3_4bit.json:5–16,38–49`). A 32,000-token trace needs at least **53.3 tokens/s** within 600 seconds, or **66.7 tokens/s** within the 480-second interior, before other costs. Those envelope limits are real (`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:17–18,32–33,98`).

**What would change my position.** A replicated, context-controlled effect within the actual MATH token range that changes model comparisons materially would make context characterization urgent. The proposed single forced trace cannot establish that generalization.

**Cheapest night sketch.** If context dependence remains a priority, use Qwen3 8B 4-bit alone: twelve 600-second envelopes, four randomized repetitions at each of three prospectively selected context lengths, provisionally 1k/8k/24k. Measure the next 1,024 decoded tokens after controlled prefill and thermal preparation. Establish fit before freezing the lengths. Report bin joules, J/token, tokens/s, mean power, and paired context contrasts with uncertainty. Treat repetitions—not tokens—as energy replicates. With a roughly 5 J effective contrast bar, 1,024-token bins require roughly **0.0049 J/token** separation just to reach that scale; large total bin energy alone does not guarantee resolution (`docs/decision_log.md:5335–5338`). This experiment does not reproduce a natural 32k reasoning trace; label its narrower estimand.

**Risks.** It displaces instrument validation and task-level observations. Thermal history, artificial prefixes, and forced continuation can dominate interpretation. An alternative architecture is not essential initially. The scout’s inventory uncertainty is partly resolvable: the installed Qwen3.5-122B-A10B config explicitly lists linear and full-attention layers (`/Users/edr/jw_models/mlx-community/Qwen3.5-122B-A10B-4bit/config.json:27–40`). That is a candidate, not evidence of execution feasibility or a controlled attention comparison.

### Q2 — POSITION: AMEND

Run a **paired DC-input/rail boundary characterization**, initially at 4-bit. Do not call it an instrument-accuracy result or postpone everything for bit-width coverage.

**Decisive argument.** The archived KM003C reader measures USB-C Vbus × Ibus, not AC wall power (`/Users/edr/night-archive/km003c-tools-20260923/km003c_probe.py:2–11,41–44`). The software manifest names CPU, GPU, and ANE (`joulewise/adapters/powermetrics.py:57–58`). These are different boundaries.

A phase-dependent ratio could reflect battery charging/discharging, other system loads, conversion losses, or counter behavior. It cannot identify counter bias or DRAM energy uniquely. Rail labels also do not establish exactly which physical circuitry Apple includes. Two instruments measuring different quantities cannot calibrate each other by taking their ratio.

Communication is demonstrated by the archived reads, but their receipt timestamps do not establish acquisition latency or averaging semantics (`/Users/edr/night-archive/km003c-tools-20260923/meter_paired.txt:1–6`; `km003c_probe.py:124–134` at that same archive root).

**Falsification.** Repeatable phase-dependent ratios would falsify a phase-invariant boundary conversion. They would not prove the hypothesized cause. A same-boundary, independently characterized reference would be needed to establish counter accuracy.

**Cheapest night sketch.** Use the admitted 1.7B and 8B 4-bit models: two models × prefill/decode × three repetitions = twelve envelopes, counterbalanced over the night. Use sustained phase-dominated workloads; include fixed idle brackets and measure remaining phase contamination. Collect synchronized DC and rail energy, battery state/flow, temperature, and workload timing. Report both gross energies in joules, their ratio, repeatability, and alignment sensitivity; incremental load-minus-idle values are secondary and explicitly defined. Require a demonstrated stable battery condition before interpreting phase differences. Add meter logging to later nights only after validating its overhead and alignment. The admitted panel currently supplies the two 4-bit cells (`configs/model_panels/qwen3_4bit.json:5–16,38–49`).

**Risks.** Integration consumes preparation time and an initial quiet slot, but addresses a uncertainty that affects every later energy claim. Battery buffering could make short phase comparisons uninterpretable. Bit-width expansion introduces artifact and runtime differences before the basic boundary problem is understood. “Run alongside” must mean one integrated acquisition, not competing collectors.

### Q3 — POSITION: AMEND

Adopt assigned budgets as the primary intervention; retain model size and all five MATH levels. Stage parallel voting as a separate, small experiment. Do not promise an identified optimum.

**Decisive argument.** The illustrative R = 1.019 is a planning example, not an observed crossover. Its accuracy-only calculation gives SE(log R) = **0.237**, approximately ×/÷ **1.59** at n = 64; at n = 128 the factor is 1.39 (AP:295–316). These figures are assumption-dependent: paired correctness covariance and energy–correctness dependence matter. Nevertheless, they plainly do not support locating a tiny near-equality effect.

A frontier does not cure sampling uncertainty. Searching more policies can make winner selection less reliable. The useful question is: **how does an assigned inference policy change energy and correctness on this problem population?**

**Cheapest adequate design.**

- Independent variable: **total generated-token cap**, initially {512, 2,048, 8,192}; two models, five reported levels, thinking enabled. Call this a thinking-budget intervention only if the implementation separately controls thinking and answer generation.
- Target **n = 64 distinct problems per level**, paired across all six model/cap policies. Freeze sampling, seeds, answer extraction, and cap semantics. Spread energy replication over independently captured blocks and nights. A disjoint pilot determines feasibility and precision, not a favorable policy.
- Estimands per model/level/cap: mean gross **J/attempt**, probability correct, and **E[energy]/P(correct), J/correct**. Report their joint uncertainty and pairwise changes. Report unresolved rankings; zero or sparse correctness must not become a finite “optimum.”
- A1 extension: one model, k = 1 versus 4, sequential versus batched execution at a fixed cap, initially on 16 distinct problems per level. Use corresponding stochastic draws and a frozen vote/tie/invalid-answer rule. That is a mechanism pilot, not a powered accuracy-ranking claim.

This is a staged campaign, not one night. Even the six-cell main design permits **6,881,280 generated tokens** at its caps. The older, narrower plan already estimates about 12 nights at n = 64 (AP:1297–1298).

**Falsification.** If increased budgets are capped or yield virtually no valid answers throughout the feasible range, this design cannot identify a useful frontier. If extra budgets give indistinguishable policy outcomes within prespecified practical margins, their added complexity is not justified. The design can reveal both outcomes; n = 64 does not guarantee resolution.

**Risks.** This displaces the existing single-cap analysis and requires coordinated contract changes: PC:138–149 fixes two model roles and one selected arm’s cap; AP:483–499 fixes the existing estimand and claim ceiling. Batching adds memory pressure, sampling dependence, and scheduler effects. Greedy duplicates are not useful independent votes. Importantly, the current rule counts every capped attempt incorrect even when an answer parses (AP:542–549): changing caps under that rule changes the completion policy, not simply “reasoning ability.”

### Q4 — POSITION: AMEND; support all three work items, not their strongest advertised conclusions

**Decisive argument.**

1. **Clock:** add monotonic event timing while preserving raw epoch anchors and clock-domain mapping. `now()` returns epoch time and the protocol promises that unit (`joulewise/clock.py:30–38,55–72`). Replacing its return value with monotonic seconds would violate that contract. Monotonic workload events alone do not repair wall-time behavior in the power stream. Remove network-time toggling only after end-to-end mapping survives injected steps and slews.
2. **Order:** prospectively balance ABBA and BAAB starts, using a frozen randomized allocation within relevant strata. Current generation repeats ABBA and explicitly disclaims randomization (`configs/campaigns/d117_contrast_v5/generate_configs.py:208,1708–1710,2538–2545`). Balance helps order effects; it does not eliminate arbitrary thermal carryover.
3. **Statistics:** simulate before claim-bearing use. D-165 measures widening of a constructed uncertainty bound, not directly the fraction of physical variability caused by timing (`docs/decision_log.md:10737–10749`). Its sensitivity to width/SD is therefore expected; interpretation is the scientific issue.

The floor includes a prediction term and a sample maximum (`joulewise/detection_floor.py:871–881`). But the claim code also checks intervals, multiplicity, and equivalence (`joulewise/analysis_engine/claims.py:343–382`). The blanket “neither TOST nor minimum-effect” criticism is unsupported. **Do not divide the entire floor by √n:** shared systematic uncertainty does not average away.

**Cheapest design and falsification.** No quiet night. Replay the actual corner/point functions and claim path under declared Gaussian, heavy-tailed, drift, and shared/local-error scenarios; vary calibration n, analysis n, effect, and width/SD independently. Evaluate the joint twelve-component verdict with its dependence. Report coverage, false claims, power, and refusal rates against a declared claim meaning. If existing behavior meets those targets, reject the alleged scale defect. The quoted 0.47 probability remains unverified here.

**Risks.** Clock and order edits change evidence semantics and frozen registrations; they are not cosmetic fixes. Simulations can become tautological if generated solely from the estimator’s assumptions. Preserve prior evidence and require a new prospective version.

### Q5 — POSITION: AMEND

Use full gating for **anything capable of changing a scientific result or its admissibility**; one independent reviewer plus relevant CI elsewhere.

**Decisive argument.** Filenames are an unsafe boundary. A runner, clock, scorer, model pin, exclusion policy, or prose registration can alter a claim as directly as an estimator. Existing orchestration already distinguishes tiers by cost of error, yet separately imposes broad merge gates (`docs/orchestration.md:84–99,159–167`). The rule and ledger must agree; the current template explicitly requires twelve rows (`.github/pull_request_template.md:7–20`).

**Cheapest design.** Require a short impact statement, checked by the reviewer: can this change observations, selection, units, uncertainty, correctness, or a published scientific sentence? If yes, apply the full scientific review. Retain provenance, immutable evidence, and final integration verification. Cold-gate the process amendment and show Ed its disposition; the current process explicitly assigns proposed rules to that route (`docs/orchestration.md:64–71`).

**Falsification.** Audit subsequent low-tier changes for escaped scientific defects and mistaken classifications. An escape attributable to the lighter tier is evidence to tighten that boundary. Reviewer agreement or faster completion is not evidence of scientific safety.

**Risks.** Misclassification can bypass the very checks that matter; an expansive default can recreate the present burden. This should displace redundant review of low-impact work, not physical validation or adversarial examination of scientific assumptions.

### (f) ORDER — next three measurement nights

1. **DC-input/rail characterization**, after meter alignment and battery-state checks. It establishes what later energy numbers mean.
2. **Disjoint MATH budget feasibility pilot** with the two admitted models and three proposed caps. Measure timing, cap completion, scorer behavior, energy variability, and token-based energy prediction error across all levels.
3. **First registered A2 collection tranche**, if feasibility and simulated precision justify it; otherwise a prospectively defined repair/replication night addressing the pilot’s specific failure.

These are scientific priorities, not assertions about current scheduling readiness. Each night gets an explicit 9,000-second budget and at most twelve 600-second envelopes under the inspected protocol (`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:17–18,98`). A3 becomes conditional follow-up; A1 follows a successful batch pilot.

### (g) What matters more

**Define the claim before optimizing its gate.** A direction claim, a practically important effect, and an equivalence claim require different operating characteristics. The roughly 1 J attribution scale and 5 J effective phase-contrast bar are not universal constants for new durations, boundaries, or ratios (R:58; `docs/decision_log.md:5293–5297,5335–5338`). A J/correct comparison requires uncertainty propagated through both energy totals and correctness denominators; a dimensionless ratio cannot be compared directly with a joule floor.

Also test the token-arithmetic premise directly: fit a simple energy predictor using model identity, input/output tokens, and phase on separate data, then assess held-out error and whether energy measurements change substantive comparisons. That is a more relevant test of added information than demanding quadratic curvature along one forced trace.

## Residual risk

No physical feasibility, meter accuracy, battery behavior, or simulation probability was established in this read-only review. All night sketches are prospective designs. The workspace remained unchanged; no excluded state files or other seats were consulted.