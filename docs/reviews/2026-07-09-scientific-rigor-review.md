# Scientific-Rigor Review — Measurement Suite, Benchmark, and Question Bank (2026-07-09)

Session record for council C-023 (see `docs/council_log.md`). User-directed
review: steelman the methodology, scope, and objectives of the JouleWise
measurement suite and benchmark; examine every question in the research
bank; decide whether the project as specced stands up to scrutiny from a
Stanford-PhD-EE advisor — explicitly acknowledging the hardware for many
questions is not yet in hand, so the artifact under review is the
instrument, contracts, specs, and research plan.

Shape: four independent fresh gpt-5.5-high read-only lenses (L1 metrology,
L2 benchmark/statistical design, L3 question-bank audit — every question
individually, L4 advisor simulation attack/steelman/gap-list), each with a
named angle and severity-tiered deliverables; lead (Fable) read the
question bank, measurement methodology, claims ladder, and analysis plans
in full independently; lead synthesis then argued in a bidirectional
discussion round (D1) with a fresh 5.5 instance instructed to verify
contested adjudications against the repo docs. One discussion round
converged; no unresolved dissent. No worktrees (read-only session); no
code changed.

## Verdict (lead, adjudicated with 5.5 concurrence)

**Today:** the methodology is a strong PROVISIONAL chapter — the simulated
advisor does not sign the final methodology chapter yet, and both models
agree the refusal is specific and curable.

**The gap is entirely in the physical/statistical inference layer, not the
evidence layer, and every blocker-class item is closable with specs,
software, and analysis code alone — no hardware.** With the pre-hardware
artifact list below landed, both models' independent answer to the core
question is YES: the project stands up to advisor scrutiny as an
undergraduate capstone, under the frozen headline "auditable,
boundary-labeled local LLM energy characterization on named stacks," with
split inference explicitly gated as the stretch upgrade.

## Settled convergences (all four lenses + lead + D1)

1. The evidence architecture is the project's genuine contribution and is
   stronger than typical published LLM-energy work: immutable re-reducible
   bundles, strict raw-to-trace rederivation, per-backend measurement
   boundary table with forbidden cross-boundary language, the claims
   ladder (D-037) with per-level evidence requirements and downgrade
   examples, pre-registered AP rows with floor gates, MDE arithmetic,
   dependence-structure rules, and denominator-provenance requirements.
2. The question bank is unusually disciplined (claim ceilings, named
   threats, recorded kills, examiner-scoped steelman) but overgrown and
   needs a canonical registry with aliases/status/type normalized.
3. The correct capstone identity is instrument-methodology science:
   the reusable referee (contracts + strict validation + floors) is the
   contribution; the M3 Max results are the demonstration.

## Blocker-class findings (advisor-bar; all no-hardware-fixable)

- **B1 Metrological error budget missing** (L1): t-intervals capture
  repetition noise only; idle-baseline variance (stored, unused),
  sensor systematics, timestamp/interpolation/aliasing terms are not
  propagated into claim gates; idle subtraction is scalar
  stationary-baseline removal. D1 severity: blocks claim-bearing
  comparative campaigns (2M/Window A data intended for L2), not L1
  smoke operation.
- **B2 No benchmark-level multiplicity/selection policy** (L2): AP rows
  regulate single claims; nothing governs the contrast family across
  categories × models × quants × shapes × imports. Right-sized fix
  agreed in D1: lightweight analysis registry — every reader-facing
  claim labeled primary/secondary/exploratory with family_id,
  claim_role, selection_scope, multiplicity_rule; Holm within small
  confirmatory families; BH/exploratory labeling for sweeps; frozen
  before each campaign.
- **B3 No canonical RQ registry** (L3): the same question exists as
  promoted Q, banked item, capability-map row, and C5 tier row; a few
  rows still invite attribution beyond the measurement boundary.
  Registry columns agreed in D1: canonical ID, aliases, question_type
  (research question / capability claim / application idea / methodology
  artifact), status, claim ceiling, forbidden upgrade, AP owner,
  campaign owner, gate class (hardware / software / floor),
  multiplicity family, denominator policy, stack-identity-required,
  boundary class, pre-hardware preparability.
- **B4 Headline claim not frozen** (L4): freeze ONE defensible headline
  ("auditable, boundary-labeled local LLM energy characterization on
  named stacks") plus two fallbacks with allowed claim levels; split
  inference explicitly gated. Includes the one-page minimum-viable-
  capstone contract with stop-lines and cut triggers.

## Major findings accepted (design-bearing)

- **M1 Statistical comparison rule**: replace "intervals separate" with
  contrast-level inference (paired/block difference CIs; permutation
  checks where order is randomized). Amends the D-014 protocol.
- **M2 Ordering executability** (elevated by D1): C-015 promises
  round-robin/Latin-square rotation; the sequencing spec executes
  manifest_order today. Affects category/difficulty/thermal/position
  inference. Fix (per-repetition manifests or a real execution policy)
  must land before any suite campaign.
- **M3 Token-normalization contract**: request energy primary; J/token
  tokenizer-scoped; cross-tokenizer comparisons need J/char, J/byte, or
  semantic-pair companion denominators, or must avoid efficiency-ranking
  language. Plus L4's stack-identity table (runtime, kernel/library,
  tokenizer, artifact, quantization, sampler, batching in every figure).
- **M4 Phase-window claim gate**: raw phase_energy_j stays; claim
  tooling refuses under-resolved windows (sample count,
  duration/sampling ratio, clock bound) — per D1, blocker specifically
  for phase/item-window claims.
- **M5 Thermal honesty**: cooldown power-recovery gate is a proxy, not a
  thermal-state guarantee; cap-hits or sentinel drift above floor
  downgrade claims (partially in AP rules already).
- **M6 Telemetry trust hierarchy**: per-backend caveat fields
  (powermetrics = Apple-modeled SoC estimate; nvidia-smi =
  driver-reported board power with averaging semantics unknown until
  measured; wall = AC truth) + calibration runbooks pre-registered NOW
  (acceptance thresholds and claim ceilings if absent), executed when
  the meter/hardware arrives.
- **M7 Selective severities from negative space** (D1): telemetry
  perturbation cost → fold into P2-015 as an ABBA/telemetry-on-off floor
  component; output-token identity — for quantization/runtime/
  speculative-decoding efficiency claims, output equivalence or
  divergence reporting is mandatory.

## Adjudications of note

- **C5-1.1 overturned as a live blocker** (D1, accepted by lead after
  verifying citations): the C-014 amendment already caps 4-6-model
  designs at descriptive L2 pairwise contrasts, the claims ladder
  forbids active-parameter-scaling language at L1, and the capability
  map records the two-model observation as a non-claim. Residual work is
  naming hygiene in the registry, not a contract gap.
- **n=5 protocol** (L2): already provisional-by-design pending Window A
  variance (D-014 wording + AP top-up rules); recorded as adequate with
  the M1 contrast-level amendment.
- **L3 outlier-policy fragility at n=5** (MINOR): keep never-silently-
  drop; add leave-one-out influence check to the protocol amendment.

## Recommended pre-hardware work order (D1-amended; input to the next
## planning session, NOT yet queued — queue impact is Ed's step-2 call)

1. Freeze capstone headline + minimum-viable-capstone contract (B4) —
   controlling scope for everything below.
2. P2-015 as a COMBINED spec: detection floors + calibration runbooks +
   telemetry-trust hierarchy + per-backend/metric/window error budget
   (B1 structure, M6, M7 perturbation component).
3. Statistical protocol amendment + analysis registry (M1, B2).
4. Reducer/aggregator uncertainty propagation + claim gates (B1
   implementation, M4): idle variance + drift term; "not estimable" for
   single bundles; claim tooling respects identifiability flags.
5. Canonical RQ registry + claims-index linter (B3; linter refuses
   L2/L3 without AP row, floor, order policy, multiplicity family,
   denominator provenance, stack/boundary identity).
6. Ordering executability (M2) — before any suite campaign.
7. Token-normalization contract + stack identity table (M3).
8. Campaign packs for the fully-preparable list (L3 §d): Q1-Q3 split
   suite, Q6/C5-2.10 rail-vs-wall, C5-2.3 KV economics, C5-2.7, C5-2.8,
   C5-3.1/3.5 replication runbook, C5-I.1..I.5 contracts, C5-2.1/2.2
   CUDA manifests. Cut-line: no broad C5 campaign packs before the
   registry/linter exists.

## Residual risks NO spec work can close (report honestly, never promise)

Vendor telemetry bias without wall/PD calibration; single-unit-per-target
generalization; thermal/ambient/chassis empirics; KV portability and
split feasibility depend on real runtimes; OS/runtime version drift;
bounded workload ecological validity; output-quality equivalence is not
guaranteed by energy instrumentation; local-vs-datacenter crossover stays
scenario analysis.

## Question-bank highlights (L3, lead-concurred)

