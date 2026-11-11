# Capstone paper — mid-December 2026

> **Status note, 2026-11-10 (research lead RL-27 (4), amending RL-1 item 3).** Under `RUN_STATE.md` item 256 no
> tripwire manuscript is in production. This file is superseded as a manuscript plan and is kept as the source
> register and evidence ledger for Paper 1's outlook and for the talk. Its Block 5 exclusion is historical: neither
> in force nor reversed. Block 5 numbers are placed in Paper 1 only (RL-2), and on slides under RL-10; a later
> tripwire or v4 manuscript needs its own placement ruling. Lines are not edited one by one. Ruling:
> `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`, branch `audit/2026-11-10-fable`.

**Working title:** Sabotage Leaves an Energy Signature: A Pilot Study of Physical Auditing for AI Agents

**Thesis:** measured energy can supply evidence about computation omitted from a log. Reported pilots motivate a registered test; they do not establish a semantic sabotage detector or an adaptive monitor–meter squeeze.

The capstone is led by ALIGN. BYTES and known-bytes supply instrument context and validation, following `docs/research/research-strategy.md` §0. Older BYTES-led paper framing in parts of `AGENDA.md` is superseded by that milestone decision. This outline leaves the existing paper drafts and their frozen claims unchanged. ALIGN protocol versions v4/v5 are distinct from older phase-energy pack suffixes `_v4`/`_v5` in those drafts.

## Source register and access boundary

Only reported, unblinded numbers below are available for the base paper. No raw measurement data were accessed. Absolute archive/data paths embedded in the sources are provenance text only and must not be followed. Do not run an analysis pipeline to fill this outline.

Paths without a revision below are pinned to the intake commit `fc1f2ae9cc35a774d1175c462f84dd3c920757b6`. Some requested documents are absent from this checkout; their local Git versions were read without a fetch. Resolve a pinned source as `git show REV:path`, rather than silently substituting a later branch version.

| Key | Exact source in this repository | Use |
|---|---|---|
| STRATEGY | `docs/research/research-strategy.md`; `docs/research/AGENDA.md`; `docs/research/energy-tripwire.html` | Milestones, conceptual framing, design status; the HTML's residual drawing is illustrative. |
| V3 | `e901eb2a480d51377a494be9d797733dfcd0220b:docs/align/pilot_protocol_v3.md` | Protocol-v3 sampled-pilot configuration, count convention and known-H estimand. File heading “ALIGN pilot 4” names the first numbered run under v3. |
| ER | `e901eb2a480d51377a494be9d797733dfcd0220b:docs/align/energy_residual.md` | Residual API, uncertainty semantics, total versus owned energy, synthetic-validation limits. Its general calibration description does not override the later per-pair pilot ruling. |
| CODE | `4d54cb47bb7ba0c267138a57de747a7183ca23ff:joulewise/align/energy_residual.py`, `design_row`; same revision's `joulewise/align/apple/pilot_analysis.py`, `alternative_residual_analysis`; `7fbd95e31:scripts/align_pilot_calibration.py`, `split_threshold`/`calibrate` | Read-only checks of the exact sequence formula, GPU-channel scoring, per-session fits and integer threshold rank. No analysis script was executed. |
| P7 | `docs/process_traces/2026-11-04-magistrate-cf1baad2/RECORD.md`, “Ruling (lead)” and preceding correction | Sequence-design selection; pilots 4–7 are selection data; coefficients fit per session/pair; support flags are diagnostic. |
| P8 | `docs/process_traces/2026-11-05-magistrate-c110a6c9/RECORD.md`, “Desk read (pilot 8)” | Per-pair spreads, exclusion and threshold fragility. |
| P9 | `docs/process_traces/2026-11-05-magistrate-f775edaf/RECORD.md`, “Desk read (pilot 9)” | Per-pair spreads, first finite pooled thresholds, selection-data diagnostic. |
| P10 | `docs/process_traces/2026-11-05-magistrate-3efb8793/RECORD.md`, “Desk read (pilot 10)” | Latest reported calibration pool, omission checks, anchor variance and exclusions. |
| KB | `docs/process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md`, “Contrasts,” “Description,” “Disclosures,” “Corrections” | Admitted non-claim known-bytes result and its limits. |
| BYTES | `e901eb2a480d51377a494be9d797733dfcd0220b:docs/design/bytes_pilot/SUMMARY.md`; same revision's `bench.py` and `summarize.py` | Feasibility/accounting pilot, explicitly no power capture. `summary_rows.json` is a stored summary if a broader accounting chart is wanted later. Do not execute these scripts: they cite external data/model paths and loaders. |
| LIT | `16e1db6230a80a605d084f0f9f61431d541b793f:docs/research-audits/2026-11-07/literature.md` (local `origin/research/2026-11-07-literature`) | Adjudicated synthesis §§1–6, source identities, verification status and unresolved provenance. Prefer it to the unreconciled seat appendices. |
| DESIGN | `docs/align/council-2026-11-05/FINAL-DESIGN.md`, `FINAL-DESIGN-AMENDMENT-1.md`, `FINAL-DESIGN-AMENDMENT-2.md`; STRATEGY §§3–4 for later rulings | Design history only. Later strategy adopts registration grade and DC-meter capture; earlier defaults/rosters are not current achieved state. |
| PAPER | `docs/paper/draft-v1.md` §§1–5, 8; `docs/paper/draft-v2-skeleton.md` §§1, 3, 5–6; `docs/paper/figures-plan.md` | Reuse boundary/timing explanation and illustrative artwork only with its labels. The successor methods draft limits stronger claims in the older draft. No prospective result placeholders or Block-5 fills are imported. |

