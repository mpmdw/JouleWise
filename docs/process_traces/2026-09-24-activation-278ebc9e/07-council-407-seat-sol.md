```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Prioritize a paired input-energy check and the existing live measurement chain; narrow A3 and separate thinking budgets from parallel voting.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "7cd1124f394599fe8508e5802a8b134587a5f97e",
    "head_end": "7cd1124f394599fe8508e5802a8b134587a5f97e",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "Q1", "severity": "should_fix", "text": "Do not make the proposed single 32k trace the first model night or treat it as a prerequisite for MATH."},
      {"id": "Q2", "severity": "should_fix", "text": "Pair the KM003C with rail telemetry, but call it a USB-C input-energy comparison and defer the bit-width factor."},
      {"id": "Q3", "severity": "should_fix", "text": "Test thinking-budget policies in a staged factorial study; keep parallel voting separate and do not claim an exact optimum from unresolved ratios."},
      {"id": "Q4", "severity": "should_fix", "text": "Run targeted simulations and prospective clock/order changes; do not mutate a frozen pack as a cosmetic fix."},
      {"id": "Q5", "severity": "should_fix", "text": "Set review depth by effect on measurement or claims, including timing and runner code, rather than by filenames."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["7cd1124f394599fe8508e5802a8b134587a5f97e"]},
      "expected": {"exit_code": 0, "tail_regex": "^7cd1124f394599fe8508e5802a8b134587a5f97e$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The packet reports head 4a78cc0; this checkout is 7cd1124. Load-bearing source lines were inspected at the checkout head.",
      "needs": ""
    }
  ]
}
```

# Sol 6.0 — blind council seat

## Findings

### Q1 — A3 first model night: **AMEND**

**Position and science.** Study context-dependent decode energy, but do not put the proposed 32k forced trace first or call it a prerequisite for MATH. A 1k-token bin may contain tens of joules, comfortably above the approximately 1 J attribution limit and 5 J effective claim bar. That makes a *large bin difference* measurable; it does not make one trace an estimate of a general slope. Forced continuation after a natural stop can change the workload, thermal state can drift along the trace, and `E(n)=an+bn²` confounds a fixed setup cost with curvature. The current workload is thinking-off, greedy, forced 512 tokens; A3 is a new workload. The admitted 1.7B and 8B panels declare 40,960-token context, but neither a successful 32k run nor an alternative-attention artifact is established. At 600 seconds, 32k output requires over 53 tokens/s before setup; the quiet protocol has twelve 600-second envelopes in 9,000 seconds. (`docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md:46,58,128-131`; `docs/decision_log.md:10755-10762`; `configs/model_panels/qwen3_4bit.json:16,49`; `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:17-18,76,98`.)

**What would change my mind?** A replicated, material rise in marginal J/token over context lengths actually reached by the scored workload, persisting after input-energy and thermal checks, would make A3 important to interpretation. The proposed single trace could reveal a trend; it could not distinguish context growth from those other changes or establish the attention mechanism.

**Cheapest night.** After a load and duration smoke, use the admitted 8B 4-bit model and a frozen nested prefix. Assign three envelopes each to starting contexts near 1k, 8k, 16k and 32k tokens, in balanced order; generate the same 1k-token continuation policy in each 600-second envelope. Record gross and baseline-adjusted joules, token timing, throughput, power state and refusals. Report marginal J/token by context with replicate intervals and a token-only prediction check. Treat the quadratic as a sensitivity fit, and add an alternative-attention model only after its weights and executed path are verified. The runtime has max-token, EOS-suppression and token-event machinery for this pilot. (`joulewise/adapters/mlx_runtime.py:694-701,727-745,765-835`; `docs/research_question_registry.md:55`.)

**Critical-path risk.** This costs a quiet night and a new registration while the existing `_v5` chain needs its G2-a prefill selection. Even a clean context slope may say little about short MATH answers; an unsuccessful 32k load or uncontrolled temperature would leave the night uninterpretable. (`docs/decision_log.md:10755-10762,10766-10774`.)

### Q2 — B1 alongside: **AMEND**

**Position and science.** Yes to paired measurement soon, at 4-bit first. The KM003C probe reads USB-C voltage and current, so it measures **DC input at its placement**, not mains wall energy or an independently calibrated total-system truth. The `powermetrics` manifest sums CPU, GPU and ANE rails. A raw input/rail ratio therefore mixes omitted components, conversion loss, idle load and possible battery flow; calling a larger decode ratio “DRAM bias” would outrun the instrument. The archived probe shows watts about 0.5 seconds apart, but its printed time is the host receipt time and establishes neither meter latency nor calibration. (`/Users/edr/night-archive/km003c-tools-20260923/km003c_probe.py:2-13,120-134`; `/Users/edr/night-archive/km003c-tools-20260923/meter_paired.txt:3-8`; `joulewise/adapters/powermetrics.py:50-58`.)