Strongest five: Q4 fixed+marginal model (AP-1, holdouts — the most
advisor-defensible science in the bank); the detection floor; C5-2.3
predicted-vs-measured KV economics; C5-W.1 token-shape sufficiency;
Q6/C5-2.10 boundary sensitivity. Weakest/most-overclaimed: C5-1.1
(as previously worded), intelligence-per-joule (correctly killed),
C5-I.2 difficulty strata, C5-2.9 datacenter crossover (appendix, not
headline), C5-W.3 (Q5 duplicate). Coverage gaps worth adding to the
registry: telemetry perturbation cost, OS/runtime version-drift
forensics as science, marker/window jitter sensitivity, output-token
identity effects, idle-baseline stationarity as a named question,
quality-equivalent quantization comparisons, coefficient transport from
synthetic grids to realistic session traces.

---

# Appendices: verbatim model outputs (evidence)

Lens prompts pinned angle, severity tiers, doc citations, and concrete
failure scenarios; all sessions read-only, no network. File paths in
citations are absolute paths from the review sandbox.

## Appendix A — L1 Metrology lens (gpt-5.5, fresh, read-only)

**1. STEELMAN**

JouleWise is unusually strong for an undergraduate energy benchmark because it treats measurement as an auditable evidence pipeline rather than as a table of numbers. The core scientific move is correct: every run emits a bundle with config, metadata, event log, raw telemetry, derived trace, outputs, and reducer output, and the summary is explicitly not the source of truth. Strict validation re-derives summaries from `power_trace.csv` and, for powermetrics, re-derives the trace from the preserved raw plist. That is a real metrology virtue: parser bugs and summary bugs are separable from hardware reruns.

The boundary model is also more honest than most LLM energy papers. The docs distinguish Apple SoC rails, NVIDIA board power, Jetson module input, and AC wall power, and the claims ladder forbids cross-boundary quantitative winners without calibration. That alone prevents a common bad conclusion: comparing Apple package rails to NVIDIA board power as if both were “device energy.” Rail manifests are explicit, and the reader rejects duplicated or partially aligned multi-rail rows instead of silently summing nonsense.

The lifecycle design is technically thoughtful. The measured window is marker-bounded after sampler readiness and before sampler wind-down, avoiding sudo startup, process parsing, and output writes in the energy integral. Controller co-residency is at least acknowledged and mitigated by resident-controller idle baselines and buffered logging. Repetition and ordering are specified: independent bundles, experiment manifests, cooldown gates, t intervals, outlier flagging without silent deletion, and raw points beside aggregates.

Finally, the claims ladder is conservative. L0/L1/L2/L3/L4 evidence requirements are explicit; per-token claims require runtime-observed token counts; cross-boundary claims need calibration; floor-gated effects below resolution must be called `not resolvable`. As a benchmark architecture, this is far better than “run model, sample watts, divide by tokens.” It is scientifically useful as a boundary-labeled, reproducible instrument-result harness, especially for within-target comparisons.

**2. FINDINGS**

1. **BLOCKER: There is no actual metrological error budget yet.**  
   Citation: [measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md) “Uncertainty” and “Measurement Quality Fields”; [phase_4_plan.md](/Users/edr/code/JouleWise/docs/phase_4/phase_4_plan.md) Stage 4.0; [aggregate.py](/Users/edr/code/JouleWise/joulewise/aggregate.py).  
   The code implements repetition statistics: mean, sample standard deviation, Student-t CI, outlier flags. That is not an error budget. It does not propagate sensor accuracy, timestamp-anchor uncertainty, idle-baseline uncertainty, interpolation error, sample quantization, phase-window misalignment, or vendor telemetry bias. A user could see non-overlapping CIs across five runs and conclude “condition A saves 3% energy,” when the vendor sensor systematic error or idle-subtraction model error is larger than the effect. Advisor bar: this is the main metrology gap.

2. **BLOCKER: Idle subtraction is treated as scalar baseline removal without a defensible dynamic model.**  
   Citation: [measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md) “Idle Subtraction,” “Controller Co-Residency,” “Repetition, Ordering, And Thermal Equilibrium”; [reduce.py](/Users/edr/code/JouleWise/joulewise/reduce.py) idle subtraction logic; [powermetrics.py](/Users/edr/code/JouleWise/joulewise/adapters/powermetrics.py) idle GPU suspect heuristic.  
   The reducer computes `idle_subtracted = gross - idle_mean * duration`. That assumes the idle floor is stationary, additive, and independent of workload thermal/DVFS state. The docs store idle stddev but do not propagate it into energy uncertainty. Failure scenario: a Mac run warms the SoC, fan/thermal pressure shifts package idle by several watts, and idle-subtracted request energy changes sign or changes rank. The project partly catches this with cooldown gates and `idle_window_suspect`, but the model is still “subtract one pre-run mean.”

3. **MAJOR: Measurement boundary definitions are honest, but Apple powermetrics semantics are over-trusted.**  
   Citation: [measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md) “Measurement Boundaries”; [hardware_slice_implementation_guide.md](/Users/edr/code/JouleWise/docs/phase_2/hardware_slice_implementation_guide.md) Slice 2H; [powermetrics.py](/Users/edr/code/JouleWise/joulewise/adapters/powermetrics.py).  
   The docs call powermetrics “Apple SoC CPU + GPU + ANE package power,” but powermetrics is Apple-private/OS-mediated telemetry, not a calibrated external instrument. JouleWise preserves raw plists and validates parser consistency, which is good, but parser consistency is not physical accuracy. Failure scenario: ANE or memory-controller energy is misreported or excluded differently across macOS versions; JouleWise reports a phase energy shift as a workload effect when it is a telemetry-model artifact. Literature confidence: high that powermetrics is not wall power; low-to-medium on exact Apple rail accuracy because public calibration data are sparse.

4. **MAJOR: NVIDIA `nvidia-smi` board power is correctly boundary-labeled but not accuracy-limited in the measurement model.**  
   Citation: [measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md) “Measurement Boundaries”; [hardware_slice_implementation_guide.md](/Users/edr/code/JouleWise/docs/phase_2/hardware_slice_implementation_guide.md) Slice 2K; [nvidia_smi.py](/Users/edr/code/JouleWise/joulewise/adapters/nvidia_smi.py).  
   `nvidia-smi power.draw`/NVML is a driver-reported board-power reading, usually sampled/averaged and often updated at coarse cadence. Published HPC measurement work has repeatedly found NVML/nvidia-smi useful for trends but not equivalent to calibrated external meters; reported errors depend on GPU generation and workload dynamics. Low-confidence exact claim: I would expect several-percent systematic error and poor short-window fidelity, but I am not citing a precise bound without network. Failure scenario: comparing two decode kernels with bursty power at 100-300 ms scale; nvidia-smi smooths or aliases bursts and makes the “more efficient” kernel look unchanged.

5. **MAJOR: Sampling-rate versus event-duration aliasing is recognized but not consistently enforced for claim-bearing request or phase metrics.**  
   Citation: [measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md) “Clock Synchronization,” “Statistical Protocol”; [reduce.py](/Users/edr/code/JouleWise/joulewise/reduce.py) `MIN_PHASE_SAMPLES = 3`; [analysis_plans.md](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md) standing reporting rules.  
   The reducer flags phase identifiability when a phase has fewer than 3 samples, but it still emits `phase_energy_j` numbers. Request-level energy only requires two samples in-window. At ~9 Hz, a 100 ms prefill phase is physically under-resolved; trapezoidal interpolation with clamped edges can produce a precise-looking number from almost no information. Failure scenario: a report plots prefill energy for short prompts and infers prefill/decode asymmetry, when the prefill window often contains zero or one real sample.

6. **MAJOR: Clock-domain handling is thoughtful but not propagated into energy/phase uncertainty.**  
   Citation: [measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md) “Clock Synchronization And Multi-Node Alignment”; [run_bundle_layout.md](/Users/edr/code/JouleWise/docs/contracts/run_bundle_layout.md) rich telemetry timestamp note; [node_client.py](/Users/edr/code/JouleWise/joulewise/adapters/node_client.py); [powermetrics.py](/Users/edr/code/JouleWise/joulewise/adapters/powermetrics.py).  
   Remote markers produce offset estimates and bounds; powermetrics records `plist_anchor_offset_s`; events use epoch `time.time()`. But the reducer integrates as if timestamps are exact. Failure scenario: a remote node’s offset bound is 80 ms and a transfer or deserialize phase is 120 ms; the code can still produce phase joules unless a future composite reducer blocks it. For Apple, readiness-anchor uncertainty can shift first samples relative to `sampling_started`, affecting TTFT/phase attribution.

7. **MAJOR: Controller co-residency contamination is mitigated, not measured.**  
   Citation: [measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md) “Controller Co-Residency”; [controller.py](/Users/edr/code/JouleWise/joulewise/controller.py) measured-run buffering.  
   The design avoids disk writes and polling inside the measured window, and idle baseline includes the resident controller. But runtime and controller still share CPU, scheduler, memory pressure, thermal state, and possibly GPU driver pathways. Failure scenario: a small model’s energy/token changes because Python-side token logging or stream handling shifts CPU package power; idle subtraction removes the floor but not workload-correlated controller work.

