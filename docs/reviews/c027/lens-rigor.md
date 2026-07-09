## A. WHAT I READ

I reviewed:

- The live project claims and status: [README.md](/Users/edr/code/JouleWise/README.md:16), [PROJECT_STATUS.md](/Users/edr/code/JouleWise/PROJECT_STATUS.md:94), [RUN_STATE.md](/Users/edr/code/JouleWise/RUN_STATE.md:55), and [TASK_QUEUE.md](/Users/edr/code/JouleWise/TASK_QUEUE.md:87).
- All of `docs/phase_1/`, including the original methodology, measurement design, and feasibility analysis.
- The governing contracts and specifications for claim levels, token normalization, contrast inference, uncertainty, detection floors, suite order, checkpointing, and observer effects—especially [measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:111), [claims_ladder.md](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md:3), [token_normalization.md](/Users/edr/code/JouleWise/docs/contracts/token_normalization.md:16), [analysis_plans.md](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:90), and [detection_floor.md](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:41).
- The controlling decision-log entries, particularly D-014 and D-052 through D-059 in [decision_log.md](/Users/edr/code/JouleWise/docs/decision_log.md:2579).
- [research_question_registry.md](/Users/edr/code/JouleWise/docs/research_question_registry.md:51) and the full research-question bank.
- The campaign-pack README and every current pack, including baseline, split-compute, prompt/scheduling, multilingual, replication, and external-meter work.
- The measurement-bearing reports in `docs/run_reports/`, especially the 2026-07-06 and 2026-07-07 Apple M3 Max runs and the 2026-07-09 rigor/status reports.
- All six tracked real-hardware bundles under `runs/`: configs, metadata, event logs, traces, summaries, and experiment manifests.
- The relevant implementation paths for powermetrics parsing, trace reduction, uncertainty gates, aggregation, campaign generation, and claim linting.

## B. FINDINGS

### 1. BLOCKER — The README’s small-model per-token range uses the wrong denominator

The README says the 1.5B run used “~77–88 mJ per generated token” [README.md:28](/Users/edr/code/JouleWise/README.md:28). The historical table’s 76.99/87.72/87.71 figures [2026-07-06 report:42](/Users/edr/code/JouleWise/docs/run_reports/2026-07-06_first_real_mlx_run.md:42) are actually `energy_token_j`, divided by all 528 prompt-plus-output tokens. The corresponding generated-output values are 79.397/90.463/90.448 mJ from `energy_output_token_j` [r1 summary:3](/Users/edr/code/JouleWise/runs/example-mac-mlx-local__r1/summary_metrics.json:3), with 512 output and 528 total tokens recorded separately [r1 metadata:99](/Users/edr/code/JouleWise/runs/example-mac-mlx-local__r1/metadata.json:99).

The approximate mean “~87 mJ/output-token” is coincidentally salvageable—the corrected mean is 86.77 mJ—but the stated range is not. Both model headlines also pair gross request energy (~47 J and ~304 J) with idle-subtracted token energy without naming that change of basis, contrary to the normalization contract [token_normalization.md:16](/Users/edr/code/JouleWise/docs/contracts/token_normalization.md:16).

**Defense objection:** “You relabeled an all-token metric as a generated-token metric and silently mixed gross and idle-subtracted quantities. Why should I trust the rest of the headline table?”

**Neutralizer:** Correct only the live claim surfaces and publish a provenance table giving formula, denominator, and gross-versus-idle-subtracted basis. Do not alter the dated run report; label it as superseded where reused.

### 2. BLOCKER — The present headline claims did not pass the machinery now advertised as governing claims

Every legacy real-hardware summary has `uncertainty: null`, including the small run [r1 summary:34](/Users/edr/code/JouleWise/runs/example-mac-mlx-local__r1/summary_metrics.json:34). The claim ladder explicitly leaves historical claims under manual review [claims_ladder.md:3](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md:3), while D-059 says the linter is structural and its forbidden-language scan remains warning-only [decision_log.md:2752](/Users/edr/code/JouleWise/docs/decision_log.md:2752). Strict bundle validation establishes evidence-path integrity, not eligibility under the later uncertainty and detection-floor rules.

