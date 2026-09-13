OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: high
reasoning summaries: none
session id: 019fdd0d-b829-7443-a6a2-4313971168ce
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

== YOUR ASSIGNED DIRECTION (open-explore-repo) ==
OPEN-ENDED: examine the repository itself — instrument code capabilities, banked non-claim data, custody machinery, existing diagnostics — and propose 3 papers that the CURRENT assets make uniquely cheap or uniquely strong. Full deliverable template per idea, compressed.

2026-08-07T16:28:13.616430Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
codex
I’ll treat this as a read-only portfolio screen: first establish the frozen D-117 baseline and instrument limits, then inventory reusable code/data/custody assets, and finally rank three paper directions by scientific strength per quiet-window cost. I won’t modify the repository.
  → Read required paper, D-117, feasibility, strategy, and question documents
  • Inspect repo intake state plus instrument, custody, and banked diagnostic assets
  • Develop and compare three quantitative paper proposals
  • Deliver compressed reviewable proposals with kill criteria
exec
/bin/zsh -lc 'git status --short --branch && wc -l docs/paper/draft-v1.md CLAIMS_STATUS.md docs/decision_log.md docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md docs/strategy/2026-08-06-impressiveness-roadmap.md docs/research_question_registry.md docs/research_question_bank.md docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md RUN_STATE.md TASK_QUEUE.md docs/agent_playbook.md docs/orchestration.md && rg -n "ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next|Current Queue|Do-Not-Do-Yet|Mission M0" RUN_STATE.md TASK_QUEUE.md docs/agent_playbook.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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
    2837 RUN_STATE.md
     474 TASK_QUEUE.md
     475 docs/agent_playbook.md
     346 docs/orchestration.md
   14036 total
docs/agent_playbook.md:26:1. Run Mission M0 (preflight) — always.
docs/agent_playbook.md:50:## Mission M0: Preflight (every session)
docs/agent_playbook.md:52:1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
docs/agent_playbook.md:53:   if present, "Current Project Status", "Known Workspace State", and
docs/agent_playbook.md:54:   "What Is Next". If the stop card is ACTIVE, it overrides this
docs/agent_playbook.md:56:2. Read `TASK_QUEUE.md`'s Current Queue and Do-Not-Do-Yet list.
docs/agent_playbook.md:326:in the run report. Never close it silently (Do-Not-Do-Yet list).
docs/agent_playbook.md:356:- Land Slice 2N first (Do-Not-Do-Yet list) — 2G builds on the post-2N
RUN_STATE.md:2004:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
RUN_STATE.md:2039:## ACTIVE_STOP_CARD
RUN_STATE.md:2178:## Current Project Status
RUN_STATE.md:2739:## Known Workspace State
TASK_QUEUE.md:15:6. If `RUN_STATE.md` contains an ACTIVE `ACTIVE_STOP_CARD`, that card
TASK_QUEUE.md:96:Current Queue region is the sole live work-selection view.
TASK_QUEUE.md:213:## Current Do-Not-Do-Yet List
TASK_QUEUE.md:306:## Current Queue

exec
/bin/zsh -lc "sed -n '1,260p' docs/paper/draft-v1.md; sed -n '1,240p' CLAIMS_STATUS.md; rg -n '"'^## D-117|D-117'"' docs/decision_log.md | tail -20; sed -n '2039,2215p' RUN_STATE.md; sed -n '2739,2837p' RUN_STATE.md; sed -n '213,380p' TASK_QUEUE.md; sed -n '50,105p' docs/agent_playbook.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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
7084:> **2026-08-07 supersession (D-117):** clause 3's historical re-mint
7088:> allowance correction STAND and bind the D-117 mints.
7249:> **2026-08-07 amendment (D-117 cl.4):** the readiness dependency on
7507:## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired
## ACTIVE_STOP_CARD

Status: NONE — no stop card is active. Stop-card authority: D-050 / D-063 ([decision log](docs/decision_log.md)).

## Active Global Work-Selection Gates

NONE — no global work-selection gate is active.

## Restart By Machine-State Lane

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-05). Latest report: [16h runway checkpoint 2026-08-03: D-108..D-112 minted; kernel pins 60; CAL-BRACKET held at 2e61ff9 (rule-11 gate owed for B1 round 2); winB license exhausted as drawn (r06 disposition parked, WINB-R06-DISPOSITION-01); mint chain D-110-blocked; CLAIMS_STATUS §1 honestly NONE; checkpoint block at the top of RUN_STATE is the successor resume script.](docs/run_reports/2026-08-03-16h-runway.md).

### [ED-EXTERNAL]

- READY — E1 `P1-008`: Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).

### [QUIET-MAC]

- READY — Q2 `P2-006`: Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison.

### [AGENT]

- READY — A0 `P2-035`: RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests).

<!-- END GENERATED: state-kernel run-state-intake -->

## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open

The RESUME list from the 2026-07-17 checkpoint is fully executed. The
relaunched execution-lens review, fix rounds 1-2, and their delta
re-audits had already run earlier on 2026-07-18 (commits `1aebf14`,
`6d80039`); this session closed the surviving P1 (child accepted any
JSON object as the frozen cooldown anchor) plus every finding from four
further delta re-audits, as fix rounds 3-8 in commit `ad0920b`:
canonical anchor validator (`joulewise/cooldown_anchor.py`) enforced
fail-closed at parent/CLI/controller boundaries; collision-safe,
crash-atomic, flock-serialized rejection-verdict custody
(`experiments/rejections/`); physical-domain baseline validation (the
`inf`-anchor fail-open gate is closed); discriminating process-race
regression. Suite green lead-side at every round boundary, final
`Ran 1746 tests`, `OK (skipped=12)`. Awake-half live probe validation
passed on real hardware (zero probe errors); the Ventura screensaver is
now disabled on the machine (`idleTime = 0`). PR #77 carries the gate
narrative; merge is Ed's call. Full record:
`docs/run_reports/2026-07-18-d077-fix-rounds.md`. Tooling: codex-run-v3
xhigh review-genre sessions ended with null final messages 4x
(bridge-resume recovered each; personal-tooling defect, recorded in the
run report and the global codex-delegation skill field notes, not the
repo queue).

## CHECKPOINT 2026-07-18: Claude script bridge runs in the pet's app task

The actual Claude Code fallback route is `scripts/codex-bridge`, not the MCP
server for recent audited work. The wrapper now sends `new` and `review` turns
through a dedicated app-owned Codex desktop task when the local host id is
configured. This is the same local-conversation state the native pet consumes;
the prior observer-only diagnosis was incorrect because the pet never reads
`~/.codex/claude-spawned/index.jsonl`. A live Sol/high smoke appeared in the
Codex app as thread `019f77a6-3612-7332-9f5e-be9fbde56be5`, turn
`019f77a9-2827-7de1-accf-ac2eda21927e`, and returned
`JOULEWISE_NATIVE_PET_BRIDGE_OK` through the script. Adaptive effort remains
unchanged: `high` fallback/default, `xhigh` only on named hard-task triggers,
and `ultra` only for sessions that must spawn subagents. Full record:
`docs/run_reports/2026-07-18-claude-codex-pet-observer.md`.

Committed 2026-07-18 on `impl/env-guard-cooldown` (after the D-077
packet boundary `6d80039`) with a lead execution review at the bench:
IPC socket ownership/permission checks, PID-checked host-task lock,
interrupt-on-terminate, no-network sandbox policy, and one-hop rule all
verified in `scripts/codex-app-bridge.mjs`; real-socket fake-router
tests plus observer lifecycle tests included; canonical suite green
lead-side (`Ran 1722 tests`, `OK (skipped=12)`). The same commit
carries the doctor-driven CLAUDE.md trims (global + repo; content
deduplicated into `.claude/skills/codex/SKILL.md`, which is the
operating home) and stamp-only `docs/site/*.html` provenance refresh.

## CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending

Window A floors contamination diagnosed from primary data: macOS Ventura
*video* screensaver on an awake display contaminated 43/50 suite-calibration
bundles (~+30% energy, −11% throughput; engage at HID-idle +20 min, dismiss on
unlock — pmset assertion log corroborated to the second). The six "low"
su-ABBA runs (18:16–18:36 UTC) are the only CLEAN suite runs; comparative
suite floors (4.923 J item / 24.62 J suite) are transition artifacts. The
professor's power-source hypothesis is refuted (AC/140 W/100% throughout).
Details: memory note + `docs/run_reports/2026-07-17-environment-guard.md`.

Branch `impl/env-guard-cooldown` (pushed, commit e2813ee) holds the D-077
response: environment-guard preflight (+`--arm-quiet-mode`), per-run idle
admission gate, cooldown v2, unwaivable `environment_admission_failed` claim
barrier, policy sidecars, contract/doc updates. Design consult (Sol xhigh,
thread 019f7356-32d3) adjudicated and encoded; implementation by Sol xhigh
(thread 019f7362-6627, resumed via codex-bridge after an MCP transport
timeout); session-close scope check SCOPE_OK; full suite green lead-side
(OK, 12 skips). Lead bench fix included: `pmset -g systemstate` parser now
accepts the live "Capabilities are:" form (was null → fail-closed on real
hardware); fixtures pinned to verbatim live output.

RESUME (in order):
1. Relaunch the adversarial review round (was stopped mid-run at checkpoint):
   fresh read-only Sol xhigh, execution lens, over `git diff main...impl/env-guard-cooldown`
   (prompt shape in `.codex-bridge/` prompt snapshots); lead holds the
   contract lens (done for cooldown_gate/claim-barrier/anchor hunks).
2. Triage findings → fix rounds (defect-shaped regressions) → DELTA RE-AUDIT.
3. Live-validate flagged probes during next quiet-window prep:
   `pmset -g systemstate` display-asleep form + screensaver-engaged probe
   while a screensaver is actually running (run report flags
   `live_validation_provisional`).
4. PR per operation-loop §5 gate shape; then re-run suite ABBA calibration
   under the new guard ([QUIET-MAC], needs Ed) — floors D-076 figures for
   suite comparative cells must be recomputed/caveated pending re-run.