8. **MAJOR: Thermal protocol uses power recovery as a proxy, but it is not a thermal-state protocol.**  
   Citation: [measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md) “Thermal State” and “Repetition, Ordering, And Thermal Equilibrium”; [controller.py](/Users/edr/code/JouleWise/joulewise/controller.py) cooldown gate.  
   The cooldown gate waits until a rolling idle-power mean returns within 10% of the prior baseline. That is pragmatic, but it can miss latent die temperature, fan hysteresis, battery/charger state, or DVFS governor memory. Failure scenario: condition B always follows a high-power condition; idle power appears recovered, but max frequency or thermal pressure differs, changing latency and energy.

9. **MAJOR: Wall-plug ground truth is planned but absent, and this correctly caps cross-boundary claims; it should also cap absolute-energy confidence.**  
   Citation: [claims_ladder.md](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md) Global Rules; [risk_register.md](/Users/edr/code/JouleWise/docs/risk_register.md) R-007; [phase_4_plan.md](/Users/edr/code/JouleWise/docs/phase_4/phase_4_plan.md) F11.  
   The docs are honest that wall meter calibration is missing and cross-boundary comparisons are descriptive. But an advisor would also ask for at least one external sanity check per backend to bound absolute telemetry trust. Failure scenario: powermetrics and nvidia-smi both pass strict validation, but both undercount memory/host energy, and the report’s “J/request” values are interpreted as system energy.

10. **MINOR: Strict validation proves artifact consistency, not instrument validity, and README language risks overstating that.**  
   Citation: [README.md](/Users/edr/code/JouleWise/README.md) “Current State”; [cli.py](/Users/edr/code/JouleWise/joulewise/cli.py) strict validation; [run_bundle_layout.md](/Users/edr/code/JouleWise/docs/contracts/run_bundle_layout.md) raw artifact source-of-truth.  
   The README says strict validation “validates the recorded evidence path” and notes it does not rerun hardware, which is fair. But readers may still conflate re-derivation with physical validation. Failure scenario: a bundle is strict-valid, so a user treats 47 J as calibrated truth rather than “47 J under powermetrics SoC-rail semantics.”

11. **MINOR: `SummaryMetrics.uncertainty` is effectively unused for single runs.**  
   Citation: [schemas.py](/Users/edr/code/JouleWise/joulewise/schemas.py) `SummaryMetrics.uncertainty`; [aggregate.py](/Users/edr/code/JouleWise/joulewise/aggregate.py).  
   Uncertainty lives in experiment manifests, not per-run summaries. That may be architecturally fine, but the field’s presence in run summaries invites a false expectation that each energy value carries uncertainty. Failure scenario: downstream consumers read per-run summaries and miss the experiment-level intervals and quality gates.

12. **MINOR: nvidia-smi timestamp parsing depends on node timezone metadata and legacy fallback.**  
   Citation: [nvidia_smi.py](/Users/edr/code/JouleWise/joulewise/adapters/nvidia_smi.py) timestamp assumption; [node_worker_protocol.md](/Users/edr/code/JouleWise/docs/contracts/node_worker_protocol.md) “nvidia-smi Timestamp And CSV Rules.”  
   New artifacts record UTC offset, but legacy fallback uses parser-local timezone. Failure scenario: old raw CSVs are reprocessed on a controller in a different timezone and sample times shift enough to alter window inclusion.

**3. NO-HARDWARE-FIXABLE GAPS**

Several high-value gaps can be closed before broader hardware arrives.

First, write a real error-budget spec. For each backend and metric/window class, define terms: sensor systematic, sensor quantization/resolution, sampling interval, timestamp anchor uncertainty, interpolation/aliasing bound, idle-baseline standard error, idle drift term, and clock-offset bound. Even if some terms are initially “unknown, claim ceiling L1,” the structure is the metrology upgrade.

Second, implement uncertainty propagation for idle-subtracted request energy: at minimum, `Var(E_idle_sub) = Var(E_gross_repeat) + duration^2 * Var(P_idle_mean)` plus a drift term or quality flag. For single bundles, report “not estimable” rather than leaving the uncertainty field semantically dead.

Third, make detection floors executable before campaigns. The docs already specify P2-015/Phase 4 floors; turn that into a versioned calibration artifact schema and a validator gate. Reducers can keep emitting numbers, but claim tooling should refuse L2/L3 if floor artifacts are absent.

Fourth, hard-gate under-resolved phase claims. Keep raw `phase_energy_j`, but add a claim-facing field or validator that marks phase energy non-claim-bearing when sample count, duration/sampling ratio, or clock bound fails. The current `phase_identifiability` flag is the right start.

Fifth, add backend-specific telemetry caveat fields: powermetrics = Apple-reported SoC subsystem estimate, not calibrated wall; nvidia-smi = driver-reported board power, update/averaging semantics unknown unless measured; wall_meter = AC full-system. Require these caveats in report templates.

Sixth, specify calibration runbooks now: idle load, step load, sustained load, burst load, and simultaneous platform+wall capture. You cannot execute them without hardware/meter, but you can pre-register what will count as acceptable agreement and what claim ceilings apply if absent.

**4. VERDICT**

As specced, JouleWise would stand up as a rigorous auditable energy-measurement harness, but not yet as a fully rigorous metrological instrument at the Stanford-PhD-EE advisor bar. Its evidence integrity and claim discipline are strong; its physical measurement model is still underdeveloped. The single highest-leverage improvement is a backend-specific, executable error budget plus detection-floor artifact that propagates idle, sampling, clock, and sensor uncertainty into claim gates. Without that, JouleWise can honestly report boundary-labeled L1 instrument results and cautious within-boundary comparisons, but “scientifically rigorous energy differences” remain only partly supported.

**5. CHECKS PERFORMED**

Read/verified the requested methodology, adapter, bundle, claims, README, and hardware-slice docs; inspected reducer, bundle reader/strict validation, powermetrics, nvidia-smi, node clock alignment, controller lifecycle/cooldown, schemas, and aggregation code.
## Appendix B — L2 Benchmark/statistics lens

**1. STEELMAN**

JouleWise is scientifically useful if it is presented as a boundary-honest measurement instrument plus a controlled workload suite, not as a universal leaderboard. Its strongest design choice is that it treats raw evidence as primary: config, metadata, event logs, power traces, outputs, reducer results, and telemetry logs are bundled and re-reducible. That is the right instinct for energy measurement, and it aligns with the methodological tradition of JouleSort, SPEC/MLPerf-style power work, and newer ML energy tooling: define the system boundary, preserve logs, report uncertainty, and avoid uncalibrated cross-system winners.

The benchmark design is also unusually self-aware. It separates request-level energy from phase/item attribution, forbids item windows from inflating `n`, names measurement boundaries, records runtime token counts and stop reasons, and has a claims ladder that blocks cross-boundary and model-family overreach. The `B` whole-suite bundles x `k` items design is defensible: items provide breadth; bundles provide replication. That is exactly the right anti-pseudoreplication stance for an undergraduate capstone that wants advisor-grade rigor.

The real novelty is not “energy benchmarking” in general. JouleSort, MLPerf Power, Zeus/ML.ENERGY, and related work already cover large pieces of that space. The honest novelty is narrower and stronger: local heterogeneous LLM inference, explicit rail-manifest boundary semantics, re-reducible run bundles, and, if Phase 3 lands, measured energy decomposition for prefill/decode-disaggregated inference over local interconnects. The fixed-vs-marginal model `E = fixed + prefill(prompt_tokens) + decode(output_tokens)` is also a useful engineering abstraction if held to its advertised L3 standard with holdouts and floor gates.

The benchmark can stand up scientifically, but only if it resists becoming a results buffet. Its methodology is strongest when it predeclares primary estimands, reports “not resolvable,” and treats category/import/difficulty findings as controlled measurement results rather than capability claims.

**2. FINDINGS**

1. **BLOCKER: no benchmark-level multiplicity / selection policy.**  
   Citation: [analysis_plans.md §Required fields](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:12), [research_question_bank.md §Capability map](/Users/edr/code/JouleWise/docs/research_question_bank.md:430).  
   The AP rows regulate individual claims, but I found no family-wise or FDR policy for the large question bank, workload categories, model x quant x shape grids, imports, difficulty strata, and “select-after-floors” campaigns. Failure scenario: after running 6 categories x many models/quants/shapes, the report highlights only the two category flips with nominal 95% CIs and calls them L2. That will not survive a Stanford-PhD-EE advisor asking, “How many contrasts did you look at?”

2. **MAJOR: ordering language is not yet operationally consistent.**  
   Citation: [research_question_bank.md §Suite mechanism](/Users/edr/code/JouleWise/docs/research_question_bank.md:116), [prompt_sequencing_spec.md §Sequencing rules](/Users/edr/code/JouleWise/docs/specs/suite_next/prompt_sequencing_spec.md:83).  
   C-015 says order rotates round-robin or Latin-square across bundles, but the later sequencing spec says runtimes execute manifest order today and must report `manifest_order` unless per-repetition manifests or a real policy exist. Failure scenario: `jw.reason` always runs late in a warm session and appears cheaper or more expensive due to thermal/cache state, then gets interpreted as a category effect.