**Defense objection:** “The gate system appears rigorous, but none of the numbers on your front page actually went through it. Is this ex-post methodological decoration?”

**Neutralizer:** Treat all six existing bundles explicitly as legacy L1 observations with documented waivers and incomplete modern provenance. Require subsequent claims to carry machine-readable claim level, metric basis, stack identity, contrast, uncertainty budget, floor cell, and eligibility result. That preserves the old observations without pretending they passed a later protocol.

### 3. BLOCKER — The uncertainty gate is fail-closed, but its required evidence is not yet produced end to end

The reducer correctly refuses request-level eligibility when the clock-anchor bound or drift term is absent [reduce.py:523](/Users/edr/code/JouleWise/joulewise/reduce.py:523), producing reasons such as `clock_bound_unrecorded` and `drift_term_unknown` [reduce.py:549](/Users/edr/code/JouleWise/joulewise/reduce.py:549). I found no production path populating those fields for local powermetrics bundles. The captured metadata records a derivation and a point offset, not an uncertainty bound [r1 metadata:42](/Users/edr/code/JouleWise/runs/example-mac-mlx-local__r1/metadata.json:42).

**Defense objection:** “You say P2-029’s uncertainty gates have landed, but a real production run cannot supply the evidence needed to pass them.”

**Neutralizer:** Add and exercise the production evidence path before Window A: empirically bounded sampler/marker alignment, a declared drift-bound derivation, and a shakedown assertion that eligible runs do not fail merely because required metadata was never written. Failing closed is scientifically sound; calling the path operational before this is not.

### 4. BLOCKER — Data-dependent top-ups invalidate the nominal confidence levels unless sequential inference is specified

The plans repeatedly start at `n=5` and add repetitions when an observed result is near the floor or its interval is unsatisfactory [analysis_plans.md:102](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:102), [analysis_plans.md:124](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:124), [analysis_plans.md:146](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:146). D-053 correctly freezes exact contrasts and requires direct contrast intervals [decision_log.md:2596](/Users/edr/code/JouleWise/docs/decision_log.md:2596), but it does not supply an alpha-spending or group-sequential rule.

**Defense objection:** “You keep sampling when the interval looks inconvenient and then report an ordinary 95% CI. That CI no longer has its advertised coverage.”

**Neutralizer:** Either freeze sample sizes before observing campaign effects, using Window A variance for power/MDE calculations, or pre-register a valid group-sequential design with maximum `n`, stopping boundaries, alpha spending, and multiplicity accounting.

### 5. BLOCKER — The split-compute campaign cannot yet support its central “split wins” conclusion

The Q1 estimator compares split inference with the empirical minimum of two monolithic estimates [split pack:20](/Users/edr/code/JouleWise/docs/campaign_packs/split_suite_campaign_pack.md:20). Selecting the smaller observed comparator introduces selection bias unless the selection is part of the inference. The pack also admits that composite, serialization, transfer, and deserialization detection-floor rows do not yet exist [split pack:27](/Users/edr/code/JouleWise/docs/campaign_packs/split_suite_campaign_pack.md:27), and the execution commands remain planned [split pack:343](/Users/edr/code/JouleWise/docs/campaign_packs/split_suite_campaign_pack.md:343).

**Defense objection:** “Your preferred baseline is selected after seeing the data, and you have no calibrated floor for several terms that determine the split total.”

**Neutralizer:** Test split against both predeclared monolithic references, with simultaneous adjusted contrast intervals, and call it a win only if it beats both. Land the missing floor cells and end-to-end tooling before treating this pack as capable of answering Q1–Q3.

### 6. SHOULD-FIX — Detection-floor construction is credible, but transport across stacks is not identified

P2-015 is not empty ritual: it defines condition-indexed cells, a false-effect guard, a prediction bound, and an explicit ceiling for unknown systematic terms [detection_floor.md:41](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:41). It also correctly states that the guard is not a sensor-accuracy calibration.

