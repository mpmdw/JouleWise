OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: high
reasoning summaries: none
session id: 019fdd0c-9bbb-7103-8044-ee236a0b0b6d
--------
user
PAPER-PROPOSAL DEVELOPMENT SESSION (one of a 20-direction parallel fan-out).

You are developing ONE candidate research-paper direction for the JouleWise project
into a full, reviewable proposal. Work read-mostly; do NOT create or modify any files —
your final message IS the deliverable. You may read any repo file.

== PROJECT BRIEF (state as of 2026-08-07) ==
JouleWise is Ed's undergraduate CS capstone: treating Apple's `powermetrics` software
power counter as a calibrated scientific instrument for phase-resolved (prefill vs
decode), single-request LLM inference energy on one named M3 Max stack (MLX, Qwen2.5
family, 4-bit). Core findings/machinery to date: in-window bracketed pulse-train
calibration of timing attribution; the instrument is ATTRIBUTION-LIMITED (~1 J per
phase member from ~30 ms edge uncertainty × ~33 W swings; repetition cannot average it
away), not noise-limited; detection floors composed from repeatability + worst-case
attribution + measured never-zero drift, published labelled; TWO separate claim gates
(floor clearance; interval-supported direction) with a practical ~5 J sizing bar for
phase contrasts; fail-closed collection protocol (pre-registration, admission gates,
ABBA counterbalancing, hash-bound custody chains, refusal log as evidence). MVP paper
draft is complete-in-structure (docs/paper/draft-v1.md) with demonstration values
pending. The claim path (decision D-117, adopted today): THREE fresh prospective quiet
windows — 1.5B decode floor, 7B decode floor, 1.5B-vs-7B decode contrast — each
live-bracketed under an issued calibration-acceptance regime; prefill floor cells ride
the floor windows; a 256-token prefill contrast arm is an open option (128-token
prefill contrast is MARGINAL vs the bar — custodied desk check).
Steps from here: 3 quiet-mac nights (operator bookends only) + desk work (window plans,
mint pinsets, extraction specs, regression) → mint floors → populate the paper →
capstone submission; then an ICPE-class version.

== CONTEXT AND CONSTRAINTS ==
- Advisor: Suzanne Rivoire (JouleSort co-author) — sets a real metrology bar; plain
  language required in reader-facing text.
- Venue ladder: capstone (CSCSU-class) → ICPE full research track is the realistic
  ambitious target; top-tier only if a mechanism/split research bet lands.
- Hardware: M3 Max MacBook Pro 128 GB (the instrumented unit); an RTX 3080 Ti desktop
  rig; optional Jetsons; a Yokogawa WT310E wall meter is NOT owned but may be BORROWED
  from the advisor's lab (claim C8 ratified the wall-meter axis as future work).
- Measurement economics: each claim window is a 2-4 h quiet night with operator
  bookends; effects must clear the two gates (~5 J practical sizing for phase
  contrasts on this stack; workload LENGTH is the free lever since attribution error
  is ~duration-independent).
- Ed's ORIGINAL research goals (pre-metrology-pivot, still wanted long-term):
  mechanism-level energy profiling as a third metrics axis alongside quality+latency —
  speculative decoding, multi-token prediction (MTP), mixture-of-experts (MoE)
  routing, KV/attention variants (e.g. KDA), and SPLIT/disaggregated inference across
  consumer devices; a modular harness where every experiment axis (model, inference
  technique, workload, size) is swappable; energy-honest leaderboard/reporting
  critique. Repo context worth reading: docs/strategy/2026-08-06-impressiveness-roadmap.md,
  docs/research_question_registry.md, docs/research_question_bank.md,
  docs/paper/draft-v1.md (esp. §§3-5), CLAIMS_STATUS.md, docs/decision_log.md (D-117,
  at end of file).

== YOUR DELIVERABLE (final message, markdown, ~600-1200 words) ==
1. TITLE + one-sentence thesis.
2. PROJECT-BRIEF-AND-STEPS paragraph: half a page restating the current project state
   and the concrete steps from today to THIS paper (audience: Ed deciding what to
   fund with nights/desk time).
3. CONTRIBUTIONS (3-5, numbered, each falsifiable).
4. EXPERIMENT PLAN sized against the instrument: cells, contrasts, expected effect
   magnitudes vs the ~5 J sizing bar (estimate from public knowledge + repo
   diagnostics you can find; state which effects might NOT clear and what the refusal
   would mean), number of quiet windows needed, desk-work list, any new harness
   capability required (and whether it violates the frozen single-request boundary).
5. HARDWARE/INSTRUMENT needs (owned / borrowed / new; wall-meter dependency yes/no).
6. VENUE fit + why (capstone chapter? ICPE? workshop?), and how it BUILDS ON the MVP
   paper (shared method sections, what's new).
7. RISKS + KILL CRITERIA (what desk evidence would kill it before spending a night).
8. RELATION TO ED'S ORIGINAL GOALS: which original axis it serves, or state plainly
   that it does not.
Be concrete and quantitative wherever possible; flag every number you are unsure of.

== HARD CONSTRAINT (Ed, binding) ==
Every proposal MUST turn the EXISTING material into a solid scientific paper: the
calibrated instrument and its custody/fail-closed protocol machinery, the
attribution-limited finding, the banked diagnostics, the data the three D-117 windows
will produce (decode floors for 1.5B and 7B, prefill floor riders, the decode
contrast), and modest extensions collectible on the owned hardware under the SAME
instrument discipline. Do NOT propose work that abandons the instrument or needs
apparatus/data without a concrete path (the borrowed WT310E wall meter is allowed
where justified as an extension of existing material). If your assigned direction
cannot honestly be built from existing material, SAY SO PLAINLY and shrink it to the
version that can — a smaller honest paper beats an unmoored ambitious one.

== REQUIRED READING (read these in the repo before writing anything) ==
docs/paper/draft-v1.md (the whole draft — every proposal must state what it reuses
from it); CLAIMS_STATUS.md; the D-117 entry at the end of docs/decision_log.md;
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md (exactly what the three
windows produce, budgets, mint machinery); docs/strategy/2026-08-06-impressiveness-roadmap.md;
docs/research_question_registry.md; docs/research_question_bank.md;
docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md.

== YOUR ASSIGNED DIRECTION (mvp-icpe-upgrade) ==
The MVP metrology paper upgraded to an ICPE full-research-track submission: what additional experiments, characterization, and framing turn the capstone into a full paper. Be specific about the delta.

codex
I’ll read the full required evidence set, then shape this as the smallest credible ICPE upgrade—explicitly budgeting every additional quiet window and separating must-have evidence from optional ambition. I’ll make no file changes.
exec
/bin/zsh -lc 'git status --short --branch && wc -l docs/paper/draft-v1.md CLAIMS_STATUS.md docs/decision_log.md docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md docs/strategy/2026-08-06-impressiveness-roadmap.md docs/research_question_registry.md docs/research_question_bank.md docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## main...origin/main
     194 docs/paper/draft-v1.md
     179 CLAIMS_STATUS.md
    7566 docs/decision_log.md
     489 docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md
     214 docs/strategy/2026-08-06-impressiveness-roadmap.md
     134 docs/research_question_registry.md
    1095 docs/research_question_bank.md
      33 docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md
    9904 total

exec
/bin/zsh -lc "sed -n '1,260p' docs/paper/draft-v1.md
sed -n '1,240p' CLAIMS_STATUS.md
sed -n '7520,7585p' docs/decision_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# JouleWise: Detection Floors for LLM Inference Energy Measurement on Consumer Silicon

## 1. Introduction

Energy numbers for large language model (LLM) inference now appear in leaderboards, systems papers, product comparisons, and policy debates. Published estimates for apparently similar queries can differ by an order of magnitude, yet the numbers are rarely accompanied by an error bar that says how small a difference the measurement method can actually distinguish. This omission is especially consequential on consumer hardware. Apple's `powermetrics` utility makes processor power estimates available without a laboratory meter and is therefore attractive for repeated experiments, but, to our knowledge, it has not been validated in published work as an instrument for separating the energy of LLM inference phases. Apple describes its outputs as estimates; treating them as exact readings can turn timing uncertainty at a phase boundary into a spurious energy difference.

The core difficulty is physical as much as statistical. Energy is the integral of power over time. An experiment may repeat consistently and still assign energy to the wrong phase if a power sample near the boundary between prompt processing and token generation is placed on the wrong side. Averaging more repetitions reduces random scatter but does not remove that attribution error. Slow changes in thermal or background state can add a second false difference over a long collection session.

We argue that a software power counter should be treated as a scientific instrument rather than as a logging convenience. The instrument must be calibrated in the same session in which it is used; each reported result must carry a detection floor, meaning the smallest false effect that the calibrated method could plausibly produce under the stated conditions; and the analysis must decline a directional claim when the observed effect cannot clear that floor and its own measurement uncertainty. JouleWise implements this discipline for phase-resolved, single-request LLM inference on one named Apple-silicon machine and software stack. The runtime emits the phase boundaries because it drives the workload, while `powermetrics` supplies the power samples integrated between those boundaries.

This scope is deliberately narrow. A measurement characterizes one physical unit, operating-system build, runtime and library stack, model artifact, quantization, tokenizer, sampling policy, single-request execution policy, telemetry backend, and measurement boundary. It does not establish that an Apple hardware class or vendor is more efficient than another platform. Without an external power meter, absolute values remain internal to the named `powermetrics` system-on-chip boundary; same-boundary contrasts can still be scientifically useful when they pass the calibration and floor gates. Gross joules per request are the primary energy metric. Joules per prompt or output token are tokenizer-scoped companion metrics and are never treated as tokenizer-independent work units.

This paper makes the following contributions:

1. (C-i) an in-window calibration method that measures timing-attribution error for phase-resolved energy integration;
2. (C-ii) detection floors composed from measured repeatability, worst-case attribution, and measured drift — published with every result;
3. (C-iii) a fail-closed collection protocol (admission gates, ABBA ordering, custody chains, pre-registration) with its refusal log as evidence;
4. (C-iv) full instrument characterization: linearity, null response across magnitudes, empirical floor verification, phase-attribution causal consistency, drift/settle;
5. (C-v) demonstration measurements: phase-resolved J/token for two model sizes with a pre-registered contrast [+ quantization ladder if window budget allows];
6. (C-vi) open tool + hash-bound reproducible artifacts.

## 2. Background and the gap

### Energy-benchmarking rules

The first relevant lineage is formal energy benchmarking. MLPerf Power and the associated Standard Performance Evaluation Corporation methodology treat uncertainty and validity as properties of each measured run. They require a qualified analyzer, uncertainty evaluated at the observed load, fixed measurement ranges, synchronized clocks, sufficiently long intervals, invalid-sample accounting, and explicit treatment of battery-backed systems [MLPerfPower]. These rules establish an important principle: a benchmark result is not valid merely because the meter has a specification sheet. The evidence recorded during the run must show that the measurement operated inside its accepted conditions. These standards, however, assume external instruments and data-center-style workloads; they do not provide a method for validating phase boundaries reported by a software counter on a consumer system.

### Software-counter validation

The second lineage validates software-visible energy counters against external power. Intel's Running Average Power Limit (RAPL) counters have been studied through lag alignment, regression against wall power, counter-resolution tests, sampler-overhead audits, and thermal controls [RAPLInAction]. Jay and Ostapenco's CCGRID 2023 study likewise shows that the gap between a software meter and wall power can depend on load rather than behave as one fixed offset, and it refrains from component-level conclusions when no reference instrument observes the component [JayOstapenco]. This work provides a strong model for whole-machine scale validation. It does not define a detection limit for a reported effect, does not validate `powermetrics` on Apple silicon, and cannot by itself establish whether software samples were assigned to the correct LLM phase. A wall meter observes a total; phase attribution needs a separate timing experiment.

### LLM energy studies

The third lineage measures LLM energy across models, hardware, and workloads. TokenPowerBench reports prompt-processing and token-generation energy with phase-appropriate token denominators; ML.ENERGY, Silicon Showdown, and Intelligence-per-Watt broaden empirical coverage across deployed systems [TokenPowerBench; MLENERGY; SiliconShowdown; IntelligencePerWatt]. This breadth makes inference energy visible, but the nearest studies do not jointly characterize counter timing, repeatability, drift, and the minimum resolvable effect. Phase labels are consequently easy to read as exact even when the method does not report the boundary events, alignment uncertainty, or a floor below which a difference should be refused.

The specific gap is therefore not another energy table. To our knowledge, no published work combines phase-resolved LLM energy on consumer silicon, a per-measurement error budget, and validation of `powermetrics` timing attribution under its named measurement boundary (as distinct from validating its absolute counter gain or whole-system energy scale, which would require an external meter). JouleWise fills that gap by making instrument characterization and refusal behavior the primary result; model comparisons are demonstrations of what the characterized instrument can and cannot resolve.

## 3. In-window calibration method (C-i)

### Measurement model and boundary

JouleWise measures one sequential request at a time. Prompt processing (often called *prefill*) converts the input sequence into the model's internal state; token generation (often called *decode*) produces output tokens from that state. Because the experiment controls the runtime, it records the start and stop of these phases directly in the runtime event stream rather than inferring them from shapes in the power trace. The reducer then integrates the named `powermetrics` system-on-chip power channels between each pair of phase events using trapezoidal integration.

The runtime and the telemetry sampler do not share a perfect clock. Operating-system launch latency, timestamp anchoring, and the sampler's averaging behavior can shift an apparent edge. A phase-energy estimate must therefore be an interval, not only a point. The calibration asks a concrete question: if software commands a load pulse at a known time, how far can the rising and falling edges of that pulse appear displaced in the sampled power trace?

### Bracketed pulse-train calibration

Immediately before and after every claim-bearing collection window—that is, a window eligible to support a reader-facing scientific claim—JouleWise runs a fresh pulse-train calibration under the same machine, operating-system, power-supply, and telemetry state as the science workload. The current protocol commands 59 graphics-processor matrix-multiplication pulses. Their durations are fixed in advance, their gaps follow a deterministic low-discrepancy schedule rather than a single repeated period, and quiet baselines of at least 4.5 seconds separate the fitted regions. The varied schedule reduces the risk that the calibration accidentally locks to the telemetry sampler's cadence. The 59-pulse design supports the pre-registered nonparametric 95/95 bound: a conservative bound intended to cover at least 95% of the calibration population with 95% confidence under the stated transfer assumptions.

For each pulse, the estimator compares the commanded interval with the observed power plateau and fits the start-edge and stop-edge lags independently. This distinction matters. A common shift of both edges may leave pulse energy nearly unchanged, while an early start combined with a late stop can add energy at both boundaries. The calibration therefore retains a bound for the instrument's edge-placement error rather than collapsing the evidence to one best-fit lag.

Each science member, meaning one recorded workload run, also carries a local bound on how its runtime clock is anchored to the trace, including the observed span between wall time and a monotonic clock that is not adjusted by network synchronization. For a reported phase, the analysis combines the member-local common shift, the calibration edge bound, and the clock-span term. It evaluates the energy integral at all four combinations of early and late start and stop edges, while scanning the allowed common shift exactly. The minimum and maximum of those integrals form the admissible energy interval. The physical intuition is simple: the interval asks how much energy could move into or out of the phase if both boundaries were placed at their most adverse calibrated positions.

The pre- and post-window calibrations form a bracket around the measurements. Both must be authenticated, fresh, and causally outside the science interval. The operative bound is the larger of the two. Separately, the absolute difference between the pre- and post-window calibrations is screened against a derived bracket-drift limit of about 10.82 ms: a small repeatability-only excess is propagated into every floor and claim, while an identified systematic defect cannot be absorbed by that budget. If the post-window bound is larger than the one used when a member was first reduced, the member must be re-reduced through the pre-specified path with the wider bound or it cannot support a claim; metadata is never patched to make the bounds agree. A pre-flight level screen also runs before the first science member. It rejects a calibration whose fitted lag is outside the previously characterized family, such as a graphics-processor frequency ramp that the pulse model could mistake for a timing shift. A retry is allowed only after a specific cause is identified and removed, within the retry count frozen before collection. Repeating merely until a favorable calibration appears would be selection on the outcome.

This procedure validates timing attribution, not the gain of the power counter. The pulses are graphics-processor matrix multiplications under a relatively light central-processor load, so transfer of their timing bound to sustained mixed-load inference is an explicit assumption. The in-session bracket, empirical floor probes in Section 6, and stack-specific labels constrain that assumption; only an external meter could additionally validate the absolute whole-system scale.

## 4. Detection-floor composition (C-ii)

A *detection floor* is a practical guard against false observed effects for one declared condition family: the same telemetry backend, metric, window type, workload profile, and stack identity. One such family forms a measurement cell. The floor is not a claim that a population percentile has been estimated exactly. JouleWise computes separate absolute and comparative floors and takes their maximum for the cell. An absolute floor measures how far repeated measurements of the same condition wander from their mean. A comparative floor measures the apparent difference between labels that are deliberately made identical and collected in A/B/B/A order.

### Repeatability and false-comparison guards

For an absolute cell with energies \(E_i\), residuals \(r_i=E_i-\bar E\), sample standard deviation \(s_r\), and \(n\) valid bundles, the point guard is

\[
F_{\mathrm{abs,point}}=\max\left(\max_i |r_i|,
t_{0.975,n-1}s_r\sqrt{1+1/n}\right).
\]

For \(n\) valid null-comparison blocks with within-block deltas \(\delta_i\), the corresponding guard is

\[
F_{\mathrm{cmp,point}}=\max\left(\max_i |\delta_i|,
|\bar\delta|+t_{0.975,n-1}s_\delta\sqrt{1+1/n}\right).
\]

The observed maximum protects against a false effect already seen; the Student-*t* prediction term protects against one additional observation under the repeatability model. Small samples receive a pre-registered guard factor, and fewer than five valid bundles or blocks are treated only as development evidence, not as a claim gate. Items within one bundle are not counted as independent repetitions.

### Worst-case timing attribution

Point repeatability is not the full floor. Each energy value is an interval from the timing calibration in Section 3. The floor computation evaluates the complete point-floor estimator over the joint corners of all member intervals that pass the admission and evidence gates, then takes the largest value. For a null A/B/B/A block, the four signed member intervals are propagated through the contrast together. This corner calculation is deliberately conservative: a systematic boundary-placement error is not independent Gaussian noise, so adding it in root-sum-square form would understate the worst case. The published floor is no smaller than the largest accepted attribution width.

This calculation revealed a stable and important limitation of the present instrument. Ordinary repeatability is smaller than the uncertainty caused by placing samples at phase edges: approximately one joule can be assigned to the wrong phase when a roughly 30 ms timing uncertainty meets a power change of roughly 33 W. The instrument is therefore *attribution-limited*, not *noise-limited*. More repetitions can refine the repeatability term, but they cannot average away this boundary-placement limit.

### Measured, never-zero drift allowance

Drift is a slow change in the machine or measurement response over the collection window. It is measured rather than assumed away. Each prospective window includes three fixed reference runs at the start, one at the midpoint, and three at the end. Gross energy and idle-subtracted energy are treated as separate claim families (idle-subtracted energy is gross energy minus the measured idle mean power multiplied by the phase duration). For each family, the protocol derives a repeatability bound from a settled reference corpus and measures the largest excursion among the start mean, midpoint, and end mean. The allowance is

\[
A_{\mathrm{drift}}=\max(\text{observed start/mid/end excursion},
\text{derived reference-repeatability bound}).
\]

Consequently, a passing drift screen never means zero drift. The allowance remains positive even in an exceptionally stable window, and the midpoint protects against an interior excursion that similar endpoints would miss. No duration-scaling law is applied because the available evidence does not identify a physical law relating drift to elapsed time.

For each absolute or comparative component, the guarded, corner-widened value is increased once by its matching drift allowance. The operative floor for a cell is then

\[
F_{\mathrm{cell}}=\max(F_{\mathrm{abs}},F_{\mathrm{cmp}}),
\]

not their sum. Cross-window components keep their own calibration basis and allowance; an allowance is never added again at the cell or reporting level. Operative floor values and their full decomposition for each demonstration stack are withheld here until the corrected artifacts are issued: **[RESULT PENDING RE-MINT]**.

### LABELLED publication and the effective decision bar

When timing attribution dominates, the floor remains publishable only through the **LABELLED** path. Every artifact and reader-facing result must identify the limit as attribution-limited, publish the corner-widened value rather than the smaller point diagnostic, retain the point-only repeatability number as a non-publishing diagnostic, and carry `floor_source = E_clock_anchor_shift_bound_j`. This field names energy uncertainty caused by shifting the phase edges within the calibrated clock-anchor bound as the dominant term. The label prevents a precise repeatability number from masquerading as the instrument's total resolving power.

The floor is only one side of a claim decision. The calibrated floor bounds a false effect produced by the calibration condition; the confidence or decision interval for the particular measured contrast separately carries that contrast's timing-attribution uncertainty. These are distinct uses of the same physical uncertainty and both are required. The effective bar is therefore

\[
\text{effective clearable effect}=F_{\mathrm{cell}}+B_{\mathrm{claim}},
\]

where \(B_{\mathrm{claim}}\) is the claim-side measurement bound. For the measured phase-contrast regime, this combined bar is approximately 5 J. Neither term may be removed as an apparent double count. Effects below the floor are reported as *not resolvable*, not as zero, equal, or evidence of no difference. A directional claim is made only when the effect and its interval clear the applicable bar.

## 5. Fail-closed collection protocol (C-iii)

*Fail-closed* means that missing, inconsistent, stale, or contaminated evidence produces a refusal rather than an optimistic default. The collection unit is one uninterrupted two-to-four-hour window with one power state, one instrument identity, fresh calibration before and after, a fresh drift-bound corpus, and one verdict over the exact member set. Work that does not fit with at least a 20% failure margin is split prospectively into another independently calibrated window.

### Pre-registration and admission

Before quiet time, the operator freezes the run identifiers, membership, stage order, comparison definitions, calibration retry count, acceptance thresholds, extraction specification, code revision, and an initially empty waiver list. Every configuration is validated and dry-run against a fresh output root. These choices are made before outcomes are visible. Pre-registration here is executable: the launcher and final verifier check the frozen values rather than relying on a narrative promise.

Each stage then passes admission gates immediately before measurement. The approved power supply and power policy must be unchanged; displays must be asleep; the screensaver and low-power mode must be off; thermal pressure must be nominal; and central- and graphics-processor activity must meet the quiet-state criteria. Known background work is allowed to finish before the window, followed by a settling interval, rather than being ignored during analysis. Runtime and telemetry identities, clock anchoring, sample cadence, calibration freshness, and post-run environment observations are also checked. No environment override can produce a claim-bearing member.

### Counterbalanced order

Comparisons use A/B/B/A blocks, abbreviated **ABBA**. Conditions A and B are measured in the order A, B, B, A, with ordinary cooldown between members. Averaging the two outer A observations and the two inner B observations cancels a linear time trend within the block to first order. For null-floor calibration, A and B are aliases of the exact same configuration and payload, so any nonzero block delta is a false comparative effect. For scientific contrasts, the A and B definitions are frozen in advance, and the contrast is computed within each block before blocks are aggregated. ABBA reduces common drift; it does not replace the measured whole-window drift allowance.

### Evidence custody and refusals

Every member is a self-contained bundle of configuration, raw power trace, runtime events, environment observations, and derived summary. Cryptographic hashes bind those files to the campaign manifest. Failed or interrupted artifacts are never deleted or overwritten. An occupied retry slot is moved to a quarantine area outside the active runs root; the exact member is recollected only under an allowed retry; and an append-only supersession record names which occurrence governs. Two present bundles for one occurrence refuse. The final whole-window verdict binds the exact member-occurrence set, calibration bracket, policy, and drift evidence by hash, so a later consumer cannot silently select a more favorable subset.

Collection does not continue indefinitely through environmental interruptions. Each stage attempt stops at its first member failure, and after the same cause fails a window stage for the third time the window itself closes rather than being retried; in actual operation, nights with three environmental member interruptions were closed and preserved as salvage rather than repeatedly retried. The surviving data may remain diagnostic, but it becomes claim-bearing only if the pre-registered verdict and extraction rules accept the exact resulting basis. This abandon-after-three rule limits outcome-dependent retrying and makes the cost of a noisy environment visible.

The custody chain continues after collection. The immutable corpus is backed up before extraction. The extractor re-authenticates member hashes, required files and cross-file consistency, calibration identity, environment admission, complete campaign membership, cooldown evidence, phase metric identity, and the whole-window drift allowance. It excludes or refuses a cell according to the frozen rules; missing uncertainty never becomes zero. The current artifact boundary is stated honestly: until floor artifacts are independently bound to their source extraction, a claim-bearing floor must be produced by protocol-controlled extraction in the same controlled custody session as the analysis that consumes it. A standalone floor file is not independently claim-licensing.

The refusal log is part of the evaluation, not an embarrassment to omit. It records contaminated members, out-of-family calibration, stale drift evidence, unresolved clock anchors, duplicate occurrences, and below-floor effects. In one real end-of-night case, the governed re-evaluation refused a window because a member's internal clock alignment could not be resolved. Independent adjudication found that refusal correct. The result remained non-claim-bearing: an example of the fail-closed design working as intended, not a software defect to be bypassed.

## 6. Instrument characterization (C-iv)

Instrument characterization asks whether the complete measurement system behaves predictably when driven by signals whose qualitative answer is known in advance. The workload is therefore a test signal, not yet the scientific finding. All tests retain the same calibration, admission, custody, and floor rules as the later demonstration measurements. Existing campaign fragments are not promoted where the governing whole-window verdict did not pass; the table marks the required claim-bearing results explicitly.

| Property | Characterization method | What a passing result would establish | Claim-bearing result |
|---|---|---|---|
| Linearity | Hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. Regress gross request and decode energy on the runtime-observed output count; inspect residual structure as well as the fitted slope. | Energy responds proportionally over the tested dynamic range, and the fitted per-token slope can serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
| Null response across magnitudes | Run identical A-equals-B ABBA blocks at short, medium, and long output magnitudes. Evaluate the paired deltas against zero and against the predicted decision envelopes. | The comparison path does not create a directional effect merely because total energy or duration changes, and false contrasts across the tested range are contained by the error model. A non-significant result alone is insufficient; the interval must be interpreted relative to the floor. | **[PENDING WINDOW C]** |
| Empirical floor verification | Use the pre-registered linearity slope to create micro-deltas with predicted effects near 0.5, 1, 1.5, and 3 times the declared floor. Test positive and negative directions in counterbalanced blocks. | Sub-floor effects are refused while sufficiently super-floor effects clear in both directions. This is an operational check of the detection boundary, not a validation of the counter's absolute gain. | **[PENDING WINDOW C]** |
| Phase-attribution causal consistency | First compare the sum of separately integrated phase energies with the gross energy over their enclosing request. Then vary output length while holding prompt tokens fixed and fit the slope of prefill energy against output length. | Phase accounting is additive within its stated boundaries, and energy assigned to prefill does not acquire a systematic dependence on work that occurs later in decode. Together these tests challenge both missing energy and cross-phase leakage. | **[PENDING WINDOW C]** |
| Drift and settling | Place long controlled holds and fixed reference workloads through the window, including start, midpoint, and end references. After operator or stage activity, repeat the reference while recording the time required for thermal and admission observables to stabilize; compare it with the 180 s operating convention. | The measured drift trajectory is contained by the published allowance, and the chosen settling time is supported or revised from observed recovery rather than convenience. Endpoint agreement alone is not enough if the midpoint reveals curvature. | **[PENDING WINDOW C]** |
| Between-session stability | Repeat calibrations, null blocks, and floor cells across at least three sessions or days with the full stack identity recorded. | The calibration and floor are stable enough to reuse only under their declared freshness and identity rules, or reveal that a new session must mint a new floor. | **[PENDING WINDOW C]** |

Linearity and the null ladder test complementary failure modes. A smooth response can still carry an offset, and a zero-centered null can coexist with a nonlinear scale. The micro-delta experiment then closes the loop by using the measured slope to place effects deliberately below and above the declared decision boundary. Success requires the instrument to refuse the former and resolve the latter in both directions; merely observing larger effects with larger workloads is not sufficient.

The causal tests address the most important phase-specific risk. Additivity checks conservation inside the declared request boundary: phase intervals should reconcile with the enclosing total, subject to explicitly labeled setup or gap intervals. Causal invariance checks direction: holding the prompt fixed while increasing later decode work should not change energy attributed to earlier prefill. A nonzero prefill slope would indicate boundary leakage, shared-state coupling that invalidates the simple phase model, or both; it would narrow the claim rather than be explained away.

Temporal characterization separates slow drift from thermal settling. Start, midpoint, and end references expose whole-window curvature, while post-transition references estimate how long the system takes to return to its admitted state after operator activity or stage churn. Repetition across days tests whether one session's calibration is representative under identical recorded bindings. Internal channel-sum versus package reconciliation is retained as a secondary consistency check. External wall-power regression remains conditional on a suitable meter and would validate totals only; the pulse experiment remains the evidence for phase splitting.

Every resulting figure and table will identify the physical unit, operating-system version and build, runtime and relevant library versions, model artifact hash, quantization, tokenizer identity, sampler and output policy, configured and realized batch/concurrency policy, measurement boundary, and telemetry backend. Silent omission is not permitted. Measurements support stack-specific conclusions only; independent replication or a calibrated boundary bridge would be required for hardware-class, vendor-class, or cross-boundary rankings.

## 7. Demonstration results (C-v)

**[RESULT PENDING RE-MINT]**

This section will report phase-resolved gross joules per request for two model sizes, with tokenizer-scoped joules per prompt token and per output token as companion metrics. It will contain the pre-registered same-boundary model-size contrast, its interval, the complete floor decomposition, the claim-side bound, the effect-to-floor ratio, and the final resolvable/unresolved verdict. No demonstration energy value from the superseded mint is carried into this draft. A quantization ladder will be included only if it is collected under its own stack-specific floors and the frozen window budget permits it.

## 8. Related work

### LLM inference energy measurement

TokenPowerBench provides one of the closest reporting structures: it separates prompt-processing and token-generation energy, uses phase-appropriate token denominators, and groups results by context length [TokenPowerBench]. Its disclosed method, however, does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline, or external validation, and continuous batching makes an “active phase” label difficult to interpret when requests overlap. JouleWise adopts phase-specific reporting but restricts its primary scope to one sequential request, where runtime-emitted phase boundaries are well posed and can be calibrated.

The Illusion of Power Capping in LLM Decode samples graphics-processor power, integrates those samples, repeats configurations, and cross-checks sufficiently long operations against a separate hardware energy counter [IllusionPowerCapping]. This is a stronger measurement template than an unqualified software reading. Its counter agreement, run-to-run variation, snapshot fallback, and timing alignment nevertheless remain separate diagnostics rather than one bound on the reported effect, and its long sweeps do not use a drift-control ordering. JouleWise composes those classes of uncertainty into a decision rule for each contrast.

Apple-focused system comparisons reinforce the need for boundary labels. Silicon Showdown compares a graphics-board boundary on one platform with a whole-system-on-chip `powermetrics` boundary on Apple hardware, while runtimes and precision stacks also differ [SiliconShowdown]. Intelligence-per-Watt and ML.ENERGY similarly emphasize breadth across deployed inference configurations [IntelligencePerWatt; MLENERGY]. Such studies answer valuable systems questions, but unlike boundaries and software stacks cannot by themselves support a hardware-class causal ranking. JouleWise therefore makes the named stack and measurement boundary part of every result and prioritizes within-boundary effects.

### Software power counters and measurement standards

RAPL in Action established a validation agenda for commodity software counters: align lag before comparing streams, model wall power rather than assuming identity, account for temporal correlation, warm the system, measure sampler overhead, and inspect update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. Jay and Ostapenco likewise regress software readings against wall power and show that disagreement varies with load; they avoid claims about subtotals that the reference meter cannot observe [JayOstapenco]. JouleWise follows this epistemic boundary. A future external meter could test total gain and load dependence, but it would not validate how a total is divided between prefill and decode. The in-window pulse train addresses that distinct question.

MLPerf Power and SPEC require load-specific analyzer uncertainty, fixed ranges, clock synchronization, minimum intervals, invalid-sample accounting, and controlled battery behavior [MLPerfPower]. JouleWise translates their per-run reject-on-missing-evidence principle to a consumer software counter. The difference is that its principal uncertainty is not only an analyzer specification; it includes whether samples at a software-defined phase edge belong inside or outside the integral.

### Metrology and experimental discipline

Prospective paired minimum-detectable-effect methods estimate the smallest effect a planned paired study has adequate statistical power to find. They size the study from the variance of paired differences and can impose a one-way prior ratchet: observed variability may raise the planned threshold but may not lower it after outcomes are seen [PairedMDE]. JouleWise uses that logic for prospective workload sizing, but it does not treat the worst-case attribution term as independent random noise. Root-sum-square composition would be anti-conservative for a systematic edge-placement bound. Instead, the analysis maximizes over calibrated edge positions, measures drift with bracketed references, and publishes the resulting floor with the effect.

This emphasis changes the role of failed runs. A rejected admission, stale calibration, contaminated member, or below-floor contrast is evidence about the instrument's operating domain. Hash-bound raw traces, runtime events, configurations, supersessions, verdicts, and pre-registration records make that evidence re-reducible. The refusal is retained rather than disappearing behind a final average.

### Split and disaggregated inference

Split, or disaggregated, inference places prompt processing and token generation on different devices and transfers intermediate state between them. Revisiting Disaggregation Energy reports that the energy outcome depends on load, baseline, and transfer conditions on its evaluated two-graphics-processor node [RevisitingDisaggregationEnergy]. DualScale studies phase placement and per-phase power control on homogeneous server hardware [DualScale]. Prima.cpp includes whole-run energy and communication accounting but not a per-stage energy split [PrimaCPP], while SplitZip characterizes lossless transfer compression without making an energy claim [SplitZip].

JouleWise does not claim a new split scheduler in this paper. Split inference is instead a demanding future demonstration of the instrument because it introduces two physical boundaries, a transfer interval, and clock alignment across devices. A valid comparison would have to measure both ends, name each boundary, and clear a pre-registered floor or calibrated bridge. Whether splitting saves energy remains an empirical outcome; the reusable contribution is a method that can issue, qualify, or refuse the result.
# Claims Status

**The single standing home for "what can we actually claim right now."**
Every scientific number the project can publish, is holding, or must not
repeat — with its exact validity state and blocker. Refresh this file
whenever claim-bearing state changes (a verdict, a mint, a merge in the
D-095 chain, an adjudication); quote verdicts as issued, never
reinterpreted. Companion docs: `RUN_STATE.md` (session pointer),
`WINDOW_STATUS.md` (machine state), `docs/decision_log.md` (policy).

Last updated: **2026-08-07** (D-117: the historical re-mint path is
SUPERSEDED — structurally closed at main after the D-116 issuance
(candidate discovery excludes import-marked receipts by design); the
claim path forward is THREE PROSPECTIVE WINDOWS — fresh 1.5B decode
floor, fresh 7B decode floor, fresh decode contrast — live-bracketed
under the issued acceptance regime, with prefill floor cells riding
both floor windows. Prior "re-mint conditions" in this file are
historical: D-109 landed (PR #100), issuance executed (D-116, PR #109),
validator pin widening landed (PR #105). Full record:
`docs/process_traces/2026-08-06-d110-remint-fork/`.)

Earlier header (2026-08-03 night, for the record): D-108/D-109 ruled +
executed; D-110 made mint #1 retroactively NON-CLAIM-BEARING; window B
re-evaluation STOPPED → D-112; mint-1 re-derivability proven
byte-identical; report: `docs/run_reports/2026-08-03-16h-runway.md`.

---

## 1. VALID — minted, mainline, citable

**NONE at this checkpoint.** D-110 (2026-08-03, sweep finding RT-1)
made mint #1 and every number derived from it retroactively
non-claim-bearing: its floors embed a never-zero allowance of ZERO
where D-102 pin 3 mandates +max(drift, 0.010818 s) (~+43% on the a10
operative bound). The previously-listed values (operative 7.377086 J;
a10 components 3.823787 / 3.592138 J; window C comparative 7.377086 J)
move to §5 until the re-mint. The DERIVATION toolchain itself is
proven honest: the full pinned replay (2026-08-03) reproduced both
extraction reports, the artifact, and the statement BYTE-IDENTICAL
(`docs/process_traces/2026-08-03-q1-remint-bytecompare/`). The taint is
semantic (the selector the era used), not derivational.
**2026-08-07 (D-117):** the historical re-mint order is SUPERSEDED —
all three former re-mint conditions completed (D-109 via PR #100;
issuance via D-116/PR #109; pin widening via PR #105) and the FIRST
consumption attempt then proved historical consumption structurally
closed at main. Replacement: three prospective windows (D-117 cl.2);
the never-zero allowance correction binds their mints. All four PASSED
window verdicts remain untainted (sweep RT-5), but pre-genesis windows
CANNOT be claim-consumed — their role is diagnostic and
rule-establishing only.

**Standing measurement fact (D-078 cl.11, Ed-ratified):** the instrument
is attribution-limited (~1 J), not noise-limited (~0.3 J). Floors
publish LABELLED with the widened number; the effective clearable
effect for phase contrasts is floor + claim-side bound ≈ 5 J. No
instrument-tightening program.

## 2. EVIDENCE-BEARING — collected and verdict-PASSED, awaiting a specific gate

| Candidate claim | Value (prose-only until gated) | Window / verdict | Blocker |
|---|---|---|---|
| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
| **1.5B-vs-7B decode contrast** (demonstration study #1) | **Registered claim metric (frozen v3 manifest): `phase_energy_j.decode`, 7B−1.5B = 141.29 J per block.** The widely-quoted 146.730349 J (σ 0.241 J, n=10 ABBA) is the `idle_subtracted_energy_j` whole-request DIAGNOSTIC — quote it only labelled as such, never as the claim (sweep DC-1; both reproduce byte-exactly from disk). | `window_contrast_20260730`, **PASSED** | **RE-SCOPED by D-117 (2026-08-07):** `window_contrast_20260730` is pre-genesis and cannot be claim-consumed; values are DIAGNOSTIC and the design template for the fresh contrast window (D-117 cl.2). The D-095 chain now runs through the prospective windows' mints. |

## 3. COLLECTED — verdicts FAILED as-issued; adjudication RULED (D-100, 2026-08-01)

The machinery adjudication is complete (MET-VERDICT-ADJ-01 → D-100 cold-
gate synthesis). Both verdicts **stand as issued, permanently by
construction**: any licensed re-evaluation appends a NEW row under
`consumption_semantics_id: salvage_dangler_exclusion_v1` with a new
pinned basis; the original FAILED rows are never edited and govern
default consumption. Outcomes per window:

- **Window A: permanently non-claim-bearing.** Its only post-cal retry
  binds a T1-incompatible power-policy identity (immutable evidence; the
  machinery's rejection was CORRECT), so no calibration bracket can ever
  form. C1 re-collects in a future window.
- **Window B: TERMINALLY CLAIM-RETIRED (D-113, Ed ruling 2026-08-05):
  RETAINED_IMMUTABLE / PERMANENTLY_NON_CLAIM_BEARING.** Ed chose
  abandonment over salvage ("soundness and quality of the project and
  claims above all"): no re-evaluation or claim consumption will ever
  occur; the WB-specific D-100/D-106/D-108 license chain is retired
  (general machinery survives for other windows);
  `WINB-R06-DISPOSITION-01` closes ABANDONED_FOR_FRESH_COLLECTION;
  labelled read-only forensic/diagnostic use remains permitted ("Window
  B, original verdict FAILED, D-113 claim-retired, non-claim
  evidence"). Every still-desired WB claim component re-collects fresh
  beginning Window C — no WB member enters a replacement claim basis.
  The F7 scope question is ANSWERED: whole-window voiding is affirmed
  as the current semantics (a cell-scoped alternative only via the
  D-083 cold gate; not built). Historical record of the 2026-08-03
  attempt below. The whole chain executed: D-108 ruled
  (clause (c) retired), row `D100-BII-BINDING-01` CLOSED (PR #99 +
  clause-(d) three-occurrence digest-bound re-record), closure +
  membership-binding artifacts authored and dry-authorized, D-093 scan
  clean 1/1, frozen corpus verified byte-identical (210+4 files, zero
  mismatches). The governed re-evaluation then REFUSED pre-verdict:
  survivor consumption failed on `mtadd-p2048o0128-r06`'s
  collection-time clock-anchor failure (`native_intersection_empty`) —
  the cold gate ruled this CORRECT fail-closed machinery (classification
  (i), convergent instruments; record
  `docs/process_traces/2026-08-03-winB-reeval-stop/`). No licensed
  channel removes r06 (exclusion cap spent on r08; not a dangler;
  waivers forbidden), and the NEG-8 drift bound expired 2026-08-02, so
  no PASS path exists under the license as drawn. Original FAILED
  verdict untouched. The WB NEG-8 bound re-mint obligation is MOOT
  under D-113; the near-run-time freshness rule continues to bind
  every future window (runbook + D-078, by cross-reference).

| Paper claim | Campaign | Collected | State after D-100 |
|---|---|---|---|
| **C1 — linearity** | `linearity_ramp` | **40/40** (window A) | DEAD for claims (window A permanent FAIL); re-collect (window C/D); data usable as design input (micro_delta slope) + corroboration diagnostics only |
| **C2 — null ladder** | `null_ladder` | o0128 + o0512 collected in window B — **returned to uncollected-for-claim state (D-113)**; o2048 never collected | Re-collect ALL of C2 fresh (window C, or split per the frozen plan); no WB member enters a replacement claim basis |
| **C3 — micro-delta** | `micro_delta` | not collected | Plan is draft-pending-slope by design; slope fit may consume window A ramp as DESIGN input (not a claim) |
| **C4 — additivity** | `additivity_shapes` | 23/24 single-root collected in window B — **returned to uncollected-for-claim state (D-113)**; 21/24 window-A corroborating remain labelled non-claim diagnostics | Re-collect C4 fresh (window C/D per the frozen plan). F7 ANSWERED by D-113: whole-window voiding affirmed as current semantics; no cell-scoped salvage |
| **C5 — long holds** | `long_holds` | not collected → window C | — |

## 4. Standing gates on EVERY claim consumption

1. ~~D-088 cl.3(c) three-check bench scan~~ — **LIFTED 2026-08-02**: the
   cooldown-join gauntlet closed (commit 3 merged, PR #93 `cb860e1`);
   the landed machinery now enforces these properties structurally
   (result-map completeness, counting domain, authenticated v2
   discrimination).
2. ~~D-093 raw-vs-validated supersession-record scan~~ — **LIFTED
   2026-08-02** with the gauntlet's close per its row contract; the
   validated reader boundary (PR #91) plus the commit-3 authenticated
   catalog own raw-record visibility permanently.
3. Verdicts consumed as issued; overrides only via the cold-gate path
   with written dissent Ed sees. (UNCHANGED — permanent.)
4. NEW (D-105): while `C3-RECOGNIZER-EXACT-01` is open, the tail
   recognizer's accepted set may only shrink, and the custody sidecar +
   writer-side key assertion may not be weakened.

## 5. DO NOT QUOTE — retired, void, or wrong-as-stated

- **ALL mint #1 floors as claims (D-110, 2026-08-03): operative
  7.377086 J, a10 components 3.823787 / 3.592138 J, window C
  comparative 7.377086 J** — retroactively non-claim-bearing (zero
  allowance where D-102 pin 3 mandates +max(drift, 0.010818 s));
  citable again only after the ruled re-mint under the repaired
  selector.
- **146.730349 J as "the contrast claim"** — it is the
  idle_subtracted_energy_j whole-request diagnostic; the registered
  claim metric is phase_energy_j.decode = 141.29 J (sweep DC-1). Either
  number only as prose with its metric named, neither as a gated claim
  yet.

- **3.17 / 2.94 J** floors — pre-allowance attribution-width
  diagnostics only (D-079 cl.5).
- **3.592138 J as "the decode floor"** — it is the isolated absolute
  component; the operative floor is 7.377086 J (D-084).
- **4.923 J item / 24.62 J suite** comparative floors — Ventura
  screensaver contamination artifacts (2026-07-17 campaign).
- Old window B (`04_phase_prefill_abba`) figures — verdict FAILED
  (`instrument_calibration_mismatch`, GPU DVFM ramp aliasing), corpus
  preserved but not claim-bearing.
- All pre-repair (pre-D-078) powermetrics corpora for claim use —
  time-anchor defect (D-078 soundness gate).
- Window A/B metrology numbers as claims — see §3 (verdicts FAILED as
  issued; window A permanently dead for claims; window B only via a NEW Ed ruling (D-112: the re-evaluation was performed 2026-08-03 and correctly refused; license exhausted as drawn).
- **Window A C1 linearity figures in any claim context** — the corpus
  is design-input/diagnostic only, permanently (D-100 + the immutable
  T1-incompatible retry).

## 6. Instrument findings queued for the paper (not claims yet)

- **Clock-anchor knife-edge** (2026-08-01 Sol consult, accepted): at
  197 s capture length the native-second intersection margin is ~±1 ms
  and the unmodeled wall/monotonic rate (~−12 ppm ≈ 2.3 ms/capture)
  exceeds it; pass/fail is quantization-phase luck. Desk item:
  rate-aware anchor design; directly publishable as a metrology
  limitation/finding.
- **Quiet-state definition**: validated windows now include suspended
  cloud sync (bird-SIGSTOP protocol) — claims describe that controlled
  state, not an arbitrary unattended Mac.
- **Operator-session streaming hazard**: the operating session's own
  output streaming can fail a member's idle admission (window B
  failure #3) — a reproducible environmental-validity observation.

1. **The D-110 clause-3 re-mint order (historical a10 consumption under
   the corrected selector) is SUPERSEDED.** The issued ledger holds only
   import-marked receipts; candidate discovery excludes imports by
   design; future live receipts cannot causally bracket past windows.
   The order is structurally unsatisfiable at main, not merely
   inconvenient. D-110's OTHER holdings STAND untouched: mint #1 and
   derivatives remain non-claim-bearing, and the never-zero
   `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3)
   BINDS every mint under this entry.
2. **Replacement: three compact prospective claim windows** — fresh
   1.5B decode floor, fresh 7B decode floor, fresh 1.5B-vs-7B contrast
   — each with fresh §5A, live pre/post calibration receipts appended
   to the issued ledger, own verdict + head-pin + custody. Claims
   chain: historical corpus → issued D-079 acceptance rule → live
   brackets → prospective floors → prospective contrast. Honest
   framing preserved from the consult: historical data establish the
   RULE; live receipts bracket all claim-bearing science.
3. **Scope (Ed's decode/prefill directive):** prefill FLOOR cells ride
   both floor windows (cheap, same members' prefill phase). The model
   contrast is DECODE-ONLY by default: the 2026-08-07 desk feasibility
   check (`docs/process_traces/2026-08-07-prefill-feasibility/`) found
   the 128-token prefill contrast MARGINAL against the effective bar
   (interval overlaps it). A prospectively frozen ≥256-token prefill
   contrast arm remains an OPEN ED OPTION (estimand change +
   ~110 core minutes, likely its own window) — not adopted here.
4. **D-113 rewire:** its readiness dependency on the historical re-mint
   completing is REMOVED. The three-window P1 closure PRECEDES the
   broader MET-WINDOW-C-01 C2/C4/C5 replacement campaign (grounds:
   Ed's paper-first priority stack, 2026-08-06).
5. **Naming:** "Window D" is unavailable (collides with
   `runs_window_d_20260726` and D-113's reserved terminology); the
   three windows receive new immutable plan/root identifiers at plan
   freeze.
6. **Option 1 (finite-allowlist historical candidacy) is PRESERVED as
   a versioned contingency ONLY**, requiring a rule-11 cold gate before
   any implementation (semantics sketch: consult response §3). The
   historical corpora remain untouched on disk, non-claim-bearing per
   D-110 cl.1, logs sha-verified.
7. **Unblocked desk queue** (consult §4): freeze three window plans +
   budgets; 1.5B decode floor plan from the proven 10-absolute/40-null
   design; generalized mint pinsets with per-plan six-decimal literals
   (the D-084 hard literal `7.377086` refuses any corrected mint under
   every option — closure is per-plan supply via the generalized path);
   extraction specs / order manifests / evidence-root ids / contrast
   manifest; synthetic three-window live-ledger integration regression;
   D-102 successor-artifact packet; results/methods prose placeholders.

exec
/bin/zsh -lc "rg -n '"'^## '"' docs/paper/draft-v1.md
rg -n 'D-117|117' docs/decision_log.md | tail -10
rg -n '"'^## '"' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md docs/strategy/2026-08-06-impressiveness-roadmap.md docs/research_question_registry.md docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
3:## 1. Introduction
22:## 2. Background and the gap
38:## 3. In-window calibration method (C-i)
58:## 4. Detection-floor composition (C-ii)
117:## 5. Fail-closed collection protocol (C-iii)
141:## 6. Instrument characterization (C-iv)
162:## 7. Demonstration results (C-v)
168:## 8. Related work
5287:`3ff9128b170136c57eea1376e954d32736d82d319d0d82bd1b64a78e616f1173`, backup ok,
5310:   (`3ff9128b170136c57eea1376e954d32736d82d319d0d82bd1b64a78e616f1173`). The
6826:   workload evidence; producer emits it at controller.py:1175) and
7084:> **2026-08-07 supersession (D-117):** clause 3's historical re-mint
7088:> allowance correction STAND and bind the D-117 mints.
7249:> **2026-08-07 amendment (D-117 cl.4):** the readiness dependency on
7507:## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired
docs/research_question_registry.md:35:## Registry Table
docs/research_question_registry.md:118:## Attribution Limits
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:112:## Findings
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:486:## Residual risk
docs/research_question_bank.md:14:## Promoted 2026-07-07 (now Q4-Q6 in PROJECT_STATUS)
docs/research_question_bank.md:33:## Methodology centerpiece (deliberately NOT a numbered RQ — C-003 vote)
docs/research_question_bank.md:42:## Banked (viable, not yet promoted)
docs/research_question_bank.md:86:## Instrument expansions adopted by C-004 (queue P2-009 / P2-010)
docs/research_question_bank.md:118:## Suite mechanism
docs/research_question_bank.md:149:## Minimal substrate scope
docs/research_question_bank.md:182:## `suite_manifest` field sketch
docs/research_question_bank.md:278:## Difficulty metadata rule
docs/research_question_bank.md:287:## Benchmark import
docs/research_question_bank.md:371:## Export / energy layer
docs/research_question_bank.md:395:## Kill / defer
docs/research_question_bank.md:411:## New questions
docs/research_question_bank.md:447:## Capability map by claim ceiling
docs/research_question_bank.md:526:## Why this instrument matters (steelman preamble, examiner-scoped)
docs/research_question_bank.md:582:## TIER 1 — answerable with current hardware (M3 Max alone)
docs/research_question_bank.md:723:## Workload/query-set expansion (first-class topic, Tier 1 hardware)
docs/research_question_bank.md:822:## TIER 2 — unlocked by already-planned hardware gates
docs/research_question_bank.md:1011:## TIER 3 — requiring new acquisitions (hardware class + rough cost tier)
docs/research_question_bank.md:1055:## Unexpected-applications shortlist (beyond papers)
docs/strategy/2026-08-06-impressiveness-roadmap.md:104:## Findings
docs/strategy/2026-08-06-impressiveness-roadmap.md:209:## Residual risk

exec
/bin/zsh -lc "sed -n '1,116p' docs/paper/draft-v1.md
sed -n '117,240p' docs/paper/draft-v1.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# JouleWise: Detection Floors for LLM Inference Energy Measurement on Consumer Silicon

## 1. Introduction

Energy numbers for large language model (LLM) inference now appear in leaderboards, systems papers, product comparisons, and policy debates. Published estimates for apparently similar queries can differ by an order of magnitude, yet the numbers are rarely accompanied by an error bar that says how small a difference the measurement method can actually distinguish. This omission is especially consequential on consumer hardware. Apple's `powermetrics` utility makes processor power estimates available without a laboratory meter and is therefore attractive for repeated experiments, but, to our knowledge, it has not been validated in published work as an instrument for separating the energy of LLM inference phases. Apple describes its outputs as estimates; treating them as exact readings can turn timing uncertainty at a phase boundary into a spurious energy difference.

The core difficulty is physical as much as statistical. Energy is the integral of power over time. An experiment may repeat consistently and still assign energy to the wrong phase if a power sample near the boundary between prompt processing and token generation is placed on the wrong side. Averaging more repetitions reduces random scatter but does not remove that attribution error. Slow changes in thermal or background state can add a second false difference over a long collection session.

We argue that a software power counter should be treated as a scientific instrument rather than as a logging convenience. The instrument must be calibrated in the same session in which it is used; each reported result must carry a detection floor, meaning the smallest false effect that the calibrated method could plausibly produce under the stated conditions; and the analysis must decline a directional claim when the observed effect cannot clear that floor and its own measurement uncertainty. JouleWise implements this discipline for phase-resolved, single-request LLM inference on one named Apple-silicon machine and software stack. The runtime emits the phase boundaries because it drives the workload, while `powermetrics` supplies the power samples integrated between those boundaries.

This scope is deliberately narrow. A measurement characterizes one physical unit, operating-system build, runtime and library stack, model artifact, quantization, tokenizer, sampling policy, single-request execution policy, telemetry backend, and measurement boundary. It does not establish that an Apple hardware class or vendor is more efficient than another platform. Without an external power meter, absolute values remain internal to the named `powermetrics` system-on-chip boundary; same-boundary contrasts can still be scientifically useful when they pass the calibration and floor gates. Gross joules per request are the primary energy metric. Joules per prompt or output token are tokenizer-scoped companion metrics and are never treated as tokenizer-independent work units.

This paper makes the following contributions:

1. (C-i) an in-window calibration method that measures timing-attribution error for phase-resolved energy integration;
2. (C-ii) detection floors composed from measured repeatability, worst-case attribution, and measured drift — published with every result;
3. (C-iii) a fail-closed collection protocol (admission gates, ABBA ordering, custody chains, pre-registration) with its refusal log as evidence;
4. (C-iv) full instrument characterization: linearity, null response across magnitudes, empirical floor verification, phase-attribution causal consistency, drift/settle;
5. (C-v) demonstration measurements: phase-resolved J/token for two model sizes with a pre-registered contrast [+ quantization ladder if window budget allows];
6. (C-vi) open tool + hash-bound reproducible artifacts.

## 2. Background and the gap

### Energy-benchmarking rules

The first relevant lineage is formal energy benchmarking. MLPerf Power and the associated Standard Performance Evaluation Corporation methodology treat uncertainty and validity as properties of each measured run. They require a qualified analyzer, uncertainty evaluated at the observed load, fixed measurement ranges, synchronized clocks, sufficiently long intervals, invalid-sample accounting, and explicit treatment of battery-backed systems [MLPerfPower]. These rules establish an important principle: a benchmark result is not valid merely because the meter has a specification sheet. The evidence recorded during the run must show that the measurement operated inside its accepted conditions. These standards, however, assume external instruments and data-center-style workloads; they do not provide a method for validating phase boundaries reported by a software counter on a consumer system.

### Software-counter validation

The second lineage validates software-visible energy counters against external power. Intel's Running Average Power Limit (RAPL) counters have been studied through lag alignment, regression against wall power, counter-resolution tests, sampler-overhead audits, and thermal controls [RAPLInAction]. Jay and Ostapenco's CCGRID 2023 study likewise shows that the gap between a software meter and wall power can depend on load rather than behave as one fixed offset, and it refrains from component-level conclusions when no reference instrument observes the component [JayOstapenco]. This work provides a strong model for whole-machine scale validation. It does not define a detection limit for a reported effect, does not validate `powermetrics` on Apple silicon, and cannot by itself establish whether software samples were assigned to the correct LLM phase. A wall meter observes a total; phase attribution needs a separate timing experiment.

### LLM energy studies

The third lineage measures LLM energy across models, hardware, and workloads. TokenPowerBench reports prompt-processing and token-generation energy with phase-appropriate token denominators; ML.ENERGY, Silicon Showdown, and Intelligence-per-Watt broaden empirical coverage across deployed systems [TokenPowerBench; MLENERGY; SiliconShowdown; IntelligencePerWatt]. This breadth makes inference energy visible, but the nearest studies do not jointly characterize counter timing, repeatability, drift, and the minimum resolvable effect. Phase labels are consequently easy to read as exact even when the method does not report the boundary events, alignment uncertainty, or a floor below which a difference should be refused.

The specific gap is therefore not another energy table. To our knowledge, no published work combines phase-resolved LLM energy on consumer silicon, a per-measurement error budget, and validation of `powermetrics` timing attribution under its named measurement boundary (as distinct from validating its absolute counter gain or whole-system energy scale, which would require an external meter). JouleWise fills that gap by making instrument characterization and refusal behavior the primary result; model comparisons are demonstrations of what the characterized instrument can and cannot resolve.

## 3. In-window calibration method (C-i)

### Measurement model and boundary

JouleWise measures one sequential request at a time. Prompt processing (often called *prefill*) converts the input sequence into the model's internal state; token generation (often called *decode*) produces output tokens from that state. Because the experiment controls the runtime, it records the start and stop of these phases directly in the runtime event stream rather than inferring them from shapes in the power trace. The reducer then integrates the named `powermetrics` system-on-chip power channels between each pair of phase events using trapezoidal integration.

The runtime and the telemetry sampler do not share a perfect clock. Operating-system launch latency, timestamp anchoring, and the sampler's averaging behavior can shift an apparent edge. A phase-energy estimate must therefore be an interval, not only a point. The calibration asks a concrete question: if software commands a load pulse at a known time, how far can the rising and falling edges of that pulse appear displaced in the sampled power trace?

### Bracketed pulse-train calibration

Immediately before and after every claim-bearing collection window—that is, a window eligible to support a reader-facing scientific claim—JouleWise runs a fresh pulse-train calibration under the same machine, operating-system, power-supply, and telemetry state as the science workload. The current protocol commands 59 graphics-processor matrix-multiplication pulses. Their durations are fixed in advance, their gaps follow a deterministic low-discrepancy schedule rather than a single repeated period, and quiet baselines of at least 4.5 seconds separate the fitted regions. The varied schedule reduces the risk that the calibration accidentally locks to the telemetry sampler's cadence. The 59-pulse design supports the pre-registered nonparametric 95/95 bound: a conservative bound intended to cover at least 95% of the calibration population with 95% confidence under the stated transfer assumptions.

For each pulse, the estimator compares the commanded interval with the observed power plateau and fits the start-edge and stop-edge lags independently. This distinction matters. A common shift of both edges may leave pulse energy nearly unchanged, while an early start combined with a late stop can add energy at both boundaries. The calibration therefore retains a bound for the instrument's edge-placement error rather than collapsing the evidence to one best-fit lag.

Each science member, meaning one recorded workload run, also carries a local bound on how its runtime clock is anchored to the trace, including the observed span between wall time and a monotonic clock that is not adjusted by network synchronization. For a reported phase, the analysis combines the member-local common shift, the calibration edge bound, and the clock-span term. It evaluates the energy integral at all four combinations of early and late start and stop edges, while scanning the allowed common shift exactly. The minimum and maximum of those integrals form the admissible energy interval. The physical intuition is simple: the interval asks how much energy could move into or out of the phase if both boundaries were placed at their most adverse calibrated positions.

The pre- and post-window calibrations form a bracket around the measurements. Both must be authenticated, fresh, and causally outside the science interval. The operative bound is the larger of the two. Separately, the absolute difference between the pre- and post-window calibrations is screened against a derived bracket-drift limit of about 10.82 ms: a small repeatability-only excess is propagated into every floor and claim, while an identified systematic defect cannot be absorbed by that budget. If the post-window bound is larger than the one used when a member was first reduced, the member must be re-reduced through the pre-specified path with the wider bound or it cannot support a claim; metadata is never patched to make the bounds agree. A pre-flight level screen also runs before the first science member. It rejects a calibration whose fitted lag is outside the previously characterized family, such as a graphics-processor frequency ramp that the pulse model could mistake for a timing shift. A retry is allowed only after a specific cause is identified and removed, within the retry count frozen before collection. Repeating merely until a favorable calibration appears would be selection on the outcome.

This procedure validates timing attribution, not the gain of the power counter. The pulses are graphics-processor matrix multiplications under a relatively light central-processor load, so transfer of their timing bound to sustained mixed-load inference is an explicit assumption. The in-session bracket, empirical floor probes in Section 6, and stack-specific labels constrain that assumption; only an external meter could additionally validate the absolute whole-system scale.

## 4. Detection-floor composition (C-ii)

A *detection floor* is a practical guard against false observed effects for one declared condition family: the same telemetry backend, metric, window type, workload profile, and stack identity. One such family forms a measurement cell. The floor is not a claim that a population percentile has been estimated exactly. JouleWise computes separate absolute and comparative floors and takes their maximum for the cell. An absolute floor measures how far repeated measurements of the same condition wander from their mean. A comparative floor measures the apparent difference between labels that are deliberately made identical and collected in A/B/B/A order.

### Repeatability and false-comparison guards

For an absolute cell with energies \(E_i\), residuals \(r_i=E_i-\bar E\), sample standard deviation \(s_r\), and \(n\) valid bundles, the point guard is

\[
F_{\mathrm{abs,point}}=\max\left(\max_i |r_i|,
t_{0.975,n-1}s_r\sqrt{1+1/n}\right).
\]

For \(n\) valid null-comparison blocks with within-block deltas \(\delta_i\), the corresponding guard is

\[
F_{\mathrm{cmp,point}}=\max\left(\max_i |\delta_i|,
|\bar\delta|+t_{0.975,n-1}s_\delta\sqrt{1+1/n}\right).
\]

The observed maximum protects against a false effect already seen; the Student-*t* prediction term protects against one additional observation under the repeatability model. Small samples receive a pre-registered guard factor, and fewer than five valid bundles or blocks are treated only as development evidence, not as a claim gate. Items within one bundle are not counted as independent repetitions.

### Worst-case timing attribution

Point repeatability is not the full floor. Each energy value is an interval from the timing calibration in Section 3. The floor computation evaluates the complete point-floor estimator over the joint corners of all member intervals that pass the admission and evidence gates, then takes the largest value. For a null A/B/B/A block, the four signed member intervals are propagated through the contrast together. This corner calculation is deliberately conservative: a systematic boundary-placement error is not independent Gaussian noise, so adding it in root-sum-square form would understate the worst case. The published floor is no smaller than the largest accepted attribution width.

This calculation revealed a stable and important limitation of the present instrument. Ordinary repeatability is smaller than the uncertainty caused by placing samples at phase edges: approximately one joule can be assigned to the wrong phase when a roughly 30 ms timing uncertainty meets a power change of roughly 33 W. The instrument is therefore *attribution-limited*, not *noise-limited*. More repetitions can refine the repeatability term, but they cannot average away this boundary-placement limit.

### Measured, never-zero drift allowance

Drift is a slow change in the machine or measurement response over the collection window. It is measured rather than assumed away. Each prospective window includes three fixed reference runs at the start, one at the midpoint, and three at the end. Gross energy and idle-subtracted energy are treated as separate claim families (idle-subtracted energy is gross energy minus the measured idle mean power multiplied by the phase duration). For each family, the protocol derives a repeatability bound from a settled reference corpus and measures the largest excursion among the start mean, midpoint, and end mean. The allowance is

\[
A_{\mathrm{drift}}=\max(\text{observed start/mid/end excursion},
\text{derived reference-repeatability bound}).
\]

Consequently, a passing drift screen never means zero drift. The allowance remains positive even in an exceptionally stable window, and the midpoint protects against an interior excursion that similar endpoints would miss. No duration-scaling law is applied because the available evidence does not identify a physical law relating drift to elapsed time.

For each absolute or comparative component, the guarded, corner-widened value is increased once by its matching drift allowance. The operative floor for a cell is then

\[
F_{\mathrm{cell}}=\max(F_{\mathrm{abs}},F_{\mathrm{cmp}}),
\]

not their sum. Cross-window components keep their own calibration basis and allowance; an allowance is never added again at the cell or reporting level. Operative floor values and their full decomposition for each demonstration stack are withheld here until the corrected artifacts are issued: **[RESULT PENDING RE-MINT]**.

### LABELLED publication and the effective decision bar

When timing attribution dominates, the floor remains publishable only through the **LABELLED** path. Every artifact and reader-facing result must identify the limit as attribution-limited, publish the corner-widened value rather than the smaller point diagnostic, retain the point-only repeatability number as a non-publishing diagnostic, and carry `floor_source = E_clock_anchor_shift_bound_j`. This field names energy uncertainty caused by shifting the phase edges within the calibrated clock-anchor bound as the dominant term. The label prevents a precise repeatability number from masquerading as the instrument's total resolving power.

The floor is only one side of a claim decision. The calibrated floor bounds a false effect produced by the calibration condition; the confidence or decision interval for the particular measured contrast separately carries that contrast's timing-attribution uncertainty. These are distinct uses of the same physical uncertainty and both are required. The effective bar is therefore

\[
\text{effective clearable effect}=F_{\mathrm{cell}}+B_{\mathrm{claim}},
\]

where \(B_{\mathrm{claim}}\) is the claim-side measurement bound. For the measured phase-contrast regime, this combined bar is approximately 5 J. Neither term may be removed as an apparent double count. Effects below the floor are reported as *not resolvable*, not as zero, equal, or evidence of no difference. A directional claim is made only when the effect and its interval clear the applicable bar.

## 5. Fail-closed collection protocol (C-iii)

*Fail-closed* means that missing, inconsistent, stale, or contaminated evidence produces a refusal rather than an optimistic default. The collection unit is one uninterrupted two-to-four-hour window with one power state, one instrument identity, fresh calibration before and after, a fresh drift-bound corpus, and one verdict over the exact member set. Work that does not fit with at least a 20% failure margin is split prospectively into another independently calibrated window.

### Pre-registration and admission

Before quiet time, the operator freezes the run identifiers, membership, stage order, comparison definitions, calibration retry count, acceptance thresholds, extraction specification, code revision, and an initially empty waiver list. Every configuration is validated and dry-run against a fresh output root. These choices are made before outcomes are visible. Pre-registration here is executable: the launcher and final verifier check the frozen values rather than relying on a narrative promise.

Each stage then passes admission gates immediately before measurement. The approved power supply and power policy must be unchanged; displays must be asleep; the screensaver and low-power mode must be off; thermal pressure must be nominal; and central- and graphics-processor activity must meet the quiet-state criteria. Known background work is allowed to finish before the window, followed by a settling interval, rather than being ignored during analysis. Runtime and telemetry identities, clock anchoring, sample cadence, calibration freshness, and post-run environment observations are also checked. No environment override can produce a claim-bearing member.

### Counterbalanced order

Comparisons use A/B/B/A blocks, abbreviated **ABBA**. Conditions A and B are measured in the order A, B, B, A, with ordinary cooldown between members. Averaging the two outer A observations and the two inner B observations cancels a linear time trend within the block to first order. For null-floor calibration, A and B are aliases of the exact same configuration and payload, so any nonzero block delta is a false comparative effect. For scientific contrasts, the A and B definitions are frozen in advance, and the contrast is computed within each block before blocks are aggregated. ABBA reduces common drift; it does not replace the measured whole-window drift allowance.

### Evidence custody and refusals

Every member is a self-contained bundle of configuration, raw power trace, runtime events, environment observations, and derived summary. Cryptographic hashes bind those files to the campaign manifest. Failed or interrupted artifacts are never deleted or overwritten. An occupied retry slot is moved to a quarantine area outside the active runs root; the exact member is recollected only under an allowed retry; and an append-only supersession record names which occurrence governs. Two present bundles for one occurrence refuse. The final whole-window verdict binds the exact member-occurrence set, calibration bracket, policy, and drift evidence by hash, so a later consumer cannot silently select a more favorable subset.

Collection does not continue indefinitely through environmental interruptions. Each stage attempt stops at its first member failure, and after the same cause fails a window stage for the third time the window itself closes rather than being retried; in actual operation, nights with three environmental member interruptions were closed and preserved as salvage rather than repeatedly retried. The surviving data may remain diagnostic, but it becomes claim-bearing only if the pre-registered verdict and extraction rules accept the exact resulting basis. This abandon-after-three rule limits outcome-dependent retrying and makes the cost of a noisy environment visible.

The custody chain continues after collection. The immutable corpus is backed up before extraction. The extractor re-authenticates member hashes, required files and cross-file consistency, calibration identity, environment admission, complete campaign membership, cooldown evidence, phase metric identity, and the whole-window drift allowance. It excludes or refuses a cell according to the frozen rules; missing uncertainty never becomes zero. The current artifact boundary is stated honestly: until floor artifacts are independently bound to their source extraction, a claim-bearing floor must be produced by protocol-controlled extraction in the same controlled custody session as the analysis that consumes it. A standalone floor file is not independently claim-licensing.

The refusal log is part of the evaluation, not an embarrassment to omit. It records contaminated members, out-of-family calibration, stale drift evidence, unresolved clock anchors, duplicate occurrences, and below-floor effects. In one real end-of-night case, the governed re-evaluation refused a window because a member's internal clock alignment could not be resolved. Independent adjudication found that refusal correct. The result remained non-claim-bearing: an example of the fail-closed design working as intended, not a software defect to be bypassed.

## 6. Instrument characterization (C-iv)

Instrument characterization asks whether the complete measurement system behaves predictably when driven by signals whose qualitative answer is known in advance. The workload is therefore a test signal, not yet the scientific finding. All tests retain the same calibration, admission, custody, and floor rules as the later demonstration measurements. Existing campaign fragments are not promoted where the governing whole-window verdict did not pass; the table marks the required claim-bearing results explicitly.

| Property | Characterization method | What a passing result would establish | Claim-bearing result |
|---|---|---|---|
| Linearity | Hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. Regress gross request and decode energy on the runtime-observed output count; inspect residual structure as well as the fitted slope. | Energy responds proportionally over the tested dynamic range, and the fitted per-token slope can serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
| Null response across magnitudes | Run identical A-equals-B ABBA blocks at short, medium, and long output magnitudes. Evaluate the paired deltas against zero and against the predicted decision envelopes. | The comparison path does not create a directional effect merely because total energy or duration changes, and false contrasts across the tested range are contained by the error model. A non-significant result alone is insufficient; the interval must be interpreted relative to the floor. | **[PENDING WINDOW C]** |
| Empirical floor verification | Use the pre-registered linearity slope to create micro-deltas with predicted effects near 0.5, 1, 1.5, and 3 times the declared floor. Test positive and negative directions in counterbalanced blocks. | Sub-floor effects are refused while sufficiently super-floor effects clear in both directions. This is an operational check of the detection boundary, not a validation of the counter's absolute gain. | **[PENDING WINDOW C]** |
| Phase-attribution causal consistency | First compare the sum of separately integrated phase energies with the gross energy over their enclosing request. Then vary output length while holding prompt tokens fixed and fit the slope of prefill energy against output length. | Phase accounting is additive within its stated boundaries, and energy assigned to prefill does not acquire a systematic dependence on work that occurs later in decode. Together these tests challenge both missing energy and cross-phase leakage. | **[PENDING WINDOW C]** |
| Drift and settling | Place long controlled holds and fixed reference workloads through the window, including start, midpoint, and end references. After operator or stage activity, repeat the reference while recording the time required for thermal and admission observables to stabilize; compare it with the 180 s operating convention. | The measured drift trajectory is contained by the published allowance, and the chosen settling time is supported or revised from observed recovery rather than convenience. Endpoint agreement alone is not enough if the midpoint reveals curvature. | **[PENDING WINDOW C]** |
| Between-session stability | Repeat calibrations, null blocks, and floor cells across at least three sessions or days with the full stack identity recorded. | The calibration and floor are stable enough to reuse only under their declared freshness and identity rules, or reveal that a new session must mint a new floor. | **[PENDING WINDOW C]** |

Linearity and the null ladder test complementary failure modes. A smooth response can still carry an offset, and a zero-centered null can coexist with a nonlinear scale. The micro-delta experiment then closes the loop by using the measured slope to place effects deliberately below and above the declared decision boundary. Success requires the instrument to refuse the former and resolve the latter in both directions; merely observing larger effects with larger workloads is not sufficient.

The causal tests address the most important phase-specific risk. Additivity checks conservation inside the declared request boundary: phase intervals should reconcile with the enclosing total, subject to explicitly labeled setup or gap intervals. Causal invariance checks direction: holding the prompt fixed while increasing later decode work should not change energy attributed to earlier prefill. A nonzero prefill slope would indicate boundary leakage, shared-state coupling that invalidates the simple phase model, or both; it would narrow the claim rather than be explained away.

Temporal characterization separates slow drift from thermal settling. Start, midpoint, and end references expose whole-window curvature, while post-transition references estimate how long the system takes to return to its admitted state after operator activity or stage churn. Repetition across days tests whether one session's calibration is representative under identical recorded bindings. Internal channel-sum versus package reconciliation is retained as a secondary consistency check. External wall-power regression remains conditional on a suitable meter and would validate totals only; the pulse experiment remains the evidence for phase splitting.

Every resulting figure and table will identify the physical unit, operating-system version and build, runtime and relevant library versions, model artifact hash, quantization, tokenizer identity, sampler and output policy, configured and realized batch/concurrency policy, measurement boundary, and telemetry backend. Silent omission is not permitted. Measurements support stack-specific conclusions only; independent replication or a calibrated boundary bridge would be required for hardware-class, vendor-class, or cross-boundary rankings.

## 7. Demonstration results (C-v)

**[RESULT PENDING RE-MINT]**

This section will report phase-resolved gross joules per request for two model sizes, with tokenizer-scoped joules per prompt token and per output token as companion metrics. It will contain the pre-registered same-boundary model-size contrast, its interval, the complete floor decomposition, the claim-side bound, the effect-to-floor ratio, and the final resolvable/unresolved verdict. No demonstration energy value from the superseded mint is carried into this draft. A quantization ladder will be included only if it is collected under its own stack-specific floors and the frozen window budget permits it.

## 8. Related work

### LLM inference energy measurement

TokenPowerBench provides one of the closest reporting structures: it separates prompt-processing and token-generation energy, uses phase-appropriate token denominators, and groups results by context length [TokenPowerBench]. Its disclosed method, however, does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline, or external validation, and continuous batching makes an “active phase” label difficult to interpret when requests overlap. JouleWise adopts phase-specific reporting but restricts its primary scope to one sequential request, where runtime-emitted phase boundaries are well posed and can be calibrated.

The Illusion of Power Capping in LLM Decode samples graphics-processor power, integrates those samples, repeats configurations, and cross-checks sufficiently long operations against a separate hardware energy counter [IllusionPowerCapping]. This is a stronger measurement template than an unqualified software reading. Its counter agreement, run-to-run variation, snapshot fallback, and timing alignment nevertheless remain separate diagnostics rather than one bound on the reported effect, and its long sweeps do not use a drift-control ordering. JouleWise composes those classes of uncertainty into a decision rule for each contrast.

Apple-focused system comparisons reinforce the need for boundary labels. Silicon Showdown compares a graphics-board boundary on one platform with a whole-system-on-chip `powermetrics` boundary on Apple hardware, while runtimes and precision stacks also differ [SiliconShowdown]. Intelligence-per-Watt and ML.ENERGY similarly emphasize breadth across deployed inference configurations [IntelligencePerWatt; MLENERGY]. Such studies answer valuable systems questions, but unlike boundaries and software stacks cannot by themselves support a hardware-class causal ranking. JouleWise therefore makes the named stack and measurement boundary part of every result and prioritizes within-boundary effects.

### Software power counters and measurement standards

RAPL in Action established a validation agenda for commodity software counters: align lag before comparing streams, model wall power rather than assuming identity, account for temporal correlation, warm the system, measure sampler overhead, and inspect update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. Jay and Ostapenco likewise regress software readings against wall power and show that disagreement varies with load; they avoid claims about subtotals that the reference meter cannot observe [JayOstapenco]. JouleWise follows this epistemic boundary. A future external meter could test total gain and load dependence, but it would not validate how a total is divided between prefill and decode. The in-window pulse train addresses that distinct question.

MLPerf Power and SPEC require load-specific analyzer uncertainty, fixed ranges, clock synchronization, minimum intervals, invalid-sample accounting, and controlled battery behavior [MLPerfPower]. JouleWise translates their per-run reject-on-missing-evidence principle to a consumer software counter. The difference is that its principal uncertainty is not only an analyzer specification; it includes whether samples at a software-defined phase edge belong inside or outside the integral.

### Metrology and experimental discipline

Prospective paired minimum-detectable-effect methods estimate the smallest effect a planned paired study has adequate statistical power to find. They size the study from the variance of paired differences and can impose a one-way prior ratchet: observed variability may raise the planned threshold but may not lower it after outcomes are seen [PairedMDE]. JouleWise uses that logic for prospective workload sizing, but it does not treat the worst-case attribution term as independent random noise. Root-sum-square composition would be anti-conservative for a systematic edge-placement bound. Instead, the analysis maximizes over calibrated edge positions, measures drift with bracketed references, and publishes the resulting floor with the effect.

This emphasis changes the role of failed runs. A rejected admission, stale calibration, contaminated member, or below-floor contrast is evidence about the instrument's operating domain. Hash-bound raw traces, runtime events, configurations, supersessions, verdicts, and pre-registration records make that evidence re-reducible. The refusal is retained rather than disappearing behind a final average.

### Split and disaggregated inference

Split, or disaggregated, inference places prompt processing and token generation on different devices and transfers intermediate state between them. Revisiting Disaggregation Energy reports that the energy outcome depends on load, baseline, and transfer conditions on its evaluated two-graphics-processor node [RevisitingDisaggregationEnergy]. DualScale studies phase placement and per-phase power control on homogeneous server hardware [DualScale]. Prima.cpp includes whole-run energy and communication accounting but not a per-stage energy split [PrimaCPP], while SplitZip characterizes lossless transfer compression without making an energy claim [SplitZip].

JouleWise does not claim a new split scheduler in this paper. Split inference is instead a demanding future demonstration of the instrument because it introduces two physical boundaries, a transfer interval, and clock alignment across devices. A valid comparison would have to measure both ends, name each boundary, and clear a pre-registered floor or calibrated bridge. Whether splitting saves energy remains an empirical outcome; the reusable contribution is a method that can issue, qualify, or refuse the result.

exec
/bin/zsh -lc "sed -n '1,180p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md
sed -n '181,360p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md
sed -n '361,540p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Complete D-117 freeze design: three prospective windows fit the envelope, but live-ledger sessions, multi-cell minting, and D-102 successor generation must land before any arm.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "dbb9685669ac76ea65bf458b78eeb98d94bc6a80",
    "head_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    "upstream_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The current ledger cannot safely reserve both bookend observations under one unchanged committed head",
        "detail": "The append path requires the physical ledger head to equal the committed pin before each reservation. Finalizing the pre observation advances the physical head, so an ordinary post reservation cannot occur without an intervening pin advance or a new bracket-session capability.",
        "recommendation": "Implement an atomic two-slot bracket-session capability plus exact postcollection bracket binding before freezing arm packets."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The generalized mint is still decode-only and single-plan/single-cell",
        "detail": "The current generalized path hard-checks phase_energy_j.decode and a decode phase target. It cannot mint the two prefill riders or D-095's required combined multi-cell, multi-plan floor artifact.",
        "recommendation": "Introduce pinset v2 with per-plan component pins and an aggregate four-cell artifact pinset."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "No usable D-102 successor-artifact path exists for a live-prefixed ledger",
        "detail": "The issued acceptance artifact is exact-byte pinned and prior-set verification assumes the issuance corpus. A valid range-expanding live observation could therefore stop a campaign before member one or prevent its verdict.",
        "recommendation": "Pre-build and cold-gate a deterministic successor builder, registry, live-prefix verification, and trigger-time operator procedure."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The referenced prefill-feasibility synthesis is absent at the inspected HEAD",
        "detail": "docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md does not exist in this worktree even though RUN_STATE says the trace was custodied.",
        "recommendation": "Recover or commit the trace before lead ratification; this memo uses D-117's adopted summary as authority."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "title": "Current queue rows still encode superseded C/D and D-110 gates",
        "detail": "TASK_QUEUE.md still presents MET-WINDOW-C-01 and MINT-GENERALIZE-01 under terminology and blockers superseded by D-117.",
        "recommendation": "Regenerate queue/state views from the owning state kernel after the plan-freeze decision is ratified."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main",
          "94a24e562290b59f7b40908315bbae7a032ea47e",
          "94a24e562290b59f7b40908315bbae7a032ea47e"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "94a24e562290b59f7b40908315bbae7a032ea47e$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "test -f docs/decision_log.md && test -f docs/process_traces/2026-08-06-d110-remint-fork/CONSULT-RESPONSE.md && test ! -e docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "FLAG1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "main advanced concurrently from dbb9685 to 94a24e5 during the read-only consult; the final state was re-inspected and remained clean.",
      "needs": "Freeze implementation scopes against 94a24e5 or a later explicitly reviewed head."
    },
    {
      "id": "FLAG2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No suites were run because this was a read-only design consult with no implementation.",
      "needs": "Each implementation unit below carries focused and canonical-suite obligations."
    }
  ]
}
```

## Findings

### F1 — Live-ledger bookending is not yet armable (blocker)

D-116’s issued ledger is the correct trust root, and D-117 correctly requires fresh live pre/post observations. The obstacle is mechanical: the present append path requires the physical ledger head to match the committed pin when reserving an attempt. Once the pre observation is finalized, that equality no longer holds for an ordinary post reservation.

The best design is an atomic `calibration_window_bracket_session.v1` capability:

1. At the pre-bookend, under a clean committed head, append one receipt reserving exactly two immutable slots: `pre` and `post`, each with its attempt ID, plan ID/SHA, evidence-root ID, expected time role, and shared session ID.
2. Finalize the pre slot before member one.
3. Leave the post slot prospectively open without treating it as an unresolved candidate or permitting claim evaluation.
4. Finalize or explicitly abort the post slot at the closing bookend.
5. Commit the terminal ledger head once, then issue an exact `calibration_bracket_binding.v1` mapping the frozen plan and evidence root to the two finalized content/receipt digests.
6. Candidate discovery still examines the complete live candidate universe; the binding selects the claimed pair but cannot hide extra candidates.

This is preferable to a source commit after the pre observation: that would mutate the repository and readiness head inside every quiet-window procedure. Two ordinary reservations appended in advance are also inferior because the outstanding post reservation would look unresolved unless ledger semantics were widened anyway.

Base plans should freeze calibration retry count at zero. A failed pre observation aborts before member one and closes the unused post slot; a failed post makes the physical attempt non-claim-bearing. If the lead wants one cause-removal retry, the session capability needs additional prospectively numbered slots and deterministic selection semantics before freeze—never an improvised retry.

Ideal no-failure receipt evolution from the issued sequence-76 head is three receipts per window—session capability, pre finalization, post finalization—ending at sequence 85 after all three windows. Exact sequence numbers are arm-time facts, not desk-frozen plan literals.

### F2 — The mint path needs a real v2, not another widened literal list (blocker)

The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:

- one plan and one artifact cell;
- `phase_energy_j.decode` only;
- `["phase","decode"]` only;
- no aggregate artifact over independently collected plans.

D-095 requires one multi-cell floor artifact whose 1.5B and 7B cells remain independently stack-scoped. D-117 adds prefill cells to both floor plans. The correct closure is therefore one four-cell artifact, not two loosely associated artifacts:

| Cell | Producer | Metric | Scientific family |
|---|---|---|---|
| 1.5B decode | 1.5B floor plan | `phase_energy_j.decode` | existing `df-ph-decode` |
| 1.5B prefill rider | 1.5B floor plan | `phase_energy_j.prefill` | new exact rider family |
| 7B decode | 7B floor plan | `phase_energy_j.decode` | D-085 `df-ph-decode-qwen25-7b` |
| 7B prefill rider | 7B floor plan | `phase_energy_j.prefill` | new exact rider family |

Each producer gets a component pinset; an aggregate pinset hard-checks both components and mints `d117-qwen25-phase-floor-set-v1`. Gamma consumes the two decode cells through D-095’s predeclared transport groups. It does not relabel contrast configs as floor configs.

### F3 — The D-102 successor packet is a pre-arm dependency (blocker)

A valid pre calibration can expand the observed range or approach the valid-observation limit. The issued artifact cannot absorb that live prefix today. The campaign therefore needs the following on disk and cold-gated before its first §5A arm:

- deterministic successor builder and validator;
- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
- generalized prior-set validation over a complete authenticated import-plus-live prefix;
- exact Decimal arithmetic, rounding, budget, prediction, and screen reproduction from D-079;
- a dry-run fixture that produces exact successor bytes and expected head pin;
- trigger-disposition logic that judges the range-expanding observation under the prior artifact before incorporating it into the successor;
- operator commands for pre-trigger and post-trigger branches.

I recommend deriving a successor from all content-distinct, valid, same-epoch observations through the chosen cutoff. Systematic, ordinary-invalid, aborted, or unresolved attempts remain recorded but excluded. The lead should explicitly ratify that corpus rule because D-102 establishes the successor obligation but does not fully spell out this live-prefix derivation policy.

At the pre bookend, a range expansion stops the chain before member one: close or preserve the bracket session according to the frozen state machine, commit the current ledger head, build and authenticate the successor, revalidate, then proceed. A post range expansion follows the same process after science but before the verdict. Systematic mismatch is a refusal, never something a successor can launder.

### F4 — Referenced trace missing (should-fix)

The named `docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md` is absent at `94a24e5`. D-117 itself records the adopted conclusion, so this memo treats the following as governing:

- floor prefill cells ride the floor-window decode members;
- gamma remains decode-only;
- the historical 128-token prefill contrast was marginal;
- a prospectively frozen 256-token contrast remains Ed’s option.

The missing trace prevents verification of any additional numerical assumptions it may contain. In particular, this memo does not freeze a 256-token runtime or effect-size target.

### F5 — Queue terminology is superseded (should-fix)

`TASK_QUEUE.md` still carries `MET-WINDOW-C-01`, prospective “C/D” splitting, and an old `MINT-GENERALIZE-01` D-110 blocker. Those rows cannot govern this work. D-117 clause 5 owns the namespace, and the live `RUN_STATE.md` block now recognizes that ruling. The queue should be regenerated after ratification, not manually interpreted during arm readiness.

### Ranked design decisions and rejected alternatives

1. **Use a two-slot ledger session capability and exact bracket binding.** Rejected: implicit reuse of neighboring observations, mid-window Git pin commits, or pre-reserving ordinary unresolved observations.

2. **Mint one four-cell floor artifact through pinset v2.** Rejected: two unrelated floor artifacts, summing arm floors, or weakening D-095’s independently stack-scoped maximum.

3. **Freeze zero calibration retries in the base plans.** Rejected: unbounded cause-removal retries and post hoc choice among observations. A retry-enabled variant requires a different capability state machine before freeze.

4. **Make prefill a metric rider over the exact decode members.** Rejected: copying the old dedicated 4096-prompt/64-output prefill workload, because that would add members and estimate a different condition. Post hoc extraction without a pre-registered cell is also insufficient.

5. **Treat the 256-token contrast as a fourth window plan.** Rejected: appending it to gamma later, which would change gamma’s plan SHA, member universe, order, multiplicity, runtime, and verdict basis.

6. **Use semantic immutable identifiers without dates or letters.** Rejected: `Window D`, C/D, and date-derived identities. Attempt dates belong in custody metadata, not scientific identity.

7. **Use a two-stage pin freeze.** Desk time freezes every knowable identifier, schema, member list, hash, and rule. Six-decimal operative values freeze only after governed collection and extraction. Rejected: placeholder literals presented as valid pins or any mint-time derivation.

### Proven template lineage

The templates are scientific and structural sources, not claim evidence.

| Plan | Files treated as the proven template | What is reused |
|---|---|---|
| 1.5B floor | `configs/campaigns/p2_015_floors/calibration_plan.json`; its SHA sidecar and generator; `02_phase_absolute/p2015-df-ph-decode-abs-r01.json` through `r10.json`; `05_phase_decode_abba/`’s forty decode configs and manifest; root `order_manifest.json`; `configs/floor_mint/a10_extraction_spec.json`; `configs/floor_mint/window_c_extraction_spec.json` | Exact Qwen2.5-1.5B stack identity, 10 absolute members, ten fixed A/B/B/A null blocks, runtime/config conventions, extraction shape |
| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
| Decode contrast | Entire `configs/campaigns/splitwise_decode_v1/`, particularly the plan, generator, forty configs, root/stage manifests, condition families, and `analysis_manifest_v3.json` | A=1.5B, B=7B, ten ABBA blocks, B−A orientation, v3 estimator and cross-stack floor rule |
| Operational references | `configs/campaigns/neg8_reference_corpus/` and the existing start/mid/end reference manifests | Twelve-member same-window NEG8 binding plus 3/1/3 references |

The old `02_phase_absolute/order_manifest.json` contains thirty interleaved decode, prefill, and short-prefill configs. It must not be copied as the new absolute manifest. Only its ten decode configs are the alpha source; the new ten-entry manifest is regenerated and independently hashed.

Historical results are diagnostic inputs only. No old evidence-root ID, calibration bracket, member output, or operative floor literal enters a prospective claim basis.

### Immutable identifier proposal

| Placeholder | Frozen plan ID | Evidence-root ID | Physical root |
|---|---|---|---|
| W-alpha | `plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-1p5b-v1` | `runs_d117_floor_qwen25_1p5b_v1` |
| W-beta | `plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-7b-v1` | `runs_d117_floor_qwen25_7b_v1` |
| W-gamma | `plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v1` | `evidence-d117-contrast-qwen25-1p5b-vs-7b-v1` | `runs_d117_contrast_qwen25_1p5b_vs_7b_v1` |

Each also gets a separately named bound root ending in `_bound`. Failed physical attempts receive custody attempt suffixes outside the scientific ID; the clean evidence root is never silently reused.

### Common order-manifest contract

Every root manifest should bind:

- plan ID, exact plan SHA, generator SHA, and model/runtime revisions;
- ordered stage records with exact stage-manifest ID, SHA, expected member count, predecessor, and successor;
- exact relative config paths and config SHAs—no globs or directory discovery;
- ordinal, member ID, ABBA block and slot where applicable;
- fixed reference and NEG8 manifests;
- the prefill rider mapping for floor members;
- frozen attempt policy, including zero calibration retries and no outcome-driven top-ups;
- evidence-root ID and expected fresh physical path;
- hashes of condition families, extraction spec, and analysis manifest;
- arm-time attachment slots for the readiness record, session capability, and actual receipt identifiers without modifying frozen plan bytes.

An ABBA stage manifest records each block as `A1,B1,B2,A2`. Splitting blocks 1–5 and 6–10 around the midpoint reference does not reset block numbering.

### Per-window plans

#### Alpha — 1.5B decode floor plus prefill rider

| Stage | Members | Order |
|---|---:|---|
| Pre calibration | 1 live observation | Finalize reserved `pre` slot before science |
| Same-window bound corpus | 12 | Frozen NEG8 order, then bound evaluation |
| Start references | 3 | Frozen triplet |
| Absolute floor | 10 | `abs-r01` through `abs-r10` |
| Null half 1 | 20 | ABBA blocks 1–5 |
| Midpoint reference | 1 | Frozen midpoint |
| Null half 2 | 20 | ABBA blocks 6–10 |
| End references | 3 | Frozen triplet |
| Post calibration | 1 live observation | Finalize reserved `post` slot |
| Closeout | 0 science members | Terminal head pin, bracket binding, verdict, dual-root backup |

Science count is 50; operational captures are 12 bound, 7 references, and 2 calibrations. The prefill rider adds no member and no runtime.

The rider is a new condition family over the same 128-prompt/512-output decode bundles. It must pre-register `phase_energy_j.prefill`, phase precheck `["phase","prefill"]`, exact tokenizer/model/config identity, the same ten absolute members and forty null members, its estimator, n=10 block basis, and both absolute and comparative floor rules. It is not the old dedicated prefill condition.

The extraction spec contains four cells: decode absolute, decode comparative, prefill absolute, and prefill comparative. It names 100 cell-member references but exactly 50 unique bundles. Each cell supplies an exact member list, config hash list, expected n, condition-family hash, metric key, phase precheck, order-manifest pin, calibration basis, and evidence-root ID. Missing prefill phases, fallback values, or member discovery outside the list are fatal.

#### Beta — 7B decode floor plus prefill rider

The schedule is identical to alpha: pre calibration; 12 NEG8; start 3; absolute 10; ABBA blocks 1–5; midpoint 1; blocks 6–10; end 3; post calibration.

The decode condition remains D-085’s `df-ph-decode-qwen25-7b`; the fresh plan does not rename settled scientific semantics. The new prefill-rider family pins `phase_energy_j.prefill` over the exact 7B decode members and stack revision.

Its extraction contract is the same four-cell/50-unique-bundle shape as alpha. Old 7B values—absolute 6.294380… J and comparative 13.998036… J—are budget/design diagnostics only and are not pre-registered pins.

#### Gamma — 1.5B-versus-7B decode contrast

| Stage | Members | Order |
|---|---:|---|
| Pre calibration | 1 live observation | Finalize `pre` slot |
| Same-window bound corpus | 12 | Frozen NEG8 order, then bound evaluation |
| Start references | 3 | Frozen triplet |
| Contrast half 1 | 20 | ABBA blocks 1–5 |
| Midpoint reference | 1 | Frozen midpoint |
| Contrast half 2 | 20 | ABBA blocks 6–10 |
| End references | 3 | Frozen triplet |
| Post calibration | 1 live observation | Finalize `post` slot |
| Closeout | 0 science members | Pin, binding, verdict, backup, then analysis |

The frozen manifest remains decode-only:

- A is the exact 1.5B stack; B is the exact 7B stack.
- Metric is exactly `phase_energy_j.decode`.
- Estimand orientation is B−A.
- Design is ten A/B/B/A blocks, n=10 block estimates.
- Estimator is `abba_block_arm_mean_difference_t_v1`.
- Test is two-sided at family alpha 0.05, with the positive direction stated as the scientific hypothesis rather than used to change the test.
- `equivalence_margin` and `mde` remain null unless prospectively ruled otherwise.
- Floor rule remains `cross_stack_armwise_max.v1`: independently resolve the 1.5B and 7B decode cells and take their maximum, never their sum.
- Claim-side anchor bounds remain separate from the detection-floor operation.
- The finalized analysis basis pins the exact forty member paths, config hashes, stack identities, floor artifact bytes, calibration binding, and evidence root.

### Runtime evidence and budgets

Historical evidence in `docs/phase_2/splitwise_decode_campaign.md` §4 supplies:

- 1.5B decode member: 92.7 s, measured n=40;
- 1.5B reference member: 90.5 s, measured n=7;
- 7B decode member: approximately 97 s from the measured/probed anchor;
- 1.5B/7B mixed ABBA half: about 31.6 min raw member time.

The stage allowances incorporate the configured 30-second idle, warmup/teardown, stage arm overhead, and cooldown conventions. The pre-calibration allowance includes the required 180-second post-admin settle. The separate ten-minute untouched quiet-idle gate is added before applying the 20% margin.

| Component, minutes | Alpha | Beta | Gamma |
|---|---:|---:|---:|
| Pre calibration bracket | 8 | 8 | 8 |
| 12 NEG8 bound members | 22 | 22 | 22 |
| Bound evaluation | 1 | 1 | 1 |
| Start 3 references | 8 | 8 | 8 |
| Absolute 10 | 19 | 20 | — |
| ABBA blocks 1–5 | 34 | 36 | 35 |
| Midpoint reference | 5 | 5 | 5 |
| ABBA blocks 6–10 | 34 | 36 | 35 |
| End 3 references | 8 | 8 | 8 |
| Post calibration bracket | 8 | 8 | 8 |
| Campaign subtotal | 147 | 152 | 130 |
| Untouched pre-arm idle | 10 | 10 | 10 |
| Base occupancy | 157 | 162 | 140 |
| With 20% failure margin | **188.4** | **194.4** | **168.0** |
| Hours | **3.14 h** | **3.24 h** | **2.80 h** |
| 2–4 h envelope | Pass | Pass | Pass |

The margin is time headroom, not authority to add members, replace a cap-hit observation, or top up an unfavorable result. The fixed manifest and frozen failure policy decide scientific validity.

### §5A operator bookends

Before each window:

1. Verify the reviewed plan/readiness record, fresh empty roots, model artifacts, charger/AC state, power policy, OS/tool identity, empty waiver set, and current acceptance artifact.
2. Verify the physical ledger head equals the authenticated committed pin.
3. Correct the clock against the trusted source, record the correction and `usingnetworktime` state, turn network time off, and settle for at least 180 seconds.
4. Establish zero-agent/zero-output-streaming conditions and complete ten untouched minutes of daemon idle.
5. Append the exact two-slot bracket session capability.
6. Capture and finalize the pre observation; run the acceptance and D-102 trigger probe.
7. Only after every gate is green, emit the one-line arm message and walk away.

At the closing bookend:

1. Capture the post observation before changing power, network-time, or workload state.
2. Finalize the post slot or write the governed failure/abort closure.
3. Commit and authenticate the terminal ledger head.
4. Emit the exact bracket binding and whole-window verdict from one immutable ledger snapshot.
5. Back up evidence and bound roots with verified return code and hashes.
6. Restore network time and record the restoration only after measurement completion and custody closeout.

### Prefill floor claim eligibility

A rider is claim-eligible only if desk freeze already binds:

- exact metric and phase path;
- exact workload parameters, model/tokenizer revision, seeds, quantization, runtime, sampling, and telemetry mode;
- absolute and comparative member lists and order manifests;
- exact condition-family ID and hash;
- n and estimator;
- calibration cell, acceptance artifact role, and D-110 allowance rule;
- extraction failure behavior;
- allowed consumer families.

For each metric, the operative floor is the maximum of independently evaluated absolute and comparative components. Apply D-110 once as `A_s = max(observed_drift, 0.010818)`. Never sum components and never borrow a decode floor for prefill.

### Two-stage mint freeze

**Desk-frozen pin requirements**

For each floor plan, freeze:

- plan ID, declared SHA, sidecar SHA, and actual artifact SHA;
- evidence-root ID;
- four intended cell roles across the two plans;
- condition-family IDs/hashes;
- metric and phase-precheck paths;
- absolute and comparative order-manifest IDs/hashes;
- extraction-spec SHA and exact members;
- expected counts;
- model/runtime/config hashes;
- calibration acceptance artifact ID/SHA/derivation rule;
- D-110 never-zero allowance rule;
- aggregate artifact ID and transport allowlists.

These live in a non-mintable `pin_requirements.v2` artifact. Unresolved values must be structurally absent or explicitly marked unresolved; the file cannot satisfy the final pinset schema.

**Postcollection-frozen pins**

After passed verdicts and governed extraction, freeze separately for each of the four cells:

- absolute and comparative evaluation-basis SHA/count;
- exact accepted pre/post receipt and content digests;
- bracket-binding SHA and terminal ledger head;
- observed drift and applied allowance;
- extraction-report SHA;
- absolute, comparative, and operative values;
- the operative literal formatted independently as exactly six decimals using the repository’s `.6f` convention.

The lead independently recomputes each six-decimal literal from primary extraction bytes. The mint only compares supplied literals and hashes; it does not calculate them. The old `7.377086` literal is never reused.

Gamma has no producer mint. Its consumer pinset instead binds the exact combined floor artifact bytes, the two decode-cell IDs, its plan/order/analysis manifests, and its finalized evaluation basis.

### Synthetic three-window live-ledger regression

The fixture begins with the exact issued-ledger semantics: 76 receipts, including 38 historical import observations—30 valid, 2 systematic, 6 ordinary-invalid. Candidate discovery must exclude every import-marked observation.

The no-failure live extension adds three bracket capabilities and six finalized live observations. From one immutable final snapshot, the regression must prove:

- exactly six live candidates and zero imported candidates;
- alpha, beta, and gamma each bind only their own pre/post pair;
- all six are same-epoch, causal, fresh, within protocol and T1 limits;
- no neighboring endpoint can substitute for a bound endpoint;
- all three verdicts use the same complete candidate universe;
- the ideal terminal sequence is 85 under the proposed three-receipt session model;
- the D-110 never-zero allowance remains active.

Required refusal vectors:

- import-marker removal, import leakage, or candidate-discovery regression;
- missing, duplicate, reordered, or conflicting session/finalization receipts;
- open or abandoned session without a governed closure;
- physical-head/pin mismatch, rollback, fork, or uncommitted terminal head;
- omitted, added, duplicated, off-ledger, or content-substituted observations;
- missing, tampered, swapped, or cross-window bracket binding;
- noncausal endpoint, stale endpoint, T1 failure, protocol failure, or epoch mismatch;
- systematic classification;
- one range-expanding live observation requiring a successor;
- the observation-count boundary reaching the D-102 limit;
- a successor whose prior set omits or changes an authenticated prefix.

### Optional 256-token prefill contrast

Clean attachment inside frozen gamma is impossible. Adding the arm changes the workload, metric family, members, order, runtime, multiplicity, plan digest, evidence root, and verdict basis.

If Ed adopts it, create a fourth independently frozen, independently calibrated plan and evidence root. It may attach later only in a higher-level synthesis/claim packet that references gamma and the new prefill result as sibling artifacts. Gamma’s bytes remain unchanged.

The floor riders here use the prefill phase of the 128-prompt decode workload. They do not automatically transport to a prospectively defined 256-token contrast. The fourth plan needs either exact matching prefill floor cells or a separately predeclared and justified transport rule. No placeholder members or plan ID should be added to gamma now.

### Freeze order and lead gates

1. **Ruling gate:** lead accepts the session-capability semantics, zero-retry policy, successor corpus rule, four-cell artifact shape, and fourth-window treatment.
2. **Toolchain gate:** ledger session/binding, successor builder, pinset v2, multi-cell mint, prefill metric support, and three-window regression all land and pass focused plus canonical suites.
3. **Desk freeze gate:** generate all three campaign packs; freeze identifiers, model revisions, configs, manifests, condition families, extraction/analysis specs, budgets, failure policy, and hashes. Six-decimal values do not yet exist.
4. **Per-window arm gate:** attach current clean head, acceptance artifact, physical/committed ledger equality, fresh roots, exact environment preflight, empty waivers, §5A evidence, and bracket-session identifiers.
5. **Pre-science trigger gate:** finalize the pre observation and either accept it, issue a governed successor, or abort before member one.
6. **Post-window gate:** finalize post, commit terminal head, issue bracket binding, verdict, and verified backup.
7. **Floor mint gate:** after alpha and beta pass, run governed four-cell extraction, independently freeze literals, mint the combined artifact, and require `validate_floor_artifact` to return no findings.
8. **Gamma claim gate:** pass the whole-window verdict, finalize the v3 basis, run D-093 root scanning, resolve both decode arm floors from exact combined-artifact bytes, and apply the armwise maximum.

### Work-order list with enforced WRITE_SCOPE units

| Unit | Exact write scope | Invariants and tests | Dependency |
|---|---|---|---|
| U1 — ledger session and binding | `joulewise/calibration_ledger.py`; `joulewise/calibration_bracketing.py`; `scripts/reserve_calibration_window_bracket.py`; `tests/test_calibration_ledger.py`; `tests/test_calibration_bracketing.py` | Two immutable slots, one-use finalization, governed abort, no unresolved-candidate leakage, exact binding, head/pin refusals. Focused ledger/bracketing tests plus full suite. | Foundation; independent of U3 |
| U2 — D-102 successor engine | `joulewise/calibration_bracketing.py`; `scripts/build_calibration_acceptance_successor.py`; `configs/calibration/calibration_acceptance_registry.json`; `tests/test_calibration_acceptance_successor.py` | Complete authenticated live prefix, deterministic bytes, parent ancestry, exact Decimal derivation, range/count triggers, systematic refusal. Focused cold-gate fixtures plus full suite. | Sequential after U1 because of shared bracketing semantics |
| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
| U4 — three-window ledger regression | `tests/fixtures/calibration_live_three_window/**`; `tests/test_calibration_live_three_window.py` | Exact issuance fixture, import exclusion, six live candidates, three causal bindings, successor and refusal vectors. | After U1 and U2 |
| U5 — alpha campaign pack | `configs/campaigns/d117_floor_qwen25_1p5b_v1/**`; `configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json`; `tests/test_d117_floor_qwen25_1p5b_plan.py` | Exact 10+40 schedule, split midpoint, two metric riders, 50 unique bundles, fresh IDs, deterministic regeneration. | After U3 schema/IDs freeze; parallel with U6 |
| U6 — beta campaign pack | `configs/campaigns/d117_floor_qwen25_7b_v1/**`; `configs/floor_mint/d117_qwen25_7b_extraction_spec.json`; `tests/test_d117_floor_qwen25_7b_plan.py` | Same as U5, retaining D-085 stack/family identity. | After U3; parallel with U5 |
| U7 — gamma campaign pack | `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/**`; `tests/test_d117_decode_contrast_plan.py` | Forty ABBA members, decode-only metric, B−A orientation, v3 estimator, exact four-cell artifact consumer pins, no prefill placeholder. | After U3 floor cell/transport IDs freeze |
| U8 — operator/readiness packet | `docs/phase_2/window_runbook.md`; `scripts/validate_frozen_plan_readiness.py`; `tests/test_frozen_plan_readiness.py` | §5A sequence, session capability, pre-trigger successor gate, fresh roots, empty waivers, terminal binding/pin/backup. | After U1, U2, U5–U7 |
| U9 — state and custody bookkeeping | `docs/process/state_kernel.json`; `RUN_STATE.md`; `TASK_QUEUE.md`; `CLAIMS_STATUS.md`; `docs/run_reports/2026-08-07-d117-plan-freeze.md` | D-117 vocabulary, no C/D plan references, exact frozen digests, generated-view consistency. | Lead-owned, after all desk artifacts pass |
| U10 — postcollection pin closure | `scripts/floor_mint_pinsets/d117_qwen25_1p5b_v2.json`; `scripts/floor_mint_pinsets/d117_qwen25_7b_v2.json`; `scripts/floor_mint_pinsets/d117_qwen25_phase_floor_set_v2.json`; `results/floor_artifacts/d117_qwen25_phase_floor_set_v1.json`; `results/floor_artifacts/d117_qwen25_phase_floor_set_v1.sha256` | Only postcollection facts; independent literal recomputation; exact receipt/binding/head pins; validator returns no findings. | Sequential after alpha and beta pass |

Every unit should run its focused tests and `python3 -m unittest discover -s tests`. Shared files make U1→U2 sequential; U1 and U3 can proceed independently. U5 and U6 can proceed independently after U3 freezes the vocabulary. U7 waits for final floor-cell and transport identifiers. U10 is deliberately absent from the desk freeze.

### What the lead should double-check

- Recover the missing prefill-feasibility trace and compare its exact 256-token assumptions with this fourth-window conclusion.
- Ratify the two-slot ledger capability against D-109/D-116, especially whether an open post slot may exist during the pre-science successor probe.
- Decide explicitly between zero calibration retries and a prospectively numbered retry-capability variant.
- Ratify the D-102 successor corpus rule: all content-distinct valid same-epoch observations through the cutoff.
- Confirm that D-085’s 7B decode family ID is preserved and contrast transport uses allowlists rather than relabeling configs.
- Confirm pinset v2 supports multiple producer plans while preserving byte-for-byte v1 behavior.
- Verify the 20% allowance does not become permission for member replacement or result-driven top-up.
- Recheck full model revisions, local artifact hashes, runtime version, charger identity, and post-move environment at each arm.
- Independently calculate all four `.6f` operative literals from primary extraction bytes.
- Verify every one of the fifty floor bundles actually contains the registered prefill phase; a missing phase must fail extraction.
- Ensure gamma takes the maximum of the two decode arm floors, never their sum, and retains separate claim-side anchor bounds.
- Ensure the 128-prompt prefill riders are not presented as a floor for a later 256-token contrast without exact transport evidence.
- Regenerate the active queue from the state kernel so superseded C/D and D-110 gates cannot be mistaken for arm authority.
- Freeze against the final reviewed repository head; this consult began at `dbb9685` and ended cleanly at concurrently advanced `94a24e5`.

## Residual risk

No live timings, calibration observations, successor generation, or mint replay were performed. Runtime estimates therefore inherit historical-machine variance; the 20% margin is the current mitigation.

The absent feasibility synthesis limits review of the optional 256-token arm. Its attachment architecture is sound, but its member count, runtime, estimand, and floor transport remain intentionally unfrozen.
exec
/bin/zsh -lc "sed -n '1,280p' docs/strategy/2026-08-06-impressiveness-roadmap.md
sed -n '1,220p' docs/research_question_registry.md
sed -n '1,120p' docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The strongest feasibility-weighted path is a clean C/D metrology campaign, external wall validation, and an evaluation-ready artifact before adding one hypothesis-driven expansion.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "head_end": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "upstream_end": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The paper's claim-bearing experimental spine is not yet complete",
        "detail": "D-110 still withholds the floor and contrast artifacts pending issuance/remint, while D-113 requires fresh Window C collection, prospectively split into D if needed."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "D-041 is not the mechanism-level fence",
        "detail": "D-041 governs external-benchmark import/export and limits the export shim to an energy layer; AXI mechanism studies are governed primarily by D-070, D-075, their analysis plans, and runtime feasibility verdicts."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Venue and calendar ambition remain unbound",
        "detail": "The report deadline, colloquium, 3080 Ti window, and venue-specific evidence-by dates remain TBD, preventing rational allocation of measurement nights."
      },
      {
        "id": "F4",
        "severity": "nit",
        "title": "The requested methods draft is not on main",
        "detail": "docs/paper/draft-v1.md exists on impl/paper-draft-v1 but is absent from main; the branch version was inspected for this review."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse --abbrev-ref HEAD && git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "665fd5821f74e579071fba9ddd9717b77ded6a01",
          "main",
          "origin/main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "665fd5821f74e579071fba9ddd9717b77ded6a01\\nmain\\norigin/main"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "test ! -e docs/paper/draft-v1.md && git cat-file -e impl/paper-draft-v1:docs/paper/draft-v1.md && printf 'draft_main=absent\\ndraft_branch=present\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "draft_main=absent",
          "draft_branch=present"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "draft_main=absent\\ndraft_branch=present"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The prompt identifies docs/paper/draft-v1.md as current, but it is present only on the impl/paper-draft-v1 branch.",
      "needs": "Lead should integrate or otherwise disposition the paper-draft branch."
    },
    {
      "id": "FL2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No test suite was run because this was a read-only strategic synthesis with no repository modifications.",
      "needs": ""
    }
  ]
}
```

## Findings

### F1 — Finish the claim-bearing metrology spine before expanding

The instrument and its evidence machinery are unusually mature, but the paper still lacks a complete claim-bearing characterization result. The 1.5B/7B contrast passed collection gates and is a compelling preliminary demonstration, yet D-110 prevents formal use until the issuance/remint chain completes. D-113 then requires fresh Window C collection—split into D if necessary—without importing any retired Window B member. See [D-113](/Users/edr/code/JouleWise/docs/decision_log.md:7240) and the [current paper outline](/Users/edr/code/JouleWise/docs/run_reports/2026-07-30-paper-outline-v1.md:1).

That is the critical path. A broad paper with incomplete C1–C6 evidence will look less serious than a narrower paper that cleanly demonstrates linearity, null response, empirical floor behavior, additivity, drift/settling, and between-session stability.

D-113’s rigor-first posture forbids:

- Salvaging failed A/B data into replacement claim cells.
- Excluding an inconvenient member after seeing results.
- Compressing an oversized campaign into one night.
- Weakening calibration, whole-window, clock, or custody gates for schedule reasons.
- Adding process or repetitions without a named validity threat or material claim benefit.

It explicitly permits—and often prefers—smaller independent windows, narrower claims, and cutting an expansion.

### F2 — Exact D-041 ruling and the real mechanism fence

D-041 is titled “Benchmark interop — frozen-subset imports + marker-shim energy layer.” It fences:

- External benchmark imports to hash-frozen subsets with identity, licensing, and contamination records.
- Export to a marker-emitting shim where the external harness owns prompts, generation semantics, and accuracy; JouleWise owns capture, bundle assembly, marker validation, and energy reduction.
- Joined reporting to observed energy beside the external metric artifact—never JouleWise accuracy, pass@k-per-joule, leaderboard standing, or intelligence-per-joule.
- Implementation to after 2M and P2-010a, unless D-034 is explicitly reopened.
- Interop expansion to be cut before core Mac characterization under schedule pressure.

Thus, “unfencing D-041” would require completing 2M and P2-010a—or an explicit decision reopening D-034/D-041 sequencing—then passing P2-022’s marker feasibility spike and writing an analysis-plan row before any L2 claim. It still would not authorize mechanism attribution.

The KDA/speculative-decode/MTP/MoE program is instead governed by D-070/D-075 and the AXI contracts:

- Post-core/floor sequencing.
- L2 ceiling for named studies unless Q4’s independent L3 machinery applies.
- Direct observability rather than inference from configuration.
- Output/quality-equivalence controls.
- Named forbidden generalizations.

The current feasibility facts matter:

- External-draft speculative generation exists, but pinned `mlx-lm` lacks actual proposal counts and decode-step emission boundaries.
- Native MTP is unsupported: the pinned runtime does not execute the heads.
- KDA/hybrid comparisons currently involve cross-model confounding and unverified long-context execution.
- MoE mechanism language requires auditable routing evidence; otherwise the claim must remain a named-model energy comparison, not routing attribution.
- No tracked repository document uses “KDA” as a governed project axis; it appears in the nonbinding mechanism-literature sweep, not D-041.

### Ranked roadmap

Planning estimates below assume the current 2–4-hour claim-window protocol, at least 20% failure margin, and physical Ed preparation through §5A.

| Rank | Expansion | Why it impresses reviewers | Estimated effort and Ed-present sessions | Dependencies and principal risk | Decision required |
|---:|---|---|---|---|---|
| **1** | **Complete C1–C7 cleanly: remint, fresh C/D, and stability** | Converts the strongest idea—the instrument and its refusal behavior—into actual evidence. This is the difference between an elaborate methodology and a metrology paper. | **3–6 weeks after desk gates; 2 mandatory nights plus 1 contingency/short stability session.** | D-079 issued artifact; D-110 remint; reviewed frozen-plan record; fresh §5A; C/D split if scope cannot fit. Risk: another environmental or clock refusal. | Reserve the core nights now and prohibit breadth work from consuming them. |
| **2** | **External wall-meter validation of totals, C8** | Directly addresses the obvious reviewer question: “Does `powermetrics` agree with physical input power?” It materially upgrades absolute-scale credibility. | **4–8 weeks; 1 pilot plus 1 confirmatory session.** The confirmatory run may share a later frozen campaign only after the importer and protocol pass independently. | Professional AC analyzer, safe inline fixture, synchronized export, fixed ranges, load-specific uncertainty, battery charge neutralization, held-out regression. It validates totals only—not phase allocation. | D-092 already decided “yes”; Ed/advisor must now authorize purchase/loan, budget, and an evidence-by date. |
| **3** | **Artifact-evaluation-quality release** | Hash-bound raw-to-figure reproducibility is a genuine differentiator and unusually well aligned with JouleWise’s thesis. Reviewers can verify refusals and re-derive results rather than trust screenshots. | **4–6 weeks; 0 measurement nights.** | Sanitized raw-bundle subset, one-command validation/reduction/figure path, locked environment, quick/full tracks, immutable archive/DOI, clear hardware-free replay. Risk: privacy, dataset size, and Mac-only collection requirements. | Decide whether the target is merely open source or formal ICPE-style artifact evaluation, and which evidence may be public. |
| **4** | **Designed workload-shape matrix with held-out prediction—Q4/L3** | A predictive fixed-plus-marginal model validated on held-out cells is substantially more serious than “we ran more prompts.” It can earn L3 rather than another collection of L1/L2 points. | **6–10 weeks; approximately 2–3 nights.** | P2-006 baseline sizing, AP-1, 4×3 grid, predeclared holdouts, residual/sensitivity analysis, floor audit. Risk: the simple model may fail its holdouts—which must be reported honestly. | Fund the full designed matrix or omit the predictive claim; do not replace it with opportunistic workload breadth. |
| **5** | **Quality-gated BF16/Q8/Q4 quantization ladder** | A clean same-family ladder with error bars and output-divergence reporting can adjudicate the reported q4-vs-q8 anomaly. Strong workshop demonstration; moderate novelty. | **4–8 weeks; 1–2 nights.** Quality screening can run outside quiet windows. | One frozen source revision, reproducible conversions, 256-item quality gate, 32-item energy subset, stack-specific floors. Risk: quality may not be equivalent or quantization may alter cadence beyond existing calibration support. | Choose the model family before conversion; accept a quality/energy trade-off result if equivalence fails. |
| **6** | **Second-unit replication after multi-day same-unit stability** | This is the clearest path beyond single-machine claims and toward L4. It demonstrates that the artifact and calibration method transfer, not merely that one laptop is stable. | **4–8 weeks once access exists; 2 sessions on the second unit, 0–2 Ed-present depending on operator.** | A second comparable Apple unit, frozen stack or explicitly modeled version difference, independent calibration and artifact execution. Risk: OS/hardware drift may make it replication-aware rather than directly pooled. | Secure a second unit/collaborator or explicitly retain the single-unit ceiling. |
| **7** | **One mechanism-level study, conditional on a hard feasibility gate** | **Highest scientific ceiling.** A controlled batch-1 speculative-decode or MTP energy result could be genuinely novel; KDA/context slope or MoE routing is also interesting if attribution is identifiable. | **2–3-week desk feasibility gate; if passed, another 6–12 weeks and roughly 2 nights.** | New/forked runtime instrumentation, direct proposal/acceptance events, output identity/equivalence, mechanism-specific AP and floors. MTP currently cannot execute; KDA is confounded; MoE routing visibility is uncertain. | Pick exactly one mechanism and a kill date. Recommended first choice: external-draft speculative decode, because it offers the cleanest same-target on/off contrast if observability can be added. |
| **8** | **Split inference: synthetic transfer plus one offline split pairing** | Demonstrates the instrument under two boundaries, a transfer interval, and cross-device clocks. A complete per-stage bundle is impressive even without a crossover. | **2–4 months; roughly 3–5 two-device measurement sessions.** Live split adds more and should remain stretch. | Schema v0.2, remaining replay verdicts, two-node telemetry, clock bounds, transfer bench, 3080 Ti window, two links, wall/host boundary or lower-bound wording. Risk is high and the engineering can dominate the paper. | Commit only to synthetic transfer plus offline replay; authorize live split separately after offline results. |
| **9** | **Additional model families, generic workloads, Jetsons** | Useful corroboration, but mostly incremental unless each addition tests a predeclared hypothesis or provides independent replication. More rows do not overcome the single-unit or boundary limitations. | **3–8 weeks and 1–2 nights per coherent axis/device.** | New model lineage, adapter, quality and floor cells; Jetson remains optional and remote pins are provisional. | Add only a model or device that changes the claim—not merely the size of a results table. |

For the wall-meter path, the right class is a calibrated bench AC power analyzer, not an inexpensive consumer plug. A concrete baseline is the Yokogawa WT310E: its manufacturer lists 10 readings/s, USB export, 0.1%-of-reading plus 0.05%-of-range basic accuracy, high crest-factor capability, and a **$2,935 base US price** before calibration/fixture costs. Actual suitability still depends on calculating uncertainty at the Mac’s observed load and using a safe inline fixture. Borrowing an in-calibration unit from an engineering lab is preferable to spending several thousand dollars. [Yokogawa WT310E specifications and current price](https://tmi.yokogawa.com/us/solutions/products/power-analyzers/digital-power-meter-wt300e/).

### Venue ambition

| Tier | What the current/expanded project can support | What should be present |
|---|---|---|
| **CSCSU** | After remint and clean C/D, this should be a strong undergraduate-conference submission. The latest published rules allow technical papers and extensive experimentation, with **5 pages including references**. [CSCSU 2026 guidance](https://cscsu-conference.github.io/) | C1–C6 core, one demonstration, crisp limitations, compact artifact pointer. Wall validation and split are not necessary. |
| **EuroMLSys/HotCarbon workshop** | The natural near-term research target. EuroMLSys’s latest call uses 6 pages excluding references; HotCarbon uses 5 pages excluding references and no appendix. [EuroMLSys](https://euromlsys.eu/), [HotCarbon CFP](https://hotcarbon.org/cfp) | Clean metrology core, model contrast, wall validation if available, and polished artifact. EuroMLSys is the better technical-method fit; HotCarbon needs a stronger sustainability-metrics argument. |
| **ICPE Emerging/WIP** | Appropriate if the core is strong but external validation, replication, or the broader predictive evaluation remains incomplete. The 2026 track used a 6-page format. [ICPE Emerging Research](https://icpe2026.spec.org/tracks-and-submissions/emerging-research-track/) | Validated core, transparent open gaps, early artifact, and a credible expansion plan. |
| **ICPE full research track** | Plausible over months, but not yet supported by the current evidence. ICPE 2027 lists research and artifact tracks but their details and dates remain TBA. The 2026 research track used 10 pages and judged novelty, technical quality, and scientific soundness; 2026’s reported full-paper acceptance rate was 28%. [ICPE 2027](https://icpe2027.spec.org/tracks-and-submissions/research-paper-track/), [2026 research criteria](https://icpe2026.spec.org/tracks-and-submissions/research-paper-track/), [acceptance history](https://icpe.spec.org/past-conferences/) | C1–C8, cross-day stability, artifact-ready release, and at least one deeper contribution: held-out Q4 prediction, second-unit replication, or a successful mechanism study. Split is not required. |

ICPE’s artifact track is especially aligned: it asks for documented, consistent, complete, exercisable artifacts, permanent archival availability, and practical setup/reproduction instructions. [ICPE artifact-evaluation criteria](https://icpe2026.spec.org/tracks-and-submissions/artifact-evaluation-track/).

### Critical path to the strongest defensible version

1. **Now:** finish D-079 issuance and the D-110 remint chain; integrate or disposition the draft branch; set actual calendar and venue evidence-by dates.
2. **In parallel:** borrow/order the wall analyzer and build its importer, synchronization, and held-out validation protocol without assuming it will arrive in time.
3. **First hardware block:** freeze and collect Window C, then D if the complete replacement cannot fit with the required margin. Add a third short day/session only if needed for the stated stability claim.
4. **Immediately after each passing window:** produce the governed artifacts, deterministic figures, claim-index entries, and experimental prose. Do not wait for all expansions before writing.
5. **Artifact block:** publish a sanitized, hash-bound raw-to-figure package with a fast hardware-free reproduction path and archival DOI.
6. **Second hardware block:** run external wall validation.
7. **Choose one expansion:** Q4 held-out prediction for the strongest ICPE case; quantization for the safest workshop enhancement; or mechanism work only if its short feasibility gate passes.
8. **Only then consider split inference.** Start it only if the 3080 Ti window is dated and the transfer/offline-replay path is rehearsed before hardware access.
9. **Freeze the dataset early:** reserve at least six weeks before submission for figures, claims audit, paper compression, artifact dry runs, and advisor review.

The strongest realistic paper is therefore: **C1–C8 metrology + the already-collected 1.5B/7B demonstration + one designed extension + an independently usable artifact.** That is more coherent and defensible than a larger model/device matrix or an unfinished split system.

### F3 — Five decisions Ed/advisor must make

1. **Venue and publication sequence.** Choose CSCSU-only, workshop-first, or ICPE-full ambition, and verify whether a workshop publication may later be extended for ICPE. Build a 10-page master manuscript even if the first submission is shorter.

2. **Physical measurement budget.** Recommended commitment: **5–7 Ed-present sessions**—C, D, one contingency/stability repeat, wall pilot/confirmation, and one extension. An ICPE-full attempt with Q4 and second-unit work likely needs **8–10 total sessions** across operators.

3. **Meter execution.** D-092 has already answered “yes.” The remaining decision is: borrow versus buy, approximately $3,000-class budget, calibration/fixture responsibility, and a cutoff date after which C8 is cleanly removed.

4. **Mechanism ambition.** Do not ask simply “unfence D-041.” Decide whether to retain D-070’s all-five-axis commitment or narrow it to one paper-worthy study. Recommended rule: two-to-three-week feasibility gate for speculative-decode observability; if it fails, return immediately to Q4/quantization.

5. **External hardware priority.** Decide whether scarce coordination goes to a second Apple unit, the 3080 Ti split study, or Jetsons. Recommendation: second-unit replication first, 3080 Ti second, Jetsons last.

### F4 — Draft-state correction

The methods draft was inspected from `impl/paper-draft-v1` at commit `af0b7195`; it is one commit ahead of and one commit behind `main`. It already reflects the right rigor: result placeholders remain pending remint, all characterization rows are pending Window C, and the split section is framed as future demonstration work. It should be integrated deliberately so the paper itself becomes the continuously updated claim-state surface.

## Residual risk

- The mechanism-literature sweep is explicitly desk research, not governed project evidence. Any “first measured” novelty claim needs a fresh literature search immediately before submission.
- Venue formats and deadlines cited above are current published 2026 rules or incomplete 2027 pages; 2027 calls may change.
- Measurement-night estimates are planning ranges, not validated campaign runtimes.
- Wall validation cannot establish phase attribution, and one external meter does not create cross-device generality.
- Even an excellent single-Mac study remains stack-specific under the claims ladder unless second-unit or cross-lab replication lands.# Research Question Registry

Purpose: this is the canonical live index for JouleWise research questions,
capability claims, application ideas, and methodology artifacts. It normalizes
aliases, status, claim ceilings, owners, gates, and pre-hardware readiness so
claims and campaign plans can point to one row. Promotion rules are unchanged
from `docs/research_question_bank.md`: promotion still requires a named RQ slot
in `PROJECT_STATUS.md`, a data plan that does not displace queue ranks above
it, and scope fit.

Maintenance rule: registry rows are LIVE state. The research question bank
remains the historical and deliberative record, including council wording,
kills, quarantines, and amendments. Single-writer split: update this registry
for current indexing and cross-references; update the bank only when recording
new deliberation history.

Column legend:

- `canonical_id`: stable row key for the live index.
- `aliases`: other IDs, names, or capability-map labels for the same question.
- `question_type`: one of `research question`, `capability claim`,
  `application idea`, or `methodology artifact`.
- `status`: `promoted`, `banked`, `candidate`, `killed`, `answered-L1`, or
  the review-specific `candidate (C-023)`.
- `claim_ceiling`: highest claim level currently allowed by the bank, review,
  or capability map, before future evidence upgrades.
- `forbidden_upgrade`: short reminder of language the row cannot support.
- `AP owner`: analysis-plan owner if already named; otherwise `none-yet`.
- `campaign owner`: queue row, phase, or campaign owner if already named.
- `gate_class`: dominant gate class: `hardware`, `software`, `floor`,
  `substrate`, or `coordination`.
- `pre_hardware_preparable`: `fully`, `analysis-plan-only`, or `no`.
- `one-line note`: indexing note, not a re-adjudication.

## Registry Table

| canonical_id | aliases | question_type | status | claim_ceiling | forbidden_upgrade | AP owner | campaign owner | gate_class | pre_hardware_preparable | one-line note |
|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | Split reduces energy | research question | promoted | L2 boundary-labeled; stronger only with calibration | no uncalibrated cross-boundary total-energy winner | none-yet | Phase 3 split; P1-004; P1-006 | hardware | fully | Central split question; total energy must be decomposed and boundary-labeled. |
| Q2 | Link bandwidth sensitivity | research question | promoted | L2 | no nominal-link crossover without measured links | none-yet | Phase 3 split; P1-004 | hardware | fully | Clean interconnect sensitivity question; link throughput and transfer energy must be measured. |
| Q3 | Split energy-latency Pareto | research question | promoted | L2 | no Pareto claim without frozen set and latency metric | none-yet | Phase 3 split | hardware | fully | Requires a fixed comparison set and latency metric per figure. |
| Q4 | Fixed-vs-marginal energy model; C5-2.14 cache-policy coefficient rider | research question | promoted | L3 | no holdout-prediction claim without AP-1 floor and residual checks | AP-1 | P2-019 q4_l3_shape_grid_v1 | floor | analysis-plan-only | Strongest predictive science row; includes compositional split-energy prediction only when transfer terms exist. C5-2.14 is a candidate rider capped at L2, earliest PF, with no coefficient-direction claim below P2-015 floors ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| Q5 | Ranking stability | research question | promoted | L2 | no uncalibrated cross-device winner; no ranking where gap below MDE | AP-3 | 2M; Window B grid | floor | analysis-plan-only | Promoted within-machine ranking question; workload-axis analogue C5-W.3 remains a separate candidate row. |
| Q6 | Boundary sensitivity; C5-2.10 boundary-directional bias quantification | research question | promoted | L2; L4 only with replication | no wall/rail conclusion flip claim without paired boundary plan | none-yet | P1-003 wall meter; F11 | hardware | fully | Registry indexes C5-2.10 as the C5 elaboration of promoted Q6. |
| RQ-METHOD-FLOOR | Detection floor; noise floor; short-difference resolvability; phase/item identifiability flags; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | banked | L1 methodology | no below-floor effect language except `not resolvable`; no module-energy fraction or regression-slope attribution | none-yet | P2-015 | floor | analysis-plan-only | Methodology centerpiece and prerequisite for most comparative claims; the candidate module-attribution nonclaim attaches here at earliest NS instead of becoming a row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.11 | Dark silicon; rail utilization; ANE-dark finding | research question | candidate | L2 structural | no true silicon-energy fraction from modeled rails | none-yet | P2-009 rich telemetry; C5-1.8 runtime grid | software | analysis-plan-only | Measures modeled-rail utilization structure, not physical absolute rail truth. |
| C5-1.3 | CPU:GPU phase division; rail/DVFS phase signatures; prefill/decode power asymmetry | research question | candidate | L2 structural | no short-phase joules when windows are under-resolved | none-yet | 2M with P2-009 | floor | analysis-plan-only | Merges the banked CPU:GPU phase question with C5-1.3 telemetry framing. |
| RQ-KV-GROWTH | KV-growth decode drift; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | banked | L1/L2 chunked | no per-token joule claims; no attention-vs-FFN fraction from context slopes | none-yet | none | floor | analysis-plan-only | Candidate riders, earliest PF: bounded-window KV marginal slope and named-artifact attention/context slope; both retain chunked-window/floor discipline and stay attached rather than becoming independent rows ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.5 | Cooldown recovery as thermal characterization; cooldown-recovery curves | research question | candidate | L1/L2 | no claim that power recovery proves thermal-state equality | none-yet | none | floor | analysis-plan-only | Turns cooldown tails and cap-hit rates into reportable methodology evidence. |
| C5-1.10 | Failure frontier | research question | candidate | L1/L2 descriptive | no silent discard of failures; no population claim from one memory class | none-yet | none | software | analysis-plan-only | Structured `unsupported`, fit, swap, throttle, and cap-hit outcomes become data. |
| C5-1.7 | Cold-start / keep-warm energy; reload-vs-resident scheduling | research question | banked | L2 after harness extension | no breakeven without load-window and resident-idle sampling | none-yet | none | software | analysis-plan-only | Review and bank both identify reload-vs-resident as the same question. |
| C5-1.9 | Energy-per-correct-answer vs difficulty; MoE-vs-dense controlled ladder | research question | banked | L2 after envelope and denominator guards | no intelligence-per-joule; no `difficulty causes energy` | AP-5 | P2-010a plus P2-010b plus later scored campaign | substrate | analysis-plan-only | Correctness remains quarantined annotation under the C-004/C-014 rules. |
| C5-2.5 | Speculative-decoding energy; C5-2.5b proposal-work rider; C5-2.5c break-even rider | research question | banked | L2 | no efficiency claim without output equivalence and accepted-token accounting | none-yet | none | software | analysis-plan-only | C5-2.5c is the primary PF Q4 rider, C5-2.5b its PF secondary, and C5-2.5d the mandatory PF contamination control; C5-2.5a remains a deferred NS bank rider. `C-023-OUTPUT-IDENTITY` binds all efficiency contrasts ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-POWER-MODE | Power-mode Pareto | research question | banked | L2 possible | no OS-mode conclusion until power mode is a first-class config field | none-yet | none | software | analysis-plan-only | Waits on config/environment capture for OS power modes. |
| RQ-INTELLIGENCE-PER-JOULE | General joules-per-solved-task; intelligence-per-joule | research question | killed | none | no general intelligence-per-joule ratio | none-yet | none | substrate | no | Killed/quarantined by C-003/C-004; controlled ladder is the surviving minimal form. |
| RQ-AUDITABLE-EVIDENCE | Can JouleWise produce auditable local-LLM energy evidence? | capability claim | answered-L1 | L0/L1 | no physical calibration claim from strict validation alone | none-yet | existing Mac/MLX/powermetrics bundles | software | no | Artifact contribution, not a research question. |
| RQ-QWEN25-SMOKE | Qwen2.5-1.5B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from smoke result | none-yet | 2026-07-06 2I | software | no | Legit instrument observation for one named stack/workload. |
| RQ-QWEN35-SMOKE | Qwen3.5-122B-A10B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from n=3 | none-yet | 2026-07-07 flagship addendum | software | no | Legit instrument observation for one named stack/workload. |
| RQ-TWO-MODEL-ACTIVE-NONCLAIM | Did the two observed models demonstrate active-parameter scaling? | capability claim | answered-L1 | L1 hypothesis only | no active-parameter scaling claim | none-yet | 122B addendum; capability map | floor | no | Negative guard: two points are consistent with a hypothesis but do not support scaling. |
| RQ-SHORT-PREFILL-RESOLVABILITY | Are short prefill phase joules resolvable?; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | answered-L1 | L1 `not resolvable` | no standalone short-prefill joule result; no relabeling request phases as module phases | none-yet | Phase 4 observation | floor | no | Existing cadence precedent owns the candidate module-attribution guard, earliest NS; no separate methodology row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-MLX-KV-REPLAY | Same-machine MLX KV replay token identity and size prediction; C5-2.13 | capability claim | answered-L1 | L1 feasibility | no cross-machine portability claim | none-yet | Stage 3.0.1 | software | no | The L1 feasibility result remains answered; candidate C5-2.13, earliest PF and capped at L2, attaches the same-machine energy-crossover rider without cross-stack generalization ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-MAC-BASELINES | Per-profile Mac baselines | capability claim | candidate | L1 per condition | no novelty or comparison claim without AP/floor | none-yet | 2M | floor | analysis-plan-only | Necessary baseline corpus, not a headline by itself. |
| RQ-SHAPE-ENERGY | Workload shape changes request energy | research question | candidate | L2 | no causal token-shape claim beyond AP-2 contrasts | AP-2 | 2M | floor | analysis-plan-only | Distinct from Q4 because it describes shape contrasts rather than holdout prediction. |
| C5-1.1 | Active-parameter energy scaling | research question | candidate | L2 pairwise only unless larger predeclared model set | no active+total+KV regression on 4-6 models | none-yet | P2-024 shortlist | floor | analysis-plan-only | C-014 caps the tempting wording; registry hygiene, not re-adjudication. |
| C5-1.2 | Context-length energy scaling; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | candidate | L2/L3 if modeled | no short-prompt phase point claims; no wall implication from SoC rails | none-yet | none | floor | analysis-plan-only | Natural local-inference question with chunked phase limits; the two candidate PF riders remain capped at L2 and forbid module attribution from context-associated slopes ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.4 | DVFS residency as throttling early-warning | research question | candidate | L2 if prediction rule fixed | no prediction claim without horizon and rule | none-yet | none | software | analysis-plan-only | Convert characterization to a predeclared warning rule before claiming prediction. |
| C5-1.6 | Sampling-strategy energy overhead | research question | candidate | L2 if above floor | no telemetry-perturbation claim from this row | none-yet | P2-024 shortlist | floor | analysis-plan-only | Bank row is greedy vs temperature/top-p/beam overhead, not sampler instrumentation cost. |
| C5-1.8 | Runtime energy attribution; same-silicon kernel-layer provenance rider | research question | candidate | L2 stack-vs-stack | no `belongs to runtime` or `belongs to kernel layer` language when artifacts/formats differ; no runtime-agnostic kernel claim | none-yet | P2-024 shortlist | floor | analysis-plan-only | Candidate NV provenance rider stays inside the stack-conditioned comparison; it does not mint C5-1.13 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.12 | Quantization benefit decomposition, Mac leg | research question | candidate | L2 | no quantization efficiency claim without output divergence reporting | none-yet | P2-024 shortlist | floor | analysis-plan-only | Splits benefit into lower watts vs shorter time on one stack/family. |
| C5-W.1 | Category beyond token counts; Token-Shape Sufficiency Null | research question | candidate | L2 | no category effect below floor or without shape control | AP-4 | jw_mixed_v1 after P2-010a | substrate | analysis-plan-only | Strong null-or-effect design for workload-category residuals. |
| C5-W.2 | Thinking-token inflation | research question | candidate | L2 | no cognition claim; attribute only to emitted-token/stop distributions | none-yet | jw_mixed_v1 natural-EOS pilot | substrate | analysis-plan-only | Operational-cost view for reasoning models under natural EOS. |
| C5-W.3 | Category energy-ranking stability; workload-axis Q5 analogue | research question | candidate | L2 | no category ranking claim where rank gap is below MDE or without workload-expansion gate | none-yet | jw_mixed_v1 workload expansion | substrate | analysis-plan-only | Workload-axis analogue of promoted Q5, not the same ratified question; asks whether code/long-context/reasoning categories flip model/quant ordering. |
| C5-I.3 | C5-W.4; FLORES tokenizer fertility tax | research question | candidate | L2 | no tokenizer efficiency ranking without semantic and token-matched legs | none-yet | FLORES after HumanEval smoke | substrate | fully | C5-I.3 and C5-W.4 are the same FLORES fertility question. |
| C5-I.1 | External benchmark energy signatures | research question | candidate | L2 | no benchmark capability or accuracy claim | none-yet | import/export contracts | substrate | fully | Needs matched shape/output policy before family-level energy signatures. |
| C5-I.2 | Published-difficulty strata vs energy | research question | candidate | L1 association; L2 only if preplanned repeated bundles | no `difficulty causes energy` | none-yet | import/export contracts | substrate | fully | Weak/secondary because source difficulty labels are heterogeneous. |
| C5-I.4 | Harness overhead floor | methodology artifact | candidate | L1/L2 | no item energy claim when harness overhead dominates unnoticed | none-yet | P2-022 shim | substrate | fully | Methodology question for marked external harnesses. |
| C5-I.5 | Prompt-template energy sensitivity | research question | candidate | L2 | no prompt-quality or capability claim | none-yet | import/export contracts | substrate | fully | Same external item, canonical vs JouleWise-rendered prompt format. |
| RQ-CONTENT-SENTINEL | Synthetic prompt content sentinel; fixed-shape content sensitivity | research question | candidate | L2 | no content-effect claim unless realized shape/stop policy stays matched and effect clears floor; no broad content-neutrality claim beyond the five tested AP-6 conditions | AP-6 | P2-020 content sentinel | substrate | analysis-plan-only | Tests whether synthetic prompt content matters at fixed shape under the AP-6 ids-native no-BOS sentinel design. |
| RQ-ENERGY-VARIANCE | Sampling-induced energy variance; energy-at-risk per prompt; lucky-short-reasoning variance | research question | candidate | L2 within boundary | no intelligence-per-joule or correctness-causal claim (C-004 quarantine); variance claims need repeated-bundle n sized for variance estimation and floor-gated residuals; per-bundle sampler seeds must be recorded | none-yet | none (post-floor; reasoning model on current Mac feasible) | floor | analysis-plan-only | Ed-added 2026-07-09 row: distribution (not just mean) of request energy for a fixed hard prompt under sampling; decomposable into reasoning-length vs residual variance via recorded output token IDs + deterministic replay of sampled paths (P2-025 capture + 3.0.1 replay make paths replayable). |
| RQ-SESSION-SHAPE | Session-shape energy | research question | candidate | L2/L3 depending holdout | no app-session prediction without holdout validation | none-yet | suite profiles after P2-010a | substrate | analysis-plan-only | Tests whether Q4 coefficients compose in realistic session ecology. |
| RQ-ORDER-POSITION | Order-position effects | methodology artifact | candidate | L2 | no category/thermal inference without executable order policy | none-yet | suite profiles after ordering executability | substrate | analysis-plan-only | Drift/order probe; not a headline result. |
| RQ-CACHE-PREFIX | Cache/prefix economics; C5-2.13 | research question | candidate | L2 | no bundled cache-state conclusion without exact cache policy; no crossover generalization beyond the measured prompt-length ladder | none-yet | none | software | analysis-plan-only | Covers prefix reuse, resident state, and prompt-cache warmth; candidate C5-2.13 attaches a same-machine/same-stack energy crossover at earliest PF ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-AXI-HYBRID-PAIR | Named hybrid (SSM/attention)-vs-pure-transformer pair | research question | candidate | L2 pair-specific characterization | no architecture-class efficiency generalization, causal SSM-mechanism attribution, or tokenizer-blind ranking from one named pair | none-yet | post-floors named-pair campaign | floor | analysis-plan-only | Earliest PF; floor-gated and bindingly worded as “this named pair”; controlled-pair availability remains NEEDS-WEB ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-EXTERNAL-MARKED-RUNNER | External marked-runner energy layer | capability claim | candidate | L1/L2 with AP row | no accuracy, leaderboard, pass@k, or capability interpretation | none-yet | P2-022 | substrate | fully | Export-layer feasibility becomes research only when overhead/energy comparisons are specified. |
| RQ-HUMANEVAL-IMPORT-SMOKE | HumanEval import smoke | capability claim | candidate | L0/L1 | no coding-capability, pass@k, or accuracy claim | none-yet | P2-023 | substrate | no | Plumbing smoke for frozen external subset provenance. |
| C5-2.1 | Quantization decomposition, cross-stack | research question | candidate | L2 | no cross-boundary quant winner without calibration | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Extends C5-1.12 to CUDA/GGUF legs. |
| C5-2.2 | Batch size and prefill/decode energy split | research question | candidate | L2 | no serving conclusion without latency-bound policy | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Strong systems question for serving-style hardware and batching backend. |
| C5-2.3 | Predicted-vs-measured KV economics | research question | candidate | L2 | no KV economics claim without measured payload/link/deserialization terms | none-yet | P1-004 plus P1-006 | hardware | fully | One of the strongest Phase 3 questions; useful even if live split fails. |
| C5-2.4 | KV-cache quantization end-to-end; C5-2.11 on-device MLX leg | research question | candidate | L2 | no byte-saving equals energy-saving claim | none-yet | none | software | analysis-plan-only | Transfer leg still depends on cache portability; candidate C5-2.11 is the PF on-device MLX-scoped leg and also binds output-equivalence evidence ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.11 | On-device quantized-KV energy | research question | candidate | L2, per-boundary, MLX-scoped | no byte-saving-equals-energy-saving claim; no cross-runtime generalization from MLX alone; no quality-neutrality claim without C-023-style output-equivalence evidence | none-yet | post-floors Mac cache-policy campaign | floor | analysis-plan-only | Earliest PF; indexed under C5-2.4/C5-1.12/C-023-QUALITY-EQUIV-QUANT and runnable without the transfer leg ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.6 | Request coalescing under latency bound | research question | candidate | L2 | no scheduler optimum without arrival trace and latency policy | none-yet | none | hardware | analysis-plan-only | Useful but drifts toward scheduler research. |
| C5-2.7 | Device perf/W rankings with runtime held constant; kernel-provenance rider | research question | candidate | L2 within boundary; L4 with second unit/calibration | no generic hardware or cross-vendor kernel-API ranking from heterogeneous boundaries | none-yet | P1-006; 3080 Ti borrow window | hardware | fully | Candidate NV rider records attention-kernel/BLAS/graph provenance and remains per-boundary at L2; NEEDS-WEB feasibility stays open ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.8 | Placement-policy optimality from Q4 coefficients | research question | candidate | L2/L3 | no optimal-placement claim without measured split validation cells | none-yet | Phase 3 full set | hardware | fully | Uses Q4 coefficients plus measured transfer costs to choose placement. |
| C5-2.9 | Local-vs-datacenter crossover economics | research question | candidate | scenario result only | no measured-equivalent cloud comparison | none-yet | P1-003 plus P1-004 | hardware | analysis-plan-only | Surviving scenario form of the carbon-label kill. |
| C5-3.1 | Machine-to-machine variance; generalizability floor | research question | candidate | L4 enabler | no population claim from one unit | none-yet | second M-series unit | hardware | fully | Cheapest route from stack-specific to replication-aware claims. |
| C5-3.2 | Battery-path energy and modeled-rail validation | research question | candidate | L2/L4 bridge | no full-system claim from modeled rails alone | none-yet | USB-C PD analyzer | hardware | fully | Complements AC wall meter with a second physical boundary. |
| C5-3.3 | Cross-ISA NPU/SoC comparison; backend-provenance rider | research question | candidate | L4 only after replication | no broad cross-ISA claim before platform-specific adapter study; no NVIDIA-vs-AMD efficiency claim from single units or heterogeneous boundaries | none-yet | new platform adapters | hardware | analysis-plan-only | Candidate PC provenance rider is capped at L1 and records backend identity now; it creates no AMD science commitment ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-3.4 | Phone-class edge inference | capability claim | candidate | L0/L1 first | no promised phone science before telemetry feasibility | none-yet | phone feasibility | hardware | no | Feasibility verdict may be the result. |
| C5-3.5 | Cross-lab replication | methodology artifact | candidate | L4 enabler | no public benchmark credibility claim without replication | none-yet | external lab coordination | coordination | fully | Coordination-gated credibility layer. |
| C-023-TELEMETRY-PERTURBATION | Telemetry perturbation cost | methodology artifact | candidate (C-023) | L1/L2 floor component | no near-floor claim without telemetry-on/off ABBA check | none-yet | P2-015 component | floor | analysis-plan-only | New coverage-gap row; distinct from C5-1.6 sampling-strategy overhead. |
| C-023-VERSION-DRIFT | OS/runtime version-drift forensics; OS/driver/runtime update forensics | research question | candidate (C-023) | L1/L2 stack-conditioned | no version regression claim without before/after pinned bundles | none-yet | none | software | analysis-plan-only | Turns version churn into a named science/application row. |
| C-023-MARKER-JITTER | Marker/window jitter sensitivity; sampler-phase jitter sensitivity | methodology artifact | candidate (C-023) | L1 methodology; blocker for phase/item claims | no phase/item joule claim without jitter/sampler-phase sensitivity bound | none-yet | P2-015 or claim gate | floor | analysis-plan-only | Quantifies reducer sensitivity to timestamp jitter and sampler phase offset. |
| C-023-OUTPUT-IDENTITY | Output-token identity effects; binding gate for C5-2.5a/b/c/d | methodology artifact | candidate (C-023) | L1/L2 depending comparison | no quant/runtime/spec-decoding efficiency claim without equivalence or divergence report | none-yet | none | software | analysis-plan-only | Fixed output-token count is not fixed decoded work; binding for the PF/NS speculative-decoding riders admitted by D-075 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C-023-IDLE-STATIONARITY | Idle-baseline stationarity | methodology artifact | candidate (C-023) | L1 methodology | no idle-subtracted conclusion without idle model-choice sensitivity | none-yet | P2-015 component | floor | analysis-plan-only | D-067 CLOSED the headline-basis question: gross energy within the named boundary is primary. This row stays alive only to test how idle-model choice affects conclusions in the labeled within-device SECONDARY view. |
| C-023-QUALITY-EQUIV-QUANT | Quality-equivalent quantization comparisons; C5-2.11 gate | research question | candidate (C-023) | L2 after equivalence rule | no quantization efficiency or quality-neutrality claim without AP-level equivalence rule | none-yet | none | software | analysis-plan-only | C5-2.11's candidate PF on-device KV leg binds this gate; footprint savings alone do not establish energy or quality neutrality ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C-023-COEFF-TRANSPORT | Coefficient transport synthetic-to-realistic; energy model portability across workload mixtures | research question | candidate (C-023) | L2/L3 depending holdout | no realistic-session prediction from synthetic grid without transport validation | none-yet | suite traces after Q4 | substrate | analysis-plan-only | Explicitly tests Q4 coefficient transport from synthetic grids to realistic app traces. |
| APP-PROMPT-PROFILER | Prompt/template energy profiler | application idea | candidate | internal L1/L2 only | no prompt-quality claim | none-yet | none | software | analysis-plan-only | Product-facing use of prompt/template energy sensitivity. |
| APP-BUNDLE-POWER-BUG | Attach-a-bundle power-bug repro | application idea | candidate | L0/L1 support workflow | no general bug diagnosis without reproduced bundle | none-yet | none | software | analysis-plan-only | Uses bundle completeness as a maintainer repro artifact. |
| APP-CI-ENERGY-GATES | CI energy-regression gates | application idea | candidate | internal L1/L2 after floors | no CI failure threshold below detection floor | none-yet | P2-015 prerequisite | floor | analysis-plan-only | Needs floors, env snapshots, and baseline-refresh policy. |
| APP-VENDOR-PRESS-AUDIT | Vendor/press claim audit | application idea | candidate | boundary-named L1/L2 | no absolute device-energy verdict without calibration | none-yet | none | hardware | analysis-plan-only | Can audit specific boundary/workload claims, not universal efficiency. |
| APP-MODEL-CARDS | Practitioner energy model cards / leaderboard | application idea | candidate | internal only until L4 replication | no public leaderboard before cross-lab replication | none-yet | C5-3.5 prerequisite | coordination | analysis-plan-only | Internal table can exist; public version is killed until replication. |
| APP-TEACHING-INSTRUMENT | Teaching instrument | application idea | candidate | pedagogical L0/L1 | no research generalization from teaching bundles | none-yet | none | software | analysis-plan-only | Uses bundles for methodology labs on boundaries, floors, and uncertainty. |
| APP-STANDARDS-CONTRIBUTION | Bundle contract as standards contribution | application idea | candidate | methodology artifact proposal | no claim to be the standard | none-yet | none | coordination | analysis-plan-only | Exports the artifact format and validation discipline. |
| APP-CARBON-LABELS | Carbon labels | application idea | killed | none | no carbon label without wall meter and grid assumptions | none-yet | none | hardware | no | Killed as product label; C5-2.9 is the surviving scenario question. |
| APP-BATTERY-RUNTIME | Battery-runtime estimates without calibration | application idea | killed | none | no battery-runtime estimate without system-level calibration | none-yet | none | hardware | no | Explicitly deferred/killed by the application shortlist. |
| APP-LOCAL-CLOUD-ROUTING | Local-vs-cloud routing product | application idea | killed | none | no routing product while cloud side is unmeasured | none-yet | none | hardware | no | Killed product form; scenario analysis remains C5-2.9. |

## Attribution Limits

The rows whose historical wording most invited over-attribution are:

- `C5-1.1`: active-parameter energy scaling. The C-014 amendment caps
  4-6-model designs at descriptive L2 pairwise contrasts unless the model set
  grows enough for a predeclared one-covariate fit, and forbids fitting
  active+total+KV covariates on 4-6 model points. The claims ladder also
  prevents L1 active-parameter-scaling language; the capability map records
  the current two-model observation as a non-claim.
- `C5-1.8`: runtime energy attribution. The bank already says comparisons
  where formats force different artifacts are stack-vs-stack comparisons.
  The registry therefore forbids wording that energy "belongs to the runtime"
  unless the artifact/runtime identity problem is actually controlled.

This subsection is hygiene for claims indexing. It does not re-adjudicate the
ratified C-014/C-015 bank decisions.
# Prefill-contrast feasibility desk check — synthesis (2026-08-07)

Sol scout (read-only, high, gpt-5.6-sol) over historical diagnostics;
prompt + full response in this directory. ALL NUMBERS NON-CLAIM /
DIAGNOSTIC.

**Verdict: MARGINAL at the historical 128-token workload.** Best-evidence
matched ABBA diagnostic (decode-contrast window's off-manifest prefill
field, 20v20 members, identical prompt hash): 7B−1.5B prefill delta
5.809930 J point vs the ~5 J practical bar (D-078 cl.11 / D-083 wording
control — two separately enforced gates, not one summed threshold);
composed contrast half-width ~1.81 J puts the interval lower edge ~4.0 J,
BELOW the bar. Independent cross-window subtraction corroborates
(5.903 J).

**Length is the lever:** 1.5B prefill scales ~proportionally with prompt
length (128→4096 tokens predicts within ~3.3%); a prospectively frozen
256-token prompt projects ~11.6 J (~2.3× bar). NO long-prompt 7B corpus
exists — the projection is an extrapolation and workload resizing is a
preregistration decision (estimand change).

**Recommended default (scout + magistrate CONCUR):** claim prefill
FLOORS; keep the model contrast decode-only; state the 128-token
marginality as a limitation. The 256-token contrast is Ed's ruling
(needs_ruling row): +~110 core minutes, likely splits into its own
window.

**Consumed by:** the MVP paper draft §7 "Prospective workload sizing"
(qualitative, no diagnostic joules quoted per the draft's
no-demo-values discipline) and the pending fork/window planning.
Scout flags F1 (D-083 wording preserved), F2 (no long-prompt 7B
evidence), F3 (CLAIMS_STATUS staleness vs D-116 — check before window
freeze) all noted.

exec
/bin/zsh -lc "sed -n '1,260p' docs/strategy/2026-08-06-impressiveness-roadmap.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The strongest feasibility-weighted path is a clean C/D metrology campaign, external wall validation, and an evaluation-ready artifact before adding one hypothesis-driven expansion.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "head_end": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "upstream_end": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The paper's claim-bearing experimental spine is not yet complete",
        "detail": "D-110 still withholds the floor and contrast artifacts pending issuance/remint, while D-113 requires fresh Window C collection, prospectively split into D if needed."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "D-041 is not the mechanism-level fence",
        "detail": "D-041 governs external-benchmark import/export and limits the export shim to an energy layer; AXI mechanism studies are governed primarily by D-070, D-075, their analysis plans, and runtime feasibility verdicts."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Venue and calendar ambition remain unbound",
        "detail": "The report deadline, colloquium, 3080 Ti window, and venue-specific evidence-by dates remain TBD, preventing rational allocation of measurement nights."
      },
      {
        "id": "F4",
        "severity": "nit",
        "title": "The requested methods draft is not on main",
        "detail": "docs/paper/draft-v1.md exists on impl/paper-draft-v1 but is absent from main; the branch version was inspected for this review."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse --abbrev-ref HEAD && git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "665fd5821f74e579071fba9ddd9717b77ded6a01",
          "main",
          "origin/main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "665fd5821f74e579071fba9ddd9717b77ded6a01\\nmain\\norigin/main"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "test ! -e docs/paper/draft-v1.md && git cat-file -e impl/paper-draft-v1:docs/paper/draft-v1.md && printf 'draft_main=absent\\ndraft_branch=present\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "draft_main=absent",
          "draft_branch=present"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "draft_main=absent\\ndraft_branch=present"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The prompt identifies docs/paper/draft-v1.md as current, but it is present only on the impl/paper-draft-v1 branch.",
      "needs": "Lead should integrate or otherwise disposition the paper-draft branch."
    },
    {
      "id": "FL2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No test suite was run because this was a read-only strategic synthesis with no repository modifications.",
      "needs": ""
    }
  ]
}
```

## Findings

### F1 — Finish the claim-bearing metrology spine before expanding

The instrument and its evidence machinery are unusually mature, but the paper still lacks a complete claim-bearing characterization result. The 1.5B/7B contrast passed collection gates and is a compelling preliminary demonstration, yet D-110 prevents formal use until the issuance/remint chain completes. D-113 then requires fresh Window C collection—split into D if necessary—without importing any retired Window B member. See [D-113](/Users/edr/code/JouleWise/docs/decision_log.md:7240) and the [current paper outline](/Users/edr/code/JouleWise/docs/run_reports/2026-07-30-paper-outline-v1.md:1).

That is the critical path. A broad paper with incomplete C1–C6 evidence will look less serious than a narrower paper that cleanly demonstrates linearity, null response, empirical floor behavior, additivity, drift/settling, and between-session stability.

D-113’s rigor-first posture forbids:

- Salvaging failed A/B data into replacement claim cells.
- Excluding an inconvenient member after seeing results.
- Compressing an oversized campaign into one night.
- Weakening calibration, whole-window, clock, or custody gates for schedule reasons.
- Adding process or repetitions without a named validity threat or material claim benefit.

It explicitly permits—and often prefers—smaller independent windows, narrower claims, and cutting an expansion.

### F2 — Exact D-041 ruling and the real mechanism fence

D-041 is titled “Benchmark interop — frozen-subset imports + marker-shim energy layer.” It fences:

- External benchmark imports to hash-frozen subsets with identity, licensing, and contamination records.
- Export to a marker-emitting shim where the external harness owns prompts, generation semantics, and accuracy; JouleWise owns capture, bundle assembly, marker validation, and energy reduction.
- Joined reporting to observed energy beside the external metric artifact—never JouleWise accuracy, pass@k-per-joule, leaderboard standing, or intelligence-per-joule.
- Implementation to after 2M and P2-010a, unless D-034 is explicitly reopened.
- Interop expansion to be cut before core Mac characterization under schedule pressure.

Thus, “unfencing D-041” would require completing 2M and P2-010a—or an explicit decision reopening D-034/D-041 sequencing—then passing P2-022’s marker feasibility spike and writing an analysis-plan row before any L2 claim. It still would not authorize mechanism attribution.

The KDA/speculative-decode/MTP/MoE program is instead governed by D-070/D-075 and the AXI contracts:

- Post-core/floor sequencing.
- L2 ceiling for named studies unless Q4’s independent L3 machinery applies.
- Direct observability rather than inference from configuration.
- Output/quality-equivalence controls.
- Named forbidden generalizations.

The current feasibility facts matter:

- External-draft speculative generation exists, but pinned `mlx-lm` lacks actual proposal counts and decode-step emission boundaries.
- Native MTP is unsupported: the pinned runtime does not execute the heads.
- KDA/hybrid comparisons currently involve cross-model confounding and unverified long-context execution.
- MoE mechanism language requires auditable routing evidence; otherwise the claim must remain a named-model energy comparison, not routing attribution.
- No tracked repository document uses “KDA” as a governed project axis; it appears in the nonbinding mechanism-literature sweep, not D-041.

### Ranked roadmap

Planning estimates below assume the current 2–4-hour claim-window protocol, at least 20% failure margin, and physical Ed preparation through §5A.

| Rank | Expansion | Why it impresses reviewers | Estimated effort and Ed-present sessions | Dependencies and principal risk | Decision required |
|---:|---|---|---|---|---|
| **1** | **Complete C1–C7 cleanly: remint, fresh C/D, and stability** | Converts the strongest idea—the instrument and its refusal behavior—into actual evidence. This is the difference between an elaborate methodology and a metrology paper. | **3–6 weeks after desk gates; 2 mandatory nights plus 1 contingency/short stability session.** | D-079 issued artifact; D-110 remint; reviewed frozen-plan record; fresh §5A; C/D split if scope cannot fit. Risk: another environmental or clock refusal. | Reserve the core nights now and prohibit breadth work from consuming them. |
| **2** | **External wall-meter validation of totals, C8** | Directly addresses the obvious reviewer question: “Does `powermetrics` agree with physical input power?” It materially upgrades absolute-scale credibility. | **4–8 weeks; 1 pilot plus 1 confirmatory session.** The confirmatory run may share a later frozen campaign only after the importer and protocol pass independently. | Professional AC analyzer, safe inline fixture, synchronized export, fixed ranges, load-specific uncertainty, battery charge neutralization, held-out regression. It validates totals only—not phase allocation. | D-092 already decided “yes”; Ed/advisor must now authorize purchase/loan, budget, and an evidence-by date. |
| **3** | **Artifact-evaluation-quality release** | Hash-bound raw-to-figure reproducibility is a genuine differentiator and unusually well aligned with JouleWise’s thesis. Reviewers can verify refusals and re-derive results rather than trust screenshots. | **4–6 weeks; 0 measurement nights.** | Sanitized raw-bundle subset, one-command validation/reduction/figure path, locked environment, quick/full tracks, immutable archive/DOI, clear hardware-free replay. Risk: privacy, dataset size, and Mac-only collection requirements. | Decide whether the target is merely open source or formal ICPE-style artifact evaluation, and which evidence may be public. |
| **4** | **Designed workload-shape matrix with held-out prediction—Q4/L3** | A predictive fixed-plus-marginal model validated on held-out cells is substantially more serious than “we ran more prompts.” It can earn L3 rather than another collection of L1/L2 points. | **6–10 weeks; approximately 2–3 nights.** | P2-006 baseline sizing, AP-1, 4×3 grid, predeclared holdouts, residual/sensitivity analysis, floor audit. Risk: the simple model may fail its holdouts—which must be reported honestly. | Fund the full designed matrix or omit the predictive claim; do not replace it with opportunistic workload breadth. |
| **5** | **Quality-gated BF16/Q8/Q4 quantization ladder** | A clean same-family ladder with error bars and output-divergence reporting can adjudicate the reported q4-vs-q8 anomaly. Strong workshop demonstration; moderate novelty. | **4–8 weeks; 1–2 nights.** Quality screening can run outside quiet windows. | One frozen source revision, reproducible conversions, 256-item quality gate, 32-item energy subset, stack-specific floors. Risk: quality may not be equivalent or quantization may alter cadence beyond existing calibration support. | Choose the model family before conversion; accept a quality/energy trade-off result if equivalence fails. |
| **6** | **Second-unit replication after multi-day same-unit stability** | This is the clearest path beyond single-machine claims and toward L4. It demonstrates that the artifact and calibration method transfer, not merely that one laptop is stable. | **4–8 weeks once access exists; 2 sessions on the second unit, 0–2 Ed-present depending on operator.** | A second comparable Apple unit, frozen stack or explicitly modeled version difference, independent calibration and artifact execution. Risk: OS/hardware drift may make it replication-aware rather than directly pooled. | Secure a second unit/collaborator or explicitly retain the single-unit ceiling. |
| **7** | **One mechanism-level study, conditional on a hard feasibility gate** | **Highest scientific ceiling.** A controlled batch-1 speculative-decode or MTP energy result could be genuinely novel; KDA/context slope or MoE routing is also interesting if attribution is identifiable. | **2–3-week desk feasibility gate; if passed, another 6–12 weeks and roughly 2 nights.** | New/forked runtime instrumentation, direct proposal/acceptance events, output identity/equivalence, mechanism-specific AP and floors. MTP currently cannot execute; KDA is confounded; MoE routing visibility is uncertain. | Pick exactly one mechanism and a kill date. Recommended first choice: external-draft speculative decode, because it offers the cleanest same-target on/off contrast if observability can be added. |
| **8** | **Split inference: synthetic transfer plus one offline split pairing** | Demonstrates the instrument under two boundaries, a transfer interval, and cross-device clocks. A complete per-stage bundle is impressive even without a crossover. | **2–4 months; roughly 3–5 two-device measurement sessions.** Live split adds more and should remain stretch. | Schema v0.2, remaining replay verdicts, two-node telemetry, clock bounds, transfer bench, 3080 Ti window, two links, wall/host boundary or lower-bound wording. Risk is high and the engineering can dominate the paper. | Commit only to synthetic transfer plus offline replay; authorize live split separately after offline results. |
| **9** | **Additional model families, generic workloads, Jetsons** | Useful corroboration, but mostly incremental unless each addition tests a predeclared hypothesis or provides independent replication. More rows do not overcome the single-unit or boundary limitations. | **3–8 weeks and 1–2 nights per coherent axis/device.** | New model lineage, adapter, quality and floor cells; Jetson remains optional and remote pins are provisional. | Add only a model or device that changes the claim—not merely the size of a results table. |

For the wall-meter path, the right class is a calibrated bench AC power analyzer, not an inexpensive consumer plug. A concrete baseline is the Yokogawa WT310E: its manufacturer lists 10 readings/s, USB export, 0.1%-of-reading plus 0.05%-of-range basic accuracy, high crest-factor capability, and a **$2,935 base US price** before calibration/fixture costs. Actual suitability still depends on calculating uncertainty at the Mac’s observed load and using a safe inline fixture. Borrowing an in-calibration unit from an engineering lab is preferable to spending several thousand dollars. [Yokogawa WT310E specifications and current price](https://tmi.yokogawa.com/us/solutions/products/power-analyzers/digital-power-meter-wt300e/).

### Venue ambition

| Tier | What the current/expanded project can support | What should be present |
|---|---|---|
| **CSCSU** | After remint and clean C/D, this should be a strong undergraduate-conference submission. The latest published rules allow technical papers and extensive experimentation, with **5 pages including references**. [CSCSU 2026 guidance](https://cscsu-conference.github.io/) | C1–C6 core, one demonstration, crisp limitations, compact artifact pointer. Wall validation and split are not necessary. |
| **EuroMLSys/HotCarbon workshop** | The natural near-term research target. EuroMLSys’s latest call uses 6 pages excluding references; HotCarbon uses 5 pages excluding references and no appendix. [EuroMLSys](https://euromlsys.eu/), [HotCarbon CFP](https://hotcarbon.org/cfp) | Clean metrology core, model contrast, wall validation if available, and polished artifact. EuroMLSys is the better technical-method fit; HotCarbon needs a stronger sustainability-metrics argument. |
| **ICPE Emerging/WIP** | Appropriate if the core is strong but external validation, replication, or the broader predictive evaluation remains incomplete. The 2026 track used a 6-page format. [ICPE Emerging Research](https://icpe2026.spec.org/tracks-and-submissions/emerging-research-track/) | Validated core, transparent open gaps, early artifact, and a credible expansion plan. |
| **ICPE full research track** | Plausible over months, but not yet supported by the current evidence. ICPE 2027 lists research and artifact tracks but their details and dates remain TBA. The 2026 research track used 10 pages and judged novelty, technical quality, and scientific soundness; 2026’s reported full-paper acceptance rate was 28%. [ICPE 2027](https://icpe2027.spec.org/tracks-and-submissions/research-paper-track/), [2026 research criteria](https://icpe2026.spec.org/tracks-and-submissions/research-paper-track/), [acceptance history](https://icpe.spec.org/past-conferences/) | C1–C8, cross-day stability, artifact-ready release, and at least one deeper contribution: held-out Q4 prediction, second-unit replication, or a successful mechanism study. Split is not required. |

ICPE’s artifact track is especially aligned: it asks for documented, consistent, complete, exercisable artifacts, permanent archival availability, and practical setup/reproduction instructions. [ICPE artifact-evaluation criteria](https://icpe2026.spec.org/tracks-and-submissions/artifact-evaluation-track/).

### Critical path to the strongest defensible version

1. **Now:** finish D-079 issuance and the D-110 remint chain; integrate or disposition the draft branch; set actual calendar and venue evidence-by dates.
2. **In parallel:** borrow/order the wall analyzer and build its importer, synchronization, and held-out validation protocol without assuming it will arrive in time.
3. **First hardware block:** freeze and collect Window C, then D if the complete replacement cannot fit with the required margin. Add a third short day/session only if needed for the stated stability claim.
4. **Immediately after each passing window:** produce the governed artifacts, deterministic figures, claim-index entries, and experimental prose. Do not wait for all expansions before writing.
5. **Artifact block:** publish a sanitized, hash-bound raw-to-figure package with a fast hardware-free reproduction path and archival DOI.
6. **Second hardware block:** run external wall validation.
7. **Choose one expansion:** Q4 held-out prediction for the strongest ICPE case; quantization for the safest workshop enhancement; or mechanism work only if its short feasibility gate passes.
8. **Only then consider split inference.** Start it only if the 3080 Ti window is dated and the transfer/offline-replay path is rehearsed before hardware access.
9. **Freeze the dataset early:** reserve at least six weeks before submission for figures, claims audit, paper compression, artifact dry runs, and advisor review.

The strongest realistic paper is therefore: **C1–C8 metrology + the already-collected 1.5B/7B demonstration + one designed extension + an independently usable artifact.** That is more coherent and defensible than a larger model/device matrix or an unfinished split system.

### F3 — Five decisions Ed/advisor must make

1. **Venue and publication sequence.** Choose CSCSU-only, workshop-first, or ICPE-full ambition, and verify whether a workshop publication may later be extended for ICPE. Build a 10-page master manuscript even if the first submission is shorter.

2. **Physical measurement budget.** Recommended commitment: **5–7 Ed-present sessions**—C, D, one contingency/stability repeat, wall pilot/confirmation, and one extension. An ICPE-full attempt with Q4 and second-unit work likely needs **8–10 total sessions** across operators.

3. **Meter execution.** D-092 has already answered “yes.” The remaining decision is: borrow versus buy, approximately $3,000-class budget, calibration/fixture responsibility, and a cutoff date after which C8 is cleanly removed.

4. **Mechanism ambition.** Do not ask simply “unfence D-041.” Decide whether to retain D-070’s all-five-axis commitment or narrow it to one paper-worthy study. Recommended rule: two-to-three-week feasibility gate for speculative-decode observability; if it fails, return immediately to Q4/quantization.

5. **External hardware priority.** Decide whether scarce coordination goes to a second Apple unit, the 3080 Ti split study, or Jetsons. Recommendation: second-unit replication first, 3080 Ti second, Jetsons last.

### F4 — Draft-state correction

The methods draft was inspected from `impl/paper-draft-v1` at commit `af0b7195`; it is one commit ahead of and one commit behind `main`. It already reflects the right rigor: result placeholders remain pending remint, all characterization rows are pending Window C, and the split section is framed as future demonstration work. It should be integrated deliberately so the paper itself becomes the continuously updated claim-state surface.

## Residual risk

- The mechanism-literature sweep is explicitly desk research, not governed project evidence. Any “first measured” novelty claim needs a fresh literature search immediately before submission.
- Venue formats and deadlines cited above are current published 2026 rules or incomplete 2027 pages; 2027 calls may change.
- Measurement-night estimates are planning ranges, not validated campaign runtimes.
- Wall validation cannot establish phase attribution, and one external meter does not create cross-device generality.
- Even an excellent single-Mac study remains stack-specific under the claims ladder unless second-unit or cross-lab replication lands.
exec
/bin/zsh -lc "sed -n '1,170p' docs/research_question_registry.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Research Question Registry

Purpose: this is the canonical live index for JouleWise research questions,
capability claims, application ideas, and methodology artifacts. It normalizes
aliases, status, claim ceilings, owners, gates, and pre-hardware readiness so
claims and campaign plans can point to one row. Promotion rules are unchanged
from `docs/research_question_bank.md`: promotion still requires a named RQ slot
in `PROJECT_STATUS.md`, a data plan that does not displace queue ranks above
it, and scope fit.

Maintenance rule: registry rows are LIVE state. The research question bank
remains the historical and deliberative record, including council wording,
kills, quarantines, and amendments. Single-writer split: update this registry
for current indexing and cross-references; update the bank only when recording
new deliberation history.

Column legend:

- `canonical_id`: stable row key for the live index.
- `aliases`: other IDs, names, or capability-map labels for the same question.
- `question_type`: one of `research question`, `capability claim`,
  `application idea`, or `methodology artifact`.
- `status`: `promoted`, `banked`, `candidate`, `killed`, `answered-L1`, or
  the review-specific `candidate (C-023)`.
- `claim_ceiling`: highest claim level currently allowed by the bank, review,
  or capability map, before future evidence upgrades.
- `forbidden_upgrade`: short reminder of language the row cannot support.
- `AP owner`: analysis-plan owner if already named; otherwise `none-yet`.
- `campaign owner`: queue row, phase, or campaign owner if already named.
- `gate_class`: dominant gate class: `hardware`, `software`, `floor`,
  `substrate`, or `coordination`.
- `pre_hardware_preparable`: `fully`, `analysis-plan-only`, or `no`.
- `one-line note`: indexing note, not a re-adjudication.

## Registry Table

| canonical_id | aliases | question_type | status | claim_ceiling | forbidden_upgrade | AP owner | campaign owner | gate_class | pre_hardware_preparable | one-line note |
|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | Split reduces energy | research question | promoted | L2 boundary-labeled; stronger only with calibration | no uncalibrated cross-boundary total-energy winner | none-yet | Phase 3 split; P1-004; P1-006 | hardware | fully | Central split question; total energy must be decomposed and boundary-labeled. |
| Q2 | Link bandwidth sensitivity | research question | promoted | L2 | no nominal-link crossover without measured links | none-yet | Phase 3 split; P1-004 | hardware | fully | Clean interconnect sensitivity question; link throughput and transfer energy must be measured. |
| Q3 | Split energy-latency Pareto | research question | promoted | L2 | no Pareto claim without frozen set and latency metric | none-yet | Phase 3 split | hardware | fully | Requires a fixed comparison set and latency metric per figure. |
| Q4 | Fixed-vs-marginal energy model; C5-2.14 cache-policy coefficient rider | research question | promoted | L3 | no holdout-prediction claim without AP-1 floor and residual checks | AP-1 | P2-019 q4_l3_shape_grid_v1 | floor | analysis-plan-only | Strongest predictive science row; includes compositional split-energy prediction only when transfer terms exist. C5-2.14 is a candidate rider capped at L2, earliest PF, with no coefficient-direction claim below P2-015 floors ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| Q5 | Ranking stability | research question | promoted | L2 | no uncalibrated cross-device winner; no ranking where gap below MDE | AP-3 | 2M; Window B grid | floor | analysis-plan-only | Promoted within-machine ranking question; workload-axis analogue C5-W.3 remains a separate candidate row. |
| Q6 | Boundary sensitivity; C5-2.10 boundary-directional bias quantification | research question | promoted | L2; L4 only with replication | no wall/rail conclusion flip claim without paired boundary plan | none-yet | P1-003 wall meter; F11 | hardware | fully | Registry indexes C5-2.10 as the C5 elaboration of promoted Q6. |
| RQ-METHOD-FLOOR | Detection floor; noise floor; short-difference resolvability; phase/item identifiability flags; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | banked | L1 methodology | no below-floor effect language except `not resolvable`; no module-energy fraction or regression-slope attribution | none-yet | P2-015 | floor | analysis-plan-only | Methodology centerpiece and prerequisite for most comparative claims; the candidate module-attribution nonclaim attaches here at earliest NS instead of becoming a row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.11 | Dark silicon; rail utilization; ANE-dark finding | research question | candidate | L2 structural | no true silicon-energy fraction from modeled rails | none-yet | P2-009 rich telemetry; C5-1.8 runtime grid | software | analysis-plan-only | Measures modeled-rail utilization structure, not physical absolute rail truth. |
| C5-1.3 | CPU:GPU phase division; rail/DVFS phase signatures; prefill/decode power asymmetry | research question | candidate | L2 structural | no short-phase joules when windows are under-resolved | none-yet | 2M with P2-009 | floor | analysis-plan-only | Merges the banked CPU:GPU phase question with C5-1.3 telemetry framing. |
| RQ-KV-GROWTH | KV-growth decode drift; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | banked | L1/L2 chunked | no per-token joule claims; no attention-vs-FFN fraction from context slopes | none-yet | none | floor | analysis-plan-only | Candidate riders, earliest PF: bounded-window KV marginal slope and named-artifact attention/context slope; both retain chunked-window/floor discipline and stay attached rather than becoming independent rows ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.5 | Cooldown recovery as thermal characterization; cooldown-recovery curves | research question | candidate | L1/L2 | no claim that power recovery proves thermal-state equality | none-yet | none | floor | analysis-plan-only | Turns cooldown tails and cap-hit rates into reportable methodology evidence. |
| C5-1.10 | Failure frontier | research question | candidate | L1/L2 descriptive | no silent discard of failures; no population claim from one memory class | none-yet | none | software | analysis-plan-only | Structured `unsupported`, fit, swap, throttle, and cap-hit outcomes become data. |
| C5-1.7 | Cold-start / keep-warm energy; reload-vs-resident scheduling | research question | banked | L2 after harness extension | no breakeven without load-window and resident-idle sampling | none-yet | none | software | analysis-plan-only | Review and bank both identify reload-vs-resident as the same question. |
| C5-1.9 | Energy-per-correct-answer vs difficulty; MoE-vs-dense controlled ladder | research question | banked | L2 after envelope and denominator guards | no intelligence-per-joule; no `difficulty causes energy` | AP-5 | P2-010a plus P2-010b plus later scored campaign | substrate | analysis-plan-only | Correctness remains quarantined annotation under the C-004/C-014 rules. |
| C5-2.5 | Speculative-decoding energy; C5-2.5b proposal-work rider; C5-2.5c break-even rider | research question | banked | L2 | no efficiency claim without output equivalence and accepted-token accounting | none-yet | none | software | analysis-plan-only | C5-2.5c is the primary PF Q4 rider, C5-2.5b its PF secondary, and C5-2.5d the mandatory PF contamination control; C5-2.5a remains a deferred NS bank rider. `C-023-OUTPUT-IDENTITY` binds all efficiency contrasts ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-POWER-MODE | Power-mode Pareto | research question | banked | L2 possible | no OS-mode conclusion until power mode is a first-class config field | none-yet | none | software | analysis-plan-only | Waits on config/environment capture for OS power modes. |
| RQ-INTELLIGENCE-PER-JOULE | General joules-per-solved-task; intelligence-per-joule | research question | killed | none | no general intelligence-per-joule ratio | none-yet | none | substrate | no | Killed/quarantined by C-003/C-004; controlled ladder is the surviving minimal form. |
| RQ-AUDITABLE-EVIDENCE | Can JouleWise produce auditable local-LLM energy evidence? | capability claim | answered-L1 | L0/L1 | no physical calibration claim from strict validation alone | none-yet | existing Mac/MLX/powermetrics bundles | software | no | Artifact contribution, not a research question. |
| RQ-QWEN25-SMOKE | Qwen2.5-1.5B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from smoke result | none-yet | 2026-07-06 2I | software | no | Legit instrument observation for one named stack/workload. |
| RQ-QWEN35-SMOKE | Qwen3.5-122B-A10B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from n=3 | none-yet | 2026-07-07 flagship addendum | software | no | Legit instrument observation for one named stack/workload. |
| RQ-TWO-MODEL-ACTIVE-NONCLAIM | Did the two observed models demonstrate active-parameter scaling? | capability claim | answered-L1 | L1 hypothesis only | no active-parameter scaling claim | none-yet | 122B addendum; capability map | floor | no | Negative guard: two points are consistent with a hypothesis but do not support scaling. |
| RQ-SHORT-PREFILL-RESOLVABILITY | Are short prefill phase joules resolvable?; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | answered-L1 | L1 `not resolvable` | no standalone short-prefill joule result; no relabeling request phases as module phases | none-yet | Phase 4 observation | floor | no | Existing cadence precedent owns the candidate module-attribution guard, earliest NS; no separate methodology row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-MLX-KV-REPLAY | Same-machine MLX KV replay token identity and size prediction; C5-2.13 | capability claim | answered-L1 | L1 feasibility | no cross-machine portability claim | none-yet | Stage 3.0.1 | software | no | The L1 feasibility result remains answered; candidate C5-2.13, earliest PF and capped at L2, attaches the same-machine energy-crossover rider without cross-stack generalization ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-MAC-BASELINES | Per-profile Mac baselines | capability claim | candidate | L1 per condition | no novelty or comparison claim without AP/floor | none-yet | 2M | floor | analysis-plan-only | Necessary baseline corpus, not a headline by itself. |
| RQ-SHAPE-ENERGY | Workload shape changes request energy | research question | candidate | L2 | no causal token-shape claim beyond AP-2 contrasts | AP-2 | 2M | floor | analysis-plan-only | Distinct from Q4 because it describes shape contrasts rather than holdout prediction. |
| C5-1.1 | Active-parameter energy scaling | research question | candidate | L2 pairwise only unless larger predeclared model set | no active+total+KV regression on 4-6 models | none-yet | P2-024 shortlist | floor | analysis-plan-only | C-014 caps the tempting wording; registry hygiene, not re-adjudication. |
| C5-1.2 | Context-length energy scaling; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | candidate | L2/L3 if modeled | no short-prompt phase point claims; no wall implication from SoC rails | none-yet | none | floor | analysis-plan-only | Natural local-inference question with chunked phase limits; the two candidate PF riders remain capped at L2 and forbid module attribution from context-associated slopes ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.4 | DVFS residency as throttling early-warning | research question | candidate | L2 if prediction rule fixed | no prediction claim without horizon and rule | none-yet | none | software | analysis-plan-only | Convert characterization to a predeclared warning rule before claiming prediction. |
| C5-1.6 | Sampling-strategy energy overhead | research question | candidate | L2 if above floor | no telemetry-perturbation claim from this row | none-yet | P2-024 shortlist | floor | analysis-plan-only | Bank row is greedy vs temperature/top-p/beam overhead, not sampler instrumentation cost. |
| C5-1.8 | Runtime energy attribution; same-silicon kernel-layer provenance rider | research question | candidate | L2 stack-vs-stack | no `belongs to runtime` or `belongs to kernel layer` language when artifacts/formats differ; no runtime-agnostic kernel claim | none-yet | P2-024 shortlist | floor | analysis-plan-only | Candidate NV provenance rider stays inside the stack-conditioned comparison; it does not mint C5-1.13 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.12 | Quantization benefit decomposition, Mac leg | research question | candidate | L2 | no quantization efficiency claim without output divergence reporting | none-yet | P2-024 shortlist | floor | analysis-plan-only | Splits benefit into lower watts vs shorter time on one stack/family. |
| C5-W.1 | Category beyond token counts; Token-Shape Sufficiency Null | research question | candidate | L2 | no category effect below floor or without shape control | AP-4 | jw_mixed_v1 after P2-010a | substrate | analysis-plan-only | Strong null-or-effect design for workload-category residuals. |
| C5-W.2 | Thinking-token inflation | research question | candidate | L2 | no cognition claim; attribute only to emitted-token/stop distributions | none-yet | jw_mixed_v1 natural-EOS pilot | substrate | analysis-plan-only | Operational-cost view for reasoning models under natural EOS. |
| C5-W.3 | Category energy-ranking stability; workload-axis Q5 analogue | research question | candidate | L2 | no category ranking claim where rank gap is below MDE or without workload-expansion gate | none-yet | jw_mixed_v1 workload expansion | substrate | analysis-plan-only | Workload-axis analogue of promoted Q5, not the same ratified question; asks whether code/long-context/reasoning categories flip model/quant ordering. |
| C5-I.3 | C5-W.4; FLORES tokenizer fertility tax | research question | candidate | L2 | no tokenizer efficiency ranking without semantic and token-matched legs | none-yet | FLORES after HumanEval smoke | substrate | fully | C5-I.3 and C5-W.4 are the same FLORES fertility question. |
| C5-I.1 | External benchmark energy signatures | research question | candidate | L2 | no benchmark capability or accuracy claim | none-yet | import/export contracts | substrate | fully | Needs matched shape/output policy before family-level energy signatures. |
| C5-I.2 | Published-difficulty strata vs energy | research question | candidate | L1 association; L2 only if preplanned repeated bundles | no `difficulty causes energy` | none-yet | import/export contracts | substrate | fully | Weak/secondary because source difficulty labels are heterogeneous. |
| C5-I.4 | Harness overhead floor | methodology artifact | candidate | L1/L2 | no item energy claim when harness overhead dominates unnoticed | none-yet | P2-022 shim | substrate | fully | Methodology question for marked external harnesses. |
| C5-I.5 | Prompt-template energy sensitivity | research question | candidate | L2 | no prompt-quality or capability claim | none-yet | import/export contracts | substrate | fully | Same external item, canonical vs JouleWise-rendered prompt format. |
| RQ-CONTENT-SENTINEL | Synthetic prompt content sentinel; fixed-shape content sensitivity | research question | candidate | L2 | no content-effect claim unless realized shape/stop policy stays matched and effect clears floor; no broad content-neutrality claim beyond the five tested AP-6 conditions | AP-6 | P2-020 content sentinel | substrate | analysis-plan-only | Tests whether synthetic prompt content matters at fixed shape under the AP-6 ids-native no-BOS sentinel design. |
| RQ-ENERGY-VARIANCE | Sampling-induced energy variance; energy-at-risk per prompt; lucky-short-reasoning variance | research question | candidate | L2 within boundary | no intelligence-per-joule or correctness-causal claim (C-004 quarantine); variance claims need repeated-bundle n sized for variance estimation and floor-gated residuals; per-bundle sampler seeds must be recorded | none-yet | none (post-floor; reasoning model on current Mac feasible) | floor | analysis-plan-only | Ed-added 2026-07-09 row: distribution (not just mean) of request energy for a fixed hard prompt under sampling; decomposable into reasoning-length vs residual variance via recorded output token IDs + deterministic replay of sampled paths (P2-025 capture + 3.0.1 replay make paths replayable). |
| RQ-SESSION-SHAPE | Session-shape energy | research question | candidate | L2/L3 depending holdout | no app-session prediction without holdout validation | none-yet | suite profiles after P2-010a | substrate | analysis-plan-only | Tests whether Q4 coefficients compose in realistic session ecology. |
| RQ-ORDER-POSITION | Order-position effects | methodology artifact | candidate | L2 | no category/thermal inference without executable order policy | none-yet | suite profiles after ordering executability | substrate | analysis-plan-only | Drift/order probe; not a headline result. |
| RQ-CACHE-PREFIX | Cache/prefix economics; C5-2.13 | research question | candidate | L2 | no bundled cache-state conclusion without exact cache policy; no crossover generalization beyond the measured prompt-length ladder | none-yet | none | software | analysis-plan-only | Covers prefix reuse, resident state, and prompt-cache warmth; candidate C5-2.13 attaches a same-machine/same-stack energy crossover at earliest PF ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-AXI-HYBRID-PAIR | Named hybrid (SSM/attention)-vs-pure-transformer pair | research question | candidate | L2 pair-specific characterization | no architecture-class efficiency generalization, causal SSM-mechanism attribution, or tokenizer-blind ranking from one named pair | none-yet | post-floors named-pair campaign | floor | analysis-plan-only | Earliest PF; floor-gated and bindingly worded as “this named pair”; controlled-pair availability remains NEEDS-WEB ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-EXTERNAL-MARKED-RUNNER | External marked-runner energy layer | capability claim | candidate | L1/L2 with AP row | no accuracy, leaderboard, pass@k, or capability interpretation | none-yet | P2-022 | substrate | fully | Export-layer feasibility becomes research only when overhead/energy comparisons are specified. |
| RQ-HUMANEVAL-IMPORT-SMOKE | HumanEval import smoke | capability claim | candidate | L0/L1 | no coding-capability, pass@k, or accuracy claim | none-yet | P2-023 | substrate | no | Plumbing smoke for frozen external subset provenance. |
| C5-2.1 | Quantization decomposition, cross-stack | research question | candidate | L2 | no cross-boundary quant winner without calibration | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Extends C5-1.12 to CUDA/GGUF legs. |
| C5-2.2 | Batch size and prefill/decode energy split | research question | candidate | L2 | no serving conclusion without latency-bound policy | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Strong systems question for serving-style hardware and batching backend. |
| C5-2.3 | Predicted-vs-measured KV economics | research question | candidate | L2 | no KV economics claim without measured payload/link/deserialization terms | none-yet | P1-004 plus P1-006 | hardware | fully | One of the strongest Phase 3 questions; useful even if live split fails. |
| C5-2.4 | KV-cache quantization end-to-end; C5-2.11 on-device MLX leg | research question | candidate | L2 | no byte-saving equals energy-saving claim | none-yet | none | software | analysis-plan-only | Transfer leg still depends on cache portability; candidate C5-2.11 is the PF on-device MLX-scoped leg and also binds output-equivalence evidence ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.11 | On-device quantized-KV energy | research question | candidate | L2, per-boundary, MLX-scoped | no byte-saving-equals-energy-saving claim; no cross-runtime generalization from MLX alone; no quality-neutrality claim without C-023-style output-equivalence evidence | none-yet | post-floors Mac cache-policy campaign | floor | analysis-plan-only | Earliest PF; indexed under C5-2.4/C5-1.12/C-023-QUALITY-EQUIV-QUANT and runnable without the transfer leg ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.6 | Request coalescing under latency bound | research question | candidate | L2 | no scheduler optimum without arrival trace and latency policy | none-yet | none | hardware | analysis-plan-only | Useful but drifts toward scheduler research. |
| C5-2.7 | Device perf/W rankings with runtime held constant; kernel-provenance rider | research question | candidate | L2 within boundary; L4 with second unit/calibration | no generic hardware or cross-vendor kernel-API ranking from heterogeneous boundaries | none-yet | P1-006; 3080 Ti borrow window | hardware | fully | Candidate NV rider records attention-kernel/BLAS/graph provenance and remains per-boundary at L2; NEEDS-WEB feasibility stays open ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.8 | Placement-policy optimality from Q4 coefficients | research question | candidate | L2/L3 | no optimal-placement claim without measured split validation cells | none-yet | Phase 3 full set | hardware | fully | Uses Q4 coefficients plus measured transfer costs to choose placement. |
| C5-2.9 | Local-vs-datacenter crossover economics | research question | candidate | scenario result only | no measured-equivalent cloud comparison | none-yet | P1-003 plus P1-004 | hardware | analysis-plan-only | Surviving scenario form of the carbon-label kill. |
| C5-3.1 | Machine-to-machine variance; generalizability floor | research question | candidate | L4 enabler | no population claim from one unit | none-yet | second M-series unit | hardware | fully | Cheapest route from stack-specific to replication-aware claims. |
| C5-3.2 | Battery-path energy and modeled-rail validation | research question | candidate | L2/L4 bridge | no full-system claim from modeled rails alone | none-yet | USB-C PD analyzer | hardware | fully | Complements AC wall meter with a second physical boundary. |
| C5-3.3 | Cross-ISA NPU/SoC comparison; backend-provenance rider | research question | candidate | L4 only after replication | no broad cross-ISA claim before platform-specific adapter study; no NVIDIA-vs-AMD efficiency claim from single units or heterogeneous boundaries | none-yet | new platform adapters | hardware | analysis-plan-only | Candidate PC provenance rider is capped at L1 and records backend identity now; it creates no AMD science commitment ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-3.4 | Phone-class edge inference | capability claim | candidate | L0/L1 first | no promised phone science before telemetry feasibility | none-yet | phone feasibility | hardware | no | Feasibility verdict may be the result. |
| C5-3.5 | Cross-lab replication | methodology artifact | candidate | L4 enabler | no public benchmark credibility claim without replication | none-yet | external lab coordination | coordination | fully | Coordination-gated credibility layer. |
| C-023-TELEMETRY-PERTURBATION | Telemetry perturbation cost | methodology artifact | candidate (C-023) | L1/L2 floor component | no near-floor claim without telemetry-on/off ABBA check | none-yet | P2-015 component | floor | analysis-plan-only | New coverage-gap row; distinct from C5-1.6 sampling-strategy overhead. |
| C-023-VERSION-DRIFT | OS/runtime version-drift forensics; OS/driver/runtime update forensics | research question | candidate (C-023) | L1/L2 stack-conditioned | no version regression claim without before/after pinned bundles | none-yet | none | software | analysis-plan-only | Turns version churn into a named science/application row. |
| C-023-MARKER-JITTER | Marker/window jitter sensitivity; sampler-phase jitter sensitivity | methodology artifact | candidate (C-023) | L1 methodology; blocker for phase/item claims | no phase/item joule claim without jitter/sampler-phase sensitivity bound | none-yet | P2-015 or claim gate | floor | analysis-plan-only | Quantifies reducer sensitivity to timestamp jitter and sampler phase offset. |
| C-023-OUTPUT-IDENTITY | Output-token identity effects; binding gate for C5-2.5a/b/c/d | methodology artifact | candidate (C-023) | L1/L2 depending comparison | no quant/runtime/spec-decoding efficiency claim without equivalence or divergence report | none-yet | none | software | analysis-plan-only | Fixed output-token count is not fixed decoded work; binding for the PF/NS speculative-decoding riders admitted by D-075 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C-023-IDLE-STATIONARITY | Idle-baseline stationarity | methodology artifact | candidate (C-023) | L1 methodology | no idle-subtracted conclusion without idle model-choice sensitivity | none-yet | P2-015 component | floor | analysis-plan-only | D-067 CLOSED the headline-basis question: gross energy within the named boundary is primary. This row stays alive only to test how idle-model choice affects conclusions in the labeled within-device SECONDARY view. |
| C-023-QUALITY-EQUIV-QUANT | Quality-equivalent quantization comparisons; C5-2.11 gate | research question | candidate (C-023) | L2 after equivalence rule | no quantization efficiency or quality-neutrality claim without AP-level equivalence rule | none-yet | none | software | analysis-plan-only | C5-2.11's candidate PF on-device KV leg binds this gate; footprint savings alone do not establish energy or quality neutrality ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C-023-COEFF-TRANSPORT | Coefficient transport synthetic-to-realistic; energy model portability across workload mixtures | research question | candidate (C-023) | L2/L3 depending holdout | no realistic-session prediction from synthetic grid without transport validation | none-yet | suite traces after Q4 | substrate | analysis-plan-only | Explicitly tests Q4 coefficient transport from synthetic grids to realistic app traces. |
| APP-PROMPT-PROFILER | Prompt/template energy profiler | application idea | candidate | internal L1/L2 only | no prompt-quality claim | none-yet | none | software | analysis-plan-only | Product-facing use of prompt/template energy sensitivity. |
| APP-BUNDLE-POWER-BUG | Attach-a-bundle power-bug repro | application idea | candidate | L0/L1 support workflow | no general bug diagnosis without reproduced bundle | none-yet | none | software | analysis-plan-only | Uses bundle completeness as a maintainer repro artifact. |
| APP-CI-ENERGY-GATES | CI energy-regression gates | application idea | candidate | internal L1/L2 after floors | no CI failure threshold below detection floor | none-yet | P2-015 prerequisite | floor | analysis-plan-only | Needs floors, env snapshots, and baseline-refresh policy. |
| APP-VENDOR-PRESS-AUDIT | Vendor/press claim audit | application idea | candidate | boundary-named L1/L2 | no absolute device-energy verdict without calibration | none-yet | none | hardware | analysis-plan-only | Can audit specific boundary/workload claims, not universal efficiency. |
| APP-MODEL-CARDS | Practitioner energy model cards / leaderboard | application idea | candidate | internal only until L4 replication | no public leaderboard before cross-lab replication | none-yet | C5-3.5 prerequisite | coordination | analysis-plan-only | Internal table can exist; public version is killed until replication. |
| APP-TEACHING-INSTRUMENT | Teaching instrument | application idea | candidate | pedagogical L0/L1 | no research generalization from teaching bundles | none-yet | none | software | analysis-plan-only | Uses bundles for methodology labs on boundaries, floors, and uncertainty. |
| APP-STANDARDS-CONTRIBUTION | Bundle contract as standards contribution | application idea | candidate | methodology artifact proposal | no claim to be the standard | none-yet | none | coordination | analysis-plan-only | Exports the artifact format and validation discipline. |
| APP-CARBON-LABELS | Carbon labels | application idea | killed | none | no carbon label without wall meter and grid assumptions | none-yet | none | hardware | no | Killed as product label; C5-2.9 is the surviving scenario question. |
| APP-BATTERY-RUNTIME | Battery-runtime estimates without calibration | application idea | killed | none | no battery-runtime estimate without system-level calibration | none-yet | none | hardware | no | Explicitly deferred/killed by the application shortlist. |
| APP-LOCAL-CLOUD-ROUTING | Local-vs-cloud routing product | application idea | killed | none | no routing product while cloud side is unmeasured | none-yet | none | hardware | no | Killed product form; scenario analysis remains C5-2.9. |

## Attribution Limits

The rows whose historical wording most invited over-attribution are:

- `C5-1.1`: active-parameter energy scaling. The C-014 amendment caps
  4-6-model designs at descriptive L2 pairwise contrasts unless the model set
  grows enough for a predeclared one-covariate fit, and forbids fitting
  active+total+KV covariates on 4-6 model points. The claims ladder also
  prevents L1 active-parameter-scaling language; the capability map records
  the current two-model observation as a non-claim.
- `C5-1.8`: runtime energy attribution. The bank already says comparisons
  where formats force different artifacts are stack-vs-stack comparisons.
  The registry therefore forbids wording that energy "belongs to the runtime"
  unless the artifact/runtime identity problem is actually controlled.

This subsection is hygiene for claims indexing. It does not re-adjudicate the
ratified C-014/C-015 bank decisions.

codex
The governing plan is unusually concrete: the three D-117 windows already cost about 9.2 quiet hours total (3.14 h, 3.24 h, 2.80 h), produce four floor cells plus the decode contrast, and require no extra runtime for the prefill riders. I’m now checking the question bank for which ICPE delta adds real scientific depth without diluting that spine.
exec
/bin/zsh -lc "sed -n '1,410p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Research Question Bank

Candidate research questions the instrument can answer, beyond the named
set in `PROJECT_STATUS.md`. Populated from council sessions C-003/C-004
(2026-07-07; see `docs/council_log.md` for positions and votes). Promotion
out of the bank requires: a named RQ slot in `PROJECT_STATUS.md`, a data
plan that does not displace queue ranks above it, and (post P1-001) scope
fit. Killed ideas stay recorded with their cause of death.

Canonical live index: `docs/research_question_registry.md`. The registry is
the current index for aliases, status, claim ceilings, owners, and gates; this
bank remains the historical and deliberative record.

## Promoted 2026-07-07 (now Q4-Q6 in PROJECT_STATUS)

- **Q4 Fixed-vs-marginal energy model** — fit
  `E = fixed + prefill(prompt_tokens) + decode(output_tokens)` per
  target/model/quantization; predicts which workloads flatter which
  devices and enables compositional split-energy prediction (predict
  split-run energy from monolithic coefficients + transfer measurements,
  validate on a subset) — the method that makes Q1 answerable at scale.
  Subsumes the prefill-scaling-exponent question. L3 wording requires AP-1
  in `docs/contracts/analysis_plans.md` (2026-07-08, C-014).
- **Q5 Ranking stability** — do within-machine rankings survive workload
  changes (prompt/output/quantization regimes), or where do they flip?
  Cross-device extension is hardware-gated. Uses the 2M matrix directly
  as a substrate; rank wording follows AP-3 in
  `docs/contracts/analysis_plans.md` (2026-07-08, C-014).
- **Q6 Boundary sensitivity** — do conclusions change when measured at
  platform rails vs AC wall power? (Gated on the wall meter, P1-003/R-007;
  reframes calibration as a research result.)

## Methodology centerpiece (deliberately NOT a numbered RQ — C-003 vote)

- **Detection floor / noise floor**: the smallest idle-subtracted energy
  difference each target/telemetry backend can honestly resolve. Observed
  motivation: idle baseline stddev (5.4 W) exceeded its mean (3.5 W) in
  the first real capture. Pairs with the reducer feature all council
  members converged on: **phase/item identifiability flags** (windows with
  fewer than N samples report a flag, not a bare joule value).

## Banked (viable, not yet promoted)

- **Dark silicon / rail utilization**: what fraction of a SoC's rails does
  a runtime energize? (Measured: ANE at 0.0 W through 512 tokens of MLX
  decode — the most quotable standalone finding to date.)
- **CPU:GPU energy division by phase**: does the rail mix shift between
  compute-bound prefill and memory-bound decode? Upstream of split
  economics.
- **KV-growth decode drift**: does per-token energy rise with sequence
  position? Valid only in CHUNKED form — token cadence (~4 ms) far
  outruns the power sampler (~113 ms); no per-token joule claims.
- **Cooldown recovery as thermal characterization**: recovery time vs
  preceding run intensity; cap-hit rates (observed: one 305 s cap-hit vs a
  117 s recovery in the first flagship experiment).
- **Failure frontier**: structured `unsupported` bundles as data — which
  model/quant/context combinations fit, fail, or throttle. Competitors
  discard their failures.
- **Cold-start / keep-warm energy**: model-load joules and the reload-vs-
  resident breakeven. Needs sampling outside the current measured window
  (harness extension).
- **Energy-per-correct-answer vs difficulty** (C-004): instrumented by the
  `affine_mod_ladder_v1` scored workload profile (see below). Claim shape
  pinned by the council: "energy per correct answer rises as accuracy
  falls under a controlled per-attempt energy envelope" — difficulty is
  DESIGNED to hold token budget approximately constant, and observed
  token/stop-reason distributions must be reported to verify residual
  EOS/output-length effects are negligible (wrong-answers-terminate-early
  would bias the curve's magnitude). NOT "difficulty causes energy."
  Amendment 2026-07-08 (C-014): before any scored campaign, an
  envelope-validation smoke gate must show level-invariant emitted-token
  and stop-reason distributions; energy/correct also requires the binomial
  guard in AP-5 (`docs/contracts/analysis_plans.md`). The full 64-level
  scored campaign is deferred until C5-1.9 has a claims-index/figure
  consumer.
- **Speculative-decoding energy**: joules per accepted token with/without
  a draft model. Needs runtime support + quality-equivalence controls.
- **Power-mode Pareto**: energy-latency tradeoff across OS power modes;
  wait until power mode is a first-class config/environment field.
- **Deferred (C-003/C-004 unanimous): general joules-per-solved-task /
  intelligence-per-joule** — drags in accuracy-evaluation policy before
  the measurement dataset matures, and sits in Intelligence per Watt's
  lane where JouleWise is least differentiated. The quarantined ladder
  profile above is the minimal version that survives.

## Instrument expansions adopted by C-004 (queue P2-009 / P2-010)

- **P2-009 rich telemetry (land FIRST — zero capture cost):** parse the
  already-captured-but-discarded plist fields — per-cluster E/P-core DVFS
  residency histograms, per-core frequencies/idle/parking, GPU
  freq/dvfm_states/idle_ratio/sw-requested-vs-achieved state, vendor
  combined_power as a cross-check — plus per-bundle environment snapshots
  (battery/charger state, Low Power Mode, memory pressure, load, display
  state; all sudo-free). Evidence this matters: decode pins the GPU at
  1380 MHz / idle_ratio 0.0 / ~22 W, and the contaminated idle window was
  mechanically visible in `gpu.idle_ratio` (first half at 13 W / 1363 MHz
  before true idle) — parsing it turns our contamination anecdote into an
  automated idle-quality gate. Opt-in `rich_telemetry` tier later: the
  `tasks` sampler (per-process attribution — the direct answer to
  background contamination), disk/network samplers.
- **P2-010 scored workload suite v1:** `affine_mod_ladder_v1` per the
  C-004 design (seed-deterministic SHA-256-derived modular recurrences;
  difficulty = iteration count with prompt shape and answer length fixed;
  exact-integer scoring; levels `{1, 2, 4, 8, 16, 32, 64}`, 16 items/level;
  suite-per-bundle with item/level marker events; level-window energy
  primary; per-item flagged unidentifiable below minimum samples;
  correctness lives in stdlib `joulewise/workloads.py`, scored by the
  reducer so summaries stay re-reducible). Quarantine rules (C-004):
  one optional workload profile, correctness as annotation, no
  "difficulty causes energy" claims. Amendment 2026-07-08 (C-014):
  P2-010 splits into P2-010a suite substrate and P2-010b smoke ladder;
  the full scored ladder remains deferred as above.
  Amendment 2026-07-08 (D-047.1): the level set is the ratified
  powers-of-two set above, not a linear 1..64 sweep.

# Suite architecture v2, benchmark interop, and capability map (Council C-015, 2026-07-08)

## Suite mechanism

C-015 adopts one suite mechanism for benchmark breadth: a suite CAMPAIGN is
`B` whole-suite bundles x `k` distinct items; each suite bundle executes
its `k` items once (`r_within = 1`).
Replication is the count of whole-suite bundles (`B >= 5`, top-up to
`B = 10` near the floor). Item windows inside one bundle are breadth and
attribution evidence, not independent `n` (D-038/AP rules).

Within-bundle repeats are reserved for sentinel items. They estimate
order/cache/thermal effects and same-session repeatability; they never
inflate `n` (C-015). There are no per-item micro-cooldowns by default:
back-to-back execution is a named session ecology, not a flaw. Order
rotates round-robin or Latin-square across bundles, with `item_index`,
`block_index`, `position`, `prev_item`, `prefix_group`, and `order_seed`
recorded (C-015).

Split a suite into balanced blocks when measured wall time exceeds roughly
10-15 minutes or when drift sentinels / floor identifiability degrade.
The first default is `k = 24`; mature panels may use `k = 48` only after
Window A floors and drift checks are clean (C-015). Throughput arithmetic:
`suite_items_per_hour = 3600 * k / (load + idle + cooldown + k * item_runtime)`,
which buys roughly 3-15x item coverage versus one-item bundles, while
`B` remains the `n` and items remain breadth (C-015).

Architectural line: after P2-010a, no workload expansion gets bespoke
marker/window plumbing. New benchmarks are manifests plus generators.
`affine_mod_ladder_v1`, `jw_mixed_v1`, `q4_l3_shape_grid_v1`, the content
sentinel, and benchmark imports are all profiles of the same suite
manifest, marker, and window mechanism (C-015).

## Minimal substrate scope

P2-010a is capped to the minimal generic substrate (C-015): suite/item/block/level
markers, `BundleReader.item_windows()`, source/category/output-policy
fields, per-item token/stop/response hashes, order/cache metadata, manifest
validation, and the per-item validity/status model below. Future
`docs/contracts/run_bundle_layout.md` fields for suite/item/block/level
markers and per-item outputs land with implementation, not in this docs batch
(C-015).

P2-010a status enum:

- `succeeded`
- `malformed`
- `capped`
- `runtime_failed`
- `below_floor`
- `excluded_from_claim`

Aggregation rules (C-015): a block or suite remains claim-usable when the
predeclared aggregation level has enough `succeeded` item windows, paired
markers validate, strict bundle validation passes, and failed/excluded
items are reported rather than silently dropped. `below_floor` items may
contribute only to block/suite-level windows, not item-level joule claims.
`malformed`, `capped`, and `runtime_failed` items remain provenance and
failure-frontier evidence but do not enter numeric claim denominators
unless an AP row predeclares that status as part of the endpoint.
`excluded_from_claim` is an explicit analysis decision with a reason and
does not make the surrounding strict-valid bundle unusable by itself.

Deferred from P2-010a (C-015): scorers, import-specific fields, and rich
difficulty machinery until suite profiles need them.

## `suite_manifest` field sketch

Trimmed P2-010a substrate scope (C-015):

```yaml
schema_version
suite_id
suite_profile
suite_revision
suite_seed
generator:
  name
  version
  parameters_hash
analysis_contract:
  independent_unit
  primary_window_class
  allowed_aggregation_levels
execution_policy:
  order_policy
  within_bundle_repeats
  cooldown_policy
  cache_policy
  warmup_policy
  default_output_policy
source_manifest:
  source_id
  source_kind
  revision
  subset_id
  subset_sha256
  license
  contamination_note
items:
  - item_id
    item_type
    category
    difficulty:
      axis
      value
      scale
      label
      source
      quarantine_note
    shape:
      planned_prompt_tokens
      planned_output_tokens
      prompt_level
      decode_level
    source:
      source_item_id
      source_sha256
      prompt_template_id
      license
      contamination_note
    grouping:
      condition_id
      block_id
      level_id
      prefix_group_id
    output_policy
    status_policy
    tags
markers:
  suite_start_event
  suite_end_event
  block_start_event
  block_end_event
  level_start_event
  level_end_event
  item_start_event
  item_end_event
outputs:
  per_item_response_hash
  per_item_token_count
  per_item_stop_reason
  per_item_status
```

Amendments 2026-07-08 (D-044/D-045/D-046): the sketch is historical and
receives these additive pins. `outputs` gains `per_item_response_text`,
with response text carried in `outputs/suite_items.jsonl` (D-045.8).
`markers` and `outputs` are optional in authored manifests, materialized
to pinned defaults, validated when present, and included in the canonical
effective-manifest hash (D-044/D-045.3). Items gain an additive,
mutually-exclusive `prompt_token_ids` source for ids-native sentinels,
with per-item prompt identity using the D-033 token-ID hash
(D-045.5/D-046).

Deferred fields (C-015): `scoring.scorer_id`,
`scoring.expected_answer_hash`, `scoring.correctness_quarantine`, import-
specific source fields, and richer grouping/difficulty structures such as
`pair_id` and `holdout_role` until a profile and AP row need them.
AP-5's smoke-ladder acceptance already requires level-window energy, so
the deferral condition is met at birth (verification catch, C-015).

## Difficulty metadata rule

Difficulty is first-class quarantined item metadata (C-015):
`{axis, value, scale, label, source}`. Shape is not difficulty:
`q4_l3_shape_grid_v1` prompt/decode cells stay under `shape`, not
`difficulty`. Difficulty metadata enables stratified analysis and envelope
checks; it never licenses "difficulty causes energy" or
intelligence-per-joule wording, and the C-004 quarantine composes.

## Benchmark import

`benchmark_import` is a thin source-to-suite manifest that composes with
the C-005 frozen-subset discipline: hash-manifested subsets, never
"latest split" (C-015). Field sketch:

```text
schema_version
manifest_id
suite_profile
source_benchmark:
  source_id
  name
  upstream_url
  citation
  license_id
  license_text_sha256
  redistribution_policy
  revision_or_commit
  retrieval_date
  source_archive_sha256
  source_split
contamination:
  note
  known_public_benchmark
  intended_use
  prohibited_claims
subset:
  selection_rule
  selection_rule_sha256
  selector_version
  selected_item_ids
  selected_item_ids_sha256
  canonical_subset_json_sha256
prompt_mapping:
  prompt_template_id
  prompt_template_sha256
  source_fields_used
  render_policy
  rendered_prompt_sha256_policy
  output_policy
expected_answer:
  source_field
  stored_as
  expected_answer_sha256
  quarantine: true
  scorer_allowed: false
items:
  suite_item_id
  source_item_id
  source_row_sha256
  source_position
  type_label
  difficulty_label
  difficulty_source
  category
  level
  prompt_template_id
  expected_answer_sha256
  license_override
  contamination_override
  shape_hints
  tags
```

First target: HumanEval as a plumbing smoke import, not a difficulty or
accuracy paper (C-015). Rationale: MIT license, small recognizable corpus,
contamination is explicit and quarantined, 256/512-token code completions
clear the observed ~9 Hz item-window floor more plausibly than one-letter
answers, and `difficulty_label = none/source_not_provided` is acceptable
for a plumbing smoke. MMLU and tinyBenchmarks are rejected as first import
targets because they drag the project toward short-answer score estimation
or benchmark-score estimation. FLORES is the second import target for
tokenizer/multilingual science (C5-W.4/C5-I.3), not the first plumbing
target (C-015).

Claims unlocked by imports (C-015): L0 "JouleWise can freeze and execute an
external benchmark subset as suite items with auditable provenance"; L1
"on a named stack/boundary/output policy, external-shaped items produced
observed item/subset energy and token/stop distributions"; L2 only after an
AP row and repeated strict-valid bundles. Never claim accuracy, pass@k,
capability, benchmark-score standing, or intelligence per joule from this
layer (C-015/C-004).

## Export / energy layer

C-015 adopts a marker-emitting shim for export. The external harness owns
prompts, generation semantics, accuracy artifacts, and metric artifacts.
JouleWise owns power capture, bundle assembly, marker validation, and
energy reduction. The full contract lives in
`docs/contracts/adapter_contracts.md`.

P2-022 is a verdict-shaped feasibility spike (C-015) with verdicts:

- `external_markers_supported`
- `partial(<limitation>)`
- `external_markers_unsupported`

(contract home: docs/contracts/adapter_contracts.md)

P2-022 inherits D-035 subprocess isolation and D-036 computed-verdict
discipline. Its scope is pinned to energy-layer feasibility only (C-015):
3+ marked items, external result artifact hashed, strict bundle valid, no
accuracy interpretation, no leaderboard join, no pass@k-energy ratio, and
no general adapter framework. Any L2 energy comparison from the shim needs
strict bundles, repeated runs, same or calibrated boundary, and an AP row
(C-015).

## Kill / defer

Kill or defer:

- leaderboard integration.
- live dataset fetching.
- "latest split" support.
- JouleWise accuracy scoring beyond quarantined annotation.
- external judge calls, retries, pass@k, or benchmark-score normalization.
- full adapter per harness as the first export path.
- generation-callable wrapper as the first export path.
- MMLU/tinyBenchmarks as first import.
- public energy model-card leaderboard before cross-lab replication.
- per-item uncertainty treated as independent replication.
- any intelligence-per-joule ratio.


exec
/bin/zsh -lc "sed -n '411,825p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## New questions

Interop questions adopted by C-015:

- **C5-I.1 External benchmark energy signatures:** Do imported benchmark
  families have distinguishable energy profiles after matching token shape
  and output policy? Ceiling L2, no capability claim.
- **C5-I.2 Published-difficulty strata vs energy:** Do source-provided
  difficulty or published accuracy strata correlate with energy/stop
  behavior? Ceiling L1 association unless preplanned repeated-bundle L2;
  never "difficulty causes energy."
- **C5-I.3 FLORES tokenizer fertility tax:** For semantic-matched vs
  token-matched FLORES items, how much energy follows tokenizer fertility
  by script/language? Ceiling L2.
- **C5-I.4 Harness overhead floor:** For external harnesses, when does
  harness/process overhead dominate item energy? Ceiling L1/L2
  measurement-method result.
- **C5-I.5 Prompt-template energy sensitivity:** For the same external
  item, how much does canonical vs JouleWise-rendered prompt format change
  energy? Ceiling L2.

Architecture-unlocked candidates, recorded post-2O/post-floor and not
promised campaign work (C-015):

- **Session-shape energy:** does a realistic mixed session cost what
  fixed+prompt+decode coefficients predict, or is there a session overhead
  term?
- **Order-position effects:** how much does energy drift by item position
  after controlling for shape and category?
- **Cache/prefix economics:** what is the joule benefit of prefix reuse,
  resident model state, or prompt-cache warmth versus cold independent
  requests?
- **Reload-vs-resident scheduling:** at what item/session length does
  suite-style batching dominate one-request bundles in total energy and
  wall time?

## Capability map by claim ceiling

### Today

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Can JouleWise produce auditable local-LLM energy evidence? | L0/L1 | "The harness can execute `<target/runtime/telemetry>` and preserve config, metadata, events, raw power trace, raw telemetry, outputs, and reducer summary in a strict-valid run bundle." | Existing Mac/MLX/powermetrics bundles; strict bundle layout. | Strict validation proves re-derivation of recorded evidence, not independent hardware rerun. |
| What did Qwen2.5-1.5B consume on the M3 Max for the 512-output-token smoke workload? | L1 | "On `M3 Max / MLX / powermetrics SoC rails`, under `<workload/output policy>`, Qwen2.5-1.5B-4bit observed `<mean gross J>` request energy, `<TTFT>`, and `<throughput>` across 3 strict-valid bundles." | 2026-07-06 2I: about 47 J gross, about 94 ms TTFT, about 257 tok/s, gross CV 1.4%. | Idle-subtracted result is contaminated in rep 1; use gross for the cleanest current instrument result. |
| What did Qwen3.5-122B-A10B consume on the same workload? | L1 | "On `M3 Max / MLX / powermetrics SoC rails`, under the same 512-output-token workload, Qwen3.5-122B-A10B-4bit observed `<mean gross J>` request energy, `<TTFT>`, and `<throughput>` across 3 strict-valid bundles." | 2026-07-07: about 304 J gross, about 270 ms TTFT, about 46 tok/s, gross CV 0.3%. | L1 only; n=3 is below comparative protocol. |
| Did the two observed models demonstrate active-parameter scaling? | No; L1 hypothesis only | "The two observed Mac/MLX/powermetrics points are consistent with a fixed/marginal decode-time hypothesis, but they do not support an active-parameter scaling claim." | 122B addendum and claims-ladder downgrade. | Model size, architecture, quantization, and runtime details are confounded. |
| Are short prefill phase joules resolvable at current powermetrics cadence? | L1 "not resolvable" | "On `M3 Max / MLX / powermetrics`, short-prefill phase energy for `<~94 ms window>` is not resolvable at the observed sampling cadence and must not be reported as a standalone joule result." | Observed about 8.8-8.9 Hz; Phase 4 says about 94 ms prefill has fewer than one sample. | Sampler cadence remains near current observed rate. |
| Can same-machine MLX KV replay preserve token identity and size prediction? | L1 feasibility result | "On this M3 Max / mlx-lm stack, prompt-cache replay was supported for `<prompt length>`: resumed greedy decode matched monolithic tokens and measured cache size was within `<delta>` of the KV-size prediction." | Stage 3.0.1: 1024/2048 prompt cache, 64/64 tokens identical, +0.018%/+0.009% size delta. | Same machine/same venv only; not cross-machine portability. |

### After Window A

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| What is the detection floor per metric/window? | L1 methodology result | "For `<target/backend/metric/window class>`, differences below `<floor>` J are not resolvable; supported comparisons use `max(floor_abs_j, floor_cmp_j)`." | P2-015 calibration. | Calibration machine state is representative of later quiet campaigns. |
| What are per-profile Mac baselines? | L1 per condition | "On `M3 Max / MLX / powermetrics`, `<model>` under `<profile>` observed `<energy_request_j>`, `<gross J>`, `<mJ/output-token>`, `<TTFT>`, and `<throughput>` with 95% t-intervals over n=5." | 2M: `short_short`, `long_short`, `short_long`, `mid_mid`. | Output-token denominator and output policy must be runtime-observed/pinned. |
| Does workload shape change request energy on one stack? | L2 | "Within `M3 Max / MLX / powermetrics`, `<profile A>` differed from `<profile B>` for `<model>` by `<effect>` on `<metric/window>`, with n=5 per condition, CIs, manifest order, and effect above floor." | 2M + AP-2. | Drift sentinels and block-position metadata LANDED 2026-07-08 (PR #15). |
| Is prefill/decode power asymmetry visible at long context? | L2 | "Within `M3 Max / MLX / powermetrics`, `long_short` and `short_long` differed in gross phase-window power/energy structure by `<effect>`, above the Window A floor; short-prefill windows remain not resolvable." | 2M/AP-2. | Phase claims are gross-only until phase-idle modeling exists. |
| Do same-boundary efficiency rankings flip across 2M profiles? | L2 | "Within `M3 Max / MLX / powermetrics`, `<condition A>` ranked above `<condition B>` for `<metric>` on `<shape>` only where rank gap exceeded comparison MDE; otherwise the result is an unresolved tie." | 2M + AP-3. | Two-model/four-shape grid may produce unresolved ties rather than rank claims. |
| Do rail/DVFS signatures differ by phase? | L2 structural, not absolute rail truth | "Within `M3 Max / MLX / powermetrics`, rich telemetry showed `<GPU/CPU/ANE/DVFS>` structure differed between `<phase/profile>` and `<phase/profile>`; the claim is about modeled-rail structure, not full-system watts." | 2M with P2-009 rich telemetry. | Powermetrics rails are modeled SoC subsystems, not wall power. |

### After Window B + substrate

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Can Q4 fit fixed + prompt + decode energy terms? | L3 | "For `<target/model/quant/policy>`, the categorical model `E = fixed + prompt_level + decode_level` predicted held-out cells `(512,256)` and `(4096,512)` within `<error>` after floor and residual checks." | P2-019 `q4_l3_shape_grid_v1`, AP-1. | Holdouts may fail or effects may be below floor, forcing L1/L2 downgrade. |
| Do rankings stay stable on the full shape grid? | L2 | "Within the same boundary, `<model/quant/runtime A>` ranked above `<B>` on `<shape/metric>` only where rank gap exceeded comparison MDE; otherwise unresolved tie." | Window B grid + AP-3. | Rank gaps may be smaller than MDE. |
| Does synthetic prompt content matter at fixed shape? | L2 | "At equal shape, `<content condition>` differed from repeated-seed control by `<delta>` on request energy, with n sized from Window A and above floor." | P2-020 content sentinel, AP-6. | Realized shape/stop policy must stay matched. |
| Does category explain energy beyond token counts? | L2 | "On the common `512/256 fixed_budget_exact` stratum, category residual after controlling for shape was `<delta>`; equivalence/null only if the residual CI lies entirely within ±2% of request energy AND the 2% margin exceeds max(floor_abs_j, floor_cmp_j) (AP-4 gate)." | `jw_mixed_v1` identification core after P2-010a; AP-4. | Small category deltas may be below floor. |
| Does natural-EOS "thinking" inflate reasoning-model energy? | L2 | "For `<reasoning model>`, natural-EOS reasoning requests consumed `<delta>` more request energy than fixed-budget controls, attributable to observed emitted-token/stop-reason distributions, not hidden correctness filtering." | `jw_mixed_v1` natural-EOS pilot. | Output-length inflation must be observed cleanly; no accuracy/judge claim. |
| Is multilingual tokenizer fertility an energy tax? | L2 | "For `<script/language>`, semantic-matched energy differed from token-matched controls by `<delta>`; token-matched null/effect reported separately." | `jw_mixed_v1` multilingual legs; FLORES after HumanEval smoke. | Source licensing and tokenizer-shape matching must be exact. |
| Energy per correct answer under controlled envelope? | L2, only after P2-010b/full scored run | "On the controlled affine ladder, `<model class>` observed `<energy_per_correct>` at `<level band>` only where level-window energy cleared floor and the correctness denominator guard passed; no intelligence-per-joule claim." | P2-010a substrate + P2-010b smoke + later scored campaign; AP-5. | Envelope validation and binomial guard can force `not estimable`. |
| External marked-runner energy layer? | L1/L2 with AP row | "External harness `<X>` version `<Y>` reported metric artifact `<Z>`; JouleWise measured energy for the same marked item/subset windows." | P2-022 shim spike, then AP-covered repetitions only. | Harness markers must pair, stay inside measured windows, and preserve hashed result artifacts. |
| HumanEval import smoke? | L0/L1 | "JouleWise froze and executed a HumanEval subset as suite items with auditable provenance and observed item/subset energy under a named output policy." | P2-023 after P2-022. | Plumbing smoke only; no pass@k, accuracy, or coding-capability interpretation. |

P2-022 shim and P2-023 HumanEval rows are post-2M + substrate (Window B not required).

### Hardware-gated

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Does split inference reduce energy? | L2 boundary-labeled; stronger with wall calibration | "For `<device pair/link/model/shape>`, split total energy `<prefill + serialize + transfer + deserialize + decode>` was `<less/greater>` than the better monolithic reference by `<delta>`, with boundaries named and calibration status stated." | Phase 3 split; Q1/F4/F5. | Cross-boundary sums are descriptive unless calibrated. |
| How sensitive is split energy to link speed? | L2 | "For `<payload/model/pair>`, changing `<1GbE/2.5GbE/10GbE>` changed transfer energy/time by `<delta>` and moved/did not move the crossover within the measured range." | P1-004 links + transfer bench. | Link throughput must be measured, not assumed. |
| What is the split energy-latency Pareto frontier? | L2 | "Within `<comparison set>`, `<configuration>` is Pareto-frontier because no measured alternative had both lower energy/token and lower `<latency metric>`." | Phase 3 + F6. | Latency metric choice must be fixed per figure. |
| Does measurement boundary change conclusions? | L2; L4 only with replication | "For `<condition pair>`, the conclusion under platform rails `<matched/flipped>` under `wall_meter AC` by `<delta>`." | P1-003 wall meter; Q6/F11. | Wall-meter synchronization/export quality. |
| Do KV-size predictions match measured transfer economics? | L2 | "For `<runtime/model/link>`, analytic KV size predicted serialized payload within `<error>` and transfer energy/GiB within `<interval>`." | P1-004 + P1-006; C5-2.3. | Runtime cache format must be portable or explicitly scoped. |
| Do device rankings generalize beyond one machine? | L2 within boundary; L4 with second unit/calibration | "Across named `<units/stacks>`, `<finding>` replicated under stated workloads and boundaries; cross-boundary quantitative ranking uses named calibration bundles." | P1-006 devices, second unit, wall/USB-C, cross-lab. | Unit-to-unit variance may dominate current floors. |
| Local-vs-datacenter full-system crossover? | Scenario result, not measured-equivalent cloud claim | "Under documented external datacenter-energy assumptions and local `wall_meter AC` measurement, local request energy was `<less/greater>` than the modeled remote alternative for `<workload>`." | Wall meter + network leg; C5-2.9. | Cloud-side energy remains assumption-based, not measured by JouleWise. |

C-015 records three unscheduled cheap campaigns as a select-after-floors
shortlist, not stealth scope: C5-1.6 sampler ABBA, C5-1.12 quantization
benefit decomposition, and C5-1.8 runtime energy attribution. Queue row
P2-024 owns the post-Window-A selection.


# Hardware-gated research agenda — steelmanned potential (Council C-005)

Drafted 2026-07-07 by council C-005 (session shape B; see
`docs/council_log.md` C-005 for positions, adjudications, and dissents).
Format follows `docs/research_question_bank.md`: candidate questions, not
promotions — promotion still requires a named RQ slot in
`PROJECT_STATUS.md`, a data plan that does not displace queue ranks, and
scope fit. IDs here are `C5-<tier>.<n>` to avoid colliding with Q1-Q6.

Every question below survived a devil's-advocate (examiner) round; the
scoping is deliberate, not decorative. Standing kills re-affirmed and
inherited by everything here: no per-token joule claims (~9 Hz sampler vs
~4 ms token cadence — chunked windows only), no unqualified absolute-joule
claims from modeled rails, no general intelligence-per-joule, claim
wording "on this M3 Max / MLX / powermetrics" until a second unit or lab
exists, and present-tense capability claims only for landed code (P2-010 scored suite is QUEUED,
not landed (D-014/P2-011 aggregation and P2-009 telemetry LANDED 2026-07-07)).
(Amendment 2026-07-08: the P2-010 substrate + affine core + generator
engine are now LANDED (PRs #17-#20, D-044..D-047); still not landed:
envelope-gate script, real-tokenizer manifests, all suite campaigns.)

## Why this instrument matters (steelman preamble, examiner-scoped)

**Auditability is the differentiator, not topic novelty.** Energy
benchmarks exist (MLPerf Power; TokenPowerBench; ML.ENERGY-style
datacenter work) — what does not exist is local-inference joules/token
that a skeptic can re-derive: JouleWise publishes self-contained bundles
where config, raw power trace, vendor telemetry, event log, and outputs
are preserved and `validate-bundle --strict` proves the summary re-reduces
identically from raw evidence. Energy tables are otherwise unauditable at
exactly the step that matters.

**Energy per request is becoming the binding constraint on local AI.**
Battery, thermal envelope, and sustained throughput all reduce to joules
per completed request. Latency says whether a local model feels fast
once; `energy_request_j` with uncertainty says whether it can run all day.
The instrument already resolves this at CV 0.3-1.4% across repetitions.

**Apple-Silicon unified memory is a clean window into the memory-bound
decode regime.** The measured 1.5B vs 122B-MoE pair showed energy/token
numerically aligning with the active-parameter ratio while decode power
stayed nearly flat (~23.5 → ~27.5 W). That is hypothesis-generating, not
a scaling result (see C5-1.1), but it demonstrates that the instrument can
see the shape of the regime that throughput benchmarks cannot.

**Negative results are structured data.** did-not-fit, throttle,
contaminated-idle, and cap-hit outcomes produce complete `unsupported` or
quality-flagged bundles. Competitors discard their failures; here the
feasibility frontier is itself a reportable dataset (this is how a
negative Hailo verdict stays a finding).

**The benchmark can referee efficiency claims.** Quantization, runtime,
and architecture "efficiency" claims mix latency, memory, and energy with
no common accounting. Typed configs + one reducer + named measurement
boundaries make within-boundary refereeing possible today and boundary-
labeled cross-target comparisons possible with planned hardware.

**Q4's fixed-vs-marginal model turns benchmark data into engineering
budgets.** `E = fixed + prefill(p) + decode(d)` per target/model/quant
lets an app team budget a workload distribution (an agent session, a RAG
pipeline) from benchmark coefficients — the bridge from instrument to
battery-life engineering.

**The split study is a first-of-kind edge measurement.** Prefill/decode
disaggregation is argued from datacenter throughput; nobody has measured
the ENERGY crossover on local links with both-end power sampling and
per-stage decomposition (prefill/serialize/transfer/deserialize/decode).
Either verdict — crossover exists or doesn't in range — is publishable.
(Examiner note, recorded as standing tension: this is also the most
hardware-gated item in the agenda; the feasibility-first Phase 3 ladder
is the mitigation.)

**The infrastructure outlives any single result.** Every future target is
forced through the same contract (config → bundle → strict re-reduction →
boundary-named summary). The M3 Max numbers are the demo; the reusable
referee is the contribution.

## TIER 1 — answerable with current hardware (M3 Max alone)

Landed software (P2-009 rich telemetry, P2-011 uncertainty
aggregation, 2M campaign tooling — all 2026-07-07) is available;
queued software (P2-010 scored suite) is assumed where noted; no new
hardware. (Amendment 2026-07-08: the suite substrate/ladder-core/
generators are landed, PRs #17-#20; campaign execution still pending.) Throughput reality: ~30-75 bundles/hour makes n=10-20 designs
cheap.

- **C5-1.1 Active-parameter energy scaling (the honest version of the
  122B observation).** Does decode energy/token scale with active rather
  than total parameters across dense and MoE models on one pinned stack?
  Measure on the named M3 Max / MLX / powermetrics SoC-rail boundary:
  gross decode-window joules, mean power, and throughput across 4-6 model
  points (dense 1.5B/7B/14B bridge + ≥2 MoE), same quant recipe, pinned MLX
  version, fixed shapes, n≥5 interleaved; fit gross mJ/token ~ active_params
  (+ total-param/KV covariates) with intervals. Any idle-subtracted result is
  a labeled within-device secondary sensitivity view, not the scaling
  headline (D-067).
  Hardware: now. Methodology: runtime is part of the condition — rerun
  after MLX updates as a separate condition. Threat: model families
  differ in more than active params; the dense bridge and quant pinning
  carry the inference. Who cares: efficient-ML and MoE architecture
  researchers; local-inference benchmark authors. Amendment 2026-07-08
  (C-014): with 4-6 model points, this supports descriptive L2 pairwise
  contrasts only unless the model set grows enough for a predeclared
  one-covariate fit; never fit active+total+KV covariates on 4-6 model
  points.

- **C5-1.2 Context-length energy scaling.** Where does measured energy
  stop being linear in prompt length? Measure: prefill/decode energy over
  prompt 128→8192 (fixed decode 64/256), n≥5; unsupported cells recorded.
  Hardware: now. Methodology: chunked windows; short-prompt prefill
  reported "unresolved at sampler resolution", never 0.03 J-style point
  claims. Threat: SoC boundary underrepresents unified-memory traffic —
  directional bias for long-context (examiner #11); flag pending Q6
  calibration. Who cares: long-context model teams, serving researchers.

- **C5-1.3 Phase-resolved compute-vs-memory signatures (uses landed P2-009 telemetry).**
  Does the rail mix and DVFS residency shift between compute-bound
  prefill and memory-bound decode, and how does the shift move with model
  size/quant? Measure: per-phase CPU:GPU energy division, GPU
  frequency/dvfm residency, idle_ratio across the 2M matrix. Hardware:
  now. Methodology: promotes the banked "CPU:GPU division by phase" item
  with the telemetry that makes it cheap. Threat: modeled rails — claims
  are about STRUCTURE (ratios, shifts), not absolute rail watts. Who
  cares: Apple/Metal/MLX performance engineers, systems-paper authors.

- **C5-1.4 DVFS residency as a throttling early-warning (uses landed P2-009 telemetry).**
  Do residency histograms and idle_ratio drift predict throttling before
  energy/throughput visibly degrade under sustained inference? Measure:
  20-60 min sustained blocks; per-rep energy, residency, cap-hit rates,
  recovery slopes; n≥5 blocks. Hardware: now. Methodology: cooldown-gate
  records and interleaving separate warmup, drift, and throttling.
  Threat: one chassis/ambient; report as within-target characterization.
  Who cares: laptop-inference tool builders, mobile/edge systems
  researchers, thermal-management teams.

- **C5-1.5 Cooldown-recovery curves and the energy tail (promotes banked
  item).** Recovery time and excess idle joules vs preceding run
  intensity; is the tail material to honest energy/request accounting?
  Measure: post-run recovery traces after an intensity ladder; time-to-
  baseline, cap-hit rate, excess joules; n≥5. Hardware: now. Threat:
  ambient sensitivity — record environment snapshots (P2-009). Who
  cares: on-device serving teams, benchmark methodology authors.

- **C5-1.6 Sampling-strategy energy overhead (power-gated).** Does
  temperature/top-p/beam sampling cost measurable energy beyond
  deterministic decoding at fixed output length? Measure: greedy vs
  sampled at fixed decode caps, recorded stop reasons; PRECONDITION:
  measured detection floor first; n≥10 paired ABBA. Hardware: now.
  Threat: plausibly below floor at n=5 — the null ("sampler choice is
  energy-free at this resolution") is the likely and still-reportable
  result. Who cares: runtime maintainers, generation-defaults tuning.

- **C5-1.7 Keep-warm vs reload breakeven (promotes banked cold-start
  item; harness extension).** Model-load joules, resident idle-power
  delta, cold-vs-warm TTFT → breakeven interarrival time per
  model/quant. Measure: load-window sampling (extension: measure outside
  current window), idle-resident deltas, n≥5. Hardware: now. Threat:
  idle-resident delta may be near the detection floor for small models;
  report identifiability. Model-load/warmup trace capture was reviewed and
  DEFERRED by C-015 (R2 items 14-15); it must land before any C5-1.7
  corpus. Who cares: desktop-assistant and agent-framework teams,
  serverless-inference researchers.

- **C5-1.8 Runtime energy attribution.** How much of measured inference
  energy belongs to the runtime, not the model? Same model artifact
  (where format permits) across MLX vs llama.cpp-Metal vs ollama on the
  same machine. Measure: energy/token, power, TTFT, rail mix over a
  shared shape grid, n≥5; artifact hashes and versions pinned. Hardware:
  now. Methodology: where formats force different artifacts (MLX vs
  GGUF), the comparison is stack-vs-stack, stated as such. Threat:
  version churn — this question is BUILT on the pinning discipline
  rather than wounded by it. Who cares: runtime maintainers, local-LLM
  users, model publishers choosing release formats.

  **2026-07-17 kernel-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **NV**. On the 3080 Ti, same model artifact where format
  permits: llama.cpp-CUDA vs vLLM (TensorRT-LLM gated on Ampere-support
  verification) — how much energy variance tracks kernel-library identity vs
  runtime scheduler? Ceiling: **L2 stack-vs-stack**. Forbidden upgrade: **no
  `belongs to the kernel layer` language when artifacts/formats differ; no
  runtime-agnostic kernel claims**. This is an amendment to C5-1.8, not a new
  C5-1.13 thesis. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-1.9 MoE-vs-dense energy per correct answer, quarantined (needs
  P2-010).** Under the controlled-envelope ladder, do MoE and dense
  models at similar quality bands differ in energy per correct answer?
  Measure: affine_mod_ladder_v1 level-window energy + exact scoring;
  token/stop-reason distributions reported (EOS-bias audit). Hardware:
  now. Methodology: C-004 quarantine binds — correctness is an
  annotation; claim template "on this controlled ladder", never
  intelligence-per-joule. Who cares: MoE architecture teams, benchmark-
  methodology reviewers.

- **C5-1.10 The failure frontier as an energy dataset (promotes banked
  item).** Which model × quant × context cells fit, fail, swap, or
  throttle on 128 GB unified memory — with pre-failure energy and memory
  pressure recorded? Measure: full matrix including structured
  `unsupported` bundles, env snapshots. Hardware: now. Threat: one
  memory configuration; frame as the 128 GB-class frontier. Who cares:
  model release engineers, hardware buyers, benchmark authors.

- **C5-1.11 Dark-silicon rail utilization, systematized (promotes banked
  item; needs P2-009).** What fraction of the SoC's rails does each
  runtime/model pair energize (ANE-dark being the first quotable
  instance)? Measure: per-rail energy share and residency by phase
  across the runtime grid of C5-1.8. Hardware: now. Threat: modeled
  rails — report utilization structure, cross-checked against vendor
  combined_power. Who cares: accelerator vendors, runtime implementers.

- **C5-1.12 Quantization benefit decomposition, Mac leg.** For MLX quant
  variants of one family (4/8-bit), how much energy benefit is lower
  power vs shorter time? Measure: decode energy, mean power, throughput
  per quant at fixed shapes, n≥5. Hardware: now (extends to Tier 2 for
  CUDA/GGUF legs). Threat: quant recipes change outputs — greedy-diff
  and report divergence. Who cares: quantization researchers, edge
  deployment teams.

## Workload/query-set expansion (first-class topic, Tier 1 hardware)

Today's workloads are single-prompt fixed-shape grids plus the queued
affine ladder. (Amendment 2026-07-08: the affine ladder CORE is landed,
PRs #17-#20; the envelope-gate script and smoke campaign remain queued.) The council's workload lens designed the expansion; the
examiner frame was applied up front: at fixed token shape, most category
differences may collapse into token counts — that null is itself a
publishable result, named here the **Token-Shape Sufficiency Null**.

**Category taxonomy and expected energy mechanisms.** Six categories,
each with a mechanistic reason energy could differ and an honest
distinguishability call:
chat/instruction (high output-length variance under natural EOS; expected
NULL at fixed shape — the ecological baseline); code generation
(decode-heavy, distinct stop-reason behavior; near-null at fixed budget
unless tokenizer throughput differs on code tokens); summarization/
long-context (prefill-heavy, KV growth — YES, distinguishable via prefill
energy/TTFT/phase mix); reasoning/CoT (thinking-token inflation on
reasoning models — YES, the category effect most likely to be large,
directly measurable on the already-benchmarked Qwen3.5-122B); structured
JSON extraction (early valid-close stops make short answers cheap —
collapses at fixed envelope; probes EOS bias); multilingual (tokenizer
fertility differs sharply by script — YES when semantically matched,
expected null when token-matched; run BOTH, the pair separates fertility
from semantics).

**Realistic-vs-synthetic discipline (hybrid, both by design).**
Deterministic seed-derived synthetic profiles are the CONTROLS
(reproducible, shape-matched, redistribution-safe); pinned realistic
exemplars are the ecological probes (licensing/contamination/tokenizer
caveats recorded per source). Every realistic category runs in two modes:
`fixed_budget_exact` (greedy, EOS suppressed, fixed max_tokens — the
headline category-at-fixed-shape comparison) and `natural_eos` (greedy,
EOS allowed, stop reasons recorded — the operational-cost view). EOS-bias
rule inherited from C-004: natural termination is a workload property,
not a fairness control; wrong/short/refusal answers looking energy-cheap
must be visible in stop-reason distributions, never hidden.

**Sources to pin (hash-manifested frozen subsets, never "latest split"):**
LMSYS-Chat-1M for chat SHAPE distributions (terms-gated, not for
redistribution — derive synthetic shapes from it); HumanEval/MBPP-style
code prompts (MIT, contaminated — prompt exemplars only, no accuracy
claims); public-domain/government texts + synthetic needle controls for
summarization; GSM8K/MMLU-style items for reasoning shapes (MIT on HF,
contaminated — shape not correctness); synthetic fixed-schema records for
JSON; FLORES-200 for multilingual (CC BY-SA, parallel sentences enable
the semantic-matched leg). Where licenses are uncertain, synthetic wins.

**Concrete recommendation — `jw_mixed_v1` (adopt as the first official
workload expansion).** Amendment 2026-07-08 (C-014): this supersedes the
C-005 fixed-budget-full-first sequencing; the C-005 category/source
discipline otherwise remains intact. Phase 1 is the identification core:
all 6 categories at the common-shape identification stratum, `512/256`
`fixed_budget_exact`, synthetic + realistic where licensing is clean.
Phase 2 is a natural-EOS pilot with >=4 items/category on reasoning, JSON,
chat, and multilingual. Phase 3 is the full category panels, gated on
above-floor structure from Phases 1-2. The original full panel remains the
expansion target after the gate: 6 categories x 8 items = 48 items per
target/model/quant, n=5, categories interleaved round-robin, with the
C-005 category shapes (chat 512/256; code 4x512/256 + 4x1024/512;
summarization 4096/256; reasoning 512/512; JSON extraction 1024/128;
multilingual FLORES 8 languages semantic-matched then token-matched
512/256; ~240 bundles = 3-8 hours per target/model/quant at observed
throughput) unless the Phase 1/2 gate amends them. Harness needs (all additive): `workload_profile.category` +
`source_manifest` + sha256 + per-item `output_policy` fields; category as
a campaign-matrix axis alongside shape (never instead of it); per-item
stop reason/emitted-token/response hash in outputs; reuse P2-010a item
windows + identifiability flags; aggregation waits on P2-011. Out of
scope stays out: no accuracy evals, no judges, no retries — correctness
only as quarantined annotation. Category claims follow AP-4 in
`docs/contracts/analysis_plans.md`.
Amendment 2026-07-08 (D-046 and deferred-binding B6 disposition):
`jw.multiling` synthetic is phase-1 control material, not a C5-W.4 FLORES
replacement; the FLORES 6-vs-8 language count and token-matched
substitution decision are deferred to the FLORES/source session.

**Questions it unlocks (Tier 1):**

- **C5-W.1 Does category explain energy beyond token counts?** Paired
  synthetic controls vs realistic exemplars at identical shape; either a
  category effect or the Token-Shape Sufficiency Null — both reportable.
  Threat: small deltas need the detection floor first (examiner #2). The
  reportable comparison is AP-4 in `docs/contracts/analysis_plans.md`,
  using the common-shape stratum and the predeclared equivalence margin
  from C-014. Who cares: benchmark authors, app engineers budgeting
  features.
- **C5-W.2 Does thinking-token inflation dominate reasoning-model request
  energy?** Fixed-budget vs natural-EOS on the reasoning flagship;
  measures the energy price of "thinking" as output-length inflation.
  Who cares: reasoning-model teams, agent builders choosing modes.
- **C5-W.3 Is category energy-ranking stable across models and quants?**
  The workload-axis analogue of Q5; do code/long-context/reasoning flip
  the ordering? Who cares: procurement, model-selection tooling.
- **C5-W.4 Tokenizer fertility as an energy tax.** Semantic-matched vs
  token-matched multilingual pairs isolate joules attributable to
  tokenizer choice per script. Who cares: multilingual deployment,
  tokenizer designers.


## TIER 2 — unlocked by already-planned hardware gates

Gates by name: P1-006 device access (owned RTX 3050; Jetson Orin Nano),
the 3080 Ti borrow window (Phase 3 interconnect sweep only), P1-003 wall

exec
/bin/zsh -lc "sed -n '826,1160p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
meter decision (R-007), P1-004 network topology (1GbE / 2.5GbE / optional
10GbE).

- **C5-2.1 Quantization decomposition, cross-stack.** C5-1.12 extended
  to llama.cpp-CUDA/vLLM on the 3050: is the time-vs-watts split of
  quantization benefit hardware-dependent? Gate: P1-006. Threat:
  nvidia-smi board boundary ≠ SoC boundary — within-target decomposition
  first, cross-target only boundary-labeled. Who cares: quantization and
  runtime teams.

- **C5-2.2 Batch size and the prefill/decode energy split.** Does
  static batching reshape gross energy/request and the phase split under
  an interactive latency bound? Measure: B in {1,2,4,8,16}, group gross
  energy and gross joules/request within the named target/telemetry
  boundary, latency distribution, and structured memory-fit failures.
  The Mac leg is MINTED (2026-07-16: AXI-SB verdict `supported` on pinned
  mlx-lm 0.31.3, lead-run B∈{2,4} live probes with full per-request
  observability — `docs/specs/axi/sb_static_batch_verdict.md`); execution
  still requires the follow-on batch adapter row, P2-015 floors, and its own
  scheduled quiet-Mac block. The serving-style leg remains gated on P1-006.
  Continuous batching is a post-capstone extension (D-070).
  Who cares: serving researchers, scheduler developers.

- **C5-2.3 Predicted-vs-measured KV economics.** Does the analytic
  kv-size model predict serialized cache size, transfer energy, and
  deserialize energy? Measure: transfer joules/GiB both ends over
  payload ladder 16 MiB-2 GiB per link; deserialize windows; predicted
  vs actual deltas calibrate the model. Gates: P1-004 links + any second
  node (P1-006). Methodology: both-end sampling, clock-offset bounds
  flagged; this is the instrument's designed home turf. Who cares:
  disaggregated-inference researchers, KV-cache system builders.

- **C5-2.4 KV-cache quantization end-to-end.** Does q8_0 cache save
  energy after serialize/deserialize overhead, or only bytes? Gates:
  P1-006 + P1-004 (llama.cpp cache portability spike verdict). Who
  cares: llama.cpp maintainers, KV-compression researchers.

- **C5-2.5 Speculative decoding joules per ACCEPTED token (promotes
  banked item).** With/without draft model at output equivalence.
  Measure: total joules, acceptance rate, joules/accepted-token, n≥5.
  Gate: runtime support (MLX or 3050 stack). Methodology: the
  accepted-token denominator is the trap the harness's token accounting
  defuses. Who cares: speculative-decoding researchers, runtime teams.

  **2026-07-17 DSpark/DFlash candidate riders (D-075).** These remain
  riders on C5-2.5, not four independent theses; every effect is floor-gated
  and `C-023-OUTPUT-IDENTITY` is binding. Evidence for all four:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

  - **C5-2.5a — cross-method contrast.** Status: **candidate (deferred
    rider)**; earliest phase: **NS**. At matched target model, quantization,
    prompt roster, and output equivalence, do a fixed-K block-diffusion
    drafter (DFlash) and a variable-K confidence-scheduled drafter (DSpark)
    differ in gross request energy and gross J/committed-output-token on the
    same MLX stack? Ceiling: **L2**. Forbidden upgrade: **No cross-method
    efficiency generalization beyond the measured target/runtime/tokenizer
    pair; accepted-draft J/token stays a mechanism diagnostic, never the
    on/off efficiency denominator (token_normalization.md D-037 rider).** It
    stays out of the committed standalone set until a prospective
    cross-mechanism design is affordable.

  - **C5-2.5b — proposal-work secondary.** Status: **candidate**; earliest
    phase: **PF**. Is proposal length an energy knob: holding drafter and
    target fixed, does gross J/committed-output-token vary systematically
    with realized mean proposed-K (DFlash block-size sweep 8/16 vs DSpark's
    dynamic schedule), i.e. does per-round proposed work enter the Q4
    coefficients? Ceiling: **L2**. Forbidden upgrade: **No claim that
    K-scheduling saves energy in general; result scoped to one
    runtime/target/boundary, and realized per-round tokens_proposed must be
    runtime-observed, never inferred from the configured cap.**

  - **C5-2.5c — primary Q4 break-even rider.** Status: **candidate**;
    earliest phase: **PF**. Drafter-overhead economics: at what aggregate
    acceptance rate does spec-on gross energy break even with spec-off for
    each drafter class (block-diffusion vs semi-autoregressive vs native MTP
    if a supported runtime lands), at matched output? Ceiling: **L2**.
    Forbidden upgrade: **No serving-system or cross-hardware generalization
    from one pair; the MTP arm is contingent on an AXI-SC supported verdict
    and is a separate frozen family (FAM-AXI-SPEC-NATIVE-MTP), never pooled
    with draft_model arms.**

  - **C5-2.5d — mandatory contamination control.** Status: **candidate**;
    earliest phase: **PF**. Hybrid-lookup contamination bound: how much does
    mlx-dspark's drafter-free n-gram lookup path (on by default) shift
    measured gross energy and acceptance accounting vs `--no-lookup-drafts`,
    quantified as an attribution-contamination diagnostic? Ceiling: **L2
    (diagnostic/methods row)**. Forbidden upgrade: **No mechanism-yield or
    efficiency claim from mixed-origin rounds; the row exists to justify the
    mode pin, not to rank lookup vs drafter.**

- **C5-2.6 Energy-optimal request coalescing under a latency bound.**
  Replayed arrival traces × coalescing windows → joules/request vs
  p95 latency Pareto. Gate: P1-006. Who cares: edge gateways, serving
  schedulers.

- **C5-2.7 Device perf/W rankings with runtime held constant (extends
  Q5, doesn't duplicate it).** Same llama.cpp build/model/quant across
  M3 Max / 3050 / Orin (+3080 Ti in window): do rankings survive
  workload changes when the RUNTIME variable is removed? Gates: P1-006,
  borrow window. Threat: boundary heterogeneity — ranking claims are
  per-boundary until wall-calibrated (C5-2.9). Who cares: hardware
  reviewers, edge procurement.

  **2026-07-17 kernel-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **NV**. When the runtime is held constant (same llama.cpp
  build/model/quant) across M3 Max Metal and 3080 Ti CUDA, does recorded
  kernel-layer identity (attention kernel, BLAS backend, graph mode) explain
  residual energy structure beyond device? Ceiling: **L2 within each
  measurement boundary; per-boundary only until wall-calibrated (C5-2.9)**.
  Forbidden upgrade: **no cross-vendor kernel-API efficiency ranking; no
  cross-device winner across heterogeneous boundaries**. Evidence:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.8 Placement-policy optimality from Q4 coefficients.** Can
  fitted fixed+marginal coefficients + measured transfer costs choose
  the energy-optimal prefill/decode placement, validated against
  measured splits? Gates: full Phase 3 set (P1-006, P1-004, borrow
  window). Methodology: modeled-vs-measured labeled; composite bundles.
  Who cares: disaggregated-serving and placement-policy researchers.

- **C5-2.9 Local-vs-datacenter crossover economics (survivor of the
  carbon-label kill).** When is a local request energy-cheaper than
  shipping it out — full-system watts, transfer included, datacenter
  side as DOCUMENTED published-figure assumptions, never measured-
  equivalent? Gates: P1-003 wall meter (+P1-004 for transfer leg).
  Methodology: the wall meter is what makes the local side full-system
  honest; boundary-directional bias (examiner #11) is why SoC rails
  alone can't carry this. Who cares: sustainability-of-ML community,
  enterprise local-vs-cloud deciders.

- **C5-2.10 Boundary-directional bias quantification (elevates Q6).**
  Not just "does the boundary change conclusions" but WHICH comparisons
  flip: memory-heavy vs compute-heavy conditions should diverge
  rail-vs-wall differently. Gate: P1-003. Methodology: pairs with
  C5-1.2/C5-2.3 threat notes; turns their caveat into a measured
  correction. Who cares: every downstream consumer of cross-target
  numbers; measurement-methodology reviewers.

- **C5-2.11 On-device quantized-KV energy.** Status: **candidate**;
  earliest phase: **PF**. Does quantized KV cache (`kv_bits` 8/4, mlx-lm)
  reduce gross request energy for long-context decode on-device, or only
  memory footprint? Ceiling: **L2, per-boundary, MLX-scoped; un-gated variant
  of C5-2.4 (no transfer leg, runnable on the D-073 fleet now)**. Forbidden
  upgrade: **No byte-saving-equals-energy-saving claim (inherits C5-2.4's
  ban); no cross-runtime generalization from MLX alone; no quality-neutrality
  claim without C-023-style output-equivalence evidence**. Attachments:
  C5-2.4, C5-1.12, and C-023-QUALITY-EQUIV-QUANT. Evidence: [2026-07-17
  extension-axis evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.12 Bounded-window KV marginal-slope rider.** Status:
  **candidate**; earliest phase: **PF**. Does a bounded evicting window
  (`RotatingKVCache` via `max_kv_size`) flatten the marginal J/token slope
  over long generations versus an unbounded step-growing `KVCache`? Ceiling:
  **L2 in chunked windows only (RQ-KV-GROWTH discipline: token cadence
  outruns power sampling)**. Forbidden upgrade: **No per-token joule claims
  below the cadence/sampling floor; no output-equivalence assumption —
  eviction changes generations, so contrasts are work-matched, never
  output-matched**. This is an amendment under C5-1.2/RQ-KV-GROWTH, not an
  independent thesis. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.13 Serialized prompt-cache crossover rider.** Status:
  **candidate**; earliest phase: **PF**. Is save+load+replay of a serialized
  prompt cache energy-cheaper than re-prefill at prompt length N on the same
  machine, and where is the crossover? Ceiling: **L2 same-machine,
  same-stack (promotes answered-L1 RQ-MLX-KV-REPLAY to an energy claim)**.
  Forbidden upgrade: **No cross-machine or cross-stack portability claim
  (RQ-MLX-KV-REPLAY's existing ban); no generalization beyond the measured
  prompt-length ladder**. This is an amendment under RQ-CACHE-PREFIX and
  RQ-MLX-KV-REPLAY, not an independent thesis. Evidence: [2026-07-17
  extension-axis evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.14 Q4 cache-policy coefficient rider.** Status: **candidate**;
  earliest phase: **PF**. Do KV-cache-policy contrasts move the fitted Q4
  coefficients in the predicted direction (marginal per-token term down
  under quantized KV, fixed term unchanged)? Ceiling: **L2; L3 only through
  Q4/AP-1's existing holdout machinery (D-070 clause 5)**. The candidate
  rider itself remains capped at L2. Forbidden upgrade: **No new-thesis
  framing — this is a Q4 stress test, not a KV-energy model; no
  coefficient-direction claim below P2-015 detection floors**. Evidence:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

## TIER 3 — requiring new acquisitions (hardware class + rough cost tier)

- **C5-3.1 Machine-to-machine variance / generalizability floor.** A
  second M-series unit (used M1/M2/M4, ~$500-1500) answers the
  examiner's sharpest structural attack: which Tier-1 findings replicate
  on a second box, and what is unit-to-unit variance relative to the
  detection floor? Also unlocks chassis-thermal comparisons (Air vs Pro
  fanless/fanned envelopes). This is the cheapest purchase that converts
  "on this M3 Max" claims into population claims.

- **C5-3.2 Battery-path energy and modeled-rail validation.** A USB-C PD
  power analyzer (~$100-300) measures DC input on battery-excluded runs
  and cross-checks powermetrics' modeled rails at a second physical
  boundary — a cheap partial answer to the modeled-vs-measured attack,
  complementary to the AC wall meter.

- **C5-3.3 Cross-ISA NPU/SoC comparison.** AMD Ryzen-AI mini-PC and/or
  Snapdragon-X laptop (~$800-2000 each): do the dark-silicon and
  active-param-scaling structures hold beyond Apple's stack? Requires
  one new telemetry adapter per platform (the adapter contract is the
  deliverable that makes this tractable).

  **2026-07-17 backend-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **PC**. Record kernel/backend build provenance
  (CUDA/Metal/HIP target, kernel library ids) in all bundles now so a
  post-capstone AMD/ROCm replication leg is comparable without re-running the
  NVIDIA/Mac corpus. Candidate-rider ceiling: **L1 feasibility**; the parent
  row's separate L4 replication posture is not an intake upgrade. Forbidden
  upgrade: **no NVIDIA-vs-AMD efficiency claim from single
  units or heterogeneous boundaries; no cross-ISA claim before a
  platform-specific adapter study**. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-3.4 Phone-class edge inference.** One flagship phone
  (~$800-1200) + llama.cpp/MLX-swift: the actual battery-constrained
  edge story. Honest note: telemetry access on phones is the hard part;
  a feasibility verdict (possibly `unsupported`) is itself the
  publishable first result, exactly like Hailo.

- **C5-3.5 Cross-lab replication (zero hardware, the credibility
  acquisition).** A second lab runs the frozen suite from published
  bundles + configs. Gates every public-facing application (leaderboard,
  standard, audit service); costs coordination, not money.

## Unexpected-applications shortlist (beyond papers)

Ranked by usefulness × lowest extra work; every public-facing one carries
the internal-first ladder from the examiner round.

1. **Prompt/template energy profiler** — product engineers measure the
   joule cost of system-prompt/RAG-template variants; ~3-8 person-days
   (prompt-matrix configs + diff report); rides per-request joules +
   phase attribution. Available now.
2. **Attach-a-bundle power-bug repro** — runtime maintainers receive
   "model got slow/hot" reports as reproducible bundles; ~5-10 days
   (issue template + doc); rides bundle completeness. Available now;
   mundane and high-leverage.
3. **CI energy-regression gates** for MLX/llama.cpp — nightly pinned-host
   run fails on mJ/token regressions; ~5-15 days; rides strict
   validation + config hashing. PRECONDITIONS (examiner): measured
   detection floor as the threshold unit, env snapshots (P2-009),
   baseline-refresh policy across OS updates.
4. **Vendor/press claim audit** — "efficient" claims answered with
   boundary-named measured bundles; ~5-10 days. Defensible as "on this
   boundary, this workload"; overclaims if framed as absolute device
   energy without wall calibration.
5. **Practitioner energy model cards / leaderboard** — joules/token with
   uncertainty next to quality scores; ~5-10 days internal. Ladder:
   internal table → published methodology → cross-lab public table
   (C5-3.5); public version is KILLED until then.
6. **OS/driver/runtime update forensics** — before/after bundles detect
   power-behavior regressions from macOS/MLX updates (DVFS residency
   makes it mechanistic); ~5-15 days; stronger with landed P2-009 rich telemetry.
7. **Teaching instrument** — a measurement-methodology lab course (idle
   subtraction, boundaries, uncertainty, negative results) with bundles
   as graded artifacts; ~5-12 days.
8. **Bundle contract as a standards contribution** — the run-bundle
   layout + boundary table + strict validator packaged as a proposed
   artifact format for edge-LLM energy (MLPerf-Power-adjacent); ~15-30
   days. Export the methodology; do not claim to BE the standard.

Deferred/killed applications: carbon LABELS (needs wall meter + grid
assumptions; see C5-2.9 for the surviving question), battery-runtime
estimates without system-level calibration, local-vs-cloud ROUTING as a
product (cloud side unmeasurable today).

exec
/bin/zsh -lc 'rg -n "linearity|micro.delta|micro_delta|additivity|long.hold|Q4|q4_l3|shape_grid|slope" docs configs results CLAIMS_STATUS.md | head -240' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
rg: results: No such file or directory (os error 2)
CLAIMS_STATUS.md:112:| **C1 — linearity** | `linearity_ramp` | **40/40** (window A) | DEAD for claims (window A permanent FAIL); re-collect (window C/D); data usable as design input (micro_delta slope) + corroboration diagnostics only |
CLAIMS_STATUS.md:114:| **C3 — micro-delta** | `micro_delta` | not collected | Plan is draft-pending-slope by design; slope fit may consume window A ramp as DESIGN input (not a claim) |
CLAIMS_STATUS.md:115:| **C4 — additivity** | `additivity_shapes` | 23/24 single-root collected in window B — **returned to uncollected-for-claim state (D-113)**; 21/24 window-A corroborating remain labelled non-claim diagnostics | Re-collect C4 fresh (window C/D per the frozen plan). F7 ANSWERED by D-113: whole-window voiding affirmed as current semantics; no cell-scoped salvage |
CLAIMS_STATUS.md:116:| **C5 — long holds** | `long_holds` | not collected → window C | — |
CLAIMS_STATUS.md:162:- **Window A C1 linearity figures in any claim context** — the corpus
docs/strategy/2026-08-06-impressiveness-roadmap.md:110:That is the critical path. A broad paper with incomplete C1–C6 evidence will look less serious than a narrower paper that cleanly demonstrates linearity, null response, empirical floor behavior, additivity, drift/settling, and between-session stability.
docs/strategy/2026-08-06-impressiveness-roadmap.md:137:- L2 ceiling for named studies unless Q4’s independent L3 machinery applies.
docs/strategy/2026-08-06-impressiveness-roadmap.md:159:| **4** | **Designed workload-shape matrix with held-out prediction—Q4/L3** | A predictive fixed-plus-marginal model validated on held-out cells is substantially more serious than “we ran more prompts.” It can earn L3 rather than another collection of L1/L2 points. | **6–10 weeks; approximately 2–3 nights.** | P2-006 baseline sizing, AP-1, 4×3 grid, predeclared holdouts, residual/sensitivity analysis, floor audit. Risk: the simple model may fail its holdouts—which must be reported honestly. | Fund the full designed matrix or omit the predictive claim; do not replace it with opportunistic workload breadth. |
docs/strategy/2026-08-06-impressiveness-roadmap.md:160:| **5** | **Quality-gated BF16/Q8/Q4 quantization ladder** | A clean same-family ladder with error bars and output-divergence reporting can adjudicate the reported q4-vs-q8 anomaly. Strong workshop demonstration; moderate novelty. | **4–8 weeks; 1–2 nights.** Quality screening can run outside quiet windows. | One frozen source revision, reproducible conversions, 256-item quality gate, 32-item energy subset, stack-specific floors. Risk: quality may not be equivalent or quantization may alter cadence beyond existing calibration support. | Choose the model family before conversion; accept a quality/energy trade-off result if equivalence fails. |
docs/strategy/2026-08-06-impressiveness-roadmap.md:162:| **7** | **One mechanism-level study, conditional on a hard feasibility gate** | **Highest scientific ceiling.** A controlled batch-1 speculative-decode or MTP energy result could be genuinely novel; KDA/context slope or MoE routing is also interesting if attribution is identifiable. | **2–3-week desk feasibility gate; if passed, another 6–12 weeks and roughly 2 nights.** | New/forked runtime instrumentation, direct proposal/acceptance events, output identity/equivalence, mechanism-specific AP and floors. MTP currently cannot execute; KDA is confounded; MoE routing visibility is uncertain. | Pick exactly one mechanism and a kill date. Recommended first choice: external-draft speculative decode, because it offers the cleanest same-target on/off contrast if observability can be added. |
docs/strategy/2026-08-06-impressiveness-roadmap.md:175:| **ICPE full research track** | Plausible over months, but not yet supported by the current evidence. ICPE 2027 lists research and artifact tracks but their details and dates remain TBA. The 2026 research track used 10 pages and judged novelty, technical quality, and scientific soundness; 2026’s reported full-paper acceptance rate was 28%. [ICPE 2027](https://icpe2027.spec.org/tracks-and-submissions/research-paper-track/), [2026 research criteria](https://icpe2026.spec.org/tracks-and-submissions/research-paper-track/), [acceptance history](https://icpe.spec.org/past-conferences/) | C1–C8, cross-day stability, artifact-ready release, and at least one deeper contribution: held-out Q4 prediction, second-unit replication, or a successful mechanism study. Split is not required. |
docs/strategy/2026-08-06-impressiveness-roadmap.md:187:7. **Choose one expansion:** Q4 held-out prediction for the strongest ICPE case; quantization for the safest workshop enhancement; or mechanism work only if its short feasibility gate passes.
docs/strategy/2026-08-06-impressiveness-roadmap.md:197:2. **Physical measurement budget.** Recommended commitment: **5–7 Ed-present sessions**—C, D, one contingency/stability repeat, wall pilot/confirmation, and one extension. An ICPE-full attempt with Q4 and second-unit work likely needs **8–10 total sessions** across operators.
docs/strategy/2026-08-06-impressiveness-roadmap.md:201:4. **Mechanism ambition.** Do not ask simply “unfence D-041.” Decide whether to retain D-070’s all-five-axis commitment or narrow it to one paper-worthy study. Recommended rule: two-to-three-week feasibility gate for speculative-decode observability; if it fails, return immediately to Q4/quantization.
docs/reviews/2026-07-10-hardening-adjudication.md:42:| Wall/PD bridge design | Already designed under D-054, [detection_floor.md](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md), Q6/C5-2.10, D-018, and registry Q6/C5-3.2. It already specifies paired deltas, slope/intercept bridge fitting, residual gates, synchronization, and boundary-specific claim ceilings. | P1-003 meter decision, external-meter importer/CLI, and live campaign remain. Do not create another design document. |
docs/reviews/2026-07-10-hardening-adjudication.md:51:| Research agenda | Nearly every §11 question already has a canonical equivalent in the D-055 registry: HET-PD→Q1/Q2/Q3; MODEL→Q4/C5-2.8; QNT→C5-1.12/C5-2.1; XFER→Q2/C5-2.3; KVQ→C5-2.4; SPEC→C5-2.5; CACHE→RQ-CACHE-PREFIX; GEN→C5-3.1/C5-3.5. | No new registry rows are justified now. |
docs/reviews/2026-07-10-hardening-adjudication.md:85:| 9 | **P2-048 — External-meter importer and bridge CLI** | `[AGENT]`, P2 conditional on P1-003 | Implement the already-designed Q6 artifact/import format and `boundary-calibrate`; bind meter metadata, synchronization, paired windows, slope/intercept, residuals, held-out gate, floor identity, and refusal reasons. The design itself should not be duplicated. |
docs/reviews/2026-07-09-c027-whole-project-review.md:221:- **Q4 Stop line:** direction adopted, gates amended per counterreview:
docs/axi-handoff.md:59:  view, never used to rank devices. Q4's fixed term (E = fixed +
docs/axi-handoff.md:68:  energy-proportionality problem and extends Q4 falsifiably
docs/axi-handoff.md:86:stress tests of the single Q4 thesis, not five new theses. The registry
docs/axi-handoff.md:122:idle-subtracted as labeled secondary within-device view; Q4 fixed term
docs/axi-handoff.md:231:  breakpoint handling; framed as a Q4 coefficient stress test.
docs/axi-handoff.md:269:  through Q4/AP-1's existing holdout machinery); ceilings move only via
docs/project_critique_review.html:500:          <p><strong>Q4, the fixed-vs-marginal energy model</strong>, is the best centerpiece. A model such as <code>E = fixed + prefill(prompt_tokens) + decode(output_tokens)</code> is valuable even if live split inference never works. It gives the project a practical contribution for app builders and creates a bridge from benchmarking to energy budgeting.</p>
docs/project_critique_review.html:812:        <strong>Example downgrade:</strong> "Energy per token scales almost exactly with active parameters" should become "In two strict-valid Mac/MLX/powermetrics points, energy per output token was consistent with active-parameter-driven scaling; this is a hypothesis pending bridge models and a fitted Q4 matrix."
docs/project_critique_review.html:819:        <li><strong>After 2M:</strong> fit Q4 only inside one boundary, with raw points and interval separation rules.</li>
docs/project_critique_review.html:859:        <li><strong>Fit Q4 narrowly first.</strong> One stack, one model family where possible, prompt/output ladders, n >= 5, clear uncertainty intervals.</li>
docs/process/model_allocation_ledger.md:158:| L-015 | 2026-07-14/15 | C-034 | ULTRA comparison audit (intended, pre-declared) | Sol | ultra | independent audit (comparison arm) | 2 blockers / 20 findings, triaged per Ed's substance-over-ceremony ruling (7 fixed, 4 bench, 5 queued, rest dispositioned) | 2 blockers | **comparison verdict never recorded** — the entry states the audit ran and what it found, but not whether ultra beat xhigh; see §5 Q4 | `docs/council_log.md` index row C-034 (l.1506) |
docs/process/model_allocation_ledger.md:275:**Q4 — What did the ULTRA comparison audit actually show?** L-015 records
docs/reviews/2026-07-13-comprehensive-audit/packets/pa2-out.md:124:      "TASK_QUEUE.md §Current Queue row P2-019 and generated row Q4",
docs/critique_text_extract.txt:97:Q4, the fixed-vs-marginal energy model
docs/critique_text_extract.txt:572: "Energy per token scales almost exactly with active parameters" should become "In two strict-valid Mac/MLX/powermetrics points, energy per output token was consistent with active-parameter-driven scaling; this is a hypothesis pending bridge models and a fitted Q4 matrix."
docs/critique_text_extract.txt:585: fit Q4 only inside one boundary, with raw points and interval separation rules.
docs/critique_text_extract.txt:652:Fit Q4 narrowly first.
docs/campaign_packs/split_suite_q1_q2_q3.md:376:- AP-1 Q4 coefficients and monolithic references for the same model/runtime
docs/process/state_kernel.json:2026:      "goal": "q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6).",
docs/campaign_packs/README.md:27:| Placement-policy optimality from Q4 coefficients | C5-2.8 | `docs/campaign_packs/c5_2_8_placement_optimality.md` |
docs/advisor_briefs/2026-07-17-window-a-brief.html:982:            <p>Planned as a Q4 stress test under exact artifact, quality-equivalence, and floor gates—not as “fewer bytes means less energy.”</p>
docs/reviews/2026-07-09-scientific-rigor-review.md:167:Strongest five: Q4 fixed+marginal model (AP-1, holdouts — the most
docs/reviews/2026-07-09-scientific-rigor-review.md:355:| Q4 Fixed + marginal model | Yes under AP-1 | Yes via holdouts | Yes after Window B grid | Yes, L3 | Pre-hardware prep; data pending | One of the strongest: predictive, bounded, and advisor-defensible. |
docs/reviews/2026-07-09-scientific-rigor-review.md:374:| Session-shape energy | Yes under Q4 coefficients | Yes | Suite sessions sufficient | L2/L3 depending holdout | Substrate | Strong follow-on to Q4: tests whether coefficients compose in realistic sessions. |
docs/reviews/2026-07-09-scientific-rigor-review.md:385:| Workload shape changes request energy | Yes under AP-2 | Yes | Yes after 2M | L2 | Current Mac | Good descriptive result; distinct from Q4 because it does not predict holdouts. |
docs/reviews/2026-07-09-scientific-rigor-review.md:404:| C5-2.8 Placement optimality | Yes | Yes | Needs Q4 + transfer + measured splits | L2/L3 | Hardware-gated | Excellent capstone extension if Phase 3 lands. |
docs/reviews/2026-07-09-scientific-rigor-review.md:414:1. **Q4 fixed + marginal model**: bounded variables, holdout prediction, AP-1, and a clear L3 ceiling. This is the most advisor-defensible “science” in the bank.
docs/reviews/2026-07-09-scientific-rigor-review.md:446:- C5-2.8 placement optimality: Q4 coefficient input contract plus measured-split validation cells.
docs/reviews/2026-07-09-scientific-rigor-review.md:509:| Science vs plumbing | Partial: Q4-Q6 and claim tracks exist. | Freeze one headline claim and 2 fallback claims with allowed claim level. |
docs/reviews/c027/lens-rigor.md:106:**Neutralizer:** Call it “held-out in-grid prediction” or “interaction/additivity validation.” A genuine extrapolation claim needs an out-of-range condition and a defensible parametric functional form.
docs/phase_4/phase_4_plan.md:128:| F9 | Q4 coefficient fit: fixed+prompt+decode categorical effects, holdout prediction error, and residuals from AP-1 (C-014) | Q4 |
docs/campaign_packs/c5_2_8_placement_optimality.md:1:# C5-2.8 Pack: Placement-Policy Optimality From Q4 Coefficients
docs/campaign_packs/c5_2_8_placement_optimality.md:5:predictions until AP-1/Q4 coefficients and measured transfer terms exist.
docs/campaign_packs/c5_2_8_placement_optimality.md:11:- Formula uses AP-1/Q4 fixed, prompt, and decode coefficients plus measured
docs/campaign_packs/c5_2_8_placement_optimality.md:16:- If Q4 holdouts fail, downgrade to exploratory placement accounting.
docs/campaign_packs/c5_2_8_placement_optimality.md:22:| Plan ID / RQ consumer | DRAFT-AP-C5-2.8 / C5-2.8 placement-policy optimality from Q4 coefficients. DRAFT until registry freeze. |
docs/campaign_packs/c5_2_8_placement_optimality.md:30:| Inclusion/exclusion + quality-flag waiver rules | Include only strict-valid source bundles, Q4 coefficient artifact, transfer payload manifests, measured split validation bundles, stack-identity tables, and prediction-freeze artifact with timestamp/hash before validation execution. D-014 quality waivers must be named before registry freeze. |
docs/campaign_packs/c5_2_8_placement_optimality.md:34:| Denominator provenance requirement | Q4 coefficient artifact hash, AP-1 holdout verdict, runtime-observed output tokens, stop reason, model artifact hash, quantization, tokenizer identity, sampler/output policy, serialized payload bytes, payload SHA-256, link throughput, serialize/transfer/deserialize markers, and measured split validation bundle hashes. |
docs/campaign_packs/c5_2_8_placement_optimality.md:37:| Disqualifiers + not-resolvable conditions | Missing AP-1/Q4 coefficients, failed Q4 holdouts, no prediction-freeze artifact before validation, missing measured split validation cells, missing transfer/deserialize terms, floor row missing for the claim window, non-equivalent output policy, or placement searched after seeing validation results. |
docs/campaign_packs/c5_2_8_placement_optimality.md:43:`<<AP-1.*>>` placeholders are gated by AP-1/Q4, and `<<PHASE3.*>>`
docs/campaign_packs/c5_2_8_placement_optimality.md:108:`source_artifacts_manifest.json` records Q4 coefficient hash, holdout verdict,
docs/campaign_packs/c5_2_8_placement_optimality.md:143:- Caption states whether Q4 holdouts cleared; if not, this is exploratory
docs/campaign_packs/c5_2_8_placement_optimality.md:152:- AP-1/Q4 coefficients from Window B.
docs/campaign_packs/c5_2_8_placement_optimality.md:163:- Do not promote this pack beyond exploratory placement accounting if Q4
docs/campaign_packs/c5_2_8_placement_optimality.md:195:1. Verify AP-1/Q4 coefficients and holdout verdict. If holdouts fail, freeze
docs/reviews/c027/counterreview.md:119:### Q4 — The stop-line direction is right, but its gates are simultaneously too soft and too rigid
docs/site/run_state.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Run State - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html" class="active">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#start-here-for-every-big-run">Start Here For Every Big Run</a> <a href="#historical-stop-card-note">Historical Stop-Card Note</a> <a href="#active-stop-card">ACTIVE_STOP_CARD</a> <a href="#active-global-work-selection-gates">Active Global Work-Selection Gates</a> <a href="#restart-by-machine-state-lane">Restart By Machine-State Lane</a> <a href="#checkpoint-2026-07-18-late-d-077-adversarial-arc-complete-pr-77-open">CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR 77 open</a> <a href="#checkpoint-2026-07-18-claude-script-bridge-runs-in-the-pet-s-app-task">CHECKPOINT 2026-07-18: Claude script bridge runs in the pet&#x27;s app task</a> <a href="#checkpoint-2026-07-17-late-session-env-guard-branch-open-review-pending">CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending</a> <a href="#superseded-stop-card-cp-5">Superseded stop card (CP-5)</a> <a href="#current-project-status">Current Project Status</a> <a href="#session-history-pointers-only-run-reports-own-the-narrative">Session History (pointers only — run reports own the narrative)</a> <a href="#current-verification">Current Verification</a> <a href="#known-workspace-state">Known Workspace State</a> <a href="#historical-next-work-snapshot-superseded-2026-07-15">Historical Next-Work Snapshot (superseded 2026-07-15)</a> <a href="#reference-decisions-and-blockers-non-selection-context">Reference Decisions And Blockers (non-selection context)</a></aside> <div class="doc-wrap doc-source-run-state-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>RUN_STATE.md</code></p> <div class="provenance-plate"><span class="source-chip" title="RUN_STATE.md · commit 1af9f92"><span class="source-file">RUN_STATE.md</span><span class="source-commit">commit 1af9f92</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>JouleWise Run State</h1> <p>Last updated: 2026-07-25. <strong>Main is at <code>c3e2647</code>: PR #79&#39;s D-078 instrument repair merged on 2026-07-22, and PR #85&#39;s ratified SCREEN+BUDGET rules are merged with green CI after the four-round adversarial gauntlet.</strong> The repaired-instrument collection contains 229 strict members across four bracketed windows (a5-a8). Those windows are non-claim-bearing diagnostic, instrument-proving evidence; they do not license a floor or research claim.</p> <p>The merged rules now screen gross and idle-subtracted energy separately, carry a never-zero drift allowance for each family, require a fresh 24-hour drift bound, reject fallback-clock members from floor/claim cells, derive mockness from custody-bound config, and bar terminal mock evidence. NEXT: use one clean <code>[QUIET-MAC]</code> window and follow <code>docs/phase_2/window_runbook.md</code> exactly — mint the bound inside the window, collect the start triplet, midpoint reference, and end triplet, and produce the first claim-grade floors. Then re-verdict a8 and size the Splitwise campaign. The capsule was redeployed from <code>c3e2647</code> as <code>dep_2I04CG6tQ4t0mzY7</code> at 2026-07-25T01:46Z.</p> <p>Prior context (historical, pre-repair; superseded by the sign-off above): PRs #77 and #78 are both MERGED (#78 at b52abf3). The recal windows of 2026-07-18/19 collected 94 + 266 strict-valid bundles under the production environment guard (records: <code>docs/run_reports/2026-07-19-d077-recal-window.md</code>, <code>2026-07-19-recal456-extended-window.md</code>); that corpus is instrument evidence only — the pre-repair floor re-extraction plan is VOID, and P2-015 restarts under the repaired instrument per the roadmap. Ed-side standing: <code>sudo pmset -c displaysleep 10</code>.</p> <p>Prior arc (2026-07-17, SESSION ARC COMPLETE: Window A floors published (222 strict-valid bundles; P2-015 partial pending P2-039 artifact + P2-037 adjudication); advisor brief delivered (docs/advisor_briefs/); Ed DEPLOYED the README-first site + Learn guide (PR #75); exploratory block measured (OLMoE ~229 J / Qwen3-4B ~362.8 J / 122B ~1072 J gross suite, n=3, exploratory-labeled); DSpark/DFlash MLX feasibility CONFIRMED w/ per-round observability; D-075 extension-axis intake folded. Session records: docs/run_reports/2026-07-16-resumption-nohw-batch.md + 2026-07-17-window-a-floors.md.)</p> <h2 id="start-here-for-every-big-run">Start Here For Every Big Run</h2> <p>Before starting substantial work:</p> <ol> <li>Read this file.</li> <li>Read <code>TASK_QUEUE.md</code>.</li> <li>Read <code>AGENT_PLAN.md</code> (phase index) and the active phase&#39;s plan doc under <code>docs/phase_N/</code>; per-item status lives in the phase exit checklist (D-023).</li> <li>Read <code>docs/planning_reflection_protocol.md</code>.</li> <li>Check <code>docs/decision_log.md</code> before re-deciding anything; check <code>docs/risk_register.md</code> if starting a phase or a hardware-dependent task.</li> <li>Check the last 2-3 commits with <code>git log --oneline --decorate -3</code>.</li> <li>Check <code>git status --short --branch</code>.</li> <li>Run <code>python3 -m unittest discover -s tests</code> unless the task is docs-only.</li> <li>Do not commit local deletions or unrelated changes unless the user asks.</li> <li>Heartbeat rule (<code>docs/milestones.md</code>): if &gt;14 days passed with no run report and no recorded break, start with a milestones + risk review.</li> <li>Live MLX gates use the repo venv: <code>.venv/bin/python -m joulewise ...</code> (system python3 lacks mlx → <code>runtime_unavailable</code>).</li> <li>If an <code>ACTIVE_STOP_CARD</code> exists below, it overrides every normal &quot;restart&quot;, &quot;next&quot;, queue, and mission pointer until explicitly cleared.</li> </ol> <p>At the end of substantial work:</p> <ol> <li>Update only hand-authored factual/history sections of this file.</li> <li>Update <code>docs/process/state_kernel.json</code> for live task state and regenerate; do not hand-edit either generated region.</li> <li>Add or update a detailed report in <code>docs/run_reports/</code>.</li> <li>Record tests, commands, and blockers; generated lane heads own next-work selection.</li> <li>Record new decision-log entries and any risk-register status changes.</li> <li>Refresh <code>PROJECT_STATUS.md</code> if advisor-visible state changed.</li> <li>Push green commits promptly (small doc/bookkeeping commits straight to main; multi-commit code series as branch + PR per D-031). Do not accumulate unpushed local state — the remote and the high-level docs (README, PROJECT_STATUS) are the user&#39;s and advisor&#39;s view.</li> <li>Run a docs-consistency sweep before the final bookkeeping commit (delegate to a fast subagent): stale test counts, gate-state contradictions between prose summaries and checklist matrix rows, numbers cited in multiple places (C-002; D-023 extension). After any session that changed front-facing state, refresh <code>docs/site/DRIFT.md</code> (site-drift report) instead of deploying: per D-068 (2026-07-14) NO agent regenerates or deploys the site, ever — automation informs; Ed deploys manually. (Supersedes the C-013 regenerate+redeploy convention.)</li> <li>Call out any dirty working-tree state that should not be accidentally committed.</li> </ol> <h2 id="historical-stop-card-note">Historical Stop-Card Note</h2> <p>This 2026-07-11 clearance note is retained as history only; current stop-card and work-selection state is generated immediately below from the kernel.</p> <!-- BEGIN GENERATED: state-kernel run-state-intake --> <h2 id="active-stop-card">ACTIVE_STOP_CARD</h2> <p>Status: NONE — no stop card is active. Stop-card authority: D-050 / D-063 (<a href="docs/decision_log.md">decision log</a>).</p> <h2 id="active-global-work-selection-gates">Active Global Work-Selection Gates</h2> <p>NONE — no global work-selection gate is active.</p> <h2 id="restart-by-machine-state-lane">Restart By Machine-State Lane</h2> <p>Source of truth for work selection: <a href="docs/process/state_kernel.json">state kernel</a> (updated 2026-07-25). Latest report: <a href="docs/run_reports/2026-07-24-screen-budget-gauntlet.md">SCREEN+BUDGET rules ratified, adversarially verified, and merged via PR #85; prospective quiet-window collection is next</a>.</p> <h3>[ED-EXTERNAL]</h3> <ul> <li>READY — E1 <code>P1-008</code>: Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).</li> </ul> <h3>[QUIET-MAC]</h3> <ul> <li>READY — Q1 <code>P2-015</code>: Collect the first claim-grade Window A floors in one clean prospective quiet window per the claim-window run-book: mint the drift bound in-window, then run the start triplet, midpoint reference, and end triplet before the a8 re-verdict and Splitwise sizing.</li> </ul> <h3>[AGENT]</h3> <ul> <li>READY — A3 <code>FLOOR-BIND-01</code>: Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions.</li> </ul> <!-- END GENERATED: state-kernel run-state-intake --><h2>CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open</h2> <p>The RESUME list from the 2026-07-17 checkpoint is fully executed. The relaunched execution-lens review, fix rounds 1-2, and their delta re-audits had already run earlier on 2026-07-18 (commits <code>1aebf14</code>, <code>6d80039</code>); this session closed the surviving P1 (child accepted any JSON object as the frozen cooldown anchor) plus every finding from four further delta re-audits, as fix rounds 3-8 in commit <code>ad0920b</code>: canonical anchor validator (<code>joulewise/cooldown_anchor.py</code>) enforced fail-closed at parent/CLI/controller boundaries; collision-safe, crash-atomic, flock-serialized rejection-verdict custody (<code>experiments/rejections/</code>); physical-domain baseline validation (the <code>inf</code>-anchor fail-open gate is closed); discriminating process-race regression. Suite green lead-side at every round boundary, final <code>Ran 1746 tests</code>, <code>OK (skipped=12)</code>. Awake-half live probe validation passed on real hardware (zero probe errors); the Ventura screensaver is now disabled on the machine (<code>idleTime = 0</code>). PR #77 carries the gate narrative; merge is Ed&#39;s call. Full record: <code>docs/run_reports/2026-07-18-d077-fix-rounds.md</code>. Tooling: codex-run-v3 xhigh review-genre sessions ended with null final messages 4x (bridge-resume recovered each; personal-tooling defect, recorded in the run report and the global codex-delegation skill field notes, not the repo queue).</p> <h2 id="checkpoint-2026-07-18-claude-script-bridge-runs-in-the-pet-s-app-task">CHECKPOINT 2026-07-18: Claude script bridge runs in the pet&#39;s app task</h2> <p>The actual Claude Code fallback route is <code>scripts/codex-bridge</code>, not the MCP server for recent audited work. The wrapper now sends <code>new</code> and <code>review</code> turns through a dedicated app-owned Codex desktop task when the local host id is configured. This is the same local-conversation state the native pet consumes; the prior observer-only diagnosis was incorrect because the pet never reads <code>~/.codex/claude-spawned/index.jsonl</code>. A live Sol/high smoke appeared in the Codex app as thread <code>019f77a6-3612-7332-9f5e-be9fbde56be5</code>, turn <code>019f77a9-2827-7de1-accf-ac2eda21927e</code>, and returned <code>JOULEWISE_NATIVE_PET_BRIDGE_OK</code> through the script. Adaptive effort remains unchanged: <code>high</code> fallback/default, <code>xhigh</code> only on named hard-task triggers, and <code>ultra</code> only for sessions that must spawn subagents. Full record: <code>docs/run_reports/2026-07-18-claude-codex-pet-observer.md</code>.</p> <p>Committed 2026-07-18 on <code>impl/env-guard-cooldown</code> (after the D-077 packet boundary <code>6d80039</code>) with a lead execution review at the bench: IPC socket ownership/permission checks, PID-checked host-task lock, interrupt-on-terminate, no-network sandbox policy, and one-hop rule all verified in <code>scripts/codex-app-bridge.mjs</code>; real-socket fake-router tests plus observer lifecycle tests included; canonical suite green lead-side (<code>Ran 1722 tests</code>, <code>OK (skipped=12)</code>). The same commit carries the doctor-driven CLAUDE.md trims (global + repo; content deduplicated into <code>.claude/skills/codex/SKILL.md</code>, which is the operating home) and stamp-only <code>docs/site/*.html</code> provenance refresh.</p> <h2 id="checkpoint-2026-07-17-late-session-env-guard-branch-open-review-pending">CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending</h2> <p>Window A floors contamination diagnosed from primary data: macOS Ventura <em>video</em> screensaver on an awake display contaminated 43/50 suite-calibration bundles (~+30% energy, −11% throughput; engage at HID-idle +20 min, dismiss on unlock — pmset assertion log corroborated to the second). The six &quot;low&quot; su-ABBA runs (18:16–18:36 UTC) are the only CLEAN suite runs; comparative suite floors (4.923 J item / 24.62 J suite) are transition artifacts. The professor&#39;s power-source hypothesis is refuted (AC/140 W/100% throughout). Details: memory note + <code>docs/run_reports/2026-07-17-environment-guard.md</code>.</p> <p>Branch <code>impl/env-guard-cooldown</code> (pushed, commit e2813ee) holds the D-077 response: environment-guard preflight (+<code>--arm-quiet-mode</code>), per-run idle admission gate, cooldown v2, unwaivable <code>environment_admission_failed</code> claim barrier, policy sidecars, contract/doc updates. Design consult (Sol xhigh, thread 019f7356-32d3) adjudicated and encoded; implementation by Sol xhigh (thread 019f7362-6627, resumed via codex-bridge after an MCP transport timeout); session-close scope check SCOPE_OK; full suite green lead-side (OK, 12 skips). Lead bench fix included: <code>pmset -g systemstate</code> parser now accepts the live &quot;Capabilities are:&quot; form (was null → fail-closed on real hardware); fixtures pinned to verbatim live output.</p> <p>RESUME (in order):</p> <ol> <li>Relaunch the adversarial review round (was stopped mid-run at checkpoint): fresh read-only Sol xhigh, execution lens, over <code>git diff main...impl/env-guard-cooldown</code> (prompt shape in <code>.codex-bridge/</code> prompt snapshots); lead holds the contract lens (done for cooldown_gate/claim-barrier/anchor hunks).</li> <li>Triage findings → fix rounds (defect-shaped regressions) → DELTA RE-AUDIT.</li> <li>Live-validate flagged probes during next quiet-window prep: <code>pmset -g systemstate</code> display-asleep form + screensaver-engaged probe while a screensaver is actually running (run report flags <code>live_validation_provisional</code>).</li> <li>PR per operation-loop §5 gate shape; then re-run suite ABBA calibration under the new guard ([QUIET-MAC], needs Ed) — floors D-076 figures for suite comparative cells must be recomputed/caveated pending re-run.</li> </ol> <p>Status: <strong>CLEARED 2026-07-11.</strong> Every clearance criterion met: all checkpoint-#4 resume items executed (P2-044 fix+merge #55; P2-037 audit dispositions → two fix rounds + approved NEEDS_SCOPE expansion + delta re-audit → #58; P2-043 #57; P2-045 #56); the four held hardening PRs #50-#53 merged after the cross-stream integration review over the combined tree (38 pre-merge cross-stream failures caught and fixed; 1 review blocker confirmed by refuters → PR #59; SF1 refuted; SF3 → queue row P2-049); DOC-008 kernel refreshed at final head (schema v2, authority field, branch impl/doc008-kernel awaiting PR); bookkeeping arc complete (run report, C-028 council entry with layer catch-rates and ~57-invocation spend record, D-064 ratified incl. manifest v3 + claude-codex-report/v1 + WRITE_SCOPE enforcement; queue reconciled; consistency sweep; site regen+deploy). All clearance-time opens since CLOSED same day: #59 MERGED, DOC-008 MERGED (#60). Remaining queue heads: P2-049/P2-050/TOOL-01.</p> <h2 id="superseded-stop-card-cp-5">Superseded stop card (CP-5)</h2> <p>Status: <strong>CLEARED 2026-07-09</strong> by the CP-5 resume session. Every clearance criterion was met: all three worktree diffs lead-gated (envgate live-gated against the real affine mock bundle) and merged as PRs #23/#24/#25; PR #22 merged after a fresh final-head pass; the methodology synthesis and suite_next specs packet adjudicated (CP-6 in the stream log); all accepted pre-campaign changes landed and merged (PRs #26/#27/#28); both post-merge integration reviews CLEAN; queue rank 0 closed. Full record: <code>docs/run_reports/2026-07-09-cp5-resume.md</code>. No stop card is active.</p> <h2 id="current-project-status">Current Project Status</h2> <p><strong>Collection era open (2026-07-25): main <code>c3e2647</code> contains the merged instrument repair (PR #79) and the merged SCREEN+BUDGET rules (PR #85). The 229-member a5-a8 collection is non-claim-bearing diagnostic, instrument-proving evidence.</strong> The next claim attempt is one clean prospective quiet window per <code>docs/phase_2/window_runbook.md</code>, with an in-window bound mint and start-triplet + midpoint + end-triplet references. A passing window produces the first claim-grade floors; the a8 re-verdict and Splitwise sizing follow. Records: <code>docs/run_reports/2026-07-23-window-a-collection-arc.md</code> and <code>docs/run_reports/2026-07-24-screen-budget-gauntlet.md</code>.</p> <p>The D-078 Phase-0 instrument repair was signed off and merged through PR #79 on 2026-07-22. Registered limitation L1 remains owned by FLOOR-BIND-01; it does not reopen the completed repair. Record: <code>docs/run_reports/2026-07-20-p0-instrument-repair.md</code>. Earlier arcs below are historical.</p> <p><strong>C-028 CLOSED (2026-07-11): the full hardening + analysis-engine arc is on main.</strong> Reducer lattice 0.4.2 (inter-token metric) / 0.4.1 (idle ESS, HAC variance — local r1&#39;s 47x underestimate closed) / 0.4.0 (verdict split + window_evidence_precheck) with frozen legacy arms; the analysis trio complete (P2-042 manifest → P2-041 verdict split → P2-037 contrast/claim engine with unwaivable cleanup claim gating per the two-layer waiver reconciliation); doctor preflight; publication privacy pack (fail-closed inventory); packaging CI; primary-verified related work; load-transition prep (B remains [QUIET-MAC]). Window A&#39;s software gates are ALL satisfied; execution needs a quiet machine + Ed.</p> <p>PRs #41-#60 form the landed C-028 arc, all merged 2026-07-11 (incl. the #59 integration-review fixes and the #60 DOC-008 kernel refresh); none implies live evidence. P0-003 is satisfied by the verified iCloud backup/restore. All NVIDIA/Orin protocol pins remain PROVISIONAL pending P1-006 live evidence.</p> <p><strong>Historical restart snapshot (recorded 2026-07-13; non-operative).</strong> The numbered sequence below is retained as dated handoff narrative, not current work-selection authority. Use the generated region above for selection.</p> <ol> <li>DONE 2026-07-13: #61-#63 merged at delta-audited heads; site deployed live under the cap; XSI-1 CI hardening green on main; bridge landed and lead-verified (8/8 protocol checks; suite 1318 OK).</li> <li>[ED + AGENT] <strong>Comprehensive whole-project audit (declared gate).</strong> The audit method proposal is with Ed; no further feature work, queue pulls, or campaign prep until the audit runs and its findings are adjudicated. Audit focus per Ed: overproduction (excess code/tests), plus everything a serious external review would check.</li> <li>[QUIET-MAC + ED] After the audit: Window A — C-019 production-shaped shakedown and P2-015-SMOKE, then P2-015 floors and P2-006 baselines. Do not run this lane while an agent session is active.</li> <li>[AGENT] Post-audit, outside a quiet window: P2-050 adjudication, SITE-02 follow-ups, P2-027 publication prep. P2-022/P2-023 remain blocked until the 2M corpus exists.</li> </ol> <h2 id="session-history-pointers-only-run-reports-own-the-narrative">Session History (pointers only — run reports own the narrative)</h2> <p>Parenthetical states below are historical at each report&#39;s head; they are not current restart instructions. Current state is the C-028 block above.</p> <ul> <li><p>2026-07-18 Claude Code script bridge + native pet integration: <code>docs/run_reports/2026-07-18-claude-codex-pet-observer.md</code></p> </li> <li><p>2026-07-13 Bridge v1: bridge-protocol/v1 contract + scripts/bridge tooling (PR #64; co-designed with Sol over the bridge itself): <code>docs/run_reports/2026-07-13-bridge-v1.md</code></p> </li> <li><p>2026-07-13 Restart close: #61-#63 merged at delta-audited heads (DRA-001 fixed; XSI-1 CI hardening), site live under cap; audit gate declared: <code>docs/run_reports/2026-07-13-restart-merge-deploy.md</code></p> </li> <li><p>2026-07-12 Claude↔Sol bidirectional bridge (concurrent Ed-directed thread; lead-verified 2026-07-13): <code>docs/run_reports/2026-07-12-claude-sol-bridge.md</code></p> </li> <li><p>2026-07-12 Agent-lane triple: SITE-01/P2-049/P2-028 → PRs #61-#63 at lead-gated heads; delta re-audits owed pre-merge on #62/#63: <code>docs/run_reports/2026-07-12-agent-lane-triple.md</code></p> </li> <li><p>2026-07-11 P2-041 vetted rebuild (uncommitted; lead pathspec review and commit pending): <code>docs/run_reports/2026-07-11-p2041-vetted-rebuild.md</code></p> </li> <li><p>2026-07-10 NV-GATE-2 idle-capture regression debug/fix (uncommitted; localhost re-verification remains lead-gated): <code>docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md</code></p> </li> <li><p>2026-07-10 NV-GATE-2 CODE-NOW implementation (NV-1/NV-3/NV-4/NV-5; live promotion evidence still gated): <code>docs/run_reports/2026-07-10-nvgate2-codenow.md</code></p> </li> <li><p>2026-07-10 NV-GATE-2 accepted-findings fix round (uncommitted; merge metadata recreation and lead gate pending): <code>docs/run_reports/2026-07-10-nvgate2-fix-round.md</code></p> </li> <li><p>2026-07-10 P2-038 accepted-findings fix round (all FIX-1..FIX-6 green; content-merged <code>origin/main</code>, Git merge metadata sandbox-blocked): <code>docs/run_reports/2026-07-10-p2038-fix-round.md</code></p> </li> <li><p>2026-07-10 P2-038 production uncertainty software path (live quiet-machine closure still open): <code>docs/run_reports/2026-07-10-p2038-production-uncertainty.md</code></p> </li> <li><p>2026-07-10 P2-040 reducer-version compatibility review fix (uncommitted): <code>docs/run_reports/2026-07-10-p2040-versioning-fix.md</code></p> </li> <li><p>2026-07-10 P2-040 remainder implementation (uncommitted, pending lead pathspec commit/corpus gate): <code>docs/run_reports/2026-07-10-p2040-remainder.md</code></p> </li> <li><p>2026-07-10 P2-040 / RETRO-001 fix round (committed on c027-int-p2040 after lead review): <code>docs/run_reports/2026-07-10-p2040-fix-round.md</code></p> </li> <li><p>2026-07-09 C-027 whole-project council review (7 gpt-5.6-sol lenses + counterreview + independent final examiner): <code>docs/reviews/2026-07-09-c027-whole-project-review.md</code> (compact run report: <code>docs/run_reports/2026-07-09-c027-council-review.md</code>)</p> </li> <li><p>2026-07-09 Claude Code → Codex MCP bridge hardening and live smoke: <code>docs/run_reports/2026-07-09-claude-codex-mcp-bridge.md</code></p> </li> <li><p>2026-07-12 adaptive Claude Code ↔ Sol/Fable bridge follow-up: <code>docs/run_reports/2026-07-12-claude-sol-bridge.md</code></p> </li> <li><p>2026-07-09 P2-034 broad campaign packs (C-026; PR #39): <code>docs/run_reports/2026-07-09-p2034-broad-packs.md</code></p> </li> <li><p>2026-07-09 spec-fleshing wave 2, ultracode (C-025; PRs #33..#38; D-056..D-059): <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></p> </li> <li><p>2026-07-09 spec-fleshing wave 1 (C-024; PRs #29..#32; D-052..D-055): <code>docs/run_reports/2026-07-09-spec-fleshing-wave1.md</code></p> </li> <li><p>2026-07-09 scientific-rigor review of suite/benchmark/question bank (C-023; review-only; full record in <code>docs/reviews/2026-07-09-scientific-rigor-review.md</code>): <code>docs/run_reports/2026-07-09-scientific-rigor-review.md</code></p> </li> <li><p>2026-07-09 CP-5 resume: pre-campaign review completed, stop card cleared, PRs #22..#28 merged, Window-A GO (C-022): <code>docs/run_reports/2026-07-09-cp5-resume.md</code></p> </li> <li><p>2026-07-09 meta-process stop-card + codex-bridge audit cleanup (D-050; CP-5 preserved untouched): <code>docs/run_reports/2026-07-09-meta-process-stop-card-cleanup.md</code></p> </li> <li><p>2026-07-09 advisor status-site live-depth refresh (D-051/C-021; subordinate to the then-active CP-5 stop card): <code>docs/run_reports/2026-07-09-advisor-status-site.md</code></p> </li> <li><p>2026-07-08 suite build (C-017; adjudication + PRs #17/#18/#20/#19; D-044..D-047): <code>docs/run_reports/2026-07-08-suite-build.md</code></p> </li> <li><p>2026-07-08 suite-science + expansion (C-014/C-015; PRs #14/#15/#16; D-038..D-042): <code>docs/run_reports/2026-07-08-suite-science-expansion.md</code></p> </li> <li><p>2026-07-08 Lakebed deploy (C-013): <code>docs/run_reports/2026-07-08-lakebed-deploy.md</code></p> </li> <li><p>2026-07-08 site observatory (PR #13): <code>docs/run_reports/2026-07-08-site-observatory.md</code></p> </li> <li><p>2026-07-08 critique second-pass + councils+critique (C-011 → PR #12): <code>docs/run_reports/2026-07-08-councils-critique-session.md</code></p> </li> <li><p>2026-07-07/08 resume+merge (C-009 first full run; PRs #8..#11): <code>docs/run_reports/2026-07-07-resume-merge-session.md</code></p> </li> <li><p>Older: see <code>docs/run_reports/</code> (dated files).</p> </li> </ul> <h2 id="current-verification">Current Verification</h2> <ul> <li><strong>Merged main <code>c3e2647</code> / PR #85 (2026-07-25, current):</strong> the SCREEN+BUDGET implementation completed four adversarial audit rounds. Final PR-head CI was green on all five checks (<code>build</code>, <code>installed-wheel</code>, <code>release-chain</code>, <code>test (3.11)</code>, <code>test (3.14)</code>). The final lead-side suite recorded 2141 passed / 21 skipped; its one battery-timing flake passed on rerun. The capsule was redeployed as <code>dep_2I04CG6tQ4t0mzY7</code> at 2026-07-25T01:46Z.</li> <li><strong>D-078 repair sign-off gate (2026-07-22, historical merged gate):</strong> branch <code>impl/p0-instrument-repair</code> code/test head <code>040ca3a</code> (docs-only close-out <code>debc6d2</code> carries it unchanged; merged through PR #79): lead-run <code>pytest -q tests/</code> = <strong>2088 passed, 15 skipped, 1570 subtests, 0 failures</strong>; round-9 focused review surface 357 passed at the same head. Entries below are historical.</li> <li>PR #65 branch <code>impl/bridge-v1.1</code> final head <code>8b96bd4</code>: canonical <code>Ran 1387 tests</code>, <code>OK (skipped=10)</code>, lead-run 2026-07-13 (four lead-side full-suite runs across the fix arc: 1371→1381→1385→1387); CI green on the final head (build, installed-wheel, tests 3.11 + 3.14); <code>scripts/check-codex-mcp.mjs</code> 5/5 PASS with the v1.1 adapter; live session-open/close and reverse-consult probes recorded in <code>docs/run_reports/2026-07-13-bridge-v11.md</code>.</li> <li>Merged main <code>d285989</code> (post #65): canonical <code>Ran 1387 tests</code>, <code>OK (skipped=10)</code>, lead-run 2026-07-13 on the merged head; <code>scripts/check-codex-mcp.mjs</code> all PASS; no active workspace leases.</li> <li>Previous session (post #61-#63 merges + bridge v1 landing, pre-commit head <code>99b8640</code>): canonical <code>Ran 1318 tests in 111.017s</code>, <code>OK (skipped=10)</code>, lead-run 2026-07-13; bridge protocol checker 8/8 PASS; bridge focused tests 4/4 OK. Merged-main backstop at <code>12131b0</code> was <code>Ran 1314 tests</code>, <code>OK (skipped=10)</code>. Live capsule: measured artifact 854,349 B deployed, routes 5/5 HTTP 200, freshness 14/14 current at <code>7d3ea57</code>.</li> <li>Prior head <code>main@194ea39</code> (post #59 + #60 merges): canonical <code>Ran 1258 tests</code>, <code>OK (skipped=10)</code>, lead-run 2026-07-11 fresh-thread intake. PRs #41-#60 are all merged.</li> <li>Prior head <code>main@cc3afc3</code>: canonical <code>Ran 1220 tests</code>, <code>OK (skipped=10)</code>; retained corpus strict gate 6/6; PR #59 pre-merge lead replay was <code>Ran 1224 tests</code>, <code>OK (skipped=12)</code>.</li> <li>Count convention for C-028 records: ordinary worktree replays report <code>skipped=12</code>, final main reports <code>skipped=10</code>, and restricted managed sandboxes may report <code>skipped=13</code> when their environment-gated probe is unavailable. Preserve those environment labels when citing a tail.</li> </ul> <h3>Historical verification archive (exact at the recorded heads)</h3> <ul> <li><p>P2-041 vetted rebuild: baseline canonical <code>Ran 1041 tests in 67.995s</code>, <code>OK (skipped=13)</code>; final focused recipe modules <code>Ran 398 tests in 54.964s</code>, <code>OK (skipped=1)</code>; final canonical <code>Ran 1062 tests in 76.436s</code>, <code>OK (skipped=13)</code>; <code>git diff --check</code> and the dead-private-helper search clean. The retained corpus and localhost socket gates skipped loudly; no live or quiet-Mac validation was claimed. Report: <code>docs/run_reports/2026-07-11-p2041-vetted-rebuild.md</code>.</p> </li> <li><p>PR #49 P2-038 rail-only flake: pre-fix exact-test loop failed 4/100; retained failure emitted <code>cadence_ratio_unrecorded</code> plus <code>interpolation_bound_unrecorded</code> because the final trace sample preceded the stop marker. Archived <code>origin/main</code> reproduced on iteration 6. The fixture-only terminal-sample handshake fix passed the exact test 100/100, focused module <code>Ran 5 tests in 30.480s</code>, <code>OK</code>, and canonical suite <code>Ran 1041 tests in 66.509s</code>, <code>OK (skipped=13)</code>. Report: <code>docs/run_reports/2026-07-10-pr49-p2038-flake-root-cause.md</code>.</p> </li> <li><p>NV-GATE-2 idle-capture regression fix: historic fake-sampler plus new delayed-readiness regression passed together in 3 consecutive fresh processes; canonical suite <code>Ran 1023 tests in 35.164s</code>, <code>OK (skipped=13)</code>; <code>py_compile</code> and <code>git diff --check</code> clean. The exact localhost contract was attempted 3 times but loudly skipped before worker execution because this sandbox denied socket bind; lead socket-capable 3x rerun remains required. Report: <code>docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md</code>.</p> </li> <li><p>NV-GATE-2 accepted-findings fix round: focused node-worker/subprocess, controller, reducer, strict-dispatch, and schema surface <code>Ran 229 tests in 4.995s</code>, <code>OK (skipped=2)</code>; the historic fake-sampler test passed three consecutive fresh-process runs; canonical suite <code>Ran 1022 tests in 34.406s</code>, <code>OK (skipped=13)</code>; targeted <code>py_compile</code> and <code>git diff --check</code> clean. The 0.3.1 dispatch came from <code>origin/impl/p2040-remainder</code> because post-main did not contain it. Report: <code>docs/run_reports/2026-07-10-nvgate2-fix-round.md</code>.</p> </li> <li><p>NV-GATE-2 CODE-NOW worktree: baseline <code>Ran 910 tests in 32.549s</code>, <code>OK (skipped=12)</code>; final canonical suite <code>Ran 922 tests in 33.551s</code>, <code>OK (skipped=13)</code>; focused NV-1/NV-3/NV-4/NV-5 surface <code>Ran 232 tests in 6.085s</code>, <code>OK (skipped=2)</code>; <code>git diff --check</code> and targeted <code>py_compile</code> clean. The added skip is loud and specific: this managed sandbox denied localhost socket bind for NV-5. No live NVIDIA evidence or de-provisionalization was claimed.</p> </li> <li><p>P2-038 accepted-findings fix round: all FIX-1..FIX-6 complete; focused <code>Ran 70 tests in 41.211s</code>, <code>OK</code>; canonical <code>Ran 992 tests in 68.140s</code>, <code>OK (skipped=12)</code>; <code>git diff --check</code> clean. The real-child rail-only path now withholds drift on unknown contamination while gross remains eligible; P2-039&#39;s pending guard validator accepts the emitted block; backup launch failure, extreme-sentinel exclusion, child invocation, and literal phase constants are regression-tested. The absent worktree <code>runs/</code> corpus produced the loud six-bundle acceptance-gate skip. Git merge metadata remains absent because the managed sandbox cannot write the external worktree admin dir; the exact clean three-way <code>origin/main</code> content snapshot is applied.</p> </li> <li><p>P2-040 reducer-version review fix: focused strict/reducer run <code>Ran 84 tests in 1.908s</code>, <code>OK</code>; extended strict/reducer/schema run <code>Ran 104 tests in 1.997s</code>, <code>OK (skipped=1)</code>. Canonical run reached <code>Ran 926 tests in 33.732s</code>, <code>FAILED (failures=1, skipped=12)</code> solely at pre-existing <code>test_telemetry_measure_idle_with_fake_nvidia_smi</code>; isolated reruns reproduce its 0.2-second fake-process timing failure. All reducer/version tests pass; no out-of-scope node-worker change was made.</p> </li> <li><p>P2-040 remainder worktree: pre-change baseline <code>Ran 910 tests in 34.584s</code>, <code>OK (skipped=12)</code>; post-change focused affected modules <code>Ran 256 tests in 3.744s</code>, <code>OK (skipped=1)</code>; canonical <code>Ran 924 tests in 32.812s</code>, <code>OK (skipped=12)</code>; compileall and <code>git diff --check</code> clean. The unchanged six-corpus test produced its required loud skip because <code>runs/</code> is absent; lead 6/6 strict read-only rerun remains the landing gate.</p> </li> <li><p>P2-042 emitter branch <code>impl/p2042</code> (lead-committed base; draft PR #46; targeted-review fix round complete in the worktree, no fix-round commit): FIX-1 fail-closed typed identity/linkage validation, FIX-2 semantic <code>run_id</code> derivation, and FIX-3 raw-byte AP hashing/LF config emission are implemented. Focused manifest/generator/campaign checks: <code>Ran 82 tests in 12.317s, OK</code>; final canonical suite: <code>Ran 989 tests in 33.405s, OK (skipped=12)</code>. Review regressions cover <code>run_id=[]</code>, one malformed identity at each manifest object layer, a fully rehashed coherent rename, and a CRLF AP fixture. Report: <code>docs/run_reports/2026-07-10-p2042-analysis-manifest.md</code>.</p> </li> <li><p>P2-040 reducer-version review fix: focused strict/reducer run <code>Ran 84 tests in 1.908s</code>, <code>OK</code>; extended strict/reducer/schema run <code>Ran 104 tests in 1.997s</code>, <code>OK (skipped=1)</code>. Canonical run reached <code>Ran 926 tests in 33.732s</code>, <code>FAILED (failures=1, skipped=12)</code> solely at pre-existing <code>test_telemetry_measure_idle_with_fake_nvidia_smi</code>; isolated reruns reproduce its 0.2-second fake-process timing failure. All reducer/version tests pass; no out-of-scope node-worker change was made.</p> </li> <li><p>P2-040 remainder worktree: pre-change baseline <code>Ran 910 tests in 34.584s</code>, <code>OK (skipped=12)</code>; post-change focused affected modules <code>Ran 256 tests in 3.744s</code>, <code>OK (skipped=1)</code>; canonical <code>Ran 924 tests in 32.812s</code>, <code>OK (skipped=12)</code>; compileall and <code>git diff --check</code> clean. The unchanged six-corpus test produced its required loud skip because <code>runs/</code> is absent; lead 6/6 strict read-only rerun remains the landing gate.</p> </li> <li><p>P2-040 / RETRO-001 fix-round worktree: canonical suite <code>Ran 908 tests in 32.723s</code>, <code>OK (skipped=11)</code>; focused 211 tests OK; claims lint exit 0 with no errors; <code>git diff --check</code> clean. The absent <code>runs/</code> corpus produced the required loud six-bundle acceptance-gate skip; the lead corpus gate then PASSED (6/6 strict via corpus symlink), plus mock e2e run+strict+reduce and the post-merge full suite (OK, skipped=12).</p> </li> <li><p>Claude Code 2.1.207, Codex CLI 0.144.0, and Node 23.7.0 pass the bidirectional protocol checker. Claude → Sol now uses <code>gpt-5.6-sol</code> with <code>high</code> fallback/default and task-triggered xhigh/ultra escalation; the final guarded <code>/codex</code> smoke returned <code>JOULEWISE_SOL_HIGH_GUARDED_OK</code> (thread <code>019f5a2a-2f4a-7b33-8a6d-b44dcc5a7a26</code>) with source <code>mcp</code>, effort <code>high</code>, read-only sandbox, and <code>on-request</code> approvals. Claude-originated Sol sessions disable the reverse server. Top-level Sol → Fable uses the sole <code>consult_fable</code> MCP tool; live token <code>JOULEWISE_FABLE_MCP_OK</code> on thread <code>019f5a26-d8a6-7993-b48d-8131d88748b9</code>. Focused bridge tests pass 4/4 and <code>gen_state.py --check</code> passes. The current full suite ran 1,317 tests but is not green: one failure + one error in <code>test_gen_state</code> are caused by the concurrent uncommitted state-kernel removal of <code>P2-028</code> while the existing fidelity tests still require that ID; bridge tests are unaffected. Full details: <code>docs/run_reports/2026-07-12-claude-sol-bridge.md</code>.</p> </li> <li><p>Last code-bearing verified head c095c83 (post PR #39; note: 36d5641 later changed <code>scripts/build_site.py</code> on main without a recorded verification — flagged by C-027, covered by RETRO-001): suite <code>OK (skipped=10)</code> and repo lint errors=0, lead-run; pack lint errors=0 warnings=0.</p> </li> <li><p>Prior: main after wave-2 integration fixes: <code>python3 -m unittest discover -s tests</code> → <code>Ran 877 tests, OK (skipped=10)</code>, lead-run; repo lint errors=0; CI green on all six PR heads (#33..#38); combined-ref pre-merge suite check green; live rotated mock campaign strict-valid with order provenance (lead-validated); mock e2e emits uncertainty fields per D-057.</p> </li> <li><p>Prior: series head f75134d (post PRs #29..#32; docs-only) lead-verified; integration-fix commit 7156295 is also docs-only (no test surface): <code>python3 -m unittest discover -s tests</code> → <code>Ran 822 tests, OK (skipped=10)</code>, lead-run; CI green on all four PR heads (py3.11+py3.14); integration reviewer independently re-ran the suite and recomputed the detection-floor campaign arithmetic.</p> </li> <li><p>Prior verification (7666652, post PRs #22..#28): <code>Ran 822 tests, OK (skipped=10)</code>, lead-run.</p> </li> <li><p>Live lead gates this session (real MLX, Qwen2.5-1.5B via <code>.venv</code>, mock telemetry): single-prompt + TWO full 48-item jw_mixed suite runs (pre-merge old manifests, then final merged main with the REGENERATED manifests) — all strict-valid; 48/48 hash-domain closures on the real tokenizer; output token ids, model artifact hash, pinned sampler, and package versions verified present in the bundles.</p> </li> <li><p>Envelope gate live: honest <code>envelope_failed[E1]</code> on the mock affine bundle; refusals for wrong-profile/malformed/mixed inputs; exit codes 0/2/3.</p> </li> <li><p>Bundle pack live: pack → verify(0) → tamper → verify(2).</p> </li> <li><p>Manifest regen: byte-identical double-regen; all realized counts 512; new effective shas 855be4e5 (mixed) / 0316283d (sentinel).</p> </li> <li><p>CI green on every merged head (PR #27&#39;s first merge-ref run failed on a cross-branch fixture interaction; fixed test-side, then green).</p> </li> <li><p>Post-merge integration reviews (both waves): CLEAN, incl. an end-to-end mock campaign → strict → envelope-gate → pack → verify flow and a D-033 legacy-identity spoof probe that failed closed.</p> </li> <li><p><code>validate-bundle --strict</code> green over all 6 real corpus bundles under the new era rule (PR #22 live gate: 6/6 valid, tamper fails named).</p> </li> </ul> <h2 id="known-workspace-state">Known Workspace State</h2> <ul> <li>(2026-07-25) <code>main</code> and <code>origin/main</code> are at <code>c3e2647</code>, the PR #85 merge. PR #79&#39;s repair and PR #85&#39;s SCREEN+BUDGET implementation are both landed; final PR-head CI is green. The current working tree contains intentional lead bookkeeping and run-book/report work that must be preserved; it is not a clean measurement checkout. The next quiet-window operator must start from a separate clean, merged-main measurement checkout per <code>docs/phase_2/window_runbook.md</code>.</li> <li>The generated state-kernel blocks are authoritative for work selection. Hand-authored <code>RUN_STATE.md</code> and <code>TASK_QUEUE.md</code> text remains authoritative only for its own factual, policy, and historical domains; <code>docs/decision_log.md</code> remains the policy authority, exit checklists own phase completion, and evidence artifacts own scientific truth.</li> <li>Retained corpus and session scratchpad evidence are immutable.</li> </ul> <h2 id="historical-next-work-snapshot-superseded-2026-07-15">Historical Next-Work Snapshot (superseded 2026-07-15)</h2> <p>The following 2026-07-13 narrative is retained for chronology only. It is not a live queue or restart instruction; the generated work-selection region is the sole selector.</p> <p>The comprehensive whole-project audit is the declared gate (Ed, 2026-07-13): method proposal pending Ed&#39;s approval, then the audit runs and its findings are adjudicated before any further feature work. After that: Window A in the first clean quiet-machine window (C-019/P2-015-SMOKE, then P2-015 floors, P2-006 baselines), with post-audit [AGENT] heads P2-050 adjudication, SITE-02, and P2-027 publication prep outside quiet windows. <code>TASK_QUEUE.md</code> remains the ordering authority.</p> <p>Hardware-gated (unchanged): 2K/2L (P1-006; NV-GATE-2 additions from C-027 apply at live promotion), wall meter (P1-003), topology (P1-004), calendar mapping (P1-008).</p> <h2 id="reference-decisions-and-blockers-non-selection-context">Reference Decisions And Blockers (non-selection context)</h2> <p>These pointers retain external-dependency context but do not rank or select work. The generated region controls task selection.</p> <ul> <li>Supervisor approval and scope pending (P1-001, R-001 — mitigation holding); gates FULL D-016 closure.</li> <li>Calendar dates pending (P1-008, R-012).</li> <li>Wall-meter decision pending (P1-003, R-007).</li> <li>Physical network topology pending (P1-004, R-011).</li> <li>NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).</li> <li>Git author identity on this machine auto-selected as <code>Ed R &lt;edr@Eds-MacBook-Pro.local&gt;</code>. Amend future commits if a different identity is needed.</li> </ul> </div> </div> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>RUN_STATE.md · commit 1af9f92 · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/reviews/2026-07-08-technical-merit-review.md:39:3. **Home-cluster and edge-orchestration tooling authors** (exo/prima.cpp lineage) -- served by the Q4 -> placement arc. These systems partition on latency and memory feasibility with zero measured energy input; JouleWise would supply the first energy-placement coefficients. The scope caveat is mandatory: the validated arc addresses *phase* placement (prefill vs decode node), not the layer-split assignment these tools mostly do, so they get a validated model shape and a worked example, not a coverage table.
docs/reviews/2026-07-08-technical-merit-review.md:53:2. **The Q4 -> placement-optimality arc.** A holdout-validated fixed-plus-marginal energy model, composed with measured link-transfer energy to *predict* measured split energy. The standalone fit is methodologically incremental but predictive with predeclared interpolation/extrapolation holdouts, on a device class and whole-device rail boundary the surveyed literature omits; the compositional validation is what elevates Q1 from a point observation to a transferable theory, and it is the program's only L3-templated question. The already-measured near-constant decode power (~23.5 -> 27.5 W across an 81x parameter spread) is exactly the raw material it needs.
docs/reviews/2026-07-08-technical-merit-review.md:65:4. **Zero findings above L1 as of today.** Six bundles versus hundreds of pages of gating machinery; the full bundle->plan->floor->ladder chain has never run end-to-end on real data. The sequencing is methodologically correct (floors before sized campaigns), and the program caught two contamination events -- one by human review before the gate existed, one by the gate's first true positive -- but all research merit is currently design merit, concentrated in a Phase 3 + Q4 bet with a thin fallback. *Defusal:* run the floor calibration and push one campaign through the entire chain.
docs/reviews/2026-07-08-technical-merit-review.md:96:- **Question ranking (adjudicated):** 1. the coupled Q4→Q1 compositional
docs/phase_3/phase_3_plan.md:4:pre-registered compositional split-energy predictions (from AP-1 Q4
docs/site/roadmap.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Roadmap - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html" class="active">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <section class="observatory-hero"> <div class="kicker">Roadmap</div> <h1>Queue rank is the flight plan.</h1> <p class="lede">The current queue is parsed from the exact live table headers in <code>TASK_QUEUE.md</code>. Lane filters are progressive enhancement.</p> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </section> <section class="flight-plan"> <div class="next-two"><span class="card-label">Next two</span><strong class="mono">P1-008 -> P2-027</strong><p>P1-008 runs first, then P2-027.</p></div> <div class="lane-filters" aria-label="Filter queue by lane"> <button type="button" data-lane-filter="all" aria-pressed="true" class="active">All</button> <button type="button" data-lane-filter="QUIET-MAC" aria-pressed="false">Quiet Mac</button> <button type="button" data-lane-filter="AGENT" aria-pressed="false">Agent</button> <button type="button" data-lane-filter="ED-EXTERNAL" aria-pressed="false">Ed</button> </div> </section> <section class="queue-stack"><article class="lane-card" data-lane="ED-EXTERNAL"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#E1</span><span class="mono task-code">P1-008</span><span class="status-chip">READY</span><span class="lane-chip lane-ed-external">ED-EXTERNAL</span></div> <p class="status-note">READY</p> <h2>Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).</h2> <details><summary>Acceptance</summary><p>Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: <a href="docs/milestones.md">Milestones + R-012</a>. Acceptance: <a href="docs/process/state_kernel.json">P1-008 acceptance</a>. Note: R-012 is the biggest active management risk for an undergrad timeline.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="ED-EXTERNAL"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#E2</span><span class="mono task-code">P2-027</span><span class="status-chip">READY</span><span class="lane-chip lane-ed-external">ED-EXTERNAL</span></div> <p class="status-note">READY</p> <h2>Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party.</h2> <details><summary>Acceptance</summary><p>Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: <a href="docs/reviews/2026-07-09-c027-whole-project-review.md">C-020 + C-027 NEG-9</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-027 acceptance</a>. Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="ED-EXTERNAL"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#E3</span><span class="mono task-code">P1-001</span><span class="status-chip">READY</span><span class="lane-chip lane-ed-external">ED-EXTERNAL</span></div> <p class="status-note">READY</p> <h2>Capture supervisor approval and scope notes.</h2> <details><summary>Acceptance</summary><p>Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: <a href="docs/risk_register.md">R-001</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="ED-EXTERNAL"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#E4</span><span class="mono task-code">P1-003</span><span class="status-chip">READY</span><span class="lane-chip lane-ed-external">ED-EXTERNAL</span></div> <p class="status-note">READY</p> <h2>Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method.</h2> <details><summary>Acceptance</summary><p>Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: <a href="docs/decision_log.md">D-018/C-003</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Elevated value: gates Q6 boundary sensitivity (C-003).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="ED-EXTERNAL"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#E5</span><span class="mono task-code">P1-004</span><span class="status-chip">READY</span><span class="lane-chip lane-ed-external">ED-EXTERNAL</span></div> <p class="status-note">READY</p> <h2>Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method.</h2> <details><summary>Acceptance</summary><p>Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: <a href="docs/risk_register.md">R-011</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Partial.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="ED-EXTERNAL"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#E6</span><span class="mono task-code">P1-006</span><span class="status-chip">READY</span><span class="lane-chip lane-ed-external">ED-EXTERNAL</span></div> <p class="status-note">READY</p> <h2>Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L).</h2> <details><summary>Acceptance</summary><p>Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: <a href="docs/phase_2/hardware_slice_implementation_guide.md">Remote gate / NV-GATE-2</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q1</span><span class="mono task-code">P2-015</span><span class="status-chip">PARTIAL</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">PARTIAL; READY</p> <h2>Collect the first claim-grade Window A floors in one clean prospective quiet window per the claim-window run-book: mint the drift bound in-window, then run the start triplet, midpoint reference, and end triplet before the a8 re-verdict and Splitwise sizing.</h2> <details><summary>Acceptance</summary><p>Reducer-0.5.2/0.6.2 strict-valid calibration bundles; per-metric floor_abs_j and floor_cmp_j; governed idle uncertainty retained; calibration manifest hash cited by later reports. Evidence: Versioned strict-valid calibration bundles; Per-metric/window-class floor_abs_j + floor_cmp_j; Calibration manifest hash cited by later reports. Authority: <a href="docs/phase_2/detection_floor.md">D-054 + detection floor spec</a>. Acceptance: <a href="docs/phase_2/phase_2_exit_checklist.md">Phase 2 exit checklist</a>. Fence: Claim-bearing collection requires fresh 59-pulse protocol-v3 calibration BRACKETING the window (consumed max(B_pre,B_post)); floor artifacts are claim-licensing only from same-custody-session governed extraction until FLOOR-BIND-01 closes (D-078 clause 8 (L1) + bracketing ruling). Note: PR #79 instrument repair and PR #85 SCREEN+BUDGET rules are merged; the start gate is one clean quiet window executed per docs/phase_2/window_runbook.md.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q2</span><span class="mono task-code">P2-006</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">BLOCKED — P2-015 (Window-A floors measured first)</p> <h2>Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison.</h2> <details><summary>Acceptance</summary><p>Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: <a href="docs/phase_2/phase_2_plan.md">Phase 2 plan + analysis plans</a>. Acceptance: <a href="docs/phase_2/phase_2_exit_checklist.md">Phase 2 exit checklist</a>. Note: Software interpretation gates are satisfied; execution remains blocked until P2-015 Window-A floors complete.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q3</span><span class="mono task-code">P2-010</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">BLOCKED — P2-015 (quiet-window tail available after floors)</p> <h2>P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail.</h2> <details><summary>Acceptance</summary><p>joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: <a href="docs/contracts/analysis_plans.md">AP-5 + affine stream log</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-010 acceptance</a>. Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q4</span><span class="mono task-code">P2-019</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">BLOCKED — P2-006 (Window-A baselines size n)</p> <h2>q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6).</h2> <details><summary>Acceptance</summary><p>Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: <a href="docs/contracts/analysis_plans.md">AP-1</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-019 acceptance</a>.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q5</span><span class="mono task-code">P2-020</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">BLOCKED — P2-006 (Window-A baselines size n)</p> <h2>Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts.</h2> <details><summary>Acceptance</summary><p>Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: <a href="docs/contracts/analysis_plans.md">AP-6 + D-046</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-020 acceptance</a>. Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q6</span><span class="mono task-code">P2-012</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">BLOCKED — P2-006 (identification-core runs after Window A)</p> <h2>Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases.</h2> <details><summary>Acceptance</summary><p>Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: <a href="docs/contracts/analysis_plans.md">AP-4 + D-039/D-040</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-012 acceptance</a>. Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q8</span><span class="mono task-code">P2-046B</span><span class="status-chip">READY</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">READY</p> <h2>Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts.</h2> <details><summary>Acceptance</summary><p>Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C6</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-046B acceptance</a>. Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q9</span><span class="mono task-code">P2-047B</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">BLOCKED — P2-015 (Window-A floors exist), P2-047A (frozen controller-overhead harness exists)</p> <h2>Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict.</h2> <details><summary>Acceptance</summary><p>Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C7</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-047B acceptance</a>.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A0</span><span class="mono task-code">P2-035</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-015 (P2-015 detection floors measured)</p> <h2>RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests).</h2> <details><summary>Acceptance</summary><p>Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: <a href="docs/specs/rq_energy_variance_design.md">RQ-ENERGY-VARIANCE candidate design</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-035 acceptance</a>. Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A3</span><span class="mono task-code">FLOOR-BIND-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions.</h2> <details><summary>Acceptance</summary><p>Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: <a href="docs/decision_log.md">D-078 clause 8 (confirmation round 9, registered limitation L1)</a>. Acceptance: <a href="docs/process/state_kernel.json">FLOOR-BIND-01 acceptance</a>. Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A4</span><span class="mono task-code">AXI-SB-ADAPTER</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims.</h2> <details><summary>Acceptance</summary><p>The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: <a href="docs/specs/axi/sb_static_batch_verdict.md">AXI-SB verdict document (supported; mint-on-supported follow-on)</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SB-ADAPTER acceptance</a>. Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A6</span><span class="mono task-code">AXI-SD</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Prepare the matched dense/MoE pair proposal with the consult&#x27;s pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT.</h2> <details><summary>Acceptance</summary><p>A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016&#x27;s cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: <a href="docs/axi-handoff.md#4-work-program-post-audit-clearance-streams">AXI handoff work program S-D</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SD acceptance</a>. Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A7</span><span class="mono task-code">AXI-SE</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-015 (P2-015 publishes Window-A floors before AXI analysis plans are finalized)</p> <h2>Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult&#x27;s floor and ownership closures.</h2> <details><summary>Acceptance</summary><p>The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A&#x27;s gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: <a href="docs/axi-handoff.md#4-work-program-post-audit-clearance-streams">AXI handoff work program S-E</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SE acceptance</a>. Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A16</span><span class="mono task-code">P3-000</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — R-003 (user approves the 3.0.2 installs (R-003))</p> <h2>KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8).</h2> <details><summary>Acceptance</summary><p>Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: <a href="docs/decision_log.md">D-035/D-036</a>. Acceptance: <a href="docs/phase_3/phase_3_exit_checklist.md">Phase 3 exit checklist</a>. Note: 3.0.1 complete and merged (PR #9, replay_supported).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A17</span><span class="mono task-code">P2-022</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041))</p> <h2>Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported).</h2> <details><summary>Acceptance</summary><p>3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: <a href="docs/decision_log.md">D-041 (post-2M gate)</a>. Acceptance: <a href="docs/contracts/adapter_contracts.md">Adapter contract</a>. Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A18</span><span class="mono task-code">P2-023</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded)</p> <h2>HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy.</h2> <details><summary>Acceptance</summary><p>Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: <a href="docs/decision_log.md">D-041 (post-2M gate)</a>. Acceptance: <a href="docs/research_question_bank.md">RQ bank import-smoke design</a>. Fence: No pass@k, accuracy, or capability claim (D-041).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A19</span><span class="mono task-code">P2-024</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-006 (2M reductions identify floor/MDE headroom), P2-015 (Window-A floors measured)</p> <h2>Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC].</h2> <details><summary>Acceptance</summary><p>Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: <a href="docs/research_question_bank.md">C-015 + RQ bank</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-024 acceptance</a>.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A21</span><span class="mono task-code">P3-001b</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-006 (2M affine coefficients exist)</p> <h2>Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049).</h2> <details><summary>Acceptance</summary><p>AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: <a href="docs/decision_log.md">D-048/D-049</a>. Acceptance: <a href="docs/contracts/analysis_plans.md">Analysis plans (split row)</a>.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A22</span><span class="mono task-code">P2-004</span><span class="status-chip">PARTIAL</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">PARTIAL; READY; GATES close: P1-001</p> <h2>Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding.</h2> <details><summary>Acceptance</summary><p>Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: <a href="docs/decision_log.md">D-016</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Provisional small-model pick 2026-07-06 opens 2G.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A23</span><span class="mono task-code">P2-005</span><span class="status-chip">PARTIAL</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">PARTIAL; READY; GATES live_promotion: P1-006</p> <h2>Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute.</h2> <details><summary>Acceptance</summary><p>Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: <a href="docs/specs/c027/nv-gate-2_live_promotion.md">NV-GATE-2 live-promotion spec</a>. Acceptance: <a href="docs/phase_1/2k_live_verification_checklist.md">2K live verification checklist</a>. Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A24</span><span class="mono task-code">P2-016</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-006 (the 2M corpus exists)</p> <h2>Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment.</h2> <details><summary>Acceptance</summary><p>Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: <a href="docs/reviews/2026-07-09-c027-whole-project-review.md">C-011 ledger + C-027 (post-2M umbrella)</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-016 acceptance</a>. Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A25</span><span class="mono task-code">P2-047A</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-015 (Window-A floors exist before overhead design is frozen)</p> <h2>Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes.</h2> <details><summary>Acceptance</summary><p>A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C7</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-047A acceptance</a>. Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p4"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A29</span><span class="mono task-code">DOC-008-REFLECTION</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6.</h2> <details><summary>Acceptance</summary><p>Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 reflection-protocol retirement</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 reflection-protocol retirement</a>. Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p4"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A30</span><span class="mono task-code">DOC-008-STATUS</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8.</h2> <details><summary>Acceptance</summary><p>Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 PROJECT_STATUS compaction</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 PROJECT_STATUS compaction</a>. Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p4"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A31</span><span class="mono task-code">DOC-008-INTAKE</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9.</h2> <details><summary>Acceptance</summary><p>Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 intake and procedure reconciliation</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 intake reconciliation</a>. Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p4"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A32</span><span class="mono task-code">DOC-008</span><span class="status-chip">PARTIAL</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS</p> <h2>Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked.</h2> <details><summary>Acceptance</summary><p>Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 state-kernel specification</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 required outcomes</a>. Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A33</span><span class="mono task-code">P2-050</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2.</h2> <details><summary>Acceptance</summary><p>Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives its own adjudication; Semantic cooldown-row verification receives its own adjudication; Once-per-manifest first-run exemption receives its own adjudication; Scoped top-up detection and cooldown trace v2 receive their own adjudications. Authority: <a href="docs/run_reports/2026-07-11-c028-continuation.md">C-028 dissent-record queue candidates</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-050 acceptance</a>. Fence: Do not implement any candidate before its own recorded adjudication (C-028 dissent-record queue candidates).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A34</span><span class="mono task-code">TOOL-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Fix codex-run-v3 defects: resume-after-NEEDS_SCOPE no-op; preventive permission profiles; NEEDS_RULING recognition; effort-default passthrough; stream-death OK exits with thin out-files; resume --last cross-thread attachment through the global latest session; and session-open paths lacking per-path match specifiers.</h2> <details><summary>Acceptance</summary><p>All seven codex-run-v3 defects close in lead personal tooling with targeted regressions and updated adapter operations lessons. Evidence: Resume after NEEDS_SCOPE continues the requested work; Preventive permission profiles and NEEDS_RULING recognition are covered; Omitted effort defaults to xhigh instead of config passthrough; Upstream stream death fails instead of exiting OK with a thin out-file; Resume requires an explicit session ID and cannot cross-attach through a global --last pointer; Session-open accepts a per-path match specifier without post-hoc child expansion. Authority: <a href="docs/run_reports/2026-07-13-bridge-v11.md">Bridge v1.1 wrapper and session operations record</a>. Acceptance: <a href="docs/process/state_kernel.json">TOOL-01 acceptance</a>. Fence: Keep implementation in lead personal tooling; this repository owns only the work record (Bridge v1.1 wrapper and session operations record). Note: lead personal tooling, non-repo</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A35</span><span class="mono task-code">AUD-FOLLOWUPS</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Close the ULTRA comparison audit&#x27;s accepted small residue in one bounded agent task: WO-012&#x27;s owned D-062 lint queue row, WO-014 realized-token discrimination, WO-017 default no-handoff regression, WO-020 standalone bridge-checker decision, and WO-040 authored-instruction absolute-path plus genuine pristine-clone coverage.</h2> <details><summary>Acceptance</summary><p>The ULTRA comparison audit&#x27;s five accepted small follow-ups close with discriminating tests or an explicit recorded decision, without creating a ceremony-dispositions task. Evidence: WO-012&#x27;s owned D-062 lint queue-row obligation is implemented and covered; WO-014 has a realized-token discriminating test; WO-017 has a default no-handoff regression assertion; WO-020 has a recorded standalone bridge-checker decision; WO-040 has authored-instruction absolute-path coverage plus a genuine pristine-clone test. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/report.md">Comprehensive-audit close-out and accepted-residue list</a>. Acceptance: <a href="docs/process/state_kernel.json">AUD-FOLLOWUPS acceptance</a>. Fence: Do not create AUD-CEREMONY-DISPOSITIONS; ceremony dispositions remain report-owned (Comprehensive-audit report disposition ledger). Note: Accepted small residue only; audit ceremony dispositions remain in the report.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A36</span><span class="mono task-code">AUD-WO-033</span><span class="status-chip">READY;</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY; GATES close: P2-006</p> <h2>After 2M, split scripts/run_campaign.py along tested policy seams, pure validation and provenance first and execution lifecycle second, only when campaign-scale or split or multi-node work first forces edits to that path.</h2> <details><summary>Acceptance</summary><p>The post-2M campaign-runner refactor is behavior-preserving across the full campaign test portfolio and retains every collection and claim-readiness safeguard. Evidence: Pure validation and provenance seams are extracted before execution lifecycle seams; The full campaign behavior-parity portfolio is green before and after the split; Locks, waivers, backups, cooldown, and claim-readiness behavior remain unchanged. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-033</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-033</a>. Fence: Keep this post-2M and behavior-preserving; do not redesign campaigns or weaken locks, waivers, backups, cooldown, or claim-readiness gates (Comprehensive-audit register WO-033 non-goals and risk note).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A37</span><span class="mono task-code">AUD-WO-034</span><span class="status-chip">READY;</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY; GATES close: PHASE-3-SPLIT-SCHEDULED</p> <h2>At Phase-3 split scheduling, assign bounded owners and dependencies for transfer-bench, split replay, composite validate and reduce, KV-economics reduction, and matrix-generator extension before any PLANNED command becomes executable.</h2> <details><summary>Acceptance</summary><p>When Phase-3 split work is scheduled, every PLANNED pack command gains an owner or explicit deferred marker without pack collapse or premature implementation. Evidence: Every PLANNED command has a bounded owner row or explicit deferred-design marker; Pack-command ownership lint passes positive and negative fixtures; Settled split pre-registration requirements and offline-before-live fences remain intact. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-034</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-034</a>. Fence: Do not prune draft designs, collapse campaign packs, or implement split or KV work in this ownership pass (Comprehensive-audit register WO-034 non-goals).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A38</span><span class="mono task-code">AUD-WO-035</span><span class="status-chip">READY;</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY; GATES close: 2K-LIVE-REMOTE-TRANSFER-SCHEDULED</p> <h2>Before the first 2K-live or remote split-transfer task, define a versioned discriminated node-worker payload and test realistic typed rejection without overloading telemetry blocks.</h2> <details><summary>Acceptance</summary><p>The 2K-live and remote roadmap has a versioned transfer-task payload seam with typed rejection before split-transfer implementation. Evidence: A versioned discriminated payload path exists for transfer tasks; A realistic unsupported transfer request fails with a typed versioned error; Telemetry blocks are not overloaded with transfer semantics. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-035</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-035</a>. Fence: Define and reject the future transfer shape only; do not implement split execution or transfer benchmarking (Comprehensive-audit register WO-035 non-goals). Note: D-043 supersession closure falls due at landing: add the dated protocol-version supersession line identified by PA-2.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A39</span><span class="mono task-code">AUD-WO-036</span><span class="status-chip">READY;</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY; GATES close: 2K-LIVE-REMOTE-CONCURRENCY-SCHEDULED</p> <h2>When 2K-live or remote retries or concurrency are introduced, add a pre-launch node and GPU ownership lease plus idempotent duplicate prepare and start behavior.</h2> <details><summary>Acceptance</summary><p>Retries or concurrent 2K-live and remote campaigns cannot double-own a node or GPU and duplicate delivery is idempotent. Evidence: Duplicate prepare and start delivery is idempotent; Node and GPU ownership is leased before launch; Concurrency coverage exercises the ownership and duplicate-delivery contract. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-036</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-036</a>. Fence: Do not run concurrent hardware campaigns or make live-correctness claims in this agent task (Comprehensive-audit register WO-036 non-goals).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A40</span><span class="mono task-code">AUD-WO-037</span><span class="status-chip">READY;</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED</p> <h2>Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path.</h2> <details><summary>Acceptance</summary><p>Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-037</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-037</a>. Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A41</span><span class="mono task-code">AUD-WO-038</span><span class="status-chip">READY;</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED</p> <h2>At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition.</h2> <details><summary>Acceptance</summary><p>At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-038</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-038</a>. Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A42</span><span class="mono task-code">AUD-WO-039</span><span class="status-chip">PARTIAL</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED</p> <h2>At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review.</h2> <details><summary>Acceptance</summary><p>The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-039</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-039</a>. Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A43</span><span class="mono task-code">CUSTODY-HARDEN-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Custody hardening follow-on from the screen+budget gauntlet: reduce-layer label-trust removal (G2A), drift-bound seal authentication (A3-r2), dead no-freshness accommodation disposition, artifact_schema_invalid mislabel.</h2> <details><summary>Acceptance</summary><p>Close the PR #85 gauntlet&#x27;s deferred custody-hardening seams: config-derived mockness reaches the reduce-layer barriers, the drift-bound seal stops being self-certifying, and two diagnostic nits are resolved. Evidence: Reduce-layer environment/CPU claim barriers derive mockness from the custody-bound config, with metadata/summary-label early returns removed; Drift-bound artifact corpus identities resolve against repo-registered or custody-bound bytes (seal no longer self-certifying); Dead pre-addendum no-freshness accommodation removed or pinned as intentional forward-compatibility; artifact_schema_invalid evidence-binding mislabel renamed or documented at emission site. Authority: <a href="docs/council_log.md">C-033 gauntlet deferrals (council log; detail in docs/run_reports/2026-07-24-screen-budget-gauntlet.md)</a>. Acceptance: <a href="docs/process/state_kernel.json">CUSTODY-HARDEN-01 acceptance</a>. Note: Minted 2026-07-25 from PR #85 gauntlet deferrals; triangle-agreement enforcement (merged) already raises these seams to three-file forgery cost.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A44</span><span class="mono task-code">CAL-REBRACKET-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Implement the governed max-bracket prospective re-reduction flow (authenticated bracket max, sealed reduction manifest, basis revision, consumption binding), then re-reduce and extract windows a10/a9.</h2> <details><summary>Acceptance</summary><p>Close the max-bracket consumption gap: post&gt;pre calibration windows (a coin flip) are structurally unconsumable until the D-078-required prospective re-reduction flow exists. Evidence: A governed prospective-reduction flow re-reduces a complete 37-occurrence evaluation basis under the authenticated max(B_pre,B_post), never a caller-supplied scalar; Derived summaries land in a dedicated custody directory with a hash-sealed manifest binding source/raw/stored-summary/reducer/calibration/policy/derived hashes; Whole-window verification and extraction select the exact revised basis and reject incomplete, mixed, duplicated, or latest-wins artifacts; Regressions cover omitted references, substituted summaries, scalar inflation, partial coverage, conflicting basis rows; Windows a10 and a9 re-reduced and consumed; a10 phase floors extracted with drift allowances. Authority: <a href="docs/decision_log.md">D-078 bracketing ruling (max(B_pre,B_post)) + 2026-07-25 collection-night consult (S1 design in job tmp bracket_consult.md)</a>. Acceptance: <a href="docs/process/state_kernel.json">CAL-REBRACKET-01 acceptance</a>. Fence: The earliest valid causal post-calibration is the operative post; later valid captures never replace it, and retrying a valid calibration to seek a smaller bound is forbidden. (No-verdict-shopping ruling). Note: Minted 2026-07-25 from the first collection night under the merged rules: a9+a10 both PASSED verdicts at mint; consumption refused calibration_bracket_exceeds_minted_bound (post 25.046ms &gt; pre 24.879ms minted). Operator deviation recorded: post-cal pulse-failure retry outside the run-book&#x27;s clock-anchor-only retry shape (evidence preserved; earliest-valid-causal selection unaffected).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A45</span><span class="mono task-code">FLOOR-LABEL-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Convert admissible_set_uncertainty_dominates_point_floor from hard refusal to a labelled claim path (floor_source names the dominant term; point floor retained as repeatability diagnostic), after Ed ratifies the D-078 amendment.</h2> <details><summary>Acceptance</summary><p>Attribution-limited floors become claimable and labelled, so instrument-limited windows publish an honest floor instead of refusing. Evidence: D-078 amendment ratified by Ed BEFORE any code softening (closed-registry channel); Extraction emits a labelled claim-path floor with floor_source naming the dominant uncertainty term; Point (repeatability) floor preserved and reported separately as a diagnostic; Single-count discipline recorded: effective clearable effect = floor + claim-side bound; neither may be optimized away; a10 phase cells extract as labelled attribution-limited floors. Authority: <a href="docs/decision_log.md">2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)</a>. Acceptance: <a href="docs/process/state_kernel.json">FLOOR-LABEL-01 acceptance</a>. Fence: No code change to the dominating-uncertainty gate before Ed ratifies the D-078 amendment; the registry channel is mandatory. (D-054 floor semantics / closed-registry amendment rule). Note: Minted 2026-07-25. D-054 defines the floor as a practical prediction bound on FALSE OBSERVED EFFECTS, not a repeatability statistic; the corner-widened maximum satisfies that definition. GATE: Ed ratifies the amendment first — do not soften the gate in code before ratification.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A46</span><span class="mono task-code">FLOOR-WORKLOAD-SIZING-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Re-size the floor/science campaign workloads so measured effects clear the duration-independent attribution floor, and pilot the resulting effect-to-floor ratio before spending quiet-machine nights on ABBA collection at current sizes.</h2> <details><summary>Acceptance</summary><p>Anchor-attribution error is approximately duration-independent (~1 J regardless of phase size) while effects scale with workload, so lengthening prefill/decode raises effect-to-floor linearly at zero instrument cost. Evidence: Measured effect-to-floor ratio at candidate workload sizes, from a pilot rather than assumption; Re-sized configs for the remaining floor stages, with the sizing rationale recorded; Explicit decision on which queued stages are collected at which sizes. Authority: <a href="docs/decision_log.md">2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)</a>. Acceptance: <a href="docs/process/state_kernel.json">FLOOR-WORKLOAD-SIZING-01 acceptance</a>. Note: Minted 2026-07-25; scope corrected same day after the quantitative replay. NOT a blocker on the ABBA roadmap: under the labelled-floor path the queued stages remain scientifically viable at current sizes (tens-of-percent effects on ~50 J clear a ~3 J floor plus claim-side bound). This is a MARGIN optimisation — attribution error is duration-independent while effects scale with workload, so longer prefill/decode buys effect-to-floor ratio for free. Pilot the ratio at candidate sizes before committing the remaining quiet-machine nights.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A47</span><span class="mono task-code">FLOOR-COMMONMODE-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Pre-register and evaluate a common-mode anchor estimator for ABBA blocks: sweep one shared fiducial shift across all four members, re-integrate measured curves, and add only genuinely per-bundle components adversarially.</h2> <details><summary>Acceptance</summary><p>The fiducial term is ~80% of the composed anchor bound (24.9 of ~31.1 ms, verified) and is literally the same artifact for all four members of a block; treating it as four independent adversarial draws is itself an unphysical modelling choice. Evidence: Block-timescale fiducial stationarity registered as a NAMED transfer assumption with its evidence; Estimator pre-registered before it touches claim-bearing data; The identical estimator applied to BOTH the calibration blocks and the consuming science contrast (a floor calibrated with cancellation the consumer does not get would understate false effects); Quantified gain on a5/a10 blocks versus the worst-case-sum default. Authority: <a href="docs/decision_log.md">2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)</a>. Acceptance: <a href="docs/process/state_kernel.json">FLOOR-COMMONMODE-01 acceptance</a>. Note: Minted 2026-07-25. Quantified same day on a5 decode ABBA (10 complete blocks): implemented worst-case-sum half-width gives a 6.46 J comparative floor; a common-mode proxy gives 2.13 J, a 3x improvement — material, but still above that cell&#x27;s 0.60 J point floor, so it does not by itself restore extraction under the current gate. Value is in tightening the labelled floor, not in avoiding the label. Fiducial share of the composed bound measured at 80-87%.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A48</span><span class="mono task-code">PHASE-SHARE-ESTIMAND-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Investigate the anti-correlated prefill/decode boundary error: energy a shift removes from one phase it adds to the other, so the phase-share estimand has ONE boundary nuisance parameter whose joint envelope is a curve, not a box.</h2> <details><summary>Acceptance</summary><p>Treating each phase&#x27;s anchor envelope as an independent box double-spends the shared interior boundary and inflates uncertainty on exactly the split/share quantity the Splitwise replication needs. Evidence: Determined whether _corner_composed_anchor_shift_envelope treats the shared interior boundary independently; Joint envelope over the single boundary-position parameter derived by re-integration sweep (measured-curve arithmetic only); Quantified effect on the phase-asymmetry claim envelope versus the independent-box treatment. Authority: <a href="docs/decision_log.md">2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)</a>. Acceptance: <a href="docs/process/state_kernel.json">PHASE-SHARE-ESTIMAND-01 acceptance</a>. Note: Minted 2026-07-25 from the attribution-limit adjudication. Potentially the largest single win available for Splitwise sizing, at no instrument cost.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article></section> <section class="interlock"><h2>Do not do yet</h2><ul><li>(satisfied 2026-06-12) The mock bundle/reducer path and report generator now exist; dashboard/report work is no longer blocked.</li> <li>(satisfied 2026-06-12) The mock lifecycle is runnable, so live MLX/powermetrics implementation may proceed once its hardware gates open (P1-002 + D-016); follow <code>docs/phase_2/hardware_slice_implementation_guide.md</code>.</li> <li>(resolved 2026-06-12) Hailo feasibility has a verdict (<code>unsupported_workload</code>); do not implement a Hailo backend — report it as an applicability finding.</li> <li>Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in D-008; implementation waits).</li> <li>Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware pairings, or borrow-window scheduling before 2M baselines and the Stage 3.0 verdicts exist (C-007 wording fix; was previously stated as a blanket Phase 3 hold that contradicted the queue).</li> <li>Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the rehearsed runbook exist (R-006).</li> <li>Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has produced data.</li> <li>Do not close D-016 (model selection) without P1-001 supervisor scope or an explicit user go-ahead.</li> <li>(satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own gates (D-016 + <code>[mac]</code> install; privileged sample + D-004 sudoers) open — build on the post-2N seams (RunContext raw evidence, D-026 markers, D-027 rail rows, 2N.3 observed-token fallback).</li></ul><span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span></section> <section class="timeline-rail"><h2>Completed reel</h2><div class="timeline-node"><span class="mono">2026-07-18</span><strong>CODEX-BRIDGE-PET</strong><p>Make the native Codex pet reflect Claude Code background Sol work without changing adaptive effort routing</p></div> <div class="timeline-node"><span class="mono">2026-07-17</span><strong>P2-015-SMOKE</strong><p>Complete the pre-Window-A production-shaped campaign shakedown through doctor, strict validation, reducer 0.4.2, strict revalidation, campaign verdict split, and approved backup; keep extra samplers disabled pending DF-TELEM</p></div> <div class="timeline-node"><span class="mono">2026-07-17</span><strong>P2-038</strong><p>Close the production-uncertainty live tail with a true MLX + <code>/usr/bin/powermetrics</code> production-shaped shakedown through strict validation, reducer 0.4.2, strict revalidation, request-eligibility gating, and approved backup</p></div> <div class="timeline-node"><span class="mono">2026-07-17</span><strong>AXI-SC</strong><p>AXI stream S-C leg 1: pinned mlx-lm speculative-decode/MTP feasibility spike — verdict <code>unsupported_for_joulewise</code> (external draft: <code>event_observability</code>; native MTP: <code>native_mtp_generation</code>); Mac energy leg not minted, with explicit runtime-upgrade revisit triggers</p></div> <div class="timeline-node"><span class="mono">2026-07-16</span><strong>AXI-SB</strong><p>AXI stream S-B: pinned mlx-lm static-batch feasibility spike — verdict <code>supported</code> (mlx-lm 0.31.3 BatchGenerator path; true B&gt;1 execution with full per-request observability); Mac C5-2.2 leg minted per D-070; follow-on adapter row AXI-SB-ADAPTER minted at rank 4</p></div> <div class="timeline-node"><span class="mono">2026-07-16</span><strong>SPLIT-AP</strong><p>Split pre-registration freeze (adjudicated Part I, D-067-reconciled): gross-only primary estimand and headline; both monolithic references mandatory (Holm, intersection-union); pinned idle-sub calculation with D-067 reporting restriction; D-048 predictor over all five gross components; named open gates OPEN-GATE-SPLITAP-PACK-LINT + OPEN-SPLIT-PRED-FIXED-COMPOSITION</p></div> <div class="timeline-node"><span class="mono">2026-07-16</span><strong>SITE-02</strong><p>Close SITE-01 D1/D2 deferrals: loud structured Lakebed discovery (env + OS-path, exact-version refusal incl. wrong-before-correct PATH ordering, never silent estimator fallback) + node decode regression executing the EMITTED TypeScript via pinned esbuild; D2 guaranteed in CI (release-chain focused step)</p></div> <div class="timeline-node"><span class="mono">2026-07-16</span><strong>AXI-SA</strong><p>AXI stream S-A: burst-decode metric-semantics contract implementation, stages 0-7 (versioned request-scoped emission events, proposal/acceptance counters, speculation identity, sibling analysis manifest with frozen AP-SPEC denominators, output-identity gate, mock spec adapter last)</p></div> <div class="timeline-node"><span class="mono">2026-07-15</span><strong>AXI-S0</strong><p>AXI stream S-0: advisor-facing doc alignment (gross basis+boundary on every number, D-067 attributed rationale, harness/benchmark split, five-axis Q4 agenda, C-023-IDLE-STATIONARITY note, DRIFT.md refresh)</p></div> <div class="timeline-node"><span class="mono">2026-07-13</span><strong>SITE-01</strong><p>Site capsule under the 1 MiB Lakebed cap + live redeploy</p></div> <div class="timeline-node"><span class="mono">2026-07-13</span><strong>P2-028</strong><p>Response-hash determinism gate (<code>joulewise determinism-gate</code>)</p></div> <div class="timeline-node"><span class="mono">2026-07-13</span><strong>P2-049</strong><p>analysis_manifest.py explicit-root-or-fail-closed resolution (C-028 SF3)</p></div><span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span></section> <script>
docs/site/advisor_brief.html:983:            <p>Planned as a Q4 stress test under exact artifact, quality-equivalence, and floor gates—not as “fewer bytes means less energy.”</p>
docs/specs/c027/rpt-001_report_vertical_slice.md:10:  §5-Q4 gate 4, and §7 rows TOP-6, RIG-2, ARC-9, NEG-2, and NEG-5.
docs/reviews/2026-07-13-comprehensive-audit/receipts/ULTRA-comparison-response.md:73:- **F7 — MAJOR/MINOR — WO-012:** **Major:** the action-required owned deferred D-062 lint queue row does not exist. **Minor:** generated Q4/P2-019 still says “top-up near-floor cells,” relying on an external supersession note, and the eight pack/RQ rows lack PA2’s requested dated replacement/reference. These deviate from “replace … stale TASK_QUEUE rows” and the PA2 supersession clause.
docs/site/record.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Record - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html" class="active">Record</a> <a href="library.html">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <section class="observatory-hero"> <div class="kicker">Record</div> <h1>The narrative stays in the reports.</h1> </section> <section class="record-grid"> <div class="latest-card"><span class="card-label">Latest run report · 2026-07-18</span><h2>Claude Code → native Codex pet bridge</h2><p>Date: 2026-07-18 Lane: [AGENT] Task: CODEX-BRIDGE-PET</p><span class="source-chip" title="docs/run_reports/2026-07-18-claude-codex-pet-observer.md · commit 006eb47"><span class="source-file">docs/<wbr>run_reports/<wbr>2026-07-18-claude-codex-pet-observer.md</span><span class="source-commit">commit 006eb47</span></span></div> </section> <section class="timeline-rail"><h2>Sessions timeline</h2><div class="timeline-day"><h3 class="mono">2026-07-18</h3><div class="timeline-node"><strong>Claude Code script bridge + native pet integration</strong><p><a href="latest_run_report.html">docs/run_reports/2026-07-18-claude-codex-pet-observer.md</a></p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-13</h3><div class="timeline-node"><strong>Bridge v1</strong><p><a href="../run_reports/2026-07-13-bridge-v1.md">docs/run_reports/2026-07-13-bridge-v1.md</a></p></div> <div class="timeline-node"><strong>Restart close</strong><p><a href="../run_reports/2026-07-13-restart-merge-deploy.md">docs/run_reports/2026-07-13-restart-merge-deploy.md</a></p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-12</h3><div class="timeline-node"><strong>Claude↔Sol bidirectional bridge (concurrent Ed-directed thread; lead-verified 2026-07-13)</strong><p><a href="../run_reports/2026-07-12-claude-sol-bridge.md">docs/run_reports/2026-07-12-claude-sol-bridge.md</a></p></div> <div class="timeline-node"><strong>Agent-lane triple</strong><p><a href="../run_reports/2026-07-12-agent-lane-triple.md">docs/run_reports/2026-07-12-agent-lane-triple.md</a></p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-11</h3><div class="timeline-node"><strong>P2-041 vetted rebuild (uncommitted; lead pathspec review and commit pending)</strong><p><a href="../run_reports/2026-07-11-p2041-vetted-rebuild.md">docs/run_reports/2026-07-11-p2041-vetted-rebuild.md</a></p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-10</h3><div class="timeline-node"><strong>NV-GATE-2 idle-capture regression debug/fix (uncommitted; localhost re-verification remains lead-gated)</strong><p><a href="../run_reports/2026-07-10-nvgate2-idle-capture-fix.md">docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md</a></p></div> <div class="timeline-node"><strong>NV-GATE-2 CODE-NOW implementation (NV-1/NV-3/NV-4/NV-5; live promotion evidence still gated)</strong><p><a href="../run_reports/2026-07-10-nvgate2-codenow.md">docs/run_reports/2026-07-10-nvgate2-codenow.md</a></p></div> <div class="timeline-node"><strong>NV-GATE-2 accepted-findings fix round (uncommitted; merge metadata recreation and lead gate pending)</strong><p><a href="../run_reports/2026-07-10-nvgate2-fix-round.md">docs/run_reports/2026-07-10-nvgate2-fix-round.md</a></p></div> <div class="timeline-node"><strong>P2-038 accepted-findings fix round (all FIX-1..FIX-6 green; content-merged <code>origin/main</code>, Git merge metadata sandbox-blocked)</strong><p><a href="../run_reports/2026-07-10-p2038-fix-round.md">docs/run_reports/2026-07-10-p2038-fix-round.md</a></p></div> <div class="timeline-node"><strong>P2-038 production uncertainty software path (live quiet-machine closure still open)</strong><p><a href="../run_reports/2026-07-10-p2038-production-uncertainty.md">docs/run_reports/2026-07-10-p2038-production-uncertainty.md</a></p></div> <div class="timeline-node"><strong>P2-040 reducer-version compatibility review fix (uncommitted)</strong><p><a href="../run_reports/2026-07-10-p2040-versioning-fix.md">docs/run_reports/2026-07-10-p2040-versioning-fix.md</a></p></div> <div class="timeline-node"><strong>P2-040 remainder implementation (uncommitted, pending lead pathspec commit/corpus gate)</strong><p><a href="../run_reports/2026-07-10-p2040-remainder.md">docs/run_reports/2026-07-10-p2040-remainder.md</a></p></div> <div class="timeline-node"><strong>P2-040 / RETRO-001 fix round (committed on c027-int-p2040 after lead review)</strong><p><a href="../run_reports/2026-07-10-p2040-fix-round.md">docs/run_reports/2026-07-10-p2040-fix-round.md</a></p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-09</h3><div class="timeline-node"><strong>C-027 whole-project council review (7 gpt-5.6-sol lenses + counterreview + independent final examiner)</strong><p><a href="../run_reports/2026-07-09-c027-council-review.md">docs/run_reports/2026-07-09-c027-council-review.md</a></p></div> <div class="timeline-node"><strong>Claude Code → Codex MCP bridge hardening and live smoke</strong><p><a href="../run_reports/2026-07-09-claude-codex-mcp-bridge.md">docs/run_reports/2026-07-09-claude-codex-mcp-bridge.md</a></p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-12</h3><div class="timeline-node"><strong>adaptive Claude Code ↔ Sol/Fable bridge follow-up</strong><p><a href="../run_reports/2026-07-12-claude-sol-bridge.md">docs/run_reports/2026-07-12-claude-sol-bridge.md</a></p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-09</h3><div class="timeline-node"><strong>P2-034 broad campaign packs (C-026; PR #39)</strong><p><a href="../run_reports/2026-07-09-p2034-broad-packs.md">docs/run_reports/2026-07-09-p2034-broad-packs.md</a></p></div> <div class="timeline-node"><strong>spec-fleshing wave 2, ultracode (C-025; PRs #33..#38; D-056..D-059)</strong><p><a href="../run_reports/2026-07-09-spec-fleshing-wave2.md">docs/run_reports/2026-07-09-spec-fleshing-wave2.md</a></p></div> <div class="timeline-node"><strong>spec-fleshing wave 1 (C-024; PRs #29..#32; D-052..D-055)</strong><p><a href="../run_reports/2026-07-09-spec-fleshing-wave1.md">docs/run_reports/2026-07-09-spec-fleshing-wave1.md</a></p></div> <div class="timeline-node"><strong>scientific-rigor review of suite/benchmark/question bank (C-023; review-only; full record in <code>docs/reviews/2026-07-09-scientific-rigor-review.md</code>)</strong><p><a href="../run_reports/2026-07-09-scientific-rigor-review.md">docs/run_reports/2026-07-09-scientific-rigor-review.md</a></p></div> <div class="timeline-node"><strong>CP-5 resume</strong><p><a href="../run_reports/2026-07-09-cp5-resume.md">docs/run_reports/2026-07-09-cp5-resume.md</a></p></div> <div class="timeline-node"><strong>meta-process stop-card + codex-bridge audit cleanup (D-050; CP-5 preserved untouched)</strong><p><a href="../run_reports/2026-07-09-meta-process-stop-card-cleanup.md">docs/run_reports/2026-07-09-meta-process-stop-card-cleanup.md</a></p></div> <div class="timeline-node"><strong>advisor status-site live-depth refresh (D-051/C-021; subordinate to the then-active CP-5 stop card)</strong><p><a href="../run_reports/2026-07-09-advisor-status-site.md">docs/run_reports/2026-07-09-advisor-status-site.md</a></p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-08</h3><div class="timeline-node"><strong>suite build (C-017; adjudication + PRs #17/#18/#20/#19; D-044..D-047)</strong><p><a href="../run_reports/2026-07-08-suite-build.md">docs/run_reports/2026-07-08-suite-build.md</a></p></div> <div class="timeline-node"><strong>suite-science + expansion (C-014/C-015; PRs #14/#15/#16; D-038..D-042)</strong><p><a href="../run_reports/2026-07-08-suite-science-expansion.md">docs/run_reports/2026-07-08-suite-science-expansion.md</a></p></div> <div class="timeline-node"><strong>Lakebed deploy (C-013)</strong><p><a href="../run_reports/2026-07-08-lakebed-deploy.md">docs/run_reports/2026-07-08-lakebed-deploy.md</a></p></div> <div class="timeline-node"><strong>site observatory (PR #13)</strong><p><a href="../run_reports/2026-07-08-site-observatory.md">docs/run_reports/2026-07-08-site-observatory.md</a></p></div> <div class="timeline-node"><strong>critique second-pass + councils+critique (C-011 → PR #12)</strong><p><a href="../run_reports/2026-07-08-councils-critique-session.md">docs/run_reports/2026-07-08-councils-critique-session.md</a></p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-07/08</h3><div class="timeline-node"><strong>resume+merge (C-009 first full run; PRs #8..#11)</strong><p><a href="../run_reports/2026-07-07-resume-merge-session.md">docs/run_reports/2026-07-07-resume-merge-session.md</a></p></div></div><span class="source-chip" title="RUN_STATE.md · commit 1af9f92"><span class="source-file">RUN_STATE.md</span><span class="source-commit">commit 1af9f92</span></span></section> <section class="decision-summary"> <div class="readout-row compact"> <div class="readout"><div class="val">77</div><div class="sub">accepted</div></div> <div class="readout cyan"><div class="val">1</div><div class="sub">open</div></div> <div class="readout plain"><div class="val">0</div><div class="sub">superseded</div></div> </div> <div class="record-cards"><article class="record-card"><span class="mono">D-078</span><h3>Soundness gate: no claim-bearing extraction from time-anchor-defective powermetrics corpora</h3><p>accepted; operative under Ed&#x27;s direction through the full repair arc (close-out cap explicitly Ed-ratified 2026-07-22; original-text ratification rides PR #79 review)</p></article> <article class="record-card"><span class="mono">D-077</span><h3>Environment guard, idle admission, and cooldown v2</h3><p>accepted</p></article> <article class="record-card"><span class="mono">D-076</span><h3>Site capacity right-sizing (AUD-WO-039 review): measured-first budgets</h3><p>accepted</p></article> <article class="record-card"><span class="mono">D-075</span><h3>Extension-axis intake: ranked fold-in without new thesis proliferation</h3><p>accepted</p></article> <article class="record-card"><span class="mono">D-074</span><h3>Conditional Qwen3-4B primary repin + OLMo-1B conversion spike authorized</h3><p>accepted</p></article> <article class="record-card"><span class="mono">D-073</span><h3>D-016 device-list amendment: Mac + 3080 Ti primary fleet, 12 GiB cap</h3><p>accepted</p></article></div><span class="source-chip" title="docs/decision_log.md · commit 1af9f92 + uncommitted"><span class="source-file">docs/<wbr>decision_log.md</span><span class="source-commit">commit 1af9f92 + uncommitted</span></span> </section> <section class="timeline-rail"><h2>Council timeline</h2><div class="timeline-day"><h3 class="mono">2026-07-06</h3><div class="timeline-node"><strong><span class="mono">C-001</span> Adopt review/counterreview between Claude and Codex (2H precedent)</strong><p>adopted; all 10 findings accepted, Codex improved the blocker fix design</p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-07</h3><div class="timeline-node"><strong><span class="mono">C-002</span> Reverse review of the 9-commit vertical-slice series; push vs PR</strong><p>PR convention adopted; run_id renamed; P2-008 promoted; D-023 extended; sweep step added</p></div> <div class="timeline-node"><strong><span class="mono">C-003</span> Research agenda: what else can the instrument answer; robustness; scale-up</strong><p>Q4-Q6 promoted; detection floor = methodology centerpiece; D-014 uncertainty found unimplemented; nodes/&lt;node_id&gt; flagged as pre-multi-node breaking fix</p></div> <div class="timeline-node"><strong><span class="mono">C-004</span> Difficulty-graded scored workload suites; collect-more-per-run</strong><p>affine_mod_ladder_v1 adopted as ONE quarantined profile; rich-telemetry parsing (P2-009) prioritized ahead of it; examiner reframe adopted</p></div> <div class="timeline-node"><strong><span class="mono">C-005</span> Steelmanned research agenda + workload expansion</strong><p>31 tiered questions + kill list; jw_mixed_v1 starter suite specified (→ P2-012)</p></div> <div class="timeline-node"><strong><span class="mono">C-006</span> Session trace + orchestration meta-review of the six-stream parallel day</strong><p>13 attributed catches; integration-review step vindicated; skills deduplicated; operation-loop installed</p></div> <div class="timeline-node"><strong><span class="mono">C-007</span> Whole-project design/planning council (user-directed) + P2-013 fix design</strong><p>P2-013 re-ranked above 2M with raw-to-trace gate added in-stream; two-claim-track framing adopted; detection floor gets an owning Phase 4 gate; machine-state queue lanes; pre-2M contract amendments (P2-014)</p></div> <div class="timeline-node"><strong><span class="mono">C-008</span> Multi-stream hardware-prep session (4 streams, Opus directors + Codex volume), user-checkpointed mid-flight</strong><p>3.0.1 verdict replay_supported; P2-013 groups 1-4 (19/31 pins); 2K protocol v1 provisional; DOC-007 done; Slice 2O landed; ledgers v2 + calibration + wake-gap lessons folded into skills same-session</p></div> <div class="timeline-node"><strong><span class="mono">C-009</span> META-REVIEW of the orchestration system itself (user-directed): 2 blind Codex analyses vs Fable&#x27;s blind positions → conferral → SIGNED consensus</strong><p>Hybrid topology + lead stream-state table; foreground-wait orchestrators + STALLED-handback; heartbeat demoted to backstop; Codex up-stack (design freedom, schema drafts, lead-decision packets); docs single-writer end-state (run report = session record; council log = deliberation only; RUN_STATE = pointer; ledgers retire at integration WITH branch/hash pointer); retired-artifact pointer rule; codex-run patch queued; preflight gates (device inventory, quiet lock, provisional labels)</p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-08</h3><div class="timeline-node"><strong><span class="mono">C-010</span> Resume+merge session — first full run under the C-009 topology (pointer entry; full record in the resume-merge run report)</strong><p>Lead-driven pipelines validated (zero stalls, no subagent directors); B-14/B-15 wire pins overturned by lens review pre-hardware; fabricated-evidence defect caught at lead diff gate (B-44); Ed grants standing self-merge-with-review authority; final-head review rule adopted; PRs #8/#9/#10/#11 merged</p></div> <div class="timeline-node"><strong><span class="mono">C-011</span> Counter-review of the independent project critique (4 verification lenses + 5.5-high adjudication; full entry below)</strong><p>Critique findings adjudicated into mechanics: fail-closed campaign runner, counterbalanced order manifest, reducer honesty flags, claims ladder (D-037), P2-015 ranked before 2M; merged as PR #12</p></div> <div class="timeline-node"><strong><span class="mono">C-012</span> Site observatory stream (pointer entry; full record in run report <code>2026-07-08-site-observatory.md</code>) — dual-prior design round, 2 image-critique rounds, visual sign-off, counterreview, final-head gate</strong><p>Data-driven status frontend merged as PR #13; fail-closed parser honesty enforced (2 counterreview blockers fixed); P2-017 per-source stamps closed; image-heavy analysis routed to Codex as standing doctrine (Ed)</p></div> <div class="timeline-node"><strong><span class="mono">C-013</span> Lakebed deployment stream (pointer entry; full record in run report <code>2026-07-08-lakebed-deploy.md</code>) — 5.5 impl + 6 platform-constraint fix rounds + fresh counterreview</strong><p>Site live as a shareable capsule with a live GitHub freshness layer (fails soft); lead owns deploy/claim (no sandbox network); site regen+redeploy folded into the RUN_STATE end-of-work loop</p></div> <div class="timeline-node"><strong><span class="mono">C-014</span> Workload-suite science hardening (full entry below) — lead audit + scout + 3 design lenses + invited peer counterreview</strong><p>Q4-at-L3 gap closed via <code>q4_l3_shape_grid_v1</code> (4x3 + holdouts); P2-015 expanded to comparative MDE floors; jw_mixed common-shape stratum (C-W.1 was unfalsifiable); P2-010 split substrate/smoke, scored ladder deferred; two-quiet-window plan; analysis-plans contract (D-038); program restructure (D-039); two lead designs overturned by invited peer</p></div> <div class="timeline-node"><strong><span class="mono">C-015</span> Benchmark expansion council (full entry below) — reach lenses R1/R2 + design lenses E1/E2 + peer counterreview</strong><p>Suite architecture v2 (D-040: B×k bundles, one generic mechanism, per-item status model); interop direction (D-041: HumanEval-first imports, marker-shim energy layer, kill list); capability map landed in bank; R2 collect-now set spawned the window-a-capture stream; capstone stop-line + D-034 gate restated</p></div> <div class="timeline-node"><strong><span class="mono">C-016</span> Post-large-workload meta-reassessment (pointer entry; records: D-043, <code>~/.claude/skills/skill-usage-log.md</code>, run report addendum) — 4 analysts (council/decision/skill mining + cold-start derivability) + completeness critic, Workflow-orchestrated</strong><p>Supersession drift named as THE recurring unfolded failure mode (~70% of doc defects) → D-043 write-time + sweep-time discipline; operative merge-authority contradiction fixed; 5 skill divergences fixed; codex-delegation rewritten procedure-first; clean-machine derivability closed (scripts/codex-run committed + orchestration.md pointer map); §10 post-large-workload trigger now standing</p></div> <div class="timeline-node"><strong><span class="mono">C-017</span> Suite-build adjudication + implementation gates (full entry below) — Codex disposition draft + fresh adversarial round + lead calls; 11 unit lenses + 1 Opus outage substitute + 7-reviewer oversight + 3 final-head + integration</strong><p>37 amendments dispositioned → D-044..D-047; substrate/ladder/generators BUILT and merged (PRs #17/#18/#20/#19, suite 732); 3 lead live-only catches (refs, strict rollup, sampler namespace); oversight caught 2 validation holes pre-merge; PR #18 base-retarget slip recovered via #20</p></div> <div class="timeline-node"><strong><span class="mono">C-018</span> D-013 alignment-capture window fix (parallel session; full entry below)</strong><p>sampling_stopped stamped before alignment capture (PR #21: <code>255a7e6</code>, bookkeeping <code>c2e51b2</code>, merge <code>49c5b66</code>); suite 734; D-013 prose back-annotated to marker-bounded wording in the reassessment batch</p></div> <div class="timeline-node"><strong><span class="mono">C-019</span> Post-suite-build meta-reassessment (full entry below) — 4 analyst lanes (5.5-direction study over 43 invocations; calibration longitudinal; project status/value ranking; closure) + completeness critic</strong><p>Direction doctrine folded into codex-delegation skill (precedence/autonomy/FIX-N/production-gate clauses; model-version scoping rule pre-upgrade); D-013 prose back-annotated marker-bounded; shakedown gate added to P2-015; P2-025 adjacency + P1-008 elevation (incl. examiner acceptance-bar ask); pre-#21 corpus validity noted (dict-read-scale overhead, no re-reduction); watch items: integration-after-oversight, Opus A/B</p></div> <div class="timeline-node"><strong><span class="mono">C-020</span> STOP-AND-ANALYZE WHOLE PROJECT: technical + research merit debate (full entry below) — 69-agent Codex assessment workflow + 2 independent Fable position papers + recorded Fable-vs-Codex debate; owner-directed</strong><p>Merit verdict recorded (docs/reviews/2026-07-08-technical-merit-review.md); D-048 model-first split program + D-049 transfer-boundary accounting promoted; question ranking adjudicated (Q4→Q1 coupled #1, Token-Shape Null sustained #2, Q6 elevated #3, affine ladder = validity instrument); crossover prior corrected by arithmetic; cheap-validity priority set (bundle publication + external re-reduction first); repo-verified gaps: bundles unpublished, no LICENSE, D-033 strict-validation legacy bypass</p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-09</h3><div class="timeline-node"><strong><span class="mono">C-021</span> Advisor status-site live-depth refresh (pointer entry; D-051; run report <code>2026-07-09-advisor-status-site.md</code>)</strong><p>Static generated pages remain the audit fallback; Lakebed gets fail-soft live overlays from current GitHub markdown; Story page volatile counts removed; advisor cockpit expanded with attention, readiness, evidence, and claim-ceiling panels; gpt-5.5-high counterreview used before deploy</p></div> <div class="timeline-node"><strong><span class="mono">C-022</span> CP-5 resume session (pointer entry; run report <code>2026-07-09-cp5-resume.md</code> owns the full trace) — lead-driven, ~35 codex sessions: implementation, fix rounds, 12+ lenses/final-head passes, 2 integration reviews</strong><p>PRs #22..#28 merged (merge-gate shape held: lens→fix→lead live gate→fresh final-head→CI→merge); final-head layer caught 3 blockers + 7 should-fixes post-lens; CI merge-ref caught the one cross-branch interaction (#23 fixtures × #27 strict rules) no other layer could see; 1 lead prompt-defect (inferred-sidecar pin) caught and refixed; methodology synthesis + suite_next packet adjudicated (CP-6); D-047 sampler clause amended (fail-closed); stop card CLEARED; Window-A GO</p></div> <div class="timeline-node"><strong><span class="mono">C-023</span> Scientific-rigor review of the measurement suite, benchmark, and full question bank (user-directed; full record <code>docs/reviews/2026-07-09-scientific-rigor-review.md</code>) — 4 fresh 5.5 lenses (metrology, benchmark/stats, per-question bank audit, advisor simulation) + independent lead read + 1 bidirectional discussion round</strong><p>Verdict: strong provisional, advisor sign-off after a named all-software artifact list (error budget/P2-015 combined spec, analysis registry + multiplicity policy, canonical RQ registry + linter, frozen headline, contrast-level stats amendment, ordering executability, token-normalization contract); every blocker no-hardware-fixable; C5-1.1 blocker OVERTURNED in discussion (already contract-capped by C-014/D-037); ordering gap (C-015 promise vs manifest_order execution) elevated to pre-campaign; queue impact deferred to the step-2 planning session</p></div> <div class="timeline-node"><strong><span class="mono">C-024</span> Spec-fleshing wave 1 (pointer entry; run report <code>2026-07-09-spec-fleshing-wave1.md</code>) — 4 worktree streams (5.5 implement), 4 counterreview lenses, 3 fix rounds, 4 final-head + 1 tail-verification pass, integration review</strong><p>PRs #29..#32 merged (D-052..D-055 ratified: scope contract, contrast-level stats + registry, false-effect guard floor, RQ registry); R2&#x27;s estimator kill (percentile-UCB unidentifiable at n=10) was the session&#x27;s decisive catch; integration review caught 5 cross-stream seam drifts (S1/S2 written against pre-S3 contract text); P2-015-PREP (queue rank 0) closed; checkpoint-push cadence adopted mid-session (Ed)</p></div> <div class="timeline-node"><strong><span class="mono">C-025</span> Wave 2 — ultracode workflow build (pointer entry; run report <code>2026-07-09-spec-fleshing-wave2.md</code>) — 46-agent workflow (4 impl streams, 8 lenses, severity-tiered refuters) + 2 lead-driven reinforcement streams + 6 final-heads + tail verification + combined-ref check + integration review</strong><p>PRs #33..#38 merged (D-056..D-059 ratified: order policies + order_row, drift-is-a-bound + stable reason codes, token-normalization contract, claims-lint CI enforcement); refuter layer killed 10 findings pre-triage; final-heads caught 2 live-path defects (MLX position under rotation; linter false-negative regression); mutation testing debuted in the test-audit lens; combined-ref suite check validated the p2029 x p2030 strict-surface interaction pre-merge; suite 877</p></div> <div class="timeline-node"><strong><span class="mono">C-026</span> P2-034 broad campaign packs (pointer entry; run report <code>2026-07-09-p2034-broad-packs.md</code>) — design-round-first (memo ratified w/ 3 pins), single worktree stream, dual lenses, final-head CLEAN</strong><p>PR #39 merged; six packs, pack lint errors=0; compliance lens caught a char-level registry drift the linter cannot see (code-span nesting) + a scorer-leak + P2-022 structure flattening; executability lens caught the external-lab cold-start gap; pre-hardware campaign surface COMPLETE (every pre_hardware_preparable=fully row packed)</p></div> <div class="timeline-node"><strong><span class="mono">C-027</span> Whole-project council review with gpt-5.6-sol xhigh (first production session; 7 lenses: topdocs/rigor/stats/meta/reverse/arch/negspace + counterreview + independent Fable-tier final examiner; full record <code>docs/reviews/2026-07-09-c027-whole-project-review.md</code>)</strong><p>8 blocker clusters confirmed (token-denominator mislabel, superseded D-053 prose, RUN_STATE dual next-action, claim machinery unimplemented+unowned, empty D-050 manifest, four D-031 direct-to-main commits, evidence-integrity trio, protocol blockers); claim surfaces corrected same session; 14 follow-up queue rows + NV-GATE-2 additions to P2-005; D-060 proposed + D-061..D-063 accepted; counterreview reversed the lead twice (legacy-gate framing, restructure staging)</p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-22</h3><div class="timeline-node"><strong><span class="mono">C-031</span> D-078 P0 instrument-repair close-out (round-8/8b landing + §C-028 delta re-audit with 3 lenses / 11 refuter runs, round-9 FINAL confirmation, L1 adjudication, PR #79)</strong><p>Round-8b delta re-audit caught the understated-B_fiducial ClockStamp blocker two audited rounds missed; refuters killed 2 findings, narrowed 1, split 1 (lead-synthesized); CR9-1 adjudicated as registered limitation L1 + FLOOR-BIND-01; failure modes recorded (content-filter refuter kills -&gt; data-quality rephrase; bench-edit-during-enforced-scope false attribution; review-genre null-final recovery)</p></div></div> <div class="timeline-day"><h3 class="mono">2026-07-24</h3><div class="timeline-node"><strong><span class="mono">C-032</span> NEG-8 drift-gate estimand debate (Ed-directed pre-ratification cross-model debate; Sol xhigh peer vs lead ruling)</strong><p>Peer disagreed on inferential role (screen != stability proof) and was adjudicated CORRECT; Ed ratified the amended screen+budget design (option F full) with rigor-spiral + no-invented-physics guardrails; second recorded case of peer design judgment overturning a lead ruling pre-implementation</p></div></div><span class="source-chip" title="docs/council_log.md · commit 1af9f92"><span class="source-file">docs/<wbr>council_log.md</span><span class="source-commit">commit 1af9f92</span></span></section> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>RUN_STATE.md · commit 1af9f92 · docs/decision_log.md · commit 1af9f92 + uncommitted · docs/council_log.md · commit 1af9f92 · docs/run_reports/2026-07-18-claude-codex-pet-observer.md · commit 006eb47 · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/contracts/capstone_scope.md:19:paper leads with its linearity, additivity, detection-limit, and drift-control
docs/site/DRIFT.md:5:`dep_2I04CG6tQ4t0mzY7` from `c3e2647`, 2026-07-25):
docs/site/DRIFT.md:8:  window A (`window_metrologyA_20260731`, linearity_ramp 40/40 complete)
docs/site/DRIFT.md:10:  additivity 23/24 single-root, clean 2.25 ms bracket). BOTH
docs/site/DRIFT.md:32:The deployed capsule is still `dep_2I04CG6tQ4t0mzY7`, built from main
docs/site/DRIFT.md:87:council-log capsule redirect) as `dep_2I04CG6tQ4t0mzY7`; the capsule
docs/specs/c027/doc-008_state_kernel.md:471:| 5 | P2-019 → Q4 `blocked` | hard P2-006; `lead_only` | AP-1 + phase-2 plan → K |
docs/contracts/claims_ladder.md:70:  architecture, and quantization are hypothesis-generating for Q4. They are
docs/specs/c027/split-ap_ap-edit_amendments.md:133:> `(512,256)` and `(4096,512)` held-out in-grid corner predictions (interaction/additivity validation — both factor levels occur in the training grid, so neither is statistical extrapolation); prediction errors must clear the AP-1 floor gate. No extrapolation claim is available from this grid.
docs/site/council_log.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Council Log - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html" class="active">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#index">Index</a> <a href="#c-026-p2-034-broad-campaign-packs-2026-07-09">C-026: P2-034 broad campaign packs (2026-07-09)</a> <a href="#c-027-whole-project-council-review-with-gpt-5-6-sol-2026-07-09">C-027: Whole-project council review with gpt-5.6-sol (2026-07-09)</a> <a href="#index-row">Index row</a> <a href="#full-entry">Full entry</a> <a href="#c-028-c-027-adjudication-and-integration-arc-infrastructure-wave-prs-49-54-55-and-the-integration-window-2026-07-10-11">C-028: C-027 adjudication and integration arc — infrastructure wave, PRs 49/54/55, and the integration window (2026-07-10/11)</a> <a href="#c-031-d-078-p0-instrument-repair-close-out-session-round-8-landing-round-9-final-confirmation-sign-off-2026-07-22">C-031: D-078 P0 instrument-repair close-out session — round-8 landing, round-9 final confirmation, sign-off (2026-07-22)</a> <a href="#c-032-neg-8-estimand-debate-peer-disagreement-adopted-ed-ratification-2026-07-24">C-032: NEG-8 estimand debate — peer disagreement adopted, Ed ratification (2026-07-24)</a> <a href="#c-033-neg-8-screen-budget-audit-gauntlet-a-new-refuter-pairing-under-a-b-four-audit-rounds-pr-85-2026-07-24-25">C-033: NEG-8 screen+budget audit gauntlet — a new refuter pairing under A/B, four audit rounds, PR 85 (2026-07-24/25)</a></aside> <div class="doc-wrap doc-source-docs-council-log-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>docs/council_log.md</code></p> <div class="provenance-plate"><span class="source-chip" title="docs/council_log.md · commit 1af9f92"><span class="source-file">docs/<wbr>council_log.md</span><span class="source-commit">commit 1af9f92</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>Council Log</h1> <p>Chronicle of multi-model review councils: sessions where more than one model reviews, counterreviews, or votes on JouleWise work before it lands. Companion to <code>docs/decision_log.md</code> (which records WHAT was decided about the system; this file records HOW cross-model review reached it). One entry per council session; keep entries concise — positions, votes, resolutions, and follow-ups, not transcripts.</p> <p>Standing council roles (adopted C-001; process decision D-031):</p> <ul> <li><strong>Claude (lead/orchestrator)</strong> — scopes work, diagnoses live/hardware failures, runs adversarial review workflows, owns bookkeeping and the final merge decision, and is the only member that touches real hardware.</li> <li><strong>Codex / gpt-5.5 (peer implementer-reviewer)</strong> — implements against pinned specs, counterreviews findings on its own code, reverse-reviews Claude&#39;s commits and orchestration decisions, and is asked for design judgment explicitly (&quot;argue the tradeoffs before you code&quot;).</li> <li><strong>Opus subagents (fast reviewers)</strong> — parallel lower-level sweeps (commit hygiene, docs consistency, fixture audits) whose findings feed the discussion; cheap enough to run every session.</li> </ul> <p>(Amended 2026-07-08: the Opus fast-reviewer tier was dropped at C-006 after zero unique catches; lead-driven pipelines are the default per C-010; Ed granted standing self-merge-with-review authority in the C-010 addendum.)</p> <p>Disagreements are discussed in at most one or two rounds; unresolved disagreements are decided by the lead and recorded here with the dissent. Anything user-facing (push/merge/publish) follows the user&#39;s standing instructions.</p> <h2 id="index">Index</h2> <div class="table-scroll"><table> <thead> <tr> <th>ID</th> <th>Date</th> <th>Topic</th> <th>Outcome</th> </tr> </thead> <tbody><tr> <td>C-001</td> <td>2026-07-06</td> <td>Adopt review/counterreview between Claude and Codex (2H precedent)</td> <td>adopted; all 10 findings accepted, Codex improved the blocker fix design</td> </tr> <tr> <td>C-002</td> <td>2026-07-07</td> <td>Reverse review of the 9-commit vertical-slice series; push vs PR</td> <td>PR convention adopted; run_id renamed; P2-008 promoted; D-023 extended; sweep step added</td> </tr> <tr> <td>C-003</td> <td>2026-07-07</td> <td>Research agenda: what else can the instrument answer; robustness; scale-up</td> <td>Q4-Q6 promoted; detection floor = methodology centerpiece; D-014 uncertainty found unimplemented; nodes/<node_id> flagged as pre-multi-node breaking fix</td> </tr> <tr> <td>C-004</td> <td>2026-07-07</td> <td>Difficulty-graded scored workload suites; collect-more-per-run</td> <td>affine_mod_ladder_v1 adopted as ONE quarantined profile; rich-telemetry parsing (P2-009) prioritized ahead of it; examiner reframe adopted</td> </tr> <tr> <td>C-005</td> <td>2026-07-07</td> <td>Steelmanned research agenda + workload expansion</td> <td>31 tiered questions + kill list; jw_mixed_v1 starter suite specified (→ P2-012)</td> </tr> <tr> <td>C-006</td> <td>2026-07-07</td> <td>Session trace + orchestration meta-review of the six-stream parallel day</td> <td>13 attributed catches; integration-review step vindicated; skills deduplicated; operation-loop installed</td> </tr> <tr> <td>C-007</td> <td>2026-07-07</td> <td>Whole-project design/planning council (user-directed) + P2-013 fix design</td> <td>P2-013 re-ranked above 2M with raw-to-trace gate added in-stream; two-claim-track framing adopted; detection floor gets an owning Phase 4 gate; machine-state queue lanes; pre-2M contract amendments (P2-014)</td> </tr> <tr> <td>C-008</td> <td>2026-07-07</td> <td>Multi-stream hardware-prep session (4 streams, Opus directors + Codex volume), user-checkpointed mid-flight</td> <td>3.0.1 verdict replay_supported; P2-013 groups 1-4 (19/31 pins); 2K protocol v1 provisional; DOC-007 done; Slice 2O landed; ledgers v2 + calibration + wake-gap lessons folded into skills same-session</td> </tr> <tr> <td>C-009</td> <td>2026-07-07</td> <td>META-REVIEW of the orchestration system itself (user-directed): 2 blind Codex analyses vs Fable&#39;s blind positions → conferral → SIGNED consensus</td> <td>Hybrid topology + lead stream-state table; foreground-wait orchestrators + STALLED-handback; heartbeat demoted to backstop; Codex up-stack (design freedom, schema drafts, lead-decision packets); docs single-writer end-state (run report = session record; council log = deliberation only; RUN_STATE = pointer; ledgers retire at integration WITH branch/hash pointer); retired-artifact pointer rule; codex-run patch queued; preflight gates (device inventory, quiet lock, provisional labels)</td> </tr> <tr> <td>C-010</td> <td>2026-07-08</td> <td>Resume+merge session — first full run under the C-009 topology (pointer entry; full record in the resume-merge run report)</td> <td>Lead-driven pipelines validated (zero stalls, no subagent directors); B-14/B-15 wire pins overturned by lens review pre-hardware; fabricated-evidence defect caught at lead diff gate (B-44); Ed grants standing self-merge-with-review authority; final-head review rule adopted; PRs #8/#9/#10/#11 merged</td> </tr> <tr> <td>C-011</td> <td>2026-07-08</td> <td>Counter-review of the independent project critique (4 verification lenses + 5.5-high adjudication; full entry below)</td> <td>Critique findings adjudicated into mechanics: fail-closed campaign runner, counterbalanced order manifest, reducer honesty flags, claims ladder (D-037), P2-015 ranked before 2M; merged as PR #12</td> </tr> <tr> <td>C-012</td> <td>2026-07-08</td> <td>Site observatory stream (pointer entry; full record in run report <code>2026-07-08-site-observatory.md</code>) — dual-prior design round, 2 image-critique rounds, visual sign-off, counterreview, final-head gate</td> <td>Data-driven status frontend merged as PR #13; fail-closed parser honesty enforced (2 counterreview blockers fixed); P2-017 per-source stamps closed; image-heavy analysis routed to Codex as standing doctrine (Ed)</td> </tr> <tr> <td>C-013</td> <td>2026-07-08</td> <td>Lakebed deployment stream (pointer entry; full record in run report <code>2026-07-08-lakebed-deploy.md</code>) — 5.5 impl + 6 platform-constraint fix rounds + fresh counterreview</td> <td>Site live as a shareable capsule with a live GitHub freshness layer (fails soft); lead owns deploy/claim (no sandbox network); site regen+redeploy folded into the RUN_STATE end-of-work loop</td> </tr> <tr> <td>C-014</td> <td>2026-07-08</td> <td>Workload-suite science hardening (full entry below) — lead audit + scout + 3 design lenses + invited peer counterreview</td> <td>Q4-at-L3 gap closed via <code>q4_l3_shape_grid_v1</code> (4x3 + holdouts); P2-015 expanded to comparative MDE floors; jw_mixed common-shape stratum (C-W.1 was unfalsifiable); P2-010 split substrate/smoke, scored ladder deferred; two-quiet-window plan; analysis-plans contract (D-038); program restructure (D-039); two lead designs overturned by invited peer</td> </tr> <tr> <td>C-015</td> <td>2026-07-08</td> <td>Benchmark expansion council (full entry below) — reach lenses R1/R2 + design lenses E1/E2 + peer counterreview</td> <td>Suite architecture v2 (D-040: B×k bundles, one generic mechanism, per-item status model); interop direction (D-041: HumanEval-first imports, marker-shim energy layer, kill list); capability map landed in bank; R2 collect-now set spawned the window-a-capture stream; capstone stop-line + D-034 gate restated</td> </tr> <tr> <td>C-016</td> <td>2026-07-08</td> <td>Post-large-workload meta-reassessment (pointer entry; records: D-043, <code>~/.claude/skills/skill-usage-log.md</code>, run report addendum) — 4 analysts (council/decision/skill mining + cold-start derivability) + completeness critic, Workflow-orchestrated</td> <td>Supersession drift named as THE recurring unfolded failure mode (~70% of doc defects) → D-043 write-time + sweep-time discipline; operative merge-authority contradiction fixed; 5 skill divergences fixed; codex-delegation rewritten procedure-first; clean-machine derivability closed (scripts/codex-run committed + orchestration.md pointer map); §10 post-large-workload trigger now standing</td> </tr> <tr> <td>C-020</td> <td>2026-07-08</td> <td>STOP-AND-ANALYZE WHOLE PROJECT: technical + research merit debate (full entry below) — 69-agent Codex assessment workflow + 2 independent Fable position papers + recorded Fable-vs-Codex debate; owner-directed</td> <td>Merit verdict recorded (docs/reviews/2026-07-08-technical-merit-review.md); D-048 model-first split program + D-049 transfer-boundary accounting promoted; question ranking adjudicated (Q4→Q1 coupled #1, Token-Shape Null sustained #2, Q6 elevated #3, affine ladder = validity instrument); crossover prior corrected by arithmetic; cheap-validity priority set (bundle publication + external re-reduction first); repo-verified gaps: bundles unpublished, no LICENSE, D-033 strict-validation legacy bypass</td> </tr> <tr> <td>C-019</td> <td>2026-07-08</td> <td>Post-suite-build meta-reassessment (full entry below) — 4 analyst lanes (5.5-direction study over 43 invocations; calibration longitudinal; project status/value ranking; closure) + completeness critic</td> <td>Direction doctrine folded into codex-delegation skill (precedence/autonomy/FIX-N/production-gate clauses; model-version scoping rule pre-upgrade); D-013 prose back-annotated marker-bounded; shakedown gate added to P2-015; P2-025 adjacency + P1-008 elevation (incl. examiner acceptance-bar ask); pre-#21 corpus validity noted (dict-read-scale overhead, no re-reduction); watch items: integration-after-oversight, Opus A/B</td> </tr> <tr> <td>C-018</td> <td>2026-07-08</td> <td>D-013 alignment-capture window fix (parallel session; full entry below)</td> <td>sampling_stopped stamped before alignment capture (PR #21: <code>255a7e6</code>, bookkeeping <code>c2e51b2</code>, merge <code>49c5b66</code>); suite 734; D-013 prose back-annotated to marker-bounded wording in the reassessment batch</td> </tr> <tr> <td>C-017</td> <td>2026-07-08</td> <td>Suite-build adjudication + implementation gates (full entry below) — Codex disposition draft + fresh adversarial round + lead calls; 11 unit lenses + 1 Opus outage substitute + 7-reviewer oversight + 3 final-head + integration</td> <td>37 amendments dispositioned → D-044..D-047; substrate/ladder/generators BUILT and merged (PRs #17/#18/#20/#19, suite 732); 3 lead live-only catches (refs, strict rollup, sampler namespace); oversight caught 2 validation holes pre-merge; PR #18 base-retarget slip recovered via #20</td> </tr> <tr> <td>C-021</td> <td>2026-07-09</td> <td>Advisor status-site live-depth refresh (pointer entry; D-051; run report <code>2026-07-09-advisor-status-site.md</code>)</td> <td>Static generated pages remain the audit fallback; Lakebed gets fail-soft live overlays from current GitHub markdown; Story page volatile counts removed; advisor cockpit expanded with attention, readiness, evidence, and claim-ceiling panels; gpt-5.5-high counterreview used before deploy</td> </tr> <tr> <td>C-022</td> <td>2026-07-09</td> <td>CP-5 resume session (pointer entry; run report <code>2026-07-09-cp5-resume.md</code> owns the full trace) — lead-driven, ~35 codex sessions: implementation, fix rounds, 12+ lenses/final-head passes, 2 integration reviews</td> <td>PRs #22..#28 merged (merge-gate shape held: lens→fix→lead live gate→fresh final-head→CI→merge); final-head layer caught 3 blockers + 7 should-fixes post-lens; CI merge-ref caught the one cross-branch interaction (#23 fixtures × #27 strict rules) no other layer could see; 1 lead prompt-defect (inferred-sidecar pin) caught and refixed; methodology synthesis + suite_next packet adjudicated (CP-6); D-047 sampler clause amended (fail-closed); stop card CLEARED; Window-A GO</td> </tr> <tr> <td>C-023</td> <td>2026-07-09</td> <td>Scientific-rigor review of the measurement suite, benchmark, and full question bank (user-directed; full record <code>docs/reviews/2026-07-09-scientific-rigor-review.md</code>) — 4 fresh 5.5 lenses (metrology, benchmark/stats, per-question bank audit, advisor simulation) + independent lead read + 1 bidirectional discussion round</td> <td>Verdict: strong provisional, advisor sign-off after a named all-software artifact list (error budget/P2-015 combined spec, analysis registry + multiplicity policy, canonical RQ registry + linter, frozen headline, contrast-level stats amendment, ordering executability, token-normalization contract); every blocker no-hardware-fixable; C5-1.1 blocker OVERTURNED in discussion (already contract-capped by C-014/D-037); ordering gap (C-015 promise vs manifest_order execution) elevated to pre-campaign; queue impact deferred to the step-2 planning session</td> </tr> <tr> <td>C-024</td> <td>2026-07-09</td> <td>Spec-fleshing wave 1 (pointer entry; run report <code>2026-07-09-spec-fleshing-wave1.md</code>) — 4 worktree streams (5.5 implement), 4 counterreview lenses, 3 fix rounds, 4 final-head + 1 tail-verification pass, integration review</td> <td>PRs #29..#32 merged (D-052..D-055 ratified: scope contract, contrast-level stats + registry, false-effect guard floor, RQ registry); R2&#39;s estimator kill (percentile-UCB unidentifiable at n=10) was the session&#39;s decisive catch; integration review caught 5 cross-stream seam drifts (S1/S2 written against pre-S3 contract text); P2-015-PREP (queue rank 0) closed; checkpoint-push cadence adopted mid-session (Ed)</td> </tr> <tr> <td>C-025</td> <td>2026-07-09</td> <td>Wave 2 — ultracode workflow build (pointer entry; run report <code>2026-07-09-spec-fleshing-wave2.md</code>) — 46-agent workflow (4 impl streams, 8 lenses, severity-tiered refuters) + 2 lead-driven reinforcement streams + 6 final-heads + tail verification + combined-ref check + integration review</td> <td>PRs #33..#38 merged (D-056..D-059 ratified: order policies + order_row, drift-is-a-bound + stable reason codes, token-normalization contract, claims-lint CI enforcement); refuter layer killed 10 findings pre-triage; final-heads caught 2 live-path defects (MLX position under rotation; linter false-negative regression); mutation testing debuted in the test-audit lens; combined-ref suite check validated the p2029 x p2030 strict-surface interaction pre-merge; suite 877</td> </tr> <tr> <td>C-026</td> <td>2026-07-09</td> <td>P2-034 broad campaign packs (pointer entry; run report <code>2026-07-09-p2034-broad-packs.md</code>) — design-round-first (memo ratified w/ 3 pins), single worktree stream, dual lenses, final-head CLEAN</td> <td>PR #39 merged; six packs, pack lint errors=0; compliance lens caught a char-level registry drift the linter cannot see (code-span nesting) + a scorer-leak + P2-022 structure flattening; executability lens caught the external-lab cold-start gap; pre-hardware campaign surface COMPLETE (every pre_hardware_preparable=fully row packed)</td> </tr> <tr> <td>C-027</td> <td>2026-07-09</td> <td>Whole-project council review with gpt-5.6-sol xhigh (first production session; 7 lenses: topdocs/rigor/stats/meta/reverse/arch/negspace + counterreview + independent Fable-tier final examiner; full record <code>docs/reviews/2026-07-09-c027-whole-project-review.md</code>)</td> <td>8 blocker clusters confirmed (token-denominator mislabel, superseded D-053 prose, RUN_STATE dual next-action, claim machinery unimplemented+unowned, empty D-050 manifest, four D-031 direct-to-main commits, evidence-integrity trio, protocol blockers); claim surfaces corrected same session; 14 follow-up queue rows + NV-GATE-2 additions to P2-005; D-060 proposed + D-061..D-063 accepted; counterreview reversed the lead twice (legacy-gate framing, restructure staging)</td> </tr> <tr> <td>C-031</td> <td>2026-07-22</td> <td>D-078 P0 instrument-repair close-out (round-8/8b landing + §C-028 delta re-audit with 3 lenses / 11 refuter runs, round-9 FINAL confirmation, L1 adjudication, PR #79)</td> <td>Round-8b delta re-audit caught the understated-B_fiducial ClockStamp blocker two audited rounds missed; refuters killed 2 findings, narrowed 1, split 1 (lead-synthesized); CR9-1 adjudicated as registered limitation L1 + FLOOR-BIND-01; failure modes recorded (content-filter refuter kills -&gt; data-quality rephrase; bench-edit-during-enforced-scope false attribution; review-genre null-final recovery)</td> </tr> <tr> <td>C-032</td> <td>2026-07-24</td> <td>NEG-8 drift-gate estimand debate (Ed-directed pre-ratification cross-model debate; Sol xhigh peer vs lead ruling)</td> <td>Peer disagreed on inferential role (screen != stability proof) and was adjudicated CORRECT; Ed ratified the amended screen+budget design (option F full) with rigor-spiral + no-invented-physics guardrails; second recorded case of peer design judgment overturning a lead ruling pre-implementation</td> </tr> </tbody></table></div> <hr> <blockquote> <p><strong>Site view:</strong> the complete entry index appears above; the 20 older full entries are omitted from this page for capsule size. The complete log is the repository file <a href="https://github.com/mpmdw/JouleWise/blob/main/docs/council_log.md"><code>docs/council_log.md</code></a>.</p> </blockquote> <h2 id="c-026-p2-034-broad-campaign-packs-2026-07-09">C-026: P2-034 broad campaign packs (2026-07-09)</h2> <p>Pointer entry. Full narrative: <code>docs/run_reports/2026-07-09-p2034-broad-packs.md</code>. Design round ratified with three lead pins (unnamed second-family placeholder; runtime-held-constant = revision/build-family; smallest method-transfer suite first for C5-3.5); no new decision-log entries (pack content rides ratified contracts). Dissents: none.</p> <h2 id="c-027-whole-project-council-review-with-gpt-5-6-sol-2026-07-09">C-027: Whole-project council review with gpt-5.6-sol (2026-07-09)</h2> <p>Full record: <code>docs/reviews/2026-07-09-c027-whole-project-review.md</code> (disposition table for all ~80 lens findings, per-blocker verification lines, deliberation traces). Raw lens/counterreview/examiner outputs archived under <code>docs/reviews/c027/</code>. This entry records only the genuine deliberation.</p> <p>Participants: Fable 5 lead; Codex gpt-5.6-sol xhigh (FIRST production session of the new model; CLI upgraded 0.143.0→0.144.0 mid-session after the old CLI rejected the model) — 7 read-only lenses + 1 counterreview; 1 fresh-context Fable-tier final examiner. Scope declaration: all peer passes were STATIC-ONLY and single-model-family — execution behavior, SSH-path security, and licensing were reviewed by nobody and are recorded as open debts, not clean.</p> <p>Positions → resolutions (design-bearing only):</p> <ul> <li>Legacy-gates framing: lead draft said the six real bundles &quot;failed the advertised gates&quot;; counterreview showed D-037 binds from 2M onward, so the correct frame is legacy L1 + manual waivers — counterreview PREVAILED (the lead&#39;s framing would have manufactured an ex-post-protocol defense problem).</li> <li>Process-restructure staging: lead deferred the machine-readable state kernel; counterreview argued deferral leaves the demonstrated drift mode active and that policy generation is the harder half — counterreview PREVAILED; kernel is Stage 1 (D-063 records the reversal).</li> <li>Layer-drop rule: lead&#39;s &quot;3 applicable sessions, severity-weighted&quot; was attacked as reintroducing post-hoc discretion; adopted WITH the peer&#39;s mechanical-predicate construction (D-061).</li> <li>ARCH severity: undifferentiated blocker trio split into immediate (zero-window, P2-040) vs NVIDIA-gated (NV-GATE-2) per counterreview.</li> <li>Sequential sampling: fixed-n + explicit demotion adopted over both status quo and default alpha-spending (D-062); peer confirmed the demotion rule is coherent only with its four explicit clauses.</li> </ul> <p>Layer yields (C-027): lenses 8 confirmed blocker clusters + ~60 accepted findings, 0 verified false positives (blocker tier; lower tiers unaudited); counterreview 3 synthesis blockers (2 were LEAD errors — the only confirmed review errors this session were the lead&#39;s); final examiner 8 dropped/under-tiered findings + the validity-threats section, all adopted. Reverse-review layer indicted the lead&#39;s own conduct (empty D-050 manifest, four D-031 direct-to-main commits) — accepted in full, remedies in MET-001/RETRO-001.</p> <p>Dissents overridden: none unresolved. Lead notes for the record: ARC-1/2 remain hard acceptance gates at NVIDIA live promotion despite the severity downgrade.</p> <p>Calibration (model-version scoping): one promising 5.6-sol batch — 9/9 OK exits, ~28 verified file:line claims all accurate, unprompted premise correction (5 instances), the counterreview out-argued the lead twice. NOT a promotion; the pre-registered sealed A/B remains the gate before delegation-boundary changes.</p> <hr> <h2 id="index-row">Index row</h2> <p>| C-028 | 2026-07-09/11 | C-027 adjudication → integration arc under the Fable-lead / gpt-5.6-sol division of labor (this segment: infrastructure wave + PRs #49/#54/#55 + integration window) | PRs #49, #54, #55 merged mid-arc; held wave #50–#53, #56–#58 integration-reviewed and merged (SHA-guarded) after the integration tree caught 38 cross-stream failures pre-merge; follow-up PR #59 opened from the cross-stream review; refuter tier narrowed 2 blockers via contradictory verdicts; delta re-audits caught 2 fresh blockers in newly-reachable paths; claude-codex-report/v1 + codex-run-v3 + WRITE_SCOPE backstop + NEEDS_RULING adopted (D-064); ~57 recorded Sol invocations | | C-029 | 2026-07-11/12 | Agent-lane triple (SITE-01 / P2-049 / P2-028): three standard-tier Sol pipelines, per-stream lenses, lead bench adjudication of 5 blocker claims (2 confirmed, 1 partially refuted, 1 design ruling, 1 reproduce-first — refuters replaced by lead code-reading where cheaper); trace + calibration table in <code>docs/run_reports/2026-07-12-agent-lane-triple.md</code> §Process Trace Appendix (the ONE home; no full entry here) | PRs #61/#62/#63 opened at lead-gated heads; lead-gate unique catch: fix round&#39;s <code>succeeded</code>-only rule would refuse legitimate <code>capped</code> cells (FIX-14; third &quot;fix rounds introduce defects&quot; datum); implementer caught a stale kernel authority pointer (half-right — lead archaeology completed it, <code>507f600</code>); process defects logged: WRITE_SCOPE in-prompt requirement (3 rc=64), unintended ULTRA effort on all 13 invocations (config passthrough; TOOL-01), upstream outage killed 3 delta-audit attempts (re-audits owed pre-merge on #62/#63) | | C-030 | 2026-07-13 | Restart close (continuation of C-029; Ed-authorized merges): delta re-audits on #62/#63 finals + post-merge integration review, all explicit xhigh (effort fix held: 3 sessions ≈ 7.0M tokens vs the prior 13 ≈ 118M); two lead bench fixes with defect regressions; trace in <code>docs/run_reports/2026-07-13-restart-merge-deploy.md</code> (the ONE home; no full entry) | #61-#63 MERGED; delta-audit unique catch DRA-001 (equal-but-malformed identity hashes counted as identity evidence — fourth &quot;fix rounds introduce defects&quot; datum, this one surviving TWO earlier review layers); integration-review unique catch XSI-1 (installed-wheel CI ran only --help; now smokes both new fail-closed surfaces); lead-live layer: deploy ACCEPTED 854,349 B / routes 5/5 / freshness clear + cross-thread breakage fix (P2-028 kernel retirement vs gen_state fidelity tests, caught by the concurrent bridge thread&#39;s suite run); concurrent Claude↔Sol bridge landed same tree, lead-verified 8/8 protocol + 4/4 tests before commit; PAUSE: comprehensive whole-project audit declared next gate (Ed) | | C-031 | 2026-07-13 | Bridge v1 (Ed-directed): 3-round Fable&lt;-&gt;Sol design discussion held OVER the MCP bridge itself (thread 019f5a67-00f5); Sol out-designed the lead 3x (hard-block leases vs warn-only, path-level baseline manifests vs status digest, split event logs) — all accepted; 5 draft-choices lead-adjudicated; impl + 2 fix rounds + fresh lens + delta re-audit; full record <code>docs/run_reports/2026-07-13-bridge-v1.md</code> (the ONE home) | PR #64 MERGED: bridge-protocol/v1 contract + scripts/bridge (atomic hard-block leases — direct fix for the 2026-07-12 cross-thread collision — baselines, 4-verdict scope-check, thread registry) + adapter FAILED-synthesis; lens caught 4 blockers, delta re-audit caught 1 NEW blocker (malformed-override fail-open; FIFTH fix-rounds-inject-defects datum); audit-loop termination ruling: post-fix2 residue lead-verified directly; suite 1358 OK | | C-032 | 2026-07-13 | Bridge v1.1 (Ed-directed: &quot;fix up the bridge for maximum co-work&quot;): Sol xhigh design consult over the bridge (thread 019f5d1d-b681-7db1-8714-812fdd2f198b; 5 amendments accepted + v1 duplicate-sentinel adapter bug confirmed); ratified spec Sol-implemented; 3 lenses → 3 fix rounds → 3 delta re-audits, finding convergence 13→6→2→1; full record <code>docs/run_reports/2026-07-13-bridge-v11.md</code> (the ONE home; no full entry) | PR #65 MERGED <code>d285989</code> (Ed named the merge same session after the harness declined agent self-merge): discussion lane, receipt-anchored session-open/close wrappers (session.lock-serialized, write-only in v1.1), tolerant envelope, per-call reverse effort + echo, peer channels + bounded proposal diffs, one-home effort dedup; delta re-audits caught 6+2+1 fix-round findings (sixth/seventh &quot;fix rounds introduce defects&quot; data) incl. two corrections of the lead; suite 1387 OK; CI green on final head 8b96bd4 | | C-035 | 2026-07-15 | AXI spec-design phase (Ed: &quot;design as many specs as you can with help from sol&quot;; arc opened post-clearance with predeclared deliverable per WO-022 §5a): three parallel Sol spec pipelines (SA xhigh / SD high / SE xhigh), each author -&gt; fresh counterreview -&gt; fix round(s) -&gt; delta -&gt; lead termination; ~14 Sol sessions ≈ 71.2M tokens (est.); full trace in the 2026-07-14 run report §AXI spec-design phase | Specs landed <code>1464c93</code>/<code>d2bd5ee</code>/<code>3b5c4bf</code>: SA burst-decode contract (implementation-ready; honest frozen-arm goldens after the counterreview refuted byte-identical vs actual code; deterministic anti-top-up ledger), SD pair scorecard (four-option D-016 decision box for Ed; forced-continuation memory probe), SE six AP drafts (estimand demotion on AP-REASON-VARIANCE; union-bound + Markov-quantile floor guards; 21 PROVISIONAL cells with named triggers); 30+ counterreview findings fixed pre-landing; 3 benign lease-close artifacts pending Ed batch adjudication | | C-034 | 2026-07-14/15 | Audit fix-wave resume + close-out (Ed&#39;s AXI handoff §0.2 sequencing; full record <code>docs/run_reports/2026-07-14-audit-resume-axi.md</code>, the ONE home): per-order cadence Sol high/xhigh implement → fresh checker → fix rounds → lead gate; 28 Sol sessions ≈ 251M tokens (ARC HARD crossing recorded in the refreshed WO-022 receipt — gate-closing work, policy landed mid-arc); ULTRA comparison audit (intended, pre-declared) + xhigh integration review + Fable completeness critic + C-033 coherence council | S1 closed (WO-010 NEEDS_SCOPE grant, WO-011 checker-FAIL→fix→delta-PASS), S4 closed (WO-019 PASS-0-findings; WO-031 3-major fix round), WO-027 fix round, WO-021 xhigh 3-phase w/ 8a receipt + 4-record-loss BLOCKER migration, WO-022 verbatim landing; integration tree <code>impl/audit-integration</code>: 2 unique integration catches (capsule budget union breach; D-068 vacuous-green surfaces) + ULTRA&#39;s 2 blockers/20 findings triaged per Ed&#39;s substance-over-ceremony ruling (7 fixed <code>913a2a6</code>, 4 bench, 5 queued, rest dispositioned §8.5); D-043 closure (17 lines + 6 lead decision-log amendments); critic&#39;s 3 gaps closed same session; suite 1532 OK at <code>f8f0f92</code>; PR to main awaits Ed&#39;s adoption merge; 3 lease adjudications Ed-approved after classifier refused lead self-approval (correctly, all three times) | | C-033 | 2026-07-14 | AXI intake council (Ed-directed via <code>docs/axi-handoff.md</code> + Ed&#39;s batched §5 answers this session): short recorded Sol high read-only coherence review of drafted D-066..D-070 (outcomes Ed-directed, not re-decided; consult ran over the audited CLI path because the MCP server is unavailable in this headless session; prompt/response tracked at <code>docs/process_traces/2026-07-14-c033-axi-consult/</code>) | Sol verdict DISCUSSION: outcomes authorized, Ed&#39;s four D-067 amendments honored; 6 coherence corrections identified and ALL lead-accepted before commit: explicit supersession of the D-058 token-normalization Primary Metric clause (contract text assigned to S-A, keeping S-0 docs-only), dual-basis-capture bundle-state definition (successful idle-eligible request-level; nullable semantics preserved), D-032 gross-only phase semantics named, deploy convention re-attributed C-012→C-013, registry source homes corrected (C5-* bank vs C-023-<em>/RQ-</em> registry per D-055), <code>request_id</code> pinned to <code>events.jsonl</code> <code>metadata.request_id</code> with new-version-only reducer dispatch, D-064 duplicate/mismatched index rows cleaned; remaining deploy-instruction surfaces routed to WO-031 + S-0 | | C-037 | 2026-07-17 | Window-A execution + wrap arc (Ed: floors-first overnight -&gt; advisor deadline -&gt; site rebuild -&gt; exploratory breadth; full records: the two 2026-07-16/17 run reports, the ONE homes): four-failure shakedown story (stale-bundle reuse, wallpaper idle contamination caught by sentinel, 34.6ms trace-boundary bracket via two live-bundle triages, stale-lock exit-0 wart) -&gt; canonical PASS; 248-line/222-bundle floor campaign verified by 8-agent ultracode extraction; advisor brief + README-first site + Learn guide (Ed deployed); exploratory 9-bundle block; DSpark/DFlash feasibility confirmed; D-071..D-075 recorded | PRs #72-#75 merged under D-072 standing authority; delta re-audits caught blockers twice more (10th datum incl. lead-pinned formula defect); fold-in round&#39;s refusal caught a forced-report placeholder trace; scope enforcement caught the lead&#39;s own stray file (adjudicated benign); floors: request 0.527/0.052 J, phase 1.477/0.786 J, ABBA comparative w/ flagged tail drift; exploratory gross suite: OLMoE ~229 J vs Qwen3-4B ~362.8 J vs 122B ~1072 J (exploratory-labeled) | | C-036 | 2026-07-16 | Resumption + no-hardware batch (Ed: audits in a workflow + &quot;handle the merge yourself if all is well... get the project ready for my quiet mac&quot;; full record <code>docs/run_reports/2026-07-16-resumption-nohw-batch.md</code>, the ONE home): ultracode readiness workflow (4 Sol-high audits + severity-tiered refuters) BEFORE work selection; then 4 streams (SPLIT-AP xhigh contract tier, SITE-02 high standard, AXI-SB xhigh spike, AXI-SD Fable web-verification); every fix round delta-re-audited; three self-merges under Ed&#39;s in-session delegation, each with the full D-031-amended gate | PRs #67 (<code>7593259</code>, AXI-SA + CI portability fix after the audit caught red CI), #68 (<code>2778ed2</code>, SITE-02 — D2 step verified EXECUTED in the CI log), #69 (<code>9db4546</code>, SPLIT-AP freeze) merged; integration review 0 cross-stream defects, merged main 1630 OK; kernel closures 51→48 IDs; AXI-SB live probes (lead-run, B∈{2,4}) → verdict <code>supported</code>, Mac C5-2.2 leg mint staged on <code>impl/axi-sb</code> (effective on its merge); delta re-audit caught a LEAD-pinned predictor defect (8th fix-rounds-inject-defects datum, first lead-authored); AXI-SD memo: OLMo pair d_active 0.0016 + 8GB-fit may moot Option A&#39;s premise, Qwen3 pair confirmed-fails G10 (17.17 GB) |</p> <hr> <h2 id="full-entry">Full entry</h2> <h2>C-028: C-027 adjudication and integration arc — infrastructure wave, PRs #49/#54/#55, and the integration window (2026-07-10/11)</h2> <p>Full record: <code>docs/run_reports/2026-07-11-c028-continuation.md</code>; binding rulings: <code>docs/specs/c027/ADJUDICATION.md</code>. No tracked <code>docs/process_traces/</code> artifact is present in this checkout; the run report&#39;s aggregate invocation record is therefore the durable evidence available for this arc, and D-064 governs future tracked event streams. This limitation is recorded rather than repaired with an invented pointer. The arc&#39;s earlier segment (adjudication rounds, PRs #41–#48) is recorded in the CP-5/checkpoint records and stop-card history; this entry records the 2026-07-10/11 continuation.</p> <p>Participants: Fable lead; gpt-5.6-sol as implementer, reviewer, refuter, auditor, and design consultant across ~57 recorded invocations. The lead retained worktree/merge authority, every final diff gate, all live verification, and bookkeeping.</p> <p>Scope of this segment: PR #49 (NV-GATE-2 code-now + flake root-causes) merged <code>1b0f1f6</code> + <code>10e0ad2</code>; PR #54 (P2-041 vetted rebuild from the RED-tranche triage recipe, review + fix round + delta review) merged <code>69a3393</code>; PR #55 (P2-044 idle dependence / HAC / ESS, design-consult-first, review + fix round) merged <code>56d103e</code>. At the Ed-directed pause (stop card checkpoint #4 + amendments) PRs #50–#53 and #56–#58 stood open and lead-gated with the resume order pinned; after resume, the integration tree (<code>c028-integration</code> @ <code>190a0fc</code>, main post-#55 + 7 branches) caught 38 cross-stream failures, the fix round + cross-stream review cleared them, and the full wave merged SHA-guarded (#50, #51, #52, #53, #56, #57, #58 — P2-037 last), with final main verified green and content-identical to the reviewed tree; follow-up PR #59 (from the cross-stream review) is under review and DOC-008 rounds remain in flight. Delegation infrastructure landed on main: adapter, codex-run-v3, usage guard, scope backstop.</p> <p>Closeout amendment (2026-07-11): C-028 is <strong>CLOSED</strong>. PRs #41-#58 are merged; current main&#39;s canonical suite is 1,220 OK (<code>skipped=10</code>) and the corpus gate is 6/6. PR #59 remains open with a 1,224-test green worktree replay (<code>skipped=12</code>), and <code>impl/doc008-kernel</code> is pushed awaiting PR. These open follow-ups do not reopen the card. Every Window-A software gate and P0-003 are satisfied; quiet-machine execution with Ed remains deliberately separate from landed-software status. NVIDIA/Orin protocol pins remain PROVISIONAL pending live evidence.</p> <p>Layer structure: Sol implementation sessions (xhigh; 2 ultra for the p2041-vetted composition and the P2-037 engine) → review lenses (contract + semantics per stream) → severity-tiered refuters (2 per blocker) → independent post-hoc audits (P2-037) → delta re-audits after fix rounds → lead gates (live runs, arithmetic checks, final heads, CI) → cross-stream integration tree before each merge.</p> <p>Unique catches per layer (D-061 evaluation record):</p> <ul> <li><strong>Sol merge review:</strong> caught the lead&#39;s own merge-resolution error — the branch&#39;s updated P2-005 row silently lost by a whole-file <code>--theirs</code> checkout during the #49 conflict resolution; repaired as a proper 3-way merge (<code>13f6c9e</code>). Only layer to catch it.</li> <li><strong>Refuter tier:</strong> narrowed 2 blockers via CONTRADICTORY paired verdicts — P2-041 B1 (contract refuter confirmed, reachability refuter refuted the broad form → landed as the narrowed shared fail-closed cooldown verifier, <code>f2c4701</code>) and P2-037 F1 (design vs repro refuters split the same way → F1 narrowed before the fix round). The disagreement itself was the signal; neither single refuter would have produced the narrowed form.</li> <li><strong>Delta re-audits:</strong> 2 fresh blockers in paths newly reachable only after the fix round (P2-037 delta re-audit: blocker=2/should-fix=3), plus the recurring symlink pattern — cooldown provenance <code>Path.resolve</code> unwrapped against symlink loop/OSError, wrapped fail-closed with a cross-version regression test (<code>5f1f161</code>). Neither finding existed in the pre-fix tree; the re-audit layer is what sees post-fix reachability.</li> <li><strong>Lead gates:</strong> P2-044 F1 cadence arithmetic verified directly (all-intervals population; binding Qwen-r3 values asserted exactly: median 0.1199250625, ratio 1.0581313969 — <code>dc1ab95</code>); live NV-5 localhost gate 3/3 OK closing the open lead gate on #49 (<code>10e0ad2</code>); live doctor run. All three are lead-live-only — no static layer could produce them.</li> <li><strong>Integration tree:</strong> 38 pre-merge cross-stream test failures caught at the combined head, dominated by REPRO-002&#39;s fail-closed environment/inventory checks meeting post-cut fields from sibling streams. Zero of these were visible in any single stream&#39;s green suite.</li> <li><strong>Enforcement layer (scope backstop, live):</strong> 2 bytecode false-positive firings tuned same-day; NEEDS_SCOPE compliant stops ×3 (p2037 fix round, doc008 ×2) — each returning the correct paths where the lead had guessed wrong.</li> </ul> <p>Scope enforcement fired in production: two sessions (p2043-impl, p2044-fixround) exited SCOPE_VIOLATION with work preserved in evidence bundles, not landed; one wrapper crash (lead in-place edit of the installed runner mid-run) was recovered via a lead-authored recovery row rather than a mutated record — both behaviors are now ratified in D-064.</p> <p>Rough spend (from the two manifests + local usage accounting; estimates, not billing truth): 2 ultra sessions ≈ 100M tokens (p2041-vetted composition, P2-037 engine); 53 recorded xhigh invocations (14 v2-manifest + 37 v3-event-stream + 2 transition-era rows) — local 24h accounting shows 50 xhigh sessions ≈ 171M tokens; 2 high (both FAILED rc=1 resume attempts, work recovered in later sessions) ≈ 40M. Fable lead: ~1.8M generation / ~14.8M billed-ish / ~570M cache reads. Two v3 sessions (doc008-r3, pr59-review) still RUNNING at the manifest snapshot.</p> <p>Spend snapshot addendum (2026-07-11 ~20:00Z, <code>codex-usage</code> 24h window, arc-close truth for the table above; estimates, not billing): 59 Sol sessions / 330.6M tokens / ~17.5h session time — xhigh 55 ≈ 190.4M, ultra 2 ≈ 100.3M, high 2 ≈ 40.0M (both FAILED). Composition (measured from raw session records): ~97.4% of Sol input is cached, output ≈ 0.37% of volume. API-list-price equivalent (GPT-5.6-sol $5/$30, cached $0.50; Fable 5 $10/$50, cache reads $1): Sol ≈ $240, Fable ≈ $810 — combined ≈ $1,050 for the recorded arc; upper bound ≈ $2,300 counting all local Codex sessions (includes non-manifest sessions; resume rows may double-count). Note the inversion: Sol is ~180x the token volume but Fable is ~3.4x the cost — cache reads dominate the lead&#39;s footprint. Snapshot convention now standing in the council skill §Recording + instrumentation.</p> <p>Process artifacts adopted this arc (ratified as/alongside D-064):</p> <ul> <li><strong>claude-codex-report/v1</strong> — canonical machine-parsed session report envelope; run_finished rows record parse validity, finding counts, verification counts, scope flags.</li> <li><strong>codex-run-v3</strong> — append-only event-stream manifest (run_started/run_finished/run_consumed), retry-with-resume, lead-authored recovery rows on wrapper failure.</li> <li><strong>WRITE_SCOPE backstop</strong> — post-run diff vs declared scope; exit 77 + evidence bundle on violation; NEEDS_SCOPE prospective-only expansion (AGENTS.md precedence section, <code>9ca89cc</code>).</li> <li><strong>NEEDS_RULING</strong> — any blocking non-delegable decision early-returns a structured question instead of a guess (<code>31b3f5e</code>); usage guard + usage-pressure mode active.</li> <li><strong>Design-consult-by-default</strong> — Ed-prompted global-rule amendment; exercised for P2-044 (HAC/ESS design consult, <code>827df12</code>) before implementation.</li> </ul> <p>Dissents overridden: none unresolved. The P2-041 RED tranche (ultra round deleting P2-038/P2-040 wholesale) was not landed or argued — it was triaged per-file and rebuilt from main under three Ed-approved C rulings (<code>96e10bd</code>, <code>750f7d0</code>).</p> <p>Calibration note (model-version scoping, per C-027): the refuter contradictory-verdict pattern produced correct narrowings twice; the two scope violations and one thin-output ultra warning are the arc&#39;s recorded 5.6-sol failure modes. Sealed A/B remains the gate before any delegation-boundary change.</p> <h2 id="c-031-d-078-p0-instrument-repair-close-out-session-round-8-landing-round-9-final-confirmation-sign-off-2026-07-22">C-031: D-078 P0 instrument-repair close-out session — round-8 landing, round-9 final confirmation, sign-off (2026-07-22)</h2> <p>Shape: lead resumed the paused arc cold from scratchpad pointers; collected the checkpointed Sol round-8 fix wave; §C-028 delta re-audit (3 fresh read-only Sol lenses over a shared packet → 8 xhigh refuter verdicts, blockers 2 refuters with distinct lenses); Sol xhigh round-8b fix wave under enforced WRITE_SCOPE (one NEEDS_SCOPE early-return, lead-ruled, fixture fix applied at the bench); bounded 8b delta re-audit; lead full-suite gates (2081 → 2088 passed, 0 failures); commit <code>040ca3a</code>; round-9 FINAL confirmation (Sol xhigh review genre); CR9-1 adjudicated as registered limitation L1 per the loop-termination doctrine; close-out <code>debc6d2</code>; PR #79 opened for Ed-named merge.</p> <p>Layer catches (unique):</p> <ul> <li>Sol review lenses: A1 (v3 claim-eligibility contract divergence), B1 (ClockStamp physical-sanity gap → understated B_fiducial ~3 µs), C1/C2 (boundary float, OverflowError escape), C3/C4 (test-wiring gaps).</li> <li>Sol xhigh refuters: killed A2/B2 outright (both plausible, both wrong — A2&#39;s &quot;legacy records break&quot; was self-invalid synthetic-only; B2&#39;s stale-vs-invalid relabel would have broken a ratified distinction); narrowed C1 to a registered nit; split on A1 (contract-confirmed, reachability-refuted) — lead synthesis: pre-existing defense-in-depth hardening, not a round-8 regression.</li> <li>Round-9 confirmation: CR9-1 (floor artifacts self-attesting) — the only finding of the round, repro-backed, lead-reproduced at the bench.</li> <li>Lead unique: false-attribution triage of the 8b audit&#39;s two &quot;blockers&quot; (both were the lead&#39;s own authorized bench edits); the L1 adjudication.</li> </ul> <p>Failure modes recorded: (1) upstream cyber-content filter killed 3/8 refuters mid-run on adversarial phrasing (&quot;malformed/tamper/escape&quot;) — rephrasing as data-quality QA of our own instrument recovered all three (route: keep refuter briefs mechanism-neutral); (2) lead bench-edited the worktree while an enforced-scope Sol session ran in it → false SCOPE_VIOLATION attribution + resume-registry loss (rule: no lead edits in a tree with a live enforced-scope session); (3) the known xhigh review-genre null-final-message mode recurred on round 9; the documented bridge-resume recovery worked first try.</p> <p>Dissent recorded: the 8b delta auditor&#39;s should-fix (OverflowError normalization also reaching v1 replay error behavior) was overridden by lead ruling — frozen-replay doctrine protects computed semantics of parsable artifacts, not crash reproduction on impossible inputs; the reducer&#39;s structured-failure contract governs all protocols.</p> <h2 id="c-032-neg-8-estimand-debate-peer-disagreement-adopted-ed-ratification-2026-07-24">C-032: NEG-8 estimand debate — peer disagreement adopted, Ed ratification (2026-07-24)</h2> <p>Ed directed a formal cross-model debate on the clause-10 ruling before ratifying. Shape: lead position paper + explicit license and request to disagree; one xhigh peer round evaluating five design options plus a peer-proposed sixth; lead adjudication; plain-language synthesis to Ed; Ed ratified the amended design with recorded guardrails (decision log clause-10 addendum). Yield: the peer&#39;s structural correction (anomaly screen must not erase drift from the claim budget) was adopted — the second recorded case of invited peer design judgment beating the lead&#39;s ruling. The debate also surfaced one gap neither model had specced (drift-bound freshness horizon — prompted by Ed&#39;s own risk question) and one open science question (a7-vs-a5 prefill floor scatter, 3x). Calibration note: invited-disagreement debate briefs (steelman each option, demand failure modes + examiner view) produced markedly higher design yield than review-shaped prompts; adopt as the default shape for estimand/contract rulings.</p> <h2>C-033: NEG-8 screen+budget audit gauntlet — a new refuter pairing under A/B, four audit rounds, PR #85 (2026-07-24/25)</h2> <p>Shape: the Ed-ratified SCREEN + BUDGET wave (D-078 clause 10) was taken through four adversarial audit rounds (fresh read-only Sol per round; rounds 1–3 xhigh, round 4 high) with per-severity refuter tiers using a NEW pairing under evaluation — <strong>Opus-contract + Sol-execution distinct lenses</strong> (Ed-directed A/B; now the recorded default per the instrument-mix-authority memory). Three Sol fix rounds (xhigh, xhigh + a high alignment pass, high) plus lead bench fixes closed the findings; two lead-owned decision-log addenda were written at the bench between rounds. Commit stack on main(<code>125a48d</code>): <code>b120d07</code> wave → <code>69b65e5</code> addendum 2 → <code>ad75542</code> fix round 1 → <code>315810a</code> addendum 3 → <code>a5a7acf</code> capsule trim → <code>907ee58</code> fix round 2 → <code>dbf6339</code> fix round 3 → <code>19e15d9</code> assertion restore → <code>60b12af</code> capsule pagination → merged <code>c3e2647</code> (PR #85, 56 files, +6012/−439).</p> <p>Layer catches (unique):</p> <ul> <li><strong>Auditor (fresh Sol, per round):</strong> found real mechanisms in every round — round 1: estimand-dispatch downgrade (row shape selects the legacy gross-only evaluator), allowance fail-open (missing allowances silently become no allowance), anchor-gate bypass on the existing-bundle re-verdict path, and the refusal-registry gap (the authoritative registry test actually failed on <code>anchor_fallback_member_unusable</code>); round 2: coordinated-downgrade v2 (strip basis <em>and</em> the whole drift group together) and the mock-label seam (<code>telemetry_source=&quot;mock&quot;</code> defeats both dispatch and the anchor gate); round 3: TypeError on malformed basis values, telemetry-triangle downgrade into the frozen arm at the whole-window barrier, and loss of nonempty positive-path integration coverage; round 4: two omitted assertions in the replacement companion (nonempty affected-contrast set, <code>n == 5</code>). BUT it severity-inflated repeatedly — of 7 blocker-tier claims across rounds 1–2, refuter synthesis sustained 3–4 at tier (round 3 and round 4 produced no blockers at all: three should-fix, then one).</li> <li><strong>Opus-contract refuter (unique):</strong> F2 collapse (the &quot;broken frozen replay&quot; blocker rested on a misreading of the freshness addendum&#39;s scoping — landed as a documented superseded gross-only wire, not a code fix); F6 refutation (condition-level distinctness was already contract-discharged at the consumer boundary); G1 re-price (the full-strip variant is a subclass of registered limitation L1, whose closure is queued as FLOOR-BIND-01, not a fresh blocker); G2 re-price (the ratified non-mock carve-out plus D-030&#39;s strict/raw-evidence binding bound the exposure); blast-radius refutation of the auditor&#39;s proposed G2 fixture fix (strict validation binds backend raw evidence, so the naive fix breaks legitimate fixtures); <strong>A1 terminal-mock-bar gap — the session&#39;s best catch</strong>: an <em>honest</em> mock member could reach claim evidence with all mock-exempted barriers disabled, no attacker required; the NEG-8 sentinel route on round-3 F2 (the one route with no downstream catch); and the F3 fixture-fix refutation (a production-promoted fixture cannot be strict-valid — use a patch idiom instead).</li> <li><strong>Sol-execution refuter (unique):</strong> discovery of the coordinated-downgrade <em>variants</em> (strip the drift group and restore the headline floors and the record validates clean — reproduced on the repo fixture, gate <code>20.799350577898302 → 20.399350577898304</code>, exactly the fixture&#39;s 0.4 J allowance; asymmetric removal from the comparative record alone also validates clean); the G2A adjacent blocker (the reduce layer independently trusts metadata/summary mockness in the environment and CPU-admission barriers, so fresh re-reduction reproduces the forged exemption and strict stored-vs-fresh comparison is not a backstop); identification of the authoritative mockness source (custody-bound <code>config().hardware_target.telemetry_backend</code>, bound through <code>metadata.config_sha256</code>); the <code>mock:*</code> tagged-source class caveat (<code>axi_valid_burst</code> config <code>mock</code> vs summary <code>mock:target</code> — compare backend <em>class</em>, not raw strings); and every runnable probe, including the estimand-flip demonstration (<code>mock</code> → no refusals vs <code>powermetrics</code> → <code>whole_window_verdict_provenance_invalid</code> on identical evidence).</li> <li><strong>Lead (unique):</strong> the two D-078 clause-10 registry addenda (2 and 3) — component-7 anchor-fallback gate ruling derived from the a7-vs-a5 prefill-scatter root cause (a7&#39;s 11.85 J &quot;floor&quot; was one fallback-anchored member, r03; true floor ≈ 3.3–3.7 J), and the terminal mock bar; severity synthesis on the split verdicts (kept F4 at blocker priority on imminent-use grounds against the contract refuter&#39;s downgrade); the capsule shard-budget trim (<code>a5a7acf</code>) and the pagination ruling that followed (deterministic <code>D-NNN</code> pagination + D-076 artifact-cap redirects); the battery-flake adjudications; and the bench fixes (registry clause, the fixture metadata line that blocked Sol&#39;s canonical run, the round-4 assertion restore).</li> </ul> <p>Rough spend (estimates, not billing truth): the gauntlet proper (audit round 1 onward) recorded 11 distinct Sol wrapper invocations — 4 audits (3 xhigh, 1 high), 2 execution refuters (both high), 3 implementation rounds (xhigh; xhigh + a high alignment pass; high), 1 capsule session (xhigh), plus retry attempts on two of them; counting the same day&#39;s pre-audit wave, fold, fold2 and run-book sessions brings the day&#39;s Sol total to ~15. Four Opus agents: three contract/design refuters (~96k / 120k / 144k tokens) plus one dictated-fills drafting/verification agent (~115k) — the latter caught five material errors in the lead&#39;s own dictation of this entry, including the effort-tier discrepancy ruled on below. Lead orchestration on top. The <code>codex-usage</code> ledger reads all zeros for the 5h and 24h windows (&quot;local quota signal unavailable in referenced session logs&quot;) — the feed is suspected broken, so no token-volume snapshot is recorded this session.</p> <p>Verdict: <strong>the Opus-contract + Sol-execution pairing changed the triage outcome in every round it ran</strong> — it collapsed one blocker outright (F2), re-priced two (G1, G2), refuted two proposed fixes before they landed (G2 fixture, F3 fixture), and produced one blocker the auditor never saw (A1 terminal mock bar). The two lenses split on G1/G2 (Sol sustained both at blocker; Opus re-priced both) and the lead synthesized rather than majority-voted, per §C-028. Adopted as the default blocker-refuter shape; memory and skills to be updated by the lead.</p> <p>Dissent recorded: on F4 the lead overrode the contract refuter&#39;s downgrade and kept blocker priority, on the grounds that the anchor-fallback replay path was about to be exercised by the next window&#39;s re-verdict. On G1/G2 the lead implemented both fixes despite the contract lens&#39;s re-price, treating the re-price as a scope argument (what is <em>newly</em> broken) rather than a licence to defer.</p> <p>Calibration note: the auditor layer&#39;s yield is real but its severity calibration is not — four consecutive rounds produced findings worth fixing while its blocker tier held at roughly half strength. The refuter tier is what converts that into correct triage; running a single-lens refuter would have inherited the inflation.</p> <p>Effort-tier ruling (lead, flagged by the drafting agent&#39;s verification pass): the execution refuters ran at <code>high</code>, not the adversarial-review skill&#39;s <code>xhigh</code> default — deliberately in round 1 (Ed&#39;s A/B spec named &quot;sol high&quot;) and carried into round 2 for comparability. The A/B verdict therefore stands on high-tier refuters, which is the STRONGER form of the result: paired distinct-lens refuters at high changed triage outcomes that single-lens xhigh refuters have historically missed. Ruling: in the paired-lens shape, <code>high</code> is the default refuter tier; reserve <code>xhigh</code> for single-refuter verification or judgment-dense standalone audits. The lead will amend the adversarial-review skill&#39;s effort note accordingly.</p> <p>Scorecard (dispositions per docs/orchestration.md): 20 findings raised across 4 audit rounds incl. refuter adjacents. Accepted-and-fixed in PR #85: 13 (r1 F1/F3/F4/F5/F7; r2 G1/G2/G3 + adjacent A1 terminal mock bar; r3 F1/F2/F3; r4 F1). Re-priced by refuters before fixing: 4 of those (r1 F4 blocker→should-fix; r2 G1/G2 blocker→should-fix; r1 F2 blocker→docs-only, landed as contract clarification). Rejected / non-obligating: 2 (r1 F6 contract-refuted; r2-A2 traced not-reachable, defensive comment only). Queued: 4 → kernel row CUSTODY-HARDEN-01 (G2A reduce-layer label trust, drift-bound seal authentication, dead no-freshness accommodation, artifact_schema_invalid mislabel); full-strip custody discrimination remains inside pre-existing FLOOR-BIND-01/L1. Owners: all fixed items closed at merge c3e2647 (lead-verified); queued items owned by the kernel rows named above; no open finding without an owner.</p> </div> </div> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>docs/council_log.md · commit 1af9f92 · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/contracts/analysis_plans.md:88:- Capped `long_short` cells are excluded from prompt-slope and rank claims
docs/contracts/analysis_plans.md:106:### AP-1: Q4 fixed+marginal grid fit
docs/contracts/analysis_plans.md:110:| Plan ID / RQ consumer | AP-1 / Q4 fixed-vs-marginal energy model; feeds Q5 rank rules and Phase 4 F9 (C-014). |
docs/contracts/analysis_plans.md:111:| family_id | FAM-Q4-GRID-MODEL |
docs/contracts/analysis_plans.md:114:| multiplicity_rule | Holm within FAM-Q4-GRID-MODEL across confirmatory fixed/prompt/decode contrasts and holdout pass/fail claims; linear/log sensitivity terms are secondary unless frozen as primary before execution. |
docs/contracts/analysis_plans.md:118:| Inclusion/exclusion + quality-flag waiver rules | Strict-valid bundles only; D-014 quality flags excluded unless the report names and justifies a waiver; capped cells are excluded from prompt-slope/rank claims unless realized prompt lengths match. |
docs/contracts/analysis_plans.md:123:| Holdout cells (L3 only) | `(512,256)` and `(4096,512)` held-out in-grid corner predictions (interaction/additivity validation — both factor levels occur in the training grid, so neither is statistical extrapolation); prediction errors must clear the AP-1 floor gate. No extrapolation claim is available from this grid. |
docs/contracts/analysis_plans.md:132:| Plan ID / RQ consumer | AP-2 / Slice 2M qualitative prefill/decode asymmetry; supports Q4 substrate only (C-014). |
docs/council_log.md:47:| C-003 | 2026-07-07 | Research agenda: what else can the instrument answer; robustness; scale-up | Q4-Q6 promoted; detection floor = methodology centerpiece; D-014 uncertainty found unimplemented; nodes/<node_id> flagged as pre-multi-node breaking fix |
docs/council_log.md:58:| C-014 | 2026-07-08 | Workload-suite science hardening (full entry below) — lead audit + scout + 3 design lenses + invited peer counterreview | Q4-at-L3 gap closed via `q4_l3_shape_grid_v1` (4x3 + holdouts); P2-015 expanded to comparative MDE floors; jw_mixed common-shape stratum (C-W.1 was unfalsifiable); P2-010 split substrate/smoke, scored ladder deferred; two-quiet-window plan; analysis-plans contract (D-038); program restructure (D-039); two lead designs overturned by invited peer |
docs/council_log.md:61:| C-020 | 2026-07-08 | STOP-AND-ANALYZE WHOLE PROJECT: technical + research merit debate (full entry below) — 69-agent Codex assessment workflow + 2 independent Fable position papers + recorded Fable-vs-Codex debate; owner-directed | Merit verdict recorded (docs/reviews/2026-07-08-technical-merit-review.md); D-048 model-first split program + D-049 transfer-boundary accounting promoted; question ranking adjudicated (Q4→Q1 coupled #1, Token-Shape Null sustained #2, Q6 elevated #3, affine ladder = validity instrument); crossover prior corrected by arithmetic; cheap-validity priority set (bundle publication + external re-reduction first); repo-verified gaps: bundles unpublished, no LICENSE, D-033 strict-validation legacy bypass |
docs/council_log.md:160:- Key outputs: Codex's fixed-vs-marginal energy model (adopted as Q4;
docs/council_log.md:172:- Resolutions: promote Q4-Q6; queue D-014 implementation as the highest
docs/council_log.md:237:  the unified-memory story; the fixed-vs-marginal model (Q4) as the bridge
docs/council_log.md:745:    to optional. Q4 phrased as fixed-vs-marginal workload structure (not a
docs/council_log.md:783:- **Q4/Q5 promotion (PP3): strategist and project-examiner converged
docs/council_log.md:1006:Convergent blockers (lead + all three lenses independently): Q4
docs/council_log.md:1014:consumers — Q4-Q6 had NO Phase 4 figure/claims-index consumers, P2-010
docs/council_log.md:1027:lead adopted. POSITION REVERSAL. (4) Q4 grid: lead proposed 3x3; peer
docs/council_log.md:1251:- D1 question ranking: coupled Q4→Q1 (compositional prediction +
docs/council_log.md:1526:| C-039 | 2026-07-28 | Mint-implementation session (Ed: resume per RUN_STATE, then "merge on green + start the mint consult"; magistrate topology; full record `docs/run_reports/2026-07-28-floor-mint-implementation.md`, the ONE home): PR #87 gauntlet (2 Sol xhigh lenses + 5 Sol high refuters + 1 Opus contract refuter, lieutenant-directed), E4 fix + CLEAN delta re-audit, D-081 parser ruling (Ed, async question), Sol xhigh mint design consult (3 DISAGREEs sustained -> D-082), 7-stage xhigh implementation, suite-pruning consult (0 removals clear D-061) | PR #87 MERGED `058c918`; `impl/mint-tool` pushed unmerged (review owed); C1 SPLIT (Sol nit vs Opus should-fix) magistrate-synthesized to should-fix, closed via ratified Q4; 5 broken-wake incidents -> tracked-poll pattern folded to codex-delegation; lieutenant self-flagged 2 retracted fabricated verdict narrations (mechanism removed); concurrent-session force-push anomaly flagged to Ed; **ADDENDUM at the end of this file** records the 2026-07-29/30 continuation (FIX-6..9 gauntlet, three cold gates with paired Opus contract-lens refuters, mint #1, the 7B floor window; rulings D-083..D-088; D-088 recorded in the same-day close-out); **ADDENDUM II** records the 2026-07-30/31 escalation consults (cooldown-join design consult → D5-J/D-089; contrast-window recovery consult, the first trigger firing inside a measurement window) |
docs/council_log.md:2142:  Overall verdict **FAIL** (Q1 FAIL, Q2 FAIL, Q3 PASS-WITH-CONCERN, Q4/Q5/Q6
docs/site/decision_log_archive_1.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Decision Log — Archive 1 - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html" class="active">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#how-to-use-this-log">How To Use This Log</a> <a href="#index">Index</a> <a href="#d-073-d-016-device-list-amendment-mac-3080-ti-primary-fleet-12-gib-cap">D-073: D-016 device-list amendment — Mac + 3080 Ti primary fleet, 12 GiB cap</a> <a href="#d-074-conditional-qwen3-4b-primary-repin-olmo-1b-conversion-spike-authorized">D-074: Conditional Qwen3-4B primary repin + OLMo-1B conversion spike authorized</a> <a href="#d-075-extension-axis-intake-ranked-fold-in-without-new-thesis-proliferation">D-075: Extension-axis intake — ranked fold-in without new thesis proliferation</a> <a href="#d-076-site-capacity-right-sizing-aud-wo-039-review-measured-first-budgets">D-076: Site capacity right-sizing (AUD-WO-039 review) — measured-first budgets</a> <a href="#d-077-environment-guard-idle-admission-and-cooldown-v2">D-077: Environment guard, idle admission, and cooldown v2</a></aside> <div class="doc-wrap doc-source-docs-decision-log-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>docs/decision_log.md</code></p> <nav class="doc-meta" aria-label="Decision log parts"><span>Decision log parts:</span> <a href="decision_log.html">Recent</a> · <strong aria-current="page">Archive 1</strong></nav> <div class="provenance-plate"><span class="source-chip" title="docs/decision_log.md · commit 1af9f92 + uncommitted"><span class="source-file">docs/<wbr>decision_log.md</span><span class="source-commit">commit 1af9f92 + uncommitted</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>Decision Log</h1> <p>This is the canonical record of design decisions for JouleWise. Every decision that binds later work, trades off real alternatives, or would otherwise need to be re-derived by a future agent gets an entry here.</p> <h2 id="how-to-use-this-log">How To Use This Log</h2> <ul> <li>Before implementing anything non-trivial, check whether a decision here already covers it. Do not silently re-decide settled questions.</li> <li>When you make a new decision of this kind during a run, add an entry, link it from the run report, and reference its ID (<code>D-NNN</code>) in the code review or doc that applies it.</li> <li>Statuses: <code>accepted</code> (binding until revisited), <code>open</code> (criteria defined, evidence pending), <code>proposed</code> (recorded, awaiting Ed&#39;s ratification), <code>superseded by D-NNN</code>.</li> <li>Every entry must include Options Considered and Considerations. A decision without recorded alternatives is not auditable.</li> <li>Revisit triggers are part of the contract: when a trigger fires, the decision must be re-examined, not quietly worked around.</li> </ul> <h2 id="index">Index</h2> <div class="table-scroll"><table> <thead> <tr> <th>ID</th> <th>Title</th> <th>Status</th> </tr> </thead> <tbody><tr> <td>D-001</td> <td>Run bundles store normalized <code>config.json</code>, not YAML</td> <td>accepted</td> </tr> <tr> <td>D-002</td> <td>Telemetry sampling via subprocess + file, no controller threading</td> <td>accepted</td> </tr> <tr> <td>D-003</td> <td>Timestamp and clock-alignment policy</td> <td>accepted</td> </tr> <tr> <td>D-004</td> <td><code>powermetrics</code> privilege workflow</td> <td>accepted</td> </tr> <tr> <td>D-005</td> <td>One bundle per repetition, grouped by experiment manifest</td> <td>accepted</td> </tr> <tr> <td>D-006</td> <td>Dashboard v1 is a static HTML report generator</td> <td>accepted</td> </tr> <tr> <td>D-007</td> <td>YAML config input is deferred</td> <td>accepted</td> </tr> <tr> <td>D-008</td> <td>Split runs arrive via schema v0.2 (<code>run_kind</code> + <code>split_plan</code>)</td> <td>accepted</td> </tr> <tr> <td>D-009</td> <td>Dependency policy: stdlib core, optional extras</td> <td>accepted</td> </tr> <tr> <td>D-010</td> <td>Run ID scheme</td> <td>accepted</td> </tr> <tr> <td>D-011</td> <td><code>summary_metrics.json</code> is the bundle completion marker</td> <td>accepted</td> </tr> <tr> <td>D-012</td> <td>Failure-reason to run-status mapping</td> <td>accepted</td> </tr> <tr> <td>D-013</td> <td>Controller-as-DUT mitigation for Mac-local runs</td> <td>accepted</td> </tr> <tr> <td>D-014</td> <td>Statistical protocol for repeated runs</td> <td>accepted</td> </tr> <tr> <td>D-015</td> <td>Split-mechanism priority and same-runtime rule</td> <td>accepted</td> </tr> <tr> <td>D-016</td> <td>Benchmark model selection</td> <td>open (provisional small-model pick 2026-07-06; opens 2G only)</td> </tr> <tr> <td>D-017</td> <td>CI scope</td> <td>accepted</td> </tr> <tr> <td>D-018</td> <td>Per-backend <code>power_w</code> definition and rail policy</td> <td>accepted</td> </tr> <tr> <td>D-019</td> <td>Mock adapters use simulated time via an injectable clock</td> <td>accepted</td> </tr> <tr> <td>D-020</td> <td>CLI binds <code>FakeClock</code> for all-mock runs, <code>SystemClock</code> otherwise</td> <td>accepted</td> </tr> <tr> <td>D-021</td> <td>Controller flushes <code>events.jsonl</code> before the reduce stage</td> <td>accepted</td> </tr> <tr> <td>D-022</td> <td>Auto-generated run-ID suffix is config-hash-derived, not random</td> <td>accepted</td> </tr> <tr> <td>D-023</td> <td>Per-item phase status lives solely in the exit checklists</td> <td>accepted</td> </tr> <tr> <td>D-024</td> <td>Adapters receive a <code>RunContext</code>, not piecemeal parameters</td> <td>accepted; implemented (2N.1, 2026-07-06)</td> </tr> <tr> <td>D-025</td> <td>One shared bundle read layer for reducer, report, validation, and aggregation</td> <td>accepted; implemented (2N.8, 2026-07-06)</td> </tr> <tr> <td>D-026</td> <td>Measured window is bounded by sampling-active marker events</td> <td>accepted</td> </tr> <tr> <td>D-027</td> <td>Per-rail rows must share per-sample timestamps; misalignment is a structured failure</td> <td>accepted</td> </tr> <tr> <td>D-028</td> <td><code>reduce</code> verb rewrites <code>summary_metrics.json</code> in place (the one sanctioned post-finalize mutation)</td> <td>accepted</td> </tr> <tr> <td>D-029</td> <td>Config schema declares nullable optionals; serialization (and config hashes) unchanged</td> <td>accepted</td> </tr> <tr> <td>D-030</td> <td><code>validate-bundle</code> stays structural by default; <code>--strict</code> adds raw-evidence checks</td> <td>accepted</td> </tr> <tr> <td>D-031</td> <td>Multi-model council review; PR convention for multi-commit sessions (merge authority amended by C-010); D-023 extension + end-of-session consistency sweep</td> <td>accepted</td> </tr> <tr> <td>D-032</td> <td><code>phase_energy_j</code> is gross-only in summary v0.1</td> <td>accepted</td> </tr> <tr> <td>D-033</td> <td>Prompt-content provenance is recorded per run bundle</td> <td>accepted</td> </tr> <tr> <td>D-034</td> <td>Slice 2O owns the workload program after 2M and 3.0.1; implementation lane reopened by D-042</td> <td>accepted</td> </tr> <tr> <td>D-035</td> <td>Replay claims require fresh-process (subprocess-per-stage) isolation</td> <td>accepted</td> </tr> <tr> <td>D-036</td> <td>Spike verdict codes derive from measured data, never hardcoded</td> <td>accepted</td> </tr> <tr> <td>D-037</td> <td>Claims ladder (L0-L4) binds reader-facing claim language from 2M onward</td> <td>accepted</td> </tr> <tr> <td>D-038</td> <td>Analysis plans bind L2/L3 claims to pre-registered comparison rows</td> <td>accepted</td> </tr> <tr> <td>D-039</td> <td>Workload program v2: substrate first, identification before scale; pre-Window-A allowlist superseded by D-041/D-042</td> <td>accepted</td> </tr> <tr> <td>D-040</td> <td>Suite architecture v2: generic suite mechanism, bundle-level replication</td> <td>accepted</td> </tr> <tr> <td>D-041</td> <td>Benchmark interop via frozen-subset imports and marker-shim energy layer; interop lane remains post-2M + post-P2-010a</td> <td>accepted</td> </tr> <tr> <td>D-042</td> <td>D-034 implementation lane reopened; suite build may proceed pre-2M</td> <td>accepted</td> </tr> <tr> <td>D-043</td> <td>Supersession-closure discipline</td> <td>accepted</td> </tr> <tr> <td>D-044</td> <td>Suite config identity: omission-serialized ref + effective-manifest hash</td> <td>accepted</td> </tr> <tr> <td>D-045</td> <td>Suite substrate execution semantics (run_suite, statuses, per-item outputs)</td> <td>accepted</td> </tr> <tr> <td>D-046</td> <td>AP-6 sentinel delivery is ids-native BOS-less at literal equal shape</td> <td>accepted</td> </tr> <tr> <td>D-047</td> <td>Affine ladder pins: level set, smoke sizing, gate denominators</td> <td>accepted</td> </tr> <tr> <td>D-048</td> <td>Split program is model-first: pre-registered compositional prediction before split runs</td> <td>accepted</td> </tr> <tr> <td>D-049</td> <td>Split transfer-energy boundary accounting on discrete-GPU ends</td> <td>accepted</td> </tr> <tr> <td>D-050</td> <td>Active stop cards and process-trace manifests</td> <td>accepted</td> </tr> <tr> <td>D-051</td> <td>Advisor status site uses source-derived static pages plus fail-soft live GitHub overlays</td> <td>accepted</td> </tr> <tr> <td>D-052</td> <td>Capstone scope contract: frozen umbrella headline and contribution ladder</td> <td>accepted</td> </tr> <tr> <td>D-053</td> <td>Contrast-level statistical inference and the frozen analysis registry</td> <td>accepted</td> </tr> <tr> <td>D-054</td> <td>False-effect guard floor and unknown-term claim-ceiling policy</td> <td>accepted</td> </tr> <tr> <td>D-055</td> <td>Research-question registry is the canonical live index</td> <td>accepted</td> </tr> <tr> <td>D-056</td> <td>Suite order policies and order_row provenance</td> <td>accepted</td> </tr> <tr> <td>D-057</td> <td>Uncertainty terms: drift is a bound; stable claim-gate reason codes</td> <td>accepted</td> </tr> <tr> <td>D-058</td> <td>Token-normalization and stack-identity contract adopted</td> <td>accepted</td> </tr> <tr> <td>D-059</td> <td>Claims-lint mechanical enforcement in CI</td> <td>accepted</td> </tr> <tr> <td>D-060</td> <td>Depth-before-breadth stop line</td> <td>accepted (ratified 2026-07-10)</td> </tr> <tr> <td>D-061</td> <td>Review-layer evaluation rule v2</td> <td>accepted</td> </tr> <tr> <td>D-062</td> <td>Confirmatory sampling policy (fixed n, demotion)</td> <td>accepted</td> </tr> <tr> <td>D-063</td> <td>Process architecture v2 (state kernel first)</td> <td>accepted</td> </tr> <tr> <td>D-064</td> <td>Delegated-invocation compliance surface: tracked per-session JSONL event stream, canonical report envelope, enforced write scope</td> <td>accepted</td> </tr> <tr> <td>D-065</td> <td>bridge-protocol/v1.1 — co-work lane, session wrappers, tolerant envelope</td> <td>accepted</td> </tr> <tr> <td>D-066</td> <td>Scoped spec-freeze override for the AXI extension agenda (Ed override)</td> <td>accepted</td> </tr> <tr> <td>D-067</td> <td>Idle reporting basis — gross headline; idle-subtracted is a labeled within-device secondary view</td> <td>accepted</td> </tr> <tr> <td>D-068</td> <td>Site deployment is Ed-manual; sessions end with a drift report, never a deploy</td> <td>accepted</td> </tr> <tr> <td>D-069</td> <td>Advisor-doc alignment (stream S-0) is sanctioned front-facing work</td> <td>accepted</td> </tr> <tr> <td>D-070</td> <td>Architectural-axes extension agenda (AXI): scope, claim posture, batch-axis rulings</td> <td>accepted</td> </tr> <tr> <td>D-071</td> <td>G10 memory-fit rule ratified (axi-sd-memory-fit-shape-v1); device-list review opened</td> <td>accepted</td> </tr> <tr> <td>D-072</td> <td>Standing self-merge-with-full-gate authority (gh merges included)</td> <td>accepted</td> </tr> <tr> <td><a href="decision_log_archive_1.html#d-073">D-073</a></td> <td>D-016 device-list amendment: Mac + 3080 Ti primary fleet, 12 GiB cap</td> <td>accepted</td> </tr> <tr> <td><a href="decision_log_archive_1.html#d-074">D-074</a></td> <td>Conditional Qwen3-4B primary repin + OLMo-1B conversion spike authorized</td> <td>accepted</td> </tr> <tr> <td><a href="decision_log_archive_1.html#d-075">D-075</a></td> <td>Extension-axis intake: ranked fold-in without new thesis proliferation</td> <td>accepted</td> </tr> <tr> <td><a href="decision_log_archive_1.html#d-076">D-076</a></td> <td>Site capacity right-sizing (AUD-WO-039 review): measured-first budgets</td> <td>accepted</td> </tr> <tr> <td><a href="decision_log_archive_1.html#d-077">D-077</a></td> <td>Environment guard, idle admission, and cooldown v2</td> <td>accepted</td> </tr> <tr> <td><a href="decision_log.html#d-078">D-078</a></td> <td>Soundness gate: no claim-bearing extraction from time-anchor-defective powermetrics corpora</td> <td>accepted; operative under Ed&#39;s direction through the full repair arc (close-out cap explicitly Ed-ratified 2026-07-22; original-text ratification rides PR #79 review)</td> </tr> </tbody></table></div> <hr> <blockquote> <p><strong>Site view:</strong> the complete entry index appears above; the 72 older full entries are omitted from this page for capsule size. The complete log is the repository file <a href="https://github.com/mpmdw/JouleWise/blob/main/docs/decision_log.md"><code>docs/decision_log.md</code></a>.</p> </blockquote> <span id="d-073"></span><h2 id="d-073-d-016-device-list-amendment-mac-3080-ti-primary-fleet-12-gib-cap">D-073: D-016 device-list amendment — Mac + 3080 Ti primary fleet, 12 GiB cap</h2> <p>Date: 2026-07-16. Owner: Ed (ruled on the D-071 brief, <code>docs/process_traces/2026-07-16-device-list-brief/brief.md</code>). The primary cross-target fleet is the 128 GB M3 Max Mac and the 3080 Ti (12 GiB) rig; the G10 capacity cap re-floors from 8 GiB to <strong>12 GiB</strong> (3080 Ti class sets the floor). Jetson hardware is retained as OPTIONAL, non-cap-setting replication — the edge/8 GiB cell can be added later as a replication row without re-deciding this. The split study&#39;s two nodes are the Mac and the 3080 Ti rig. Big models remain open via the Mac-only subsystem (D-071 clause 3). Follow-ons ruled by Ed same session: (a) conditional primary-model repin remains open with a WIDENED candidate search under the new cap (Ed: &quot;is there really nothing better than Qwen3-1.7B? Gemma 4B or something?&quot;) — 3-4B-class models now fit comfortably; (b) dense/MoE pair re-search under the 12 GiB cap (OLMo dense arm failed G4 as published — see the OLMo verification record in the same trace directory).</p> <span id="d-074"></span><h2 id="d-074-conditional-qwen3-4b-primary-repin-olmo-1b-conversion-spike-authorized">D-074: Conditional Qwen3-4B primary repin + OLMo-1B conversion spike authorized</h2> <p>Date: 2026-07-16. Owner: Ed (ruled on the 12 GiB model search, <code>docs/process_traces/2026-07-16-device-list-brief/model-search-12gib.md</code>). (1) Qwen3-4B becomes the D-016 primary CONDITIONALLY: the repin lands only when the evidence gates pass (immutable source/license, MLX-Q4/GGUF-Q4/CUDA artifact receipts, three-runtime generation, G10 at the 12 GiB cap, KV receipts, thinking-mode policy pinned); any gate failure retains Qwen2.5-1.5B. New evidence era on success: manifests + quant ladder regenerate from one frozen source revision; Qwen2.5 results preserved as legacy. Runner-up Qwen3-1.7B; Gemma-3-4B rejected for the gated custom license + multimodal MLX seam. (2) The time-boxed OLMo-1B original-format→MLX conversion spike is authorized; success revives the matched OLMoE pair, failure files the dated negative finding and the pair defers (Option C) without re-litigation. Both execute next session as agent-lane work.</p> <span id="d-075"></span><h2 id="d-075-extension-axis-intake-ranked-fold-in-without-new-thesis-proliferation">D-075: Extension-axis intake — ranked fold-in without new thesis proliferation</h2> <ul> <li>Date: 2026-07-17</li> <li>Status: accepted (Ed-directed intake via the 2026-07-17 evaluation)</li> <li>Phase: Phase 2+ research program</li> </ul> <p>Context: Ed directed a six-axis evaluation and ratified the resulting roadmap at <code>docs/process_traces/2026-07-17-extension-axes/roadmap-synthesis.md</code>. D-055 keeps C5 deliberation in the bank and the registry as the canonical live index; D-070 keeps these axes as stress tests of Q4, caps candidate commitments at L2, and reserves commitment authority to Ed. The disposition ledger is <code>docs/stream_logs/2026-07-17-axes-foldin.md</code>.</p> <p>Decision:</p> <ol> <li>Admit C5-2.5c as the primary speculative-decoding Q4 break-even rider, C5-2.5b as its proposal-work secondary, and C5-2.5d as a mandatory contamination control. Preserve C5-2.5a in the deliberative bank as a deferred candidate rider only; it is not a standalone campaign commitment before a prospective cross-mechanism design is affordable. All four retain the evaluation&#39;s exact ceilings and forbidden upgrades, and C-023-OUTPUT-IDENTITY is binding.</li> <li>Admit C5-2.11 as the on-device MLX quantized-KV candidate and attach it to C5-2.4, C5-1.12, and C-023-QUALITY-EQUIV-QUANT. Preserve C5-2.12, C5-2.13, and C5-2.14 only as candidate riders on the existing context/KV-growth, prompt-cache/replay, and Q4/AP-1 homes.</li> <li>Admit one new canonical RQ row, RQ-AXI-HYBRID-PAIR, at an L2 named-pair ceiling. Attach the attention/context-slope and module-attribution refinements to existing rows. Record kernel/backend provenance as amendments to C5-1.8, C5-2.7, and C5-3.3, not new theses.</li> <li>Keep the roadmap&#39;s do-not-fold set out of the canonical row set. Its negative dispositions and all unresolved feasibility questions remain in the stream ledger, including explicit <strong>NEEDS-WEB</strong> markers. Intake does not convert an unresolved runtime, model-pair, adapter, or device-fit question into a capstone commitment.</li> </ol> <p>Options considered:</p> <ol> <li>Mint every evaluated suggestion as an independent live question. Rejected: it duplicates existing homes, imports unidentifiable mechanism claims, and violates D-070&#39;s single-Q4-thesis posture.</li> <li>Admit only the top three ranked items. Rejected: the lower-cost controls, riders, and provenance amendments prevent predictable attribution errors without creating independent theses.</li> <li>Apply the roadmap&#39;s ranked fold-in and explicit exclusions. Chosen by Ed.</li> </ol> <p>Considerations: this is research-agenda intake, not campaign scheduling or evidence promotion. Every admitted candidate/rider remains floor-gated, earliest-phase tagged, capped at L2 unless an already-existing parent row&#39;s separate machinery says otherwise, and subject to its named forbidden upgrade. The published corpus remains claim-evidence-flagged; no fixture, runtime feasibility result, or registry entry is live energy evidence. D-070 remains the authority for Ed&#39;s axis commitments and quiet-Mac ordering.</p> <p>Revisit triggers: a relevant <strong>NEEDS-WEB</strong> feasibility finding lands; a named runtime/pair becomes unsupported; P2-015 floors make a predeclared effect undetectable; or Ed changes the D-070 commitment set. Revisit by amending the owning row and this decision&#39;s ledger, never by silently promoting an excluded candidate.</p> <span id="d-076"></span><h2 id="d-076-site-capacity-right-sizing-aud-wo-039-review-measured-first-budgets">D-076: Site capacity right-sizing (AUD-WO-039 review) — measured-first budgets</h2> <p>Date: 2026-07-17/18. Owner: lead under Ed&#39;s &quot;host the brief&quot; directive (the capacity decision event AUD-WO-039 fenced on). Ruling, encoded in tests with PR #76: the 1 MiB Lakebed hard cap is inviolate; the measured-artifact budget is 1,000,000 B (measured mode via the pinned validator, SITE-02 loud-discovery discipline); the 943,718 B conservative-estimate guard remains ONLY as fallback when measured mode is unavailable (estimator overshoot documented ~4.3% on identical input). WO-039 preservation boundary held: no advisor-facing page, navigation, provenance, or deep link trimmed. Current measured artifact 961,210 B. Revisit trigger: measured artifact within 24 KB of the hard cap forces the next right-sizing review before any addition.</p> <span id="d-077"></span><h2 id="d-077-environment-guard-idle-admission-and-cooldown-v2">D-077: Environment guard, idle admission, and cooldown v2</h2> <ul> <li>Date: 2026-07-17</li> <li>Status: accepted</li> <li>Phase: 2 / measurement</li> </ul> <p>Context: a Ventura video screensaver compositing on an awake display was identified as a material, repeatable contaminant. The affected windows showed about 50% GPU duty and were already detected by the existing <code>idle_window_suspect</code> thresholds. The campaign preflight, per-run admission, and D-014 cooldown nevertheless lacked one shared environment policy, exact override custody, and a sustained-window implementation. In particular, the old cooldown could release after one 5-second sub-window even though the contract called for a rolling 30-second recovery window.</p> <p>Options considered:</p> <ol> <li>Treat doctor output as a quietness certificate and continue to rely on operator judgment between members. Rejected: a point-in-time advisory cannot certify the later measured window and cannot enforce fixed-n admission.</li> <li>Change persistent display/screensaver preferences or allow contaminated members to be skipped or waived. Rejected: campaign preparation must not mutate host policy, and outcome-dependent skipping/waiving would break the fixed-n design and conceal the contamination.</li> <li>Use a hash-bound campaign-policy sidecar, an enforcing campaign preflight, per-run idle admission with one evidence-bearing retry, and cooldown v2 with frozen clean-anchor fallback. Chosen.</li> </ol> <p>Decision:</p> <ul> <li>A shared pure evaluator owns environment findings. Doctor consumes it only advisorily. <code>run_campaign.py</code> consumes it enforcingly after taking the campaign lock and before member 1. Critical unknowns fail closed. Load average is recorded as evidence but is never a member-admission gate.</li> <li>The production quiet-Mac policy requires AC power with an externally connected source, low-power mode off, all online displays asleep, the screensaver disengaged, and Nominal thermal pressure. Quiet-mode arming is explicit and transient: countdown, <code>pmset displaysleepnow</code>, then a complete re-probe. Persistent settings are never changed.</li> <li>An environment override must name the exact snapshot and findings digests it acknowledges. It is recorded as an override, never a waiver, and makes every resulting member universally claim-ineligible.</li> <li>Per-run idle admission reuses the validated <code>idle_window_suspect == false</code> threshold. It permits exactly one fully evidenced retry with distinct raw artifacts. Persistent awake-display, screensaver, or unknown critical state aborts immediately. Production aborts after retry; the exploratory-only <code>flag</code> path completes the fixed-n member but stamps the unwaivable <code>environment_admission_failed</code> reason on gross-energy, idle-subtracted-energy, and throughput claims. There is no skip action.</li> <li>Cooldown v2 amends D-014: recovery requires a complete, duration-weighted, sustained 30-second evidence window; the one-sided rule is <code>rolling_mean &lt;= reference * (1 + tolerance)</code>, so a below-reference window is recovered. Nominal thermal state is conjunctive. A calibrated absolute ceiling, when configured, is only an additional upper cap. A preceding baseline is reference-eligible only when its idle window is clean, critical environment checks passed, and policy/environment provenance is present. Otherwise the campaign uses one frozen clean anchor (NEG-8 reference start when present, else the first admission-passing baseline), records its provenance, never updates it from later outcomes, and fails closed when no eligible reference or anchor exists. Historical recovered rows are not reinterpreted.</li> <li>The policy owner is a strictly typed, byte-hashed sidecar under <code>configs/campaign_policies/</code>; policy version and SHA-256 are copied into each governed bundle. Campaign execution defaults to the production sidecar. Direct <code>joulewise run</code> without a sidecar retains legacy non-enforcing behavior. All bundle/config additions are nullable or omission-serialized; legacy normalized config bytes and hashes are unchanged.</li> <li>This amends D-057&#39;s stable claim-reason vocabulary by adding <code>environment_admission_failed</code> and <code>environment_override</code>. Both are universal and unwaivable for gross-energy, idle-subtracted-energy, and throughput claims.</li> </ul> <p>Considerations: environment admission is measurement-apparatus integrity, not post-hoc data cleaning. Duration weighting prevents irregular sub-window cadence from manufacturing coverage. Frozen-anchor provenance prevents a contaminated or outcome-selected member from quietly becoming the campaign&#39;s new recovery reference. The doctor remains useful as an early advisor without claiming more than its snapshot can prove.</p> <p>Consequences: campaign and bundle contracts gain policy/preflight/admission provenance, environment snapshots gain nullable display/screensaver/HID fields plus a post-run observation, and D-014&#39;s recovery wording is governed by cooldown v2 for new evidence. This decision is separate from AUD-WO-033, which remains behavior-preserving; D-077 intentionally changes future measurement admission and cooldown behavior and does not reinterpret sealed historical bundles.</p> <p>Revisit when: live quiet-window validation contradicts the defensive <code>pmset -g systemstate</code> display parser; calibrated platform data justifies an absolute ceiling; or a new platform cannot expose an equivalent critical probe without privilege.</p> <p>Fix-round amendment (2026-07-18): review found that summing sub-window durations as the completeness test made small inter-probe gaps reject an otherwise complete wall-clock window. Cooldown v2 now requires both a retained wall-clock span of at least <code>sustained_window_s</code> and captured coverage of at least <code>coverage_fraction * sustained_window_s</code>, with <code>coverage_fraction</code> defaulting to 0.8 and recorded in thresholds, trace rows, and release evidence. The same fix round made the existing frozen-reference rule operational for controller repetitions, attached cooldown evidence to each physical repetition (and each AXI entry), froze the first eligible repetition in execution order, re-probed the full governed environment per repetition, and added a guard observation after every idle capture. Environment-preflight early exits now retain a terminal campaign verdict; missing screensaver defaults domains use the macOS 20-minute default; and the two D-077 claim barriers are registered in the canonical reducer vocabulary. These are defect corrections to the accepted policy, not new policy alternatives.</p> <nav class="doc-meta" aria-label="Decision log parts"><span>Decision log parts:</span> <a href="decision_log.html">Recent</a> · <strong aria-current="page">Archive 1</strong></nav> </div> </div> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>docs/decision_log.md · commit 1af9f92 + uncommitted · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/site/readme.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>README - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html" class="active">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#current-state">Current State</a> <a href="#verify">Verify</a> <a href="#release">Release</a> <a href="#run-the-harness-mock-target-no-hardware-or-extras-needed">Run The Harness (mock target — no hardware or extras needed)</a> <a href="#config-and-schema-verbs">Config And Schema Verbs</a> <a href="#documentation-map">Documentation Map</a></aside> <div class="doc-wrap doc-source-readme-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>README.md</code></p> <div class="provenance-plate"><span class="source-chip" title="README.md · commit 1af9f92"><span class="source-file">README.md</span><span class="source-commit">commit 1af9f92</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>JouleWise</h1> <p>JouleWise is an extensible measurement harness for energy-wise LLM inference across heterogeneous local hardware. The benchmark layered on that harness is the frozen workload suite, run rules, and strict validator. The name is a deliberate nod to JouleSort and Splitwise: energy measurement as the spine, split inference as the first major research application.</p> <p>The harness is designed around three stable ideas:</p> <ul> <li>Typed experiment configs define what should run.</li> <li>Runtime and telemetry adapters define how each hardware target is exercised and measured.</li> <li>Run bundles preserve raw traces, events, metadata, logs, and summary metrics for later audit and analysis.</li> </ul> <p><strong>Status:</strong> research prototype. The Mac (Apple M3 Max) measurement harness has completed its instrument repair (D-078 phase 0) and the repaired path has collected 229 strict members across four bracketed windows, a5-a8. Those windows are non-claim-bearing diagnostic, instrument-proving evidence, not published floors. The SCREEN+BUDGET rules are ratified and merged (D-078 clause 10; council C-033): they screen gross and idle-subtracted energy separately, retain a nonzero drift allowance for each family, require a fresh 24-hour bound, reject fallback-clock members from floor cells, and bar mock evidence from claims. The next step is one clean prospective quiet-machine window following <code>docs/phase_2/window_runbook.md</code>, producing the first claim-grade floors before the a8 re-verdict and Splitwise sizing.</p> <p>The post-audit architectural verdicts remain deliberately bounded: AXI-SB is <code>supported</code> for native static-batch runtime feasibility with request-scoped observability, while AXI-SC is <code>unsupported_for_joulewise</code> on the pinned runtime because the required speculative-decode/MTP observability or execution surface is absent. Neither is energy evidence. This summary does not select work: the generated state-kernel regions in <code>RUN_STATE.md</code> and <code>TASK_QUEUE.md</code> own live gates and next-task state. Quiet-machine execution still requires the lead-controlled hardware lane with Ed. The verified end-user quickstart remains a Phase 5 deliverable.</p> <h2 id="current-state">Current State</h2> <p>Phase 1 is in its final stretch; <strong>Phase 2&#39;s Mac vertical slice is complete and the project has its first real energy measurements</strong> (2026-07-06). From a typed config, one command produces a complete, schema-valid, auditable run bundle and reduces it to energy/latency summary metrics — proven first on deterministic mock adapters, and now live on real hardware: the MLX runtime + <code>powermetrics</code> telemetry adapters measured Qwen2.5-1.5B-Instruct (4-bit) on an Apple M3 Max. <strong>P2-003, gross energy — M3 Max / powermetrics SoC rails:</strong> ~47.2 J per 512-token request. <strong>P2-003, idle-subtracted energy — M3 Max / powermetrics SoC rails:</strong> ~44.4 J per request and ~79-90 mJ per generated output token (mean 86.8 mJ). Throughput was 257 tok/s. These are legacy L1 preliminary observations (pre-2M, manual review) under <code>docs/contracts/claims_ladder.md</code>; metric bases per <code>docs/contracts/token_normalization.md</code>. The six real corpus bundles pass <code>validate-bundle --strict</code> read-only and unrewritten: strict re-derives the recorded powermetrics power trace from raw plist evidence, re-derives summary metrics from the recorded trace and event log, checks the legacy additive summary comparison, and requires shape-valid provenance for new-era bundles. This validates the recorded evidence path; it does not independently rerun the hardware session.</p> <p>Unless a figure explicitly states otherwise, JouleWise uses gross measured energy within the named measurement boundary as the headline basis. Gross energy retains the idle, model-residency, and runtime overhead present during the measured interval, so comparisons across devices, configurations, and split versus monolithic execution use gross energy. Idle-subtracted energy is reported separately as a within-device secondary view of activity above the measured idle baseline; it is not used to rank devices or configurations. In Q4, the fixed term is estimated from the gross-energy workload sweep and is not set equal to measured idle energy. The advisor-review rationale and full basis/boundary rule are recorded in <a href="PROJECT_STATUS.md#measurement-methodology-highlights"><code>PROJECT_STATUS.md</code></a>.</p> <p>Under D-070, static batching, speculative decoding / native MTP, MoE versus dense execution, quantization, and reasoning-length variance are five stress tests of Q4&#39;s single thesis. The harness must instrument all five axes and all five have strict-valid L0 smoke-bundle support plus characterization commitments, but every study remains floor-gated, capped at L2, and sequenced after Window A. See the fuller <a href="PROJECT_STATUS.md#summary">Q4 architectural stress-test agenda</a> in <code>PROJECT_STATUS.md</code>.</p> <p>D-075 now folds a ranked extension-axis evaluation into that same agenda without proliferating theses: DSpark/DFlash break-even and control riders, on-device quantized KV, one named hybrid pair, and attached cache/context/kernel/backend provenance work. Every admitted unit remains a floor-gated candidate at or below L2 with a named forbidden upgrade; unresolved runtime and device-fit questions stay NEEDS-WEB, and Ed retains commitment authority. Separate lead-run DSpark/DFlash smokes established native MLX execution and per-round observability only. Their thinking-mode, unmatched-output throughput inversion is hypothesis-generating, not energy evidence.</p> <p>Window A remains open and still requires Ed and a quiet Mac. The repaired instrument has produced the 229-member a5-a8 diagnostic collection, and the merged screening and uncertainty-budget rules (D-078 clause 10) are ready for prospective use. The next claim attempt must follow the run-book: mint the drift bound inside the quiet window, then collect a start triplet, midpoint reference, and end triplet around the science members. A passing window will support the first claim-grade floors; only then do the a8 re-verdict and Splitwise sizing follow. The earlier 222-bundle floor publication remains a caveated historical record. Use the generated state kernel—not this summary—to select the next live or agent-lane step.</p> <p>A separate nine-bundle follow-on is now available as an explicitly <strong>exploratory, unmatched, no-claim</strong> observation block. All nine bundles are strict-valid and collection-usable but claim-evidence-flagged; each model ran three repetitions of the fixed five-item sentinel shape and emitted 1,280 generated output tokens per bundle.</p> <div class="table-scroll"><table> <thead> <tr> <th>unmatched configuration</th> <th align="right">mean gross suite energy — Apple M3 Max / powermetrics SoC rails (CPU + GPU + ANE)</th> <th align="right">mean gross energy/generated output token — same boundary</th> <th align="right">runtime-observed output throughput</th> </tr> </thead> <tbody><tr> <td>OLMoE-1B-7B BF16</td> <td align="right">229.028 J</td> <td align="right">178.928 mJ/token</td> <td align="right">122.361 tok/s</td> </tr> <tr> <td>Qwen3-4B INT4</td> <td align="right">362.772 J</td> <td align="right">283.416 mJ/token</td> <td align="right">106.519 tok/s</td> </tr> <tr> <td>Qwen3.5-122B-A10B INT4</td> <td align="right">1072.273 J</td> <td align="right">837.713 mJ/token</td> <td align="right">39.473 tok/s</td> </tr> </tbody></table></div> <p>These points differ in model scale, architecture, tokenizer, and quantization, so they do not establish a controlled scaling relation, architecture effect, or efficiency comparison. The stored per-generated-token field is idle-subtracted and appears only as D-067&#39;s labeled within-device secondary view in the <a href="docs/process_traces/2026-07-17-exploratory-block/results.md">bundle-cited extraction</a>, which also records spreads, every repetition, the floor comparison, and the Qwen thinking/config caveats.</p> <p>Remaining backends plug into the same adapter interfaces: the fixture-first 2K NVIDIA stack (SSH transport, node worker, nvidia-smi + vLLM adapters) includes NV-GATE-2 software hardening: per-backend raw-lineage verifier registration, usage-first vLLM streaming, and identity-aware process-survival handling. The NV-5 localhost lead gate passed 3/3, but ALL remote protocol pins remain PROVISIONAL pending first live hardware contact; Jetson Orin (2L) remains gated on device access.</p> <p>The landed C-028 arc includes the frozen analysis manifest, the production-uncertainty path, the campaign-verdict split, idle-dependence/HAC uncertainty, the inter-token metric, doctor preflight, and the contrast/claim engine. The analysis trio—manifest, verdict split, and contrast/claim engine—is complete. The six frozen legacy arms and 0.3.x/0.4.x dispatch rules remain explicit; landed software is not being presented as new live evidence. P0-003 closed with an iCloud Drive backup and a fresh restore that was strict-valid and byte-identical. No new live NVIDIA or quiet-Mac measurement is claimed here.</p> <p>The post-audit landings add request-scoped AXI-SA burst/decode semantics, freeze SPLIT-AP Part I before outcomes, close SITE-02&#39;s discovery and emitted-code regression work, and establish AXI-SB&#39;s <code>supported</code> verdict from lead-run B=2/B=4 Metal probes. The probes establish runtime feasibility and request observability only; they add no energy result. The corresponding AXI-SC pinned-runtime spike returned <code>unsupported_for_joulewise</code>: the external- draft path lacks the full proposal/acceptance/decode-boundary observability contract, and native MTP lacks a usable generation surface. No Mac energy leg was minted from that negative applicability result.</p> <p>The repository currently contains:</p> <ul> <li>Typed config and output schemas with JSON-Schema export and validation.</li> <li>Runtime, telemetry, and transport interface contracts, with shipped mock adapters and a backend registry.</li> <li>The runnable harness: bundle writer, controller lifecycle, reducer, a shared bundle read layer, static HTML report generator, and a CLI (<code>run</code>, <code>validate-bundle</code>, <code>reduce</code>, <code>report</code>).</li> <li>Example Mac-local and mock-local configs.</li> <li>Phase 1 methodology, feasibility, and measurement-design docs.</li> <li>A test suite run in CI on every push, including a mock end-to-end run and bundle validation. The canonical command below and CI output own the current result; reader docs intentionally do not copy its volatile count.</li> </ul> <h2 id="verify">Verify</h2> <pre><code class="language-bash">python3 -m unittest discover -s tests
docs/specs/axi/sd_model_pair_scorecard.md:208:| GGUF/llama.cpp | Same BF16 source; `Q4_0` weight type; block size 32. |
docs/specs/axi/sd_model_pair_scorecard.md:490:| `Q8_G64` | 8-bit weights, group size 64. | Same converter revision, scale/bias convention, module allowlist, skipped modules, and source tensors as Q4; only bit width differs. | `NEEDS-VERIFICATION` |
docs/specs/axi/sd_model_pair_scorecard.md:491:| `Q4_G64` | 4-bit weights, group size 64. | Same recipe as Q8 except bit width. | `NEEDS-VERIFICATION` |
docs/specs/axi/sd_model_pair_scorecard.md:499:two-level `BF16`/`Q4_G64` ladder; after the freeze, missing Q8 is a structured
docs/specs/axi/sd_model_pair_scorecard.md:541:comparisons (`Q8_G64 - BF16` and `Q4_G64 - BF16`). The two-level capability
docs/specs/axi/sd_model_pair_scorecard.md:542:fallback has `m = 1` (`Q4_G64 - BF16`) only if it is declared before the
docs/specs/axi/sd_model_pair_scorecard.md:550:`20260715` and the level order `Q8_G64`, then `Q4_G64`. Sort the 10,000 means
docs/research_question_registry.md:42:| Q4 | Fixed-vs-marginal energy model; C5-2.14 cache-policy coefficient rider | research question | promoted | L3 | no holdout-prediction claim without AP-1 floor and residual checks | AP-1 | P2-019 q4_l3_shape_grid_v1 | floor | analysis-plan-only | Strongest predictive science row; includes compositional split-energy prediction only when transfer terms exist. C5-2.14 is a candidate rider capped at L2, earliest PF, with no coefficient-direction claim below P2-015 floors ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:45:| RQ-METHOD-FLOOR | Detection floor; noise floor; short-difference resolvability; phase/item identifiability flags; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | banked | L1 methodology | no below-floor effect language except `not resolvable`; no module-energy fraction or regression-slope attribution | none-yet | P2-015 | floor | analysis-plan-only | Methodology centerpiece and prerequisite for most comparative claims; the candidate module-attribution nonclaim attaches here at earliest NS instead of becoming a row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:48:| RQ-KV-GROWTH | KV-growth decode drift; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | banked | L1/L2 chunked | no per-token joule claims; no attention-vs-FFN fraction from context slopes | none-yet | none | floor | analysis-plan-only | Candidate riders, earliest PF: bounded-window KV marginal slope and named-artifact attention/context slope; both retain chunked-window/floor discipline and stay attached rather than becoming independent rows ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:53:| C5-2.5 | Speculative-decoding energy; C5-2.5b proposal-work rider; C5-2.5c break-even rider | research question | banked | L2 | no efficiency claim without output equivalence and accepted-token accounting | none-yet | none | software | analysis-plan-only | C5-2.5c is the primary PF Q4 rider, C5-2.5b its PF secondary, and C5-2.5d the mandatory PF contamination control; C5-2.5a remains a deferred NS bank rider. `C-023-OUTPUT-IDENTITY` binds all efficiency contrasts ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:63:| RQ-SHAPE-ENERGY | Workload shape changes request energy | research question | candidate | L2 | no causal token-shape claim beyond AP-2 contrasts | AP-2 | 2M | floor | analysis-plan-only | Distinct from Q4 because it describes shape contrasts rather than holdout prediction. |
docs/research_question_registry.md:65:| C5-1.2 | Context-length energy scaling; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | candidate | L2/L3 if modeled | no short-prompt phase point claims; no wall implication from SoC rails | none-yet | none | floor | analysis-plan-only | Natural local-inference question with chunked phase limits; the two candidate PF riders remain capped at L2 and forbid module attribution from context-associated slopes ([evaluation](process_traces/2026-07-17-extension-axes/)). |
docs/research_question_registry.md:80:| RQ-SESSION-SHAPE | Session-shape energy | research question | candidate | L2/L3 depending holdout | no app-session prediction without holdout validation | none-yet | suite profiles after P2-010a | substrate | analysis-plan-only | Tests whether Q4 coefficients compose in realistic session ecology. |
docs/research_question_registry.md:93:| C5-2.8 | Placement-policy optimality from Q4 coefficients | research question | candidate | L2/L3 | no optimal-placement claim without measured split validation cells | none-yet | Phase 3 full set | hardware | fully | Uses Q4 coefficients plus measured transfer costs to choose placement. |
docs/research_question_registry.md:106:| C-023-COEFF-TRANSPORT | Coefficient transport synthetic-to-realistic; energy model portability across workload mixtures | research question | candidate (C-023) | L2/L3 depending holdout | no realistic-session prediction from synthetic grid without transport validation | none-yet | suite traces after Q4 | substrate | analysis-plan-only | Explicitly tests Q4 coefficient transport from synthetic grids to realistic app traces. |
docs/site/project_status_full.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Project Status (full) - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html" class="active">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#summary">Summary</a> <a href="#status-at-a-glance">Status At A Glance</a> <a href="#capstone-artifact-map">Capstone Artifact Map</a> <a href="#architecture">Architecture</a> <a href="#measurement-methodology-highlights">Measurement Methodology Highlights</a> <a href="#experiment-plan">Experiment Plan</a> <a href="#phase-plan-detail">Phase Plan Detail</a> <a href="#evolution-from-the-original-architecture-sketch">Evolution From The Original Architecture Sketch</a> <a href="#risks-and-minimum-viable-outcome">Risks And Minimum Viable Outcome</a> <a href="#timeline">Timeline</a> <a href="#deliverables-at-completion">Deliverables At Completion</a> <a href="#repository-map-for-verification">Repository Map (for verification)</a> <a href="#process-note">Process Note</a> <a href="#maintenance-of-this-document">Maintenance Of This Document</a></aside> <div class="doc-wrap doc-source-project-status-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>PROJECT_STATUS.md</code></p> <div class="provenance-plate"><span class="source-chip" title="PROJECT_STATUS.md · commit 1af9f92"><span class="source-file">PROJECT_STATUS.md</span><span class="source-commit">commit 1af9f92</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>JouleWise: Project Status — Full Reference</h1> <p><strong><a href="project_status.html">← Back to project status summary</a></strong></p> <p>This page continues the project-status document with its architecture, planning, and historical reference material.</p> <h2 id="summary">Summary</h2> <p>JouleWise combines a reusable, typed measurement harness with a benchmark defined by its frozen workload suite, run rules, and strict validator. It measures the energy of LLM inference across heterogeneous local hardware. The name nods to JouleSort and Splitwise: energy measurement is the spine of the system; disaggregated (&quot;split&quot;) inference - running prefill and decode on different machines with the KV cache transferred between them - is the validating research study, not the whole architecture.</p> <p>The capstone now has two explicit claim tracks. The guaranteed capstone is auditable local LLM energy measurement: the harness plus the Apple-Silicon characterization it can already execute on the M3 Max. Split (disaggregated) inference remains the differentiating validating study; when Phase 3 hardware and feasibility gates land, it upgrades the capstone from local characterization to a split-energy crossover study.</p> <p>The frozen capstone headline, fallback claims, contribution ladder, and minimum-viable stop-lines are now recorded in <code>docs/contracts/capstone_scope.md</code>; that contract is the scope pointer for reader-facing wording under the claims ladder.</p> <p>The first working slice runs on a MacBook (Apple Silicon) with MLX as the runtime and <code>powermetrics</code> as the power source, producing complete, auditable run bundles. Further backends (NVIDIA + vLLM/llama.cpp, Jetson Orin, Raspberry Pi + Hailo as a feasibility finding) plug into the same adapter interfaces.</p> <p>Research questions:</p> <ul> <li><strong>Q1</strong>: Under what conditions (model size, prompt length, link speed, device pair) does splitting inference reduce total energy versus running monolithically on either device?</li> <li><strong>Q2</strong>: How sensitive is the split&#39;s energy cost to interconnect bandwidth (1GbE vs 2.5GbE vs optional 10GbE) - where is the crossover?</li> <li><strong>Q3</strong>: When splitting saves energy, what latency does it cost, and vice versa (energy-latency Pareto frontier)?</li> <li><strong>Q4</strong> (added 2026-07-07, council C-003): What fixed-vs-marginal energy model <code>E = fixed + prefill(prompt_tokens) + decode(output_tokens)</code> does each target/model/quantization follow — and can split-run energy be predicted compositionally from monolithic coefficients plus transfer measurements?</li> <li><strong>Q5</strong> (C-003/C-007): On one machine, do workload/model/quantization efficiency rankings stay stable as workload shape, model, and quantization change, or where do they flip? A cross-device ranking extension is hardware-gated.</li> <li><strong>Q6</strong> (C-003; gated on the wall meter): Does the measurement boundary (platform rails vs AC wall power) change the conclusions?</li> </ul> <p>Current question status, aliases, gates, and claim ceilings live in the canonical live index, <code>docs/research_question_registry.md</code>. The curated bank of further candidate questions and deliberately killed ones remains the historical/deliberative record in <code>docs/research_question_bank.md</code>; the measurement noise floor / detection limit is treated as the methodology centerpiece rather than a numbered question.</p> <p>The capability map by claim ceiling is reflected in <code>docs/research_question_registry.md</code> (C-015), alongside the suite architecture v2 and benchmark interop direction; the guaranteed-capstone stop-line is recorded in the Phase 2 plan.</p> <p><strong>Q4 architectural stress-test agenda (D-070).</strong> Static batching, speculative decoding / native MTP, MoE versus dense execution, quantization, and reasoning-length variance are five stress tests of Q4&#39;s single fixed-plus-marginal energy thesis, not five additional theses. The harness must instrument every axis well enough to produce strict-valid L0 smoke bundles; the benchmark supplies the frozen workload suite, run rules, and strict validator for claim-bearing runs. Per Ed&#39;s ruling, all five axes have characterized-study commitments. Every study remains floor-gated and capped at L2; L3 is available only through Q4/AP-1&#39;s existing holdout machinery. Window A remains first, and no AXI quiet-Mac characterization starts before Window A completes. Static batching is the capstone scope; continuous batching remains a post-capstone extension.</p> <p><strong>Ranked extension-axis intake (D-075).</strong> The later six-axis evaluation did not create six more theses. It attached DSpark/DFlash break-even, proposal-work, and contamination-control riders to the speculative-decoding home; admitted an on-device MLX quantized-KV candidate and one named hybrid pair; and attached cache/context, module-nonattribution, kernel, and backend provenance riders to their existing questions. All admitted units remain candidate work with earliest-phase tags, named forbidden upgrades, floor gates, and an intake ceiling at or below L2. Unverified runtime, pair, adapter, and device-fit questions remain explicitly NEEDS-WEB, and Ed retains commitment and ordering authority under D-070.</p> <h2 id="status-at-a-glance">Status At A Glance</h2> <div class="table-scroll"><table> <thead> <tr> <th>Phase</th> <th>Scope</th> <th>Status</th> </tr> </thead> <tbody><tr> <td>1. Approval, feasibility, measurement design</td> <td>contracts, methodology, hardware feasibility evidence</td> <td><strong>in progress</strong> — the Phase 1 exit checklist owns exact completion and external gates</td> </tr> <tr> <td>2. Harness, Mac vertical slice, homogeneous baselines</td> <td>runnable harness, first real measurements, per-target baselines</td> <td><strong>in progress</strong> — Mac vertical slice and analysis software are implemented; remote protocol pins remain PROVISIONAL; the state kernel and quiet-machine rules own execution eligibility</td> </tr> <tr> <td>3. Disaggregation, KV replay, interconnect sweep</td> <td>split-energy decomposition, crossover dataset</td> <td>planned (feasibility-first)</td> </tr> <tr> <td>4. Characterization and analysis</td> <td>statistics, figures, claims audit</td> <td>planned</td> </tr> <tr> <td>5. Presentation and submission</td> <td>report, colloquium, reproducible release</td> <td>planned</td> </tr> </tbody></table></div> <h2 id="capstone-artifact-map">Capstone Artifact Map</h2> <div class="table-scroll"><table> <thead> <tr> <th>chapter/report-component</th> <th>owning doc or deliverable</th> <th>status</th> <th>missing evidence</th> </tr> </thead> <tbody><tr> <td>Background / related work</td> <td>Phase 4 Stage 4.6, <code>docs/phase_4/related_work_draft.md</code></td> <td>drafted (11 verified sources)</td> <td>background-chapter assembly and the Phase 4 exit pass</td> </tr> <tr> <td>Measurement methodology</td> <td><code>docs/contracts/measurement_methodology.md</code></td> <td>complete</td> <td>Phase 4 ratification may amend statistical details against observed variance</td> </tr> <tr> <td>Harness / instrument</td> <td><code>joulewise/</code></td> <td>complete; pre-campaign software review cleared; C-028 closed</td> <td>live execution eligibility comes from the state kernel; quiet-machine work also requires Ed and the clean hardware lane</td> </tr> <tr> <td>Apple-Silicon characterization / homogeneous baselines</td> <td>Phase 2 Slice 2M, <code>docs/phase_2/baseline_results.md</code></td> <td>Window A open; production shakedown closed and first floors published; quiet-Mac execution remains</td> <td>P2-037 claim adjudication and the live state kernel govern the next baseline step; needs Ed + quiet Mac</td> </tr> <tr> <td>Split-inference study</td> <td>Phase 3</td> <td>planned</td> <td>needs KV-feasibility spikes plus a real pairing, or the synthetic-transfer + analytical-composition floor</td> </tr> <tr> <td>Results / limitations + claims audit</td> <td>Phase 4 Stages 4.3-4.5</td> <td>analysis path implemented; Window-A calibration data exist</td> <td>the floor corpus is strict-valid but claim-evidence-flagged; P2-037 adjudication must preserve the published caveats before any claim promotion</td> </tr> </tbody></table></div> <p>Complete so far (all verifiable in the repository):</p> <ul> <li>A runnable harness: from a typed config, one command (<code>python3 -m joulewise run ...</code>) produces a complete, schema-valid, auditable run bundle and reduces it to energy/latency summary metrics - proven first on deterministic mock adapters (controller, bundle contract, and reducer math verified without hardware) and now running live on the Mac target. Bundle writer, controller lifecycle, reducer, static-HTML report generator, and CLI verbs <code>run</code> / <code>validate-bundle</code> / <code>reduce</code> (post-hoc re-derivation of summary metrics from the recorded power trace and events) / <code>report</code>. Strict validation now also re-derives powermetrics traces from raw plist evidence, checks legacy additive-summary compatibility, and requires shape-valid provenance on new-era bundles. All bundle consumers read through one shared, tested read layer, which sharply reduces the risk of displayed numbers diverging from reported ones.</li> <li>Typed config and output schemas with validation, JSON-Schema export, and a CLI, plus the canonical suite run in CI on every push, including a mock end-to-end run and bundle validation. The command and CI output own the current result; reader docs do not copy its volatile count. Emitted configs round-trip their own published schema, and config hashes (run identity) are pinned by test.</li> <li>Adapter interface contracts (runtime / telemetry / transport), the run bundle artifact contract, and the measurement methodology (idle subtraction, measurement boundaries, clock synchronization, statistical protocol - highlights below).</li> <li>Evidence-shaped plans for every phase, a design-decision log whose index is mechanically checked against its decision bodies (with D-060 ratified by Ed); the log itself is the structural authority, and most entries record the alternatives considered), a risk register with an explicit descope ladder, and example configs for the Mac and mock targets.</li> <li>The complete Mac vertical slice: the MLX runtime adapter (2G), the <code>powermetrics</code> telemetry adapter (2H, parser pinned to a captured privileged sample, raw plists preserved verbatim in every bundle), and the flagship integration (2I) — three strict-valid repetition bundles of real energy measurements on the M3 Max. <strong>P2-003, gross energy — M3 Max / powermetrics SoC rails:</strong> ~47.2 J per 512-token request. <strong>P2-003, idle-subtracted energy — M3 Max / powermetrics SoC rails:</strong> ~44.4 J per request and ~79-90 mJ per generated output token. TTFT was ~94 ms at 257 tokens/s; these are legacy L1 preliminary observations for provisional model Qwen2.5-1.5B-Instruct-4bit, mirrored locally. The separately recorded <strong>FLAGSHIP-001, gross energy — M3 Max / powermetrics SoC rails:</strong> ~304.0 J per 512-token request; <strong>FLAGSHIP-001, idle-subtracted energy — M3 Max / powermetrics SoC rails:</strong> ~298.7 J per request and ~583 mJ per generated output token. These historical values are basis labels on the recorded results, not a new reduction.</li> <li>The P2-042 frozen analysis manifest, P2-041 campaign verdict split, P2-037 contrast/claim engine, P2-040 reducer/gate remainder, P2-038 production-uncertainty software path, and NV-GATE-2 code-now hardening. Reducer dispatch is frozen across the legacy and 0.3.x arms and current through 0.4.2. None of this promotes fixture-first NVIDIA evidence to live validation.</li> <li>The report&#39;s related-work survey draft (11 sources with verified citations and an honest positioning audit) and an off-machine iCloud Drive backup whose fresh restored bundles passed strict validation and were byte-identical to their sources.</li> </ul> <p>Live remote-hardware validation has not started: NVIDIA/vLLM and Jetson Orin promotion (2K/2L) remain gated on device access. The fixture-first implementation and NV-GATE-2 software hardening are landed, but all remote protocol pins remain PROVISIONAL until live hardware contact; a P1-006 evidence checklist exists there. Code-level specs are in <code>docs/phase_2/hardware_slice_implementation_guide.md</code>. The mock-first core landed first by design, so measurement code is never debugging the measurement harness and a live hardware integration at the same time.</p> <p>Waiting on external input (most of it does not block current software work; P0-003&#39;s backup gate is satisfied, and the grading rubric/calendar (P1-008) carries the provisional-contract fallback under ratified D-060):</p> <ol> <li>NVIDIA / Jetson Orin device access evidence — the one hard gate left, for the remote-target slices 2K/2L. (The <code>nvidia_3050</code> in the architecture table is the owned always-available NVIDIA target; the 3080 Ti is a separate, borrowed card used only for Phase 3&#39;s interconnect sweep.)</li> <li>Calendar anchors: colloquium date, report deadline, and the 3080 Ti borrow window, to derive phase target dates.</li> <li>Advisor scope confirmation (see the sanity-check note above) — finalizes model selection; deliberately deprioritized while all work remains harness-shaped and valuable under any scope.</li> </ol> <p>Closed since the last revision: the comprehensive audit; AXI-SA&#39;s burst-decode contract; SITE-02 D1/D2; the SPLIT-AP Part I pre-registration freeze; AXI-SB&#39;s <code>supported</code> static-batch verdict with its Mac C5-2.2 leg; P2-038&#39;s production-shaped live gate; and AXI-SC&#39;s <code>unsupported_for_joulewise</code> pinned- runtime verdict. The later DSpark/DFlash MLX feasibility smokes and D-075 extension-axis intake are recorded without promoting an energy claim, and the nine-bundle OLMoE/Qwen follow-on remains explicitly exploratory. Window A&#39;s software gates are satisfied, its first floor corpus is published, and the window remains open. The floors are calibration thresholds rather than claim promotion: P2-037 adjudication remains pending because strict-valid collection and claim readiness are separate gates; execution timing is governed by the live work-selection state in <code>RUN_STATE.md</code>&#39;s generated state-kernel region and still requires Ed plus a quiet Mac.</p> <h2 id="architecture">Architecture</h2> <pre><code class="language-text">typed config
docs/site/project_status_full.html:9:</code></pre> <p>Key elements:</p> <ul> <li><p><strong>Single controller, flexible transports.</strong> <code>local</code> for one-machine runs; <code>ssh</code> for remote NVIDIA/Orin targets and split experiments.</p> </li> <li><p><strong>Two adapter layers.</strong> Runtime adapters answer how a model workload executes; telemetry adapters answer how power and thermal state are measured. They are independent, so any runtime can pair with any telemetry source.</p> </li> <li><p><strong>A target is a composition</strong> of transport + runtime + telemetry:</p> <div class="table-scroll"><table> <thead> <tr> <th>Target</th> <th>Transport</th> <th>Runtime</th> <th>Telemetry</th> </tr> </thead> <tbody><tr> <td>macbook_m3_max</td> <td>local</td> <td>mlx</td> <td>powermetrics</td> </tr> <tr> <td>nvidia_3050</td> <td>ssh</td> <td>vllm (llama.cpp-CUDA fallback)</td> <td>nvidia-smi</td> </tr> <tr> <td>orin_nano</td> <td>ssh</td> <td>tbd</td> <td>board rails (INA3221)</td> </tr> <tr> <td>pi5_hailo</td> <td>ssh</td> <td>hailo - unsupported (verdict 2026-06-12)</td> <td>wall meter</td> </tr> </tbody></table></div> </li> <li><p><strong>Every run writes a self-contained run bundle</strong>: normalized config, device/environment metadata, timestamped event log (lifecycle + phase + token events), raw power trace, backend-native raw telemetry preserved verbatim, logs, model outputs, and reduced summary metrics. Summary numbers are always derived, re-derivable artifacts; the raw bundle is the source of truth.</p> </li> <li><p><strong>Typed schemas</strong> (Python dataclasses, standard library only in the core) validate configs and outputs and emit JSON Schema documentation.</p> </li> <li><p><strong>Unsupported is a result, not a crash.</strong> Infeasible hardware/model/runtime combinations return structured failure codes (<code>did_not_fit</code>, <code>runtime_unavailable</code>, <code>telemetry_unavailable</code>, ...) and still produce complete bundles - hardware applicability is itself reportable data (this is how a negative Hailo verdict stays a finding).</p> </li> <li><p><strong>Dashboard v1 is a read-only run browser</strong>, generated as static HTML from bundles (run table, per-run pages, power traces with phase shading). It has no orchestration role.</p> </li> </ul> <h2 id="measurement-methodology-highlights">Measurement Methodology Highlights</h2> <p>Unless a figure explicitly states otherwise, JouleWise uses gross measured energy within the named measurement boundary as the headline basis. Gross energy retains the idle, model-residency, and runtime overhead present during the measured interval, so comparisons across devices, configurations, and split versus monolithic execution use gross energy. Idle-subtracted energy is reported separately as a within-device secondary view of activity above the measured idle baseline; it is not used to rank devices or configurations. In Q4, the fixed term is estimated from the gross-energy workload sweep and is not set equal to measured idle energy.</p> <p>This reporting choice follows Dr. Rivoire&#39;s advisor review, as recorded in D-067: subtracting idle penalizes energy-proportional devices and rewards high-idle ones; for split runs, subtracting both nodes&#39; idles deletes exactly the cost that the Q1 crossover question adjudicates.</p> <ul> <li><strong>Dual-basis capture.</strong> Every eligible measured request records gross and idle-subtracted energy plus idle variance; the reporting rule above changes no stored evidence (D-067).</li> <li><strong>Measurement boundaries are named, not assumed.</strong> Each telemetry backend measures a different physical boundary - powermetrics: Apple SoC subsystems (CPU+GPU+ANE); nvidia-smi: GPU board only; Jetson rails: module input; wall meter: full system AC. Within-target comparisons are the primary claim type; cross-target comparisons always state the boundary difference, calibrated against the wall meter where available.</li> <li><strong>Uncertainty is quantified.</strong> Headline comparisons use n&gt;=5 repetitions with mean, standard deviation, and 95% t-intervals; outliers are flagged (never silently dropped); raw points appear in every figure. Differences are claimed only from the confidence interval of the predeclared paired/block difference or named model contrast — never from marginal-interval separation — with the D-053 three-way wording rule (below-floor: not resolvable; above-floor non-directional: unresolved; equivalence only via a predeclared gate). Thermal state is controlled with an idle-power-recovery gate between repetitions.</li> <li><strong>Multi-node clock discipline.</strong> For split runs, per-node clock offset is bounded with controller-mediated marker events and recorded; cross-node intervals shorter than the bound are flagged rather than trusted.</li> <li><strong>Measurement quality is first-class data</strong>: requested vs observed sampling rate, dropped samples, idle variance, thermal drift, telemetry source - all in every summary.</li> </ul> <h2 id="experiment-plan">Experiment Plan</h2> <p><strong>Homogeneous baselines (Phase 2).</strong> Per target and model: a workload matrix spanning prefill-heavy, decode-heavy, and balanced profiles (prompt 128-4096 tokens x decode 64-512), n=5, producing energy/token and energy/request with intervals - and reproducing the qualitative prefill/decode power asymmetry that motivates disaggregation.</p> <p><strong>Disaggregation (Phase 3), feasibility-first.</strong> KV-cache portability is the project&#39;s central technical risk, so the phase is a ladder where each rung is publishable even if the next fails:</p> <ol> <li><em>Synthetic transfer microbenchmark</em> (guaranteed): move KV-sized payloads between nodes with both-end power sampling - transfer energy and time vs payload size vs link speed, independent of any LLM runtime&#39;s cooperation.</li> <li><em>Offline replay</em> (primary): persist the prompt cache on the prefill node, transfer the file, resume decode on the decode node - same pinned runtime on both ends. Per-runtime feasibility spikes (mlx-lm, llama.cpp including cross-machine portability, vLLM time-boxed) run before any borrowed-hardware scheduling.</li> <li><em>Live split</em> (stretch): streamed KV during the run; explicitly droppable without harming the study.</li> </ol> <p>Payload sizes are analytically predictable (2 x layers x kv_heads x head_dim x 2 bytes per token, fp16), which drives experiment design - for a 2048-token prompt: a 1.5B-class model ~56 MiB (~0.5 s at 1GbE), an 8B-class model ~256 MiB (~2.3 s at 1GbE). At 1GbE, mid-size-model transfer time is the same order as prefill time on weaker devices - exactly the regime where an energy crossover can exist; the sweep spans prompt lengths and link speeds accordingly.</p> <p><strong>Analysis (Phase 4).</strong> Aggregation over validated bundles with an exclusion log (no silent data drops); a deterministic figure pipeline (every report figure regenerates from a script); a claims-to-evidence index (every quantitative claim traces to figure -&gt; script -&gt; raw bundles); a sensitivity audit checking that headline effects exceed their confidence intervals.</p> <h2 id="phase-plan-detail">Phase Plan Detail</h2> <p>Each phase has a step-by-step plan and an evidence-gated exit checklist in the repository; a phase closes only when every required item has recorded evidence or a documented blocker.</p> <ul> <li><strong>Phase 1</strong> - <code>docs/phase_1/</code>: lock contracts and methodology (done); gather feasibility evidence: advisor scope, Mac telemetry permissions, wall-meter decision, network topology for the sweep, Hailo verdict, NVIDIA/Orin access, calendar mapping.</li> <li><strong>Phase 2</strong> - <code>docs/phase_2/</code>: bundle writer -&gt; mock adapters -&gt; controller -&gt; reducer -&gt; one-command run (all hardware-independent, exact-arithmetic tests) -&gt; then the real Mac slice (MLX + powermetrics, repeated with variance) -&gt; remote targets as access permits -&gt; homogeneous baselines.</li> <li><strong>Phase 3</strong> - <code>docs/phase_3/</code>: feasibility spikes -&gt; split-run config schema -&gt; transfer microbenchmark -&gt; offline-replay splits with per-stage energy decomposition (prefill / transfer / deserialize / decode) -&gt; interconnect sweep -&gt; crossover dataset.</li> <li><strong>Phase 4</strong> - <code>docs/phase_4/</code>: statistics ratification, aggregation, figures F1-F12 (baselines, traces, phase asymmetry, split decomposition, crossover curves, Pareto frontier, interconnect costs, measurement quality), claims index, results + limitations draft, background / related-work draft (new stage 4.6 — the report&#39;s background chapter now has an owner).</li> <li><strong>Phase 5</strong> - <code>docs/phase_5/</code>: verified README quickstart, backend extension guide (verified by a shipped tutorial adapter), sample bundles, dataset freeze with hash manifest and release tag, colloquium slides, final report.</li> </ul> <h2 id="evolution-from-the-original-architecture-sketch">Evolution From The Original Architecture Sketch</h2> <p>The project began from the &quot;Energy Benchmark Architecture And Expanded Plan&quot; sketch. Its architecture survives intact; implementation thinking has been refined in documented ways (full rationale in <code>docs/decision_log.md</code>):</p> <div class="table-scroll"><table> <thead> <tr> <th>Original sketch</th> <th>Current position</th> <th>Why</th> </tr> </thead> <tbody><tr> <td>Configs YAML/JSON; bundle stores <code>config.yaml</code></td> <td>JSON now; bundle stores normalized <code>config.json</code>; YAML deferred until authoring pain is real</td> <td>zero-dependency core; sorted-key JSON gives stable config hashing for aggregation (D-001, D-007)</td> </tr> <tr> <td>&quot;Likely Python + Pydantic&quot; schemas</td> <td>stdlib dataclasses with the same contract; Pydantic port possible later</td> <td>Phase 1 runs with no installs; semantics unchanged (D-009)</td> </tr> <tr> <td>Mac MLX slice implemented first</td> <td>mock vertical slice first, Mac immediately after</td> <td>the harness is proven with exact-arithmetic tests before real telemetry can confound it; Mac remains the first real backend (Phase 2 plan)</td> </tr> <tr> <td>Dashboard file-backed; &quot;DuckDB/SQLite if browsing gets slow&quot;</td> <td>static HTML generator; analysis aggregation via CSV + pandas in Phase 4; no DB planned</td> <td>smallest sustainable tool that serves the two real uses: sanity-checking runs and showing progress (D-006)</td> </tr> <tr> <td>Offline KV replay before live disaggregation</td> <td>same, hardened into a three-rung feasibility ladder with per-runtime spikes and a same-runtime rule</td> <td>KV tensors are not portable across engines; cross-runtime transfer (e.g. vLLM-prefill -&gt; MLX-decode) is out of scope; heterogeneous <em>hardware</em> pairs use a portable runtime where its backends allow, pending an explicit portability spike (D-015)</td> </tr> <tr> <td>GPU-to-Apple split experiments listed directly</td> <td>pairings are planned only after spike verdicts; synthetic transfer sweep guarantees the crossover dataset either way</td> <td>converts the project&#39;s largest feasibility risk into a bounded one (R-004, R-005)</td> </tr> <tr> <td>(not covered)</td> <td>measurement boundaries, multi-node clock discipline, controller co-residency mitigation, statistical protocol</td> <td>added rigor required for defensible cross-device energy claims (D-003, D-013, D-014, D-018)</td> </tr> </tbody></table></div> <p>Verdict from the 2026-06-09 audit: the sketch remains coherent; nothing in it has been contradicted - the changes above are refinements with recorded rationale, and the repository&#39;s plans are the maintained, authoritative version of it.</p> <h2 id="risks-and-minimum-viable-outcome">Risks And Minimum Viable Outcome</h2> <p>Top risks (full register with triggers and fallbacks in <code>docs/risk_register.md</code>):</p> <div class="table-scroll"><table> <thead> <tr> <th>Risk</th> <th>Posture</th> </tr> </thead> <tbody><tr> <td>KV persist/resume unsupported in a runtime (esp. vLLM)</td> <td>spikes before hardware scheduling; llama.cpp fallback; synthetic-transfer floor + analytical composition keeps the study publishable</td> </tr> <tr> <td>Cache files not portable across machines/backends</td> <td>explicit cross-machine spike; fallback to same-platform pairs; portability finding is itself reportable</td> </tr> <tr> <td>Schedule vs fixed academic deadlines</td> <td>every phase has a hardware-independent floor; explicit descope ladder</td> </tr> <tr> <td>3080 Ti borrow window slips</td> <td>borrow time is execution-only against a rehearsed runbook; pairing droppable</td> </tr> <tr> <td>No wall meter</td> <td>within-target claims unaffected; cross-target claims carry the stated boundary caveat</td> </tr> <tr> <td>Advisor approval delay</td> <td>all current work is harness-shaped and valuable under any scope</td> </tr> </tbody></table></div> <p>Minimum viable outcome (worst-case floor; still a complete, defensible capstone if reached): the reusable harness + Mac vertical slice + homogeneous baselines + synthetic interconnect sweep + an analytical split-energy model - honest, measured, reproducible.</p> <h2 id="timeline">Timeline</h2> <p>Dates pending (this is an explicit ask): colloquium date, report deadline, borrow window. Once known they anchor <code>docs/milestones.md</code> and phase target dates are derived backwards (slides want frozen figures &gt;=1 week ahead; the report wants its claims audit &gt;=1 week ahead). Until then, the dependency structure is the schedule: Phase 4 is deskwork and serves as the buffer; hardware-gated steps are scheduled around access windows with desk work filling gaps.</p> <p>Known: the Mac authorization gate closed 2026-07-06 (privileged sample captured, scoped sudo rule installed); remote-device access (NVIDIA, Orin) is the remaining hardware gate. Work paused 2026-06-13 to 2026-07-04 (planned break, recorded in <code>docs/milestones.md</code>).</p> <h2 id="deliverables-at-completion">Deliverables At Completion</h2> <ul> <li>The JouleWise repository: harness, adapters, tests, CI, extension guide, README quickstart that a new user can run in minutes.</li> <li>The dataset: raw run bundles + hash manifest, frozen and tagged, with every figure regenerable by script.</li> <li>The study: where splitting wins, loses, and why - with uncertainty, limitations, and hardware-applicability findings (including negative verdicts).</li> <li>Final report and colloquium presentation, every quantitative claim traceable to raw data.</li> </ul> <h2 id="repository-map-for-verification">Repository Map (for verification)</h2> <div class="table-scroll"><table> <thead> <tr> <th>Where</th> <th>What</th> </tr> </thead> <tbody><tr> <td><code>README.md</code></td> <td>entry point and quickstart (grows in Phase 5)</td> </tr> <tr> <td><code>AGENT_PLAN.md</code></td> <td>phase index and acceptance criteria</td> </tr> <tr> <td><code>docs/phase_N/phase_N_plan.md</code> + <code>_exit_checklist.md</code></td> <td>per-phase steps and evidence gates</td> </tr> <tr> <td><code>docs/contracts/</code></td> <td>measurement methodology, run-bundle layout, adapter contracts</td> </tr> <tr> <td><code>docs/decision_log.md</code></td> <td>every design decision with alternatives considered</td> </tr> <tr> <td><code>docs/risk_register.md</code></td> <td>risks, triggers, mitigations, descope ladder</td> </tr> <tr> <td><code>docs/milestones.md</code></td> <td>calendar map</td> </tr> <tr> <td><code>docs/run_reports/</code></td> <td>dated work logs with commands and outcomes</td> </tr> <tr> <td><code>joulewise/</code>, <code>tests/</code></td> <td>the harness package + canonical test suite; the command and CI output own its current result</td> </tr> </tbody></table></div> <h2 id="process-note">Process Note</h2> <p>The machinery exists to protect measurement claims from unchecked summaries, stale assumptions, and review-induced drift.</p> <p>This project is developed by a human researcher directing a multi-agent AI system he designed and iteratively engineered over the course of the project — the orchestration itself is a second, deliberate piece of engineering alongside the measurement harness and its benchmark, and by now it is interesting in its own right.</p> <p>The full description lives in <code>docs/orchestration.md</code> (the loop, the roles, the artifact system, and how the topology itself evolved under its own review machinery); this section is the summary.</p> <p><strong>The division of labor.</strong> Ed sets the research direction, the methodology standards (the decision log&#39;s non-negotiables: raw-evidence bundles, dual-basis capture with gross-energy headlines, named measurement boundaries, no unauditable claims), the hardware and access decisions, and — the part that is easy to underrate — the <em>process policy</em>: every rule below exists because he observed a failure or an opportunity and issued a standing instruction. The AI staff executes: the designated lead agent is the final reviewer and single point of accountability: decomposition, design adjudication, every final diff gate, live verification, merges, and bookkeeping. Independent implementation and review agents do the volume work against pinned specs, adversarial review lenses, test writing, and fresh-instance test auditing; specialist agents handle bounded sweeps. Cross-model review is load-bearing by design: the attributed catch record shows the models and review layers catching different classes of defect.</p> <p><strong>The machinery, briefly.</strong> Independent tasks run as parallel git worktrees, the lead driving each stream&#39;s implementation/review pipeline directly (a topology that is itself the product of a signed cross-model meta-review, then validated by a full session with zero coordination stalls — the evolution is traced in <code>docs/orchestration.md</code>). Every implementation passes through a layered pipeline: a design argument round (the implementer must argue trade-offs before coding), fresh-instance counterreview lenses with lead-triaged dispositions, a test-amplification round, a writer-never-reviews-its-own-tests audit, the lead&#39;s diff gate, and lead-side live verification on real hardware — the one layer never delegated, because it has repeatedly caught blockers whose own tests were green (the tests encoded the same wrong assumption as the code). Merges add their own gate: a pre-merge oversight pass by fresh reviewers with distinct angles, and a standing <em>final-head rule</em> — any commit landing after the last review round gets one more fresh review before merge (its first application caught a crash path in a &quot;trivial&quot; late fix). After parallel streams merge, a dedicated integration review hunts the cross-stream defects no per-stream review can see (two interaction defects on its first outing, two more on its second). An event-driven review council convenes for contract-bearing work, and — per Ed&#39;s instruction — its <em>deliberations</em> are recorded, not just its verdicts: the council log preserves positions, the reasoning exchanged, who prevailed and why, and overridden dissents, so a future reader (or model) can reconstruct why any decision was made.</p> <p><strong>The paper trail (each claim traceable to its evidence home; the external re-reduction demonstration is still pending).</strong> Each fact has one home: <code>docs/decision_log.md</code> — the binding design decisions (the log is the count authority), most recording alternatives considered and revisit conditions; <code>docs/council_log.md</code> — the deliberation record; <code>docs/stream_logs/</code> — per-stream decision ledgers committed <em>with</em> the code they justify (wrong decisions are superseded in place, never erased); <code>docs/run_reports/</code> — one record per session with verification evidence, a per-review-layer catch table, and a delegation-calibration ledger (outcomes assigned by the lead after the gate, never self-reported; prompt-defects separated from model-defects). The whole loop is self-instrumenting: every review layer&#39;s unique catches are attributed and tallied, and a layer that stops earning its keep is dropped by its own evidence rule (one already has been). Delegation boundaries move on calibration evidence, not intuition. Lessons are folded into the process playbooks the same session they are learned — measurably: one failure mode recurred five times before its fix was distilled, and zero times after. The loop even reviews itself: a meta-review consensus (C-009) redesigned the coordination topology, and the next session (C-010) validated the redesign with a zero-stall run.</p> <p><strong>What one day of this looks like (2026-07-07).</strong> Five implementation streams plus a repo-wide test audit ran concurrently: statistical uncertainty, contamination detection, deep DVFS telemetry, campaign automation, and a KV-cache size model. All five merged the same day; the test suite grew 254 → 369; the layered review recorded thirteen attributed catches including three blockers that no single reviewer would plausibly have found together. One blocker surfaced only when the real CLI was run against code whose own tests were green, because the tests encoded the same wrong assumption as the code.</p> <p><strong>How the scope grew.</strong> The project began as an architecture sketch for &quot;measure LLM inference energy on edge hardware.&quot; Contracts-first engineering turned that into an auditable instrument: typed configs, self-contained evidence bundles, a strict re-reduction validator. The mock vertical slice proved the math without hardware; the Mac slice produced the first real joules; the flagship run put a 122-billion- parameter mixture-of-experts model through the identical harness and yielded the first real cross-model observation: two confounded points that differ in size, architecture, and quantization, with energy/token behavior consistent with the fixed-vs-marginal model while decode power stays nearly flat — the big model costs time, not watts. This week the instrument gained the statistical and forensic machinery above, and a steelmanned, devil&#39;s-advocated research agenda of 31 tiered questions — 16 answerable on the current hardware alone (<code>docs/research_question_bank.md</code>). The pattern throughout: capability first, claims only when the instrument can defend them.</p> <p><strong>And the most recent day (2026-07-07/08).</strong> Four checkpointed streams were resumed, completed, and merged in one session: the integrity/ provenance overhaul (all 31 audit-pinned defects fixed; strict validation now re-derives the power trace from raw evidence), the docs package, the KV-cache replay feasibility verdict, and the complete fixture-first NVIDIA stack. The layered review recorded ~30 attributed catches, including two blockers no implementer&#39;s tests could see (a provenance hash that did not prove the actual generation input; a validation-gate bypass via mutable metadata), two pinned wire contracts overturned by review before they could ever touch hardware, and one fabricated-evidence defect caught only at the lead&#39;s diff gate. The suite went 415 → 546 tests with zero expected failures, and the lead never wrote implementation code and never skipped a gate.</p> <p><strong>Where to look.</strong> <code>docs/orchestration.md</code> is the process description. <code>docs/council_log.md</code> is the deliberation record — C-006 is a full orchestration trace of the five-stream day; C-009/C-010 are the topology meta-review and its validation; C-011 is the critique counter-review. <code>docs/decision_log.md</code> holds the binding design decisions with alternatives considered (the log is the count authority). <code>docs/run_reports/</code> narrates each working session, with per-layer catch tables and the delegation-calibration ledger. The executable orchestration playbooks live outside this repository as reusable skills (council, delegation, multi-stream worktrees, adversarial review, and a top-level operation-loop that sequences them), so the machinery survives this project and transfers to the next one.</p> <h2 id="maintenance-of-this-document">Maintenance Of This Document</h2> <p>Updated at phase transitions and whenever advisor-visible state changes (a gate closes, a verdict lands, the schedule moves). Volatile work-selection facts stay in the state kernel, verification results stay in command/CI output, and decision structure stays in the checked decision-log index. A front-facing change also refreshes <code>docs/site/DRIFT.md</code>; Ed alone regenerates and deploys the site (D-068).</p> </div> </div> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>PROJECT_STATUS.md · commit 1af9f92 · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/specs/axi/se_analysis_plans_draft.md:36:does not measure a B>1 slope, a spec pair, a quant/quality joint gate, a
docs/specs/axi/se_analysis_plans_draft.md:50:Q4/AP-1 holdout machinery, which none of these drafts invokes.
docs/specs/axi/se_analysis_plans_draft.md:130:| `PILOT-MOEBATCH-V1` | Three complete paired-model superblocks: 31 groups per model per superblock, 186 group executions. | Dense/MoE slope/DID, normalized-energy, routing-if-visible, and latency covariance. |
docs/specs/axi/se_analysis_plans_draft.md:144:| Plan ID / RQ consumer | `AP-BATCH-DRAFT` / Mac leg of C5-2.2; a static-batch stress test of Q4's fixed-plus-marginal thesis. |
docs/specs/axi/se_analysis_plans_draft.md:145:| `family_id` | `FAM-AXI-BATCH-MODEL-SELECTION` is one seven-hypothesis family: one affine slope, three fixed lack-of-fit departures, and three frozen breakpoint hinges. `FAM-AXI-BATCH-NORMALIZED` owns B-versus-B1 gross J/request and J/committed-token contrasts. `FAM-AXI-BATCH-LATENCY` owns eight separate two-sided difference hypotheses: TTFT-p95 and end-to-end-p95 at each of B=2,4,8,16 versus B=1. |
docs/specs/axi/se_analysis_plans_draft.md:146:| `claim_role` | Affine slope and lack-of-fit: primary inside the one model-selection family. Frozen-candidate breakpoint: gate-kept secondary inside that same family and multiplicity budget. Normalized energy and latency: secondary. Memory-fit disposition: structured descriptive outcome. |
docs/specs/axi/se_analysis_plans_draft.md:148:| `multiplicity_rule` | One Holm denominator of exactly seven covers the complete `FAM-AXI-BATCH-MODEL-SELECTION`: one affine-slope hypothesis; the three lack-of-fit contrasts `d_1,d_2,d_3`; and one continuous-hinge coefficient for each frozen knot `K_BATCH={2,4,8}`. The single selection rule is: select `affine adequate` only when every simultaneous adjusted lack-of-fit interval lies inside its floor-clearing equivalence band; if any adjusted, floor-clearing `d_j` instead establishes lack of fit, open the three hinge candidates without resetting alpha and select one only when its hinge survives the same seven-hypothesis Holm denominator, it has the uniquely lowest leave-one-block-out RMSE, and its RMSE gap clears the pilot-frozen comparison bound; otherwise report `shape unresolved`/`breakpoint unresolved`. Any other knot is exploratory. Normalized contrasts have their own complete Holm denominator. The latency family has exactly eight two-sided difference hypotheses and one Holm denominator of eight. |
docs/specs/axi/se_analysis_plans_draft.md:283:| `selection_scope` | The S-D preferred `BF16/Q8_G64/Q4_G64` ladder or its prospectively frozen `BF16/Q4_G64` capability fallback (**PROVISIONAL-UNTIL-S-D-SCORECARD**) for the one scorecard model family, tokenizer, MLX runtime/recipe, target/boundary, `axi-sd-greedy-eos128-v1` output policy, 32-item energy subset, and 256-item quality screen. Artifact revisions, levels, hashes, and fallback status freeze before outputs or energy. Cross-stack and cross-boundary comparisons are outside this Mac-leg plan. |
docs/specs/axi/se_analysis_plans_draft.md:426:| `family_id` | `FAM-AXI-MOE-BATCH-OBSERVED` for gross-energy slope/DID interactions; `FAM-AXI-MOE-BATCH-NORMALIZED` for J/request and J/token interactions; `FAM-AXI-MOE-BATCH-LATENCY` for separate TTFT/end-to-end interactions; and conditional `FAM-AXI-MOE-BATCH-ROUTING` for the two exact routing summaries below. |
docs/specs/axi/se_analysis_plans_draft.md:429:| `multiplicity_rule` | Holm separately over every frozen observed-energy, normalized, latency, and—if admitted—routing contrast. Routing admission and its complete denominator freeze before execution; no counter observed after execution creates a family. Gross-energy slope and DID rows share the complete observed-interaction denominator. |
docs/specs/axi/se_analysis_plans_draft.md:436:| Floor gate | **PROVISIONAL-UNTIL-P2-015:** same-design paired-model group calibration must supply joint `Sigma_F` across model x B cells. For slope interaction vector `c_int`, use `F_int=sqrt(c_int^T Sigma_F c_int)`, its transported `D_int`, and additive `G_int=F_int+D_int`; every DID uses its exact `c_DID` and analogous additive guard. J/request uses linear total/16 weights; J/token uses the full two-model/two-B ratio gradient and summed stochastic/deterministic guards. Missing cross-model covariance, unsupported duration/B/state, or any nonlinear input forces refusal and a dedicated 62-group alias-calibration superblock. Latency/routing precision comes from the AP pilot, not a joule floor. |
docs/specs/axi/se_analysis_plans_draft.md:449:| `MOEBATCH-SLOPE-INTERACTION` | `FAM-AXI-MOE-BATCH-OBSERVED` / primary | Difference between dense and MoE all-B affine slopes on gross group energy. |
docs/specs/axi/se_analysis_plans_draft.md:462:  primary slope interaction; neither permits outcome-selected knots.
docs/site/claims_ladder.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Claims Ladder - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html" class="active">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#global-rules">Global Rules</a> <a href="#ladder">Ladder</a> <a href="#downgrade-examples">Downgrade Examples</a></aside> <div class="doc-wrap doc-source-docs-contracts-claims-ladder-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>docs/contracts/claims_ladder.md</code></p> <div class="provenance-plate"><span class="source-chip" title="docs/contracts/claims_ladder.md · commit db150a0"><span class="source-file">docs/<wbr>contracts/<wbr>claims_ladder.md</span><span class="source-commit">commit db150a0</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>Claims Ladder</h1> <p>Status: binding for reader-facing claims from Slice 2M onward. Decision D-037 records adoption. Per-claim IDs and mechanical enforcement arrive with the Phase 4 claims index; until then, authors apply this ladder during review.</p> <p>This contract governs wording in reports, slides, README/status prose, figure captions, and tables that a reader could treat as a result. Dated run reports, stream logs, council logs, and decision logs may preserve historical wording, but later reader-facing summaries must use the current level.</p> <p>The warning-only prose scan mechanically enumerates <code>README.md</code>, <code>PROJECT_STATUS.md</code>, <code>docs/report_src/**</code>, the generated Phase-4 claims projection, Markdown tables/captions under analysis and figure artifacts, and present or future <code>slides/</code>, <code>captions/</code>, and <code>tables/</code> publication trees. Historical <code>docs/run_reports/**</code> records and the decision/council/stream logs are deliberately outside that scan. Warning-only exit behavior remains the D-059 policy: these findings require editorial review but are not structural claim-gate failures.</p> <p>The canonical JSONL accepts two authority-distinct row dialects through one fail-closed validator: the single pre-P2-037 legacy L1 row only under its exact hash-pinned identity, and current rows linked to a governed <code>joulewise.claim_verdicts.v1</code> artifact. Rows with unknown authority fields or a mixture of legacy and engine-linked authority fields are invalid. Verdict semantics belong to <code>joulewise.analysis_engine</code>; the claims-index layer adds only linkage, canonical ordering/rendering, relative-path, editorial, and current production-admission checks. <code>two_look_alpha_spending</code> remains outside claims-index production admission until separately ruled in; current admission is deliberately <code>fixed_n</code> only.</p> <h2 id="global-rules">Global Rules</h2> <ul> <li>Strict validation is the entry ticket for evidence. A run bundle that cannot pass the applicable strict checks does not support a result claim.</li> <li>Measurement boundaries follow D-018. Claims must name the boundary label where it matters, for example <code>M3 Max / MLX / powermetrics SoC rails</code>, <code>RTX / vLLM / nvidia-smi board power</code>, or <code>wall_meter AC</code>.</li> <li>Cross-boundary comparisons are descriptive only unless a named calibration bundle exists for the compared boundaries. Calibration bundles include wall meter or USB-C PD evidence that explicitly bridges the boundary.</li> <li>Comparative claims from 2M use the experiment manifest order. Interleaved order is required where model reload and operational constraints permit; if block order is forced, the claim must say so and remain below L2 unless the Phase 4 drift audit clears it.</li> <li>Detection-floor gates follow Phase 4 Stage 4.0 and Stage 4.5. Effects below the floor are reported as <code>not resolvable</code>, not as wins, losses, or no difference.</li> <li>Energy-per-output-token claims require runtime-observed output token counts, the runtime stop reason, and the output policy label. If the denominator comes from config fallback rather than runtime observation, the claim downgrades to L0 capability language.</li> <li>(2026-07-09) Token-denominated metrics and cross-tokenizer comparison language follow <code>docs/contracts/token_normalization.md</code>, including its stack-identity table, across all surfaces this ladder governs.</li> </ul> <h2 id="ladder">Ladder</h2> <div class="table-scroll"><table> <thead> <tr> <th>Level</th> <th>Allowed Claim Shape</th> <th>Required Evidence</th> <th>Forbidden Language</th> </tr> </thead> <tbody><tr> <td>L0 - Capability</td> <td>The harness can execute this path and preserve auditable evidence.</td> <td>One complete bundle; applicable strict validation; raw artifacts present; boundary label recorded. Config-fallback token denominators may appear only here.</td> <td>faster, cheaper, more efficient, scales, crossover, ranking, law, proves</td> </tr> <tr> <td>L1 - Instrument Result</td> <td>On this exact stack, boundary, workload, and output policy, this measured quantity was observed.</td> <td>n &gt;= 3 strict-valid bundles, or a single run only if explicitly labeled smoke/capability; runtime-observed token counts for per-token claims; stop reason and output policy label; no suspect quality flags unless waived in text.</td> <td>general device ranking, model-family law, cross-target winner, active-parameter scaling result</td> </tr> <tr> <td>L2 - Comparative Result</td> <td>Condition A differed from condition B within the same measurement boundary under a named workload and policy.</td> <td>n &gt;= 5 per condition; strict-valid bundles; 2M experiment manifest order recorded and interleaved where permitted; confidence intervals reported; effect clears the Phase 4 detection floor; same boundary label, or a named calibration bundle if boundaries differ.</td> <td>cross-boundary winner without calibration, universal, architecture-wide conclusion, extrapolated crossover</td> </tr> <tr> <td>L3 - Model Fit</td> <td>A fitted fixed/marginal model predicts held-out cells within stated error for the tested matrix.</td> <td>Designed matrix with holdout cells; strict-valid source bundles; runtime-observed token denominators; residual and sensitivity analysis; detection-floor audit for every fitted effect; boundaries and workload policies stated.</td> <td>law, universal scaling, architecture-wide result, causal language beyond the fitted variables</td> </tr> <tr> <td>L4 - Generalized Finding</td> <td>The finding holds across named stacks, units, or calibrated boundaries under stated limits.</td> <td>Independent replication across a second target or second unit; strict-valid bundles; n and order rules satisfied per condition; named calibration bundles for cross-boundary quantitative comparison; replicated runbook; sensitivity audit survives boundary and version changes.</td> <td>unqualified claims outside tested hardware, workloads, runtime versions, policies, or calibration scope</td> </tr> </tbody></table></div> <h2 id="downgrade-examples">Downgrade Examples</h2> <ul> <li>Two strict-valid Mac/MLX/powermetrics points that differ in model size, architecture, and quantization are hypothesis-generating for Q4. They are not an active-parameter scaling result.</li> <li>A same-boundary energy/token difference with runtime-observed token counts but fewer than five interleaved repetitions is L1 until the comparative protocol is satisfied.</li> <li>A per-token result using configured output length because runtime token counts were unavailable is L0 capability language, even if the bundle is otherwise strict-valid.</li> </ul> </div> </div> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>docs/contracts/claims_ladder.md · commit db150a0 · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/paper/draft-v1.md:18:4. (C-iv) full instrument characterization: linearity, null response across magnitudes, empirical floor verification, phase-attribution causal consistency, drift/settle;
docs/paper/draft-v1.md:147:| Linearity | Hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. Regress gross request and decode energy on the runtime-observed output count; inspect residual structure as well as the fitted slope. | Energy responds proportionally over the tested dynamic range, and the fitted per-token slope can serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
docs/paper/draft-v1.md:149:| Empirical floor verification | Use the pre-registered linearity slope to create micro-deltas with predicted effects near 0.5, 1, 1.5, and 3 times the declared floor. Test positive and negative directions in counterbalanced blocks. | Sub-floor effects are refused while sufficiently super-floor effects clear in both directions. This is an operational check of the detection boundary, not a validation of the counter's absolute gain. | **[PENDING WINDOW C]** |
docs/paper/draft-v1.md:150:| Phase-attribution causal consistency | First compare the sum of separately integrated phase energies with the gross energy over their enclosing request. Then vary output length while holding prompt tokens fixed and fit the slope of prefill energy against output length. | Phase accounting is additive within its stated boundaries, and energy assigned to prefill does not acquire a systematic dependence on work that occurs later in decode. Together these tests challenge both missing energy and cross-phase leakage. | **[PENDING WINDOW C]** |
docs/paper/draft-v1.md:154:Linearity and the null ladder test complementary failure modes. A smooth response can still carry an offset, and a zero-centered null can coexist with a nonlinear scale. The micro-delta experiment then closes the loop by using the measured slope to place effects deliberately below and above the declared decision boundary. Success requires the instrument to refuse the former and resolve the latter in both directions; merely observing larger effects with larger workloads is not sufficient.
docs/paper/draft-v1.md:156:The causal tests address the most important phase-specific risk. Additivity checks conservation inside the declared request boundary: phase intervals should reconcile with the enclosing total, subject to explicitly labeled setup or gap intervals. Causal invariance checks direction: holding the prompt fixed while increasing later decode work should not change energy attributed to earlier prefill. A nonzero prefill slope would indicate boundary leakage, shared-state coupling that invalidates the simple phase model, or both; it would narrow the claim rather than be explained away.
docs/stream_logs/2026-07-07-2k-nvidia.md:150:Evidence: lens memos §Q4; conversion rule is orchestrator synthesis (neither
docs/site/research.html:17:</header> <main> <section class="learn-hero"> <div class="kicker">Interactive field guide · programming knowledge assumed · measurement science taught here</div> <p class="readme-eyebrow">From watts to warranted claims.</p> <h1>How do you measure<br>a machine thinking?</h1> <p class="lede">You already know how programs execute. This guide adds the uncomfortable part: deciding which physical signal belongs to the program, how much noise the instrument adds, and what the evidence actually permits you to say.</p> <nav class="chapter-nav" aria-label="Guide chapters"> <a href="#hard">The hard part</a><a href="#units">Watts &amp; joules</a> <a href="#sampling">Sampling</a><a href="#bundles">Bundles</a> <a href="#floor">Detection floors</a><a href="#found">Findings</a> <a href="#next">Next</a> </nav> <div class="provenance-plate"><span class="source-chip" title="docs/contracts/measurement_methodology.md · commit 6d80039"><span class="source-file">docs/<wbr>contracts/<wbr>measurement_methodology.md</span><span class="source-commit">commit 6d80039</span></span> <span class="source-chip" title="docs/site_src/research.html · commit 05002b1"><span class="source-file">docs/<wbr>site_src/<wbr>research.html</span><span class="source-commit">commit 05002b1</span></span></div> </section> <section class="learn-chapter" id="hard"> <div class="chapter-number">01</div> <div class="chapter-copy"> <div class="kicker">Why this is hard</div> <h2>The model does not come with an energy return value.</h2> <p class="chapter-lede">A profiler can tell you which function consumed CPU time. Energy is a physical quantity observed through a separate instrument. You have to align two clocks, define a boundary, and decide what else was happening while the model ran.</p> <div class="concept-grid"> <article><span>Boundary</span><h3>Which power?</h3><p>SoC rails omit parts of the whole machine. Wall power includes more than the chip. Neither is automatically wrong; an unlabeled boundary is.</p></article> <article><span>Attribution</span><h3>Which interval?</h3><p>Load the model too late or stop sampling too early and the number answers a different question than the experiment config asked.</p></article> <article><span>Workload</span><h3>Which work?</h3><p>Prompt length, generated tokens, batching, caching, stop behavior, and content can all change the physical execution.</p></article> <article><span>Noise</span><h3>Which difference?</h3><p>Background activity, thermal state, sampling cadence, clock error, and run order can manufacture a small “effect.”</p></article> </div> <aside class="learn-aside"><strong>The measurement-science move:</strong> replace “I got a number” with “I defined a quantity, captured the evidence, bounded what could imitate it, and stated the claim ceiling.”</aside> </div> </section> <section class="learn-chapter" id="units"> <div class="chapter-number">02</div> <div class="chapter-copy"> <div class="kicker">Watts, joules, and idle</div> <h2>Power is a rate. Energy is the area.</h2> <p class="chapter-lede">A watt is one joule per second. If power changes over time, energy is the integral under the power trace. That identity is a unit definition—not a JouleWise measurement result.</p> <div class="equation-stack"> <div><span>instantaneous power</span><strong>P(t)</strong><small>watts = joules / second</small></div> <div><span>gross measured energy</span><strong>E = ∫ P(t) dt</strong><small>headline basis within the named boundary</small></div> <div><span>idle-subtracted energy</span><strong>E<sub>secondary</sub> = ∫ (P(t) − P<sub>idle</sub>) dt</strong><small>within-device secondary view only</small></div> </div> <p>Idle is not “free energy to erase.” It is an observed baseline under a stated condition. Subtracting it can help describe activity above baseline on one device, but it can distort comparisons: a high-idle device gets a larger subtraction. JouleWise therefore uses <strong>gross energy for every cross-device, cross-configuration, and split-vs-monolithic headline</strong>. Phase energy is gross-only.</p> <div class="provenance-plate"><span class="source-chip" title="docs/contracts/measurement_methodology.md · commit 6d80039"><span class="source-file">docs/<wbr>contracts/<wbr>measurement_methodology.md</span><span class="source-commit">commit 6d80039</span></span></div> </div> </section> <section class="learn-chapter" id="sampling"> <div class="chapter-number">03</div> <div class="chapter-copy"> <div class="kicker">How powermetrics sampling works</div> <h2>You never see the continuous curve.</h2> <p class="chapter-lede"><code>powermetrics</code> reports discrete samples from named Apple power rails. JouleWise aligns those samples with runtime events and integrates between explicit measured-window boundaries. Move the toy controls below: the underlying program is unchanged, but the estimated area changes when the window or sample pattern changes.</p> <div class="interactive-card" data-trace-lab> <div class="interactive-head"><div><span class="card-label">Toy trace · illustrative, not project evidence</span><h3>Drag the window and sample controls.</h3></div><span class="status-chip amber">local-only SVG + JS</span></div> <svg class="power-lab" viewBox="0 0 720 290" role="img" aria-labelledby="traceTitle traceDesc"> <title id="traceTitle">Interactive toy power trace</title> <desc id="traceDesc">A toy idle, prefill, decode, and cooldown power curve with adjustable integration window and sample points.</desc> <g class="lab-grid"><line x1="56" y1="35" x2="56" y2="246"/><line x1="56" y1="246" x2="694" y2="246"/><line x1="56" y1="176" x2="694" y2="176"/><line x1="56" y1="106" x2="694" y2="106"/><line x1="56" y1="36" x2="694" y2="36"/></g> <text class="lab-axis" x="12" y="42">power</text><text class="lab-axis" x="649" y="276">time →</text> <rect class="lab-window" data-window x="180" y="36" width="390" height="210"/> <path class="lab-area" data-trace-area d=""/><path class="lab-line" data-trace-line d=""/> <g data-samples></g> <line class="lab-handle" data-start-line x1="180" y1="30" x2="180" y2="252"/> <line class="lab-handle" data-end-line x1="570" y1="30" x2="570" y2="252"/> <text class="lab-label" x="82" y="226">idle</text><text class="lab-label" x="243" y="62">prefill</text><text class="lab-label" x="405" y="105">decode</text><text class="lab-label" x="600" y="226">cooldown</text> </svg> <div class="lab-controls"> <label>window start <input data-start type="range" min="5" max="70" value="22"><output data-start-out>22%</output></label> <label>window end <input data-end type="range" min="30" max="98" value="82"><output data-end-out>82%</output></label> <label>sample spacing <input data-spacing type="range" min="3" max="16" value="7"><output data-spacing-out>7%</output></label> <label>sample phase <input data-phase type="range" min="0" max="100" value="28"><output data-phase-out>28%</output></label> </div> <div class="lab-readouts" aria-live="polite"> <div><span>Toy gross energy · illustrative gross basis</span><strong data-gross-out>—</strong></div> <div><span>Toy idle-subtracted energy · illustrative within-device secondary</span><strong data-idle-out>—</strong></div> <div><span>Samples inside measured window</span><strong data-count-out>—</strong></div> </div> <p class="interactive-note">The orange curve is an invented signal. Cyan dots are discrete samples; the shaded band is the measured window. Real JouleWise bundles retain the trace and event markers so the integration can be replayed rather than trusted.</p> </div> </div> </section> <section class="learn-chapter" id="bundles"> <div class="chapter-number">04</div> <div class="chapter-copy"> <div class="kicker">Strict validation and bundles</div> <h2>A bundle is a proof packet, not a CSV export.</h2> <p class="chapter-lede">The run directory is deliberately boring: normalized configuration, metadata, timestamped events, raw power evidence, logs, model outputs, and summary metrics. The interesting part is what strict validation does with it.</p> <div class="bundle-diagram" role="img" aria-label="Run bundle artifacts flow through strict validation to a bounded claim"> <div class="bundle-box"><span>run bundle</span><code>config.json</code><code>metadata.json</code><code>events.jsonl</code><code>raw telemetry</code><code>outputs + logs</code><code>summary metrics</code></div> <div class="bundle-arrow">replay →</div> <div class="bundle-box validator-box"><span>strict validator</span><p>parse raw evidence</p><p>re-derive windows</p><p>recompute energy</p><p>check provenance</p><p>fail on mismatch</p></div> <div class="bundle-arrow">gate →</div> <div class="bundle-box claim-box"><span>claim ceiling</span><p>L0: auditability</p><p>L1: descriptive</p><p>L2+: only after floor, uncertainty, plan, and evidence gates</p></div> </div> <p><strong>Strict-valid does not mean scientifically conclusive.</strong> It means the recorded artifact is internally valid under the strict contract. A bundle can be strict-valid and still carry flags that prevent a comparison claim. That distinction matters in the newest floor data.</p> <div class="provenance-plate"><span class="source-chip" title="docs/contracts/claims_ladder.md · commit db150a0"><span class="source-file">docs/<wbr>contracts/<wbr>claims_ladder.md</span><span class="source-commit">commit db150a0</span></span></div> </div> </section> <section class="learn-chapter" id="floor"> <div class="chapter-number">05</div> <div class="chapter-copy"> <div class="kicker">Detection floors</div> <h2>How small is too small to resolve?</h2> <p class="chapter-lede">Repeat the same condition and the measured energy moves anyway. The false-effect guard floor summarizes how large that repeat scatter—or an ABBA comparison artifact—can look. An effect below the applicable floor is <strong>not resolvable</strong>, not proven absent.</p> <div class="interactive-card floor-lab" data-floor-lab> <div class="interactive-head"><div><span class="card-label">Effect-versus-floor gate</span><h3>Try to clear a real verified floor.</h3></div><span class="status-chip">calibration logic</span></div> <label class="floor-select">Choose the applicable gate <select data-floor-select> <option value="0.527197" data-basis="gross request · absolute repeat">Gross mid-request absolute · 0.527197 J</option> <option value="0.909237" data-basis="gross request · comparative ABBA">Gross mid-request comparative · 0.909237 J</option> <option value="0.536632" data-basis="idle-subtracted request · within-device secondary">Idle-subtracted mid-request absolute · 0.536632 J</option> <option value="0.894215" data-basis="idle-subtracted request · within-device secondary comparative">Idle-subtracted mid-request comparative · 0.894215 J</option> <option value="1.738940" data-basis="gross prefill phase · governing gate">Gross prefill phase gate · 1.738940 J</option> <option value="1.026892" data-basis="gross decode phase · governing gate">Gross decode phase gate · 1.026892 J</option> <option value="4.922865" data-basis="gross suite-item · governing gate">Gross suite-item gate · 4.922865 J</option> <option value="24.618735" data-basis="gross suite-level · governing gate">Gross suite-level gate · 24.618735 J</option> </select> </label> <label class="effect-control">Hypothetical observed effect <input data-effect type="range" min="0" max="30" value="0.70" step="0.01"> <output data-effect-out>0.70 J</output> </label> <div class="floor-track" aria-hidden="true"><span data-floor-mark></span><i data-effect-mark></i></div> <div class="floor-verdict" data-floor-verdict aria-live="polite"></div> <p class="interactive-note">Clearing this numeric gate is necessary, not sufficient. It does not clear clock, sampling, uncertainty, contamination, multiplicity, correctness, or pre-registered analysis-plan gates.</p> </div> <div class="provenance-plate"><span class="source-chip" title="docs/phase_2/detection_floor.md · commit 907ee58"><span class="source-file">docs/<wbr>phase_2/<wbr>detection_floor.md</span><span class="source-commit">commit 907ee58</span></span></div> </div> </section> <section class="learn-chapter" id="found"> <div class="chapter-number">06</div> <div class="chapter-copy"> <div class="kicker">What the project has found so far</div> <h2>Real floors, plus an important warning.</h2> <p class="chapter-lede">The verified Window-A extraction reports the following false-effect guard floors. Comparative values use ABBA blocks; “gate” is the larger applicable absolute/comparative value. Every energy number states its D-067 basis.</p> <div class="table-scroll"> <table class="ledger measurement-table learn-floor-table"> <thead><tr><th>window</th><th>energy basis</th><th>verified floor</th><th>how to read it</th></tr></thead> <tbody> <tr><td>mid request · absolute</td><td>gross · headline</td><td>0.527197 J</td><td>repeat-scatter floor</td></tr> <tr><td>mid request · comparative</td><td>gross · headline</td><td>0.909237 J</td><td>ABBA comparison floor</td></tr> <tr><td>mid request · absolute</td><td>idle-subtracted · within-device secondary</td><td>0.536632 J</td><td>repeat-scatter floor</td></tr> <tr><td>mid request · comparative</td><td>idle-subtracted · within-device secondary</td><td>0.894215 J</td><td>ABBA comparison floor</td></tr> <tr><td>prefill phase</td><td>gross · phase basis</td><td>1.738940 J</td><td>governing gate</td></tr> <tr><td>decode phase</td><td>gross · phase basis</td><td>1.026892 J</td><td>governing gate</td></tr> <tr><td>suite item</td><td>gross · headline</td><td>4.922865 J</td><td>governing gate</td></tr> <tr><td>suite level</td><td>gross · headline</td><td>24.618735 J</td><td>governing gate</td></tr> </tbody> </table> </div> <aside class="evidence-warning"><strong>The warning is part of the result.</strong> The floor collection is strict-valid and collection-usable, yet every contributing bundle is claim-evidence flagged. Universal clock-bound and in-window-sample flags, plus drift/cooldown concerns in several comparative cells, mean these values are calibration evidence pending adjudication—not a license for an L2/L3 comparison claim.</aside> <p class="source-path">Cited artifact: <a href="https://github.com/mpmdw/JouleWise/blob/main/docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json"><code>docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json</code></a> </p> <div class="provenance-plate"><span class="source-chip" title="docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json · commit b28c895"><span class="source-file">docs/<wbr>process_traces/<wbr>2026-07-17-floor-extraction/<wbr>extraction-verified.json</span><span class="source-commit">commit b28c895</span></span></div> </div> </section> <section class="learn-chapter" id="next"> <div class="chapter-number">07</div> <div class="chapter-copy"> <div class="kicker">What comes next</div> <h2>Turn calibration into governed comparisons.</h2> <div class="next-grid"> <article><span>Adjudicate</span><h3>Resolve the evidence flags.</h3><p>Decide whether clock-bound, cadence, drift, and cooldown evidence allows these floors to govern later claims or requires a revised capture.</p></article> <article><span>Baseline</span><h3>Run the controlled Mac campaign.</h3><p>Use counterbalanced order, fixed workloads, strict-valid bundles, and the applicable floor gates before interpreting model differences.</p></article> <article><span>Stress</span><h3>Test the energy model.</h3><p>Batching, speculative decoding, MoE versus dense execution, quantization, and reasoning length probe where the fixed-plus-marginal model holds or breaks.</p></article> <article><span>Extend</span><h3>Add hardware without changing honesty.</h3><p>Remote NVIDIA and Orin paths remain provisional until live contact. Cross-device headlines stay gross-first and boundary-labeled.</p></article> </div> <div class="research-questions"> <h3>The research arc</h3> <p><strong>Q1:</strong> when can split inference reduce total gross energy? <strong>Q2:</strong> how does interconnect bandwidth move that crossover? <strong>Q3:</strong> what is the energy–latency trade? <strong>Q4:</strong> what fixed-plus-marginal model describes each target? <strong>Q5:</strong> where do efficiency rankings flip? <strong>Q6:</strong> how sensitive are conclusions to the measurement boundary?</p> </div> <div class="readme-actions"><a href="status.html">Read current status</a><a href="roadmap.html">Inspect the governed queue</a><a href="results.html">Open the measurement ledger</a></div> </div> </section> <script>var svgNS="http://www.w3.org/2000/svg",traceLab=document.querySelector("[data-trace-lab]");if(traceLab){let u=function(e){return e<.2?4.8+.25*Math.sin(e*70):e<.31?7+118*(e-.2)+2*Math.sin(e*55):e<.69?13.7+1.2*Math.sin(e*48)+.5*Math.sin(e*117):e<.82?13.2-62*(e-.69):4.9+.22*Math.sin(e*64)},r=function(e){return x0+(x1-x0)*e},i=function(e){return yBottom-e/22*(yBottom-yTop)},d=function(){var e=Number(startInput.value)/100,a=Number(endInput.value)/100;a-e<.08&&(document.activeElement===startInput?e=a-.08:a=e+.08,startInput.value=String(Math.round(e*100)),endInput.value=String(Math.round(a*100)));var v=Number(spacingInput.value)/100,F=Number(phaseInput.value)/100*v,c=r(e),f=r(a),h=traceLab.querySelector("[data-window]");h.setAttribute("x",c.toFixed(1)),h.setAttribute("width",(f-c).toFixed(1)),traceLab.querySelector("[data-start-line]").setAttribute("x1",c.toFixed(1)),traceLab.querySelector("[data-start-line]").setAttribute("x2",c.toFixed(1)),traceLab.querySelector("[data-end-line]").setAttribute("x1",f.toFixed(1)),traceLab.querySelector("[data-end-line]").setAttribute("x2",f.toFixed(1));var y=traceLab.querySelector("[data-samples]");y.textContent="";for(var o=[],n=F;n<=1.0001;n+=v){var s=document.createElementNS(svgNS,"circle"),S=u(n);s.setAttribute("cx",r(n).toFixed(1)),s.setAttribute("cy",i(S).toFixed(1)),s.setAttribute("r",n>=e&&n<=a?"4.2":"2.7"),s.setAttribute("class",n>=e&&n<=a?"lab-sample in-window":"lab-sample"),y.appendChild(s),n>=e&&n<=a&&o.push([n,S])}for(var b=0,x=0,q=4.8,l=1;l<o.length;l+=1){var g=(o[l][0]-o[l-1][0])*10;b+=g*(o[l][1]+o[l-1][1])/2,x+=g*(Math.max(0,o[l][1]-q)+Math.max(0,o[l-1][1]-q))/2}traceLab.querySelector("[data-start-out]").textContent=Math.round(e*100)+"%",traceLab.querySelector("[data-end-out]").textContent=Math.round(a*100)+"%",traceLab.querySelector("[data-spacing-out]").textContent=Math.round(v*100)+"%",traceLab.querySelector("[data-phase-out]").textContent=phaseInput.value+"%",traceLab.querySelector("[data-gross-out]").textContent=o.length>1?b.toFixed(2)+" toy J":"too few samples",traceLab.querySelector("[data-idle-out]").textContent=o.length>1?x.toFixed(2)+" toy J":"too few samples",traceLab.querySelector("[data-count-out]").textContent=String(o.length)};for(var powerAt=u,xFor=r,yFor=i,renderTrace=d,startInput=traceLab.querySelector("[data-start]"),endInput=traceLab.querySelector("[data-end]"),spacingInput=traceLab.querySelector("[data-spacing]"),phaseInput=traceLab.querySelector("[data-phase]"),x0=56,x1=694,yBottom=246,yTop=36,lineParts=[],areaParts=["M "+r(0)+" "+yBottom],point=0;point<=96;point+=1){var t=point/96,command=point===0?"M":"L";lineParts.push(command+" "+r(t).toFixed(1)+" "+i(u(t)).toFixed(1)),areaParts.push("L "+r(t).toFixed(1)+" "+i(u(t)).toFixed(1))}areaParts.push("L "+r(1)+" "+yBottom+" Z"),traceLab.querySelector("[data-trace-line]").setAttribute("d",lineParts.join(" ")),traceLab.querySelector("[data-trace-area]").setAttribute("d",areaParts.join(" ")),[startInput,endInput,spacingInput,phaseInput].forEach(function(e){e.addEventListener("input",d)}),d()}var floorLab=document.querySelector("[data-floor-lab]");if(floorLab){let u=function(){var r=floorSelect.options[floorSelect.selectedIndex],i=Number(r.value),d=Number(effectInput.value),e=d>=i;floorLab.querySelector("[data-effect-out]").textContent=d.toFixed(2)+" J",floorLab.querySelector("[data-floor-mark]").style.left=Math.min(100,i/30*100)+"%",floorLab.querySelector("[data-effect-mark]").style.left=Math.min(100,d/30*100)+"%";var a=floorLab.querySelector("[data-floor-verdict]");a.className="floor-verdict "+(e?"clears":"below"),a.innerHTML=e?"<strong>Above this numeric floor.</strong><span>"+d.toFixed(2)+" J clears "+i.toFixed(6)+" J on the "+r.dataset.basis+" gate. Other claim gates still apply.</span>":"<strong>Not resolvable at this gate.</strong><span>"+d.toFixed(2)+" J is below "+i.toFixed(6)+" J on the "+r.dataset.basis+" gate. This does not prove zero effect.</span>"};var renderFloor=u,floorSelect=floorLab.querySelector("[data-floor-select]"),effectInput=floorLab.querySelector("[data-effect]");floorSelect.addEventListener("change",u),effectInput.addEventListener("input",u),u()}</script> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>docs/site_src/research.html · commit 05002b1 · docs/contracts/measurement_methodology.md · commit 6d80039 · docs/phase_2/detection_floor.md · commit 907ee58 · docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json · commit b28c895 · docs/contracts/claims_ladder.md · commit db150a0 · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/site/project_status.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Project Status - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html" class="active">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#current-repository-view-30-second-read">Current Repository View — 30-second read</a> <a href="#previous-update-as-of-2026-07-09-c-027-whole-project-council-review-30-second-read">Previous Update (as of 2026-07-09, C-027 whole-project council review) — 30-second read</a> <a href="#previous-update-as-of-2026-07-09-advisor-status-cockpit-30-second-read">Previous Update (as of 2026-07-09, advisor status cockpit) — 30-second read</a> <a href="#previous-update-as-of-2026-07-08-all-four-streams-merged-30-second-read">Previous Update (as of 2026-07-08, all four streams merged) — 30-second read</a> <a href="#previous-update-2026-07-07-fifth-update-30-second-read">Previous Update (2026-07-07, fifth update) — 30-second read</a> <a href="#previous-update-2026-07-07-fourth-update-30-second-read">Previous Update (2026-07-07, fourth update) — 30-second read</a> <a href="#update-ledger">Update Ledger</a></aside> <div class="doc-wrap doc-source-project-status-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>PROJECT_STATUS.md</code></p> <div class="provenance-plate"><span class="source-chip" title="PROJECT_STATUS.md · commit 1af9f92"><span class="source-file">PROJECT_STATUS.md</span><span class="source-commit">commit 1af9f92</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>JouleWise: Project Status, Plan, And Architecture</h1> <p>Audience: project advisor. This is the standalone monitoring document - it summarizes what the project is, how it is built, where it stands, and what it needs, without requiring any other file. Pointers into the repository are provided for anyone who wants the full evidence trail.</p> <ul> <li>Freshness owner: phase completion lives in the phase exit checklists; live gates and work selection live only in the generated state-kernel regions of <code>RUN_STATE.md</code> and <code>TASK_QUEUE.md</code>; the canonical suite command and CI own the current verification result. This page deliberately does not duplicate volatile commit, pull-request, queue, or test-count facts.</li> <li>Repository state: <code>main</code> contains the repaired measurement instrument (D-078 phase 0) and the audited screening and uncertainty-budget rules (D-078 clause 10; council C-033). The repaired-instrument collection has 229 members across four bracketed windows, a5-a8. Those windows are useful diagnostic evidence that the instrument works, but they are not claim-bearing and do not yet publish a floor. The next step is one clean prospective quiet-machine collection following <code>docs/phase_2/window_runbook.md</code>; if it passes, it will produce the first claim-grade floors before the a8 re-verdict and Splitwise sizing.</li> <li>Project phase: see the phase exit checklists for exact completion state; live eligibility and next work come from the generated state kernel, not this reader-facing summary.</li> <li>Repository: <code>github.com/mpmdw/JouleWise</code> (branch <code>main</code>)</li> <li>Live status site: <a href="https://quiet-signal-6af8833395.lakebed.app">https://quiet-signal-6af8833395.lakebed.app</a> (Lakebed capsule; it is an Ed-deployed snapshot, not the repository authority. <code>docs/site/DRIFT.md</code> records known differences; agents refresh that report when front-facing state changes and never regenerate or deploy the site.)</li> </ul> <h2 id="current-repository-view-30-second-read">Current Repository View — 30-second read</h2> <p><strong>The repaired instrument has completed its first collection era, but the first claim-grade floor is still ahead.</strong> The D-078 phase-0 repair fixed the timing and calibration path on 2026-07-22. Four bracketed windows then collected 229 strict members (a5-a8). They are retained as non-claim-bearing diagnostic, instrument-proving evidence: they showed that the repaired path works and exposed the remaining drift-screen problem, but they are not a published floor set.</p> <p>That problem is now resolved in the merged SCREEN+BUDGET rules (D-078 clause 10). Gross and idle-subtracted energy are screened separately; each passing window keeps a nonzero drift allowance in its uncertainty budget; the drift bound expires after 24 hours; fallback-clock members cannot support a floor; and mock evidence is identified from the bound configuration and barred from claims. The next quiet session will mint its bound inside the window and collect three start references, one midpoint reference, and three end references. The older 222-bundle floor table below remains visible as a caveated historical record, not the current measurement posture.</p> <p>AXI-SB remains <code>supported</code> for native static-batch runtime feasibility with request-scoped observability; AXI-SC is <code>unsupported_for_joulewise</code> on the pinned runtime because the required speculative-decode/MTP observability or execution surface is absent. Neither verdict is an energy result. Remote protocol pins remain PROVISIONAL, and the generated state kernel remains the work-selection authority.</p> <h3>Published Window-A floor summary</h3> <blockquote> <p><strong>CAVEAT (2026-07-19 soundness audit):</strong> a trace-time-anchor defect was found in the powermetrics evidence path (power timestamps misaligned with runtime events at the ~0.5–1 s scale). It affects the corpora behind this table; every row below is <strong>under re-adjudication</strong> and none should be cited as a promoted floor until the instrument is repaired and the rows re-extracted. Record: <code>docs/reviews/2026-07-19-measurement-soundness-audit.md</code>.</p> </blockquote> <p>Every energy value below is a false-effect guard floor in joules on the <strong>Apple M3 Max / powermetrics SoC-rail boundary (CPU + GPU + ANE)</strong>. Gross is the D-067 headline basis; idle-subtracted values are labeled within-device secondary views. Absolute rows use repeated identical conditions; comparative rows use same-condition ABBA blocks. Each primary row uses <code>n=10</code> strict-valid bundles or ABBA blocks.</p> <div class="table-scroll"><table> <thead> <tr> <th>window / basis</th> <th align="right">absolute floor</th> <th align="right">comparative floor</th> <th align="right">computed <code>floor_gate_j</code> / disposition</th> </tr> </thead> <tbody><tr> <td>mid request, gross — M3 Max / powermetrics SoC rails</td> <td align="right">0.527 J</td> <td align="right">0.909 J</td> <td align="right">0.909 J</td> </tr> <tr> <td>mid request, idle-subtracted — M3 Max / powermetrics SoC rails</td> <td align="right">0.537 J</td> <td align="right">0.894 J</td> <td align="right">0.894 J; within-device secondary</td> </tr> <tr> <td>short request, gross — M3 Max / powermetrics SoC rails</td> <td align="right">0.052 J</td> <td align="right">—</td> <td align="right">absolute floor only</td> </tr> <tr> <td>short request, idle-subtracted — M3 Max / powermetrics SoC rails</td> <td align="right">0.059 J</td> <td align="right">—</td> <td align="right">absolute floor only; within-device secondary</td> </tr> <tr> <td>prefill phase, gross — M3 Max / powermetrics SoC rails</td> <td align="right">1.477 J</td> <td align="right">1.739 J</td> <td align="right">1.739 J</td> </tr> <tr> <td>decode phase, gross — M3 Max / powermetrics SoC rails</td> <td align="right">0.786 J</td> <td align="right">1.027 J</td> <td align="right">1.027 J</td> </tr> <tr> <td>short-prefill stress, gross — M3 Max / powermetrics SoC rails</td> <td align="right">0.027 J</td> <td align="right">—</td> <td align="right">smoke-only; <code>not_resolvable_sample_count</code></td> </tr> <tr> <td>suite item, gross — M3 Max / powermetrics SoC rails</td> <td align="right">0.333 J</td> <td align="right">4.923 J</td> <td align="right">4.923 J; drift review required</td> </tr> <tr> <td>suite level, gross — M3 Max / powermetrics SoC rails</td> <td align="right">1.664 J</td> <td align="right">24.619 J</td> <td align="right">24.619 J; drift review required</td> </tr> </tbody></table></div> <p>The start/end NEG-8 reference pair is an <code>n=2</code> drift diagnostic, not a campaign floor. Its gross request energy moved by 7.659 J; the idle-subtracted within-device secondary view moved by 6.608 J (same boundary). Verified extraction: <code>docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json</code>; reader deliverable: <code>docs/advisor_briefs/2026-07-17-window-a-brief.html</code>.</p> <h3>2026-07-19 re-calibration under the environment guard — PRELIMINARY</h3> <p>The caveated suite rows were re-measured in two bracketed windows under the D-077 guard: <strong>94 strict-valid bundles</strong>, all admission predicates satisfied. Reviewed readout: suite gross <strong>147.96 ± 0.39 J</strong> clean (contaminated cells were ~+30%); frozen-estimator provisional comparative floor <strong>≈ 1.13 J (~0.77%)</strong> from 5 of 10 planned ABBA blocks (~22× tighter, same estimator, than the caveated figure); long-decode <strong>83.9 mJ/output-token</strong>, matching the 07-17 decode cell to ~0.1%. That corpus was claim-ineligible on source provenance (dirty collection tree); details: <code>docs/advisor_briefs/2026-07-19-recalibration-update.html</code>.</p> <p>UPDATE (2026-07-19 night): the clean re-run is done — 288 strict-valid bundles with clean source provenance (<code>runs_recal3/4/5/6_20260719/</code>) cover every planned Window-A cell except DF-TELEM at planned n, including the complete n=10 suite-ABBA comparative cell; the source provenance gate is closed. <strong>SUPERSEDING UPDATE (2026-07-19/20): a same-day soundness audit found a timing bug, and no energy number from the existing recordings will be used for claims until re-measurement.</strong> In plain terms: the power meter and the workload log time on two different clocks, and our alignment between them could be off by up to ~1 second. Energy is computed by summing meter samples inside the workload&#39;s start/stop window, so a misaligned window integrates the wrong slice of the recording — dramatic for sub-second test runs (one 0.37 s run read 0.27 J when its true consumption, plainly present in the recording, was <del>8 J), and a meaningful hidden uncertainty (</del>±10 J) even on 60-second runs. Nothing measured negative; the recordings are intact and self-consistent; long-run repeatability (~0.3% across nights) shows the platform is stable. Very short workloads are simply below this instrument&#39;s resolution and will not be claimed — by design, not workaround. The fix (align on the meter&#39;s own timestamps, attach an explicit uncertainty range to every number, calibrate end-to-end with 40 precisely-timed GPU bursts before new data) is implemented and in adversarial review. Plain-language explainer: <code>docs/advisor_briefs/2026-07-20-timing-defect-explainer.md</code>; technical record: <code>docs/reviews/2026-07-19-measurement-soundness-audit.md</code>.</p> <p><strong>REPAIR COMPLETE (2026-07-22): the instrument repair is finished and signed off.</strong> Over three days the timing defect was fixed and the whole measurement chain was hardened through nine rounds of independent adversarial review (each round tried to break the instrument; the last round found one remaining gap, recorded below). In plain terms, the instrument now: (a) knows precisely when its power readings happened relative to the model&#39;s work (the clock-alignment fix, with the alignment uncertainty — about 27 milliseconds — carried into every result as an explicit error bar); (b) proves its own calibration is genuine and fresh — a calibration recording that was tampered with, mislabeled, taken under the wrong procedure, or older than 24 hours is automatically rejected; and (c) refuses to report a result rather than report a doubtful one, in every failure case we could construct. One known limitation is recorded honestly: the file that stores the detection-floor statistics is not yet cryptographically tied back to the raw measurements it came from, so we only trust such files when our own pipeline produced them in the same verified session (a fix is queued). Live validation on the real hardware passed: the validation recording (made under the earlier 40-pulse calibration procedure) detected all 40 calibration pulses with no false detections, and a test measurement reproduced the expected physics where the old defective pipeline had been wrong by a factor of ~28. Production measurements will use the newer 59-pulse calibration procedure, which supports the stronger statistical guarantee we quote for the timing error bar. Next: a fresh calibration and re-collection of the measurement campaign under the repaired instrument. Record: <code>docs/run_reports/2026-07-20-p0-instrument-repair.md</code>.</p> <p><strong>COLLECTION ERA UPDATE (2026-07-24): the repaired instrument has now been proven in production.</strong> Over two nights we collected 229 clean measurements across four properly-bracketed windows. The standout result: two identical reference measurements taken three hours apart agreed to within 0.007 joules on a ~38.5 joule task — about 0.02%, which is excellent repeatability for whole-system power measurement. The windows are not yet &quot;claim-grade&quot; for one honest reason: our own stability check (comparing a reference task at each window&#39;s start and end) was found to be asking a mathematically unanswerable question, so it failed every window on a technicality while the underlying data was good. After a formal debate between the two AI models working on the project — which the reviewing model won on one substantive point — the check was redesigned and ratified: windows are now screened for anomalous drift against a limit derived from measured repeatability (instead of an arbitrary constant), and any drift observed is carried into the results&#39; error bars rather than being ignored once a window &quot;passes&quot;. Reference measurements are also being tripled at each window edge. One collection session under the new rules produces the project&#39;s first claim-grade detection-floor table, which then sizes the Splitwise replication experiments. Records: <code>docs/run_reports/2026-07-23-window-a-collection-arc.md</code>, decision log D-078 clauses 8-10.</p> <p><strong>SCREENING RULES BUILT, AUDITED, AND MERGED (2026-07-25; council C-033).</strong> The redesigned stability screen described above is now implemented and on main: both energy families are screened separately, every passing window carries an explicit drift allowance into its error bars, drift limits expire after 24 hours so stale calibrations cannot be reused, and a measurement whose internal clock had to be guessed can never anchor a result (that one rule alone corrected a floor that was overstated by roughly a factor of three). The code went through an unusually deep adversarial review — four independent audit rounds and three rounds of cross-examination between two different AI models — which caught and fixed several ways the new rules could have been silently bypassed. The step-by-step measurement procedure for the next collection session is written up in <code>docs/phase_2/window_runbook.md</code>. Records: <code>docs/run_reports/2026-07-24-screen-budget-gauntlet.md</code>, council log C-033.</p> <h3>Exploratory follow-on — not a promoted claim</h3> <p>Nine additional strict-valid, collection-usable bundles cover three repetitions each of unmatched OLMoE-1B-7B BF16, Qwen3-4B INT4, and Qwen3.5-122B-A10B INT4 configurations on the fixed five-item <code>jw_mixed_v1_sentinel</code> shape. Every bundle is claim-evidence-flagged, the model/config points differ in architecture, scale, tokenizer, and quantization, and the repetition count is below the headline protocol. The values are therefore descriptive <strong>EXPLORATORY / L1-legacy observations only</strong>.</p> <div class="table-scroll"><table> <thead> <tr> <th>unmatched configuration</th> <th align="right">mean gross suite energy — Apple M3 Max / powermetrics SoC rails (CPU + GPU + ANE)</th> <th align="right">mean gross energy/generated output token — same boundary</th> <th align="right">runtime-observed output throughput</th> </tr> </thead> <tbody><tr> <td>OLMoE-1B-7B BF16</td> <td align="right">229.028 J (227.141–231.790 J)</td> <td align="right">178.928 mJ/token (177.454–181.086 mJ/token)</td> <td align="right">122.361 tok/s (122.261–122.481 tok/s)</td> </tr> <tr> <td>Qwen3-4B INT4</td> <td align="right">362.772 J (362.642–362.903 J)</td> <td align="right">283.416 mJ/token (283.314–283.518 mJ/token)</td> <td align="right">106.519 tok/s (106.470–106.545 tok/s)</td> </tr> <tr> <td>Qwen3.5-122B-A10B INT4</td> <td align="right">1072.273 J (1061.722–1085.144 J)</td> <td align="right">837.713 mJ/token (829.471–847.769 mJ/token)</td> <td align="right">39.473 tok/s (39.349–39.569 tok/s)</td> </tr> </tbody></table></div> <p>Each bundle emitted 1,280 generated output tokens. Gross per-output-token values above are derived from the gross suite numerator; the stored <code>energy_output_token_j</code> field instead uses the idle-subtracted numerator and is retained as a labeled within-device secondary view in the full extraction. For the like-for-like suite-level gross window on the Apple M3 Max / powermetrics SoC-rail boundary, the exploratory OLMoE-versus-Qwen3-4B mean gap is 133.720 J, above the published 24.619 J suite-level gross <code>floor_gate_j</code>. That only says the descriptive gap exceeds the measurement guard: unmatched configurations, evidence flags, drift review, and the lack of a prospective contrast still prohibit efficiency or architecture claims. Every aggregate and raw repetition is bundle-cited in <code>docs/process_traces/2026-07-17-exploratory-block/results.md</code>.</p> <h2 id="previous-update-as-of-2026-07-09-c-027-whole-project-council-review-30-second-read">Previous Update (as of 2026-07-09, C-027 whole-project council review) — 30-second read</h2> <p><strong>The project put itself in front of a hostile examiner and corrected its own front page.</strong> A seven-lens cross-model review (new Codex model, extra-high reasoning) plus an independent final examiner audited the docs, the scientific claims, the statistics implementation, the architecture, and the operating loop itself. Verdict: the evidence discipline and instrument core are sound, but reader-facing claims had drifted from the evidence (the 1.5B per-token headline used the wrong denominator — now corrected as <strong>P2-003, idle-subtracted energy — M3 Max / powermetrics SoC rails:</strong> ~79-90 mJ per generated output token), the D-053 contrast-CI machinery exists as binding specs but not yet as code (now owned as queue rows P2-037..P2-042 and gating Window-A interpretation), and the loop&#39;s own audit trail and the capstone-critical path (grading rubric, report skeleton, off-machine backup, one data-to-figure slice) need attention before any new breadth. All measured values above remain legacy L1 preliminary observations. Full adjudicated record: <code>docs/reviews/2026-07-09-c027-whole-project-review.md</code>.</p> <h2 id="previous-update-as-of-2026-07-09-advisor-status-cockpit-30-second-read">Previous Update (as of 2026-07-09, advisor status cockpit) — 30-second read</h2> <p><strong>The public preview is being upgraded for live advisor observation.</strong> The project-status page remains generated from repository evidence, but Lakebed now has a narrow fail-soft live overlay contract: freshness from GitHub commit checks plus parsed current fields from <code>PROJECT_STATUS.md</code>, <code>RUN_STATE.md</code>, <code>TASK_QUEUE.md</code>, and the risk register. The advisor cockpit adds live snapshot state, attention items, campaign readiness, evidence cards, and claim-ceiling panels; the Story page drops hand-authored volatile counts. The operational policy is D-051: repo markdown remains the source of truth and Lakebed never hides static provenance. Current work follows <code>TASK_QUEUE.md</code>: C-019 shakedown, then P2-015 quiet calibration for Window A (the CP-5 stop card was cleared 2026-07-09).</p> <h2 id="previous-update-as-of-2026-07-08-all-four-streams-merged-30-second-read">Previous Update (as of 2026-07-08, all four streams merged) — 30-second read</h2> <p><strong>Everything landed.</strong> The multi-stream session merged as four PRs: P2-013 and P2-014 are closed — all 31 audit pins fixed, the suite passed with zero expected failures (current count authority is RUN_STATE.md Current Verification; the suite-build merge was 732 tests and the post-alignment state is 734), bundle provenance now records prompt/workload identities, and <code>validate-bundle --strict</code> includes the powermetrics raw-plist-to-trace gate plus the legacy additive-summary comparison. The six existing real corpus bundles pass strict read-only and unrewritten; strict proves re-derivation of the recorded evidence, not independent rerunning of the hardware session. New-era bundles must carry shape-valid provenance to pass. The Stage 3.0.1 KV spike is merged with a lead-reverified verdict of <code>replay_supported</code> (tokens identical; cache size +0.018% vs prediction) — Phase 3&#39;s central technical risk is retired on current hardware. The fixture-first 2K NVIDIA stack is merged; ALL its protocol pins remain PROVISIONAL until first live hardware contact (the live-verification checklist is ready). The independent project critique now carries a second-pass reassessment (its recommendations that became code are marked resolved; 16/17 of its checkable claims were lead-verified against file evidence): <code>docs/project_critique_review.html</code>. Next: the detection-floor calibration (P2-015) then the 2M two-model baseline campaign on a quiet machine. Reader-facing status below defers to the phase checklist matrix rows for per-item authority.</p> <h2 id="previous-update-2026-07-07-fifth-update-30-second-read">Previous Update (2026-07-07, fifth update) — 30-second read</h2> <p><strong>The instrument grew four capabilities in one session and is now campaign-ready.</strong> <em>(Historical claim; C-027 (2026-07-09) supersedes the gating: execution is conditioned on P0-003 backup, P2-038, P2-039, and P2-015-SMOKE.)</em> Five parallel work streams landed (PRs #2-#6): (1) <strong>statistical uncertainty</strong> — every multi-repetition experiment now carries per-metric 95% confidence intervals with outlier detection and explicit below-protocol flags, re-derivable byte-identically from the raw evidence bundles (verified on a live 3-repetition run as <strong>D-014 verification workload, idle-subtracted energy — M3 Max / powermetrics SoC rails:</strong> 99.19 ± 1.36 mJ/output-token); (2) <strong>contamination detection</strong> — an idle-window quality gate that mechanically flags runs taken on a non-quiet machine (it caught its first real contamination during verification); (3) <strong>deep telemetry</strong> — per-sample GPU/CPU-cluster frequency and residency forensics plus a machine-state snapshot in every bundle; (4) <strong>campaign automation</strong> — a deterministic config-matrix generator and a resumable sequential runner, so the planned two-model baseline matrix (4 workload shapes × 2 models × 5 repetitions) runs unattended. A review council also produced a hardware-tiered research agenda: 16 questions answerable on current hardware alone, 10 more behind planned gates (<code>docs/research_question_bank.md</code>). The P2-013 evidence-integrity and P2-014 provenance fixes are now complete; next Mac corpus step is the baseline matrix on a quiet machine.</p> <h2 id="previous-update-2026-07-07-fourth-update-30-second-read">Previous Update (2026-07-07, fourth update) — 30-second read</h2> <p><strong>A flagship-class model is now benchmarked.</strong> Qwen3.5-122B (Feb 2026 generation, 122B-parameter mixture-of-experts with 10B active, a reasoning model) ran through the identical harness and workload on the M3 Max. <strong>FLAGSHIP-001, gross energy — M3 Max / powermetrics SoC rails:</strong> ~304.0 J per 512-token request. <strong>FLAGSHIP-001, idle-subtracted energy — M3 Max / powermetrics SoC rails:</strong> ~298.7 J per request and ~583 mJ per generated output token. Throughput was 46 tokens/s, and the gross-energy sample CV was 0.3% across three sequential repetitions in one warm-cache session. The earlier model recorded <strong>P2-003, gross energy — M3 Max / powermetrics SoC rails:</strong> ~47.2 J per request and <strong>P2-003, idle-subtracted energy — M3 Max / powermetrics SoC rails:</strong> ~87 mJ per generated output token at 257 tok/s. <em>(Metric bases and CV wording corrected 2026-07-09, C-027.)</em> First cross-model finding: the two measured points differ in size, architecture, and quantization, so they are not a demonstrated scaling law. They are, however, consistent with the fixed-vs-marginal structure Q4 models: <strong>unsubtracted decode-window mean power — M3 Max / powermetrics SoC rails:</strong> ~23.5 W for P2-003 and ~27.5 W for FLAGSHIP-001, while the bigger model&#39;s cost showed up mostly as time. Also this update: the research agenda grew to six named questions (Q4-Q6) after a multi-model review council, with a curated question bank (<code>docs/research_question_bank.md</code>) and an instrument roadmap (richer telemetry parsing, a difficulty-graded scored workload suite, and implementing the statistical-uncertainty protocol) queued.</p> <h2 id="update-ledger">Update Ledger</h2> <div class="table-scroll"><table> <thead> <tr> <th>date</th> <th>label</th> <th>one-line outcome</th> <th>run-report link</th> </tr> </thead> <tbody><tr> <td>2026-07-19</td> <td>Measurement-soundness audit (Ed-directed)</td> <td>VERDICT: unsound for claim-bearing use as recorded — trace-time-anchor defect misattributes request/phase energies (all four P0s lead-verified); metric-level prechecks already failed 238/288 request metrics; four cooldown cap hits unjoined; analysis-engine wire incompat. Corpora demoted to instrument evidence; published 07-17 floor table caveated; instrument-repair path defined.</td> <td><code>docs/reviews/2026-07-19-measurement-soundness-audit.md</code></td> </tr> <tr> <td>2026-07-19</td> <td>Extended clean-provenance re-collection</td> <td>266/266 strict-valid bundles with clean SOURCE provenance from clean main (288 total with the completion window); all planned cells except DF-TELEM executed at planned n; one unlock abort quarantined (guard&#39;s 4th live catch); Sol recompute audit PASS on arithmetic. See the superseding soundness-audit row above for claim status.</td> <td><code>docs/run_reports/2026-07-19-recal456-extended-window.md</code></td> </tr> <tr> <td>2026-07-19</td> <td>Suite re-calibration under the guard (preliminary, review-corrected)</td> <td>94 strict-valid bundles; suite 147.96 ± 0.39 J clean; provisional comparative floor ≈ 1.13 J (~0.77%, 5/10 blocks); claim-ineligible on provenance pending clean re-run; three-lens review corrected two over-promoted claims.</td> <td><code>docs/run_reports/2026-07-19-d077-recal-window.md</code></td> </tr> <tr> <td>2026-07-18</td> <td>Contamination diagnosis + environment-guard hardening (D-077)</td> <td>Suite-cell inflation attributed to the macOS video screensaver on an awake idle display (43/50 bundles; power-source hypothesis refuted); suite comparative cells caveated pending re-run; the D-077 guard (preflight, idle admission, cooldown v2, claim barrier, anchor custody) was built and taken through an eight-round adversarial arc.</td> <td><code>docs/run_reports/2026-07-17-environment-guard.md</code>; <code>docs/run_reports/2026-07-18-d077-fix-rounds.md</code></td> </tr> <tr> <td>2026-07-17</td> <td>exploratory block + D-075 re-wrap</td> <td>Nine retained OLMoE/Qwen bundles re-validated and extracted as unmatched, claim-evidence-flagged exploratory observations; DSpark/DFlash smokes and D-075&#39;s ranked extension-axis intake folded in without promoting evidence; Ed&#39;s manual site deployment recorded as the new drift baseline.</td> <td><code>docs/run_reports/2026-07-17-window-a-floors.md</code> (final re-wrap addendum; lead gate pending)</td> </tr> <tr> <td>2026-07-17</td> <td>Window A floors + advisor brief</td> <td>PRs #72/#74 closed the bounded powermetrics drain defects and P2-038 passed on merged main; PR #73 filed the AXI-SC negative verdict; 222 strict-valid floor bundles extracted and independently verified, claim-readiness caveats retained; advisor brief shipped.</td> <td><code>docs/run_reports/2026-07-17-window-a-floors.md</code> (LEAD-ACCEPTED)</td> </tr> <tr> <td>2026-07-16</td> <td>audit close + no-hardware resumption batch</td> <td>PR #66 closed the comprehensive audit; PRs #67-#70 landed AXI-SA, SITE-02 D1/D2, the SPLIT-AP Part I freeze, and the AXI-SB <code>supported</code> verdict with its Mac C5-2.2 leg. Window A is software-unblocked but still needs Ed + quiet Mac; no new energy measurement is claimed.</td> <td><code>docs/run_reports/2026-07-16-resumption-nohw-batch.md</code></td> </tr> <tr> <td>2026-07-10/11</td> <td>C-028 hardening and integration arc</td> <td>PRs #41-#58 merged; analysis trio complete; reducer lattice through 0.4.2; P0-003 restore proof and every Window-A software gate satisfied; PR #59 open as a bounded follow-up; no new live evidence claimed.</td> <td><code>docs/run_reports/2026-07-11-c028-continuation.md</code></td> </tr> <tr> <td>2026-07-06</td> <td>third update / first real energy</td> <td>Mac slices 2G/2H/2I landed and produced strict-valid M3 Max measurements. <strong>P2-003, gross energy — M3 Max / powermetrics SoC rails:</strong> ~47.2 J per 512-token request. <strong>P2-003, idle-subtracted energy — M3 Max / powermetrics SoC rails:</strong> ~79-90 mJ per generated output token; the originally reported range used the prompt+output denominator and was corrected 2026-07-09 (C-027). TTFT ~94 ms, 257 tok/s, gross CV 1.4%, powermetrics observed at ~8.8-8.9 Hz; short prefill energy is below the current detection capability and is not a quantitative result (D-055).</td> <td><code>docs/run_reports/2026-07-06-slice-2i-first-real-energy.md</code></td> </tr> <tr> <td>2026-07-06</td> <td>third update / powermetrics telemetry</td> <td>The powermetrics telemetry adapter and privileged sampling path were brought up, preserving raw plists and exposing the real sampling-rate constraints.</td> <td><code>docs/run_reports/2026-07-06-slice-2h-powermetrics.md</code></td> </tr> <tr> <td>2026-07-06</td> <td>third update / pre-hardware hardening</td> <td>Slice 2N closed the evidence-path hardening before real hardware: raw evidence retention, measured-window markers, rail validation, shared bundle reading, and post-hoc reduction.</td> <td><code>docs/run_reports/2026-07-06-slice-2n-pre-hardware-hardening.md</code></td> </tr> <tr> <td>2026-06-12</td> <td>first/second updates / mock vertical slice</td> <td>The mock-first harness reached an end-to-end auditable run path before hardware time: typed config to complete bundle, validation, reduction, and report.</td> <td><code>docs/run_reports/2026-06-12-phase-2-mock-vertical-slice.md</code></td> </tr> </tbody></table></div> <p><strong><a href="project_status_full.html">Full project status →</a></strong></p> </div> </div> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>PROJECT_STATUS.md · commit 1af9f92 · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/run_reports/2026-07-09-p2034-broad-packs.md:12:validation cells, gated on AP-1/Q4); C5-3.1+3.5 replication runbook with
docs/stream_logs/2026-07-07-doc007-docs.md:72:## [orchestrator] Q4 softening applies to BOTH prose sites; the observation is "consistent with", not "models exactly"
docs/stream_logs/2026-07-07-doc007-docs.md:76:  structure Q4 models" is softened to: a two-point, confounded comparison
docs/stream_logs/2026-07-07-doc007-docs.md:84:- Why: C-007 res 14 pins Q4 as fixed-vs-marginal workload structure, NOT an
docs/stream_logs/2026-07-07-doc007-docs.md:197:### D-3 [codex] [type: framing] Q4 Observation Softened To Motivation, Not Scaling Law
docs/stream_logs/2026-07-07-doc007-docs.md:203:The comparison varies size, architecture, and quantization at once, so the old scaling phrasing overclaimed. Keeping the observation still helps explain why Q4 is interesting, while moving the caveat into the claim sentence prevents a reader from retaining the stronger version before seeing the limitation.
docs/stream_logs/2026-07-07-doc007-docs.md:208:Future references to the 122B flagship result and Q4 fixed-vs-marginal wording.
docs/stream_logs/2026-07-07-doc007-docs.md:263:Accepted: related-work map row "not started" → "drafted (11 verified sources)" (the doc contradicted itself); 2H ledger-row startup-latency misattribution removed (discovery lives in the 2I report); MVO "already a complete capstone" → "still a complete, defensible capstone if reached"; AGENT_PLAN 3.3 reworded "stretch beyond the required offline replay" so live-split's droppability cannot blur into split-study demotion (PROJECT_STATUS's ladder wording left alone — rung 2 "primary" already disambiguates). Rejected: tracer's Process-Note flags (token-volume estimate, "every hardware bug", external-skills claim — the C-007 directive was to keep the essay's prose intact except the Q4 softening; already hedged with "roughly"); tracer's architecture-table flag (the "Not yet started" section two paragraphs later already disambiguates design from implementation); tracer's artifact-map "complete and campaign-ready" flag (the row's missing-evidence column already carries the P2-013 qualifier).
docs/stream_logs/2026-07-07-doc007-docs.md:278:preserve historical records, keep the two-claim-track/Q4/detection-floor
docs/stream_logs/2026-07-17-rewrap.md:45:Decision: fold D-075 into the reader docs as one ranked extension of Q4's
docs/site/task_queue.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Task Queue - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html" class="active">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#intake-rule-for-new-tasks">Intake Rule For New Tasks</a> <a href="#priority-scale">Priority Scale</a> <a href="#ranking-factors">Ranking Factors</a> <a href="#ready-shelf-rule">Ready/Shelf Rule</a> <a href="#machine-state-lanes-adopted-c-007-2026-07-07">Machine-State Lanes (adopted C-007, 2026-07-07)</a> <a href="#historical-queue-snapshot-superseded-2026-07-15">Historical Queue Snapshot (superseded 2026-07-15)</a> <a href="#completed-queue-items">Completed Queue Items</a> <a href="#shelved-follow-ups-with-triggers-c-027-disposition-ledger-rev-10">Shelved Follow-Ups With Triggers (C-027 disposition ledger — REV-10)</a> <a href="#current-do-not-do-yet-list">Current Do-Not-Do-Yet List</a> <a href="#queue-maintenance">Queue Maintenance</a> <a href="#current-queue">Current Queue</a> <a href="#active-global-work-selection-gates">Active Global Work-Selection Gates</a></aside> <div class="doc-wrap doc-source-task-queue-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>TASK_QUEUE.md</code></p> <div class="provenance-plate"><span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>JouleWise Task Queue</h1> <p>This is the live queue for JouleWise work. When the user gives a new task, first triage it here instead of assuming it should happen immediately.</p> <h2 id="intake-rule-for-new-tasks">Intake Rule For New Tasks</h2> <p>For every new user task:</p> <ol> <li>Read <code>RUN_STATE.md</code>.</li> <li>Read this file.</li> <li>Check <code>git status --short --branch</code>.</li> <li>Review the last 2-3 commits with <code>git log --oneline --decorate -3</code>.</li> <li>Check relevant handoffs in <code>docs/run_reports/</code>.</li> <li>If <code>RUN_STATE.md</code> contains an ACTIVE <code>ACTIVE_STOP_CARD</code>, that card outranks this queue. Execute or preserve the card&#39;s resume/cleanup instructions before considering any lower-ranked work.</li> <li>Decide whether the task is:<ul> <li>urgent workspace hygiene,</li> <li>Phase 1 evidence work,</li> <li>Phase 2 implementation prep,</li> <li>later-phase research work,</li> <li>documentation/reporting,</li> <li>or unrelated/new scope.</li> </ul> </li> <li>Place or update the task in the queue with priority, rationale, evidence, and blockers.</li> <li>If executing it now, say why it outranks the current top task.</li> <li>Closure rule (D-023): a row may move to Completed only after the corresponding phase exit-checklist matrix row already shows the same status with dated evidence, and the Completed row&#39;s evidence cell must cite that matrix row (file + item id). If no matrix row exists for the work, say so explicitly in the evidence cell.</li> </ol> <h2 id="priority-scale">Priority Scale</h2> <ul> <li><strong>P0 Safety</strong>: prevents accidental data loss, bad commits, broken handoffs, or corrupted repo state.</li> <li><strong>P1 Phase Gate</strong>: required to close the current phase or unblock the next phase responsibly.</li> <li><strong>P2 Next Slice</strong>: next implementation slice after current phase gates are adequately planned or closed.</li> <li><strong>P3 Research Expansion</strong>: useful experiment or feature, but not needed for current gate.</li> <li><strong>P4 Polish</strong>: quality-of-life, dashboard polish, formatting, cleanup, or presentation work.</li> </ul> <h2 id="ranking-factors">Ranking Factors</h2> <p>Rank higher when a task:</p> <ul> <li>Prevents accidental loss or bad Git history.</li> <li>Produces evidence for the current phase exit checklist.</li> <li>Removes ambiguity for multiple later steps.</li> <li>Is required before physical hardware time is spent.</li> <li>Is cheap to verify and reduces future confusion.</li> <li>Matches the current phase better than jumping ahead.</li> </ul> <p>Rank lower when a task:</p> <ul> <li>Depends on unavailable hardware or supervisor input.</li> <li>Is a later-phase feature.</li> <li>Adds polish before a runnable vertical slice exists.</li> <li>Produces code without a clear run-bundle or test artifact.</li> </ul> <h2 id="ready-shelf-rule">Ready/Shelf Rule</h2> <p>A partially built or proposed task is <strong>READY</strong> only when it has:</p> <ul> <li>one authority document or stream-log pointer,</li> <li>bounded files/modules or a bounded artifact target,</li> <li>explicit acceptance evidence or a verification command,</li> <li>no hidden hardware/user/token-budget dependency, and</li> <li>a named lane (<code>[AGENT]</code>, <code>[QUIET-MAC]</code>, or <code>[ED-EXTERNAL]</code>).</li> </ul> <p>If any of those are missing, keep the item as a shelved concept or planning note instead of letting it compete with executable queue work. Half-finished work should be resumed only through its authority pointer and stop-card/checkpoint state, not by inference from prose summaries.</p> <h2 id="machine-state-lanes-adopted-c-007-2026-07-07">Machine-State Lanes (adopted C-007, 2026-07-07)</h2> <p>Every task carries a lane; a session picks the top task COMPATIBLE with its machine state, not the top task absolutely:</p> <ul> <li><strong>[QUIET-MAC]</strong> — measurement campaigns only: no agent fleet, no Codex load, idle gate will flag contamination.</li> <li><strong>[AGENT]</strong> — code, docs, feasibility spikes; safe during agent-heavy sessions.</li> <li><strong>[ED-EXTERNAL]</strong> — needs the user: advisor, calendar, device access, purchases, destinations.</li> </ul> <h2 id="historical-queue-snapshot-superseded-2026-07-15">Historical Queue Snapshot (superseded 2026-07-15)</h2> <p>The former hand-authored live table was removed because it duplicated kernel tasks. Dated completion and disposition history remains below; the generated Current Queue region is the sole live work-selection view.</p> <h2 id="completed-queue-items">Completed Queue Items</h2> <div class="table-scroll"><table> <thead> <tr> <th>ID</th> <th>Priority</th> <th>Completed</th> <th>Task</th> <th>Evidence</th> </tr> </thead> <tbody><tr> <td>CODEX-BRIDGE-PET</td> <td>P4 Polish</td> <td>2026-07-18</td> <td>Make the native Codex pet reflect Claude Code background Sol work without changing adaptive effort routing</td> <td>No phase exit-checklist row exists for this personal bridge UI integration; actual <code>scripts/codex-bridge</code> route traced, app-owned thread follower implemented, live Sol/high app-thread smoke <code>019f77a9-2827-7de1-accf-ac2eda21927e</code>, focused IPC/termination tests, and report <code>docs/run_reports/2026-07-18-claude-codex-pet-observer.md</code></td> </tr> <tr> <td>P2-015-SMOKE</td> <td>P2 Next Slice</td> <td>2026-07-17</td> <td>Complete the pre-Window-A production-shaped campaign shakedown through doctor, strict validation, reducer 0.4.2, strict revalidation, campaign verdict split, and approved backup; keep extra samplers disabled pending DF-TELEM</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this precondition; <code>production_uncertainty_v1</code> PASSED on merged main at <code>runs/window_a_shakedown_final</code> (<code>request_eligible: true</code>, reasons <code>[]</code>, strict pre+post reduce passed, backup exit 0), pinned in <code>docs/phase_2/detection_floor.md</code>; the extra-sampler overhead layer is deferred with DF-TELEM and remains required before enabling extra samplers</td> </tr> <tr> <td>P2-038</td> <td>P2 Next Slice</td> <td>2026-07-17</td> <td>Close the production-uncertainty live tail with a true MLX + <code>/usr/bin/powermetrics</code> production-shaped shakedown through strict validation, reducer 0.4.2, strict revalidation, request-eligibility gating, and approved backup</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this hardening gate; <code>production_uncertainty_v1</code> PASSED on merged main at <code>runs/window_a_shakedown_final</code> (<code>request_eligible: true</code>, reasons <code>[]</code>, strict pre+post reduce passed, backup exit 0); drain fixes PR #72 + PR #74; exact <code>caffeinate -is</code> command and display-sleep environment pin recorded in <code>docs/phase_2/detection_floor.md</code></td> </tr> <tr> <td>AXI-SC</td> <td>P2 Next Slice</td> <td>2026-07-17</td> <td>AXI stream S-C leg 1: pinned mlx-lm speculative-decode/MTP feasibility spike — verdict <code>unsupported_for_joulewise</code> (external draft: <code>event_observability</code>; native MTP: <code>native_mtp_generation</code>); Mac energy leg not minted, with explicit runtime-upgrade revisit triggers</td> <td>No matrix row exists in a phase exit checklist for this spike; PR #73 merged; lead-run live probes with evidence + SHA-256 (<code>docs/process_traces/2026-07-17-axi-sc-live-probes/</code>); negative applicability verdict filed in <code>docs/specs/axi/sc_spec_decode_verdict.md</code>; vLLM leg remains fixture-first PROVISIONAL and outside this filing</td> </tr> <tr> <td>AXI-SB</td> <td>P2 Next Slice</td> <td>2026-07-16</td> <td>AXI stream S-B: pinned mlx-lm static-batch feasibility spike — verdict <code>supported</code> (mlx-lm 0.31.3 BatchGenerator path; true B&gt;1 execution with full per-request observability); Mac C5-2.2 leg minted per D-070; follow-on adapter row AXI-SB-ADAPTER minted at rank 4</td> <td>No matrix row exists in a phase exit checklist for this spike; PR #70 merged (self-merge under Ed&#39;s 2026-07-16 delegation; CI green); lead-run live probes B∈{2,4} with evidence + SHA-256 (<code>docs/process_traces/2026-07-16-axi-sb-live-probes/</code>); anti-gaming lens -&gt; fix -&gt; delta 2 blockers (9th fix-rounds-inject-defects datum) -&gt; micro-round -&gt; lead termination (post-hardening live re-probe <code>supported</code> at controller_evidence_validation); verdict doc <code>docs/specs/axi/sb_static_batch_verdict.md</code>; ledger <code>docs/stream_logs/2026-07-16-axi-sb.md</code></td> </tr> <tr> <td>SPLIT-AP</td> <td>P2 Next Slice</td> <td>2026-07-16</td> <td>Split pre-registration freeze (adjudicated Part I, D-067-reconciled): gross-only primary estimand and headline; both monolithic references mandatory (Holm, intersection-union); pinned idle-sub calculation with D-067 reporting restriction; D-048 predictor over all five gross components; named open gates OPEN-GATE-SPLITAP-PACK-LINT + OPEN-SPLIT-PRED-FIXED-COMPOSITION</td> <td>No matrix row exists in a phase exit checklist for this pre-registration stream; PR #69 merged <code>9db4546</code> (self-merge under Ed&#39;s 2026-07-16 delegation; CI green); Sol xhigh impl -&gt; xhigh counterreview -&gt; fix -&gt; delta (caught lead-pinned predictor blocker) -&gt; micro-round -&gt; focused delta -&gt; bench fix -&gt; MR1 -&gt; lead termination; ledger <code>docs/stream_logs/2026-07-16-split-ap.md</code> (SPLITAP-1..10)</td> </tr> <tr> <td>SITE-02</td> <td>P4 Polish</td> <td>2026-07-16</td> <td>Close SITE-01 D1/D2 deferrals: loud structured Lakebed discovery (env + OS-path, exact-version refusal incl. wrong-before-correct PATH ordering, never silent estimator fallback) + node decode regression executing the EMITTED TypeScript via pinned esbuild; D2 guaranteed in CI (release-chain focused step)</td> <td>No matrix row exists in a phase exit checklist for this site-tooling task; PR #68 merged <code>2778ed2</code> (self-merge under Ed&#39;s 2026-07-16 delegation; D2 step verified executed in the release-chain CI log, <code>Ran 1 test ... OK</code>); Sol high impl -&gt; bug+test lenses -&gt; fix -&gt; delta -&gt; micro-round -&gt; lead termination; ledger <code>docs/stream_logs/2026-07-16-site-02.md</code> (SITE02-1..5)</td> </tr> <tr> <td>AXI-SA</td> <td>P2 Next Slice</td> <td>2026-07-16</td> <td>AXI stream S-A: burst-decode metric-semantics contract implementation, stages 0-7 (versioned request-scoped emission events, proposal/acceptance counters, speculation identity, sibling analysis manifest with frozen AP-SPEC denominators, output-identity gate, mock spec adapter last)</td> <td>No matrix row exists in a phase exit checklist for this contract stream; spec <code>docs/specs/axi/sa_burst_decode_contract.md</code> is the authority; Sol xhigh impl, xhigh checker FAIL 5 blockers -&gt; fix -&gt; xhigh delta FAIL 2 -&gt; micro-round -&gt; lead termination (canonical 1626 OK, mock spec-decode e2e replayed at the lead bench); PR #67 merged <code>7593259</code> (self-merge under Ed&#39;s 2026-07-16 in-session delegation; CI-only portability fix <code>0914374</code> reviewed fresh, CI green 5/5); run report <code>docs/run_reports/2026-07-14-audit-resume-axi.md</code></td> </tr> <tr> <td>AXI-S0</td> <td>P2 Next Slice</td> <td>2026-07-15</td> <td>AXI stream S-0: advisor-facing doc alignment (gross basis+boundary on every number, D-067 attributed rationale, harness/benchmark split, five-axis Q4 agenda, C-023-IDLE-STATIONARITY note, DRIFT.md refresh)</td> <td>No matrix row exists in a phase exit checklist for this docs stream; kernel row completed (AXI-SA dep satisfied); Sol high impl, fresh checker FAIL 4 majors -&gt; fix round -&gt; delta PASS; freshness+suite green; run report <code>docs/run_reports/2026-07-14-audit-resume-axi.md</code></td> </tr> <tr> <td>SITE-01</td> <td>P2 Next Slice</td> <td>2026-07-13</td> <td>Site capsule under the 1 MiB Lakebed cap + live redeploy</td> <td>No matrix row exists in a phase exit checklist for this site-tooling task; PR #63 (gzip shards, measured-artifact postcondition); delta re-audit no-blockers (D3 fixed, D1/D2 → SITE-02); live deploy ACCEPTED at 854,349 B, routes 5/5 200, freshness 14/14 current; reports <code>2026-07-12-agent-lane-triple.md</code> + <code>2026-07-13-restart-merge-deploy.md</code></td> </tr> <tr> <td>P2-028</td> <td>P2 Next Slice</td> <td>2026-07-13</td> <td>Response-hash determinism gate (<code>joulewise determinism-gate</code>)</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this post-checklist gate task; PR #62 + DRA-001 malformed-identity fix; both retained corpus groups formally <code>determinism_supported</code>; ledger P2028-1..5; same two reports</td> </tr> <tr> <td>P2-049</td> <td>P3 Hardening Candidates</td> <td>2026-07-13</td> <td>analysis_manifest.py explicit-root-or-fail-closed resolution (C-028 SF3)</td> <td>No matrix row exists in a phase exit checklist for this hardening task; PR #61 (lens CLEAN, replay 1261 OK); installed-wheel CI now smokes the refusal (XSI-1 fix on main); same two reports</td> </tr> <tr> <td>CODEX-BRIDGE-3</td> <td>P0 Safety</td> <td>2026-07-13</td> <td>bridge-protocol/v1.1 for maximum co-work (Ed-directed): discussion lane, session-open/close wrappers, tolerant envelope, per-call reverse effort, peer channels + proposal diffs</td> <td>PR #65 MERGED <code>d285989</code> (Ed-named merge); merged-main suite 1387 OK lead-run; 3 lenses + 3 delta re-audits, findings 13→6→2→1; suite 1387 OK; CI green at <code>8b96bd4</code>; D-065; report <code>2026-07-13-bridge-v11.md</code></td> </tr> <tr> <td>CODEX-BRIDGE-2</td> <td>P0 Safety</td> <td>2026-07-12</td> <td>Make the Claude Code ↔ Sol/Fable bridge bidirectional with adaptive Sol effort (<code>high</code> default; xhigh/ultra only by trigger) and a hard one-hop guard</td> <td>Claude → Sol live <code>/codex</code> token <code>JOULEWISE_SOL_HIGH_GUARDED_OK</code>, thread <code>019f5a2a-2f4a-7b33-8a6d-b44dcc5a7a26</code>; Sol → Fable live <code>consult_fable</code> token <code>JOULEWISE_FABLE_MCP_OK</code>, thread <code>019f5a26-d8a6-7993-b48d-8131d88748b9</code>; protocol checker + 4 focused tests; report <code>2026-07-12-claude-sol-bridge.md</code></td> </tr> <tr> <td>INT-59</td> <td>P2 Next Slice</td> <td>2026-07-11</td> <td>Bounded integration-review cleanup/ratio-readiness follow-up</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this integration-review follow-up; PR #59 MERGED 2026-07-11; post-merge main canonical 1,258 OK/10 skipped at <code>194ea39</code> (lead-run)</td> </tr> <tr> <td>DOC-008</td> <td>P2 Next Slice</td> <td>PARTIAL — REOPENED 2026-07-15</td> <td>Machine-readable state kernel (schema v3, <code>AUTHORITATIVE_WORK_SELECTION_STATE</code> for work selection only) generating the RUN_STATE restart block + live queue view</td> <td>PR #60&#39;s 2026-07-11 completion record is reopened by WO-021 because the original spec conditions were only partially satisfied; phase A adds global gates, independent-oracle fidelity checks, CI drift enforcement, and DOC-010&#39;s two-part fence. DOC-008 may not return to complete until every condition in <code>docs/specs/c027/doc-008_state_kernel.md</code> §1.1 lands.</td> </tr> <tr> <td>C-028</td> <td>P0/P1 integration arc</td> <td>2026-07-11</td> <td>Close the #41-#58 hardening + analysis-engine arc; clear the stop card while tracking #59 separately</td> <td><code>docs/run_reports/2026-07-11-c028-continuation.md</code>; council C-028; D-064; main canonical 1,220 OK/10 skipped; corpus 6/6</td> </tr> <tr> <td>C028-SWEEP</td> <td>P4 consistency</td> <td>2026-07-11</td> <td>C-002/D-023 end-of-arc consistency sweep and advisor-doc refresh</td> <td>Same dated C-028 report closeout addendum; <code>claims_lint --mode all</code>; diff/scope checks</td> </tr> <tr> <td>P2-015-PREP</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>P2-015 detection-floor design doc — combined floors, error budget, telemetry trust, and calibration runbooks</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this design-doc task; <code>docs/phase_2/detection_floor.md</code>; D-054; PR #31; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave1.md</code></td> </tr> <tr> <td>P2-029</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Reducer/aggregator uncertainty propagation and claim gates</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this post-checklist implementation task; D-057; PR #33; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></td> </tr> <tr> <td>P2-030</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Ordering executability: rotation policies and order provenance</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this post-checklist implementation task; D-056; PR #34; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></td> </tr> <tr> <td>P2-031</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Token-normalization contract and stack-identity table</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this post-checklist contract task; D-058; PR #35; <code>docs/contracts/token_normalization.md</code>; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></td> </tr> <tr> <td>P2-032</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Campaign packs: Q1-Q3 split suite, Q6 rail-vs-wall, and C5-2.3 KV economics</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this campaign-pack task; PR #36; <code>docs/campaign_packs/</code>; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></td> </tr> <tr> <td>P2-034</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Broad campaign packs: C5-2.7/2.8, replication runbook, and C5-I.1..I.5</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this campaign-pack task; PR #39; six packs in <code>docs/campaign_packs/</code>; pack lint errors=0; run report <code>docs/run_reports/2026-07-09-p2034-broad-packs.md</code></td> </tr> <tr> <td>CODEX-BRIDGE</td> <td>P0 Safety</td> <td>2026-07-09</td> <td>Make the Claude Code → Codex bridge durable, full-session capable, and process-safe</td> <td>Root <code>AGENTS.md</code>; tracked Claude subagent + <code>/codex</code> command; protocol checker; Claude-approved live <code>codex</code> + same-thread <code>codex-reply</code> smoke; report <code>2026-07-09-claude-codex-mcp-bridge.md</code></td> </tr> <tr> <td>RESUME-CP5</td> <td>P0 Safety</td> <td>2026-07-09</td> <td>Resume and complete the CP-5 pre-campaign review session</td> <td>7 PRs merged (#22..#28); stop card CLEARED; CP-6 dispositions in the stream log; run report <code>2026-07-09-cp5-resume.md</code>; suite 822 OK</td> </tr> <tr> <td>P2-026</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>D-033 strict legacy-bypass close (frozen six-identity allowlist)</td> <td>PR #22; live-gated 6/6 corpus + tamper-fails + spoof probe fails closed</td> </tr> <tr> <td>P2-025</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Campaign-runner expected-vs-realized prompt-hash check (+ runtime/validator closure)</td> <td>PRs #24 + #27; fail-closed with type-discriminated sidecar inference; live-gated classifier truth table; 48/48 real-tokenizer closures</td> </tr> <tr> <td>P2-010b-GATE</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Envelope-gate analysis script (E1-E4 + E5 advisory, D-036 verdicts, CLI)</td> <td>PR #23; live-gated on the real mock affine bundle incl. refusal cases</td> </tr> <tr> <td>P2-027-TOOLING</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Bundle-pack publication tooling (pack + one-command verify)</td> <td>PR #25; live pack→verify→tamper→verify(2)</td> </tr> <tr> <td>CAPTURE-HARDENING</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Pre-campaign capture: output token IDs, fail-closed sampler pin (D-047 amendment), model weight hashing, env versions, hash-domain closure</td> <td>PR #27; live MLX gate incl. two full jw_mixed suite runs</td> </tr> <tr> <td>P2-012-MANIFESTS</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Tokenizer identity widening + real-tokenizer manifest regeneration</td> <td>PR #26; byte-identical double-regen; counts 512/512</td> </tr> <tr> <td>ADVISOR-SITE</td> <td>P4 Polish</td> <td>2026-07-09</td> <td>Advisor status site + suite_next draft-spec packet landing (D-051)</td> <td>PR #28; stop-card sha-verified intact; site regenerated with real renderer</td> </tr> <tr> <td>P2-018</td> <td>P4 Polish</td> <td>2026-07-08</td> <td>Deploy the site as a shareable Lakebed capsule with live GitHub freshness</td> <td>Live at <a href="https://quiet-signal-6af8833395.lakebed.app">https://quiet-signal-6af8833395.lakebed.app</a>; <code>scripts/pack_capsule.py</code> + <code>site_capsule/</code>; per-source drift vs <code>main</code>, fails soft; run report <code>2026-07-08-lakebed-deploy.md</code></td> </tr> <tr> <td>P2-021</td> <td>P2 Next Slice</td> <td>2026-07-08</td> <td>Drift sentinels + block-position covariates in the 2M generator</td> <td>PR #15 (merged 8765ee1); fail-loud sentinel manifest; campaign-log covariate echo; run report <code>2026-07-08-suite-science-expansion.md</code></td> </tr> <tr> <td>P2-017</td> <td>P2 Next Slice</td> <td>2026-07-08</td> <td>Honest per-source site provenance stamps</td> <td>PR #13 site-observatory rewrite: <code>git log -1 -- &lt;source&gt;</code> per page + <code>+ uncommitted</code> dirty marker; parser-tested; run report <code>2026-07-08-site-observatory.md</code></td> </tr> <tr> <td>P2-011</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>D-014 cross-repetition uncertainty (aggregate engine + manifest enrichment)</td> <td>PR #6; lead-verified real n=3 experiment, byte-identical re-derivation; run report 2026-07-07-parallel-streams-session.md; C-006 trace</td> </tr> <tr> <td>P2-008</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>Mock telemetry × SystemClock strictly-interior stamping</td> <td>PR #5; live-verified at 1 Hz real-MLX; 20 Hz workaround retired</td> </tr> <tr> <td>P2-009</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>Rich telemetry + idle-quality gate + environment capture</td> <td>PR #4 + INT-002 (8856c04); idle gate first live true positive</td> </tr> <tr> <td>2M-TOOLING</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>Campaign matrix generator + resumable sequential runner</td> <td>PR #3 + INT-001 (a05e54d); dry-run/resume/crash flows lead-verified</td> </tr> <tr> <td>KV-SIZE</td> <td>P3 Research Expansion</td> <td>2026-07-07</td> <td>Stage 3.0.0 kv-size helper (module + CLI verb)</td> <td>PR #2; anchors verified against both mirrored models</td> </tr> <tr> <td>FLAGSHIP-001</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>User-directed flagship benchmark: Qwen3.5-122B-A10B-4bit on the M3 Max</td> <td>3/3 strict-valid bundles: ~304.0 J gross / ~298.7 J idle-sub per 512-tok request, 582-585 mJ/generated-output-token idle-sub (mean 583.4), 46 tok/s, gross CV 0.3% within one warm-cache session; legacy L1 (bases corrected 2026-07-09, C-027); run report <code>2026-07-07-flagship-qwen35-122b.md</code>; first Q4 data point</td> </tr> <tr> <td>P1-002</td> <td>P1 Phase Gate</td> <td>2026-07-06</td> <td>Mac-local Phase 1 telemetry/runtime evidence — sample captured, fields pinned, D-004 sudoers installed + <code>sudo -n</code> verified, MLX installed</td> <td>Phase 1 exit checklist instrumentation section; fixture committed; live 2I run</td> </tr> <tr> <td>P2-003</td> <td>P2 Next Slice</td> <td>2026-07-06</td> <td>Mac MLX + powermetrics vertical slice (2G, 2H, 2I) — <strong>first real energy numbers</strong></td> <td>Commits <code>3eb0acd</code>/<code>26dca41</code>/<code>b4d4173</code>; 3/3 strict-valid bundles: ~47.2 J gross / ~44.4 J idle-sub per 512-token request, 79.4-90.5 mJ/generated-output-token idle-sub (mean 86.8), 257 tok/s, TTFT ~94 ms; legacy L1 (bases corrected 2026-07-09, C-027; the old 77-88 figure used the prompt+output denominator); run reports 2026-07-06 (buildout, 2H, 2I)</td> </tr> <tr> <td>P0-002</td> <td>P0 Safety</td> <td>2026-07-06</td> <td>Measurement-corpus backup protocol (R-016) — interim destination per user direction</td> <td><code>scripts/backup_runs.sh</code>; restore test green (<code>validate-bundle</code> on restored copy); protocol in R-016; follow-up P0-003 tracks the real destination</td> </tr> <tr> <td>P3-001</td> <td>P3 Research Expansion</td> <td>2026-07-06</td> <td>Background/related-work draft (Phase 4 Stage 4.6)</td> <td><code>docs/phase_4/related_work_draft.md</code>: 11 sources, independently verified citations, positioning claims honestly adjusted (claims 1-2 narrowed, claim 3 stands)</td> </tr> <tr> <td>2G (P2-003 part)</td> <td>P2 Next Slice</td> <td>2026-07-06</td> <td>MLX runtime adapter — first real generation traces on the M3 Max</td> <td>Commit <code>3eb0acd</code>; succeeded bundle <code>example-mac-mlx-mock-telemetry</code> (TTFT 81.5 ms, 265.8 tok/s, <code>--strict</code> valid); suite 230 OK both interpreters; implemented by Codex via <code>scripts/codex-bridge</code>, reviewed + live-verified by Claude</td> </tr> <tr> <td>DOC-006</td> <td>P2 Next Slice</td> <td>2026-07-06</td> <td>Independent status-review intake (user-directed): all three findings verified and fixed — P1 event-timestamp hardening, P2 <code>validate-bundle --strict</code> (D-030), P3 adapter raw-write helper</td> <td>Review <code>2026-07-06-project-status-review.md</code>; fixes run report <code>2026-07-06-status-review-fixes.md</code>; 226 tests OK</td> </tr> <tr> <td>P2-007</td> <td>P2 Next Slice</td> <td>2026-07-06</td> <td>Slice 2N pre-hardware hardening (all nine items, three commits)</td> <td>Run report <code>2026-07-06-slice-2n-pre-hardware-hardening.md</code>; D-024..D-029; 216 tests OK; exit-checklist 2N row closed</td> </tr> <tr> <td>DOC-005</td> <td>P4 Polish</td> <td>2026-07-06</td> <td>External architecture review intake (user-directed): D-024 RunContext, D-025 shared bundle reader, node-worker protocol contract, 2N items 8-9</td> <td>Run report <code>2026-07-06-architecture-review-intake.md</code>; <code>docs/contracts/node_worker_protocol.md</code></td> </tr> <tr> <td>DOC-004</td> <td>P4 Polish</td> <td>2026-07-05</td> <td>Agent playbook (user-directed): per-mission execution guides for all remaining steps</td> <td><code>docs/agent_playbook.md</code>; pointers in <code>README.md</code>/<code>AGENT_PLAN.md</code>; Stage 4.6 seeded with named competitor set</td> </tr> <tr> <td>P0-001</td> <td>P0 Safety</td> <td>2026-07-05</td> <td>Move repo off iCloud-synced Desktop (R-017)</td> <td>New path <code>~/code/CapstoneRivoire/Capstone</code>; git + suite verified green at the new location; recorded in <code>RUN_STATE.md</code></td> </tr> <tr> <td>DOC-003</td> <td>P4 Polish</td> <td>2026-07-05</td> <td>Docs/meta-layer cleanup (user-directed): drift fixes, D-023 status consolidation, plan/guide dedup, R-016/R-017, Slice 2N + Stage 4.6 planned</td> <td>Run report <code>2026-07-05-docs-meta-cleanup.md</code>; D-023; risk register updated</td> </tr> <tr> <td>P2-001</td> <td>P2 Next Slice</td> <td>2026-06-12</td> <td>Mock vertical slice: slices 2A-2E</td> <td>Harness runs end-to-end; <code>validate-bundle</code> green; CI mock e2e step added; 169 tests. <code>joulewise/{bundle,clock,controller,reduce,cli}.py</code> + <code>adapters/</code>; run report <code>2026-06-12-phase-2-mock-vertical-slice.md</code></td> </tr> <tr> <td>P2-002</td> <td>P2 Next Slice</td> <td>2026-06-12</td> <td>Repetitions + experiment manifests (slice 2F)</td> <td><code>run_experiment</code> + cooldown gate; 3-rep + kill-after-rep-2 + cooldown tests; manifest per D-005. Same run report</td> </tr> <tr> <td>P2-J</td> <td>P2 Next Slice</td> <td>2026-06-12</td> <td>Static report generator (slice 2J)</td> <td><code>joulewise/report.py</code>; matplotlib behind <code>[analysis]</code>; graceful structured failure when absent; tests skip cleanly without the extra</td> </tr> <tr> <td>P1-005</td> <td>P1 Phase Gate</td> <td>2026-06-12</td> <td>Hailo feasibility verdict</td> <td><code>unsupported_workload</code> from official-source desk research; recorded in the Phase 1 exit checklist Hailo section</td> </tr> <tr> <td>P1-007</td> <td>P1 Phase Gate</td> <td>2026-06-12</td> <td>Phase 2 readiness review</td> <td>Recorded in the Phase 1 exit checklist; verdict &quot;mock-first Phase 2 may begin&quot;</td> </tr> <tr> <td>Q-000</td> <td>P0 Safety</td> <td>2026-06-09</td> <td>Resolve the local <code>Energy_Benchmark_Architecture.docx</code> deletion decision</td> <td>User confirmed the Word doc was unrelated; deletion committed in <code>a5d7404</code></td> </tr> <tr> <td>PLAN-001</td> <td>P1 Phase Gate</td> <td>2026-06-09</td> <td>Build evidence-shaped plans for Phases 2-5 (user-directed)</td> <td>Per-phase plan + exit-checklist docs; <code>docs/decision_log.md</code> (D-001..D-019); <code>docs/risk_register.md</code>; <code>docs/milestones.md</code>; methodology/bundle-layout amendments; <code>AGENT_PLAN.md</code> restructured as index; run report <code>docs/run_reports/2026-06-09-phase-2-5-planning-buildout.md</code></td> </tr> <tr> <td>CI-001</td> <td>P2 Next Slice</td> <td>2026-06-09</td> <td>Add core-tests CI workflow (D-017)</td> <td><code>.github/workflows/ci.yml</code>; extended 2026-06-12 with the mock end-to-end run</td> </tr> <tr> <td>DOC-001</td> <td>P4 Polish</td> <td>2026-06-09</td> <td>Unify Phase 1 doc scheme with Phases 2-5 (user-directed)</td> <td><code>docs/phase_1/</code> reduced to <code>phase_1_plan.md</code> + <code>phase_1_exit_checklist.md</code>; contracts moved to <code>docs/contracts/</code>; run report <code>docs/run_reports/2026-06-09-phase-1-doc-unification.md</code></td> </tr> <tr> <td>DOC-002</td> <td>P4 Polish</td> <td>2026-06-09</td> <td>Add advisor-facing status/plan/architecture doc + audit original sketch (user-directed)</td> <td>Root <code>PROJECT_STATUS.md</code>; run report <code>docs/run_reports/2026-06-09-advisor-status-doc.md</code></td> </tr> </tbody></table></div> <h2 id="shelved-follow-ups-with-triggers-c-027-disposition-ledger-rev-10">Shelved Follow-Ups With Triggers (C-027 disposition ledger — REV-10)</h2> <p>Previously promised follow-ups whose queue rows had silently died; each now has an explicit disposition:</p> <ul> <li><p>D-013 SSH-controlled vs co-resident controller comparison — SHELF, trigger: first 2K live session (validation cell rides that session).</p> </li> <li><p>Empirical corpus for the 0.40 GPU-idle contamination threshold — SHELF, trigger: Window-A calibration data exists (P2-015 output feeds it).</p> </li> <li><p><code>dvfm_states</code> slimming option — SHELF, trigger: bundle-size pain during the 2M campaign; otherwise declined as premature.</p> </li> <li><p>Cold-load / model-load-energy capture — DECLINED for the capstone scope (CP-5 deferral made permanent unless an AP row claims it; warm-cache protocol is the declared scope).</p> </li> <li><p>CI-003 developer polish (console script, macOS CI job, Ruff, coverage thresholds) — SHELF, trigger: G6-equivalent reference release (hardening adjudication C10).</p> </li> <li><p>DOC-010 historical-archive audit — SHELF, trigger: DOC-008 state kernel proven in use (hardening adjudication C11).</p> </li> </ul> <h2 id="current-do-not-do-yet-list">Current Do-Not-Do-Yet List</h2> <ul> <li>(satisfied 2026-06-12) The mock bundle/reducer path and report generator now exist; dashboard/report work is no longer blocked.</li> <li>(satisfied 2026-06-12) The mock lifecycle is runnable, so live MLX/powermetrics implementation may proceed once its hardware gates open (P1-002 + D-016); follow <code>docs/phase_2/hardware_slice_implementation_guide.md</code>.</li> <li>(resolved 2026-06-12) Hailo feasibility has a verdict (<code>unsupported_workload</code>); do not implement a Hailo backend — report it as an applicability finding.</li> <li>Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in D-008; implementation waits).</li> <li>Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware pairings, or borrow-window scheduling before 2M baselines and the Stage 3.0 verdicts exist (C-007 wording fix; was previously stated as a blanket Phase 3 hold that contradicted the queue).</li> <li>Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the rehearsed runbook exist (R-006).</li> <li>Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has produced data.</li> <li>Do not close D-016 (model selection) without P1-001 supervisor scope or an explicit user go-ahead.</li> <li>(satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own gates (D-016 + <code>[mac]</code> install; privileged sample + D-004 sudoers) open — build on the post-2N seams (RunContext raw evidence, D-026 markers, D-027 rail rows, 2N.3 observed-token fallback).</li> </ul> <h2 id="queue-maintenance">Queue Maintenance</h2> <p>At the end of substantial work:</p> <ul> <li>Update live status, rank, dependencies, and new tasks in <code>docs/process/state_kernel.json</code>.</li> <li>Remove terminal tasks from the kernel only after their owning completion evidence supports closure; preserve the dated Completed row here.</li> <li>Run <code>python3 scripts/gen_state.py</code>; never hand-edit generated queue or restart rows.</li> <li>Keep hand-authored edits here to policy, completed/history records, and non-selection context.</li> </ul> <h2 id="current-queue">Current Queue</h2> <p>The generated region below is the sole live queue and source of truth for work selection. Edit the kernel and regenerate; do not hand-edit its rows.</p> <p>Superseded (2026-07-15, WO-012; D-043): Q4/P2-019 sample size is frozen in the hash-bound analysis registry before outcomes, and outcome-dependent growth permanently demotes the contrast to exploratory; see <code>docs/contracts/analysis_plans.md</code> §Required fields.</p> <p>Superseded (2026-07-15, WO-017; D-043): P2-027 publication and uninvolved-party re-reduction are optional owner-directed evidence-handoff work, not the default reproducibility or project-completion gate; see <code>docs/specs/c027/rpt-001_report_vertical_slice.md</code> §0.4 and <code>docs/contracts/publication_privacy.md</code> §Publication boundary.</p> <!-- BEGIN GENERATED: state-kernel current-queue --> <!-- GENERATED from docs/process/state_kernel.json by scripts/gen_state.py. Do NOT hand-edit between the markers; edit the kernel and regenerate. --><p>Source of truth for work selection: <a href="docs/process/state_kernel.json">state kernel</a> (updated 2026-07-25).</p> <p>Generated compatibility table for repository consumers; the lane tables below are the detailed view of the same kernel state.</p> <div class="table-scroll"><table> <thead> <tr> <th>Rank</th> <th>ID</th> <th>Priority</th> <th>Status</th> <th>Task</th> <th>Evidence / Acceptance</th> </tr> </thead> <tbody><tr> <td>E1</td> <td>P1-008</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).</td> <td>Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: <a href="docs/milestones.md">Milestones + R-012</a>. Acceptance: <a href="docs/process/state_kernel.json">P1-008 acceptance</a>. Note: R-012 is the biggest active management risk for an undergrad timeline.</td> </tr> <tr> <td>E2</td> <td>P2-027</td> <td>P2 Next Slice</td> <td>READY [ED-EXTERNAL]</td> <td>Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party.</td> <td>Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: <a href="docs/reviews/2026-07-09-c027-whole-project-review.md">C-020 + C-027 NEG-9</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-027 acceptance</a>. Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL.</td> </tr> <tr> <td>E3</td> <td>P1-001</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Capture supervisor approval and scope notes.</td> <td>Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: <a href="docs/risk_register.md">R-001</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped.</td> </tr> <tr> <td>E4</td> <td>P1-003</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method.</td> <td>Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: <a href="docs/decision_log.md">D-018/C-003</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Elevated value: gates Q6 boundary sensitivity (C-003).</td> </tr> <tr> <td>E5</td> <td>P1-004</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method.</td> <td>Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: <a href="docs/risk_register.md">R-011</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Partial.</td> </tr> <tr> <td>E6</td> <td>P1-006</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L).</td> <td>Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: <a href="docs/phase_2/hardware_slice_implementation_guide.md">Remote gate / NV-GATE-2</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>.</td> </tr> <tr> <td>Q1</td> <td>P2-015</td> <td>P2 Next Slice</td> <td>PARTIAL; READY [QUIET-MAC]</td> <td>Collect the first claim-grade Window A floors in one clean prospective quiet window per the claim-window run-book: mint the drift bound in-window, then run the start triplet, midpoint reference, and end triplet before the a8 re-verdict and Splitwise sizing.</td> <td>Reducer-0.5.2/0.6.2 strict-valid calibration bundles; per-metric floor_abs_j and floor_cmp_j; governed idle uncertainty retained; calibration manifest hash cited by later reports. Evidence: Versioned strict-valid calibration bundles; Per-metric/window-class floor_abs_j + floor_cmp_j; Calibration manifest hash cited by later reports. Authority: <a href="docs/phase_2/detection_floor.md">D-054 + detection floor spec</a>. Acceptance: <a href="docs/phase_2/phase_2_exit_checklist.md">Phase 2 exit checklist</a>. Fence: Claim-bearing collection requires fresh 59-pulse protocol-v3 calibration BRACKETING the window (consumed max(B_pre,B_post)); floor artifacts are claim-licensing only from same-custody-session governed extraction until FLOOR-BIND-01 closes (D-078 clause 8 (L1) + bracketing ruling). Note: PR #79 instrument repair and PR #85 SCREEN+BUDGET rules are merged; the start gate is one clean quiet window executed per docs/phase_2/window_runbook.md.</td> </tr> <tr> <td>Q2</td> <td>P2-006</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (Window-A floors measured first) [QUIET-MAC]</td> <td>Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison.</td> <td>Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: <a href="docs/phase_2/phase_2_plan.md">Phase 2 plan + analysis plans</a>. Acceptance: <a href="docs/phase_2/phase_2_exit_checklist.md">Phase 2 exit checklist</a>. Note: Software interpretation gates are satisfied; execution remains blocked until P2-015 Window-A floors complete.</td> </tr> <tr> <td>Q3</td> <td>P2-010</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (quiet-window tail available after floors) [QUIET-MAC]</td> <td>P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail.</td> <td>joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: <a href="docs/contracts/analysis_plans.md">AP-5 + affine stream log</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-010 acceptance</a>. Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains.</td> </tr> <tr> <td>Q4</td> <td>P2-019</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC]</td> <td>q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6).</td> <td>Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: <a href="docs/contracts/analysis_plans.md">AP-1</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-019 acceptance</a>.</td> </tr> <tr> <td>Q5</td> <td>P2-020</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC]</td> <td>Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts.</td> <td>Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: <a href="docs/contracts/analysis_plans.md">AP-6 + D-046</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-020 acceptance</a>. Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6).</td> </tr> <tr> <td>Q6</td> <td>P2-012</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (identification-core runs after Window A) [QUIET-MAC]</td> <td>Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases.</td> <td>Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: <a href="docs/contracts/analysis_plans.md">AP-4 + D-039/D-040</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-012 acceptance</a>. Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27).</td> </tr> <tr> <td>Q8</td> <td>P2-046B</td> <td>P1 Phase Gate</td> <td>READY [QUIET-MAC]</td> <td>Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts.</td> <td>Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C6</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-046B acceptance</a>. Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution.</td> </tr> <tr> <td>Q9</td> <td>P2-047B</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (Window-A floors exist), P2-047A (frozen controller-overhead harness exists) [QUIET-MAC]</td> <td>Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict.</td> <td>Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C7</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-047B acceptance</a>.</td> </tr> <tr> <td>A0</td> <td>P2-035</td> <td>P3 Research Expansion</td> <td>BLOCKED — P2-015 (P2-015 detection floors measured) [AGENT]</td> <td>RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests).</td> <td>Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: <a href="docs/specs/rq_energy_variance_design.md">RQ-ENERGY-VARIANCE candidate design</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-035 acceptance</a>. Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine).</td> </tr> <tr> <td>A3</td> <td>FLOOR-BIND-01</td> <td>P1 Phase Gate</td> <td>READY [AGENT]</td> <td>Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions.</td> <td>Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: <a href="docs/decision_log.md">D-078 clause 8 (confirmation round 9, registered limitation L1)</a>. Acceptance: <a href="docs/process/state_kernel.json">FLOOR-BIND-01 acceptance</a>. Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed.</td> </tr> <tr> <td>A4</td> <td>AXI-SB-ADAPTER</td> <td>P2 Next Slice</td> <td>READY [AGENT]</td> <td>Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims.</td> <td>The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: <a href="docs/specs/axi/sb_static_batch_verdict.md">AXI-SB verdict document (supported; mint-on-supported follow-on)</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SB-ADAPTER acceptance</a>. Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership).</td> </tr> <tr> <td>A6</td> <td>AXI-SD</td> <td>P2 Next Slice</td> <td>READY [AGENT]</td> <td>Prepare the matched dense/MoE pair proposal with the consult&#39;s pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT.</td> <td>A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016&#39;s cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: <a href="docs/axi-handoff.md#4-work-program-post-audit-clearance-streams">AXI handoff work program S-D</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SD acceptance</a>. Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership).</td> </tr> <tr> <td>A7</td> <td>AXI-SE</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (P2-015 publishes Window-A floors before AXI analysis plans are finalized) [AGENT]</td> <td>Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult&#39;s floor and ownership closures.</td> <td>The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A&#39;s gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: <a href="docs/axi-handoff.md#4-work-program-post-audit-clearance-streams">AXI handoff work program S-E</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SE acceptance</a>. Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership).</td> </tr> <tr> <td>A16</td> <td>P3-000</td> <td>P3 Research Expansion</td> <td>BLOCKED — R-003 (user approves the 3.0.2 installs (R-003)) [AGENT]</td> <td>KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8).</td> <td>Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: <a href="docs/decision_log.md">D-035/D-036</a>. Acceptance: <a href="docs/phase_3/phase_3_exit_checklist.md">Phase 3 exit checklist</a>. Note: 3.0.1 complete and merged (PR #9, replay_supported).</td> </tr> <tr> <td>A17</td> <td>P2-022</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)) [AGENT]</td> <td>Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported).</td> <td>3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: <a href="docs/decision_log.md">D-041 (post-2M gate)</a>. Acceptance: <a href="docs/contracts/adapter_contracts.md">Adapter contract</a>. Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission.</td> </tr> <tr> <td>A18</td> <td>P2-023</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded) [AGENT]</td> <td>HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy.</td> <td>Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: <a href="docs/decision_log.md">D-041 (post-2M gate)</a>. Acceptance: <a href="docs/research_question_bank.md">RQ bank import-smoke design</a>. Fence: No pass@k, accuracy, or capability claim (D-041).</td> </tr> <tr> <td>A19</td> <td>P2-024</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (2M reductions identify floor/MDE headroom), P2-015 (Window-A floors measured) [AGENT]</td> <td>Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC].</td> <td>Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: <a href="docs/research_question_bank.md">C-015 + RQ bank</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-024 acceptance</a>.</td> </tr> <tr> <td>A21</td> <td>P3-001b</td> <td>P3 Research Expansion</td> <td>BLOCKED — P2-006 (2M affine coefficients exist) [AGENT]</td> <td>Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049).</td> <td>AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: <a href="docs/decision_log.md">D-048/D-049</a>. Acceptance: <a href="docs/contracts/analysis_plans.md">Analysis plans (split row)</a>.</td> </tr> <tr> <td>A22</td> <td>P2-004</td> <td>P2 Next Slice</td> <td>PARTIAL; READY; GATES close: P1-001 [AGENT]</td> <td>Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding.</td> <td>Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: <a href="docs/decision_log.md">D-016</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Provisional small-model pick 2026-07-06 opens 2G.</td> </tr> <tr> <td>A23</td> <td>P2-005</td> <td>P2 Next Slice</td> <td>PARTIAL; READY; GATES live_promotion: P1-006 [AGENT]</td> <td>Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute.</td> <td>Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: <a href="docs/specs/c027/nv-gate-2_live_promotion.md">NV-GATE-2 live-promotion spec</a>. Acceptance: <a href="docs/phase_1/2k_live_verification_checklist.md">2K live verification checklist</a>. Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open.</td> </tr> <tr> <td>A24</td> <td>P2-016</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (the 2M corpus exists) [AGENT]</td> <td>Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment.</td> <td>Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: <a href="docs/reviews/2026-07-09-c027-whole-project-review.md">C-011 ledger + C-027 (post-2M umbrella)</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-016 acceptance</a>. Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake.</td> </tr> <tr> <td>A25</td> <td>P2-047A</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (Window-A floors exist before overhead design is frozen) [AGENT]</td> <td>Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes.</td> <td>A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C7</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-047A acceptance</a>. Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7).</td> </tr> <tr> <td>A29</td> <td>DOC-008-REFLECTION</td> <td>P4 Polish</td> <td>READY [AGENT]</td> <td>Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6.</td> <td>Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 reflection-protocol retirement</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 reflection-protocol retirement</a>. Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence).</td> </tr> <tr> <td>A30</td> <td>DOC-008-STATUS</td> <td>P4 Polish</td> <td>READY [AGENT]</td> <td>Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8.</td> <td>Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 PROJECT_STATUS compaction</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 PROJECT_STATUS compaction</a>. Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence).</td> </tr> <tr> <td>A31</td> <td>DOC-008-INTAKE</td> <td>P4 Polish</td> <td>READY [AGENT]</td> <td>Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9.</td> <td>Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 intake and procedure reconciliation</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 intake reconciliation</a>. Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence).</td> </tr> <tr> <td>A32</td> <td>DOC-008</td> <td>P4 Polish</td> <td>PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS [AGENT]</td> <td>Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked.</td> <td>Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 state-kernel specification</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 required outcomes</a>. Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live.</td> </tr> <tr> <td>A33</td> <td>P2-050</td> <td>P3 Hardening Candidates</td> <td>READY [AGENT]</td> <td>Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2.</td> <td>Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives i </div> </div> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>TASK_QUEUE.md · commit de665ea · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/stream_logs/2026-07-17-axes-foldin.md:25:Q4 rather than proliferate independent theses.
docs/stream_logs/2026-07-17-axes-foldin.md:33:| C5-2.5c | primary bank Q4 break-even rider; registry alias on C5-2.5 | candidate | L2 | PF | no serving-system or cross-hardware generalization from one pair; native MTP stays contingent and in its separate frozen family |
docs/stream_logs/2026-07-17-axes-foldin.md:38:| C5-2.14 | bank rider attached to Q4/AP-1 | candidate | L2 | PF | no new-thesis framing and no coefficient-direction claim below P2-015 floors |
docs/stream_logs/2026-07-17-axes-foldin.md:41:| RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | guard attached to RQ-SHORT-PREFILL-RESOLVABILITY/RQ-METHOD-FLOOR | candidate guard | L1 methodology | NS | no module-energy fraction, request-phase relabeling, or module-share inference from regression slopes |
docs/stream_logs/2026-07-17-axes-foldin.md:49:rider even though Q4's already-existing AP-1 machinery can separately support
docs/stream_logs/2026-07-17-axes-foldin.md:67:| C5-2.12–C5-2.14 as independent theses | Each is useful only as a refinement of the existing context/KV-growth, replay/cache, or Q4/AP-1 question. They remain candidate riders. |
docs/run_reports/2026-07-31-claims-desk-session.md:31:**PR #90** (`81a484b`): five campaigns — `linearity_ramp`, `null_ladder`,
docs/run_reports/2026-07-31-claims-desk-session.md:32:`additivity_shapes`, `micro_delta` (k=64), `long_holds` — **150 configs** across
docs/run_reports/2026-07-31-claims-desk-session.md:40:`linearity_ramp`, `null_ladder`, `additivity_shapes`, `long_holds` — flipped to
docs/run_reports/2026-07-31-claims-desk-session.md:42:deterministically, sidecars re-pinned, one stage dry-run clean). `micro_delta`
docs/run_reports/2026-07-31-claims-desk-session.md:43:stays `draft_pending_slope` by design.
docs/run_reports/2026-07-14-audit-resume-axi.md:162:five-axis Q4 agenda; DRIFT.md is current for Ed's one manual deploy.
docs/stream_logs/2026-07-16-advisor-refresh.md:40:`PROJECT_STATUS.md` Measurement Methodology Highlights and Q4 agenda; D-071 at
docs/run_reports/2026-07-30-sweep-techniques.md:47:**Adopt/adapt (Jay/Ostapenco):** closest published template for the powermetrics-vs-wall study: fixed machine config, N=10 reps, 1-min cooldowns, component-targeted workloads (their compute/memory/mixed maps to decode-heavy/prefill-heavy/idle), automated + published artifact. Resample-then-correlate, **then regress with wall as response** — their headline: slope 1.17–1.18, i.e. the software-vs-wall gap is load-dependent, **never a constant offset**, and must be characterized per node. Their §V-C2 honesty: refuse to rank where no reference exists — the wall meter validates *totals only*; phase splits stay validated only by the pulse-train method and should be labelled so. Disclose campaign energy (theirs: ~480 kWh).
docs/run_reports/2026-07-30-sweep-techniques.md:49:**Avoid:** consumer-grade reference with no stated accuracy class (Khan's Plugwise, internally inconsistent 0.1 vs 10 Hz); publishing accuracy claims where no reference exists (Khan's EC2 arm); leading with Pearson r (0.95–0.99 doesn't discriminate — slope/intercept/MAPE do); reference sampling slower than the tool under test (CCGRID's 1 Hz reference was their binding constraint); trusting embedded telemetry (BMC/SMC) as a second reference without characterization.
docs/stream_logs/2026-07-09-stats.md:41:| AP-1 | FAM-Q4-GRID-MODEL | primary | Holm across fixed/prompt/decode and holdout claims; sensitivities secondary unless frozen primary. |
docs/stream_logs/2026-07-09-stats.md:51:  claim-bearing mechanics: Q4 modeling, 2M shape asymmetry, within-boundary
docs/run_reports/2026-07-28-floor-mint-implementation.md:133:  magistrate to should-fix; closed in the mint series via ratified Q4
docs/stream_logs/2026-07-08-precampaign-review.md:47:  question for Q4 coefficients.
docs/run_reports/2026-07-30-sweep-mechanisms.md:28:- Implied effect shape: full attention's J/token grows with context (KV reads); linear layers' does not. Nobody has published the on-device energy-vs-context *slope*.
docs/run_reports/2026-07-30-sweep-mechanisms.md:74:| 5 | Hybrid-linear vs full-attn: J/tok-vs-context slope | GQA slope from KV reads; linear ~flat; tens of % at 16–32k ctx | context-sweep design, per-point Δ ≥ 50–100 J | ~5–10× (**runtime risk**) |
docs/run_reports/2026-07-30-sweep-mechanisms.md:75:| 6 | MoE top-k slope (same weights) | expert-FFN energy ~∝ k; maybe 20–40% of J/tok | ×2048 ≈ 100–250 J | ~10× (**mechanism knob unverified**) |
docs/run_reports/2026-07-30-sweep-mechanisms.md:86:5. **Attention slope**: on-device d(J/tok)/d(context) for hybrid-delta vs full attention — 2605.11999 is H200-only and whole-request.
docs/stream_logs/2026-07-09-rqreg.md:35:  families such as Q4 with session-shape and coefficient transport.
docs/run_reports/2026-08-01-desk-adjudication-session.md:103:   scope** (the other six additivity cells and both null rungs remain
docs/run_reports/2026-08-01-desk-adjudication-session.md:170:  ramp survives as micro_delta DESIGN input + corroboration diagnostics.
docs/process_traces/2026-07-16-device-list-brief/model-search-12gib.md:134:| **1** | **Qwen3-4B** | Adoption count NEEDS-WEB; Apache-2.0 verified | MLX-Q4 plus MLX/llama.cpp/vLLM architecture support recorded; exact GGUF-Q4 and CUDA-Q4 pins NEEDS-WEB. Freeze non-thinking identically across runtimes. [memo.md:223](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-axi-sd-web-verification/memo.md:223) | Strong: ≈2.52 GiB weights + ≈1.14 GiB KV at 8,320 tokens leaves ≈6.54 GiB before the 10.2 GiB ceiling. Medium-high repin cost. [memo.md:174](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-axi-sd-web-verification/memo.md:174) |
docs/process_traces/2026-07-16-device-list-brief/model-search-12gib.md:135:| **2** | **Qwen3-1.7B** | ≈5.8M monthly downloads in the dated brief; exact license receipt NEEDS-WEB | Official MLX-Q4, GGUF and native vLLM paths recorded. Same non-thinking complication. [brief.md:98](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-device-list-brief/brief.md:98), [brief.md:101](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-device-list-brief/brief.md:101) | Best expected headroom and lowest-evidence-risk successor; medium repin cost. |
docs/process_traces/2026-07-16-device-list-brief/model-search-12gib.md:137:| **4** | Gemma-3-4B-IT | Adoption NEEDS-WEB; custom, gated Gemma terms verified | Exact 4B MLX-Q4/GGUF-Q4/CUDA pins NEEDS-WEB. Its multimodal architecture may require `mlx-vlm`, unlike the proven `mlx-lm` adapter. [brief.md:102](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-device-list-brief/brief.md:102) | Strong expected fit, but high adapter/licensing cost. |
docs/process_traces/2026-07-16-device-list-brief/model-search-12gib.md:143:Every repin starts a new evidence era: preserve Qwen2.5 results, regenerate tokenizer-bound manifests, repeat MLX/CUDA/GGUF, G10/KV/batch gates, and rebuild BF16/Q8/Q4 from one source revision. [brief.md:104](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-device-list-brief/brief.md:104), [sd_model_pair_scorecard.md:471](/Users/edr/code/JouleWise/docs/specs/axi/sd_model_pair_scorecard.md:471)
docs/process_traces/2026-07-16-device-list-brief/model-search-12gib.md:153:Qwen3-30B-A3B still fails outright: its crude Q4 floor is **14.218 GiB**, and the recorded artifact is **15.995 GiB**, both above 10.2 GiB before KV or activations. [memo.md:202](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-axi-sd-web-verification/memo.md:202) Qwen1.5-MoE-A2.7B becomes smoke-admissible by weight under 12 GiB, but ≈8.34 GiB weights + ≈1.5 GiB KV leaves only ≈0.36 GiB, while its dense sibling already fails active matching and has mismatched non-Apache licenses. [memo.md:285](/Users/edr/code/JouleWise/docs/process_traces/2026-07-16-axi-sd-web-verification/memo.md:285)
docs/process_traces/2026-07-16-device-list-brief/model-search-12gib.md:157:- **P1:** For all six ranked models, what are the 2026-07-16 monthly downloads, exact license/revision/gating, and immutable MLX-Q4, GGUF-Q4 and vLLM-compatible CUDA-Q4 artifact IDs, sizes and revisions?
docs/process_traces/2026-07-16-device-list-brief/model-search-12gib.md:159:- **M1:** Enumerate public 7.0–14.5B-total decoder MoEs, giving exact active parameters including shared experts, same-release dense sibling/tokenizer/tuning state, license, MLX-lm 0.31.3/GGUF/vLLM support, Q4 byte size, and KV bytes/token at the G10 shape.
docs/research_question_bank.md:14:## Promoted 2026-07-07 (now Q4-Q6 in PROJECT_STATUS)
docs/research_question_bank.md:16:- **Q4 Fixed-vs-marginal energy model** — fit
docs/research_question_bank.md:145:`affine_mod_ladder_v1`, `jw_mixed_v1`, `q4_l3_shape_grid_v1`, the content
docs/research_question_bank.md:282:`q4_l3_shape_grid_v1` prompt/decode cells stay under `shape`, not
docs/research_question_bank.md:475:| Can Q4 fit fixed + prompt + decode energy terms? | L3 | "For `<target/model/quant/policy>`, the categorical model `E = fixed + prompt_level + decode_level` predicted held-out cells `(512,256)` and `(4096,512)` within `<error>` after floor and residual checks." | P2-019 `q4_l3_shape_grid_v1`, AP-1. | Holdouts may fail or effects may be below floor, forcing L1/L2 downgrade. |
docs/research_question_bank.md:562:**Q4's fixed-vs-marginal model turns benchmark data into engineering
docs/research_question_bank.md:634:  recovery slopes; n≥5 blocks. Hardware: now. Methodology: cooldown-gate
docs/research_question_bank.md:892:    dynamic schedule), i.e. does per-round proposed work enter the Q4
docs/research_question_bank.md:898:  - **C5-2.5c — primary Q4 break-even rider.** Status: **candidate**;
docs/research_question_bank.md:941:- **C5-2.8 Placement-policy optimality from Q4 coefficients.** Can
docs/research_question_bank.md:977:- **C5-2.12 Bounded-window KV marginal-slope rider.** Status:
docs/research_question_bank.md:979:  (`RotatingKVCache` via `max_kv_size`) flatten the marginal J/token slope
docs/research_question_bank.md:1000:- **C5-2.14 Q4 cache-policy coefficient rider.** Status: **candidate**;
docs/research_question_bank.md:1001:  earliest phase: **PF**. Do KV-cache-policy contrasts move the fitted Q4
docs/research_question_bank.md:1004:  Q4/AP-1's existing holdout machinery (D-070 clause 5)**. The candidate
docs/research_question_bank.md:1006:  framing — this is a Q4 stress test, not a KV-energy model; no
docs/run_reports/2026-07-24-screen-budget-gauntlet.md:124:Redeployed after the merge: deploy `dep_2I04CG6tQ4t0mzY7`, capsule
docs/run_reports/2026-07-08-suite-science-expansion.md:21:  - Program v2 (D-039): `q4_l3_shape_grid_v1` (4x3 + interpolation/
docs/run_reports/2026-07-08-suite-science-expansion.md:100:- **Catches (unique, by layer):** lead pre-lens audit 4 (incl. Q4-at-L3
docs/run_reports/2026-07-08-suite-science-expansion.md:112:  OVERTURNED lead single-window — position reversal), Q4 grid (peer
docs/process_traces/2026-07-16-device-list-brief/brief.md:78:| Q4–Q6 | Q4 is fitted per target; Q5’s cross-device extension merely benefits from more targets; Q6 needs the wall meter, not Jetson. [docs/research_question_bank.md:16](/Users/edr/code/JouleWise/docs/research_question_bank.md:16), [docs/research_question_bank.md:24](/Users/edr/code/JouleWise/docs/research_question_bank.md:24) |
docs/process_traces/2026-07-16-device-list-brief/brief.md:109:- Rebuild §8’s BF16/Q8/Q4 ladder from one newly frozen source revision; community conversions are discovery evidence, not acceptable lineage. [docs/specs/axi/sd_model_pair_scorecard.md:471](/Users/edr/code/JouleWise/docs/specs/axi/sd_model_pair_scorecard.md:471), [docs/specs/axi/sd_model_pair_scorecard.md:508](/Users/edr/code/JouleWise/docs/specs/axi/sd_model_pair_scorecard.md:508)
docs/process_traces/2026-07-16-device-list-brief/brief.md:115:1. Require immutable source/license, derived MLX-Q4/GGUF-Q4/CUDA artifact receipts, three-runtime generation, G10, KV, and no-thinking-policy evidence.
docs/run_reports/2026-07-17-window-a-floors.md:277:decoding Q4 break-even rider, C5-2.5b as proposal-work secondary, and
docs/run_reports/2026-07-07-flagship-qwen35-122b.md:9:runtime details. They are hypothesis-generating for Q4's fixed-vs-marginal
docs/run_reports/2026-07-07-flagship-qwen35-122b.md:58:**Finding (first real Q4 data point):** energy per output token scaled
docs/run_reports/2026-07-07-flagship-qwen35-122b.md:64:fixed-vs-marginal structure Q4's model fits — two points on the curve
docs/site_src/research.html:237:      <strong>Q3:</strong> what is the energy–latency trade? <strong>Q4:</strong>
docs/process_traces/2026-08-05-t3-amend/AMENDMENT-MAP.md:46:| A22 | Q4 — “TUI operation remains available” only outside `[QUIET-MAC]`; claim runs use an ordinary guarded shell with zero agent sessions | **LANDED** — contract §4, final t3-routing paragraph. |
docs/process_traces/2026-08-05-t3-amend/AMENDMENT-MAP.md:47:| A23 | Q4 / SX2 — corrected provenance of Sol's full-shadow dissent | **CHECKED / NO NEW WRITE** — the correction is an evidence-record matter and already lives in frozen cure exhibit SX2 plus the synthesis; it creates no bridge rule. |
docs/run_reports/2026-07-30-paper-outline-v1.md:29:  as evidence; (C-iv) full instrument characterization: linearity, null
docs/run_reports/2026-07-30-paper-outline-v1.md:86:- Detection threshold: micro-delta probes walking known effects across
docs/run_reports/2026-07-30-paper-outline-v1.md:89:- Attribution: additivity (phases sum to whole) + causal invariance
docs/run_reports/2026-07-30-paper-outline-v1.md:90:  (prefill energy independent of output length; slope 0 ± ε).
docs/run_reports/2026-07-30-paper-outline-v1.md:92:- Temporal: long holds → drift curvature within allowance; measured
docs/run_reports/2026-07-30-paper-outline-v1.md:138:2. Metrology window A: linearity ramp + additivity shapes + null(mid) +
docs/run_reports/2026-07-30-paper-outline-v1.md:139:   holds in tails → C1, C4, C5 (+slope for C3 design).
docs/run_reports/2026-07-30-paper-outline-v1.md:140:3. Metrology window B: null ladder ends + micro-deltas (k from ramp
docs/run_reports/2026-07-30-paper-outline-v1.md:141:   slope) + stability repeat #2 → C2, C3, C6 partial.
docs/run_reports/2026-07-09-cp5-resume.md:87:cold-start Q4 term are out of claim scope until a load-window capture
docs/run_reports/2026-07-09-cp5-resume.md:95:unresolvable); Q4 fixed+prompt+decode model with holdouts (P2-019/AP-1,
docs/run_reports/2026-08-01-metrology-window-b.md:12:**additivity 23/24 single-root** (C4), clean calibration bracket
docs/run_reports/2026-08-01-metrology-window-b.md:18:item; the remainder (null_o2048, long_holds, one additivity slot) moves
docs/run_reports/2026-08-01-metrology-window-b.md:33:additivity was 21/24 at final state (not 23/24), and the charger is a
docs/run_reports/2026-08-01-metrology-window-b.md:72:   #2 `mtadd-p2048o0128-r08` (06:13 PT, same signature, additivity at
docs/phase_2/splitwise_decode_campaign.md:519:**Q4 — Ratify the two-arm `stack_scope.arms` shape** replacing p2_015's scalar

exec
/bin/zsh -lc "sed -n '1,210p' docs/run_reports/2026-07-31-claims-desk-session.md
sed -n '1,210p' docs/run_reports/2026-07-30-paper-outline-v1.md
rg -n \"linearity|slope|decode.*J|micro\" docs/run_reports/2026-08-01-desk-adjudication-session.md docs/run_reports/2026-07-17-window-a-floors.md docs/process_traces -g '*.md' | head -180" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# 2026-07-31 — Claims desk day: metrology suite merged, four decisions, and the cooldown-join gauntlet's first two commits

A ~4 h desk session (no measurement; the machine stayed free for the night's
window). Four parallel lanes ran first and produced four decision entries and
two merges; the second half was the cooldown-join gauntlet's execution arc,
which landed commits 1–2 through four independent audits and a second cold gate.

Main moved `7ee680c` → `67d268a` (PR #91 merge).

## Lane 1 — MANIFEST-CONTRAST design consult (D-095)

A rule-2 pre-decision consult (Sol xhigh, one round, explicit license to
disagree) over the contrast claim's manifest design. Adopted as **D-095**:
analysis-manifest **v3** as a new module plus dispatcher with v1/v2 byte-frozen,
governed ABBA block derivation, `folded_sha256` arm binding, Holm m=1 two-sided
positive-direction testing, and a `cross_stack_armwise_max.v1` floor rule.

The entry also ratifies the **honest claim dependency chain**, which is now the
governing sequence for the contrast claim:

> `COOLDOWN-JOIN-GAUNTLET-01` → analysis-manifest v3 (D-095) → multi-cell mint
> (`MINT-GENERALIZE-01`) → the gated contrast claim.

Implementation was **not** ordered: D-095 is design-only, queued behind the
gauntlet. Recorded at `27deb3e`.

## Lane 2 — metrology suite review, PR #90, and the D-096 freeze

The `metrology_v1` campaign suite (authored overnight by Sol xhigh under
enforced `WRITE_SCOPE`, commit `a93a2c6`) went through lead review and merged as
**PR #90** (`81a484b`): five campaigns — `linearity_ramp`, `null_ladder`,
`additivity_shapes`, `micro_delta` (k=64), `long_holds` — **150 configs** across
23 condition families, deterministic regenerate-twice generators, per-campaign
and suite READMEs with duration arithmetic and window packing.

The ratification pass over the READMEs' OPEN QUESTIONS and the PR review findings
landed as **D-096** (`f010d5a`): `staleness_sentinel` `use_role`, plan-only field
shapes, and recorded vocabulary fallbacks ratified; the F2 `--k` hardening
registered as a standing pre-replacement condition. Four window-A plans —
`linearity_ramp`, `null_ladder`, `additivity_shapes`, `long_holds` — flipped to
`freeze_status: frozen_before_measurement` (no member ever measured, regenerated
deterministically, sidecars re-pinned, one stage dry-run clean). `micro_delta`
stays `draft_pending_slope` by design.

**Metrology window A now needs only Ed's §5A and a launch.**

Same commit lowered `build_site`'s `DECISION_LOG_PART_MARKDOWN_BYTES` from
18000 to 12000: the source-based pagination ceiling had let a dense-entry page
render past the 30 kB packer shard budget (bisected to the D-095 entry). The
lower ceiling restores compliant splits structurally rather than by trimming
governance records.

## Lane 3 — queue reconciliation (`8d991cc`)

`QUEUE-RECONCILE-01` closed: `P2-015` (first claim-grade Window A floors)
retired to the completed table, its **7 hard dependents** flipped to
satisfied-with-evidence (invariant 3 then mechanically promoted `AXI-SE`,
`P2-006`, `P2-010`, `P2-035`, `P2-047A` from blocked to queued;
`P2-024`/`P2-047B` stay blocked on their remaining edges), and
`COOLDOWN-JOIN-DA1-01` promoted from the intake table into the live kernel at
agent rank 13.

## Lane 4 — the gauntlet counting domain (D-094)

D-088 clause 2 mandated a bounded pre-decision consult before the counting
domain could be chosen. Sol xhigh ran it with record-by-record corpus ground
truth. **D-094** (`5960625`) adopts the **composed** design: prospective
manifests record a closed per-`existing`-row outcome enum
(`usable|failed|incomplete|waived`); legacy v1 rows classify by exact, unique
manifest/member/bundle binding to `campaign_log.jsonl`, failing closed on
missing, inconsistent, ambiguous, or unparseable bindings. Declaration order
defines physical-occurrence segments. The full truth table preserves D5-J's
struck cell, and DA-1 closes at the raw reader boundary — the shape D-093
required. Rejected: writer-bit-only and order-only.

D-094 also **corrects D-088's trigger record on the evidence**: the 7B corpus
carries **44 benign** duplicate ids (24 `invoked→existing`, 20
`invoked→existing→existing`) plus **2 genuine**, not "46 benign". D-088's
structural holding is unaffected.

The landing order it fixed — each commit independently audited, C1 first — is
what the rest of the day executed.

## The gauntlet arc — PR #91 (`67d268a`)

Branch `impl/cooldown-gauntlet`. **Every audit in this arc was an independent,
read-only Sol xhigh session**; no session graded its own work.

1. **C1** (`75e9f29`) — result-map completeness: the join's returned keyset is
   explicitly the union of candidate emission ids and normalized declared ids,
   and every unresolved id gets the complete five-field refusal payload from one
   shared literal.
2. **C1 audit → response** (`c0adc93`). The audit FAILED on classification
   honesty: emissions are structurally a subset of declarations, so C1's commit
   message overclaimed a behavior delta that is unreachable through the public
   join, and the completeness test did not discriminate. Response extracted
   `_cooldown_result_bundle_ids` as a pure, unit-locked helper with the
   invariant documented and the union's second leg marked DEFENSIVE, added the
   discriminating unit lock, and corrected the record: C1's tests are contract
   locks, not defect regressions. Bench-implemented by the lead (below the
   delegation threshold).
3. **C2 — reader/domain, closing DA-1** (`e749c95`). The supersession reader now
   returns recognizable raw candidates with validation results
   (`supersession_entry_validation_results`; `None` = global fail-closed), so a
   malformed same-bundle record can no longer disappear before ambiguity
   evaluation: the **V4-driver shape (valid exact record + corrupted same-bundle
   clone) REFUSES**, closing DA-1 per D-093/D-094.
   `validated_supersession_entries` survives as a documented compatibility
   filter for non-ambiguity callers.
4. **Audit → FAIL, three blockers → fix** (`8880395`). B1: an `outcome` field on
   a v1 existing row is malformed and refuses. B2: legacy members bind to an
   exact campaign-log row **identity**, each row authenticating at most one
   existing occurrence, so the `I-E-E` one-row-reuse collapse refuses. B3:
   selected-path member invariants apply at catalog admission, so a malformed
   member in **any** catalog manifest — selected or sibling — refuses the whole
   join per C5. All three regressions fail on parent `c0adc93` and pass post-fix.
5. **Delta re-audit → FAIL, B1 only.** The fix had discriminated v2 by
   self-asserted `schema_version`, and the re-audit demonstrated a **one-file
   relabel** of a real 7B v1 manifest bypassing the mandatory legacy log binding
   while still resolving 57/57.
6. **Cold gate (mandatory).** B1 had now failed **two consecutive formulations**
   with the same signature, so per the standing rule-11 trigger the next spend
   was a gate, not a third round: a **cold Fable instance plus an Opus
   contract-lens refuter**, and they **converged** — no third in-manifest
   formulation exists, because with no writer emitting the enum every in-manifest
   marker is self-asserted. Authenticated discrimination needs writer-minted
   evidence and therefore belongs to commit 3.
7. **D-097** (`1ef40e5`, deferral commit `a9b9d4a`). The magistrate synthesis
   adopts the refuter's stricter **O3 variant**: strike commit-2's v2
   outcome-consumption clauses *and* remove v2 from the join's accepted schema
   set, so the reader's accepted set exactly equals the writer's emitted set
   (**v1 only**). A v2-labelled manifest refuses at the catalog gate; an
   `outcome` field on any member refuses. Grounds: no legitimate writer can
   produce either today (`run_campaign.py` emits only v1; its own resume/policy
   scanners skip non-v1; **zero v2 manifests across all 29 corpora**), so
   presence is uniform malformation. The relabel probe became a permanent
   regression that fails on parent `8880395`.
8. **Fresh delta re-audit → PASS, zero findings.** Full suite lead-run at the
   branch head: **2305 OK**. PR #91 merged at `67d268a`.

D-097's four binding merge-train release conditions were all met: the deferral
commit landed on the branch, a regression proves the relabel probe refuses, the
fresh delta re-audit passed with the suite green and lead-verified, and both
real-corpus mappings stayed hash-identical (**57/57 and 47/47**). B2, B3, and
DA-1 remain independently verified closed.

Two commit-3 riders are on the record in D-097: (i) the legacy binding
authenticates but **discards** the classified status — a v1 existing row bound to
a failed or incomplete log row is representative-equivalent to usable, so
commit 3 must decide whether classification beyond authentication is consumed;
(ii) the v1 log binding is **anti-malformation, not anti-tamper** — a coordinated
manifest+log rewrite defeats it, and the tamper layer is source-manifest hashing
in the verdict path.

## Two cold gates in one day

This was the day's **second** cold gate. The first, D-093, ruled on DA-1 during
the D5-J merge and produced the boundary-fix contract that commit 2 executed.
The second, D-097, ruled on B1's second same-signature formulation. Both were
convened by mandatory trigger rather than discretion; both returned unanimous or
converged verdicts; neither required a magistrate dissent.

## Verification ledger

- Suite counts at branch heads across the arc: **2301 → 2304 → 2305** tests,
  worktree skip convention **21**.
- Final branch head: lead-run **2305 OK**; fresh delta re-audit PASS with zero
  findings.
- C1 audit, C2 audit, the B1 delta re-audit, and the final delta re-audit were
  four **independent read-only Sol xhigh** sessions.
- Real-corpus preservation held at every commit: 57/57 + 2 supersessions (7B
  window) and 47/47 + 1 (contrast window), hash-identical at the merged head.
- Metrology docs trio at `f010d5a`: **67 OK**.
- The post-merge canonical suite on `main` at `67d268a` was in flight at report
  write; the magistrate records its result in RUN_STATE §Current Verification.

## State at close

- `COOLDOWN-JOIN-DA1-01` is **CLOSED** by the PR #91 merge and retired to the
  completed table.
- `COOLDOWN-JOIN-GAUNTLET-01` remains **OPEN** on commit 3: writer outcome
  emission + a writer-external authenticated discriminator + reader
  re-acceptance + the D-094 v2 truth-table row, as **one composed, audited
  change** per D-097.
- **D-088 clause 3(c) and the D-093 raw-vs-validated supersession scans stay
  binding** on every claim consumption until the gauntlet fully closes; the
  no-mint-from-a-duplicate-bearing-corpus condition still blocks
  `MINT-GENERALIZE-01`.
- Metrology window A is launch-ready on frozen plans (D-096) and needs Ed's §5A.
- D-095's v3 implementation is unblocked file-wise and orderable next session.

## Process Trace

- Active stop card at start: none
- Skills/playbooks used: codex-delegation; adversarial-review (§C-028 delta
  re-audit after every fix round); council (cold gate by mandatory trigger);
  rule-2 pre-decision consult; rule-11 standing escalation trigger
- Subagents / delegated sessions:
  - role/lens: counting-domain pre-decision consult — model: Sol xhigh —
    disposition: adopted as D-094
  - role/lens: MANIFEST-CONTRAST design consult — model: Sol xhigh —
    disposition: adopted as D-095
  - role/lens: C1 independent audit — model: Sol xhigh (read-only) —
    disposition: FAIL on classification honesty; answered in `c0adc93`
  - role/lens: C2 independent audit — model: Sol xhigh (read-only) —
    disposition: FAIL, three blockers B1/B2/B3; answered in `8880395`
  - role/lens: delta re-audit — model: Sol xhigh (read-only) — disposition:
    FAIL, B1 only (relabel bypass); escalated to the cold gate
  - role/lens: final delta re-audit — model: Sol xhigh (read-only) —
    disposition: PASS, zero findings; merge cleared
# Paper outline v1 — metrology-centric (post-Rivoire-ratification, 2026-07-30)

*Provenance: verbatim copy of `paper-outline-v1.md` from the 2026-07-30 magistrate session scratchpad
(`/private/tmp/claude-501/-Users-edr-code-JouleWise/abec37a6-31cd-4c56-a8a8-9448acaf12be/scratchpad/`), committed to the repository 2026-07-31.*

Working title (Rivoire to adjudicate; recommendation #1):
**"JouleWise: Detection Floors for LLM Inference Energy Measurement on
Consumer Silicon"**
Alt: "How Many Joules Can a MacBook See?" (workshop register) /
"Joules per Token, With Error Bars" (findings register).

Target shape: 6-page workshop (EuroMLSys ~Feb '27 / HotCarbon ~May '27)
expandable to ICPE full track. Artifact-evaluation-ready by construction.

## 1. Introduction (~0.75 pp)
- Hook: LLM energy numbers are everywhere (leaderboards, policy debates,
  per-query estimates spanning 10×); error bars are nowhere. The field's
  most-used free instrument on consumer hardware (Apple powermetrics) has
  never been validated; its own docs call its outputs estimates.
- Thesis: treat the software power counter as a scientific instrument —
  calibrate it in-session, derive detection floors, refuse claims beneath
  them.
- Contributions (numbered): (C-i) an in-window calibration method that
  measures timing-attribution error for phase-resolved energy integration;
  (C-ii) detection floors composed from measured repeatability,
  worst-case attribution, and measured drift — published with every
  result; (C-iii) a fail-closed collection protocol (admission gates,
  ABBA ordering, custody chains, pre-registration) with its refusal log
  as evidence; (C-iv) full instrument characterization: linearity, null
  response across magnitudes, empirical floor verification, phase-
  attribution causal consistency, drift/settle; (C-v) demonstration
  measurements: phase-resolved J/token for two model sizes with a
  pre-registered contrast [+ quantization ladder if window budget
  allows]; (C-vi) open tool + hash-bound reproducible artifacts.

## 2. Background and the gap (~0.5 pp)
- Three lineages: energy benchmarking rules (SPEC/MLPerf Power — per-run
  uncertainty accounting, but datacenter instruments); software-counter
  validation (RAPL in Action, CCGRID '23 — error bars vs wall power, no
  detection-limit concept, no Apple silicon); LLM energy studies
  (TokenPowerBench, ML.ENERGY, Silicon Showdown, Intelligence-per-Watt —
  breadth without instrument characterization).
- The gap sentence: no published work combines phase-resolved LLM energy
  + consumer silicon + per-measurement error budgets + any validation of
  powermetrics. (Verified sweep 2026-07-30; nearest-neighbor table in §8.)

## 3. The instrument (~1 pp)
- Measurement principle: power sampling integrated between phase-boundary
  events emitted by the runtime adapter (we drive the workload; phases
  are known from code, not inferred from traces). Single-request
  sequential scope AS A DESIGN DECISION: it is what makes phase
  attribution well-posed (contrast: TokenPowerBench's unspecified
  tagging under batching).
- Threat model, 5 threats × defense × evidence-it-fired:
  (1) contamination → admission gates (evidence: XProtect + Time Machine
  catches, quarantine/supersession records); (2) slow drift → ABBA
  cancellation (arithmetic) + measured whole-window allowance from
  dedicated reference runs; (3) attribution/clock → bracketing pulse-train
  calibration (§4); (4) custody/tampering → hash-bound bundles,
  re-derive-never-trust, exclusive writes (evidence: the mint refusing
  its own inputs); (5) analysis flexibility → pre-registration with
  hard literals, fail-closed gates (evidence: refusal-then-repair
  history on the record).
- Protocol figure: window timeline (pre-cal → bound corpus → references →
  members → references → post-cal).

## 4. Error model and detection floors (~1 pp)
- The three measured terms: repeatability (max of worst observed dev and
  Student-t bound, n=10); attribution (measured boundary-placement bound
  × boundary power, worst-case corner composition across ABBA members);
  drift allowance (derived per-window from NEG-8 references).
- Composition: max(statistical, attribution) + allowance; single-count
  discipline; why RSS would be anti-conservative for the worst-case term.
- MDE formalism: powered minimum-detectable-effect δ* = 2.80·σ_D/√m and
  the workload-sizing inversion; prior-ratchet pre-registration.
- Floor values with full decomposition table (1.5B: 7.38 J; 7B: 14.00 J)
  and the finding that floors scale with device power (not model-
  independent).

## 5. Instrument characterization (~1.25 pp — THE core results)
The property/test-signal/result/claim table, one row per campaign:
- Linearity: ramp 128→2048 output tokens; response linear, fitted
  per-token cost = energy standard for later tests.  [CLAIM C1]
- Zero: null (A==A) ladder across magnitudes; unbiased, scatter tracks
  the error model's envelope.                        [CLAIM C2]
- Detection threshold: micro-delta probes walking known effects across
  the floor (0.5×/1×/1.5×/3×); floor operationally verified both
  directions.                                        [CLAIM C3]
- Attribution: additivity (phases sum to whole) + causal invariance
  (prefill energy independent of output length; slope 0 ± ε).
                                                     [CLAIM C4]
- Temporal: long holds → drift curvature within allowance; measured
  thermal settle time vs the 180 s convention.       [CLAIM C5]
- Stability: calibrations/nulls/floors repeated across ≥3 sessions/days.
                                                     [CLAIM C6]
- Internal cross-validation: channel-sum vs package reconciliation
  [+ battery/SMC drain check if feasible].           [CLAIM C7]
- [CONDITIONAL, pending wall-meter decision: external validation —
  regression wall = f(powermetrics) per SPEC/Khan/CCGRID design;
  validates totals only, phase splits remain pulse-train-validated.
                                                     CLAIM C8]

## 6. Demonstration measurements (~0.75 pp)
- Phase-resolved J/token, both models, per-phase denominators,
  context-binned.
- The pre-registered model-size contrast (1.5B vs 7B decode, same-window
  ABBA): effect, CI, effect/floor ratio, "operationally meaningful"
  column. Sublinear scaling observation (4.7× params → 3.8× energy;
  power AND time decomposition).
- [If budget: quantization ladder 4/8/16-bit with per-stack floors.]
- Every number: value ± floor-decomposed uncertainty, effect/floor
  multiple.

## 7. Limitations, scope, and threats to validity (~0.5 pp)
- Internal-to-powermetrics scale (unless C8 lands): gain error would
  bias absolute J uniformly; ratios and detections survive.
- Pulse-to-inference transfer assumption for the attribution bound
  (mitigated by C3).
- One machine, one runtime (MLX), single-request scope; floors are
  per-stack properties (demonstrated, not assumed — the 7 vs 14 J
  result).
- Conservative composition (~3× potential tightening identified, queued).

## 8. Related work (~0.5 pp)
Nearest-neighbor table (from the 2026-07-30 sweep): work × hardware ×
phase-resolved? × error budgets? × pre-registered? × consumer silicon?
Explicit differentiation vs TokenPowerBench (phase energy, no
uncertainty), Illusion-of-Power-Capping (mechanism energy, no error
composition), Silicon Showdown / IPW (Apple silicon, unvalidated
counter), Jay/Khan (validation lineage, no floors, no LLM phases).

## 9. Availability (~0.25 pp)
Tool (pip), hash-bound artifacts, refusal logs, pre-registration
records; artifact-evaluation packaging (ICPE badge target).

## Campaign → claim dependency map (execution order)
1. Contrast window (READY, runs first): feeds §6 + stresses cross-stack.
2. Metrology window A: linearity ramp + additivity shapes + null(mid) +
   holds in tails → C1, C4, C5 (+slope for C3 design).
3. Metrology window B: null ladder ends + micro-deltas (k from ramp
   slope) + stability repeat #2 → C2, C3, C6 partial.
4. Window C (any night): stability repeat #3 + spillover → C6.
5. Desk throughout: C7 reconciliation; MDE machinery; counter-mechanics
   audit (paper §3/§7 support); wall meter iff ratified+hardware [C8].
Total: ~3-4 quiet windows beyond tonight's contrast. September target
comfortable.
docs/run_reports/2026-08-01-desk-adjudication-session.md:170:  ramp survives as micro_delta DESIGN input + corroboration diagnostics.
docs/run_reports/2026-07-17-window-a-floors.md:91:| decode phase, gross — M3 Max / powermetrics SoC rails | 0.786337 J | 1.026892 J | 1.026892 J |
docs/process_traces/2026-07-16-device-list-brief/brief.md:84:Mac + 3080 Ti can be the two physical split nodes. They cannot perform claim-bearing MLX-prefill → vLLM-decode replay: cross-runtime cache portability is out of scope. A shared llama.cpp build plus the same GGUF artifact could qualify only after the cross-machine portability spike passes. [PROJECT_STATUS.md:455](/Users/edr/code/JouleWise/PROJECT_STATUS.md:455), [PROJECT_STATUS.md:521](/Users/edr/code/JouleWise/PROJECT_STATUS.md:521)
docs/process_traces/2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md:182:| `runs_window_7bfloor_20260729/sw7bfloor-df-ph-decode-abs-r{01..10}/summary_metrics.json` | 7B; 128 prompt, 512 output | 7.552262 J; SD 0.194722 J; range 7.373120–7.916055 J | 10 | Clean/PASSED |
docs/process_traces/2026-08-06-qg-census-consult/CONSULT-REPORT.md:35:            "Replace /bin/ps PID listing and per-PID ps parent queries with an accepted KERN_PROC_ALL inventory containing at least PID, parent PID, and microsecond start time. Treat that payload as the presence/topology snapshot.",
docs/process_traces/2026-08-06-qg-census-consult/CONSULT-REPORT.md:128:            "test": "Decode a discriminating KERN_PROC_ALL payload with microsecond starts and parent links; assert no /bin/ps call occurs and malformed, duplicate, or cyclic rows refuse. In the same structural suite, assert every lease owner and registry identity is exactly present in custody_roots, roots cannot shrink while a lease is retained, and any future identity-bearing state addition requires an explicit schema-version/root rule."
docs/process_traces/2026-08-06-qg-census-consult/SYNTHESIS.md:28:3. **KERN_PROC_ALL single-snapshot inventory** (PID/ppid/microsecond
docs/process_traces/RESUME-2026-07-28.md:53:floors are **3.823787 J prefill / 3.592138 J decode**, INCLUDING the 0.652272 J
docs/process_traces/2026-07-17-extension-axes/roadmap-synthesis.md:15:| 5 | [C5-2.12](/Users/edr/code/JouleWise/docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:49) | PF | Runnable marginal-slope test. |
docs/process_traces/RESUME-2026-07-26.md:69:| decode | **2.939866 J** | 0.493448 J | labelled `attribution_limited`, extractable |
docs/process_traces/RESUME-2026-07-26.md:130:Expected a10 floors once labelling lands: **prefill ≈ 3.17 J, decode ≈ 2.94 J,
docs/process_traces/RESUME-2026-07-26.md:150:| `FLOOR-COMMONMODE-01` | common-mode ABBA anchor estimator | **best available lever**: ~3× on comparative floors (a5 decode 6.46 → 2.13 J), pure desk work on existing data, no re-collection |
docs/process_traces/2026-08-03-d111-backfill/testspeed/testspeed-impl-report.md:239:- Shard 2 — 171.365s: `test_2k_amplification`, `test_aggregate`, `test_audit_bundle_validation`, `test_audit_cli_examples`, `test_audit_powermetrics_parser`, `test_audit_report`, `test_axi_burst_reduce`, `test_axi_mock_spec`, `test_axi_output_identity`, `test_axi_schemas`, `test_bundle_read`, `test_claims_index_lint`, `test_doctor`, `test_env_locks`, `test_gen_state`, `test_generate_matrix`, `test_idle_dependence`, `test_interfaces`, `test_microdelta_generate_configs`, `test_mint_floor_artifact`, `test_mlx_runtime`, `test_mock_adapters`, `test_p2038_production_path`, `test_pack_capsule`, `test_package_bundle_pack`, `test_rpt002_related_work`, `test_shard_tests`, `test_uncertainty_evidence`
docs/process_traces/RESUME-2026-07-27.md:51:| a9, a10 | earlier corpora | **PASSED**, consumable; a10 yields prefill ≈3.17 J / decode ≈2.94 J once FLOOR-LABEL-01 merges |
docs/process_traces/RESUME-2026-07-27.md:53:| **C** (`05_phase_decode_abba`) | 2 aborted attempts | both quarantined intact in `~/JouleWise-window-custody/window_c_20260726/quarantine/`; runs roots cleared; **re-run tonight** |
docs/process_traces/2026-08-03-d111-backfill/adjudication_packet_20260801/COLD-GATE-PACKET-dangling-terminal-semantic.md:58:   planned members). Window A's C1 linearity 40/40 stays non-claim-
docs/process_traces/2026-08-03-d111-backfill/adjudication_packet_20260801/close-out-windowA.md:5:  campaigns: linearity_ramp -> claim C1, additivity_shapes -> C4,
docs/process_traces/2026-08-03-d111-backfill/adjudication_packet_20260801/close-out-windowA.md:32:  3/3; **linearity_ramp 40/40 COMPLETE** (claim C1's campaign);
docs/process_traces/2026-08-03-d111-backfill/adjudication_packet_20260801/close-out-windowA.md:97:  Collection facts unchanged: linearity 40/40 (C1's campaign) and

exec
/bin/zsh -lc "find configs/campaigns/metrology_v1 -maxdepth 2 -type f -name 'README.md' -print 2>/dev/null
rg -n \"Members|members|rung|128|2048|hold|duration|window|Total|total|shape|k=\" configs/campaigns/metrology_v1 -g 'README.md' -g '*.json' | head -220" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
configs/campaigns/metrology_v1/null_ladder/README.md
configs/campaigns/metrology_v1/linearity_ramp/README.md
configs/campaigns/metrology_v1/micro_delta/README.md
configs/campaigns/metrology_v1/additivity_shapes/README.md
configs/campaigns/metrology_v1/long_holds/README.md
configs/campaigns/metrology_v1/README.md
configs/campaigns/metrology_v1/README.md:6:members here use the frozen Qwen2.5-1.5B MLX stack and the existing window
configs/campaigns/metrology_v1/README.md:10:measurement. `micro_delta/k0064` is only a DRAFT-PENDING-SLOPE placeholder.
configs/campaigns/metrology_v1/README.md:20:| `additivity_shapes` | `runs/metrology_v1/additivity_shapes` | `runs/metrology_v1/additivity_shapes/campaign_log.jsonl` |
configs/campaigns/metrology_v1/README.md:22:| `long_holds` | `runs/metrology_v1/long_holds` | `runs/metrology_v1/long_holds/campaign_log.jsonl` |
configs/campaigns/metrology_v1/README.md:29:The governed 3+1+3 window references and 12-member NEG-8 in-window bound corpus
configs/campaigns/metrology_v1/README.md:30:are supplied by `configs/campaigns/window_references/` and
configs/campaigns/metrology_v1/README.md:36:- Metrology window A (~2.8 h): `linearity_ramp` + `additivity_shapes` +
configs/campaigns/metrology_v1/README.md:37:  `null_ladder` stage `02_null_o0512` + long-holds Part A =
configs/campaigns/metrology_v1/README.md:38:  3727+2257+1842+319 = 8145 s = 2.26 h science, plus 3+1+3 window references
configs/campaigns/metrology_v1/README.md:39:  (~11 min) and the 12-member NEG-8 in-window bound corpus (~19 min) =
configs/campaigns/metrology_v1/README.md:40:  ~2.76 h. FITS one ~3 h window.
configs/campaigns/metrology_v1/README.md:41:- Metrology window B (~3.1 h, TIGHT): `null_ladder` stages 01 + 03
configs/campaigns/metrology_v1/README.md:44:  to window C.
configs/campaigns/metrology_v1/README.md:45:- Window C: long-holds Part B (25 min incl. the extended-idle members) + the
configs/campaigns/metrology_v1/README.md:59:  of the single-family 7B shape and needs ratification before consumption by a
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:3:  "plan_id": "metrology-v1-long-holds-m3max",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:4:  "calibration_scope": "production_window",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:20:        "mt-q15-decode-p0128-o4096": 30.0,
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:21:        "mt-q15-decode-p0128-o0128-idle0120": 120.0,
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:22:        "mt-q15-decode-p0128-o0128-idle0300": 300.0,
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:23:        "mt-q15-decode-p0128-o0128-idle0600": 600.0
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:28:        "condition_family_id": "mt-q15-decode-p0128-o0128-idle0120",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:32:        "condition_family_id": "mt-q15-decode-p0128-o0128-idle0300",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:36:        "condition_family_id": "mt-q15-decode-p0128-o0128-idle0600",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:40:        "condition_family_id": "mt-q15-decode-p0128-o4096",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:52:      "cell_id": "metrology-long-hold-decode-o4096",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:57:      "window_class": "phase",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:61:      "condition_family_id": "mt-q15-decode-p0128-o4096",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:64:        "mthold-o4096-r01",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:65:        "mthold-o4096-r02",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:66:        "mthold-o4096-r03"
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:75:      "window_class": "phase",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:79:      "condition_family_id": "mt-q15-decode-p0128-o0128-idle0120",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:91:      "window_class": "phase",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:95:      "condition_family_id": "mt-q15-decode-p0128-o0128-idle0300",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:107:      "window_class": "phase",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:111:      "condition_family_id": "mt-q15-decode-p0128-o0128-idle0600",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:119:    "production_metrology_window": {
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:122:        "01_holds",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:129:    "window_references": {
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:130:      "source": "configs/campaigns/window_references/",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:136:      "integration": "supplied_by_window_chain_not_science_stage"
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:138:    "in_window_bound_corpus": {
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:145:      "integration": "supplied_by_window_chain_not_science_stage"
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:148:  "runs_dir": "runs/metrology_v1/long_holds",
configs/campaigns/metrology_v1/long_holds/calibration_plan.json:150:  "campaign_log": "runs/metrology_v1/long_holds/campaign_log.jsonl",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:3:  "manifest_id": "metrology-v1-long-holds-order-v1",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:4:  "plan_id": "metrology-v1-long-holds-m3max",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:10:      "subcampaign_id": "01_holds",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:11:      "role": "sustained_decode_holds",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:28:      "config": "01_holds/mthold-o4096-r01.json",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:29:      "run_id": "mthold-o4096-r01",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:32:      "workload": "mt-q15-decode-p0128-o4096",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:40:      "config": "01_holds/mthold-o4096-r02.json",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:41:      "run_id": "mthold-o4096-r02",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:44:      "workload": "mt-q15-decode-p0128-o4096",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:52:      "config": "01_holds/mthold-o4096-r03.json",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:53:      "run_id": "mthold-o4096-r03",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:56:      "workload": "mt-q15-decode-p0128-o4096",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:68:      "workload": "mt-q15-decode-p0128-o0128-idle0120",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:80:      "workload": "mt-q15-decode-p0128-o0128-idle0300",
configs/campaigns/metrology_v1/long_holds/order_manifest.json:92:      "workload": "mt-q15-decode-p0128-o0128-idle0600",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0120-r01.json:10:    "context_window": 32768
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0120-r01.json:28:    "prompt_tokens": 128,
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0120-r01.json:29:    "output_tokens": 128
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0120-r01.json:45:      "long-holds",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0120-r01.json:46:      "production-window",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0120-r01.json:48:      "df-condition=mt-q15-decode-p0128-o0128-idle0120",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/order_manifest.json:3:  "manifest_id": "metrology-v1-long-holds-02_idle_extended-order-v1",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/order_manifest.json:4:  "plan_id": "metrology-v1-long-holds-m3max",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/order_manifest.json:15:      "workload": "mt-q15-decode-p0128-o0128-idle0120",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/order_manifest.json:27:      "workload": "mt-q15-decode-p0128-o0128-idle0300",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/order_manifest.json:39:      "workload": "mt-q15-decode-p0128-o0128-idle0600",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0300-r01.json:10:    "context_window": 32768
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0300-r01.json:28:    "prompt_tokens": 128,
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0300-r01.json:29:    "output_tokens": 128
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0300-r01.json:45:      "long-holds",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0300-r01.json:46:      "production-window",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0300-r01.json:48:      "df-condition=mt-q15-decode-p0128-o0128-idle0300",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0600-r01.json:10:    "context_window": 32768
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0600-r01.json:28:    "prompt_tokens": 128,
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0600-r01.json:29:    "output_tokens": 128
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0600-r01.json:45:      "long-holds",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0600-r01.json:46:      "production-window",
configs/campaigns/metrology_v1/long_holds/02_idle_extended/mtidle-i0600-r01.json:48:      "df-condition=mt-q15-decode-p0128-o0128-idle0600",
configs/campaigns/metrology_v1/long_holds/README.md:1:# Metrology v1: long holds
configs/campaigns/metrology_v1/long_holds/README.md:10:Part A contains three 4096-output-token sustained decode members. Part B
configs/campaigns/metrology_v1/long_holds/README.md:11:contains one 128-output-token member at each of 120, 300, and 600 idle seconds.
configs/campaigns/metrology_v1/long_holds/README.md:19:(`configs/campaigns/neg8_reference_corpus/`) are NOT idle members — they run
configs/campaigns/metrology_v1/long_holds/README.md:22:`joulewise/schemas.py:1170`). Therefore Part B = 3 members with output_tokens
configs/campaigns/metrology_v1/long_holds/README.md:23:128, prompt_tokens 128, and `sampling.idle_seconds` ∈ {120.0, 300.0, 600.0}.
configs/campaigns/metrology_v1/long_holds/README.md:29:The exact evidence root is `runs/metrology_v1/long_holds`; the exact log is
configs/campaigns/metrology_v1/long_holds/README.md:30:`runs/metrology_v1/long_holds/campaign_log.jsonl`.
configs/campaigns/metrology_v1/long_holds/README.md:33:.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/long_holds/01_holds \
configs/campaigns/metrology_v1/long_holds/README.md:34:  --runs-dir runs/metrology_v1/long_holds \
configs/campaigns/metrology_v1/long_holds/README.md:35:  --log runs/metrology_v1/long_holds/campaign_log.jsonl \
configs/campaigns/metrology_v1/long_holds/README.md:37:.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/long_holds/02_idle_extended \
configs/campaigns/metrology_v1/long_holds/README.md:38:  --runs-dir runs/metrology_v1/long_holds \
configs/campaigns/metrology_v1/long_holds/README.md:39:  --log runs/metrology_v1/long_holds/campaign_log.jsonl \
configs/campaigns/metrology_v1/long_holds/README.md:50:| `mt-q15-decode-p0128-o4096` | 128/4096 | `phase_energy_j.decode` | `b3ded631d0be157a5ff8d7d53f71bb7f06ebe35ebef345787dfbefe7fbba5154` |
configs/campaigns/metrology_v1/long_holds/README.md:51:| `mt-q15-decode-p0128-o0128-idle0120` | 128/128, idle 120 s | `phase_energy_j.decode` | `e2e3670670547c0f6ddf7857ab612cd897bd10e0214ed6d79f1d185250795a17` |
configs/campaigns/metrology_v1/long_holds/README.md:52:| `mt-q15-decode-p0128-o0128-idle0300` | 128/128, idle 300 s | `phase_energy_j.decode` | `5f05f3b5d0060dc9f054e5219e47eec1b9a6c9f36a65b9a44420365a2c5890b8` |
configs/campaigns/metrology_v1/long_holds/README.md:53:| `mt-q15-decode-p0128-o0128-idle0600` | 128/128, idle 600 s | `phase_energy_j.decode` | `5a22f0e9a356eb0a84d3e5debb0c2659a0f3cccf47c75b41d06e37ab4d42f431` |
configs/campaigns/metrology_v1/long_holds/README.md:60:1201.5 s = 20.0 min. Total 1520 s = 25.3 min, 6 members. Basis: the
configs/campaigns/metrology_v1/long_holds/README.md:70:  `mt-q15-decode-p0128-o0128-idleSSSS` family ID. The plan describes variable
configs/campaigns/metrology_v1/long_holds/README.md:74:  idle-duration family has exactly one planned observation; these are
configs/campaigns/metrology_v1/long_holds/01_holds/order_manifest.json:3:  "manifest_id": "metrology-v1-long-holds-01_holds-order-v1",
configs/campaigns/metrology_v1/long_holds/01_holds/order_manifest.json:4:  "plan_id": "metrology-v1-long-holds-m3max",
configs/campaigns/metrology_v1/long_holds/01_holds/order_manifest.json:11:      "config": "mthold-o4096-r01.json",
configs/campaigns/metrology_v1/long_holds/01_holds/order_manifest.json:12:      "run_id": "mthold-o4096-r01",
configs/campaigns/metrology_v1/long_holds/01_holds/order_manifest.json:15:      "workload": "mt-q15-decode-p0128-o4096",
configs/campaigns/metrology_v1/long_holds/01_holds/order_manifest.json:23:      "config": "mthold-o4096-r02.json",
configs/campaigns/metrology_v1/long_holds/01_holds/order_manifest.json:24:      "run_id": "mthold-o4096-r02",
configs/campaigns/metrology_v1/long_holds/01_holds/order_manifest.json:27:      "workload": "mt-q15-decode-p0128-o4096",
configs/campaigns/metrology_v1/long_holds/01_holds/order_manifest.json:35:      "config": "mthold-o4096-r03.json",
configs/campaigns/metrology_v1/long_holds/01_holds/order_manifest.json:36:      "run_id": "mthold-o4096-r03",
configs/campaigns/metrology_v1/long_holds/01_holds/order_manifest.json:39:      "workload": "mt-q15-decode-p0128-o4096",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r01.json:3:  "run_id": "mthold-o4096-r01",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r01.json:10:    "context_window": 32768
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r01.json:28:    "prompt_tokens": 128,
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r01.json:45:      "long-holds",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r01.json:46:      "production-window",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r01.json:48:      "df-condition=mt-q15-decode-p0128-o4096",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r01.json:51:      "sustained-decode-hold"
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r03.json:3:  "run_id": "mthold-o4096-r03",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r03.json:10:    "context_window": 32768
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r03.json:28:    "prompt_tokens": 128,
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r03.json:45:      "long-holds",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r03.json:46:      "production-window",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r03.json:48:      "df-condition=mt-q15-decode-p0128-o4096",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r03.json:51:      "sustained-decode-hold"
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r02.json:3:  "run_id": "mthold-o4096-r02",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r02.json:10:    "context_window": 32768
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r02.json:28:    "prompt_tokens": 128,
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r02.json:45:      "long-holds",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r02.json:46:      "production-window",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r02.json:48:      "df-condition=mt-q15-decode-p0128-o4096",
configs/campaigns/metrology_v1/long_holds/01_holds/mthold-o4096-r02.json:51:      "sustained-decode-hold"
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o0128_idle0300.json:3:  "condition_family_id": "mt-q15-decode-p0128-o0128-idle0300",
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o0128_idle0300.json:8:    "prompt_tokens": 128,
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o0128_idle0300.json:9:    "output_tokens": 128
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o0128_idle0300.json:13:    "window_class": "phase"
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o0128_idle0120.json:3:  "condition_family_id": "mt-q15-decode-p0128-o0128-idle0120",
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o0128_idle0120.json:8:    "prompt_tokens": 128,
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o0128_idle0120.json:9:    "output_tokens": 128
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o0128_idle0120.json:13:    "window_class": "phase"
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o4096.json:3:  "condition_family_id": "mt-q15-decode-p0128-o4096",
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o4096.json:8:    "prompt_tokens": 128,
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o4096.json:13:    "window_class": "phase"
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o0128_idle0600.json:3:  "condition_family_id": "mt-q15-decode-p0128-o0128-idle0600",
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o0128_idle0600.json:8:    "prompt_tokens": 128,
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o0128_idle0600.json:9:    "output_tokens": 128
configs/campaigns/metrology_v1/long_holds/condition_families/condition_family_mt_q15_decode_p0128_o0128_idle0600.json:13:    "window_class": "phase"
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:24:      "workload": "mt-q15-decode-p0128-o0512",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:35:      "workload": "mt-q15-decode-p0128-o0576",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:46:      "workload": "mt-q15-decode-p0128-o0576",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:57:      "workload": "mt-q15-decode-p0128-o0512",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:68:      "workload": "mt-q15-decode-p0128-o0512",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:79:      "workload": "mt-q15-decode-p0128-o0576",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:90:      "workload": "mt-q15-decode-p0128-o0576",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:101:      "workload": "mt-q15-decode-p0128-o0512",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:112:      "workload": "mt-q15-decode-p0128-o0512",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:123:      "workload": "mt-q15-decode-p0128-o0576",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:134:      "workload": "mt-q15-decode-p0128-o0576",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:145:      "workload": "mt-q15-decode-p0128-o0512",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:156:      "workload": "mt-q15-decode-p0128-o0512",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:167:      "workload": "mt-q15-decode-p0128-o0576",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:178:      "workload": "mt-q15-decode-p0128-o0576",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:189:      "workload": "mt-q15-decode-p0128-o0512",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:200:      "workload": "mt-q15-decode-p0128-o0512",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:211:      "workload": "mt-q15-decode-p0128-o0576",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:222:      "workload": "mt-q15-decode-p0128-o0576",
configs/campaigns/metrology_v1/micro_delta/order_manifest.json:233:      "workload": "mt-q15-decode-p0128-o0512",
configs/campaigns/metrology_v1/null_ladder/README.md:19:.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/null_ladder/01_null_o0128 \
configs/campaigns/metrology_v1/null_ladder/README.md:27:.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/null_ladder/03_null_o2048 \
configs/campaigns/metrology_v1/null_ladder/README.md:40:| `mt-q15-decode-p0128-o0128` | 128/128 | `phase_energy_j.decode` | `eec17ac336e270e556158638d8c720b669412f9bbffa453ebbe5d5d4a1110d62` |
configs/campaigns/metrology_v1/null_ladder/README.md:41:| `mt-q15-decode-p0128-o0512` | 128/512 | `phase_energy_j.decode` | `6974fbf58bcce32b757631fb8536750788a13d371731354d8873abbfc23fd54d` |
configs/campaigns/metrology_v1/null_ladder/README.md:42:| `mt-q15-decode-p0128-o2048` | 128/2048 | `phase_energy_j.decode` | `a5b3b5682e21aa71052cd7e5d899f4d7635c36531a2912822532f1c4fffd65ad` |
configs/campaigns/metrology_v1/null_ladder/README.md:46:Per-member wall = 90 s fixed overhead + output_tokens × 0.004004 s. o128:
configs/campaigns/metrology_v1/null_ladder/README.md:47:20×90.5=1810 s; o512: 20×92.1=1842 s; o2048: 20×98.2=1964 s;
configs/campaigns/metrology_v1/null_ladder/README.md:48:total 5616 s = 93.6 min, 60 members. Basis: the 2026-07-29 timing probe; the
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:3:  "plan_id": "metrology-v1-additivity-shapes-m3max",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:4:  "calibration_scope": "production_window",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:23:        "condition_family_id": "mt-q15-decode-p0128-o2048",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:24:        "condition_family_sha256": "a5b3b5682e21aa71052cd7e5d899f4d7635c36531a2912822532f1c4fffd65ad"
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:31:        "condition_family_id": "mt-q15-decode-p2048-o0128",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:35:        "condition_family_id": "mt-q15-prefill-p0128-o2048",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:43:        "condition_family_id": "mt-q15-prefill-p2048-o0128",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:47:        "condition_family_id": "mt-q15-request-p0128-o2048",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:55:        "condition_family_id": "mt-q15-request-p2048-o0128",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:67:      "cell_id": "metrology-additivity-decode-p2048-o0128",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:72:      "window_class": "phase",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:76:      "condition_family_id": "mt-q15-decode-p2048-o0128",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:79:        "mtadd-p2048o0128-r01",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:80:        "mtadd-p2048o0128-r02",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:81:        "mtadd-p2048o0128-r03",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:82:        "mtadd-p2048o0128-r04",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:83:        "mtadd-p2048o0128-r05",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:84:        "mtadd-p2048o0128-r06",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:85:        "mtadd-p2048o0128-r07",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:86:        "mtadd-p2048o0128-r08"
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:90:      "cell_id": "metrology-additivity-prefill-p2048-o0128",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:95:      "window_class": "phase",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:99:      "condition_family_id": "mt-q15-prefill-p2048-o0128",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:102:        "mtadd-p2048o0128-r01",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:103:        "mtadd-p2048o0128-r02",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:104:        "mtadd-p2048o0128-r03",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:105:        "mtadd-p2048o0128-r04",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:106:        "mtadd-p2048o0128-r05",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:107:        "mtadd-p2048o0128-r06",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:108:        "mtadd-p2048o0128-r07",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:109:        "mtadd-p2048o0128-r08"
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:113:      "cell_id": "metrology-additivity-request-p2048-o0128",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:118:      "window_class": "request",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:122:      "condition_family_id": "mt-q15-request-p2048-o0128",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:125:        "mtadd-p2048o0128-r01",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:126:        "mtadd-p2048o0128-r02",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:127:        "mtadd-p2048o0128-r03",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:128:        "mtadd-p2048o0128-r04",
configs/campaigns/metrology_v1/additivity_shapes/calibration_plan.json:129:        "mtadd-p2048o0128-r05",

exec
/bin/zsh -lc "sed -n '1,90p' configs/campaigns/metrology_v1/README.md
sed -n '1,100p' configs/campaigns/metrology_v1/linearity_ramp/README.md
sed -n '1,100p' configs/campaigns/metrology_v1/micro_delta/README.md
sed -n '1,90p' configs/campaigns/metrology_v1/additivity_shapes/README.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Metrology v1 campaign suite

This suite characterizes the measurement instrument for paper claims C1-C5. It
does not gate a scientific claim, introduce a model, or mint a detection floor.
The program reuses its two already-characterized stacks; the runnable metrology
members here use the frozen Qwen2.5-1.5B MLX stack and the existing window
reference/bound corpus uses that same reference stack.

The five draft plans are deterministic and must be magistrate-ratified before
measurement. `micro_delta/k0064` is only a DRAFT-PENDING-SLOPE placeholder.

## Evidence roots

Each campaign writes beneath its exact `--runs-dir` root:

| Campaign | Evidence root | Campaign log |
| --- | --- | --- |
| `linearity_ramp` | `runs/metrology_v1/linearity_ramp` | `runs/metrology_v1/linearity_ramp/campaign_log.jsonl` |
| `null_ladder` | `runs/metrology_v1/null_ladder` | `runs/metrology_v1/null_ladder/campaign_log.jsonl` |
| `additivity_shapes` | `runs/metrology_v1/additivity_shapes` | `runs/metrology_v1/additivity_shapes/campaign_log.jsonl` |
| `micro_delta` | `runs/metrology_v1/micro_delta` | `runs/metrology_v1/micro_delta/campaign_log.jsonl` |
| `long_holds` | `runs/metrology_v1/long_holds` | `runs/metrology_v1/long_holds/campaign_log.jsonl` |

The campaign READMEs give the exact command for every stage. Governed
extraction invocations must pass an ABSOLUTE `--runs-dir` and an explicit
`--evaluation-basis-sha256`; these are tool-contract requirements, not
optional conveniences.

The governed 3+1+3 window references and 12-member NEG-8 in-window bound corpus
are supplied by `configs/campaigns/window_references/` and
`configs/campaigns/neg8_reference_corpus/`. They are not science stages in
these campaign directories.

## Window packing

- Metrology window A (~2.8 h): `linearity_ramp` + `additivity_shapes` +
  `null_ladder` stage `02_null_o0512` + long-holds Part A =
  3727+2257+1842+319 = 8145 s = 2.26 h science, plus 3+1+3 window references
  (~11 min) and the 12-member NEG-8 in-window bound corpus (~19 min) =
  ~2.76 h. FITS one ~3 h window.
- Metrology window B (~3.1 h, TIGHT): `null_ladder` stages 01 + 03
  (1810+1964 = 3774 s) + `micro_delta` three k slots (~5535 s) = 9309 s =
  2.59 h + references/corpus 30 min = ~3.09 h. RECOMMEND moving one k slot
  to window C.
- Window C: long-holds Part B (25 min incl. the extended-idle members) + the
  third `micro_delta` k slot + stability repeat + spillover.

## OPEN QUESTIONS FOR RATIFICATION

- All characterization cells use `use_role: staleness_sentinel`, the spec's
  first-choice non-claim vocabulary. The calibration-plan document has no
  active schema validator for this literal, so ratification must confirm it.
- Non-micro plans use `freeze_status:
  draft_pending_magistrate_ratification`; `micro_delta` uses
  `draft_pending_slope`. These are deliberate draft literals, not frozen-plan
  claims.
- Cell kinds and modular family IDs follow the campaign READMEs. The plan-level
  multi-family `stack_scope.condition_families` list is a descriptive extension
  of the single-family 7B shape and needs ratification before consumption by a
  future plan validator.
# Metrology v1: linearity ramp

This campaign feeds paper claim C1 by measuring instrument-response linearity
and fitting the per-token decode slope that becomes C3's energy standard.

These campaigns measure the INSTRUMENT, not a gated scientific claim. They
therefore need no new model stacks and no new detection floors. They reuse the
two already-characterized stacks; this member set uses the frozen 1.5B stack.

Eight fixed, auditable, counterbalanced replicate-blocks cover five output
levels for 40 members. The generator asserts one occurrence of every level per
block and a mean level position within ±0.5 of 3.0.

## Evidence root and execution

The exact evidence root is `runs/metrology_v1/linearity_ramp`; the exact log is
`runs/metrology_v1/linearity_ramp/campaign_log.jsonl`.

```sh
.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/linearity_ramp/01_ramp \
  --runs-dir runs/metrology_v1/linearity_ramp \
  --log runs/metrology_v1/linearity_ramp/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
```

Extraction invocations must pass an ABSOLUTE `--runs-dir` and
`--evaluation-basis-sha256`.

## Condition families

| ID | Prompt/output | Metric | Canonical SHA-256 |
| --- | --- | --- | --- |
| `mt-q15-decode-p0128-o0128` | 128/128 | `phase_energy_j.decode` | `eec17ac336e270e556158638d8c720b669412f9bbffa453ebbe5d5d4a1110d62` |
| `mt-q15-decode-p0128-o0256` | 128/256 | `phase_energy_j.decode` | `f1590ef7099780219aba4578dbf56cb963269c87f5ebc2bde28b5b05452d8ae3` |
| `mt-q15-decode-p0128-o0512` | 128/512 | `phase_energy_j.decode` | `6974fbf58bcce32b757631fb8536750788a13d371731354d8873abbfc23fd54d` |
| `mt-q15-decode-p0128-o1024` | 128/1024 | `phase_energy_j.decode` | `d57bfcd616d61e7a30f1fc9c08d9006c6f9457df45671952d4f53d2313f42abb` |
| `mt-q15-decode-p0128-o2048` | 128/2048 | `phase_energy_j.decode` | `a5b3b5682e21aa71052cd7e5d899f4d7635c36531a2912822532f1c4fffd65ad` |

## Duration arithmetic

Per-member wall = 90 s fixed overhead + output_tokens × 0.004004 s. The supplied
values are o128 90.5 s, o256 91.0 s, o512 92.1 s, o1024 94.1 s, and o2048
98.2 s. Total: 8 × (90.5+91.0+92.1+94.1+98.2) = 8 × 465.9 = 3727 s =
62.1 min, 40 members. Basis: the 2026-07-29 timing probe; the four-token warmup
is absorbed in overhead.

## OPEN QUESTIONS FOR RATIFICATION

- `use_role: staleness_sentinel`, `freeze_status:
  draft_pending_magistrate_ratification`, and `kind: absolute` are the selected
  plan literals; the plan vocabulary is not runner-validated.
- Family IDs use the ratified `mt-q15-decode-p0128-oOOOO` template. The
  `mt-q15-decode-p0128-o2048` definition is byte-identical to additivity's
  shared decode-heavy family.
# Metrology v1: micro delta

**DRAFT-PENDING-SLOPE: `k0064` is a placeholder only. Do not measure it until
the linearity slope fixes and the magistrate ratifies all k slots.**

This campaign feeds paper claim C3 by walking a known decode-energy effect
across the detection floor in both directions.

These campaigns measure the INSTRUMENT, not a gated scientific claim. They
therefore need no new model stacks and no new detection floors. They reuse the
two already-characterized stacks; both A and B here use the identical frozen
1.5B stack and differ only in output length.

The generator accepts repeatable `--k` arguments. With no arguments it emits
only the 20-member `k0064` placeholder: five fixed A/B/B/A blocks with A=512
and B=576 output tokens.

## Evidence root and execution

The exact evidence root is `runs/metrology_v1/micro_delta`; the exact log is
`runs/metrology_v1/micro_delta/campaign_log.jsonl`.

```sh
.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/micro_delta/k0064 \
  --runs-dir runs/metrology_v1/micro_delta \
  --log runs/metrology_v1/micro_delta/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
```

Extraction invocations must pass an ABSOLUTE `--runs-dir` and
`--evaluation-basis-sha256`.

## Condition families

| ID | Prompt/output | Metric | Canonical SHA-256 |
| --- | --- | --- | --- |
| `mt-q15-decode-p0128-o0512` | 128/512 (A) | `phase_energy_j.decode` | `6974fbf58bcce32b757631fb8536750788a13d371731354d8873abbfc23fd54d` |
| `mt-q15-decode-p0128-o0576` | 128/576 (B, k=64) | `phase_energy_j.decode` | `cdcf30d0c40a64638aa4d18eb9fca72b96fdeb1a41fbd50008966d90129ebc91` |

## Duration arithmetic

Per-member wall = 90 s fixed overhead + output_tokens × 0.004004 s. For k=64:
5 × (2×92.1 + 2×92.35) = 5 × 368.9 = 1845 s = 30.7 min,
20 members. Three k slots ≈ 92 min, 60 members; only k=64 is generated now.
Basis: the 2026-07-29 timing probe; the four-token warmup is absorbed in
overhead.

## OPEN QUESTIONS FOR RATIFICATION

- `use_role: staleness_sentinel`, `freeze_status: draft_pending_slope`,
  `kind: comparative_contrast`, `null_alias: false`, and
  `difference_orientation: condition_b_minus_condition_a` are the selected
  plan literals; the plan vocabulary is not runner-validated.
- The condition-family validator accepts only
  `comparison_policy: same_condition_repeat_and_null_abba_alias` with
  `abba_alias_relation: A_equals_B`. Those literals are therefore used for the
  A≠B contrast families as the spec-directed fallback, even though the plan
  correctly declares a non-null contrast.
- The plan's two arms use per-k `condition_families` and `output_tokens_by_k`
  fields so repeatable `--k` generation stays descriptive. Ratification should
  confirm those plan-only field names before a plan validator is introduced.
- Family IDs follow `mt-q15-decode-p0128-oOOOO`; the k-derived B family changes
  with each final slot. The placeholder remains DRAFT-PENDING-SLOPE until the
  fitted slope targets 0.5× / 1× / 1.5× / 3× the published floor.
# Metrology v1: additivity shapes

This campaign feeds paper claim C4 by testing phase-to-whole conservation and
the causal invariance of prefill energy with respect to output length.

These campaigns measure the INSTRUMENT, not a gated scientific claim. They
therefore need no new model stacks and no new detection floors. They reuse the
two already-characterized stacks; this member set uses the frozen 1.5B stack.

There are 24 members, not 72. Each shape member records prefill-phase energy,
decode-phase energy, and whole-request energy; the plan has three cells per
shape pointing to the same ordered bundle IDs.

## Evidence root and execution

The exact evidence root is `runs/metrology_v1/additivity_shapes`; the exact log
is `runs/metrology_v1/additivity_shapes/campaign_log.jsonl`.

```sh
.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/additivity_shapes/01_shapes \
  --runs-dir runs/metrology_v1/additivity_shapes \
  --log runs/metrology_v1/additivity_shapes/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
```

Extraction invocations must pass an ABSOLUTE `--runs-dir` and
`--evaluation-basis-sha256`.

## Condition families

| ID | Prompt/output | Metric | Canonical SHA-256 |
| --- | --- | --- | --- |
| `mt-q15-decode-p2048-o0128` | 2048/128 | `phase_energy_j.decode` | `61e5b2244686edcb67808fb4b67ebb664374d6c6c093ab5bbde3c078c52c6f6a` |
| `mt-q15-prefill-p2048-o0128` | 2048/128 | `phase_energy_j.prefill` | `0617f1072282ce443fd8ad7cd151b5644a214ed514728dd4428af88d5e1bd4fe` |
| `mt-q15-request-p2048-o0128` | 2048/128 | `energy_request_j` | `90c8d4c0ac2e84ec46a253e3b5896262c18a0a2b649eaef0f418123ecf459e44` |
| `mt-q15-decode-p0512-o0512` | 512/512 | `phase_energy_j.decode` | `c6818da04094e6ffe87c8c5462c3300bc0bae58050df02d834385ed047e0e9cf` |
| `mt-q15-prefill-p0512-o0512` | 512/512 | `phase_energy_j.prefill` | `9a77ea91d9eb2ac02a2f388d720df03036b0446824b362a30aa36ea59102c45e` |
| `mt-q15-request-p0512-o0512` | 512/512 | `energy_request_j` | `6aed2b73c4d3a8dbb5d96a42e6f446a090d69eca2b83ae8a5405f353b3ee2fe6` |
| `mt-q15-decode-p0128-o2048` | 128/2048 | `phase_energy_j.decode` | `a5b3b5682e21aa71052cd7e5d899f4d7635c36531a2912822532f1c4fffd65ad` |
| `mt-q15-prefill-p0128-o2048` | 128/2048 | `phase_energy_j.prefill` | `b7fb463adf73f972923bd65fccde1d17d0ec1d53560ae389914fe74698d58468` |
| `mt-q15-request-p0128-o2048` | 128/2048 | `energy_request_j` | `c8c0ed2de6e078078e4584b2e5223459745cd9a808580e4796b7f663d75cc5dc` |

## Duration arithmetic

Per-member wall = 90 s fixed overhead + output_tokens × 0.004004 s.
8 × (91.5 + 92.4 + 98.2) = 8 × 282.1 = 2257 s = 37.6 min,
24 members. The 91.5 and 92.4 figures include a ≤1 s prefill allowance for
the 2048- and 512-token prompts. Prefill time is not in the 2026-07-29 timing
probe and remains unmeasured; the four-token warmup is absorbed in overhead.

## OPEN QUESTIONS FOR RATIFICATION

- `use_role: staleness_sentinel`, `freeze_status:
  draft_pending_magistrate_ratification`, and nine `kind: absolute` cells are
  the selected plan literals; the plan vocabulary is not runner-validated.
- The spec says the workload name is an exception for additivity but supplies
  no replacement literal. `df_ph_decode` is retained because the shared
  `mt-q15-decode-p0128-o2048` family must be byte-identical to linearity's
  definition. Ratification should confirm that modularity-directed fallback.
- Each member carries all three metric-specific `df-condition=` tags, and each
  manifest entry names the request family as its primary `workload` while also
  listing all three `condition_family_ids`; a future manifest consumer should
  ratify that descriptive vocabulary.

exec
/bin/zsh -lc "find configs -iname '*q4*' -o -iname '*shape_grid*' | head -80
rg -n \"q4_l3_shape_grid|prompt.level|decode.level|8192|holdout\" docs/contracts/analysis_plans.md docs/process/state_kernel.json docs/run_reports/2026-07-08-suite-science-expansion.md | head -140" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
docs/run_reports/2026-07-08-suite-science-expansion.md:21:  - Program v2 (D-039): `q4_l3_shape_grid_v1` (4x3 + interpolation/
docs/run_reports/2026-07-08-suite-science-expansion.md:22:    extrapolation holdouts — the only current path to L3), P2-015 expanded
docs/contracts/analysis_plans.md:32:| Holdout cells (L3 only) | Named holdout cells and prediction-error rule for L3 plans; write `not applicable` for L2 plans. |
docs/contracts/analysis_plans.md:113:| selection_scope | Frozen target/model/profile 4x3 prompt `{128,512,2048,4096}` x decode `{64,256,512}` grid, its predeclared fixed/prompt/decode terms, and the named holdout cells. |
docs/contracts/analysis_plans.md:114:| multiplicity_rule | Holm within FAM-Q4-GRID-MODEL across confirmatory fixed/prompt/decode contrasts and holdout pass/fail claims; linear/log sensitivity terms are secondary unless frozen as primary before execution. |
docs/contracts/analysis_plans.md:117:| Estimator/formula | Primary fit is categorical-additive: `E = fixed + prompt_level + decode_level` on the 4x3 grid prompt `{128,512,2048,4096}` x decode `{64,256,512}`. Linear/log sensitivity is secondary. |
docs/contracts/analysis_plans.md:119:| Order/blocking/covariates | Interleaved or recorded manifest order; block/session and drift sentinel terms available as covariates; no curvature term promoted unless categorical residuals and holdouts clear the floor. |
docs/process/state_kernel.json:1985:          "8192 anchor cells on small+mid models"
docs/process/state_kernel.json:2026:      "goal": "q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6).",

exec
/bin/zsh -lc "sed -n '95,140p' docs/contracts/analysis_plans.md
sed -n '1,150p' docs/run_reports/2026-07-08-suite-science-expansion.md
sed -n '1965,2045p' docs/process/state_kernel.json" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
  runtime timestamp. If any burst lacks individual timestamps, that metric is
  null. The frozen `throughput_tokens_s` N-over-span convention is retained
  only for compatibility and explicitly labeled legacy wherever reported; it
  is not eligible to stand in for the governed inter-token metric.
  Request/burst bundles instead report the separately named decode-phase
  committed-output throughput, emission-event rate, and burst-size
  distribution defined by
  `docs/specs/axi/sa_burst_decode_contract.md`.

## Seeded plans

### AP-1: Q4 fixed+marginal grid fit

| Field | Value |
|---|---|
| Plan ID / RQ consumer | AP-1 / Q4 fixed-vs-marginal energy model; feeds Q5 rank rules and Phase 4 F9 (C-014). |
| family_id | FAM-Q4-GRID-MODEL |
| claim_role | primary |
| selection_scope | Frozen target/model/profile 4x3 prompt `{128,512,2048,4096}` x decode `{64,256,512}` grid, its predeclared fixed/prompt/decode terms, and the named holdout cells. |
| multiplicity_rule | Holm within FAM-Q4-GRID-MODEL across confirmatory fixed/prompt/decode contrasts and holdout pass/fail claims; linear/log sensitivity terms are secondary unless frozen as primary before execution. |
| Metric + exact window class | `gross_energy_j` (gross request window) and `energy_request_j` (idle-subtracted request window); phase terms may be reported gross-only and only when window samples clear the standing rule (C-014). |
| Unit of analysis + dependence structure | Bundle-level repetitions within target/model/profile cell; uncertainty is across bundles, blocked by model/session/window (C-014). |
| Estimator/formula | Primary fit is categorical-additive: `E = fixed + prompt_level + decode_level` on the 4x3 grid prompt `{128,512,2048,4096}` x decode `{64,256,512}`. Linear/log sensitivity is secondary. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid bundles only; D-014 quality flags excluded unless the report names and justifies a waiver; capped cells are excluded from prompt-slope/rank claims unless realized prompt lengths match. |
| Order/blocking/covariates | Interleaved or recorded manifest order; block/session and drift sentinel terms available as covariates; no curvature term promoted unless categorical residuals and holdouts clear the floor. |
| Floor gate | pending-P2-015: `max(floor_abs_j, floor_cmp_j)` for request windows and any reported phase window. |
| MDE/n sizing + predeclared top-up rule | n frozen at registry freeze (D-062): n=10 for near-floor cells/contrasts, n=5 elsewhere, sized from Window-A variance/MDE. Sizing/top-up governed by the D-062 clause in the shared field definition above (frozen n; outcome-dependent growth demotes to exploratory). |
| Denominator provenance requirement | Runtime-observed output tokens for per-token companion tables; request-energy fit does not use config-token denominators. |
| Holdout cells (L3 only) | `(512,256)` and `(4096,512)` held-out in-grid corner predictions (interaction/additivity validation — both factor levels occur in the training grid, so neither is statistical extrapolation); prediction errors must clear the AP-1 floor gate. No extrapolation claim is available from this grid. |
| Claim ceiling + exact forbidden upgrade | Ceiling L3. Forbidden upgrade: no curvature, universal scaling law, or architecture-wide conclusion from this grid. |
| Disqualifiers + not-resolvable conditions | Holdout miss, residual above floor, below-floor effects, unresolved rank gaps, or short-prefill <3 samples downgrade or report `not resolvable`. |
| Linked manifests/bundle hashes | pending post-execution. |

### AP-2: 2M prefill/decode power asymmetry

| Field | Value |
|---|---|
| Plan ID / RQ consumer | AP-2 / Slice 2M qualitative prefill/decode asymmetry; supports Q4 substrate only (C-014). |
| family_id | FAM-2M-SHAPE-CONTRASTS |
| claim_role | primary |
| selection_scope | Frozen four-profile 2M matrix: `short_short`, `long_short`, `short_long`, and canonical `mid_mid` within one target/model/profile campaign. |
| multiplicity_rule | Holm within FAM-2M-SHAPE-CONTRASTS across the predeclared request-energy and resolvable gross phase-window contrasts; unplanned metric or profile contrasts are exploratory. |
| Metric + exact window class | Gross request energy, idle-subtracted request energy, gross phase-window energy, mean power, TTFT, and runtime-observed output-token companion metrics. |
| Unit of analysis + dependence structure | Bundle-level repetitions within target/model/profile; session/block recorded for drift. |
| Estimator/formula | Descriptive pairwise contrasts among `short_short`, `long_short`, `short_long`, and canonical `mid_mid` profiles with contrast-level t-intervals from D-014. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid bundles only; quality-flag waivers must be named; capped prompt cells handled by the standing capped-cell rule. |
# Run report — suite-science hardening + benchmark expansion (2026-07-08)

**Deliverable check (Ed's session ask, restated):** harden the science the
prompt/workload suite can answer; decide and begin what to build next;
expand toward multi-prompt/difficulty/type suites and benchmark interop.
SHIPPED: the science-hardening contract stack, the expansion design, the
Window-A capture + sentinel code, and the cross-checked implementation
research for the suite itself. NOT YET SHIPPED: the suite implementation
(P2-010a/P2-012/P2-020 code) — build lane reopened by D-042; the handoff is
`docs/phase_2/suite_implementation_research.md` (adjudicate its amendments
first). Mid-session, Ed had to point out the suite itself wasn't being
built — recorded as a process lesson (skill-usage log).

## Product outcomes (all merged to main, HEAD `fcd111a`)

- **PR #14 (suite-science-hardening, 4 commits, merged `5c19099`):**
  - `docs/contracts/analysis_plans.md` (D-038): pre-registered analysis
    plans binding L2/L3 claims; AP-1..AP-6 seeded; MDE arithmetic
    (`MDE95 ~= 1.46xCV`, 80%-power `~2.0xCV` t-based); pseudo-replication
    rule; floor gate `max(floor_abs, floor_cmp)`.
  - Program v2 (D-039): `q4_l3_shape_grid_v1` (4x3 + interpolation/
    extrapolation holdouts — the only current path to L3), P2-015 expanded
    to per-metric/window-class floors + comparative MDE, jw_mixed
    common-shape stratum + 3-phase sequencing, P2-010a/b split,
    two-quiet-window plan, Phase 4 figures F9-F12.
  - Suite architecture v2 + interop (C-015, D-040/D-041): one generic
    suite mechanism (B×k bundles, r_within=1, per-item status model,
    difficulty as quarantined metadata); `benchmark_import` manifest
    (HumanEval smoke first, FLORES second); marker-shim energy layer
    (contract in `adapter_contracts.md`; P2-022 verdict-shaped spike);
    kill list; capability map by claim ceiling (bank).
  - `docs/phase_2/suite_implementation_research.md`: 4 cross-checked
    research reports (execution architecture, category generators,
    affine ladder, licensing) — amendments unresolved by design.
  - D-042: owner directive reopens the suite BUILD lane pre-2M; campaign
    execution ordering unchanged.
  - Queue: P2-019..P2-024 added; P2-010/012/015/016/020 amended.
- **PR #15 (p2-021-drift-sentinels, merged `8765ee1`):** P2-021 DONE —
  `short_short_sentinel` at each model-block boundary (self-identifying
  tags), block/position covariates in the order manifest + campaign-log
  echo, fail-loud on sentinel-less blocks. Suite 602.
- **PR #16 (window-a-capture, merged `fcd111a`):** the C-015/R2
  collect-before-Window-A set: per-run env snapshots at prepare-end
  (+2s settle; failure_fallback scope for early failures), cooldown-gate
  trace preservation, signed inter-run gaps + `clock_step_suspect`,
  `tokenize`/`generation_setup` phase markers, MLX memory snapshots
  (prepare_end/cleanup_start), powermetrics sampler metadata,
  connected-display semantics via system_profiler (framebuffer pipes
  separated). Suite 611.
- Councils C-014 + C-015 (full entries); decisions D-038..D-042.
- Global: skill-usage logging started (`~/.claude/skills/skill-usage-log.md`,
  Ed's standing instruction; memory entry added).

## Verification evidence

- Merged main (fcd111a): `python3 -m unittest discover -s tests` → 617 OK
  (skipped=10), lead-run post-merge (PR heads were 602/611 standalone;
  the merge union adds the cross-stream tests).
- Live lead gates on the capture head (real MLX 1.5B + mock telemetry,
  `.venv` python): strict-valid bundles at both 740c32c and db54cc2;
  no run_end snapshot (blocker fix live-proven); all 4 phases paired and
  honestly `not_resolvable` at sub-sample durations; prepare_end snapshot
  871MB active; display 1 built-in/0 external with pipes 5/4 separated;
  clock probe correct on host (`timed_running: true`).
- 6/6 real corpus bundles strict-valid under the new code (run twice:
  pre- and post-fix rounds).
- CI green both matrix legs on every PR final head.
- Review stack: C-014 (scout + 3 lenses + peer), C-015 (2 reach + 2
  design lenses + peer), pre-commit docs-verify workflow (1 blocker +
  6 should-fixes), stream reviews (S: 7 should-fixes; C: 1 BLOCKER —
  in-window run_end snapshot — + 8 should-fixes), pre-merge oversight
  (3 reviewers + refuters; AP-4 self-contradiction caught), final-head
  passes on every post-review commit (3 wording fixes on #14; #16 clear).
- Post-merge integration review: launched post-fcd111a; its findings and
  the stale-line bookkeeping fixes land in the checkpoint commit
  (see RUN_STATE for outcome).

## Restart instructions (next agent)

1. Read RUN_STATE, then this report, then
   `docs/phase_2/suite_implementation_research.md`.
2. **Suite build (D-042, [AGENT], unblocked):** adjudicate the four
   reports' cross-check amendments (recorded dispositions), then
   implement P2-010a substrate → P2-010b smoke ladder → P2-012 phase-1
   generators + P2-020 sentinel content, per the execution-architecture
   report. Full review tier (measurement-semantics).
3. **Quiet Window A ([QUIET-MAC], next machine-quiet opportunity):**
   P2-015 expanded floors (incl. lead-run tasks-sampler + settle smoke)
   then P2-006 2M with drift sentinels. Corpus now carries covariates.
4. Window B (P2-019 q4 grid + P2-020 campaign) sized from Window A.

## Process trace appendix

- **Shape:** 1 design stream → re-decomposed to 3 (L docs / C capture /
  S sentinels) on Ed's worktree directive; ultracode → 6 Workflow runs
  (2 stream reviews, docs-verify, oversight, suite research, +
  final-head codex passes) over ~60 workflow agents + ~25 codex-run
  sessions. Tiers: full pipeline for capture (measurement semantics) and
  all contract docs; standard for sentinels.
- **Catches (unique, by layer):** lead pre-lens audit 4 (incl. Q4-at-L3
  gap); scout 4; C-014 lenses 16; C-014 peer overturned 2 lead designs
  (4x3 grid, two windows); C-015 peer 1 unique (per-item failure
  economics); docs-verify 7 (incl. 1 blocker: 2O self-contradiction);
  stream-S review 7; stream-C review 9 (incl. THE blocker: run_end
  snapshot inside the measured window — all 3 code lenses independently,
  refuters confirmed with line chains); oversight 8 (incl. AP-4
  equivalence self-contradiction, display pipe-counting via live DUT
  repro); final-head passes 3; lead diff/live gates 4 (C-014 impl 2,
  deprecation fix, venv/runtime_unavailable diagnosis).
- **Deliberations:** P2-010 split (consensus), jw_mixed phasing
  (supersedes C-005 sequencing, consensus), window packing (peer
  OVERTURNED lead single-window — position reversal), Q4 grid (peer
  AMENDED 3x3→4x3 — position reversal), D-042 gate reopening (owner
  directive, recorded not re-decided).
- **Interventions:** zero wake stalls across all codex-runs/workflows.
  Worktree-commit sandbox block hit 2x (lead commits at gate — skill
  fold staged). Ed interventions: worktrees directive; ultracode;
  skill-usage logging; hold-skill-folds-for-full-evidence; the
  object-level suite catch (the session's most important correction).
- **Delegation calibration (schema v2):**

| id | to | unit | altitude | outcome | catches | lead-rework |
|---|---|---|---|---|---|---|
| scout-1 | codex | review packet | pinned-spec | good | 4 unique | none |
| lenses x9 | codex | design/reach/review | design-freedom | good-excellent | 40+ unique | none |
| peers x2 | codex | counterreview | judgment-invited | excellent | 2 overturns + 1 unique | none |
| impl-docs x2 | codex | doc batches | pinned-spec | good | — | 2 inline gate fixes |
| impl-code x2 | codex | streams C/S | pinned+design | good; review layers caught 1 blocker + 15 SF | — | 1 deprecation fix |
| fix rounds x5 | codex | pinned fixes | pinned-spec | clean one-shot each | — | none |
| workflows x6 | workflow(codex) | review/research fan-outs | pinned-spec | high precision (~2 refuted / ~30 confirmed) | — | none |
| research x4 | 2 codex + 2 claude(web) | suite research | design-freedom | sound-with-amendments x4 | 37 amendments self-caught | none |

- **Yield/spend:** ~2.3M workflow-agent tokens + ~25 codex sessions.
  Pre-merge catches that would have been expensive post-2M: the
  sacred-window blocker (would have contaminated the entire 2M corpus),
  the AP-4 unfalsifiable-null (would have poisoned pre-registration),
  dead probes (silent evidence loss on every Window-A bundle).
- **Skill-usage:** full entry + staged folds in
  `~/.claude/skills/skill-usage-log.md` (folds applied at session close
  per Ed's full-evidence hold).


## Addendum — post-large-workload meta-reassessment (same day, C-016)

Run after all merges as the session's final step (now standing per
operation-loop §10 / Ed's directive). Shape: 4 parallel analysts over the
full council log, decision log, and skill stack + a cold-start
derivability audit + a completeness critic; then a pre-commit docs-verify
pass over its own batch (5 should-fixes caught, two by D-043's self-test).
Landed: D-043 supersession-closure discipline + back-annotations
      ],
      "fallback": null,
      "fences": [],
      "flags": [
        "blocked_post_2m"
      ],
      "goal": "Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment.",
      "id": "P2-016",
      "lane": "agent",
      "priority": "p2_next_slice",
      "rank": 24,
      "status": "blocked",
      "status_note": "Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake.",
      "stop_card": null
    },
    "P2-019": {
      "acceptance": {
        "evidence": [
          "AP-1 grid campaign bundles",
          "Holdout cells honored",
          "8192 anchor cells on small+mid models"
        ],
        "pointer": {
          "json_pointer": "/tasks/P2-019/acceptance",
          "label": "P2-019 acceptance",
          "path": "docs/process/state_kernel.json"
        },
        "summary": "Grid campaign lands per AP-1; top-up near-floor cells before L3 wording."
      },
      "authority": {
        "label": "AP-1",
        "path": "docs/contracts/analysis_plans.md"
      },
      "dependencies": [
        {
          "evidence": {
            "label": "R-016 mitigated: off-machine backup and restore proof",
            "path": "docs/risk_register.md"
          },
          "kind": "task",
          "required": "external backup destination live before irreplaceable Window-A evidence accumulates",
          "scope": "retain_evidence",
          "state": "satisfied",
          "strength": "hard",
          "target": "P0-003"
        },
        {
          "evidence": null,
          "kind": "task",
          "required": "Window-A baselines size n",
          "scope": "start",
          "state": "pending",
          "strength": "hard",
          "target": "P2-006"
        }
      ],
      "fallback": null,
      "fences": [],
      "flags": [
        "lead_only"
      ],
      "goal": "q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6).",
      "id": "P2-019",
      "lane": "quiet_mac",
      "priority": "p2_next_slice",
      "rank": 4,
      "status": "blocked",
      "stop_card": null
    },
    "P2-020": {
      "acceptance": {
        "evidence": [
          "Five equal-shape ids-native conditions",
          "Request-energy deltas + MDE verdicts"
        ],
        "pointer": {
          "json_pointer": "/tasks/P2-020/acceptance",
          "label": "P2-020 acceptance",
          "path": "docs/process/state_kernel.json"
        },
        "summary": "Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046)."

codex
# From Software Counter to Scientific Instrument: Phase-Resolved LLM Energy Measurement with Calibrated Refusal

**Thesis:** An Apple software power counter can support reproducible, phase-resolved LLM energy research only when in-session calibration determines both what it can measure and what it must refuse; full characterization, held-out workload prediction, and wall-boundary validation elevate JouleWise from a capstone demonstration to an ICPE-quality metrology paper.

## Project brief and steps

JouleWise currently has a complete paper structure but no live claim-bearing values: historical windows establish the rules and supply design diagnostics, while D-117 requires three fresh prospective windows. The 1.5B floor window contains 10 absolute members and 10 four-member null-ABBA blocks; the 7B floor window repeats that 50-bundle design; both obtain prefill floors from the same bundles at zero additional runtime. The contrast window contains ten 1.5B/7B decode ABBA blocks. Their budgeted durations, including calibration, NEG8 bounds, references, untouched idle, and 20% margin, are 3.14, 3.24, and 2.80 hours respectively. Before any night, desk work must land the two-slot live-calibration ledger session, D-102 acceptance-successor machinery, prefill-capable four-cell mint, three frozen campaign packs, synthetic live-ledger regression, extraction specifications, and readiness packet. After the floor windows pass, mint the combined 1.5B/7B decode-and-prefill floor artifact; after the contrast passes, apply the two distinct claim gates and populate the MVP manuscript.

The ICPE delta should then be disciplined rather than broad: collect the already-designed metrology suite in two or three windows; run the promoted Q4 4×3 workload-shape study in two or three windows; borrow Suzanne Rivoire’s lab WT310E for a pilot and confirmatory whole-machine validation; and package a hardware-free raw-to-figure artifact. Total target: **9–10 claim sessions**, comprising D-117’s three plus **6–7 additional sessions**, with one contingency night reserved but not silently used for outcome-dependent top-up.

## Contributions

1. **Calibrated phase attribution:** Across accepted sessions, the 59-pulse bookends bound edge placement, and every admitted science interval remains inside its authenticated bracket. A systematic or out-of-family calibration falsifies transfer and refuses the window.

2. **Operational detection floors:** Null contrasts at 128, 512, and 2048 output tokens stay inside the declared envelopes, while prospectively sized micro-deltas below the floor are refused and sufficiently above-floor effects clear in both directions. Failure of this ordering falsifies the floor model.

3. **Phase-accounting validity:** Prefill plus decode reconciles with the enclosing request boundary, and prefill does not acquire an above-floor dependence on later decode length. A material residual or slope narrows or defeats phase-resolved claims.

4. **Held-out workload prediction:** A categorical model, \(E=\text{fixed}+\text{prompt level}+\text{decode level}\), fitted without the `(512,256)` and `(4096,512)` cells predicts those held-out cells within the prospectively frozen tolerance. A miss is published and downgrades Q4 from L3 to descriptive L2.

5. **Boundary validation:** On held-out loads, synchronized WT310E measurements determine whether `powermetrics` has a stable gain or load-dependent disagreement for whole-request totals. This does not validate phase allocation; it tests only the absolute whole-machine boundary.

## Experiment plan

The D-117 contrast is low-risk scientifically: the historical diagnostic decode effect is **141.29 J**, roughly 28× the stated 5 J sizing bar and about 10× the historical 7B comparative-floor diagnostic of 14.0 J. Neither historical number is claim-bearing, but both justify the design. The 128-token prefill contrast is excluded: its diagnostic point effect is 5.81 J, but its interval reaches approximately 4.0 J. A refusal would mean “not resolvable at this workload,” not equality.

Metrology window A collects the five-level 1.5B decode ramp (128–2048 outputs; 40 members), three-shape additivity set (24 bundles), the 512-token null rung, and sustained 4096-token holds. Window B collects the 128/2048 null rungs and micro-deltas; a short third window carries extended 120/300/600-second idle holds, stability repetition, or spillover. From diagnostic request energies, the 1.5B decode slope is approximately **0.09–0.10 J/token (uncertain)**: a 64-token delta should be roughly 5.8–6.4 J, while the full ramp spans roughly 170–190 J. Final micro-delta lengths must be computed from the fresh ramp to target approximately 0.5×, 1×, 1.5×, and 3× the minted bar. Near-floor members may honestly refuse.

Q4 uses prompt `{128,512,2048,4096}` × output `{64,256,512}` on the two frozen Qwen2.5 stacks, normally five repetitions per cell and ten only where prospectively identified as near-floor. Decode-length effects should be approximately 12 J per additional 128 tokens for 1.5B and much larger for 7B (**uncertain diagnostics**); long-prompt effects should reach tens of joules. Short-prompt 1.5B effects may not clear 5 J and would become unresolved cells, not fitted evidence. This remains sequential single-request inference and therefore does **not** violate the frozen boundary. Required harness additions are multi-session campaign packing, held-out prediction artifacts, and wall-meter import/synchronization—not batching or concurrency.

## Hardware and instrument needs

Owned: M3 Max/128 GB, pinned MLX/Qwen artifacts, `powermetrics`, and existing calibration/custody machinery. The RTX 3080 Ti and Jetsons are unnecessary. Borrowed: an in-calibration Yokogawa WT310E, safe inline fixture, and its export interface. **Wall-meter dependency: yes for this proposed ICPE-full version**, but no for the underlying MVP. If a qualified loan and safe fixture cannot be secured, do not substitute a consumer plug; submit the metrology core to a workshop or ICPE Emerging track.

## Venue and relationship to the MVP

This is a strong capstone chapter immediately after D-117. ICPE full-track fit comes from the combination of instrument characterization, falsifiable held-out performance prediction, physical-boundary validation, and an artifact reviewers can replay. It reuses the MVP draft’s introduction, related-work gap, measurement model, pulse calibration, floor composition, fail-closed protocol, custody rules, and single-stack limitations. New material is the completed C1–C8 results, cross-day stability, Q4 prediction study, wall regression, and artifact evaluation. Without Q4 or equivalent depth, the work remains an excellent metrology workshop paper rather than a convincing full research-track submission.

## Risks and kill criteria

Kill the ICPE upgrade before spending expansion nights if D-117 cannot mint valid floors; the 150-config metrology suite cannot be repacked below four hours with 20% margin; fresh ramp diagnostics cannot safely place micro-deltas around the operative floor; or Q4 dry runs show missing phases, capped contexts, or a campaign budget above three nights. Kill wall validation if the meter lacks current calibration, safe fixture, adequate synchronized sampling, fixed-range uncertainty at Mac loads, or battery-charge neutralization. A failed Q4 holdout or load-dependent wall discrepancy does not kill the paper—both are publishable findings—but they prohibit predictive or simple-gain claims.

## Relation to Ed’s original goals

This direction directly serves the “energy as a third axis beside quality and latency” goal and the energy-honest leaderboard critique: it supplies the error model and refusal semantics every later comparison needs. Q4 also advances the modular harness by making workload and model axes swappable under one calibrated protocol. It does **not** yet deliver speculative decoding, MTP, MoE routing, KV mechanisms, or split inference. Those remain follow-on studies; forcing one into this paper would weaken its coherent instrument-first contribution.
tokens used
130,264
# From Software Counter to Scientific Instrument: Phase-Resolved LLM Energy Measurement with Calibrated Refusal

**Thesis:** An Apple software power counter can support reproducible, phase-resolved LLM energy research only when in-session calibration determines both what it can measure and what it must refuse; full characterization, held-out workload prediction, and wall-boundary validation elevate JouleWise from a capstone demonstration to an ICPE-quality metrology paper.

## Project brief and steps

JouleWise currently has a complete paper structure but no live claim-bearing values: historical windows establish the rules and supply design diagnostics, while D-117 requires three fresh prospective windows. The 1.5B floor window contains 10 absolute members and 10 four-member null-ABBA blocks; the 7B floor window repeats that 50-bundle design; both obtain prefill floors from the same bundles at zero additional runtime. The contrast window contains ten 1.5B/7B decode ABBA blocks. Their budgeted durations, including calibration, NEG8 bounds, references, untouched idle, and 20% margin, are 3.14, 3.24, and 2.80 hours respectively. Before any night, desk work must land the two-slot live-calibration ledger session, D-102 acceptance-successor machinery, prefill-capable four-cell mint, three frozen campaign packs, synthetic live-ledger regression, extraction specifications, and readiness packet. After the floor windows pass, mint the combined 1.5B/7B decode-and-prefill floor artifact; after the contrast passes, apply the two distinct claim gates and populate the MVP manuscript.

The ICPE delta should then be disciplined rather than broad: collect the already-designed metrology suite in two or three windows; run the promoted Q4 4×3 workload-shape study in two or three windows; borrow Suzanne Rivoire’s lab WT310E for a pilot and confirmatory whole-machine validation; and package a hardware-free raw-to-figure artifact. Total target: **9–10 claim sessions**, comprising D-117’s three plus **6–7 additional sessions**, with one contingency night reserved but not silently used for outcome-dependent top-up.

## Contributions

1. **Calibrated phase attribution:** Across accepted sessions, the 59-pulse bookends bound edge placement, and every admitted science interval remains inside its authenticated bracket. A systematic or out-of-family calibration falsifies transfer and refuses the window.

2. **Operational detection floors:** Null contrasts at 128, 512, and 2048 output tokens stay inside the declared envelopes, while prospectively sized micro-deltas below the floor are refused and sufficiently above-floor effects clear in both directions. Failure of this ordering falsifies the floor model.

3. **Phase-accounting validity:** Prefill plus decode reconciles with the enclosing request boundary, and prefill does not acquire an above-floor dependence on later decode length. A material residual or slope narrows or defeats phase-resolved claims.

4. **Held-out workload prediction:** A categorical model, \(E=\text{fixed}+\text{prompt level}+\text{decode level}\), fitted without the `(512,256)` and `(4096,512)` cells predicts those held-out cells within the prospectively frozen tolerance. A miss is published and downgrades Q4 from L3 to descriptive L2.

5. **Boundary validation:** On held-out loads, synchronized WT310E measurements determine whether `powermetrics` has a stable gain or load-dependent disagreement for whole-request totals. This does not validate phase allocation; it tests only the absolute whole-machine boundary.

## Experiment plan

The D-117 contrast is low-risk scientifically: the historical diagnostic decode effect is **141.29 J**, roughly 28× the stated 5 J sizing bar and about 10× the historical 7B comparative-floor diagnostic of 14.0 J. Neither historical number is claim-bearing, but both justify the design. The 128-token prefill contrast is excluded: its diagnostic point effect is 5.81 J, but its interval reaches approximately 4.0 J. A refusal would mean “not resolvable at this workload,” not equality.

Metrology window A collects the five-level 1.5B decode ramp (128–2048 outputs; 40 members), three-shape additivity set (24 bundles), the 512-token null rung, and sustained 4096-token holds. Window B collects the 128/2048 null rungs and micro-deltas; a short third window carries extended 120/300/600-second idle holds, stability repetition, or spillover. From diagnostic request energies, the 1.5B decode slope is approximately **0.09–0.10 J/token (uncertain)**: a 64-token delta should be roughly 5.8–6.4 J, while the full ramp spans roughly 170–190 J. Final micro-delta lengths must be computed from the fresh ramp to target approximately 0.5×, 1×, 1.5×, and 3× the minted bar. Near-floor members may honestly refuse.

Q4 uses prompt `{128,512,2048,4096}` × output `{64,256,512}` on the two frozen Qwen2.5 stacks, normally five repetitions per cell and ten only where prospectively identified as near-floor. Decode-length effects should be approximately 12 J per additional 128 tokens for 1.5B and much larger for 7B (**uncertain diagnostics**); long-prompt effects should reach tens of joules. Short-prompt 1.5B effects may not clear 5 J and would become unresolved cells, not fitted evidence. This remains sequential single-request inference and therefore does **not** violate the frozen boundary. Required harness additions are multi-session campaign packing, held-out prediction artifacts, and wall-meter import/synchronization—not batching or concurrency.

## Hardware and instrument needs

Owned: M3 Max/128 GB, pinned MLX/Qwen artifacts, `powermetrics`, and existing calibration/custody machinery. The RTX 3080 Ti and Jetsons are unnecessary. Borrowed: an in-calibration Yokogawa WT310E, safe inline fixture, and its export interface. **Wall-meter dependency: yes for this proposed ICPE-full version**, but no for the underlying MVP. If a qualified loan and safe fixture cannot be secured, do not substitute a consumer plug; submit the metrology core to a workshop or ICPE Emerging track.

## Venue and relationship to the MVP

This is a strong capstone chapter immediately after D-117. ICPE full-track fit comes from the combination of instrument characterization, falsifiable held-out performance prediction, physical-boundary validation, and an artifact reviewers can replay. It reuses the MVP draft’s introduction, related-work gap, measurement model, pulse calibration, floor composition, fail-closed protocol, custody rules, and single-stack limitations. New material is the completed C1–C8 results, cross-day stability, Q4 prediction study, wall regression, and artifact evaluation. Without Q4 or equivalent depth, the work remains an excellent metrology workshop paper rather than a convincing full research-track submission.

## Risks and kill criteria

Kill the ICPE upgrade before spending expansion nights if D-117 cannot mint valid floors; the 150-config metrology suite cannot be repacked below four hours with 20% margin; fresh ramp diagnostics cannot safely place micro-deltas around the operative floor; or Q4 dry runs show missing phases, capped contexts, or a campaign budget above three nights. Kill wall validation if the meter lacks current calibration, safe fixture, adequate synchronized sampling, fixed-range uncertainty at Mac loads, or battery-charge neutralization. A failed Q4 holdout or load-dependent wall discrepancy does not kill the paper—both are publishable findings—but they prohibit predictive or simple-gain claims.

## Relation to Ed’s original goals

This direction directly serves the “energy as a third axis beside quality and latency” goal and the energy-honest leaderboard critique: it supplies the error model and refusal semantics every later comparison needs. Q4 also advances the modular harness by making workload and model axes swappable under one calibrated protocol. It does **not** yet deliver speculative decoding, MTP, MoE routing, KV mechanisms, or split inference. Those remain follow-on studies; forcing one into this paper would weaken its coherent instrument-first contribution.