3. **MAJOR: n=5 is acceptable for large effects, not a default scientific sample size.**  
   Citation: [measurement_methodology.md §Statistical Protocol](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:187), [analysis_plans.md §Standing reporting rules](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:30).  
   The MDE arithmetic is good, but n=5 plus t-intervals should be treated as provisional unless Window A variance proves the effect scale. Failure scenario: idle-subtracted CV is 7.4%, a true 5% optimization is invisible, and the benchmark reports “no measurable difference” when the design simply lacked power.

4. **MAJOR: “intervals separate” is the wrong comparison rule.**  
   Citation: [measurement_methodology.md §Statistical Protocol](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:192), [analysis_plans.md AP-3](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:88).  
   Claims should be based on the CI for the paired/block contrast, not visual separation of two marginal intervals. Failure scenario: two conditions are run in ABBA order; marginal CIs overlap, but paired differences are consistent and above floor. The current prose would underclaim. Conversely, separated marginal intervals under drift can overclaim.

5. **MAJOR: thermal equilibrium control is necessary but not sufficient.**  
   Citation: [measurement_methodology.md §Repetition, Ordering, And Thermal Equilibrium](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:171).  
   A 30 s idle-power return within 10%, capped at 5 minutes, is a reasonable practical gate, but it is not a thermal-state guarantee. Failure scenario: skin/fan/DVFS state remains shifted after a long-context suite, idle power recovers, and the next condition inherits a different cooling regime. Cap-hit must downgrade claims unless drift sentinels clear it.

6. **MAJOR: J/token is not comparable across tokenizer families without stronger semantics.**  
   Citation: [claims_ladder.md §Global Rules](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md:29), [prompt_sequencing_spec.md §Current lanes](/Users/edr/code/JouleWise/docs/specs/suite_next/prompt_sequencing_spec.md:18), [research_question_bank.md §Workload/query-set expansion](/Users/edr/code/JouleWise/docs/research_question_bank.md:715).  
   Runtime-observed token denominators prevent fake denominators, but they do not make tokens equivalent work. Failure scenario: Model A has lower J/token on Chinese because it emits more/finer tokens; Model B has higher J/token but lower J/character or J/semantic item. Token metrics should be tokenizer-scoped companion metrics, not cross-family efficiency rankings.

7. **MAJOR: representativeness is controlled, not ecological, and should be named that way.**  
   Citation: [research_question_bank.md §Workload/query-set expansion](/Users/edr/code/JouleWise/docs/research_question_bank.md:711), [PROJECT_STATUS.md §Experiment Plan](/Users/edr/code/JouleWise/PROJECT_STATUS.md:327).  
   The common 512/256 fixed-budget stratum is excellent for mechanism isolation, but it is not representative of local LLM inference overall. Failure scenario: the benchmark headline says category effects are null, but real summarization workloads are dominated by 4K+ prefill and natural-EOS behavior. The docs partly know this; the public benchmark naming must preserve the distinction.

8. **MAJOR: benchmark import design is promising but underpromoted fields are a trap.**  
   Citation: [research_question_bank.md §Benchmark import](/Users/edr/code/JouleWise/docs/research_question_bank.md:283), [prompt_sequencing_spec.md §Manifest and sidecar rules](/Users/edr/code/JouleWise/docs/specs/suite_next/prompt_sequencing_spec.md:49).  
   The import manifest sketch is strong: license hash, archive hash, revision, selection rule, contamination, prompt mapping. But benchmark-import fields are still deferred/rejected in current suite manifests. Failure scenario: HumanEval smoke lands through sidecars, then later cannot prove exact source/prompt/rendering identity from the run identity surface.

9. **MINOR: difficulty metadata quarantine is correct but incomplete for analysis.**  
   Citation: [research_question_bank.md §Difficulty metadata rule](/Users/edr/code/JouleWise/docs/research_question_bank.md:276).  
   “Difficulty is metadata, not causality” is the right rule. Missing piece: difficulty scales are source-local unless calibrated. Failure scenario: HumanEval difficulty, GSM8K grade level, and affine ladder level get plotted on one axis and interpreted as a universal difficulty-energy curve.

10. **MINOR: outlier policy is principled but fragile at n=5.**  
   Citation: [measurement_methodology.md §Statistical Protocol](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:197).  
   Modified z-score on MAD is unstable with five repetitions. Failure scenario: one contaminated run shifts the MAD enough that no point flags, or one benign point dominates. Add leave-one-out influence and trace-level quality causes; keep the current “never silently drop” rule.

**3. NO-HARDWARE-FIXABLE GAPS**

Most gaps above are fixable with specs/software/analysis code alone:

- Add a benchmark-level analysis registry: primary endpoints, secondary endpoints, exploratory endpoints, contrast families, and multiplicity policy. Use Holm for small confirmatory families and BH/FDR or hierarchical models for exploratory category/import sweeps.
- Replace “intervals separate” with contrast-level inference: paired/block difference estimators, randomization/permutation checks where order is randomized, and mixed-effects models for bundle/block/item structures.
- Make ordering executable: generate per-repetition manifests with distinct effective hashes, or implement runtime order policy; otherwise force reports to say `manifest_order`.
- Add a token-normalization contract: request energy is primary; token metrics are tokenizer-scoped; multilingual/code comparisons also report J/character, J/byte, J/source-item, or semantic-pair denominators where available.
- Promote benchmark-import identity fields before real imports: source archive hash, license text hash, revision, selector version, selected IDs hash, prompt template hash, contamination note, and expected-answer quarantine.
- Add an analysis-code gate that refuses L2/L3 output unless AP row, floor artifact, order manifest, multiplicity family, denominator provenance, and claim ceiling are present.
- Add thermal/drift analysis rules: cap-hit handling, drift sentinel regression, position covariates, and mandatory downgrade when drift is above floor.

**4. VERDICT**

JouleWise is scientifically useful as a measurement benchmark if it stays within its own discipline: boundary-labeled, raw-bundle-auditable, floor-gated, and explicit about controlled versus ecological workloads. It is not yet statistically publication-grade as a broad benchmark because the per-claim rigor is stronger than the benchmark-level inference policy. The single highest-leverage improvement is to add a **predeclared benchmark analysis registry with multiplicity-aware contrast families and executable order/randomization manifests**. That one change would prevent most advisor-level objections about cherry-picking, pseudoreplication, and drift-confounded category claims.

**5. CHECKS PERFORMED**

Read required repo docs in read-only/no-network mode, plus related-work draft; no code edits or tests run. Low-confidence literature note: 2025/2026 related-work details were not independently re-verified online.
## Appendix C — L3 Question-bank audit lens

**Per-Question Table**