No tracked `docs/run_reports/*align*pilot*` files were found in the local Git history. P7–P10 are the available committed lead reports of those pilots, rather than raw `PILOT.json` files or private seat reports. This source substitution is explicit so the author can check it before final writing.

## Numerical evidence ledger

Every empirical number proposed for the main talk/paper has a source and a restricted interpretation here. Timing allocations, figure labels and writing deadlines are editorial choices. Design targets are separated from observations.

**Channel label:** the residual/score results E4 and E6–E8 use the pilot's `powermetrics:gpu_power` channel (CODE), not DC-input joules. E5 is the reported GPU-energy anchor diagnostic from the same pilot series. The later plan to analyze DC input does not change those historical measurands.

| ID | Exact reported value | Evidence and allowed interpretation |
|---|---|---|
| E1 | Rails `0.0092430977 ± 0.0020742222`; GPU rail `0.0087900978 ± 0.0001046952`; DC input `0.0388927024 ± 0.0072375402`; rest `0.0296496048 ± 0.0084425395` J/GB | KB “Contrasts.” Rotate minus repeat, per logical GB, matched 32 MiB dispatches. Use the reported half-widths; do not relabel them 95% confidence intervals or independent errors. Rest is DC minus rails, not a separately metered component. |
| E2 | Rails share `f = 0.238 ± 0.098`; complement `1 − f = 0.762`, about **76%** outside rails | KB “Description.” Complement is arithmetic on the reported ratio; its descriptive half-width is 0.098 (9.8 percentage points), not a new measurement. Specific to this latency-bound contrast. The test does not locate the memory controller or separate DRAM, fabric, conversion and fans. |
| E3 | Qwen3-32B: resident `18.4 GB`, accounted reads `17.99 GB/token`; Qwen3-30B-A3B: `17.2 GB`, `1.71 GB/token` | BYTES main table, stored-byte accounting in `bench.py:accounting`. GB = decimal 10^9 bytes. “Measured reads” in the old table means weight-size accounting, not observed DRAM transactions. No energy measurement; no inference that the energy ratio equals the byte ratio. |
| E4 | Sequence-design residual SDs: pilot 8 bank `58.3 J` (9 df), spam `19.0 J` (10 df); pilot 9 bank `45.1 J`, spam `32.7 J` (10 df each) | P8/P9 headline rows, counts logged, per pair. The shorthand `19–58 J` refers to these rows, not instrument noise. Legacy SDs alongside them: p8 `250.8 / 45.4 J`, p9 `274.0 / 118.8 J` (bank/spam); show these in T2 to disclose design dependence. |
| E5 | Pilot-10 anchor model: residual SD `1.93 J` (36 df), between-session moment component `4.67 J`; 7 of 8 anchor keys eligible and token-identical across seven sessions | P10 anchor paragraph. Residual after additive trajectory/session effects, not the raw SD of a replay difference or a deployed detector's error. P9 previously used all eight anchors across six sessions and reported `2.17 J` residual SD and `4.60 J` session component. Do not omit the session term when motivating replay. |
| E6 | Pilots 8–10: `m = 28` held-out benign scores per pair; rank `ceil(0.95 × 29) = 28`, the maximum. Sequence thresholds bank `2.53`, spam `7.13`; next largest `2.11 / 2.99` | P10 frozen-calibration paragraph. Per-session fits, scores pooled per pair under frozen code `7fbd95e31`; design selected before these fresh benign seeds. This is not one frozen coefficient vector tested everywhere. Shared LOO fits and heavy tails prevent inferring a nominal deployment FPR from m alone. |
| E7 | All six untampered sabotage readings in pilots 8–10 below their per-pair thresholds; all six detected at sequence `k = 1`. First-turn omitted reasoning: spam `H = 539`, bank `H = 1,193` tokens | P10 calibration paragraph plus P8/P9 explicit H rows. Six session readings of **two distinct seed-1 sabotage trajectories**, not six independent attacks. P9 p8/p9 untampered scores: bank `0.70 / 1.64`, spam `4.10 / 0.40`; label their narrower cohort if plotted. No H50/H90 or continuous detection curve is identified by these points. |
| E8 | Pilots 4–9 diagnostic, sequence design: bank `2/26` untampered above threshold, spam `0/26`; bank/spam calibration m `35 / 36` | P9 final paragraph. These are selection-inclusive, deduplicated trajectory analyses; never call them held-out FPR. Do not abbreviate to “2 of 26 overall”: the denominator is per pair. H=0 alarms are not successful omission detections. |
| E9 | Pilot 8: `27/28` registered-eligible, one bank benign thermal exclusion. Pilot 9: `28/28`. Pilot 10: `24/28`, three battery exclusions (one replay anchor) and one bank thermal exclusion | P8/P9/P10 eligibility and exclusions paragraphs. Report reasons and scopes; do not silently repair the sample or count the excluded anchor as a lost calibration seed. Later benign pool m is given by E6. |