The remaining gap is transfer. The floor key is backend × metric × window × condition family, with a calibrated configuration pinned inside a cell [detection_floor.md:94](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:94). The 2M campaign spans radically different 1.5B and 122B operating regimes [phase_2_plan.md:642](/Users/edr/code/JouleWise/docs/phase_2/phase_2_plan.md:642), but there is not yet evidence that a floor measured at one stack/power/duration regime conservatively bounds the other.

**Defense objection:** “Why is your null-run floor portable from a short low-power workload to a long high-power model?”

**Neutralizer:** Calibrate per materially different stack/power/duration regime, or predeclare and validate a conservative transport rule using worst-case cadence, duration, drift, and observer bounds.

### 7. SHOULD-FIX — Powermetrics supports a labeled rail-proxy observation, not calibrated process energy

The project now labels the boundary reasonably: Apple’s modeled CPU+GPU+ANE rails, excluding display, storage, memory, and PSU losses [measurement_methodology.md:111](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:111). The detection-floor document also acknowledges that powermetrics is not an external wall calibration [detection_floor.md:267](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:267).

Two residual problems matter:

- It is whole-rail energy, not attribution to the benchmark process. Time-varying OS or co-resident work is not guaranteed to affect idle and load equally.
- The adapter starts its run clock only after receiving the first parsed powermetrics document [powermetrics.py:196](/Users/edr/code/JouleWise/joulewise/adapters/powermetrics.py:196), while timestamp construction advances cumulative elapsed time before assigning the first timestamp [powermetrics.py:588](/Users/edr/code/JouleWise/joulewise/adapters/powermetrics.py:588). The first interval’s relationship to the workload marker therefore needs an empirical bound, particularly for sub-second prefill.

**Defense objection:** “Strict validation proves that you consistently integrated what powermetrics emitted. It does not prove process attribution, physical calibration, or exact phase alignment.”

**Neutralizer:** Keep absolute results at L1 and call them “powermetrics-reported rail energy.” Bound marker-to-sample phase empirically, use task/process observations as contamination diagnostics, and reserve calibrated-system or cross-device efficiency claims for the external-meter bridge.

### 8. SHOULD-FIX — “Repeatable to 0.3%” overstates a three-point within-session CV

The 122B headline calls the result “repeatable to 0.3%” [PROJECT_STATUS.md:97](/Users/edr/code/JouleWise/PROJECT_STATUS.md:97). That is the sample CV of gross energy across three sequential repetitions in one warm-cache session, not instrument accuracy or repeatability over sessions, days, thermal states, or machines. Ambient conditions were not recorded, and temperature/fan telemetry was unavailable in the captured bundles.

**Defense objection:** “You measured short-run consistency three times. Where is the evidence for general repeatability?”

**Neutralizer:** State exactly: “Gross-energy sample CV was 0.3% across three sequential repetitions in one session.” Establish broader repeatability with blocked runs across sessions and thermal re-equilibration, with at least the D-014 headline count.

### 9. SHOULD-FIX — The two model points do not identify a model-size, MoE, or quantization effect

The good news is that the controlling record already concedes this. The 122B report addendum says architecture, quantization, runtime behavior, and model size are confounded [2026-07-07 report:5](/Users/edr/code/JouleWise/docs/run_reports/2026-07-07_flagship_122b_run.md:5), and the canonical registry marks active-parameter scaling as a non-claim [research_question_registry.md:56](/Users/edr/code/JouleWise/docs/research_question_registry.md:56).

This prompt’s premise that active-parameter scaling remains a live headline claim is therefore not correct under D-055. The raw configurations reinforce the point: the stacks differ in model family/architecture, quantization metadata, tokenizer, memory behavior, and warm-up policy—not merely parameter count.

**Defense objection:** “You have two highly confounded system configurations, not a controlled model-size experiment.”

**Neutralizer:** Report them as two named-stack observations only. Numerical ratios and descriptive time-versus-power decompositions are acceptable; causal claims about parameters, MoE routing, memory-boundedness, or quantization are not.

### 10. SHOULD-FIX — AP1’s claimed “extrapolation” test is an in-grid held-out interaction test

AP1 fits a categorical prompt-length × output-length model, then holds out `(512,256)` and `(4096,512)` [analysis_plans.md:102](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:102). Because both factor levels occur in the training grid, `(4096,512)` is not extrapolation in the statistical sense. It tests whether an additive/categorical model predicts a missing corner.