| ID / short name | Well-posed? | Falsifiable / decidable? | Instrument-sufficient as specced? | Claim ceiling consistent? | Gate | One-line judgment |
|---|---|---|---|---|---|---|
| Q1 Split reduces energy | Mostly: pair/link/model/shape pinned in template | Yes | Not yet: needs split + transfer + calibrated or labeled boundaries | Yes, L2 descriptive unless calibrated | Hardware-gated | Strong central question, but only if “total energy” is decomposed and boundary-labeled. |
| Q2 Link bandwidth sensitivity | Yes | Yes | Needs measured links, not nominal speed | Yes, L2 | Hardware-gated | Clean, engineering-useful, and directly measurable. |
| Q3 Split energy-latency Pareto | Partial: latency metric must be fixed | Yes | Needs Phase 3 split matrix | Yes, L2 | Hardware-gated | Good, but “Pareto” is meaningless until the comparison set and latency metric are frozen. |
| Q4 Fixed + marginal model | Yes under AP-1 | Yes via holdouts | Yes after Window B grid | Yes, L3 | Pre-hardware prep; data pending | One of the strongest: predictive, bounded, and advisor-defensible. |
| Q5 Ranking stability | Mostly | Yes, with MDE rank-gap rule | Yes within boundary; cross-device gated | Yes, L2 | Partly answerable now | Useful but duplicate-prone; must avoid uncalibrated cross-device winners. |
| Q6 / C5-2.10 Boundary sensitivity | Yes | Yes | Needs wall meter / boundary bridge | Yes, L2; L4 only with replication | Hardware-gated | Excellent methods question; turns a limitation into a result. |
| Detection / noise floor | Yes | Yes | Yes after P2-015 | Yes, L1 methodology | Answerable pre-campaign | Essential; should probably be treated as a prerequisite to every other claim. |
| Dark silicon / C5-1.11 | Partial: “fraction of rails” needs denominator | Yes descriptively | Rich telemetry sufficient structurally, not physically absolute | Mostly, L2 structural only | Current Mac | Good if framed as modeled-rail utilization, not true silicon energy. |
| CPU:GPU phase division / C5-1.3 | Yes if phase windows clear samples | Yes | Rich telemetry sufficient; short prefill may fail | Yes, L2 structural | Current Mac | Strong within-boundary phase-structure question. |
| KV-growth decode drift | Partial: needs chunk definitions | Yes | Yes only chunked, not per-token | Yes if L1/L2 chunked | Current Mac | Interesting, but must never imply per-token joule resolution. |
| Cooldown recovery / C5-1.5 | Yes | Yes | Yes with post-run traces | Yes, L1/L2 | Current Mac | Methodologically valuable; may matter more than headline users expect. |
| Failure frontier / C5-1.10 | Yes | Yes | Yes via unsupported bundles + env snapshots | Yes, L1/L2 descriptive | Current Mac | Publishable negative-result dataset if memory pressure and throttle states are standardized. |
| Cold-start / keep-warm / C5-1.7 | Yes | Yes | Not yet: needs load-window sampling | Yes, L2 after extension | Current Mac + harness extension | Strong applied systems question; currently underspecified by the measured window. |
| Energy per correct vs difficulty / C5-1.9 | Partial: “similar quality bands” is soft | Decidable only with denominator guard | Suite/scorer not enough unless envelope gate passes | Yes, capped at L2 | Current Mac + scored suite campaign | Risky but defensible only as controlled-ladder accounting, not intelligence efficiency. |
| Speculative decoding / C5-2.5 | Yes if output equivalence pinned | Yes | Needs runtime support + accepted-token accounting | Yes, L2 | Runtime/hardware gated | Good question; quality equivalence is the hard part. |
| Power-mode Pareto | Partial: OS modes and workload set missing | Yes | Needs power-mode as config field | L2 possible | Current Mac + config extension | Potentially useful, but not analysis-ready. |
| General joules-per-solved-task | No | Not cleanly | Measurement alone insufficient | Correctly killed | Deferred/killed | This would drag JouleWise outside its strongest measurement boundary. |
| C5-I.1 External benchmark signatures | Partial: “families” broad | Yes with matched shape | Suite import sufficient after AP | L2 ceiling okay | Substrate | Worth doing only after token-shape matching; otherwise it is category confounding. |
| C5-I.2 Difficulty strata vs energy | Weak: source difficulty is heterogeneous | Barely, as association | Instrument can observe energy/stop behavior | L1/L2 ceiling cautious | Substrate | Low scientific value unless difficulty metadata is standardized. |
| C5-I.3 / C5-W.4 FLORES fertility tax | Yes | Yes | Yes with semantic and token-matched legs | Yes, L2 | Substrate + source work | Strong natural question for this instrument. |
| C5-I.4 Harness overhead floor | Yes | Yes | Shim markers sufficient | Yes, L1/L2 | Substrate/export | Good methodology question; especially useful for itemized suites. |
| C5-I.5 Prompt-template sensitivity | Yes | Yes | Yes | Yes, L2 | Substrate/import | Clean, practical, and likely publishable if matched by item. |
| Session-shape energy | Yes under Q4 coefficients | Yes | Suite sessions sufficient | L2/L3 depending holdout | Substrate | Strong follow-on to Q4: tests whether coefficients compose in realistic sessions. |
| Order-position effects | Yes | Yes | Suite order metadata sufficient | L2 | Substrate | Good contamination/drift probe, not a headline result. |
| Cache / prefix economics | Partial: prefix/cache states need exact policy | Yes | Needs cache controls | L2 | Substrate + runtime support | Valuable, but currently too many cache mechanisms are bundled together. |
| Reload-vs-resident scheduling | Yes | Yes | Needs load and resident idle windows | L2 | Harness extension | Overlaps cold-start; merge or alias it. |
| Auditable evidence capability | Yes as capability, not science | Yes | Already yes | L0/L1 | Answered today | Not a research question; it is the artifact contribution. |
| Qwen2.5 smoke consumption | Yes | Yes | Already yes | L1 only | Answered today | Legit instrument result, not comparative science. |
| Qwen3.5 smoke consumption | Yes | Yes | Already yes | L1 only | Answered today | Legit instrument result; do not compare as scaling. |
| Two-model active-param non-claim | Yes as negative guard | Yes | Already enough to reject scaling claim | L1 hypothesis only | Answered today | Good honesty check; not itself a positive result. |
| Short-prefill resolvability | Yes | Yes | Already mostly yes | L1 “not resolvable” | Answered / Window A | Important because it prevents bogus tiny joule claims. |
| Same-machine MLX KV replay | Yes | Yes | Already yes for same stack | L1 feasibility | Answered today | Good feasibility result; not portability evidence. |
| Per-profile Mac baselines | Yes | Yes | Yes after 2M | L1 | Current Mac | Necessary dataset, but not novel alone. |
| Workload shape changes request energy | Yes under AP-2 | Yes | Yes after 2M | L2 | Current Mac | Good descriptive result; distinct from Q4 because it does not predict holdouts. |
| Content sentinel / AP-6 | Yes | Yes | Yes | L2 | Substrate | Excellent control for token-shape claims. |
| External marked-runner layer | Partial: feasibility, not science | Yes | P2-022 sufficient | L1/L2 with AP | Substrate/export | Useful infrastructure; only becomes research when overhead or energy comparison is specified. |
| HumanEval import smoke | Yes as plumbing | Yes | Yes after import | L0/L1 | Substrate/import | Correctly scoped; no accuracy or coding-capability claim. |
| C5-1.1 Active-parameter scaling | Weak: architecture/family confounded | Partly | Instrument measures, but design underpowered | L2 pairwise only | Current Mac | Scientifically tempting but overfit-prone; 4-6 models cannot support the advertised regression. |
| C5-1.2 Context-length scaling | Yes | Yes | Yes, with chunked phase limits | L2/L3 if modeled | Current Mac | Strong and natural for local inference. |
| C5-1.4 DVFS throttling warning | Partial: “predict” needs predeclared horizon | Yes | Rich telemetry sufficient | L2 if prediction rule fixed | Current Mac | Good if converted from characterization to a predictive rule. |
| C5-1.6 Sampling overhead | Yes | Yes | Yes after detection floor | L2 if above floor | Current Mac | Likely null; still useful if ABBA and floor-gated. |
| C5-1.8 Runtime attribution | Partial: runtime vs artifact confounding | Yes descriptively | Yes | L2 stack-vs-stack | Current Mac | Valuable, but “belongs to runtime not model” overstates attribution when formats differ. |
| C5-1.12 Quantization decomposition Mac | Yes | Yes | Yes | L2 | Current Mac | Strong, provided output divergence is reported. |
| C5-W.1 Category beyond token counts | Yes under AP-4 | Yes | Yes after suite | L2 | Substrate | Very strong because the null is meaningful. |
| C5-W.2 Thinking-token inflation | Mostly | Yes | Yes with natural-EOS pilot | L2 | Substrate | Good if attributed to emitted-token/stop distributions, not cognition. |
| C5-W.3 Category ranking stability | Partial | Yes | Needs enough category x model x quant data | L2 | Substrate | Probably too broad for first campaign; Q5 duplicate in workload clothing. |
| C5-2.1 Quantization cross-stack | Yes within stack | Yes | Needs CUDA/3050 data | L2 | Hardware-gated | Good extension; cross-boundary comparison must stay descriptive. |
| C5-2.2 Batch size phase split | Yes | Yes | Needs batching backend | L2 | Hardware-gated | Strong systems question for serving-style hardware. |
| C5-2.3 Predicted vs measured KV economics | Yes | Yes | Needs second node/link | L2 | Hardware-gated | One of the best Phase 3 questions. |
| C5-2.4 KV-cache quantization | Yes | Yes | Needs cache portability + q8 support | L2 | Hardware/runtime gated | Good but depends on runtime features outside JouleWise. |
| C5-2.6 Request coalescing | Mostly | Yes | Needs arrival traces and batching | L2 | Hardware-gated | Useful, but starts to become scheduler research. |
| C5-2.7 Device perf/W rankings held runtime | Mostly | Yes | Needs devices; calibration for cross-boundary | L2/L4 | Hardware-gated | Better than generic device ranking, but still boundary-fragile. |
| C5-2.8 Placement optimality | Yes | Yes | Needs Q4 + transfer + measured splits | L2/L3 | Hardware-gated | Excellent capstone extension if Phase 3 lands. |
| C5-2.9 Local-vs-datacenter crossover | Partial: cloud side modeled | Decidable only as scenario | Local side measurable; cloud side not | Scenario only | Wall/network gated | Interesting, but not a JouleWise-measured comparison. |
| C5-3.1 Unit variance | Yes | Yes | Needs second unit | L4 enabler | New hardware | Scientifically important; cheapest route to generalization. |
| C5-3.2 Battery-path validation | Yes | Yes | Needs USB-C PD analyzer | L2/L4 bridge | New hardware | Strong calibration purchase. |
| C5-3.3 Cross-ISA NPU/SoC | Partial: broad | Yes if narrowed | Needs adapters + hardware | L4 only after replication | New hardware | Too ambitious unless split into one platform-specific adapter study. |
| C5-3.4 Phone-class edge | Partial: telemetry uncertain | Yes as feasibility | Not guaranteed | L0/L1 first | New hardware | Fine as feasibility, weak as promised science. |
| C5-3.5 Cross-lab replication | Yes | Yes | Needs external lab | L4 enabler | Coordination gated | Essential for public benchmark credibility. |

**Strongest 5**