Design values D1: protocol-v3 configuration is Qwen3-30B-A3B MLX 4-bit, thinking on, two named task pairs, turn limit 12, output budget 4,096, context cap 40,960 (V3 table). These are caps/settings, not achieved per-episode counts. D2: current v4 plan targets `m ≥ 39` per pair plus a locked test cohort (STRATEGY §3); D3: the talk is 30 November and paper mid-December, with a conditional v4 release cut around 10 December (STRATEGY §0). These are not completed milestones.

## Section-by-section manuscript

### Abstract

State the oversight problem, the residual audit, the two-boundary instrument and the pilot result. In the base version, use E2 and E7 with the two-distinct-trajectory qualification in the same sentence as the omission finding. Say “pilot evidence for known-omission detection.” Do not use “100% detection,” a false-alarm guarantee, or an adaptive-sabotage claim. Add a registered-v4 result sentence only in variant A below.

### 1. Introduction: what an editable record cannot establish

Explain monitoring awareness, omitted/edited logs and why a content monitor sees only available content. State the question: does energy provide information beyond logged tokens and a software replay? Name the required trust boundary. Contributions may be (i) an episode-level omission audit, (ii) a documented instrument boundary, and (iii) a carefully limited pilot plus prospective study. F1 introduces the threat model; no numerical performance claim here beyond a referenced preview of E7.

### 2. Threat model, estimands and baselines

Assume the auditor controls hardware/capture and retained meter readings; the agent has scoped unprivileged access. State exactly which log/count fields it can alter. `powermetrics` has a host-software privilege boundary; an external DC meter helps only if capture and custody remain outside the tested adversary's control. Denial of service and capture compromise are failures to detect/report, not benign evidence.