**What would change my mind?** If calibrated, synchronized, idle-adjusted input and rail differences agree across sustained prefill and decode within their uncertainty, a phase-dependent boundary problem would lose priority. A paired design can show that result. It still cannot certify absolute mains-wall accuracy without measuring that boundary.

**Cheapest night.** Use the admitted 1.7B and 8B 4-bit models: two models × two sustained phases × three repeats = twelve 600-second envelopes. Balance condition order. Each envelope brackets repeated fixed-workload prefill or decode with idle, while the KM003C and rail sampler run together. Register alignment tolerance, battery/charging state, meter calibration check and refusal rules beforehand. Estimate **incremental input joules minus incremental rail joules**, plus their ratio, by phase and model; report both boundaries and intervals. Defer bit-width because the admitted Qwen3 panel contains only 4-bit artifacts. A phase difference materially above the roughly 5 J effective bar would be worth explaining, but that bar does not certify meter accuracy. (`configs/model_panels/qwen3_4bit.json:5-17,38-50`; `docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md:46,140-144`; `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:17-18,98`.)

**Critical-path risk.** A dedicated night delays the `_v5` transaction. Uncertain sample timestamps, battery contribution, phase windows too short for alignment, or an uncalibrated meter could turn a precise ratio into an uninterpretable one. Passive co-recording on another night is useful engineering evidence, but should not silently become the B1 claim.

### Q3 — replace the headline with budgets and votes: **AMEND**

**Position and science.** Make thinking budget an explicit *policy intervention* in a staged study; do not merge it immediately with voting or promise an “energy-optimal” model. At Level 5, the draft’s illustrative ratio is 1.019 and its n=64 sampling interval is about ×/÷1.59. Changing the independent variable does not shrink that uncertainty. It does remove the hidden choice of one pilot-selected cap, and can show whether large budget changes move accuracy and energy. The current AP-5M row and packer contract fix one selected arm cap, two model roles and five levels; six budgets plus vote count would require a new registered design, not a parameter edit. (`docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:300-315,480-500,525-532`; `docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:74-86,131-160`.)

**What would change my mind?** If predeclared budget changes yield essentially the same correctness and energy frontier, while the original two-model contrast is large and reproducible, the added factor would buy little. A factorial budget study can produce that result. Six caps × models × levels without sufficient independent problems would instead produce many uncertain apparent winners.

**Cheapest informative design.** First register two thinking-cap policies, **1k and 4k tokens**, crossed with admitted **1.7B and 8B** models and MATH **Levels 1, 3 and 5**. Use **n=64 distinct, matched problems per level** across the four policies: 768 attempts. Keep a fixed, explicitly scored final-answer allowance after the thinking cap; otherwise a cap hit conflates “less thought” with “no chance to answer.” The independent variable is the assigned thinking cap. The primary estimand is total joules per attempt divided by the probability of a correct answer, **J/correct**, for each model × level × policy; report accuracy, J/attempt, cap hits and paired uncertainty alongside it. Call any winner the cheapest **among tested policies**, and leave close comparisons unresolved. This is a coarse stage, not a six-cap optimum or a one-night headline.

Test votes separately after stochastic sampling is reproducible: for one model and a selected level, compare k={1,2,4} using the **same sampled answers** sequentially and batched, with n=64 problems. The schedule contrast estimates incremental **J per voted answer**; answer accuracy and the deterministic tie rule are separate outcomes. Greedy copies would not be independent votes. The review’s B=2/4 feasibility statement does not establish k=8/16 energy or memory fit. (`docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md:117-126`; `docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:1289-1303`.)

**Critical-path risk.** This redesign interrupts AP-5M adoption and the current packer-to-reducer-to-estimator chain. Even the coarse study is many attempts; the draft budgets roughly 12 or 23 nights for its *existing* two-arm design. Cap enforcement, final-answer extraction, stochastic reproducibility and low correct counts can each make J/correct unstable. (`docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:493-500,1297-1303`; `docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:125-160`.)

### Q4 — clock, ABBA, simulations: **AMEND**

**Position and science.** Run the D-165 and claim-scale simulations now; make clock and order changes prospectively. `SystemClock.now()` returns epoch time, while `stamp()` brackets an epoch read with monotonic reads. Changing `now()` alone would put token events and existing epoch consumers on different scales. The bench record also says the present anchor cure retained 11/12 pilot captures, so removal of network-time attestation is a hypothesis to validate, not an automatic consequence. (`joulewise/clock.py:47-72`; `joulewise/adapters/mlx_runtime.py:820-835`; `docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md:9-11,20-28`.)