1. **Q4 fixed + marginal model**: bounded variables, holdout prediction, AP-1, and a clear L3 ceiling. This is the most advisor-defensible “science” in the bank.
2. **Detection floor**: not glamorous, but it is the backbone. Without it, many energy differences are numerology.
3. **C5-2.3 predicted-vs-measured KV economics**: natural to the split-inference thesis, tightly measurable, and useful even if live split fails.
4. **C5-W.1 token-shape sufficiency / category residual**: a clean null-or-effect design that prevents hand-wavy workload claims.
5. **Q6 / C5-2.10 boundary sensitivity**: strong methodology contribution; directly tests whether rail-level conclusions survive wall-level measurement.

**Weakest / Most Overclaimed 5**

1. **C5-1.1 active-parameter scaling**: too many confounds for 4-6 model points. Runtime, architecture, quantization, tokenizer, KV structure, and model family all move.
2. **General joules-per-solved-task / intelligence-per-joule**: correctly quarantined. It would make JouleWise depend on evaluation policy rather than measurement rigor.
3. **C5-I.2 difficulty strata vs energy**: source-provided difficulty is not a controlled independent variable.
4. **C5-2.9 local-vs-datacenter crossover**: scenario analysis, not a measured-equivalent comparison. Good appendix, weak headline.
5. **C5-W.3 category ranking stability**: duplicates Q5 and risks becoming a combinatorial campaign without a sharp scientific payoff.

**Coverage Gaps**

- Telemetry perturbation cost: does `powermetrics`, `nvidia-smi`, wall sampling, or external marker emission measurably change energy/latency?
- OS/runtime version drift as science: before/after macOS, MLX, llama.cpp, or driver updates with pinned bundles.
- Marker/window alignment sensitivity: how much reducer output changes under plausible timestamp jitter and sampler phase offset.
- Output-token identity effects: fixed token count is not the same as fixed decoded token sequence; the bank covers prompt content better than output content.
- Idle-baseline stationarity: detection floor exists, but there should be a direct question about how idle model choice affects idle-subtracted conclusions.
- Quality-equivalent quantization/runtime comparisons: quantization rows mention output divergence, but need an AP-level equivalence rule before efficiency claims.
- Energy model portability across workload mixtures: session-shape exists, but it should explicitly test coefficient transport from synthetic grids to realistic app traces.

**Fully Preparably Pre-Hardware**

These can have analysis plan, manifest/config templates, expected bundle schema, exclusion rules, and figure skeletons written now:

- Q1, Q2, Q3 split suite: device-pair manifest, per-stage windows, transfer payload ladder, boundary labels, Pareto metric.
- Q6 / C5-2.10: rail-vs-wall paired plan, synchronization contract, flip/no-flip decision rule.
- C5-2.3 KV economics: payload sizes, link-speed matrix, predicted-size formula, transfer-energy artifact spec.
- C5-2.7 device rankings: same-runtime manifest and calibration downgrade rules.
- C5-2.8 placement optimality: Q4 coefficient input contract plus measured-split validation cells.
- C5-2.1 and C5-2.2: CUDA/3050 campaign manifests and boundary-labeled claim templates.
- C5-3.1 and C5-3.5: replication runbook, frozen suite manifest, expected artifact hash manifest.
- C5-3.2: USB-C/AC bridge plan and boundary-comparison AP.
- C5-I.1 to C5-I.5: import/export manifest contracts and AP rows, especially before external benchmark claims proliferate.

**Findings**

- **BLOCKER:** The bank lacks a canonical RQ registry. The same question appears as promoted Q, banked item, capability-map row, and tiered C5 item. That will break claims indexing unless aliases, status, ceiling, AP owner, and campaign owner are normalized.
- **BLOCKER:** Several rows still invite causal or architectural attribution beyond the measurement boundary. Active-parameter scaling and runtime attribution are the clearest examples.
- **MAJOR:** Many “questions” are capability statements or application ideas, not research questions. The capability map is useful, but it should not be mixed into the RQ bank without labels.
- **MAJOR:** Some “current hardware” questions actually require harness extensions, scored-suite gates, or post-floor APs. The bank should distinguish hardware-gated from software/protocol-gated.
- **MAJOR:** Correctness-bearing questions remain scientifically fragile. The AP-5 quarantine is good, but the bank should keep these visibly secondary.
- **MINOR:** The unexpected-applications section is useful product thinking, but it should be separated from the scientific agenda to avoid scope creep.

**Verdict**

JouleWise has a credible research core, but the bank is overgrown. The defensible center is audited energy measurement, detection floors, fixed/marginal energy modeling, boundary sensitivity, and split/KV transfer economics. The weak edge is where the bank tries to infer architecture, intelligence, or datacenter equivalence from a local power instrument. A Stanford-PhD-EE advisor would likely respect the rigor of the contracts, but would ask for a sharper canonical question set with duplicates collapsed and attribution limits enforced.

**Checks Performed**

Read `docs/research_question_bank.md` in full, `PROJECT_STATUS.md`, `docs/contracts/claims_ladder.md`, and `docs/contracts/analysis_plans.md`; no network used; sandbox was read-only.
## Appendix D — L4 Advisor-simulation lens

**PART A — The Attack**

1. **Your scope is still too big for one undergraduate.** Five phases, split inference, interconnect sweep, NVIDIA, Orin, wall meter, external benchmark interop, workload suite, claims index, and final release is a graduate-lab program unless aggressively cut. The docs admit supervisor scope, calendar dates, wall-meter availability, target telemetry permissions, and Orin/remote access are still open: [AGENT_PLAN.md](/Users/edr/code/JouleWise/AGENT_PLAN.md:98), [docs/milestones.md](/Users/edr/code/JouleWise/docs/milestones.md:3), [docs/risk_register.md](/Users/edr/code/JouleWise/docs/risk_register.md:21).

2. **What is the scientific claim, not the software deliverable?** “I built a careful instrument” is valuable engineering, but the capstone needs a defensible result. The docs now split guaranteed local measurement from gated split inference, which helps, but the final headline is still not frozen: [PROJECT_STATUS.md](/Users/edr/code/JouleWise/PROJECT_STATUS.md:122).

3. **External validity is nearly nonexistent if you have one sample of each hardware target.** One M3 Max, one RTX class target, one Orin is not “Apple vs NVIDIA vs edge.” At best it is stack-specific characterization. The claims ladder handles this by requiring independent replication for L4 generalization, but the report must obey it ruthlessly: [docs/contracts/claims_ladder.md](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md:38).

4. **Software stack may swamp hardware.** MLX vs vLLM vs llama.cpp differ in tokenizer, kernels, batching, KV behavior, graph capture, quantization, and sampling. If you call that “hardware efficiency,” I will stop reading. The adapter separation is good, but the claim must be stack-bound: “M3 Max / MLX / powermetrics rails,” not “Mac is more efficient.”

5. **powermetrics and nvidia-smi are not ground truth.** You preserve raw telemetry and name boundaries, but without wall/PD cross-checks you have driver-reported or OS-reported power, not calibrated energy. The docs correctly limit cross-boundary claims absent calibration: [docs/contracts/claims_ladder.md](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md:19), [docs/contracts/measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:111).

6. **J/token comparability across models and tokenizers is dangerous.** Tokens are not common physical units across tokenizers, prompt sources, BOS handling, stop policies, and output caps. The docs partly neutralize this with runtime-observed token counts and provenance requirements, but per-token headline language must be stack/model/tokenizer scoped: [docs/contracts/claims_ladder.md](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md:29), [docs/contracts/run_bundle_layout.md](/Users/edr/code/JouleWise/docs/contracts/run_bundle_layout.md:154).

7. **Detection floor is not optional.** You already saw contaminated idle-subtracted variance. Until P2-015 exists, small energy differences are not results. The docs say below-floor effects become `not resolvable`, but the calibration artifact is still pending: [docs/research_question_bank.md](/Users/edr/code/JouleWise/docs/research_question_bank.md:29), [docs/contracts/analysis_plans.md](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:22).

8. **Single-run or n=3 numbers must not become comparative claims.** The first real Mac result is L1-ish instrument evidence, not a comparison. Your own ladder says L2 needs n>=5 per condition, CIs, strict bundles, order, and floor clearance: [docs/contracts/claims_ladder.md](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md:39).

9. **Remote/NVIDIA protocol is still fixture-first.** The repo has a serious node-worker contract, but the docs explicitly mark 2K protocol pins provisional until first live hardware contact: [docs/contracts/node_worker_protocol.md](/Users/edr/code/JouleWise/docs/contracts/node_worker_protocol.md:3), [PROJECT_STATUS.md](/Users/edr/code/JouleWise/PROJECT_STATUS.md:228).

10. **Who uses this benchmark, and for what decision?** The docs imply users are local-LLM practitioners deciding workload/model/runtime/energy tradeoffs, and researchers needing auditable energy bundles. That needs to be a first-page claim: “Use JouleWise to decide whether a given local stack/workload is measurably more energy efficient under a named measurement boundary.”

**PART B — The Steelman**