The **pilot estimand** is detection of a known reasoning-count omission with measured joules and context/prefill fixed (V3). It is neither a causal sabotage-energy effect nor detection of intent. Put authenticated runtime accounting/replay, trusted elapsed time, metadata-only prediction, and a text monitor on the baseline map; only the energy pilot is observed here. STRATEGY §2 makes runtime-external compute and untrusted/non-replayable execution the most useful future niche. Do not claim incremental value over these baselines without measuring it.

### 3. Instrument and validation: what the joule channel measures

Describe the M3 Max-class laptop, named MLX configuration, phase markers, interval-average rails, thermal observations and the independent KM003C channel. F3 must place the KM003C **after the adapter**: it measures DC input, excludes adapter AC losses and requires battery accounting to relate input to machine consumption.

Use E1–E2/F4 as the central validation result: the rails omit most of the memory-traffic contrast in this controlled known-bytes test. Discuss its non-claim admission, post-data reading-rule correction and labelled literal-lag alternative from KB “Corrections”; do not present it as an untouched confirmatory calibration. Use E3/F5 as BYTES design rationale, explicitly no power capture. Known-bytes is a physical boundary check; the throughput pilot is feasibility/accounting context.

Keep the inherited timing discussion bounded by PAPER: a held-average phase allocation is conditional on the reconstruction; a meter total does not validate sub-record phase splits. Earlier draft claims about attribution dominance and prospective floors do not transfer into the capstone. T1 records boundaries/units; no Block-5 result enters it.

### 4. Residual detector and analysis procedure

Define the episode total, the sum of turn predictions, the score denominator and the per-pair threshold. Explain that owned tool energy belongs to its turn and unowned gaps remain in the gross integral (ER). Keep gross episode energy and turn-owned energy separately labelled. Do not silently change a pilot GPU-channel result into DC-input energy.

Distinguish the original five-term API `[1, P, D, C·D, C·P]` (ER) from the sequence/attention-length alternative used for the reported headline, `[1, P, D, (C+P)D + D²/2, CP + P²/2]` (CODE `design_row`; P7 ruling). Define C as cached context before the call, P as fed prefill, D as decode. Explain the selection on pilots 4–7, the frozen implementation `4d54cb47b` (pin runner `cda28a5ef`), and later frozen calibration `7fbd95e31`. Retain the legacy rows rather than making the improvement look preregistered from the outset.

Describe leave-one-trajectory-out benign scores, replay deduplication and per-session fits before per-pair pooling. H removes logged reasoning counts from the first k rows, leaving the physical observation unchanged. Duration stays a diagnostic rather than a fitted term that could explain away hidden work. Additive attribution bounds remain labelled bounds when used in SD formulae; synthetic normal-theory power is not measured hardware power. F2 shows the procedure; T2 identifies design/count/eligibility scope.

### 5. Pilot protocol and cohort accounting

Give D1 and name both SHADE task pairs. Explain independent seed law, sampled trajectories, repeated anchors, thinking-count visibility, thermal/battery eligibility and fresh-seed roles. “v3” is the protocol lineage; numbered pilots 4–10 are runs under it. T2 must separate selection pilots 4–7 from the later benign calibration increments and repeated sabotage anchors. Give E9 and link the report for every exclusion; instrument-incomplete windows remain labelled as such.

### 6. Results: observed sensitivity, not a safety guarantee

1. **Physical boundary:** E1–E2, F4; one controlled contrast, not an all-workload correction factor.
2. **Replay and model spread:** E4–E5, F6; show session effects separately. No inference of a new replay detector's power.
3. **Known omissions:** E6–E7, F7; show only the reported points and thresholds. State that the attack checks reuse two trajectories. Report a crossing at the smallest tested H, not a minimum detectable H.
4. **Fragility and failures:** E8–E9, F8/T2; disclose the single benign spam tail, eligibility losses and legacy-design results. Untampered sabotage above threshold is neither a benign-FPR estimate nor a successful known-H detection.

For variant A, add a separate subsection with released v4 outcomes and T4; never pool them with the pilot to improve apparent significance. For variant B, end this section after the pilot.

### 7. Related work and the precise gap