For a **new** block family, balance ABBA and BAAB starts by a frozen assignment. Existing `_v5` blocks are fixed ABBA under a deterministic registration; changing that family after freeze would change the experiment. Simulate D-165 using the actual corner-widened and point floors over declared repeatability and timing-width ranges, including shared-error cases. Simulate claim admission across n under null and meaningful alternatives. The floor has a one-new-observation prediction term; `claims.py` has both a floor refusal and a TOST branch, so the review’s blanket “neither TOST nor minimum effect” diagnosis is unsupported. The unresolved question is whether this floor is an appropriate claim margin for a mean contrast. (`configs/campaigns/d117_contrast_v5/generate_configs.py:204-208,1702-1722,2538-2545`; `docs/decision_log.md:10732-10753`; `joulewise/detection_floor.py:871-881,1132-1144`; `joulewise/analysis_engine/claims.py:343-382`.)

**What would change my mind?** If simulation shows D-165 has useful discrimination over plausible instrument conditions, the current dominance rule deserves to stay. If an audited monotonic-to-epoch mapping plus pilot shows no timing benefit or introduces mismatch, retain the current anchor. If BAAB starts show no relevant order sensitivity, do not spend a new pack family on them. These are testable with the proposed simulations and prospective pilot; a one-line edit cannot answer them.

**Cheapest design and risk.** No measurement night is needed for the two simulations. Use fixed seeds, the production floor and admission functions, and publish false-admission and missed-effect rates against n and timing width. Clock validation needs a small registered real pilot before dropping an attestation. The cost is a targeted code/review lane; the principal risk is corrupting timestamp meaning or retroactively changing frozen evidence.

### Q5 — review-tier rule: **AMEND**

**Position and science.** Reduce repeated review where an error cannot change a measured quantity or a claim, but define the full tier by **semantic effect**. Timing, collectors, runner scheduling, calibration, scoring, packers, reducers, estimators, admission logic and registrations can all change the result. Calling only four filenames “claim-bearing” misses that route. The existing process already distinguishes measurement-semantic and contract work from light-tier docs, while its merge gate still requires fresh oversight and final-head review; a blanket “one reviewer plus CI elsewhere” conflicts with that rule. (`docs/orchestration.md:84-99,154-167`; `joulewise/clock.py:55-72`; `docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:125-160`.)

**What would change my mind?** A prospective ledger showing that the lighter tier lets through measurement-affecting defects, or saves negligible elapsed time, would defeat it. Conversely, clean audited lower-tier changes with a real reduction in delay would support it. The proposed filename rule cannot reliably produce that comparison; an impact-based rule with recorded defect escapes can.

**Cheapest design and risk.** Cold-gate a short impact predicate and trial it on isolated documentation and non-measurement helpers, with one independent reviewer and CI. Preserve full review and lead live verification for any changed path that can alter raw evidence, estimated energy, correctness, registration or claim admission. The risk is misclassifying an indirect dependency; the existing ledger and merge requirements must be amended together if the trial becomes policy. (`docs/orchestration.md:64-71,84-99,154-167`; `.github/pull_request_template.md:1-20`.)

## (f) Order of the next three measurement nights

1. **G2-a prefill shakedown.** It selects the `_v5` prefill length from a measured sample-count rule and is the existing prerequisite to the transaction. Keep its result diagnostic. (`docs/decision_log.md:212-213,10755-10762`.)
2. **Paired 4-bit USB-C-input/rail phase night**, with the Q2 design above. It checks the energy boundary before interpreting a model contrast or expanding a scored campaign. If meter alignment or battery accounting fails at the desk, use this slot for the already planned `_v5` continuation rather than issue a B1 ratio.
3. **The registered `_v5` G2-b/transaction night**, after the G2-a pin and required desk proof. This is the shortest route to a genuine contrast under the existing design. Prepare the budget-policy pilot in the agent lane; schedule its nights after the measurement and scoring contracts are settled. A3 follows as a bounded context study if its load smoke and metrology check justify it. (`docs/decision_log.md:208,212-213,10766-10774`.)

## (g) What matters more

Define the **measurement boundary and the policy being estimated** before optimizing any headline. An input-energy discrepancy is not automatically DRAM energy; a capped answer is not automatically evidence that thinking is wasteful; and a J/correct winner near ratio 1 is not established by picking the lowest point estimate. Publish component values, calibration and alignment limits, cap-hit and scoring counts, and uncertainty with every candidate result. The paper’s adopted metrology-first direction makes a well-bounded, real measurement more valuable than a broader grid whose energy or correctness denominator cannot be interpreted. (`docs/decision_log.md:135-136`; `docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:278-315,486-500`.)

## Residual risk

I did not load a model or operate the meter. The 32k fit, KM003C calibration and latency, battery contribution, and feasible duration of the proposed scored policies remain live-gate questions; the packet likewise marks them unsettled. (`docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/06-open-facts.md:5-15`.)