The strongest defense is that this project is unusually honest about claim ceilings. The claims ladder forbids cross-boundary winners without calibration, requires strict validation as the entry ticket, and caps generalized findings at L4 only with replication: [docs/contracts/claims_ladder.md](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md:14). That is exactly what many LLM-energy papers fail to do.

The evidence model is also strong. Run bundles preserve configs, metadata, events, power traces, outputs, logs, and summaries; summaries are explicitly derived, not source truth: [docs/contracts/measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:8), [docs/contracts/run_bundle_layout.md](/Users/edr/code/JouleWise/docs/contracts/run_bundle_layout.md:102). The code backs this up: strict validation re-reduces summaries and checks raw-to-trace paths: [joulewise/cli.py](/Users/edr/code/JouleWise/joulewise/cli.py:272); tests pin powermetrics raw-to-trace tamper detection and provenance failures: [tests/test_cli_run.py](/Users/edr/code/JouleWise/tests/test_cli_run.py:707).

The methodology admits boundary problems rather than hiding them. powermetrics, nvidia-smi, Jetson rails, and wall meter are separate physical boundaries with explicit exclusions: [docs/contracts/measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:119). That is mature.

The statistical plan is pre-registered enough to be credible: n thresholds, Student-t intervals, bootstrap sensitivity, outlier handling, raw points in figures, and “not resolvable” language are specified before the main campaign: [docs/contracts/measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:187). Analysis-plan rows require window class, unit of analysis, dependence structure, floor gate, MDE, denominator provenance, and disqualifiers: [docs/contracts/analysis_plans.md](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:12).

The project also has a credible fallback ladder. If split inference collapses, the guaranteed capstone is still auditable Apple-Silicon local LLM energy characterization plus synthetic transfer/compositional analysis: [PROJECT_STATUS.md](/Users/edr/code/JouleWise/PROJECT_STATUS.md:122), [docs/risk_register.md](/Users/edr/code/JouleWise/docs/risk_register.md:225).

**PART C — Gap List**

| Attack | Current answer | Spec-only artifact to neutralize |
|---|---|---|
| Scope realism | Partial: descope ladder exists, but dates and approval are TBD. | One-page “minimum viable capstone contract” with hard stop-lines, deliverables, and cut triggers. |
| Science vs plumbing | Partial: Q4-Q6 and claim tracks exist. | Freeze one headline claim and 2 fallback claims with allowed claim level. |
| One sample external validity | Adequate if obeyed: L4 requires second target/unit. | Add “single-unit limitation language” template for final report captions. |
| Stack confound | Partial: boundaries and adapter contracts exist. | Add a “stack identity table” requiring runtime, kernel/library, tokenizer, model artifact, quantization, sampler, and batching policy in every figure. |
| Telemetry trust | Partial: raw preservation and boundaries strong; calibration still gated. | P2-015 detection/calibration design doc including wall/PD/nvidia-smi/powermetrics trust hierarchy and no-calibration claim ceiling. |
| J/token comparability | Partial: runtime token provenance exists. | Add tokenizer-normalization policy: when J/output-token is allowed, when request-energy is primary, and when cross-tokenizer comparison is forbidden. |
| Detection floor | Partial: planned and in AP rows, not complete. | P2-015 floor artifact schema plus example mock/calculated acceptance thresholds. |
| n=3 / underpowered comparisons | Adequate in docs: L2 requires n>=5 and intervals. | Add claims-index linter/spec that rejects L2/L3 rows without n/floor/CI fields. |
| Remote hardware provisional | Adequate: clearly marked provisional. | Live-validation checklist template with pass/fail evidence fields before any NVIDIA/Orin claim. |
| Who uses it | Partial: implicit, not sharp. | Add “benchmark consumer and decision” section to README/status: local deployer, researcher, advisor/reviewer; decision each can make. |

**PART D — Verdict**

I do **not** sign off on the final methodology chapter today. I would sign off on the **instrument-methodology draft as a strong provisional chapter**, because the evidence-bundle discipline and claim ladder are real. But final sign-off requires the detection-floor artifact, frozen claim scope, and explicit calibration/telemetry trust policy.

The three changes that most move me toward signing:

1. Finish P2-015 as a written detection-floor and calibration specification before more campaign data.
2. Freeze the capstone headline: “auditable, boundary-labeled local LLM energy characterization on named stacks,” with split inference explicitly gated.
3. Add a stack/tokenizer comparability policy so no figure accidentally implies hardware causality from MLX-vs-vLLM-vs-llama.cpp differences.

CHECKS PERFORMED: Read requested docs and one run report; skimmed AGENT_PLAN; inspected bundle/strict-validation/reducer/powermetrics code and related tests. Did not run tests because the sandbox is read-only.
## Appendix E — Lead synthesis packet sent to discussion

# Lead synthesis — JouleWise scientific-rigor review (Fable, 2026-07-09)

Inputs: four independent gpt-5.5 review lenses (L1 metrology, L2 benchmark/stats,
L3 question-bank audit, L4 advisor simulation) + lead's own read of
research_question_bank.md, measurement_methodology.md, claims_ladder.md,
analysis_plans.md, PROJECT_STATUS Q1-Q6. Full lens reports live in this
directory: L1-metrology.md, L2-benchmark-stats.md, L3-question-bank.md,
L4-advisor-sim.md.

## Where all lenses + lead converge (treated as settled)

1. The evidence architecture (immutable bundles, strict rederivation,
   boundary table, claims ladder with forbidden language, pre-registered
   AP rows with floor gates and dependence rules) is the project's real
   contribution and is stronger than typical published LLM-energy work.
2. The project is NOT yet at final advisor sign-off, and the gap is
   entirely in the physical/statistical inference layer, not the evidence
   layer. Every blocker is closable with specs/software only — no hardware.
3. Verdict shape: "strong provisional methodology chapter; sign-off after
   named artifacts land."

## Consolidated blocker-class findings (lead triage)

B1 (L1) No metrological error budget: t-intervals capture repetition noise
   only; idle-baseline variance, sensor systematic, timestamp/interpolation
   error are not propagated into claim gates. Idle subtraction is scalar
   stationary-baseline removal with stored-but-unused stddev.
B2 (L2) No benchmark-level multiplicity/selection policy: AP rows regulate
   single claims; nothing governs the contrast family across categories x
   models x quants x shapes; cherry-picking objection is currently open.