**Defense objection:** “Calling this extrapolation makes the result sound stronger than it is. Nothing was predicted outside the supported factor levels.”

**Neutralizer:** Call it “held-out in-grid prediction” or “interaction/additivity validation.” A genuine extrapolation claim needs an out-of-range condition and a defensible parametric functional form.

### 11. SHOULD-FIX — “Not resolvable” cannot count as successful replication

The replication pack says replication succeeds if the direction survives **or the difference is not resolvable** [replication pack:29](/Users/edr/code/JouleWise/docs/campaign_packs/replication_campaign_pack.md:29). Failure to distinguish an effect from zero is not evidence that the prior result replicated.

**Defense objection:** “An inconclusive study cannot be relabeled a successful replication.”

**Neutralizer:** Use three outcomes: replicated, contradicted, and inconclusive. If “practically equivalent” is intended, predeclare an equivalence margin and conduct an equivalence test.

### 12. SHOULD-FIX — Live prose conflicts with controlling decisions

Named decisions win, but current reader-facing prose still presents obsolete rules:

- PROJECT_STATUS says differences are claimed when marginal intervals separate [PROJECT_STATUS.md:327](/Users/edr/code/JouleWise/PROJECT_STATUS.md:327), whereas D-053 explicitly requires a direct contrast CI and forbids marginal-interval separation [decision_log.md:2606](/Users/edr/code/JouleWise/docs/decision_log.md:2606).
- PROJECT_STATUS still advertises approximately 0.03 J of prefill [PROJECT_STATUS.md:115](/Users/edr/code/JouleWise/PROJECT_STATUS.md:115), while the D-055-controlled registry says short prefill is not resolvable [research_question_registry.md:60](/Users/edr/code/JouleWise/docs/research_question_registry.md:60).
- Several methodology documents still say the contrast rule is pending ratification even though D-053 accepted it.

**Defense objection:** “Which scientific policy governs the thesis—the decision log, the status page, or the methodology?”

**Neutralizer:** Update only live/current guidance to point to the accepted decisions and canonical registry. Preserve dated historical records unchanged.

## C. MINIMAL DEFENSIBLE CLAIM SET

The strongest present-tense result that survives a hostile defense is:

> JouleWise is an auditable research prototype for boundary-labeled local-LLM energy characterization. On one Apple M3 Max system, it captured strict-valid bundles using MLX and powermetrics’ modeled CPU+GPU+ANE rails. These observations establish reproducible evidence processing, not calibrated wall energy or benchmark-process attribution.
>
> In one legacy three-repetition session, the Qwen2.5-1.5B stack averaged **47.22 J gross rail energy per request**. Its idle-subtracted mean was **44.43 J/request** and **86.77 mJ/generated output token**, but the idle estimate showed contamination and should not be the primary headline.
>
> In a separate legacy three-repetition session, the Qwen3.5-122B stack averaged **304.02 J gross rail energy per request**, **298.69 J idle-subtracted per request**, and **583.37 mJ/generated output token**. Gross-energy sample CV was **0.3% within that single session**.
>
> The two observations are named-stack measurements, not a controlled scaling experiment. They do not identify effects of parameter count, MoE architecture, quantization, tokenizer, memory behavior, or model family. Short prefill energy was below the current resolution of this measurement path and is not a quantitative result.
>
> The uncertainty, detection-floor, and campaign machinery is a credible design for stronger future L2 contrasts, but those stronger claims remain prospective until production evidence fields, fixed or sequentially valid sampling rules, and campaign-specific floor cells are exercised on real data.

The 2M campaign can support per-stack L1 baselines and potentially large, predeclared within-stack L2 shape contrasts. It cannot by itself establish a general model-scaling law, hardware ranking, or causal architecture effect.

## D. CHECKS PERFORMED

**CHECKS PERFORMED:** Static read of governing docs, decisions, code, campaign packs, reports, and all tracked real-hardware bundles; JSON/CSV/config/manifest values cross-checked with `jq` and `rg`; read-only Git status/log/diff inspected; no suite run, no hardware run, no network access, and no files changed.