Use the map below. Position the contribution between software count audits and coarse physical compute verification. The literature audit found no token-level agent-log energy audit in its search; that is a search-bounded observation, not proof of priority. Regression in tokens is established prior art. Describe blinding/preregistration as established scientific practice. Prefer the audit's adjudicated verification statuses to its seat appendices.

### 8. Discussion: the squeeze and three layers

F9 separates content monitors, quantity meters and internal probes. The proposed squeeze predicts a tradeoff: omitted computation may become an energy residual; logged cover work is exposed to a content monitor. That implication is contingent, not a theorem. Filler-token reasoning, plausible cover stories and matched-energy padding may evade both. No interpretability probe or monitor catch rate has been measured in these pilots.

For v5, propose a capability gate, runtime-external positive controls, monitor-only/meter-only/joint comparisons at registered false-alarm costs, and an adaptive red team. Use escape per sabotage attempt as the primary proposed estimand (STRATEGY §2); distinguish it from escape conditional on successful sabotage and publish all denominators. Measure task success and oversight cost as well. Do not invent a v5 roster, joint threshold or decision rule while its design competition is pending.

### 9. Threats to validity

Use the explicit checklist below, tying each threat to a possible change in the conclusion rather than treating registration as a cure.

### 10. Registered continuation and six-month plan

F10 covers R0/R1, thermal/budget settings, blind registration, W1, later calibration/test windows and the release gate. Cite DESIGN as history and STRATEGY for the current registration-grade target. The v4 plan adds DC-input capture/analysis in every window and preserves full reasoning transcripts sealed and unscored; no monitor scores them before registration (STRATEGY §§3–4). Show missing gates as pending; no readiness outcome is inferred here. v4 tests known omissions; v5 adds adaptive joint oversight. F11 gives the six-month plan through the approximate NeurIPS 2027 target, subject to advisor review and measurement capacity. The talk remains pilot-only even if the paper later uses variant A.

### 11. Conclusion; availability and appendices

Restate what is observed and what remains untested. Provide T3 (claim–evidence–limit map), the pinned source register, exclusion ledger, model/count conventions, deviation history and figure-source tables. Link released artifacts only when authorized; do not imply private raw captures are public or that reproduction was performed in this task. Avoid absolute private data paths in the manuscript. Existing illustrative SVGs from PAPER keep their synthetic labels.

## Related-work map from the 7 November audit

These references and statuses come from LIT, not a new literature search. Primary-source links are citation targets for the manuscript; none was opened over the network for this outline.