B3 (L3) No canonical RQ registry: same question exists as promoted Q,
   banked item, capability-map row, and C5 tier row; aliases/status/
   ceiling/AP-owner not normalized; a few rows still invite attribution
   beyond the measurement boundary (C5-1.1 wording, C5-1.8 "belongs to
   runtime").
B4 (L4) Headline claim not frozen: advisor needs ONE defensible headline
   ("auditable, boundary-labeled local LLM energy characterization on
   named stacks") with split inference explicitly gated as stretch.

## Major-class accepted by lead (design-bearing, need peer discussion)

M1 (L2) Replace "intervals separate" with contrast-level inference
   (paired/block difference CI; permutation checks where order randomized).
   This AMENDS D-014's statistical protocol — design-bearing.
M2 (L2) Ordering promise vs implementation: C-015 says round-robin/Latin
   square; sequencing spec says manifest_order today. Make ordering
   executable (per-repetition manifests) or force claim wording downgrade.
M3 (L2/L4) Token-normalization contract: request energy primary; J/token
   tokenizer-scoped; cross-tokenizer comparisons need J/char / J/byte /
   semantic-pair companion denominators.
M4 (L1) Hard-gate under-resolved phase windows for claim-bearing use
   (raw phase_energy_j stays; claim tooling refuses below sample/duration/
   clock-bound thresholds).
M5 (L1/L2) Thermal: cooldown power-recovery gate is a proxy; cap-hit or
   sentinel drift above floor must downgrade claims (partially in AP rules).
M6 (L1/L4) Backend telemetry trust hierarchy: per-backend caveat fields +
   pre-registered calibration runbooks (wall/USB-C PD) with acceptance
   thresholds written NOW, executed when hardware arrives.

## Lead positions to challenge

P1 Severity: B1 is a blocker for the FINAL methodology chapter, not for
   current operations — the ladder already caps everything at L1/L2 and
   floors are pending-P2-015 by design. Agree/disagree?
P2 Right-sizing: full clinical-trial-style multiplicity machinery would be
   over-engineering for an undergrad capstone. Proposed: a lightweight
   analysis registry — every reader-facing claim labeled
   primary/secondary/exploratory; Holm within small confirmatory families;
   BH or hierarchical-model honesty for exploratory sweeps; registry
   frozen before each campaign. Is this the right size?
P3 The canonical RQ registry (B3) should be THE organizing artifact for
   the next work phase (specs/plans for all no-hardware pieces), with
   columns: canonical ID, aliases, status, claim ceiling, AP owner,
   campaign owner, gate (hardware vs software vs floor), pre-hardware
   preparability. Agree this subsumes L3's lists (a)-(d)?
P4 Proposed pre-hardware work order (step-2 plan skeleton):
   1. P2-015 detection-floor + calibration artifact spec (already queued;
      now also carries error-budget structure per backend/metric/window).
   2. Uncertainty propagation in reducer/aggregator (idle-var + drift term;
      "not estimable" for single bundles).
   3. Canonical RQ registry + frozen capstone headline + claims-index
      linter (refuse L2/L3 without AP row/floor/order/multiplicity fields).
   4. Statistical protocol amendment (M1) + analysis registry (P2).
   5. Token-normalization contract + stack identity table (M3, L4 gap).
   6. Ordering executability (M2), phase-window claim gate (M4),
      telemetry-caveat fields + calibration runbooks (M6).
   7. Pre-hardware campaign packs for the L3 "fully preparable" list
      (Q1-Q3 split suite, Q6 rail-vs-wall, C5-2.3 KV economics, C5-2.7,
      C5-2.8, C5-3.1/3.5 replication runbook, C5-I.1..I.5 contracts).
   Challenge the order and the cut-lines.
P5 Anything all four lenses AND the lead missed (negative space)? In
   particular: telemetry perturbation cost (L3 flagged), sampler-phase
   jitter sensitivity, output-token identity effects — do any of these
   deserve blocker status rather than gap status?

## Appendix F — D1 discussion round (gpt-5.5 response to the synthesis)

**P1 — AMEND**

B1 is not a blocker for L0/L1 smoke/current harness operation, but it is a blocker before any campaign is allowed to mature into L2/L3 evidence. The lead is too gentle if “current operations” includes collecting 2M/Window A data intended for comparative claims.

The docs already gate reader-facing claims on detection floors: effects below floor must be `not resolvable` [claims_ladder.md](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md:26), and every L2/L3 AP row requires `max(floor_abs_j, floor_cmp_j)` from P2-015 [analysis_plans.md](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:22). But implementation today only subtracts `idle_mean * duration` [reduce.py](/Users/edr/code/JouleWise/joulewise/reduce.py:409) and aggregates repetition t-intervals [aggregate.py](/Users/edr/code/JouleWise/joulewise/aggregate.py:260). Idle stddev is recorded as quality data, not propagated [reduce.py](/Users/edr/code/JouleWise/joulewise/reduce.py:432). So: L1 instrument observations may proceed; claim-bearing comparative campaigns need the error-budget/floor contract frozen first, or you risk collecting data under an underspecified inference model.

**P2 — AGREE, with enforcement**

Yes, clinical-trial machinery is overkill. The proposed primary/secondary/exploratory registry is the right size for a capstone. But it must be executable, not prose.

Required addition: every reader-facing claim row needs a `family_id`, `claim_role`, `selection_scope`, and `multiplicity_rule`. Holm for small confirmatory families is right. BH/FDR or explicitly exploratory hierarchical summaries are fine for sweeps. The existing AP contract is strong, but it does not yet include multiplicity family fields [analysis_plans.md](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:12). Without that, B2 remains open because the suite space is large: categories, models, quants, shapes, imports, and post-floor shortlist items.

Also amend D-014 now: “intervals separate” is the wrong rule [measurement_methodology.md](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:201). Use contrast-level CIs/block-paired differences for comparative claims.

**P3 — AMEND**

A canonical RQ registry should be a central artifact, but not *the* organizing artifact ahead of the error-budget/statistical contracts. It should sit beside P2-015 and the analysis registry.

It should subsume L3’s lists only if it distinguishes `research question`, `capability claim`, `application idea`, and `methodology artifact`. The current bank explicitly mixes these: capability-map rows, promoted Qs, Tier C5 rows, and application sketches coexist [research_question_bank.md](/Users/edr/code/JouleWise/docs/research_question_bank.md:443). Add columns beyond the lead’s list: `question_type`, `multiplicity_family`, `denominator_policy`, `stack_identity_required`, `boundary_class`, `forbidden_upgrade`, and `preclaim_linter_status`.

This is also where I’d normalize aliases for Q6/C5-2.10, Q5/C5-W.3, cold-start/reload-vs-resident, and benchmark import rows.

**P4 — AMEND the order**

I would reorder the pre-hardware work like this:

1. Freeze the capstone headline and minimum viable capstone contract first. The status doc already has the two-track shape: guaranteed local energy characterization, split as gated upgrade [PROJECT_STATUS.md](/Users/edr/code/JouleWise/PROJECT_STATUS.md:122). Make that the controlling scope before generating more artifacts.

2. P2-015 as a combined detection-floor, calibration, telemetry-trust, and error-budget spec. Do not leave calibration runbooks and backend caveats until step 6; they define what the floors mean.

3. Statistical protocol amendment plus analysis registry: contrast-level inference, multiplicity family fields, selection policy, and claim role labels. This should land before reducer/aggregator output is interpreted.

4. Reducer/aggregator uncertainty propagation and claim gates: idle variance, drift term, timestamp/sample/window terms, `not estimable` for single bundles, and hard refusal for under-resolved claim-facing phase/item windows. Raw `phase_energy_j` can remain; claim tooling must respect `phase_identifiability` [reduce.py](/Users/edr/code/JouleWise/joulewise/reduce.py:593).

5. Canonical RQ registry plus claims-index linter. The linter should reject L2/L3 claims without AP row, floor, order policy, multiplicity family, denominator provenance, and stack/boundary identity.

6. Ordering executability. This needs to move earlier than any suite campaign pack: the sequencing spec says runtimes execute `manifest_order` today and round-robin/Latin-square claims require per-repetition manifests or a real execution policy [prompt_sequencing_spec.md](/Users/edr/code/JouleWise/docs/specs/suite_next/prompt_sequencing_spec.md:83).

7. Token-normalization and stack identity table. Request energy remains primary; J/token is tokenizer-scoped; cross-tokenizer figures need J/char, J/byte, item/semantic denominators, or must avoid efficiency-ranking language.

8. Then campaign packs for the fully preparable list.

Cut-line: do not build broad C5 campaign packs before the registry/linter exists. Otherwise the bank’s breadth becomes scope pressure.

**P5 — AMEND**

Telemetry perturbation cost: major, not global blocker. It is blocker only for claims near the detection floor and for C5-1.6-style sampler overhead. Fold it into P2-015 as an ABBA/telemetry-on-off floor component.

Sampler-phase jitter sensitivity: blocker for phase/item-window claims. The current reducer emits phase joules even when identifiability fails [reduce.py](/Users/edr/code/JouleWise/joulewise/reduce.py:571). The docs already know short prefill is not resolvable at ~9 Hz [phase_4_plan.md](/Users/edr/code/JouleWise/docs/phase_4/phase_4_plan.md:39), but claim tooling must enforce a jitter/sampling sensitivity bound.

Output-token identity effects: major, selectively blocker. Fixed output-token count is not fixed decoded work. For request-energy characterization, record hashes and proceed. For quantization/runtime/speculative-decoding efficiency claims, output equivalence or divergence reporting is mandatory; otherwise downgrade to stack/policy-conditioned energy, not “more efficient model/runtime.”

**Wrongly Accepted Finding**

The lead wrongly accepted C5-1.1 as an unresolved attribution blocker. The wording is still tempting, but the existing contract already handles the dangerous claim: the bank amendment says 4-6 model points support only descriptive L2 pairwise contrasts and forbids active+total+KV fits on that sample [research_question_bank.md](/Users/edr/code/JouleWise/docs/research_question_bank.md:599). The claims ladder also explicitly forbids active-parameter scaling at L1 [claims_ladder.md](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md:39), and the capability map says the observed two-model result does not support active-parameter scaling [research_question_bank.md](/Users/edr/code/JouleWise/docs/research_question_bank.md:452). Rename it for hygiene, but do not treat it as a live blocker.

**Under-Weighted Finding**

M2 ordering is under-weighted. This is not just a report wording mismatch; it affects category, difficulty, thermal, and item-position inference. The docs currently promise rotation in C-015 [research_question_bank.md](/Users/edr/code/JouleWise/docs/research_question_bank.md:127), while the executable spec says manifest order unless new manifests/policy exist [prompt_sequencing_spec.md](/Users/edr/code/JouleWise/docs/specs/suite_next/prompt_sequencing_spec.md:85). Fix before suite campaigns.

**Core Answer**

With the amended P4 artifacts landed, yes: JouleWise stands up to a Stanford-PhD-EE advisor as an undergraduate capstone, provided the claim is “auditable, boundary-labeled local LLM energy characterization on named stacks,” with split inference gated as stretch/upgrade. It would be a rigorous instrument-methodology capstone, not a calibrated universal energy benchmark.

Residual risks no spec work can close: vendor telemetry may be biased without wall/PD calibration; one unit per target cannot support generalization; thermal/ambient/chassis effects remain empirical; KV portability and split feasibility depend on real runtimes; OS/runtime/version drift can change results; workload ecological validity remains bounded; output quality equivalence is not guaranteed by energy instrumentation; cloud/datacenter crossover stays scenario analysis unless externally measured.

CHECKS PERFORMED: Read synthesis + L1-L4, then verified claims against `claims_ladder.md`, `analysis_plans.md`, `measurement_methodology.md`, `prompt_sequencing_spec.md`, `PROJECT_STATUS.md`, `research_question_bank.md`, Phase 4 plan, risk register, reducer, and aggregator; no edits/tests due read-only sandbox.