Status: **CLEARED 2026-07-11.** Every clearance criterion met: all
checkpoint-#4 resume items executed (P2-044 fix+merge #55; P2-037
audit dispositions → two fix rounds + approved NEEDS_SCOPE expansion +
delta re-audit → #58; P2-043 #57; P2-045 #56); the four held hardening
PRs #50-#53 merged after the cross-stream integration review over the
combined tree (38 pre-merge cross-stream failures caught and fixed; 1
review blocker confirmed by refuters → PR #59; SF1 refuted; SF3 →
queue row P2-049); DOC-008 kernel refreshed at final head (schema v2,
authority field, branch impl/doc008-kernel awaiting PR); bookkeeping
arc complete (run report, C-028 council entry with layer catch-rates
and ~57-invocation spend record, D-064 ratified incl. manifest v3 +
claude-codex-report/v1 + WRITE_SCOPE enforcement; queue reconciled;
consistency sweep; site regen+deploy). All clearance-time opens since CLOSED same day: #59 MERGED, DOC-008
MERGED (#60). Remaining queue heads: P2-049/P2-050/TOOL-01.

## Superseded stop card (CP-5)

Status: **CLEARED 2026-07-09** by the CP-5 resume session. Every
clearance criterion was met: all three worktree diffs lead-gated
(envgate live-gated against the real affine mock bundle) and merged as
PRs #23/#24/#25; PR #22 merged after a fresh final-head pass; the
methodology synthesis and suite_next specs packet adjudicated (CP-6 in
the stream log); all accepted pre-campaign changes landed and merged
(PRs #26/#27/#28); both post-merge integration reviews CLEAN; queue
rank 0 closed. Full record:
`docs/run_reports/2026-07-09-cp5-resume.md`. No stop card is active.

## Current Project Status

**Mint era OPEN AND FIRST MINT LANDED (2026-07-30): main `da83337`. The
data exists and passes, and the code path that turns it into a published
floor now exists and has been exercised — `df-ph-decode-floor-mint1` is
mainline.**

### The central measurement fact (read before any measurement decision)

The instrument is **attribution-limited (~1 J), not noise-limited
(~0.3 J)** — D-078 clause 11, Ed-ratified. Floors publish LABELLED with
the widened number; the point floor is a repeatability diagnostic that
may never be the published claim floor. The anchor term appears in
**both** the floor and each claim's decision interval, so the effective
clearable effect is floor + claim-side bound ≈ 5 J for phase contrasts,
and neither term may later be deleted as an apparent double count. Do
not launch an instrument-tightening program; it was measured and
eliminated.

### Collection state

| Window | Contents | Verdict | Notes |
|---|---|---|---|
| a9, a10 | earlier corpora | **PASSED** | a10 supplies the absolute component |
| **B** (`04_phase_prefill_abba`) | 40 prefill ABBA members, 59/59 collected clean | **FAILED** | `instrument_calibration_mismatch`, bracket drift 11.581436 ms; preserved, not claim-bearing |
| **C** (`05_phase_decode_abba`) | 40 decode ABBA members, 59/59 collected | **PASSED** | bracket drift 1.279 ms; first comparative window in project history to pass |
| **D** (absolute) | 30 claim members, 49/49 collected | **PASSED** | bracket drift 0.484 ms, tightest of the campaign |
| **7B floor** (`window_7bfloor_20260729`) | Qwen2.5 7B decode floor, collected 2026-07-29 | **PASSED** | CLAIM-BEARING; governed extraction clean (`all_cells_extractable` true). Floors: absolute 6.294380135190098 J, comparative 13.998036715259254 J; absolute-cell member mean 192.38623252628366 J (n=10). NOT yet minted — `MINT-GENERALIZE-01` is OPEN and unblocked as of 2026-08-02 (gauntlet closed PR #93; D-088 no-mint condition lifted), so these figures live only in prose plus the out-of-repo custody extraction until that mint runs |
| **contrast** (`window_contrast_20260730`) | 40 contrast ABBA members + 7 references, 47 bundles, 1 supersession | **PASSED** | bracket drift 1.281 ms; contrast diagnostic 146.730349 J σ 0.241 (n=10 blocks) UNGATED — MANIFEST-CONTRAST-01 closed 2026-08-02 (PR #95); the gated claim now rides `MINT-GENERALIZE-01` then the D-095 chain |

Window B's cause is established and is NOT a clock problem: a GPU DVFM
power ramp that the rectangular-pulse fiducial estimator aliases into an
apparent onset shift (93.28% of the drift; the wall-clock term moved the
OPPOSITE way, −0.201464 ms). D-079 clause 3 adds a pre-flight screen that
detects it in the ~4-minute pre-calibration, with cause-removal (never
outcome-selection) retry semantics.

**Corrected floor figures — the old ones must not be repeated.** a10's
## Known Workspace State

- (2026-08-02, CURRENT) `main` and `origin/main` at `bcbc10b`; working
  tree clean except the untracked private `CLAUDE.local.md` (Ed's;
  never commit) and `.desk/` (adjudication custody; never commit).
  PR #93 merged (the c3 branch is closed). Branch
  `impl/d100-bii-binding` exists in the session worktree
  `scratchpad/d100bii` holding the UNCOMMITTED, audit-pending
  D100-BII-BINDING-01 diff (envelope protocol failure; see §9).
- (2026-07-31, historical) `main` and `origin/main` were both at `6ed1625`:
  the PR #89 merge `7ee680c` (D5-J) plus the close-out commits
  `49c1876`, `0d0bd0b`, and `6ed1625`. Branch `impl/mint-tool` is MERGED
  (verified `git merge-base --is-ancestor impl/mint-tool main`), as are
  `impl/floor-mint` and `impl/floor-label-clean`; all three may be
  deleted. Their scratchpad worktrees are still registered (`minttool`
  plus ~11 review/pin worktrees under the `9c166892…` session dir, and
  prunable entries under `ad48bfae…` and `d714f367…`) — `git worktree
  prune` plus explicit removal is owed as housekeeping. The working tree
  is clean except for the untracked private `CLAUDE.local.md` (Ed's
  file; never commit it).
- (2026-07-28 late, historical) `main` and `origin/main` were at that
  session's bookkeeping commit atop the PR #87 merge `058c918`. Branch
  `impl/mint-tool` (pushed, then UNMERGED) held the 9-commit mint series
  `2a0ecbc..697f741` in worktree
  `/private/tmp/claude-501/-Users-edr-code-JouleWise/9c166892-d763-42c4-8cf7-383912f054c9/scratchpad/minttool`;
  canonical suite at its head `1d83d68` is UNVERIFIED (rerun was in
  flight at checkpoint). Branch `impl/floor-mint` is merged via PR #87
  and may be deleted. NOTE: a concurrent session force-rewrote main
  history this evening (content preserved; see run report Anomalies) —
  verify `git log` freshness before building on a cached head.
- (2026-07-27, historical) `main` and `origin/main` were at `7337b33`. Branch
  `impl/floor-mint` @ `617060a` is pushed and NOT merged; it carries the
  pre-mint floor schema hardening. Window C (+bound) and a10 (+bound)
  remain FULLY resident in the working tree (mint #1 inputs); windows B/D
  and all other runs corpora are locally pruned to small evidence files
  (traces archived + verified in iCloud, see "Disk" above), and custody
  material lives OUTSIDE the repo at `~/JouleWise-window-custody/` — an
  agent searching only the repo will wrongly report quarantined evidence
  missing. Disk has 115 GB free; a window writes ~6 GB. The next quiet-window operator must start
  from a separate clean, merged-main measurement checkout per
  `docs/phase_2/window_runbook.md`.
- The generated state-kernel regions in this file and `TASK_QUEUE.md` are
  IN SYNC with `docs/process/state_kernel.json`
  (`python3 scripts/gen_state.py --check` exits 0), and the kernel's own
  content was refreshed on 2026-08-01 (desk adjudication session):
  stamped `updated: 2026-08-01`, `latest_report` points at
  `docs/run_reports/2026-08-01-desk-adjudication-session.md`, the MET
  rows are folded in, the completed
  `FLOOR-LABEL-01`, `STACK-ID-BIND-01`, `P2-015`, and
  `COOLDOWN-JOIN-DA1-01` rows are retired to
  `TASK_QUEUE.md`'s completed table, and the post-mint intake
  (`COOLDOWN-JOIN-GAUNTLET-01`, `MINT-GENERALIZE-01`,
  `MANIFEST-CONTRAST-01`, `SUPERSESSION-DUP-REFUSAL-01`,
  `QA-10A-JOIN-OMISSION`, `QA-10B-EXISTING-RETRY`) is folded in. Any
  further change means editing the kernel and then running
  `python3 scripts/gen_state.py` — never hand-editing the generated
  regions.
- (2026-07-25, historical) `main` and `origin/main` were at `c3e2647`,
  the PR #85 merge; PR #79's repair and PR #85's SCREEN+BUDGET
  implementation both landed with green final PR-head CI.
- The generated state-kernel blocks are authoritative for work selection.
  Hand-authored `RUN_STATE.md` and `TASK_QUEUE.md` text remains authoritative
  only for its own factual, policy, and historical domains;
  `docs/decision_log.md` remains the policy authority, exit checklists own
  phase completion, and evidence artifacts own scientific truth.
- Retained corpus and session scratchpad evidence are immutable.

## Historical Next-Work Snapshot (superseded 2026-07-15)

The following 2026-07-13 narrative is retained for chronology only. It is not
a live queue or restart instruction; the generated work-selection region is
the sole selector.

The comprehensive whole-project audit is the declared gate (Ed,
2026-07-13): method proposal pending Ed's approval, then the audit runs
and its findings are adjudicated before any further feature work. After
that: Window A in the first clean quiet-machine window (C-019/P2-015-SMOKE,
then P2-015 floors, P2-006 baselines), with post-audit [AGENT] heads
P2-050 adjudication, SITE-02, and P2-027 publication prep outside quiet
windows. `TASK_QUEUE.md` remains the ordering authority.

Hardware-gated (unchanged): 2K/2L (P1-006; NV-GATE-2 additions from
C-027 apply at live promotion), wall meter (P1-003), topology (P1-004),
calendar mapping (P1-008).

## Reference Decisions And Blockers (non-selection context)

These pointers retain external-dependency context but do not rank or select
work. The generated region controls task selection.

- Supervisor approval and scope pending (P1-001, R-001 — mitigation
  holding); gates FULL D-016 closure.
- Calendar dates pending (P1-008, R-012).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).
- Git author identity on this machine auto-selected as
  `Ed R <edr@Eds-MacBook-Pro.local>`. Amend future commits if a
  different identity is needed.
## Current Do-Not-Do-Yet List

- (satisfied 2026-06-12) The mock bundle/reducer path and report generator
  now exist; dashboard/report work is no longer blocked.
- (satisfied 2026-06-12) The mock lifecycle is runnable, so live
  MLX/powermetrics implementation may proceed once its hardware gates open
  (P1-002 + D-016); follow `docs/phase_2/hardware_slice_implementation_guide.md`.
- (resolved 2026-06-12) Hailo feasibility has a verdict
  (`unsupported_workload`); do not implement a Hailo backend — report it as
  an applicability finding.
- Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in
  D-008; implementation waits).
- Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate
  (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware
  pairings, or borrow-window scheduling before 2M baselines and the Stage
  3.0 verdicts exist (C-007 wording fix; was previously stated as a
  blanket Phase 3 hold that contradicted the queue).
- Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the
  rehearsed runbook exist (R-006).
- Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has
  produced data.
- Do not close D-016 (model selection) without P1-001 supervisor scope or an
  explicit user go-ahead.
- (satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own
  gates (D-016 + `[mac]` install; privileged sample + D-004 sudoers) open —
  build on the post-2N seams (RunContext raw evidence, D-026 markers,
  D-027 rail rows, 2N.3 observed-token fallback).

## Queue Maintenance

At the end of substantial work:

- Update live status, rank, dependencies, and new tasks in
  `docs/process/state_kernel.json`.
- Remove terminal tasks from the kernel only after their owning completion
  evidence supports closure; preserve the dated Completed row here.
- Run `python3 scripts/gen_state.py`; never hand-edit generated queue or
  restart rows.
- Keep hand-authored edits here to policy, completed/history records, and
  non-selection context.

## Intake Batch Owed To The Kernel (2026-07-30/31)

**PARTIALLY FOLDED 2026-07-30.** Six rows —
`COOLDOWN-JOIN-GAUNTLET-01`, `QA-10A-JOIN-OMISSION`,
`QA-10B-EXISTING-RETRY`, `MINT-GENERALIZE-01`, `MANIFEST-CONTRAST-01`,
and `SUPERSESSION-DUP-REFUSAL-01` — were folded into
`docs/process/state_kernel.json` on 2026-07-30; their staged rows were
removed from this table. Of the six, only `MINT-GENERALIZE-01` and
`SUPERSESSION-DUP-REFUSAL-01` remain LIVE as of 2026-08-02: the
gauntlet trio retired with PR #93 and `MANIFEST-CONTRAST-01` with
PR #95 (see the completed table).
`COOLDOWN-JOIN-DA1-01` followed on 2026-07-31 (D-093), in the same pass
that retired `P2-015` to the completed table and closed
`QUEUE-RECONCILE-01`; both of those staged rows were removed too. It was
short-lived as a live row: DA-1 closed later the same day inside the
gauntlet's commit 2 and `COOLDOWN-JOIN-DA1-01` is now retired to the
completed table (PR #91, `67d268a`).

**The rows that remain below are STAGED, not live**, and stay staged by
magistrate scope decision 2026-07-30 (the P2/P3/P4 residue is not
competing for this window's selection). Work selection is the generated
region below; nothing here competes with it until the magistrate folds a
row into `docs/process/state_kernel.json` and runs
`python3 scripts/gen_state.py`. They are recorded here — hand-authored,
outside the generated markers — so the 2026-07-29/30 arc's owed rows
cannot be lost between the ruling and the kernel refresh (kernel refresh
is magistrate-owned).

Sources: `docs/decision_log.md` D-083..D-093; `docs/council_log.md` C-039
addendum + addendum II; the delegated related-work sweep
(`docs/run_reports/2026-07-30-sweep-techniques.md`); the
`splitwise_decode_v1` campaign doc §2
(`docs/phase_2/splitwise_decode_campaign.md`, on main since `27ffc91`).

| ID | Priority | Lane | Task | Evidence / Acceptance | Authority |
|---|---|---|---|---|---|
| QA-1-COOLDOWN-LAUNDER | P0 Safety | [AGENT] | **CLOSED at `16c7af0` (FIX-10, 2026-07-30).** The fail-open declared-occurrence edge the FIX-9 delta re-audit found (a member declaring `bundle_ids: ["x", "x"]` with only one usable `physical_members` row resolved via the one-row fast path without the supersession matcher) is closed by declared-occurrence tallying; both defect-shaped regressions failed pre-fix and pass post-fix. The FIX-10 delta re-audit confirmed this shape closed while finding the two successor edges now carried as the LIVE kernel rows `QA-10A-JOIN-OMISSION` and `QA-10B-EXISTING-RETRY` (folded 2026-07-30; see the generated region below). | Closed: fast path licensed only at declared count exactly 1; regressions in `SupersessionAwareCooldownJoinTests`; lead-verified 48/48 focused. | [D-086/D-088](docs/decision_log.md); FIX-10 delta re-audit 2026-07-30 |
| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
| MDE-ADOPT-01 | P2 Next Slice | [AGENT] | Powered MDE for the **repeatability arm** + workload-sizing inversion: replace the informal repeatability statistic with δ\* = 2.80·σ_D/√m (α = 0.05, power 0.80) over ABBA pair differences, and size the pilot with m ≥ 2.80²·σ_D²/δ². Desk work on existing data; makes the ad hoc "+5 J claim-side" principled. | Floor computation carries a powered MDE for the repeatability arm with its α and power stated. **Hard boundary, do not cross:** this does NOT apply to the systematic arm — RSS composition is valid only for independent random components, and RSS-ing a worst-case attribution bound as if it were an SD is anti-conservative. `max(repeatability, corner) + drift` stays. | [Sweep-techniques top-10 #1 + §5](docs/run_reports/2026-07-30-sweep-techniques.md) |
| MIN-WINDOW-RULE-01 | P2 Next Slice | [AGENT] | Minimum-window rule + loop-to-60 s for short phases: declare a duration-conditional validity domain (N× the powermetrics cadence; SPEC's 60 s reached by looping the workload if shorter) and **fail-close** phases below it. Attacks the attribution-dominated 6–14 J floors directly, since edge error amortizes with window length. | A declared, enforced validity domain with phases below it refused rather than reported. Note the coupling: changing workload duration resizes the science, so any loop-to-60 s change is a pre-registration change and therefore Ed's call (see `FLOOR-WORKLOAD-SIZING-01`). | [Sweep-techniques top-10 #3](docs/run_reports/2026-07-30-sweep-techniques.md) |
| BATTERY-CROSSCHECK-01 | P2 Next Slice | [QUIET-MAC] | Internal dual-instrument cross-check **before** any wall meter: validate powermetrics integrals against an independent on-device channel (battery/SMC drain over long windows; channel-sum vs package reconciliation) and publish the agreement bound **with its validity domain**. Narrows "never externally validated" without a purchase. | A published agreement bound with its stated validity domain. Caution carried from the same memo: embedded telemetry (BMC/SMC) must NOT be treated as a trusted second reference without its own characterization — the bound is a cross-check, not a calibration. | [Sweep-techniques top-10 #4](docs/run_reports/2026-07-30-sweep-techniques.md) |
| REFUSAL-VOCAB-RATIFY-01 | P1 Phase Gate | [AGENT] + magistrate | Ratification question, deferred out of cold gate F1: reordering the separation-validation phases would **alter refusal precedence**, which D-087 placed in "vocabulary-ratification territory". The refusal vocabulary needs a ruling before any reorder is attempted. | A ruling on the refusal vocabulary and precedence, recorded in the decision log; only then may a phase reorder be proposed. | [D-087](docs/decision_log.md); refusal-scope spec v1 (`ea16730`, on main via PR #88) |
| MOCK-SAMPLER-PROV-01 | P4 Polish | [AGENT] | (Cold-gate finding **F2**.) The mock runtime should emit **truthful sampler provenance**; today the integration tests rewrite metadata to inject a sampler — a test-honesty item. | Mock runtime emits real sampler provenance and the metadata-rewriting test helper is deleted. Mitigated meanwhile: mock bundles are already refused at claim binding by `MOCK_TELEMETRY_CLAIM_REFUSAL`, so there is no claim exposure. | [D-087](docs/decision_log.md) (F2 disposition) |
| COOLDOWN-JOIN-FIXTURE-01 | P4 Polish | [AGENT] | (FIX-9 delta re-audit finding **QA-2**.) No repository fixture composes the **real** supersession validator/reader with the cooldown join; the FIX-9 regressions stub the reader, which is adequate for join/matcher behavior and insufficient as custody-path closure. | A real validator-reader-join fixture exercising the composed custody path end-to-end. | [C-039 addendum](docs/council_log.md); FIX-9 delta re-audit QA-2 |
| MINT-TOCTOU-01 | P4 Polish | [AGENT] | (Audit finding **Audit-F1**, adjudicated QUEUE.) TOCTOU between the mint's pre-check and its authenticated artifact read. Requires concurrent mutation of a frozen input; a different signature from the FIX-8 defect class. | Either the read is made atomic with the pre-check, or the exposure is recorded as an accepted limitation with its precondition stated. | Session ledger, staged-mint section; D-087 sibling dispositions |
| FLOOR-ARTIFACT-SHA-PIN-01 | P2 Next Slice | [AGENT] | Review finding **B2** — artifact-SHA pin. **Detail owed:** the finding's text lives in the review packet, not in the session ledger; whoever promotes this row must restate the defect from the packet before it can be READY per the Ready/Shelf rule. | Not yet acceptance-specified — promote to READY only after the B2 finding text is recovered and restated. | Session ledger, F2 disposition paragraph ("register at bookkeeping with … B2 artifact-SHA-pin row") |
| EXACT-SET-REGRESSION-01 | P2 Next Slice | [AGENT] | Review finding **S2** — exact-set regression. **Detail owed** (same caveat as B2): the ledger names the row but not its content. Likely adjacent to D-086 root cause 1 (exact-set vs governed-subset matching when `--evaluation-basis-sha256` is omitted), but that adjacency is **inference and must be confirmed against the packet**, not assumed. | Not yet acceptance-specified — promote to READY only after the S2 finding text is recovered and restated. | Session ledger, F2 disposition paragraph |
| COLLECTOR-NIT-B1 | P4 Polish | [AGENT] | Review finding **B1** collector nit (distinct from the refuted B1 `device.boundary` placeholder finding — do not conflate). **Detail owed**, same caveat as B2/S2. | Not yet acceptance-specified. | Session ledger, F2 disposition paragraph |
| SITE-ROADMAP-PAGINATE-01 | P3 Tooling | [AGENT] | Paginate or shard the site roadmap page: `roadmap.html` emits one card per live kernel row and now sits at 29,620 of the 30,000-byte capsule shard budget (98.7%) after the 2026-07-30 kernel fold — the NEXT intake fold breaks `CapsulePackError`. | `build_site` succeeds with at least 10 additional live kernel rows; no shard exceeds budget; existing roadmap content preserved. | Kernel-refresh finding 2026-07-30 (session report) |
| DOC-RUNSDIR-ABS-01 | P4 Polish | [AGENT] | Tool contract doc note: the extraction CLI's `--runs-dir` **must be an absolute path**. Document it at the tool contract, and consider a fail-closed check rather than leaving it as operator lore. | Doc note landed; optionally a refusal on a relative `--runs-dir` with a regression. | [D-086](docs/decision_log.md) (queued from lieutenant findings) |
| LITREAD-VERIFY-01 | P4 Polish | [AGENT] | Pre-submission verbatim re-verification of the two load-bearing related-work sources against the **PDFs of record**: TokenPowerBench (arXiv **2512.03024**) and "The Illusion of Power Capping in LLM Decode" (arXiv **2605.11999**). Both were read in full text during the sweep, but through WebFetch's extraction model against the arXiv HTML renders. | Every quote and number cited in a submission re-checked against the PDF. **Note the id correction:** TokenPowerBench is 2512.03024; 2605.11999 is the Illusion paper — earlier handoff text conflated the two. | [Sweep-techniques access summary](docs/run_reports/2026-07-30-sweep-techniques.md) |

## Current Queue

The generated region below is the sole live queue and source of truth for
work selection. Edit the kernel and regenerate; do not hand-edit its rows.

Superseded (2026-07-15, WO-012; D-043): Q4/P2-019 sample size is frozen in the hash-bound analysis registry before outcomes, and outcome-dependent growth permanently demotes the contrast to exploratory; see `docs/contracts/analysis_plans.md` §Required fields.

Superseded (2026-07-15, WO-017; D-043): P2-027 publication and uninvolved-party re-reduction are optional owner-directed evidence-handoff work, not the default reproducibility or project-completion gate; see `docs/specs/c027/rpt-001_report_vertical_slice.md` §0.4 and `docs/contracts/publication_privacy.md` §Publication boundary.

<!-- BEGIN GENERATED: state-kernel current-queue -->
<!-- GENERATED from docs/process/state_kernel.json by scripts/gen_state.py. Do NOT hand-edit between the markers; edit the kernel and regenerate. -->

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-05).

Generated compatibility table for repository consumers; the lane tables below are the detailed view of the same kernel state.

| Rank | ID | Priority | Status | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| E1 | P1-008 | P1 Phase Gate | READY [ED-EXTERNAL] | Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability). | Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: [Milestones + R-012](docs/milestones.md). Acceptance: [P1-008 acceptance](docs/process/state_kernel.json). Note: R-012 is the biggest active management risk for an undergrad timeline. |
| E2 | P2-027 | P2 Next Slice | READY [ED-EXTERNAL] | Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party. | Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: [C-020 + C-027 NEG-9](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-027 acceptance](docs/process/state_kernel.json). Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL. |
| E3 | P1-001 | P1 Phase Gate | READY [ED-EXTERNAL] | Capture supervisor approval and scope notes. | Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: [R-001](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped. |
| E4 | P1-003 | P1 Phase Gate | READY [ED-EXTERNAL] | Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method. | Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: [D-018/C-003](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Elevated value: gates Q6 boundary sensitivity (C-003). |
| E5 | P1-004 | P1 Phase Gate | READY [ED-EXTERNAL] | Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method. | Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: [R-011](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Partial. |
| E6 | P1-006 | P1 Phase Gate | READY [ED-EXTERNAL] | Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L). | Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: [Remote gate / NV-GATE-2](docs/phase_2/hardware_slice_implementation_guide.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). |
| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) [QUIET-MAC] | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
| Q2 | P2-006 | P2 Next Slice | READY [QUIET-MAC] | Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison. | Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: [Phase 2 plan + analysis plans](docs/phase_2/phase_2_plan.md). Acceptance: [Phase 2 exit checklist](docs/phase_2/phase_2_exit_checklist.md). Note: Software interpretation gates are satisfied; Window-A floors landed 2026-07-31 (mint #1 mainline), so only the campaign remains. |
| Q3 | P2-010 | P2 Next Slice | READY [QUIET-MAC] | P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail. | joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: [AP-5 + affine stream log](docs/contracts/analysis_plans.md). Acceptance: [P2-010 acceptance](docs/process/state_kernel.json). Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains. |
| Q4 | P2-019 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC] | q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6). | Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: [AP-1](docs/contracts/analysis_plans.md). Acceptance: [P2-019 acceptance](docs/process/state_kernel.json). |
| Q5 | P2-020 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC] | Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts. | Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: [AP-6 + D-046](docs/contracts/analysis_plans.md). Acceptance: [P2-020 acceptance](docs/process/state_kernel.json). Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6). |
| Q6 | P2-012 | P2 Next Slice | BLOCKED — P2-006 (identification-core runs after Window A) [QUIET-MAC] | Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases. | Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: [AP-4 + D-039/D-040](docs/contracts/analysis_plans.md). Acceptance: [P2-012 acceptance](docs/process/state_kernel.json). Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27). |
| Q8 | P2-046B | P1 Phase Gate | READY [QUIET-MAC] | Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts. | Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: [Hardening adjudication C6](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-046B acceptance](docs/process/state_kernel.json). Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution. |
| Q9 | P2-047B | P2 Next Slice | BLOCKED — P2-047A (frozen controller-overhead harness exists) [QUIET-MAC] | Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict. | Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047B acceptance](docs/process/state_kernel.json). |
| A0 | P2-035 | P3 Research Expansion | READY [AGENT] | RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests). | Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: [RQ-ENERGY-VARIANCE candidate design](docs/specs/rq_energy_variance_design.md). Acceptance: [P2-035 acceptance](docs/process/state_kernel.json). Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine). |
| A2 | QUIET-GUARD-01 | P1 Phase Gate | READY; GATES live_promotion: T3-CHAR-PAIR-01 [AGENT] | Quiet-guard work order (full gauntlet): host-wide quiet lease, refuse-at-arm, characterized resident watcher; plus Ed requirements recorded 2026-08-03 — t3-armed operation (a t3-launched claude session arms a detached guarded chain, then self-quits and quits t3 with a survivor inventory), t3-relaunch-on-close, and README-banner signaling. | The quiet guard lands through the full C-028 gauntlet with the host-wide lease, refuse-at-arm, characterized resident watcher, and all three Ed-required t3 behaviors working end to end. Evidence: Commit 1 only: host-wide quiet lease implemented and enforced; Refuse-at-arm: arming refuses when the host is not quiet (usable by the ordinary guarded-shell window launcher); Installed-INACTIVE: no arming path, no production lease, live_promotion=false; Seven focused-audit blockers closed (priv-esc interpreter, validate/install TOCTOU, arbitrary-root initializer, macOS process identity, boot/hostname wedge, decision entry, independently-pinned tests); Full gauntlet on the landed commit: independent audit + delta re-audit of every fix round. Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [QUIET-GUARD-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). ROW RE-SCOPED TO COMMIT 1 ONLY: the host-wide quiet lease + process census, installed-INACTIVE. Retained because it has non-t3 value — mechanical refuse-at-arm for the ordinary guarded window launcher, replacing procedural eyeballing. SHELVED: commit 2 (launcher interception), commit 3 (t3 handoff + resident watcher), commit 4 (t3-relaunch + README banner projection + all credential handling). In flight at checkpoint: Sol fix round closing 7 audit blockers; work UNCOMMITTED in scratchpad/quietguard (branch impl/quiet-guard); harvest scratchpad/qg-fix-out.md. |
| A3 | FLOOR-BIND-01 | P1 Phase Gate | READY [AGENT] | Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions. | Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: [D-078 clause 8 (confirmation round 9, registered limitation L1)](docs/decision_log.md). Acceptance: [FLOOR-BIND-01 acceptance](docs/process/state_kernel.json). Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed. |
| A4 | AXI-SB-ADAPTER | P2 Next Slice | READY [AGENT] | Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims. | The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: [AXI-SB verdict document (supported; mint-on-supported follow-on)](docs/specs/axi/sb_static_batch_verdict.md). Acceptance: [AXI-SB-ADAPTER acceptance](docs/process/state_kernel.json). Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership). |
| A5 | TEST-SPEED-01 | P2 Next Slice | READY [AGENT] | Cut suite wall-clock (three Ed-ratified levers, 2026-08-03): collect per-module timing data with the recovered profiling scripts, implement the shard-runner and the PR-fast/full tier split from the data, and evaluate Blacksmith runners. | The three Ed-ratified levers land: timing data drives a shard-runner plus PR-fast/full split with the full suite still holding every authoritative gate, and the Blacksmith runner option is evaluated on evidence. Evidence: Per-module timing corpus collected on a quiet bench (the recovered Sol profiling scripts; timings.jsonl + summary.json banked under .desk/) identifying the slow tail by module and by test; Shard-runner and the ratified PR-fast/full tier split implemented from the data: the fast tier gates PRs, the FULL suite remains the gate for merges, verdicts, and audited heads; zero test deletions; Blacksmith runner evaluation recorded with an adopt/defer recommendation and measured latency/cost comparison against GitHub-hosted runners. Authority: [Ed ratification 2026-08-03 (three levers: suite-speed priority, PR-fast/full split, Blacksmith runner evaluation); origin row in the 2026-07-28 report](docs/run_reports/2026-07-28-floor-mint-implementation.md). Acceptance: [TEST-SPEED-01 acceptance](docs/process/state_kernel.json). Fence: No test deletions, and the fast tier never substitutes for a required full-suite gate: merges, whole-window verdicts, and audited heads keep the full suite (D-061 zero-deletion clearance; the full suite as the authoritative gate). Note: 2026-08-03: timing DATA collected (quiet bench, 93 modules, 695s serial; raw in .desk/test-speed-consult/timings-20260803.jsonl) and DESIGN done (.desk/test-speed-consult/DESIGN-from-timing-data.md). Findings: suite is a 2-module problem (run_campaign 182s + p2038 133s = 45%); module-atomic sharding CAPS at 182s so those two must be split by TestCase class; shard-runner + splits -> ~87s wall @8 workers (6.5x); fast tier (drop 11 heavy integ modules) -> 25-40s PR feedback with the full suite still the merge gate. Blacksmith (lever 3) NEEDS ED (account/cost; likely marginal once sharded). Implementation queued: scripts/shard_tests.py + class-split + CI matrix — mechanical, delegatable, zero deletions (D-061). 2026-08-04: PHASE 1 LANDED — PR #98 MERGED (9b02539): module-atomic shard-runner + 8-way CI shard matrix, main CI green under it (~15min -> ~6min proven); worktree/branch pruned. Remaining scope: class-split of the two heavy modules (Phase 2), fast PR tier (lever 2), Blacksmith runners (lever 3, NEEDS ED). |
| A6 | AXI-SD | P2 Next Slice | READY [AGENT] | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
| A7 | AXI-SE | P2 Next Slice | READY [AGENT] | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
| A10 | SUPERSESSION-DUP-REFUSAL-01 | P1 Phase Gate | READY [AGENT] | Rule on and then implement write-time refusal in the supersession recorder, which today appends silent duplicate records when run more than once for a member and voids campaign membership downstream; the ruling is the first half of the deliverable. | A repeat recorder invocation for the same member refuses instead of appending a duplicate record. Evidence: The write-time refusal ruling is recorded in the decision log before any implementation; A regression asserts that a second recorder invocation for the same member refuses. Authority: [D-086 supersession-aware cooldown-evidence join (recorder duplicate-append defect)](docs/decision_log.md). Acceptance: [SUPERSESSION-DUP-REFUSAL-01 acceptance](docs/process/state_kernel.json). Fence: Until the refusal lands, run the supersession recorder exactly once per member (D-086 operator mitigation). Note: Minted 2026-07-30 from the D-086 arc; ruling-first, no implementation before it. |
| A11 | T3-PROV-SCHEMA-01 | P2 Next Slice | READY [AGENT] | Implement the tracked four-axis provenance record with authority_class and the ingestion-event schema, then make reverse-consult admission consume authoritative launch-route and owner_kind evidence so bridge §8's transitional convention ends. | The four-axis provenance plus ingestion-event schema ends bridge §8's transitional convention by mechanically enforcing reverse-consult eligibility from authoritative route and ownership evidence. Evidence: A tracked provenance record represents the four axes control_plane, transport, authority_class, and governance, with authority_class explicit; A tracked ingestion-event schema binds native session identity, output digest, lead disposition, and tracked process-trace location; Reverse-consult admission consumes authoritative launch-route and owner_kind evidence rather than self-reported headers; Rejection regressions fail closed on delegated, unknown, or contradictory provenance and prove that merely persisting the schema cannot end the transition. Authority: [Bridge protocol §8 transitional reverse-consult enforcement follow-on](docs/contracts/bridge_protocol.md). Acceptance: [T3-PROV-SCHEMA-01 acceptance](docs/process/state_kernel.json). Fence: The transition ends only when admission consumes authoritative launch-route and owner_kind evidence with rejection tests; defining or persisting the schema alone is insufficient (Bridge protocol §8 fail-closed transition rule). Note: Bridge §8 currently validates only self-reported headers; consumption-side fail-closed is the actual protection until this row supplies real enforcement. |
| A12 | MINT-GENERALIZE-01 | P1 Phase Gate | BLOCKED — D-110 (The remaining D-110 re-mint conditions hold before ANY further mint, including the governed 7B mint: (b) the acceptance artifact is ISSUED after verified R2 backfill and deterministic ledger bootstrap; (c) the evidence_root_id validator pin is widened) [AGENT] | Generalize the mint beyond the mint-1 pair: scripts/mint_floor_artifact.py is hard-pinned to the p2_015, a10, and window-C evidence (cell id, plan sha, both order-manifest ids, the two member counts, the expected operative-floor text), so build a sibling taking those pins per plan and carrying the 7B mint's remaining scope. | A generalized mint sibling takes the mint-1 hard pins per plan so a second floor artifact can be minted without weakening the pre-registration gate. Evidence: A 7B decode-floor artifact mints from qwen25_7b_decode_floor_v1 evidence with its own hard six-decimal operative-floor literal supplied per plan, never derived inside the mint path; The pre-registration gate passes as-embedded and validate_floor_artifact returns no findings; The generalized path mints byte-identical to the reviewed core from the same inputs on the same integration tree (core-vs-wrapper parity per D-109 addendum II; NOT a match against historical mint-1 digests, which D-110's corrected re-mint may legitimately change). Authority: [splitwise_decode_v1 campaign doc section 2 Blocker A (mint pins); D-082, D-084, D-085 Q6](docs/phase_2/splitwise_decode_campaign.md). Acceptance: [MINT-GENERALIZE-01 acceptance](docs/process/state_kernel.json). Fence: Generalize the plumbing, never the pins: six-decimal floor literals and lead-verified digests stay supplied per plan and hard-checked in-tool (D-082 and D-084 operative-floor pins). Note: 2026-08-03: D-110 (sweep finding RT-1/RT-2): mint #1 is retroactively NON-CLAIM-BEARING (taint-and-remint); the night consult's conditional 7B-mint license is SUSPENDED. The mint-1 byte-compare replay completed BYTE-IDENTICAL at pinned 3de370ec (all four digests; docs/process_traces/2026-08-03-q1-remint-bytecompare/). 2026-08-05: condition (a) is satisfied by merged PR #100. Condition (b) preparation is complete and its verification blocker is resolved: the B1 disposition is lead-ruled 30/2/6 and deterministic bootstrap is implemented on impl/ledger-bootstrap, under audit. Condition (c) is in flight on impl/validator-rootpins. The row remains hard-blocked on the still-pending D-110 (b)+(c) completion gate. |
| A13 | CODEX-BRIDGE-SANDBOX-01 | P2 Next Slice | READY [AGENT] | Correct scripts/codex-bridge review-mode sandbox enforcement: pass the read-only sandbox flag instead of launching workspace-write while recording read-only metadata. | codex-bridge review launches read-only exactly as its audit manifest claims, with regression coverage binding recorded and effective sandbox values. Evidence: scripts/codex-bridge review passes the read-only sandbox flag to every non-app review launch; The review audit manifest records the sandbox actually supplied to the launch; A regression proves the recorded review sandbox and launched sandbox are both read-only and cannot drift apart. Authority: [2026-08-05 live inspection: review records observer_sandbox=read-only but the non-app launch omits -s read-only](scripts/codex-bridge). Acceptance: [CODEX-BRIDGE-SANDBOX-01 acceptance](docs/process/state_kernel.json). Note: Caught live 2026-08-05: observer_sandbox is set to read-only, but the non-app review invocation omits the sandbox flag, so audit metadata misstates enforcement. |
| A14 | COLDGATE-HANDOFF-01 | P2 Next Slice | READY [AGENT] | Build runner-owned sealed-byte judge handoff: capture immutable in-process packet, charter, and exhibit byte snapshots; compute digests over those exact buffers; construct judge input from the same buffers; and specify and test transport byte-to-request binding. | The convening runner delivers exactly the bytes the validator observed, with immutable snapshot-to-judge transport binding and a judge-identity-bound runner receipt. Evidence: Deterministic post-hash path replacement delivers the original immutable snapshot or refuses without invoking the judge; Same-inode mutation through a second descriptor never delivers mutated bytes under the old receipt; Judge-received payload hashes equal the receipt hashes and the runner receipt binds the judge request or session identity. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 handoff ruling and tests](docs/process_traces/2026-08-05-cgv-f3-consult/CONSULT-REPORT.md). Acceptance: [COLDGATE-HANDOFF-01 acceptance](docs/process/state_kernel.json). Fence: Until this row lands, no validator PASS may be used to convene a cold judge (2026-08-05 F3 consult standing operational constraint). Note: Design warnings: holding file descriptors open does NOT seal bytes because a second descriptor can mutate the same inode; path-based launch-time revalidation alone leaves a revalidate-to-read race. Pending-ratification payload carried by this row: the proposed amendment to docs/process/coldgate_charter_registry.md separating validator observation from runner custody. The registry is Ed-ratified and is NOT edited by this or any session without a cold-gate/Ed ratification. |
| A15 | C3-RECOGNIZER-EXACT-01 | P1 Phase Gate | READY [AGENT] | Close the two D-105-registered recognizer-exactness blockers: exact escape-ordering completion-feasibility (F1) and the documented decidable superset number grammar (F2, with the D-104 cl.2 subset-direction amendment), plus the bundled F3/N2 release-path hygiene if not already landed. | The two registered recognizer-exactness blockers (escaped-key ordering; number-prefix over-acceptance) close together under D-105's refuter-amended criteria with an independent audit. Evidence: F1 closes via the exact escape-ordering completion-feasibility procedure (hex-digit interval derivation, surrogate-pair arithmetic, prefix-extension rule) with both registered counterexamples pinned verbatim and a BMP/non-BMP boundary property test; F2 closes via a DOCUMENTED DECIDABLE SUPERSET grammar of json.dumps float spellings (fixed-notation exponent window, coefficient rules, two-digit exponent padding) — the D-104 cl.2 subset direction is amended per D-105 to 'accepted within the documented superset AND containing every real writer prefix'; both counterexamples refuse; randomized-float completeness property passes; Both registered blockers close together with an independent delta audit at the exact head; the acceptance-set contract re-proven in both amended directions over a corpus including non-BMP keys. Authority: [D-105 disposition synthesis (F1/F2 registered as a NEW ruling, not D-088 precedent; closure criteria refuter-amended; number-grammar exactness struck)](docs/decision_log.md). Acceptance: [C3-RECOGNIZER-EXACT-01 acceptance](docs/process/state_kernel.json). Fence: F1/F2 severity may not be downgraded by any role; closure ONLY through this row; while open the recognizer's accepted set may only SHRINK; the custody sidecar and writer-side ASCII key assertion (the D-105 micro-commit) are load-bearing compensating controls and may not be weakened (D-105 registration fences). Fence: This registration must not be cited as precedent for registering corpus-absent defects generally; it is a new ruling made with three recorded independent absence scans and mechanical compensating controls (D-105: branch-introduced registration is NOT QA-10A/B precedent). |
| A16 | P3-000 | P3 Research Expansion | BLOCKED — R-003 (user approves the 3.0.2 installs (R-003)) [AGENT] | KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8). | Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: [D-035/D-036](docs/decision_log.md). Acceptance: [Phase 3 exit checklist](docs/phase_3/phase_3_exit_checklist.md). Note: 3.0.1 complete and merged (PR #9, replay_supported). |
| A17 | P2-022 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)) [AGENT] | Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported). | 3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [Adapter contract](docs/contracts/adapter_contracts.md). Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission. |
| A18 | P2-023 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded) [AGENT] | HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy. | Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [RQ bank import-smoke design](docs/research_question_bank.md). Fence: No pass@k, accuracy, or capability claim (D-041). |
| A19 | P2-024 | P2 Next Slice | BLOCKED — P2-006 (2M reductions identify floor/MDE headroom) [AGENT] | Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC]. | Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: [C-015 + RQ bank](docs/research_question_bank.md). Acceptance: [P2-024 acceptance](docs/process/state_kernel.json). |
| A21 | P3-001b | P3 Research Expansion | BLOCKED — P2-006 (2M affine coefficients exist) [AGENT] | Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049). | AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: [D-048/D-049](docs/decision_log.md). Acceptance: [Analysis plans (split row)](docs/contracts/analysis_plans.md). |
| A22 | P2-004 | P2 Next Slice | PARTIAL; READY; GATES close: P1-001 [AGENT] | Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding. | Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: [D-016](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Provisional small-model pick 2026-07-06 opens 2G. |
| A23 | P2-005 | P2 Next Slice | PARTIAL; READY; GATES live_promotion: P1-006 [AGENT] | Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute. | Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: [NV-GATE-2 live-promotion spec](docs/specs/c027/nv-gate-2_live_promotion.md). Acceptance: [2K live verification checklist](docs/phase_1/2k_live_verification_checklist.md). Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open. |
| A24 | P2-016 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists) [AGENT] | Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment. | Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: [C-011 ledger + C-027 (post-2M umbrella)](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-016 acceptance](docs/process/state_kernel.json). Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake. |
| A25 | P2-047A | P2 Next Slice | READY [AGENT] | Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes. | A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047A acceptance](docs/process/state_kernel.json). Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7). |
| A29 | DOC-008-REFLECTION | P4 Polish | READY [AGENT] | Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6. | Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence). |
| A30 | DOC-008-STATUS | P4 Polish | READY [AGENT] | Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8. | Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence). |
| A31 | DOC-008-INTAKE | P4 Polish | READY [AGENT] | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |
| A32 | DOC-008 | P4 Polish | PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS [AGENT] | Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked. | Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: [DOC-008 state-kernel specification](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 required outcomes](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live. |
| A33 | P2-050 | P3 Hardening Candidates | READY [AGENT] | Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2. | Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives its own adjudication; Semantic cooldown-row verification receives its own adjudication; Once-per-manifest first-run exemption receives its own adjudication; Scoped top-up detection and cooldown trace v2 receive their own adjudications. Authority: [C-028 dissent-record queue candidates](docs/run_reports/2026-07-11-c028-continuation.md). Acceptance: [P2-050 acceptance](docs/process/state_kernel.json). Fence: Do not implement any candidate before its own recorded adjudication (C-028 dissent-record queue candidates). |
| A34 | TOOL-01 | P3 Tooling | READY [AGENT] | Fix codex-run-v3 defects: resume-after-NEEDS_SCOPE no-op; preventive permission profiles; NEEDS_RULING recognition; effort-default passthrough; stream-death OK exits with thin out-files; resume --last cross-thread attachment through the global latest session; and session-open paths lacking per-path match specifiers. | All seven codex-run-v3 defects close in lead personal tooling with targeted regressions and updated adapter operations lessons. Evidence: Resume after NEEDS_SCOPE continues the requested work; Preventive permission profiles and NEEDS_RULING recognition are covered; Omitted effort defaults to xhigh instead of config passthrough; Upstream stream death fails instead of exiting OK with a thin out-file; Resume requires an explicit session ID and cannot cross-attach through a global --last pointer; Session-open accepts a per-path match specifier without post-hoc child expansion. Authority: [Bridge v1.1 wrapper and session operations record](docs/run_reports/2026-07-13-bridge-v11.md). Acceptance: [TOOL-01 acceptance](docs/process/state_kernel.json). Fence: Keep implementation in lead personal tooling; this repository owns only the work record (Bridge v1.1 wrapper and session operations record). Note: lead personal tooling, non-repo |
| A35 | AUD-FOLLOWUPS | P3 Hardening Candidates | READY [AGENT] | Close the ULTRA comparison audit's accepted small residue in one bounded agent task: WO-012's owned D-062 lint queue row, WO-014 realized-token discrimination, WO-017 default no-handoff regression, WO-020 standalone bridge-checker decision, and WO-040 authored-instruction absolute-path plus genuine pristine-clone coverage. | The ULTRA comparison audit's five accepted small follow-ups close with discriminating tests or an explicit recorded decision, without creating a ceremony-dispositions task. Evidence: WO-012's owned D-062 lint queue-row obligation is implemented and covered; WO-014 has a realized-token discriminating test; WO-017 has a default no-handoff regression assertion; WO-020 has a recorded standalone bridge-checker decision; WO-040 has authored-instruction absolute-path coverage plus a genuine pristine-clone test. Authority: [Comprehensive-audit close-out and accepted-residue list](docs/reviews/2026-07-13-comprehensive-audit/report.md). Acceptance: [AUD-FOLLOWUPS acceptance](docs/process/state_kernel.json). Fence: Do not create AUD-CEREMONY-DISPOSITIONS; ceremony dispositions remain report-owned (Comprehensive-audit report disposition ledger). Note: Accepted small residue only; audit ceremony dispositions remain in the report. |
| A36 | AUD-WO-033 | P3 Hardening Candidates | READY; GATES close: P2-006 [AGENT] | After 2M, split scripts/run_campaign.py along tested policy seams, pure validation and provenance first and execution lifecycle second, only when campaign-scale or split or multi-node work first forces edits to that path. | The post-2M campaign-runner refactor is behavior-preserving across the full campaign test portfolio and retains every collection and claim-readiness safeguard. Evidence: Pure validation and provenance seams are extracted before execution lifecycle seams; The full campaign behavior-parity portfolio is green before and after the split; Locks, waivers, backups, cooldown, and claim-readiness behavior remain unchanged. Authority: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Keep this post-2M and behavior-preserving; do not redesign campaigns or weaken locks, waivers, backups, cooldown, or claim-readiness gates (Comprehensive-audit register WO-033 non-goals and risk note). |
| A37 | AUD-WO-034 | P3 Hardening Candidates | READY; GATES close: PHASE-3-SPLIT-SCHEDULED [AGENT] | At Phase-3 split scheduling, assign bounded owners and dependencies for transfer-bench, split replay, composite validate and reduce, KV-economics reduction, and matrix-generator extension before any PLANNED command becomes executable. | When Phase-3 split work is scheduled, every PLANNED pack command gains an owner or explicit deferred marker without pack collapse or premature implementation. Evidence: Every PLANNED command has a bounded owner row or explicit deferred-design marker; Pack-command ownership lint passes positive and negative fixtures; Settled split pre-registration requirements and offline-before-live fences remain intact. Authority: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not prune draft designs, collapse campaign packs, or implement split or KV work in this ownership pass (Comprehensive-audit register WO-034 non-goals). |
| A38 | AUD-WO-035 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-TRANSFER-SCHEDULED [AGENT] | Before the first 2K-live or remote split-transfer task, define a versioned discriminated node-worker payload and test realistic typed rejection without overloading telemetry blocks. | The 2K-live and remote roadmap has a versioned transfer-task payload seam with typed rejection before split-transfer implementation. Evidence: A versioned discriminated payload path exists for transfer tasks; A realistic unsupported transfer request fails with a typed versioned error; Telemetry blocks are not overloaded with transfer semantics. Authority: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Define and reject the future transfer shape only; do not implement split execution or transfer benchmarking (Comprehensive-audit register WO-035 non-goals). Note: D-043 supersession closure falls due at landing: add the dated protocol-version supersession line identified by PA-2. |
| A39 | AUD-WO-036 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-CONCURRENCY-SCHEDULED [AGENT] | When 2K-live or remote retries or concurrency are introduced, add a pre-launch node and GPU ownership lease plus idempotent duplicate prepare and start behavior. | Retries or concurrent 2K-live and remote campaigns cannot double-own a node or GPU and duplicate delivery is idempotent. Evidence: Duplicate prepare and start delivery is idempotent; Node and GPU ownership is leased before launch; Concurrency coverage exercises the ownership and duplicate-delivery contract. Authority: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not run concurrent hardware campaigns or make live-correctness claims in this agent task (Comprehensive-audit register WO-036 non-goals). |
| A40 | AUD-WO-037 | P3 Hardening Candidates | READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED [AGENT] | Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path. | Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2. |
| A41 | AUD-WO-038 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED [AGENT] | At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition. | At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2. |
| A42 | AUD-WO-039 | P3 Hardening Candidates | PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED [AGENT] | At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review. | The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2. |
| A43 | CUSTODY-HARDEN-01 | P2 Next Slice | READY [AGENT] | Custody hardening follow-on from the screen+budget gauntlet: reduce-layer label-trust removal (G2A), drift-bound seal authentication (A3-r2), dead no-freshness accommodation disposition, artifact_schema_invalid mislabel. | Close the PR #85 gauntlet's deferred custody-hardening seams: config-derived mockness reaches the reduce-layer barriers, the drift-bound seal stops being self-certifying, and two diagnostic nits are resolved. Evidence: Reduce-layer environment/CPU claim barriers derive mockness from the custody-bound config, with metadata/summary-label early returns removed; Drift-bound artifact corpus identities resolve against repo-registered or custody-bound bytes (seal no longer self-certifying); Dead pre-addendum no-freshness accommodation removed or pinned as intentional forward-compatibility; artifact_schema_invalid evidence-binding mislabel renamed or documented at emission site. Authority: [C-045 gauntlet deferrals (council log; detail in docs/run_reports/2026-07-24-screen-budget-gauntlet.md)](docs/council_log.md). Acceptance: [CUSTODY-HARDEN-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from PR #85 gauntlet deferrals; triangle-agreement enforcement (merged) already raises these seams to three-file forgery cost. |
| A46 | FLOOR-WORKLOAD-SIZING-01 | P1 Phase Gate | READY [AGENT] | Re-size the floor/science campaign workloads so measured effects clear the duration-independent attribution floor, and pilot the resulting effect-to-floor ratio before spending quiet-machine nights on ABBA collection at current sizes. | Anchor-attribution error is approximately duration-independent (~1 J regardless of phase size) while effects scale with workload, so lengthening prefill/decode raises effect-to-floor linearly at zero instrument cost. Evidence: Measured effect-to-floor ratio at candidate workload sizes, from a pilot rather than assumption; Re-sized configs for the remaining floor stages, with the sizing rationale recorded; Explicit decision on which queued stages are collected at which sizes. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-WORKLOAD-SIZING-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25; scope corrected same day after the quantitative replay. NOT a blocker on the ABBA roadmap: under the labelled-floor path the queued stages remain scientifically viable at current sizes (tens-of-percent effects on ~50 J clear a ~3 J floor plus claim-side bound). This is a MARGIN optimisation — attribution error is duration-independent while effects scale with workload, so longer prefill/decode buys effect-to-floor ratio for free. Pilot the ratio at candidate sizes before committing the remaining quiet-machine nights. |
| A47 | FLOOR-COMMONMODE-01 | P2 Next Slice | READY [AGENT] | Pre-register and evaluate a common-mode anchor estimator for ABBA blocks: sweep one shared fiducial shift across all four members, re-integrate measured curves, and add only genuinely per-bundle components adversarially. | The fiducial term is ~80% of the composed anchor bound (24.9 of ~31.1 ms, verified) and is literally the same artifact for all four members of a block; treating it as four independent adversarial draws is itself an unphysical modelling choice. Evidence: Block-timescale fiducial stationarity registered as a NAMED transfer assumption with its evidence; Estimator pre-registered before it touches claim-bearing data; The identical estimator applied to BOTH the calibration blocks and the consuming science contrast (a floor calibrated with cancellation the consumer does not get would understate false effects); Quantified gain on a5/a10 blocks versus the worst-case-sum default. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-COMMONMODE-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25. Quantified same day on a5 decode ABBA (10 complete blocks): implemented worst-case-sum half-width gives a 6.46 J comparative floor; a common-mode proxy gives 2.13 J, a 3x improvement — material, but still above that cell's 0.60 J point floor, so it does not by itself restore extraction under the current gate. Value is in tightening the labelled floor, not in avoiding the label. Fiducial share of the composed bound measured at 80-87%. |
| A48 | PHASE-SHARE-ESTIMAND-01 | P2 Next Slice | READY [AGENT] | Investigate the anti-correlated prefill/decode boundary error: energy a shift removes from one phase it adds to the other, so the phase-share estimand has ONE boundary nuisance parameter whose joint envelope is a curve, not a box. | Treating each phase's anchor envelope as an independent box double-spends the shared interior boundary and inflates uncertainty on exactly the split/share quantity the Splitwise replication needs. Evidence: Determined whether _corner_composed_anchor_shift_envelope treats the shared interior boundary independently; Joint envelope over the single boundary-position parameter derived by re-integration sweep (measured-curve arithmetic only); Quantified effect on the phase-asymmetry claim envelope versus the independent-box treatment. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [PHASE-SHARE-ESTIMAND-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from the attribution-limit adjudication. Potentially the largest single win available for Splitwise sizing, at no instrument cost. |
| A49 | MODULARITY-01 | P3 Hardening Candidates | READY [AGENT] | Close the campaign-authoring modularity gap surveyed 2026-07-29: parameterize the campaign generator over a campaign-spec artifact and replace code-side literal assertions (analysis-manifest condition pairs, calibration scopes, phase-metric list) with registry-declared hash-validated sets. | Close the campaign-authoring modularity gap: campaign-spec-driven generation and registry-declared closed sets make every experiment axis swappable by config, per Ed's modularity directive. Evidence: Campaign generator is a parameterized function over a campaign-spec artifact (model, N, size profiles, block pattern, suite ref, run-ID prefix); a model swap touches one spec file and MODEL_TAG/PLAN_ID/run-ID prefixes derive from it with no parallel literal edits; Analysis-side closed sets (condition pairs, calibration scopes, phase-metric list) are declared in hash-bound registry artifacts and validated against those declarations, replacing the code-side literals at analysis_manifest.py:29-30,542-549 and detection_floor.py:87,89-95; Recorded-but-deferred residue dispositioned or re-queued: powermetrics references outside the adapter boundary, external-dataset ingestion, chat-template/thinking-mode seam, ABBA arity welded into three sites. Authority: [2026-07-29 modularity survey (Ed directive + per-axis grades)](docs/run_reports/2026-07-29-modularity-survey.md). Acceptance: [MODULARITY-01 acceptance](docs/process/state_kernel.json). Fence: Modularity applies to the harness, never to frozen claim pins: ratified hard literals (six-decimal pre-registration floor pins, lead-verified digests) stay anti-modular on purpose and must not be parameterized. (D-078 provenance amendment + D-079 operative-floor pins (hard literals are lead-verified, never parameterized)). Note: Minted 2026-07-29 from Ed's modularity directive. Survey verdict: runtime/telemetry Protocol layer and content-addressed provenance spine are already modular; the gap is campaign authoring above the adapter and literal assertions below the reader. Practical payoff lands with the planned Qwen3 cross-generation follow-up. |
| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
| A51 | NODE-CUSTODY-DEFAULT-01 | P3 Hardening Candidates | READY [AGENT] | Decide and implement whether the production DEFAULT_RETENTION_ROOT should be process/instance-unique: it currently is a fixed shared temp path (a latent collision hazard for genuinely concurrent clients), but making it unique conflicts with next-session custody reclamation. Resolve the tradeoff or record it as accepted. | Harden the production DEFAULT_RETENTION_ROOT against concurrent-client collision while preserving next-session custody reclamation (the NEEDS_RULING tradeoff deferred from NVIDIA-RETENTION-FLAKE-01). Evidence: The production DEFAULT_RETENTION_ROOT no longer collides for genuinely concurrent NodeClients sharing a scope, without breaking next-session custody reclamation (a later process must still locate the manifest it is entitled to reclaim); A regression proves two default-constructed clients in one process do not clobber each other AND that the documented reclamation contract still resolves the correct manifest across process boundaries; No retention/custody assertion is weakened; only root selection changes. Authority: [NVIDIA-RETENTION-FLAKE-01 fix report F1/F3 (PR #97): unique default roots close concurrent collision but conflict with next-session reclamation](docs/run_reports/2026-08-03-desk-session.md). Acceptance: [NODE-CUSTODY-DEFAULT-01 acceptance](docs/process/state_kernel.json). Fence: Isolation-only: do not weaken any retention/custody assertion; the reclamation contract's cross-process manifest resolution must survive any default-root change (NVIDIA-RETENTION-FLAKE-01 test-side fix (PR #97) already closed the flake). Note: Deferred 2026-08-03 from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake); the production hardening is a NEEDS_RULING tradeoff, non-blocking (no current concurrent-client scenario). |
## Mission M0: Preflight (every session)

1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
   if present, "Current Project Status", "Known Workspace State", and
   "What Is Next". If the stop card is ACTIVE, it overrides this
   playbook and the task queue until cleared.
2. Read `TASK_QUEUE.md`'s Current Queue and Do-Not-Do-Yet list.
3. Read the selected mission's own read-first list. Read `AGENT_PLAN.md`
   only at phase starts or when the project structure changes. Consult
   `docs/decision_log.md` by targeted decision ID, not as a whole-file
   intake step.
   If the session involves delegation, review, or multi-stream work, also
   read `docs/orchestration.md` (the process layer) — not optional for
   landing code.
4. Check workspace state with `git status --short --branch`; inspect
   recent commits only when the handoff or mission needs them.
5. `python3 -m unittest discover -s tests` — expect `Ran <N> tests` (N per `RUN_STATE.md` Current Verification; `, OK
   (skipped=10)` with zero expected failures as of 2026-07-08 after
   P2-013/P2-014 and the C-011 rigor mechanics. The skips are the `[analysis]`-extra chart tests plus one
   optional-jsonschema test. A red suite is itself the mission: stop and fix
   or report.
6. Review `docs/risk_register.md` at phase starts, before hardware tasks,
   when a trigger fires, or if >14 days passed since the last run report
   with no break recorded in `docs/milestones.md`.
7. At session end, always: update `RUN_STATE.md`, update `TASK_QUEUE.md`,
   write a dated run report in `docs/run_reports/`, update the phase exit
   checklist for anything that closed, and `PROJECT_STATUS.md` if
   advisor-visible state changed. Commit when the user asks or has
   standing-approved it.

Environment cautions:

- The repo must stay at a non-iCloud path (`~/code/...`; R-017). If you
  see `Operation not permitted` on reads inside the repo, stop, wait for
  the lock to clear, re-run the suite, and record the incident.
- CI installs no extras; every new test must pass on a bare Python
  (lazy imports, `skipUnless` for optional deps — D-009).
- Schema changes are additive-only until v0.2 (R-015/D-008).

---

## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)

**Gate:** none. **Spec + acceptance:** `docs/phase_2/phase_2_plan.md`
Slice 2N. This mission adds the code-level route for each work item,
sourced from the 2026-07-05 external code review. Line numbers are from
commit `ae48abe` — re-locate by symbol name if the files have moved on.

Read first: `phase_2_plan.md` Slice 2N + Cross-Slice Contracts;
`joulewise/bundle.py`, `controller.py`, `reduce.py`, `interfaces.py`
(skim whole files — they are small and the invariants interlock).

2N is one mission but NOT one sitting: it touches adapter interfaces,
controller timing, reducer behavior, report parsing, CLI, schema export,
and validation policy. Work item-by-item with the suite green after each,
and land it as roughly three commits so a failure bisects cleanly:

exec
/bin/zsh -lc "sed -n '1,120p' docs/paper/draft-v1.md; sed -n '121,240p' docs/paper/draft-v1.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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
/bin/zsh -lc "rg -n '"'^## .*D-117|''^### .*D-117|D-117'"' docs/decision_log.md | tail -30; sed -n '1,220p' CLAIMS_STATUS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
7084:> **2026-08-07 supersession (D-117):** clause 3's historical re-mint
7088:> allowance correction STAND and bind the D-117 mints.
7249:> **2026-08-07 amendment (D-117 cl.4):** the readiness dependency on
7507:## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired
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

exec
/bin/zsh -lc "sed -n '7507,7585p' docs/decision_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired

**Date:** 2026-08-07 (Ed directive, in-thread; transcribed by the Fable
magistrate. Ed, verbatim: "if i recall for a paper ready at the quality
needed we need 3 more machine quiet nights and a lot of desk work",
with an explicit go to "execute all the deskwork" — read together with
his 2026-08-06 in-thread MVP-scope directive "a little more than just
decode, at least decode/prefill". His ruling moots a cold gate: apex
authority per rule 11.)
**Status:** ADOPTED. Full technical record:
`docs/process_traces/2026-08-06-d110-remint-fork/` (DIAGNOSIS: the
structural closure live-reproduced at `c537386`; Sol xhigh consult run
`20260806T165843Z-10884`; SYNTHESIS: magistrate concurrence).

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
/bin/zsh -lc "sed -n '1,180p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md; sed -n '181,360p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md; sed -n '361,540p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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
/bin/zsh -lc "sed -n '1,260p' docs/strategy/2026-08-06-impressiveness-roadmap.md; sed -n '1,180p' docs/research_question_registry.md; sed -n '1,120p' docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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
/bin/zsh -lc "sed -n '1,115p' docs/strategy/2026-08-06-impressiveness-roadmap.md; sed -n '116,240p' docs/strategy/2026-08-06-impressiveness-roadmap.md; sed -n '1,75p' docs/research_question_registry.md; sed -n '76,160p' docs/research_question_registry.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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

exec
/bin/zsh -lc "sed -n '1,70p' docs/research_question_registry.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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

exec
/bin/zsh -lc "sed -n '71,160p' docs/research_question_registry.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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
The frozen plan makes one portfolio constraint decisive: the three D-117 windows already consume about 9.2 quiet hours and produce four phase-floor cells plus the large decode contrast. I’m now looking for extensions that reuse those exact bundles or require at most one additional, independently calibrated window—anything needing a new telemetry boundary or an unobservable mechanism is being screened out early.
exec
/bin/zsh -lc "sed -n '1,250p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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

exec
/bin/zsh -lc "sed -n '251,500p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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

exec
/bin/zsh -lc "sed -n '501,750p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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

exec
/bin/zsh -lc "sed -n '751,1000p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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

exec
/bin/zsh -lc "sed -n '1001,1160p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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
/bin/zsh -lc "rg --files joulewise scripts configs docs results tests | sed -n '1,240p'; rg -n \"joint envelope|phase.share|phase_share|shared interior|common.mode|micro.delta|linearity|additivity|wall meter|WT310|q4_l3|fixed.*marginal|refusal log|refusal\" docs configs joulewise scripts results tests | head -400" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
rg: results: No such file or directory (os error 2)
configs/floor_mint/a10_extraction_spec.json
configs/floor_mint/window_c_extraction_spec.json
configs/floor_mint/condition_family_df_ph_decode.json
configs/analysis_registry/slice_2m_ap2.v1.json
configs/analysis_registry/ap_spec_native_mtp_front.v2.json
configs/analysis_registry/ap_spec_draft_front.v2.json
scripts/backup_runs.sh
scripts/extract_detection_floors.py
scripts/claude-bridge-mcp.mjs
scripts/calibration_ledger_bootstrap.py
scripts/quiet_mac_prep.sh
scripts/axi_sc_spec_decode_spike.py
scripts/codex-run
scripts/run_campaign.py
scripts/test_timings.json
scripts/mint_floor_artifact.py
scripts/characterize_load_transition.py
scripts/build_site.py
scripts/reconcile_retained_powermetrics.py
scripts/validate_powermetrics_fiducial.py
scripts/shard_tests.py
scripts/gen_jw_mixed.py
scripts/quiet_guard.py
scripts/setup_quiet_guard.sh
scripts/check-codex-mcp.mjs
scripts/validate_gate_packet.py
scripts/generate_matrix.py
scripts/corpus_compat_receipt.py
scripts/codex-app-bridge.mjs
joulewise/validation.py
joulewise/quiet_guard_process.py
joulewise/report.py
joulewise/powermetrics_fiducial.py
joulewise/__main__.py
joulewise/doctor.py
joulewise/provenance.py
joulewise/floor_extraction.py
docs/phase_1/phase_1_exit_checklist.md
docs/phase_1/phase_1_plan.md
docs/phase_1/2k_live_verification_checklist.md
scripts/floor_mint_pinsets/mint1.json
scripts/floor_reconciliation_receipt.py
scripts/gen_affine_smoke.py
scripts/axi_sb_static_batch_spike.py
scripts/make_figures.py
scripts/quiet_guard_privileged.py
scripts/release_check.py
scripts/bridge
scripts/quiet_window_clock.sh
scripts/calibration_ledger_backfill.py
scripts/package_bundle_pack.py
scripts/claims_lint.py
scripts/spike_mlx_prompt_cache.py
scripts/pack_capsule.py
scripts/gen_state.py
scripts/prewindow_check.sh
scripts/build_capstone.py
scripts/codex-bridge
scripts/check_sealed_bundle_compatibility.py
scripts/mint_floor_artifact_generalized.py
scripts/window_status.sh
joulewise/clock.py
joulewise/whole_window.py
joulewise/workloads.py
joulewise/calibration_bracketing.py
joulewise/bundle_read.py
joulewise/analysis_manifest.py
joulewise/analysis_manifest_v3.py
joulewise/reduce.py
joulewise/envelope_gate.py
joulewise/output_identity.py
joulewise/suite.py
joulewise/controller.py
joulewise/idle_dependence.py
joulewise/publication_privacy.py
joulewise/campaign_provenance.py
joulewise/aggregate.py
joulewise/bundle.py
joulewise/interfaces.py
joulewise/determinism_gate.py
joulewise/quiet_guard.py
docs/strategy/2026-08-06-impressiveness-roadmap.md
joulewise/gensuite/__init__.py
joulewise/environment_admission.py
joulewise/environment.py
joulewise/uncertainty_evidence.py
joulewise/idle_admission.py
joulewise/salvage_dangler.py
joulewise/cli.py
joulewise/detection_floor.py
joulewise/schemas.py
joulewise/calibration_ledger.py
tests/test_axi_mock_spec.py
tests/test_cli_run.py
tests/test_2k_amplification.py
tests/test_experiment.py
tests/test_d078_reason_registry.py
tests/test_corpus_strict_validation.py
tests/test_publication_privacy.py
tests/test_mlx_runtime.py
tests/test_analysis_integration.py
tests/test_calibration_ledger.py
tests/test_detection_floor.py
tests/test_env_locks.py
tests/test_powermetrics_fiducial.py
tests/test_mint_floor_artifact_generalized.py
tests/test_node_client.py
tests/test_analysis_claims.py
tests/test_audit_powermetrics_parser.py
tests/test_package_bundle_pack.py
tests/test_docs_freshness.py
tests/test_audit_cli_examples.py
tests/test_analysis_multiplicity.py
tests/test_axi_analysis_manifest.py
tests/test_uncertainty_evidence.py
tests/test_floor_extraction.py
tests/test_rpt001_report_slice.py
tests/test_audit_reduce_degenerate.py
tests/test_bundle_read.py
tests/test_suite_control_parity.py
tests/test_envelope_gate.py
tests/test_adapters_powermetrics.py
tests/test_salvage_dangler.py
tests/test_claims_index_lint.py
tests/test_p2038_production_path.py
tests/test_analysis_manifest_v3.py
tests/test_vllm_runtime.py
tests/test_whole_window.py
tests/test_node_worker_subprocess.py
tests/test_gen_state.py
tests/test_powermetrics.py
tests/test_audit_schema_edges.py
tests/test_build_site_parsers.py
tests/test_nvidia_smi.py
tests/test_codex_bridge_observer.py
tests/test_bundle.py
tests/test_idle_dependence.py
tests/test_axi_schemas.py
tests/test_claims_lint.py
tests/test_claude_bridge_mcp.py
tests/test_node_worker.py
tests/test_audit_amplification.py
tests/test_idle_admission.py
tests/test_report.py
tests/test_analysis_ratio_integration.py
tests/test_codex_app_bridge.py
tests/test_whole_window_selection.py
tests/test_axi_controller_events.py
tests/test_doctor.py
tests/test_run_campaign.py
tests/test_load_transition_alignment.py
tests/test_schemas.py
tests/test_controller.py
tests/test_calibration_bracketing.py
tests/test_workloads.py
tests/verify_calibration_acceptance_corpus.py
tests/test_environment.py
tests/test_mint_floor_artifact.py
tests/test_ssh_transport.py
tests/test_axi_sb_spike.py
tests/test_axi_sc_spike.py
tests/test_audit_clock.py
tests/test_bridge.py
tests/test_pack_capsule.py
tests/test_mock_adapters.py
tests/test_uncertainty_p2029.py
tests/test_audit_report.py
tests/test_cli.py
tests/test_clock.py
tests/test_generate_matrix.py
tests/test_analysis_engine.py
tests/test_axi_output_identity.py
tests/test_validate_gate_packet.py
tests/test_rpt002_related_work.py
joulewise/adapters/mock_telemetry.py
configs/campaigns/p2_015_floors/10_df_telem_onoff_unavailable/README.md
joulewise/adapters/local_transport.py
joulewise/adapters/ssh_transport.py
joulewise/adapters/suite_control.py
joulewise/adapters/mock_runtime.py
joulewise/adapters/node_client.py
joulewise/adapters/__init__.py
joulewise/adapters/powermetrics.py
joulewise/adapters/nvidia_smi.py
joulewise/adapters/vllm_runtime.py
joulewise/adapters/mock_spec_runtime.py
joulewise/adapters/node_worker.py
joulewise/adapters/mlx_runtime.py
joulewise/kv_size.py
joulewise/axi_decode_config.py
joulewise/cooldown_anchor.py
joulewise/load_transition_alignment.py
docs/reviews/2026-07-11-p2044-design-consult.md
docs/reviews/2026-07-10-hardening-adjudication.md
docs/reviews/2026-07-09-c027-whole-project-review.md
configs/campaigns/p2_015_floors/11_neg8_end/p2015-neg8-reference-end.json
configs/campaigns/p2_015_floors/11_neg8_end/order_manifest.json
configs/campaigns/p2_015_floors/calibration_plan.json
configs/campaigns/p2_015_floors/backup_icloud.sh
configs/campaigns/p2_015_floors/order_manifest.json
configs/campaigns/p2_015_floors/generate_configs.py
tests/fixtures/state_kernel/selection_semantics.json
tests/fixtures/state_kernel/cleared_audit_gate.json
tests/fixtures/state_kernel/historical_audit_gate.json
joulewise/analysis_engine/multiplicity.py
joulewise/analysis_engine/estimators.py
joulewise/analysis_engine/inputs.py
joulewise/analysis_engine/distributions.py
joulewise/analysis_engine/sensitivity.py
joulewise/analysis_engine/__init__.py
joulewise/analysis_engine/claims.py
joulewise/analysis_engine/registry.py
joulewise/analysis_engine/artifact.py
joulewise/analysis_engine/ratio.py
joulewise/__init__.py
joulewise/cooldown.py
tests/test_reduce.py
tests/test_nvidia_node_integration.py
tests/test_sealed_bundle_compatibility.py
tests/test_gensuite.py
tests/test_axi_request_validation.py
tests/test_quiet_guard_process.py
tests/test_audit_bundle_validation.py
tests/test_aggregate.py
tests/test_kv_size.py
tests/test_suite.py
tests/test_microdelta_generate_configs.py
tests/goldens/legacy_reducer_041.provenance.json
tests/goldens/d078_r01_reducer_052.json
tests/goldens/axi_controller_request_events.jsonl
tests/goldens/axi_summary_v061.json
tests/goldens/axi_dispatch_receipt_failed.json
tests/goldens/legacy_reducer_042.patch.json
tests/goldens/axi_decode_emission.json
tests/goldens/mock_axi_spec_request_tokens.jsonl
tests/goldens/axi_summary_v060.json
tests/goldens/config_schema.json
tests/goldens/axi_request_row.json
tests/goldens/output_identity_exact.json
tests/goldens/legacy_reducer_050.patch.json
rg: results: No such file or directory (os error 2)
scripts/extract_detection_floors.py:11:  evidence refusals are recorded per member/cell, never silently dropped);
scripts/extract_detection_floors.py:166:        row["bundle_id"] for row in report.get("spec_membership_refusals", [])
docs/phase_1/phase_1_exit_checklist.md:332:  nvidia-smi, optional wall meter. Transport: ssh.
docs/phase_1/phase_1_exit_checklist.md:355:  INA3221 rails preferred, `tegrastats` fallback, wall meter last resort
joulewise/quiet_guard_process.py:8:observation failure after acceptance is a refusal.
docs/phase_1/phase_1_plan.md:196:record whether energy could be measured (wall meter) even if the runtime
tests/test_controller.py:1640:            _window_thermal_pressure_refusals,
tests/test_controller.py:1736:            _window_thermal_pressure_refusals(
tests/test_controller.py:2686:        data["run_id"] = "tail-subsecond-refusal"
tests/test_controller.py:2697:        self.assertFalse((self.runs_root / "tail-subsecond-refusal").exists())
scripts/quiet_mac_prep.sh:12:# 1. Power state (no wall meter needed for P2-038/floors; AC is required).
tests/test_calibration_bracketing.py:273:        refusal_reasons=(),
tests/test_calibration_bracketing.py:349:            refusal_reasons=(),
tests/test_calibration_bracketing.py:527:            refusal_reasons=("calibration_ledger_head_mismatch",),
tests/test_calibration_bracketing.py:694:            self.assertEqual(snapshot.refusal_reasons, ())
docs/strategy/2026-08-06-impressiveness-roadmap.md:110:That is the critical path. A broad paper with incomplete C1–C6 evidence will look less serious than a narrower paper that cleanly demonstrates linearity, null response, empirical floor behavior, additivity, drift/settling, and between-session stability.
docs/strategy/2026-08-06-impressiveness-roadmap.md:156:| **1** | **Complete C1–C7 cleanly: remint, fresh C/D, and stability** | Converts the strongest idea—the instrument and its refusal behavior—into actual evidence. This is the difference between an elaborate methodology and a metrology paper. | **3–6 weeks after desk gates; 2 mandatory nights plus 1 contingency/short stability session.** | D-079 issued artifact; D-110 remint; reviewed frozen-plan record; fresh §5A; C/D split if scope cannot fit. Risk: another environmental or clock refusal. | Reserve the core nights now and prohibit breadth work from consuming them. |
docs/strategy/2026-08-06-impressiveness-roadmap.md:158:| **3** | **Artifact-evaluation-quality release** | Hash-bound raw-to-figure reproducibility is a genuine differentiator and unusually well aligned with JouleWise’s thesis. Reviewers can verify refusals and re-derive results rather than trust screenshots. | **4–6 weeks; 0 measurement nights.** | Sanitized raw-bundle subset, one-command validation/reduction/figure path, locked environment, quick/full tracks, immutable archive/DOI, clear hardware-free replay. Risk: privacy, dataset size, and Mac-only collection requirements. | Decide whether the target is merely open source or formal ICPE-style artifact evaluation, and which evidence may be public. |
docs/strategy/2026-08-06-impressiveness-roadmap.md:159:| **4** | **Designed workload-shape matrix with held-out prediction—Q4/L3** | A predictive fixed-plus-marginal model validated on held-out cells is substantially more serious than “we ran more prompts.” It can earn L3 rather than another collection of L1/L2 points. | **6–10 weeks; approximately 2–3 nights.** | P2-006 baseline sizing, AP-1, 4×3 grid, predeclared holdouts, residual/sensitivity analysis, floor audit. Risk: the simple model may fail its holdouts—which must be reported honestly. | Fund the full designed matrix or omit the predictive claim; do not replace it with opportunistic workload breadth. |
docs/strategy/2026-08-06-impressiveness-roadmap.md:166:For the wall-meter path, the right class is a calibrated bench AC power analyzer, not an inexpensive consumer plug. A concrete baseline is the Yokogawa WT310E: its manufacturer lists 10 readings/s, USB export, 0.1%-of-reading plus 0.05%-of-range basic accuracy, high crest-factor capability, and a **$2,935 base US price** before calibration/fixture costs. Actual suitability still depends on calculating uncertainty at the Mac’s observed load and using a safe inline fixture. Borrowing an in-calibration unit from an engineering lab is preferable to spending several thousand dollars. [Yokogawa WT310E specifications and current price](https://tmi.yokogawa.com/us/solutions/products/power-analyzers/digital-power-meter-wt300e/).
joulewise/floor_extraction.py:96:    whole_window_refusal_reasons,
joulewise/floor_extraction.py:101:    current_environment_refusals,
joulewise/floor_extraction.py:102:    environment_admission_refusals,
joulewise/floor_extraction.py:152:# refusal merely because the legacy container name says "refusal".
joulewise/floor_extraction.py:213:    if not consumption_session.refusal_reasons:
joulewise/floor_extraction.py:722:    refusal_reasons: tuple[str, ...]
joulewise/floor_extraction.py:733:            and set(self.refusal_reasons) == set(CELL_LABELLED_CONDITION_CODES)
joulewise/floor_extraction.py:739:    def terminal_refusal_reasons(self) -> tuple[str, ...]:
joulewise/floor_extraction.py:742:            reason for reason in self.refusal_reasons if reason not in conditions
joulewise/floor_extraction.py:747:        return not self.terminal_refusal_reasons and self.floor is not None
joulewise/floor_extraction.py:814:            "refusal_reasons": list(self.terminal_refusal_reasons),
joulewise/floor_extraction.py:858:    refusals: Sequence[str],
joulewise/floor_extraction.py:863:        and set(refusals) == set(CELL_LABELLED_CONDITION_CODES)
joulewise/floor_extraction.py:946:    reasons = set(environment_admission_refusals(admission))
joulewise/floor_extraction.py:956:                current_environment_refusals(
joulewise/floor_extraction.py:1078:            if consumption_session.refusal_reasons:
joulewise/floor_extraction.py:1079:                reasons.extend(consumption_session.refusal_reasons)
joulewise/floor_extraction.py:1083:                # Local refusals never take this arm: they preserve readiness
joulewise/floor_extraction.py:1189:            # A claim-bearing pin that cannot be computed is a refusal, never a
joulewise/floor_extraction.py:1313:    refusals: list[str] = []
joulewise/floor_extraction.py:1339:            refusals.extend(fatal)
joulewise/floor_extraction.py:1346:    if not refusals:
joulewise/floor_extraction.py:1348:            refusals.append("insufficient_members_after_exclusion")
joulewise/floor_extraction.py:1349:            refusals.extend(fallback_exclusion_diagnostics)
joulewise/floor_extraction.py:1363:                refusals.append(
joulewise/floor_extraction.py:1375:                refusals.append(
joulewise/floor_extraction.py:1379:    attribution_limited = _sole_attribution_limit(refusals, floor)
joulewise/floor_extraction.py:1391:            if not refusals or attribution_limited
joulewise/floor_extraction.py:1394:        refusal_reasons=tuple(sorted(dict.fromkeys(refusals))),
joulewise/floor_extraction.py:1399:            if not refusals or attribution_limited
joulewise/floor_extraction.py:1448:    refusals: list[str] = []
joulewise/floor_extraction.py:1499:            refusals.extend(block_fatal)
joulewise/floor_extraction.py:1519:    if not refusals:
joulewise/floor_extraction.py:1521:            refusals.append("insufficient_members_after_exclusion")
joulewise/floor_extraction.py:1522:            refusals.extend(fallback_exclusion_diagnostics)
joulewise/floor_extraction.py:1534:                refusals.append(
joulewise/floor_extraction.py:1546:                refusals.append(
joulewise/floor_extraction.py:1550:    attribution_limited = _sole_attribution_limit(refusals, floor)
joulewise/floor_extraction.py:1562:            if not refusals or attribution_limited
joulewise/floor_extraction.py:1565:        refusal_reasons=tuple(sorted(dict.fromkeys(refusals))),
joulewise/floor_extraction.py:1568:            if not refusals or attribution_limited
joulewise/floor_extraction.py:1625:    whole_window_refusals = _whole_window_extraction_refusals(
joulewise/floor_extraction.py:1634:        if consumption_session.ready or consumption_session.refusal_reasons
joulewise/floor_extraction.py:1690:    if not whole_window_refusals:
joulewise/floor_extraction.py:1704:    if whole_window_refusals:
joulewise/floor_extraction.py:1708:                refusal_reasons=tuple(
joulewise/floor_extraction.py:1709:                    sorted(set(report.refusal_reasons) | set(whole_window_refusals))
joulewise/floor_extraction.py:1724:                refusal_reasons=tuple(
joulewise/floor_extraction.py:1726:                        set(report.refusal_reasons)
joulewise/floor_extraction.py:1789:    spec_membership_refusals = [
joulewise/floor_extraction.py:1847:        "spec_membership_refusals": spec_membership_refusals,
joulewise/floor_extraction.py:1848:        "idle_admission_refusals": list(whole_window_refusals),
joulewise/floor_extraction.py:1859:            and not spec_membership_refusals
joulewise/floor_extraction.py:1867:def _whole_window_extraction_refusals(
joulewise/floor_extraction.py:1877:    return whole_window_refusal_reasons(
tests/test_mint_floor_artifact.py:569:            refusal_reasons = ()
tests/test_mint_floor_artifact.py:570:            path_refusal_reasons = {}
tests/test_mint_floor_artifact.py:581:                "whole_window_refusal_reasons",
tests/test_mint_floor_artifact.py:717:            "spec_membership_refusals": [],
tests/test_mint_floor_artifact.py:718:            "idle_admission_refusals": [],
tests/test_mint_floor_artifact.py:726:                    "refusal_reasons": [],
tests/test_mint_floor_artifact.py:880:            "spec_membership_refusals": [],
tests/test_mint_floor_artifact.py:881:            "idle_admission_refusals": [],
tests/test_mint_floor_artifact.py:889:                    "refusal_reasons": [],
tests/test_mint_floor_artifact.py:944:    def test_authenticated_replay_does_not_import_prefill_refusal(
tests/test_mint_floor_artifact.py:949:            refusal_reasons: tuple[str, ...] = ()
tests/test_mint_floor_artifact.py:950:            path_refusal_reasons = {
tests/test_mint_floor_artifact.py:975:                mint, "whole_window_refusal_reasons", return_value=()
tests/test_mint_floor_artifact.py:997:            refusal_reasons: tuple[str, ...] = ()
tests/test_mint_floor_artifact.py:998:            path_refusal_reasons = {
tests/test_mint_floor_artifact.py:1023:                mint, "whole_window_refusal_reasons", return_value=()
scripts/run_campaign.py:163:    current_environment_refusals,
scripts/run_campaign.py:164:    post_run_environment_refusals,
scripts/run_campaign.py:3787:def _current_member_environment_refusals(
scripts/run_campaign.py:3812:    return current_environment_refusals(
scripts/run_campaign.py:4149:        current_environment_reasons = _current_member_environment_refusals(evaluation)
scripts/run_campaign.py:4161:                    post_run_environment_refusals(evaluation.metadata)
scripts/run_campaign.py:5230:                + ", ".join(consumption_session.refusal_reasons)
scripts/run_campaign.py:5485:        current_environment_reasons = _current_member_environment_refusals(evaluation)
scripts/run_campaign.py:5491:            reasons.update(post_run_environment_refusals(evaluation.metadata))
scripts/run_campaign.py:5692:    """Map the advisory core surface onto claim-bearing refusal reasons."""
docs/reviews/2026-07-10-hardening-adjudication.md:41:| Detection-floor artifact | Landed in PR #45: versioned artifact, guarded and unguarded floors, ABBA deltas, exact identities, transport refusal, provenance validation. | Real calibration bundles and automatic consumption by an eligible real claim remain unexecuted. |
docs/reviews/2026-07-10-hardening-adjudication.md:85:| 9 | **P2-048 — External-meter importer and bridge CLI** | `[AGENT]`, P2 conditional on P1-003 | Implement the already-designed Q6 artifact/import format and `boundary-calibrate`; bind meter metadata, synchronization, paired windows, slope/intercept, residuals, held-out gate, floor identity, and refusal reasons. The design itself should not be duplicated. |
joulewise/environment_admission.py:42:def post_run_environment_refusals(metadata: Any) -> tuple[str, ...]:
joulewise/environment_admission.py:116:def current_environment_refusals(
joulewise/environment_admission.py:131:        environment_admission_refusals(admission, require_attempt_timing=True)
joulewise/environment_admission.py:133:    reasons.update(_recomputed_environment_evaluation_refusals(metadata))
joulewise/environment_admission.py:195:    reasons.update(post_run_environment_refusals(metadata))
joulewise/environment_admission.py:197:        _window_thermal_pressure_refusals(
joulewise/environment_admission.py:231:def _recomputed_environment_evaluation_refusals(metadata: Any) -> tuple[str, ...]:
joulewise/environment_admission.py:264:def _window_thermal_pressure_refusals(
joulewise/environment_admission.py:383:def environment_admission_refusals(
scripts/mint_floor_artifact.py:56:    whole_window_refusal_reasons,
scripts/mint_floor_artifact.py:529:    reasons = whole_window_refusal_reasons(
scripts/mint_floor_artifact.py:542:            target_reasons = session.path_refusal_reasons.get(
scripts/mint_floor_artifact.py:641:        or cell.get("refusal_reasons") not in ([], ())
scripts/mint_floor_artifact.py:1048:        report.get("spec_membership_refusals") not in ([], ())
scripts/mint_floor_artifact.py:1049:        or report.get("idle_admission_refusals") not in ([], ())
scripts/mint_floor_artifact.py:1051:        raise MintError("extraction report carries global refusal records")
tests/test_pack_capsule.py:493:            "emitted pages.ts roundtrip and corruption refusal verified"
joulewise/salvage_dangler.py:34:LAUNCHER_REFUSAL_SCHEMA = "joulewise.salvage_launcher_refusal.v1"
joulewise/salvage_dangler.py:846:def inspect_launcher_refusal(
joulewise/salvage_dangler.py:847:    refusal: Mapping[str, Any], custody_roots: Sequence[str | Path]
joulewise/salvage_dangler.py:849:    """Validate D-100 b-i: a hash-sealed refusal and no occurrence bytes."""
joulewise/salvage_dangler.py:851:    payload = {key: value for key, value in refusal.items() if key != "record_sha256"}
joulewise/salvage_dangler.py:861:        or not isinstance(payload.get("refusal_code"), str)
joulewise/salvage_dangler.py:862:        or not payload.get("refusal_code")
joulewise/salvage_dangler.py:863:        or refusal.get("record_sha256") != _canonical_sha256(payload)
joulewise/salvage_dangler.py:865:        raise SalvageAuthorizationError("launcher refusal record is malformed")
joulewise/salvage_dangler.py:868:        raise SalvageAuthorizationError("launcher refusal record is malformed")
joulewise/salvage_dangler.py:876:        raise SalvageAuthorizationError("launcher refusal custody universe is empty")
joulewise/salvage_dangler.py:878:        raise SalvageAuthorizationError("launcher refusal custody universe has duplicates")
joulewise/salvage_dangler.py:958:        "license_branch": "launcher_refusal_zero_bytes",
joulewise/salvage_dangler.py:959:        "refusal_code": payload["refusal_code"],
joulewise/salvage_dangler.py:964:        "license_branch": "launcher_refusal_zero_bytes",
joulewise/salvage_dangler.py:968:        "refusal_record": dict(refusal),
joulewise/salvage_dangler.py:1063:    has_launcher_refusal = any(
joulewise/salvage_dangler.py:1065:        and occurrence.get("license_branch") == "launcher_refusal_zero_bytes"
joulewise/salvage_dangler.py:1097:    if has_launcher_refusal:
joulewise/salvage_dangler.py:1167:        elif branch == "launcher_refusal_zero_bytes":
joulewise/salvage_dangler.py:1168:            refusal_path_text = occurrence.get("launcher_refusal_path")
joulewise/salvage_dangler.py:1169:            if not isinstance(refusal_path_text, str) or not refusal_path_text:
joulewise/salvage_dangler.py:1171:                    "closure launcher refusal path is missing"
joulewise/salvage_dangler.py:1173:            refusal_path = Path(refusal_path_text)
joulewise/salvage_dangler.py:1174:            if refusal_path.is_symlink():
joulewise/salvage_dangler.py:1176:                    "closure launcher refusal path is a symlink"
joulewise/salvage_dangler.py:1179:                refusal_path = refusal_path.resolve(strict=True)
joulewise/salvage_dangler.py:1180:                if not stat.S_ISREG(refusal_path.lstat().st_mode):
joulewise/salvage_dangler.py:1182:                        "closure launcher refusal is not a regular file"
joulewise/salvage_dangler.py:1186:                    "closure launcher refusal is unreadable"
joulewise/salvage_dangler.py:1188:            record = _read_json_object(refusal_path)
joulewise/salvage_dangler.py:1189:            observation = inspect_launcher_refusal(record, custody_roots)
joulewise/salvage_dangler.py:1190:            observation["launcher_refusal_path"] = str(refusal_path)
joulewise/salvage_dangler.py:1191:            observation["artifact_manifest"] = [_descriptor(refusal_path)]
joulewise/salvage_dangler.py:1196:            "launcher_refusal_zero_bytes",
joulewise/salvage_dangler.py:1291:                    "refusal_record",
joulewise/salvage_dangler.py:1292:                    "launcher_refusal_path",
joulewise/salvage_dangler.py:1410:    "inspect_launcher_refusal",
scripts/validate_powermetrics_fiducial.py:144:    Timeout is a governed refusal, not permission to fall through. The
scripts/validate_powermetrics_fiducial.py:373:        """Best effort on ruled failures; a failed append leaves pending refusal."""
tests/test_cli.py:52:    def test_reduce_unsupported_or_crossed_version_is_structured_refusal(self) -> None:
tests/test_cli.py:54:        # traceback instead of the governed CLI refusal surface.
joulewise/detection_floor.py:11:- the pure conservative regime-transport refusal rule
joulewise/detection_floor.py:68:    "transport_refusal_reasons",
joulewise/detection_floor.py:522:    """Classify the registered D-078 condition without turning it into refusal.
joulewise/detection_floor.py:2997:# Conservative regime-transport refusal rule (pure)
joulewise/detection_floor.py:3009:def transport_refusal_reasons(
joulewise/detection_floor.py:3027:    the two artifact-level refusal codes reachable before transport checks.
scripts/validate_gate_packet.py:36:errors emit a machine-readable refusal receipt and exit nonzero.  ``--help``
scripts/validate_gate_packet.py:84:    """Raised instead of argparse terminating without a refusal receipt."""
scripts/validate_gate_packet.py:534:def _cli_refusal() -> dict[str, Any]:
scripts/validate_gate_packet.py:556:        return _emit_receipt(_cli_refusal())
scripts/validate_gate_packet.py:573:        return _emit_receipt(_cli_refusal())
scripts/validate_gate_packet.py:575:        receipt = _refuse(_cli_refusal(), "internal_error")
joulewise/calibration_ledger.py:93:# Stable refusal taxonomy.  Consumers propagate these exact spellings into
joulewise/calibration_ledger.py:228:    refusal_reasons: tuple[str, ...]
joulewise/calibration_ledger.py:234:        return not self.refusal_reasons
joulewise/calibration_ledger.py:735:        refusal_reasons=tuple(sorted(reasons)),
joulewise/calibration_ledger.py:1305:    # secondary key used before the duplicate-attempt refusal above.
tests/test_validate_gate_packet.py:126:    def assert_refusal(
tests/test_validate_gate_packet.py:170:        self.assert_refusal(completed, receipt, "charter_trusted_observed_mismatch")
tests/test_validate_gate_packet.py:175:        self.assert_refusal(
tests/test_validate_gate_packet.py:186:        self.assert_refusal(
tests/test_validate_gate_packet.py:193:        self.assert_refusal(completed, receipt, "packet_digest_mismatch")
tests/test_validate_gate_packet.py:201:        self.assert_refusal(completed, receipt, "packet_digest_mismatch")
tests/test_validate_gate_packet.py:219:    def test_every_nonzero_path_emits_one_v2_refusal_receipt(self) -> None:
tests/test_validate_gate_packet.py:252:        validation_refusal, _ = self.run_validator(
tests/test_validate_gate_packet.py:269:                "validation_refusal",
tests/test_validate_gate_packet.py:270:                validation_refusal.returncode,
tests/test_validate_gate_packet.py:271:                validation_refusal.stdout,
tests/test_validate_gate_packet.py:300:        self.assert_refusal(completed, receipt, "exhibit_digest_mismatch")
tests/test_validate_gate_packet.py:309:        self.assert_refusal(completed, receipt, "charter_pin_missing")
tests/test_validate_gate_packet.py:314:        self.assert_refusal(completed, receipt, "charter_pin_duplicate")
tests/test_validate_gate_packet.py:398:                self.assert_refusal(completed, receipt, reason)
tests/test_validate_gate_packet.py:444:        self.assert_refusal(completed, receipt, "charter_pin_ambiguous")
tests/test_validate_gate_packet.py:455:        self.assert_refusal(completed, receipt, "charter_pin_ambiguous")
tests/test_validate_gate_packet.py:464:        self.assert_refusal(completed, receipt, "exhibit_unreadable")
tests/test_validate_gate_packet.py:474:        self.assert_refusal(completed, receipt, "manifest_parse_error")
tests/test_validate_gate_packet.py:484:                self.assert_refusal(completed, receipt, "manifest_parse_error")
tests/test_validate_gate_packet.py:493:        self.assert_refusal(completed, receipt, "exhibit_custody_invalid")
tests/test_validate_gate_packet.py:505:        self.assert_refusal(completed, receipt, "exhibit_custody_invalid")
tests/test_validate_gate_packet.py:513:        self.assert_refusal(completed, receipt, "exhibit_custody_invalid")
tests/test_validate_gate_packet.py:527:        self.assert_refusal(completed, receipt, "exhibit_alias_duplicate")
tests/test_validate_gate_packet.py:552:                self.assert_refusal(completed, receipt, "cli_invalid")
tests/test_validate_gate_packet.py:583:                self.assert_refusal(completed, receipt, "cli_invalid")
tests/test_validate_gate_packet.py:590:        ``assert_refusal`` and the explicit PASS assertions guard the new v2
tests/test_validate_gate_packet.py:608:        self.assert_refusal(refused, refuse_receipt, "packet_digest_mismatch")
tests/test_validate_gate_packet.py:648:                self.assert_refusal(completed, receipt, reason)
tests/test_validate_gate_packet.py:691:                self.assert_refusal(completed, receipt, reason)
joulewise/quiet_guard.py:145:    """A fail-closed guard refusal carrying a canonical cause."""
joulewise/quiet_guard.py:160:    """Return the stable wire representation for one refusal cause."""
joulewise/quiet_guard.py:835:    def arm_refusal(self) -> dict[str, Any]:
joulewise/quiet_guard.py:849:        refusal = self.arm_refusal()
joulewise/quiet_guard.py:850:        raise GuardError(refusal["cause"], refusal["detail"])
tests/test_quiet_guard.py:200:        refusal = self.engine.arm_refusal()
tests/test_quiet_guard.py:201:        self.assertEqual(refusal["cause"], "t3_char_pair_verdict_missing")
tests/test_quiet_guard.py:203:            refusal["signature"],
tests/test_quiet_guard.py:321:    def test_validation_refusal_does_not_create_missing_control_lock(self) -> None:
tests/test_quiet_guard.py:322:        root = self.root / "validation-only-refusal"
tests/test_quiet_guard.py:653:    def test_lock_unavailable_is_canonical_refusal(self) -> None:
tests/test_quiet_guard.py:1119:    def test_cli_arm_refusal_cause_matches_commit_one_contract(self) -> None:
tests/test_quiet_guard.py:1707:    def test_commit_one_omits_drain_constants_and_launch_refusal_surface(self) -> None:
tests/test_quiet_guard.py:1718:        self.assertFalse(hasattr(guard_module, "agent_launch_refusal"))
tests/test_quiet_guard.py:1719:        self.assertNotIn("agent_launch_refusal", engine_source)
tests/test_d078_reason_registry.py:1:"""D-078 stable claim/refusal vocabulary is decision-log registered."""
tests/test_whole_window.py:161:                refusal_reasons=(),
tests/test_whole_window.py:382:    def test_local_microphase_refusals_preserve_decode_and_cannot_leak(
tests/test_whole_window.py:436:                        refusal_reasons: tuple[str, ...] = ()
tests/test_whole_window.py:472:                    session.ready, session.refusal_reasons
tests/test_whole_window.py:474:                self.assertEqual(session.refusal_reasons, ())
tests/test_whole_window.py:479:                            session.path_refusal_reasons.items()
tests/test_whole_window.py:488:                    decode.extractable, decode.refusal_reasons
tests/test_whole_window.py:492:                    local_reason, tokenize.refusal_reasons
tests/test_whole_window.py:495:                    baseline.extractable, baseline.refusal_reasons
tests/test_whole_window.py:574:            session.refusal_reasons, ("negative_power_sample",)
tests/test_whole_window.py:576:        self.assertEqual(session.path_refusal_reasons, {})
tests/test_whole_window.py:603:            session.refusal_reasons,
tests/test_whole_window.py:606:        self.assertEqual(session.path_refusal_reasons, {})
tests/test_whole_window.py:632:            session.refusal_reasons, (LOCAL_CROSSING,)
tests/test_whole_window.py:634:        self.assertEqual(session.path_refusal_reasons, {})
tests/test_whole_window.py:656:            session.refusal_reasons, (UNRECORDED_ENVELOPE,)
tests/test_whole_window.py:658:        self.assertEqual(session.path_refusal_reasons, {})
tests/test_whole_window.py:698:        self.assertTrue(session.ready, session.refusal_reasons)
tests/test_whole_window.py:699:        self.assertEqual(session.refusal_reasons, ())
tests/test_whole_window.py:701:            session.path_refusal_reasons,
tests/test_whole_window.py:707:        self.assertIn(UNRECORDED_ENVELOPE, report.refusal_reasons)
tests/test_whole_window.py:735:            session.refusal_reasons, (UNRECORDED_ENVELOPE,)
tests/test_whole_window.py:737:        self.assertEqual(session.path_refusal_reasons, {})
docs/reviews/2026-07-13-comprehensive-audit/packets/C1.json:156:        "action": "Define and enforce safe single-component identifier syntax on both client and worker before path construction, with absolute/traversal refusal tests.",
tests/test_axi_request_validation.py:326:    def test_all_validator_refusal_codes_have_exact_failing_cases(self) -> None:
tests/test_analysis_integration.py:66:    whole_window_refusal_reasons,
tests/test_analysis_integration.py:132:        refusal_reasons=(),
tests/test_analysis_integration.py:627:    def test_v3_abba_engine_and_d093_refusal_precedence(self):
tests/test_analysis_integration.py:1285:                whole_window_refusal_reasons(
tests/test_analysis_integration.py:1361:                reasons = whole_window_refusal_reasons(runs, set(bundle_ids))
tests/test_analysis_integration.py:1382:                self.refusal_reasons = ()
tests/test_analysis_integration.py:1441:                "joulewise.analysis_engine.inputs.whole_window_refusal_reasons",
tests/test_analysis_integration.py:1540:    def test_named_strata_manifest_preserves_terminal_mock_refusal(self):
tests/test_analysis_integration.py:1581:    def test_named_strata_manifest_preserves_terminal_mock_refusal_with_production_telemetry_identity(
tests/test_analysis_integration.py:2907:    def test_cli_binds_distinct_calibration_bundles_and_preserves_mock_refusal(self):
tests/test_analysis_integration.py:2912:    def test_cli_binds_distinct_calibration_bundles_and_preserves_mock_refusal_with_production_telemetry_identity(
tests/test_analysis_integration.py:4435:    def test_authenticated_bare_v2_existing_reaches_join_refusal(self):
tests/test_analysis_integration.py:4845:    def test_unresolved_declared_id_has_exact_refusal_payload(self):
tests/test_calibration_ledger.py:315:        self.assertIn("calibration_ledger_pending", snapshot.refusal_reasons)
tests/test_calibration_ledger.py:355:        self.assertIn("calibration_ledger_rollback", snapshot.refusal_reasons)
tests/test_calibration_ledger.py:361:        self.assertIn("calibration_ledger_head_mismatch", snapshot.refusal_reasons)
tests/test_calibration_ledger.py:381:        self.assertIn("calibration_ledger_chain_conflict", snapshot.refusal_reasons)
tests/test_calibration_ledger.py:383:            "calibration_ledger_attempt_conflict", snapshot.refusal_reasons
tests/test_calibration_ledger.py:385:        self.assertNotIn("calibration_ledger_head_mismatch", snapshot.refusal_reasons)
tests/test_calibration_ledger.py:417:            snapshot.refusal_reasons,
tests/test_calibration_ledger.py:429:        self.assertIn("calibration_ledger_baseline_missing", snapshot.refusal_reasons)
tests/test_detection_floor.py:42:    transport_refusal_reasons,
tests/test_detection_floor.py:2244:            refusal_reasons=(),
tests/test_detection_floor.py:2271:                "joulewise.floor_extraction._whole_window_extraction_refusals",
tests/test_detection_floor.py:2283:            extracted["cells"][0]["refusal_reasons"],
tests/test_detection_floor.py:2328:        reasons = transport_refusal_reasons(consumer, self.group, self.cells_by_id)
tests/test_detection_floor.py:2337:        reasons = transport_refusal_reasons(
tests/test_detection_floor.py:2347:        reasons = transport_refusal_reasons(
tests/test_detection_floor.py:2357:        # different stack identity hash -> refusal, never silent transport.
tests/test_detection_floor.py:2409:        reasons = transport_refusal_reasons(make_consumer(), self.group, stale)
tests/test_detection_floor.py:2414:        reasons = transport_refusal_reasons(make_consumer(), self.group, smoke)
tests/test_detection_floor.py:2417:        reasons = transport_refusal_reasons(make_consumer(), self.group, {})
tests/test_detection_floor.py:2421:        reasons = transport_refusal_reasons(make_consumer(), empty_group, self.cells_by_id)
scripts/claims_lint.py:411:    """Accept D-062 demotion or AXI-SA's stricter closed refusal rule."""
scripts/claims_lint.py:421:    axi_closed_refusal = all(marker in lowered for marker in AXI_CLOSED_TOPUP_MARKERS)
scripts/claims_lint.py:422:    return d062_qualified or axi_closed_refusal
scripts/spike_mlx_prompt_cache.py:567:def add_common_model_arg(parser: argparse.ArgumentParser) -> None:
scripts/spike_mlx_prompt_cache.py:581:    add_common_model_arg(monolithic)
scripts/spike_mlx_prompt_cache.py:588:    add_common_model_arg(prefill)
scripts/spike_mlx_prompt_cache.py:599:    add_common_model_arg(run)
tests/test_powermetrics_fiducial.py:633:        # refusal reason still serialized status=valid.
tests/test_whole_window_selection.py:42:    whole_window_refusal_reasons,
tests/test_whole_window_selection.py:107:    def test_screen_budget_refusals_are_bidirectionally_registered(self):
tests/test_whole_window_selection.py:251:    def test_config_absent_frozen_member_keeps_empty_current_refusal_set(self):
tests/test_whole_window_selection.py:439:                    refusal_reasons=(),
tests/test_whole_window_selection.py:521:                    "joulewise.whole_window.whole_window_refusal_reasons",
tests/test_whole_window_selection.py:562:                    "joulewise.whole_window.whole_window_refusal_reasons",
tests/test_whole_window_selection.py:974:                    whole_window_refusal_reasons(root, {"A", "B"}), ()
tests/test_whole_window_selection.py:1004:                    whole_window_refusal_reasons(
tests/test_whole_window_selection.py:1060:                    whole_window_refusal_reasons(root, {"A", "B"}),
tests/test_whole_window_selection.py:1115:                "joulewise.whole_window.current_environment_refusals",
tests/test_whole_window_selection.py:1135:        *, refusal_reasons: tuple[str, ...] = ()
tests/test_whole_window_selection.py:1144:            refusal_reasons=refusal_reasons,
tests/test_whole_window_selection.py:1165:                reasons = whole_window_refusal_reasons(
tests/test_whole_window_selection.py:1175:            refusal_reasons=("calibration_ledger_pending",),
tests/test_whole_window_selection.py:1192:                    reasons = whole_window_refusal_reasons(
tests/test_whole_window_selection.py:1202:        self.assertEqual(session.refusal_reasons, ("calibration_ledger_pending",))
tests/test_whole_window_selection.py:1212:                reasons = whole_window_refusal_reasons(root, bundle_ids)
tests/test_whole_window_selection.py:1224:                reasons = whole_window_refusal_reasons(root, bundle_ids)
tests/test_whole_window_selection.py:1243:                reasons = whole_window_refusal_reasons(
tests/test_whole_window_selection.py:2088:            # A metric-local refusal that already existed at mint time is not
tests/test_whole_window_selection.py:2139:        self.assertTrue(session.ready, session.refusal_reasons)
tests/test_whole_window_selection.py:2210:            self.assertTrue(session.ready, session.refusal_reasons)
tests/test_whole_window_selection.py:2292:                    "joulewise.reduce.current_environment_refusals",
tests/test_whole_window_selection.py:2296:                    "joulewise.reduce.environment_admission_refusals",
tests/test_whole_window_selection.py:2409:            self.assertTrue(session.ready, session.refusal_reasons)
tests/test_whole_window_selection.py:2446:    def test_session_retains_widening_introduced_metric_local_refusal(
tests/test_whole_window_selection.py:2527:        self.assertTrue(session.ready, session.refusal_reasons)
tests/test_whole_window_selection.py:2528:        self.assertEqual(session.refusal_reasons, ())
tests/test_whole_window_selection.py:2530:            session.path_refusal_reasons,
tests/test_whole_window_selection.py:2586:        self.assertTrue(session.ready, session.refusal_reasons)
tests/test_whole_window_selection.py:2671:                session.refusal_reasons = ("instrument_calibration_invalid",)
tests/test_whole_window_selection.py:2679:                session.refusal_reasons = ()
tests/test_whole_window_selection.py:2750:            session.refusal_reasons,
tests/test_whole_window_selection.py:2816:            session.refusal_reasons,
tests/test_whole_window_selection.py:2900:            reasons = whole_window_refusal_reasons(self.root, set(bundle_ids))
tests/test_whole_window_selection.py:2903:                whole_window_refusal_reasons(
tests/test_whole_window_selection.py:2935:                whole_window_refusal_reasons(
tests/test_whole_window_selection.py:2951:                        whole_window_refusal_reasons(
tests/test_whole_window_selection.py:2967:            reasons = whole_window_refusal_reasons(
tests/test_whole_window_selection.py:3023:            reasons = whole_window_refusal_reasons(
docs/reviews/2026-07-13-comprehensive-audit/report.md:599:| Harness permission classifier | three refusals of lead self-approved lease abandonments (all subsequently Ed-adjudicated) |
joulewise/load_transition_alignment.py:48:    """Fail-closed input or artifact refusal with a stable reason code."""
joulewise/load_transition_alignment.py:126:            "refusal_policy",
joulewise/load_transition_alignment.py:246:    refusal_policy = manifest["refusal_policy"]
joulewise/load_transition_alignment.py:247:    if not isinstance(refusal_policy, Mapping):
joulewise/load_transition_alignment.py:248:        raise AlignmentRefusal(reason, "refusal_policy must be an object")
joulewise/load_transition_alignment.py:250:        refusal_policy,
joulewise/load_transition_alignment.py:252:        "manifest.refusal_policy",
joulewise/load_transition_alignment.py:260:    if dict(refusal_policy) != expected_reasons:
joulewise/load_transition_alignment.py:261:        raise AlignmentRefusal(reason, "refusal_policy reason codes differ from the frozen policy")
tests/test_mint_floor_artifact_generalized.py:496:            "refusal_reasons": [],
tests/test_mint_floor_artifact_generalized.py:508:        "spec_membership_refusals": [],
tests/test_mint_floor_artifact_generalized.py:509:        "idle_admission_refusals": [],
tests/test_mint_floor_artifact_generalized.py:1019:                    # The pinset-load refusal must fire on its own merits:
joulewise/analysis_engine/estimators.py:80:    governed common-mode rule may instead supply an already-derived
joulewise/analysis_engine/estimators.py:626:                "ratio deterministic common-mode residuals must be derived in ratio units before estimation"
joulewise/analysis_engine/estimators.py:736:                    "ratio deterministic common-mode residuals must be derived in ratio units "
tests/test_microdelta_generate_configs.py:15:    / "micro_delta"
tests/test_analysis_claims.py:2613:            any("supersession refusal forbids estimation" in error for error in errors),
tests/test_analysis_claims.py:2617:            any("supersession refusal must take precedence" in error for error in errors),
tests/test_axi_schemas.py:197:    def test_request_roster_hash_domains_and_boolean_integer_refusal(self) -> None:
tests/test_run_campaign.py:576:    def test_r9_refusal_table_is_global_and_append_touches_nothing(self) -> None:
tests/test_run_campaign.py:577:        refusals = (
tests/test_run_campaign.py:596:            for index, (name, tail) in enumerate(refusals):
tests/test_run_campaign.py:7266:    def test_neg8_bound_binding_changes_trigger_stale_refusal(self) -> None:
tests/test_run_campaign.py:7886:    def test_environment_refusal_does_not_hide_valid_retry_telemetry(self) -> None:
tests/test_run_campaign.py:7895:            "_current_member_environment_refusals",
tests/test_run_campaign.py:8761:            "_current_member_environment_refusals",
tests/test_run_campaign.py:8765:            "joulewise.whole_window.current_environment_refusals",
tests/test_p2038_production_path.py:489:            # If the gate is not eligible, the ONLY acceptable refusals are
tests/test_p2038_production_path.py:596:        # rather than laundering those independent refusals into a pass.
tests/test_analysis_manifest_v3.py:63:    def test_ratified_freeze_and_refusal_edges(self) -> None:
joulewise/analysis_engine/inputs.py:47:    transport_refusal_reasons,
joulewise/analysis_engine/inputs.py:60:    whole_window_refusal_reasons,
joulewise/analysis_engine/inputs.py:272:    """Return stable public refusal codes from detailed binding diagnostics."""
joulewise/analysis_engine/inputs.py:914:        # immediately follows and remains the authority for refusal details.
joulewise/analysis_engine/inputs.py:1372:                    reasons = whole_window_refusal_reasons(
joulewise/analysis_engine/inputs.py:1800:    refusal payload.
joulewise/analysis_engine/inputs.py:1999:    refusal_payload = {
joulewise/analysis_engine/inputs.py:2047:            resolved[bundle_id] = dict(refusal_payload)
joulewise/analysis_engine/inputs.py:2820:    whole_window_reasons = whole_window_refusal_reasons(
joulewise/analysis_engine/inputs.py:3335:            # This is a version/method eligibility refusal, not malformed
joulewise/analysis_engine/inputs.py:3777:    refusals = transport_refusal_reasons(
joulewise/analysis_engine/inputs.py:3789:        refusals = tuple(dict.fromkeys((*refusals, "artifact_schema_invalid")))
joulewise/analysis_engine/inputs.py:3807:        refusals = tuple(dict.fromkeys((*refusals, "artifact_schema_invalid")))
joulewise/analysis_engine/inputs.py:3808:    if refusals:
joulewise/analysis_engine/inputs.py:3819:            reason_codes=tuple(refusals),
tests/test_package_bundle_pack.py:499:    def test_multi_bundle_duplicate_and_later_invalid_refusals(self) -> None:
tests/test_package_bundle_pack.py:544:            side_effect=package_bundle_pack.PrivacyAuditError("injected refusal"),
joulewise/determinism_gate.py:137:        except Exception as exc:  # noqa: BLE001 - validator failures become refusals.
joulewise/determinism_gate.py:772:        "refusal_message": "inputs are not comparable strict-valid repetition bundles",
joulewise/reduce.py:93:    current_environment_refusals,
joulewise/reduce.py:94:    environment_admission_refusals,
joulewise/reduce.py:95:    post_run_environment_refusals,
joulewise/reduce.py:143:    """Governed reducer dispatch refusal, distinct from unrelated ValueError."""
joulewise/reduce.py:711:                current_environment_refusals(
joulewise/reduce.py:720:                environment_admission_refusals(
joulewise/reduce.py:727:            reasons.extend(post_run_environment_refusals(metadata))
joulewise/reduce.py:794:            environment_admission_refusals(
joulewise/reduce.py:2395:    resolved_refusal_reasons = (
joulewise/reduce.py:2421:    if resolved_refusal_reasons:
joulewise/reduce.py:2429:                merge(gate, resolved_refusal_reasons)
joulewise/reduce.py:2436:                    merge(gate, resolved_refusal_reasons)
tests/test_determinism_gate.py:974:    def test_cli_zero_bundle_arguments_emit_refusal_envelope(self) -> None:
tests/test_determinism_gate.py:1093:                "refusal_message",
tests/test_axi_analysis_manifest.py:132:    def test_manifest_refusal_code_goldens(self) -> None:
tests/test_axi_analysis_manifest.py:249:    def test_manifest_cardinality_integers_reject_booleans_with_named_refusal(self) -> None:
joulewise/envelope_gate.py:42:# Out-of-domain suite shape is a D-036 input refusal, not a failed science
joulewise/envelope_gate.py:82:    refusal_reasons: list[str] = []

exec
/bin/zsh -lc "find . -maxdepth 2 -type d | sort | sed -n '1,240p'; rg --files docs/process_traces docs/run_reports configs/campaigns | rg 'phase-share|commonmode|window|floor|contrast|linearity|micro|q4|wall|boundary|refusal|custody|anchor|splitwise' | sed -n '1,320p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
.
./.agents
./.agents/skills
./.claude
./.claude/agents
./.claude/commands
./.claude/skills
./.codex
./.codex-bridge
./.codex-bridge/prompts
./.codex-bridge/responses
./.github
./.github/workflows
./analysis
./analysis/rpt001-v1
./analysis/rpt001-v2
./configs
./configs/analysis_registry
./configs/calibration
./configs/campaign_policies
./configs/campaigns
./configs/characterization
./configs/examples
./configs/floor_mint
./configs/suite_manifests
./docs
./docs/advisor_briefs
./docs/campaign_packs
./docs/contracts
./docs/paper
./docs/phase_1
./docs/phase_2
./docs/phase_3
./docs/phase_4
./docs/phase_5
./docs/process
./docs/process_traces
./docs/report_src
./docs/reviews
./docs/run_reports
./docs/site
./docs/site_src
./docs/specs
./docs/strategy
./docs/stream_logs
./env
./figures
./figures/rpt001-v1
./figures/rpt001-v2
./joulewise
./joulewise/adapters
./joulewise/analysis_engine
./joulewise/gensuite
./scripts
./scripts/floor_mint_pinsets
./site_capsule
./site_capsule/client
./site_capsule/server
./tests
./tests/fixtures
./tests/goldens
configs/campaigns/p2_015_floors/10_df_telem_onoff_unavailable/README.md
configs/campaigns/p2_015_floors/11_neg8_end/p2015-neg8-reference-end.json
configs/campaigns/p2_015_floors/11_neg8_end/order_manifest.json
configs/campaigns/p2_015_floors/calibration_plan.json
configs/campaigns/p2_015_floors/backup_icloud.sh
configs/campaigns/p2_015_floors/order_manifest.json
configs/campaigns/p2_015_floors/generate_configs.py
docs/run_reports/2026-07-31-contrast-window-collection.md
docs/run_reports/2026-07-23-window-a-collection-arc.md
docs/run_reports/2026-07-17-window-a-floors.md
docs/run_reports/2026-07-19-recal456-extended-window.md
docs/run_reports/2026-08-01-metrology-window-b.md
docs/run_reports/2026-07-19-d077-recal-window.md
docs/run_reports/2026-07-28-floor-mint-implementation.md
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b05-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b10-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b03-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b09-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b06-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b02-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b08-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b07-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b04-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b01-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b10-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/order_manifest.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b05-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b06-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b09-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b03-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b07-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b08-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b02-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b01-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b04-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b01-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b04-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b07-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b08-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b02-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b06-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b09-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b03-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b10-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b05-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b04-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b01-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b02-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b08-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b07-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b03-b2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b09-a2.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b06-b1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b05-a1.json
configs/campaigns/p2_015_floors/05_phase_decode_abba/p2015-df-cmp-abba-ph-decode-b10-a2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b06-b1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b09-a2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b03-b2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b10-a2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b05-a1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b01-a2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b04-a1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b07-b1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b08-a2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b02-b2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b03-a2.json
configs/campaigns/p2_015_floors/07_suite_abba/order_manifest.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b09-b2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b06-a1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b05-b1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b10-b2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b04-b1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b01-b2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b02-a2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b08-b2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b07-a1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b02-a1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b08-b1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b07-a2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b04-b2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b01-b1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b05-b2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b10-b1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b03-a1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b09-b1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b06-a2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b07-b2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b08-a1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b02-b1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b01-a1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b04-a2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b10-a1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b05-a2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b06-b2.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b09-a1.json
configs/campaigns/p2_015_floors/07_suite_abba/p2015-df-cmp-abba-su-b03-b1.json
configs/campaigns/p2_015_floors/06_suite_absolute/p2015-df-su-sentinel-abs-r02.json
configs/campaigns/p2_015_floors/06_suite_absolute/p2015-df-su-sentinel-abs-r03.json
configs/campaigns/p2_015_floors/06_suite_absolute/p2015-df-su-sentinel-abs-r08.json
configs/campaigns/p2_015_floors/06_suite_absolute/order_manifest.json
configs/campaigns/p2_015_floors/06_suite_absolute/p2015-df-su-sentinel-abs-r04.json
configs/campaigns/p2_015_floors/06_suite_absolute/p2015-df-su-sentinel-abs-r05.json
configs/campaigns/p2_015_floors/06_suite_absolute/p2015-df-su-sentinel-abs-r09.json
configs/campaigns/p2_015_floors/06_suite_absolute/p2015-df-su-sentinel-abs-r06.json
configs/campaigns/p2_015_floors/06_suite_absolute/p2015-df-su-sentinel-abs-r10.json
configs/campaigns/p2_015_floors/06_suite_absolute/p2015-df-su-sentinel-abs-r07.json
configs/campaigns/p2_015_floors/06_suite_absolute/p2015-df-su-sentinel-abs-r01.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r05.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r07.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r09.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r09.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r05.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r04.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r08.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r10.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r08.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r06.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r04.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r03.json
configs/campaigns/p2_015_floors/02_phase_absolute/order_manifest.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r03.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r01.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r02.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r02.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r01.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r03.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r01.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r02.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r05.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r07.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r07.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r09.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r08.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r10.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-prefill-abs-r06.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r06.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-short-prefill-abs-r04.json
configs/campaigns/p2_015_floors/02_phase_absolute/p2015-df-ph-decode-abs-r10.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b04-b1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b01-b2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b02-a2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b08-b2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b07-a1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b03-a2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b09-b2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b06-a1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b05-b1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b10-b2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b01-a2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b04-a1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/order_manifest.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b07-b1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b08-a2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b02-b2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b06-b1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b09-a2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b03-b2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b10-a2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b05-a1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b10-a1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b05-a2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b06-b2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b09-a1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b03-b1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b07-b2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b08-a1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b02-b1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b01-a1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b04-a2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b05-b2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b10-b1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b03-a1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b09-b1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b06-a2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b02-a1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b08-b1.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b07-a2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b04-b2.json
configs/campaigns/p2_015_floors/04_phase_prefill_abba/p2015-df-cmp-abba-ph-prefill-b01-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b05-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b10-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b03-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b06-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b09-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b02-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b07-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b08-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b04-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b01-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b10-a1.json
configs/campaigns/p2_015_floors/03_request_abba/order_manifest.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b05-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b09-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b06-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b03-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b08-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b07-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b02-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b01-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b04-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b01-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b04-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b08-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b07-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b02-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b09-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b06-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b03-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b10-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b05-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b04-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b01-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b02-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b07-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b08-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b03-a2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b06-a1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b09-b2.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b05-b1.json
configs/campaigns/p2_015_floors/03_request_abba/p2015-df-cmp-abba-rq-b10-b2.json
docs/process_traces/2026-08-03-d111-backfill/adjudication_packet_20260801/close-out-windowA.md
docs/process_traces/2026-08-03-d111-backfill/adjudication_packet_20260801/close-out-windowB.md
configs/campaigns/p2_015_floors/00_neg8_start/order_manifest.json
configs/campaigns/p2_015_floors/00_neg8_start/p2015-neg8-reference-start.json
docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json
docs/process_traces/2026-08-06-d079-issuance-coldgate/ISSUANCE-custody-manifest.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b10-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b05-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b09-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b06-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b03-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b08-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b07-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b02-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b01-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b04-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b05-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/order_manifest.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b10-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b03-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b06-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b09-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b02-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b07-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b08-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b04-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b01-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b04-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b01-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b02-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b07-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b08-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b03-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b06-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b09-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b05-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b10-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b01-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b04-b1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b08-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b07-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b02-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b09-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b06-a1.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b03-a2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b10-b2.json
configs/campaigns/p2_015_floors/09_optional_short_prefill_abba/p2015-df-cmp-abba-ph-short-prefill-b05-b1.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r02.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r01.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r03.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r08.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r10.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r06.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/order_manifest.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r04.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r05.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r07.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r09.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r04.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r10.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r08.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r06.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r07.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r09.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r05.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r02.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-decode-abs-r03.json
configs/campaigns/p2_015_floors/08_optional_long_request_absolute/p2015-df-rq-long-prompt-abs-r01.json
configs/campaigns/p2_015_floors/calibration_plan.sha256
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r09.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r02.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r01.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r03.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r06.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r05.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r10.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r07.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r04.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r06.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r03.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r10.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r01.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r07.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r02.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r09.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r04.json
configs/campaigns/p2_015_floors/01_request_absolute_core/order_manifest.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r08.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-mid-abs-r05.json
configs/campaigns/p2_015_floors/01_request_absolute_core/p2015-df-rq-short-abs-r08.json
configs/campaigns/window_references/start_triplet/neg8-window-start-r3.json
configs/campaigns/window_references/start_triplet/neg8-window-start-r2.json
configs/campaigns/window_references/start_triplet/order_manifest.json
configs/campaigns/window_references/start_triplet/neg8-window-start-r1.json
configs/campaigns/splitwise_decode_v1/calibration_plan.json
configs/campaigns/splitwise_decode_v1/order_manifest.json
configs/campaigns/splitwise_decode_v1/generate_configs.py
configs/campaigns/window_references/midpoint/order_manifest.json
configs/campaigns/window_references/midpoint/neg8-window-midpoint.json
configs/campaigns/window_references/README.md

exec
/bin/zsh -lc 'for f in docs/run_reports/2026-07-31-contrast-window-collection.md docs/run_reports/2026-07-23-window-a-collection-arc.md docs/run_reports/2026-07-17-window-a-floors.md docs/run_reports/2026-08-01-metrology-window-b.md docs/run_reports/2026-07-19-recal456-extended-window.md docs/run_reports/2026-07-28-floor-mint-implementation.md; do echo "FILE $f"; rg -n "''^#|''^##|141'"\\.29|146\\.730|5\\.809|5\\.903|192\\.386|6\\.294|13\\.998|31\\.1|24\\.9|6\\.46|2\\.13|linearity|slope|additivity|phase|refus|FAILED|PASSED|diagnostic|duration|energy\" \""'$f" | head -180; done' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
FILE docs/run_reports/2026-07-31-contrast-window-collection.md
1:# 2026-07-31 — Contrast window `window_contrast_20260730`: collection, recovery, and PASSED verdict
7:## What ran
22:## Chain
30:## Calibrations and the bracket
33:  **0.026131301462788137** s, §5B screen PASSED, single attempt.
41:## Members
51:## Verdict
53:**Whole-window verdict: PASSED** — row **58** of the claim log.
62:## Deviations and recovery (§10-sanctioned, evidence preserved)
97:## Custody
103:## No floor extraction — by design
109:**7.377086 J** (mint #1, mainline) and the 7B floors, absolute **6.294380** /
110:comparative **13.998037** J.
112:## Diagnostics vs gated claims — the distinction that governs this window
116:- **A-arm (1.5B)** idle-subtracted decode energy mean **51.961375 J**
119:- **Per-block ABBA contrast (7B − 1.5B)** mean **146.730349 J**, σ = 0.241,
129:diagnostics above as a claim would be exactly the promotion the pre-registration
132:## Status and the one open operator action
134:- **Collection COMPLETE, verdict PASSED.** The window is evidence-bearing now
140:## Process Trace
FILE docs/run_reports/2026-07-23-window-a-collection-arc.md
1:# 2026-07-22 → 24 — First live collection under the repaired instrument: two nights, four bracketed windows, three collection-path repairs, and the NEG-8 gate adjudication
8:## Arc summary
31:  diagnostic-cascade decoupling; explicit hash-sealed occurrence
32:  supersession (default refusal preserved); waiver consumption in the
36:  (the guard refused correctly every time); post-subcampaign churn
41:## Collected corpora (all strict-collected, currently non-claim-bearing as windows)
45:| a5 | 07-23 04:45→13:57 | 108 | NEG-8 start, request-abs 20/20, phase-abs 30/30, decode-ABBA 40/40 | failed — real drift (stale end ref, −0.778 J workload-level) + one true clock-anchor refusal |
47:| a7 | 07-24 02:57→05:33 | 42 | NEG-8 start, phase-abs 30/30 | failed — end reference admission refusal (correct) |
54:## The decisive adjudication (Sol xhigh, 2026-07-24)
65:   becomes a reported diagnostic (it already lives, correctly, in the
69:   the gate refuses `neg8_drift_bound_underived`.
74:## Path to the first claim-bearing floors
85:A diagnostic (non-claim) extraction over the four corpora is running;
FILE docs/run_reports/2026-07-17-window-a-floors.md
1:# Run report — Window A shakedown, floors, and advisor brief (2026-07-17)
8:Measurement boundary for every energy value below: **Apple M3 Max /
11:## Deliverable check
22:  `docs/phase_2/detection_floor.md`; Window A is open.
29:## Measurement narrative
31:### Production-shaped gate: four failures that protected the corpus
39:| `runs/window_a_shakedown` | `request_ineligible`; request cadence unrecorded | The native trace ended about 0.53 s before `sampling_stopped`, so no right-edge bracketing gap or cadence could be established. | PR #72 added a bounded post-marker powermetrics drain while preserving marker-bounded energy integration and sampler termination. |
52:### Floor campaign execution and accounting
54:The floor inputs covered normal telemetry and the planned request, phase,
59:then skipped completed members and continued from the interrupted phase-ABBA
66:- 17 resumed `status=skipped` rows that re-list already completed phase-ABBA
75:## Verified floor results
77:All energy values are false-effect guard floors in joules at the **Apple M3
79:headline basis. Idle-subtracted request energy is a labeled within-device
84:| cell / energy basis and boundary | absolute floor | comparative floor | computed `floor_gate_j` / status |
90:| prefill phase, gross — M3 Max / powermetrics SoC rails | 1.476788 J | 1.738940 J | 1.738940 J |
91:| decode phase, gross — M3 Max / powermetrics SoC rails | 0.786337 J | 1.026892 J | 1.026892 J |
96:The NEG-8 start/end pair is an `n=2` drift-anchor diagnostic, not a campaign
98:energy changed by 7.658896 J. The idle-subtracted within-device secondary view
99:changed by 6.608040 J on the same boundary. The diagnostic confirms meaningful
102:### Evidence ceiling and anomalies retained
116:- Suite ABBA b01/b02 contain a six-member low-energy regime that drives the
123:## Mechanism verdicts and landed history
129:  observability, and native MTP lacks a generation surface. No Mac energy leg
132:  request-scoped observability. This is functionality evidence, not an energy
135:## Spend
148:## Process catch / yield draft
161:## Restart pointers
182:## Evidence index
188:| P2-038 canonical pass command, display-sleep pin, acceptance fields, plumbing-only ceiling | `docs/phase_2/detection_floor.md` §1 Ordering Preconditions |
194:## Draft deviations requiring lead attention
206:## Draft verification
220:## ADDENDUM — exploratory block, extension axes, and deploy closeout draft
226:Measurement boundary for every addendum energy value: **Apple M3 Max /
229:### Exploratory observation block
238:| unmatched model/config | gross suite energy — M3 Max / SoC rails, mean ± sample SD (range) | gross energy/generated output token — same boundary, mean (range) | idle-subtracted energy/generated output token — same boundary, within-device secondary, mean (range) | runtime-observed output tok/s, mean (range) |
245:256-token items. The stored `energy_output_token_j` uses the idle-subtracted
247:`gross_energy_j / 1280` rather than silently relabeling the stored field.
263:### DSpark/DFlash feasibility smokes and D-075 fold-in
270:unmatched. These are throughput/observability smokes, not energy measurements;
286:### Ed's deployment and current drift
296:### Process notes retained without laundering
304:- **Forced-report placeholder:** the fold-in round refused to treat a thin
306:  was re-persisted in `f656c90` before D-075 consumed it. The refusal prevented
314:### Addendum evidence and verification
FILE docs/run_reports/2026-08-01-metrology-window-b.md
1:# 2026-08-01 — Metrology window B: collected + salvage-closed; both metrology verdicts FAILED as-issued
6:## Outcome in one paragraph
12:**additivity 23/24 single-root** (C4), clean calibration bracket
14:verdicts **FAILED and stand as issued** — with *distinct* condition
18:item; the remainder (null_o2048, long_holds, one additivity slot) moves
21:## Window A verdict (emitted first, 00:26–00:47 PT): FAILED
29:null: the selector refused to form a bracket rather than consuming the
33:additivity was 21/24 at final state (not 23/24), and the charger is a
37:## Window B launch arc
72:   #2 `mtadd-p2048o0128-r08` (06:13 PT, same signature, additivity at
83:## Window B verdict (06:54–07:19 PT): FAILED — a different machinery shape
85:Recorder-then-verdict order preserved. The §8 bracket **PASSED**
97:## The adjudication this hands the desk (three question groups)
101:it). (b) Deviation-retry post-cal selection (A refused; B formed).
107:## Records
FILE docs/run_reports/2026-07-19-recal456-extended-window.md
1:# 2026-07-19 — Extended clean-provenance re-collection: 266 strict-valid bundles across three bracketed windows
8:> scale, so the request/phase/item point energies in this report are NOT
14:> or missing energy. This report's original "claim-eligible" headline
18:> (suite bundles) and zero phase/item windows. Four cooldown `cap_hit`
21:> instrument/calibration evidence; NO floor, MDE, or point energy below may
24:> additionally a shape artifact (target phase metrics differ ~0.62%), and
37:## Deviation record
46:## What was measured (all Qwen2.5-1.5B-4bit MLX, powermetrics backend)
57:  absolute core (df-rq-mid 10 + df-rq-short 10), phase absolute
62:  (40), phase-prefill (40), phase-decode (40), short-prefill (40).
71:## Mid-window incident: one guard abort, chain restaged
90:## The n=10 suite-ABBA comparative cell is complete (execution-wise)
98:## Exploratory lead-side readout (NOT the verified extraction)
133:  phase-prefill 0.354 / 0.905 J on 39.872 ± 0.610 J; phase-decode
141:## Open follow-ups
FILE docs/run_reports/2026-07-28-floor-mint-implementation.md
1:# 2026-07-28 — Mint-era resumption: hardening merged, mint tool implemented, mint #1 staged
7:## Deliverable check (operation-loop §8, first lines)
17:## Outcomes
51:   `docs/phase_2/floor_mint_contract.md` on the branch. All
64:## Verification evidence
72:  at `5befb3e` was `Ran 2241 tests, FAILED (errors=5, skipped=21)` — all
77:  `Ran 2241 tests, FAILED (errors=2, skipped=21)` — both survivors at
88:## Restart instructions (next session)
95:   questions — window-class narrowed to ("request","phase"); whole-window
111:## Anomalies and process notes
137:## Artifacts
144:  `docs/phase_2/floor_mint_contract.md` (branch).
149:## Process Trace Appendix

exec
/bin/zsh -lc "find configs/campaigns -maxdepth 2 -type d | sort | rg 'q4|shape|splitwise|7b|linearity|micro|additivity'; rg -n \"class .*Protocol|@runtime_checkable|def (integrate|extract|validate|build|compute|evaluate|reserve)|phase_energy_j|clock_anchor|calibration|custody|sha256|ABBA|abba\" joulewise/interfaces.py joulewise/reduce.py joulewise/floor_extraction.py joulewise/calibration_ledger.py joulewise/calibration_bracketing.py joulewise/whole_window.py joulewise/analysis_manifest_v3.py joulewise/analysis_engine/*.py joulewise/bundle.py joulewise/validation.py joulewise/suite.py joulewise/output_identity.py | head -400; rg -n \"q4_l3_shape_grid|holdout|prompt_level|decode_level|fixed.*marginal\" configs docs/contracts/analysis_plans.md docs/phase_2 | head -260" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
configs/campaigns/exploratory_2026_07_17/01_olmoe-1b-7b
configs/campaigns/metrology_v1/additivity_shapes
configs/campaigns/metrology_v1/linearity_ramp
configs/campaigns/metrology_v1/micro_delta
configs/campaigns/qwen25_7b_decode_floor_v1
configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute
configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05
configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10
configs/campaigns/qwen25_7b_decode_floor_v1/condition_families
configs/campaigns/splitwise_decode_v1
configs/campaigns/splitwise_decode_v1/01_decode_contrast_blocks_01_05
configs/campaigns/splitwise_decode_v1/02_decode_contrast_blocks_06_10
configs/campaigns/splitwise_decode_v1/condition_families
joulewise/analysis_engine/__init__.py:18:    ESTIMATOR_ID as ABBA_ESTIMATOR_ID,
joulewise/analysis_engine/__init__.py:369:        arm.get("condition_family_id"): arm.get("condition_family_sha256")
joulewise/analysis_engine/__init__.py:392:                and request.condition_family_sha256
joulewise/analysis_engine/__init__.py:405:                        artifact_sha256=inputs.floor_sha256,
joulewise/analysis_engine/__init__.py:417:                    unavailable_floor_resolution(inputs.floor_artifact, inputs.floor_sha256)
joulewise/analysis_engine/__init__.py:432:                    cell_scientific_identity_sha256={},
joulewise/analysis_engine/__init__.py:433:                    cell_stack_identity_sha256={},
joulewise/analysis_engine/__init__.py:434:                    bound_bundle_sha256s=frozenset(),
joulewise/analysis_engine/__init__.py:440:                inputs.floor_sha256,
joulewise/analysis_engine/__init__.py:448:                    artifact_sha256=resolution.artifact_sha256,
joulewise/analysis_engine/__init__.py:512:            "the two-run stochastic test seam is not valid for v3 ABBA blocks"
joulewise/analysis_engine/__init__.py:635:                    "E_clock_anchor_shift_bound_j" in names
joulewise/analysis_engine/__init__.py:644:                    # add the two arm bounds.  No ABBA cancellation is inferred.
joulewise/analysis_engine/__init__.py:730:        estimate_paired_blocks(observations, estimator=ABBA_ESTIMATOR_ID)
joulewise/analysis_engine/__init__.py:965:    anchor_term = "E_clock_anchor_shift_bound_j"
joulewise/analysis_engine/__init__.py:1173:        return estimate_paired_blocks(observations, estimator=ABBA_ESTIMATOR_ID)
joulewise/analysis_engine/__init__.py:1638:            (evidence.bundle_id, evidence.config_sha256)
joulewise/analysis_engine/__init__.py:1777:                "file_sha256": inputs.manifest_sha256,
joulewise/analysis_engine/__init__.py:1781:                "file_sha256": inputs.floor_sha256,
joulewise/analysis_manifest_v3.py:1:"""Frozen cross-stack ABBA analysis-manifest v3.
joulewise/analysis_manifest_v3.py:25:ESTIMATOR_ID = "abba_block_arm_mean_difference_t_v1"
joulewise/analysis_manifest_v3.py:57:        "condition_family_sha256": (
joulewise/analysis_manifest_v3.py:60:        "condition_family_file_sha256": (
joulewise/analysis_manifest_v3.py:70:                "algorithm": "sha256",
joulewise/analysis_manifest_v3.py:72:                "folded_sha256": (
joulewise/analysis_manifest_v3.py:110:        "condition_family_sha256": (
joulewise/analysis_manifest_v3.py:113:        "condition_family_file_sha256": (
joulewise/analysis_manifest_v3.py:123:                "algorithm": "sha256",
joulewise/analysis_manifest_v3.py:125:                "folded_sha256": (
joulewise/analysis_manifest_v3.py:191:    "calibration_plan",
joulewise/analysis_manifest_v3.py:197:FILE_REF_KEYS = {"path", "sha256"}
joulewise/analysis_manifest_v3.py:198:PLAN_REF_KEYS = {"path", "sha256", "plan_id"}
joulewise/analysis_manifest_v3.py:199:STAGE_REF_KEYS = {"stage_id", "path", "sha256"}
joulewise/analysis_manifest_v3.py:203:    "file_sha256",
joulewise/analysis_manifest_v3.py:204:    "condition_family_sha256",
joulewise/analysis_manifest_v3.py:206:VERDICT_KEYS = {"status", "evaluation_basis_sha256"}
joulewise/analysis_manifest_v3.py:219:    "condition_family_sha256",
joulewise/analysis_manifest_v3.py:227:    "config_sha256",
joulewise/analysis_manifest_v3.py:297:    return "am-" + hashlib.sha256(canonical_json_bytes(body)).hexdigest()
joulewise/analysis_manifest_v3.py:333:        "calibration_plan": {
joulewise/analysis_manifest_v3.py:334:            "path": "calibration_plan.json",
joulewise/analysis_manifest_v3.py:335:            "sha256": CALIBRATION_PLAN_SHA256,
joulewise/analysis_manifest_v3.py:340:            "sha256": ROOT_ORDER_SHA256,
joulewise/analysis_manifest_v3.py:346:                "sha256": digest,
joulewise/analysis_manifest_v3.py:354:                "file_sha256": freeze["condition_family_file_sha256"],
joulewise/analysis_manifest_v3.py:355:                "condition_family_sha256": freeze["condition_family_sha256"],
joulewise/analysis_manifest_v3.py:361:            "evaluation_basis_sha256": VERDICT_BASIS_SHA256,
joulewise/analysis_manifest_v3.py:372:                "condition_family_sha256",
joulewise/analysis_manifest_v3.py:405:            "name": "phase_energy_j.decode",
joulewise/analysis_manifest_v3.py:423:            "metric": "phase_energy_j.decode",
joulewise/analysis_manifest_v3.py:437:def build_analysis_manifest_v3(campaign_dir: Path) -> dict[str, Any]:
joulewise/analysis_manifest_v3.py:442:    if hashlib.sha256(order_raw).hexdigest() != ROOT_ORDER_SHA256:
joulewise/analysis_manifest_v3.py:473:                "config_sha256": hashlib.sha256(config_raw).hexdigest(),
joulewise/analysis_manifest_v3.py:505:            "design_id": "splitwise_decode_cross_model_abba_v1",
joulewise/analysis_manifest_v3.py:508:            "unit_of_analysis": "abba_block_arm_mean_difference",
joulewise/analysis_manifest_v3.py:522:                "scheme": "deterministic_abba",
joulewise/analysis_manifest_v3.py:529:            "rule_id": "swdec_contrast_run_id_to_abba_block.v1",
joulewise/analysis_manifest_v3.py:574:            expected_sha = value.get("sha256", value.get("file_sha256"))
joulewise/analysis_manifest_v3.py:575:            if hashlib.sha256(raw).hexdigest() != expected_sha:
joulewise/analysis_manifest_v3.py:588:    digest = artifact.get("folded_sha256") or artifact.get("sha256")
joulewise/analysis_manifest_v3.py:592:        or artifact.get("algorithm") != "sha256"
joulewise/analysis_manifest_v3.py:597:    artifact.pop("sha256", None)
joulewise/analysis_manifest_v3.py:598:    artifact.pop("folded_sha256", None)
joulewise/analysis_manifest_v3.py:599:    artifact["digest_sha256"] = digest
joulewise/analysis_manifest_v3.py:603:def validate_analysis_manifest_v3(
joulewise/analysis_manifest_v3.py:633:            "design_id": "splitwise_decode_cross_model_abba_v1",
joulewise/analysis_manifest_v3.py:636:            "unit_of_analysis": "abba_block_arm_mean_difference",
joulewise/analysis_manifest_v3.py:639:                "scheme": "deterministic_abba",
joulewise/analysis_manifest_v3.py:670:            source.get("calibration_plan"),
joulewise/analysis_manifest_v3.py:671:            expected_source["calibration_plan"],
joulewise/analysis_manifest_v3.py:672:            "manifest.source.calibration_plan",
joulewise/analysis_manifest_v3.py:721:                            if hashlib.sha256(raw).hexdigest() != ref["file_sha256"]:
joulewise/analysis_manifest_v3.py:733:            "rule_id": "swdec_contrast_run_id_to_abba_block.v1",
joulewise/analysis_manifest_v3.py:764:                    "condition_family_sha256",
joulewise/analysis_manifest_v3.py:826:            errors.append(f"{where}: duplicate physical ABBA position")
joulewise/analysis_manifest_v3.py:829:        digest = entry.get("config_sha256")
joulewise/analysis_manifest_v3.py:838:                if not isinstance(digest, str) or hashlib.sha256(raw).hexdigest() != digest:
joulewise/analysis_manifest_v3.py:839:                    errors.append(f"{where}.config_sha256: source byte hash mismatch")
joulewise/analysis_engine/artifact.py:59:_AUTHENTICATED_SHA_BASIS_KEYS = {"kind", "sha256"}
joulewise/analysis_engine/artifact.py:60:_AUTHENTICATED_SHA_SET_BASIS_KEYS = {"kind", "sha256s"}
joulewise/analysis_engine/artifact.py:79:_INPUT_ARTIFACT_KEYS = {"manifest_id", "file_sha256"}
joulewise/analysis_engine/artifact.py:80:_INPUT_FLOOR_KEYS = {"artifact_id", "file_sha256", "embedded_bytes_base64"}
joulewise/analysis_engine/artifact.py:88:    "config_sha256",
joulewise/analysis_engine/artifact.py:89:    "expected_config_sha256",
joulewise/analysis_engine/artifact.py:90:    "manifest_config_sha256",
joulewise/analysis_engine/artifact.py:91:    "summary_sha256",
joulewise/analysis_engine/artifact.py:119:_CAMPAIGN_RAW_KEYS = {"path", "sha256", "records"}
joulewise/analysis_engine/artifact.py:395:    return "cv-" + hashlib.sha256(canonical_json_bytes(body)).hexdigest()
joulewise/analysis_engine/artifact.py:542:    hash_value = value.get("file_sha256")
joulewise/analysis_engine/artifact.py:544:        errors.append(f"{where}.file_sha256: must be 64 lowercase hex characters")
joulewise/analysis_engine/artifact.py:584:            == "abba_block_arm_mean_difference_t_v1"
joulewise/analysis_engine/artifact.py:848:def validate_claim_verdicts(value: Mapping[str, Any]) -> list[str]:
joulewise/analysis_engine/artifact.py:943:                        expected_sha256=floor_link.get("file_sha256"),
joulewise/analysis_engine/artifact.py:1017:                                "whole_window_evaluation_basis_sha256",
joulewise/analysis_engine/artifact.py:1018:                                "analysis_manifest_file_sha256",
joulewise/analysis_engine/artifact.py:1020:                            and isinstance(basis.get("sha256"), str)
joulewise/analysis_engine/artifact.py:1021:                            and SHA_RE.fullmatch(str(basis.get("sha256")))
joulewise/analysis_engine/artifact.py:1027:                        digests = basis.get("sha256s")
joulewise/analysis_engine/artifact.py:1030:                            == "floor_component_campaign_log_sha256"
joulewise/analysis_engine/artifact.py:1128:                "config_sha256",
joulewise/analysis_engine/artifact.py:1129:                "expected_config_sha256",
joulewise/analysis_engine/artifact.py:1130:                "summary_sha256",
joulewise/analysis_engine/artifact.py:1137:            manifest_config_sha = row["manifest_config_sha256"]
joulewise/analysis_engine/artifact.py:1141:                errors.append(f"{where}.manifest_config_sha256: must be a SHA-256")
joulewise/analysis_engine/artifact.py:1200:                    if not isinstance(raw_artifact["sha256"], str) or not SHA_RE.fullmatch(
joulewise/analysis_engine/artifact.py:1201:                        raw_artifact["sha256"]
joulewise/analysis_engine/artifact.py:1204:                            f"{where}.campaign_cooldown.raw_artifact.sha256: invalid"
joulewise/analysis_engine/artifact.py:2025:                ) != "abba_block_arm_mean_difference_t_v1":
joulewise/analysis_engine/artifact.py:2027:                        f"{where}.estimator.name: v3 floor requires the registered ABBA estimator"
joulewise/analysis_engine/artifact.py:2048:                        f"{where}.bundle_blocks.blocks: v3 requires all four physical ABBA positions"
joulewise/analysis_engine/artifact.py:3272:def validate_claim_verdicts_for_claim_index(value: Any) -> list[str]:
joulewise/analysis_engine/claims.py:19:from joulewise.calibration_ledger import REFUSAL_TAXONOMY
joulewise/analysis_engine/claims.py:34:# passing gate.  The three ``anchor``/``clock_anchor`` barriers are the
joulewise/analysis_engine/claims.py:57:        "clock_anchor_unresolved",
joulewise/analysis_engine/claims.py:58:        "instrument_calibration_missing",
joulewise/analysis_engine/claims.py:59:        "instrument_calibration_mismatch",
joulewise/analysis_engine/claims.py:60:        "instrument_calibration_invalid",
joulewise/analysis_engine/claims.py:61:        "instrument_calibration_stale",
joulewise/analysis_engine/claims.py:62:        "calibration_acceptance_bound_stale",
joulewise/analysis_engine/claims.py:63:        "instrument_calibration_bracket_missing",
joulewise/analysis_engine/claims.py:70:        "pulse_calibration_rollover_gate_timeout",
joulewise/analysis_engine/claims.py:133:        "calibration_bracket_exceeds_minted_bound",
joulewise/analysis_engine/claims.py:169:        "calibration_bracket_exceeds_minted_bound",
joulewise/analysis_engine/claims.py:252:def evaluate_claim(
joulewise/output_identity.py:16:    sha256_bytes,
joulewise/output_identity.py:36:    "config_sha256_unavailable",
joulewise/output_identity.py:67:    "run_id", "config_sha256", "requests_artifact_sha256",
joulewise/output_identity.py:68:    "request_tokens_artifact_sha256", "summary_sha256",
joulewise/output_identity.py:69:    "strict_validation_state", "strict_validation_report_sha256",
joulewise/output_identity.py:73:    "allowed_difference_pointers", "spec_off_projection_sha256",
joulewise/output_identity.py:74:    "spec_on_projection_sha256", "projections_equal",
joulewise/output_identity.py:79:    "spec_on_request_id", "spec_off_token_ids_sha256",
joulewise/output_identity.py:80:    "spec_on_token_ids_sha256", "spec_off_text_sha256",
joulewise/output_identity.py:81:    "spec_on_text_sha256", "output_token_count_equal",
joulewise/output_identity.py:104:        return hashlib.sha256(path.read_bytes()).hexdigest()
joulewise/output_identity.py:149:        sha256_bytes(canonical_json_bytes(payload)),
joulewise/output_identity.py:184:        (config_hash is None, "config_sha256_unavailable"),
joulewise/output_identity.py:195:        "config_sha256": config_hash,
joulewise/output_identity.py:196:        "requests_artifact_sha256": requests_hash,
joulewise/output_identity.py:197:        "request_tokens_artifact_sha256": tokens_hash,
joulewise/output_identity.py:198:        "summary_sha256": summary_hash,
joulewise/output_identity.py:200:        "strict_validation_report_sha256": strict_hash,
joulewise/output_identity.py:261:            "spec_off_projection_sha256": None,
joulewise/output_identity.py:262:            "spec_on_projection_sha256": None,
joulewise/output_identity.py:269:    off_hash = sha256_bytes(canonical_json_bytes(off_projection))
joulewise/output_identity.py:270:    on_hash = sha256_bytes(canonical_json_bytes(on_projection))
joulewise/output_identity.py:274:        "spec_off_projection_sha256": off_hash,
joulewise/output_identity.py:275:        "spec_on_projection_sha256": on_hash,
joulewise/output_identity.py:338:    off_tokens = off.get("emitted_token_ids_sha256") if isinstance(off, Mapping) else None
joulewise/output_identity.py:339:    on_tokens = on.get("emitted_token_ids_sha256") if isinstance(on, Mapping) else None
joulewise/output_identity.py:340:    off_text = off.get("response_text_sha256") if isinstance(off, Mapping) else None
joulewise/output_identity.py:341:    on_text = on.get("response_text_sha256") if isinstance(on, Mapping) else None
joulewise/output_identity.py:431:        "spec_off_token_ids_sha256": values["off_tokens"],
joulewise/output_identity.py:432:        "spec_on_token_ids_sha256": values["on_tokens"],
joulewise/output_identity.py:433:        "spec_off_text_sha256": values["off_text"],
joulewise/output_identity.py:434:        "spec_on_text_sha256": values["on_text"],
joulewise/output_identity.py:446:    return "oir-" + sha256_bytes(canonical_json_bytes(content))
joulewise/output_identity.py:516:def build_output_identity_report(
joulewise/output_identity.py:572:        ("spec_off_token_ids_sha256", "spec_off_token_ids_unavailable"),
joulewise/output_identity.py:573:        ("spec_on_token_ids_sha256", "spec_on_token_ids_unavailable"),
joulewise/output_identity.py:574:        ("spec_off_text_sha256", "spec_off_response_text_unavailable"),
joulewise/output_identity.py:575:        ("spec_on_text_sha256", "spec_on_response_text_unavailable"),
joulewise/output_identity.py:595:    off_tokens = request["spec_off_token_ids_sha256"]
joulewise/output_identity.py:596:    on_tokens = request["spec_on_token_ids_sha256"]
joulewise/output_identity.py:597:    off_text = request["spec_off_text_sha256"]
joulewise/output_identity.py:598:    on_text = request["spec_on_text_sha256"]
joulewise/output_identity.py:645:def validate_output_identity_report(
joulewise/output_identity.py:667:            "config_sha256", "requests_artifact_sha256",
joulewise/output_identity.py:668:            "request_tokens_artifact_sha256", "summary_sha256",
joulewise/output_identity.py:669:            "strict_validation_report_sha256",
joulewise/output_identity.py:683:            ("config_sha256", "config_sha256_unavailable"),
joulewise/output_identity.py:684:            ("requests_artifact_sha256", "requests_artifact_unavailable"),
joulewise/output_identity.py:685:            ("request_tokens_artifact_sha256", "request_tokens_artifact_unavailable"),
joulewise/output_identity.py:686:            ("summary_sha256", "summary_artifact_unavailable"),
joulewise/output_identity.py:693:        if (bundle["strict_validation_report_sha256"] is None) != strict_missing or (bundle["strict_validation_state"] == "unavailable") != strict_missing:
joulewise/output_identity.py:699:    for key in ("spec_off_projection_sha256", "spec_on_projection_sha256"):
joulewise/output_identity.py:708:    projection_missing = any(gate[key] is None for key in ("spec_off_projection_sha256", "spec_on_projection_sha256", "projections_equal"))
joulewise/output_identity.py:712:        gate["spec_off_projection_sha256"],
joulewise/output_identity.py:713:        gate["spec_on_projection_sha256"],
joulewise/output_identity.py:750:            ("spec_off_token_ids_sha256", "spec_off_token_ids_unavailable"),
joulewise/output_identity.py:751:            ("spec_on_token_ids_sha256", "spec_on_token_ids_unavailable"),
joulewise/output_identity.py:752:            ("spec_off_text_sha256", "spec_off_response_text_unavailable"),
joulewise/output_identity.py:753:            ("spec_on_text_sha256", "spec_on_response_text_unavailable"),
joulewise/output_identity.py:777:            "spec_off_token_ids_sha256",
joulewise/output_identity.py:778:            "spec_on_token_ids_sha256",
joulewise/output_identity.py:779:            "spec_off_text_sha256",
joulewise/output_identity.py:780:            "spec_on_text_sha256",
joulewise/suite.py:84:    "per_item_response_hash": "response_sha256",
joulewise/suite.py:96:            "suite_manifest_sha256",
joulewise/suite.py:119:            "prompt_sha256",
joulewise/suite.py:132:            "response_sha256",
joulewise/suite.py:458:    subset_sha256: str
joulewise/suite.py:472:                "subset_sha256",
joulewise/suite.py:485:            subset_sha256=_require_string(
joulewise/suite.py:486:                data.get("subset_sha256"), "source_manifest.subset_sha256"
joulewise/suite.py:575:    source_sha256: str
joulewise/suite.py:589:                "source_sha256",
joulewise/suite.py:611:            source_sha256=_require_string(
joulewise/suite.py:612:                data.get("source_sha256"), "items[].source.source_sha256"
joulewise/suite.py:737:    def validate(self) -> None:
joulewise/suite.py:876:    def validate(self) -> None:
joulewise/suite.py:1096:def suite_manifest_sha256(mapping: dict[str, Any]) -> str:
joulewise/suite.py:1105:    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
joulewise/suite.py:1113:    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
joulewise/calibration_bracketing.py:1:"""Claim-time pre/post powermetrics fiducial calibration bracketing.
joulewise/calibration_bracketing.py:3:The bracket carries a nonparametric 95/95 calibration-distribution bound into
joulewise/calibration_bracketing.py:19:from joulewise.calibration_ledger import (
joulewise/calibration_bracketing.py:36:    protocol_sha256,
joulewise/calibration_bracketing.py:41:BRACKET_SCHEMA = "joulewise.instrument_calibration_bracket.v1"
joulewise/calibration_bracketing.py:42:ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
joulewise/calibration_bracketing.py:44:    "joulewise.calibration_acceptance_bound.v2.fixture.v1"
joulewise/calibration_bracketing.py:46:ACCEPTANCE_EVALUATION_SCHEMA = "joulewise.calibration_acceptance_evaluation.v2"
joulewise/calibration_bracketing.py:50:    / "calibration"
joulewise/calibration_bracketing.py:51:    / "calibration_acceptance_d079_v2.json"
joulewise/calibration_bracketing.py:78:    manifest_sha256: str
joulewise/calibration_bracketing.py:79:    evidence_sha256: str
joulewise/calibration_bracketing.py:95:            "manifest_sha256": self.manifest_sha256,
joulewise/calibration_bracketing.py:96:            "evidence_sha256": self.evidence_sha256,
joulewise/calibration_bracketing.py:109:def _canonical_sha256(value: Mapping[str, Any]) -> str:
joulewise/calibration_bracketing.py:117:    return hashlib.sha256(raw).hexdigest()
joulewise/calibration_bracketing.py:151:def _current_estimator_code_sha256() -> dict[str, str] | None:
joulewise/calibration_bracketing.py:154:            relative: hashlib.sha256((_REPO_ROOT / relative).read_bytes()).hexdigest()
joulewise/calibration_bracketing.py:166:    core = {key: item for key, item in value.items() if key != "derivation_sha256"}
joulewise/calibration_bracketing.py:208:            and _valid_sha256(cutoff.get("head_digest"))
joulewise/calibration_bracketing.py:224:        or value.get("acceptance_id") != "d079_calibration_acceptance_v2_n19"
joulewise/calibration_bracketing.py:226:        or value.get("derivation_sha256") != _canonical_sha256(core)
joulewise/calibration_bracketing.py:234:        or prospective.get("protocol_sha256") != protocol_sha256(PROTOCOL_ID)
joulewise/calibration_bracketing.py:235:        or not isinstance(prospective.get("estimator_code_sha256"), Mapping)
joulewise/calibration_bracketing.py:236:        or set(prospective["estimator_code_sha256"]) != set(ESTIMATOR_CODE_PATHS)
joulewise/calibration_bracketing.py:238:            not _valid_sha256(item)
joulewise/calibration_bracketing.py:239:            for item in prospective["estimator_code_sha256"].values()
joulewise/calibration_bracketing.py:281:                "manifest_sha256",
joulewise/calibration_bracketing.py:282:                "instrument_evidence_sha256",
joulewise/calibration_bracketing.py:286:            or not _valid_sha256(member.get("manifest_sha256"))
joulewise/calibration_bracketing.py:287:            or not _valid_sha256(member.get("instrument_evidence_sha256"))
joulewise/calibration_bracketing.py:306:            or not _valid_sha256(observation.get("content_id"))
joulewise/calibration_bracketing.py:340:                "manifest.json": member["manifest_sha256"],
joulewise/calibration_bracketing.py:342:                    "instrument_evidence_sha256"
joulewise/calibration_bracketing.py:411:        != "max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s"
joulewise/calibration_bracketing.py:431:def load_calibration_acceptance_bound(
joulewise/calibration_bracketing.py:456:    expected_sha256 = {
joulewise/calibration_bracketing.py:460:    if hashlib.sha256(raw).hexdigest() != expected_sha256:
joulewise/calibration_bracketing.py:472:    pinned = load_calibration_acceptance_bound()
joulewise/calibration_bracketing.py:478:def _acceptance_artifact_sha256(artifact: Mapping[str, Any]) -> str:
joulewise/calibration_bracketing.py:488:def _valid_sha256(value: Any) -> bool:
joulewise/calibration_bracketing.py:525:        and binding_evidence.get("binding_vector_sha256")
joulewise/calibration_bracketing.py:526:        == hashlib.sha256(canonical).hexdigest()
joulewise/calibration_bracketing.py:528:        and binary.get("sha256") == bindings.get("powermetrics_sha256")
joulewise/calibration_bracketing.py:536:def load_calibration_candidate(
joulewise/calibration_bracketing.py:567:        if not _valid_sha256(expected) or hashlib.sha256(raw).hexdigest() != expected:
joulewise/calibration_bracketing.py:591:        or bindings.get("protocol_sha256") != protocol_sha256(str(protocol_id))
joulewise/calibration_bracketing.py:609:    artifact_hashes = evidence.get("artifact_sha256")
joulewise/calibration_bracketing.py:613:        != hashlib.sha256(events_raw).hexdigest()
joulewise/calibration_bracketing.py:615:        != hashlib.sha256(powermetrics_raw).hexdigest()
joulewise/calibration_bracketing.py:653:        manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
joulewise/calibration_bracketing.py:654:        evidence_sha256=hashlib.sha256(evidence_raw).hexdigest(),
joulewise/calibration_bracketing.py:665:    """Authenticate one valid ledger observation from its custody locator."""
joulewise/calibration_bracketing.py:669:    custody = Path(observation.custody_locator)
joulewise/calibration_bracketing.py:670:    candidate = load_calibration_candidate(
joulewise/calibration_bracketing.py:671:        custody,
joulewise/calibration_bracketing.py:672:        runs_root=custody.parent.parent,
joulewise/calibration_bracketing.py:683:        candidate.manifest_sha256
joulewise/calibration_bracketing.py:684:        != observation.artifact_sha256.get("manifest.json")
joulewise/calibration_bracketing.py:685:        or candidate.evidence_sha256
joulewise/calibration_bracketing.py:686:        != observation.artifact_sha256.get("instrument_evidence.json")
joulewise/calibration_bracketing.py:687:        or content_id_from_artifact_hashes(observation.artifact_sha256)
joulewise/calibration_bracketing.py:705:        relative_path=observation.custody_locator,
joulewise/calibration_bracketing.py:712:def discover_calibration_candidates(
joulewise/calibration_bracketing.py:784:def evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:801:            "calibration_bracket_max_drift_s": (
joulewise/calibration_bracketing.py:802:                policy.calibration_bracket_max_drift_s
joulewise/calibration_bracketing.py:810:        "calibration_drift_allowance_s": None,
joulewise/calibration_bracketing.py:823:        return result, ("instrument_calibration_bracket_missing",)
joulewise/calibration_bracketing.py:827:        load_calibration_acceptance_bound()
joulewise/calibration_bracketing.py:840:        return result, ("calibration_acceptance_bound_stale",)
joulewise/calibration_bracketing.py:842:    artifact_sha256 = _acceptance_artifact_sha256(artifact)
joulewise/calibration_bracketing.py:848:                "artifact_sha256": artifact_sha256,
joulewise/calibration_bracketing.py:849:                "authentication": "checked_in_genesis_fixture_byte_sha256_pin",
joulewise/calibration_bracketing.py:858:        return result, ("calibration_acceptance_bound_stale",)
joulewise/calibration_bracketing.py:864:            "artifact_sha256": artifact_sha256,
joulewise/calibration_bracketing.py:866:                "checked_in_issued_artifact_byte_sha256_pin"
joulewise/calibration_bracketing.py:868:                else "checked_in_genesis_fixture_byte_sha256_pin"
joulewise/calibration_bracketing.py:879:        return result, ("calibration_ledger_snapshot_required",)
joulewise/calibration_bracketing.py:892:        return result, ("calibration_ledger_baseline_missing",)
joulewise/calibration_bracketing.py:894:        return result, ("calibration_ledger_baseline_missing",)
joulewise/calibration_bracketing.py:899:            "calibration_bracket_max_drift_s_role": (
joulewise/calibration_bracketing.py:923:            "artifact_sha256": artifact_sha256,
joulewise/calibration_bracketing.py:925:                "checked_in_issued_artifact_byte_sha256_pin"
joulewise/calibration_bracketing.py:927:                else "checked_in_genesis_fixture_byte_sha256_pin"
joulewise/calibration_bracketing.py:931:            "derivation_sha256": artifact["derivation_sha256"],
joulewise/calibration_bracketing.py:938:            "trigger_guard_protocol_sha256": prospective["protocol_sha256"],
joulewise/calibration_bracketing.py:939:            "trigger_guard_estimator_code_sha256": dict(
joulewise/calibration_bracketing.py:940:                prospective["estimator_code_sha256"]
joulewise/calibration_bracketing.py:948:                "authenticated_calibration_ledger_snapshot_only"
joulewise/calibration_bracketing.py:970:        return result, ("calibration_acceptance_bound_stale",)
joulewise/calibration_bracketing.py:994:        return result, ("calibration_ledger_off_ledger_artifact",)
joulewise/calibration_bracketing.py:1006:            or candidate.manifest_sha256
joulewise/calibration_bracketing.py:1007:            != observation.artifact_sha256.get("manifest.json")
joulewise/calibration_bracketing.py:1008:            or candidate.evidence_sha256
joulewise/calibration_bracketing.py:1009:            != observation.artifact_sha256.get("instrument_evidence.json")
joulewise/calibration_bracketing.py:1011:            return result, ("calibration_ledger_off_ledger_artifact",)
joulewise/calibration_bracketing.py:1013:    # 59-pulse v3 protocol carries the governed 95/95 claim calibration.
joulewise/calibration_bracketing.py:1027:            return result, ("instrument_calibration_invalid",)
joulewise/calibration_bracketing.py:1034:        protocol_sha256(PROTOCOL_ID) != prospective.get("protocol_sha256")
joulewise/calibration_bracketing.py:1035:        or _current_estimator_code_sha256()
joulewise/calibration_bracketing.py:1036:        != dict(prospective["estimator_code_sha256"])
joulewise/calibration_bracketing.py:1075:        return result, ("calibration_observation_unclassifiable",)
joulewise/calibration_bracketing.py:1124:            "instrument_calibration_stale"
joulewise/calibration_bracketing.py:1126:            else "instrument_calibration_bracket_missing"
joulewise/calibration_bracketing.py:1139:        return result, ("instrument_calibration_invalid",)
joulewise/calibration_bracketing.py:1193:        return result, ("instrument_calibration_mismatch",)
joulewise/calibration_bracketing.py:1214:        return result, ("calibration_acceptance_bound_stale",)
joulewise/calibration_bracketing.py:1233:        return result, ("instrument_calibration_mismatch",)
joulewise/calibration_bracketing.py:1239:            "calibration_drift_allowance_s": float(allowance),
joulewise/calibration_bracketing.py:1256:def calibration_bracket_for_bundles(
joulewise/calibration_bracketing.py:1267:        empty, _ = evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:1276:        return empty, ("instrument_calibration_bracket_missing",)
joulewise/calibration_bracketing.py:1284:            calibration = metadata.get("instrument_calibration")
joulewise/calibration_bracketing.py:1285:            binding = calibration.get("bindings") if isinstance(calibration, Mapping) else None
joulewise/calibration_bracketing.py:1287:                raise ValueError("member omits calibration binding evidence")
joulewise/calibration_bracketing.py:1291:        empty, _ = evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:1300:        return empty, ("instrument_calibration_bracket_missing",)
joulewise/calibration_bracketing.py:1306:        empty, _ = evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:1315:        return empty, ("instrument_calibration_mismatch",)
joulewise/calibration_bracketing.py:1319:        candidates = discover_calibration_candidates(ledger_snapshot)
joulewise/calibration_bracketing.py:1326:            empty, _ = evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:1335:            return empty, ("calibration_ledger_custody_invalid",)
joulewise/calibration_bracketing.py:1336:    return evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:1352:    "calibration_bracket_for_bundles",
joulewise/calibration_bracketing.py:1353:    "discover_calibration_candidates",
joulewise/calibration_bracketing.py:1354:    "evaluate_calibration_bracket",
joulewise/calibration_bracketing.py:1355:    "load_calibration_acceptance_bound",
joulewise/calibration_bracketing.py:1356:    "load_calibration_candidate",
joulewise/bundle.py:7:  ``metadata.json`` and exposed as ``RunBundleWriter.config_sha256``.
joulewise/bundle.py:65:_EXPERIMENT_CUSTODY_LOCK_NAME = ".custody.lock"
joulewise/bundle.py:68:SOURCE_DIFF_IDENTITY_ALGORITHM = "sha256"
joulewise/bundle.py:244:    suffix = hashlib.sha256(config_bytes).hexdigest()[:4]
joulewise/bundle.py:249:    """Recognize the one terminal-verdict schema that has rejection custody."""
joulewise/bundle.py:266:    manifest publication must stop rather than replace unknown custody.
joulewise/bundle.py:288:def _experiment_custody_lock(experiments_dir: Path) -> Iterator[None]:
joulewise/bundle.py:426:                with _experiment_custody_lock(experiments_dir):
joulewise/bundle.py:484:    already exists, its custody wins: the rejection is written under
joulewise/bundle.py:514:        with _experiment_custody_lock(experiments_dir):
joulewise/bundle.py:636:    digest = hashlib.sha256()
joulewise/bundle.py:646:                content_digest = hashlib.sha256()
joulewise/bundle.py:655:                content_identity = hashlib.sha256(target).digest()
joulewise/bundle.py:675:        "diff_sha256": SOURCE_STATE_UNKNOWN,
joulewise/bundle.py:736:    diff_sha256 = SOURCE_STATE_UNKNOWN
joulewise/bundle.py:738:        digest = hashlib.sha256()
joulewise/bundle.py:747:        diff_sha256 = digest.hexdigest()
joulewise/bundle.py:754:        "diff_sha256": diff_sha256,
joulewise/bundle.py:776:        if state["diff_sha256"] == SOURCE_STATE_UNKNOWN:
joulewise/bundle.py:817:        config_sha256: str,
joulewise/bundle.py:824:        self._config_sha256 = config_sha256
joulewise/bundle.py:854:        config_sha256 = hashlib.sha256(config_bytes).hexdigest()
joulewise/bundle.py:860:            config_sha256=config_sha256,
joulewise/bundle.py:874:    def config_sha256(self) -> str:
joulewise/bundle.py:875:        return self._config_sha256
joulewise/bundle.py:949:            "config_sha256",
joulewise/bundle.py:970:            "config_sha256": self._config_sha256,
joulewise/whole_window.py:42:from joulewise.calibration_bracketing import (
joulewise/whole_window.py:43:    calibration_bracket_for_bundles,
joulewise/whole_window.py:44:    load_calibration_acceptance_bound,
joulewise/whole_window.py:46:from joulewise.calibration_ledger import (
joulewise/whole_window.py:48:    load_calibration_ledger_snapshot,
joulewise/whole_window.py:54:    _verify_instrument_calibration,
joulewise/whole_window.py:74:CONSUMPTION_PROVENANCE_PRECHECK_KEY = "calibration_rebracket_consumption"
joulewise/whole_window.py:128:        "calibration_ledger_missing",
joulewise/whole_window.py:129:        "calibration_ledger_malformed",
joulewise/whole_window.py:130:        "calibration_ledger_chain_conflict",
joulewise/whole_window.py:131:        "calibration_ledger_attempt_conflict",
joulewise/whole_window.py:132:        "calibration_ledger_content_conflict",
joulewise/whole_window.py:133:        "calibration_ledger_pending",
joulewise/whole_window.py:134:        "calibration_ledger_head_uncommitted",
joulewise/whole_window.py:135:        "calibration_ledger_head_mismatch",
joulewise/whole_window.py:136:        "calibration_ledger_rollback",
joulewise/whole_window.py:137:        "calibration_ledger_baseline_missing",
joulewise/whole_window.py:138:        "calibration_ledger_custody_invalid",
joulewise/whole_window.py:139:        "calibration_ledger_snapshot_required",
joulewise/whole_window.py:140:        "calibration_ledger_off_ledger_artifact",
joulewise/whole_window.py:141:        "calibration_observation_unclassifiable",
joulewise/whole_window.py:155:        "clock_anchor_unresolved",
joulewise/whole_window.py:156:        "instrument_calibration_missing",
joulewise/whole_window.py:157:        "instrument_calibration_mismatch",
joulewise/whole_window.py:158:        "instrument_calibration_invalid",
joulewise/whole_window.py:159:        "instrument_calibration_stale",
joulewise/whole_window.py:160:        "calibration_acceptance_bound_stale",
joulewise/whole_window.py:199:    "phase": "phase_energy_j",
joulewise/whole_window.py:395:        evaluation_basis_sha256: str | None = None,
joulewise/whole_window.py:397:        calibration_ledger_snapshot: CalibrationLedgerSnapshot | None = None,
joulewise/whole_window.py:398:        _allow_unissued_calibration_fixture: bool = False,
joulewise/whole_window.py:410:        self.evaluation_basis_sha256 = evaluation_basis_sha256
joulewise/whole_window.py:412:        self.calibration_ledger_snapshot = calibration_ledger_snapshot
joulewise/whole_window.py:413:        self._allow_unissued_calibration_fixture = (
joulewise/whole_window.py:414:            _allow_unissued_calibration_fixture
joulewise/whole_window.py:416:        if self.calibration_ledger_snapshot is None:
joulewise/whole_window.py:417:            acceptance = load_calibration_acceptance_bound()
joulewise/whole_window.py:423:            self.calibration_ledger_snapshot = load_calibration_ledger_snapshot(
joulewise/whole_window.py:431:        self.calibration_bracket: Mapping[str, Any] | None = None
joulewise/whole_window.py:487:        if self.calibration_ledger_snapshot is None:
docs/contracts/analysis_plans.md:26:| Estimator/formula | Estimator and formula, including fixed, marginal, categorical, paired, or equivalence terms. |
docs/contracts/analysis_plans.md:32:| Holdout cells (L3 only) | Named holdout cells and prediction-error rule for L3 plans; write `not applicable` for L2 plans. |
docs/contracts/analysis_plans.md:106:### AP-1: Q4 fixed+marginal grid fit
docs/contracts/analysis_plans.md:110:| Plan ID / RQ consumer | AP-1 / Q4 fixed-vs-marginal energy model; feeds Q5 rank rules and Phase 4 F9 (C-014). |
docs/contracts/analysis_plans.md:113:| selection_scope | Frozen target/model/profile 4x3 prompt `{128,512,2048,4096}` x decode `{64,256,512}` grid, its predeclared fixed/prompt/decode terms, and the named holdout cells. |
docs/contracts/analysis_plans.md:114:| multiplicity_rule | Holm within FAM-Q4-GRID-MODEL across confirmatory fixed/prompt/decode contrasts and holdout pass/fail claims; linear/log sensitivity terms are secondary unless frozen as primary before execution. |
docs/contracts/analysis_plans.md:117:| Estimator/formula | Primary fit is categorical-additive: `E = fixed + prompt_level + decode_level` on the 4x3 grid prompt `{128,512,2048,4096}` x decode `{64,256,512}`. Linear/log sensitivity is secondary. |
docs/contracts/analysis_plans.md:119:| Order/blocking/covariates | Interleaved or recorded manifest order; block/session and drift sentinel terms available as covariates; no curvature term promoted unless categorical residuals and holdouts clear the floor. |
docs/phase_2/phase_2_plan.md:709:`q4_l3_shape_grid_v1` campaign and the content-sensitivity sentinel; claim
docs/phase_2/phase_2_plan.md:755:| `q4_l3_shape_grid_v1` | categorical fixed+prompt+decode grid with holdouts | Q4 L3 fit, Q5 | Window B; 2 models; prompt `{128,512,2048,4096}` x decode `{64,256,512}`; n sized from Window A |
docs/phase_2/phase_2_plan.md:768:CV/floor/MDE. Window B runs `q4_l3_shape_grid_v1` with n sized from Window
docs/phase_2/phase_2_plan.md:769:A results plus the content-sensitivity sentinel. `q4_l3_shape_grid_v1`
docs/phase_2/phase_2_plan.md:770:uses [QUIET-MAC] Window B, two models, the AP-1 4x3 grid, holdouts
docs/phase_2/suite_implementation_research.md:124:**New module `joulewise/suite.py`** (stdlib-only, mirrors `schemas.py` style): dataclasses `SuiteManifest`, `SuiteGenerator`, `AnalysisContract`, `ExecutionPolicy`, `SourceManifest`, `SuiteItem`, `ItemShape`, `ItemSource`, `ItemGrouping`, `ItemDifficulty` — exactly the trimmed C-015 field sketch (bank lines 176–253), each with `from_mapping` validation, `to_dict`, plus `load_suite_manifest(path)` and `suite_manifest_sha256(dict)`. Item prompt source rule: exactly one of `prompt_text` (materialized at manifest-build time — generators run offline, never at execution) or `shape.planned_prompt_tokens` (synthetic). `difficulty` is pass-through quarantined metadata `{axis, value, scale, label, source, quarantine_note}` — validated shape, no behavior. Deferred fields (`scoring.*`, `pair_id`, `holdout_role`, import fields) are **rejected as unknown keys** so the deferral is enforced, not silent.
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:45:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:48:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:81:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:84:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:117:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:120:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:153:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:156:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:189:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:192:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:225:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:228:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:261:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:264:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:297:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:300:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:333:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:336:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:369:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:372:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:405:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:408:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:441:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:444:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:477:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:480:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:513:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:516:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:549:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:552:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:585:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:588:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:621:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:624:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:657:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:660:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:693:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:696:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:729:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:732:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:765:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:768:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:801:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:804:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:837:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:840:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:873:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:876:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:909:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:912:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:945:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:948:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:981:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:984:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1017:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1020:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1053:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1056:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1089:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1092:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1125:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1128:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1161:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1164:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1197:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1200:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1233:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1236:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1269:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1272:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1305:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1308:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1341:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1344:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1377:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1380:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1413:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1416:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1449:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1452:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1485:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1488:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1521:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1524:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1557:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1560:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1593:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1596:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1629:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1632:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1665:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1668:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1701:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1704:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1737:        "decode_level": "256_tokens",
configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:1740:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:45:        "decode_level": "256_tokens",
configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:48:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:596:        "decode_level": "256_tokens",
configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:599:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:1147:        "decode_level": "256_tokens",
configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:1150:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:1698:        "decode_level": "256_tokens",
configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:1701:        "prompt_level": "512_tokens"
configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:2249:        "decode_level": "256_tokens",
configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:2252:        "prompt_level": "512_tokens"
configs/suite_manifests/mock_suite_manifest.json:50:        "prompt_level": "short",
configs/suite_manifests/mock_suite_manifest.json:51:        "decode_level": "short"
configs/suite_manifests/mock_suite_manifest.json:85:        "prompt_level": "short",
configs/suite_manifests/mock_suite_manifest.json:86:        "decode_level": "short"
configs/suite_manifests/mock_suite_manifest.json:121:        "prompt_level": "short",
configs/suite_manifests/mock_suite_manifest.json:122:        "decode_level": "short"
configs/suite_manifests/mock_suite_manifest.json:157:        "prompt_level": "short",
configs/suite_manifests/mock_suite_manifest.json:158:        "decode_level": "short"
configs/suite_manifests/mock_suite_manifest.json:193:        "prompt_level": "short",
configs/suite_manifests/mock_suite_manifest.json:194:        "decode_level": "short"
configs/suite_manifests/affine_smoke_v1.json:44:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:47:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:83:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:86:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:120:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:123:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:157:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:160:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:194:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:197:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:231:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:234:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:268:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:271:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:305:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:308:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:342:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:345:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:379:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:382:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:416:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:419:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:453:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:456:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:490:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:493:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:527:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:530:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:564:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:567:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:601:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:604:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:638:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:641:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:675:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:678:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:712:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:715:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:749:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:752:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:786:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:789:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:823:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:826:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:860:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:863:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:897:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:900:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:934:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:937:        "prompt_level": "affine_fixed_text_raw_completion"
configs/suite_manifests/affine_smoke_v1.json:971:        "decode_level": "answer_only_natural_eos_budget_16",
configs/suite_manifests/affine_smoke_v1.json:974:        "prompt_level": "affine_fixed_text_raw_completion"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen3-4b.json:46:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen3-4b.json:49:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen3-4b.json:596:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen3-4b.json:599:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen3-4b.json:1146:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen3-4b.json:1149:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen3-4b.json:1696:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen3-4b.json:1699:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen3-4b.json:2246:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen3-4b.json:2249:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_olmoe-1b-7b.json:46:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_olmoe-1b-7b.json:49:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_olmoe-1b-7b.json:596:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_olmoe-1b-7b.json:599:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_olmoe-1b-7b.json:1146:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_olmoe-1b-7b.json:1149:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_olmoe-1b-7b.json:1696:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_olmoe-1b-7b.json:1699:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_olmoe-1b-7b.json:2246:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_olmoe-1b-7b.json:2249:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen35-122b.json:46:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen35-122b.json:49:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen35-122b.json:596:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen35-122b.json:599:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen35-122b.json:1146:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen35-122b.json:1149:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen35-122b.json:1696:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen35-122b.json:1699:        "prompt_level": "512_tokens"
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen35-122b.json:2246:        "decode_level": "256_tokens",
configs/campaigns/exploratory_2026_07_17/suite_manifests/jw_sentinel_v1_qwen35-122b.json:2249:        "prompt_level": "512_tokens"

exec
/bin/zsh -lc "rg -n '"'^## AP-|Q4|fixed|holdout|boundary|wall|phase|additivity|energy model'"' docs/contracts/analysis_plans.md | head -220; sed -n '1,180p' docs/contracts/analysis_plans.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
24:| Metric + exact window class | Metric name and exact window class: gross request, idle-subtracted request, static-batch gross group, phase window, item window, level window, or session window. A static-batch group is not relabeled as a request, and request windows within an overlapping group carry no per-request energy attribution. |
26:| Estimator/formula | Estimator and formula, including fixed, marginal, categorical, paired, or equivalence terms. |
30:| MDE/n sizing + predeclared top-up rule | Planned n, MDE arithmetic, and the predeclared replacement rule. Per D-062 (the ONE normative statement; AP rows point here): confirmatory n is FROZEN at registry freeze from Window-A variance/MDE evidence (nearer 10 than 5 for near-floor contrasts), embedded in the frozen registry artifact, and covered by that artifact's hash; n is not a mutable generator/runtime parameter. Technically invalid runs are replaced under the predeclared replacement rule and are not top-ups. Any outcome-dependent top-up permanently DEMOTES the contrast to exploratory — the original fixed-n analysis is reported regardless of direction, pooled estimates never carry nominal confirmatory coverage, and no later re-promotion occurs. |
32:| Holdout cells (L3 only) | Named holdout cells and prediction-error rule for L3 plans; write `not applicable` for L2 plans. |
64:  request-energy shape contrasts, within-boundary ranks, equivalence tests,
84:- Phase metrics are GROSS-only until phase-idle modeling exists (C-014/D-032).
99:  Request/burst bundles instead report the separately named decode-phase
106:### AP-1: Q4 fixed+marginal grid fit
110:| Plan ID / RQ consumer | AP-1 / Q4 fixed-vs-marginal energy model; feeds Q5 rank rules and Phase 4 F9 (C-014). |
111:| family_id | FAM-Q4-GRID-MODEL |
113:| selection_scope | Frozen target/model/profile 4x3 prompt `{128,512,2048,4096}` x decode `{64,256,512}` grid, its predeclared fixed/prompt/decode terms, and the named holdout cells. |
114:| multiplicity_rule | Holm within FAM-Q4-GRID-MODEL across confirmatory fixed/prompt/decode contrasts and holdout pass/fail claims; linear/log sensitivity terms are secondary unless frozen as primary before execution. |
115:| Metric + exact window class | `gross_energy_j` (gross request window) and `energy_request_j` (idle-subtracted request window); phase terms may be reported gross-only and only when window samples clear the standing rule (C-014). |
117:| Estimator/formula | Primary fit is categorical-additive: `E = fixed + prompt_level + decode_level` on the 4x3 grid prompt `{128,512,2048,4096}` x decode `{64,256,512}`. Linear/log sensitivity is secondary. |
119:| Order/blocking/covariates | Interleaved or recorded manifest order; block/session and drift sentinel terms available as covariates; no curvature term promoted unless categorical residuals and holdouts clear the floor. |
120:| Floor gate | pending-P2-015: `max(floor_abs_j, floor_cmp_j)` for request windows and any reported phase window. |
123:| Holdout cells (L3 only) | `(512,256)` and `(4096,512)` held-out in-grid corner predictions (interaction/additivity validation — both factor levels occur in the training grid, so neither is statistical extrapolation); prediction errors must clear the AP-1 floor gate. No extrapolation claim is available from this grid. |
132:| Plan ID / RQ consumer | AP-2 / Slice 2M qualitative prefill/decode asymmetry; supports Q4 substrate only (C-014). |
136:| multiplicity_rule | Holm within FAM-2M-SHAPE-CONTRASTS across the predeclared request-energy and resolvable gross phase-window contrasts; unplanned metric or profile contrasts are exploratory. |
137:| Metric + exact window class | Gross request energy, idle-subtracted request energy, gross phase-window energy, mean power, TTFT, and runtime-observed output-token companion metrics. |
142:| Floor gate | pending-P2-015: `max(floor_abs_j, floor_cmp_j)` for request and gross phase windows. |
146:| Claim ceiling + exact forbidden upgrade | Ceiling L2. Forbidden upgrade: no L3 fixed+prefill+decode fit from the four-cell 2M matrix. |
172:### AP-3: Q5 within-boundary rank stability
176:| Plan ID / RQ consumer | AP-3 / Q5 within-boundary ranking stability; Phase 4 F10 (C-014). |
179:| selection_scope | Frozen same-boundary candidate set for each workload shape, metric, model/quant set, and session block included in the ranking campaign. |
180:| multiplicity_rule | Holm within each frozen same-boundary workload-shape x metric rank family; any expanded all-pairs or cross-shape ranking sweep uses Benjamini-Hochberg at q=0.10 and is labeled secondary/exploratory according to the frozen registry. |
181:| Metric + exact window class | Same-boundary request-energy, runtime-observed energy/output-token, `inter_token_throughput_tokens_s`, and latency metrics on request windows. |
182:| Unit of analysis + dependence structure | Bundle-level repetitions within same workload shape, boundary, model/quant, and session block. |
185:| Order/blocking/covariates | Same manifest order where possible; block/session drift covariate from sentinels; no cross-boundary rank upgrade without D-018 calibration evidence. |
190:| Claim ceiling + exact forbidden upgrade | Ceiling L2 within boundary. Forbidden upgrade: cross-device/device ranking unless hardware and boundary calibration gates are met. |
191:| Disqualifiers + not-resolvable conditions | Rank gap <= comparison MDE, boundary mismatch without calibration, capped prompt mismatch, or quality contamination gives `unresolved tie` or descriptive L1. |
201:| selection_scope | Frozen common-shape synthetic and realistic item categories at `512/256 fixed_budget_exact`, limited to the categories and source manifests named before execution. |
203:| Metric + exact window class | Request energy on the common `512/256 fixed_budget_exact` shape; optional gross phase-window descriptors only. |
210:| Denominator provenance requirement | Runtime-observed emitted tokens and stop reasons; source-manifest hashes and `fixed_budget_exact` policy recorded per item. |
228:| Inclusion/exclusion + quality-flag waiver rules | Strict-valid bundles; envelope-validation smoke gate must pass before any scored campaign; correctness remains quarantined annotation under C-004. Threshold definitions, design rationale, and the pre-data sensitivity record live in `docs/phase_2/suite_implementation_research.md` §3 under D-047.3/D-047.7; empirical robustness is deferred to the first strict-valid smoke/P2-015 evidence and cannot be used for outcome-dependent retuning. |
297:  n-1 under the frozen guard, phase metric-path enforcement) are specified in
298:  `docs/phase_2/detection_floor.md` Section 5 — the ONE home; this section
# Analysis Plans

Status: binding for reader-facing L2/L3 claims adopted on 2026-07-08
(C-014). This contract rides `docs/contracts/claims_ladder.md` (D-037):
from adoption, any reader-facing L2 or L3 claim must cite a filled
analysis-plan row before the claim is drafted. Amendment 2026-07-09
pending ratification (C-023 S3): reader-facing L2/L3 claims also need
analysis-registry fields for claim role, selection scope, multiplicity, and
contrast-level inference wording.

The plan is a compact table, not a prose ritual (C-014). A comparison that
cannot fill the fields below is not eligible for L2/L3 wording. It may
remain L0/L1 capability or instrument-result language under D-037.

## Required fields

| Field | Requirement |
|---|---|
| Plan ID / RQ consumer | Stable analysis-plan ID and the question or consumer it serves. |
| family_id | Stable multiplicity family ID; the family is the complete frozen set of claim-bearing contrasts generated by the same selection opportunity. |
| claim_role | One of `primary`, `secondary`, or `exploratory`; primary and secondary roles must be frozen before campaign execution. |
| selection_scope | The exact metric/window/cell/category/model/shape/search space examined to find or support this claim; must be narrow enough that a reviewer can count what was searched. |
| multiplicity_rule | Named rule for the family: Holm for small confirmatory families; Benjamini-Hochberg with the declared q level for sweeps; or explicitly exploratory/no confirmatory inference. |
| Metric + exact window class | Metric name and exact window class: gross request, idle-subtracted request, static-batch gross group, phase window, item window, level window, or session window. A static-batch group is not relabeled as a request, and request windows within an overlapping group carry no per-request energy attribution. |
| Unit of analysis + dependence structure | Bundle, level, item, session, or block; itemized suites require bundle- or block-level uncertainty and must never treat item windows as independent replicates unless a stronger repeated-bundle design is named. |
| Estimator/formula | Estimator and formula, including fixed, marginal, categorical, paired, or equivalence terms. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-validation rule, exclusion causes, and any quality-flag waiver rule allowed by D-014/D-037. |
| Order/blocking/covariates | Manifest order, blocking variables, drift terms, covariates, and any limits on covariate count. |
| Floor gate | `max(floor_abs_j, floor_cmp_j)` from the P2-015 calibration artifact for the same metric/window class. |
| MDE/n sizing + predeclared top-up rule | Planned n, MDE arithmetic, and the predeclared replacement rule. Per D-062 (the ONE normative statement; AP rows point here): confirmatory n is FROZEN at registry freeze from Window-A variance/MDE evidence (nearer 10 than 5 for near-floor contrasts), embedded in the frozen registry artifact, and covered by that artifact's hash; n is not a mutable generator/runtime parameter. Technically invalid runs are replaced under the predeclared replacement rule and are not top-ups. Any outcome-dependent top-up permanently DEMOTES the contrast to exploratory — the original fixed-n analysis is reported regardless of direction, pooled estimates never carry nominal confirmatory coverage, and no later re-promotion occurs. |
| Denominator provenance requirement | Runtime-observed, config fallback, scored denominator, or source-manifest denominator; config fallback cannot carry L2/L3 per-token claims under D-037. |
| Holdout cells (L3 only) | Named holdout cells and prediction-error rule for L3 plans; write `not applicable` for L2 plans. |
| Claim ceiling + exact forbidden upgrade | Maximum allowed claim level and the exact stronger claim that remains forbidden. |
| Disqualifiers + not-resolvable conditions | Conditions that force downgrade, `not resolvable`, or `not estimable` wording. |
| Linked manifests/bundle hashes | Manifest IDs and bundle hashes; filled post-execution before claims are published. |

## Analysis Registry

Amendment 2026-07-09 pending ratification (C-023 S3): the analysis registry
is the frozen claim-facing view of this table plus campaign-specific
manifest IDs, family IDs, claim roles, selection scopes, and multiplicity
rules.

Pointer 2026-07-09: mechanical checks: `scripts/claims_lint.py`.

- The registry is FROZEN before each campaign's execution. The freeze
  records the AP rows in scope, the campaign manifest hash or planned
  manifest ID, and the complete frozen set of claim-bearing contrasts
  generated by the same selection opportunity.
- The frozen registry enumerates each claim-bearing `contrast_id` with its
  family, role, metric/window class, cells/categories/models,
  estimator/coding, alpha or q, and the exact Holm/BH denominator `m`.
- Post-execution claims, metrics, subsets, model/quant/shape cells, or
  contrasts that do not match an enumerated frozen `contrast_id` are labeled
  `exploratory` and cannot carry primary/secondary L2/L3 wording until a
  later campaign freezes them prospectively.
- Small confirmatory families use Holm adjustment within family. Broad
  sweeps use Benjamini-Hochberg at the declared q level or are labeled
  explicitly exploratory with no confirmatory inference. BH item-level
  sweeps are limited to correctness or difficulty-metadata summaries unless
  a repeated-bundle/block design is named; item-window energy sweeps remain
  exploratory and cannot carry L2/L3 energy inference.
- Family IDs are local to an estimand family, not a whole paper section:
  request-energy shape contrasts, within-boundary ranks, equivalence tests,
  ladder correctness/energy accounting, and content-sentinel contrasts are
  separate families unless a frozen campaign explicitly searches across
  them.

## Standing reporting rules

- Unpaired MDE reference arithmetic at n=5 is pinned by C-014: for
  two-condition comparisons, `MDE95 ~= 1.46 x CV` and approximately 80%-power
  `MDE ~= 2.0 x CV` using the t-based factor
  `(t_.975,8 + t_.80,8) * sqrt(2/5) = (2.306+0.889)*0.632 ~= 2.02`.
  Observed CV anchors are 0.3% in the flagship
  Qwen3.5-122B run report, 1.4% gross in the first real-energy run
  report, and 7.4% contaminated idle-subtracted in the same first
  real-energy report (docs/run_reports/2026-07-07-flagship-qwen35-122b.md;
  docs/run_reports/2026-07-06-slice-2i-first-real-energy.md).
- Paired/block designs use paired arithmetic for gates. Compute the
  contrast on block differences, with CI half-width
  `t_.975,n_blocks-1 * s_d / sqrt(n_blocks)`, and compute the power MDE on
  the same contrast-scale standard deviation `s_d`.
- Phase metrics are GROSS-only until phase-idle modeling exists (C-014/D-032).
  They must not be mixed with idle-subtracted request headlines.
- Short-prefill windows with fewer than 3 samples report `not resolvable`,
  never near-zero point values (C-014).
- Capped `long_short` cells are excluded from prompt-slope and rank claims
  unless realized prompt lengths match across compared cells (C-014).
- Rank claims require rank gap > comparison MDE; otherwise the wording is
  `unresolved tie` (C-014).
- Reader-facing steady-state decode-throughput claims use
  `inter_token_throughput_tokens_s`, the N−1 inter-token-interval convention,
  only when every committed output token in scope has a genuine per-token
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
| Order/blocking/covariates | Counterbalanced order manifest; drift sentinel at start/end of each model block with block position recorded as a covariate (C-014/P2-021). |
| Floor gate | pending-P2-015: `max(floor_abs_j, floor_cmp_j)` for request and gross phase windows. |
| MDE/n sizing + predeclared top-up rule | n frozen at registry freeze (D-062): `sampling_plan.planned_n_blocks` is authored as n=5 from D-014 or n=10 only if Window-A evidence marks the contrast near-floor, then hash-bound in the frozen AP-2 registry artifact before generation. Sizing/top-up is governed by the D-062 clause above (frozen n; no runtime override; outcome-dependent growth demotes to exploratory). |
| Denominator provenance requirement | Runtime-observed output tokens and stop reasons for per-token/per-output tables; config fallback remains QA-only. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | Ceiling L2. Forbidden upgrade: no L3 fixed+prefill+decode fit from the four-cell 2M matrix. |
| Disqualifiers + not-resolvable conditions | Below-floor differences, short-prefill <3 samples, missing sentinel/block metadata, or capped prompt mismatch force `not resolvable` or L1 wording. |
| Linked manifests/bundle hashes | pending post-execution. |

### AP-SPEC: matched-output speculative-decode contrast

| Field | Value |
|---|---|
| Plan ID / RQ consumer | AP-SPEC / C5-2.5 plus C-023-OUTPUT-IDENTITY; speculative-on versus speculative-off under matched output policy and exact config projection. |
| family_id | One separately frozen family per mechanism: `FAM-AXI-SPEC-DRAFT-MATCHED-OUTPUT` or `FAM-AXI-SPEC-NATIVE-MTP-MATCHED-OUTPUT`; never pooled. |
| claim_role | primary |
| selection_scope | One frozen target stack, request roster, sampler/output policy, batch policy, paired spec-off/spec-on configuration, manifest digest, planned n, and exhaustive contrast-ID set; only the four speculation config pointers frozen by the AXI-SA contract may differ. |
| multiplicity_rule | Holm at alpha 0.05 across the primary paired execution-unit gross-energy contrast and gross-per-committed-output-token companion; accepted-draft energy is a spec-on mechanism diagnostic, not an on/off contrast. |
| Metric + exact window class | Primary `gross_energy_j` on `gross_request` for single-request mode or `batch_group_gross_energy_j` on `gross_batch_group` for static-batch mode; companion `gross_energy_per_committed_output_token_j`; diagnostic `gross_energy_per_accepted_draft_token_j` for spec-on only. Static group energy is never stored or analyzed under a request-scoped name. |
| Unit of analysis + dependence structure | Paired bundle within counterbalanced block. Static B>1 energy is group-gross; request events provide latency/count/output evidence and are not independent energy replicates. |
| Estimator/formula | Primary mean of paired `spec_on - spec_off` execution-unit gross-energy differences. Token companions use ratio of arm totals, never mean request/event ratios. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid event-semantics-v2 bundles only; exact config-projection match and a C-023 output-identity report are mandatory. Ordinary D-014/D-037 exclusions apply. |
| Order/blocking/covariates | Counterbalanced on/off order within frozen blocks; pair ID, block ID, planned replicate, request roster, and counterpart entry are manifest-bound. |
| Floor gate | pending-P2-015: `max(floor_abs_j, floor_cmp_j)` for the same `gross_request` or `gross_batch_group` window under an explicit equal-or-harder transport rule; otherwise a dedicated calibration cell is required. |
| MDE/n sizing + predeclared top-up rule | Every v2 registry freezes non-null paired n and binds exactly one manifest ID and byte digest before dispatch. A front-frozen mock registry fixes its mock n; after Window-A variance/MDE, a new campaign-frozen registry fixes claim-bearing n. The manifest has exactly n pairs, 2n entries, and contiguous unique replicate indices. The closed technical-invalid set is `dispatch_failed_before_bundle_creation` and `strict_bundle_invalid`, each with the AXI-SA predicate; unknown reasons count eligible. Every attempt is ledgered, and analysis uses first-eligible-per-cell by ascending attempt ordinal. Any outcome-dependent added/substituted pair, manifest, attempt selection, or retry after eligibility is refused as `outcome_dependent_topup_forbidden`; AP-SPEC permits no post-hoc top-up or pair subset. |
| Denominator provenance requirement | Runtime-observed committed output tokens for the on/off companion; runtime-observed accepted draft/MTP tokens for the spec-on diagnostic. Spec-off accepted-token denominator is null, never zero. |
| Holdout cells (L3 only) | not applicable. |
| Claim ceiling + exact forbidden upgrade | Ceiling L2. Forbidden upgrade: no generic speculative-decoding, serving, hardware, or quality conclusion from one stack/pair; no matched-decoded-work claim unless output state is `exact_token_match`. |
| Disqualifiers + not-resolvable conditions | Output state other than exact token match, unexpected config difference, missing request evidence, pending/invalid floor selector, below-floor effect, zero committed denominator, or missing counter instrumentation forces the frozen divergence disposition, `not resolvable`, or L0/L1 wording. |
| Linked manifests/bundle hashes | Registry `planned_manifest_id` and `planned_manifest_sha256`, the complete contrast-ID set, registry semantic digest, configs, and roster are hash-bound before any mock or live AP-SPEC dispatch; the canonical complete attempt-ledger hash, bundle hashes, and immutable execution/report links are filled post-execution without mutating the manifest. |

### AP-3: Q5 within-boundary rank stability

| Field | Value |
|---|---|
| Plan ID / RQ consumer | AP-3 / Q5 within-boundary ranking stability; Phase 4 F10 (C-014). |
| family_id | FAM-Q5-WITHIN-BOUNDARY-RANKS |
| claim_role | primary |
| selection_scope | Frozen same-boundary candidate set for each workload shape, metric, model/quant set, and session block included in the ranking campaign. |
| multiplicity_rule | Holm within each frozen same-boundary workload-shape x metric rank family; any expanded all-pairs or cross-shape ranking sweep uses Benjamini-Hochberg at q=0.10 and is labeled secondary/exploratory according to the frozen registry. |

exec
/bin/zsh -lc "sed -n '2039,2177p' RUN_STATE.md; sed -n '2178,2255p' RUN_STATE.md; sed -n '2739,2837p' RUN_STATE.md; sed -n '213,305p' TASK_QUEUE.md; sed -n '306,390p' TASK_QUEUE.md; sed -n '1,380p' docs/orchestration.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## ACTIVE_STOP_CARD

Status: NONE — no stop card is active. Stop-card authority: D-050 / D-063 ([decision log](docs/decision_log.md)).

## Active Global Work-Selection Gates

NONE — no global work-selection gate is active.

## Restart By Machine-State Lane

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-05). Latest report: [16h runway checkpoint 2026-08-03: D-108..D-112 minted; kernel pins 60; CAL-BRACKET held at 2e61ff9 (rule-11 gate owed for B1 round 2); winB license exhausted as drawn (r06 disposition parked, WINB-R06-DISPOSITION-01); mint chain D-110-blocked; CLAIMS_STATUS §1 honestly NONE; checkpoint block at the top of RUN_STATE is the successor resume script.](docs/run_reports/2026-08-03-16h-runway.md).

### [ED-EXTERNAL]

- READY — E1 `P1-008`: Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).

### [QUIET-MAC]

- READY — Q2 `P2-006`: Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison.

### [AGENT]

- READY — A0 `P2-035`: RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests).

<!-- END GENERATED: state-kernel run-state-intake -->

## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open

The RESUME list from the 2026-07-17 checkpoint is fully executed. The
relaunched execution-lens review, fix rounds 1-2, and their delta
re-audits had already run earlier on 2026-07-18 (commits `1aebf14`,
`6d80039`); this session closed the surviving P1 (child accepted any
JSON object as the frozen cooldown anchor) plus every finding from four
further delta re-audits, as fix rounds 3-8 in commit `ad0920b`:
canonical anchor validator (`joulewise/cooldown_anchor.py`) enforced
fail-closed at parent/CLI/controller boundaries; collision-safe,
crash-atomic, flock-serialized rejection-verdict custody
(`experiments/rejections/`); physical-domain baseline validation (the
`inf`-anchor fail-open gate is closed); discriminating process-race
regression. Suite green lead-side at every round boundary, final
`Ran 1746 tests`, `OK (skipped=12)`. Awake-half live probe validation
passed on real hardware (zero probe errors); the Ventura screensaver is
now disabled on the machine (`idleTime = 0`). PR #77 carries the gate
narrative; merge is Ed's call. Full record:
`docs/run_reports/2026-07-18-d077-fix-rounds.md`. Tooling: codex-run-v3
xhigh review-genre sessions ended with null final messages 4x
(bridge-resume recovered each; personal-tooling defect, recorded in the
run report and the global codex-delegation skill field notes, not the
repo queue).

## CHECKPOINT 2026-07-18: Claude script bridge runs in the pet's app task

The actual Claude Code fallback route is `scripts/codex-bridge`, not the MCP
server for recent audited work. The wrapper now sends `new` and `review` turns
through a dedicated app-owned Codex desktop task when the local host id is
configured. This is the same local-conversation state the native pet consumes;
the prior observer-only diagnosis was incorrect because the pet never reads
`~/.codex/claude-spawned/index.jsonl`. A live Sol/high smoke appeared in the
Codex app as thread `019f77a6-3612-7332-9f5e-be9fbde56be5`, turn
`019f77a9-2827-7de1-accf-ac2eda21927e`, and returned
`JOULEWISE_NATIVE_PET_BRIDGE_OK` through the script. Adaptive effort remains
unchanged: `high` fallback/default, `xhigh` only on named hard-task triggers,
and `ultra` only for sessions that must spawn subagents. Full record:
`docs/run_reports/2026-07-18-claude-codex-pet-observer.md`.

Committed 2026-07-18 on `impl/env-guard-cooldown` (after the D-077
packet boundary `6d80039`) with a lead execution review at the bench:
IPC socket ownership/permission checks, PID-checked host-task lock,
interrupt-on-terminate, no-network sandbox policy, and one-hop rule all
verified in `scripts/codex-app-bridge.mjs`; real-socket fake-router
tests plus observer lifecycle tests included; canonical suite green
lead-side (`Ran 1722 tests`, `OK (skipped=12)`). The same commit
carries the doctor-driven CLAUDE.md trims (global + repo; content
deduplicated into `.claude/skills/codex/SKILL.md`, which is the
operating home) and stamp-only `docs/site/*.html` provenance refresh.

## CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending

Window A floors contamination diagnosed from primary data: macOS Ventura
*video* screensaver on an awake display contaminated 43/50 suite-calibration
bundles (~+30% energy, −11% throughput; engage at HID-idle +20 min, dismiss on
unlock — pmset assertion log corroborated to the second). The six "low"
su-ABBA runs (18:16–18:36 UTC) are the only CLEAN suite runs; comparative
suite floors (4.923 J item / 24.62 J suite) are transition artifacts. The
professor's power-source hypothesis is refuted (AC/140 W/100% throughout).
Details: memory note + `docs/run_reports/2026-07-17-environment-guard.md`.

Branch `impl/env-guard-cooldown` (pushed, commit e2813ee) holds the D-077
response: environment-guard preflight (+`--arm-quiet-mode`), per-run idle
admission gate, cooldown v2, unwaivable `environment_admission_failed` claim
barrier, policy sidecars, contract/doc updates. Design consult (Sol xhigh,
thread 019f7356-32d3) adjudicated and encoded; implementation by Sol xhigh
(thread 019f7362-6627, resumed via codex-bridge after an MCP transport
timeout); session-close scope check SCOPE_OK; full suite green lead-side
(OK, 12 skips). Lead bench fix included: `pmset -g systemstate` parser now
accepts the live "Capabilities are:" form (was null → fail-closed on real
hardware); fixtures pinned to verbatim live output.

RESUME (in order):
1. Relaunch the adversarial review round (was stopped mid-run at checkpoint):
   fresh read-only Sol xhigh, execution lens, over `git diff main...impl/env-guard-cooldown`
   (prompt shape in `.codex-bridge/` prompt snapshots); lead holds the
   contract lens (done for cooldown_gate/claim-barrier/anchor hunks).
2. Triage findings → fix rounds (defect-shaped regressions) → DELTA RE-AUDIT.
3. Live-validate flagged probes during next quiet-window prep:
   `pmset -g systemstate` display-asleep form + screensaver-engaged probe
   while a screensaver is actually running (run report flags
   `live_validation_provisional`).
4. PR per operation-loop §5 gate shape; then re-run suite ABBA calibration
   under the new guard ([QUIET-MAC], needs Ed) — floors D-076 figures for
   suite comparative cells must be recomputed/caveated pending re-run.

Status: **CLEARED 2026-07-11.** Every clearance criterion met: all
checkpoint-#4 resume items executed (P2-044 fix+merge #55; P2-037
audit dispositions → two fix rounds + approved NEEDS_SCOPE expansion +
delta re-audit → #58; P2-043 #57; P2-045 #56); the four held hardening
PRs #50-#53 merged after the cross-stream integration review over the
combined tree (38 pre-merge cross-stream failures caught and fixed; 1
review blocker confirmed by refuters → PR #59; SF1 refuted; SF3 →
queue row P2-049); DOC-008 kernel refreshed at final head (schema v2,
authority field, branch impl/doc008-kernel awaiting PR); bookkeeping
arc complete (run report, C-028 council entry with layer catch-rates
and ~57-invocation spend record, D-064 ratified incl. manifest v3 +
claude-codex-report/v1 + WRITE_SCOPE enforcement; queue reconciled;
consistency sweep; site regen+deploy). All clearance-time opens since CLOSED same day: #59 MERGED, DOC-008
MERGED (#60). Remaining queue heads: P2-049/P2-050/TOOL-01.

## Superseded stop card (CP-5)

Status: **CLEARED 2026-07-09** by the CP-5 resume session. Every
clearance criterion was met: all three worktree diffs lead-gated
(envgate live-gated against the real affine mock bundle) and merged as
PRs #23/#24/#25; PR #22 merged after a fresh final-head pass; the
methodology synthesis and suite_next specs packet adjudicated (CP-6 in
the stream log); all accepted pre-campaign changes landed and merged
(PRs #26/#27/#28); both post-merge integration reviews CLEAN; queue
rank 0 closed. Full record:
`docs/run_reports/2026-07-09-cp5-resume.md`. No stop card is active.

## Current Project Status

**Mint era OPEN AND FIRST MINT LANDED (2026-07-30): main `da83337`. The
data exists and passes, and the code path that turns it into a published
floor now exists and has been exercised — `df-ph-decode-floor-mint1` is
mainline.**

### The central measurement fact (read before any measurement decision)

The instrument is **attribution-limited (~1 J), not noise-limited
(~0.3 J)** — D-078 clause 11, Ed-ratified. Floors publish LABELLED with
the widened number; the point floor is a repeatability diagnostic that
may never be the published claim floor. The anchor term appears in
**both** the floor and each claim's decision interval, so the effective
clearable effect is floor + claim-side bound ≈ 5 J for phase contrasts,
and neither term may later be deleted as an apparent double count. Do
not launch an instrument-tightening program; it was measured and
eliminated.

### Collection state

| Window | Contents | Verdict | Notes |
|---|---|---|---|
| a9, a10 | earlier corpora | **PASSED** | a10 supplies the absolute component |
| **B** (`04_phase_prefill_abba`) | 40 prefill ABBA members, 59/59 collected clean | **FAILED** | `instrument_calibration_mismatch`, bracket drift 11.581436 ms; preserved, not claim-bearing |
| **C** (`05_phase_decode_abba`) | 40 decode ABBA members, 59/59 collected | **PASSED** | bracket drift 1.279 ms; first comparative window in project history to pass |
| **D** (absolute) | 30 claim members, 49/49 collected | **PASSED** | bracket drift 0.484 ms, tightest of the campaign |
| **7B floor** (`window_7bfloor_20260729`) | Qwen2.5 7B decode floor, collected 2026-07-29 | **PASSED** | CLAIM-BEARING; governed extraction clean (`all_cells_extractable` true). Floors: absolute 6.294380135190098 J, comparative 13.998036715259254 J; absolute-cell member mean 192.38623252628366 J (n=10). NOT yet minted — `MINT-GENERALIZE-01` is OPEN and unblocked as of 2026-08-02 (gauntlet closed PR #93; D-088 no-mint condition lifted), so these figures live only in prose plus the out-of-repo custody extraction until that mint runs |
| **contrast** (`window_contrast_20260730`) | 40 contrast ABBA members + 7 references, 47 bundles, 1 supersession | **PASSED** | bracket drift 1.281 ms; contrast diagnostic 146.730349 J σ 0.241 (n=10 blocks) UNGATED — MANIFEST-CONTRAST-01 closed 2026-08-02 (PR #95); the gated claim now rides `MINT-GENERALIZE-01` then the D-095 chain |

Window B's cause is established and is NOT a clock problem: a GPU DVFM
power ramp that the rectangular-pulse fiducial estimator aliases into an
apparent onset shift (93.28% of the drift; the wall-clock term moved the
OPPOSITE way, −0.201464 ms). D-079 clause 3 adds a pre-flight screen that
detects it in the ~4-minute pre-calibration, with cause-removal (never
outcome-selection) retry semantics.

**Corrected floor figures — the old ones must not be repeated.** a10's
**absolute** floors are **3.823787 J prefill / 3.592138 J decode**,
INCLUDING the 0.652272 J whole-window drift allowance. The 3.17 / 2.94 J
numbers circulated earlier are the attribution-width floors BEFORE the
allowance and are diagnostics only (D-079 clause 5).

**AMENDED BY D-084 (2026-07-29): `3.592138` is the ABSOLUTE COMPONENT IN
ISOLATION, not the operative decode floor.** Mint #1's cell composes
a10's absolute 3.592138 J with window C's comparative 7.377086 J, and
under W3 rule 8 the cell gate is the **max, never the sum** — so the
canonical **operative decode floor is 7.377086 J**, and that is the hard
six-decimal literal pinned in `scripts/mint_floor_artifact.py`. D-079
clause 5's "3.592138" pin predates window C's comparative extraction and
is superseded for the operative figure; both components remain published
and LABELLED per D-078 clause 11.

### The critical path: build the mint (HISTORICAL — CLOSED 2026-07-30)

All four blockers below are closed and this section is retained as
chronology only: `scripts/mint_floor_artifact.py` is the non-test call
site (1), the 30-vs-37 basis question RESOLVED (2), `production_window`
is in `_CALIBRATION_SCOPES` (3), and `impl/floor-mint` merged via PR #87
(4). Mint #1 merged via PR #88 at `da83337`.

`build_floor_cell` / `build_floor_artifact` / `build_absolute_record` /
`build_comparative_record` in `joulewise/detection_floor.py` have zero
non-test call sites; `scripts/extract_detection_floors.py` writes an
extraction report and stops. Established blockers:

1. **`claim_ready` requires an absolute AND a comparative record in the
   SAME cell**, so a10 alone mints a structurally `smoke_only` artifact.
   Mint #1 must pair a10's absolute cell with window C's decode
   comparative. Verifying that the two share backend, metric,
   `window_class`, condition family, and stack identity is a GO/NO-GO,
   not a task.
2. **A 30-vs-37 member authentication mismatch:** the a10 phase spec
   selects 30 members; the passed verdict authenticates 37. Extraction of
   the authenticated basis takes **20 min 36 s** on real data — budget
   for it.
3. **Windows C and D have no legal `calibration_scope`.**
   `_CALIBRATION_SCOPES` is `("window_a", "window_b_revalidation",
## Known Workspace State

- (2026-08-02, CURRENT) `main` and `origin/main` at `bcbc10b`; working
  tree clean except the untracked private `CLAUDE.local.md` (Ed's;
  never commit) and `.desk/` (adjudication custody; never commit).
  PR #93 merged (the c3 branch is closed). Branch
  `impl/d100-bii-binding` exists in the session worktree
  `scratchpad/d100bii` holding the UNCOMMITTED, audit-pending
  D100-BII-BINDING-01 diff (envelope protocol failure; see §9).
- (2026-07-31, historical) `main` and `origin/main` were both at `6ed1625`:
  the PR #89 merge `7ee680c` (D5-J) plus the close-out commits
  `49c1876`, `0d0bd0b`, and `6ed1625`. Branch `impl/mint-tool` is MERGED
  (verified `git merge-base --is-ancestor impl/mint-tool main`), as are
  `impl/floor-mint` and `impl/floor-label-clean`; all three may be
  deleted. Their scratchpad worktrees are still registered (`minttool`
  plus ~11 review/pin worktrees under the `9c166892…` session dir, and
  prunable entries under `ad48bfae…` and `d714f367…`) — `git worktree
  prune` plus explicit removal is owed as housekeeping. The working tree
  is clean except for the untracked private `CLAUDE.local.md` (Ed's
  file; never commit it).
- (2026-07-28 late, historical) `main` and `origin/main` were at that
  session's bookkeeping commit atop the PR #87 merge `058c918`. Branch
  `impl/mint-tool` (pushed, then UNMERGED) held the 9-commit mint series
  `2a0ecbc..697f741` in worktree
  `/private/tmp/claude-501/-Users-edr-code-JouleWise/9c166892-d763-42c4-8cf7-383912f054c9/scratchpad/minttool`;
  canonical suite at its head `1d83d68` is UNVERIFIED (rerun was in
  flight at checkpoint). Branch `impl/floor-mint` is merged via PR #87
  and may be deleted. NOTE: a concurrent session force-rewrote main
  history this evening (content preserved; see run report Anomalies) —
  verify `git log` freshness before building on a cached head.
- (2026-07-27, historical) `main` and `origin/main` were at `7337b33`. Branch
  `impl/floor-mint` @ `617060a` is pushed and NOT merged; it carries the
  pre-mint floor schema hardening. Window C (+bound) and a10 (+bound)
  remain FULLY resident in the working tree (mint #1 inputs); windows B/D
  and all other runs corpora are locally pruned to small evidence files
  (traces archived + verified in iCloud, see "Disk" above), and custody
  material lives OUTSIDE the repo at `~/JouleWise-window-custody/` — an
  agent searching only the repo will wrongly report quarantined evidence
  missing. Disk has 115 GB free; a window writes ~6 GB. The next quiet-window operator must start
  from a separate clean, merged-main measurement checkout per
  `docs/phase_2/window_runbook.md`.
- The generated state-kernel regions in this file and `TASK_QUEUE.md` are
  IN SYNC with `docs/process/state_kernel.json`
  (`python3 scripts/gen_state.py --check` exits 0), and the kernel's own
  content was refreshed on 2026-08-01 (desk adjudication session):
  stamped `updated: 2026-08-01`, `latest_report` points at
  `docs/run_reports/2026-08-01-desk-adjudication-session.md`, the MET
  rows are folded in, the completed
  `FLOOR-LABEL-01`, `STACK-ID-BIND-01`, `P2-015`, and
  `COOLDOWN-JOIN-DA1-01` rows are retired to
  `TASK_QUEUE.md`'s completed table, and the post-mint intake
  (`COOLDOWN-JOIN-GAUNTLET-01`, `MINT-GENERALIZE-01`,
  `MANIFEST-CONTRAST-01`, `SUPERSESSION-DUP-REFUSAL-01`,
  `QA-10A-JOIN-OMISSION`, `QA-10B-EXISTING-RETRY`) is folded in. Any
  further change means editing the kernel and then running
  `python3 scripts/gen_state.py` — never hand-editing the generated
  regions.
- (2026-07-25, historical) `main` and `origin/main` were at `c3e2647`,
  the PR #85 merge; PR #79's repair and PR #85's SCREEN+BUDGET
  implementation both landed with green final PR-head CI.
- The generated state-kernel blocks are authoritative for work selection.
  Hand-authored `RUN_STATE.md` and `TASK_QUEUE.md` text remains authoritative
  only for its own factual, policy, and historical domains;
  `docs/decision_log.md` remains the policy authority, exit checklists own
  phase completion, and evidence artifacts own scientific truth.
- Retained corpus and session scratchpad evidence are immutable.

## Historical Next-Work Snapshot (superseded 2026-07-15)

The following 2026-07-13 narrative is retained for chronology only. It is not
a live queue or restart instruction; the generated work-selection region is
the sole selector.

The comprehensive whole-project audit is the declared gate (Ed,
2026-07-13): method proposal pending Ed's approval, then the audit runs
and its findings are adjudicated before any further feature work. After
that: Window A in the first clean quiet-machine window (C-019/P2-015-SMOKE,
then P2-015 floors, P2-006 baselines), with post-audit [AGENT] heads
P2-050 adjudication, SITE-02, and P2-027 publication prep outside quiet
windows. `TASK_QUEUE.md` remains the ordering authority.

Hardware-gated (unchanged): 2K/2L (P1-006; NV-GATE-2 additions from
C-027 apply at live promotion), wall meter (P1-003), topology (P1-004),
calendar mapping (P1-008).

## Reference Decisions And Blockers (non-selection context)

These pointers retain external-dependency context but do not rank or select
work. The generated region controls task selection.

- Supervisor approval and scope pending (P1-001, R-001 — mitigation
  holding); gates FULL D-016 closure.
- Calendar dates pending (P1-008, R-012).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).
- Git author identity on this machine auto-selected as
  `Ed R <edr@Eds-MacBook-Pro.local>`. Amend future commits if a
  different identity is needed.
## Current Do-Not-Do-Yet List

- (satisfied 2026-06-12) The mock bundle/reducer path and report generator
  now exist; dashboard/report work is no longer blocked.
- (satisfied 2026-06-12) The mock lifecycle is runnable, so live
  MLX/powermetrics implementation may proceed once its hardware gates open
  (P1-002 + D-016); follow `docs/phase_2/hardware_slice_implementation_guide.md`.
- (resolved 2026-06-12) Hailo feasibility has a verdict
  (`unsupported_workload`); do not implement a Hailo backend — report it as
  an applicability finding.
- Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in
  D-008; implementation waits).
- Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate
  (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware
  pairings, or borrow-window scheduling before 2M baselines and the Stage
  3.0 verdicts exist (C-007 wording fix; was previously stated as a
  blanket Phase 3 hold that contradicted the queue).
- Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the
  rehearsed runbook exist (R-006).
- Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has
  produced data.
- Do not close D-016 (model selection) without P1-001 supervisor scope or an
  explicit user go-ahead.
- (satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own
  gates (D-016 + `[mac]` install; privileged sample + D-004 sudoers) open —
  build on the post-2N seams (RunContext raw evidence, D-026 markers,
  D-027 rail rows, 2N.3 observed-token fallback).

## Queue Maintenance

At the end of substantial work:

- Update live status, rank, dependencies, and new tasks in
  `docs/process/state_kernel.json`.
- Remove terminal tasks from the kernel only after their owning completion
  evidence supports closure; preserve the dated Completed row here.
- Run `python3 scripts/gen_state.py`; never hand-edit generated queue or
  restart rows.
- Keep hand-authored edits here to policy, completed/history records, and
  non-selection context.

## Intake Batch Owed To The Kernel (2026-07-30/31)

**PARTIALLY FOLDED 2026-07-30.** Six rows —
`COOLDOWN-JOIN-GAUNTLET-01`, `QA-10A-JOIN-OMISSION`,
`QA-10B-EXISTING-RETRY`, `MINT-GENERALIZE-01`, `MANIFEST-CONTRAST-01`,
and `SUPERSESSION-DUP-REFUSAL-01` — were folded into
`docs/process/state_kernel.json` on 2026-07-30; their staged rows were
removed from this table. Of the six, only `MINT-GENERALIZE-01` and
`SUPERSESSION-DUP-REFUSAL-01` remain LIVE as of 2026-08-02: the
gauntlet trio retired with PR #93 and `MANIFEST-CONTRAST-01` with
PR #95 (see the completed table).
`COOLDOWN-JOIN-DA1-01` followed on 2026-07-31 (D-093), in the same pass
that retired `P2-015` to the completed table and closed
`QUEUE-RECONCILE-01`; both of those staged rows were removed too. It was
short-lived as a live row: DA-1 closed later the same day inside the
gauntlet's commit 2 and `COOLDOWN-JOIN-DA1-01` is now retired to the
completed table (PR #91, `67d268a`).

**The rows that remain below are STAGED, not live**, and stay staged by
magistrate scope decision 2026-07-30 (the P2/P3/P4 residue is not
competing for this window's selection). Work selection is the generated
region below; nothing here competes with it until the magistrate folds a
row into `docs/process/state_kernel.json` and runs
`python3 scripts/gen_state.py`. They are recorded here — hand-authored,
outside the generated markers — so the 2026-07-29/30 arc's owed rows
cannot be lost between the ruling and the kernel refresh (kernel refresh
is magistrate-owned).

Sources: `docs/decision_log.md` D-083..D-093; `docs/council_log.md` C-039
addendum + addendum II; the delegated related-work sweep
(`docs/run_reports/2026-07-30-sweep-techniques.md`); the
`splitwise_decode_v1` campaign doc §2
(`docs/phase_2/splitwise_decode_campaign.md`, on main since `27ffc91`).

| ID | Priority | Lane | Task | Evidence / Acceptance | Authority |
|---|---|---|---|---|---|
| QA-1-COOLDOWN-LAUNDER | P0 Safety | [AGENT] | **CLOSED at `16c7af0` (FIX-10, 2026-07-30).** The fail-open declared-occurrence edge the FIX-9 delta re-audit found (a member declaring `bundle_ids: ["x", "x"]` with only one usable `physical_members` row resolved via the one-row fast path without the supersession matcher) is closed by declared-occurrence tallying; both defect-shaped regressions failed pre-fix and pass post-fix. The FIX-10 delta re-audit confirmed this shape closed while finding the two successor edges now carried as the LIVE kernel rows `QA-10A-JOIN-OMISSION` and `QA-10B-EXISTING-RETRY` (folded 2026-07-30; see the generated region below). | Closed: fast path licensed only at declared count exactly 1; regressions in `SupersessionAwareCooldownJoinTests`; lead-verified 48/48 focused. | [D-086/D-088](docs/decision_log.md); FIX-10 delta re-audit 2026-07-30 |
| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
| MDE-ADOPT-01 | P2 Next Slice | [AGENT] | Powered MDE for the **repeatability arm** + workload-sizing inversion: replace the informal repeatability statistic with δ\* = 2.80·σ_D/√m (α = 0.05, power 0.80) over ABBA pair differences, and size the pilot with m ≥ 2.80²·σ_D²/δ². Desk work on existing data; makes the ad hoc "+5 J claim-side" principled. | Floor computation carries a powered MDE for the repeatability arm with its α and power stated. **Hard boundary, do not cross:** this does NOT apply to the systematic arm — RSS composition is valid only for independent random components, and RSS-ing a worst-case attribution bound as if it were an SD is anti-conservative. `max(repeatability, corner) + drift` stays. | [Sweep-techniques top-10 #1 + §5](docs/run_reports/2026-07-30-sweep-techniques.md) |
| MIN-WINDOW-RULE-01 | P2 Next Slice | [AGENT] | Minimum-window rule + loop-to-60 s for short phases: declare a duration-conditional validity domain (N× the powermetrics cadence; SPEC's 60 s reached by looping the workload if shorter) and **fail-close** phases below it. Attacks the attribution-dominated 6–14 J floors directly, since edge error amortizes with window length. | A declared, enforced validity domain with phases below it refused rather than reported. Note the coupling: changing workload duration resizes the science, so any loop-to-60 s change is a pre-registration change and therefore Ed's call (see `FLOOR-WORKLOAD-SIZING-01`). | [Sweep-techniques top-10 #3](docs/run_reports/2026-07-30-sweep-techniques.md) |
| BATTERY-CROSSCHECK-01 | P2 Next Slice | [QUIET-MAC] | Internal dual-instrument cross-check **before** any wall meter: validate powermetrics integrals against an independent on-device channel (battery/SMC drain over long windows; channel-sum vs package reconciliation) and publish the agreement bound **with its validity domain**. Narrows "never externally validated" without a purchase. | A published agreement bound with its stated validity domain. Caution carried from the same memo: embedded telemetry (BMC/SMC) must NOT be treated as a trusted second reference without its own characterization — the bound is a cross-check, not a calibration. | [Sweep-techniques top-10 #4](docs/run_reports/2026-07-30-sweep-techniques.md) |
| REFUSAL-VOCAB-RATIFY-01 | P1 Phase Gate | [AGENT] + magistrate | Ratification question, deferred out of cold gate F1: reordering the separation-validation phases would **alter refusal precedence**, which D-087 placed in "vocabulary-ratification territory". The refusal vocabulary needs a ruling before any reorder is attempted. | A ruling on the refusal vocabulary and precedence, recorded in the decision log; only then may a phase reorder be proposed. | [D-087](docs/decision_log.md); refusal-scope spec v1 (`ea16730`, on main via PR #88) |
| MOCK-SAMPLER-PROV-01 | P4 Polish | [AGENT] | (Cold-gate finding **F2**.) The mock runtime should emit **truthful sampler provenance**; today the integration tests rewrite metadata to inject a sampler — a test-honesty item. | Mock runtime emits real sampler provenance and the metadata-rewriting test helper is deleted. Mitigated meanwhile: mock bundles are already refused at claim binding by `MOCK_TELEMETRY_CLAIM_REFUSAL`, so there is no claim exposure. | [D-087](docs/decision_log.md) (F2 disposition) |
| COOLDOWN-JOIN-FIXTURE-01 | P4 Polish | [AGENT] | (FIX-9 delta re-audit finding **QA-2**.) No repository fixture composes the **real** supersession validator/reader with the cooldown join; the FIX-9 regressions stub the reader, which is adequate for join/matcher behavior and insufficient as custody-path closure. | A real validator-reader-join fixture exercising the composed custody path end-to-end. | [C-039 addendum](docs/council_log.md); FIX-9 delta re-audit QA-2 |
| MINT-TOCTOU-01 | P4 Polish | [AGENT] | (Audit finding **Audit-F1**, adjudicated QUEUE.) TOCTOU between the mint's pre-check and its authenticated artifact read. Requires concurrent mutation of a frozen input; a different signature from the FIX-8 defect class. | Either the read is made atomic with the pre-check, or the exposure is recorded as an accepted limitation with its precondition stated. | Session ledger, staged-mint section; D-087 sibling dispositions |
| FLOOR-ARTIFACT-SHA-PIN-01 | P2 Next Slice | [AGENT] | Review finding **B2** — artifact-SHA pin. **Detail owed:** the finding's text lives in the review packet, not in the session ledger; whoever promotes this row must restate the defect from the packet before it can be READY per the Ready/Shelf rule. | Not yet acceptance-specified — promote to READY only after the B2 finding text is recovered and restated. | Session ledger, F2 disposition paragraph ("register at bookkeeping with … B2 artifact-SHA-pin row") |
| EXACT-SET-REGRESSION-01 | P2 Next Slice | [AGENT] | Review finding **S2** — exact-set regression. **Detail owed** (same caveat as B2): the ledger names the row but not its content. Likely adjacent to D-086 root cause 1 (exact-set vs governed-subset matching when `--evaluation-basis-sha256` is omitted), but that adjacency is **inference and must be confirmed against the packet**, not assumed. | Not yet acceptance-specified — promote to READY only after the S2 finding text is recovered and restated. | Session ledger, F2 disposition paragraph |
| COLLECTOR-NIT-B1 | P4 Polish | [AGENT] | Review finding **B1** collector nit (distinct from the refuted B1 `device.boundary` placeholder finding — do not conflate). **Detail owed**, same caveat as B2/S2. | Not yet acceptance-specified. | Session ledger, F2 disposition paragraph |
| SITE-ROADMAP-PAGINATE-01 | P3 Tooling | [AGENT] | Paginate or shard the site roadmap page: `roadmap.html` emits one card per live kernel row and now sits at 29,620 of the 30,000-byte capsule shard budget (98.7%) after the 2026-07-30 kernel fold — the NEXT intake fold breaks `CapsulePackError`. | `build_site` succeeds with at least 10 additional live kernel rows; no shard exceeds budget; existing roadmap content preserved. | Kernel-refresh finding 2026-07-30 (session report) |
| DOC-RUNSDIR-ABS-01 | P4 Polish | [AGENT] | Tool contract doc note: the extraction CLI's `--runs-dir` **must be an absolute path**. Document it at the tool contract, and consider a fail-closed check rather than leaving it as operator lore. | Doc note landed; optionally a refusal on a relative `--runs-dir` with a regression. | [D-086](docs/decision_log.md) (queued from lieutenant findings) |
| LITREAD-VERIFY-01 | P4 Polish | [AGENT] | Pre-submission verbatim re-verification of the two load-bearing related-work sources against the **PDFs of record**: TokenPowerBench (arXiv **2512.03024**) and "The Illusion of Power Capping in LLM Decode" (arXiv **2605.11999**). Both were read in full text during the sweep, but through WebFetch's extraction model against the arXiv HTML renders. | Every quote and number cited in a submission re-checked against the PDF. **Note the id correction:** TokenPowerBench is 2512.03024; 2605.11999 is the Illusion paper — earlier handoff text conflated the two. | [Sweep-techniques access summary](docs/run_reports/2026-07-30-sweep-techniques.md) |

## Current Queue

The generated region below is the sole live queue and source of truth for
work selection. Edit the kernel and regenerate; do not hand-edit its rows.

Superseded (2026-07-15, WO-012; D-043): Q4/P2-019 sample size is frozen in the hash-bound analysis registry before outcomes, and outcome-dependent growth permanently demotes the contrast to exploratory; see `docs/contracts/analysis_plans.md` §Required fields.

Superseded (2026-07-15, WO-017; D-043): P2-027 publication and uninvolved-party re-reduction are optional owner-directed evidence-handoff work, not the default reproducibility or project-completion gate; see `docs/specs/c027/rpt-001_report_vertical_slice.md` §0.4 and `docs/contracts/publication_privacy.md` §Publication boundary.

<!-- BEGIN GENERATED: state-kernel current-queue -->
<!-- GENERATED from docs/process/state_kernel.json by scripts/gen_state.py. Do NOT hand-edit between the markers; edit the kernel and regenerate. -->

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-05).

Generated compatibility table for repository consumers; the lane tables below are the detailed view of the same kernel state.

| Rank | ID | Priority | Status | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| E1 | P1-008 | P1 Phase Gate | READY [ED-EXTERNAL] | Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability). | Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: [Milestones + R-012](docs/milestones.md). Acceptance: [P1-008 acceptance](docs/process/state_kernel.json). Note: R-012 is the biggest active management risk for an undergrad timeline. |
| E2 | P2-027 | P2 Next Slice | READY [ED-EXTERNAL] | Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party. | Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: [C-020 + C-027 NEG-9](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-027 acceptance](docs/process/state_kernel.json). Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL. |
| E3 | P1-001 | P1 Phase Gate | READY [ED-EXTERNAL] | Capture supervisor approval and scope notes. | Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: [R-001](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped. |
| E4 | P1-003 | P1 Phase Gate | READY [ED-EXTERNAL] | Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method. | Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: [D-018/C-003](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Elevated value: gates Q6 boundary sensitivity (C-003). |
| E5 | P1-004 | P1 Phase Gate | READY [ED-EXTERNAL] | Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method. | Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: [R-011](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Partial. |
| E6 | P1-006 | P1 Phase Gate | READY [ED-EXTERNAL] | Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L). | Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: [Remote gate / NV-GATE-2](docs/phase_2/hardware_slice_implementation_guide.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). |
| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) [QUIET-MAC] | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
| Q2 | P2-006 | P2 Next Slice | READY [QUIET-MAC] | Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison. | Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: [Phase 2 plan + analysis plans](docs/phase_2/phase_2_plan.md). Acceptance: [Phase 2 exit checklist](docs/phase_2/phase_2_exit_checklist.md). Note: Software interpretation gates are satisfied; Window-A floors landed 2026-07-31 (mint #1 mainline), so only the campaign remains. |
| Q3 | P2-010 | P2 Next Slice | READY [QUIET-MAC] | P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail. | joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: [AP-5 + affine stream log](docs/contracts/analysis_plans.md). Acceptance: [P2-010 acceptance](docs/process/state_kernel.json). Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains. |
| Q4 | P2-019 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC] | q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6). | Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: [AP-1](docs/contracts/analysis_plans.md). Acceptance: [P2-019 acceptance](docs/process/state_kernel.json). |
| Q5 | P2-020 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC] | Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts. | Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: [AP-6 + D-046](docs/contracts/analysis_plans.md). Acceptance: [P2-020 acceptance](docs/process/state_kernel.json). Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6). |
| Q6 | P2-012 | P2 Next Slice | BLOCKED — P2-006 (identification-core runs after Window A) [QUIET-MAC] | Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases. | Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: [AP-4 + D-039/D-040](docs/contracts/analysis_plans.md). Acceptance: [P2-012 acceptance](docs/process/state_kernel.json). Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27). |
| Q8 | P2-046B | P1 Phase Gate | READY [QUIET-MAC] | Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts. | Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: [Hardening adjudication C6](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-046B acceptance](docs/process/state_kernel.json). Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution. |
| Q9 | P2-047B | P2 Next Slice | BLOCKED — P2-047A (frozen controller-overhead harness exists) [QUIET-MAC] | Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict. | Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047B acceptance](docs/process/state_kernel.json). |
| A0 | P2-035 | P3 Research Expansion | READY [AGENT] | RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests). | Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: [RQ-ENERGY-VARIANCE candidate design](docs/specs/rq_energy_variance_design.md). Acceptance: [P2-035 acceptance](docs/process/state_kernel.json). Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine). |
| A2 | QUIET-GUARD-01 | P1 Phase Gate | READY; GATES live_promotion: T3-CHAR-PAIR-01 [AGENT] | Quiet-guard work order (full gauntlet): host-wide quiet lease, refuse-at-arm, characterized resident watcher; plus Ed requirements recorded 2026-08-03 — t3-armed operation (a t3-launched claude session arms a detached guarded chain, then self-quits and quits t3 with a survivor inventory), t3-relaunch-on-close, and README-banner signaling. | The quiet guard lands through the full C-028 gauntlet with the host-wide lease, refuse-at-arm, characterized resident watcher, and all three Ed-required t3 behaviors working end to end. Evidence: Commit 1 only: host-wide quiet lease implemented and enforced; Refuse-at-arm: arming refuses when the host is not quiet (usable by the ordinary guarded-shell window launcher); Installed-INACTIVE: no arming path, no production lease, live_promotion=false; Seven focused-audit blockers closed (priv-esc interpreter, validate/install TOCTOU, arbitrary-root initializer, macOS process identity, boot/hostname wedge, decision entry, independently-pinned tests); Full gauntlet on the landed commit: independent audit + delta re-audit of every fix round. Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [QUIET-GUARD-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). ROW RE-SCOPED TO COMMIT 1 ONLY: the host-wide quiet lease + process census, installed-INACTIVE. Retained because it has non-t3 value — mechanical refuse-at-arm for the ordinary guarded window launcher, replacing procedural eyeballing. SHELVED: commit 2 (launcher interception), commit 3 (t3 handoff + resident watcher), commit 4 (t3-relaunch + README banner projection + all credential handling). In flight at checkpoint: Sol fix round closing 7 audit blockers; work UNCOMMITTED in scratchpad/quietguard (branch impl/quiet-guard); harvest scratchpad/qg-fix-out.md. |
| A3 | FLOOR-BIND-01 | P1 Phase Gate | READY [AGENT] | Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions. | Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: [D-078 clause 8 (confirmation round 9, registered limitation L1)](docs/decision_log.md). Acceptance: [FLOOR-BIND-01 acceptance](docs/process/state_kernel.json). Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed. |
| A4 | AXI-SB-ADAPTER | P2 Next Slice | READY [AGENT] | Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims. | The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: [AXI-SB verdict document (supported; mint-on-supported follow-on)](docs/specs/axi/sb_static_batch_verdict.md). Acceptance: [AXI-SB-ADAPTER acceptance](docs/process/state_kernel.json). Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership). |
| A5 | TEST-SPEED-01 | P2 Next Slice | READY [AGENT] | Cut suite wall-clock (three Ed-ratified levers, 2026-08-03): collect per-module timing data with the recovered profiling scripts, implement the shard-runner and the PR-fast/full tier split from the data, and evaluate Blacksmith runners. | The three Ed-ratified levers land: timing data drives a shard-runner plus PR-fast/full split with the full suite still holding every authoritative gate, and the Blacksmith runner option is evaluated on evidence. Evidence: Per-module timing corpus collected on a quiet bench (the recovered Sol profiling scripts; timings.jsonl + summary.json banked under .desk/) identifying the slow tail by module and by test; Shard-runner and the ratified PR-fast/full tier split implemented from the data: the fast tier gates PRs, the FULL suite remains the gate for merges, verdicts, and audited heads; zero test deletions; Blacksmith runner evaluation recorded with an adopt/defer recommendation and measured latency/cost comparison against GitHub-hosted runners. Authority: [Ed ratification 2026-08-03 (three levers: suite-speed priority, PR-fast/full split, Blacksmith runner evaluation); origin row in the 2026-07-28 report](docs/run_reports/2026-07-28-floor-mint-implementation.md). Acceptance: [TEST-SPEED-01 acceptance](docs/process/state_kernel.json). Fence: No test deletions, and the fast tier never substitutes for a required full-suite gate: merges, whole-window verdicts, and audited heads keep the full suite (D-061 zero-deletion clearance; the full suite as the authoritative gate). Note: 2026-08-03: timing DATA collected (quiet bench, 93 modules, 695s serial; raw in .desk/test-speed-consult/timings-20260803.jsonl) and DESIGN done (.desk/test-speed-consult/DESIGN-from-timing-data.md). Findings: suite is a 2-module problem (run_campaign 182s + p2038 133s = 45%); module-atomic sharding CAPS at 182s so those two must be split by TestCase class; shard-runner + splits -> ~87s wall @8 workers (6.5x); fast tier (drop 11 heavy integ modules) -> 25-40s PR feedback with the full suite still the merge gate. Blacksmith (lever 3) NEEDS ED (account/cost; likely marginal once sharded). Implementation queued: scripts/shard_tests.py + class-split + CI matrix — mechanical, delegatable, zero deletions (D-061). 2026-08-04: PHASE 1 LANDED — PR #98 MERGED (9b02539): module-atomic shard-runner + 8-way CI shard matrix, main CI green under it (~15min -> ~6min proven); worktree/branch pruned. Remaining scope: class-split of the two heavy modules (Phase 2), fast PR tier (lever 2), Blacksmith runners (lever 3, NEEDS ED). |
| A6 | AXI-SD | P2 Next Slice | READY [AGENT] | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
| A7 | AXI-SE | P2 Next Slice | READY [AGENT] | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
| A10 | SUPERSESSION-DUP-REFUSAL-01 | P1 Phase Gate | READY [AGENT] | Rule on and then implement write-time refusal in the supersession recorder, which today appends silent duplicate records when run more than once for a member and voids campaign membership downstream; the ruling is the first half of the deliverable. | A repeat recorder invocation for the same member refuses instead of appending a duplicate record. Evidence: The write-time refusal ruling is recorded in the decision log before any implementation; A regression asserts that a second recorder invocation for the same member refuses. Authority: [D-086 supersession-aware cooldown-evidence join (recorder duplicate-append defect)](docs/decision_log.md). Acceptance: [SUPERSESSION-DUP-REFUSAL-01 acceptance](docs/process/state_kernel.json). Fence: Until the refusal lands, run the supersession recorder exactly once per member (D-086 operator mitigation). Note: Minted 2026-07-30 from the D-086 arc; ruling-first, no implementation before it. |
| A11 | T3-PROV-SCHEMA-01 | P2 Next Slice | READY [AGENT] | Implement the tracked four-axis provenance record with authority_class and the ingestion-event schema, then make reverse-consult admission consume authoritative launch-route and owner_kind evidence so bridge §8's transitional convention ends. | The four-axis provenance plus ingestion-event schema ends bridge §8's transitional convention by mechanically enforcing reverse-consult eligibility from authoritative route and ownership evidence. Evidence: A tracked provenance record represents the four axes control_plane, transport, authority_class, and governance, with authority_class explicit; A tracked ingestion-event schema binds native session identity, output digest, lead disposition, and tracked process-trace location; Reverse-consult admission consumes authoritative launch-route and owner_kind evidence rather than self-reported headers; Rejection regressions fail closed on delegated, unknown, or contradictory provenance and prove that merely persisting the schema cannot end the transition. Authority: [Bridge protocol §8 transitional reverse-consult enforcement follow-on](docs/contracts/bridge_protocol.md). Acceptance: [T3-PROV-SCHEMA-01 acceptance](docs/process/state_kernel.json). Fence: The transition ends only when admission consumes authoritative launch-route and owner_kind evidence with rejection tests; defining or persisting the schema alone is insufficient (Bridge protocol §8 fail-closed transition rule). Note: Bridge §8 currently validates only self-reported headers; consumption-side fail-closed is the actual protection until this row supplies real enforcement. |
| A12 | MINT-GENERALIZE-01 | P1 Phase Gate | BLOCKED — D-110 (The remaining D-110 re-mint conditions hold before ANY further mint, including the governed 7B mint: (b) the acceptance artifact is ISSUED after verified R2 backfill and deterministic ledger bootstrap; (c) the evidence_root_id validator pin is widened) [AGENT] | Generalize the mint beyond the mint-1 pair: scripts/mint_floor_artifact.py is hard-pinned to the p2_015, a10, and window-C evidence (cell id, plan sha, both order-manifest ids, the two member counts, the expected operative-floor text), so build a sibling taking those pins per plan and carrying the 7B mint's remaining scope. | A generalized mint sibling takes the mint-1 hard pins per plan so a second floor artifact can be minted without weakening the pre-registration gate. Evidence: A 7B decode-floor artifact mints from qwen25_7b_decode_floor_v1 evidence with its own hard six-decimal operative-floor literal supplied per plan, never derived inside the mint path; The pre-registration gate passes as-embedded and validate_floor_artifact returns no findings; The generalized path mints byte-identical to the reviewed core from the same inputs on the same integration tree (core-vs-wrapper parity per D-109 addendum II; NOT a match against historical mint-1 digests, which D-110's corrected re-mint may legitimately change). Authority: [splitwise_decode_v1 campaign doc section 2 Blocker A (mint pins); D-082, D-084, D-085 Q6](docs/phase_2/splitwise_decode_campaign.md). Acceptance: [MINT-GENERALIZE-01 acceptance](docs/process/state_kernel.json). Fence: Generalize the plumbing, never the pins: six-decimal floor literals and lead-verified digests stay supplied per plan and hard-checked in-tool (D-082 and D-084 operative-floor pins). Note: 2026-08-03: D-110 (sweep finding RT-1/RT-2): mint #1 is retroactively NON-CLAIM-BEARING (taint-and-remint); the night consult's conditional 7B-mint license is SUSPENDED. The mint-1 byte-compare replay completed BYTE-IDENTICAL at pinned 3de370ec (all four digests; docs/process_traces/2026-08-03-q1-remint-bytecompare/). 2026-08-05: condition (a) is satisfied by merged PR #100. Condition (b) preparation is complete and its verification blocker is resolved: the B1 disposition is lead-ruled 30/2/6 and deterministic bootstrap is implemented on impl/ledger-bootstrap, under audit. Condition (c) is in flight on impl/validator-rootpins. The row remains hard-blocked on the still-pending D-110 (b)+(c) completion gate. |
| A13 | CODEX-BRIDGE-SANDBOX-01 | P2 Next Slice | READY [AGENT] | Correct scripts/codex-bridge review-mode sandbox enforcement: pass the read-only sandbox flag instead of launching workspace-write while recording read-only metadata. | codex-bridge review launches read-only exactly as its audit manifest claims, with regression coverage binding recorded and effective sandbox values. Evidence: scripts/codex-bridge review passes the read-only sandbox flag to every non-app review launch; The review audit manifest records the sandbox actually supplied to the launch; A regression proves the recorded review sandbox and launched sandbox are both read-only and cannot drift apart. Authority: [2026-08-05 live inspection: review records observer_sandbox=read-only but the non-app launch omits -s read-only](scripts/codex-bridge). Acceptance: [CODEX-BRIDGE-SANDBOX-01 acceptance](docs/process/state_kernel.json). Note: Caught live 2026-08-05: observer_sandbox is set to read-only, but the non-app review invocation omits the sandbox flag, so audit metadata misstates enforcement. |
| A14 | COLDGATE-HANDOFF-01 | P2 Next Slice | READY [AGENT] | Build runner-owned sealed-byte judge handoff: capture immutable in-process packet, charter, and exhibit byte snapshots; compute digests over those exact buffers; construct judge input from the same buffers; and specify and test transport byte-to-request binding. | The convening runner delivers exactly the bytes the validator observed, with immutable snapshot-to-judge transport binding and a judge-identity-bound runner receipt. Evidence: Deterministic post-hash path replacement delivers the original immutable snapshot or refuses without invoking the judge; Same-inode mutation through a second descriptor never delivers mutated bytes under the old receipt; Judge-received payload hashes equal the receipt hashes and the runner receipt binds the judge request or session identity. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 handoff ruling and tests](docs/process_traces/2026-08-05-cgv-f3-consult/CONSULT-REPORT.md). Acceptance: [COLDGATE-HANDOFF-01 acceptance](docs/process/state_kernel.json). Fence: Until this row lands, no validator PASS may be used to convene a cold judge (2026-08-05 F3 consult standing operational constraint). Note: Design warnings: holding file descriptors open does NOT seal bytes because a second descriptor can mutate the same inode; path-based launch-time revalidation alone leaves a revalidate-to-read race. Pending-ratification payload carried by this row: the proposed amendment to docs/process/coldgate_charter_registry.md separating validator observation from runner custody. The registry is Ed-ratified and is NOT edited by this or any session without a cold-gate/Ed ratification. |
| A15 | C3-RECOGNIZER-EXACT-01 | P1 Phase Gate | READY [AGENT] | Close the two D-105-registered recognizer-exactness blockers: exact escape-ordering completion-feasibility (F1) and the documented decidable superset number grammar (F2, with the D-104 cl.2 subset-direction amendment), plus the bundled F3/N2 release-path hygiene if not already landed. | The two registered recognizer-exactness blockers (escaped-key ordering; number-prefix over-acceptance) close together under D-105's refuter-amended criteria with an independent audit. Evidence: F1 closes via the exact escape-ordering completion-feasibility procedure (hex-digit interval derivation, surrogate-pair arithmetic, prefix-extension rule) with both registered counterexamples pinned verbatim and a BMP/non-BMP boundary property test; F2 closes via a DOCUMENTED DECIDABLE SUPERSET grammar of json.dumps float spellings (fixed-notation exponent window, coefficient rules, two-digit exponent padding) — the D-104 cl.2 subset direction is amended per D-105 to 'accepted within the documented superset AND containing every real writer prefix'; both counterexamples refuse; randomized-float completeness property passes; Both registered blockers close together with an independent delta audit at the exact head; the acceptance-set contract re-proven in both amended directions over a corpus including non-BMP keys. Authority: [D-105 disposition synthesis (F1/F2 registered as a NEW ruling, not D-088 precedent; closure criteria refuter-amended; number-grammar exactness struck)](docs/decision_log.md). Acceptance: [C3-RECOGNIZER-EXACT-01 acceptance](docs/process/state_kernel.json). Fence: F1/F2 severity may not be downgraded by any role; closure ONLY through this row; while open the recognizer's accepted set may only SHRINK; the custody sidecar and writer-side ASCII key assertion (the D-105 micro-commit) are load-bearing compensating controls and may not be weakened (D-105 registration fences). Fence: This registration must not be cited as precedent for registering corpus-absent defects generally; it is a new ruling made with three recorded independent absence scans and mechanical compensating controls (D-105: branch-introduced registration is NOT QA-10A/B precedent). |
| A16 | P3-000 | P3 Research Expansion | BLOCKED — R-003 (user approves the 3.0.2 installs (R-003)) [AGENT] | KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8). | Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: [D-035/D-036](docs/decision_log.md). Acceptance: [Phase 3 exit checklist](docs/phase_3/phase_3_exit_checklist.md). Note: 3.0.1 complete and merged (PR #9, replay_supported). |
| A17 | P2-022 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)) [AGENT] | Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported). | 3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [Adapter contract](docs/contracts/adapter_contracts.md). Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission. |
| A18 | P2-023 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded) [AGENT] | HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy. | Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [RQ bank import-smoke design](docs/research_question_bank.md). Fence: No pass@k, accuracy, or capability claim (D-041). |
| A19 | P2-024 | P2 Next Slice | BLOCKED — P2-006 (2M reductions identify floor/MDE headroom) [AGENT] | Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC]. | Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: [C-015 + RQ bank](docs/research_question_bank.md). Acceptance: [P2-024 acceptance](docs/process/state_kernel.json). |
| A21 | P3-001b | P3 Research Expansion | BLOCKED — P2-006 (2M affine coefficients exist) [AGENT] | Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049). | AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: [D-048/D-049](docs/decision_log.md). Acceptance: [Analysis plans (split row)](docs/contracts/analysis_plans.md). |
| A22 | P2-004 | P2 Next Slice | PARTIAL; READY; GATES close: P1-001 [AGENT] | Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding. | Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: [D-016](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Provisional small-model pick 2026-07-06 opens 2G. |
| A23 | P2-005 | P2 Next Slice | PARTIAL; READY; GATES live_promotion: P1-006 [AGENT] | Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute. | Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: [NV-GATE-2 live-promotion spec](docs/specs/c027/nv-gate-2_live_promotion.md). Acceptance: [2K live verification checklist](docs/phase_1/2k_live_verification_checklist.md). Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open. |
| A24 | P2-016 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists) [AGENT] | Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment. | Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: [C-011 ledger + C-027 (post-2M umbrella)](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-016 acceptance](docs/process/state_kernel.json). Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake. |
| A25 | P2-047A | P2 Next Slice | READY [AGENT] | Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes. | A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047A acceptance](docs/process/state_kernel.json). Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7). |
| A29 | DOC-008-REFLECTION | P4 Polish | READY [AGENT] | Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6. | Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence). |
| A30 | DOC-008-STATUS | P4 Polish | READY [AGENT] | Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8. | Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence). |
| A31 | DOC-008-INTAKE | P4 Polish | READY [AGENT] | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |
| A32 | DOC-008 | P4 Polish | PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS [AGENT] | Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked. | Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: [DOC-008 state-kernel specification](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 required outcomes](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live. |
| A33 | P2-050 | P3 Hardening Candidates | READY [AGENT] | Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2. | Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives its own adjudication; Semantic cooldown-row verification receives its own adjudication; Once-per-manifest first-run exemption receives its own adjudication; Scoped top-up detection and cooldown trace v2 receive their own adjudications. Authority: [C-028 dissent-record queue candidates](docs/run_reports/2026-07-11-c028-continuation.md). Acceptance: [P2-050 acceptance](docs/process/state_kernel.json). Fence: Do not implement any candidate before its own recorded adjudication (C-028 dissent-record queue candidates). |
| A34 | TOOL-01 | P3 Tooling | READY [AGENT] | Fix codex-run-v3 defects: resume-after-NEEDS_SCOPE no-op; preventive permission profiles; NEEDS_RULING recognition; effort-default passthrough; stream-death OK exits with thin out-files; resume --last cross-thread attachment through the global latest session; and session-open paths lacking per-path match specifiers. | All seven codex-run-v3 defects close in lead personal tooling with targeted regressions and updated adapter operations lessons. Evidence: Resume after NEEDS_SCOPE continues the requested work; Preventive permission profiles and NEEDS_RULING recognition are covered; Omitted effort defaults to xhigh instead of config passthrough; Upstream stream death fails instead of exiting OK with a thin out-file; Resume requires an explicit session ID and cannot cross-attach through a global --last pointer; Session-open accepts a per-path match specifier without post-hoc child expansion. Authority: [Bridge v1.1 wrapper and session operations record](docs/run_reports/2026-07-13-bridge-v11.md). Acceptance: [TOOL-01 acceptance](docs/process/state_kernel.json). Fence: Keep implementation in lead personal tooling; this repository owns only the work record (Bridge v1.1 wrapper and session operations record). Note: lead personal tooling, non-repo |
| A35 | AUD-FOLLOWUPS | P3 Hardening Candidates | READY [AGENT] | Close the ULTRA comparison audit's accepted small residue in one bounded agent task: WO-012's owned D-062 lint queue row, WO-014 realized-token discrimination, WO-017 default no-handoff regression, WO-020 standalone bridge-checker decision, and WO-040 authored-instruction absolute-path plus genuine pristine-clone coverage. | The ULTRA comparison audit's five accepted small follow-ups close with discriminating tests or an explicit recorded decision, without creating a ceremony-dispositions task. Evidence: WO-012's owned D-062 lint queue-row obligation is implemented and covered; WO-014 has a realized-token discriminating test; WO-017 has a default no-handoff regression assertion; WO-020 has a recorded standalone bridge-checker decision; WO-040 has authored-instruction absolute-path coverage plus a genuine pristine-clone test. Authority: [Comprehensive-audit close-out and accepted-residue list](docs/reviews/2026-07-13-comprehensive-audit/report.md). Acceptance: [AUD-FOLLOWUPS acceptance](docs/process/state_kernel.json). Fence: Do not create AUD-CEREMONY-DISPOSITIONS; ceremony dispositions remain report-owned (Comprehensive-audit report disposition ledger). Note: Accepted small residue only; audit ceremony dispositions remain in the report. |
| A36 | AUD-WO-033 | P3 Hardening Candidates | READY; GATES close: P2-006 [AGENT] | After 2M, split scripts/run_campaign.py along tested policy seams, pure validation and provenance first and execution lifecycle second, only when campaign-scale or split or multi-node work first forces edits to that path. | The post-2M campaign-runner refactor is behavior-preserving across the full campaign test portfolio and retains every collection and claim-readiness safeguard. Evidence: Pure validation and provenance seams are extracted before execution lifecycle seams; The full campaign behavior-parity portfolio is green before and after the split; Locks, waivers, backups, cooldown, and claim-readiness behavior remain unchanged. Authority: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Keep this post-2M and behavior-preserving; do not redesign campaigns or weaken locks, waivers, backups, cooldown, or claim-readiness gates (Comprehensive-audit register WO-033 non-goals and risk note). |
| A37 | AUD-WO-034 | P3 Hardening Candidates | READY; GATES close: PHASE-3-SPLIT-SCHEDULED [AGENT] | At Phase-3 split scheduling, assign bounded owners and dependencies for transfer-bench, split replay, composite validate and reduce, KV-economics reduction, and matrix-generator extension before any PLANNED command becomes executable. | When Phase-3 split work is scheduled, every PLANNED pack command gains an owner or explicit deferred marker without pack collapse or premature implementation. Evidence: Every PLANNED command has a bounded owner row or explicit deferred-design marker; Pack-command ownership lint passes positive and negative fixtures; Settled split pre-registration requirements and offline-before-live fences remain intact. Authority: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not prune draft designs, collapse campaign packs, or implement split or KV work in this ownership pass (Comprehensive-audit register WO-034 non-goals). |
| A38 | AUD-WO-035 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-TRANSFER-SCHEDULED [AGENT] | Before the first 2K-live or remote split-transfer task, define a versioned discriminated node-worker payload and test realistic typed rejection without overloading telemetry blocks. | The 2K-live and remote roadmap has a versioned transfer-task payload seam with typed rejection before split-transfer implementation. Evidence: A versioned discriminated payload path exists for transfer tasks; A realistic unsupported transfer request fails with a typed versioned error; Telemetry blocks are not overloaded with transfer semantics. Authority: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Define and reject the future transfer shape only; do not implement split execution or transfer benchmarking (Comprehensive-audit register WO-035 non-goals). Note: D-043 supersession closure falls due at landing: add the dated protocol-version supersession line identified by PA-2. |
| A39 | AUD-WO-036 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-CONCURRENCY-SCHEDULED [AGENT] | When 2K-live or remote retries or concurrency are introduced, add a pre-launch node and GPU ownership lease plus idempotent duplicate prepare and start behavior. | Retries or concurrent 2K-live and remote campaigns cannot double-own a node or GPU and duplicate delivery is idempotent. Evidence: Duplicate prepare and start delivery is idempotent; Node and GPU ownership is leased before launch; Concurrency coverage exercises the ownership and duplicate-delivery contract. Authority: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not run concurrent hardware campaigns or make live-correctness claims in this agent task (Comprehensive-audit register WO-036 non-goals). |
| A40 | AUD-WO-037 | P3 Hardening Candidates | READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED [AGENT] | Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path. | Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2. |
| A41 | AUD-WO-038 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED [AGENT] | At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition. | At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2. |
| A42 | AUD-WO-039 | P3 Hardening Candidates | PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED [AGENT] | At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review. | The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2. |
| A43 | CUSTODY-HARDEN-01 | P2 Next Slice | READY [AGENT] | Custody hardening follow-on from the screen+budget gauntlet: reduce-layer label-trust removal (G2A), drift-bound seal authentication (A3-r2), dead no-freshness accommodation disposition, artifact_schema_invalid mislabel. | Close the PR #85 gauntlet's deferred custody-hardening seams: config-derived mockness reaches the reduce-layer barriers, the drift-bound seal stops being self-certifying, and two diagnostic nits are resolved. Evidence: Reduce-layer environment/CPU claim barriers derive mockness from the custody-bound config, with metadata/summary-label early returns removed; Drift-bound artifact corpus identities resolve against repo-registered or custody-bound bytes (seal no longer self-certifying); Dead pre-addendum no-freshness accommodation removed or pinned as intentional forward-compatibility; artifact_schema_invalid evidence-binding mislabel renamed or documented at emission site. Authority: [C-045 gauntlet deferrals (council log; detail in docs/run_reports/2026-07-24-screen-budget-gauntlet.md)](docs/council_log.md). Acceptance: [CUSTODY-HARDEN-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from PR #85 gauntlet deferrals; triangle-agreement enforcement (merged) already raises these seams to three-file forgery cost. |
| A46 | FLOOR-WORKLOAD-SIZING-01 | P1 Phase Gate | READY [AGENT] | Re-size the floor/science campaign workloads so measured effects clear the duration-independent attribution floor, and pilot the resulting effect-to-floor ratio before spending quiet-machine nights on ABBA collection at current sizes. | Anchor-attribution error is approximately duration-independent (~1 J regardless of phase size) while effects scale with workload, so lengthening prefill/decode raises effect-to-floor linearly at zero instrument cost. Evidence: Measured effect-to-floor ratio at candidate workload sizes, from a pilot rather than assumption; Re-sized configs for the remaining floor stages, with the sizing rationale recorded; Explicit decision on which queued stages are collected at which sizes. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-WORKLOAD-SIZING-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25; scope corrected same day after the quantitative replay. NOT a blocker on the ABBA roadmap: under the labelled-floor path the queued stages remain scientifically viable at current sizes (tens-of-percent effects on ~50 J clear a ~3 J floor plus claim-side bound). This is a MARGIN optimisation — attribution error is duration-independent while effects scale with workload, so longer prefill/decode buys effect-to-floor ratio for free. Pilot the ratio at candidate sizes before committing the remaining quiet-machine nights. |
| A47 | FLOOR-COMMONMODE-01 | P2 Next Slice | READY [AGENT] | Pre-register and evaluate a common-mode anchor estimator for ABBA blocks: sweep one shared fiducial shift across all four members, re-integrate measured curves, and add only genuinely per-bundle components adversarially. | The fiducial term is ~80% of the composed anchor bound (24.9 of ~31.1 ms, verified) and is literally the same artifact for all four members of a block; treating it as four independent adversarial draws is itself an unphysical modelling choice. Evidence: Block-timescale fiducial stationarity registered as a NAMED transfer assumption with its evidence; Estimator pre-registered before it touches claim-bearing data; The identical estimator applied to BOTH the calibration blocks and the consuming science contrast (a floor calibrated with cancellation the consumer does not get would understate false effects); Quantified gain on a5/a10 blocks versus the worst-case-sum default. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-COMMONMODE-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25. Quantified same day on a5 decode ABBA (10 complete blocks): implemented worst-case-sum half-width gives a 6.46 J comparative floor; a common-mode proxy gives 2.13 J, a 3x improvement — material, but still above that cell's 0.60 J point floor, so it does not by itself restore extraction under the current gate. Value is in tightening the labelled floor, not in avoiding the label. Fiducial share of the composed bound measured at 80-87%. |
| A48 | PHASE-SHARE-ESTIMAND-01 | P2 Next Slice | READY [AGENT] | Investigate the anti-correlated prefill/decode boundary error: energy a shift removes from one phase it adds to the other, so the phase-share estimand has ONE boundary nuisance parameter whose joint envelope is a curve, not a box. | Treating each phase's anchor envelope as an independent box double-spends the shared interior boundary and inflates uncertainty on exactly the split/share quantity the Splitwise replication needs. Evidence: Determined whether _corner_composed_anchor_shift_envelope treats the shared interior boundary independently; Joint envelope over the single boundary-position parameter derived by re-integration sweep (measured-curve arithmetic only); Quantified effect on the phase-asymmetry claim envelope versus the independent-box treatment. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [PHASE-SHARE-ESTIMAND-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from the attribution-limit adjudication. Potentially the largest single win available for Splitwise sizing, at no instrument cost. |
| A49 | MODULARITY-01 | P3 Hardening Candidates | READY [AGENT] | Close the campaign-authoring modularity gap surveyed 2026-07-29: parameterize the campaign generator over a campaign-spec artifact and replace code-side literal assertions (analysis-manifest condition pairs, calibration scopes, phase-metric list) with registry-declared hash-validated sets. | Close the campaign-authoring modularity gap: campaign-spec-driven generation and registry-declared closed sets make every experiment axis swappable by config, per Ed's modularity directive. Evidence: Campaign generator is a parameterized function over a campaign-spec artifact (model, N, size profiles, block pattern, suite ref, run-ID prefix); a model swap touches one spec file and MODEL_TAG/PLAN_ID/run-ID prefixes derive from it with no parallel literal edits; Analysis-side closed sets (condition pairs, calibration scopes, phase-metric list) are declared in hash-bound registry artifacts and validated against those declarations, replacing the code-side literals at analysis_manifest.py:29-30,542-549 and detection_floor.py:87,89-95; Recorded-but-deferred residue dispositioned or re-queued: powermetrics references outside the adapter boundary, external-dataset ingestion, chat-template/thinking-mode seam, ABBA arity welded into three sites. Authority: [2026-07-29 modularity survey (Ed directive + per-axis grades)](docs/run_reports/2026-07-29-modularity-survey.md). Acceptance: [MODULARITY-01 acceptance](docs/process/state_kernel.json). Fence: Modularity applies to the harness, never to frozen claim pins: ratified hard literals (six-decimal pre-registration floor pins, lead-verified digests) stay anti-modular on purpose and must not be parameterized. (D-078 provenance amendment + D-079 operative-floor pins (hard literals are lead-verified, never parameterized)). Note: Minted 2026-07-29 from Ed's modularity directive. Survey verdict: runtime/telemetry Protocol layer and content-addressed provenance spine are already modular; the gap is campaign authoring above the adapter and literal assertions below the reader. Practical payoff lands with the planned Qwen3 cross-generation follow-up. |
| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
| A51 | NODE-CUSTODY-DEFAULT-01 | P3 Hardening Candidates | READY [AGENT] | Decide and implement whether the production DEFAULT_RETENTION_ROOT should be process/instance-unique: it currently is a fixed shared temp path (a latent collision hazard for genuinely concurrent clients), but making it unique conflicts with next-session custody reclamation. Resolve the tradeoff or record it as accepted. | Harden the production DEFAULT_RETENTION_ROOT against concurrent-client collision while preserving next-session custody reclamation (the NEEDS_RULING tradeoff deferred from NVIDIA-RETENTION-FLAKE-01). Evidence: The production DEFAULT_RETENTION_ROOT no longer collides for genuinely concurrent NodeClients sharing a scope, without breaking next-session custody reclamation (a later process must still locate the manifest it is entitled to reclaim); A regression proves two default-constructed clients in one process do not clobber each other AND that the documented reclamation contract still resolves the correct manifest across process boundaries; No retention/custody assertion is weakened; only root selection changes. Authority: [NVIDIA-RETENTION-FLAKE-01 fix report F1/F3 (PR #97): unique default roots close concurrent collision but conflict with next-session reclamation](docs/run_reports/2026-08-03-desk-session.md). Acceptance: [NODE-CUSTODY-DEFAULT-01 acceptance](docs/process/state_kernel.json). Fence: Isolation-only: do not weaken any retention/custody assertion; the reclamation contract's cross-process manifest resolution must survive any default-root change (NVIDIA-RETENTION-FLAKE-01 test-side fix (PR #97) already closed the flake). Note: Deferred 2026-08-03 from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake); the production hardening is a NEEDS_RULING tradeoff, non-blocking (no current concurrent-client scenario). |
| A52 | D080-TRIGGER-01 | P3 Hardening Candidates | BLOCKED — D-080-amendment (Ed ratifies the trigger cadence and the runner (cron routine vs manual)) [AGENT] | Wire D-080's standing fresh-eyes sweep to a REAL trigger (calendar cron or every-N-merged-PRs), run as a separate concurrent read-only instance per the Ed-validated 2026-08-03 pattern, findings delivered mid-flight; reconcile D-080 clause 4(ii)'s stale zero-unique-catch citation. | The fresh-eyes sweep fires without anyone remembering it, on a ratified cadence, as a concurrent read-only instance. Evidence: A ratified trigger exists (cron routine or PR-count hook) and has fired at least once; D-080 clause 4(ii)'s stale citation is reconciled by amendment. Authority: [D-080 + the 2026-08-03 sweep finding (never fired) + Ed's concurrent-audit validation](docs/decision_log.md). Acceptance: [D080-TRIGGER-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-03: minted from the two-week soundness sweep's finding that D-080 has never fired, plus Ed's validated concurrent-audit pattern (memory: concurrent-fable-audit-pattern). Non-blocking hardening. |
| A53 | CGV-HARDEN-01 | P3 Hardening Candidates | READY [AGENT] | Harden runner-owned receipt persistence after validator --receipt-out removal: use a dirfd-relative receipt write that closes receipt-write TOCTOU and supplies fsync plus directory-sync atomicity. | The convening runner durably persists validator receipts through a dirfd-relative, crash-atomic, fsync-complete write path. Evidence: The convening runner persists the validator receipt with a dirfd-relative write that closes the receipt-write TOCTOU; Receipt publication is atomic and includes file fsync plus parent-directory sync; Regression tests distinguish path replacement, durability failure, and successful atomic publication. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 receipt-persistence disposition](docs/process_traces/2026-08-05-cgv-f3-consult/SYNTHESIS.md). Acceptance: [CGV-HARDEN-01 acceptance](docs/process/state_kernel.json). Fence: Keep this row a sibling of COLDGATE-HANDOFF-01 and never merge them: durable receipt storage and validated-byte judge handoff have different contracts, tests, and failure consequences (2026-08-05 F3 consult Q2 dissent). Note: 2026-08-05: runner-scoped because PR #103 removed the validator's --receipt-out; deliberately registered as a sibling of, never folded into, COLDGATE-HANDOFF-01. |

## Active Global Work-Selection Gates

NONE — no global work-selection gate is active.

### [ED-EXTERNAL] lane

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
# The Orchestration Process

How this project is actually built: a human researcher directing a
multi-model AI system whose workflow is itself a deliberate, versioned,
self-instrumenting piece of engineering. This document is the single
in-repo description of that process. (The executable playbooks live
outside the repository as reusable "skills" so they transfer to future
projects; this page describes what they do and where their evidence
lands in this repo.) Binding role and process changes live in
`docs/decision_log.md`; this page avoids copying volatile model versions.

## Roles: a lead, independent implementers/reviewers, and a human at the top

- **Ed (researcher)** sets research direction, methodology
  non-negotiables (raw-evidence bundles, dual-basis capture with gross-energy
  headlines, named
  measurement boundaries, no unauditable claims), hardware/access
  decisions, and — critically — *process policy*: every rule below
  traces to a standing instruction issued after an observed failure or
  opportunity. External-facing claims and merge authority derive from
  him (he granted the lead conditional self-merge authority on
  2026-07-08 once the review gate had proven itself).
- **The designated lead** owns
  decomposition, triage, design adjudication, every final diff gate,
  all live/hardware verification, merge decisions, bookkeeping, and
  process evolution. Other agents save lead capacity without inheriting
  final authority; all escalation paths terminate at the lead.
- **Independent implementation and review agents** do the heavy reading and
  writing: implementation against pinned specs, adversarial review
  lenses, test writing, test *auditing* (never of its own tests — a
  fresh instance audits), docs drafting, and review of the lead's own
  consequential decisions. Cross-model review is load-bearing by
  design: the attributed per-layer catch record (below) shows the two
  roles consistently catching different classes of defect.
- **Specialist agents** handle bounded sweeps (for example, docs
  consistency) and, when a stream genuinely needs
  mid-stream judgment, as a stream director — a role that is now the
  exception rather than the default (see Topology).
- **Image-heavy analysis uses the designated image-capable review route** per
  C-012, after the site-observatory stream's image-critique rounds.
- **Invited-peer validation is allowed to overturn lead designs**; C-014
  recorded two lead designs overturned by an invited peer before
  implementation.

## The loop, end to end

Every substantial session runs one conductor procedure:

1. **Intake** — read `RUN_STATE.md` (the intake pointer), the task
   queue, the latest run report; never re-decide anything the decision
   log settled.
2. **Decompose** — split work into genuinely independent streams
   (disjoint expected diff footprints), one git worktree + branch each;
   assign each stream a review tier by *cost of being wrong*
   (measurement-semantics and contract-bearing work gets the full
   pipeline; docs get a light tier). Preflight gates: hardware-shaped
   streams require a confirmed device inventory; anything pinned
   without live validation carries a PROVISIONAL label; measurement
   sessions require a no-agent "quiet machine" lock.
3. **Per-stream pipeline** — for each reviewable unit: an invited
   design-argument round (the implementer must argue trade-offs before
   coding), implementation, then a layered review stack:
   2–3 fresh-instance counterreview lenses over the diff → lead triage
   with recorded dispositions → fixes → a dedicated test-amplification
   round (an independent writer adds edge-case tests) → a
   writer≠reviewer test audit (a fresh instance hunts tautological,
   vacuous, or wrong-expectation tests) → the lead's diff gate.
4. **Lead live gates** — never delegated: the lead runs the real flow
   (real corpus, real CLI, real hardware where present). This layer has
   repeatedly caught blockers no other layer saw, including defects
   whose own tests were green because the tests encoded the same wrong
   assumption as the code.
5. **Merge gate** — multi-commit series land as branch + PR. Before any
   merge: a pre-merge oversight pass by 2–3 fresh reviewers with
   distinct angles (deep regression hunt; claim-to-evidence trace;
   merge-order simulation across sibling PRs), lead triage, fixes, CI
   green. **Final-head rule:** any commit that lands after the last
   review round gets one more fresh review before merge — no commit
   merges unreviewed, however small (its first application caught a
   crash path in a "trivial" post-review fix).
6. **Integration review** — after parallel streams merge, one dedicated
   review hunts *interaction* defects no single-stream review can see.
   Its catches are definitionally unique (first outing: two).
7. **Bookkeeping** — a single session record (run report) with a
   verbatim process-trace appendix; the intake pointer and queue
   refreshed; a delegated docs-consistency sweep before the final
   commit (its latest pass found 15 real drift items; earlier passes
   found 5–6). Large documentation batches add the pre-commit
   docs-verify mode; the `consistency-sweep` skill owns that shape,
   including the D-043 supersession check.
8. **Same-session distillation** — lessons fold into the process
   playbooks the same session they are learned. Measured effect: one
   failure mode recurred five times before its fix was distilled, zero
   times after. The current operation-loop also runs its §0
   primary-deliverable check and §8 shipped-check before the session is
   considered done.
9. **Post-landing verification and close-out** — landed work gets the
   matching verification workflow with severity-tiered refuters. Sessions
   that change front-facing state refresh `docs/site/DRIFT.md`; no agent
   regenerates or deploys the site. Automation informs and Ed deploys
   manually, per D-068 and `RUN_STATE.md` end-of-work step 8.
10. **Meta-review (the final step)** — event-driven, not calendar-driven:
    when a review layer stops earning its keep, when an intervention
    repeats despite a folded fix, or when the user asks, the loop is
    reviewed with its own evidence discipline (see Topology for the
    consensus one such review produced). After large workloads the
    post-large-workload meta-reassessment (owned by operation-loop §10)
    always fires, and it runs LAST.

### Stop cards and paused work

When a session stops with live work in progress, the lead creates or
updates an `ACTIVE_STOP_CARD` at the top of `RUN_STATE.md`. While active,
that card is the single restart authority and overrides every lower
"what next" list, queue rank, mission guide, and run-report default.

A stop card must name:

- the resume authority and exact artifact pointer,
- the reason for stopping,
- worktrees, branches, PRs, and off-repo artifacts that must not be
  cleaned accidentally,
- status terms for each paused item,
- the first resume action, and
- the clearance criteria.

Use these status terms for paused work:

| Term | Meaning |
|---|---|
| `APPLIED_UNVERIFIED` | A worker reports code or docs are applied, but the lead has not gated the diff. Not merge-safe. |
| `LEAD_GATED` | The lead has reviewed and run the required local/live checks for the item. |
| `PR_OPEN_CI_GREEN` | A PR exists and CI is green, but merge authority has not yet fired. |
| `MERGED` | The accepted work has landed on main. |
| `UNREAD_UNADJUDICATED` | A report/synthesis exists but has not been consumed into decisions, queue rows, or rejected findings. |
| `ADJUDICATED` | Findings have explicit accept/reject/defer disposition and downstream artifacts are updated. |

Before an intentional pause, do the minimal stop sync even if full
bookkeeping cannot fit: update only `RUN_STATE.md`'s stop card and the
rank-0 queue row. That is enough to prevent accidental bypass.

## The artifact system (where rigor becomes auditable)

Each fact has exactly one home; everything else points at it:

| Artifact | Role |
|---|---|
| `docs/decision_log.md` | Binding design decisions, each with alternatives considered, consequences, and revisit conditions. The log is the count authority; nothing re-decides these silently. |
| `docs/council_log.md` | The deliberation record: review-council positions, reasoning exchanged, who prevailed, overridden dissents — so a future reader can reconstruct *why*, not just *what*. The log is the range/count authority. |
| `docs/contracts/` | Claim/evidence contracts: `claims_ladder.md` (D-037) plus `analysis_plans.md` (D-038) form the claim gate; strict validation is the evidence ticket. |
| `docs/stream_logs/` | Per-stream decision ledgers, committed WITH the code they justify: every non-trivial in-stream decision (`A-1..A-30`, `B-1..B-46`, …) with mandatory evidence pointers; wrong pins are SUPERSEDED in place, never erased. |
| `docs/run_reports/` | One record per working session: outcomes, verification evidence, a per-layer catch/yield table, the delegation-calibration ledger, restart instructions. |
| `docs/process/state_kernel.json` | Source of truth for work selection: active gates, dependencies, and machine-state lanes ([QUIET-MAC] / [AGENT] / [ED-EXTERNAL]). |
| `TASK_QUEUE.md` | Generated detailed queue projection plus dated history; do not hand-copy its live rows into reader docs. |
| `RUN_STATE.md` | Intake pointer with the generated restart projection. History lives in run reports. |
| `docs/risk_register.md` | Live risks with triggers and mitigation states. |

Instrumentation ledgers close the loop on the process itself:

- **Per-layer yield:** every review layer's unique catches are
  attributed and tallied per session under D-061 (C-027; replaces the
  earlier two-zero-sessions auto-drop, which the integration-review
  zero/zero/five sequence falsified): applicability is decided by
  PRE-DECLARED mechanical predicates; outcomes are classified
  accepted-unique-defect / duplicate / clean-verification /
  false-positive-suppression (suppression is not a catch); severity
  weights are fixed before the session; three applicable exposures
  TRIGGER an expected-loss review decision, never automatic deletion;
  safety/final-head/integration layers are never auto-dropped on
  zero-defect streaks. (One layer, the default specialist review lens, was
  dropped under the old rule before D-061.)
- **Delegation calibration:** every delegated unit gets a row — task
  altitude (pinned-spec / design-freedom / judgment-call), outcome
  (assigned by the lead after the gate, never self-labeled), catches,
  and lead rework minutes, with prompt-defects separated from
  model-defects. Delegation boundaries move on this evidence, not
  vibes. Current signal: pinned-spec delegation runs essentially
  defect-free; the serious defects cluster in volunteered additions and
  design-freedom wire contracts — which is exactly where the full lens
- **Invocation manifest:** substantial delegated/tool/skill runs get a
  lightweight manifest row per invocation. Minimum fields:
  `run_id`, `parent_report`, `role_or_lens`, `model`, `wrapper`,
  `session_id`, `prompt_sha256`, `prompt_path`, `output_path`, `status`,
  `consumed_by`, `disposition`, and `commit_or_pr`. Raw logs can stay
  out of git; every ephemeral artifact still needs a committed pointer
  row with `path`, `sha256` or stable id, `promoted_to`, and
  `not_promoted_reason`.

## Council discipline

Councils are expensive instruments. Use a full council for methodology,
measurement validity, schema/contract changes, claim boundaries, hardware
protocols, or explicit user requests. For ordinary implementation, use a
small number of targeted lenses plus lead adjudication.

Every high-impact council must leave a durable scorecard:

- unique catches by severity,
- accepted/rejected/deferred/false-positive counts,
- lead triage and rework time when practical,
- shipped artifacts,
- queue rows created or re-ranked,
- decision-log IDs promoted, and
- a disposition table: finding → ruling → owner → artifact/queue/decision
  target → closure check.

Deferred decision-log promotion is itself a tracked obligation, not
ambient prose in a report.

## Spend guardrails (WO-022; R2 ruled, Ed-ratified 2026-07-13)

The following policy text is the R2-ratified section, landed verbatim per
audit work order WO-022 (`docs/reviews/2026-07-13-comprehensive-audit/`).

SPEND GUARDRAILS (capstone benchmark bands) — provisional calibration constants; review after two completed arcs; sunset at capstone submission.

1. ACCOUNTING SOURCE. Sol spend: `codex-usage` local accounting (the standing snapshot convention), corroborated by codex-run-v3 manifest `token_usage` rows where populated. The extraction window must cover the full arc — sum incremental snapshots for multi-day arcs; a single trailing-24h view is insufficient. Fable spend: estimated from local usage accounting; each snapshot names its method and price-table version. Price table v2026-07 (pinned until amended): GPT-5.6-sol $5/$30 per M in/out, cached input $0.50; Fable 5 $10/$50, cache reads $1. All figures are estimates, not billing truth, and are recorded as such. Missing data is recorded as `accounting_unknown`, never as zero.

2. DENOMINATOR AND CACHED-TOKEN TREATMENT. Token bands count total tokens (cached + uncached, all directions) exactly as codex-usage reports them — cached tokens are never excluded (exclusion invites cache-heavy gaming). Dollar figures apply cached pricing honestly. Cross-family aggregate ceilings bind in combined estimated dollars, because raw cross-family token sums are not commensurable (C-028: Sol ~180x the token volume, Fable ~3.4x the cost).

3. BOUNDARIES AND ATTRIBUTION. An arc = one council-log C-row, opened at its first delegated session, closed at its closeout snapshot. A work order = one WO/task id. Failed calls, retries, resumes, refuters, fix rounds, delta re-audits, lead usage, and subagents all count against the initiating WO and arc. Arcs and WOs may not be split, renamed, or reopened to reset counters.

4. BANDS. Each dimension is independent. SOFT crossing = record-and-continue: flag in the spend snapshot plus a one-line justification in the council row. HARD crossing = pause-and-ask Ed before any NEW delegated work in that category; in-flight sessions finish; quiet-machine measurement is never interrupted.

   | Scope | Soft | Hard |
   |---|---|---|
   | Sol high session | 6M tokens | 12M |
   | Sol xhigh session | 8M | 16M |
   | Sol ultra session | 40M | 60M |
   | Bench-effort WO | 10M / 3 Sol sessions / ~$40 combined | 20M / 6 / ~$80 |
   | Session-effort WO | 30M / 8 Sol sessions / ~$100 combined | 60M / 12 / ~$200 |
   | Arc | 100M / 25 Sol sessions / ~$400 combined / 6 Sol active-hours / 2 elapsed days | 200M / 40 / ~$800 / 12 h / 4 days |

   WO dollar figures are best-effort: when per-WO Fable attribution is accounting_unknown, the token/session pair binds. Ultra: at most 2 INTENDED ultra sessions per arc, each with a pre-run recorded statement of why xhigh is insufficient and what bounded subagent work it will perform; an unintended ultra is recorded as an anomaly and still counts.

   Calibration anchors (recorded so recalibration stays honest): healthy xhigh ≈ 2.3–3.5M tokens/session (C-030 post effort-fix; C-028 average); the recorded broken state averaged ~9M. C-028 (330.6M / 59 sessions / ~$1,050 / ~17.5h) crosses every substantive arc HARD dimension — it is the anti-example. The 2026-07-13 comprehensive audit (~30 Sol sessions + ~70 Fable agents, Ed-authorized) crosses arc SOFT on session count only — the intended "exceptional: justify and continue" outcome.

5. CHECKPOINTS (procedural; owner = the Fable lead). (a) At arc open: predeclare one accepted deliverable increment for the arc — a corpus/measurement result, analysis/figure/report increment, evaluator requirement, or cited advancement of a D-060 gate — and classify planned delegated work as deliverable-facing or process-facing (mixed sessions count as process-facing unless separately attributable). (b) Before each next delegated call: check the completed session against its tier band (a lightweight glance, not a full snapshot); no runtime killing is promised — evaluation happens on completed sessions before any resume, replacement, or new call. (c) At WO close and arc close: take the spend snapshot and evaluate all bands. One missed checkpoint blocks new process-facing delegation until reconciled.

6. DELIVERABLE-PROGRESS TRIPWIRE (binds while ANY D-060 gate is unmet). If process-facing combined estimated cost exceeds 33% of arc cost OR $250 — whichever occurs first — HARD pause-and-ask Ed before further process-facing delegation. Independently, an arc that closes with process-facing spend but NO accepted deliverable increment pauses further non-exempt process work even if the 33% threshold was not crossed.

7. EXCEPTIONS AND OVERRIDES. Gate-closing work is deliverable-facing by definition. Correctness-defect and data-preservation work may override the allocation tripwire but is always fully counted. Ed direction is NOT a blanket exemption (the finding's own exemplar — bridge v1/v1.1 — was Ed-directed): it is a recorded override carrying an incremental budget and an expiry, and its spend counts.

8. NAMED-FAILURE BAR FOR PROCESS INNOVATION. Any NEW process layer, tool, skill, wrapper version, or contract version requires a decision-log entry citing: (a) a named recorded failure it addresses, (b) why existing controls did not cover it, (c) the smallest new layer that does, (d) its applicability predicate, (e) its marginal budget, (f) a sunset/retirement condition. Absent that entry, it is D-060 breadth and waits for the gates.

9. KEEP-DEFENDER GUARANTEE. No cap consequence auto-deletes a review layer. Layers with recorded unique catches survive any cap; a cap response batches, rescopes, or seeks Ed approval — never silently drops catch-bearing gates (final-head, integration, lead-live, claim/evidence safeguards).

10. MECHANISM. This policy is PROCEDURAL, not mechanical: no checker script is built now (adding process code during an overengineering correction is self-defeating; the arithmetic is a handful of numbers already recorded at existing snapshot points). Two recorded accounting discrepancies or skipped checkpoints across two arcs constitute the named failure that authorizes an executable checker with tests — via the §8 bar.

11. RECALIBRATION AND OWNERSHIP. Band values are calibration constants: the lead may amend SOFT values at arc close with evidence via a one-line decision-log amendment; HARD values and this section's structure are Ed-owned. Scheduled review after two completed arcs. The whole policy sunsets at capstone submission.

Court amendments (T09, folded at the register): canonical session
inclusion uses manifest-corroborated sessions with known token records;
resume rows are deduplicated; non-manifest sessions are reported only as
a labeled upper bound. The 2026-07-13 audit anchor in section 4 is
estimated/accounting_unknown until an audit-close spend snapshot receipts
it (docs/reviews/2026-07-13-comprehensive-audit/receipts/
WO-022-audit-close-spend.json); only a receipted anchor may be used for
recalibration.

## Topology: how it evolved (an example of the loop improving itself)

- **v1 (2026-07-07 AM):** per-stream Fable orchestrator subagents, each
  driving its own Codex thread. Worked, but expensive at the apex tier.
- **v2 (2026-07-07 PM):** Opus orchestrators directing Codex, Fable
  apex-only. Ran four streams — and surfaced a structural flaw: subagent
  orchestrators are not woken by their childrens' completion (the "wake
  gap"), forcing the lead to babysit with heartbeats. The session's own
  trace captured two fleet-wide stalls.
- **Meta-review (C-009):** a signed cross-model consensus — two blind
  Codex analyses vs. the lead's blind position, one conferral round —
  produced a hybrid: the lead drives pipeline-shaped streams directly
  (inheriting the harness's only reliable wake guarantee); subagent
  directors are reserved for judgment-heavy streams.
- **Validation (C-010, 2026-07-08):** the first full session under the
  new topology ran ~26 Codex sessions across four streams — resume
  through merge — with zero coordination stalls, zero manual wake
  interventions, and no subagent stream directors at all.
  The consensus is now the stamped default.

The same mechanism has overturned the lead's own designs: a Codex
review of the lead's process schemas rejected two of them and supplied
better ones (now the v2 ledger and calibration formats), and review
lenses have refuted two of the lead's sanctioned wire-protocol pins
before they could reach hardware. Seniority is not infallibility; the
adjudication of every such challenge remains the lead's.

## What one session looks like (2026-07-07/08, the merge session)

Four checkpointed streams resumed, completed, and landed as four PRs:
the integrity/provenance overhaul (all 31 audit-pinned defects fixed;
strict validation now re-derives the power trace from raw evidence),
the docs package, the KV-cache replay feasibility verdict, and the
complete fixture-first NVIDIA stack. The layered review recorded, among
~30 attributed catches: two blockers found only by fresh-instance
lenses (a provenance hash that did not prove the actual generation
input; a strict-gate bypass via mutable metadata), two pinned wire
contracts overturned before hardware contact, one fabricated-evidence
defect caught only at the lead's diff gate, two integration defects
caught only by the post-merge integration review, and a crash path
caught only by the final-head rule on the last commit of the night.
Suite: 415 → 546 tests, zero expected failures. Roughly two dozen
delegated Codex sessions; the lead never wrote implementation code and
never skipped a gate.

## Reconstructing the loop on a clean machine

Pointer map only; mechanics stay in their owning files.

- Committed invocation wrapper: `scripts/codex-run`.
  Usage: `codex-run <out.md> [--timeout SEC] [-C DIR] [-s SANDBOX] [--resume] '<prompt>'`.
  It writes `<out>.status`.
- Project bridge: `scripts/codex-bridge`; writes prompt snapshots,
  response snapshots, logs, status files, and
  `.codex-bridge/invocation_manifest.jsonl` rows with prompt/output/log
  hashes.
- Workspace-write bridge ceremony: `scripts/bridge session-open` and
  `session-close`; the reduced discussion header, tolerant return envelope,
  receipt anchoring, and recovery primitives are defined only in
  `docs/contracts/bridge_protocol.md` (`bridge-protocol/v1.1`).
- Skill-only mechanics on the operator's machine live under
  `~/.claude/skills`: `operation-loop` is the conductor,
  `codex-delegation` is the invocation/consumption contract,
  `adversarial-review` defines refutation tiers,
  `multi-stream-worktrees` defines parallel stream mechanics,
  `consistency-sweep` owns drift control, and `council` owns
  triggers/roles.
- Repo-derivable on a clean clone: this file gives the loop shape;
  council log C-009/C-010 give topology and gates; the claims and
  analysis-plans contracts give claim gating; `docs/stream_logs/` and
  `docs/run_reports/` provide live templates for ledgers and trace
  appendices; `scripts/codex-run` and `scripts/codex-bridge` provide
  execution entry points.
- Skill-only: exact conductor sequencing, delegated-agent prompt/consumption
  contract, severity-tiered refuter recipes, multi-worktree stream
  operations, and consistency-sweep checklists.

## Where to read the evidence

- Yield tables and calibration aggregates: the latest run reports
  (`docs/run_reports/2026-07-07-resume-merge-session.md` and
  `...checkpoint-multistream-session.md`).
- Deliberations and consensus texts: `docs/council_log.md` (C-007
  design council; C-009 topology consensus; C-010 validation).
- The binding rules themselves: `docs/decision_log.md`.
- Per-decision, in-stream reasoning: `docs/stream_logs/`.

Required sources and repository assets reviewed; three proposals selected to span the cheapest publishable core, the strongest owned-hardware science extension, and the strongest borrowed-instrument validation extension.
  ✓ Read required paper, D-117, feasibility, strategy, and question documents
  ✓ Inspect repo intake state plus instrument, custody, and banked diagnostic assets
  ✓ Develop and compare three quantitative paper proposals
  ✓ Deliver compressed reviewable proposals with kill criteria
codex
# Three asset-leveraged paper proposals

## Shared project brief and steps

JouleWise already has a nearly complete metrology paper: the [draft](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/paper/draft-v1.md) defines bracketed pulse calibration, attribution-aware intervals, composed detection floors, ABBA comparisons, drift allowances, and hash-bound refusals. The central result is that phase measurement is attribution-limited—roughly 1 J can cross an edge—so repetition cannot remove the dominant error and phase contrasts need roughly 5 J of practical separation. No scientific number is presently claim-bearing. D-117 replaces historical consumption with three prospective windows: 1.5B floor plus prefill rider (3.14 h budgeted), 7B floor plus rider (3.24 h), and decode contrast (2.80 h), totaling about 9.2 quiet hours including 20% margin. Historical diagnostics predict a very large decode contrast—141.29 J on the registered metric—and a marginal 128-token prefill contrast, 5.81 J point with approximately 1.81 J half-width; these are sizing inputs, not results. Before collection, desk work must land the two-slot calibration-ledger session, acceptance-successor machinery, four-cell mint, prefill extraction support, frozen campaign packs, and readiness regression described in the [D-117 memo](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md). The three proposals below all fund that same critical path; none treats the banked data as claim evidence.

## 1. When More Repetitions Do Not Help

**Thesis:** A software power counter can support phase-resolved LLM energy claims only when timing attribution, drift, and repeatability are calibrated and enforced as separate refusal gates.

**Contributions**

1. Show whether 59-pulse, live-bookended calibration contains the observed phase-edge uncertainty in all three prospective windows.
2. Mint four falsifiable floor cells—prefill and decode for each model—with absolute and null-ABBA components published separately.
3. Test whether the prospective 7B−1.5B decode interval clears both its arm-wise floor and claim-side bound.
4. Demonstrate that missing, substituted, stale, or duplicate evidence produces governed refusal rather than a changed estimate.

**Experiment:** Exactly the three D-117 windows: 50 science bundles per floor window and 40 contrast bundles, plus bound/reference/calibration captures. The expected decode effect is approximately 140 J **[diagnostic estimate]**, vastly above 5 J and even above the old 7B comparative-floor diagnostic of 14.0 J. Prefill riders add no runtime; no prefill model contrast is claimed. A below-floor cell or failed bracket remains a publishable instrument-domain result, but a failed window cannot populate the demonstration table.

**Needs and fit:** Owned M3 Max only; no wall meter; no change to single-request scope. Reuse draft §§1–5 and §8 nearly intact, replacing placeholders in §§6–7. This is the capstone paper and a strong CSCSU/ICPE Emerging or metrology-workshop submission; with a polished artifact, it is a credible ICPE-full foundation. It serves Ed’s energy-honest reporting goal, though not yet a mechanism axis.

**Kill criterion:** None short of an unrepaired instrument defect. Repeated prospective refusals narrow the paper to calibrated non-identifiability; they do not justify relaxed gates.

## 2. From Measurements to Workload Energy Budgets

**Thesis:** A calibrated fixed-plus-prompt-plus-decode model can predict held-out single-request energy on one named local-LLM stack, provided every coefficient and prediction error is interpreted relative to the detection floor.

**Contributions**

1. Fit the preregistered categorical model \(E=fixed+prompt\_level+decode\_level\).
2. Test held-out cells `(512,256)` and `(4096,512)` rather than merely explaining training observations.
3. Identify which workload increments are resolvable and where attribution prevents coefficient claims.
4. Compare model-size contrast evidence from D-117 with workload-shape effects without claiming universal parameter scaling.

**Experiment:** After D-117, collect AP-1’s 4×3 grid—prompt `{128,512,2048,4096}` by output `{64,256,512}`—for one stack first; add the second only if the first passes holdouts. Use n=5 normally and n=10 for near-floor cells, requiring about 2–3 additional nights. Diagnostics suggest output 64→512 effects near 45 J for 1.5B and 165–170 J for 7B **[linear estimates]**. For prefill, 128→512 may be only about 4 J **[uncertain; may not clear]**, while 128→2048 is roughly 19 J **[uncertain]** and should clear. A holdout miss means the additive model is rejected—not patched with an interaction after inspection.

**Needs and fit:** Owned Mac only, no wall meter, still sequential single requests. Most runtime, suite, reducer, ABBA, custody, and analysis-registry infrastructure exists; new work is campaign-spec generation, AP-1 registry freeze, deterministic holdout analysis, and figures. It reuses the MVP’s complete method/error sections and turns the demonstration section into predictive systems science. Best fit: capstone second chapter, then ICPE full research. It directly serves the modular-harness, workload-swappability, split-budgeting, and third-metrics-axis goals.

**Kill criterion:** A desk simulation kills or shrinks the study if the frozen design cannot fit three nights, if planned cells lack compatible floor transport, or if historical residuals predict holdout errors below identifiability.

## 3. Do SoC-Rail and Wall-Power Measurements Support the Same Conclusion?

**Thesis:** External AC measurement can validate whole-request scale and reveal load-dependent boundary bias, while remaining explicitly unable to validate the prefill/decode split.

**Contributions**

1. Quantify agreement and load dependence between `powermetrics` SoC energy and WT310E AC input energy.
2. Test whether the 1.5B-versus-7B direction survives measurement-boundary change.
3. Test compute-heavy versus long-context conditions for boundary-dependent contrast changes.
4. Empirically separate total-scale validation from phase-attribution validation.

**Experiment:** One pilot and one confirmatory quiet window, simultaneously measuring repeated D-117 configurations plus a long-output and long-prompt condition in ABBA order. The model-size effect should exceed 100 J **[uncertain extrapolation from the 141 J decode diagnostic]**; the absolute wall-minus-SoC gap is probably tens of joules for long requests **[high uncertainty]**. Boundary-interaction effects may be below 5 J; that outcome means “no flip resolvable,” not boundary equivalence.

**Needs and fit:** Borrow an in-calibration Yokogawa WT310E and safe inline fixture; add synchronized export/import, fixed-range uncertainty calculation, battery-charge neutralization, and dual-stream custody. No new compute hardware and no multi-request change. This reuses all MVP instrument sections, D-117 floors and contrast, adding a physical-boundary validation section. It is the strongest ICPE upgrade and serves energy-honest comparison, though not a mechanism study.

**Kill criterion:** Do not spend a night unless the meter is in calibration, exports at adequate cadence, its load-specific uncertainty is acceptable, clocks can be bounded, and battery charging can be held neutral. If any fails, retain this as future work and submit Proposal 1 unchanged.
tokens used
158,410
# Three asset-leveraged paper proposals

## Shared project brief and steps

JouleWise already has a nearly complete metrology paper: the [draft](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/paper/draft-v1.md) defines bracketed pulse calibration, attribution-aware intervals, composed detection floors, ABBA comparisons, drift allowances, and hash-bound refusals. The central result is that phase measurement is attribution-limited—roughly 1 J can cross an edge—so repetition cannot remove the dominant error and phase contrasts need roughly 5 J of practical separation. No scientific number is presently claim-bearing. D-117 replaces historical consumption with three prospective windows: 1.5B floor plus prefill rider (3.14 h budgeted), 7B floor plus rider (3.24 h), and decode contrast (2.80 h), totaling about 9.2 quiet hours including 20% margin. Historical diagnostics predict a very large decode contrast—141.29 J on the registered metric—and a marginal 128-token prefill contrast, 5.81 J point with approximately 1.81 J half-width; these are sizing inputs, not results. Before collection, desk work must land the two-slot calibration-ledger session, acceptance-successor machinery, four-cell mint, prefill extraction support, frozen campaign packs, and readiness regression described in the [D-117 memo](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md). The three proposals below all fund that same critical path; none treats the banked data as claim evidence.

## 1. When More Repetitions Do Not Help

**Thesis:** A software power counter can support phase-resolved LLM energy claims only when timing attribution, drift, and repeatability are calibrated and enforced as separate refusal gates.

**Contributions**

1. Show whether 59-pulse, live-bookended calibration contains the observed phase-edge uncertainty in all three prospective windows.
2. Mint four falsifiable floor cells—prefill and decode for each model—with absolute and null-ABBA components published separately.
3. Test whether the prospective 7B−1.5B decode interval clears both its arm-wise floor and claim-side bound.
4. Demonstrate that missing, substituted, stale, or duplicate evidence produces governed refusal rather than a changed estimate.

**Experiment:** Exactly the three D-117 windows: 50 science bundles per floor window and 40 contrast bundles, plus bound/reference/calibration captures. The expected decode effect is approximately 140 J **[diagnostic estimate]**, vastly above 5 J and even above the old 7B comparative-floor diagnostic of 14.0 J. Prefill riders add no runtime; no prefill model contrast is claimed. A below-floor cell or failed bracket remains a publishable instrument-domain result, but a failed window cannot populate the demonstration table.

**Needs and fit:** Owned M3 Max only; no wall meter; no change to single-request scope. Reuse draft §§1–5 and §8 nearly intact, replacing placeholders in §§6–7. This is the capstone paper and a strong CSCSU/ICPE Emerging or metrology-workshop submission; with a polished artifact, it is a credible ICPE-full foundation. It serves Ed’s energy-honest reporting goal, though not yet a mechanism axis.

**Kill criterion:** None short of an unrepaired instrument defect. Repeated prospective refusals narrow the paper to calibrated non-identifiability; they do not justify relaxed gates.

## 2. From Measurements to Workload Energy Budgets

**Thesis:** A calibrated fixed-plus-prompt-plus-decode model can predict held-out single-request energy on one named local-LLM stack, provided every coefficient and prediction error is interpreted relative to the detection floor.

**Contributions**

1. Fit the preregistered categorical model \(E=fixed+prompt\_level+decode\_level\).
2. Test held-out cells `(512,256)` and `(4096,512)` rather than merely explaining training observations.
3. Identify which workload increments are resolvable and where attribution prevents coefficient claims.
4. Compare model-size contrast evidence from D-117 with workload-shape effects without claiming universal parameter scaling.

**Experiment:** After D-117, collect AP-1’s 4×3 grid—prompt `{128,512,2048,4096}` by output `{64,256,512}`—for one stack first; add the second only if the first passes holdouts. Use n=5 normally and n=10 for near-floor cells, requiring about 2–3 additional nights. Diagnostics suggest output 64→512 effects near 45 J for 1.5B and 165–170 J for 7B **[linear estimates]**. For prefill, 128→512 may be only about 4 J **[uncertain; may not clear]**, while 128→2048 is roughly 19 J **[uncertain]** and should clear. A holdout miss means the additive model is rejected—not patched with an interaction after inspection.

**Needs and fit:** Owned Mac only, no wall meter, still sequential single requests. Most runtime, suite, reducer, ABBA, custody, and analysis-registry infrastructure exists; new work is campaign-spec generation, AP-1 registry freeze, deterministic holdout analysis, and figures. It reuses the MVP’s complete method/error sections and turns the demonstration section into predictive systems science. Best fit: capstone second chapter, then ICPE full research. It directly serves the modular-harness, workload-swappability, split-budgeting, and third-metrics-axis goals.

**Kill criterion:** A desk simulation kills or shrinks the study if the frozen design cannot fit three nights, if planned cells lack compatible floor transport, or if historical residuals predict holdout errors below identifiability.

## 3. Do SoC-Rail and Wall-Power Measurements Support the Same Conclusion?

**Thesis:** External AC measurement can validate whole-request scale and reveal load-dependent boundary bias, while remaining explicitly unable to validate the prefill/decode split.

**Contributions**

1. Quantify agreement and load dependence between `powermetrics` SoC energy and WT310E AC input energy.
2. Test whether the 1.5B-versus-7B direction survives measurement-boundary change.
3. Test compute-heavy versus long-context conditions for boundary-dependent contrast changes.
4. Empirically separate total-scale validation from phase-attribution validation.

**Experiment:** One pilot and one confirmatory quiet window, simultaneously measuring repeated D-117 configurations plus a long-output and long-prompt condition in ABBA order. The model-size effect should exceed 100 J **[uncertain extrapolation from the 141 J decode diagnostic]**; the absolute wall-minus-SoC gap is probably tens of joules for long requests **[high uncertainty]**. Boundary-interaction effects may be below 5 J; that outcome means “no flip resolvable,” not boundary equivalence.

**Needs and fit:** Borrow an in-calibration Yokogawa WT310E and safe inline fixture; add synchronized export/import, fixed-range uncertainty calculation, battery-charge neutralization, and dual-stream custody. No new compute hardware and no multi-request change. This reuses all MVP instrument sections, D-117 floors and contrast, adding a physical-boundary validation section. It is the strongest ICPE upgrade and serves energy-honest comparison, though not a mechanism study.

**Kill criterion:** Do not spend a night unless the meter is in calibration, exports at adequate cadence, its load-specific uncertainty is acceptable, clocks can be bounded, and battery charging can be held neutral. If any fails, retain this as future work and submit Proposal 1 unchanged.