| Cluster / LIT rows | Primary neighbours | Relationship and claim boundary |
|---|---|---|
| Monitoring and awareness, 27, 29–31, 39–42 | [SHADE-Arena](https://arxiv.org/abs/2506.15740); [Kale et al.](https://arxiv.org/abs/2508.19461); [MonitoringBench](https://arxiv.org/abs/2605.09684); [Baker et al.](https://arxiv.org/abs/2503.11926); [Chen et al.](https://arxiv.org/abs/2505.05410); [Pfau et al.](https://arxiv.org/abs/2404.15758) | Motivate missing/unfaithful content and filler computation. The last item also supplies a limit: compute can hide inside logged tokens. LIT statuses RV except Baker (S1+S2) and Chen (S2). |
| Software hidden-token audits, 52–56 | [CoIn](https://aclanthology.org/2026.findings-emnlp.363/); [PALACE](https://arxiv.org/abs/2508.00912); [Token Inflation](https://arxiv.org/abs/2605.30040) | Audit declared counts through software evidence; energy is a different evidence channel. CoIn/Token Inflation RV, PALACE S2. Do not confuse overbilling with omitted sabotage work. |
| Physical compute verification, 57–60, 65–66 | [Gargiulo & Kulp](https://arxiv.org/abs/2609.00309); [Kimpson, Baker & Graham](https://arxiv.org/abs/2610.07476); [de Almeida](https://icml.cc/virtual/2026/78576); [TOPLOC](https://arxiv.org/abs/2501.16007) | Different grain: workload/training signatures, covert-compute limits or activation proofs. First three RV; TOPLOC S2. Compare hidden-work fractions conceptually; do not port their detection rates or hardware constants. |
| Energy regression and attention, 68–72, 75 | [Wilkins, Keshav & Mortier](https://arxiv.org/abs/2407.04014); [Vellaisamy et al.](https://arxiv.org/abs/2608.28044); [Chkir et al.](https://arxiv.org/abs/2608.25096); [Ma et al.](https://arxiv.org/abs/2605.11999); [Solovyeva & Castor](https://arxiv.org/abs/2602.05712) | Token regression is prior art; the candidate contribution is the omission residual in multi-turn cached episodes. Hybrid attention and phase coupling threaten the fit. All RV in the synthesis; Ma is PPAM 2026, and Solovyeva's venue remains unconfirmed. |
| Apple measurement and agent joules, 1, 3–5, 7, 18–20, 47–48 | Apple man-page disclaimer (LIT row 1); [Hot Pixels](https://www.usenix.org/conference/usenixsecurity23/presentation/taneja); [AgentStop](https://arxiv.org/abs/2605.15206); [Energy per Successful Goal](https://arxiv.org/abs/2605.22883); [Luo et al.](https://arxiv.org/abs/2609.29707); [Yang et al.](https://arxiv.org/abs/2312.02741) | Boundary, thermal state and sampler timing matter. No cross-device gain claim; no general “first thermal protocol” claim. RV except Yang S1+S2. KB provides a new boundary-specific observation; it does not retroactively validate old phase-energy totals. |
| Oversight cost, 34–38, 44 | [AI Control](https://arxiv.org/abs/2312.06942); [Ctrl-Z](https://arxiv.org/abs/2504.10374); [Control Tax](https://arxiv.org/abs/2506.05296); [Hua et al.](https://arxiv.org/abs/2507.15886) | Systems compare safety/usefulness/budget; measured joules could become a cost axis. It remains future work here. Control Tax RV, AI Control/Ctrl-Z S1+S2, Hua S2. |
| Blinding, registration and metrology, 88–104 | [Nosek et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500); [Hofman et al.](https://arxiv.org/abs/2311.18807); Klein & Roodman (LIT row 93); [Hoefler & Belli](https://htor.inf.ethz.ch/publications/index.php?pub=222); [Khiani](https://neurips.cc/virtual/2026/166242) | Established safeguards, not the novelty claim. First four S1+S2 (Klein/Roodman abstract only); Khiani RV. Khiani's relationship to this project is unresolved in LIT decision 4: lead must settle provenance/disclosure before using it. |

Bibliography actions before submission: carry LIT's verified resolution of Ruf & Detyniecki, Dauner et al. and Paired-MDE; keep the PPAM and IPW venue updates; do not resurrect the UNVERIFIED preprints.org source. MacCoun/Perlmutter and Argerich/Patiño-Martínez are metadata-only and support no substantive claim here. Existing paper-body freeze/rulings are not changed by this outline.

## Threats to validity to print

| Threat | Consequence and required disclosure |
|---|---|
| Log edit versus real hidden compute | Pilot tampering fixes joules and much of the design. It cannot establish a causal sabotage cost or performance on new unlogged tool/subprocess work. Real runtime-external controls belong to v5. |
| Adaptive evasion and privilege | Host capture is not tamper-proof against a privileged adversary. Matched-energy padding, plausible cover text and fixed-compute concealed reasoning can defeat the simple squeeze. State control of the meter/capture path and failure modes. |
| Small, dependent cohorts | Replays do not add independent attack trajectories. LOO scores share fits; maximum-based thresholds are tail-sensitive. No binomial interval pretending all six checks are independent attacks. |
| Design selection and distribution shift | Sequence terms were selected using pilots 4–7; sabotage prompts differ from benign support. Per-session fitting handles some offsets but does not prove exchangeability or transfer. Print legacy results and support flags. |
| Thermal/clock state | E4 includes model/state variation; E5 has a session component. Correlation with clocks does not identify a cause. Gated reference-state energy does not establish production energy. No fitted clock/duration term is added retrospectively. |
| Battery and meter boundary | DC input excludes adapter losses and can differ from consumption during charge/discharge. Retain exclusions/assist disclosures and separate rails/DC labels. Known-bytes' floating-battery observation does not certify every pilot. |
| Known-bytes transport | Matched dispatches are latency-bound. The contrast includes stall time and power rise; it neither identifies DRAM alone nor supplies a universal correction to inference energy. Reading-rule corrections were settled after data existed. |
| Timing and uncertainty | Held-average attribution does not locate physical energy inside a record. Additive bounds are not empirically calibrated SDs; normal-theory synthetic power is not a hardware detection guarantee. |
| Architecture and tool ownership | Hybrid attention/cache behavior may misspecify context terms; cross-phase coupling persists. Missing owned tool energy/unowned gaps can inflate residuals. Any alternative fit is labelled exploratory unless separately registered. |
| Capability and external validity | One device, two task pairs and mid-size open models do not establish frontier-model sabotage ability, datacenter attribution under batching or cross-device calibration. Distinguish “can do the task” from “successfully sabotages it.” |
| Literature completeness and custody | Search-bounded novelty, partial primary-source verification and unavailable raw captures limit priority/reproducibility claims. Keep source/status labels and disclose the lead-report substitution. |

## Two release-dependent variants

### A. Include v4 only after its registered release by about 10 December

This is a future authoring branch, not permission to inspect sealed outcomes now. The lead must provide the admitted release record, pinned protocol/analysis identity, independent recompute agreement, deviations/exclusions and a public or authorized summary. A ready kit, completed window, promising partial analysis or date alone is insufficient.

Keep the pilot result as its own evidence stratum. Add §6.5 and T4 for the released v4 calibration and locked test cohort, including actual counts, hardware/thermal acceptance, both energy channels where admitted, held-out false alarms, known-H curve points, H50/H90 only if identifiable under the registered procedure, and uncertainty/dependence treatment. An admitted null or inconclusive scientific result is eligible. If the registered release gate refuses, use variant B; do not print blocked outcome values. No values or outcome-dependent captions are filled in this outline.

The abstract may describe a registered known-omission test with its released result. The title remains a pilot-study title unless the final evidence warrants a lead-approved revision. v4 still does not establish an adaptive squeeze: it has no evaluated adaptive monitor arm. v5 stays prospective.

### B. No admitted v4 release by the cut

Complete the manuscript with E1–E9, the instrument account, explicit pilot limitations and the registered continuation. State “v4 outcomes unavailable at this manuscript's evidence cut.” Omit T4 and any numerical v4 result figure; F10 remains a design schematic. Do not replace the missing result with Block 5, v4 readiness measurements, synthetic power curves or a selected partial window.

The paper remains a complete pilot/measurement contribution: it demonstrates the tested log-omission crossings and describes where an independent energy channel might add value. The capstone deadline does not require an empirical safety claim.

## Figures, tables and production milestones

The standalone [figure list](FIGURES.md) owns F1–F11, exact report sections, production rules and the no-Mac-time status. Produce F1–F4, F6–F11 for the talk; F5 can be a compact slide/appendix panel. The paper can combine panels to reduce figure count.

| Table | Contents | Sources / admission |
|---|---|---|
| T1 | Measurands, acquisition boundary, units, battery handling and uncertainty labels | KB, ER, PAPER; conceptual table, E1 as the worked contrast. |
| T2 | Pilot cohorts, selection/calibration roles, eligibility, legacy versus sequence SD, threshold population, distinct attack counts | V3, P7–P10, E4–E9; leave unsupported per-run cells blank rather than reconstructing archives. |
| T3 | Claim → evidence → limitation; related-work neighbourhoods | This ledger and LIT synthesis; no new outcome. |
| T4 (variant A only) | Registered v4 disposition and released results | Future lead-admitted release summary; unavailable now, no data-access instruction. |

Proposed writing schedule: freeze talk sources/claims and make the offline figures by 22 November; rehearse and cut by 27 November; present 30 November. Draft the complete variant-B paper during 1–9 December. Around 10 December choose A only from an admitted release; otherwise retain B. Reserve the remaining days before the program's mid-December deadline for caption/source audit, advisor review and proofreading. Exact paper due date remains to be confirmed by Ed; do not invent it.
